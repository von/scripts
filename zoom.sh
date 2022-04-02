#!/usr/bin/env bash
# Manage Zoom.app from the commandline
# Uses environment variable ZOOM_DEFAULT_ID if set.

usage() {
  echo "$0 <zoom id>"
}

id=${1:-$ZOOM_DEFAULT_ID}
if test -z "${id}" ; then
  usage
  exit 1
fi

echo "Joining Zoom meeting ${id}"
open "zoommtg://zoom.us/join?action=join&confno=${id}"
exit $?
