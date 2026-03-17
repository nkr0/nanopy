import json, urllib.request, urllib.parse

all = [
    'account_balance', 'account_block_count', 'account_info', 'account_create',
    'account_get', 'account_history', 'account_list', 'account_move',
    'account_key', 'account_remove', 'account_representative',
    'account_representative_set', 'account_weight', 'accounts_balances',
    'accounts_create', 'accounts_frontiers', 'accounts_pending',
    'available_supply', 'block', 'blocks', 'blocks_info', 'block_account',
    'block_confirm', 'block_count', 'block_count_type', 'bootstrap',
    'bootstrap_any', 'chain', 'confirmation_history', 'delegators',
    'delegators_count', 'deterministic_key', 'frontiers', 'frontier_count',
    'mrai_from_raw', 'mrai_to_raw', 'krai_from_raw', 'krai_to_raw',
    'rai_from_raw', 'rai_to_raw', 'keepalive', 'key_create', 'key_expand',
    'ledger', 'block_create', 'payment_begin', 'payment_init', 'payment_end',
    'payment_wait', 'process', 'receive', 'receive_minimum',
    'receive_minimum_set', 'representatives', 'representatives_online',
    'wallet_representative', 'wallet_representative_set', 'republish',
    'search_pending', 'search_pending_all', 'send', 'stats', 'stop',
    'validate_account_number', 'successors', 'version', 'peers', 'pending',
    'pending_exists', 'unchecked', 'unchecked_clear', 'unchecked_get',
    'unchecked_keys', 'wallet_add', 'wallet_add_watch', 'wallet_balances',
    'wallet_change_seed', 'wallet_contains', 'wallet_create', 'wallet_destroy',
    'wallet_export', 'wallet_frontiers', 'wallet_info', 'wallet_ledger',
    'wallet_pending', 'wallet_republish', 'wallet_work_get', 'password_change',
    'password_enter', 'password_valid', 'wallet_lock', 'wallet_locked',
    'work_cancel', 'work_generate', 'work_get', 'work_set', 'work_peer_add',
    'work_peers', 'work_peers_clear', 'work_validate'
]

minimal = [
    'account_balance', 'account_block_count', 'account_info', 'account_history',
    'account_representative', 'account_weight', 'accounts_balances',
    'accounts_frontiers', 'accounts_pending', 'block', 'blocks', 'blocks_info',
    'block_account', 'block_confirm', 'block_count', 'block_count_type',
    'chain', 'confirmation_history', 'delegators', 'delegators_count',
    'frontiers', 'frontier_count', 'process', 'representatives',
    'representatives_online', 'successors', 'version', 'pending',
    'pending_exists', 'unchecked'
]

tools = [
    'account_get', 'account_key', 'available_supply', 'mrai_from_raw',
    'mrai_to_raw', 'krai_from_raw', 'krai_to_raw', 'rai_from_raw', 'rai_to_raw',
    'validate_account_number'
]

work = ['work_cancel', 'work_generate', 'work_validate']

rpc_enabled = minimal


def application(environ, start_response):
    status = '400 Bad Request'
    response = b''
    request_body = b''
    try:
        if environ['SCRIPT_NAME'][5:] in ['nano', 'xrb', 'main', 'live']:
            rpc = 'http://localhost:7076'
        elif environ['SCRIPT_NAME'][5:] == 'beta':
            rpc = 'http://localhost:55000'
        elif environ['SCRIPT_NAME'][5:] == 'banano':
            rpc = 'http://localhost:7072'
        else:
            raise ValueError

        if (environ['REQUEST_METHOD'] == 'GET'):
            query_raw = urllib.parse.parse_qs(environ['QUERY_STRING'])
            query = {}
            for key in query_raw:
                query[key] = str(query_raw.get(key)[0])
            request_body = json.dumps(query).encode('utf-8')
        elif (environ['REQUEST_METHOD'] == 'POST'):
            try:
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            except (ValueError):
                request_body_size = 0
            request_body = environ['wsgi.input'].read(request_body_size)

        if json.loads(request_body)['action'] in rpc_enabled:
            req = urllib.request.Request(rpc, request_body)
            with urllib.request.urlopen(req) as response_raw:
                response = response_raw.read()
            status = '200 OK'
    except:
        pass

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(response)))]
    start_response(status, response_headers)
    return [response]
