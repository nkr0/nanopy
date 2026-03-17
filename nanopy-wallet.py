import nanopy, sys, argparse, getpass, gnupg, os, random, ed25519_blake2b, json

class bcolors:
	ok1 = '\033[95m'
	ok2 = '\033[94m'
	ok3 = '\033[92m'
	warn1 = '\033[93m'
	warn2 = '\033[91m'
	end = '\033[0m'
	bold = '\033[1m'
	underline = '\033[4m'

def generate_block(seed):
	sk, pk = nanopy.seed_account(seed, args.index) # secret/private key, public key

	nb={}
	nb['type']="state"
	nb['account']=nanopy.account_nano(pk.hex())
	print("Acc:\t", nb['account'])

	while True:
		info=nanopy.account_info(nb['account'])
		rb=nanopy.accounts_pending([nb['account']])['blocks'][nb['account']]
		try:
			nb['previous']=info['frontier']
			nb['balance']=info['balance']
			nb['representative']=info['representative']
			print("\nBal:\t", bcolors.ok1, int(nb["balance"])/10**30, bcolors.end, "NANO\t", nb["balance"], "RAW")
			print("Rep:\t", nb["representative"])
			
			try: # nag users to change representative
				if int(nanopy.account_info(nb['representative'])['weight'])*100/133248289196499221154116917710445381553>1.0 and (not args.change_rep_to):
					print(bcolors.warn1, "\nYour representative has too much voting weight.", bcolors.end)
					if ((input("Change rep?("+bcolors.bold+"y"+bcolors.end+"/n): ") or 'y')=='y'):
						args.change_rep_to=input("Rep: \t ")
			except KeyError:
				pass

			if args.change_rep_to:
				nb['representative']=args.change_rep_to
				nb['link'] = "0000000000000000000000000000000000000000000000000000000000000000"

			if (not args.send_to) and (not args.change_rep_to):
				if not rb:
					break
				if ((input("\nReceive pending blocks?("+bcolors.bold+"y"+bcolors.end+"/n): ") or 'y')!='y'):
					break
			
		except KeyError:
			if not rb:
				print(bcolors.warn2, info, bcolors.end)
				break
			else:
				args.send_to=None
				nb['previous']="0000000000000000000000000000000000000000000000000000000000000000"
				nb['balance']='0'
				print("Bal:\t", bcolors.ok1, int(nb["balance"])/10**30, bcolors.end, "NANO\t", nb["balance"], "RAW")
				nb['representative']=input("Rep: \t ")

		if args.send_to:
			nb['link'] = nanopy.nano_account(args.send_to)
			print("\nTo :\t", nanopy.account_nano(nb['link']))
			if args.empty_to:
				print("Amt:\t", bcolors.warn2, int(nb["balance"])/10**30, bcolors.end, "NANO\t", nb["balance"], "RAW")
				nb['balance']='0'
			else:
				while True:
					amount=format(float(input("Amount to send: "))*10**6, '.0f')+"000000000000000000000000"
					if int(amount)<=int(nb['balance']):
						nb['balance']=str(int(nb['balance'])-int(amount))
						break
					print(bcolors.warn2, "Amount must be less than or equal to balance.", bcolors.end)
			print("\nBal:\t", bcolors.warn1, int(nb["balance"])/10**30, bcolors.end, "NANO\t", nb["balance"], "RAW")

		elif rb:
			nb['link']=rb[0]
			nb['balance']=str(int(nb['balance'])+int(nanopy.blocks_info(rb)['blocks'][nb['link']]['amount']))
			print("\nBal:\t", bcolors.ok3, int(nb["balance"])/10**30, bcolors.end, "NANO\t", nb["balance"], "RAW")

		if(args.send_to or args.change_rep_to or rb):
			args.send_to=None
			args.change_rep_to=None

			work_hash=nb['previous']
			if(nb['previous']=="0000000000000000000000000000000000000000000000000000000000000000"):
				work_hash=nanopy.nano_account(nb['account'])

			if(args.remote):
				try:
					nb['work']=nanopy.work_generate(work_hash)['work']
				except KeyError:
					print(bcolors.warn1, "Node rejected work request, switching to local PoW.", bcolors.end)
					args.remote=False

			if not args.remote:
				nb['work']=nanopy.pow_generate(work_hash)

			bh=nanopy.block_hash(nb)
			nb['signature'] = ed25519_blake2b.signature(bh,sk,pk).hex()

			print("\n"+json.dumps(nb))

			if ((input("\nBroadcast block?(y/"+bcolors.bold+"n"+bcolors.end+"): ") or 'n')=='y'):
				ack={'demo':'broadcasting is blocked.'}
				if not args.demo:
					ack=nanopy.process(json.dumps(nb))

				try:
					print(bcolors.ok3, ack['hash'], bcolors.end)
				except KeyError:
					print(bcolors.warn2, ack, bcolors.end)

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--index', default=0, type=int, help='Index of the account generated from the seed. (Default=0)')
	parser.add_argument('--new', action='store_true', help='Generate a new account and output the GPG encrypted seed.')

	send_group = parser.add_mutually_exclusive_group()
	send_group.add_argument('--send-to', metavar='XRB/NANO_ADDRESS', help='Send NANO to XRB/NANO_ADDRESS.')
	send_group.add_argument('--empty-to', metavar='XRB/NANO_ADDRESS', help='Send all the funds to XRB/NANO_ADDRESS.')

	parser.add_argument('--change-rep-to', metavar='XRB/NANO_ADDRESS', help='Change representative to XRB/NANO_ADDRESS.')

	parser.add_argument('--remote', action='store_true', help='Compute work on the node.')
	parser.add_argument('-t', '--tor', action='store_true', help='Connect to the RPC node via tor.')

	audit_group = parser.add_mutually_exclusive_group()
	audit_group.add_argument('--audit-seed', default=None, metavar='MAX_INDEX', type=int, help='Check state of all the accounts from index 0 to MAX_INDEX.')
	audit_group.add_argument('--audit-file', default=None, metavar='FILENAME', type=str, help='Check state of all the accounts in the file FILENAME.')

	parser.add_argument('--demo', action='store_true', help='Run in demo mode. Never broadcast blocks.')

	args = parser.parse_args()
	
	if args.demo:
		print(bcolors.warn1, "Running in demo mode.", bcolors.end)
	
	if args.empty_to:
		args.send_to=args.empty_to

	if args.tor:
		nanopy.rpc.proxies['http'] = 'socks5h://localhost:9050'
		nanopy.rpc.proxies['https'] = 'socks5h://localhost:9050'

	with open("api.dat", "rb") as f:
		urls = [line.rstrip(b'\n').decode() for line in f]
	nanopy.url=random.choice(urls)
	
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
			print(bcolors.warn2, "Passwords do not match.", bcolors.end)

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
			print(bcolors.warn2, seed.status, bcolors.end)
			sys.exit()

	if args.audit_file or args.audit_seed:
		info=nanopy.accounts_balances(accounts)
		for account in accounts:
			print("\nAcc:\t", account)
			try:
				print("Bal:\t", bcolors.ok1, int(info[account]["balance"])/10**30, bcolors.end, "NANO\t", info[account]["balance"], "RAW")
				if int(info[account]["pending"]):
					print(bcolors.ok3, "Pending block(s)", bcolors.end)
			except KeyError:
				print(bcolors.warn2, info[account], bcolors.end)

