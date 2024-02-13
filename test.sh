#!/bin/bash

ERR_MISSING_HEADER=21
ERR_INVALID_INSTRUCTION=22
ERR_OTHER_LEX_SYN=23
OK=0

RED='\033[0;31m'
COLOR_RESET='\033[0m'

TEST_COUNT=0
PASSED_TESTS=0

# $1 - test value, $2 - expected, $3 - name
# also increments test_count
test_val () {
    echo -n "$3: "
    TEST_COUNT=$(expr $TEST_COUNT + 1)
    if [ "$1" = "$2" ]; then
        echo passed
        PASSED_TESTS=$(expr $PASSED_TESTS + 1)
    else
        echo -e "${RED}failed (expected $2, got $1)$COLOR_RESET"
    fi
}

# $1 - file to test, $2 - expected return code
test_file () {
    cat "$1" | ./run.sh > /dev/null 2> /dev/null
    test_val $? $2 "$1"
}

# empty input (blank line)
echo "" | ./run.sh > /dev/null 2> /dev/null
test_val $? $ERR_MISSING_HEADER "blank line"

# empty input (nothing at all)
echo -n "" | ./run.sh > /dev/null 2> /dev/null
test_val $? $ERR_MISSING_HEADER "nothing at all"

test_file example.txt $OK
test_file test_01.txt $OK
test_file test_02.txt $OK
test_file test_03.txt $OK
test_file test_04.txt $ERR_INVALID_INSTRUCTION
test_file test_05.txt $ERR_OTHER_LEX_SYN
test_file test_06.txt $ERR_OTHER_LEX_SYN

echo "all tests done (passed $PASSED_TESTS/$TEST_COUNT)"