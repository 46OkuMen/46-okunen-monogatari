## Space Saving Tricks
* English is almost always longer than Japanese, so

## Tricks
* Using ASCII encoding instead of Shift-JIS.
	* Impact: Massive. Halves the required space for the game script.
	* This one's a no-brainer - it looks better than the vaporwave-ish spaced-apart Shift-JIS Roman characters, and it's natively supported by the PC-98, so it requires no effort at all.
* Using the error block as an overflow container.
	* Impact: Provides 780 more characters of space per file.
	* The error messages in this block only show up during a fatal crash, and they usually don't help. With my optimism, I blanked the entire error block in every file so I can reroute the pointers of strings that overflow from their blocks.
* Using the end-of-block padding as overflow containers.
	* Impact: Varies widely. 250 more characters in ST2.EXE, 280 in ST3.EXE.
* Removing the Shift-JIS spaces that serve to center text in credits and CG sequences.
	* Impact: Provides 8-10 more characters per centered string, but removes the emphatic effect.
	* This is sometimes the only thing I can do to get space in OPENING.EXE and ENDING.EXE, which have no spare block.

## Other things I might try
* Rewriting the spare-block pointer table, which immediately precedes it.
	* Yeah that definitely doesn't work. The game boots but it corrupts particular bits of text...
		* Not even bits of text that get moved to that location, either. I wonder what's going on?
	* Maybe I should rewrite the pointer-pointers too??
* ~~Using the Borland compiler message as a spare block.~~
	* Changed it to "Barland", now the chapter won't boot.
	* Changed one character of "Abnormal program termination." as well, also won't boot.
* Eliminating duplicate strings ("Got $d EVO Genes.")
* Using tab characters to indent stuff rather than the 4-5 SJIS spaces.
	* Not as easy to insert in Excel as newlines...
	* \t just shows up ingame as a yen symbol. Maybe it's something else?
* Removing the error messages within normal text blocks. (Sometimes causes the game to not boot.)
* Removing the indentation after a line break in normal lines of dialogue.
	* Gotta look for the bytes 0A-81-40 in what pointer-peek finds.