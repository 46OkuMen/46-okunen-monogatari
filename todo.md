### Text Oddities
* Some odd text timing in the Ch6 hopeless Devil fight.
    * Too-long pause after "bolts of lightning", no pause at all when it tells you how much damage you've taken
        * Check out the JP version
            * Looks like the JP version tries not to display the damage numbers at all! 
        * Insert [PAUSE] control codes as needed.

* "forelegs" / "hind legs".

* Find other numbers that are likely victims of the number corruption bug.

### Other weird things
* Evolution during a game over story. Phaestus -> Goblin story -> Asamin.
    * Evolved by increasing Endurance.
    * Had infinite EVO genes on.
* Why is it so hard to land accuracy-based attacks (Air Power, skills) in the Ch5 Devil fight for me, but not kuoushi?

### Typesetting
* Manual text stuff.
    * Chapter 1: done
    * Chapter 2: done
    * Chapter 3: done
    * Chapter 4: did three passes, has like 3 things that still need to be fixed
    * Chapter 5: did one pass, pretty good
    * Chapter 6: done

* Center the credits text

* Broken text in game over stories:
    * Green Dragon - manual fix (space before "Human")
    * Gold Dragon - manual fix
    * Merychippus
    * Coelacanth
    * Currently being kept track of on a google sheet.

### tech debt
* Unify spare_block and other_spare_block.

### Bugs Present in the JP Version
* Ch5 Gaia's Heart transaprency, but only in Shambahla.

* Ch5 Graphical glitch in the lava when entering the second-to-last screen in the Stonehenge dungeon.

* Protungulatum encyclopedia entry doesn't wait after the last line.
    * Fixed this one (it's pretty easy)

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