"""ep123 "sorry shrink": a sunny glassed-in porch, one square card table with a yellow-and-white checked cloth.
Aunt Mae (13 cm tall, an evenly scaled R6 rig) stands on the cloth beside a white mug with a red stripe at her
height. Cards (plain backs with a diamond glyph, faces with suit glyphs only), a score pad of tally strokes, a
wall calendar glyph, a brass corner cap with two coral strokes.

One sun, fixed: nothing here glows, pulses or changes light. What the story moves is driven by cues (see animate):
the rule meter (a camera child: a ruler glyph and Mae's height in inches, a second line for mine), Mae's shrink,
who sits, which of my hands is on the cloth, the calendar's arrows, the nudged card, the slap, the neighbor's bike.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {}
T = G.T
SUN = dict(sun=3.4, sun_col="#fff0d8", el=48.0, az=205.0, fill=1.3, fill_col="#eef2ff")


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def sample(name, tl, t, defaults):
    cur, prev = dict(defaults), dict(defaults)
    for c in tl["cues"]:
        if c["name"] != name:
            continue
        if c["t"] > t:
            break
        prev = dict(cur)
        cur.update({k: v for k, v in c.items() if k in defaults})
        dur = c.get("dur", 0.0)
        if dur > 0 and t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            return {k: (prev[k] + (cur[k] - prev[k]) * u if isinstance(cur[k], (int, float)) else cur[k]) for k in cur}
    return cur


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def _hide(ob, hide):
    ob.hide_render = hide
    for c in ob.children_recursive:
        c.hide_render = hide


# ---------------------------------------------------------------------------------------------- cards
SUITS = {"dia": "#e2463b", "dot": "#2a2a40", "sq": "#3f7fe0", "tri": "#2f9f4a"}


def pip(kit, name, kind, x, y, z, parent, s=0.016):
    m = kit.plastic(SUITS[kind], 0.5, spec=0.1)
    if kind == "dia":
        kit.box(name, (s, s, 0.002), (x, y, z), m, parent, rot=(0, 0, 45 * D2R))
    elif kind == "dot":
        kit.cyl(name, s * 0.62, 0.002, (x, y, z), m, parent, n=12)
    elif kind == "sq":
        kit.box(name, (s * 0.9, s * 0.9, 0.002), (x, y, z), m, parent)
    else:
        kit.box(name, (s * 0.5, s * 1.1, 0.002), (x, y, z), m, parent, rot=(0, 0, 30 * D2R))
        kit.box(name + "b", (s * 0.5, s * 1.1, 0.002), (x, y, z), m, parent, rot=(0, 0, -30 * D2R))


def card(kit, name, loc, rotz, face, kind="dia", n=1, w=0.11, l=0.16, back="#3f7fe0"):
    """A card lying flat; loc is the centre of its underside. Returns the empty that carries it."""
    root = kit.empty(name, loc, rot=(0, 0, rotz * D2R))
    paper = kit.plastic("#fffaf0", 0.55, spec=0.1)
    kit.box(f"{name}.body", (w, l, 0.003), (0, 0, 0.0015), paper, root, bevel=0.0008)
    top = 0.003
    if face:
        # corner glyphs plus n big glyphs down the middle
        pip(kit, f"{name}.c1", kind, -w * 0.32, l * 0.38, top + 0.0005, root, 0.014)
        pip(kit, f"{name}.c2", kind, w * 0.32, -l * 0.38, top + 0.0005, root, 0.014)
        spots = {1: [(0, 0)], 2: [(0, 0.2 * l), (0, -0.2 * l)], 3: [(0, 0.26 * l), (0, 0), (0, -0.26 * l)]}[min(3, n)]
        for i, (px, py) in enumerate(spots):
            pip(kit, f"{name}.p{i}", kind, px, py, top + 0.0005, root, 0.03)
    else:
        kit.box(f"{name}.back", (w - 0.014, l - 0.014, 0.001), (0, 0, top + 0.0003), kit.plastic(back, 0.55, spec=0.1), root)
        pip(kit, f"{name}.g", "dia", 0, 0, top + 0.001, root, 0.04)
        kit.box(f"{name}.gi", (0.02, 0.02, 0.002), (0, 0, top + 0.0016), kit.plastic("#fffaf0", 0.5), root, rot=(0, 0, 45 * D2R))
    return root


def fan(kit, name, base, axis_yaw, spread, face, kinds, back="#3f7fe0", z0=T, count=5, reach=0.065):
    """count cards fanned flat from `base`; their long axes point `axis_yaw` degrees round from -y."""
    cards = []
    for i in range(count):
        a = axis_yaw + (i - (count - 1) / 2) * spread
        rz = 180.0 + a
        dx, dy = -math.sin(rz * D2R), math.cos(rz * D2R)
        c = card(kit, f"{name}{i}", (base[0] + reach * dx, base[1] + reach * dy, z0 + 0.0006 + 0.0036 * i), rz, face,
                 kinds[i % len(kinds)], 1 + i % 3, back=back)
        cards.append(c)
    return cards


# ---------------------------------------------------------------------------------------------- the rule meter
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "4": "bcfg", "5": "acdfg", "6": "acdefg", "9": "abcdfg"}


def seven(kit, root, name, cx, cy, w, h, th, mat):
    """Seven segments of a digit, centred (cx, cy), as flat boxes on the tag. Returns {segment: object}."""
    out = {}
    hh = h / 2
    defs = {"a": (0, hh - th / 2, w, th), "d": (0, -hh + th / 2, w, th), "g": (0, 0, w, th),
            "f": (-w / 2 + th / 2, hh / 2, th, hh), "b": (w / 2 - th / 2, hh / 2, th, hh),
            "e": (-w / 2 + th / 2, -hh / 2, th, hh), "c": (w / 2 - th / 2, -hh / 2, th, hh)}
    for s, (dx, dy, sx, sy) in defs.items():
        ob = kit.box(f"{name}.{s}", (sx, sy, 0.004), (cx + dx, cy + dy, 0.008), mat, root)
        noshadow(ob)
        out[s] = ob
    return out


def build_tag(kit):
    """The rule meter: a cream plate top-left on the camera. Line one: a ruler glyph and Mae's height in inches
    (a big digit). Line two (from L17 on): my height, 6'0" then 5'11"."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    cream = kit.emit("#fff1cc", 0.9, "tagcream")
    edge = kit.emit("#3a2210", 0.5, "tagedge")
    ink = kit.emit("#3a2210", 0.6, "tagnum")
    coral = kit.emit("#e8503c", 0.8, "tagcoral")
    blue = kit.emit("#2f6fd6", 0.8, "tagblue")

    def b(name, size, loc, mat, rot=0.0, parent=None):
        ob = kit.box(name, (size[0], size[1], 0.004), (loc[0], loc[1], loc[2]), mat, parent or root,
                     rot=(0, 0, rot * D2R))
        noshadow(ob)
        return ob

    b("tag.edge", (1.06, 0.66), (0, 0, 0.0), edge)
    b("tag.plate", (1.0, 0.6), (0, 0, 0.004), cream)
    # the ruler glyph: a long coral bar standing upright with five ticks
    b("tag.rbar", (0.17, 0.5), (-0.33, 0, 0.008), coral)
    for i in range(5):
        b(f"tag.rtick{i}", (0.11 if i % 2 == 0 else 0.07, 0.035), (-0.33 + 0.07 - (0.0 if i % 2 == 0 else 0.02), -0.2 + i * 0.1, 0.012),
          cream)
    W["d1"] = seven(kit, root, "tag.d1", 0.2, 0.0, 0.36, 0.5, 0.085, ink)
    # line two: a person glyph, then 6'0" / 5'11" in three small digits
    r2 = kit.empty("tag2", (0, -0.7, 0), root)
    W["tag2"] = r2
    b("tag2.edge", (1.06, 0.56), (0, 0, 0.0), edge, parent=r2)
    b("tag2.plate", (1.0, 0.5), (0, 0, 0.004), cream, parent=r2)
    b("tag2.head", (0.1, 0.1), (-0.36, 0.14, 0.008), blue, parent=r2)
    b("tag2.body", (0.17, 0.2), (-0.36, -0.03, 0.008), blue, parent=r2)
    b("tag2.legs", (0.17, 0.13), (-0.36, -0.2, 0.008), blue, parent=r2)
    W["d2"] = [seven(kit, r2, f"tag2.d{i}", x, 0.0, 0.17, 0.36, 0.05, ink) for i, x in enumerate((-0.14, 0.14, 0.34))]
    W["ticks2"] = [b("tag2.foot", (0.04, 0.1), (-0.02, 0.13, 0.008), ink, 20, r2),
                   b("tag2.in1", (0.04, 0.1), (0.5 - 0.0, 0.13, 0.008), ink, 20, r2)]
    W["ticks2"].append(b("tag2.in2", (0.04, 0.1), (0.54 - 0.0, 0.13, 0.008), ink, 20, r2))
    # dummy to keep names unique
    return root


def set_digit(segs, ch):
    on = SEG.get(ch, "")
    for s, ob in segs.items():
        ob.hide_render = s not in on


# ---------------------------------------------------------------------------------------------- the set
def brass_cap(kit):
    """The table's lower-right corner cap (seen from the front): brass with two coral scratches. A plain tally."""
    brass = kit.metal("#c9a23c", 0.35)
    x, y = 0.47, -0.47
    W["cap"] = []
    W["cap"].append(kit.box("cap.plate", (0.09, 0.09, 0.012), (x - 0.0, y, T + 0.002), brass, bevel=0.002))
    for i, dx in enumerate((-0.012, 0.012)):
        W["cap"].append(kit.box(f"cap.stroke{i}", (0.006, 0.06, 0.003), (x + dx * 1.8, y, T + 0.0095), kit.plastic("#ff7f6b", 0.5), rot=(0, 0, 12 * D2R * (1 if i else -1))))
    for ob in W["cap"]:
        ob["bx"], ob["by"] = ob.location.x, ob.location.y


def build_table(kit):
    wood = kit.plastic("#fffaf0", 0.6, spec=0.1)
    kit.box("table.top", (1.04, 1.04, 0.05), (0, 0, T - 0.035), wood, bevel=0.006)
    cloth = kit.checker("#ffd84d", "#fffaf0", 14.0, "cloth", 0.8)
    kit.box("table.cloth", (1.0, 1.0, 0.02), (0, 0, T - 0.01), cloth)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"table.leg{sx}{sy}", (0.06, 0.06, T - 0.06), (sx * 0.47, sy * 0.47, (T - 0.06) / 2), wood)
    # the cloth hangs a little at the front
    kit.box("table.drape", (1.0, 0.012, 0.16), (0, -0.506, T - 0.09), cloth)
    kit.box("table.draper", (0.012, 1.0, 0.16), (0.506, 0, T - 0.09), cloth)
    kit.box("table.drapel", (0.012, 1.0, 0.16), (-0.506, 0, T - 0.09), cloth)
    brass_cap(kit)
    # the mug (Mae's height plus an inch), a coffee disc, a handle and the red height stripe
    mx, my = G.MUG
    white = kit.plastic("#fffaf0", 0.35, spec=0.4)
    kit.cyl("mug.body", 0.045, G.MUG_H, (mx, my, T + G.MUG_H / 2), white, n=24)
    kit.cyl("mug.coffee", 0.039, 0.003, (mx, my, T + G.MUG_H - 0.0004), kit.plastic("#6a3a1e", 0.4), n=24)
    kit.cyl("mug.stripe", 0.0465, 0.014, (mx, my, T + G.MAE_H), kit.plastic("#e2463b", 0.5), n=24)
    kit.box("mug.handle", (0.034, 0.012, 0.09), (mx - 0.058, my, T + 0.095), white, bevel=0.004)
    kit.box("mug.handle2", (0.012, 0.012, 0.062), (mx - 0.074, my, T + 0.095), white)
    # a plate of shortbread
    kit.cyl("plate", 0.085, 0.008, (-0.31, -0.28, T + 0.004), kit.plastic("#fffaf0", 0.4, spec=0.3), n=20)
    for i, (dx, dy, r) in enumerate(((-0.02, 0.0, 10), (0.02, 0.01, -15), (0.0, -0.025, 80))):
        kit.box(f"short{i}", (0.07, 0.025, 0.012), (-0.31 + dx, -0.28 + dy, T + 0.014), kit.plastic("#e8b868", 0.7), rot=(0, 0, r * D2R), bevel=0.003)
    # the score pad: two columns, hers (coral) with sixty tally strokes in twelve fives, mine (blue) empty
    px, py = G.PAD
    pad = kit.empty("pad", (px, py, T), rot=(0, 0, 14 * D2R))
    kit.box("pad.back", (0.24, 0.30, 0.012), (0, 0, 0.006), kit.plastic("#d8c08c", 0.8), pad)
    kit.box("pad.sheet", (0.22, 0.28, 0.003), (0, 0, 0.0135), kit.plastic("#fffdf4", 0.8), pad)
    ink = kit.plastic("#2a2a40", 0.7)
    kit.box("pad.mid", (0.003, 0.26, 0.002), (0, 0, 0.0158), kit.plastic("#8a8a94", 0.8), pad)
    kit.box("pad.head", (0.21, 0.004, 0.002), (0, 0.105, 0.0158), kit.plastic("#8a8a94", 0.8), pad)
    kit.cyl("pad.coral", 0.016, 0.003, (-0.055, 0.12, 0.016), kit.plastic("#ff7f6b", 0.6), pad, n=14)
    kit.cyl("pad.blue", 0.016, 0.003, (0.055, 0.12, 0.016), kit.plastic("#3f7fe0", 0.6), pad, n=14)
    n = 0
    for g in range(12):
        gx = -0.085 + (g % 2) * 0.052
        gy = 0.082 - (g // 2) * 0.034
        for s in range(4):
            kit.box(f"pad.t{n}", (0.0032, 0.026, 0.002), (gx - 0.016 + s * 0.0105, gy, 0.0158), ink, pad)
            n += 1
        kit.box(f"pad.t{n}", (0.0032, 0.045, 0.002), (gx, gy, 0.0162), ink, pad, rot=(0, 0, 62 * D2R))
        n += 1
    # the two fans: Mae's winning hand (faces), mine (backs), then my winning hand (faces) for L14 and L15
    fx, fy = 0.38, -0.395
    W["maecards"] = fan(kit, "mc", (fx, fy), -85, 24, True, ["dia", "dot", "sq", "tri", "dia"], z0=T)
    W["minecards"] = fan(kit, "yc", (-0.02, 0.50), 0, 14, False, ["dia"], back="#3f7fe0", z0=T)
    W["wincards"] = fan(kit, "wc", (-0.02, 0.50), 0, 14, True, ["sq", "tri", "dot", "dia", "sq"], z0=T)
    W["wincards_z"] = [c.location.z for c in W["wincards"]]
    W["wincards_xy"] = [(c.location.x, c.location.y) for c in W["wincards"]]
    W["maelast"] = W["maecards"][-1]
    W["maelast_loc"] = tuple(W["maelast"].location)


def build_porch(kit):
    wallc = kit.plastic("#8fc4ee", 0.85, spec=0.05)
    white = kit.plastic("#fffaf0", 0.75, spec=0.05)
    wick = kit.plastic("#f4efe4", 0.8, spec=0.05)
    floor = kit.planks("#e8d0a0", "#d8bc88", 1.0)
    kit.plane("floor", (7, 6), (0, 0.4, 0.0), floor)
    # the back wall (y = 2.6): blue siding below, a band of windows with white mullions, a lintel above
    wy = 2.6
    kit.box("wall.low", (7, 0.2, 0.9), (0, wy, 0.45), wallc)
    kit.box("wall.lintel", (7, 0.2, 0.5), (0, wy, 2.55), wallc)
    kit.box("wall.sill", (7, 0.3, 0.05), (0, wy - 0.02, 0.92), white)
    for i in range(-3, 4):
        kit.box(f"wall.mull{i}", (0.07, 0.12, 1.4), (i * 1.0, wy - 0.02, 1.6), white)
    # sides, low, so a wide never shows the void
    for sx in (-1, 1):
        kit.box(f"wall.side{sx}", (0.2, 6, 3.0), (sx * 3.5, 0.4, 1.5), wallc)
    # outside the glass: lawn, a white picket fence, a sidewalk, houses and sky
    kit.plane("lawn", (60, 30), (0, 14, -0.01), kit.grime("#79c850", 0.86, 1.4, "lawn", 0.95))
    kit.plane("walk", (60, 1.6), (0, 9.0, 0.0), kit.plastic("#d8d4cc", 0.8))
    for i in range(-14, 15):
        kit.box(f"fence{i}", (0.1, 0.06, 0.6), (i * 0.35, 3.4, 0.3), white)
    kit.box("fence.rail", (12, 0.05, 0.06), (0, 3.4, 0.4), white)
    kit.box("house.far", (9, 0.4, 3.6), (-3.0, 14.0, 1.8), kit.plastic("#ffb98a", 0.85, spec=0.05))
    kit.box("house.far2", (7, 0.4, 3.0), (7.0, 15.0, 1.5), kit.plastic("#cfe8c0", 0.85, spec=0.05))
    kit.box("house.roof", (9.4, 0.5, 0.4), (-3.0, 14.0, 3.8), kit.plastic("#b5472f", 0.8))
    # hanging ferns (green clusters on a cord) and a wicker chair on each side
    leaf = kit.plastic("#5cc46a", 0.8, spec=0.05)
    leaf2 = kit.plastic("#43a85a", 0.8, spec=0.05)
    for k, fx in enumerate((-1.45, 1.35)):
        kit.cyl(f"fern{k}.pot", 0.12, 0.14, (fx, 2.3, 1.95), kit.plastic("#d8704a", 0.7), n=12)
        for j in range(9):
            a = j * 40 * D2R
            kit.box(f"fern{k}.l{j}", (0.07, 0.4, 0.04), (fx + 0.2 * math.sin(a), 2.3 + 0.2 * math.cos(a), 1.78), leaf if j % 2 else leaf2,
                    rot=(0.8 * math.cos(a), 0.8 * math.sin(a), a))
    for k, cx in enumerate((-1.7, 1.7)):
        kit.box(f"wchair{k}.seat", (0.6, 0.6, 0.08), (cx, 0.4, 0.45), wick, bevel=0.02)
        kit.box(f"wchair{k}.back", (0.6, 0.08, 0.9), (cx, 0.72, 0.9), wick, bevel=0.02)
        for sx in (-1, 1):
            for sy in (-1, 1):
                kit.box(f"wchair{k}.l{sx}{sy}", (0.06, 0.06, 0.44), (cx + sx * 0.26, 0.4 + sy * 0.26, 0.22), wick)
    # my chair across the table
    cx, cy = G.CHAIR
    kit.box("chair.seat", (0.55, 0.55, 0.07), (cx, cy, 0.46), wick, bevel=0.02)
    kit.box("chair.back", (0.55, 0.07, 0.9), (cx, cy + 0.27, 0.95), wick, bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"chair.l{sx}{sy}", (0.06, 0.06, 0.43), (cx + sx * 0.24, cy + sy * 0.24, 0.21), wick)
    # the wall calendar: a red header, seven columns of white cells, Sundays in the first column circled in red,
    # a down arrow that lands on each circled Sunday in turn
    cx_, cy_ = G.CAL
    cal = kit.empty("cal", (cx_, cy_ - 0.02, 1.25))
    kit.box("cal.card", (0.62, 0.02, 0.74), (0, 0, 0), kit.plastic("#fffaf0", 0.7), cal)
    kit.box("cal.head", (0.62, 0.025, 0.16), (0, -0.003, 0.29), kit.plastic("#e2463b", 0.6), cal)
    for i, rx in enumerate((-0.16, 0.16)):
        kit.cyl(f"cal.ring{i}", 0.018, 0.04, (rx, -0.01, 0.37), kit.plastic("#8a8a94", 0.4), cal, rot=(math.pi / 2, 0, 0), n=10)
    gcell = kit.plastic("#d8d4c4", 0.8)
    W["arrows"] = []
    for r in range(4):
        for c in range(7):
            x = -0.255 + c * 0.085
            z = 0.17 - r * 0.115
            kit.box(f"cal.c{r}{c}", (0.07, 0.006, 0.09), (x, -0.013, z), gcell, cal)
            if c > 0:
                kit.box(f"cal.d{r}{c}", (0.014, 0.006, 0.014), (x, -0.018, z), kit.plastic("#8a8a94", 0.7), cal)
    red = kit.plastic("#e2463b", 0.5)
    for r in range(3):
        x = -0.255
        z = 0.17 - r * 0.115
        for nm, (sx, sz, dx, dz) in {"t": (0.082, 0.008, 0, 0.048), "b": (0.082, 0.008, 0, -0.048), "l": (0.008, 0.1, -0.04, 0),
                                     "r": (0.008, 0.1, 0.04, 0)}.items():
            kit.box(f"cal.ring{r}{nm}", (sx, 0.008, sz), (x + dx, -0.022, z + dz), red, cal)
        arrow = kit.empty(f"cal.arrow{r}", (x, -0.03, z + 0.01), cal)
        kit.box(f"cal.arrow{r}.s", (0.026, 0.01, 0.05), (0, 0, 0.02), kit.plastic("#3f7fe0", 0.5), arrow)
        kit.box(f"cal.arrow{r}.h", (0.054, 0.01, 0.054), (0, 0, -0.03), kit.plastic("#3f7fe0", 0.5), arrow, rot=(0, 45 * D2R, 0))
        W["arrows"].append(arrow)
    # the neighbor's bike on the lawn (a frame, two wheels, a seat, no lettering)
    nx, ny = G.NEIGH
    bike = kit.empty("bike", (nx, ny + 0.5, 0.0))
    W["bike"] = bike
    dark = kit.plastic("#2a2a40", 0.6)
    redb = kit.plastic("#e2463b", 0.5)
    for sx in (-1, 1):
        kit.cyl(f"bike.w{sx}", 0.34, 0.05, (sx * 0.55, 0, 0.34), dark, bike, rot=(math.pi / 2, 0, 0), n=18)
    kit.box("bike.f1", (1.1, 0.05, 0.05), (0.0, 0, 0.55), redb, bike, rot=(0, 0.4, 0))
    kit.box("bike.f2", (0.7, 0.05, 0.05), (0.2, 0, 0.5), redb, bike, rot=(0, -0.7, 0))
    kit.box("bike.seat", (0.22, 0.08, 0.05), (-0.35, 0, 0.9), dark, bike)
    kit.box("bike.bar", (0.05, 0.4, 0.05), (0.56, 0, 0.95), dark, bike)


def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    sun = kit.light("sun", "SUN", (0, -30, 40), 1.0, SUN["sun_col"], size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, SUN["fill_col"], shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    az, el = SUN["az"] * D2R, SUN["el"] * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    sun.location = d * 60
    kit.aim(sun, (0, 0, 0))
    build_porch(kit)
    build_table(kit)
    build_tag(kit)
    return {}


# ---------------------------------------------------------------------------------------------- finishing touches
def first_frame(kit, story):
    gp = bpy.data.objects.get("mae.headg")
    if gp is not None:
        pearl = kit.plastic("#fffaf0", 0.2, spec=0.7)
        gray = kit.plastic("#c4c4d0", 0.85, spec=0.05)
        # glasses: no lens fill (it read as a bandage), only red rims round each lens
        frame = kit.plastic("#d22f3c", 0.4)
        for sx in (-1, 1):
            ln = bpy.data.objects.get(f"mae.gl{sx}")
            if ln is None:
                continue
            ly = ln.location.y - 0.01
            cx, cz = ln.location.x, ln.location.z
            bpy.data.objects.remove(ln, do_unlink=True)
            kit.box(f"mae.glr_b{sx}", (0.46, 0.04, 0.05), (cx, ly, cz - 0.16), frame, gp)
            for ex in (-1, 1):
                kit.box(f"mae.glr_s{sx}{ex}", (0.05, 0.04, 0.34), (cx + ex * 0.205, ly, cz), frame, gp)
        for sx in (-1, 1):
            kit.sphere(f"mae.pearl{sx}", 0.1, (sx * 0.68, -0.05, -0.32), pearl, gp, seg=8)
            kit.box(f"mae.pearlh{sx}", (0.05, 0.05, 0.12), (sx * 0.68, -0.05, -0.22), pearl, gp)
        # a gray perm: little rounded curls round the crown
        for i in range(12):
            a = i * 30 * D2R
            r = 0.52
            kit.sphere(f"mae.curl{i}", 0.2, (r * math.sin(a) * 1.15, r * math.cos(a) * 0.7, 0.45 + 0.1 * math.cos(a * 2)), gray, gp, seg=8)
    mh = bpy.data.objects.get("me.arm1")
    if mh is not None:
        kit.box("me.watch", (1.15, 1.15, 0.35), (0, 0, -1.55), kit.plastic("#2a2a40", 0.4, spec=0.4), mh, bevel=0.04)
        kit.box("me.watchface", (0.7, 1.18, 0.24), (0, 0, -1.55), kit.plastic("#fffaf0", 0.4), mh)
    nb = bpy.data.objects.get("neighbor.headg")
    if nb is not None:
        kit.box("nb.cap", (1.35, 1.35, 0.35), (0, 0, 0.75), kit.plastic("#e2463b", 0.5), nb, bevel=0.06)


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        W["inited"] = True
        first_frame(kit, story)
        for who in ("me", "neighbor", "mae"):
            ro = bpy.data.objects.get(who)
            if ro is not None:
                for ob in ro.children_recursive:
                    ob.hide_render = ro.hide_render
        mae = bpy.data.objects.get("mae")
        W["mae_sc"] = tuple(mae.scale) if mae else (1, 1, 1)
    # who sits (hips on the seat)
    sits = {}
    for c in tl["cues"]:
        if c["name"] == "sit" and c["t"] <= t:
            sits[c["who"]] = c
    for who, c in sits.items():
        root = bpy.data.objects.get(who)
        if c.get("on") and root is not None:
            root.location.z += 0.62 - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    # Aunt Mae: an inch shorter at L09 (0.8x), a slide over 0.8 s
    mae = bpy.data.objects.get("mae")
    sk = sample("shrink", tl, t, {"k": 0.0})
    if mae is not None:
        f = 1.0 - 0.2 * sk["k"]
        mae.scale = tuple(v * f for v in W["mae_sc"])
    # the tag
    h1 = sample("h1", tl, t, {"v": 5.0})
    set_digit(W["d1"], str(int(round(h1["v"]))))
    t2 = sample("tag2", tl, t, {"on": 0.0, "v": 0.0})
    W["tag2"].hide_render = t2["on"] < 0.5
    for ob in W["tag2"].children_recursive:
        ob.hide_render = t2["on"] < 0.5
    v2 = int(round(t2["v"]))
    d2 = W["d2"]
    on2 = t2["on"] >= 0.5
    set_digit(d2[0], ("6" if v2 == 0 else "5") if on2 else "")
    set_digit(d2[1], ("0" if v2 == 0 else "1") if on2 else "")
    set_digit(d2[2], ("" if v2 == 0 else "1") if on2 else "")
    ticks = W["ticks2"]
    ticks[0].hide_render = t2["on"] < 0.5
    ticks[1].hide_render = t2["on"] < 0.5 or v2 == 0
    ticks[2].hide_render = t2["on"] < 0.5 or v2 == 0
    # tag position: top-left on the camera, sized by the lens
    lens = 40.0
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next((s for s in story["shots"] if s["id"] == shot["id"]), None)
    if spec:
        keys = spec["cam"]
        u2 = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
        lens = keys[0][3]
        if len(keys) > 1:
            for a, b in zip(keys, keys[1:]):
                if u2 <= b[0]:
                    lens = a[3] + (b[3] - a[3]) * ss((u2 - a[0]) / max(1e-6, b[0] - a[0]))
                    break
            else:
                lens = keys[-1][3]
    dist = 0.3
    h2 = dist * 12.0 / lens
    w2 = h2 * 9.0 / 16.0
    s = 0.62 * w2
    W["tag"].scale = (s, s, s)
    W["tag"].location = (-0.86 * w2 + 0.53 * s, 0.88 * h2 - 0.33 * s, -dist)
    # the calendar's arrows land in turn (0.4 s apart), staying once landed
    n = int(round(sample("arrows", tl, t, {"n": 0.0})["n"]))
    for i, a in enumerate(W["arrows"]):
        _hide(a, i >= n)
    # Mae's last card, nudged into the fan with her shoe
    nd = sample("nudge", tl, t, {"k": 0.0, "dur": 0})
    k = ss(nd["k"])
    lc = W["maelast"]
    bx, by, bz = W["maelast_loc"]
    lc.location = (bx + 0.03 * (1 - k), by + 0.02 * (1 - k), bz)
    # who has which cards on the cloth
    sm = sample("mine", tl, t, {"on": 1.0})
    for c in W["minecards"]:
        _hide(c, sm["on"] < 0.5)
    cm = sample("capmove", tl, t, {"dx": 0.0, "dy": 0.0})
    for ob in W["cap"]:
        ob.location = (ob.get("bx") + cm["dx"], ob.get("by") + cm["dy"], ob.location.z)
    mcs = sample("maecards", tl, t, {"on": 1.0})
    for c in W["maecards"]:
        _hide(c, mcs["on"] < 0.5)
    sw = sample("win", tl, t, {"on": 0.0, "slap": 0.0})
    lift = 0.0
    if sw["on"] >= 0.5:
        # the slap: the hand drops from 6 cm to the cloth in 0.18 s, then settles
        sl = sample("slap", tl, t, {"u": 1.0})
        lift = 0.06 * (1.0 - min(1.0, sl["u"]) ** 2)
    wp = sample("winpos", tl, t, {"dx": 0.0, "dy": 0.0})
    for c, z, xy in zip(W["wincards"], W["wincards_z"], W["wincards_xy"]):
        _hide(c, sw["on"] < 0.5)
        c.location = (xy[0] + wp["dx"], xy[1] + wp["dy"], z + lift)
    # the neighbor's bike
    bk = sample("bike", tl, t, {"on": 0.0})
    _hide(W["bike"], bk["on"] < 0.5)
    return {"sun": SUN["sun"], "fill": SUN["fill"]}

