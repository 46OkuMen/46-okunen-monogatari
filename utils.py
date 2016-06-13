"""Various utilities for use in the dumper/reinserter for 46 Okunen Monogatari: The Shinka Ron."""

import os, re
from rominfo import file_blocks

SCRIPT_DIR = os.path.dirname(__file__)
SRC_PATH = os.path.join(SCRIPT_DIR, 'intermediate_roms')
DEST_PATH = os.path.join(SCRIPT_DIR, 'patched_roms')

SRC_ROM_PATH = os.path.join(SRC_PATH, "46 Okunen Monogatari - The Sinkaron (J) A user.FDI")
DEST_ROM_PATH = os.path.join(DEST_PATH, "46 Okunen Monogatari - The Sinkaron (J) A user.FDI")

DUMP_XLS = "shinkaron_dump_test.xlsx"
POINTER_XLS = "shinkaron_pointer_dump.xlsx"

pointer_regex = r"(\\x[0-f][0-f]\\x[0-f][0-f](\\x[0-f][0-f])(\\x[0-f][0-f]))((\\x[0-f][0-f])\\x[0-f][0-f]\2\3(?!\3\5)){7,}"
new_dialogue_pointer_regex = r"\\x1e\\xb8\\x([0-f][0-f])\\x([0-f][0-f])" # Minus the \\x50. Adds 50 more pointers.

# Binary patterns used in GDT pattern encoding
gdt_patterns = [0b00000000, 0b00100010, 0b01010101, 0b01110111, 0b11111111, 0b11011101, 0b10101010, None, 0b00000000, 
               (0b11011101, 0b10001000), (0b01010101, 0b10101010), (0b01110111, 0b11011101), 0b11111111,
               (0b11011101, 0b01110111), (0b10101010, 0b01010101), None]

def capture_pointers_from_table(first, second, hx):
    return re.compile(r'(\\x([0-f][0-f])\\x([0-f][0-f])\\x%s\\x%s)' % (first, second)).finditer(hx)


def capture_pointers_from_function(hx):
    # No first and second; always preceded by 1E-B8 which is in the regex
    return re.compile(new_dialogue_pointer_regex).finditer(hx)
    # old: 4276 pointers
    # new: 4326 pointers


def unpack(s, t):
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


def get_current_block(text_offset, file):
    for index, block in enumerate(file.blocks):
        lo, hi = block.location
        if (text_offset >= lo) and (text_offset < hi):
            return index


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
    eng_bytestring = ""
    for c in eng:
        eng_bytestring += "%02x" % ord(c)
    return eng_bytestring


def sjis_to_hex_string(jp):
    jp_bytestring = ""
    sjis = jp.encode('shift-jis')
    for c in sjis:
        hx = "%02x" % ord(c)
        if hx == '20': # SJS spaces get mis-encoded as ascii, which means the strings don't get found. Fix to 81-40
            hx = '8140'
        jp_bytestring += hx
    return jp_bytestring

def sjis_to_hex_string_preserve_spaces(jp):
    """On rare occasions, the space replacing in the above method is a mistake."""
    jp_bytestring = ""
    sjis = jp.encode('shift-jis')
    for c in sjis:
        hx = "%02x" % ord(c)
        jp_bytestring += hx
    return jp_bytestring

def onscreen_length(eng):
    """ASCII numbers are displayed as full-width characters ingame, so their length is 2."""
    result = 0
    for char in eng:
        if char.isdigit():
            result += 2
        else:
            result += 1
    return result