# nanopy
Python implementation of NANO-related functions.

## C library for work generation
* For CPU blake2 libraries are required. `sudo apt-get install libb2-dev`
* For GPU, appropriate OpenCL ICD and headers are required. `sudo apt-get install ocl-icd-opencl-dev nvidia-opencl-icd/amd-opencl-icd`

Install the library by running `python setup.py build && python setup.py install`.

## WSGI node API
* `nanopy.wsgi` is a WSGI-Python script that routes requests from a public port to the node RPC. It has no Python dependencies and will run on pure Python.
* By default the tool looks for node RPC at `http://localhost:<port>`. `<port>` number varies depending on the url. If the url is one of `/rpc-nano`, `/rpc-xrb`, `/rpc-main`, `/rpc-live`, `<port>` is 7076. `/rpc-beta` sets `<port>` as 55000. `/rpc-banano` sets `<port>` as 7072. This means you can have multiple nodes running on the same machine and serve their corresponding RPCs at separate urls. 
* It is not safe to make all the RPC methods available. Hence, by default only a `minimal` set of RPC methods are made available. You can adjust the list `rpc_enabled` in `nanopy.wsgi` to change the list of methods that are made available. For e.g., if you want to provide work computation services, you can set `rpc_enabled = minimal + work`. To provide some nano specific tools, `rpc_enabled += tools`.

### Apache2 - mod_wsgi framework
* `sudo apt-get install libapache2-mod-wsgi-py3`
* Add the directives below into apache conf file, `/etc/apache2/sites-available/000-default.conf`. Modify the path as necessary. Node API will be served at `http://localhost/rpc-<network>` and RPC methods can be submitted as GET/POST requests.
```
WSGIScriptAliasMatch ^/rpc-(.{3,6}) /path/to/nanopy.wsgi
<Directory /path/to>
    Require all granted
</Directory>
```
* `sudo a2enmod wsgi && sudo systemctl restart apache2`
* If you want to throttle/rate-limit/authenticate your clients, apache2 has several modules that can help you with this. `mod_evasive, mod_ratelimit, mod_auth*`.

## Wallet
Although not part of the package, the light wallet included in the repository is a good reference to understand how the library works.

### Wallet options
* The wallet looks for default configuration in `$HOME/.config/nanopy/<network>.conf`.
  * Default mode of operation is to check state of all accounts in `$HOME/.config/nanopy/<network>.conf`.
* `--new`. Generate a new seed and derive index 0 account from it.
  * Seeds are generated using `os.urandom()`
  * Generated seeds are stored in a GnuPG AES256 encrypted file.
  * AES256 encryption key is 8 bytes salt + password stretched with 65011712 rounds of SHA512.
  * Wallets can also be made by encrypting a file that has a seed using the command, `gpg -ca --s2k-digest-algo SHA512 FILE`
  * Options used by the encryption can be verified by inspecting the header in the gpg file. `gpg --list-packets --verbose FILE.asc`. `cipher 9` is AES256. `s2k 3` is iterated and salted key derivation mode. `hash 10` corresponds to SHA512. `count` is the number of iterations (max 65011712).
  * To get the seed, `gpg -d FILE.asc`
* `--audit-file`. Check state of all accounts in a file.
* `--broadcast`. Broadcast a block in JSON format. Blocks generated on an air-gapped system using `--offline` tag can be broadcast using this option.
* `--network`. Choose the network to interact with. main, beta, banano.
  * The default network is main. On the main network, addresses can be input with either `xrb_` or `nano_` prefix. However, the RPC responses from the nodes are still in `xrb_` format.
* `-t` or `--tor`. Communicate with RPC node via the tor network.

The wallet has a sub-command, `nanopy-wallet open FILE.asc`, to unlock previously encrypted seeds. `open` has the following options.
* `-i` or `--index`. Index of the account unlocked from the seed. (Default=0)
* `-s` or `--send-to`. Supply destination address to create a send block.
* `--empty-to`. Empty out funds to the specified send address.
* `--unlock`. Unlock wallet.
* `-c` or `--change-rep-to`. Supply representative address to change representative.
  * Change representative tag can be combined with send and receive blocks.
* `--audit`. Check state of all accounts from index 0 to the specified limit. (limit is supplied using the `-i` tag)
* `--offline`. Generate blocks in offline mode. In the offline mode, current state of the account is acquired from the default configuration in `$HOME/.config/nanopy/<network>.conf`. Refer to the sample file for more details.
* `--demo`. Run in demo mode. Never broadcast blocks.

## Pull requests
  * When submitting pull requests please format the code using `yapf` (for Python) or `clang-format` (for C).
  * `clang-format --style google -i nanopy/work.c`
  * `yapf --style google -i -r nanopy`
  * `yapf --style google -i nanopy-wallet`
  * `yapf --style google -i setup.py`
  * `yapf --style google -i nanopy.wsgi`

## Contact
  * Find me on discord in NANO's channel. My handle is `128#2928`.

## Donations
  * `nano_3ooycog5ejbce9x7nmm5aueui18d1kpnd74gc4s67nid114c5bp4g9nowusy`
