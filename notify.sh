#!/bin/bash
# Display a Mac notification
# Kudos: https://apple.stackexchange.com/a/115373/104604

usage()
{
  cat <<-END
Usage: $0 [<options>] <notification message>

Options:
  -h              Print help and exit.
  -s <subtitle>   Set notification subtitle (ignored if no title given)
  -s <title>      Set notification title
END
}

# Leading colon means silent errors, script will handle them
# Colon after a parameter, means that parameter has an argument in $OPTARG
while getopts ":hs:t:" opt; do
  case $opt in
    h) usage ; exit 0 ;;
    s) subtitle="${OPTARG}" ;;
    t) title="${OPTARG}" ;;
    \?) echo "Invalid option: -$OPTARG" >&2 ;;
  esac
done

shift $(($OPTIND - 1))

message="${@}"
if test -z "${message}" ; then
  usage
  exit 1
fi


(  # subshell to produce script
  printf "display notification \"${message}\""
  if test -n "${title}" ; then
    printf " with title \"${title}\""
    if test -n "${subtitle}" ; then
      printf " subtitle \"${subtitle}\""
    fi
  fi
  printf "\n"
) | osascript -i
exit $?
