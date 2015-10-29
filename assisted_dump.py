# Makes use of a tool called SJIS_Dump which deals with the encoding better.

# Use SJIS-Dump to dump all the SJIS from the game's source files.
# Parse the dump into (source, offset, dump).
# Insert the text into the excel spreadsheet. Columns: File, Offset, Japanese, English.

# SJIS_Dump on its own messes up any file larger than 0x100 bytes, since its internal buffer is
# that size. It splits two-byte characters across multiple buffers, and as a result, it mis-encodes them.
# Trying to alter the C++ program to have a larger buffer had some odd results, so my solution:
# Split up the source files themselves into 0x100 and smaller chunks by splitting them into the
# game text lines themselves, which are never longer than the game window.

# TODO: Where is the weird ASCII at the end of SINKA.DAT strings coming from?

# TODO: Add a column for the string's pointer location, if there is one.
# TODO: Add control codes?

import os
import subprocess
import codecs
import xlsxwriter
import re

from utils import file_blocks
from utils import specific_pointer_regex
from utils import pointer_constants, pointer_separators
from utils import pack, unpack, location_from_pointer


# Game contains disks.
# Disks contain files.
# Files contain blocks.
# Blocks contain snippets, separated by \x00. (<END> tags)
# Snippets contain strings, separated by \x0a or \x0d. (line beaks)
        
workbook = xlsxwriter.Workbook('shinkaron_dump.xlsx')
worksheet = workbook.add_worksheet()

# Set column sizes to something reasonable where necessary.
worksheet.set_column('A:A', 20)
worksheet.set_column('D:D', 80)
worksheet.set_column('E:E', 90)

excel_row = 0

dump_files = []

for file in file_blocks:
    print "Dumping file %s..." % file[0]
    in_file = open(file[0], 'rb')
    
    pointer_locations = {}
    if file[0] in pointer_constants:
        first, second = pointer_separators[file[0]]
        print specific_pointer_regex(first, second)
        pattern = re.compile(specific_pointer_regex(first, second))
        
        bytes = in_file.read()
        only_hex = ""
        for c in bytes:
            only_hex += "\\x%02x" % ord(c)
        #print only_hex
        pointers = pattern.finditer(only_hex)
        
        for p in pointers:
            print p.group(2), p.group(3)
            pointer_location = only_hex.index(p.group(0))
            location_pointed_to = location_from_pointer((p.group(2), p.group(3)), pointer_constants[file[0]])
            pointer_locations[pointer_location] = location_pointed_to
            
            # wait, how should I make sure these are just associated with their own files?
    
    for (block_start, block_end) in file[1]:
        dat_dump = file[0] == 'SINKA.DAT' or file[0] == 'SEND.DAT'
        block_length = block_end - block_start
        
        in_file.seek(block_start)
        bytes = in_file.read(block_length)
        only_hex = ""
        for c in bytes:
            only_hex += "\\x%02x" % ord(c)
        if dat_dump:
            snippets = only_hex.split('\\x0d\\x0a')  # these don't have any x00s in them
            print snippets
        else:
            snippets = only_hex.split('\\x00')
        for snippet in snippets:
            if snippet and len(snippet) > 4:       # at least one byte representation
                snippet_start = only_hex.index(snippet)
                offset = hex(block_start + (snippet_start / 4))
                snippet_filename = "snippet_" + offset + "_" + file[0]
                snippet_file = open(snippet_filename, 'wb')
                snippet_bytes = snippet.replace('\\x', '').decode('hex')
                snippet_file.write(snippet_bytes)
                snippet_file.close()
                
                snippet_dump = "dump_" + snippet_filename
                if dat_dump:
                    subprocess.call(".\SJIS_Dump %s %s 1 1" % (snippet_filename, snippet_dump))
                else:
                    subprocess.call(".\SJIS_Dump %s %s 1 0" % (snippet_filename, snippet_dump))
                
                dump_files.append(snippet_dump)
                os.remove(snippet_filename)
    in_file.close()
        
dump = []
#print dump_files
#print len(dump_files)
        
for file in dump_files:
    # file.split('_') is ('dump', 'snippet', sourcefile, offset)
    source = file.split('_')[3]
    offset = file.split('_')[2]

    fo = codecs.open(file, "r", encoding='shift_jis', errors='ignore') 

    lines = fo.readlines()

    for n in range(0, len(lines)-1, 3):
        offset_string = lines[n][11:].rstrip()     # first line of three, minus "Position : ", minus "\n"
        offset_within_snippet = hex(int(offset_string, 16))
        
        try:
            total_offset = int(offset, 16)
        except TypeError:
            total_offset = offset
            
        total_offset += int(offset_within_snippet, 16)
            
        total_offset = hex(total_offset)
        #print total_offset
        
        text = lines[n+1]
    
        dump.append((source, total_offset, text))
        
    fo.close()

# Access this in a separate for loop, since there might be multiple texts in a snippet
for snippet in dump:
    # excel cols: File, Offset, Pointer, Japanese, English
    worksheet.write(excel_row, 0, snippet[0])
    worksheet.write(excel_row, 1, snippet[1])
    worksheet.write(excel_row, 2, snippet[2])
    worksheet.write(excel_row, 3, snippet[2])
    excel_row += 1

workbook.close()

for file in dump_files:
    #os.remove(file)       #Wonder why it's not finding these?
    pass
