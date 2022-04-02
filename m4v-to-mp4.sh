#!/bin/bash
# Convert an .m4v file to an .mp4 file
# Uses HandBrakeCLI (install via 'brew cask install handbrakecli')

# Defaults
preset="Normal"

usage()
{
  cat <<-END
Usage: $0 [<options>] <m4v file>

Options:
  -h              Print help and exit.
END
}

# Leading colon means silent errors, script will handle them
# Colon after a parameter, means that parameter has an argument in $OPTARG
while getopts ":hp:" opt; do
  case $opt in
    h) usage ; exit 0 ;;
    p) preset=$OPTARG ; echo "Using preset: ${preset}" ;;
    \?) echo "Invalid option: -$OPTARG" >&2 ;;
  esac
done

shift $(($OPTIND - 1))

if test $# -ne 1 ; then
  echo "Missing input filename" >&2
  usage
  exit 1
fi

input_file=$1 ; shift
output_file=${input_file/.m4v/.mp4}

HandBrakeCLI --preset ${preset} -i "${input_file}" -o "${output_file}"
if test $? -ne 0 ; then
  echo "HandBrakeCLI exited with status $?" >&2
  exit $?
fi
ls -l "${output_file}"
echo "Success."
exit 0
