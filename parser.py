#!/usr/bin/env python3

import sys

# Local imports
from lexer import Lexer

# Set True to disable console output, False otherwise
SUPPRESS_OUTPUT = False


def main(input_filename):
    if SUPPRESS_OUTPUT:
        sys.stdout = None

    with open(input_filename) as f:
        lexer = Lexer(f.read())

    n_start(lexer)
    print('\n---- Completed parsing ----')


def print_rule(lhs, rhs):
    print(f'{lhs} -> {rhs}')


def error(line_no):
    print(f'Line {line_no}: syntax error')
    sys.exit(1)


def n_start(lexer):
    n_prog(lexer)
    print_rule('N_START', 'N_PROG')


def n_prog(lexer):
    n_prog_lbl(lexer)

    if next(lexer.tokens) != 'T_IDENT':
        error(lexer.line_no)

    if next(lexer.tokens) != 'T_SCOLON':
        error(lexer.line_no)

    n_block(lexer)

    if next(lexer.tokens) != 'T_DOT':
        error(lexer.line_no)

    print_rule('N_PROG', 'N_PROGLBL T_IDENT T_SCOLON N_BLOCK T_DOT')


def n_prog_lbl(lexer):
    if next(lexer.tokens) != 'T_PROG':
        error(lexer.line_no)


def n_block(lexer):
    n_var_dec_part(lexer)
    n_proc_dec_part(lexer)
    n_stmt_part(lexer)


def n_var_dec_part(lexer):
    if next(lexer.tokens) == 'T_VAR':
        n_var_dec(lexer)


def n_var_dec(lexer):
    ident(lexer)
    ident_list(lexer)

    if next(lexer.tokens) != 'T_COLON':
        error(lexer.line_no)

    n_type(lexer)


def n_proc_dec_part(lexer):
    pass


def n_stmt_part(lexer):
    pass


if __name__ == '__main__':
    main(sys.argv[1])
