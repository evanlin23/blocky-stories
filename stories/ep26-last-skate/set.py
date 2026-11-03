"""ep26 "last-skate" / "Skip Ahead": the set. A bright roller rink on a Saturday afternoon (the old rink, re-lit).

Metres, z up, a character with yaw 0 faces -y (yaw 90 faces +x). The hall runs x -8 .. 8, y -9 .. 6.4, ceiling 5.2.
  - the maple floor is x +-7, y +-4.4. A waist-high cherry rail rings it on y = +-4.15 and x = +-7.15, cream posts
    every 1.2 m from x = 0 (the south rail has a gap between the posts at x -1.2 and 1.2).
  - the south concourse (y -9 .. -4.4): the snack bar on the west (stools at x -5.0 and -3.8, ledge, amber lamp, the
    clock with hands only on the wall above), the hire counter on the east (x 2.4 .. 6.8, cubby wall behind it).
  - the DJ booth on the north wall (Lenny at -0.35, 5.25, floor of the booth z 1.74): the cherry skip button at
    x -0.9 and the cream back button at x 0.2 on the ledge, and above them the song lights, twelve round bulbs.
  - I lean on the south rail at x 3.0; the Skater stands at the rail at x 3.8 or 4.3, in the middle, or far rail.

Cues set.py reads (all go through `tl["cues"]`, resolved to "t"):
  dim      {"level", "dur"}                 the room's lights, a slow ramp from this cue's time
  spot     {"to": [x, y], "gain", "size", "dur"}   the spotlight: where, how bright, the cone (deg), a slow ramp
  skater   {"pos", "yaw", "pose": rest|reach|straight, "fold": [left knee, right knee, left elbow, right elbow],
            "head": [yaw, pitch] relative | "look": [x, y], "hidden", "reach_side"}
  skates   {"who", "on"}                    roller skates on a character
  song     {"i", "state": off|cream|gold|cherry, "dur"}   one of the twelve song lights (the rule meter)
  clock    {"min", "dur"}                   the snack-bar clock, minutes since 3:00
  press    {"btn": skip|back}               a button dips for a moment
  ribbon   {"group": couples|gus, "on"}     the cherry ribbon hoops between wrists
Acting keys read here (acting.py ignores them): "sit": true, "skate": true, "wobble": degrees.
"""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector
from PIL import Image, ImageDraw, ImageFilter

from blocky import acting, faces, rig

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

CHERRY, CREAM, PINK = "#a8242d", "#e9dcc2", "#d9a0a2"
HALL = (-8.0, 8.0, -9.0, 6.4)
CEIL = 5.2
RAIL_Y = (-4.15, 4.15)
POSTS = 1.2
SEAT_Z = 0.7
STOOL_Y, LEDGE_Y, LEDGE_Z = -6.7, -5.98, 1.12
STOOLS = {"me": -5.0, "gus": -3.8}

# ---- the Skater's body (metres). Each limb has a second joint that is open (straight) or folded (bent twice).
LEGL = 0.26
LEG = (LEGL, LEGL, LEGL)
UPPER, FORE, FORE2 = 0.34, 0.32, 0.28
BOOT_H = 0.28
TORSO = (0.64, 0.34, 0.72)
SK_SCALE = 0.85
KNEE_DZ = {0: 3 * LEGL, 1: 0.45, 2: 0.08}    # the hip's height above the boots by how many knees are folded
FOLD_ARM = (70, -70, 70)                       # a folded arm: a zigzag flat against the chest, elbows showing
REACH_ARM = (-25, -155, -25)                  # a held-out arm: forward, back, forward (two bends)


def _leg_zigzag(dz):
    """Angles of a folded leg whose vertical extent is dz. A tight fold (dz small) bends at acute angles, about 40
    degrees between thigh and shin (a hard turn of 140): absolute angles (-a, 140 - a, -a). Else the old (-a, 1.8a, -a)."""
    if dz < 0.2:
        g = lambda a: LEGL * (2 * math.cos(math.radians(a)) + math.cos(math.radians(140 - a)))
        lo, hi = 20.0, 110.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if g(mid) > dz:
                lo = mid
            else:
                hi = mid
        a = (lo + hi) / 2
        return (-a, 140 - a, -a)
    f = lambda a: LEGL * (2 * math.cos(math.radians(a)) + math.cos(math.radians(1.8 * a)))
    lo, hi = 0.0, 67.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if f(mid) > dz:
            lo = mid
        else:
            hi = mid
    a = (lo + hi) / 2
    return (-a, 1.8 * a, -a)



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
    stripe = wstripes(kit, "wall stripes", "#a3434b", "#e3d6bb", 1.0)
    stripe2 = wstripes(kit, "wall stripes out", "#99444c", "#d9cdb4", 1.0)
    # floors
    kit.box("rink floor", (14.0, 8.8, 0.1), (0, 0, -0.05), kit.planks("#d4a05c", "#bd8446", 1.0, "X", rough=0.55))
    kit.box("concourse", (16.0, 4.6, 0.1), (0, -6.7, -0.05), kit.checker("#733a40", "#cdbf9f", 1.4, rough=0.45))
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
    wbox(kit, "w south", -8.2, 8.2, -9.3, -9.1, 0, H, stripe)
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
    kit.light("lot", "POINT", (-14.0, -2.0, 5.3), 60, "#ffc58a", size=0.3)
    kit.light("lot2", "POINT", (-14.0, -13.5, 5.3), 60, "#ffc58a", size=0.3)
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
    cherry = kit.plastic("#a63f48", 0.4)
    padm = kit.plastic("#8f3740", 0.7)
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
    kit.cyl("lampcord", 0.01, 1.0, (STOOLS["gus"], STOOL_Y, 2.85), kit.metal("#222222"))
    kit.cyl("lampshade", 0.05, 0.22, (STOOLS["gus"], STOOL_Y, 2.25), kit.emit("#ffb050", 5.0), n=18, r2=0.24)
    kit.sphere("lampbulb", 0.07, (STOOLS["gus"], STOOL_Y, 2.12), kit.emit("#ffd9a0", 14.0))
    # a paper boat of gold fries on the ledge, no steam, one fry drooping
    gold = kit.plastic("#e8b43c", 0.6)
    boat_x = -4.7
    kit.box("boat", (0.26, 0.11, 0.07), (boat_x, LEDGE_Y, LEDGE_Z + 0.065), cream, bevel=0.01)
    kit.box("boat band", (0.27, 0.115, 0.02), (boat_x, LEDGE_Y, LEDGE_Z + 0.06), cherry)
    for i in range(14):
        ang = i * 2.4
        kit.box(f"fry{i}", (0.022, 0.022, 0.11 - (i % 3) * 0.01),
                (boat_x + 0.085 * math.cos(ang) * (0.3 + (i % 4) * 0.22), LEDGE_Y + 0.03 * math.sin(ang),
                 LEDGE_Z + 0.135 + (i % 3) * 0.012), gold, rot=(0.2 * math.sin(ang), 0.25 * math.cos(ang * 1.7), ang))
    kit.box("fry droop", (0.022, 0.022, 0.12), (boat_x + 0.15, LEDGE_Y + 0.02, LEDGE_Z + 0.12), gold, rot=(0.0, 1.15, 0.3))
    # the clock: hands only, no numerals, no ticks. Face and hands look north, into the rink.
    clock_x, clock_z = -4.3, 3.3
    kit.cyl("clock rim", 0.57, 0.08, (clock_x, -9.05, clock_z), cherry, rot=(math.pi / 2, 0, 0), n=40)
    kit.cyl("clock face", 0.5, 0.06, (clock_x, -9.0, clock_z), cream, rot=(math.pi / 2, 0, 0), n=40)
    dark_h = kit.plastic("#1f1618", 0.5)
    hub_m = kit.empty("clock minute", (clock_x, -8.93, clock_z))
    kit.box("clock minute hand", (0.05, 0.02, 0.42), (0, 0, 0.17), dark_h, hub_m)
    hub_h = kit.empty("clock hour", (clock_x, -8.91, clock_z))
    kit.box("clock hour hand", (0.07, 0.02, 0.28), (0, 0, 0.1), dark_h, hub_h)
    kit.cyl("clock cap", 0.05, 0.03, (clock_x, -8.89, clock_z), cherry, rot=(math.pi / 2, 0, 0), n=16)
    ctx["clock"] = {"min": hub_m, "hour": hub_h}
    # lights
    kit.light("amber", "POINT", (STOOLS["gus"], STOOL_Y, 2.0), 170, "#ffbf70", size=0.1)


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


BULB_X = [(i - 5.5) * 0.34 for i in range(12)]
BULB_STATE = {   # colour, emission strength
    "off": ("#3a2a2e", 0.15), "cream": ("#f2e6c8", 0.9), "gold": ("#ffb42e", 1.3), "cherry": ("#ff2a4c", 1.2),
}
BTN_X = {"skip": -0.9, "back": 0.2}
BTN_Y, LEDGE_TOP = 4.64, 2.705


def build_booth(kit, ctx):
    cream = kit.plastic("#e8dcc2", 0.5)
    cherry = kit.plastic("#a63f48", 0.4)
    stripe = wstripes(kit, "wall stripes", "#a3434b", "#e3d6bb", 1.0)
    dark = kit.plastic("#1b1618", 0.4)
    kit.box("booth deck", (4.4, 2.0, 1.7), (0, 5.4, 0.85), stripe)
    kit.box("booth floor", (4.2, 1.8, 0.04), (0, 5.4, 1.72), kit.planks("#8f6535", "#7a552b", 1.0, "X"))
    kit.box("booth front", (4.4, 0.12, 0.9), (0, 4.5, 2.2), cream, bevel=0.02)
    kit.box("booth ledge", (4.6, 0.4, 0.07), (0, 4.58, 2.67), cherry)
    for sx in (-1.0, 1.0):
        kit.box(f"deck{sx}", (0.8, 0.34, 0.07), (sx * 1.5, 4.58, 2.74), dark)
        kit.cyl(f"platter{sx}", 0.14, 0.02, (sx * 1.5, 4.58, 2.78), kit.plastic("#2a2a30", 0.3))
    kit.box("booth roof", (4.8, 2.2, 0.12), (0, 5.4, 4.4), kit.plastic("#3a2a2c", 0.8))
    for sx in (-2.3, 2.3):
        kit.box(f"boothpost{sx}", (0.1, 0.1, 2.7), (sx, 4.5, 3.05), cream)
    kit.cyl("micpole", 0.012, 0.5, (1.05, 4.9, 2.95), kit.metal("#333333"))
    kit.sphere("micball", 0.045, (1.05, 4.9, 3.22), dark)
    kit.sphere("boothbulb", 0.08, (0.5, 5.0, 3.55), kit.emit("#ffd9a0", 14.0))
    kit.light("booth", "POINT", (0.5, 5.0, 3.4), 160, "#ffbf70", size=0.15)
    # the song lights: a cream board over the booth with twelve round bulbs, no text. The rule meter.
    kit.box("song board", (4.2, 0.1, 0.42), (0, 4.52, 3.85), cream, bevel=0.02)
    kit.box("song trim top", (4.3, 0.12, 0.05), (0, 4.5, 4.1), cherry)
    kit.box("song trim bottom", (4.3, 0.12, 0.05), (0, 4.5, 3.6), cherry)
    ctx["bulbs"] = []
    for i, x in enumerate(BULB_X):
        col, st = BULB_STATE["off"]
        m = kit.emit(col, st, name=f"songbulb{i}")
        b = kit.sphere(f"songbulb{i}", 0.11, (x, 4.44, 3.85), m, seg=18)
        b.scale = (1.0, 0.55, 1.0)
        node = next(n for n in m.node_tree.nodes if n.type == "EMISSION")
        ctx["bulbs"].append(node)
    # the two buttons on the ledge, side by side: cherry skip (a forward glyph of our own), cream back (the same reversed)
    ctx["btn"] = {}
    for name, bc, gc, flip in (("skip", kit.plastic("#c2283a", 0.35), kit.plastic("#f3e8d0", 0.4), 0.0),
                               ("back", kit.plastic("#efe3c8", 0.35), kit.plastic("#b0293b", 0.4), math.pi)):
        e = kit.empty(f"btn {name}", (BTN_X[name], BTN_Y, LEDGE_TOP))
        kit.cyl(f"btn {name} cap", 0.13, 0.08, (0, 0, 0.04), bc, e, n=28)
        for dx in (-0.045, 0.045):
            kit.cyl(f"btn {name} glyph{dx}", 0.05, 0.02, (dx * (1 if not flip else -1), 0, 0.095), gc, e, rot=(0, 0, flip), n=3)
        ctx["btn"][name] = e


def build_lights(kit, ctx):
    for i, hx in enumerate((-4.5, 0.0, 4.5)):
        kit.light(f"house{i}", "AREA", (hx, 0.4, 4.9), 720, "#ffd7a3", rot=(0, 0, 0), size=3.2)
    for i, cx in enumerate((-3.0, 3.5)):
        kit.light(f"conc{i}", "AREA", (cx, -6.6, 4.8), 520, "#ffd7a3", size=2.6)
    kit.aim(kit.light("flood", "SPOT", (-17.0, -3.0, 4.6), 2600, "#fff1d8", size=0.6, spot=75, blend=0.8), (-8.4, -6.0, 1.4))
    kit.light("dusk", "SUN", (0, 0, 10), 2.6, "#fff4e2", rot=(math.radians(60), 0, math.radians(-70)))
    kit.light("spot", "SPOT", (0, 0, 4.7), 2300, "#fff0dc", rot=(0, 0, 0), size=0.4, spot=40, blend=1.0)
    for n in ("house0", "house1", "house2", "conc0", "conc1"):
        pass


# ------------------------------------------------------------------------------------------ the Skater


def skater_face(path: Path):
    W, H = faces.TEX_W, faces.TEX_H
    cream = (176, 166, 146)
    im = Image.new("RGB", (W, H), cream)
    d = ImageDraw.Draw(im)
    cx = W // 2
    # a smooth, very slightly paler oval plate: no nose, no brows, no mouth but the painted smile
    d.ellipse([cx - 250, int(H * 0.06), cx + 250, int(H * 0.96)], fill=(186, 176, 156))
    im = im.filter(ImageFilter.GaussianBlur(5))
    d = ImageDraw.Draw(im)
    ink = (22, 16, 15)
    cherry = (170, 44, 54)
    ey = int(H * 0.40)
    for sx in (-1, 1):
        ex = cx + sx * 92
        d.ellipse([ex - 58, ey - 92, ex + 58, ey + 92], fill=(120, 24, 34))          # a dark cherry rim
        d.ellipse([ex - 49, ey - 80, ex + 49, ey + 80], fill=(226, 218, 198))        # a pale ring
        d.ellipse([ex - 36, ey - 60, ex + 36, ey + 66], fill=ink)                    # big dark pupil
    # the painted smile: a thin upturned arc across 60% of the plate, curled ends
    my = int(H * 0.66)
    hw = 150
    d.arc([cx - hw, my - 70, cx + hw, my + 70], 22, 158, fill=(52, 8, 16), width=8)
    for sx in (-1, 1):
        ex_ = cx + sx * hw * math.cos(math.radians(22))
        ey_ = my + 70 * math.sin(math.radians(22))
        d.line([(ex_, ey_), (ex_ + sx * 12, ey_ - 22)], fill=(52, 8, 16), width=8)   # the curl
        d.ellipse([ex_ + sx * 12 - 4, ey_ - 26, ex_ + sx * 12 + 4, ey_ - 18], fill=(52, 8, 16))
    im.save(path)
    return im


def build_ribbons(kit, ctx):
    """The rule marker on the couples skate: one cherry ribbon hoop (a hand-span ring) hanging between the near wrists of
    each pair (and, at L30, of Gus and me). Our own prop, no text. The Skater and the singles never wear one."""
    rb = kit.emit("#ff2e5a", 3.5)
    ctx["ribbons"] = []
    for key, group in ((("c1a", "c1b"), "couples"), (("c2a", "c2b"), "couples"), (("c3a", "c3b"), "couples"),
                       (("gus", "me"), "gus")):
        bpy.ops.mesh.primitive_torus_add(location=(0, 0, -9), major_radius=0.24, minor_radius=0.05, major_segments=28,
                                         minor_segments=8)
        ring = bpy.context.active_object
        ring.name = f"ribbon {key[0]}"
        ring.scale = (1.35, 1.35, 1.35)
        ring.data.materials.append(rb)
        for p_ in ring.data.polygons:
            p_.use_smooth = True
        ctx["ribbons"].append((key, group, ring, []))


def build_skater(kit, ctx):
    wd = ROOT / "out" / "work" / "ep26-last-skate" / "faces"
    wd.mkdir(parents=True, exist_ok=True)
    skin = kit.plastic("#e9dfc9", 0.55)
    glove = kit.plastic("#f3ead6", 0.5)
    joint = kit.plastic("#1f1618", 0.5)
    sm = ostripes(kit, "skater stripes", "#8f1d2a", "#e6d9bd", 5.0)
    sm2 = ostripes(kit, "skater stripes b", "#972230", "#e8dcc1", 6.0)
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
                add(kit.box(f"sk.kneeb{sx}{k}", (0.235, 0.235, 0.05), (0, 0, -L), joint, parent, bevel=0.01))
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
        add(kit.box(f"sk.shb{sx}", (0.24, 0.24, 0.1), (0, 0, 0.02), joint, j, bevel=0.015))
        chain = [j]
        parent = j
        for k, L in enumerate((UPPER, FORE, FORE2)):
            add(kit.box(f"sk.arm{sx}{k}", (0.2, 0.2, L), (0, 0, -L / 2), sm2 if k != 1 else sm, parent, bevel=0.02))
            nx = kit.empty(f"sk.el{sx}{k}", (0, 0, -L), parent)
            if k < 2:
                add(kit.box(f"sk.elb{sx}{k}", (0.215, 0.215, 0.05), (0, 0, -L), joint, parent, bevel=0.01))
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
        v = 1.0 - (faces.TEX_H * 0.40 - 7) / faces.TEX_H
        pz = 0.08 + v * (Hh - 0.16) - Hh / 2
        pr = 1.006
        hl = kit.sphere(f"sk.hl{sx}", 0.02, (px * pr, py * pr, pz), kit.emit("#fff8ee", 40.0), inner, seg=8)
        objs.append(hl)
    for ob in objs:
        pass
    # lights that follow it
    kit.light("sk_up", "POINT", (0, 0, 0.2), 150, "#ffffff", size=0.15)
    kit.light("sk_rim", "SPOT", (0, 0, 3), 300, "#dc7a86", size=0.1, spot=38, blend=0.8)
    allobjs = objs + list(root.children_recursive)
    link_only(kit, "skater_up", "sk_up", [o for o in allobjs if o.type == "MESH"], "only")
    link_only(kit, "skater_rim", "sk_rim", [o for o in allobjs if o.type == "MESH"], "only")
    for n in ("conc0", "conc1", "amber", "hirefill", "tube", "spot", "house0", "house1", "house2", "dusk", "flood", "lot", "lot2"):
        link_only(kit, f"skater_not_{n}", n, [o for o in allobjs if o.type == "MESH"], "except")


def pose_skater(ctx, st):
    """fold = [left knee, right knee, left elbow, right elbow], 1 folded (bent twice), 0 open (straight). The hip's
    height follows the knees: both open stands a head taller than the room, both folded comes up to my shoulder.
    pose "straight" opens everything; "reach" holds the arm on reach_side out in front, bent twice."""
    sk = ctx["sk"]
    rad = math.radians
    straight = st["pose"] == "straight"
    fold = [0, 0, 0, 0] if straight else [int(bool(v)) for v in st.get("fold", [1, 1, 1, 1])]
    nk = fold[0] + fold[1]
    dz = KNEE_DZ[nk]
    zig = _leg_zigzag(dz) if nk else (0.0, 0.0, 0.0)
    dy = sum(L * math.sin(rad(a)) for L, a in zip(LEG, zig))
    sk["body"].location = (0, -dy if nk else 0.0, dz + BOOT_H)
    splay = math.degrees(math.acos(min(1.0, dz / (3 * LEGL))))
    for sx, f in ((-1, fold[0]), (1, fold[1])):
        ch = sk["legs"][sx]
        if f:
            la = [rad(a) for a in zig]
            prev = 0.0
            for k, a in enumerate(la):
                ch[k].rotation_euler = (a - prev, 0, 0)
                prev = a
            ch[3].rotation_euler = (-la[-1], 0, 0)       # the skate stays level
        else:                                             # open: straight, too long, splayed out to stand at the same height
            for k in range(3):
                ch[k].rotation_euler = (0, 0, 0)
            ch[0].rotation_euler = (0, -sx * rad(splay), 0)
            ch[3].rotation_euler = (0, sx * rad(splay), 0)
    for sx, f in ((-1, fold[2]), (1, fold[3])):
        ch = sk["arms"][sx]
        reach = st["pose"] == "reach" and sx == st.get("reach_side", -1)
        prev = 0.0
        ch[1].location = (0, 0, -UPPER)
        ch[2].location = (0, 0, -FORE)
        if reach:
            ch[0].location = (sx * 0.41, -0.1, TORSO[2] - 0.08)
            for k, a in enumerate(REACH_ARM):
                ch[k].rotation_euler = (rad(a) - prev, 0, 0)
                prev = rad(a)
        elif f:   # a zigzag in the chest's plane, pressed to the front of the stripes
            ch[0].location = (sx * 0.38, -0.27, TORSO[2] - 0.12)
            for k, a in enumerate(FOLD_ARM):
                ch[k].rotation_euler = (0, sx * (rad(a) - prev), 0)
                prev = rad(a)
        else:     # open: hanging straight at its side
            ch[0].location = (sx * 0.41, 0, TORSO[2] - 0.08)
            for k in range(3):
                ch[k].rotation_euler = (0, 0, 0)
    sk["root"].location = (st["pos"][0], st["pos"][1], 0.0)
    sk["root"].rotation_euler = (0, 0, rad(st["yaw"]))
    sk["root"].scale = (SK_SCALE, SK_SCALE, SK_SCALE)
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
    build_ribbons(kit, ctx)
    build_skater(kit, ctx)
    ctx["sk_state"] = None
    return ctx


SPOT0 = {"to": [3.0, -3.9], "gain": 0.0, "size": 34.0}
DIM0 = {"level": 1.0}
# the song lights at the start of the film: 0..4 played, 5 cherry (the loop's guy, it cools), 6 playing, the rest to come
BULB0 = ["cream"] * 5 + ["cherry", "gold"] + ["off"] * 5


def _hex(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]


def _lin(c):
    return [(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in c]


def _bulb_look(tl, i, t):
    """(rgb, strength) of song light i at time t: a ramp from its last state to the next, never a pop."""
    st_from = BULB0[i]
    st_to = BULB0[i]
    t0, dur = -1e9, 1e-6
    for cue in sorted(_cues(tl, "song"), key=lambda c: c["t"]):
        if cue["i"] != i or cue["t"] > t + 1e-9:
            continue
        st_from = st_to          # a new cue starts from the state the last one was heading for
        st_to = cue["state"]
        t0, dur = cue["t"], max(float(cue.get("dur", 0.4)), 1e-6)
    u = _ss((t - t0) / dur)
    (c0, s0), (c1, s1) = BULB_STATE[st_from], BULB_STATE[st_to]
    a, b = _lin(_hex(c0)), _lin(_hex(c1))
    return [x + (y - x) * u for x, y in zip(a, b)], s0 + (s1 - s0) * u


def _init_cast(kit, story, tl, ctx):
    ctx["init"] = True
    ctx["skates"] = {}
    boot_c = {"coworker": "#f4f1ea", "me": "#f1efe9", "gus": "#f1efe9"}
    for who, spec in story["cast"].items():
        sc = rig.S * spec.get("height", 1.0)
        objs = []
        if who == "lenny":
            continue
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
    R = faces.HEAD_R
    # Gus: navy shorts above the knee (bare shins), a gold paper crown with no text
    if "gus" in story["cast"]:
        skin = kit.plastic(story["cast"]["gus"]["skin"], 0.5)
        for sx in (-1, 1):
            leg = bpy.data.objects[f"gus.leg{sx}"]
            kit.box(f"gus.shin{sx}", (0.995, 1.015, 1.1), (0, 0, -1.18), skin, leg, bevel=0.08)
        hg = bpy.data.objects["gus.headg"]
        gold = kit.plastic("#e3b23c", 0.35)
        top = faces.HEAD_H / 2
        kit.cyl("gus.crown base", R + 0.07, 0.24, (0, 0, top + 0.1), gold, hg, n=32)
        for k in range(6):
            a = k * math.pi / 3
            kit.box(f"gus.crown spike{k}", (0.2, 0.2, 0.34), ((R - 0.02) * math.cos(a), (R - 0.02) * math.sin(a), top + 0.36), gold, hg,
                    rot=(0, 0, a + math.pi / 4), bevel=0.02)
    # the lady from work: a cup of soda in her hand
    if "coworker" in story["cast"]:
        arm = bpy.data.objects["coworker.arm-1"]
        kit.cyl("cw.cup", 0.3, 0.75, (0, -0.45, -1.85), kit.plastic("#f3ead6", 0.4), arm, n=20, r2=0.36)
        kit.cyl("cw.cupband", 0.34, 0.2, (0, -0.45, -1.8), kit.plastic("#a3232b", 0.45), arm, n=20, r2=0.35)
        kit.cyl("cw.straw", 0.04, 0.5, (0.1, -0.45, -1.2), kit.plastic("#2a8d88", 0.4), arm, n=8)
    # Lenny: the headphones round his neck, not on his ears
    ch = rig.CHARS.get("lenny")
    if ch is not None:
        for ob in ch.hp["neck"]:
            ob.hide_render = False
        for ob in ch.hp["ears"]:
            ob.hide_render = True
    ctx["linkdone"] = True


def _skater_state(tl, t):
    cs = [c for c in _cues(tl, "skater") if c["t"] <= t + 1e-9]
    st = {"pos": [0.0, 0.0], "yaw": 0.0, "pose": "rest", "head": [0.0, 0.0], "hidden": True, "reach_side": -1,
          "fold": [1, 1, 1, 1]}
    for c in cs:
        for k in ("pos", "yaw", "pose", "hidden", "reach_side", "fold"):
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
    for n in ("dusk", "flood", "lot", "lot2"):     # the window light goes with the hall
        over[n] = 0.03 + 0.97 * dim ** 3
    over["conc0"] = over["conc1"] = 0.08 + 0.92 * dim ** 2
    over["amber"] = 0.3 + 0.7 * dim ** 2
    over["hirefill"] = 0.08 + 0.92 * dim ** 2
    over["tube"] = 0.15 + 0.85 * dim ** 2
    # ---- a per-shot level (story.json shots[].expo) so cuts land at similar brightness
    import os
    if os.environ.get("DBGDIM"):
        print("DBG t", t, "shot", shot, "dim", dim, {k: round(v, 3) for k, v in over.items()}, flush=True)
    expo = next((sh.get("expo", 1.0) for sh in story["shots"] if sh["id"] == shot), 1.0)
    for n in list(kit.LIGHTS):
        over[n] = over.get(n, 1.0) * expo
    # ---- the spotlight: a soft pool that slides, never pops
    sp = _ramp(_cues(tl, "spot"), t, SPOT0, ["to", "gain", "size"])
    tx, ty = sp["to"]
    s = kit.LIGHTS["spot"]
    s["obj"].location = (tx - 1.2, ty - 0.9, 4.7)
    kit.aim(s["obj"], (tx, ty, 0.0))
    s["light"].spot_size = math.radians(sp["size"])
    over["spot"] = sp["gain"] * expo
    # ---- the song lights, the rule meter: cream played, gold now, cherry skipped
    for i, node in enumerate(ctx["bulbs"]):
        rgb, strength = _bulb_look(tl, i, t)
        node.inputs["Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
        node.inputs["Strength"].default_value = strength
    # ---- the buttons dip when pressed
    for name, e in ctx["btn"].items():
        dip = 0.0
        for c in _cues(tl, "press"):
            if c["btn"] == name and 0 <= t - c["t"] < 0.3:
                dip = 0.03 * math.sin(math.pi * (t - c["t"]) / 0.3)
        e.location = (BTN_X[name], BTN_Y, LEDGE_TOP - dip)
    # ---- the clock: the minute hand jumps on each skip (a quick ease), the hour hand follows
    mins = _ramp(_cues(tl, "clock"), t, {"min": 10.0}, ["min"])["min"]
    ctx["clock"]["min"].rotation_euler = (0, -math.radians((mins % 60) * 6.0), 0)
    ctx["clock"]["hour"].rotation_euler = (0, -math.radians(((3 * 60 + mins) / 60.0 % 12) * 30.0), 0)
    # ---- the fans
    for i, hub in enumerate(ctx["fans"]):
        hub.rotation_euler = (0, 0, t * 1.1 + i)
    overhead = shot in set(story.get("overhead_shots", []))
    for o in ctx["ceiling"]:
        o.hide_render = overhead
    # ---- the Skater and the lights that follow it
    st = _skater_state(tl, t)
    pose_skater(ctx, st)
    px, py = st["pos"]
    d = math.hypot(px - tx, py - ty)
    near = 1.0 - _ss((d - 1.4) / 2.2)
    side = 1.0 if px < 1.0 else -1.0
    up = kit.LIGHTS["sk_up"]["obj"]
    boost = next((sh.get("skboost", 1.0) for sh in story["shots"] if sh["id"] == shot), 1.0)
    up.location = (px + 1.4 * side, py + 0.1, 0.2) if boost == 1.0 else (px - 1.1, py + 0.8, 0.3)   # boosted: low, from the side
    over["sk_up"] = (0.3 + 0.7 * near) * expo * boost
    rim = kit.LIGHTS["sk_rim"]["obj"]
    rim.location = (px - 0.4, py + 2.6, 2.9)
    kit.aim(rim, (px, py, 1.5))
    over["sk_rim"] = (0.35 + 0.65 * near) * expo * boost
    # ---- the cast: sitting, skating, wobbling, skates on and off
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
            # a skater glides: no walking arm swing or step bob on top of the pose
            wl = acting.state(tl, who, t)
            for sx, sg in ((-1, 1), (1, -1)):
                arm = bpy.data.objects.get(f"{who}.arm{sx}")
                if arm is not None:
                    e = arm.rotation_euler
                    arm.rotation_euler = (e[0] + sg * wl["legs"] * 0.9, e[1], e[2])
            root.location.z -= wl["bob"]
        if on and not _switch(keys, "sit", t, False):
            root.location.z += lift
        amp = _switch(keys, "wobble", t, 0.0)
        if amp:
            r = math.radians(amp) * (math.sin(2 * math.pi * 0.85 * t) + 0.5 * math.sin(2 * math.pi * 1.55 * t + 1.0))
            e = root.rotation_euler
            root.rotation_euler = (e[0] + 0.5 * r * math.sin(2 * math.pi * 0.85 * t + 2.0), r, e[2])
    # ---- the ribbons: tied between the near wrists of each pair while the group's cue is on
    bpy.context.view_layer.update()
    for (a, b), group, strip, knots in ctx["ribbons"]:
        on = bool(_switch([c for c in _cues(tl, "ribbon") if c.get("group") == group], "on", t, False))
        ra, rb_ = bpy.data.objects.get(a), bpy.data.objects.get(b)
        show = on and ra is not None and rb_ is not None and not ra.hide_render and not rb_.hide_render
        best = None
        if show:
            tips = lambda w: [bpy.data.objects[f"{w}.arm{sx}"].matrix_world @ Vector((0, 0, -1.7)) for sx in (-1, 1)]
            for pa in tips(a):
                for pb in tips(b):
                    d = (pa - pb).length
                    if best is None or d < best[0]:
                        best = (d, pa, pb)
        ok = best is not None and best[0] < 1.3
        for o in [strip] + knots:
            o.hide_render = not ok
        if ok:
            d, pa, pb = best
            mid = (pa + pb) / 2
            axis = (pb - pa).cross(Vector((0, 0, 1)))        # the hoop stands in the vertical plane through both wrists
            if axis.length < 1e-3:
                axis = Vector((0, 1, 0))
            strip.location = mid + Vector((0, 0, -0.06))
            strip.rotation_euler = axis.normalized().to_track_quat("Z", "Y").to_euler()
    return over
