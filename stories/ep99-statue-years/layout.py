"""Shared places for ep99 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0."""
Z0 = 3.0                 # the park's ground height (the town is at z = 0)
ZB = Z0 + 1.0            # top of the statue's plinth
TRAY_Y = -6.0            # the brass candle tray
BENCH = (-6.5, -9.0)     # the bench faces +y (the statue)
STEPS_Y = (-16.0, -26.5)  # top and bottom of the brick steps
STREET = (60.0, 0.0)     # main street: the bakery's front is at y = +2.0 above it
COUNTER = (100.0, 0.0)   # inside the bakery: customers at y < 0.4, Mrs. Lark behind the counter
HOME_IN = (-80.0, 0.0)   # our hall (mirror on the +y wall) and kitchen table
HOME_OUT = (140.0, 0.0)  # our front door
CAL = (0.0, -100.0)      # the calendar glyph
SLAB = (0.0, -140.0)     # the statue's cheek, close: the stone face is at x = SLAB_X
SLAB_X = 1.25
MIRRORS = (-40.0, 0.0)   # the town's mirror wall
