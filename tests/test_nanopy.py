import hashlib
import json
import os
import re
import pytest
import nanopy as npy

PACC0 = "nano_1111111111111111111111111111111111111111111111111111hifc8npp"
PACC1 = "nano_16aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46ajbtsyew7c"
SACC0 = "nano_18gmu6engqhgtjnppqam181o5nfhj4sdtgyhy36dan3jr9spt84rzwmktafc"
Z64 = "0" * 64
R64 = os.urandom(32).hex()


def work_validate(b: npy.StateBlock, difficulty: str) -> bool:
    w = bytearray.fromhex(b.work)
    h = bytes.fromhex(b.prev)
    w.reverse()
    b2b_h = bytearray(hashlib.blake2b(w + h, digest_size=8).digest())
    b2b_h.reverse()
    if b2b_h >= bytes.fromhex(difficulty):
        return True
    return False


def test_deterministic_key() -> None:
    assert (
        npy.deterministic_key(Z64, 0)
        == "9f0e444c69f77a49bd0be89db92c38fe713e0963165cca12faf5712d7657120f"
    )


def test_generate_mnemonic() -> None:
    assert len(npy.generate_mnemonic(strength=256, language="english").split()) == 24


def test_mnemonic_key() -> None:
    assert (
        npy.mnemonic_key(
            "edge defense waste choose enrich upon flee junk siren film clown finish luggage leader kid quick brick print evidence swap drill paddle truly occur",
            i=0,
            passphrase="some password",
            language="english",
        )
        == "3be4fc2ef3f3b7374e6fc4fb6e7bb153f8a2998b3b3dab50853eabe128024143"
    )


class TestAccount:
    def test_init(self) -> None:
        acc = npy.Account(addr=PACC0)
        assert str(acc) == PACC0
        assert acc.addr == PACC0
        assert acc.pk == Z64
        assert not acc.sk

    def test_addr(self) -> None:
        acc = npy.Account()
        acc.addr = PACC0
        assert str(acc) == PACC0
        assert acc.addr == PACC0
        assert acc.pk == Z64
        assert not acc.sk

    def test_pk(self) -> None:
        acc = npy.Account()
        acc.pk = Z64
        assert str(acc) == PACC0
        assert acc.addr == PACC0
        assert acc.pk == Z64
        assert not acc.sk

    def test_sk(self) -> None:
        acc = npy.Account()
        acc.sk = Z64
        assert str(acc) == SACC0
        assert acc.addr == SACC0
        assert (
            acc.pk == "19d3d919475deed4696b5d13018151d1af88b2bd3bcff048b45031c1f36d1858"
        )
        assert acc.sk == Z64

    def test_bal(self) -> None:
        acc = npy.Account(addr=PACC0)
        assert acc.bal == "0.000000000000000000000000000000"
        acc.bal = "1"
        assert acc.bal == "1.000000000000000000000000000000"
        acc.bal = "0.000000000000000000000000000001"
        assert acc.bal == "0.000000000000000000000000000001"

    def test_raw_bal(self) -> None:
        acc = npy.Account(addr=PACC0)
        with pytest.raises(ValueError, match="Balance cannot be < 0"):
            acc.raw_bal = -1
        with pytest.raises(ValueError, match=re.escape("Balance cannot be >= 2^128")):
            acc.raw_bal = 1 << 128
        acc.raw_bal = 1
        assert acc.raw_bal == 1

    def test_frontier(self) -> None:
        acc = npy.Account(addr=PACC0)
        with pytest.raises(ValueError):
            acc.frontier = "x" * 64
        with pytest.raises(AssertionError):
            acc.frontier = "ff"
        acc.frontier = "f" * 64
        assert acc.frontier == "f" * 64

    def test_rep(self) -> None:
        acc = npy.Account(addr=PACC0)
        with pytest.raises(ValueError, match="Representative is not initialised"):
            acc.rep = npy.Account()
        rep = npy.Account(addr=PACC1)
        acc.rep = rep
        assert acc.rep == rep

    def test_state(self) -> None:
        acc = npy.Account(addr=PACC0)
        rep = npy.Account(addr=PACC1)
        acc.state = (R64, 1, rep)
        assert acc.state == (R64, 1, rep)

    def test_change_rep(self) -> None:
        acc = npy.Account(addr=PACC0)
        with pytest.raises(NotImplementedError, match="This method needs private key"):
            acc.change_rep(acc)
        TESTNET = npy.Network()
        TESTNET.send_difficulty = "fffffe0000000000"
        acc = npy.Account(TESTNET)
        acc.sk = Z64
        acc.change_rep(acc)
        b = acc.change_rep(acc, work="f" * 16)
        assert b.verify_signature()
        assert acc.frontier == b.digest

    def test_receive(self) -> None:
        acc = npy.Account()
        with pytest.raises(NotImplementedError, match="This method needs private key"):
            acc.change_rep(acc)
        acc.sk = Z64
        with pytest.raises(ValueError, match="Amount must be a positive integer"):
            acc.receive(Z64, -1)
        with pytest.raises(
            ValueError,
            match=re.escape("raw balance after receive cannot be >= 2^128"),
        ):
            acc.receive(Z64, 1 << 128)
        acc.receive(Z64, 1, work="f" * 16)
        rep = npy.Account(addr=PACC0)
        b = acc.receive(Z64, 1, rep)
        assert b.verify_signature()
        assert acc.frontier == b.digest
        assert acc.raw_bal == b.bal
        assert acc.raw_bal == 2
        assert acc.rep == rep

    def test_send(self) -> None:
        acc = npy.Account(addr=PACC0)
        with pytest.raises(NotImplementedError, match="This method needs private key"):
            acc.change_rep(acc)
        TESTNET = npy.Network()
        TESTNET.send_difficulty = "fffffe0000000000"
        acc = npy.Account(TESTNET)
        acc.sk = Z64
        to = npy.Account(addr=PACC0)
        with pytest.raises(ValueError, match="Amount must be a positive integer"):
            acc.send(to, -1)
        with pytest.raises(ValueError, match="raw balance after send cannot be < 0"):
            acc.send(to, 1)
        acc.raw_bal = 2
        acc.send(to, 1, work="f" * 16)
        b = acc.send(to, 1, to)
        assert b.verify_signature()
        assert acc.frontier == b.digest
        assert acc.raw_bal == b.bal
        assert acc.raw_bal == 0
        assert acc.rep == to


class TestNetwork:
    def test_from_multiplier(self) -> None:
        assert "fffffe0000000000" == npy.NANO.from_multiplier(1 / 8)

    def test_to_multiplier(self) -> None:
        with pytest.raises(ValueError, match="Difficulty should be 16 hex char"):
            npy.NANO.to_multiplier("0")
        assert 0.125 == npy.NANO.to_multiplier("fffffe0000000000")

    def test_from_pk(self) -> None:
        with pytest.raises(ValueError, match="Public key should be 64 hex char"):
            npy.NANO.from_pk("0")
        assert PACC0 == npy.NANO.from_pk(Z64)

    def test_to_pk(self) -> None:
        with pytest.raises(ValueError, match="Invalid address"):
            npy.NANO.to_pk("nano_wrong_address")
        with pytest.raises(ValueError, match="Invalid address"):
            npy.NANO.to_pk(
                "xxxx_111111111111111111111111111111111111111111111111111111111111"
            )
        with pytest.raises(ValueError, match="Invalid address"):
            npy.NANO.to_pk(
                "nano_1111111111111111111111111111111111111111111111111111hifc8npr"
            )
        assert Z64 == npy.NANO.to_pk(PACC0)

    def test_from_raw(self) -> None:
        assert "0.000000000000000000000123456789" == npy.NANO.from_raw(123456789)
        assert "1.234567890000000000000000000000" == npy.NANO.from_raw(
            1234567890000000000000000000000
        )

    def test_to_raw(self) -> None:
        assert 123456789 == npy.NANO.to_raw("0.000000000000000000000123456789")
        assert 1234567890000000000000000000000 == npy.NANO.to_raw("1.23456789")


class TestStateBlock:
    acc = npy.Account()
    acc.sk = Z64
    b = npy.StateBlock(acc, acc, acc.raw_bal, acc.frontier, Z64)

    def test_digest(self) -> None:
        assert (
            self.b.digest
            == "1f5bc8e8c4b862fdc5d01857325dade3561349505f4a4d478610e3394d2105f3"
        )

    def test_json(self) -> None:
        d = {
            "type": "state",
            "account": SACC0,
            "previous": Z64,
            "representative": SACC0,
            "balance": 0,
            "link": Z64,
            "work": "",
            "signature": "",
        }
        assert self.b.json == json.dumps(d)

    def test_verify_signature(self) -> None:
        self.b.sig = "c55eaa93631bcb701ca1d1f080b73d279c501a24e743566cd3f78c74de7c055242169d28cc171a468d1f85f93e441b75081699e210d941aa320f041ebd2fcb03"
        assert self.b.verify_signature()

    def test_work_generate(self) -> None:
        self.b.work_generate(npy.NANO.receive_difficulty)
        assert work_validate(self.b, npy.NANO.receive_difficulty)

    def test_work_validate(self) -> None:
        self.b.work = "0" * 16
        assert not self.b.work_validate(npy.NANO.receive_difficulty)
        self.b.work = "e1c6427755027448"
        assert self.b.work_validate(npy.NANO.receive_difficulty)
