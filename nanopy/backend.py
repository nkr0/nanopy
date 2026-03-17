#!/usr/bin/env python3
import json, requests
from flask import Flask, request, abort

session = requests.session()
session.proxies = {}
url = 'http://localhost:55000'

rpc_enabled = ['block_count', 'account_balance']

app = Flask(__name__)


@app.route('/')
def index():
    return "Print enabled rpc calls and other stats here"


@app.route('/', methods=['POST'])
def process_rpc():
    try:
        if not json.loads(request.data)['action'] in rpc_enabled:
            abort(400)
        response = session.post(url, data=request.data).text
        return response, 200
    except:
        abort(400)


if __name__ == '__main__':
    app.run()
