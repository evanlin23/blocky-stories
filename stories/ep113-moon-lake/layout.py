"""Shared places for ep113 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0.
The lake is a round disc of radius 50 at the origin; its water top is WZ. Grandma's dock runs north off the lawn."""
WZ = 0.1                 # the water's top
DECK = 0.62              # the dock deck's top
DOCK_X = 0.0
DOCK_Y0, DOCK_Y1 = -52.0, -30.0   # shore end, lake end
MID = (1.5, -18.0)       # where the moon sleeps (the glow), 12 m off the dock's end
DOME_R = 12.0            # the moon's rising cap (never seen whole)
BOAT_HOME = (2.5, -29.0)
HOUSE = (0.0, -64.0)
PORCH_Y = -57.0
BEACH = (-33.0, -40.0)
NDOCK1 = (22.0, -38.0)   # the coffee neighbour's dock end
NDOCK2 = (-14.0, -41.0)  # the old man fishing
U = (1200.0, 0.0)         # the lake bed
UFLOOR = -9.0
UTOP = -5.0              # the moon patch's top on the bed
WATCH = (200.0, -100.0)
