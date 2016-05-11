## Crashes
* Soft lock in chapter 2 on entering first cave. Player character walks to the right on entering and gets lost.
** Saving and loading in that spot restores the camera. They walk onto a background object and can't walk off.
** Something in the last few text blocks. Not the names.
** Found it - this is caused by changing the length of "Yes/No/Cancel". Fixed by padding "Cancel" to 10chars.
*** Hm, maybe there's something interesting (starting positions? starting movements?) right after these.
* Chapter 2 crashes on changing maps when stuff in the final dialogue block is changed. Break up the block.
* Soft lock in chapter 3 on entering the second cave, in Scandinavia. Player never walks to the right place...

## Non-Crash Glitches
* Graphical glitch on the first mountain in chapter 3 - "ghost" of player's right until entering battle.
** Plus, on leaving that map, the characcter goes right instead of left... weird.
** (Is this also a problem with not padding "Cancel" like above?)

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
** Correction: "Can't make a dent..."?

* "Unlucky hit!" is the enemy's critical hit, which the text doesn't convey very well.

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

### update_duplicates.py
* When creature name X is translated, also look for creature names XA, XB, XC, XD, XE.

### future tools
* A tool to combine all the %d, %u, %s formatted strings in all sheets.
** Gotta review the character encoding conversions.