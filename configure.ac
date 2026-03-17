AC_INIT()
AC_LANG(C)
AC_PROG_CC([gcc-8 gcc])
AC_ARG_ENABLE([gpu], AS_HELP_STRING([--enable-gpu], [Enable GPU use]))
AS_IF([test "x$enable_gpu" = "xyes"], [
AC_CHECK_HEADERS([CL/cl.h OpenCL/cl.h])
AC_CHECK_LIB(CL, clGetPlatformIDs, [], [])
AC_CHECK_LIB(OpenCL, clGetPlatformIDs, [], [])
], [
AC_CHECK_HEADERS(blake2.h, [], [AC_ERROR([blake2 headers missing.])])
AC_CHECK_LIB(b2, blake2b_init, [], [AC_ERROR([blake2 library missing.])])
AC_OPENMP()
])
CFLAGS="$CFLAGS -Wall -Wextra"
AC_OUTPUT(makefile)
