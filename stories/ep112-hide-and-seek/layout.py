"""Shared places for ep112 (make_story.py and set.py). x east, y north (away from the usual camera), z up.
A character facing -y has yaw 0, +x 90, +y 180, -x -90. Everything is one back yard."""
TA = (0.0, 4.0)            # picnic table A (Mr. Glenn's, Grandma's): tabletop x -1.3..1.3, y 3.5..4.5, top z 0.78
TB = (-4.3, 3.4)           # picnic table B (the cousins', the big salad bowl), left of table A
FAR = 0.95                 # the far bench is TABLE_Y + FAR, the near bench TABLE_Y - FAR
SEAT = 0.52                # hip height of someone seated on a bench
SHED = (-7.0, 8.6)         # the old shed: x -8.5..-5.5, front face y 7.4, door at x -6.0
FENCE_Y = 14.0             # the white fence to the neighbor's yard
GH = (11.5, 14.0)          # Grandma's house (centre x, centre y); porch deck y 8.4..11 in front of it
PORCH = (11.5, 9.7)
NH = (-4.0, 21.5)          # the neighbor's yellow house; front face y 18.5
MAILBOX = (1.6, 16.6)
GLENN_FENCE = (-2.0, 14.55)
