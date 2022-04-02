#!/bin/sh
# Popup a tmux window with persistent session
# Kudos: https://github.com/meain/dotfiles/blob/master/scripts/.bin/popuptmux
#
# Reads configuration file based on window name from ~/.tmux/popup/

set -o errexit  # Exit on error

# Options {{{
# These may be overridden by the configuration file

# Options for 'tmux popup'
# Exit when complete, if successful
popup_opts="-E -E"
# Bottom of window
popup_opts+=" -xP -yP -w100% -h100%"

# Options for started session
session_opts=""

# Window name for session
# If empty, session name is used
window_name=""

# Tmux commands to run in new session
# Must be separated by escaped semicolon ('\;')
# If session is destroyed, dettach client to avoid attaching to other session
session_cmds="set-option detach-on-destroy on"

# Prefix for popup sessions
popup_prefix="popup"

# Name to use for popup session (with popup_prefix)
session_name=""

# Prefix for configuration files
config_path="${HOME}/.tmux/popup/"

# }}} Options

# read_config() {{{
# Read configuration from
# This file is sourced as a set of bash commands and is intended
# to modify variables above.
function read_config() {
  local path=$1 ; shift
  if test ! -f "${path}" ; then
    echo "Configuration file does not exist: ${path}" 1>&2
    return 1
  fi
  source "${path}"
}
# }}} read_config()

# Argument processing {{{

usage()
{
  cat <<-END
Usage: $0 [<options>] [<cmd> <args>]

Options:
  -a <session>    Attach to session with name 'popup-<session>'
  -A              Attach to session with name 'popup-<window name>'
  -c              Popup starts in current pane's working directory
  -h              Print help and exit.
END
# Note 'END' above most be fully left justified.
}

# Leading colon means silent errors, script will handle them
# Colon after a parameter, means that parameter has an argument in $OPTARG
while getopts ":a:Ach" opt; do
  case $opt in
    a) session_name="${OPTARG}" ;;
    A) session_name="$(tmux display-message -p -F "#{window_name}")" ;;
    c) popup_opts+=' -d #{pane_current_path}' ;;
    h) usage ; exit 0 ;;
    \?) echo "Invalid option: -$OPTARG" >&2 ;;
  esac
done

shift $(($OPTIND - 1))
# }}} Argument processing

if test -n "${session_name}" ; then
  popup_session=${popup_prefix}-${session_name}

  if test -f "${config_path}/${session_name}" ; then
    read_config "${config_path}/${session_name}"
  fi

  session_opts+=" -n ${window_name:-${session_name}}"
  if test -n "${session_cmds}" ; then
    session_opts+=" \; ${session_cmds}"
  fi

  cmd="tmux attach -t ${popup_session} || tmux new -s ${popup_session} ${session_opts}"
else
  set -x
  if test $# -eq 0 ; then
    usage
    exit 1
  fi
  cmd="$@"
fi

# Dettach if we are in a popup session {{{ #
#
current_session="$(tmux display-message -p -F "#{session_name}")"

if [[ "$current_session" =~ ^${popup_prefix}.* ]] ; then
  # Already in a popup session, disconnect
  tmux detach-client
  exit $?
fi

# }}} Dettach if we are in a popup session #

tmux popup ${popup_opts} "${cmd}"
exit $?
# vim: foldmethod=marker: #
