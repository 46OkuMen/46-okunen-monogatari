### Crashes

### Text Oddities
* "Escape" is invisible in Ch5.
    * Both pointers on the sheet point to the right thing, check what other pointers should be pointing there.

* Ch5 Gaia's Heart transaprency, but only in Shambahla.

* Find other numbers that are likely victims of the number corruption bug.

### Typesetting
* Find overflowing windows. (4 or more lines). Put a [SPLIT] where appropriate. (Then unsink the final line of the original end of the text)
    * Chapter 1: done
    * Chapter 2: done
    * Chapter 3: done
    * Chapter 4:
    * Chapter 5:
    * Chapter 6:

* Find 'sunken' text. (text occupying bottom two rows with no newline at the end). Put a [LN] at the end of the final line.
    * Chapter 1: done
    * Chapter 2: done
    * Chapter 3: done
    * Chapter 4:
    * Chapter 5:
    * Chapter 6:

* Find text that's typeset unaware of the next string. (Lines that contain only one word or so, when the next string could help fill up the rest of the line). Redistribute the text to even it out.
    * Chapter 1: done
    * Chapter 2: done
    * Chapter 3: done
    * Chapter 4:
    * Chapter 5:
    * Chapter 6:

* Look at the original JP layout for the end credits, see if the weird centering/indenting issue is real

* Re-center "ENIX PRESENTS" text?

* Re-align centered/indented dialogue that's had its spaces taken away.
    * Chapter 1: done
    * Chapter 2: done
    * Chapter 3: done
    * Chapter 4: done
    * Chapter 5: done
    * Chapter 6: done

### Polish
* Edit GEAGRDRV.EXE and insert a "Thanks for playing" type message instead of that string at the end of the credits.
    * String 2 of 3 - "ＧＥＡＧＲを解放しました"

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

### portuguese stuff
* What characters go unused in the game script? Need maybe 26 of them.
    * Actually less complicated to implement would be A1-DF, which are half-width kana.
    * Anex86 needs anex86.bmp edits.
    * np2 needs FONT.ROM edits.

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