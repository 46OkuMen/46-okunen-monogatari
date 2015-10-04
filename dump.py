import xlsxwriter
import codecs

hex_full = ""
hex_chunks = {}

offsets = [(0x4de0, 0x539a), (0x53a9, 0x555d), (0x55e9, 0x5638), (0x5657, 0x5868)]

with open('./A/OPENING.EXE', 'rb') as f:
    # Encode the exe binary into hex.
    for chunk in iter(lambda: f.read(), b''):
        hex_full = chunk.encode('hex')
    f.close()
    
    # Run through the offset ranges and grab sections separated by 0x00.
    for (start, stop) in offsets:
        section_text = hex_full[(start*2):(stop*2)]  # hex size = twice the binary size.
        chunks = section_text.split('00')   # TODO: Test on "80-0B" or similar
        offset = start
        length_of_previous_chunks = 0
        for chunk in chunks:
            offset = start + length_of_previous_chunks
            hex_chunks[("OPENING.EXE", hex(offset))] = chunk
            length_of_previous_chunks += ((len(chunk)+2)/2)   # 2 chars in a hex pair, add 2 for the removed 0x00
            #print hex(offset)
            #print chunk
            #print hex(length_of_previous_chunks)
            #print "\n"
        
            
        
    #print hex_chunks
        
# open "OPENING.EXE" in binary mode
# encode it into hex
# 
# split the chunk into smaller chunks by the end character (0x00)
# (make sure to keep track of the original offsets)
# if the text is '' or '*.GDT', remove it

# excel columns: file, offset, japanese, english