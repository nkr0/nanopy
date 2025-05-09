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
from typing import ClassVar, Optional, Tuple
from . import ext  # type: ignore

decimal.setcontext(decimal.BasicContext)
decimal.getcontext().traps[decimal.Inexact] = True
decimal.getcontext().traps[decimal.Subnormal] = True
decimal.getcontext().prec = 40


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
        """Derive deterministic private key from mnemonic based on index i.
           Requires `mnemonic <https://pypi.org/project/mnemonic>`_

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


@dataclasses.dataclass
class Network:
    """Network

    :arg name: name of the network
    :arg prefix: prefix for accounts in the network
    :arg difficulty: base difficulty
    :arg send_difficulty: difficulty for send/change blocks
    :arg receive_difficulty: difficulty for receive/open blocks
    :arg exp: exponent to convert between raw and base currency unit
    :arg rpc_url: default RPC url for the network
    :arg std_unit: symbol or label for the default currency unit
    """

    name: str = "nano"
    prefix: str = "nano_"
    difficulty: str = "ffffffc000000000"
    send_difficulty: str = "fffffff800000000"
    receive_difficulty: str = "fffffe0000000000"
    exp: int = 30
    rpc_url: str = "http://localhost:7076"
    std_unit: str = "Ӿ"

    _D: ClassVar[type["decimal.Decimal"]] = decimal.Decimal
    _B32STD: ClassVar[bytes] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
    _B32NANO: ClassVar[bytes] = b"13456789abcdefghijkmnopqrstuwxyz"
    _NANO2STD: ClassVar[bytes] = bytes.maketrans(_B32NANO, _B32STD)
    _STD2NANO: ClassVar[bytes] = bytes.maketrans(_B32STD, _B32NANO)

    def from_multiplier(self, multiplier: float) -> str:
        """Get difficulty from multiplier

        :arg multiplier: positive number
        :return: 16 hex char difficulty
        """
        d = int((int(self.difficulty, 16) - (1 << 64)) / multiplier + (1 << 64))
        return f"{d:016x}"

    def to_multiplier(self, difficulty: str) -> float:
        """Get multiplier from difficulty

        :arg difficulty: 16 hex char difficulty
        :return: multiplier
        """
        if len(difficulty) != 16:
            raise ValueError("Difficulty should be 16 hex char")
        base_d = (1 << 64) - int(self.difficulty, 16)
        d = (1 << 64) - int(difficulty, 16)
        return base_d / d

    def from_pk(self, pk: str) -> str:
        """Get account address from public key

        :arg pk: 64 hex char public key
        """
        if len(pk) != 64:
            raise ValueError("Public key should be 64 hex char")
        p = bytes.fromhex(pk)
        checksum = hashlib.blake2b(p, digest_size=5).digest()
        addr = base64.b32encode(b"000" + p + checksum[::-1])
        addr = addr.translate(self._STD2NANO)[4:]
        return self.prefix + addr.decode()

    def to_pk(self, addr: str) -> str:
        """Get public key from account address

        :arg addr: account address
        """
        if len(addr) != len(self.prefix) + 60:
            raise ValueError(f"Invalid address: {addr}")
        if addr[: len(self.prefix)] != self.prefix:
            raise ValueError(f"Invalid address: {addr}")
        pc = base64.b32decode((b"1111" + addr[-60:].encode()).translate(self._NANO2STD))
        p, checksum = pc[3:-5], pc[:-6:-1]
        if hashlib.blake2b(p, digest_size=5).digest() != checksum:
            raise ValueError(f"Invalid address: {addr}")
        return p.hex()

    def from_raw(self, raw: int, exp: int = 0) -> str:
        """Divide raw by 10^exp

        :arg raw: raw amount
        :arg exp: positive number
        :return: raw divided by 10^exp
        """
        if exp <= 0:
            exp = self.exp
        nano = self._D(raw) * self._D(self._D(10) ** -exp)
        return f"{nano.quantize(self._D(self._D(10) ** -exp)):.{exp}f}"

    def to_raw(self, val: str, exp: int = 0) -> int:
        """Multiply val by 10^exp

        :arg val: val
        :arg exp: positive number
        :return: val multiplied by 10^exp
        """
        if exp <= 0:
            exp = self.exp
        return int((self._D(val) * self._D(self._D(10) ** exp)).quantize(self._D(1)))


NANO = Network()


class Account:
    """Account

    :arg network: network of this account
    """

    def __init__(self, network: "Network" = NANO, addr: str = "") -> None:
        self._frontier = "0" * 64
        self.network = network
        self._pk = self.network.to_pk(addr) if addr else ""
        self._raw_bal = 0
        self._rep = self
        self._sk = ""

    def __repr__(self) -> str:
        return self.addr

    def __bool__(self) -> bool:
        try:
            return self.addr != ""
        except ValueError:
            return False

    @property
    def addr(self) -> str:
        "Account address"
        return self.network.from_pk(self._pk)

    @addr.setter
    def addr(self, addr: str) -> None:
        self._pk = self.network.to_pk(addr)
        self._sk = ""

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
    def frontier(self) -> str:
        "64 hex char account frontier block hash"
        return self._frontier

    @frontier.setter
    def frontier(self, frontier: str) -> None:
        assert len(bytes.fromhex(frontier)) == 32
        self._frontier = frontier

    @property
    def rep(self) -> "Account":
        "Account representative"
        return self._rep

    @rep.setter
    def rep(self, rep: "Account") -> None:
        if not rep:
            raise ValueError("Representative is not initialised")
        self._rep = rep

    @property
    def state(self) -> Tuple[str, int, "Account"]:
        "State of the account (frontier block digest, raw balance, representative)"
        return self.frontier, self.raw_bal, self.rep

    @state.setter
    def state(self, value: Tuple[str, int, "Account"]) -> None:
        self.frontier = value[0]
        self.raw_bal = value[1]
        self.rep = value[2]

    def change_rep(self, rep: "Account", work: str = "") -> "StateBlock":
        """Construct a signed change StateBlock with work

        :arg rep: representative account
        :arg work: 16 hex char work for the block
        :return: a signed change StateBlock
        """
        b = StateBlock(self, rep, self.raw_bal, self.frontier, "0" * 64)
        self._sign(b)
        if work:
            assert len(bytes.fromhex(work)) == 8
            b.work = work
        else:
            b.work_generate(self.network.send_difficulty)
        self.rep = rep
        self.frontier = b.digest
        return b

    def receive(
        self, digest: str, raw_amt: int, rep: Optional["Account"] = None, work: str = ""
    ) -> "StateBlock":
        """Construct a signed receive StateBlock with work

        :arg digest: 64 hex char hash digest of the receive block
        :arg raw_amt: raw amount to receive
        :arg rep: representative account
        :arg work: 16 hex char work for the block
        :return: a signed receive StateBlock
        """
        assert len(bytes.fromhex(digest)) == 32
        if raw_amt <= 0:
            raise ValueError("Amount must be a positive integer")
        final_raw_bal = self.raw_bal + raw_amt
        if final_raw_bal >= 1 << 128:
            raise ValueError("raw balance after receive cannot be >= 2^128")
        brep = rep if rep else self.rep
        b = StateBlock(self, brep, final_raw_bal, self.frontier, digest)
        self._sign(b)
        if work:
            assert len(bytes.fromhex(work)) == 8
            b.work = work
        else:
            b.work_generate(self.network.receive_difficulty)
        if rep:
            self.rep = rep
        self.raw_bal = final_raw_bal
        self.frontier = b.digest
        return b

    def send(
        self,
        to: "Account",
        raw_amt: int,
        rep: Optional["Account"] = None,
        work: str = "",
    ) -> "StateBlock":
        """Construct a signed send StateBlock with work

        :arg to: Destination account
        :arg raw_amt: raw amount to send
        :arg rep: representative account
        :arg work: 16 hex char work for the block
        :return: a signed send StateBlock
        """
        if not isinstance(raw_amt, int) or raw_amt <= 0:
            raise ValueError("Amount must be a positive integer")
        final_raw_bal = self.raw_bal - raw_amt
        if final_raw_bal < 0:
            raise ValueError("raw balance after send cannot be < 0")
        brep = rep if rep else self.rep
        b = StateBlock(self, brep, final_raw_bal, self.frontier, to.pk)
        self._sign(b)
        if work:
            assert len(bytes.fromhex(work)) == 8
            b.work = work
        else:
            b.work_generate(self.network.send_difficulty)
        if rep:
            self.rep = rep
        self.raw_bal = final_raw_bal
        self.frontier = b.digest
        return b

    def _sign(self, b: "StateBlock") -> None:
        """Sign a block

        :arg b: state block to be signed
        """
        if not self._sk:
            raise NotImplementedError("This method needs private key")
        h = bytes.fromhex(b.digest)
        s = bytes.fromhex(self._sk)
        b.sig = str(ext.sign(s, h, os.urandom(32)).hex())


@dataclasses.dataclass
class StateBlock:
    """State block

    :arg acc: account of the block
    :arg rep: account representative
    :arg bal: account balance
    :arg prev: 64 hex char hash digest of the previous block
    :arg link: 64 hex char block link
    :arg sig: 128 hex char block signature
    :arg work: 16 hex char block work
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
        h = f"{'0' * 63}6{self.acc.pk}{self.prev}{self.rep.pk}{self.bal:032x}{self.link}"
        return hashlib.blake2b(bytes.fromhex(h), digest_size=32).hexdigest()

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
        w = ext.work_generate(bytes.fromhex(self.prev), int(difficulty, 16))
        self.work = f"{w:016x}"

    def work_validate(self, difficulty: str) -> bool:
        """Check whether block has a valid work.

        :arg difficulty: 16 hex char difficulty
        :arg multiplier: positive number, overrides difficulty
        """
        assert len(bytes.fromhex(difficulty)) == 8
        h = bytes.fromhex(self.prev)
        return bool(ext.work_validate(int(self.work, 16), h, int(difficulty, 16)))
