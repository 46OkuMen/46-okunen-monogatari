# Disk A

## 46.EXE
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

## **ENDING.EXE**
* 3C63-440F: Credits
* 443B-4B1E: Ending text

## GEAGRDRV.EXE

## INST.EXE
* Text appears to be mostly system related.

## MUSIC.COM
* 5553-5AA3: Probably different music settings related text?

## **OPENING.EXE**
* (0x4dda, 0x5868)
* 4DDA-539A: Credits
* 53A9-555D: Scrolling intro text w/earth formation graphics
* 55E9-5638: MUSIC/GEAGR driver stuff, unlikely to be seen
* 5657-5868: Beginning static text, ENIX PRESENTS, then scrolling intro text
* Control codes:
** 00=<ln>

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
* (0xd873, 11204d)
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
** 00032-00082: At top
** 000a2-000d7: Below that (check above and below for stuff separated by 00 00)
** 0d934-0d983: Above menu options & dialogue (though kinda small for dialogue...)
** 10f96-10fc9: Above the sea creature names
** 11ca0-11d41: Above the error messages

### ST2.EXE
* (0xc23b, 0x1085e)
* C23B-DD4E: Dialogue?
* DE34-FA9F: More dialogue
* FAE5-FE2C: Animal names?
* 10004-1001C: Yes/No/Cancel
* 100D4-101E1: Error messages?
* 10571-1087B: Error messages?

### ST3.EXE
* (0xb49d, 0xee70)

### ST4.EXE
* (e263, 1688a)
* e263-ea3e: Battle

### ST5S3.EXE
* In-battle text.

### ST6.EXE
* BBD0: **"OK! TAKE IT EASY!" text** (only English text I remembered seeing, clued me in to the presence of the other text)


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