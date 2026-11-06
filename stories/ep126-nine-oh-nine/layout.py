"""Shared places for ep126 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0,
+x 90, +y 180, -x -90. Main street runs north-south (one block, y -36 to 0) and ends at the red feed store
(x -7..7, y 0..9, flat roof at ZR). The ladder is bolted up the store's back (north) wall."""

ZR = 6.2                       # the feed store's flat roof
LADDER_X = 2.6                 # the iron ladder on the back wall (y = 9)
ROOF_FACE_Y = 8.4              # where I stand at the ladder top
BUS = (200.0, 0.0)             # inside the bus (a far-off little set, roofed)
KITCHEN = (-200.0, 0.0)        # the kitchen memory (roofed)
ROAD = (300.0, 100.0)          # the dark road with the bus pulled over
CRATE = (-1.0, 5.4)            # centre of the old crate; the radio sits on its east end
RADIO = (-0.55, 5.4)
GRANDPA = (1.05, 5.4, 0.0)     # dancing: he faces south
GRANDMA = (1.5, 4.65, 180.0)   # and she faces north, over his shoulder
SIT_G = (-1.4, 5.4)            # where Grandma sits on the crate's west end
GP_STAND = (-2.3, 5.0)         # Grandpa beside her, facing south
ME_PARAPET = (3.45, 8.8)       # me, sitting on the north parapet from L28
CANE = (0.15, 8.62)
BOARD = (5.0, -3.2)            # the town notice board
STREET_DOORS = {}              # filled by set.py
