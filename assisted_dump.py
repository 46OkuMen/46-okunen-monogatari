# Makes use of a tool called SJIS_Dump which deals with the encoding better.

# Use SJIS-Dump to dump all the SJIS from the game's source files.
# Parse the dump into (source, offset, dump).
# Insert the text into the excel spreadsheet. Columns: File, Offset, Pointer, Japanese, English.

# SJIS_Dump on its own messes up any file larger than 0x100 bytes, since its internal buffer is
# that size. It splits two-byte characters across multiple buffers, and as a result, it mis-encodes them.
# Trying to alter the C++ program to have a larger buffer had some odd results, so my solution:
# Split up the source files themselves into 0x100 and smaller chunks by splitting them into the
# game text lines themselves, which are never longer than the game window.

# TODO: These pointer values are straight up wrong, where are they coming from?
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

pointer_locations = {}

for (file, blocks) in file_blocks:
    print "Dumping file %s..." % file
    in_file = open(file, 'rb')
    
    if file in pointer_constants:
        first, second = pointer_separators[file]
        #print specific_pointer_regex(first, second)
        pattern = re.compile(specific_pointer_regex(first, second))
        
        bytes = in_file.read()
        only_hex = ""
        for c in bytes:
            only_hex += "\\x%02x" % ord(c)
        #print only_hex
        pointers = pattern.finditer(only_hex)
        
        for p in pointers:
            # pointer_locations[(file, text_location)] = pointer_location
            # Since we want to take a piece of text from the file and find its pointer.
            pointer_location = hex(only_hex.index(p.group(0)))  # Where is this pointer found?
            #print pointer_location
            # Take the value of the pointer, 
            text_location = location_from_pointer((p.group(2), p.group(3)), pointer_constants[file])
            #print text_location
            pointer_locations[(file, text_location)] = pointer_location
            
    
    for (block_start, block_end) in blocks:
        dat_dump = (file == 'SINKA.DAT' or file == 'SEND.DAT')
        if dat_dump:
            #print "dat dumping"
            in_file = codecs.open(file, 'r', 'shift_jis')
            whole_file = in_file.read()
            in_file.seek(0)
            snippets = in_file.readlines()
            for snippet in snippets:
                if snippet and len(snippet) > 4:
                    snippet_start = whole_file.index(snippet)
                    offset = hex(snippet_start)
                    #print offset
                    
                    snippet_filename = "snippet_" + offset + "_" + file
                    snippet_file = open(snippet_filename, 'w')
                    snippet_file.write(snippet.encode('shift_jis'))
                    snippet_file.close()
                    
                    snippet_dump = "dump_" + snippet_filename
                    
                    subprocess.call(".\SJIS_Dump %s %s 1 1" % (snippet_filename, snippet_dump))
                    
                    dump_files.append(snippet_dump)
                    os.remove(snippet_filename)
            
        else:
            block_length = block_end - block_start
        
            in_file.seek(block_start)
            bytes = in_file.read(block_length)
            only_hex = ""
            for c in bytes:
                only_hex += "\\x%02x" % ord(c)
                
            snippets = only_hex.split('\\x00')
        #if dat_dump:
            #snippets = only_hex.split(r'\\x0d\\x0a')  # these don't have any x00s in them
            #print snippets
            
            for snippet in snippets:
                if snippet and len(snippet) > 4:       # at least one byte representation
                    snippet_start = only_hex.index(snippet)
                    offset = hex(block_start + (snippet_start / 4))
                    if len(snippet) / 4 > 0x100:
                        print str(len(snippet)/4) + " check " + offset + " for garbage"
                        print snippet
                    snippet_filename = "snippet_" + offset + "_" + file
                    snippet_file = open(snippet_filename, 'wb')
                    snippet_bytes = snippet.replace('\\x', '').decode('hex')
                    snippet_file.write(snippet_bytes)
                    snippet_file.close()
                
                    snippet_dump = "dump_" + snippet_filename
                    
                    subprocess.call(".\SJIS_Dump %s %s 1 0" % (snippet_filename, snippet_dump))
                
                    dump_files.append(snippet_dump)
                    os.remove(snippet_filename)
    in_file.close()
        
dump = []
#print dump_files
#print len(dump_files)
#print pointer_locations
        
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
        
        try:
            pointer = pointer_locations[(source, total_offset)]
        except KeyError:
            pointer = ''
    
        dump.append((source, total_offset, pointer, text))
        
    fo.close()

# Access this in a separate for loop, since there might be multiple texts in a snippet
for snippet in dump:
    # excel cols: File, Offset, Pointer, Japanese, English
    worksheet.write(excel_row, 0, snippet[0])
    worksheet.write(excel_row, 1, snippet[1])
    worksheet.write(excel_row, 2, snippet[2])
    worksheet.write(excel_row, 3, snippet[3])
    excel_row += 1

    
# Cleanup.
workbook.close()

for file in dump_files:
    try:
        os.remove(file)       #Wonder why it's not finding these?
    except WindowsError:
        pass
