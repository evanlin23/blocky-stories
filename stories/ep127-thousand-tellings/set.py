"""ep127 "thousand tellings": a green tackle shop on a sunny river, a wood stove, two red armchairs facing each other,
one low amber lamp, a chalk slate by the till. The rule meter is a small cream tag on the camera (an open-book glyph
and Grandpa's count); the slate on the set shows the same number.

Light never changes inside a shot: day and night are separate cuts (the story's "look" cues are all set on a cut), and
the lamp, when it is on, is steady. Cues in story.json (read in animate): look, count, door, hook, rods, car, bag.
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


LOOKS = {
    "day": dict(sun=3.4, sun_col="#fff0d8", el=48.0, az=160.0, fill=0.9, fill_col="#fff0e0", sky="#8fd3ff", sky_str=1.0,
                lamp=0.0, shopday=1.0, night=0.0, moon=0.0),
    "night": dict(sun=0.9, sun_col="#9fb4ff", el=38.0, az=165.0, fill=0.8, fill_col="#eef0ff", sky="#1f2f5a", sky_str=0.6,
                  lamp=1.0, shopday=0.0, night=1.0, moon=1.0),
}


def look_at(tl, t):
    cur = LOOKS["day"]
    for c in tl["cues"]:
        if c["name"] == "look":
            if c["t"] > t:
                break
            cur = LOOKS[c["id"]]
    return {k: (kit_col(v) if isinstance(v, str) else v) for k, v in cur.items()}


def last_cue(tl, name, t):
    cur = None
    for c in tl["cues"]:
        if c["name"] == name:
            if c["t"] > t:
                break
            cur = c
    return cur


def sample_cue(tl, name, t, key, default, dur_default=0.0):
    """A numeric cue field eased over the cue's own dur."""
    cues = [c for c in tl["cues"] if c["name"] == name and key in c]
    cur = prev = default
    for c in cues:
        if c["t"] > t:
            break
        prev, cur = cur, c[key]
        dur = c.get("dur", dur_default)
        if dur > 0 and t < c["t"] + dur:
            return prev + (cur - prev) * ss((t - c["t"]) / dur)
    return cur


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


# ---------------------------------------------------------------------------------------------- seven-segment digits
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc",
       "8": "abcdefg", "9": "abcdfg"}
DW, DH, DT = 0.5, 1.0, 0.13


class Display:
    """Up to five characters of chalk (or tag) numerals under one parent: digits 0-9 and a comma."""

    def __init__(self, kit, name, parent, mat, plane, thick):
        self.plane = plane
        self.slots = []
        for i in range(5):
            e = kit.empty(f"{name}.s{i}", (0, 0, 0), parent)
            segs = {}
            geo = {"a": (0, DH / 2 - DT / 2, DW, DT), "g": (0, 0, DW, DT), "d": (0, -DH / 2 + DT / 2, DW, DT),
                   "f": (-DW / 2 + DT / 2, DH / 4, DT, DH / 2), "b": (DW / 2 - DT / 2, DH / 4, DT, DH / 2),
                   "e": (-DW / 2 + DT / 2, -DH / 4, DT, DH / 2), "c": (DW / 2 - DT / 2, -DH / 4, DT, DH / 2)}
            for k, (x, y, sx, sy) in geo.items():
                if plane == "xy":
                    ob = kit.box(f"{name}.s{i}{k}", (sx, sy, thick), (x, y, 0), mat, e)
                else:
                    ob = kit.box(f"{name}.s{i}{k}", (sx, thick, sy), (x, 0, y), mat, e)
                noshadow(ob)
                segs[k] = ob
            parts = []
            for k, (cw, ch_, cx_, cy_, ang) in enumerate([(0.17, 0.17, 0.0, -DH / 2 + 0.085, 0.0),
                                                           (0.09, 0.26, -0.035, -DH / 2 - 0.07, 0.45)]):
                if plane == "xy":
                    cb = kit.box(f"{name}.s{i}c{k}", (cw, ch_, thick), (cx_, cy_, 0), mat, e, rot=(0, 0, ang))
                else:
                    cb = kit.box(f"{name}.s{i}c{k}", (cw, thick, ch_), (cx_, 0, cy_), mat, e, rot=(0, -ang, 0))
                noshadow(cb)
                parts.append(cb)
            self.slots.append((e, segs, parts))

    def show(self, s, scale, cx, avail_w, hmax):
        nd = sum(1 for ch in s if ch.isdigit())
        nc = len(s) - nd
        H = min(hmax, avail_w / (0.66 * nd + 0.3 * nc)) * max(0.0, scale)
        total = (0.66 * nd + 0.3 * nc) * H
        x = cx - total / 2
        for i, (e, segs, comma) in enumerate(self.slots):
            ch = s[i] if i < len(s) and scale > 0.02 else None
            for k, ob in segs.items():
                ob.hide_render = not (ch is not None and ch.isdigit() and k in SEG[ch])
            for cb in comma:
                cb.hide_render = ch != ","
            if ch is None:
                continue
            pitch = (0.66 if ch.isdigit() else 0.3) * H
            e.location = (x + pitch / 2, 0, 0.02 if self.plane == "xy" else 0)
            e.scale = (H, H, H)
            x += pitch


def count_state(tl, t):
    cues = [c for c in tl["cues"] if c["name"] == "count"]
    cur, prev = ("997", 1.0), None
    s_cur, s_prev = "997", "997"
    for c in cues:
        if c["t"] > t:
            break
        s_prev, s_cur = s_cur, c["s"]
        dur = c.get("dur", 0.0)
        if dur > 0 and t < c["t"] + dur:
            u = (t - c["t"]) / dur
            return (s_prev, 1 - 2 * u) if u < 0.5 else (s_cur, 2 * u - 1)
    return s_cur, 1.0


# ---------------------------------------------------------------------------------------------- the shop
def armchair(kit, name, x, y, yaw, red, dark, wear=False):
    root = kit.empty(name, (x, y, 0), rot=(0, 0, yaw * D2R))
    kit.box(f"{name}.seat", (0.95, 0.9, 0.22), (0, 0, 0.35), red, root, bevel=0.05)
    kit.box(f"{name}.cush", (0.8, 0.74, 0.06), (0, -0.02, 0.48), dark, root, bevel=0.03)
    kit.box(f"{name}.back", (0.95, 0.2, 0.85), (0, 0.4, 0.72), red, root, bevel=0.06)
    kit.box(f"{name}.top", (0.8, 0.22, 0.14), (0, 0.4, 1.18), red, root, bevel=0.05)
    for sx in (-1, 1):
        kit.box(f"{name}.arm{sx}", (0.18, 0.9, 0.3), (sx * 0.5, 0, 0.62), red, root, bevel=0.05)
        for sy in (-1, 1):
            kit.box(f"{name}.leg{sx}{sy}", (0.1, 0.1, 0.2), (sx * 0.4, sy * 0.35, 0.1), dark, root)
    if wear:   # the worn patch on the right arm, 1 cm proud
        kit.box(f"{name}.wear", (0.14, 0.4, 0.012), (0.5, -0.05, 0.777), kit.plastic("#e8a090", 0.9, spec=0.02), root)
        kit.box(f"{name}.wear2", (0.1, 0.2, 0.012), (0.5, -0.12, 0.79), kit.plastic("#f0b8a8", 0.9, spec=0.02), root)
    return root


def front_wall(kit, outer, inner, trim):
    H = 3.4
    wx0, wx1 = G.WIN_X - 1.15, G.WIN_X + 1.15
    dx0, dx1 = G.DOOR_X - 0.55, G.DOOR_X + 0.55
    holes = sorted([(wx0, wx1, 0.95, 2.4), (dx0, dx1, 0.0, 2.2)])
    pieces, x = [], -6.3
    for a, b, z0, z1 in holes:
        pieces.append((x, a, 0.0, H))
        if z0 > 0:
            pieces.append((a, b, 0.0, z0))
        pieces.append((a, b, z1, H))
        x = b
    pieces.append((x, 6.3, 0.0, H))
    for i, (a, b, z0, z1) in enumerate(pieces):
        kit.box(f"fw.o{i}", (b - a, 0.2, z1 - z0), ((a + b) / 2, -6.05, (z0 + z1) / 2), outer)
        kit.box(f"fw.i{i}", (b - a, 0.2, z1 - z0), ((a + b) / 2, -5.85, (z0 + z1) / 2), inner)
    # trim round both openings (stands proud of both wall faces)
    for nm, a, b, z0, z1 in [("win", wx0, wx1, 0.95, 2.4), ("door", dx0, dx1, 0.0, 2.2)]:
        t = 0.09
        kit.box(f"{nm}.top", (b - a, 0.34, t), ((a + b) / 2, -5.95, z1 - t / 2), trim)
        kit.box(f"{nm}.l", (t, 0.34, z1 - z0), (a + t / 2, -5.95, (z0 + z1) / 2), trim)
        kit.box(f"{nm}.r", (t, 0.34, z1 - z0), (b - t / 2, -5.95, (z0 + z1) / 2), trim)
        if z0 > 0:
            kit.box(f"{nm}.sill", (b - a + 0.2, 0.5, 0.07), ((a + b) / 2, -6.0, z0 + 0.035), trim)


def build_shop(kit, P):
    plastic = kit.plastic
    pine = plastic("#e0b07a", 0.6, spec=0.1)
    pine2 = plastic("#f0c890", 0.55, spec=0.1)
    cream = plastic("#f6ecd8", 0.7, spec=0.05)
    red = plastic("#c8473a", 0.7, spec=0.05)
    dark_red = plastic("#9a342c", 0.7, spec=0.05)
    iron = kit.metal("#3a3d44", 0.5)
    trim = plastic("#fff6e6", 0.6, spec=0.1)
    green_out = kit.planks("#3f9f6a", "#37905e", 1.0, "X")
    wallin = plastic("#f1dfb8", 0.8, spec=0.05)
    floor = kit.planks("#c9976a", "#b78456", 1.0)
    # floor, walls
    kit.plane("shop.floor", (12.6, 8.0), (0, -2.1, 0.02), floor)
    front_wall(kit, green_out, wallin, trim)
    kit.box("wall.left", (0.3, 8.0, 3.4), (-6.15, -2.1, 1.7), wallin)
    kit.box("wall.right", (0.3, 8.0, 3.4), (6.15, -2.1, 1.7), wallin)
    kit.box("wall.back", (12.6, 0.3, 3.4), (0, 1.95, 1.7), wallin)
    # stove and pipe
    kit.box("stove", (0.9, 0.75, 1.0), (-2.7, -2.3, 0.5), iron, bevel=0.04)
    kit.box("stove.top", (0.96, 0.8, 0.06), (-2.7, -2.3, 1.03), iron)
    kit.cyl("stove.pipe", 0.09, 2.6, (-2.7, -2.1, 2.3), iron, n=14)
    kit.box("stove.door", (0.4, 0.04, 0.4), (-2.7, -2.7, 0.55), plastic("#22252a", 0.5))
    # chairs
    armchair(kit, "gchair", G.GCH[0], G.GCH[1], 0, red, dark_red)
    armchair(kit, "mchair", G.MCH[0], G.MCH[1], 180, red, dark_red, wear=True)
    # the lamp on a small table
    lx, ly = G.LAMP
    kit.cyl("ltable.top", 0.34, 0.05, (lx, ly, 0.62), pine, n=24)
    kit.cyl("ltable.leg", 0.05, 0.6, (lx, ly, 0.3), pine, n=10)
    kit.cyl("ltable.foot", 0.2, 0.04, (lx, ly, 0.02), pine, n=18)
    kit.cyl("lamp.base", 0.1, 0.2, (lx, ly, 0.75), plastic("#c8873a", 0.5, spec=0.3), n=14)
    kit.cyl("lamp.shade", 0.2, 0.26, (lx, ly, 0.98), kit.emit("#ffb347", 1.6, "lampshade"), n=20, r2=0.12)
    # the slate by the till
    sx, sy, sz = G.SLATE
    wood = plastic("#a8744a", 0.7, spec=0.1)
    board = plastic("#3a4148", 0.9, spec=0.02)
    kit.box("slate.board", (0.78, 0.04, 0.6), (sx, sy + 0.14, sz), board)          # y 1.74..1.78
    for nm, bx, bz, w_, h_ in [("t", 0, 0.33, 0.9, 0.07), ("b", 0, -0.33, 0.9, 0.07),
                               ("l", -0.42, 0, 0.07, 0.6), ("r", 0.42, 0, 0.07, 0.6)]:
        kit.box(f"slate.f{nm}", (w_, 0.07, h_), (sx + bx, sy + 0.135, sz + bz), wood)
    W["slate_parent"] = kit.empty("slate.disp", (sx, sy + 0.115, sz))
    chalk = plastic("#f2f2ea", 0.95, spec=0.0)
    W["slate"] = Display(kit, "chalk", W["slate_parent"], chalk, "xz", 0.04)
    # the counter, till, lure wall, tank
    kit.box("counter", (3.9, 0.9, 1.1), (3.8, G.CNT_Y, 0.55), pine, bevel=0.02)
    kit.box("counter.top", (4.1, 1.1, 0.08), (3.8, G.CNT_Y, 1.14), pine2, bevel=0.02)
    kit.box("till", (0.5, 0.4, 0.28), (2.35, 0.7, 1.32), cream, bevel=0.04)
    kit.box("till.key", (0.4, 0.3, 0.05), (2.35, 0.62, 1.48), plastic("#4a4d52", 0.5), bevel=0.02)
    kit.box("tank", (0.9, 0.5, 0.45), (4.4, 0.0, 0.225), plastic("#2f8f8a", 0.3, spec=0.5), bevel=0.02)
    brass = plastic("#e3b04b", 0.35, spec=0.6)
    kit.box("tank.lid", (0.94, 0.54, 0.05), (4.4, 0.0, 0.475), brass)
    kit.box("tank.rim", (0.94, 0.04, 0.12), (4.4, -0.27, 0.46), brass)            # front plate of the lid
    for k in range(2):                                                          # the two river-blue strokes, 1 cm proud
        kit.box(f"tank.stroke{k}", (0.025, 0.012, 0.08), (4.05 + 0.07 * k, -0.296, 0.46), plastic("#3f8fd8", 0.5, spec=0.1))
    kit.box("peg", (3.9, 0.05, 1.9), (3.8, 1.76, 2.4), plastic("#bfe3d8", 0.8, spec=0.05))
    cols = ["#ff5fa0", "#ffd23f", "#3fd0ff", "#ff8a3a", "#7be06a"]
    for r in range(5):
        for c in range(13):
            x = 2.0 + c * 0.285
            z = 1.62 + r * 0.34
            m = plastic(cols[(r * 3 + c) % 5], 0.45, spec=0.3)
            kit.box(f"lure{r}_{c}", (0.14, 0.04, 0.08), (x, 1.72, z), m, bevel=0.015)
            kit.box(f"lure{r}_{c}t", (0.06, 0.03, 0.1), (x + 0.1, 1.72, z), m, rot=(0, 0.5, 0))
    # fishing rods: leaning in the corner until L66, then by the door (cue "rods")
    rods = kit.empty("rods", (-5.6, 1.4, 0))
    for i in range(2):
        kit.cyl(f"rod{i}", 0.035, 2.3, (0.14 * i, 0.05 * i, 1.15), plastic("#a8703a", 0.5), rods, n=8)
        kit.cyl(f"reel{i}", 0.07, 0.07, (0.14 * i, -0.06, 1.0), plastic("#e8503a", 0.4, spec=0.4), rods,
                rot=(math.pi / 2, 0, 0), n=12)
    W["rods"] = rods
    # the screen door (a leaf hinged on its right jamb), the hook and its eye
    jx = G.DOOR_X + 0.52
    hinge = kit.empty("sdoor", (jx, -6.0, 0))
    leafm = plastic("#d9e8c8", 0.6, spec=0.1)
    kit.box("sdoor.stileL", (0.1, 0.05, 2.1), (-1.0, 0, 1.05), leafm, hinge)
    kit.box("sdoor.stileR", (0.1, 0.05, 2.1), (-0.05, 0, 1.05), leafm, hinge)
    kit.box("sdoor.top", (1.04, 0.05, 0.1), (-0.52, 0, 2.05), leafm, hinge)
    kit.box("sdoor.mid", (1.04, 0.05, 0.12), (-0.52, 0, 0.85), leafm, hinge)
    kit.box("sdoor.kick", (1.04, 0.05, 0.4), (-0.52, 0, 0.2), leafm, hinge)
    W["door"] = hinge
    hx, hz = G.DOOR_X - 1.0, 1.6
    brass_ = plastic("#c9a24a", 0.4, spec=0.6)
    kit.box("hook.plate", (0.16, 0.02, 0.16), (hx - 0.02, -5.735, hz), brass_)
    kit.box("hook.block", (0.1, 0.05, 0.1), (hx, -5.71, hz), iron)
    kit.box("eye.plate", (0.14, 0.02, 0.14), (hx + 0.34, -5.735, hz - 0.02), brass_)
    kit.box("eye.stud", (0.04, 0.05, 0.04), (hx + 0.34, -5.71, hz - 0.02), iron)
    kit.cyl("eye.ring", 0.05, 0.03, (hx + 0.34, -5.69, hz - 0.02), iron, rot=(math.pi / 2, 0, 0), n=14)
    hk = kit.empty("hook", (hx, -5.685, hz))
    kit.box("hook.bar", (0.36, 0.035, 0.04), (0.18, 0, 0), iron, hk)
    kit.box("hook.tip", (0.04, 0.035, 0.09), (0.34, 0, -0.04), iron, hk)
    W["hook"] = hk
    # the tackle box that props the door open
    W["tbox"] = kit.box("tbox", (0.45, 0.28, 0.24), (G.DOOR_X - 0.1, -7.1, 0.12), plastic("#ff8a3a", 0.5, spec=0.2), bevel=0.03)
    # outside: lot, river, far bank
    kit.plane("lot", (16, 11), (3.5, -11.7, 0.015), plastic("#d3c6a6", 0.95, spec=0.02))
    kit.plane("river", (500, 120), (0, -75, 0.03), plastic("#3f8fd8", 0.25, spec=0.6))
    W["streak"] = kit.plane("moonstreak", (7, 90), (-22, -85, 0.05), plastic("#cfe0ff", 0.3, spec=0.5))
    W["moon"] = kit.sphere("moon", 7.0, (-45, -300, 90), kit.emit("#e8f0ff", 1.3, "moon"), seg=16)
    noshadow(W["moon"])
    for k, x in enumerate(range(-90, 100, 22)):
        tree(kit, f"ftree{k}", x + (k % 3) * 5, -140 - (k % 2) * 6, 0, 9.0)
    for k, x in enumerate([-14, -9, 12, 17]):
        tree(kit, f"stree{k}", x, -9 + (k % 2) * 3, 0, 6.5)
    # lights
    kit.light("lamp", "POINT", (lx - 0.05, ly + 0.02, 0.86), 70.0, "#ffd09a", size=0.15)
    kit.light("shopday", "POINT", (0.0, -2.0, 3.0), 380.0, "#fff0d8", size=0.8, shadow=False)
    kit.light("shopnight", "POINT", (-0.4, -2.2, 2.6), 150.0, "#fff4e6", size=0.8, shadow=False)
    kit.light("doornight", "POINT", (G.DOOR_X, -4.6, 2.0), 220.0, "#fff4e6", size=0.8, shadow=False)
    kit.light("outnight", "POINT", (G.DOOR_X, -9.6, 3.2), 170.0, "#f4f6ff", size=1.0, shadow=False)
    kit.light("cntnight", "POINT", (3.8, -1.2, 2.4), 110.0, "#fff4e6", size=0.8, shadow=False)


def tree(kit, name, x, y, z, h=6.0, tint="#cfe8c0"):
    try:
        kit.prop("commontree_1", (x, y, z), height=h, tint=tint)
    except Exception:
        kit.cyl(f"{name}.trunk", 0.3, h * 0.45, (x, y, z + h * 0.22), kit.plastic("#7a5230", 0.8), n=8)
        kit.sphere(f"{name}.crown", h * 0.28, (x, y, z + h * 0.68), kit.plastic("#5fae4a", 0.8), seg=10)


# ---------------------------------------------------------------------------------------------- the car
def build_car(kit):
    plastic = kit.plastic
    blue = plastic("#2f6fd0", 0.35, spec=0.5)
    blue2 = plastic("#5a96e8", 0.4, spec=0.4)
    dark = plastic("#2a2d33", 0.6)
    car = kit.empty("car", (150, 0, 0))
    kit.box("car.body", (1.9, 4.1, 0.5), (0, 0, 0.62), blue, car, bevel=0.06)
    kit.box("car.hood", (1.86, 1.3, 0.2), (0, -1.4, 0.95), blue, car, bevel=0.05)
    kit.box("car.trunk", (1.86, 0.9, 0.2), (0, 1.6, 0.95), blue, car, bevel=0.05)
    kit.box("car.dash", (1.8, 0.5, 0.55), (0, -0.82, 1.1), blue2, car, bevel=0.05)
    kit.box("car.floor", (1.8, 2.3, 0.1), (0, 0.4, 0.6), dark, car)
    for sx in (-1, 1):
        kit.box(f"car.apil{sx}", (0.09, 0.09, 1.1), (sx * 0.94, -0.95, 1.5), blue, car, rot=(0.0, 0, 0))
        kit.box(f"car.cpil{sx}", (0.09, 0.09, 1.1), (sx * 0.94, 1.45, 1.5), blue, car)
        kit.box(f"car.bpil{sx}", (0.09, 0.09, 1.1), (sx * 0.94, 0.3, 1.5), blue, car)
        for sy in (-1, 1):
            kit.cyl(f"car.wheel{sx}{sy}", 0.38, 0.24, (sx * 0.96, sy * 1.35, 0.38), dark, car, rot=(0, math.pi / 2, 0), n=16)
        kit.box(f"car.head{sx}", (0.36, 0.06, 0.2), (sx * 0.6, -2.08, 0.82), plastic("#fff3b0", 0.4), car)
    kit.box("car.roof", (2.0, 2.7, 0.1), (0, 0.25, 2.07), blue2, car, bevel=0.04)
    kit.box("car.seat", (0.9, 0.8, 0.14), (G.CAR_DX, 0.18, 0.55), plastic("#d9d2c0", 0.8), car, bevel=0.03)
    kit.box("car.seatb", (0.9, 0.14, 0.9), (G.CAR_DX, 0.62, 1.0), plastic("#d9d2c0", 0.8), car, bevel=0.03)
    kit.box("car.seat2", (0.9, 0.8, 0.14), (-G.CAR_DX, 0.18, 0.55), plastic("#d9d2c0", 0.8), car, bevel=0.03)
    kit.box("car.seatb2", (0.9, 0.14, 0.9), (-G.CAR_DX, 0.62, 1.0), plastic("#d9d2c0", 0.8), car, bevel=0.03)
    kit.box("car.back", (1.8, 0.7, 0.14), (0, 1.1, 0.55), plastic("#d9d2c0", 0.8), car, bevel=0.03)
    W["bag"] = kit.box("car.bag", (0.7, 0.4, 0.42), (-0.2, 1.1, 0.83), plastic("#d9473a", 0.7, spec=0.05), car, bevel=0.07)
    W["car"] = car


# ---------------------------------------------------------------------------------------------- remote stages
def build_stages(kit):
    plastic = kit.plastic
    lawn = plastic("#9cc98a", 0.9, spec=0.02)
    kit.plane("ground", (2600, 2600), (300, 0, 0), lawn)
    # --- the ceiling (S14)
    cx, cy = G.CEIL
    kit.plane("ceil.floor", (10, 8), (cx, cy, 0.02), kit.planks("#c9976a", "#b78456", 1.0))
    kit.box("ceil.back", (10, 0.3, 3.2), (cx, cy + 3.5, 1.6), plastic("#f1dfb8", 0.8, spec=0.05))
    kit.box("ceil.boards", (10, 7, 0.1), (cx, cy, 3.25), kit.planks("#d8a870", "#c8955f", 1.0, "X"))
    for k in range(-2, 3):
        kit.box(f"ceil.beam{k}", (0.18, 7, 0.16), (cx + k * 2.0, cy, 3.14), plastic("#9a6a3c", 0.7, spec=0.05))
    for k in range(2):
        kit.box(f"ceil.sun{k}", (0.55, 5.0, 0.01), (cx - 1.5 + k * 3.0, cy, 3.195), plastic("#fff2c0", 0.9, spec=0.0))
    kit.light("ceillight", "POINT", (cx, cy - 1.0, 2.3), 140.0, "#fff0d8", size=0.8, shadow=False)
    # --- the road (S13, S65), my car's river road
    rx, ry = G.ROAD
    kit.plane("road", (6.0, 220), (rx, ry, 0.02), plastic("#4a4f5a", 0.9, spec=0.05))
    for k in range(-20, 40):
        kit.box(f"road.dash{k}", (0.14, 1.4, 0.01), (rx, ry + k * 4.0, 0.035), plastic("#ffd23f", 0.6))
    kit.plane("road.river", (70, 220), (rx + 40, ry, 0.03), plastic("#3f8fd8", 0.25, spec=0.6))
    kit.plane("road.bank", (6, 220), (rx + 6, ry, 0.025), plastic("#d3c6a6", 0.95))
    for k in range(-5, 18):
        kit.box(f"road.post{k}", (0.14, 0.14, 0.7), (rx + 3.5, ry + k * 3.0, 0.35), plastic("#fff6e6", 0.7))
    for k in range(-5, 16):
        tree(kit, f"road.tree{k}", rx - 5.5 - (k % 3) * 1.5, ry + k * 3.7 - 6, 0, 6 + (k % 2))
    kit.light("roadlight", "POINT", (rx - 1.5, ry - 4.0, 3.5), 120.0, "#fff0d8", size=1.0, shadow=False)
    # --- the bridge (S44)
    bx, by = G.BRIDGE
    deck = kit.planks("#6b4a2e", "#4e3520", 1.0, "Y")
    kit.plane("bridge.river", (140, 240), (bx, by, 0.03), plastic("#3f8fd8", 0.25, spec=0.6))
    kit.box("bridge.deck", (7.0, 60, 0.16), (bx, by, 0.04), deck)
    green = plastic("#3f9f6a", 0.5, spec=0.15)
    for sx in (-1, 1):
        kit.box(f"bridge.rail{sx}", (0.14, 60, 0.14), (bx + sx * 3.4, by, 1.05), green)
        kit.box(f"bridge.rail2{sx}", (0.1, 60, 0.1), (bx + sx * 3.4, by, 0.55), green)
        for k in range(-14, 15):
            kit.box(f"bridge.post{sx}{k}", (0.16, 0.16, 1.1), (bx + sx * 3.4, by + k * 2.0, 0.6), green)
    for k in range(10):
        tree(kit, f"bridge.tree{k}", bx - 30 + k * 7, by + 60 + (k % 2) * 4, 0, 8)
    kit.light("bridgelight", "POINT", (bx - 1.5, by - 4.0, 3.5), 120.0, "#fff0d8", size=1.0, shadow=False)
    # --- the city kitchen (S12a) and the doorway (S64)
    kx, ky = G.KITCHEN
    kit.plane("k.floor", (16, 10), (kx, ky, 0.02), kit.checker("#f6ecd8", "#cfe6e0", 0.8) if hasattr(kit, "checker") else plastic("#f6ecd8"))
    kit.box("k.wall", (16, 0.3, 3.2), (kx, ky + 3.15, 1.6), plastic("#fbe8b0", 0.8, spec=0.05))
    kit.box("k.hall", (16, 0.3, 3.2), (kx, ky + 6.0, 1.6), plastic("#e8d8f0", 0.8, spec=0.05))
    trimw = plastic("#fff6e6", 0.6, spec=0.1)
    # the doorway in the back wall (x = kx - 1.4 .. kx - 0.2)
    kit.box("k.wallL", (6.6, 0.3, 3.2), (kx - 5.0 + 0.0, ky + 3.15, 1.6), plastic("#fbe8b0", 0.8, spec=0.05))
    kit.box("k.door.top", (1.3, 0.34, 0.1), (kx - 1.4, ky + 3.15, 2.25), trimw)
    kit.box("k.door.l", (0.1, 0.34, 2.2), (kx - 2.0, ky + 3.15, 1.1), trimw)
    kit.box("k.door.r", (0.1, 0.34, 2.2), (kx - 0.8, ky + 3.15, 1.1), trimw)
    kit.box("k.hook", (0.5, 0.05, 0.05), (kx - 3.0, ky + 6.0 - 0.2, 1.7), plastic("#3a3d44", 0.5))
    kit.box("k.cab", (6.5, 0.7, 0.9), (kx + 2.75, ky + 2.6, 0.45), plastic("#6fc3b5", 0.5, spec=0.2))
    kit.box("k.cabtop", (6.7, 0.8, 0.06), (kx + 2.75, ky + 2.6, 0.93), plastic("#f6ecd8", 0.5, spec=0.2))
    kit.box("k.upper", (6.0, 0.4, 0.9), (kx + 3.0, ky + 2.85, 2.3), plastic("#6fc3b5", 0.5, spec=0.2))
    px, py = kx + 1.6, ky + 2.55
    kit.box("phone", (0.078, 0.158, 0.012), (px, py, 0.966), plastic("#1c1c20", 0.4, spec=0.4), bevel=0.006)
    kit.box("phone.scr", (0.068, 0.138, 0.004), (px, py, 0.974), plastic("#9fd0f0", 0.3, spec=0.3))
    kit.cyl("phone.call", 0.023, 0.004, (px, py, 0.9775), plastic("#3ad06a", 0.4), n=16)
    kit.box("phone.h1", (0.03, 0.008, 0.004), (px, py - 0.006, 0.9805), plastic("#ffffff", 0.4))
    kit.box("phone.h2", (0.008, 0.03, 0.004), (px - 0.01, py, 0.9805), plastic("#ffffff", 0.4))
    # the keys on the counter by the door
    kk = plastic("#c0c4cc", 0.3, spec=0.6)
    kit.cyl("keys.ring", 0.07, 0.02, (kx - 0.12, ky + 2.4, 0.975), kk, n=16)
    for i in range(3):
        kit.box(f"keys.k{i}", (0.06, 0.2, 0.02), (kx - 0.12 + 0.08 * (i - 1), ky + 2.23, 0.975), plastic("#f0c040", 0.3, spec=0.6),
                rot=(0, 0, 0.35 * (i - 1)))
    kit.light("kitlight", "POINT", (kx - 0.5, ky - 1.5, 2.8), 260.0, "#fff0d8", size=0.8, shadow=False)
    # --- the porch (S03, S04)
    ox, oy = G.PORCH
    kit.box("p.deck", (9, 5, 0.3), (ox, oy, 0.15), kit.planks("#c9976a", "#b78456", 1.0))
    kit.box("p.wall", (9, 0.3, 3.4), (ox, oy + 2.65, 1.7), kit.planks("#f6d8b8", "#efcba8", 1.0, "X"))
    kit.box("p.door", (1.1, 0.12, 2.3), (ox - 2.6, oy + 2.45, 1.45), plastic("#3f8fd8", 0.5, spec=0.2))
    kit.box("p.win", (1.6, 0.12, 1.2), (ox + 2.6, oy + 2.45, 1.9), plastic("#9fd0f0", 0.3, spec=0.5))
    kit.box("p.winframe", (1.8, 0.08, 1.4), (ox + 2.6, oy + 2.48, 1.9), trimw)
    for k in range(7):
        kit.sphere(f"p.flower{k}", 0.12, (ox + 1.95 + k * 0.22, oy + 2.28, 1.1), plastic(["#ff5fa0", "#ffd23f"][k % 2], 0.6), seg=8)
    kit.box("p.flowerbox", (1.7, 0.25, 0.2), (ox + 2.6, oy + 2.35, 0.95), plastic("#8a5a3a", 0.8))
    kit.cyl("p.table", 0.62, 0.05, (ox - 0.2, oy - 0.3, 0.76), plastic("#fff4e0", 0.8), n=28)
    kit.cyl("p.tleg", 0.07, 0.74, (ox - 0.2, oy - 0.3, 0.37), plastic("#8a5a3a", 0.7), n=10)
    kit.cyl("p.cup1", 0.07, 0.09, (ox - 0.45, oy - 0.45, 0.83), plastic("#ff8a3a", 0.4, spec=0.3), n=14)
    kit.cyl("p.cup2", 0.07, 0.09, (ox + 0.1, oy - 0.5, 0.83), plastic("#3fd0ff", 0.4, spec=0.3), n=14)
    kit.sphere("p.pot", 0.14, (ox - 0.2, oy - 0.1, 0.91), plastic("#ff5fa0", 0.4, spec=0.3), seg=12)
    kit.box("p.chair1", (0.6, 0.6, 0.08), (ox - 0.2, oy + 0.9, 0.46), plastic("#a8744a", 0.7), bevel=0.02)
    kit.box("p.chair1b", (0.6, 0.08, 0.7), (ox - 0.2, oy + 1.2, 0.8), plastic("#a8744a", 0.7), bevel=0.02)
    kit.box("p.chair1l", (0.5, 0.5, 0.2), (ox - 0.2, oy + 0.9, 0.3), plastic("#a8744a", 0.7))
    for sx in (-1, 1):
        for k in range(5):
            kit.box(f"p.rail{sx}{k}", (0.09, 0.09, 0.9), (ox + sx * 4.3, oy - 2.0 + k * 1.0, 0.75), trimw)
        kit.box(f"p.railt{sx}", (0.12, 5, 0.1), (ox + sx * 4.3, oy, 1.2), trimw)
    kit.light("porchlight", "POINT", (ox, oy - 2.5, 3.0), 160.0, "#fff0d8", size=1.0, shadow=False)
    # --- main street in July (S06)
    sx0, sy0 = G.STREET
    kit.plane("st.road", (70, 11), (sx0, sy0, 0.02), plastic("#5a606a", 0.9, spec=0.05))
    kit.plane("st.walkN", (70, 3), (sx0, sy0 + 7.0, 0.03), plastic("#efd2b0", 0.9))
    kit.plane("st.walkS", (70, 3), (sx0, sy0 - 7.0, 0.03), plastic("#efd2b0", 0.9))
    cols = ["#ee9c86", "#f6d8b8", "#e8b49c", "#f2c9a8", "#9fd0f0", "#ffe08a"]
    for i in range(10):
        for sgn in (-1, 1):
            xx = sx0 - 22 + i * 5.0
            h = 4.4 + (i % 3) * 0.8
            kit.box(f"st.h{sgn}{i}", (4.6, 5, h), (xx, sy0 + sgn * 10.5, h / 2), plastic(cols[(i + (sgn > 0)) % 6], 0.7, spec=0.05))
            kit.box(f"st.w{sgn}{i}", (1.4, 0.1, 1.2), (xx, sy0 + sgn * 7.97, 1.9), plastic("#7fb2cc", 0.2, spec=0.7))
            kit.box(f"st.d{sgn}{i}", (1.0, 0.1, 2.1), (xx + 1.5, sy0 + sgn * 7.97, 1.05), plastic("#8a5a3a", 0.6))
    flag = ["#ff5fa0", "#ffd23f", "#3fd0ff", "#ff8a3a", "#7be06a", "#ffffff"]
    for line in range(-4, 5):
        lx0 = sx0 + line * 4.5
        kit.box(f"st.line{line}", (0.03, 16, 0.03), (lx0, sy0, 4.6), plastic("#444444", 0.8))
        for k in range(-7, 8):
            kit.box(f"st.flag{line}_{k}", (0.03, 0.34, 0.34), (lx0, sy0 + k * 1.05, 4.4 - 0.02 * abs(k)), plastic(flag[(k + line) % 6], 0.6),
                    rot=(0.78, 0, 0))
    W["snow"] = []
    rnd = random.Random(7)
    sm = kit.emit("#ffffff", 0.0, "snowmat") if False else plastic("#ffffff", 0.9, spec=0.0)
    for k in range(110):
        W["snow"].append((kit.box(f"flake{k}", (0.07, 0.07, 0.07), (0, 0, 0), sm),
                          rnd.uniform(-9, 9), rnd.uniform(-6, 6), rnd.uniform(0, 7), rnd.uniform(0.7, 1.1), rnd.uniform(0, 6.28)))
    kit.light("streetlight", "POINT", (sx0 - 6, sy0 - 2.0, 3.0), 120.0, "#fff0d8", size=1.0, shadow=False)
    # --- Mr. Pike's yard (S05, S07)
    yx, yy = G.YARD
    kit.plane("y.lawn", (30, 20), (yx, yy, 0.02), plastic("#8fd070", 0.9, spec=0.02))
    kit.plane("y.path", (1.4, 12), (yx - 3.0, yy - 3.0, 0.03), plastic("#e8d8b8", 0.9))
    for k in range(18):
        kit.box(f"y.fence{k}", (0.14, 0.05, 1.1), (yx - 6.5 + k * 0.76, yy + 3.6, 0.55), plastic("#fff6e6", 0.7))
    kit.box("y.fencer1", (13.5, 0.06, 0.1), (yx, yy + 3.57, 0.4), plastic("#fff6e6", 0.7))
    kit.box("y.fencer2", (13.5, 0.06, 0.1), (yx, yy + 3.57, 0.85), plastic("#fff6e6", 0.7))
    tree(kit, "y.tree1", yx + 4.5, yy + 6.0, 0, 8.0)
    tree(kit, "y.tree2", yx - 5.0, yy + 7.0, 0, 7.0)
    kit.box("y.house", (7, 4, 4.0), (yx + 1.5, yy + 9.0, 2.0), plastic("#f2c9a8", 0.7, spec=0.05))
    kit.box("y.roof", (7.6, 4.6, 0.4), (yx + 1.5, yy + 9.0, 4.2), plastic("#c4624a", 0.7, spec=0.1))
    for k in range(6):
        kit.sphere(f"y.bush{k}", 0.4, (yx - 3.5 + k * 1.3, yy + 3.0, 0.4), plastic("#4f9e4a", 0.8), seg=8)
    kit.light("yardlight", "POINT", (yx, yy - 2.5, 3.0), 160.0, "#fff0d8", size=1.0, shadow=False)


# ---------------------------------------------------------------------------------------------- the rule tag
def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    cream = kit.emit("#f6eed6", 0.8, "tagcream")
    edge = kit.emit("#2a4a5c", 0.5, "tagedge")
    ink = kit.emit("#1d3b4f", 0.7, "taginkd")
    page = kit.emit("#f6eed6", 0.8, "tagpage")

    def b(name, size, loc, mat, parent=root, rot=(0, 0, 0)):
        ob = kit.box(name, size, loc, mat, parent, rot=rot)
        noshadow(ob)
        return ob

    b("tag.edge", (2.0, 0.9, 0.004), (0, 0, 0.0), edge)
    b("tag.plate", (1.92, 0.82, 0.004), (0, 0, 0.004), cream)
    # an open book: a dark cover with two pale pages and a spine
    b("tag.cover", (0.74, 0.52, 0.004), (-0.66, 0, 0.008), ink)
    b("tag.pageL", (0.3, 0.4, 0.004), (-0.85, 0.0, 0.012), page, rot=(0, 0, 0.08))
    b("tag.pageR", (0.3, 0.4, 0.004), (-0.47, 0.0, 0.012), page, rot=(0, 0, -0.08))
    for k in range(3):
        b(f"tag.line{k}", (0.18, 0.025, 0.004), (-0.85, 0.1 - 0.1 * k, 0.016), ink)
        b(f"tag.line{k}r", (0.18, 0.025, 0.004), (-0.47, 0.1 - 0.1 * k, 0.016), ink)
    W["tag_disp"] = Display(kit, "tagnum", root, ink, "xy", 0.03)


def _first_frame(kit, story):
    gh = bpy.data.objects.get("grandpa.headg")
    if gh is not None:
        beard = kit.plastic("#dcdcd4", 0.9, spec=0.02)
        # a short beard on the chin only, below a clear mouth line
        kit.box("gp.chin", (0.66, 0.16, 0.2), (0, -0.53, -0.57), beard, gh, bevel=0.06)
        # the hat tipped back about 14 degrees so the brim clears his eyes
        crown, brim = bpy.data.objects.get("grandpa.bcrown"), bpy.data.objects.get("grandpa.bbrim")
        if crown is not None and brim is not None:
            piv = kit.empty("gp.hatpiv", (0, 0.5, crown.location.z - 0.1), gh)
            bpy.context.view_layer.update()
            for ob in (crown, brim):
                mw = ob.matrix_world.copy()
                ob.parent = piv
                ob.matrix_world = mw
            piv.rotation_euler = (-14 * D2R, 0, 0)
    hh = bpy.data.objects.get("husband.headg")
    if hh is not None:   # thin warm rims, no grey lenses: they read as glasses, not a visor
        rim = kit.plastic("#d9b36a", 0.5)
        for sx in (-1, 1):
            for nm in (f"husband.gl{sx}", f"husband.glf{sx}"):
                ob = bpy.data.objects.get(nm)
                if ob is not None:
                    ob.hide_render = True
            lens = bpy.data.objects.get(f"husband.gl{sx}")
            ly_ = lens.location.y if lens is not None else -0.55
            cx_, cz_ = sx * 0.24, -0.02
            for k, (w_, h_, ox_, oz_) in enumerate([(0.4, 0.035, 0, 0.15), (0.4, 0.035, 0, -0.15),
                                                    (0.035, 0.3, -0.19, 0), (0.035, 0.3, 0.19, 0)]):
                kit.box(f"husband.rim{sx}{k}", (w_, 0.04, h_), (cx_ + ox_, ly_ - 0.02, cz_ + oz_), rim, hh)
    W["inited"] = True


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    look = look_at(tl, t)
    gains = {"sun": look["sun"], "fill": look["fill"], "lamp": look["lamp"], "shopday": look["shopday"],
             "shopnight": look["night"], "doornight": look["night"], "outnight": look["night"], "cntnight": look["night"]}
    # the sky is always from the look
    so = kit.LIGHTS["sun"]["obj"]
    az, el = look["az"] * D2R, look["el"] * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    so.location = d * 60
    kit.aim(so, (0, 0, 0))
    kit.LIGHTS["sun"]["light"].color = look["sun_col"]
    kit.LIGHTS["fill"]["light"].color = look["fill_col"]
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*look["sky"], 1.0)
    bg.inputs["Strength"].default_value = look["sky_str"]
    W["moon"].hide_render = look["moon"] < 0.5
    W["streak"].hide_render = look["moon"] < 0.5
    # the count: the tag and the slate always agree
    s, sc = count_state(tl, t)
    # the tag sits in the top-left corner at a fixed fraction of the frame, whatever the lens
    lens = 40.0
    shot = next((x for x in tl["shots"] if x["start"] <= t < x["end"]), tl["shots"][-1])
    spec = next((x for x in story["shots"] if x["id"] == shot["id"]), None)
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
    tag = W["tag"]
    s_ = 0.2 * w2 * 2.0
    tag.scale = (s_, s_, s_)
    tag.location = (-w2 + 0.045 * 2 * w2 + s_, h2 - 0.065 * 2 * h2 - 0.45 * s_, -dist)
    W["tag_disp"].show(s, sc, 0.28, 1.1, 0.56)
    W["slate"].show(s, sc, 0.0, 0.62, 0.34)
    # the screen door, the hook, the rods
    W["door"].rotation_euler = (0, 0, sample_cue(tl, "door", t, "a", 0.0, 0.6) * D2R)
    hu = sample_cue(tl, "hook", t, "u", 0.0, 0.5)
    W["hook"].rotation_euler = (0, -55 * D2R * (1 - hu), 0)
    rs = last_cue(tl, "rods", t)
    door_side = bool(rs and rs.get("at_door"))
    rd = W["rods"]
    if door_side:
        rd.location = (G.DOOR_X - 0.5, -6.3, 0)
        rd.rotation_euler = (-6 * D2R, 0, 0)
    else:
        rd.location = (-5.6, 1.4, 0)
        rd.rotation_euler = (0, -6 * D2R, 0)
    W["tbox"].hide_render = not (rs and rs.get("box"))
    # L64: the jacket is half on: my screen-right sleeve is bare skin (a cue "halfon")
    ho = last_cue(tl, "halfon", t)
    bare = bool(ho and ho.get("on"))
    skin_ob = bpy.data.objects.get("me.skinarm1")
    for nm in ("me.sleeve1",):
        ob = bpy.data.objects.get(nm)
        if ob is None or skin_ob is None or not ob.data.materials:
            continue
        W.setdefault("sleeve_mat", {})
        W["sleeve_mat"].setdefault(nm, ob.data.materials[0])
        ob.data.materials[0] = skin_ob.data.materials[0] if bare else W["sleeve_mat"][nm]
    # the car: where it stands, or wherever "me" is driving it
    cc = last_cue(tl, "car", t)
    car = W["car"]
    if cc and cc.get("mode") == "me":
        me = bpy.data.objects.get("me")
        if me is not None:
            car.location = (me.location.x - G.CAR_DX, me.location.y - G.CAR_DY, cc.get("z", 0.0))
            car.rotation_euler = (0, 0, 0)
    elif cc:
        car.location = (cc["x"], cc["y"], cc.get("z", 0.0))
        car.rotation_euler = (0, 0, cc.get("yaw", 0.0) * D2R)
    bg_ = last_cue(tl, "bag", t)
    W["bag"].hide_render = not (bg_ and bg_.get("on"))
    # the July snow falls and drifts
    sx0, sy0 = G.STREET
    for (ob, x0, y0, z0, sp, ph) in W["snow"]:
        z = (z0 - sp * t) % 7.0
        ob.location = (sx0 + x0 + 0.35 * math.sin(0.7 * t + ph), sy0 + y0 + 0.2 * math.cos(0.5 * t + ph), z)
    # who sits: legs straight out forward, hips on the seat (eased over the cue's dur)
    sits = {}
    for c in tl["cues"]:
        if c["name"] == "sit" and c["t"] <= t:
            sits[c["who"]] = c
    for who, c in sits.items():
        root = bpy.data.objects.get(who)
        if root is None:
            continue
        dur = c.get("dur", 0.0)
        u = ss((t - c["t"]) / dur) if dur > 0 else 1.0
        fr = u if c.get("on") else 1.0 - u
        if fr <= 0.0:
            continue
        root.location.z += (c.get("z", 0.47) - 0.68) * fr
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg:
                leg.rotation_euler = (-math.pi / 2 * 0.97 * fr, 0, 0)
    return gains


def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    sun = kit.light("sun", "SUN", (0, -30, 40), 1.0, "#fff0d8", size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#cfe6ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    build_stages(kit)
    build_shop(kit, {})
    build_car(kit)
    build_tag(kit)
    return {}
