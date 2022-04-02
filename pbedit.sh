#!/usr/bin/env bash
# Edit the paste buffer

set -o errexit  # Exit on error

# Defaults
editor=${EDITOR:-vi}

usage()
{
  cat <<-END
Usage: $0 [<options>]

Options:
  -h              Print help and exit.
END
# Note 'END' above most be fully left justified.
}

# Leading colon means silent errors, script will handle them
# Colon after a parameter, means that parameter has an argument in $OPTARG
while getopts ":e:h" opt; do
  case $opt in
    e) editor=$OPTARG ;;
    h) usage ; exit 0 ;;
    \?) echo "Invalid option: -$OPTARG" >&2 ;;
  esac
done

shift $(($OPTIND - 1))

# Use --nofork for mvim
if [[ ${editor} == *mvim ]] ; then
  editor="${editor} --nofork"
fi

tmpfile=$(mktemp)".txt"
pbpaste -Prefer txt > ${tmpfile}
${editor} ${tmpfile}
cat ${tmpfile} | pbcopy
exit 0
