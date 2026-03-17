import nanopy, sys, argparse, getpass, gnupg, os, random, json

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
	nb=nanopy.nano_block()
	nb['account']=nanopy.seed_nano(seed, args.index)
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
					if ((input("Change rep?("+bcolors.bold+"y"+bcolors.end+"/n): ") or 'y')=='y'): args.change_rep_to=input("Rep: \t ")
			except KeyError: pass

			if args.change_rep_to: nb['representative']=args.change_rep_to

			if (not args.send_to) and (not args.change_rep_to):
				if not rb: break
				if ((input("\nReceive pending blocks?("+bcolors.bold+"y"+bcolors.end+"/n): ") or 'y')!='y'): break

		except KeyError:
			if not rb:
				print(bcolors.warn2, info, bcolors.end)
				break
			else:
				args.send_to=None
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
			if(nb['previous']=="0000000000000000000000000000000000000000000000000000000000000000"): work_hash=nanopy.nano_account(nb['account'])

			if(args.remote):
				try: nb['work']=nanopy.work_generate(work_hash)['work']
				except KeyError:
					print(bcolors.warn1, "Node rejected work request, switching to local PoW.", bcolors.end)
					args.remote=False

			while True:
				if not args.remote: nb['work']=nanopy.pow_generate(work_hash)
				if nanopy.pow_validate(nb['work'], work_hash): break

			nb['signature'] = nanopy.sign_block(seed, args.index, nb)

			print("\n"+json.dumps(nb))

			if ((input("\nBroadcast block?(y/"+bcolors.bold+"n"+bcolors.end+"): ") or 'n')=='y'):
				ack={'demo':'broadcasting is blocked.'}
				if not args.demo: ack=nanopy.process(json.dumps(nb))

				try: print(bcolors.ok3, ack['hash'], bcolors.end)
				except KeyError: print(bcolors.warn2, ack, bcolors.end)

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--index', default=0, type=int, help='Index of the account generated from the seed. (Default=0)')
	parser.add_argument('--new', action='store_true', help='Generate a new account and output the GPG encrypted seed.')

	parser.add_argument('--unlock', action='store_true', help='Unlock wallet.')
	parser.add_argument('--change-rep-to', metavar='ADDRESS', help='Change representative to ADDRESS.')

	send_group = parser.add_mutually_exclusive_group()
	send_group.add_argument('--send-to', metavar='ADDRESS', help='Send NANO to ADDRESS.')
	send_group.add_argument('--empty-to', metavar='ADDRESS', help='Send all the funds to ADDRESS.')

	parser.add_argument('--remote', action='store_true', help='Compute work on the node.')
	parser.add_argument('-t', '--tor', action='store_true', help='Connect to the RPC node via tor.')

	audit_group = parser.add_mutually_exclusive_group()
	audit_group.add_argument('--audit-seed', default=None, metavar='MAX_INDEX', type=int, help='Check state of all the accounts from index 0 to MAX_INDEX.')
	audit_group.add_argument('--audit-file', default=None, metavar='FILENAME', type=str, help='Check state of all the accounts in the file FILENAME.')

	parser.add_argument('--demo', action='store_true', help='Run in demo mode. Never broadcast blocks.')

	args = parser.parse_args()

	try:
		with open(os.path.expanduser('~')+"/.config/nanopy-wallet.conf") as conf: options=json.load(conf)
	except FileNotFoundError: options={'accounts': [''], 'tor': False, 'rpc': ['https://getcanoe.io/rpc']}

	if args.demo: print(bcolors.warn1, "Running in demo mode.", bcolors.end)

	if args.empty_to: args.send_to=args.empty_to

	if (args.audit_seed or args.send_to or args.change_rep_to) : args.unlock = True

	if args.tor or options['tor']:
		nanopy.rpc.proxies['http'] = 'socks5h://localhost:9050'
		nanopy.rpc.proxies['https'] = 'socks5h://localhost:9050'

	nanopy.url=random.choice(options['rpc'])

	gpg = gnupg.GPG()

	accounts=[]

	if args.new:

		accounts.append('')

		pwd = getpass.getpass()

		if pwd == getpass.getpass(prompt="Enter password again: "):

			seed=os.urandom(32).hex()

			with open(nanopy.seed_nano(seed, 0)+".asc", "w") as f:
				asc = gpg.encrypt(seed, symmetric='AES256', passphrase=pwd, recipients=None, extra_args=['--s2k-digest-algo', 'SHA512'])
				print(f.name[:-4])
				print(str(asc))
				f.write(str(asc))
		else: print(bcolors.warn2, "Passwords do not match.", bcolors.end)

	elif args.audit_file:
		with open(args.audit_file, "rb") as f: accounts = [line.rstrip(b'\n').decode() for line in f]

	elif args.unlock:

		with open(input("GPG encrypted file name: "), "rb") as f: seed=gpg.decrypt_file(f, passphrase=getpass.getpass())

		if seed.ok:

			if args.audit_seed:
				for i in range(args.audit_seed+1): accounts.append(nanopy.seed_nano(str(seed)[:64], i))

			else:
				generate_block(str(seed))
				sys.exit()

		else:
			print(bcolors.warn2, seed.status, bcolors.end)
			sys.exit()

	else: accounts=options['accounts']

	if accounts[0]:
		info=nanopy.accounts_balances(accounts)
		for account in accounts:
			print("\nAcc:\t", account)
			try:
				print("Bal:\t", bcolors.ok1, int(info[account]["balance"])/10**30, bcolors.end, "NANO\t", info[account]["balance"], "RAW")
				if int(info[account]["pending"]): print(bcolors.ok3, "Pending block(s)", bcolors.end)
			except KeyError: print(bcolors.warn2, info[account], bcolors.end)
