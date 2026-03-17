import hashlib
import nanopy as npy


def work_validate(
    work: str, _hash: str, difficulty: str = "", multiplier: float = 0
) -> bool:
    if multiplier:
        difficulty = npy.from_multiplier(multiplier)
    elif not difficulty:
        difficulty = npy.DIFFICULTY
    assert len(work) == 16
    assert len(_hash) == 64
    assert len(difficulty) == 16

    w = bytearray.fromhex(work)
    h = bytes.fromhex(_hash)

    w.reverse()
    b2b_h = bytearray(hashlib.blake2b(w + h, digest_size=8).digest())
    b2b_h.reverse()
    if b2b_h >= bytes.fromhex(difficulty):
        return True
    return False


def test_state_block() -> None:
    sb = npy.state_block()
    assert sb["type"] == "state"
    assert sb["account"] == ""
    assert sb["previous"] == "0" * 64
    assert sb["representative"] == ""
    assert sb["balance"] == ""
    assert sb["link"] == "0" * 64
    assert sb["work"] == ""
    assert sb["signature"] == ""


def test_account_key() -> None:
    assert (
        npy.account_key(
            "nano_1111111111111111111111111111111111111111111111111111hifc8npp"
        )
        == "0" * 64
    )


def test_account_get() -> None:
    assert (
        npy.account_get("0" * 64)
        == "nano_1111111111111111111111111111111111111111111111111111hifc8npp"
    )


def test_validate_account_number() -> None:
    assert npy.validate_account_number(
        "nano_1111111111111111111111111111111111111111111111111111hifc8npp"
    )
    assert not npy.validate_account_number(
        "nano_1111111111111111111111111111111111111111111111111111hifc8npy"
    )
    assert not npy.validate_account_number(
        "nano_1111111111111111111111111111111111111111111111111111hifc8np0"
    )


def test_deterministic_key() -> None:
    assert npy.deterministic_key("0" * 64, 0) == (
        "9f0e444c69f77a49bd0be89db92c38fe713e0963165cca12faf5712d7657120f",
        "c008b814a7d269a1fa3c6528b19201a24d797912db9996ff02a1ff356e45552b",
        "nano_3i1aq1cchnmbn9x5rsbap8b15akfh7wj7pwskuzi7ahz8oq6cobd99d4r3b7",
    )


def test_generate_mnemonic() -> None:
    assert len(npy.generate_mnemonic(strength=256, language="english").split()) == 24


def test_mnemonic_key() -> None:
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


def test_from_multiplier() -> None:
    assert "fffffe0000000000" == npy.from_multiplier(1 / 8)


def test_to_multiplier() -> None:
    assert 0.125 == npy.to_multiplier("fffffe0000000000")


def test_work_validate() -> None:
    assert npy.work_validate(
        "e1c6427755027448", "0" * 64, difficulty=npy.from_multiplier(1 / 8)
    )
    assert npy.work_validate("e1c6427755027448", "0" * 64, multiplier=1 / 8)
    assert not npy.work_validate("e1c6427755027448", "0" * 64)
    npy.DIFFICULTY = npy.from_multiplier(1 / 8)
    assert npy.work_validate("e1c6427755027448", "0" * 64)


def test_work_generate() -> None:
    assert work_validate(
        npy.work_generate("0" * 64, difficulty=npy.from_multiplier(1 / 8)),
        "0" * 64,
        multiplier=1 / 8,
    )
    assert work_validate(
        npy.work_generate("0" * 64, multiplier=1 / 8), "0" * 64, multiplier=1 / 8
    )
    npy.DIFFICULTY = npy.from_multiplier(1 / 8)
    assert work_validate(npy.work_generate("0" * 64), "0" * 64)


def test_from_raw() -> None:
    assert "0.000000000000000000000123456789" == npy.from_raw("123456789")
    assert "1.234567890000000000000000000000" == npy.from_raw(
        "1234567890000000000000000000000"
    )


def test_to_raw() -> None:
    assert "123456789" == npy.to_raw("0.000000000000000000000123456789")
    assert "1234567890000000000000000000000" == npy.to_raw("1.23456789")


def test_block_hash() -> None:
    assert (
        npy.block_hash(
            {
                "account": "nano_1111111111111111111111111111111111111111111111111111hifc8npp",
                "previous": "0" * 64,
                "representative": "nano_1111111111111111111111111111111111111111111111111111hifc8npp",
                "balance": "0",
                "link": "0" * 64,
            }
        )
        == "262fe88523691984386d53b022c52d5a8e414570d8a3ce941475760184465b18"
    )


def test_sign() -> None:
    sk, pk, _ = npy.key_expand("0" * 64)
    h = "0" * 64
    sig = npy.sign(sk, h)
    assert npy.verify_signature(sig, pk, h)


def test_verify_signature() -> None:
    _, pk, _ = npy.key_expand("0" * 64)
    h = "0" * 64
    sig = "094708dc716647d0f039dc7ea683eb9ebeb35e8f2f21d70d6513b3d4711953efaf129ca0ebe46650dd13afe63327d45bf792ede71fe3058c6a5e1019c2dd240a"
    assert npy.verify_signature(sig, pk, h)
    assert not npy.verify_signature("0" * 64, pk, h)


def test_block_create() -> None:
    b = npy.block_create("0" * 64, "", npy.account_get("0" * 64), "0", "0" * 64)
    assert npy.verify_signature(
        b["signature"], npy.account_key(b["account"]), npy.block_hash(b)
    )
    assert npy.work_validate(b["work"], npy.account_key(b["account"]))

    b = npy.block_create("0" * 64, "0" * 64, npy.account_get("0" * 64), "0", "0" * 64)
    assert npy.verify_signature(
        b["signature"], npy.account_key(b["account"]), npy.block_hash(b)
    )
    assert npy.work_validate(b["work"], "0" * 64)
