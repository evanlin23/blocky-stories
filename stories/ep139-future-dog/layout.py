"""Shared places for ep139 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0,
+x 90, +y 180, -x -90. Three scenes, far apart along x so no shot sees another:
the patio (x -4..4), the leafy side street (x 60..100) and two montage spots (x 200, x 230)."""

# ---- my patio: brick wall behind at y 3.8, low white fence east (x 3.0, with the side gate) and west (x -3.0)
TABLE = (0.0, 1.4)          # round table, r 0.7, top z 0.72
TABLE_R = 0.7
TABLE_Z = 0.72
ME_SEAT = (-0.2, 2.4)         # my chair; I sit facing the camera (south)
SEAT_H = 0.46
PHONE = (-0.45, 1.7, 0.735)  # my phone, face-up, on the table edge nearest the camera
PHOTO = (0.3, 1.0)         # the framed photo on the table
CHAIR2 = (-1.05, 1.55)        # the chair beside the phone (Noodle hops up on it)
GATE_X = 3.0                 # the side gate in the east fence, leaf between y 0.4 and 1.4
GATE_Y0, GATE_Y1 = 0.4, 1.4
DOOR_ME = (1.8, 3.35)        # me in the sliding door at sunrise
NOODLE_UNDER = (0.45, 1.5)
NOODLE_LIE = (2.35, 0.9)     # lying by the gate, facing east

# ---- the street (sidewalk y -1.4..1.4, road south of it, houses north)
ST = 60.0
SIDEWALK_Y = 0.2
VAN_X = 86.0                 # the van's centre x; its back (south end) at y 0.7, the ramp down to the sidewalk
THEO_AT = (84.6, -0.9)       # Theo by the ramp
HOUSE = (78.0, 10.0)         # Theo's yellow house, porch on its south face at y 6.6
PORCH_Y = 6.2

# ---- montage spots
NEIGH = (200.0, 0.0)
SAM = (230.0, 0.0)
