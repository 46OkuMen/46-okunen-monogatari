import xlsxwriter
import codecs

hex_full = ""
hex_chunks = {}

offsets = [(0x4de0, 0x539a), (0x53A9, 0x555D), (0x5657, 0x5868)]

with open('./A/OPENING.EXE', 'rb') as f:
    for chunk in iter(lambda: f.read(), b''):
        hex_full = chunk.encode('hex')
    f.close()
    #print hex_text
    for (start, stop) in offsets:
        section_text = hex_full[(start*2):(stop*2)+1]
        chunks = section_text.split('00')   # TODO: Test on "80-0B" or similar
        # This is definitely giving me some weird results, look for a better way to split it.
        #print chunks
        #offset = start + length of all previous chunks
        offset = start
        print hex(offset)
        length_of_previous_chunks = 0
        for chunk in chunks:
            offset += length_of_previous_chunks
            hex_chunks[hex(offset)] = chunk
            length_of_previous_chunks += ((len(chunk)/2) + 2)   # 2 chars in a hex pair, add 2 for the 00
            print hex(offset)
            print chunk
            print length_of_previous_chunks
            print "\n"
            
        
    #print hex_chunks
        
# open "OPENING.EXE" in binary mode
# encode it into hex
# 
# split the chunk into smaller chunks by the end character (0x00)
# (make sure to keep track of the original offsets)
# remove the '.GDT' strings

# excel columns: file, offset, japanese, english

# Hexdump sample from c2.com
"""
 import sys

 def hexdump(fname, start, end, width):
    for line in get_lines(fname, int(start), int(end), int(width)):
        nums = ["%02x" % ord(c) for c in line]
        txt = [fixchar(c) for c in line]
        print " ".join(nums), "".join(txt)

 def fixchar(char):    
    from string import printable
    if char not in printable[:-5]:
        return "."
    return char

 def get_lines(fname, start, end, width):
    f = open(fname, "rb")
    f.seek(start)
    chunk = f.read(end-start)
    gap = width - (len(chunk) % width)
    chunk += gap * '\000'
    while chunk:
        yield chunk[:width]
        chunk = chunk[width:]

 hexdump('./A/OPENING.EXE', 0x4de0, 0x539a, 16)
 """