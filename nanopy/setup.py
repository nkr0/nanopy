from setuptools import setup, Extension
import sys

eca = []
ela = []
libs = []
macros = []

if '--enable-gpu' in sys.argv:
    sys.argv.remove('--enable-gpu')
    libs = ['OpenCL']
    macros = [('HAVE_CL_CL_H', '1')]
    if sys.platform == 'darwin':
        macros = [('HAVE_OPENCL_OPENCL_H', '1')]
        ela = ['-framework', 'OpenCL']
else:
    libs = ['b2']
    eca = ['-fopenmp']

setup(
    name="nanopy",
    version='0.0.1',
    description='Python implementation of NANO-related functions.',
    url='https://github.com/nano128/nanopy',
    author='128',
    scripts=['__init__.py', 'ed25519_blake2b.py', 'rpc.py'],
    license='MIT',
    python_requires='>=3.0',
    install_requires=['requests'],
    ext_modules=[
        Extension(
            'work',
            sources=['work.c'],
            extra_compile_args=eca,
            extra_link_args=ela,
            libraries=libs,
            define_macros=macros)
    ])
