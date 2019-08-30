#!/usr/bin/env python3

import sys
import inspect

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
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    print('caller name:', calframe[1][3])
    sys.exit(1)


def n_start(lexer):
    n_prog(lexer)
    print_rule('N_START', 'N_PROG')


def n_prog_lbl(lexer):
    if next(lexer.tokens) != 'T_PROG':
        error(lexer.line_no)

    print_rule('N_PROGLBL', 'T_PROG')


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


def n_block(lexer):
    n_var_dec_part(lexer)
    n_proc_dec_part(lexer)
    n_stmt_part(lexer)

    print_rule('N_BLOCK', 'N_VARDECPART N_PROCDECPART N_STMTPART')


def n_var_dec_part(lexer):
    # TODO
    if lexer.current == 'T_VAR':
        n_var_dec(lexer)

        if next(lexer.tokens) != 'T_SCOLON':
            error(lexer.line_no)

        var_dec_lst(lexer)

        print_rule('N_VARDECPART', 'T_VAR N_VARDEC T_SCOLON N_VARDECLIST')
    else:
        print_rule('N_VARDECPART', 'epsilon')


def n_var_dec_lst(lexer):
    pass


def n_var_dec(lexer):
    n_ident(lexer)
    n_ident_lst(lexer)

    token = next(lexer.tokens)
    if token != 'T_COLON':
        print('error here: ' + token)
        error(lexer.line_no)

    n_type(lexer)

    print_rule('N_VARDEC', 'N_IDENT N_IDENTLIST T_COLON N_TYPE')


def n_ident(lexer):
    if next(lexer.tokens) != 'T_IDENT':
        error(lexer.line_no)

    print_rule('N_IDENT', 'T_IDENT')


def n_ident_lst(lexer):
    if lexer.current == 'T_COMMA':
        n_ident(lexer)
        n_ident_lst(lexer)

        print_rule('N_IDENTLST', 'T_COMMA N_IDENT N_IDENTLIST')
    else:
        print_rule('N_IDENTLST', 'epsilon')


def n_type(lexer):
    print("type: " + next(lexer.tokens))


def n_array(lexer):
    if next(lexer.tokens) != 'T_ARRAY':
        error(lexer.line_no)

    if next(lexer.tokens) != 'T_LBRACK':
        error(lexer.line_no)

    n_idx_range(lexer)

    if next(lexer.tokens) != 'T_RBRACK':
        error(lexer.line_no)

    if next(lexer.tokens) != 'T_OF':
        error(lexer.line_no)

    n_simple(lexer)

    print_rule('N_ARRAY', 'T_ARRAY T_LBRACK N_IDXRANGE T_RBRACK T_OF N_SIMPLE')


def n_idx(lexer):
    int_const(lexer)


def n_idx_range(lexer):
    pass


def n_simple(lexer):
    token = next(lexer.tokens)

    if token not in ('T_INT', 'T_CHAR', 'T_BOOL'):
        error(lexer.line_no)

    print_rule('N_SIMPLE', token)


def n_proc_dec_part(lexer):
    pass


def n_stmt_part(lexer):
    pass


if __name__ == '__main__':
    main(sys.argv[1])
