
ERR_MISSING_HEADER=21

RED='\033[0;31m'
COLOR_RESET='\033[0m'

TEST_COUNT=0
PASSED_TESTS=0

# test value, expected
test_val () {
    TEST_COUNT=$(expr $TEST_COUNT + 1)
    if [ "$1" = "$2" ]; then
        echo passed
        PASSED_TESTS=$(expr $PASSED_TESTS + 1)
    else
        echo -e "${RED}failed (expected $2, got $1)$COLOR_RESET"
    fi
}

# empty input (blank line)
echo "" | ./run.sh
test_val $? $ERR_MISSING_HEADER

echo "all tests done (passed $PASSED_TESTS/$TEST_COUNT)"