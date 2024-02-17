FILES="parse.py readme1.md img/class_diagram.svg"

RED='\033[0;31m'
COLOR_RESET='\033[0m'

# prints red warning
echo_warning () {
        echo -e "${RED}WARNING: $@$COLOR_RESET"
}

# counts 'todo' in $1
check_todo () {
    TODO_COUNT=$(grep -c todo $1)
    if [ $TODO_COUNT -gt 0 ]; then
        echo_warning "$1 contains $TODO_COUNT todos"
    fi
}

all_files () {
    for FILE in $FILES; do
        if [ ! -f $FILE ]; then
            echo_warning "$FILE not present"
        fi
    done
}

all_files
py change_date.py
check_todo parse.py
dos2unix $FILES
zip xpavli0a.zip $FILES
