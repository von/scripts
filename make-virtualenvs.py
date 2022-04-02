#!/usr/bin/env python3
"""Create a set of virtualenvs as specified by a configuration file
(~/.virtualenvs.conf by default)"""

# Python 3.6+ required due to f-strings

import argparse
import configparser
import os.path
import subprocess
import sys
import venv

# Constants
PIP = "pip"


# Output functions
output = print


def error(*args, **kwargs):
    """Output an error message."""
    print(*args, file=sys.stderr, **kwargs)


def get_path(venv, config):
    """Return the path for given environment.
    By default it is ~/.virtualenvs/<name>"""
    try:
        path = config[venv]["path"]
    except KeyError:
        pass
    else:
        return path
    try:
        venv_path = config["DEFAULT"]["venv_path"]
    except KeyError:
        venv_path = "~/.virtualenvs"
    return os.path.join(venv_path, venv)


def do_create(args, config):
    """Create virtualenvs"""
    error_detected = 0
    output("Creating virtualenvs...")
    sections = args.venvs or config.sections()
    for s in sections:
        try:
            v = config[s]
        except KeyError:
            error(f"Unknown virtualenv {s}")
            error_detected = 1
            continue
        if "skip" in v:
            rc = subprocess.run(v["skip"]).returncode
            if not rc:
                output("Skipping...")
                continue
        path = get_path(s, config)
        if os.path.exists(os.path.expanduser(path)) and not args.force:
            output(f"Virtualenv {s} exists ({path})")
            continue
        output(f"Creating virtualenv {s} at {path}")
        venv.create(os.path.expanduser(path),
                    system_site_packages=v.getboolean(
                        "system_site_packages"),
                    clear=args.force,
                    symlinks=v.getboolean("symlinks"),
                    with_pip=True,  # Required to install packages via pip
                    prompt=v.get("prompt", None),
                    upgrade_deps=False)
        if "pip_install" in v:
            output(f'Installing via pip: {v["pip_install"]}')
            # Update pip to avoid warnings of it being out of date
            rc = subprocess.run(f'source {path}/bin/activate'
                                f' && {PIP} install --upgrade pip'
                                f' && {PIP} install {v["pip_install"]}',
                                shell=True).returncode
            if rc:
                error_detected = 1
                continue
        if "shellcmd" in v:
            output(f'Executing shell cmd: {v["shellcmd"]}')
            rc = subprocess.run(f'source {path}/bin/activate'
                                f' && {v["shellcmd"]}',
                                shell=True).returncode
            if rc:
                error_detected = 1
                continue
    return 1 if error_detected else 0


def do_update(args, config):
    """Update virtualenvs"""
    error_detected = 0
    output("Updating virtualenvs...")
    sections = args.venvs or config.sections()
    for s in sections:
        try:
            v = config[s]
        except KeyError:
            error(f"Unknown virtualenv {s}")
            error_detected = 1
            continue
        if "skip" in v:
            rc = subprocess.run(v["skip"]).returncode
            if not rc:
                output("Skipping...")
                continue
        path = get_path(s, config)
        if not os.path.exists(os.path.expanduser(path)):
            output(f"Virtualenv {s} does not exist ({path})")
            error_detected = 1
            continue
        output(f"Updating virtualenv {s} at {path}")
        # Kudos: https://stackoverflow.com/a/3452888/197789
        rc = subprocess.run(f'source {path}/bin/activate'
                            f' && {PIP} install --upgrade pip'
                            " && pip list --outdated --format=freeze |"
                            " grep -v '^\\-e' | cut -d = -f 1  |"
                            " xargs -n1 pip install -U",
                            shell=True).returncode
        if rc:
            error_detected = 1
            continue
    return 1 if error_detected else 0


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
    parser.add_argument("-c", "--conf_file",
                        default="~/.virtualenvs.conf",
                        help="Specify config file", metavar="FILE")
    parser.add_argument("-f", "--force", action='store_true',
                        default=False, help="Force action")

    subparsers = parser.add_subparsers(help='sub-command help')

    # create the parser for the "create" command
    parser_create = subparsers.add_parser('create', help=do_create.__doc__)
    parser_create.set_defaults(func=do_create)
    parser_create.add_argument('venvs', nargs='*',
                               help='Virtualenvs to create')

    # create the parser for the "update" command
    parser_update = subparsers.add_parser('update', help=do_update.__doc__)
    parser_update.set_defaults(func=do_update)
    parser_update.add_argument('venvs', nargs='*',
                               help='Specify virtualenvs to update')

    args = parser.parse_args()
    print(args)  # DEBUG

    config = configparser.ConfigParser()
    # Explicity open file so we throw exception if it doesn't exist
    with open(os.path.expanduser(args.conf_file), "r") as f:
        config.read_file(f)

    try:
        func = args.func
    except AttributeError:
        parser.print_help()
        sys.exit(1)
    status = func(args, config)
    return status


if __name__ == "__main__":
    sys.exit(main())
