#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <blake2.h>
#include <ed25519-hash-custom.h>
#include <ed25519.h>
#include <stdbool.h>
#include <time.h>

#ifdef USE_OCL
#include "opencl_program.h"
#ifdef __APPLE__
#include <OpenCL/opencl.h>
#else
#include <CL/cl.h>
#endif
#else
#include <omp.h>
#endif

typedef struct {
  uint64_t s[16];
  uint8_t p;
} nonce_state;

static uint64_t xorshift1024star(nonce_state *n) {
  const uint64_t s0 = n->s[n->p++];
  uint64_t s1 = n->s[n->p &= 15];
  s1 ^= s1 << 31;        // a
  s1 ^= s1 >> 11;        // b
  s1 ^= s0 ^ (s0 >> 30); // c
  n->s[n->p] = s1;
  return s1 * 1181783497276652981ull;
}

static bool is_valid(uint64_t work, uint8_t *h32, uint64_t difficulty) {
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
  if (p0 != 32)
    return PyErr_Format(PyExc_ValueError, "Hash must be 32 bytes");

  bool res = is_valid(work, h32, difficulty);
  return Py_BuildValue("i", res);
}

static PyObject *work_generate(PyObject *self, PyObject *args) {
  uint8_t *h32;
  int i;
  uint64_t difficulty, work = 0, nonce, work_size = 1024 * 1024;
  nonce_state n;
  Py_ssize_t p0;

  if (!PyArg_ParseTuple(args, "y#K", &h32, &p0, &difficulty))
    return NULL;
  if (p0 != 32)
    return PyErr_Format(PyExc_ValueError, "Hash must be 32 bytes");

  srand(time(NULL));
  n.p = 0;
  for (i = 0; i < 16; i++)
    n.s[i] = (uint64_t)rand() << 32 | rand();

#ifdef USE_OCL
  int err;
  cl_uint num;
  cl_platform_id cpPlatform;

  err = clGetPlatformIDs(1, &cpPlatform, &num);
  if (err || !num)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clGetPlatformIDs", err);
#ifndef NDEBUG
  char cl_platform_name[128];
  clGetPlatformInfo(cpPlatform, CL_PLATFORM_NAME, sizeof(cl_platform_name),
                    cl_platform_name, NULL);
  printf("OpenCL: %s\n", cl_platform_name);
#endif

  size_t length = strlen(opencl_program);
  cl_mem d_nonce, d_work, d_h32, d_difficulty;
  cl_device_id device_id;
  cl_context context;
  cl_command_queue queue;
  cl_program program;
  cl_kernel kernel;

#ifdef USE_OCL_CPU
  err = clGetDeviceIDs(cpPlatform, CL_DEVICE_TYPE_CPU, 1, &device_id, NULL);
#else
  err = clGetDeviceIDs(cpPlatform, CL_DEVICE_TYPE_GPU, 1, &device_id, NULL);
#endif
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clGetDeviceIDs", err);
#ifndef NDEBUG
  char cl_device_name[128];
  clGetDeviceInfo(device_id, CL_DEVICE_NAME, sizeof(cl_device_name),
                  cl_device_name, NULL);
  printf("OpenCL: %s\n", cl_device_name);
#endif

  context = clCreateContext(0, 1, &device_id, NULL, NULL, &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateContext", err);

#ifndef __APPLE__
  queue = clCreateCommandQueueWithProperties(context, device_id, 0, &err);
  if (err)
    return PyErr_Format(
        PyExc_RuntimeError,
        "OpenCL:%d: Failed to clCreateCommandQueueWithProperties", err);
#else
  queue = clCreateCommandQueue(context, device_id, 0, &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateCommandQueue", err);
#endif

  program = clCreateProgramWithSource(
      context, 1, (const char **)&opencl_program, &length, &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateProgramWithSource", err);

  err = clBuildProgram(program, 0, NULL, NULL, NULL, NULL);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clBuildProgram", err);

  d_nonce = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, 8,
                           &nonce, &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateBuffer", err);

  d_work = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, 8,
                          &work, &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateBuffer", err);

  d_h32 = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, 32,
                         h32, &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateBuffer", err);

  d_difficulty = clCreateBuffer(
      context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, 8, &difficulty, &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateBuffer", err);

  kernel = clCreateKernel(program, "nano_work", &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateKernel", err);

  err = clSetKernelArg(kernel, 0, sizeof(d_nonce), &d_nonce);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clSetKernelArg", err);

  err = clSetKernelArg(kernel, 1, sizeof(d_work), &d_work);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clSetKernelArg", err);

  err = clSetKernelArg(kernel, 2, sizeof(d_h32), &d_h32);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clSetKernelArg", err);

  err = clSetKernelArg(kernel, 3, sizeof(d_difficulty), &d_difficulty);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clSetKernelArg", err);

  err = clEnqueueWriteBuffer(queue, d_h32, CL_FALSE, 0, 32, h32, 0, NULL, NULL);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clEnqueueWriteBuffer", err);

  err = clEnqueueWriteBuffer(queue, d_difficulty, CL_FALSE, 0, 8, &difficulty,
                             0, NULL, NULL);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clEnqueueWriteBuffer", err);

  while (!work) {
    nonce = xorshift1024star(&n);

    err = clEnqueueWriteBuffer(queue, d_nonce, CL_FALSE, 0, 8, &nonce, 0, NULL,
                               NULL);
    if (err)
      return PyErr_Format(PyExc_RuntimeError,
                          "OpenCL:%d: Failed to clEnqueueWriteBuffer", err);

    err = clEnqueueNDRangeKernel(queue, kernel, 1, NULL, &work_size, NULL, 0,
                                 NULL, NULL);
    if (err)
      return PyErr_Format(PyExc_RuntimeError,
                          "OpenCL:%d: Failed to clEnqueueNDRangeKernel", err);

    err = clEnqueueReadBuffer(queue, d_work, CL_FALSE, 0, 8, &work, 0, NULL,
                              NULL);
    if (err)
      return PyErr_Format(PyExc_RuntimeError,
                          "OpenCL:%d: Failed to clEnqueueReadBuffer", err);

    err = clFinish(queue);
    if (err)
      return PyErr_Format(PyExc_RuntimeError, "OpenCL:%d: Failed to clFinish",
                          err);
  }

  err = clReleaseMemObject(d_nonce);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clReleaseMemObject", err);

  err = clReleaseMemObject(d_work);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clReleaseMemObject", err);

  err = clReleaseMemObject(d_h32);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clReleaseMemObject", err);

  err = clReleaseMemObject(d_difficulty);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clReleaseMemObject", err);

  err = clReleaseKernel(kernel);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clReleaseKernel", err);

  err = clReleaseProgram(program);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clReleaseProgram", err);

  err = clReleaseCommandQueue(queue);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clReleaseCommandQueue", err);

  err = clReleaseContext(context);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clReleaseContext", err);
#else
  while (!work) {
    nonce = xorshift1024star(&n);
#pragma omp parallel for
    for (i = 0; i < work_size; i++) {
      if (!work && is_valid(nonce + i, h32, difficulty)) {
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
  const uint8_t *sk;
  Py_ssize_t p0;
  ed25519_public_key pk;

  if (!PyArg_ParseTuple(args, "y#", &sk, &p0))
    return NULL;
  if (p0 != 32)
    return PyErr_Format(PyExc_ValueError, "Secret key must be 32 bytes");

  ed25519_publickey(sk, pk);
  return Py_BuildValue("y#", pk, sizeof(pk));
}

static PyObject *sign(PyObject *self, PyObject *args) {
  const uint8_t *sk, *m, *r;
  Py_ssize_t p0, p1, p2;

  if (!PyArg_ParseTuple(args, "y#y#y#", &sk, &p0, &m, &p1, &r, &p2))
    return NULL;
  if (p0 != 32)
    return PyErr_Format(PyExc_ValueError, "Secret key must be 32 bytes");
  if (p2 != 32)
    return PyErr_Format(PyExc_ValueError, "Random must be 32 bytes");

  ed25519_public_key pk;
  ed25519_publickey(sk, pk);
  ed25519_signature sig;
  ed25519_sign(m, p1, r, sk, pk, sig);
  return Py_BuildValue("y#", sig, sizeof(sig));
}

static PyObject *verify_signature(PyObject *self, PyObject *args) {
  const uint8_t *sig, *pk, *m;
  Py_ssize_t p0, p1, p2;

  if (!PyArg_ParseTuple(args, "y#y#y#", &sig, &p0, &pk, &p1, &m, &p2))
    return NULL;
  if (p0 != 64)
    return PyErr_Format(PyExc_ValueError, "Signature must be 64 bytes");
  if (p1 != 32)
    return PyErr_Format(PyExc_ValueError, "Public key must be 32 bytes");

  bool res = ed25519_sign_open(m, p2, pk, sig) == 0;
  return Py_BuildValue("i", res);
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
