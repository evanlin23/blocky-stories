"""Places shared by set.py and generator/make_story.py (metres; x east, y away from the gate, z up).

The gate is at (0, 0) in the fence line y = 0. The pavement is y -6..0, the road y -12..-6, the park lawns lie
beyond. Inside the fence are 17 small greens and the last green (x -3.2..3.2, y 19..31) with two tee mats at its
start, a bench and a lamp post on its east side and the windmill on its west. A character facing -y has yaw 0,
facing +x 90, facing -x -90, facing +y 180.
"""

ROWS = [
    (4.5, [-10, -6, -2, 2, 6, 10]),
    (9.6, [10, 6, 2, -2, -6, -10]),
    (14.4, [-8, -4, 0, 4, 8]),
]
HOLES = []                                   # (n, x, y), n = 1..17
_n = 1
for _y, _xs in ROWS:
    for _x in _xs:
        HOLES.append((_n, _x, _y))
        _n += 1

LAST = {"x0": -3.2, "x1": 3.2, "y0": 19.0, "y1": 31.0}
TEE_L = (-0.9, 19.9)                         # Dad's tee
TEE_R = (0.9, 19.9)                          # the second tee
CUP = (0.0, 29.6)
BENCH = (4.4, 24.0)
LAMP = (4.8, 27.5)
WINDMILL = (-8.8, 25.0)
KIOSK = (3.3, 1.7)
BALL_L = (-0.9, 20.9)
SHADOW_SIT = (2.6, 24.3)                     # the bun shadow on the last green

HOUSE = (-40.0, -38.0)                       # the front wall's middle (x, y)
BENCH_HOUSE = (-38.6, -39.4)
ROOM_A = (150.0, 0.0)                        # my bedroom
ROOM_B = (150.0, 12.0)                       # Dad's bedroom (and its hall to the south)
ROOM_C = (150.0, 28.0)                       # the kitchen
EX_DOOR = (-22.0, 2.0)                       # the ex's front door and step (facing -y)
PITCH = (34.0, -26.0)
LAWN_RAIL = (34.0, -19.4)
