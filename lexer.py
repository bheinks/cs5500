import re

# Reserved words
KEYWORDS = {
    'and':      'T_AND',
    'array':    'T_ARRAY',
    'begin':    'T_BEGIN',
    'boolean':  'T_BOOL',
    'char':     'T_CHAR',
    'div':      'T_DIV',
    'do':       'T_DO',
    'else':     'T_ELSE',
    'end':      'T_END',
    'false':    'T_FALSE',
    'if':       'T_IF',
    'integer':  'T_INT',
    'not':      'T_NOT',
    'of':       'T_OF',
    'or':       'T_OR',
    'procedure':'T_PROC',
    'program':  'T_PROG',
    'read':     'T_READ',
    'then':     'T_THEN',
    'true':     'T_TRUE',
    'var':      'T_VAR',
    'while':    'T_WHILE',
    'write':    'T_WRITE',
}

# Token pattern specification
TOKEN_SPEC = (
    ('T_INTCONST',    r'\d+'),          # Integer constants
    ('T_CHARCONST',   r"'.'"),          # Character constants
    ('T_IDENT',       r'[A-Za-z_]\w*'), # Identifiers
    ('T_DOTDOT',      r'\.\.'),         # Begin operators
    ('T_ASSIGN',      r':='),
    ('T_LE',          r'<='),
    ('T_NE',          r'<>'),
    ('T_GE',          r'>='),
    ('T_LPAREN',      r'\('),              
    ('T_RPAREN',      r'\)'),
    ('T_MULT',        r'\*'),
    ('T_PLUS',        r'\+'),
    ('T_COMMA',       r','),
    ('T_MINUS',       r'-'),
    ('T_DOT',         r'\.'),
    ('T_COLON',       r':'),
    ('T_SCOLON',      r';'),
    ('T_LT',          r'<'),
    ('T_EQ',          r'='),
    ('T_GT',          r'>'),
    ('T_LBRACK',      r'\['),
    ('T_RBRACK',      r']'),            # End operators
    ('INVALIDCHAR',   r"''"),           # Invalid character constant
    ('WHITESPACE',    r'[ \t\r\n]+'),   # Whitespace
    ('UNKNOWN',       r'.'),            # Everything else
)


def valid_integer(intconst):
    # Python supports arbitrarily large integers, so there's no chance of overflow
    return int(intconst) <= 2147483647


def print_token(token, lexeme):
    print(f'TOKEN: {token:<12}LEXEME: {lexeme}')


def get_token(input_file):
    # Strip out all comments
    input_file = re.sub('\(\*.*?\*\)', '', input_file, flags=re.DOTALL)

    # Build token regex
    token_regex = '|'.join(f'(?P<{token}>{pattern})' for token, pattern in TOKEN_SPEC)

    # Loop over every match
    for match in re.finditer(token_regex, input_file, flags=re.ASCII):
        token = match.lastgroup
        lexeme = match.group()

        # Integer constants
        if token == 'T_INTCONST':
            if not valid_integer(lexeme):
                print(f'**** Invalid integer constant: {lexeme}')
                continue
        # Identifiers
        elif token == 'T_IDENT' and lexeme in KEYWORDS:
            token = KEYWORDS[lexeme]
        # Whitespace
        elif token == 'WHITESPACE':
            continue
        # Invalid character constants
        elif token == 'INVALIDCHAR' or (token == 'UNKNOWN' and lexeme.startswith("'")):
            print(f'**** Invalid character constant: {lexeme}')
            continue

        # Print token info
        print_token(token, lexeme)

        yield lexeme
