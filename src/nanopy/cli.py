# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
import argparse
import configparser
import getpass
import os
from typing import Callable

import platformdirs
import pykeepass  # type: ignore

from . import Account, StateBlock, deterministic_key
from .rpc import HTTP


class Session:

    def __init__(self, rpc: "HTTP"):
        self.rpc = rpc

    def check_status(self, accounts: list[str]) -> None:
        if not accounts:
            return
        n = Account.network
        info = self.rpc.accounts_balances(accounts)
        for account in accounts:
            accinfo = info["balances"][account]
            print(f"Acc : {account}")
            print(f"Bal : {n.from_raw(int(accinfo['balance'])):>40} {n.std_unit}")
            if int(accinfo["receivable"]) > 0:
                print(
                    f"Rec : {n.from_raw(int(accinfo['receivable'])):>40} {n.std_unit}"
                )

    def create_new_key(self, f: str, k: str, g: str = "") -> None:
        acc = Account()
        seed = os.urandom(32).hex()
        acc.sk = deterministic_key(seed, 0)
        kp = pykeepass.PyKeePass(f, password=getpass.getpass())
        g = kp.find_groups(name=g, first=True) if g else kp.root_group
        kp.add_entry(g, k, acc.addr, seed)
        kp.save()
        print(f"{k} {acc}")

    def get_key(self, f: str, k: str, g: str = "") -> str:
        kp = pykeepass.PyKeePass(f, password=getpass.getpass())
        g = kp.find_groups(name=g, first=True) if g else kp.root_group
        entry = kp.find_entries(title=k, group=g, recursive=False, first=True)
        seed = entry.password  # pylint: disable=no-member
        try:
            assert len(bytes.fromhex(seed)) == 32
        except Exception as e:
            raise ValueError("Failed to retrieve key") from e
        return str(seed)

    def get_addresses(self, seed: str, index: int = 0) -> list[str]:
        a = Account()
        addresses = []
        for i in range(index + 1):
            a.sk = deterministic_key(seed, i)
            addresses.append(a.addr)
        return addresses

    def get_account_info(self, acc: Account) -> None:
        info = self.rpc.account_info(acc.addr, representative=True)
        if "frontier" in info:
            acc.state = (
                info["frontier"],
                int(info["balance"]),
                Account(addr=info["representative"]),
            )
        print(f"Acc : {acc}")
        print(f"Bal : {acc.bal:>40} {acc.network.std_unit}")
        print(f"Rep : {acc.rep}")

    def change_rep(self, acc: Account, rep: Account) -> StateBlock:
        print(f"Rep : {rep}")
        return acc.change_rep(rep)

    def receive(
        self, acc: Account, hash_: str, rep: Account | None = None
    ) -> StateBlock:
        info = self.rpc.block_info(hash_)
        raw_amt = int(info["amount"])
        print(f"From: {info['block_account']}")
        print(f"Amt : {acc.network.from_raw(raw_amt):>40} {acc.network.std_unit}")
        if rep:
            print(f"Rep : {rep}")
        return acc.receive(hash_, raw_amt, rep)

    def send(
        self, acc: Account, to: Account, amt: str, rep: Account | None = None
    ) -> StateBlock:
        raw_amt = acc.network.to_raw(amt)
        print(f"To  : {to}")
        print(f"Amt : {acc.network.from_raw(raw_amt):>40} {acc.network.std_unit}")
        if rep:
            print(f"Rep : {rep}")
        return acc.send(to, raw_amt, rep)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--network",
        choices=["banano", "beta", "nano"],
        default="nano",
        help="Choose the network to interact with. (nano)",
        type=str,
    )

    subparsers = parser.add_subparsers(dest="sub")
    o = subparsers.add_parser("open", help="Open KDBX file")
    o.add_argument("f", metavar="FILE", type=str, help="*.kdbx file.")
    o.add_argument("k", metavar="KEY", help="Key label.")
    o.add_argument("-g", "--group", help="Key group. (root)", type=str)
    o.add_argument("-i", "--index", default=0, help="Account index. (0)", type=int)
    o.add_argument("--rep", help="Change rep", metavar="ADDRESS", type=Account)

    ox = o.add_mutually_exclusive_group()
    ox.add_argument("--audit", action="store_true", help="Audit key")
    ox.add_argument("-n", "--new", action="store_true", help="Add a new key.")
    ox.add_argument("-r", "--receive", help="Receive block", metavar="HASH", type=str)
    ox.add_argument(
        "-R", "--receive-all", action="store_true", help="Receive all pending blocks."
    )
    ox.add_argument("-s", "--send", help="Send to", metavar="ADDRESS", type=Account)

    sx = o.add_mutually_exclusive_group()
    sx.add_argument("-a", "--amount", type=str, help="Amount to send")
    sx.add_argument("-e", "--empty", action="store_true", help="Empty account")
    args = parser.parse_args()

    config = configparser.ConfigParser(allow_no_value=True)
    config.read(platformdirs.user_config_dir("nanopy.ini"))

    Account.set_network(name=args.network)
    n = Account.network
    s = Session(HTTP(url=str(config[n.name].get("rpc", fallback=n.rpc_url))))

    receivable: Callable[[Account], list[str]] = lambda acc: s.rpc.receivable(str(acc))[
        "blocks"
    ]
    process: Callable[[StateBlock], str] = lambda b: s.rpc.process(b.dict_)["hash"]

    if not args.sub:
        s.check_status([a for a in config.options(n.name) if a.startswith(n.prefix)])
        return

    if args.new:
        s.create_new_key(args.f, args.k, args.group)
        return

    seed = s.get_key(args.f, args.k, args.group)

    if args.audit:
        s.check_status(s.get_addresses(seed, args.index))
        return

    acc = Account(sk=deterministic_key(seed, args.index))
    s.get_account_info(acc)
    if args.send:
        if args.empty:
            print(process(s.send(acc, args.send, acc.bal, args.rep)))
        elif args.amount:
            print(process(s.send(acc, args.send, args.amount, args.rep)))
    elif args.receive:
        print(process(s.receive(acc, args.receive, args.rep)))
    elif args.receive_all:
        for r in receivable(acc):
            print(process(s.receive(acc, r, args.rep)))
    elif args.rep:
        print(process(s.change_rep(acc, args.rep)))


if __name__ == "__main__":  # pragma: no cover
    main()
