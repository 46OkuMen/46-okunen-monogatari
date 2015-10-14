# Makes use of a tool called SJIS_Dump which deals with the encoding better.

# Execute the command ".\SJIS_Dump OPENING.EXE opening 2 0"
# Clean that dump of any characters that freak out my SJIS decoder.
# Parse the dump into (source, offset, dump)
# Insert the text into the excel spreadsheet. Columns: File, Offset, Japanese, English.

# TODO: Add a field for the pointers.
# TODO: Add control codes?

import subprocess
import codecs
import xlsxwriter

files = ['OPENING.EXE', '46.EXE', 'ST1.EXE', 'ST2.EXE', 'ST3.EXE', 'ST4.EXE', 'ST5.EXE',
         'ST6.EXE', 'ST5S1.EXE', 'ST5S2.EXE', 'ST5S3.EXE', 'SEND.DAT', 'SINKA.DAT', 'ENDING.EXE']

workbook = xlsxwriter.Workbook('shinkaron_dump.xlsx')
worksheet = workbook.add_worksheet()

worksheet.set_column('A:A', 20)
worksheet.set_column('C:C', 80)
worksheet.set_column('D:D', 90)

excel_row = 0

for file in files:
    file_dump = "dump_" + file
    subprocess.call(".\SJIS_Dump %s %s 2 0" % (file, file_dump))
    # How small to go? Gotta minimize the signal-to-noise ratio to avoid annoying the translator.
    # But there are definitely some legit/important strings that are just 2 kanji (stats)
    # and maybe some one-kanji (the "rest" ability name?).

            # also see if byte.encode('hex') == ...
            # opening: '00' = <ln>
            # sinka.dat = '00-0A-09' = <ln>, '00-0A-00-0A' = <ln><ln>, '0D-0A' = <entry#>
            # send.dat : '0D-0A' = <wait> ?
            # st1.exe : 
            # 0A-13-0A-00: <wait>
            # 13-0A-0A-00: <wait>
            # 0A-13-00:    <wait>
            # 0A-0A-00: <wait>
            # 0A-00: <ln><ln>, keep printing in same window without waiting
            # 13-00: <wait>
            # 16-21: <new window>
            # 16-22: <clear>
            # 16-1E: <clear>
            # 83-65: ?
            # 81-40 or 81-41: just a space. used as a line break in some cases - so looks like line breaks themselves are handled in software
            # 81-41-0A: Line break in the middle of a line
            
            # screen pans down: w, W, [, ], 
            # 3 fish move right: [N...N...N..]. ..
            # may require several passes through the data, looking for the larger chunks first
        
    dump = []
    # SJIS-Dump spits out some garbage characters not included in SJIS specification.
    # Rather than try to get rid of them, just ignore all decoding errors and it'll be fine.
    fo = codecs.open(file_dump, "r", encoding='shift_jis', errors='ignore') 

    lines = fo.readlines()

    for n in range(0, len(lines)-1, 3):
        offset_string = lines[n][11:].rstrip()     # first line of three, minus "Position : ", minus "\n"
        offset = hex(int(offset_string, 16))
    
        text = lines[n+1]
    
        dump.append((file, offset, text))

    for snippet in dump:
        # excel cols: File, Offset, Japanese, English
        worksheet.write(excel_row, 0, snippet[0])
        worksheet.write(excel_row, 1, snippet[1])
        worksheet.write(excel_row, 2, snippet[2])
        excel_row += 1
    
    fo.close()
    
workbook.close()