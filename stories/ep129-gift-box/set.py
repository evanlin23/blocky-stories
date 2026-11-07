"""ep129 "gift box": Dad's front room, his porch and steps, his kitchen, and three montage rooms.

Nothing here moves and no light changes (batch 14): one steady sun, one steady fill, daylight all the way. Every
state of the box is its own small stage, 60 m apart along x (see layout.py): wrapped on the mantel with the bow
straight (R1), held at waist height (R2), wrapped on the mantel with the bow bent (R3, R3N at night), the open
empty box on the mantel (R4, R5 with the small blue box), a bare mantel (R6), and the kitchen in eight states. A shot
points the camera at the stage it needs and the acting keys put the people there. There is no animate().

The extras on the cast (Dad's goatee, the backward cap, the backpack strap) are added to the rig while it is built,
by a wrapper installed in build(), so a shard that starts mid-film sees the same people as a continuous run.
No lettering anywhere: the clock has dots, the truck is plain white.
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: F401
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
SUN = dict(sun=2.6, sun_col="#fff0d8", el=58.0, az=200.0, fill=2.2, fill_col="#eef2ff")

BUTTER = "#f6dc84"
WHITE = "#f7f4ec"
SKY_BLUE = "#7fc4ef"
RED = "#d2443a"
CREAM = "#f3e3c0"
FLOOR_A, FLOOR_B = "#d6a35c", "#c8944c"
RAIL = "#4f8fd6"
LAWN = "#5cc65a"
MINT = "#9fe0c4"
NEWBLUE = "#3a72d6"
CARD = "#e6d3a3"
CARD_IN = "#dcc590"

_M = {}


def mat(kit, hexc, rough=0.6, spec=0.15):
    k = (hexc, rough, spec)
    if k not in _M:
        _M[k] = kit.plastic(hexc, rough, spec=spec)
    return _M[k]


class Stage:
    """A small stage: everything it builds is shifted by its x offset and named after its tag."""

    def __init__(self, kit, name):
        self.kit, self.tag, self.ox, self.i = kit, name, G.ST[name], 0

    def nm(self, s):
        self.i += 1
        return f"{self.tag}.{s}{self.i}"

    def _m(self, c, rough, spec):
        return mat(self.kit, c, rough, spec) if isinstance(c, str) else c

    def box(self, s, size, loc, c, rough=0.6, spec=0.15, rot=(0, 0, 0), bevel=0.0, parent=None):
        l = loc if parent is not None else (loc[0] + self.ox, loc[1], loc[2])
        return self.kit.box(self.nm(s), size, l, self._m(c, rough, spec), parent, rot, bevel)

    def cyl(self, s, r, h, loc, c, rough=0.6, spec=0.15, rot=(0, 0, 0), n=20, r2=None, parent=None):
        l = loc if parent is not None else (loc[0] + self.ox, loc[1], loc[2])
        return self.kit.cyl(self.nm(s), r, h, l, self._m(c, rough, spec), parent, rot, n=n, r2=r2)

    def plane(self, s, size, loc, c, rough=0.7, spec=0.1, rot=(0, 0, 0)):
        return self.kit.plane(self.nm(s), size, (loc[0] + self.ox, loc[1], loc[2]), self._m(c, rough, spec), None, rot)

    def empty(self, s, loc, rot=(0, 0, 0), parent=None):
        l = loc if parent is not None else (loc[0] + self.ox, loc[1], loc[2])
        return self.kit.empty(self.nm(s), l, parent, rot)


# ---------------------------------------------------------------------------------------------- the boxes
def wrapped_box(S, c, size=None, paper=RED, ribbon=CREAM, bow="straight", dark="#d9c49a"):
    """A wrapped cube centred on c: paper, a broad ribbon cross on every face and across the top, and a bow whose
    tails point west (-x), toward the front door. bow: straight, bent or none."""
    b = size or G.BOX
    h = b / 2
    cx, cy, cz = c
    w = 0.1 * b / G.BOX
    S.box("paper", (b, b, b), c, paper, 0.7, 0.05, bevel=0.012)
    # a vertical band on each face (1.2 cm proud), then a belt across it (2 cm proud): a cross on every face
    for dx, dy in ((0, -1), (0, 1)):
        S.box("vb", (w, 0.024, b + 0.01), (cx, cy + dy * h, cz), ribbon, 0.6, 0.05)
        S.box("hb", (b, 0.04, w), (cx, cy + dy * h, cz), ribbon, 0.6, 0.05)
    for dx, dy in ((-1, 0), (1, 0)):
        S.box("vb", (0.024, w, b + 0.01), (cx + dx * h, cy, cz), ribbon, 0.6, 0.05)
        S.box("hb", (0.04, b, w), (cx + dx * h, cy, cz), ribbon, 0.6, 0.05)
    S.box("tb1", (w, b, 0.024), (cx, cy, cz + h), ribbon, 0.6, 0.05)
    S.box("tb2", (b, w, 0.032), (cx, cy, cz + h), ribbon, 0.6, 0.05)
    top = cz + h + 0.016
    if bow == "none":
        return top
    k = b / G.BOX
    if bow == "straight":
        S.box("knot", (0.11 * k, 0.11 * k, 0.07 * k), (cx - 0.02 * k, cy, top + 0.035 * k), ribbon, 0.6, 0.05, bevel=0.01)
        for sx in (-1, 1):
            S.box("loop", (0.22 * k, 0.08 * k, 0.13 * k), (cx - 0.02 * k + sx * 0.15 * k, cy, top + 0.08 * k), ribbon, 0.6, 0.05,
                  rot=(0, -sx * 28 * D2R, 0), bevel=0.012)
            S.box("loopin", (0.12 * k, 0.012, 0.06 * k), (cx - 0.02 * k + sx * 0.15 * k, cy - 0.046 * k, top + 0.082 * k), dark, 0.7,
                  0.03, rot=(0, -sx * 28 * D2R, 0))
        for sy in (-1, 1):
            S.box("tail", (0.26 * k, 0.07 * k, 0.012), (cx - 0.2 * k, cy + sy * 0.05 * k, top + 0.006), ribbon, 0.6, 0.05,
                  rot=(0, 0, sy * 14 * D2R))
    else:   # bent: the knot turned, the east loop drooping, one tail slipping over the west side
        S.box("knot", (0.11 * k, 0.11 * k, 0.07 * k), (cx - 0.03 * k, cy + 0.01, top + 0.03 * k), ribbon, 0.6, 0.05,
              rot=(8 * D2R, 0, 24 * D2R), bevel=0.01)
        S.box("loop", (0.22 * k, 0.08 * k, 0.13 * k), (cx - 0.18 * k, cy + 0.01, top + 0.075 * k), ribbon, 0.6, 0.05,
              rot=(0, 24 * D2R, 10 * D2R), bevel=0.012)
        S.box("loopin", (0.12 * k, 0.012, 0.06 * k), (cx - 0.18 * k, cy - 0.036 * k, top + 0.077 * k), dark, 0.7, 0.03,
              rot=(0, 24 * D2R, 10 * D2R))
        S.box("loop", (0.2 * k, 0.08 * k, 0.12 * k), (cx + 0.15 * k, cy + 0.02, top + 0.02 * k), ribbon, 0.6, 0.05,
              rot=(0, -62 * D2R, -8 * D2R), bevel=0.012)
        S.box("tail", (0.24 * k, 0.07 * k, 0.012), (cx - 0.2 * k, cy + 0.05 * k, top + 0.006), ribbon, 0.6, 0.05,
              rot=(0, 0, 22 * D2R))
        S.box("tail", (0.2 * k, 0.07 * k, 0.012), (cx - 0.1 * k, cy - 0.09 * k, top + 0.006), ribbon, 0.6, 0.05,
              rot=(0, 0, -34 * D2R))
    return top


def open_box(S, c, size=None, lid=None):
    """The same cube as plain cream cardboard, empty and open at the top. lid: None, or ("tilt", degrees) for a lid
    hinged at the back edge, or ("flat", (x, y, z)) for a lid lying elsewhere."""
    b = size or G.BOX
    h = b / 2
    cx, cy, cz = c
    t = 0.02
    S.box("bot", (b, b, t), (cx, cy, cz - h + t / 2), CARD_IN, 0.9, 0.02)
    S.box("wf", (b, t, b), (cx, cy - h + t / 2, cz), CARD, 0.9, 0.02)
    S.box("wb", (b, t, b), (cx, cy + h - t / 2, cz), CARD, 0.9, 0.02)
    S.box("wl", (t, b - 2 * t, b), (cx - h + t / 2, cy, cz), CARD, 0.9, 0.02)
    S.box("wr", (t, b - 2 * t, b), (cx + h - t / 2, cy, cz), CARD, 0.9, 0.02)
    S.box("lip", (b + 0.03, t, 0.03), (cx, cy - h - 0.005, cz + h - 0.015), CARD_IN, 0.9, 0.02)
    if lid:
        make_lid(S, c, b, lid)


def make_lid(S, c, b, lid):
    cx, cy, cz = c
    h = b / 2
    kind, v = lid
    if kind == "tilt":
        piv = S.empty("lidpiv", (cx, cy + h + 0.02, cz + h + 0.03), rot=(v * D2R, 0, 0))
        S.box("lid", (b + 0.04, b + 0.04, 0.03), (0, -(b + 0.04) / 2, 0.0), CARD, 0.9, 0.02, parent=piv)
        for sx in (-1, 1):
            S.box("lids", (0.02, b + 0.04, 0.06), (sx * (b / 2 + 0.01), -(b + 0.04) / 2, -0.04), CARD, 0.9, 0.02, parent=piv)
        S.box("lidf", (b + 0.04, 0.02, 0.06), (0, -(b + 0.04) + 0.01, -0.04), CARD, 0.9, 0.02, parent=piv)
    else:
        x, y, z = v
        S.box("lid", (b + 0.04, b + 0.04, 0.03), (x, y, z), CARD, 0.9, 0.02, rot=(0, 0, 18 * D2R))


def paper_heap(S, x, y, z0):
    """A heap of crumpled red wrapping paper and a coil of cream ribbon on a counter."""
    rr = mat(S.kit, RED, 0.8, 0.03)
    specs = [(0.34, 0.26, 0.05, 0, 0, 12), (0.28, 0.3, 0.06, 0.04, 0.03, -28), (0.22, 0.2, 0.06, -0.05, 0.04, 50),
             (0.2, 0.22, 0.05, 0.06, -0.04, 76), (0.16, 0.14, 0.05, -0.02, -0.02, 20)]
    z = z0
    for i, (sx, sy, sz, dx, dy, r) in enumerate(specs):
        S.box("pap", (sx, sy, sz), (x + dx, y + dy, z + sz / 2), rr, rot=(0.12 * (-1) ** i, 0.1, r * D2R), bevel=0.01)
        z += sz * 0.7
    S.cyl("coil", 0.06, 0.03, (x + 0.3, y - 0.05, z0 + 0.015), CREAM, 0.6, 0.05)
    S.cyl("coil", 0.03, 0.035, (x + 0.3, y - 0.05, z0 + 0.016), "#e8d6a8", 0.6, 0.05)


# ---------------------------------------------------------------------------------------------- the front room
def clock(S, x, z):
    blue = mat(S.kit, RAIL, 0.5, 0.2)
    S.cyl("clkrim", 0.34, 0.06, (x, 2.83, z), blue, rot=(math.pi / 2, 0, 0), n=32)
    S.cyl("clkface", 0.29, 0.02, (x, 2.79, z), WHITE, 0.4, 0.2, rot=(math.pi / 2, 0, 0), n=32)
    ink = mat(S.kit, "#27406e", 0.5, 0.1)
    for i in range(12):
        a = i * 30 * D2R
        s = 0.026 if i % 3 == 0 else 0.016
        S.cyl("clkdot", s, 0.01, (x + 0.235 * math.sin(a), 2.775, z + 0.235 * math.cos(a)), ink, rot=(math.pi / 2, 0, 0), n=10)
    for L, a, wd in ((0.16, 300, 0.035), (0.23, 60, 0.026)):   # hour hand toward ten, minute hand toward two
        r = a * D2R
        S.box("hand", (wd, 0.012, L), (x + L / 2 * math.sin(r), 2.76, z + L / 2 * math.cos(r)), ink, rot=(0, -r, 0))
    S.cyl("clkpin", 0.03, 0.02, (x, 2.75, z), ink, rot=(math.pi / 2, 0, 0), n=10)
    brass = S.kit.metal("#c9a23c", 0.35)
    S.box("brass", (0.46, 0.07, 0.09), (x, 2.815, z - 0.4), brass, bevel=0.01)
    cream = mat(S.kit, CREAM, 0.6, 0.05)
    for sx in (-1, 1):   # two cream strokes scratched into the brass base: a plain tally, nothing else
        S.box("tally", (0.012, 0.012, 0.055), (x + sx * 0.04, 2.775, z - 0.4), cream, rot=(0, sx * 6 * D2R, 0))


def mantel(S, state):
    white = mat(S.kit, WHITE, 0.5, 0.1)
    S.box("hearth", (1.7, 0.5, 1.1), (0, 2.61, 0.55), white, bevel=0.01)
    S.box("firebox", (0.9, 0.04, 0.62), (0, 2.34, 0.42), "#5a463c", 0.9, 0.02)
    S.box("hearthstone", (1.5, 0.3, 0.03), (0, 2.18, 0.015), "#c9c4b8", 0.8, 0.05)
    S.box("shelf", (2.0, 0.62, 0.1), (0, 2.55, 1.15), white, bevel=0.012)
    clock(S, 0.0, 2.4)
    by = G.MANTEL_Y
    if state == "wrapped":
        wrapped_box(S, (0, by, G.BOX_Z), bow="straight")
    elif state == "bent":
        wrapped_box(S, (0, by, G.BOX_Z), bow="bent")
    elif state in ("open", "open_blue"):
        open_box(S, (0, by, G.BOX_Z))
        lying_bow(S, -0.2, by, G.BOX_Z + G.BOX / 2)   # the bent cream bow lies on the box's west rim, tails to the door
        if state == "open_blue":
            wrapped_box(S, (0.62, by + 0.04, G.SHELF_Z + 0.16), size=0.32, paper=NEWBLUE, bow="straight")


def lying_bow(S, x, y, rim):
    """The bent cream bow resting on an open box's west rim, its two tails hanging over the outside toward the door."""
    cr = mat(S.kit, CREAM, 0.6, 0.05)
    S.box("knot", (0.11, 0.11, 0.07), (x, y, rim + 0.04), cr, rot=(0, 0, 24 * D2R), bevel=0.01)
    S.box("loop", (0.22, 0.08, 0.13), (x - 0.15, y + 0.01, rim + 0.08), cr, rot=(0, 24 * D2R, 10 * D2R), bevel=0.012)
    S.box("loop", (0.2, 0.08, 0.12), (x + 0.15, y + 0.02, rim + 0.07), cr, rot=(0, -50 * D2R, -8 * D2R), bevel=0.012)
    for sy in (-1, 1):   # the tails slip over the west wall (1.5 cm proud of it)
        S.box("tail", (0.012, 0.07, 0.24), (-G.BOX / 2 - 0.016, y + sy * 0.06, rim - 0.1), cr, rot=(0, 0, 0))
    S.box("tailtop", (0.12, 0.07, 0.012), (-G.BOX / 2 + 0.0, y - 0.06, rim + 0.012), cr, rot=(0, 0, 0))
    S.box("tailtop", (0.12, 0.07, 0.012), (-G.BOX / 2 + 0.0, y + 0.06, rim + 0.012), cr, rot=(0, 0, 0))


def bench(S, state):
    """Dad's low white bench (R7): the box sits on it in front of him, at chest height, the clock on the wall above."""
    white = mat(S.kit, WHITE, 0.5, 0.1)
    cy, top = G.CON_Y, G.CON_TOP
    S.box("conbase", (1.5, 0.56, top - 0.05), (0, cy, (top - 0.05) / 2), white, bevel=0.012)
    S.box("contop", (1.66, 0.68, 0.05), (0, cy, top - 0.025), white, bevel=0.012)
    S.box("conkick", (1.56, 0.6, 0.06), (0, cy, 0.03), "#c9c4b8", 0.8, 0.05)
    clock(S, 0.0, 2.4)
    bz = top + G.BOX / 2
    if state == "open":
        open_box(S, (0, cy, bz))
        lying_bow(S, -0.2, cy, bz + G.BOX / 2)
    else:
        wrapped_box(S, (0, cy, bz), bow=state)


def room(kit, name, state="wrapped", held=False, night=False, truck=False, streamers=False, console=None):
    S = Stage(kit, name)
    H = 2.8
    planks = G_PLANKS(kit)
    S.plane("floor", (7.2, 7.76), (0, -1.02, 0.0), planks)
    # walls: the north wall is the house front (blue siding outside, butter inside) with a door and a window
    def nseg(x0, x1, z0, z1):
        S.box("nw", (x1 - x0, 0.2, z1 - z0), ((x0 + x1) / 2, 3.0, (z0 + z1) / 2), SKY_BLUE, 0.8, 0.05)
        S.box("nws", (x1 - x0, 0.04, z1 - z0), ((x0 + x1) / 2, 2.88, (z0 + z1) / 2), BUTTER, 0.85, 0.05)
    dx0, dx1 = G.DOOR_X - 0.5, G.DOOR_X + 0.5
    nseg(-3.6, dx0, 0, H)
    nseg(dx0, dx1, 2.1, H)
    nseg(dx1, G.WIN_X0, 0, H)
    nseg(G.WIN_X0, G.WIN_X1, 0, 0.9)
    nseg(G.WIN_X0, G.WIN_X1, 2.1, H)
    nseg(G.WIN_X1, 3.6, 0, H)
    for sx in (-1, 1):
        S.box("sidewall", (0.2, 7.9, H), (sx * 3.7, -1.0, H / 2), BUTTER, 0.85, 0.05)
    S.box("southwall", (7.6, 0.2, H), (0, -5.0, H / 2), BUTTER, 0.85, 0.05)
    S.box("base", (7.2, 0.03, 0.12), (0, 2.845, 0.06), WHITE, 0.5, 0.1)
    # the door (open, swung out onto the porch) and its trim
    S.box("djl", (0.08, 0.06, 2.14), (dx0 + 0.04, 2.83, 1.07), WHITE, 0.5, 0.1)
    S.box("djr", (0.08, 0.06, 2.14), (dx1 - 0.04, 2.83, 1.07), WHITE, 0.5, 0.1)
    S.box("djt", (1.0, 0.06, 0.08), (G.DOOR_X, 2.83, 2.14), WHITE, 0.5, 0.1)
    S.box("thresh", (0.84, 0.3, 0.03), (G.DOOR_X, 2.98, 0.015), "#b88a52", 0.7, 0.05)
    S.box("door", (0.05, 0.95, 2.04), (dx0 - 0.05, 3.58, 1.02), "#2f9fa8", 0.5, 0.2, bevel=0.01)
    S.box("knob", (0.05, 0.06, 0.06), (dx0 - 0.1, 3.9, 1.0), "#c9a23c", 0.3, 0.6)
    # the window with its white frame and cross-bars
    wx, ww = (G.WIN_X0 + G.WIN_X1) / 2, G.WIN_X1 - G.WIN_X0
    S.box("wsill", (ww + 0.2, 0.2, 0.05), (wx, 2.76, 0.925), WHITE, 0.5, 0.1)
    S.box("wtl", (0.08, 0.06, 1.2), (G.WIN_X0 + 0.04, 2.83, 1.5), WHITE, 0.5, 0.1)
    S.box("wtr", (0.08, 0.06, 1.2), (G.WIN_X1 - 0.04, 2.83, 1.5), WHITE, 0.5, 0.1)
    S.box("wtt", (ww, 0.06, 0.08), (wx, 2.83, 2.06), WHITE, 0.5, 0.1)
    S.box("wmv", (0.05, 0.06, 1.2), (wx, 2.98, 1.5), WHITE, 0.5, 0.1)
    S.box("wmh", (ww, 0.06, 0.05), (wx, 2.99, 1.5), WHITE, 0.5, 0.1)
    if night:
        S.box("pane", (ww, 0.03, 1.2), (wx, 3.04, 1.5), "#27345a", 0.4, 0.3)
    # mantel and what is on it (R7: a low bench in front of Dad instead, nothing behind him to walk into)
    if console:
        bench(S, console)
    else:
        mantel(S, state)
    if held:   # a wrapped box held at waist height in front of whoever stands at HOLD
        wrapped_box(S, G.HOLD_BOX, bow="straight")
    # seating: Dad's armchair and the couch, both turned to face south, and a rug
    S.box("rug", (3.6, 2.4, 0.02), (0.2, 0.9, 0.01), "#bcdcf0", 0.95, 0.02)
    ax, ay = G.ARM
    chair_blue, chair_lt = mat(kit, SKY_BLUE, 0.7, 0.08), mat(kit, "#a9d8f5", 0.8, 0.05)
    S.box("armbase", (1.04, 0.8, 0.25), (ax, ay, 0.175), chair_blue, bevel=0.03)
    S.box("armcush", (0.7, 0.6, 0.15), (ax, ay - 0.06, 0.375), chair_lt, bevel=0.04)
    S.box("armback", (1.04, 0.2, 0.9), (ax, ay + 0.3, 0.475), chair_blue, bevel=0.03)
    for sx in (-1, 1):
        S.box("armarm", (0.18, 0.8, 0.58), (ax + sx * 0.43, ay, 0.34), chair_blue, bevel=0.03)
    cx, cy = G.COUCH
    S.box("couchbase", (2.0, 0.8, 0.25), (cx, cy, 0.175), chair_blue, bevel=0.03)
    S.box("couchcush", (1.64, 0.6, 0.15), (cx, cy - 0.06, 0.375), chair_lt, bevel=0.04)
    S.box("couchback", (2.0, 0.2, 0.9), (cx, cy + 0.3, 0.475), chair_blue, bevel=0.03)
    for sx in (-1, 1):
        S.box("couchend", (0.18, 0.8, 0.58), (cx + sx * 0.91, cy, 0.34), chair_blue, bevel=0.03)
    # a side table and lamp at the couch's east end
    S.box("sidetab", (0.5, 0.5, 0.55), (2.75, 1.5, 0.275), "#e8c9a0", 0.7, 0.05, bevel=0.02)
    S.cyl("lampbase", 0.07, 0.22, (2.75, 1.5, 0.66), "#c9a23c", 0.4, 0.4)
    S.cyl("lamppole", 0.025, 0.2, (2.75, 1.5, 0.87), "#c9a23c", 0.4, 0.4)
    shade = kit.emit("#ffd9a0", 1.1, "lampshade") if night else mat(kit, "#f8ecd0", 0.8, 0.02)
    S.cyl("lampshade", 0.17, 0.26, (2.75, 1.5, 1.08), shade, r2=0.11, n=16)
    if night:   # a blanket over the couch's west seat, striped coral and yellow
        S.box("blanket", (0.82, 0.3, 0.45), (G.ME_SEAT[0], G.ME_SEAT[1] - 0.36, 0.62), kit.checker("#ff9a88", "#ffd24a", 9.0, "blanketc", 0.9),
              bevel=0.03)
    # the plant by the window
    kit.prop("houseplant_1", (3.2 + S.ox, 2.2, 0.0), rot=20, height=1.2)
    # the porch: deck, blue rail, five white steps going north, the lawn, the curb and the street
    S.box("deck", (7.4, 2.1, 0.08), (0, 4.15, -0.04), planks_wood(kit))
    post = mat(kit, RAIL, 0.5, 0.15)
    for px in (-3.55, 3.55):
        S.box("post", (0.12, 0.12, 0.95), (px, 5.15, 0.475), post)
        S.box("post", (0.12, 0.12, 0.95), (px, 3.2, 0.475), post)
        S.box("siderail", (0.06, 2.0, 0.06), (px, 4.2, 0.92), post)
        S.box("siderail2", (0.06, 2.0, 0.06), (px, 4.2, 0.45), post)
    for (x0, x1) in ((-3.5, -3.05), (-1.55, 3.5)):
        S.box("rail", (x1 - x0, 0.06, 0.06), ((x0 + x1) / 2, 5.15, 0.92), post)
        S.box("rail", (x1 - x0, 0.06, 0.06), ((x0 + x1) / 2, 5.15, 0.45), post)
        nb = int((x1 - x0) / 0.3)
        for j in range(nb + 1):
            S.box("bal", (0.04, 0.04, 0.45), (x0 + (x1 - x0) * j / max(1, nb), 5.15, 0.68), post)
    for px in (-3.05, -1.55):
        S.box("steppost", (0.1, 0.1, 0.95), (px, 5.15, 0.475), post)
        S.box("steprail", (0.06, 2.2, 0.06), (px, 6.15, 0.46), post, rot=(24 * D2R, 0, 0))
        S.box("steppost", (0.1, 0.1, 0.55), (px, 7.1, 0.0), post)
    white = mat(kit, WHITE, 0.6, 0.08)
    for i in range(5):
        top = -0.18 * (i + 1)
        S.box("step", (1.5, 0.42, top + 0.95), (-2.3, 5.4 + 0.42 * i, (top - 0.95) / 2), white, bevel=0.008)
    S.plane("lawn", (44, 30), (0, 14.0, -0.95), kit.grime(LAWN, 0.8, 1.6, "lawn129", 0.95))
    S.box("walkway", (1.3, 6.4, 0.03), (-2.3, 8.7, -0.935), "#d8d4cc", 0.85, 0.03)
    S.box("sidewalk", (44, 1.5, 0.06), (0, 11.5, -0.92), "#d8d4cc", 0.85, 0.03)
    S.box("curb", (44, 0.2, 0.18), (0, 12.35, -0.86), "#c4c0b8", 0.85, 0.03)
    S.box("street", (44, 8.0, 0.05), (0, 16.4, -0.95), "#5a5d66", 0.9, 0.02)
    S.box("hse1", (9, 1.0, 4.4), (-7.0, 25.0, 1.3), "#ffb98a", 0.85, 0.05)
    S.box("hse1r", (9.6, 1.2, 0.5), (-7.0, 25.0, 3.7), "#b5472f", 0.8, 0.05)
    S.box("hse2", (8, 1.0, 3.6), (6.5, 26.0, 0.85), "#cfe8c0", 0.85, 0.05)
    S.box("hse2r", (8.6, 1.2, 0.5), (6.5, 26.0, 2.9), "#7a6ab0", 0.8, 0.05)
    kit.prop("commontree_1", (-5.5 + S.ox, 8.5, -0.95), rot=30, height=5.0)
    kit.prop("commontree_2", (6.0 + S.ox, 9.5, -0.95), rot=100, height=5.5)
    kit.prop("bush_1", (4.6 + S.ox, 6.2, -0.95), rot=10, height=1.0)
    kit.prop("bush_2", (-4.6 + S.ox, 6.0, -0.95), rot=40, height=1.0)
    if streamers:
        string_streamers(S)
    if truck:
        moving_truck(S)


def string_streamers(S):
    """Paper streamers (plain colour, no lettering) swagging from the corner posts to the wall top and the door."""
    cols = ["#ff7f6b", "#ffc94a", "#7fc4ef", "#9fe0c4", "#ff9fc0"]
    for k, px in enumerate((-3.55, 3.55)):
        S.box("tallpost", (0.12, 0.12, 2.5), (px, 5.15, 1.25), RAIL, 0.5, 0.15)
    for j in range(4):   # two swags across the porch front, each in strips of colour
        for s in range(9):
            u0, u1 = s / 9, (s + 1) / 9
            x0, x1 = -3.55 + 7.1 * u0, -3.55 + 7.1 * u1
            z0 = 2.5 - 0.35 * math.sin(math.pi * u0) - j * 0.0
            z1 = 2.5 - 0.35 * math.sin(math.pi * u1)
            L = math.hypot(x1 - x0, 5.1 - 5.1) + 0.0
            zc = (z0 + z1) / 2 - j * 0.03
            ang = math.atan2(z1 - z0, x1 - x0)
            S.box("strm", (x1 - x0 + 0.02, 0.04, 0.07), ((x0 + x1) / 2, 5.1 - j * 0.0 + 0.04 * j, zc), cols[(s + j) % 5], 0.8, 0.02,
                  rot=(0, -ang, 0))
    for s in range(7):   # pennants hanging below the front swag
        u = (s + 0.5) / 7
        x = -3.55 + 7.1 * u
        z = 2.5 - 0.35 * math.sin(math.pi * u) - 0.05
        S.box("penn", (0.16, 0.02, 0.22), (x, 5.1, z - 0.12), cols[(s * 2) % 5], 0.8, 0.02, rot=(0, 0, 45 * D2R * (1 if s % 2 else -1)))


def moving_truck(S):
    """A plain white box truck at the curb, side to the house, no lettering anywhere."""
    x0, y0, z0 = 6.35, 13.8, -0.9
    white = mat(S.kit, "#f4f4f2", 0.55, 0.15)
    S.box("cargo", (6.0, 2.5, 2.6), (x0 + 0.0, y0, z0 + 0.55 + 1.3), white, bevel=0.04)
    S.box("cab", (1.9, 2.4, 2.0), (x0 - 3.95, y0, z0 + 0.55 + 1.0), white, bevel=0.06)
    S.box("windshield", (0.06, 2.0, 0.8), (x0 - 4.9, y0, z0 + 0.55 + 1.35), "#4a5a78", 0.2, 0.7)
    S.box("sidewin", (1.0, 0.04, 0.7), (x0 - 4.0, y0 - 1.2, z0 + 0.55 + 1.4), "#4a5a78", 0.2, 0.7)
    S.box("bumper", (0.2, 2.3, 0.25), (x0 - 4.98, y0, z0 + 0.55 + 0.1), "#8d9097", 0.5, 0.3)
    S.box("under", (7.8, 2.2, 0.3), (x0 - 1.0, y0, z0 + 0.6), "#3a3d46", 0.8, 0.05)
    for wx in (-4.0, -0.8, 1.9):
        for sy in (-1, 1):
            S.cyl("wheel", 0.48, 0.3, (x0 + wx, y0 + sy * 1.1, z0 + 0.48), "#2a2a32", 0.8, 0.05, rot=(math.pi / 2, 0, 0), n=18)
            S.cyl("hub", 0.22, 0.32, (x0 + wx, y0 + sy * 1.1, z0 + 0.48), "#a8abb2", 0.4, 0.4, rot=(math.pi / 2, 0, 0), n=12)
    S.box("stripe", (6.0, 0.02, 0.26), (x0, y0 - 1.27, z0 + 0.55 + 0.75), NEWBLUE, 0.6, 0.05)   # a plain blue band, no lettering
    S.box("seam", (0.03, 0.02, 2.4), (x0 + 1.0, y0 - 1.26, z0 + 0.55 + 1.3), "#c9ccd2", 0.6, 0.05)
    S.box("seam", (5.6, 0.02, 0.03), (x0 + 0.0, y0 - 1.26, z0 + 0.55 + 0.5), "#c9ccd2", 0.6, 0.05)


def G_PLANKS(kit):
    if "planks" not in _M:
        _M["planks"] = kit.planks(FLOOR_A, FLOOR_B, 1.0)
    return _M["planks"]


def planks_wood(kit):
    if "deck" not in _M:
        _M["deck"] = kit.planks("#e9e2d2", "#d9d0bc", 1.2)
    return _M["deck"]


# ---------------------------------------------------------------------------------------------- the kitchen
def kitchen(kit, name, state, night=False):
    S = Stage(kit, name)
    if "tile" not in _M:
        _M["tile"] = kit.checker("#f4ecd6", "#e4d6b0", 5.0, "tile129", 0.5)
    S.plane("floor", (7.4, 7.0), (0, 0.4, 0.0), _M["tile"])
    S.box("backwall", (7.4, 0.2, 2.8), (0, 3.3, 1.4), "#f9e8a8", 0.85, 0.05)
    S.box("sidewall", (0.2, 7.0, 2.8), (-3.7, 0.4, 1.4), "#f9e8a8", 0.85, 0.05)
    S.box("sidewall", (0.2, 7.0, 2.8), (3.7, 0.4, 1.4), "#f9e8a8", 0.85, 0.05)
    mint = mat(kit, MINT, 0.5, 0.15)
    S.box("lowcab", (4.6, 0.6, 0.86), (0, 2.9, 0.43), mint, bevel=0.012)
    S.box("counter", (4.7, 0.66, 0.05), (0, 2.88, 0.885), WHITE, 0.4, 0.2)
    for sx in (-1, 1):
        S.box("upcab", (1.7, 0.36, 0.75), (sx * 1.45, 3.07, 1.95), mint, bevel=0.012)
        S.box("knob", (0.05, 0.05, 0.05), (sx * 0.8, 2.87, 1.7), "#c9a23c", 0.3, 0.5)
    for sx in (-1.8, -1.0, 1.0, 1.8):
        S.box("drawerline", (0.02, 0.01, 0.8), (sx * 1.0, 2.595, 0.43), "#6fbfa0", 0.6, 0.05)
    # a window between the upper cabinets: white frame, sky (or navy at night)
    S.box("wf", (1.2, 0.04, 1.0), (0, 3.18, 1.8), WHITE, 0.5, 0.1)
    pane = mat(kit, "#27345a", 0.4, 0.3) if night else kit.emit("#cfe9ff", 0.9, "kitwin")
    S.box("pane", (1.04, 0.03, 0.84), (0, 3.15, 1.8), pane)
    S.box("wm", (0.05, 0.04, 0.84), (0, 3.13, 1.8), WHITE, 0.5, 0.1)
    S.box("wm", (1.04, 0.04, 0.05), (0, 3.13, 1.8), WHITE, 0.5, 0.1)
    # the island: low mint cabinet, white slab
    iy = G.ISLE_Y
    S.box("isle", (3.0, 0.7, G.ISLE_Z - 0.05), (0, iy, (G.ISLE_Z - 0.05) / 2), mint, bevel=0.012)
    S.box("islet", (3.2, 0.8, 0.05), (0, iy, G.ISLE_Z - 0.025), WHITE, 0.4, 0.2, bevel=0.006)
    top = G.ISLE_Z
    for sx in (-1, 1):   # two stools on the camera side
        S.cyl("stool", 0.2, 0.05, (sx * 0.95, 0.15, 0.62), "#e8c9a0", 0.7, 0.05, n=16)
        S.cyl("stoolleg", 0.05, 0.6, (sx * 0.95, 0.15, 0.3), "#b88a52", 0.7, 0.05, n=8)
    if night:
        S.cyl("lampbase", 0.07, 0.04, (-1.1, 1.05, top + 0.02), "#c9a23c", 0.4, 0.4)
        S.cyl("lamppole", 0.025, 0.24, (-1.1, 1.05, top + 0.16), "#c9a23c", 0.4, 0.4)
        S.cyl("lampshade", 0.15, 0.24, (-1.1, 1.05, top + 0.38), kit.emit("#ffd9a0", 1.1, "lampshade"), r2=0.1, n=16)
    mug = mat(kit, "#fffaf0", 0.35, 0.3)
    if state == "KA":    # twelve years ago: an empty open box and a roll of red paper on the island
        open_box(S, (-0.45, iy, top + G.BOX / 2 + 0.01))
        rr = mat(kit, RED, 0.7, 0.05)
        S.cyl("roll", 0.07, 0.7, (0.65, iy + 0.05, top + 0.075), rr, rot=(0, math.pi / 2, 18 * D2R), n=14)
        S.box("sheet", (0.5, 0.35, 0.012), (0.95, iy - 0.12, top + 0.008), rr, rot=(0, 0, -20 * D2R))
    elif state == "KB":  # morning
        S.cyl("mug", 0.06, 0.1, (-0.6, iy + 0.05, top + 0.05), mug, n=16)
        S.cyl("plate", 0.13, 0.015, (0.55, iy, top + 0.0075), mug, n=20)
        S.box("toast", (0.12, 0.12, 0.025), (0.55, iy, top + 0.03), "#e0a85c", 0.8, 0.02, bevel=0.01)
        S.cyl("mug", 0.06, 0.1, (0.1, iy - 0.2, top + 0.05), mug, n=16)
    elif state == "KC":  # the paper coming off: red panels on three sides, the top and the front peeled back
        b = G.BOX
        h = b / 2
        cz = top + h + 0.01
        cardm = CARD
        S.box("cardbox", (b - 0.02, b - 0.02, b - 0.02), (0, iy, cz), cardm, 0.9, 0.02)
        rr = mat(kit, RED, 0.75, 0.05)
        t = 0.012
        S.box("pl", (t, b, b), (-h + t / 2 + 0.002, iy, cz), rr)
        S.box("pr", (t, b, b), (h - t / 2 - 0.002, iy, cz), rr)
        S.box("pb", (b, t, b), (0, iy + h - t / 2 - 0.002, cz), rr)
        fp = S.empty("pfront", (0, iy - h - 0.012, cz + h), rot=(-24 * D2R, 0, 0))   # hinged at its top edge, the foot peeling out
        S.box("pf", (b, t, b), (0, 0, -b / 2), rr, parent=fp)
        tp = S.empty("ptop", (0, iy + h, cz + h), rot=(-14 * D2R, 0, 0))                  # hinged at the back, its front edge lifting
        S.box("pt", (b, b, t), (0, -b / 2, 0), rr, parent=tp)
        cr = mat(kit, CREAM, 0.6, 0.05)
        S.box("cut", (0.5, 0.07, 0.01), (0.8, iy - 0.05, top + 0.006), cr, rot=(0, 0, 14 * D2R))
        S.box("cut", (0.4, 0.07, 0.01), (-0.9, iy + 0.1, top + 0.006), cr, rot=(0, 0, -30 * D2R))
        S.box("bowflat", (0.2, 0.14, 0.06), (0.95, iy - 0.2, top + 0.03), cr, rot=(0, 0, 20 * D2R), bevel=0.01)
    elif state == "KD":  # the lid half up
        open_box(S, (0, iy, top + G.BOX / 2 + 0.01), lid=("tilt", -34))
        paper_heap(S, -1.0, iy, top)
    elif state == "KE":  # the lid off, the box empty, seen from above
        open_box(S, (0, iy, top + G.BOX / 2 + 0.01), lid=("flat", (1.0, iy - 0.05, top + 0.017)))
        paper_heap(S, -1.0, iy, top)
    elif state == "KF":  # Dad holds the open empty box at waist height in front of the island; its lid lies on the island
        open_box(S, G.KF_BOX)
        paper_heap(S, -1.1, iy, top)
        S.box("lid", (0.54, 0.54, 0.03), (1.1, iy - 0.05, top + 0.017), CARD, 0.9, 0.02, rot=(0, 0, 18 * D2R))
    elif state == "KG":  # a plain white frosted cake, no candles, no numerals, and two plates
        S.cyl("plate", 0.26, 0.015, (0, iy - 0.05, top + 0.0075), mug, n=24)
        S.cyl("cake", 0.2, 0.13, (0, iy - 0.05, top + 0.08), "#fff7ea", 0.6, 0.05, n=24)
        S.cyl("frost", 0.205, 0.035, (0, iy - 0.05, top + 0.13), "#ffffff", 0.5, 0.05, n=24)
        S.cyl("band", 0.206, 0.025, (0, iy - 0.05, top + 0.045), "#ffc9d6", 0.6, 0.03, n=24)
        for sx in (-1, 1):
            S.cyl("plate", 0.13, 0.012, (sx * 0.55, iy - 0.1, top + 0.006), mug, n=20)
            S.box("fork", (0.02, 0.15, 0.01), (sx * 0.55 + 0.17, iy - 0.1, top + 0.005), "#c9ccd2", 0.3, 0.6)
    elif state == "KH":  # night: the small blue box on the island
        wrapped_box(S, (-0.4, iy, top + 0.17), size=0.34, paper=NEWBLUE, bow="straight")


# ---------------------------------------------------------------------------------------------- the montage rooms
def room_shell(S, wall, floor, w=7.0, d=6.0, back=3.2):
    S.plane("floor", (w, d), (0, back - d / 2, 0), floor)
    S.box("back", (w, 0.2, 2.8), (0, back, 1.4), wall, 0.85, 0.05)
    S.box("sw", (0.2, d, 2.8), (-w / 2, back - d / 2, 1.4), wall, 0.85, 0.05)
    S.box("sw", (0.2, d, 2.8), (w / 2, back - d / 2, 1.4), wall, 0.85, 0.05)


def albee_porch(kit):
    S = Stage(kit, "MA")
    room_shell(S, "#8fd48f", kit.planks("#e9e2d2", "#d9d0bc", 1.2))
    S.box("wd", (1.6, 0.05, 1.5), (-1.7, 3.05, 1.5), WHITE, 0.5, 0.1)
    S.box("wp", (1.4, 0.04, 1.3), (-1.7, 3.02, 1.5), kit.emit("#cfe9ff", 0.8, "albwin"))
    S.box("door", (1.1, 0.06, 2.1), (1.9, 3.05, 1.05), "#d2443a", 0.5, 0.2)
    S.box("doorin", (0.8, 0.02, 1.7), (1.9, 3.0, 1.05), "#e8665a", 0.5, 0.2)
    for sx in (-1, 1):   # white railing in front, low, and flower pots
        S.box("rail", (3.0, 0.06, 0.06), (sx * 2.0, -0.6, 0.9), WHITE, 0.5, 0.1)
        S.box("rail", (3.0, 0.06, 0.06), (sx * 2.0, -0.6, 0.45), WHITE, 0.5, 0.1)
        for j in range(8):
            S.box("bal", (0.05, 0.05, 0.45), (sx * 0.55 + sx * j * 0.4, -0.6, 0.68), WHITE, 0.5, 0.1)
        S.cyl("pot", 0.22, 0.3, (sx * 2.7, 2.5, 0.15), "#d8704a", 0.7, 0.05, n=14)
        S.cyl("fl", 0.28, 0.25, (sx * 2.7, 2.5, 0.45), "#ff9fc0", 0.8, 0.02, n=10)
    # the shoebox: orange card, a white lid, red and white circus stripes, held at her waist
    sx0, sy0, sz0 = 0.0, 0.84, 0.9
    S.box("sbox", (0.46, 0.24, 0.12), (sx0, sy0, sz0 - 0.03), SKY_BLUE, 0.8, 0.03, bevel=0.01)
    S.box("slid", (0.48, 0.26, 0.05), (sx0, sy0, sz0 + 0.05), WHITE, 0.6, 0.05, bevel=0.01)
    for i in range(4):
        S.box("sstripe", (0.045, 0.264, 0.056), (sx0 - 0.18 + i * 0.12, sy0, sz0 + 0.05), "#d2443a", 0.6, 0.05)
    kit.prop("houseplant_1", (-3.0 + S.ox, 2.5, 0.0), rot=0, height=1.1)
    # a green house post outside on the right, and the lawn behind the railing
    S.plane("lawn", (30, 20), (0, -11.0, -0.4), kit.grime(LAWN, 0.8, 1.6, "lawn129b", 0.95))


def sam_kitchen(kit):
    S = Stage(kit, "MS")
    room_shell(S, "#ffe9b0", kit.checker("#f4ecd6", "#e4d6b0", 5.0, "tile129", 0.5), back=3.4)
    mint = mat(kit, MINT, 0.5, 0.15)
    S.box("cab", (4.0, 0.6, 0.86), (0, 3.0, 0.43), mint, bevel=0.012)
    S.box("cabtop", (4.1, 0.66, 0.05), (0, 2.98, 0.885), WHITE, 0.4, 0.2)
    S.box("up", (1.6, 0.36, 0.75), (-1.6, 3.17, 1.95), mint, bevel=0.012)
    S.box("up", (1.6, 0.36, 0.75), (1.6, 3.17, 1.95), mint, bevel=0.012)
    S.box("wf", (1.2, 0.04, 1.0), (0, 3.28, 1.8), WHITE, 0.5, 0.1)
    S.box("pane", (1.04, 0.03, 0.84), (0, 3.25, 1.8), kit.emit("#cfe9ff", 0.9, "samwin"))
    # the table, the box on it and Sam's chair
    wood = mat(kit, "#d9a25c", 0.6, 0.1)
    S.box("table", (1.5, 0.95, 0.05), (0, 1.65, 0.74), wood, bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            S.box("tleg", (0.06, 0.06, 0.72), (sx * 0.68, 1.65 + sy * 0.4, 0.36), wood)
    S.box("seat", (0.55, 0.5, 0.06), (0, 2.45, 0.43), wood, bevel=0.01)
    S.box("chback", (0.55, 0.06, 0.55), (0, 2.7, 0.7), wood, bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            S.box("chleg", (0.05, 0.05, 0.42), (sx * 0.23, 2.45 + sy * 0.2, 0.21), wood)
    # the box from his sister: card, a green ribbon cross, a bow
    wrapped_box(S, (0.45, 1.6, 0.765 + 0.17), size=0.34, paper="#c9a26a", ribbon="#4cae5e", bow="straight", dark="#3a8f4a")


def post_office(kit):
    S = Stage(kit, "MP")
    room_shell(S, "#d9e8f2", kit.planks("#c9b08a", "#b99d74", 1.2), back=3.4)
    # pigeonholes on the back wall: dark cubbies in a grid, no labels
    S.box("cubbyback", (3.4, 0.05, 1.5), (0, 3.28, 1.55), "#a8b8c4", 0.8, 0.05)
    for r in range(3):
        for c in range(6):
            S.box("cubby", (0.46, 0.04, 0.38), (-1.4 + c * 0.56, 3.24, 1.0 + r * 0.46), "#4a5a78", 0.9, 0.02)
    brown = mat(kit, "#a8703c", 0.6, 0.1)
    S.box("counter", (3.0, 0.8, 1.05), (-0.9, 0.95, 0.525), brown, bevel=0.012)
    S.box("countertop", (3.1, 0.9, 0.05), (-0.9, 0.95, 1.075), "#c9965a", 0.5, 0.15)
    S.box("scale", (0.4, 0.35, 0.1), (-1.5, 0.95, 1.15), "#8d9097", 0.4, 0.4, bevel=0.01)
    S.box("stamp", (0.12, 0.12, 0.1), (0.2, 0.9, 1.15), "#2a2a40", 0.5, 0.2, bevel=0.01)
    # the crate beside him: slatted wood, a darker wet patch on one corner, a puddle on the floor
    crate = mat(kit, "#b9824a", 0.8, 0.03)
    cx, cy = 1.0, 1.9
    S.box("crate", (0.62, 0.62, 0.62), (cx, cy, 0.31), crate, bevel=0.008)
    for z in (0.08, 0.31, 0.54):
        for sx in (-1, 1):
            S.box("slat", (0.66, 0.05, 0.1), (cx, cy + sx * 0.3, z), "#9a6c3c", 0.8, 0.03)
            S.box("slat", (0.05, 0.66, 0.1), (cx + sx * 0.3, cy, z), "#9a6c3c", 0.8, 0.03)
    for sx in (-1, 1):
        S.box("post", (0.06, 0.06, 0.66), (cx + sx * 0.3, cy - 0.3, 0.31), "#8a5a30", 0.8, 0.03)
    S.box("wet", (0.3, 0.012, 0.3), (cx - 0.31 + 0.0, cy - 0.34, 0.12), "#6a4a2c", 0.2, 0.5)
    S.cyl("puddle", 0.22, 0.01, (cx - 0.25, cy - 0.5, 0.006), "#7f98ac", 0.1, 0.8, n=20)


# ---------------------------------------------------------------------------------------------- the cast's extras
def _extras(self, hg, spec, kit, faces):
    n = self.name
    R, H = faces.HEAD_R, faces.HEAD_H
    top = H / 2
    if spec.get("goatee"):   # Dad: a gray goatee and sideburns, clear of the mouth
        gc = kit.plastic(spec["goatee"], 0.9, spec=0.02)
        kit.box(f"{n}.chin", (0.66, 0.16, 0.2), (0, -0.53, -0.57), gc, hg, bevel=0.06)
    if spec.get("stubble"):   # Dad at 48: gray stubble along the jaw, clear of the mouth
        sc_ = kit.plastic(spec["stubble"], 0.95, spec=0.02)
        kit.box(f"{n}.stub", (0.78, 0.1, 0.2), (0, -0.52, -0.52), sc_, hg, bevel=0.04)
    if spec.get("backcap"):   # Sam: a cap worn backward, brim at the back
        cc = kit.plastic(spec["backcap"], 0.6)
        kit.box(f"{n}.capc", (2 * R + 0.12, 2 * R + 0.12, 0.42), (0, 0.0, top + 0.08), cc, hg, bevel=0.18)
        kit.box(f"{n}.capb", (2 * R * 0.8, 0.6, 0.07), (0, R + 0.28, top - 0.08), cc, hg, bevel=0.03)
        kit.box(f"{n}.capr", (2 * R + 0.14, 0.5, 0.3), (0, -R + 0.25, top - 0.05), cc, hg, bevel=0.1)
    if spec.get("strap"):   # a backpack strap over one shoulder, down the chest
        sc = kit.plastic(spec["strap"], 0.6)
        kit.box(f"{n}.strap", (0.26, 0.07, 1.45), (0.62, -0.53, 1.12), sc, self.upper, rot=(0, 0.1, 0), bevel=0.03)


def _install_extras():
    try:
        from blocky import faces, kit as kit_mod, rig
    except Exception:   # the framing lint runs this file without Blender
        return
    if getattr(rig.Character, "_ep129", False):
        return
    orig = rig.Character._accessories

    def accessories(self, hg, spec):
        orig(self, hg, spec)
        _extras(self, hg, spec, kit_mod, faces)

    rig.Character._accessories = accessories
    rig.Character._ep129 = True


# ---------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    _M.clear()
    _install_extras()
    sun = kit.light("sun", "SUN", (0, -30, 40), SUN["sun"], SUN["sun_col"], size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -30, 30), SUN["fill"], SUN["fill_col"], shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    az, el = SUN["az"] * D2R, SUN["el"] * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    sun.location = d * 60
    kit.aim(sun, (0, 0, 0))
    # three narrow spot fills, steady: they light the shaded east face of the box for S25, S30b, S36 and S60, and the back
    # of my head on the steps for S55 (the sun is behind the house, so those faces would otherwise render nearly black)
    for nm, ox, loc, tgt, w, cone in (("fillR1", 0.0, (3.2, 2.0, 1.7), (0.0, 2.55, 1.5), 700.0, 30),
                                       ("fillR2", 60.0, (3.2, 0.83, 0.9), (0.0, 0.83, 0.65), 500.0, 30),
                                       ("fillR3N", 180.0, (3.2, 2.0, 1.7), (0.0, 2.55, 1.5), 700.0, 30),
                                       ("fillR4", 240.0, (3.2, 2.0, 1.7), (0.0, 2.55, 1.5), 700.0, 30),
                                       ("fillSteps", 0.0, (-2.3, 11.0, 4.0), (-2.3, 5.4, 0.9), 900.0, 24)):
        sp = kit.light(nm, "SPOT", (loc[0] + ox, loc[1], loc[2]), w, "#fff4e0", spot=cone, blend=0.7, size=0.4, shadow=False)
        kit.aim(sp, (tgt[0] + ox, tgt[1], tgt[2]))
    room(kit, "R1", "wrapped")
    room(kit, "R2", "none", held=True)
    room(kit, "R3", "bent", truck=True, streamers=True)
    room(kit, "R3N", "bent", night=True)
    room(kit, "R4", "open")
    room(kit, "R5", "open_blue")
    room(kit, "R6", "none")
    room(kit, "R7", "none", console="straight")
    room(kit, "R7B", "none", console="bent")
    room(kit, "R7O", "none", console="open")
    for nm in ("KA", "KB", "KC", "KD", "KE", "KF", "KG", "KH"):
        kitchen(kit, nm, nm, night=(nm == "KH"))
    albee_porch(kit)
    sam_kitchen(kit)
    post_office(kit)
    return {}
