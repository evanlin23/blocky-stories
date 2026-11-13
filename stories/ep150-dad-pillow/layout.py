"""Shared places for ep150 "my stepdad's pillow dreams of someone knocking" (make_story.py and set.py).
x east, y north, z up. A character facing -y has yaw 0, +x 90, +y 180, -x -90. Stages sit far apart so their lights
never mix:
  GUEST   Dad's guest room (origin): x -2.6..2.8, y -4.6..3.6, ceiling 2.7. Bed along the west wall, head north.
  HALL    Dad's front hall (60, 0): x 57.4..62.6, y -1.5..5.0, ceiling 3.2. The front door is in the north wall (x 60);
          stairs up the west side. It is lit as the waking hall (door open, sunny porch beyond) or as the dream
          (door shut, gold behind it) by the `mode` cue. The porch lies north of the door (y 5.4..9.5).
  MEM     the porch at sixteen (60, -60): the house wall at y 0..0.3, a shut door and a side window, a lit room behind.
  KITCH   the kitchen (120, 0): room y 0.3..4.6, a doorway in the south wall (x 120), a sunny hall corridor y -3..0.
  COUSIN  (-60, 0): a bedroom.   BUDDY (-60, 40): a living room with a big dog bed.
"""
# ---- guest room
GX0, GX1, GY0, GY1, GH = -2.6, 2.8, -4.6, 3.6, 2.7
BX = -1.4                       # bed centre line (x); mattress -1.88..-0.92, y 1.55..3.55, top at z 0.52
HEAD_Y = 3.15
LY_ROOT = (1.58, 0.69)          # lying body: feet y and root z (lean -84 puts the head at HEAD_Y, z 0.85)
ME_G = (0.6, -0.6)              # me standing, holding the pillow

# ---- hall
HX = 60.0
HX0, HX1, HY0, HY1, HH = 57.4, 62.6, -1.5, 5.0, 3.2
DOOR_W, DOOR_H = 1.2, 2.2
STEP_Y0, STEP_DY, STEP_DZ = 0.8, 0.4, 0.2
DAD_X = 58.25                   # Dad on the third stair
DAD_Y = 1.85
STAIR3 = 0.6                    # tread top of the third stair
ME_H = (HX, 3.1)                # me, mid-hall in the dream
PORCH_Y = 6.4

# ---- memory porch (evening)
MX = 60.0
MY = -60.0
# ---- kitchen
KX = 120.0
# ---- cousin and buddy
CX, CY = -60.0, 0.0
BDX, BDY = -60.0, 40.0
