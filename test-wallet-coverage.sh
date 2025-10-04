set -ex

SRC=nano_1h38a9z1dzff6xuwu86z8g3q9pecz5uuxetdb59pjjpp4f5y3cxdadprn6w3
DST=nano_13k3ozab7hof3jruos6trmghebncxw9shdqk7adnas5csor74csr6knsaudj
REP=nano_3kc8wwut3u8g1kwa6x4drkzu346bdbyqzsn14tmabrpeobn8igksfqkzajbb

coverage run nanopy-wallet
coverage run --append nanopy-wallet open test -r $DST
echo send 0.00001
coverage run --append nanopy-wallet open test -s $DST -r $SRC
echo send 0.00001
coverage run --append nanopy-wallet open test -s $DST
coverage run --append nanopy-wallet open test -a -i 1
echo do not receive
coverage run --append nanopy-wallet open test -i 1
coverage run --append nanopy-wallet open test -i 1
coverage run --append nanopy-wallet open test -i 1 -s $SRC -e
coverage run --append nanopy-wallet open test -r $REP
coverage run --append nanopy-wallet -n banano
coverage run --append nanopy-wallet -n beta
coverage html
