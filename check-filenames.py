#!/usr/bin/env python3
"""Check filenames for unicode, leading/trailing whitespace, etc."""
import argparse
import itertools
import os
import sys


def make_argparser():
    """Return arparse.ArgumentParser instance"""
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
    parser.add_argument("path", metavar="path", type=str,
                        default=os.path.curdir,
                        help="Path to check (default is current directory)")
    return parser


def main(argv=None):
    parser = make_argparser()
    args = parser.parse_args(argv if argv else sys.argv[1:])

    for root, dirs, files in os.walk(args.path):
        for file in itertools.chain(dirs, files):
            path = os.path.join(root, file)
            if file != file.strip():
                print(f"Whitespace: {path}")
            try:
                file.encode('ascii')
            except UnicodeEncodeError:
                print(f"Non-ascii: {path}")

    return(0)


if __name__ == "__main__":
    sys.exit(main())
