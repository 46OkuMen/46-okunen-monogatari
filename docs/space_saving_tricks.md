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
	* Impact: Allows full utilization of the 780 characters in the error block, which was underutilized by 200-300 characters in ST2 and St3.

* Removing Shift-JIS spaces that indent text.
	* Impact: Varies pretty widely, still calculating.
	* This is sometimes the only thing I can do to get space in OPENING.EXE and ENDING.EXE, which have no spare block.

* Removing error messages in the menu text block.
	* Impact: 13-26 more characters per file.

## Other things I might try
* Using a "second spare block" (159 characters) right before the footer.
	* I must have tried this before, did this give me graphical glitches? It seems fine so far in Ch2.
* ~~Rewriting the spare-block pointer table, which immediately precedes it.~~
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
* Allowing truly "blank" translations instead of the one space I use for them currently.
	* Really scraping the bottom of the barrel.
* NightWolve's recommendation - implementing a space text compressor/decompressor in the main text routine.

* Expanding files!! This would be the hardest thing to do, maybe, but would solve all the problems. 
	* Compare file footers in the EXE files, as well as headers, to look for any information that hardcodes file length.
	* "Increase ROM size" appends FF to the end of the file.
	* Looks like I an expand the ROM without any problems, but pointing stuff to the expanded space might not work...?
		* Does that extra space get loaded into the game?
			* Yep, "Hello World" appears to be in the game's memory at address 00013a50.
			* But that's separate from the rest of the ST1.EXE contents, which shows up around 0004100.
				* ...and it gets overwritten as soon as the dialogue is over.
				* What else is in this separate earlier block?
				* The entire footer, plus some of the error block? (138f5 - 138a8 = 4d) last spaces of it.
				* The total amount of room made: 13ca8 - 138a8 = 0x200 = 512, or one page.
				* The rest of the spaces are with the rest of the file. Spaces: (444ed - 0x4432d = 1c0 spaces)
					* The game file has: 1204d - 11e8d = 1c0. All spaces accounted for.
					* So why is it split up there?
				* !!The footer shows up in two locations - that place around 13a50, and alo at 0x44640, with the rest of the text. But it has some garbage after it instead of the text I write...!!
				* Actually it's not the split that matters; I can point to stuff at the end of the error block and it shows up just fine. It's just anything beyond that final 18-byte footer...
					* I can totally insert stuff in that last block of 20's, too. Cool.
					* Any way I can move that footer?
						* Are there any pointers to it?
						* Need to look for pointers that have values between b4 49 and c8 49.
							* 0x02c5: c849
							* 0x02d1: b649
							* 00x2e3: ba49
							* 0x02dd: c649
							* 0x030b: b849
							* 0x0b65: c849
							* 0x0b97: c849
							* 0x0ba2: c849
							* 0x3c90: be49
							* 0x88cf: b449
							* 0xa880: bc49
							* 0xaa09: bc49
							* 0xaecd: be49
						
						* Some of these are clearly unrelated. Bad side effects of adjusting all of them:
							* Controls do unexpected things & can't move very far.
							* Crash when trying to load an image in combat.
						* Seems like the real limit is the c849 value, so look at just those:
							* 0x02c5: c849 - edit this, and "Hallo World" gets addressed to "Has6'"????
							* 0x0b65: c849
							* 0x0b97: c849
							* 0x0ba2: c849

					* Debugging: Look at code that looks at addresses 13a3c thru 13a4f.


			* Maybe the code at the end of the file splits it up right before the last mass of 20s?
				* Only two pointers to stuff beyond error block: 0x001de points to 0x120f2, and 0x120f0 points to 0x120f4.
		* Can I fiddle with that header value any?
		* Or should I move the footer somewhere else?
		* Is there anything in 46.EXE that tells it how much to load each file?
			* 0xfa02: pointer value pointing to ST1.EXE
				* 0x59d (doubtful)
				* 0xa07, 0xa0c (probable)

## header format?
It's a standard DOS header format ("MZ").

00-01: 4d 5a (constant)
02-04: a8 01 91,    <- does this resemble 121a7?
       d6 01 85,    <- does this resemble 109d5?
       e8 01 78,    <- does this resemble 0e5e7?
       02 00 b6,    <- does this resemble 16a01? 
       58 01 92     <- does this resemble 12357?
       bc 01 1e     (ST5S1)                3bbb
       62 00 1d     (ST5S2)                3861
       f0 00 29     (ST5S3)                50ef
       b0 00 6d     (ST6)                  d8af
       4c 00 30     (OPENING)              5e4b
       56 01 28     (ENDING)               4f55

05-0b: 00 70 00 20 00 30 00,
       00 71 00 20 00 25 00,
       00 75 00 20 00 25 00,
       00 77 00 20 00 25 00,
       00 74 00 20 00 30 00
0c-0d: ff ff (constant)
0e-0f: 1b 12,
       93 10,
       f4 0e,
       96 16,
       36 12
10-25: e6 00 00 00 00 00 00 00 22 00 00 00 01 00 fb 20 72 6a 01 00 00 00
26

4d5a = signature.
next word: last page size.
third word: number of pages.


## ST1.EXE header
4d 5a a8 01 91 00 70 00 20 00 30 00 ff ff 1b 12 e6 00 00 00 00 00 00 00 22 00 00 00 01 00 fb 20 72 6a 01 00 00 00 45 0e 00 00 9d 0e 00 00 a4 0e 00 00 (pointer table)

last page size: 0x01a8
file pages: 0x91
relocation items: 0x70
header paragraphs: 0x20 (16 byte blocks - yep, everything until 0x200 is just headers/pointers)
MINALLOC: 0x30 (paragraphs)
MAXALLOC: 0xffff
Initial SS Value: 0x121b
Initial SP Value: 0x00e6
Complemented Checksum: 0x0000 (probably unused)
Initial IP Value: 0x0000
Prelocated CS Value: 0x0000
Relocation Table Offset: 0x0022
Overlay Number: 0x0000


final spaces thing: 120f4 - 12193
with expansion: 120f4 - 12193

rom size:121a6
with exp: 121a7, appends "FF" to end of ROM

right before the final pointer, there's 14 49 53 0d, which is a pointer to... the beginning of the spaces that immediately follow (12193 - 120f4 = 9f, or a0)
That's odd, the original rom header ends with 01 after the 99. That's a serious problem - am I slicing the files one byte too soon before I place them in the patched roms folder?
* Fixed that.

final footer:
00 00 90 01 90 01 97 01 98 01 56 ab 5b ab 5b ab 5b ab 99 01

Important values: 
5e 0d (pointer separator)
d7 e0 (pointer constant)
0x121a7 (file length)
49 c7 (file length - pointer constant)
* 49c7 occurs at 0x37d9 in the middle of file code.
* c749 does not occur.


## ST2.EXE header
4d 5a d6 01 85 00 71 00 20 00 25 00 ff ff 93 10 e6 00 00 00 00 00 00 00 22 00 00 00 01 00 fb 20 72 6a 01 00 00 00 36 10 00 00 3d 10 00 00 c1 15 00 00 (pointer table)

final footer:

00 00 90 01 90 01 97 01 98 01 e6 a4 eb a4 eb a4 eb a4 99

Important values:

f7 0b (pointer sep)
c1 70 (pointer const)
0x109d5 (file length)
4c 25 (file length - pointer constant)

## ST3.EXE header
4d 5a e8 01 78 00 75 00 20 00 25 00 ff ff f4 0e e6 00 00 00 00 00 00 00 22 00 00 00 01 00 fb 20 72 6a 01 00 00 00 2a 0d 00 00 ca 0f 00 00 d1 0f 00 00 20 10 00 00 27 10 00 00 (pointer table)

## ST4.EXE header
4d 5a 02 00 b6 00 77 00 20 00 25 00 ff ff 96 16 e6 00 00 00 00 00 00 00 22 00 00 00 01 00 fb 20 72 6a 01 00 00 00 0c 0f 00 00 38 11 00 00 3f 11 00 00 97 11 00 00 9e 11 00 00 (pointer table)

## ST5.EXE header
4d 5a 58 01 92 00 74 00 20 00 30 00 ff ff 36 12 e6 00 00 00 00 00 00 00 22 00 00 00 01 00 fb 20 72 6a 01 00 00 00 00 0f 00 00 ef 10 00 00 f6 10 00 00 45 11 00 00 4c 11 00 00 (pointer table)