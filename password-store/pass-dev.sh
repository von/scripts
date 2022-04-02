# pass-dev.sh
# Description: Create scrach password store for testing

# Create a temporary GPG identity
# Kudos: https://www.gnupg.org/documentation/manuals/gnupg/Unattended-GPG-key-generation.html
export GNUPGHOME="$(mktemp -d)"
cat > ${GNUPGHOME}/makekey <<EOF
     %echo Generating a basic OpenPGP key
     Key-Type: DSA
     Key-Length: 1024
     Subkey-Type: ELG-E
     Subkey-Length: 1024
     Name-Real: Pass Tester
     Name-Comment: with stupid passphrase
     Name-Email: test@example.com
     Expire-Date: 0
     # Do a commit here, so that we can later print "done" :-)
     %commit
     %echo Done. Passphrase: abc
EOF
gpg --batch --passphrase "" --gen-key ${GNUPGHOME}/makekey
# Get keyid of key we just generated
keyid=$(gpg --list-keys test@example.com | grep pub | awk -F "/" '{print $2}' | awk '{print $1}')

export PASSWORD_STORE_DIR="$(mktemp -d)"
test -d ${PASSWORD_STORE_DIR} || mkdir ${PASSWORD_STORE_DIR}
pass init ${keyid}
