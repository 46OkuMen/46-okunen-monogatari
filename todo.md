# Priorities
* Playable game all the way through
* Whole game is English
* No jarring graphical glitches
* Good presentation
* Minimizing arbitrary limits on the translation
* Having a nice codebase

### Crashes

### Text Oddities
* Ch4: Work, Refuse, d
* Ch4: "I believe I can thiank you properly now." "Hold on to me!" have a text leak of EVO Encyclopedia after them.
* Ch4: "Fellas! With me!" is followed by "Are you stupid? YOu're so disgusting I don't even feel like eating you!" which probably doesn't belong there.
* Ch4: "Let's go, fellas!" is followed by 'However..."'

* Ch5 Gaia's Heart transaprency, but only in Shambahla.

### Tools
* write() for .DAT files seems to write files of their original length, not their expanded length...

### Typesetting
* So it looks like ST6.EXE has a lot of lines that end in <LN><END>, which means pointer_peek never looks past the end of that line. So that's why you get really short middle lines when it gets typeset.
    * Ah, sage. The planet's balance is beginning to crumble everywhere<LN><END>
    * due to the influence of the Witch's evil waves."<WAIT><LN><END>
    * Gotta just take care of those manually, I suppose...?

* Split text into 3-line windows.
    * Even including the nametag... very tricky.
    * Figured out which strings need this; it's all in the sheet now. Use the [SPLIT] control code.
        * Lines with a [SPLIT] need an extra <LN> at the end before the initial <WAIT>...

* Center ENDING story text.

* Undo integrate_spaces() if possible.

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

* Reinsert the revised images.
    * Prologue: this one's going to be hard, watch out
    * Chapter 1: done
    * Chapter 2: done
    * Chapter 3: done
    * Chapter 4: slight graphical glitch on left side of second 'r'
    * Chapter 5:
    * Chapter 6:
    * Epilogue:

### tech debt
* Unify spare_block and other_spare_block.

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