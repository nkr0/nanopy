# nanopy
Python 3 implementation of NANO-related functions and an RPC light wallet.

Addresses can be input in both `xrb_` and `nano_`. However, the RPC responses from the nodes are still in `xrb_` format.

## Wallet options
* The wallet looks for default configuration in `$HOME/.config/nanopy-wallet.conf`.
  * Default mode of operation is to check state of all accounts in `$HOME/.config/nanopy-wallet.conf`.
* `--new`. Generate a new seed and derive index 0 account from it.
  * Seeds are generated using `os.urandom()`
  * Generated seeds are stored in a GnuPG AES256 encrypted file.
  * AES256 encryption key is 8 bytes salt + password stretched with 65011712 rounds of SHA512.
* `-i` or `--index`. Change the index of the generated account from the default 0.
* `--send-to`. Supply destination address to create a send block.
  * Send amount is rounded off to 6 decimal places.
* `--empty-to`. Empty out funds to the specified send address.
* `--unlock`. Unlock wallet.
* `--change-rep-to`. Supply representative address to change representative.
  * Change representative tag can be combined with send and receive blocks.
* `--remote`. Compute PoW on the RPC node.
  * Work generation is local by default. If the C library is compiled, that is used. Otherwise, the python function is used.
  * Use this command to compile the C library. `gcc -lb2 -fopenmp -shared -Wl,-soname,libnanopow -o libnanopow.so -fPIC nano_pow.c`
* `--audit-seed`. Check state of all accounts from index 0 to the specified limit.
* `--audit-file`. Check state of all accounts in a file.
* `-t` or `--tor`. Communicate with RPC node via the tor network.
* `--demo`. Run in demo mode. Never broadcast blocks.
