import csv
from nanopy import ext  # type: ignore
import pytest


def test_work_validate() -> None:
    with pytest.raises(ValueError, match="Hash must be 32 bytes"):
        ext.work_validate(0, b"", 0)
    difficulty = int("fffffe0000000000", 16)
    with open("tests/work.csv") as f:
        cf = csv.reader(f)
        for e in cf:
            h = bytes.fromhex(e[0])
            work = int(e[1], 16)
            assert ext.work_validate(work, h, difficulty)


def test_work_generate() -> None:
    with pytest.raises(ValueError, match="Hash must be 32 bytes"):
        ext.work_generate(b"", 0)
    ext.work_generate(b"0" * 32, 0)


def test_publickey() -> None:
    with pytest.raises(ValueError, match="Secret key must be 32 bytes"):
        ext.publickey(b"")
    with open("tests/ed25519.csv") as f:
        cf = csv.reader(f)
        for e in cf:
            sk = bytes.fromhex(e[0])
            pk = bytes.fromhex(e[1])
            assert pk == ext.publickey(sk)


def test_sign() -> None:
    with pytest.raises(ValueError, match="Secret key must be 32 bytes"):
        ext.sign(b"", b"", b"")
    with pytest.raises(ValueError, match="Random must be 32 bytes"):
        ext.sign(b"0" * 32, b"", b"")
    with open("tests/ed25519.csv") as f:
        cf = csv.reader(f)
        for e in cf:
            sk = bytes.fromhex(e[0])
            m = bytes.fromhex(e[2])
            r = bytes.fromhex(e[3])
            sig = bytes.fromhex(e[4])
            assert sig == ext.sign(sk, m, r)


def test_verify_signature() -> None:
    with pytest.raises(ValueError, match="Signature must be 64 bytes"):
        ext.verify_signature(b"", b"", b"")
    with pytest.raises(ValueError, match="Public key must be 32 bytes"):
        ext.verify_signature(b"0" * 64, b"", b"")
    with open("tests/ed25519.csv") as f:
        cf = csv.reader(f)
        for e in cf:
            pk = bytes.fromhex(e[1])
            m = bytes.fromhex(e[2])
            sig = bytes.fromhex(e[4])
            assert ext.verify_signature(sig, pk, m)
