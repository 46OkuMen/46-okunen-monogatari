"""Finds the duplicate entries in the dump excel sheet, taking one sheet as the base."""

import sys
from os import path
from openpyxl import load_workbook


script_dir = path.abspath(__file__)
xls_dir = path.dirname(script_dir)

dump_xls = "shinkaron_dump_test.xlsx"

xls_path = path.join(xls_dir, dump_xls)

wb = load_workbook(dump_xls)
sheets = wb.get_sheet_names()
ws = wb.get_sheet_by_name(str(sys.argv[1]))

translations = {}
for sheet in sheets:
    ws = wb.get_sheet_by_name(sheet)
    for row in ws.rows[1:]:  # Skip the first row, it's just labels
        japanese = row[2].value
        english = row[4].value

        if not english or not japanese:
            continue

        translations[japanese] = english

        #sjis = japanese.encode('utf-8')
        #print english
        #print repr(japanese)
        # '\xef\xbc\xa1'
        # \uefbca1

        #for letter in range(1, 7):
        #    print sjis + u'\xef' + u'\xbc' + u'\xa%s' % letter
            #print sjis + '\\xef\\xbc\\xa' + str(letter)


        #print str(japanese)
        for letter in ['\uff21', '\uff22', '\uff23', '\uff24', '\uff25', '\uff26']:
            jp_suffix = (japanese + letter.decode('utf-8'))
            translations[jp_suffix] = english + " X"

        #print repr(japanese), english

for sheet in sheets:
    worksheet = wb.get_sheet_by_name(sheet)
    for row in worksheet.rows[1:]:
        japanese = row[2].value
        try:
            english = translations[japanese]
            row[4].value = english
            #print english, "found again in sheet", sheet
        except KeyError:
            continue

wb.save('shinkaron_dump_test_duplicates.xlsx')