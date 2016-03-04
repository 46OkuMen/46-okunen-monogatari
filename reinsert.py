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

# TODO: Figure out what's going on with the dialogue which can't be found.

# TODO: Figure out why some Thelodus nametags have .. in front of them.

# TODO: Why duplicates? Some duplicates also have different pointer diffs, which is very bad.
# One cause is the interstitial text-finding loop in the pointer diff loop incorrectly assigning
# to the text offset instead of n. That's fixed now, but now it looks like some pointers are missing...

# TODO: Hmm. The non-text pointers are complicating this. Pointer tables and pointers to various
# weird things are in the spaces between text blocks. They are counted among the overflow text.
# But do they need to be moved? Probably not... 
# The issue with identifying overflow text in the translation loop is that there are no pointer diffs
# yet, so you can't really tell what's overflowing.

# TODO: What about control codes??? If I move text from one block to another, I'll need to move hte control code as well.

# TODO: Pretty big gap between 0x10fc8 and 0x117c7... are there any pointers to the creature names in that block? Do the interstitial numbers mean anything?

dump_xls = "shinkaron_dump_test.xlsx"
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
    if file != "ST1.EXE":
        continue

    # First, index all the translations by the offset of the japanese text.
    translations = OrderedDict() # translations[offset] = (japanese, english)

    overflow_text = []

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
           english = ""

        translations[offset] = (japanese, english)

    # Next, load all the pointers from the excel sheet.
    pointers = {}              # text_offset: pointer_offset
    pointer_diffs = {}         # text_offset: diff

    last_pointer_diff = 0
    last_text_offset = file_blocks[file][0][0]

    current_text_block = 0
    current_block_end = 0

    pointer_wb = load_workbook(pointer_xls)
    pointer_sheet = pointer_wb.get_sheet_by_name("Sheet1") # For now, they are all in the same sheet... kinda ugly.

    for row in pointer_sheet.rows:
        if row[0].value != file:
            continue                          # Access ptrs for the current file only.
            
        text_offset = int(row[1].value, 16)
        pointer_offset = int(row[2].value, 16)
        pointers[text_offset] = pointer_offset

        pointer_diffs[text_offset] = last_pointer_diff
        #print hex(text_offset), last_pointer_diff

        current_text_block = get_current_block(text_offset, file)
        #print "block", current_text_block
        try:
            current_block_end = file_blocks[file][current_text_block][1] # the hi value.
        except TypeError:
            pass

        # When the text_offset is 60871 (0xedc7), where the text is changed, it is between two ptrs.
        # Rather than look for something with the exact pointer, look for any translated text with a value between last_pointer_offset (excl) and text_offset (incl)
        # Calculate the diff, then add it to last_pointer_diff. There might be three or more bits of text betweeen the pointers (ex. dialogue)

        # This is being calculated incorrectly. Consecutive pointers, which should be picking up multiple bits of text, are picking them up one at a time...

        # I need to look at the space between the pointers, not text offsets.
        # lo should be the location of the text_offset of the previous pointer.
        # hi should be the location of the text_offset of the current pointer.

        lo = last_text_offset
        hi = text_offset
        for n in range((lo), (hi)):
            #print hex(lo), hex(hi)
            try:
                #print hex(n)
                jp, eng = translations[n]

                #print hex(lo), hex(hi)

                end_of_string = n + len(eng) + last_pointer_diff
                if end_of_string > current_block_end:
                    print hex(n), "overflows past", hex(current_block_end), "with diff", last_pointer_diff
                    overflow_text.append(n)
                    # For items in overflow_text:
                    # 1) In the rom, replace the jp text with equivalent number of spaces
                    # 2) Replace all of the error block with equivalent number of spaces
                    # 3) Place all the text in the error block (what control codes???)
                    # 4) Rewrite all the pointer values to point to new locations
                
                # If the eng part of the translation is blank, don't calculate a pointer diff.
                # But we still want it to be put in the overflow_text list.
                if not eng:
                    continue

                len_diff = len(eng) - (len(jp)*2)
                # The tricky part: adjusting text length adjusts the NEXT pointer's value!
                # So save the adjustment for next time here.
                # Plus, there can be a bunch of text between pointers. Save it up for next time.
                last_pointer_diff += len_diff
            except KeyError:
                continue

        last_text_offset = text_offset
        print hex(text_offset), last_pointer_diff

    #print pointer_diffs
    print overflow_text


    # Now, to begin the ROM edits.
    src_file_path = os.path.join(src_path, file)
    dest_file_path = os.path.join(dest_path, file)
    copyfile(src_file_path, dest_file_path)

    patched_file = open(dest_file_path, 'rb+')

    # First, rewrite the pointers - that doesn't change the length of anything.
    pointer_constant = pointer_constants[file]

    error_block_lo, error_block_hi = file_blocks[file][-1]

    for text_location, diff in pointer_diffs.iteritems():
        if (text_location >= error_block_lo) and (text_location <= error_block_hi):
            #print "It's an error code ", text_location
            text_location = error_block_lo

        pointer_location = pointers[text_location]

        original_pointer_value = text_location - pointer_constant
        new_pointer_value = original_pointer_value + diff

        byte_1, byte_2 = pack(new_pointer_value)
        #print byte_1, byte_2
        byte_1, byte_2 = chr(byte_1), chr(byte_2)
        patched_file.seek(pointer_location)
        patched_file.write(byte_1)
        patched_file.write(byte_2)

    # Then, rewrite the actual text.
    min_pointer_diff = min(pointer_diffs.itervalues())
    patched_file.seek(0)

    # First get a string of the whole file's bytes.
    file_string = ""
    for c in patched_file.read():
        file_string += "%02x" % ord(c)

    # Then get individual strings of each text block, and put them in a list.
    block_strings = []
    for index, block in enumerate(file_blocks[file]):
        lo, hi = block
        block_length = hi - lo
        block_string = ""
        patched_file.seek(lo)

        for c in patched_file.read(block_length):
            block_string += "%02x" % ord(c)

        block_strings.append(block_string)

    original_block_strings = list(block_strings)
    patched_file.close()

    # Replace each jp bytestring with eng bytestrings in the text blocks.
    for original_location, (jp, eng) in translations.iteritems():

        if original_location in overflow_text:
            eng = ""
            # Hmm. This keeps it the same lengths, which means overflow still occurs.
            # It's better to delete it.
            #eng = " "*(len(jp)*2)
            #print "Replacing text with blanks at", hex(original_location)

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
            print "Could not find the text with the original location", hex(original_location)
            # Most of the missing ones start with the left quote...
            # Is there some kind of overlap? Are the beginning/end being replaced in other replacements?
            # Some of the jp_bytestrings can be found if you slice it like [4:20] or something.
            continue

        new_block_string = block_string.replace(jp_bytestring, eng_bytestring, 1)  # Only the first occurrence.
        block_strings[current_block] = new_block_string

        total_replacements += 1

    # Finally, replace the old text blocks with the translated ones.
    for i, blk in enumerate(block_strings):
        block_diff = len(blk) - len(original_block_strings[i])   # if block is too short, negative; too long, positive
        print block_diff

        if block_diff < 0:
            blk += "20"*block_diff  # 0x20 is ascii for the space.
        elif block_diff > 0:
            print "Something went wrong, it's too long"

        print len(blk), len(original_block_strings[i])
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