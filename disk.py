"""Classes for the 46 Okunen Monogatari text reinserter."""

from __future__ import division
import os
from binascii import unhexlify
from math import floor

from openpyxl import load_workbook

from utils import pack, file_to_hex_string, DUMP_XLS, POINTER_XLS
from utils import sjis_to_hex_string, ascii_to_hex_string
from rominfo import file_blocks, file_location, file_length, POINTER_CONSTANT
from rominfo import STARTING_MAP_NUMBER_LOCATION, SPARE_BLOCK, CREATURE_BLOCK

class Disk(object):
    """The main .FDI file for a PC-98 game. Disks have the properties:

    Attributes:
        src_path: A string with the path to the original .FDI.
        dest_path: A string with the path to the patched .FDI.
        dest_dir: A string to the path of the containing folder of the patched .FDI.
        original_romstring: A hex string of the entire file. Don't change it!
        romstring: A hex string of the entire file. Change this!
        gamefiles: EXEFile and DATFile objects identified in files_to_translate.

    Methods:
        translate(): Perform reinsertion and translation of all files.
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
    """Any file on the disk targeted for reinsertion.

    Attributes:
        filename: String with filename and extension.
        disk: The Disk object containing the file.
        location: Int, starting offset of the file in DiskA.FDI. (Not valid for HDI.)
        length: Int, length in bytes of the file.
        original_filestring: Hex string of the untranslated string.
        filestring: Hex string of the file; gets edited during reinsertion.
        blocks: List of Block objects belonging to the file.

    Methods:
        incorporate(): Reinsert this translated file into its disk.
        write(): Write this file independently to the patched directory.
        report_progress(): Print the file's percent completion.
    """

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

    def get_string(self, offset):
        """Get a string at a particular offset in the file."""
        result = ""
        source = self.filestring[offset*2:]
        byte_index = 0
        while source[byte_index:byte_index+2] != "00": # TODO add other sep bytes. (you seppo)
            result += source[byte_index:byte_index+2]
            byte_index += 2
        return result 

    def __repr__(self):
        return self.filename


class EXEFile(Gamefile):
    """An executable gamefile. Needs to deal with pointers and blocks and overflow.

    Attributes:
        pointer_constant: File-specific constant added to pointer values to retrive text location.
        pointers: A dict of {text_location: Pointer} pairs.
        spare_block: A Block identified as expendable; overflow text can be placed here.
        creature_block: A Block with different padding rules.
        overflow_bytestrings: A dict of locations and bytestrings which get retrouted to the spare block.

    Methods:
        edit_pointers_in_range: Adjust the pointers which point between (lo, hi) with a given diff.
        get_pointers: Retrive a dict of Pointer objects.
        most_recent_pointer: Grabs a pointer one pointer before the given one... within certain limts.
        move_overflow: Move overflow to the spare block and adjust pointers.
        change_starting_map: Cheat and change the beginning-of-chapter spawn point.
         """

    def __init__(self, disk, filename):
        Gamefile.__init__(self, disk, filename)
        self.pointer_constant = POINTER_CONSTANT[filename]
        self.pointers = self.get_pointers()
        # Look for a spare block and designate it as such.
        try:
            spare_start, _ = SPARE_BLOCK[self.filename]
            for block in self.blocks:
                if block.start == spare_start:
                    self.spare_block = block
                    block.is_spare = True
        except KeyError:
            self.spare_block = None

        # Then look for a creature block and designate it as such.
        try:
            creature_start, _ = CREATURE_BLOCK[self.filename]
            for block in self.blocks:
                if block.start == creature_start:
                    self.creature_block = block
                    block.is_creature = True

        except KeyError:
            self.creature_block = None
        self.overflow_bytestrings = {}

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
            if len(self.overflow_bytestrings) > 0:
                print "Uh oh, stuff has spilled out but there's no room to store it!!"
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
                            jp_bytestring = trans.jp_bytestring
                            en_bytestring = trans.en_bytestring

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

"""
    def change_starting_map(self, map_number):
        # TODO: Better way of doing this?
        offset_in_rom = STARTING_MAP_NUMBER_LOCATION[self.filename] + self.location
        new_map_bytes = str(map_number).encode()
        with open(DEST_ROM_PATH, 'rb+') as f:
            f.seek(offset_in_rom)
            f.write(new_map_bytes)
"""


class DATFile(Gamefile):
    """A data gamefile. Doesn't have pointers or a fixed length, so it's much simpler."""

    def __init__(self, disk, filename):
        Gamefile.__init__(self, disk, filename)
        self.blocks = []
        # DATFiles just get one big DATBlock.
        for block in file_blocks[self.filename]:
            self.blocks.append(Block(self, block))

        self.src_path = os.path.join(self.disk.src_path, filename)

    def translate(self):
        """Replace all japanese strings with english ones."""
        for trans in self.blocks[0].get_translations():
            if trans.english == "":
                continue
            jp_bytestring = sjis_to_hex_string(trans.japanese)
            en_bytestring = ascii_to_hex_string(trans.english)

            self.filestring = self.filestring.replace(jp_bytestring, en_bytestring, 1)


class Block(object):
    """A text block.

    Attributes:
        gamefile: The EXEFile or DATFile object it belongs to.
        start = Beginning offset of the block.
        stop  = Ending offset of the block.
        original_blockstring: Hex string of entire block.
        blockstring: Hex string of entire block for editing.
        translations: List of Translation objects.
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
        is_overflowing = False

        for trans in self.translations:
            if is_overflowing:
                # Leave immediately; the rest of this string is in gamefile.overflow_bytestrings now.
                break

            jp_bytestring = trans.jp_bytestring
            en_bytestring = trans.en_bytestring

            # jp_bytestring might include ASCII; if it's not found, try the ascii preserving method.
            try:
                j = self.blockstring.index(jp_bytestring)
            except ValueError: # substring not found
                jp_bytestring = trans.jp_bytestring_alt

            if en_bytestring:
                new_text_offset = trans.location + len(en_bytestring)//2 + pointer_diff
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
            en_bytestring = ascii_to_hex_string(eng)
            this_string_diff = (len(en_bytestring) - len(jp_bytestring)) // 2

            # Pad creature name strings.
            if self.is_creature:
                if self.start <= trans.location <= self.stop:
                    if this_string_diff <= 0:
                        en_bytestring += "00"*(this_string_diff*(-1))
                    else:
                        jp_bytestring += "00"*(this_string_diff)
                    this_string_diff = (len(en_bytestring) - len(jp_bytestring)) // 2
                    assert this_string_diff == 0, 'creature diff not 0'

            # Method 1: old method. keep track of last replacement, start looking there
            #old_slice = self.blockstring[previous_replacement_offset*2:]

            # Method 2: using where the string should be.
            location_in_blockstring = ((pointer_diff + trans.location - self.start) * 2)
            old_slice = self.blockstring[location_in_blockstring:]

            try:
                i = old_slice.index(jp_bytestring)//2
            except ValueError:
                # Sometimes the location_in_blockstring is just wrong... I wonder why?
                old_slice = self.blockstring
                i = old_slice.index(jp_bytestring)//2

            if i > 2:    # text on final lines of dialogue has an i=2.
                try:
                    print trans, "location in blockstring is too high, i =", i
                    print "predicted location was", location_in_blockstring
                except UnicodeEncodeError:
                    print "something might have been replaced incorrectly, i =", i

            new_slice = old_slice.replace(jp_bytestring, en_bytestring, 1)

            self.blockstring = self.blockstring.replace(old_slice, new_slice, 1)

            pointer_diff += this_string_diff

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


class Translation(object):
    """Has an offset, a SJIS japanese string, and an ASCII english string."""
    def __init__(self, block, location, japanese, english):
        self.location = location
        self.block = block
        self.japanese = japanese
        self.english = english
        self.block = block

        self.jp_bytestring = sjis_to_hex_string(japanese)
        self.en_bytestring = ascii_to_hex_string(english)

        self.jp_bytestring_alt = sjis_to_hex_string(japanese, preserve_spaces=True)

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

            # TODO: This is likely a really time-intensive way to do this.
            # A smarter thing to do would have been to use (mutable) bytearrays instead of
            # "bytestrings" for all these string editing operations...

            string_before = self.gamefile.filestring[0:location_in_string]
            string_after = self.gamefile.filestring[location_in_string+4:]

            rom_bytestring = self.gamefile.filestring[location_in_string:location_in_string+4]
            if self.old_bytestring != rom_bytestring:
                print "Pointer at %s got edited before; make sure it's right" % hex(self.location)

            self.gamefile.filestring = string_before + new_bytestring + string_after

    def __repr__(self):
        return hex(self.location), "pointing to", hex(self.text_location)


class DumpExcel(object):
    """Takes a dump excel path, and lets you get a block's translations from it."""
    def __init__(self, path):
        self.path = path
        self.workbook = load_workbook(self.path)

    def get_translations(self, block):
        """Get the translations for an EXE or DAT file."""
        # So they can make use of Translation() objects as well.
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
