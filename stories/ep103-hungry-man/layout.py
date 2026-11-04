"""Shared places for ep103 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0.

The street runs along x. North houses (side +1) have their fronts at y = +9 and face -y, south houses (side -1) have
fronts at y = -9 and face +y. Our house is north x = 0 (hollow, with a hall inside); Grandpa's is south x = 0.
"""
FRONT = 9.0                 # |y| of every front wall
DECK_OUT = 1.8              # the porch deck sticks out this far from the front wall
DECK_Z = 0.3                # top of the deck
PLATE_DX = 1.3              # the plate sits this far right of the house's centre line, on the deck
PLATE_DY = 1.15             # and this far out from the front wall
SPACING = 9.0
KS = list(range(-6, 7))
# named neighbours: (side, k)
OURS = (1, 0)
GRANDPA = (-1, 0)
FERRO = (-1, 2)
ABERN = (1, 2)
BRISCO = (-1, -2)
FRONT_DOOR_HINGE = (-0.6, 9.15)
KITCHEN = (200.0, 0.0)      # our kitchen: back wall y = +3.5
GROOM = (300.0, 0.0)        # Grandpa's hall and kitchen


def px(side, k):
    return k * SPACING


def plate_pos(side, k):
    return (k * SPACING + PLATE_DX, side * (FRONT - DECK_OUT + (DECK_OUT - PLATE_DY)) , DECK_Z)
