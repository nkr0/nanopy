#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <blake2.h>
#include <ed25519-hash-custom.h>
#include <ed25519.h>
#include <stdbool.h>

#ifdef USE_OCL
#if __has_include(<CL/cl.h>)
#include <CL/cl.h>
#else
#include <OpenCL/opencl.h>
#endif
#include "opencl_program.h"
#else
#ifdef _WIN32
#include <windows.h>
#else
#include <pthread.h>
#include <unistd.h>
#endif
#endif

static const size_t n = 1 << 20;

typedef struct {
  uint64_t s[16];
  int p;
  PyObject *os;
#ifdef USE_OCL
  cl_platform_id platform;
  cl_device_id device;
  cl_context context;
  cl_command_queue queue;
  cl_program program;
  cl_mem d_nonce, d_work, d_h, d_difficulty;
  cl_kernel kernel;
#endif
} ms;

static uint64_t xorshift1024star(ms *self) {
  uint64_t s0 = self->s[self->p++], s1 = self->s[self->p &= 15];
  s1 ^= s1 << 31;
  s1 ^= s1 >> 11;
  s1 ^= s0 ^ (s0 >> 30);
  self->s[self->p] = s1;
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

static PyObject *work_validate(PyObject *Py_UNUSED(m), PyObject *args) {
  uint8_t *h;
  uint64_t difficulty, work;
  Py_ssize_t n0;

  if (!PyArg_ParseTuple(args, "Ky#K", &work, &h, &n0, &difficulty))
    return PyErr_Format(PyExc_RuntimeError, "Failed to parse arguments");
  if (n0 != 32)
    return PyErr_Format(PyExc_ValueError, "Hash must be 32 bytes");

  bool res = is_valid(work, h, difficulty);
  return Py_BuildValue("i", res);
}

#ifdef USE_OCL
static PyObject *setup_cl(PyObject *m) {
  ms *self = PyModule_GetState(m);
  int err = clGetPlatformIDs(1, &self->platform, NULL);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clGetPlatformIDs", err);
#ifndef NDEBUG
  char cl_platform_name[128];
  clGetPlatformInfo(platform, CL_PLATFORM_NAME, sizeof cl_platform_name,
                    cl_platform_name, NULL);
  printf("OpenCL: %s\n", cl_platform_name);
#endif

#ifdef USE_OCL_CPU
  err = clGetDeviceIDs(self->platform, CL_DEVICE_TYPE_CPU, 1, &self->device,
                       NULL);
#else
  err = clGetDeviceIDs(self->platform, CL_DEVICE_TYPE_GPU, 1, &self->device,
                       NULL);
#endif
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clGetDeviceIDs", err);
#ifndef NDEBUG
  char cl_device_name[128];
  clGetDeviceInfo(self->device, CL_DEVICE_NAME, sizeof cl_device_name,
                  cl_device_name, NULL);
  printf("OpenCL: %s\n", cl_device_name);
#endif

  self->context = clCreateContext(NULL, 1, &self->device, NULL, NULL, &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateContext", err);

#ifdef CL_VERSION_2_0
  self->queue = clCreateCommandQueueWithProperties(self->context, self->device,
                                                   NULL, &err);
  if (err)
    return PyErr_Format(
        PyExc_RuntimeError,
        "OpenCL:%d: Failed to clCreateCommandQueueWithProperties", err);
#else
  self->queue = clCreateCommandQueue(self->context, self->device, 0, &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateCommandQueue", err);
#endif

  self->program =
      clCreateProgramWithSource(self->context, 1, opencl_program, NULL, &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateProgramWithSource", err);

  err = clBuildProgram(self->program, 0, NULL, NULL, NULL, NULL);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clBuildProgram", err);

  self->d_nonce =
      clCreateBuffer(self->context, CL_MEM_READ_ONLY, 8, NULL, &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateBuffer", err);

  self->d_work =
      clCreateBuffer(self->context, CL_MEM_WRITE_ONLY, 8, NULL, &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateBuffer", err);

  self->d_h = clCreateBuffer(self->context, CL_MEM_READ_ONLY, 32, NULL, &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateBuffer", err);

  self->d_difficulty =
      clCreateBuffer(self->context, CL_MEM_READ_ONLY, 8, NULL, &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateBuffer", err);

  self->kernel = clCreateKernel(self->program, "nano_work", &err);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clCreateKernel", err);

  err = clSetKernelArg(self->kernel, 0, sizeof(cl_mem), &self->d_nonce);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clSetKernelArg", err);

  err = clSetKernelArg(self->kernel, 1, sizeof(cl_mem), &self->d_work);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clSetKernelArg", err);

  err = clSetKernelArg(self->kernel, 2, sizeof(cl_mem), &self->d_h);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clSetKernelArg", err);

  err = clSetKernelArg(self->kernel, 3, sizeof(cl_mem), &self->d_difficulty);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clSetKernelArg", err);

  return NULL;
}

static PyObject *work_generate_impl(ms *self, uint8_t *h, uint64_t difficulty) {
  uint64_t work = 0;

  int err = clEnqueueWriteBuffer(self->queue, self->d_work, CL_TRUE, 0, 8,
                                 &work, 0, NULL, NULL);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clEnqueueWriteBuffer", err);

  err = clEnqueueWriteBuffer(self->queue, self->d_h, CL_TRUE, 0, 32, h, 0, NULL,
                             NULL);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clEnqueueWriteBuffer", err);

  err = clEnqueueWriteBuffer(self->queue, self->d_difficulty, CL_TRUE, 0, 8,
                             &difficulty, 0, NULL, NULL);
  if (err)
    return PyErr_Format(PyExc_RuntimeError,
                        "OpenCL:%d: Failed to clEnqueueWriteBuffer", err);

  while (!work) {
    const uint64_t nonce = xorshift1024star(self);

    err = clEnqueueWriteBuffer(self->queue, self->d_nonce, CL_TRUE, 0, 8,
                               &nonce, 0, NULL, NULL);
    if (err)
      return PyErr_Format(PyExc_RuntimeError,
                          "OpenCL:%d: Failed to clEnqueueWriteBuffer", err);

    err = clEnqueueNDRangeKernel(self->queue, self->kernel, 1, NULL, &n, NULL,
                                 0, NULL, NULL);
    if (err)
      return PyErr_Format(PyExc_RuntimeError,
                          "OpenCL:%d: Failed to clEnqueueNDRangeKernel", err);

    err = clEnqueueReadBuffer(self->queue, self->d_work, CL_TRUE, 0, 8, &work,
                              0, NULL, NULL);
    if (err)
      return PyErr_Format(PyExc_RuntimeError,
                          "OpenCL:%d: Failed to clEnqueueReadBuffer", err);
  }

  return Py_BuildValue("K", work);
}
#else
typedef struct {
  uint8_t *h;
  uint64_t difficulty, nonce, result;
} thread_arg_t;

#ifdef _WIN32
static DWORD WINAPI worker(LPVOID arg) {
#else
static void *worker(void *arg) {
#endif
  thread_arg_t *a = (thread_arg_t *)arg;
  for (uint64_t i = 0; i < n; i++) {
    if (is_valid(a->nonce + i, a->h, a->difficulty)) {
      a->result = a->nonce + i;
      break;
    }
  }
  return 0;
}

static PyObject *work_generate_impl(ms *self, uint8_t *h, uint64_t difficulty) {
  uint64_t work = 0;
  Py_BEGIN_ALLOW_THREADS;
#ifdef _WIN32
  long NUM_THREADS = GetActiveProcessorCount(ALL_PROCESSOR_GROUPS);
  HANDLE *threads = malloc(NUM_THREADS * sizeof(HANDLE));
#else
  long NUM_THREADS = sysconf(_SC_NPROCESSORS_ONLN);
  pthread_t *threads = malloc(NUM_THREADS * sizeof(pthread_t));
#endif
  thread_arg_t *wargs = malloc(NUM_THREADS * sizeof(thread_arg_t));
  while (!work) {
    for (int t = 0; t < NUM_THREADS; t++) {
      wargs[t].h = h;
      wargs[t].difficulty = difficulty;
      wargs[t].nonce = xorshift1024star(self);
      wargs[t].result = 0;
#ifdef _WIN32
      threads[t] = CreateThread(NULL, 0, worker, &wargs[t], 0, NULL);
#else
      pthread_create(&threads[t], NULL, worker, &wargs[t]);
#endif
    }
    for (int t = 0; t < NUM_THREADS; t++) {
#ifdef _WIN32
      WaitForSingleObject(threads[t], INFINITE);
      CloseHandle(threads[t]);
#else
      pthread_join(threads[t], NULL);
#endif
      if (wargs[t].result)
        work = wargs[t].result;
    }
  }
  free(threads);
  free(wargs);
  Py_END_ALLOW_THREADS;
  return Py_BuildValue("K", work);
}
#endif

static PyObject *work_generate(PyObject *m, PyObject *args) {
  uint8_t *h;
  uint64_t difficulty;
  Py_ssize_t n0;
  ms *self = PyModule_GetState(m);

  if (!PyArg_ParseTuple(args, "y#K", &h, &n0, &difficulty))
    return PyErr_Format(PyExc_RuntimeError, "Failed to parse arguments");
  if (n0 != 32)
    return PyErr_Format(PyExc_ValueError, "Hash must be 32 bytes");

  return work_generate_impl(self, h, difficulty);
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

static PyObject *publickey(PyObject *Py_UNUSED(m), PyObject *args) {
  uint8_t *sk;
  Py_ssize_t n0;
  ed25519_public_key pk;

  if (!PyArg_ParseTuple(args, "y#", &sk, &n0))
    return PyErr_Format(PyExc_RuntimeError, "Failed to parse arguments");
  if (n0 != 32)
    return PyErr_Format(PyExc_ValueError, "Secret key must be 32 bytes");

  ed25519_publickey(sk, pk);
  return Py_BuildValue("y#", pk, sizeof(ed25519_public_key));
}

static PyObject *sign(PyObject *m, PyObject *args) {
  uint8_t *sk, *msg, *r, R[32];
  Py_ssize_t n0, n1, n2 = 0;

  if (!PyArg_ParseTuple(args, "y#y#|y#", &sk, &n0, &msg, &n1, &r, &n2))
    return PyErr_Format(PyExc_RuntimeError, "Failed to parse arguments");
  if (n0 != 32)
    return PyErr_Format(PyExc_ValueError, "Secret key must be 32 bytes");

  if (n2 != 32) {
    ms *self = PyModule_GetState(m);
    PyObject *seed = PyObject_CallMethod(self->os, "urandom", "i", sizeof R);
    PyBytes_AsStringAndSize(seed, (char **)R, &n1);
    Py_DECREF(seed);
    r = &R[0];
  }

  ed25519_public_key pk;
  ed25519_publickey(sk, pk);
  ed25519_signature sig;
  ed25519_sign(msg, n1, r, sk, pk, sig);
  return Py_BuildValue("y#", sig, sizeof(ed25519_signature));
}

static PyObject *verify_signature(PyObject *Py_UNUSED(m), PyObject *args) {
  uint8_t *sig, *pk, *msg;
  Py_ssize_t n0, n1, n2;

  if (!PyArg_ParseTuple(args, "y#y#y#", &sig, &n0, &pk, &n1, &msg, &n2))
    return PyErr_Format(PyExc_RuntimeError, "Failed to parse arguments");
  if (n0 != 64)
    return PyErr_Format(PyExc_ValueError, "Signature must be 64 bytes");
  if (n1 != 32)
    return PyErr_Format(PyExc_ValueError, "Public key must be 32 bytes");

  bool res = ed25519_sign_open(msg, n2, pk, sig) == 0;
  return Py_BuildValue("i", res);
}

static PyMethodDef m[] = {
    {"work_generate", work_generate, METH_VARARGS, NULL},
    {"work_validate", work_validate, METH_VARARGS, NULL},
    {"publickey", publickey, METH_VARARGS, NULL},
    {"sign", sign, METH_VARARGS, NULL},
    {"verify_signature", verify_signature, METH_VARARGS, NULL},
    {}};

static int m_exec(PyObject *m) {
  ms *self = PyModule_GetState(m);
  Py_ssize_t n;

  self->os = PyImport_ImportModule("os");
  PyObject *seed =
      PyObject_CallMethod(self->os, "urandom", "i", sizeof self->s);
  PyBytes_AsStringAndSize(seed, (char **)self->s, &n);
  Py_DECREF(seed);
  self->p = 0;

#ifdef USE_OCL
  if (setup_cl(m))
    return -1;
#endif

  return 0;
}

static void m_free(void *m) {
  ms *self = PyModule_GetState((PyObject *)m);
  Py_DECREF(self->os);
#ifdef USE_OCL
  clReleaseKernel(self->kernel);
  clReleaseMemObject(self->d_nonce);
  clReleaseMemObject(self->d_work);
  clReleaseMemObject(self->d_h);
  clReleaseMemObject(self->d_difficulty);
  clReleaseProgram(self->program);
  clReleaseCommandQueue(self->queue);
  clReleaseContext(self->context);
#endif
}

static PyModuleDef_Slot slots[] = {{Py_mod_exec, m_exec},
#ifdef Py_GIL_DISABLED
                                   {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
                                   {0, NULL}};

static PyModuleDef ext = {PyModuleDef_HEAD_INIT, .m_name = "ext",
                          .m_size = sizeof(ms),  .m_methods = m,
                          .m_slots = slots,      .m_free = m_free};

PyMODINIT_FUNC PyInit_ext(void) { return PyModuleDef_Init(&ext); }
