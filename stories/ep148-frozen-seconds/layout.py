"""Shared places for ep148 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0
(faces a camera to the south), +x 90, +y 180, -x -90. The fountain stands at F; people sit on its south rim."""
import math

F = (0.0, 8.0)             # fountain centre
R_OUT, R_IN = 2.6, 2.0     # rim outer / inner radius
RIM_Z = 0.5                # rim top
FLOOR_Z = 0.3              # basin floor (people can wade)
WATER_Z = 0.36
COL_R = 0.5                # the spray column's base radius


def rim_y(x, r=R_OUT):
    return F[1] - math.sqrt(r * r - x * x)


SIT_Z = -0.18              # pos z of a sitter (hip on the rim top)
ME_SIT = (-0.8, round(rim_y(-0.8) + 0.05, 3))
LEO_SIT = (0.8, round(rim_y(0.8) + 0.05, 3))
PRETZEL = (0.25, round(rim_y(0.25, 2.5), 3))   # on its napkin, on the front of the rim top, between us
# standing places on the plaza before we sit
ME_STAND = (-0.7, 3.9)
LEO_STAND = (0.9, 3.9)
# Leo hides behind the spray column, steps out to LEO_OUT
LEO_HIDE = (0.0, 9.15)
LEO_OUT = (0.85, 7.1)
# the montage rooms, far off along x
KITCHEN = (40.0, 0.0)
FRONT = (70.0, 0.0)
CAR = (9.0, 2.0)
