from __future__ import division

# Reinsertion script for 46 Okunen Monogatari: The Shinka Ron.

# TODO: Needs function pointers. Changing the length of the last bit of dialogue breaks some function at the end of the file.
# Find the addresses of those functions in other parts of the file during dumping, add them to pointer table?
# If that's a wrong-headed approach, I should dive into the disassembly with reko or just two instances of np2debug,
# one window with the original rom and one with the patched version, see where it crashes.

# Alternate idea: keep the total file length an identical size for every text block. That way, the function pointers won't break.
# If a block's total length is too short, add spaces where they won't hurt. (At the end, after the control codes?)
# If a block's total length is too long... hmm. I can sacrifice the error codes block at the end...
# Looks like the blocks will in general be too long. But I have 0x0030c space left in error codes.
# If the total pointer diff is less than 0x30c (708 dec), I can figure out a way to store it all in there.

# TODO: Gotta come up with a way to replace the first after a given offset. Can't just repalce the first one.
# If the text blocks are going to remain the same length, I might go and extract the original, block by block, and
# do the replacements that way. Then, I won't have to worry about code being replaced.

# TODO: Figure out what's going on with the first bits of dialogue which can't be found.

# TODO: Figure out why some Thelodus nametags have .. in front of them.

dump_xls = "shinkaron_dump_no_errors.xlsx"
pointer_xls = "shinkaron_pointer_dump.xlsx"

import os
import openpyxl
from binascii import unhexlify

from utils import file_blocks
from utils import pointer_constants, pointer_separators
from utils import pack, unpack, location_from_pointer, pointer_value_from_location, get_current_block, compare_strings

from openpyxl import load_workbook
from shutil import copyfile

from collections import OrderedDict

script_dir = os.path.dirname(__file__)
src_path = os.path.join(script_dir, 'original_roms')
dest_path = os.path.join(script_dir, 'patched_roms')

wb = load_workbook(dump_xls)
sheets = wb.get_sheet_names()
sheets.remove(u'ORIGINAL')
sheets.remove(u'MISC TITLES')
for file in sheets:
    # TODO: Remvoe this when more text is translated in other files.
    if file != "ST1.EXE":
        continue

    # First, index all the translations by the offset of the japanese text.
    translations = OrderedDict() # translations[offset] = (japanese, english)

    ws = wb.get_sheet_by_name(file)
    # These two variables count the replacements to track reinsertion progress.
    total_rows = 0
    total_replacements = 0

    for row in ws.rows[1:]:  # Skip the first row, it's just labels
        total_rows += 1

        offset = int(row[0].value, 16)
        japanese = row[2].value
        english = row[4].value

        if not english:
            # No translation is available; skip this row. (It still has a ptr, so its diff will be calculated later)
            continue
        translations[offset] = (japanese, english)

    #for _,e in translations.iteritems():
    #    print e

    # Next, load all the pointers from the excel sheet.
    pointers = {}              # text_offset: pointer_offset
    pointer_diffs = {}         # text_offset: diff

    last_pointer_diff = 0
    last_text_offset = 0

    current_text_block = 0

    pointer_wb = load_workbook(pointer_xls)
    pointer_sheet = pointer_wb.get_sheet_by_name("Sheet1") # For now, they are all in the same sheet... kinda ugly.

    for row in pointer_sheet.rows:
        if row[0].value == file:                          # Access ptrs for the current file only.
            text_offset = int(row[1].value, 16)
            pointer_offset = int(row[2].value, 16)
            pointers[text_offset] = pointer_offset

            pointer_diffs[text_offset] = last_pointer_diff
            print last_pointer_diff

            for block_index, block in enumerate(file_blocks[file]):
                lo, hi = block
                #print text_offset, lo, hi
                if (text_offset >= lo) and (text_offset <= hi):
                    if current_text_block != block_index:
                        current_text_block = block_index
                        print "block ", block_index
                        last_pointer_diff = 0
                        # Assign these here - since the error block is the last one, they will remain correct when called during ROM edits.
                        error_block_lo, error_block_hi = lo, hi
                        break

            # When the text_offset is 60871 (0xedc7), where the text is changed, it is between two ptrs.
            # Rather than look for something with the exact pointer, look for any translated text with a value between last_pointer_offset (excl) and text_offset (incl)
            # Calculate the diff, then add it to last_pointer_diff.
            lo = last_text_offset
            hi = text_offset
            for n in range((lo+1), (hi+1)):
                try:
                    jp, eng = translations[n]
                    len_diff = len(eng) - (len(jp)*2)                 # Shift_JIS has two-byte characters
                    #print len(eng), len(jp)*2
                    pointer_diffs[text_offset] = last_pointer_diff    # Tricky part: an adjustment takes effect first in the next pointer!!!
                    last_pointer_diff += len_diff                     # So let it get assigned the next time. (Also it's cumulative.)
                    #print "Here's the line! ", len_diff, last_pointer_diff
                except KeyError:
                    pass

            last_text_offset = text_offset

    #print pointer_diffs

    # Now, to begin the ROM edits.
    src_file_path = os.path.join(src_path, file)
    dest_file_path = os.path.join(dest_path, file)
    copyfile(src_file_path, dest_file_path)

    patched_file = open(dest_file_path, 'rb+')

    # First, rewrite the pointers - that doesn't change the length of anything.
    pointer_constant = pointer_constants[file]

    for text_location, diff in pointer_diffs.iteritems():
        if (text_location >= error_block_lo) and (text_location <= error_block_hi):
            #print "It's an error code ", text_location
            text_location = error_block_lo

        pointer_location = pointers[text_location]
        original_pointer_value = text_location - pointer_constant
        new_pointer_value = original_pointer_value + diff
        #print new_pointer_value
        # If the text is an error code, re-point it to the first bit of text in the block, which will probably just say "Error".

        byte_1, byte_2 = pack(new_pointer_value)
        #print byte_1, byte_2
        byte_1, byte_2 = chr(byte_1), chr(byte_2)
        patched_file.seek(pointer_location)
        patched_file.write(byte_1)
        patched_file.write(byte_2)

    # Then, rewrite the actual text.
    # Thought about just using replace but that involves converting the file to a string, searching bytes, etc.
    # Ideally I could just write the english string where the pointer is pointing, but I need to delete the jp text first.
    # Replace it is! Really slow... Is there a way to slice it up and know for sure?
    min_pointer_diff = min(pointer_diffs.itervalues())
    patched_file.seek(0)

    # First get a string of the whole file's bytes.
    file_string = ""
    for c in patched_file.read():
        file_string += "%02x" % ord(c)

    # Then get individual strings of each text block, and put them in a list.
    original_block_strings = []
    for index, block in enumerate(file_blocks[file]):
        lo, hi = block
        block_length = hi - lo
        block_string = ""
        patched_file.seek(lo)

        for c in patched_file.read(block_length):
            block_string += "%02x" % ord(c)

        original_block_strings.append(block_string)

    block_strings = []
    for index, block in enumerate(file_blocks[file]):
        lo, hi = block
        block_length = hi - lo
        block_string = ""
        patched_file.seek(lo)

        for c in patched_file.read(block_length):
            block_string += "%02x" % ord(c)

        block_strings.append(block_string)

    patched_file.close()

    # Replace each jp bytestring with eng bytestrings in the text blocks.
    for original_location, (jp, eng) in translations.iteritems():
        jp_bytestring = ""
        sjis = jp.encode('shift-jis')
        for c in sjis:
            jp_bytestring += "%02x" % ord(c)

        eng_bytestring = ""
        for c in eng:
            eng_bytestring += "%02x" % ord(c)

        current_block = get_current_block(original_location, file)
        block_string = block_strings[current_block]

        try:
            i = hex(block_string.index(jp_bytestring)//2)
        except ValueError:
            print "Could not find the text with the original location ", hex(original_location)
            continue

        new_block_string = block_string.replace(jp_bytestring, eng_bytestring, 1)  # Only the first occurrence.
        block_strings[current_block] = new_block_string

        total_replacements += 1

    # Finally, replace the old text blocks with the translated ones.
    for i, blk in enumerate(block_strings):
        #print compare_strings(blk, original_block_strings[i])
        #print hex(file_string.index(original_block_strings[i])//2)
        file_string = file_string.replace(original_block_strings[i], blk, 1)

    # Write the data to the patched file.
    with open(dest_file_path, "wb") as output_file:
        # omg I tried to call "unhexify" a million times. ugh
        data = unhexlify(file_string)
        output_file.write(data)

    # Print out stats. Pop open the champagne.
    translation_percent = (total_replacements / total_rows) * 100
    print file + " " + "%02f" % translation_percent + "% complete"