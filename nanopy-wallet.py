import sys, argparse, getpass, gnupg, os, random, json, configparser
from nanopy import *

class bcolors:
	ok1 = '\033[95m'
	ok2 = '\033[94m'
	ok3 = '\033[92m'
	warn1 = '\033[93m'
	warn2 = '\033[91m'
	end = '\033[0m'
	bold = '\033[1m'
	underline = '\033[4m'

def get_no_value_options(section):
	options=config.options(section)
	try: options.remove('tor')
	except ValueError: pass
	try: options.remove('rpc')
	except ValueError: pass
	try: options.remove('offline')
	except ValueError: pass
	try: options.remove('account')
	except ValueError: pass
	try: options.remove('frontier')
	except ValueError: pass
	try: options.remove('balance')
	except ValueError: pass
	try: options.remove('representative')
	except ValueError: pass
	return options

def generate_block(seed):
	nb=nano_block()
	nb['account']=seed_nano(seed, args.index)
	print("Acc:\t", nb['account'])

	info={'error': 'Account not found'}
	rb={}
	for state in states:
		if config[state]['account']==nb['account']:
			state_found=True
			break

	while True:
		if online:
			info=rpc.account_info(nb['account'])
			rb=rpc.accounts_pending([nb['account']])['blocks']['xrb'+nb['account'][-61:]] # just change already!!!! !@$@#%!$#^#!^
		elif state_found:
			info['frontier']=config[state]['frontier']
			info['balance']=config[state]['balance']
			info['representative']=config[state]['representative']
			rb=get_no_value_options(state)
		try:
			nb['previous']=info['frontier']
			nb['balance']=info['balance']
			nb['representative']=info['representative']
			print("\nBal:\t", bcolors.ok1, int(nb["balance"])/10**30, bcolors.end, "NANO\t", nb["balance"], "RAW")
			print("Rep:\t", nb["representative"])

			if online:
				try: # nag users to change representative
					if int(rpc.account_info(nb['representative'])['weight'])*100/133248289196499221154116917710445381553>1.0 and (not args.change_rep_to):
						print(bcolors.warn1, "\nYour representative has too much voting weight.", bcolors.end)
						if ((input("Change rep?("+bcolors.bold+"y"+bcolors.end+"/n): ") or 'y')=='y'): args.change_rep_to=input("Rep: \t ")
				except KeyError: pass

			if args.change_rep_to: nb['representative']=args.change_rep_to

			if (not args.send_to) and (not args.change_rep_to):
				if state_found and online:
					config[state]['frontier']=info['frontier']
					config[state]['balance']=info['balance']
					config[state]['representative']=info['representative']
					with open(os.path.expanduser('~')+"/.config/nanopy-wallet.conf", 'w') as f: config.write(f)
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
			nb['link'] = nano_account(args.send_to)
			print("\nTo :\t", account_nano(nb['link']))
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
			if online: nb['balance']=str(int(nb['balance'])+int(rpc.blocks_info(rb)['blocks'][nb['link']]['amount']))
			else: nb['balance']=str(int(nb['balance'])+int(config[state][rb[0]]))
			print("\nBal:\t", bcolors.ok3, int(nb["balance"])/10**30, bcolors.end, "NANO\t", nb["balance"], "RAW")

		if(args.send_to or args.change_rep_to or rb):
			args.send_to=None
			args.change_rep_to=None

			work_hash=nb['previous']
			if(nb['previous']=="0000000000000000000000000000000000000000000000000000000000000000"): work_hash=nano_account(nb['account'])

			if(args.remote):
				try: nb['work']=rpc.work_generate(work_hash)['work']
				except KeyError:
					print(bcolors.warn1, "Node rejected work request, switching to local PoW.", bcolors.end)
					args.remote=False

			while True:
				if not args.remote: nb['work']=pow_generate(work_hash)
				if pow_validate(nb['work'], work_hash): break

			nb['signature'] = sign_block(seed, args.index, nb)

			print("\n"+json.dumps(nb))

			if online: query="\nBroadcast block?(y/"+bcolors.bold+"n"+bcolors.end+"): "
			else: query="\nUpdate state?(y/"+bcolors.bold+"n"+bcolors.end+"): "
			if ((input(query) or 'n')=='y'):
				if args.demo: print(bcolors.warn1, 'demo mode', bcolors.end)
				else:
					if online:
						ack=rpc.process(json.dumps(nb))
						try: print(bcolors.ok3, ack['hash'], bcolors.end)
						except KeyError: print(bcolors.warn2, ack, bcolors.end)
					if state_found:
						config[state]['frontier']=block_hash(nb).hex()
						config[state]['balance']=nb['balance']
						config[state]['representative']=nb['representative']
						if rb:
							try: config.remove_option(state, rb[0])
							except: pass
						with open(os.path.expanduser('~')+"/.config/nanopy-wallet.conf", 'w') as f: config.write(f)
						print(bcolors.ok3, 'saved new state to '+os.path.expanduser('~')+"/.config/nanopy-wallet.conf", bcolors.end)

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers()
parser_open = subparsers.add_parser('open', help='Unlock GPG encrypted wallet')
parser_open.add_argument('f', metavar='FILENAME', type=argparse.FileType('rb'), help='Decrypt seed from FILENAME.')
parser_open.add_argument('-i', '--index', default=0, type=int, help='Index of the account unlocked from the seed. (Default=0)')
parser_open.add_argument('-c', '--change-rep-to', metavar='ADDRESS', help='Change representative to ADDRESS.')
parser_open.add_argument('--demo', action='store_true', help='Run in demo mode. Never broadcast blocks.')

open_group = parser_open.add_mutually_exclusive_group()
open_group.add_argument('-s', '--send-to', metavar='ADDRESS', help='Send NANO to ADDRESS.')
open_group.add_argument('--empty-to', metavar='ADDRESS', help='Send all the funds to ADDRESS.')
open_group.add_argument('--audit', action='store_true', help='Check state of all accounts from index 0 to INDEX.')

offline_group = parser_open.add_mutually_exclusive_group()
offline_group.add_argument('--offline', action='store_true', help='Run in offline mode.')
offline_group.add_argument('--remote', action='store_true', help='Compute work on the node.')

parser.add_argument('--new', action='store_true', help='Generate a new account and output the GPG encrypted seed.')
parser.add_argument('--audit-file', metavar='FILENAME', type=argparse.FileType('rb'), help='Check state of all the accounts in FILENAME.')
parser.add_argument('--broadcast', action='store_true', help='Broadcast a block in JSON format.')
parser.add_argument('-t', '--tor', action='store_true', help='Connect to the RPC node via tor.')

args = parser.parse_args()
config = configparser.ConfigParser(allow_no_value=True)
config.read(os.path.expanduser('~')+"/.config/nanopy-wallet.conf")

states=config.sections()
try: states.remove('Accounts')
except ValueError: pass

online = not config['DEFAULT'].getboolean('offline')
if online:
	try: online= not args.offline
	except AttributeError: online=True

if online:
	import nanopy.rpc as rpc
	rpc.url=config['DEFAULT'].get('rpc', fallback='https://getcanoe.io/rpc')
	if args.tor or config['DEFAULT'].getboolean('tor', fallback=args.tor):
		rpc.session.proxies['http'] = 'socks5h://localhost:9050'
		rpc.session.proxies['https'] = 'socks5h://localhost:9050'
else: print(bcolors.warn1, "Running in offline mode.", bcolors.end)

try:
	unlock=(args.f!=None)
	if args.demo: print(bcolors.warn1, "Running in demo mode.", bcolors.end)
	if args.empty_to: args.send_to=args.empty_to
except: unlock=False

gpg = gnupg.GPG()

accounts=[]

if args.new:

	accounts.append('')

	pwd = getpass.getpass()

	if pwd == getpass.getpass(prompt="Enter password again: "):

		seed=os.urandom(32).hex()

		with open(seed_nano(seed, 0)+".asc", "w") as f:
			asc = gpg.encrypt(seed, symmetric='AES256', passphrase=pwd, recipients=None, extra_args=['--s2k-digest-algo', 'SHA512'])
			print(f.name[:-4])
			print(str(asc))
			f.write(str(asc))
	else: print(bcolors.warn2, "Passwords do not match.", bcolors.end)

elif args.audit_file: accounts = [line.rstrip(b'\n').decode() for line in args.audit_file]

elif unlock:

	seed=gpg.decrypt_file(args.f, passphrase=getpass.getpass())

	if seed.ok:

		if args.audit:
			for i in range(args.index+1): accounts.append(seed_nano(str(seed)[:64], i))

		else:
			generate_block(str(seed))
			sys.exit()

	else:
		print(bcolors.warn2, seed.status, bcolors.end)
		sys.exit()

elif args.broadcast and online:
	ack=rpc.process(json.dumps(json.loads(input("Enter JSON block to broadcast: "))))
	try: print(bcolors.ok3, ack['hash'], bcolors.end)
	except KeyError: print(bcolors.warn2, ack, bcolors.end)
	sys.exit()

else: accounts=get_no_value_options('Accounts')

if accounts[0] and online:
	info=rpc.accounts_balances(accounts)
	for account in accounts:
		print("\nAcc:\t", account)
		try:
			print("Bal:\t", bcolors.ok1, int(info[account]["balance"])/10**30, bcolors.end, "NANO\t", info[account]["balance"], "RAW")
			if int(info[account]["pending"]): print(bcolors.ok3, "Pending block(s)", bcolors.end)
		except KeyError: print(bcolors.warn2, info[account], bcolors.end)
