file_blocks = [ ('OPENING.EXE', ((0x4dda, 0x5868),),),
          ('ST1.EXE', ((0xd873, 0xd933), (0xd984, 0x10f85), (0x10fca, 0x11595), (0x117c7, 0x119a3), (0x11d42, 0x1204e))),
          ('ST2.EXE', ((0xc23b, 0xdd4f), (0xde35, 0xfaa0), (0xfae4, 0xfe50), (0x10004, 0x101df), (0x10570, 0x1087b))),
          ('ST3.EXE', ((0xb49d, 0xb548), (0xb58a, 0xdb3a), (0xdb7e, 0xe2d5), (0xe617, 0xe7f3), (0xeb82, 0xee8e))),
          ('ST4.EXE', ((0xe262, 0xe29e), (0xe2f4, 0x120a0), (0x12114, 0x149e4), (0x14a28, 0x15a1e), (0x16031, 0x1620d), (0x1659c, 0x168a8))),
          ('ST5.EXE', ((0xcc02, 0xcc5e), (0xccf2, 0xcd2e), (0xcd74, 0xeabe), (0xebc3, 0x107a3), (0x107e6, 0x11466), (0x11976, 0x11b53), (0x11ef2, 0x121fe))),
          ('ST5S1.EXE', ((0x24e8, 0x3af1),),),
          ('ST5S2.EXE', ((0x23f9, 0x3797),),),
          ('ST5S3.EXE', ((0x3db9, 0x4ed0),),),
          ('ST6.EXE', ((0xa4f1, 0xa55b), (0xa59c, 0xccd1), (0xcd14, 0xce25), (0xcede, 0xd0bb), (0xd44a, 0xd756))),
          ('ENDING.EXE', ((0x3c4e, 0x4b1f),)),
          ('SINKA.DAT', ((0x0000, 0x874a),)),
          ('SEND.DAT', ((0x000, 0x8740),)),
          ('46.EXE', ((0x93e8, 0x946d), (0x94b9, 0x971b), (0x9cb8, 0xa07a)))
]

pointer_separators = {
        'OPENING.EXE': ("68", "04"), # Sep: 68-04
        'ST1.EXE': ("5e", "0d"), # 5e-0d
        'ST2.EXE': ("f7", "0b"), # fc-0b
        'ST3.EXE': ("20", "0b"),
        'ST4.EXE': ("f4", "0d"),
        'ST5.EXE': ("96", "0c"),
        'ST6.EXE': ("26", "0a"),
        'ST5S1.EXE': ("24", "02"),
        'ST5S3.EXE': ("ae", "03"),
        'ENDING.EXE': ("5a", "03"),
        '46.EXE': ('0a', '0c')
}

pointer_constants = {
        'OPENING.EXE': 0x4a80,  # trying a new one
        'ST1.EXE': 0xd7e0,
        'ST2.EXE': 0xc170,
        'ST3.EXE': 0xb400,
        'ST4.EXE': 0xe140,
        'ST5.EXE': 0xcb60,
        'ST6.EXE': 0xa460,
        'ST5S1.EXE': 0x2440,
        #'ST5S2.EXE': 0x2360,
        'ST5S3.EXE': 0x3ce0,
        'ENDING.EXE': 0x39a0,
        '46.EXE': 0x92c0,
}

old_regex = r"(\\x[0-f][0-f]\\x[0-f][0-f](\\x[0-f][0-f]\\x[0-f][0-f]))(\\x[0-f][0-f]\\x[0-f][0-f]\2){2,}"
pointer_regex = r"(\\x[0-f][0-f]\\x[0-f][0-f](\\x[0-f][0-f])(\\x[0-f][0-f]))((\\x[0-f][0-f])\\x[0-f][0-f]\2\3(?!\3\5)){7,}"

def specific_pointer_regex(first, second):
    return r'(\\x([0-f][0-f])\\x([0-f][0-f])\\x%s\\x%s)' % (first, second)
    
def unpack(s, t):
    s = int(s, 16)
    t = int(t, 16)
    value = (t * 0x100) + s
    return value
    
def pack(h):
    s = h % 0x100
    t = h // 0x100
    return (s, t)
    
def location_from_pointer(pointer, constant):
    print "pointer:" + str(pointer)
    print "constant: " + hex(constant)
    value = hex(unpack(pointer[0], pointer[1]) + constant)
    print value
    return value