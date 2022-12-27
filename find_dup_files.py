#!/usr/bin/env python3
"""Find and print duplicate (identical) files."""
import argparse
import filecmp
import itertools
import os
import os.path
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
    parser.add_argument("files", metavar="files", type=str, nargs="*",
                        help="Files to check (default is all in current directory")
    return parser


def main(argv=None):
    parser = make_argparser()
    args = parser.parse_args(argv if argv else sys.argv[1:])
    if len(args.files):
        files = args.files
    else:
        files = filter(lambda f: os.path.isfile(f), os.listdir("."))

    for pairs in itertools.combinations(files, 2):
        if filecmp.cmp(pairs[0], pairs[1]):
            print(f"{pairs[0]}, {pairs[1]}")

    return(0)


if __name__ == "__main__":
    sys.exit(main())
