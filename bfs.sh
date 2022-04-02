#!/bin/sh
# List files under given directory breadth first.
#
# Useful for fzf so early results are likely more relevant.
#
# Yes, 'find' does not have a breadth first option.
#
# Kudos: https://unix.stackexchange.com/a/375375/29832

usage()
{
  cat <<-END
Usage: $0 [<starting directory>] <find options>"

Options:
  -h              Print help and exit.
END
# Note 'END' above most be fully left justified.
}

# Leading colon means silent errors, script will handle them
# Colon after a parameter, means that parameter has an argument in $OPTARG
while getopts ":h" opt; do
  case $opt in
    h) usage ; exit 0 ;;
    \?) echo "Invalid option: -$OPTARG" >&2 ;;
  esac
done

shift $(($OPTIND - 1))

# Use current directory if none given
path="."
if test $# -gt 0 ; then
  path="$1"
  shift
fi

if test $# -gt 0 ; then
  usage
  echo "Extra arguments ignored"
  exit 1
fi

i=0
while results=$(find "$path" -mindepth $i -maxdepth $i) && [[ -n $results ]]; do
  echo "$results"
  ((i++))
done
exit 0
