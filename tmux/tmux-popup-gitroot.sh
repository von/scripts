#!/usr/bin/env bash
# Open a tmux popup with a window in the gitroot of the current pane
# or for the path passed to the script. Intended to be be called
# from vim or similar.

# Options for 'tmux popup'
# Exit when complete, if successful
popup_opts="-E -E"

# Bottom of window
popup_opts+=" -xP -yP -w100% -h100%"

# Prefix for popup sessions
popup_prefix="popup"

# Options for started session
session_opts=""

usage()
{
  cat <<-END
Usage: $0 [<options>] [<path>]

<path>   Optional path to use for git root determination.

Options:
  -h              Print help and exit.
END
# Note 'END' above most be fully left justified.
}

set -o errexit  # Exit on error

# Leading colon means silent errors, script will handle them
# Colon after a parameter, means that parameter has an argument in $OPTARG
while getopts ":h" opt; do
  case $opt in
    h) usage ; exit 0 ;;
    \?) echo "Invalid option: -$OPTARG" >&2 ;;
  esac
done

shift $(($OPTIND - 1))

if test $# -eq 0 ; then
  gitroot=$(git rev-parse --show-toplevel)
else
  gitroot=$(cd "${1}" ; git rev-parse --show-toplevel)
  shift
fi

session_opts+=" -c \"${gitroot}\""

popup_session=${popup_prefix}-$(basename "${gitroot}")
cmd="tmux attach -t ${popup_session} || tmux new -s ${popup_session} ${session_opts}"

tmux popup ${popup_opts} "${cmd}"

exit 0
