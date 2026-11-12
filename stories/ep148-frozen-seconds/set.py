"""ep148 "frozen seconds": a bright city park at noon: a round stone fountain with a tall centre jet, lawns, trees, a
hedge, a pretzel cart with a green umbrella, benches, a pale stone plaza. Two small montage places far off along x
(an uncle's kitchen, the lady next door's front path).

ONE sun, never changed: the freeze is a motion stop only. No colour drain, no dimming, no flash. The jet's droplets move
until the freeze cue and hold still after it (steady small highlights, nothing twinkles), and move again at the thaw.
The rule meter is a cream tag on the camera (top-left): a pause glyph and "1461", then a minutes:seconds count down.
Cues read by animate(): tag (mode, s), freeze (f: 0 running, 1 stopped), sit_<who> (s), note_me / note_leo (m: 0 hidden,
1 going into the pocket, 2 on the palm), bite (b).
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

W = {}
SIT = -math.pi / 2 * 0.97
FX, FY = G.F


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


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


# ------------------------------------------------------------------------------------------------ the park
def build_park(kit):
    pl = kit.plastic
    kit.plane("lawn", (500, 500), (0, 0, -0.03), pl("#5cc45a", 0.9, spec=0.05))
    stone = pl("#d6cfbd", 0.85, spec=0.05)
    kit.cyl("plaza", 4.3, 0.05, (FX, FY, 0.0), stone, n=40)
    kit.box("path", (3.2, 16.0, 0.05), (0, -4.0, 0.0), stone)
    for k in range(6):   # pale joints in the path
        kit.box(f"path.joint{k}", (3.2, 0.03, 0.055), (0, -11.0 + 2.5 * k, 0.0), pl("#cfc8b8", 0.9))
    # hedge and trees behind the fountain, so every low angle has green behind it
    hedge = pl("#3b8a40", 0.9, spec=0.03)
    kit.box("hedge", (30, 1.3, 1.1), (0, 14.5, 0.5), hedge, bevel=0.15)
    kit.box("hedge.w", (1.3, 12.0, 1.1), (-15.0, 9.0, 0.5), hedge, bevel=0.15)
    kit.box("hedge.e", (1.3, 12.0, 1.1), (15.0, 9.0, 0.5), hedge, bevel=0.15)
    tr = "#d4f0c4"
    for i, (x, y, h) in enumerate([(-11, 17.5, 7.5), (-5.5, 19.0, 8.0), (-0.5, 17.8, 7.0), (5.0, 19.5, 8.5), (10.5, 17.5, 7.5),
                                   (-16.5, 11.0, 7.0), (16.5, 10.0, 7.5), (-16.5, 3.0, 6.5), (16.5, 2.0, 7.0)]):
        kit.prop("commontree_1" if i % 2 == 0 else "sub_tree_large", (x, y, 0), rot=17 * i, height=h, tint=tr)
    for i, (x, y) in enumerate([(-9, 7), (9.5, 8.0), (-12, 13), (12, 13)]):
        kit.prop("bush_1" if i % 2 else "bush_2", (x, y, 0), height=1.2, tint=tr)
    # benches
    wood = pl("#b9874f", 0.7)
    for k, (bx, by, rot) in enumerate([(-6.0, 9.5, 0), (6.0, 9.5, 0)]):
        kit.box(f"bench{k}.seat", (1.7, 0.5, 0.08), (bx, by, 0.45), wood)
        kit.box(f"bench{k}.back", (1.7, 0.08, 0.5), (bx, by + 0.28, 0.75), wood)
        for sx in (-1, 1):
            kit.box(f"bench{k}.leg{sx}", (0.08, 0.45, 0.45), (bx + sx * 0.75, by, 0.22), pl("#4a4a50", 0.6))
    # lamppost
    kit.cyl("lamp.pole", 0.06, 3.6, (5.8, 1.5, 1.8), pl("#33363c", 0.5), n=8)
    kit.sphere("lamp.globe", 0.22, (5.8, 1.5, 3.7), pl("#f4f0e0", 0.4), seg=10)
    # the plain pretzel cart with a green umbrella (no lettering)
    cx, cy = -7.0, 4.0
    kit.box("cart.body", (1.6, 0.9, 0.8), (cx, cy, 0.7), wood, bevel=0.03)
    kit.box("cart.top", (1.7, 1.0, 0.06), (cx, cy, 1.13), pl("#a67844", 0.6))
    for sx in (-1, 1):
        kit.cyl(f"cart.wheel{sx}", 0.3, 0.1, (cx + sx * 0.85, cy, 0.3), pl("#2a2a2e", 0.7), rot=(0, math.pi / 2, 0), n=14)
    kit.cyl("cart.pole", 0.03, 2.2, (cx, cy, 2.1), pl("#cfd2d6", 0.4, spec=0.7), n=8)
    kit.cyl("cart.umbrella", 1.35, 0.4, (cx, cy, 3.1), pl("#4fae5a", 0.55), n=16, r2=0.06)
    kit.cyl("cart.umbrellarim", 1.37, 0.05, (cx, cy, 2.92), pl("#3f9a4a", 0.6), n=16)
    # fountain: a stone basin, water lower than the rim, a tiered stone centre and a bowl
    fs = pl("#b9b19c", 0.8, spec=0.05)
    kit.cyl("fountain.floor", G.R_OUT, G.FLOOR_Z, (FX, FY, G.FLOOR_Z / 2), fs, n=48)
    wat = pl("#7ad0f0", 0.25, spec=0.35)
    kit.cyl("fountain.water", G.R_IN, 0.06, (FX, FY, G.WATER_Z - 0.03), wat, n=48)
    n = 36
    rmid = (G.R_OUT + G.R_IN) / 2
    for i in range(n):
        a = 2 * math.pi * i / n
        kit.box(f"fountain.rim{i}", (G.R_OUT - G.R_IN, 2 * math.pi * rmid / n + 0.04, G.RIM_Z),
                (FX + rmid * math.cos(a), FY + rmid * math.sin(a), G.RIM_Z / 2), fs, rot=(0, 0, a))
    kit.cyl("fountain.base", 0.75, 0.3, (FX, FY, G.FLOOR_Z + 0.15), fs, n=24)
    kit.cyl("fountain.pedestal", G.COL_R, 2.0, (FX, FY, G.FLOOR_Z + 1.3), fs, n=24, r2=0.4)
    kit.cyl("fountain.tier", 0.62, 0.14, (FX, FY, G.FLOOR_Z + 2.35), fs, n=24)
    kit.cyl("fountain.bowl", 0.85, 0.16, (FX, FY, G.FLOOR_Z + 2.5), fs, n=24, r2=0.6)
    kit.cyl("fountain.jet", 0.07, 1.5, (FX, FY, G.FLOOR_Z + 3.35), wat, n=10, r2=0.04)


DROP_ARCS = 22
DROP_PER = 9
REACH = 1.8
PEAK = 4.15
SPEED = 0.55


def drop_pos(a, k, g):
    """Droplet k of arc a at motion clock g: out along a parabola from the jet top to the water."""
    u = (k / DROP_PER + 0.37 * (a % 3) / DROP_PER + g * SPEED) % 1.0
    r = 0.06 + REACH * u
    z = PEAK - 3.8 * u * u
    az = 2 * math.pi * a / DROP_ARCS + 0.05 * (a % 2)
    return FX + r * math.cos(az), FY + r * math.sin(az), z


def clock(tl, t):
    """The droplet clock g(t): runs at 1 until the freeze, eases to a stop over 0.45 s, holds, eases back up at the thaw."""
    fz = [c for c in tl["cues"] if c["name"] == "freeze"]
    t1 = next((c["t"] for c in fz if c.get("f", 0) > 0.5), 1e9)
    t2 = next((c["t"] for c in fz if c["t"] > t1 and c.get("f", 1) < 0.5), 1e9)
    d = 0.45
    def run(a, b):   # integral of speed over [a, b] with the ramps
        return max(0.0, b - a)
    g = 0.0
    # before the freeze
    if t <= t1 - d:
        return t
    g = t1 - d
    if t <= t1:
        u = (t - (t1 - d)) / d
        return g + d * (u - u * u / 2)
    g += d / 2
    if t <= t2:
        return g
    if t <= t2 + d:
        u = (t - t2) / d
        return g + d * (u * u / 2)
    return g + d / 2 + (t - t2 - d)


def build_drops(kit, tl):
    pl = kit.plastic
    m = pl("#a8e2f8", 0.3, spec=0.3)
    W["drops"] = []
    fz = [c for c in tl["cues"] if c["name"] == "freeze"]
    tf = next((c["t"] for c in fz if c.get("f", 0) > 0.5), 1e9)
    gf = clock(tl, tf + 0.5) if tf < 1e8 else 0.0
    keep_out = [G.LEO_OUT, G.LEO_HIDE, (0.6, 7.0)] + [(sx * 0.8, yy) for sx in (-1, 1) for yy in (6.4, 6.7, 7.0, 7.3)]
    for a in range(DROP_ARCS):
        for k in range(DROP_PER):
            x, y, z = drop_pos(a, k, gf)
            if any(math.hypot(x - px, y - py) < 0.62 and z < 2.4 for px, py in keep_out):
                continue
            ob = kit.sphere(f"drop.{a}.{k}", 0.042, (x, y, z), m, seg=8)
            noshadow(ob)
            W["drops"].append((ob, a, k))


def build_pretzel(kit):
    pl = kit.plastic
    px, py = G.PRETZEL
    kit.box("napkin", (0.42, 0.34, 0.012), (px, py, G.RIM_Z + 0.006), pl("#fbfbf6", 0.9))
    brown = pl("#b8742f", 0.55, spec=0.2)
    root = kit.empty("pretzel", (px, py, G.RIM_Z + 0.14), rot=(math.radians(-48), 0, 0))
    W["pretzel"] = root
    W["bitepieces"] = []
    n = 16
    R = 0.15
    for i in range(n):
        a = 2 * math.pi * i / n
        ob = kit.box(f"pretzel.seg{i}", (0.1, 0.075, 0.085), (R * math.cos(a), 0, R * math.sin(a)), brown, root,
                     rot=(0, -a + math.pi / 2, 0), bevel=0.02)
        if i in (2, 3, 4):
            W["bitepieces"].append(ob)
    for s in (-1, 1):   # the twist: two crossing straps
        ob = kit.box(f"pretzel.strap{s}", (0.3, 0.075, 0.075), (0, 0, -0.05), brown, root, rot=(0, s * math.radians(38), 0), bevel=0.02)
    rnd = random.Random(148)
    salt = pl("#fffdf4", 0.5)
    for i in range(22):
        a = rnd.uniform(0, 2 * math.pi)
        r = R + rnd.uniform(-0.02, 0.02)
        ob = kit.box(f"pretzel.salt{i}", (0.02, 0.02, 0.02), (r * math.cos(a), -0.047, r * math.sin(a)), salt, root, rot=(0, rnd.uniform(0, 3), 0))
        if 2.2 < a / (2 * math.pi) * n < 5.2 and False:
            pass
        W["bitepieces"].append(ob) if (2 * math.pi * 1.6 / n < a < 2 * math.pi * 5.0 / n) else None
    W["pretzel_all"] = [o for o in bpy.data.objects if o.name.startswith("pretzel.") or o.name == "napkin"]
    # the tally: two short pale-blue strokes scratched into the rim, 1.5 cm proud
    blue = pl("#9fd8ff", 0.6)
    for k in range(2):
        kit.box(f"tally{k}", (0.025, 0.16, 0.015), (px - 0.33 + 0.07 * k, py, G.RIM_Z + 0.0075), blue)


def build_notes(kit):
    pl = kit.plastic
    cream = pl("#f2e6c8", 0.7)
    fold = pl("#c9b896", 0.7)
    W["notes"] = {}
    for who in ("me", "leo"):
        root = kit.empty(f"note.{who}", (0, 0, -50))
        kit.box(f"note.{who}.card", (0.34, 0.02, 0.24), (0, 0, 0), cream, root, bevel=0.004)
        kit.box(f"note.{who}.fold", (0.014, 0.024, 0.24), (0, 0, 0), fold, root)
        W["notes"][who] = root


def build_pigeon(kit, name, loc, scale=1.0):
    pl = kit.plastic
    gray = pl("#8d93a0", 0.7)
    dk = pl("#5d6370", 0.7)
    root = kit.empty(name, loc)
    kit.box(f"{name}.body", (0.18 * scale, 0.34 * scale, 0.16 * scale), (0, 0, 0), gray, root, bevel=0.04)
    kit.sphere(f"{name}.head", 0.075 * scale, (0, -0.2 * scale, 0.07 * scale), dk, root, seg=8)
    kit.box(f"{name}.beak", (0.025, 0.06 * scale, 0.025), (0, -0.28 * scale, 0.06 * scale), pl("#e8a030", 0.6), root)
    kit.box(f"{name}.tail", (0.14 * scale, 0.14 * scale, 0.025), (0, 0.24 * scale, 0.0), dk, root)
    for s_ in (-1, 1):
        kit.box(f"{name}.wing{s_}", (0.34 * scale, 0.26 * scale, 0.025), (s_ * 0.2 * scale, 0.02, 0.1 * scale), pl("#b8bdc8", 0.7), root,
                rot=(0, s_ * math.radians(-52), 0), bevel=0.01)
    return root


def build_car(kit):
    pl = kit.plastic
    cx, cy = G.CAR
    body = pl("#4a7fb8", 0.4, spec=0.5)
    dark = pl("#2a2a2e", 0.7)
    root = kit.empty("car", (cx, cy, 0))
    kit.box("car.body", (1.8, 4.2, 0.62), (0, 0, 0.62), body, root, bevel=0.06)
    kit.box("car.cabin", (1.62, 1.7, 0.58), (0, 0.75, 1.2), body, root, bevel=0.07)
    gl = pl("#9ed4f0", 0.12, spec=0.9)
    kit.box("car.wind", (1.5, 0.05, 0.4), (0, 1.62, 1.22), gl, root)
    for sx in (-1, 1):
        kit.box(f"car.sidewin{sx}", (0.05, 1.3, 0.38), (sx * 0.82, 0.75, 1.22), gl, root)
        for yy in (-1.3, 1.3):
            kit.cyl(f"car.wheel{sx}{yy}", 0.34, 0.24, (sx * 0.9, yy, 0.34), dark, root, rot=(0, math.pi / 2, 0), n=14)
    kit.box("car.deck", (1.7, 1.4, 0.04), (0, -1.1, 0.95), pl("#3a6a9c", 0.5), root)
    card = pl("#c8a068", 0.8)
    for i, (x, y, z, sx_, sy_, sz_) in enumerate([(-0.45, -1.5, 1.27, 0.7, 0.7, 0.6), (0.4, -1.45, 1.22, 0.75, 0.65, 0.5),
                                                   (-0.1, -0.85, 1.2, 0.6, 0.55, 0.45), (0.0, -1.5, 1.8, 0.6, 0.6, 0.5)]):
        kit.box(f"car.box{i}", (sx_, sy_, sz_), (x, y, z), card, root, bevel=0.02)
        kit.box(f"car.tape{i}", (0.06, sy_ + 0.01, sz_ + 0.01), (x, y, z), pl("#e8dcc0", 0.7), root)


def build_kitchen(kit):
    pl = kit.plastic
    kx, ky = G.KITCHEN
    kit.box("kitchen.floor", (9, 7, 0.08), (kx, ky + 0.5, 0.0), pl("#e0c89a", 0.6, spec=0.15))
    kit.box("kitchen.wall", (9, 0.3, 3.4), (kx, ky + 4.0, 1.7), pl("#f6e2a8", 0.85, spec=0.05))
    kit.box("kitchen.wallw", (0.3, 7, 3.4), (kx - 4.5, ky + 0.5, 1.7), pl("#f0d890", 0.85, spec=0.05))
    kit.box("kitchen.walle", (0.3, 7, 3.4), (kx + 4.5, ky + 0.5, 1.7), pl("#f0d890", 0.85, spec=0.05))
    kit.box("kitchen.ceil", (9, 7.4, 0.2), (kx, ky + 0.5, 3.5), pl("#fbf2d0", 0.9))
    kit.box("kitchen.windowframe", (2.0, 0.08, 1.5), (kx + 1.6, ky + 3.82, 1.9), pl("#fff7e6", 0.6))
    kit.box("kitchen.window", (1.7, 0.1, 1.2), (kx + 1.6, ky + 3.8, 1.9), pl("#8fd0ff", 0.3, spec=0.5))
    for sx in (-1, 1):
        kit.box(f"kitchen.cab{sx}", (2.4, 0.7, 0.95), (kx + sx * 2.9, ky + 3.55, 0.5), pl("#e8803a", 0.6))
        kit.box(f"kitchen.counter{sx}", (2.5, 0.75, 0.06), (kx + sx * 2.9, ky + 3.55, 1.0), pl("#f4f4f2", 0.5))
    kit.box("kitchen.table", (1.9, 0.95, 0.06), (kx - 2.4, ky + 1.6, 0.76), pl("#d9a45b", 0.5))
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"kitchen.tleg{sx}{sy}", (0.06, 0.06, 0.7), (kx - 2.4 + sx * 0.88, ky + 1.6 + sy * 0.42, 0.38), pl("#8a5a34", 0.7))
    kit.cyl("kitchen.mug", 0.055, 0.1, (kx - 2.7, ky + 1.55, 0.84), pl("#4a8ad9", 0.5), n=12)
    # the cake an inch from the floor: a plate, a frosted cake with dots, held in the air
    cakex, cakey, cz = kx + 0.55, ky + 0.35, 0.115
    kit.cyl("cake.plate", 0.3, 0.015, (cakex, cakey, cz), pl("#f4f4f2", 0.4), n=20)
    kit.cyl("cake.base", 0.22, 0.12, (cakex, cakey, cz + 0.07), pl("#f2a0b8", 0.6), n=20)
    kit.cyl("cake.top", 0.21, 0.09, (cakex, cakey, cz + 0.175), pl("#fff1d8", 0.6), n=20)
    for k in range(8):
        a = k * math.pi / 4
        kit.sphere(f"cake.dot{k}", 0.028, (cakex + 0.17 * math.cos(a), cakey + 0.17 * math.sin(a), cz + 0.225), pl("#f2a0b8", 0.5), seg=8)


def build_front(kit):
    pl = kit.plastic
    fx, fy = G.FRONT
    kit.plane("front.lawn", (60, 40), (fx, fy + 4, -0.02), pl("#5cc45a", 0.9, spec=0.05))
    kit.box("front.path", (1.8, 9.0, 0.05), (fx, fy - 1.5, 0.0), pl("#e2dccf", 0.85))
    kit.prop("sub_building_type_a", (fx - 14.0, fy + 6.0, 0), rot=90, height=5.5)
    for sx in (-1, 1):
        kit.prop("sub_fence", (fx + sx * 3.2, fy + 3.2, 0), height=1.0, tint="#f0ece4")
        kit.prop("sub_fence", (fx + sx * 5.2, fy + 3.2, 0), height=1.0, tint="#f0ece4")
    kit.prop("sub_tree_large", (fx - 7, fy + 6, 0), height=6.0, tint="#d4f0c4")
    kit.prop("sub_tree_large", (fx + 8, fy + 7, 0), height=6.5, tint="#d4f0c4")
    kit.prop("commontree_1", (fx + 3.5, fy + 14, 0), height=8.0, tint="#d4f0c4")
    kit.prop("bush_1", (fx - 2.5, fy + 3.0, 0), height=1.0, tint="#d4f0c4")
    kit.prop("bush_2", (fx + 2.5, fy + 3.0, 0), height=1.0, tint="#d4f0c4")


# ------------------------------------------------------------------------------------------------ the rule meter
DIGIT_SEGS = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd", 6: "afgedc", 7: "abc",
              8: "abcdefg", 9: "abcdfg"}


def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    edge = kit.emit("#2b2118", 0.6, "tagedge")
    plate = kit.emit("#f2e6c8", 0.85, "tagplate")
    ink = kit.emit("#2b2118", 0.6, "tagink")
    teal = kit.emit("#14867a", 0.9, "tagteal")

    def b(name, size, loc, mat, parent=None):
        ob = kit.box(name, size, loc, mat, parent or root)
        noshadow(ob)
        return ob

    b("tag.edge", (1.5, 0.7, 0.006), (0, 0, 0), edge)
    b("tag.plate", (1.44, 0.64, 0.006), (0, 0, 0.007), plate)
    z = 0.016
    # the pause glyph: two teal bars in a teal ring-less square
    for sx in (-1, 1):
        b(f"tag.pause{sx}", (0.1, 0.4, 0.006), (-0.52 + sx * 0.085, 0.0, z), teal)

    def seven(prefix, cx, cy, dw, dh, t):
        pos = {"a": (0, dh / 2 - t / 2, dw, t), "g": (0, 0, dw, t), "d": (0, -dh / 2 + t / 2, dw, t),
               "f": (-dw / 2 + t / 2, dh / 4, t, dh / 2), "b": (dw / 2 - t / 2, dh / 4, t, dh / 2),
               "e": (-dw / 2 + t / 2, -dh / 4, t, dh / 2), "c": (dw / 2 - t / 2, -dh / 4, t, dh / 2)}
        return {k: b(f"{prefix}{k}", (sw, sh, 0.006), (cx + px, cy + py, z), ink) for k, (px, py, sw, sh) in pos.items()}

    W["digits"] = [seven(f"tag.d{i}", cx, 0.0, 0.11, 0.38, 0.04) for i, cx in enumerate((-0.2, -0.04, 0.2, 0.36))]
    W["colon"] = [b("tag.c1", (0.04, 0.04, 0.006), (0.08, 0.07, z), ink), b("tag.c2", (0.04, 0.04, 0.006), (0.08, -0.07, z), ink)]


# ------------------------------------------------------------------------------------------------ build / animate
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    sun = kit.light("sun", "SUN", (18, -27, 51), 1.0, "#fff1d6", size=0.06)
    sun.data.angle = 0.05
    kit.aim(sun, (0, 0, 0))
    fill = kit.light("fill", "SUN", (0, -10, 30), 1.0, "#e8f0ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    build_park(kit)
    build_drops(kit, tl)
    build_pretzel(kit)
    build_notes(kit)
    build_car(kit)
    build_kitchen(kit)
    build_front(kit)
    build_tag(kit)
    # the pigeons and the leaves held in the air (shown only while the world is stopped, or in the neighbour's shot)
    W["pigeon"] = build_pigeon(kit, "pigeon", (-3.4, 6.2, 2.5), 2.0)
    W["pigeon"].rotation_euler = (math.radians(10), 0, math.radians(-25))
    W["pigeon2"] = build_pigeon(kit, "pigeon2", (G.FRONT[0] - 0.1, G.FRONT[1] + 0.2, 1.9), 1.3)
    rnd = random.Random(7)
    W["leaves"] = []
    lm = [kit.plastic(c, 0.8) for c in ("#e8c040", "#7ac04a", "#d98a30")]
    for i in range(14):
        ob = kit.box(f"leaf{i}", (0.1, 0.07, 0.012), (rnd.uniform(-5, 5), rnd.uniform(5.5, 10.5), rnd.uniform(1.8, 4.0)), lm[i % 3],
                     rot=(rnd.uniform(0, 3), rnd.uniform(0, 3), rnd.uniform(0, 3)))
        noshadow(ob)
        W["leaves"].append(ob)
    # a soft constant fill for faces in the montage rooms
    uf = kit.light("kfill", "AREA", (G.KITCHEN[0], G.KITCHEN[1] - 3.0, 2.8), 160, "#fff4e4", size=2.0, shadow=False)
    kit.aim(uf, (G.KITCHEN[0], G.KITCHEN[1] + 1.0, 1.0))
    return {}


def _first_frame(kit, story):
    W["inited"] = True


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    gains = {"sun": 4.2, "fill": 1.2, "kfill": 1.0}
    cur = next((x for x in tl["shots"] if x["start"] <= t < x["end"]), tl["shots"][-1])
    # the droplets: moving, then held
    g = clock(tl, t)
    for ob, a, k in W["drops"]:
        ob.location = drop_pos(a, k, g)
    fr = sample("freeze", tl, t, {"f": 0.0})["f"] > 0.5
    # objects that exist only in the stopped world
    for ob in W["leaves"]:
        ob.hide_render = not fr
    W["pigeon"].hide_render = not (fr and cur["id"] in ("S18b",))
    # the pretzel's bite
    bite = sample("bite", tl, t, {"b": 0.0})["b"] > 0.5
    pz = sample("pretz", tl, t, {"p": 0.0})["p"] > 0.5
    for ob in W["pretzel_all"]:
        ob.hide_render = not pz
    for ob in W["bitepieces"]:
        if bite:
            ob.hide_render = True
    # the tag: a pause glyph and the count, then the countdown
    tm = sample("tag", tl, t, {"mode": 0.0, "s": 1461.0})
    secs = int(round(tm["s"]))
    mm, ss_ = secs // 60, secs % 60
    cd = tm["mode"] > 0.5
    digs = (mm // 10, mm % 10, ss_ // 10, ss_ % 10) if cd else (1, 4, 6, 1)
    for d, n in zip(W["digits"], digs):
        for k, ob in d.items():
            ob.hide_render = k not in DIGIT_SEGS[n]
    for ob in W["colon"]:
        ob.hide_render = not cd
    shot = cur
    spec = next((s for s in story["shots"] if s["id"] == shot["id"]), None)
    lens = 40.0
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
    s = 0.46 * w2
    tag = W["tag"]
    tag.scale = (s, s, s)
    tag.location = (-0.5 * w2, 0.62 * h2, -dist)
    # sitting: me and Leo on the rim (legs forward)
    for who in ("me", "leo"):
        sv = sample(f"sit_{who}", tl, t, {"s": 0.0})["s"]
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg and sv > 0.001:
                leg.rotation_euler = (leg.rotation_euler.x * (1 - sv) + SIT * sv, 0, 0)
    for who in ("uncle", "walker", "jogger"):
        pass
    # the notes follow the holder's head
    for who, off in (("me", (-0.5, -0.6, -0.45)), ("leo", (-0.5, -0.6, -0.45))):
        nm = sample(f"note_{who}", tl, t, {"m": 0.0})["m"]
        root = W["notes"][who]
        gh = bpy.data.objects.get(f"{who}.headg")
        if nm < 1.02 or gh is None:
            root.location = (0, 0, -50)
            continue
        hp = gh.matrix_world.translation
        u = min(1.0, max(0.0, 2.0 - nm))     # 0 on the palm, 1 in the pocket
        root.location = (hp.x + off[0] + 0.05 * u, hp.y + off[1] + 0.1 * u, hp.z + off[2] - 0.5 * u)
        root.rotation_euler = (math.radians(-12), 0, 0)
    return gains
