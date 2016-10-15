## Crashes
* The FDI rom crashes when ST1.EXE is reinserted - "Abnormal program termination".

* Ch5 crash on entering Shambahla.
    * So much progress lost...
        * Not quite. You can reload the EXE file by ingame saving, loading an empty save and switching to Disk 2, then loading the original save again and switching disks. Great!
    * Looks like a problem with the image, not the map. Should be the very first thing in ST5S2.
    * That image pointer looks fine too, as does the text...
    * Is it a problem with ST5S2 reinsertion?
        * Yeah, somehow - it works fine when I delete all the ST5S2 text.
        * How about reinserting everything except the first string?
            * Nope.
        * It's not that I overwrote the memory error either.
    
* Losing the ability to navigate menus in Ch3 after a few battles...??
    * Also happened in Ch4 after a lot of battles...?
    * Check if this still happens after fixing the overflow filename strings bug.

* Crash on selecting "EVO Encyclopedia" in Ch6.

* Crash on reading the encyclopedia entry for Dino Hominid/Dinosaur Man.
    * I think that SINKA.DAT was impropertly reinserted - some older strings are showing up in the game that are definitely not in the real translation, but were probably in the placeholder one.

* Ch2 crash right after "The gigantic rock lost its balance and fell into the river of magama below."
    * This is going to be quite annoying to fix - it's super late into the chapter...
    * Pointer-peek 0x6457, 0x6468, 0x649a, 0x64cc, ...
    * 0x6468 points to 0x1078d, which is nothing
    * 0x64cc points to 0x10789, which is also nothing
    * Check if this still happens after fixing the overflow filename strings bug.

## Non-Crash Glitches
* Random "u" being shown during the Ending.

* There's an extra string at the end of the Ch3 "You found Gaia's Heart" msg.

* One creature is "Goaton" in game but "Hitsujion" in the encyclopedia.

* Ch4 menu items are misaligned.

* Make sure to fix the "Text Speed" alignment which gests messed up in a few chapters.

* One entry in the credits (character digitizing) is being skipped.

* "Wisdom" runs against the stat number, any way to realign it?

## Tools

### disk.py
* Allow a "blank" translation entry rather than just doing the one-space thing I'm doing now.
    * Currently a blank entry just means no translation is provided, so the text remains japanese.
    * I should implement a control code like <blank> for this.

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
* Figure out which "You defeated the demon!" strings in Ch5 actually get used.
    * Americas, Asia use ST5S3 battle mssages.
    * Continue investigating from the save file alt+f6.
* Will the game display the umlaut in "Dusseldorf" correctly?
* What is the ST1S1.EXE, ST1S2.EXE, etc. that gets pointed to in ST1.EXE?

* Looks like the .gitignore is on the fritz...

* ST5S2 has like 100 pointers to 0x2360 (Turbo-C compiler message), all 4 apart (like in a table). Is this normal?

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