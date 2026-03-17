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
    libs = ['OpenCL']
    try:
        macros = [('HAVE_CL_CL_H', '1')]
        try_build()
    except:
        macros = [('HAVE_OPENCL_CL_H', '1')]
        try_build()
    print("Success!!! Built with GPU work computation.")
except:
    try:
        libs = ['CL']
        try:
            macros = [('HAVE_CL_CL_H', '1')]
            try_build()
        except:
            macros = [('HAVE_OPENCL_CL_H', '1')]
            try_build()
        print("Success!!! Built with GPU work computation.")
    except:
        try:
            libs = ['b2']
            eca = ['-fopenmp']
            macros = []
            try_build()
            print("Success!!! Built with OpenMP work computation.")
        except:
            print("Build failed.")
