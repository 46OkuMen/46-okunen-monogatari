# Makes use of a tool called SJIS_Dump which deals with the encoding better.

# Execute the command ".\SJIS_Dump OPENING.EXE opening 4 0"
# Open opening in write mode.
# Clean opening, removing large quantities of leading spaces and adjusting the offeset based on how many spaces are removed.
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
        print byte.encode('hex')
        byte = f.read(2)

#clean_bytes_string.replace("\xe6\x7f", "")
print clean_bytes_string

clean_bytes = bytearray(clean_bytes_string)

with open('opening', 'wb') as f:
    f.write(clean_bytes)
        
  
        
dump = {}

fo = codecs.open("opening", "r", encoding='shift_jis')
lines = fo.readlines()

for n in range(0, len(lines)+1, 3):
    offset_string = lines[n][11:].rstrip()     # first line of three, minus "Position : ", minus "\n"
    offset = int(offset_string, 16)
    #print offset_string
    #print offset
    text_raw = lines[n+1]
    #print text_raw[0:2]             # omg this was breaking it???
    #while text_raw[0:2] == '\xc3':    # checking for the space.  (Encoding error)
    #    text_raw = text_raw[5:]
    #    offset += 2
    hex_offset = hex(offset)
    
    print hex_offset
    #print text_raw
    
    dump[hex_offset] = text_raw
    

# Position : 3920
# japanese text
# blank

# ...