#!/bin/bash

# Where to find sample input files
INPUT="./input"

# Where to place the actual output of running the program
OUTPUT="./output"

# Where to find the expected output
EXPECTED="./expected"

# Where to place generated diffs
REPORTS="./reports"

# The name of the executable file
EXEC=./parser.py

green=`tput setaf 2`
red=`tput setaf 1`
reset=`tput sgr0`

fails=0
passes=0

for f in $INPUT/*; do
    filename=$(basename $f) # strip path
    testname="${filename%.*}" # strip extension

    # actually run file
    ${EXEC} "$INPUT/$filename" > "$OUTPUT/$filename.out"

    # run diff
    diff -yib "$OUTPUT/$filename.out" "$EXPECTED/$filename.out" > "$REPORTS/$filename"

    if [ $? -ne 0 ]; then
        fails=$[ $fails + 1 ]
        echo "check: ${red}[fail]${reset} $testname"
        head "$REPORTS/$filename"
    else
        passes=$[ $passes + 1 ]
        echo "check: ${pass}[pass]${reset} $testname"
    fi
done

echo "check: ${green}$passes tests passed${reset}"
echo "check: ${red}$fails tests failed${reset}"
