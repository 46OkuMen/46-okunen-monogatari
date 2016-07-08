## Crashes

## Mistaken Text Replacement
* In the middle of finding a better way to slice the blockstring when looking for the original jp_bytestring.
    * I still get like 5-10 strings per program which are not at their expected locations. Currently they're being handled by using the entire old blockstring as the slice to be searched, which means if the string appears as a substring of some other previous string, it'll do mistaken text replacement.
        * So what's going on with these strings?

* It'd be nice if I had a tool that checked the jp strings to see if they're substrings of any previous string, so I could have a list of what could go wrong if I can't fix mistaken text replacement as a whole.

* One cause of mistaken text replacement is when the string appears twice after the last translated text - of course it'll translate the first one it finds after the last translated thing, regardless of whether it's in dialogue or whatever.

## Non-Crash Glitches

## Dump Problems
* Lots of spaces at Ch5:0xfe7d; why?

* Should I consider dumping/getting translations for INST.EXE as well?
    * A preliminary dump shows error messages, installation stuff. Will this ever be seen?? I should ask Skye.

* Why are SINKA.DAT and SEND.DAT offsets still wrong? And why aren't the files in the dump from assisted_dump.py at all??

* Carnivorous Dino Person had a missing piece of dialogue between 0xcf16 and 0xcf64.
    * Same as below. Used sjis-dump to dump st5 again...
    * Should I be nervous whenever I see two nametags in a row?
    * Oddly, this line of dialogue was present in the original dump I gave to kuoushi...?

* ST2.EXE 0xd1fe nametag gets duplicated, skipping a line of dialogue. The skipped line shows up at 0xd3d3...
    * Fixed this. Not sure why it happened, unfortunately.

## Text Fixes
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

## Tools

### reinsert.py
* Allow a manual line break in english text: <LN> becomes the byte 0A, or whatever.
    * This is tricky with length stuff, I think - the ln is only one character, so make sure the diff is still calculated correctly.

* Rewriting the romstring, filestring, and blockstring properties to use bytearrays instead of immutable strings would improve speed a lot!
    * This changes a lot of the biz logic, of course. (Mostly, string indexes are /2 of their original value, and so are lengths)

### test.py
* Assert that a blank translation sheet returns no overflow errors.
    * If it does, that means that block is a byte or two too short.
* A test suite would be good at telling if strings are where I think they are, and thereby spot mistaken reinsertion.
* Assert that there is no overflow in files without a spare block.
* String length validation.

### cheats.py
* Get rid of this and make it a method of an EXEFile.
* Anything I can do with the creature stat values? Can I decrease them, for example, in a way that makes me evolve into a bipedal creature faster for testing ch5?

### length validation
* I don't think unit tests are a good way to check the translation integrity.
** I can probably write real unit tests, though, now that there's a more object oriented structure.
** And I can just use a normal script to find all the strings that need shortening.

* What is the best way to do editing for line lengths and such?
    * The simplest is that all strings definitely can't be over 76. (max for bottom narration)
        * All strings in SINKA.DAT and SEND.DAT must be below 68. (bottom narration - indent)
    * Strings in creature block < 21.
    * Strings in battle block < 43.
    * Strings in the menu block < 43. (Since evolution messages, etc.)

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
    * I really do need some version of the dump where I can see these control codes. At this point it may be worth it to write my own SJIS-Dump that 1) lacks the bug, and 2) can use a custom .tbl file.
    * table-dump. Y'know, like table flipping.
        * Uh this is pretty difficult. I think I will wait til I study some more string algorithms to know what I'm doing here.

### other
* Actually make a patch!
    * It'd be nice to generate a patch immediately during the reinsert process.
        * Look into Travis CI or whatever standard windows build tools there are.
    * Looks like the best option is floating ips, or flips. I can make a batch file to make multiple patches.
    	* Although that doesn't play well with the command line... hm...

* I wonder if the dump has grown more complicated and might need a database.
    * SQL queries insetad of loading the data from the xls sheet and manipulating it in memory.
    * DB validations instead of 'unit' tests.
    * Easier to categorize blocks a certain way, just have a 'block type' column.

* Remind myself what the "intermediate roms" folder is for.
	* It has an edited 46.EXE, so I don't need to change that every time. Anything else?
	* .DAT files are also pre-inserted in Intermediate.
		* This is dumb - it tries to re-do the changes it's already done, and fails silently! Better way?
    * If I put the patched images in the intermediate roms, will it break the reinsertion by changing file locations???

* Fix the randomly decaying excel formulas.
    * I am very incompetent at excel, it seems.

* What is the purpose of Disk B1? Does it contain anything not in Disk B2? Is it a part of gameplay at all?

* Can I insert brag text into the credits?
    * Probably quite difficult unless I take some poor developer out of the credits.

* Looks like the .gitignore is on the fritz...

### common problems and their solutions
* If a "&" appears before a string when it gets replaced:
    * There's probably an 81-40 sjis space in front of it. Add it to the JP part of the dump so it gets replaced.

* If something in the overflow text overflows into another string:
    * Make sure you split up the block of the first overflow string AFTER an <END> tag.

* If the reinserter can't find the original jp string:
    * Look in the dump that includes ASCII text, there's probably some wonky spaces or something.
    * Especially if it's in OPENING or ENDING.