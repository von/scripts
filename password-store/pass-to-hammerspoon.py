#!/usr/bin/env python3
"""Put password-store file into Hammerspoon registers.

Uses Hammerpoon commandline client:
http://www.hammerspoon.org/docs/hs.ipc.html
"""

import argparse
import fileinput
import itertools
import os
import os.path
import re
import subprocess
import sys
import time


# Hammerspoon CLI command
# Expected to take commands on stdin.
HS_CMD = "hs"

# Password-store command
PASS_CMD = "pass"


# Regexes for Password-store lines
EXPIRES_REGEX = re.compile("^Expires (?P<month>\d+)/(?P<year>\d+)$")
CVV_REGEX = re.compile("^(CVV:\w+)?^(?P<cvv>\d\d\d)$")


class HammerspoonCmd(object):
    """Class to create and execute Hammerpoon command"""
    def __init__(self, debug=False, quiet=False):
        self.cmd = ""
        self.debug = debug
        self.quiet = quiet

    def add_to_cmd(self, str):
        """Add str to command to be executed."""
        self.cmd += str

    def add_set_register(self, register, value):
        """Add code to set register"""
        self.add_to_cmd(
            'hs.pasteboard.setObject("{}", "Hammerspoon-register-{}")\n'.format(value,
                                                                                register))

    def add_clear_register(self, register):
        """Add code to clear register"""
        self.add_to_cmd(
            'hs.pasteboard.deletePasteboard("Hammerspoon-register-{}")\n'.format(register))

    def add_printf(self, message):
        """Add code to print given message"""
        self.add_to_cmd('hs.printf("{}")\n'.format(message))

    def execute(self):
        """Run built-up command using Hammerspoon CLI"""
        if self.debug:
            print("Running Hammerspoon command:\n" + self.cmd)
        pipe = subprocess.Popen([HS_CMD], stdin=subprocess.PIPE)
        pipe.communicate(self.cmd.encode('utf8'))
        rc = pipe.wait()
        if rc:
            print("{} returned {}".format(HS_CMD, rc))
        return rc


def parse_pass(args):
    """Parse password store output and feed into Hammerspoon."""
    hs_cmd = HammerspoonCmd(debug=args.debug, quiet=args.quiet)
    # Command we'll run after delay to clear the paste registers
    hs_clear_cmd = HammerspoonCmd(debug=args.debug, quiet=args.quiet)
    passfile = args.passfile[0]
    if not args.quiet:
        print("Parsing password store for \"" + passfile + "\"")
    hs_cmd.add_set_register("u", os.path.basename(passfile))
    if not args.quiet:
        hs_cmd.add_printf("Adding username to register 'u'")
    hs_clear_cmd.add_clear_register("u")
    output = subprocess.check_output([PASS_CMD, "show", passfile]).decode('utf8')
    for linenum, line in zip(itertools.count(1), output.split("\n")):
        if args.debug:
            print("LINE: " + line)
        if linenum == 1:
            # password
            hs_cmd.add_set_register("p", line.strip())
            if not args.quiet:
                hs_cmd.add_printf("Adding password to register 'p'")
            hs_clear_cmd.add_clear_register("p")
            continue
        # Subsequent lines
        m = EXPIRES_REGEX.match(line)
        if m:
            hs_cmd.add_set_register("m", m.group("month"))
            hs_cmd.add_set_register("y", m.group("year"))
            if not args.quiet:
                hs_cmd.add_printf("Adding expiration month to register 'm'")
                hs_cmd.add_printf("Adding expiration year to register 'y'")
            hs_clear_cmd.add_clear_register("m")
            hs_clear_cmd.add_clear_register("y")
            continue
        m = CVV_REGEX.match(line)
        if m:
            hs_cmd.add_set_register("c", m.group("cvv"))
            if not args.quiet:
                hs_cmd.add_printf("Adding CVV to register 'c'")
            hs_clear_cmd.add_clear_register("c")
            continue
    rc = hs_cmd.execute()
    if rc:
        return rc
    if args.clear:
        if not args.quiet:
            print("Sleeping {} seconds before clearing registers.".format(args.clear))
        time.sleep(args.clear)
        if not args.quiet:
            print("Clearing registers.")
        rc = hs_clear_cmd.execute()
    return rc


def make_parser():
    """Return arparse>ArgumentParser instance"""
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
    clear_group = parser.add_mutually_exclusive_group()
    clear_group.add_argument("-C", "--no-clear",
                             action='store_const', const=0,
                             dest="clear", default=45,
                             help="Don't clear registers")
    clear_group.add_argument("-c", "--clear-time",
                             action='store', dest="clear",
                             metavar="SECONDS", help="Set time before clearing registers")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    parser.add_argument('passfile', metavar='passfile', type=str, nargs=1,
                        help='Password store file to parse')
    return parser


def main(argv=None):
    parser = make_parser()
    args = parser.parse_args(argv if argv else sys.argv[1:])
    rc = parse_pass(args)
    return(rc)

if __name__ == "__main__":
    sys.exit(main())
