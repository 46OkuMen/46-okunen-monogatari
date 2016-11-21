### Crashes
* Ch4 freeze upon entering Ch5.
    * There were excessive spaces that time, remove those and try again.
    * Crash on displaying the disk number you're supposed to insert??
        * Trying again with a fresh playthrough.

### Text Oddities
* Some odd text timing in the Ch6 hopeless Devil fight.
    * Too-long pause after "bolts of lightning", no pause at all when it tells you how much damage you've taken
        * Check out the JP version
            * Looks like the JP version tries not to display the damage numbers at all! 
        * Insert [PAUSE] control codes as needed.

* Find other numbers that are likely victims of the number corruption bug.

### Typesetting
* So the code I wrote to indent dialogue is a total mess.
    * I need to find a way to indent it during the textlines loop that's checking the length. Otherwise, indenting it later without checking the length might cause it to spill over of course.
    * Also gotta be careful not to add spaces in a way that could cause overflow in the make-sure-bytestrings-have-equal-length phase at the end. Adding them between two newlines is harmless, or between a wait and an end...

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

* I can probably get away with a 44-character window if I can manually remove the <LN> between two lines!
    * A handful of typeset lines look overly cautious as they are now.

* The typesetter seems really wrong about the width of particular strings, since it's refreshing the text locs.

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