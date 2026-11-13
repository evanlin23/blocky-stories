"""Shared places for ep154 "Dad's empty car leaves every dawn" (make_story.py and set.py). x east, y north, z up.
A character facing -y has yaw 0, +x 90, +y 180, -x -90. Stages sit far apart so their lights never mix, and each
has its own sky dome (set.py), so the beach can be noon and the memory gray while the rest is sunrise.

  HOME     our hilltop driveway (origin): the mint bungalow (front wall y = 10) with its white porch, the driveway
           east of it, Dad's teal hatchback and Mom's yellow one parked nose-out (facing south), the street at
           y -9 and the view falling away south to the fields.
  KITCHEN  our yellow kitchen at (0, 300): a round table, Mom and Dad across it, a ceiling.
  BEACH    Mr. Fenn's noon beach lot at (-300, 0): the sea north of y 12.
  HILL     the hill road at x 300, from the crest (y 70) down to a crossroads at y 0; the low stone wall on the
           west side of the road at the bottom, with a tree and wildflowers. The car stops at CAR_WALL.
  DINER    the cherry diner at (-300, 300), its gravel lot south of it.
  RAIN     last spring's rainy stretch of the hill road at (0, -300), running east-west.

The car (set.py build_car): front +y in its own frame, origin on the ground at its middle. A car's yaw is its
Blender turn about z: yaw 0 faces north, 180 south, 90 west (the opposite of a character's). Its seats are SEATS (local x, y, cushion top); a seated rider's root sits
at the cushion top + 0.17 - 0.68 h (the rig's hips are 0.68 h above the feet, and the legs, turned flat forward,
are 0.34 thick), and faces the car's front: yaw = car yaw + 180.
"""
import math

# ---- the car (local, front +y)
CAR_W, CAR_L = 2.6, 4.6
CUSH = 0.5                   # seat cushion top
SEATS = {"driver": (-0.72, 0.15), "pass": (0.72, 0.15), "pass_back": (0.72, -0.2),
         "rear_l": (-0.45, -1.25), "rear_r": (0.6, -1.25)}
MUFFIN_L = (0.32, 1.13, 1.25)   # the muffin's place on the dash top (local)


def rot(x, y, yaw):
    a = math.radians(yaw)
    return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)


def to_world(car, lx, ly, lz=0.0):
    """car = (x, y, z, yaw): a local point of the car in the world."""
    dx, dy = rot(lx, ly, car[3])
    return (round(car[0] + dx, 3), round(car[1] + dy, 3), round(car[2] + lz, 3))


def seat(car, name, h=1.0, sink=0.0):
    """Where a rider's root goes (x, y, z) and the yaw it faces, for the car pose car = (x, y, z, yaw)."""
    lx, ly = SEATS[name]
    p = to_world(car, lx, ly, CUSH + 0.17 - 0.68 * h - sink)
    return p, (car[3] + 180) % 360


# ---- home
HOUSE_Y = 10.0               # the bungalow's front wall
PORCH = (-5.0, 1.0, 7.5, 10.0)   # x0 x1 y0 y1, floor z PZ
PZ = 0.45
CAR_HOME = (5.0, 3.0, 0.0, 180.0)
MOM_HOME = (9.6, 3.0, 0.0, 180.0)
CAR_OUT = (5.0, -9.0, 0.0, 180.0)      # down at the street, where it leaves frame
DAD_PORCH = (-0.4, 8.6, PZ)
ME_WIN = (3.2, 2.9, 0.0)           # me outside the driver's window (S01a, S26)

# ---- kitchen
KX, KY = 0.0, 300.0
K_X0, K_X1, K_Y0, K_Y1, K_H = -3.6, 3.6, 295.0, 302.5, 2.8
TABLE = (0.0, 299.6)
TABLE_Z = 0.92
CHAIR_Z = 0.5
MOM_K = (-0.78, 299.75)
DAD_K = (0.78, 299.75)

# ---- beach
BX, BY = -300.0, 0.0
FENN_CAR = (-300.0, 5.0, 0.0, 0.0)    # facing north, the sea
BOSS_CAR = (-300.0, -0.2, 0.0, 0.0)
FENN = (-297.2, 9.2, 0.0)
BOSS = (-295.7, 9.2, 0.0)

# ---- hill
HX = 300.0
SLOPE = 0.07


def hill_z(y):
    return SLOPE * min(70.0, max(0.0, y))


CAR_WALL = (299.1, 0.0, 0.0, 180.0)
WALL_X = 296.0                     # the wall's middle line (it runs north-south)
COOK_WALL = (297.15, -0.6, 0.0)

# ---- diner
DX, DY = -300.0, 300.0
CAR_DINER = (-298.5, 298.0, 0.0, 90.0)   # facing west, its passenger side to the diner (north)
COOK_DINER = (-297.95, 300.05, 0.0)   # local (2.05, -0.55): clear of the open door

# ---- rain
RX, RY = 0.0, -300.0
RAIN_ROAD_Y = -300.0              # the road's middle
COOK_RAIN_Y = -303.4               # the south verge


def ground(x, y):
    """The ground under a car: the hill road's slope on the hill stage, flat everywhere else."""
    if abs(x - HX) < 100 and -100 < y < 100:
        return hill_z(y)
    return 0.0


# ---- S07a: through the kitchen window at the front of the house, on the driveway
KWIN_CAM = (1.7, 9.7, 1.75)
KWIN_TGT = (5.0, 1.5, 0.9)
KWIN_DIST = 1.3


def kwin_place():
    """Where the window frame hangs (centre) and its yaw, KWIN_DIST along the S07a camera's line of sight."""
    d = [KWIN_TGT[i] - KWIN_CAM[i] for i in range(3)]
    n = math.sqrt(sum(v * v for v in d))
    p = tuple(round(KWIN_CAM[i] + d[i] / n * KWIN_DIST, 3) for i in range(3))
    return p, math.degrees(math.atan2(-d[0], d[1]))
