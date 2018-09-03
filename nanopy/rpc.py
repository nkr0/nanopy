import json, requests

session = requests.session()
session.proxies = {}
url = 'http://localhost:7076'


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


def account_info(account):
    data = {}
    data['action'] = 'account_info'
    data['account'] = account
    data['representative'] = 'true'
    data['weight'] = 'true'
    data['pending'] = 'true'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def account_create(wallet, work=False):
    data = {}
    data['action'] = 'account_create'
    data['wallet'] = wallet
    data['work'] = work
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
    data['raw'] = raw
    if head:
        data['head'] = head
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
    if work:
        data['work'] = work
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
    data['work'] = work
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
    data['source'] = source
    data['include_active'] = include_active
    return json.loads(session.post(url, data=json.dumps(data)).text)


def available_supply():
    data = {}
    data['action'] = 'available_supply'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def block(_hash):
    data = {}
    data['action'] = 'block'
    data['hash'] = _hash
    return json.loads(session.post(url, data=json.dumps(data)).text)


def blocks(hashes):
    data = {}
    data['action'] = 'blocks'
    data['hashes'] = hashes
    return json.loads(session.post(url, data=json.dumps(data)).text)


def blocks_info(hashes, pending=False, source=False, balance=False):
    data = {}
    data['action'] = 'blocks_info'
    data['hashes'] = hashes
    data['pending'] = pending
    data['source'] = source
    data['balance'] = balance
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


def bootstrap(address, port):
    data = {}
    data['action'] = 'bootstrap'
    data['address'] = address
    data['port'] = port
    return json.loads(session.post(url, data=json.dumps(data)).text)


def bootstrap_any():
    data = {}
    data['action'] = 'bootstrap_any'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def chain(block, count):
    data = {}
    data['action'] = 'chain'
    data['block'] = block
    data['count'] = count
    return json.loads(session.post(url, data=json.dumps(data)).text)


def confirmation_history():
    data = {}
    data['action'] = 'confirmation_history'
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
           modified_since=False,
           sorting=False):
    data = {}
    data['action'] = 'ledger'
    data['account'] = account
    data['count'] = count
    data['representative'] = representative
    data['weight'] = weight
    data['pending'] = pending
    data['modified_since'] = modified_since
    data['sorting'] = sorting
    return json.loads(session.post(url, data=json.dumps(data)).text)


def block_create(balance, key, representative, link, previous, work=None):
    data = {}
    data['action'] = 'block_create'
    data['type'] = 'state'
    data['balance'] = balance
    data['key'] = key
    data['representative'] = representative
    data['link'] = link
    data['previous'] = previous
    if work: data['work'] = work
    return json.loads(session.post(url, data=json.dumps(data)).text)


def process(block, force=False):
    data = {}
    data['action'] = 'process'
    data['block'] = block
    data['force'] = force
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


def representatives():
    data = {}
    data['action'] = 'representatives'
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
    data['sorting'] = sorting
    return json.loads(session.post(url, data=json.dumps(data)).text)


def representatives_online():
    data = {}
    data['action'] = 'representatives_online'
    return json.loads(session.post(url, data=json.dumps(data)).text)


def work_generate(_hash):
    data = {}
    data['action'] = 'work_generate'
    data['hash'] = _hash
    return json.loads(session.post(url, data=json.dumps(data)).text)
