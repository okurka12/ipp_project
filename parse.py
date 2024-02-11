##################
##  Vit Pavlik  ##
##   xpavli0a   ##
##    251301    ##
##              ##
##  Created:    ##
##  2024-02-18  ##
##              ##
##  Edited:     ##
##  2024-02-11  ##
##################
import sys
import os
from enum import Enum
from enum import auto as enum_auto

# filename of this file (without path)
FILE = os.path.basename(__file__)

USAGE = f"USAGE: {FILE} [--help]"

HELP = f"""
{FILE} reads IPPcode24 code from stdin and writes its
XML representation to stdout

ERROR RETURN CODES:
  10 - invalid argument or arguments, invalid combination of arguments
  21 - missing IPPcode24 header
  22 - unknown opcode
  23 - other lexical or syntactical error
"""

# error codes
ERR_WRONG_ARG = 10


class Element:
    """A class for an element (an XML tag)"""

    def __init__(self, type: str) -> None:
        self.type = type
        self.attr = []
        self.children = []
        self.content = ""



def perr(*args, **kwargs) -> None:
    """print to stderr, use like `print`"""
    if "file" in kwargs:
        raise RuntimeError("perr should not be called with "
                           "keyword argument \"file\"")
    print(*args, **kwargs, file=sys.stderr)


def perr_usage() -> None:
    """prints USAGE variable to stderr"""
    perr(USAGE)


def check_args() -> None:
    """
    checks arguments, if there is `--help`, prints help and exits,
    if there are more, prints error and exits
    """

    if len(sys.argv) > 2:
        perr("Too many arguments...")
        perr_usage()
        sys.exit(ERR_WRONG_ARG)

    if len(sys.argv) == 2 and sys.argv[1] != "--help":
        perr(f"invalid argument: '{sys.argv[1]}'")
        perr_usage()
        sys.exit(ERR_WRONG_ARG)

    # sys.argv[1] is "--help"
    if len(sys.argv) == 2:
        print(USAGE)
        print(HELP)


def load_stdin() -> str:
    """loads the whole standard input"""
    content = ""

    while True:
        try:
            content += input()
        except EOFError:
            break

    return content



def main():
    check_args()

    # whole program from the input
    pgr_in = load_stdin()

    pass


if __name__ == "__main__":
    main()