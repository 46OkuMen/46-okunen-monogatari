from utils import TYPESET_ROM_PATH

#RED_PLANET_OFFSET = 0x7d882

#GOLD_DRAGON_OFFSET = 0x3b346 # should be the offset after "the Devil's minions, at least...", and point to the first 0d0a afterwards

with open(TYPESET_ROM_PATH, 'r+b') as f:
	buffer = f.read()

	# Ch2 fixes
	red_planet_offset = buffer.find(b'red\n planet."  ')
	red_planet_offset += 0x0f
	f.seek(red_planet_offset, 0)
	f.write(b' ')

	distant_future_offset = buffer.find(b'\'In the distant future')
	distant_future_offset -= 2
	f.seek(distant_future_offset, 0)
	f.write(b' \n')

	# Fix mistakenly indented string
	fur_offset = buffer.find(b'"Fur?')
	fur_offset -= 3
	f.seek(fur_offset, 0)
	f.write(b'\x13\x0a\x00')

	# Overrwrite extraneous newline
	clockwise_offset = buffer.find(b'rotation."  ')
	clockwise_offset += 12 # yeah, decimal 12
	f.seek(clockwise_offset, 0)
	f.write(b' ')

	# Replace an <END> 'line break' with a space, to make the next line indent properly.
	#desolation_offset = buffer.find(b'beauty. The desolation')
	#desolation_offset += 0x16
	#f.seek(desolation_offset, 0)
	#f.write(b'\x0a')

	# Replace <WAIT><LN> with <LN><WAIT>.
	atlantis_army_offset = buffer.find(b' Atlantis army..."')
	atlantis_army_offset += 0x12
	f.seek(atlantis_army_offset, 0)
	f.write(b'\x0a\x13')

	# SEND.DAT fixes
	gold_dragon_offset = buffer.find(b'the Devil\'s minions')
	gold_dragon_offset += 0x22
	f.seek(gold_dragon_offset, 0)
	f.write(b'  ')

	green_dragon_offset = buffer.find(b'might stumble upon it.')
	green_dragon_offset += 0x16
	f.seek(green_dragon_offset, 0)
	f.write(b' \x0d\n')

	print hex(red_planet_offset), hex(distant_future_offset), hex(gold_dragon_offset), hex(green_dragon_offset)

	# replace ("stumble upon it...0d0a20" with "stumble upon it...200d0a")