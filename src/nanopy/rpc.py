# pylint: disable=too-many-lines
"""
nanopy.rpc
##########
A wrapper to make RPC requests to a node.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Callable

import requests
import websocket
from jsonschema import validate

import nanopy as npy


class RPC(ABC):  # pylint: disable=too-many-public-methods
    "RPC base class"

    _AccP = "^[a-z]{3,4}_[0-9a-z]{60}$"
    _Acc = {"type": "string", "pattern": _AccP}
    _H16P = "^[0-9a-fA-F]{16}$"
    _H16 = {"type": "string", "pattern": _H16P}
    _H64P = "^[0-9a-fA-F]{64}$"
    _H64 = {"type": "string", "pattern": _H64P}
    _H128P = "^[0-9a-fA-F]{128}$"
    _H128 = {"type": "string", "pattern": _H128P}
    _UInt = {"type": "string", "pattern": "^[0-9]{1,39}$"}
    _UDbl = {"type": "string", "pattern": "^[0-9.]{1,39}$"}
    _Bool = {"type": "string", "pattern": "^true|false$"}
    _Type = {"type": "string", "pattern": "^change|epoch|receive|send|state$"}
    _ZO = {"type": "string", "pattern": "^[01]?$"}
    _IPP = "^[][0-9a-fA-F:.]{1,53}$"
    _IP = {"type": "string", "pattern": _IPP}
    _List: Callable[[dict[str, Any]], dict[str, Any]] = lambda x: {
        "type": "array",
        "items": x,
    }
    _Dict: Callable[[dict[str, Any]], dict[str, Any]] = lambda x: {
        "type": "object",
        "properties": x,
        "additionalProperties": False,
    }
    _DictP: Callable[[dict[str, Any]], dict[str, Any]] = lambda x: {
        "type": "object",
        "patternProperties": x,
        "additionalProperties": False,
    }
    _Req: Callable[[list[str]], dict[str, Any]] = lambda x: {
        "anyOf": [
            {"required": ["error"]},
            {"required": ["errors"]},
            {"required": x},
        ],
    }
    _Blk = _Dict(
        {
            "type": _Type,
            "account": _Acc,
            "previous": _H64,
            "representative": _Acc,
            "balance": _UInt,
            "link": _H64,
            "link_as_account": _Acc,
            "signature": _H128,
            "work": _H16,
        }
    )

    @abstractmethod
    def request(self, data: dict[str, Any]) -> Any:
        """Make RPC request. Override in derived class.

        :arg data: dict like object
        :return: JSON reponse as dict
        """
        raise NotImplementedError("Implement in a derived class")

    def _request(
        self, data: dict[str, Any], schema: None | dict[str, Any] = None
    ) -> Any:
        """Make a request and validate response with JSON schema

        :arg data: dict like object
        :arg schema: JSON schema to validate response
        :return: JSON reponse as dict
        """
        r = self.request(data)
        if schema:
            schema.pop("additionalProperties", None)
            validate(r, schema)
        return r

    def account_balance(self, account: str, include_only_confirmed: bool = True) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_balance"
        data: dict[str, Any] = {}
        data["action"] = "account_balance"
        data["account"] = account
        if not include_only_confirmed:
            data["include_only_confirmed"] = False
        s = RPC._Dict(
            {
                "balance": RPC._UInt,
                "pending": RPC._UInt,
                "receivable": RPC._UInt,
            }
        ) | RPC._Req(["balance", "pending", "receivable"])
        return self._request(data, s)

    def account_block_count(self, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_block_count"
        data: dict[str, Any] = {}
        data["action"] = "account_block_count"
        data["account"] = account
        s = RPC._Dict({"block_count": RPC._UInt}) | RPC._Req(["block_count"])
        return self._request(data, s)

    def account_get(self, key: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_get"
        data: dict[str, Any] = {}
        data["action"] = "account_get"
        data["key"] = key
        s = RPC._Dict({"account": RPC._Acc}) | RPC._Req(["account"])
        return self._request(data, s)

    def account_history(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        account: str,
        count: int = 1,
        raw: bool = False,
        head: str = "",
        include_linked_account: bool = False,
        offset: int = 0,
        reverse: bool = False,
        account_filter: list[str] | None = None,
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_history"
        data: dict[str, Any] = {}
        data["action"] = "account_history"
        data["account"] = account
        data["count"] = count
        if raw:
            data["raw"] = True
        if head:
            data["head"] = head
        if include_linked_account:
            data["include_linked_account"] = True
        if offset:
            data["offset"] = offset
        if reverse:
            data["reverse"] = reverse
        if account_filter:
            data["account_filter"] = account_filter
        s = RPC._Dict(
            {
                "account": RPC._Acc,
                "history": RPC._List(
                    RPC._Dict(
                        {
                            "type": RPC._Type,
                            "account": RPC._Acc,
                            "amount": RPC._UInt,
                            "local_timestamp": RPC._UInt,
                            "height": RPC._UInt,
                            "hash": RPC._H64,
                            "confirmed": RPC._Bool,
                        }
                    )
                ),
                "previous": RPC._H64,
            }
        ) | RPC._Req(["account", "history"])
        return self._request(data, s)

    def account_info(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        account: str,
        include_confirmed: bool = False,
        representative: bool = False,
        weight: bool = False,
        pending: bool = False,
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_info"
        data: dict[str, Any] = {}
        data["action"] = "account_info"
        data["account"] = account
        if include_confirmed:
            data["include_confirmed"] = True
        if representative:
            data["representative"] = True
        if weight:
            data["weight"] = True
        if pending:
            data["pending"] = True
        s = RPC._Dict(
            {
                "frontier": RPC._H64,
                "open_block": RPC._H64,
                "representative_block": RPC._H64,
                "balance": RPC._UInt,
                "confirmed_balance": RPC._UInt,
                "modified_timestamp": RPC._UInt,
                "block_count": RPC._UInt,
                "account_version": RPC._UInt,
                "confirmation_height": RPC._UInt,
                "confirmation_height_frontier": RPC._H64,
                "representative": RPC._Acc,
                "confirmed_representative": RPC._Acc,
                "weight": RPC._UInt,
                "pending": RPC._UInt,
                "receivable": RPC._UInt,
                "confirmed_pending": RPC._UInt,
                "confirmed_receivable": RPC._UInt,
            }
        ) | RPC._Req(
            [
                "frontier",
                "open_block",
                "representative_block",
                "balance",
                "modified_timestamp",
                "block_count",
                "account_version",
                "confirmation_height",
                "confirmation_height_frontier",
            ]
        )
        return self._request(data, s)

    def account_key(self, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_key"
        data: dict[str, Any] = {}
        data["action"] = "account_key"
        data["account"] = account
        s = RPC._Dict({"key": RPC._H64}) | RPC._Req(["key"])
        return self._request(data, s)

    def account_representative(self, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_representative"
        data: dict[str, Any] = {}
        data["action"] = "account_representative"
        data["account"] = account
        s = RPC._Dict({"representative": RPC._Acc}) | RPC._Req(["representative"])
        return self._request(data, s)

    def account_weight(self, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_weight"
        data: dict[str, Any] = {}
        data["action"] = "account_weight"
        data["account"] = account
        s = RPC._Dict({"weight": RPC._UInt}) | RPC._Req(["weight"])
        return self._request(data, s)

    def accounts_balances(
        self, accounts: list[str], include_only_confirmed: bool = True
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#accounts_balances"
        data: dict[str, Any] = {}
        data["action"] = "accounts_balances"
        data["accounts"] = accounts
        if not include_only_confirmed:
            data["include_only_confirmed"] = False
        s = RPC._Dict(
            {
                "balances": RPC._DictP(
                    {
                        RPC._AccP: RPC._Dict(
                            {
                                "balance": RPC._UInt,
                                "pending": RPC._UInt,
                                "receivable": RPC._UInt,
                            }
                        )
                    }
                )
            }
        ) | RPC._Req(["balances"])
        return self._request(data, s)

    def accounts_frontiers(self, accounts: list[str]) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#accounts_frontiers"
        data: dict[str, Any] = {}
        data["action"] = "accounts_frontiers"
        data["accounts"] = accounts
        s = RPC._Dict({"frontiers": RPC._DictP({RPC._AccP: RPC._H64})}) | RPC._Req(
            ["frontiers"]
        )
        return self._request(data, s)

    def accounts_receivable(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        accounts: list[str],
        count: int = 1,
        threshold: str = "",
        source: bool = False,
        include_active: bool = False,
        sorting: bool = False,
        include_only_confirmed: bool = True,
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#accounts_receivable"
        data: dict[str, Any] = {}
        data["action"] = "accounts_receivable"
        data["accounts"] = accounts
        data["count"] = count
        if threshold:
            data["threshold"] = threshold
        if source:
            data["source"] = True
        if include_active:
            data["include_active"] = True
        if sorting:
            data["sorting"] = True
        if not include_only_confirmed:
            data["include_only_confirmed"] = False
        s = RPC._Dict(
            {
                "blocks": RPC._DictP(
                    {
                        RPC._AccP: {
                            "anyOf": [
                                RPC._List(RPC._H64),
                                RPC._DictP(
                                    {
                                        RPC._H64P: {
                                            "anyOf": [
                                                RPC._UInt,
                                                RPC._Dict(
                                                    {
                                                        "amount": RPC._UInt,
                                                        "source": RPC._Acc,
                                                    }
                                                ),
                                            ]
                                        }
                                    }
                                ),
                            ]
                        }
                    }
                )
            }
        ) | RPC._Req(["blocks"])
        return self._request(data, s)

    def accounts_representatives(self, accounts: list[str]) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#accounts_representatives"
        data: dict[str, Any] = {}
        data["action"] = "accounts_representatives"
        data["accounts"] = accounts
        s = RPC._Dict(
            {"representatives": RPC._DictP({RPC._AccP: RPC._Acc})}
        ) | RPC._Req(["representatives"])
        return self._request(data, s)

    def available_supply(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#available_supply"
        data: dict[str, Any] = {}
        data["action"] = "available_supply"
        s = RPC._Dict({"available": RPC._UInt}) | RPC._Req(["available"])
        return self._request(data, s)

    def block_account(self, _hash: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#block_account"
        data: dict[str, Any] = {}
        data["action"] = "block_account"
        data["hash"] = _hash
        s = RPC._Dict({"account": RPC._Acc}) | RPC._Req(["account"])
        return self._request(data, s)

    def block_confirm(self, _hash: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#block_confirm"
        data: dict[str, Any] = {}
        data["action"] = "block_confirm"
        data["hash"] = _hash
        s = RPC._Dict({"started": RPC._ZO}) | RPC._Req(["started"])
        return self._request(data, s)

    def block_count(self, include_cemented: bool = True) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#block_count"
        data: dict[str, Any] = {}
        data["action"] = "block_count"
        if not include_cemented:
            data["include_cemented"] = False
        s = RPC._Dict(
            {"count": RPC._UInt, "unchecked": RPC._UInt, "cemented": RPC._UInt}
        ) | RPC._Req(["count", "unchecked"])
        return self._request(data, s)

    def block_create(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
        self,
        balance: str,
        representative: str,
        previous: str,
        wallet: str = "",
        account: str = "",
        key: str = "",
        source: str = "",
        destination: str = "",
        link: str = "",
        work: str = "",
        version: str = "work_1",
        difficulty: str = "",
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#block_create"
        data: dict[str, Any] = {}
        data["action"] = "block_create"
        data["type"] = "state"
        data["balance"] = balance
        if wallet:
            data["wallet"] = wallet
        if account:
            data["account"] = account
        if key:
            data["key"] = key
        if source:
            data["source"] = source
        if destination:
            data["destination"] = destination
        if link:
            data["link"] = link
        data["representative"] = representative
        data["previous"] = previous
        if work:
            data["work"] = work
        elif difficulty:
            data["difficulty"] = difficulty
        if version in ["work_1"]:
            data["version"] = version
        data["json_block"] = True
        s = RPC._Dict(
            {"hash": RPC._H64, "difficulty": RPC._H16, "block": RPC._Blk}
        ) | RPC._Req(["hash", "difficulty", "block"])
        return self._request(data, s)

    def block_hash(self, block: dict[str, str]) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#block_hash"
        data: dict[str, Any] = {}
        data["action"] = "block_hash"
        data["block"] = block
        data["json_block"] = True
        s = RPC._Dict({"hash": RPC._H64}) | RPC._Req(["hash"])
        return self._request(data, s)

    def _validate_block(self, _hash: str, block: Any) -> None:
        "validate block content"
        b = npy.StateBlock(
            npy.Account(block["account"]),
            npy.Account(block["representative"]),
            int(block["balance"]),
            block["previous"],
            block["link"],
            block["signature"],
            block["work"],
        )
        assert b.digest == _hash.lower()
        assert b.verify_signature()

    def _validate_block_info(self, _hash: str, r: Any) -> None:
        "validate the response of block_info"
        self._validate_block(_hash, r["contents"])

    def block_info(self, _hash: str, include_linked_account: bool = False) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#block_info"
        data: dict[str, Any] = {}
        data["action"] = "block_info"
        data["hash"] = _hash
        data["json_block"] = True
        if include_linked_account:
            data["include_linked_account"] = True
        s = RPC._Dict(
            {
                "block_account": RPC._Acc,
                "amount": RPC._UInt,
                "balance": RPC._UInt,
                "height": RPC._UInt,
                "local_timestamp": RPC._UInt,
                "successor": RPC._H64,
                "confirmed": RPC._Bool,
                "contents": RPC._Blk,
                "subtype": RPC._Type,
            }
        ) | RPC._Req(
            [
                "block_account",
                "amount",
                "balance",
                "height",
                "local_timestamp",
                "successor",
                "confirmed",
                "contents",
                "subtype",
            ]
        )
        r = self._request(data, s)
        self._validate_block_info(_hash, r)
        return r

    def _validate_blocks(self, hashes: list[str], r: Any) -> None:
        "validate the response of blocks"
        for h in hashes:
            self._validate_block(h, r["blocks"][h])

    def blocks(self, hashes: list[str]) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#blocks"
        data: dict[str, Any] = {}
        data["action"] = "blocks"
        data["hashes"] = hashes
        data["json_block"] = True
        s = RPC._Dict({"blocks": RPC._DictP({RPC._H64P: RPC._Blk})}) | RPC._Req(
            ["blocks"]
        )
        r = self._request(data, s)
        self._validate_blocks(hashes, r)
        return r

    def _validate_blocks_info(self, hashes: list[str], r: Any) -> None:
        "validate the response of blocks_info"
        for h in hashes:
            self._validate_block_info(h, r["blocks"][h])

    def blocks_info(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        hashes: list[str],
        include_linked_account: bool = False,
        pending: bool = False,
        source: bool = False,
        receive_hash: bool = False,
        include_not_found: bool = False,
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#blocks_info"
        data: dict[str, Any] = {}
        data["action"] = "blocks_info"
        data["hashes"] = hashes
        if include_linked_account:
            data["include_linked_account"] = True
        if pending:
            data["pending"] = True
        if source:
            data["source"] = True
        if receive_hash:
            data["receive_hash"] = True
        data["json_block"] = True
        if include_not_found:
            data["include_not_found"] = True
        s = RPC._Dict(
            {
                "blocks": RPC._DictP(
                    {
                        RPC._H64P: RPC._Dict(
                            {
                                "block_account": RPC._Acc,
                                "amount": RPC._UInt,
                                "balance": RPC._UInt,
                                "height": RPC._UInt,
                                "local_timestamp": RPC._UInt,
                                "successor": RPC._H64,
                                "confirmed": RPC._Bool,
                                "contents": RPC._Blk,
                                "subtype": RPC._Type,
                                "pending": RPC._ZO,
                                "source_account": RPC._Acc,
                                "receive_hash": RPC._H64,
                            }
                        )
                    }
                ),
                "blocks_not_found": RPC._List(RPC._H64),
            }
        ) | RPC._Req(["blocks"])
        r = self._request(data, s)
        self._validate_blocks_info(hashes, r)
        return r

    def bootstrap(
        self,
        address: str,
        port: str,
        bypass_frontier_confirmation: bool = False,
        _id: str = "",
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#bootstrap"
        data: dict[str, Any] = {}
        data["action"] = "bootstrap"
        data["address"] = address
        data["port"] = port
        if _id:
            data["id"] = _id
        if bypass_frontier_confirmation:
            data["bypass_frontier_confirmation"] = True
        s = RPC._Dict({"success": RPC._ZO}) | RPC._Req(["success"])
        return self._request(data, s)

    def bootstrap_any(
        self, force: bool = False, _id: str = "", account: str = ""
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#bootstrap_any"
        data: dict[str, Any] = {}
        data["action"] = "bootstrap_any"
        if force:
            data["force"] = True
        if _id:
            data["id"] = _id
        if account:
            data["account"] = account
        s = RPC._Dict({"success": RPC._ZO}) | RPC._Req(["success"])
        return self._request(data, s)

    def bootstrap_lazy(self, hash_: str, force: bool = False, _id: str = "") -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#bootstrap_lazy"
        data: dict[str, Any] = {}
        data["action"] = "bootstrap_lazy"
        data["hash"] = hash_
        if force:
            data["force"] = True
        if _id:
            data["id"] = _id
        s = RPC._Dict({"started": RPC._ZO}) | RPC._Req(["started"])
        return self._request(data, s)

    def bootstrap_priorities(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#bootstrap_priorities"
        data: dict[str, Any] = {}
        data["action"] = "bootstrap_priorities"
        return self._request(data)

    def bootstrap_reset(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#bootstrap_reset"
        data: dict[str, Any] = {}
        data["action"] = "bootstrap_reset"
        return self._request(data)

    def bootstrap_status(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#bootstrap_status"
        data: dict[str, Any] = {}
        data["action"] = "bootstrap_status"
        return self._request(data)

    def chain(
        self, block: str, count: int = 1, offset: int = 0, reverse: bool = False
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#chain"
        data: dict[str, Any] = {}
        data["action"] = "chain"
        data["block"] = block
        data["count"] = count
        if offset:
            data["offset"] = offset
        if reverse:
            data["reverse"] = True
        s = RPC._Dict({"blocks": RPC._List(RPC._H64)}) | RPC._Req(["blocks"])
        return self._request(data, s)

    def confirmation_active(self, announcements: int = 0) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#confirmation_active"
        data: dict[str, Any] = {}
        data["action"] = "confirmation_active"
        if announcements:
            data["announcements"] = announcements
        s = RPC._Dict(
            {
                "confirmations": RPC._List(RPC._H128),
                "unconfirmed": RPC._UInt,
                "confirmed": RPC._UInt,
            }
        ) | RPC._Req(["confirmations", "unconfirmed", "confirmed"])
        return self._request(data, s)

    def confirmation_history(self, _hash: str = "") -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#confirmation_history"
        data: dict[str, Any] = {}
        data["action"] = "confirmation_history"
        if _hash:
            data["hash"] = _hash
        s = RPC._Dict({}) | RPC._Req(["confirmation_stats", "confirmations"])
        return self._request(data, s)

    def confirmation_info(
        self,
        root: str,
        contents: bool = True,
        representatives: bool = False,
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#confirmation_info"
        data: dict[str, Any] = {}
        data["action"] = "confirmation_info"
        data["root"] = root
        if not contents:
            data["contents"] = False
        if representatives:
            data["representatives"] = True
        data["json_block"] = True
        s = RPC._Dict(
            {
                "announcements": RPC._UInt,
                "last_winner": RPC._H64,
                "total_tally": RPC._UInt,
                "blocks": RPC._DictP({RPC._H64P: {}}),
            }
        ) | RPC._Req(["announcements", "last_winner", "total_tally", "blocks"])
        return self._request(data, s)

    def confirmation_quorum(self, peer_details: bool = False) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#confirmation_quorum"
        data: dict[str, Any] = {}
        data["action"] = "confirmation_quorum"
        if peer_details:
            data["peer_details"] = True
        s = RPC._Dict(
            {
                "quorum_delta": RPC._UInt,
                "online_weight_quorum_percent": RPC._UInt,
                "online_weight_minimum": RPC._UInt,
                "online_stake_total": RPC._UInt,
                "peers_stake_total": RPC._UInt,
                "trended_stake_total": RPC._UInt,
            }
        ) | RPC._Req(
            [
                "quorum_delta",
                "online_weight_quorum_percent",
                "online_weight_minimum",
                "online_stake_total",
                "peers_stake_total",
                "trended_stake_total",
            ]
        )
        return self._request(data, s)

    def database_txn_tracker(self, min_read_time: int, min_write_time: int) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#database_txn_tracker"
        data: dict[str, Any] = {}
        data["action"] = "database_txn_tracker"
        data["min_read_time"] = min_read_time
        data["min_write_time"] = min_write_time
        return self._request(data)

    def delegators(
        self, account: str, threshold: int = 0, count: int = 0, start: str = ""
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#delegators"
        data: dict[str, Any] = {}
        data["action"] = "delegators"
        data["account"] = account
        if threshold:
            data["threshold"] = threshold
        if count:
            data["count"] = count
        if start:
            data["start"] = start
        s = RPC._Dict({"delegators": RPC._DictP({RPC._AccP: RPC._UInt})}) | RPC._Req(
            ["delegators"]
        )
        return self._request(data, s)

    def delegators_count(self, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#delegators_count"
        data: dict[str, Any] = {}
        data["action"] = "delegators_count"
        data["account"] = account
        s = RPC._Dict({"count": RPC._UInt}) | RPC._Req(["count"])
        return self._request(data, s)

    def deterministic_key(self, seed: str, index: int) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#deterministic_key"
        data: dict[str, Any] = {}
        data["action"] = "deterministic_key"
        data["seed"] = seed
        data["index"] = index
        s = RPC._Dict(
            {"private": RPC._H64, "public": RPC._H64, "account": RPC._Acc}
        ) | RPC._Req(["private", "public", "account"])
        return self._request(data, s)

    def election_statistics(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#election_statistics"
        data: dict[str, Any] = {}
        data["action"] = "election_statistics"
        s = RPC._Dict(
            {
                "normal": RPC._UInt,
                "priority": RPC._UInt,
                "hinted": RPC._UInt,
                "optimistic": RPC._UInt,
                "total": RPC._UInt,
                "aec_utilization_percentage": RPC._UDbl,
                "max_election_age": RPC._UInt,
                "average_election_age": RPC._UInt,
            }
        ) | RPC._Req(
            [
                "normal",
                "priority",
                "hinted",
                "optimistic",
                "total",
                "aec_utilization_percentage",
                "max_election_age",
                "average_election_age",
            ]
        )
        return self._request(data, s)

    def epoch_upgrade(
        self, epoch: int, key: str, count: int = 0, threads: int = 0
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#epoch_upgrade"
        data: dict[str, Any] = {}
        data["action"] = "epoch_upgrade"
        data["epoch"] = epoch
        data["key"] = key
        if count:
            data["count"] = count
        if threads:
            data["threads"] = threads
        s = RPC._Dict({"started": RPC._ZO}) | RPC._Req(["started"])
        return self._request(data, s)

    def frontier_count(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#frontier_count"
        data: dict[str, Any] = {}
        data["action"] = "frontier_count"
        s = RPC._Dict({"count": RPC._UInt}) | RPC._Req(["count"])
        return self._request(data, s)

    def frontiers(self, account: str, count: int = 1) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#frontiers"
        data: dict[str, Any] = {}
        data["action"] = "frontiers"
        data["account"] = account
        data["count"] = count
        s = RPC._Dict({"frontiers": RPC._DictP({RPC._AccP: RPC._H64})}) | RPC._Req(
            ["frontiers"]
        )
        return self._request(data, s)

    def keepalive(self, address: str, port: int) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#keepalive"
        data: dict[str, Any] = {}
        data["action"] = "keepalive"
        data["address"] = address
        data["port"] = port
        s = RPC._Dict({"started": RPC._ZO}) | RPC._Req(["started"])
        return self._request(data, s)

    def key_create(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#key_create"
        data: dict[str, Any] = {}
        data["action"] = "key_create"
        s = RPC._Dict(
            {"private": RPC._H64, "public": RPC._H64, "account": RPC._Acc}
        ) | RPC._Req(["private", "public", "account"])
        return self._request(data, s)

    def key_expand(self, key: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#key_expand"
        data: dict[str, Any] = {}
        data["action"] = "key_expand"
        data["key"] = key
        s = RPC._Dict(
            {"private": RPC._H64, "public": RPC._H64, "account": RPC._Acc}
        ) | RPC._Req(["private", "public", "account"])
        return self._request(data, s)

    def ledger(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        account: str,
        count: int = 1,
        representative: bool = False,
        weight: bool = False,
        receivable: bool = False,
        modified_since: int = 0,
        sorting: bool = False,
        threshold: int = 0,
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#ledger"
        data: dict[str, Any] = {}
        data["action"] = "ledger"
        data["account"] = account
        data["count"] = count
        if representative:
            data["representative"] = True
        if weight:
            data["weight"] = True
        if receivable:
            data["receivable"] = True
        if modified_since:
            data["modified_since"] = modified_since
        if sorting:
            data["sorting"] = True
        if threshold:
            data["threshold"] = threshold
        s = RPC._Dict(
            {
                "accounts": RPC._DictP(
                    {
                        RPC._AccP: RPC._Dict(
                            {
                                "frontier": RPC._H64,
                                "open_block": RPC._H64,
                                "representative_block": RPC._H64,
                                "balance": RPC._UInt,
                                "modified_timestamp": RPC._UInt,
                                "block_count": RPC._UInt,
                                "representative": RPC._Acc,
                                "weight": RPC._UInt,
                                "pending": RPC._UInt,
                                "receivable": RPC._UInt,
                            }
                        )
                    }
                )
            }
        ) | RPC._Req(["accounts"])
        return self._request(data, s)

    def node_id(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#node_id"
        data: dict[str, Any] = {}
        data["action"] = "node_id"
        s = RPC._Dict(
            {
                "private": RPC._H64,
                "public": RPC._H64,
                "as_account": RPC._Acc,
                "node_id": RPC._Acc,
            }
        ) | RPC._Req(["private", "public", "as_account", "node_id"])
        return self._request(data, s)

    def peers(self, peer_details: bool = False) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#peers"
        data: dict[str, Any] = {}
        data["action"] = "peers"
        if peer_details:
            data["peer_details"] = True
        s = RPC._Dict(
            {
                "peers": {
                    "anyOf": [
                        RPC._DictP({RPC._IPP: RPC._UInt}),
                        RPC._DictP(
                            {
                                RPC._IPP: RPC._Dict(
                                    {
                                        "protocol_version": RPC._UInt,
                                        "node_id": RPC._Acc,
                                        "type": {"type": "string", "pattern": "^tcp$"},
                                    }
                                )
                            }
                        ),
                    ]
                }
            }
        ) | RPC._Req(["peers"])
        return self._request(data, s)

    def populate_backlog(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#populate_backlog"
        data: dict[str, Any] = {}
        data["action"] = "populate_backlog"
        s = RPC._Dict({"success": RPC._ZO}) | RPC._Req(["success"])
        return self._request(data, s)

    def process(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        block: str | dict[str, str],
        force: bool = False,
        subtype: str = "",
        watch_work: bool = True,
        _async: bool = False,
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#process"
        data: dict[str, Any] = {}
        data["action"] = "process"
        data["block"] = block
        if force:
            data["force"] = True
        if subtype:
            data["subtype"] = subtype
        data["json_block"] = True
        if not watch_work:
            data["watch_work"] = False
        if _async:
            data["async"] = True
        s = RPC._Dict({"hash": RPC._H64}) | RPC._Req(["hash"])
        return self._request(data, s)

    def receivable(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        account: str,
        count: int = 0,
        threshold: int = 0,
        source: bool = False,
        include_active: bool = False,
        min_version: bool = False,
        sorting: bool = False,
        include_only_confirmed: bool = True,
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#receivable"
        data: dict[str, Any] = {}
        data["action"] = "receivable"
        data["account"] = account
        if count:
            data["count"] = count
        if threshold:
            data["threshold"] = threshold
        if source:
            data["source"] = True
        if include_active:
            data["include_active"] = True
        if min_version:
            data["min_version"] = True
        if sorting:
            data["sorting"] = True
        if not include_only_confirmed:
            data["include_only_confirmed"] = False
        s = RPC._Dict(
            {
                "blocks": RPC._DictP(
                    {
                        RPC._AccP: {
                            "anyOf": [
                                RPC._List(RPC._H64),
                                RPC._DictP(
                                    {
                                        RPC._H64P: {
                                            "anyOf": [
                                                RPC._UInt,
                                                RPC._Dict(
                                                    {
                                                        "amount": RPC._UInt,
                                                        "source": RPC._Acc,
                                                    }
                                                ),
                                            ]
                                        }
                                    }
                                ),
                            ]
                        }
                    }
                )
            }
        ) | RPC._Req(["blocks"])
        return self._request(data, s)

    def receivable_exists(
        self,
        _hash: str,
        include_active: bool = False,
        include_only_confirmed: bool = True,
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#receivable_exists"
        data: dict[str, Any] = {}
        data["action"] = "receivable_exists"
        data["hash"] = _hash
        if include_active:
            data["include_active"] = True
        if not include_only_confirmed:
            data["include_only_confirmed"] = False
        s = RPC._Dict({"exists": RPC._ZO}) | RPC._Req(["exists"])
        return self._request(data, s)

    def representatives(self, count: int = 1, sorting: bool = False) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#representatives"
        data: dict[str, Any] = {}
        data["action"] = "representatives"
        data["count"] = count
        if sorting:
            data["sorting"] = True
        s = RPC._Dict(
            {"representatives": RPC._DictP({RPC._AccP: RPC._UInt})}
        ) | RPC._Req(["representatives"])
        return self._request(data, s)

    def representatives_online(
        self, weight: bool = False, accounts: list[str] | None = None
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#representatives_online"
        data: dict[str, Any] = {}
        data["action"] = "representatives_online"
        if weight:
            data["weight"] = True
        if accounts:
            data["accounts"] = accounts
        s = RPC._Dict(
            {
                "representatives": {
                    "anyOf": [
                        RPC._List(RPC._Acc),
                        RPC._DictP({RPC._AccP: RPC._Dict({"weight": RPC._UInt})}),
                    ]
                }
            }
        ) | RPC._Req(["representatives"])
        return self._request(data, s)

    def republish(
        self, _hash: str, count: int = 1, sources: int = 0, destinations: int = 0
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#republish"
        data: dict[str, Any] = {}
        data["action"] = "republish"
        data["hash"] = _hash
        if sources:
            data["sources"] = sources
            data["count"] = count
        if destinations:
            data["destinations"] = destinations
            data["count"] = count
        s = RPC._Dict({"success": RPC._ZO, "blocks": RPC._List(RPC._H64)}) | RPC._Req(
            ["blocks"]
        )
        return self._request(data, s)

    def sign(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        key: str = "",
        wallet: str = "",
        account: str = "",
        block: str = "",
        _hash: str = "",
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#sign"
        data: dict[str, Any] = {}
        data["action"] = "sign"
        if key:
            data["key"] = key
        if wallet:
            data["wallet"] = wallet
        if account:
            data["account"] = account
        if isinstance(block, str):
            data["block"] = block
        else:
            data["block"] = json.dumps(block)
        if _hash:
            data["_hash"] = _hash
        data["json_block"] = True
        s = RPC._Dict({"signature": RPC._H128, "block": RPC._Blk}) | RPC._Req(
            ["signature"]
        )
        return self._request(data, s)

    def stats(self, _type: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#stats"
        data: dict[str, Any] = {}
        data["action"] = "stats"
        data["type"] = _type
        return self._request(data)

    def stats_clear(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#stats_clear"
        data: dict[str, Any] = {}
        data["action"] = "stats_clear"
        s = RPC._Dict({"success": RPC._ZO}) | RPC._Req(["success"])
        return self._request(data, s)

    def stop(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#stop"
        data: dict[str, Any] = {}
        data["action"] = "stop"
        s = RPC._Dict({"success": RPC._ZO}) | RPC._Req(["success"])
        return self._request(data, s)

    def successors(
        self, block: str, count: int = 1, offset: int = 0, reverse: bool = False
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#successors"
        data: dict[str, Any] = {}
        data["action"] = "successors"
        data["block"] = block
        data["count"] = count
        if offset:
            data["offset"] = offset
        if reverse:
            data["reverse"] = True
        s = RPC._Dict({"blocks": RPC._List(RPC._H64)}) | RPC._Req(["blocks"])
        return self._request(data, s)

    def telemetry(self, raw: bool = False, address: int = 0, port: int = 7075) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#telemetry"
        data: dict[str, Any] = {}
        data["action"] = "telemetry"
        if raw:
            data["raw"] = True
        if address:
            data["address"] = address
            data["port"] = port
        return self._request(data)

    def validate_account_number(self, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#validate_account_number"
        data: dict[str, Any] = {}
        data["action"] = "validate_account_number"
        data["account"] = account
        s = RPC._Dict({"valid": RPC._ZO}) | RPC._Req(["valid"])
        return self._request(data, s)

    def version(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#version"
        data: dict[str, Any] = {}
        data["action"] = "version"
        s = RPC._Dict(
            {
                "rpc_version": RPC._UInt,
                "store_version": RPC._UInt,
                "protocol_version": RPC._UInt,
                "node_vendor": {"type": "string"},
                "store_vendor": {"type": "string"},
                "network": {"type": "string"},
                "network_identifier": RPC._H64,
                "build_info": {"type": "string"},
            }
        ) | RPC._Req(
            [
                "rpc_version",
                "store_version",
                "protocol_version",
                "node_vendor",
                "store_vendor",
                "network",
                "network_identifier",
                "build_info",
            ]
        )
        return self._request(data, s)

    def unchecked(self, count: int = 1) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#unchecked"
        data: dict[str, Any] = {}
        data["action"] = "unchecked"
        data["json_block"] = True
        data["count"] = count
        s = RPC._Dict({"blocks": RPC._DictP({RPC._H64P: RPC._Blk})}) | RPC._Req(
            ["blocks"]
        )
        return self._request(data, s)

    def unchecked_clear(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#unchecked_clear"
        data: dict[str, Any] = {}
        data["action"] = "unchecked_clear"
        s = RPC._Dict({"success": RPC._ZO}) | RPC._Req(["success"])
        return self._request(data, s)

    def unchecked_get(self, _hash: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#unchecked_get"
        data: dict[str, Any] = {}
        data["action"] = "unchecked_get"
        data["hash"] = _hash
        data["json_block"] = True
        s = RPC._Dict(
            {
                "modified_timestamp": RPC._UInt,
                "contents": RPC._DictP({RPC._H64P: RPC._Blk}),
            }
        ) | RPC._Req(["modified_timestamp", "contents"])
        return self._request(data, s)

    def unchecked_keys(self, key: str, count: int = 1) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#unchecked_keys"
        data: dict[str, Any] = {}
        data["action"] = "unchecked_keys"
        data["key"] = key
        data["count"] = count
        data["json_block"] = True
        s = RPC._Dict(
            {
                "key": RPC._H64,
                "hash": RPC._H64,
                "modified_timestamp": RPC._UInt,
                "contents": RPC._DictP({RPC._H64P: RPC._Blk}),
            }
        ) | RPC._Req(["key", "hash", "modified_timestamp", "contents"])
        return self._request(data, s)

    def unopened(self, account: str = "", count: int = 1, threshold: int = 0) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#unopened"
        data: dict[str, Any] = {}
        data["action"] = "unopened"
        if account:
            data["account"] = account
        if count:
            data["count"] = count
        if threshold:
            data["threshold"] = threshold
        s = RPC._Dict({"accounts": RPC._DictP({RPC._AccP: RPC._UInt})}) | RPC._Req(
            ["accounts"]
        )
        return self._request(data, s)

    def uptime(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#uptime"
        data: dict[str, Any] = {}
        data["action"] = "uptime"
        s = RPC._Dict({"seconds": RPC._UInt}) | RPC._Req(["seconds"])
        return self._request(data, s)

    def work_cancel(self, _hash: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#work_cancel"
        data: dict[str, Any] = {}
        data["action"] = "work_cancel"
        data["hash"] = _hash
        s = RPC._Dict({"success": RPC._ZO}) | RPC._Req(["success"])
        return self._request(data, s)

    def work_generate(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        _hash: str,
        use_peers: bool = False,
        difficulty: str = "",
        multiplier: int = 0,
        account: str = "",
        version: str = "work_1",
        block: str = "",
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#work_generate"
        data: dict[str, Any] = {}
        data["action"] = "work_generate"
        data["hash"] = _hash
        if use_peers:
            data["use_peers"] = True
        if multiplier:
            data["multiplier"] = multiplier
        elif difficulty:
            data["difficulty"] = difficulty
        if account:
            data["account"] = account
        if version in ["work_1"]:
            data["version"] = version
        if block:
            data["block"] = block
        data["json_block"] = True
        s = RPC._Dict(
            {
                "work": RPC._H16,
                "difficulty": RPC._H16,
                "multiplier": RPC._UDbl,
                "hash": RPC._H64,
            }
        ) | RPC._Req(["work", "difficulty", "multiplier", "hash"])
        return self._request(data, s)

    def work_peer_add(self, address: str, port: int) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#work_peer_add"
        data: dict[str, Any] = {}
        data["action"] = "work_peer_add"
        data["address"] = address
        data["port"] = port
        s = RPC._Dict({"success": RPC._ZO}) | RPC._Req(["success"])
        return self._request(data, s)

    def work_peers(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#work_peers"
        data: dict[str, Any] = {}
        data["action"] = "work_peers"
        s = RPC._Dict({"work_peers": RPC._List(RPC._IP)}) | RPC._Req(["work_peers"])
        return self._request(data, s)

    def work_peers_clear(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#work_peers_clear"
        data: dict[str, Any] = {}
        data["action"] = "work_peers_clear"
        s = RPC._Dict({"success": RPC._ZO}) | RPC._Req(["success"])
        return self._request(data, s)

    def work_validate(
        self,
        work: str,
        _hash: str,
        difficulty: str = "",
        multiplier: int = 0,
        version: str = "work_1",
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#work_validate"
        data: dict[str, Any] = {}
        data["action"] = "work_validate"
        data["work"] = work
        data["hash"] = _hash
        if multiplier:
            data["multiplier"] = multiplier
        elif difficulty:
            data["difficulty"] = difficulty
        if version in ["work_1"]:
            data["version"] = version
        s = RPC._Dict(
            {
                "valid_all": RPC._ZO,
                "valid_receive": RPC._ZO,
                "difficulty": RPC._H16,
                "multiplier": RPC._UDbl,
            }
        ) | RPC._Req(["valid_all", "valid_receive", "difficulty", "multiplier"])
        return self._request(data, s)

    def account_create(self, wallet: str, index: int = 0, work: bool = True) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_create"
        data: dict[str, Any] = {}
        data["action"] = "account_create"
        data["wallet"] = wallet
        if index:
            data["index"] = index
        if not work:
            data["work"] = False
        s = RPC._Dict({"account": RPC._Acc}) | RPC._Req(["account"])
        return self._request(data, s)

    def account_list(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_list"
        data: dict[str, Any] = {}
        data["action"] = "account_list"
        data["wallet"] = wallet
        s = RPC._Dict({"accounts": RPC._List(RPC._Acc)}) | RPC._Req(["accounts"])
        return self._request(data, s)

    def account_move(self, wallet: str, source: str, accounts: list[str]) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_move"
        data: dict[str, Any] = {}
        data["action"] = "account_move"
        data["wallet"] = wallet
        data["source"] = source
        data["accounts"] = accounts
        s = RPC._Dict({"moved": RPC._ZO}) | RPC._Req(["moved"])
        return self._request(data, s)

    def account_remove(self, wallet: str, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_remove"
        data: dict[str, Any] = {}
        data["action"] = "account_remove"
        data["wallet"] = wallet
        data["account"] = account
        s = RPC._Dict({"removed": RPC._ZO}) | RPC._Req(["removed"])
        return self._request(data, s)

    def account_representative_set(
        self, wallet: str, account: str, representative: str, work: str = ""
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_representative_set"
        data: dict[str, Any] = {}
        data["action"] = "account_representative_set"
        data["wallet"] = wallet
        data["account"] = account
        data["representative"] = representative
        if work:
            data["work"] = work
        s = RPC._Dict({"block": RPC._H64}) | RPC._Req(["block"])
        return self._request(data, s)

    def accounts_create(self, wallet: str, count: int = 1, work: bool = True) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#accounts_create"
        data: dict[str, Any] = {}
        data["action"] = "accounts_create"
        data["wallet"] = wallet
        data["count"] = count
        if not work:
            data["work"] = False
        s = RPC._Dict({"accounts": RPC._List(RPC._Acc)}) | RPC._Req(["accounts"])
        return self._request(data, s)

    def password_change(self, wallet: str, password: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#password_change"
        data: dict[str, Any] = {}
        data["action"] = "password_change"
        data["wallet"] = wallet
        data["password"] = password
        s = RPC._Dict({"changed": RPC._ZO}) | RPC._Req(["changed"])
        return self._request(data, s)

    def password_enter(self, wallet: str, password: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#password_enter"
        data: dict[str, Any] = {}
        data["action"] = "password_enter"
        data["wallet"] = wallet
        data["password"] = password
        s = RPC._Dict({"valid": RPC._ZO}) | RPC._Req(["valid"])
        return self._request(data, s)

    def password_valid(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#password_valid"
        data: dict[str, Any] = {}
        data["action"] = "password_valid"
        data["wallet"] = wallet
        s = RPC._Dict({"valid": RPC._ZO}) | RPC._Req(["valid"])
        return self._request(data, s)

    def receive(self, wallet: str, account: str, block: str, work: str = "") -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#receive"
        data: dict[str, Any] = {}
        data["action"] = "receive"
        data["wallet"] = wallet
        data["account"] = account
        data["block"] = block
        if work:
            data["work"] = work
        s = RPC._Dict({"block": RPC._H64}) | RPC._Req(["block"])
        return self._request(data, s)

    def receive_minimum(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#receive_minimum"
        data: dict[str, Any] = {}
        data["action"] = "receive_minimum"
        s = RPC._Dict({"amount": RPC._UInt}) | RPC._Req(["amount"])
        return self._request(data, s)

    def receive_minimum_set(self, amount: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#receive_minimum_set"
        data: dict[str, Any] = {}
        data["action"] = "receive_minimum_set"
        data["amount"] = amount
        s = RPC._Dict({"success": RPC._ZO}) | RPC._Req(["success"])
        return self._request(data, s)

    def search_receivable(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#search_receivable"
        data: dict[str, Any] = {}
        data["action"] = "search_receivable"
        data["wallet"] = wallet
        s = RPC._Dict({"started": RPC._ZO}) | RPC._Req(["started"])
        return self._request(data, s)

    def search_receivable_all(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#search_receivable_all"
        data: dict[str, Any] = {}
        data["action"] = "search_receivable_all"
        s = RPC._Dict({"success": RPC._ZO}) | RPC._Req(["success"])
        return self._request(data, s)

    def send(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        wallet: str,
        source: str,
        destination: str,
        amount: str,
        _id: str = "",
        work: str = "",
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#send"
        data: dict[str, Any] = {}
        data["action"] = "send"
        data["wallet"] = wallet
        data["source"] = source
        data["destination"] = destination
        data["amount"] = amount
        if _id:
            data["id"] = _id
        if work:
            data["work"] = work
        s = RPC._Dict({"block": RPC._H64}) | RPC._Req(["block"])
        return self._request(data, s)

    def wallet_add(self, wallet: str, key: str, work: bool = False) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_add"
        data: dict[str, Any] = {}
        data["action"] = "wallet_add"
        data["wallet"] = wallet
        data["key"] = key
        if work:
            data["work"] = True
        s = RPC._Dict({"account": RPC._Acc}) | RPC._Req(["account"])
        return self._request(data, s)

    def wallet_add_watch(self, wallet: str, accounts: list[str]) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_add_watch"
        data: dict[str, Any] = {}
        data["action"] = "wallet_add_watch"
        data["wallet"] = wallet
        data["accounts"] = accounts
        s = RPC._Dict({"success": RPC._ZO}) | RPC._Req(["success"])
        return self._request(data, s)

    def wallet_balances(self, wallet: str, threshold: int = 0) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_balances"
        data: dict[str, Any] = {}
        data["action"] = "wallet_balances"
        data["wallet"] = wallet
        if threshold:
            data["threshold"] = threshold
        s = RPC._Dict(
            {
                "balances": RPC._DictP(
                    {
                        RPC._AccP: RPC._Dict(
                            {
                                "balance": RPC._UInt,
                                "pending": RPC._UInt,
                                "receivable": RPC._UInt,
                            }
                        )
                    }
                )
            }
        ) | RPC._Req(["balances"])
        return self._request(data, s)

    def wallet_change_seed(self, wallet: str, seed: str, count: int = 0) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_change_seed"
        data: dict[str, Any] = {}
        data["action"] = "wallet_change_seed"
        data["wallet"] = wallet
        data["seed"] = seed
        if count:
            data["count"] = count
        s = RPC._Dict({"success": RPC._ZO}) | RPC._Req(["success"])
        return self._request(data, s)

    def wallet_contains(self, wallet: str, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_contains"
        data: dict[str, Any] = {}
        data["action"] = "wallet_contains"
        data["wallet"] = wallet
        data["account"] = account
        s = RPC._Dict({"exists": RPC._ZO}) | RPC._Req(["exists"])
        return self._request(data, s)

    def wallet_create(self, seed: str = "") -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_create"
        data: dict[str, Any] = {}
        data["action"] = "wallet_create"
        if seed:
            data["seed"] = seed
        s = RPC._Dict({"wallet": RPC._H64}) | RPC._Req(["wallet"])
        return self._request(data, s)

    def wallet_destroy(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_destroy"
        data: dict[str, Any] = {}
        data["action"] = "wallet_destroy"
        data["wallet"] = wallet
        s = RPC._Dict({"destroyed": RPC._ZO}) | RPC._Req(["destroyed"])
        return self._request(data, s)

    def wallet_export(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_export"
        data: dict[str, Any] = {}
        data["action"] = "wallet_export"
        data["wallet"] = wallet
        return self._request(data)

    def wallet_frontiers(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_frontiers"
        data: dict[str, Any] = {}
        data["action"] = "wallet_frontiers"
        data["wallet"] = wallet
        s = RPC._Dict({"frontiers": RPC._DictP({RPC._AccP: RPC._H64})}) | RPC._Req(
            ["frontiers"]
        )
        return self._request(data, s)

    def wallet_history(self, wallet: str, modified_since: int = 0) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_history"
        data: dict[str, Any] = {}
        data["action"] = "wallet_history"
        data["wallet"] = wallet
        if modified_since:
            data["modified_since"] = modified_since
        s = RPC._Dict(
            {
                "history": RPC._List(
                    RPC._Dict(
                        {
                            "type": RPC._Type,
                            "account": RPC._Acc,
                            "amount": RPC._UInt,
                            "block_account": RPC._Acc,
                            "hash": RPC._H64,
                            "local_timestamp": RPC._UInt,
                        }
                    )
                )
            }
        ) | RPC._Req(["history"])
        return self._request(data, s)

    def wallet_info(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_info"
        data: dict[str, Any] = {}
        data["action"] = "wallet_info"
        data["wallet"] = wallet
        s = RPC._Dict(
            {
                "balance": RPC._UInt,
                "pending": RPC._UInt,
                "receivable": RPC._UInt,
                "accounts_count": RPC._UInt,
                "adhoc_count": RPC._UInt,
                "deterministic_count": RPC._UInt,
                "deterministic_index": RPC._UInt,
                "accounts_block_count": RPC._UInt,
                "accounts_cemented_block_count": RPC._UInt,
            }
        ) | RPC._Req(
            [
                "balance",
                "pending",
                "receivable",
                "accounts_count",
                "adhoc_count",
                "deterministic_count",
                "deterministic_index",
                "accounts_block_count",
                "accounts_cemented_block_count",
            ]
        )
        return self._request(data, s)

    def wallet_ledger(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        wallet: str,
        representative: bool = False,
        weight: bool = False,
        receivable: bool = False,
        modified_since: str = "",
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_ledger"
        data: dict[str, Any] = {}
        data["action"] = "wallet_ledger"
        data["wallet"] = wallet
        if representative:
            data["representative"] = True
        if weight:
            data["weight"] = True
        if receivable:
            data["receivable"] = True
        if modified_since:
            data["modified_since"] = modified_since
        s = RPC._Dict(
            {
                "accounts": RPC._DictP(
                    {
                        RPC._AccP: RPC._Dict(
                            {
                                "frontier": RPC._H64,
                                "open_block": RPC._H64,
                                "representative_block": RPC._H64,
                                "balance": RPC._UInt,
                                "modified_timestamp": RPC._UInt,
                                "block_count": RPC._UInt,
                            }
                        )
                    }
                )
            }
        ) | RPC._Req(["accounts"])
        return self._request(data, s)

    def wallet_lock(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_lock"
        data: dict[str, Any] = {}
        data["action"] = "wallet_lock"
        data["wallet"] = wallet
        s = RPC._Dict({"locked": RPC._ZO}) | RPC._Req(["locked"])
        return self._request(data, s)

    def wallet_locked(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_locked"
        data: dict[str, Any] = {}
        data["action"] = "wallet_locked"
        data["wallet"] = wallet
        s = RPC._Dict({"locked": RPC._ZO}) | RPC._Req(["locked"])
        return self._request(data, s)

    def wallet_receivable(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        wallet: str,
        count: int = 1,
        threshold: int = 0,
        source: bool = False,
        include_active: bool = False,
        min_version: bool = False,
        include_only_confirmed: bool = True,
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_receivable"
        data: dict[str, Any] = {}
        data["action"] = "wallet_receivable"
        data["wallet"] = wallet
        data["count"] = count
        if threshold:
            data["threshold"] = threshold
        if source:
            data["source"] = True
        if include_active:
            data["include_active"] = True
        if min_version:
            data["min_version"] = True
        if not include_only_confirmed:
            data["include_only_confirmed"] = False
        s = RPC._Dict(
            {
                "blocks": RPC._DictP(
                    {
                        RPC._AccP: {
                            "anyOf": [
                                RPC._List(RPC._H64),
                                RPC._DictP(
                                    {
                                        RPC._H64P: {
                                            "anyOf": [
                                                RPC._UInt,
                                                RPC._Dict(
                                                    {
                                                        "amount": RPC._UInt,
                                                        "source": RPC._Acc,
                                                    }
                                                ),
                                            ]
                                        }
                                    }
                                ),
                            ]
                        }
                    }
                )
            }
        ) | RPC._Req(["blocks"])
        return self._request(data, s)

    def wallet_representative(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_representative"
        data: dict[str, Any] = {}
        data["action"] = "wallet_representative"
        data["wallet"] = wallet
        s = RPC._Dict({"representative": RPC._Acc}) | RPC._Req(["representative"])
        return self._request(data, s)

    def wallet_representative_set(
        self, wallet: str, representative: str, update_existing_accounts: bool = False
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_representative_set"
        data: dict[str, Any] = {}
        data["action"] = "wallet_representative_set"
        data["wallet"] = wallet
        data["representative"] = representative
        if update_existing_accounts:
            data["update_existing_accounts"] = True
        s = RPC._Dict({"set": RPC._ZO}) | RPC._Req(["set"])
        return self._request(data, s)

    def wallet_republish(self, wallet: str, count: int = 1) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_republish"
        data: dict[str, Any] = {}
        data["action"] = "wallet_republish"
        data["wallet"] = wallet
        data["count"] = count
        s = RPC._Dict({"blocks": RPC._List(RPC._H64)}) | RPC._Req(["blocks"])
        return self._request(data, s)

    def wallet_work_get(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_work_get"
        data: dict[str, Any] = {}
        data["action"] = "wallet_workget"
        data["wallet"] = wallet
        s = RPC._Dict({"works": RPC._DictP({RPC._AccP: RPC._H16})}) | RPC._Req(
            ["works"]
        )
        return self._request(data, s)

    def work_get(self, wallet: str, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#workget"
        data: dict[str, Any] = {}
        data["action"] = "workget"
        data["wallet"] = wallet
        data["account"] = account
        s = RPC._Dict({"work": RPC._H16}) | RPC._Req(["work"])
        return self._request(data, s)

    def work_set(self, wallet: str, account: str, work: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#work_set"
        data: dict[str, Any] = {}
        data["action"] = "work_set"
        data["wallet"] = wallet
        data["account"] = account
        data["work"] = work
        s = RPC._Dict({"success": RPC._ZO}) | RPC._Req(["success"])
        return self._request(data, s)

    def nano_to_raw(self, amount: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#nano_to_raw"
        data: dict[str, Any] = {}
        data["action"] = "nano_to_raw"
        data["amount"] = amount
        s = RPC._Dict({"amount": RPC._UInt}) | RPC._Req(["amount"])
        return self._request(data, s)

    def raw_to_nano(self, amount: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#raw_to_nano"
        data: dict[str, Any] = {}
        data["action"] = "raw_to_nano"
        data["amount"] = amount
        s = RPC._Dict({"amount": RPC._UInt}) | RPC._Req(["amount"])
        return self._request(data, s)


class HTTP(RPC):
    """HTTP RPC class

    :arg url: URL of the nano node
    """

    def __init__(self, url: str = "http://localhost:7076"):
        self.url = url
        self.api = requests.session()

    def request(self, data: dict[str, Any]) -> Any:
        r = self.api.post(self.url, json=data)
        r.raise_for_status()
        return r.json()


class WS(RPC):
    """WS RPC class

    :arg url: URL of the nano node
    """

    def __init__(self, url: str = "ws://localhost:7078"):
        self.api = websocket.create_connection(url)

    def __del__(self) -> None:
        self.api.close()

    def request(self, data: dict[str, Any]) -> Any:
        self.api.send(json.dumps(data))
        r = json.loads(self.api.recv())
        return r
