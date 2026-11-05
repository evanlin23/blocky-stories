"""Shared places for ep107 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0.

Tulley's: the shop is x -7..7, y -4 (front wall) to 10 (back wall); the counter is at y = 3.5 (customers at y < 3, Mr.
Tulley behind it at y = 4.7); the back room is y 10 to 30 behind the door at x = 2.57. Every other place is its own cell
far away on the x axis, so their lights never meet.
"""
SHOP_DOOR = (-3.0, -4.0)         # the front door (hinge at x - 0.7)
COUNTER_Y = 3.5
COUNTER_TOP = 1.0
TUL = (-1.8, 4.4)                # Mr. Tulley's mark behind the counter
MEC = (-1.8, 2.5)                # me at the counter
STAMP_X = 0.0                    # the rubber stamp sits at x = STAMP_X + 0.02 (Tulley's right hand is at TUL x + 0.51)
BELL = (-3.2, 3.5)               # the brass bell on the counter
BACK_DOOR = (2.57, 10.0)         # the plain wooden door to the back room
AISLE_R = 2.57                   # the right aisle (my boxes on the right bank, facing -x)
AISLE_L = -2.57
ROW_Y0 = 12.4                    # my 47 boxes: y = ROW_Y0 + 0.3 k, k = 0..46 (k = 46 is the newest)
ROW_X = 4.3                      # the face of the right bank
BULB = (2.57, 24.6, 3.7)
KX = 80.0                        # Dad's kitchen (x 74..86, y 0..9)
HX = 140.0                       # Dad's house, outside
CX = 200.0                       # the road with the shoulder
HALLX = 260.0                    # the office hallway
RAINX = 320.0                    # the rainy front step
ODX = 380.0                      # Mrs. Oduya's driveway
LOBX = 440.0                     # the office lobby
APX = 500.0                      # my apartment
BACKX = 560.0                    # macro plates (receipt backs)
