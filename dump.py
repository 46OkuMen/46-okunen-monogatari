dump = {}
# open "OPENING.EXE" as bytes/hex
# look for text that says ".GDT " = 2E-47-44-54-00
# create a new key-value pair. key: filename.GDT, value: []
# for every two-byte pair that isn't a filename or a 00:
#     convert the word from shift-JIS -> Unicode
#     append Unicode string to dump[filename.GDT]