import nanopy as npy
from nanopy.rpc import RPC
import nanopy.work

#print(npy.work_generate(_hash, multiplier=1/8))
assert ('fffffe0000000000' == npy.from_multiplier(1 / 8))
assert ('fffffff800000000' == npy.from_multiplier(8))
assert (0.125 == npy.to_multiplier('fffffe0000000000'))
assert (8.0 == npy.to_multiplier('fffffff800000000'))

