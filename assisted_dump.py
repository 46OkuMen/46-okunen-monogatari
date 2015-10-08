# Makes use of a tool called SJIS_Dump which deals with the encoding better.

# Execute the command ".\SJIS_Dump OPENING.EXE opening 4 0"
# Clean that dump of any characters that freak out my SJIS decoder.
# Parse the dump into offset:text pairs.
# Insert the text into the excel spreadsheet. Columns: File, Offset, Japanese, English.

import subprocess
import codecs
import xlsxwriter

subprocess.call(".\SJIS_Dump OPENING.EXE opening 7 0")

# need to remove characters like E67F that freak the SJIS parser out for some reason
clean_bytes_string = ""

with open('opening', 'rb') as f:
    byte = f.read(2)
    while byte !="":
        if byte.encode('hex') != "e67f":
            clean_bytes_string += byte
        else:
            print "Found an E67F, got rid of it"
        #print byte.encode('hex')
        byte = f.read(2)

#print clean_bytes_string

clean_bytes = bytearray(clean_bytes_string)

with open('opening', 'wb') as f:
    f.write(clean_bytes)
    
# Now the SJIS-Dump is clean, parse it and deal with it in memory.
        
dump = {}

fo = codecs.open("opening", "r", encoding='shift_jis')
lines = fo.readlines()

for n in range(0, len(lines)-1, 3):
    offset_string = lines[n][11:].rstrip()     # first line of three, minus "Position : ", minus "\n"
    offset = hex(int(offset_string, 16))
    
    text = lines[n+1]
    
    dump[offset] = text
    
    
workbook = xlsxwriter.Workbook('opening_dump.xlsx')
worksheet = workbook.add_worksheet()

worksheet.set_column('C:C', 75)

row = 0

for source, text in dump.iteritems():
    # excel cols: File, Offset, Japanese, English
    worksheet.write(row, 1, offset)
    worksheet.write(row, 2, text)
    row += 1
    
workbook.close()