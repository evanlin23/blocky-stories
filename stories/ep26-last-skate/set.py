"""ep26 "last-skate": the set. An old roller rink on its last night.

Metres, z up, a character with yaw 0 faces -y (yaw 90 faces +x). The hall runs x -8 .. 8, y -9 .. 6.4, ceiling 5.2.
  - the maple floor is x +-7, y +-4.4. A waist-high cherry rail rings it on y = +-4.15 and x = +-7.15, cream posts
    every 1.2 m from x = 0 (the south rail has a gap between the posts at x = -1.2 and 1.2).
  - the south concourse (y -9 .. -4.4): the snack bar on the west (stools at x -5.0 and -3.8, ledge, amber lamp),
    the hire counter on the east (x 2.4 .. 6.8, cubby wall behind it), the hire-counter door in the south wall at x 0,
    the entrance on the west wall (y -8 .. -6).
  - the DJ booth on the north wall (Lenny at 0, 5.5, floor of the booth z 1.7).
  - Nan waits at the south rail at x 3.0; the Skater stands at the rail at x 1.65 or in the middle, or far rail.

Cues set.py reads (all go through `tl["cues"]`, resolved to "t"):
  dim      {"level", "dur"}                 the room's lights, a slow ramp from this cue's time
  spot     {"to": [x, y], "gain", "size", "dur"}   the spotlight: where, how bright, the cone (deg), a slow ramp
  skater   {"pos", "yaw", "pose", "head": [yaw, pitch] relative | "look": [x, y], "hidden", "dur"}
  skates   {"who", "on"}                    roller skates on a character
  door     {"open", "dur"}                  the hire-counter door
  steam    {"on"}                           the chips' steam
Acting keys read here (acting.py ignores them): "sit": true, "skate": true, "wobble": degrees.
"""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector
from PIL import Image, ImageDraw, ImageFilter

from blocky import faces, rig

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

CHERRY, CREAM, PINK = "#a8242d", "#e9dcc2", "#d9a0a2"
HALL = (-8.0, 8.0, -9.0, 6.4)
CEIL = 5.2
RAIL_Y = (-4.15, 4.15)
POSTS = 1.2
SEAT_Z = 0.7
STOOL_Y, LEDGE_Y, LEDGE_Z = -6.7, -5.98, 1.12
STOOLS = {"me": -5.0, "pop": -3.8}

# ---- the Skater's body (metres)
LEG = (0.46, 0.46, 0.46)
UPPER, FORE, FORE2 = 0.42, 0.40, 0.34
BOOT_H = 0.28
TORSO = (0.64, 0.34, 0.72)
POSES = {   # absolute angles in degrees: dir = (0, sin a, -cos a), front is -y
    "rest": {"leg": (-55, 62, -58), "arm": (8, 172, 8), "dx": 0.17},
    "reach": {"leg": (-55, 62, -58), "arm": (8, 172, 8), "dx": 0.17, "reach": (-75, -10, -95)},
}


# ------------------------------------------------------------------------------------------ small helpers


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def _switch(keys, attr, t, default):
    v = default
    for k in keys:
        if attr in k and k["t"] <= t + 1e-9:
            v = k[attr]
    return v


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


def _ramp(cues, t, initial, fields):
    """Fold ramping cues: each starts at its t and eases over its dur from where the state was."""
    cur = dict(initial)
    for c in sorted(cues, key=lambda c: c["t"]):
        if t < c["t"]:
            break
        u = _ss((t - c["t"]) / max(float(c.get("dur", 0.0)), 1e-6))
        for f in fields:
            if f not in c:
                continue
            a, b = cur[f], c[f]
            cur[f] = [x + (y - x) * u for x, y in zip(a, b)] if isinstance(a, (list, tuple)) else a + (b - a) * u
        if u < 1:
            break
    return cur


def wbox(kit, name, x0, x1, y0, y1, z0, z1, mat, parent=None):
    return kit.box(name, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), mat, parent)


def wstripes(kit, name, c1, c2, scale, rough=0.75):
    """Bands in world height (so every wall piece lines up): c1 for the first half of each period, then c2."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(c1)
    b.inputs["Roughness"].default_value = rough
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = scale
    nt.links.new(sep.outputs["Z"], mul.inputs[0])
    fr = nt.nodes.new("ShaderNodeMath")
    fr.operation = "FRACT"
    nt.links.new(mul.outputs[0], fr.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = kit.col(c1)
    ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements[1].color = kit.col(c2)
    nt.links.new(fr.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m


def ostripes(kit, name, c1, c2, scale, rough=0.7):
    """Bands in the object's own height (the Skater's limbs and body wear them as rings)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(c1)
    b.inputs["Roughness"].default_value = rough
    rig._stripes(m, c1, c2, scale)
    kit._fogged(m, b.outputs[0])
    return m


def ghost(name, alpha, hexc="#ffffff"):
    """A faint see-through white, for steam."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    df = nt.nodes.new("ShaderNodeEmission")
    df.inputs["Color"].default_value = (0.9, 0.9, 0.9, 1)
    df.inputs["Strength"].default_value = 0.5
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = alpha
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(df.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    return m, mix


def link_only(kit, coll, light_name, objs, mode):
    """Light linking: mode "only" = this light lights only objs; "except" = everything but objs."""
    col = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    if mode == "except":
        for co in col.collection_objects:
            co.light_linking.link_state = "EXCLUDE"
    else:
        for co in col.collection_objects:
            co.light_linking.link_state = "INCLUDE"
    kit.LIGHTS[light_name]["obj"].light_linking.receiver_collection = col


# ------------------------------------------------------------------------------------------ the hall


def build_hall(kit, ctx):
    x0, x1, y0, y1 = HALL
    stripe = wstripes(kit, "wall stripes", "#9f2a31", "#e3d6bb", 1.0)
    stripe2 = wstripes(kit, "wall stripes out", "#8f2830", "#d9cdb4", 1.0)
    # floors
    kit.box("rink floor", (14.0, 8.8, 0.1), (0, 0, -0.05), kit.planks("#d4a05c", "#bd8446", 1.0, "X", rough=0.55))
    kit.box("concourse", (16.0, 4.6, 0.1), (0, -6.7, -0.05), kit.checker("#6c2128", "#cdbf9f", 1.4, rough=0.45))
    kit.box("north strip", (16.0, 1.9, 0.1), (0, 5.45, -0.05), kit.planks("#a97b44", "#8f6535", 1.0, "X"))
    kit.box("floor w", (1.0, 8.8, 0.1), (-7.5, 0, -0.05), kit.planks("#a97b44", "#8f6535", 1.0, "Y"))
    kit.box("floor e", (1.0, 8.8, 0.1), (7.5, 0, -0.05), kit.planks("#a97b44", "#8f6535", 1.0, "Y"))
    # walls: x -8 (west, with the entrance y -8 .. -6), x 8, y 6.5 (north), y -9.1 (south, with the door x -0.6 .. 0.6)
    H = CEIL
    wbox(kit, "w west a", -8.2, -8.0, y0, -8.0, 0, H, stripe)
    wbox(kit, "w west b", -8.2, -8.0, -6.0, y1 + 0.1, 0, H, stripe)
    wbox(kit, "w west lintel", -8.2, -8.0, -8.0, -6.0, 2.3, H, stripe)
    wbox(kit, "w east", 8.0, 8.2, y0, y1 + 0.1, 0, H, stripe)
    wbox(kit, "w north", -8.2, 8.2, y1, y1 + 0.2, 0, H, stripe)
    wbox(kit, "w south a", -8.2, -0.6, -9.3, -9.1, 0, H, stripe)
    wbox(kit, "w south b", 0.6, 8.2, -9.3, -9.1, 0, H, stripe)
    wbox(kit, "w south lintel", -0.6, 0.6, -9.3, -9.1, 2.1, H, stripe)
    # the exterior: facade stripes, ground, a car park, a lamp
    wbox(kit, "facade a", -9.0, -8.2, -12.0, -8.0, 0, 5.0, stripe2)
    wbox(kit, "facade b", -9.0, -8.2, -6.0, 8.0, 0, 5.0, stripe2)
    wbox(kit, "facade lintel", -9.0, -8.2, -8.0, -6.0, 2.3, 5.0, stripe2)
    kit.box("ground", (70, 60, 0.1), (-43, -6, -0.06), kit.concrete("#3a3c40", 2.0, 0.6))
    kit.box("kerb", (1.0, 22, 0.14), (-9.6, -2, 0.0), kit.concrete("#6f6d68", 2.0, 0.4))
    for i, (cx, cy, cc) in enumerate([(-17, -2.5, "#2f5d6e"), (-17, -10.5, "#7a3a3a"), (-23, -6.8, "#b9b1a0")]):
        body = kit.plastic(cc, 0.35)
        kit.box(f"car{i}", (1.9, 4.3, 0.75), (cx, cy, 0.62), body, bevel=0.12)
        kit.box(f"cab{i}", (1.6, 2.2, 0.62), (cx, cy - 0.15, 1.28), kit.glass("#a6bcc4"), bevel=0.1)
        for sx in (-0.9, 0.9):
            for sy in (-1.35, 1.35):
                kit.cyl(f"wheel{i}{sx}{sy}", 0.33, 0.22, (cx + sx, cy + sy, 0.33), kit.plastic("#16171a", 0.8), rot=(0, math.pi / 2, 0))
    for k, py in enumerate((-13.5, -2.0, 7.0)):
        kit.cyl(f"pole{k}", 0.08, 5.5, (-14.0, py, 2.75), kit.metal("#4a4d52"))
        kit.sphere(f"lampg{k}", 0.22, (-14.0, py, 5.5), kit.emit("#ffc890", 6.0))
    kit.light("lot", "POINT", (-14.0, -2.0, 5.3), 900, "#ffc58a", size=0.3)
    kit.light("lot2", "POINT", (-14.0, -13.5, 5.3), 900, "#ffc58a", size=0.3)
    # ceiling and its beams (hidden in the overhead shots)
    ctx["ceiling"] = [kit.box("ceiling", (16.4, 15.8, 0.2), (0, -1.3, CEIL + 0.1), kit.plastic("#3a2a2c", 0.9))]
    for i, bx in enumerate(range(-6, 7, 3)):
        ctx["ceiling"].append(kit.box(f"beam{i}", (0.3, 15.6, 0.3), (bx, -1.3, CEIL - 0.15), kit.plastic("#5b2b2f", 0.8)))
    # the three slow fans (blades turn in animate; they cast no shadow so the pool never flickers)
    ctx["fans"] = []
    fanm = kit.plastic("#d8ccb2", 0.5)
    for i, fx in enumerate((-5.0, 0.0, 5.0)):
        hub = kit.empty(f"fan{i}", (fx, 2.7, 4.4))
        kit.cyl(f"fanrod{i}", 0.03, 0.8, (0, 0, 0.4), kit.metal("#7a7d82"), hub)
        kit.cyl(f"fanhub{i}", 0.16, 0.14, (0, 0, 0), fanm, hub)
        for k in range(4):
            arm = kit.empty(f"fanarm{i}{k}", (0, 0, 0), hub, rot=(0, 0, k * math.pi / 2))
            b = kit.box(f"fanblade{i}{k}", (0.24, 0.8, 0.025), (0, 0.6, 0), fanm, arm, rot=(0, 0.08, 0))
            b.visible_shadow = False
        ctx["fans"].append(hub)


def build_rail(kit, ctx):
    cherry = kit.plastic("#a3232b", 0.4)
    padm = kit.plastic("#8f1c25", 0.7)
    cream = kit.plastic("#eadfc6", 0.45)
    kit.cyl  # (kept for clarity)
    runs = []   # (axis, fixed, a, b)
    for y in RAIL_Y:
        runs.append(("x", y, -7.2, 7.2))
    for x in (-7.15, 7.15):
        runs.append(("y", x, -4.15, 4.15))
    for axis, fixed, a, b in runs:
        if axis == "x" and fixed < 0:
            pieces = [(-7.2, -1.2), (1.2, 7.2)]     # the gap between the posts at x -1.2 and 1.2
        else:
            pieces = [(a, b)]
        for k, (p0, p1) in enumerate(pieces):
            ln = p1 - p0
            mid = (p0 + p1) / 2
            if axis == "x":
                kit.box(f"railcap{fixed}{k}", (ln, 0.24, 0.13), (mid, fixed, 1.0), cherry, bevel=0.05)
                kit.box(f"railpad{fixed}{k}", (ln, 0.16, 0.2), (mid, fixed, 0.85), padm, bevel=0.04)
                kit.box(f"railkick{fixed}{k}", (ln, 0.06, 0.07), (mid, fixed, 0.3), cream, bevel=0.02)
            else:
                kit.box(f"railcap{fixed}{k}", (0.24, ln, 0.13), (fixed, mid, 1.0), cherry, bevel=0.05)
                kit.box(f"railpad{fixed}{k}", (0.16, ln, 0.2), (fixed, mid, 0.85), padm, bevel=0.04)
                kit.box(f"railkick{fixed}{k}", (0.06, ln, 0.07), (fixed, mid, 0.3), cream, bevel=0.02)
    for i in range(-6, 7):
        x = i * POSTS
        for y in RAIL_Y:
            if y < 0 and -1.2 < x < 1.2:
                continue
            kit.box(f"post{i}{y}", (0.1, 0.1, 1.0), (x, y, 0.5), cream, bevel=0.02)
    for j in range(-3, 4):
        y = j * POSTS
        for x in (-7.15, 7.15):
            kit.box(f"postv{j}{x}", (0.1, 0.1, 1.0), (x, y, 0.5), cream, bevel=0.02)


def build_snack(kit, ctx):
    cream = kit.plastic("#e8dcc2", 0.5)
    cherry = kit.plastic("#a3232b", 0.5)
    chrome = kit.metal("#b9bcc0", 0.25)
    wood = kit.planks("#5d3b25", "#4a2e1d", 1.0, "X")
    # the bar along the south wall, and its back shelf
    kit.box("snack counter", (4.6, 0.8, 1.04), (-4.3, -8.45, 0.52), cream, bevel=0.03)
    kit.box("snack top", (4.8, 0.95, 0.06), (-4.3, -8.42, 1.07), chrome)
    kit.box("snack kick", (4.6, 0.82, 0.18), (-4.3, -8.45, 0.09), cherry)
    kit.box("snack back", (4.8, 0.12, 1.5), (-4.3, -9.0, 1.9), wood)
    for i in range(6):   # jars and cups on the shelf, plain
        kit.cyl(f"jar{i}", 0.09, 0.22, (-6.3 + i * 0.75, -8.9, 1.28), kit.glass("#cfe0e6") if i % 2 else cream, n=14)
    kit.cyl("urn", 0.2, 0.5, (-2.6, -8.7, 1.4), chrome)
    # the ledge people lean on, facing the rink, and its legs
    kit.box("ledge", (3.6, 0.44, 0.06), (-4.5, LEDGE_Y, LEDGE_Z), wood)
    for lx in (-6.1, -2.9):
        kit.box(f"ledgeleg{lx}", (0.06, 0.06, LEDGE_Z), (lx, LEDGE_Y + 0.15, LEDGE_Z / 2), chrome)
    # stools
    for i, sx in enumerate((-6.2, -5.0, -3.8, -2.7)):
        kit.cyl(f"stoolpole{i}", 0.03, SEAT_Z - 0.05, (sx, STOOL_Y, (SEAT_Z - 0.05) / 2), chrome, n=10)
        kit.cyl(f"stoolbase{i}", 0.18, 0.03, (sx, STOOL_Y, 0.015), chrome, n=18)
        kit.cyl(f"stoolseat{i}", 0.2, 0.09, (sx, STOOL_Y, SEAT_Z - 0.045), cherry, n=22)
    # the amber lamp over Pop's stool
    kit.cyl("lampcord", 0.01, 1.0, (STOOLS["pop"], STOOL_Y, 2.85), kit.metal("#222222"))
    kit.cyl("lampshade", 0.05, 0.22, (STOOLS["pop"], STOOL_Y, 2.25), kit.emit("#ffb050", 5.0), n=18, r2=0.24)
    kit.sphere("lampbulb", 0.07, (STOOLS["pop"], STOOL_Y, 2.12), kit.emit("#ffd9a0", 14.0))
    # the chips: a tub on the ledge, between the stools
    tub = kit.cyl("tub", 0.1, 0.22, (-4.4, LEDGE_Y, LEDGE_Z + 0.14), cream, n=20, r2=0.125)
    kit.cyl("tubband", 0.112, 0.06, (-4.4, LEDGE_Y, LEDGE_Z + 0.14), cherry, n=20, r2=0.118)
    for i in range(14):
        a = i * 2.4
        kit.box(f"chip{i}", (0.03, 0.03, 0.09), (-4.4 + 0.05 * math.cos(a) * (0.4 + (i % 4) * 0.2), LEDGE_Y + 0.05 * math.sin(a) * (0.4 + (i % 3) * 0.3), LEDGE_Z + 0.27 + (i % 3) * 0.02),
                kit.plastic("#e8b43c", 0.6), rot=(0.3 * (i % 3), 0.5 * (i % 4), a))
    ctx["steam"] = []
    for i in range(3):
        m, mix = ghost(f"steam{i}", 0.0)
        s = kit.sphere(f"steam{i}", 0.045, (-4.4 + 0.02 * (i - 1), LEDGE_Y, LEDGE_Z + 0.35), m, seg=20)
        s.scale = (1.0, 1.0, 2.6)
        ctx["steam"].append((s, mix, i))
    # lights
    kit.light("amber", "POINT", (STOOLS["pop"], STOOL_Y, 2.0), 170, "#ffa845", size=0.1)


def build_hire(kit, ctx):
    cream = kit.plastic("#e8dcc2", 0.5)
    cherry = kit.plastic("#a3232b", 0.45)
    wood = kit.plastic("#6a4529", 0.7)
    dark = kit.plastic("#3b2617", 0.8)
    kit.box("hire counter", (4.6, 0.8, 1.04), (4.6, -7.55, 0.52), cream, bevel=0.03)
    kit.box("hire top", (4.8, 0.95, 0.06), (4.6, -7.55, 1.07), kit.planks("#9a6a38", "#80552b", 1.0, "X"))
    kit.box("hire kick", (4.6, 0.82, 0.18), (4.6, -7.55, 0.09), cherry)
    kit.box("hire back", (4.6, 0.06, 2.2), (4.6, -8.97, 2.2), dark)
    cols, rows = 8, 4
    x0, x1, z0 = 2.3, 6.9, 1.12
    cw, ch = (x1 - x0) / cols, 0.5
    for c in range(cols + 1):
        kit.box(f"cubv{c}", (0.035, 0.5, rows * ch), (x0 + c * cw, -8.72, z0 + rows * ch / 2), wood)
    for r in range(rows + 1):
        kit.box(f"cubh{r}", (x1 - x0, 0.5, 0.035), ((x0 + x1) / 2, -8.72, z0 + r * ch), wood)
    boot = kit.plastic("#e5d9bf", 0.5)
    wheel = kit.plastic("#a3232b", 0.5)
    for r in range(rows):
        for c in range(cols):
            if r == 0 and c == cols - 1:
                continue    # the end cubby of the bottom row is the odd one, built below
            cx = x0 + (c + 0.5) * cw
            zb = z0 + r * ch
            for sx in (-1, 1):
                kit.box(f"sk{r}{c}{sx}", (0.15, 0.33, 0.17), (cx + sx * 0.12, -8.78, zb + 0.15), boot, bevel=0.03)
                kit.box(f"skw{r}{c}{sx}", (0.13, 0.26, 0.06), (cx + sx * 0.12, -8.78, zb + 0.045), wheel)
    # the odd pair: far too long, cherry red, laces still tied in their factory bows, a tally pressed in the near heel
    cx = x0 + (cols - 0.5) * cw
    leather = "#a3232b"
    for k, sx in enumerate((-1, 1)):
        bx = cx + sx * 0.12
        kit.box(f"long{k}", (0.15, 0.95, 0.19), (bx, -8.5, z0 + 0.15), kit.plastic(leather, 0.55), bevel=0.03)
        kit.box(f"longw{k}", (0.12, 0.8, 0.05), (bx, -8.5, z0 + 0.04), kit.plastic("#2a1416", 0.6))
        kit.box(f"longcuff{k}", (0.15, 0.2, 0.18), (bx, -8.18, z0 + 0.3), kit.plastic(leather, 0.55), bevel=0.03)
        for j in range(3):   # the laces, tied in bows
            lz = z0 + 0.26
            ly = -8.72 - j * 0.13
            kit.box(f"lace{k}{j}", (0.1, 0.012, 0.012), (bx, ly, lz), kit.plastic("#efe6d0", 0.8))
            for sl in (-1, 1):
                kit.box(f"bow{k}{j}{sl}", (0.045, 0.02, 0.03), (bx + sl * 0.045, ly, lz + 0.012), kit.plastic("#efe6d0", 0.8),
                        rot=(0, 0.5 * sl, 0))
    heel_y = -8.5 + 0.475
    ink = kit.plastic("#5a0f15", 0.7)
    for sx in (-1, 1):   # a plain tally of two upright strokes, one per partner
        kit.box(f"tally{sx}", (0.016, 0.006, 0.085), (cx - 0.12 + sx * 0.026, heel_y + 0.001, z0 + 0.17), ink)
    # the neon-style tube over the counter: steady, soft
    kit.box("tube", (2.6, 0.06, 0.06), (4.6, -8.8, 3.55), kit.emit("#ff7080", 3.0))
    kit.light("tube", "AREA", (4.6, -8.3, 3.4), 90, "#ff6a78", size=1.5)
    kit.light("hirefill", "AREA", (4.6, -6.5, 3.3), 300, "#ffd9a8", size=1.8)
    # the door by the counter, a closet of warm light behind it
    dm = kit.plastic("#8f2830", 0.5)
    kit.box("closet", (3.0, 1.6, 2.6), (0, -10.1, 1.3), kit.plastic("#d8c7a4", 0.9))
    kit.box("closet floor", (3.0, 1.6, 0.05), (0, -10.1, 0.0), kit.planks("#a97b44", "#8f6535", 1.0, "X"))
    kit.box("closet bulb", (0.3, 0.3, 0.06), (0, -10.1, 2.58), kit.emit("#ffe0b0", 9.0))
    kit.light("closet", "POINT", (0, -9.9, 2.2), 260, "#ffdba8", size=0.2)
    hinge = kit.empty("doorhinge", (-0.58, -9.12, 0))
    kit.box("door", (1.16, 0.05, 2.08), (0.58, 0, 1.04), dm, hinge, bevel=0.01)
    ctx["door"] = hinge


def build_booth(kit, ctx):
    cream = kit.plastic("#e8dcc2", 0.5)
    stripe = wstripes(kit, "wall stripes", "#9f2a31", "#e3d6bb", 1.0)
    dark = kit.plastic("#1b1618", 0.4)
    kit.box("booth deck", (4.4, 2.0, 1.7), (0, 5.4, 0.85), stripe)
    kit.box("booth floor", (4.2, 1.8, 0.04), (0, 5.4, 1.72), kit.planks("#8f6535", "#7a552b", 1.0, "X"))
    kit.box("booth front", (4.4, 0.12, 0.9), (0, 4.5, 2.2), cream, bevel=0.02)
    kit.box("booth ledge", (4.6, 0.4, 0.07), (0, 4.58, 2.67), kit.plastic("#a3232b", 0.4))
    for sx in (-1.0, 1.0):
        kit.box(f"deck{sx}", (0.8, 0.34, 0.07), (sx, 4.58, 2.74), dark)
        kit.cyl(f"platter{sx}", 0.14, 0.02, (sx, 4.58, 2.78), kit.plastic("#2a2a30", 0.3))
    kit.box("booth roof", (4.8, 2.2, 0.12), (0, 5.4, 4.0), kit.plastic("#3a2a2c", 0.8))
    for sx in (-2.3, 2.3):
        kit.box(f"boothpost{sx}", (0.1, 0.1, 2.3), (sx, 4.5, 2.85), cream)
    kit.cyl("micpole", 0.012, 0.5, (0.25, 4.85, 2.95), kit.metal("#333333"))
    kit.sphere("micball", 0.045, (0.25, 4.85, 3.22), dark)
    kit.sphere("boothbulb", 0.08, (0.5, 5.0, 3.55), kit.emit("#ffd9a0", 14.0))
    kit.light("booth", "POINT", (0.5, 5.0, 3.4), 160, "#ffbf70", size=0.15)


def build_lights(kit, ctx):
    for i, hx in enumerate((-4.5, 0.0, 4.5)):
        kit.light(f"house{i}", "AREA", (hx, 0.4, 4.9), 720, "#ffd7a3", rot=(0, 0, 0), size=3.2)
    for i, cx in enumerate((-3.0, 3.5)):
        kit.light(f"conc{i}", "AREA", (cx, -6.6, 4.8), 520, "#ffd7a3", size=2.6)
    kit.aim(kit.light("flood", "SPOT", (-17.0, -3.0, 4.6), 2600, "#9fd3da", size=0.6, spot=75, blend=0.8), (-8.4, -6.0, 1.4))
    kit.light("dusk", "SUN", (0, 0, 10), 2.2, "#6fb0b8", rot=(math.radians(60), 0, math.radians(-70)))
    kit.light("spot", "SPOT", (0, 0, 4.7), 2300, "#fff0dc", rot=(0, 0, 0), size=0.4, spot=40, blend=1.0)
    for n in ("house0", "house1", "house2", "conc0", "conc1"):
        pass


# ------------------------------------------------------------------------------------------ the Skater


def skater_face(path: Path):
    W, H = faces.TEX_W, faces.TEX_H
    cream = (233, 223, 201)
    im = Image.new("RGB", (W, H), cream)
    d = ImageDraw.Draw(im)
    cx = W // 2
    # a smooth, very slightly paler oval plate: no nose, no brows, no mouth but the painted smile
    d.ellipse([cx - 250, int(H * 0.06), cx + 250, int(H * 0.96)], fill=(241, 233, 213))
    im = im.filter(ImageFilter.GaussianBlur(5))
    d = ImageDraw.Draw(im)
    ink = (22, 16, 15)
    ey = int(H * 0.40)
    for sx in (-1, 1):
        ex = cx + sx * 92
        d.ellipse([ex - 44, ey - 88, ex + 44, ey + 88], fill=ink)
        d.ellipse([ex - 20 + sx * 4, ey - 62, ex + 4 + sx * 4, ey - 38], fill=(255, 255, 255))
    my = int(H * 0.72)
    pts = [(cx + (i / 24 - 0.5) * 460, my + 70 * math.cos((i / 24 - 0.5) * math.pi) - 46) for i in range(25)]
    d.line(pts, fill=ink, width=9, joint="curve")
    im.save(path)
    return im


def build_skater(kit, ctx):
    wd = ROOT / "out" / "work" / "ep26-last-skate" / "faces"
    wd.mkdir(parents=True, exist_ok=True)
    skin = kit.plastic("#e9dfc9", 0.55)
    glove = kit.plastic("#f3ead6", 0.5)
    joint = kit.plastic("#33262a", 0.5)
    sm = ostripes(kit, "skater stripes", "#c58f96", "#e9dcc2", 5.0)
    sm2 = ostripes(kit, "skater stripes b", "#c9929a", "#ebe0c8", 6.0)
    skate = kit.plastic("#eadfc7", 0.45)
    wheel = kit.plastic("#b84a52", 0.5)
    objs = []
    root = kit.empty("skater", (0, 0, 0))
    ctx["sk"] = {"root": root, "objs": objs}
    ctx["sk"]["body"] = body = kit.empty("sk.body", (0, 0, 1.0), root)

    def add(o):
        objs.append(o)
        return o

    legs = {}
    for sx in (-1, 1):
        j = kit.empty(f"sk.hip{sx}", (sx * 0.19, 0, 0), body)
        chain = [j]
        parent = j
        for k, L in enumerate(LEG):
            seg = add(kit.box(f"sk.leg{sx}{k}", (0.22, 0.22, L), (0, 0, -L / 2), sm if k != 1 else sm2, parent, bevel=0.025))
            kn = kit.empty(f"sk.knee{sx}{k}", (0, 0, -L), parent)
            if k < 2:
                add(kit.box(f"sk.kneeb{sx}{k}", (0.27, 0.27, 0.2), (0, 0, -L), joint, parent, bevel=0.03))
            chain.append(kn)
            parent = kn
        # the skate on the last end
        add(kit.box(f"sk.boot{sx}", (0.2, 0.42, 0.18), (0, -0.09, -0.06), skate, parent, bevel=0.04))
        add(kit.box(f"sk.plate{sx}", (0.17, 0.4, 0.04), (0, -0.07, -0.18), joint, parent))
        for wy in (-0.24, -0.1, 0.04, 0.16):
            add(kit.cyl(f"sk.wh{sx}{wy}", 0.05, 0.07, (0, wy - 0.02, -0.23), wheel, parent, rot=(0, math.pi / 2, 0), n=14))
        legs[sx] = chain
    ctx["sk"]["legs"] = legs
    ctx["sk"]["torso"] = torso = kit.empty("sk.torso", (0, 0, 0), body)
    add(kit.box("sk.torsob", TORSO, (0, 0, TORSO[2] / 2), sm, torso, bevel=0.05))
    add(kit.box("sk.collar", (0.44, 0.3, 0.1), (0, 0, TORSO[2] + 0.02), joint, torso, bevel=0.03))
    arms = {}
    for sx in (-1, 1):
        j = kit.empty(f"sk.sh{sx}", (sx * 0.41, 0, TORSO[2] - 0.08), torso)
        add(kit.box(f"sk.shb{sx}", (0.27, 0.27, 0.27), (0, 0, 0), joint, j, bevel=0.03))
        chain = [j]
        parent = j
        for k, L in enumerate((UPPER, FORE, FORE2)):
            add(kit.box(f"sk.arm{sx}{k}", (0.2, 0.2, L), (0, 0, -L / 2), sm2 if k != 1 else sm, parent, bevel=0.02))
            nx = kit.empty(f"sk.el{sx}{k}", (0, 0, -L), parent)
            if k < 2:
                add(kit.box(f"sk.elb{sx}{k}", (0.23, 0.23, 0.17), (0, 0, -L), joint, parent, bevel=0.03))
            chain.append(nx)
            parent = nx
        add(kit.box(f"sk.hand{sx}", (0.15, 0.1, 0.2), (0, 0, -0.1), glove, parent, bevel=0.03))
        add(kit.box(f"sk.thumb{sx}", (0.04, 0.05, 0.1), (-sx * 0.085, -0.02, -0.07), glove, parent, bevel=0.015))
        arms[sx] = chain
    ctx["sk"]["arms"] = arms
    neck = kit.empty("sk.neck", (0, 0, TORSO[2] + 0.05), torso)
    add(kit.box("sk.neckb", (0.14, 0.14, 0.16), (0, 0, 0.06), joint, neck))
    headp = kit.empty("sk.head", (0, 0, 0.12), neck)
    hs = (0.40, 0.40, 0.46)       # a tall, narrow oval: R 0.22 m, H 0.48 m
    headg = kit.empty("sk.headg", (0, 0, 0.01), headp)
    headg.scale = hs
    hm, tex = rig.head_material("skater", "#e9dfc9")
    skater_face(wd / "skater-face.png")
    img = bpy.data.images.load(str(wd / "skater-face.png"))
    img.colorspace_settings.name = "sRGB"
    tex.image = img
    inner = kit.empty("sk.headinner", (0, 0, faces.HEAD_H / 2), headg)
    add(rig.head_mesh("sk.headm", hm, inner))
    ctx["sk"]["head"] = headp
    # the eye highlights: two tiny emissive points, the brightest thing in frame
    R, Hh = faces.HEAD_R, faces.HEAD_H
    for sx in (-1, 1):
        th = (92 / (faces.TEX_W / (2 * math.pi * 1.0)))      # radians round the head
        ang = sx * th
        px, py = R * math.sin(ang), -R * math.cos(ang)
        v = 1.0 - (faces.TEX_H * 0.40 - 50) / faces.TEX_H
        pz = 0.08 + v * (Hh - 0.16) - Hh / 2
        pr = 1.006
        hl = kit.sphere(f"sk.hl{sx}", 0.045, (px * pr, py * pr, pz), kit.emit("#fff8ee", 40.0), inner, seg=8)
        objs.append(hl)
    for ob in objs:
        pass
    # lights that follow it
    kit.light("sk_up", "POINT", (0, 0, 0.2), 110, "#ffe0c0", size=0.15)
    kit.light("sk_rim", "SPOT", (0, 0, 3), 520, "#f27a88", size=0.1, spot=38, blend=0.8)
    allobjs = objs + list(root.children_recursive)
    link_only(kit, "skater_up", "sk_up", [o for o in allobjs if o.type == "MESH"], "only")
    link_only(kit, "skater_rim", "sk_rim", [o for o in allobjs if o.type == "MESH"], "only")
    for n in ("conc0", "conc1", "amber", "hirefill", "closet", "tube"):
        link_only(kit, f"skater_not_{n}", n, [o for o in allobjs if o.type == "MESH"], "except")


def pose_skater(ctx, st):
    sk = ctx["sk"]
    P = POSES[st["pose"]]
    rad = math.radians
    la = [rad(a) for a in P["leg"]]
    dy = sum(L * math.sin(a) for L, a in zip(LEG, la))
    dz = sum(L * math.cos(a) for L, a in zip(LEG, la))
    sk["body"].location = (0, -dy, dz + BOOT_H)
    for sx in (-1, 1):
        ch = sk["legs"][sx]
        prev = 0.0
        for k, a in enumerate(la):
            ch[k].rotation_euler = (a - prev, 0, 0)
            prev = a
    for sx in (-1, 1):
        sk["legs"][sx][3].rotation_euler = (-la[-1], 0, 0)     # the skate stays level
    for sx in (-1, 1):
        ch = sk["arms"][sx]
        reach = "reach" in P and sx == st.get("reach_side", 1)
        angs = P["reach"] if reach else P["arm"]
        prev = 0.0
        for k, a in enumerate(angs):
            ch[k].rotation_euler = (rad(a) - prev, 0, 0)
            prev = rad(a)
        off = 0.0 if reach else P["dx"]
        ch[1].location = (sx * off, 0, -UPPER)
        ch[2].location = (sx * off, 0, -FORE)
    sk["root"].location = (st["pos"][0], st["pos"][1], 0.0)
    sk["root"].rotation_euler = (0, 0, rad(st["yaw"]))
    hy, hp = st["head"]
    sk["head"].rotation_euler = (rad(hp), 0, rad(hy))
    for ob in [sk["root"]] + list(sk["root"].children_recursive):
        ob.hide_render = bool(st["hidden"])


# ------------------------------------------------------------------------------------------ build / animate


def build(kit, story, tl):
    ctx = {}
    build_lights(kit, ctx)
    build_hall(kit, ctx)
    build_rail(kit, ctx)
    build_snack(kit, ctx)
    build_hire(kit, ctx)
    build_booth(kit, ctx)
    build_skater(kit, ctx)
    ctx["sk_state"] = None
    return ctx


SPOT0 = {"to": [-6.5, -3.9], "gain": 1.0, "size": 38.0}
DIM0 = {"level": 0.2}


def _init_cast(kit, story, tl, ctx):
    ctx["init"] = True
    ctx["skates"] = {}
    boot_c = {"nan": "#f4f1ea", "pop": "#6e4a2c"}
    for who, spec in story["cast"].items():
        sc = rig.S * spec.get("height", 1.0)
        wid = spec.get("width", 1.0)
        objs = []
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg is None:
                continue
            boot = kit.plastic(boot_c.get(who, "#e8dcc2"), 0.45)
            wh = kit.plastic("#a3232b", 0.5)
            objs.append(kit.box(f"{who}.skboot{sx}", (1.02, 1.5, 0.55), (0, -0.2, -1.74), boot, leg, bevel=0.1))
            objs.append(kit.box(f"{who}.skplate{sx}", (0.9, 1.5, 0.08), (0, -0.2, -2.04), kit.plastic("#2c2b30", 0.5), leg))
            for wy in (-0.7, -0.25, 0.2, 0.55):
                objs.append(kit.cyl(f"{who}.skwh{sx}{wy}", 0.17, 0.16, (0, wy - 0.1, -2.13), wh, leg, rot=(0, math.pi / 2, 0), n=12))
        ctx["skates"][who] = (objs, 0.3 * sc)
    # Pop: bald with a white fringe, shorts above the knee and thick white tape on both knees, a plain watch
    if "pop" in story["cast"]:
        sk = story["cast"]["pop"]["skin"]
        skin = kit.plastic(sk, 0.5)
        tape = kit.plastic("#f6f3ec", 0.7)
        for sx in (-1, 1):
            leg = bpy.data.objects[f"pop.leg{sx}"]
            kit.box(f"pop.shin{sx}", (0.995, 1.015, 1.1), (0, 0, -1.18), skin, leg, bevel=0.08)
            for k, zz in enumerate((-0.82, -1.02, -1.22)):
                kit.box(f"pop.tape{sx}{k}", (1.07, 1.09, 0.2), (0, 0, zz), tape, leg, bevel=0.05)
        hg = bpy.data.objects["pop.headg"]
        white = kit.plastic("#ecebe8", 0.8)
        R = faces.HEAD_R
        kit.box("pop.fb", (2 * R + 0.02, 0.3, 0.46), (0, R - 0.06, 0.02), white, hg, bevel=0.1)
        for sx in (-1, 1):
            kit.box(f"pop.fs{sx}", (0.2, 0.8, 0.4), (sx * (R - 0.02), 0.22, 0.02), white, hg, bevel=0.08)
        arm = bpy.data.objects["pop.arm-1"]
        kit.box("pop.band", (1.03, 1.03, 0.26), (0, 0, -1.55), kit.plastic("#3a2a1c", 0.6), arm, bevel=0.04)
        kit.cyl("pop.wface", 0.27, 0.08, (0, -0.53, -1.55), kit.plastic("#f1ead8", 0.4), arm, rot=(math.pi / 2, 0, 0), n=20)
        kit.box("pop.wh1", (0.03, 0.02, 0.2), (0, -0.585, -1.5), kit.plastic("#17120f", 0.5), arm)
        kit.box("pop.wh2", (0.16, 0.02, 0.03), (0.07, -0.585, -1.55), kit.plastic("#17120f", 0.5), arm)
    ctx["linkdone"] = True


def _skater_state(tl, t):
    cs = [c for c in _cues(tl, "skater") if c["t"] <= t + 1e-9]
    st = {"pos": [0.0, 0.0], "yaw": 0.0, "pose": "rest", "head": [0.0, 0.0], "hidden": True, "reach_side": 1}
    for c in cs:
        for k in ("pos", "yaw", "pose", "hidden", "reach_side"):
            if k in c:
                st[k] = c[k]
        if "head" in c:
            st["head"] = list(c["head"])
        if "look" in c:
            dx, dy = c["look"][0] - st["pos"][0], c["look"][1] - st["pos"][1]
            want = math.degrees(math.atan2(dx, -dy))
            rel = (want - st["yaw"] + 180) % 360 - 180
            st["head"] = [rel, c.get("pitch", 0.0)]
    return st


def animate(kit, story, tl, t, ctx):
    if not ctx.get("init"):
        _init_cast(kit, story, tl, ctx)
    over = {}
    shot = _shot(tl, t)["id"]
    # ---- the room: a slow ramp between levels
    dim = _ramp(_cues(tl, "dim"), t, DIM0, ["level"])["level"]
    for n in ("house0", "house1", "house2"):
        over[n] = dim ** 1.5
    over["conc0"] = over["conc1"] = 0.15 + 0.85 * dim
    over["amber"] = 0.55 + 0.45 * dim
    over["hirefill"] = 0.3 + 0.7 * dim
    # ---- the spotlight: a soft pool that slides, never pops
    sp = _ramp(_cues(tl, "spot"), t, SPOT0, ["to", "gain", "size"])
    tx, ty = sp["to"]
    s = kit.LIGHTS["spot"]
    s["obj"].location = (tx - 1.2, ty - 0.9, 4.7)
    kit.aim(s["obj"], (tx, ty, 0.0))
    s["light"].spot_size = math.radians(sp["size"])
    over["spot"] = sp["gain"]
    # ---- the fans
    for i, hub in enumerate(ctx["fans"]):
        hub.rotation_euler = (0, 0, t * 1.1 + i)
    overhead = shot in set(story.get("overhead_shots", []))
    for o in ctx["ceiling"]:
        o.hide_render = overhead
    # ---- the hire-counter door
    dc = _ramp(_cues(tl, "door"), t, {"open": 0.0}, ["open"])
    ctx["door"].rotation_euler = (0, 0, -math.radians(95) * dc["open"])
    # ---- the Skater and the lights that follow it
    st = _skater_state(tl, t)
    pose_skater(ctx, st)
    px, py = st["pos"]
    d = math.hypot(px - tx, py - ty)
    near = 1.0 - _ss((d - 1.4) / 2.2)
    side = 1.0 if px < 1.0 else -1.0
    up = kit.LIGHTS["sk_up"]["obj"]
    up.location = (px + 0.9 * side, py - 0.9, 0.22)
    over["sk_up"] = 0.3 + 0.7 * near
    rim = kit.LIGHTS["sk_rim"]["obj"]
    rim.location = (px - 0.4, py + 2.6, 2.9)
    kit.aim(rim, (px, py, 1.5))
    over["sk_rim"] = 0.35 + 0.65 * near
    # ---- the cast: sitting, skating, wobbling, skates on and off
    steam_on = _switch(_cues(tl, "steam"), "on", t, False)
    for who, keys in tl["acting"].items():
        root = bpy.data.objects.get(who)
        if root is None:
            continue
        hidden = bool(_switch(keys, "hidden", t, False))
        on = False
        for c in _cues(tl, "skates"):
            if c["who"] == who and c["t"] <= t + 1e-9:
                on = bool(c["on"])
        skating = bool(_switch(keys, "skate", t, False))
        objs, lift = ctx["skates"].get(who, ([], 0.0))
        for ob in objs:
            ob.hide_render = hidden or not on
        if _switch(keys, "sit", t, False):
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (-math.pi / 2, 0, 0)
        elif skating:
            seed = sum(map(ord, who))
            ph = 2 * math.pi * 0.42 * t + seed
            for sx, sg in ((-1, 1), (1, -1)):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (sg * 0.3 * math.sin(ph), 0, 0)
        if on and not _switch(keys, "sit", t, False):
            root.location.z += lift
        amp = _switch(keys, "wobble", t, 0.0)
        if amp:
            r = math.radians(amp) * (math.sin(2 * math.pi * 0.85 * t) + 0.5 * math.sin(2 * math.pi * 1.55 * t + 1.0))
            e = root.rotation_euler
            root.rotation_euler = (e[0] + 0.5 * r * math.sin(2 * math.pi * 0.85 * t + 2.0), r, e[2])
    # ---- steam
    for ob, mix, i in ctx["steam"]:
        ph = ((t * 0.18 + i / 3.0) % 1.0)
        ob.hide_render = not steam_on
        ob.location = (-4.4 + 0.03 * math.sin(ph * 6 + i), LEDGE_Y, LEDGE_Z + 0.3 + 0.28 * ph)
        mix.inputs[0].default_value = 0.0 if not steam_on else 0.035 * math.sin(math.pi * ph)
    return over
