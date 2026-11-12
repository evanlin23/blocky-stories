"""Shared places for ep145-dog-barks (make_story.py and set.py). x east, y north, z up. Yaw 0 faces -y, 90 faces +x,
180 faces +y, -90 faces -x.

Our backyard on a Sunday: the yellow house across the north (y = 7), a red brick patio in front of it, a lawn, a white
picket fence round the other three sides, the side gate in the south fence, and Mr. Hale's house over the west fence.
"""
import math

FX0, FX1, FY0 = -6.6, 8.5, -2.5          # west fence x, east fence x, south fence y
HOUSE_Y = 7.0                            # the back wall's outer face
GATE = (-1.5, FY0)                       # the side gate's centre in the south fence (opening 1.6 m wide)
GATE_W = 1.6
GRILL = (0.0, 4.4)
ME_G = (-0.75, 3.4)                      # me at the grill
GR_G = (0.75, 3.4)                       # Grant at the grill (1.9 m from me)
TABLE = (3.7, 5.5)                       # the picnic table's centre (long side along x)
WIN = (1.5, 1.15, 2.35)                  # kitchen window: centre x, sill z, head z
RING = (1.1, 6.78, 1.27)                 # the ring box on the sill (centre)
DOOR_X = -3.0                            # the back door
HALE_HOUSE_X = -10.6                     # the neighbour's east wall
HALE = (-7.0, 2.6)


def yaw_to(a, b):
    """The yaw of someone at a looking at b."""
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)
