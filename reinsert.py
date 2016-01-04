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
from utils import specific_pointer_regex
from utils import pointer_constants, pointer_separators
from utils import pack, unpack, location_from_pointer

from openpyxl import load_workbook

wb = load_workbook(dump_xls)
sheets = wb.get_sheet_names()
print sheets
sheets.remove(u'ORIGINAL')
sheets.remove(u'MISC TITLES')
for sheet in sheets:
    ws = wb.get_sheet_by_name(sheet)
    text = {} # offset: (jp, eng)
    for row in ws.rows[1:]:  # Skip the first row, it's just labels
        offset = int(row[0].value, 16)
        if row[2].value:
            jp_len = len(row[2].value)
            # Check if the English is too long (longer than twice the jp_len). If so, replace it with AAAAs.
            english = row[4].value
            if not english:
                english = 'A'*jp_len*2
            else:
                en_len = len(english)
                if en_len > (jp_len*2):
                    #print "English too long at" + offset
                    #print english
                    #print "JP: " + str(jp_len)
                    #print "EN: " + str(en_len)
                    english = 'A'*jp_len*2
                    #print english
                  
            text[offset] = (row[2], row[4])
            # NEXT: Make sure this is right. Can't print it though.
            # TODO: Then open the file, go to the offsets, write the English.
    print len(text)
    
    in_file = open(sheet, 'rb+')
    for offset in text:
        in_file.seek(offset, 0)
        in_file.write(english)
    print in_file.read()
    wait = raw_input("waiting")