# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,too-many-statements
import os
import sys
import unittest
from contextlib import contextmanager
from io import StringIO
from typing import Iterator
from unittest.mock import Mock, call, patch

import nanopy as npy
from nanopy import cli

Z64 = "0" * 64
O64 = "1" * 64
R64 = os.urandom(32).hex()
ZR = "        0.000000000000000000000000000000 Ӿ"
OR = "        0.000000000000000000000000000001 Ӿ"
TR = "        0.000000000000000000000000000002 Ӿ"
ZEROR = "0.000000000000000000000000000000"
ONER = "0.000000000000000000000000000001"
PACC0 = "nano_1111111111111111111111111111111111111111111111111111hifc8npp"
PACC1 = "nano_16aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46ajbtsyew7c"
SACC0 = "nano_18gmu6engqhgtjnppqam181o5nfhj4sdtgyhy36dan3jr9spt84rzwmktafc"
ZACC0 = "nano_3i1aq1cchnmbn9x5rsbap8b15akfh7wj7pwskuzi7ahz8oq6cobd99d4r3b7"
ZACC1 = "nano_3rrf6cus8pye6o1kzi5n6wwjof8bjb7ff4xcgesi3njxid6x64pms6onw1f9"


@contextmanager
def captured_output() -> Iterator[StringIO]:
    try:
        sys.stdout = StringIO()
        yield sys.stdout
    finally:
        sys.stdout = sys.__stdout__


class TestSession(unittest.TestCase):
    s = cli.Session(Mock())

    def test_check_status(self) -> None:
        self.s.check_status([])

        with captured_output() as out:
            r = {
                "balances": {
                    PACC0: {
                        "balance": "1",
                        "receivable": "0",
                    },
                }
            }
            with patch.object(self.s.rpc, "accounts_balances", return_value=r):
                self.s.check_status([PACC0])
            assert (
                out.getvalue()  # pylint: disable=no-member
                == f"Acc : {PACC0}\nBal : {OR}\n"
            )

        with captured_output() as out:
            r = {
                "balances": {
                    PACC0: {
                        "balance": "1",
                        "receivable": "2",
                    },
                }
            }
            with patch.object(self.s.rpc, "accounts_balances", return_value=r):
                self.s.check_status([PACC0])
            assert (
                out.getvalue()  # pylint: disable=no-member
                == f"Acc : {PACC0}\nBal : {OR}\nRec : {TR}\n"
            )

        with captured_output() as out:
            r = {
                "balances": {
                    PACC0: {
                        "balance": "1",
                        "receivable": "0",
                    },
                    PACC1: {
                        "balance": "2",
                        "receivable": "1",
                    },
                }
            }
            with patch.object(self.s.rpc, "accounts_balances", return_value=r):
                self.s.check_status([PACC0, PACC1])
            assert out.getvalue() == (  # pylint: disable=no-member
                f"Acc : {PACC0}\n"
                f"Bal : {OR}\n"
                f"Acc : {PACC1}\n"
                f"Bal : {TR}\n"
                f"Rec : {OR}\n"
            )

    @patch("pykeepass.PyKeePass")
    @patch("getpass.getpass")
    @patch("os.urandom")
    def test_create_new_key(
        self, mock_urandom: Mock, mock_getpass: Mock, mock_kp: Mock
    ) -> None:
        mock_urandom.return_value = bytes.fromhex(Z64)
        with captured_output() as out:
            self.s.create_new_key("f", "k")
            assert out.getvalue() == f"k {ZACC0}\n"  # pylint: disable=no-member
        mock_urandom.assert_called_once_with(32)
        mock_getpass.assert_called_once()
        mock_kp.assert_called_once_with("f", password=mock_getpass.return_value)
        mock_kp.return_value.add_entry.assert_called_once_with(
            mock_kp.return_value.root_group, "k", ZACC0, Z64
        )
        mock_kp.return_value.save.assert_called_once()

        with captured_output() as out:
            self.s.create_new_key("f", "k", "g")
            assert out.getvalue() == f"k {ZACC0}\n"  # pylint: disable=no-member
        mock_urandom.assert_called_with(32)
        mock_kp.assert_called_with("f", password=mock_getpass.return_value)
        mock_kp.return_value.find_groups.assert_called_once_with(name="g", first=True)
        mock_kp.return_value.add_entry.assert_called_with(
            mock_kp.return_value.find_groups(), "k", ZACC0, Z64
        )
        mock_kp.return_value.save.assert_called()

    @patch("pykeepass.PyKeePass")
    @patch("getpass.getpass")
    def test_get_key(self, mock_getpass: Mock, mock_kp: Mock) -> None:
        mock_kp.return_value.find_entries().password = "p"
        with self.assertRaisesRegex(ValueError, "Failed to retrieve key"):
            self.s.get_key("f", "k")
        mock_getpass.assert_called_once()
        mock_kp.assert_called_once_with("f", password=mock_getpass.return_value)
        mock_kp.return_value.find_entries.assert_called_with(
            title="k",
            group=mock_kp.return_value.root_group,
            recursive=False,
            first=True,
        )

        mock_kp.return_value.find_entries().password = "1234"
        with self.assertRaisesRegex(ValueError, "Failed to retrieve key"):
            self.s.get_key("f", "k")
        mock_getpass.assert_called()
        mock_kp.assert_called_with("f", password=mock_getpass.return_value)
        mock_kp.return_value.find_entries.assert_called_with(
            title="k",
            group=mock_kp.return_value.root_group,
            recursive=False,
            first=True,
        )

        mock_kp.return_value.find_entries().password = R64
        assert self.s.get_key("f", "k") == R64
        mock_getpass.assert_called()
        mock_kp.assert_called_with("f", password=mock_getpass.return_value)
        mock_kp.return_value.find_entries.assert_called_with(
            title="k",
            group=mock_kp.return_value.root_group,
            recursive=False,
            first=True,
        )

        assert self.s.get_key("f", "k", "g") == R64
        mock_getpass.assert_called()
        mock_kp.assert_called_with("f", password=mock_getpass.return_value)
        mock_kp.return_value.find_groups.assert_called_once_with(name="g", first=True)
        mock_kp.return_value.find_entries.assert_called_with(
            title="k",
            group=mock_kp.return_value.find_groups(),
            recursive=False,
            first=True,
        )

    def test_get_addresses(self) -> None:
        assert self.s.get_addresses(Z64) == [ZACC0]
        assert self.s.get_addresses(Z64, 1) == [ZACC0, ZACC1]

    def test_get_account_info(self) -> None:
        acc = npy.Account(addr=PACC0)
        with captured_output() as out:
            with patch.object(self.s.rpc, "account_info"):
                self.s.get_account_info(acc)
            assert (
                out.getvalue()  # pylint: disable=no-member
                == f"Acc : {PACC0}\nBal : {ZR}\nRep : {PACC0}\n"
            )

        r = {"balance": "1", "frontier": R64, "representative": PACC0}
        with captured_output() as out:
            with patch.object(self.s.rpc, "account_info", return_value=r):
                self.s.get_account_info(acc)
            assert (
                out.getvalue()  # pylint: disable=no-member
                == f"Acc : {PACC0}\nBal : {OR}\nRep : {PACC0}\n"
            )
        assert acc.frontier == R64
        assert acc.raw_bal == 1
        assert acc.rep == PACC0

    def test_change_rep(self) -> None:
        acc = npy.Account(sk=Z64)
        acc.network.send_difficulty = acc.network.receive_difficulty
        with captured_output() as out:
            b = self.s.change_rep(acc, npy.Account(PACC1))
            assert out.getvalue() == f"Rep : {PACC1}\n"  # pylint: disable=no-member
        assert acc.rep == PACC1
        assert b.acc == SACC0
        assert b.rep == PACC1
        assert b.bal == 0
        assert b.prev == Z64
        assert b.link == Z64
        assert len(bytes.fromhex(b.sig)) == 64
        assert len(bytes.fromhex(b.work)) == 8
        acc.network = npy.Network()

    def test_receive(self) -> None:
        acc = npy.Account(sk=Z64)
        r = {"amount": "1", "block_account": PACC0}
        with captured_output() as out:
            with patch.object(self.s.rpc, "block_info", return_value=r):
                b0 = self.s.receive(acc, O64)
                b1 = self.s.receive(acc, R64, npy.Account(PACC1))
            assert (
                out.getvalue()  # pylint: disable=no-member
                == f"From: {PACC0}\nAmt : {OR}\nFrom: {PACC0}\nAmt : {OR}\nRep : {PACC1}\n"
            )
        assert acc.raw_bal == 2
        assert acc.frontier == b1.digest
        assert b1.acc == SACC0
        assert b1.rep == PACC1
        assert b1.bal == 2
        assert b1.prev == b0.digest
        assert b1.link == R64
        assert len(bytes.fromhex(b1.sig)) == 64
        assert len(bytes.fromhex(b1.work)) == 8

    def test_send(self) -> None:
        acc = npy.Account(sk=Z64)
        acc.network.send_difficulty = acc.network.receive_difficulty
        acc.raw_bal = 2
        with captured_output() as out:
            b0 = self.s.send(acc, npy.Account(PACC1), ONER)
            b1 = self.s.send(acc, npy.Account(PACC1), ONER, npy.Account(PACC0))
            assert (
                out.getvalue()  # pylint: disable=no-member
                == f"To  : {PACC1}\nAmt : {OR}\nTo  : {PACC1}\nAmt : {OR}\nRep : {PACC0}\n"
            )
        assert acc.raw_bal == 0
        assert acc.frontier == b1.digest
        assert b1.acc == SACC0
        assert b1.rep == PACC0
        assert b1.bal == 0
        assert b1.prev == b0.digest
        assert b1.link == O64
        assert len(bytes.fromhex(b1.sig)) == 64
        assert len(bytes.fromhex(b1.work)) == 8
        acc.network = npy.Network()


class TestModuleLevel(unittest.TestCase):
    @patch("nanopy.cli.Session")
    @patch("configparser.ConfigParser")
    @patch.object(sys, "argv", [])
    def test_main(self, mock_cp: Mock, mock_session: Mock) -> None:
        mock_cp.return_value.options.return_value = ["x", PACC0, PACC1]
        s = mock_session.return_value
        s.get_key.return_value = Z64
        s.get_addresses.side_effect = [[ZACC0], [ZACC0, ZACC1]]
        s.rpc.receivable.return_value = {"blocks": [Z64, R64]}

        with captured_output():
            sys.argv = ["nanopy"]
            cli.main()

            sys.argv = ["nanopy", "open", "f", "k"]
            cli.main()

            sys.argv = ["nanopy", "open", "f", "k", "-g", "g"]
            cli.main()

            sys.argv = ["nanopy", "open", "f", "k", "-n"]
            cli.main()

            sys.argv = ["nanopy", "open", "f", "k", "-g", "g", "-n"]
            cli.main()

            sys.argv = ["nanopy", "open", "f", "k", "--audit"]
            cli.main()

            sys.argv = ["nanopy", "open", "f", "k", "--audit", "-i", "1"]
            cli.main()

            sys.argv = ["nanopy", "open", "f", "k", "-s", PACC0, "-a", ONER]
            cli.main()

            sys.argv = ["nanopy", "open", "f", "k", "-s", PACC0, "-e", "--rep", PACC1]
            cli.main()

            sys.argv = ["nanopy", "open", "f", "k", "-r", R64]
            cli.main()

            sys.argv = ["nanopy", "open", "f", "k", "-R"]
            cli.main()

            sys.argv = ["nanopy", "open", "f", "k", "--rep", PACC0]
            cli.main()

        assert s.check_status.call_args_list == [
            call([PACC0, PACC1]),
            call([ZACC0]),
            call([ZACC0, ZACC1]),
        ]
        assert (
            s.get_key.call_args_list
            == [call("f", "k", None), call("f", "k", "g")] + [call("f", "k", None)] * 7
        )
        assert s.get_account_info.call_args_list == [call(ZACC0)] * 7
        assert s.create_new_key.call_args_list == [
            call("f", "k", None),
            call("f", "k", "g"),
        ]
        assert s.send.call_args_list == [
            call(ZACC0, PACC0, ONER, None),
            call(ZACC0, PACC0, ZEROR, PACC1),
        ]
        assert s.receive.call_args_list == [
            call(ZACC0, R64, None),
            call(ZACC0, Z64, None),
            call(ZACC0, R64, None),
        ]
        assert s.change_rep.call_args_list == [call(ZACC0, PACC0)]
