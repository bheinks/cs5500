#!/usr/bin/env python3

import sys

# Local imports
from lexer import get_token

# Set True to disable console output, False otherwise
SUPPRESS_OUTPUT = False


def main(input_filename):
    if SUPPRESS_OUTPUT:
        sys.stdout = None

    with open(input_filename) as f:
        tokens = get_token(f.read())

    print(next(tokens))
    print(next(tokens))
    print(next(tokens))
    print(next(tokens))
    print(next(tokens))
    print(next(tokens))
    print(next(tokens))


if __name__ == '__main__':
    main(sys.argv[1])
