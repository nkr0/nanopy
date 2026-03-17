import json, requests

session = requests.session()
session.proxies = {}
url = 'http://localhost:7076'
work_url = ''


def account_balance(account):
    data = {}
    data['action'] = 'account_balance'
    data['account'] = account
    return json.loads(session.post(url, data=json.dumps(data)).text)


def account_block_count(account):
    data = {}
    data['action'] = 'account_block_count'
    data['account'] = account
    return json.loads(session.post(url, data=json.dumps(data)).text)


def account_info(account, representative=False, weight=False, pending=False):
    data = {}
    data['action'] = 'account_info'
    data['account'] = account
    if representative: data['representative'] = True
    if weight: data['weight'] = True
    if pending: data['pending'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def account_create(wallet, index=0, work=False):
    data = {}
    data['action'] = 'account_create'
    data['wallet'] = wallet
    if index: data['index'] = index
    if work: data['work'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def account_get(key):
    data = {}
    data['action'] = 'account_get'
    data['key'] = key
    return json.loads(session.post(url, data=json.dumps(data)).text)


def account_history(account, count=1, raw=False, head=None):
    data = {}
    data['action'] = 'account_history'
    data['account'] = account
    data['count'] = count
    if raw: data['raw'] = True
    if head: data['head'] = head
    return json.loads(session.post(url, data=json.dumps(data)).text)


def account_list(wallet):
    data = {}
    data['action'] = 'account_list'
    data['wallet'] = wallet
    return json.loads(session.post(url, data=json.dumps(data)).text)


def account_move(wallet, source, accounts):
    data = {}
    data['action'] = 'account_move'
    data['wallet'] = wallet
    data['source'] = source
    data['accounts'] = accounts
    return json.loads(session.post(url, data=json.dumps(data)).text)


def account_key(account):
    data = {}
    data['action'] = 'account_key'
    data['account'] = account
    return json.loads(session.post(url, data=json.dumps(data)).text)


def account_remove(wallet, account):
    data = {}
    data['action'] = 'account_remove'
    data['wallet'] = wallet
    data['account'] = account
    return json.loads(session.post(url, data=json.dumps(data)).text)


def account_representative(account):
    data = {}
    data['action'] = 'account_representative'
    data['account'] = account
    return json.loads(session.post(url, data=json.dumps(data)).text)


def account_representative_set(wallet, account, representative, work=None):
    data = {}
    data['action'] = 'account_representative_set'
    data['wallet'] = wallet
    data['account'] = account
    data['representative'] = representative
    if work: data['work'] = work
    return json.loads(session.post(url, data=json.dumps(data)).text)


def account_weight(account):
    data = {}
    data['action'] = 'account_weight'
    data['account'] = account
    return json.loads(session.post(url, data=json.dumps(data)).text)


def accounts_balances(accounts):
    data = {}
    data['action'] = 'accounts_balances'
    data['accounts'] = accounts
    return json.loads(session.post(url, data=json.dumps(data)).text)


def accounts_create(wallet, count, work=False):
    data = {}
    data['action'] = 'accounts_create'
    data['wallet'] = wallet
    data['count'] = count
    if work: data['work'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def accounts_frontiers(accounts):
    data = {}
    data['action'] = 'accounts_frontiers'
    data['accounts'] = accounts
    return json.loads(session.post(url, data=json.dumps(data)).text)


def accounts_pending(accounts,
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
    return json.loads(session.post(url, data=json.dumps(data)).text)


def available_supply():
    data = {}
    data['action'] = 'available_supply'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def block_info(_hash, json_block=False):
    data = {}
    data['action'] = 'block_info'
    data['hash'] = _hash
    if json_block: data['json_block'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def blocks(hashes):
    data = {}
    data['action'] = 'blocks'
    data['hashes'] = hashes
    return json.loads(session.post(url, data=json.dumps(data)).text)


def blocks_info(hashes,
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
    return json.loads(session.post(url, data=json.dumps(data)).text)


def block_account(_hash):
    data = {}
    data['action'] = 'block_account'
    data['hash'] = _hash
    return json.loads(session.post(url, data=json.dumps(data)).text)


def block_confirm(_hash):
    data = {}
    data['action'] = 'block_confirm'
    data['hash'] = _hash
    return json.loads(session.post(url, data=json.dumps(data)).text)


def block_count():
    data = {}
    data['action'] = 'block_count'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def block_count_type():
    data = {}
    data['action'] = 'block_count_type'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def block_hash(block, json_block=False):
    data = {}
    data['action'] = 'block_hash'
    if type(block) == str:
        data['block'] = block
    else:
        data['block'] = json.dumps(block)
    if json_block: data['json_block'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def bootstrap(address, port):
    data = {}
    data['action'] = 'bootstrap'
    data['address'] = address
    data['port'] = port
    return json.loads(session.post(url, data=json.dumps(data)).text)


def bootstrap_lazy(hash_, force=False):
    data = {}
    data['action'] = 'bootstrap_lazy'
    data['hash'] = hash_
    if force: data['force'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def bootstrap_any():
    data = {}
    data['action'] = 'bootstrap_any'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def bootstrap_status():
    data = {}
    data['action'] = 'bootstrap_status'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def chain(block, count, offset=0, reverse=False):
    data = {}
    data['action'] = 'chain'
    data['block'] = block
    data['count'] = count
    if offset: data['offset'] = offset
    if reverse: data['reverse'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def confirmation_active(announcements=0):
    data = {}
    data['action'] = 'confirmation_active'
    if announcements: data['announcements'] = announcements
    return json.loads(session.post(url, data=json.dumps(data)).text)


def confirmation_history():
    data = {}
    data['action'] = 'confirmation_history'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def confirmation_info(root,
                      contents=True,
                      representatives=False,
                      json_block=False):
    data = {}
    data['action'] = 'confirmation_info'
    data['root'] = root
    if not contents: data['contents'] = False
    if representatives: data['representatives'] = True
    if json_block: data['json_block'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def confirmation_quorum(peer_details=False):
    data = {}
    data['action'] = 'confirmation_quorum'
    if peer_details: data['peer_details'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def delegators(account):
    data = {}
    data['action'] = 'delegators'
    data['account'] = account
    return json.loads(session.post(url, data=json.dumps(data)).text)


def delegators_count(account):
    data = {}
    data['action'] = 'delegators_count'
    data['account'] = account
    return json.loads(session.post(url, data=json.dumps(data)).text)


def deterministic_key(seed, index):
    data = {}
    data['action'] = 'deterministic_key'
    data['seed'] = seed
    data['index'] = index
    return json.loads(session.post(url, data=json.dumps(data)).text)


def frontiers(account, count):
    data = {}
    data['action'] = 'frontiers'
    data['account'] = account
    data['count'] = count
    return json.loads(session.post(url, data=json.dumps(data)).text)


def frontier_count():
    data = {}
    data['action'] = 'frontier_count'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def mrai_from_raw(amount):
    data = {}
    data['action'] = 'mrai_from_raw'
    data['amount'] = amount
    return json.loads(session.post(url, data=json.dumps(data)).text)


def mrai_to_raw(amount):
    data = {}
    data['action'] = 'mrai_to_raw'
    data['amount'] = amount
    return json.loads(session.post(url, data=json.dumps(data)).text)


def krai_from_raw(amount):
    data = {}
    data['action'] = 'krai_from_raw'
    data['amount'] = amount
    return json.loads(session.post(url, data=json.dumps(data)).text)


def krai_to_raw(amount):
    data = {}
    data['action'] = 'krai_to_raw'
    data['amount'] = amount
    return json.loads(session.post(url, data=json.dumps(data)).text)


def rai_from_raw(amount):
    data = {}
    data['action'] = 'rai_from_raw'
    data['amount'] = amount
    return json.loads(session.post(url, data=json.dumps(data)).text)


def rai_to_raw(amount):
    data = {}
    data['action'] = 'rai_to_raw'
    data['amount'] = amount
    return json.loads(session.post(url, data=json.dumps(data)).text)


def keepalive(address, port):
    data = {}
    data['action'] = 'keepalive'
    data['address'] = address
    data['port'] = port
    return json.loads(session.post(url, data=json.dumps(data)).text)


def key_create():
    data = {}
    data['action'] = 'key_create'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def key_expand(key):
    data = {}
    data['action'] = 'key_expand'
    data['key'] = key
    return json.loads(session.post(url, data=json.dumps(data)).text)


def ledger(account,
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
    return json.loads(session.post(url, data=json.dumps(data)).text)


def block_create(balance,
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
    return json.loads(session.post(url, data=json.dumps(data)).text)


def node_id():
    data = {}
    data['action'] = 'node_id'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def node_id_delete():
    data = {}
    data['action'] = 'node_id_delete'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def payment_begin(wallet):
    data = {}
    data['action'] = 'payment_begin'
    data['wallet'] = wallet
    return json.loads(session.post(url, data=json.dumps(data)).text)


def payment_init(wallet):
    data = {}
    data['action'] = 'payment_init'
    data['wallet'] = wallet
    return json.loads(session.post(url, data=json.dumps(data)).text)


def payment_end(account, wallet):
    data = {}
    data['action'] = 'payment_end'
    data['account'] = account
    data['wallet'] = wallet
    return json.loads(session.post(url, data=json.dumps(data)).text)


def payment_wait(account, amount, timeout):
    data = {}
    data['action'] = 'payment_wait'
    data['account'] = account
    data['amount'] = amount
    data['timeout'] = timeout
    return json.loads(session.post(url, data=json.dumps(data)).text)


def process(block, force=False, subtype=None, json_block=False):
    data = {}
    data['action'] = 'process'
    data['block'] = block
    if force: data['force'] = True
    if subtype: data['subtype'] = subtype
    if json_block: data['json_block'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def receive(wallet, account, block, work=None):
    data = {}
    data['action'] = 'receive'
    data['wallet'] = wallet
    data['account'] = account
    data['block'] = block
    if work: data['work'] = work
    return json.loads(session.post(url, data=json.dumps(data)).text)


def receive_minimum():
    data = {}
    data['action'] = 'receive_minimum'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def receive_minimum_set(amount):
    data = {}
    data['action'] = 'receive_minimum_set'
    data['amount'] = amount
    return json.loads(session.post(url, data=json.dumps(data)).text)


def representatives(count=0, sorting=False):
    data = {}
    data['action'] = 'representatives'
    if count: data['count'] = count
    if sorting: data['sorting'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def representatives_online(weight=False):
    data = {}
    data['action'] = 'representatives_online'
    if weight: data['weight'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_representative(wallet):
    data = {}
    data['action'] = 'wallet_representative'
    data['wallet'] = wallet
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_representative_set(wallet,
                              representative,
                              update_existing_accounts=False):
    data = {}
    data['action'] = 'wallet_representative_set'
    data['wallet'] = wallet
    data['representative'] = representative
    if update_existing_accounts: data['update_existing_accounts'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def republish(_hash, count=0, sources=0, destinations=0):
    data = {}
    data['action'] = 'republish'
    data['hash'] = _hash
    if sources:
        data['sources'] = sources
        data['count'] = count
    if destinations:
        data['destinations'] = destinations
        data['count'] = count
    return json.loads(session.post(url, data=json.dumps(data)).text)


def search_pending(wallet):
    data = {}
    data['action'] = 'search_pending'
    data['wallet'] = wallet
    return json.loads(session.post(url, data=json.dumps(data)).text)


def search_pending_all():
    data = {}
    data['action'] = 'search_pending_all'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def send(wallet, source, destination, amount, _id=None, work=None):
    data = {}
    data['action'] = 'send'
    data['wallet'] = wallet
    data['source'] = source
    data['destination'] = destination
    data['amount'] = amount
    if _id: data['id'] = _id
    if work: data['work'] = work
    return json.loads(session.post(url, data=json.dumps(data)).text)


def sign(key='', wallet='', account='', _hash='', json_block=False):
    data = {}
    data['action'] = 'sign'
    if key: data['key'] = key
    if wallet: data['wallet'] = wallet
    if account: data['account'] = account
    if _hash: data['_hash'] = _hash
    if json_block: data['json_block'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def stats(_type):
    data = {}
    data['action'] = 'stats'
    data['type'] = _type
    return json.loads(session.post(url, data=json.dumps(data)).text)


def stats_clear():
    data = {}
    data['action'] = 'stats_clear'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def stop():
    data = {}
    data['action'] = 'stop'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def validate_account_number(account):
    data = {}
    data['action'] = 'validate_account_number'
    data['account'] = account
    return json.loads(session.post(url, data=json.dumps(data)).text)


def successors(block, count=1, offset=0, reverse=False):
    data = {}
    data['action'] = 'successors'
    data['block'] = block
    data['count'] = count
    if offset: data['offset'] = offset
    if reverse: data['reverse'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def version():
    data = {}
    data['action'] = 'version'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def peers(peer_details=False):
    data = {}
    data['action'] = 'peers'
    if peer_details: data['peer_details'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def pending(account, count=1, threshold=0, source=False, include_active=False):
    data = {}
    data['action'] = 'pending'
    data['account'] = account
    data['count'] = count
    if threshold: data['threshold'] = threshold
    if source: data['source'] = True
    if include_active: data['include_active'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def pending_exists(_hash):
    data = {}
    data['action'] = 'pending_exists'
    data['hash'] = _hash
    return json.loads(session.post(url, data=json.dumps(data)).text)


def unchecked(count=1):
    data = {}
    data['action'] = 'unchecked'
    data['count'] = count
    return json.loads(session.post(url, data=json.dumps(data)).text)


def unchecked_clear():
    data = {}
    data['action'] = 'unchecked_clear'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def unchecked_get(_hash, json_block=False):
    data = {}
    data['action'] = 'unchecked_get'
    data['hash'] = _hash
    if json_block: data['json_block'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def unchecked_keys(key, count=1, json_block=False):
    data = {}
    data['action'] = 'unchecked_keys'
    data['key'] = key
    data['count'] = count
    if json_block: data['json_block'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def unopened(account=None, count=0):
    data = {}
    data['action'] = 'unopened'
    if account: data['account'] = account
    if count: data['count'] = count
    return json.loads(session.post(url, data=json.dumps(data)).text)


def uptime():
    data = {}
    data['action'] = 'uptime'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_add(wallet, key, work=False):
    data = {}
    data['action'] = 'wallet_add'
    data['wallet'] = wallet
    data['key'] = key
    if work: data['work'] = True
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_add_watch(wallet, accounts):
    data = {}
    data['action'] = 'wallet_add_watch'
    data['wallet'] = wallet
    data['accounts'] = accounts
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_balances(wallet, threshold=0):
    data = {}
    data['action'] = 'wallet_balances'
    data['wallet'] = wallet
    if threshold: data['threshold'] = threshold
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_change_seed(wallet, seed, count=0):
    data = {}
    data['action'] = 'wallet_change_seed'
    data['wallet'] = wallet
    data['seed'] = seed
    if count: data['count'] = count
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_contains(wallet, account):
    data = {}
    data['action'] = 'wallet_contains'
    data['wallet'] = wallet
    data['account'] = account
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_create(seed=''):
    data = {}
    data['action'] = 'wallet_create'
    if seed: data['seed'] = seed
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_destroy(wallet):
    data = {}
    data['action'] = 'wallet_destroy'
    data['wallet'] = wallet
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_export(wallet):
    data = {}
    data['action'] = 'wallet_export'
    data['wallet'] = wallet
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_frontiers(wallet):
    data = {}
    data['action'] = 'wallet_frontiers'
    data['wallet'] = wallet
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_info(wallet):
    data = {}
    data['action'] = 'wallet_info'
    data['wallet'] = wallet
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_history(wallet, modified_since=0):
    data = {}
    data['action'] = 'wallet_history'
    data['wallet'] = wallet
    if modified_since: data['modified_since'] = modified_since
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_ledger(wallet,
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
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_pending(wallet,
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
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_republish(wallet, count=1):
    data = {}
    data['action'] = 'wallet_republish'
    data['wallet'] = wallet
    data['count'] = count
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_work_get(wallet):
    data = {}
    data['action'] = 'wallet_work_get'
    data['wallet'] = wallet
    return json.loads(session.post(url, data=json.dumps(data)).text)


def password_change(wallet, password):
    data = {}
    data['action'] = 'password_change'
    data['wallet'] = wallet
    data['password'] = password
    return json.loads(session.post(url, data=json.dumps(data)).text)


def password_enter(wallet, password):
    data = {}
    data['action'] = 'password_enter'
    data['wallet'] = wallet
    data['password'] = password
    return json.loads(session.post(url, data=json.dumps(data)).text)


def password_valid(wallet):
    data = {}
    data['action'] = 'password_valid'
    data['wallet'] = wallet
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_lock(wallet):
    data = {}
    data['action'] = 'wallet_lock'
    data['wallet'] = wallet
    return json.loads(session.post(url, data=json.dumps(data)).text)


def wallet_locked(wallet):
    data = {}
    data['action'] = 'wallet_locked'
    data['wallet'] = wallet
    return json.loads(session.post(url, data=json.dumps(data)).text)


def work_cancel(_hash):
    data = {}
    data['action'] = 'work_cancel'
    data['hash'] = _hash
    return json.loads(session.post(work_url, data=json.dumps(data)).text)


def work_generate(_hash, use_peers=False):
    data = {}
    data['action'] = 'work_generate'
    data['hash'] = _hash
    if use_peers: data['use_peers'] = True
    return json.loads(session.post(work_url, data=json.dumps(data)).text)


def work_get(wallet, account):
    data = {}
    data['action'] = 'work_get'
    data['wallet'] = wallet
    data['account'] = account
    return json.loads(session.post(url, data=json.dumps(data)).text)


def work_set(wallet, account, work):
    data = {}
    data['action'] = 'work_set'
    data['wallet'] = wallet
    data['account'] = account
    data['work'] = work
    return json.loads(session.post(url, data=json.dumps(data)).text)


def work_peer_add(address, port):
    data = {}
    data['action'] = 'work_peer_add'
    data['address'] = address
    data['port'] = port
    return json.loads(session.post(url, data=json.dumps(data)).text)


def work_peers():
    data = {}
    data['action'] = 'work_peers'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def work_peers_clear():
    data = {}
    data['action'] = 'work_peers_clear'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def work_validate(work, _hash):
    data = {}
    data['action'] = 'work_validate'
    data['work'] = work
    data['hash'] = _hash
    return json.loads(session.post(work_url, data=json.dumps(data)).text)
