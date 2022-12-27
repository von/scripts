#!/bin/sh
# Clean all the stuff MacOSX puts on a USB stick
#
# Note that whatever terminal program this is run in will need
# full disk access permissions or you will get "Operation not
# permitted" errors.
# System Preferences ->  Security and Privacy -> Privacy -> Full Disk Access
if test $# -ne 1 ; then
  echo "$0 <path to USB>"
  exit 1
fi

usb_path=$1; shift

if test ! -d "${usb_path}" ; then
  echo "USB path \"${usb_path}\" does not exist."
  exit 1
fi

set errexit

echo "Cleaning \"${usb_path}\""
echo "If you get errors, make sure the terminal program has"
echo "full disk access permissions:"
echo "  System Preferences ->  Security and Privacy -> Privacy -> Full Disk Access"0
cd "${usb_path}"
rm -rf .Spotlight-V100 .fseventsd
find . -type f -name '\._*' -delete
exit 0
