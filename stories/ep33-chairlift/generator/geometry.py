"""Where things are on the lift (pure Python: make_story.py and set.py both read it, so a rider's feet and the chair
under them always agree). Metres. The line runs up +y from the bottom wheel at the origin to the top wheel at
y = LL. The up rope is at x = +1.8 and the down rope at x = -1.8. A chair faces the way it travels.

A position on the loop is `u`: 0..LL up the line, then half a turn round the top wheel, then down the line, then half a
turn round the bottom wheel (behind the loading deck, y < 0) back to 0.
"""
import math

R = 1.8            # both bull wheels
LL = 128.0         # the line, wheel to wheel
XU, XD = 1.8, -1.8
ARC = math.pi * R
TOT = 2 * LL + 2 * ARC
HANG = 1.9         # rope above a chair's seat top
SIDE = 0.72        # a rider's centre from the chair's centre
HIP_Y = 0.05       # a rider's hips, back from the chair's centre (chair front is -y at yaw 0)
ROOT_DZ = 0.17 - 0.68   # a seated rider's feet-root below the seat top (hips sit 0.17 above it)
ROPE = [(-5, 2.45), (0, 2.45), (3, 2.7), (22, 8.0), (50, 14.0), (80, 28.0), (108, 40.5), (128, 42.0), (140, 42.0)]
TOWERS = [22.0, 50.0, 80.0, 108.0]


def rope_z(y):
    if y <= ROPE[0][0]:
        return ROPE[0][1]
    for (y0, z0), (y1, z1) in zip(ROPE, ROPE[1:]):
        if y <= y1:
            return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
    return ROPE[-1][1]


def ground(x, y):
    """The land. Below zero is lake bed (the water plane is at 0)."""
    ramp = 0.48 * min(82.0, max(0.0, y - 40.0))
    if y > 140:
        ramp = max(0.0, ramp - 0.34 * (y - 140))
    side = 0.62 * max(0.0, abs(x) - 11.0 - 0.0 * y)
    if y > 40:
        side *= 1.0
    back = 0.4 if y < -13 else -3.0
    z = max(ramp, side, back)
    if y < 40 and ramp <= 0 and side <= 0 and back < 0:
        z = -3.0
    return z


def path(u):
    """(x, y, rope z, yaw) of a chair at loop position u. yaw 0 faces -y (the rig's convention)."""
    u = u % TOT
    if u < LL:
        x, y, dx, dy = XU, u, 0.0, 1.0
    elif u < LL + ARC:
        a = (u - LL) / R
        x, y = R * math.cos(a), LL + R * math.sin(a)
        dx, dy = -math.sin(a), math.cos(a)
    elif u < 2 * LL + ARC:
        x, y, dx, dy = XD, LL - (u - LL - ARC), 0.0, -1.0
    else:
        a = (u - 2 * LL - ARC) / R
        x, y = -R * math.cos(a), -R * math.sin(a)
        dx, dy = math.sin(a), -math.cos(a)   # the tangent of (-R cos a, -R sin a)
    return x, y, rope_z(y), math.atan2(dx, -dy)


def up(y):
    """Loop position of the up line at height y along it."""
    return y


def down(y):
    return LL + ARC + (LL - y)


def line_u(line, y):
    return up(y) if line == "up" else down(y)


def seat_root(cx, cy, seat_top, yaw, s):
    """A seated rider's feet-root for a chair centred at (cx, cy) with its seat top at seat_top, facing yaw, on its
    side s (+1/-1 along the rider's own x)."""
    c, sn = math.cos(yaw), math.sin(yaw)
    lx, ly = s * SIDE, HIP_Y
    return [round(cx + lx * c - ly * sn, 4), round(cy + lx * sn + ly * c, 4), round(seat_top + ROOT_DZ, 4)]


def rider(line, y, s):
    """(pos [x, y, z], yaw degrees) of a rider on the up/down line at y, side s."""
    x, yy, z, yaw = path(line_u(line, y))
    return seat_root(x, yy, z - HANG, yaw, s), math.degrees(yaw)


def rider_u(u, s):
    """(pos, yaw degrees) of a rider at loop position u (use for the wheels' arcs)."""
    x, y, z, yaw = path(u)
    return seat_root(x, y, z - HANG, yaw, s), math.degrees(yaw)


BOTTOM_ARC = 2 * LL + ARC       # u where the bottom half-turn starts
TOP_ARC = LL                    # u where the top half-turn starts
