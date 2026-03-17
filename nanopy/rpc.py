import json, requests


class RPC:

    def __init__(self, url='http://localhost:7076', work_url=''):
        self.session = requests.session()
        self.session.proxies = {}
        self.url = url
        self.work_url = work_url

    def account_balance(self, account):
        data = {}
        data['action'] = 'account_balance'
        data['account'] = account
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def account_block_count(self, account):
        data = {}
        data['action'] = 'account_block_count'
        data['account'] = account
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

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
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def account_create(self, wallet, index=0, work=False):
        data = {}
        data['action'] = 'account_create'
        data['wallet'] = wallet
        if index: data['index'] = index
        if work: data['work'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def account_get(self, key):
        data = {}
        data['action'] = 'account_get'
        data['key'] = key
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def account_history(self, account, count=1, raw=False, head=None):
        data = {}
        data['action'] = 'account_history'
        data['account'] = account
        data['count'] = count
        if raw: data['raw'] = True
        if head: data['head'] = head
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def account_list(self, wallet):
        data = {}
        data['action'] = 'account_list'
        data['wallet'] = wallet
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def account_move(self, wallet, source, accounts):
        data = {}
        data['action'] = 'account_move'
        data['wallet'] = wallet
        data['source'] = source
        data['accounts'] = accounts
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def account_key(self, account):
        data = {}
        data['action'] = 'account_key'
        data['account'] = account
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def account_remove(self, wallet, account):
        data = {}
        data['action'] = 'account_remove'
        data['wallet'] = wallet
        data['account'] = account
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def account_representative(self, account):
        data = {}
        data['action'] = 'account_representative'
        data['account'] = account
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

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
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def account_weight(self, account):
        data = {}
        data['action'] = 'account_weight'
        data['account'] = account
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def accounts_balances(self, accounts):
        data = {}
        data['action'] = 'accounts_balances'
        data['accounts'] = accounts
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def accounts_create(self, wallet, count, work=False):
        data = {}
        data['action'] = 'accounts_create'
        data['wallet'] = wallet
        data['count'] = count
        if work: data['work'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def accounts_frontiers(self, accounts):
        data = {}
        data['action'] = 'accounts_frontiers'
        data['accounts'] = accounts
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def accounts_pending(self,
                         accounts,
                         count=1,
                         threshold=None,
                         source=False,
                         include_active=False):
        data = {}
        data['action'] = 'accounts_pending'
        data['accounts'] = accounts
        data['count'] = count
        if threshold: data['threshold'] = threshold
        if source: data['source'] = True
        if include_active: data['include_active'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def available_supply(self):
        data = {}
        data['action'] = 'available_supply'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def block_info(self, _hash, json_block=False):
        data = {}
        data['action'] = 'block_info'
        data['hash'] = _hash
        if json_block: data['json_block'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def blocks(self, hashes):
        data = {}
        data['action'] = 'blocks'
        data['hashes'] = hashes
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def blocks_info(self,
                    hashes,
                    pending=False,
                    source=False,
                    balance=False,
                    json_block=False):
        data = {}
        data['action'] = 'blocks_info'
        data['hashes'] = hashes
        if pending: data['pending'] = True
        if source: data['source'] = True
        if balance: data['balance'] = True
        if json_block: data['json_block'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def block_account(self, _hash):
        data = {}
        data['action'] = 'block_account'
        data['hash'] = _hash
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def block_confirm(self, _hash):
        data = {}
        data['action'] = 'block_confirm'
        data['hash'] = _hash
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def block_count(self):
        data = {}
        data['action'] = 'block_count'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def block_count_type(self):
        data = {}
        data['action'] = 'block_count_type'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def block_hash(self, block, json_block=False):
        data = {}
        data['action'] = 'block_hash'
        if type(block) == str:
            data['block'] = block
        else:
            data['block'] = json.dumps(block)
        if json_block: data['json_block'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def bootstrap(self, address, port):
        data = {}
        data['action'] = 'bootstrap'
        data['address'] = address
        data['port'] = port
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def bootstrap_lazy(self, hash_, force=False):
        data = {}
        data['action'] = 'bootstrap_lazy'
        data['hash'] = hash_
        if force: data['force'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def bootstrap_any(self):
        data = {}
        data['action'] = 'bootstrap_any'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def bootstrap_status(self):
        data = {}
        data['action'] = 'bootstrap_status'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def chain(self, block, count, offset=0, reverse=False):
        data = {}
        data['action'] = 'chain'
        data['block'] = block
        data['count'] = count
        if offset: data['offset'] = offset
        if reverse: data['reverse'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def confirmation_active(self, announcements=0):
        data = {}
        data['action'] = 'confirmation_active'
        if announcements: data['announcements'] = announcements
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def confirmation_history(self):
        data = {}
        data['action'] = 'confirmation_history'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

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
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def confirmation_quorum(self, peer_details=False):
        data = {}
        data['action'] = 'confirmation_quorum'
        if peer_details: data['peer_details'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def delegators(self, account):
        data = {}
        data['action'] = 'delegators'
        data['account'] = account
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def delegators_count(self, account):
        data = {}
        data['action'] = 'delegators_count'
        data['account'] = account
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def deterministic_key(self, seed, index):
        data = {}
        data['action'] = 'deterministic_key'
        data['seed'] = seed
        data['index'] = index
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def frontiers(self, account, count):
        data = {}
        data['action'] = 'frontiers'
        data['account'] = account
        data['count'] = count
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def frontier_count(self):
        data = {}
        data['action'] = 'frontier_count'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def mrai_from_raw(self, amount):
        data = {}
        data['action'] = 'mrai_from_raw'
        data['amount'] = amount
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def mrai_to_raw(self, amount):
        data = {}
        data['action'] = 'mrai_to_raw'
        data['amount'] = amount
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def krai_from_raw(self, amount):
        data = {}
        data['action'] = 'krai_from_raw'
        data['amount'] = amount
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def krai_to_raw(self, amount):
        data = {}
        data['action'] = 'krai_to_raw'
        data['amount'] = amount
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def rai_from_raw(self, amount):
        data = {}
        data['action'] = 'rai_from_raw'
        data['amount'] = amount
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def rai_to_raw(self, amount):
        data = {}
        data['action'] = 'rai_to_raw'
        data['amount'] = amount
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def keepalive(self, address, port):
        data = {}
        data['action'] = 'keepalive'
        data['address'] = address
        data['port'] = port
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def key_create(self):
        data = {}
        data['action'] = 'key_create'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def key_expand(self, key):
        data = {}
        data['action'] = 'key_expand'
        data['key'] = key
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def ledger(self,
               account,
               count,
               representative=False,
               weight=False,
               pending=False,
               modified_since=0,
               sorting=False):
        data = {}
        data['action'] = 'ledger'
        data['account'] = account
        data['count'] = count
        if representative: data['representative'] = True
        if weight: data['weight'] = True
        if pending: data['pending'] = True
        if modified_since: data['modified_since'] = modified_since
        if sorting: data['sorting'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def block_create(self,
                     balance,
                     key,
                     representative,
                     link,
                     previous,
                     work=None,
                     json_block=False):
        data = {}
        data['action'] = 'block_create'
        data['type'] = 'state'
        data['balance'] = balance
        data['key'] = key
        data['representative'] = representative
        data['link'] = link
        data['previous'] = previous
        if work: data['work'] = work
        if json_block: data['json_block'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def node_id(self):
        data = {}
        data['action'] = 'node_id'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def node_id_delete(self):
        data = {}
        data['action'] = 'node_id_delete'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def payment_begin(self, wallet):
        data = {}
        data['action'] = 'payment_begin'
        data['wallet'] = wallet
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def payment_init(self, wallet):
        data = {}
        data['action'] = 'payment_init'
        data['wallet'] = wallet
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def payment_end(self, account, wallet):
        data = {}
        data['action'] = 'payment_end'
        data['account'] = account
        data['wallet'] = wallet
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def payment_wait(self, account, amount, timeout):
        data = {}
        data['action'] = 'payment_wait'
        data['account'] = account
        data['amount'] = amount
        data['timeout'] = timeout
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def process(self, block, force=False, subtype=None, json_block=False):
        data = {}
        data['action'] = 'process'
        data['block'] = block
        if force: data['force'] = True
        if subtype: data['subtype'] = subtype
        if json_block: data['json_block'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def receive(self, wallet, account, block, work=None):
        data = {}
        data['action'] = 'receive'
        data['wallet'] = wallet
        data['account'] = account
        data['block'] = block
        if work: data['work'] = work
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def receive_minimum(self):
        data = {}
        data['action'] = 'receive_minimum'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def receive_minimum_set(self, amount):
        data = {}
        data['action'] = 'receive_minimum_set'
        data['amount'] = amount
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def representatives(self, count=0, sorting=False):
        data = {}
        data['action'] = 'representatives'
        if count: data['count'] = count
        if sorting: data['sorting'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def representatives_online(self, weight=False):
        data = {}
        data['action'] = 'representatives_online'
        if weight: data['weight'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_representative(self, wallet):
        data = {}
        data['action'] = 'wallet_representative'
        data['wallet'] = wallet
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_representative_set(self,
                                  wallet,
                                  representative,
                                  update_existing_accounts=False):
        data = {}
        data['action'] = 'wallet_representative_set'
        data['wallet'] = wallet
        data['representative'] = representative
        if update_existing_accounts: data['update_existing_accounts'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def republish(self, _hash, count=0, sources=0, destinations=0):
        data = {}
        data['action'] = 'republish'
        data['hash'] = _hash
        if sources:
            data['sources'] = sources
            data['count'] = count
        if destinations:
            data['destinations'] = destinations
            data['count'] = count
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def search_pending(self, wallet):
        data = {}
        data['action'] = 'search_pending'
        data['wallet'] = wallet
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def search_pending_all(self):
        data = {}
        data['action'] = 'search_pending_all'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def send(self, wallet, source, destination, amount, _id=None, work=None):
        data = {}
        data['action'] = 'send'
        data['wallet'] = wallet
        data['source'] = source
        data['destination'] = destination
        data['amount'] = amount
        if _id: data['id'] = _id
        if work: data['work'] = work
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def sign(self, key='', wallet='', account='', _hash='', json_block=False):
        data = {}
        data['action'] = 'sign'
        if key: data['key'] = key
        if wallet: data['wallet'] = wallet
        if account: data['account'] = account
        if _hash: data['_hash'] = _hash
        if json_block: data['json_block'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def stats(self, _type):
        data = {}
        data['action'] = 'stats'
        data['type'] = _type
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def stats_clear(self):
        data = {}
        data['action'] = 'stats_clear'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def stop(self):
        data = {}
        data['action'] = 'stop'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def validate_account_number(self, account):
        data = {}
        data['action'] = 'validate_account_number'
        data['account'] = account
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def successors(self, block, count=1, offset=0, reverse=False):
        data = {}
        data['action'] = 'successors'
        data['block'] = block
        data['count'] = count
        if offset: data['offset'] = offset
        if reverse: data['reverse'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def version(self):
        data = {}
        data['action'] = 'version'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def peers(self, peer_details=False):
        data = {}
        data['action'] = 'peers'
        if peer_details: data['peer_details'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def pending(self,
                account,
                count=1,
                threshold=0,
                source=False,
                include_active=False):
        data = {}
        data['action'] = 'pending'
        data['account'] = account
        data['count'] = count
        if threshold: data['threshold'] = threshold
        if source: data['source'] = True
        if include_active: data['include_active'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def pending_exists(self, _hash):
        data = {}
        data['action'] = 'pending_exists'
        data['hash'] = _hash
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def unchecked(self, count=1):
        data = {}
        data['action'] = 'unchecked'
        data['count'] = count
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def unchecked_clear(self):
        data = {}
        data['action'] = 'unchecked_clear'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def unchecked_get(self, _hash, json_block=False):
        data = {}
        data['action'] = 'unchecked_get'
        data['hash'] = _hash
        if json_block: data['json_block'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def unchecked_keys(self, key, count=1, json_block=False):
        data = {}
        data['action'] = 'unchecked_keys'
        data['key'] = key
        data['count'] = count
        if json_block: data['json_block'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def unopened(self, account=None, count=0):
        data = {}
        data['action'] = 'unopened'
        if account: data['account'] = account
        if count: data['count'] = count
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def uptime(self):
        data = {}
        data['action'] = 'uptime'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_add(self, wallet, key, work=False):
        data = {}
        data['action'] = 'wallet_add'
        data['wallet'] = wallet
        data['key'] = key
        if work: data['work'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_add_watch(self, wallet, accounts):
        data = {}
        data['action'] = 'wallet_add_watch'
        data['wallet'] = wallet
        data['accounts'] = accounts
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_balances(self, wallet, threshold=0):
        data = {}
        data['action'] = 'wallet_balances'
        data['wallet'] = wallet
        if threshold: data['threshold'] = threshold
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_change_seed(self, wallet, seed, count=0):
        data = {}
        data['action'] = 'wallet_change_seed'
        data['wallet'] = wallet
        data['seed'] = seed
        if count: data['count'] = count
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_contains(self, wallet, account):
        data = {}
        data['action'] = 'wallet_contains'
        data['wallet'] = wallet
        data['account'] = account
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_create(self, seed=''):
        data = {}
        data['action'] = 'wallet_create'
        if seed: data['seed'] = seed
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_destroy(self, wallet):
        data = {}
        data['action'] = 'wallet_destroy'
        data['wallet'] = wallet
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_export(self, wallet):
        data = {}
        data['action'] = 'wallet_export'
        data['wallet'] = wallet
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_frontiers(self, wallet):
        data = {}
        data['action'] = 'wallet_frontiers'
        data['wallet'] = wallet
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_info(self, wallet):
        data = {}
        data['action'] = 'wallet_info'
        data['wallet'] = wallet
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_history(self, wallet, modified_since=0):
        data = {}
        data['action'] = 'wallet_history'
        data['wallet'] = wallet
        if modified_since: data['modified_since'] = modified_since
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

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
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_pending(self,
                       wallet,
                       count=1,
                       threshold=0,
                       source=False,
                       include_active=False):
        data = {}
        data['action'] = 'wallet_pending'
        data['wallet'] = wallet
        data['count'] = count
        if threshold: data['threshold'] = threshold
        if source: data['source'] = True
        if include_active: data['include_active'] = True
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_republish(self, wallet, count=1):
        data = {}
        data['action'] = 'wallet_republish'
        data['wallet'] = wallet
        data['count'] = count
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_work_get(self, wallet):
        data = {}
        data['action'] = 'wallet_work_get'
        data['wallet'] = wallet
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def password_change(self, wallet, password):
        data = {}
        data['action'] = 'password_change'
        data['wallet'] = wallet
        data['password'] = password
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def password_enter(self, wallet, password):
        data = {}
        data['action'] = 'password_enter'
        data['wallet'] = wallet
        data['password'] = password
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def password_valid(self, wallet):
        data = {}
        data['action'] = 'password_valid'
        data['wallet'] = wallet
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_lock(self, wallet):
        data = {}
        data['action'] = 'wallet_lock'
        data['wallet'] = wallet
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def wallet_locked(self, wallet):
        data = {}
        data['action'] = 'wallet_locked'
        data['wallet'] = wallet
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def work_cancel(self, _hash):
        data = {}
        data['action'] = 'work_cancel'
        data['hash'] = _hash
        return json.loads(
            self.session.post(self.work_url, data=json.dumps(data)).text)

    def work_generate(self, _hash, use_peers=False, difficulty=None):
        data = {}
        data['action'] = 'work_generate'
        data['hash'] = _hash
        if use_peers: data['use_peers'] = True
        if difficulty: data['difficulty'] = difficulty
        return json.loads(
            self.session.post(self.work_url, data=json.dumps(data)).text)

    def work_get(self, wallet, account):
        data = {}
        data['action'] = 'work_get'
        data['wallet'] = wallet
        data['account'] = account
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def work_set(self, wallet, account, work):
        data = {}
        data['action'] = 'work_set'
        data['wallet'] = wallet
        data['account'] = account
        data['work'] = work
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def work_peer_add(self, address, port):
        data = {}
        data['action'] = 'work_peer_add'
        data['address'] = address
        data['port'] = port
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def work_peers(self):
        data = {}
        data['action'] = 'work_peers'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def work_peers_clear(self):
        data = {}
        data['action'] = 'work_peers_clear'
        return json.loads(
            self.session.post(self.url, data=json.dumps(data)).text)

    def work_validate(self, work, _hash, difficulty=None):
        data = {}
        data['action'] = 'work_validate'
        data['work'] = work
        data['hash'] = _hash
        if difficulty: data['difficulty'] = difficulty
        return json.loads(
            self.session.post(self.work_url, data=json.dumps(data)).text)
