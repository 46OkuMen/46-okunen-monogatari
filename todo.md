## Crashes
* Ch3 combat pointers are really messed up.

* The FDI rom crashes when ST1.EXE is reinserted - "Abnormal program termination".

* Ch2 crash right after "The gigantic rock lost its balance and fell into the river of magama below."
    * This is going to be quite annoying to fix - it's super late into the chapter...
    * Pointer-peek 0x6457, 0x6468, 0x649a, 0x64cc, ...
    * 0x6468 points to 0x1078d, which is nothing
    * 0x64cc points to 0x10789, which is also nothing

## Non-Crash Glitches
* Random "u" being shown during the Ending.

* Gotta fix the Ch3 and Ch4 menu item alignments again. Ugh.

* Ch2, Ch3 environment text problems
    * "Got %d EVO Genes. <LN> You defeated the enemy!"
    * "Got %d EVO Genes. <LN> 'Ho-ho-ho-ho!'"
        * Bug: Christmas comes early
    * I should make sure there are <END> codes after "Got %s evo genes" whenever it appears in the spare block.
* One entry in the credits (character digitizing) is being skipped.

## Dump Problems
* A significant number of problems I've been facing recently have had to do with the Shift-JIS spaces missing in the dump. It's weird when they're missing from the middle of strings...

* Why are SINKA.DAT and SEND.DAT offsets still wrong? And why aren't the files in the dump from assisted_dump.py at all??

## Block Layout
* I should put stuff that comes before Gaia's Heart text in a separate block! That will remove the super awkward constraints I'm facing.
* Looks like I need to be stricter with splitting the blocks at map files as well. I thought I fixed that, but I guess not enough...
    * This might be a </<= error with the new way I'm handling overflow and editing pointers and stuff. I am having mroe of those problems now than I did before.

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

* Allow a "blank" translation entry rather than just doing the one-space thing I'm doing now.
    * Currently a blank entry just means no translation is provided, so the text remains japanese.
    * I should implement a control code like <blank> for this.

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

* ~~Is there a hard length limit on skill names?~~
    * "Swift AttacGo Behind"
    * Intimidate" is fine.
    * Swift Attack and Go Behind look fine in the ROM dump itself.
    * ~~Changing Swift Attack to be "Swift" in the sheet, see if that helps?~~
        * Nope. No hard limit on skill names, either...
        * Why is it going wrong then?

* Because text speed=0 makes some text unreadable if arranged improperly, I need to nail down the rules.
    * No more than 3 lines between <WAIT>s?
        * I can insert new <LN>s in the middle of lines, but that means I should remove the later one.

### rerouting pointers for duplicate strings 
* ST1.EXE, "Got %dp. EVO Genes."
    * Text at 0x691b, pointer at 0x1586.
    * Text at 0x10f6e, pointer at 0x7731.
* ST2.EXE, "Got %dp. EVO Genes."
    * Text at 0xc263, pointer at 0x1746.
    * Text at 0xe907, pointer at 0x5e4f.
    * Text at 0xfa8a, pointer at 0x7255.
* ST3.EXE, "Got %dp. EVO Genes."
    * Text at 0xb531, pointer at 0x162a.
    * Text at 0xd252, pointer at 0x59ae.
    * Text at 0xdb25, pointer at 0x652e.
* ST5S3.EXE, 'Demon'
* ST5S3.EXE, 'The enemy'
* ST5S3.EXE, duplicate skill name strings

### images
* 46 OK gdt is completely illegible, of course.
    * When and why does the codec return "Sequence contains no elements"??

### other
* What is the ST1S1.EXE, ST1S2.EXE, etc. that gets pointed to in ST1.EXE?

* Looks like the .gitignore is on the fritz...

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