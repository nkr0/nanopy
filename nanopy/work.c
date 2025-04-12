#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <blake2.h>
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

uint64_t xorshift1024star(void) { // nano-node/nano/node/xorshift.hpp
  const uint64_t s0 = s[p++];
  uint64_t s1 = s[p &= 15];
  s1 ^= s1 << 31;        // a
  s1 ^= s1 >> 11;        // b
  s1 ^= s0 ^ (s0 >> 30); // c
  s[p] = s1;
  return s1 * (uint64_t)1181783497276652981;
}

static inline bool is_valid(uint64_t *work, uint8_t *h32,
                            uint64_t *difficulty) {
  uint64_t b2b_h = 0;
  blake2b_state b2b;
  blake2b_init(&b2b, 8);
  blake2b_update(&b2b, work, 8);
  blake2b_update(&b2b, h32, 32);
  blake2b_final(&b2b, &b2b_h, 8);
  return b2b_h >= *difficulty;
}

static PyObject *validate(PyObject * /*self*/, PyObject *args) {
  uint8_t *h32;
  uint64_t difficulty = 0, work = 0;
  Py_ssize_t p0;

  if (!PyArg_ParseTuple(args, "Ky#K", &work, &h32, &p0, &difficulty))
    return NULL;
  assert(p0 == 32);

  return Py_BuildValue("i", is_valid(&work, h32, &difficulty));
}

static PyObject *generate(PyObject * /*self*/, PyObject *args) {
#ifdef USE_VISUAL_C
  int i, j;
#else
  size_t i, j;
#endif
  uint8_t *h32;
  uint64_t difficulty = 0, work = 0, nonce = 0;
  const size_t work_size = 1024 * 1024; // default value from nano
  Py_ssize_t p0;

  if (!PyArg_ParseTuple(args, "y#K", &h32, &p0, &difficulty))
    return NULL;
  assert(p0 == 32);

  srand(time(NULL));
  for (i = 0; i < 16; i++)
    for (j = 0; j < 4; j++)
      ((uint16_t *)&s[i])[j] = rand();

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

#pragma omp parallel
#pragma omp for
    for (i = 0; i < work_size; i++) {
      uint64_t nonce_l = nonce + i;
#ifdef USE_VISUAL_C
      if (work == 0 && is_valid(&nonce_l, h32, &difficulty)) {
#pragma omp critical
        work = nonce_l;
      }
#else
      if (is_valid(&nonce_l, h32, &difficulty)) {
#pragma omp atomic write
        work = nonce_l;
#pragma omp cancel for
      }
#pragma omp cancellation point for
#endif
    }
  }
#endif
  return Py_BuildValue("K", work);
}

static PyMethodDef m_methods[] = {{"generate", generate, METH_VARARGS, NULL},
                                  {"validate", validate, METH_VARARGS, NULL},
                                  {NULL, NULL, 0, NULL}};

static struct PyModuleDef work_module = {
    PyModuleDef_HEAD_INIT, "work", NULL, -1, m_methods, NULL, NULL, NULL, NULL};

PyMODINIT_FUNC PyInit_work(void) { return PyModule_Create(&work_module); }
