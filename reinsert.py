""" Reinsertion script for 46 Okunen Monogatari: The Shinka Ron."""

from collections import OrderedDict

from utils import SRC_ROM_PATH, DEST_ROM_PATH
from utils import get_current_block
from utils import sjis_to_hex_string, sjis_to_hex_string_preserve_spaces 
from utils import ascii_to_hex_string
from cheats import change_starting_map

from disk import Disk, EXEFile, DATFile

FILES_TO_TRANSLATE = ['ST1.EXE', 'ST2.EXE', 'ST3.EXE', 'ST4.EXE', 'ST5.EXE', 'ST5S1.EXE',
                      'ST5S2.EXE', 'ST5S3.EXE', 'ST6.EXE', 'OPENING.EXE'] #'SINKA.DAT', 
                      #'ENDING.EXE', 'SEND.DAT']

# for testing the oh-so-problematic Ch5:
#FILES_TO_TRANSLATE = ['ST5.EXE', 'ST5S1.EXE', 'ST5S2.EXE', 'ST5S3.EXE']

def edit_text(block):
    """Replace each japanese string with the translated english string."""
    pointer_diff = 0
    previous_text_offset = block.start
    previous_replacement_offset = 0
    is_overflowing = False

    for trans in block.translations:
        if is_overflowing:
            # Leave immediately; the rest of this string is in gamefile.overflow_bytestrings now.
            break

        jp_bytestring = sjis_to_hex_string(trans.japanese)
        eng_bytestring = ascii_to_hex_string(trans.english)

        # jp_bytestring might include ASCII; if it's not found, try the ascii preserving method.
        try:
            j = block.blockstring.index(jp_bytestring)
        except ValueError: # substring not found
            jp_bytestring = sjis_to_hex_string_preserve_spaces(trans.japanese)

        if eng_bytestring:
            new_text_offset = trans.location + len(eng_bytestring)//2 + pointer_diff
        else:
            new_text_offset = trans.location + len(jp_bytestring)//2 + pointer_diff

        if new_text_offset >= block.stop:
            is_overflowing = True
            # Pointers usually point to control codes before the text. So look for a recent pointer.
            # But don't backtrack as far as previous_text_offset (maybe already translated)
            recent_pointer = block.gamefile.most_recent_pointer(previous_text_offset, trans.location)

            start_in_block = (recent_pointer - block.start)*2
            overflow_bytestring = block.original_blockstring[start_in_block:]
            # Store the start and end of the overflow bytestring, 
            # to make sure all pointers are adjusted in the range.
            overflow_lo, overflow_hi = recent_pointer, block.stop
           
            block.gamefile.overflow_bytestrings[(overflow_lo, overflow_hi)] = overflow_bytestring

        block.gamefile.edit_pointers_in_range((previous_text_offset, trans.location), pointer_diff)

        previous_text_offset = trans.location

        # "eng" is an ugly way of doing this. But we want to be able to do the thing where, if
        # it's overflowing, do a "translation" of the overflow bytestring into "".
        # If we set trans.english to "", it wouldn't get translated later.
        # So use a separate "eng" variable which can be english or blank, but don't lose data.
        eng = trans.english
        if eng == "":
            # No replacement necessary - pointers are edited, so we're done here.
            continue

        if is_overflowing:
            # Then we want to blank the entire overflow bytestring.
            # So use the rest of the function already there to do that.
            eng = ""
            jp_bytestring = overflow_bytestring

        # Recalculate in case it got altered due to overflow.
        eng_bytestring = ascii_to_hex_string(eng)
        this_string_diff = (len(eng_bytestring) - len(jp_bytestring)) // 2

        # Pad creature name strings.
        if block.is_creature:
            if block.start <= trans.location <= block.stop:
                if this_string_diff <= 0:
                    eng_bytestring += "00"*(this_string_diff*(-1))
                else:
                    jp_bytestring += "00"*(this_string_diff)
                this_string_diff = (len(eng_bytestring) - len(jp_bytestring)) // 2
                assert this_string_diff == 0, 'creature diff not 0'

        pointer_diff += this_string_diff

        old_slice = block.blockstring[previous_replacement_offset*2:]
        i = old_slice.index(jp_bytestring)//2
        previous_replacement_offset += i//2
        new_slice = old_slice.replace(jp_bytestring, eng_bytestring, 1)

        #j = block.blockstring.index(old_slice)
        block.blockstring = block.blockstring.replace(old_slice, new_slice, 1)

    block.incorporate()


if __name__ == '__main__':
    DiskA = Disk(SRC_ROM_PATH, DEST_ROM_PATH)

    for filename in FILES_TO_TRANSLATE:
        if filename in ('SINKA.DAT', 'SEND.DAT'):
            gamefile = DATFile(DiskA, filename)
            gamefile.translate()
            gamefile.write()

        else:
            gamefile = EXEFile(DiskA, filename)

            # Then get individual strings of each text block, and put them in a list.
            #block_strings = gamefile.blocks
            #original_block_strings = list(block_strings)

            for block in gamefile.blocks:
                edit_text(block)
            gamefile.move_overflow()
            gamefile.incorporate()
            gamefile.write()
            gamefile.report_progress()

    DiskA.write()

    #change_starting_map('ST1.EXE', 100)
    #change_starting_map('ST5.EXE', 600)

# 100: open water, volcano cutscene immediately, combat
# 101: caves, hidden hemicyclapsis, Gaia's Heart in upper right
# 202: useful! take one step, die from fresh water, respawn as an Ichthyostega!
# 204: mountain, right near the top! easy access to combat, cut scenes - plus fish equivs of animals

# testing new ch5 starting maps:
# 600: ch6 world map; can't use menus?; dying (at imp guy in africa, ch5) sends you to glitch land ch5