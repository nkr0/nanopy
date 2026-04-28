import os
import platform
import sysconfig

import setuptools

k, _, _, _, m, _ = platform.uname()
print(k, m)
BLAKE2B_DIR = "src/nanopy/blake2b"
ED25519_DIR = "src/nanopy/ed25519-donna"
ED25519_SRC = ED25519_DIR + "/ed25519.c"
ED25519_IMPL = []
ARCH_FLAG = []
if m.lower() in ["x86_64", "amd64"]:
    BLAKE2B_DIR += "/sse"
    ED25519_IMPL = [("ED25519_SSE2", None)]
    ARCH_FLAG = ["/arch:AVX2" if k == "Windows" else "-march=x86-64-v3"]
elif m.lower().startswith("arm64") or m.lower().startswith("aarch64"):
    BLAKE2B_DIR += "/neon"
    ARCH_FLAG = ["/arch:armv8.0" if k == "Windows" else "-march=armv8-a"]
else:
    BLAKE2B_DIR += "/ref"
BLAKE2B_SRC = BLAKE2B_DIR + "/blake2b.c"

e = setuptools.Extension("nanopy.ext", ["src/nanopy/ext.c", BLAKE2B_SRC, ED25519_SRC])
e.define_macros += ED25519_IMPL
e.extra_compile_args += ARCH_FLAG
e.include_dirs += [BLAKE2B_DIR, ED25519_DIR]

o = {}
if not sysconfig.get_config_var("Py_GIL_DISABLED"):
    e.py_limited_api = True
    e.define_macros += [("Py_LIMITED_API", "0x030A0000")]
    o = {"bdist_wheel": {"py_limited_api": "cp310"}}

if os.environ.get("USE_OCL"):
    e.define_macros += [("USE_OCL", None)]
    if os.environ.get("CI"):
        e.define_macros += [("USE_OCL_CPU", None)]
    if k == "Darwin":
        e.extra_link_args += ["-framework", "OpenCL"]
    else:
        e.libraries += ["OpenCL"]

if os.environ.get("DBG"):
    e.undef_macros += ["NDEBUG"]

print(vars(e))
setuptools.setup(ext_modules=[e], options=o)
