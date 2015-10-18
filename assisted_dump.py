# Makes use of a tool called SJIS_Dump which deals with the encoding better.

# Use SJIS-Dump to dump all the SJIS from the game's source files.
# Parse the dump into (source, offset, dump).
# Insert the text into the excel spreadsheet. Columns: File, Offset, Japanese, English.


# TODO: SJIS-Dump might not be the best tool for the job - like in ST1.EXE:0xfb00, it gets off-by-one
# and reads some pretty innocuous hiragana as really dense meaningless kanji. 
# (Like, it reads 82-E9 82-E6 as ...E9-82 E6-82.)
# This is really hard to recognize and will result in a bad translation.
# I should look into writing a script to do this myself, or at least see if I can modify SJIS-Dump.

# TODO: Add a field for the pointers.
# TODO: Add control codes?

import subprocess
import codecs
import xlsxwriter

# Dict of files and dump blocks.
files = { 'OPENING.EXE': ((0x4dda, 0x5868),),
          'ST1.EXE': ((0xd873, 0x1240d),),
          'ST2.EXE': ((0xc23b, 0x1085e),),
          'ST3.EXE': ((0xb49d, 0xee70),),
          'ST4.EXE': ((0xe263, 0x1688a),),          }



#files = ['OPENING.EXE', '46.EXE', 'ST1.EXE', 'ST2.EXE', 'ST3.EXE', 'ST4.EXE', 'ST5.EXE',
#         'ST6.EXE', 'ST5S1.EXE', 'ST5S2.EXE', 'ST5S3.EXE', 'SEND.DAT', 'SINKA.DAT', 'ENDING.EXE']

workbook = xlsxwriter.Workbook('shinkaron_dump.xlsx')
worksheet = workbook.add_worksheet()

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
    
workbook.close()