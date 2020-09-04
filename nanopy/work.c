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
const char *opencl_program = R"%%%(
enum Blake2b_IV {
    iv0 = 0x6a09e667f3bcc908UL,
    iv1 = 0xbb67ae8584caa73bUL,
    iv2 = 0x3c6ef372fe94f82bUL,
    iv3 = 0xa54ff53a5f1d36f1UL,
    iv4 = 0x510e527fade682d1UL,
    iv5 = 0x9b05688c2b3e6c1fUL,
    iv6 = 0x1f83d9abfb41bd6bUL,
    iv7 = 0x5be0cd19137e2179UL,
};

enum IV_Derived {
    nano_xor_iv0 = 0x6a09e667f2bdc900UL,  // iv1 ^ 0x1010000 ^ outlen
    nano_xor_iv4 = 0x510e527fade682f9UL,  // iv4 ^ inbytes
    nano_xor_iv6 = 0xe07c265404be4294UL,  // iv6 ^ ~0
};

#ifdef cl_amd_media_ops
#pragma OPENCL EXTENSION cl_amd_media_ops : enable
static inline ulong rotr64(ulong x, int shift)
{
    uint2 x2 = as_uint2(x);
    if (shift < 32)
        return as_ulong(amd_bitalign(x2.s10, x2, shift));
    return as_ulong(amd_bitalign(x2, x2.s10, (shift - 32)));
}
#else
static inline ulong rotr64(ulong x, int shift)
{
    return rotate(x, 64UL - shift);
}
#endif

#define G32(m0, m1, m2, m3, vva, vb1, vb2, vvc, vd1, vd2) \
    do {                                                  \
        vva += (ulong2)(vb1 + m0, vb2 + m2);              \
        vd1 = rotr64(vd1 ^ vva.s0, 32);                   \
        vd2 = rotr64(vd2 ^ vva.s1, 32);                   \
        vvc += (ulong2)(vd1, vd2);                        \
        vb1 = rotr64(vb1 ^ vvc.s0, 24);                   \
        vb2 = rotr64(vb2 ^ vvc.s1, 24);                   \
        vva += (ulong2)(vb1 + m1, vb2 + m3);              \
        vd1 = rotr64(vd1 ^ vva.s0, 16);                   \
        vd2 = rotr64(vd2 ^ vva.s1, 16);                   \
        vvc += (ulong2)(vd1, vd2);                        \
        vb1 = rotr64(vb1 ^ vvc.s0, 63);                   \
        vb2 = rotr64(vb2 ^ vvc.s1, 63);                   \
    } while (0)

#define G2v(m0, m1, m2, m3, a, b, c, d)                                   \
    G32(m0, m1, m2, m3, vv[a / 2], vv[b / 2].s0, vv[b / 2].s1, vv[c / 2], \
        vv[d / 2].s0, vv[d / 2].s1)

#define G2v_split(m0, m1, m2, m3, a, vb1, vb2, c, vd1, vd2) \
    G32(m0, m1, m2, m3, vv[a / 2], vb1, vb2, vv[c / 2], vd1, vd2)

#define ROUND(m0, m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12, m13, m14, \
              m15)                                                             \
    do {                                                                       \
        G2v(m0, m1, m2, m3, 0, 4, 8, 12);                                      \
        G2v(m4, m5, m6, m7, 2, 6, 10, 14);                                     \
        G2v_split(m8, m9, m10, m11, 0, vv[5 / 2].s1, vv[6 / 2].s0, 10,         \
                  vv[15 / 2].s1, vv[12 / 2].s0);                               \
        G2v_split(m12, m13, m14, m15, 2, vv[7 / 2].s1, vv[4 / 2].s0, 8,        \
                  vv[13 / 2].s1, vv[14 / 2].s0);                               \
    } while (0)

static inline ulong blake2b(ulong const nonce, __constant ulong *h)
{
    ulong2 vv[8] = {
        {nano_xor_iv0, iv1}, {iv2, iv3},          {iv4, iv5},
        {iv6, iv7},          {iv0, iv1},          {iv2, iv3},
        {nano_xor_iv4, iv5}, {nano_xor_iv6, iv7},
    };

    ROUND(nonce, h[0], h[1], h[2], h[3], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
    ROUND(0, 0, h[3], 0, 0, 0, 0, 0, h[0], 0, nonce, h[1], 0, 0, 0, h[2]);
    ROUND(0, 0, 0, nonce, 0, h[1], 0, 0, 0, 0, h[2], 0, 0, h[0], 0, h[3]);
    ROUND(0, 0, h[2], h[0], 0, 0, 0, 0, h[1], 0, 0, 0, h[3], nonce, 0, 0);
    ROUND(0, nonce, 0, 0, h[1], h[3], 0, 0, 0, h[0], 0, 0, 0, 0, h[2], 0);
    ROUND(h[1], 0, 0, 0, nonce, 0, 0, h[2], h[3], 0, 0, 0, 0, 0, h[0], 0);
    ROUND(0, 0, h[0], 0, 0, 0, h[3], 0, nonce, 0, 0, h[2], 0, h[1], 0, 0);
    ROUND(0, 0, 0, 0, 0, h[0], h[2], 0, 0, nonce, 0, h[3], 0, 0, h[1], 0);
    ROUND(0, 0, 0, 0, 0, h[2], nonce, 0, 0, h[1], 0, 0, h[0], h[3], 0, 0);
    ROUND(0, h[1], 0, h[3], 0, 0, h[0], 0, 0, 0, 0, 0, h[2], 0, 0, nonce);
    ROUND(nonce, h[0], h[1], h[2], h[3], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
    ROUND(0, 0, h[3], 0, 0, 0, 0, 0, h[0], 0, nonce, h[1], 0, 0, 0, h[2]);

    return nano_xor_iv0 ^ vv[0].s0 ^ vv[4].s0;
}
#undef G32
#undef G2v
#undef G2v_split
#undef ROUND

__kernel void nano_work(__constant ulong *attempt,
                        __global ulong *result_a,
                        __constant uchar *item_a,
                        __constant ulong *difficulty)
{
    const ulong attempt_l = *attempt + get_global_id(0);
    if (blake2b(attempt_l, item_a) >= *difficulty)
        *result_a = attempt_l;
}
)%%%";
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

  srand(time(NULL));
  for (i = 0; i < 16; i++)
    for (j = 0; j < 4; j++)
      ((uint16_t *)&s[i])[j] = rand();

#if defined(HAVE_CL_CL_H) || defined(HAVE_OPENCL_OPENCL_H)
  int err;
  cl_uint num;
  cl_platform_id cpPlatform;

  err = clGetPlatformIDs(1, &cpPlatform, &num);
  if (err != CL_SUCCESS) {
    printf("clGetPlatformIDs failed with error code %d\n", err);
    goto FAIL;
  } else if (num == 0) {
    printf("clGetPlatformIDs failed to find a gpu device\n");
    goto FAIL;
  } else {
    size_t length = strlen(opencl_program);
    cl_mem d_nonce, d_work, d_h32, d_difficulty;
    cl_device_id device_id;
    cl_context context;
    cl_command_queue queue;
    cl_program program;
    cl_kernel kernel;

    err = clGetDeviceIDs(cpPlatform, CL_DEVICE_TYPE_GPU, 1, &device_id, NULL);
    if (err != CL_SUCCESS) {
      printf("clGetDeviceIDs failed with error code %d\n", err);
      goto FAIL;
    }

    context = clCreateContext(0, 1, &device_id, NULL, NULL, &err);
    if (err != CL_SUCCESS) {
      printf("clCreateContext failed with error code %d\n", err);
      goto FAIL;
    }

#ifndef __APPLE__
    queue = clCreateCommandQueueWithProperties(context, device_id, 0, &err);
    if (err != CL_SUCCESS) {
      printf("clCreateCommandQueueWithProperties failed with error code %d\n",
             err);
      goto FAIL;
    }
#else
    queue = clCreateCommandQueue(context, device_id, 0, &err);
    if (err != CL_SUCCESS) {
      printf("clCreateCommandQueue failed with error code %d\n", err);
      goto FAIL;
    }
#endif

    program = clCreateProgramWithSource(
        context, 1, (const char **)&opencl_program, &length, &err);
    if (err != CL_SUCCESS) {
      printf("clCreateProgramWithSource failed with error code %d\n", err);
      goto FAIL;
    }

    err = clBuildProgram(program, 0, NULL, NULL, NULL, NULL);
    if (err != CL_SUCCESS) {
      printf("clBuildProgram failed with error code %d\n", err);
      goto FAIL;
    }

    d_nonce = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR,
                             8, &nonce, &err);
    if (err != CL_SUCCESS) {
      printf("clCreateBuffer failed with error code %d\n", err);
      goto FAIL;
    }

    d_work = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR,
                            8, &work, &err);
    if (err != CL_SUCCESS) {
      printf("clCreateBuffer failed with error code %d\n", err);
      goto FAIL;
    }

    d_h32 = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR,
                           32, h32, &err);
    if (err != CL_SUCCESS) {
      printf("clCreateBuffer failed with error code %d\n", err);
      goto FAIL;
    }

    d_difficulty =
        clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, 8,
                       &difficulty, &err);
    if (err != CL_SUCCESS) {
      printf("clCreateBuffer failed with error code %d\n", err);
      goto FAIL;
    }

    kernel = clCreateKernel(program, "nano_work", &err);
    if (err != CL_SUCCESS) {
      printf("clCreateKernel failed with error code %d\n", err);
      goto FAIL;
    }

    err = clSetKernelArg(kernel, 0, sizeof(d_nonce), &d_nonce);
    if (err != CL_SUCCESS) {
      printf("clSetKernelArg failed with error code %d\n", err);
      goto FAIL;
    }

    err = clSetKernelArg(kernel, 1, sizeof(d_work), &d_work);
    if (err != CL_SUCCESS) {
      printf("clSetKernelArg failed with error code %d\n", err);
      goto FAIL;
    }

    err = clSetKernelArg(kernel, 2, sizeof(d_h32), &d_h32);
    if (err != CL_SUCCESS) {
      printf("clSetKernelArg failed with error code %d\n", err);
      goto FAIL;
    }

    err = clSetKernelArg(kernel, 3, sizeof(d_difficulty), &d_difficulty);
    if (err != CL_SUCCESS) {
      printf("clSetKernelArg failed with error code %d\n", err);
      goto FAIL;
    }

    err =
        clEnqueueWriteBuffer(queue, d_h32, CL_FALSE, 0, 32, h32, 0, NULL, NULL);
    if (err != CL_SUCCESS) {
      printf("clEnqueueWriteBuffer failed with error code %d\n", err);
      goto FAIL;
    }

    err = clEnqueueWriteBuffer(queue, d_difficulty, CL_FALSE, 0, 8, &difficulty,
                               0, NULL, NULL);
    if (err != CL_SUCCESS) {
      printf("clEnqueueWriteBuffer failed with error code %d\n", err);
      goto FAIL;
    }

    while (work == 0) {
      nonce = xorshift1024star();

      err = clEnqueueWriteBuffer(queue, d_nonce, CL_FALSE, 0, 8, &nonce, 0,
                                 NULL, NULL);
      if (err != CL_SUCCESS) {
        printf("clEnqueueWriteBuffer failed with error code %d\n", err);
        goto FAIL;
      }

      err = clEnqueueNDRangeKernel(queue, kernel, 1, NULL, &work_size, NULL, 0,
                                   NULL, NULL);
      if (err != CL_SUCCESS) {
        printf("clEnqueueNDRangeKernel failed with error code %d\n", err);
        goto FAIL;
      }

      err = clEnqueueReadBuffer(queue, d_work, CL_FALSE, 0, 8, &work, 0, NULL,
                                NULL);
      if (err != CL_SUCCESS) {
        printf("clEnqueueReadBuffer failed with error code %d\n", err);
        goto FAIL;
      }

      err = clFinish(queue);
      if (err != CL_SUCCESS) {
        printf("clFinish failed with error code %d\n", err);
        goto FAIL;
      }
    }

    err = clReleaseMemObject(d_nonce);
    if (err != CL_SUCCESS) {
      printf("clReleaseMemObject failed with error code %d\n", err);
      goto FAIL;
    }
    err = clReleaseMemObject(d_work);
    if (err != CL_SUCCESS) {
      printf("clReleaseMemObject failed with error code %d\n", err);
      goto FAIL;
    }
    err = clReleaseMemObject(d_h32);
    if (err != CL_SUCCESS) {
      printf("clReleaseMemObject failed with error code %d\n", err);
      goto FAIL;
    }
    err = clReleaseMemObject(d_difficulty);
    if (err != CL_SUCCESS) {
      printf("clReleaseMemObject failed with error code %d\n", err);
      goto FAIL;
    }
    err = clReleaseKernel(kernel);
    if (err != CL_SUCCESS) {
      printf("clReleaseKernel failed with error code %d\n", err);
      goto FAIL;
    }
    err = clReleaseProgram(program);
    if (err != CL_SUCCESS) {
      printf("clReleaseProgram failed with error code %d\n", err);
      goto FAIL;
    }
    err = clReleaseCommandQueue(queue);
    if (err != CL_SUCCESS) {
      printf("clReleaseCommandQueue failed with error code %d\n", err);
      goto FAIL;
    }
    err = clReleaseContext(context);
    if (err != CL_SUCCESS) {
      printf("clReleaseContext failed with error code %d\n", err);
      goto FAIL;
    }
  }
FAIL:
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

PyMODINIT_FUNC PyInit_work(void) {
  PyObject *m = PyModule_Create(&work_module);
  if (m == NULL)
    return NULL;
  return m;
}
