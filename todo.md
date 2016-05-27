## Crashes

## Mistaken Text Replacement

## Non-Crash Glitches
* Two menu items have disappeared in Ch2.

## Dump Problems
* Carnivorous Dino Person has a missing piece of dialogue between 0xcf16 and 0xcf64.

* ST2.EXE 0xd1fe nametag gets duplicated, skipping a line of dialogue. The skipped line shows up at 0xd3d3...
** Fixed this. Not sure why it happened, unfortunately.

## Text Fixes
* Why isn't "Escape" getting translated in 5-S3?

* "Unlucky hit!" is the enemy's critical hit, which the text doesn't convey very well.

* Any way to reposition the stats? Like add a few spaces to the left of DEF and HP?
** Just spaces seems to have no effect. Look in the ROM and see if the spaces are there...
** Oh, actually this works fine. DEF looks good, HP could use another space but there's no room.
*** Can I subtract a space from the preivous stat?

* Also, any way to get an extra character in "TextSpeed:"? There's gotta be something I can rearrange.
** Looks like the message box size is fixed! The numnber appears as the last two characters of the box, overwriting whatever's there...

* "Your turn!" jumps up and down if you enter and leave the "Special" menu. Check if this happens in JP version.
** Yeah, it happens there too.

## Tools

### reinsert.py
* Better progress reporting.
** Separate the reporting into a different function. Build a dict of file, progress and process it in a function.
** Get a combined percentage for ch5 files (ST5, ST5S1, ST5S2, ST5S3) (done but ugly)
** Get a (translations/rows) breakdown as well. (done)

* I've got serious problems reinserting into OPENING.EXE...
** Maybe I should try again using the original JP strings that have spaces in them? It's having trouble finding all the credits names.
** Also, crashing for some reason, maybe I shouldn't treat the errors as a spare block???

* PEP8 stuff. Shiny new Pylint extension will annoy me into fixing a lot of it.
** Definitely look for ways to break up edit_text(). It's way too big now.
** Ehh. It's a little late to try and make it OOP. But I have learned my lesson - "why OOP is useful in preventing spaghettification of code"

### cheats.py
* Are stats stored in memory during chapter changes? Can I find and edit them?

* I'd love to figrue out where the position of the character is loaded, so I can warp to more maps.

* Can I replace OPENING.EXE with ENDING.EXE for testing?
** No, it just skips it...

### update_duplicates.py
* When creature name X is translated, also look for creature names XA, XB, XC, XD, XE.
** Gotta review the character encoding conversions.

### future tools
* A tool to combine all the %d, %u, %s formatted strings in all sheets.

### other
* Actually make a patch!
** It'd be nice to generate a patch immediately during the reinsert process.
*** Look into Travis CI or whatever standard windows build tools there are.
** Any good python modules for creating ips patches or maybe Lunar or Ninja ones?

* Fix the randomly decaying excel formulas.
* What is the purpose of Disk B1? Does it contain anything not in Disk B2? Is it a part of gameplay at all?

### common problems
* If a "&" appears before a string when it gets replaced:
** There's probably an 81-40 sjis space in front of it. Add it to the JP part of the dump so it gets replaced.

* If something in the overflow text overflows into another string:
** Make sure you split up the block of the first overflow string AFTER an <END> tag.