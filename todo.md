## Crashes
* Possible soft lock: Can't advance beyond the Euparkeria in the cave in ch4 because the wrong dialogue is loaded??
** Removing that block of text prior to the text in question and seeing what happens.

* Crash on entering warp rock in ch4.
** Delete text blocks to figure out which one is the culprit.
*** Looks like it's in the last dialogue block.
*** Fixed when breaking up this text block.

* Crash on talking to the elder dino guy at the top of the second warp rock in ch4.
** This looks like some kind of error with the pointers - displays a "v" text box, then syntax error, then crash.
** A pointer to character-move control codes is probably getting messed up. Better not include those in the block.
** Oh, looks like it's the "forest" text replacment listed below that's to blame.
*** Removed the "forest" replacement, now it works.

## Mistaken Text Replacement
* "Slime" in ch3 is replacing the "slime" in the nametag for "Anxious Slime".
** Looks like this messes up some of the dialogue pointers in the rest of the area's text.
** Looks like there's no crash due to it. Yay!

* "Forest" in ch4 is replacing the mention of it in some previous dialogue.

## Non-Crash Glitches
* Fix MAP100.GDT, which got overwritten somewhere.

## Dump Problems
* Duplicate entries in the encyclopedia? エリオセリス has a few entries, etc
** Whoops, I'm dumb - it's just the same creature showing up in different chapters.

* ST2.EXE 0xd1fe nametag gets duplicated, skipping a line of dialogue. The skipped line shows up at 0xd3d3...

## Text Fixes
* "A Eryops attacked!!"
** Is there a non-articled way of phrasing this that still sounds like English?
*** "A wild Eryops attacked!!"
*** "The Eryops attacked!"
** Or is there a way of calling "A" or "An" appropriately?
*** Look at what text is called when fighting Lucifer - probably a different bit of text is called.
*** Hope this doesn't involve ASM hacking.
** Same thing for "You evolved into a Eryops!"

* "You can't make a dent..." can also be triggered by the opponent's attack not making a dent.
** Correction: "Can't make a dent..."? "It won't make a dent..."?

* "Unlucky hit!" is the enemy's critical hit, which the text doesn't convey very well.

* Any way to reposition the stats? Like add a few spaces to the left of DEF and HP?
** Just spaces seems to have no effect. Look in the ROM and see if the spaces are there...
** Oh, actually this works fine. DEF looks good, HP could use another space but there's no room.

* "Your turn!" jumps up and down if you enter and leave the "Special" menu. Check if this happens in JP version.

## Tools

### reinsert.py
* I might want to make the overflow checker more flexible.
** It doesn't catch non-translated stuff at the ends of blocks.
** Or, I could just wait until this stuff is translated...

* PEP8 stuff. Shiny new Pylint extension will annoy me into fixing a lot of it.
** Definitely look for ways to break up edit_text(). It's way too big now.

* See if get_translations() works for the .dat files. If so, we can get rid of get_dat_translations.
** If that's the case, I can probably separate the pointer-counting and text-editing parts of edit_text().

* Cheats - changing the starting map currently only works for chapters 1 and 2.
** Could I change disks while the TITLE1.GDT image is being displayed to get it to load a different chapter map?
*** Nah, that doesn't work...

### update_duplicates.py
* When creature name X is translated, also look for creature names XA, XB, XC, XD, XE.
** Gotta review the character encoding conversions.

### future tools
* A tool to combine all the %d, %u, %s formatted strings in all sheets.

### other
* Fix the randomly decaying excel formulas.