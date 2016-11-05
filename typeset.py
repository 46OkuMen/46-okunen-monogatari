"""
    Typesetting tools for E.V.O.: The Theory of Evolution.
"""

from utils import SRC_ROM_PATH, DEST_ROM_PATH, TYPESET_ROM_PATH, onscreen_length
from rominfo import DAT_MAX_LENGTH

from disk import Disk, EXEFile, DATFile, Pointer

FILES_TO_TYPESET = ['ST1.EXE', 'ST2.EXE', 'ST3.EXE', 'ST4.EXE', 'ST5.EXE', 'ST5S1.EXE', 'ST5S2.EXE', 'ST6.EXE']

PATCHED_ROM_PATH = DEST_ROM_PATH
TYPESET_ROM_PATH = TYPESET_ROM_PATH

if __name__ == '__main__':
    DiskA = Disk(DEST_ROM_PATH, TYPESET_ROM_PATH, FILES_TO_TYPESET)
    for gamefile in DiskA.gamefiles:
        #if gamefile == 'SEND.DAT':
         #   for t in gamefile.blocks[0].translations:
         #       t.simple_typeset()
         #       if t.english.count('[SENLN]') != 
        gamefile.refresh_pointers()
        for b in gamefile.blocks:
            if b in (gamefile.spare_block, gamefile.other_spare_block, gamefile.creature_block):
                continue
            for p_int in b.get_pointers():
                first_pointer = gamefile.pointers[p_int][0]
                if len(first_pointer.translations) > 0:
                    if first_pointer.translations[0].english == 'Cancel':
                        continue
                    try:
                        original_text = str(first_pointer.text())
                        first_pointer.typeset()
                    except TypeError:
                        pass
        gamefile.incorporate()
        gamefile.write()
    DiskA.write()