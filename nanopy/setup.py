from setuptools import setup, Extension

setup(
    name="nanopy",
    scripts=['__init__.py', 'ed25519_blake2b.py', 'rpc.py'],
    ext_modules=[
        Extension(
            'work',
            sources=['work.c'],
            extra_compile_args=['-fopenmp'],
            libraries=['b2'])
    ])
