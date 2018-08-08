import sys, os, random, json, ctypes, requests, ed25519_blake2b, hashlib
from bitstring import BitArray

rpc = requests.session()
rpc.proxies = {}
url=''

def nano_block(): return dict([('type', 'state'), ('account', ''), ('previous', '0000000000000000000000000000000000000000000000000000000000000000'), ('balance', ''), ('representative', ''), ('link', '0000000000000000000000000000000000000000000000000000000000000000'), ('work', ''), ('signature', '')])

def nano_account(address):
	# Given a string containing an NANO address, confirm validity and provide resulting hex address
	if (len(address) == 64 and (address[:4] == 'xrb_')) or (len(address) == 65 and (address[:5] == 'nano_')):
		account_map = "13456789abcdefghijkmnopqrstuwxyz"				# each index = binary value, account_lookup[0] == '1'
		account_lookup = {}
		for i in range(0,32):											# populate lookup index with prebuilt bitarrays ready to append
			account_lookup[account_map[i]] = BitArray(uint=i,length=5)

		acrop_key = address[-60:-8]										# we want the 52 characters after 'xrb_' or 'nano_' but before the 8-char checksum
		acrop_check = address[-8:]										# extract checksum

		# convert base-32 (5-bit) values to byte string by appending each 5-bit value to the bitstring, essentially bitshifting << 5 and then adding the 5-bit value.
		number_l = BitArray()
		for x in range(0, len(acrop_key)):
			number_l.append(account_lookup[acrop_key[x]])
		number_l = number_l[4:]											# reduce from 260 to 256 bit (upper 4 bits are never used as account is a uint256)

		check_l = BitArray()
		for x in range(0, len(acrop_check)):
			check_l.append(account_lookup[acrop_check[x]])
		check_l.byteswap()												# reverse byte order to match hashing format

		result = number_l.hex.upper()

		# verify checksum
		h = hashlib.blake2b(digest_size=5)
		h.update(number_l.bytes)
		if (h.hexdigest() == check_l.hex):return result
	return False

def account_nano(account):
	# Given a string containing a hex address, encode to public address format with checksum
	account_map = "13456789abcdefghijkmnopqrstuwxyz"					# each index = binary value, account_lookup['00001'] == '3'
	account_lookup = {}
	for i in range(0,32):												# populate lookup index for binary string to base-32 string character
		account_lookup[BitArray(uint=i,length=5).bin] = account_map[i]

	account = BitArray(hex=account)										# hex string > binary

	# get checksum
	h = hashlib.blake2b(digest_size=5)
	h.update(account.bytes)
	checksum = BitArray(hex=h.hexdigest())

	# encode checksum
	checksum.byteswap()													# swap bytes for compatibility with original implementation
	encode_check = ''
	for x in range(0,int(len(checksum.bin)/5)):
			encode_check += account_lookup[checksum.bin[x*5:x*5+5]]		# each 5-bit sequence = a base-32 character from account_map

	# encode account
	encode_account = ''
	while len(account.bin) < 260:										# pad our binary value so it is 260 bits long before conversion (first value can only be 00000 '1' or 00001 '3')
		account = '0b0' + account
	for x in range(0,int(len(account.bin)/5)):
			encode_account += account_lookup[account.bin[x*5:x*5+5]]	# each 5-bit sequence = a base-32 character from account_map

	return 'xrb_'+encode_account+encode_check							# build final address string

def seed_keys(seed, index):
	# Given an account seed and index #, provide the account private and public keys
	h = hashlib.blake2b(digest_size=32)

	seed_data = BitArray(hex=seed)
	seed_index = BitArray(int=index,length=32)

	h.update(seed_data.bytes)
	h.update(seed_index.bytes)

	account_key = h.digest()
	return account_key, ed25519_blake2b.publickey(account_key)

def seed_nano(seed, index):
	# Given an account seed and index #, provide the public address
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
			random_bytes = bytearray((random.getrandbits(8) for i in range(8)))		# generate random array of bytes
			for r in range(0,256):
				random_bytes[7] =(random_bytes[7] + r) % 256						# iterate over the last byte of the random bytes
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

	bh.update(BitArray(hex="0000000000000000000000000000000000000000000000000000000000000006").bytes) # preamble
	bh.update(BitArray(hex=nano_account(block["account"])).bytes)
	bh.update(BitArray(hex=block["previous"]).bytes)
	bh.update(BitArray(hex=nano_account(block["representative"])).bytes)
	bh.update(BitArray(hex=format(int(block["balance"]),'032x')).bytes)
	bh.update(BitArray(hex=block["link"]).bytes)

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
