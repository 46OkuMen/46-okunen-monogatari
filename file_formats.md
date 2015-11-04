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