from setuptools import setup, Extension


def try_build():
    setup(
        name="nanopy",
        scripts=['__init__.py', 'ed25519_blake2b.py', 'rpc.py'],
        ext_modules=[
            Extension(
                'work',
                sources=['work.c'],
                extra_compile_args=eca,
                libraries=libs,
                define_macros=macros)
        ])


eca = []
try:
    print('\033[92m' + "Trying to build in GPU mode." + '\033[0m')
    libs = ['OpenCL']
    try:
        macros = [('HAVE_CL_CL_H', '1')]
        try_build()
    except:
        macros = [('HAVE_OPENCL_OPENCL_H', '1')]
        try_build()
    print('\033[92m' + "Success!!! Built with GPU work computation." +
          '\033[0m')
except:
    print('\033[91m' + "Failed to build in GPU mode." + '\033[0m')
    print('\033[92m' + "Trying to build in CPU mode." + '\033[0m')
    try:
        libs = ['b2']
        eca = ['-fopenmp']
        macros = []
        try_build()
        print('\033[92m' + "Success!!! Built with CPU work computation." +
              '\033[0m')
    except:
        print('\033[91m' + "Build failed." + '\033[0m')
