"""Shared places for ep105 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0.
The cul-de-sac is the main stage: my pale blue house on the west (x -7.5), Vern's butter yellow house on the east
(x +7.5), a white picket fence on x = 0, the street to the south (y < -7). Other rooms sit far off so they never show."""
MY_HOUSE = (-7.5, 9.0)       # centre of my house body (front wall at y = 6)
VERN_HOUSE = (7.5, 9.0)
FRONT_Y = 6.0                # both front walls
MY_DOOR = (-6.0, 6.0)
VERN_DOOR = (7.5, 6.0)
MY_WINDOW = (-10.2, 6.0)     # window onto a small room behind (the toothbrush window)
CAL = (6.0, 5.93)           # the porch calendar on its nail, left of Vern's door (x, y), z 1.65
CHAIR_A = (8.9, 4.9)         # Vern's rocking chairs
CHAIR_B = (10.5, 4.9)
MBOX_ME = (-3.7, -5.6)       # the mailboxes
MBOX_VERN = (3.7, -5.6)
FENCE_Y = (-4.0, 3.2)        # the fence on x = 0 runs from y0 to y1
MAPLE = (0.2, 4.6)           # the maple between the yards, behind the fence's end
DRIVE = (12.9, 0.0)          # the moving truck lane, east of Vern's house
ROOM = (60.0, 0.0)           # Vern's living room: photo wall on the +y side, window wall at y = -3
WED = (-60.0, 0.0)           # the garden wedding
BARB = (0.0, 60.0)           # the barbershop corner
GAR = (60.0, 60.0)           # Vern's garage
