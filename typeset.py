"""
    Typesetting tools for E.V.O.: The Theory of Evolution.
"""

from utils import SRC_ROM_PATH, DEST_ROM_PATH, TYPESET_ROM_PATH, onscreen_length
from rominfo import DAT_MAX_LENGTH

from disk import Disk, EXEFile, DATFile, Pointer

FILES_TO_TYPESET = ['ST1.EXE', 'ST5S2.EXE']

PATCHED_ROM_PATH = DEST_ROM_PATH
TYPESET_ROM_PATH = TYPESET_ROM_PATH

if __name__ == '__main__':
    DiskA = Disk(DEST_ROM_PATH, TYPESET_ROM_PATH, FILES_TO_TYPESET)
    for gamefile in DiskA.gamefiles:
        gamefile.refresh_pointers()
        for b in gamefile.blocks:
            print "NEW BLOCK"
            for p_int in b.get_pointers():
                first_pointer = gamefile.pointers[p_int][0]
                if len(first_pointer.translations) > 0:
                    try:
                        original_text = str(first_pointer.text())
                        first_pointer.typeset()
                        #if original_text != first_pointer.text():
                        #    print original_text
                        #    print first_pointer.text()
                    except TypeError:
                        pass
        gamefile.incorporate()
    DiskA.write()

"""
        if gamefile.filename.endswith('DAT'):
            for t in gamefile.blocks[0].translations:
                t.english = t.simple_typeset()
                print t.english

        else:
            spare_start, spare_stop = gamefile.spare_block.start, gamefile.spare_block.stop
            print hex(spare_start), hex(spare_stop)
            for _, pointer in sorted(gamefile.pointers.iteritems()):
                for p in pointer:
                    # skip error messages
                    if spare_start < p.text_location < spare_stop:
                        continue
                    print hex(p.new_text_location)
                    original_text = p.text()
                    textlines = original_text.splitlines()
                    print original_text
                    for i, line in enumerate(textlines):
                        if onscreen_length(line) > 44:
                            if i == len(textlines) - 1:
                                joinedlines = line
                            else:
                                joinedlines = line + "\n" + textlines[i+1]
                            words = joinedlines.split(' ')
                            firstline = ''
                            while onscreen_length(firstline + " ") <= 44:
                                if onscreen_length(firstline + " " + words[0]) <= 44:
                                    # Only add a space if it's not empty to begin with.
                                    if len(firstline) > 0:
                                        firstline += " "
                                    firstline += words.pop(0)
                                    print firstline
                                else:
                                    break
                            secondline = ' '.join(words)
                            if i == len(textlines) - 1:
                                textlines.append('')
                            
                            textlines[i], textlines[i+1] = firstline, secondline
                    new_text = '\n'.join(textlines)
                    print new_text
                    p.print_dialogue_box()
                    # So one problem with the text that's showing up is that it's probably the old error message pointers.
                    # I can filter those out with a list comp, I think.

                    # I need to edit pointers as well, since I might add more line breaks. Tricky!
"""