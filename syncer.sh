#!/bin/bash
# Given a path to a USB stick or other device, run an associated script
# to sync data to it.

CONF_DIR="${HOME}/.syncer/"

usage()
{
  cat <<-END
Usage: $0 [<options>] <path>

Options:
  -h              Print help and exit.
END
}

# do_rsync <src> <dst>
#  Make <dst> match <src>, deleting files in <dst> not in <src>
do_rsync()
{
  src=$1; shift
  dst=$1; shift
  test -n "$dst" || { echo "Usage: do_rsync <src> <dst>" ; return 1 ; }

  cd "${src}"
  # rsync options:
  # --size-only: I don't think the NAS keeps accurate timestamps
  # --ignore-errors: .Spotlight-V100 can cause errors
  # --delete-during: Delete files in dst not in source
  #
  # caffeinate options:
  #  -i: prevent system from idle sleeping
  #  -m: prevent disk from idle sleeping
  #  -s: prevent system from sleeping on AC power
  caffeinate -ims rsync -urv --size-only --delete-during --ignore-errors . "${dst}"
}

# do_sync <path1> <path2>
#  Make <path1> and <path2>, coping any files not in one to the other
do_sync()
{
  path1=$1; shift
  path2=$1; shift
  test -n "$dst" || { echo "Usage: do_sync <path1> <path2>" ; return 1 ; }

  cd "${path1}"
  # rsync options:
  # --size-only: I don't think the NAS keeps accurate timestamps
  # --ignore-errors: .Spotlight-V100 can cause errors
  #
  # caffeinate options:
  #  -i: prevent system from idle sleeping
  #  -m: prevent disk from idle sleeping
  #  -s: prevent system from sleeping on AC power
  caffeinate -ims rsync -urv --size-only --ignore-errors . "${path2}"
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

SYNC_PATH=$1; shift
if test -z "${SYNC_PATH}" ; then
  usage
  exit 1
fi

if test -d "${SYNC_PATH}" ; then
  :
else
  echo "Path not found: ${SYNC_PATH}"
  exit 1
fi

BASENAME=$(basename "${SYNC_PATH}")
CONF_FILE=${CONF_DIR}/${BASENAME}.sh

if test -e "${CONF_FILE}" ; then
  echo "Using ${CONF_FILE}"
else
  echo "No configuration file for ${SYNC_PATH}"
  exit 1
fi

source "${CONF_FILE}" "${SYNC_PATH}"
echo "Success."
exit 0
