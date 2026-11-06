"""Shared places for ep132 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0,
+x 90, +y 180, -x -90. The shelter stands on the north sidewalk (cameras look north at the bench); the street runs
east-west in front of it and the depot is across the street, its front face at y = DEPOT_Y facing north."""

SEAT_Z = 0.46            # the bench seat's top
SIT_Z = -0.05            # a seated character's z (legs level, resting on the seat)
BENCH_Y = 1.1            # where the seated characters sit (their centre line)
ME = (1.55, BENCH_Y)      # the bench's right end
TOL = (0.5, BENCH_Y)     # Mr. Tolley, on my left
WOM = (-0.5, BENCH_Y)    # the woman in the sun hat
MAN = (-1.5, BENCH_Y)    # the man in the scarf
NC = (1.95, BENCH_Y)     # the new commuter (S20, S21), me on her left
ME8 = (1.95, BENCH_Y)    # me, S08 to S13 (slid right so the chalk count fits beside the bench two-shot)
TOL8 = (0.9, BENCH_Y)   # Mr. Tolley beside me, S08 to S12
ME_NC = (0.95, BENCH_Y)  # me beside the new commuter (S21)
BOARD = (2.39, 1.55, 1.6)   # centre of the chalk board (face at y 1.52)

DEPOT_Y = -12.0          # the depot's front face
BUS_HALF = 4.5           # half the bus's length
BUS_SEAT_Z = 0.44        # a seated character's z on the bus's seats (seat top 0.95)
BUS_DRV = (0.55, -3.3)   # driver's seat, in bus-local x, y (the bus's nose is toward local -y)
BUS_FRONT = (-0.55, -3.3)  # the front seat on the door side
# bus states: (x, y, yaw degrees)
BUS_HIDE = (0.0, -19.5, 180.0)     # inside the depot, behind the shut door
BUS_IN = (0.0, -17.4, 180.0)       # door up: the nose just inside the mouth
BUS_MOUTH = (0.0, -16.2, 180.0)    # nose at the depot's mouth, driver at the wheel
BUS_STOP = (3.6, -3.45, -90.0)     # stopped at the shelter, heading west, front door on the north side
