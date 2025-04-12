import os
import nanopy as npy
import ed25519_blake2b

# signature

tk, pk, _ = npy.key_expand(
    "0000000000000000000000000000000000000000000000000000000000000000"
)
m = "test"
sig = npy.sign(tk, msg=m)
assert npy.verify_signature(m, sig, pk)
assert ed25519_blake2b.checkvalid(bytes.fromhex(sig), m.encode(), bytes.fromhex(pk))
m = "fail"
assert not npy.verify_signature(m, sig, pk)

# work computation

assert "fffffe0000000000" == npy.from_multiplier(1 / 8)
assert "fffffff800000000" == npy.from_multiplier(8)
assert 0.125 == npy.to_multiplier("fffffe0000000000")
assert 8.0 == npy.to_multiplier("fffffff800000000")

h = os.urandom(32).hex()
w = npy.work_generate(h, multiplier=1 / 8)
print(w)
print(npy.work_validate(w, h))
assert npy.work_validate(w, h, multiplier=1 / 8)

assert "0.000000000000000000000123456789" == npy.raw_to_nano("123456789")
assert "123456789" == npy.nano_to_raw("0.000000000000000000000123456789")

# https://docs.nano.org/integration-guides/key-management/

assert npy.mnemonic_key(
    "edge defense waste choose enrich upon flee junk siren film clown finish luggage leader kid quick brick print evidence swap drill paddle truly occur",
    index=0,
    passphrase="some password",
    language="english",
) == (
    "3be4fc2ef3f3b7374e6fc4fb6e7bb153f8a2998b3b3dab50853eabe128024143",
    "5b65b0e8173ee0802c2c3e6c9080d1a16b06de1176c938a924f58670904e82c4",
    "nano_1pu7p5n3ghq1i1p4rhmek41f5add1uh34xpb94nkbxe8g4a6x1p69emk8y1d",
)

assert npy.key_expand(
    "781186FB9EF17DB6E3D1056550D9FAE5D5BBADA6A6BC370E4CBB938B1DC71DA3"
) == (
    "781186FB9EF17DB6E3D1056550D9FAE5D5BBADA6A6BC370E4CBB938B1DC71DA3",
    "3068bb1ca04525bb0e416c485fe6a67fd52540227d267cc8b6e8da958a7fa039",
    "nano_1e5aqegc1jb7qe964u4adzmcezyo6o146zb8hm6dft8tkp79za3sxwjym5rx",
)
