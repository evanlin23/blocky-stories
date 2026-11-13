"""Places shared by set.py and generator/make_story.py (x east, y north; the camera looks north from the south).
A character facing -y (the camera) has yaw 0; yaw 90 faces east (+x)."""
H = 5.8                      # room height (tall walls: the dollhouse shots see no sky)
CURT_TOP = 3.0               # the curtain's rod height
CURT_BOT = 0.03              # its hem
UPPER = 3.5                  # the picture-rail height
WALL_N = 2.9                 # inside face of the north wall
ROOM_X = 2.9                 # side walls at +-2.9
ROOM_S = -7.0                # the (hidden) south wall
TABLE = (0.0, 0.85)          # a long table running north-south
TABLE_W, TABLE_D, TABLE_Z = 1.0, 1.8, 0.76
CAKE = (0.0, 1.4)
CLOCK_X, CLOCK_Z = 0.0, 2.35
SEAT = 0.42                  # a seated person is lowered by this
GRANDMA = (-1.0, 1.1)      # west side, turned toward us
MOM = (-1.0, 0.1)
GRANDPA = (0.0, 2.05)         # the head of the table, under the clock, on a stool
DAD = (1.0, 1.1)           # east side
ME = (1.0, 0.1)
ARM = (-2.45, 1.0)           # the red armchair (A): its back flush against the west wall, facing east
CLOSET_X = -1.9              # the hall closet's door (C)
CURT_X0, CURT_X1 = 1.5, 2.8  # the yellow curtain (B)
CURT_Y = 2.22                # its centre depth
IVY0 = (2.12, 2.6)      # Ivy behind it (toes poke out under the hem)
CHAIR6 = (0.0, -0.38)    # Ivy's empty sixth chair at the foot of the table, pulled in
IVY_OUT = (1.15, 2.45)        # where she stops after stepping out, facing us
IVY_HUG = (0.82, 2.42)
