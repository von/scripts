#!/usr/bin/env python3
"""Manage a playlist of files

A playlist is a text file with one directory or file per line.
If a line contains a directory, all of its contents are copied."""

import argparse
import errno
import os
import os.path
import shutil
import sys


def sizeof_fmt(num, fmt="%5.3f", suffix='B'):
    """Return string representation of given size"""
    # Force num to be a flost
    num += 0.0
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024:
            s = fmt % num
            s += unit
            s += suffix
            return s
        num /= 1024
    return "%.1f%s%s" % (num, 'Y', suffix)


class Playlist(object):

    def __init__(self, path):
        self.path = path

    def copy(self, dest_path, path_depth=3):
        """Copy playlist files to destination

        path_depth is the number of path components to maintain.
        Default is 3, i.e. Artist/Album/Song"""
        for file in self.files():
            relfile = os.path.join(
                *os.path.normpath(file).split(os.sep)[-path_depth:])
            dest = os.path.abspath(os.path.join(dest_path, relfile))
            try:
                os.makedirs(os.path.dirname(dest))
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise
            if not os.path.exists(dest):
                print("Copying to {}".format(dest))
                shutil.copy(file, dest)

    def export(self, dest_path):
        """Export playlist to m3u file"""
        print("Write playlist to {}".format(dest_path))
        with open(dest_path, "w") as dest:
            for file in self.files():
                dest.write(file + "\n")

    def files(self):
        """Iterator returning files in playlist"""
        with open(self.path) as f:
            for entry in [e.strip() for e in f.readlines()]:
                if not os.path.exists(entry):
                    print("Warning: {} does not exist".format(entry))
                elif os.path.isfile(entry):
                    yield entry
                elif os.path.isdir(entry):
                    for root, dirs, files in os.walk(entry):
                        for f in files:
                            yield os.path.join(root, f)

    def size(self):
        """Return total size of playlist"""
        return sum([os.path.getsize(f) for f in self.files()])


def copy_cmd(args):
    args.playlist.copy(args.dest[0])
    return 0


def export_cmd(args):
    args.playlist.export(args.dest[0])
    return 0


def size_cmd(args):
    size = args.playlist.size()
    print(sizeof_fmt(size))
    return 0


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
    subparsers = parser.add_subparsers()

    # 'copy' subcommand
    parser_copy = subparsers.add_parser("copy", help="Copy playlist to dest")
    parser_copy.add_argument("playlist", metavar="playlist", type=str, nargs=1,
                             help="playlist")
    parser_copy.add_argument("dest", metavar="dest", type=str, nargs=1,
                             help="destination path")
    parser_copy.set_defaults(func=copy_cmd)

    # 'export' subcommand
    parser_export = subparsers.add_parser("export",
                                          help="Export playlist to m3u file")
    parser_export.add_argument("playlist", metavar="playlist", type=str, nargs=1,
                             help="playlist")
    parser_export.add_argument("dest", metavar="dest", type=str, nargs=1,
                             help="destination path")
    parser_export.set_defaults(func=export_cmd)

    # 'size' subcommand
    parser_size = subparsers.add_parser("size", help="Calculate playlist size")
    parser_size.add_argument("playlist", metavar="playlist", type=str, nargs=1,
                             help="playlist")
    parser_size.set_defaults(func=size_cmd)

    args = parser.parse_args()

    try:
        if args.playlist:
            args.playlist = Playlist(args.playlist[0])
    except AttributeError:
        # No playlist provided
        parser.print_usage()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
