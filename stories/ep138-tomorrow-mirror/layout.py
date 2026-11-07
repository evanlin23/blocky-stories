"""Shared places for ep138 "the gym where you see tomorrow" (make_story.py and set.py). x east, y north, z up.
A character facing -y has yaw 0, +x 90, +y 180, -x -90 (the camera looking west sees yaw 90 faces).
One small bright gym: x from -5 to 5, y from -6.5 to 4.5, ceiling 3.2. The mirror is on the EAST wall (x = 5) from
y -4.6 to 0.2, with thick chrome mullions (vertical bars) every 1.4 m and a pillar at each end. "The glass" is a
camera standing at the mirror (GCAM) looking west out into the same gym. The date board is on the WEST wall."""

H = 3.2
X0, X1, Y0, Y1 = -5.0, 5.0, -6.5, 4.5
MIR_X = 5.0                      # the wall's inner face
MIR_Y0, MIR_Y1 = -4.6, 0.2       # the mirror plate's extent
MULL = [0.2, -1.2, -2.6, -4.6]   # mullion centres (pillars at both ends)
M = (3.7, 0.9)                   # my real spot, beside the north end of the mirror (the pillar is just south of me)
GY = -1.8                        # the glass axis (y)
GCAM = (4.7, GY, 1.5)            # the camera at the mirror
T = (2.5, GY)                    # where the glass subject stands, facing east
BENCH = (-0.5, GY)               # Dre's bench (3 m behind the glass subject)
BOARD = (-4.97, 1.4, 1.7)        # the date board's centre (west wall)
WEN = (-3.9, 0.0)                # Big Wendell, beside the board
SIT_Z = -0.05
