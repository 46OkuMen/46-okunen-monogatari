## Crashes
* The FDI rom crashes when ST1.EXE is reinserted - "Abnormal program termination".

* Ch2 crash right after "The gigantic rock lost its balance and fell into the river of magama below."
    * This is going to be quite annoying to fix - it's super late into the chapter...
    * Pointer-peek 0x6457, 0x6468, 0x649a, 0x64cc, ...
    * 0x6468 points to 0x1078d, which is nothing
    * 0x64cc points to 0x10789, which is also nothing
    * Check if this still happens after fixing the overflow filename strings bug.

## Text Oddities
* Strings with numbers which get displayed more than once have the numbers get corrupted into ASCII letters.
    * "One pillar alone was over (10m) P0m, at the very least."
    * "R.T (3.5) billion years"
    * "STT (5) evolve"
    * O, P, (Q), R, S, T
    * 0, 1, (2), 3, 4, 5
    * ASCII letters: 79, 80, 81, 82, 83, 84
    * ASCII numbers: 48, 49, 50, 51, 52, 53
    * Do you get the same effects if you just insert the fullwidth numbers in those places to begin with?
        * Looks like it crashes when it tries to render the fullwidth numbers in a string with ASCII stuff.

* Ch5 Gaia's Heart transaprency, but only in Shambahla.

* Random "u" being shown during the Ending.

* "Swift AttackLeap"
    * "Swift AttacGo Around" in Ch1, above in Ch3

* Ch4 menu items are misaligned.

* Make sure to fix the "Text Speed" alignment which gests messed up in a few chapters.

* One entry in the credits (character digitizing) is being skipped.

* "Wisdom" runs against the stat number, any way to realign it?

## Freeing Space
* What locations actually have the "Can't save EVO" restriction? That string and the "curse" string can be blanked in chapters without it.
    * The Hemicyclapsis cave in Ch1.
    * Nothing in Ch5.
    * Nothing in Ch6.

## Tools

### Typesetting
* Because text speed=0 makes some text unreadable if arranged improperly, I need to nail down the rules.
    * No more than 3 lines between <WAIT>s?

* Determine the widths of every string in the game.
    * Chapter 1: done.
    * Chapter 2: partially done, up until the giant boulder falling.
    * Chapter 3: done.
    * Chapter 4: not started.
    * Chapter 5: partially done, from the Carnivorous Primate Boss forward.
    * Chapter 6: done.

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
* ST5S1.EXE, 'The frenzied Carnivorous Primate Boss attacks!'
* ST5S3.EXE, 'Demon'
* ST5S3.EXE, 'The enemy'
* ST5S3.EXE, duplicate skill name strings

### images
* 46 OK gdt is completely illegible, of course.
    * When and why does the codec return "Sequence contains no elements"??

### other
* What is the ST1S1.EXE, ST1S2.EXE, etc. that gets pointed to in ST1.EXE?

* Looks like the .gitignore is on the fritz...

* ST5S2 has like 100 pointers to 0x2360 (Turbo-C compiler message), all 4 apart (like in a table). Is this normal?

* Flashing lights warning?

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