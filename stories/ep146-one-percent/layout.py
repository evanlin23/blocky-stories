"""Shared places for ep146 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0,
facing +y has yaw 180. The jetty runs north-south at x 0 and ends at the houseboat's gangplank."""
DECK_Z = 0.5                       # the houseboat's deck above the dock top (z 0)
ME = (0.0, 0.9, 0.0)               # I stand at the gangplank's foot, facing north (yaw 180)
DEX = (0.0, 4.9, DECK_Z)           # Dex stands behind the rail's gate, facing south (yaw 0): 4.0 m from me
RAIL_Y = 4.2                       # the houseboat's south rail
ROOM = (100.0, 0.0)                # Grandma's living room (local x, y added to these)
GRANDMA = (ROOM[0] + 0.3, 2.6)
FLIP = (ROOM[0] - 0.95, 1.5, 0.74)
FLASH_ME = (-0.7, 5.5, DECK_Z)     # the bet on the deck, three years ago
FLASH_DEX = (0.7, 5.5, DECK_Z)
FLASH_GPA = (0.0, 6.7, DECK_Z)
RAILPH = (0.45, RAIL_Y - 0.03, DECK_Z + 1.34)   # Dex's phone propped upright on the rail top, to the right of his face (S01a)
