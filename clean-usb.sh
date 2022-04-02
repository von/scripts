#!/bin/sh
# Clean all the stuff MacOSX puts on a USB stick
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
cd "${usb_path}"
rm -rf .Spotlight-V100 .fseventsd
find . -type f -name '\._*' -delete
exit 0
