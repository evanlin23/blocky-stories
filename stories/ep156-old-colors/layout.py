"""Shared places for ep156 "Miss Your Old House, Turn Its COLORS" (make_story.py and set.py). x east, y north, z up.
A character facing -y has yaw 0, +x 90, +y 180, -x -90. Five stages sit far apart so their lights never mix:
  KIT     Mom's new kitchen at the origin: x -4.2..4.2, y -4.2..3.4, ceiling 2.9. Cabinets and the fridge on the north
          wall, a window on the west wall, a back door on the east wall, the table in the middle.
  PORCH   the old swing on a back porch at (-60, 0).
  PRATT   Mr. Pratt's porch over a low fence at (60, 0).
  STREET  two street examples at (0, 60): the bench at x 0, the plaid house at x 14.
  ROOM    my room at (60, 60): a bed against the north wall.
"""
AX0, AX1, AY0, AY1, AH = -4.2, 4.2, -4.2, 3.4, 2.9
TABLE = (0.0, 0.35)
TABLE_W, TABLE_D, TABLE_H = 0.7, 1.5, 0.76      # x and y extents: the long side runs north to south
LEO = (0.0, -0.4)               # my place at the table (facing north, yaw 180)
MOM = (0.0, 1.0)                # Mom's place (facing south, yaw 0)
FRIDGE = (2.2, 3.0)             # centre; its door faces south at y = FRIDGE[1] - 0.375
FRIDGE_FACE = FRIDGE[1] - 0.375
CAL = (2.45, FRIDGE_FACE - 0.02, 1.62)      # the calendar page on the door
PRINTS = [(1.95, 1.34), (2.05, 1.46), (1.88, 1.18)]      # x, z of the fingerprints on the door
WINDOW_Y = 0.3
DOOR_Y = -1.15                  # the back door on the east wall
PORCH = (-60.0, 0.0)
PRATT = (60.0, 0.0)
STREET = (0.0, 60.0)
ROOM = (60.0, 60.0)
