# Makes use of a tool called SJIS_Dump which deals with the encoding better.

# Execute the command ".\SJIS_Dump OPENING.EXE opening 4 0"
# Open opening in write mode.
# Clean opening, removing large quantities of leading spaces and adjusting the offeset based on how many spaces are removed.
# Insert the text into the excel spreadsheet. Columns: File, Offset, Japanese, English.

import subprocess

subprocess.call(".\SJIS_Dump OPENING.EXE opening 4 0")

dump = {}

fo = open("opening", "r+")
lines = fo.readlines()

for n in range(0, len(lines)+1, 3):
    offset_string = lines[n][11:].rstrip()     # first line of three, minus "Position : ", minus "\n"
    offset = int(offset_string, 16)
    #print offset_string
    #print offset
    text_raw = lines[n+1]
    print text_raw[0:2]
    while text_raw[0:2] == '\xc3':    # checking for the space.  (Encoding error)
        text_raw = text_raw[5:]
        offset += 2
    hex_offset = hex(offset)
    
    print hex_offset
    print text_raw
    
    dump[hex_offset] = text_raw
    

# Position : 3920
# japanese text
# blank

# ...