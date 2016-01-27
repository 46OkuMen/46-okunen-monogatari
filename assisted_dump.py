# Assisted Text Dumper for 46 Okunen Monogatari: The Shinka Ron. Use in a directory with the contents of
# Disk A (User).FDI, extracted with EditDisk.

# For each file, dump all the discovered pointer tables into a dict "pointers".
# For each text block in the file (locations found previously), split it into smaller snippets,
# then write each snippet to its own temp file.
# Use SJIS-Dump to dump all the SJIS from these temp files, which puts it in other temp files.
# Read all the SJIS strings from these temp files, then determine their original offset and the location
# of their pointer, if they have one.
# Parse each string into a tuple (source file, offset, pointer location, text).
# Write all these values to an excel spreadsheet for use by the translator.
# Cleanup all the temp files.

# SJIS_Dump on its own messes up any file larger than 0x100 bytes, since its internal buffer is
# that size. It splits two-byte characters across multiple buffers, and as a result, it mis-encodes them.
# I didn't know enough C++ to alter the program without causing memory leaks. Messy solution:
# Split up the source files themselves into 0x100 and smaller chunks by splitting them into the
# game text lines themselves, which are never longer than the game window (usually like 60 bytes of text).

# TODO: When a string is repeated multiple times in a file, they are all assigned the offset of the earliest instance.

# TODO: Add control codes? (Very low priority)

# TODO: The pointer constant for OPENING.EXE is probably wrong - only one pointer is getting matched up.

import os
import subprocess
import codecs
import xlsxwriter
import re

from utils import file_blocks
from utils import capture_pointers_from_table, capture_pointers_from_function
from utils import pointer_constants, pointer_separators
from utils import pack, unpack, location_from_pointer


# Nomenclature for different parts of things:
# Game contains disks.
# Disks contain files.
# Files contain blocks.
# Blocks contain snippets, separated by \x00. (<END> tags)
# Snippets contain strings, separated by \x0a or \x0d. (line beaks)

script_dir = os.path.dirname(__file__)
rel_path = 'original_roms'
abs_file_path = os.path.join(script_dir, rel_path)
        
workbook = xlsxwriter.Workbook('shinkaron_dump.xlsx')
worksheet = workbook.add_worksheet()

# Set column sizes to something reasonable where necessary.
worksheet.set_column('A:A', 20)
worksheet.set_column('D:D', 80)
worksheet.set_column('E:E', 90)

excel_row = 0

dump_files = []

pointer_locations = {}
pointer_count = 0

for (file, blocks) in file_blocks:
    print "Dumping file %s..." % file
    file_path = os.path.join(abs_file_path, file)
    in_file = open(file_path, 'rb')
    
    if file in pointer_constants:
        bytes = in_file.read()
        only_hex = ""
        for c in bytes:
            only_hex += "\\x%02x" % ord(c)

        first, second = pointer_separators[file]

        pointers = capture_pointers_from_table(first, second, only_hex)
        dialogue_pointers = capture_pointers_from_function(only_hex)

        #print pointers
        
        for p in pointers:
            # pointer_locations[(file, text_location)] = pointer_location
            # Since we want to take a piece of text from the file and find its pointer.
            pointer_location = hex(only_hex.index(p.group(0))/4)  # Where is this pointer found?
            #print file 
            #print "Where the pointer is: " + pointer_location
            # Take the value of the pointer, 
            text_location = location_from_pointer((p.group(2), p.group(3)), pointer_constants[file])
            #print "What it points to: " + text_location
            pointer_locations[(file, text_location)] = pointer_location
        for p in dialogue_pointers:
            pointer_location = hex(only_hex.index(p.group(0))/4)
            #print p.group(1), p.group(2)
            text_location = location_from_pointer((p.group(1), p.group(2)), pointer_constants[file])
            pointer_locations[(file, text_location)] = pointer_location


        #for p in dialogue_pointers:
        #    pointer_location = hex(only_hex.index(p.group(0))/4)
        #    text_location
            
    
    for (block_start, block_end) in blocks:
        dat_dump = (file == 'SINKA.DAT' or file == 'SEND.DAT')
        if dat_dump:
            #print "dat dumping"
            in_file = codecs.open(file_path, 'r', 'shift_jis')
            whole_file = in_file.read()
            in_file.seek(0)
            snippets = in_file.readlines()
            for snippet in snippets:
                if snippet and len(snippet) > 4:
                    snippet_start = whole_file.index(snippet)
                    offset = hex(snippet_start)
                    
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
                    #if len(snippet) / 4 > 0x100:
                        #print str(len(snippet)/4) + " check " + offset + " for garbage"
                        #print snippet
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

#for p in pointer_locations.iteritems():
#    print p
# There are plenty of pointer locations at this point... maybe they don't match?
        
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
            
        #total_offset = hex(total_offset)
        total_offset = '0x%05x' % total_offset
        #print total_offset
        
        text = lines[n+1]
        
        try:
            pointer = pointer_locations[(source, total_offset)]
            pointer_count += 1
            # This prints all the successfully matched pointers. Not a lot...
        except KeyError:
            pointer = ''
    
        dump.append((source, total_offset, pointer, text))
        
    fo.close()

#sorted_dump = sorted(dump, key = lambda x: (x[0], x[1]))
    
print "Writing to shinkaron_dump.xls..."
# Access this in a separate for loop, since there might be multiple texts in a snippet
for snippet in dump:
    # excel cols: File, Offset, Pointer, Japanese, English
    worksheet.write(excel_row, 0, snippet[0])
    worksheet.write(excel_row, 1, snippet[1])
    worksheet.write(excel_row, 2, snippet[2])
    worksheet.write(excel_row, 3, snippet[3])
    excel_row += 1

print "Cleaning up..."
# Cleanup.
workbook.close()

for file in dump_files:
    try:
        os.remove(file)
    except WindowsError: # Sometimes it doesn't find the file... strange.
        pass
print "Dump successful. %i pointers matched." % pointer_count