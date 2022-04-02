#!/usr/bin/env python3
"""Manage the OSX screensaver

OSX seems to only accept following values for screensaver idle delay:
60, 120, 300, 600, 1200, 1800, 6000

"""

import argparse
import subprocess
import sys
import time

# Default time to delay screensaver in seconds.
# Note, see --delay, this must be one of set of values accepted by OSC.
DEFAULT_DELAY = 1200

# Default time to suspend in seconds
DEFAULT_SUSPEND_TIME = 3600


def killall_cfprefsd():
    """Restart cfprefsd. Needed to causes defaults to be read.

    Kudos: https://superuser.com/a/914884"""
    return subprocess.call(["killall", "cfprefsd"])


def set_idleTime(seconds):
    """Set idleTime for screensaver.

    0 disables the screensaver.

    Otherwise, OSX seems to only accept following values:
    60, 120, 300, 600, 1200, 1800, 6000
    Anything else defaults to 1200.
    """
    rc = subprocess.call(["defaults",
                          "-currentHost",
                          "write",
                          "com.apple.screensaver",
                          "idleTime",
                          "-int",
                          str(seconds)
                          ])
    if rc:
        return rc
    rc = killall_cfprefsd()
    return rc


def get_idleTime():
    """Get idleTime for screensaver in seconds"""
    time_str = subprocess.check_output(
        ["defaults",
         "-currentHost",
         "read",
         "com.apple.screensaver",
         "idleTime"
         ])
    time = int(time_str.strip())
    return time


def cmd_disable(args):
    """Disable screensaver"""
    args.print_func("Disabling screensaver")
    return set_idleTime(0)


def cmd_enable(args):
    """Enable screensaver

    If args.time is set, set delay for screensave to args.time seconds.
    See set_idleTime() for details."""
    delay = args.delay
    args.print_func("Enabling screensaver (delay: {}s)".format(delay))
    return set_idleTime(delay)


def cmd_get(args):
    """Print screensaver timeout"""
    args.print_func(get_idleTime())
    return 0


def cmd_suspend(args):
    """Suspend screensaver

    If args.delay is set, suspend for args.delay seconds, else one hour"""
    suspend_time = args.time
    delay = get_idleTime()
    args.print_func(
        "Suspending screensaver for {} seconds".format(suspend_time))
    rc = set_idleTime(0)
    if rc:
        return rc
    time.sleep(suspend_time)
    args.print_func(
        "Restoring screensaver ({}s)".format(delay))
    rc = set_idleTime(delay)
    return(rc)


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
    # TODO: If no command given, an error results. Should print help.
    parser.set_defaults(
        cmd_func=None,
        print_func=print,
        )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    subparsers = parser.add_subparsers(help="Commands")

    # disable command
    parser_disable = subparsers.add_parser("disable",
                                           help="disable screensaver")
    parser_disable.set_defaults(cmd_func=cmd_disable)

    # enable command
    parser_enable = subparsers.add_parser("enable",
                                          help="enable screensaver")
    # delay command
    parser_enable.set_defaults(
        cmd_func=cmd_enable,
        delay=DEFAULT_DELAY
    )
    parser_enable.add_argument("delay",
                               metavar="seconds",
                               nargs='?',
                               type=int,
                               # OSX seems to only accept these values
                               # anything else defaults to 1200
                               choices=[60, 120, 300, 600,
                                        1200, 1800, 6000])

    # 'get' command: display idle time
    parser_disable = subparsers.add_parser("get",
                                           help="get screensave idle time")
    parser_disable.set_defaults(cmd_func=cmd_get)

    # suspend command
    parser_suspend = subparsers.add_parser("suspend",
                                           help="suspend screensaver")
    parser_suspend.set_defaults(
        cmd_func=cmd_suspend,
        time=DEFAULT_SUSPEND_TIME,
        )
    parser_suspend.add_argument("time",
                                metavar="seconds",
                                nargs='?',
                                type=int)

    args = parser.parse_args()
    return args.cmd_func(args)

if __name__ == "__main__":
    sys.exit(main())
