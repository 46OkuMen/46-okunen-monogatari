### Crashes
* Ch4 freeze upon loading a Ch3 save.
    * Happens upon loading a Ch3 save, loading a Ch1 save, and entering Ch5.
    * Definitely something in ST4.
        * Delete strings 400-700: broken
        * Delete strings 100-400: works
        * Delete strings 200-400: works
        * Delete strings 200-300: works
        * Delete strings 200-250: broken
        * Delete strings 250-275: the length is too long to do that
        * Delete string 265: works
            * 265 is responsible. It's really long, but otherwise pretty ordinary.
            * Broke up the block after that string. Now the Ch3 save works.

* Ch1 freeze upon loading a Ch4 save.
    * Had to do with the cladoselache history lesson... broke up the block after that string. Fixed now.

* Ch3 and Ch4: Freeze after loading the first character of "Insert disk #X", "Save EVO" or "Load EVO" on saving/loading/changing disks.
    * Works ok with Text Speed 0, but nothing that displays characters one at a time.
    * Check alllllll the pointers to Save Game, Load Game, etc.
    * It doesn't have to do with Disk Error being blanked out.
    * Also occurs with a blank ST3 sheet. No translations have happened, but changes like the space-reclaiming functions have already 
    * Try it without the altered 46.EXE. It isn't anything with ST3...
    * Fixed by breaking up the text blocks a bit better.
    * Seems to persist in my save states, but not from a fresh load of the file. Odd...

### Text Oddities
* Some odd text timing in the Ch6 hopeless Devil fight.
    * Too-long pause after "bolts of lightning", no pause at all when it tells you how much damage you've taken
        * Check out the JP version
            * Looks like the JP version tries not to display the damage numbers at all! 
        * Insert [PAUSE] control codes as needed.

* The end of the encyclopedia entry for Protungulatum doesn't wait at the end in the JP version. See how to fix it in ours.

* Find other numbers that are likely victims of the number corruption bug.

### Typesetting
* Manual text stuff.
    * Chapter 1: done
    * Chapter 2: good enough.
    * Chapter 3: did two passes. Basically done.
    * Chapter 4: did two passes. Mostly done, but crashes at the end
    * Chapter 5:
    * Chapter 6: done

* Center the credits text

* Broken text in game over stories:
    * Green Dragon
    * ?
    * Currently being kept track of on a google sheet.

### images
* Reinsert the revised images.
    * Title: still stupidly hard
        * "Index was outside the bounds of the array" when run through the decoder again. Generally fails after a few blocks of stars.
    * Prologue: minor glitch
        * purple fuzz on right side of screen, OR it loops around to the left side if you make it wider...
    * Chapter 1: done
    * Chapter 2: done
    * Chapter 3: done
    * Chapter 4: done
    * Chapter 5: quite minor glitch
        * left side of final "t"'s hat
    * Chapter 6: done
    * Epilogue:  done

### quality of life
* Get save files for each chapter and give myself tons of EVO Genes.
    * EVO genes are located at offset 0x1a-1b in each save file.

### tech debt
* Unify spare_block and other_spare_block.

### Bugs Present in the JP Version
* Ch5 Gaia's Heart transaprency, but only in Shambahla.
    * This is present in the original JP version.

* Ch5 Graphical glitch in the lava when entering the second-to-last screen in the Stonehenge dungeon.

### common problems and their solutions
* If a "&" appears before a string when it gets replaced:
    * There's probably an 81-40 sjis space in front of it. Add it to the JP part of the dump so it gets replaced.

* If something in the overflow text overflows into another string:
    * Make sure you split up the block of the first overflow string AFTER an <END> tag.

* If the reinserter can't find the original jp string:
    * Look for Shift-JIS spaces that accidentally got converted to ASCII spaces.
    * Also check to see if two blocks accidentally overlap.

* If the Gaia's Hearts don't do anything:
    * Try not to disturb the length of the strings above the You Found Gaia's Heart msg. (Give them their own block?)

* If it freezes before the next map loads:
    * Look at the location of "MAPXYZ.MAP" and make sure the previous block ends at the first "M", not slightly before.

* If a block is "too long" despite all the countermeasures:
    * It's probably ending at the wrong place, go fix that.
    * Or there are a bunch of untranslated strings right at the end of the block, so it can't tell that it overflows.

* If it can't find the string when it's creating overflows/checking their new length:
    * Check the overflow pointers and see if some random pointer is breaking up the text before the next text pointer. Absorb that pointer into the one at the beginning of the text.

* If NPC movement is broken:
    * Make sure map pointers are ok.
    * Make sure "You evolved further..." is untouched/the SEND.DAT, rb, ISIWAKU.GDT, etc. strings before the battle block are ok.