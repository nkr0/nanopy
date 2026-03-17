import json, requests


class RPC:

    def __init__(self, url='http://localhost:7076', headers={}, use_tor=False):
        if url[:7] == 'http://' or url[:8] == 'https://':
            self.__mode = 'requests'
            self.session = requests.session()
            self.session.proxies = {}
            if use_tor:
                self.session.proxies['http'] = self.session.proxies[
                    'https'] = 'socks5h://localhost:9050'
        elif url[:5] == 'ws://' or url[:6] == 'wss://':
            from websocket import create_connection
            self.__mode = 'websockets'
            if use_tor:
                self.session = create_connection(url,
                                                 http_proxy_host="localhost",
                                                 http_proxy_port=9050,
                                                 proxy_type='socks5h')
            else:
                self.session = create_connection(url)
            self.session.settimeout(20.0)
        else:
            raise Exception('Unable to parse url: ' + url)
        self.__url = url
        self.__headers = headers

    def _post(self, data):
        if self.__mode == 'requests':
            return self.session.post(self.__url,
                                     json=data,
                                     headers=self.__headers).json()
        elif self.__mode == 'websockets':
            self.session.send(json.dumps(data))
            return json.loads(self.session.recv())

    def disconnect(self):
        if self.__mode == 'websockets': self.session.close()

    def account_balance(self, account):
        data = {}
        data['action'] = 'account_balance'
        data['account'] = account
        return self._post(data)

    def account_block_count(self, account):
        data = {}
        data['action'] = 'account_block_count'
        data['account'] = account
        return self._post(data)

    def account_info(self,
                     account,
                     representative=False,
                     weight=False,
                     pending=False):
        data = {}
        data['action'] = 'account_info'
        data['account'] = account
        if representative: data['representative'] = True
        if weight: data['weight'] = True
        if pending: data['pending'] = True
        return self._post(data)

    def account_create(self, wallet, index=0, work=True):
        data = {}
        data['action'] = 'account_create'
        data['wallet'] = wallet
        if index: data['index'] = index
        if not work: data['work'] = False
        return self._post(data)

    def account_get(self, key):
        data = {}
        data['action'] = 'account_get'
        data['key'] = key
        return self._post(data)

    def account_history(self,
                        account,
                        count=1,
                        raw=False,
                        head=None,
                        offset=0,
                        reverse=False,
                        account_filter=[]):
        data = {}
        data['action'] = 'account_history'
        data['account'] = account
        data['count'] = count
        if raw: data['raw'] = True
        if head: data['head'] = head
        if offset: data['offset'] = offset
        if reverse: data['reverse'] = reverse
        if account_filter: data['account_filter'] = account_filter
        return self._post(data)

    def account_list(self, wallet):
        data = {}
        data['action'] = 'account_list'
        data['wallet'] = wallet
        return self._post(data)

    def account_move(self, wallet, source, accounts):
        data = {}
        data['action'] = 'account_move'
        data['wallet'] = wallet
        data['source'] = source
        data['accounts'] = accounts
        return self._post(data)

    def account_key(self, account):
        data = {}
        data['action'] = 'account_key'
        data['account'] = account
        return self._post(data)

    def account_remove(self, wallet, account):
        data = {}
        data['action'] = 'account_remove'
        data['wallet'] = wallet
        data['account'] = account
        return self._post(data)

    def account_representative(self, account):
        data = {}
        data['action'] = 'account_representative'
        data['account'] = account
        return self._post(data)

    def account_representative_set(self,
                                   wallet,
                                   account,
                                   representative,
                                   work=None):
        data = {}
        data['action'] = 'account_representative_set'
        data['wallet'] = wallet
        data['account'] = account
        data['representative'] = representative
        if work: data['work'] = work
        return self._post(data)

    def account_weight(self, account):
        data = {}
        data['action'] = 'account_weight'
        data['account'] = account
        return self._post(data)

    def accounts_balances(self, accounts):
        data = {}
        data['action'] = 'accounts_balances'
        data['accounts'] = accounts
        return self._post(data)

    def accounts_create(self, wallet, count=1, work=True):
        data = {}
        data['action'] = 'accounts_create'
        data['wallet'] = wallet
        data['count'] = count
        if not work: data['work'] = False
        return self._post(data)

    def accounts_frontiers(self, accounts):
        data = {}
        data['action'] = 'accounts_frontiers'
        data['accounts'] = accounts
        return self._post(data)

    def accounts_pending(self,
                         accounts,
                         count=1,
                         threshold=None,
                         source=False,
                         include_active=False,
                         sorting=False,
                         include_only_confirmed=False):
        data = {}
        data['action'] = 'accounts_pending'
        data['accounts'] = accounts
        data['count'] = count
        if threshold: data['threshold'] = threshold
        if source: data['source'] = True
        if include_active: data['include_active'] = True
        if sorting: data['sorting'] = True
        if include_only_confirmed: data['include_only_confirmed'] = True
        return self._post(data)

    def active_difficulty(self, include_trend=False):
        data = {}
        data['action'] = 'active_difficulty'
        if include_trend: data['include_trend'] = True
        return self._post(data)

    def available_supply(self):
        data = {}
        data['action'] = 'available_supply'
        return self._post(data)

    def block_info(self, _hash, json_block=False):
        data = {}
        data['action'] = 'block_info'
        data['hash'] = _hash
        if json_block: data['json_block'] = True
        return self._post(data)

    def blocks(self, hashes):
        data = {}
        data['action'] = 'blocks'
        data['hashes'] = hashes
        return self._post(data)

    def blocks_info(self,
                    hashes,
                    pending=False,
                    source=False,
                    balance=False,
                    json_block=False,
                    include_not_found=False):
        data = {}
        data['action'] = 'blocks_info'
        data['hashes'] = hashes
        if pending: data['pending'] = True
        if source: data['source'] = True
        if balance: data['balance'] = True
        if json_block: data['json_block'] = True
        if include_not_found: data['include_not_found'] = True
        return self._post(data)

    def block_account(self, _hash):
        data = {}
        data['action'] = 'block_account'
        data['hash'] = _hash
        return self._post(data)

    def block_confirm(self, _hash):
        data = {}
        data['action'] = 'block_confirm'
        data['hash'] = _hash
        return self._post(data)

    def block_count(self, include_cemented=False):
        data = {}
        data['action'] = 'block_count'
        if include_cemented: data['include_cemented'] = True
        return self._post(data)

    def block_count_type(self):
        data = {}
        data['action'] = 'block_count_type'
        return self._post(data)

    def block_hash(self, block, json_block=False):
        data = {}
        data['action'] = 'block_hash'
        if type(block) == str:
            data['block'] = block
        else:
            data['block'] = json.dumps(block)
        if json_block: data['json_block'] = True
        return self._post(data)

    def bootstrap(self, address, port):
        data = {}
        data['action'] = 'bootstrap'
        data['address'] = address
        data['port'] = port
        return self._post(data)

    def bootstrap_lazy(self, hash_, force=False):
        data = {}
        data['action'] = 'bootstrap_lazy'
        data['hash'] = hash_
        if force: data['force'] = True
        return self._post(data)

    def bootstrap_any(self):
        data = {}
        data['action'] = 'bootstrap_any'
        return self._post(data)

    def bootstrap_status(self):
        data = {}
        data['action'] = 'bootstrap_status'
        return self._post(data)

    def chain(self, block, count=1, offset=0, reverse=False):
        data = {}
        data['action'] = 'chain'
        data['block'] = block
        data['count'] = count
        if offset: data['offset'] = offset
        if reverse: data['reverse'] = True
        return self._post(data)

    def confirmation_active(self, announcements=0):
        data = {}
        data['action'] = 'confirmation_active'
        if announcements: data['announcements'] = announcements
        return self._post(data)

    def confirmation_height_currently_processing(self):
        data = {}
        data['action'] = 'confirmation_height_currently_processing'
        return self._post(data)

    def confirmation_history(self, _hash=None):
        data = {}
        data['action'] = 'confirmation_history'
        if _hash: data['hash'] = _hash
        return self._post(data)

    def confirmation_info(self,
                          root,
                          contents=True,
                          representatives=False,
                          json_block=False):
        data = {}
        data['action'] = 'confirmation_info'
        data['root'] = root
        if not contents: data['contents'] = False
        if representatives: data['representatives'] = True
        if json_block: data['json_block'] = True
        return self._post(data)

    def confirmation_quorum(self, peer_details=False):
        data = {}
        data['action'] = 'confirmation_quorum'
        if peer_details: data['peer_details'] = True
        return self._post(data)

    def database_txn_tracker(self, min_read_time, min_write_time):
        data = {}
        data['action'] = 'database_txn_tracker'
        data['min_read_time'] = min_read_time
        data['min_write_time'] = min_write_time
        return self._post(data)

    def delegators(self, account):
        data = {}
        data['action'] = 'delegators'
        data['account'] = account
        return self._post(data)

    def delegators_count(self, account):
        data = {}
        data['action'] = 'delegators_count'
        data['account'] = account
        return self._post(data)

    def deterministic_key(self, seed, index):
        data = {}
        data['action'] = 'deterministic_key'
        data['seed'] = seed
        data['index'] = index
        return self._post(data)

    def frontiers(self, account, count=1):
        data = {}
        data['action'] = 'frontiers'
        data['account'] = account
        data['count'] = count
        return self._post(data)

    def frontier_count(self):
        data = {}
        data['action'] = 'frontier_count'
        return self._post(data)

    def mrai_from_raw(self, amount):
        data = {}
        data['action'] = 'mrai_from_raw'
        data['amount'] = amount
        return self._post(data)

    def mrai_to_raw(self, amount):
        data = {}
        data['action'] = 'mrai_to_raw'
        data['amount'] = amount
        return self._post(data)

    def krai_from_raw(self, amount):
        data = {}
        data['action'] = 'krai_from_raw'
        data['amount'] = amount
        return self._post(data)

    def krai_to_raw(self, amount):
        data = {}
        data['action'] = 'krai_to_raw'
        data['amount'] = amount
        return self._post(data)

    def rai_from_raw(self, amount):
        data = {}
        data['action'] = 'rai_from_raw'
        data['amount'] = amount
        return self._post(data)

    def rai_to_raw(self, amount):
        data = {}
        data['action'] = 'rai_to_raw'
        data['amount'] = amount
        return self._post(data)

    def keepalive(self, address, port):
        data = {}
        data['action'] = 'keepalive'
        data['address'] = address
        data['port'] = port
        return self._post(data)

    def key_create(self):
        data = {}
        data['action'] = 'key_create'
        return self._post(data)

    def key_expand(self, key):
        data = {}
        data['action'] = 'key_expand'
        data['key'] = key
        return self._post(data)

    def ledger(self,
               account,
               count=1,
               representative=False,
               weight=False,
               pending=False,
               modified_since=0,
               sorting=False,
               threshold=0):
        data = {}
        data['action'] = 'ledger'
        data['account'] = account
        data['count'] = count
        if representative: data['representative'] = True
        if weight: data['weight'] = True
        if pending: data['pending'] = True
        if modified_since: data['modified_since'] = modified_since
        if sorting: data['sorting'] = True
        if threshold: data['threshold'] = threshold
        return self._post(data)

    def block_create(self,
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
                     json_block=False):
        data = {}
        data['action'] = 'block_create'
        data['type'] = 'state'
        data['balance'] = balance
        if wallet: data['wallet'] = wallet
        if account: data['account'] = account
        if key: data['key'] = key
        if source: data['source'] = source
        if destination: data['destination'] = destination
        if link: data['link'] = link
        data['representative'] = representative
        data['previous'] = previous
        if work: data['work'] = work
        if json_block: data['json_block'] = True
        return self._post(data)

    def node_id(self):
        data = {}
        data['action'] = 'node_id'
        return self._post(data)

    def node_id_delete(self):
        data = {}
        data['action'] = 'node_id_delete'
        return self._post(data)

    def payment_begin(self, wallet):
        data = {}
        data['action'] = 'payment_begin'
        data['wallet'] = wallet
        return self._post(data)

    def payment_init(self, wallet):
        data = {}
        data['action'] = 'payment_init'
        data['wallet'] = wallet
        return self._post(data)

    def payment_end(self, account, wallet):
        data = {}
        data['action'] = 'payment_end'
        data['account'] = account
        data['wallet'] = wallet
        return self._post(data)

    def payment_wait(self, account, amount, timeout):
        data = {}
        data['action'] = 'payment_wait'
        data['account'] = account
        data['amount'] = amount
        data['timeout'] = timeout
        return self._post(data)

    def process(self, block, force=False, subtype=None, json_block=False):
        data = {}
        data['action'] = 'process'
        if type(block) == str:
            data['block'] = block
        else:
            data['block'] = json.dumps(block)
        if force: data['force'] = True
        if subtype: data['subtype'] = subtype
        if json_block: data['json_block'] = True
        return self._post(data)

    def receive(self, wallet, account, block, work=None):
        data = {}
        data['action'] = 'receive'
        data['wallet'] = wallet
        data['account'] = account
        data['block'] = block
        if work: data['work'] = work
        return self._post(data)

    def receive_minimum(self):
        data = {}
        data['action'] = 'receive_minimum'
        return self._post(data)

    def receive_minimum_set(self, amount):
        data = {}
        data['action'] = 'receive_minimum_set'
        data['amount'] = amount
        return self._post(data)

    def representatives(self, count=1, sorting=False):
        data = {}
        data['action'] = 'representatives'
        data['count'] = count
        if sorting: data['sorting'] = True
        return self._post(data)

    def representatives_online(self, weight=False):
        data = {}
        data['action'] = 'representatives_online'
        if weight: data['weight'] = True
        return self._post(data)

    def wallet_representative(self, wallet):
        data = {}
        data['action'] = 'wallet_representative'
        data['wallet'] = wallet
        return self._post(data)

    def wallet_representative_set(self,
                                  wallet,
                                  representative,
                                  update_existing_accounts=False):
        data = {}
        data['action'] = 'wallet_representative_set'
        data['wallet'] = wallet
        data['representative'] = representative
        if update_existing_accounts: data['update_existing_accounts'] = True
        return self._post(data)

    def republish(self, _hash, count=1, sources=0, destinations=0):
        data = {}
        data['action'] = 'republish'
        data['hash'] = _hash
        if sources:
            data['sources'] = sources
            data['count'] = count
        if destinations:
            data['destinations'] = destinations
            data['count'] = count
        return self._post(data)

    def search_pending(self, wallet):
        data = {}
        data['action'] = 'search_pending'
        data['wallet'] = wallet
        return self._post(data)

    def search_pending_all(self):
        data = {}
        data['action'] = 'search_pending_all'
        return self._post(data)

    def send(self, wallet, source, destination, amount, _id=None, work=None):
        data = {}
        data['action'] = 'send'
        data['wallet'] = wallet
        data['source'] = source
        data['destination'] = destination
        data['amount'] = amount
        if _id: data['id'] = _id
        if work: data['work'] = work
        return self._post(data)

    def sign(self,
             key='',
             wallet='',
             account='',
             block='',
             _hash='',
             json_block=False):
        data = {}
        data['action'] = 'sign'
        if key: data['key'] = key
        if wallet: data['wallet'] = wallet
        if account: data['account'] = account
        if type(block) == str:
            data['block'] = block
        else:
            data['block'] = json.dumps(block)
        if _hash: data['_hash'] = _hash
        if json_block: data['json_block'] = True
        return self._post(data)

    def stats(self, _type):
        data = {}
        data['action'] = 'stats'
        data['type'] = _type
        return self._post(data)

    def stats_clear(self):
        data = {}
        data['action'] = 'stats_clear'
        return self._post(data)

    def stop(self):
        data = {}
        data['action'] = 'stop'
        return self._post(data)

    def validate_account_number(self, account):
        data = {}
        data['action'] = 'validate_account_number'
        data['account'] = account
        return self._post(data)

    def successors(self, block, count=1, offset=0, reverse=False):
        data = {}
        data['action'] = 'successors'
        data['block'] = block
        data['count'] = count
        if offset: data['offset'] = offset
        if reverse: data['reverse'] = True
        return self._post(data)

    def version(self):
        data = {}
        data['action'] = 'version'
        return self._post(data)

    def peers(self, peer_details=False):
        data = {}
        data['action'] = 'peers'
        if peer_details: data['peer_details'] = True
        return self._post(data)

    def pending(self,
                account,
                count=1,
                threshold=0,
                source=False,
                include_active=False,
                sorting=False,
                include_only_confirmed=False):
        data = {}
        data['action'] = 'pending'
        data['account'] = account
        data['count'] = count
        if threshold: data['threshold'] = threshold
        if source: data['source'] = True
        if include_active: data['include_active'] = True
        if sorting: data['sorting'] = True
        if include_only_confirmed: data['include_only_confirmed'] = True
        return self._post(data)

    def pending_exists(self,
                       _hash,
                       include_active=False,
                       include_only_confirmed=False):
        data = {}
        data['action'] = 'pending_exists'
        data['hash'] = _hash
        if include_active: data['include_active'] = True
        if include_only_confirmed: data['include_only_confirmed'] = True
        return self._post(data)

    def unchecked(self, count=1):
        data = {}
        data['action'] = 'unchecked'
        data['count'] = count
        return self._post(data)

    def unchecked_clear(self):
        data = {}
        data['action'] = 'unchecked_clear'
        return self._post(data)

    def unchecked_get(self, _hash, json_block=False):
        data = {}
        data['action'] = 'unchecked_get'
        data['hash'] = _hash
        if json_block: data['json_block'] = True
        return self._post(data)

    def unchecked_keys(self, key, count=1, json_block=False):
        data = {}
        data['action'] = 'unchecked_keys'
        data['key'] = key
        data['count'] = count
        if json_block: data['json_block'] = True
        return self._post(data)

    def unopened(self, account=None, count=1, threshold=0):
        data = {}
        data['action'] = 'unopened'
        if account: data['account'] = account
        if count: data['count'] = count
        if threshold: data['threshold'] = threshold
        return self._post(data)

    def uptime(self):
        data = {}
        data['action'] = 'uptime'
        return self._post(data)

    def wallet_add(self, wallet, key, work=True):
        data = {}
        data['action'] = 'wallet_add'
        data['wallet'] = wallet
        data['key'] = key
        if not work: data['work'] = False
        return self._post(data)

    def wallet_add_watch(self, wallet, accounts):
        data = {}
        data['action'] = 'wallet_add_watch'
        data['wallet'] = wallet
        data['accounts'] = accounts
        return self._post(data)

    def wallet_balances(self, wallet, threshold=0):
        data = {}
        data['action'] = 'wallet_balances'
        data['wallet'] = wallet
        if threshold: data['threshold'] = threshold
        return self._post(data)

    def wallet_change_seed(self, wallet, seed, count=0):
        data = {}
        data['action'] = 'wallet_change_seed'
        data['wallet'] = wallet
        data['seed'] = seed
        if count: data['count'] = count
        return self._post(data)

    def wallet_contains(self, wallet, account):
        data = {}
        data['action'] = 'wallet_contains'
        data['wallet'] = wallet
        data['account'] = account
        return self._post(data)

    def wallet_create(self, seed=''):
        data = {}
        data['action'] = 'wallet_create'
        if seed: data['seed'] = seed
        return self._post(data)

    def wallet_destroy(self, wallet):
        data = {}
        data['action'] = 'wallet_destroy'
        data['wallet'] = wallet
        return self._post(data)

    def wallet_export(self, wallet):
        data = {}
        data['action'] = 'wallet_export'
        data['wallet'] = wallet
        return self._post(data)

    def wallet_frontiers(self, wallet):
        data = {}
        data['action'] = 'wallet_frontiers'
        data['wallet'] = wallet
        return self._post(data)

    def wallet_info(self, wallet):
        data = {}
        data['action'] = 'wallet_info'
        data['wallet'] = wallet
        return self._post(data)

    def wallet_history(self, wallet, modified_since=0):
        data = {}
        data['action'] = 'wallet_history'
        data['wallet'] = wallet
        if modified_since: data['modified_since'] = modified_since
        return self._post(data)

    def wallet_ledger(self,
                      wallet,
                      representative=False,
                      weight=False,
                      pending=False,
                      modified_since=None):
        data = {}
        data['action'] = 'wallet_ledger'
        data['wallet'] = wallet
        if representative: data['representative'] = True
        if weight: data['weight'] = True
        if pending: data['pending'] = True
        if modified_since: data['modified_since'] = modified_since
        return self._post(data)

    def wallet_pending(self,
                       wallet,
                       count=1,
                       threshold=0,
                       source=False,
                       include_active=False,
                       include_only_confirmed=False):
        data = {}
        data['action'] = 'wallet_pending'
        data['wallet'] = wallet
        data['count'] = count
        if threshold: data['threshold'] = threshold
        if source: data['source'] = True
        if include_active: data['include_active'] = True
        if include_only_confirmed: data['include_only_confirmed'] = True
        return self._post(data)

    def wallet_republish(self, wallet, count=1):
        data = {}
        data['action'] = 'wallet_republish'
        data['wallet'] = wallet
        data['count'] = count
        return self._post(data)

    def wallet_work_get(self, wallet):
        data = {}
        data['action'] = 'wallet_work_get'
        data['wallet'] = wallet
        return self._post(data)

    def password_change(self, wallet, password):
        data = {}
        data['action'] = 'password_change'
        data['wallet'] = wallet
        data['password'] = password
        return self._post(data)

    def password_enter(self, wallet, password):
        data = {}
        data['action'] = 'password_enter'
        data['wallet'] = wallet
        data['password'] = password
        return self._post(data)

    def password_valid(self, wallet):
        data = {}
        data['action'] = 'password_valid'
        data['wallet'] = wallet
        return self._post(data)

    def wallet_lock(self, wallet):
        data = {}
        data['action'] = 'wallet_lock'
        data['wallet'] = wallet
        return self._post(data)

    def wallet_locked(self, wallet):
        data = {}
        data['action'] = 'wallet_locked'
        data['wallet'] = wallet
        return self._post(data)

    def work_cancel(self, _hash):
        data = {}
        data['action'] = 'work_cancel'
        data['hash'] = _hash
        return self._post(data)

    def work_generate(self,
                      _hash,
                      use_peers=False,
                      difficulty=None,
                      multiplier=0):
        data = {}
        data['action'] = 'work_generate'
        data['hash'] = _hash
        if use_peers: data['use_peers'] = True
        if multiplier: data['multiplier'] = multiplier
        elif difficulty:
            if type(difficulty) == str: data['difficulty'] = difficulty
            else: data['difficulty'] = format(difficulty, '016x')
        return self._post(data)

    def work_get(self, wallet, account):
        data = {}
        data['action'] = 'work_get'
        data['wallet'] = wallet
        data['account'] = account
        return self._post(data)

    def work_set(self, wallet, account, work):
        data = {}
        data['action'] = 'work_set'
        data['wallet'] = wallet
        data['account'] = account
        data['work'] = work
        return self._post(data)

    def work_peer_add(self, address, port):
        data = {}
        data['action'] = 'work_peer_add'
        data['address'] = address
        data['port'] = port
        return self._post(data)

    def work_peers(self):
        data = {}
        data['action'] = 'work_peers'
        return self._post(data)

    def work_peers_clear(self):
        data = {}
        data['action'] = 'work_peers_clear'
        return self._post(data)

    def work_validate(self, work, _hash, difficulty=None, multiplier=1):
        data = {}
        data['action'] = 'work_validate'
        data['work'] = work
        data['hash'] = _hash
        if multiplier: data['multiplier'] = multiplier
        elif difficulty:
            if type(difficulty) == str: data['difficulty'] = difficulty
            else: data['difficulty'] = format(difficulty, '016x')
        return self._post(data)
