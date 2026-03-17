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


def get_work_ext_kwargs(use_gpu=False,
                        link_omp=False,
                        use_vc=False,
                        platform=None):
    """
    builds extension kwargs depending on environment

    :param use_gpu: use OpenCL GPU work generation
    :param link_omp: Link with the OMP library (OSX)
    :param use_vc: use Visual C compiler (Windows)
    :param platform: OS platform

    :return: extension kwargs
    """

    e_args = {
        'name': 'nanopy.work',
        'sources': ['nanopy/blake2b/blake2b.c', 'nanopy/work.c'],
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
            if link_omp:
                e_args['libraries'] = ['omp']
            e_args['extra_compile_args'] = ['-fopenmp']
            e_args['extra_link_args'] = ['-fopenmp']
    elif platform in ['linux', 'win32', 'cygwin']:
        if use_gpu:
            e_args['define_macros'] = [('HAVE_CL_CL_H', '1')]
            e_args['libraries'] = ['OpenCL']
        else:
            if use_vc:
                e_args['define_macros'] = [('USE_VISUAL_C', '1')]
                e_args['extra_compile_args'] = [
                    '/openmp', '/arch:SSE2', '/arch:AVX', '/arch:AVX2'
                ]
                e_args['extra_link_args'] = [
                    '/openmp', '/arch:SSE2', '/arch:AVX', '/arch:AVX2'
                ]
            else:
                e_args['extra_compile_args'] = ['-fopenmp']
                e_args['extra_link_args'] = ['-fopenmp']
    else:
        raise OSError('Unsupported OS platform')

    return e_args


def get_ed25519_blake2b_ext_kwargs(use_vc=False, platform=None):
    """
    builds extension kwargs depending on environment

    :param use_vc: use Visual C compiler (Windows)
    :param platform: OS platform

    :return: extension kwargs
    """

    e_args = {
        'name': 'nanopy.ed25519_blake2b',
        'sources': [
            'nanopy/blake2b/blake2b.c', 'nanopy/ed25519-donna/ed25519.c',
            'nanopy/ed25519_blake2b.c'
        ],
        'extra_compile_args': [],
        'extra_link_args': [],
        'define_macros': [],
    }

    if platform == 'win32' and use_vc:
        e_args['extra_compile_args'] = [
            '/ED25519_SSE2', '/ED25519_CUSTOMRNG', '/ED25519_CUSTOMHASH',
            '/arch:SSE2', '/arch:AVX', '/arch:AVX2'
        ]
        e_args['extra_link_args'] = [
            '/ED25519_SSE2', '/ED25519_CUSTOMRNG', '/ED25519_CUSTOMHASH',
            '/arch:SSE2', '/arch:AVX', '/arch:AVX2'
        ]
    else:
        e_args['define_macros'] = [('ED25519_SSE2', '1'),
                                   ('ED25519_CUSTOMRNG', '1'),
                                   ('ED25519_CUSTOMHASH', '1')]

    return e_args


env = os.environ
try:
    env['CC'] = os.getenv('CC') or find_gcc(
        *(5, 9), dirs=os.getenv('PATH').split(os.pathsep))
except:
    pass

setup(name="nanopy",
      version='20.0.0',
      packages=['nanopy'],
      url='https://github.com/npy0/nanopy',
      license='MIT',
      python_requires='>=3.6',
      ext_modules=[
          Extension(**get_work_ext_kwargs(
              use_gpu=True if env.get('USE_GPU') == '1' else False,
              link_omp=True if env.get('LINK_OMP') == '1' else False,
              use_vc=True if env.get('USE_VC') == '1' else False,
              platform=sys.platform)),
          Extension(**get_ed25519_blake2b_ext_kwargs(
              use_vc=True if env.get('USE_VC') == '1' else False,
              platform=sys.platform))
      ])
