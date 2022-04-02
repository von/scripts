#!/usr/bin/env python3
"""Check for network connectivity (including captive portals)

Uses connectivitycheck.gstatic.com/generate_204

Kudos: https://android.stackexchange.com/a/129811"""

import argparse
import sys
import urllib.request, urllib.parse, urllib.error

CHECK_URL="http://connectivitycheck.gstatic.com/generate_204"

def main(argv=None):
    # Do argv default this way, as doing it in the functional
    # declaration sets it at compile time.
    if argv is None:
        argv = sys.argv

    # Argument parsing
    parser = argparse.ArgumentParser(
        description=__doc__,  # printed with -h/--help
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # To have --help print defaults with trade-off it changes
        # formatting, use: ArgumentDefaultsHelpFormatter
    )
    # Only allow one of debug/quiet mode
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument("-d", "--debug",
                                 action='store_true', default=False,
                                 help="Turn on debugging")
    verbosity_group.add_argument("-q", "--quiet",
                                 action="store_true", default=False,
                                 help="run quietly")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    args = parser.parse_args()

    debug = print if args.debug else lambda *a, **k:None

    debug("Checking {}".format(CHECK_URL))
    try:
        f = urllib.request.urlopen(CHECK_URL)
    except Exception as ex:
        debug(str(ex))
        print("No network connectivity")
        return(1)

    # We should get back a 204 code, if not we're probably hitting a captive
    # portal.
    if f.getcode() != 204:
        debug("Did not get expected 204 code")
        print("Cannot reach Internet")
        return(1)

    # Success
    debug("Success.")
    return(0)

if __name__ == "__main__":
    sys.exit(main())
