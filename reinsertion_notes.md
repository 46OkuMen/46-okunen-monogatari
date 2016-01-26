### ST1.EXE
(0x00022, 0x00031): 4 pointers, 00-00. (?)
(0x00032, 0x00081): 20 pointers, 5e-0d. Pointer-pointers for menu options.
(0x00082, 0x000a1): 8 pointers, 00-00. (?)
(0x000a2, 0x000d7): 13 pointers, 5e-0d. Pointer-pointers for Y/N/Cancel/#s.
(0x000d8, 0x0014d): 30 pointers, 00-00. (?)
(0x0014e, 0x001e1): 5e-0d. Pointer-pointers for error messages.
(0x01584, 0x0d7e0): Dialogue pointers within functions. (very coarse)



(0x0d934, 0x0d983): 5e-0d. Menu options, battle skills.



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
* 11a10-11baf: (?) To investigate through corruption
**Little-endian numbers incrementing by decimal 14, in a sea of 00s?? Myserious.
* 11d40-1204d: Error messages

* Landmarks:
** edc7: First scene dialogue
** eb8f: fight menu options
** eca7: stats

* Pointer Tables:
** Separators:
*** 53-0d: Add 0xd7e0.
*** 00-00: (?)
** 00022-00031: (?) 4 pointers, 00-00.
** 00032-00081: 20 pointers, 5e-0d. Points to pointers in the menu options region, in reverse order.
** 00082-000a2: (?) 8 pointers, 00-00.
***[0x46ee, 0x46e7, 0x46c9, 0x46c2, 0x46a6, 0x469f, 0x4681, 0x467a]
***sorted, dec: [18042, 18049, 18079, 18086, 18114, 18121, 18151, 18158]
***diffs: [7, 30, 7, 28, 7 30, 7]
** 000a2-000d7: 13 pointers, 5e-0d. Point to the yes/no/cancel, etc. pointers below.
** 000d8-0014d: (?) 30 pointers, 00-00.
** 0014e-001e1: Points to pointers for error messages. 5e-0d.
** 0d934-0d983: Menu options, some battle skills. Add 0xd7e0. 5e-0d.
** 10f96-10fc9: 13 pointers, 5e-od. Yes/No/Cancel, ascii numbers 1-6...
** 11cae-11d41: Pointers for error messages. Sep: 5e-0d.

* Dialogue Pointers:
** Starting around offset 2000, there are dialogue pointers hard-coded into functions.
** They begin with 1E-B8 and end with a long string 50-FF-76-FE...
** First piece of dialogue calls the pointer 1206 (612) which is at 0x2232.
** 0xd7e0 + 612 = ddf2, which is where the text points.
** So, same constant as in the normal pointer tables.