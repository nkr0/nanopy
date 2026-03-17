# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup, Extension


def _find_gcc(*min_max, dirs):
    """
    Looks in `dirs` for gcc-{GCC_MIN_MAX}, starting with MAX.

    If no gcc-{VERSION} is found, `None` is returned.

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


def ext_args(**kwargs):
    """
    decides compiler based on passed kwargs and builds compiler args

    :param:gcc: user-supplied gcc compiler
    :param:use_gpu: use OpenCL GPU work generation (default False)
    :param:link_omp: Link with the OMP library (OSX) (default False)
    :param:platform: OS platform
    :param:gcc_min_max: look for gcc between these versions

    :return: (compiler, compiler_args)
    """

    e_args = {
        'name': 'nanopy.work',
        'sources': ['nanopy/work.c'],
        'extra_compile_args': [],
        'extra_link_args': [],
        'libraries': [],
        'define_macros': [],
    }

    platform = kwargs.get('platform')
    use_gpu = kwargs.get('use_gpu')

    if platform == 'darwin':
        if use_gpu:
            e_args['define_macros'] = [('HAVE_OPENCL_OPENCL_H', '1')]
            e_args['extra_link_args'] = ['-framework', 'OpenCL']
        else:
            e_args['libraries'] = ['b2', 'omp'] if kwargs.get('link_omp') else ['b2']
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

    # return user provided gcc or greatest version found
    return kwargs.get('gcc') or _find_gcc(*kwargs.get('gcc_min_max'), dirs=kwargs.get('path')), e_args


env = os.environ
env['CC'], ext_kwargs = ext_args(
    gcc=env.get('CC', None),
    use_gpu=True if env.get('USE_GPU') == '1' else False,
    link_omp=True if env.get('LINK_OMP') == '1' else False,
    path=os.getenv('PATH').split(os.path.pathsep),
    gcc_min_max=(5, 9),
    platform=sys.platform
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
    ext_modules=[Extension(**ext_kwargs)]
)
