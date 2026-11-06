"""Shared places for ep128 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0.
Every place is a small still set at its own origin, 60 m apart, so no light reaches another place."""
APT_D = (0.0, 0.0)       # my one room by day (cream, coral couch, butter fridge, teal kitchen)
APT_B = (60.0, 0.0)      # the same room by day with moving boxes (S07b, S08)
APT_N = (120.0, 0.0)     # the same room at violet dusk
ST_D = (180.0, 0.0)      # the stairwell by day, Mom's door shut
ST_N = (240.0, 0.0)      # the stairwell at night, Mom's door open on her lilac flat
FRIDGE = (300.0, 0.0)    # the open fridge, close
DEN = (360.0, 0.0)       # Grandpa's den
DINER = (420.0, 0.0)     # the diner counter
HALL_D = (480.0, 0.0)    # my childhood hallway by day (and the desk)
HALL_N = (540.0, 0.0)    # the same hallway at dusk
CAR = (600.0, 0.0)       # the packed car

# the apartment (local): interior x[-3,3] y[0,5.6] h 2.9
APT_W, APT_D_, APT_H = 3.0, 5.6, 2.9
COUCH_X, COUCH_Y = -0.85, 4.9        # where I sit (root); seat top z = 0.44
PHONE_COUCH = (-1.5, 4.55, 0.44)
STOVE = (1.75, 2.2)                 # where I stand at the kitchen
COUNTER_PHONE = (2.5, 3.5, 0.95)
MID = (0.0, 2.8)

# the stairwell (local): x[-1.2,1.2]; stairs rise along +y from y 0 (z 0) to the landing y 4.2 (z 2.55)
STEP_N, STEP_DY, STEP_DZ = 12, 0.35, 0.2125
LAND_Z = 2.55
LAND_Y = (4.2, 6.4)
DOOR_Y = 6.4
FLAT_Y = (6.4, 12.0)               # Mom's flat, floor at z = LAND_Z
FLAT_W = 2.8
MOM_XY = (0.0, 9.4)                # where she is frozen
FLAT_COUCH = (-1.3, 11.0)
FLAT_TABLE = (1.6, 10.2)
FLAT_PHONE = (1.55, 10.15)
