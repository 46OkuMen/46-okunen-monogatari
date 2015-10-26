# Makes use of a tool called SJIS_Dump which deals with the encoding better.

# Use SJIS-Dump to dump all the SJIS from the game's source files.
# Parse the dump into (source, offset, dump).
# Insert the text into the excel spreadsheet. Columns: File, Offset, Japanese, English.

# SJIS_Dump on its own messes up any file larger than 0x100 bytes, since its internal buffer is
# that size. It splits two-byte characters across multiple buffers, and as a result, it mis-encodes them.
# Trying to alter the C++ program to have a larger buffer had some odd results, so my solution:
# Split up the source files themselves into 0x100 and smaller chunks by splitting them into the
# game text lines themselves, which are never longer than the game window.

# TODO: Look for garbage.
# TODO: Where is the weird ASCII at the end of SINKA.DAT strings coming from?

# TODO: Print progress.

# TODO: Add a column for the string's pointer location, if there is one.
# TODO: Add control codes?

import os
import subprocess
import codecs
import xlsxwriter

# Game contains disks.
# Disks contain files.
# Files contain blocks.
# Blocks contain snippets, separated by \x00. (<END> tags)
# Snippets contain strings, separated by \x0a or \x0d. (line beaks)
        

# Dict of files and dump blocks.
files = [ ('OPENING.EXE', ((0x4dda, 0x5868),),),
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

workbook = xlsxwriter.Workbook('shinkaron_dump.xlsx')
worksheet = workbook.add_worksheet()

# Set column sizes to something reasonable.
worksheet.set_column('A:A', 20)
worksheet.set_column('C:C', 80)
worksheet.set_column('D:D', 90)

excel_row = 0

dump_files = []

for file in files:
    for (block_start, block_end) in file[1]:
        dat_dump = file[0] == 'SINKA.DAT' or file[0] == 'SEND.DAT'
        block_length = block_end - block_start
        in_file = open(file[0], 'rb')
        in_file.seek(block_start)
        bytes = in_file.read(block_length)
        only_hex = ""
        for c in bytes:
            only_hex += "\\x%02x" % ord(c)
        if dat_dump:
            snippets = only_hex.split('\\x0d\\x0a')  # these don't have any x00s in them
            print snippets
        else:
            snippets = only_hex.split('\\x00')
        for snippet in snippets:
            if snippet and len(snippet) > 4:       # at least one byte representation
                snippet_start = only_hex.index(snippet)
                offset = hex(block_start + (snippet_start / 4))
                snippet_filename = "snippet_" + offset + "_" + file[0]
                snippet_file = open(snippet_filename, 'wb')
                snippet_bytes = snippet.replace('\\x', '').decode('hex')
                snippet_file.write(snippet_bytes)
                snippet_file.close()
                
                snippet_dump = "dump_" + snippet_filename
                if dat_dump:
                    subprocess.call(".\SJIS_Dump %s %s 1 1" % (snippet_filename, snippet_dump))
                else:
                    subprocess.call(".\SJIS_Dump %s %s 1 0" % (snippet_filename, snippet_dump))
                
                dump_files.append(snippet_dump)
                os.remove(snippet_filename)
        
dump = []
#print dump_files
#print len(dump_files)
        
for file in dump_files:
    # file.split('_') is ('dump', 'snippet', sourcefile, offset)
    source = file.split('_')[3]
    offset = file.split('_')[2]

    fo = codecs.open(file, "r", encoding='shift_jis', errors='ignore') 

    lines = fo.readlines()

    for n in range(0, len(lines)-1, 3):
        offset_string = lines[n][11:].rstrip()     # first line of three, minus "Position : ", minus "\n"
        offset_within_snippet = hex(int(offset_string, 16))
        
        try:
            total_offset = int(offset, 16)
        except TypeError:
            total_offset = offset
            
        total_offset += int(offset_within_snippet, 16)
            
        total_offset = hex(total_offset)
        #print total_offset
        
        text = lines[n+1]
    
        dump.append((source, total_offset, text))
        
    fo.close()

# Access this in a separate for loop, since there might be multiple texts in a snippet
for snippet in dump:
    # excel cols: File, Offset, Japanese, English
    worksheet.write(excel_row, 0, snippet[0])
    worksheet.write(excel_row, 1, snippet[1])
    worksheet.write(excel_row, 2, snippet[2])
    excel_row += 1

workbook.close()

for file in dump_files:
    #os.remove(file)       #Wonder why it's not finding these?
    pass
