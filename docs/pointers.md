# Pointers in 46 Okunen Monogatari #
In order to change the length of any individual string in the game without throwing the rest of the game out of alignment, you need to change pointers. Thus, finding every last pointer and changing them in precisely the right way is probably the largest part of the project.

Here's how they work, so you can skip all the reverse engineering and/or blind pawing that was performed on this game.

First, you need the pointer constant. There's one for each file. If "t" is the offset of beginning of the string "Turbo-C Copyright (c) 1988 Borland Intl" in the file, the pointer constant is `t % 16`. For example, in `ST1.EXE` it's `0xd7e0`.

Pointers come in two types: system pointers and dialogue pointers.

### System Pointers ###
These are the more obvious of the two - every ROMhacking tutorial says "look for a repeating, increasing sequence of bytes before a bunch of text." Yeah, 46 Okunen Monogatari has this kind of pointers.

System pointers live in tables with four-byte-long rows, the first two bytes being the pointer, and the second two bytes being another file-specific set of bytes. Here's a table at `ST1.EXE:0x10f96`:

`e7-3f-5e-0d`
`ec-3f-5e-0d`
`f3-3f-5e-0d`
`f5-3f-5e-0d`
`00-40-5e-0d`...

The pointer separator bytes ofr this file, `5e-0d`, don't appear to mean anything, they must be defined somewhere and looked for by the program.

The pointer itself is little-endian, since the PC-98 is on an x86 system. So to get the pointer's value, first reverse the two bytes and treat it as a single number:

`e7-3f -> 0x3fe7`

Then, add the file's pointer constant to this number:

` 0x3fe7
`+0xd7e0`
`-------`
`0x117c7`

Which is to a Japanese word for "Yes." It's right above the creature name block, so I was expecting something more exciting... but the tables don't always point where you expect them to.

The pointers don't always increase, which is annoying because I was looking for that.

If the pointer values are all increasing by 4, it's probably a table of pointer-pointers. As in the table exists only to point to the pointers of another table.

Also, there are a few tables in each file that appear to be system pointer tables, but they are separated with the bytes `00-00` instead of the pointer separators. I have learned not to mess with them - I think they point to functions or system things. Not totally sure how to use them, though.

Unfortunately these account for only about 16% of the text, and it's usually the more boring text like menu items, attack names, and the error messages (which will be deleted anyway to make room for overflow). The others are in...

### Dialogue Pointers ###
I had to ask for help on finding these - they're hiding pretty deep, hard-coded into the functions. The first 80% of each file or so looks like unstructured garbage in a hex editor, but it's full of these dialogue pointers. I assume various other things like timing, what pitch "scrolling noise" happens while the string is printing, etc. are controlled in the code adjacent to the pointers.

Anyway, each pointer announces itself with a prefix `1e-b8`, and usually ends with a suffix `50-ff`.

'Usually'? I ended up not including the `50-ff` in my regex to search for dialogue pointers. There are about 50 pointers (out of like 4,824) that don't have this suffix, for whatever reason. Weird.

Once you get the pointer value, you reverse the bytes and add the pointer constant as described above.