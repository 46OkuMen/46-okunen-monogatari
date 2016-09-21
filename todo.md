## Crashes
* The FDI rom crashes when ST1.EXE is reinserted - "Abnormal program termination".

* Ch4 crash on entering first area on map.
    * Occurs when reinserting something in the last dialogue block (ending 0x14847 ish)

* Two OPENING.EXE has two crashes/sticking points: 
    * on the third intro image/ "A barred spiral galaxy on the outreaches of space...." Some pointer thing?
    * MUsic Programming: TAGUCHI Yasuhiro (never progresses past that)
    * Something is up with the pointers, certainly - if I only translate Character Digitizing in the credits, the first one that shows up as translated is Map Digitizing (one after)...

* At least one sticking point in ENDING.EXE:
    * "But you had no body" or something like that.
    * And maybe the one afterwards? Check that.

* Is the end of the game really a GEAGR error after the credits???? That can't be right.
    * If I am evil, I might just replace that error message with "Brought to you by hollowaytape, kuoushi, SkyeWelse, and friends"

## Mistaken Text Replacement
* In the middle of finding a better way to slice the blockstring when looking for the original jp_bytestring.
    * I still get like 5-10 strings per program which are not at their expected locations. Currently they're being handled by using the entire old blockstring as the slice to be searched, which means if the string appears as a substring of some other previous string, it'll do mistaken text replacement.
        * So what's going on with these strings?
        * One theory: It's all the strings that have SJIS spaces before the actual text begins!
            * That's great, since I was going to need to look for those anyway and shorten them.

## Non-Crash Glitches
* Ch2, Ch3 environment text problems
    * "The temperature dropped suddenly!!" "s" <-- oh, this problem is probably from the overflow problems - check it again
    * "Got %d EVO Genes. <LN> You defeated the enemy!"
    * I should make sure there are <END> codes after "Got %s evo genes" whenever it appears in the spare block.

## Dump Problems
* A significant number of problems I've been facing recently have had to do with the Shift-JIS spaces missing in the dump. It's weird when they're missing from the middle of strings...

* Why are SINKA.DAT and SEND.DAT offsets still wrong? And why aren't the files in the dump from assisted_dump.py at all??
 
## Text Fixes
* Remove the extra spaces around 0xe160 in the robot's dialogue.

* Why are various humanoid creatures in ch5 showing up with different names in their nametag and HP bar?
    * "Vegetarian Monkey People" show up as creature type "Neanderthal".
    * Check to see if this is also the case in the jp version.

* I'm still not entirely sure how I fixed the Save/Load Game spacing in ch2, other than "trial and error with inserting spaces before and after the string"...
    * Oh, I think I at least understand why it's that way:
        * You have multiple pointers to "Save Game" in ch2, called once for the menu item and once for the header text box of actually saving your game.
        * In the header, it's offset from the left by one space to make it more centered in the box.
        * So in the string "  Save Game", the menu item is a pointer to the third character and the header is a pointer to the first character.
            * (I read about this later in one of Gideon Zhi's tutorials: http://agtp.romhack.net/docs/pointers.html )
        * Sometimes the game has multiple "Save Game" or "Load Game" strings with spaces/no spaces, sometimes they are combined in this way.

* In ST5S3.EXE, you have to keep the battle options pretty much the same length, Some pointers are being weird.

* Any way to reposition the stats? Like add a few spaces to the left of DEF and HP?
    * Just spaces seems to have no effect. Look in the ROM and see if the spaces are there...
    * Oh, actually this works fine. DEF looks good, HP could use another space but there's no room.
        * Can I subtract a space from the preivous stat?
            * Yes.
    * Check to see if larger INT values run into the stat name later.
        * Doesn't look like it - the game is intelligent about spacing text like that.
        * Still need the INT stat name to be 5-6 character max. Wisdom maybe? (not really good for describing animals)

## Tools

### disk.py
* Looks like most chapter scripts will be too long. Is there any other way for me to get space?
    * Definitely can't expand into the block of 00s and various other data right after the last block... causes graphical errors.
    * Can I use the small block of 20s after that?
        * No - the chapter doesn't even boot if there's anything in that area.
    * How much space is taken up by the text padding I create when I slice the blocks that overflow in the first place?
        * I could try inserting shorter overflow bytestrings there in the first place before I even move to the spare block.
            * In progress. Requires a lot of restructuring how overflow works.
    * I can probably trim the spaces from some of the AV events that use spaces to center text...
        * Can I use tabs to achieve a similar effect without using so much space?

* Allow a manual line break in english text: <LN> becomes the byte 0A, or whatever.
    * This is tricky with length stuff, I think - the ln is only one character, so make sure the diff is still calculated correctly.
    * Not even necessary! Newlines in excel (alt+enter) show up ingame, since 0A is a newline in ascii and sjis.
    * The real issue is - how to remove line breaks after the strings if I want to change the \n's position?
        * I could fuse the jp string into a "s1\ns2\ns3" excel row...
        * Any way to do that quickly?

* Rewriting the romstring, filestring, and blockstring properties to use bytearrays instead of immutable strings would improve speed a lot!
    * This changes a lot of the biz logic, of course. (Mostly, string indexes are /2 of their original value, and so are lengths)
    * This wasn't the real bottleneck anyway - that was the unnecessary Excel sheet reading.

### test.py
* Assert that a blank translation sheet returns no overflow errors.
    * If there are errors, that means that block is a byte or two too short in rominfo.py.
* A test suite would be good at telling if strings are where I think they are, and thereby spot mistaken reinsertion.
* Assert that there is no overflow in files without a spare block.
* String length validation.

### cheats.py
* Original map-changing cheats aren't working now for some reason. Is it due to the image reinsertion?
    * Nope, the mapname file is just part of a block when it wasn't before. So something else is getting edited instead.
    * Tried to split the block, got "block too long" errors...

* Get rid of this and make it a method of an EXEFile.

### length validation
* What is the best way to do editing for line lengths and such?
    * The simplest is that all strings definitely can't be over 76. (max for bottom narration)
        * All strings in SINKA.DAT and SEND.DAT must be below 68. (bottom narration - indent)
    * Strings in creature block <= 22.
    * Strings in battle block <= 42.
    * Strings in the menu block <= 42. (Since evolution messages, etc.)
    * Strings in opening/ending <= 76. (It loops around at that point and looks ugly)
    * Stamina/Strength/Attack are fine, but Intelligence needs to be 5-6 chars or less.

* Is there any way to programmatically check which strings are part of fullscreen narration events?
    * One clue: it comes right after an AV*.GDT file (in the full dump).
        * (But how many strings in a row?? Doesn't it swtich to dialogue at some point?)
            * (Could I recognize nametags as they come up?)
                * (Not really useful, sometimes dialogue is fullscreen (ex. Gaia ch1))
    * I probably can't do the whole thing programmatically, but I can get a list of strings after AV.GDTs and mark them manually from there.
        * I can probably just use a column in the dump sheet to specify if it's fullscreen or not.
            * I was thinking I'd have to label every string with some category, but I really just need to distinguish dialogue and fullscreen, I think - the rest are easy enough to tell.

* Because text speed=0 makes some text unreadable if arranged improperly, I need to nail down the rules.
    * No more than 3 lines between <WAIT>s?
        * I can insert new <LN>s in the middle of lines, but that means I should remove the later one.

### other
* Fix the randomly decaying excel formulas.
    * I am very incompetent at excel, it seems.

* What is the purpose of Disk B1? Does it contain anything not in Disk B2? Is it a part of gameplay at all?
    * It might be an install disk.

* Looks like the .gitignore is on the fritz...

### common problems and their solutions
* If a "&" appears before a string when it gets replaced:
    * There's probably an 81-40 sjis space in front of it. Add it to the JP part of the dump so it gets replaced.

* If something in the overflow text overflows into another string:
    * Make sure you split up the block of the first overflow string AFTER an <END> tag.

* If the reinserter can't find the original jp string:
    * Look for Shift-JIS spaces that accidentally got converted to ASCII spaces.

* If the Gaia's Hearts don't do anything:
    * Try not to disturb the length of the strings above the You Found Gaia's Heart msg. (Give them their own block?)