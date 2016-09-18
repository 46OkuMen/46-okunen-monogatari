"""Classes for the 46 Okunen Monogatari text reinserter."""

from __future__ import division
import os
from binascii import unhexlify
from math import floor

from openpyxl import load_workbook

from utils import pack, unpack, file_to_hex_string, DUMP_XLS, POINTER_XLS
from utils import sjis_to_hex_string, ascii_to_hex_string, get_current_block
from rominfo import file_blocks, file_location, file_length, POINTER_CONSTANT
from rominfo import SPARE_BLOCK, CREATURE_BLOCK

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

        self.dump_excel = DumpExcel(DUMP_XLS)

        # If I want to hardcode the total strings here, it's 4,815 (9/7/16)
        # wait - when I don't hardcode it, it's 5,240?? (Is that just the numbers in the .dat files?)
        # # TODO: Determine number of strings in whole game.
        self.total_strings = 0
        self.translated_strings = 0

        self.gamefiles = []
        for filename in files_to_translate:
            if filename.endswith('.EXE'):
                exefile = EXEFile(self, filename)
                self.total_strings += exefile.total_strings
                self.translated_strings += exefile.translated_strings
                self.gamefiles.append(exefile)
            elif filename.endswith('.DAT'):
                datfile = DATFile(self, filename)
                self.total_strings += datfile.total_strings
                self.translated_strings += datfile.translated_strings
                self.gamefiles.append(datfile)

        
    def translate(self):
        """Perform translation and reinsertion."""
        for gamefile in self.gamefiles:
            if gamefile.filename.endswith('DAT'):
                gamefile.translate()
                gamefile.write()
            else:
                for block in gamefile.blocks:
                    block.edit_text()
                try:
                    gamefile.creature_block.edit_text()
                except AttributeError:
                    # Doesn't have a creature block. Don't worry about it.
                    pass
                gamefile.move_overflow()
                gamefile.incorporate()
                gamefile.write()
                gamefile.report_progress()
        try:
            self.write()
        except IOError:
            _ = raw_input("You have the game open; close it and hit Enter to continue")
            self.write()
        self.report_progress()

    def write(self):
        """Write the patched bytes to a new FDI."""
        data = unhexlify(self.romstring)
        with open(self.dest_path, 'wb') as fileopen:
            fileopen.write(data)

    def report_progress(self):
        """Calculate and print the progress made in translating this file."""

        percentage = int(floor((self.translated_strings / self.total_strings * 100)))
        print 'The Shinkaron', str(percentage), "% complete",
        print "(%s / %s)\n" % (self.translated_strings, self.total_strings)



class Gamefile(object):
    """
    Any file on the disk targeted for reinsertion.

    Attributes:
        filename: String with filename and extension.
        disk: The Disk object containing the file.
        location: Int, starting offset of the file in DiskA.FDI. (Not valid for HDI.)
        length: Int, length in bytes of the file.
        original_filestring: Hex string of the untranslated string.
        filestring: Hex string of the file; gets edited during reinsertion.
        blocks: List of Block objects belonging to the file.
        total_strings: Number of Japanese strings in the file.
        translated_strings: Number of replacements made.

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

        self.total_strings = 0
        self.translated_strings = 0
        for block in self.blocks:
            for trans in block.translations:
                if isinstance(trans.japanese, float):
                    # Skip the numbers in .DAT files, they're boring
                    continue
                self.total_strings += 1
                if trans.english:
                    self.translated_strings += 1


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

        percentage = int(floor((self.translated_strings / self.total_strings * 100)))
        print self.filename, str(percentage), "% complete",
        print "(%s / %s)\n" % (self.translated_strings, self.total_strings)

    def __repr__(self):
        return self.filename


class EXEFile(Gamefile):
    """An executable gamefile. Needs to deal with pointers and blocks and overflow.

    Attributes:
        pointer_constant: File-specific constant added to pointer values to retrive text location.
        pointers: A dict of {text_location: Pointer} pairs.
        spare_block: A Block identified as expendable; overflow text can be placed here.
        creature_block: A Block with different padding rules.
        overflows: A list of Overflows which will get moved and repointed elsewhere.

    Methods:
        edit_pointers_in_range: Adjust the pointers which point between (lo, hi) with a given diff.
        get_pointers: Retrive a dict of Pointer objects.
        most_recent_pointer: Grabs a pointer one pointer before the given one... within certain limts.
        move_overflow: Move overflow to the spare block and adjust pointers.
        (change_starting_map: Cheat and change the beginning-of-chapter spawn point. (Not implemented yet))
         """

    def __init__(self, disk, filename):
        Gamefile.__init__(self, disk, filename)
        self.pointer_constant = POINTER_CONSTANT[filename]
        self.pointers = self.get_pointers()

        # Look for a spare block and designate it as such.
        try:
            spare_start, spare_stop = SPARE_BLOCK[self.filename]
            for block in self.blocks:
                if block.start == spare_start:
                    self.spare_block = block
                    block.is_spare = True
        except KeyError:
            self.spare_block = None

        # You can also store stuff in the padding at the ends of blocks, so store those locs here.
        self.spares = []
        if self.spare_block:
            self.spares.append((spare_start, spare_stop))

        # Then look for a creature block and designate it as such.
        try:
            creature_start, creature_stop = CREATURE_BLOCK[self.filename]
            for block in self.blocks:
                if block.start == creature_start:
                    self.creature_block = CreatureBlock(self, (creature_start, creature_stop))
                    self.blocks.remove(block)
        except KeyError:
            self.creature_block = None

        self.overflows = []

        self.total_strings = 0
        self.translated_strings = 0

        for block in self.blocks:
            for trans in block.translations:
                self.total_strings += 1
                if trans.english:
                    self.translated_strings += 1

        if self.creature_block:
            for c in self.creature_block.translations:
                self.total_strings += 1
                if c.english:
                    self.translated_strings += 1

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
        offset = stop+1
        while offset not in self.pointers:
            offset -= 1
        return offset

    def most_recent_string(self, start, stop):
        """Return the highest offset with a pointer in the given range."""
        # Gets called with args lo = previous_text_offset, hi=original_location.
        # What's with the +1s???
        # The lo is +1 here because we don't want to include the previous text that was replaced.
        # The hi is +1 here because we do want to include the original location as a possibility...
        for offset in reversed(range(start+1, stop+1)):
            if offset in self.pointers:
                return offset
        # If there are no other pointers, just return the hi value.
        return stop


    def move_overflow(self):
        """Move the overflow bytestrings into the spare block, and adjust the pointers."""
        if not self.spare_block:
            if len(self.overflows) > 0:
                print "Uh oh, stuff has spilled out but there's no room to store it!!"
                print self.overflows
            return None

        self.spare_block.blockstring = ""

        # Want to try to put the largest overflows into the smallest containing spare, for best space usage.
        self.overflows.sort(key=lambda x: x.new_length, reverse=True)
        self.spares.sort(key=lambda x: x[1] - x[0])
        
        for overflow in self.overflows:
            print "Overflow:", [p.new_length for p in self.overflows]
            print "Spares:", [s[1] - s[0] for s in self.spares]
            overflow_length = overflow.new_length
            for i, s in enumerate(self.spares):
                if s[1] - s[0] >= overflow_length:
                    overflow.move(s[0])
                    self.spares[i] = s[0] + overflow_length, s[1]
                    self.spares.sort(key=lambda x: x[1] - x[0])
                    break

        excess = len(self.spare_block.blockstring)//2 - (self.spare_block.stop - self.spare_block.start)
        assert excess < 0, "Spare block is %s too long" % (excess)

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

        self.is_spare = False

    def get_translations(self):
        """Grab all translations in this block."""
        excel = self.gamefile.disk.dump_excel
        return excel.get_translations(self)

    def get_pointers(self):
        file_pointers = self.gamefile.pointers
        block_pointers = [p for p in file_pointers if p >= self.start and p <= self.stop]
        block_pointers.sort()
        return block_pointers

    def overflow_location(self):
        """
        Find the first pointer that contains text that will overflow.
        """
        result = None
        diff = 0
        block_length = self.stop - self.start

        block_pointers = self.get_pointers()

        block_pointers.append(self.stop) # Should solve the problem of the last pointer not being considered (due to ranges)

        for i, ptr in enumerate(block_pointers):
            if i >= len(block_pointers)-1:
                break
            ptr_range = (ptr, block_pointers[i+1])
            
            # Look for all translations located in the pointer range.
            translations = [t for t in self.translations if t.location >= ptr_range[0] and t.location < ptr_range[1]]

            for trans in translations:
                location_in_blockstring = (trans.location * 2) - self.start
                jp_bytestring, en_bytestring = trans.jp_bytestring, trans.en_bytestring

                if en_bytestring:
                    text_length = len(en_bytestring)//2
                    this_string_diff = (len(en_bytestring) - len(jp_bytestring)) // 2
                else:
                    text_length = len(jp_bytestring)//2
                    this_string_diff = 0

                new_text_offset = trans.location + text_length + diff # TODO: + this_string_diff?

                if new_text_offset >= self.stop:
                    while ptr + text_length + diff > self.stop:
                        ptr = block_pointers[i-1]
                        i -= 1

                    return ptr

                diff += this_string_diff
                
                

    def edit_text(self):
        """Replace each japanese string in the block with the translated english string."""
        pointer_diff = 0
        previous_text_offset = self.start
        is_overflowing = False

        overflow_location = self.overflow_location()

        for trans in self.translations:
            jp_bytestring, en_bytestring = trans.jp_bytestring, trans.en_bytestring

            # jp_bytestring might include ASCII; if it's not found, try the ascii preserving method.
            try:
                j = self.blockstring.index(jp_bytestring)
            except ValueError: # substring not found
                jp_bytestring = trans.jp_bytestring_alt

            if (trans.location >= overflow_location) and overflow_location:
                print "%s >= %s" % (hex(trans.location), hex(overflow_location))
                is_overflowing = True

                recent_string = self.gamefile.most_recent_string(previous_text_offset, 
                                                                 trans.location)
                recent_pointer = overflow_location

                start_in_block = (recent_pointer - self.start)*2
                overflow_bytestring = self.original_blockstring[start_in_block:]
                # Store the start and end of the overflow bytestring, 
                # to make sure all pointers are adjusted in the range.
                overflow_lo, overflow_hi = recent_pointer, self.stop

                overflow_pointers = [p for p in self.get_pointers() if overflow_lo <= p <= overflow_hi]
                if self.stop not in overflow_pointers:
                    overflow_pointers.append(self.stop)
                print [hex(x) for x in overflow_pointers]

                for i, p in enumerate(overflow_pointers):
                    if i == len(overflow_pointers)-1:
                        break
                    next_p = overflow_pointers[i+1]
                    print hex(p), hex(next_p)
                    start_in_block = (p - self.start)*2
                    stop_in_block = (next_p - self.start)*2

                    this_bytestring = self.original_blockstring[start_in_block:stop_in_block]
                    print this_bytestring
                    this_overflow = Overflow(self.gamefile, (p, next_p), this_bytestring)
                    self.gamefile.overflows.append(this_overflow)

                #this_overflow = Overflow(self.gamefile, (overflow_lo, overflow_hi), overflow_bytestring)
               
                #self.gamefile.overflows.append(this_overflow)

            self.gamefile.edit_pointers_in_range((previous_text_offset, trans.location), pointer_diff)

            previous_text_offset = trans.location

            # "eng" is an ugly way of doing this. But we want to be able to do the thing where, if
            # it's overflowing, do a "translation" of the overflow bytestring into "".
            # If we set trans.english to "", it wouldn't get translated later.
            # So use a separate temporary "eng" variable which can be english or blank, but don't lose data.
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
                print hex(trans.location)
                i = old_slice.index(jp_bytestring)//2

            if i > 2:    # text on final lines of dialogue has an i=2.
                try:
                    # still not sure when this occurs...
                    print trans, "location in blockstring is too high, i =", i
                    print "predicted location was", location_in_blockstring
                except UnicodeEncodeError:
                    print "something might have been replaced incorrectly, i =", i

            new_slice = old_slice.replace(jp_bytestring, en_bytestring, 1)

            self.blockstring = self.blockstring.replace(old_slice, new_slice, 1)

            pointer_diff += this_string_diff

            if is_overflowing:
                break

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
            padding_start = self.start + len(self.blockstring)//2
            self.blockstring += '20' * number_of_spaces  # (ASCII space)
            #print number_of_spaces, "spaces inserted"
            padding_stop = self.start + len(self.blockstring)//2

            self.gamefile.spares.append((padding_start, padding_stop))
        assert len(self.original_blockstring) == len(self.blockstring)

    def __repr__(self):
        return "(%s, %s)" % (hex(self.start), hex(self.stop))


class CreatureBlock(Block):
    """
    The creature block has all the names of creatures in that file, plus some stat info.
    There's a consistent length to each creature's entry in this block which can't be altered.
    If you pad the creature's name with spaces, the spaces show up in gameplay text...
    But if you pad it with 00 bytes, everything is fine!
    So no pointers need to be adjusted, you just need to pad the strings.
    So the edit_text() method is a lot simpler for a CreatureBlock.
    """

    def edit_text(self):
        for trans in self.translations:
            jp_bytestring = trans.jp_bytestring
            en_bytestring = trans.en_bytestring

            this_string_diff = (len(en_bytestring) - len(jp_bytestring)) // 2

            if this_string_diff <= 0:
                en_bytestring += "00"*(this_string_diff*(-1))
            else:
                jp_bytestring += "00"*(this_string_diff)

            this_string_diff = (len(en_bytestring) - len(jp_bytestring)) // 2
            assert this_string_diff == 0, 'creature diff not 0'

            location_in_blockstring = (trans.location - self.start) * 2
            old_slice = self.blockstring[location_in_blockstring:]

            try:
                i = old_slice.index(jp_bytestring)//2
            except ValueError:
                old_slice = self.blockstring
                i = old_slice.index(jp_bytestring)//2

            new_slice = old_slice.replace(jp_bytestring, en_bytestring, 1)

            self.blockstring = self.blockstring.replace(old_slice, new_slice, 1)

        self.incorporate()


class SpareBlock(Block):
    pass


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

            string_before = self.gamefile.filestring[0:location_in_string]
            string_after = self.gamefile.filestring[location_in_string+4:]
                
            self.gamefile.filestring = string_before + new_bytestring + string_after

    def __repr__(self):
        return "%s pointing to %s" % (hex(self.location), hex(self.text_location))


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

                if isinstance(japanese, float):
                    # Causes some encoding problems? Trying to skip them for now
                    continue

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

class Overflow(object):
    """A string of data that must be repositioned elsewhere."""
    def __init__(self, gamefile, original_location, bytestring):
        self.gamefile = gamefile
        self.start, self.stop = original_location
        self.original_bytestring = bytestring
        self.bytestring = bytestring

        self.new_length = self.get_length()

    def get_length(self):
        # This duplicates some functionality of move(), because we really just need this to get the new length.
        for offset in range(self.start, self.stop):
            for block in self.gamefile.blocks:
                for trans in [x for x in block.translations if x.location == offset]:

                    jp_bytestring = trans.jp_bytestring
                    en_bytestring = trans.en_bytestring

                    j = self.bytestring.index(jp_bytestring)
                    self.bytestring = self.bytestring.replace(jp_bytestring, en_bytestring)

        # return the length of the new bytestring, but restore the original bytestring first
        result = len(self.bytestring) // 2
        self.bytestring = str(self.original_bytestring)
        return result

    def move(self, location):

        # TODO: Does this always insert at exactly the place I expect it to??
        destination_block = self.gamefile.blocks[get_current_block(location, self.gamefile)]

        pointer_diff = location - self.start
        previous_text_location = self.start-1

        for offset in range(self.start, self.stop):
            for block in self.gamefile.blocks:
                for trans in [x for x in block.translations if x.location == offset]:

                    jp_bytestring = trans.jp_bytestring
                    en_bytestring = trans.en_bytestring

                    this_string_diff = (len(en_bytestring) - len(jp_bytestring)) // 2

                    j = self.bytestring.index(jp_bytestring)
                    self.bytestring = self.bytestring.replace(jp_bytestring, en_bytestring)

                    self.gamefile.edit_pointers_in_range((previous_text_location, trans.location),
                                                         pointer_diff)
                    previous_text_location = trans.location
                    pointer_diff += this_string_diff

        destination_block.blockstring += self.bytestring

    def __repr__(self):
        return hex(self.start) + " " + hex(self.stop)