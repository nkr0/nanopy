import hashlib
import json
import re
import pytest
import nanopy as npy


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
        npy.deterministic_key("0" * 64, 0)
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


def test_account_init() -> None:
    n = npy.Network()
    with pytest.raises(ValueError, match="One of acc, pk, or sk is needed"):
        npy.Account(n)
    assert (
        npy.Account(
            n, acc="nano_1111111111111111111111111111111111111111111111111111hifc8npp"
        ).pk
        == "0" * 64
    )
    assert (
        str(npy.Account(n, pk="0" * 64))
        == "nano_1111111111111111111111111111111111111111111111111111hifc8npp"
    )
    assert (
        npy.Account(n, pk="0" * 64).acc
        == "nano_1111111111111111111111111111111111111111111111111111hifc8npp"
    )
    assert (
        npy.Account(n, sk="0" * 64).acc
        == "nano_18gmu6engqhgtjnppqam181o5nfhj4sdtgyhy36dan3jr9spt84rzwmktafc"
    )


def test_account_bal() -> None:
    n = npy.Network()
    acc = npy.Account(n, pk="0" * 64)
    assert acc.bal() == "0.000000000000000000000000000000"
    acc.raw_bal = 1
    assert acc.bal() == "0.000000000000000000000000000001"


def test_account_change_rep() -> None:
    n = npy.Network()
    with pytest.raises(NotImplementedError, match="This method needs private key"):
        npy.Account(n, pk="0" * 64).change_rep(npy.Account(n, pk="0" * 64))
    acc = npy.Account(n, sk="0" * 64)
    b = acc.change_rep(acc)
    assert b.verify_signature()
    assert acc.frontier == b.digest()


def test_account_receive() -> None:
    n = npy.Network()
    with pytest.raises(NotImplementedError, match="This method needs private key"):
        npy.Account(n, pk="0" * 64).receive("0" * 64, 1)
    with pytest.raises(AttributeError, match="Amount must be a positive integer"):
        acc = npy.Account(n, sk="0" * 64)
        acc.receive("0" * 64, -1)
    with pytest.raises(
        AttributeError, match=re.escape("Balance after receive cannot be >= 2^128")
    ):
        acc = npy.Account(n, sk="0" * 64)
        acc.receive("0" * 64, 1 << 128)
    acc = npy.Account(n, sk="0" * 64)
    acc.raw_bal = 0
    b = acc.receive("0" * 64, 1)
    assert b.verify_signature()
    assert acc.frontier == b.digest()
    assert acc.raw_bal == 1
    rep = npy.Account(n, pk="0" * 64)
    b = acc.receive("0" * 64, 1, rep)
    assert b.verify_signature()
    assert acc.frontier == b.digest()
    assert acc.raw_bal == 2
    assert acc.rep == rep


def test_account_send() -> None:
    n = npy.Network()
    with pytest.raises(NotImplementedError, match="This method needs private key"):
        npy.Account(n, pk="0" * 64).send(npy.Account(n, pk="0" * 64), 1)
    with pytest.raises(AttributeError, match="Amount must be a positive integer"):
        acc = npy.Account(n, sk="0" * 64)
        acc.send(acc, -1)
    with pytest.raises(AttributeError, match="Balance after send cannot be < 0"):
        acc = npy.Account(n, sk="0" * 64)
        acc.send(acc, 1)
    acc = npy.Account(n, sk="0" * 64)
    acc.raw_bal = 2
    b = acc.send(acc, 1)
    assert b.verify_signature()
    assert acc.frontier == b.digest()
    assert acc.raw_bal == 1
    rep = npy.Account(n, pk="0" * 64)
    b = acc.send(acc, 1, rep)
    assert b.verify_signature()
    assert acc.frontier == b.digest()
    assert acc.raw_bal == 0
    assert acc.rep == rep


def test_account_set_bal() -> None:
    n = npy.Network()
    acc = npy.Account(n, pk="0" * 64)
    acc.set_bal("1")
    assert acc.bal() == "1.000000000000000000000000000000"


def test_account_sign() -> None:
    n = npy.Network()
    with pytest.raises(NotImplementedError, match="This method needs private key"):
        acc = npy.Account(n, pk="0" * 64)
        b = npy.StateBlock(acc, acc, acc.raw_bal, acc.frontier, "0" * 64)
        acc.sign(b)
    acc = npy.Account(n, sk="0" * 64)
    b = npy.StateBlock(acc, acc, acc.raw_bal, acc.frontier, "0" * 64)
    acc.sign(b)
    assert b.verify_signature()


def test_state_block_digest() -> None:
    n = npy.Network()
    acc = npy.Account(n, pk="0" * 64)
    assert (
        npy.StateBlock(acc, acc, acc.raw_bal, acc.frontier, "0" * 64).digest()
        == "262fe88523691984386d53b022c52d5a8e414570d8a3ce941475760184465b18"
    )


def test_state_block_json() -> None:
    n = npy.Network()
    acc = npy.Account(n, pk="0" * 64)
    d = {
        "type": "state",
        "account": "nano_1111111111111111111111111111111111111111111111111111hifc8npp",
        "previous": "0000000000000000000000000000000000000000000000000000000000000000",
        "representative": "nano_1111111111111111111111111111111111111111111111111111hifc8npp",
        "balance": 0,
        "link": "0000000000000000000000000000000000000000000000000000000000000000",
        "work": "",
        "signature": "",
    }
    assert npy.StateBlock(
        acc, acc, acc.raw_bal, acc.frontier, "0" * 64
    ).json() == json.dumps(d)


def test_state_block_verify_signature() -> None:
    n = npy.Network()
    acc = npy.Account(n, sk="0" * 64)
    b = npy.StateBlock(acc, acc, acc.raw_bal, acc.frontier, "0" * 64)
    b.sig = "c55eaa93631bcb701ca1d1f080b73d279c501a24e743566cd3f78c74de7c055242169d28cc171a468d1f85f93e441b75081699e210d941aa320f041ebd2fcb03"
    assert b.verify_signature()


def test_state_block_work_generate() -> None:
    n = npy.Network()
    acc = npy.Account(n, pk="0" * 64)
    b = npy.StateBlock(acc, acc, acc.raw_bal, acc.frontier, "0" * 64)
    b.work_generate(n.receive_difficulty)
    assert work_validate(b, n.receive_difficulty)


def test_state_block_work_validate() -> None:
    n = npy.Network()
    acc = npy.Account(n, pk="0" * 64)
    b = npy.StateBlock(acc, acc, acc.raw_bal, acc.frontier, "0" * 64)
    b.work = "0" * 16
    assert not b.work_validate(n.receive_difficulty)
    b.work = "e1c6427755027448"
    assert b.work_validate(n.receive_difficulty)


def test_network_from_raw() -> None:
    n = npy.Network()
    assert "0.000000000000000000000123456789" == n.from_raw(123456789)
    assert "1.234567890000000000000000000000" == n.from_raw(
        1234567890000000000000000000000
    )


def test_network_to_raw() -> None:
    n = npy.Network()
    assert 123456789 == n.to_raw("0.000000000000000000000123456789")
    assert 1234567890000000000000000000000 == n.to_raw("1.23456789")


def test_network_from_multiplier() -> None:
    n = npy.Network()
    assert "fffffe0000000000" == n.from_multiplier(1 / 8)


def test_network_to_multiplier() -> None:
    n = npy.Network()
    assert 0.125 == n.to_multiplier("fffffe0000000000")
