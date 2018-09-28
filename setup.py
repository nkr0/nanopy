# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup, Extension


def find_gcc(*min_max, dirs):
    """
    Looks in `dirs` for gcc-{min_max}, starting with max.

    If no gcc-{version} is found, `None` is returned.

    :param min_max: tuple of min and max gcc versions
    :param dirs: list of directories to look in
    :return: gcc name or None
    """

    for version in range(*min_max).__reversed__():
        f_name = 'gcc-{0}'.format(version)

        for _dir in dirs:
            full_path = os.path.join(_dir, f_name)
            if os.path.exists(full_path) and os.access(full_path, os.X_OK):
                return f_name

    return None


def get_ext_kwargs(use_gpu=False, link_omp=False, platform=None):
    """
    builds extension kwargs depending on environment

    :param use_gpu: use OpenCL GPU work generation
    :param link_omp: Link with the OMP library (OSX)
    :param platform: OS platform

    :return: extension kwargs
    """

    e_args = {
        'name': 'nanopy.work',
        'sources': ['nanopy/work.c'],
        'extra_compile_args': [],
        'extra_link_args': [],
        'libraries': [],
        'define_macros': [],
    }

    if platform == 'darwin':
        if use_gpu:
            e_args['define_macros'] = [('HAVE_OPENCL_OPENCL_H', '1')]
            e_args['extra_link_args'] = ['-framework', 'OpenCL']
        else:
            e_args['libraries'] = ['b2', 'omp'] if link_omp else ['b2']
            e_args['extra_compile_args'] = ['-fopenmp']
    elif platform == 'linux':
        if use_gpu:
            e_args['define_macros'] = [('HAVE_CL_CL_H', '1')]
            e_args['libraries'] = ['OpenCL']
        else:
            e_args['extra_compile_args'] = ['-fopenmp']
            e_args['libraries'] = ['b2']
    else:
        raise OSError('Unsupported OS platform')

    return e_args


env = os.environ
env['CC'] = env.get('CC', None) or find_gcc(
    *(5, 9),
    dirs=env.get('PATH').split(os.path.pathsep)
)

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
            **get_ext_kwargs(
                use_gpu=True if env.get('USE_GPU') == '1' else False,
                link_omp=True if env.get('LINK_OMP') == '1' else False,
                platform=sys.platform
            )
        )
    ]
)
