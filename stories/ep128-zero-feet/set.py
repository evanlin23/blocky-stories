"""ep128 "zero feet": small still sets, each at its own origin (layout.py), and the rule meter: a cream tag in the
top-left corner of every frame with a house glyph, a footprint glyph and my number, 0.

Batch 13: nothing blinks, pulses, flickers or switches. Every light is steady for the whole film, day and night are
different places, and the windows are painted backdrops that never change. animate() only keeps the tag the same size
on screen whatever the lens, sits people down, and holds Mom in her frozen mid-step.
"""
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {}
LAND = G.LAND_Z
LIGHT = 0.3      # one knob for how bright every steady practical light is


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


class Pl:
    """A place: everything is added at its origin and its names carry a tag, so nothing collides."""

    def __init__(self, kit, O, tag):
        self.kit, self.O, self.tag = kit, O, tag

    def p(self, loc):
        return (self.O[0] + loc[0], self.O[1] + loc[1], loc[2])

    def box(self, n, size, loc, mat, bevel=0.0, rot=(0, 0, 0), parent=None):
        return self.kit.box(f"{self.tag}.{n}", size, self.p(loc) if parent is None else loc, mat, parent, rot, bevel)

    def cyl(self, n, r, h, loc, mat, rot=(0, 0, 0), nseg=16, r2=None, parent=None):
        return self.kit.cyl(f"{self.tag}.{n}", r, h, self.p(loc) if parent is None else loc, mat, parent, rot, nseg, r2)

    def sph(self, n, r, loc, mat, seg=10, parent=None):
        return self.kit.sphere(f"{self.tag}.{n}", r, self.p(loc) if parent is None else loc, mat, parent, seg)

    def empty(self, n, loc, rot=(0, 0, 0)):
        return self.kit.empty(f"{self.tag}.{n}", self.p(loc), None, rot)

    def light(self, n, loc, energy, hexc="#fff2e0", size=0.6):
        return self.kit.light(f"{self.tag}.{n}", "POINT", self.p(loc), energy * LIGHT, hexc, size=size, shadow=False)

    def wall_x(self, n, y, x0, x1, z0, z1, th, mat, holes=()):
        """A wall along x at y. holes: (a0, a1, zb, zt) in x."""
        cur = x0
        for i, (a0, a1, zb, zt) in enumerate(sorted(holes)):
            if a0 > cur:
                self.box(f"{n}.f{i}", (a0 - cur, th, z1 - z0), ((cur + a0) / 2, y, (z0 + z1) / 2), mat)
            if zb > z0:
                self.box(f"{n}.b{i}", (a1 - a0, th, zb - z0), ((a0 + a1) / 2, y, (z0 + zb) / 2), mat)
            if zt < z1:
                self.box(f"{n}.t{i}", (a1 - a0, th, z1 - zt), ((a0 + a1) / 2, y, (zt + z1) / 2), mat)
            cur = a1
        if x1 > cur:
            self.box(f"{n}.e", (x1 - cur, th, z1 - z0), ((cur + x1) / 2, y, (z0 + z1) / 2), mat)

    def wall_y(self, n, x, y0, y1, z0, z1, th, mat, holes=()):
        cur = y0
        for i, (a0, a1, zb, zt) in enumerate(sorted(holes)):
            if a0 > cur:
                self.box(f"{n}.f{i}", (th, a0 - cur, z1 - z0), (x, (cur + a0) / 2, (z0 + z1) / 2), mat)
            if zb > z0:
                self.box(f"{n}.b{i}", (th, a1 - a0, zb - z0), (x, (a0 + a1) / 2, (z0 + zb) / 2), mat)
            if zt < z1:
                self.box(f"{n}.t{i}", (th, a1 - a0, z1 - zt), (x, (a0 + a1) / 2, (zt + z1) / 2), mat)
            cur = a1
        if y1 > cur:
            self.box(f"{n}.e", (th, y1 - cur, z1 - z0), (x, (cur + y1) / 2, (z0 + z1) / 2), mat)


# ----------------------------------------------------------------------------------------------- glyphs and digits
SEG = {"0": "abcdef", "1": "bc", "3": "abcdghi", "9": "abcdfg"}


def seg7(add, ch, cx, cy, H, w, t):
    """Blocky digit made of bars. add(name, (sx, sy), (x, y)) draws one bar."""
    on = SEG[ch]
    hv = H / 2
    pos = {"a": ((w, t), (0, H / 2 - t / 2)), "d": ((w, t), (0, -H / 2 + t / 2)), "g": ((w - 2 * t, t), (0, 0)),
           "b": ((t, hv), (w / 2 - t / 2, H / 4)), "c": ((t, hv), (w / 2 - t / 2, -H / 4)),
           "f": ((t, hv), (-w / 2 + t / 2, H / 4)), "e": ((t, hv), (-w / 2 + t / 2, -H / 4)),
           # curled ends for the 3 (a short tick down from the top bar, up from the bottom bar), so it never reads as an E
           "h": ((t, 2 * t), (-w / 2 + t / 2, H / 2 - 1.5 * t)), "i": ((t, 2 * t), (-w / 2 + t / 2, -H / 2 + 1.5 * t))}
    for s in on:
        sz, (x, y) = pos[s]
        add(f"seg{s}", sz, (cx + x, cy + y))


def foot(add, cx, cy, s):
    """A footprint that reads as a sole: a ball, a narrow arch and a heel in one column, and five separate toe dots over
    a clear gap (so it never reads as a numeral)."""
    # a peanut-shaped sole (wide ball, narrow waist on the arch side, round heel) built from stacked bars
    for k, (dx, dy, w, h) in enumerate([(0.0, 0.3, 0.6, 0.14), (0.0, 0.16, 0.84, 0.16), (0.0, 0.0, 0.84, 0.17),
                                        (0.1, -0.16, 0.54, 0.16), (0.1, -0.31, 0.5, 0.15), (0.07, -0.46, 0.6, 0.16),
                                        (0.07, -0.61, 0.5, 0.14)]):
        add(f"sole{k}", (w * s, h * s), (cx + dx * s, cy + dy * s))
    for k, (dx, dy, w, h) in enumerate([(-0.3, 0.57, 0.19, 0.17), (-0.08, 0.65, 0.15, 0.15), (0.1, 0.65, 0.14, 0.14),
                                        (0.25, 0.61, 0.13, 0.13), (0.37, 0.55, 0.11, 0.11)]):
        add(f"toe{k}", (w * s, h * s), (cx + dx * s, cy + dy * s))


def house(add, cx, cy, s):
    add("base", (0.9 * s, 0.62 * s), (cx, cy - 0.22 * s))
    add("roof1", (0.95 * s, 0.16 * s), (cx - 0.24 * s, cy + 0.2 * s), 38)
    add("roof2", (0.95 * s, 0.16 * s), (cx + 0.24 * s, cy + 0.2 * s), -38)
    add("door", (0.2 * s, 0.34 * s), (cx, cy - 0.38 * s), 0, True)


def road(add, cx, cy, s):
    """A road going away: two slanted edges and three dashes."""
    add("l", (0.12 * s, 1.3 * s), (cx - 0.3 * s, cy), -14)
    add("r", (0.12 * s, 1.3 * s), (cx + 0.3 * s, cy), 14)
    for k, (yy, h) in enumerate([(-0.4, 0.22), (0.0, 0.18), (0.38, 0.14)]):
        add(f"d{k}", (0.1 * s, h * s), (cx, cy + yy * s))


def make_phone(kit, pl, n, loc, yaw, digits, glyph="foot", scale=1.0, flip=False):
    """A phone lying flat, screen up, top of the screen toward (-sin yaw, cos yaw). Blocky digits and a glyph only."""
    root = pl.empty(n, loc, (0, 0, yaw * D2R))
    root.scale = (scale, scale, scale)
    body = kit.plastic("#2a2d3a", 0.35, spec=0.5)
    screen = kit.emit("#fff1c4", 0.9, "phscreen")
    ink = kit.emit("#16222e", 1.0, "phink")
    pl.box(f"{n}.body", (0.26, 0.46, 0.03), (0, 0, 0.015), body, bevel=0.012, parent=root)
    pl.box(f"{n}.scr", (0.23, 0.42, 0.004), (0, 0, 0.0305), screen, parent=root)
    zl = 0.0345

    def add(name, size, xy, rot=0, dark=False):
        return pl.box(f"{n}.{name}", (size[0], size[1], 0.006), (xy[0], xy[1], zl), ink, parent=root,
                      rot=(0, 0, rot * D2R))

    nd = len(digits)
    H = 0.17 if nd < 3 else 0.12
    w = 0.1 if nd < 3 else 0.062
    pitch = w * 1.35
    x0 = -pitch * (nd - 1) / 2
    for i, ch in enumerate(digits):
        seg7(lambda nm, sz, xy, i=i: add(f"d{i}{nm}", sz, (-xy[0] if flip else xy[0], xy[1])), ch, x0 + i * pitch, -0.07, H, w, 0.022 if nd < 3 else 0.017)
    if glyph == "foot":
        foot(lambda nm, sz, xy, rot=0, dark=False: add(f"g{nm}", sz, xy, rot), -0.01, 0.125, 0.105)
    elif glyph == "road":
        road(lambda nm, sz, xy, rot=0, dark=False: add(f"g{nm}", sz, xy, rot), 0, 0.14, 0.15)
    return root


# ----------------------------------------------------------------------------------------------- the pieces
def basket(kit, pl, n, x, y, z, scale=1.0):
    wick = kit.plastic("#e0c28a", 0.8, spec=0.1)
    pl.box(f"{n}.base", (0.62 * scale, 0.46 * scale, 0.04), (x, y, z + 0.02), wick)
    for sx in (-1, 1):
        pl.box(f"{n}.sx{sx}", (0.04, 0.46 * scale, 0.34), (x + sx * 0.29 * scale, y, z + 0.19), wick)
    for sy in (-1, 1):
        pl.box(f"{n}.sy{sy}", (0.62 * scale, 0.04, 0.34), (x, y + sy * 0.21 * scale, z + 0.19), wick)
    cols = ["#7cc4ff", "#ff9ac8", "#ffd95a", "#b9a4f0", "#ffffff", "#9be15d"]
    for k in range(6):
        pl.box(f"{n}.sh{k}", (0.48 * scale, 0.34 * scale, 0.075), (x, y, z + 0.08 + k * 0.078), kit.plastic(cols[k], 0.8, spec=0.1), bevel=0.01)
        pl.box(f"{n}.sl{k}", (0.12 * scale, 0.34 * scale, 0.077), (x - 0.18 * scale, y, z + 0.08 + k * 0.078), kit.plastic(cols[(k + 3) % 6], 0.8, spec=0.1))


def laundry_pile(kit, pl, n, x, y, z):
    """A sky-blue plastic laundry basket heaped with folded coloured shirts (collars and sleeves), and a neat stack on the couch beside it."""
    bas = kit.plastic("#4f9fe8", 0.5, spec=0.25)
    pl.box(f"{n}.base", (0.7, 0.5, 0.05), (x, y, z + 0.025), bas, bevel=0.01)
    for sx in (-1, 1):
        pl.box(f"{n}.sx{sx}", (0.05, 0.5, 0.3), (x + sx * 0.325, y, z + 0.17), bas, bevel=0.01)
    for sy in (-1, 1):
        pl.box(f"{n}.sy{sy}", (0.7, 0.05, 0.3), (x, y + sy * 0.225, z + 0.17), bas, bevel=0.01)
        for k in range(3):
            pl.box(f"{n}.slot{sy}{k}", (0.12, 0.052, 0.07), (x - 0.2 + k * 0.2, y + sy * 0.225, z + 0.19), kit.plastic("#2f78c4", 0.5))
    cols = ["#ff7a5c", "#ffd95a", "#ffffff", "#ff9ac8", "#9be15d", "#b9a4f0"]
    for k in range(5):
        c = kit.plastic(cols[k], 0.8, spec=0.05)
        r = (0.16, -0.12, 0.2, -0.18, 0.1)[k]
        zz = z + 0.2 + k * 0.075
        pl.box(f"{n}.sh{k}", (0.5, 0.38, 0.07), (x + 0.015 * (k % 2), y, zz), c, rot=(0, 0, r), bevel=0.012)
        pl.box(f"{n}.sl{k}", (0.14, 0.3, 0.075), (x + (0.28 if k % 2 else -0.28) * math.cos(r), y + 0.0, zz), c, rot=(0, 0, r + 0.3), bevel=0.01)
        pl.box(f"{n}.co{k}", (0.14, 0.05, 0.078), (x + 0.0, y - 0.19, zz), kit.plastic(cols[(k + 2) % 6], 0.8), rot=(0, 0, r), bevel=0.008)
    # folded shirts on the couch seat beside it
    for k in range(3):
        pl.box(f"{n}.cs{k}", (0.42, 0.32, 0.07), (x + 0.8, y - 0.12, z + 0.035 + 0.075 * k), kit.plastic(["#7cc4ff", "#ff9a2e", "#ff7a5c"][k], 0.8), rot=(0, 0, 0.06 * (k - 1)), bevel=0.012)


def window_backdrop(kit, pl, n, x, y0, y1, z0, z1, night, faceplus=False, k=1.0):
    """A painted city behind a window on a side wall: steady, flat, never changing."""
    sky = kit.emit("#5a45cc" if night else "#8fd8ff", 1.0 if night else 1.1 * k, f"sky{int(night)}{int(k * 10)}")
    pl.box(f"{n}.sky", (0.05, y1 - y0, z1 - z0), (x, (y0 + y1) / 2, (z0 + z1) / 2), sky)
    cols = (["#2c2370", "#3a2f8a", "#261e66", "#40349a"] if night else ["#ffb59a", "#ffe08a", "#9be3c8", "#f6a8d0"])
    sgn = -1 if x < 0 else 1
    ww = (y1 - y0) / 4
    for k in range(4):
        h = 0.7 + 0.35 * ((k * 5) % 3)
        pl.box(f"{n}.bd{k}", (0.05, ww * 0.94, h), (x - sgn * 0.04, y0 + ww * (k + 0.5), z0 + h / 2 + 0.05),
               kit.emit(cols[k], 0.8, f"bd{k}{int(night)}"))
        if night:
            for r in range(2):
                pl.box(f"{n}.bw{k}{r}", (0.05, 0.12, 0.14), (x - sgn * 0.075, y0 + ww * (k + 0.5), z0 + 0.25 + r * 0.3),
                       kit.emit("#9a8aea", 0.7, "paintwin"))


def couch(kit, pl, n, cx, cy, z0, col, light_col):
    c = kit.plastic(col, 0.6, spec=0.15)
    c2 = kit.plastic(light_col, 0.6, spec=0.15)
    pl.box(f"{n}.base", (2.2, 0.9, 0.32), (cx, cy, z0 + 0.16), c, bevel=0.04)
    pl.box(f"{n}.seat", (1.8, 0.8, 0.12), (cx, cy - 0.04, z0 + 0.38), c2, bevel=0.04)
    pl.box(f"{n}.back", (2.2, 0.22, 0.6), (cx, cy + 0.34, z0 + 0.6), c, bevel=0.05)
    for sx in (-1, 1):
        pl.box(f"{n}.arm{sx}", (0.2, 0.9, 0.3), (cx + sx * 1.0, cy, z0 + 0.46), c, bevel=0.05)
    pl.box(f"{n}.pillow", (0.34, 0.12, 0.34), (cx - 0.82, cy + 0.2, z0 + 0.62), kit.plastic("#f6c453", 0.7), rot=(0, 0.2, 0.3), bevel=0.04)


def room_shell(kit, pl, n, x0, x1, y0, y1, z0, h, wall, floor, ceil, front_holes=(), left_holes=(), right_holes=(), back_holes=(), th=0.2):
    pl.box(f"{n}.floor", (x1 - x0 + 0.6, y1 - y0 + 0.6, 0.1), ((x0 + x1) / 2, (y0 + y1) / 2, z0 - 0.05), floor)
    pl.box(f"{n}.ceil", (x1 - x0 + 0.6, y1 - y0 + 0.6, 0.1), ((x0 + x1) / 2, (y0 + y1) / 2, z0 + h + 0.05), ceil)
    pl.wall_x(f"{n}.back", y1 + th / 2, x0 - th, x1 + th, z0, z0 + h, th, wall, back_holes)
    pl.wall_x(f"{n}.front", y0 - th / 2, x0 - th, x1 + th, z0, z0 + h, th, wall, front_holes)
    pl.wall_y(f"{n}.left", x0 - th / 2, y0, y1, z0, z0 + h, th, wall, left_holes)
    pl.wall_y(f"{n}.right", x1 + th / 2, y0, y1, z0, z0 + h, th, wall, right_holes)
    trim = kit.plastic("#ffffff", 0.7, spec=0.1)
    # a thin white crown line and skirting, so a ceiling shot still has an edge to read
    pl.box(f"{n}.crownB", (x1 - x0, 0.07, 0.1), ((x0 + x1) / 2, y1 - 0.035, z0 + h - 0.05), trim)
    pl.box(f"{n}.crownF", (x1 - x0, 0.07, 0.1), ((x0 + x1) / 2, y0 + 0.035, z0 + h - 0.05), trim)
    pl.box(f"{n}.crownL", (0.07, y1 - y0, 0.1), (x0 + 0.035, (y0 + y1) / 2, z0 + h - 0.05), trim)
    pl.box(f"{n}.crownR", (0.07, y1 - y0, 0.1), (x1 - 0.035, (y0 + y1) / 2, z0 + h - 0.05), trim)
    pl.box(f"{n}.skB", (x1 - x0, 0.05, 0.1), ((x0 + x1) / 2, y1 - 0.025, z0 + 0.05), trim)


def mom_kitchen(kit, pl, n, x, ya, yb, z0, cab_col, fridge_col, fridge_y):
    teal = kit.plastic(cab_col, 0.5, spec=0.2)
    cream = kit.plastic("#fff6e4", 0.5, spec=0.2)
    dark = kit.plastic("#2b2e36", 0.5, spec=0.3)
    yc = (ya + yb) / 2
    pl.box(f"{n}.cab", (0.9, yb - ya, 0.9), (x, yc, z0 + 0.45), teal, bevel=0.02)
    pl.box(f"{n}.top", (1.0, yb - ya + 0.1, 0.06), (x - 0.02, yc, z0 + 0.93), cream, bevel=0.02)
    for k in range(int((yb - ya) / 0.6)):
        pl.box(f"{n}.dl{k}", (0.012, 0.02, 0.78), (x - 0.456, ya + 0.6 * (k + 1), z0 + 0.46), kit.plastic("#1f8f82", 0.6))
    ys = ya + 0.8
    pl.box(f"{n}.hob", (0.5, 0.5, 0.012), (x, ys, z0 + 0.966), dark)
    for k, dy in enumerate((-0.12, 0.12)):
        pl.cyl(f"{n}.ring{k}", 0.1, 0.014, (x, ys + dy, z0 + 0.974), kit.plastic("#555a66", 0.4, spec=0.5), nseg=16)
        pl.cyl(f"{n}.ringin{k}", 0.055, 0.016, (x, ys + dy, z0 + 0.976), dark, nseg=16)
    fr = kit.plastic(fridge_col, 0.45, spec=0.35)
    pl.box(f"{n}.fridge", (0.9, 0.7, 1.9), (x, fridge_y, z0 + 0.95), fr, bevel=0.04)
    pl.box(f"{n}.fseam", (0.012, 0.66, 0.02), (x - 0.456, fridge_y, z0 + 1.3), kit.plastic("#b99a2a", 0.5))
    pl.box(f"{n}.fh1", (0.04, 0.04, 0.5), (x - 0.47, fridge_y - 0.25, z0 + 1.65), kit.plastic("#8a8f99", 0.3, spec=0.8))
    pl.box(f"{n}.fh2", (0.04, 0.04, 0.4), (x - 0.47, fridge_y - 0.25, z0 + 0.95), kit.plastic("#8a8f99", 0.3, spec=0.8))


# ----------------------------------------------------------------------------------------------- the apartment
def build_apt(kit, O, tag, night, boxes):
    pl = Pl(kit, O, tag)
    wall = kit.plastic("#f3e3c2" if night else "#f4ead8", 0.85, spec=0.05)
    floor = kit.planks("#c08f62", "#b2835a", 1.0) if night else kit.planks("#d9ab72", "#c99a62", 1.0)
    ceil = kit.plastic("#eadcbe" if night else "#dcd5e2", 0.9, spec=0.02)
    room_shell(kit, pl, "r", -3.0, 3.0, -1.2, 5.6, 0.0, 2.9, wall, floor, ceil,
               front_holes=[(-1.55, -0.65, 0.0, 2.2)], left_holes=[(1.4, 3.8, 0.9, 2.4)])
    white = kit.plastic("#ffffff", 0.6, spec=0.15)
    # the window: frame, sill, a mullion, and a painted backdrop outside
    pl.box("w.sill", (0.22, 2.6, 0.06), (-2.96, 2.6, 0.9), white)
    pl.box("w.head", (0.12, 2.5, 0.07), (-2.96, 2.6, 2.4), white)
    pl.box("w.mull", (0.1, 0.07, 1.5), (-2.97, 2.6, 1.65), white)
    pl.box("w.rail", (0.1, 2.4, 0.06), (-2.97, 2.6, 1.65), white)
    window_backdrop(kit, pl, "wd", -3.7, 0.9, 4.3, 0.3, 3.1, night)
    # my door to the stairs
    pl.box("door", (0.9, 0.08, 2.2), (-1.1, -1.22, 1.1), kit.plastic("#b8793f", 0.6, spec=0.15), bevel=0.02)
    pl.sph("knob", 0.045, (-0.8, -1.15, 1.05), kit.plastic("#e3b04b", 0.3, spec=0.7))
    if night:
        # a second painted dusk window over the couch (flat on the wall, steady): the night read behind my head
        sk = kit.emit("#5a45cc", 1.0, "sky10")
        pl.box("bwin.sky", (1.3, 0.02, 0.95), (-1.3, 5.585, 1.8), sk)
        for k, (bx, bh) in enumerate([(-1.82, 0.5), (-1.45, 0.72), (-1.1, 0.42), (-0.75, 0.6)]):
            pl.box(f"bwin.b{k}", (0.3, 0.02, bh), (bx + 0.08, 5.57, 1.325 + bh / 2), kit.emit(["#2c2370", "#3a2f8a", "#261e66", "#40349a"][k], 0.8, f"bd{k}1"))
        for nm, sz, lc in [("t", (1.42, 0.04, 0.06), (-1.3, 5.53, 2.3)), ("b", (1.42, 0.04, 0.06), (-1.3, 5.53, 1.3)),
                           ("l", (0.06, 0.04, 1.0), (-2.0, 5.53, 1.8)), ("r", (0.06, 0.04, 1.0), (-0.6, 5.53, 1.8)),
                           ("m", (0.04, 0.04, 0.95), (-1.3, 5.53, 1.8))]:
            pl.box(f"bwin.f{nm}", sz, lc, white)
    else:
        # a picture of colour blocks over the couch (no marks)
        pl.box("pic", (1.1, 0.04, 0.75), (-1.3, 5.56, 1.75), kit.plastic("#5a3b24", 0.7))
        for k, c in enumerate(["#ff7a5c", "#f6c453", "#2fb8a8"]):
            pl.box(f"pic{k}", (0.28, 0.02, 0.55), (-1.55 + k * 0.3, 5.53, 1.75), kit.plastic(c, 0.6))
    couch(kit, pl, "cch", -1.3, 5.05, 0.0, "#ff7a5c", "#ff9a80")
    pl.box("rug", (2.2, 1.8, 0.02), (-0.6, 2.7, 0.01), kit.plastic("#f6c453", 0.9, spec=0.02))
    pl.box("rug2", (1.8, 1.4, 0.022), (-0.6, 2.7, 0.011), kit.plastic("#ffd978", 0.9, spec=0.02))
    mom_kitchen(kit, pl, "k", 2.55, 0.9, 4.5, 0.0, "#2fb8a8", "#ffd95a", 5.25)
    basket(kit, pl, "bk", -2.3, 3.4, 0.0)
    make_phone(kit, pl, "phone", (2.5, 3.5, 0.96), -90, "0", "foot")
    make_phone(kit, pl, "cphone", G.PHONE_COUCH, 0, "0", "foot", scale=1.35)
    # a plain ceiling fixture and two ceiling beams, so a shot at the ceiling reads as a ceiling
    fx = kit.plastic("#f4f0fa", 0.6, spec=0.1)
    pl.cyl("cfix", 0.36, 0.09, (0.3, 3.0, 2.865), fx, nseg=24)
    pl.cyl("cdome", 0.24, 0.05, (0.3, 3.0, 2.82), fx, nseg=24)   # a plain fixture, never glowing
    for k, by in enumerate((1.7, 4.3)):
        pl.box(f"cbeam{k}", (5.9, 0.28, 0.07), (0.0, by, 2.865), kit.plastic("#dccfae" if night else "#f2eef8", 0.85))
    if boxes:
        card = kit.plastic("#d9a86a", 0.8, spec=0.05)
        tape = kit.plastic("#f0d9a0", 0.6)
        for k, (x, y, z, sx, sy, sz, r) in enumerate([(-0.9, 2.7, 0.25, 0.6, 0.5, 0.5, 0.1), (-0.2, 3.0, 0.2, 0.5, 0.45, 0.4, -0.15),
                                                    (-0.85, 2.7, 0.7, 0.5, 0.42, 0.4, -0.2), (0.5, 2.2, 0.22, 0.55, 0.5, 0.44, 0.3),
                                                    (-2.0, 1.6, 0.2, 0.5, 0.5, 0.4, 0.0), (1.2, 4.2, 0.22, 0.5, 0.5, 0.44, 0.2)]):
            pl.box(f"cb{k}", (sx, sy, sz), (x, y, z), card, rot=(0, 0, r), bevel=0.01)
            pl.box(f"cbt{k}", (0.1, sy + 0.01, 0.012), (x, y, z + sz / 2 + 0.005), tape, rot=(0, 0, r))
    # steady light. By night: the ceiling lamps are low, a warm key from the front lights my face, the dusk window glows violet
    warm = "#ffcf94" if night else "#fff3e0"
    dm = 0.55 if night else 1.0
    pl.light("k1", (-1.4, 2.0, 2.25), 520 * dm, warm)
    pl.light("k2", (1.4, 2.0, 2.25), 520 * dm, warm)
    pl.light("k3", (0.0, 4.1, 2.25), 460 * dm, warm)
    pl.light("f1", (0.0, 0.0, 1.9), 420 * (0.9 if night else 1.0), warm)
    pl.light("f2", (1.8, 0.0, 1.4), 220 * (0.8 if night else 1.0), warm)
    pl.light("f3", (-1.0, -0.6, 1.6), 200 * (0.8 if night else 1.0), warm)
    if night:
        pl.light("win", (-2.5, 2.6, 1.9), 150, "#9d86ff")      # violet only in the window
        pl.light("bwin", (-1.3, 4.6, 2.2), 50, "#a890ff")
        # a steady amber lamp by the couch
        pl.cyl("lamp.pole", 0.035, 1.3, (0.35, 5.2, 0.65), kit.plastic("#555a66", 0.4, spec=0.5), nseg=8)
        pl.cyl("lamp.base", 0.16, 0.04, (0.35, 5.2, 0.02), kit.plastic("#555a66", 0.4, spec=0.5), nseg=14)
        pl.cyl("lamp.shade", 0.24, 0.34, (0.35, 5.2, 1.45), kit.emit("#ffb54d", 0.7, "ambershade"), nseg=16, r2=0.16)
        pl.light("lamp", (0.2, 4.6, 1.5), 360, "#ffb25c", size=0.5)
    else:
        pl.light("win", (-2.5, 2.6, 1.9), 420, "#fff6e6")


# ----------------------------------------------------------------------------------------------- stairwell and flat
def build_stair(kit, O, tag, night, flat):
    pl = Pl(kit, O, tag)
    mint = kit.plastic("#bfeedd", 0.85, spec=0.05)
    white = kit.plastic("#fafafa", 0.7, spec=0.1)
    ceil = kit.plastic("#dcdad6" if not night else "#a9a0c8", 0.9, spec=0.02)
    wood = kit.plastic("#b8793f", 0.6, spec=0.15)
    brass = kit.plastic("#e3b04b", 0.3, spec=0.7)
    run = kit.plastic("#ff9a8a", 0.9, spec=0.02)
    top_z = 5.7
    # the shell: floor, left and right walls, front wall with my door, ceiling
    pl.box("fl0", (2.6, 3.4, 0.1), (0, -1.5, -0.05), kit.plastic("#f1e6d0", 0.8))
    pl.box("ceil", (2.8, 10.4, 0.1), (0, 1.5, top_z + 0.05), ceil)
    pl.wall_y("wl", -1.3, -3.4, 6.5, 0.0, top_z, 0.2, mint, holes=[(4.6, 6.0, 3.1, 5.0)])
    pl.wall_y("wr", 1.3, -3.4, 6.5, 0.0, top_z, 0.2, mint)
    pl.wall_x("wf", -3.3, -1.4, 1.4, 0.0, top_z, 0.2, mint, holes=[(-0.5, 0.5, 0.0, 2.2)])
    pl.box("mydoor", (1.0, 0.07, 2.2), (0, -3.2, 1.1), wood, bevel=0.02)
    pl.sph("myknob", 0.05, (0.35, -3.14, 1.05), brass)
    # the stairs and the landing
    for i in range(G.STEP_N):
        top = (i + 1) * G.STEP_DZ
        yc = i * G.STEP_DY + G.STEP_DY / 2
        pl.box(f"st{i}", (2.4, G.STEP_DY, top), (0, yc, top / 2), white)
        pl.box(f"run{i}", (1.1, G.STEP_DY - 0.04, 0.018), (0.0, yc, top + 0.009), run)
        pl.box(f"bal{i}", (0.05, 0.05, 0.85), (-1.0, yc, top + 0.425), white)
    pl.box("land", (2.4, 2.25, LAND), (0, 5.275, LAND / 2), kit.plastic("#f1e6d0", 0.8))
    ang = math.atan2(LAND - G.STEP_DZ, 4.2)
    ln = math.hypot(4.2, LAND - G.STEP_DZ)
    pl.box("rail", (0.07, ln, 0.07), (-1.0, 2.1, (LAND + G.STEP_DZ) / 2 + 0.85), white, rot=(ang, 0, 0))
    # the newel post at the foot, a brass cap with two mint strokes scratched on its front
    pl.box("newel", (0.26, 0.26, 1.05), (-1.0, -0.2, 0.525), white)
    pl.box("cap", (0.4, 0.4, 0.18), (-1.0, -0.2, 1.14), brass, bevel=0.01)
    for k in range(2):   # two thick dark-green strokes, 3 cm proud of the cap's front
        pl.box(f"cap{k}", (0.06, 0.03, 0.14), (-1.07 + k * 0.14, -0.415, 1.14), kit.plastic("#0b6b40", 0.5))
    # the landing window and its painted backdrop, the landing light (a fixture, always on)
    window_backdrop(kit, pl, "lw", -2.1, 4.6, 6.0, 3.1, 5.0, night, k=0.55)
    pl.box("lfix", (0.5, 0.5, 0.07), (0, 5.3, top_z - 0.04), kit.emit("#ffc070", 0.9 if not night else 1.1, "landlamp"))
    dm = 0.55 if night else 1.0
    pl.light("land", (0, 5.3, 4.95), 380 if not night else 330, "#ffc070", size=0.8)
    pl.light("mid", (0, 2.4, 4.5), 800 * dm, "#fff6e8")
    pl.light("low", (0, 0.4, 3.4), 700 * dm, "#ffffff")
    pl.light("foot", (0, -1.9, 3.0), 600 * (0.85 if night else 1.0), "#fff3df")
    # Mom's door at the top
    hinge = pl.empty("hinge", (-0.55, G.DOOR_Y - 0.0, LAND), (0, 0, (100 if flat else 0) * D2R))
    pl.box("leaf", (1.1, 0.08, 2.2), (0.55, 0, 1.1), kit.plastic("#b890e8", 0.6, spec=0.15), bevel=0.02, parent=hinge)
    pl.sph("pknob", 0.05, (0.95, 0.07, 1.05), brass, parent=hinge)
    pl.sph("pknobF", 0.075, (0.93, -0.1, 1.05), brass, parent=hinge)
    pl.box("pknobP", (0.12, 0.05, 0.12), (0.93, -0.06, 1.05), brass, bevel=0.01, parent=hinge)
    panel = kit.plastic("#8f63c4", 0.6, spec=0.1)
    for nm, zc, hh in (("a", 1.62, 0.8), ("b", 0.55, 0.7)):
        pl.box(f"ppan{nm}", (0.7, 0.03, hh), (0.5, -0.055, zc), panel, bevel=0.01, parent=hinge)
    frm = kit.plastic("#6a4328", 0.6, spec=0.1)
    for sx in (-1, 1):
        pl.box(f"dfr{sx}", (0.12, 0.1, 2.2), (sx * 0.61, G.DOOR_Y - 0.07, LAND + 1.1), frm, bevel=0.01)
    pl.box("dfrT", (1.34, 0.1, 0.12), (0, G.DOOR_Y - 0.07, LAND + 2.26), frm, bevel=0.01)
    if not flat:
        pl.wall_x("wb", 6.5, -1.4, 1.4, 0.0, top_z, 0.2, mint)
        return pl
    pl.wall_x("wb", 6.5, -3.1, 3.1, 0.0, top_z, 0.2, kit.plastic("#d6bff5", 0.85, spec=0.05), holes=[(-0.55, 0.55, LAND, LAND + 2.2)])
    # the lilac flat: same room as mine, a green couch, lamps already on
    z0 = LAND
    wall = kit.plastic("#dcc8f7", 0.85, spec=0.05)
    floor = kit.planks("#e8cfa6", "#dcc096", 1.0)
    ceil2 = kit.plastic("#f4efe9", 0.9, spec=0.02)
    pl.box("ffloor", (6.4, 5.8, 0.1), (0, 9.2, z0 - 0.05), floor)
    pl.box("fceil", (6.4, 5.8, 0.1), (0, 9.2, z0 + 2.95), ceil2)
    pl.wall_y("fl", -2.9, 6.4, 12.0, z0, z0 + 2.9, 0.2, wall, holes=[(8.3, 10.5, z0 + 0.9, z0 + 2.4)])
    pl.wall_y("fr", 3.0, 6.4, 12.0, z0, z0 + 2.9, 0.2, wall)
    pl.wall_x("fb", 12.1, -3.0, 3.0, z0, z0 + 2.9, 0.2, wall)
    trim = kit.plastic("#ffffff", 0.7, spec=0.1)
    for nm, sz, lc in [("cb", (5.9, 0.07, 0.1), (0, 12.0, z0 + 2.85)), ("cl", (0.07, 5.6, 0.1), (-2.88, 9.2, z0 + 2.85)),
                       ("cr", (0.07, 5.6, 0.1), (2.88, 9.2, z0 + 2.85)), ("cf", (5.9, 0.07, 0.1), (0, 6.5, z0 + 2.85))]:
        pl.box(nm, sz, lc, trim)
    pl.box("wsill", (0.2, 2.4, 0.06), (-2.86, 9.4, z0 + 0.9), trim)
    window_backdrop(kit, pl, "fw", -3.6, 7.8, 11.0, z0 + 0.3, z0 + 3.0, True)
    couch(kit, pl, "gcch", -1.3, 11.55, z0, "#6fcf7f", "#8fe09c")
    pl.box("frug", (2.4, 2.0, 0.02), (0.0, 9.4, z0 + 0.01), kit.plastic("#f4a7c9", 0.9, spec=0.02))
    mom_kitchen(kit, pl, "fk", 2.55, 7.2, 9.6, z0, "#9be0d0", "#ffe9a0", 11.55)
    # a round table set for two, her phone beside the plates
    tx, ty = 1.2, 10.4
    wood2 = kit.plastic("#c58b57", 0.6, spec=0.15)
    pl.cyl("tab", 0.62, 0.06, (tx, ty, z0 + 0.78), wood2, nseg=24)
    pl.cyl("tabl", 0.07, 0.75, (tx, ty, z0 + 0.38), wood2, nseg=10)
    pl.cyl("tabf", 0.3, 0.04, (tx, ty, z0 + 0.02), wood2, nseg=16)
    for k, sx in enumerate((-1, 1)):
        pl.cyl(f"pl{k}", 0.15, 0.015, (tx + sx * 0.3, ty - 0.12, z0 + 0.82), kit.plastic("#fffaf0", 0.4, spec=0.4), nseg=18)
        pl.cyl(f"plin{k}", 0.09, 0.017, (tx + sx * 0.3, ty - 0.12, z0 + 0.822), kit.plastic("#ffd0e0", 0.5), nseg=18)
        pl.cyl(f"cup{k}", 0.05, 0.1, (tx + sx * 0.3, ty + 0.22, z0 + 0.88), kit.plastic("#7cc4ff", 0.4, spec=0.5), nseg=12)
        pl.box(f"chair{k}", (0.42, 0.42, 0.06), (tx + sx * 0.8, ty - 0.1, z0 + 0.42), wood2)
        pl.box(f"chairb{k}", (0.42, 0.06, 0.45), (tx + sx * 0.8, ty + 0.12, z0 + 0.66), wood2)
        for lx in (-1, 1):
            for ly in (-1, 1):
                pl.box(f"chl{k}{lx}{ly}", (0.04, 0.04, 0.4), (tx + sx * 0.8 + lx * 0.18, ty - 0.1 + ly * 0.18, z0 + 0.2), wood2)
    make_phone(kit, pl, "mphone", (tx + 0.0, ty + 0.02, z0 + 0.815), 0, "0", "foot")
    laundry_pile(kit, pl, "fbk", -1.4, 11.1, z0 + 0.44)
    # floor lamps (steady shades) and the lights that make her room bright
    for k, (lx, ly) in enumerate([(-2.5, 7.4), (2.6, 11.6)]):
        pl.cyl(f"lp{k}", 0.04, 1.4, (lx, ly, z0 + 0.7), kit.plastic("#555a66", 0.4, spec=0.5), nseg=8)
        pl.cyl(f"ls{k}", 0.22, 0.34, (lx, ly, z0 + 1.55), kit.emit("#ffe9b0", 0.8, "flampshade"), nseg=16, r2=0.16)
    pl.light("fkey", (0.0, 9.6, z0 + 2.3), 230, "#fff0dc")
    pl.light("ffront", (0.0, 7.0, z0 + 2.0), 200, "#fff4e6")
    pl.light("ffront2", (-1.2, 7.4, z0 + 1.6), 100, "#fff4e6")
    pl.light("fback", (0.0, 11.3, z0 + 2.2), 120, "#fff0dc")
    pl.light("fwin", (-2.5, 9.4, z0 + 1.9), 100, "#c9bcff")
    return pl


# ----------------------------------------------------------------------------------------------- the small places
def build_fridge(kit, O):
    pl = Pl(kit, O, "fg")
    teal = kit.plastic("#2fb8a8", 0.7, spec=0.1)
    pl.box("floor", (9, 7, 0.1), (0, 1.0, -0.05), kit.planks("#d9ab72", "#c99a62", 1.0))
    pl.box("wall", (9, 0.2, 3.2), (0, 3.25, 1.6), teal)
    pl.box("wallL", (0.2, 7, 3.2), (-4.5, 1.0, 1.6), teal)
    pl.box("wallR", (0.2, 7, 3.2), (4.5, 1.0, 1.6), kit.plastic("#f4ead8", 0.85, spec=0.05))
    pl.box("ceil", (9, 7, 0.1), (0, 1.0, 3.25), kit.plastic("#f1ede6", 0.9, spec=0.02))
    shell = kit.plastic("#fbfcff", 0.5, spec=0.4)
    yel = kit.plastic("#ffd95a", 0.45, spec=0.35)
    pl.box("back", (1.3, 0.05, 2.0), (0, 3.0, 1.0), shell)
    for sx in (-1, 1):
        pl.box(f"side{sx}", (0.06, 0.85, 2.0), (sx * 0.62, 2.6, 1.0), yel)
    pl.box("top", (1.3, 0.85, 0.06), (0, 2.6, 2.03), yel)
    pl.box("bot", (1.3, 0.85, 0.08), (0, 2.6, 0.04), shell)
    sh = kit.plastic("#d6ecfb", 0.4, spec=0.5)
    for z in (0.78, 1.2, 1.62):
        pl.box(f"shelf{z}", (1.2, 0.8, 0.03), (0, 2.6, z), sh)
    # the door, open toward us on the left hinge
    hinge = pl.empty("hinge", (-0.66, 2.18, 0), (0, 0, -105 * D2R))
    pl.box("leaf", (1.3, 0.1, 2.0), (0.65, 0, 1.0), yel, bevel=0.03, parent=hinge)
    pl.box("lin", (1.2, 0.06, 1.9), (0.65, 0.07, 1.0), shell, parent=hinge)
    for z in (0.5, 1.0, 1.5):
        pl.box(f"dsh{z}", (1.1, 0.16, 0.03), (0.65, 0.16, z), sh, parent=hinge)
        for k in range(5):
            c = ["#ff7a5c", "#9be15d", "#7cc4ff", "#f6c453", "#ff9ac8"][(k + int(z * 2)) % 5]
            pl.cyl(f"bot{z}{k}", 0.05, 0.28, (0.2 + k * 0.2, 0.18, z + 0.16), kit.plastic(c, 0.4, spec=0.5), nseg=10, parent=hinge)
    # full and neat: rows on every shelf, drawers at the bottom
    white = kit.plastic("#ffffff", 0.4, spec=0.4)
    for z, items in [(0.795, "milk"), (1.215, "eggs"), (1.635, "fruit")]:
        if items == "milk":
            for k in range(4):
                pl.box(f"milk{k}", (0.15, 0.13, 0.28), (-0.48 + k * 0.17, 2.4, z + 0.14), white, bevel=0.01)
                pl.box(f"milkc{k}", (0.15, 0.13, 0.07), (-0.48 + k * 0.17, 2.4, z + 0.31), kit.plastic("#4f8fe8", 0.5), bevel=0.01)
            for k in range(3):
                pl.box(f"juice{k}", (0.14, 0.12, 0.24), (0.22 + k * 0.17, 2.4, z + 0.12), kit.plastic("#ff9a2e", 0.5), bevel=0.01)
            for k in range(5):
                pl.cyl(f"yog{k}", 0.05, 0.09, (-0.48 + k * 0.12, 2.68, z + 0.05), kit.plastic(["#ffb3c8", "#fff0a8"][k % 2], 0.5), nseg=10)
        elif items == "eggs":
            for r in range(2):
                for k in range(6):
                    pl.sph(f"egg{r}{k}", 0.05, (-0.5 + k * 0.11, 2.4 + r * 0.12, z + 0.05), kit.plastic("#fff3d6", 0.5), seg=8)
            for k in range(3):
                pl.box(f"tup{k}", (0.3, 0.24, 0.1), (0.3, 2.45 + 0.0, z + 0.05 + 0.1 * k), kit.plastic("#cfe9f7", 0.4, spec=0.5), bevel=0.01)
                pl.box(f"tupl{k}", (0.31, 0.25, 0.025), (0.3, 2.45, z + 0.1 + 0.1 * k), kit.plastic(["#ff7a5c", "#9be15d", "#b9a4f0"][k], 0.5))
            pl.box("cheese", (0.22, 0.18, 0.1), (-0.3, 2.78, z + 0.05), kit.plastic("#ffd23f", 0.5), bevel=0.02)
        else:
            for k in range(8):
                pl.sph(f"fru{k}", 0.06, (-0.5 + k * 0.13, 2.42 + 0.1 * (k % 2), z + 0.06), kit.plastic(["#e8493a", "#9be15d", "#ff9a2e", "#e8493a"][k % 4], 0.4), seg=8)
            for k in range(3):
                pl.cyl(f"jar{k}", 0.06, 0.15, (-0.35 + k * 0.17, 2.74, z + 0.08), kit.plastic("#f6c453", 0.4, spec=0.5), nseg=10)
    for k, c in enumerate(["#8fd77b", "#ffa94d"]):
        pl.box(f"drawer{k}", (0.58, 0.7, 0.4), (-0.3 + k * 0.6, 2.6, 0.3), kit.plastic(c, 0.5, spec=0.3), bevel=0.02)
    pl.light("in", (0.0, 2.45, 1.5), 140, "#ffffff", size=0.3)
    pl.light("key", (0.0, 0.2, 2.2), 900, "#fff3e0")
    pl.light("key2", (-1.2, 0.0, 1.4), 400, "#fff3e0")


def build_den(kit, O):
    pl = Pl(kit, O, "dn")
    wall = kit.plastic("#efd9b0", 0.85, spec=0.05)
    pl.box("floor", (7.2, 7.0, 0.1), (0, 2.3, -0.05), kit.planks("#a7703f", "#946236", 1.0))
    pl.box("ceil", (7.2, 7.0, 0.1), (0, 2.3, 2.85), kit.plastic("#f1ede6", 0.9, spec=0.02))
    pl.wall_x("back", 5.2, -3.4, 3.4, 0.0, 2.8, 0.2, wall)
    pl.wall_x("front", -1.3, -3.4, 3.4, 0.0, 2.8, 0.2, wall)
    pl.wall_y("left", -3.3, -1.2, 5.2, 0.0, 2.8, 0.2, wall)
    pl.wall_y("right", 3.3, -1.2, 5.2, 0.0, 2.8, 0.2, wall)
    pl.box("wain", (6.6, 0.05, 0.9), (0, 5.07, 0.45), kit.plastic("#b88a5a", 0.7))
    pl.box("rug", (3.0, 2.2, 0.02), (0.6, 3.4, 0.01), kit.plastic("#c04a4a", 0.9, spec=0.02))
    brown = kit.plastic("#6b3f26", 0.65, spec=0.15)
    brown2 = kit.plastic("#8d5a38", 0.65, spec=0.15)
    cx, cy = 0.6, 4.2
    pl.box("cbase", (1.3, 1.1, 0.32), (cx, cy, 0.16), brown, bevel=0.04)
    pl.box("cseat", (1.0, 1.0, 0.12), (cx, cy - 0.02, 0.38), brown2, bevel=0.04)
    pl.box("cback", (1.5, 0.22, 1.15), (cx, 4.82, 0.75), brown, bevel=0.05)
    pl.box("cpanel", (0.9, 0.04, 0.8), (cx, 4.69, 0.8), brown2, bevel=0.02)
    pl.box("clarm", (0.22, 1.1, 0.34), (-0.05, cy, 0.46), brown, bevel=0.04)
    pl.box("crarm", (0.46, 1.1, 0.34), (1.27, cy, 0.46), brown, bevel=0.04)
    make_phone(kit, pl, "phone", (1.25, 4.0, 0.63), 0, "3", "foot", scale=1.3)
    # a bookshelf of colour blocks, a painting of blocks, a plant, a lamp
    pl.box("shelf", (1.5, 0.35, 2.0), (-2.2, 4.95, 1.0), kit.plastic("#8d5a38", 0.7))
    for r in range(4):
        for k in range(7):
            pl.box(f"bk{r}{k}", (0.15, 0.26, 0.3), (-2.8 + k * 0.17, 4.78, 0.45 + r * 0.45), kit.plastic(["#e8584a", "#2fb8a8", "#f6c453", "#4f8fe8", "#9be15d"][(r + k) % 5], 0.6))
    pl.box("frm", (1.0, 0.04, 0.7), (2.3, 5.07, 1.7), kit.plastic("#5a3b24", 0.7))
    for k, c in enumerate(["#4f8fe8", "#f6c453", "#e8584a"]):
        pl.box(f"fb{k}", (0.26, 0.02, 0.55), (2.0 + k * 0.3, 5.04, 1.7), kit.plastic(c, 0.6))
    pl.cyl("pot", 0.2, 0.3, (2.7, 4.5, 0.15), kit.plastic("#e8845a", 0.7), nseg=12)
    pl.sph("leaf", 0.4, (2.7, 4.5, 0.75), kit.plastic("#4faf5a", 0.7), seg=10)
    pl.cyl("lpole", 0.03, 1.4, (-1.3, 4.5, 0.7), kit.plastic("#444444", 0.5, spec=0.4), nseg=8)
    pl.cyl("lshade", 0.2, 0.3, (-1.3, 4.5, 1.5), kit.emit("#fff0c8", 1.4, "lampshade"), nseg=14, r2=0.14)
    for k, (x, y, e) in enumerate([(-1.5, 2.0, 520), (1.5, 2.0, 520), (0.4, 4.0, 360)]):
        pl.light(f"l{k}", (x, y, 2.2), e, "#ffe6c4")
    pl.light("fill", (0.4, 0.0, 1.8), 460, "#fff0dc")


def build_diner(kit, O):
    pl = Pl(kit, O, "dr")
    pl.box("floor", (7.2, 8.4, 0.1), (0, 2.6, -0.05), kit.checker("#f7f7f2", "#2fb8a8", 1.0))
    pl.box("ceil", (7.2, 8.4, 0.1), (0, 2.6, 3.05), kit.plastic("#f1ede6", 0.9, spec=0.02))
    wall = kit.plastic("#ffe3b3", 0.85, spec=0.05)
    pl.wall_x("back", 6.5, -3.4, 3.4, 0.0, 3.0, 0.2, wall)
    pl.wall_x("front", -1.3, -3.4, 3.4, 0.0, 3.0, 0.2, wall)
    pl.wall_y("left", -3.3, -1.2, 6.5, 0.0, 3.0, 0.2, wall)
    pl.wall_y("right", 3.3, -1.2, 6.5, 0.0, 3.0, 0.2, wall)
    pl.box("band", (6.6, 0.05, 0.4), (0, 6.37, 1.6), kit.plastic("#e8584a", 0.6))
    pl.box("band2", (6.6, 0.05, 0.12), (0, 6.37, 2.05), kit.plastic("#2fb8a8", 0.6))
    coral = kit.plastic("#ff7a5c", 0.5, spec=0.25)
    pl.box("cbase", (6.0, 0.7, 0.95), (0, 3.4, 0.475), coral, bevel=0.02)
    pl.box("ctop", (6.2, 0.95, 0.06), (0, 3.4, 0.98), kit.plastic("#fff6e4", 0.4, spec=0.3), bevel=0.02)
    pl.cyl("saucer", 0.12, 0.01, (0.05, 3.4, 1.016), kit.plastic("#ffffff", 0.3, spec=0.5), nseg=16)
    pl.cyl("cup", 0.07, 0.1, (0.05, 3.4, 1.07), kit.plastic("#7cc4ff", 0.4, spec=0.5), nseg=12)
    make_phone(kit, pl, "phone", (0.75, 3.4, 1.015), 0, "900", "road")
    # the stool he sits on, shelves, a machine, lamps
    pl.cyl("stool", 0.28, 0.06, (0, 4.4, 0.41), kit.plastic("#e8584a", 0.5, spec=0.3), nseg=16)
    pl.cyl("stoolleg", 0.05, 0.4, (0, 4.4, 0.2), kit.plastic("#8a8f99", 0.3, spec=0.7), nseg=8)
    for z in (1.4, 2.0):
        pl.box(f"sh{z}", (5.0, 0.4, 0.06), (0, 6.25, z), kit.plastic("#b88a5a", 0.7))
        for k in range(12):
            pl.box(f"jar{z}{k}", (0.22, 0.2, 0.3), (-2.4 + k * 0.43, 6.25, z + 0.18), kit.plastic(["#f6c453", "#e8584a", "#4f8fe8", "#9be15d"][k % 4], 0.5))
    pl.box("mach", (0.6, 0.5, 0.7), (2.4, 5.6, 1.35), kit.plastic("#2b2e36", 0.4, spec=0.5), bevel=0.03)
    pl.box("machr", (0.62, 0.52, 0.12), (2.4, 5.6, 1.7), kit.plastic("#e8584a", 0.5))
    for k, x in enumerate((-1.6, 1.6)):
        pl.cyl(f"pend{k}", 0.3, 0.2, (x, 3.8, 2.5), kit.emit("#fff0c8", 1.3, "pendant"), nseg=16, r2=0.12)
        pl.cyl(f"pendw{k}", 0.015, 0.5, (x, 3.8, 2.85), kit.plastic("#333333", 0.5), nseg=6)
    for k, (x, y, e) in enumerate([(-1.6, 2.2, 520), (1.6, 2.2, 520), (0.0, 4.6, 380)]):
        pl.light(f"l{k}", (x, y, 2.3), e, "#fff0dc")
    pl.light("fill", (0.0, 0.0, 1.9), 460, "#fff6e8")


def build_hall(kit, O, tag, night):
    pl = Pl(kit, O, tag)
    wall = kit.plastic("#e6c2c8" if night else "#ffd9b8", 0.85, spec=0.05)
    pl.box("floor", (2.6, 8.4, 0.1), (0, 3.8, -0.05), kit.planks("#d9ab72", "#c99a62", 1.0))
    pl.box("ceil", (2.6, 8.4, 0.1), (0, 3.8, 2.85), kit.plastic("#f1ede6", 0.9, spec=0.02))
    pl.wall_y("left", -1.1, 0, 7.7, 0.0, 2.8, 0.2, wall)
    pl.wall_y("right", 1.1, 0, 7.7, 0.0, 2.8, 0.2, wall, holes=[(3.8, 5.6, 0.9, 2.2)])
    pl.wall_x("front", -0.1, -1.2, 1.2, 0.0, 2.8, 0.2, wall)
    pl.wall_x("end", 7.8, -1.2, 1.2, 0.0, 2.8, 0.2, wall, holes=[(-0.45, 0.45, 0.0, 2.1)])
    white = kit.plastic("#ffffff", 0.6, spec=0.15)
    pl.box("wsill", (0.2, 1.9, 0.06), (1.0, 4.7, 0.9), white)
    window_backdrop(kit, pl, "hw", 1.7, 3.8, 5.6, 0.3, 2.6, night)
    pl.box("skirt", (0.04, 7.6, 0.1), (-0.98, 3.8, 0.05), white)
    # Mom's door at the end, open on a small warm room
    pl.box("frame", (1.0, 0.1, 0.08), (0, 7.74, 2.12), white)
    hinge = pl.empty("hinge", (-0.45, 7.7, 0), (0, 0, 105 * D2R))
    pl.box("leaf", (0.9, 0.08, 2.1), (0.45, 0, 1.05), kit.plastic("#d4b8f2", 0.6, spec=0.15), bevel=0.02, parent=hinge)
    rw = kit.plastic("#ffe7a0", 0.85, spec=0.05)
    pl.box("rfloor", (3.4, 3.2, 0.1), (0, 9.3, -0.05), kit.planks("#e8cfa6", "#dcc096", 1.0))
    pl.box("rback", (3.4, 0.2, 2.8), (0, 10.9, 1.4), rw)
    pl.box("rl", (0.2, 3.2, 2.8), (-1.7, 9.3, 1.4), rw)
    pl.box("rr", (0.2, 3.2, 2.8), (1.7, 9.3, 1.4), rw)
    pl.box("rceil", (3.4, 3.2, 0.1), (0, 9.3, 2.85), kit.plastic("#f4efe9", 0.9, spec=0.02))
    pl.box("rbed", (1.3, 1.9, 0.5), (0.6, 10.0, 0.25), kit.plastic("#f4a7c9", 0.8))
    pl.box("rpil", (0.9, 0.35, 0.18), (0.6, 10.7, 0.59), white)
    pl.light("room", (0, 9.2, 2.2), 520, "#ffd9a0")
    pl.light("rdoor", (0, 7.2, 2.1), 220, "#ffd9a0")
    # my childhood desk with the old phone, a lamp, books
    wood = kit.plastic("#c58b57", 0.6, spec=0.15)
    pl.box("desk", (0.6, 1.5, 0.06), (-0.72, 2.8, 0.75), wood)
    for sx in (-1, 1):
        for sy in (-1, 1):
            pl.box(f"dl{sx}{sy}", (0.05, 0.05, 0.72), (-0.72 + sx * 0.25, 2.8 + sy * 0.65, 0.36), wood)
    make_phone(kit, pl, "phone", (-0.7, 2.7, 0.78), 90, "10", "foot")
    for k, c in enumerate(["#e8584a", "#4f8fe8", "#f6c453"]):
        pl.box(f"book{k}", (0.22, 0.3, 0.05), (-0.8, 3.3, 0.805 + 0.05 * k), kit.plastic(c, 0.6))
    pl.cyl("dlp", 0.02, 0.3, (-0.9, 2.1, 0.93), kit.plastic("#444444", 0.5), nseg=8)
    pl.cyl("dls", 0.12, 0.12, (-0.9, 2.1, 1.12), kit.emit("#fff0c8", 1.3, "lampshade"), nseg=12, r2=0.06)
    for k, c in enumerate(["#4f8fe8", "#f6c453", "#e8584a", "#9be15d"]):
        pl.box(f"pst{k}", (0.03, 0.3, 0.3), (-1.0, 2.4 + 0.36 * k, 1.7), kit.plastic(c, 0.6))
    warm = "#ffd7a8" if night else "#fff3e0"
    hd = 0.5 if night else 1.0
    pl.light("h1", (0, 1.4, 2.35), 420 * hd, warm)
    pl.light("h2", (0, 4.4, 2.35), 420 * hd, warm)
    pl.light("h3", (0.6, 2.8, 1.8), 220 * hd, warm)
    pl.light("h0", (0.2, 0.4, 1.9), 320 * (0.8 if night else 1.0), warm)
    if night:
        pl.light("hwin", (0.6, 4.7, 1.8), 260, "#9d86ff")


def build_car(kit, O):
    pl = Pl(kit, O, "car")
    pl.box("ground", (40, 40, 0.1), (0, 0, -0.05), kit.plastic("#8fc98a", 0.9, spec=0.02))
    pl.box("road", (6.0, 40, 0.02), (0, 0, 0.01), kit.plastic("#8e939c", 0.9, spec=0.02))
    red = kit.plastic("#e8584a", 0.35, spec=0.5)
    dark = kit.plastic("#2b2e36", 0.5, spec=0.3)
    pl.box("floor", (2.0, 4.4, 0.2), (0, -0.4, 0.3), red, bevel=0.03)
    pl.box("hood", (2.0, 1.9, 0.3), (0, -2.0, 0.85), red, bevel=0.04)
    pl.box("dash", (1.96, 0.6, 0.5), (0, -1.05, 0.8), dark, bevel=0.04)
    for sx in (-1, 1):
        pl.box(f"door{sx}", (0.1, 2.6, 0.8), (sx * 0.98, 0.3, 0.7), red, bevel=0.03)
        pl.box(f"pillar{sx}", (0.1, 0.1, 1.25), (sx * 0.95, -0.55, 1.5), red, rot=(-0.65, 0, 0))
        pl.box(f"rpil{sx}", (0.1, 0.12, 1.15), (sx * 0.95, 1.7, 1.5), red)
    pl.box("roof", (2.0, 2.2, 0.08), (0, 0.65, 2.02), red, bevel=0.03)
    pl.box("header", (2.0, 0.14, 0.12), (0, -0.2, 1.97), red)
    # seats: me on the left, packed boxes on the right and behind
    seat = kit.plastic("#4f6a8f", 0.7, spec=0.1)
    pl.box("dseat", (0.7, 0.65, 0.3), (-0.45, 0.35, 0.3), seat, bevel=0.04)
    pl.box("dback", (0.7, 0.2, 0.95), (-0.45, 0.85, 0.85), seat, bevel=0.05)
    pl.box("pseat", (0.7, 0.65, 0.3), (0.5, 0.35, 0.3), seat, bevel=0.04)
    card = kit.plastic("#d9a86a", 0.8, spec=0.05)
    tape = kit.plastic("#f0d9a0", 0.6)
    for k, (x, y, z, sx, sy, sz) in enumerate([(0.5, 0.3, 0.7, 0.6, 0.55, 0.6), (0.45, 0.35, 1.25, 0.5, 0.5, 0.5), (-0.4, 1.4, 0.8, 0.7, 0.6, 0.7),
                                               (0.45, 1.4, 0.75, 0.7, 0.6, 0.6), (0.0, 1.45, 1.4, 0.8, 0.55, 0.5), (-0.45, 1.5, 1.85, 0.5, 0.4, 0.4)]):
        pl.box(f"cb{k}", (sx, sy, sz), (x, y, z), card, rot=(0, 0, 0.08 * (k % 3 - 1)), bevel=0.01)
        pl.box(f"cbt{k}", (0.1, sy + 0.01, 0.012), (x, y, z + sz / 2 + 0.005), tape)
    # the wheel: a ring of blocks facing the driver
    wheel = pl.empty("wheel", (-0.45, -0.5, 1.12), (-0.5, 0, 0))
    ring = kit.plastic("#2b2e36", 0.5, spec=0.3)
    for k in range(14):
        a = 2 * math.pi * k / 14
        pl.box(f"wr{k}", (0.12, 0.05, 0.05), (0.2 * math.cos(a), 0, 0.2 * math.sin(a)), ring, rot=(0, -(a + math.pi / 2), 0), parent=wheel)
    pl.cyl("hub", 0.06, 0.06, (0, 0, 0), ring, rot=(math.pi / 2, 0, 0), nseg=10, parent=wheel)
    pl.box("spoke", (0.4, 0.04, 0.04), (0, 0, 0), ring, parent=wheel)
    pl.light("k", (0.0, -3.6, 3.4), 1400, "#fff3e0", size=1.0)
    pl.light("k2", (-1.0, -2.0, 2.5), 600, "#ffffff", size=0.8)
    pl.light("in", (0.0, 0.0, 1.8), 300, "#fff3e0")


# ----------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    build_apt(kit, G.APT_D, "ad", False, False)
    build_apt(kit, G.APT_B, "ab", False, True)
    build_apt(kit, G.APT_N, "an", True, False)
    build_stair(kit, G.ST_D, "sd", False, False)
    build_stair(kit, G.ST_N, "sn", True, True)
    build_fridge(kit, G.FRIDGE)
    build_den(kit, G.DEN)
    build_diner(kit, G.DINER)
    build_hall(kit, G.HALL_D, "hd", False)
    build_hall(kit, G.HALL_N, "hn", True)
    build_car(kit, G.CAR)
    build_tag(kit)
    return {}


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def build_tag(kit):
    """The rule meter: a cream tag on the camera, top-left. A house, a footprint and my number, 0. Glyphs only."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    cream = kit.emit("#fff1cf", 0.9, "tagcream")
    edge = kit.emit("#ff7a5c", 0.9, "tagedge")
    ink = kit.emit("#16304a", 1.0, "taginkk")

    def b(name, size, loc, mat, rot=0):
        ob = kit.box(name, size, loc, mat, root, rot=(0, 0, rot * D2R))
        noshadow(ob)
        return ob

    b("tag.edge", (1.0, 0.5, 0.004), (0, 0, 0.0), edge)
    b("tag.plate", (0.95, 0.45, 0.004), (0, 0, 0.004), cream)

    def add_ink(prefix):
        def add(name, size, xy, rot=0, cutout=False):
            return b(f"tag.{prefix}.{name}", (size[0], size[1], 0.004), (xy[0], xy[1], 0.008), cream if cutout else ink, rot)
        return add

    house(add_ink("h"), -0.355, 0.0, 0.17)
    fadd = add_ink("f")
    fcx, fcy, th = -0.07, 0.0, 14.0

    def frot(name, size, xy, rot=0, cutout=False):   # the print leans, like a real one
        dx, dy = xy[0] - fcx, xy[1] - fcy
        c, sn = math.cos(th * D2R), math.sin(th * D2R)
        return fadd(name, size, (fcx + dx * c - dy * sn, fcy + dx * sn + dy * c), rot + th)
    foot(frot, fcx, fcy, 0.27)
    seg7(lambda nm, sz, xy: b(f"tag.z.{nm}", (sz[0], sz[1], 0.004), (xy[0], xy[1], 0.008), ink), "0", 0.355, 0.0, 0.32, 0.18, 0.06)


def _first_frame(kit, story):
    mh = bpy.data.objects.get("mom.headg")
    if mh is not None:
        hair = kit.plastic("#3b2418", 0.65)
        R, H = 0.62, 1.2
        top = H / 2
        # a short bob: back and sides to the jaw, so she reads as a woman at a glance
        kit.box("mom.bobB", (2 * R + 0.12, 0.4, 0.9), (0, R - 0.1, top - 0.45), hair, mh, bevel=0.1)
        for sx in (-1, 1):
            kit.box(f"mom.bobS{sx}", (0.26, 0.85, 0.82), (sx * (R + 0.02), 0.12, top - 0.43), hair, mh, bevel=0.1)
        sil = kit.plastic("#8b8796", 0.8, spec=0.05)
        ob = kit.box("mom.streak", (0.045, 0.02, 0.26), (-0.17, -R - 0.052, top - 0.11), sil, mh, bevel=0.01)
        ob.rotation_euler = (0, 0.08, 0.0)
        ear = kit.plastic("#ffd54a", 0.3, spec=0.7)
        for sx in (-1, 1):
            kit.sphere(f"mom.ear{sx}", 0.07, (sx * (R + 0.06), -0.02, -0.22), ear, mh, seg=8)
    W["inited"] = True


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    # the tag stays one size on screen whatever the lens
    lens = 40.0
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next((s for s in story["shots"] if s["id"] == shot["id"]), None)
    if spec:
        keys = spec["cam"]
        u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
        lens = keys[0][3]
        if len(keys) > 1:
            for a, b in zip(keys, keys[1:]):
                if u <= b[0]:
                    lens = a[3] + (b[3] - a[3]) * ss((u - a[0]) / max(1e-6, b[0] - a[0]))
                    break
            else:
                lens = keys[-1][3]
    dist = 1.0
    h2 = dist * 12.0 / lens
    w2 = h2 * 9.0 / 16.0
    s = 0.62 * w2
    tag = W["tag"]
    tag.scale = (s, s, s)
    tag.location = (-0.52 * w2, 0.76 * h2, -dist)
    # who sits: legs straight out forward, hips on the seat
    sits = {}
    for c in sorted(tl["cues"], key=lambda c: c["t"]):
        if c["name"] == "sit" and c["t"] <= t:
            sits[c["who"]] = c
    for who, c in sits.items():
        root = bpy.data.objects.get(who)
        if c.get("on") and root is not None:
            root.location.z += c.get("z", 0.62) - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    # Mom, frozen mid-step: one heel up, held
    fz = None
    for c in sorted(tl["cues"], key=lambda c: c["t"]):
        if c["name"] == "freeze" and c["t"] <= t:
            fz = c
    if fz is not None and fz.get("on"):
        for name, ang in (("mom.leg-1", -0.6), ("mom.leg1", 0.5), ("mom.coat-1", -0.6), ("mom.coat1", 0.5)):
            ob = bpy.data.objects.get(name)
            if ob is not None:
                ob.rotation_euler = (ang, 0, 0)
        root = bpy.data.objects.get("mom")
        if root is not None:
            root.location.z -= 0.03
    return {}
