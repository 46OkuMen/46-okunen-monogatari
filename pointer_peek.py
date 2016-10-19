"""
Takes a file and an offset of a pointer and returns what that pointer points to, location and snippet.
"""

import sys
import os
from utils import SRC_PATH, DEST_PATH, unpack
from rominfo import POINTER_CONSTANT

def ensure_src_file_path(str):
    try:
        f = open(str, 'r')
        f.close()
    except IOError:
        str = os.path.join(SRC_PATH, str)
        f = open(str, 'r')
        f.close()
    return str

def ensure_dest_file_path(str):
    try:
        f = open(str, 'r')
        f.close()
    except IOError:
        str = os.path.join(DEST_PATH, str)
        f = open(str, 'r')
        f.close()
    return str

def word_at_offset(filename, offset):
    #filename = ensure_src_file_path(filename)
    with open(filename, 'rb') as f:
        result = ""
        f.seek(offset)
        data = f.read(2)
        for b in data:
            result += "%02x" % ord(b)
        return unpack(result[0:2], result[2:])

def text_at_offset(filename, offset):
    try:
        f = open(filename, 'rb')
    except TypeError:
        filename = os.path.join(DEST_PATH, filename.filename)
        f = open(filename, 'rb')

    f.seek(offset)
    result = ""
    data = f.read(1)
    while ord(data) != 00:   # END control code
        result += data
        data = f.read(1)
    f.close()
    return result

def text_with_pointer(filename, pointer_offset):
    pointer_offset = int(pointer_offset, 16)
    constant = POINTER_CONSTANT[filename]
    try: 
        f = open(filename, 'rb')
        f.close()
    except IOError:
        filename = os.path.join(DEST_PATH, filename)

        destination = word_at_offset(filename, pointer_offset) + constant

        return text_at_offset(filename, destination)


if __name__ == '__main__':
    filename = sys.argv[1]
    constant = POINTER_CONSTANT[filename]

    offset = int(sys.argv[2], 16)
    filepath = os.path.join(DEST_PATH, filename)
    pointer_value =  word_at_offset(filepath, offset)

    print "value:", hex(pointer_value)
    if pointer_value == 0xb81e:
        # Lots of things listed in the pointer spreadhseet are 2 too high, and point to the "ptr begin" ctrl code.
        print "I think you meant %s" % offset
        pointer_value = word_at_offset(filepath, offset+2)
    pointed_location = pointer_value + constant
    print "points to:", hex(pointed_location)
    print text_at_offset(filepath, pointed_location)
