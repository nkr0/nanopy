#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <blake2.h>
#include <ed25519-hash-custom.h>
#include <ed25519.h>
#include <stdbool.h>

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

static uint64_t s[16];
static int p;

static uint64_t xorshift1024star() {
  uint64_t s0 = s[p++], s1 = s[p &= 15];
  s1 ^= s1 << 31;
  s1 ^= s1 >> 11;
  s1 ^= s0 ^ (s0 >> 30);
  s[p] = s1;
  return s1 * 1181783497276652981ull;
}

static bool is_valid(uint64_t work, uint8_t *h, uint64_t difficulty) {
  uint64_t d;
  blake2b_state b;
  blake2b_init(&b, 8);
  blake2b_update(&b, &work, 8);
  blake2b_update(&b, h, 32);
  blake2b_final(&b, &d, 8);
  return d >= difficulty;
}

static PyObject *work_validate(PyObject *Py_UNUSED(self), PyObject *args) {
  uint8_t *h;
  uint64_t difficulty, work;
  Py_ssize_t n0;

  if (!PyArg_ParseTuple(args, "Ky#K", &work, &h, &n0, &difficulty))
    return NULL;
  if (n0 != 32)
    return PyErr_Format(PyExc_ValueError, "Hash must be 32 bytes");

  bool res = is_valid(work, h, difficulty);
  return Py_BuildValue("i", res);
}

static PyObject *work_generate(PyObject *Py_UNUSED(self), PyObject *args) {
  uint8_t *h, *r;
  uint64_t difficulty, work = 0, nonce, n = 1024 * 1024;
  Py_ssize_t n0, n1;

  if (!PyArg_ParseTuple(args, "y#Ky#", &h, &n0, &difficulty, &r, &n1))
    return NULL;
  if (n0 != 32)
    return PyErr_Format(PyExc_ValueError, "Hash must be 32 bytes");
  if (n1 != sizeof s)
    return PyErr_Format(PyExc_ValueError, "Random must be 128 bytes");

  p = 0;
  memcpy(s, r, sizeof s);

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
  clGetPlatformInfo(cpPlatform, CL_PLATFORM_NAME, sizeof cl_platform_name,
                    cl_platform_name, NULL);
  printf("OpenCL: %s\n", cl_platform_name);
#endif

  size_t length = strlen(opencl_program);
  cl_mem d_nonce, d_work, d_h, d_difficulty;
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
  clGetDeviceInfo(device_id, CL_DEVICE_NAME, sizeof cl_device_name,
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

  d_h = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, 32, h,
                       &err);
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

  err = clSetKernelArg(kernel, 0, sizeof(cl_mem), &d_nonce);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clSetKernelArg", err);

  err = clSetKernelArg(kernel, 1, sizeof(cl_mem), &d_work);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clSetKernelArg", err);

  err = clSetKernelArg(kernel, 2, sizeof(cl_mem), &d_h);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clSetKernelArg", err);

  err = clSetKernelArg(kernel, 3, sizeof(cl_mem), &d_difficulty);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clSetKernelArg", err);

  err = clEnqueueWriteBuffer(queue, d_h, CL_FALSE, 0, 32, h, 0, NULL, NULL);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clEnqueueWriteBuffer", err);

  err = clEnqueueWriteBuffer(queue, d_difficulty, CL_FALSE, 0, 8, &difficulty,
                             0, NULL, NULL);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clEnqueueWriteBuffer", err);

  while (!work) {
    nonce = xorshift1024star();

    err = clEnqueueWriteBuffer(queue, d_nonce, CL_FALSE, 0, 8, &nonce, 0, NULL,
                               NULL);
    if (err)
      return PyErr_Format(PyExc_RuntimeError,
                          "OpenCL:%d: Failed to clEnqueueWriteBuffer", err);

    err =
        clEnqueueNDRangeKernel(queue, kernel, 1, NULL, &n, NULL, 0, NULL, NULL);
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

  err = clReleaseMemObject(d_h);
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
    nonce = xorshift1024star();
    int i;
#pragma omp parallel for default(none) shared(n, work, nonce, h, difficulty)
    for (i = 0; i < (int)n; i++) {
      if (!work && is_valid(nonce + i, h, difficulty)) {
#pragma omp critical
        work = nonce + i;
      }
    }
  }
#endif
  return Py_BuildValue("K", work);
}

void ed25519_randombytes_unsafe(void *Py_UNUSED(out),
                                size_t Py_UNUSED(outlen)) {}

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

static PyObject *publickey(PyObject *Py_UNUSED(self), PyObject *args) {
  uint8_t *sk;
  Py_ssize_t n0;
  ed25519_public_key pk;

  if (!PyArg_ParseTuple(args, "y#", &sk, &n0))
    return NULL;
  if (n0 != 32)
    return PyErr_Format(PyExc_ValueError, "Secret key must be 32 bytes");

  ed25519_publickey(sk, pk);
  return Py_BuildValue("y#", pk, sizeof(ed25519_public_key));
}

static PyObject *sign(PyObject *Py_UNUSED(self), PyObject *args) {
  uint8_t *sk, *m, *r;
  Py_ssize_t n0, n1, n2;

  if (!PyArg_ParseTuple(args, "y#y#y#", &sk, &n0, &m, &n1, &r, &n2))
    return NULL;
  if (n0 != 32)
    return PyErr_Format(PyExc_ValueError, "Secret key must be 32 bytes");
  if (n2 != 32)
    return PyErr_Format(PyExc_ValueError, "Random must be 32 bytes");

  ed25519_public_key pk;
  ed25519_publickey(sk, pk);
  ed25519_signature sig;
  ed25519_sign(m, n1, r, sk, pk, sig);
  return Py_BuildValue("y#", sig, sizeof(ed25519_signature));
}

static PyObject *verify_signature(PyObject *Py_UNUSED(self), PyObject *args) {
  uint8_t *sig, *pk, *m;
  Py_ssize_t n0, n1, n2;

  if (!PyArg_ParseTuple(args, "y#y#y#", &sig, &n0, &pk, &n1, &m, &n2))
    return NULL;
  if (n0 != 64)
    return PyErr_Format(PyExc_ValueError, "Signature must be 64 bytes");
  if (n1 != 32)
    return PyErr_Format(PyExc_ValueError, "Public key must be 32 bytes");

  bool res = ed25519_sign_open(m, n2, pk, sig) == 0;
  return Py_BuildValue("i", res);
}

static PyMethodDef m[] = {{"work_generate", work_generate, METH_VARARGS},
                          {"work_validate", work_validate, METH_VARARGS},
                          {"publickey", publickey, METH_VARARGS},
                          {"sign", sign, METH_VARARGS},
                          {"verify_signature", verify_signature, METH_VARARGS},
                          {}};

static struct PyModuleDef ext = {PyModuleDef_HEAD_INIT, "ext", NULL, 0, m};

PyMODINIT_FUNC PyInit_ext(void) { return PyModule_Create(&ext); }
