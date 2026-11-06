"""Shared places for ep134 "five rooms" (make_story.py and set.py). x east, y north, z up. A character facing -y has
yaw 0, +x is 90, -x is -90. Every place is a small still set at its own origin, 60 m apart.

Nothing in the film moves in the set: the hall is built seven times, each a still state (which of the doors are open),
and a cut goes from one to the next. The tenth door is already there and shut in the morning copy (M)."""

HALL_W = 3.4           # x from -1.7 to 1.7
HALL_L = 14.5          # y from 0 (the stair head) to the end wall with the window
HALL_H = 2.8
LX, RX = -1.7, 1.7     # the walls the doors are in
DOORY = {5: 2.4, 6: 4.4, 7: 6.4, 8: 8.4, 9: 10.4, 10: 12.4}     # left wall doors (and the tenth, shut, in M)
RDOORY = {1: 3.4, 2: 5.8, 3: 8.2, 4: 10.6}                       # right wall doors

# the hall in its states: which left doors are open, and how far (degrees)
HALLS = {
    "A": {"o": {}},                              # night, 5 to 9 shut
    "B": {"o": {7: 7}},                          # door seven open an inch
    "C": {"o": {7: 100}},
    "D": {"o": {7: 100, 5: 100}},
    "E": {"o": {7: 100, 5: 100, 8: 100}},
    "F": {"o": {7: 100, 5: 100, 8: 100, 6: 100, 9: 100}},
    "M": {"o": {7: 100, 5: 100, 8: 100, 6: 100, 9: 100}, "morning": True},
}
HALL_O = {k: (60.0 * i, 0.0) for i, k in enumerate("ABCDEFM")}

HOUSE = (480.0, 0.0)     # the newlyweds' small sunny house
BOARD = (540.0, 0.0)     # the boarding house on the hill
THEO = (600.0, 0.0)      # Theo's apartment hall
KIT = (660.0, 0.0)       # the kitchen (June)
LIV = (720.0, 0.0)       # the living room (Dad)
PORCH = (780.0, 0.0)     # the porch and front door
