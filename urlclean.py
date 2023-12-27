#!/usr/bin/env python3
""" Clean up a URL

This script docstring serves as a usage message (with -h).

Kudos: http://www.artima.com/weblogs/viewpost.jsp?thread=4829

Modified to use argparse (new in 2.7) instead of getopt.
"""

import argparse
import fileinput
import subprocess
import sys
import urllib.request
import urllib.parse
import urllib.error
import urllib.parse
import webbrowser

# Allow building list of cleanup functions to call using descorator
cleanup_functions = []


def url_cleanup_function(function):
    """Decorator to make a function a URL clean up function to call."""
    cleanup_functions.append(function)
    return function


@url_cleanup_function
def clean_google_redirect(urlstring):
    """Clean up a Google redirect from search or calendar

    Google search result:
        https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=4&ved=0ahUKEwjex5Om3_nQAhXGqVQKHUiHDIoQFggoMAM&url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2F%2522Hello%2C_World!%2522_program&usg=AFQjCNGfl-sRw62JgahA16FJaZSX9L7oCg&bvm=bv.142059868,d.eWE
    Converts to:
        https://en.wikipedia.org/wiki/%22Hello,_World!%22_program

    Calendar URLs are similar but use 'q' instead of 'url'
    """

    parsed_url = urllib.parse.urlparse(urlstring)
    if parsed_url.netloc == "www.google.com" and \
            parsed_url.path == "/url" and \
            parsed_url.query:
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if "url" in query_params:
            return query_params["url"][0]
        elif "q" in query_params:
            return query_params["q"][0]
    return None


@url_cleanup_function
def remove_google_docs_heading(urlstring):
    """Remove headings from Google docs urls

    Google docs with heading:
        https://docs.google.com/document/d/1YLZzQbY__0HSEDZ6UWO8KgaULu2R1gv0jGI6XWWSh6w/edit#heading=h.6puqf6utazmp
    Coverts to:
        https://docs.google.com/document/d/1YLZzQbY__0HSEDZ6UWO8KgaULu2R1gv0jGI6XWWSh6w/edit
    """
    parsed_url = urllib.parse.urlparse(urlstring)
    if parsed_url.netloc == "docs.google.com" and \
            parsed_url.path.startswith("/document/") and \
            parsed_url.fragment and \
            parsed_url.fragment.startswith("heading="):
        return(parsed_url._replace(fragment="").geturl())
    return None


@url_cleanup_function
def utm_cleaner(urlstring):
    """Clean UTM fields out of query

    For URLs in email tracking campaigns.

    Woodsmith email tracking URL:
        http://www.woodsmithtips.com/2016/12/15/our-favorite-shop-materials/?utm_source=WoodsmithTips&utm_medium=email&utm_campaign=11806
    Converts to:
        http://www.woodsmithtips.com/2016/12/15/our-favorite-shop-materials/
    """
    parsed_url = urllib.parse.urlparse(urlstring)
    if not parsed_url.query:
        return None
    query_params = urllib.parse.parse_qs(parsed_url.query)
    # Remove elements from dict
    # kudos: http://stackoverflow.com/a/11277439/197789
    query_params.pop("utm_source", None)
    query_params.pop("utm_medium", None)
    query_params.pop("utm_campaign", None)
    query = urllib.parse.urlencode(query_params, doseq=True)
    # Create modified parsed_url using _replace()
    # Kudos: http://stackoverflow.com/a/24201020/197789
    return(parsed_url._replace(query=query).geturl())


@url_cleanup_function
def misc_query_cleaner(urlstring):
    """Clean misc fields out of query

    For URLs in email tracking campaigns.

    Woodsmith email tracking URL:
        https://www.aip.org/fyi/2016/congress-passes-national-defense-authorization-act?dm_i=%5B%271ZJN%2C4OZJ0%2CE29EEG%2CHJY6C%2C1%27%5D
    Converts to:
        https://www.aip.org/fyi/2016/congress-passes-national-defense-authorization-act
    """
    parsed_url = urllib.parse.urlparse(urlstring)
    if not parsed_url.query:
        return None
    query_params = urllib.parse.parse_qs(parsed_url.query)
    # Remove elements from dict
    # kudos: http://stackoverflow.com/a/11277439/197789
    query_params.pop("dm_i", None)
    query = urllib.parse.urlencode(query_params, doseq=True)
    # Create modified parsed_url using _replace()
    # Kudos: http://stackoverflow.com/a/24201020/197789
    return(parsed_url._replace(query=query).geturl())


def get_clipboard():
    """Return contents of clipboard"""
    p = subprocess.Popen(["pbpaste"],
                         stdout=subprocess.PIPE,
                         close_fds=True)
    return p.stdout.read().decode('utf8')


def set_clipboard(value):
    """Set contents of clipboard"""
    p = subprocess.Popen(["pbcopy"],
                         stdin=subprocess.PIPE,
                         close_fds=True)
    p.stdin.write(value.encode('utf8'))


def parse_url(urlstring):
    """Parse URL and print it

    Meant for debugging."""
    print(urlstring)
    parsed_url = urllib.parse.urlparse(urlstring)
    for attr in ["scheme", "netloc", "path",
                 "params", "fragment", "username",
                 "password", "hostname", "port"]:
        val = getattr(parsed_url, attr)
        if not val:
            continue
        print("{}: {}".format(attr, val))

    if parsed_url.query:
        query_params = urllib.parse.parse_qs(parsed_url.query)
        print(query_params)

    return(0)


def process_url(urlstring):
    global cleanup_functions
    try:
        urllib.parse.urlparse(urlstring)
    except ValueError:
        # Best I can tell, this is the only exception type possible
        print("Bad url: {}".format(urlstring))
        return(1)
    for func in cleanup_functions:
        result = func(urlstring)
        if result is None:
            continue
        urlstring = result
    return urlstring


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
    parser.set_defaults(
        output_func=print,
        readclipboard=False
        )
    parser.add_argument("-c", "--clipboard",
                        action="store_const",
                        dest="output_func",
                        const=set_clipboard,
                        help="Put resulting URL in clipboard")
    parser.add_argument("-C", "--readclipboard",
                        action="store_true",
                        dest="readclipboard",
                        help="Read URL from clipboard")
    parser.add_argument("-o", "--open",
                        action="store_const",
                        dest="output_func",
                        const=webbrowser.open,
                        help="Open resulting URL in browser")
    parser.add_argument("-p", "--parse",
                        action="store_true", default=False,
                        help="Print parsed URL")
    parser.add_argument("-P", "--print",
                        action="store_const",
                        dest="output_func",
                        const=print,
                        help="Print resulting URL")
    parser.add_argument('url', metavar='url', type=str, nargs="*",
                        help='url to parse')
    args = parser.parse_args()

    if args.readclipboard:
        url = get_clipboard()
        if not url:
            print("Failed to read url from clipboard.", file=sys.stderr)
            return(1)
        args.url.append(url)
    elif not args.url:
        # No URL given on commandline, read from stdin
        url = "".join([line.rstrip() for line in fileinput.input()])
        if not url:
            print("Failed to read url from stdin.", file=sys.stderr)
            return(1)
        args.url.append(url)

    if args.parse:
        return(parse_url(args.url[0]))
    url = process_url(args.url[0])
    args.output_func(url)
    return(0)


if __name__ == "__main__":
    sys.exit(main())
