"""
nanopy
######
"""

import base64
import binascii
import dataclasses
import decimal
import hashlib
import hmac
import json
import os
from typing import Optional
from . import work  # type: ignore
from . import ed25519_blake2b  # type: ignore

decimal.setcontext(decimal.BasicContext)
decimal.getcontext().traps[decimal.Inexact] = True
decimal.getcontext().traps[decimal.Subnormal] = True
decimal.getcontext().prec = 40
_D = decimal.Decimal

B32STD = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
B32NANO = b"13456789abcdefghijkmnopqrstuwxyz"
NANO2B32 = bytes.maketrans(B32NANO, B32STD)
B322NANO = bytes.maketrans(B32STD, B32NANO)


def deterministic_key(seed: str, i: int = 0) -> str:
    """Derive deterministic private key from seed based on index i

    :arg seed: 64 hex-char seed
    :arg i: index number, 0 to 2^32 - 1
    :return: 64 hex-char private key
    """
    assert len(seed) == 64
    assert 0 <= i <= 1 << 32
    return hashlib.blake2b(
        bytes.fromhex(seed) + i.to_bytes(4, byteorder="big"), digest_size=32
    ).hexdigest()


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
        words: str, i: int = 0, passphrase: str = "", language: str = "english"
    ) -> str:
        """Derive deterministic private key from mnemonic based on index i. Requires
          `mnemonic <https://pypi.org/project/mnemonic>`_

        :arg words: word list
        :arg i: account index
        :arg passphrase: passphrase to generate seed
        :arg language: word list language
        :return: 64 hex-char private key
        """
        m = mnemonic.Mnemonic(language)
        assert m.check(words)
        key = b"ed25519 seed"
        msg = m.to_seed(words, passphrase)
        h = hmac.new(key, msg, hashlib.sha512).digest()
        sk, key = h[:32], h[32:]
        for j in [44, 165, i]:
            j = j | 0x80000000
            msg = b"\x00" + sk + j.to_bytes(4, byteorder="big")
            h = hmac.new(key, msg, hashlib.sha512).digest()
            sk, key = h[:32], h[32:]
        return sk.hex()

except ModuleNotFoundError:  # pragma: no cover
    pass  # pragma: no cover


class Account:
    """Account

    :arg network: network of this account
    :arg sk: private/secret key
    :arg pk: public key
    :arg acc: account address
    """

    def __init__(
        self, network: "Network", sk: str = "", pk: str = "", acc: str = ""
    ) -> None:
        self.acc = ""
        self.frontier = "0" * 64
        self.network = network
        self.pk = ""
        self.raw_bal = 0
        self.rep = self
        self.sk = ""
        if sk:
            self.sk = sk
            self._set_pk_acc()
        elif pk:
            self.pk = pk
            self._set_acc()
        elif acc:
            self.acc = acc
            self._set_pk()
        else:
            raise ValueError("One of acc, pk, or sk is needed")

    def __repr__(self) -> str:
        """class string represenation

        :return: account address as string
        """
        return self.acc

    def _set_acc(self) -> None:
        "Set account from public key"
        assert len(self.pk) == 64
        p = bytes.fromhex(self.pk)
        checksum = hashlib.blake2b(p, digest_size=5).digest()
        p = b"\x00\x00\x00" + p + checksum[::-1]
        acc = base64.b32encode(p)
        acc = acc.translate(B322NANO)[4:]
        self.acc = self.network.prefix + acc.decode()

    def _set_pk(self) -> None:
        "Set public key from account"
        assert (
            len(self.acc) == len(self.network.prefix) + 60
            and self.acc[: len(self.network.prefix)] == self.network.prefix
        )

        p = base64.b32decode((b"1111" + self.acc[-60:].encode()).translate(NANO2B32))
        checksum = p[:-6:-1]
        p = p[3:-5]
        assert hashlib.blake2b(p, digest_size=5).digest() == checksum
        self.pk = p.hex()

    def _set_pk_acc(self) -> None:
        "Set public key and account number from private key"
        assert len(self.sk) == 64
        self.pk = ed25519_blake2b.publickey(bytes.fromhex(self.sk)).hex()
        self._set_acc()

    def bal(self, exp: int = 0) -> str:
        """Account balance

        :arg exp: exponent to convert bal to raw
        :return: account balance
        """
        return self.network.from_raw(self.raw_bal, exp)

    def change_rep(self, rep: "Account") -> "StateBlock":
        """Construct a signed change StateBlock. Work is not added.

        :arg rep: rep account
        :return: a signed change StateBlock
        """
        if not self.sk:
            raise NotImplementedError("This method needs private key")
        self.rep = rep
        b = StateBlock(self, self.rep, self.raw_bal, self.frontier, "0" * 64)
        self.frontier = b.digest()
        self.sign(b)
        return b

    def receive(
        self, digest: str, raw_amt: int, rep: Optional["Account"] = None
    ) -> "StateBlock":
        """Construct a signed receive StateBlock. Work is not added.

        :arg digest: hash digest of the receive block
        :arg raw_amt: raw amount to receive
        :arg rep: Optionally, change rep account
        :return: a signed receive StateBlock
        """
        if not self.sk:
            raise NotImplementedError("This method needs private key")
        assert len(digest) == 64
        if not isinstance(raw_amt, int) or raw_amt <= 0:
            raise AttributeError("Amount must be a positive integer")
        if self.raw_bal + raw_amt >= 1 << 128:
            raise AttributeError("Balance after receive cannot be >= 2^128")
        self.raw_bal += raw_amt
        assert 0 <= self.raw_bal < 1 << 128
        if rep:
            self.rep = rep
        b = StateBlock(self, self.rep, self.raw_bal, self.frontier, digest)
        self.frontier = b.digest()
        self.sign(b)
        return b

    def send(
        self, to: "Account", raw_amt: int, rep: Optional["Account"] = None
    ) -> "StateBlock":
        """Construct a signed send StateBlock. Work is not added.

        :arg to: Destination account
        :arg raw_amt: raw amount to send
        :arg rep: Optionally, change rep account
        :return: a signed send StateBlock
        """
        if not self.sk:
            raise NotImplementedError("This method needs private key")
        if not isinstance(raw_amt, int) or raw_amt <= 0:
            raise AttributeError("Amount must be a positive integer")
        if self.raw_bal - raw_amt < 0:
            raise AttributeError("Balance after send cannot be < 0")
        self.raw_bal -= raw_amt
        assert 0 <= self.raw_bal < 1 << 128
        if rep:
            self.rep = rep
        b = StateBlock(self, self.rep, self.raw_bal, self.frontier, to.pk)
        self.frontier = b.digest()
        self.sign(b)
        return b

    def set_bal(self, bal: str, exp: int = 0) -> None:
        """Set account balance

        :arg bal: account balance
        :arg exp: exponent to convert bal to raw
        """
        self.raw_bal = self.network.to_raw(bal, exp)

    def sign(self, b: "StateBlock") -> None:
        """Sign a block

        :arg b: state block to be signed
        """
        if not self.sk:
            raise NotImplementedError("This method needs private key")
        h = bytes.fromhex(b.digest())
        s = bytes.fromhex(self.sk)
        b.sig = str(ed25519_blake2b.signature(s, h, os.urandom(32)).hex())


@dataclasses.dataclass
class Network:
    """Network

    :arg prefix: prefix for accounts in the network
    :arg difficulty: base difficulty
    :arg send_difficulty: difficulty for send/change blocks
    :arg receive_difficulty: difficulty for receive/open blocks
    :arg exp: exponent to convert between raw and base currency unit
    """

    prefix: str = "nano_"
    difficulty: str = "ffffffc000000000"
    send_difficulty: str = "fffffff800000000"
    receive_difficulty: str = "fffffe0000000000"
    exp: int = 30

    def from_raw(self, val: int, exp: int = 0) -> str:
        """Divide val by 10^exp

        :arg val: val
        :arg exp: positive number
        :return: val divided by 10^exp
        """
        assert isinstance(val, int)
        if exp <= 0:
            exp = self.exp
        nano = _D(val) * _D(_D(10) ** -exp)
        return format(nano.quantize(_D(_D(10) ** -exp)), "." + str(exp) + "f")

    def to_raw(self, val: str, exp: int = 0) -> int:
        """Multiply val by 10^exp

        :arg val: val
        :arg exp: positive number
        :return: val multiplied by 10^exp
        """
        assert isinstance(val, str)
        if exp <= 0:
            exp = self.exp
        return int((_D(val) * _D(_D(10) ** exp)).quantize(_D(1)))

    def from_multiplier(self, multiplier: float) -> str:
        """Get difficulty from multiplier

        :arg multiplier: positive number
        :return: 16 hex-char difficulty
        """
        return format(
            int((int(self.difficulty, 16) - (1 << 64)) / multiplier + (1 << 64)), "016x"
        )

    def to_multiplier(self, difficulty: str) -> float:
        """Get multiplier from difficulty

        :arg difficulty: 16 hex-char difficulty
        :return: multiplier
        """
        return float((1 << 64) - int(self.difficulty, 16)) / float(
            (1 << 64) - int(difficulty, 16)
        )


@dataclasses.dataclass
class StateBlock:
    """State block

    :arg acc: account of the block
    :arg rep: account representative
    :arg bal: account balance
    :arg prev: hash digest of the previous block
    :arg link: block link
    :arg sig: block signature
    :arg work: block work
    """

    acc: Account
    rep: Account
    bal: int
    prev: str
    link: str
    sig: str = ""
    work: str = ""

    def digest(self) -> str:
        """hash digest of block

        :return: 64 hex char hash digest
        """
        return hashlib.blake2b(
            bytes.fromhex(
                "0" * 63
                + "6"
                + self.acc.pk
                + self.prev
                + self.rep.pk
                + format(self.bal, "032x")
                + self.link
            ),
            digest_size=32,
        ).hexdigest()

    def json(self) -> str:
        """block as JSON string

        :return: JSON string
        """
        d = {
            "type": "state",
            "account": self.acc.acc,
            "previous": self.prev,
            "representative": self.rep.acc,
            "balance": self.bal,
            "link": self.link,
            "work": self.work,
            "signature": self.sig,
        }
        return json.dumps(d)

    def verify_signature(self) -> bool:
        """Verify signature for block

        :return: True if valid, False otherwise
        """
        s = bytes.fromhex(self.sig)
        p = bytes.fromhex(self.acc.pk)
        h = bytes.fromhex(self.digest())
        return bool(ed25519_blake2b.checkvalid(s, p, h))

    def work_generate(self, difficulty: str) -> None:
        """Compute work

        :arg difficulty: 16 hex-char difficulty
        """
        assert len(bytes.fromhex(difficulty)) == 8
        self.work = format(
            work.generate(bytes.fromhex(self.prev), int(difficulty, 16)), "016x"
        )

    def work_validate(self, difficulty: str) -> bool:
        """Check whether block has a valid work.

        :arg difficulty: 16 hex-char difficulty
        :arg multiplier: positive number, overrides difficulty
        """
        assert len(bytes.fromhex(difficulty)) == 8
        h = bytes.fromhex(self.prev)
        return bool(work.validate(int(self.work, 16), h, int(difficulty, 16)))
