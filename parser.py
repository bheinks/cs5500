#!/usr/bin/env python3

import sys

# Local imports
from lexer import Lexer
from symboltable import SymbolTable

# Print debug output if true
DEBUG = False

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer      # Lexer instance
        self.scopes = []        # Stack of symbol tables
        self.temp_idents = []   # List of idents waiting to be added to symbol table

    def get_token(self):
        try:
            self.token, self.lexeme = next(self.lexer.tokens)
        except StopIteration:
            self.token = None
            self.lexeme = None

    def error(self, message):
        print(f'Line {self.lexer.line_no}: {message}')
        sys.exit(1)

    def open_scope(self):
        if DEBUG:
            print('\n\n>>> Entering new scope...')

        self.scopes.append(SymbolTable())

    def close_scope(self):
        if DEBUG:
            print('\n<<< Exiting scope...')

        self.scopes.pop()

    def new_id(self, name, var_type, bounds=None, base_type=None):
        current_scope = self.scopes[-1]

        # If identifier doesn't exist in current scope, add it
        if not current_scope.add(name, var_type, bounds, base_type):
            self.error('Multiply defined identifier')

    # Search for identifier in all open scopes
    def search_id(self, ident_name):
        ident = None

        for scope in reversed(self.scopes):
            ident = scope.get(ident_name)

            if ident:
                break

        return ident

    def n_prog_lbl(self):
        print_rule('N_PROGLBL', 'T_PROG')

        if self.token == 'T_PROG':
            self.get_token()
        else:
            self.error('syntax error')

    def n_prog(self):
        print_rule('N_PROG', 'N_PROGLBL T_IDENT T_SCOLON N_BLOCK T_DOT')

        self.n_prog_lbl()

        # Open global scope
        self.open_scope()

        if self.token == 'T_IDENT':
            # Add program to global scope
            self.new_id(self.lexeme, 'PROGRAM')

            self.get_token()
            if self.token == 'T_SCOLON':
                self.get_token()
                self.n_block()

                if self.token == 'T_DOT':
                    self.get_token()

                    if self.token:
                        print('Syntax error: unexpected chars at end of program!')
                        sys.exit(1)
                else:
                    self.error('syntax error')
            else:
                self.error('syntax error')
        else:
            self.error('syntax error')

    def n_block(self):
        print_rule('N_BLOCK', 'N_VARDECPART N_PROCDECPART N_STMTPART')

        self.n_var_dec_part()
        self.n_proc_dec_part()
        self.n_stmt_part()

        self.close_scope()

    def n_var_dec_part(self):
        if self.token == 'T_VAR':
            print_rule('N_VARDECPART', 'T_VAR N_VARDEC T_SCOLON N_VARDECLST')

            self.get_token()
            self.n_var_dec()

            if self.token == 'T_SCOLON':
                self.get_token()
                self.n_var_dec_lst()
            else:
                self.error('syntax error')
        else:
            print_rule('N_VARDECPART', 'epsilon')

    def n_var_dec_lst(self):
        if self.token == 'T_IDENT':
            print_rule('N_VARDECLST', 'N_VARDEC T_SCOLON N_VARDECLST')
            self.n_var_dec()

            if self.token == 'T_SCOLON':
                self.get_token()
                self.n_var_dec_lst()
            else:
                self.error('syntax error')
        else:
            print_rule('N_VARDECLST', 'epsilon')

    def n_var_dec(self):
        print_rule('N_VARDEC', 'N_IDENT N_IDENTLST T_COLON N_TYPE')

        # Append first identifier to temporary list
        self.temp_idents.append(self.n_ident())

        self.n_ident_lst()

        if self.token == 'T_COLON':
            self.get_token()

            # Get variable type (and bounds and base type if array)
            var_type, bounds, base_type = self.n_type()

            # Add all identifiers to scope
            for ident in self.temp_idents:
                self.new_id(ident, var_type, bounds, base_type)

            # Reset temporary list of identifiers
            self.temp_idents = []
        else:
            self.error('syntax error')

    def n_ident(self):
        print_rule('N_IDENT', 'T_IDENT')

        if self.token == 'T_IDENT':
            name = self.lexeme
            self.get_token()

            return name
        else:
            self.error('syntax error')

    def n_ident_lst(self):
        if self.token == 'T_COMMA':
            print_rule('N_IDENTLST', 'T_COMMA N_IDENT N_IDENTLST')

            self.get_token()

            # Add additional identifiers to temporary list
            self.temp_idents.append(self.n_ident())

            self.n_ident_lst()
        else:
            print_rule('N_IDENTLST', 'epsilon')

    def n_type(self):
        bounds = None
        base_type = None

        if self.token in ('T_INT', 'T_CHAR', 'T_BOOL'):
            print_rule('N_TYPE', 'N_SIMPLE')
            var_type = self.n_simple()
        elif self.token == 'T_ARRAY':
            print_rule('N_TYPE', 'N_ARRAY')
            var_type = 'ARRAY'
            bounds, base_type = self.n_array()
        else:
            self.error('syntax error')

        return var_type, bounds, base_type

    def n_array(self):
        print_rule('N_ARRAY', 'T_ARRAY T_LBRACK N_IDXRANGE T_RBRACK T_OF N_SIMPLE')

        if self.token == 'T_ARRAY':
            self.get_token()

            if self.token == 'T_LBRACK':
                self.get_token()
                bounds = self.n_idx_range()

                if self.token == 'T_RBRACK':
                    self.get_token()

                    if self.token == 'T_OF':
                        self.get_token()
                        base_type = self.n_simple()

                        return bounds, base_type
                    else:
                        self.error('syntax error')
                else:
                    self.error('syntax error')
            else:
                self.error('syntax error')
        else:
            self.error('syntax error')

    def n_idx(self):
        print_rule('N_IDX', 'T_INTCONST')

        if self.token == 'T_INTCONST':
            bound = self.lexeme
            self.get_token()

            return bound
        else:
            self.error('syntax error')

    def n_idx_range(self):
        print_rule('N_IDXRANGE', 'N_IDX T_DOTDOT N_IDX')

        left_bound = self.n_idx()

        if self.token == 'T_DOTDOT':
            self.get_token()
            right_bound = self.n_idx()

            return left_bound, right_bound
        else:
            self.error('syntax error')

    def n_simple(self):
        print_rule('N_SIMPLE', self.token)

        if self.token in ('T_INT', 'T_CHAR', 'T_BOOL'):
            var_type = self.lexeme.upper()
            self.get_token()

            return var_type
        else:
            self.error('syntax error')

    def n_proc_dec_part(self):
        if self.token == 'T_PROC':
            print_rule('N_PROCDECPART', 'N_PROCDEC T_SCOLON N_PROCDECPART')
            self.n_proc_dec()

            if self.token == 'T_SCOLON':
                self.get_token()
                self.n_proc_dec_part()
            else:
                self.error('syntax error')
        else:
            print_rule('N_PROCDECPART', 'epsilon')

    def n_proc_dec(self):
        print_rule('N_PROCDEC', 'N_PROCHDR N_BLOCK')

        self.n_proc_hdr()

        # Open new scope
        self.open_scope()

        self.n_block()

    def n_proc_hdr(self):
        print_rule('N_PROCHDR', 'T_PROC T_IDENT T_SCOLON')

        if self.token == 'T_PROC':
            self.get_token()

            if self.token == 'T_IDENT':
                # Add new procedure to current scope
                self.new_id(self.lexeme, 'PROCEDURE')

                self.get_token()

                if self.token == 'T_SCOLON':
                    self.get_token()
                else:
                    self.error('syntax error')
            else:
                self.error('syntax error')
        else:
            self.error('syntax error')

    def n_stmt_part(self):
        print_rule('N_STMTPART', 'N_COMPOUND')
        self.n_compound()

    def n_compound(self):
        print_rule('N_COMPOUND', 'T_BEGIN N_STMT N_STMTLST T_END')

        if self.token == 'T_BEGIN':
            self.get_token()
            self.n_stmt()
            self.n_stmt_lst()

            if self.token == 'T_END':
                self.get_token()
            else:
                self.error('syntax error')
        else:
            self.error('syntax error')

    def n_stmt_lst(self):
        if self.token == 'T_SCOLON':
            print_rule('N_STMTLST', 'T_SCOLON N_STMT N_STMTLST')

            self.get_token()
            self.n_stmt()
            self.n_stmt_lst()
        else:
            print_rule('N_STMTLST', 'epsilon')

    def n_stmt(self):
        if self.token == 'T_IDENT':
            ident = self.search_id(self.lexeme)
            if not ident:
                self.error('Unidentified identifier')

            if ident.var_type == 'PROCEDURE':
                print_rule('N_STMT', 'N_PROCSTMT')
                self.n_proc_stmt()
            else:
                print_rule('N_STMT', 'N_ASSIGN')
                self.n_assign()
        elif self.token == 'T_READ':
            print_rule('N_STMT', 'N_READ')
            self.n_read()
        elif self.token == 'T_WRITE':
            print_rule('N_STMT', 'N_WRITE')
            self.n_write()
        elif self.token == 'T_IF':
            print_rule('N_STMT', 'N_CONDITION')
            self.n_condition()
        elif self.token == 'T_WHILE':
            print_rule('N_STMT', 'N_WHILE')
            self.n_while()
        elif self.token == 'T_BEGIN':
            print_rule('N_STMT', 'N_COMPOUND')
            self.n_compound()
        else:
            self.error('syntax error')

    def n_assign(self):
        print_rule('N_ASSIGN', 'N_VARIABLE T_ASSIGN N_EXPR')

        self.n_variable()

        if self.token == 'T_ASSIGN':
            self.get_token()
            self.n_expr()
        else:
            self.error('syntax error')

    def n_proc_stmt(self):
        print_rule('N_PROCSTMT', 'N_PROCIDENT')
        self.n_proc_ident()

    def n_proc_ident(self):
        print_rule('N_PROCIDENT', 'T_IDENT')

        if self.token == 'T_IDENT':
            self.get_token()
        else:
            self.error('syntax error')

    def n_read(self):
        print_rule('N_READ', 'T_READ T_LPAREN N_INPUTVAR N_INPUTLST T_RPAREN')

        if self.token == 'T_READ':
            self.get_token()

            if self.token == 'T_LPAREN':
                self.get_token()
                self.n_input_var()
                self.n_input_lst()

                if self.token == 'T_RPAREN':
                    self.get_token()
                else:
                    self.error('syntax error')
            else:
                self.error('syntax error')
        else:
            self.error('syntax error')

    def n_input_lst(self):
        if self.token == 'T_COMMA':
            print_rule('N_INPUTLST', 'T_COMMA N_INPUTVAR N_INPUTLST')

            self.get_token()
            self.n_input_var()
            self.n_input_lst()
        else:
            print_rule('N_INPUTLST', 'epsilon')

    def n_input_var(self):
        print_rule('N_INPUTVAR', 'N_VARIABLE')
        self.n_variable()

    def n_write(self):
        print_rule('N_WRITE', 'T_WRITE T_LPAREN N_OUTPUT N_OUTPUTLST T_RPAREN')

        if self.token == 'T_WRITE':
            self.get_token()

            if self.token == 'T_LPAREN':
                self.get_token()
                self.n_output()
                self.n_output_lst()

                if self.token == 'T_RPAREN':
                    self.get_token()
                else:
                    self.error('syntax error')
            else:
                self.error('syntax error')
        else:
            self.error('syntax error')

    def n_output_lst(self):
        if self.token == 'T_COMMA':
            print_rule('N_OUTPUTLST', 'T_COMMA N_OUTPUT N_OUTPUTLST')

            self.get_token()
            self.n_output()
            self.n_output_lst()
        else:
            print_rule('N_OUTPUTLST', 'epsilon')

    def n_output(self):
        print_rule('N_OUTPUT', 'N_EXPR')
        self.n_expr()

    def n_condition(self):
        print_rule('N_CONDITION', 'T_IF N_EXPR T_THEN N_STMT N_ELSEPART')

        if self.token == 'T_IF':
            self.get_token()
            self.n_expr()

            if self.token == 'T_THEN':
                self.get_token()
                self.n_stmt()
                self.n_else_part()
            else:
                self.error('syntax error')
        else:
            self.error('syntax error')

    def n_else_part(self):
        if self.token == 'T_ELSE':
            print_rule('N_ELSEPART', 'T_ELSE N_STMT')

            self.get_token()
            self.n_stmt()
        else:
            print_rule('N_ELSEPART', 'epsilon')

    def n_while(self):
        print_rule('N_WHILE', 'T_WHILE N_EXPR T_DO N_STMT')

        if self.token == 'T_WHILE':
            self.get_token()
            self.n_expr()

            if self.token == 'T_DO':
                self.get_token()
                self.n_stmt()
            else:
                self.error('syntax error')
        else:
            self.error('syntax error')

    def n_expr(self):
        print_rule('N_EXPR', 'N_SIMPLEEXPR N_OPEXPR')

        simple_type = self.n_simple_expr()
        op_type = self.n_op_expr()

        return "BOOLEAN" if op_type else simple_type

    def n_op_expr(self):
        if self.token in ('T_LT', 'T_LE', 'T_NE', 'T_EQ', 'T_GT', 'T_GE'):
            print_rule('N_OPEXPR', 'N_RELOP N_SIMPLEEXPR')

            self.n_rel_op()
            simple_type = self.n_simple_expr()

            return simple_type
        else:
            print_rule('N_OPEXPR', 'epsilon')

    def n_simple_expr(self):
        print_rule('N_SIMPLEEXPR', 'N_TERM N_ADDOPLST')
        term_type = self.n_term()
        self.n_add_op_lst()

        return term_type

    def n_add_op_lst(self):
        if self.token in ('T_PLUS', 'T_MINUS', 'T_OR'):
            print_rule('N_ADDOPLST', 'N_ADDOP N_TERM N_ADDOPLST')

            self.n_add_op()
            self.n_term()
            self.n_add_op_lst()
        else:
            print_rule('N_ADDOPLST', 'epsilon')

    def n_term(self):
        print_rule('N_TERM', 'N_FACTOR N_MULTOPLST')

        factor_type = self.n_factor()
        self.n_mult_op_lst()

        return factor_type

    def n_mult_op_lst(self):
        if self.token in ('T_MULT', 'T_DIV', 'T_AND'):
            print_rule('N_MULTOPLST', 'N_MULTOP N_FACTOR N_MULTOPLST')

            self.n_mult_op()
            self.n_factor()
            self.n_mult_op_lst()
        else:
            print_rule('N_MULTOPLST', 'epsilon')

    def n_factor(self):
        if self.token in ('T_PLUS', 'T_MINUS', 'T_IDENT'):
            print_rule('N_FACTOR', 'N_SIGN N_VARIABLE')

            self.n_sign()
            var_type = self.n_variable()

            return var_type
        elif self.token in ('T_INTCONST', 'T_CHARCONST', 'T_TRUE', 'T_FALSE'):
            print_rule('N_FACTOR', 'N_CONST')

            const_type = self.n_const()

            return const_type
        elif self.token == 'T_LPAREN':
            print_rule('N_FACTOR', 'T_LPAREN N_EXPR T_RPAREN')

            self.get_token()
            expr_type = self.n_expr()

            if self.token == 'T_RPAREN':
                self.get_token()
            else:
                self.error('syntax error')

            return expr_type
        elif self.token == 'T_NOT':
            print_rule('N_FACTOR', 'T_NOT N_FACTOR')

            self.get_token()
            self.n_factor()

            return "BOOLEAN"
        else:
            self.error('syntax error')

    def n_sign(self):
        if self.token in ('T_PLUS', 'T_MINUS'):
            print_rule('N_SIGN', self.token)
            self.get_token()
        else:
            print_rule('N_SIGN', 'epsilon')

    def n_add_op(self):
        print_rule('N_ADDOP', self.token)

        if self.token in ('T_PLUS', 'T_MINUS', 'T_OR'):
            self.get_token()
        else:
            self.error('syntax error')

    def n_mult_op(self):
        print_rule('N_MULTOP', self.token)

        if self.token in ('T_MULT', 'T_DIV', 'T_AND'):
            self.get_token()
        else:
            self.error('syntax error')

    def n_rel_op(self):
        print_rule('N_RELOP', self.token)

        if self.token in ('T_LT', 'T_LE', 'T_NE', 'T_EQ', 'T_GT', 'T_GE'):
            self.get_token()
        else:
            self.error('syntax error')

    def n_variable(self):
        print_rule('N_VARIABLE', 'T_IDENT N_IDXVAR')

        if self.token == 'T_IDENT':
            # Search for identifier in scope
            ident = self.search_id(self.lexeme)

            self.get_token()
            self.n_idx_var()

            return ident.var_type
        else:
            self.error('syntax error')

    def n_idx_var(self):
        if self.token == 'T_LBRACK':
            print_rule('N_IDXVAR', 'T_LBRACK N_EXPR T_RBRACK')

            self.get_token()
            self.n_expr()

            if self.token == 'T_RBRACK':
                self.get_token()
            else:
                self.error('syntax error')
        else:
            print_rule('N_IDXVAR', 'epsilon')

    def n_const(self):
        if self.token == 'T_INTCONST':
            print_rule('N_CONST', self.token)
            self.get_token()

            return 'INTEGER'
        elif self.token == 'T_CHARCONST':
            print_rule('N_CONST', self.token)
            self.get_token()

            return 'CHAR'
        elif self.token in ('T_TRUE', 'T_FALSE'):
            print_rule('N_CONST', 'N_BOOLCONST')
            self.n_bool_const()

            return 'BOOLEAN'
        else:
            self.error('syntax error')

    def n_bool_const(self):
        print_rule('N_BOOLCONST', self.token)

        if self.token in ('T_TRUE', 'T_FALSE'):
            self.get_token()
        else:
            self.error('syntax error')


def print_rule(lhs, rhs):
    if DEBUG:
        print(f'{lhs} -> {rhs}')


def main(input_filename):
    with open(input_filename) as f:
        parser = Parser(Lexer(f.read()))

    parser.get_token() # Initialize with first token
    parser.n_prog()

    print('\n---- Completed parsing ----')


if __name__ == '__main__':
    main(sys.argv[1])
