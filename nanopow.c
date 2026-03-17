#include<stdlib.h>
#include<stdio.h>
#include<unistd.h>
#include<string.h>
#include<fcntl.h>

#ifdef HAVE_OPENCL_CL_H
#include<OpenCL/opencl.h>
#elif HAVE_CL_CL_H
#include<CL/opencl.h>
//~ #include<CL/cl_intel.h>
#else
#include<omp.h>
#include<blake2.h>
#endif

#define WORK_SIZE 1024*1024 // default value from nano

///////////////////////////////////////////////////////////////////////////////////
// 64-bit version of Mersenne Twister pseudorandom number generator.
// http://www.math.sci.hiroshima-u.ac.jp/~m-mat/MT/VERSIONS/C-LANG/mt19937-64.c
///////////////////////////////////////////////////////////////////////////////////

#define NN 312
#define MM 156
#define MATRIX_A 0xB5026F5AA96619E9ULL
#define UM 0xFFFFFFFF80000000ULL /* Most significant 33 bits */
#define LM 0x7FFFFFFFULL /* Least significant 31 bits */

/* The array for the state vector */
static unsigned long long mt[NN]; 
/* mti==NN+1 means mt[NN] is not initialized */
static int mti=NN+1; 

/* initializes mt[NN] with a seed */
void init_genrand64(unsigned long long seed)
{
    mt[0] = seed;
    for (mti=1; mti<NN; mti++) 
        mt[mti] =  (6364136223846793005ULL * (mt[mti-1] ^ (mt[mti-1] >> 62)) + mti);
}

/* generates a random number on [0, 2^64-1]-interval */
unsigned long long genrand64_int64(void)
{
    int i;
    unsigned long long x;
    static unsigned long long mag01[2]={0ULL, MATRIX_A};

    if (mti >= NN) { /* generate NN words at one time */

        /* if init_genrand64() has not been called, */
        /* a default initial seed is used     */
        if (mti == NN+1) 
            init_genrand64(5489ULL); 

        for (i=0;i<NN-MM;i++) {
            x = (mt[i]&UM)|(mt[i+1]&LM);
            mt[i] = mt[i+MM] ^ (x>>1) ^ mag01[(int)(x&1ULL)];
        }
        for (;i<NN-1;i++) {
            x = (mt[i]&UM)|(mt[i+1]&LM);
            mt[i] = mt[i+(MM-NN)] ^ (x>>1) ^ mag01[(int)(x&1ULL)];
        }
        x = (mt[NN-1]&UM)|(mt[0]&LM);
        mt[NN-1] = mt[MM-1] ^ (x>>1) ^ mag01[(int)(x&1ULL)];

        mti = 0;
    }
  
    x = mt[mti++];

    x ^= (x >> 29) & 0x5555555555555555ULL;
    x ^= (x << 17) & 0x71D67FFFEDA60000ULL;
    x ^= (x << 37) & 0xFFF7EEE000000000ULL;
    x ^= (x >> 43);

    return x;
}

///////////////////////////////////////////////////////////////////////////////////

void swapLong(uint64_t *X){
	uint64_t x = *X;
	x = (x & 0x00000000FFFFFFFF) << 32 | (x & 0xFFFFFFFF00000000) >> 32;
	x = (x & 0x0000FFFF0000FFFF) << 16 | (x & 0xFFFF0000FFFF0000) >> 16;
	x = (x & 0x00FF00FF00FF00FF) << 8  | (x & 0xFF00FF00FF00FF00) >> 8;
}

int hexchr2bin(char hex, uint8_t *out)
{
    if (out == NULL)
        return 0;

    if (hex >= '0' && hex <= '9') {
        *out = hex - '0';
    } else if (hex >= 'A' && hex <= 'F') {
        *out = hex - 'A' + 10;
    } else if (hex >= 'a' && hex <= 'f') {
        *out = hex - 'a' + 10;
    } else {
        return 0;
    }

    return 1;
}

size_t hex2bin(char *hex, uint8_t **out)
{
    size_t len, i;
    uint8_t b1, b2;

    if (hex == NULL || *hex == '\0' || out == NULL)
        return 0;

    len = strlen(hex);
    if (len % 2 != 0)
        return 0;
    len /= 2;

    *out = malloc(len);
    memset(*out, 'A', len);
    for (i=0; i<len; i++) {
        if (!hexchr2bin(hex[i*2], &b1) || !hexchr2bin(hex[i*2+1], &b2)) return 0;
        (*out)[i] = (b1 << 4) | b2;
    }
    return len;
}

#if !defined(HAVE_OPENCL_CL_H) && !defined(HAVE_CL_CL_H)
void pow_omp(uint8_t *str, char *work){
	int i=0;
	uint64_t r_str=0;
	while(i==0){
		r_str=genrand64_int64();
		#pragma omp parallel
		#pragma omp for
		for(int j=0;j<WORK_SIZE;j++){
			uint64_t r_str_l=r_str+j, b2b_b=0;
			char b2b_h[17];
			blake2b_state b2b;
			
			blake2b_init(&b2b, 8);
			blake2b_update(&b2b, (uint8_t *)&r_str_l, 8);
			blake2b_update(&b2b, str, 32);
			blake2b_final(&b2b, (uint8_t *)&b2b_b, 8);

			swapLong(&b2b_b);
			sprintf(b2b_h, "%016lx", b2b_b);

			if(strcmp( b2b_h , "ffffffc000000000")>0){
				swapLong(&r_str_l);
				#pragma omp atomic write
				i=sprintf(work, "%016lx", r_str_l);
				#pragma omp cancel for
			}
			#pragma omp cancellation point for
		}
	}
}
#endif

char *pow_generate(char *hash){
	char *work=malloc(17);
	uint8_t *str;
	uint64_t mt_seed=0;

	hex2bin(hash, &str);

	int fd = open("/dev/urandom", O_RDONLY);
	read(fd, &mt_seed, 8);
	close(fd);
	init_genrand64(mt_seed);

#if defined(HAVE_OPENCL_CL_H) || defined(HAVE_CL_CL_H)
	cl_platform_id cpPlatform;
	cl_uint num;

	clGetPlatformIDs(1, &cpPlatform, &num);
	if(num>0){
		int i=0;
		char *opencl_program;
		size_t length;
		const size_t work_size = WORK_SIZE;
		uint64_t workb=0, r_str=0;
		cl_mem d_rand, d_work, d_str;
		cl_device_id device_id;
		cl_program program;

		clGetDeviceIDs(cpPlatform, CL_DEVICE_TYPE_GPU, 1, &device_id, NULL);
		cl_context context = clCreateContext(0, 1, &device_id, NULL, NULL, NULL);
		cl_command_queue queue = clCreateCommandQueueWithProperties(context, device_id, 0, NULL);

		FILE *f = fopen ("nanopow.cl", "rb");

		fseek (f, 0, SEEK_END);
		length = ftell (f);
		rewind(f);
		opencl_program = malloc(length);
		if (opencl_program) fread (opencl_program, 1, length, f);
		fclose (f);

		program = clCreateProgramWithSource(context, 1, (const char **)&opencl_program, &length, NULL);
		clBuildProgram(program, 0, NULL, NULL, NULL, NULL);

		d_rand = clCreateBuffer(context, CL_MEM_READ_WRITE|CL_MEM_COPY_HOST_PTR, 8, &r_str, NULL);
		d_work = clCreateBuffer(context, CL_MEM_READ_WRITE|CL_MEM_COPY_HOST_PTR, 8, &workb, NULL);
		d_str = clCreateBuffer(context, CL_MEM_READ_WRITE|CL_MEM_COPY_HOST_PTR, 32, str, NULL);

		cl_kernel kernel = clCreateKernel(program, "raiblocks_work", NULL);

		clSetKernelArg(kernel, 0, sizeof(d_rand), &d_rand);
		clSetKernelArg(kernel, 1, sizeof(d_work), &d_work);
		clSetKernelArg(kernel, 2, sizeof(d_str), &d_str);

		while(i==0){
			r_str=genrand64_int64();

			clEnqueueWriteBuffer(queue, d_rand, CL_FALSE, 0, 8, &r_str, 0, NULL, NULL );
			clEnqueueWriteBuffer(queue, d_str, CL_FALSE, 0, 32, str, 0, NULL, NULL );

			clEnqueueNDRangeKernel(queue, kernel, 1, NULL, &work_size, NULL, 0, NULL, NULL);

			clEnqueueReadBuffer(queue, d_work, CL_FALSE, 0, 8, &workb, 0, NULL, NULL );

			clFinish(queue);

			if(workb!=0){
				swapLong(&workb);
				i=sprintf(work, "%016lx", workb);
			}
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
	pow_omp(str, work);
#endif
	return work;
}

int main(int argc, char *argv[]){
    if(argc> 1){
		char *work;
		work=pow_generate(argv[1]);
		printf("%s\n", work);
		free(work);
	}
}
