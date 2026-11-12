"""ep149 "cuckoo six": Grandpa's bright living room on his birthday, 7 PM sun.

One room, one stage, nothing teleports. The camera looks north from the south end. North wall (y = 2.9): the carved
cuckoo clock over Grandpa's chair (x = 0), the red armchair (A) with its back against the wall, the hall closet (C,
ajar, a coat sleeve in the gap) on the left, and the window with the long yellow curtain (B) on the right. Ivy
stands behind the curtain from the first frame (only her red sneakers under the hem, and the curtain's bulge). The
long table with its white-and-red cloth to the floor (D) and the birthday cake are in front of the north seats.

animate(): the clock's little door and bird (a pop at every cuckoo), the corner counter tag (five people, six
cuckoo ticks, a cake meter), the letters A to D, a ring round the curtain. No light changes.
No lettering anywhere but the A, B, C, D plates (they are the puzzle's own marks) and the sugar 80.
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: F401
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
FONT_PATH = Path(__file__).resolve().parents[2] / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"   # the caption font
W = {}
_M = {}
MASTERS = {"S06", "S08", "S11a", "S11b", "S11c"}   # dollhouse shots: the ceiling is lifted away

WALL_G = "#5aa85a"
WALL_G2 = "#4f9d4f"
CREAM = "#f6ecd2"
WOOD = "#7a4a28"
WOOD_D = "#5a3418"
SUN_Y = "#ffcc33"
RED = "#d94a3a"
SNEAK = "#ff2a2a"
PINK = "#ff9cc0"
FLOOR_A, FLOOR_B = "#d2a164", "#c4914f"

FONT = {
    "8": ("111", "101", "111", "101", "111"), "0": ("111", "101", "101", "101", "111"),
}
_FONT_OBJ = []


def text3d(kit, name, s, size, loc, m, parent=None, ext=0.02, bevel=0.0, rot=(math.pi / 2, 0, 0)):
    """A text object in the caption font, centred on loc (rot (pi/2, 0, 0) faces -y; (0, 0, 0) faces +z)."""
    import bpy as _b
    if not _FONT_OBJ:
        _FONT_OBJ.append(_b.data.fonts.load(str(FONT_PATH)))
    cu = _b.data.curves.new(name, "FONT")
    cu.body, cu.font, cu.size = s, _FONT_OBJ[0], size
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    cu.extrude, cu.bevel_depth = ext, bevel
    cu.materials.append(m)
    ob = _b.data.objects.new(name, cu)
    ob.location, ob.rotation_euler = loc, rot
    kit.link(ob, parent)
    ob.visible_shadow = False
    return ob


def mat(kit, hexc, rough=0.6, spec=0.15):
    k = (hexc, rough, spec)
    if k not in _M:
        _M[k] = kit.plastic(hexc, rough, spec=spec)
    return _M[k]


def M(kit, c, rough=0.6, spec=0.15):
    return mat(kit, c, rough, spec) if isinstance(c, str) else c


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def ct(tl, name):
    for c in tl["cues"]:
        if c["name"] == name:
            return c["t"]
    return None


def trap(t, t0, up, hold, down):
    """0 -> 1 over `up`, held `hold`, back to 0 over `down`."""
    if t < t0 or t > t0 + up + hold + down:
        return 0.0
    if t < t0 + up:
        return (t - t0) / up
    if t < t0 + up + hold:
        return 1.0
    return 1.0 - (t - t0 - up - hold) / down


# ---------------------------------------------------------------------------------------------- room
def box(kit, name, size, loc, c, rough=0.6, spec=0.15, rot=(0, 0, 0), bevel=0.0, parent=None):
    return kit.box(name, size, loc, M(kit, c, rough, spec), parent, rot, bevel)


def cyl(kit, name, r, h, loc, c, rough=0.6, spec=0.15, rot=(0, 0, 0), n=20, r2=None, parent=None):
    return kit.cyl(name, r, h, loc, M(kit, c, rough, spec), parent, rot, n=n, r2=r2)


def pixel_text(kit, name, text, cx, y, cz, px, c, parent=None, gap=0.5, depth=0.02, emit=None):
    """Block letters (3 x 5 pixels) facing -y, centred on (cx, cz), at depth y."""
    w = 3 * px
    total = len(text) * w + (len(text) - 1) * gap * px
    x0 = cx - total / 2 + w / 2
    out = []
    for i, ch in enumerate(text):
        bx = x0 + i * (w + gap * px)
        for r, row in enumerate(FONT[ch]):
            for q, v in enumerate(row):
                if v == "1":
                    loc = (bx + (q - 1) * px, y, cz + (2 - r) * px)
                    out.append(kit.box(f"{name}{i}{r}{q}", (px, depth, px), loc, c, parent))
    return out


def wall_seg(kit, x0, x1, z0, z1):
    w = M(kit, kit.checker(WALL_G, WALL_G2, 9.0, "wallpaper"))
    kit.box("nw", (x1 - x0, 0.2, z1 - z0), ((x0 + x1) / 2, 3.0, (z0 + z1) / 2), w)


def build_room(kit):
    Hh = G.H
    X = G.ROOM_X
    kit.plane("floor", (2 * X + 0.4, 12.0), (0, -2.6, 0.0), kit.planks(FLOOR_A, FLOOR_B, 1.0))
    # rug under the table
    box(kit, "rug", (3.4, 3.6, 0.02), (0, 1.1, 0.011), "#e7d3a6", 0.95, 0.02, bevel=0.01)
    box(kit, "rugb", (3.15, 3.35, 0.025), (0, 1.1, 0.013), "#d96b5a", 0.95, 0.02, bevel=0.01)
    box(kit, "rugc", (2.95, 3.15, 0.03), (0, 1.1, 0.015), "#f1e2bd", 0.95, 0.02, bevel=0.01)
    # ceiling, side walls, south wall
    W["ceiling"] = kit.box("ceiling", (2 * X + 0.4, 12.0, 0.1), (0, -2.6, Hh + 0.05), kit.emit("#f6ecd4", 0.6, "ceilingemit"))
    ww = kit.checker(WALL_G, WALL_G2, 9.0, "wallpaper")
    for sx in (-1, 1):
        kit.box(f"sidewall{sx}", (0.2, 12.0, Hh), (sx * (X + 0.1), -2.6, Hh / 2), ww)
    W["south"] = kit.box("southwall", (2 * X + 0.4, 0.2, Hh), (0, G.ROOM_S - 0.1, Hh / 2), ww)
    # the north wall, with the closet door and the window cut out
    c0, c1 = G.CLOSET_X - 0.4, G.CLOSET_X + 0.4
    w0, w1 = G.CURT_X0 - 0.35, G.CURT_X1 + 0.1
    wall_seg(kit, -X - 0.2, c0, 0, Hh)
    wall_seg(kit, c0, c1, 2.1, Hh)
    wall_seg(kit, c1, w0, 0, Hh)
    wall_seg(kit, w0, w1, 0, 0.85)
    wall_seg(kit, w0, w1, 2.55, Hh)
    wall_seg(kit, w1, X + 0.2, 0, Hh)
    # cream wainscot (1 cm proud of the paper) and a picture rail
    for (a, b) in ((-X, c0), (c1, w0), (w1, X)):
        box(kit, "wains", (b - a, 0.03, 0.9), ((a + b) / 2, G.WALL_N - 0.015, 0.45), CREAM, 0.7, 0.05)
        box(kit, "wcap", (b - a, 0.05, 0.05), ((a + b) / 2, G.WALL_N - 0.025, 0.92), "#fffaf0", 0.6, 0.05)
    for sx in (-1, 1):
        box(kit, "wainss", (12.0, 0.03, 0.9), (sx * (X - 0.015), -2.6, 0.45), CREAM, 0.7, 0.05, rot=(0, 0, math.pi / 2))
    # baseboard
    box(kit, "base", (2 * X, 0.04, 0.12), (0, G.WALL_N - 0.02, 0.06), "#fffaf0", 0.5, 0.1)
    # a sky-blue window behind the curtain (soft, never white)
    wx, wwid = (w0 + w1) / 2, w1 - w0
    sky = kit.emit("#a9d4f2", 0.9, "windowsky")
    kit.box("windowsky", (wwid, 0.02, 1.7), (wx, 3.04, 1.7), sky)
    for nm, sz, loc in (("wl", (0.08, 0.02, 1.8), (w0 + 0.04, 2.905, 1.7)), ("wr", (0.08, 0.02, 1.8), (w1 - 0.04, 2.905, 1.7)),
                        ("wt", (wwid, 0.02, 0.08), (wx, 2.905, 2.56)), ("wb", (wwid, 0.02, 0.08), (wx, 2.905, 0.86)),
                        ("wm", (0.05, 0.02, 1.7), (wx, 2.905, 1.7))):
        box(kit, nm, sz, loc, "#fffaf0", 0.5, 0.1)
    box(kit, "wsill", (wwid + 0.2, 0.2, 0.05), (wx, 2.8, 0.83), "#fffaf0", 0.5, 0.1)
    # sunlight patch on the floor (a soft warm plane, 1.5 cm proud of the rug)
    # the pictures: two framed leaf prints on the wall between the closet and the armchair, one over the sideboard
    pic(kit, -0.95, 2.85, 2.15, 0.5, 0.62)
    # the closet (C): the recess, the coat, the door ajar
    build_closet(kit)
    build_curtain(kit)
    build_armchair(kit)
    build_clock(kit)
    build_table(kit)
    build_cake(kit)
    # a standing lamp by the east wall and a plant in the west corner for the room to read as lived in
    cyl(kit, "lampbase", 0.14, 0.03, (-2.55, 2.1, 0.015), "#c9a23c", 0.4, 0.4)
    cyl(kit, "lamppole", 0.025, 1.45, (-2.55, 2.1, 0.75), "#c9a23c", 0.4, 0.4)
    cyl(kit, "lampshade", 0.24, 0.3, (-2.55, 2.1, 1.6), "#fbeccc", 0.8, 0.02, r2=0.17, n=16)
    kit.prop("houseplant_1", (-2.5, -0.5, 0.0), rot=20, height=1.3)
    build_decor(kit)


def build_decor(kit):
    """The birthday: bunting along the north wall, balloons, presents, a longer rug; they fill the dollhouse frame."""
    # the rug runs south under the sixth chair
    box(kit, "rugs", (3.4, 1.6, 0.02), (0, -1.4, 0.011), "#e7d3a6", 0.95, 0.02, bevel=0.01)
    box(kit, "rugsb", (3.15, 1.5, 0.025), (0, -1.4, 0.013), "#d96b5a", 0.95, 0.02, bevel=0.01)
    box(kit, "rugsc", (2.95, 1.3, 0.03), (0, -1.4, 0.015), "#f1e2bd", 0.95, 0.02, bevel=0.01)
    # a picture rail and bunting (plain flags, no letters) sagging between the side walls
    box(kit, "rail", (2 * G.ROOM_X, 0.05, 0.06), (0, G.WALL_N - 0.03, G.UPPER + 0.5), "#fffaf0", 0.6, 0.05)
    cols = ["#e8402e", "#ffcc33", "#ff7fb0", "#1f9f8a", "#6fb4ea"]
    n = 22
    for i in range(n):
        u = (i + 0.5) / n
        x = -2.6 + 5.2 * u
        sag = 0.45 * 4 * u * (1 - u)
        zc = G.UPPER + 0.35 - sag
        pm = M(kit, cols[i % 5], 0.8, 0.02)
        kit.mesh_obj(f"flag{i}", [(x - 0.12, G.WALL_N - 0.06, zc), (x + 0.12, G.WALL_N - 0.06, zc), (x, G.WALL_N - 0.06, zc - 0.3)],
                     [(0, 1, 2)], pm)
        kit.box(f"bstr{i}", (5.2 / n + 0.02, 0.01, 0.015), (x, G.WALL_N - 0.065, zc + 0.005), M(kit, "#7a4a28"))
    # balloon bunches (east foreground and by the west wall), on strings
    bal = ["#e8402e", "#ffcc33", "#ff7fb0", "#1f9f8a", "#6fb4ea", "#e8402e"]
    for bx, by, bz0 in ((-2.45, -1.9, 1.9), (-2.35, 1.0, 2.5)):
        kit.cyl("bstring", 0.008, bz0, (bx, by, bz0 / 2), M(kit, "#fffaf0"), None, (0, 0, 0), n=6)
        for k in range(6):
            a = k * 1.05
            kit.sphere("balloon", 0.2, (bx + 0.2 * math.sin(a), by + 0.14 * math.cos(a), bz0 + 0.18 + 0.12 * (k % 3)),
                       M(kit, bal[k], 0.3, 0.5), None, 14)
    # presents on the floor in the west foreground
    for nm, sz, loc, c, rb in (("pr1", (0.5, 0.4, 0.3), (-1.9, -0.9, 0.15), "#6fb4ea", "#e8402e"),
                               ("pr2", (0.36, 0.36, 0.4), (-1.45, -1.15, 0.2), "#ff9cc0", "#ffcc33"),
                               ("pr3", (0.4, 0.3, 0.24), (-1.7, -1.4, 0.12), "#1f9f8a", "#fffaf0")):
        box(kit, nm, sz, loc, c, 0.6, 0.1, bevel=0.01)
        box(kit, nm + "r1", (sz[0] + 0.02, 0.05, sz[2] + 0.02), loc, rb, 0.6, 0.1)
        box(kit, nm + "r2", (0.05, sz[1] + 0.02, sz[2] + 0.02), loc, rb, 0.6, 0.1)


def pic(kit, x, y, z, w, h):
    box(kit, "picf", (w + 0.1, 0.04, h + 0.1), (x, y - 0.0, z), WOOD, 0.5, 0.2, bevel=0.01)
    box(kit, "pic", (w, 0.02, h), (x, y - 0.03, z), CREAM, 0.7, 0.02)
    cyl(kit, "picleaf", 0.11, 0.015, (x, y - 0.045, z), "#5fa35f", 0.7, 0.02, rot=(math.pi / 2, 0, 0))


def build_closet(kit):
    cx = G.CLOSET_X
    # the recess behind the opening: dark but not black, with a lit coat in the gap
    box(kit, "cl_back", (0.9, 0.05, 2.1), (cx, 3.55, 1.05), "#3a2f2a", 0.9, 0.02)
    box(kit, "cl_l", (0.05, 0.5, 2.1), (cx - 0.425, 3.3, 1.05), "#3a2f2a", 0.9, 0.02)
    box(kit, "cl_r", (0.05, 0.5, 2.1), (cx + 0.425, 3.3, 1.05), "#3a2f2a", 0.9, 0.02)
    box(kit, "cl_top", (0.9, 0.5, 0.05), (cx, 3.3, 2.1), "#3a2f2a", 0.9, 0.02)
    box(kit, "cl_floor", (0.9, 0.5, 0.03), (cx, 3.3, 0.015), "#4a3c33", 0.9, 0.02)
    box(kit, "cl_rod", (0.8, 0.03, 0.03), (cx, 3.15, 1.85), "#c9a23c", 0.4, 0.4)
    box(kit, "coat", (0.3, 0.1, 0.9), (cx + 0.2, 3.1, 1.35), "#b9835a", 0.9, 0.02, bevel=0.03)
    box(kit, "coat2", (0.3, 0.1, 0.9), (cx - 0.15, 3.1, 1.35), "#4a6a9a", 0.9, 0.02, bevel=0.03)
    box(kit, "coatsl", (0.12, 0.1, 0.55), (cx + 0.02, 3.0, 1.3), "#b9835a", 0.9, 0.02, bevel=0.03)
    # trim around the opening
    box(kit, "cl_tl", (0.06, 0.06, 2.12), (cx - 0.43, G.WALL_N - 0.0, 1.06), "#fffaf0", 0.5, 0.1)
    box(kit, "cl_tr", (0.06, 0.06, 2.12), (cx + 0.43, G.WALL_N - 0.0, 1.06), "#fffaf0", 0.5, 0.1)
    box(kit, "cl_tt", (0.92, 0.06, 0.06), (cx, G.WALL_N - 0.0, 2.12), "#fffaf0", 0.5, 0.1)
    # the door leaf, hinged at its left edge, swung out 24 degrees
    hinge = kit.empty("cl_hinge", (cx - 0.4, G.WALL_N - 0.06, 0.0), None, (0, 0, 24 * D2R))
    box(kit, "cl_door", (0.78, 0.05, 2.06), (0.39, -0.03, 1.03), "#f2e6c8", 0.6, 0.1, parent=hinge, bevel=0.01)
    box(kit, "cl_pan", (0.6, 0.02, 0.8), (0.39, -0.065, 1.4), "#e3d5b0", 0.7, 0.05, parent=hinge)
    box(kit, "cl_pan2", (0.6, 0.02, 0.7), (0.39, -0.065, 0.45), "#e3d5b0", 0.7, 0.05, parent=hinge)
    box(kit, "cl_knob", (0.07, 0.06, 0.07), (0.7, -0.09, 1.0), "#c9a23c", 0.3, 0.6, parent=hinge)


def build_curtain(kit):
    x0, x1, y = G.CURT_X0, G.CURT_X1, G.CURT_Y
    cm = mat(kit, SUN_Y, 0.85, 0.04)
    cd = mat(kit, "#f0b422", 0.85, 0.04)
    n = 9
    wd = (x1 - x0) / n
    top, bot = G.CURT_TOP, G.CURT_BOT
    for i in range(n):
        x = x0 + wd * (i + 0.5)
        fwd = 0.07 if i % 2 else 0.0
        if i in (3, 4, 5):   # Ivy's bulge: three folds pushed forward round her shoulders
            fwd += 0.09
        # every fold runs back to one plane, so nothing behind the curtain shows between the folds
        kit.box(f"fold{i}", (wd * 1.04, 0.1 + fwd, top - bot), (x, y - fwd / 2, (top + bot) / 2), cm if i % 2 else cd,
                None, (0, 0, 0), 0.02)
    # a brass rod with finials above it; the gathered tie-back is NOT used: both edges hang straight
    box(kit, "rod", (x1 - x0 + 0.3, 0.04, 0.04), ((x0 + x1) / 2, y, top + 0.06), "#c9a23c", 0.35, 0.5)
    for sx in (x0 - 0.17, x1 + 0.17):
        kit.sphere("fin", 0.05, (sx, y, top + 0.06), M(kit, "#c9a23c", 0.35, 0.5))
    # Ivy's red sneaker toes poking out under the hem (the first clue): a pair of shoes, white soles, laces, stripe;
    # they go when she steps out (cue "toes_off")
    tr = kit.empty("toes", (0, 0, 0))
    W["toes"] = tr
    red = kit.emit("#ff0048", 0.38, "toeemit")
    wh = M(kit, "#fafafa", 0.6, 0.1)
    for sx in (-1, 1):
        tx = G.IVY0[0] + sx * 0.17
        kit.box("toe", (0.24, 0.42, 0.15), (tx, 2.0 + 0.04, 0.105), red, tr, (0, 0, 0), 0.05)
        kit.box("toesole", (0.25, 0.44, 0.03), (tx, 2.0 + 0.04, 0.015), wh, tr, (0, 0, 0), 0.01)
        kit.box("toecap", (0.2, 0.1, 0.08), (tx, 1.84, 0.085), wh, tr, (0, 0, 0), 0.03)
        kit.box("toestripe", (0.245, 0.12, 0.025), (tx, 2.1, 0.13), wh, tr, (0, 0, 0), 0.01)
    # the frosting smudge on the curtain's free edge at hand height (the second clue), 2.5 cm proud of the fold,
    # a big hot-pink thumb smear with a drag below it
    pk = M(kit, "#ff5fa8", 0.6, 0.05)
    kit.box("smudge", (0.12, 0.02, 0.17), (x0 + 0.072, y - 0.075, 1.05), pk, None, (0, 0, 0.25), 0.01)
    kit.box("smudge2", (0.07, 0.02, 0.07), (x0 + 0.1, y - 0.077, 0.88), pk, None, (0, 0, 0.3), 0.01)


def build_armchair(kit):
    ax, ay = G.ARM
    red, redl = mat(kit, RED, 0.7, 0.08), mat(kit, "#e86a5a", 0.7, 0.08)
    kit.box("armbase", (0.85, 1.0, 0.28), (ax, ay, 0.2), red, bevel=0.04)
    kit.box("armcush", (0.62, 0.7, 0.16), (ax + 0.06, ay, 0.42), redl, bevel=0.05)
    kit.box("armback", (0.2, 1.0, 0.95), (ax - 0.33, ay, 0.52), red, bevel=0.05)
    for sy in (-1, 1):
        kit.box(f"armarm{sy}", (0.85, 0.17, 0.62), (ax, ay + sy * 0.42, 0.38), red, bevel=0.05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box("armleg", (0.07, 0.07, 0.1), (ax + sx * 0.36, ay + sy * 0.4, 0.05), M(kit, WOOD_D))


def build_clock(kit):
    cx, cz = G.CLOCK_X, G.CLOCK_Z
    yb = G.WALL_N - 0.18      # body centre (0.3 deep: back flush to the wall, front y = 2.6)
    wood, wood_d = mat(kit, WOOD, 0.55, 0.2), mat(kit, WOOD_D, 0.55, 0.2)
    kit.box("clk_body", (0.66, 0.3, 0.9), (cx, yb, cz + 0.0), wood, bevel=0.02)
    # gabled roof: two slabs, overhanging
    for sx in (-1, 1):
        kit.box(f"clk_roof{sx}", (0.46, 0.38, 0.06), (cx + sx * 0.2, yb - 0.01, cz + 0.55), wood_d, rot=(0, sx * 0.62, 0), bevel=0.01)
    kit.box("clk_gable", (0.5, 0.3, 0.22), (cx, yb, cz + 0.5), wood, bevel=0.01)
    # carved trim bands (2 cm proud)
    kit.box("clk_band1", (0.7, 0.03, 0.05), (cx, yb - 0.165, cz + 0.4), wood_d)
    kit.box("clk_band2", (0.7, 0.03, 0.05), (cx, yb - 0.165, cz - 0.42), wood_d)
    # the little door (top) and its recess
    kit.box("clk_recess", (0.22, 0.03, 0.26), (cx, yb - 0.165, cz + 0.28), M(kit, "#2a1a10"))
    hinge = kit.empty("clk_dhinge", (cx - 0.115, yb - 0.19, cz + 0.28), None, (0, 0, 0))
    kit.box("clk_dleaf", (0.23, 0.025, 0.28), (0.115, -0.0, 0.0), M(kit, "#f0d9a0", 0.6, 0.1), hinge)
    kit.box("clk_dknob", (0.035, 0.03, 0.035), (0.19, -0.02, 0.0), M(kit, WOOD_D), hinge)
    W["dhinge"] = hinge
    # the bird: a red body, a yellow beak, spread white wings, black eyes, turned three-quarters so it reads as a bird
    slide = kit.empty("clk_bird", (cx, yb - 0.1, cz + 0.28), None, (0, 0, 0.6))
    kit.box("bd_body", (0.13, 0.19, 0.15), (0, 0, -0.03), M(kit, "#e01c18", 0.5, 0.1), slide, bevel=0.035)
    kit.box("bd_head", (0.1, 0.1, 0.1), (0, -0.09, 0.05), M(kit, "#e01c18", 0.5, 0.1), slide, bevel=0.03)
    kit.box("bd_beak", (0.05, 0.1, 0.04), (0, -0.2, 0.045), M(kit, "#ffc21e", 0.5, 0.1), slide, bevel=0.012)
    kit.box("bd_beak2", (0.035, 0.07, 0.025), (0, -0.27, 0.04), M(kit, "#ff9a14", 0.5, 0.1), slide, bevel=0.008)
    kit.box("bd_tail", (0.05, 0.14, 0.05), (0, 0.15, 0.0), M(kit, "#a02a20", 0.5, 0.1), slide, rot=(0.4, 0, 0))
    for sx in (-1, 1):
        kit.box(f"bd_wing{sx}", (0.17, 0.12, 0.025), (sx * 0.13, 0.0, 0.03), M(kit, "#fff4e0", 0.5, 0.1), slide,
                rot=(0, -sx * 0.75, 0), bevel=0.008)
        kit.box(f"bd_eye{sx}", (0.02, 0.02, 0.02), (sx * 0.052, -0.12, 0.075), M(kit, "#1a1008", 0.4, 0.2), slide)
    W["bird"] = slide
    W["bird0"] = (cx, yb - 0.1, cz + 0.28)
    # the face: cream disc in a dark ring, dots at the hours, hands at SEVEN (hour hand to 7, minute hand to 12)
    fz = cz - 0.12
    fy = yb - 0.17
    kit.cyl("clk_ring", 0.21, 0.03, (cx, fy + 0.0, fz), M(kit, WOOD_D), None, (math.pi / 2, 0, 0), n=32)
    kit.cyl("clk_face", 0.18, 0.02, (cx, fy - 0.014, fz), M(kit, "#fff4dc", 0.4, 0.2), None, (math.pi / 2, 0, 0), n=32)
    ink = M(kit, "#2a1a0e", 0.5, 0.1)
    for i in range(12):
        a = i * 30 * D2R
        s = 0.017 if i % 3 == 0 else 0.011
        kit.cyl(f"clk_dot{i}", s, 0.01, (cx + 0.146 * math.sin(a), fy - 0.026, fz + 0.146 * math.cos(a)), ink, None,
                (math.pi / 2, 0, 0), n=10)
    for L, a, wd in ((0.09, 210, 0.026), (0.14, 0, 0.018)):
        r = a * D2R
        kit.box("clk_hand", (wd, 0.012, L), (cx + L / 2 * math.sin(r), fy - 0.032, fz + L / 2 * math.cos(r)), ink, None,
                (0, -r, 0))
    kit.cyl("clk_pin", 0.02, 0.014, (cx, fy - 0.036, fz), ink, None, (math.pi / 2, 0, 0), n=10)
    # pine-cone weights hang on hooks at the body's sides, above Ivy's head (nothing hangs below the body)
    for sx in (-1, 1):
        kit.box("clk_hook", (0.1, 0.02, 0.02), (cx + sx * 0.38, yb - 0.12, cz - 0.1), M(kit, "#c9a23c", 0.4, 0.5))
        kit.box("clk_chain", (0.012, 0.012, 0.12), (cx + sx * 0.42, yb - 0.12, cz - 0.17), M(kit, "#c9a23c", 0.4, 0.5))
        kit.cyl("clk_cone", 0.055, 0.14, (cx + sx * 0.42, yb - 0.12, cz - 0.3), M(kit, "#7a5530", 0.7, 0.1), None, (0, 0, 0), n=10, r2=0.025)


def build_table(kit):
    tx, ty = G.TABLE
    w, d, z = G.TABLE_W, G.TABLE_D, G.TABLE_Z
    white = mat(kit, "#fbf8f0", 0.9, 0.02)
    red = mat(kit, "#d6453a", 0.9, 0.02)
    kit.box("tabletop", (w, d, 0.05), (tx, ty, z - 0.025), M(kit, WOOD), bevel=0.01)
    # the cloth: over the top, skirts to 1 cm off the floor; red stripes 1.2 cm proud
    kit.box("cloth", (w + 0.1, d + 0.1, 0.02), (tx, ty, z + 0.01), white)
    kit.box("skirt_f", (w + 0.1, 0.03, z), (tx, ty - d / 2 - 0.05, z / 2 + 0.01), white, bevel=0.005)
    kit.box("skirt_b", (w + 0.1, 0.03, z), (tx, ty + d / 2 + 0.05, z / 2 + 0.01), white, bevel=0.005)
    for sx in (-1, 1):
        kit.box(f"skirt_s{sx}", (0.03, d + 0.1, z), (tx + sx * (w / 2 + 0.05), ty, z / 2 + 0.01), white, bevel=0.005)
    for zz in (0.12, 0.62):
        kit.box("stripe_f", (w + 0.11, 0.012, 0.05), (tx, ty - d / 2 - 0.075, zz), red)
        for sx in (-1, 1):
            kit.box(f"stripe_s{sx}", (0.012, d + 0.11, 0.05), (tx + sx * (w / 2 + 0.075), ty, zz), red)
    kit.box("stripe_t", (w + 0.11, 0.05, 0.012), (tx, ty - 0.55, z + 0.026), red)
    kit.box("stripe_t2", (w + 0.11, 0.05, 0.012), (tx, ty + 0.15, z + 0.026), red)
    # four dining chairs, two a side, backs outward; Grandpa's seat at the head is a backless stool (Ivy's hug)
    wd = mat(kit, "#b98a52", 0.6, 0.15)
    for (px, py) in (G.GRANDMA, G.MOM, G.DAD, G.ME):
        o = -1 if px < 0 else 1
        kit.box("seat", (0.5, 0.5, 0.05), (px + o * 0.05, py, 0.44), wd, bevel=0.01)
        kit.box("chback", (0.05, 0.5, 0.5), (px + o * 0.32, py, 0.72), wd, bevel=0.01)
        for sx in (-1, 1):
            for sy in (-1, 1):
                kit.box("chleg", (0.05, 0.05, 0.42), (px + o * 0.05 + sx * 0.21, py + sy * 0.21, 0.21), wd)
    # Ivy's empty sixth chair at the foot, pulled in under the cloth's edge, and a plate set at it
    cx6, cy6 = G.CHAIR6
    r6 = kit.empty("chair6", (0, 0, 0))
    W["chair6"] = r6
    kit.box("seat6", (0.5, 0.5, 0.05), (cx6, cy6, 0.44), wd, r6, bevel=0.01) if False else kit.box("seat6", (0.5, 0.5, 0.05), (cx6, cy6, 0.44), wd, r6, (0, 0, 0), 0.01)
    kit.box("chback6", (0.5, 0.05, 0.55), (cx6, cy6 - 0.3, 0.74), wd, r6, (0, 0, 0), 0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box("chleg6", (0.05, 0.05, 0.42), (cx6 + sx * 0.21, cy6 + sy * 0.21, 0.21), wd, r6)
    kit.cyl("plate6", 0.2, 0.014, (0.0, 0.14, G.TABLE_Z + 0.027), M(kit, "#fffdf8", 0.3, 0.3), None, (0, 0, 0), n=28)
    kit.box("fork6", (0.025, 0.17, 0.008), (-0.27, 0.14, G.TABLE_Z + 0.025), M(kit, "#d8d8dc", 0.3, 0.6))
    kit.box("nap6", (0.15, 0.15, 0.008), (0.27, 0.14, G.TABLE_Z + 0.025), M(kit, "#e86a5a", 0.8, 0.02), None, (0, 0, 0.3))
    for (px, py) in (G.GRANDMA, G.MOM, G.DAD, G.ME):
        o = -1 if px < 0 else 1
        kit.cyl("plate", 0.14, 0.014, (o * 0.36, py, G.TABLE_Z + 0.027), M(kit, "#fffdf8", 0.3, 0.3), None, (0, 0, 0), n=24)
    gx, gy = G.GRANDPA
    kit.box("stool", (0.5, 0.5, 0.06), (gx, gy, 0.44), M(kit, RED, 0.7, 0.1), bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box("stoolleg", (0.05, 0.05, 0.42), (gx + sx * 0.2, gy + sy * 0.2, 0.21), wd)


def build_cake(kit):
    cx, cy = G.CAKE
    z = G.TABLE_Z + 0.02
    kit.cyl("plate", 0.34, 0.015, (cx, cy, z + 0.008), M(kit, "#fffdf8", 0.3, 0.3), None, (0, 0, 0), n=32)
    sponge = M(kit, "#fff0d0", 0.8, 0.02)
    frost = M(kit, PINK, 0.65, 0.05)
    kit.box("cake", (0.52, 0.4, 0.17), (cx, cy, z + 0.1), M(kit, "#fff8ec", 0.8, 0.02), bevel=0.012)
    # the frosting slab with a thumb-sized scoop out of the front-left corner (the clue): sponge shows in the notch
    zt = z + 0.185 + 0.0
    kit.box("frost_a", (0.52, 0.29, 0.04), (cx, cy + 0.055, zt + 0.02), frost, bevel=0.012)
    kit.box("frost_b", (0.37, 0.11, 0.04), (cx + 0.075, cy - 0.145, zt + 0.02), frost, bevel=0.012)
    kit.box("scoop", (0.15, 0.11, 0.012), (cx - 0.185, cy - 0.145, zt + 0.006), M(kit, "#6a3a1c", 0.8, 0.02))
    kit.box("scoopw", (0.15, 0.012, 0.04), (cx - 0.185, cy - 0.09, zt + 0.02), M(kit, "#8a5226", 0.8, 0.02))
    kit.box("scoopd", (0.012, 0.11, 0.04), (cx - 0.11, cy - 0.145, zt + 0.02), M(kit, "#8a5226", 0.8, 0.02))
    kit.box("scoopcrumb", (0.07, 0.05, 0.02), (cx - 0.3, cy - 0.27, z + 0.024), frost, None, (0, 0, 0.4), 0.008)
    # a frosting border along the sides (1 cm proud), and the sugar "80" in cream numerals on top
    kit.box("frost_side", (0.54, 0.02, 0.035), (cx, cy + 0.205, z + 0.16), frost)
    kit.box("frost_side2", (0.02, 0.4, 0.035), (cx + 0.27, cy, z + 0.16), frost)
    sugar = M(kit, "#fff3c8", 0.5, 0.1)
    px = 0.026
    for i, ch in enumerate("80"):
        bx = cx - 0.07 + i * 0.12
        for r, row in enumerate(FONT[ch]):
            for q, v in enumerate(row):
                if v == "1":
                    kit.box(f"sug{i}{r}{q}", (px, px, 0.016), (bx + (q - 1) * px, cy + 0.02 + (2 - r) * px, zt + 0.048), sugar)
    # the cake server on the cloth, cream handle
    W["server"] = kit.box("server", (0.05, 0.28, 0.012), (cx + 0.22, cy + 0.3, G.TABLE_Z + 0.036), M(kit, "#d8d8dc", 0.3, 0.6), None, (0, 0, 0.1), 0.003)


# ---------------------------------------------------------------------------------------------- the tag and letters
def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    plate = kit.emit("#fff1cf", 1.0, "tagplate")
    edge = kit.emit("#6b4326", 0.6, "tagedge")
    ink = kit.emit("#2a1a0e", 0.5, "tagink")
    dim = kit.emit("#d8c9a8", 0.8, "tagdim")
    gold = kit.emit("#ffb400", 1.7, "taggold")
    pinkm = kit.emit("#ff7fb0", 1.3, "tagpink")
    redm = kit.emit("#e8402e", 1.2, "tagred")
    wh = kit.emit("#ffffff", 1.0, "tagwhite")

    def b(name, size, loc, m, parent=None):
        ob = kit.box(name, size, loc, m, parent or root)
        noshadow(ob)
        return ob
    b("tag.edge", (1.04, 0.66, 0.004), (0, 0, 0.0), edge)
    b("tag.plate", (0.98, 0.6, 0.004), (0, 0, 0.004), plate)
    # row 1: the bird glyph, then the count as big digits: "5" from frame 1, a "6" beside it from the sixth cuckoo
    # ("5 . 6"), and at the end the "6" alone
    b("tag.bbody", (0.12, 0.09, 0.004), (-0.38, 0.14, 0.008), redm)
    b("tag.bhead", (0.06, 0.06, 0.004), (-0.43, 0.19, 0.012), redm)
    b("tag.bbeak", (0.04, 0.025, 0.004), (-0.48, 0.19, 0.012), gold)
    b("tag.btail", (0.06, 0.03, 0.004), (-0.32, 0.12, 0.012), ink)
    W["d5"] = kit.empty("tag.d5", (-0.06, 0.12, 0.012), root)
    text3d(kit, "tag.t5", "5", 0.5, (0, 0, 0), ink, W["d5"], ext=0.002, bevel=0.002, rot=(0, 0, 0))
    W["dot"] = kit.empty("tag.dot", (0.14, 0.1, 0.012), root)
    b("tag.dotb", (0.05, 0.05, 0.004), (0, 0, 0), ink, W["dot"])
    W["d6"] = kit.empty("tag.d6", (0.3, 0.12, 0.012), root)
    text3d(kit, "tag.t6", "6", 0.5, (0, 0, 0), redm, W["d6"], ext=0.002, bevel=0.002, rot=(0, 0, 0))
    # row 2: six tally marks, dim until each cuckoo
    W["ticks"] = []
    for i in range(6):
        x = -0.34 + i * 0.136
        b(f"tag.tkd{i}", (0.05, 0.14, 0.004), (x, -0.13, 0.008), dim)
        piv = kit.empty(f"tag.tk{i}", (x, -0.13, 0.012), root)
        b(f"tag.tkl{i}", (0.05, 0.14, 0.004), (0, 0, 0), gold, piv)
        W["ticks"].append(piv)
    # row 3: a cake glyph (white slab, pink top) and a pink fill bar
    b("tag.ck1", (0.14, 0.04, 0.004), (-0.38, -0.25, 0.008), wh)
    b("tag.ck2", (0.14, 0.03, 0.004), (-0.38, -0.215, 0.012), pinkm)
    b("tag.trk", (0.66, 0.06, 0.004), (0.13, -0.245, 0.008), dim)
    piv = kit.empty("tag.cakefill", (-0.2, -0.245, 0.012), root)
    b("tag.cf", (0.66, 0.06, 0.004), (0.33, 0.0, 0.0), pinkm, piv)
    W["cake"] = piv


def build_letters(kit):
    W["letters"] = {}
    # A over the armchair, B on the curtain's top, C over the closet door, D on the tablecloth skirt
    spots = {"A": (-1.75, 0.75, 1.65), "B": ((G.CURT_X0 + G.CURT_X1) / 2, 1.85, 3.2), "C": (G.CLOSET_X, 2.55, 2.75),
             "D": (0.0, -0.05, 1.0)}
    face = kit.emit("#fff3d0", 1.2, "ltrface")
    rim = kit.emit("#2a1a0e", 0.5, "ltrrim")
    inkm = kit.emit("#0b0b0b", 1.0, "ltrink")
    for k, (x, y, z) in spots.items():
        root = kit.empty(f"ltr.{k}", (x, y, z), None)
        kit.cyl(f"ltr.{k}.rim", 0.4, 0.02, (0, 0.0, 0), rim, root, (math.pi / 2, 0, 0), n=32)
        kit.cyl(f"ltr.{k}.face", 0.36, 0.02, (0, -0.012, 0), face, root, (math.pi / 2, 0, 0), n=32)
        text3d(kit, f"ltr.{k}.t", k, 0.62, (0, -0.03, -0.0), inkm, root, ext=0.012, bevel=0.01)
        noshadow(root)
        W["letters"][k] = (root, (x, y, z))
    # the ring round the curtain
    ring = kit.empty("ring", (1.6, 2.3, 1.5), None)
    rm = kit.emit("#fffdf0", 1.8, "ringglow")
    rd = kit.emit("#4a2a10", 0.6, "ringdark")
    cx = (G.CURT_X0 + G.CURT_X1) / 2
    hw, hh = (G.CURT_X1 - G.CURT_X0) / 2 + 0.2, 1.5
    for nm, sz, loc in (("t", (2 * hw, 0.04, 0.1), (0, 0, hh)), ("b", (2 * hw, 0.04, 0.1), (0, 0, -hh)),
                        ("l", (0.1, 0.04, 2 * hh), (-hw, 0, 0)), ("r", (0.1, 0.04, 2 * hh), (hw, 0, 0))):
        kit.box(f"ring.{nm}", sz, loc, rm, ring)
        kit.box(f"ring.{nm}d", (sz[0] + 0.06 if sz[0] > 0.2 else sz[0] + 0.06, sz[1], sz[2] + 0.06 if sz[2] > 0.2 else sz[2] + 0.06),
                (loc[0], loc[1] + 0.025, loc[2]), rd, ring)
    noshadow(ring)
    W["ring"] = ring
    W["ring0"] = (cx, 2.0, 1.5)


# ---------------------------------------------------------------------------------------------- the cast's extras
def _extras(self, hg, spec, kit, faces):
    import bpy as _b
    n = self.name
    R, Hh = faces.HEAD_R, faces.HEAD_H
    top = Hh / 2
    if spec.get("wbeard"):   # Grandpa: a full white beard, cheeks and chin, clear of the mouth
        gc = kit.plastic(spec["wbeard"], 0.9, spec=0.02)
        kit.box(f"{n}.chin", (0.84, 0.2, 0.3), (0, -0.52, -0.6), gc, hg, bevel=0.08)
        for sx in (-1, 1):
            kit.box(f"{n}.cheek{sx}", (0.14, 0.4, 0.5), (sx * 0.43, -0.3, -0.38), gc, hg, bevel=0.05)
        kit.box(f"{n}.mus", (0.5, 0.1, 0.1), (0, -0.56, -0.38), gc, hg, bevel=0.04)
    if spec.get("crown"):    # a paper party crown in plain gold: a band and five points
        cc = kit.plastic(spec["crown"], 0.45, spec=0.35)
        kit.cyl(f"{n}.crband", R + 0.06, 0.2, (0, 0, top + 0.02), cc, hg, n=24)
        for k in range(5):
            a = k * 2 * math.pi / 5
            kit.box(f"{n}.crpt{k}", (0.17, 0.12, 0.3), ((R + 0.03) * math.sin(a), (R + 0.03) * math.cos(a), top + 0.26), cc, hg,
                    rot=(0, 0, -a), bevel=0.02)
    if spec.get("sneakers"):  # Ivy's bright red sneakers: a long toe, a white sole and stripe, laces, on both feet
        sc = kit.emit("#ff0048", 0.38, "sneakemit")
        so = kit.plastic("#fafafa", 0.6, spec=0.1)
        for sx in (-1, 1):
            leg = _b.data.objects.get(f"{n}.leg{sx}")
            if leg is None:
                continue
            kit.box(f"{n}.sneak{sx}", (0.9, 1.7, 0.6), (0, -0.28, -1.76), sc, leg, bevel=0.1)
            kit.box(f"{n}.sole{sx}", (0.94, 1.76, 0.14), (0, -0.28, -2.04), so, leg, bevel=0.04)
            kit.box(f"{n}.stripe{sx}", (1.0, 0.8, 0.1), (0, -0.2, -1.8), so, leg, bevel=0.02)
            kit.box(f"{n}.lace{sx}", (0.5, 0.6, 0.06), (0, -0.1, -1.44), so, leg, bevel=0.02)
    if spec.get("frosting"):  # Ivy's thumbs: a dab of pink frosting on the front of each hand
        fc = kit.plastic(spec["frosting"], 0.6, spec=0.05)
        for sx in (-1, 1):
            arm = _b.data.objects.get(f"{n}.arm{sx}")
            if arm is not None:
                kit.box(f"{n}.dab{sx}", (0.4, 0.4, 0.6), (0.0, -0.52, -1.7), fc, arm, bevel=0.1)
    if spec.get("curls"):    # long black curls round the face and down to the shoulders (she reads as a sister)
        cc = kit.plastic(spec.get("hair_c", "#15100c"), 0.55, spec=0.15)
        for k in range(8):
            a = k * math.pi / 4
            y = 0.48 * math.cos(a)
            if y < -0.3:
                y = -0.3
            kit.sphere(f"{n}.curl{k}", 0.24, (0.52 * math.sin(a), y + 0.05, top + 0.04), cc, hg, seg=10)
        for sx in (-1, 1):
            for k in range(5):
                kit.sphere(f"{n}.curls{sx}{k}", 0.26, (sx * (R + 0.14), 0.0 + 0.04 * k, 0.4 - 0.36 * k), cc, hg, seg=10)
    if "glasses" in spec.get("extras", []):   # no glossy lens (it threw a white glare): open frames instead
        gc = kit.plastic(spec.get("extra_c", "#222222"), 0.5, spec=0.05)
        for sx in (-1, 1):
            lens = _b.data.objects.get(f"{n}.gl{sx}")
            if lens is not None:
                lens.hide_render = True
            kit.box(f"{n}.glo{sx}", (0.46, 0.04, 0.05), (sx * 0.24, -R - 0.05, -0.17), gc, hg)
            for sx2 in (-1, 1):
                kit.box(f"{n}.gls{sx}{sx2}", (0.05, 0.04, 0.32), (sx * 0.24 + sx2 * 0.21, -R - 0.05, -0.01), gc, hg)


def _install_extras():
    try:
        from blocky import faces, kit as kit_mod, rig
    except Exception:
        return
    if getattr(rig.Character, "_ep149", False):
        return
    orig = rig.Character._accessories

    def accessories(self, hg, spec):
        orig(self, hg, spec)
        _extras(self, hg, spec, kit_mod, faces)

    rig.Character._accessories = accessories
    rig.Character._ep149 = True


# ---------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    _M.clear()
    W.clear()
    _install_extras()
    sun = kit.light("sun", "SUN", (0, -30, 40), 1.3, "#fff0d8", size=0.06, shadow=False)
    kit.aim(sun, (0, 0, 0))
    az, el = 160 * D2R, 52 * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    sun.location = d * 60
    kit.aim(sun, (0, 0, 0))
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.5, "#eef2ff", shadow=False)
    kit.aim(fill, (0, 0, 0))
    # warm soft lamp over the table (casts the soft shadow under the cake and chairs), steady
    lamp = kit.light("tablelamp", "POINT", (0.0, 0.6, 2.9), 300.0, "#fff1d8", size=0.6)
    # a frontal fill from the camera side so faces read
    for nm, loc, tgt, w in (("faceL", (-1.5, -3.5, 2.8), (0, 1.5, 1.2), 300.0), ("faceR", (1.5, -3.5, 2.8), (0, 1.5, 1.2), 300.0)):
        sp = kit.light(nm, "SPOT", loc, w, "#fff4e0", spot=60, blend=0.8, size=0.5, shadow=False)
        kit.aim(sp, tgt)
    build_room(kit)
    build_tag(kit)
    build_letters(kit)
    return {}


# ---------------------------------------------------------------------------------------------- animate
def animate(kit, story, tl, t, ctx):
    sid = next((sh["id"] for sh in tl["shots"] if sh["start"] <= t < sh["end"]), tl["shots"][-1]["id"])
    W["ceiling"].hide_render = sid in MASTERS
    W["south"].hide_render = True
    sh_hold = sid in ("S02", "S06", "S08", "S11a", "S11b", "S11c", "S12")
    for c_ in [W["chair6"]] + list(W["chair6"].children):
        c_.hide_render = not sh_hold
    off_t = ct(tl, "toes_off")
    W["toes"].hide_render = off_t is not None and t >= off_t
    for c_ in W["toes"].children:
        c_.hide_render = W["toes"].hide_render
    sv0, sv1 = ct(tl, "cake_on"), ct(tl, "server_off")
    if sv0 is not None and sv1 is not None and sv0 <= t < sv1:
        W["server"].location = (0.0, 1.62, 0.99)
        W["server"].rotation_euler = (0.15, 0, 0)
    else:
        W["server"].location = (G.CAKE[0] + 0.22, G.CAKE[1] + 0.3, G.TABLE_Z + 0.036)
        W["server"].rotation_euler = (0, 0, 0.1)
    # the clock: the bird out for the opening and at each cuckoo
    ext = trap(t, 0.0, 0.25, 1.0, 0.2)
    t0 = ct(tl, "bird_off")
    if t0 is not None:
        ext = trap(t, 0.0, 0.25, max(0.1, t0), 0.2)
    for i in range(6):
        c = ct(tl, f"ck{i}")
        if c is not None:
            ext = max(ext, trap(t, c - 0.04, 0.09, 0.2, 0.1))
    x, y, z = W["bird0"]
    W["bird"].location = (x, y - 0.22 * ext + 0.06, z)
    W["dhinge"].rotation_euler = (0, 0, -ext * 1.5)
    # the counter tag: "5" from frame 1, a tally mark per cuckoo, "6" beside it at the sixth ("5 . 6"), the "6" alone at the end
    for i, piv in enumerate(W["ticks"]):
        c = ct(tl, f"ck{i}")
        lit = c is not None and t >= c
        piv.scale = (1, 1 if lit else 0.001, 1)
    s6, s6b = ct(tl, "six"), ct(tl, "sixshow")
    u6 = 0.0 if s6b is None else kit.ss((t - s6b) / 0.25)
    uz = 0.0 if s6 is None else kit.ss((t - s6) / 0.4)       # the settle: the 5 and the dot leave, the 6 slides to the middle
    sc6 = max(0.001, u6) * (1.0 + 0.25 * math.sin(min(1.0, (t - (s6b or 0)) / 0.25) * math.pi) if s6b is not None and t >= s6b else 1.0)
    W["d6"].scale = (sc6, sc6, 1)
    W["d6"].location = (0.3 - 0.2 * uz, 0.12, 0.012)
    k5 = max(0.001, 1 - uz)
    W["d5"].scale = (k5, k5, 1)
    W["dot"].scale = (max(0.001, u6 * (1 - uz)), max(0.001, u6 * (1 - uz)), 1)
    c0, c1 = ct(tl, "cake_on"), ct(tl, "cake_off")
    if c0 is not None and c1 is not None:
        u = min(1.0, max(0.0, (t - c0) / max(0.1, c1 - c0)))
        W["cake"].scale = (max(0.001, u * 0.82), 1, 1)
    else:
        W["cake"].scale = (0.001, 1, 1)
    # the letters pop (0.15 s), A to D, hold, and go when the answer starts
    off = ct(tl, "ltr_off")
    for k in "ABCD":
        root, loc = W["letters"][k]
        c = ct(tl, f"ltr{k}")
        if c is None or t < c or (off is not None and t >= off) or (k == "D" and sid == "S09"):
            root.location = (loc[0], loc[1], -60.0)
            continue
        u = (t - c) / 0.15
        sc = kit.ss(u) * (1.0 + 0.12 * math.sin(min(1.0, u) * math.pi))
        root.location = loc
        root.scale = (sc, sc, sc)
    # the ring round the curtain
    r0, r1 = ct(tl, "ring"), ct(tl, "ring_off")
    ring = W["ring"]
    if r0 is None or t < r0 or (r1 is not None and t > r1):
        ring.location = (0, 0, -60.0)
    else:
        u = kit.ss((t - r0) / 0.3)
        sc = 1.35 - 0.35 * u
        ring.location = W["ring0"]
        ring.scale = (sc, 1, sc)
    return {}
