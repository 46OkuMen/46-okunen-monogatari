# This seems like a much better way of doing it.
# TODO: Figure out how to get rid of the garbage.
# 1. ASCII text ("ISIWAKU.GDT")
# 2. Control codes.
# 3. Still more random garbage.

import string
from utils import file_blocks

for file in blocks:
    in_file = open(file[0], 'rb')
    out_file = open("dump_" + file[0], "w")
    for block in file[1]:
        block_length = block[1] - block[0]
        in_file.seek(block[0], 0)
        text = in_file.read(block_length)
        segments = text.split("\x00")
        for segment in segments:
            segment.decode('shift_jis', errors='ignore').encode('utf-8')
            #print repr(segment)
            # Sub in control codes.
            #clean = segment.replace('\x0d', '<LINE>\n').replace('\x0a', '<LINE>\n').replace('\x13', '<WAIT>\n') 
            # Delete the just-ASCII lines, but keep ASCII within lines of SJIS text.
            # If there's any string left when you remove the ASCII, insert the line.
            #without_ascii = filter(lambda x: x not in string.printable, clean)
            
            #if clean.strip() and without_ascii.strip():
            #    out_file.write(clean + "\n")
                #out_file.write(repr(clean) + "\n")
            out.file.write(segment + "\n")
    