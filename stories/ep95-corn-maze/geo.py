"""Shared places and path shapes for ep95-corn-maze (pure python: set.py and the generator both read it).

Every scene has its own origin so the shots never see each other (400 m apart, each on its own ground plane).
Local coordinates: x east, y away from the gate, z up. A layout is a set of path shapes on a 0.5 m cell grid.
"""
from __future__ import annotations

import math

CELL = 0.5
FW, FH = 40.0, 64.0

ORG = {"face": (0, 0), "partial": (1200, 0), "star": (0, 0), "tractor": (0, 0), "pig": (0, 0),
       "entrance": (400, 0), "day": (800, 0), "closed": (800, 0), "open": (800, 0),
       "summer": (1200, 0), "dawn": (1600, 0), "new": (2000, 0)}
SIZE = {"new": (20.0, 26.0)}


def W(scene, x, y, z=0.0):
    ox, oy = ORG[scene]
    return [round(ox + x, 3), round(oy + y, 3), z]


# ---------------------------------------------------------------------------------------------- shapes
def disc(cx, cy, r):
    return lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def ring(cx, cy, rx, ry, w):
    def f(x, y):
        d = math.hypot((x - cx) / rx, (y - cy) / ry)
        return abs(d - 1.0) * min(rx, ry) <= w / 2
    return f


def arc(cx, cy, r, a0, a1, w):
    def f(x, y):
        dx, dy = x - cx, y - cy
        d = math.hypot(dx, dy)
        a = math.degrees(math.atan2(dy, dx)) % 360
        lo, hi = a0 % 360, a1 % 360
        inside = lo <= a <= hi if lo <= hi else (a >= lo or a <= hi)
        if inside and abs(d - r) <= w / 2:
            return True
        for ang in (a0, a1):
            ex, ey = cx + r * math.cos(math.radians(ang)), cy + r * math.sin(math.radians(ang))
            if (x - ex) ** 2 + (y - ey) ** 2 <= (w / 2) ** 2:
                return True
        return False
    return f


def seg(x0, y0, x1, y1, w):
    def f(x, y):
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy or 1.0
        u = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / L2))
        return (x - (x0 + u * dx)) ** 2 + (y - (y0 + u * dy)) ** 2 <= (w / 2) ** 2
    return f


def poly(pts, w, closed=False):
    segs = [seg(*pts[i], *pts[i + 1], w) for i in range(len(pts) - 1)]
    if closed:
        segs.append(seg(*pts[-1], *pts[0], w))
    return lambda x, y: any(s(x, y) for s in segs)


def rect(x0, y0, x1, y1, w):
    return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], w, True)


def anyof(shapes):
    return lambda x, y: any(s(x, y) for s in shapes)


# ---------------------------------------------------------------------------------------------- the big maze + the face
EYE_L, EYE_R = (-6.2, 12.0), (6.6, 11.0)
HEAD = (0.0, -0.5, 14.5, 24.5)


def _wob(th):
    return 1 + 0.05 * math.sin(3 * th + 0.7) + 0.035 * math.sin(5 * th + 2.1) + 0.02 * math.sin(9 * th)


def maze_nodes(seed=95, na=13, nb=21):
    import random
    rnd = random.Random(seed)
    seen, edges, stack = {(0, 0)}, set(), [(0, 0)]
    while stack:
        a, b = stack[-1]
        nb_ = [(a + dx, b + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
               if 0 <= a + dx < na and 0 <= b + dy < nb and (a + dx, b + dy) not in seen]
        if not nb_:
            stack.pop()
            continue
        n = rnd.choice(nb_)
        seen.add(n)
        edges.add(frozenset(((a, b), n)))
        stack.append(n)
    for _ in range(14):
        a, b = rnd.randrange(na - 1), rnd.randrange(nb - 1)
        edges.add(frozenset(((a, b), rnd.choice(((a + 1, b), (a, b + 1))))))
    return edges


def maze_fn(w=FW, h=FH):
    edges = maze_nodes()

    def f(x, y):
        i, j = int((x + w / 2) / CELL), int((y + h / 2) / CELL)
        ua, va, a, b = i % 6, j % 6, i // 6, j // 6
        iu, iv = 1 <= ua <= 3, 1 <= va <= 3
        if iu and iv:
            return a < 13 and b < 21
        if iv and not iu:
            l = (i - 4) // 6
            return frozenset(((l, b), (l + 1, b))) in edges
        if iu and not iv:
            l = (j - 4) // 6
            return frozenset(((a, l), (a, l + 1))) in edges
        return False
    return f


def head_outside(x, y):
    cx, cy, rx, ry = HEAD
    th = math.atan2((y - cy) / ry, (x - cx) / rx)
    return math.hypot((x - cx) / rx, (y - cy) / ry) / _wob(th) > 1.0


def outline_band(x, y):
    cx, cy, rx, ry = HEAD
    th = math.atan2((y - cy) / ry, (x - cx) / rx)
    rho = math.hypot((x - cx) / rx, (y - cy) / ry) / _wob(th)
    if abs(rho - 1.0) * rx > 1.0:
        return False
    d = math.degrees(th) % 360
    return not any(lo <= d <= hi for lo, hi in ((20, 36), (98, 116), (158, 171), (222, 335)))


def eye_paths(c, outer, inner, gap_o, gap_i, tilt=0.0):
    ex, ey = c
    return [arc(ex, ey, outer, gap_o[1], gap_o[0] + 360, 1.9), arc(ex, ey, inner, gap_i[1], gap_i[0] + 360, 1.6),
            seg(ex + outer * math.cos(math.radians(200)), ey + outer * math.sin(math.radians(200)),
                ex + inner * math.cos(math.radians(200)), ey + inner * math.sin(math.radians(200)), 1.0),
            seg(ex + inner * math.cos(math.radians(40 + tilt)), ey + inner * math.sin(math.radians(40 + tilt)), ex, ey, 1.0),
            disc(ex, ey, 1.05)]


SMILE = [(-11.0, -10.4)] + [(11.0 * math.cos(math.radians(a)), -8.0 + 11.8 * math.sin(math.radians(a)))
                            for a in range(205, 336, 13)] + [(11.0, -10.4)]


def face_fn():
    mz = maze_fn()
    feats = []
    feats += eye_paths(EYE_L, 4.3, 2.3, (95, 130), (290, 325))
    ex, ey = EYE_R
    feats += [arc(ex, ey, 4.0, 110, 60 + 360, 1.9), arc(ex + 0.4, ey - 0.3, 2.0, 220, 130 + 360, 1.5),
              seg(ex + 4.0, ey - 1.0, ex + 4.0, ey - 3.2, 1.2), seg(ex - 3.5, ey + 1.9, ex - 3.5, ey + 3.6, 1.0),
              seg(ex + 2.0, ey - 0.1, ex + 0.4, ey - 0.3, 1.0), disc(ex + 0.9, ey + 0.4, 0.8)]
    # a wide plain smile: a crescent with upturned corners (a little flick up at each end)
    feats += [poly(SMILE, 2.7), seg(-11.0, -10.4, -11.5, -8.0, 2.2), seg(11.0, -10.4, 11.5, -8.0, 2.2)]
    for (sx, sy, ex2, ey2) in ((-3.4, -19.4, -3.4, -22.2), (4.4, -19.0, 4.8, -22.0), (0.6, -19.8, 0.6, -22.6),
                               (-8.8, -16.0, -9.6, -18.6)):
        feats.append(seg(sx, sy, ex2, ey2, 1.1))
    feats += [seg(-2.0, 3.0, 1.0, 3.0, 1.1), seg(1.0, 3.0, 1.0, -1.2, 1.1), seg(1.0, -1.2, 3.4, -1.2, 1.1),
              seg(-11.0, -3.0, -8.0, -3.0, 1.1), seg(-8.0, -3.0, -8.0, -6.2, 1.1), seg(9.0, 2.0, 6.0, 2.0, 1.1)]
    cx, cy, rx, ry = HEAD
    for ang, ln in ((60, 2.8), (205, 2.4), (130, 2.0)):
        th = math.radians(ang)
        p0 = (cx + rx * _wob(th) * math.cos(th), cy + ry * _wob(th) * math.sin(th))
        feats.append(seg(p0[0], p0[1], p0[0] - ln * math.cos(th), p0[1] - ln * math.sin(th), 1.1))
    return lambda x, y: (head_outside(x, y) and mz(x, y)) or outline_band(x, y) or any(f(x, y) for f in feats)


# ---------------------------------------------------------------------------------------------- the overhead shapes
def _pent(r, cx, cy):
    return [(cx + r * math.sin(math.radians(144 * k)), cy + r * math.cos(math.radians(144 * k))) for k in range(5)]


STAR_PTS = _pent(12.5, 0, 1.0)
STAR_PATH = [STAR_PTS[0], STAR_PTS[1], STAR_PTS[2], STAR_PTS[3], STAR_PTS[4], STAR_PTS[0]]
# a tractor from above: big rear wheels, a cab, a narrow hood, small front wheels
TR_RECTS = [(-3.2, -9.0, 3.2, 2.0), (-2.0, 2.0, 2.0, 12.5),
            (4.8, -10.5, 7.9, -1.5), (-7.9, -10.5, -4.8, -1.5), (3.6, 7.0, 5.8, 12.0), (-5.8, 7.0, -3.6, 12.0)]
TR_SEAT = (0.0, -3.5)
# a pig from above: a body, a head with two ears and a snout, four feet and a curl of tail
PIG_BODY = (-2.5, 0.0, 10.5, 7.0)


def pig_shapes():
    cx, cy, rx, ry = PIG_BODY
    return [ring(cx, cy, rx, ry, 1.8), ring(11.8, 0, 4.2, 4.2, 1.7), disc(16.0, 0, 1.7),
            poly([(10.5, 3.6), (11.4, 7.6), (13.6, 4.4)], 1.4), poly([(10.5, -3.6), (11.4, -7.6), (13.6, -4.4)], 1.4),
            disc(3.5, 8.6, 1.3), disc(-8.5, 7.0, 1.3), disc(3.5, -8.6, 1.3), disc(-8.5, -7.0, 1.3),
            arc(-14.5, 0, 2.0, 150, 330, 1.5)]


def surround(shape_list, rx=20.0, ry=26.0):
    mz = maze_fn()
    inner = anyof(shape_list)
    return [lambda x, y: (mz(x, y) and (x / rx) ** 2 + (y / ry) ** 2 > 1.0) or inner(x, y)]


# ---------------------------------------------------------------------------------------------- the day maze
CW = 2.6      # corridor width


def day_shapes(variant="day"):
    L_UP = seg(-9, 9.5, -9, 24, CW)
    clear = disc(-9, 26.4, 3.4)
    loop3 = poly([(-9, 14), (-17, 14), (-17, 28)], CW)
    if variant == "closed":
        return [L_UP, clear, loop3]
    if variant == "open":
        return [L_UP, clear, loop3, poly([(-9, 26.4), (-1.5, 26.4), (-1.5, 17), (5.5, 17), (5.5, 27), (12, 27)], CW)]
    return [seg(-12, -29.5, 12, -29.5, 5.0), seg(0, -29, 0, 6, CW), poly([(0, 6), (-9, 6), (-9, 24)], CW), clear,
            poly([(0, 6), (8, 6), (8, -29)], CW), disc(0, 8.4, 1.6), poly([(0, -14), (-12, -14), (-12, -4)], CW),
            poly([(8, -10), (15, -10), (15, 12)], CW), loop3]


# lanterns along the way, in the order they go out: the gate first, the exit one last
LANT_DAY = [(-1.9, -29.4), (0.95, -21), (-0.95, -16), (0.95, -11), (-0.95, -6), (0.95, -1), (-0.95, 3.2),
            (-4.2, 5.05), (-7.5, 6.95), (-8.05, 12.0), (-9.95, 17.0), (7.05, -26.2)]
LANT_NEW = [(-1.9, -9.0), (1.9, -9.0), (-5.2, -1.0), (3.4, 5.0)]
LANT_ENT = (0.3, 0.0)

# June's route in the day maze
FORK = (0.0, 6.0)
CLEAR = (-9.0, 26.4)
QUILT = (-9.0, 26.4)      # the quilt in the clearing
BALE = (10.4, -28.5)
PUMPKIN = (7.5, 3.4)
SCARE = (0.0, 8.5)


def summer_shapes():
    return [seg(-12, -29.5, 12, -29.5, 5.0),
            poly([(-4, -29), (-4, -20), (0, -12), (2, -4), (-3, 4), (-8, 10), (-8, 20)], 2.2)]


MOW = [(-4, -29), (-4, -20), (0, -12), (2, -4), (-3, 4), (-8, 10), (-8, 20)]


def dawn_shapes():
    return [seg(-12, -29.5, 12, -29.5, 5.0), seg(0, -29, 0, 24, CW), disc(0, 26.4, 3.4),
            poly([(0, -10), (-6, -10), (-6, 2)], CW)]


def new_shapes():
    return [seg(-8, -12, 8, -12, 3.0), poly([(0, -12), (0, -6), (-3.4, -2), (-3.4, 4), (1.5, 7.5), (1.5, 11)], 1.8),
            poly([(0, -6), (4.8, -4), (4.8, 2)], 1.8)]


NEW_SHOOTS = [(0, -9), (0.2, -6), (-0.8, -4.2), (-2.2, -2.6), (-3.2, -0.8), (-3.4, 1.4), (-3.2, 3.6), (-2.2, 5.4), (-0.6, 6.8), (1.0, 7.8)]


def entrance_shapes():
    return [seg(0, -40, 0, 0, 3.0), seg(0, 0, 8, 7, 3.0), seg(8, 7, 8, 40, 3.0)]


def layout_shapes(name):
    if name == "face":
        return [face_fn()]
    if name == "partial":
        return [arc(0, 3.0, 14.0, 215, 300, 2.4)]
    if name == "star":
        return surround([poly(STAR_PATH, 2.0), ring(0, 1.0, 15, 15, 1.7)])
    if name == "tractor":
        return surround([rect(*r, 1.5) for r in TR_RECTS] + [seg(-4.8, -6, 4.8, -6, 1.4), seg(-4.6, 9.5, 4.6, 9.5, 1.4)], 21, 27)
    if name == "pig":
        return surround(pig_shapes(), 21, 27)
    if name == "entrance":
        return entrance_shapes()
    if name in ("day", "closed", "open"):
        return day_shapes(name)
    if name == "summer":
        return summer_shapes()
    if name == "dawn":
        return dawn_shapes()
    if name == "new":
        return new_shapes()
    raise KeyError(name)
