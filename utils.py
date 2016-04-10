from rominfo import file_blocks
import re

#old_regex = r"(\\x[0-f][0-f]\\x[0-f][0-f](\\x[0-f][0-f]\\x[0-f][0-f]))(\\x[0-f][0-f]\\x[0-f][0-f]\2){2,}"
pointer_regex = r"(\\x[0-f][0-f]\\x[0-f][0-f](\\x[0-f][0-f])(\\x[0-f][0-f]))((\\x[0-f][0-f])\\x[0-f][0-f]\2\3(?!\3\5)){7,}"
#dialogue_pointer_regex = r"\\x1e\\xb8\\x([0-f][0-f])\\x([0-f][0-f])\\x50" # Starts with \\x1e\\xb8 , then the thing to be captured, then \\x50.
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
    for index, block in enumerate(file_blocks[file]):
        lo, hi = block
        if (text_offset >= lo) and (text_offset < hi):
            return index
        #else:
        #    # It returns None when the text is overflowing. Rather,
        #    # you want to get the previous block.
        #    if text_offset > 0:
        #        print "trying current_block at", hex(text_offset-60)
        #        return get_current_block(text_offset-60, file)
        #    else:
        #        return None


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
        return [hex(i/2) for i in xrange(len(a)) if a[i] != b[i]]
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