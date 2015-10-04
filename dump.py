# Python's shift-jis codec has not proven terribly useful - I may be better off using the
# shinkaron.tbl file in a maketrans

# Or maybe just try to keep it as bytes the whole time?
# Or use a string but with \x ?

import xlsxwriter
import codecs
import string

hex_full = ""
hex_chars = ""
hex_chunks = {}

offsets = [(0x4de0, 0x539a), (0x53a9, 0x555d), (0x55e9, 0x5638), (0x5657, 0x5868)]

with open('./A/OPENING.EXE', 'rb') as f:
    # Encode the exe binary into hex.
    for binary in iter(lambda: f.read(), b''):
        hex_full = binary.encode('hex')
    f.close()
    
    hex_chars = [text[i:i+4] for i in range(0, len(text), 4]
    
    # Run through the offset ranges and grab sections separated by 0x00.
    for (start, stop) in offsets:
        section_text = hex_full[(start*2):(stop*2)]  # hex size = twice the binary size.
        chunks = section_text.split('00')   # TODO: Splits inappropriately at "B00A" etc
        offset = start
        length_of_previous_chunks = 0
        for chunk in chunks:
            #chunk = chunk + '00'
            offset = start + length_of_previous_chunks
            hex_chunks[("OPENING.EXE", hex(offset))] = chunk
            length_of_previous_chunks += ((len(chunk)+2)/2)   # 2 chars in a hex pair, add 2 for the removed 0x00
            #print hex(offset)
            #print chunk
            #print "length: " + str(len(chunk))
            #print hex(length_of_previous_chunks)
            #print "\n"
        
workbook = xlsxwriter.Workbook('opening_dump.xlsx')
worksheet = workbook.add_worksheet()

worksheet.set_column('C:C', 50)

row = 0
col = 0

for source, text in hex_chunks.iteritems():
    # source[0] = file, source[1] = offset
    #print text
    try:
        print text
        print bytearray.fromhex(text)
    except TypeError: # sometimes there are two odd-length chars in a row; fix that for real
        #print bytearray.fromhex(text[0:len(text)-1])
        pass
    #bytearray = [text[i:i+4] for i in range(0, len(text), 4]
        
    worksheet.write(row, col+3, text.decode('shift-jis').encode('utf-8'))
    row += 1
    
    
workbook.close()
        
# open "OPENING.EXE" in binary mode
# encode it into hex
# 
# split the chunk into smaller chunks by the end character (0x00)
# (make sure to keep track of the original offsets)
# if the text is '' or '*.GDT', remove it

# excel columns: file, offset, japanese, english