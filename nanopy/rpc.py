"""
nanopy.rpc
##########
A wrapper to make RPC requests to a node.
"""

from abc import ABC, abstractmethod  # pragma: no cover
from typing import Any  # pragma: no cover
import json  # pragma: no cover
import requests  # pragma: no cover
import websocket  # pragma: no cover


class RPC(ABC):  # pragma: no cover
    "RPC base class"

    @abstractmethod
    def request(self, data: Any) -> Any:
        "Make request to nano node. Implemented in derived classes."
        raise NotImplementedError("Implement in a derived class")

    def account_balance(self, account: str, include_only_confirmed: bool = True) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_balance"
        data: dict[str, Any] = {}
        data["action"] = "account_balance"
        data["account"] = account
        if not include_only_confirmed:
            data["include_only_confirmed"] = False
        return self.request(data)

    def account_block_count(self, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_block_count"
        data: dict[str, Any] = {}
        data["action"] = "account_block_count"
        data["account"] = account
        return self.request(data)

    def accountget(self, key: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#accountget"
        data: dict[str, Any] = {}
        data["action"] = "accountget"
        data["key"] = key
        return self.request(data)

    def account_history(
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
        return self.request(data)

    def account_info(
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
        return self.request(data)

    def account_key(self, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_key"
        data: dict[str, Any] = {}
        data["action"] = "account_key"
        data["account"] = account
        return self.request(data)

    def account_representative(self, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_representative"
        data: dict[str, Any] = {}
        data["action"] = "account_representative"
        data["account"] = account
        return self.request(data)

    def account_weight(self, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_weight"
        data: dict[str, Any] = {}
        data["action"] = "account_weight"
        data["account"] = account
        return self.request(data)

    def accounts_balances(
        self, accounts: list[str], include_only_confirmed: bool = True
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#accounts_balances"
        data: dict[str, Any] = {}
        data["action"] = "accounts_balances"
        data["accounts"] = accounts
        if not include_only_confirmed:
            data["include_only_confirmed"] = False
        return self.request(data)

    def accounts_frontiers(self, accounts: list[str]) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#accounts_frontiers"
        data: dict[str, Any] = {}
        data["action"] = "accounts_frontiers"
        data["accounts"] = accounts
        return self.request(data)

    def accounts_receivable(
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
        return self.request(data)

    def accounts_representatives(self, accounts: list[str]) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#accounts_representatives"
        data: dict[str, Any] = {}
        data["action"] = "accounts_representatives"
        data["accounts"] = accounts
        return self.request(data)

    def available_supply(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#available_supply"
        data: dict[str, Any] = {}
        data["action"] = "available_supply"
        return self.request(data)

    def block_account(self, _hash: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#block_account"
        data: dict[str, Any] = {}
        data["action"] = "block_account"
        data["hash"] = _hash
        return self.request(data)

    def block_confirm(self, _hash: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#block_confirm"
        data: dict[str, Any] = {}
        data["action"] = "block_confirm"
        data["hash"] = _hash
        return self.request(data)

    def block_count(self, include_cemented: bool = True) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#block_count"
        data: dict[str, Any] = {}
        data["action"] = "block_count"
        if not include_cemented:
            data["include_cemented"] = False
        return self.request(data)

    def block_create(
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
        json_block: bool = False,
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
        if json_block:
            data["json_block"] = True
        return self.request(data)

    def block_hash(self, block: dict[str, str], json_block: bool = False) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#block_hash"
        data: dict[str, Any] = {}
        data["action"] = "block_hash"
        data["block"] = block
        if json_block:
            data["json_block"] = True
        return self.request(data)

    def block_info(
        self, _hash: str, json_block: bool = False, include_linked_account: bool = False
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#block_info"
        data: dict[str, Any] = {}
        data["action"] = "block_info"
        data["hash"] = _hash
        if json_block:
            data["json_block"] = True
        if include_linked_account:
            data["include_linked_account"] = True
        return self.request(data)

    def blocks(self, hashes: list[str], json_block: bool = False) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#blocks"
        data: dict[str, Any] = {}
        data["action"] = "blocks"
        data["hashes"] = hashes
        if json_block:
            data["json_block"] = True
        return self.request(data)

    def blocks_info(
        self,
        hashes: list[str],
        include_linked_account: bool = False,
        pending: bool = False,
        source: bool = False,
        receive_hash: bool = False,
        json_block: bool = False,
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
        if json_block:
            data["json_block"] = True
        if include_not_found:
            data["include_not_found"] = True
        return self.request(data)

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
        return self.request(data)

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
        return self.request(data)

    def bootstrap_lazy(self, hash_: str, force: bool = False, _id: str = "") -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#bootstrap_lazy"
        data: dict[str, Any] = {}
        data["action"] = "bootstrap_lazy"
        data["hash"] = hash_
        if force:
            data["force"] = True
        if _id:
            data["id"] = _id
        return self.request(data)

    def bootstrap_priorities(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#bootstrap_priorities"
        data: dict[str, Any] = {}
        data["action"] = "bootstrap_priorities"
        return self.request(data)

    def bootstrap_reset(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#bootstrap_reset"
        data: dict[str, Any] = {}
        data["action"] = "bootstrap_reset"
        return self.request(data)

    def bootstrap_status(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#bootstrap_status"
        data: dict[str, Any] = {}
        data["action"] = "bootstrap_status"
        return self.request(data)

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
        return self.request(data)

    def confirmation_active(self, announcements: int = 0) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#confirmation_active"
        data: dict[str, Any] = {}
        data["action"] = "confirmation_active"
        if announcements:
            data["announcements"] = announcements
        return self.request(data)

    def confirmation_height_currently_processing(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#confirmation_height_currently_processing"
        data: dict[str, Any] = {}
        data["action"] = "confirmation_height_currently_processing"
        return self.request(data)

    def confirmation_history(self, _hash: str = "") -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#confirmation_history"
        data: dict[str, Any] = {}
        data["action"] = "confirmation_history"
        if _hash:
            data["hash"] = _hash
        return self.request(data)

    def confirmation_info(
        self,
        root: str,
        contents: bool = True,
        representatives: bool = False,
        json_block: bool = False,
    ) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#confirmation_info"
        data: dict[str, Any] = {}
        data["action"] = "confirmation_info"
        data["root"] = root
        if not contents:
            data["contents"] = False
        if representatives:
            data["representatives"] = True
        if json_block:
            data["json_block"] = True
        return self.request(data)

    def confirmation_quorum(self, peer_details: bool = False) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#confirmation_quorum"
        data: dict[str, Any] = {}
        data["action"] = "confirmation_quorum"
        if peer_details:
            data["peer_details"] = True
        return self.request(data)

    def database_txn_tracker(self, min_read_time: int, min_write_time: int) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#database_txn_tracker"
        data: dict[str, Any] = {}
        data["action"] = "database_txn_tracker"
        data["min_read_time"] = min_read_time
        data["min_write_time"] = min_write_time
        return self.request(data)

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
        return self.request(data)

    def delegators_count(self, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#delegators_count"
        data: dict[str, Any] = {}
        data["action"] = "delegators_count"
        data["account"] = account
        return self.request(data)

    def deterministic_key(self, seed: str, index: int) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#deterministic_key"
        data: dict[str, Any] = {}
        data["action"] = "deterministic_key"
        data["seed"] = seed
        data["index"] = index
        return self.request(data)

    def election_statistics(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#election_statistics"
        data: dict[str, Any] = {}
        data["action"] = "election_statistics"
        return self.request(data)

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
        return self.request(data)

    def frontier_count(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#frontier_count"
        data: dict[str, Any] = {}
        data["action"] = "frontier_count"
        return self.request(data)

    def frontiers(self, account: str, count: int = 1) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#frontiers"
        data: dict[str, Any] = {}
        data["action"] = "frontiers"
        data["account"] = account
        data["count"] = count
        return self.request(data)

    def keepalive(self, address: str, port: int) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#keepalive"
        data: dict[str, Any] = {}
        data["action"] = "keepalive"
        data["address"] = address
        data["port"] = port
        return self.request(data)

    def key_create(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#key_create"
        data: dict[str, Any] = {}
        data["action"] = "key_create"
        return self.request(data)

    def key_expand(self, key: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#key_expand"
        data: dict[str, Any] = {}
        data["action"] = "key_expand"
        data["key"] = key
        return self.request(data)

    def ledger(
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
        return self.request(data)

    def node_id(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#node_id"
        data: dict[str, Any] = {}
        data["action"] = "node_id"
        return self.request(data)

    def node_id_delete(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#node_id_delete"
        data: dict[str, Any] = {}
        data["action"] = "node_id_delete"
        return self.request(data)

    def peers(self, peer_details: bool = False) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#peers"
        data: dict[str, Any] = {}
        data["action"] = "peers"
        if peer_details:
            data["peer_details"] = True
        return self.request(data)

    def populate_backlog(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#populate_backlog"
        data: dict[str, Any] = {}
        data["action"] = "populate_backlog"
        return self.request(data)

    def process(
        self,
        block: str | dict[str, str],
        force: bool = False,
        subtype: str = "",
        json_block: bool = False,
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
        if json_block:
            data["json_block"] = True
        if not watch_work:
            data["watch_work"] = False
        if _async:
            data["async"] = True
        return self.request(data)

    def receivable(
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
        return self.request(data)

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
        return self.request(data)

    def representatives(self, count: int = 1, sorting: bool = False) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#representatives"
        data: dict[str, Any] = {}
        data["action"] = "representatives"
        data["count"] = count
        if sorting:
            data["sorting"] = True
        return self.request(data)

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
        return self.request(data)

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
        return self.request(data)

    def sign(
        self,
        key: str = "",
        wallet: str = "",
        account: str = "",
        block: str = "",
        _hash: str = "",
        json_block: bool = False,
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
        if json_block:
            data["json_block"] = True
        return self.request(data)

    def stats(self, _type: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#stats"
        data: dict[str, Any] = {}
        data["action"] = "stats"
        data["type"] = _type
        return self.request(data)

    def stats_clear(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#stats_clear"
        data: dict[str, Any] = {}
        data["action"] = "stats_clear"
        return self.request(data)

    def stop(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#stop"
        data: dict[str, Any] = {}
        data["action"] = "stop"
        return self.request(data)

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
        return self.request(data)

    def telemetry(self, raw: bool = False, address: int = 0, port: int = 7075) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#telemetry"
        data: dict[str, Any] = {}
        data["action"] = "telemetry"
        if raw:
            data["raw"] = True
        if address:
            data["address"] = address
            data["port"] = port
        return self.request(data)

    def validate_account_number(self, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#validate_account_number"
        data: dict[str, Any] = {}
        data["action"] = "validate_account_number"
        data["account"] = account
        return self.request(data)

    def version(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#version"
        data: dict[str, Any] = {}
        data["action"] = "version"
        return self.request(data)

    def unchecked(self, json_block: bool = False, count: int = 1) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#unchecked"
        data: dict[str, Any] = {}
        data["action"] = "unchecked"
        if json_block:
            data["json_block"] = True
        data["count"] = count
        return self.request(data)

    def unchecked_clear(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#unchecked_clear"
        data: dict[str, Any] = {}
        data["action"] = "unchecked_clear"
        return self.request(data)

    def uncheckedget(self, _hash: str, json_block: bool = False) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#uncheckedget"
        data: dict[str, Any] = {}
        data["action"] = "uncheckedget"
        data["hash"] = _hash
        if json_block:
            data["json_block"] = True
        return self.request(data)

    def unchecked_keys(self, key: str, count: int = 1, json_block: bool = False) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#unchecked_keys"
        data: dict[str, Any] = {}
        data["action"] = "unchecked_keys"
        data["key"] = key
        data["count"] = count
        if json_block:
            data["json_block"] = True
        return self.request(data)

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
        return self.request(data)

    def uptime(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#uptime"
        data: dict[str, Any] = {}
        data["action"] = "uptime"
        return self.request(data)

    def work_cancel(self, _hash: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#work_cancel"
        data: dict[str, Any] = {}
        data["action"] = "work_cancel"
        data["hash"] = _hash
        return self.request(data)

    def work_generate(
        self,
        _hash: str,
        use_peers: bool = False,
        difficulty: str = "",
        multiplier: int = 0,
        account: str = "",
        version: str = "work_1",
        block: str = "",
        json_block: bool = False,
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
            if json_block:
                data["json_block"] = json_block
        return self.request(data)

    def work_peer_add(self, address: str, port: int) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#work_peer_add"
        data: dict[str, Any] = {}
        data["action"] = "work_peer_add"
        data["address"] = address
        data["port"] = port
        return self.request(data)

    def work_peers(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#work_peers"
        data: dict[str, Any] = {}
        data["action"] = "work_peers"
        return self.request(data)

    def work_peers_clear(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#work_peers_clear"
        data: dict[str, Any] = {}
        data["action"] = "work_peers_clear"
        return self.request(data)

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
        return self.request(data)

    def account_create(self, wallet: str, index: int = 0, work: bool = True) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_create"
        data: dict[str, Any] = {}
        data["action"] = "account_create"
        data["wallet"] = wallet
        if index:
            data["index"] = index
        if not work:
            data["work"] = False
        return self.request(data)

    def account_list(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_list"
        data: dict[str, Any] = {}
        data["action"] = "account_list"
        data["wallet"] = wallet
        return self.request(data)

    def account_move(self, wallet: str, source: str, accounts: list[str]) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_move"
        data: dict[str, Any] = {}
        data["action"] = "account_move"
        data["wallet"] = wallet
        data["source"] = source
        data["accounts"] = accounts
        return self.request(data)

    def account_remove(self, wallet: str, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#account_remove"
        data: dict[str, Any] = {}
        data["action"] = "account_remove"
        data["wallet"] = wallet
        data["account"] = account
        return self.request(data)

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
        return self.request(data)

    def accounts_create(self, wallet: str, count: int = 1, work: bool = True) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#accounts_create"
        data: dict[str, Any] = {}
        data["action"] = "accounts_create"
        data["wallet"] = wallet
        data["count"] = count
        if not work:
            data["work"] = False
        return self.request(data)

    def password_change(self, wallet: str, password: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#password_change"
        data: dict[str, Any] = {}
        data["action"] = "password_change"
        data["wallet"] = wallet
        data["password"] = password
        return self.request(data)

    def password_enter(self, wallet: str, password: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#password_enter"
        data: dict[str, Any] = {}
        data["action"] = "password_enter"
        data["wallet"] = wallet
        data["password"] = password
        return self.request(data)

    def password_valid(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#password_valid"
        data: dict[str, Any] = {}
        data["action"] = "password_valid"
        data["wallet"] = wallet
        return self.request(data)

    def receive(self, wallet: str, account: str, block: str, work: str = "") -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#receive"
        data: dict[str, Any] = {}
        data["action"] = "receive"
        data["wallet"] = wallet
        data["account"] = account
        data["block"] = block
        if work:
            data["work"] = work
        return self.request(data)

    def receive_minimum(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#receive_minimum"
        data: dict[str, Any] = {}
        data["action"] = "receive_minimum"
        return self.request(data)

    def receive_minimum_set(self, amount: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#receive_minimum_set"
        data: dict[str, Any] = {}
        data["action"] = "receive_minimum_set"
        data["amount"] = amount
        return self.request(data)

    def search_receivable(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#search_receivable"
        data: dict[str, Any] = {}
        data["action"] = "search_receivable"
        data["wallet"] = wallet
        return self.request(data)

    def search_receivable_all(self) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#search_receivable_all"
        data: dict[str, Any] = {}
        data["action"] = "search_receivable_all"
        return self.request(data)

    def send(
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
        return self.request(data)

    def wallet_add(self, wallet: str, key: str, work: bool = False) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_add"
        data: dict[str, Any] = {}
        data["action"] = "wallet_add"
        data["wallet"] = wallet
        data["key"] = key
        if work:
            data["work"] = True
        return self.request(data)

    def wallet_add_watch(self, wallet: str, accounts: list[str]) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_add_watch"
        data: dict[str, Any] = {}
        data["action"] = "wallet_add_watch"
        data["wallet"] = wallet
        data["accounts"] = accounts
        return self.request(data)

    def wallet_balances(self, wallet: str, threshold: int = 0) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_balances"
        data: dict[str, Any] = {}
        data["action"] = "wallet_balances"
        data["wallet"] = wallet
        if threshold:
            data["threshold"] = threshold
        return self.request(data)

    def wallet_change_seed(self, wallet: str, seed: str, count: int = 0) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_change_seed"
        data: dict[str, Any] = {}
        data["action"] = "wallet_change_seed"
        data["wallet"] = wallet
        data["seed"] = seed
        if count:
            data["count"] = count
        return self.request(data)

    def wallet_contains(self, wallet: str, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_contains"
        data: dict[str, Any] = {}
        data["action"] = "wallet_contains"
        data["wallet"] = wallet
        data["account"] = account
        return self.request(data)

    def wallet_create(self, seed: str = "") -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_create"
        data: dict[str, Any] = {}
        data["action"] = "wallet_create"
        if seed:
            data["seed"] = seed
        return self.request(data)

    def wallet_destroy(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_destroy"
        data: dict[str, Any] = {}
        data["action"] = "wallet_destroy"
        data["wallet"] = wallet
        return self.request(data)

    def wallet_export(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_export"
        data: dict[str, Any] = {}
        data["action"] = "wallet_export"
        data["wallet"] = wallet
        return self.request(data)

    def wallet_frontiers(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_frontiers"
        data: dict[str, Any] = {}
        data["action"] = "wallet_frontiers"
        data["wallet"] = wallet
        return self.request(data)

    def wallet_history(self, wallet: str, modified_since: int = 0) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_history"
        data: dict[str, Any] = {}
        data["action"] = "wallet_history"
        data["wallet"] = wallet
        if modified_since:
            data["modified_since"] = modified_since
        return self.request(data)

    def wallet_info(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_info"
        data: dict[str, Any] = {}
        data["action"] = "wallet_info"
        data["wallet"] = wallet
        return self.request(data)

    def wallet_ledger(
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
        return self.request(data)

    def wallet_lock(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_lock"
        data: dict[str, Any] = {}
        data["action"] = "wallet_lock"
        data["wallet"] = wallet
        return self.request(data)

    def wallet_locked(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_locked"
        data: dict[str, Any] = {}
        data["action"] = "wallet_locked"
        data["wallet"] = wallet
        return self.request(data)

    def wallet_receivable(
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
        return self.request(data)

    def wallet_representative(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_representative"
        data: dict[str, Any] = {}
        data["action"] = "wallet_representative"
        data["wallet"] = wallet
        return self.request(data)

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
        return self.request(data)

    def wallet_republish(self, wallet: str, count: int = 1) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_republish"
        data: dict[str, Any] = {}
        data["action"] = "wallet_republish"
        data["wallet"] = wallet
        data["count"] = count
        return self.request(data)

    def wallet_work_get(self, wallet: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#wallet_work_get"
        data: dict[str, Any] = {}
        data["action"] = "wallet_workget"
        data["wallet"] = wallet
        return self.request(data)

    def work_get(self, wallet: str, account: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#workget"
        data: dict[str, Any] = {}
        data["action"] = "workget"
        data["wallet"] = wallet
        data["account"] = account
        return self.request(data)

    def work_set(self, wallet: str, account: str, work: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#work_set"
        data: dict[str, Any] = {}
        data["action"] = "work_set"
        data["wallet"] = wallet
        data["account"] = account
        data["work"] = work
        return self.request(data)

    def nano_to_raw(self, amount: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#nano_to_raw"
        data: dict[str, Any] = {}
        data["action"] = "nano_to_raw"
        data["amount"] = amount
        return self.request(data)

    def raw_to_nano(self, amount: str) -> Any:
        "https://docs.nano.org/commands/rpc-protocol/#raw_to_nano"
        data: dict[str, Any] = {}
        data["action"] = "raw_to_nano"
        data["amount"] = amount
        return self.request(data)


class HTTP(RPC):  # pragma: no cover
    """HTTP RPC class

    :arg url: URL of the nano node
    """

    def __init__(self, url: str = "http://localhost:7076"):
        self.url = url
        self.api = requests.session()

    def get(self) -> Any:
        """JSON GET request

        :return: JSON reponse as dict
        """
        r = self.api.get(self.url)
        r.raise_for_status()
        return r.json()

    def post(self, data: Any) -> Any:
        """JSON POST request

        :arg data: dict like object
        :return: JSON reponse as dict
        """
        r = self.api.post(self.url, json=data)
        r.raise_for_status()
        return r.json()

    def request(self, data: Any) -> Any:
        """Make HTTP POST RPC request to nano node.
        Overridden from base class RPC

        :arg data: dict like object
        :return: JSON reponse as dict
        """
        return self.post(data)


class WS(RPC):  # pragma: no cover
    """WS RPC class

    :arg url: URL of the nano node
    """

    def __init__(self, url: str = "ws://localhost:7078"):
        self.api = websocket.create_connection(url)

    def __del__(self) -> None:
        self.api.close()

    def request(self, data: Any) -> Any:
        """Make JSON WS request.
        Overridden from base class RPC

        :arg data: dict like object
        :return: JSON reponse as dict
        """
        self.api.send(json.dumps(data))
        return json.loads(self.api.recv())
