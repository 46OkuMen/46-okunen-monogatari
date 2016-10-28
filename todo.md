# Priorities
* Playable game all the way through
* Whole game is English
* No jarring graphical glitches
* Good presentation
* Minimizing arbitrary limits on the translation
* Having a nice codebase

### Crashes
* The FDI rom crashes when ST1.EXE is reinserted - "Abnormal program termination".

* Crash after defeating final boss.
    * Yep, it's definitely something in ST6 - a blank translation doesn't have this problem.
    * Deleted strings 118-227, can't remember if worked
    * Deleted strings 118-157, didn't work
    * Deleted strings 159-301: works
        * Deleted strings 289-301: doesn't work
        * Deleted strings 159-200: works
            * Deleted strings 159-176: works
                * Deleted strings 175-176: Doesn't work
                * Deleted strings 159-169: Doesn't work
                * Deleted strings 170-174: works
                    * Deleted strings 172-174: doesn't work
                    * Deleted strings 170-171: doesn't work
                    * Deleted strings 171-173: doesn't work
                    * Deleted strings 171-172: doesn't work
                    * Set strings 170-174 to the same length: works
                        * (That could be a workaround.)
                    * Split the block after string 174: works with full translation


### Text Oddities
* Ch4: Work, Refuse, d
* Ch4: "I believe I can thiank you properly now." "Hold on to me!" have a text leak of EVO Encyclopedia after them.
* Ch4: "Fellas! With me!" is followed by "Are you stupid? YOu're so disgusting I don't even feel like eating you!" which probably doesn't belong there.
* Ch4: "Let's go, fellas!" is followed by 'However..."'

* Strings with numbers which get displayed more than once have the numbers get corrupted into ASCII letters.
    * "One pillar alone was over (10m) P0m, at the very least."
    * "R.T (3.5) billion years"
    * "STT (5) evolve"
    * O, P, (Q), R, S, T
    * 0, 1, (2), 3, 4, 5
    * ASCII letters: 4f, 50, 51, 52, 53, 54...
    * ASCII numbers: 30, 31, 32, 33, 34, 35...
    * SJIS numbers:824f, 50, 51, 52, 53, 54... (oh, ok)
        * The game text-printing routine probably takes the number in memory, increments it by 0x1f, and prepends 82 to it prior to printing.
            * This instruction is present in gameplay files but not OPENING/ENDING.
    * Do you get the same effects if you just insert the fullwidth numbers in those places to begin with?
        * Looks like it crashes when it tries to render the fullwidth numbers in a string with ASCII stuff.

* Ch5 Gaia's Heart transaprency, but only in Shambahla.

* "Wisdom" runs against the stat number, any way to realign it?

* Make sure to fix the "Text Speed" alignment which gests messed up in a few chapters.

* Add a space after the number in the switch disks message in 46.EXE.

### Tools
* write() for .DAT files seems to write files of their original length, not their expanded length...

### Typesetting
* What's causing the infinite loops in ST2, ST3, ST4, ST5 typesetting?

* ST5S1 has an assertion error about too many textlines in a pointer.

* Split text into 3-line windows. 

* Determine alignment of ENDING credits entries. (Lots of text is already centered)

* Center ENDING story text.

* Undo integrate_spaces() if possible.

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

### images
* AV04B.GDT is completely illegible, of course.
    * When and why does the codec return "Sequence contains no elements"??

* Let's try just getting the logo in the game as a placeholder.
    * But it needs to take up most of the screen to prevent the previous images from showing through.
        * Width:
            * 600 is actually not wide enough - green graphical glitches show up on the side.
        * Height:
            * 258 doesn't work
            * 250 works, but stuff shows through
            * 266 doesn't work
            * 286 doesn't work
            * 300 doesn't work
            * 302 doesn't work
            * 304 doesn't work
            * 306 doesn't work
            * 308 doesn't work
            * 310 doesn't work
            * 314 doesn't work
            * 358 doesn't work
            * 360 is close to working, but not really
            * 368 is also really close to working, but also not really
            * 370, 372, 374 look the same as 368
            * 378 is closer still
            * 380-400 all don't work
            * 500 also doesn't work
* With the luck I'm having, I may just want to try the whole damn thing. If I get lucky and it works, I'd like to only need to get lucky once.

### tech debt
* Change the pointers API to store Pointer objs, not integers corresponding to text location.

* Unify spare_block and other_spare_block.

### other
* Looks like the .gitignore is on the fritz...

* Flashing lights warning?

### portuguese stuff
* What characters go unused in the game script? Need maybe 26 of them.
    * Actually less complicated to implement would be A1-DF, which are half-width kana.
    * Anex86 needs anex86.bmp edits.
    * np2 needs FONT.ROM edits.

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

* If it can't find the string when it's creating overflows/checking their new length:
    * Check the overflow pointers and see if some random pointer is breaking up the text before the next text pointer. Absorb that pointer into the one at the beginning of the text.

* If NPC movement is broken:
    * Make sure map pointers are ok.
    * Make sure "You evolved further..." is untouched/the SEND.DAT, rb, ISIWAKU.GDT, etc. strings before the battle block are ok.