## Crashes
* The FDI rom crashes when ST1.EXE is reinserted - "Abnormal program termination".

* Ch2 crash right after "The gigantic rock lost its balance and fell into the river of magama below."
    * This is going to be quite annoying to fix - it's super late into the chapter...
    * Pointer-peek 0x6457, 0x6468, 0x649a, 0x64cc, ...
    * 0x6468 points to 0x1078d, which is nothing
    * 0x64cc points to 0x10789, which is also nothing

* Two OPENING.EXE has two crashes/sticking points: 
    * on the third intro image/ "A barred spiral galaxy on the outreaches of space...." Some pointer thing?
    * MUsic Programming: TAGUCHI Yasuhiro (never progresses past that)
    * Something is up with the pointers, certainly - if I only translate Character Digitizing in the credits, the first one that shows up as translated is Map Digitizing (one after)...
    * Pointer-peek 0x4c05, 0x4cc09, 0x4c0d, 0x4c15.

* At least one sticking point in ENDING.EXE:
    * "But you had no body to return to" or something like that.
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
    * "Got %d EVO Genes. <LN> You defeated the enemy!"
    * I should make sure there are <END> codes after "Got %s evo genes" whenever it appears in the spare block.

## Dump Problems
* A significant number of problems I've been facing recently have had to do with the Shift-JIS spaces missing in the dump. It's weird when they're missing from the middle of strings...

* Why are SINKA.DAT and SEND.DAT offsets still wrong? And why aren't the files in the dump from assisted_dump.py at all??

## Block Layout
* I should put stuff that comes before Gaia's Heart text in a separate block! That will remove the super awkward constraints I'm facing.
 
## Text Fixes
* Why are various humanoid creatures in ch5 showing up with different names in their nametag and HP bar?
    * "Vegetarian Monkey People" show up as creature type "Neanderthal".
    * Check to see if this is also the case in the jp version.

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
* Why isn't ST2.EXE using all of the spare block? There should be like 100 characters left...

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

### test.py
* Assert that a blank translation sheet returns no overflow errors.
    * If there are errors, that means that block is a byte or two too short in rominfo.py.

### length validation
* What is the best way to do editing for line lengths and such?
    * The simplest is that all strings definitely can't be over 76. (max for bottom narration)
        * All strings in SINKA.DAT and SEND.DAT must be below 68. (bottom narration - indent)
    * Strings in creature block <= 22.
    * Strings in battle block <= 42.
    * Strings in the menu block <= 42. (Since evolution messages, etc.)
    * Strings in opening/ending <= 76. (It loops around at that point and looks ugly)
    * Stamina/Strength/Attack are fine, but Intelligence needs to be 5-6 chars or less.

* Looks like there are simply SJIS spaces after newlines, which means I can remove those if I want.
    * That means the max length of a dialogue is 44, but 42 excluding that space.
    * Do we want to keep that space?

* Is there a hard length limit on skill names?
    * "Swift AttacGo Behind"
    * Intimidate" is fine.
    * Swift Attack and Go Behind look fine in the ROM dump itself.
    * Changing Swift Attack to be "Swift" in the sheet, see if that helps?
        * Nope. No hard limit on skill names, either...
        * Why is it going wrong then?

* Because text speed=0 makes some text unreadable if arranged improperly, I need to nail down the rules.
    * No more than 3 lines between <WAIT>s?
        * I can insert new <LN>s in the middle of lines, but that means I should remove the later one.

### other
* What is the purpose of Disk B1? Does it contain anything not in Disk B2? Is it a part of gameplay at all?
    * It might be an install disk. Or just the intro (which is on Disk A...)

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

* If it freezes before the next map loads:
    * Look at the location of "MAPXYZ.MAP" and make sure the previous block ends at the first "M", not slightly before.