"""Shared places for ep127 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0."""
# the tackle shop (roofless; the river and the lot are on its -y side)
FRONT_Y = -6.0           # front wall centre (outer face -6.15)
BACK_Y = 1.8             # back wall inner face
GCH = (-0.6, -1.0)       # Grandpa's armchair (faces -y)
MCH = (-0.6, -3.6)       # my armchair (faces +y)
LAMP = (0.35, 1.3)       # the one low lamp, on a small table against the back wall, right of Grandpa's chair
SLATE = (1.4, 1.62, 1.75)    # chalk slate on the back wall, by the till
WIN_X = -0.6
DOOR_X = 2.9
CNT_X0, CNT_X1, CNT_Y = 1.9, 5.7, 0.75   # the long counter
BEHIND = (3.8, 1.3)      # where a person stands behind the counter
SEAT_TOP = 0.46
LOT = (5.0, -11.0)       # my car's place in the gravel lot
# remote stages
CEIL = (60.0, 0.0)
ROAD = (150.0, 0.0)
BRIDGE = (250.0, 0.0)
KITCHEN = (350.0, 0.0)
PORCH = (450.0, 0.0)
STREET = (550.0, 0.0)
YARD = (650.0, 0.0)
CAR_DX = 0.48            # the driver's seat, left of the car's centre line (x)
CAR_DY = 0.12
BWIN = (-1.25, 0.95, 2.45, 1.7)   # the back-wall window behind Grandpa's chair: centre x, sill z, top z, width
