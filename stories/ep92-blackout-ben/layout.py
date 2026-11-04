"""Places for ep92 "blackout ben", shared by generator/make_story.py and set.py. x east, y north, z up.
A character facing -y has yaw 0, +x is 90, -x is -90, +y is 180."""

# living room: x -5..5, y -3.5..3.5, back wall (mantel) at y = 3.5, window in the front wall (y = -3.5)
LR_X0, LR_X1, LR_Y0, LR_Y1, WALL_H = -5.0, 5.0, -3.5, 3.5, 2.8
COUCH = (0.3, 2.25)
SEAT_Y = 2.08
SEAT_Z = 0.6
SEAT = {"L": -0.85, "M": 0.3, "R": 1.45}
TABLE = (0.3, 0.1)            # coffee table
DINE = (-3.2, 0.45)           # round dining table
MANTEL_X = 0.0
# hall: x 5..12, y -1..1; my door in the wall at x = 12
HALL_X0, HALL_X1 = 5.0, 12.0
# my bedroom: x 12..17, y -2.5..2.5
BR_X0, BR_X1, BR_Y0, BR_Y1 = 12.0, 17.0, -2.5, 2.5
BED = (15.2, 1.15)            # centre; lengthwise along x, head to the east wall
STAND = (16.45, 0.0)          # bedside table
# street: our house front is y = -3.5; road y -14..-9; row of houses across at y = -24
HOUSE_Y = -24.0
HOUSE_X = [-20.0, -10.0, 0.0, 10.0, 20.0]
CAR = (-8.0, -7.0)            # car centre, nose toward +x
# the window room for the families seen through a window
WR = (60.0, 0.0)
# kitchen drawer
KD = (90.0, 0.0)
