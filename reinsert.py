from __future__ import division

# Reinsertion script for 46 Okunen Monogatari: The Shinka Ron.
# TODO: See what's going on with the JP closing quotes. Are they not included? in the xls? Is jp_len*2 not long enough - should it be +2?

dump_xls = "shinkaron_just_one_change.xlsx"
pointer_xls = "shinkaron_pointer_dump.xlsx"

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
for file in sheets:
    # TODO: Remvoe this when more text is translated in other files.
    if file != "ST1.EXE":
        continue

    # First, index all the translations by the offset of the japanese text.
    translations = OrderedDict() # translations[offset] = (japanese, english)   TODO: Does it need to be ordered?

    ws = wb.get_sheet_by_name(file)
    # These two variables count the replacements to track reinsertion progress.
    total_rows = 0
    total_replacements = 0

    for row in ws.rows[1:]:  # Skip the first row, it's just labels
        total_rows += 1

        offset = int(row[0].value, 16)
        japanese = row[2].value
        english = row[4].value

        if not english:
            # No translation is available; skip this row. (It still has a ptr, so its diff will be calculated later)
            continue
        translations[offset] = (japanese, english)

    #for _,e in translations.iteritems():
    #    print e

    # Next, load all the pointers from the excel sheet.
    pointers = {}              # text_offset: pointer_offset
    pointer_diffs = {}         # text_offset: diff

    last_pointer_diff = 0
    last_text_offset = 0

    pointer_wb = load_workbook(pointer_xls)
    pointer_sheet = pointer_wb.get_sheet_by_name("Sheet1") # For now, they are all in the same sheet... kinda ugly.

    for row in pointer_sheet.rows:
        if row[0].value == file:                          # Access ptrs for the current file only.
            text_offset = int(row[1].value, 16)
            pointer_offset = int(row[2].value, 16)
            pointers[text_offset] = pointer_offset

            pointer_diffs[text_offset] = last_pointer_diff

            # When the text_offset is 60871 (0xedc7), where the text is changed, it is between two ptrs.
            # ...
            # Rather than look for something with the exact pointer, look for any translated text with a value between last_pointer_offset (excl) and text_offset (incl)
            # Calculate the diff, then add it to last_pointer_diff.
            lo = last_text_offset
            hi = text_offset
            for n in range((lo+1), (hi+1)):
                try:
                    jp, eng = translations[n]
                    len_diff = len(eng) - (len(jp)*2)                 # Shift_JIS has two-byte characters
                    #print len(eng), len(jp)*2
                    pointer_diffs[text_offset] = last_pointer_diff    # Tricky part: an adjustment takes effect first in the next pointer!!!
                    last_pointer_diff += len_diff                     # So let it get assigned the next time. (Also it's cumulative.)
                    print "Here's the line! ", len_diff, last_pointer_diff
                except KeyError:
                    pass

            last_text_offset = text_offset

    print pointer_diffs


"""
    # Each file is on a separate sheet.
    src_file_path = os.path.join(src_path, file)
    dest_file_path = os.path.join(dest_path, file)

    copyfile(src_file_path, dest_file_path)

    in_file = open(dest_file_path, 'rb+')
    for offset in translations:
        total_replacements += 1
        in_file.seek(offset, 0)
        in_file.write(translations[offset][1])

    pointer_constant = pointer_constants[file]

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

"""