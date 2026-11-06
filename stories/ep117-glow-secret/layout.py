"""Shared places for ep117 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0.
Every scene is open on its -y side, where the camera stands. Each little scene sits 60 m from the next."""
ROOM = (0.0, 0.0)          # the pizza place: back wall at y 4.0, the booth bench along it, window above
SEAT_Y = 3.45              # hips of anyone sitting on the bench
SEAT_Z = 0.67              # hip height when seated (the bench top is 0.5)
HEAD_SEATED = 1.56
TABLE_Y = (2.4, 3.2)
PIZZA = (0.0, 2.8, 0.98)
GUM = (9.8, 3.0)          # the gumball machine
LOT = (60.0, 0.0)          # the dark parking lot: Dad's wagon along x at y 16
CAR = (60.0, 16.0)
BUS = (-60.0, 0.0)         # a bus stop: back wall y 5
PLAN = (-120.0, 0.0)       # a party planner's door
CARD = (-180.0, 0.0)       # an empty card table
FRIDGE = (-240.0, 0.0)     # a kitchen, the open fridge
STAGE = (-300.0, 0.0)      # a purple stage for the joke insert
BW = 0.58                  # body_width of everyone who sits in the booth, so three faces fit the frame
