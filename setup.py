import os, shutil, sys, platform
from setuptools import setup, Extension


def find_gcc(*max_min):
    """
    Looks in PATH for gcc or gcc-{max_min}, starting with max.

    If no gcc or gcc-{version} is found, `None` is returned.

    :param max_min: tuple of max and min gcc versions
    :return: gcc name or None
    """

    if shutil.which("gcc"):
        return "gcc"
    for version in range(*max_min, -1):
        f_name = "gcc-{0}".format(version)
        if shutil.which(f_name):
            return f_name
    return None


def config_arch():
    global BLAKE2B_DIR
    global BLAKE2B_SRC
    global ED25519_DIR
    global ED25519_SRC
    global ED25519_IMPL
    m = platform.machine()
    BLAKE2B_DIR = "nanopy/blake2b/"
    ED25519_DIR = "nanopy/ed25519-donna"
    ED25519_SRC = ED25519_DIR + "/ed25519.c"
    ED25519_IMPL = None
    if m.startswith("x86") or m in ("i386", "i686", "AMD64"):
        BLAKE2B_DIR += "sse"
        ED25519_IMPL = "ED25519_SSE2"
    elif (m.startswith("arm") and sys.maxsize > 2**32) or m.startswith("aarch64"):
        BLAKE2B_DIR += "neon"
    else:
        BLAKE2B_DIR += "ref"
    BLAKE2B_SRC = BLAKE2B_DIR + "/blake2b.c"
    print(m, sys.maxsize > 2**32, BLAKE2B_SRC, ED25519_IMPL)


def get_work_ext_kwargs(use_gpu):
    """
    builds extension kwargs depending on environment

    :param use_gpu: use OpenCL GPU work generation

    :return: extension kwargs
    """

    e_args = {
        "name": "nanopy.work",
        "sources": ["nanopy/work.c", BLAKE2B_SRC],
        "include_dirs": [BLAKE2B_DIR],
        "extra_compile_args": ["-O3", "-march=native"],
        "extra_link_args": ["-s"],
        "libraries": [],
        "define_macros": [],
    }

    if use_gpu:
        if sys.platform == "darwin":
            e_args["define_macros"] = [("HAVE_OPENCL_OPENCL_H", "1")]
            e_args["extra_link_args"].extend("-framework", "OpenCL")
        else:
            if sys.platform == "win32":
                e_args["extra_compile_args"] = []
                e_args["extra_link_args"] = []
            e_args["define_macros"] = [("HAVE_CL_CL_H", "1")]
            e_args["libraries"] = ["OpenCL"]
    else:
        e_args["extra_compile_args"].append("-fopenmp")
        e_args["extra_link_args"].append("-fopenmp")
        if sys.platform == "win32":
            e_args["extra_compile_args"] = [
                "/openmp:llvm",
                "/arch:SSE2",
                "/arch:AVX",
                "/arch:AVX2",
            ]
            e_args["extra_link_args"] = []

    return e_args


def get_ed25519_blake2b_ext_kwargs():
    """
    builds extension kwargs depending on environment

    :return: extension kwargs
    """

    e_args = {
        "name": "nanopy.ed25519_blake2b",
        "sources": ["nanopy/ed25519_blake2b.c", BLAKE2B_SRC, ED25519_SRC],
        "include_dirs": [BLAKE2B_DIR, ED25519_DIR],
        "extra_compile_args": ["-O3", "-march=native"],
        "extra_link_args": ["-s"],
        "define_macros": [],
    }

    if ED25519_IMPL:
        e_args["define_macros"].append((ED25519_IMPL, "1"))

    if sys.platform == "win32":
        e_args["extra_compile_args"] = [
            "/arch:SSE2",
            "/arch:AVX",
            "/arch:AVX2",
        ]
        e_args["extra_link_args"] = []

    return e_args


if sys.platform not in ["linux", "win32", "cygwin", "darwin"]:
    raise OSError("Unsupported OS platform")

env = os.environ
try:
    env["CC"] = os.getenv("CC") or find_gcc(*(19, 5))
except:
    pass

config_arch()

setup(
    ext_modules=[
        Extension(
            **get_work_ext_kwargs(env.get("USE_GPU") == "1")
        ),
        Extension(**get_ed25519_blake2b_ext_kwargs()),
    ],
)
