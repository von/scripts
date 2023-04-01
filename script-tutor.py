#!/usr/bin/env python3
"""script-tutor: Help me learn my lines in a script

A script is a text file that looks like the following (indentation
for readability):

    Scripts use blank lines to delimit paragraphs. Paragraphs without special
    formatting, like this one, are considered stage direction and just printed.

    # Paragraphs starting with a hash characters are treated as comments
    # and ignored.

    # A character name followed by a "->" sets the voice name for the
    # character. See '-v' option for say(1) for more information on voice
    # names.

    Alice -> Karen

    Bob -> Ralph

    Eve -> Kathy

    # Lines with a character name followed by a colon are treated as lines
    # to be read by that character. Note that the '-m <character>' option
    # can be used to mute a character (so their lines may be practiced).

    Alice: Bob, I have a secret to tell you.

    Bob: Go ahead.

    Eve walks in from stage right.

    # Indentation on lines is ignored.

    Eve: Not so fast, I'm going to listen in! Ha! Ha! Ha!
        It's all part of my master plan.

    Bob hands Alice a piece of paper.

    Bob: Alice, here is my public key.

    Eve: Curses, foiled again.

    Eve exits stage right.
"""
# Kudos: https://infoheap.com/convert-text-to-speech-on-mac-using-utility-say/
# See also:
#   https://support.apple.com/guide/mac-help/change-the-voice-your-mac-uses-to-speak-text-mchlp2290/mac

import argparse
import re
import subprocess
import sys


class Character:

    # Commandline utility
    say_cmd = "say"

    characters = {}

    def __init__(self, name):
        self.name = name
        self.characters[name] = self
        self.voice = None
        self.muted = False

    def __str__(self):
        return self.name

    def set_voice(self, voice_name):
        """Set the voice to use for this character

        Must be one of the voices returned by 'say -v \\?'"""
        self.voice = voice_name

    def mute(self):
        """Mute character so it does not speak"""
        self.muted = True

    def say(self, line):
        print()
        if self.muted:
            print(self.name + "[MUTED]: ")
            print(line)
            return
        print(self.name + ": ")
        try:
            args = [self.say_cmd, "-i"]
            if self.voice:
                args.extend(["-v", self.voice])
            args.append(line)
            subprocess.run(args, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to run \"{self.say_cmd}\":"
                  f" {e.stderr} (rc={e.returncode}")

    @classmethod
    def get(cls, name, create=True):
        try:
            return cls.characters[name]
        except KeyError:
            if create:
                return Character(name)
            else:
                return None


class Script:

    empty_line_regex = re.compile("\\s*")
    line_regex = re.compile("(\\w+):\\s*(.*)")
    voice_regex = re.compile("(\\w+)\\s*->\\s*(.*)")
    comment_regex = re.compile("\\s*#.*")

    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename)

    def __del__(self):
        if self.file:
            self.file.close()

    def read_paragraph(self):
        """Return next blank-line delimited paragraph from the script"""
        # Read any empty lines until we hit a paragraph
        line = self.file.readline()
        while line and self.empty_line_regex.fullmatch(line):
            line = self.file.readline()
        if not line:
            # EOF
            return None
        paragraph = line.strip()
        # Read and add to paragraph until we hit an empty line
        line = self.file.readline()
        while not self.empty_line_regex.fullmatch(line):
            paragraph += " " + line.strip()
            line = self.file.readline()
        return paragraph

    def read(self, pause=True):
        """Read the script.

        If pause is True, wait for keypress between lines."""
        while paragraph := self.read_paragraph():
            if self.comment_regex.fullmatch(paragraph):
                continue
            elif match := self.line_regex.fullmatch(paragraph):
                character = Character.get(match.group(1))
                line = match.group(2)
                character.say(line)
                if pause:
                    input("Press return to continue...")
            elif match := self.voice_regex.fullmatch(paragraph):
                character = Character.get(match.group(1))
                voice = match.group(2)
                character.set_voice(voice)
            else:
                # Assume stage direction
                print()
                print(paragraph)


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

    parser.add_argument("-m", "--mute", metavar="character",
                        action='store', type=str, default=None,
                        help="Mute character")
    parser.add_argument("-p", "--pause",
                        action='store_true', default=True,
                        help="Pause between lines for keypress")
    parser.add_argument("-P", "--nopause",
                        action='store_false', dest="pause",
                        help="Do not pause between lines for keypress")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    parser.add_argument("script", metavar="script", type=str, nargs=1,
                        help="Script file to read")
    return parser


def main(argv=None):
    parser = make_argparser()
    args = parser.parse_args(argv if argv else sys.argv[1:])

    if args.mute:
        c = Character.get(args.mute)
        c.mute()

    script = Script(args.script[0])
    script.read(pause=args.pause)
    return(0)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)
