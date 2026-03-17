import os
import nanopy as npy

h = os.urandom(32).hex()
w = npy.work_generate(h, multiplier=1 / 8)
print(w)
print(npy.work_validate(w, h))
assert npy.work_validate(w, h, multiplier=1 / 8)
