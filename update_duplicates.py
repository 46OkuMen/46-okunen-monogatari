from openpyxl import load_workbook
from utils import files
import os

script_dir = os.path.dirname(__file__)

dump_xls = "shinkaron_dump_test.xlsx"

wb = load_workbook(dump_xls)
sheets = wb.get_sheet_names()
ws = wb.get_sheet_by_name('ST4.EXE')

translations = {}
for sheet in sheets:
    ws = wb.get_sheet_by_name(sheet)
    for row in ws.rows[1:]:  # Skip the first row, it's just labels
        japanese = row[2].value
        english = row[4].value

        if not english:
            continue

        translations[japanese] = english


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