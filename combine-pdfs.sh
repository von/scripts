#!/usr/bin/env bash
# Combine multiple PDFs into one pdf.
#
# Uses ghostscript, which is installed via 'brew install ghostscript'
#
# Kudos: https://apple.stackexchange.com/a/293198/104604

FORCE=0

usage()
{
  cat <<-END
Usage: $0 [<options>] <source pdf1> <source pdf2> <source pdf3...> <output pdf>

Options:
  -f              Force overwrite of output pdf if it exists.
  -h              Print help and exit.
END
# Note 'END' above most be fully left justified.
}

# Leading colon means silent errors, script will handle them
# Colon after a parameter, means that parameter has an argument in $OPTARG
while getopts ":fh" opt; do
  case $opt in
    f) FORCE=1 ;;
    h) usage ; exit 0 ;;
    \?) echo "Invalid option: -$OPTARG" >&2 ;;
  esac
done

shift $(($OPTIND - 1))

if test $# -lt 3 ; then
  usage
  exit 1
fi

# Kudos: https://stackoverflow.com/a/26041521/197789
OUTPUT_PDF="${@: -1}"
if test -f "${OUTPUT_PDF}" -a $FORCE -eq 0 ; then
  echo "Output file ${OUTPUT_PDF} exists."
  exit 1
fi

echo "Outputing to ${OUTPUT_PDF}"

# ${@:1:$#-1} returns all but last argument
# https://stackoverflow.com/a/1215592/197789
declare -a INPUT_PDFS
INPUT_PDFS=( "${@:1:$#-1}" )

GS=${HOMEBREW_PREFIX:-/opt/homebrew}/bin/gs

if test -x "${GS}" ; then
  : # Ghostscript found
else
  echo "Ghostscript not found at ${GS}"
  exit 1
fi

# No '@Q' on INPUT_PDFS expansion here intentional as it adds unneeded
# quoting that confuses the shell.
${GS} -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="${OUTPUT_PDF}" "${INPUT_PDFS[@]}"
exit $?
