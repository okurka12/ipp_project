# in parse.py, in a header like below,
# this script replaces xxxxx with todays date

##################
##  Vit Pavlik  ##
##   xpavli0a   ##
##    251301    ##
##              ##
##  Created:    ##
##  2024-02-18  ##
##              ##
##  Edited:     ##
##  xxxxxxxxxx  ##
##################

# also replaces the date in this footer
# ```
# Vít Pavlík (`xpavli0a`), 17. 2. 2024
# ```
# in readme1.md

import datetime
today = datetime.date.today()

FILENAME="parse.py"
FILENAME_2="readme1.md"

with open(FILENAME, "r", encoding="utf-8") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "##  Edited:     ##" in line:
            break
    lines[i + 1] = f"##  {today.year}-{today.month:02}-{today.day:02}  ##\n"

with open(FILENAME, "w", encoding="utf-8") as f:
    f.write("".join(lines))

print(f"changed 'edited' date of {FILENAME}")

with open(FILENAME_2, "r", encoding="utf-8") as f:
    lines_edited = []
    lines = f.readlines()
    for line in lines:
        if "Vít Pavlík (`xpavli0a`)" in line:
            replacement = f"Vít Pavlík (`xpavli0a`), " \
            f"{today.day}. {today.month}. {today.year}\n"
            lines_edited.append(replacement)
        else:
            lines_edited.append(line)

with open(FILENAME_2, "w", encoding="utf-8") as f:
    f.write("".join(lines_edited))

print(f"changed date in {FILENAME_2}")
