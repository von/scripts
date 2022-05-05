#!/bin/sh

_dotbot=dotbot
_dotbot_args="-Q"

# Kudos: https://stackoverflow.com/a/246128/197789
_path=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

_conf=${_path}/install.conf.yaml

echo "Installing from ${_path}"
${_dotbot} ${_dotbot_args} -d ${_path} -c ${_conf} || exit 1
echo "Success."
exit 0
