# Makes use of a tool called SJIS_Dump which deals with the encoding better.

# Execute the command ".\SJIS_Dump OPENING.EXE opening 4 0"
# Clean that dump of any characters that freak out my SJIS decoder.
# Parse the dump into offset:text pairs.
# Insert the text into the excel spreadsheet. Columns: File, Offset, Japanese, English.

import subprocess
import codecs
import xlsxwriter

files = ['OPENING.EXE', '46.EXE', 'ST1.EXE', 'ST2.EXE', 'ST3.EXE', 'ST4.EXE', 'ST5.EXE',
         'ST6.EXE', 'ST5S1.EXE', 'ST5S2.EXE', 'ST5S3.EXE', 'SEND.DAT', 'SINKA.DAT', 'ENDING.EXE']
# Make sure the files aren't hidden in Windows!

workbook = xlsxwriter.Workbook('shinkaron_dump.xlsx')
worksheet = workbook.add_worksheet()

worksheet.set_column('A:A', 30)
worksheet.set_column('C:C', 80)
worksheet.set_column('D:D', 90)

excel_row = 0

for file in files:
    file_dump = "dump_" + file
    subprocess.call(".\SJIS_Dump %s %s 3 0" % (file, file_dump))
    # What is the optimal sensitivity? Smaller = lesser chance of missing text,
    # but more image-file-kanji garbage and more SJIS codes will break the parser.
    # Sorting the dump helps the garbage problem - garbage regions are collected in one place.
    # Just gotta find more parser-breaking codes and go down to sensitivity=2, for the 2-kanji stats.

    # need to remove characters like E67F that freak the SJIS parser out for some reason
    # TODO: Here is the place to do post-processing, like inserting control codes, etc
    clean_bytes_string = ""

    with open(file_dump, 'rb') as f:
        byte = f.read(2)
        while byte !="":
            hx = byte.encode('hex')
            if hx != "e67f" and hx != "7fe6" and hx != "e97f" and hx != "8259":  # this'll leave a spare e6 and 7f on either side if it's like "XX-E6-7F-YY", but it's a garbage line to begin with
                clean_bytes_string += byte
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
            else:
                print "Found an E67F, got rid of it"
            #print byte.encode('hex')
            byte = f.read(2)
    f.close()
    #print clean_bytes_string

    clean_bytes = bytearray(clean_bytes_string)

    with open(file_dump, 'wb') as f:
        f.write(clean_bytes)
    f.close()
    # Now the SJIS-Dump is clean, parse it and deal with it in memory.
        
    dump = []

    fo = codecs.open(file_dump, "r", encoding='shift_jis')
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