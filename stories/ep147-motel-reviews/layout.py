"""Shared places for ep147 "Room Six" (make_story.py and set.py). x east, y north, z up. Front is -y (yaw 0).
Three stages far apart so their lights never mix:
  ROOM    Room Six at the origin: x -3..4.2, y -8..2.5, ceiling 3.0. The back wall (y 2.5) holds the desk with a window
          over it (x -0.7) and the closet (opening x 1.15..2.55, cavity to y 3.9). Beds along the west wall; the door
          is on the east wall (y 0.8..1.7). No south wall in the shots: the camera stands inside it.
  EXT     the motel row at x 60: a long wall at y 6 with mint doors, a canopy, a patio with the bucket pool.
  OFFICE  the office at x -60: a counter at y 1.2, the clerk behind it, the key board on the back wall.
"""
RX0, RX1, RY0, RY1, RH = -3.0, 4.2, -8.0, 2.5, 3.0
DESK = (-0.7, 1.95)          # desk centre x, front-edge y (0.55 deep, against the back wall)
DESK_TOP = 0.85
DESK_W = 1.5
WIN = (-0.7, 1.85)           # window centre x, z
CL0, CL1, CLH, CLY = 1.15, 2.55, 2.7, 3.9   # closet opening x range, height, back panel y
CLX = (CL0 + CL1) / 2
MAN = (CLX, 3.1)             # the closet man's spot
MAN_DESK = (-0.7, 1.7)
DOOR = (4.2, 1.25)           # east-wall door (x, y centre)
ME_C = (1.0, -0.9)           # me, the card shots
DAD_C = (-0.7, -1.0)

EX = 60.0
EXT_WALL_Y = 6.0
EXT_WALK_Y = 4.4             # where people stand
EXT_DOOR_X = 60.0
EXT_POOL = (66.5, 4.3)

OX, OY = -60.0, 0.0
CNT_Y = 1.2
CLERK = (-60.5, 2.0)
BELL = (-60.0, 1.45)
BOARD = (-58.0, 3.0)
