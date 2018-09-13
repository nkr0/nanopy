import json, urllib.request

url = 'http://localhost:7076'

rpc_enabled = ['block_count', 'account_balance']


def application(environ, start_response):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)

    try:
        if not json.loads(request_body)['action'] in rpc_enabled:
            status = '400 Bad Request'

        req = urllib.request.Request(url, request_body)
        with urllib.request.urlopen(req) as response_raw:
            response = response_raw.read()

        response_headers = [('Content-type', 'text/plain'),
                            ('Content-Length', str(len(response)))]

        status = '200 OK'
        start_response(status, response_headers)
        return [response]
    except:
        status = '400 Bad Request'
