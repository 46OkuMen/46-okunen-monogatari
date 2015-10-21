# Attempting to port the C++ script to python to avoid the weird memory leaks.
# Seems to be more trouble than it's worth, so look at lazy_dump.py instead.

# Open a file in binary mode, see which two-byte sequences correspond to SJIS characters,
# and dump them in a file with their original position as well.

import os
import subprocess
import codecs
import xlsxwriter

# Dict of files and dump blocks.
"""files = { 'OPENING.EXE': ((0x4dda, 0x5868),),
          'ST1.EXE': ((0xd873, 0x119a3), (0x11d42, 0x1240d),),
          'ST2.EXE': ((0xc23b, 0x1085e),),
          'ST3.EXE': ((0xb49d, 0xee70),),
          'ST4.EXE': ((0xe263, 0x1620d), (0x1659c, 0x168a8)),
          'ST5.EXE': ((0xcc01, 0x11465), (0x11977, 0x11b52), (0x11ef2, 0x121fd)),
          'ST5S1.EXE': ((0x24ee, 0x3af1),),
          'ST5S2.EXE': ((0x23f9, 0x3797),),
          'ST5S3.EXE': ((0x3db9, 0x4ed0),),
          'ST6.EXE': ((0xa51a, 0xcdf4),),
          'ENDING.EXE': ((0x3c4e, 0x4b1f),),
          'SINKA.DAT': ((0x0000, 0x874a),),
          'SEND.DAT': ((0x000, 0x8740),),
          '46.EXE': ((0x93e8, 0x946d), (0x94b9, 0x971b), (0x9cb8, 0xa07a))
}"""

files = ["ST1.EXE",]

for file in files:
    #fo = codecs.open(file, "r", encoding='shift_jis', errors='ignore')
    
    in_file = open(file, 'rb')
    out_file = open("dump " + file, "r+")
    file_size = os.path.getsize(file)
    
    threshold = 1
    
    curr_char = 0x0000
    file_pos = 0
    
    buffer = []
    buffer_pos = 0
    
    while file_pos < file_size:
        if contains_letter(buffer, buffer_pos):
            length = letter_length(buffer, buffer_pos)
            temp_buffer_pos = buffer_pos
            
            sjis_sentence = True
            
            i = 0
            while i < threshold:
                if contains_letter(buffer, temp_buffer_pos):
                    length = letter_length(buffer, buffer_pos)
                    temp_buffer_pos += length
                    i += 1
                else:
                    # Not a SJIS sentence, break
                    sjis_sentence = False
                    break
            
            i = 0
            if sjis_sentence:
                out_file.write("Position: 0x" + file_pos + "\n")
                
                while contains_letter(buffer, buffer_pos):
                    length = letter_length(buffer, buffer_pos)
                    temp_buffer_pos = buffer_pos
                    
                    while i < length:
                        out_file.write(
                        
                    
                    
            
            
            
            while 
            
    
    
    
    
    
hex = lambda data: ' '.join('{:02X}'.format(i) for i in data)

str = lambda data: ''.join(31 < i < 127 and chr(i) or '.' for i in data)
    
def contains_letter(buffer, buffer_pos):
    pass