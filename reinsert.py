""" Reinsertion script for 46 Okunen Monogatari: The Shinka Ron."""

from __future__ import division
import os
from math import floor
from binascii import unhexlify
from collections import OrderedDict
from openpyxl import load_workbook

from utils import DUMP_XLS, POINTER_XLS, SRC_PATH, DEST_PATH, SRC_ROM_PATH, DEST_ROM_PATH
from utils import pack, get_current_block, file_to_hex_string
from utils import sjis_to_hex_string, sjis_to_hex_string_preserve_spaces 
from utils import ascii_to_hex_string
from utils import compare_strings
from rominfo import file_blocks, file_location, file_length, POINTER_CONSTANT
from rominfo import CREATURE_BLOCK, spare_block, CHAPTER_FIVE_FILES
from cheats import change_starting_map

from disk import Disk, EXEFile, DATFile

FILES_TO_TRANSLATE = ['ST1.EXE', 'ST2.EXE', 'ST3.EXE', 'ST4.EXE', 'ST5.EXE', 'ST5S1.EXE',
                      'ST5S2.EXE', 'ST5S3.EXE', 'ST6.EXE', 'OPENING.EXE', 'SINKA.DAT', 'ENDING.EXE', 'SEND.DAT']
#FILES_TO_TRANSLATE = ['ST5.EXE', 'ST5S1.EXE', 'ST5S2.EXE', 'ST5S3.EXE', 'SINKA.DAT']


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

def edit_pointer(file, text_location, diff):
    """Increment or decrement all pointers pointing to a single text location."""
    if diff == 0:
        return file.filestring

    pointer_constant = POINTER_CONSTANT[file.filename]
    pointer_locations = pointers[text_location]

    patched_file_string = file.filestring
    for ptr in pointer_locations:
        #print "text is at", hex(text_location), "so edit pointer at", hex(ptr), "with diff", diff

        old_value = text_location - pointer_constant
        old_bytes = pack(old_value)
        old_bytestring = "{:02x}".format(old_bytes[0]) +"{:02x}".format(old_bytes[1])

        location_in_string = ptr*2
        rom_bytestring = file.filestring[location_in_string:location_in_string+4]
        if old_bytestring != rom_bytestring:
            print "This one got edited before; make sure it's right"

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


def edit_pointers_in_range(gamefile, (start, stop), diff):
    """Edit all the pointers in the (start, stop) range."""
    if diff == 0:
        return gamefile.filestring
    for n in range(start+1, stop+1):
        if n in pointers:
            gamefile.filestring = edit_pointer(gamefile, n, diff)
    return gamefile.filestring


def most_recent_pointer(lo, hi):
    """Return the highest offset with a pointer in the given range."""
    for n in reversed(range(lo, hi+1)):
        if n in pointers:
            return n
    # If there are no other pointers, just return the hi value.
    return hi


def edit_text(file):
    """Replace each japanese string with the translated english string."""

    creature_block_lo, creature_block_hi = CREATURE_BLOCK[gamefile.filename]

    pointer_diff = 0
    previous_text_offset = file_blocks[gamefile.filename][0][0]
    previous_replacement_offset = 0

    current_block = file.blocks[0]
    block_string = file.blocks[0].blockstring
    #block_index = 0

    previous_text_block = 0
    #current_text_block = 0
    current_block_start, current_block_end = current_block.location
    is_overflowing = False

    overflow_bytestrings = OrderedDict()

    for original_location, (jp, eng) in file.translations.iteritems():
        block_index = get_current_block(original_location, file)
        if block_index != previous_text_block:
            # Reset all relevant variables.
            pointer_diff = 0
            previous_replacement_offset = 0
            is_overflowing = False
            block_string = file.blocks[block_index].blockstring

            current_block_start, current_block_end = file.blocks[block_index].location

        if block_index:
            # Does not update if the current_block is 0... since 0 is falsy.
            # Can't do "or if current_text_block == 0", since that's "true or false" (always true)
            previous_text_block = block_index

        # If I'm rewriting the whole overflow bytestring at once,
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
            j = file.blocks[block_index].blockstring.index(jp_bytestring)
        except ValueError: # substring not found
            jp_bytestring = sjis_to_hex_string_preserve_spaces(jp)

        if eng_bytestring:
            new_text_offset = original_location + len(eng_bytestring)//2 + pointer_diff
        else:
            new_text_offset = original_location + len(jp_bytestring)//2 + pointer_diff

        if new_text_offset >= current_block_end:
            is_overflowing = True
            # Here's the problem. Some pointers point to something a few control codes before the text.
            # So I need to calculate start_in_block as the pointer right before its current value...
            # Otherwise, the other pointers won't get adjusted.

            # A lot of times the overflow text will be preceded by a <LN> which has a different pointer offset.
            # Backtrack to the most recent offset with a pointer.
            # But don't backtrack as far as previous_text_offset, it may have already been translated...
            recent_pointer = most_recent_pointer(previous_text_offset+1, original_location)

            start_in_block = (recent_pointer - current_block_start)*2    # start position in the blockstring.
            overflow_bytestring = file.blocks[block_index].original_blockstring[start_in_block:]
            # Store the start and end of the overflow bytestring, 
            # to make sure all pointers are adjusted in the range.
            overflow_lo, overflow_hi = recent_pointer, current_block_end
           
            overflow_bytestrings[(overflow_lo, overflow_hi)] = overflow_bytestring

        if not is_overflowing:
            file.filestring = edit_pointers_in_range(file, (previous_text_offset, original_location),
                                                    pointer_diff)

        previous_text_offset = original_location

        if eng == "":
            # No replacement necessary - leave the original jp.
            continue

        if is_overflowing:
            # Then we want to blank the entire overflow bytestring.
            # So use the rest of the function already there to do that.
            eng = ""
            jp_bytestring = overflow_bytestring

        # Recalculate in case it got altered due to overflow.
        eng_bytestring = ascii_to_hex_string(eng)

        this_string_diff = (len(eng_bytestring) - len(jp_bytestring)) // 2

        if (original_location >= creature_block_lo) and (original_location <= creature_block_hi):
            if this_string_diff <= 0:
                eng_bytestring += "00"*(this_string_diff*(-1))
            else:
                jp_bytestring += "00"*(this_string_diff)

            this_string_diff = (len(eng_bytestring) - len(jp_bytestring)) // 2

        pointer_diff += this_string_diff

        block_string = file.blocks[block_index].blockstring
        #print jp_bytestring
        #print block_string
        old_slice = block_string[previous_replacement_offset*2:]

        try:
            i = old_slice.index(jp_bytestring)//2
            previous_replacement_offset += i//2
        except ValueError:
            print "Can't find the string at:", hex(original_location)
            print "It's looking starting at:", hex((block_string.index(old_slice)//2 + ((current_block_start))))
            print "the english string", eng, "is causing problems"

        new_slice = old_slice.replace(jp_bytestring, eng_bytestring, 1)

        j = file.blocks[block_index].blockstring.index(old_slice)
        #new_block_string = block_strings[current_text_block].replace(old_slice, new_slice, 1)
        block_string = file.blocks[block_index].blockstring.replace(old_slice, new_slice, 1)
        #block_strings[current_text_block] = new_block_string
        file.blocks[block_index].blockstring = block_string
        # TODO replace this with a write() method.

    # If there's a spare block, fill that shit up.
    if file.filename in spare_block:
        file.filestring = move_overflow(file, overflow_bytestrings)
    else:
        print overflow_bytestrings
        # TODO: This is important. Activate it again later!!
        #assert not overflow_bytestrings, "Things are overflowing but there's no room for them!'"

    #patched_file_string = pad_text_blocks(file, block_strings)
    for blk in file.blocks:
        blk.incorporate()
    # Should this take patched_file_string as an argument instead?

    return file.filestring

"""
def pad_text_blocks(gamefile, block_strings, file_string):
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
"""

def move_overflow(file, overflow_bytestrings):
    """Insert the overflow strings in the spare block, and reroute their pointers."""
    spare_block_lo, spare_block_hi = spare_block[file.filename]
    spare_length = spare_block_hi - spare_block_lo
    spare_block_string = ''

    for (lo, hi), bytestring in overflow_bytestrings.iteritems():
        # TODO: Surely this is a large repetition of functionality????
        # The first pointer must be adjusted to point to the beginning of the spare block.
        pointer_diff = (spare_block_lo - lo) + len(spare_block_string)//2
        # Find all the translations that need to be applied.
        trans = OrderedDict()
        previous_text_location = lo
        for i in [i for i in range(lo, hi) if i in file.translations]:    # TODO: This is... vile
            print "translating overflow"
            print "previous_text_location:", hex(previous_text_location)
            print hex(i), pointer_diff
            trans[i] = file.translations[i]
            japanese, english = trans[i]
            print english

            jp_bytestring = sjis_to_hex_string(japanese)
            eng_bytestring = ascii_to_hex_string(english)

            this_string_diff = (len(eng_bytestring) - len(jp_bytestring)) // 2
            print english
            j = bytestring.index(jp_bytestring)
            bytestring = bytestring.replace(jp_bytestring, eng_bytestring)
            edit_pointers_in_range(file, (previous_text_location-1, i), pointer_diff)
            previous_text_location = i
            pointer_diff += this_string_diff

        spare_block_string += bytestring

    assert len(spare_block_string)//2 <= spare_length
    spare = file.blocks[-1]
    spare.blockstring = spare_block_string
    spare.incorporate()

    return file.filestring


def edit_dat_text(gamefile):
    """Edit text for SINKA.DAT or SEND.DAT. Does not adjust pointers."""
    for (japanese, english) in gamefile.translations:
        if english == "":
            continue
        jp_bytestring = sjis_to_hex_string(japanese)
        eng_bytestring = ascii_to_hex_string(english)

        gamefile.filestring = gamefile.filestring.replace(jp_bytestring, eng_bytestring, 1)
    return gamefile.filestring


if __name__ == '__main__':
    DiskA = Disk(SRC_ROM_PATH, DEST_ROM_PATH)

    #while True:
    #    try:
    ##        DiskA.write()
     #       break
    #    except IOError:
    #        print "Looks like the game is open. Close it and press enter to continue."
    #        raw_input()

    #ORIGINAL_FILE_STRINGS = get_file_strings()
    #file_strings = ORIGINAL_FILE_STRINGS.copy()

    #chapter_five_total_strings = 0
    #chapter_five_translated_strings = 0


    for filename in FILES_TO_TRANSLATE:
        print filename
        if filename in ('SINKA.DAT', 'SEND.DAT'):
            gamefile = DATFile(DiskA, filename)

            #dat_path = os.path.join(SRC_PATH, gamefile)
            #dest_dat_path = os.path.join(DEST_PATH, gamefile)
            #dat_file_string = file_to_hex_string(dat_path)

            # !!use gamefile.src_path, gamefile.dest_path, and gamefile.filestring.

            translations = gamefile.translations

            #patched_dat_file_string = edit_dat_text(gamefile, dat_file_string)
            gamefile.filestring = edit_dat_text(gamefile)

            gamefile.write()

            #with open(gamefile.dest_path, "wb") as output_file:
            #    data = unhexlify(gamefile.filestring)
            #    output_file.write(data)

            # TODO: Whoops, I still need a method to write the file as well, not just to the FDI...

        else:
            gamefile = EXEFile(DiskA, filename)

            pointers = get_pointers(filename)

            # Then get individual strings of each text block, and put them in a list.
            #block_strings = get_block_strings(gamefile)
            block_strings = gamefile.blocks
            original_block_strings = list(block_strings)
            # Needs to be copied like this - simple assignment would just pass the ref.

            patched_file_string = edit_text(gamefile)

            # Replace the original file string with the patched one.
            #i = DiskA.romstring.index(ORIGINAL_FILE_STRINGS[gamefile])
            #DiskA.romstring = DiskA.romstring.replace(ORIGINAL_FILE_STRINGS[gamefile],
            #                                          patched_file_string)

            gamefile.incorporate()
            # Write the changes to the patched disk file.
            DiskA.write()

            # Write the translated file alone to a new file too.
            gamefile.write()

            #dest_file_path = os.path.join(DEST_PATH, gamefile)
            #with open(dest_file_path, "wb") as output_file:
            #    data = unhexlify(patched_file_string)
            #    output_file.write(data)

        # Get some quick stats on reinsertion progress.
        #total_strings = 0
        #translated_strings = 0
        #for (_, (jp, _)) in translations.iteritems():
        #    if isinstance(jp, long):
        #        # .DAT encyclopedia indexes; don't get translated
        #        pass
        #    else:
        #        total_strings += 1#

        #total_strings = len(translations)
        #for _, eng in translations.itervalues():
        #    if eng:
        #        translated_strings += 1

        #if gamefile in CHAPTER_FIVE_FILES:
        #    chapter_five_total_strings += total_strings
        #    chapter_five_translated_strings += translated_strings

        #translation_percent = int(floor((translated_strings / total_strings) * 100))
        #print gamefile, str(translation_percent), "% complete",
        #print "(%s / %s)" % (translated_strings, total_strings)

        #if gamefile == "ST5S3.EXE":
        #    print "CH5 Total:", int(floor((chapter_five_translated_strings / chapter_five_total_strings) * 100)), "% complete",
        #    print "(%s / %s)" % (chapter_five_translated_strings, chapter_five_total_strings)

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