# TODO: Someitmes it gets tripped up by a consistent 2nd byte of the pointer, and it counts it as a delimiter. How to avoid this?
# Is there any way to perform the regex search from right-to-left?
# TODO: Define a function to identify pointers that point to other pointer tables - identify whether some segment of the tables' unpacked values are increasing or decreasing by 0x4 the whole time.

import re
from utils import file_blocks
from utils import pointer_regex


files = ['ST1.EXE', 'OPENING.EXE']

pointers = {}
# hex loc: (hex a, hex b)
    
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
            last_part = table.group(4).split('\\x')
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
                delimiter = table.group(2) + table.group(3)
                #print table.group(0)
                #print delimiter
                values = []
                # Can't just do this - sometimes part of the delimiter shows up in the pointer itself! (10-00-00-00)
                 #values = table.group(0).split(delimiter)
                # So just slice the string into the first two bytes.
                for x in range(0, len(table.group(0))-15, 16):
                    pointer_string = table.group(0)[x:x+8]
                    pointer_tuple = pointer_string.split('\\x')[1], pointer_string.split('\\x')[2]
                    values.append(pointer_tuple)
                pointers = []
                for (first, second) in values:
                    pointers.append(hex(unpack(int(first, 16), int(second, 16))))
                print str(count) + " pointers at " + hex(start) + ", delimiter: " + delimiter
                pointers.sort()
                print pointers
                # next, calculate the diffs. and figure out if it's just 4 over and over
                diffs = []
                for pointer in range(0, len(pointers)-1):
                    diffs.append(int(pointers[pointer+1],16) - (int(pointers[pointer],16)))
                print diffs
                
        #out_file = open('dump_' + file, 'w+')
        #out_file.write(only_hex)
        
def find_string_offsets():
    for (file, blocks) in file_blocks:
        diffs_filename = "diffs_" + file
        diffs_out_file = open(diffs_filename, "w")
        
        text_filename = "text_" + file
        text_out_file = open(text_filename, 'w')
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
                    
                    s.strip('\\x').decode('shift_jis', errors='ignore').encode('utf-8')
                    text_out_file.write(s + "\n")
            
            pointeds.sort()
            print pointeds
            for i in range(0, len(pointeds)-1):
                diff = int(pointeds[i+1], 16) - int(pointeds[i], 16)
                if diff == 0 or diff > 1000:
                    print i, pointeds[i+1], pointeds[i], diff
                diffs.append(diff)
            print diffs
            
            for d in range(0, len(diffs)-7, 8):
                diffs_out_file.write(str(diffs[d]) + " " + str(diffs[d+1]) + " " + str(diffs[d+2]) + " " + str(diffs[d+3]) + str(diffs[d+4]) + " " + str(diffs[d+5]) + " " + str(diffs[d+6]) + " " + str(diffs[d+7]) + " " + "\n")
            diffs_out_file.write("\n")
        diffs_out_file.close()
 
#find_pointers() 
find_string_offsets()