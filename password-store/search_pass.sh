#!/bin/bash
# Search passwords for string and return matches, one per line

store="${PASSWORD_STORE_DIR:-$HOME/.password-store}"

if test $# -ne 1 ; then
  echo "Usage: $0 <search_string>" 1>&2
  exit 1
fi

# Change dir to store so we can run 'find .' and not match
# on password store directory.
cd "${store}"

# All arguments escaped and joined into one string
search_string="$*"

# Find first clause prunes .git/ directory
# Second clause matches full paths with matching directory components
# Third clause matches any part of filename, ignoring .gpg suffix
# -iname and -ipath are case-insensitive
# sed command strips path prefix and .gpg suffix
find . -type d -name .git -prune \
  -o -ipath "*/*${search_string}*/*" -type f -print \
  -o -iname "*${search_string}*.gpg" -type f -print \
  | sed -e "s#./##" -e 's#\.gpg$##' | sort
