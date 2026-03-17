import nanopy, sys, argparse, getpass, gnupg, os, ed25519_blake2b, json

def generate_block(seed):
	sk, pk = nanopy.seed_account(seed, args.index) # secret/private key, public key

	nb={}
	nb['type']="state"
	nb['account']=nanopy.account_nano(pk.hex())
	print("Acc:\t", nb['account'])

	info=nanopy.account_info(nb['account'])
	rb=nanopy.accounts_pending([nb['account']])['blocks'][nb['account']]
	while True:
		try:
			nb['previous']=info['frontier']
			nb['balance']=info['balance']
			nb['representative']=info['representative']
			print("Bal:\t", int(nb["balance"])/10**30, "NANO\t", nb["balance"], "RAW")
			print("Rep:\t", nb["representative"])
			
			try: # nag users to change representative
				if int(nanopy.account_info(nb['representative'])['weight'])*100/133248289196499221154116917710445381553>1.0:
					print("\n\nYour representative has too much voting weight.")
					if (input("Change rep?(y/n): ")=='y'):
						args.change_rep_to=input("Rep: \t ")
			except KeyError:
				pass

			if args.change_rep_to:
				nb['representative']=args.change_rep_to
				nb['link'] = "0000000000000000000000000000000000000000000000000000000000000000"

		except KeyError:
			if rb=='':
				print(info)
				nb['balance']='0'
				break
			else:
				args.send_to=None
				args.change_rep_to=None
				nb['previous']="0000000000000000000000000000000000000000000000000000000000000000"
				nb['balance']='0'
				print("Bal:\t", int(nb["balance"])/10**30, "NANO\t", nb["balance"], "RAW")
				nb['representative']=input("Rep:\t ")

		if args.send_to:
			nb['link'] = nanopy.nano_account(args.send_to)
			if args.empty_to:
				nb['balance']='0'
			else:
				amount=format(float(input("Amt:\t "))*10**6, '.0f')+"000000000000000000000000"
				nb['balance']=str(int(nb['balance'])-int(amount))

		elif rb!='':
			nb['link']=rb[0]
			nb['balance']=str(int(nb['balance'])+int(nanopy.blocks_info(rb)['blocks'][nb['link']]['amount']))

		if(args.send_to or args.change_rep_to or rb!=''):
			work_hash=nb['previous']
			if(nb['previous']=="0000000000000000000000000000000000000000000000000000000000000000"):
				work_hash=nanopy.nano_account(nb['account'])

			if(args.remote):
				try:
					nb['work']=nanopy.work_generate(work_hash)['work']
				except KeyError:
					print("Node rejected work request, switching to local PoW.")
					args.remote=False

			if not args.remote:
				nb['work']=nanopy.pow_generate(work_hash)

			bh=nanopy.block_hash(nb)
			nb['signature'] = ed25519_blake2b.signature(bh,sk,pk).hex()

			if args.send_to:
				print("\n\nTo :\t", nanopy.account_nano(nb['link']))
				if not args.empty_to:
					print("Amt:\t", int(amount)/10**30, "NANO\t", amount, "RAW")
				else:
					print("Amt:\t", int(info["balance"])/10**30, "NANO\t", info["balance"], "RAW")

			print("\n\nBal:\t", int(nb["balance"])/10**30, "NANO\t", nb["balance"], "RAW\n")
			print(json.dumps(nb))

			if (input("\n\nBroadcast block?(y/n): ")=='y'):
				print(nanopy.process(json.dumps(nb)))
				info=nanopy.account_info(nb['account'])
				rb=nanopy.accounts_pending([nb['account']])['blocks'][nb['account']]
				nb['previous']=info['frontier']

			nb['balance']=info['balance']
			nb['representative']=info['representative']
			print("Bal:\t", int(nb["balance"])/10**30, "NANO\t", nb["balance"], "RAW")

		if rb!='':
			if (input("\n\nReceive pending blocks?(y/n): ")=='y'):
				continue
		break

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--index', default=0, type=int, help='Index of the account generated from the seed. (Default=0)')
	parser.add_argument('--new', action='store_true', help='Generate a new account and output the GPG encrypted seed.')

	send_group = parser.add_mutually_exclusive_group()
	send_group.add_argument('--send-to', metavar='XRB_ADDRESS', help='Send NANO to XRB_ADDRESS.')
	send_group.add_argument('--empty-to', metavar='XRB_ADDRESS', help='Send all the funds to XRB_ADDRESS.')

	parser.add_argument('--change-rep-to', metavar='XRB_ADDRESS', help='Change representative to XRB_ADDRESS.')

	parser.add_argument('--remote', action='store_true', help='Compute work on the node.')
	parser.add_argument('-t', '--tor', action='store_true', help='Connect to the RPC node via tor.')

	audit_group = parser.add_mutually_exclusive_group()
	audit_group.add_argument('--audit-seed', default=None, metavar='MAX_INDEX', type=int, help='Check state of all the accounts from index 0 to MAX_INDEX.')
	audit_group.add_argument('--audit-file', default=None, metavar='FILENAME', type=str, help='Check state of all the accounts in the file FILENAME.')

	args = parser.parse_args()
	
	if args.empty_to:
		args.send_to=args.empty_to

	if args.tor:
		nanopy.rpc.proxies['http'] = 'socks5h://localhost:9050'
		nanopy.rpc.proxies['https'] = 'socks5h://localhost:9050'
		print(nanopy.rpc.get('https://httpbin.org/ip').text)

	nanopy.url='https://getcanoe.io/rpc'
	# ~ nanopy.url='https://nanovault.io/api/node-api'
	
	gpg = gnupg.GPG()

	if args.new:

		pwd = getpass.getpass()

		if pwd == getpass.getpass(prompt="Enter password again: "):

			seed=os.urandom(32).hex()
			sk, pk = nanopy.seed_account(seed, 0)

			print("Index 0 account:\t", nanopy.account_nano(pk.hex()))

			with open(nanopy.account_nano(pk.hex())+".asc", "w") as f:
				asc = gpg.encrypt(seed, symmetric='AES256', passphrase=pwd, recipients=None, extra_args=['--s2k-digest-algo', 'SHA512'])
				print(str(asc))
				f.write(str(asc))
		else:
			print("Passwords do not match.")

	elif args.audit_file:
		with open(args.audit_file, "rb") as f:
			accounts = [line.rstrip(b'\n').decode() for line in f]

	else:

		with open(input("GPG encrypted file name: "), "rb") as f:
			seed=gpg.decrypt_file(f, passphrase=getpass.getpass())

		if seed.ok:

			if args.audit_seed:
				accounts=[]
				for i in range(args.audit_seed+1):
					sk, pk = nanopy.seed_account(str(seed), i)
					accounts.append(nanopy.account_nano(pk.hex()))

			else:
				generate_block(str(seed))

		else:
			print(seed.status)
			sys.exit()

	if args.audit_file or args.audit_seed:
		info=nanopy.accounts_balances(accounts)
		for account in accounts:
			print("\nAcc:\t", account)
			try:
				print("Bal:\t", int(info[account]["balance"])/10**30, "NANO\t", info[account]["balance"], "RAW")
				if int(info[account]["pending"]):
					print("Pending block(s)")
			except KeyError:
				print(info[account])

