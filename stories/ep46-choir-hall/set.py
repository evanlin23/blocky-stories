"""The choir hall (ep46): a hillside village in early winter, one narrow cottage, and the village hall where a choir of
twelve chairs sits eleven strong. Built from kit.py's parts; nothing here is shared with another story's set. There is no
text anywhere in the set.

Places (metres). The STREET is the origin: the lane runs down the hill along -y (x -2 .. 2), left cottages at x < 0
facing +x, right cottages at x > 0 facing -x, one plot every 7 m (plot k spans y -7k .. -7k-7, gate at its middle).
Our house is left plot 2 (y -17.5), Ron's is left plot 3. The KITCHEN is a room at x = 40, the BEDROOM and its landing at
x = 60, the HALL at x = 100 (HX): stage end at y = -10.5, back wall (door and window) at y = +9, gravel path and lamp
post outside it.

THE GRIN (the creature). One model, built once and posed by the acting keys: an ordinary singer from the same blocks, in
the choir robe, with a pale waxy face, no drawn eyes (two tiny glints) and a bare neck far too long. What is wrong is its mouth: a
thin dark seam, upturned at the corners, that goes on round the sides of the head and meets itself at the back. It has no cord and no beads.
It is never seen moving: every change of pose is across a cut.

Cues read here: tod, lt (one light's level, with a ramp), bead_off / bead_on, cord, cordfade, bulge, scarf, door, hdoor, c12
(the twelfth chair's yaw), turned (the other eleven chairs turn to face it), rows, audience, bunting, grin.
"""

from __future__ import annotations

import math
import random

import bpy
from mathutils import Vector as V
from PIL import ImageDraw

from blocky import acting as ac
from blocky import faces

S = 0.34
HX = 100.0
KX, KY = 40.0, 0.0
BX, BY = 60.0, 0.0
FOGC = "#c8d4de"

TOD = {
    "morning": dict(sun=3.6, dir=(-0.55, 0.6, 0.42), sunc="#ffd9b0", sky=1.25, hor="#d6e4ee", zen="#8fb4d8",
                    fogc="#cfdbe4", fogd=0.008, lamp=0.0, win=0.0, stars=0.0),
    "dusk": dict(sun=1.8, dir=(0.6, -0.5, 0.2), sunc="#ff9c60", sky=0.8, hor="#e0a088", zen="#4f6094",
                 fogc="#9a90a6", fogd=0.012, lamp=0.5, win=0.6, stars=0.0),
    "night": dict(sun=0.9, dir=(-0.3, 0.45, 0.6), sunc="#9fb4ff", sky=0.45, hor="#2d3a58", zen="#0e1526",
                  fogc="#1c2433", fogd=0.03, lamp=1.0, win=1.0, stars=1.0),
    "dawn": dict(sun=1.6, dir=(0.7, 0.5, 0.3), sunc="#cfd8f0", sky=0.85, hor="#b9c2d0", zen="#7389ad",
                 fogc="#a9b4c2", fogd=0.018, lamp=0.3, win=0.5, stars=0.0),
    "inside": dict(sun=0.0, dir=(0, 0, 1), sunc="#ffffff", sky=0.25, hor="#1c2433", zen="#1c2433",
                   fogc="#20242e", fogd=0.0, lamp=0.0, win=0.0, stars=0.0),
}
# every named light and its nominal full strength (the story's lt cues set a level 0..n; the level defaults are DEF)
DEF = {"hall_house": 0.0, "riser": 0.0, "grin_key": 0.0, "grin_rim": 0.0, "hall_low": 0.0, "door_wedge": 0.0, "back_wash": 0.0,
       "kitchen_day": 0.0, "kitchen_lamp": 0.0, "bed_lamp": 0.0, "landing": 0.0, "mum_key": 0.0, "front_key": 0.0}


# ------------------------------------------------------------------------------------------------ helpers
def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def _last(cs, t):
    cs = [c for c in cs if c["t"] <= t + 1e-9]
    return cs[-1] if cs else None


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def eased(cs, key, t, default):
    level = prev = default
    for c in cs:
        if c["t"] > t + 1e-9 or key not in c:
            continue
        prev, level = level, c[key]
        d = float(c.get("dur", 0.0))
        if d > 0 and t < c["t"] + d and isinstance(level, (int, float)) and isinstance(prev, (int, float)):
            level = prev + (level - prev) * ss((t - c["t"]) / d)
    return level


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lin(c):
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def mixc(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


def show(objs, on):
    for o in objs:
        for oo in [o] + list(o.children_recursive):
            oo.hide_render = not on


def pbr(kit, name, hexc, rough=0.6, metal=0.0, spec=0.4, noise=None, bump=0.0, emit=None, emit_s=0.0):
    """A Principled material through kit's fog. noise = (scale, dark factor, rough variation)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = spec
            break
    if emit:
        b.inputs["Emission Color"].default_value = kit.col(emit)
        b.inputs["Emission Strength"].default_value = emit_s
    if noise:
        tc = N.new("ShaderNodeTexCoord")
        nz = N.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = noise[0]
        nz.inputs["Detail"].default_value = 6.0
        L.new(tc.outputs["Object"], nz.inputs["Vector"])
        ramp = N.new("ShaderNodeValToRGB")
        c = kit.col(hexc)
        ramp.color_ramp.elements[0].position = 0.3
        ramp.color_ramp.elements[0].color = (c[0] * noise[1], c[1] * noise[1], c[2] * noise[1], 1)
        ramp.color_ramp.elements[1].position = 0.7
        ramp.color_ramp.elements[1].color = c
        L.new(nz.outputs["Fac"], ramp.inputs["Fac"])
        L.new(ramp.outputs["Color"], b.inputs["Base Color"])
        if bump:
            bp = N.new("ShaderNodeBump")
            bp.inputs["Strength"].default_value = bump
            bp.inputs["Distance"].default_value = 0.03
            L.new(nz.outputs["Fac"], bp.inputs["Height"])
            L.new(bp.outputs["Normal"], b.inputs["Normal"])
    m.diffuse_color = kit.col(hexc)
    kit._fogged(m, b.outputs[0])
    return m


def bx(kit, name, size, loc, mat, parent=None, rot=(0, 0, 0), bevel=0.0):
    return kit.box(name, size, loc, mat, parent, rot, bevel=bevel)


def prism(kit, name, w, d, h, mat, loc, parent=None):
    """A gable roof: ridge along y, w across x, d along y, h high (centred on loc at its base)."""
    x, y = w / 2, d / 2
    v = [(-x, -y, 0), (x, -y, 0), (0, -y, h), (-x, y, 0), (x, y, 0), (0, y, h)]
    f = [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)]
    return kit.mesh_obj(name, v, f, mat, parent, loc)


def curve_pts(fn, n=240):
    pts = [fn(i / n) for i in range(n + 1)]
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    return pts, cum


def resample(fn, count, margin=0.5):
    pts, cum = curve_pts(fn)
    out = []
    for i in range(count):
        target = cum[-1] * (i + margin) / count
        j = next(k for k, c in enumerate(cum) if c >= target)
        out.append(pts[j])
    return out


# ------------------------------------------------------------------------------------------------ materials
def materials(kit):
    M = {}
    M["frost"] = pbr(kit, "frost ground", "#cfd9d6", 0.95, noise=(1.6, 0.78, 0.0), bump=0.1)
    M["lane"] = kit.cobbles("#4a4f58", "#8a8c90", "#25272c", 3.2, 0.1, "lane cobbles")
    M["render"] = pbr(kit, "render", "#e9e0cc", 0.9, noise=(0.8, 0.88, 0.0))
    M["render2"] = pbr(kit, "render2", "#dcd6c4", 0.9, noise=(0.9, 0.88, 0.0))
    M["slate"] = pbr(kit, "slate", "#4a5560", 0.7, noise=(5.0, 0.7, 0.0), bump=0.2)
    M["frostroof"] = pbr(kit, "frostroof", "#aab6bd", 0.8, noise=(5.0, 0.8, 0.0))
    M["hedge"] = pbr(kit, "hedge", "#44624a", 0.95, noise=(6.0, 0.55, 0.0), bump=0.4)
    M["hedgefrost"] = pbr(kit, "hedgefrost", "#e2ece9", 0.95)
    M["sage"] = pbr(kit, "sage", "#8fa58a", 0.5)
    M["cream"] = pbr(kit, "cream", "#efe6cf", 0.5)
    M["duck"] = pbr(kit, "duck", "#9cc2bd", 0.5)
    M["plum"] = pbr(kit, "plumdoor", "#6e4a62", 0.5)
    M["wood"] = pbr(kit, "wood", "#6b4a2e", 0.7, noise=(7.0, 0.7, 0.1))
    M["brick"] = kit.bricks("#8a4a38", "#6e3b2e", "#4a4540", 1.2, "chimney bricks")
    M["pane_day"] = pbr(kit, "pane day", "#34455a", 0.1, spec=0.6)
    M["pane_lit"] = pbr(kit, "pane lit", "#3a3026", 0.6, emit="#ffc880", emit_s=0.0)
    M["post"] = pbr(kit, "post metal", "#23282b", 0.5, metal=0.6)
    M["mug"] = pbr(kit, "mug", "#c8553a", 0.4)
    M["gravel"] = pbr(kit, "gravel", "#8e897f", 0.95, noise=(9.0, 0.6, 0.0), bump=0.5)
    M["wall_out"] = pbr(kit, "hall wall out", "#a99f88", 0.9, noise=(1.0, 0.8, 0.0))
    # hall
    M["pine"] = kit.planks("#c79a62", "#a87c46", 1.0, "X", "hall pine")
    M["pine_y"] = kit.planks("#c79a62", "#a87c46", 1.0, "Y", "hall pine y")
    M["hallwall"] = pbr(kit, "hallwall", "#ece2c8", 0.92)
    M["ceil"] = pbr(kit, "ceil", "#d9cfb6", 0.95)
    M["beam"] = pbr(kit, "beam", "#6b4a2e", 0.8)
    M["curtain"] = pbr(kit, "curtain", "#4c3038", 0.95, noise=(3.0, 0.55, 0.0))
    M["chair"] = pbr(kit, "chair wood", "#b07a42", 0.6, noise=(8.0, 0.75, 0.1))
    M["chair2"] = pbr(kit, "chair frame", "#7d5a36", 0.6)
    M["enamel"] = pbr(kit, "enamel", "#e8e4d4", 0.22, spec=0.7)
    M["flex"] = pbr(kit, "flex", "#141414", 0.5)
    M["bulb"] = pbr(kit, "bulb", "#ffe2b0", 0.4, emit="#ffd8a0", emit_s=9.0)
    M["stroke"] = pbr(kit, "stroke", "#7a1f2e", 0.9)
    M["scarf"] = pbr(kit, "scarf", "#d9a23a", 0.9, noise=(14.0, 0.7, 0.0))
    M["stand"] = pbr(kit, "stand", "#25272a", 0.5, metal=0.5)
    M["bunting_a"] = pbr(kit, "bunt a", "#d96b5a", 0.8)
    M["bunting_b"] = pbr(kit, "bunt b", "#e8c25a", 0.8)
    M["bunting_c"] = pbr(kit, "bunt c", "#5a90c8", 0.8)
    M["bunting_d"] = pbr(kit, "bunt d", "#7cb07a", 0.8)
    # rooms
    M["tile"] = kit.checker("#b9a98a", "#8e7e66", 2.0, "kitchen tile", 0.5)
    M["plaster"] = pbr(kit, "plaster", "#d8cfae", 0.95)
    M["plaster2"] = pbr(kit, "plaster2", "#c9b79c", 0.95)
    M["cabinet"] = pbr(kit, "cabinet", "#8fa58a", 0.55)
    M["table"] = kit.planks("#a9794a", "#8a5f38", 1.4, "X", "table wood")
    M["white"] = pbr(kit, "white", "#ece8de", 0.5)
    M["clockface"] = pbr(kit, "clockface", "#efe9d8", 0.4)
    M["hand"] = pbr(kit, "hand", "#1c1c1c", 0.5)
    M["floorb"] = kit.planks("#7b5636", "#5e3f27", 1.0, "X", "bedroom boards")
    M["quilt"] = pbr(kit, "quilt", "#6b4a6e", 0.9, noise=(10.0, 0.7, 0.0))
    M["pillow"] = pbr(kit, "pillow", "#e6e2d6", 0.9)
    M["lampshade"] = pbr(kit, "lampshade", "#f3d9a8", 0.5, emit="#ffc880", emit_s=1.6)
    M["cup"] = pbr(kit, "cup", "#d8d4c6", 0.3)
    M["tea"] = pbr(kit, "tea", "#3a2a1a", 0.2)
    M["bead_lit"] = bead_mat(kit, "bead_lit", 1.0)
    M["bead_dark"] = bead_mat(kit, "bead_dark", 0.0)
    return M


BEAD_AMBER = "#ffb648"
BEAD_SMOKE = "#3a3430"
BEAD_LIT_S = 1.5


def bead_mat(kit, name, lit):
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(BEAD_SMOKE)
    b.inputs["Roughness"].default_value = 0.12
    b.inputs["Emission Color"].default_value = kit.col(BEAD_AMBER)
    b.inputs["Emission Strength"].default_value = BEAD_LIT_S * lit
    kit._fogged(m, b.outputs[0])
    return m


# ------------------------------------------------------------------------------------------------ the street
def cottage(kit, M, k, side, ctx):
    """One render cottage facing the lane. side -1 is the left (x < 0), +1 the right."""
    pal = [("render", "sage", "slate"), ("render2", "cream", "slate"), ("render", "duck", "slate"),
           ("render2", "plum", "slate"), ("render", "cream", "slate")]
    wall, door, roof = pal[(k + (2 if side > 0 else 0)) % 5]
    cy = -7 * k - 3.5
    root = kit.empty(f"cot{side}{k}", (side * (5.6 + 2.3), cy, 0), None, (0, 0, 0 if side < 0 else math.pi))
    bx(kit, f"cot{side}{k}.body", (4.6, 5.0, 3.1), (0, 0, 1.55), M[wall], root)
    prism(kit, f"cot{side}{k}.roof", 5.4, 5.8, 1.7, M["slate"], (0, 0, 3.1), root)
    ridge = kit.box(f"cot{side}{k}.ridgefrost", (0.3, 5.8, 0.06), (0, 0, 4.82), M["frostroof"], root)
    bx(kit, f"cot{side}{k}.chim", (0.7, 0.8, 1.6), (0.3, 1.8, 4.2), M["brick"], root)
    bx(kit, f"cot{side}{k}.door", (0.1, 1.0, 2.1), (2.33, 0, 1.05), M[door], root, bevel=0.02)
    bx(kit, f"cot{side}{k}.step", (0.7, 1.5, 0.12), (2.7, 0, 0.06), M["gravel"], root)
    for sy in (-1.6, 1.6):
        bx(kit, f"cot{side}{k}.win{sy}", (0.06, 1.0, 1.1), (2.32, sy, 1.7), ctx["panes"][k % 2], root)
        bx(kit, f"cot{side}{k}.winf{sy}", (0.1, 1.2, 0.1), (2.34, sy, 2.3), M["white"], root)
        bx(kit, f"cot{side}{k}.wins{sy}", (0.14, 1.2, 0.08), (2.35, sy, 1.1), M["white"], root)
        bx(kit, f"cot{side}{k}.winm{sy}", (0.08, 0.06, 1.1), (2.35, sy, 1.7), M["white"], root)
    return root, cy


def gate(kit, M, name, x, y, side, hexmat):
    """A picket gate across a gap in the front hedge, with two posts. A mug on the near post."""
    root = kit.empty(name, (x, y, 0))
    for sy in (-0.62, 0.62):
        bx(kit, f"{name}.post{sy}", (0.16, 0.16, 1.15), (0, sy, 0.57), M["white"], root, bevel=0.02)
    for i in range(7):
        bx(kit, f"{name}.pk{i}", (0.05, 0.1, 0.9), (0, -0.48 + i * 0.16, 0.5), hexmat, root, bevel=0.01)
    bx(kit, f"{name}.rail1", (0.04, 1.0, 0.07), (-0.02, 0, 0.3), hexmat, root)
    bx(kit, f"{name}.rail2", (0.04, 1.0, 0.07), (-0.02, 0, 0.75), hexmat, root)
    return root


def build_street(kit, M, ctx):
    kit.plane("ground", (260, 260), (0, -40, -0.001), M["frost"])
    kit.box("lane", (3.9, 90, 0.03), (0, -30, 0.012), M["lane"])
    ctx["panes"] = [pbr(kit, f"pane{i}", "#34455a", 0.1, spec=0.6, emit="#ffc880", emit_s=0.0) for i in range(2)]
    ctx["win_mats"] = list(ctx["panes"])
    gmats = [M["sage"], M["cream"], M["duck"], M["cream"], M["sage"]]
    for side in (-1, 1):
        for k in range(-1, 6):
            if k >= 0:
                cottage(kit, M, k, side, ctx)
            cy = -7 * k - 3.5
            if k < 0:
                continue
            gx = side * 3.0
            # front hedge in two pieces either side of the gate
            for lo, hi in ((cy + 0.7, cy + 3.5), (cy - 3.5, cy - 0.7)):
                h = kit.box(f"hedge{side}{k}{lo}", (0.8, hi - lo, 1.0), (gx, (lo + hi) / 2, 0.5), M["hedge"], bevel=0.12)
                kit.box(f"hedgef{side}{k}{lo}", (0.62, hi - lo - 0.1, 0.07), (gx, (lo + hi) / 2, 1.0), M["hedgefrost"], bevel=0.02)
            gate(kit, M, f"gate{side}{k}", gx, cy, side, gmats[(k + (2 if side > 0 else 0)) % 5])
            # hedge between plots
            yb = -7 * k
            kit.box(f"hedgeb{side}{k}", (2.6, 0.7, 1.25), (side * 4.3, yb, 0.62), M["hedge"], bevel=0.12)
            kit.box(f"hedgebf{side}{k}", (2.4, 0.5, 0.07), (side * 4.3, yb, 1.25), M["hedgefrost"], bevel=0.02)
            # garden path from gate to door
            kit.box(f"gpath{side}{k}", (2.6, 0.9, 0.03), (side * 4.3, cy, 0.016), M["gravel"])
    # the mug stays on the first right gatepost and a second on a left post
    mug = kit.cyl("mug", 0.06, 0.1, (3.0, -3.5 - 0.62, 1.2), M["mug"], None, n=14)
    ctx["mug"] = mug
    # street lamps for the night
    ctx["lamps"] = []
    for i, (lx, ly) in enumerate(((2.3, -10.0), (-2.3, -20.0), (2.3, -31.0), (-2.3, -2.0))):
        kit.cyl(f"lamp{i}.pole", 0.06, 3.6, (lx, ly, 1.8), M["post"], None, n=10)
        kit.box(f"lamp{i}.head", (0.34, 0.34, 0.4), (lx, ly, 3.75), M["post"], None, bevel=0.04)
        bulb = kit.box(f"lamp{i}.bulb", (0.24, 0.24, 0.28), (lx, ly, 3.72), ctx["lampbulb"], None, bevel=0.03)
        L = kit.light(f"lamp{i}", "POINT", (lx, ly, 3.5), 900.0, "#e8b060", size=0.15)
        ctx["lamps"].append(L)
    # stars
    rng = random.Random(7)
    stars = []
    sm = bpy.data.materials.new("star")
    sm.use_nodes = True
    nt = sm.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 9.0
    em.inputs["Color"].default_value = kit.col("#dfe8ff")
    nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    for i in range(140):
        az = rng.uniform(0, 2 * math.pi)
        el = rng.uniform(math.radians(18), math.radians(80))
        r = 90.0
        p = (r * math.cos(el) * math.cos(az), -30 + r * math.cos(el) * math.sin(az), r * math.sin(el))
        s = kit.sphere(f"star{i}", rng.uniform(0.1, 0.22), p, sm, seg=6)
        stars.append(s)
    ctx["stars"] = stars


# ------------------------------------------------------------------------------------------------ kitchen
def build_kitchen(kit, M, ctx):
    x0, y0 = KX, KY
    kit.box("k.floor", (4.6, 4.6, 0.1), (x0, y0, -0.05), M["tile"])
    kit.box("k.ceil", (4.6, 4.6, 0.1), (x0, y0, 2.65), M["plaster"])
    kit.box("k.wall_w", (0.2, 4.6, 2.7), (x0 - 2.3, y0, 1.3), M["plaster"])
    kit.box("k.wall_e", (0.2, 4.6, 2.7), (x0 + 2.3, y0, 1.3), M["plaster"])
    kit.box("k.wall_s", (4.6, 0.2, 2.7), (x0, y0 - 2.3, 1.3), M["plaster"])
    # north wall with a window (x -0.8 .. 0.8, z 0.95 .. 2.15)
    kit.box("k.wn_l", (1.5, 0.2, 2.7), (x0 - 1.55, y0 + 2.3, 1.3), M["plaster"])
    kit.box("k.wn_r", (1.5, 0.2, 2.7), (x0 + 1.55, y0 + 2.3, 1.3), M["plaster"])
    kit.box("k.wn_b", (1.6, 0.2, 0.95), (x0, y0 + 2.3, 0.47), M["plaster"])
    kit.box("k.wn_t", (1.6, 0.2, 0.55), (x0, y0 + 2.3, 2.42), M["plaster"])
    kw = pbr(kit, "kwin", "#a9a49a", 0.8)       # a dimmer off-white, so the sunlit frame never clips
    kit.box("k.wsill", (1.9, 0.4, 0.06), (x0, y0 + 2.28, 0.97), kw)
    kit.box("k.wbar", (0.06, 0.06, 1.2), (x0, y0 + 2.3, 1.55), kw)
    kit.box("k.wbar2", (1.6, 0.06, 0.06), (x0, y0 + 2.3, 2.02), kw)
    # a round table and two chairs
    kit.cyl("k.table", 0.8, 0.07, (x0 - 0.2, y0 - 0.3, 0.78), M["table"], None, n=32)
    kit.cyl("k.tleg", 0.07, 0.75, (x0 - 0.2, y0 - 0.3, 0.38), M["chair2"], None, n=10)
    kit.cyl("k.tfoot", 0.35, 0.05, (x0 - 0.2, y0 - 0.3, 0.03), M["chair2"], None, n=20)
    ctx["kchairs"] = []
    for i, (cx, cy, yw) in enumerate(((x0 - 0.2, y0 + 0.62, 0), (x0 - 0.2, y0 - 1.22, 180))):
        g = kit.empty(f"kchair{i}", (cx, cy, 0), None, (0, 0, math.radians(yw)))
        bx(kit, f"kchair{i}.seat", (0.46, 0.46, 0.05), (0, 0, 0.45), M["chair"], g, bevel=0.01)
        for lx, ly in ((-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2)):
            bx(kit, f"kchair{i}.l{lx}{ly}", (0.04, 0.04, 0.45), (lx, ly, 0.22), M["chair2"], g)
        bx(kit, f"kchair{i}.back", (0.46, 0.04, 0.5), (0, 0.22, 0.72), M["chair"], g, bevel=0.01)
        ctx["kchairs"].append(g)
    # a clock with no numbers on the east wall
    kit.cyl("k.clock", 0.24, 0.05, (x0 + 2.18, y0 - 0.6, 1.85), M["clockface"], None, rot=(0, math.pi / 2, 0), n=28)
    bx(kit, "k.hand1", (0.02, 0.025, 0.17), (x0 + 2.15, y0 - 0.6, 1.9), M["hand"])
    bx(kit, "k.hand2", (0.02, 0.17, 0.025), (x0 + 2.15, y0 - 0.52, 1.85), M["hand"])
    # counter with cabinets along the south wall
    kit.box("k.cab", (3.2, 0.6, 0.9), (x0 + 0.3, y0 - 1.95, 0.45), M["cabinet"], bevel=0.02)
    kit.box("k.top", (3.3, 0.66, 0.05), (x0 + 0.3, y0 - 1.95, 0.92), M["white"])
    kit.cyl("k.cup", 0.06, 0.09, (x0 - 0.45, y0 - 0.25, 0.86), M["cup"], None, n=14)
    kit.cyl("k.tea", 0.05, 0.01, (x0 - 0.45, y0 - 0.25, 0.9), M["tea"], None, n=14)
    kit.cyl("k.cup2", 0.06, 0.09, (x0 + 0.12, y0 - 0.4, 0.86), M["cup"], None, n=14)
    kit.cyl("k.tea2", 0.05, 0.01, (x0 + 0.12, y0 - 0.4, 0.9), M["tea"], None, n=14)
    # a stove ring and a kettle on the counter
    kit.box("k.ring", (0.5, 0.45, 0.03), (x0 + 0.95, y0 - 1.95, 0.945), M["post"], None, bevel=0.01)
    kit.cyl("k.kettle", 0.16, 0.22, (x0 + 0.95, y0 - 1.95, 1.07), M["enamel"], None, n=20, r2=0.12)
    kit.box("k.spout", (0.14, 0.06, 0.06), (x0 + 0.95, y0 - 1.78, 1.1), M["enamel"], None, rot=(0, 0, 0.4))
    kit.box("k.khandle", (0.04, 0.22, 0.14), (x0 + 0.95, y0 - 2.12, 1.14), M["post"], None, bevel=0.01)
    # the hall, far up the hill, seen through the kitchen window at night (cue farwin)
    far = []
    far.append(kit.box("far.body", (11.0, 2.0, 7.0), (x0 + 1.3, 26.2, 3.5), pbr(kit, "far hall", "#1a1d28", 0.9)))
    fm = pbr(kit, "far glow", "#ffcf8a", 0.6, emit="#ffb860", emit_s=22.0)
    far.append(kit.box("far.glow", (4.6, 0.1, 2.6), (x0 + 1.3, 25.1, 3.3), fm))
    for i in range(5):
        far.append(kit.box(f"far.bar{i}", (0.07, 0.12, 2.6), (x0 - 0.7 + i * 1.15, 25.05, 3.3), pbr(kit, "far bar", "#3a2c22", 0.9)))
    far.append(kit.box("far.barh", (4.6, 0.12, 0.07), (x0 + 1.3, 25.05, 3.3), pbr(kit, "far bar", "#3a2c22", 0.9)))
    ctx["far"] = far
    kit.light("kitchen_day", "AREA", (x0, y0 + 3.4, 1.6), 90.0, "#cfe0f4", (math.pi / 2, 0, math.pi), size=1.4)
    kit.light("kitchen_lamp", "POINT", (x0 - 0.2, y0 - 0.3, 2.1), 150.0, "#ffd49a", size=0.3)
    # the table lamp shade, hanging
    kit.cyl("k.shade", 0.22, 0.2, (x0 - 0.2, y0 - 0.3, 2.15), M["lampshade"], None, n=20, r2=0.1)
    kit.cyl("k.shadecord", 0.01, 0.6, (x0 - 0.2, y0 - 0.3, 2.5), M["flex"], None, n=6)


# ------------------------------------------------------------------------------------------------ bedroom and landing
def build_bedroom(kit, M, ctx):
    x0 = BX
    # bedroom y -2.2 .. 2 ; the landing y 2 .. 4.6 ; the door at x = 60 in the wall y = 2
    kit.box("b.floor", (4.6, 7.0, 0.1), (x0, 1.2, -0.05), M["floorb"])
    kit.box("b.ceil", (4.6, 7.0, 0.1), (x0, 1.2, 2.65), M["plaster2"])
    kit.box("b.wall_w", (0.2, 7.0, 2.7), (x0 - 2.3, 1.2, 1.3), M["plaster2"])
    kit.box("b.wall_e", (0.2, 7.0, 2.7), (x0 + 2.3, 1.2, 1.3), M["plaster2"])
    kit.box("b.wall_s", (4.6, 0.2, 2.7), (x0, -2.3, 1.3), M["plaster2"])
    kit.box("b.wall_n", (4.6, 0.2, 2.7), (x0, 4.7, 1.3), M["plaster2"])
    # the dividing wall at y = 2 with a door gap x 59.4 .. 60.6
    kit.box("b.div_l", (1.7, 0.2, 2.7), (x0 - 1.45, 2.0, 1.3), M["plaster2"])
    kit.box("b.div_r", (1.7, 0.2, 2.7), (x0 + 1.45, 2.0, 1.3), M["plaster2"])
    kit.box("b.div_t", (1.2, 0.2, 0.6), (x0, 2.0, 2.4), M["plaster2"])
    kit.box("b.frame_l", (0.08, 0.26, 2.1), (x0 - 0.62, 2.0, 1.05), M["white"])
    kit.box("b.frame_r", (0.08, 0.26, 2.1), (x0 + 0.62, 2.0, 1.05), M["white"])
    # the door: hinged on its west edge, opening into the room (toward -y)
    hinge = kit.empty("b.doorhinge", (x0 - 0.58, 2.0, 0))
    bx(kit, "b.doorleaf", (1.12, 0.06, 2.05), (0.56, 0.0, 1.03), M["white"], hinge, bevel=0.01)
    bx(kit, "b.doorknob", (0.06, 0.12, 0.06), (1.0, 0.0, 1.0), M["stand"], hinge)
    ctx["bdoor"] = hinge
    # bed along the west wall, headboard south
    kit.box("b.bed", (1.7, 2.1, 0.5), (x0 - 1.35, -0.8, 0.25), M["quilt"], bevel=0.04)
    kit.box("b.pillow", (1.0, 0.45, 0.14), (x0 - 1.35, -1.6, 0.56), M["pillow"], bevel=0.05)
    kit.box("b.table", (0.5, 0.5, 0.5), (x0 - 2.0, 0.55, 0.25), M["chair"], bevel=0.02)
    kit.cyl("b.lampshade", 0.17, 0.26, (x0 - 2.0, 0.55, 0.66), M["lampshade"], None, n=20, r2=0.1)
    kit.light("bed_lamp", "POINT", (x0 - 1.95, 0.55, 0.7), 60.0, "#ffbe78", size=0.1)
    kit.light("landing", "AREA", (x0, 3.4, 2.5), 90.0, "#b4c4e8", (0, 0, 0), size=0.8)
    kit.light("mum_key", "AREA", (x0 + 0.4, 0.4, 1.9), 55.0, "#ffd0a0", (0, 0, 0), size=0.6)


# ------------------------------------------------------------------------------------------------ the hall
def hall_chair(kit, M, name, loc, yaw_deg, scale=1.0):
    g = kit.empty(name, loc, None, (0, 0, math.radians(yaw_deg)))
    bx(kit, f"{name}.seat", (0.46, 0.44, 0.04), (0, 0, 0.45), M["chair"], g, bevel=0.01)
    for lx, ly in ((-0.2, -0.19), (0.2, -0.19), (-0.2, 0.19), (0.2, 0.19)):
        bx(kit, f"{name}.l{lx}{ly}", (0.035, 0.035, 0.45), (lx, ly, 0.225), M["chair2"], g)
    for lx in (-0.2, 0.2):
        bx(kit, f"{name}.p{lx}", (0.035, 0.035, 0.5), (lx, 0.21, 0.72), M["chair2"], g)
    bx(kit, f"{name}.rail1", (0.46, 0.03, 0.1), (0, 0.21, 0.92), M["chair"], g)
    bx(kit, f"{name}.rail2", (0.46, 0.03, 0.1), (0, 0.21, 0.74), M["chair"], g)
    return g


# riser: three steps; (z top, y centre of its chair row)
TWELFTH_X = HX - 1.65
STEPS = [(0.9, -8.65), (0.6, -7.15), (0.3, -5.65)]
CHX = [-1.65, -0.55, 0.55, 1.65]


def chair_slots():
    """Twelve (x, y, z) in hall metres: the twelfth chair is the far-right (-x) one on the top step; singers 1..11 take the rest."""
    slots = []
    for z, y in STEPS:
        for dx in CHX:
            slots.append((HX + dx, y, z))
    twelfth = slots[0]
    return twelfth, slots[1:]


def wall_x(kit, name, mat, y, x0, x1, h, holes, thick=0.3):
    """A wall along x at y with rectangular holes [(xa, xb, za, zb)]."""
    xs = sorted(holes, key=lambda hh: hh[0])
    cur = x0
    for i, (xa, xb, za, zb) in enumerate(xs):
        if xa > cur:
            bx(kit, f"{name}.s{i}", (xa - cur, thick, h), ((cur + xa) / 2, y, h / 2), mat)
        if za > 0:
            bx(kit, f"{name}.b{i}", (xb - xa, thick, za), ((xa + xb) / 2, y, za / 2), mat)
        if zb < h:
            bx(kit, f"{name}.t{i}", (xb - xa, thick, h - zb), ((xa + xb) / 2, y, (zb + h) / 2), mat)
        cur = xb
    if cur < x1:
        bx(kit, f"{name}.e", (x1 - cur, thick, h), ((cur + x1) / 2, y, h / 2), mat)


def build_hall(kit, M, ctx):
    ylo, yhi = -12.0, 9.0
    ym = (ylo + yhi) / 2
    kit.box("h.floor", (10.4, yhi - ylo + 0.4, 0.2), (HX, ym, -0.1), M["pine"])
    kit.box("h.ceil", (10.4, yhi - ylo + 0.4, 0.2), (HX, ym, 5.1), M["ceil"])
    for i in range(6):
        kit.box(f"h.beam{i}", (10.4, 0.25, 0.3), (HX, ylo + 2.0 + i * 3.4, 4.85), M["beam"])
    # the low side window on the west wall (y -5.2 .. -2.2, z 0.95 .. 2.25), small square panes, seen from the gravel strip
    wy0, wy1, wz0, wz1 = -5.2, -2.2, 0.95, 2.25
    wx = HX - 5.15
    kit.box("h.ww_s", (0.3, wy0 - ylo, 5.0), (wx, (ylo + wy0) / 2, 2.5), M["hallwall"])
    kit.box("h.ww_n", (0.3, yhi - wy1, 5.0), (wx, (wy1 + yhi) / 2, 2.5), M["hallwall"])
    kit.box("h.ww_b", (0.3, wy1 - wy0, wz0), (wx, (wy0 + wy1) / 2, wz0 / 2), M["hallwall"])
    kit.box("h.ww_t", (0.3, wy1 - wy0, 5.0 - wz1), (wx, (wy0 + wy1) / 2, (wz1 + 5.0) / 2), M["hallwall"])
    for i in range(7):
        kit.box(f"h.wwv{i}", (0.1, 0.05, wz1 - wz0), (wx, wy0 + i * (wy1 - wy0) / 6, (wz0 + wz1) / 2), M["white"])
    for j in range(4):
        kit.box(f"h.wwh{j}", (0.1, wy1 - wy0, 0.05), (wx, (wy0 + wy1) / 2, wz0 + j * (wz1 - wz0) / 3), M["white"])
    kit.box("h.wwsill", (0.4, wy1 - wy0 + 0.2, 0.06), (wx - 0.2, (wy0 + wy1) / 2, wz0 - 0.03), M["white"])
    kit.box("h.wall_e", (0.3, yhi - ylo, 5.0), (HX + 5.15, ym, 2.5), M["hallwall"])
    # the stage-end wall has one high window behind the twelfth chair (seen from the gravel strip outside)
    wall_x(kit, "h.wall_s", M["hallwall"], ylo - 0.15, HX - 5.3, HX + 5.3, 5.0, [(HX - 3.4, HX + 1.9, 1.7, 4.4)])
    for i, bxo in enumerate((-3.4, -2.2, -0.5, 0.7, 1.9)):
        kit.box(f"h.sb{i}", (0.05, 0.1, 2.7), (HX + bxo, ylo - 0.05, 3.05), M["white"])
    kit.box("h.sbh", (5.3, 0.1, 0.05), (HX - 0.75, ylo - 0.05, 3.7), M["white"])
    # the back wall (y = +9): a door (x HX-3.3 .. HX-1.7) and a window (x HX+1.9 .. HX+3.7, z 1.5 .. 3.2)
    wall_x(kit, "h.wall_n", M["hallwall"], yhi + 0.15, HX - 5.3, HX + 5.3, 5.0,
           [(HX - 3.3, HX - 1.7, 0.0, 2.4), (HX + 1.9, HX + 3.7, 1.5, 3.2)])
    wall_x(kit, "h.wall_n_out", M["wall_out"], yhi + 0.36, HX - 5.3, HX + 5.3, 5.0,
           [(HX - 3.3, HX - 1.7, 0.0, 2.4), (HX + 1.9, HX + 3.7, 1.5, 3.2)], thick=0.1)
    # the window frame: a cross of bars and a sill
    for i in range(3):
        kit.box(f"h.wb{i}", (0.05, 0.1, 1.7), (HX + 2.4 + i * 0.6, yhi + 0.2, 2.35), M["white"])
    kit.box("h.wbh", (1.8, 0.1, 0.05), (HX + 2.8, yhi + 0.2, 2.35), M["white"])
    kit.box("h.wsill", (2.0, 0.4, 0.08), (HX + 2.8, yhi + 0.1, 1.5), M["white"])
    # the door: hinged on its +x edge, opening inward
    hinge = kit.empty("h.doorhinge", (HX - 1.7, yhi + 0.15, 0))
    bx(kit, "h.doorleaf", (1.6, 0.08, 2.35), (-0.8, 0.0, 1.18), M["wood"], hinge, bevel=0.01)
    ctx["hdoor"] = hinge
    # high small-pane windows on the side walls, dim blue at night
    ctx["hpanes"] = []
    pm = pbr(kit, "hall pane", "#243048", 0.2, emit="#7f98c8", emit_s=0.2)
    for sx in (-1, 1):
        for i in range(4):
            yy = -6.0 + i * 4.4
            kit.box(f"h.wp{sx}{i}", (0.06, 1.2, 1.3), (HX + sx * 4.97, yy, 3.4), pm)
            kit.box(f"h.wpb{sx}{i}", (0.1, 0.05, 1.3), (HX + sx * 4.95, yy, 3.4), M["white"])
            kit.box(f"h.wph{sx}{i}", (0.1, 1.2, 0.05), (HX + sx * 4.95, yy, 3.4), M["white"])
    # the stage end: curtains, riser, backboard, strokes
    ctx["curwin"] = []
    for i in range(14):
        cb = kit.box(f"h.cur{i}", (0.8, 0.28 + 0.12 * (i % 2), 4.5), (HX - 4.55 + i * 0.7, ylo + 0.2 + 0.06 * (i % 2), 2.35), M["curtain"], bevel=0.1)
        if i in (3, 4, 5, 6, 7, 8, 9):
            ctx["curwin"].append(cb)
    kit.box("h.curtop", (10.0, 0.5, 0.4), (HX, ylo + 0.3, 4.7), M["curtain"])
    ry0, ry1 = -9.4, -4.9
    for k, (z, yc) in enumerate(STEPS):
        kit.box(f"h.step{k}", (7.6, 1.5, z), (HX - 0.5, yc, z / 2), M["pine_y"])
    kit.box("h.back", (7.6, 0.06, 0.7), (HX - 0.5, -9.5, 1.25), M["pine"])
    # eleven short upright maroon strokes scratched into the backboard, one behind each singer; the stretch behind the
    # twelfth chair (the far -x end) is bare
    for i in range(11):
        kit.box(f"h.stroke{i}", (0.05, 0.03, 0.32), (HX - 1.15 + i * 0.25, -9.55, 1.25), M["stroke"])
    # the twelve chairs
    twelfth, rest = chair_slots()
    ctx["c12"] = hall_chair(kit, M, "ch12", twelfth, 180)
    ctx["c12pos"] = twelfth
    ctx["chairs"] = []
    for i, p in enumerate(rest):
        ctx["chairs"].append((hall_chair(kit, M, f"ch{i}", p, 180), p))
    # the hall lamp over the riser: a long flex and an enamel shade
    lx, ly = HX - 0.9, -7.4
    kit.cyl("h.flex", 0.012, 1.3, (lx, ly, 4.4), M["flex"], None, n=6)
    kit.cyl("h.shade", 0.5, 0.34, (lx, ly, 3.62), M["enamel"], None, n=28, r2=0.12)
    kit.sphere("h.bulb", 0.11, (lx, ly, 3.55), M["bulb"], seg=10)
    # the lamp's spot (the shade is a cone so its light goes down), a side key and rim for the Grin
    sp = kit.light("riser", "SPOT", (lx, ly, 3.5), 1500.0, "#ffe6c4", spot=75, blend=0.6, size=0.1)
    kit.aim(sp, (HX - 0.4, -7.2, 0.8))
    kit.light("camfill", "POINT", (0, 0, 0), 1.0, "#a8bce8", size=0.3)
    kit.light("front_key", "POINT", (HX - 3.2, -0.2, 2.9), 300.0, "#ffd9a0", size=0.4)
    k = kit.light("grin_key", "SPOT", (twelfth[0] + 0.6, -4.4, 0.2), 700.0, "#a9c6f2", spot=44, blend=0.7, size=0.15)
    kit.aim(k, (twelfth[0], twelfth[1], twelfth[2] + 1.9))
    r = kit.light("grin_rim", "SPOT", (twelfth[0] - 1.2, -10.8, 4.2), 1400.0, "#cfe4ff", spot=26, blend=0.5, size=0.1)
    kit.aim(r, (twelfth[0], twelfth[1], twelfth[2] + 2.0))
    # a wash from behind the riser that lights the backboard strokes and the backs of the heads (cued)
    bw = kit.light("back_wash", "SPOT", (HX - 0.4, -11.5, 3.9), 900.0, "#ffd9b0", spot=70, blend=0.7, size=0.3)
    kit.aim(bw, (HX - 0.4, -8.2, 1.6))
    # the general hall light: three area panels in the ceiling; a very low fill for the dark hall
    for i, yy in enumerate((-6.5, 0.0, 6.0)):
        kit.light(f"hall_house{i}", "AREA", (HX, yy, 4.9), 900.0, "#ffe4b8", (0, 0, 0), size=3.5)
    kit.light("hall_low", "AREA", (HX, 0.0, 4.9), 120.0, "#8fa0c8", (0, 0, 0), size=6.0)
    # the ceiling panels light the room but are never seen as pale rectangles in frame
    for _n in ("hall_house0", "hall_house1", "hall_house2", "hall_low"):
        _o = kit.LIGHTS[_n]["obj"] if _n in kit.LIGHTS else bpy.data.objects.get(_n)
        if _o is not None:
            _o.visible_camera = False
    # the streetlight through the open door: a narrow spot from the lamp post outside
    kit.light("door_wedge", "SPOT", (HX - 2.5, 10.8, 2.0), 9000.0, "#d4def5", spot=20, blend=0.4, size=0.15)
    kit.aim(kit.LIGHTS["door_wedge"]["obj"], (HX - 0.4, -7.2, 0.9))
    # outside: gravel, the lamp post, a path
    kit.box("h.ground", (120, 120, 0.1), (HX, 20, -0.06), M["gravel"])
    kit.box("h.path", (2.2, 28, 0.03), (HX - 2.5, 24, 0.03), M["lane"])
    kit.cyl("h.post", 0.07, 3.8, (HX - 3.8, 14.2, 1.9), M["post"], None, n=10)
    kit.box("h.posthead", (0.34, 0.34, 0.4), (HX - 3.8, 14.2, 3.9), M["post"], bevel=0.04)
    kit.box("h.postbulb", (0.24, 0.24, 0.28), (HX - 3.8, 14.2, 3.86), ctx["lampbulb"], bevel=0.03)
    kit.light("post", "POINT", (HX - 3.6, 14.0, 3.5), 900.0, "#e8b060", size=0.15)
    # the music stand for Mum, and the audience rows (off until the concert), and bunting
    stand = kit.empty("h.stand", (HX + 1.2, -3.5, 0.0))
    kit.cyl("h.standpole", 0.015, 1.3, (0, 0, 0.65), M["stand"], stand, n=6)
    kit.box("h.standtop", (0.5, 0.03, 0.34), (0, -0.02, 1.4), M["stand"], stand, rot=(math.radians(-18), 0, 0))
    kit.box("h.standbase", (0.5, 0.5, 0.03), (0, 0, 0.02), M["stand"], stand)
    ctx["stand"] = stand
    rows = []
    for r_ in range(6):
        for c_ in range(7):
            if c_ == 3:
                continue
            x = HX - 3.6 + c_ * 1.2
            y = -1.0 + r_ * 1.15
            rows.append(hall_chair(kit, M, f"aud{r_}{c_}", (x, y, 0), 0))
    ctx["rows"] = rows
    rng = random.Random(46)
    cols = ["#5a6a8a", "#8a5a5a", "#4a6a5a", "#7a6a8a", "#9a8a5a", "#3a4a6a", "#6a4a4a", "#5a5a5a", "#8a7a6a"]
    skins = ["#e0b08a", "#c68a62", "#8c5c40", "#f0c8a0", "#d9a07c"]
    people = []
    for r_ in range(1, 5):
        for c_ in range(7):
            if c_ == 3 or rng.random() < 0.28:
                continue
            x = HX - 3.6 + c_ * 1.2
            y = -1.0 + r_ * 1.15 + 0.1
            g = kit.empty(f"aud_p{r_}{c_}", (x, y, 0))
            body = pbr(kit, f"aud body {rng.choice(cols)}{r_}{c_}", rng.choice(cols), 0.9)
            bx(kit, f"aud_p{r_}{c_}.t", (0.5, 0.3, 0.6), (0, 0.0, 0.85), body, g, bevel=0.06)
            hc = pbr(kit, f"aud head {r_}{c_}", rng.choice(skins), 0.6)
            kit.cyl(f"aud_p{r_}{c_}.h", 0.13, 0.26, (0, 0.0, 1.3), hc, g, n=14)
            hair = pbr(kit, f"aud hair {r_}{c_}", rng.choice(["#2a1d15", "#6a5a3a", "#9a9a9a", "#3a2a22", "#171717"]), 0.9)
            kit.cyl(f"aud_p{r_}{c_}.hr", 0.14, 0.14, (0, 0.03, 1.35), hair, g, n=14)
            people.append(g)
    ctx["people"] = people
    # bunting: small triangles along three swags
    tris = []
    cmats = [M["bunting_a"], M["bunting_b"], M["bunting_c"], M["bunting_d"]]
    for line, (ya, za) in enumerate(((-2.5, 4.3), (1.5, 4.3), (5.0, 4.3))):
        for i in range(16):
            u = i / 15
            x = HX - 4.6 + u * 9.2
            z = za - 0.5 * math.sin(math.pi * u)
            v = [(-0.14, 0, 0), (0.14, 0, 0), (0, 0, -0.34)]
            t = kit.mesh_obj(f"bunt{line}{i}", v, [(0, 1, 2)], cmats[i % 4], None, (x, ya, z))
            tris.append(t)
    kit.box("bunt_line1", (9.4, 0.01, 0.01), (HX, -2.5, 4.05), M["flex"])
    ctx["bunting"] = tris
    # the scarf draped over the twelfth chair, and the folded robe on its seat (cue props)
    sc = kit.empty("scarfprop", (twelfth[0], twelfth[1], twelfth[2]))
    red = pbr(kit, "scarf red", "#9a2e2a", 0.9, noise=(14.0, 0.7, 0.0))
    cream = pbr(kit, "scarf cream", "#efe2c0", 0.9, noise=(14.0, 0.7, 0.0))
    # a chunky knitted scarf thrown over the chair back: a fat loop over the top rail, one tail down the front of the
    # back, one over the seat's edge, stripes and fringe so it reads as cloth and not a card (chair back is at -y)
    bx(kit, "scarfprop.loop", (0.46, 0.2, 0.2), (0, -0.2, 1.0), M["scarf"], sc, bevel=0.07)
    bx(kit, "scarfprop.loopb", (0.46, 0.16, 0.24), (0, -0.27, 0.9), M["scarf"], sc, bevel=0.07)
    bx(kit, "scarfprop.t1", (0.17, 0.1, 0.6), (-0.1, -0.12, 0.72), M["scarf"], sc, rot=(0.12, 0.0, 0.05), bevel=0.04)
    bx(kit, "scarfprop.seat", (0.34, 0.3, 0.14), (0.04, 0.02, 0.56), M["scarf"], sc, rot=(0.0, 0.0, 0.25), bevel=0.06)
    bx(kit, "scarfprop.t2", (0.17, 0.1, 0.4), (0.12, 0.2, 0.42), M["scarf"], sc, rot=(-0.2, 0.0, -0.1), bevel=0.04)
    for i, (z_, c_) in enumerate(((0.82, red), (0.7, cream), (0.58, red))):
        bx(kit, f"scarfprop.s{i}", (0.18, 0.105, 0.05), (-0.1 + (0.82 - z_) * 0.2, -0.12 + (0.82 - z_) * 0.07, z_), c_, sc, rot=(0.12, 0.0, 0.05), bevel=0.015)
    bx(kit, "scarfprop.stripe_a", (0.47, 0.205, 0.045), (0, -0.2, 0.97), red, sc, bevel=0.02)
    bx(kit, "scarfprop.stripe_b", (0.47, 0.205, 0.045), (0, -0.2, 1.06), cream, sc, bevel=0.02)
    for i in range(5):
        bx(kit, f"scarfprop.f{i}", (0.02, 0.02, 0.1), (-0.14 + i * 0.07 + 0.0, 0.2 + 0.03 * (i % 2), 0.2), cream, sc, bevel=0.005)
    ctx["scarfprop"] = sc
    rb = kit.empty("robeprop", (twelfth[0], twelfth[1], twelfth[2]))
    bx(kit, "robeprop.a", (0.4, 0.38, 0.12), (0, 0.0, 0.53), M["curtain"], rb, bevel=0.04)
    bx(kit, "robeprop.b", (0.38, 0.36, 0.06), (0, 0.0, 0.62), M["enamel"], rb, bevel=0.02)
    ctx["robeprop"] = rb


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    M = materials(kit)
    ctx = {"M": M, "lt": {}}
    ctx["lampbulb"] = pbr(kit, "lamp bulb", "#ffe2b0", 0.4, emit="#ffc880", emit_s=0.0)
    w = bpy.context.scene.world
    nt = w.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.55
    mr.clamp = True
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], nt.nodes["Background"].inputs["Color"])
    ctx["sky"] = (ramp, nt.nodes["Background"])
    build_street(kit, M, ctx)
    build_kitchen(kit, M, ctx)
    build_bedroom(kit, M, ctx)
    build_hall(kit, M, ctx)
    sun = kit.light("sun", "SUN", (-20, 24, 17), 1.0, "#ffd9b0", size=0.02)
    kit.aim(sun, (0, 0, 0))
    ctx["sun"] = sun
    ctx["inited"] = False
    ctx["shotspec"] = {sh["id"]: sh for sh in story["shots"]}
    return ctx


# ------------------------------------------------------------------------------------------------ the Grin's face
def grin_texture(skin):
    """A pale waxy face with no drawn eyes (two dark sockets; the glints are kit.emit pieces in decorate), its top half
    sunk in shadow, and a thin dark seam for a mouth, slightly upturned at the corners, that runs all the way round the
    head and meets itself at the back."""
    face = {"eyes": "none", "brows": False, "mouth": "none", "ink": "#1a1416"}
    im = faces.face_image(face, skin, "neutral", 0.0, (0, 0), 0.0).copy().convert("RGB")
    d = ImageDraw.Draw(im)
    W, H = im.size
    s = faces.FX1 - faces.FX0
    cx = W / 2
    ink = (3, 2, 3)
    # the top half of the face (and head) in shadow: a gradient from near-black at the brow to the skin at the cheeks
    y_top, y_full = faces._fy(0.0), faces._fy(0.74)
    px = im.load()
    for y in range(0, int(y_full)):
        u = max(0.0, min(1.0, (y - y_top) / max(1.0, y_full - y_top)))
        k = 0.05 + 0.95 * u ** 2.5
        for x in range(W):
            r, g, b = px[x, y]
            px[x, y] = (int(r * k), int(g * k), int(b * (k * 1.08)))
    # the back and the far sides of the head are dark: only the front reads, the rim catches the outline
    for y in range(H):
        for x in range(W):
            dx = abs((x - cx + W / 2) % W - W / 2) / s
            f = 1.0 if dx < 0.5 else max(0.1, 1.0 - (dx - 0.5) * 2.2)
            if f < 1.0:
                r, g, b = px[x, y]
                px[x, y] = (int(r * f), int(g * f), int(b * f))
    # two sunk sockets, no whites and no pupils
    ey = faces._fy(0.40)
    for side in (-1, 1):
        ex = cx + side * 0.21 * s
        rx, ry = 0.11 * s, 0.05 * s
        d.ellipse([ex - rx, ey - ry, ex + rx, ey + ry], fill=(4, 3, 5))
    cy = faces._fy(0.80)
    a = 0.40 * s

    def y_of(dx):
        # uneven corners: the left one lifts further than the right, with a small wobble
        r = min(1.0, abs(dx) / a)
        lift = (0.085 if dx < 0 else 0.045) * s
        return cy - lift * r * r + 0.008 * s * math.sin(dx / s * 9.0)

    # a thick near-black seam all the way round, meeting itself once at the back
    n = 720
    for i in range(n):
        x0 = W * i / n
        x1 = W * (i + 1) / n
        dx = (x0 + x1) / 2 - cx
        dx = (dx + W / 2) % W - W / 2   # wrap
        th = (0.060 + 0.022 * max(0.0, 1.0 - abs(dx) / (0.9 * s))) * s
        d.line([(x0 - 1, y_of(dx)), (x1 + 1, y_of(dx))], fill=ink, width=max(4, int(th)))
    return im


# ------------------------------------------------------------------------------------------------ decorate
def attach_beads(kit, M, who, style, ctx):
    tor = bpy.data.objects.get(f"{who}.torso")
    if tor is None:
        return
    spec = ctx["bead_specs"].get(who, {})
    dark = spec.get("dark", 0)
    own = spec.get("own", None)             # animate this many beads (a list of per-bead materials)
    key = spec.get("share", who)
    r = 0.115
    if style == "chest":
        def fn(u):
            x = -0.82 + 1.64 * u
            return (x, -0.62, 0.95 + 1.0 * (x / 0.82) ** 2)
        pts = resample(fn, 10)
    elif style == "collar":
        def fn(u):
            x = -0.62 + 1.24 * u
            return (x, -0.62, 1.32 + 0.64 * (x / 0.62) ** 2)
        pts = resample(fn, 10)
        r = 0.105
    elif style == "ron":
        pts = []
        for loop, low in enumerate((1.55, 1.15, 0.75)):
            def fn(u, low=low):
                x = -0.88 + 1.76 * u
                return (x, -0.62 - 0.11 * loop, low + (1.95 - low) * (x / 0.88) ** 2)
            pts += [(x, y, z) for x, y, z in resample(fn, 15)]
        r = 0.095
    else:
        return
    mats = ctx["bead_mats"].setdefault(key, [])
    beads = []
    for i, p in enumerate(pts):
        if own is not None and (style != "ron" or i in ctx["ron_fade"]):
            if len(mats) < len(pts):
                m = bead_mat(kit, f"bead {key} {i}", 1.0)
                mats.append((i, m))
            m = next(mm for ii, mm in mats if ii == i)
        else:
            m = M["bead_dark"] if i >= len(pts) - dark and style != "ron" else M["bead_lit"]
        b = kit.sphere(f"{who}.bead{i}", r, p, m, tor, seg=10)
        beads.append(b)
    ctx.setdefault("beads_obj", {})[who] = beads


def decorate(kit, story, ctx):
    M = ctx["M"]
    names = list(story["cast"].keys())
    ctx["ron_fade"] = list(range(34, 41))      # seven beads at the bottom of Ron's third loop, middle of the row
    ctx["bead_mats"] = {}
    ctx["bead_specs"] = {"me": {"own": True}, "mum": {"own": True, "share": "mum"}, "mumr": {"own": True, "share": "mum"},
                         "postman": {"own": True}, "gateman": {"own": True}, "gatewoman": {"own": True},
                         "nb1": {"own": True}, "nb2": {"own": True}}
    for who in names:
        if who == "grin":
            continue
        style = "collar" if who == "me" else "chest"
        attach_beads(kit, M, who, style, ctx)
    # per-owner animated material lists, ordered by bead index
    ctx["bm"] = {k: [m for _, m in sorted(v, key=lambda e: e[0])] for k, v in ctx["bead_mats"].items()}
    # my long cord (70 beads down the front and over the knees, seated), and the bulge under the knit
    tor = bpy.data.objects.get("me.torso")
    cord = []
    cord_mats = []
    if tor is not None:
        n = 70
        for i in range(n):
            u = i / (n - 1)
            if u < 0.62:
                v = u / 0.62
                x = 0.62 * math.sin(v * math.pi * 3.1)
                z = 1.2 - 1.05 * v
                y = -0.64 - 0.05 * (i % 2)
            else:
                v = (u - 0.62) / 0.38
                x = 0.55 * math.sin(v * math.pi * 3.0) * 0.8
                z = 0.62 + 0.04 * (i % 2)
                y = -0.7 - 1.45 * v
            m = bead_mat(kit, f"cord {i}", 1.0)
            cord_mats.append(m)
            b = kit.sphere(f"me.cord{i}", 0.1, (x, y, z), m, tor, seg=8)
            cord.append(b)
        knit = bpy.data.objects["me.torsom"].data.materials[0]
        bl = []
        for j, (bxx, bz, rr) in enumerate(((-0.35, 0.55, 0.45), (0.3, 0.45, 0.5), (0.0, 0.2, 0.42), (0.0, 0.85, 0.4))):
            bl.append(kit.sphere(f"me.bulge{j}", rr, (bxx, -0.66, bz), knit, tor, seg=12))
            bl[-1].scale = (1.0, 0.55, 0.9)
        ctx["bulge"] = bl
    ctx["cord"], ctx["cord_mats"] = cord, cord_mats
    # Mum's scarf (worn) for the mum rigs
    ctx["mscarf"] = []
    for who in ("mum", "mumr"):
        t_ = bpy.data.objects.get(f"{who}.torso")
        if t_ is None:
            continue
        a = bx(kit, f"{who}.scarfw", (2.1, 1.14, 0.26), (0, 0, 2.02), M["scarf"], t_, bevel=0.1)
        b_ = bx(kit, f"{who}.scarftail", (0.42, 0.1, 1.0), (0.72, 0.62, 1.4), M["scarf"], t_, bevel=0.05)
        ctx["mscarf"].append((who, [a, b_]))
    # the postman's satchel, Ron's brows, the Grin's face
    pt = bpy.data.objects.get("postman.torso")
    if pt is not None:
        sat = bx(kit, "postman.satchel", (1.5, 0.6, 1.1), (0.9, -0.2, 0.5), pbr(kit, "satchel", "#7a5a38", 0.8), pt, rot=(0, 0.35, 0), bevel=0.1)
        bx(kit, "postman.strap", (0.2, 1.06, 0.08), (0, 0.0, 1.5), pbr(kit, "satchel", "#7a5a38", 0.8), pt, rot=(0, -0.65, 0))
    gh = bpy.data.objects.get("grin.headg")
    if gh is not None:
        # the buzz-cut slab overhangs the round head like a mortarboard: shrink it inside the outline
        hz = bpy.data.objects.get("grin.buzz")
        if hz is not None:
            # fitted brown block hair: a short round cap hugging the crown, not a slab
            hz.hide_render = True
            hz.scale = (0.01, 0.01, 0.01)
            kit.cyl("grin.hair", faces.HEAD_R + 0.02, 0.34, (0, 0, faces.HEAD_H / 2 - 0.13), hz.data.materials[0], gh, n=28)
        gh.scale = (0.92, 0.92, 0.92)           # a head a little small for the body
        # the stretched part: a bare neck far too long, so the head rides high and bends further than any neck should
        NECK = 1.1
        head = bpy.data.objects["grin.head"]
        head.location = (0, 0, NECK)
        nm = pbr(kit, "grin neck", "#9d998c", 0.5)
        bx(kit, "grin.neckbox", (0.58, 0.48, NECK + 0.5), (0, 0.0, NECK / 2 - 0.1), nm, bpy.data.objects["grin.neck"], bevel=0.05)
        # two tiny cold glints just in front of the sockets, the brightest points in the frame
        gm = kit.emit("#dff0ff", 70.0, "grin glint")
        for sx in (-1, 1):
            kit.sphere(f"grin.glint{sx}", 0.024, (sx * 0.21 * 0.9, -(faces.HEAD_R + 0.012), 0.12), gm, gh, seg=8)
    # Ron's earmuffs: two fat knitted cranberry cups and a band over the crown, on his head
    rg = bpy.data.objects.get("ron.headg")
    if rg is not None:
        knit = pbr(kit, "earmuff knit", "#b8324a", 0.97, noise=(26.0, 0.62, 0.0), bump=0.3)
        band = pbr(kit, "earmuff band", "#a02a40", 0.97, noise=(30.0, 0.66, 0.0))
        for sx in (-1, 1):
            kit.cyl(f"ron.muff{sx}", 0.47, 0.34, (sx * (faces.HEAD_R + 0.1), 0.02, 0.02), knit, rg,
                    rot=(0, math.pi / 2, 0), n=20)
        for i in range(9):
            th = math.pi * i / 8
            r_ = faces.HEAD_R + 0.1
            bx(kit, f"ron.band{i}", (0.3, 0.2, 0.14), (r_ * math.cos(th), 0.02, 0.02 + (r_ + 0.02) * math.sin(th)), band, rg,
               rot=(0, -(th + math.pi / 2), 0), bevel=0.03)
    ctx["grin_tex"] = None
    mat = bpy.data.materials.get("head grin")
    if mat is not None:
        tex = next(n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE")
        img = grin_texture(story["cast"]["grin"]["skin"])
        import os
        import tempfile
        path = os.path.join(tempfile.gettempdir(), f"ep46-grin-face-{os.getpid()}.png")
        img.save(path)
        loaded = bpy.data.images.load(path)
        loaded.colorspace_settings.name = "sRGB"
        tex.image = loaded
        ctx["grin_tex"] = (tex, loaded)
    # fog nodes (density multiply and fog emission), found once
    d0 = story["look"]["fog_density"]
    fc = lin(hexrgb(story["look"]["fog"]))
    dens, ems = [], []
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        for n in m.node_tree.nodes:
            if n.type == "MATH" and n.operation == "MULTIPLY" and abs(n.inputs[1].default_value + d0) < 1e-6:
                dens.append(n)
            elif n.type == "EMISSION":
                c = n.inputs["Color"].default_value
                if all(abs(c[i] - fc[i]) < 0.02 for i in range(3)) and abs(n.inputs["Strength"].default_value - 1.0) < 1e-6:
                    ems.append(n)
    ctx["fog_dens"], ctx["fog_ems"] = dens, ems
    ctx["inited"] = True


def tod_state(tl, t):
    cs = [c for c in _cues(tl, "tod") if c["t"] <= t + 1e-9]
    cur = cs[-1]["set"] if cs else "morning"
    prev = cs[-2]["set"] if len(cs) > 1 else cur
    u = 1.0
    if cs and float(cs[-1].get("dur", 0)) > 0:
        u = ss((t - cs[-1]["t"]) / float(cs[-1]["dur"]))
    a, b = TOD[prev], TOD[cur]
    out = {}
    for k in a:
        if isinstance(a[k], str):
            out[k] = mixc(hexrgb(a[k]), hexrgb(b[k]), u)
        elif isinstance(a[k], tuple):
            out[k] = tuple(x + (y - x) * u for x, y in zip(a[k], b[k]))
        else:
            out[k] = a[k] + (b[k] - a[k]) * u
    return out


def bead_level(evs, t):
    """evs: [(t0, target, dur)] sorted. Starts lit (1)."""
    v = 1.0
    for t0, tgt, dur in evs:
        if t < t0:
            break
        if dur > 0 and t < t0 + dur:
            return v + (tgt - v) * ss((t - t0) / dur)
        v = tgt
    return v


def animate(kit, story, tl, t, ctx):
    bpy.context.view_layer.update()
    if not ctx["inited"]:
        decorate(kit, story, ctx)
        bpy.context.view_layer.update()
    M = ctx["M"]
    over = {}
    # ---------------------------------------------------------------- the sky, the sun, the street lamps
    s = tod_state(tl, t)
    sd = V(s["dir"]).normalized() if isinstance(s["dir"], tuple) else V(TOD["morning"]["dir"]).normalized()
    ctx["sun"].location = tuple(sd * 40)
    kit.aim(ctx["sun"], (0, 0, 0))
    ctx["sun"].data.color = lin(s["sunc"])
    over["sun"] = s["sun"]
    ramp, bg = ctx["sky"]
    ramp.color_ramp.elements[0].color = (*lin(s["hor"]), 1)
    ramp.color_ramp.elements[1].color = (*lin(s["zen"]), 1)
    bg.inputs["Strength"].default_value = s["sky"] * 0.6
    for n in ctx["fog_dens"]:
        n.inputs[1].default_value = -s["fogd"]
    fcol = lin(s["fogc"])
    for n in ctx["fog_ems"]:
        n.inputs["Color"].default_value = (*fcol, 1)
    for i in range(4):
        over[f"lamp{i}"] = s["lamp"]
    over["post"] = s["lamp"]
    ctx["lampbulb"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 14.0 * s["lamp"]
    for m in ctx["win_mats"]:
        m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 5.0 * s["win"]
    for o in ctx["stars"]:
        o.hide_render = s["stars"] < 0.5
    ctx["mug"].hide_render = False
    # ---------------------------------------------------------------- a fill that rides with the camera in some night shots
    shot_id = next((sh["id"] for sh in tl["shots"] if sh["start"] <= t < sh["end"]), tl["shots"][-1]["id"])
    spec = ctx["shotspec"].get(shot_id, {})
    cf = spec.get("fill")
    cl = kit.LIGHTS["camfill"]
    if cf:
        k0 = spec["cam"][0]
        cl["obj"].location = (k0[1][0], k0[1][1], k0[1][2] + 0.1)
        cl["light"].color = lin(hexrgb(cf[1]))
        over["camfill"] = cf[0]
    else:
        over["camfill"] = 0.0
    # ---------------------------------------------------------------- named lights by cue
    for name in DEF:
        cs = [c for c in _cues(tl, "lt") if c["l"] == name]
        lv = eased(cs, "v", t, DEF[name])
        if name == "hall_house":
            for i in range(3):
                over[f"hall_house{i}"] = lv
        else:
            over[name] = lv
    # hidden people take their beads, cord and seam with them (decorate adds those after the first pose)
    for who in story["cast"]:
        r_ = bpy.data.objects.get(who)
        if r_ is not None and r_.hide_render:
            for o in r_.children_recursive:
                o.hide_render = True
    # the rig swaps every head's face image per frame; keep the Grin's own (wraparound grin) on
    if ctx.get("grin_tex"):
        ctx["grin_tex"][0].image = ctx["grin_tex"][1]
    # ---------------------------------------------------------------- doors, chairs, props
    ang = eased(_cues(tl, "door"), "deg", t, 0.0)
    ctx["bdoor"].rotation_euler = (0, 0, math.radians(ang))
    hd = eased(_cues(tl, "hdoor"), "deg", t, 0.0)
    ctx["hdoor"].rotation_euler = (0, 0, math.radians(hd))
    c12 = eased(_cues(tl, "c12"), "deg", t, 0.0)
    ctx["c12"].rotation_euler = (0, 0, math.radians(180 + c12))
    turned = bool((_last(_cues(tl, "turned"), t) or {}).get("on"))
    tw = ctx["c12pos"]
    for g, p in ctx["chairs"]:
        if turned:
            yw = math.degrees(math.atan2(tw[0] - p[0], -(tw[1] - p[1])))
            g.rotation_euler = (0, 0, math.radians(yw))
        else:
            g.rotation_euler = (0, 0, math.radians(180))
    show(ctx["curwin"], shot_id != tl["shots"][-1]["id"])
    # the last shot is far off: a thicker seam so it reads at phone size
    _sm = bpy.data.objects.get("grin.seam")
    if _sm is not None:
        _sm.scale = (1.7, 1.4, 1.0) if shot_id == tl["shots"][-1]["id"] else (1.0, 1.0, 1.0)
    st_ = _last(_cues(tl, "stand"), t)
    if st_ is not None:
        ctx["stand"].location = tuple(st_["pos"])
    fw_ = _last(_cues(tl, "farwin"), t)
    show(ctx["far"], bool(fw_ and fw_.get("on")))
    show(ctx["rows"], bool((_last(_cues(tl, "rows"), t) or {}).get("on")))
    show(ctx["people"], bool((_last(_cues(tl, "audience"), t) or {}).get("on")))
    show(ctx["bunting"], bool((_last(_cues(tl, "bunting"), t) or {}).get("on")))
    pr = (_last(_cues(tl, "props"), t) or {})
    show([ctx["scarfprop"]], bool(pr.get("scarf")))
    show([ctx["robeprop"]], bool(pr.get("robe")))
    # ---------------------------------------------------------------- poses the rig doesn't do: sitting, bending, rolling
    for who, keys in tl["acting"].items():
        root = bpy.data.objects.get(who)
        if root is None or root.hide_render:
            continue
        tor = bpy.data.objects.get(f"{who}.torso")
        neck = bpy.data.objects.get(f"{who}.neck")
        tor.rotation_euler = (math.radians(ac._held(keys, "bend", t, 0.0)), math.radians(ac._held(keys, "roll", t, 0.0)), 0)
        _tl = ac._held(keys, "tilt", t, 0.0)
        if who == "grin":
            # the neck stays nearly upright; the small head folds sideways at the top joint
            neck.rotation_euler = (neck.rotation_euler.x, math.radians(_tl * 0.2), neck.rotation_euler.z)
            _hb = bpy.data.objects.get("grin.head")
            if _hb is not None:
                _hb.rotation_euler = (0, math.radians(_tl * 1.25 if _tl else -24.0), 0)
        else:
            neck.rotation_euler = (neck.rotation_euler.x, math.radians(_tl), neck.rotation_euler.z)
        lunge = ac._held(keys, "lunge", t, 0.0)
        if lunge:
            for sx, sgn in ((-1, -1), (1, 1)):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (math.radians(lunge * sgn), 0, 0)
        sit = False
        for k in keys:
            if "sit" in k and k["t"] <= t + 1e-9:
                sit = k["sit"]
        if sit:
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (-math.pi / 2, 0, 0)
                coat = bpy.data.objects.get(f"{who}.coat{sx}")
                if coat is not None:
                    coat.rotation_euler = (-math.pi / 2, 0, 0)
    # ---------------------------------------------------------------- beads
    ev = {}
    for c in _cues(tl, "bead_off") + _cues(tl, "bead_on"):
        tgt = 0.0 if c["name"] == "bead_off" else 1.0
        who = c["who"]
        for k, idx in enumerate(c["idx"]):
            ev.setdefault((who, idx), []).append((c["t"] + k * float(c.get("step", 0.0)), tgt, float(c.get("dur", 0.45))))
    for key, mats in ctx["bm"].items():
        for i, m in enumerate(mats):
            evs = sorted(ev.get((key, i), []))
            lvl = bead_level(evs, t)
            m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = BEAD_LIT_S * lvl
    # the long cord and the bulge
    cs_ = _last(_cues(tl, "cord"), t)
    cord_on = bool(cs_ and cs_.get("on"))
    me_root = bpy.data.objects.get("me")
    me_vis = me_root is not None and not me_root.hide_render
    for b in ctx["cord"]:
        b.hide_render = not (cord_on and me_vis)
    cf = _last(_cues(tl, "cordfade"), t)
    for i, m in enumerate(ctx["cord_mats"]):
        lvl = 1.0
        if cf:
            lvl = 1.0 - ss((t - (cf["t"] + i * float(cf.get("step", 0.035)))) / 0.4)
        m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = BEAD_LIT_S * lvl
    bu = _last(_cues(tl, "bulge"), t)
    for b in ctx.get("bulge", []):
        b.hide_render = not (bu and bu.get("on") and me_vis)
    sc = _last(_cues(tl, "scarf"), t)
    for who, objs in ctx["mscarf"]:
        r_ = bpy.data.objects.get(who)
        vis = r_ is not None and not r_.hide_render and bool(sc and who in sc.get("who", []))
        for o in objs:
            o.hide_render = not vis
    return over
