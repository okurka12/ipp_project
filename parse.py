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
import pdb

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
ERR_MISSING_HEADER = 21
ERR_INVALID_OPCODE = 22

SIGNATURES = {
    "MOVE": ["var", "symb"],
    "CREATEFRAME": [],
    "PUSHFRAME": [],
    "POPFRAME": [],
    "DEFVAR": ["var"],
    "CALL": ["label"],
    "RETURN": [],
    "PUSHS": ["symb"],
    "POPS": ["var"],
    "ADD": ["var", "symb", "symb"],
    "SUB": ["var", "symb", "symb"],
    "MUL": ["var", "symb", "symb"],
    "IDIV": ["var", "symb", "symb"],
    "LT": ["var", "symb", "symb"],
    "GT": ["var", "symb", "symb"],
    "EQ": ["var", "symb", "symb"],
    "AND": ["var", "symb", "symb"],
    "OR": ["var", "symb", "symb"],
    "NOT": ["var", "symb", "symb"],
    "INT2CHAR": ["var", "symb"],
    "STR2INT": ["var", "symb", "symb"],
    "READ": ["var", "type"],
    "WRITE": ["symb"],
    "CONCAT": ["var", "symb", "symb"],
    "STRLEN": ["var", "symb"],
    "GETCHAR": ["var", "symb", "symb"],
    "SETCHAR": ["var", "symb", "symb"],
    "TYPE": ["var", "symb"],
    "LABEL": ["label"],
    "JUMP": ["label"],
    "JUMPIFEQ": ["label", "symb", "symb"],
    "JUMPIFNEQ": ["label", "symb", "symb"],
    "EXIT": ["symb"],
    "DPRINT": ["symb"],
    "BREAK": []
}


# class OpType(Enum):
#     """operand type"""

#     VAR = enum_auto()
#     SYMB = enum_auto()
#     LABEL = enum_auto()
#     TYPE = enum_auto()


class Operand:
    def __init__(self, operand_type: str, value: str) -> None:
        self.type = operand_type
        self.value = value





# IPPcode24 instructions
class Instruction:
    def __init__(self, opcode: str, *operands) -> None:
        if opcode.upper() not in SIGNATURES:
            perr(f"Invalid opcode: '{opcode}'")
            sys.exit()

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
        sys.exit(0)


def load_stdin() -> str:
    """loads the whole standard input"""
    content = ""

    while True:
        try:
            content += input()
            content += "\n"
        except EOFError:
            break

    return content


def parse_input(pgr: str) -> list[Instruction]:
    """parses the program to return a list of instructions"""
    instructions = []



def preprocess(pgr: str) -> str:
    """strips comments and blank lines"""

    # finite state machine state: 0 - init, 1 - comment
    state = 0

    output = ""

    # finite state machine
    for letter in pgr:
        if state == 0:
            if letter == "#":
                state = 1
            else:
                output += letter
        else:
            if letter == "\n":
                output += "\n"
                state = 0

    # remove blank lines
    lines = output.splitlines()
    no_blank_lines = [
        line for line in lines if not line.isspace() and len(line) > 0
    ]
    no_blank_lines = "\n".join(no_blank_lines)

    return no_blank_lines


def header_present(pgr: str) -> bool:
    """returns if .IPPcode24 is present in the first line"""

    if len(pgr.splitlines()) == 0:
        sys.exit(ERR_MISSING_HEADER)

    first_line = pgr.splitlines()[0]
    first_line = first_line.strip()
    first_line = first_line.upper()
    return ".IPPCODE24" == first_line



def main():
    check_args()

    # whole program from the input
    pgr_in = load_stdin()

    processed = preprocess(pgr_in)

    if not header_present(processed):
        perr("Missing header .IPPcode24")
        sys.exit(ERR_MISSING_HEADER)

    # print(processed)
    print("parse.py: all ok", file=sys.stderr)

if __name__ == "__main__":
    main()
