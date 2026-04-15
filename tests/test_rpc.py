# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
import copy
import inspect
from typing import Any
from unittest import TestCase
from unittest.mock import Mock, patch

from jsonschema.exceptions import ValidationError

import nanopy.rpc

from . import PACC0, PACC1, R16, R64, R128, RB, RD, RI, RIP, Z64

rpc = nanopy.rpc.HTTP()
R: dict[str, list[Any]] = {
    "account_balance": [{"balance": RI, "pending": RI, "receivable": RI}],
    "account_block_count": [{"block_count": RI}],
    "account_get": [{"account": PACC0}],
    "account_history": [
        {
            "account": PACC0,
            "history": [
                {
                    "type": "send",
                    "account": PACC1,
                    "amount": RI,
                    "local_timestamp": RI,
                    "height": RI,
                    "hash": R64,
                    "confirmed": "true",
                }
            ],
            "previous": R64,
        }
    ],
    "account_info": [
        {
            "frontier": R64,
            "open_block": R64,
            "representative_block": R64,
            "balance": RI,
            "confirmed_balance": RI,
            "modified_timestamp": RI,
            "block_count": RI,
            "account_version": RI,
            "confirmation_height": RI,
            "confirmation_height_frontier": R64,
            "representative": PACC0,
            "confirmed_representative": PACC0,
            "weight": RI,
            "pending": RI,
            "receivable": RI,
            "confirmed_pending": RI,
            "confirmed_receivable": RI,
        }
    ],
    "account_key": [{"key": R64}],
    "account_representative": [{"representative": PACC0}],
    "account_weight": [{"weight": RI}],
    "accounts_balances": [
        {"balances": {PACC0: {"balance": RI, "pending": RI, "receivable": RI}}}
    ],
    "accounts_frontiers": [{"frontiers": {PACC0: R64}}],
    "accounts_receivable": [
        {"blocks": {PACC0: [R64]}},
        {"blocks": {PACC0: {R64: RI}}},
        {"blocks": {PACC0: {R64: {"amount": RI, "source": PACC0}}}},
    ],
    "accounts_representatives": [{"representatives": {PACC0: PACC0}}],
    "available_supply": [{"available": RI}],
    "block_account": [{"account": PACC0}],
    "block_confirm": [{"started": "1"}],
    "block_count": [{"count": RI, "unchecked": RI, "cemented": RI}],
    "block_create": [{"hash": R64, "difficulty": R16, "block": RB}],
    "block_hash": [{"hash": R64}],
    "block_info": [
        {
            "block_account": PACC0,
            "amount": RI,
            "balance": RI,
            "height": RI,
            "local_timestamp": RI,
            "successor": R64,
            "confirmed": "true",
            "subtype": "send",
            "contents": RB,
        }
    ],
    "blocks": [{"blocks": {R64: RB}}],
    "blocks_info": [
        {
            "blocks": {
                R64: {
                    "block_account": PACC0,
                    "amount": RI,
                    "balance": RI,
                    "height": RI,
                    "local_timestamp": RI,
                    "successor": R64,
                    "confirmed": "true",
                    "subtype": "send",
                    "contents": RB,
                    "pending": "1",
                    "source_account": PACC0,
                    "receive_hash": R64,
                }
            },
            "blocks_not_found": [R64],
        }
    ],
    "bootstrap": [{"success": ""}],
    "bootstrap_any": [{"success": ""}],
    "bootstrap_lazy": [{"started": "1"}],
    "bootstrap_priorities": [{}],
    "bootstrap_reset": [{}],
    "bootstrap_status": [{}],
    "chain": [{"blocks": [R64]}],
    "confirmation_active": [
        {"confirmations": [R128], "unconfirmed": RI, "confirmed": RI}
    ],
    "confirmation_history": [{"confirmation_stats": {}, "confirmations": ""}],
    "confirmation_info": [
        {
            "announcements": RI,
            "last_winner": R64,
            "total_tally": RI,
            "blocks": {R64: {}},
        }
    ],
    "confirmation_quorum": [
        {
            "quorum_delta": RI,
            "online_weight_quorum_percent": RI,
            "online_weight_minimum": RI,
            "online_stake_total": RI,
            "peers_stake_total": RI,
            "trended_stake_total": RI,
        }
    ],
    "database_txn_tracker": [{}],
    "delegators": [{"delegators": {PACC0: RI}}],
    "delegators_count": [{"count": RI}],
    "deterministic_key": [{"private": R64, "public": R64, "account": PACC0}],
    "election_statistics": [
        {
            "normal": RI,
            "priority": RI,
            "hinted": RI,
            "optimistic": RI,
            "total": RI,
            "aec_utilization_percentage": RD,
            "max_election_age": RI,
            "average_election_age": RI,
        }
    ],
    "epoch_upgrade": [{"started": "1"}],
    "frontier_count": [{"count": RI}],
    "frontiers": [{"frontiers": {PACC0: R64}}],
    "keepalive": [{"started": "1"}],
    "key_create": [{"private": R64, "public": R64, "account": PACC0}],
    "key_expand": [{"private": R64, "public": R64, "account": PACC0}],
    "ledger": [
        {
            "accounts": {
                PACC0: {
                    "frontier": R64,
                    "open_block": R64,
                    "representative_block": R64,
                    "balance": RI,
                    "modified_timestamp": RI,
                    "block_count": RI,
                    "representative": PACC0,
                    "weight": RI,
                    "pending": RI,
                    "receivable": RI,
                }
            }
        }
    ],
    "node_id": [{"private": R64, "public": R64, "as_account": PACC0, "node_id": PACC0}],
    "peers": [
        {"peers": {RIP: RI}},
        {"peers": {RIP: {"protocol_version": RI, "node_id": PACC0, "type": "tcp"}}},
    ],
    "populate_backlog": [{"success": ""}],
    "process": [{"hash": R64}],
    "receivable": [
        {"blocks": [R64]},
        {"blocks": {R64: RI}},
        {"blocks": {R64: {"amount": RI, "source": PACC0}}},
    ],
    "receivable_exists": [{"exists": "1"}],
    "representatives": [{"representatives": {PACC0: RI}}],
    "representatives_online": [
        {"representatives": [PACC0]},
        {"representatives": {PACC0: {"weight": RI}}},
    ],
    "republish": [{"success": "", "blocks": [R64]}],
    "sign": [{"signature": R128, "block": RB}],
    "stats": [{}],
    "stats_clear": [{"success": ""}],
    "stop": [{"success": ""}],
    "successors": [{"blocks": [R64]}],
    "telemetry": [{}],
    "validate_account_number": [{"valid": "1"}],
    "version": [
        {
            "rpc_version": RI,
            "store_version": RI,
            "protocol_version": RI,
            "node_vendor": "",
            "store_vendor": "",
            "network": "",
            "network_identifier": R64,
            "build_info": "",
        }
    ],
    "unchecked": [{"blocks": {R64: RB}}],
    "unchecked_clear": [{"success": ""}],
    "unchecked_get": [{"modified_timestamp": RI, "contents": {R64: RB}}],
    "unchecked_keys": [
        {"key": R64, "hash": R64, "modified_timestamp": RI, "contents": {R64: RB}}
    ],
    "unopened": [{"accounts": {PACC0: RI}}],
    "uptime": [{"seconds": RI}],
    "work_cancel": [{"success": ""}],
    "work_generate": [{"work": R16, "difficulty": R16, "multiplier": RD, "hash": R64}],
    "work_peer_add": [{"success": ""}],
    "work_peers": [{"work_peers": [RIP]}],
    "work_peers_clear": [{"success": ""}],
    "work_validate": [
        {"valid_all": "1", "valid_receive": "1", "difficulty": R16, "multiplier": RD}
    ],
    "account_create": [{"account": PACC0}],
    "account_list": [{"accounts": [PACC0]}],
    "account_move": [{"moved": "1"}],
    "account_remove": [{"removed": "1"}],
    "account_representative_set": [{"block": R64}],
    "accounts_create": [{"accounts": [PACC0]}],
    "password_change": [{"changed": "1"}],
    "password_enter": [{"valid": "1"}],
    "password_valid": [{"valid": "1"}],
    "receive": [{"block": R64}],
    "receive_minimum": [{"amount": RI}],
    "receive_minimum_set": [{"success": ""}],
    "search_receivable": [{"started": "1"}],
    "search_receivable_all": [{"success": ""}],
    "send": [{"block": R64}],
    "wallet_add": [{"account": PACC0}],
    "wallet_add_watch": [{"success": ""}],
    "wallet_balances": [
        {"balances": {PACC0: {"balance": RI, "pending": RI, "receivable": RI}}}
    ],
    "wallet_change_seed": [{"success": ""}],
    "wallet_contains": [{"exists": "1"}],
    "wallet_create": [{"wallet": R64}],
    "wallet_destroy": [{"destroyed": "1"}],
    "wallet_export": [{}],
    "wallet_frontiers": [{"frontiers": {PACC0: R64}}],
    "wallet_history": [
        {
            "history": [
                {
                    "type": "send",
                    "account": PACC0,
                    "amount": RI,
                    "block_account": PACC0,
                    "hash": R64,
                    "local_timestamp": RI,
                }
            ]
        }
    ],
    "wallet_info": [
        {
            "balance": RI,
            "pending": RI,
            "receivable": RI,
            "accounts_count": RI,
            "adhoc_count": RI,
            "deterministic_count": RI,
            "deterministic_index": RI,
            "accounts_block_count": RI,
            "accounts_cemented_block_count": RI,
        }
    ],
    "wallet_ledger": [
        {
            "accounts": {
                PACC0: {
                    "frontier": R64,
                    "open_block": R64,
                    "representative_block": R64,
                    "balance": RI,
                    "modified_timestamp": RI,
                    "block_count": RI,
                }
            }
        }
    ],
    "wallet_lock": [{"locked": "1"}],
    "wallet_locked": [{"locked": "1"}],
    "wallet_receivable": [
        {"blocks": {PACC0: [R64]}},
        {"blocks": {PACC0: {R64: RI}}},
        {"blocks": {PACC0: {R64: {"amount": RI, "source": PACC0}}}},
    ],
    "wallet_representative": [{"representative": PACC0}],
    "wallet_representative_set": [{"set": "1"}],
    "wallet_republish": [{"blocks": [R64]}],
    "wallet_work_get": [{"works": {PACC0: R16}}],
    "work_get": [{"work": R16}],
    "work_set": [{"success": ""}],
    "nano_to_raw": [{"amount": RI}],
    "raw_to_nano": [{"amount": RI}],
}


@patch.object(nanopy.rpc.HTTP, "request")
class TestRPC(TestCase):

    def test_response_validation(self, mr: Mock) -> None:
        with (
            patch.object(rpc, "_validate_block"),
            patch.object(rpc, "_validate_block_info"),
            patch.object(rpc, "_validate_blocks"),
            patch.object(rpc, "_validate_blocks_info"),
        ):
            for n, m in inspect.getmembers(rpc, predicate=inspect.ismethod):
                if n.startswith("_"):
                    continue
                params = inspect.signature(m).parameters
                args = [v.default for p, v in params.items() if p != "self"]
                with self.subTest(n):
                    for r in R[n]:
                        mr.return_value = r
                        m(*args)

    def test_account_block_count(self, mr: Mock) -> None:
        se = [
            {"test": "x"},
            {"block_count": "-1"},
            {"block_count": "1" * 40},
            {"block_count": "a"},
        ]
        for s in se:
            mr.return_value = s
            with self.assertRaises(ValidationError):
                rpc.account_block_count(PACC0)

    def test_account_get(self, mr: Mock) -> None:
        se = [
            {"account": ""},
            {"account": "x"},
        ]
        for s in se:
            mr.return_value = s
            with self.assertRaises(ValidationError):
                rpc.account_get(Z64)

    def test_block_info(self, mr: Mock) -> None:
        mr.return_value = copy.deepcopy(R["block_info"][0])
        rpc.block_info(
            "1f5bc8e8c4b862fdc5d01857325dade3561349505f4a4d478610e3394d2105f3"
        )
        with self.assertRaises(AssertionError):
            mr.return_value["contents"]["signature"] = R128
            rpc.block_info(
                "1f5bc8e8c4b862fdc5d01857325dade3561349505f4a4d478610e3394d2105f3"
            )
