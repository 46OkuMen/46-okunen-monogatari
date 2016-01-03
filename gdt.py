# Command-line encoder/deocder for the .GDT graphics format used in 46 Okunen Monogatari: The Shinka Ron.
# GDT graphics are split into eight-column blocks, then into color planes, then one line at a time.
# The lines themselves are represented by the binary form of each byte.
# Blocks are ended with the byte 10.
# Each color plane of a block has a one-byte prefix describing which encoding method is used:
# 04 (run-length encoding) or 81 (positional encoding).
# Since some lines are repeated 4 times, the bytes ff-84 within a run-length plane mean "run-length of
# the next line is 4."
# 00-00-00 between blocks means an empty block.

# TODO: I think my focus should switch from converting GDT->BMP to converting BMP->GDT.
# GDT->BMP just proves I know how GDTs work. Creating a simple GDT would be a lot more useful for my ends,
# plus easier to develop iteratively since I know how some states work but not others.
# First step might be to convert a red square or something to a GDT.

from PIL import Image
from utils import unpack, gdt_patterns

def pixels_from_byte(color="white", byte):
    bits = bin(int(byte, 16))[2:].zfill(8)
    line = []
    # TODO: Figure out the correct RGB pixel format. Also, figoure out how GDT color planes are determined.
    
    
def get_block_length(remaining_bytes):
    next_04 = remaining_bytes.index('04')
    next_06 = remaining_bytes.index('06')
    next_0c = remaining_bytes.index('0c')
    next_81 = remaining_bytes.index('81')
    next_10 = remaining_bytes.index('10')
    block_length = min(next_04, next_06, next_0c, next_81, next_10)
    return block_length

def pixels_from_run_length(block_bytes):
    # Takes a list of hex strings representing bytes when run-length encoding is specified.
    # Returns a pixel array of the block.
    block = []
    
    # Can't just use a for loop - sometimes we need to consider multiple bytes at once, sometimes not
    block_length = len(block_bytes)
    p = 0
    while p < block_length:
        print block_bytes[p]
        # now, how should I tell the difference between a line and a run-length?
        if block_bytes[p] == '00':
            run_length = int(block_bytes[p+1], 16)
            # append that many black lines; they usually occur with run-lengths
            block.append([0*8 for i in range(run_length)])
            p += 2
        elif block_bytes[p] == 'ff' and block_bytes[p+1] == '84':
            run_length = 4            # hard-coded this way
            line = pixels_from_byte(block_bytes[p+2])
            block.append(line)
            p += 3
        else:
            line = pixels_from_byte(block_bytes[p])
            block.append(line)
            p += 1
    print block
            
        
    
def pixels_from_position(block_bytes):
    pass
    
def pixels_from_pattern(block_bytes):
    pass
    
def gdt_to_bmp(source):
    fo = open(source, 'rb')
    bytes = fo.read()
    # fhex = file hex
    fhex = []
    for byte in bytes:
        fhex.append("%02x" % ord(byte))
    #print fhex
    if fhex[0] != '88'  or fhex[1] != 'e4':
        print "Not a valid .GDT file"
    
    imgx = unpack(fhex[6], fhex[7])
    imgy = unpack(fhex[8], fhex[9]) * 2
    
    img = Image.new('RGB', (imgx, imgy))
    
    # img divided into 8-column-wide blocks.
    blocks = []
    
    blank_block = [[0]*8 for i in range(imgy)]
    
    # i is the position. start right after the header ends (at 11).
    i = 11
    
    while i <= len(fhex):
        print hex(i), fhex[i]
        # 00-00-00: a blank block.
        if fhex[i] == fhex[i+1] == fhex[i+2] == '00':
            blocks.append(blank_block)
            i += 3
            #print blocks
        elif fhex[i] == '04':
            print "run length encoding"
            # find the next 04, 81, or 10 to determine the length of the block
            block_length = get_block_length(fhex[i+1:])
            print block_length, "block length"
            
            block_bytes = fhex[i:i+block_length+1]
            pixels_from_run_length(block_bytes)
            
            i += block_length # TODO: look for off-by-one errors
        elif fhex[i] == '81':
            print "positional encoding"
            block_length = get_block_length(fhex[i+1:])
            block_range = (i, i+block_length)
            
            blocok_bytes = fhex[i:i+block_length+1]
            pixels_from_position(block_bytes)
            i += block_length
    
    
    
gdt_to_bmp('GAMEOVER.GDT')