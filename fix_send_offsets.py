"""SJIS-Dump incorrectly reports the offset of strings in files where the first text is ASCII.
This script finds the true offsets of SEND.DAT strings and puts them in a new excel spreadsheet 
to be copied into the main one."""

import os

SCRIPT_DIR = os.path.dirname(__file__)
SRC_PATH = os.path.join(SCRIPT_DIR, 'original_roms')
DEST_PATH = os.path.join(SCRIPT_DIR, 'patched_roms')

SRC_ROM_PATH = os.path.join(SRC_PATH, "46 Okunen Monogatari - The Sinkaron (J) A user.FDI")
DEST_ROM_PATH = os.path.join(DEST_PATH, "46 Okunen Monogatari - The Sinkaron (J) A user.FDI")

DUMP_XLS = "shinkaron_dump_test.xlsx"

from openpyxl import Workbook
from disk import Disk, DumpExcel
from utils import file_to_hex_string
from rominfo import file_blocks

DiskA = Disk(SRC_ROM_PATH, DEST_ROM_PATH, ['SEND.DAT',])

dump_path = os.path.join(SCRIPT_DIR, DUMP_XLS)
dump = DumpExcel(dump_path)
sendfile = file_to_hex_string(os.path.join(SRC_PATH, "SEND.DAT"))
send_translations = dump.get_translations(DiskA.gamefiles[0].blocks[0])

new_wb = Workbook()
new_filename = 'fixed_send_offsets.xlsx'
ws1 = new_wb.active

for t in send_translations:
	bytestring = t.jp_bytestring.replace('0d0a', '')
	correct_offset = sendfile.index(bytestring)//2
	if '/*' in t.japanese:
		ws1.append(['0x' + format(correct_offset-4, '04x'), 'some number'])
	ws1.append(['0x' + format(correct_offset, '04x'), t.english])

new_wb.save(new_filename)