"""Shared places for ep119 (make_story.py and set.py). x east, y north (the way the train faces), z up.
A character facing -y has yaw 0; +x is yaw 90, +y is 180, -x is -90."""
HALF = 2.15                 # the quiet car's inner half-width
CAR_L = 28.0                # inner length, y from 0 (rear end door) to 28
CEIL = 2.7
ROWS = 10
ROW0, PITCH = 4.0, 2.1
WIN_X = 1.5                 # where a sitter at the window sits (seat 1.625 wide .95)
WIN_SEAT = 1.625
AISLE_X = 0.75              # aisle seat centre
SEAT_H = 0.5                # cushion top
HIP = 0.55                  # a seated hip


def row_y(i):
    return ROW0 + PITCH * i


ME_ROW, TED_ROW = 3, 4
AIS = 0.8                               # where a sitter at an aisle seat sits
ME = (-AIS, row_y(ME_ROW))              # my aisle seat (left)
TED = (AIS, row_y(TED_ROW))             # Teddy's aisle seat (right), one row ahead; his window is the one beside it
SEAT9 = (0.75, row_y(7))                # seat nine (right aisle seat)
SEAT12 = (-WIN_X, row_y(6))             # seat twelve (left)
RACK_HAT = (-WIN_X, row_y(8))
DOOR = (0.4, 1.8)                       # side door opening, y range, in the right wall
LOUD_Y0 = -29.0                         # the loud car: interior y from -29 to -1
PLAT = (1.95, 9.6, -4.5, 9.5)           # platform x0, x1, y0, y1
PARTY = (60.0, 0.0)
BUS = (60.0, 40.0)
BATH = (60.0, 80.0)
ENV_PERIOD = 48.0
SPEED = 2.4
