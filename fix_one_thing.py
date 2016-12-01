from utils import TYPESET_ROM_PATH

RED_PLANET_OFFSET = 0x7d882
GOLD_DRAGON_OFFSET = 0x3b346 # should be the offset after "the Devil's minions, at least...", and point to the first 0d0a afterwards

with open(TYPESET_ROM_PATH, 'r+b') as f:
	f.seek(RED_PLANET_OFFSET, 0)
	f.write(b' ')

	f.seek(GOLD_DRAGON_OFFSET, 0)
	f.write(b'  ')

	# replace ("stumble upon it...0d0a20" with "stumble upon it...200d0a")