import os, hashlib, base64, decimal, hmac
try:
    import nanopy.ed25519_blake2b as ed25519_blake2b
except ModuleNotFoundError:
    import nanopy.ed25519_blake2b_py as ed25519_blake2b

account_prefix = 'nano_'
work_difficulty = 'ffffffc000000000'

decimal.getcontext().traps[decimal.Inexact] = 1
decimal.getcontext().prec = 40
D = decimal.Decimal

RFC_3548 = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
ENCODING = b'13456789abcdefghijkmnopqrstuwxyz'


def account_key(account):
    if account_prefix in ['nano_', 'xrb_']:  # stupid inconsistent main network.
        assert (len(account) == 64 and
                account[:4] == 'xrb_') or (len(account) == 65 and
                                           (account[:5] == 'nano_'))
    else:
        assert len(account) == len(account_prefix) + 60 and account[:len(
            account_prefix)] == account_prefix

    account = b'1111' + account[-60:].encode()
    account = account.translate(bytes.maketrans(ENCODING, RFC_3548))
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
    account = account.translate(bytes.maketrans(RFC_3548, ENCODING))[4:]

    return account_prefix + account.decode()


def validate_account_number(account):
    try:
        account_key(account)
        return True
    except AssertionError:
        return False


def key_expand(key):
    sk = bytes.fromhex(key)
    pk = ed25519_blake2b.publickey(sk).hex()
    return key, pk, account_get(pk)


def deterministic_key(seed, index=0):
    return key_expand(
        hashlib.blake2b(
            bytes.fromhex(seed) + index.to_bytes(4, byteorder='big'),
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


def work_validate(work, _hash, difficulty=None):
    work = bytearray.fromhex(work)
    _hash = bytearray.fromhex(_hash)
    difficulty = difficulty if difficulty else work_difficulty
    difficulty = bytearray.fromhex(difficulty)

    work.reverse()
    b2b_h = bytearray(hashlib.blake2b(work + _hash, digest_size=8).digest())
    b2b_h.reverse()
    if b2b_h >= difficulty: return True
    return False


try:
    import nanopy.work

    def work_generate(_hash, difficulty=None):
        difficulty = difficulty if difficulty else work_difficulty
        work = format(
            nanopy.work.generate(bytes.fromhex(_hash), int(difficulty, 16)),
            '016x')
        assert work_validate(work, _hash, difficulty)
        return work
except ModuleNotFoundError:
    print('\033[93m' + 'No work extension' + '\033[0m')
    import random

    def work_generate(_hash, difficulty=None):
        _hash = bytearray.fromhex(_hash)
        b2b_h = bytearray.fromhex('0' * 16)
        difficulty = difficulty if difficulty else work_difficulty
        difficulty = bytearray.fromhex(difficulty)
        while b2b_h < difficulty:
            work = bytearray((random.getrandbits(8) for i in range(8)))
            for r in range(0, 256):
                work[7] = (work[7] + r) % 256
                b2b_h = bytearray(
                    hashlib.blake2b(work + _hash, digest_size=8).digest())
                b2b_h.reverse()
                if b2b_h >= difficulty: break
        work.reverse()
        return work.hex()


def mrai_from_raw(amount):
    assert type(amount) is str
    mrai = D(amount) * D(D(10)**-30)
    return format(mrai.quantize(D(D(10)**-30)), '.30f')


def mrai_to_raw(amount):
    assert type(amount) is str
    raw = D(amount) * D(D(10)**30)
    return str(raw.quantize(D(1)))


def krai_from_raw(amount):
    assert type(amount) is str
    krai = D(amount) * D(D(10)**-27)
    return format(krai.quantize(D(D(10)**-27)), '.27f')


def krai_to_raw(amount):
    assert type(amount) is str
    raw = D(amount) * D(D(10)**27)
    return str(raw.quantize(D(1)))


def rai_from_raw(amount):
    assert type(amount) is str
    rai = D(amount) * D(D(10)**-24)
    return format(rai.quantize(D(D(10)**-24)), '.24f')


def rai_to_raw(amount):
    assert type(amount) is str
    raw = D(amount) * D(D(10)**24)
    return str(raw.quantize(D(1)))


def base_block():
    return dict([('type', 'state'), ('account', ''), ('previous', '0' * 64),
                 ('balance', ''), ('representative', ''), ('link', '0' * 64),
                 ('work', ''), ('signature', '')])


def block_hash(block):
    return hashlib.blake2b(
        bytes.fromhex('0' * 63 + '6' + account_key(block['account']) +
                      block['previous'] + account_key(block['representative']) +
                      format(int(block['balance']), '032x') + block['link']),
        digest_size=32).hexdigest()


def sign_block(sk, pk, block):
    return ed25519_blake2b.signature(
        bytes.fromhex(block_hash(block)), os.urandom(32), bytes.fromhex(sk),
        bytes.fromhex(pk)).hex()
