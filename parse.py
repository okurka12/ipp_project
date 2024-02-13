##################
##  Vit Pavlik  ##
##   xpavli0a   ##
##    251301    ##
##              ##
##  Created:    ##
##  2024-02-18  ##
##              ##
##  Edited:     ##
##  2024-02-13  ##
##################
import sys
import os
from enum import Enum
from enum import auto as enum_auto
import pdb
import re

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

# error codes below

# wrong parameters for parse.py
ERR_WRONG_PARAMETERS = 10

# missing .ippcode24 header
ERR_MISSING_HEADER = 21

# invalid or unknown opcode
ERR_INVALID_OPCODE = 22

# other lexical or syntactical error
ERR_OTHER_LEXSYN = 23

# dont change these
NONE = 4
ERROR = 3
WARNING = 2
INFO = 1
DEBUG = 0

# chosen log level (choose from the above)
LOG_LEVEL = DEBUG

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


class Operand:
    def __init__(self, operand_type: str, value: str) -> None:
        """
        `operand_type` - int, bool, string, nil, label, type, var
        `value` - text, literal, frame@identifier
        """
        self.type = operand_type
        self.value = value

    def __repr__(self) -> str:
        return f"{self.value} ({self.type})"

    def is_constant(self) -> bool:
        return self.type in ["int", "bool", "string", "nil"]

    def is_symb(self) -> bool:
        """symb - constant or a variable"""
        return self.is_constant() or self.type == "var"

    def is_label(self) -> bool:
        return self.type == "label"

    def is_var(self) -> bool:
        return self.type == "var"

    def is_type(self) -> bool:
        return self.type == "type"


# IPPcode24 instructions
class Instruction:
    def __init__(self, opcode: str, operands: list[Operand]) -> None:
        self.opcode = opcode
        self.operands = operands

    def __repr__(self) -> str:
        operands = ""
        for op in self.operands:
            operands += str(op) + ", "
        operands = operands.rstrip(", ")

        return f"{self.opcode} {operands}"

    # def op_iter(self) -> Operand:
    def op_iter(self):
        """iterator for instruction's operands/arguments (class Operand)"""
        for op in self.operands:
            yield op


class Element:
    """A class for an element (an XML tag)"""

    def __init__(self, type: str) -> None:
        self.type = type
        self.attr = {}
        self.children = []
        self.content = ""

    def add_children(self, children: list) -> None:
        """add children in bulk (`childrem` is a list of elements)"""
        self.children.extend(children)

    def add_attribute(self, key: str, value: str) -> None:
        """adds one attribute `key` with a value `value`"""
        self.attr[key] = value

    def set_content(self, content) -> None:
        self.content = content

    def opening(self) -> str:
        """returns element's opening tag"""
        attr_str = ""
        for key, value in self.attr.items():
            attr_str += f"{key}=\"{value}\", "
        attr_str = attr_str.rstrip(", ")
        return f"<{self.type} {attr_str}>"

    def closing(self) -> str:
        return f"</{self.type}>"

    def print_xml(self) -> None:
        """prints XML representation (including children) recursively"""
        print(self.opening())
        for child in self.children:
            child.print_xml()
        if len(self.content) > 0:
            print(self.content)
        print(self.closing())


def perr(*args, **kwargs) -> None:
    """print to stderr, use like `print`"""
    if "file" in kwargs:
        raise RuntimeError("perr should not be called with "
                           "keyword argument \"file\"")
    print(*args, **kwargs, file=sys.stderr)


def log(level: int, *args, **kwargs) -> None:
    """
    log to stderr, level is 0 - 3 (DEBUG, INFO, WARNING, ERROR)
    otherwise, use like print
    """
    level_str = ["DEBUG", "INFO", "WARNING", "ERROR"][level]
    if level >= LOG_LEVEL:
        perr(f"{level_str}:", *args, **kwargs)


def check_args() -> None:
    """
    checks arguments, if there is `--help`, prints help and exits,
    if there are more, prints error and exits
    """

    if len(sys.argv) > 2:
        perr("Too many arguments...")
        perr(USAGE)
        sys.exit(ERR_WRONG_PARAMETERS)

    if len(sys.argv) == 2 and sys.argv[1] != "--help":
        perr(f"invalid argument: '{sys.argv[1]}'")
        perr(USAGE)
        sys.exit(ERR_WRONG_PARAMETERS)

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


# todo: remove??
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


def process_operand(op: str) -> Operand:

    # label, type
    if "@" not in op:
        if op in ["int", "string", "bool"]:
            return Operand("type", op)
        else:
           return Operand("label", op)


    # prefix and value/name
    prefix, *val = op.split("@")
    val = "@".join(val)

    # var
    if prefix.upper() in ["GF", "LF", "TF"]:
        return Operand("var", f"{prefix.upper()}@{val}")

    # int, bool, string, nil,
    elif prefix.lower() in ["int", "bool", "string", "nil"]:
        return Operand(prefix.lower(), val)


def do_match(expected: str, op: Operand) -> bool:
    """
    returns if `op` matches the expected type
    `expected` (var, symb, label, type)
    """
    assert expected in ["var", "symb", "label", "type"]
    return (expected == "var" and op.is_var()) or \
           (expected == "symb" and op.is_symb()) or \
           (expected == "label" and op.is_label()) or \
           (expected == "type" and op.is_type())


def process_line(line:str, instructions: list[Instruction]) -> None:
    """processes line and adds instruction object to `instructions`"""
    tokens = line.split()

    opcode = tokens.pop(0).upper()
    log(DEBUG, f"opcode {opcode}")

    if opcode not in SIGNATURES:
        perr(f"unknown opcode: {opcode}")
        sys.exit(ERR_INVALID_OPCODE)

    # todo: should this even be here????
    # i guess yeah
    # at this point, `tokens` only contains operands
    if len(tokens) != len(SIGNATURES[opcode]):
        perr(f"invalid number of operands:")
        perr(f"    {line}")
        sys.exit(ERR_OTHER_LEXSYN)

    operands: list[Operand] = []
    for i, op_str in enumerate(tokens):
        op_obj = process_operand(op_str)

        # todo: check if this check is appropriate
        expected_type = SIGNATURES[opcode][i]
        if not do_match(expected_type, op_obj):
            perr(f"invalit argument: {op_str}")
            perr(f"    {line}")
            sys.exit(ERR_OTHER_LEXSYN)

        operands.append(op_obj)

    instructions.append(Instruction(opcode, operands))


def generate_element_tree(instructions: list[Instruction]) -> Element:
    prg_el = Element("program")
    prg_el.add_attribute("language", "IPPcode24")
    for i, inst in enumerate(instructions):

        # instruction element
        inst_el = Element("instruction")
        inst_el.add_attribute("order", str(i))
        inst_el.add_attribute("opcode", inst.opcode.upper())

        for j, op in enumerate(inst.op_iter()):
            op_el = Element(f"arg{j + 1}")
            op_el.add_attribute("type", op.type)
            op_el.set_content(op.value)
            inst_el.add_children([op_el])

        prg_el.add_children([inst_el])


    return prg_el


def main():
    check_args()

    # whole program from the input
    pgr_in = load_stdin()

    # remove comments + blank lines
    processed = preprocess(pgr_in)

    # check for header (.IPPcode24)
    if not header_present(processed):
        perr("Missing header .IPPcode24")
        sys.exit(ERR_MISSING_HEADER)

    # parse code line by line to get a list of instruction objects
    instructions = []
    for line in processed.splitlines()[1:]:
        process_line(line, instructions)

    # log processed instructions for debugging purposes
    for instruction in instructions:
        log(DEBUG, instruction)

    # construct element tree from the list of instructions
    prg_el = generate_element_tree(instructions)

    # print xml representation of the element tree
    prg_el.print_xml()


    log(INFO, "parse.py: all ok")
    sys.exit(0)

if __name__ == "__main__":
    main()
