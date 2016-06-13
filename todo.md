## Crashes
* Crash upon leaving austrolepithecus village in ch5.
    * Mistaken text replacement? One of the choices you select is filled in and the other is not...

* Menu crash in ch5 has returned.
    * Looks like something is beting treated as overflowing when it shouldn't be...?
    * Ah. Gotta end every block AFTER an <END> tag, not on the first one.
    * It would be useful to have a test that sees if any file has overflow when it's passed a blank translation sheet...

## Mistaken Text Replacement
* Lots of pointer oddities/mistaken replacement in ch5...
    * Pliopithecus 2nd dialogue, "Ancient Mammoth" nametag instead rewrites a mention of it in dialogue...

* One cause of mistaken text replacement is when the string appears twice after the last translated text - of course it'll translate the first one it finds after the last translated thing, regardless of whether it's in dialogue or whatever.
    * Maybe I'll use something else instead of last_replacement_offset in the reinserter.

## Non-Crash Glitches
* OPENING.EXE isn't very happy after the refactoring... wonder what went wrong?

## Dump Problems
* Why are SINKA.DAT and SEND.DAT offsets still wrong? And why aren't the files in the dump at all??

* Carnivorous Dino Person has a missing piece of dialogue between 0xcf16 and 0xcf64.
    * Same as below. Used sjis-dump to dump st5 again...
    * Should I be nervous whenever I see two nametags in a row?

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

* Why isn't "Escape" getting translated in 5-S3?
    * It is; there are some weird ASCII spaces at the end of "Fight" and "Special" though in the original japanese...?
    * Ooh, looks like one of my old tricks is backfiring - it truly is an ASCII space (20) and my script is replacing all those with SJIS spaces, so it can't find it in the original text.
    * How about if I just add a space to the end of the english?
        * Uh, that just adds another space to the one that's there...
    * Hm. I fixed the space problem but I think this is something else - mistaken text replacement?
        * Some battle message gets repeatedly messed up. It involves the kanji for "power".
            * I removed the translations of "enemy"; no artifacts this time.
    * Some problem with the latter half of the skills block?
    * Remove everything in the block before the first "escape": menu item becoems "pe"
        * Remove the space in the jp text: remains "pe"
    * Hey, so this is the second "Escape" that's the issue.
        * Or maybe it's the first, and mistaken text replacement makes it hard to spot....
    * I think I can solve this by spacing the first several things cleverly...
    	* Yeah. This is really the best option.

* Any way to reposition the stats? Like add a few spaces to the left of DEF and HP?
    * Just spaces seems to have no effect. Look in the ROM and see if the spaces are there...
    * Oh, actually this works fine. DEF looks good, HP could use another space but there's no room.
        * Can I subtract a space from the preivous stat?
            * Yes.
    * Check to see if larger INT values run into the stat name later.

* Also, any way to get an extra character in "TextSpeed:"? There's gotta be something I can rearrange.
    * Looks like the message box size is fixed! The numnber appears as the last two characters of the box, overwriting whatever's there...
    * ...But in ST2 I was able to add an SJIS space before it! That gives me room.

## Tools

### reinsert.py
* Allow a manual line break in english text: <LN> becomes the byte 0A, or whatever.
    * This is tricky with length stuff, I think - the ln is only one character, so make sure the diff is still calculated correctly.

* Better progress reporting.
    * Separate the reporting into a different function. Build a dict of file, progress and process it in a function.

### cheats.py

### length validation
* What is the best way to do editing for line lengths and such?
    * The simplest is that all strings definitely can't be over 76. (max for bottom narration)
        * All strings in SINKA.DAT and SEND.DAT must be below 68. (bottom narration - indent)
    * Strings in creature block < 21.
    * Strings in battle block < 43.
    * Strings in the menu block < 43. (Since evolution messages, etc.)

* Is there any way to programmatically check which strings are part of fullscreen narration events?
    * One clue: it comes right after an AV        *.GDT file (in the full dump).
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

* Fix the randomly decaying excel formulas.
    * I am very incompetent at excel, it seems.

* What is the purpose of Disk B1? Does it contain anything not in Disk B2? Is it a part of gameplay at all?

* Can I insert the team name into the credits? 
    * Probably quite difficult unless I take some guy out of the credits.

### common problems and their solutions
* If a "&" appears before a string when it gets replaced:
    * There's probably an 81-40 sjis space in front of it. Add it to the JP part of the dump so it gets replaced.

* If something in the overflow text overflows into another string:
    * Make sure you split up the block of the first overflow string AFTER an <END> tag.

* If the reinserter can't find the original jp string:
    * Look in the dump that includes ASCII text, there's probably some wonky spaces or something.
    * Especially if it's in OPENING or ENDING.