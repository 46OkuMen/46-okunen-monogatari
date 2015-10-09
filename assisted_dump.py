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
    subprocess.call(".\SJIS_Dump %s %s 5 0" % (file, file_dump))

    # need to remove characters like E67F that freak the SJIS parser out for some reason
    # TODO: Here is the place to do post-processing, like inserting control codes, etc
    clean_bytes_string = ""

    with open(file_dump, 'rb') as f:
        byte = f.read(2)
        while byte !="":
            if byte.encode('hex') != "e67f":
                clean_bytes_string += byte
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
        
    dump = {}

    fo = codecs.open(file_dump, "r", encoding='shift_jis')
    lines = fo.readlines()

    # TODO: good way to sort these before inserting? (Or is it better to just sort in excel?)
    for n in range(0, len(lines)-1, 3):
        offset_string = lines[n][11:].rstrip()     # first line of three, minus "Position : ", minus "\n"
        offset = hex(int(offset_string, 16))
    
        text = lines[n+1]
    
        dump[(file, offset)] = text

    for source, text in dump.iteritems():
        # excel cols: File, Offset, Japanese, English
        worksheet.write(excel_row, 0, source[0])
        worksheet.write(excel_row, 1, source[1])
        worksheet.write(excel_row, 2, text)
        excel_row += 1
    
    fo.close()
    
workbook.close()