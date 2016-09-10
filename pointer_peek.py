"""
Takes a file and an offset of a pointer and returns what that pointer points to, location and snippet.
"""

import sys
import os
from utils import DEST_PATH, unpack
from rominfo import POINTER_CONSTANT

def word_at_offset(filename, offset):
    with open(filename, 'rb') as f:
        f.seek(offset)
        result = ""
        data = f.read(2)
        for b in data:
            result += "%02x" % ord(b)
        return unpack(result[0:2], result[2:])

def text_at_offset(filename, offset):
    with open(filename, 'rb') as f:
        f.seek(offset)
        result = ""
        data = f.read(100)
        return data + "..."

if __name__ == '__main__':
    print sys.argv
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
