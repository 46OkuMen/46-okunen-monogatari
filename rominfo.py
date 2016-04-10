files = ['OPENING.EXE', '46.EXE', 'ST1.EXE', 'ST2.EXE', 'ST3.EXE', 'ST4.EXE', 'ST5.EXE', 'ST5S1.EXE', 'ST5S2.EXE',
         'ST5S3.EXE', 'ST6.EXE', 'ENDING.EXE', 'SINKA.DAT', 'SEND.DAT']

file_blocks = {'OPENING.EXE': ((0x4dda, 0x5868),),
               '46.EXE': ((0x93e8, 0x9cd9), (0x9d6e, 0xa07a)),
               'ST1.EXE': ((0xd873, 0xd934),  # not variable; environment messages
                           (0xd984, 0xe6f9),
                           (0xe6f9, 0xec4c),  # not variable; battle msgs    # ec4c separation is necessary! (AWAKU0.GDT)
                           (0xec4c, 0xec9e),  # not variable; evolution msgs
                           (0xec9e, 0x10e39),  # variable; dialogue
                           (0x10e39, 0x10f96),  # not variable; environment messages
                           (0x10fca, 0x117c7),  # variable; creature names
                           (0x117c7, 0x117df),  # not variable; yes/no/cancel    # iffy ending
                           (0x11839, 0x11857),  # not variable; "evolved too far" message
                           (0x11893, 0x119ae),  # not variable; battle msgs      # iffy ending
                           (0x11d42, 0x1204e)),  # error block
               'ST2.EXE': ((0xc23b, 0xc27c),   # environment
                           (0xc2bc, 0xd757),   # evo files, dialogue
                           (0xd757, 0xd894),   # evolution, menu
                           (0xd894, 0xdd50),   # battle stuff
                           (0xde35, 0xf948),   # dialogue
                           (0xf980, 0xfaa2),   # environment (probably needs additional splits)
                           (0xfae4, 0xfe50),   # creature block
                           (0x10004, 0x101df), # battle stuff
                           (0x10570, 0x1087d)), # error block
               'ST3.EXE': ((0xb49d, 0xb548),
                           (0xb58a, 0xbccb), # split at AWAKU0.GDT
                           (0xbccb, 0xdb3a),
                           (0xdb7e, 0xe2d5),
                           (0xe617, 0xe7f3),
                           (0xeb82, 0xee8e)),
               'ST4.EXE': ((0xe262, 0xe29e),
                           (0xe2f4, 0x120a0),
                           (0x12114, 0x149e4),
                           (0x14a28, 0x15a1e),
                           (0x16031, 0x1620d),
                           (0x1659c, 0x168a8)),
               'ST5.EXE': ((0xcc02, 0xcc5e),
                           (0xccf2, 0xcd2e),
                           (0xcd74, 0xeabe),
                           (0xebc3, 0x107a3),
                           (0x107e6, 0x11466),
                           (0x11976, 0x11b53),
                           (0x11ef2, 0x121fe)),
               'ST5S1.EXE': ((0x24e8, 0x3af1),),
               'ST5S2.EXE': ((0x23f9, 0x3797),),
               'ST5S3.EXE': ((0x3db9, 0x4ed0),),
               'ST6.EXE': ((0xa4f1, 0xa55b), (0xa59c, 0xccd1), (0xcd14, 0xce25), (0xcede, 0xd0bb), (0xd44a, 0xd756)),
               'ENDING.EXE': ((0x3c4e, 0x4b1f),),
               'SINKA.DAT': ((0x0000, 0x69a4),),
               'SEND.DAT': ((0x000, 0x8740),)
}

# TODO: Now that the blocks are less finicky, I can probably combine a lot of these blocks rather than
# split them wherever there's a filename.

# What is my methodology for deciding when a block starts and ends?
# The end of a block has to be a place where spaces are okay. My mistake may have been in putting them after filenames.
# If you end right on top of a filename, the extra spaces will push the filename into the correct position... maybe?

spare_block = {#'OPENING.EXE': None,
               '46.EXE': (0x9cb8, 0xa07a),
               'ST1.EXE': (0x11d42, 0x1204e),
               'ST2.EXE': (0x10570, 0x1087b),
               'ST3.EXE': (0xeb82, 0xee8e),
               'ST4.EXE': (0x1659c, 0x168a8),
               'ST5.EXE': (0x11ef2, 0x121fe),
               #'ENDING.EXE': None,
               #'SINKA.DAT': None,
               #'SEND.DAT': None
               }
 # Usually the last block.
               # TODO: In progress. Also figure out what to do with the Nones.

creature_block = {'OPENING.EXE': (0, 0),
                  'ST1.EXE': (0x10fca, 0x11595),
                  'ST2.EXE': (0xfae4, 0xfe50),
                  'ST3.EXE': (0xdb7e, 0xe2d5),
                  'ST4.EXE': (0x14a28, 0x15a1e),
                  'ST5.EXE': (0x107e6, 0x11466),
                  'ENDING.EXE': (0, 0),
                  'SINKA.DAT': (0, 0),
                  'SEND.DAT': (0, 0)}
               # TODO: Even more in progress than the last one.
# Usually the third-to-last block.

# Starting position, in bytes, of each file within the Disk 1 rom.
file_location = {'OPENING.EXE': 0x58800,
              'ST1.EXE': 0x5e800,
              'ST2.EXE': 0x70c00,
              'ST3.EXE': 0x81800,
              'ST4.EXE': 0x90800,
              'ST5.EXE': 0xa7400,
              'ST5S1.EXE': 0xb9800,
              'ST5S2.EXE': 0xbd400,
              'ST5S3.EXE': 0xc1000,
              'ST6.EXE': 0xc6400,
              'ENDING.EXE': 0x4e000,
              'SINKA.DAT': 0x3d000,
              'SEND.DAT': 0x34800,}

# Length in bytes.
file_length = {'OPENING.EXE': 0x5e4b,
               'ST1.EXE': 0x121a7,
               'ST2.EXE': 0x109d5,
               'ST3.EXE':  0xefe7,
               'ST4.EXE': 0x16a01,
               'ST5.EXE': 0x12357,
               'ST5S1.EXE': 0x3bbb,
               'ST5S2.EXE': 0x3861,
               'ST5S3.EXE': 0x50ef,
               'ST6.EXE': 0xd8af,
               'ENDING.EXE': 0x4f55,
               'SINKA.DAT': 0x69a4}

pointer_separators = {
        'OPENING.EXE': ("68", "04"), # Sep: 68-04
        'ST1.EXE': ("5e", "0d"), # 5e-0d
        'ST2.EXE': ("f7", "0b"), # fc-0b
        'ST3.EXE': ("20", "0b"),
        'ST4.EXE': ("f4", "0d"),
        'ST5.EXE': ("96", "0c"),
        'ST6.EXE': ("26", "0a"),
        'ST5S1.EXE': ("24", "02"),
        'ST5S2.EXE': ('00', '00'), # Wrong; no pointer tables
        'ST5S3.EXE': ("ae", "03"),
        'ENDING.EXE': ("5a", "03"),
        '46.EXE': ('0a', '0c')
}

pointer_constants = {
        'OPENING.EXE': 0x4a80,
        'ST1.EXE': 0xd7e0,
        'ST2.EXE': 0xc170,
        'ST3.EXE': 0xb400,
        'ST4.EXE': 0xe140,
        'ST5.EXE': 0xcb60,
        'ST6.EXE': 0xa460,
        'ST5S1.EXE': 0x2440,
        'ST5S2.EXE': 0x2360,
        'ST5S3.EXE': 0x3ce0,
        'ENDING.EXE': 0x39a0,
        '46.EXE': 0x92c0,
}