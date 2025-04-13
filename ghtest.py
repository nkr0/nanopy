import hashlib, os, random
import nanopy as npy
import ed25519_blake2b

# signature

tk, pk, _ = npy.key_expand("0" * 64)
m = "test"
sig = npy.sign(tk, msg=m)
assert npy.verify_signature(m, sig, pk)
assert ed25519_blake2b.checkvalid(bytes.fromhex(sig), m.encode(), bytes.fromhex(pk))
m = "fail"
assert not npy.verify_signature(m, sig, pk)

# work computation


def work_validate(work, _hash, difficulty=None, multiplier=0):
    assert len(work) == 16
    assert len(_hash) == 64
    work = bytearray.fromhex(work)
    _hash = bytes.fromhex(_hash)
    if multiplier:
        difficulty = npy.from_multiplier(multiplier)
    else:
        difficulty = difficulty if difficulty else work_difficulty
    difficulty = bytes.fromhex(difficulty)

    work.reverse()
    b2b_h = bytearray(hashlib.blake2b(work + _hash, digest_size=8).digest())
    b2b_h.reverse()
    if b2b_h >= difficulty:
        return True
    return False


def work_generate(_hash, difficulty=None, multiplier=0):
    assert len(_hash) == 64
    _hash = bytes.fromhex(_hash)
    b2b_h = bytearray.fromhex("0" * 16)
    if multiplier:
        difficulty = npy.from_multiplier(multiplier)
    else:
        difficulty = difficulty if difficulty else work_difficulty
    difficulty = bytes.fromhex(difficulty)
    while b2b_h < difficulty:
        work = bytearray((random.getrandbits(8) for i in range(8)))
        for r in range(0, 256):
            work[7] = (work[7] + r) % 256
            b2b_h = bytearray(hashlib.blake2b(work + _hash, digest_size=8).digest())
            b2b_h.reverse()
            if b2b_h >= difficulty:
                break
    work.reverse()
    return work.hex()


assert "fffffe0000000000" == npy.from_multiplier(1 / 8)
assert "fffffff800000000" == npy.from_multiplier(8)
assert 0.125 == npy.to_multiplier("fffffe0000000000")
assert 8.0 == npy.to_multiplier("fffffff800000000")

h = os.urandom(32).hex()
w = npy.work_generate(h, multiplier=1 / 8)
print(w)
assert npy.work_validate(w, h, multiplier=1 / 8)
assert not npy.work_validate(w, "0" * 64, multiplier=1 / 8)
assert work_validate(w, h, multiplier=1 / 8)

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
