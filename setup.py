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
    packages=['nanopy'],
    description='Python implementation of NANO-related functions.',
    url='https://github.com/nano128/nanopy',
    author='128',
    author_email="42086377+nano128@users.noreply.github.com",
    license='MIT',
    python_requires='>=3.0',
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
