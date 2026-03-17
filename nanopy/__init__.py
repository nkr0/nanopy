import hashlib, decimal, nanopy.ed25519_blake2b, nanopy.work

account_prefix = 'nano_'
mrai_name = 'NANO'

decimal.getcontext().traps[decimal.Inexact] = 1
# ~ decimal.getcontext().traps[decimal.Rounded] = 1
decimal.getcontext().prec = 40
D = decimal.Decimal


def account_key(account):
    if account_prefix in ['nano_', 'xrb_']:  # stupid inconsistent main network.
        assert (len(account) == 64 and
                account[:4] == 'xrb_') or (len(account) == 65 and
                                           (account[:5] == 'nano_'))
    else:
        assert len(account) == len(account_prefix) + 60 and account[:len(
            account_prefix)] == account_prefix

    account_map = "13456789abcdefghijkmnopqrstuwxyz"
    account_lookup = {}
    for x in range(32):
        account_lookup[account_map[x]] = format(x, '05b')

    acrop_key = account[-60:-8]
    acrop_check = account[-8:]

    number_l = ''.join(account_lookup[acrop_key[x]] for x in range(52))
    number_l = int(number_l[4:], 2).to_bytes(32, byteorder='big')

    check_l = ''.join(account_lookup[acrop_check[x]] for x in range(8))
    check_l = bytearray(int(check_l, 2).to_bytes(5, byteorder='big'))
    check_l.reverse()

    h = hashlib.blake2b(digest_size=5)
    h.update(number_l)

    assert h.digest() == check_l

    return number_l.hex()


def account_get(key):
    assert len(key) == 64
    account_map = "13456789abcdefghijkmnopqrstuwxyz"
    account_lookup = {}
    for x in range(32):
        account_lookup[format(x, '05b')] = account_map[x]

    h = hashlib.blake2b(digest_size=5)
    h.update(bytes.fromhex(key))
    checksum = bytearray(h.digest())

    checksum.reverse()
    checksum = format(int.from_bytes(checksum, byteorder='big'), '040b')

    encode_check = ''.join(
        account_lookup[checksum[x * 5:x * 5 + 5]] for x in range(8))

    keyb = format(int(key, 16), '0260b')

    encode_account = ''.join(
        account_lookup[keyb[x * 5:x * 5 + 5]] for x in range(52))

    return account_prefix + encode_account + encode_check


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


def deterministic_key(seed, index):
    h = hashlib.blake2b(digest_size=32)

    h.update(bytes.fromhex(seed))
    h.update(index.to_bytes(4, byteorder='big'))

    sk = h.digest()
    return key_expand(sk.hex())


def work_validate(work, _hash):
    workb = bytearray.fromhex(work)
    hashb = bytearray.fromhex(_hash)

    workb.reverse()

    h = hashlib.blake2b(digest_size=8)
    h.update(workb)
    h.update(hashb)

    final = bytearray(h.digest())
    final.reverse()

    if final > b'\xFF\xFF\xFF\xC0\x00\x00\x00\x00': return True
    return False


def work_generate(_hash):
    work = format(nanopy.work.generate(bytes.fromhex(_hash)), '016x')
    assert work_validate(work, _hash)
    return work


def mrai_from_raw(amount):
    assert type(amount) is str
    mrai = D(amount) * D(D(10)**-30)
    return str(mrai.quantize(D(D(10)**-30)))


def mrai_to_raw(amount):
    assert type(amount) is str
    raw = D(amount) * D(D(10)**30)
    return str(raw.quantize(D(1)))


def krai_from_raw(amount):
    assert type(amount) is str
    krai = D(amount) * D(D(10)**-27)
    return str(krai.quantize(D(D(10)**-27)))


def krai_to_raw(amount):
    assert type(amount) is str
    raw = D(amount) * D(D(10)**27)
    return str(raw.quantize(D(1)))


def rai_from_raw(amount):
    assert type(amount) is str
    rai = D(amount) * D(D(10)**-24)
    return str(rai.quantize(D(D(10)**-24)))


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
            "0000000000000000000000000000000000000000000000000000000000000006"))
    bh.update(bytes.fromhex(account_key(block["account"])))
    bh.update(bytes.fromhex(block["previous"]))
    bh.update(bytes.fromhex(account_key(block["representative"])))
    bh.update(bytes.fromhex(format(int(block["balance"]), '032x')))
    bh.update(bytes.fromhex(block["link"]))

    return bh.hexdigest()


def sign_block(sk, pk, block):
    return nanopy.ed25519_blake2b.signature(
        bytes.fromhex(block_hash(block)), bytes.fromhex(sk),
        bytes.fromhex(pk)).hex()
