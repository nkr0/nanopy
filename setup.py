import os
import platform
import setuptools
import sysconfig

k, _, _, _, m, _ = platform.uname()
cc = os.getenv("CC", sysconfig.get_config_var("CC"))
print(k, m, cc)
BLAKE2B_DIR = "src/nanopy/blake2b"
ED25519_DIR = "src/nanopy/ed25519-donna"
ED25519_SRC = ED25519_DIR + "/ed25519.c"
ED25519_IMPL = None
if m.lower() in ["x86_64", "amd64"]:
    BLAKE2B_DIR += "/sse"
    ED25519_IMPL = "ED25519_SSE2"
elif m.lower().startswith("arm64") or m.lower().startswith("aarch64"):
    BLAKE2B_DIR += "/neon"
else:
    BLAKE2B_DIR += "/ref"
BLAKE2B_SRC = BLAKE2B_DIR + "/blake2b.c"

e_args = {
    "name": "nanopy.ext",
    "sources": ["src/nanopy/ext.c", BLAKE2B_SRC, ED25519_SRC],
    "include_dirs": [BLAKE2B_DIR, ED25519_DIR],
    "define_macros": [],
    "extra_compile_args": [],
    "extra_link_args": [],
    "libraries": [],
}

if k == "Windows":
    e_args["extra_compile_args"] += ["/arch:SSE2", "/arch:AVX", "/arch:AVX2"]
else:
    e_args["extra_compile_args"] += ["-O3", "-flto", "-march=native"]
    e_args["extra_link_args"] += ["-O3", "-flto", "-march=native", "-s"]

if ED25519_IMPL:
    e_args["define_macros"] += [(ED25519_IMPL, None)]

if os.environ.get("USE_GPU"):
    if k == "Darwin":
        e_args["define_macros"] += [("HAVE_OPENCL_OPENCL_H", None)]
        e_args["extra_link_args"] += ["-framework", "OpenCL"]
    else:
        e_args["define_macros"] += [("HAVE_CL_CL_H", None)]
        e_args["libraries"] += ["OpenCL"]
elif k == "Windows":
    e_args["extra_compile_args"] += ["/openmp"]
else:
    e_args["extra_compile_args"] += ["-fopenmp"]
    e_args["extra_link_args"] += ["-fopenmp"]

print(e_args)
setuptools.setup(ext_modules=[setuptools.Extension(**e_args)])
