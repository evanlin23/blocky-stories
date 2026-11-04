"""Shared places for ep102 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0.
Every scene is open on its -y side, where the camera stands."""
FARM = (0.0, 0.0)          # Aunt Clem's: porch deck y 1.5..6, house wall y 6, rail at y 1.6 (x 2..8), swing at x -6
GATE = (0.0, -8.0)         # her wooden gate; the lane runs away from it along -y
RAIL_TOP = 1.5             # z of the rail top
MAIL = (200.0, 0.0)        # the mailbox row (the dirt lane runs along x at y 0, the boxes stand at y 3)
GAS = (100.0, 0.0)         # the gas station (building y 6), pump at y -1, picnic table at x -8
ROOM = (-60.0, 0.0)        # the guest room: back wall y 3.4, window with the sill, bed at left, photo
KIT = (-120.0, 0.0)        # our city kitchen: back wall y 3.4, window over the roofs, sink at left
CITY = (-180.0, 0.0)       # our street: the building stands at y 8, street runs along x at y 0
BUS = (-240.0, 0.0)        # inside a bus
ROAD = (300.0, 0.0)        # the ridge road runs along y at x 300; fence post and the turn at y 30
POST_Y = 30.0
