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

# TODO: Calculate original length (in bytes) of each string.
# TODO: Assign correct offsets to strings repeated in the .DAT files.
# TODO: Find the pointer-pointers and mark them in the pointer sheet.

# TODO: Sort the pointer sheet.

# TODO: Add control codes? (Not really necessary)

import os
import subprocess
import codecs
import xlsxwriter
import re

from utils import file_blocks
from utils import capture_pointers_from_table, capture_pointers_from_function
from utils import pointer_constants, pointer_separators
from utils import pack, unpack, location_from_pointer

DUMP_ASCII = False

# Nomenclature for different parts of things:
# Game contains disks.
# Disks contain files.
# Files contain blocks.
# Blocks contain snippets, separated by \x00. (<END> tags)
# Snippets contain strings, separated by \x0a or \x0d. (line beaks)

script_dir = os.path.dirname(__file__)
rel_path = 'original_roms'
rom_file_path = os.path.join(script_dir, rel_path)

snippet_folder_path = os.path.join(script_dir, "snippets")
#print snippet_folder_path
        
workbook = xlsxwriter.Workbook('shinkaron_dump.xlsx')
worksheet = workbook.add_worksheet()

# Set column sizes to something reasonable where necessary.
worksheet.set_column('A:A', 20)
worksheet.set_column('E:E', 80)
worksheet.set_column('F:F', 90)

excel_row = 0

dump_files = []

pointer_locations = {}
pointer_count = 0


for (file, blocks) in file_blocks:
    print "Dumping file %s..." % file
    file_path = os.path.join(rom_file_path, file)
    in_file = open(file_path, 'rb')
    
    if file in pointer_constants:
        bytes = in_file.read()
        only_hex = ""
        for c in bytes:
            only_hex += "\\x%02x" % ord(c)

        first, second = pointer_separators[file]

        pointers = capture_pointers_from_table(first, second, only_hex)
        dialogue_pointers = capture_pointers_from_function(only_hex)
        
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
    
    for (block_start, block_end) in blocks:
        # TODO: If the dump has already been done, abort this loop.
        #if os.path.exists(os.path.join(snippet_folder_path, ""))

        dat_dump = (file == 'SINKA.DAT' or file == 'SEND.DAT')

        if dat_dump:
            in_file = codecs.open(file_path, 'r', 'shift_jis')
            whole_file = in_file.read()
            in_file.seek(0)
            snippets = in_file.readlines()
            for snippet in snippets:
                if snippet and len(snippet) > 4:
                    snippet_start = whole_file.index(snippet)
                    # ^ Here's where the offset calculation mistake is happening.
                    # Plus a whole lot of inefficiency... any way to trim the file whenever I find an index?
                    offset = hex(snippet_start)
                    # TODO: If there's already a snippet file with the same source and offset, recalculate the offset.
                    snippet_filename = "snippet_" + offset + "_" + "60" + "_" + file
                    snippet_dump = "dump_" + snippet_filename
                    snippet_file_path = os.path.join(snippet_folder_path, snippet_filename)
                    dump_file_path = os.path.join(snippet_folder_path, snippet_dump)

                    # TODO: Could probably make this recalculation a function.
                    while snippet_dump in dump_files:
                        truncated_file = whole_file[snippet_start+4:]
                        snippet_start += (whole_file.index(snippet)+4)
                        offset = hex(snippet_start)
                        # TODO: Should I really calculate the length of these strings? They don't need ptr adjustments. Here's 60 in the meantime.
                        snippet_filename = "snippet_" + offset + "_" + "60" + "_" + file
                        snippet_file_path = os.path.join(snippet_folder_path, snippet_filename)
                        snippet_dump = "dump_" + snippet_filename
                        dump_file_path = os.path.join(snippet_folder_path, snippet_dump)

                    snippet_file = open(snippet_filename, 'w')
                    snippet_file.write(snippet.encode('shift_jis'))
                    snippet_file.close()
                    
                    subprocess.call(".\SJIS_Dump %s %s 1 1" % (snippet_file_path, dump_file_path))
                    
                    dump_files.append(dump_file_path)
                    #os.remove(snippet_filename)
            
        else:
            block_length = block_end - block_start
        
            in_file.seek(block_start)
            bytes = in_file.read(block_length)
            only_hex = ""
            for c in bytes:
                only_hex += "\\x%02x" % ord(c)
                
            snippets = only_hex.split('\\x00')
            
            for snippet in snippets:
                if snippet and len(snippet) > 4:       # at least one byte
                    snippet_start = only_hex.index(snippet)
                    offset = hex(block_start + (snippet_start / 4))

                    snippet_bytes = snippet.replace('\\x', '').decode('hex')

                    snippet_filename = "snippet_" + offset + "_" + str(len(snippet_bytes)) + "_" + file
                    snippet_file = open(snippet_filename, 'wb')
                    snippet_file_path = os.path.join(snippet_folder_path, snippet_filename)
                    snippet_file.write(snippet_bytes)
                    snippet_file.close()
                
                    snippet_dump = "dump_" + snippet_filename
                    dump_file_path = os.path.join(snippet_folder_path, snippet_dump)

                    if DUMP_ASCII: 
                        subprocess.call(".\SJIS_Dump %s %s 1 1" % (snippet_file_path, dump_file_path))
                    else:
                        subprocess.call(".\SJIS_Dump %s %s 1 0" % (snippet_file_path, dump_file_path))
                    # Last argument: whether to dump ASCII text as well.
                    # Don't want them for the clean JP text dump, but do want them for dealing with pointers.
                
                    dump_files.append(dump_file_path)
                    #os.remove(snippet_filename)
    in_file.close()
        
dump = []
        
for file in dump_files:
    # file.split('_') is ('dump', 'snippet', offset, length, source)
    #offset, length, source = tuple(file.split('_')[2:5])
    source = file.split('_')[4]
    offset = file.split('_')[2]
    length = file.split('_')[3]

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
        total_offset = '0x%05x' % total_offset
        
        text = lines[n+1].rstrip() # No more newline chars
        
        try:
            pointer = pointer_locations[(source, total_offset)]
            pointer_count += 1
        except KeyError:
            pointer = ''
    
        dump.append(((source, total_offset), (pointer, text, length)))
        
    fo.close()

#sorted_dump = sorted(dump, key = lambda x: (x[0], x[1]))
    
print "Writing text dump to shinkaron_dump.xls..."
# Access this in a separate for loop, since there might be multiple texts in a snippet
for snippet in dump:
    worksheet.write(excel_row, 0, snippet[0][0])     # Source File
    worksheet.write(excel_row, 1, snippet[0][1])     # Text Location
    worksheet.write(excel_row, 2, snippet[1][0])     # Pointer Location
    worksheet.write(excel_row, 3, snippet[1][2])     # JP_Char
    worksheet.write(excel_row, 4, snippet[1][1])     # JP Text
    excel_row += 1

# Second sheet: all the pointers, regardless of whether they get matched up with any particular text.
# (So they don't get missed during reinsertion.)
print "Writing pointer sheet..."
pointer_sheet = workbook.add_worksheet()
excel_row = 0
pointer_strings = {}
# pointer_locations[(source, text_location)] = pointer_location
# dump = ((source, text_location), (pointer_location, text))
for (source, text_location) in pointer_locations.iterkeys():
    try:
        # This isn't taking well to tuple unpacking... Ugly solution it is!
        pointer_location= [d[1] for d in dump if d[0] == (source, text_location)][0][0]
        text = [d[1] for d in dump if d[0] == (source, text_location)][0][1]
        # TODO: Add JP_Char.
    except IndexError:
        (pointer_location, text) = (pointer_locations[(source, text_location)], '')

    pointer_sheet.write(excel_row, 0, source)           # Source File
    pointer_sheet.write(excel_row, 1, text_location)    # Text Location
    pointer_sheet.write(excel_row, 2, pointer_location) # Pointer
    pointer_sheet.write(excel_row, 3, len(text))        # JP_Char
    pointer_sheet.write(excel_row, 4, text)             # JP Text
    excel_row += 1



print "Cleaning up..."
# Cleanup.
workbook.close()

#for file in dump_files:
#    try:
#        os.remove(file)
#    except WindowsError: # Sometimes it doesn't find the file... strange.
#        pass
print "Dump successful. %i pointers matched." % pointer_count