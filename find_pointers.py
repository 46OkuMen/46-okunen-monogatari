pointers = {}
# hex loc: (hex a, hex b)

def unpack(s, t):
    return (t * 0x100) + s
    
def pack(h):
    s = h % 0x100
    t = h // 0x100
    return (s, t)