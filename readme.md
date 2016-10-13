# shank-a-rom
Romhacking notes and text dumping/reinserting utilities for *E.V.O.: The Theory of Evolution*, otherwise known as *46 Okunen Monogatari: The Shinkaron*, the 1990 Japan-only predecessor to *E.V.O: Search for Eden* for the SNES.

![screen from mid-Chapter 1, translated](https://raw.githubusercontent.com/hollowaytape/shank-a-rom/master/img/evidence_02.png)

## Draft Reinsertion Progress:
| Segment      | %    | Strings      |
| -------------|-----:|:------------:|
| Opening      |100%  |  (45 / 45)   |
| Chapter 1    |100%  | (501 / 501)  |
| Chapter 2    | 99%  | (430 / 434)  |
| Chapter 3    | 98%  | (334 / 338)  |
| Chapter 4    | 92%  | (689 / 747)  |
| Chapter 5    | 90%  | (806 / 892)  |
| Chapter 6    | 95%  | (305 / 319)  |
| Ending       |100%  |  (70 / 70)   |
| System       |100%  |   (5 / 5)    |
| Images       | 89%  |   (8 / 9)    |
| Encyclopedia |100%  | (935 / 935)  |
| Game Overs   |  3%  |  (25 / 729)  |
| Total        | 83%  |(4489 / 5373) |

## How do I use this?
* There is a development IPS patch in the "patch" folder. It's not a release, it's just a proof-of-concept. And I don't recommend playing with it, other than to confirm for yourself "hey, this project really is getting somewhere!" The game will almost certainly crash at some point!!
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