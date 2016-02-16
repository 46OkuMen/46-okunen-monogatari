from __future__ import division

# Reinsertion script for 46 Okunen Monogatari: The Shinka Ron.

# TODO: See what's going on with the JP closing quotes. Are they not included? in the xls? Is jp_len*2 not long enough - should it be +2?

dump_xls = "shinkaron_dump_split.xlsx"

import os
import subprocess
import codecs
import xlsxwriter
import openpyxl
import re

from utils import file_blocks
from utils import pointer_constants, pointer_separators
from utils import pack, unpack, location_from_pointer, pointer_value_from_location

from openpyxl import load_workbook
from shutil import copyfile

from collections import OrderedDict

script_dir = os.path.dirname(__file__)
src_path = os.path.join(script_dir, 'original_roms')
dest_path = os.path.join(script_dir, 'patched_roms')

wb = load_workbook(dump_xls)
sheets = wb.get_sheet_names()
#print sheets
sheets.remove(u'ORIGINAL')
sheets.remove(u'MISC TITLES')
for sheet in sheets:
    # TODO: Remvoe this when more text is translated in other files.
    if sheet != "ST1.EXE" and sheet != "46.EXE":
        continue

    translations = OrderedDict() # translations[offset] = (jp, eng)
    ptr_diffs = OrderedDict() # ptr_diffs[ptr_offset] = n

    prev_len_diff = 0 # Ptr diffs affect the next pointer, not the current one

    ws = wb.get_sheet_by_name(sheet)
    total_rows = 0
    total_replacements = 0

    for row in ws.rows[1:]:  # Skip the first row, it's just labels
        total_rows += 1
        offset = int(row[0].value, 16)
        if row[2].value:
            jp_len = len(row[2].value)
            english = row[4].value
            if not english:
                # If no translation, leave the JP text untouched & skip to next row.
                # ...but I still want to adjust the pointer even if there's no translated text here.
                ptr_diffs[offset] = prev_len_diff
                continue
            en_len = len(english)
            len_diff = en_len - (jp_len*2)
            if len_diff > 0: # Positive result: english too long (requires pointer adjustment)
                #print "English too long at" + offset
                #print english
                #print "JP: " + str(jp_len)
                #print "EN: " + str(en_len)
                #continue
                pass
            elif len_diff < 0: # Negative result: english too short, requires padding (later, adjust ptrs)
                english += " "*len_diff
                  
            translations[offset] = (row[2], english)
            pointer_offset = row[1].value # it's a string like '0x4fc9'
            adjustment = prev_len_diff

            ptr_diffs[offset] = adjustment

            prev_len_diff += len_diff # The effect is cumulative

    # Each file is on a separate sheet.
    src_file_path = os.path.join(src_path, sheet)
    dest_file_path = os.path.join(dest_path, sheet)

    copyfile(src_file_path, dest_file_path)

    in_file = open(dest_file_path, 'rb+')
    for offset in translations:
        total_replacements += 1
        in_file.seek(offset, 0)
        in_file.write(translations[offset][1])

    pointer_constant = pointer_constants[sheet]

    for ptr in ptr_diffs:
        original_pointer = ptr - pointer_constant
        print original_pointer
        new_pointer = original_pointer + ptr_diffs[ptr]
        new_pointer_bytes = pack(new_pointer)
        print new_pointer, new_pointer_bytes
        # TODO: Actually write these values.
        # BUT FIRST: Dump the pointer-pointers so they can be adjusted as well; otherwise it'll crash.

    translation_percent = (total_replacements / total_rows) * 100
    print sheet + " " + str(translation_percent) + "% complete"
    print ptr_diffs