"""Shared places for ep144 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0.

One outdoor town pool. The water runs y 0..Y (the near wall at y 0, the far wall at y Y), eight lanes 1.8 m wide
from x -7.2 to 7.2, lane k centred at (k - 4.5) * 1.8. The deck is south (y < 0, the changing house and the
board), east, west and north of it. Water is z 0, the deck top is DECK.
"""
Y = 14.0
LW = 1.8
DECK = 0.14
SWIM_Z = -0.5            # a swimmer's root, leaning forward: shoulders at the surface, head just above it
STAND_Z = -1.12          # a swimmer standing at the wall, chest-deep
BLOCK_H = 0.5


def lane_x(k):
    return (k - 4.5) * LW


L4 = lane_x(4)           # -0.9
L2 = lane_x(2)           # -4.5
BLOCK = (L4, -0.55)      # lane four's starting block (top DECK + BLOCK_H)
BOARD = (-1.7, -4.6)     # the lap board, facing +y; plate centre z 1.75
SIGN = (-0.15, -2.2)     # the pool sign, facing +y
CHAIR = (2.42, -3.2)     # the lifeguard's tall chair on the south deck, turned to watch lane four
CHAIR_YAW = 205.0        # its front (and the guard) faces north-west, up lane four
SEAT_TOP = 2.3
HOUSE = (-3.5, -10.5)    # the changing house centre
