"""Shared places for ep153 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0
(faces a camera to the south), +x 90, +y 180, -x -90.

The pier runs north into the bay; its deck top is z = 0. The green lock-box stands on a post at the pier's north
end, facing south (down the pier). My garage and Bea's office are far off along x, on their own sunny streets."""

PIER_W = 6.0               # deck width (x -3..3)
PIER_Y0, PIER_Y1 = -30.0, 14.0
RAIL_H = 1.1
WATER_Z = -1.6

BOX = (0.0, 13.45)         # the lock-box's centre (x, y); it faces south
BOX_Z0, BOX_Z1 = 1.05, 1.55   # body bottom and top
BOX_W, BOX_D = 0.72, 0.5
ME_BOX = (-1.2, 13.15)     # me beside the box, facing the camera
HAL_BOX = (1.25, 13.15)    # Old Hal and Bea stand on the box's other side
BEA_BOX = (1.25, 13.15)

RAIL_E = 2.7               # standing places at the east rail (Ty and me, the gulls)
ME_RAIL = (1.6, 6.0)
TY_RAIL = (-0.4, 6.4)
SHACK = (-1.9, 0.0)        # the bait shack's centre (west side); its awning reaches east
TY_SHACK = (-0.3, -1.6)
HAL_CAST = (-1.9, 9.5)     # Hal at the west rail, casting
POST = (-6.5, 12.0)        # the tall piling out in the water, left of which the fish are

GARAGE = (40.0, 0.0)       # the garage door's centre on the street (y = 0 is the door line); the room runs north
G_W, G_D, G_H = 5.2, 6.4, 3.4
DOOR_W, DOOR_H = 3.8, 3.0
BIKE = (GARAGE[0] - 1.75, 3.9)     # the sheeted bike, along the west wall (front wheel to the north)
BENCH = (GARAGE[0] + 0.5, 5.8)     # the workbench along the north wall (its front edge faces south)
BENCH_L = 2.8
BENCH_Z = 0.95
C1B = (GARAGE[0] - 0.62, 5.62)     # card one and card two propped on the bench
C2B = (GARAGE[0] - 0.16, 5.62)
ME_G = (GARAGE[0] - 0.1, 2.9)      # me in the garage
TY_DOOR = (GARAGE[0] + 0.5, -0.6)  # Ty in the doorway

OFFICE = (80.0, 0.0)       # Bea's office door (a wall facing south)
