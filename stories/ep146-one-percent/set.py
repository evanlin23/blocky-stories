"""ep146 "one percent": a sunny marina, Grandpa's teal-and-white houseboat with its covered deck, and Grandma's living room.

Daylight all through, nothing flickers or switches. The only things that change are the two phones' screens and the
rule tag's glyph, and they change by shot (a table below), so animate() is a pure function of t (a shard that starts
mid-film sees what a continuous run sees). No lettering anywhere: phone screens and the tag carry a battery glyph, a
percent sign, a duck, a phone or a bolt only.

World (layout.py): the jetty runs north-south at x 0 (top z 0), the houseboat is moored at its north end (deck z 0.5,
roof z 3.0 over the front deck), a gangplank joins them. I stand at the gangplank's foot facing north, Dex at the rail
facing south. The far shores are green ridges with a few houses and trees, so every angle has a lit subject against a
darker, calmer background.
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: F401
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {}

SUN = dict(sun=3.0, sun_col="#fff0d8", el=55.0, az=200.0, fill=2.6, fill_col="#e8f0ff")
WATER = "#3aa7e0"
DOCK_A, DOCK_B = "#b3a88f", "#a29780"
HULL_W = "#d4d0c2"
TEAL = "#2fb3a6"
TEAL_D = "#1f8f84"
DECK_C = "#c79a66"
ROOF_C = "#c6d6d0"
RAIL_C = "#e6e2d4"
GREEN = "#4e9e48"
INK = "#16304a"
RED = "#e0402f"
GRN = "#4ccf5a"
YEL = "#ffd23a"

_M = {}


def mat(kit, hexc, rough=0.6, spec=0.15):
    k = (hexc, rough, spec)
    if k not in _M:
        _M[k] = kit.plastic(hexc, rough, spec=spec)
    return _M[k]


# ------------------------------------------------------------------------------------------- glyphs (phone + tag)
def battery(P, cx, cz, w, h, kind):
    """A battery glyph centred on (cx, cz) through P(name, cx, cz, sx, sz, hex, layer, rot). kind: low (a red
    sliver), empty (red outline), bolt (green outline, yellow bolt), dim (grey, fading)."""
    t = min(w, h) * 0.13
    oc = {"low": INK, "empty": RED, "bolt": GRN, "dim": "#6d7782"}[kind]
    P("bt", cx, cz + h / 2 - t / 2, w, t, oc, 2, 0)
    P("bb", cx, cz - h / 2 + t / 2, w, t, oc, 2, 0)
    P("bl", cx - w / 2 + t / 2, cz, t, h - 2 * t, oc, 2, 0)
    P("br", cx + w / 2 - t / 2, cz, t, h - 2 * t, oc, 2, 0)
    P("nub", cx + w / 2 + t * 0.6, cz, t * 1.2, h * 0.34, oc, 2, 0)
    iw, ih = w - 2 * t, h - 2 * t
    if kind == "low":
        P("sl", cx - iw / 2 + iw * 0.06, cz, iw * 0.12, ih * 0.82, RED, 2, 0)
    elif kind == "dim":
        P("sl", cx - iw / 2 + iw * 0.06, cz, iw * 0.12, ih * 0.82, "#7a4a46", 2, 0)
    elif kind == "bolt":
        s = ih * 0.46
        P("bz1", cx + s * 0.18, cz + s * 0.5, s * 0.32, s * 1.15, YEL, 3, 28)
        P("bz2", cx - s * 0.18, cz - s * 0.5, s * 0.32, s * 1.15, YEL, 3, 28)
        P("bz3", cx, cz, s * 0.7, s * 0.26, YEL, 3, 0)


def one_percent(P, cx, cz, h, col=INK):
    """'1%' as bars: a one (stem and flag) and a percent sign (two squares and a slash)."""
    w = h * 0.5
    P("o1", cx - h * 0.45, cz, w * 0.34, h, col, 2, 0)
    P("o1f", cx - h * 0.45 - w * 0.24, cz + h * 0.34, w * 0.4, w * 0.3, col, 2, 28)
    px = cx + h * 0.28
    P("p1", px - h * 0.22, cz + h * 0.3, h * 0.26, h * 0.26, col, 2, 0)
    P("p2", px + h * 0.22, cz - h * 0.3, h * 0.26, h * 0.26, col, 2, 0)
    P("ps", px, cz, h * 0.12, h * 1.0, col, 2, -32)


class Phone:
    """A phone made of boxes. Its screen faces local -y. States are groups of emissive boxes; animate() shows one."""
    BW, BH, BT = 0.26, 0.44, 0.03
    SW, SH = 0.22, 0.38

    def __init__(self, kit, name):
        self.kit, self.name = kit, name
        self.root = kit.empty(name, (0, -40, -5))
        body = kit.plastic("#23262e", 0.35, spec=0.4)
        kit.box(f"{name}.body", (self.BW, self.BT, self.BH), (0, 0, 0), body, self.root, bevel=0.012)
        kit.box(f"{name}.dark", (self.SW, 0.01, self.SH), (0, -0.0155, 0.0), kit.plastic("#0b0c10", 0.3, spec=0.5), self.root)
        self.groups = {}
        self.add_state("A", "#e6eef5", 0.9, lambda P: (battery(P, 0, 0.05, 0.17, 0.10, "low"), one_percent(P, 0, -0.1, 0.07)))
        self.add_state("dim", "#2c3138", 0.6, lambda P: battery(P, 0, 0.05, 0.17, 0.10, "dim"))
        self.add_state("D", "#bfe6ff", 0.9, self._duck)
        self.add_state("P", "#2e9a50", 0.85, self._call)
        self.add_state("B", "#0b0c10", 0.2, lambda P: battery(P, 0, 0.0, 0.17, 0.10, "bolt"))
        self.show(None)

    def add_state(self, state, bg, strength, glyph):
        kit, name = self.kit, self.name
        objs = []
        bgm = kit.emit(bg, strength, f"{name}.{state}.bg")
        objs.append(kit.box(f"{name}.{state}.bg", (self.SW, 0.01, self.SH), (0, -0.0205, 0), bgm, self.root))

        def P(nm, cx, cz, sx, sz, hexc, layer, rot):
            m = kit.emit(hexc, 0.9 if hexc not in (INK,) else 1.0, f"{name}.{state}.{hexc}")
            y = {2: -0.0305, 3: -0.0405}[layer]
            objs.append(kit.box(f"{name}.{state}.{nm}", (sx, 0.01, sz), (cx, y, cz), m, self.root, rot=(0, -rot * D2R, 0)))
        glyph(P)
        self.groups[state] = objs

    @staticmethod
    def _duck(P):
        P("db", -0.01, -0.03, 0.15, 0.09, "#ffd23a", 2, 0)
        P("dh", 0.06, 0.05, 0.08, 0.09, "#ffd23a", 2, 0)
        P("dbk", 0.115, 0.04, 0.06, 0.03, "#ff8c1a", 3, 0)
        P("de", 0.065, 0.075, 0.018, 0.018, "#16304a", 3, 0)
        P("dt", -0.095, -0.0, 0.05, 0.05, "#ffd23a", 2, 20)
        P("dw", -0.01, -0.03, 0.07, 0.04, "#e9b800", 3, 0)

    @staticmethod
    def _call(P):
        P("h1", 0, 0, 0.14, 0.05, "#ffffff", 2, 40)
        P("h2", -0.065, -0.05, 0.05, 0.075, "#ffffff", 2, 40)
        P("h3", 0.065, 0.05, 0.05, 0.075, "#ffffff", 2, 40)

    def show(self, state):
        for s, objs in self.groups.items():
            for o in objs:
                o.hide_render = (s != state)
                o.hide_viewport = (s != state)


class Tag:
    """The rule tag: a cream plate on the camera. States: low (battery + 1%), empty, bolt."""

    def __init__(self, kit):
        cam = kit.OBJ["cam"]
        self.root = kit.empty("tag", (0, 0, 0), cam)
        self.groups = {}
        cream = kit.emit("#fff1cf", 0.9, "tagcream")
        edge = kit.emit("#ff7a5c", 0.9, "tagedge")
        self.base = [self._b(kit, "tag.edge", (1.0, 0.5, 0.004), (0, 0, 0.0), edge),
                     self._b(kit, "tag.plate", (0.95, 0.45, 0.004), (0, 0, 0.004), cream)]
        for state in ("low", "empty", "bolt"):
            objs = []

            def P(nm, cx, cz, sx, sz, hexc, layer, rot, objs=objs, state=state):
                m = kit.emit(hexc, 1.0, f"tag.{state}.{hexc}")
                objs.append(self._b(kit, f"tag.{state}.{nm}", (sx, sz, 0.004), (cx, cz, 0.008 + 0.004 * (layer - 2)), m, rot))
            if state == "low":
                battery(P, -0.2, 0.0, 0.5, 0.28, "low")
                one_percent(P, 0.3, 0.0, 0.26)
            elif state == "empty":
                battery(P, -0.02, 0.0, 0.6, 0.31, "empty")
            else:
                battery(P, -0.02, 0.0, 0.6, 0.31, "bolt")
            self.groups[state] = objs
        self.show("low")

    @staticmethod
    def _b(kit, name, size, loc, m, rot=0):
        ob = kit.box(name, size, loc, m, bpy.data.objects["tag"], rot=(0, 0, rot * D2R))
        ob.visible_shadow = False
        return ob

    def show(self, state):
        for s, objs in self.groups.items():
            for o in objs:
                o.hide_render = (s != state)
                o.hide_viewport = (s != state)


# ------------------------------------------------------------------------------------------- the marina
def box(kit, name, size, loc, c, rough=0.6, spec=0.15, rot=(0, 0, 0), bevel=0.0, parent=None):
    return kit.box(name, size, loc, mat(kit, c, rough, spec) if isinstance(c, str) else c, parent, rot, bevel)


def boat(kit, n, x, y, yaw, hull_c, cabin_c, length=4.2):
    root = kit.empty(f"boat{n}", (x, y, -0.5), None, (0, 0, yaw * D2R))
    box(kit, f"boat{n}.hull", (1.7, length, 0.9), (0, 0, 0.1), hull_c, 0.5, 0.2, bevel=0.08, parent=root)
    box(kit, f"boat{n}.stripe", (1.74, length * 0.98, 0.14), (0, 0, 0.3), "#f2efe6", 0.5, 0.2, parent=root)
    box(kit, f"boat{n}.cabin", (1.1, length * 0.4, 0.7), (0, -length * 0.1, 0.9), cabin_c, 0.5, 0.2, bevel=0.06, parent=root)
    box(kit, f"boat{n}.win", (1.12, length * 0.26, 0.2), (0, -length * 0.1, 1.0), "#cfe8f4", 0.2, 0.5, parent=root)


def marina(kit):
    water = kit.plastic(WATER, 0.42, spec=0.2)
    box(kit, "water", (500, 500, 0.4), (0, 0, -0.7), water)
    # the jetty: planks, edge beams, posts
    planks = kit.planks(DOCK_A, DOCK_B, 1.0, "X")
    box(kit, "jetty", (3.2, 17.8, 0.3), (0, -7.3, -0.15), planks)
    box(kit, "jettyfoot", (4.6, 1.2, 0.3), (0, 1.2, -0.15), planks)
    for sx in (-1, 1):
        box(kit, f"beam{sx}", (0.2, 17.8, 0.35), (sx * 1.65, -7.3, -0.25), "#8a8070", 0.8, 0.05)
    for k, y in enumerate((-14.5, -11.5, -8.5, -5.5, -2.5, 0.5, 1.7)):
        for sx in (-1, 1):
            kit.cyl(f"post{k}{sx}", 0.13, 1.1, (sx * 1.75, y, 0.35), mat(kit, "#9a8e76", 0.8, 0.05), n=10)
            kit.cyl(f"postcap{k}{sx}", 0.16, 0.06, (sx * 1.75, y, 0.92), mat(kit, "#d8d0bc", 0.7, 0.05), n=10)
    # small boats on both sides of the jetty
    for n, (x, y, yaw, hc, cc) in enumerate(((-4.2, -2.0, 4, "#d6453a", "#f2efe6"), (4.3, -4.5, -3, "#2f6fd6", "#f2efe6"),
                                              (-4.4, -8.0, -5, "#f2c230", "#2fb3a6"), (4.2, -10.5, 6, "#f2efe6", "#d6453a"),
                                              (-4.3, -12.5, 2, "#2fb3a6", "#f2efe6"))):
        boat(kit, n, x, y, yaw, hc, cc)
    # far shores: green ridges, with houses and trees on them
    ridge = mat(kit, GREEN, 0.9, 0.02)
    box(kit, "ridgeS", (240, 24, 7), (0, -50, 2.8), ridge)
    box(kit, "ridgeS2", (120, 14, 4), (-30, -38, 1.4), "#5fb056", 0.9, 0.02)
    box(kit, "ridgeN", (240, 24, 8), (0, 50, 3.2), ridge)
    box(kit, "ridgeE", (24, 200, 6), (55, 0, 2.2), ridge)
    box(kit, "ridgeW", (24, 200, 6), (-55, 0, 2.2), ridge)
    for k, (x, y, yaw) in enumerate(((-18, -43, 0), (-6, -42, 0), (9, -43, 0), (22, -44, 0), (-30, -44, 0))):
        kit.prop("sub_building_type_a" if k % 2 == 0 else "sub_building_type_c", (x, y, 6.2), rot=yaw, height=5.0)
    for k in range(16):
        kit.prop("pinetree_1" if k % 3 else "commontree_1", (-36 + k * 5 + (k % 3) * 1.2, -41 + (k % 4) * 1.4, 6.2), rot=k * 40, height=6.5)
    for k in range(10):
        kit.prop("pinetree_2", (-24 + k * 6, 41 + (k % 3), 7.2), rot=k * 25, height=6.5)


def houseboat(kit):
    ox = 0.0
    deck = kit.planks(DECK_C, "#b98a58", 1.0, "X")
    box(kit, "hull", (9.4, 6.0, 1.0), (0, 7.0, 0.0), HULL_W, 0.5, 0.2, bevel=0.1)
    box(kit, "hullstripe", (9.46, 6.06, 0.16), (0, 7.0, 0.22), TEAL, 0.5, 0.2)
    box(kit, "deck", (9.0, 5.7, 0.08), (0, 7.0, 0.46), deck)
    # cabin at the back, teal with white trim, a shut door and two windows
    box(kit, "cabin", (8.0, 2.8, 2.5), (0, 8.5, 1.75), TEAL, 0.55, 0.15, bevel=0.06)
    box(kit, "cabintrim", (8.1, 2.9, 0.2), (0, 8.5, 0.6), HULL_W, 0.6, 0.1)
    for sx in (-1, 1):
        box(kit, f"win{sx}", (1.5, 0.08, 1.0), (sx * 2.4, 7.07, 1.7), "#cfe8f4", 0.15, 0.6)
        box(kit, f"winf{sx}", (1.7, 0.06, 1.2), (sx * 2.4, 7.05, 1.7), "#f2efe6", 0.5, 0.1)
    box(kit, "door", (1.0, 0.08, 1.9), (-3.4, 7.07, 1.45), TEAL_D, 0.55, 0.1)
    box(kit, "doorf", (1.2, 0.06, 2.1), (-3.4, 7.05, 1.5), "#f2efe6", 0.5, 0.1)
    # the covered deck's roof (the ceiling for every deck angle) on four white posts
    box(kit, "roof", (9.8, 6.6, 0.25), (0, 7.2, 3.1), ROOF_C, 0.7, 0.05)
    box(kit, "roofedge", (9.9, 0.2, 0.4), (0, 4.0, 3.1), TEAL, 0.6, 0.1)
    for x in (-4.5, -3.0, 3.0, 4.5):
        box(kit, f"rpost{x}", (0.16, 0.16, 2.6), (x, 4.3, 1.8), RAIL_C, 0.6, 0.05)
    # the south rail with a gate gap where the gangplank lands
    for sx in (-1, 1):
        x0, x1 = (0.75, 4.6) if sx > 0 else (-4.6, -0.75)
        xc, ln = (x0 + x1) / 2 * 1.0, x1 - x0
        box(kit, f"railtop{sx}", (ln, 0.1, 0.1), (xc, G.RAIL_Y, G.DECK_Z + 1.0), RAIL_C, 0.5, 0.1)
        box(kit, f"railmid{sx}", (ln, 0.06, 0.07), (xc, G.RAIL_Y, G.DECK_Z + 0.55), RAIL_C, 0.5, 0.1)
        for k in range(int(ln / 0.9) + 1):
            box(kit, f"railp{sx}{k}", (0.09, 0.09, 1.0), (x0 + k * ln / max(1, int(ln / 0.9)), G.RAIL_Y, G.DECK_Z + 0.5), RAIL_C, 0.5, 0.1)
    for sx in (-1, 1):
        box(kit, f"gate{sx}", (0.1, 0.1, 1.0), (sx * 0.75, G.RAIL_Y, G.DECK_Z + 0.5), RAIL_C, 0.5, 0.1)
    # life rings on the rail (plain, no lettering): a ring of blocks, orange and white
    for k, x in enumerate((-2.2, 2.4)):
        ring = kit.empty(f"ring{k}", (x, G.RAIL_Y - 0.12, G.DECK_Z + 0.62), None, (math.pi / 2, 0, 0))
        for j in range(12):
            a = 2 * math.pi * j / 12
            box(kit, f"ring{k}.{j}", (0.2, 0.09, 0.09), (0.26 * math.cos(a), 0.26 * math.sin(a), 0),
                "#ff7a2a" if j % 2 == 0 else "#f6f3ea", 0.5, 0.1, rot=(0, 0, a + math.pi / 2), parent=ring)
    # the gangplank (a ramp) and the tally post beside its foot
    gp0, gp1 = (0.0, 1.7, 0.0), (0.0, 4.2, G.DECK_Z + 0.04)
    ln = math.hypot(gp1[1] - gp0[1], gp1[2] - gp0[2])
    ang = math.atan2(gp1[2] - gp0[2], gp1[1] - gp0[1])
    box(kit, "gangplank", (1.3, ln, 0.1), ((gp0[0] + gp1[0]) / 2, (gp0[1] + gp1[1]) / 2, (gp0[2] + gp1[2]) / 2 - 0.05),
        kit.planks("#b99d78", "#a98c66", 1.0, "X"), rot=(ang, 0, 0))
    for sx in (-1, 1):
        box(kit, f"gprail{sx}", (0.07, ln, 0.07), (sx * 0.62, (gp0[1] + gp1[1]) / 2, (gp0[2] + gp1[2]) / 2 + 0.75), RAIL_C, 0.5, 0.1,
            rot=(ang, 0, 0))
        box(kit, f"gpp{sx}", (0.08, 0.08, 0.8), (sx * 0.62, 2.0, 0.4), RAIL_C, 0.5, 0.1)
    # the tally post: two short teal strokes scratched at hip height (a clear centimetre proud of the post)
    box(kit, "tallypost", (0.2, 0.2, 1.1), (0.95, 1.55, 0.55), "#8f8470", 0.8, 0.05)
    for k, dx in enumerate((-0.04, 0.04)):
        box(kit, f"tally{k}", (0.025, 0.012, 0.2), (0.95 + dx, 1.55 - 0.106, 0.62), TEAL, 0.6, 0.05, rot=(0, 0.2 * (1 if k else -1), 0))
    # deck dressing: two deck chairs, potted plants, a little table
    for x, yaw in ((-2.6, 12), (2.7, -14)):
        chair = kit.empty(f"chair{x}", (x, 5.4, G.DECK_Z), None, (0, 0, yaw * D2R))
        box(kit, f"chair{x}.seat", (0.7, 0.7, 0.1), (0, 0, 0.4), "#f2c230", 0.6, 0.1, parent=chair)
        box(kit, f"chair{x}.back", (0.7, 0.1, 0.75), (0, 0.3, 0.75), "#f2c230", 0.6, 0.1, rot=(-0.25, 0, 0), parent=chair)
        for lx in (-0.3, 0.3):
            for ly in (-0.3, 0.3):
                box(kit, f"chair{x}.l{lx}{ly}", (0.07, 0.07, 0.4), (lx, ly, 0.2), "#e6e2d4", 0.6, 0.1, parent=chair)
    for x in (-4.0, 4.0):
        kit.prop("nat_pot_large", (x, 5.0, G.DECK_Z), height=0.8)
        kit.prop("houseplant_1", (x, 5.0, G.DECK_Z + 0.5), height=0.9)
    box(kit, "table", (0.6, 0.6, 0.06), (-1.35, 5.9, G.DECK_Z + 0.55), "#e6e2d4", 0.6, 0.1)
    kit.cyl("tablel", 0.05, 0.55, (-1.35, 5.9, G.DECK_Z + 0.27), mat(kit, "#e6e2d4", 0.6, 0.1), n=8)


def grandma_room(kit):
    ox, _ = G.ROOM
    floor = kit.planks("#c8935a", "#b7824c", 1.0, "X")
    box(kit, "gr.floor", (6.0, 7.0, 0.1), (ox, 1.5, -0.05), floor)
    wallc = "#f4d98a"
    box(kit, "gr.back", (6.0, 0.2, 3.0), (ox, 4.6, 1.5), wallc, 0.9, 0.02)
    box(kit, "gr.left", (0.2, 7.0, 3.0), (ox - 3.0, 1.5, 1.5), "#f0cf78", 0.9, 0.02)
    box(kit, "gr.right", (0.2, 7.0, 3.0), (ox + 3.0, 1.5, 1.5), "#f0cf78", 0.9, 0.02)
    box(kit, "gr.ceiling", (6.2, 7.2, 0.2), (ox, 1.5, 3.05), "#fff3d6", 0.9, 0.02)
    box(kit, "gr.wainscot", (5.9, 0.12, 0.9), (ox, 4.48, 0.45), "#e8b873", 0.7, 0.05)
    # a window on the right wall with a blue sky
    box(kit, "gr.window", (0.06, 1.5, 1.2), (ox + 2.88, 2.2, 1.7), kit.emit("#bfe6ff", 1.2, "gr.sky"))
    box(kit, "gr.winf", (0.1, 1.7, 1.4), (ox + 2.9, 2.2, 1.7), "#f2efe6", 0.5, 0.1)
    # the radio on a shelf on the back wall, left of centre
    box(kit, "gr.shelf", (1.9, 0.4, 0.08), (ox - 0.9, 4.35, 1.35), "#a8723c", 0.7, 0.05)
    box(kit, "gr.radio", (0.95, 0.38, 0.55), (ox - 0.9, 4.33, 1.67), "#d6453a", 0.5, 0.2, bevel=0.05)
    box(kit, "gr.radiof", (0.62, 0.02, 0.32), (ox - 1.05, 4.13, 1.67), "#f6efd6", 0.5, 0.1)
    for k, dx in enumerate((0.28, 0.28)):
        kit.cyl(f"gr.knob{k}", 0.07, 0.04, (ox - 0.9 + 0.32, 4.13, 1.78 - k * 0.2), mat(kit, "#2a2a30", 0.4, 0.3), rot=(math.pi / 2, 0, 0), n=10)
    box(kit, "gr.ant", (0.03, 0.03, 0.6), (ox - 0.6, 4.33, 2.2), "#cfcfcf", 0.3, 0.6, rot=(0, 0.3, 0))
    # a plant and a lamp for depth
    kit.prop("houseplant_1", (ox + 2.3, 3.8, 0), height=1.3)
    kit.prop("light_floor1", (ox - 2.4, 3.8, 0), height=1.6)
    # the table with a doily and the flip phone open on it
    kit.prop("table_roundsmall", (G.FLIP[0], G.FLIP[1], 0), height=0.7)
    box(kit, "gr.rug", (3.0, 2.2, 0.02), (ox, 2.2, 0.01), "#d6453a", 0.9, 0.02)
    fx, fy, fz = G.FLIP
    flip = kit.empty("flip", (fx, fy, fz), None, (0, 0, -12 * D2R))
    box(kit, "flip.base", (0.22, 0.34, 0.04), (0, 0, 0.02), "#3b4048", 0.4, 0.3, parent=flip)
    lid = kit.empty("flip.lid", (0, 0.17, 0.04), flip, (80 * D2R, 0, 0))
    box(kit, "flip.lidb", (0.22, 0.34, 0.04), (0, 0.17, 0), "#3b4048", 0.4, 0.3, parent=lid)
    box(kit, "flip.scr", (0.18, 0.26, 0.01), (0, 0.17, 0.025), kit.emit("#e6eef5", 0.9, "flip.bg"), parent=lid)

    def Pl(nm, cx, cy, sx, sy, hexc, layer, rot):   # glyph boxes in the lid's plane, facing out of its +z side
        box(kit, f"flip.{nm}", (sx, sy, 0.01), (cx, 0.17 + cy, 0.036 + 0.009 * (layer - 2)),
            kit.emit(hexc, 0.9, f"flip.{hexc}"), rot=(0, 0, -rot * D2R), parent=lid)
    battery(Pl, 0, 0.05, 0.14, 0.08, "low")
    one_percent(Pl, 0, -0.05, 0.05)


# ------------------------------------------------------------------------------------------- the people
def _extras(self, hg, spec, kit, faces):
    R, H = faces.HEAD_R, faces.HEAD_H
    top = H / 2
    n = self.name
    if spec.get("stache"):   # Grandpa's big gray moustache, clear of the mouth
        mc = kit.plastic(spec["stache"], 0.9, spec=0.02)
        kit.box(f"{n}.stache", (0.9, 0.2, 0.2), (0, -R - 0.02, -0.3), mc, hg, bevel=0.08)
        for sx in (-1, 1):
            kit.box(f"{n}.stacheE{sx}", (0.22, 0.2, 0.3), (sx * 0.4, -R - 0.02, -0.4), mc, hg, bevel=0.08)
    if spec.get("curls"):   # Dex's big curly top: a cluster of rounded blocks on top of the mop
        cc = kit.plastic(spec["curls"], 0.85, spec=0.05)
        for k, (x, y, z, s) in enumerate(((-0.5, 0.0, 0.46, 0.42), (0.0, 0.1, 0.62, 0.46), (0.5, 0.0, 0.46, 0.42),
                                          (-0.3, -0.3, 0.5, 0.36), (0.3, -0.3, 0.5, 0.36), (0.0, 0.4, 0.45, 0.4))):
            kit.box(f"{n}.curl{k}", (s, s, s), (x, y, top + z - 0.12), cc, hg, bevel=0.16)
    if spec.get("freckles"):   # a few freckles on the cheeks, a hair proud of the face
        fc = kit.plastic(spec["freckles"], 0.9, spec=0.02)
        for k, (x, z) in enumerate(((-0.28, -0.1), (-0.14, -0.16), (0.14, -0.16), (0.28, -0.1), (-0.2, -0.04), (0.2, -0.04))):
            kit.box(f"{n}.fr{k}", (0.05, 0.03, 0.05), (x, -R - 0.045, z), fc, hg)


def _install_extras():
    try:
        from blocky import faces, kit as kit_mod, rig
    except Exception:   # the framing lint runs this file without Blender
        return
    if getattr(rig.Character, "_ep146", False):
        return
    orig = rig.Character._accessories

    def accessories(self, hg, spec):
        orig(self, hg, spec)
        _extras(self, hg, spec, kit_mod, faces)

    rig.Character._accessories = accessories
    rig.Character._ep146 = True


# ------------------------------------------------------------------------------------------- build / animate
def build(kit, story, tl):
    _M.clear()
    W.clear()
    _install_extras()
    sun = kit.light("sun", "SUN", (0, -30, 40), SUN["sun"], SUN["sun_col"], size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, 30, 30), SUN["fill"], SUN["fill_col"], shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    az, el = SUN["az"] * D2R, SUN["el"] * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    sun.location = d * 60
    kit.aim(sun, (0, 0, 0))
    marina(kit)
    houseboat(kit)
    # Grandma's room has its own soft light (its ceiling shuts the sun out)
    for nm, loc, tgt, w in (("grA", (G.ROOM[0] - 1.5, -0.3, 2.7), (G.ROOM[0], 3.0, 1.2), 380.0),
                            ("grB", (G.ROOM[0] + 1.8, 0.4, 2.7), (G.ROOM[0] - 0.6, 2.4, 1.0), 260.0)):
        sp = kit.light(nm, "SPOT", loc, w, "#fff4e0", spot=60, blend=0.8, size=0.4, shadow=False)
        kit.aim(sp, tgt)
    grandma_room(kit)
    W["dex"] = Phone(kit, "phoneD")
    W["me"] = Phone(kit, "phoneM")
    W["tag"] = Tag(kit)
    ch = kit.empty("charger", (0, -40, -5))
    box(kit, "charger.brick", (0.2, 0.12, 0.2), (0, 0, 0), "#e2dfd2", 0.5, 0.2, bevel=0.025, parent=ch)
    for sx in (-1, 1):
        box(kit, f"charger.prong{sx}", (0.03, 0.07, 0.1), (sx * 0.05, 0.09, 0.0), "#9aa0a8", 0.3, 0.6, parent=ch)
    for k, (x, z) in enumerate(((0.0, -0.17), (0.07, -0.26), (0.18, -0.3), (0.3, -0.27))):
        box(kit, f"charger.cab{k}", (0.09, 0.04, 0.05), (x, -0.02, z), "#f2efe6", 0.5, 0.1, rot=(0, 0.5 * k, 0), parent=ch)
    W["charger"] = ch
    W["cur"] = {}
    return {}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# phone placement by shot: who -> (state, mode, a, z, side, scale). mode "held": the phone sits `a` metres in front of
# the person's chest at height z (`side` to their right as the camera sees it); mode "at": at the world point `a`.
# A state may be a list [(u, state), ...] changing at that share of the shot (an eased fade through "dim").
PH = {}
TAG = {}
CAMF = {}   # shot id -> first camera position, from story.json (the phones face it)

DEX_P = (G.DEX[0], G.DEX[1], G.DEX[2])
ME_P = (G.ME[0], G.ME[1], G.ME[2])


def _place(ph, who, st, tl_t, shot, camp):
    state, mode, a, z, side, scale = st
    if isinstance(state, list):
        u = (tl_t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
        cur = state[0][1]
        for uu, ss_ in state:
            if u >= uu:
                cur = ss_
        state = cur
    if state is None:
        ph.root.location = (0, -40, -5)
        ph.show(None)
        return
    if mode == "held":
        base = DEX_P if who == "dex" else ME_P
        fy = 1.0 if who == "me" else -1.0   # I face north (+y), Dex faces south (-y)
        loc = (base[0] + side, base[1] + fy * a, base[2] + z)
    else:
        loc = a
    ph.root.location = loc
    dx, dy = camp[0] - loc[0], camp[1] - loc[1]
    ph.root.rotation_euler = (-8 * D2R, 0, math.atan2(dx, -dy))
    ph.root.scale = (scale, scale, scale)
    ph.show(state)


def animate(kit, story, tl, t, ctx):
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    sid = shot["id"]
    camp = CAMF.get(sid)
    if camp is None:
        spec = next((s for s in story["shots"] if s["id"] == sid), None)
        camp = tuple(spec["cam"][0][1]) if spec else (0, -3, 1.5)
        CAMF[sid] = camp
    row = PH.get(sid, {})
    for who in ("dex", "me"):
        _place(W[who], who, row.get(who, (None, "held", 0, 0, 0, 1.0)), t, shot, camp)
    W["tag"].show(TAG.get(sid, "low"))
    if sid == "S20":
        W["charger"].location = (G.DEX[0], G.DEX[1] - 0.55, G.DEX[2] + 1.22)
        W["charger"].rotation_euler = (0, 0, math.atan2(camp[0] - G.DEX[0], -(camp[1] - G.DEX[1])))
        W["charger"].scale = (1.5, 1.5, 1.5)
    else:
        W["charger"].location = (0, -40, -5)
    return {}


# --- the tables (read by animate) ---------------------------------------------------------------------------------
def _tables():
    A, D, P, B = "A", "D", "P", "B"
    low_me = lambda *_: (A, "held", 0.35, 1.5, 0.3, 0.95)
    PH.update({
        "S01a": {"dex": (A, "at", G.RAILPH, 0, 0, 1.0)},
        "S01a2": {"dex": (A, "at", G.RAILPH, 0, 0, 1.0)},
        "S01b": {"me": low_me()},
        "S01c": {"dex": (A, "held", 0.5, 1.0, 0.0, 1.0)},
        "S02": {"dex": (A, "held", 0.5, 1.0, 0.0, 1.5)},
        "S03a": {"dex": (A, "held", 0.5, 0.95, 0.0, 1.0)},
        "S03b": {"dex": (A, "held", 0.5, 0.95, 0.0, 1.0)},
        "S05": {"me": low_me()},
        "S06": {"dex": (D, "held", 0.5, 1.08, 0.0, 1.2)},
        "S07a": {"dex": (A, "held", 0.5, 1.0, 0.0, 1.0)},
        "S07b": {"dex": (A, "held", 0.5, 1.0, 0.0, 1.0)},
        "S11": {"me": low_me()},
        "S13a": {"me": low_me()},
        "S13b": {"me": (P, "held", 0.35, 1.5, 0.3, 0.95)},
        "S14a": {"dex": (D, "held", 0.5, 1.08, 0.0, 1.2)},
        "S14b": {"dex": (D, "held", 0.5, 1.0, 0.0, 1.0)},
        "S15": {"dex": ([(0, A), (0.45, "dim"), (0.7, None)], "held", 0.5, 1.08, 0.0, 1.2)},
        "S16": {"me": ([(0, A), (0.35, "dim"), (0.6, None)], "held", 0.5, 1.08, 0.0, 1.2)},
        "S17": {"me": (A, "held", 0.5, 1.12, 0.0, 1.5)},
        "S18": {"me": (A, "held", 0.55, 0.98, 0.0, 1.35)},
        "S21": {"me": (B, "held", 0.5, 0.95, 0.0, 1.1)},
    })
    for s in ("S15", "S16", "S17", "S18", "S19a", "S19b", "S20"):
        TAG[s] = "empty"
    TAG["S21"] = "bolt"


_tables()
