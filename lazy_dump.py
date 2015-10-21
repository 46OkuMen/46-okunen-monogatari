# This seems like a much better way of doing it.
# TODO: Figure out how to get rid of the garbage.
# 1. ASCII text ("ISIWAKU.GDT")
# 2. Control codes.
# 3. Still more random garbage.

import string

files = [('ST1.EXE', ((0xd873, 0xd933), (0xd984, 0x10f85), (0x10fca, 0x11565), (0x11839, 0x119a3), (0x11d42, 0x1204e),),),

        ]

for file in files:
    in_file = open(file[0], 'rb')
    out_file = open("dump_" + file[0], "w")
    
    
    for block in file[1]:
        block_length = block[1] - block[0]
        in_file.seek(block[0], 0)
        text = in_file.read(block_length)
        segments = text.split("\x00")
        for segment in segments:
            segment.decode('shift_jis', errors='ignore').encode('utf-8')
            print repr(segment)
            clean = segment.replace('\x0d', '<LINE>\n').replace('\x0a', '<LINE>\n').replace('\x13', '<WAIT>\n') 
            if clean.strip():
                out_file.write(clean + "\n")
    
    