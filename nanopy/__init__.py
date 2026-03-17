import sys, os, random, hashlib, nanopy.ed25519_blake2b, nanopy.work

def nano_block(): return dict([('type', 'state'), ('account', ''), ('previous', '0000000000000000000000000000000000000000000000000000000000000000'), ('balance', ''), ('representative', ''), ('link', '0000000000000000000000000000000000000000000000000000000000000000'), ('work', ''), ('signature', '')])

def nano_account(address):
	if (len(address) == 64 and (address[:4] == 'xrb_')) or (len(address) == 65 and (address[:5] == 'nano_')):
		account_map = "13456789abcdefghijkmnopqrstuwxyz"
		account_lookup = {}
		for x in range(32): account_lookup[account_map[x]] = format(x,'05b')

		acrop_key = address[-60:-8]
		acrop_check = address[-8:]

		number_l = ''.join(account_lookup[acrop_key[x]] for x in range (52))
		number_l=int(number_l[4:], 2).to_bytes(32, byteorder='big')

		check_l = ''.join(account_lookup[acrop_check[x]] for x in range(8))
		check_l=bytearray(int(check_l, 2).to_bytes(5, byteorder='big'))
		check_l.reverse()

		h = hashlib.blake2b(digest_size=5)
		h.update(number_l)
		if (h.digest() == check_l):return number_l.hex()
	return False

def account_nano(account):
	account_map = "13456789abcdefghijkmnopqrstuwxyz"
	account_lookup = {}
	for x in range(32): account_lookup[format(x,'05b')] = account_map[x]

	h = hashlib.blake2b(digest_size=5)
	h.update(bytes.fromhex(account))
	checksum = bytearray(h.digest())

	checksum.reverse()
	checksum=format(int.from_bytes(checksum, byteorder='big'),'040b')

	encode_check = ''.join(account_lookup[checksum[x*5:x*5+5]] for x in range(8))

	account = format(int(account, 16),'0260b')

	encode_account = ''.join(account_lookup[account[x*5:x*5+5]] for x in range(52))

	return 'nano_'+encode_account+encode_check

def seed_keys(seed, index):
	h = hashlib.blake2b(digest_size=32)

	h.update(bytes.fromhex(seed))
	h.update(index.to_bytes(4, byteorder='big'))

	account_key = h.digest()
	return account_key, nanopy.ed25519_blake2b.publickey(account_key)

def seed_nano(seed, index):
	_, pk = seed_keys(seed, index)
	return account_nano(pk.hex())

def pow_threshold(check):
	if check > b'\xFF\xFF\xFF\xC0\x00\x00\x00\x00': return True
	return False

def pow_validate(pow, hash):
	pow_data = bytearray.fromhex(pow)
	hash_data = bytearray.fromhex(hash)

	pow_data.reverse()

	h = hashlib.blake2b(digest_size=8)
	h.update(pow_data)
	h.update(hash_data)

	final = bytearray(h.digest())
	final.reverse()

	return pow_threshold(final)

def pow_generate(hash):
	pow=format(nanopy.work.generate(bytes.fromhex(hash)),'016x')
	if(pow_validate(pow, hash)): return pow
	return False

def block_hash(block):
	bh = hashlib.blake2b(digest_size=32)

	bh.update(bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000006"))
	bh.update(bytes.fromhex(nano_account(block["account"])))
	bh.update(bytes.fromhex(block["previous"]))
	bh.update(bytes.fromhex(nano_account(block["representative"])))
	bh.update(bytes.fromhex(format(int(block["balance"]),'032x')))
	bh.update(bytes.fromhex(block["link"]))

	return bh.digest()

def sign_block(seed, index, block):	return nanopy.ed25519_blake2b.signature(block_hash(block),*seed_keys(seed, index)).hex()
