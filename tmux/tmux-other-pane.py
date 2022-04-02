#!/usr/bin/env python3
# TODO: What is there is no other pane? Create one?
# TODO: Make sure other pane is visible and gets focus.

import argparse
import subprocess
import sys

TMUX_CMD="tmux"

SHELLS=["sh", "bash", "zsh"]

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
    parser.add_argument("-f", "--focus", action='store_true', default=False,
                        help="Focus on target pane after sending command")
    parser.add_argument("-t", "--target", action='store', default="{next}",
                        metavar="PANE", help="Pane to run comment in")
    parser.add_argument("-z", "--zoom", action='store_true', default=False,
                        help="Zoom other pane after sending command (implies --focus)")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    parser.add_argument('cmd', metavar='CMD', type=str, nargs='+',
                        help="Command to execute")
    return parser


def main(argv=None):
    parser = make_parser()
    args = parser.parse_args(argv if argv else sys.argv[1:])

    # Make sure there is another pane and create if needed.
    # Kudos: https://unix.stackexchange.com/questions/186390/tmux-get-number-of-panes-in-the-current-window-in-bash-variable#comment311064_186405
    num_panes = int(subprocess.check_output([TMUX_CMD,
                                          "display-message", "-p", "#{window_panes}"]))
    if num_panes == 1:
        # No other pane exists. Create one and send command.
        subprocess.check_call([TMUX_CMD,
                               # Use '-d' so we don't automatically switch to new pane
                               "split-window", "-d", ";",
                               "send-keys", "-t", args.target, " ".join(args.cmd), "Enter"])
    else:
        # Pane exists.
        # Get command from target pane and make sure its a shell so we don't
        # paste into some other running process.
        pane_cmd = subprocess.check_output(
            [TMUX_CMD,
             "select-pane", "-t", args.target, ";",
             "run-shell", "echo #{pane_current_command}" ";",
             "select-pane", "-t", "{last}"]
        ).decode('utf8').strip()
        if not pane_cmd in SHELLS:
            print("Process ({}) not a shell.".format(pane_cmd))
            return 1

        subprocess.check_call([TMUX_CMD, "send-keys",
                            "-t", args.target,
                            " ".join(args.cmd), "Enter"])

    # Command should have been sent. Handle other options.
    if args.focus or args.zoom:
        subprocess.check_call([TMUX_CMD, "select-pane", "-t", args.target])
        if args.zoom:
            subprocess.check_call([TMUX_CMD, "resize-pane", "-Z"])

    return(0)

if __name__ == "__main__":
    sys.exit(main())
