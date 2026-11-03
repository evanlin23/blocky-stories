"""Places for ep41-orchard-rows, in metres. Plain numbers, read by set.py (Blender) and generator/make_story.py.

Four places, far apart so one sun lights them all and no shot sees another:
- the orchard and Nana's house at (0, OY): the house's back wall (y = OY) faces the orchard, which runs along +y.
  Rows are tree lines across the way (row k at y = OY + ROW0 + 8 (k - 1)), 8 trunks to a row with a gap at x = 0 for
  the path. The far row (row 7) is at +62; the bench is just past it.
- the town street along y at x = 0 (z = 0 cobbles).
- the townsman's kitchen at (30, 0).
- the garden path and green door at (60, 0).
Characters face -y at yaw 0.
"""
OY = 200.0
ROW0 = 14.0
ROW_GAP = 8.0
FLOOR = 0.9            # Nana's floor height above the grass
H_X0, H_X1 = -6.0, 5.0     # the house, x
H_Y0, H_Y1 = -7.5, 0.0     # the house, y (relative to OY); the back wall (with door and kitchen window) is y = 0
DOOR_X = 0.0
WIN_X0, WIN_X1 = -3.2, -2.0   # kitchen window x
WIN_Z0, WIN_Z1 = FLOOR + 1.0, FLOOR + 2.3
PART_X1 = -3.6        # partition: my room (west) | kitchen
PART_X2 = 2.5         # partition: kitchen | Nana's bedroom
BENCH_Y = 69.5        # relative to OY
LEFT = -1.1           # the Rough One's stride to the left of the path x = 0


def o(x, y, z=0.0):
    """Orchard coordinates (y relative to OY) to world."""
    return [round(x, 3), round(OY + y, 3), z]
