"""Shared places for ep136 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0,
+x 90, +y 180, -x -90. The Rim: the railing runs east-west along y = RAIL_Y, the dirt lot is north of it, and the
canyon is south of it, with the far wall at y = WALL_Y (its face looks north). Cameras that look north at a person
hang over the gap; the bluff behind the lot is their backdrop."""

RAIL_Y = 0.35
ST = (0.0, 1.35)           # where Eli and every vignette person stands, behind the railing, facing the canyon (-y)
POST_RAIL = (0.95, 1.3)    # the post at the railing, beside the person
WALL_Y = -34.0             # the far wall's face plane
ROCK_X = (8.0, 0.0, -8.0)  # the one-, two- and three-dot rocks (east is the left of a camera looking south)
ROCK_Z = 6.2               # rock centre height
XT, YT = 2.6, 8.0          # the pickup (nose toward the canyon, -y)
SEAT = (XT - 0.45, YT + 0.15, 0.11)   # Eli's seat in the cab (x, y, z)
POST_BEHIND = (XT + 0.45, YT + 3.7)   # the post when seen behind the truck
POST_AHEAD = (XT - 0.1, YT - 3.9)     # the post when seen ahead through the windshield
CAR = (0.0, 4.4)           # Mr. Bell's red car, nose just behind him
