#!/usr/bin/env python3
"""Parse the output of password-store and render as requested

Intended execution: pass <store> | pass-parse [<options>]"""

import argparse
import fileinput
import os
import subprocess
import sys


def parse_input(args):
    """Parse password store coming from stdin

    This is a coroutine yielding each line for output.
    It may send the password to pastebuffer."""
    for line in fileinput.input("-"):
        if fileinput.isfirstline():
            # Handle password
            if args.clipboard:
                to_pastebuffer(line)
            if args.tail:
                pass  # Discard password
            elif args.chunk:
                # Kudos: http://stackoverflow.com/a/9475354/197789
                yield " ".join([line[i:i+args.chunk]
                                for i in range(0, len(line), args.chunk)])
            else:
                yield line
        else:
            # Handle lines after password
            yield line


def to_pastebuffer(text):
    """Put the given text into the pastebuffer"""
    # XXX Mac-specific
    pb_prog = "pbcopy"
    pipe = subprocess.Popen([pb_prog], stdin=subprocess.PIPE)
    pipe.communicate(text.encode("utf-8"))
    retcode = pipe.wait()
    if retcode:
        print("{} returned {}".format(pb_prog, retcode))


def show_output(output, timeout=120):
    """Show the output to the user via vim"""
    # "vim -" reads contents to be edited from stdin, avoids vim
    # complaining about stdin not being a tty.
    cmd = os.environ["EDITOR"] if "EDITOR" in os.environ else "vi"
    pipe = subprocess.Popen([cmd, "-R", "-"], stdin=subprocess.PIPE)
    try:
        pipe.communicate(output.encode("utf-8"), timeout=timeout)
    except subprocess.TimeoutExpired:
        pipe.terminate()
        # Call wait otherwise print() doesn't work
        retcode = pipe.wait()
        print("Timeout reached.")
    else:
        # Process has already exited, get return code
        retcode = pipe.wait()
        if retcode:
            print("Vim returned {}".format(retcode))


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
    parser.add_argument("-c", "--clipboard",
                        action='store_true', default=False,
                        help="Send password to clipboard")
    # What to do with the password
    passwd_group = parser.add_mutually_exclusive_group()
    passwd_group.add_argument("-C", "--chunk",
                              action="store_const", const=3, default=0,
                              help="Chunk password")
    passwd_group.add_argument("-t", "--tail",
                              action="store_true", default=False,
                              help="Discard password in output")
    try:
        args = parser.parse_args()
    except SystemExit:
        # Discard input on stdin to keep gpg from complaining about
        # a broken pipe.
        for line in fileinput.input("-"):
            pass
        return(1)

    output = "".join(parse_input(args))
    if len(output) == 0:
        return(1)
    show_output(output)
    return(0)


if __name__ == "__main__":
    sys.exit(main())
