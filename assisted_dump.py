"""Assisted text dumper for 46 Okunen Monogatari: The Shinka Ron. Use with SJIS_Dump.exe."""
# SJIS_Dump is available at http://www.romhacking.net/utilities/645/

# Far from optimized or presentable; this is a script I'd call "good enough."

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
# that size. It splits two-byte characters across multiple buffers, so it mis-encodes them.
# I didn't know enough C++ to alter the program without causing memory leaks. Messy solution:
# Split up the source files themselves into 0x100 and smaller chunks by splitting them into the
# game text lines themselves, which are never longer than the game window (usually like 80 bytes of text).

import os
import subprocess
import codecs
from collections import OrderedDict, namedtuple

import xlsxwriter

from rominfo import file_blocks, pointer_constants, pointer_separators

from utils import capture_pointers_from_table, capture_pointers_from_function
from utils import unpack, location_from_pointer

# SJIS_Dump has an option to dump ASCII text as well.
# Set to False for getting game text, and True for getting pointers too.
DUMP_ASCII = True

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

pointer_locations = OrderedDict()
pointer_count = 0

for file, blocks in file_blocks.iteritems():
    print "Dumping file %s..." % file
    file_path = os.path.join(rom_file_path, file)
    in_file = open(file_path, 'rb')
    file_length = os.stat(file_path).st_size
    
    if file in pointer_constants:
        bytes = in_file.read()
        only_hex = ""
        for c in bytes:
            only_hex += "\\x%02x" % ord(c)

        first, second = pointer_separators[file]

        pointers = capture_pointers_from_table(first, second, only_hex)
        dialogue_pointers = capture_pointers_from_function(only_hex)
        
        for p in pointers:
            # pointer_locations[(file, text_location)] = [pointer1_location, pointer2,...]
            # Multiple pointer_locations for the same text_location...

            #pointer_location = only_hex.index(p.group(0))/4  # Where is this pointer found?
            pointer_location = p.start()/4

            pointer_location = '0x%05x' % pointer_location
            # And where does it point?
            text_location = location_from_pointer((p.group(2), p.group(3)), pointer_constants[file])

            if int(text_location, 16) > file_length:     # Clearly something is wrong.
                # These include: the code that tells pointers to add the pointer constant, ...
                #print "Weird pointer at", pointer_location, "points to", text_location
                continue

            #print text_location, pointer_location
            all_locations = [pointer_location,]

            if (file, text_location) in pointer_locations:
                all_locations = pointer_locations[(file, text_location)]
                all_locations.append(pointer_location)

            pointer_locations[(file, text_location)] = all_locations

        for p in dialogue_pointers:
            pointer_location = p.start()/4 + 2 # Don't include the identifier! Go 2 bytes after it.
            pointer_location = '0x%05x' % pointer_location
            #print p.group(1), p.group(2)
            text_location = location_from_pointer((p.group(1), p.group(2)), pointer_constants[file])
            if int(text_location, 16) > file_length:
                #print "Weird pointer at", pointer_location, "points to", text_location
                continue

            ##print text_location, pointer_location
            all_locations = [pointer_location,]

            if (file, text_location) in pointer_locations:
                all_locations = pointer_locations[(file, text_location)]
                all_locations.append(pointer_location)

            pointer_locations[(file, text_location)] = all_locations

        # So, it looks like some of the weird pointers are the table regex picking up lone 5e-0ds in the
        # function code. Safe to ignore those.

    for (block_start, block_end) in blocks:
        dat_dump = (file == 'SINKA.DAT' or file == 'SEND.DAT')

        if dat_dump:
            in_file = codecs.open(file_path, 'r', 'shift_jis')
            whole_file = in_file.read()
            in_file.seek(0)
            snippets = in_file.readlines()

            last_snippet_offset = 0

            for snippet in snippets:
                if snippet and len(snippet) > 4:
                    slice = whole_file[last_snippet_offset:]
                    snippet_start = slice.index(snippet) + last_snippet_offset
                    last_snippet_offset = snippet_start

                    offset = hex(snippet_start)
                    snippet_filename = "snippet_" + offset  + "_" + file
                    snippet_dump = "dump_" + snippet_filename
                    snippet_file_path = os.path.join(snippet_folder_path, snippet_filename)
                    dump_file_path = os.path.join(snippet_folder_path, snippet_dump)

                    snippet_file = open(snippet_file_path, 'w')
                    snippet_file.write(snippet.encode('shift_jis'))
                    snippet_file.close()
                    
                    subprocess.call(r".\SJIS_Dump %s %s 1 1" % (snippet_file_path, dump_file_path))
                    
                    dump_files.append(dump_file_path)
                    #os.remove(snippet_filename)
            
        else:
            block_length = block_end - block_start
        
            in_file.seek(block_start)
            bytes = in_file.read(block_length)
            only_hex = ""                      # Text block of all the block
            for c in bytes:
                only_hex += "\\x%02x" % ord(c)
                
            snippets = only_hex.split('\\x00')

            last_snippet_offset = 0
            
            for snippet in snippets:
                if snippet and len(snippet) > 4:       # at least one byte
                    slice = only_hex[last_snippet_offset*4:]
                    index_within_snippet = slice.index(snippet) / 4
                    snippet_start = index_within_snippet + last_snippet_offset
                    offset = hex(snippet_start + block_start)
                    #print offset

                    last_snippet_offset = snippet_start

                    snippet_bytes = snippet.replace('\\x', '').decode('hex')

                    snippet_filename = "snippet_" + offset + "_" + file
                    snippet_file_path = os.path.join(snippet_folder_path, snippet_filename)
                    snippet_file = open(snippet_file_path, 'wb')
                    snippet_file.write(snippet_bytes)
                    snippet_file.close()
                
                    snippet_dump = "dump_" + snippet_filename
                    dump_file_path = os.path.join(snippet_folder_path, snippet_dump)

                    #print snippet_file_path
                    #print dump_file_path

                    if DUMP_ASCII: 
                        subprocess.call(r".\SJIS_Dump %s %s 1 1" % (snippet_file_path, dump_file_path))
                    else:
                        subprocess.call(r".\SJIS_Dump %s %s 1 0" % (snippet_file_path, dump_file_path))
                    # Last argument: whether to dump ASCII text as well.
                    # Don't want them for the clean JP text dump, but do want them for dealing with pointers.
                
                    dump_files.append(dump_file_path)
                    #os.remove(snippet_filename)
    in_file.close()
        
dump = []
        
for file in dump_files:
    # file.split('_') is ('dump', 'snippet', offset, source)
    source = file.split('_')[3]
    offset = file.split('_')[2]

    fo = codecs.open(file, "r", encoding='shift_jis', errors='ignore') 

    lines = fo.readlines()

    for n in range(0, len(lines)-1, 3):
        offset_string = lines[n][11:].rstrip()  # first line of three, minus "Position : ", minus "\n"
        offset_within_snippet = hex(int(offset_string, 16))
        
        try:
            total_offset = int(offset, 16)
        except TypeError:
            total_offset = offset
            
        total_offset += int(offset_within_snippet, 16)
        total_offset = '0x%05x' % total_offset
        
        text = lines[n+1].rstrip() # No more newline chars

        if (source, total_offset) in pointer_locations:
            for ptr in pointer_locations[(source, total_offset)]:
                try:
                    pointer = ptr
                    pointer_count += 1
                except KeyError:
                    pointer = ''
    
                dump.append(((source, total_offset), (pointer, text)))
        
    fo.close()

#sorted_dump = sorted(dump, key = lambda x: (x[0], x[1]))
    
print "Writing text dump to shinkaron_dump.xlsx..."
# Access this in a separate for loop, since there might be multiple texts in a snippet
for snippet in dump:
    worksheet.write(excel_row, 0, snippet[0][0])     # Source File
    worksheet.write(excel_row, 1, snippet[0][1])     # Text Location
    worksheet.write(excel_row, 2, snippet[1][0])     # Pointer Location
    worksheet.write(excel_row, 3, snippet[1][1])     # JP Text
    excel_row += 1

# Second sheet: all the pointers, regardless of whether they get matched up with any particular text.
# (So they don't get missed during reinsertion.)
print "Writing pointer list to shinkaron_pointer_dump.xlsx..."
pointer_workbook = xlsxwriter.Workbook('shinkaron_pointer_dump.xlsx')
pointer_sheet = pointer_workbook.add_worksheet()
excel_row = 0


for (source, text_location), pointer_locs in pointer_locations.iteritems():
    for ptr in pointer_locs:
        # What is this try/except loop trying to do? Match up pointers with their text to put them on the sheet?
        try:
            # This isn't taking well to tuple unpacking... Ugly solution it is!
            #pointer_location = [d[1] for d in dump if d[0] == (source, text_location)][0][0]
            pointer_location = ptr
            text = [d[1] for d in dump if d[0] == (source, text_location)][0][1]
        except IndexError:
            pointer_location = ptr
            text = ''

        pointer_sheet.write(excel_row, 0, source)           # Source File
        pointer_sheet.write(excel_row, 1, text_location)    # Text Location
        pointer_sheet.write(excel_row, 2, pointer_location) # Pointer
        pointer_sheet.write(excel_row, 3, text)             # JP Text
        excel_row += 1

print "Cleaning up..."
# Cleanup.
workbook.close()
pointer_workbook.close()

print "Dump successful. %i pointers matched." % pointer_count