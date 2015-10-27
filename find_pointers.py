# TODO: Someitmes it gets tripped up by a consistent 2nd byte of the pointer, and it counts it as a delimiter. How to avoid this?
# TODO: Define a function to identify pointers that point to other pointer tables - identify whether some segment of the tables' unpacked values are increasing or decreasing by 0x4 the whole time.

import re

files = ['ST1.EXE',]

file_blocks = [ ('OPENING.EXE', ((0x4dda, 0x5868),),),
('ST1.EXE', ((0xd873, 0xd933), (0xd984, 0x10f85), (0x10fca, 0x11595), (0x117c7, 0x119a3), (0x11d42, 0x1204e))),
          ('ST2.EXE', ((0xc23b, 0xdd4f), (0xde35, 0xfaa0), (0xfae4, 0xfe50), (0x10004, 0x101df), (0x10570, 0x1087b))),
          ('ST3.EXE', ((0xb49d, 0xb548), (0xb58a, 0xdb3a), (0xdb7e, 0xe2d5), (0xe617, 0xe7f3), (0xeb82, 0xee8e))),
          ('ST4.EXE', ((0xe262, 0xe29e), (0xe2f4, 0x120a0), (0x12114, 0x149e4), (0x14a28, 0x15a1e), (0x16031, 0x1620d), (0x1659c, 0x168a8))),
          ('ST5.EXE', ((0xcc02, 0xcc5e), (0xccf2, 0xcd2e), (0xcd74, 0xeabe), (0xebc3, 0x107a3), (0x107e6, 0x11466), (0x11976, 0x11b53), (0x11ef2, 0x121fe))),
          ('ST5S1.EXE', ((0x24e8, 0x3af1),),),
          ('ST5S2.EXE', ((0x23f9, 0x3797),),),
          ('ST5S3.EXE', ((0x3db9, 0x4ed0),),),
          ('ST6.EXE', ((0xa4f1, 0xa55b), (0xa59c, 0xccd1), (0xcd14, 0xce25), (0xcede, 0xd0bb), (0xd44a, 0xd756))),
          ('ENDING.EXE', ((0x3c4e, 0x4b1f),)),
          ('SINKA.DAT', ((0x0000, 0x874a),)),
          ('SEND.DAT', ((0x000, 0x8740),)),
          ('46.EXE', ((0x93e8, 0x946d), (0x94b9, 0x971b), (0x9cb8, 0xa07a)))
]

pointers = {}
# hex loc: (hex a, hex b)

pointer_regex = r"(\\x[0-f][0-f]\\x[0-f][0-f](\\x[0-f][0-f]\\x[0-f][0-f]))(\\x[0-f][0-f]\\x[0-f][0-f]\2){2,}"

def unpack(s, t):
    return (t * 0x100) + s
    
def pack(h):
    s = h % 0x100
    t = h // 0x100
    return (s, t)
    
def go_to_pointer(pointer, offset):
    return unpack(pointer[0], pointer[1]) + offset
    
def find_pointers():
    p = re.compile(pointer_regex)
    for file in files:
        in_file = open(file, 'rb')
        print file
        bytes = in_file.read()
        #text.decode('shift_jis', errors='ignore').encode('utf-8')
        only_hex = ""
        for c in bytes:
            #print ord(c)
            only_hex += "\\x%02x" % ord(c)
        #print only_hex
        #print bytes.encode('hex')
        tables = p.finditer(only_hex)
        for table in tables:
            last_part = table.group(3).split('\\x')
            #print last_part
            if last_part[1] == last_part[2] == last_part[3] == last_part[4]: # ignore FFFFFFFFFF sections
                pass
            elif "\\x00\\x00\\x00\\x00" in table.group(0):  # sometimes they sneak by. catch them here
                pass
            else:
                #print table.group(0)
                start = table.start() / 4 # divide by four, since 4 characters per byte in our dump)
                stop = table.end() / 4
                count = (stop - start) / 4 # div by 4 again, since 4 bytes per pointer
                delimiter = table.group(2)
                #print table.group(0)
                #print delimiter
                values = []
                # Can't do this - sometimes part of the delimiter shows up in the pointer itself! (10-00-00-00)
                 #values = table.group(0).split(delimiter)
                # So just slice the string into the first two bytes.
                for x in range(0, len(table.group(0))-15, 16):
                    pointer_string = table.group(0)[x:x+8]
                    pointer_tuple = pointer_string.split('\\x')[1], pointer_string.split('\\x')[2]
                    values.append(pointer_tuple)
                #print values
                pointers = []
                for (first, second) in values:
                    pointers.append(hex(unpack(int(first, 16), int(second, 16))))
                print str(count) + " pointers at " + hex(start) + ", delimiter: " + delimiter
                print pointers
                # next, calculate the diffs. and figure out if it's just 4 over and over
        #out_file = open('dump_' + file, 'w+')
        #out_file.write(only_hex)
        
def find_string_offsets():
    for (file, blocks) in file_blocks:
        diffs_filename = "diffs_" + file
        diffs_out_file = open(diffs_filename, "w")
        for block in blocks:
            diffs_out_file.write(str(file) + " " + str(block) + "\n")
            
            pointeds = []
            diffs = [0,]
            
            block_start = block[0]
            block_stop = block[1]
            block_length = block_stop - block_start
            
            in_file = open(file, 'rb')
            in_file.seek(block_start)
            bytes = in_file.read(block_length)
            only_hex = ""
            
            for c in bytes:
                only_hex += "\\x%02x" % ord(c)
                
            strings = only_hex.split('\\x00')

            for s in strings:
                if s:
                    string_start = only_hex.index(s)
                    offset = hex(block_start + (string_start / 4))
                    pointeds.append(offset)
                    
                    try:
                        print pointeds[-1]
                        print pointeds[-2]
                        print "\n"
                        diffs.append(int(pointeds[-1], 16) - int(pointeds[-2], 16))
                    except IndexError:
                        diffs.append(0)
            
            for d in range(0, len(diffs)-7, 8):
                diffs_out_file.write(str(diffs[d]) + " " + str(diffs[d+1]) + " " + str(diffs[d+2]) + " " + str(diffs[d+3]) + str(diffs[d+4]) + " " + str(diffs[d+5]) + " " + str(diffs[d+6]) + " " + str(diffs[d+7]) + " " + "\n")
            diffs_out_file.write("\n")
        diffs_out_file.close()
 
find_pointers() 
#find_string_offsets()