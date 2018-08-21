#include <Python.h>
#include <fcntl.h>
#include <time.h>
#include <unistd.h>

#ifdef HAVE_OPENCL_CL_H
#include <OpenCL/opencl.h>
#elif HAVE_CL_CL_H
#include <CL/opencl.h>
#else
#include <blake2.h>
#include <omp.h>
#endif

#define WORK_SIZE 1024 * 1024  // default value from nano

static uint64_t s[16];
static int p;

uint64_t xorshift1024star(void) {  // raiblocks/rai/node/xorshift.hpp
  const uint64_t s0 = s[p++];
  uint64_t s1 = s[p &= 15];
  s1 ^= s1 << 31;         // a
  s1 ^= s1 >> 11;         // b
  s1 ^= s0 ^ (s0 >> 30);  // c
  s[p] = s1;
  return s1 * (uint64_t)1181783497276652981;
}

void swapLong(uint64_t *X) {
  uint64_t x = *X;
  x = (x & 0x00000000FFFFFFFF) << 32 | (x & 0xFFFFFFFF00000000) >> 32;
  x = (x & 0x0000FFFF0000FFFF) << 16 | (x & 0xFFFF0000FFFF0000) >> 16;
  x = (x & 0x00FF00FF00FF00FF) << 8 | (x & 0xFF00FF00FF00FF00) >> 8;
}

static PyObject *generate(PyObject *self, PyObject *args) {
  int i = 0;
  uint8_t *str;
  uint64_t workb = 0, r_str = 0;

  if (!PyArg_ParseTuple(args, "y#", &str, &i)) return NULL;

  srand(time(NULL));
  for (i = 0; i < 16; i++)
    for (int j = 0; j < 4; j++) ((uint16_t *)&s[i])[j] = rand();

  i = 0;

#if defined(HAVE_OPENCL_CL_H) || defined(HAVE_CL_CL_H)
  cl_platform_id cpPlatform;
  cl_uint num;

  clGetPlatformIDs(1, &cpPlatform, &num);
  if (num > 0) {
    char *opencl_program;
    size_t length;
    const size_t work_size = WORK_SIZE;
    cl_mem d_rand, d_work, d_str;
    cl_device_id device_id;
    cl_program program;

    clGetDeviceIDs(cpPlatform, CL_DEVICE_TYPE_GPU, 1, &device_id, NULL);
    cl_context context = clCreateContext(0, 1, &device_id, NULL, NULL, NULL);
    cl_command_queue queue =
        clCreateCommandQueueWithProperties(context, device_id, 0, NULL);

    FILE *f = fopen("work.cl", "rb");

    fseek(f, 0, SEEK_END);
    length = ftell(f);
    rewind(f);
    opencl_program = malloc(length);
    if (opencl_program) fread(opencl_program, 1, length, f);
    fclose(f);

    program = clCreateProgramWithSource(
        context, 1, (const char **)&opencl_program, &length, NULL);
    clBuildProgram(program, 0, NULL, NULL, NULL, NULL);

    d_rand = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR,
                            8, &r_str, NULL);
    d_work = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR,
                            8, &workb, NULL);
    d_str = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR,
                           32, str, NULL);

    cl_kernel kernel = clCreateKernel(program, "raiblocks_work", NULL);

    clSetKernelArg(kernel, 0, sizeof(d_rand), &d_rand);
    clSetKernelArg(kernel, 1, sizeof(d_work), &d_work);
    clSetKernelArg(kernel, 2, sizeof(d_str), &d_str);

    while (i == 0) {
      r_str = xorshift1024star();

      clEnqueueWriteBuffer(queue, d_rand, CL_FALSE, 0, 8, &r_str, 0, NULL,
                           NULL);
      clEnqueueWriteBuffer(queue, d_str, CL_FALSE, 0, 32, str, 0, NULL, NULL);

      clEnqueueNDRangeKernel(queue, kernel, 1, NULL, &work_size, NULL, 0, NULL,
                             NULL);

      clEnqueueReadBuffer(queue, d_work, CL_FALSE, 0, 8, &workb, 0, NULL, NULL);

      clFinish(queue);

      if (workb != 0) i = 1;
    }

    free(opencl_program);
    clReleaseMemObject(d_rand);
    clReleaseMemObject(d_work);
    clReleaseMemObject(d_str);
    clReleaseKernel(kernel);
    clReleaseProgram(program);
    clReleaseCommandQueue(queue);
    clReleaseContext(context);
  }
#else
  while (i == 0) {
    r_str = xorshift1024star();

#pragma omp parallel
#pragma omp for
    for (int j = 0; j < WORK_SIZE; j++) {
      uint64_t r_str_l = r_str + j, b2b_b = 0;
      blake2b_state b2b;

      blake2b_init(&b2b, 8);
      blake2b_update(&b2b, (uint8_t *)&r_str_l, 8);
      blake2b_update(&b2b, str, 32);
      blake2b_final(&b2b, (uint8_t *)&b2b_b, 8);

      swapLong(&b2b_b);

      if (b2b_b >= 0xffffffc000000000ul) {
#pragma omp atomic write
        workb = r_str_l;
        i = 1;
#pragma omp cancel for
      }
#pragma omp cancellation point for
    }
  }
#endif
  swapLong(&workb);
  return Py_BuildValue("K", workb);
}

static PyMethodDef generate_method[] = {
    {"generate", generate, METH_VARARGS, NULL}, {NULL, NULL, 0, NULL}};

static struct PyModuleDef work_module = {PyModuleDef_HEAD_INIT, "work", NULL,
                                         -1, generate_method};

PyMODINIT_FUNC PyInit_work(void) {
  PyObject *m = PyModule_Create(&work_module);
  if (m == NULL) return NULL;
  return m;
}
