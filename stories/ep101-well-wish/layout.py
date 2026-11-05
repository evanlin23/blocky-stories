"""Shared places for ep101 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0
(yaw 90 faces +x, 180 faces +y, -90 faces -x). Every place is its own island, far from the others."""
SQ = (0.0, 0.0)            # the town square: the well is at its centre, the bakery wall on the +y side
ST = (100.0, 0.0)          # our street: runs north-south, houses on both sides, our house on the west corner
HB = (200.0, 0.0)          # Mr. Hobb's corner (a second street) with the bus
KP = (300.0, 0.0)          # Mrs. Kemp's snowy street
LR = (400.0, 0.0)          # our living room, stairs on the +y wall
WR = (440.0, 0.0)          # Wes's room (door on the -x wall)
HL = (431.6, 0.0)          # the hall outside Wes's door
KT = (480.0, 0.0)          # the kitchen
BI = (520.0, 0.0)          # inside the bus
HW = (560.0, 0.0)          # the highway at sunrise (a windshield view)
MT = (600.0, 0.0)          # the big meter tag for the close-ups
LP = (640.0, 0.0)          # the laptop map
BLOCK = 14.0               # one block is the distance to the stop sign
LANE_X = ST[0] - 1.5       # the west lane
STOP_Y = ST[1] - 14.0      # the stop sign
LINE_Y = ST[1] - 60.0      # the town-line post
WELL_Z = 0.9               # the well wall's top
