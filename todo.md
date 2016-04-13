* Focus of hte moment: In pad_text_blocks(), sometimes it doesn't find the original_block_string in the patched file string.
** This came up once in ST1.EXE. Not sure how it went away, but it was some one byte being changed at some point. I'll look back in the git history to see what I did.
** In ST2, it happens in three places:
*** a few changes happen at a move-character-control-code section (easy; just exclude it from blocks).
*** One is at an 81-40 SJIS space (did that get changed to an ascii 20 somewhere?). 
*** One is somewhere completely inexplicable, like in the middle of some text.
** In ST3...?

* PEP8 stuff. Shiny new Pylint extension will annoy me into fixing a lot of it.
** Definitely look for ways to break up edit_text(). It's way too big now.
* See if get_translations() works for the .dat files. If so, we can get rid of get_dat_translations.
** If that's the case, I can probably separate the pointer-counting and text-editing parts of edit_text().
* Chapter 2 crashes on changing maps when stuff in the final dialogue block is changed. Break up the block.