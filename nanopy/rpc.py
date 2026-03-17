"""
nanopy.rpc
##########
A wrapper to make RPC requests to a node. Requires `requests <https://pypi.org/project/requests>`_. Additionally,  `websocket-client <https://pypi.org/project/websocket-client>`_ for websocket connections, and `pysocks <https://pypi.org/project/pysocks>`_ for connecting via TOR network.
"""

import json, requests


class RPC:
    """RPC class

    :arg str url: URL of the nano node
    :arg dict headers: Optional headers for the RPC requests
    :arg bool tor: Whether to connect via TOR network.

    Refer `docs <https://docs.nano.org/commands/rpc-protocol>`_ for information on methods.

    Return type is ``dict`` for all methods except ``disconnect``.
    """

    def __init__(self, url="http://localhost:7076", headers={}, tor=False):
        if url[:7] == "http://" or url[:8] == "https://":
            self.__mode = "requests"
            self.API = requests.session()
            self.API.proxies = {}
            if tor:
                self.API.proxies["http"] = self.API.proxies["https"] = (
                    "socks5h://localhost:9050"
                )
        elif url[:5] == "ws://" or url[:6] == "wss://":
            from websocket import create_connection

            self.__mode = "websockets"
            if tor:
                self.API = create_connection(
                    url,
                    http_proxy_host="localhost",
                    http_proxy_port=9050,
                    proxy_type="socks5h",
                )
            else:
                self.API = create_connection(url)
            self.API.settimeout(20.0)
        else:
            raise Exception("Unable to parse url: " + url)
        self.__url = url
        self.__headers = headers

    def _get(self):
        if self.__mode == "requests":
            response = self.API.get(self.__url, headers=self.__headers)
            response.raise_for_status()
            return response.json()

    def _post(self, data):
        if self.__mode == "requests":
            response = self.API.post(self.__url, json=data, headers=self.__headers)
            response.raise_for_status()
            return response.json()
        elif self.__mode == "websockets":
            self.API.send(json.dumps(data))
            response = self.API.recv()
            return json.loads(response)

    def disconnect(self):
        "Close RPC connection. Only necessary for websocket connections."
        if self.__mode == "websockets":
            self.API.close()

    # Node RPCs

    def account_balance(self, account, include_only_confirmed=True):
        "https://docs.nano.org/commands/rpc-protocol/#account_balance"
        data = {}
        data["action"] = "account_balance"
        data["account"] = account
        if not include_only_confirmed:
            data["include_only_confirmed"] = False
        return self._post(data)

    def account_block_count(self, account):
        "https://docs.nano.org/commands/rpc-protocol/#account_block_count"
        data = {}
        data["action"] = "account_block_count"
        data["account"] = account
        return self._post(data)

    def account_get(self, key):
        "https://docs.nano.org/commands/rpc-protocol/#account_get"
        data = {}
        data["action"] = "account_get"
        data["key"] = key
        return self._post(data)

    def account_history(
        self,
        account,
        count=1,
        raw=False,
        head=None,
        offset=0,
        reverse=False,
        account_filter=[],
    ):
        "https://docs.nano.org/commands/rpc-protocol/#account_history"
        data = {}
        data["action"] = "account_history"
        data["account"] = account
        data["count"] = count
        if raw:
            data["raw"] = True
        if head:
            data["head"] = head
        if offset:
            data["offset"] = offset
        if reverse:
            data["reverse"] = reverse
        if account_filter:
            data["account_filter"] = account_filter
        return self._post(data)

    def account_info(
        self,
        account,
        include_confirmed=False,
        representative=False,
        weight=False,
        pending=False,
    ):
        "https://docs.nano.org/commands/rpc-protocol/#account_info"
        data = {}
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
        return self._post(data)

    def account_key(self, account):
        "https://docs.nano.org/commands/rpc-protocol/#account_key"
        data = {}
        data["action"] = "account_key"
        data["account"] = account
        return self._post(data)

    def account_representative(self, account):
        "https://docs.nano.org/commands/rpc-protocol/#account_representative"
        data = {}
        data["action"] = "account_representative"
        data["account"] = account
        return self._post(data)

    def account_weight(self, account):
        "https://docs.nano.org/commands/rpc-protocol/#account_weight"
        data = {}
        data["action"] = "account_weight"
        data["account"] = account
        return self._post(data)

    def accounts_balances(self, accounts, include_only_confirmed=True):
        "https://docs.nano.org/commands/rpc-protocol/#accounts_balances"
        data = {}
        data["action"] = "accounts_balances"
        data["accounts"] = accounts
        if not include_only_confirmed:
            data["include_only_confirmed"] = False
        return self._post(data)

    def accounts_frontiers(self, accounts):
        "https://docs.nano.org/commands/rpc-protocol/#accounts_frontiers"
        data = {}
        data["action"] = "accounts_frontiers"
        data["accounts"] = accounts
        return self._post(data)

    def accounts_receivable(
        self,
        accounts,
        count=1,
        threshold=None,
        source=False,
        include_active=False,
        sorting=False,
        include_only_confirmed=True,
    ):
        "https://docs.nano.org/commands/rpc-protocol/#accounts_receivable"
        data = {}
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
        return self._post(data)

    def accounts_representatives(self, accounts):
        "https://docs.nano.org/commands/rpc-protocol/#accounts_representatives"
        data = {}
        data["action"] = "accounts_representatives"
        data["accounts"] = accounts
        return self._post(data)

    def available_supply(self):
        "https://docs.nano.org/commands/rpc-protocol/#available_supply"
        data = {}
        data["action"] = "available_supply"
        return self._post(data)

    def block_account(self, _hash):
        "https://docs.nano.org/commands/rpc-protocol/#block_account"
        data = {}
        data["action"] = "block_account"
        data["hash"] = _hash
        return self._post(data)

    def block_confirm(self, _hash):
        "https://docs.nano.org/commands/rpc-protocol/#block_confirm"
        data = {}
        data["action"] = "block_confirm"
        data["hash"] = _hash
        return self._post(data)

    def block_count(self, include_cemented=True):
        "https://docs.nano.org/commands/rpc-protocol/#block_count"
        data = {}
        data["action"] = "block_count"
        if not include_cemented:
            data["include_cemented"] = False
        return self._post(data)

    def block_create(
        self,
        balance,
        representative,
        previous,
        wallet=None,
        account=None,
        key=None,
        source=None,
        destination=None,
        link=None,
        work=None,
        version="work_1",
        json_block=False,
        difficulty=None,
    ):
        "https://docs.nano.org/commands/rpc-protocol/#block_create"
        data = {}
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
        # Currently 'work_1' is the default and only valid option.
        # if version in []: data['version'] = version
        if json_block:
            data["json_block"] = True
        return self._post(data)

    def block_hash(self, block, json_block=False):
        "https://docs.nano.org/commands/rpc-protocol/#block_hash"
        data = {}
        data["action"] = "block_hash"
        if type(block) == str:
            data["block"] = block
        else:
            data["block"] = json.dumps(block)
        if json_block:
            data["json_block"] = True
        return self._post(data)

    def block_info(self, _hash, json_block=False):
        "https://docs.nano.org/commands/rpc-protocol/#block_info"
        data = {}
        data["action"] = "block_info"
        data["hash"] = _hash
        if json_block:
            data["json_block"] = True
        return self._post(data)

    def blocks(self, hashes, json_block=False):
        "https://docs.nano.org/commands/rpc-protocol/#blocks"
        data = {}
        data["action"] = "blocks"
        data["hashes"] = hashes
        if json_block:
            data["json_block"] = True
        return self._post(data)

    def blocks_info(
        self,
        hashes,
        pending=False,
        source=False,
        receive_hash=False,
        json_block=False,
        include_not_found=False,
    ):
        "https://docs.nano.org/commands/rpc-protocol/#blocks_info"
        data = {}
        data["action"] = "blocks_info"
        data["hashes"] = hashes
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
        return self._post(data)

    def bootstrap(self, address, port, bypass_frontier_confirmation=False, _id=""):
        "https://docs.nano.org/commands/rpc-protocol/#bootstrap"
        data = {}
        data["action"] = "bootstrap"
        data["address"] = address
        data["port"] = port
        if _id:
            data["id"] = _id
        return self._post(data)

    def bootstrap_any(self, force=False, _id="", account=""):
        "https://docs.nano.org/commands/rpc-protocol/#bootstrap_any"
        data = {}
        data["action"] = "bootstrap_any"
        if force:
            data["force"] = True
        if _id:
            data["id"] = _id
        if account:
            data["account"] = account
        return self._post(data)

    def bootstrap_lazy(self, hash_, force=False, _id=""):
        "https://docs.nano.org/commands/rpc-protocol/#bootstrap_lazy"
        data = {}
        data["action"] = "bootstrap_lazy"
        data["hash"] = hash_
        if force:
            data["force"] = True
        if _id:
            data["id"] = _id
        return self._post(data)

    def bootstrap_status(self):
        "https://docs.nano.org/commands/rpc-protocol/#bootstrap_status"
        data = {}
        data["action"] = "bootstrap_status"
        return self._post(data)

    def chain(self, block, count=1, offset=0, reverse=False):
        "https://docs.nano.org/commands/rpc-protocol/#chain"
        data = {}
        data["action"] = "chain"
        data["block"] = block
        data["count"] = count
        if offset:
            data["offset"] = offset
        if reverse:
            data["reverse"] = True
        return self._post(data)

    def confirmation_active(self, announcements=0):
        "https://docs.nano.org/commands/rpc-protocol/#confirmation_active"
        data = {}
        data["action"] = "confirmation_active"
        if announcements:
            data["announcements"] = announcements
        return self._post(data)

    def confirmation_height_currently_processing(self):
        "https://docs.nano.org/commands/rpc-protocol/#confirmation_height_currently_processing"
        data = {}
        data["action"] = "confirmation_height_currently_processing"
        return self._post(data)

    def confirmation_history(self, _hash=None):
        "https://docs.nano.org/commands/rpc-protocol/#confirmation_history"
        data = {}
        data["action"] = "confirmation_history"
        if _hash:
            data["hash"] = _hash
        return self._post(data)

    def confirmation_info(
        self, root, contents=True, representatives=False, json_block=False
    ):
        "https://docs.nano.org/commands/rpc-protocol/#confirmation_info"
        data = {}
        data["action"] = "confirmation_info"
        data["root"] = root
        if not contents:
            data["contents"] = False
        if representatives:
            data["representatives"] = True
        if json_block:
            data["json_block"] = True
        return self._post(data)

    def confirmation_quorum(self, peer_details=False):
        "https://docs.nano.org/commands/rpc-protocol/#confirmation_quorum"
        data = {}
        data["action"] = "confirmation_quorum"
        if peer_details:
            data["peer_details"] = True
        return self._post(data)

    def database_txn_tracker(self, min_read_time, min_write_time):
        "https://docs.nano.org/commands/rpc-protocol/#database_txn_tracker"
        data = {}
        data["action"] = "database_txn_tracker"
        data["min_read_time"] = min_read_time
        data["min_write_time"] = min_write_time
        return self._post(data)

    def delegators(self, account, threshold=0, count=0, start=""):
        "https://docs.nano.org/commands/rpc-protocol/#delegators"
        data = {}
        data["action"] = "delegators"
        data["account"] = account
        if threshold:
            data["threshold"] = threshold
        if count:
            data["count"] = count
        if start:
            data["start"] = start
        return self._post(data)

    def delegators_count(self, account):
        "https://docs.nano.org/commands/rpc-protocol/#delegators_count"
        data = {}
        data["action"] = "delegators_count"
        data["account"] = account
        return self._post(data)

    def deterministic_key(self, seed, index):
        "https://docs.nano.org/commands/rpc-protocol/#deterministic_key"
        data = {}
        data["action"] = "deterministic_key"
        data["seed"] = seed
        data["index"] = index
        return self._post(data)

    def election_statistics(self):
        "https://docs.nano.org/commands/rpc-protocol/#election_statistics"
        data = {}
        data["action"] = "election_statistics"
        return self._post(data)

    def epoch_upgrade(self, epoch, key, count=0, threads=0):
        "https://docs.nano.org/commands/rpc-protocol/#epoch_upgrade"
        data = {}
        data["action"] = "epoch_upgrade"
        data["epoch"] = epoch
        data["key"] = key
        if count:
            data["count"] = count
        if threads:
            data["threads"] = threads
        return self._post(data)

    def frontier_count(self):
        "https://docs.nano.org/commands/rpc-protocol/#frontier_count"
        data = {}
        data["action"] = "frontier_count"
        return self._post(data)

    def frontiers(self, account, count=1):
        "https://docs.nano.org/commands/rpc-protocol/#frontiers"
        data = {}
        data["action"] = "frontiers"
        data["account"] = account
        data["count"] = count
        return self._post(data)

    def keepalive(self, address, port):
        "https://docs.nano.org/commands/rpc-protocol/#keepalive"
        data = {}
        data["action"] = "keepalive"
        data["address"] = address
        data["port"] = port
        return self._post(data)

    def key_create(self):
        "https://docs.nano.org/commands/rpc-protocol/#key_create"
        data = {}
        data["action"] = "key_create"
        return self._post(data)

    def key_expand(self, key):
        "https://docs.nano.org/commands/rpc-protocol/#key_expand"
        data = {}
        data["action"] = "key_expand"
        data["key"] = key
        return self._post(data)

    def ledger(
        self,
        account,
        count=1,
        representative=False,
        weight=False,
        receivable=False,
        modified_since=0,
        sorting=False,
        threshold=0,
    ):
        "https://docs.nano.org/commands/rpc-protocol/#ledger"
        data = {}
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
        return self._post(data)

    def node_id(self):
        "https://docs.nano.org/commands/rpc-protocol/#node_id"
        data = {}
        data["action"] = "node_id"
        return self._post(data)

    def node_id_delete(self):
        "https://docs.nano.org/commands/rpc-protocol/#node_id_delete"
        data = {}
        data["action"] = "node_id_delete"
        return self._post(data)

    def peers(self, peer_details=False):
        "https://docs.nano.org/commands/rpc-protocol/#peers"
        data = {}
        data["action"] = "peers"
        if peer_details:
            data["peer_details"] = True
        return self._post(data)

    def populate_backlog(self):
        "https://docs.nano.org/commands/rpc-protocol/#populate_backlog"
        data = {}
        data["action"] = "populate_backlog"
        return self._post(data)

    def process(
        self,
        block,
        force=False,
        subtype=None,
        json_block=False,
        watch_work=True,
        _async=False,
    ):
        "https://docs.nano.org/commands/rpc-protocol/#process"
        data = {}
        data["action"] = "process"
        if type(block) == str:
            data["block"] = block
        else:
            data["block"] = json.dumps(block)
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
        return self._post(data)

    def receivable(
        self,
        account,
        count=0,
        threshold=0,
        source=False,
        include_active=False,
        min_version=False,
        sorting=False,
        include_only_confirmed=True,
    ):
        "https://docs.nano.org/commands/rpc-protocol/#receivable"
        data = {}
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
        return self._post(data)

    def receivable_exists(
        self, _hash, include_active=False, include_only_confirmed=True
    ):
        "https://docs.nano.org/commands/rpc-protocol/#receivable_exists"
        data = {}
        data["action"] = "receivable_exists"
        data["hash"] = _hash
        if include_active:
            data["include_active"] = True
        if not include_only_confirmed:
            data["include_only_confirmed"] = False
        return self._post(data)

    def representatives(self, count=1, sorting=False):
        "https://docs.nano.org/commands/rpc-protocol/#representatives"
        data = {}
        data["action"] = "representatives"
        data["count"] = count
        if sorting:
            data["sorting"] = True
        return self._post(data)

    def representatives_online(self, weight=False, accounts=[]):
        "https://docs.nano.org/commands/rpc-protocol/#representatives_online"
        data = {}
        data["action"] = "representatives_online"
        if weight:
            data["weight"] = True
        if accounts:
            data["accounts"] = repr(accounts)
        return self._post(data)

    def republish(self, _hash, count=1, sources=0, destinations=0):
        "https://docs.nano.org/commands/rpc-protocol/#republish"
        data = {}
        data["action"] = "republish"
        data["hash"] = _hash
        if sources:
            data["sources"] = sources
            data["count"] = count
        if destinations:
            data["destinations"] = destinations
            data["count"] = count
        return self._post(data)

    def sign(self, key="", wallet="", account="", block="", _hash="", json_block=False):
        "https://docs.nano.org/commands/rpc-protocol/#sign"
        data = {}
        data["action"] = "sign"
        if key:
            data["key"] = key
        if wallet:
            data["wallet"] = wallet
        if account:
            data["account"] = account
        if type(block) == str:
            data["block"] = block
        else:
            data["block"] = json.dumps(block)
        if _hash:
            data["_hash"] = _hash
        if json_block:
            data["json_block"] = True
        return self._post(data)

    def stats(self, _type):
        "https://docs.nano.org/commands/rpc-protocol/#stats"
        data = {}
        data["action"] = "stats"
        data["type"] = _type
        return self._post(data)

    def stats_clear(self):
        "https://docs.nano.org/commands/rpc-protocol/#stats_clear"
        data = {}
        data["action"] = "stats_clear"
        return self._post(data)

    def stop(self):
        "https://docs.nano.org/commands/rpc-protocol/#stop"
        data = {}
        data["action"] = "stop"
        return self._post(data)

    def successors(self, block, count=1, offset=0, reverse=False):
        "https://docs.nano.org/commands/rpc-protocol/#successors"
        data = {}
        data["action"] = "successors"
        data["block"] = block
        data["count"] = count
        if offset:
            data["offset"] = offset
        if reverse:
            data["reverse"] = True
        return self._post(data)

    def telemetry(self, raw=False, address=0, port="7075"):
        "https://docs.nano.org/commands/rpc-protocol/#telemetry"
        data = {}
        data["action"] = "telemetry"
        if raw:
            data["raw"] = True
        if address:
            data["address"] = address
            data["port"] = port
        return self._post(data)

    def validate_account_number(self, account):
        "https://docs.nano.org/commands/rpc-protocol/#validate_account_number"
        data = {}
        data["action"] = "validate_account_number"
        data["account"] = account
        return self._post(data)

    def version(self):
        "https://docs.nano.org/commands/rpc-protocol/#version"
        data = {}
        data["action"] = "version"
        return self._post(data)

    def unchecked(self, json_block=False, count=1):
        "https://docs.nano.org/commands/rpc-protocol/#unchecked"
        data = {}
        data["action"] = "unchecked"
        if json_block:
            data["json_block"] = True
        data["count"] = count
        return self._post(data)

    def unchecked_clear(self):
        "https://docs.nano.org/commands/rpc-protocol/#unchecked_clear"
        data = {}
        data["action"] = "unchecked_clear"
        return self._post(data)

    def unchecked_get(self, _hash, json_block=False):
        "https://docs.nano.org/commands/rpc-protocol/#unchecked_get"
        data = {}
        data["action"] = "unchecked_get"
        data["hash"] = _hash
        if json_block:
            data["json_block"] = True
        return self._post(data)

    def unchecked_keys(self, key, count=1, json_block=False):
        "https://docs.nano.org/commands/rpc-protocol/#unchecked_keys"
        data = {}
        data["action"] = "unchecked_keys"
        data["key"] = key
        data["count"] = count
        if json_block:
            data["json_block"] = True
        return self._post(data)

    def unopened(self, account=None, count=1, threshold=0):
        "https://docs.nano.org/commands/rpc-protocol/#unopened"
        data = {}
        data["action"] = "unopened"
        if account:
            data["account"] = account
        if count:
            data["count"] = count
        if threshold:
            data["threshold"] = threshold
        return self._post(data)

    def uptime(self):
        "https://docs.nano.org/commands/rpc-protocol/#uptime"
        data = {}
        data["action"] = "uptime"
        return self._post(data)

    def work_cancel(self, _hash):
        "https://docs.nano.org/commands/rpc-protocol/#work_cancel"
        data = {}
        data["action"] = "work_cancel"
        data["hash"] = _hash
        return self._post(data)

    def work_generate(
        self,
        _hash,
        use_peers=False,
        difficulty=None,
        multiplier=0,
        account=None,
        version="work_1",
        block=None,
        json_block=False,
    ):
        "https://docs.nano.org/commands/rpc-protocol/#work_generate"
        data = {}
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
        # Currently 'work_1' is the default and only valid option.
        # if version in []: data['version'] = version
        if block:
            data["block"] = block
            if json_block:
                data["json_block"] = json_block
        return self._post(data)

    def work_peer_add(self, address, port):
        "https://docs.nano.org/commands/rpc-protocol/#work_peer_add"
        data = {}
        data["action"] = "work_peer_add"
        data["address"] = address
        data["port"] = port
        return self._post(data)

    def work_peers(self):
        "https://docs.nano.org/commands/rpc-protocol/#work_peers"
        data = {}
        data["action"] = "work_peers"
        return self._post(data)

    def work_peers_clear(self):
        "https://docs.nano.org/commands/rpc-protocol/#work_peers_clear"
        data = {}
        data["action"] = "work_peers_clear"
        return self._post(data)

    def work_validate(
        self, work, _hash, difficulty=None, multiplier=0, version="work_1"
    ):
        "https://docs.nano.org/commands/rpc-protocol/#work_validate"
        data = {}
        data["action"] = "work_validate"
        data["work"] = work
        data["hash"] = _hash
        if multiplier:
            data["multiplier"] = multiplier
        elif difficulty:
            data["difficulty"] = difficulty
        # Currently 'work_1' is the default and only valid option.
        # if version in []: data['version'] = version
        return self._post(data)

    # Wallet RPCs

    def account_create(self, wallet, index=0, work=True):
        "https://docs.nano.org/commands/rpc-protocol/#account_create"
        data = {}
        data["action"] = "account_create"
        data["wallet"] = wallet
        if index:
            data["index"] = index
        if not work:
            data["work"] = False
        return self._post(data)

    def account_list(self, wallet):
        "https://docs.nano.org/commands/rpc-protocol/#account_list"
        data = {}
        data["action"] = "account_list"
        data["wallet"] = wallet
        return self._post(data)

    def account_move(self, wallet, source, accounts):
        "https://docs.nano.org/commands/rpc-protocol/#account_move"
        data = {}
        data["action"] = "account_move"
        data["wallet"] = wallet
        data["source"] = source
        data["accounts"] = accounts
        return self._post(data)

    def account_remove(self, wallet, account):
        "https://docs.nano.org/commands/rpc-protocol/#account_remove"
        data = {}
        data["action"] = "account_remove"
        data["wallet"] = wallet
        data["account"] = account
        return self._post(data)

    def account_representative_set(self, wallet, account, representative, work=None):
        "https://docs.nano.org/commands/rpc-protocol/#account_representative_set"
        data = {}
        data["action"] = "account_representative_set"
        data["wallet"] = wallet
        data["account"] = account
        data["representative"] = representative
        if work:
            data["work"] = work
        return self._post(data)

    def accounts_create(self, wallet, count=1, work=True):
        "https://docs.nano.org/commands/rpc-protocol/#accounts_create"
        data = {}
        data["action"] = "accounts_create"
        data["wallet"] = wallet
        data["count"] = count
        if not work:
            data["work"] = False
        return self._post(data)

    def password_change(self, wallet, password):
        "https://docs.nano.org/commands/rpc-protocol/#password_change"
        data = {}
        data["action"] = "password_change"
        data["wallet"] = wallet
        data["password"] = password
        return self._post(data)

    def password_enter(self, wallet, password):
        "https://docs.nano.org/commands/rpc-protocol/#password_enter"
        data = {}
        data["action"] = "password_enter"
        data["wallet"] = wallet
        data["password"] = password
        return self._post(data)

    def password_valid(self, wallet):
        "https://docs.nano.org/commands/rpc-protocol/#password_valid"
        data = {}
        data["action"] = "password_valid"
        data["wallet"] = wallet
        return self._post(data)

    def receive(self, wallet, account, block, work=None):
        "https://docs.nano.org/commands/rpc-protocol/#receive"
        data = {}
        data["action"] = "receive"
        data["wallet"] = wallet
        data["account"] = account
        data["block"] = block
        if work:
            data["work"] = work
        return self._post(data)

    def receive_minimum(self):
        "https://docs.nano.org/commands/rpc-protocol/#receive_minimum"
        data = {}
        data["action"] = "receive_minimum"
        return self._post(data)

    def receive_minimum_set(self, amount):
        "https://docs.nano.org/commands/rpc-protocol/#receive_minimum_set"
        data = {}
        data["action"] = "receive_minimum_set"
        data["amount"] = amount
        return self._post(data)

    def search_receivable(self, wallet):
        "https://docs.nano.org/commands/rpc-protocol/#search_receivable"
        data = {}
        data["action"] = "search_receivable"
        data["wallet"] = wallet
        return self._post(data)

    def search_receivable_all(self):
        "https://docs.nano.org/commands/rpc-protocol/#search_receivable_all"
        data = {}
        data["action"] = "search_receivable_all"
        return self._post(data)

    def send(self, wallet, source, destination, amount, _id=None, work=None):
        "https://docs.nano.org/commands/rpc-protocol/#send"
        data = {}
        data["action"] = "send"
        data["wallet"] = wallet
        data["source"] = source
        data["destination"] = destination
        data["amount"] = amount
        if _id:
            data["id"] = _id
        if work:
            data["work"] = work
        return self._post(data)

    def wallet_add(self, wallet, key, work=False):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_add"
        data = {}
        data["action"] = "wallet_add"
        data["wallet"] = wallet
        data["key"] = key
        if work:
            data["work"] = True
        return self._post(data)

    def wallet_add_watch(self, wallet, accounts):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_add_watch"
        data = {}
        data["action"] = "wallet_add_watch"
        data["wallet"] = wallet
        data["accounts"] = accounts
        return self._post(data)

    def wallet_balances(self, wallet, threshold=0):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_balances"
        data = {}
        data["action"] = "wallet_balances"
        data["wallet"] = wallet
        if threshold:
            data["threshold"] = threshold
        return self._post(data)

    def wallet_change_seed(self, wallet, seed, count=0):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_change_seed"
        data = {}
        data["action"] = "wallet_change_seed"
        data["wallet"] = wallet
        data["seed"] = seed
        if count:
            data["count"] = count
        return self._post(data)

    def wallet_contains(self, wallet, account):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_contains"
        data = {}
        data["action"] = "wallet_contains"
        data["wallet"] = wallet
        data["account"] = account
        return self._post(data)

    def wallet_create(self, seed=""):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_create"
        data = {}
        data["action"] = "wallet_create"
        if seed:
            data["seed"] = seed
        return self._post(data)

    def wallet_destroy(self, wallet):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_destroy"
        data = {}
        data["action"] = "wallet_destroy"
        data["wallet"] = wallet
        return self._post(data)

    def wallet_export(self, wallet):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_export"
        data = {}
        data["action"] = "wallet_export"
        data["wallet"] = wallet
        return self._post(data)

    def wallet_frontiers(self, wallet):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_frontiers"
        data = {}
        data["action"] = "wallet_frontiers"
        data["wallet"] = wallet
        return self._post(data)

    def wallet_history(self, wallet, modified_since=0):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_history"
        data = {}
        data["action"] = "wallet_history"
        data["wallet"] = wallet
        if modified_since:
            data["modified_since"] = modified_since
        return self._post(data)

    def wallet_info(self, wallet):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_info"
        data = {}
        data["action"] = "wallet_info"
        data["wallet"] = wallet
        return self._post(data)

    def wallet_ledger(
        self,
        wallet,
        representative=False,
        weight=False,
        receivable=False,
        modified_since=None,
    ):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_ledger"
        data = {}
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
        return self._post(data)

    def wallet_lock(self, wallet):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_lock"
        data = {}
        data["action"] = "wallet_lock"
        data["wallet"] = wallet
        return self._post(data)

    def wallet_locked(self, wallet):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_locked"
        data = {}
        data["action"] = "wallet_locked"
        data["wallet"] = wallet
        return self._post(data)

    def wallet_receivable(
        self,
        wallet,
        count=1,
        threshold=0,
        source=False,
        include_active=False,
        min_version=False,
        include_only_confirmed=True,
    ):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_receivable"
        data = {}
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
        return self._post(data)

    def wallet_representative(self, wallet):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_representative"
        data = {}
        data["action"] = "wallet_representative"
        data["wallet"] = wallet
        return self._post(data)

    def wallet_representative_set(
        self, wallet, representative, update_existing_accounts=False
    ):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_representative_set"
        data = {}
        data["action"] = "wallet_representative_set"
        data["wallet"] = wallet
        data["representative"] = representative
        if update_existing_accounts:
            data["update_existing_accounts"] = True
        return self._post(data)

    def wallet_republish(self, wallet, count=1):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_republish"
        data = {}
        data["action"] = "wallet_republish"
        data["wallet"] = wallet
        data["count"] = count
        return self._post(data)

    def wallet_work_get(self, wallet):
        "https://docs.nano.org/commands/rpc-protocol/#wallet_work_get"
        data = {}
        data["action"] = "wallet_work_get"
        data["wallet"] = wallet
        return self._post(data)

    def work_get(self, wallet, account):
        "https://docs.nano.org/commands/rpc-protocol/#work_get"
        data = {}
        data["action"] = "work_get"
        data["wallet"] = wallet
        data["account"] = account
        return self._post(data)

    def work_set(self, wallet, account, work):
        "https://docs.nano.org/commands/rpc-protocol/#work_set"
        data = {}
        data["action"] = "work_set"
        data["wallet"] = wallet
        data["account"] = account
        data["work"] = work
        return self._post(data)

    # Unit conversion RPCs

    def nano_to_raw(self, amount):
        "https://docs.nano.org/commands/rpc-protocol/#nano_to_raw"
        data = {}
        data["action"] = "nano_to_raw"
        data["amount"] = amount
        return self._post(data)

    def raw_to_nano(self, amount):
        "https://docs.nano.org/commands/rpc-protocol/#raw_to_nano"
        data = {}
        data["action"] = "raw_to_nano"
        data["amount"] = amount
        return self._post(data)
