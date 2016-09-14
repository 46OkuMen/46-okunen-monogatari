# shank-a-rom
Romhacking notes and text dumping/reinserting utilities for *46 Okunen Monogatari: The Shinka Ron*, the 1990 Japan-only predecessor to *E.V.O: Search for Eden*. 

![screen from mid-Chapter 1, translated](https://raw.githubusercontent.com/hollowaytape/shank-a-rom/master/img/evidence_02.png)

## Reinsertion Progress:
| Segment      | %    | Strings      |
| -------------|-----:|:------------:|
| Opening      | 28%  |  (13 / 45)   |
| Chapter 1    |100%  | (501 / 501)  |
| Chapter 2    | 90%  | (391 / 434)  |
| Chapter 3    | 76%  | (257 / 338)  |
| Chapter 4    | 23%  | (172 / 746)  |
| Chapter 5    | 20%  | (186 / 892)  |
| Chapter 6    | 17%  |  (55 / 319)  |
| Ending       |  0%  |   (0 / 69)   |
| System       |100%  |   (5 / 5)    |
| Images       | 11%  |   (1 / 9)    |
| Encyclopedia | 48%  | (363 / 741)  |
| Gag Endings  |  0%  | (0 / 723)    |
| Total        | 40%  | (2119 / 5238)|

## How do I use this?
* There is a development IPS patch in the "patch" folder. It's not a release, it's just a proof-of-concept. and I don't recommend playing with it, other than to confirm for yourself "hey, this project really is getting somewhere!"
* Use LunarIPS (or whatever other IPS program you have) to patch your Disk A image.
* The patch targets these disk images:
	* 46 Okunen Monogatari - The Sinkaron (J) A user.FDI `md5: CA56B37F74885C40EDC9B1D2AACB5DA6`
	* 46 Okunen Monogatari - The Sinkaron (J) B 1.FDI `md5: EE852EC006ACD94C9CFB04B2505A51D7`
	* 46 Okunen Monogatari - The Sinkaron (J) B 2.FDI `md5: 3C1C0FBE1CF0A4C1B4574FFC26A490AB`
	* 46 Okunen Monogatari - The Sinkaron (J) B 3.FDI `md5: A3934EED652627ABB45A756F13EC531A`
	* 46 Okunen Monogatari - The Sinkaron (J) B 4.FDI `md5: 60E4D019F0CEF79C3D2EA3D44E6BF70E`
* Support is later planned for this hardware-compatible disk image:
	* 46okunenm.hdi `md5: 2B00A01944048980647FCE7ADEF07F57`
* If you want to use any of the utilities for yourself, I didn't really plan for that. Check back later when there are fewer hard-coded file paths. (You'll still need your own ROMs of course.)