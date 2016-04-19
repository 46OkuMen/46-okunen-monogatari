* Focus of hte moment: In pad_text_blocks(), sometimes it doesn't find the original_block_string in the patched file string.
** This came up once in ST1.EXE. Not sure how it went away, but it was some one byte being changed at some point. I'll look back in the git history to see what I did.
** In ST2, it happens in three places:
*** a few changes happen at a move-character-control-code section (easy; just exclude it from blocks).
*** One is at an 81-40 SJIS space (did that get changed to an ascii 20 somewhere?). 
*** (c8be) One is near an 81-40 SJIS space, but a few later. 81-40-91-81 gets changed to 81-40-91-91...
**** This one gets edited right after 0xd9b0 text, 0x4b0a pointer gets edited. What???
**** So at 0x4ab7, the replacement is 1818 -> 1918. But it's getting replaced here instead.
*** (d561) One is somewhere inexplicable: 82-DC-82-DC-91-A7 gets changed to 82-DC-82-DC-A1-A7...
**** This gets changed after text 0xd9b0, pointer 0x52ad is edited... what?
**** So at 0x52ad, the replacement is c91a -> ca1a. But it's replacing this at 0xd561 instead of 0x52ad.
*** So, random incrementing by 0x10? Why is that?
**** Just a coincidence...

* So, a few contributions to the pointer-editing-OOB problem above:
** Some strings in the dump, when they're substrings of previous strings, return the previous string's offset.
*** Wrote a new util, fix_order.py that finds these and tells me to fix them manuallly. (~3 per file)
** If the same pointer gets edited twice, it still looks for the old pointer value the second time, so it doesn't find it and it tries to edit something that's in the text, which makes pad_text_blocks() fail.
*** I write to the pointer location directly without looking for its current value. Risky? Probably. I'll write a checker too.

* PEP8 stuff. Shiny new Pylint extension will annoy me into fixing a lot of it.
** Definitely look for ways to break up edit_text(). It's way too big now.
* See if get_translations() works for the .dat files. If so, we can get rid of get_dat_translations.
** If that's the case, I can probably separate the pointer-counting and text-editing parts of edit_text().
* Chapter 2 crashes on changing maps when stuff in the final dialogue block is changed. Break up the block.