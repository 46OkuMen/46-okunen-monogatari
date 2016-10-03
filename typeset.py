"""
	Typesetting tools for E.V.O.: The Theory of Evolution.
"""

from utils import SRC_ROM_PATH, DEST_ROM_PATH
from cheats import change_starting_map

from disk import Disk, EXEFile, DATFile, Pointer

FILES_TO_TYPESET = ['ST1.EXE', ]

if __name__ == '__main__':
    DiskA = Disk(SRC_ROM_PATH, DEST_ROM_PATH, FILES_TO_TYPESET)
    for gamefile in DiskA.gamefiles:
    	for text_offset, pointer in sorted(gamefile.pointers.iteritems()):
    		for p in pointer:
    			print hex(p.location)
    			print hex(p.text_location)
    			print hex(p.new_text_location)
    			print p.text() + "\n"
    			# i am making a large mistake somewhere
    			# This is giving me something 2 bytes too far into the string, and 2 bytes further than what pointer_peek.py gives me.
