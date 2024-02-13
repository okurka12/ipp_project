FILES="parse.py readme.md"

RED='\033[0;31m'
COLOR_RESET='\033[0m'

# counts 'todo' in $1
check_todo () {
    TODO_COUNT=$(grep -c todo $1)
    if [ $TODO_COUNT -gt 0 ]; then
        echo -e "${RED}WARNING: $1 contains $TODO_COUNT todos$COLOR_RESET"
    fi
}

all_files () {
    for FILE in $FILES; do
        if [ ! -f $FILE ]; then
            echo -e "${RED}WARNING: $FILE not present$COLOR_RESET"
        fi
    done
}

all_files
py change_date.py
check_todo parse.py
dos2unix $FILES
zip xpavli0a.zip $FILES
