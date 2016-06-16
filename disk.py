"""Classes for the 46 Okunen Monogatari translation patch."""

from __future__ import division
import os
from binascii import unhexlify
from collections import OrderedDict
from math import floor

from openpyxl import load_workbook

from utils import file_to_hex_string, DUMP_XLS, POINTER_XLS, sjis_to_hex_string, ascii_to_hex_string
from rominfo import file_blocks, file_location, file_length, POINTER_CONSTANT, SPARE_BLOCK, CREATURE_BLOCK

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

    def __init__(self, src_path, dest_path):
        self.src_path = src_path
        self.dest_path = dest_path

        self.dest_dir = os.path.abspath(os.path.join(dest_path, os.pardir))

        self.original_romstring = file_to_hex_string(src_path)
        self.romstring = "" + self.original_romstring

        #self.gamefiles = []
        #for gf in file_blocks.iterkeys():
        #    self.gamefiles.append(Gamefile(self, gf))

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

        self.translations = self.get_translations()

    def get_translations(self):
        """Make a DumpExcel and grab this file's translations from it."""
        excel = DumpExcel(DUMP_XLS)
        return excel.get_translations(self)

    def incorporate(self):
        """Add the edited file to the Disk in the original's place."""
        # TODO: Is it safe to incorporate all the blocks here, too? Look at where this is used.
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

        for (japanese, english) in self.translations.itervalues():
            if isinstance(japanese, float):
                # Skip the numbers in .DAT files, they're boring
                continue
            strings += 1
            if english:
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
        except KeyError:
            self.spare_block = None

        try:
            creature_start, _ = CREATURE_BLOCK[self.filename]
            for block in self.blocks:
                if block.start == creature_start:
                    self.creature_block = block
        except KeyError:
            self.creature_block = None

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
        return stop       # but it's not +1 here???


class DATFile(Gamefile):
    """A data gamefile.

    Attributes:
        #src_path: A string for the orgiinal location of the standalone file. DAT files"""

    def __init__(self, disk, filename):
        Gamefile.__init__(self, disk, filename)
        self.src_path = os.path.join(self.disk.src_path, filename)

    def get_translations(self):
        excel = DumpExcel(DUMP_XLS)
        return excel.get_dat_translations(self)

    def translate(self):
        for (japanese, english) in self.get_translations():
            if english == "":
                continue
            jp_bytestring = sjis_to_hex_string(japanese)
            eng_bytestring = ascii_to_hex_string(english)

            self.filestring = self.filestring.replace(jp_bytestring, eng_bytestring, 1)


class Block(object):
    """A text block."""

    def __init__(self, gamefile, (start, stop)):
        self.gamefile = gamefile
        self.start = start
        self.stop = stop
        self.length = stop - start
        self.location = (start, stop)

        start_in_disk = start + self.gamefile.location
        self.original_blockstring = file_to_hex_string(self.gamefile.disk.src_path,
                                                       start_in_disk, self.length)
        self.blockstring = "" + self.original_blockstring

        assert len(self.blockstring) == (stop - start)*2

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


class CreatureBlock(Block):
    """A block with creature names."""

    pass

class SpareBlock(Block):
    """A block to be erased for holding overflow strings."""
    pass


class DumpExcel(object):
    """Takes a dump excel path, and lets you get translations from it."""
    def __init__(self, path):
        self.path = path
        self.workbook = load_workbook(self.path)

    def get_translations(self, gamefile):
        """Get the translations for an EXE file."""
        trans = OrderedDict()    # translations[offset] = (japanese, english)
        worksheet = self.workbook.get_sheet_by_name(gamefile.filename)

        for row in worksheet.rows[1:]:  # Skip the first row, it's just labels
            offset = int(row[0].value, 16)
            japanese = row[2].value
            english = row[4].value

            # Yeah this is important - blank strings are None, so use an empty string instead.
            if not english:
                english = ""

            trans[offset] = (japanese, english)

        return trans

    def get_dat_translations(self, gamefile):
        """Retrieve the translations for dat files, which don't need offset info."""
        trans = []
        worksheet = self.workbook.get_sheet_by_name(gamefile.filename)

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
        ptrs = OrderedDict()

        for row in [r for r in self.pointer_sheet.rows if r[0].value == gamefile.filename]:
            text_offset = int(row[1].value, 16)
            pointer_offset = int(row[2].value, 16)
            if text_offset in ptrs:
                ptrs[text_offset].append(pointer_offset)
            else:
                ptrs[text_offset] = [pointer_offset]
        return ptrs
