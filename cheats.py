"""Cheats for making debugging easier."""

from rominfo import STARTING_MAP_NUMBER_LOCATION, file_location
from utils import DEST_ROM_PATH

def change_starting_map(gamefile, map_number):
    """Cheats! Load a different map instead of thelodus sea."""
    offset_in_rom = STARTING_MAP_NUMBER_LOCATION[gamefile] + file_location[gamefile]
    new_map_bytes = str(map_number).encode()
    with open(DEST_ROM_PATH, 'rb+') as f:
        f.seek(offset_in_rom)
        f.write(new_map_bytes)