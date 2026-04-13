# nanopy
*nanopy* includes *C* extensions for work generation and signing, and therefore needs a compiler to install.

```sh
sudo apt install gcc python3-dev
pip install nanopy
```

When needed, use the environment variables `CC`, `LDSHARED`, `CFLAGS`, and `LDFLAGS` to tweak build options. See [*setuptools* documentation](https://setuptools.pypa.io/) for further info.

GPU support can be enabled with ``USE_OCL=1`` and appropriate *OpenCL* dependencies.

```sh
sudo apt install gcc python3-dev ocl-icd-opencl-dev intel/mesa/nvidia/pocl/rocm-opencl-icd
USE_OCL=1 pip install nanopy
```

* Install `mnemonic` to generate mnemonic wallets.
* Install `requests` or `websocket-client` to use *http* or *websocket* *RPC*, respectively.

## Usage
```py
from nanopy import Account, deterministic_key
from nanopy.rpc import HTTP

# create an account (defaults to NANO network) and set secret key
acc = Account(sk=deterministic_key(seed="0000000...."))

# if it is not a new account, set the current state of the account (frontier, raw bal, rep)
acc.state = ("1234....", 1200000000000000, Account(addr="nano_repaddress..."))

# create a receive block and optionally, change rep along with it
rb = acc.receive(hash_="5678....", raw_amt=acc.network.to_raw("10"), rep=Account(addr="nano_newrepaddress..."))

# create a send block
sb = acc.send(Account(addr="nano_sendaddress..."), acc.network.to_raw("1"))

# broadcast
r = HTTP(url="http://localhost:7076")
r.process(rb.json)
r.process(sb.json)
```

## Wallet
A cli wallet is included with the library

* Configuration is in `~/.config/nanopy.ini`

```ini
[nano]
nano_1111111111111111111111111111111111111111111111111111hifc8npp
nano_16aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46aj46ajbtsyew7c
rpc = http://localhost:7076
```

* `-n`, `--network`. Choose the network to interact with - *nano*, *banano*, or *beta*. The default network is *nano*.
* Checks state of accounts in `~/.config/nanopy.ini` by default.
* Open a wallet, `nanopy-wallet open FILE KEY`. `KEY` is a seed in a KDBX `FILE`. See `nanopy-wallet open -h` for options.
