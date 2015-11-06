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
**02-01: Begin header?
**04-03: ?
**06-05: ?
**08-07: Image width (640 for titles, 416 for sad ends, 160 for maps
**10-9: Image height, scanlines subtracted (200 for titles, 143-144 for sad ends, 64 for map)
**12-11: End of header??

*Experiments with GAMEOVER.GDT
**at 0x119, there's 9 00s in a row - is this the divide between the two words, or a division between color planes?
**lots of instances of "00-41" or "00-47" or "00-46" throughout. 0xa0 (160) is like twice 0x46 (70), with a difference of 10, which is the (scanlined) maximum height of the letters...
***So those words are probably something like color-runlength.
**There are 22 instances of "10," which is the height of letters. How many maximal vertical lines exist in the image?
***1 (G), 6 (M), 5 (E), 5 (E), 5 (R) = 22 lines.
***It probably writes 10 blue, then fills in the interior with smaller colors later to make it white.
***What codes are doing this? 10-04, 10-06, ...
**The series of nine 00s (0x119-121) in the  middle is the separation between "GAME" and "OVER".
***Could 00 just be the end-of-column marker?
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
**80 at 0x58:
***0x89, adds 00000101 pixels in the 4th row.
***0x8F, adds 00001111 pixels in the 4th row.
***0xFF, breaks everything/adds lots of blue pixels and overflows a lot.