#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <blake2.h>
#include <ed25519-hash-custom.h>
#include <ed25519.h>
#include <stdbool.h>
#include <time.h>

#ifdef HAVE_CL_CL_H
#include "opencl_program.h"
#include <CL/cl.h>
#elif HAVE_OPENCL_OPENCL_H
#include "opencl_program.h"
#include <OpenCL/opencl.h>
#else
#include <omp.h>
#endif

static uint64_t s[16];
static int p;

uint64_t xorshift1024star(void) {
  const uint64_t s0 = s[p++];
  uint64_t s1 = s[p &= 15];
  s1 ^= s1 << 31;        // a
  s1 ^= s1 >> 11;        // b
  s1 ^= s0 ^ (s0 >> 30); // c
  s[p] = s1;
  return s1 * 1181783497276652981ull;
}

bool is_valid(uint64_t work, uint8_t *h32, uint64_t difficulty) {
  uint64_t b2b_h;
  blake2b_state b2b;
  blake2b_init(&b2b, 8);
  blake2b_update(&b2b, &work, 8);
  blake2b_update(&b2b, h32, 32);
  blake2b_final(&b2b, &b2b_h, 8);
  return b2b_h >= difficulty;
}

static PyObject *work_validate(PyObject *self, PyObject *args) {
  uint8_t *h32;
  uint64_t difficulty, work;
  Py_ssize_t p0;

  if (!PyArg_ParseTuple(args, "Ky#K", &work, &h32, &p0, &difficulty))
    return NULL;
  assert(p0 == 32);

  return Py_BuildValue("i", is_valid(work, h32, difficulty));
}

static PyObject *work_generate(PyObject *self, PyObject *args) {
  uint8_t *h32;
  uint64_t i, difficulty, work = 0, nonce, work_size = 1024 * 1024;
  Py_ssize_t p0;

  if (!PyArg_ParseTuple(args, "y#K", &h32, &p0, &difficulty))
    return NULL;
  assert(p0 == 32);

  srand(time(NULL));
  for (i = 0; i < 16; i++)
    s[i] = (uint64_t)rand() << 32 | rand();

#if defined(HAVE_CL_CL_H) || defined(HAVE_OPENCL_OPENCL_H)
  int err;
  cl_uint num;
  cl_platform_id cpPlatform;

  err = clGetPlatformIDs(1, &cpPlatform, &num);
  assert(err == CL_SUCCESS);
  if (num == 0) {
    PyErr_SetString(PyExc_RuntimeError, "No GPUs found");
    return NULL;
  }

  size_t length = strlen(opencl_program);
  cl_mem d_nonce, d_work, d_h32, d_difficulty;
  cl_device_id device_id;
  cl_context context;
  cl_command_queue queue;
  cl_program program;
  cl_kernel kernel;

  err = clGetDeviceIDs(cpPlatform, CL_DEVICE_TYPE_GPU, 1, &device_id, NULL);
  assert(err == CL_SUCCESS);

  context = clCreateContext(0, 1, &device_id, NULL, NULL, &err);
  assert(err == CL_SUCCESS);

#ifndef __APPLE__
  queue = clCreateCommandQueueWithProperties(context, device_id, 0, &err);
  assert(err == CL_SUCCESS);
#else
  queue = clCreateCommandQueue(context, device_id, 0, &err);
  assert(err == CL_SUCCESS);
#endif

  program = clCreateProgramWithSource(
      context, 1, (const char **)&opencl_program, &length, &err);
  assert(err == CL_SUCCESS);

  err = clBuildProgram(program, 0, NULL, NULL, NULL, NULL);
  assert(err == CL_SUCCESS);

  d_nonce = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, 8,
                           &nonce, &err);
  assert(err == CL_SUCCESS);

  d_work = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, 8,
                          &work, &err);
  assert(err == CL_SUCCESS);

  d_h32 = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, 32,
                         h32, &err);
  assert(err == CL_SUCCESS);

  d_difficulty = clCreateBuffer(
      context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, 8, &difficulty, &err);
  assert(err == CL_SUCCESS);

  kernel = clCreateKernel(program, "nano_work", &err);
  assert(err == CL_SUCCESS);

  err = clSetKernelArg(kernel, 0, sizeof(d_nonce), &d_nonce);
  assert(err == CL_SUCCESS);

  err = clSetKernelArg(kernel, 1, sizeof(d_work), &d_work);
  assert(err == CL_SUCCESS);

  err = clSetKernelArg(kernel, 2, sizeof(d_h32), &d_h32);
  assert(err == CL_SUCCESS);

  err = clSetKernelArg(kernel, 3, sizeof(d_difficulty), &d_difficulty);
  assert(err == CL_SUCCESS);

  err = clEnqueueWriteBuffer(queue, d_h32, CL_FALSE, 0, 32, h32, 0, NULL, NULL);
  assert(err == CL_SUCCESS);

  err = clEnqueueWriteBuffer(queue, d_difficulty, CL_FALSE, 0, 8, &difficulty,
                             0, NULL, NULL);
  assert(err == CL_SUCCESS);

  while (work == 0) {
    nonce = xorshift1024star();

    err = clEnqueueWriteBuffer(queue, d_nonce, CL_FALSE, 0, 8, &nonce, 0, NULL,
                               NULL);
    assert(err == CL_SUCCESS);

    err = clEnqueueNDRangeKernel(queue, kernel, 1, NULL, &work_size, NULL, 0,
                                 NULL, NULL);
    assert(err == CL_SUCCESS);

    err = clEnqueueReadBuffer(queue, d_work, CL_FALSE, 0, 8, &work, 0, NULL,
                              NULL);
    assert(err == CL_SUCCESS);

    err = clFinish(queue);
    assert(err == CL_SUCCESS);
  }

  err = clReleaseMemObject(d_nonce);
  assert(err == CL_SUCCESS);

  err = clReleaseMemObject(d_work);
  assert(err == CL_SUCCESS);

  err = clReleaseMemObject(d_h32);
  assert(err == CL_SUCCESS);

  err = clReleaseMemObject(d_difficulty);
  assert(err == CL_SUCCESS);

  err = clReleaseKernel(kernel);
  assert(err == CL_SUCCESS);

  err = clReleaseProgram(program);
  assert(err == CL_SUCCESS);

  err = clReleaseCommandQueue(queue);
  assert(err == CL_SUCCESS);

  err = clReleaseContext(context);
  assert(err == CL_SUCCESS);
#else
  while (work == 0) {
    nonce = xorshift1024star();
#pragma omp parallel for
    for (i = 0; i < work_size; i++) {
      if (work == 0 && is_valid(nonce + i, h32, difficulty)) {
#pragma omp critical
        work = nonce + i;
      }
    }
  }
#endif
  return Py_BuildValue("K", work);
}

void ed25519_randombytes_unsafe(void *out, size_t outlen) {}

void ed25519_hash_init(ed25519_hash_context *ctx) { blake2b_init(ctx, 64); }

void ed25519_hash_update(ed25519_hash_context *ctx, uint8_t const *in,
                         size_t inlen) {
  blake2b_update(ctx, in, inlen);
}

void ed25519_hash_final(ed25519_hash_context *ctx, uint8_t *out) {
  blake2b_final(ctx, out, 64);
}

void ed25519_hash(uint8_t *out, uint8_t const *in, size_t inlen) {
  ed25519_hash_context ctx;
  ed25519_hash_init(&ctx);
  ed25519_hash_update(&ctx, in, inlen);
  ed25519_hash_final(&ctx, out);
}

static PyObject *publickey(PyObject *self, PyObject *args) {
  const unsigned char *sk;
  Py_ssize_t p0;
  ed25519_public_key pk;

  if (!PyArg_ParseTuple(args, "y#", &sk, &p0))
    return NULL;
  assert(p0 == 32);
  ed25519_publickey(sk, pk);
  return Py_BuildValue("y#", &pk, 32);
}

static PyObject *sign(PyObject *self, PyObject *args) {
  const unsigned char *sk, *m, *r;
  Py_ssize_t p0, p1, p2;

  if (!PyArg_ParseTuple(args, "y#y#y#", &sk, &p0, &m, &p1, &r, &p2))
    return NULL;
  assert(p0 == 32);
  assert(p2 == 32);
  ed25519_public_key pk;
  ed25519_publickey(sk, pk);
  ed25519_signature sig;
  ed25519_sign(m, p1, r, sk, pk, sig);
  return Py_BuildValue("y#", &sig, 64);
}

static PyObject *verify_signature(PyObject *self, PyObject *args) {
  const unsigned char *sig, *pk, *m;
  Py_ssize_t p0, p1, p2;

  if (!PyArg_ParseTuple(args, "y#y#y#", &sig, &p0, &pk, &p1, &m, &p2))
    return NULL;
  assert(p0 == 64);
  assert(p1 == 32);
  return Py_BuildValue("i", ed25519_sign_open(m, p2, pk, sig) == 0);
}

static PyMethodDef m_methods[] = {
    {"work_generate", work_generate, METH_VARARGS, NULL},
    {"work_validate", work_validate, METH_VARARGS, NULL},
    {"publickey", publickey, METH_VARARGS, NULL},
    {"sign", sign, METH_VARARGS, NULL},
    {"verify_signature", verify_signature, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef ext_module = {
    PyModuleDef_HEAD_INIT, "ext", NULL, -1, m_methods, NULL, NULL, NULL, NULL};

PyMODINIT_FUNC PyInit_ext(void) { return PyModule_Create(&ext_module); }
