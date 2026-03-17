"""
nanopy
######
"""

import base64
import binascii
import decimal
import hashlib
import hmac
import os
from . import work  # type: ignore
from . import ed25519_blake2b  # type: ignore

ACCOUNT_PREFIX = "nano_"
DIFFICULTY = "ffffffc000000000"
EXPONENT = 30

decimal.setcontext(decimal.BasicContext)
decimal.getcontext().traps[decimal.Inexact] = True
decimal.getcontext().traps[decimal.Subnormal] = True
decimal.getcontext().prec = 40
_D = decimal.Decimal

B32STD = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
B32NANO = b"13456789abcdefghijkmnopqrstuwxyz"
NANO2B32 = bytes.maketrans(B32NANO, B32STD)
B322NANO = bytes.maketrans(B32STD, B32NANO)


def state_block() -> dict[str, str]:
    """Get a dict with fields of a state block

    :return: a state block
    """
    return dict(
        [
            ("type", "state"),
            ("account", ""),
            ("previous", "0" * 64),
            ("representative", ""),
            ("balance", ""),
            ("link", "0" * 64),
            ("work", ""),
            ("signature", ""),
        ]
    )


def account_key(account: str) -> str:
    """Get the public key for account

    :arg account: account number
    :return: 64 hex-char public key
    :raise AssertionError: for invalid account
    """
    assert (
        len(account) == len(ACCOUNT_PREFIX) + 60
        and account[: len(ACCOUNT_PREFIX)] == ACCOUNT_PREFIX
    )

    p = base64.b32decode((b"1111" + account[-60:].encode()).translate(NANO2B32))

    checksum = p[:-6:-1]
    p = p[3:-5]

    assert hashlib.blake2b(p, digest_size=5).digest() == checksum

    return p.hex()


def account_get(pk: str) -> str:
    """Get account number for the public key

    :arg pk: 64 hex-char public key
    :return: account number
    :raise AssertionError: for invalid key
    """
    assert len(pk) == 64

    p = bytes.fromhex(pk)
    checksum = hashlib.blake2b(p, digest_size=5).digest()
    p = b"\x00\x00\x00" + p + checksum[::-1]
    account = base64.b32encode(p)
    account = account.translate(B322NANO)[4:]

    return ACCOUNT_PREFIX + account.decode()


def validate_account_number(account: str) -> bool:
    """Check whether account is a valid account number using checksum

    :arg account: account number
    """
    try:
        account_key(account)
        return True
    except AssertionError:
        return False
    except binascii.Error:
        return False


def key_expand(sk: str) -> tuple[str, str, str]:
    """Derive public key and account number from private key

    :arg sk: 64 hex-char private key
    :return: (private key, public key, account number)
    :raise AssertionError: for invalid key
    """
    assert len(sk) == 64
    pk = ed25519_blake2b.publickey(bytes.fromhex(sk)).hex()
    return sk, pk, account_get(pk)


def deterministic_key(seed: str, index: int = 0) -> tuple[str, str, str]:
    """Derive deterministic keypair from seed based on index

    :arg seed: 64 hex-char seed
    :arg index: index number, 0 to 2^32 - 1
    :return: (private key, public key, account number)
    :raise AssertionError: for invalid seed
    """
    assert len(seed) == 64
    return key_expand(
        hashlib.blake2b(
            bytes.fromhex(seed) + index.to_bytes(4, byteorder="big"), digest_size=32
        ).hexdigest()
    )


try:
    import mnemonic

    def generate_mnemonic(strength: int = 256, language: str = "english") -> str:
        """Generate a BIP39 type mnemonic. Requires `mnemonic <https://pypi.org/project/mnemonic>`_

        :arg strength: choose from 128, 160, 192, 224, 256
        :arg language: one of the installed word list languages
        :return: word list
        """
        m = mnemonic.Mnemonic(language)
        return m.generate(strength=strength)

    def mnemonic_key(
        words: str, index: int = 0, passphrase: str = "", language: str = "english"
    ) -> tuple[str, str, str]:
        """Derive deterministic keypair from mnemonic based on index. Requires
          `mnemonic <https://pypi.org/project/mnemonic>`_

        :arg words: word list
        :arg index: account index
        :arg passphrase: passphrase to generate seed
        :arg language: word list language
        :return: (private key, public key, account number)
        :raise AssertionError: for invalid string of words
        """
        m = mnemonic.Mnemonic(language)
        assert m.check(words)
        key = b"ed25519 seed"
        msg = m.to_seed(words, passphrase)
        h = hmac.new(key, msg, hashlib.sha512).digest()
        sk, key = h[:32], h[32:]
        for i in [44, 165, index]:
            i = i | 0x80000000
            msg = b"\x00" + sk + i.to_bytes(4, byteorder="big")
            h = hmac.new(key, msg, hashlib.sha512).digest()
            sk, key = h[:32], h[32:]
        return key_expand(sk.hex())

except ModuleNotFoundError:  # pragma: no cover
    pass  # pragma: no cover


def from_multiplier(multiplier: float) -> str:
    """Get difficulty from multiplier

    :arg multiplier: positive number
    :return: 16 hex-char difficulty
    """
    return format(
        int((int(DIFFICULTY, 16) - (1 << 64)) / multiplier + (1 << 64)), "016x"
    )


def to_multiplier(difficulty: str) -> float:
    """Get multiplier from difficulty

    :arg difficulty: 16 hex-char difficulty
    :return: multiplier
    """
    return float((1 << 64) - int(DIFFICULTY, 16)) / float(
        (1 << 64) - int(difficulty, 16)
    )


def work_validate(
    _work: str, _hash: str, difficulty: str = "", multiplier: float = 0
) -> bool:
    """Check whether _work is valid for _hash.

    :arg _work: 16 hex-char work
    :arg _hash: 64 hex-char hash
    :arg difficulty: 16 hex-char difficulty
    :arg multiplier: positive number, overrides difficulty
    """
    if multiplier:
        difficulty = from_multiplier(multiplier)
    elif not difficulty:
        difficulty = DIFFICULTY
    assert len(_work) == 16
    assert len(_hash) == 64
    assert len(difficulty) == 16
    return bool(
        work.validate(int(_work, 16), bytes.fromhex(_hash), int(difficulty, 16))
    )


def work_generate(_hash: str, difficulty: str = "", multiplier: float = 0) -> str:
    """Compute work for _hash.

    :arg _hash: 64 hex-char hash
    :arg difficulty: 16 hex-char difficulty
    :arg multiplier: positive number, overrides difficulty
    :return: 16 hex-char work
    """
    if multiplier:
        difficulty = from_multiplier(multiplier)
    elif not difficulty:
        difficulty = DIFFICULTY
    assert len(_hash) == 64
    assert len(difficulty) == 16
    return format(work.generate(bytes.fromhex(_hash), int(difficulty, 16)), "016x")


def from_raw(amount: str, exp: int = 0) -> str:
    """Divide amount by 10^exp

    :arg amount: amount
    :arg exp: positive number
    :return: amount divided by 10^exp
    """
    assert isinstance(amount, str)
    if exp <= 0:
        exp = EXPONENT
    nano = _D(amount) * _D(_D(10) ** -exp)
    return format(nano.quantize(_D(_D(10) ** -exp)), "." + str(exp) + "f")


def to_raw(amount: str, exp: int = 0) -> str:
    """Multiply amount by 10^exp

    :arg amount: amount
    :arg exp: positive number
    :return: amount multiplied by 10^exp
    """
    assert isinstance(amount, str)
    if exp <= 0:
        exp = EXPONENT
    raw = _D(amount) * _D(_D(10) ** exp)
    return str(raw.quantize(_D(1)))


def block_hash(block: dict[str, str]) -> str:
    """Compute block hash

    :arg block: "account", "previous", "representative", "balance", and "link" are the required
      entries
    :return: 64 hex-char hash
    """
    return hashlib.blake2b(
        bytes.fromhex(
            "0" * 63
            + "6"
            + account_key(block["account"])
            + block["previous"]
            + account_key(block["representative"])
            + format(int(block["balance"]), "032x")
            + block["link"]
        ),
        digest_size=32,
    ).hexdigest()


def sign(sk: str, _hash: str) -> str:
    """Sign a hash

    :arg sk: 64 hex-char private key
    :arg _hash: 64 hex-char hash
    :return: 128 hex-char signature
    """

    assert len(sk) == 64
    assert len(_hash) == 64

    h = bytes.fromhex(_hash)
    s = bytes.fromhex(sk)

    return str(ed25519_blake2b.signature(s, h, os.urandom(32)).hex())


def verify_signature(sig: str, pk: str, _hash: str) -> bool:
    """Verify signature for hash with public key

    :arg sig: signature for the message
    :arg pk: public key for the signature
    :arg _hash: 64 hex-char hash
    :return: True if valid, False otherwise
    """

    s = bytes.fromhex(sig)
    p = bytes.fromhex(pk)
    h = bytes.fromhex(_hash)

    return bool(ed25519_blake2b.checkvalid(s, p, h))


def block_create(
    sk: str,
    previous: str,
    representative: str,
    balance: str,
    link: str,
    _work: str = "",
    difficulty: str = "",
) -> dict[str, str]:
    """Create a block

    :arg sk: 64 hex-char private key
    :arg previous: 64 hex-char previous hash
    :arg representative: representative address
    :arg balance: balance in raw
    :arg link: 64 hex-char link
    :arg _work: 16 hex-char work
    :arg difficulty: 16 hex-char difficulty: send/change require a minimum #fffffff800000000
      and receive requires #fffffe0000000000. Default is #ffffffc000000000.
    :return: a block with work and signature
    """
    nb = state_block()
    _, pk, acc = key_expand(sk)
    work_hash = previous if previous else pk
    if not difficulty:
        difficulty = DIFFICULTY
    nb["account"] = acc
    nb["previous"] = previous if previous else "0" * 64
    nb["representative"] = representative
    nb["balance"] = balance
    nb["link"] = link
    nb["work"] = _work if _work else work_generate(work_hash, difficulty)
    nb["signature"] = sign(sk, block_hash(nb))
    return nb
