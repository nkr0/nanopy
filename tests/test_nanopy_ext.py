# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
import csv
import unittest

from nanopy import ext  # type: ignore


class TestModuleLevel(unittest.TestCase):
    def test_work_validate(self) -> None:
        with self.assertRaisesRegex(ValueError, "Hash must be 32 bytes"):
            ext.work_validate(0, b"", 0)
        difficulty = int("fffffe0000000000", 16)
        with open("tests/work.csv", encoding="ascii") as f:
            cf = csv.reader(f)
            for e in cf:
                h = bytes.fromhex(e[0])
                work = int(e[1], 16)
                assert ext.work_validate(work, h, difficulty)

    def test_work_generate(self) -> None:
        with self.assertRaisesRegex(ValueError, "Hash must be 32 bytes"):
            ext.work_generate(b"", 0)
        ext.work_generate(b"0" * 32, 0)

    def test_publickey(self) -> None:
        with self.assertRaisesRegex(ValueError, "Secret key must be 32 bytes"):
            ext.publickey(b"")
        with open("tests/ed25519.csv", encoding="ascii") as f:
            cf = csv.reader(f)
            for e in cf:
                sk = bytes.fromhex(e[0])
                pk = bytes.fromhex(e[1])
                assert pk == ext.publickey(sk)

    def test_sign(self) -> None:
        with self.assertRaisesRegex(ValueError, "Secret key must be 32 bytes"):
            ext.sign(b"", b"", b"")
        with self.assertRaisesRegex(ValueError, "Random must be 32 bytes"):
            ext.sign(b"0" * 32, b"", b"")
        with open("tests/ed25519.csv", encoding="ascii") as f:
            cf = csv.reader(f)
            for e in cf:
                sk = bytes.fromhex(e[0])
                m = bytes.fromhex(e[2])
                r = bytes.fromhex(e[3])
                sig = bytes.fromhex(e[4])
                assert sig == ext.sign(sk, m, r)

    def test_verify_signature(self) -> None:
        with self.assertRaisesRegex(ValueError, "Signature must be 64 bytes"):
            ext.verify_signature(b"", b"", b"")
        with self.assertRaisesRegex(ValueError, "Public key must be 32 bytes"):
            ext.verify_signature(b"0" * 64, b"", b"")
        with open("tests/ed25519.csv", encoding="ascii") as f:
            cf = csv.reader(f)
            for e in cf:
                pk = bytes.fromhex(e[1])
                m = bytes.fromhex(e[2])
                sig = bytes.fromhex(e[4])
                assert ext.verify_signature(sig, pk, m)
