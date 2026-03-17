import csv
from nanopy import ext  # type: ignore


def test_work_validate() -> None:
    difficulty = int("fffffe0000000000", 16)
    with open("tests/work.csv") as f:
        cf = csv.reader(f)
        for e in cf:
            h = bytes.fromhex(e[0])
            work = int(e[1], 16)
            assert ext.work_validate(work, h, difficulty)


def test_publickey() -> None:
    with open("tests/ed25519.csv") as f:
        cf = csv.reader(f)
        for e in cf:
            sk = bytes.fromhex(e[0])
            pk = bytes.fromhex(e[1])
            assert pk == ext.publickey(sk)


def test_sign() -> None:
    with open("tests/ed25519.csv") as f:
        cf = csv.reader(f)
        for e in cf:
            sk = bytes.fromhex(e[0])
            h = bytes.fromhex(e[2])
            r = bytes.fromhex(e[3])
            sig = bytes.fromhex(e[4])
            assert sig == ext.sign(sk, h, r)


def test_verify_signature() -> None:
    with open("tests/ed25519.csv") as f:
        cf = csv.reader(f)
        for e in cf:
            pk = bytes.fromhex(e[1])
            h = bytes.fromhex(e[2])
            sig = bytes.fromhex(e[4])
            assert ext.verify_signature(sig, pk, h)
