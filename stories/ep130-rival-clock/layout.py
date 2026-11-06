"""Shared places for ep130-rival-clock (make_story.py and set.py). Metres, z up. A character facing -y has yaw 0
(toward a camera that stands at smaller y and looks along +y). Stations of the one greenhouse run along x; the other
places (bus, yard sale, sidewalk, bedroom) are far apart in y."""
import math

HALL = (-9.0, 52.0)           # the greenhouse's x range; y runs -7 to 9
SX = {"bench": 0.0, "hose": 8.0, "tom": 16.0, "radio": 24.0, "tank": 32.0, "aisle": 37.0, "table": 43.0}
BUS = (0.0, -100.0)
YARD = (0.0, -200.0)
WALK = (0.0, -300.0)
BED = (0.0, -400.0)

# the bench: top at z 0.9, x -1.2..1.2, y -0.05..0.75
BENCH_TOP = 0.90
BENCH_ARM = (0.55, 0.36, BENCH_TOP)          # the forearm prop lying on it (along x)
# the koi tank: coping top at 1.12, water at 1.0; Gus stands behind it at y 0.62
TANK_Y = 0.62
RIM_ARM = (SX["tank"] - 0.15, -0.72, 1.12)   # the front coping
# Gus's table
TABLE_Z = 0.75
TABLE_ARM = (SX["table"] - 0.05, -0.26, TABLE_Z)
CHAIR_Y = 0.92
RADIO_Z = 0.92                                 # the top of the radio on its crate


def d2r(a):
    return a * math.pi / 180.0
