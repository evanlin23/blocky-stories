"""Shared places for ep129 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0.

Nothing in this set moves (batch 14). Every state of the box is its own small stage, 60 m apart along x, and a shot
just points the camera at the stage it needs. Characters are placed at (stage offset + local x, y) by the acting keys.
Local coordinates below are inside one stage.
"""
# stage x offsets
ST = {
    "R1": 0.0,      # front room, wrapped box on the mantel, bow straight, daylight, no truck
    "R2": 60.0,     # front room, bare mantel, a wrapped box held at waist height in front of the holder
    "R3": 120.0,    # front room, wrapped box on the mantel, bow bent; truck at the curb, streamers on the porch
    "R3N": 180.0,   # same, night: navy window pane, a steady lamp, a blanket on the couch, no truck
    "R4": 240.0,    # open empty box on the mantel, the cream bow beside it
    "R5": 300.0,    # R4 plus the small blue box
    "R6": 360.0,    # bare mantel, nothing held
    "KA": 440.0,    # kitchen, an empty open box and a roll of red paper (twelve years ago)
    "KB": 500.0,    # kitchen, morning: a mug and a plate
    "KC": 560.0,    # box on the counter, the paper coming off
    "KD": 620.0,    # box on the counter, the lid tilted up
    "KE": 680.0,    # box on the counter, lid off, empty
    "KF": 740.0,    # open empty box held an inch over the counter
    "KG": 800.0,    # cake
    "KH": 860.0,    # night: the small blue box, a lamp, a navy window
    "MA": 940.0,    # Mrs. Albee's green porch
    "MS": 1000.0,   # Sam's kitchen table
    "MP": 1060.0,   # the post office counter
}

BOX = 0.5                        # the box is a 0.5 m cube
MANTEL_Y = 2.55                  # the box's centre depth on the mantel
SHELF_Z = 1.2                    # top of the mantel shelf
BOX_Z = SHELF_Z + BOX / 2        # centre of the box on the shelf
DOOR_X = -2.3                    # the front door in the north wall (centre)
WIN_X0, WIN_X1 = 1.5, 3.0        # the window in the north wall
ARM = (-0.5, 1.25)               # Dad's armchair (faces south)
COUCH_X0 = 0.1                   # the couch's west end (it is 2.0 wide)
COUCH = (1.1, 1.25)              # its centre
SEAT = 0.42                      # a seated person is lowered by this
DAD_SEAT = (-0.5, 1.25)
ME_SEAT = (0.75, 1.25)
HOLD = (0.0, 1.45)               # where the holder stands in R2 (box centre 0.62 m in front, z 1.0)
HOLD_BOX = (0.0, 0.8, 0.88)
ISLE_Y = 1.1                     # the kitchen island's centre depth
ISLE_Z = 0.82                    # its top
STAND_Y = 1.85                   # where people stand behind the island
