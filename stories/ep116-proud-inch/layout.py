"""Shared places for ep116 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0.

The shop is one room: x -7.5..4.4, y -6..4.5, ceiling 3.4. The counter runs along y 0 (x -5..1.5), Grandpa's crate sits
at its right-hand end in the corner, the back doorway (with the pencil-marked frame) is on the back wall behind him,
the front window and door are on the front wall. The three montage places are far to the east.
"""
S = 0.34                       # metres per rig unit
GH = 1.6                       # Grandpa's height spec
CEIL = 3.4
CRATE_H = 0.4
G_POS = (3.1, 1.0)             # Grandpa's crate (his feet point at -y)
G_HIP = CRATE_H + 0.27         # his hips when seated
ME_POS = (-0.5, 0.9)            # me behind the counter
ME_FRONT = (1.7, 0.5)        # me at the counter end, beside Grandpa
DOOR_X0, DOOR_X1, DOOR_TOP = 2.05, 3.45, 2.2
POST_X0 = 1.55                 # the marked left post spans x 1.55..2.05
BACK_Y = 4.5
MARK_X = 1.70
MARK_Z0, MARK_DZ, MARKS = 1.52, 0.0254, 50
CAFE = (40.0, 0.0)
GARDEN = (80.0, 0.0)
WEDDING = (120.0, 0.0)
FDOOR_X = -5.6                 # front door centre on the front wall y -6
FRONT_Y = -6.0


def head_z(h, hip_z):
    """Height of a head's centre for a character h tall whose hips are at hip_z (rig: neck 4.0, head centre +0.64)."""
    return hip_z + (4.64 - 2.0) * S * h


G_HEAD = head_z(GH, G_HIP)     # seated
ME_HEAD = head_z(1.0, 2 * S)
