# Reinsertion script for 46 Okunen Monogatari: The Shinka Ron.
# Plan right now: Take the strings identified as part of the dump, replace them with "AAA" of equal length.

dump_xls = "shinkaron_dump_split.xlsx"

import os
import subprocess
import codecs
import xlsxwriter
import openpyxl
import re

from utils import file_blocks
#from utils import pointer_constants, pointer_separators
#from utils import pack, unpack, location_from_pointer

from openpyxl import load_workbook
from shutil import copyfile

script_dir = os.path.dirname(__file__)
src_path = os.path.join(script_dir, 'original_roms')
dest_path = os.path.join(script_dir, 'patched_roms')

wb = load_workbook(dump_xls)
sheets = wb.get_sheet_names()
#print sheets
sheets.remove(u'ORIGINAL')
sheets.remove(u'MISC TITLES')
for sheet in sheets:
    # Just ST1.EXE for now:
    if sheet != "ST1.EXE":
        continue
    ws = wb.get_sheet_by_name(sheet)
    text = {} # offset: (jp, eng)
    for row in ws.rows[1:]:  # Skip the first row, it's just labels
        offset = int(row[0].value, 16)
        if row[2].value:
            jp_len = len(row[2].value)
            english = row[4].value
            if not english:
                continue
            else:
                en_len = len(english)
                len_diff = (jp_len*2) - en_len
                if len_diff < 0: # Negative result: english too long (requires pointer adjustment)
                    #print "English too long at" + offset
                    print english
                    print "JP: " + str(jp_len)
                    print "EN: " + str(en_len)
                    #print english
                    continue
                elif len_diff > 0: # Positive result: english requires padding (later, adjust ptrs)
                    english += " "*len_diff
                  
            text[offset] = (row[2], english)
    #print len(text)
    
    # Each file is on a separate sheet.
    src_file_path = os.path.join(src_path, sheet)
    dest_file_path = os.path.join(dest_path, sheet)

    copyfile(src_file_path, dest_file_path)

    in_file = open(dest_file_path, 'rb+')
    for offset in text:
        in_file.seek(offset, 0)
        in_file.write(text[offset][1])