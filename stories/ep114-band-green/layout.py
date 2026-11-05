"""Shared places for ep114 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0,
+x 90, +y 180, -x -90. The town green is a square lawn; the white bandstand is at the north end (+y), its stage
faces the lawn. My bench is on the west edge, facing east."""
import math

BENCH1 = (-6.5, -1.0)        # centre of my iron bench (faces +x)
BENCH2 = (7.4, -0.6)         # the other bench, in the last shots (faces -x)
STAGE = (0.0, 8.8)          # centre of the players' row; the stage floor is at z = 0.9
STAGE_Z = 0.9
BAND_X = [-3.2, -1.6, 0.0, 1.6, 3.2]
BAND_OFF_Y = 26.0            # where the band comes from and goes to (behind the bandstand)
BEAT = 60.0 / 128.0          # seconds per beat (128 BPM)

# name: (x, y, yaw degrees at rest)
DANCE = {
    "grandpa": (-4.4, -3.0, 60.0),
    "bank": (-3.4, 0.5, 110.0),
    "mail": (-3.0, 3.1, 140.0),
    "sand": (-2.2, -1.2, 30.0),
    "t1": (-0.6, -3.6, 200.0),
    "t2": (1.6, -0.8, 120.0),
    "t3": (0.2, 2.2, 250.0),
    "t4": (3.0, 3.6, 170.0),
    "t5": (-1.2, 5.4, 310.0),
    "t6": (4.6, -2.8, 80.0),
    "t7": (2.8, -4.6, 15.0),
}
ME_SEAT = (-6.25, -1.75)     # me, seated (yaw 90, facing +x)
ME_STAND = (-5.2, -0.7)      # where I dance


def yaw_to(frm, to):
    """The yaw (radians) that faces `to` from `frm`."""
    return math.atan2(to[0] - frm[0], -(to[1] - frm[1]))
