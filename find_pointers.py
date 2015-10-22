import re

files = ['ST1.EXE', 'OPENING.EXE']

pointers = {}
# hex loc: (hex a, hex b)

pointer_regex = r"(\\x[0-f][0-f]\\x[0-f][0-f](\\x[0-f][0-f]\\x[0-f][0-f]))(\\x[0-f][0-f]\\x[0-f][0-f]\2){5,}"

def unpack(s, t):
    return (t * 0x100) + s
    
def pack(h):
    s = h % 0x100
    t = h // 0x100
    return (s, t)
    
def find_pointers():
    p = re.compile(pointer_regex)
    for file in files:
        in_file = open(file, 'rb')
        text = in_file.read()
        text.decode('shift_jis', errors='ignore').encode('utf-8')
        print repr(text)
        tables = p.findall(repr(text))
        print tables
        
find_pointers()