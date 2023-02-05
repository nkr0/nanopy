#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <time.h>

#ifdef HAVE_CL_CL_H
#include <CL/cl.h>
#elif HAVE_OPENCL_OPENCL_H
#include <OpenCL/opencl.h>
#else
#include <omp.h>

#include "blake2.h"
#endif

#if defined(HAVE_CL_CL_H) || defined(HAVE_OPENCL_OPENCL_H)
// this is the variable opencl_program in nano-node/nano/node/openclwork.cpp
const char *opencl_program = "\n\
enum Blake2b_IV {\n\
    iv0 = 0x6a09e667f3bcc908UL,\n\
    iv1 = 0xbb67ae8584caa73bUL,\n\
    iv2 = 0x3c6ef372fe94f82bUL,\n\
    iv3 = 0xa54ff53a5f1d36f1UL,\n\
    iv4 = 0x510e527fade682d1UL,\n\
    iv5 = 0x9b05688c2b3e6c1fUL,\n\
    iv6 = 0x1f83d9abfb41bd6bUL,\n\
    iv7 = 0x5be0cd19137e2179UL,\n\
};\n\
\n\
enum IV_Derived {\n\
    nano_xor_iv0 = 0x6a09e667f2bdc900UL,  // iv1 ^ 0x1010000 ^ outlen\n\
    nano_xor_iv4 = 0x510e527fade682f9UL,  // iv4 ^ inbytes\n\
    nano_xor_iv6 = 0xe07c265404be4294UL,  // iv6 ^ ~0\n\
};\n\
\n\
#ifdef cl_amd_media_ops\n\
#pragma OPENCL EXTENSION cl_amd_media_ops : enable\n\
static inline ulong rotr64(ulong x, int shift)\n\
{\n\
    uint2 x2 = as_uint2(x);\n\
    if (shift < 32)\n\
        return as_ulong(amd_bitalign(x2.s10, x2, shift));\n\
    return as_ulong(amd_bitalign(x2, x2.s10, (shift - 32)));\n\
}\n\
#else\n\
static inline ulong rotr64(ulong x, int shift)\n\
{\n\
    return rotate(x, 64UL - shift);\n\
}\n\
#endif\n\
\n\
#define G32(m0, m1, m2, m3, vva, vb1, vb2, vvc, vd1, vd2) \\\n\
    do {                                                  \\\n\
        vva += (ulong2)(vb1 + m0, vb2 + m2);              \\\n\
        vd1 = rotr64(vd1 ^ vva.s0, 32);                   \\\n\
        vd2 = rotr64(vd2 ^ vva.s1, 32);                   \\\n\
        vvc += (ulong2)(vd1, vd2);                        \\\n\
        vb1 = rotr64(vb1 ^ vvc.s0, 24);                   \\\n\
        vb2 = rotr64(vb2 ^ vvc.s1, 24);                   \\\n\
        vva += (ulong2)(vb1 + m1, vb2 + m3);              \\\n\
        vd1 = rotr64(vd1 ^ vva.s0, 16);                   \\\n\
        vd2 = rotr64(vd2 ^ vva.s1, 16);                   \\\n\
        vvc += (ulong2)(vd1, vd2);                        \\\n\
        vb1 = rotr64(vb1 ^ vvc.s0, 63);                   \\\n\
        vb2 = rotr64(vb2 ^ vvc.s1, 63);                   \\\n\
    } while (0)\n\
\n\
#define G2v(m0, m1, m2, m3, a, b, c, d)                                   \\\n\
    G32(m0, m1, m2, m3, vv[a / 2], vv[b / 2].s0, vv[b / 2].s1, vv[c / 2], \\\n\
        vv[d / 2].s0, vv[d / 2].s1)\n\
\n\
#define G2v_split(m0, m1, m2, m3, a, vb1, vb2, c, vd1, vd2) \\\n\
    G32(m0, m1, m2, m3, vv[a / 2], vb1, vb2, vv[c / 2], vd1, vd2)\n\
\n\
#define ROUND(m0, m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12, m13, m14, \\\n\
              m15)                                                             \\\n\
    do {                                                                       \\\n\
        G2v(m0, m1, m2, m3, 0, 4, 8, 12);                                      \\\n\
        G2v(m4, m5, m6, m7, 2, 6, 10, 14);                                     \\\n\
        G2v_split(m8, m9, m10, m11, 0, vv[5 / 2].s1, vv[6 / 2].s0, 10,         \\\n\
                  vv[15 / 2].s1, vv[12 / 2].s0);                               \\\n\
        G2v_split(m12, m13, m14, m15, 2, vv[7 / 2].s1, vv[4 / 2].s0, 8,        \\\n\
                  vv[13 / 2].s1, vv[14 / 2].s0);                               \\\n\
    } while (0)\n\
\n\
static inline ulong blake2b(ulong const nonce, __constant ulong *h)\n\
{\n\
    ulong2 vv[8] = {\n\
        {nano_xor_iv0, iv1}, {iv2, iv3},          {iv4, iv5},\n\
        {iv6, iv7},          {iv0, iv1},          {iv2, iv3},\n\
        {nano_xor_iv4, iv5}, {nano_xor_iv6, iv7},\n\
    };\n\
\n\
    ROUND(nonce, h[0], h[1], h[2], h[3], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);\n\
    ROUND(0, 0, h[3], 0, 0, 0, 0, 0, h[0], 0, nonce, h[1], 0, 0, 0, h[2]);\n\
    ROUND(0, 0, 0, nonce, 0, h[1], 0, 0, 0, 0, h[2], 0, 0, h[0], 0, h[3]);\n\
    ROUND(0, 0, h[2], h[0], 0, 0, 0, 0, h[1], 0, 0, 0, h[3], nonce, 0, 0);\n\
    ROUND(0, nonce, 0, 0, h[1], h[3], 0, 0, 0, h[0], 0, 0, 0, 0, h[2], 0);\n\
    ROUND(h[1], 0, 0, 0, nonce, 0, 0, h[2], h[3], 0, 0, 0, 0, 0, h[0], 0);\n\
    ROUND(0, 0, h[0], 0, 0, 0, h[3], 0, nonce, 0, 0, h[2], 0, h[1], 0, 0);\n\
    ROUND(0, 0, 0, 0, 0, h[0], h[2], 0, 0, nonce, 0, h[3], 0, 0, h[1], 0);\n\
    ROUND(0, 0, 0, 0, 0, h[2], nonce, 0, 0, h[1], 0, 0, h[0], h[3], 0, 0);\n\
    ROUND(0, h[1], 0, h[3], 0, 0, h[0], 0, 0, 0, 0, 0, h[2], 0, 0, nonce);\n\
    ROUND(nonce, h[0], h[1], h[2], h[3], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);\n\
    ROUND(0, 0, h[3], 0, 0, 0, 0, 0, h[0], 0, nonce, h[1], 0, 0, 0, h[2]);\n\
\n\
    return nano_xor_iv0 ^ vv[0].s0 ^ vv[4].s0;\n\
}\n\
#undef G32\n\
#undef G2v\n\
#undef G2v_split\n\
#undef ROUND\n\
\n\
__kernel void nano_work(__constant ulong *attempt,\n\
                        __global ulong *result_a,\n\
                        __constant ulong *item_a,\n\
                        __constant ulong *difficulty)\n\
{\n\
    const ulong attempt_l = *attempt + get_global_id(0);\n\
    if (blake2b(attempt_l, item_a) >= *difficulty)\n\
        *result_a = attempt_l;\n\
}\n\
";
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

static PyObject *generate(PyObject *self, PyObject *args) {
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
#ifdef USE_VISUAL_C
      if (work == 0) {
#endif
        uint64_t nonce_l = nonce + i, b2b_h = 0;
        blake2b_state b2b;

        blake2b_init(&b2b, 8);
        blake2b_update(&b2b, &nonce_l, 8);
        blake2b_update(&b2b, h32, 32);
        blake2b_final(&b2b, &b2b_h, 8);

#ifdef USE_VISUAL_C
        if (b2b_h >= difficulty) {
#pragma omp critical
          work = nonce_l;
        }
      }
#else
      if (b2b_h >= difficulty) {
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
                                  {NULL, NULL, 0, NULL}};

static struct PyModuleDef work_module = {PyModuleDef_HEAD_INIT, "work", NULL,
                                         -1, m_methods};

PyMODINIT_FUNC PyInit_work(void) { return PyModule_Create(&work_module); }
