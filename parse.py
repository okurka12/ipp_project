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

USAGE = "USAGE: parse.py [--help]"

# error codes
ERR_WRONG_ARG = 10


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




def main():
    check_args()

    pass


if __name__ == "__main__":
    main()