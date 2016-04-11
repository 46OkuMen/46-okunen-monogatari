""" Reinsertion script for 46 Okunen Monogatari: The Shinka Ron."""

# Environment message pointers aren't getting adjusted correctly.
# Either way, the spaces in front of the "volcanic currrents" message are unsightly.

# Moving overflow to the error block/spare block.
    # Done?) Actually figure out where they are
    # Done) In the rom, replace the jp text with equivalent number of spaces
    # 2) Replace all of the error block with equivalent number of spaces
    # 3) Place all the text in the error block (what about control codes???)
    # 4) Rewrite all the pointer values to point to new locations

from __future__ import division
import os
import math
from binascii import unhexlify
from shutil import copyfile
from collections import OrderedDict
from openpyxl import load_workbook

from utils import pack, get_current_block, file_to_hex_string
from utils import sjis_to_hex_string, ascii_to_hex_string
from rominfo import file_blocks, file_location, file_length, pointer_constants
from rominfo import creature_block, spare_block

SCRIPT_DIR = os.path.dirname(__file__)
SRC_PATH = os.path.join(SCRIPT_DIR, 'intermediate_roms')
DEST_PATH = os.path.join(SCRIPT_DIR, 'patched_roms')

SRC_ROM_PATH = os.path.join(SRC_PATH, "46 Okunen Monogatari - The Sinkaron (J) A user.FDI")
DEST_ROM_PATH = os.path.join(DEST_PATH, "46 Okunen Monogatari - The Sinkaron (J) A user.FDI")

DUMP_XLS = "shinkaron_dump_test.xlsx"
POINTER_XLS = "shinkaron_pointer_dump.xlsx"

FILES_TO_TRANSLATE = ['ST1.EXE', 'SINKA.DAT']

FULL_ROM_STRING = file_to_hex_string(SRC_ROM_PATH)


def get_translations(gamefile):
    """For the given file, return a diciotnary of its translations from the dump."""
    trans = OrderedDict() # translations[offset] = (japanese, english)
    
    workbook = load_workbook(DUMP_XLS)
    worksheet = workbook.get_sheet_by_name(gamefile)

    total_rows = total_replacements = 0
    overflow_block_lo, overflow_block_hi = spare_block[gamefile]  # Doesn't need translations.

    for row in worksheet.rows[1:]:  # Skip the first row, it's just labels
        total_rows += 1
        offset = int(row[0].value, 16)

        if (offset >= overflow_block_lo) and (offset <= overflow_block_hi):
            continue

        japanese = row[2].value
        english = row[4].value

        if english:
            total_replacements += 1
        else:
            english = ""

        trans[offset] = (japanese, english)

    return trans


def get_dat_translations(gamefile):
    """Return a translation dict for the SINKA.DAT or SEND.DAT files."""
    trans = []
    workbook = load_workbook(DUMP_XLS)
    worksheet = workbook.get_sheet_by_name(gamefile)

    total_rows = total_replacements = 0
    for row in worksheet.rows[1:]:
        total_rows += 1
        japanese = row[2].value
        english = row[4].value
        if english:
            total_replacements += 1
        else:
            english = ""
        trans.append((japanese, english))
    return trans


def get_pointers(gamefile):
    """For the file, return a dict of all the pointers."""
    ptrs = OrderedDict()              # text_offset: pointer_offset

    pointer_wb = load_workbook(POINTER_XLS)
    pointer_sheet = pointer_wb.get_sheet_by_name("Sheet1") 

    for row in pointer_sheet.rows:
        if row[0].value != gamefile:
            continue                          # Access ptrs for the current file only.

        text_offset = int(row[1].value, 16)
        pointer_offset = int(row[2].value, 16)
        if text_offset in ptrs:
            ptrs[text_offset].append(pointer_offset)
        else:
            ptrs[text_offset] = [pointer_offset]

    return ptrs


def get_file_strings():
    """Grab file strings for each gamefile."""
    file_strings = {}
    for gamefile in FILES_TO_TRANSLATE:
        start = file_location[gamefile]
        length = file_length[gamefile]
        file_strings[gamefile] = file_to_hex_string(SRC_ROM_PATH, start, length)
    return file_strings


def get_block_strings(gamefile):
    """For a certain gamefile, grab bytestrings for each block."""
    blocks = []
    for block in file_blocks[gamefile]:
        lo, hi = block
        block_length = hi - lo
        block_start = file_location[gamefile] + lo

        blocks.append(file_to_hex_string(SRC_ROM_PATH, block_start, block_length))
    return blocks


def edit_pointer(file, text_location, diff, file_string):
    """Increment or decrement all pointers pointing to a single text location."""
    if diff == 0:
        return file_string

    pointer_constant = pointer_constants[file]
    pointer_locations = pointers[text_location]
    #print "This text has", len(pointer_locations), "depending on it"

    patched_file_string = file_string
    for ptr in pointer_locations:
        print "text is at", hex(text_location), "so edit pointer at", hex(ptr), "with diff", diff

        old_value = text_location - pointer_constant
        old_bytes = pack(old_value)
        old_bytestring = "{:02x}".format(old_bytes[0]) +"{:02x}".format(old_bytes[1])

        location_in_file_string = ptr*2
        rom_bytestring = ORIGINAL_FILE_STRINGS[file][location_in_file_string:location_in_file_string+4]
        assert old_bytestring == rom_bytestring, 'Pointer bytestring not equal to value in rom'

        #print hex(pointer_location)
        print "old:", old_value, old_bytes, old_bytestring

        new_value = old_value + diff

        new_bytes = pack(new_value)
        new_bytestring = "{:02x}".format(new_bytes[0]) + "{:02x}".format(new_bytes[1])
        print "new:", new_value, new_bytes, new_bytestring

        location_in_string = ptr * 2

        old_slice = file_string[location_in_string:]
        new_slice = old_slice.replace(old_bytestring, new_bytestring, 1)
        patched_file_string = patched_file_string.replace(old_slice, new_slice, 1)

    return patched_file_string


def edit_pointers_in_range(file, file_string, (lo, hi), diff):
    """Edit all the pointers in the (lo, hi) range."""
    #print "lo hi", hex(lo), hex(hi)
    for n in range(lo+1, hi+1):
        if n in pointers:
            file_string = file_strings[file]
            patched_file_string = edit_pointer(file, n, diff, file_string)
            file_strings[file] = patched_file_string
    return file_strings[file]


def edit_text(file, translations):
    """Replace each japanese string with the translated english string."""

    creature_block_lo, creature_block_hi = creature_block[file]

    pointer_diff = 0
    previous_text_offset = file_blocks[file][0][0]
    previous_replacement_offset = 0
    block_string = file_blocks[file][0]
    previous_text_block = 0
    current_text_block = 0
    current_block_start, current_block_end = file_blocks[file][0]
    is_overflowing = False

    overflow_bytestrings = OrderedDict()

    for original_location, (jp, eng) in translations.iteritems():
        file_strings[file] = edit_pointers_in_range(file, file_strings[file], (previous_text_offset, original_location), pointer_diff)
        print hex(original_location), pointer_diff
        current_text_block = get_current_block(original_location, file)
        if current_text_block != previous_text_block:
            pointer_diff = 0
            previous_replacement_offset = 0
            is_overflowing = False
            block_string = block_strings[current_text_block]
            current_block_start, current_block_end = file_blocks[file][current_text_block]
        if current_text_block:
            # Does not update if the current_block is 0... since 0 is falsy.
            # Can't do "or if current_text_bllock == 0", since that's "true or false" (always true)
            previous_text_block = current_text_block

        previous_text_offset = original_location

        jp_bytestring = sjis_to_hex_string(jp)
        eng_bytestring = ascii_to_hex_string(eng)

        if eng_bytestring:
            new_text_offset = original_location + len(eng_bytestring)//2 + pointer_diff
            # The bytestring is twice as long as the number of bytes.
        else:
            new_text_offset = original_location + len(jp_bytestring)//2 + pointer_diff

        if new_text_offset > current_block_end and not is_overflowing:
            print hex(new_text_offset), "overflows past", hex(current_block_end)
            print eng
            is_overflowing = True
            # TODO: Here's the problem. Some pointers point to something a few control codes before the text.
            # So I need to calculate start_in_block as the pointer right before its current value...
            # Otherwise, the pointers won't get readjusted!
            start_in_block = (original_location - current_block_start)*2
            overflow_bytestring = original_block_strings[current_text_block][start_in_block:]
            # Store the start and end of the overflow bytestring, 
            # to make sure all pointers are adjusted in the range.
            overflow_lo, overflow_hi = original_location, current_block_end

            overflow_bytestrings[(overflow_lo, overflow_hi)] = overflow_bytestring

        if eng == "":
            continue

        if is_overflowing:
            print hex(original_location), "is part of an overflow"
            eng = ""

        # Recalculate this in case eng got erased.
        eng_bytestring = ascii_to_hex_string(eng)

        this_string_diff = ((len(eng_bytestring) - len(jp_bytestring)) // 2)   # since 2 chars per byte

        if (original_location >= creature_block_lo) and (original_location <= creature_block_hi):
            if this_string_diff <= 0:
                eng_bytestring += "00"*(this_string_diff*(-1))
            else:
                jp_bytestring += "00"*(this_string_diff)

            this_string_diff = ((len(eng_bytestring) - len(jp_bytestring)) // 2)

        pointer_diff += this_string_diff

        block_string = block_strings[current_text_block]
        old_slice = block_string[previous_replacement_offset*2:]
        i = old_slice.index(jp_bytestring)//2

        new_slice = old_slice.replace(jp_bytestring, eng_bytestring, 1)
        j = block_strings[current_text_block].index(old_slice)
        new_block_string = block_strings[current_text_block].replace(old_slice, new_slice, 1)
        block_strings[current_text_block] = new_block_string

        previous_replacement_offset += i

    patched_file_string = move_overflow(file, file_strings[file], overflow_bytestrings)


    patched_file_string = pad_text_blocks(file, block_strings, file_strings[file])
    # Should this take patched_file_string as an argument instead?

    return patched_file_string


def pad_text_blocks(file, block_strings, file_string):
    """Add ascii spaces to the end of each block to preserve the function code."""
    patched_file_string = file_string
    for i, blk in enumerate(block_strings):
        # if block is too short, negative; too long, positive
        block_diff = len(blk) - len(original_block_strings[i])
        #print len(original_block_strings[i]), len(blk)
        print "padding block #", i
        print block_diff
        assert block_diff <= 0, 'Block ending in %s is too long' % hex(file_blocks[file][i][1])
        if block_diff < 0:
            number_of_spaces = ((-1)*block_diff)//2
            inserted_spaces_index = file_blocks[file][i][1]
            blk += '20' * number_of_spaces       # Fill it up with ascii 20 (space)
            print number_of_spaces, "added at", hex(inserted_spaces_index)

        j = ORIGINAL_FILE_STRINGS[file].index(original_block_strings[i])
        j = patched_file_string.index(original_block_strings[i])
        patched_file_string = patched_file_string.replace(original_block_strings[i], blk, 1)

    return patched_file_string


def move_overflow(file, file_string, overflow_bytestrings):
    """Insert the overflow strings in the spare block, and reroute their pointers."""
    spare_block_lo, spare_block_hi = spare_block[file]
    spare_block_string = ''
    #location_in_spare_block = 0
    for (lo, hi), bytestring in overflow_bytestrings.iteritems():
        # The first pointer must be adjusted to point to the beginning of the spare block.
        #last_pointer_adjustment = lo-1
        pointer_diff = (spare_block_lo - lo)
        # Find all the translations that need to be applied.
        trans = OrderedDict()
        for i in range(lo, hi):
            previous_text_location = lo
            if i in translations:
                print "translating overflow"
                print hex(i), pointer_diff
                trans[i] = translations[i]
                jp, eng = trans[i]
                print eng

                jp_bytestring = sjis_to_hex_string(jp)
                eng_bytestring = ascii_to_hex_string(eng)

                this_string_diff = ((len(eng_bytestring) - len(jp_bytestring)) // 2)

                j = bytestring.index(jp_bytestring)
                bytestring = bytestring.replace(jp_bytestring, eng_bytestring)
                print "editing pointers between", hex(previous_text_location), hex(i)
                edit_pointers_in_range(file, file_string, (previous_text_location, i), pointer_diff)
                # TODO: Plus this pointer isn't getting the proper adjustment anyway...

                spare_block_string += bytestring

                #print spare_block_string

                previous_text_location = i
                pointer_diff += this_string_diff

    block_strings[-1] = spare_block_string
    original_block_string = original_block_strings[-1]
    file_string = file_string.replace(original_block_string, spare_block_string)
    return file_string


def edit_dat_text(gamefile, file_string):
    """Edit text for SINKA.DAT or SEND.DAT. Do not adjust pointers."""
    trans = get_dat_translations(gamefile)

    patched_file_string = file_string

    for (jp, eng) in trans:
        if eng == "":
            continue
        jp_bytestring = sjis_to_hex_string(jp)
        eng_bytestring = ascii_to_hex_string(eng)

        patched_file_string = patched_file_string.replace(jp_bytestring, eng_bytestring, 1)
    return patched_file_string


def change_starting_map(map_number):
    """Cheats! Load a different map instead of thelodus sea."""
    starting_map_number_location = 0xedaa + file_location['ST1.EXE']
    new_map_bytes = str(map_number).encode()
    with open(DEST_ROM_PATH, 'rb+') as f:
        f.seek(starting_map_number_location)
        f.write(new_map_bytes)

if __name__ == '__main__':
    copyfile(SRC_ROM_PATH, DEST_ROM_PATH)
    ORIGINAL_FILE_STRINGS = get_file_strings()
    file_strings = ORIGINAL_FILE_STRINGS.copy()


    for file in FILES_TO_TRANSLATE:
        if file == "SINKA.DAT" or file == 'SEND.DAT':
            # Edit the file separately. That'll have to do for now.
            dat_path = os.path.join(SRC_PATH, file)
            dest_dat_path = os.path.join(DEST_PATH, file)
            dat_file_string = file_to_hex_string(dat_path)

            patched_dat_file_string = edit_dat_text(file, dat_file_string)

            with open(dest_dat_path, "wb") as output_file:
                data = unhexlify(patched_dat_file_string)
                output_file.write(data)
            continue

        translations = get_translations(file)
        pointers = get_pointers(file)

        # Then get individual strings of each text block, and put them in a list.
        block_strings = get_block_strings(file)
        original_block_strings = list(block_strings)   
        # Needs to be copied - simple assignment would just pass the ref.

        patched_file_string = edit_text(file, translations)

        i = FULL_ROM_STRING.index(ORIGINAL_FILE_STRINGS[file])
        FULL_ROM_STRING = FULL_ROM_STRING.replace(ORIGINAL_FILE_STRINGS[file], patched_file_string)
        # Whoops, allegedly constant FULL_ROM_STRING changes...

        # Write the data to the patched file.
        with open(DEST_ROM_PATH, "wb") as output_file:
            data = unhexlify(FULL_ROM_STRING)
            output_file.write(data)

        # Write the translated file alone to the file too.
        dest_file_path = os.path.join(DEST_PATH, file)
        with open(dest_file_path, "wb") as output_file:
            data = unhexlify(patched_file_string)
            output_file.write(data)

        # Get some quick stats on reinsertion progress.
        translated_strings = 0
        total_strings = len(translations)
        for _, eng in translations.itervalues():
            if eng:
                translated_strings += 1

        translation_percent = int(math.floor((translated_strings / total_strings) * 100))
        print file, str(translation_percent), "% complete"

    change_starting_map(101)

# 100: open water, volcano cutscene immediately, combat
# 101: caves, hidden hemicyclapsis, Gaia's Heart in upper right
# 102: OOB cladoselache cave
# 103: OOB ???
# 104: OOB Gaia portal
# 105: (default) thelodus sea
# 200: chapter 2 world map
# 201: super glitchy salamander cave
# 202: useful! take one step, die from fresh water, respawn as an Ichthyostega!
# goes until 209.
# 300: black screen. It's on a different disk, of course...