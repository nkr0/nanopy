import os
import platform
import setuptools

k, _, _, _, m, _ = platform.uname()
print(m, k)
BLAKE2B_DIR = "nanopy/blake2b/"
ED25519_DIR = "nanopy/ed25519-donna"
ED25519_SRC = ED25519_DIR + "/ed25519.c"
ED25519_IMPL = None
if m in ("i686", "x86_64", "AMD64"):
    BLAKE2B_DIR += "sse"
    ED25519_IMPL = "ED25519_SSE2"
elif m.startswith("arm64") or m.startswith("aarch64"):
    BLAKE2B_DIR += "neon"
else:
    BLAKE2B_DIR += "ref"
BLAKE2B_SRC = BLAKE2B_DIR + "/blake2b.c"

e_args = {
    "name": "nanopy.ed25519_blake2b",
    "sources": ["nanopy/ed25519_blake2b.c", BLAKE2B_SRC, ED25519_SRC],
    "include_dirs": [BLAKE2B_DIR, ED25519_DIR],
}

w_args = {
    "name": "nanopy.work",
    "sources": ["nanopy/work.c", BLAKE2B_SRC],
    "include_dirs": [BLAKE2B_DIR],
    "extra_compile_args": [],
    "extra_link_args": [],
}

if k == "Linux":
    e_args["extra_compile_args"] = ["-O3", "-march=native"]
    e_args["extra_link_args"] = ["-s"]
    w_args["extra_compile_args"] = ["-O3", "-march=native"]
    w_args["extra_link_args"] = ["-s"]
elif k == "Windows":
    e_args["extra_compile_args"] = ["/arch:SSE2", "/arch:AVX", "/arch:AVX2"]
    w_args["extra_compile_args"] = ["/arch:SSE2", "/arch:AVX", "/arch:AVX2"]

if ED25519_IMPL:
    e_args["define_macros"] = [(ED25519_IMPL, "1")]

if os.environ.get("USE_GPU") == "1":
    if k == "Darwin":
        w_args["define_macros"] = [("HAVE_OPENCL_OPENCL_H", "1")]
        w_args["extra_link_args"].append("-framework", "OpenCL")
    else:
        w_args["define_macros"] = [("HAVE_CL_CL_H", "1")]
        w_args["libraries"] = ["OpenCL"]
elif k == "Windows":
    w_args["extra_compile_args"].append("/openmp:llvm")
else:
    w_args["extra_compile_args"].append("-fopenmp")
    w_args["extra_link_args"].append("-fopenmp")

setuptools.setup(
    ext_modules=[setuptools.Extension(**e_args), setuptools.Extension(**w_args)]
)
