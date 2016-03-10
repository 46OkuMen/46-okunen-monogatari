from __future__ import division

# Reinsertion script for 46 Okunen Monogatari: The Shinka Ron.

# TODO: Game crashing when entering evolution related menu items??
# I may have messed something up in the creature block. Maybe I should insert spaces at the end?
# Doesn't appear to be creature block related... still crashes with no creature block changes.
# One of the functions is probably breaking.

# TODO: Game crashes after you leave the first map and you learn of the thelodus sea's fate.
# FIgure out which map is being loaded, see if the pointers may have gotten messed up

# Backtracking. Just editing Yes/No/Canel. Evolution menu itmes:.crash. Loading next map: Works!
# Hmm. So the evolution menu stuff might depend on pointers that are below 0x10fa2 (ptrs) or 0x11839 (text).
# But the next map code must be located above that.

# TOOD: Check for text overflow. Examples:
# 0x10b70 - "It's all thanks to us looking after him con[LN]stantly!"
# 0x10d16 "you're from but you certainly suprised us[LN]."
# 0x10dc3 "I'm just glad you're okay[LN]!"
# 0x1094f "Do I look like I've changed to you? Elder?[LN]"
# 0x1055d "The fish are violent there after being affe[LN]cted by the light...""

# TODO: Moving overflow to the error block/spare block.
    # DONE - In the rom, replace the jp text with equivalent number of spaces
    # 2) Replace all of the error block with equivalent number of spaces
    # 3) Place all the text in the error block (what about control codes???)
    # 4) Rewrite all the pointer values to point to new locations
 # What about control codes??? If I move text from one block to another, I'll need to move hte control code as well.

# TODO: Why the extra menu item?? Look at the pointers for d9d4-ish.

# TODO: Apply changes to the disk rather than to the file; it'll save like 7 clicks per build cycle.
# Find the offset of each file (or just ST1.EXE for now) then slice the blockstring of the whole file
# at that point.

dump_xls = "shinkaron_dump_test.xlsx"
pointer_xls = "shinkaron_pointer_dump.xlsx"

import os
import math
from binascii import unhexlify

from utils import *

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
    if file != "ST1.EXE" or file == "46.EXE":
        # 46.EXE can be done manually.
        continue

    # First, index all the translations by the offset of the japanese text.

    translations = OrderedDict() # translations[offset] = (japanese, english)

    ws = wb.get_sheet_by_name(file)

    # These two variables count the replacements to track reinsertion progress.
    total_rows = 0
    total_replacements = 0

    # The spare block doesn't need translations.
    overflow_block_lo, overflow_block_hi = spare_block[file]

    for row in ws.rows[1:]:  # Skip the first row, it's just labels
        total_rows += 1

        offset = int(row[0].value, 16)

        if (offset >= overflow_block_lo) and (offset <= overflow_block_hi):
            continue

        japanese = row[2].value
        english = row[4].value

        if not english:
           english = ""

        translations[offset] = (japanese, english)

    # Next, load all the pointers from the excel sheet.
    pointers = {}              # text_offset: pointer_offset
    pointer_diffs = {}         # text_offset: diff

    pointer_diff = 0
    previous_text_offset = file_blocks[file][0][0]

    previous_text_block = 0
    current_text_block = 0
    current_block_end = 0

    pointer_wb = load_workbook(pointer_xls)
    pointer_sheet = pointer_wb.get_sheet_by_name("Sheet1") # For now, they are all in the same sheet... kinda ugly.

    overflow_text = []

    for row in pointer_sheet.rows:
        if row[0].value != file:
            continue                          # Access ptrs for the current file only.
            
        text_offset = int(row[1].value, 16)
        pointer_offset = int(row[2].value, 16)
        pointers[text_offset] = pointer_offset
        current_text_block = get_current_block(text_offset, file)
        try:
            current_block_end = file_blocks[file][current_text_block][1] # the hi value.
        except TypeError:
            pass
        print hex(current_block_end)
        # Rather than look for something with the exact pointer, look for any translated text with a value between previous_pointer_offset (excl) and text_offset (incl)
        # Calculate the diff, then add it to pointer_diff. There might be three or more bits of text betweeen the pointers (ex. dialogue)

        lo = previous_text_offset
        hi = text_offset
        for n in range((lo), (hi)):
            try:
                jp, eng = translations[n]
                len_diff = len(eng) - (len(jp)*2)

                end_of_string = n + len(eng) + pointer_diff
                if end_of_string > current_block_end:
                    print hex(n), "overflows past", hex(current_block_end), "with diff", pointer_diff
                    overflow_text.append(n)
                    # When you first hit overflow, they have totally different pointer diffs anyway
                    # So reset pointer_diff to have a fresh start when the new block begins.
                    #pointer_diff = 0
                    # TODO: Hmm... if you reset the first thing at the end of a block, it may not catch the rest...

                elif current_text_block != previous_text_block:
                    # First text in a new block. Reset the pointer diff.
                    pointer_diff = 0

                # If the eng part of the translation is blank, don't calculate a pointer diff.
                # But we still want it to be put in the overflow_text list.
                if not eng:
                    continue

                pointer_diff += len_diff
            except KeyError:
                continue

        previous_text_block = current_text_block
        previous_text_offset = text_offset
        pointer_diffs[text_offset] = pointer_diff
        print hex(text_offset), pointer_diffs[text_offset]

    #print pointer_diffs
    print overflow_text


    # Now, to begin the ROM edits.
    src_file_path = os.path.join(src_path, file)
    dest_file_path = os.path.join(dest_path, file)
    copyfile(src_file_path, dest_file_path)

    patched_file = open(dest_file_path, 'rb+')

    # First, rewrite the pointers - that doesn't change the length of anything.
    pointer_constant = pointer_constants[file]

    for text_location, diff in pointer_diffs.iteritems():
        #if diff == 0:
        #    continue
        # TODO: Redirect the old error message strings. (Or just don't, since the patch is perfect and they'll never show up?)
        if (text_location >= overflow_block_lo) and (text_location <= overflow_block_hi):
            #print "It's an error code ", text_location
            text_location = overflow_block_lo

        # TODO: Do something different for the creature text?

        pointer_location = pointers[text_location]

        original_pointer_value = text_location - pointer_constant
        #print "Original:", pack(original_pointer_value)
        new_pointer_value = original_pointer_value + diff

        byte_1, byte_2 = pack(new_pointer_value)
        #print "New:", byte_1, byte_2
        byte_1, byte_2 = chr(byte_1), chr(byte_2)

        # TODO: temporarily suppressing pointer writes!
        patched_file.seek(pointer_location)
        patched_file.write(byte_1)
        patched_file.write(byte_2)

        #print "Wrote new pointer value at", hex(pointer_location)

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

    creature_block_lo, creature_block_hi = creature_block[file]

    previous_replacement_offset = 0
    # previous replacement offset within the current block... 

    # Replace each jp bytestring with eng bytestrings in the text blocks.

    for original_location, (jp, eng) in translations.iteritems():
        if eng == "":
            # If there treally is no english translation, skip the replacement.
            continue

        if original_location in overflow_text:
            print hex(original_location), "being treated for overflow"
            eng = ""

        jp_bytestring = ""
        sjis = jp.encode('shift-jis')
        for c in sjis:
            hx = "%02x" % ord(c)
            if hx == '20': # Spaces get mis-encoded as ascii, which means the strings don't get found. Fix to 81-40
                hx = '8140'

            jp_bytestring += hx

        eng_bytestring = ""
        for c in eng:
            eng_bytestring += "%02x" % ord(c)

        if (original_location >= creature_block_lo) and (original_location <= creature_block_hi):
            this_string_diff = (len(jp)*2) - len(eng)
            #print this_string_diff
            if this_string_diff >= 0:
                eng_bytestring += "00"*this_string_diff
            else:
                # Append the 00s to the jp_bytestring so it gets replaced.
                jp_bytestring += "00"*((-1)*this_string_diff)

        current_block = get_current_block(original_location, file)
        #print "current block:", current_block
        block_string = block_strings[current_block]
        try:
            old_slice = block_string[previous_replacement_offset:]
            i = old_slice.index(jp_bytestring)//2
        except ValueError:
            previous_replacement_offset = 0
            old_slice = block_string
            i = old_slice.index(jp_bytestring)//2

        #print "original loc", hex(original_location)
        
        #print hex(original_location), hex(i)
        #print len(old_slice)

        new_slice = old_slice.replace(jp_bytestring, eng_bytestring, 1)
        new_block_string = block_strings[current_block].replace(old_slice, new_slice, 1)
        block_strings[current_block] = new_block_string

        previous_replacement_offset += i
        total_replacements += 1

    # Finally, replace the old text blocks with the translated ones.
    for i, blk in enumerate(block_strings):
        block_diff = len(blk) - len(original_block_strings[i])   # if block is too short, negative; too long, positive
        print len(original_block_strings[i])
        if block_diff < 0:
            number_of_spaces = ((-1)*block_diff)//2
            inserted_spaces_index = file_blocks[file][i][0] + (len(blk)//2)
            blk += '20' * number_of_spaces  # Fill it up with ascii 20 (space)

            print number_of_spaces, "added at", hex(inserted_spaces_index)
        elif block_diff > 0:
            print "Something went wrong, it's too long"

        print len(blk)

        file_string = file_string.replace(original_block_strings[i], blk, 1)

    # Write the data to the patched file.
    with open(dest_file_path, "wb") as output_file:
        data = unhexlify(file_string)
        output_file.write(data)

    # Print out stats. Pop open the champagne.
    translation_percent = int(math.floor((total_replacements / total_rows) * 100))
    print file , str(translation_percent) + "% complete"