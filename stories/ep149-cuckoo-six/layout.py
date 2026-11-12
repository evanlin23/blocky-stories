"""Places shared by set.py and generator/make_story.py (x east, y north; the camera looks north from the south).
A character facing -y (the camera) has yaw 0; yaw 90 faces east (+x)."""
H = 3.4                      # room height
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
CURT_X0, CURT_X1 = 1.0, 2.2  # the yellow curtain (B)
CURT_Y = 2.22                # its centre depth
IVY0 = (1.5, 2.62)       # Ivy behind it (her head stays 3 cm off the wall)
IVY_OUT = (0.0, 2.62)        # directly behind Grandpa, arms wide of his shoulders
IVY_HUG = IVY_OUT            # she hugs him from there (no second walk)
