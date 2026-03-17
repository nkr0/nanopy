# -*- coding: utf-8 -*-

import sys
import os
from setuptools import setup, Extension

eca = ela = libs = macros = None

GCC_MIN_MAX = (5, 9)  # Look for gcc versions between 5 and 9
POW_GPU = os.environ.pop('USE_GPU', False)  # Enable GPU work generation using OpenCL
LINK_OMP = os.environ.pop('LINK_OMP', False)  # Link with the OMP library (OSX)


def get_gcc():
    path = os.getenv('PATH').split(os.path.pathsep)

    for version in range(*GCC_MIN_MAX).__reversed__():
        f_name = 'gcc-{0}'.format(version)

        for _dir in path:
            full_path = os.path.join(_dir, f_name)
            if os.path.exists(full_path) and os.access(full_path, os.X_OK):
                return f_name

    raise FileNotFoundError('Requires gcc version between {0[0]} and {0[1]}'.format(GCC_MIN_MAX))


if sys.platform == 'darwin':
    if POW_GPU:
        macros = [('HAVE_OPENCL_OPENCL_H', '1')]
        ela = ['-framework', 'OpenCL']
    else:
        libs = ['b2', 'omp'] if LINK_OMP else ['b2']
        eca = ['-fopenmp']
elif sys.platform == 'linux':
    if POW_GPU:
        macros = [('HAVE_CL_CL_H', '1')]
        libs = ['OpenCL']
    else:
        libs = ['b2']
        eca = ['-fopenmp']
else:
    raise OSError('Unsupported OS platform')

# Use the most recent version of gcc
os.environ['CC'] = get_gcc()

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
