"""Classes for the 46 Okunen Monogatari translation patch."""

from __future__ import division
import os
from binascii import unhexlify
from collections import OrderedDict
from math import floor

from openpyxl import load_workbook

from utils import file_to_hex_string, DUMP_XLS, sjis_to_hex_string, ascii_to_hex_string
from rominfo import file_blocks, file_location, file_length, POINTER_CONSTANT

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
        with open(self.dest_path, 'wb') as f:
            f.write(data)


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

        #self.src_path = os.path.join(self.disk.src_path, filename)
        self.dest_path = os.path.join(self.disk.dest_dir, filename)

        self.translations = self.get_translations()

    def get_translations(self):
        """Return an OrderedDict() of translations."""
        trans = OrderedDict()    # translations[offset] = (japanese, english)
        
        workbook = load_workbook(DUMP_XLS)
        worksheet = workbook.get_sheet_by_name(self.filename)

        for row in worksheet.rows[1:]:  # Skip the first row, it's just labels
            offset = int(row[0].value, 16)
            japanese = row[2].value
            english = row[4].value

            if not english:
                # TODO: Hm, does this really do anything now?
                english = ""

            trans[offset] = (japanese, english)
        return trans

    def incorporate(self):
        """Add the edited file to the Disk in the original's place."""
        i = self.disk.romstring.index(self.original_filestring)
        self.disk.romstring = self.disk.romstring.replace(self.original_filestring, self.filestring)

    def write(self):
        """Write the new data to an independent file for later inspection."""
        data = unhexlify(self.filestring)
        with open(self.dest_path, 'wb') as f:
            f.write(data)

    def report_progress(self):
        """Calculate and print the progress made in translating this file."""
        strings = 0
        replacements = 0

        for (jp, eng) in self.translations.itervalues():
            if isinstance(jp, float):
                # Skip the numbers in .DAT files, they're boring
                continue
            strings += 1
            if eng:
                replacements += 1
        percentage = int(floor((replacements / strings) * 100))
        print self.filename, str(percentage), "% complete",
        print "(%s / %s)" % (replacements, strings)


class EXEFile(Gamefile):
    """An executable gamefile."""

    def __init__(self, disk, filename):
        Gamefile.__init__(self, disk, filename)
        self.pointer_constant = POINTER_CONSTANT[filename]


class DATFile(Gamefile):
    """A data gamefile.

    Attributes:
        #src_path: A string for the orgiinal location of the standalone file. DAT files"""

    def __init__(self, disk, filename):
        Gamefile.__init__(self, disk, filename)
        self.src_path = os.path.join(self.disk.src_path, filename)

    def get_translations(self):
        # TODO: How does this differ from the method it's overriding, exactly?
        trans = []
        workbook = load_workbook(DUMP_XLS)
        worksheet = workbook.get_sheet_by_name(self.filename)

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
        self.original_blockstring = file_to_hex_string(self.gamefile.disk.src_path, start_in_disk, self.length)
        # Tricky - file_to_hex_string takes a path, a starting point, and a LENGTH. (not a stopping point)
        self.blockstring = "" + self.original_blockstring

        assert len(self.blockstring) == (stop - start)*2

    def incorporate(self):
        """Write the new block to the source gamefile."""
        self.pad()
        self.gamefile.filestring = self.gamefile.filestring.replace(self.original_blockstring, self.blockstring)

    def pad(self):
        """Fill the remainder of the block with spaces."""
        block_diff = len(self.blockstring) - len(self.original_blockstring)
        if block_diff > 0:
            print block_diff
        assert block_diff <= 0, 'Block ending in %s is too long' % hex(self.stop)
        if block_diff < 0:
            number_of_spaces = ((-1)*block_diff)//2
            inserted_spaces_index = self.stop
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

"""
class ExcelReader(object):
    def __init__(self, path):
        self.path = path


class DumpExcel(object):
    def __init__(self, path):
        self.path = path

    def get_translations(self, gamefile):
        trans = OrderedDict()    # translations[offset] = (japanese, english)
        
        workbook = load_workbook(self.path)
        worksheet = workbook.get_sheet_by_name(gamefile.filename)

        for row in worksheet.rows[1:]:  # Skip the first row, it's just labels
            offset = int(row[0].value, 16)
            japanese = row[2].value
            english = row[4].value

            trans[offset] = (japanese, english)
        return trans
        """