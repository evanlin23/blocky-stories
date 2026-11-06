"""Shared places for ep120 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0,
+x is 90, +y is 180, -x is -90. Every place is its own little stage far from the others; set.py lights only the one
the camera is in (stage_at).
"""

DAY = (0.0, 0.0)            # the painted street by day (houses face -y, fronts at y = 8)
DAY_SHOP = (36.0, 8.0)      # the auto shop's front wall (y = 8): the lot is at y < 8
HALL = (200.0, 0.0)         # the empty house's hall (the door is on the +y wall)
KITCHEN = (200.0, 30.0)
LIVING = (200.0, 60.0)
LOT = (400.0, 0.0)          # my building's lot at night (the building's front wall is at y = 10)
CAB = (400.0, 60.0)         # the pickup's cab, inside (facing +y)
SHOP = (600.0, 0.0)         # the shop and Dad's place at night (front wall y = 0, the lot is at y < 0)
SHOPIN = (600.0, 60.0)      # the shop downstairs, Dad's couch

APT_Z = 3.2                 # the apartment's floor above the shop
ROOM_Z = 7.0                # my room's floor (third floor)
ROOM_Y0 = 10.2              # my room, behind the facade at y = 10


def stage_of(x, y):
    if x < 150:
        return "day"
    if x < 350:
        return "hall" if y < 15 else ("kitchen" if y < 45 else "living")
    if x < 550:
        return "lot" if y < 40 else "cab"
    return "shop" if y < 40 else "shopin"
