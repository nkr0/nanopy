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
from typing import Optional, Tuple
from . import ext  # type: ignore

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

    :arg seed: 64 hex char seed
    :arg i: index number, 0 to 2^32 - 1
    :return: 64 hex char private key
    """
    assert len(bytes.fromhex(seed)) == 32
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
        :return: 64 hex char private key
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
    """

    def __init__(self, network: "Network", addr: str = "") -> None:
        self.frontier = "0" * 64
        self.network = network
        self._pk = self.network.to_pk(addr) if addr else ""
        self._raw_bal = 0
        self.rep = self
        self._sk = ""

    def __repr__(self) -> str:
        return self.addr

    @property
    def addr(self) -> str:
        "Account address"
        return self.network.from_pk(self._pk)

    @property
    def pk(self) -> str:
        "64 hex char account public key"
        return self._pk

    @pk.setter
    def pk(self, key: str) -> None:
        assert len(bytes.fromhex(key)) == 32
        self._pk = key
        self._sk = ""

    @property
    def sk(self) -> str:
        "64 hex char account secret/private key"
        return self._sk

    @sk.setter
    def sk(self, key: str) -> None:
        assert len(bytes.fromhex(key)) == 32
        self._pk = ext.publickey(bytes.fromhex(key)).hex()
        self._sk = key

    @property
    def bal(self) -> str:
        "Account balance"
        return self.network.from_raw(self.raw_bal)

    @bal.setter
    def bal(self, val: str) -> None:
        self.raw_bal = self.network.to_raw(val)

    @property
    def raw_bal(self) -> int:
        "Account raw balance"
        return self._raw_bal

    @raw_bal.setter
    def raw_bal(self, val: int) -> None:
        if val < 0:
            raise ValueError("Balance cannot be < 0")
        if val >= 1 << 128:
            raise ValueError("Balance cannot be >= 2^128")
        self._raw_bal = val

    @property
    def state(self) -> Tuple[str, int, "Account"]:
        "State of the account (frontier block digest, raw balance, representative)"
        return self.frontier, self.raw_bal, self.rep

    @state.setter
    def state(self, value: Tuple[str, int, "Account"]) -> None:
        assert len(bytes.fromhex(value[0])) == 32
        self.frontier = value[0]
        self.raw_bal = value[1]
        self.rep = value[2]

    def change_rep(self, rep: "Account") -> "StateBlock":
        """Construct a signed change StateBlock. Work is not added.

        :arg rep: representative account
        :return: a signed change StateBlock
        """
        b = StateBlock(self, rep, self.raw_bal, self.frontier, "0" * 64)
        self.sign(b)
        self.rep = rep
        self.frontier = b.digest
        return b

    def receive(
        self, digest: str, raw_amt: int, rep: Optional["Account"] = None
    ) -> "StateBlock":
        """Construct a signed receive StateBlock. Work is not added.

        :arg digest: 64 hex char hash digest of the receive block
        :arg raw_amt: raw amount to receive
        :arg rep: Optionally, change representative account
        :return: a signed receive StateBlock
        """
        assert len(bytes.fromhex(digest)) == 32
        if raw_amt <= 0:
            raise AttributeError("Amount must be a positive integer")
        final_raw_bal = self.raw_bal + raw_amt
        if final_raw_bal >= 1 << 128:
            raise AttributeError("raw balance after receive cannot be >= 2^128")
        brep = rep if rep else self.rep
        b = StateBlock(self, brep, final_raw_bal, self.frontier, digest)
        self.sign(b)
        if rep:
            self.rep = rep
        self.raw_bal = final_raw_bal
        self.frontier = b.digest
        return b

    def send(
        self, to: "Account", raw_amt: int, rep: Optional["Account"] = None
    ) -> "StateBlock":
        """Construct a signed send StateBlock. Work is not added.

        :arg to: Destination account
        :arg raw_amt: raw amount to send
        :arg rep: Optionally, change representative account
        :return: a signed send StateBlock
        """
        if not isinstance(raw_amt, int) or raw_amt <= 0:
            raise AttributeError("Amount must be a positive integer")
        final_raw_bal = self.raw_bal - raw_amt
        if final_raw_bal < 0:
            raise AttributeError("raw balance after send cannot be < 0")
        brep = rep if rep else self.rep
        b = StateBlock(self, brep, final_raw_bal, self.frontier, to.pk)
        self.sign(b)
        if rep:
            self.rep = rep
        self.raw_bal = final_raw_bal
        self.frontier = b.digest
        return b

    def sign(self, b: "StateBlock") -> None:
        """Sign a block

        :arg b: state block to be signed
        """
        if not self._sk:
            raise NotImplementedError("This method needs private key")
        h = bytes.fromhex(b.digest)
        s = bytes.fromhex(self._sk)
        b.sig = str(ext.sign(s, h, os.urandom(32)).hex())


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

    def from_multiplier(self, multiplier: float) -> str:
        """Get difficulty from multiplier

        :arg multiplier: positive number
        :return: 16 hex char difficulty
        """
        return format(
            int((int(self.difficulty, 16) - (1 << 64)) / multiplier + (1 << 64)), "016x"
        )

    def to_multiplier(self, difficulty: str) -> float:
        """Get multiplier from difficulty

        :arg difficulty: 16 hex char difficulty
        :return: multiplier
        """
        if len(difficulty) != 16:
            raise ValueError("Difficulty should be 16 hex char")
        return float((1 << 64) - int(self.difficulty, 16)) / float(
            (1 << 64) - int(difficulty, 16)
        )

    def from_pk(self, pk: str) -> str:
        """Get account address from public key

        :arg pk: 64 hex char public key
        """
        if len(pk) != 64:
            raise ValueError("Public key should be 64 hex char")
        p = bytes.fromhex(pk)
        checksum = hashlib.blake2b(p, digest_size=5).digest()
        p = b"\x00\x00\x00" + p + checksum[::-1]
        addr = base64.b32encode(p)
        addr = addr.translate(B322NANO)[4:]
        return self.prefix + addr.decode()

    def to_pk(self, addr: str) -> str:
        """Get public key from account address

        :arg addr: account address
        """
        if len(addr) != len(self.prefix) + 60:
            raise ValueError("Invalid address:", addr)
        if addr[: len(self.prefix)] != self.prefix:
            raise ValueError("Invalid address:", addr)
        p = base64.b32decode((b"1111" + addr[-60:].encode()).translate(NANO2B32))
        checksum = p[:-6:-1]
        p = p[3:-5]
        if hashlib.blake2b(p, digest_size=5).digest() != checksum:
            raise ValueError("Invalid address:", addr)
        return p.hex()

    def from_raw(self, raw: int, exp: int = 0) -> str:
        """Divide raw by 10^exp

        :arg raw: raw amount
        :arg exp: positive number
        :return: raw divided by 10^exp
        """
        if exp <= 0:
            exp = self.exp
        nano = _D(raw) * _D(_D(10) ** -exp)
        return format(nano.quantize(_D(_D(10) ** -exp)), "." + str(exp) + "f")

    def to_raw(self, val: str, exp: int = 0) -> int:
        """Multiply val by 10^exp

        :arg val: val
        :arg exp: positive number
        :return: val multiplied by 10^exp
        """
        if exp <= 0:
            exp = self.exp
        return int((_D(val) * _D(_D(10) ** exp)).quantize(_D(1)))


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

    @property
    def digest(self) -> str:
        "64 hex char hash digest of block"
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

    @property
    def json(self) -> str:
        "block as JSON string"
        d = {
            "type": "state",
            "account": self.acc.addr,
            "previous": self.prev,
            "representative": self.rep.addr,
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
        h = bytes.fromhex(self.digest)
        return bool(ext.verify_signature(s, p, h))

    def work_generate(self, difficulty: str) -> None:
        """Compute work

        :arg difficulty: 16 hex char difficulty
        """
        assert len(bytes.fromhex(difficulty)) == 8
        self.work = format(
            ext.work_generate(bytes.fromhex(self.prev), int(difficulty, 16)), "016x"
        )

    def work_validate(self, difficulty: str) -> bool:
        """Check whether block has a valid work.

        :arg difficulty: 16 hex char difficulty
        :arg multiplier: positive number, overrides difficulty
        """
        assert len(bytes.fromhex(difficulty)) == 8
        h = bytes.fromhex(self.prev)
        return bool(ext.work_validate(int(self.work, 16), h, int(difficulty, 16)))
