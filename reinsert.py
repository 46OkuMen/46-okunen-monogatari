""" Reinsertion script for 46 Okunen Monogatari: The Shinka Ron."""

from __future__ import division
import os
from math import floor
from binascii import unhexlify
from shutil import copyfile
from collections import OrderedDict
from openpyxl import load_workbook

from utils import DUMP_XLS, POINTER_XLS, SRC_PATH, DEST_PATH, SRC_ROM_PATH, DEST_ROM_PATH
from utils import pack, get_current_block, file_to_hex_string
from utils import sjis_to_hex_string, sjis_to_hex_string_preserve_spaces 
from utils import ascii_to_hex_string
from utils import compare_strings
from rominfo import file_blocks, file_location, file_length, pointer_constants
from rominfo import creature_block, spare_block, CHAPTER_FIVE_FILES
from cheats import change_starting_map

#FILES_TO_TRANSLATE = ['ST1.EXE', 'ST2.EXE', 'ST3.EXE', 'ST4.EXE', 'ST5.EXE', 'ST5S1.EXE',
#                      'ST5S2.EXE', 'ST5S3.EXE', 'ST6.EXE', 'SINKA.DAT']
FILES_TO_TRANSLATE = ['ST5.EXE', 'ST5S1.EXE', 'ST5S2.EXE', 'ST5S3.EXE', 'SINKA.DAT']
#FILES_TO_TRANSLATE = ['ST5S1.EXE', ]

FULL_ROM_STRING = file_to_hex_string(SRC_ROM_PATH)

def get_translations(gamefile):
    """For the given file, return a diciotnary of its translations from the dump."""
    trans = OrderedDict()    # translations[offset] = (japanese, english)
    
    workbook = load_workbook(DUMP_XLS)
    worksheet = workbook.get_sheet_by_name(gamefile)

    total_rows = total_replacements = 0

    for row in worksheet.rows[1:]:  # Skip the first row, it's just labels
        total_rows += 1
        offset = int(row[0].value, 16)

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

    patched_file_string = file_string
    for ptr in pointer_locations:
        #print "text is at", hex(text_location), "so edit pointer at", hex(ptr), "with diff", diff

        old_value = text_location - pointer_constant
        old_bytes = pack(old_value)
        old_bytestring = "{:02x}".format(old_bytes[0]) +"{:02x}".format(old_bytes[1])

        location_in_string = ptr*2
        rom_bytestring = file_string[location_in_string:location_in_string+4]
        if old_bytestring != rom_bytestring:
            print "This one got edited before; make sure it's right"
        #assert old_bytestring == rom_bytestring, 'Pointer bytestring %s not equal to value in rom %s' % (old_bytestring, rom_bytestring)

        #print hex(pointer_location)
        #print "old:", old_value, old_bytes, old_bytestring

        new_value = old_value + diff

        new_bytes = pack(new_value)
        new_bytestring = "{:02x}".format(new_bytes[0]) + "{:02x}".format(new_bytes[1])
        #print "new:", new_value, new_bytes, new_bytestring

        #print location_in_string
        #j = rom_bytestring.index(old_bytestring)
        #if j > 0:
        #    print j, "is in a weird place"

        patched_file_string = patched_file_string[0:location_in_string] + new_bytestring + patched_file_string[location_in_string+4:]

    return patched_file_string


def edit_pointers_in_range(gamefile, file_string, (start, stop), diff):
    """Edit all the pointers in the (start, stop) range."""
    if diff == 0:
        return file_strings[gamefile]
    for n in range(start+1, stop+1):
        if n in pointers:
            file_string = file_strings[gamefile]
            patched_file_string = edit_pointer(gamefile, n, diff, file_string)
            file_strings[gamefile] = patched_file_string
    return file_strings[gamefile]


def most_recent_pointer(lo, hi):
    """Return the highest offset with a pointer in the given range."""
    for n in reversed(range(lo, hi+1)):
        if n in pointers:
            return n
    # If there are no other pointers, just return the hi value.
    return hi


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
        #print hex(original_location), pointer_diff
        current_text_block = get_current_block(original_location, file)
        if current_text_block != previous_text_block:
            pointer_diff = 0
            previous_replacement_offset = 0
            is_overflowing = False
            block_string = block_strings[current_text_block]
            current_block_start, current_block_end = file_blocks[file][current_text_block]
        if current_text_block:
            # Does not update if the current_block is 0... since 0 is falsy.
            # Can't do "or if current_text_block == 0", since that's "true or false" (always true)
            previous_text_block = current_text_block

        # This is new. If I'm rewriting the whole overflow bytestring at once,
        # skip the rest of the translations in the overflow bytestring since it already got rewritten.
        # All we need to do is check if we're in a new block yet.
        if is_overflowing:
            print "skipping string at %s due to overflow" % hex(original_location)
            continue

        jp_bytestring = sjis_to_hex_string(jp)
        eng_bytestring = ascii_to_hex_string(eng)

        # If the jp string includes ASCII spaces, it will not be found.
        # So use the different hex string-producing method.
        try:
            j = block_strings[current_text_block].index(jp_bytestring)
        except ValueError: # substring not found
            jp_bytestring = sjis_to_hex_string_preserve_spaces(jp)

        if eng_bytestring:
            new_text_offset = original_location + len(eng_bytestring)//2 + pointer_diff
        else:
            new_text_offset = original_location + len(jp_bytestring)//2 + pointer_diff

        #if eng:
        #    try:
        #        print eng, "ends at", hex(new_text_offset)
        #    except UnicodeEncodeError:
        #        print "unicode error, but it ends at", hex(new_text_offset)


        if new_text_offset >= current_block_end:
            is_overflowing = True
            # Here's the problem. Some pointers point to something a few control codes before the text.
            # So I need to calculate start_in_block as the pointer right before its current value...
            # Otherwise, the other pointers won't get adjusted.

            #print "It's overflowing"
            current_block_length = len(block_strings[current_text_block])//2

            # A lot of times the overflow text will be preceded by a <LN> which has a different pointer offset.
            # Backtrack to the most recent offset with a pointer.
            # But don't backtrack as far as previous_text_offset, it may have already been translated...
            recent_pointer = most_recent_pointer(previous_text_offset+1, original_location)
            #print "original location:", hex(original_location)
            #print "recent pointer:", hex(recent_pointer)

            start_in_block = (recent_pointer - current_block_start)*2    # start position in the blockstring.
            overflow_bytestring = original_block_strings[current_text_block][start_in_block:]
            # Store the start and end of the overflow bytestring, 
            # to make sure all pointers are adjusted in the range.
            #overflow_lo, overflow_hi = original_location, current_block_end
            overflow_lo, overflow_hi = recent_pointer, current_block_end
            #print "%s < %s" % ((overflow_lo - current_block_start), len(original_block_strings[current_text_block])//2)
            #assert overflow_lo < current_block_end
            #assert len(original_block_strings[current_text_block])//2 > (overflow_lo - current_block_start)

            overflow_bytestrings[(overflow_lo, overflow_hi)] = overflow_bytestring

        if not is_overflowing:
            file_strings[file] = edit_pointers_in_range(file, file_strings[file], 
                    (previous_text_offset, original_location), pointer_diff)

        previous_text_offset = original_location

        if eng == "":
            # No replacement necessary - leave the original jp.
            continue

        if is_overflowing:
            # Then we want to blank the entire overflow bytestring.
            # So use the rest of the function already there to do that.
            eng = ""
            #jp = overflow_bytestring
            jp_bytestring = overflow_bytestring
            #previous_text_offset = recent_pointer-1

        # Recalculate in case it got altered due to overflow.
        eng_bytestring = ascii_to_hex_string(eng)

        this_string_diff = (len(eng_bytestring) - len(jp_bytestring)) // 2

        if (original_location >= creature_block_lo) and (original_location <= creature_block_hi):
            if this_string_diff <= 0:
                eng_bytestring += "00"*(this_string_diff*(-1))
            else:
                jp_bytestring += "00"*(this_string_diff)

            this_string_diff = ((len(eng_bytestring) - len(jp_bytestring)) // 2)

        pointer_diff += this_string_diff

        block_string = block_strings[current_text_block]
        old_slice = block_string[previous_replacement_offset*2:]
        # TODO: Why are wrong replacements still happening?
        try:
            i = old_slice.index(jp_bytestring)//2
            previous_replacement_offset += i//2
        except ValueError:
            print jp_bytestring
            print old_slice
            print "Can't find the string at:", hex(original_location)
            print "It's looking starting at:", hex((block_string.index(old_slice)//2 + ((current_block_start))))
            print "the english string", eng, "is causing problems"

        new_slice = old_slice.replace(jp_bytestring, eng_bytestring, 1)
        #print "diff between slices:", (len(new_slice) - len(old_slice))//2

        j = block_strings[current_text_block].index(old_slice)
        new_block_string = block_strings[current_text_block].replace(old_slice, new_slice, 1)
        block_strings[current_text_block] = new_block_string
        #print "after replacement, block length is", len(new_block_string)//2

    if file in spare_block:
        patched_file_string = move_overflow(file, file_strings[file], overflow_bytestrings)

    patched_file_string = pad_text_blocks(file, block_strings, file_strings[file])
    # Should this take patched_file_string as an argument instead?

    return patched_file_string


def pad_text_blocks(gamefile, block_strings, file_string):
    """Add ascii spaces to the end of each block to preserve the function code."""
    patched_file_string = file_string
    for i, blk in enumerate(block_strings):
        # if block is too short, negative; too long, positive
        block_diff = len(blk) - len(original_block_strings[i])
        if block_diff > 0:
            print block_diff
            print blk
            #with open('too_long_block.txt', 'wb+') as f:
            #    f.write(blk)
        assert block_diff <= 0, 'Block ending in %s is too long' % hex(file_blocks[gamefile][i][1])
        if block_diff < 0:
            number_of_spaces = ((-1)*block_diff)//2
            inserted_spaces_index = file_blocks[gamefile][i][1]
            blk += '20' * number_of_spaces       # Fill it up with ascii 20 (space)

        j = ORIGINAL_FILE_STRINGS[gamefile].index(original_block_strings[i])
        try:
            j = patched_file_string.index(original_block_strings[i])
        except ValueError:
            #print "looking for:"
            #print original_block_strings[i]
            start, stop = file_blocks[gamefile][i]
            #print "in:"
            #print patched_file_string[start*2:stop*2]
            for n in compare_strings(original_block_strings[i], patched_file_string[start*2:stop*2]):
                print "look at offset", hex(n + file_blocks[gamefile][i][0]), "probably treated control codes as text"
        patched_file_string = patched_file_string.replace(original_block_strings[i], blk, 1)

    return patched_file_string


def move_overflow(file, file_string, overflow_bytestrings):
    """Insert the overflow strings in the spare block, and reroute their pointers."""
    spare_block_lo, spare_block_hi = spare_block[file]
    spare_length = spare_block_hi - spare_block_lo
    spare_block_string = ''
    #location_in_spare_block = 0
    for (lo, hi), bytestring in overflow_bytestrings.iteritems():
        # The first pointer must be adjusted to point to the beginning of the spare block.
        pointer_diff = (spare_block_lo - lo) + len(spare_block_string)//2
        # Find all the translations that need to be applied.
        trans = OrderedDict()
        previous_text_location = lo
        for i in range(lo, hi):
            if i in translations:
                print "translating overflow"
                print "previous_text_location:", hex(previous_text_location)
                print hex(i), pointer_diff
                trans[i] = translations[i]
                japanese, english = trans[i]
                print english

                jp_bytestring = sjis_to_hex_string(japanese)
                eng_bytestring = ascii_to_hex_string(english)

                this_string_diff = (len(eng_bytestring) - len(jp_bytestring)) // 2

                j = bytestring.index(jp_bytestring)
                bytestring = bytestring.replace(jp_bytestring, eng_bytestring)
                edit_pointers_in_range(file, file_string, (previous_text_location-1, i), pointer_diff)
                previous_text_location = i
                pointer_diff += this_string_diff

        spare_block_string += bytestring

    # TODO: This isn't quite the sapre block, it's just the last block... just as a note.
    # That's probably at least one of the problems for OPENING.EXE...
    assert len(spare_block_string)//2 <= spare_length
    block_strings[-1] = spare_block_string
    original_block_string = original_block_strings[-1]
    file_string = file_string.replace(original_block_string, spare_block_string)
    return file_string


def edit_dat_text(gamefile, file_string):
    """Edit text for SINKA.DAT or SEND.DAT. Does not adjust pointers."""
    trans = get_translations(gamefile)

    patched_file_string = "" + file_string

    for _, (japanese, english) in trans.iteritems():
        if english == "":
            continue
        jp_bytestring = sjis_to_hex_string(japanese)
        eng_bytestring = ascii_to_hex_string(english)

        patched_file_string = patched_file_string.replace(jp_bytestring, eng_bytestring, 1)
    return patched_file_string

#def print_progress_stats(progress):
#    """Report on reinsertion progress."""
    #for file, (n, d) in progress.iteritems():
        # print 


if __name__ == '__main__':
    while True:
        try:
            copyfile(SRC_ROM_PATH, DEST_ROM_PATH)
            break
        except IOError:
            print "Looks like the game is open. Close it and press enter to continue."
            raw_input()

    ORIGINAL_FILE_STRINGS = get_file_strings()
    file_strings = ORIGINAL_FILE_STRINGS.copy()

    chapter_five_total_strings = 0
    chapter_five_translated_strings = 0


    for gamefile in FILES_TO_TRANSLATE:
        if gamefile in ('SINKA.DAT', 'SEND.DAT'):
            dat_path = os.path.join(SRC_PATH, gamefile)
            dest_dat_path = os.path.join(DEST_PATH, gamefile)
            dat_file_string = file_to_hex_string(dat_path)

            translations = get_translations(gamefile)

            patched_dat_file_string = edit_dat_text(gamefile, dat_file_string)

            with open(dest_dat_path, "wb") as output_file:
                data = unhexlify(patched_dat_file_string)
                output_file.write(data)

        else:
            translations = get_translations(gamefile)
            pointers = get_pointers(gamefile)

            # Then get individual strings of each text block, and put them in a list.
            block_strings = get_block_strings(gamefile)
            original_block_strings = list(block_strings)
            # Needs to be copied like this - simple assignment would just pass the ref.

            patched_file_string = edit_text(gamefile, translations)

            i = FULL_ROM_STRING.index(ORIGINAL_FILE_STRINGS[gamefile])
            FULL_ROM_STRING = FULL_ROM_STRING.replace(ORIGINAL_FILE_STRINGS[gamefile], 
                                                      patched_file_string)

            # Write the data to the patched file.
            with open(DEST_ROM_PATH, "wb") as output_file:
                data = unhexlify(FULL_ROM_STRING)
                output_file.write(data)

            # Write the translated file alone to a new file too.
            dest_file_path = os.path.join(DEST_PATH, gamefile)
            with open(dest_file_path, "wb") as output_file:
                data = unhexlify(patched_file_string)
                output_file.write(data)

        # Get some quick stats on reinsertion progress.
        total_strings = 0
        translated_strings = 0
        for (_, (jp, _)) in translations.iteritems():
            if isinstance(jp, long):
                # .DAT encyclopedia indexes; don't get translated
                pass
            else:
                total_strings += 1

        #total_strings = len(translations)
        for _, eng in translations.itervalues():
            if eng:
                translated_strings += 1

        if gamefile in CHAPTER_FIVE_FILES:
            chapter_five_total_strings += total_strings
            chapter_five_translated_strings += translated_strings

        translation_percent = int(floor((translated_strings / total_strings) * 100))
        print gamefile, str(translation_percent), "% complete",
        print "(%s / %s)" % (translated_strings, total_strings)

        if gamefile == "ST5S3.EXE":
            print "CH5 Total:", int(floor((chapter_five_translated_strings / chapter_five_total_strings) * 100)), "% complete",
            print "(%s / %s)" % (chapter_five_translated_strings, chapter_five_total_strings)

    # Hard to see it, but the cheat calls are outside the "every file" loop.
    #change_starting_map('ST1.EXE', 100)
    #change_starting_map('ST5.EXE', 600)

# 100: open water, volcano cutscene immediately, combat
# 101: caves, hidden hemicyclapsis, Gaia's Heart in upper right
# 202: useful! take one step, die from fresh water, respawn as an Ichthyostega!
# 204: mountain, right near the top! easy access to combat, cut scenes - plus fish equivs of animals
# 300: black screen. It's on a different disk, of course...

# testing new ch5 starting maps:
# 600: ch6 world map; can't use menus?; dying (at imp guy in africa, ch5) sends you to glitch land ch5