from setuptools import setup, Extension
import sys, os


def which(pgm):
    path = os.getenv('PATH')
    for p in path.split(os.path.pathsep):
        p = os.path.join(p, pgm)
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p


os.environ["CC"] = "gcc"
if sys.platform == 'darwin':
    gcc = None
    for i in range(9, 5, -1):
        gcc = 'gcc-' + str(i)
        if which(gcc):
            os.environ["CC"] = gcc
            break

eca = []
ela = []
libs = []
macros = []

if '--enable-gpu' in sys.argv:
    sys.argv.remove('--enable-gpu')
    if sys.platform == 'darwin':
        macros = [('HAVE_OPENCL_OPENCL_H', '1')]
        ela = ['-framework', 'OpenCL']
    else:
        macros = [('HAVE_CL_CL_H', '1')]
        libs = ['OpenCL']
else:
    libs = ['b2', 'omp']
    eca = ['-fopenmp']

setup(
    name="nanopy",
    version='0.0.1',
    packages=['nanopy'],
    description='Python implementation of NANO-related functions.',
    url='https://github.com/nano128/nanopy',
    author='128',
    license='MIT',
    python_requires='>=3.6',
    install_requires=['requests'],
    ext_modules=[
        Extension(
            'nanopy.work',
            sources=['nanopy/work.c'],
            extra_compile_args=eca,
            extra_link_args=ela,
            libraries=libs,
            define_macros=macros)
    ])
