#!/bin/sh
######################################################################
#
# Make a new CA.
#
######################################################################

# Exit on any error
set -e

. include.sh

######################################################################
#
# Defaults
#

COUNTRY_NAME="US"
STATE_NAME="SomeState"
EMAIL_ADDR="test@example.org"
ORG_NAME="SomeOrg"
OU_NAME="CA"

######################################################################
#
# Parse commandline options
#

usage() {
cat <<EOF
Usage: $0 [<options>] <CA name>

Options:
  -c                   Set country of CA [default: ${COUNTRY_NAME}]
  -h                   Print help and exit.
  -o <organization>    Set organization of CA [default: ${ORG_NAME}]
  -p <pki path>        Set path for PKI files [default: ${PKI_PATH}]
  -u <orgUnit>         Set organizational unit of CA [default: ${OU_NAME}]
EOF
}

while getopts c:ho:p:u: arg
do
  case $arg in
  c) COUNTRY_NAME=$OPTARG ;;
  h) usage ; exit 0 ;;
  o) ORG_NAME=$OPTARG ;;
  p) PKI_PATH=$OPTARG ;;
  u) OU_NAME=$OPTARG ;;
  ?)
    echo "Unknown option: -$ARG"
    usage
    exit 1
  esac
done

shift `expr $OPTIND - 1`

if [ $# -gt 0 ]; then
  ca_name=$1
  shift
else
  echo "Missing CA name argument"
  usage
  exit 1
fi

######################################################################
#
# Create CA directory
#

if [ ! -d $PKI_PATH ]; then
    echo "Creating ${PKI_PATH}"
    mkdir -p $PKI_PATH
fi

ca_dir=${PKI_PATH}/CA/${ca_name}

if [ -e $ca_dir ]; then
  echo "CA directory $ca_dir already exists."
  exit 1;
fi

echo "Creating CA directory $ca_dir and contents"
mkdir -p $ca_dir
mkdir ${ca_dir}/certs
touch ${ca_dir}/index.txt
echo "01" > $ca_dir/serial

######################################################################
#
# Copy in configuration file
#

echo "Creating CA configuration"

ca_config=$ca_dir/ca.cnf
ca_key=$ca_dir/key.pem
ca_cert=$ca_dir/cert.pem
pwd=`pwd`

sed_script=""
sed_script=${sed_script}"s|Xdir|${ca_dir}|g;"
sed_script=${sed_script}"s|Xca_name|${ca_name}|g;"
sed_script=${sed_script}"s|Xca_key|${ca_key}|g;"
sed_script=${sed_script}"s|Xstate_name|${STATE_NAME}|g;"
sed_script=${sed_script}"s|Xcountry_name|${COUNTRY_NAME}|g;"
sed_script=${sed_script}"s|Xemail_addr|${EMAIL_ADDR}|g;"
sed_script=${sed_script}"s|Xorg_name|${ORG_NAME}|g;"
sed_script=${sed_script}"s|Xou_name|${OU_NAME}|g;"

sed $sed_script ca.cnf.in > $ca_config

######################################################################
#
# Generate the key and cert
#

echo "Generating CA certificate"

# These variables are used in CA configuration
COMMON_NAME=${ca_name}
export COMMON_NAME
export OU_NAME

${openssl} req -x509 -newkey rsa \
  -out ${ca_cert} \
  -keyout ${ca_key} \
  -days $lifetime \
  -config $ca_config \
  -nodes

######################################################################
#
# Ok generate the Globus-specific stuff. First ca cert file.
#

echo "Generating Globus-specific stuff"

ca_hash=`${openssl} x509 -in $ca_cert -hash -noout`

cp ${ca_cert} ${ca_dir}/${ca_hash}.0

ca_signing_policy=${ca_dir}/${ca_hash}.signing_policy
dn="/C=${COUNTRY_NAME}/O=${ORG_NAME}/OU=${OU_NAME}/CN=${COMMON_NAME}"
namespace="/C=${COUNTRY_NAME}/O=${ORG_NAME}/*"

sed_script=""
sed_script="${sed_script}s|Xdn|${dn}|g;"
sed_script="${sed_script}s|Xnamespace|${namespace}|g;"

sed "${sed_script}" signing_policy.in > $ca_signing_policy

######################################################################
#
# Success
#

echo "Success."
exit 0

#
# End
#
######################################################################


