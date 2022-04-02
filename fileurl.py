#!/usr/bin/env python3
"""Given a path to a file, return a URL for that file."""

import argparse
import os.path
import sys
import urllib.request, urllib.parse, urllib.error, urllib.parse


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
    parser.add_argument('path', metavar='path', type=str, nargs=1,
                        help='path for file')
    args = parser.parse_args()

    path = os.path.abspath(args.path[0])
    print(urllib.parse.urlunsplit(("file", "", urllib.request.pathname2url(path), "", "")))
    return(0)

if __name__ == "__main__":
    sys.exit(main())
