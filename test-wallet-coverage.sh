set -ex

SRC=nano_1ye5an4ac3an51j799usynis8rtsff1u8f6er4aos3qqu45eiwkc1rk71f3u
DST=nano_3qwge3owjz5bccn4de91iwqhcgrddhpwk4ssdnieb9fb61sdj9f3gwbb9die
REP=nano_3kc8wwut3u8g1kwa6x4drkzu346bdbyqzsn14tmabrpeobn8igksfqkzajbb

coverage run nanopy-wallet
coverage run --append nanopy-wallet open test.kdbx test1 -r $DST
echo send 0.00001
coverage run --append nanopy-wallet open test.kdbx test1 -s $DST -r $SRC
echo send 0.00001
coverage run --append nanopy-wallet open test.kdbx test1 -s $DST
coverage run --append nanopy-wallet open test.kdbx test1 -a -i 1
echo do not receive
coverage run --append nanopy-wallet open test.kdbx test1 -i 1
coverage run --append nanopy-wallet open test.kdbx test1 -i 1
coverage run --append nanopy-wallet open test.kdbx test1 -i 1 -s $SRC --empty
echo copy and broadcast
coverage run --append nanopy-wallet open test.kdbx test1 -r $REP
coverage run --append nanopy-wallet -b
coverage run --append nanopy-wallet -n banano
coverage run --append nanopy-wallet -n beta
coverage html
