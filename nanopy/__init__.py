import os, hashlib, base64, decimal, hmac
try:
    import nanopy.ed25519_blake2b as ed25519_blake2b
    ed25519_blake2b_c = True
except ModuleNotFoundError:
    import nanopy.ed25519_blake2b_py as ed25519_blake2b
    ed25519_blake2b_c = False

account_prefix = 'nano_'
work_difficulty = 'ffffffc000000000'
standard_exponent = 30

decimal.getcontext().traps[decimal.Inexact] = 1
decimal.getcontext().prec = 40
_D = decimal.Decimal

_B32 = b'13456789abcdefghijkmnopqrstuwxyz'


def state_block():
    return dict([('type', 'state'), ('account', ''), ('previous', '0' * 64),
                 ('representative', ''), ('balance', ''), ('link', '0' * 64),
                 ('work', ''), ('signature', '')])


def account_key(account):
    assert len(account) == len(
        account_prefix) + 60 and account[:len(account_prefix)] == account_prefix

    account = b'1111' + account[-60:].encode()
    account = account.translate(bytes.maketrans(_B32, base64._b32alphabet))
    key = base64.b32decode(account)

    checksum = key[:-6:-1]
    key = key[3:-5]

    assert hashlib.blake2b(key, digest_size=5).digest() == checksum

    return key.hex()


def account_get(key):
    assert len(key) == 64

    key = bytes.fromhex(key)
    checksum = hashlib.blake2b(key, digest_size=5).digest()
    key = b'\x00\x00\x00' + key + checksum[::-1]
    account = base64.b32encode(key)
    account = account.translate(bytes.maketrans(base64._b32alphabet, _B32))[4:]

    return account_prefix + account.decode()


def validate_account_number(account):
    try:
        account_key(account)
        return True
    except:
        return False


def key_expand(key):
    pk = ed25519_blake2b.publickey(bytes.fromhex(key)).hex()
    return key, pk, account_get(pk)


def deterministic_key(seed, index=0):
    return key_expand(
        hashlib.blake2b(bytes.fromhex(seed) +
                        index.to_bytes(4, byteorder='big'),
                        digest_size=32).hexdigest())


try:
    import mnemonic

    def generate_mnemonic(strength=256, language='english'):
        m = mnemonic.Mnemonic(language)
        return m.generate(strength=strength)

    def mnemonic_key(words, index=0, passphrase='', language='english'):
        m = mnemonic.Mnemonic(language)
        assert (m.check(words))
        for i in ['m', 44, 165, index]:
            if i == 'm':
                key = b'ed25519 seed'
                msg = m.to_seed(words, passphrase)
            else:
                i = i | 0x80000000
                msg = b'\x00' + sk + i.to_bytes(4, byteorder='big')
            h = hmac.new(key, msg, hashlib.sha512).digest()
            sk, key = h[:32], h[32:]
        return key_expand(sk.hex())
except ModuleNotFoundError:
    pass


def work_validate(work, _hash, difficulty=None, multiplier=0):
    work = bytearray.fromhex(work)
    _hash = bytes.fromhex(_hash)
    if multiplier:
        difficulty = format(
            int((int(work_difficulty, 16) - (1 << 64)) / multiplier +
                (1 << 64)), '016x')
    else:
        difficulty = difficulty if difficulty else work_difficulty
    difficulty = bytes.fromhex(difficulty)

    work.reverse()
    b2b_h = bytearray(hashlib.blake2b(work + _hash, digest_size=8).digest())
    b2b_h.reverse()
    if b2b_h >= difficulty:
        return True
    return False


try:
    import nanopy.work

    def work_generate(_hash, difficulty=None, multiplier=0):
        if multiplier:
            difficulty = format(
                int((int(work_difficulty, 16) - (1 << 64)) / multiplier +
                    (1 << 64)), '016x')
        else:
            difficulty = difficulty if difficulty else work_difficulty
        work = format(
            nanopy.work.generate(bytes.fromhex(_hash), int(difficulty, 16)),
            '016x')
        assert work_validate(work, _hash, difficulty)
        return work
except ModuleNotFoundError:
    print('\033[93m' + 'No work extension' + '\033[0m')
    import random

    def work_generate(_hash, difficulty=None, multiplier=0):
        _hash = bytes.fromhex(_hash)
        b2b_h = bytearray.fromhex('0' * 16)
        if multiplier:
            difficulty = format(
                int((int(work_difficulty, 16) - (1 << 64)) / multiplier +
                    (1 << 64)), '016x')
        else:
            difficulty = difficulty if difficulty else work_difficulty
        difficulty = bytes.fromhex(difficulty)
        while b2b_h < difficulty:
            work = bytearray((random.getrandbits(8) for i in range(8)))
            for r in range(0, 256):
                work[7] = (work[7] + r) % 256
                b2b_h = bytearray(
                    hashlib.blake2b(work + _hash, digest_size=8).digest())
                b2b_h.reverse()
                if b2b_h >= difficulty:
                    break
        work.reverse()
        return work.hex()


def from_raw(amount, exp=0):
    assert type(amount) is str
    exp = exp if exp else standard_exponent
    mrai = _D(amount) * _D(_D(10)**-exp)
    return format(mrai.quantize(_D(_D(10)**-exp)), '.' + str(exp) + 'f')


def to_raw(amount, exp=0):
    assert type(amount) is str
    exp = exp if exp else standard_exponent
    raw = _D(amount) * _D(_D(10)**exp)
    return str(raw.quantize(_D(1)))


def mrai_from_raw(amount):
    return from_raw(amount, exp=30)


def mrai_to_raw(amount):
    return to_raw(amount, exp=30)


def krai_from_raw(amount):
    return from_raw(amount, exp=27)


def krai_to_raw(amount):
    return to_raw(amount, exp=27)


def rai_from_raw(amount):
    return from_raw(amount, exp=24)


def rai_to_raw(amount):
    return to_raw(amount, exp=24)


def block_hash(block):
    return hashlib.blake2b(
        bytes.fromhex('0' * 63 + '6' + account_key(block['account']) +
                      block['previous'] + account_key(block['representative']) +
                      format(int(block['balance']), '032x') + block['link']),
        digest_size=32).hexdigest()


def sign(key, block=None, _hash=None, msg=None, account=None, pk=None):
    sk = bytes.fromhex(key)

    if msg:
        m = msg.encode()
    elif _hash:
        m = bytes.fromhex(_hash)
    elif block:
        m = bytes.fromhex(block_hash(block))
    else:
        return None

    if not pk:
        if account:
            pk = bytes.fromhex(account_key(account))
        elif block:
            pk = bytes.fromhex(account_key(block['account']))
        else:
            pk = ed25519_blake2b.publickey(sk)
    else:
        pk = bytes.fromhex(pk)

    if ed25519_blake2b_c:
        return ed25519_blake2b.signature(m, os.urandom(32), sk, pk).hex()
    else:
        return ed25519_blake2b.signature(m, sk, pk).hex()


def block_create(key, previous, representative, balance, link):
    nb = state_block()
    nb['account'] = account_get(
        ed25519_blake2b.publickey(bytes.fromhex(key)).hex())
    nb['previous'] = previous
    nb['representative'] = representative
    nb['balance'] = balance
    nb['link'] = link
    nb['work'] = work_generate(block_hash(nb))
    nb['signature'] = sign(key, block=nb)
    return nb
