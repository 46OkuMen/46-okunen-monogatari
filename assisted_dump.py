# Makes use of a tool called SJIS_Dump which deals with the encoding better.

# Execute the command ".\SJIS-Dump OPENING.EXE opening 4 0"
# Open opening in write mode.
# Clean opening, removing large quantities of leading spaces and adjusting the offeset based on how many spaces are removed.
# Insert the text into the excel spreadsheet. Columns: File, Offset, Japanese, English.

import subprocess

subprocess.call(".\SJIS-Dump OPENING.EXE opening 4 0", shell=True)

# ...