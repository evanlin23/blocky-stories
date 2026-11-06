"""Shared places for ep122 "face the wall" (make_story.py and set.py). x east, y north, z up. A character facing -y has
yaw 0, +x 90, +y 180, -x -90.

Upstairs (origin): the hall runs north along x -0.6..0.6, y 0..6.5; my spare room is west of it (x -4.2..-0.6, y 0..3.8),
Dad's old room east (x 0.6..4.2), Grandma's room at the north end (y 6.55..10). My bed is pushed against the west wall,
Dad's against the east wall. Other places sit far off: the kitchen at x +40, outside at +80, the stair at +120, the row
of three beds at +160.
"""
import math

# ---- upstairs
BX = -3.70           # my bed's centre line (x); mattress -4.17..-3.22, y 1.55..3.55, top at z 0.52
DX = 3.70            # Dad's bed's centre line (mirrored)
DOOR_Y = 2.6         # the door in each room's hall wall (centre), 0.9 wide
HEAD_Y = 3.15        # where a head rests on the pillow (y)
MATT_TOP = 0.52
LY_ROOT = (1.58, 0.69)   # a lying body: feet y and root z (lean -84 puts the head at HEAD_Y, z 0.85)
HS = (BX, HEAD_Y, 0.85)      # my head resting on the pillow
HD = (DX, HEAD_Y, 0.85)      # Dad's head on his pillow
WIN_X = -1.95        # the moon window in my room's north wall (x centre)

# ---- other places
KX, KY = 40.0, 0.0     # kitchen origin
EX, EY = 80.0, 0.0     # outside: house front at y = EY + 6, door at x = EX
SX, SY = 120.0, 0.0    # stairwell: steps rise to the north
RX, RY = 160.0, 0.0    # row of three beds
GX, GY = 0.0, 8.2      # Grandma's bed
GBX = 1.2              # her bed's centre line (x), against the east wall of her room

STEP_RISE, STEP_RUN = 0.19, 0.28


def yaw_to(frm, to):
    """The yaw (degrees) that faces `to` from `frm`."""
    return math.degrees(math.atan2(to[0] - frm[0], -(to[1] - frm[1])))


def orbit(tgt, dist, az, dz=0.0, lens=35, roll=0.0, tz=None):
    """A camera `dist` m from `tgt` in compass direction az (0 = east of it, 90 = north, 180 = west, 270 = south),
    dz above its height, looking at it. One key, as story.json wants it."""
    cx = tgt[0] + dist * math.cos(math.radians(az))
    cy = tgt[1] + dist * math.sin(math.radians(az))
    cz = tgt[2] + dz
    return [[0, [round(cx, 3), round(cy, 3), round(cz, 3)], [round(tgt[0], 3), round(tgt[1], 3), round(tgt[2] if tz is None else tz, 3)], lens]]
