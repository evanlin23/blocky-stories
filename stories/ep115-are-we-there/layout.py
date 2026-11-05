"""Shared places for ep115 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0 and the
camera for a face stands on the -y side looking +y. The van drives toward -y, so the world scrolls toward +y.

THE VAN (origin): floor top z = 0, interior x -1.2..1.2, y -1.6 (the cowl) .. 2.7 (the hatch), roof underside z 2.05.
Seats have their top at z = 0.5. Mom drives on the +x side (the van's left, so she is on the right of a camera that
looks back at her). The back row sits at y = 1.45: me at x = -0.85, Jo at x = 0.38, the cooler between at x = -0.235.
Heads are 1.57 m up (centre) with the feet at z = 0, so a seated character keeps its hips at 0.68 and its feet on the
floor (the legs are turned forward).
"""
MOM = (0.45, 0.0)
JO = (0.2, 1.45)
ME = (-0.8, 1.45)
COOLER = (-0.3, 1.38)
HEAD_Z = 1.57

PINE = (100.0, 0.0)       # the huge snow-capped pine on the bend
PLOW = (200.0, 0.0)       # the snowplow in its pull-off
TRUCK = (260.0, 0.0)      # the trucker's cab at a pull-off
DOOR = (320.0, 0.0)       # a cabin door, the pizza man
SILVER = (380.0, 0.0)     # the silver car of quiet grown-ups
FALLS = (440.0, 0.0)      # the frozen waterfall seen straight on

ROAD_Z = -0.45            # the road's top; the van's wheels stand on it
POST_X = -3.7             # the mile post, beside the road
FALLS_X, FALLS_Y = 7.2, 10.0   # the waterfall seen through Mom's window
