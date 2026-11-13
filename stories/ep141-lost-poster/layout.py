"""Shared places for ep141 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0,
+x 90, +y 180, -x -90. Every stage is lit and dressed alone; cuts move the cast between them.

Outdoor stages sit along y = 0 (the camera looks north from the south, the sun is behind it): the corner with the
notice board, the mailbox, my door, Grandma's door and the little blue car. Indoor stages sit along y = -60:
Mom's kitchen, my card room, Grandma's kitchen and the pie tent (a closed striped tent with an open flap on its
left wall).
"""

CORNER = (0.0, 0.0)
MAIL = (-16.0, 0.0)
ADOOR = (-32.0, 0.0)
GDOOR = (-48.0, 0.0)
CAR = (18.0, 0.0)
MOMK = (0.0, -60.0)
CARD = (30.0, -60.0)
GRANK = (60.0, -60.0)
TENT = (100.0, -60.0)

BOARD_Y = 3.0                       # the notice board's face (posters stand proud of it)
SLOT = {"umb": -1.7, "keys": -0.6, "me": 0.5, "gran": 1.6}   # the poster x on the board
POSTER_Z = 1.65                     # the poster sheets' centre height
ROOM_HALF = 4.5                     # indoor rooms are 9 x 9 m, 3 m high

SIT_Z = -0.05                       # a seated character's z (legs level on a 0.46 m seat)
