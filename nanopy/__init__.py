"""
nanopy
######
"""

import os, hashlib, base64, decimal, hmac, nanopy.work
import nanopy.ed25519_blake2b as ed25519_blake2b

account_prefix = "nano_"
work_difficulty = "ffffffc000000000"
standard_exponent = 30

decimal.getcontext().traps[decimal.Inexact] = 1
decimal.getcontext().prec = 40
_D = decimal.Decimal

_B32 = b"13456789abcdefghijkmnopqrstuwxyz"


def state_block():
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


def account_key(account):
    """Get the public key for account

    :param str account: account number
    :return: 64 hex-char public key
    :rtype: str
    :raise AssertionError: for invalid account
    """
    assert (
        len(account) == len(account_prefix) + 60
        and account[: len(account_prefix)] == account_prefix
    )

    account = b"1111" + account[-60:].encode()
    account = account.translate(bytes.maketrans(_B32, base64._b32alphabet))
    key = base64.b32decode(account)

    checksum = key[:-6:-1]
    key = key[3:-5]

    assert hashlib.blake2b(key, digest_size=5).digest() == checksum

    return key.hex()


def account_get(key):
    """Get account number for the public key

    :param str key: 64 hex-char public key
    :return: account number
    :rtype: str
    :raise AssertionError: for invalid key
    """
    assert len(key) == 64

    key = bytes.fromhex(key)
    checksum = hashlib.blake2b(key, digest_size=5).digest()
    key = b"\x00\x00\x00" + key + checksum[::-1]
    account = base64.b32encode(key)
    account = account.translate(bytes.maketrans(base64._b32alphabet, _B32))[4:]

    return account_prefix + account.decode()


def validate_account_number(account):
    """Check whether account is a valid account number using checksum

    :param str account: account number
    :return: ``True``/``False``
    :rtype: bool
    """
    try:
        account_key(account)
        return True
    except:
        return False


def key_expand(key):
    """Derive public key and account number from private key

    :param str key: 64 hex-char private key
    :return: (private key, public key, account number)
    :rtype: tuple
    :raise AssertionError: for invalid key
    """
    assert len(key) == 64
    pk = ed25519_blake2b.publickey(bytes.fromhex(key)).hex()
    return key, pk, account_get(pk)


def deterministic_key(seed, index=0):
    """Derive deterministic keypair from seed based on index

    :param str seed: 64 hex-char seed
    :param int index: index number, 0 to 2^32 - 1
    :return: (private key, public key, account number)
    :rtype: tuple
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

    def generate_mnemonic(strength=256, language="english"):
        """Generate a BIP39 type mnemonic. Requires `mnemonic <https://pypi.org/project/mnemonic>`_

        :param int strength: choose from 128, 160, 192, 224, 256
        :param str language: one of the installed word list languages
        :return: word list
        :rtype: str
        """
        m = mnemonic.Mnemonic(language)
        return m.generate(strength=strength)

    def mnemonic_key(words, index=0, passphrase="", language="english"):
        """Derive deterministic keypair from mnemonic based on index. Requires `mnemonic <https://pypi.org/project/mnemonic>`_

        :param str words: word list
        :return: (private key, public key, account number)
        :rtype: tuple
        :raise AssertionError: for invalid key
        """
        m = mnemonic.Mnemonic(language)
        assert m.check(words)
        for i in ["m", 44, 165, index]:
            if i == "m":
                key = b"ed25519 seed"
                msg = m.to_seed(words, passphrase)
            else:
                i = i | 0x80000000
                msg = b"\x00" + sk + i.to_bytes(4, byteorder="big")
            h = hmac.new(key, msg, hashlib.sha512).digest()
            sk, key = h[:32], h[32:]
        return key_expand(sk.hex())

except ModuleNotFoundError:
    pass


def from_multiplier(multiplier):
    """Get difficulty from multiplier

    :param float multiplier: positive number
    :return: 16 hex-char difficulty
    :rtype: str
    """
    return format(
        int((int(work_difficulty, 16) - (1 << 64)) / multiplier + (1 << 64)), "016x"
    )


def to_multiplier(difficulty):
    """Get multiplier from difficulty

    :param str difficulty: 16 hex-char difficulty
    :return: multiplier
    :rtype: float
    """
    return float((1 << 64) - int(work_difficulty, 16)) / float(
        (1 << 64) - int(difficulty, 16)
    )


def work_validate(work, _hash, difficulty=None, multiplier=0):
    """Check whether work is valid for _hash.

    :param str work: 16 hex-char work
    :param str _hash: 64 hex-char hash
    :param str difficulty: 16 hex-char difficulty
    :param float multiplier: positive number, overrides difficulty
    :return: ``True``/``False``
    :rtype: bool
    """
    assert len(work) == 16
    assert len(_hash) == 64
    if multiplier:
        difficulty = from_multiplier(multiplier)
    else:
        difficulty = difficulty if difficulty else work_difficulty
    return bool(
        nanopy.work.validate(int(work, 16), bytes.fromhex(_hash), int(difficulty, 16))
    )


def work_generate(_hash, difficulty=None, multiplier=0):
    """Check whether work is valid for _hash.

    :param str _hash: 64 hex-char hash
    :param str difficulty: 16 hex-char difficulty
    :param float multiplier: positive number, overrides difficulty
    :return: 16 hex-char work
    :rtype: str
    """
    assert len(_hash) == 64
    if multiplier:
        difficulty = from_multiplier(multiplier)
    else:
        difficulty = difficulty if difficulty else work_difficulty
    work = format(
        nanopy.work.generate(bytes.fromhex(_hash), int(difficulty, 16)), "016x"
    )
    return work


def from_raw(amount, exp=0):
    """Divide amount by 10^exp

    :param str amount: amount
    :param int exp: positive number
    :return: amount divided by 10^exp
    :rtype: str
    """
    assert type(amount) is str
    exp = exp if exp else standard_exponent
    nano = _D(amount) * _D(_D(10) ** -exp)
    return format(nano.quantize(_D(_D(10) ** -exp)), "." + str(exp) + "f")


def to_raw(amount, exp=0):
    """Multiply amount by 10^exp

    :param str amount: amount
    :param int exp: positive number
    :return: amount multiplied by 10^exp
    :rtype: str
    """
    assert type(amount) is str
    exp = exp if exp else standard_exponent
    raw = _D(amount) * _D(_D(10) ** exp)
    return str(raw.quantize(_D(1)))


def raw_to_nano(amount):
    """Divide a raw amount down by the raw-nano ratio (10^30)

    :param str amount: amount in raw
    :return: amount in nano
    :rtype: str
    """
    return from_raw(amount, exp=30)


def nano_to_raw(amount):
    """Multiply a nano amount by the raw-nano ratio (10^30)

    :param str amount: amount in nano
    :return: amount in raw
    :rtype: str
    """
    return to_raw(amount, exp=30)


def block_hash(block):
    """Compute block hash

    :param dict block: "account", "previous", "representative", "balance", and "link" are the required entries
    :return: 64 hex-char hash
    :rtype: str
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


def sign(key, block=None, _hash=None, msg=None, account=None, pk=None):
    """Sign a block, hash, or message

    :param str key: 64 hex-char private key
    :param dict block: "account", "previous", "representative", "balance", and "link" are the required entries
    :param str _hash: 64 hex-char hash. Overrides ``block``.
    :param str msg: message to sign. Overrides ``_hash`` and ``block``.
    :param str account: account
    :param str pk: 64 hex-char public key
    :return: 128 hex-char signature
    :rtype: str
    """
    sk = bytes.fromhex(key)

    if msg:
        m = msg.encode()
    elif _hash:
        m = bytes.fromhex(_hash)
    elif block:
        m = bytes.fromhex(block_hash(block))
    else:
        return None

    if not pk:
        if account:
            pk = bytes.fromhex(account_key(account))
        elif block:
            pk = bytes.fromhex(account_key(block["account"]))
        else:
            pk = ed25519_blake2b.publickey(sk)
    else:
        pk = bytes.fromhex(pk)

    return ed25519_blake2b.signature(m, os.urandom(32), sk, pk).hex()


def verify_signature(msg, sig, pk):
    """Verify signature for message with public key

    :param str message: message to verify
    :param str signature: signature for the message
    :param str pk: public key for the signature
    :return bool: True if valid, False otherwise
    """
    m = msg.encode()
    s = bytes.fromhex(sig)
    k = bytes.fromhex(pk)

    return bool(ed25519_blake2b.checkvalid(s, m, k))


def block_create(
    key, previous, representative, balance, link, work=None, difficulty=None
):
    """Create a block

    :param str key: 64 hex-char private key
    :param str previous: 64 hex-char previous hash
    :param str representative: representative address
    :param str balance: balance in raw
    :param str link: 64 hex-char link
    :param str work: 16 hex-char work
    :param str difficulty: 16 hex-char difficulty: send/change require a minimum #fffffff800000000 and receive requires #fffffe0000000000. Default is #ffffffc000000000.
    :return: a block with work and signature
    :rtype: dict
    """
    nb = state_block()
    nb["account"] = account_get(ed25519_blake2b.publickey(bytes.fromhex(key)).hex())
    nb["previous"] = previous
    nb["representative"] = representative
    nb["balance"] = balance
    nb["link"] = link
    nb["work"] = work if work else work_generate(block_hash(nb), difficulty)
    nb["signature"] = sign(key, block=nb)
    return nb
