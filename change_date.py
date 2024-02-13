# in a header like below, this script replaces xxxxx with todays date

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

import datetime
today = datetime.date.today()

FILENAME="parse.py"

with open(FILENAME, "r", encoding="utf-8") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "##  Edited:     ##" in line:
            break
    lines[i + 1] = f"##  {today.year}-{today.month:02}-{today.day:02}  ##\n"

with open(FILENAME, "w", encoding="utf-8") as f:
    f.write("".join(lines))

print(f"changed 'edited' date of {FILENAME}")
