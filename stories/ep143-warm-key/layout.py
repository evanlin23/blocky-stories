"""Shared places for ep143 "my old house key went warm" (make_story.py and set.py). x east, y north, z up.
A character facing -y has yaw 0, +x 90, +y 180, -x -90. Stages sit far apart so their lights never mix:
  APT     my apartment entry, origin (0, 0): x -3..3, y -2.6..3.5, ceiling 2.9. Hooks and the photo on the north wall.
  HILL    a sloped street at x 60, running north (+y) up to the old blue house at the top (plateau z = ZH).
  HOUSE   the old blue house: porch y 33.3..36, front wall y 36..36.3, the hall y 36.3..41.5, ceiling 2.7 over the hall floor.
  PIZZA   a front door at (-60, 4); GYM a locker row at (-60, 33.5); INSERT a door and lock close-up stage at (0, -60).
"""

# ---- apartment
AX0, AX1, AY0, AY1, AH = -3.0, 3.0, -2.6, 3.5, 2.9
HOOK = (-0.4, 3.38, 1.9)       # the key's hook
ME_A = (0.3, 2.35)              # me beside the hooks
PHOTO = (-1.55, 3.45, 1.45)
TABLE = (1.75, 2.75)
ME_T = (1.75, 3.2)               # me standing behind the hall table
PHONE = (1.75, 2.72, 0.80)

# ---- hill
HX = 60.0
SLOPE = 0.07
ZH = SLOPE * 30                  # the plateau under the house (2.1)


def road_z(y):
    return min(ZH, SLOPE * y)


HOUSE = (60.0, 36.0)             # door centre x, front wall's outer face y
ZP = ZH + 0.45                   # porch and hall floor
DOOR_W, DOOR_H = 1.3, 2.15
DOOR_X0 = HOUSE[0] - DOOR_W / 2  # hinge side (west)
HALL = (56.3, 63.7, 36.3, 41.5)  # x0 x1 y0 y1
HALL_H = 2.7
STICKER = (HOUSE[0] + 0.12, HOUSE[1], ZP + 1.3)

# ---- montage and inserts
PIZZA = (-60.0, 4.0)             # the door wall's face
BUDDY = (-60.0, 33.5)            # the locker wall's face
INS = (0.0, -60.0)               # the door insert wall's face (y)
