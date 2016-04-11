* Handling overflow text.
** Grab each overflow_bytestring from last known pointer. That's a problem with all 3 strings found so far.
** Figure out why they are not being adjusted with the proper pointer edits.
** Think about giving the pointers an absolute value rahter than one calculated from a diff. That would save errors coming from its being editd twice.
** Figure out why there are duplicate "Got %u EVO Genes!" instances.
* PEP8 stuff. Shiny new Pylint extension will annoy me into fixing a lot of it.
** Definitely look for ways to break up edit_text(). It's way too big now.
* See if get_translations() works for the .dat files. If so, we can get rid of get_dat_translations.
** If that's the case, I can probably separate the pointer-counting and text-editing parts of edit_text().
* Chapter 2 crashes on changing maps when stuff in the final dialogue block is changed. Break up the block.