## .GDT
* Static images, animations

*Headers:
**BIGBOMB.GDT 88-E4-00-00-00-00-80-02-C8-00-11-06-E4-70-01-01 (??, 0x8e0) (big, animated)
**TITLE1.GDT: 88-E4-00-00-00-00-80-02-C8-00-11-00-00-00-00-00 (0x41, 0x699) (640x400)
**TITLE2.GDT: 88-E4-00-00-00-00-80-02-C8-00-11-00-00-00-00-00 (0x41, 0x74b) (640x400)
**TITLE3.GDT: 88-E4-00-00-00-00-80-02-C8-00-11-00-00-00-00-00 (0x41, 0x75e) (640x400)
**TITLE4.GDT: 88-E4-00-00-00-00-80-02-C8-00-11-00-00-00-00-00 (0x41, 0x588) (640x400)
**TITLE5.GDT: 88-E4-00-00-00-00-80-02-C8-00-11-00-00-00-00-00 (0x41, 0x792) (640x400)
**GAMEOVER.GDT88-E4-18-00-08-00-A0-01-90-00-11-00-00-00-00-00 (??, 0x205) (416x288)
**SEN04.GDT:  88-E4-18-00-09-00-A0-01-8F-00-11-03-FF-00-06-E8 (??, 0x19ca) (416x288)
**SEN09.GDT:  88-E4-18-00-08-00-A0-01-90-00-11-04-FF-57-C0-00 (??, 0x1289) (416x288)
**SEN10.GDT:  88-E4-18-00-08-00-A0-01-90-00-11-05-90-48-55-2A (??, 0x1266) (416x288)
**MAP100.GDT: 88-E4-C8-01-08-00-A0-00-40-00-11-04-FF-12-1F-07 (??, 0x23c) (160x128)
**MAP200.GDT: 88-E4-C8-01-08-00-A0-00-40-00-11-03-FF-00-06-E4 (??, 0x619) (160x128)
**MAP300.GDT: 88-E4-C8-01-08-00-A0-00-40-00-11-04-FF-14-FE-FC (??, 0x5f4) (160x128)
**MAP400.GDT: 88-E4-C8-01-08-00-A0-00-40-00-11-06-84-02-F8-FE (??, 0x6f0) (160x128)
**MAP500.GDT: 88-E4-C8-01-08-00-A0-00-40-00-11-04-FF-0B-FE-F6 (??, 0x879) (160x128)

*Legend:
**01-00: Begin header
**03-02: ?
**05-04: ?
**07-06: Image width (640 for titles, 416 for sad ends, 160 for maps
**09-08: Image height, scanlines subtracted (200 for titles, 143-144 for sad ends, 64 for map)
**11-10: End of header (11=length of header)

*Experiments with GAMEOVER.GDT
**at 0x119, there's 9 00s in a row - is this the divide between the two words, or a division between color planes?
**lots of instances of "00-41" or "00-47" or "00-46" throughout. 0xa0 (160) is like twice 0x46 (70), with a difference of 10, which is the (scanlined) maximum height of the letters...
***So those words are probably something like color-runlength.
**There are 22 instances of "10," which is the height of letters. How many maximal vertical lines exist in the image?
***1 (G), 6 (M), 5 (E), 5 (E), 5 (R) = 22 lines.
***It probably writes 10 blue, then fills in the interior with smaller colors later to make it white.
***What codes are doing this? 10-04, 10-06, ...
**The series of nine 00s (0x119-121) in the  middle is the separation between "GAME" and "OVER".
**Game seems to handle graphics in 8-pixel-wide columns, starting at the top and working downward.
***Cleanest thing I've gotten so far is shaving off the right 3 columns of the "R". Now it ends in a 10. What happens if I cut up to the next 10?
***Next cut takes away 8 pixels (middle of the "R")
***Next cut takes away 8 pixels (middle of the "E")
**Most of the above is wrong. The height of the images is 0x90 (144), or 0x48 with scanlines so that rules out the theory about black... Plus, it seems to work by rows??

**Just in the G. Final 0x10:
***0x00: Everything white turns pink.
***0x01: Everything white turns pink.
***0x20: Everything white turns pink.
***0x08: Blue borders turn turqouise.
***0x09: Blue borders turn turqouise.
***0x0C: Blue borders turn turquoise. (Green glitches at top.)
***0x07: 8column turns black.
***0x0F: 8column turns black.
***0x10: Normal. (Baseline)
***0x11: Normal.
***0x12: Normal.
***0x06, breaks everything (green bullets)
***0x0E: breaks everything (green bullets)
***0x05, REALLY breaks everything. (G ghosting, weird white background at bottom)
***0x15, REALLY breaks everything.
**41 at 0x54:
***0x31, breaks everything, ghosts everything into 3 parts.
**0x43, pushes the blue stuff down a little bit.
**0x4C,
**7F at 0x55: 
***0x70, 1st row becomes 01110000. 
**FF at 0x56:
***0x0F, 3rd row becomes 00000010. (leftmost white becomes pink-ish. 2nd row half becomes pink-ish.)
**02 at 0x57:
***0x03, stretches out all the 2-tall blue lines into 3-tall blue lines.
***0x04, stretches out all the 2-tall blue lines into 4-tall blue lines.
**80 at 0x58:
***0x10: adds 00010000 pixels in the 4th row.
***0x20, adds 00100000 pixels in the 4th row.
***0x41, adds 10000001 pixels in the 4th row.
***0x89, adds 10000101 pixels in the 4th row.
***0x8F, adds 10001111 pixels in the 4th row.
***0xA0, adds 10100000 pixels in the 4th row.
***0xFF, breaks everything/adds lots of blue pixels and overflows a lot.
***Ok, so it looks like this byte is the bitmap of a particular row.
***81 at 0x60:
***0x71, weird orange dome at right side (instead of white anywhere)
**To summarize 53-5F:
***The image begins 66 lines down (not including scanlines), or 0x42. 
***00-41 at the beginning prints 0x41 lines with no blue pixels.
***7f: 01111111. Each line, in binary, is a bitmap of an eight-pixel row.
***ff-02: When a line is followed by a small integer (how small?), that's the run-length of the last row.
***00-45 at the end... 0x45 more black rows before the end?

0x3b-0x46
04: 00000011 (?? - possibly the start of the new color?)
00-42, black at top (up to 1st line)
07: 00000111 (2nd row blue)
0f: 00001111 (3rd row, BWWW)
ff-84: repeat next line 4 times
1f: 00011111 (rows 4, 5, 6, 7, BWWWW)
0f: 00001111 (8th row, BWWW)
07: 00000111 (9th row, blue)
00-46, black at bottom

0x47-0x50
04 (start of next color?)
00-43, black at top (up to 2nd line)
07: 00000111 (the white part of the 3rd line)
ff-84: repeat next line 4 times
0f: 00001111 (white part of rows 4, 5, 6, 7)
07: 00000111 (white part of 8th row)
00-47: black at bottom

10: end-of-block?

0x52-5f:
04: start of new color? (or maybe a code telling it to use positional encoding?)
00-41: black at top
7f: 01111111 (top row)
ff: 11111111 (2nd row)
02: run length of previous line
80: 10000000 (4th row)
8f: 10001111 (5th row)
9f: 10011111 (6th row)
8f: 10001111 (7th row)
ff: 11111111 (8th row)
03: run length of previous line
00-45: black at bottom

0x60-0x6d:
81: positional encoding?
42: position of next line
ff: 11111111 (2nd row, all white)
43: position of next line
80: 10000000 (white part of 3rd row)
46: position of next line
0f: 00001111 (white part of the 6th row)
48: position of next line
80: 10000000 (white part of 8th row)
49: position of next line
ff: 11111111 (white part of 9th row)
ff: ??
ff: ????? (does this have something to do with the color? it is white, after all)

10: end-of-block

0x6e-0x7b
04: run-length
00-41: 41 black lines
c0: 11000000 (1st row, blue)
e1: 11100001 (2nd row, WWB   B)
c3: 11000011 (3rd row, blue)
07: 00000111 (4th row, BWW)
cf: 11001111 (5th row, BB BWWW)
ff-84: (???) same weird thing as above
ef: 11101111 (rows 6, 7, 8, 9)
cf: 11001111 (10th row)
00-45: end black lines

0x7c-
04: run-length
00-42: 42 black lines (including 1st row)
c0: 11000000 (white part of 2nd row)
01: 00000001 (white part of 3rd row)
03: 00000011 (white part of 4th row)
07: 00000111 (white part of 5th row)
ff-84: repeat next line 4 times
c7: 11000111 (white part of rows 6, 8, 8, 9)
00-46: end black lines

10: end-of-block


*Hypothesis: ff-84 means "repeat next line 4 times." Seems consistent for 3 cases so far.

So there are 48 00's at the very beginning. How many columns are black before the G? How many full 8-column blocks are black?
*132 black columns at the start. 132 / 8 = 16 r4. (the G begins halfway into the 17th block)
*Hypothesis: 00-00-00 = a totally black block. Check this against the other black section: 9 00's. 3 blocks in between? Looks like 30 pixels, so yes.