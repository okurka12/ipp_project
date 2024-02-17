##################
##  Vit Pavlik  ##
##   xpavli0a   ##
##    251301    ##
##              ##
##  Created:    ##
##  2024-02-18  ##
##              ##
##  Edited:     ##
##  2024-02-15  ##
##################
import sys
import os
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

XML_HEADER = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"

# error codes below (important: all are prefixed with 'ERR')

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
    "NOT": ["var", "symb"],
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

TYPES = ["int", "bool", "string", "nil"]


class Operand:
    """
    class for an operand for a instruction


    instance attributes:

    `.type` - operand type (label, type, var, int, bool, string, nil)

    `.value` - value
    """
    def __init__(self, op: str, exp: str) -> None:
        """
        Instantiate Operand object from the token string `op` and expected
        operand type `exp` (var, symb, label, type)
        """
        self.type = ""
        self.value = ""
        log(DEBUG, f"instatiating Operand '{op}' ({exp})")

        match exp:
            case "label":
                if not is_valid_identifier(op):
                    perr(f"invalid label: '{op}'")
                    my_exit(ERR_OTHER_LEXSYN)
                self.type = "label"
                self.value = op
            case "var":
                self.instantiate_var(op)
            case "symb":
                self.instantiate_symb(op)
            case "type":
                if op not in TYPES:
                    perr(f"invalid type: '{op}")
                    my_exit(ERR_OTHER_LEXSYN)
                self.type = "type"
                self.value = op

    def instantiate_var(self, op: str) -> None:
        """to be used only by `__init__`"""

        if "@" not in op or len(op.split("@")) != 2:
            perr(f"invalid variable operand: '{op}'")
            my_exit(ERR_OTHER_LEXSYN)

        frame, id = op.split("@")

        if frame not in ["GF", "LF", "TF"]:
            perr(f"invalid variable frame: '{frame}'")
            my_exit(ERR_OTHER_LEXSYN)

        if not is_valid_identifier(id):
            perr(f"invalid variable identifier: '{id}'")
            my_exit(ERR_OTHER_LEXSYN)

        self.type = "var"
        self.value = op

    def instantiate_symb(self, op: str) -> None:
        """to be used only by `__init__`"""

        if "@" not in op:
            perr(f"invalid variable/constant operand: '{op}'")
            my_exit(ERR_OTHER_LEXSYN)

        prefix, *value = op.split("@")
        value = "@".join(value)

        # case: `op` is a variable
        if prefix in ["GF", "LF", "TF"]:
            self.instantiate_var(op)
            return

        if prefix not in TYPES:
            perr(f"invalid data type: '{prefix}'")
            my_exit(ERR_OTHER_LEXSYN)

        value_error_flag = False
        match prefix:
            case "int":
                value_error_flag = not is_valid_integer(value)
                self.type = "int"
                self.value = value
            case "bool":
                value_error_flag = value not in ["true", "false"]
                self.type = "bool"
                self.value = value
            case "string":
                if not is_valid_string(value):
                    perr(f"invalid string: \"{value}\"")
                    my_exit(ERR_OTHER_LEXSYN)
                self.type = "string"
                self.value = value
            case "nil":
                value_error_flag = value != "nil"
                self.type = "nil"
                self.value = value

        if value_error_flag:
            perr(f"invalid value '{value}' for type {prefix}")
            my_exit(ERR_OTHER_LEXSYN)


    def __repr__(self) -> str:
        return f"{self.value} ({self.type})"

    def is_constant(self) -> bool:
        return self.type in TYPES

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
    """
    class for instruction objects

    instance attributes:

    `.opcode` - opcode string

    `.operands` - list of operands (objects of class `Operand`)
    """
    def __init__(self, opcode: str, operands: list[Operand]) -> None:
        self.opcode = opcode
        self.operands = operands

    def __repr__(self) -> str:
        """only for debugging"""
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
    """
    A class for an element (an XML tag)

    instance attributes:

    `.type` - element name (tag)

    `.attr` - tag attributes (dictionary)

    `.children` - list of children elements (objects of class Element)

    `.content` - inner content of the element
    """

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
            attr_str += f"{key}=\"{value}\" "
        attr_str = attr_str.rstrip(" ")
        return f"<{self.type} {attr_str}>"

    def closing(self) -> str:
        """returns element's closing tag"""
        return f"</{self.type}>"

    def print_xml(self) -> None:
        """prints XML representation (including children) recursively"""

        # opening tag
        print(self.opening(), end="")

        # element's content
        if len(self.content) > 0:
            print(xml_safe(self.content), end="")
        else:
            print()

        # child elements
        for child in self.children:
            child.print_xml()

        # closing tag
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
        my_exit(ERR_WRONG_PARAMETERS)

    if len(sys.argv) == 2 and sys.argv[1] != "--help":
        perr(f"invalid argument: '{sys.argv[1]}'")
        perr(USAGE)
        my_exit(ERR_WRONG_PARAMETERS)

    # sys.argv[1] is "--help"
    if len(sys.argv) == 2:
        print(USAGE)
        print(HELP)
        my_exit(0)


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


def xml_safe(unsafe: str) -> str:
    """returns xml safe version of the string"""

    escape_table = {
        '"': "&quot;",
        "'": "&apos;",
        "<": "&lt;",
        ">": "&gt;",
        "&": "&amp;"
    }

    output = ""
    for letter in unsafe:
        if letter in escape_table:
            output += escape_table[letter]
        else:
            output += letter

    return output


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
        my_exit(ERR_MISSING_HEADER)

    first_line = pgr.splitlines()[0]
    first_line = first_line.strip()
    first_line = first_line.upper()
    return ".IPPCODE24" == first_line


# todo: use this fn
def is_valid_string(s: str) -> bool:
    pattern = r"\\\d\d\d"
    backslash_count = s.count("\\")
    pattern_match_count = len(re.findall(pattern, s))
    return backslash_count == pattern_match_count


def is_valid_identifier(id: str) -> bool:
    return re.match(r"[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*", id) is not None


# i actually don't think this check is necessary but it has come to my
# attention that when there are two '.ippcode24' headers we _should_ return
# 23 instead of 22
def is_valid_opcode(op: str) -> bool:
    return op.isalnum()


def is_valid_integer(s: str) -> bool:

    # should not happen
    if len(s) < 1:
        return False

    if "0x" in s:
        p = re.fullmatch(r"\+?0[xX][0-9a-fA-F]+", s) is not None
        m = re.fullmatch(r"\-?0[xX][0-9a-fA-F]+", s) is not None
        return p or m
    elif "0o" in s:
        p = re.fullmatch(r"\+?0[oO][0-7]+", s) is not None
        m = re.fullmatch(r"\-?0[oO][0-7]+", s) is not None
        return p or m
    else:
        p = re.fullmatch(r"\+?[0-9]+", s) is not None
        m = re.fullmatch(r"\-?[0-9]+", s) is not None
        return p or m


def process_line(line:str, instructions: list[Instruction]) -> None:
    """processes line and adds instruction object to `instructions`"""

    log(DEBUG, f"processing line: {line}")
    tokens = line.split()

    opcode = tokens.pop(0).upper()
    log(DEBUG, f"  opcode: {opcode}")

    if not is_valid_opcode(opcode):
        perr(f"invalid opcode: {opcode}")
        my_exit(ERR_OTHER_LEXSYN)

    if opcode not in SIGNATURES:
        perr(f"unknown opcode: {opcode}")
        my_exit(ERR_INVALID_OPCODE)

    # should this even be here???? *thinking*
    # i guess yeah
    # at this point, `tokens` only contains operands
    if len(tokens) != len(SIGNATURES[opcode]):
        perr(f"invalid number of operands:")
        perr(f"    \"{line}\"")
        my_exit(ERR_OTHER_LEXSYN)

    operands: list[Operand] = []
    for i, op_str in enumerate(tokens):
        log(DEBUG, f"  operand {i + 1}: {op_str}")
        operands.append(Operand(op_str, SIGNATURES[opcode][i]))

    instructions.append(Instruction(opcode, operands))


def generate_element_tree(instructions: list[Instruction]) -> Element:
    """
    generates element tree (objects of class `Element`) from a list
    of instructions
    """

    # root
    prg_el = Element("program")
    prg_el.add_attribute("language", "IPPcode24")

    # go through instructions
    for i, inst in enumerate(instructions):

        # instruction element
        inst_el = Element("instruction")
        inst_el.add_attribute("order", str(i + 1))
        inst_el.add_attribute("opcode", inst.opcode.upper())

        # argument elements
        for j, op in enumerate(inst.op_iter()):
            op_el = Element(f"arg{j + 1}")
            op_el.add_attribute("type", op.type)
            op_el.set_content(op.value)
            inst_el.add_children([op_el])

        prg_el.add_children([inst_el])


    return prg_el


def my_exit(return_code: int) -> None:
    """cals `sys.exit` but also logs"""

    # find the name in the return codes
    rc_name = ""
    for key, value in globals().items():
        if "ERR" in key and value == return_code:
            rc_name = key
            break

    log(ERROR, f"exiting with code {return_code} ({rc_name})")
    sys.exit(return_code)


def main():
    check_args()

    # whole program from the input
    pgr_in = load_stdin()

    # remove comments + blank lines
    processed = preprocess(pgr_in)

    # check for header (.IPPcode24)
    if not header_present(processed):
        perr("Missing header .IPPcode24")
        my_exit(ERR_MISSING_HEADER)

    # parse code line by line to get a list of instruction objects
    instructions = []
    for line in processed.splitlines()[1:]:
        process_line(line, instructions)

    for instruction in instructions:
        log(DEBUG, f"processed instruction: {instruction}")

    # get xml tree
    prg_el = generate_element_tree(instructions)

    print(XML_HEADER)

    # print xml representation of the element tree
    prg_el.print_xml()


    log(INFO, "parse.py: all ok")
    sys.exit(0)

if __name__ == "__main__":
    main()
