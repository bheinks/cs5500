#!/usr/bin/env python3

import sys

# Local imports
from lexer import Lexer

# Set True to disable console output, False otherwise
SUPPRESS_OUTPUT = False


def main(input_filename):
    if SUPPRESS_OUTPUT:
        sys.stdout = None

    # TODO: fix this iter nonsense so I can pull line_num as an attr
    with open(input_filename) as f:
        tokens = iter(Lexer(f.read()))

    for _ in tokens:
        pass
    #start(tokens)
    print("\n---- Completed parsing ----")


def print_rule(lhs, rhs):
    print(f"{lhs} -> {rhs}")


def start(tokens):
    prog(tokens)
    print_rule("N_START", "N_PROG")
    

def prog(tokens):
    prog_lbl(tokens)
    print_rule("N_PROG", "N_PROGLBL T_IDENT T_SCOLON N_BLOCK T_DOT")


def prog_lbl(tokens):
    if next(tokens) == "T_PROG":
        pass


if __name__ == '__main__':
    main(sys.argv[1])
