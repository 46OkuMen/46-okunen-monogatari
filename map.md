# Disk A

## 46.EXE
* (0x93e8, 0x946d), (0x94b9, 0x971b), (0x9cb8, 0xa07a)
* 93F8-940E: Data allocation error.
* 9439-946C: COMON loading stuff
* 94BB-94F4: **"Please insert Disk B in Slot No. 2" error message**
* 9550-9559: "Cancel"?
* 9686-96AB: GEAGR driver loading stuff
* 96B1-96B8: **"Evolution Factor" stat**
* 96BE-971A: Buffer overflow, syntax error, not enough brackets
* 9CB6-9CD6: Graph LIO cannot be initialized
* 9D6E-A079: File error messages


## .GDT Files
* Images, animations...
* Appear in a SJIS editor as various single kanji separated by lots of garbage.

## COMMAND.COM
* Mostly DOS related error messages.
* 540-E60: Error descriptions.
* 2370-27FA: DOS error messages
* 9340-BE80: More error descriptions/system messages.

## GEAGRDRV.EXE

## INST.EXE
* Text appears to be mostly system related.

## MUSIC.COM
* 5553-5AA3: Probably different music settings related text?

## **OPENING.EXE**
* (0x4dd1, 0x5868)
* 4DDA-539A: Credits
* 53A9-555D: Scrolling intro text w/earth formation graphics
* 55E9-5638: MUSIC/GEAGR driver stuff, unlikely to be seen
* 5657-5868: Beginning static text, ENIX PRESENTS, then scrolling intro text
* Control codes:
** 00=<ln>

* Pointer Tables:
** 36-1fd: 114 pointers, sep: 68-04. Point to the table below.
** 4c51-4dbc: 114 pointers, sep: 68-04. Point to the text.
* 0x4bf7 (location pointed to, probably) - 0x177 (value of pointer) = 0x4b80
* Use the pointers that point to other pointers to determine the constant!
* Constant = 0x4b80.

## PC0-100.46

## **SEND.DAT**
* 0000-8740: Text from the bad endings/evolutionary dead ends.

## **SINKA.DAT**
* 29KB of plaintext encyclopedia text.
* Format: -XYZ (animal index?), 0D-0A, name, 0D-0A-09, height/size, 0D-0A-09, line 1, 0D-0A-09, line 2, 0D-0A-09, line 3, 0D-0A-0D-0A.
* Control codes:
** 0D-0A=<ln>
** 09=<tab>

## **ST1-STS1.EXE**
* Lots of dialogue, important game text

### ST1.EXE
* ((0xd873, 0xd933), (0xd984, 0x10f85), (0x10fca, 0x11595), (0x117c7, 0x119a3), (0x11d42, 0x1204e))
* System, dialog/battle, creatures, battle, errors
* 0d873-0d9cf: System, save file stuff, "EVO.P" stat
* 0d9d4-0e6e6: Dialogue
* 0e6fb-0ec5b: Battle text
* 0ec6c-0ed87: Menu, options
* 0edc7-10e1d: Dialogue
* 10e39-10f7a: Environmental narration, ???, "EVO.P" stat again
* 10fca-11560: Sea creature names (check in between them...)
* 117c7-117d5: Yes/No/Cancel
* 11839-1198f-ish: Battle text
* 11d40-1204d: Error messages

* Landmarks:
** edc7: First scene dialogue
** eb8f: fight menu options
** eca7: stats

* Pointer Tables:
** 53-0d: Add 0xd7e0.
** 00-00: (?)

** 00022-00031: (?) 4 pointers, 00-00.
** 00032-00081: 20 pointers, 5e-0d. Points to pointers in the menu options region, in reverse order.
** 00082-000a2: (?) 8 pointers, 00-00.
** 000a2-000d7: 13 pointers, 5e-0d. Point to the yes/no/cancel, etc. pointer locations below.
** 000d6-0014d: (?) 30 pointers, 00-00.
** 0014e-001e1: Points to the pointers of the error messages table. (they increment by 4 each time.) 5e-0d.
** 0d934-0d983: Menu options, some battle skills. Add 0xd7e0. 5e-0d.
** 10f96-10fc9: 13 pointers, 5e-od. Yes/No/Cancel, ascii numbers 1-6...
** 11cae-11d41: Error messages! Pointers point to their little-endian value + 0xd7e0. Sep: 5e-0d.

### ST2.EXE
* (0xc23b, 0xdd4f), (0xde35, 0xfaa0), (0xfae4, 0xfe50), (0x10004, 0x101df), (0x10570, 0x1087b)
* System, dialog/battle, creatures, battle, errors
* C23B-DD4E: Dialogue?
* DE34-FA9F: More dialogue
* FAE5-FE2C: Animal names?
* 10004-1001C: Yes/No/Cancel
* 100D4-101E1: Error messages?
* 10571-1087B: Error messages?

* Pointers:
* Separator: f7-0b
* Constant: 0xc170
* (0x104dcc, 0x1056f): Error message pointers. Sep: f7-0b.

### ST3.EXE
* (0xb49d, 0xb548), (0xb58a, 0xdb3a), (0xdb7e, 0xe2d5), (0xe617, 0xe7f3), (0xeb82, 0xee8e)
* System, dialog/battle, creatures, battle, errors

* Pointers:
* Separator: 20-0b
* Constant: 0xb400
* (0xeaee, 0xed81): Error message pointers. Sep: 20-0b.

### ST4.EXE
* (0xe262, 0xe29e), (0xe2f4, 0x120a0), (0x12114, 0x149e4), (0x14a28, 0x15a1e), (0x16031, 0x1620d), (0x1659c, 0x168a8) 
* System, dialog/battle 1, dialog/battle 2, creatures, battle, errors
* e263-ea3e: Battle

* Pointers:
* Separator: f4-0d
* Constant: 0xe140

### ST5.EXE
* (0xcc02, 0xcc5e), (0xccf2, 0xcd2e), (0xcd74, 0xeabe), (0xebc3, 0x107a3), (0x107e6, 0x11466), (0x11976, 0x11b53), (0x11ef2, 0x121fe)

* Pointers:
* Separator: 96-0c
* Constant: 0xcb60

### ST5S1.EXE
* (0x24e8, 0x3af1)
* (just one block - dialog/battle)

### ST5S2.EXE
* (0x23f9, 0x3797)

### ST5S3.EXE
* (0x3db9, 0x4ed0)

* Pointers:
* Separator: ae-03

### ST6.EXE
* (0xa4f1, 0xa55b), (0xa59c, 0xccd1), (0xcd14, 0xce25), (0xcede, 0xd0bb), (0xd44a, 0xd756)
* BBD0: **"OK! TAKE IT EASY!" text** (only English text I remembered seeing, clued me in to the presence of the other text)

* Pointers:
* Separator: 26-0a
* Constant: 0xa460

## **ENDING.EXE**
* (0x3c4e, 0x4b1f)
* 3C4e-440F: Credits
* 443B-4B1E: Ending text


# Disk B1-B4
* All other disks appear to just hold images and maps... no text.

# Etc
## Control Codes
* for ST1.EXE, etc.:
* 0A-13-0A-00=<wait><ln><ln>
* 13-0A-0A-00=<wait><ln><ln>
* 0A-13-00=<wait><ln><ln>
* 0A-0A-00=<wait>
* 0A-00=<ln><ln>, keep printing in same window without waiting
* 13-00: <wait>
* 13=<wait>
* 16-21: <new window>
* 16-22: <clear>
* 16-1E: <clear>
* 83-65: ?
* 81-40 or 81-41: just a space. used as a line break in some cases - so looks like line breaks themselves are handled in software
* 81-41-0A: Line break in the middle of a line

## Misc. Info
* Line length, dialogue: 22 characters
* Line length, battle:
* Line length, bottom narration: 
* Menu item length: 6 characters?
* Creature name: 10 characters?