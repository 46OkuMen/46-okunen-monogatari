"""Various utilities for use in the dumper/reinserter for 46 Okunen Monogatari: The Shinka Ron."""

import os, re
from rominfo import file_blocks

"""
Constants for filenames and locations.
"""

SCRIPT_DIR = os.path.dirname(__file__)
SRC_PATH = os.path.join(SCRIPT_DIR, 'intermediate_roms')
DEST_PATH = os.path.join(SCRIPT_DIR, 'patched_roms')

SRC_ROM_PATH = os.path.join(SRC_PATH, "46 Okunen Monogatari - The Sinkaron (J) A user.FDI")
DEST_ROM_PATH = os.path.join(DEST_PATH, "46 Okunen Monogatari - The Sinkaron (J) A user.FDI")

TYPESET_ROM_PATH = os.path.join(SCRIPT_DIR, 'typeset_roms', '46 Okunen Monogatari - The Sinkaron (J) A user.FDI')

RAW_DUMP_XLS = 'shinkaron_dump.xlsx'
DUMP_XLS = "shinkaron_dump_test.xlsx"
POINTER_XLS = "shinkaron_pointer_dump.xlsx"

"""
Regex and methods to capture pointers from the file bytestring.
"""

dialogue_pointer_regex = r"\\x1e\\xb8\\x([0-f][0-f])\\x([0-f][0-f])" # Minus the \\x50. Adds 50 more pointers.

# Binary patterns used in GDT pattern encoding
gdt_patterns = [0b00000000, 0b00100010, 0b01010101, 0b01110111, 0b11111111, 0b11011101, 0b10101010, None, 0b00000000, 
               (0b11011101, 0b10001000), (0b01010101, 0b10101010), (0b01110111, 0b11011101), 0b11111111,
               (0b11011101, 0b01110111), (0b10101010, 0b01010101), None]

def capture_pointers_from_table(first, second, hx):
    # Doesn't usethe original  pointer_regex above - better results when you specifically look for
    # the bytes in the file-specific pointer separators.
    return re.compile(r'(\\x([0-f][0-f])\\x([0-f][0-f])\\x%s\\x%s)' % (first, second)).finditer(hx)


def capture_pointers_from_function(hx):
    # No arguments here; dialogue pointers always preceded by 1E-B8 which is in the regex
    return re.compile(dialogue_pointer_regex).finditer(hx)

"""
Methods to interpret values of little-endian pointers and the values they point to.
"""


def unpack(s, t=None):
    if t is None:
        t = str(s)[2:]
        s = str(s)[0:2]
    s = int(s, 16)
    t = int(t, 16)
    value = (t * 0x100) + s
    return value


def pack(h):
    s = h % 0x100
    t = h // 0x100
    return (s, t)


def location_from_pointer(pointer, constant):
    return '0x' + str(format((unpack(pointer[0], pointer[1]) + constant), '05x'))

def pointer_value_from_location(offset, constant):
    # Subtract the constant, pack it. Then that's the value to look for among the pointers already mapped out in excel.
    return offset - constant

def first_offset_in_block(file, block_index, offsets):
    if not offsets:
        return None
    print "first offset in block", file, block_index
    print "overflow text:", offsets
    block_lo, block_hi = file_blocks[file][block_index]
    for o in offsets:
        if (o >= block_lo) and (o <= block_hi):
            return o

def compare_strings(a, b):
    try:
        return [i/2 for i in xrange(len(a)) if a[i] != b[i]]
    except IndexError:
        return "strings different lengths, so probably different"

def file_to_hex_string(file_path, start=0, length=0):
    # Defaults: read full file from start.
    hex_string = ""
    f = open(file_path, 'rb+')
    f.seek(start)
    if length:
        for c in f.read(length):
            hex_string += "%02x" % ord(c)
    else:
        for c in f.read():
            hex_string += "%02x" % ord(c)
    return hex_string

def ascii_to_hex_string(eng):
    """Returns a hex string of the ascii bytes of a given english (translated) string."""
    eng_bytestring = ""
    if not eng:
        return ""
    else:
        try:
            eng = str(eng)
        except UnicodeEncodeError:
            print "tried to encode a fullwidth number"
            eng = eng.encode('shift-jis')
            pass
        for char in eng:
            eng_bytestring += "%02x" % ord(char)

        # handle [BLANK] control code
        if '5b424c414e4b5d' == eng_bytestring:
            eng_bytestring = ''

        # handle [LN] control code
        if '5b4c4e5d' in eng_bytestring:
            eng_bytestring = eng_bytestring.replace('5b4c4e5d', '0a')

        # handle [DEGC] control code
        if '5b444547435d' in eng_bytestring:
            eng_bytestring = eng_bytestring.replace('5b444547435d', '818e')

        # handle [004F] control code
        if '5b303034465d' in eng_bytestring:
            eng_bytestring = eng_bytestring.replace('5b303034465d', '004f')

        # handle [SPLIT] control code
        if '5b53504c49545d' in eng_bytestring:
            # add <WAIT><LN><LN> at the position of [SPLIT]
            eng_bytestring = eng_bytestring.replace('5b53504c49545d', '130a0a')

        # handle [PAUSE] control code
        if '5b50415553455d' in eng_bytestring:
            eng_bytestring = eng_bytestring.replace('5b50415553455d', '1108')

        return eng_bytestring

def sjis_to_hex_string(jp, preserve_spaces=False):
    """Returns a hex string of the Shift JIS bytes of a given japanese string."""
    jp_bytestring = ""
    try:
        sjis = jp.encode('shift-jis')
    except AttributeError:
        # Trying to encode numbers throws an attribute error; they aren't important, so just keep the number
        sjis = str(jp)
    for char in sjis:
        hexchar = "%02x" % ord(char)
        # SJS spaces get mis-encoded as ascii, which means the strings don't get found. Fix to 81-40
        if not preserve_spaces:
            if hexchar == '20': 
                hexchar = '8140'
        jp_bytestring += hexchar

    # handle [PAUSE] control code
    if '5b50415553455d' in jp_bytestring:
        jp_bytestring = jp_bytestring.replace('5b50415553455d', '1108')

    # handle [PAGE] control code
    if '5b504147455d' in jp_bytestring:
        jp_bytestring = jp_bytestring.replace('5b504147455d', '')
        # It can be a variable number of 0d0a's, so... need to think about the best way to handle this.

    return jp_bytestring

def onscreen_length(eng):
    """ASCII numbers are displayed as full-width characters ingame, so their length is 2."""
    result = 0
    if eng is None:
        return result
    # remove 'new' and 'wait' control codes - they don't display anything
    eng = eng.replace('\x16', '')
    eng = eng.replace('\x13', '')
    for char in eng:
        if char.isdigit():
            result += 2
        else:
            result += 1
    return result
    