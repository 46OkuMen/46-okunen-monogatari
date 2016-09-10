""" Reinsertion script for 46 Okunen Monogatari: The Shinka Ron."""

from utils import SRC_ROM_PATH, DEST_ROM_PATH
from cheats import change_starting_map

from disk import Disk, EXEFile, DATFile

#FILES_TO_TRANSLATE = ['ST1.EXE', 'ST2.EXE']

FILES_TO_TRANSLATE = ['ST1.EXE', 'ST2.EXE', 'ST3.EXE', 'ST4.EXE', 'ST5.EXE', 'ST5S1.EXE',
                      'ST5S2.EXE', 'ST5S3.EXE', 'ST6.EXE', 'OPENING.EXE', 'SINKA.DAT',
                      'ENDING.EXE', 'SEND.DAT']

# for testing the oh-so-problematic Ch5:
#FILES_TO_TRANSLATE = ['ST5.EXE',]# 'ST5S1.EXE', 'ST5S2.EXE', 'ST5S3.EXE']


if __name__ == '__main__':
    DiskA = Disk(SRC_ROM_PATH, DEST_ROM_PATH, FILES_TO_TRANSLATE)
    DiskA.translate()

    #change_starting_map('ST1.EXE', 100)
    #change_starting_map('ST5.EXE', 600)