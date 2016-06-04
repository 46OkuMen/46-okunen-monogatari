"""Hopelessly late unit tests for the reinserter."""

from utils import DUMP_XLS
from openpyxl import load_workbook


class TestDump:

    def test_increasing_offsets(self):
        wb = load_workbook(DUMP_XLS)
        sheets = wb.get_sheet_names()
        sheets.remove('ORIGINAL')
        sheets.remove('MISC TITLES')
        sheets.remove('SINKA.DAT')
        sheets.remove('SEND.DAT')
        for sheet in sheets:
            ws = wb.get_sheet_by_name(sheet)
            new_offset = 0
            for index, row in enumerate(ws.rows[1:]):  # Skip the first row, it's just labels
                assert int(row[0].value, 16) > new_offset, "In sheet %s, fix offset at row %s; %s < %s" % (sheet, index+2, hex(int(row[0].value, 16)), hex(new_offset))
                new_offset = int(row[0].value, 16)

    def test_all_string_lengths(self):
        wb = load_workbook(DUMP_XLS)
        sheets = wb.get_sheet_names()
        sheets.remove('ORIGINAL')
        sheets.remove('MISC TITLES')
        for sheet in sheets:
            ws = wb.get_sheet_by_name(sheet)
            new_offset = 0
            for index, row in enumerate(ws.rows[1:]):
                if row[4].value:
                    assert len(row[4].value) <= 76, "In sheet %s, shorten string at row %s" % (sheet, index+2)

# make sure a blank translation sheet doesn't return overflow errors

# make sure offsets are strictly increasing

# make sure no english string is longer than X
