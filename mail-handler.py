#!/usr/bin/env python3
# Parse mail from commandline or template and send via Mail App

import sys
import argparse
import datetime
import os.path
import re
from subprocess import Popen, PIPE


def escape(s):
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    return s


def substitute(s):
    """Make substitutions in string and return it.

    Substitutions as per format() with following keys:

    {today} - a datetime.date object for today. Which can have format
    modifiers as per the following. E.g. {date:%A} -> "Sunday"
    See https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior  #noqa
    Similarly: {tomorrow} {dayaftertomorrow}

    Example:
    Today is {today:%A}. Tomorrow is {tomorrow:%A}.
    And the day after is {dayaftertomorrow:%A}.
    """
    if s is None:
        return None
    day = datetime.timedelta(days=1)
    today = datetime.date.today()
    d = {
        "today": today,
        "tomorrow": today + day,
        "dayaftertomorrow": today + 2*day,
        }
    return s.format(**d)


def make_parser():
    """Return arparse.ArgumentParser instance"""
    parser = argparse.ArgumentParser(description="Create a new mail message")
    parser.add_argument('recipient', metavar="to-addr", nargs="*",
                        default=None, help="message recipient(s)")
    parser.add_argument('-s', '--subject', metavar="subject",
                        default=None, help="message subject")
    parser.add_argument('-c', '--cc', metavar="addr", nargs="+",
                        default=None, help="carbon copy recipient(s)")
    parser.add_argument('-b', '--bcc', metavar="addr", nargs="+",
                        default=None, help="blind carbon copy recipient(s)")
    parser.add_argument('-f', '--from', dest="from_addr",
                        default=None, metavar="addr", help="from address")
    parser.add_argument('-a', '--attach', metavar="file", nargs="+",
                        default=None, help="attachment(s)")
    parser.add_argument('--input', default=None, metavar="filename",
                        help="Input filename ('-' for stdin)")
    parser.add_argument('--mailapp', default="applemail",
                        metavar="application", help="Mail application")
    parser.add_argument('--send', action="store_true", default=False,
                        help="Send the message")
    return parser


def parse_content_fd(fd):
    """Parse message from given descriptor"""
    message = {}
    for line in iter(fd.readline, ''):
        # XXX This fails strangely if there is no value
        result = re.match("(\w+): (.*)", line)
        if not result:
            # Assume past headers
            break
        header = result.group(1).lower()
        value = result.group(2)
        if header == "to":
            message["to_addr"] = [a.strip() for a in value.split(",")]
        elif header == "subject":
            message["subject"] = value
        elif header == "from":
            message["from_addr"] = value
        elif header == "cc":
            message["cc_addr"] = [a.strip() for a in value.split(",")]
        elif header == "bcc":
            message["bcc_addr"] = [a.strip() for a in value.split(",")]
        elif header == "attach":
            message["attach"] = value

    content = fd.read()
    if content:
        message["content"] = content
    return message


# Use Apple Mail to send email
# by Nathan Grigg http://nb.nathanamy.org
# From https://gist.github.com/nathangrigg/2475544
def applemail_handler(message, send=False):
    """Uses applescript to create a mail message with the given attributes"""

    if send:
        properties = ["visible:false"]
    else:
        properties = ["visible:true"]
    if message["subject"]:
        properties.append('subject:"%s"' % escape(message["subject"]))
    if message["from_addr"]:
        properties.append('sender:"%s"' % escape(message["from_addr"]))
    if message["content"] and len(message["content"]) > 0:
        properties.append('content:"%s"' % escape(message["content"]))
    properties_string = ",".join(properties)

    template = 'make new %s with properties {%s:"%s"}'
    make_new = []
    if message["to_addr"]:
        make_new.extend([template % ("to recipient", "address", escape(addr))
                         for addr in message["to_addr"]])
    if message["cc_addr"]:
        make_new.extend([template % ("cc recipient", "address", escape(addr))
                         for addr in message["cc_addr"]])
    if message["bcc_addr"]:
        make_new.extend([template % ("bcc recipient", "address", escape(addr))
                         for addr in message["bcc_addr"]])
    if message["attach"]:
        make_new.extend([
            template % (
                "attachment", "file name",
                escape(os.path.abspath(f))) for f in message["attach"]])
    if send:
        make_new.append('send')
    if len(make_new) > 0:
        make_new_string = "".join(["tell result\n",
                                   "\n".join(make_new),
                                   "\nend tell\n"])
    else:
        make_new_string = ""

    script = """tell application "Mail"
    make new outgoing message with properties {%s}
    %s end tell
    """ % (properties_string, make_new_string)

    # run applescript
    p = Popen(['/usr/bin/osascript'], stdin=PIPE, stdout=PIPE)
    p.communicate(script.encode("utf8"))
    return p.returncode


# Use Outlook to send email
# Kudos:
#   https://gist.github.com/gourneau/5946401
#   https://apple.stackexchange.com/a/360677/104604
#   https://stackoverflow.com/a/39782325/197789
def outlook_handler(message, send=False):
    """Uses applescript to create a mail message with the given attributes"""

    properties = []
    if message["subject"]:
        properties.append('subject:"%s"' % escape(message["subject"]))
    if message["from_addr"]:
        properties.append('sender:"%s"' % escape(message["from_addr"]))
    if message["content"] and len(message["content"]) > 0:
        properties.append(
            'plain text content:"%s"' % escape(message["content"]))
    properties_string = ",".join(properties)

    emailaddr_template = 'make new %s at newMessage with properties {%s:%s}'
    template = 'make new %s at newMessage with properties {%s:"%s"}'
    def email_to_str(e): return "{address:\"%s\"}" % escape(e)
    make_new = []
    if message["to_addr"]:
        make_new.extend([emailaddr_template % ("to recipient",
                                               "email address",
                                               email_to_str(addr))
                         for addr in message["to_addr"]])
    if message["cc_addr"]:
        make_new.extend([emailaddr_template % ("cc recipient",
                                               "email address",
                                               email_to_str(addr))
                         for addr in message["cc_addr"]])
    if message["bcc_addr"]:
        make_new.extend([emailaddr_template % ("bcc recipient",
                                               "email address",
                                               email_to_str(addr))
                         for addr in message["bcc_addr"]])
    if message["attach"]:
        make_new.extend([template % (
            "attachment",
            "file",
            escape(os.path.abspath(f))) for f in message["attach"]])
    if send:
        make_new.append('send newMessage')
    else:
        make_new.append('open newMessage')
    if len(make_new) > 0:
        make_new_string = "\n".join(make_new)
        # make_new_string = "open newMessage"
    else:
        make_new_string = ""

    script = """tell application "Microsoft Outlook"
    set newMessage to make new outgoing message with properties {%s}
    %s
    end tell
    """ % (properties_string, make_new_string)

    # run applescript
    p = Popen(['/usr/bin/osascript'], stdin=PIPE, stdout=PIPE)
    p.communicate(script.encode("utf8"))
    return p.returncode


def stdout_handler(message, send=False):
    """Print mail message to stdout, probably for debugging"""

    if message["from_addr"]:
        print("From: " + message["from_addr"])
    if message["to_addr"]:
        print("To: " + ",".join(message["to_addr"]))
    if message["cc_addr"]:
        print("CC: " + ",".join(message["to_addr"]))
    if message["bcc_addr"]:
        print("BCC: " + ",".join(message["to_addr"]))
    if message["subject"]:
        print("Subject: " + message["subject"])
    if message["attach"]:
        for attachment in message["attach"]:
            print("Attachment: " + attachment)
    if message["send"]:
        print("Send: True")
    if message["content"]:
        print("\n" + message["content"])


mailapp_handler = {
    "applemail": applemail_handler,
    "outlook": outlook_handler,
    "text": stdout_handler
}


def main(argv=None):
    message = {
        "subject": None,
        "to_addr": None,
        "from_addr": None,
        "cc_addr": None,
        "bcc_addr": None,
        "attach": None,
        "content": None,
        "send": False
        }
    parser = make_parser()
    args = parser.parse_args(argv if argv else sys.argv[1:])
    if args.input:
        if args.input == "-":
            fd = sys.stdin
        else:
            fd = open(args.input, "r")
        message.update(parse_content_fd(fd))

    # Update message from args
    message["subject"] = args.subject \
        if args.subject else message["subject"]
    message["to_addr"] = args.recipient \
        if args.recipient else message["to_addr"]
    message["from_addr"] = args.from_addr \
        if args.from_addr else message["from_addr"]
    message["send"] = args.send \
        if args.send else message["send"]
    message["cc_addr"] = args.cc \
        if args.cc else message["cc_addr"]
    message["bcc_addr"] = args.bcc \
        if args.bcc else message["bcc_addr"]
    message["attach"] = args.attach \
        if args.attach else message["attach"]

    # Perform substitions on subject and content
    message["subject"] = substitute(message["subject"])
    message["content"] = substitute(message["content"])

    try:
        handler = mailapp_handler[args.mailapp]
    except KeyError:
        parser.error("Unrecognized Mail App: " + args.mailapp)
        sys.exit(1)
    code = handler(message, send=args.send)
    sys.exit(code)


if __name__ == "__main__":
    sys.exit(main())
