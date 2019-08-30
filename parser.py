#!/usr/bin/env python3

import sys
import inspect

# Local imports
from lexer import Lexer

# Set True to disable console output, False otherwise
SUPPRESS_OUTPUT = False
DEBUG = True # Debug output


class Parser:
    def __init__(self):
        self.lexer = lexer

    def get_token(self):
        self.token = next(self.lexer.tokens)

    def error(self):
        print(f'Line {self.lexer.line_no}: syntax error')

        if DEBUG:
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            print('caller name:', calframe[1][3])

        sys.exit(1)

    def n_start(self):
        self.n_prog()
        print_rule('N_START', 'N_PROG')

    def n_prog_lbl(self):
        if self.token != 'T_PROG':
            self.error()

        print_rule('N_PROGLBL', 'T_PROG')

    def n_prog(self):
        self.n_prog_lbl()

        if self.token != 'T_IDENT':
            self.error()

        if self.token != 'T_SCOLON':
            self.error()

        self.n_block()

        if next(lexer.tokens) != 'T_DOT':
            self.error()

        print_rule('N_PROG', 'N_PROGLBL T_IDENT T_SCOLON N_BLOCK T_DOT')

    def n_block(self):
        self.n_var_dec_part()
        self.n_proc_dec_part()
        self.n_stmt_part()

        print_rule('N_BLOCK', 'N_VARDECPART N_PROCDECPART N_STMTPART')

    def n_var_dec_part(self):
        if lexer.current == 'T_VAR':
            self.n_var_dec()

            if next(lexer.tokens) != 'T_SCOLON':
                self.error()

            self.var_dec_lst()

            print_rule('N_VARDECPART', 'T_VAR N_VARDEC T_SCOLON N_VARDECLIST')
        else:
            print_rule('N_VARDECPART', 'epsilon')

    def n_var_dec_lst(self):
        pass

    def n_var_dec(self):
        self.n_ident()
        self.n_ident_lst()

        token = next(lexer.tokens)
        if token != 'T_COLON':
            print('error here: ' + token)
            self.error()

        self.n_type()

        print_rule('N_VARDEC', 'N_IDENT N_IDENTLIST T_COLON N_TYPE')

    def n_ident(self):
        if next(lexer.tokens) != 'T_IDENT':
            self.error()

        print_rule('N_IDENT', 'T_IDENT')

    def n_ident_lst(self):
        if lexer.current == 'T_COMMA':
            self.n_ident()
            self.n_ident_lst()

            print_rule('N_IDENTLST', 'T_COMMA N_IDENT N_IDENTLIST')
        else:
            print_rule('N_IDENTLST', 'epsilon')

    def n_type(self):
        print("type: " + next(lexer.tokens))

    def n_array(self):
        if next(lexer.tokens) != 'T_ARRAY':
            self.error()

        if next(lexer.tokens) != 'T_LBRACK':
            self.error()

        self.n_idx_range()

        if next(lexer.tokens) != 'T_RBRACK':
            self.error()

        if next(lexer.tokens) != 'T_OF':
            self.error()

        self.n_simple()

        print_rule('N_ARRAY', 'T_ARRAY T_LBRACK N_IDXRANGE T_RBRACK T_OF N_SIMPLE')

    def n_idx(self):
        self.int_const()

    def n_idx_range(self):
        pass

    def n_simple(self):
        token = next(lexer.tokens)

        if token not in ('T_INT', 'T_CHAR', 'T_BOOL'):
            self.error()

        print_rule('N_SIMPLE', token)

    def n_proc_dec_part(self):
        pass

    def n_stmt_part(self):
        pass


def print_rule(lhs, rhs):
    print(f'{lhs} -> {rhs}')


def main(input_filename):
    if SUPPRESS_OUTPUT:
        sys.stdout = None

    with open(input_filename) as f:
        parser = Parser(Lexer(f.read()))

    parser.get_token() # Initialize with first token
    parser.n_start()

    print('\n---- Completed parsing ----')


if __name__ == '__main__':
    main(sys.argv[1])
