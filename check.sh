#!/bin/bash

# Where to find sample input files
INPUT="./input"

# Where to place the actual output of running the program
OUTPUT="./output"
mkdir -p $OUTPUT

# Where to find the expected output
EXPECTED="./sample_oal"

# Where to place generated diffs
REPORTS="./reports"
mkdir -p $REPORTS

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
    diff -yi "$OUTPUT/$filename.out" "$EXPECTED/$testname.oal" > "$REPORTS/$filename"

    if [ $? -ne 0 ]; then
        fails=$[ $fails + 1 ]
        echo "check: ${red}[fail]${reset} $testname"
        head "$REPORTS/$filename"
    else
        passes=$[ $passes + 1 ]
        echo "check: ${green}[pass]${reset} $testname"
    fi
done

echo "check: ${green}$passes tests passed${reset}"
echo "check: ${red}$fails tests failed${reset}"
