import os
import platform
import sysconfig

import setuptools

k, _, _, _, m, _ = platform.uname()
cc = os.getenv("CC", sysconfig.get_config_var("CC"))
print(k, m, cc)
BLAKE2B_DIR = "src/nanopy/blake2b"
ED25519_DIR = "src/nanopy/ed25519-donna"
ED25519_SRC = ED25519_DIR + "/ed25519.c"
ED25519_IMPL = None
ARCH_FLAG = None
if m.lower() in ["x86_64", "amd64"]:
    BLAKE2B_DIR += "/sse"
    ED25519_IMPL = "ED25519_SSE2"
    ARCH_FLAG = "/arch:AVX2" if k == "Windows" else "-march=x86-64-v3"
elif m.lower().startswith("arm64") or m.lower().startswith("aarch64"):
    BLAKE2B_DIR += "/neon"
    ARCH_FLAG = "/arch:armv8.0" if k == "Windows" else "-march=armv8-a"
else:
    BLAKE2B_DIR += "/ref"
BLAKE2B_SRC = BLAKE2B_DIR + "/blake2b.c"

e_args = {
    "define_macros": [],
    "extra_compile_args": [],
    "extra_link_args": [],
    "include_dirs": [BLAKE2B_DIR, ED25519_DIR],
    "libraries": [],
    "name": "nanopy.ext",
    "sources": ["src/nanopy/ext.c", BLAKE2B_SRC, ED25519_SRC],
    "undef_macros": [],
}

if k == "Windows":
    e_args["extra_compile_args"] += [ARCH_FLAG]
else:
    if os.environ.get("DBG"):
        e_args["extra_compile_args"] += ["-g", "-O0"]
        e_args["extra_link_args"] += ["-g", "-O0"]
        e_args["undef_macros"] += ["NDEBUG"]
    else:
        e_args["extra_compile_args"] += ["-O3", "-flto", ARCH_FLAG]
        e_args["extra_link_args"] += ["-O3", "-flto", ARCH_FLAG]

if ED25519_IMPL:
    e_args["define_macros"] += [(ED25519_IMPL, None)]

if os.environ.get("USE_OCL"):
    e_args["define_macros"] += [("USE_OCL", None)]
    if os.environ.get("CI"):
        e_args["define_macros"] += [("USE_OCL_CPU", None)]
    if k == "Darwin":
        e_args["extra_link_args"] += ["-framework", "OpenCL"]
    else:
        e_args["libraries"] += ["OpenCL"]
elif k == "Windows":
    e_args["extra_compile_args"] += ["/openmp"]
else:
    e_args["extra_compile_args"] += ["-fopenmp"]
    e_args["extra_link_args"] += ["-fopenmp"]

print(e_args)
setuptools.setup(ext_modules=[setuptools.Extension(**e_args)])
