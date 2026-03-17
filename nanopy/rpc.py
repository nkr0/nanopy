import json, requests

session = requests.session()
session.proxies = {}
url=''

def account_info(account):
	data={}
	data['action']='account_info'
	data['account']=account
	data['representative']='true'
	data['weight']='true'
	data['pending']='true'
	return json.loads(session.post(url, data = json.dumps(data)).text)

def accounts_pending(accounts, count=1):
	data={}
	data['action']='accounts_pending'
	data['accounts']=accounts
	data['count']=count
	return json.loads(session.post(url, data = json.dumps(data)).text)

def accounts_balances(accounts):
	# ~ data={}
	# ~ data['action']='accounts_balances'
	# ~ data['accounts']=accounts
	# ~ return json.loads(session.post(url, data = json.dumps(data)).text)
	##### temporary solution until api is available ###
	info={}
	for account in accounts:
		info[account]=account_info(account)
	return info

def available_supply():
	data={}
	data['action']='available_supply'
	return json.loads(session.post(url, data = json.dumps(data)).text)

def blocks_info(hashes):
	data={}
	data['action']='blocks_info'
	data['hashes']=hashes
	return json.loads(session.post(url, data = json.dumps(data)).text)

def work_generate(hash):
	data={}
	data['action']='work_generate'
	data['hash']=hash
	return json.loads(session.post(url, data = json.dumps(data)).text)

def process(block):
	data={}
	data['action']='process'
	data['block']=block
	return json.loads(session.post(url, data = json.dumps(data)).text)
