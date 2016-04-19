from os import path
from openpyxl import load_workbook

script_dir = path.dirname(__file__)

dump_xls = "shinkaron_dump_test.xlsx"

wb = load_workbook(dump_xls)
sheets = wb.get_sheet_names()

sheets.remove('ORIGINAL')
sheets.remove('SINKA.DAT')
sheets.remove('SEND.DAT')
sheets.remove('MISC TITLES')

for sheet in sheets:
    ws = wb.get_sheet_by_name(sheet)
    new_offset = 0
    for index, row in enumerate(ws.rows[1:]):  # Skip the first row, it's just labels
        if int(row[0].value, 16) < new_offset:
            print "In file", sheet, "fix the offset at row", index+2, "offset", hex(int(row[0].value, 16)), "less than", hex(new_offset)
        new_offset = int(row[0].value, 16)