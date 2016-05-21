# Oh shit I really gotta fix this one
* I have been updating the offsets, but not the pointers, of the duplicate text in fix_order.py.
** And when I fix them, they go away from fix_order.py. So I can't find them again.
*** (Well, I could go back to the original...)
** Hm. How bad is this? What kinds of text is a duplicate?
*** Nametags
*** "Text Speed:"'s pointer is "Text Speed".
**** (maybe I'm having trouble changing the options string length because I'm not updating the pointer??)
*** ST5S1.EXE has some repeated text but no pointer. yay

## Crashes
* Soft lock when changing maps in ch5.
** All the cancels are fine, though...
** Not in the dialogue block...
** It's in the final normal-combat-messages block...
** Looks like it's having trouble replacing the string "iie"/"no    "??? Why???
*** Also having trouble replacing "Received %d EVO Genes."
*** It points out both of these in a "not found" error. Let's see where it's trying to look for them...

* Crash on entering menu in ch5.
** Nothing wrong with the menu items themselves...
** Not a y/n/c error either.
** Not battle text or creature names.
** It's nothing to do with any of the text I have inserted...
** The only changes to the file are overflow changes... why are they being changed?
*** One is a menu item, I think it's the text speed!
*** Why are these treated as overflowing in the first place? They are the normal text. The block ends must be wrong.

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
* Carnivorous Dino Person has a missing piece of dialogue between 0xcf16 and 0xcf64.

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
* I've got serious problems reinserting into OPENING.EXE...
** Maybe I should try again using the original JP strings that have spaces in them? It's having trouble finding all the credits names.
** Also, crashing for some reason, maybe I shouldn't treat the errors as a spare block???

* I might want to make the overflow checker more flexible.
** It doesn't catch non-translated stuff at the ends of blocks.
** Or, I could just wait until this stuff is translated...

* PEP8 stuff. Shiny new Pylint extension will annoy me into fixing a lot of it.
** Definitely look for ways to break up edit_text(). It's way too big now.

* See if get_translations() works for the .dat files. If so, we can get rid of get_dat_translations.
** If that's the case, I can probably separate the pointer-counting and text-editing parts of edit_text().

### cheats.py

* Cheats - changing the starting map currently only works for chapters 1 and 2.
** Could I change disks while the TITLE1.GDT image is being displayed to get it to load a different chapter map?
*** Nah, that doesn't work...
** Although with the save states I have, I can just change the first map of individual chapters!
*** Done, and moved cheats to their own module cheats.py.

* Can I replace OPENING.EXE with ENDING.EXE for testing?
** No, it just skips it...

### update_duplicates.py
* When creature name X is translated, also look for creature names XA, XB, XC, XD, XE.
** Gotta review the character encoding conversions.

### future tools
* A tool to combine all the %d, %u, %s formatted strings in all sheets.

### other
* Actually make a patch!
* Fix the randomly decaying excel formulas.
* What is the purpose of Disk B1? Does it contain anything not in Disk B2? Is it a part of gameplay at all?