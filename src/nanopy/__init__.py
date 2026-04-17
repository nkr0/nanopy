"""
nanopy
######
"""

import base64
import dataclasses
import decimal
import hashlib
import hmac
import json
import os
from typing import Optional

import mnemonic

from . import ext  # type: ignore

decimal.getcontext().prec = 40


def deterministic_key(seed: str, i: int = 0) -> str:
    """Derive deterministic private key from seed based on index i

    :arg seed: 64 hex char seed
    :arg i: index number, [0, 2^32)
    :return: 64 hex char private key
    """
    assert len(bytes.fromhex(seed)) == 32
    assert 0 <= i < 1 << 32
    return hashlib.blake2b(
        bytes.fromhex(seed) + i.to_bytes(4, byteorder="big"), digest_size=32
    ).hexdigest()


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


@dataclasses.dataclass
class Network:  # pylint: disable=too-many-instance-attributes
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
        b32std = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
        b32nano = b"13456789abcdefghijkmnopqrstuwxyz"
        std2nano = bytes.maketrans(b32std, b32nano)
        addr = addr.translate(std2nano)[4:]
        return self.prefix + addr.decode()

    def to_pk(self, addr: str) -> str:
        """Get public key from account address

        :arg addr: account address
        """
        if len(addr) != len(self.prefix) + 60:
            raise ValueError(f"Invalid address: {addr}")
        if addr[: len(self.prefix)] != self.prefix:
            raise ValueError(f"Invalid address: {addr}")
        b32std = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
        b32nano = b"13456789abcdefghijkmnopqrstuwxyz"
        nano2std = bytes.maketrans(b32nano, b32std)
        pc = base64.b32decode((b"1111" + addr[-60:].encode()).translate(nano2std))
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
        d: type["decimal.Decimal"] = decimal.Decimal
        nano = d(raw) * d(d(10) ** -exp)
        return f"{nano.quantize(d(d(10) ** -exp)):.{exp}f}"

    def to_raw(self, val: str, exp: int = 0) -> int:
        """Multiply val by 10^exp

        :arg val: val
        :arg exp: positive number
        :return: val multiplied by 10^exp
        """
        if exp <= 0:
            exp = self.exp
        d: type["decimal.Decimal"] = decimal.Decimal
        return int((d(val) * d(d(10) ** exp)).quantize(d(1)))


class Account:  # pylint: disable=too-many-instance-attributes
    """Account

    :arg addr: address of this account
    :arg pk: public key of this account (overrides addr)
    :arg sk: secret key of this account (overrides addr and pk)
    """

    network = Network()

    def __init__(self, addr: str = "", pk: str = "", sk: str = "") -> None:
        self._frontier = "0" * 64
        self._pk = self.network.to_pk(addr) if addr else ""
        if pk:
            self.pk = pk
        self._raw_bal = 0
        self._rep = self
        self._sk = ""
        if sk:
            self.sk = sk

    def __repr__(self) -> str:
        return self.addr

    def __bool__(self) -> bool:
        return bool(self._pk)

    def __eq__(self, other: object) -> bool:
        return str(other) == str(self)

    @classmethod
    def set_network(cls, network: Network | None = None, name: str = "nano") -> None:
        """Set the network for all accounts

        :arg network: Generic Network
        :arg name: Network name. One of banano, beta, nano
        """
        cls.network = network if network else Network()
        if name == "banano":
            cls.network.name = "banano"
            cls.network.prefix = "ban_"
            cls.network.send_difficulty = "fffffe0000000000"
            cls.network.exp = 29
            cls.network.rpc_url = "http://localhost:7072"
            cls.network.std_unit = "BAN"
        elif name == "beta":
            cls.network.name = "beta"
            cls.network.prefix = "xrb_"
            cls.network.rpc_url = "http://localhost:55000"
            cls.network.std_unit = "β"

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
        "Account raw balance [0, 2^128)"
        return self._raw_bal

    @raw_bal.setter
    def raw_bal(self, val: int) -> None:
        if not 0 <= val < 1 << 128:
            raise ValueError("Balance must be within [0, 2^128)")
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
    def state(self) -> tuple[str, int, "Account"]:
        "State of the account (frontier block hash, raw balance, representative)"
        return self.frontier, self.raw_bal, self.rep

    @state.setter
    def state(self, value: tuple[str, int, "Account"]) -> None:
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
        self.frontier = b.hash_
        self.rep = b.rep
        return b

    def receive(
        self, hash_: str, raw_amt: int, rep: Optional["Account"] = None, work: str = ""
    ) -> "StateBlock":
        """Construct a signed receive StateBlock with work

        :arg hash_: 64 hex char receive block hash
        :arg raw_amt: raw amount to receive
        :arg rep: representative account
        :arg work: 16 hex char work for the block
        :return: a signed receive StateBlock
        """
        assert len(bytes.fromhex(hash_)) == 32
        if raw_amt <= 0:
            raise ValueError("Amount must be a positive integer")
        final_raw_bal = self.raw_bal + raw_amt
        if final_raw_bal >= 1 << 128:
            raise ValueError("Raw balance after receive cannot be >= 2^128")
        brep = rep if rep else self.rep
        b = StateBlock(self, brep, final_raw_bal, self.frontier, hash_)
        self._sign(b)
        if work:
            assert len(bytes.fromhex(work)) == 8
            b.work = work
        else:
            b.work_generate(self.network.receive_difficulty)
        self.frontier = b.hash_
        self.raw_bal = b.bal
        self.rep = b.rep
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
            raise ValueError("Raw balance after send cannot be < 0")
        brep = rep if rep else self.rep
        b = StateBlock(self, brep, final_raw_bal, self.frontier, to.pk)
        self._sign(b)
        if work:
            assert len(bytes.fromhex(work)) == 8
            b.work = work
        else:
            b.work_generate(self.network.send_difficulty)
        self.frontier = b.hash_
        self.raw_bal = b.bal
        self.rep = b.rep
        return b

    def _sign(self, b: "StateBlock") -> None:
        """Sign a block

        :arg b: state block to be signed
        """
        if not self._sk:
            raise NotImplementedError("This method needs private key")
        h = bytes.fromhex(b.hash_)
        s = bytes.fromhex(self._sk)
        b.sig = str(ext.sign(s, h, os.urandom(32)).hex())


@dataclasses.dataclass
class StateBlock:
    """State block

    :arg acc: account of the block
    :arg rep: account representative
    :arg bal: account raw balance
    :arg prev: 64 hex char previous block hash
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
    def hash_(self) -> str:
        "64 hex char block hash"
        h = f"{'0' * 63}6{self.acc.pk}{self.prev}{self.rep.pk}{self.bal:032x}{self.link}"
        return hashlib.blake2b(bytes.fromhex(h), digest_size=32).hexdigest()

    @property
    def dict_(self) -> dict[str, str]:
        "block as dict"
        return {
            "type": "state",
            "account": self.acc.addr,
            "previous": self.prev,
            "representative": self.rep.addr,
            "balance": str(self.bal),
            "link": self.link,
            "work": self.work,
            "signature": self.sig,
        }

    def verify_signature(self) -> bool:
        """Verify signature for block

        :return: True if valid, False otherwise
        """
        s = bytes.fromhex(self.sig)
        p = bytes.fromhex(self.acc.pk)
        h = bytes.fromhex(self.hash_)
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
