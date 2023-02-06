import os, sys, platform
from setuptools import setup, Extension


def find_gcc(*max_min, dirs):
    """
    Looks in `dirs` for gcc-{max_min}, starting with max.

    If no gcc-{version} is found, `None` is returned.

    :param max_min: tuple of max and min gcc versions
    :param dirs: list of directories to look in
    :return: gcc name or None
    """

    for version in range(*max_min, -1):
        f_name = "gcc-{0}".format(version)

        for _dir in dirs:
            full_path = os.path.join(_dir, f_name)
            if os.path.exists(full_path) and os.access(full_path, os.X_OK):
                return f_name

    return None


def config_arch():
    global BLAKE2B_SRC
    global BLAKE2B_DIR
    global ED25519_IMPL
    m = platform.machine()
    BLAKE2B_DIR = "nanopy/blake2b/"
    if m.startswith("x86") or m in ("i386", "i686", "AMD64"):
        BLAKE2B_DIR += "sse"
        ED25519_IMPL = "ED25519_SSE2"
    elif (m.startswith("arm") and sys.maxsize > 2**32) or m.startswith("aarch64"):
        BLAKE2B_DIR += "neon"
    else:
        BLAKE2B_DIR += "ref"
    BLAKE2B_SRC = [BLAKE2B_DIR + "/blake2b.c"]
    print(m, sys.maxsize > 2**32, BLAKE2B_SRC, ED25519_IMPL)


def get_work_ext_kwargs(use_gpu=False, link_omp=False, use_vc=False, platform=None):
    """
    builds extension kwargs depending on environment

    :param use_gpu: use OpenCL GPU work generation
    :param link_omp: Link with the OMP library (OSX)
    :param use_vc: use Visual C compiler (Windows)
    :param platform: OS platform

    :return: extension kwargs
    """

    e_args = {
        "name": "nanopy.work",
        "sources": ["nanopy/work.c"],
        "include_dirs": [],
        "extra_compile_args": ["-O3", "-march=native", "-g0"],
        "extra_link_args": ["-s"],
        "libraries": [],
        "define_macros": [],
    }

    if use_gpu:
        if platform == "darwin":
            e_args["define_macros"] = [("HAVE_OPENCL_OPENCL_H", "1")]
            e_args["extra_link_args"].extend("-framework", "OpenCL")
        else:
            if use_vc:
                e_args["extra_compile_args"] = []
                e_args["extra_link_args"] = []
            e_args["define_macros"] = [("HAVE_CL_CL_H", "1")]
            e_args["libraries"] = ["OpenCL"]
    else:
        e_args["sources"].extend(BLAKE2B_SRC)
        e_args["include_dirs"] = [BLAKE2B_DIR]
        e_args["extra_compile_args"].append("-fopenmp")
        e_args["extra_link_args"].append("-fopenmp")
        if platform == "darwin":
            if link_omp:
                e_args["libraries"] = ["omp"]
        else:
            if use_vc:
                e_args["define_macros"] = [("USE_VISUAL_C", "1")]
                e_args["extra_compile_args"] = [
                    "/openmp",
                    "/arch:SSE2",
                    "/arch:AVX",
                    "/arch:AVX2",
                ]
                e_args["extra_link_args"] = [
                    "/openmp",
                    "/arch:SSE2",
                    "/arch:AVX",
                    "/arch:AVX2",
                ]

    return e_args


def get_ed25519_blake2b_ext_kwargs(use_vc=False, platform=None):
    """
    builds extension kwargs depending on environment

    :param use_vc: use Visual C compiler (Windows)
    :param platform: OS platform

    :return: extension kwargs
    """

    e_args = {
        "name": "nanopy.ed25519_blake2b",
        "sources": BLAKE2B_SRC
        + [
            "nanopy/ed25519-donna/ed25519.c",
            "nanopy/ed25519_blake2b.c",
        ],
        "include_dirs": [BLAKE2B_DIR],
        "extra_compile_args": ["-O3", "-march=native", "-g0"],
        "extra_link_args": ["-s"],
        "define_macros": [
            ("ED25519_CUSTOMRNG", "1"),
            ("ED25519_CUSTOMHASH", "1"),
        ],
    }

    if ED25519_IMPL:
        e_args["define_macros"].append((ED25519_IMPL, "1"))

    if platform == "win32" and use_vc:
        e_args["extra_compile_args"] = [
            "/arch:SSE2",
            "/arch:AVX",
            "/arch:AVX2",
        ]
        e_args["extra_link_args"] = [
            "/arch:SSE2",
            "/arch:AVX",
            "/arch:AVX2",
        ]

    return e_args


if sys.platform not in ["linux", "win32", "cygwin", "darwin"]:
    raise OSError("Unsupported OS platform")

env = os.environ
try:
    env["CC"] = os.getenv("CC") or find_gcc(
        *(15, 5), dirs=os.getenv("PATH").split(os.pathsep)
    )
except:
    pass

BLAKE2B_SRC = []
BLAKE2B_DIR = ""
ED25519_IMPL = ""
config_arch()

setup(
    name="nanopy",
    version="24.0",
    packages=["nanopy"],
    url="https://github.com/npy0/nanopy",
    license="MIT",
    python_requires=">=3.6",
    ext_modules=[
        Extension(
            **get_work_ext_kwargs(
                use_gpu=True if env.get("USE_GPU") == "1" else False,
                link_omp=True if env.get("LINK_OMP") == "1" else False,
                use_vc=True if env.get("USE_VC") == "1" else False,
                platform=sys.platform,
            )
        ),
        Extension(
            **get_ed25519_blake2b_ext_kwargs(
                use_vc=True if env.get("USE_VC") == "1" else False,
                platform=sys.platform,
            )
        ),
    ],
    extras_require={"full": ["requests", "websocket-client", "pysocks", "mnemonic"]},
)
