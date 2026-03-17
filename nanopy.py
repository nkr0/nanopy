import sys, os, random, json, ctypes, requests, ed25519_blake2b, hashlib

rpc = requests.session()
rpc.proxies = {}
url=''

def nano_block(): return dict([('type', 'state'), ('account', ''), ('previous', '0000000000000000000000000000000000000000000000000000000000000000'), ('balance', ''), ('representative', ''), ('link', '0000000000000000000000000000000000000000000000000000000000000000'), ('work', ''), ('signature', '')])

def nano_account(address):
	if (len(address) == 64 and (address[:4] == 'xrb_')) or (len(address) == 65 and (address[:5] == 'nano_')):
		account_map = "13456789abcdefghijkmnopqrstuwxyz"
		account_lookup = {}
		for i in range(0,32): account_lookup[account_map[i]] = bin(i)[2:].zfill(5) # "{0:0>5b}".format(i)

		acrop_key = address[-60:-8]
		acrop_check = address[-8:]

		number_l = ""
		for x in range(0, len(acrop_key)): number_l+=account_lookup[acrop_key[x]]
		number_l = hex(int(number_l[4:], 2))[2:]

		check_l = ""
		for x in range(0, len(acrop_check)): check_l+=account_lookup[acrop_check[x]]
		check_l=hex(int(check_l, 2))[2:]
		check_l="".join(reversed([check_l[i:i+2] for i in range(0, len(check_l), 2)]))

		h = hashlib.blake2b(digest_size=5)
		h.update(bytes.fromhex(number_l))
		if (h.hexdigest() == check_l):return number_l #.hex.upper()
	return False

def account_nano(account):
	account_map = "13456789abcdefghijkmnopqrstuwxyz"
	account_lookup = {}
	for i in range(0,32): account_lookup[bin(i)[2:].zfill(5)] = account_map[i] # account_lookup["{0:0>5b}".format(i)]

	h = hashlib.blake2b(digest_size=5)
	h.update(bytes.fromhex(account))
	checksum = h.hexdigest()

	checksum="".join(reversed([checksum[i:i+2] for i in range(0, len(checksum), 2)]))
	checksum=bin(int(checksum, 16))[2:].zfill(40) # "{0:0>40b}".format(int(checksum, 16))

	encode_check = ''
	for x in range(0,int(len(checksum)/5)): encode_check += account_lookup[checksum[x*5:x*5+5]]

	account = bin(int(account, 16))[2:].zfill(260) # "{0:0>260b}".format(int(account, 16))

	encode_account = ''
	for x in range(0,int(len(account)/5)): encode_account += account_lookup[account[x*5:x*5+5]]

	return 'xrb_'+encode_account+encode_check

def seed_keys(seed, index):
	h = hashlib.blake2b(digest_size=32)

	h.update(bytes.fromhex(seed))
	h.update(index.to_bytes(4, byteorder='big'))

	account_key = h.digest()
	return account_key, ed25519_blake2b.publickey(account_key)

def seed_nano(seed, index):
	_, pk = seed_keys(seed, index)
	return account_nano(pk.hex())

def pow_threshold(check):
	if check > b'\xFF\xFF\xFF\xC0\x00\x00\x00\x00': return True
	return False

def pow_validate(pow, hash):
	pow_data = bytearray.fromhex(pow)
	hash_data = bytearray.fromhex(hash)

	h = hashlib.blake2b(digest_size=8)
	pow_data.reverse()
	h.update(pow_data)
	h.update(hash_data)
	final = bytearray(h.digest())
	final.reverse()

	return pow_threshold(final)

def pow_generate(hash):
	try:
		lib=ctypes.CDLL(os.path.dirname(os.path.abspath(__file__))+"/libnanopow.so")
		lib.pow_generate.restype = ctypes.c_char_p
		return lib.pow_generate(ctypes.c_char_p(hash.encode("utf-8"))).decode("utf-8")
	except OSError:
		hash_bytes = bytearray.fromhex(hash)
		while True:
			random_bytes = bytearray((random.getrandbits(8) for i in range(8)))
			for r in range(0,256):
				random_bytes[7] =(random_bytes[7] + r) % 256
				h = hashlib.blake2b(digest_size=8)
				h.update(random_bytes)
				h.update(hash_bytes)
				final = bytearray(h.digest())
				final.reverse()
				if pow_threshold(final):
					random_bytes.reverse()
					return random_bytes.hex()

def block_hash(block):
	bh = hashlib.blake2b(digest_size=32)

	bh.update(bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000006"))
	bh.update(bytes.fromhex(nano_account(block["account"])))
	bh.update(bytes.fromhex(block["previous"]))
	bh.update(bytes.fromhex(nano_account(block["representative"])))
	bh.update(bytes.fromhex(format(int(block["balance"]),'032x')))
	bh.update(bytes.fromhex(block["link"]))

	return bh.digest()

def sign_block(seed, index, block):	return ed25519_blake2b.signature(block_hash(block),*seed_keys(seed, index)).hex()

def account_info(account):
	data={}
	data['action']='account_info'
	data['account']=account
	data['representative']='true'
	data['weight']='true'
	data['pending']='true'
	return json.loads(rpc.post(url, data = json.dumps(data)).text)

def accounts_pending(accounts):
	data={}
	data['action']='accounts_pending'
	data['accounts']=accounts
	data['count']=1
	return json.loads(rpc.post(url, data = json.dumps(data)).text)

def accounts_balances(accounts):
	# ~ data={}
	# ~ data['action']='accounts_balances'
	# ~ data['accounts']=accounts
	# ~ return json.loads(rpc.post(url, data = json.dumps(data)).text)
	##### temporary solution until api is available ###
	info={}
	for account in accounts:
		info[account]=account_info(account)
	return info

def available_supply():
	data={}
	data['action']='available_supply'
	return json.loads(rpc.post(url, data = json.dumps(data)).text)

def blocks_info(hashes):
	data={}
	data['action']='blocks_info'
	data['hashes']=hashes
	return json.loads(rpc.post(url, data = json.dumps(data)).text)

def work_generate(hash):
	data={}
	data['action']='work_generate'
	data['hash']=hash
	return json.loads(rpc.post(url, data = json.dumps(data)).text)

def process(block):
	data={}
	data['action']='process'
	data['block']=block
	return json.loads(rpc.post(url, data = json.dumps(data)).text)

# ~ if __name__ == '__main__':
