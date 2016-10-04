"""Tons of constants related to the positions of things within files."""

# A list of all files with text edits during the dump/reinsert process.
files = ['OPENING.EXE', '46.EXE', 'ST1.EXE', 'ST2.EXE', 'ST3.EXE', 'ST4.EXE', 'ST5.EXE', 'ST5S1.EXE', 'ST5S2.EXE',
         'ST5S3.EXE', 'ST6.EXE', 'ENDING.EXE', 'SINKA.DAT', 'SEND.DAT']

CHAPTER_FIVE_FILES = ['ST5.EXE', 'ST5S1.EXE', 'ST5S2.EXE', "ST5S3.EXE"]

CREATURE_MAX_LENGTH = 21
DIALOGUE_MAX_LENGTH = 44
FULLSCREEN_MAX_LENGTH = 76
DAT_MAX_LENGTH = 68   # TODO: Check on SEND.DAT, see if they're indented.

# How the files themselves get broken up for reinsertion.
file_blocks = {'OPENING.EXE': ((0x4ddb, 0x555f), # cut scene
                               (0x55e9, 0x5639), # spare block
                               (0x5657, 0x586a)), # cut scenes
               #'46.EXE': ((0x93e8, 0x9cd9), (0x9d6e, 0xa07a)),
               'ST1.EXE': ((0xd873, 0xd8b3),  # fresh water messages
                           (0xd8f3, 0xd934),  # Gaia's Heart
                           (0xd984, 0xe6f9),
                           (0xe6f9, 0xec4c),  # not variable; battle msgs
                           (0xec4c, 0xec9e),  # not variable; evolution msgs
                           (0xec9e, 0xed90),
                           (0xedc7, 0x10e39),  # variable; dialogue
                           (0x10e39, 0x10f86),  # not variable; environment messages
                           (0x10fca, 0x117c7),  # variable; creature names
                           (0x117c7, 0x117e0),  # not variable; yes/no/cancel    # iffy ending
                           (0x11839, 0x11857),  # not variable; "evolved too far" message
                           (0x11893, 0x119a4),  # not variable; battle msgs      # iffy ending
                           (0x11d42, 0x1204e)),  # error block
               'ST2.EXE': ((0xc23b, 0xc27c),   # environment
                           (0xc2bc, 0xd5ae),   # evo files, dialogue
                           (0xd5b9, 0xd757),   # dialogue
                           (0xd757, 0xd894),   # evolution, menu
                           (0xd8c6, 0xdd50),   # battle stuff
                           (0xde35, 0xe5fd),   # dialogue/AV (split at AV206/stone image)
                           (0xe5fd, 0xf165),   # dialogue/AV screens
                           (0xf171, 0xf8c9),   # dialogue
                           (0xf8f5, 0xf948),   # just one environment msg
                           (0xf980, 0xfaa2),   # enviro
                           (0xfae4, 0xfe50),   # creature block
                           (0x10004, 0x10095), # Y/N/C, "evolved too far"
                           (0x100d1, 0x101e1), # battle stuff
                           (0x10570, 0x1087d)), # error block
               'ST3.EXE': ((0xb49d, 0xb548),   # environment
                           (0xb58a, 0xbccb),    # evo files, dialogue
                           (0xbccb, 0xbe16),
                           (0xbe22, 0xc01d),
                           (0xc046, 0xcaaf),
                           (0xcaaf, 0xcfe6),
                           (0xcfff, 0xd7ef),
                           (0xd7ef, 0xd963),
                           (0xd963, 0xda0d),
                           (0xda0d, 0xdb3b),  # enviro
                           (0xdb7e, 0xe2d5),  # creature block
                           (0xe617, 0xe6a7),    # Y/N/C, "evolved too far"
                           (0xe6e3, 0xe7f3),
                           (0xeb82, 0xee8e)),
               'ST4.EXE': ((0xe263, 0xe2a3), # enviro
                           (0xe2f4, 0xe8ab),
                           (0xe8ab, 0xea4b), # evolution, menus
                           (0xea4b, 0x102cb),
                           (0x102cb, 0x120a1), # dialogue... ends at crazy control codes/table
                           (0x12115, 0x12925),
                           (0x12925, 0x134d9), # dialogue
                           (0x134f6, 0x13c25), # dialogue
                           (0x13e97, 0x13fed), # dialogue
                           (0x14026, 0x1485f), # dialogue
                           (0x148c1, 0x149e5), # enviro
                           (0x14a28, 0x15a1e), # creature block
                           (0x16031, 0x160c1), # Y/N/C, evolved too far
                           (0x160fd, 0x1620d), # battle msgs
                           (0x1659c, 0x168a8)), # error block
               'ST5.EXE': ((0xcc02, 0xcc63), # dialogue?
                           (0xccf3, 0xcd34), # enviro
                           (0xcd74, 0xcedc),
                           (0xcf16, 0xea57),
                           (0xea57, 0xeac4), # dialogue
                           (0xebbe, 0x1061e), # dialogue
                           (0x10682, 0x107a4), # enviro
                           (0x107e6, 0x11467), # creature block
                           (0x11977, 0x11a07), # y/n/c, evolved too far
                           (0x11a43, 0x11b54), # battle msgs
                           (0x11ef2, 0x121fe)), # error block
               'ST5S1.EXE': ((0x24e8, 0x39bb),
                             (0x39cc, 0x3af2),),
               'ST5S2.EXE': ((0x23f9, 0x3798),),
               'ST5S3.EXE': ((0x3db9, 0x3dc6),
                             (0x3e30, 0x3f65),
                             (0x3f97, 0x4daa),
                             (0x4dba, 0x4ee0),),
               'ST6.EXE': ((0xa51b, 0xa55a), # enviro
                           (0xa59c, 0xa5e9), # evo files
                           (0xa5e9, 0xaf59), # stats/evolution
                           (0xaf59, 0xb066), # menu
                           (0xb072, 0xb457), # dialogue
                           (0xb489, 0xb8d2), # dialogue
                           (0xb8ea, 0xccaf), # dialogue 
                           (0xcd14, 0xce25), # creature block
                           (0xcedf, 0xcf6f), # y/n/c, "evolved too far"
                           (0xcfab, 0xd0bb), # enviro, battle text
                           (0xd44a, 0xd756)), # error block
               'ENDING.EXE': ((0x3c4e, 0x4b20),),
               'SINKA.DAT': ((0x0000, 0x69a4),),
               'SEND.DAT': ((0x000, 0x8740),)}


# What is my methodology for deciding when a block starts and ends?
# The end of a block has to be a place where spaces are okay. My mistake may have been in putting them after filenames.
# If you end right on top of a filename, the extra spaces will push the filename into the correct position... maybe?
# Definitely don't end on the last character of a string!! End it one or two after.
# Need to end blocks one after an "<END>" byte. This helps one overflow not spill into the next.

# Some files have an error block, which we can replace with text overflowing from other blocks.
SPARE_BLOCK = {'OPENING.EXE': (0x55e9, 0x5639),
               '46.EXE': (0x9cb8, 0xa07a),
               'ST1.EXE': (0x11d42, 0x1204e),
               'ST2.EXE': (0x10570, 0x1087d),
               'ST3.EXE': (0xeb82, 0xee8e),
               'ST4.EXE': (0x1659c, 0x168a8),
               'ST5.EXE': (0x11ef2, 0x121fe),
               'ST6.EXE': (0xd44a, 0xd756),}
 # Usually the last block. (But not in OPENNING.EXE).

CREATURE_BLOCK = {'ST1.EXE': (0x10fca, 0x11595),
                  'ST2.EXE': (0xfae4, 0xfe50),
                  'ST3.EXE': (0xdb7e, 0xe2d5),
                  'ST4.EXE': (0x14a28, 0x15a1e),
                  'ST5.EXE': (0x107e6, 0x11466),
                  'ST6.EXE': (0xcd14, 0xce25)}
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
file_length = {'OPENING.EXE': 0x5e4c,
               'ST1.EXE': 0x121a8,
               'ST2.EXE': 0x109d6,
               'ST3.EXE':  0xefe8,
               'ST4.EXE': 0x16a02,
               'ST5.EXE': 0x12358,
               'ST5S1.EXE': 0x3bbc,
               'ST5S2.EXE': 0x3862,
               'ST5S3.EXE': 0x50f0,
               'ST6.EXE': 0xd8b0,
               'ENDING.EXE': 0x4f56,
               'SINKA.DAT': 0x69a5,
               'SEND.DAT': 0x874b}

# Pointer tables have two bytes, determined by the file, which separate their values.
POINTER_SEPARATORS = {
    'OPENING.EXE': ("68", "04"),
    'ST1.EXE': ("5e", "0d"),
    'ST2.EXE': ("f7", "0b"),
    'ST3.EXE': ("20", "0b"),
    'ST4.EXE': ("f4", "0d"),
    'ST5.EXE': ("96", "0c"),
    'ST6.EXE': ("26", "0a"),
    'ST5S1.EXE': ("24", "02"),
    'ST5S2.EXE': ('00', '00'), # Not really; this file has no pointer tables
    'ST5S3.EXE': ("ae", "03"),
    'ENDING.EXE': ("5a", "03"),
    '46.EXE': ('0a', '0c')
}

# Add this constant to the little-endian pointer value to find its destination.
POINTER_CONSTANT = {
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

# For cheating!
STARTING_MAP_NUMBER_LOCATION = {
    'ST1.EXE': 0xedaa,
    'ST5.EXE': 0xcf04,
}
