## Crashes
* Soft lock in chapter 2 on entering first cave. Player character walks to the right on entering and gets lost.
* Chapter 2 crashes on changing maps when stuff in the final dialogue block is changed. Break up the block.
* Soft lock in chapter 3 on entering the second cave, in Scandinavia. Player never walks to the right place...

## Non-Crash Glitches
* Graphical glitch on the first mountain in chapter 3 - "ghost" of player's right until entering battle.
** Plus, on leaving that map, the characcter goes right instead of left... weird.

## Text Fixes
* "A Eryops attacked!!"
** Is there a non-articled way of phrasing this that still sounds like English?
*** "A wild Eryops attacked!!"
*** "The Eryops attacked!"
** Or is there a way of calling "A" or "An" appropriately?
*** Look at what text is called when fighting Lucifer - probably a different bit of text is called.
*** Hope this doesn't involve ASM hacking.

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

### update_duplicates.py
* When creature name X is translated, also look for creature names XA, XB, XC, XD, XE.

### future tools
* A tool to combine all the %d, %u, %s formatted strings in all sheets.