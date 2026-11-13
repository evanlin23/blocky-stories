"""Shared places for ep155 "good boy" (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw
0, +x 90, +y 180, -x -90. Three stages far apart along x so no shot sees another:

  DALES   the Dales' street (x 40..80): road y -3.4..3.4, front yard and picket gate (gate at y 5.4), the butter-yellow
          house with its front wall at y = FY (12), a wooden deck at z DECK (0.45) from y 10 to 12 with two steps down,
          a front room behind the wall (y 12.3..19) with a ceiling.
  ORTIZ   Mrs. Ortiz's lilac front room at x -60 (x -64..-56, y -4..4).
  CORNER  a street corner at x 140 (the man and the blank sign).
"""

# ---- the Dales
HX = 60.0                  # the door's centre x
FY = 12.0                  # the front wall's outer face
DECK = 0.45                # deck top
DECK_Y0 = 10.0             # deck front edge
DECK_X0, DECK_X1 = 56.0, 64.0
DOOR_W, DOOR_H = 1.3, 2.15
WIN_X, WIN_W = 56.7, 1.8   # the front window beside the door (ground floor), x centre and width
WIN_Z0, WIN_Z1 = 1.4, 2.7
PEG_X = 61.6               # Pepper's peg board, right of the door
PEG_Z = 2.0
GATE = (HX, 5.4)
SEAT_ME = (58.9, 10.15)    # where I sit (the blanket)
SEAT_RORY = (57.5, 10.15)  # Rory 1.4 m along the same step
SEAT_DALE = (60.3, 10.15)  # Mr. Dale 1.4 m along the other way at dusk
HIP = 0.17                 # hip height above the seat when sitting
ROOM = (54.0, 66.0, 12.3, 19.0)   # front room x0 x1 y0 y1
ROOM_H = 2.9

# ---- the other stages
ORT = (-60.0, 4.0)          # Mrs. Ortiz's room: back wall face (y)
COR = (140.0, 0.0)          # the corner
