# nanopy
* Install by running `pip install nanopy` or `pip install nanopy[mnemonic,rpc]`.
  * `mnemonic` and `rpc` install dependencies of extra features.
* Point to a custom compiler (default is `gcc`) by prepending the installation command with `CC=path/to/custom/c/compiler`.
* For GPU, appropriate OpenCL ICD and headers are required. `sudo apt install ocl-icd-opencl-dev amd/intel/nvidia-opencl-icd`
  * Enable GPU usage by prepending the installation command with `USE_GPU=1`.
  * **GPU code is a bit of a hit and miss. It is not properly tested and may or may not work**

## Usage
```py
# create an account (defaults to NANO network) and set secret key
seed = "0000000...."
index = 2
acc = npy.Account()
acc.sk = npy.deterministic_key(seed, index)

# if it is not a new account, set the current state of the account (frontier, raw bal, rep)
acc.state = ("1234....", 1200000000000000, npy.Account(addr="nano_repaddress..."))

# create a receive block and optionally, change rep along with it
_hash = "5678...."
raw_amt = acc.network.to_raw("10")
rep = npy.Account(addr="nano_newrepaddress...")
rb = acc.receive(_hash, raw_amt, rep)

# create a send block
to = npy.Account(addr="nano_sendaddress...")
raw_amt = acc.network.to_raw("1")
sb = acc.send(to, raw_amt)

# broadcast
rpc.process(rb.json)
rpc.process(sb.json)
```

## Wallet
Although not part of the package, the light wallet included in the repository can be a reference to understand how the library works.

* Configuration is in `~/.config/nanopy.conf`
* `-n`, `--network`. Choose the network to interact with - nano, banano, or beta. The default network is nano.
* Checks state of accounts in `~/.config/nanopy.conf` by default.
* Open a wallet, `nanopy-wallet open FILE KEY`, and use seeds from *kdbx files. `FILE` is the *.kdbx database and `KEY` is a seed in it. See `nanopy-wallet open -h` for options.

## Support
Contact me on discord (`npy#2928`). You can support the project by reporting any bugs you find and/or submitting fixes/improvements. When submitting pull requests please format the code using `black` (for Python) or `clang-format` (for C).
```sh
clang-format -i nanopy/*.c
black docs nanopy tests nanopy-wallet setup.py
```
