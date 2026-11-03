"""ep80 "Snow globe": one snowy street (nine painted houses a side), the front of Grandpa Gus's house with its porch
and its front room, Mrs. Ortiz's coral house across the road, the sunny dry street at the corner, a cone lot, and
the globe itself (a glass dome 18 cm across with our whole street inside it, tiny). Built from kit.py's parts.
No text anywhere: every sign is a picture.

Coordinates (metres, z up; a character faces -y at yaw 0, +x at yaw 90, -x at yaw -90, +y at yaw 180):
- the road runs along y (-40 .. 33), centred on x = 0, 8 m wide; sidewalks to x = +-5.5; fences at x = +-5.6.
- WEST side (ours): houses face +x, front walls at x = -10. Grandpa's house is at y = 0: porch x -10 .. -7.2
  (roof underside 2.76), the front room x -17 .. -10 (floor top 0.12), a big window y -2.4 .. 2.4 in the front
  wall (sill top 0.95), the globe on the sill at (-10.25, 0.9), the green armchair at (-10.95, -1.4) facing +y.
- EAST side: Mrs. Ortiz's coral house at y = 0, front wall at x = +10, gate at (5.6, 0), flowerbed (7.4, 2.4).
- the corner: the next street runs along x at y 34 .. 42, dry and sunny. The cone lot is at (200, 0).
- the Stander (the creature) stands where the cue "stander" says: unseen on the real street until snow settles on it.

Cues read here: mode (the time of day), snow (flakes), spot (the dry patch), stander, globe (pos, tilt), swirl (a shake),
fig (the tiny figure's place in the globe and on the minimap), turn (it faces our roof), mapgrow, fog (the breath on
the glass), curtains (Mrs. Ortiz's), dog, truck, car, mail, bag, phone, mug, steam, blur, cone. Every light change
ramps over at least 0.3 s (the house flash bar).
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector as V
from PIL import Image, ImageDraw, ImageFilter

from blocky import acting, bl_story, faces, polish, rig

S = rig.S
TMP = Path(tempfile.mkdtemp(prefix="snowglobe"))
FZ = 0.02                      # the floor of the front room and the porch (level with the ground, so feet stand on z = 0)
CEIL = 2.9
PORCH_ROOF = 2.76
GL = (-10.25, 0.9)             # the globe's place on the sill
SILL = 0.95
GAUGE = 1.0 / 400.0            # the tiny street's scale inside the globe
DOME_R = 0.09
HOUSE_Y = [-28.0, -21.0, -14.0, -7.0, 0.0, 7.0, 14.0, 21.0, 28.0]
PAL = ["#8de3c4", "#ffe58a", "#ff8b74", "#8ec9ff", "#c9a8ff"]
WEST_COL = ["#ffe58a", "#c9a8ff", "#8de3c4", "#ff9fb0", "#8ec9ff", "#ffe58a", "#8de3c4", "#c9a8ff", "#8de3c4"]
EAST_COL = ["#8ec9ff", "#ffe58a", "#c9a8ff", "#8de3c4", "#ff8b74", "#ffe58a", "#8ec9ff", "#c9a8ff", "#ffe58a"]
ROOFS = ["#5d6f9a", "#a8504c", "#4a7f86", "#6a5a8e"]
MAP_ORTIZ = (5.4, 0.0)
MAP_MAIL = (-4.7, 0.9)
MAP_PORCH = (-8.6, 0.0)
MAP_MID = (0.0, 0.0)
FIG_AT = {"mid": MAP_MID, "ortiz": MAP_ORTIZ, "mail": MAP_MAIL, "porch": MAP_PORCH}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


# ------------------------------------------------------------------------------------------------ cues


def _cues(tl, name):
    cache = tl.setdefault("_cache", {})
    if name not in cache:
        cache[name] = sorted((c for c in tl["cues"] if c["name"] == name), key=lambda c: c["t"])
    return cache[name]


def _last(cs, t):
    out = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            out = c
    return out


def ramped(cs, key, t, default, mind=0.3):
    """A value that eases to each cue's over its dur (never under 0.3 s), from where it was."""
    prev = default
    for c in cs:
        if key not in c:
            continue
        if t < c["t"]:
            break
        d = max(mind, c.get("dur", mind))
        v = c[key]
        if t < c["t"] + d:
            return prev + (v - prev) * ss((t - c["t"]) / d)
        prev = v
    return prev


def tween(cs, key, t, default, mind=0.0):
    """Like ramped, for vectors (positions): each cue's value is reached over its dur."""
    prev = default
    for c in cs:
        if key not in c:
            continue
        if t < c["t"]:
            break
        d = max(mind, c.get("dur", 0.0))
        v = c[key]
        if d > 0 and t < c["t"] + d:
            u = ss((t - c["t"]) / d)
            if isinstance(v, (list, tuple)):
                return [a + (b - a) * u for a, b in zip(prev, v)]
            return prev + (v - prev) * u
        prev = v
    return prev


# ------------------------------------------------------------------------------------------------ small helpers


def P(kit, hexc, rough=0.7, spec=0.25):
    return kit.plastic(hexc, rough, spec=spec)


def multibox(kit, name, boxes, mat, parent=None):
    """boxes: (sx, sy, sz, cx, cy, cz) each; one mesh."""
    verts, fcs = [], []
    for sx, sy, sz, cx, cy, cz in boxes:
        base = len(verts)
        verts += kit.box_verts(sx, sy, sz, (cx, cy, cz))
        fcs += [tuple(base + i for i in f) for f in kit.BOX_FACES]
    return kit.mesh_obj(name, verts, fcs, mat, parent)


def prism(kit, name, x0, x1, y0, y1, z0, zr, mat, parent=None):
    """A gable roof: ridge along y at the middle of x0..x1."""
    xm = (x0 + x1) / 2
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (xm, y0, zr), (xm, y1, zr)]
    f = [(0, 1, 2, 3), (0, 4, 5, 3), (1, 2, 5, 4), (0, 1, 4), (3, 5, 2)]
    return kit.mesh_obj(name, v, f, mat, parent)


def no_shadow(ob):
    try:
        ob.visible_shadow = False
    except Exception:
        pass


def ghost(kit, name, hexc, alpha, emit=0.0):
    """A see-through white-ish blob (steam, a snow blur, breath)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = max(0.05, emit)
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = alpha
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(e.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def dome_glass(kit):
    """Clear glass without refraction: see-through in the middle, a bright sky rim at the edge."""
    if "dome" in kit.MATS:
        return kit.MATS["dome"]
    m = kit._new("dome")
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.03
    gl.inputs["Color"].default_value = kit.col("#e6f3ff")
    fr = nt.nodes.new("ShaderNodeFresnel")
    fr.inputs["IOR"].default_value = 1.6
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(fr.outputs[0], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(gl.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


_IMG_N = [0]


def img_mat(kit, name, im, emit=1.0):
    _IMG_N[0] += 1
    p = TMP / f"{name}-{_IMG_N[0]}.png"
    im.save(p)
    m = kit._new(f"img {name} {_IMG_N[0]}")
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(p))
    tex.image.colorspace_settings.name = "sRGB"
    tex.interpolation = "Linear"
    uv = nt.nodes.new("ShaderNodeUVMap")
    nt.links.new(uv.outputs["UV"], tex.inputs["Vector"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Strength"].default_value = emit
    nt.links.new(tex.outputs["Color"], e.inputs["Color"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tex.outputs["Alpha"], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(e.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def img_plane(kit, name, w, h, mat, loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    x, y = w / 2, h / 2
    ob = kit.mesh_obj(name, [(-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0)], [(0, 1, 2, 3)], mat, parent, loc, rot)
    uv = ob.data.uv_layers.new(name="UV")
    for lp in ob.data.loops:
        v = ob.data.vertices[lp.vertex_index].co
        uv.data[lp.index].uv = ((v.x + x) / w, (v.y + y) / h)
    no_shadow(ob)
    return ob


# ------------------------------------------------------------------------------------------------ the world


def build_ground(kit, ctx):
    snow = P(kit, "#e9f1fa", 0.92, 0.1)
    road = P(kit, "#dfe9f5", 0.9, 0.12)
    walk = P(kit, "#d2dfec", 0.9, 0.1)
    kit.box("ground", (400, 400, 0.2), (0, 0, -0.08), snow)
    kit.box("road", (8.0, 76.0, 0.06), (0, -5.0, 0.02), road)
    for sx in (-1, 1):
        kit.box(f"walk{sx}", (1.5, 76.0, 0.04), (sx * 4.75, -5.0, 0.02), walk)
        kit.box(f"kerb{sx}", (0.18, 76.0, 0.1), (sx * 4.09, -5.0, 0.03), P(kit, "#c3d1e2", 0.9))
    # the dry patch: bare, wet asphalt, a little proud of the snow
    ctx["spot"] = kit.box("spot", (0.62, 0.5, 0.03), (0, 0, 0.065), P(kit, "#4d525c", 0.55, 0.3), bevel=0.01)
    ctx["rim"] = kit.box("spot.rim", (0.8, 0.68, 0.025), (0, 0, 0.058), P(kit, "#b9c8da", 0.9), bevel=0.01)
    ctx["rim"].parent = ctx["spot"]
    ctx["rim"].location = (0, 0, -0.007)
    # the next street: dry, sunny, beyond the snow line
    asph = P(kit, "#8b939c", 0.7, 0.2)
    kit.box("cross", (160, 9.0, 0.08), (0, 38.5, 0.0), asph)
    kit.box("dry.east", (60, 28, 0.06), (45, 52, 0.0), P(kit, "#c9d6a8", 0.9))
    kit.box("dry.west", (60, 28, 0.06), (-45, 52, 0.0), P(kit, "#c9d6a8", 0.9))
    kit.box("dry.n", (160, 30, 0.06), (0, 56.5, 0.0), P(kit, "#c9d6a8", 0.9))
    kit.box("snowline", (20, 0.5, 0.12), (0, 33.8, 0.03), P(kit, "#f7fbff", 0.9))
    # a dashed line down the cross street
    kit.box("cross.dash", (160, 0.14, 0.01), (0, 38.5, 0.05), P(kit, "#f2d65a", 0.6))
    # the crosswalk at the corner, painted in a curve round the middle of the road
    st = []
    for i in range(-4, 5):
        x = i * 0.85
        y = 30.2 + 1.9 * math.exp(-(x / 2.6) ** 2)
        st.append((0.48, 0.9, 0.012, x, y, 0.056))
    multibox(kit, "crosswalk", st, P(kit, "#ffd54a", 0.6))


def pine(kit, name, x, y, s=1.0, snowy=True):
    g = kit.empty(name, (x, y, 0))
    kit.cyl(f"{name}.trunk", 0.18 * s, 1.0 * s, (0, 0, 0.5 * s), P(kit, "#7a4f2e", 0.8), g, n=8)
    for i, (r, h, z) in enumerate(((1.5, 1.6, 1.4), (1.15, 1.4, 2.4), (0.8, 1.2, 3.3))):
        kit.cyl(f"{name}.t{i}", r * s, h * s, (0, 0, z * s), P(kit, "#2e7a4c", 0.8), g, n=8, r2=0.02)
        if snowy:
            kit.cyl(f"{name}.s{i}", r * 0.72 * s, h * 0.55 * s, (0, 0, (z + h * 0.28) * s), P(kit, "#f2f8ff", 0.9), g, n=8, r2=0.0)
    return g


def build_house(kit, ctx, name, side, y, color, roof_c, door_c="#ffffff", ours=False, ortiz=False):
    """A painted house: front wall at x = side * 10, the body going back 6 m, a snow roof, a fence with a gate."""
    f = -side                      # +1 when the front faces +x
    xf = side * 10.0               # front wall plane
    xb = side * 16.0
    xc = (xf + xb) / 2
    wall = P(kit, color, 0.6)
    trim = P(kit, "#ffffff", 0.55)
    if not ours:
        kit.box(f"{name}.body", (6.0, 6.4, 3.0), (xc, y, 1.5), wall, bevel=0.03)
    if not ours:
        prism(kit, f"{name}.roof", min(xf, xb) - 0.45, max(xf, xb) + 0.45, y - 3.6, y + 3.6, 3.0, 4.9,
              P(kit, "#f5f9ff", 0.9, 0.1))
        kit.box(f"{name}.fascia", (6.9, 0.08, 0.18), (xc, y - 3.62, 2.95), P(kit, roof_c, 0.7))
        kit.box(f"{name}.fascia2", (6.9, 0.08, 0.18), (xc, y + 3.62, 2.95), P(kit, roof_c, 0.7))
    # windows and the door on the front
    glass = P(kit, "#a9d8ff", 0.1, 0.9)
    gy = (-2.0, 2.0) if not ours else ()
    door_y = y + (1.0 if ortiz else 0.0)
    if not ours:
        for wy in gy:
            if ortiz and wy > 0:
                continue
            kit.box(f"{name}.win{wy}", (0.06, 1.3, 1.2), (xf + f * 0.035, y + wy, 1.6), glass)
            kit.box(f"{name}.wint{wy}", (0.05, 1.5, 0.12), (xf + f * 0.03, y + wy, 2.28), trim)
            kit.box(f"{name}.winb{wy}", (0.05, 1.5, 0.12), (xf + f * 0.03, y + wy, 0.96), trim)
        kit.box(f"{name}.door", (0.08, 1.0, 2.0), (xf + f * 0.045, door_y, 1.0), P(kit, door_c if door_c != "#ffffff" else "#2f7a4f", 0.5))
        kit.box(f"{name}.step", (0.9, 1.6, 0.14), (xf + f * 0.45, door_y, 0.07), P(kit, "#d8e4f0", 0.9))
    # fence along x = side * 5.6 with a gate gap at the middle for ours and Mrs. Ortiz's
    fx = side * 5.6
    pk = []
    ys = [y + k * 0.34 for k in range(-9, 10)]
    for yy in ys:
        if (ours or ortiz) and abs(yy - y) < 0.62:
            continue
        pk.append((0.07, 0.12, 0.85, fx, yy, 0.42))
    pk.append((0.05, 6.4, 0.08, fx, y, 0.28))
    pk.append((0.05, 6.4, 0.08, fx, y, 0.68))
    multibox(kit, f"{name}.fence", pk, P(kit, "#ffffff", 0.6))
    if ours or ortiz:
        for sy_ in (-0.62, 0.62):
            kit.box(f"{name}.gatepost{sy_}", (0.14, 0.14, 1.05), (fx, y + sy_, 0.52), trim)
        ctx[f"{name}.gate"] = kit.box(f"{name}.gate", (0.05, 1.1, 0.7), (fx, y, 0.45), trim)
        ctx[f"{name}.gate"].location = (fx, y, 0.45)
    # the path from the gate to the door
    xs = sorted([fx, xf + f * 0.9])
    kit.box(f"{name}.path", (abs(xs[1] - xs[0]), 1.2, 0.03), ((xs[0] + xs[1]) / 2, door_y if not ours else y, 0.045), P(kit, "#cfdceb", 0.9))
    # the mailbox on a post at the sidewalk
    mx = side * 4.7
    my = y + 1.3
    kit.box(f"{name}.mpost", (0.1, 0.1, 1.0), (mx, my, 0.5), P(kit, "#8a8f98", 0.6))
    mb = kit.box(f"{name}.mbox", (0.36, 0.22, 0.24), (mx, my, 1.1), P(kit, "#4a7fd0" if ours else "#d0584a", 0.5), bevel=0.04)
    kit.box(f"{name}.msnow", (0.38, 0.24, 0.04), (mx, my, 1.24), P(kit, "#f5f9ff", 0.9))
    # a lamp in the porch of every house? no: just a small step and snow bush
    if not ours:
        kit.box(f"{name}.bush", (1.0, 1.3, 0.55), (xf + f * 1.7, y - 2.6, 0.27), P(kit, "#4f9a5f", 0.8), bevel=0.15)
        kit.box(f"{name}.bushs", (0.9, 1.15, 0.12), (xf + f * 1.7, y - 2.6, 0.58), P(kit, "#f5f9ff", 0.9), bevel=0.04)


def build_street(kit, ctx):
    for i, y in enumerate(HOUSE_Y):
        ours = (i == 4)
        build_house(kit, ctx, f"w{i}", -1, y, WEST_COL[i], ROOFS[i % 4], ours=ours)
        ortiz = (i == 4)
        build_house(kit, ctx, f"e{i}", 1, y, EAST_COL[i], ROOFS[(i + 1) % 4], door_c="#2a5a8a" if not ortiz else "#4a2a6a", ortiz=ortiz)
    # pines behind and between
    for k, (x, y) in enumerate(((-21, -17), (-21, -3), (-21, 10), (-21, 24), (21, -11), (21, 4), (21, 17), (21, 30),
                                (-12, 36), (14, 47), (-30, 44), (30, 50), (-6, -38), (8, -38), (-16, -36), (18, -36))):
        pine(kit, f"pine{k}", x, y, 1.1 + 0.15 * (k % 3))
    # the sunny street: a yellow car and a few houses behind
    car(kit, ctx, "carsun", "#f2c230", (24, 39.5, 0), 90)
    for k, (x, c) in enumerate(((-30, "#8de3c4"), (-14, "#ffe58a"), (6, "#ff8b74"), (26, "#c9a8ff"))):
        kit.box(f"back{k}", (9, 7, 4), (x, 50, 2.0), P(kit, c, 0.6), bevel=0.03)
        kit.box(f"backr{k}", (9.8, 7.8, 0.4), (x, 50, 4.2), P(kit, ROOFS[k % 4], 0.7))
    # the streetlight on our side
    kit.cyl("lamppost", 0.07, 4.6, (-4.35, -3.4, 2.3), P(kit, "#4a5260", 0.5), n=10)
    kit.box("lamparm", (0.9, 0.08, 0.08), (-4.8, -3.4, 4.55), P(kit, "#4a5260", 0.5))
    kit.box("lamphead", (0.5, 0.3, 0.14), (-5.1, -3.4, 4.5), kit.emit("#e8f3ff", 6.0))
    kit.cyl("lamppost2", 0.07, 4.6, (4.35, 14, 2.3), P(kit, "#4a5260", 0.5), n=10)
    kit.cyl("lamppost3", 0.07, 4.6, (-4.35, 22, 2.3), P(kit, "#4a5260", 0.5), n=10)


def car(kit, ctx, name, hexc, loc, yaw):
    """A plain little car (no text): body, cabin, wheels, lights. Faces -y at yaw 0."""
    g = kit.empty(name, loc, rot=(0, 0, math.radians(yaw)))
    kit.box(f"{name}.body", (1.9, 4.2, 0.7), (0, 0, 0.62), P(kit, hexc, 0.35, 0.5), g, bevel=0.12)
    kit.box(f"{name}.cab", (1.6, 2.2, 0.62), (0, 0.2, 1.22), P(kit, hexc, 0.35, 0.5), g, bevel=0.12)
    gl = P(kit, "#7fb4de", 0.1, 0.9)
    kit.box(f"{name}.glassf", (1.5, 0.06, 0.45), (0, -0.9, 1.25), gl, g, rot=(0.3, 0, 0))
    kit.box(f"{name}.glasss", (1.64, 1.6, 0.4), (0, 0.2, 1.27), gl, g)
    for sx in (-1, 1):
        for sy_ in (-1.35, 1.35):
            kit.cyl(f"{name}.w{sx}{sy_}", 0.34, 0.24, (sx * 0.95, sy_, 0.34), P(kit, "#25272c", 0.8), g, rot=(0, math.radians(90), 0), n=12)
        kit.box(f"{name}.lamp{sx}", (0.3, 0.05, 0.16), (sx * 0.6, -2.12, 0.7), kit.emit("#fff4c8", 1.5), g)
    ctx.setdefault("cars", {})[name] = g
    return g


def build_truck(kit, ctx):
    """Grandpa's old pine-green pickup. Faces -y at yaw 0. Open cab (no glass), so we can see in."""
    g = kit.empty("truck", (-3.4, 6.5, 0))
    gr = P(kit, "#2f7a4f", 0.4, 0.45)
    kit.box("truck.chassis", (2.0, 5.4, 0.5), (0, 0, 0.6), gr, g, bevel=0.1)
    kit.box("truck.hood", (1.9, 1.5, 0.55), (0, -1.9, 0.98), gr, g, bevel=0.1)
    kit.box("truck.floor", (1.9, 1.7, 0.1), (0, -0.2, 0.9), P(kit, "#2a2f34", 0.8), g)
    kit.box("truck.seat", (1.5, 0.6, 0.2), (0, 0.5, 0.78), P(kit, "#c9b79a", 0.8), g, bevel=0.05)
    kit.box("truck.seatb", (1.5, 0.12, 0.8), (0, 0.85, 1.2), P(kit, "#c9b79a", 0.8), g, bevel=0.06)
    for sx in (-1, 1):
        kit.box(f"truck.pillar{sx}", (0.1, 0.12, 1.0), (sx * 0.92, -0.95, 1.6), gr, g)
        kit.box(f"truck.pillarb{sx}", (0.1, 0.14, 1.0), (sx * 0.92, 1.0, 1.6), gr, g)
        kit.box(f"truck.door{sx}", (0.08, 1.7, 0.55), (sx * 0.96, 0.1, 1.07), gr, g)
    kit.box("truck.roof", (2.0, 2.1, 0.12), (0, 0.0, 2.15), gr, g, bevel=0.05)
    kit.box("truck.roofs", (1.9, 2.0, 0.05), (0, 0.0, 2.24), P(kit, "#f5f9ff", 0.9), g)
    kit.box("truck.bed", (2.0, 2.0, 0.5), (0, 1.9, 0.95), gr, g, bevel=0.06)
    kit.box("truck.bedin", (1.7, 1.7, 0.1), (0, 1.9, 1.18), P(kit, "#1f5a3a", 0.7), g)
    kit.box("truck.bump", (2.1, 0.2, 0.2), (0, 2.95, 0.6), P(kit, "#dfe6ee", 0.4), g)
    kit.box("truck.bumpf", (2.1, 0.2, 0.2), (0, -2.75, 0.6), P(kit, "#dfe6ee", 0.4), g)
    wheel = P(kit, "#202226", 0.8)
    for sx in (-1, 1):
        for sy_ in (-1.7, 1.8):
            kit.cyl(f"truck.w{sx}{sy_}", 0.42, 0.3, (sx * 1.0, sy_, 0.42), wheel, g, rot=(0, math.radians(90), 0), n=14)
            kit.cyl(f"truck.h{sx}{sy_}", 0.18, 0.32, (sx * 1.0, sy_, 0.42), P(kit, "#c8d0d8", 0.4), g, rot=(0, math.radians(90), 0), n=10)
        kit.box(f"truck.lamp{sx}", (0.3, 0.06, 0.2), (sx * 0.65, -2.66, 0.95), kit.emit("#fff4c8", 1.5), g)
    # the steering wheel (a ring and a column), no hands shown on it
    kit.cyl("truck.wheel", 0.2, 0.04, (-0.45, -0.65, 1.45), P(kit, "#24272c", 0.6), g, rot=(math.radians(-60), 0, 0), n=14)
    ctx["truck"] = g


# ------------------------------------------------------------------------------------------------ Grandpa's house


def build_house_ours(kit, ctx):
    M = ctx
    honey = P(kit, "#d9a466", 0.55, 0.3)
    honey2 = P(kit, "#c58f4e", 0.55, 0.3)
    cream = P(kit, "#f2e6c8", 0.7)
    blue = P(kit, "#8ec9ff", 0.6)
    white = P(kit, "#ffffff", 0.5)
    floor = kit.box("room.floor", (7.4, 7.4, 0.12), (-13.5, 0, -0.04), P(kit, "#b98a52", 0.6, 0.3))
    # the back wall in honey panelling, with battens
    kit.box("room.back", (0.2, 7.4, 3.0), (-17.1, 0, 1.5), honey)
    kit.box("room.backrail", (0.06, 7.4, 0.08), (-16.97, 0, 1.0), honey2)
    multibox(kit, "room.battens", [(0.04, 0.12, 2.8, -16.96, y, 1.5) for y in np.arange(-3.4, 3.5, 0.6)], honey2)
    # side walls (the east one has a door at x -14.5 .. -13.5)
    kit.box("room.sideW", (7.4, 0.2, 3.0), (-13.5, -3.7, 1.5), honey)
    kit.box("room.sideE1", (2.6, 0.2, 3.0), (-15.9, 3.7, 1.5), honey)
    kit.box("room.sideE2", (3.2, 0.2, 3.0), (-11.5, 3.7, 1.5), honey)
    kit.box("room.sideE3", (1.0, 0.2, 0.8), (-14.0, 3.7, 2.6), honey)
    kit.box("room.hall", (1.0, 1.4, 2.2), (-14.0, 4.6, 1.2), P(kit, "#4a3a30", 0.9))
    kit.box("room.hallglow", (0.7, 0.04, 1.7), (-14.0, 5.1, 1.1), kit.emit("#ffcf8a", 0.9))
    for sx in (-14.55, -13.45):
        kit.box(f"room.doorjamb{sx}", (0.1, 0.26, 2.1), (sx, 3.7, 1.17), white)
    kit.box("room.doorhead", (1.2, 0.26, 0.1), (-14.0, 3.7, 2.22), white)
    # the ceiling
    kit.box("room.ceil", (7.4, 7.4, 0.12), (-13.5, 0, CEIL + 0.06), cream)
    # the front wall with the big window (y -2.4 .. 2.4, z 0.95 .. 2.3)
    fw = P(kit, "#8ec9ff", 0.6)
    inn = P(kit, "#efe0c0", 0.7)
    for nm, sz, loc in (("L", (0.25, 1.3, 3.0), (-10.125, -3.05, 1.5)), ("R", (0.25, 1.3, 3.0), (-10.125, 3.05, 1.5)),
                        ("B", (0.25, 4.8, 0.95), (-10.125, 0, 0.475)), ("T", (0.25, 4.8, 0.7), (-10.125, 0, 2.65))):
        kit.box(f"fw{nm}", sz, loc, fw)
        kit.box(f"fwi{nm}", (0.04, sz[1], sz[2]), (-10.265, loc[1], loc[2]), inn)
    # the frame (white, proud of the wall) and the deep sill
    kit.box("fr.top", (0.34, 5.0, 0.12), (-10.125, 0, 2.36), white)
    kit.box("fr.L", (0.34, 0.12, 1.5), (-10.125, -2.46, 1.6), white)
    kit.box("fr.R", (0.34, 0.12, 1.5), (-10.125, 2.46, 1.6), white)
    kit.box("sill", (0.62, 5.2, 0.07), (-10.22, 0, SILL - 0.035), P(kit, "#fbfdff", 0.5, 0.4), bevel=0.01)
    # porch: floor, two posts, the roof, the porch light
    kit.box("porch.floor", (2.9, 4.6, 0.12), (-8.65, 0, -0.03), P(kit, "#e9efe8", 0.8))
    kit.box("porch.snow", (2.9, 4.6, 0.02), (-8.65, 0, 0.04), P(kit, "#f2f7fd", 0.9))
    kit.box("porch.step", (0.6, 1.6, 0.08), (-7.0, 0, 0.04), P(kit, "#e0e8ef", 0.9))
    for sy_ in (-2.1, 2.1):
        kit.box(f"porch.post{sy_}", (0.16, 0.16, PORCH_ROOF - 0.1), (-7.35, sy_, (PORCH_ROOF + 0.1) / 2 - 0.05), white)
    kit.box("porch.roof", (3.3, 4.9, 0.1), (-8.65, 0, PORCH_ROOF + 0.05), P(kit, "#7c8fb8", 0.6))
    kit.box("porch.roofsnow", (3.3, 4.9, 0.1), (-8.65, 0, PORCH_ROOF + 0.15), P(kit, "#f5f9ff", 0.9))
    kit.box("porch.lamp", (0.18, 0.2, 0.32), (-10.08, -2.0, 2.4), kit.emit("#ffcf80", 2.5))
    # the sky-blue trim of the house body on either side of the room, and the main roof
    kit.box("house.rear", (0.5, 7.4, 3.0), (-17.4, 0, 1.5), blue)
    kit.box("house.sideN", (7.4, 0.3, 3.0), (-13.5, 3.95, 1.5), blue)
    kit.box("house.sideS", (7.4, 0.3, 3.0), (-13.5, -3.95, 1.5), blue)
    kit.box("house.up", (7.6, 7.6, 0.4), (-13.5, 0, 3.2), blue)
    prism(kit, "house.roof", -17.8, -9.6, -4.1, 4.1, 3.4, 5.2, P(kit, "#f5f9ff", 0.9, 0.1))
    # furniture: the green armchair (faces +y), a rug, a side table and lamp, a bookshelf, a plant, frames
    green = P(kit, "#2f7a4f", 0.75, 0.2)
    cx, cy = -10.95, -1.4
    kit.box("chair.seat", (0.95, 0.9, 0.2), (cx, cy, 0.5), green, bevel=0.06)
    kit.box("chair.base", (0.95, 0.9, 0.3), (cx, cy, 0.27), P(kit, "#1f5a3a", 0.8), bevel=0.04)
    kit.box("chair.back", (0.95, 0.2, 0.95), (cx, cy - 0.42, 0.95), green, bevel=0.08)
    for sx in (-1, 1):
        kit.box(f"chair.arm{sx}", (0.18, 0.86, 0.5), (cx + sx * 0.5, cy, 0.7), green, bevel=0.07)
    kit.box("rug", (3.4, 2.6, 0.02), (-12.6, 0.2, FZ + 0.012), P(kit, "#f2e6c8", 0.95))
    kit.box("rug.edge", (3.5, 2.7, 0.015), (-12.6, 0.2, FZ + 0.006), P(kit, "#e0a21c", 0.9))
    kit.box("table", (0.7, 0.7, 0.05), (-11.2, 2.9, 0.62), P(kit, "#a8743c", 0.5), bevel=0.02)
    kit.box("table.leg", (0.1, 0.1, 0.5), (-11.2, 2.9, 0.36), P(kit, "#8a5d2e", 0.5))
    kit.box("table.lamp", (0.2, 0.2, 0.28), (-11.2, 2.9, 0.81), kit.emit("#ffd9a0", 2.0))
    kit.box("shelf", (0.5, 2.0, 2.0), (-16.7, -1.5, 1.12), P(kit, "#8a5d2e", 0.55), bevel=0.02)
    for k, c in enumerate(("#e85a4f", "#4a7fd0", "#e0a21c", "#2f7a4f", "#c9a8ff", "#ff9fb0", "#8de3c4")):
        kit.box(f"shelf.b{k}", (0.3, 0.2, 0.34), (-16.62, -2.25 + k * 0.22, 1.5 - (k % 2) * 0.55), P(kit, c, 0.6))
    # a plant
    kit.cyl("pot", 0.2, 0.34, (-16.4, 2.6, 0.29), P(kit, "#c8553d", 0.6), n=12)
    for k in range(5):
        a = k * 1.26
        kit.box(f"leaf{k}", (0.12, 0.34, 0.5), (-16.4 + 0.12 * math.cos(a), 2.6 + 0.12 * math.sin(a), 0.7), P(kit, "#3f9a56", 0.6),
                rot=(0.4 * math.sin(a), 0.4 * math.cos(a), a), bevel=0.04)
    # pictures on the walls (plain colour fields, no writing)
    for k, (y, c) in enumerate(((-0.6, "#e85a4f"), (0.9, "#4a7fd0"))):
        kit.box(f"frame{k}", (0.05, 0.9, 0.7), (-16.95, y, 1.7), P(kit, "#f2e6c8", 0.6))
        kit.box(f"pic{k}", (0.04, 0.7, 0.5), (-16.92, y, 1.7), P(kit, c, 0.7))
    ctx["chair_seat_z"] = 0.62
    # a small round dinner table with two stools and two plates
    kit.cyl("dtable", 0.62, 0.05, (-14.2, 0.0, 0.7), P(kit, "#a8743c", 0.5), n=24)
    kit.cyl("dtable.leg", 0.1, 0.68, (-14.2, 0.0, 0.34), P(kit, "#8a5d2e", 0.5), n=10)
    for k, yy in enumerate((-0.98, 0.98)):
        kit.cyl(f"stool{k}", 0.24, 0.05, (-14.2, yy, 0.43), P(kit, "#2f7a4f", 0.7), n=14)
        kit.cyl(f"stool{k}.leg", 0.06, 0.4, (-14.2, yy, 0.2), P(kit, "#8a5d2e", 0.5), n=8)
        kit.cyl(f"plate{k}", 0.17, 0.02, (-14.2, yy * 0.45, 0.735), P(kit, "#fbfdff", 0.4), n=18)
        kit.box(f"food{k}", (0.14, 0.14, 0.05), (-14.2, yy * 0.45, 0.76), P(kit, "#d9843c", 0.6), bevel=0.03)


# ------------------------------------------------------------------------------------------------ Mrs. Ortiz's


def build_ortiz(kit, ctx):
    # the flowerbed in her front yard
    kit.box("bed", (2.4, 0.9, 0.18), (7.4, 2.4, 0.1), P(kit, "#6a4a36", 0.9), bevel=0.04)
    kit.box("bed.snow", (2.3, 0.82, 0.05), (7.4, 2.4, 0.2), P(kit, "#f5f9ff", 0.9), bevel=0.02)
    for k, c in enumerate(("#ff6f91", "#ffd23f", "#c77dff", "#ff6f91", "#ffd23f")):
        x = 6.5 + k * 0.45
        kit.box(f"fl.stem{k}", (0.04, 0.04, 0.4), (x, 2.4, 0.4), P(kit, "#5a7a4a", 0.8))
        kit.box(f"fl.head{k}", (0.14, 0.14, 0.1), (x, 2.4, 0.64), P(kit, c, 0.6), bevel=0.03)
    # her window with curtains that open and close
    wy = -1.8
    ctx["curt"] = []
    for k, sy_ in enumerate((-1, 1)):
        c = kit.box(f"curt{k}", (0.05, 0.62, 1.2), (9.94, wy + sy_ * 0.31, 1.6), P(kit, "#fff1e0", 0.9))
        ctx["curt"].append((c, sy_))
    ctx["glow"] = kit.box("ortiz.glow", (0.03, 1.3, 1.2), (9.97, wy, 1.6), kit.emit("#ffd9a0", 1.2))
    # her dog (a small white dog, a prop of ours): body, head, ears, tail, legs. Faces -y at yaw 0
    d = kit.empty("dog", (0, 0, -50))
    wht = P(kit, "#f6f4f0", 0.9, 0.1)
    kit.box("dog.body", (0.26, 0.5, 0.26), (0, 0, 0.3), wht, d, bevel=0.07)
    ctx["dog_head"] = kit.empty("dog.headp", (0, -0.28, 0.45), d)
    kit.box("dog.head", (0.2, 0.22, 0.2), (0, -0.04, 0.0), wht, ctx["dog_head"], bevel=0.06)
    kit.box("dog.snout", (0.1, 0.1, 0.08), (0, -0.17, -0.03), wht, ctx["dog_head"], bevel=0.03)
    kit.box("dog.nose", (0.045, 0.03, 0.04), (0, -0.23, -0.01), P(kit, "#181416", 0.4), ctx["dog_head"])
    for sx in (-1, 1):
        kit.box(f"dog.ear{sx}", (0.05, 0.1, 0.14), (sx * 0.1, 0.0, 0.1), wht, ctx["dog_head"], bevel=0.02)
        kit.box(f"dog.eye{sx}", (0.03, 0.02, 0.04), (sx * 0.05, -0.15, 0.04), P(kit, "#181416", 0.3), ctx["dog_head"])
    ctx["dog_legs"] = []
    for sx in (-1, 1):
        for sy_ in (-1, 1):
            lg = kit.empty(f"dog.legp{sx}{sy_}", (sx * 0.09, sy_ * 0.18, 0.2), d)
            kit.box(f"dog.leg{sx}{sy_}", (0.07, 0.08, 0.2), (0, 0, -0.1), wht, lg, bevel=0.02)
            ctx["dog_legs"].append((lg, sy_))
    kit.box("dog.tail", (0.05, 0.05, 0.2), (0, 0.3, 0.42), wht, d, rot=(0.5, 0, 0), bevel=0.02)
    ctx["dog"] = d


# ------------------------------------------------------------------------------------------------ the Stander
# A far-too-tall person built of our blocks, 2.7 m, that is only ever seen as the snow settled on it: the hat brim,
# the crown, the shoulders and arms, the top of the head, a dusting down its front, and a face of snow with two
# dark hollows set low. Inside the snow it's empty air. One model, posed per shot by the "stander" cue.

SNOW_C = "#ffffff"


def dust(rng, box, cell=0.075, edge_p=0.9, front_p=0.34, side_p=0.2, back_p=0.1):
    """Small snow cubes clinging to the vertical faces of a box (cx, cy, cz, sx, sy, sz): thick along the edges, patchy
    across the faces, and denser on the front (-y), so the shape reads and the window still shows through."""
    cx, cy, cz, sx, sy, sz = box
    out = []

    def face(axis, sign, p_face):
        # tangential axes: for a y face (front/back) u = x, v = z; for an x face u = y, v = z
        if axis == "y":
            nu, nv = max(1, int(sx / cell)), max(1, int(sz / cell))
        else:
            nu, nv = max(1, int(sy / cell)), max(1, int(sz / cell))
        for i in range(nu):
            for j in range(nv):
                near_edge = i in (0, nu - 1) or j in (0, nv - 1)
                if rng.random() > (edge_p if near_edge else p_face):
                    continue
                k = 0.8 + 0.4 * rng.random()
                if axis == "y":
                    u = cx - sx / 2 + (i + 0.5) * sx / nu
                    out.append((cell * k, 0.05, cell * k, u, cy + sign * (sy / 2 + 0.01), cz - sz / 2 + (j + 0.5) * sz / nv))
                else:
                    u = cy - sy / 2 + (i + 0.5) * sy / nu
                    out.append((0.05, cell * k, cell * k, cx + sign * (sx / 2 + 0.01), u, cz - sz / 2 + (j + 0.5) * sz / nv))

    face("y", -1, front_p)
    face("y", +1, back_p)
    face("x", -1, side_p)
    face("x", +1, side_p)
    return out


def build_stander(kit, ctx):
    rng = np.random.default_rng(80)
    root = kit.empty("stander", (0, 0, -60))
    hips = kit.empty("stander.hips", (0, 0, 1.05), root)
    neck = kit.empty("stander.neck", (0, 0, 0.9), hips)         # at z 1.95
    snow = P(kit, SNOW_C, 0.95, 0.05)
    dark = P(kit, "#05070f", 0.5, 0.1)
    frost = ghost(kit, "stander.frost", "#b9d6fa", 0.5, emit=1.5)     # the person-shape the snow settled on
    groups = {}

    def grp(name, parent, loc):
        g = kit.empty(f"stander.g.{name}", loc, parent)
        groups[name] = g
        return g

    # legs: only a few clinging flecks, so the street shows through
    gl = grp("legs", root, (0, 0, 0.52))
    legs = []
    for sx in (-1, 1):
        legs += dust(rng, (sx * 0.2, 0, 0.0, 0.3, 0.32, 1.04), cell=0.08, edge_p=0.0, front_p=0.0, side_p=0.0, back_p=0.0)
        legs.append((0.34, 0.36, 0.05, sx * 0.2, 0, 0.5))               # snow on each knee-top shelf
        legs.append((0.1, 0.05, 0.3, sx * 0.2 + sx * 0.15, -0.16, 0.2))   # a thin streak down each shin
    multibox(kit, "stander.legs", legs, snow, gl)
    # torso and arms (ride the hips): snow ONLY on top surfaces and a few streaks; gaps everywhere else
    gb = grp("body", hips, (0, 0, 0.45))
    up = []
    up.append((0.24, 0.4, 0.07, -0.28, 0, 0.46))                         # a thin collar-bone dusting
    up.append((0.24, 0.4, 0.07, 0.28, 0, 0.46))
    up.append((0.07, 0.05, 0.4, -0.18, -0.235, 0.25))                    # a streak down the chest
    up.append((0.07, 0.05, 0.22, 0.2, -0.235, 0.3))
    up.append((0.09, 0.05, 0.12, 0.05, -0.235, -0.1))
    for sx in (-1, 1):
        up.append((0.3, 0.34, 0.06, sx * 0.6, 0, 0.3))                  # arm-top ledge near the shoulder
        up.append((0.32, 0.36, 0.06, sx * 0.6, 0, -0.55))               # forearm shelf: the elbow bend
        up.append((0.06, 0.05, 0.3, sx * 0.6 + sx * 0.1, -0.16, -0.1))  # one streak down the outer arm
        up.append((0.3, 0.34, 0.1, sx * 0.6, 0, -1.2))                  # a mitt of snow where each hand hangs
    multibox(kit, "stander.torso", up, snow, gb)
    # (no frost fill: it read as a solid body; the shape is held by the snow alone)
    # the shoulders: a thin slab from arm to arm, with a low cap on each arm
    gs = grp("shoulders", hips, (0, 0, 0.9))
    kit.box("stander.shoulders", (1.5, 0.5, 0.05), (0, 0, 0.025), snow, gs, bevel=0.015)
    for sx in (-1, 1):
        kit.box(f"stander.sh{sx}", (0.3, 0.34, 0.07), (sx * 0.6, 0, 0.07), snow, gs, bevel=0.02)
    # head and hat (ride the neck): the head is a snow-faced block, left a little shadowed; deep uneven eye hollows
    gh = grp("head", neck, (0, 0, 0.27))
    kit.box("stander.head", (0.5, 0.5, 0.5), (0, 0, 0), P(kit, "#dfe9f7", 0.95, 0.05), gh, bevel=0.03)
    kit.box("stander.brow", (0.54, 0.54, 0.07), (0, 0, 0.235), snow, gh, bevel=0.02)
    for sx in (-1, 1):
        kit.box(f"stander.cheek{sx}", (0.12, 0.05, 0.1), (sx * 0.17, -0.265, -0.2), snow, gh, bevel=0.01)
    kit.box("stander.eyeL", (0.085, 0.09, 0.2), (-0.15, -0.255, 0.12), dark, gh)
    kit.box("stander.eyeR", (0.07, 0.09, 0.16), (0.16, -0.255, 0.07), dark, gh)
    # one tall black mouth hanging open like a dropped jaw, from under the eyes down past the chin into the chest
    kit.box("stander.mouth", (0.22, 0.09, 0.6), (0.0, -0.255, -0.35), dark, gh)
    kit.box("stander.jawback", (0.3, 0.1, 0.3), (0.0, -0.2, -0.58), dark, gh)
    gt = grp("hat", neck, (0, 0, 0.55))
    # a ragged, narrow, tilted drift of snow rather than a roof
    for nm, sz, loc, rot in (("a", (0.6, 0.5, 0.08), (-0.03, 0.0, -0.02), (0.0, 0.16, 0.1)),
                              ("b", (0.34, 0.32, 0.12), (0.06, 0.02, 0.07), (0.0, 0.1, -0.3)),
                              ("c", (0.14, 0.14, 0.1), (-0.2, -0.1, 0.0), (0.2, 0.0, 0.5))):
        o = kit.box(f"stander.hat{nm}", sz, loc, snow, gt, bevel=0.015)
        o.rotation_euler = rot
    ctx["stander"] = (root, hips, neck)
    ctx["stander_groups"] = groups


STAND_REVEAL = {"hat": 0.08, "shoulders": 0.35, "head": 0.6, "body": 0.75, "legs": 0.88}
STAND_MELT = {"hat": 0.0, "shoulders": 0.12, "head": 0.18, "body": 0.35, "legs": 0.55}


# ------------------------------------------------------------------------------------------------ the globe


def mini_box(kit, name, size, loc, mat, parent):
    return kit.box(name, size, loc, mat, parent)


def build_globe(kit, ctx):
    g = kit.empty("globe", (GL[0], GL[1], SILL))
    base = P(kit, "#cfc7b6", 0.85, 0.15)
    kit.box("globe.base", (0.19, 0.19, 0.07), (0, 0, 0.035), base, g, bevel=0.012)
    kit.cyl("globe.collar", 0.092, 0.012, (0, 0, 0.076), P(kit, "#bfb6a2", 0.85), g, n=28)
    kit.sphere("globe.dome", DOME_R, (0, 0, 0.14), dome_glass(kit), g, seg=32)
    no_shadow(bpy.data.objects["globe.dome"])
    mini = kit.empty("globe.mini", (0, 0, 0.08), g)
    mini.scale = (GAUGE, GAUGE, GAUGE)
    ctx["mini"] = mini
    kit.cyl("mini.snow", 33.0, 0.4, (0, 0, 0.0), P(kit, "#f7fbff", 0.9), mini, n=40)
    kit.box("mini.road", (8.0, 62.0, 0.2), (0, 0, 0.28), P(kit, "#ffffff", 0.8), mini)
    for sx in (-1, 1):
        kit.box(f"mini.kerb{sx}", (0.8, 62.0, 0.3), (sx * 4.4, 0, 0.3), P(kit, "#c3d1e2", 0.8), mini)
    for i, y in enumerate(HOUSE_Y):
        for side in (-1, 1):
            c = (WEST_COL if side < 0 else EAST_COL)[i]
            xc = side * 13.0
            mini_box(kit, f"mini.h{side}{i}", (6.0, 6.4, 3.0), (xc, y, 1.7), P(kit, c, 0.6), mini)
            prism(kit, f"mini.r{side}{i}", xc - 3.4, xc + 3.4, y - 3.6, y + 3.6, 3.2, 4.9, P(kit, "#f5f9ff", 0.9), mini)
            kit.box(f"mini.g{side}{i}", (0.5, 1.6, 0.9), (side * 5.6, y, 0.7), P(kit, "#ffffff", 0.7), mini)
            kit.box(f"mini.m{side}{i}", (0.8, 0.8, 1.2), (side * 4.7, y + 1.3, 0.9), P(kit, "#4a7fd0" if (side < 0 and i == 4) else "#d0584a", 0.6), mini)
    # a tiny green truck at our curb
    kit.box("mini.truck", (2.0, 5.0, 1.4), (-3.4, 6.5, 0.9), P(kit, "#2f7a4f", 0.5), mini)
    # the tiny figure: a painted figure in a long frost-blue coat and a flat black hat, a cream face, two dots set low
    fig = kit.empty("mini.fig", (0, 0, 0.18), mini)
    coat = P(kit, "#8fb8e8", 0.45, 0.35)
    kit.box("fig.coat", (1.5, 0.95, 3.0), (0, 0, 1.5), coat, fig, bevel=0.12)
    for sx in (-1, 1):
        kit.box(f"fig.arm{sx}", (0.42, 0.62, 2.3), (sx * 0.95, 0, 1.75), coat, fig, bevel=0.08)
    kit.box("fig.head", (1.15, 1.15, 1.15), (0, 0, 3.55), P(kit, "#f6e7c8", 0.5), fig, bevel=0.15)
    for sx in (-1, 1):
        kit.box(f"fig.dot{sx}", (0.2, 0.06, 0.28), (sx * 0.27, -0.6, 3.3), P(kit, "#101014", 0.3), fig)
    kit.box("fig.brim", (1.9, 1.9, 0.16), (0, 0, 4.18), P(kit, "#16161c", 0.5), fig)
    kit.box("fig.crown", (1.05, 1.05, 0.5), (0, 0, 4.5), P(kit, "#16161c", 0.5), fig)
    ctx["fig"] = fig
    # the swirl: flakes that rise in a shake and settle
    rng = np.random.default_rng(7)
    fl = []
    mat = kit.emit("#ffffff", 3.0)
    for k in range(70):
        o = kit.box(f"swirl{k}", (0.0026, 0.0026, 0.0026), (0, 0, -9), mat, g)
        fl.append((o, rng.random(6) * 6.28, rng.random(), (rng.random() - 0.5) * 0.12, (rng.random() - 0.5) * 0.12))
    ctx["swirl"] = fl
    ctx["globe"] = g


# ------------------------------------------------------------------------------------------------ the rule meter: the minimap


def map_image(turn=False, size=640):
    """The globe from above: a pale disc, the white street, nine roofs a side, and (separately) the dot."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = size / 2
    d.ellipse((2, 2, size - 3, size - 3), fill=(46, 88, 150, 255))                       # a deep ice-blue rim
    d.ellipse((22, 22, size - 23, size - 23), fill=(190, 222, 248, 255))
    s = (size / 2 - 60) / 33.0
    d.rectangle((c - 4.3 * s, c - 31 * s, c + 4.3 * s, c + 31 * s), fill=(255, 255, 255, 255))
    for sx in (-1, 1):
        d.rectangle((c + sx * 4.6 * s - 3, c - 31 * s, c + sx * 4.6 * s + 3, c + 31 * s), fill=(150, 175, 205, 255))
    for i, y in enumerate(HOUSE_Y):
        for side in (-1, 1):
            col = (WEST_COL if side < 0 else EAST_COL)[i]
            rgb = tuple(int(col[k:k + 2], 16) for k in (1, 3, 5))
            x0 = c + side * 6.0 * s
            x1 = c + side * 17.0 * s
            yy = c - y * s
            d.rounded_rectangle((min(x0, x1), yy - 3.0 * s, max(x0, x1), yy + 3.0 * s), radius=5, fill=rgb + (255,), outline=(60, 80, 120, 255), width=3)
    # our house gets a darker outline
    yy = c
    d.rounded_rectangle((c - 17 * s, yy - 3.0 * s, c - 6 * s, yy + 3.0 * s), radius=5, outline=(20, 30, 70, 255), width=6)
    return im


def dot_image(turn=False, size=128):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((2, 2, size - 3, size - 3), fill=(255, 255, 255, 255))
    d.ellipse((14, 14, size - 15, size - 15), fill=(16, 28, 120, 255))
    if turn:
        for dy in (-14, 14):
            d.ellipse((24 - 8, size / 2 + dy - 8, 24 + 8, size / 2 + dy + 8), fill=(246, 231, 200, 255))
    else:
        for dx in (-14, 14):
            d.ellipse((size / 2 + dx - 8, size - 40 - 8, size / 2 + dx + 8, size - 40 + 8), fill=(246, 231, 200, 255))
    return im


def build_map(kit, ctx):
    cam = kit.OBJ["cam"]
    piv = kit.empty("map.pivot", (0, 0, -0.4), cam)
    m1 = img_mat(kit, "map", map_image(), 1.0)
    disc = img_plane(kit, "map.disc", 1.0, 1.0, m1, (0, 0, 0), piv)
    dot = img_plane(kit, "map.dot", 1.0, 1.0, img_mat(kit, "dot", dot_image(False), 1.0), (0, 0, 0.002), piv)
    dot2 = img_plane(kit, "map.dot2", 1.0, 1.0, img_mat(kit, "dot2", dot_image(True), 1.0), (0, 0, 0.002), piv)
    ctx["map"] = (piv, disc, dot, dot2)


def lens_at(ctx, story, tl, t):
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = ctx["cams"][shot["id"]]
    loc, tgt, lens, roll = bl_story.cam_at(spec, shot, t, {}, tl)
    return shot, loc, tgt, lens, roll


# ------------------------------------------------------------------------------------------------ small props


def build_props(kit, ctx):
    # the fog of breath on the glass: two soft white patches
    im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for cx, cy, r in ((190, 290, 120), (330, 270, 100), (260, 330, 80)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(240, 248, 255, 190))
    im = im.filter(ImageFilter.GaussianBlur(26))
    ctx["breath"] = img_plane(kit, "breath", 0.9, 0.9, img_mat(kit, "breath", im, 1.0), (-10.0, -1.4, 1.95), None,
                              (math.radians(90), 0, math.radians(90)))
    ctx["breath"].location = (-10.0, -1.4, 1.95)
    ctx["breath"].rotation_euler = (math.radians(90), 0, math.radians(-90))
    # the dropped satchel and the spilled mail
    bag = kit.empty("bagdrop", (0, 0, -40))
    kit.box("bag.body", (0.42, 0.14, 0.3), (0, 0, 0.18), P(kit, "#7a4f2e", 0.7), bag, bevel=0.04)
    kit.box("bag.flap", (0.44, 0.16, 0.1), (0, 0, 0.3), P(kit, "#5d3b22", 0.7), bag, bevel=0.03)
    ctx["bag"] = bag
    ctx["mail"] = []
    rng = np.random.default_rng(3)
    for k in range(9):
        o = kit.box(f"mail{k}", (0.24, 0.16, 0.012), (0, 0, -40), P(kit, "#ffffff", 0.6), None, bevel=0.0)
        ctx["mail"].append((o, rng.random() * 3, (rng.random() - 0.5) * 1.1, (rng.random() - 0.5) * 0.8))
    # steam off the dry patch
    ctx["steam"] = [kit.sphere(f"steam{k}", 0.14, (0, 0, -40), ghost(kit, "steam", "#ffffff", 0.35, 0.8), None, seg=8) for k in range(6)]
    for o in ctx["steam"]:
        no_shadow(o)
    # the white blur between the neighbours
    ctx["blur"] = kit.box("blur", (0.5, 0.3, 1.9), (0, 0, -40), ghost(kit, "blurm", "#ffffff", 0.3, 1.0), None, bevel=0.1)
    no_shadow(ctx["blur"])
    # a car for the swerve
    car(kit, ctx, "swerve", "#d94a4a", (0, 0, -60), 180)
    # the phone
    ph = kit.empty("phone", (0, 0, -40))
    kit.box("phone.body", (0.075, 0.016, 0.155), (0, 0, 0), P(kit, "#1b1d22", 0.4), ph, bevel=0.008)
    ctx["phone_img"] = {}
    for nm in ("snow", "cal"):
        pl = img_plane(kit, f"phone.scr.{nm}", 0.066, 0.14, img_mat(kit, f"scr{nm}", phone_screen(nm), 1.0), (0, -0.0095, 0), ph,
                       (math.radians(90), 0, 0))
        ctx["phone_img"][nm] = pl
    ctx["phone"] = ph
    # the cone lot (far away) for the test
    kit.box("lot", (40, 30, 0.1), (200, 0, -0.05), P(kit, "#7d838c", 0.8))
    for k in range(6):
        x = 194 + k * 2.4
        y = (-2.2, 2.2)[k % 2]
        kit.cyl(f"cone{k}", 0.22, 0.55, (x, y, 0.28), P(kit, "#ff7a1a", 0.5), None, n=10, r2=0.05)
        kit.cyl(f"cone{k}b", 0.19, 0.08, (x, y, 0.3), P(kit, "#ffffff", 0.5), None, n=10)
    kit.box("lot.line", (30, 0.12, 0.01), (200, 5.2, 0.01), P(kit, "#f2d65a", 0.6))
    car(kit, ctx, "testcar", "#e8eef5", (203, 0.6, 0), 90)
    kit.box("lot.sun", (60, 60, 0.02), (200, 0, -0.04), P(kit, "#e6efe0", 0.9))


def phone_screen(kind, size=(264, 560)):
    im = Image.new("RGBA", size, (240, 247, 255, 255))
    d = ImageDraw.Draw(im)
    w, h = size
    if kind == "snow":
        c = (w / 2, h / 2)
        for a in range(0, 180, 30):
            r = 90
            dx, dy = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
            d.line((c[0] - dx, c[1] - dy, c[0] + dx, c[1] + dy), fill=(70, 150, 230, 255), width=14)
        d.line((c[0] - 70, c[1] - 70, c[0] + 70, c[1] + 70), fill=(220, 40, 50, 255), width=26)
        d.line((c[0] - 70, c[1] + 70, c[0] + 70, c[1] - 70), fill=(220, 40, 50, 255), width=26)
    else:
        d.rounded_rectangle((40, 150, w - 40, h - 150), radius=18, fill=(255, 255, 255, 255), outline=(220, 70, 70, 255), width=14)
        d.rectangle((40, 150, w - 40, 250), fill=(220, 70, 70, 255))
        for i in range(3):
            for j in range(3):
                d.ellipse((70 + i * 60, 290 + j * 56, 100 + i * 60, 320 + j * 56), fill=(120, 140, 170, 255))
        d.ellipse((190 - 6, 290 + 56 * 2 - 6, 190 + 36, 290 + 56 * 2 + 36), outline=(220, 70, 70, 255), width=8)
    return im


# ------------------------------------------------------------------------------------------------ the cast's extras


def _head(name):
    return bpy.data.objects[f"{name}.headg"]


def dress_gus(kit, name="gus"):
    c = rig.CHARS[name]
    hg = _head(name)
    R, H = faces.HEAD_R, faces.HEAD_H
    wh = kit.plastic("#f4f4f2", 0.8)
    # a thick white mustache under the nose, and white brows' worth of wispy side hair
    kit.box(f"{name}.must", (0.62, 0.16, 0.14), (0, -R + 0.03, -0.12), wh, hg, bevel=0.05)
    for sx in (-1, 1):
        kit.box(f"{name}.mustw{sx}", (0.2, 0.14, 0.2), (sx * 0.32, -R + 0.07, -0.18), wh, hg, bevel=0.05)
        kit.box(f"{name}.side{sx}", (0.1, 0.6, 0.5), (sx * (R + 0.01), 0.1, 0.08), wh, hg, bevel=0.04)
    # a brown flat cap he tips
    cap = kit.plastic("#7a5230", 0.7)
    kit.box(f"{name}.capb", (2 * R + 0.14, 2 * R + 0.14, 0.3), (0, 0.0, H / 2 + 0.06), cap, hg, bevel=0.1)
    kit.box(f"{name}.capt", (2 * R + 0.22, 2 * R + 0.2, 0.1), (0, -0.04, H / 2 + 0.23), cap, hg, bevel=0.06)
    kit.box(f"{name}.capv", (1.0, 0.45, 0.07), (0, -R - 0.18, H / 2 + 0.05), kit.plastic("#5d3d22", 0.7), hg, bevel=0.03)
    # cardigan: a cream placket and wooden toggles down the front
    kit.box(f"{name}.placket", (0.5, 0.04, 1.9), (0, -0.505, 1.0), kit.plastic("#f2e6c8", 0.7), c.upper, bevel=0.01)
    for k in range(3):
        kit.box(f"{name}.tog{k}", (0.12, 0.05, 0.2), (0.3, -0.54, 1.5 - k * 0.55), kit.plastic("#8a5d2e", 0.5), c.upper, bevel=0.02)
    for k in range(2):
        kit.box(f"{name}.pocket{k}", (0.5, 0.03, 0.4), (-0.7 if k == 0 else 0.7, -0.51, 0.35), kit.plastic("#27693f", 0.7), c.upper)


def dress_me(kit, name="me"):
    c = rig.CHARS[name]
    sn = kit.plastic("#ffffff", 0.5)
    # the snowflake-block patch: a plus and a diagonal cross of small blocks on the chest
    for dx, dz, sx_, sz_ in ((0, 0, 0.62, 0.14), (0, 0, 0.14, 0.62), (0.0, 0.0, 0.44, 0.1), (0.0, 0.0, 0.1, 0.44)):
        r = 0.0 if sx_ != 0.44 and sz_ != 0.44 else math.radians(45)
        kit.box(f"{name}.flake{sx_}{sz_}", (sx_, 0.03, sz_), (-0.5, -0.515, 1.35), sn, c.upper, rot=(0, r, 0), bevel=0.02)
    kit.box(f"{name}.pocket", (1.1, 0.04, 0.5), (0, -0.51, 0.3), kit.plastic("#238a87", 0.7), c.upper, bevel=0.02)
    for sx in (-1, 1):
        kit.box(f"{name}.cord{sx}", (0.06, 0.04, 0.5), (sx * 0.22, -0.515, 1.62), kit.plastic("#ffffff", 0.5), c.upper)


def dress_mailman(kit, name="mailman"):
    c = rig.CHARS[name]
    kit.box(f"{name}.sat", (1.1, 0.55, 0.9), (1.15, 0.0, 0.45), kit.plastic("#7a4f2e", 0.7), c.torso, bevel=0.07)
    kit.box(f"{name}.strapx", (0.2, 1.06, 1.9), (0.1, 0.0, 1.0), kit.plastic("#5d3b22", 0.7), c.torso, rot=(0, 0.5, 0), bevel=0.02)


def dress_mug(kit, name="n1"):
    c = rig.CHARS[name]
    arm = c.P["arm1"]
    kit.box(f"{name}.mug", (0.5, 0.5, 0.55), (0, -0.45, -1.75), kit.plastic("#f2f2f2", 0.4), arm, bevel=0.05)
    kit.box(f"{name}.coffee", (0.4, 0.4, 0.04), (0, -0.45, -1.47), kit.plastic("#4a2c1c", 0.3), arm)


def dress_clipboard(kit, name="examiner"):
    c = rig.CHARS[name]
    arm = c.P["arm1"]
    kit.box(f"{name}.board", (0.7, 0.06, 0.95), (0, -0.55, -1.5), kit.plastic("#a8743c", 0.6), arm, bevel=0.03)
    kit.box(f"{name}.paper", (0.58, 0.04, 0.8), (0, -0.59, -1.5), kit.plastic("#ffffff", 0.6), arm)


def dress_keys(kit, name="gus"):
    c = rig.CHARS[name]
    arm = c.P["arm1"]
    kit.cyl(f"{name}.ring", 0.16, 0.03, (0, -0.55, -1.98), kit.plastic("#d9a441", 0.3), arm, n=14)
    for k, a_ in enumerate((0.0, 0.9)):
        kit.box(f"{name}.key{k}", (0.1, 0.5, 0.04), (0.1 * math.sin(a_), -0.85, -1.98), kit.plastic("#e0b84a", 0.3), arm, rot=(0, 0, a_ * 0.4))


def dress_brush(kit, name="me"):
    c = rig.CHARS[name]
    arm = c.P["arm1"]
    kit.box(f"{name}.brush", (0.2, 0.2, 0.5), (0, -0.4, -1.9), kit.plastic("#8a5d2e", 0.5), arm, bevel=0.03)
    kit.box(f"{name}.bristle", (0.34, 0.34, 0.3), (0, -0.4, -2.25), kit.plastic("#f2d27a", 0.8), arm, bevel=0.05)


# ------------------------------------------------------------------------------------------------ lights and the time of day

# gains on each light's base (the day values). "world" is [strength, colour]; "sun_c" the sun's colour.
MODES = {
    "day": {"sun": 1.0, "room": 0.75, "lamp": 0.4, "porch": 0.0, "street": 0.0, "corner": 0.0, "globe": 1.0,
            "world": [1.0, "#9ad6ff"], "sun_c": "#fff0d8"},
    "snow": {"sun": 0.3, "room": 0.85, "lamp": 0.5, "porch": 0.0, "street": 0.0, "corner": 1.0, "globe": 1.0,
             "world": [1.2, "#cfe3f4"], "sun_c": "#e6f0ff"},
    "dusk": {"sun": 0.08, "room": 1.0, "lamp": 1.0, "porch": 0.6, "street": 0.5, "corner": 0.0, "globe": 1.0,
             "world": [0.55, "#476bc0"], "sun_c": "#8fa8ff"},
    "dim": {"sun": 0.04, "room": 0.28, "lamp": 0.55, "porch": 0.5, "street": 0.8, "corner": 0.0, "globe": 1.2,
            "world": [0.42, "#3a5aa8"], "sun_c": "#7f9be8", "fill": 1.0, "rim": 1.0},
    "night": {"sun": 0.04, "room": 0.4, "lamp": 0.6, "porch": 1.0, "street": 1.0, "corner": 0.0, "globe": 1.0,
              "world": [0.4, "#34549e"], "sun_c": "#7f9be8", "fill": 1.0, "rim": 1.0},
}


def build_lights(kit, ctx):
    sun = kit.light("sun", "SUN", (30, -14, 38), 3.2, "#fff0d8", size=0.3)
    kit.aim(sun, (0, 0, 0))
    kit.light("room", "AREA", (-13.5, 0.3, 2.82), 420, "#ffe2b0", size=3.0)
    kit.light("lamp", "POINT", (-11.2, 2.9, 1.15), 70, "#ffd7a0", size=0.3)
    kit.light("porch", "POINT", (-9.6, -1.6, 2.5), 320, "#ffb54d", size=0.25)
    st = kit.light("street", "SPOT", (-5.1, -3.4, 4.4), 2600, "#d6e8ff", size=0.3, spot=95, blend=0.5)
    kit.aim(st, (-8.2, -0.8, 1.1))
    gl = kit.light("globe", "SPOT", (-11.35, 0.95, 1.75), 26, "#ffffff", size=0.1, spot=26, blend=0.7)
    kit.aim(gl, (GL[0], GL[1], SILL + 0.1))
    fl = kit.light("fill", "SPOT", (-12.6, -0.4, 2.7), 90, "#cfe6ff", size=0.3, spot=40, blend=0.6)
    kit.aim(fl, (-9.5, -1.4, 1.9))
    rl = kit.light("rim", "SPOT", (-8.4, -5.2, 1.3), 1500, "#6fa6ff", size=0.2, spot=45, blend=0.5)
    kit.aim(rl, (-8.85, -1.4, 1.8))
    co = kit.light("corner", "SPOT", (0, 56, 55), 260000, "#fff0c0", size=1.0, spot=50, blend=0.4)
    kit.aim(co, (0, 40, 0))


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    ctx = {"inited": False}
    kit.OBJ["cam"].data.clip_start = 0.008
    build_ground(kit, ctx)
    build_street(kit, ctx)
    build_house_ours(kit, ctx)
    build_ortiz(kit, ctx)
    build_truck(kit, ctx)
    build_stander(kit, ctx)
    build_globe(kit, ctx)
    build_map(kit, ctx)
    build_props(kit, ctx)
    build_lights(kit, ctx)
    # the falling snow
    rng = np.random.default_rng(11)
    fm = kit.emit("#ffffff", 2.2)
    ctx["flakes"] = []
    for k in range(380):
        o = kit.box(f"flake{k}", (0.035, 0.035, 0.035), (0, 0, -100), fm, None)
        no_shadow(o)
        ctx["flakes"].append((o, rng.random(), rng.random(), rng.random(), 0.8 + 0.9 * rng.random(), rng.random()))
    ctx["world"] = bpy.context.scene.world
    return ctx


# ------------------------------------------------------------------------------------------------ animate


def fig_state(tl, t):
    cs = _cues(tl, "fig")
    pos = tween(cs, "pos", t, [0.0, 0.0])
    return pos


def car_path(c, t):
    """A car coming up the road and swerving round the middle: returns (x, y, yaw) or None when it isn't driving."""
    u = (t - c["t"]) / c["dur"]
    if not 0 <= u <= 1:
        return None
    y0, y1 = c.get("y", [-16.0, 18.0])
    lane = c.get("lane", 1.9)
    cx, cy = c.get("around", [0.0, 0.0])
    def at(uu):
        y = y0 + (y1 - y0) * uu
        x = lane + (c.get("swerve", 2.1) * math.exp(-((y - cy) / 2.6) ** 2)) * (1 if lane > 0 else -1)
        return x, y
    x, y = at(u)
    xn, yn = at(min(1.0, u + 0.01))
    xp, yp = at(max(0.0, u - 0.01))
    dx, dy = xn - xp, yn - yp
    yaw = math.degrees(math.atan2(-dx, dy)) + 180 if False else math.degrees(math.atan2(dx, -dy))
    if y1 < y0:
        pass
    return x, y, yaw


def animate(kit, story, tl, t, ctx):
    over = {}
    if not ctx["inited"]:
        dress_gus(kit)
        dress_me(kit)
        dress_mailman(kit)
        dress_mug(kit)
        dress_clipboard(kit)
        dress_keys(kit)
        dress_brush(kit)
        ctx["cams"] = polish.cam_specs(story, tl, polish.spec(story))
        ctx["inited"] = True
    shot, cloc, ctgt, lens, roll = lens_at(ctx, story, tl, t)
    # --- the time of day: gains on every light, the sky and the sun, crossfaded (never under 0.3 s)
    cs = _cues(tl, "mode")
    cur = _last(cs, t)
    prev_name = "day"
    for c in cs:
        if c is cur:
            break
        prev_name = c["set"]
    if cur is None:
        cur_name, u = "day", 1.0
    else:
        cur_name = cur["set"]
        u = ss((t - cur["t"]) / max(0.3, cur.get("dur", 0.3)))
    A, B = MODES[prev_name], MODES[cur_name]
    for k in ("sun", "room", "lamp", "porch", "street", "corner", "globe", "fill", "rim"):
        over[k] = lerp(A.get(k, 0.0), B.get(k, 0.0), u)
    pc = ramped(_cues(tl, "porch"), "on", t, 1.0, 0.3)
    over["porch"] *= pc
    sc = kit.col(A["sun_c"])[:3]
    sd = kit.col(B["sun_c"])[:3]
    kit.LIGHTS["sun"]["light"].color = tuple(lerp(a, b, u) for a, b in zip(sc, sd))
    wa, wb = A["world"], B["world"]
    bg = ctx["world"].node_tree.nodes["Background"]
    bg.inputs["Strength"].default_value = lerp(wa[0], wb[0], u)
    ca, cb = kit.col(wa[1])[:3], kit.col(wb[1])[:3]
    bg.inputs["Color"].default_value = (*[lerp(a, b, u) for a, b in zip(ca, cb)], 1)
    # --- the falling snow
    snow_on = bool((_last(_cues(tl, "snow"), t) or {"on": False}).get("on", False))
    fw = V(ctgt) - V(cloc)
    fw.normalize()
    right = fw.cross(V((0, 0, 1)))
    if right.length < 1e-4:
        right = V((1, 0, 0))
    right.normalize()
    cl = V(cloc)
    for o, r1, r2, r3, sp, ph in ctx["flakes"]:
        if not snow_on:
            o.location = (0, 0, -100)
            continue
        d = 0.7 + 9.5 * r1 * r1
        lat = (r2 * 2 - 1) * d * 0.62 + 0.12 * math.sin(t * 1.3 + ph * 9)
        hh = d * 1.0 + 0.6
        v = hh - ((t * sp + ph * hh * 2) % (2 * hh))
        p = cl + fw * d + right * lat + V((0, 0, v))
        if p.z < 0.06 or p.y > 33 or (p.x < -9.8 and abs(p.y) < 4.0 and p.x > -18) or p.x > 60 or p.x < -60:
            o.location = (0, 0, -100)
            continue
        o.location = (p.x, p.y, p.z)
        o.rotation_euler = (t * 0.7 + ph * 6, t * 0.5, ph * 6)
    # --- the dry patch
    c = _last(_cues(tl, "spot"), t)
    sp_ = ctx["spot"]
    if c and c.get("pos") is not None:
        sp_.location = (c["pos"][0], c["pos"][1], 0.065 if c["pos"][0] > -7 else 0.14)
        sp_.hide_render = False
        for ch in sp_.children:
            ch.hide_render = False
    else:
        sp_.location = (0, 0, -50)
    # --- steam off it
    c = _last(_cues(tl, "steam"), t)
    on = bool(c and c.get("on"))
    for k, o in enumerate(ctx["steam"]):
        if on:
            sx, sy = sp_.location.x, sp_.location.y
            ph = (t * 0.45 + k / 6.0) % 1.0
            o.location = (sx + 0.18 * math.sin(k * 2.3 + t * 0.8), sy + 0.15 * math.cos(k * 1.7 + t * 0.6), 0.12 + 0.8 * ph)
            sc_ = 0.6 + 1.2 * ph
            o.scale = (sc_, sc_, sc_ * 1.3)
        else:
            o.location = (0, 0, -50)
    # --- the Stander
    root, hips, neck = ctx["stander"]
    cst = _cues(tl, "stander")
    c = _last(cst, t)
    if c and not c.get("hidden"):
        pos = tween([x for x in cst if "pos" in x], "pos", t, c["pos"])
        bend = ramped(cst, "bend", t, 0.0, 0.3)
        hb = ramped(cst, "head", t, 0.0, 0.3)
        reveal = ramped(cst, "reveal", t, 1.0, 0.3)
        melt = ramped(cst, "melt", t, 0.0, 0.3)
        root.location = (pos[0], pos[1], 0.0 if pos[0] > -7.3 else 0.03)
        root.rotation_euler = (0, 0, math.radians(c.get("yaw", -90)))
        hips.rotation_euler = (math.radians(bend), 0, 0)
        neck.rotation_euler = (math.radians(hb), 0, 0)
        for nm, g_ in ctx["stander_groups"].items():
            u_in = ss((reveal - STAND_REVEAL[nm]) / 0.14)
            u_out = 1.0 - ss((melt - STAND_MELT[nm]) / 0.25)
            sc_ = u_in * u_out
            g_.scale = (max(sc_, 0.001),) * 3
    else:
        root.location = (0, 0, -60)
    # --- the globe: where it is, a tilt, a swirl
    g = ctx["globe"]
    gcs = _cues(tl, "globe")
    gp = tween(gcs, "pos", t, [GL[0], GL[1], SILL])
    gt = tween(gcs, "tilt", t, [0.0, 0.0])
    g.location = tuple(gp)
    g.rotation_euler = (math.radians(gt[0]), math.radians(gt[1]), 0)
    swc = _last(_cues(tl, "swirl"), t)
    un = (t - swc["t"]) if swc else 99.0
    amp = math.exp(-max(0.0, un) / 1.5) if 0 <= un < 6.0 else 0.0
    for k, (o, ph, r, ox, oy) in enumerate(ctx["swirl"]):
        if amp < 0.02:
            o.location = (0, 0, -9)
            continue
        rr = 0.012 + 0.06 * r
        a = ph[0] + (2.4 + ph[1] * 0.6) * un * (0.5 + amp * 0.5)
        x = rr * math.cos(a) * amp + ox * (1 - amp)
        y = rr * math.sin(a) * amp + oy * (1 - amp)
        z = 0.14 + (0.5 + 0.5 * math.sin(ph[2] + un * (2.0 + ph[3] * 0.5))) * 0.06 * amp - (1 - amp) * 0.058 + 0.02 * amp * (ph[4] - 0.5)
        o.location = (x, y, z)
    # --- the tiny figure
    fp = fig_state(tl, t)
    fig = ctx["fig"]
    fig.location = (fp[0], fp[1], 0.18)
    turn = ramped(_cues(tl, "turn"), "on", t, 0.0, 0.8)
    fig.rotation_euler = (0, 0, math.radians(-90 * turn))
    # --- the rule meter: the globe's own minimap, top-left of every shot
    piv, disc, dot, dot2 = ctx["map"]
    half_h = 0.4 * 12.0 / lens
    half_w = half_h * 9 / 16
    grow = ramped(_cues(tl, "mapgrow"), "v", t, 0.0, 0.3)
    dia = lerp(0.215, 0.94, grow) * 2 * half_w
    cx = lerp(-half_w + 0.2 * 2 * half_w, 0.0, grow)
    cy = lerp(half_h - 0.145 * 2 * half_h, 0.0, grow)
    piv.location = (cx, cy, -0.4)
    piv.scale = (dia, dia, 1.0)
    k_ = (0.5 - 60.0 / 640.0) / 33.0
    dot.scale = dot2.scale = (0.115, 0.115, 1.0)
    for o in (dot, dot2):
        o.location = (fp[0] * k_, fp[1] * k_, 0.002)
    dot.hide_render = turn > 0.5
    dot2.hide_render = turn <= 0.5
    # --- the breath on the glass
    ctx["breath"].location = (-10.0, -1.4, 1.95) if ramped(_cues(tl, "fog"), "on", t, 0.0, 0.6) > 0.02 else (0, 0, -50)
    fb = ramped(_cues(tl, "fog"), "on", t, 0.0, 0.6)
    ctx["breath"].scale = (0.6 + 0.4 * fb, 0.6 + 0.4 * fb, 1)
    # --- Mrs. Ortiz's curtains
    op = ramped(_cues(tl, "curtains"), "open", t, 0.0, 0.3)
    for c_, sy_ in ctx["curt"]:
        c_.scale = (1, lerp(1.0, 0.18, op), 1)
        c_.location = (9.94, -1.8 + sy_ * (0.62 - 0.31 * lerp(1.0, 0.18, op)) , 1.6)
    ctx["glow"].hide_render = op < 0.05
    # --- the dog
    d = ctx["dog"]
    c = _last(_cues(tl, "dog"), t)
    if c and not c.get("hidden"):
        p = tween([x for x in _cues(tl, "dog") if "pos" in x], "pos", t, c["pos"])
        d.location = (p[0], p[1], p[2] if len(p) > 2 else 0.0)
        d.rotation_euler = (0, 0, math.radians(c.get("yaw", 0)))
        brace = c.get("pose") == "brace"
        d.rotation_euler = (math.radians(-14) if brace else 0, 0, math.radians(c.get("yaw", 0)))
        ctx["dog_head"].rotation_euler = (math.radians(-35) if brace else 0, 0, 0)
        for lg, sy_ in ctx["dog_legs"]:
            lg.rotation_euler = (math.radians(-28 if (brace and sy_ < 0) else 0), 0, 0)
    else:
        d.location = (0, 0, -50)
    # --- the truck and the cars
    tr = ctx["truck"]
    tcs = [x for x in _cues(tl, "truck") if "pos" in x]
    td = [x for x in _cues(tl, "tdrive") if car_path(x, t) is not None]
    if td:
        x, y, yaw = car_path(td[-1], t)
        tr.location = (x, y, 0.0)
        tr.rotation_euler = (0, 0, math.radians(yaw))
    elif tcs:
        p = tcs[0]["pos"]
        yw = tcs[0].get("yaw", 0.0)
        for x_ in tcs:
            if x_["t"] <= t + 1e-9:
                p, yw = x_["pos"], x_.get("yaw", 0.0)
        tr.location = (p[0], p[1], 0.0)
        tr.rotation_euler = (0, 0, math.radians(yw))
    sw = ctx["cars"]["swerve"]
    cc = [x for x in _cues(tl, "car") if car_path(x, t) is not None]
    if cc:
        x, y, yaw = car_path(cc[-1], t)
        sw.location = (x, y, 0)
        sw.rotation_euler = (0, 0, math.radians(yaw))
    else:
        sw.location = (0, 0, -60)
    # --- the spilled mail and the dropped bag
    mc = _last(_cues(tl, "mail"), t)
    for k, (o, ph, ox, oy) in enumerate(ctx["mail"]):
        if mc and mc.get("n", 0) > k:
            u_ = ss((t - mc["t"]) / 0.45)
            o.location = (mc["pos"][0] + ox * u_, mc["pos"][1] + oy * u_, 0.07 + 0.6 * (1 - u_) * (1 - u_) if mc.get("fall") else 0.07)
            o.rotation_euler = (0, 0, ph + u_ * 2.5)
        else:
            o.location = (0, 0, -40)
    bc = _last(_cues(tl, "bag"), t)
    ctx["bag"].location = (bc["pos"][0], bc["pos"][1], 0.05) if bc and bc.get("pos") else (0, 0, -40)
    if bc and bc.get("pos"):
        ctx["bag"].rotation_euler = (0, 0, math.radians(bc.get("yaw", 20)))
    # --- the white blur
    bl_ = _last(_cues(tl, "blur"), t)
    if bl_ and 0 <= t - bl_["t"] < bl_["dur"]:
        u_ = (t - bl_["t"]) / bl_["dur"]
        a_, b_ = bl_["from"], bl_["to"]
        ctx["blur"].location = (lerp(a_[0], b_[0], u_), lerp(a_[1], b_[1], u_), 1.05)
    else:
        ctx["blur"].location = (0, 0, -40)
    # --- the phone
    ph_ = _last(_cues(tl, "phone"), t)
    if ph_ and ph_.get("on"):
        ctx["phone"].location = tuple(ph_["pos"])
        ctx["phone"].rotation_euler = tuple(math.radians(v) for v in ph_.get("rot", [0, 0, 0]))
        for nm, pl in ctx["phone_img"].items():
            pl.hide_render = nm != ph_.get("state", "snow")
    else:
        ctx["phone"].location = (0, 0, -40)
    # --- sitting: legs straight out in front, for the armchair, the flowerbed and the truck seat
    for who in ("gus", "ortiz", "me"):
        sit = False
        for k in tl["acting"].get(who, []):
            if "sit" in k and k["t"] <= t + 1e-9:
                sit = bool(k["sit"])
        if sit:
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (math.radians(-90), 0, 0)
    return over
