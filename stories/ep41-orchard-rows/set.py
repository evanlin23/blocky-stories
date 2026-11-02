"""Orchard Rows: a cobbled dusk street, a townsman's kitchen, a garden path, and Nan's orchard (batch 4, ep41).
Built from kit.py's parts; nothing here is shared with another story's set.

Places are in geo.py. The glowing footprints are the rule's marker: soles that glow on every character (added to
the rig's legs on the first frame) and trails of flat emissive prints that cues turn on and off:

  {"name": "trail", "id", "color", "kind": "glow"|"dark", "strength", "z", "gap", "lat", "every", "rise",
   "lines": [[[x, y], ...], ...] (static, all at once) or "walker": who (a print at each footstep from the cue on),
   "offset": [dx, dy], "per_print": bool, "boost": {"who", "factor", "dur", "radius"} (a print brightens when that
   character's foot lands within radius of it)}
  {"name": "trail_off", "id", "dur"}   {"name": "trail_str", "id", "value", "dur"}

Other cues: tod (dusk, night, dawn, day, sunrise, silver), rough (the Rough One: on, pos, yaw), lamp (the porch
lamp: to, dur), blind (to, dur), daywin (to, dur), door (to, dur), fridge (on, dur), vis (show/hide prop groups),
leaves (on, at_xy).

Every light change is a ramp of at least 0.3 s, or happens on a cut. The Rough One is built once (build_rough) and
posed by cue. Acting keys read here that acting.py ignores: "sit": true (R6 sitting on the bench).
"""

from __future__ import annotations

import importlib.util
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import acting, rig

HERE = Path(__file__).resolve().parent
_gs = importlib.util.spec_from_file_location("orchard_geo", HERE / "geo.py")
geo = importlib.util.module_from_spec(_gs)
_gs.loader.exec_module(geo)
OY, F = geo.OY, geo.FLOOR
S = rig.S

CLAY, SACK = "#a8482e", "#7a5a38"


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def cues_of(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def last_cue(cs, t):
    cs = [c for c in cs if c["t"] <= t + 1e-9]
    return cs[-1] if cs else None


def ramp_val(cs, key, t, default):
    """Piecewise: each cue eases from the value the previous one finished at (or was part way to) over its dur."""
    v0 = default
    for i, c in enumerate(cs):
        if c["t"] > t + 1e-9:
            break
        d = max(0.3, c.get("dur", 0.3))
        if t >= c["t"] + d:
            v0 = c[key]
        else:
            return v0 + (c[key] - v0) * ss((t - c["t"]) / d)
    return v0


# ------------------------------------------------------------------------------------------------ helpers
def slab(kit, name, x0, x1, y0, y1, z0, z1, mat, parent=None):
    return kit.box(name, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), mat, parent)


def wall(kit, name, axis, c, a0, a1, z0, z1, holes, mat, th=0.2):
    """A wall along `axis` ("x": it runs along x at y = c) from a0 to a1, with rectangular holes (h0, h1, hz0, hz1)."""
    zs = sorted({z0, z1, *[h[2] for h in holes], *[h[3] for h in holes]})
    zs = [z for z in zs if z0 <= z <= z1]
    for za, zb in zip(zs, zs[1:]):
        if zb - za < 1e-4:
            continue
        cuts = sorted([(h[0], h[1]) for h in holes if h[2] <= za + 1e-6 and h[3] >= zb - 1e-6])
        segs, cur = [], a0
        for h0, h1 in cuts:
            if h0 > cur:
                segs.append((cur, h0))
            cur = max(cur, h1)
        if cur < a1:
            segs.append((cur, a1))
        for s0, s1 in segs:
            if axis == "x":
                slab(kit, name, s0, s1, c - th / 2, c + th / 2, za, zb, mat)
            else:
                slab(kit, name, c - th / 2, c + th / 2, s0, s1, za, zb, mat)


def empty(kit, name, loc=(0, 0, 0), parent=None):
    return kit.empty(name, loc, parent)


# ------------------------------------------------------------------------------------------------ the world
TOD = {
    #           sun colour, sun power, sun travel direction, world colour, world power, fog colour, exposure
    "dusk":    ("#ffb472", 4.8, (0.30, 0.90, -0.30), "#d8b79c", 0.55, "#b9a291", 0.0),
    "night":   ("#8aa6e0", 0.6, (-0.45, 0.55, -0.70), "#1c2438", 0.2, "#2a3548", 0.55),
    "dawn":    ("#c4d6f2", 3.0, (-1.00, -0.12, -0.20), "#9fb0c2", 0.70, "#97a6b6", 0.15),
    "day":     ("#ffe6bc", 4.4, (0.15, -0.90, -0.35), "#d8d2c0", 0.80, "#c9c6b8", 0.0),
    "sunrise": ("#ffbe80", 4.6, (0.20, -0.95, -0.14), "#e8c8a0", 0.75, "#dcbc9a", 0.0),
    "silver":  ("#b4c4e6", 1.6, (-0.50, 0.40, -0.70), "#4a5670", 0.40, "#56637a", 0.55),
}
# gains of the room and street lights per time of day: lamps (the town's), kitchen, myroom, bedroom
ROOM = {"dusk": (0.75, 1.0, 0.3, 0.3), "night": (1.0, 0.35, 1.0, 0.8), "dawn": (0.1, 0.45, 0.3, 0.3),
        "day": (0.0, 0.6, 0.3, 0.3), "sunrise": (0.1, 0.5, 0.3, 0.3), "silver": (0.4, 0.0, 0.0, 0.0)}
# the Rough One's key (low, from the side) and rim, per time of day
RLIGHT = {"dusk": 0.5, "night": 1.8, "dawn": 0.8, "day": 0.3, "sunrise": 0.3, "silver": 1.0}


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lin(c):
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def mats(kit):
    M = {}
    M["white"] = kit.plastic("#e8e2d4", 0.9, name="whitewash")
    M["trim"] = kit.plastic("#4a3a2a", 0.8, name="trim")
    M["roof"] = kit.plastic("#5a3a2e", 0.85, name="roof")
    M["floor"] = kit.planks("#cdbd9a", "#b9a780", scale=1.0, axis="X", name="floor pale")
    M["deck"] = kit.planks("#8a6a48", "#6e5236", scale=1.3, axis="Y", name="deck")
    M["wood"] = kit.plastic("#7a5a3a", 0.8, name="wood")
    M["woodlight"] = kit.plastic("#a08560", 0.8, name="woodlight")
    M["bench"] = kit.planks("#8e7550", "#6f5a3c", scale=2.0, axis="X", name="bench wood")
    M["grass"] = kit.grime("#4f6b3a", 0.55, 2.2, name="grass", rough=0.95)
    M["moss"] = kit.plastic("#4f6b3a", 0.95, name="moss")
    M["trunk"] = kit.plastic("#4a3524", 0.95, name="trunk")
    M["leafg"] = kit.plastic("#d9a441", 0.9, name="leaf gold")
    M["leafr"] = kit.plastic("#a4552a", 0.9, name="leaf rust")
    M["leafy"] = kit.plastic("#8c8a3a", 0.9, name="leaf olive")
    M["apple"] = kit.plastic("#c0263a", 0.18, name="apple", spec=0.7)
    M["cobble"] = kit.cobbles("#3b3d44", "#6d6a66", "#1a1a1d", 2.6, 0.3, name="cobbles")
    M["brick"] = kit.bricks("#7a3b2a", "#5e2c22", "#4a4540", 1.0, name="brick")
    M["plaster"] = kit.plastic("#cbb99a", 0.9, name="plaster")
    M["plaster2"] = kit.plastic("#a9b4a6", 0.9, name="plaster green")
    M["timber"] = kit.plastic("#3e2c1e", 0.85, name="timber")
    M["slate"] = kit.plastic("#2c2f38", 0.8, name="slate")
    M["warm"] = kit.emit("#ffc27a", 3.2, name="warm window")
    M["lamphead"] = kit.emit("#ffcf94", 6.0, name="lamp head")
    M["iron"] = kit.metal("#25272b", 0.5, name="iron")
    M["linen"] = kit.plastic("#e4dcc8", 0.95, name="linen")
    M["tile"] = kit.checker("#d7dcdc", "#a4b0b4", 3.0, name="tile")
    M["white2"] = kit.plastic("#dfe3e4", 0.5, name="fridge")
    M["fridgeglow"] = kit.emit("#dcecff", 2.2, name="fridge glow")
    M["hedge"] = kit.plastic("#2f4a2a", 0.95, name="hedge")
    M["gravel"] = kit.plastic("#8a8478", 0.95, name="gravel")
    M["green"] = kit.plastic("#2e6b3c", 0.7, name="green door")
    M["brass"] = kit.metal("#b79a4a", 0.35, name="brass")
    M["wicker"] = kit.plastic("#9a7a46", 0.9, name="wicker")
    M["stroke"] = kit.plastic(CLAY, 0.95, name="stroke")
    M["quilt"] = kit.checker("#8a3b44", "#d8c9a8", 5.0, name="quilt")
    M["quilt2"] = kit.plastic("#8a3b44", 0.95, name="quilt red")
    M["sheet"] = kit.plastic("#ece6d8", 0.95, name="sheet")
    M["slipper"] = kit.plastic("#b8996a", 0.95, name="slipper tan")
    M["wool"] = kit.plastic("#e2d3b0", 0.98, name="sheepskin")
    M["boot"] = kit.plastic("#5a3a22", 0.7, name="boot leather")
    M["bootsole"] = kit.plastic("#1e1a16", 0.9, name="boot sole")
    M["lace"] = kit.plastic("#d8c9a0", 0.8, name="lace")
    M["wire"] = kit.metal("#9aa0a8", 0.35, name="wire")
    M["puddle"] = kit.plastic("#2b3640", 0.04, name="puddle", spec=0.9)
    M["mat"] = kit.plastic("#4a3a2c", 0.98, name="doormat")
    M["dark"] = kit.plastic("#05060a", 1.0, name="cut black")
    M["clay"] = kit.grime("#7a4535", 0.55, 9.0, name="clay rough", rough=1.0)
    M["sack"] = kit.checker("#5e4529", "#503a22", 80.0, name="sack weave", rough=1.0)
    M["glint"] = kit.emit("#bcd4ff", 4.0, name="glint")
    M["rsil"] = kit.plastic("#07090d", 0.9, name="rough silhouette")
    M["cutblack"] = kit.emit("#000000", 0.0, name="cut unlit")
    M["mist"] = kit.emit("#8a98a6", 0.05, name="mist in the cut")
    M["sqdark"] = kit.plastic("#18200f", 0.95, name="wet dark")
    M["sunk"] = kit.plastic("#16200f", 1.0, name="pressed")
    M["metalrod"] = kit.metal("#6a6c70", 0.5, name="ladder")
    M["bag"] = kit.plastic("#4a5a3a", 0.9, name="bag")
    M["mug"] = kit.plastic("#d8d0c0", 0.5, name="mug")
    M["rail"] = kit.plastic("#d9d2c0", 0.8, name="rail")
    M["crate"] = kit.planks("#a98a5a", "#8a6c42", scale=3.0, axis="X", name="crate")
    M["leaf"] = kit.plastic("#c9922e", 0.9, name="falling leaf")
    return M


def build_tree(kit, M, variant):
    root = kit.empty(f"tree proto {variant}", (0, 0, -50))
    kit.box("trunk", (0.3, 0.3, 1.75), (0, 0, 0.875), M["trunk"], root)
    leaves = [M["leafg"], M["leafr"], M["leafy"]] if variant == 0 else [M["leafr"], M["leafg"], M["leafg"]]
    kit.box("c1", (2.2, 2.0, 0.95), (0.0, 0.0, 2.15), leaves[0], root, bevel=0.06)
    kit.box("c2", (1.55, 1.5, 0.75), (0.25, -0.1, 2.85), leaves[1], root, bevel=0.06)
    kit.box("c3", (1.4, 1.7, 0.6), (-0.4, 0.2, 1.75), leaves[2], root, bevel=0.06)
    rng = random.Random(variant + 5)
    for i in range(7):
        kit.box(f"ap{i}", (0.13, 0.13, 0.13), (rng.uniform(-0.9, 0.9), rng.uniform(-0.8, 0.8), 1.55 + rng.uniform(0, 0.15)),
                M["apple"], root, bevel=0.025)
    return root


def clone(root, loc, rz, sc, name):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.location = loc
    e.rotation_euler = (0, 0, rz)
    e.scale = (sc, sc, sc)
    for ch in root.children:
        c = ch.copy()
        c.parent = e
        bpy.context.scene.collection.objects.link(c)
    return e


def build_orchard(kit, ctx, M):
    cy = OY + 35
    kit.plane("grass", (160, 190), (0, cy, 0), M["grass"])
    protos = [build_tree(kit, M, 0), build_tree(kit, M, 1)]
    rng = random.Random(41)
    for r in range(7):
        y = OY + geo.ROW0 + geo.ROW_GAP * r
        for x in (-23, -19, -15, -11, -7, -3, 3, 7, 11, 15, 19, 23):
            clone(protos[(r + int(x)) % 2], (x + rng.uniform(-0.25, 0.25), y + rng.uniform(-0.25, 0.25), 0),
                  rng.uniform(0, 6.28), rng.uniform(0.92, 1.14), "tree")
    # a far tree line, so the fog has something to swallow
    for x in range(-40, 41, 5):
        clone(protos[x % 2], (x, OY + 80, 0), 0.4 * x, 1.2, "far tree")
    # the gate at the start of the rows
    for sx in (-1, 1):
        kit.box("gatepost", (0.22, 0.22, 1.5), (sx * 1.4, OY + 9.8, 0.75), M["wood"])
    # the gate, wide open: each leaf swung back and hooked against its post
    for sx in (-1, 1):
        gx = sx * 1.62
        kit.box("gate rail", (0.07, 1.3, 0.07), (gx, OY + 10.5, 0.95), M["wood"])
        kit.box("gate rail", (0.07, 1.3, 0.07), (gx, OY + 10.5, 0.55), M["wood"])
        kit.box("gate rail", (0.07, 1.3, 0.07), (gx, OY + 10.5, 0.2), M["wood"])
        kit.box("gate stile", (0.09, 0.09, 1.1), (gx, OY + 11.1, 0.55), M["wood"])
        kit.box("gate hook", (0.05, 0.25, 0.04), (sx * 1.5, OY + 9.95, 0.75), M["iron"])
    # crates and the odd ladder
    for (x, y) in [(-4.2, 12.4), (4.6, 20.0), (-6.0, 28.0), (6.2, 44.0), (-4.8, 52.0)]:
        kit.box("crate", (0.7, 0.5, 0.4), (x, OY + y, 0.2), M["crate"], rot=(0, 0, 0.3))
    # bench
    by = OY + geo.BENCH_Y
    kit.box("bench seat", (1.9, 0.5, 0.08), (0, by, 0.46), M["bench"])
    kit.box("bench back", (1.9, 0.07, 0.5), (0, by + 0.26, 0.78), M["bench"], rot=(-0.12, 0, 0))
    for sx in (-0.8, 0.8):
        kit.box("bench leg", (0.08, 0.46, 0.46), (sx, by, 0.23), M["bench"])
    for sx in (-0.07, 0.07):
        kit.box("tally", (0.045, 0.2, 0.012), (sx, by - 0.02, 0.506), M["stroke"], rot=(0, 0, 0.04 * sx))
    ctx["bench_y"] = by


def build_house(kit, ctx, M):
    x0, x1, y0, y1 = geo.H_X0, geo.H_X1, OY + geo.H_Y0, OY
    ctx["house"] = (x0, x1, y0, y1)
    slab(kit, "plinth", x0, x1, y0, y1, -0.05, F, M["white"])
    kit.box("floor", (x1 - x0 - 0.3, y1 - y0 - 0.3, 0.02), ((x0 + x1) / 2, (y0 + y1) / 2, F + 0.01), M["floor"])
    zt = F + 2.9
    door = (geo.DOOR_X - 0.5, geo.DOOR_X + 0.5, F, F + 2.2)
    win = (geo.WIN_X0, geo.WIN_X1, geo.WIN_Z0, geo.WIN_Z1)
    wall(kit, "wall n", "x", y1, x0, x1, F, zt, [door, win], M["white"])
    wall(kit, "wall s", "x", y0, x0, x1, F, zt, [], M["white"])
    wall(kit, "wall w", "y", x0, y0, y1, F, zt, [], M["white"])
    wall(kit, "wall e", "y", x1, y0, y1, F, zt, [], M["white"])
    wall(kit, "part 1", "y", geo.PART_X1, y0, y1, F, zt, [], M["white"], th=0.14)
    wall(kit, "part 2", "y", geo.PART_X2, y0, y1, F, zt, [(OY - 6.0, OY - 5.0, F, F + 2.1)], M["white"], th=0.14)
    slab(kit, "roof", x0 - 0.5, x1 + 0.5, y0 - 0.5, y1 + 0.7, zt, zt + 0.16, M["roof"])
    kit.box("chimney", (0.7, 0.7, 1.2), (-0.3, OY - 6.9, zt + 0.7), M["brick"])
    # window frame and mullions
    wx = (geo.WIN_X0 + geo.WIN_X1) / 2
    wzm = (geo.WIN_Z0 + geo.WIN_Z1) / 2
    for fx in (geo.WIN_X0, geo.WIN_X1):
        kit.box("frame", (0.07, 0.26, geo.WIN_Z1 - geo.WIN_Z0), (fx, OY, wzm), M["trim"])
    for fz in (geo.WIN_Z0, geo.WIN_Z1):
        kit.box("frame", (geo.WIN_X1 - geo.WIN_X0, 0.26, 0.07), (wx, OY, fz), M["trim"])
    kit.box("mullion", (0.05, 0.1, geo.WIN_Z1 - geo.WIN_Z0), (wx, OY + 0.02, wzm), M["trim"])
    kit.box("mullion", (geo.WIN_X1 - geo.WIN_X0, 0.1, 0.05), (wx, OY + 0.02, wzm + 0.1), M["trim"])
    # the blind: pale linen on a roller
    kit.cyl("roller", 0.05, geo.WIN_X1 - geo.WIN_X0 - 0.04, (wx, OY - 0.2, geo.WIN_Z1 - 0.06), M["trim"], rot=(0, math.pi / 2, 0))
    ctx["blind"] = kit.box("blind", (geo.WIN_X1 - geo.WIN_X0 - 0.05, 0.03, 1.0), (wx, OY - 0.2, geo.WIN_Z0), M["linen"])
    # porch, steps, rail, lamp
    slab(kit, "deck", -1.0, 1.0, OY + 0.1, OY + 1.3, F - 0.08, F, M["deck"])
    slab(kit, "step1", -0.9, 0.9, OY + 1.3, OY + 1.65, 0, 0.6, M["deck"])
    slab(kit, "step2", -0.9, 0.9, OY + 1.65, OY + 2.0, 0, 0.3, M["deck"])
    for ry in (OY + 0.3, OY + 1.2):
        kit.box("post", (0.08, 0.08, 0.95), (1.0, ry, F + 0.48), M["rail"])
    kit.box("rail", (0.07, 1.0, 0.07), (1.0, OY + 0.75, F + 0.95), M["rail"])
    kit.box("lamp bracket", (0.06, 0.3, 0.05), (1.05, OY + 0.2, F + 2.55), M["iron"])
    ctx["lamp_mat"] = kit.emit("#ffcf94", 2.2, name="porch lamp")
    kit.box("lamp", (0.2, 0.2, 0.28), (1.05, OY + 0.4, F + 2.48), ctx["lamp_mat"])
    # the back door, hinged on the left, opening in
    hinge = kit.empty("door hinge", (geo.DOOR_X + 0.5, OY, F))
    kit.box("door leaf", (0.98, 0.06, 2.18), (-0.49, 0.0, 1.09), M["wood"], hinge)
    kit.box("door knob", (0.07, 0.1, 0.07), (-0.86, 0.04, 1.05), M["brass"], hinge)
    ctx["door"] = hinge
    kit.box("doormat", (0.8, 0.5, 0.025), (geo.DOOR_X, OY - 0.55, F + 0.012), M["mat"])
    # the kitchen
    kit.box("stove", (0.95, 0.7, 0.95), (-0.3, OY - 7.0, F + 0.475), M["iron"])
    kit.box("stove top", (1.0, 0.75, 0.05), (-0.3, OY - 7.0, F + 0.97), M["iron"])
    kit.cyl("flue", 0.1, 1.6, (-0.3, OY - 7.1, F + 1.8), M["iron"])
    slab(kit, "counter", geo.WIN_X0 - 0.2, geo.WIN_X1 + 0.2, OY - 0.7, OY - 0.12, F, F + 0.92, M["woodlight"])
    kit.box("basin", (0.6, 0.4, 0.04), (wx, OY - 0.4, F + 0.94), M["white2"])
    kit.box("table top", (1.3, 0.8, 0.06), (1.3, OY - 4.6, F + 0.75), M["woodlight"])
    for tx in (0.7, 1.9):
        for ty in (-4.9, -4.3):
            kit.box("table leg", (0.07, 0.07, 0.75), (tx, OY + ty, F + 0.375), M["woodlight"])
    kit.box("shelf", (1.4, 0.25, 0.04), (-1.8, OY - 7.3, F + 1.7), M["woodlight"])
    # the slippers by the stove, soaked, with a small puddle
    for sx in (-1.15, -0.95):   # tan sheepskin, dry
        kit.box("slipper", (0.14, 0.32, 0.09), (sx, OY - 6.5, F + 0.05), M["slipper"], bevel=0.03)
        kit.box("slipper wool", (0.12, 0.2, 0.05), (sx, OY - 6.58, F + 0.1), M["wool"], bevel=0.02)
    # beds
    kit.box("bed frame", (1.5, 2.1, 0.4), (4.0, OY - 5.7, F + 0.2), M["wood"])
    kit.box("mattress", (1.4, 2.0, 0.18), (4.0, OY - 5.7, F + 0.49), M["sheet"], bevel=0.03)
    kit.box("pillow", (0.9, 0.4, 0.14), (4.0, OY - 6.5, F + 0.65), M["sheet"], bevel=0.05)
    kit.box("quilt", (1.45, 1.3, 0.1), (4.0, OY - 5.0, F + 0.63), M["quilt"], bevel=0.03)
    kit.box("quilt turned", (1.45, 0.55, 0.1), (4.0, OY - 5.75, F + 0.75), M["quilt2"], rot=(0.5, 0, 0), bevel=0.03)
    kit.box("my bed", (1.0, 2.3, 0.4), (-4.8, OY - 3.0, F + 0.2), M["wood"], rot=(0, 0, math.pi / 2))
    kit.box("my mattress", (2.3, 1.0, 0.16), (-4.8, OY - 3.0, F + 0.48), M["sheet"], bevel=0.03)
    kit.box("my pillow", (0.4, 0.7, 0.14), (-5.65, OY - 3.0, F + 0.63), M["sheet"], bevel=0.05)
    kit.box("my quilt", (1.3, 1.05, 0.1), (-4.5, OY - 3.0, F + 0.62), M["quilt2"], bevel=0.03)


def build_town(kit, ctx, M):
    kit.plane("cobbles", (30, 110), (0, 5, 0), M["cobble"])
    rng = random.Random(7)
    mats_ = [M["brick"], M["plaster"], M["plaster2"], M["brick"], M["plaster"]]
    for i, y in enumerate(range(-30, 40, 8)):
        for side in (-1, 1):
            h = rng.uniform(5.2, 6.8)
            m = mats_[(i + (side > 0)) % len(mats_)]
            kit.box("house", (6.4, 7.0, h), (side * 8.0, y + rng.uniform(-0.3, 0.3), h / 2), m)
            kit.box("roof", (7.0, 7.6, 0.6), (side * 8.0, y, h + 0.3), M["slate"])
            kit.box("timber", (0.2, 7.0, 0.2), (side * 4.75, y, 2.9), M["timber"])
            for wy in (-2.0, 0.0, 2.0):
                for wz in (1.7, 4.0):
                    if rng.random() < 0.8:
                        kit.box("window", (0.06, 0.9, 1.1), (side * 4.78, y + wy, wz), M["warm"])
            kit.box("door", (0.1, 1.0, 2.1), (side * 4.78, y + 3.1, 1.05), M["timber"])
        if i % 2 == 0:
            for side in (-1, 1):
                x = side * 3.4
                kit.box("lamp post", (0.12, 0.12, 3.6), (x, y + 3.5, 1.8), M["iron"])
                kit.box("lamp head", (0.3, 0.3, 0.4), (x, y + 3.5, 3.7), M["lamphead"])
                ctx.setdefault("town_lamps", []).append((x, y + 3.5))
    for k, (x, y) in enumerate(ctx.get("town_lamps", [])):
        if y < 22 and k % 1 == 0:
            ctx.setdefault("lamp_names", []).append(f"tl{k}")
            kit.light(f"tl{k}", "POINT", (x * 0.8, y, 3.5), 380, "#ffc27a", size=0.3)
    # the bench with keys
    kit.box("tbench seat", (0.5, 1.6, 0.08), (-3.9, 9.0, 0.46), M["bench"])
    kit.box("tbench back", (0.07, 1.6, 0.5), (-4.15, 9.0, 0.78), M["bench"])
    for dy in (-0.7, 0.7):
        kit.box("tbench leg", (0.4, 0.08, 0.46), (-3.9, 9.0 + dy, 0.23), M["bench"])
    keys = kit.empty("keys", (-3.8, 9.1, 0.52))
    kit.cyl("key ring", 0.05, 0.015, (0, 0, 0.01), M["brass"], keys)
    kit.box("key a", (0.03, 0.14, 0.012), (0.0, -0.1, 0.01), M["brass"], keys)
    kit.box("key b", (0.03, 0.12, 0.012), (0.04, -0.09, 0.01), M["brass"], keys)
    ctx.setdefault("groups", {})["keys"] = [keys] + list(keys.children)


def build_kitchen_town(kit, ctx, M):
    kx, ky = 30.0, 0.0
    kit.plane("tile floor", (6, 5), (kx, ky + 2.5, 0.0), M["tile"])
    wall(kit, "tk s", "x", ky, kx - 3, kx + 3, 0, 2.7, [(29.2, 30.8, 1.0, 2.0)], M["plaster"])
    wall(kit, "tk n", "x", ky + 5, kx - 3, kx + 3, 0, 2.7, [], M["plaster"])
    wall(kit, "tk w", "y", kx - 3, ky, ky + 5, 0, 2.7, [(ky + 1.4, ky + 2.6, 0, 2.1)], M["plaster"])
    wall(kit, "tk e", "y", kx + 3, ky, ky + 5, 0, 2.7, [], M["plaster"])
    kit.box("fridge", (0.85, 0.7, 1.85), (kx + 1.0, ky + 4.6, 0.925), M["white2"])
    hinge = kit.empty("fridge hinge", (kx + 0.55, ky + 4.22, 0))
    kit.box("fridge door", (0.85, 0.07, 1.85), (0.42, 0.0, 0.925), M["white2"], hinge, rot=(0, 0, 0))
    hinge.rotation_euler = (0, 0, -1.9)
    kit.plane("fridge glow", (0.7, 1.6), (kx + 1.0, ky + 4.24, 0.95), M["fridgeglow"], rot=(math.pi / 2, 0, 0))
    kit.box("counter", (0.6, 2.0, 0.9), (kx - 2.65, ky + 3.2, 0.45), M["woodlight"])
    kit.light("fridge", "POINT", (kx + 1.0, ky + 3.9, 1.4), 90, "#d8e8ff", size=0.3)
    kit.light("tkit", "POINT", (kx, ky + 2.0, 2.4), 60, "#9fb4e0", size=0.4)


def build_garden(kit, ctx, M):
    gx = 60.0
    kit.plane("garden", (24, 30), (gx, 0, 0), M["moss"])
    kit.plane("path", (2.0, 18), (gx, 1.5, 0.004), M["gravel"])
    for sx in (-1, 1):
        kit.box("hedge", (0.9, 16, 0.9), (gx + sx * 1.7, 0.5, 0.45), M["hedge"])
    kit.box("front", (12, 0.4, 5.5), (gx, 8.2, 2.75), M["brick"])
    kit.box("roof", (12.8, 1.2, 0.5), (gx, 8.4, 5.7), M["slate"])
    kit.box("green door", (1.6, 0.14, 2.3), (gx, 7.95, 1.15), M["green"])
    for sx in (-1, 1):
        kit.box("garden window", (1.0, 0.06, 1.1), (gx + sx * 3.8, 7.96, 1.9), M["warm"])
    kit.box("lantern", (0.25, 0.25, 0.35), (gx + 1.4, 7.7, 2.5), M["lamphead"])
    kit.light("garden", "POINT", (gx + 1.2, 7.0, 2.5), 160, "#ffc27a", size=0.3)
    kit.light("gmoon", "POINT", (gx - 0.6, 1.0, 4.2), 420, "#9fb4e0", size=0.5)


def build_rough(kit, ctx, M):
    """The Rough One: a person from far too few blocks, 2.5 m. One block a part, no joints. Faces -y."""
    root = kit.empty("rough", (0, 0, -60))
    rng = random.Random(3)

    def blk(name, size, loc, mat, rot=(0, 0, 0), parent=root):
        return kit.box(name, size, loc, mat, parent, rot=rot)

    for sx in (-1, 1):
        blk("leg", (0.44, 0.46, 0.86), (sx * 0.27, 0.0, 0.07 + 0.43), M["sack"], (0, 0, rng.uniform(-0.03, 0.03)))
        blk("foot", (0.56, 0.78, 0.07), (sx * 0.27, -0.14, 0.035), M["sack"])
        blk("arm", (0.36, 0.36, 1.25), (sx * 0.78, 0.02, 0.43 + 0.625 + 0.1), M["sack"], (0, 0, sx * 0.03))
    blk("torso", (1.1, 0.62, 0.76), (0, 0, 0.93 + 0.38), M["clay"], (0, 0, 0.02))
    head = kit.empty("rough head", (0, 0, 1.69 + 0.45), root)
    hp = lambda n, size, loc, m=M["clay"]: kit.box(n, size, loc, m, head)
    hp("back", (0.9, 0.5, 0.9), (0, 0.2, 0))
    hp("top band", (0.9, 0.4, 0.25), (0, -0.25, 0.325))
    hp("low band", (0.9, 0.4, 0.195), (0, -0.25, -0.3525))
    hp("band b", (0.9, 0.4, 0.185), (0, -0.25, -0.0925))
    for (cx, w) in ((-0.375, 0.15), (0.0, 0.2), (0.375, 0.15)):
        hp("band a", (w, 0.4, 0.2), (cx, -0.25, 0.1))
    for cx in (-0.35, 0.35):
        hp("band c", (0.2, 0.4, 0.07), (cx, -0.25, -0.22))
    # the cuts: black inside, set back, with one cold glint deep in each eye hole
    for ex, ez, ew, eh in ((-0.2, 0.1, 0.2, 0.2), (0.2, 0.08, 0.2, 0.2)):
        hp("eye cut", (ew, 0.3, eh), (ex, -0.1, ez), M["cutblack"])
        hp("glint", (0.03, 0.02, 0.03), (ex + 0.03, -0.252, ez - 0.015), M["glint"])
    hp("mouth cut", (0.5, 0.3, 0.07), (0, -0.1, -0.22), M["cutblack"])
    head.rotation_euler = (0.10, 0.0, 0.035)
    ctx["rough"] = root
    ctx["rough_parts"] = [root] + list(root.children_recursive)


def link_rough_lights(kit, ctx):
    """Light linking: the sun and the moon never touch the Rough One (its own key and rim do), so it is side-lit
    from low down with a cool rim and never front-lit by the sky."""
    parts = [o for o in ctx["rough_parts"] if o.type == "MESH"]
    ex = bpy.data.collections.new("rough excluded")
    inc = bpy.data.collections.new("rough only")
    for o in parts:
        ex.objects.link(o)
        inc.objects.link(o)
    for co in ex.collection_objects:
        co.light_linking.link_state = "EXCLUDE"
    kit.LIGHTS["sun"]["obj"].light_linking.receiver_collection = ex
    kit.LIGHTS["daywin"]["obj"].light_linking.receiver_collection = ex
    for n in ("rkey", "rrim"):
        kit.LIGHTS[n]["obj"].light_linking.receiver_collection = inc


def build_lights(kit, ctx):
    kit.light("sun", "SUN", (0, 0, 50), 1.0, "#ffffff", size=0.2)
    kit.light("porch", "POINT", (1.0, OY + 0.6, F + 2.55), 150, "#ffc27a", size=0.2)
    kit.light("kitchen", "POINT", (-0.4, OY - 3.4, F + 2.4), 260, "#ffd29a", size=0.3)
    kit.light("myroom", "POINT", (-4.8, OY - 1.6, F + 2.3), 90, "#aac0ff", size=0.3)
    kit.light("bedroom", "POINT", (3.9, OY - 3.0, F + 2.3), 110, "#ffd29a", size=0.3)
    kit.light("daywin", "AREA", (geo.WIN_X0 / 2 + geo.WIN_X1 / 2, OY + 0.9, F + 1.6), 520, "#fff0d8", rot=(-math.pi / 2, 0, 0), size=1.4)
    kit.light("benchl", "POINT", (0.0, OY + 66.5, 3.4), 420, "#a8bce8", size=0.6)
    kit.light("pairl", "POINT", (0, 0, -60), 260, "#ffd9a8", size=0.4)
    kit.light("rkey", "POINT", (0, 0, -60), 150, "#b8c8ea", size=0.25)
    kit.light("rrim", "POINT", (0, 0, -60), 480, "#8fb4ff", size=0.3)


def build_extras(kit, ctx, M):
    groups = ctx.setdefault("groups", {})
    # the basket with apples
    b = kit.empty("basket", (-3.0, OY + 12.0, 0))
    kit.box("b", (0.55, 0.42, 0.3), (0, 0, 0.15), M["wicker"], b)
    for i in range(5):
        kit.box("ap", (0.14, 0.14, 0.14), (-0.15 + 0.08 * i, 0.03 * (i % 2), 0.34), M["apple"], b, bevel=0.03)
    groups["basket"] = [b] + list(b.children)
    # a ladder against row 3
    lad = kit.empty("ladder", (5.9, OY + 31.2, 0), None)
    lad.rotation_euler = (0, -0.2, 0)
    for sy in (-0.2, 0.2):
        kit.box("rail", (0.05, 0.05, 2.6), (0, sy, 1.3), M["woodlight"], lad)
    for k in range(8):
        kit.box("rung", (0.05, 0.44, 0.04), (0, 0, 0.3 + k * 0.3), M["woodlight"], lad)
    groups["ladder"] = [lad] + list(lad.children)
    # mugs on the rail
    mugs = kit.empty("mugs", (1.0, OY + 0.75, F + 0.99))
    for dy in (-0.25, 0.25):
        kit.cyl("mug", 0.06, 0.1, (0, dy, 0.05), M["mug"], mugs)
    groups["mugs"] = [mugs] + list(mugs.children)
    # my boots by the back door: laced tight, double knots, an apple leaf caught in one lace
    bt = kit.empty("boots", (-0.75, OY - 0.7, F))
    for i, bx in enumerate((-0.17, 0.17)):
        kit.box("bsole", (0.22, 0.46, 0.04), (bx, 0.0, 0.02), M["bootsole"], bt)
        kit.box("bshaft", (0.2, 0.2, 0.3), (bx, 0.1, 0.19), M["boot"], bt, bevel=0.02)
        kit.box("btoe", (0.2, 0.22, 0.13), (bx, -0.1, 0.105), M["boot"], bt, bevel=0.025)
        kit.box("blace", (0.15, 0.14, 0.015), (bx, -0.0, 0.2), M["lace"], bt, rot=(0.5, 0, 0))
        kit.box("blace", (0.15, 0.015, 0.14), (bx, 0.0, 0.26), M["lace"], bt)
        for kx in (-0.03, 0.03):
            kit.box("knot", (0.05, 0.05, 0.05), (bx + kx, -0.03, 0.31), M["lace"], bt, rot=(0.3, 0.4, 0.2))
    kit.box("blaceloop", (0.12, 0.012, 0.03), (-0.17, -0.06, 0.33), M["lace"], bt, rot=(0, 0, 0.5))
    kit.box("blaceloop", (0.12, 0.012, 0.03), (0.17, -0.06, 0.33), M["lace"], bt, rot=(0, 0, -0.5))
    kit.box("apple leaf", (0.16, 0.1, 0.012), (0.13, -0.09, 0.345), M["leafg"], bt, rot=(0.35, 0.2, 0.7))
    groups["boots"] = [bt] + list(bt.children)
    # falling leaves
    lv = kit.empty("leaves", (0, 0, -60))
    leaves = [kit.box("leaf", (0.12, 0.09, 0.012), (0, 0, 0), M["leaf"], lv) for _ in range(16)]
    ctx["leaves"] = (lv, leaves)
    for g in groups.values():
        for ob in g:
            ob.hide_render = True
    for ob in leaves:
        ob.hide_render = True


# ------------------------------------------------------------------------------------------------ prints
class Group:
    pass


def build_trails(kit, ctx, tl):
    """Make every print object up front (hidden), with its birth time and the group's window."""
    PRINT = {}
    ctx["trails"] = {}
    ons = [c for c in cues_of(tl, "trail")]
    offs = {}
    for c in cues_of(tl, "trail_off"):
        offs.setdefault(c["id"], []).append(c)
    strs = {}
    for c in cues_of(tl, "trail_str"):
        strs.setdefault(c["id"], []).append(c)

    def proto(w, l, h):
        key = (w, l, h)
        if key not in PRINT:
            vs = kit.box_verts(w, l, h, (0, 0, h / 2))
            me = bpy.data.meshes.new(f"print {key}")
            me.from_pydata(vs, [], kit.BOX_FACES)
            me.update()
            PRINT[key] = me
        return PRINT[key]

    for c in ons:
        tid = c["id"]
        g = Group()
        g.id, g.t_on, g.kind, g.rise = tid, c["t"], c["kind"], c.get("rise", 0.3)
        g.base = c.get("strength", 2.4) * 0.45
        g.str_cues = strs.get(tid, [])
        g.off = [o for o in offs.get(tid, []) if o["t"] >= c["t"]]
        g.off = g.off[0] if g.off else None
        glow = c["kind"] == "glow"
        sw, sl, sh = (0.2, 0.34, 0.008) if glow else (0.7, 0.7, 0.014)
        if c.get("size"):
            sw, sl = c["size"]
        mesh = proto(sw, sl, sh)
        gap, lat, every = c.get("gap", 0.62), c.get("lat", 0.16), c.get("every", 1)
        pts = []   # (x, y, rz, birth)
        if c.get("walker"):
            who = c["walker"]
            fs = [f for f in acting.footsteps(tl, who) if f["t"] >= c["t"] - 1e-6]
            fs = fs[::every]
            for i, f in enumerate(fs):
                st = acting.state(tl, who, f["t"] + 0.02)
                psi = st["yaw"]
                rx, ry = math.cos(psi), math.sin(psi)
                side = lat if i % 2 == 0 else -lat
                off = c.get("offset", [0, 0])
                pts.append((f["x"] + rx * side + off[0], f["y"] + ry * side + off[1], psi, f["t"] + 0.05))
        for ln in c.get("lines", []):
            d = 0.0
            for (ax, ay), (bx, by) in zip(ln, ln[1:]):
                seg = math.hypot(bx - ax, by - ay)
                if seg < 1e-6:
                    continue
                ux, uy = (bx - ax) / seg, (by - ay) / seg
                while d <= seg:
                    k = len(pts)
                    side = lat if k % 2 == 0 else -lat
                    pts.append((ax + ux * d - uy * side, ay + uy * d + ux * side, math.atan2(ux, -uy), c["t"]))
                    d += gap
                d -= seg
        base_col = c["color"]
        per = bool(c.get("per_print")) or bool(c.get("walker"))
        z0 = c.get("z", 0.0) + (0.003 if glow else 0.004)
        g.items = []
        g.mats = []
        if glow:
            shared = kit.emit(base_col, 1.0, name=f"print {tid}")
            shared_node = shared.node_tree.nodes["Emission"]
        else:
            shared = M_DARK[0]
        events = []
        if c.get("boost"):
            events = [f for f in acting.footsteps(tl, c["boost"]["who"])]
        for i, (x, y, rz, birth) in enumerate(pts):
            ob = bpy.data.objects.new(f"print {tid} {i}", mesh)
            bpy.context.scene.collection.objects.link(ob)
            ob.location = (x, y, z0)
            ob.rotation_euler = (0, 0, rz)
            ob.hide_render = True
            node = None
            if glow:
                if per:
                    m = kit.emit(base_col, 1.0, name=f"print {tid} {i}")
                    node = m.node_tree.nodes["Emission"]
                    _assign(ob, m)
                else:
                    _assign(ob, shared)
            else:
                _assign(ob, shared)
            ev = None
            if events:
                b = c["boost"]
                near = [f["t"] for f in events if math.hypot(f["x"] - x, f["y"] - y) <= b.get("radius", 0.5)]
                ev = min(near) if near else None
            g.items.append({"ob": ob, "birth": birth, "node": node, "ev": ev, "on": False})
        g.shared_node = shared_node if glow else None
        g.boost = c.get("boost")
        g.per = per
        g.glow = glow
        ctx["trails"][tid] = g


M_DARK = [None]


def _assign(ob, mat):
    """One slot on the shared mesh, linked to the object, so each print can have its own material."""
    if not ob.data.materials:
        ob.data.materials.append(None)
    ob.material_slots[0].link = "OBJECT"
    ob.material_slots[0].material = mat


def update_trails(ctx, t):
    for g in ctx["trails"].values():
        offg = 1.0
        if g.off and t >= g.off["t"]:
            offg = 1.0 - ss((t - g.off["t"]) / max(0.3, g.off.get("dur", 0.4)))
        gate = (ss((t - g.t_on) / max(0.3, g.rise)) if t >= g.t_on else 0.0) * offg
        s = ramp_val(g.str_cues, "value", t, g.base / 0.6) * 0.45
        if g.glow and not g.per:
            g.shared_node.inputs["Strength"].default_value = s * gate if g.shared_node else 0.0
        vis_group = gate > 0.002
        for it in g.items:
            if g.per or g.boost:
                f = ss((t - it["birth"]) / max(0.3, g.rise)) if t >= it["birth"] else 0.0
                f *= offg
                if g.per and g.glow:
                    mult = 1.0
                    if g.boost and it["ev"] is not None and t >= it["ev"]:
                        mult = 1.0 + (g.boost["factor"] - 1.0) * ss((t - it["ev"]) / max(0.3, g.boost["dur"]))
                    it["node"].inputs["Strength"].default_value = s * f * mult
                show = f > 0.002
            else:
                show = vis_group
            if show != it["on"]:
                it["on"] = show
                it["ob"].hide_render = not show


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    ctx = {"story": story, "kit": kit}
    M = mats(kit)
    M_DARK[0] = M["sqdark"]
    ctx["M"] = M
    build_orchard(kit, ctx, M)
    build_house(kit, ctx, M)
    build_town(kit, ctx, M)
    build_kitchen_town(kit, ctx, M)
    build_garden(kit, ctx, M)
    build_rough(kit, ctx, M)
    build_lights(kit, ctx)
    link_rough_lights(kit, ctx)
    build_extras(kit, ctx, M)
    build_trails(kit, ctx, tl)
    ctx["inited"] = False
    return ctx


def init_chars(kit, story, ctx):
    ctx["inited"] = True
    M = ctx["M"]
    # glowing soles on everyone, in their own colour
    for name, spec in story["cast"].items():
        g = spec.get("glow")
        if not g:
            continue
        sole = kit.emit(g, 4.5, name=f"sole {g}")
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{name}.leg{sx}")
            if leg:
                bw = float(spec.get("body_width", 1.0))
                kit.box(f"{name}.sole{sx}", (1.1 * bw, 1.16, 0.1), (0, 0.0, -2.0), sole, leg)
    # Nan's round wire glasses: thin silver rims over the eyes, no lenses
    hg = bpy.data.objects.get("nan.headg")
    if hg:
        R_ = 0.62
        for sx in (-1, 1):
            cx_, cz_ = sx * 0.25, 0.0
            kit.box("nan.rimt", (0.4, 0.03, 0.03), (cx_, -R_ - 0.04, cz_ + 0.2), M["wire"], hg)
            kit.box("nan.rimb", (0.4, 0.03, 0.03), (cx_, -R_ - 0.04, cz_ - 0.2), M["wire"], hg)
            for ex_ in (-0.2, 0.2):
                kit.box("nan.rims", (0.03, 0.03, 0.43), (cx_ + ex_, -R_ - 0.04, cz_), M["wire"], hg)
        kit.box("nan.rimbr", (0.1, 0.03, 0.03), (0, -R_ - 0.04, 0.12), M["wire"], hg)
    # my bag (shown by cue)
    torso = bpy.data.objects.get("me.torso")
    if torso:
        bag = kit.box("bag", (0.9, 0.55, 1.1), (-1.15, 0.5, 0.55), M["bag"], torso, bevel=0.08)
        strap = kit.box("strap", (0.18, 1.08, 0.1), (0.0, 0.0, 1.2), M["bag"], torso, rot=(0, 0.5, 0))
        ctx["groups"]["bag"] = [bag, strap]
        for ob in ctx["groups"]["bag"]:
            ob.hide_render = True
    # fog colours that follow the time of day
    ctx["fog_nodes"] = []
    fc = tuple(kit.FOG["color"])
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        for n in m.node_tree.nodes:
            if n.type == "EMISSION":
                c = tuple(n.inputs["Color"].default_value[:3])
                if all(abs(a - b) < 1e-5 for a, b in zip(c, fc)):
                    ctx["fog_nodes"].append(n)
    ctx["world_bg"] = bpy.context.scene.world.node_tree.nodes["Background"]


def dir_rot(d):
    return V(d).normalized().to_track_quat("-Z", "Y").to_euler()


def animate(kit, story, tl, t, ctx):
    if not ctx.get("inited"):
        init_chars(kit, story, ctx)
    sc = bpy.context.scene
    over = {}
    # --- time of day
    tc = last_cue(cues_of(tl, "tod"), t)
    tod = tc["set"] if tc else "dusk"
    scol, spow, sdir, wcol, wpow, fcol, expo = TOD[tod]
    L = kit.LIGHTS["sun"]
    L["light"].color = hexrgb(scol)
    L["obj"].rotation_euler = dir_rot(sdir)
    over["sun"] = spow
    ctx["world_bg"].inputs["Color"].default_value = (*lin(hexrgb(wcol)), 1)
    ctx["world_bg"].inputs["Strength"].default_value = wpow
    fl = (*lin(hexrgb(fcol)), 1)
    for n in ctx["fog_nodes"]:
        n.inputs["Color"].default_value = fl
    ec = last_cue(cues_of(tl, "expo"), t)
    sc.view_settings.exposure = expo + (ec["ev"] if ec else 0.0)
    lamps, kit_g, my_g, bed_g = ROOM[tod]
    for nm in ctx.get("lamp_names", []):
        over[nm] = lamps
    over["benchl"] = 1.0 if tod in ("night", "silver") else 0.0
    over["kitchen"], over["myroom"], over["bedroom"] = kit_g, my_g, bed_g
    over["tkit"] = 1.0
    # --- the pair light: a soft lantern glow that follows the two walkers (the sneaky pair, then Nan and me)
    pl = ramp_val(cues_of(tl, "pairlight"), "to", t, 0.0)
    over["pairl"] = pl
    if pl > 0:
        who = ("front", "follow") if t < 20 else ("me", "nan")
        pts = [acting.state(tl, w, t) for w in who]
        pts = [p_ for p_ in pts if p_ and not p_.get("hidden")]
        if pts:
            ax_ = sum(p_["x"] for p_ in pts) / len(pts)
            ay_ = sum(p_["y"] for p_ in pts) / len(pts)
            kit.LIGHTS["pairl"]["obj"].location = (ax_ - 0.9, ay_ - 0.8, 2.3)
    # --- cued ramps
    lamp = ramp_val(cues_of(tl, "lamp"), "to", t, 1.0)
    over["porch"] = lamp
    ctx["lamp_mat"].node_tree.nodes["Emission"].inputs["Strength"].default_value = 2.2 * lamp
    over["daywin"] = ramp_val(cues_of(tl, "daywin"), "to", t, 0.0)
    over["fridge"] = ramp_val([{**c, "to": c["on"]} for c in cues_of(tl, "fridge")], "to", t, 0.0)
    blind = ramp_val(cues_of(tl, "blind"), "to", t, 0.0)
    top = geo.WIN_Z1 - 0.1
    hgt = 0.12 + (geo.WIN_Z1 - geo.WIN_Z0 - 0.12) * (1.0 - blind)
    ctx["blind"].scale = (1, 1, hgt)
    ctx["blind"].location.z = top - hgt / 2
    door = ramp_val(cues_of(tl, "door"), "to", t, 0.0)
    ctx["door"].rotation_euler = (0, 0, 1.75 * door)
    # --- prop groups
    for g in ("keys", "basket", "ladder", "mugs", "bag", "boots"):
        vis = False
        for c in cues_of(tl, "vis"):
            if c["t"] <= t + 1e-9:
                if g in c.get("show", []):
                    vis = True
                if g in c.get("hide", []):
                    vis = False
        if g == "bag":
            mk = None
            for kk in tl["acting"].get("me", []):
                if kk["t"] <= t + 1e-9:
                    mk = kk
            if mk is None or mk.get("hidden"):
                vis = False
        for ob in ctx["groups"].get(g, []):
            ob.hide_render = not vis
    # --- the Rough One
    rc = last_cue(cues_of(tl, "rough"), t)
    on = bool(rc and rc["on"])
    root = ctx["rough"]
    for ob in ctx["rough_parts"]:
        ob.hide_render = not on
    sil = bool(on and rc.get("sil"))
    for ob in ctx["rough_parts"]:
        if ob.type != "MESH":
            continue
        if "orig_mat" not in ob:
            ob["orig_mat"] = ob.material_slots[0].material.name
        om = bpy.data.materials[ob["orig_mat"]]
        ob.material_slots[0].material = ctx["M"]["rsil"] if (sil and om not in (ctx["M"]["glint"], ctx["M"]["cutblack"])) else om
    if on:
        root.location = (rc["pos"][0], rc["pos"][1], 0.0)
        root.rotation_euler = (0, 0, math.radians(rc.get("yaw", 0)))
    rk = (RLIGHT[tod] * rc.get("lights", 1.0)) if on else 0.0
    px, py = (rc["pos"][0], rc["pos"][1]) if on else (0, -400)
    yawr = math.radians(rc.get("yaw", 0)) if on else 0
    # key: low and to its side, rim: cool, high and behind
    fx_, fy_ = math.sin(yawr), -math.cos(yawr)
    kit.LIGHTS["rkey"]["obj"].location = (px + 1.5 * math.cos(yawr) + fx_ * 0.9, py + 1.5 * math.sin(yawr) + fy_ * 0.9, 0.9)
    kit.LIGHTS["rrim"]["obj"].location = (px - 1.3 * math.cos(yawr) - fx_ * 1.5, py - 1.3 * math.sin(yawr) - fy_ * 1.5, 3.0)
    over["rkey"] = rk * rc.get("key", 1.0) if on else 0.0
    over["rrim"] = rk * rc.get("rim", 1.0) if on else 0.0
    # --- falling leaves
    lv, leaves = ctx["leaves"]
    lc = last_cue(cues_of(tl, "leaves"), t)
    lon = bool(lc and lc.get("on"))
    for i, ob in enumerate(leaves):
        ob.hide_render = not lon
        if lon:
            cx, cy = lc["at_xy"]
            ph = (t * 0.35 + i * 0.173) % 1.0
            ob.location = (cx + 1.8 * math.sin(i * 1.7 + t * 0.7) + (i % 3 - 1) * 0.8, cy + 1.4 * math.cos(i * 2.3 + t * 0.5) - 0.5,
                           3.2 - 3.1 * ph)
            ob.rotation_euler = (t * 1.3 + i, t * 0.9 + i * 2, i)
    # --- sitting (R6 on the bench)
    for name, keys in tl["acting"].items():
        k = None
        for kk in keys:
            if kk["t"] <= t + 1e-9:
                k = kk
        root_ob = bpy.data.objects.get(name)
        if not root_ob:
            continue
        if k and k.get("sit") and not k.get("hidden", False):
            for sx in (-1, 1):
                bpy.data.objects[f"{name}.leg{sx}"].rotation_euler = (-0.55, 0, 0)
                bpy.data.objects[f"{name}.arm{sx}"].rotation_euler = (-0.5, 0, 0)
            root_ob.location.z = root_ob.location.z + 0.53 - 2.0 * root_ob.scale[2]
    # --- the prints
    update_trails(ctx, t)
    return over
