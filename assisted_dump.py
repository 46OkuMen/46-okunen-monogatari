# Makes use of a tool called SJIS_Dump which deals with the encoding better.

# Use SJIS-Dump to dump all the SJIS from the game's source files.
# Parse the dump into (source, offset, dump).
# Insert the text into the excel spreadsheet. Columns: File, Offset, Japanese, English.

# TODO: SJIS-Dump might not be the best tool for the job - like in ST1.EXE:0xfb00, it gets off-by-one
# and reads some pretty innocuous hiragana as really dense meaningless kanji. 
# (Like, it reads 82-E9 82-E6 as ...E9-82 E6-82.)
# This is really hard to recognize and will result in a bad translation.
# I should look into writing a script to do this myself, or at least see if I can modify SJIS-Dump.

# Errors:
# ST1.EXE, 0xdefd-dfd00
# ST1.EXE, 0xfb00
# ST1.EXE, 0xe000-e001
# ST1.EXE, 0x100ff-10100
# ST1.EXE, 0x10e00
# ST1.EXE, 0x113df-113e0

# ST2.EXE, 0xc900
#            d700
#            d901
#            da00
#            db00
#            dc00

# ST3.EXE, 0xbb00

# ST4.EXE, 0x120b4 (just a random piece of kanji, fix with the ranges)

# So these errors only really show up at 00, sometimes at 0. Why???
# Answer: SJIS_Dump has a buffer 0x100 long. So it'll always misread the 0x100th byte whenever there's carryover.
# I'll just modify the source code to have a large enough buffer.
# That seems to have weird effects - when it's too large, it just dumps the same few sequences a lot... weird.

# TODO: Add a column for the string's pointer location, if there is one.
# TODO: Add control codes?

import os
import subprocess
import codecs
import xlsxwriter

# Dict of files and dump blocks.
files = { 'OPENING.EXE': ((0x4dda, 0x5868),),
          'ST1.EXE': ((0xd873, 0x117df), (0x11838, 0x119a3), (0x11d42, 0x1240d),),
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
}

workbook = xlsxwriter.Workbook('shinkaron_dump.xlsx')
worksheet = workbook.add_worksheet()

# Set column sizes to something reasonable.
worksheet.set_column('A:A', 20)
worksheet.set_column('C:C', 80)
worksheet.set_column('D:D', 90)

excel_row = 0

for file, blocks in files.iteritems():
    file_dump = "dump_" + file
    subprocess.call(".\SJIS_Dump %s %s 1 0" % (file, file_dump))
    # How small to go? Gotta minimize the signal-to-noise ratio to avoid annoying the translator.
    # But there are definitely some legit/important strings that are just 2 kanji (stats)
        
    dump = []
    # SJIS-Dump spits out some garbage characters not included in SJIS specification.
    # Rather than try to get rid of them, just ignore all decoding errors and it'll be fine.
    # Also, sticking to the ranges that have been mapped out will reduce the noise.
    fo = codecs.open(file_dump, "r", encoding='shift_jis', errors='ignore') 

    lines = fo.readlines()

    for n in range(0, len(lines)-1, 3):
        offset_string = lines[n][11:].rstrip()     # first line of three, minus "Position : ", minus "\n"
        offset = hex(int(offset_string, 16))
    
        text = lines[n+1]
    
        for block in blocks:
            if  block[0] <= int(offset, 16) < block[1]:
                dump.append((file, offset, text))

    for snippet in dump:
        # excel cols: File, Offset, Japanese, English
        worksheet.write(excel_row, 0, snippet[0])
        worksheet.write(excel_row, 1, snippet[1])
        worksheet.write(excel_row, 2, snippet[2])
        excel_row += 1
    
    fo.close()
    
    #os.remove(file_dump)
    
workbook.close()