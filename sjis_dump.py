# Open a file in binary mode, see which two-byte sequences correspond to SJIS characters,
# and dump them in a file with their original position as well.

import subprocess
import codecs
import xlsxwriter

# Dict of files and dump blocks.
files = { 'OPENING.EXE': ((0x4dda, 0x5868),),
          'ST1.EXE': ((0xd873, 0x119a3), (0x11d42, 0x1240d),),
          'ST2.EXE': ((0xc23b, 0x1085e),),
          'ST3.EXE': ((0xb49d, 0xee70),),
          'ST4.EXE': ((0xe263, 0x1620d), (0x1659c, 0x168a8)),
          'ST5.EXE': ((0xcc01, 0x11465), (0x11977, 0x11b52), (0x11ef2, 0x121fd)),
          'ST5S1.EXE': ((0x24ee, 0x3af1),),
          'ST5S2.EXE': ((0x23f9, 0x3797),),
          'ST5S3.EXE': ((0x3db9, 0x4ed0),),
          'ST6.EXE': ((0xa51a, 0xcdf4),),
          'ENDING.EXE': ((0x3c4e, 0x4b1f),),
          'SINKA.DAT': ((0x0000, 0x874a),),
          'SEND.DAT': ((0x000, 0x8740),),
          '46.EXE': ((0x93e8, 0x946d), (0x94b9, 0x971b), (0x9cb8, 0xa07a))
}

for file in files:
    fo = codecs.open(file, "r", encoding='shift_jis', errors='ignore') 