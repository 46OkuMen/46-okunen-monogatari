## Crashes
* Try to realign the final dialogue block in ch4 - filling it in causes soft locks on menu changes.
** Lucifersaurus, Accept/Decline, Lucifer is fine.
** Uh, it all seems fine to me...

* Menu crash in ch5 has returned.
** Looks like something is beting treated as overflowing when it shouldn't be...?
** Ah. Gotta end every block AFTER an <END> tag, not on the first one.
** It would be useful to have a test that sees if any file has overflow when it's passed a blank translation sheet...

## Mistaken Text Replacement

## Non-Crash Glitches

## Dump Problems
* Carnivorous Dino Person has a missing piece of dialogue between 0xcf16 and 0xcf64.

* ST2.EXE 0xd1fe nametag gets duplicated, skipping a line of dialogue. The skipped line shows up at 0xd3d3...
** Fixed this. Not sure why it happened, unfortunately.

## Text Fixes
* I'm still not entirely sure how I fixed the Save/Load Game spacing in ch2, other than "trial and error with inserting spaces before and after the string"...
** Oh, I think I at least understand why it's that way:
*** You have multiple pointers to "Save Game" in ch2, called once for the menu item and once for the header text box of actually saving your game.
*** In the header, it's offset from the left by one space to make it more centered in the box.
*** So in the string "  Save Game", the menu item is a pointer to the third character and the header is a pointer to the first character.
*** Sometimes the game has multiple "Save Game" or "Load Game" strings with spaces/no spaces, sometimes they are combined in this way.

* Why isn't "Escape" getting translated in 5-S3?
** It is; there are some weird ASCII spaces at the end of "Fight" and "Special" though in the original japanese...?
** Ooh, looks like one of my old tricks is backfiring - it truly is an ASCII space (20) and my script is replacing all those with SJIS spaces, so it can't find it in the original text.
** How about if I just add a space to the end of the english?
*** Uh, that just adds another space to the one that's there...
** Hm. I fixed the space problem but I think this is something else - mistaken text replacement?
*** Some battle message gets repeatedly messed up. It involves the kanji for "power".

* Any way to reposition the stats? Like add a few spaces to the left of DEF and HP?
** Just spaces seems to have no effect. Look in the ROM and see if the spaces are there...
** Oh, actually this works fine. DEF looks good, HP could use another space but there's no room.
*** Can I subtract a space from the preivous stat?
**** Yes.
** Check to see if larger INT values run into the stat name later.

* Also, any way to get an extra character in "TextSpeed:"? There's gotta be something I can rearrange.
** Looks like the message box size is fixed! The numnber appears as the last two characters of the box, overwriting whatever's there...
** ...But in ST2 I was able to add an SJIS space before it! That gives me room.

## Tools

### reinsert.py
* Better progress reporting.
** Separate the reporting into a different function. Build a dict of file, progress and process it in a function.
** Get a combined percentage for ch5 files (ST5, ST5S1, ST5S2, ST5S3) (done but ugly)
** Get a (translations/rows) breakdown as well. (done)
** How to think about progress reporting for strings that don't need translation? (numbers in .DATs, etc)

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