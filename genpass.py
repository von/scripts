#!/usr/bin/env python3
"""Generate passwords or pass phrases"""

import argparse
import itertools
import os.path
import random
import string
import subprocess
import sys

# Output functions
output = print
debug = print


def null_output(*args, **kwargs):
    pass

######################################################################
#
# Functions to generate different types of passwords/passs phrases
#


def pass_word(args):
    """Generate a password."""
    if args.charset:
        alphabet = alphabets[args.charset]
    else:
        alphabet = string.ascii_letters + string.digits
    if not args.lookalikes:
        alphabet = alphabet.translate(
            str.maketrans(
                # No conversions
                '', '',
                # Characters to delete
                '0O1l'
            ))
    debug("Length is {}".format(args.length))
    s = "".join([random.choice(alphabet) for i in range(args.length)])
    return s


def pass_device(args):
    """Generate a simple password suitable for entering on a device."""
    if args.charset:
        alphabet = alphabets[args.charset]
    else:
        alphabet = string.ascii_lowercase + string.digits
    if not args.lookalikes:
        alphabet = alphabet.translate(
            str.maketrans(
                # No conversions
                '', '',
                # Characters to delete
                '0O1l'
            ))
    debug("Length is {}".format(args.length))
    s = "".join([random.choice(alphabet) for i in range(args.length)])
    return s


def pass_phrase(args):
    """Generate a pass phrase."""
    words = None
    if args.dict:
        # Use user-specified file
        dict = os.path.expanduser(args.dict)
        debug("Reading user-specified dictionary {}".format(dict))
        with open(dict) as f:
            words = f.readlines()
    else:
        # Search standard places
        for dict in words_files:
            try:
                with open(dict) as f:
                    words = f.readlines()
                debug("Reading dictionary {}".format(dict))
            except FileNotFoundError:
                continue
        if not words:
            raise FileNotFoundError("No dictionary file found.")
    debug("Length is {}".format(args.length))
    # Create lists of random words and random separators
    words = [random.choice(words).strip() for i in range(args.length)]
    if args.capitalize:
        words = [str.capitalize(word) for word in words]
    sep = [random.choice(separators[args.separator])
           for i in range(args.length)]
    # Create list of (word, sep) tuples then chain those lists into a string
    # Kudos: http://stackoverflow.com/a/2017923/197789
    # The strip() handles trailing whitespace if separatores are spaces
    s = "".join(itertools.chain(*zip(words, sep))).strip()
    return s


def pass_pin(args):
    """Generate a pin."""
    alphabet = string.digits
    length = args.length
    debug("Length is {}".format(length))
    s = "".join([random.choice(alphabet) for i in range(length)])
    return s

######################################################################
#
# Password output functions
#


def output_stdout(s, args):
    """Output to stdout"""
    print(s)
    return(0)


def output_clipboard(s, args):
    """Output to paste buffer"""
    output("Putting passphrase/word into paste buffer...")
    if sys.platform == "darwin":
        prog = "pbcopy"
    else:
        prog = "xclip -in -verbose -selection clipboard"
    debug("Invoking {}".format(prog))
    p = subprocess.Popen([prog], stdin=subprocess.PIPE)
    p.communicate(s.encode('utf8'))
    status_code = p.wait()
    if status_code > 0:
        output("Putting password to clipboard failed.")
        return(1)
    return(0)


######################################################################

# Alphabets used by pass_word
alphabets = {
    "alphanum": string.ascii_letters + string.digits,
    "loweralphanum": string.ascii_lowercase + string.digits,
    "alphanumpunct": string.ascii_letters + string.digits + string.punctuation,
    }

algorithms = {
    "word": pass_word,
    "phrase": pass_phrase,
    "device": pass_device,
    "pin": pass_pin,
    }

# Separators for pass phases
separators = {
    "spaces": [" "],
    "nums": [str(i) for i in range(100)],
}

# Places to look for words files
# Used by pass_phrase
words_files = [
    "/usr/share/dict/words",
    "/usr/dict/words"
]

######################################################################


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

    # Generate password by default
    # Set all defaults in case subcommand not given, which is not an
    # error in Python 3.3+
    parser.set_defaults(
        function=pass_word,
        charset="alphanum",
        length=12,
        lookalikes=False,
        out_function=output_clipboard)
    subparsers = parser.add_subparsers()

    # Only allow one of debug/quiet mode
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "-d", "--debug",
        action='store_true', default=False,
        help="Turn on debugging")
    verbosity_group.add_argument(
        "-q", "--quiet",
        action="store_true", default=False,
        help="run quietly")

    parser.add_argument(
        "-S", "--stdout",
        action='store_const', const=output_stdout,
        dest='out_function',
        help="Write password to STDOUT")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")

    parser_word = subparsers.add_parser('word')
    parser_word.set_defaults(function=pass_word)
    parser_word.add_argument(
        "-c", "--charset",
        default="alphanum",
        help="Specify character set for passwords",
        choices=alphabets.keys())
    parser_word.add_argument(
        "-l", "--length",
        type=int, default=12,
        help="Specify password length (default=12)", metavar="LEN")
    parser_word.add_argument(
        "-L", "--lookalikes",
        action="store_true", default=False,
        help="Allow look-alike characters (0, O, 1, l, etc.)")

    parser_device = subparsers.add_parser('device')
    parser_device.set_defaults(function=pass_device)
    parser_device.add_argument(
        "-c", "--charset",
        default="loweralphanum",
        help="Specify character set for passwords",
        choices=alphabets.keys())
    parser_device.add_argument(
        "-l", "--length",
        type=int, default=8,
        help="Specify password length (default=8)", metavar="LEN")
    parser_device.add_argument(
        "-L", "--lookalikes",
        action="store_true", default=False,
        help="Allow look-alike characters (0, O, 1, l, etc.)")

    parser_pin = subparsers.add_parser('pin')
    parser_pin.set_defaults(function=pass_pin)
    parser_pin.add_argument(
        "-l", "--length",
        type=int, default=8,
        help="Specify password length (default=8)", metavar="LEN")

    parser_phrase = subparsers.add_parser('phrase')
    parser_phrase.set_defaults(function=pass_phrase)
    parser_phrase.add_argument(
        "-c", "--capitalize",
        action="store_true",
        default=False,
        help="Capitalize words in pass phrase")
    parser_phrase.add_argument(
        "-D", "--dict",
        default=os.getenv("WORDS_FILE"),
        help="Specify dictionary file to use for pass phrases",
        metavar="PATH")
    parser_phrase.add_argument(
        "-l", "--length",
        type=int, default=6,
        help="Specify passphrase length (default=6)", metavar="LEN")
    parser_phrase.add_argument(
        "-s", "--separator",
        default="spaces",
        help="Specify separator for pass phrase",
        choices=separators.keys())

    args = parser.parse_args()

    global output
    output = print if not args.quiet else null_output
    global debug
    debug = print if args.debug else null_output

    debug("Calling random.seed()")
    random.seed()

    try:
        debug("Invoking {}".format(str(args.function)))
        pass_str = args.function(args)
        debug("Returned from {}".format(str(args.function)))
    except Exception as e:
        print("Failed:" + str(e))
        if args.debug:
            raise e
        return(1)

    try:
        debug("Invoking {}".format(str(args.out_function)))
        args.out_function(pass_str, args)
        debug("Returned from {}".format(str(args.out_function)))
    except Exception as e:
        print("Failed:" + str(e))
        if args.debug:
            raise e
        return(1)

    return(0)


if __name__ == "__main__":
    sys.exit(main())
