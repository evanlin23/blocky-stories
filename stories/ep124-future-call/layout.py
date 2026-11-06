"""Shared places for ep124 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0,
+x 90, +y 180, -x -90. The garage runs x -4.6..4.6, y -3.8 (the open door) to 4.0 (the back wall)."""

ME = (-0.4, 3.3)            # me, beside the phone
PHONE = (-1.0, 3.93, 1.28)  # the wall phone's centre (its face is at y 3.93, facing the room)
DAD = (1.5, 3.35)           # Dad, behind the bench
STOOL = (1.5, 3.45)         # the low stool he drops onto
BENCH = (1.85, 2.6)         # centre of the long bench; x 0.3..3.4, y 2.2..3.0, top z 0.92
BENCH_Z = 0.92
ME_NEAR_DAD = (0.55, 3.35)  # where I stand from L31
TRUCK_X, TRUCK_Y0, TRUCK_Y1 = -3.0, -1.9, 2.9

# the three montage rooms, far off along x so no garage shot sees them
MOM_ROOM = (40.0, 0.0)
UNCLE_ROOM = (70.0, 0.0)
KITCHEN = (100.0, 0.0)
