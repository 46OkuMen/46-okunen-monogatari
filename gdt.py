from PIL import Image
from utils import unpack

def pixels_from_run_length(file, offset):
    pass
    
def pixels_from_position(file, offset):
    pass
    
def gdt_to_bmp(source):
    fo = open(source, 'rb')
    bytes = fo.read()
    # fhex = file hex
    fhex = []
    for byte in bytes:
        fhex.append("%02x" % ord(byte))
    print fhex
    if fhex[0] != '88'  or fhex[1] != 'e4':
        print "Not a valid .GDT file"
    
    imgx = unpack(fhex[6], fhex[7])
    imgy = unpack(fhex[8], fhex[9]) * 2
    
    img = Image.new('RGB', (imgx, imgy))
    
    # img divided into 8-column-wide blocks.
    blocks = []
    
    blank_block = [[0]*8 for i in range(imgy)]
    print blank_block
    
    # i is the position. start right after the header ends (at 11).
    i = 12
    
    while i <= len(fhex):
        if fhex[i] == fhex[i+1] == fhex[i+2] == '00':
            pass
    
    
    
gdt_to_bmp('TITLE1.GDT')