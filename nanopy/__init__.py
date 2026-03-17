import hashlib, base64, decimal, hmac, mnemonic, nanopy.ed25519_blake2b

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
    h = hashlib.blake2b(digest_size=5)
    h.update(key)

    assert h.digest() == checksum

    return key.hex()


def account_get(key):
    assert len(key) == 64

    key = bytes.fromhex(key)
    h = hashlib.blake2b(digest_size=5)
    h.update(key)
    checksum = h.digest()
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
    pk = nanopy.ed25519_blake2b.publickey(sk).hex()
    return key, pk, account_get(pk)


def deterministic_key(seed, index=0):
    h = hashlib.blake2b(digest_size=32)

    h.update(bytes.fromhex(seed))
    h.update(index.to_bytes(4, byteorder='big'))

    sk = h.digest()
    return key_expand(sk.hex())


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


def work_validate(work, _hash, difficulty=None):
    workb = bytearray.fromhex(work)
    hashb = bytearray.fromhex(_hash)
    difficulty = difficulty if difficulty else work_difficulty
    difficultyb = bytearray.fromhex(difficulty)

    workb.reverse()

    h = hashlib.blake2b(digest_size=8)
    h.update(workb)
    h.update(hashb)

    final = bytearray(h.digest())
    final.reverse()

    if final > difficultyb: return True
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
        hashb = bytearray.fromhex(_hash)
        b2bb = bytearray.fromhex('0000000000000000')
        difficulty = difficulty if difficulty else work_difficulty
        difficultyb = bytearray.fromhex(difficulty)
        while b2bb < difficultyb:
            workb = bytearray((random.getrandbits(8) for i in range(8)))
            for r in range(0, 256):
                workb[7] = (workb[7] + r) % 256
                h = hashlib.blake2b(digest_size=8)
                h.update(workb)
                h.update(hashb)
                b2bb = bytearray(h.digest())
                b2bb.reverse()
                if b2bb >= difficultyb: break

        workb.reverse()
        assert work_validate(workb.hex(), _hash, difficulty)
        return workb.hex()


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
    return dict(
        [('type', 'state'), ('account', ''),
         ('previous',
          '0000000000000000000000000000000000000000000000000000000000000000'),
         ('balance', ''), ('representative', ''),
         ('link',
          '0000000000000000000000000000000000000000000000000000000000000000'),
         ('work', ''), ('signature', '')])


def block_hash(block):
    bh = hashlib.blake2b(digest_size=32)

    bh.update(
        bytes.fromhex(
            '0000000000000000000000000000000000000000000000000000000000000006'))
    bh.update(bytes.fromhex(account_key(block['account'])))
    bh.update(bytes.fromhex(block['previous']))
    bh.update(bytes.fromhex(account_key(block['representative'])))
    bh.update(bytes.fromhex(format(int(block['balance']), '032x')))
    bh.update(bytes.fromhex(block['link']))

    return bh.hexdigest()


def sign_block(sk, pk, block):
    return nanopy.ed25519_blake2b.signature(
        bytes.fromhex(block_hash(block)), bytes.fromhex(sk),
        bytes.fromhex(pk)).hex()
