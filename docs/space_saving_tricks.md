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
* Expanding files!! This would be the hardest thing to do, maybe, but would solve all the problems. 
	* Compare file footers in the EXE files, as well as headers, to look for any information that hardcodes file length.
	* "Increase ROM size" appends FF to the end of the file.

## header format?
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

Seems like 02-04 is an important value for my purposes.
9101a8 - 0121a7 = 8fe001
8501d6 - 0109d5 = 8ef801
7801e8 - 00e5e7 = 771c01
b60002 - 016a01 = b49601
920158 - 12357  = 90de01

0191a8 - 0121a7 = 7001
0185d6 - 0109d5 = 7c01
0178e8 - 00e5e7 = 9301
00b602 - 16a01  =-b3ff (4c01?)
019258 - 12357 =  6f01

maybe the second value is more like a flag? don't include it in the value (explains the weird stuff with ST4)

121a7 - 91a8 = 8fff  st1  + d7e0 = 167df
109d5 - 85d6 = 83ff  st2  + c170 = 1456f
 e5e7 - 78e8 = 6cff  st3  + b400 = 120ff
16a01 - b602 = b3ff  st4  + e140 = 1953f
12357 - 9258 = 90ff  st5  + cb60 = 15c5f
3bbb - 1ebc =  1cff  st5s1+ 2440 =
3861 - 1d62 =  1aff  st5s2+ 2360 =
50ef - 29f0 =  26ff  st5s3+ 3ce0 =
d8af - 6db0 =  6aff  st6  + a460 =
5e4b - 304c =  2dff  op   + 4a80 =
4f55 - 2856 =  26ff  en   + 39a0 =


## ST1.EXE header
4d 5a a8 01 91 00 70 00 20 00 30 00 ff ff 1b 12 e6 00 00 00 00 00 00 00 22 00 00 00 01 00 fb 20 72 6a 01 00 00 00 45 0e 00 00 9d 0e 00 00 a4 0e 00 00 (pointer table)

final spaces thing: 120f4 - 12193
with expansion: 120f4 - 12193

rom size:121a6
with exp: 121a7, appends "FF" to end of ROM

right before the final pointer, there's 14 49 53 0d, which is a pointer to... the beginning of the spaces that immediately follow (12193 - 120f4 = 9f, or a0)
That's odd, the original rom header ends with 01 after the 99. That's a serious problem - am I slicing the files one byte too soon before I place them in the patched roms folder?

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