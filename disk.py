"""Classes for the 46 Okunen Monogatari text reinserter."""

from __future__ import division
import os
from binascii import unhexlify
from collections import OrderedDict
from math import floor

from openpyxl import load_workbook

from utils import pack, get_current_block, file_to_hex_string, DUMP_XLS, POINTER_XLS, sjis_to_hex_string, ascii_to_hex_string
from rominfo import file_blocks, file_location, file_length, POINTER_CONSTANT, STARTING_MAP_NUMBER_LOCATION, SPARE_BLOCK, CREATURE_BLOCK

class Disk(object):
    """The main .FDI file for a PC-98 game. Disks have the properties:

    Attributes:
        src_path: A string with the path to the original .FDI.
        dest_path: A string with the path to the patched .FDI.
        original_romstring: A hex string of the entire file. Don't change it!
        romstring: A hex string of the entire file. Change this!

    Methods:
        write(): Write the patched bytes to dest_path.

        """ 

    def __init__(self, src_path, dest_path, files_to_translate):
        self.src_path = src_path
        self.dest_path = dest_path

        self.dest_dir = os.path.abspath(os.path.join(dest_path, os.pardir))

        self.original_romstring = file_to_hex_string(src_path)
        self.romstring = "" + self.original_romstring

        self.gamefiles = []
        for filename in files_to_translate:
            if filename.endswith('.EXE'):
                self.gamefiles.append(EXEFile(self, filename))
            elif filename.endswith('.DAT'):
                self.gamefiles.append(DATFile(self, filename))

    def translate(self):
        """Perform translation and reinsertion."""
        for gamefile in self.gamefiles:
            if gamefile.filename.endswith('DAT'):
                gamefile.translate()
                gamefile.write()
            else:
                for block in gamefile.blocks:
                    block.edit_text()
                gamefile.move_overflow()
                gamefile.incorporate()
                gamefile.write()
                gamefile.report_progress()
        self.write()

    def write(self):
        """Write the patched bytes to a new FDI."""
        data = unhexlify(self.romstring)
        with open(self.dest_path, 'wb') as fileopen:
            fileopen.write(data)


class Gamefile(object):
    """All files in a disk that need editing."""

    def __init__(self, disk, filename):
        self.filename = filename
        self.disk = disk
        self.location = file_location[filename]
        self.length = file_length[filename]

        self.original_filestring = file_to_hex_string(disk.src_path, self.location, self.length)
        self.filestring = "" + self.original_filestring

        self.blocks = []
        for block in file_blocks[self.filename]:
            self.blocks.append(Block(self, block))

    def incorporate(self):
        """Add the edited file to the Disk in the original's place."""
        i = self.disk.romstring.index(self.original_filestring)
        self.disk.romstring = self.disk.romstring.replace(self.original_filestring, self.filestring)

    def write(self):
        """Write the new data to an independent file for later inspection."""
        data = unhexlify(self.filestring)
        dest_path = os.path.join(self.disk.dest_dir, self.filename)
        with open(dest_path, 'wb') as fileopen:
            fileopen.write(data)

    def report_progress(self):
        """Calculate and print the progress made in translating this file."""
        strings = 0
        replacements = 0

        for block in self.blocks:
            for trans in block.translations:
                if isinstance(trans.japanese, float):
                    # Skip the numbers in .DAT files, they're boring
                    continue
                strings += 1
                if trans.english:
                    replacements += 1
        percentage = int(floor((replacements / strings) * 100))
        print self.filename, str(percentage), "% complete",
        print "(%s / %s)" % (replacements, strings)

    def __repr__(self):
        return self.filename


class EXEFile(Gamefile):
    """An executable gamefile. Needs to deal with pointers and blocks and overflow."""

    def __init__(self, disk, filename):
        Gamefile.__init__(self, disk, filename)
        self.pointer_constant = POINTER_CONSTANT[filename]
        self.pointers = self.get_pointers()
        try:
            spare_start, _ = SPARE_BLOCK[self.filename]
            for block in self.blocks:
                if block.start == spare_start:
                    self.spare_block = block
                    block.is_spare = True

        except KeyError:
            self.spare_block = None

        try:
            creature_start, _ = CREATURE_BLOCK[self.filename]
            for block in self.blocks:
                if block.start == creature_start:
                    self.creature_block = block
                    block.is_creature = True

        except KeyError:
            self.creature_block = None
        self.overflow_bytestrings = {}
        # TODO: Make sure overflow bytestrings is empty when there's no spare_block.

    def edit_pointers_in_range(self, (start, stop), diff):
        """Edit all the pointers between two file offsets."""
        if diff != 0:
            for offset in [p for p in range(start+1, stop+1) if p in self.pointers]:
                for ptr in self.pointers[offset]:
                    ptr.edit(diff)

    def get_pointers(self):
        """Retrieve all relevant pointers from the pointer sheet."""
        excel = PointerExcel(POINTER_XLS)
        return excel.get_pointers(self)

    def most_recent_pointer(self, start, stop):
        """Return the highest offset with a pointer in the given range."""
        # Gets called with args lo = previous_text_offset, hi=original_location.
        # What's with the +1s???
        # The lo is +1 here because we don't want to include the previous text that was replaced.
        # The hi is +1 here because we do want to include the original location as a possibility...
        for offset in reversed(range(start+1, stop+1)):
            if offset in self.pointers:
                return offset
        # If there are no other pointers, just return the hi value.

        return stop                            # but it's not +1 here???
        # "Don't leave me! I still love you!"

    def move_overflow(self):
        """Move the overflow bytestrings into the spare block, and adjust the pointers."""
        if not self.spare_block:
            return None

        self.spare_block.blockstring = ""

        # TODO: Pylint be damned, (lo, hi) is a much better nomenclature.
        for (start, stop), ov_bytestring in self.overflow_bytestrings.iteritems():
            pointer_diff = (self.spare_block.start - start) + len(self.spare_block.blockstring)//2
            previous_text_location = start

            # Ugh. Literally the only downside of ditching the OrderedDict() impl of translations

            for offset in range(start, stop):
                for block in self.blocks:
                    for trans in block.translations:
                        if trans.location == offset:
                            jp_bytestring = sjis_to_hex_string(trans.japanese)
                            en_bytestring = ascii_to_hex_string(trans.english)

                            this_string_diff = len(en_bytestring) - len(jp_bytestring) // 2
                            j = ov_bytestring.index(jp_bytestring)
                            ov_bytestring = ov_bytestring.replace(jp_bytestring, en_bytestring)

                            self.edit_pointers_in_range((previous_text_location-1, trans.location),
                                                        pointer_diff)
                            previous_text_location = trans.location
                            pointer_diff += this_string_diff

            # Add this after the whole overflow bytestring has been ptr-adjusted.
            self.spare_block.blockstring += ov_bytestring

        assert len(self.spare_block.blockstring)//2 <= self.spare_block.stop - self.spare_block.start
        self.spare_block.incorporate()

    def change_starting_map(self, map_number):
        """Cheats! Load a different map instead of thelodus sea."""
        offset_in_rom = STARTING_MAP_NUMBER_LOCATION[self.filename] + self.location
        new_map_bytes = str(map_number).encode()
        with open(DEST_ROM_PATH, 'rb+') as f:
            f.seek(offset_in_rom)
            f.write(new_map_bytes)


class DATFile(Gamefile):
    """A data gamefile. Doesn't have pointers or a fixed length, so it's much simpler."""

    def __init__(self, disk, filename):
        Gamefile.__init__(self, disk, filename)
        self.blocks = []
        # DATFiles just get one big DATBlock.
        for block in file_blocks[self.filename]:
            self.blocks.append(DATBlock(self, block))

        self.src_path = os.path.join(self.disk.src_path, filename)

    def get_translations(self):
        excel = DumpExcel(DUMP_XLS)
        return excel.get_dat_translations(self)

    def translate(self):
        """Replace all japanese strings with english ones."""
        for (japanese, english) in self.get_translations():
            if english == "":
                continue
            jp_bytestring = sjis_to_hex_string(japanese)
            eng_bytestring = ascii_to_hex_string(english)

            self.filestring = self.filestring.replace(jp_bytestring, eng_bytestring, 1)


class Block(object):
    """A text block.

    Attributes:
        gamefile: The EXEFile or DATFile object it belongs to.
        start = Beginning offset of the block.
        stop  = Ending offset of the block.
        """

    def __init__(self, gamefile, (start, stop)):
        self.gamefile = gamefile
        self.start = start
        self.stop = stop

        start_in_disk = start + self.gamefile.location
        self.original_blockstring = file_to_hex_string(self.gamefile.disk.src_path,
                                                       start_in_disk, (self.stop-self.start))
        self.blockstring = "" + self.original_blockstring
        self.translations = self.get_translations()

        self.is_creature = False
        self.is_spare = False

    def get_translations(self):
        """Grab all translations in this block."""
        excel = DumpExcel(DUMP_XLS)
        return excel.get_translations(self)

    def edit_text(self):
        """Replace each japanese string in the block with the translated english string."""
        pointer_diff = 0
        previous_text_offset = self.start
        previous_replacement_offset = 0
        is_overflowing = False

        for trans in self.translations:
            if is_overflowing:
                # Leave immediately; the rest of this string is in gamefile.overflow_bytestrings now.
                break

            jp_bytestring = sjis_to_hex_string(trans.japanese)
            eng_bytestring = ascii_to_hex_string(trans.english)

            # jp_bytestring might include ASCII; if it's not found, try the ascii preserving method.
            try:
                j = self.blockstring.index(jp_bytestring)
            except ValueError: # substring not found
                jp_bytestring = sjis_to_hex_string(trans.japanese, preserve_spaces=True)

            if eng_bytestring:
                new_text_offset = trans.location + len(eng_bytestring)//2 + pointer_diff
            else:
                new_text_offset = trans.location + len(jp_bytestring)//2 + pointer_diff

            if new_text_offset >= self.stop:
                is_overflowing = True
                # Pointers usually point to control codes before the text. So look for a recent pointer.
                # But don't backtrack as far as previous_text_offset (maybe already translated)
                recent_pointer = self.gamefile.most_recent_pointer(previous_text_offset, 
                                                                   trans.location)

                start_in_block = (recent_pointer - self.start)*2
                overflow_bytestring = self.original_blockstring[start_in_block:]
                # Store the start and end of the overflow bytestring, 
                # to make sure all pointers are adjusted in the range.
                overflow_lo, overflow_hi = recent_pointer, self.stop
               
                self.gamefile.overflow_bytestrings[(overflow_lo, overflow_hi)] = overflow_bytestring

            self.gamefile.edit_pointers_in_range((previous_text_offset, trans.location), pointer_diff)

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
            if self.is_creature:
                if self.start <= trans.location <= self.stop:
                    if this_string_diff <= 0:
                        eng_bytestring += "00"*(this_string_diff*(-1))
                    else:
                        jp_bytestring += "00"*(this_string_diff)
                    this_string_diff = (len(eng_bytestring) - len(jp_bytestring)) // 2
                    assert this_string_diff == 0, 'creature diff not 0'

            pointer_diff += this_string_diff

            old_slice = self.blockstring[previous_replacement_offset*2:]
            i = old_slice.index(jp_bytestring)//2
            previous_replacement_offset += i//2
            new_slice = old_slice.replace(jp_bytestring, eng_bytestring, 1)

            #j = self.blockstring.index(old_slice)
            self.blockstring = self.blockstring.replace(old_slice, new_slice, 1)

        self.incorporate()

    def incorporate(self):
        """Write the new block to the source gamefile."""
        self.pad()
        self.gamefile.filestring = self.gamefile.filestring.replace(self.original_blockstring, 
                                                                    self.blockstring)

    def pad(self):
        """Fill the remainder of the block with spaces."""
        block_diff = len(self.blockstring) - len(self.original_blockstring)
        assert block_diff <= 0, 'The block %s is too long by %s' % (self, block_diff)
        if block_diff < 0:
            number_of_spaces = ((-1)*block_diff)//2
            #inserted_spaces_index = self.stop
            self.blockstring += '20' * number_of_spaces  # (ASCII space)
        assert len(self.original_blockstring) == len(self.blockstring)

    def __repr__(self):
        return "(%s, %s)" % (hex(self.start), hex(self.stop))


class DATBlock(Block):
    """A text block for a DAT file. Gets simpler translations."""

    def get_translations(self):
        excel = DumpExcel(DUMP_XLS)
        return excel.get_dat_translations(self)


class Translation(object):
    """Has an offset, a SJIS japanese string, and an ASCII english string."""
    def __init__(self, block, location, japanese, english):
        self.location = location
        self.block = block
        self.japanese = japanese
        self.english = english
        self.block = block

    #def jp_bytestring(self):
    #    return sjis_to_hex_string(self.japanese)#

    #def en_bytestring(self):
    #    return ascii_to_hex_string(self.english)

    def __repr__(self):
        return hex(self.location) + " " + self.english


class Pointer(object):
    """A pointer. Found in EXEFiles outside of Blocks. They can be edited with edit(diff)."""
    def __init__(self, gamefile, pointer_location, text_location):
        self.gamefile = gamefile
        self.location = pointer_location
        self.text_location = text_location

        self.old_value = text_location - gamefile.pointer_constant
        old_bytes = pack(self.old_value)
        self.old_bytestring = "{:02x}".format(old_bytes[0]) + "{:02x}".format(old_bytes[1])

    def edit(self, diff):
        """Adjusts the pointer by diff, and writes the new value to the gamefile."""
        if diff != 0:
            location_in_string = self.location*2
            new_value = self.old_value + diff
            new_bytes = pack(new_value)
            new_bytestring = "{:02x}".format(new_bytes[0]) + "{:02x}".format(new_bytes[1])

            string_before = self.gamefile.filestring[0:location_in_string]
            string_after = self.gamefile.filestring[location_in_string+4:]

            rom_bytestring = self.gamefile.filestring[location_in_string:location_in_string+4]
            if self.old_bytestring != rom_bytestring:
                print "This one got edited before; make sure it's right"

            self.gamefile.filestring = string_before + new_bytestring + string_after

    def __repr__(self):
        return hex(self.location), "pointing to", hex(self.text_location)


class DumpExcel(object):
    """Takes a dump excel path, and lets you get translations from it."""
    def __init__(self, path):
        self.path = path
        self.workbook = load_workbook(self.path)

    def get_translations(self, block):
        """Get the translations for an EXE file."""
        trans = []    # translations[offset] = Translation()
        worksheet = self.workbook.get_sheet_by_name(block.gamefile.filename)

        for row in worksheet.rows[1:]:  # Skip the first row, it's just labels
            offset = int(row[0].value, 16)
            if block.start <= offset <= block.stop:
                japanese = row[2].value
                english = row[4].value

                # Yeah this is important - blank strings are None (non-iterable), so use "" instead.
                if not english:
                    english = ""

                trans.append(Translation(block, offset, japanese, english))

        return trans

    def get_dat_translations(self, block):
        """Retrieve the translations for dat files, which don't need offset info."""
        trans = []
        worksheet = self.workbook.get_sheet_by_name(block.gamefile.filename)

        for row in worksheet.rows[1:]:
            japanese = row[2].value
            english = row[4].value

            trans.append((japanese, english))

        return trans

class PointerExcel(object):
    """Takes a pointer dump excel path, and lets you grab the relevant pointers from it."""
    def __init__(self, path):
        self.path = path
        self.pointer_wb = load_workbook(self.path)
        self.pointer_sheet = self.pointer_wb.get_sheet_by_name("Sheet1") 

    def get_pointers(self, gamefile):
        """Retrieve all relevant pointers from the pointer sheet."""
        ptrs = {}

        for row in [r for r in self.pointer_sheet.rows if r[0].value == gamefile.filename]:
            text_offset = int(row[1].value, 16)
            pointer_offset = int(row[2].value, 16)
            ptr = Pointer(gamefile, pointer_offset, text_offset)
            # TODO: Any better way of querying? Seems redundant to store offset 
            # in ptrs and the Pointer() itself.

            if text_offset in ptrs:
                ptrs[text_offset].append(ptr)
            else:
                ptrs[text_offset] = [ptr]
        return ptrs
