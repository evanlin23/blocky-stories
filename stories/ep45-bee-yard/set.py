"""Ep45 "bee yard": a harbour town on a hill, early summer, clear light. Two places in one file.

The yard (world origin at the gate, +y up the hill, -y down toward the town): a grassy slope (gz(y)), a dry-stone
wall round the yard with one wooden gate at x = 0, twelve white hives in three rows (rows at y = 5.5, 9.5, 13.5,
hives numbered 1 to 12 from the gate side, left to right), a small shed just inside the gate with the veil board
on its +x side wall, a smoker on a crate. The harbour and sea are far below in wides.

The pier (x offset PX = 300): a quay, a wooden ferry pier running +y with a white rail, a little blocky ferry at its end,
a ticket hut with a shutter, a high café table, benches, steps. No lettering anywhere.

Everything that changes in a shot is keyed from story.json cues (read here): the dials over every head but the Hover's
(`dial` cues), the veils (`veil`), the smoke (`smoke_in`, `smoke_out`), and the light is a preset per shot (LOOK_OF).
Light changes inside a shot are slow fades only: the smoke over 3 s, a dial's glow over 0.8 s and back over 1 s.
"""

from __future__ import annotations

import math

import bpy
import numpy as np
from mathutils import Vector as V

from blocky import acting, dialart, faces, rig

PX = 300.0               # the pier's x offset
SLOPE = 0.12
ROWS = (5.5, 9.5, 13.5)
COLS = (-4.5, -1.5, 1.5, 4.5)
YARD_X = 7.5
YARD_Y = 16.0
HOVER_LIFT = 0.12        # his soles are always a hand's width above the grass
DIAL_R = 0.21
FOG_NODES = {"built": False}


def G(y: float) -> float:
    return SLOPE * y if y >= 0 else SLOPE * y - 0.02 * y * y


def gz(y: float) -> float:
    """The ground as the mesh draws it: G at 2.5 m nodes, straight between them."""
    y0 = math.floor(y / 2.5) * 2.5
    u = (y - y0) / 2.5
    return G(y0) * (1 - u) + G(y0 + 2.5) * u


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------------------------------------ materials


def grass_mat(kit, name="grass", c1="#4f7a33", c2="#6c9a45"):
    if name in kit.MATS:
        return kit.MATS[name]
    m, N, L, b = kit._mat(name)
    v = kit._coords(N, L, 1.0)
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.7
    nz.inputs["Detail"].default_value = 5.0
    L.new(v, nz.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.38
    ramp.color_ramp.elements[0].color = kit.col(c1)
    ramp.color_ramp.elements[1].position = 0.62
    ramp.color_ramp.elements[1].color = kit.col(c2)
    L.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    # fine blades: a high-frequency noise darkens the green a little
    nz2 = N.new("ShaderNodeTexNoise")
    nz2.inputs["Scale"].default_value = 38.0
    nz2.inputs["Detail"].default_value = 2.0
    L.new(v, nz2.inputs["Vector"])
    mx = N.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    mx.blend_type = "MULTIPLY"
    mx.inputs["Factor"].default_value = 0.5
    L.new(ramp.outputs["Color"], mx.inputs["A"])
    mx.inputs["B"].default_value = (0.8, 0.85, 0.8, 1)
    L.new(nz2.outputs["Fac"], mx.inputs["B"])
    # buttercups and clover flowers: a few small bright cells
    out = mx.outputs["Result"]
    for k, (scale, thr_d, thr_c, colr) in enumerate(((46.0, 0.115, 0.80, "#f2cf4a"), (34.0, 0.10, 0.88, "#efe8dc"))):
        vor = N.new("ShaderNodeTexVoronoi")
        vor.inputs["Scale"].default_value = scale
        vor.inputs["Randomness"].default_value = 1.0
        L.new(v, vor.inputs["Vector"])
        sep = N.new("ShaderNodeSeparateColor")
        L.new(vor.outputs["Color"], sep.inputs["Color"])
        lt = N.new("ShaderNodeMath")
        lt.operation = "LESS_THAN"
        lt.inputs[1].default_value = thr_d
        L.new(vor.outputs["Distance"], lt.inputs[0])
        gt = N.new("ShaderNodeMath")
        gt.operation = "GREATER_THAN"
        gt.inputs[1].default_value = thr_c
        L.new(sep.outputs["Red" if k == 0 else "Green"], gt.inputs[0])
        mul = N.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        L.new(lt.outputs[0], mul.inputs[0])
        L.new(gt.outputs[0], mul.inputs[1])
        mix = N.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        L.new(mul.outputs[0], mix.inputs["Factor"])
        L.new(out, mix.inputs["A"])
        mix.inputs["B"].default_value = kit.col(colr)
        out = mix.outputs["Result"]
    L.new(out, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.92
    kit._fogged(m, b.outputs[0])
    return m


def mesh_mat(kit, hexc, alpha=0.3, name=None):
    """Fine veil mesh: pale and mostly see-through."""
    name = name or f"veilmesh {hexc} {alpha}"
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Roughness"].default_value = 0.9
    b.inputs["Alpha"].default_value = alpha
    kit._fogged(m, b.outputs[0])
    return m


def disc_mesh(kit, name, R, mat, n=48, parent=None, loc=(0, 0, 0)):
    """A flat disc facing +z with UVs mapping the square image onto it."""
    verts = [(0.0, 0.0, 0.0)] + [(R * math.cos(2 * math.pi * i / n), R * math.sin(2 * math.pi * i / n), 0.0) for i in range(n)]
    faces_ = [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)]
    ob = kit.mesh_obj(name, verts, faces_, mat, parent, loc)
    uv = ob.data.uv_layers.new(name="UVMap")
    for poly in ob.data.polygons:
        for li in poly.loop_indices:
            x, y, _ = verts[ob.data.loops[li].vertex_index]
            uv.data[li].uv = (0.5 + 0.5 * x / R, 0.5 + 0.5 * y / R)
    return ob


def ring_mesh(kit, name, r0, r1, h, mat, parent, n=48):
    """A flat brass ring (annulus) with a little height: the dial's thin rim."""
    verts, fcs = [], []
    for z in (-h / 2, h / 2):
        for r in (r0, r1):
            for i in range(n):
                a = 2 * math.pi * i / n
                verts.append((r * math.cos(a), r * math.sin(a), z))
    def idx(zi, ri, i):
        return (zi * 2 + ri) * n + i % n
    for i in range(n):
        fcs.append((idx(1, 0, i), idx(1, 1, i), idx(1, 1, i + 1), idx(1, 0, i + 1)))   # top
        fcs.append((idx(0, 1, i), idx(0, 0, i), idx(0, 0, i + 1), idx(0, 1, i + 1)))   # bottom
        fcs.append((idx(0, 1, i), idx(0, 1, i + 1), idx(1, 1, i + 1), idx(1, 1, i)))   # outer
        fcs.append((idx(0, 0, i + 1), idx(0, 0, i), idx(1, 0, i), idx(1, 0, i + 1)))   # inner
    return kit.mesh_obj(name, verts, fcs, mat, parent, (0, 0, 0.002), smooth=True)


# ------------------------------------------------------------------------------------------------ the yard


def terrain(kit, mat):
    xs = [x * 2.5 for x in range(-24, 25)]
    ys = [y * 2.5 for y in range(-32, 29)]
    verts, fcs = [], []
    for y in ys:
        for x in xs:
            verts.append((x, y, G(y)))
    W = len(xs)
    for j in range(len(ys) - 1):
        for i in range(W - 1):
            a = j * W + i
            fcs.append((a, a + 1, a + W + 1, a + W))
    return kit.mesh_obj("terrain", verts, fcs, mat, smooth=True)


def hive(kit, name, x, y, yaw, M):
    z = gz(y)
    root = kit.empty(name, (x, y, z), rot=(0, 0, math.radians(yaw)))
    kit.box(f"{name}.stand", (0.52, 0.44, 0.34), (0, 0, 0.12), M["wood_grey"], root, bevel=0.01)
    kit.box(f"{name}.b1", (0.5, 0.42, 0.3), (0, 0, 0.45), M["hive"], root, bevel=0.012)
    kit.box(f"{name}.gap", (0.47, 0.39, 0.03), (0, 0, 0.615), M["dark"], root)
    kit.box(f"{name}.b2", (0.5, 0.42, 0.3), (0, 0, 0.78), M["hive"], root, bevel=0.012)
    kit.box(f"{name}.roof", (0.58, 0.5, 0.05), (0, 0, 0.955), M["roof"], root, bevel=0.012)
    kit.box(f"{name}.slot", (0.34, 0.02, 0.035), (0, -0.215, 0.33), M["dark"], root)
    kit.box(f"{name}.land", (0.38, 0.14, 0.02), (0, -0.28, 0.285), M["hive"], root, bevel=0.005)
    return root


def build_yard(kit, ctx, M):
    terrain(kit, M["grass"])
    # sea far below and a few houses on the shore
    sea = kit.plane("sea", (1200, 1200), (0, 0, -30.0), M["sea"])
    for i, (hx, hy, w, d, h, wc, rc) in enumerate((
            (-14, -29, 5, 4, 3.2, "#f1ede2", "#c9674a"), (-6, -31, 4.2, 3.6, 2.6, "#e8d8b8", "#b8573e"),
            (3, -30, 5.5, 4, 3.4, "#f1ede2", "#c9674a"), (12, -29, 4, 4, 2.8, "#d9c7a0", "#a8503a"),
            (-22, -27, 4.4, 4, 3.0, "#e6dac2", "#c9674a"), (22, -27, 5, 4, 3.0, "#f1ede2", "#b8573e"),
            (-9, -26.5, 4, 3.4, 2.4, "#efe6d2", "#a8503a"), (8, -26.5, 4.4, 3.4, 2.6, "#e8d8b8", "#c9674a"))):
        base = gz(hy)
        kit.box(f"house{i}", (w, d, h + 3.0), (hx, hy, base + h / 2 - 1.5), kit.plastic(wc, 0.8))
        kit.box(f"house{i}.roof", (w + 0.5, d + 0.5, 0.5), (hx, hy, base + h + 0.1), kit.plastic(rc, 0.8))
    kit.box("harbour_wall", (40, 2.0, 1.2), (0, -38.0, -29.6), M["stone"])
    # the wall
    sz = 1.15
    for k, y0 in enumerate([y * 2.5 for y in range(0, 7)]):
        yc = y0 + 1.25
        a = math.atan(SLOPE)
        for sx in (-1, 1):
            kit.box(f"wall{sx}.{k}", (0.55, 2.56, sz), (sx * YARD_X, yc, gz(yc) + sz / 2 - 0.2), M["stone"], rot=(a, 0, 0))
    kit.box("wall_n", (2 * YARD_X + 0.55, 0.55, sz), (0, YARD_Y, gz(YARD_Y) + sz / 2 - 0.2), M["stone"])
    for sx, x0, x1 in ((-1, -YARD_X, -2.05), (1, 2.05, YARD_X)):
        kit.box(f"wall_s{sx}", (x1 - x0, 0.55, sz), ((x0 + x1) / 2, 0.0, gz(0) + sz / 2 - 0.2), M["stone"])
    kit.box("threshold", (4.1, 0.8, 0.04), (0, 0.0, 0.0), M["stone_lt"])
    for sx in (-1, 1):
        kit.box(f"gatepost{sx}", (0.22, 0.22, 1.45), (sx * 2.1, 0.0, 0.62), M["wood"], bevel=0.015)
    # two gate leaves hinged on the posts, swung open by animate()
    ctx["gate"] = []
    for sx in (-1, 1):
        hinge = kit.empty(f"gate_hinge{sx}", (sx * 1.98, -0.02, 0.0))
        for k, zc in enumerate((0.25, 0.55, 0.85)):
            kit.box(f"gate{sx}.rail{k}", (1.96, 0.05, 0.1), (-sx * 0.98, 0.0, zc), M["wood"], hinge, bevel=0.008)
        for k in range(7):
            kit.box(f"gate{sx}.slat{k}", (0.07, 0.04, 0.9), (-sx * (0.1 + 0.3 * k), -0.04, 0.5), M["wood"], hinge, bevel=0.008)
        if sx == 1:
            kit.box("gate.latch", (0.14, 0.06, 0.05), (-1.88, -0.07, 0.62), M["metal"], hinge)
        ctx["gate"].append(hinge)
    # a strip of trodden grass up from the gate (the way I ran)
    kit.box("trodden", (0.6, 6.5, 0.012), (1.0, 3.2, gz(3.2) + 0.004), kit.plastic("#587d3b", 0.95, name="trodden"), rot=(math.atan(SLOPE), 0, 0))
    # the hives, numbered along each row from the gate side, left to right
    ctx["hives"] = []
    k = 0
    for ri, y in enumerate(ROWS):
        for ci, x in enumerate(COLS):
            k += 1
            yaw = ((k * 37) % 9 - 4) * 1.2
            ctx["hives"].append(hive(kit, f"hive{k}", x, y, yaw, M))
    # the shed just inside the gate, its +x wall carrying the veil board
    sx0, sx1, sy0, sy1, sh = -5.6, -3.6, 0.9, 3.6, 2.25
    zb = gz((sy0 + sy1) / 2)
    kit.box("shed.foot", (sx1 - sx0 + 0.1, sy1 - sy0 + 0.1, 0.7), ((sx0 + sx1) / 2, (sy0 + sy1) / 2, zb - 0.1), M["stone"])
    kit.box("shed.body", (sx1 - sx0, sy1 - sy0, sh), ((sx0 + sx1) / 2, (sy0 + sy1) / 2, zb + 0.25 + sh / 2), M["shed"])
    roof = kit.box("shed.roof", (sx1 - sx0 + 0.5, sy1 - sy0 + 0.6, 0.12), ((sx0 + sx1) / 2, (sy0 + sy1) / 2, zb + 0.25 + sh + 0.15),
                   M["roof_dk"], rot=(math.atan(SLOPE) * 0.0, 0.05, 0))
    kit.box("shed.door", (0.9, 0.05, 1.7), (-4.6, sy0 - 0.02, zb + 1.1), M["wood"])
    # the board: two hooks, two short honey-gold strokes between them (lore.md, Third parallel batch)
    bx = sx1 + 0.03
    bz = zb + 1.65
    kit.box("board", (0.06, 1.3, 0.62), (bx, 2.25, bz), M["board"], bevel=0.01)
    for k, yy in enumerate((1.75, 2.75)):
        kit.cyl(f"hook{k}", 0.018, 0.14, (bx + 0.08, yy, bz + 0.12), M["metal"], rot=(0, math.pi / 2, 0), n=10)
    tally_m = kit._new("tally_gold")
    ntt = tally_m.node_tree
    ntt.nodes.remove(ntt.nodes["Principled BSDF"])
    emt = ntt.nodes.new("ShaderNodeEmission")
    emt.inputs["Color"].default_value = kit.col("#ffbf30")
    emt.inputs["Strength"].default_value = 1.6
    ntt.links.new(emt.outputs[0], next(n for n in ntt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    for k, yy in enumerate((2.18, 2.32)):
        kit.box(f"tally{k}", (0.016, 0.05, 0.3), (bx + 0.035, yy, bz - 0.02), tally_m)
    ctx["board_pos"] = (bx, bz)
    # crates and jars
    kit.box("crate_shed", (0.7, 0.5, 0.36), (-3.2, 1.2, gz(1.2) + 0.18), M["wood"], bevel=0.01)
    for i in range(6):
        kit.cyl(f"jar_s{i}", 0.07, 0.16, (-3.4 + 0.18 * (i % 3), 1.1 + 0.2 * (i // 3), gz(1.2) + 0.44), M["jar"], n=14)
    ctx["crate_gate"] = []
    c = kit.box("crate_gate", (0.7, 0.5, 0.36), (1.1, -1.35, gz(-1.35) + 0.18), M["wood"], bevel=0.01)
    ctx["crate_gate"].append(c)
    for i in range(6):
        ctx["crate_gate"].append(kit.cyl(f"jar_g{i}", 0.07, 0.16, (0.9 + 0.2 * (i % 3), -1.45 + 0.2 * (i // 3), gz(-1.35) + 0.44), M["jar"], n=14))
    # the smoker on an upturned crate, near row 1
    cx, cy = -2.4, 3.3
    kit.box("crate_sm", (0.5, 0.5, 0.4), (cx, cy, gz(cy) + 0.2), M["wood"], bevel=0.01)
    kit.cyl("smoker", 0.075, 0.24, (cx, cy, gz(cy) + 0.52), M["tin"], n=14)
    kit.cyl("smoker.cone", 0.075, 0.1, (cx, cy, gz(cy) + 0.69), M["tin"], n=14, r2=0.025)
    kit.box("smoker.bellows", (0.1, 0.2, 0.14), (cx + 0.12, cy, gz(cy) + 0.5), M["wood"], rot=(0, 0, 0.0))
    ctx["smoker_tip"] = (cx, cy, gz(cy) + 0.76)
    # buttercups, scattered, and the one that sits under the Hover on Wednesday
    rng = np.random.default_rng(45)
    fl = kit.plastic("#f2cf4a", 0.5)
    gr = kit.plastic("#4a7a30", 0.8)
    pts = [(float(rng.uniform(-6.8, 6.8)), float(rng.uniform(1.0, 15.5))) for _ in range(70)] + [(3.0, 13.5), (3.0, 9.5), (-2.9, 2.0)]
    for i, (x, y) in enumerate(pts):
        h = 0.09 if i >= len(pts) - 3 else float(rng.uniform(0.05, 0.1))
        kit.cyl(f"stem{i}", 0.004, h, (x, y, gz(y) + h / 2), gr, n=5)
        s = kit.sphere(f"bc{i}", 0.026, (x, y, gz(y) + h), fl, seg=8)
        s.scale = (1, 1, 0.45)


# ----------------------------------------------------------------------------------------------- the pier


def build_pier(kit, ctx, M):
    X = PX
    kit.plane("pier_sea", (400, 600), (X, 150, -1.0), M["sea_near"])
    kit.box("quay", (36, 18, 0.9), (X, -9.0, -0.45), M["cobble"])
    kit.box("deck", (6.0, 28.0, 0.28), (X, 14.0, 0.31), M["deck"])
    for k in range(3):   # steps up from the quay to the deck (tops at 0.11, 0.22, 0.33; the deck is 0.45)
        kit.box(f"step{k}", (6.0, 0.45, 0.11 * (k + 1)), (X, -0.225 - 0.45 * (2 - k), 0.055 * (k + 1)), M["deck"])
    for i in range(10):
        for sx in (-2.7, 2.7):
            kit.cyl(f"pile{i}{sx}", 0.14, 3.0, (X + sx, 1.5 + i * 2.8, -1.0), M["wood_dk"], n=10)
    for sx in (-1, 1):
        n = 17
        for i in range(n):
            y = 1.2 + i * 1.5
            kit.box(f"post{sx}.{i}", (0.1, 0.1, 1.05), (X + sx * 2.85, y, 0.45 + 0.52), M["rail"], bevel=0.01)
        kit.box(f"rail{sx}", (0.08, 25.6, 0.07), (X + sx * 2.85, 13.2, 1.46), M["rail"], bevel=0.01)
        kit.box(f"rail_lo{sx}", (0.05, 25.6, 0.05), (X + sx * 2.85, 13.2, 0.98), M["rail"])
    # the little blocky ferry moored at the end
    fz = -0.35
    kit.box("ferry.hull", (4.2, 10.0, 1.3), (X, 33.5, fz), M["hull"], bevel=0.05)
    kit.box("ferry.stripe", (4.25, 10.05, 0.22), (X, 33.5, fz + 0.1), M["blue"], bevel=0.02)
    kit.box("ferry.deck", (3.7, 9.3, 0.08), (X, 33.5, fz + 0.69), M["deck"])
    kit.box("ferry.cabin", (3.0, 4.0, 1.5), (X, 33.0, fz + 1.5), M["hull"], bevel=0.04)
    kit.box("ferry.cabin_s", (3.05, 4.05, 0.2), (X, 33.0, fz + 1.55), M["blue"], bevel=0.02)
    kit.box("ferry.win", (3.04, 3.2, 0.36), (X, 33.0, fz + 1.95), M["dark"])
    kit.box("ferry.roof", (3.3, 4.3, 0.1), (X, 33.0, fz + 2.3), M["roof"], bevel=0.02)
    kit.cyl("ferry.funnel", 0.32, 0.9, (X, 34.2, fz + 2.8), M["honey"], n=16)
    kit.cyl("ferry.funnel_top", 0.34, 0.14, (X, 34.2, fz + 3.3), M["dark"], n=16)
    kit.box("ferry.plank", (1.0, 3.6, 0.07), (X, 29.0, fz + 0.78), M["deck"], rot=(0.08, 0, 0))
    for i in range(3):
        kit.cyl(f"bollard{i}", 0.12, 0.45, (X + (-2.2 if i % 2 else 2.2), 3 + i * 9, 0.72), M["dark"], n=10)
    kit.light("hut", "POINT", (hx_ := X - 7.0 + 0.4, -4.0, 2.1), 160.0, "#ffe9c8", size=0.6, shadow=False)
    # the ticket hut: walls, a counter window with a shutter, a striped awning
    hx, hy = X - 7.0, -4.0
    kit.box("hut.back", (0.12, 3.0, 2.5), (hx - 1.5, hy, 1.25), M["hut"])
    kit.box("hut.side1", (3.0, 0.12, 2.5), (hx, hy - 1.5, 1.25), M["hut"])
    kit.box("hut.side2", (3.0, 0.12, 2.5), (hx, hy + 1.5, 1.25), M["hut"])
    kit.box("hut.front_lo", (0.12, 3.0, 0.95), (hx + 1.5, hy, 0.475), M["hut"])
    kit.box("hut.front_hi", (0.12, 3.0, 0.16), (hx + 1.5, hy, 2.42), M["hut"])
    kit.box("hut.front_l", (0.12, 0.4, 1.5), (hx + 1.5, hy - 1.3, 1.45), M["hut"])
    kit.box("hut.front_r", (0.12, 0.4, 1.5), (hx + 1.5, hy + 1.3, 1.45), M["hut"])
    kit.box("hut.sill", (0.35, 1.8, 0.07), (hx + 1.62, hy, 0.97), M["wood_dk"])
    kit.box("hut.floor", (3.0, 3.0, 0.1), (hx, hy, 0.05), M["wood_dk"])
    kit.box("hut.roof", (3.5, 3.5, 0.14), (hx, hy, 2.6), M["roof_dk"], bevel=0.02)
    kit.box("hut.shutter", (0.05, 1.7, 0.2), (hx + 1.72, hy, 2.3), M["shutter"], rot=(0, 0.25, 0))
    for i in range(6):
        kit.box(f"awning{i}", (0.9, 0.38, 0.05), (hx + 2.05, hy - 1.08 + i * 0.43 + 0.0, 2.35), M["stripe_a" if i % 2 else "stripe_b"],
                rot=(0, 0.0, 0), parent=None)
    for i in range(6):
        kit.box(f"awning_l{i}", (0.05, 0.38, 0.5), (hx + 2.5, hy - 1.08 + i * 0.43, 2.1), M["stripe_a" if i % 2 else "stripe_b"])
    kit.box("hut.stool", (0.4, 0.4, 0.5), (hx - 0.6, hy + 0.0, 0.35), M["wood"])
    # the high café table on the quay, benches, a planter
    tx, ty = X + 6.0, -5.5
    kit.cyl("cafe.table", 0.5, 0.06, (tx, ty, 1.03), M["wood"], n=24)
    kit.cyl("cafe.leg", 0.05, 1.0, (tx, ty, 0.52), M["metal"], n=10)
    kit.cyl("cafe.foot", 0.28, 0.04, (tx, ty, 0.02), M["metal"], n=18)
    kit.cyl("cafe.cup1", 0.05, 0.08, (tx - 0.2, ty + 0.05, 1.1), M["jar"], n=10)
    kit.cyl("cafe.cup2", 0.05, 0.08, (tx + 0.2, ty - 0.05, 1.1), M["jar"], n=10)
    for k, bx in enumerate((X - 2.0, X + 2.0)):
        by = 7.5 + 7 * k
        kit.box(f"bench{k}.seat", (0.5, 1.8, 0.08), (X + (-1.9 if k == 0 else 1.9), by, 0.92), M["wood"])
        kit.box(f"bench{k}.leg1", (0.4, 0.08, 0.45), (X + (-1.9 if k == 0 else 1.9), by - 0.7, 0.7), M["dark"])
        kit.box(f"bench{k}.leg2", (0.4, 0.08, 0.45), (X + (-1.9 if k == 0 else 1.9), by + 0.7, 0.7), M["dark"])
    for k in range(4):
        kit.box(f"planter{k}", (1.2, 0.5, 0.5), (X - 10 + k * 6.5, -15.0, 0.25), M["wood_dk"])
        kit.sphere(f"planter{k}.bush", 0.45, (X - 10 + k * 6.5, -15.0, 0.75), M["bush"], seg=8)
    # town front along the quay, plain colours, no lettering
    for i, (bxo, w, h, wc, rc) in enumerate(((-13, 7, 8, "#e8d8b8", "#b8573e"), (-5, 8, 10, "#f1ede2", "#c9674a"),
                                            (4, 7, 7.5, "#d9c7a0", "#a8503a"), (12, 8, 9, "#e6dac2", "#c9674a"))):
        kit.box(f"front{i}", (w, 5, h), (X + bxo, -20.5, h / 2), kit.plastic(wc, 0.8))
        kit.box(f"front{i}.roof", (w + 0.6, 5.6, 0.5), (X + bxo, -20.5, h + 0.2), kit.plastic(rc, 0.8))
        for wi in range(3):
            for wj in range(2):
                kit.box(f"front{i}.w{wi}{wj}", (0.8, 0.1, 1.1), (X + bxo - w / 3 + wi * w / 3, -17.95, 2.2 + wj * 3.2), M["dark"])
    # gulls, far off, a few dots
    ctx["gulls"] = [kit.sphere(f"gull{i}", 0.09, (X + (i - 3) * 6, 60 + 7 * i, 12 + 2 * (i % 3)), kit.plastic("#f1ede2", 0.7), seg=6) for i in range(6)]
    for g in ctx["gulls"]:
        g.scale = (3.2, 1.0, 0.5)
    ctx["far_hills"] = kit.box("far_island", (180, 30, 14), (X + 40, 330, -2), kit.plastic("#7a9a78", 0.9))


# ----------------------------------------------------------------------------------------------- veils


def make_veil(kit, name, parent, u, loc, tone, rot=(0, 0, 0), mesh_len=0.42, hang=True):
    """A wide-brimmed veil hat: straw brim and crown, a band, and a fine pale mesh falling from the brim. Sizes in
    metres times u (u = 1 / 0.34 when the parent is a character's head, which is in rig units)."""
    straw = kit.plastic("#d8c79a", 0.8)
    band = kit.plastic(tone["band"], 0.7)
    mesh = mesh_mat(kit, tone["mesh"], tone.get("alpha", 0.28))
    root = kit.empty(name, loc, parent, rot)
    kit.cyl(f"{name}.brim", 0.31 * u, 0.018 * u, (0, 0, 0), straw, root, n=32)
    kit.cyl(f"{name}.crown", 0.15 * u, 0.12 * u, (0, 0, 0.07 * u), straw, root, n=24, r2=0.135 * u)
    kit.cyl(f"{name}.band", 0.153 * u, 0.03 * u, (0, 0, 0.03 * u), band, root, n=24)
    if hang:
        v = kit.cyl(f"{name}.mesh", 0.2 * u, mesh_len * u, (0, 0, -mesh_len * u / 2), mesh, root, n=24, r2=0.29 * u)
        for p in v.data.polygons[24:]:
            pass
    return root


# ---------------------------------------------------------------------------------------------- materials


def materials(kit):
    M = {}
    M["grass"] = grass_mat(kit)
    M["stone"] = kit.cobbles("#8d8372", "#b7ad98", "#4f493f", scale=2.4, wet=0.0, name="drystone")
    M["stone_lt"] = kit.grime("#a39886", 0.7, 3.0, name="stone_lt")
    M["hive"] = kit.plastic("#f1ede2", 0.7, name="hive_white")
    M["roof"] = kit.plastic("#cfcabc", 0.7, name="hive_roof")
    M["roof_dk"] = kit.plastic("#5f5a52", 0.8, name="roof_dk")
    M["dark"] = kit.plastic("#2a2622", 0.8, name="dark")
    M["wood"] = kit.planks("#a98c62", "#7c6342", scale=2.0, axis="X", name="wood_a")
    M["wood_dk"] = kit.planks("#6e5a40", "#4a3b28", scale=2.0, axis="X", name="wood_dk")
    M["wood_grey"] = kit.planks("#9a9082", "#70685c", scale=2.0, axis="Z", name="wood_grey")
    M["shed"] = kit.planks("#9b8f7c", "#6f6656", scale=1.6, axis="Z", name="shed_wood")
    M["board"] = kit.planks("#a07f55", "#6f5638", scale=3.0, axis="Z", name="board_wood")
    M["metal"] = kit.metal("#8a8d90", 0.4, name="metal_s")
    M["tin"] = kit.metal("#a9adb2", 0.45, name="tin")
    M["honey"] = kit.plastic("#e3a53a", 0.5, name="honey")
    M["jar"] = kit.glass("#e8f0f0", name="jar")
    M["sea"] = kit.plastic("#3f7fa8", 0.3, name="sea_far")
    M["sea_near"] = kit.plastic("#3f7fa8", 0.22, name="sea_near")
    M["cobble"] = kit.cobbles("#a39a8a", "#c9c0ae", "#6a6358", scale=3.0, wet=0.05, name="quay_cobble")
    M["deck"] = kit.planks("#b3a283", "#8a7b60", scale=2.2, axis="X", name="deck")
    M["rail"] = kit.plastic("#f1ede2", 0.55, name="rail_white")
    M["hull"] = kit.plastic("#f1ede2", 0.5, name="hull_white")
    M["blue"] = kit.plastic("#3f7fa8", 0.5, name="stripe_blue")
    M["hut"] = kit.planks("#c9b48a", "#9d8a64", scale=2.0, axis="Z", name="hut_wood")
    M["shutter"] = kit.plastic("#7d8a8f", 0.6, name="shutter_grey")
    M["stripe_a"] = kit.plastic("#f1ede2", 0.6, name="stripe_cream")
    M["stripe_b"] = kit.plastic("#d4634a", 0.6, name="stripe_coral")
    M["bush"] = kit.plastic("#5e8a3c", 0.9, name="bush")
    return M


# ------------------------------------------------------------------------------------------------ build


# the light, one preset per place and hour: (sky, sky strength, sun elevation, sun azimuth, sun colour, sun power,
# fog colour, fog density). Azimuth: degrees of the sun's position round from +y toward +x.
LOOKS = {
    "day": ("#9cc8ea", 1.0, 44, 205, "#fff2dc", 3.4, "#bcd6ea", 0.0035),
    "low": ("#a4c0dc", 0.8, 20, 305, "#ffe0ae", 3.4, "#d0d4cc", 0.004),
    "late": ("#a9c4de", 0.9, 28, 215, "#ffd9a0", 3.0, "#d8d2c4", 0.004),
    "gold": ("#e8b890", 0.75, 13, 235, "#ffb868", 2.6, "#e8c4a0", 0.006),
    "dusk": ("#7a6a96", 0.45, 5, 240, "#ff8a50", 1.5, "#6a5a7a", 0.008),
    "night": ("#1a2650", 0.5, 38, 220, "#8fa6ff", 1.5, "#1a2444", 0.006),
}
SMOKE_GREY = "#8d9197"


def look_of(sid: str, n: int) -> str:
    """n is the narration line a shot sits on (the shot's "n" in story.json)."""
    if sid in ("S27", "S43"):
        return "late"
    if 15 <= n <= 18 or 61 <= n <= 65:
        return "gold"
    if n in (24, 25, 26, 27, 30, 31):
        return "low"
    if n == 37:
        return "dusk"
    if n == 38:
        return "night"
    return "day"


def build(kit, story, tl):
    ctx = {"story": story, "nmap": {sh_["id"]: sh_.get("n", 0) for sh_ in story["shots"]}}
    M = materials(kit)
    kit.light("sun", "SUN", (0, 0, 20), 3.4, "#fff2dc")
    kit.LIGHTS["sun"]["light"].angle = math.radians(2.5)
    # the Hover's three lights (each is 0 unless a shot asks): a soft front fill dead on him, a low side key, a cool rim
    kit.light("hv_fill", "POINT", (0, 0, 2), 1.0, "#fff4e0", size=0.9, shadow=False)
    kit.light("hv_key", "POINT", (0, 0, 0.3), 1.0, "#ffe2a8", size=0.35)
    kit.light("hv_rim", "POINT", (0, 0, 2), 1.0, "#9fc4ff", size=0.35)
    kit.light("board", "POINT", (-1.6, 2.3, 2.6), 1.0, "#fff1d8", size=0.8, shadow=False)
    build_yard(kit, ctx, M)
    build_pier(kit, ctx, M)
    # bees: a few small dark dots, never a swarm
    bee = kit.plastic("#f0a82a", 0.5, name="bee")
    ctx["bees"] = [kit.sphere(f"bee{i}", 0.05, (0, 0, -50), bee, seg=8) for i in range(14)]
    ctx["hover_bees"] = [kit.sphere(f"hbee{i}", 0.06, (0, 0, -50), bee, seg=8) for i in range(9)]
    ctx["lena_bees"] = [kit.sphere(f"lbee{i}", 0.05, (0, 0, -50), bee, seg=8) for i in range(3)]
    # the reveal's smoke: big soft translucent puffs round the Hover (S52 to S55)
    ctx["hpuffs"] = []
    for i in range(12):
        m = kit._new(f"hpuff{i}")
        nt = m.node_tree
        nt.nodes.remove(nt.nodes["Principled BSDF"])
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = kit.col("#7d8288")
        em.inputs["Strength"].default_value = 0.55
        mix = nt.nodes.new("ShaderNodeMixShader")
        mix.inputs[0].default_value = 0.16
        nt.links.new(tr.outputs[0], mix.inputs[1])
        nt.links.new(em.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
        ctx["hpuffs"].append(kit.sphere(f"hpuff{i}", 0.5, (0, 0, -50), m, seg=20))
    # smoke puffs from the smoker: soft grey spheres that grow, rise and fade
    ctx["puffs"] = []
    for i in range(7):
        m = kit._new(f"puff{i}")
        nt = m.node_tree
        nt.nodes.remove(nt.nodes["Principled BSDF"])
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = kit.col("#9ea2a8")
        em.inputs["Strength"].default_value = 0.9
        mix = nt.nodes.new("ShaderNodeMixShader")
        mix.inputs[0].default_value = 1.0
        nt.links.new(tr.outputs[0], mix.inputs[1])
        nt.links.new(em.outputs[0], mix.inputs[2])
        out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
        sp = kit.sphere(f"puff{i}", 0.2, (0, 0, -50), m, seg=10)
        ctx["puffs"].append((sp, mix))
    ctx["dials"] = {}
    ctx["veil_objs"] = {}
    ctx["lazy"] = False
    return ctx


# --------------------------------------------------------------------------------------------- animate


def _cues(tl, name):
    return [c for c in tl["cues"] if c["name"] == name]


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


def _sun_dir(el, az):
    e, a = math.radians(el), math.radians(az)
    return V((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)))


def _aim(ob, frm, to):
    d = V(to) - V(frm)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def _fog_nodes(kit):
    """Every material's fog: the multiply node ahead of the exponent, and the fog colour emission."""
    if FOG_NODES["built"]:
        return FOG_NODES["mul"], FOG_NODES["col"]
    mul, col = [], []
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        for nd in m.node_tree.nodes:
            if nd.type == "MATH" and nd.operation == "EXPONENT":
                src = nd.inputs[0].links[0].from_node if nd.inputs[0].links else None
                if src is not None and src.type == "MATH" and src.operation == "MULTIPLY":
                    mul.append(src)
            if nd.type == "MIX_SHADER" and len(nd.inputs[0].links) and len(nd.inputs[2].links) and nd.inputs[2].links[0].from_node.type == "EMISSION":
                col.append(nd.inputs[2].links[0].from_node)
    FOG_NODES.update(built=True, mul=mul, col=col)
    return mul, col


def _tail_key(who_keys, t):
    return None


def _dial_state(keys, t):
    """The dial's reading at t from its cue keys: discrete parts switch at the key, numbers ease over `ramp`."""
    ks = [k for k in keys if k["t"] <= t + 1e-9]
    if not ks:
        return None
    cur = {"val": "", "unit": 0, "frac": 1.0, "glow": 0.0, "vis": 1.0, "tone": "coral", "off": False, "mark": ""}
    hist = []
    for k in ks:
        before = dict(cur)
        for f in ("val", "unit", "tone", "off", "mark"):
            if f in k:
                cur[f] = k[f]
        tgt = {f: k[f] for f in ("frac", "glow", "vis") if f in k}
        hist.append((k["t"], k.get("ramp", 0.0), before, tgt))
        for f, v in tgt.items():
            cur[f] = v
    # replay with easing: start from defaults, apply each key's numeric change over its ramp
    vals = {"frac": 1.0, "glow": 0.0, "vis": 1.0}
    for (t0, ramp, _b, tgt) in hist:
        for f, v in tgt.items():
            if ramp > 1e-6 and t < t0 + ramp:
                u = ss((t - t0) / ramp)
                vals[f] = vals[f] + (v - vals[f]) * u
            else:
                vals[f] = v
    out = dict(cur)
    out.update(vals)
    return out


def _lazy_init(kit, story, tl, ctx):
    """Things that hang on the characters (they're built after build()): veils and bags."""
    S = rig.S
    for who, tone in (("lena", {"band": "#8aa37f", "mesh": "#f4f1e8", "alpha": 0.12}), ("me", {"band": "#d9d1bd", "mesh": "#ece6d6", "alpha": 0.12})):
        hg = bpy.data.objects.get(f"{who}.headg")
        if hg is not None:
            ctx["veil_objs"][who] = make_veil(kit, f"veil_{who}", hg, 1 / S, (0, 0, 0.6), tone,
                                              rot=(0.0, 0.2, 0.0) if who == "me" else (0, 0, 0))
    # her own hat, hung behind her shoulders when it isn't on
    torso = bpy.data.objects.get("lena.torso")
    if torso is not None:
        ctx["lena_hat"] = make_veil(kit, "lena_hatback", torso, 1 / S, (0, 0.62, 1.55), {"band": "#8aa37f", "mesh": "#f4f1e8"},
                                    rot=(math.radians(90), 0, 0), hang=False)
    # the woman's shopping bag, a box at her right hand
    arm = bpy.data.objects.get("b2.arm1")
    if arm is not None:
        kit.box("bag", (0.95, 0.5, 1.0), (0.0, -0.1, -2.2), kit.plastic("#d4634a", 0.8, name="bag"), arm, bevel=0.05)
    # the board's two veils on their hooks
    bx, bz = ctx["board_pos"]
    ctx["board_veils"] = []
    for k, (yy, tone) in enumerate(((1.75, {"band": "#8aa37f", "mesh": "#f4f1e8", "alpha": 0.4}),
                                    (2.75, {"band": "#d9d1bd", "mesh": "#ece6d6", "alpha": 0.45}))):
        v = make_veil(kit, f"bveil{k}", None, 1.0, (bx + 0.36, yy, bz + 0.12), tone, mesh_len=0.38)
        ctx["board_veils"].append(v)
    # a few ambient bee anchors near the hives
    ctx["lazy"] = True


def _cam_pos(story, tl, t):
    from blocky import bl_story
    shot = _shot(tl, t)
    spec = next(s for s in story["shots"] if s["id"] == shot["id"])
    loc, tgt, lens, roll = bl_story.cam_at(spec, shot, t, {}, tl)
    return V(loc), V(tgt)


def animate(kit, story, tl, t, ctx):
    over = {}
    if not ctx["lazy"]:
        _lazy_init(kit, story, tl, ctx)
    shot = _shot(tl, t)
    sid = shot["id"]
    n = ctx["nmap"][sid]
    look = LOOKS[look_of(sid, n)]
    sky, sky_s, el, az, scol, spow, fcol, fd = look
    if n in (44, 45, 46, 47) or sid == "S64":    # the reveal: the weak sun sits behind him, low, so nothing lights his front
        el, az, spow = 16, 15, 1.6
    # ---- the smoke: a slow fade in over 3 s from L40, thinning over 3 s from L59 (no step anywhere)
    sin_ = _cues(tl, "smoke_in")
    sout = _cues(tl, "smoke_out")
    sm = 0.0
    if sin_:
        sm = ss((t - sin_[0]["t"]) / 3.0)
    if sout:
        sm *= 1.0 - ss((t - sout[0]["t"]) / 3.0)
    if n >= 61:
        sm = 0.0
    c = lambda h: kit.col(h)[:3]
    mixc = lambda a, b, u: tuple(x + (y - x) * u for x, y in zip(a, b))
    sunE = spow * (1 - 0.72 * sm)
    sk = mixc(c(sky), c(SMOKE_GREY), sm)
    w = bpy.context.scene.world.node_tree.nodes["Background"]
    w.inputs["Color"].default_value = (*sk, 1)
    w.inputs["Strength"].default_value = sky_s * (1 - 0.25 * sm)
    sun = kit.LIGHTS["sun"]
    sun["obj"].rotation_euler = (V((0, 0, 0)) - _sun_dir(el, az)).to_track_quat("-Z", "Y").to_euler()
    sun["light"].color = c(scol)
    over["sun"] = sunE / sun["base"]
    mul, cols = _fog_nodes(kit)
    base_d = fd
    dens = base_d + 0.2 * sm
    fogc = mixc(c(fcol), c(SMOKE_GREY), sm)
    for nd in mul:
        nd.inputs[1].default_value = -dens
    for nd in cols:
        nd.inputs["Color"].default_value = (*fogc, 1)
    # ---- the gate: shut until Saturday, then open (a cut apart, so it never moves on camera)
    opened = 39 <= n <= 60 or n >= 66
    ctx["gate"][0].rotation_euler = (0, 0, math.radians(95 if opened else 0))
    ctx["gate"][1].rotation_euler = (0, 0, math.radians(-95 if opened else 0))
    for o in ctx["crate_gate"]:
        o.hide_render = not (39 <= n <= 43)
    # ---- who's where, and the Hover
    st = {nm: acting.state(tl, nm, t) for nm in story["cast"]}
    hv = st["hover"]
    hover_on = not hv["hidden"]
    cam, tgt = _cam_pos(story, tl, t)
    # the Hover's lights follow him and the camera
    prof = _hover_light(n, sid)
    if hover_on and prof:
        hp = V((hv["x"], hv["y"], hv["z"]))
        toc = V((cam.x - hp.x, cam.y - hp.y, 0.0))
        toc = toc.normalized() if toc.length > 1e-4 else V((0, -1, 0))
        side = V((-toc.y, toc.x, 0.0))
        away = V((0, 0, 0)) - toc
        for nm, (off, watt, colr) in prof.items():
            ob = kit.LIGHTS[nm]["obj"]
            ob.location = hp + toc * off[0] + side * off[1] + V((0, 0, off[2]))
            kit.LIGHTS[nm]["light"].color = c(colr)
            over[nm] = watt
    else:
        for nm in ("hv_fill", "hv_key", "hv_rim"):
            over[nm] = 0.0
    over["board"] = 300.0 if sid == "S42" else (70.0 if (n in (33, 34, 36, 37, 67) or sid == "S62") else 0.0)
    # ---- bees
    night = look_of(sid, n) in ("night", "dusk")
    for i, b in enumerate(ctx["bees"]):
        hv_ = ctx["hives"][(i * 5) % 12]
        a = t * (0.6 + 0.05 * i) + i * 1.9
        r = 0.35 + 0.12 * (i % 3)
        p = hv_.location
        b.location = (p.x + r * math.cos(a) * 1.0, p.y - 0.3 + r * math.sin(a * 1.3) * 0.8, p.z + 0.55 + 0.25 * math.sin(a * 0.7 + i))
        b.hide_render = night or n < 12 or n > 69 or (V(b.location) - cam).length < 1.6
    for i, b in enumerate(ctx["hover_bees"]):
        a = t * 0.9 + i * 1.57
        rr = (0.34 + 0.1 * (i % 3)) * (2.4 if sid in ("S00a", "S00b") else 1.0)     # S00: wide ring, so no dot sits on his face
        b.location = (hv["x"] + rr * math.cos(a), hv["y"] + rr * math.sin(a), hv["z"] + 1.0 + 0.14 * i + 0.05 * math.sin(a * 2 + i))
        b.hide_render = (not hover_on) or sid == "S00a" or (V(b.location) - cam).length < 0.9
        b.scale = (0.3 if sid in ("S00a", "S00b") else 1.0,) * 3     # S00 is close: small dark-gold specks, not balls
    revealing = hover_on and (n in (44, 45, 46, 47) or sid == "S64")
    for i, sp in enumerate(ctx["hpuffs"]):
        sp.hide_render = not revealing
        if revealing:
            a = i * 2.4 + t * 0.12
            rr = 0.55 + 0.3 * (i % 4)
            sp.location = (hv["x"] + rr * math.cos(a), hv["y"] + rr * math.sin(a), hv["z"] + 0.45 + 0.17 * i + 0.1 * math.sin(t * 0.5 + i))
            sp.scale = (1.1 + 0.15 * (i % 3),) * 3
    ls = st["lena"]
    lena_work = (not ls["hidden"]) and (n in (17, 21, 23, 40, 41, 50))
    for i, b in enumerate(ctx["lena_bees"]):
        a = t * 0.8 + i * 2.1
        b.location = (ls["x"] + 0.5 * math.cos(a), ls["y"] + 0.5 * math.sin(a * 1.2), ls["z"] + 1.1 + 0.3 * math.sin(a + i))
        b.hide_render = not lena_work
    # ---- smoker puffs, while Lena puffs (S48 to S50)
    puffing = [c_ for c_ in _cues(tl, "puff")]
    tip = ctx["smoker_tip"]
    for i, (sp, mix) in enumerate(ctx["puffs"]):
        on = False
        for pc in puffing:
            x = (t - pc["t"] - i * 0.45) % 3.2
            if pc["t"] <= t < pc["t"] + pc.get("dur", 4.0):
                on = True
                u = x / 3.2
                sp.location = (tip[0] + 0.12 * u + 0.1 * math.sin(i + u * 3), tip[1] + 0.08 * math.sin(i * 2 + u * 2), tip[2] + 0.1 + 0.9 * u)
                sp.scale = (0.4 + 1.4 * u,) * 3
                mix.inputs[0].default_value = 1.0 - 0.55 * math.sin(math.pi * u) ** 1.4 * ss(u * 8)
        sp.hide_render = not on
    # ---- gulls drift
    for i, g in enumerate(ctx["gulls"]):
        g.location = (PX + (i - 3) * 6 + 2.5 * math.sin(t * 0.3 + i), 60 + 7 * i + 3 * math.cos(t * 0.25 + i), 12 + 2 * (i % 3) + 0.5 * math.sin(t * 0.7 + i))
        g.rotation_euler = (0, 0.15 * math.sin(t * 0.7 + i), 0.4 * math.sin(t * 0.2 + i))
    # ---- veils: worn (on the head), or hung on the board
    veil_cues = _cues(tl, "veil")
    worn = {}
    for who, obj in ctx["veil_objs"].items():
        on = False
        for vc in veil_cues:
            if vc["who"] == who and vc["t"] <= t + 1e-9:
                on = bool(vc["on"])
        worn[who] = on and not st[who]["hidden"]
        obj.hide_render = not worn[who]
        for ch in obj.children_recursive:
            ch.hide_render = not worn[who]
    if "lena_hat" in ctx:
        hat_on = (not st["lena"]["hidden"]) and not worn.get("lena", False)
        ctx["lena_hat"].hide_render = not hat_on
        for ch in ctx["lena_hat"].children_recursive:
            ch.hide_render = not hat_on
    for k, v in enumerate(ctx["board_veils"]):
        gone = _cues(tl, "veil_take")
        hide = n >= 40 if k == 0 else (n >= 53 or (bool(gone) and t >= gone[0]["t"]))   # hers goes on Saturday morning; mine stays on its hook until it is taken in S62
        v.hide_render = hide
        for ch in v.children_recursive:
            ch.hide_render = hide
    # ---- the steam on Lena's mesh in S77: a slow fade, never a step
    mm = kit.MATS.get("veilmesh #f4f1e8 0.12")
    if mm is not None:
        a_ = 0.12 + (0.55 * ss((t - shot["start"]) / 1.2) if n == 66 else 0.0)
        mm.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = a_
    # ---- the dials
    _dials(kit, story, tl, t, ctx, st, cam, over)
    return over


def _hover_light(n: int, sid: str = ""):
    """Per shot: {light: (offset toward the camera, sideways, up, watts, colour)} relative to the Hover's feet."""
    if n in (23, 24, 25, 26, 27):    # Wednesday: front fill dead on, key low and side, cool rim
        return {"hv_fill": ((2.2, 0.0, 1.5), 55, "#fff4e0"), "hv_key": ((0.8, 1.3, 0.2), 70, "#ffe2a8"), "hv_rim": ((-1.4, -1.0, 1.9), 260, "#9fc4ff")}
    if n in (30, 31, 33):
        return {"hv_fill": ((2.4, 0.0, 1.5), 50, "#fff4e0"), "hv_key": ((0.8, 1.3, 0.2), 60, "#ffe2a8"), "hv_rim": ((-1.4, -1.0, 1.9), 220, "#9fc4ff")}
    if n == 37:                      # dusk
        return {"hv_fill": ((2.4, 0.0, 1.5), 60, "#ffd9b0"), "hv_key": ((0.8, 1.3, 0.2), 40, "#ffb070"), "hv_rim": ((-1.4, -1.0, 1.9), 150, "#9fc4ff")}
    if n == 38:                      # moonlit close on his face
        return {"hv_fill": ((1.6, 0.0, 1.6), 30, "#cfe0ff"), "hv_key": ((0.6, 1.0, 1.2), 18, "#b8ccff"), "hv_rim": ((-1.2, -0.8, 2.0), 140, "#9fc4ff")}
    if n in (44, 45, 46, 47) or sid == "S64":    # in the smoke: no front fill; a warm key from below and behind, a cool rim
        return {"hv_fill": ((2.0, 0.0, 1.6), 0.0, "#fff4e0"), "hv_key": ((-0.9, 0.5, 0.05), 520, "#ffcf7a"), "hv_rim": ((-1.5, -1.0, 2.1), 520, "#a9ccff")}
    return None


# ---------------------------------------------------------------------------------------------- dials


def _dials(kit, story, tl, t, ctx, st, cam, over):
    by_who = {}
    for cu in _cues(tl, "dial"):
        by_who.setdefault(cu["who"], []).append(cu)
    spec = story["cast"]
    for who, keys in by_who.items():
        d = ctx["dials"].get(who)
        if d is None:
            d = _make_dial(kit, who, ctx)
        s = st[who]
        state = _dial_state(keys, t)
        show = state is not None and not state["off"] and not s["hidden"]
        for ob in d["objs"]:
            ob.hide_render = not show
        if not show:
            continue
        h = spec[who].get("height", 1.0)
        top = (1.775 + 0.04 + spec[who].get("dial_dz", 0.0)) * h
        pos = V((s["x"], s["y"], s["z"] + top + 0.12 + DIAL_R))
        if s["lean"]:                      # a bent head carries its dial forward and down
            hh = (1.8 * h)
            pos.x += math.sin(s["yaw"]) * hh * math.sin(s["lean"])
            pos.y += -math.cos(s["yaw"]) * hh * math.sin(s["lean"])
            pos.z -= hh * (1 - math.cos(s["lean"]))
        d["root"].location = pos
        look = (cam - pos)
        d["root"].rotation_euler = look.to_track_quat("Z", "Y").to_euler()
        key = (state["val"], int(state["unit"]), round(state["frac"] * 60), round(state["glow"] * 10), round(state["vis"] * 10), state["tone"], state["mark"])
        if key != d["key"]:
            # a fresh image datablock for every new reading: Cycles (persistent data) doesn't see pixels changed in place
            arr = dialart.dial(state["val"], int(state["unit"]), key[2] / 60.0, key[3] / 10.0, key[4] / 10.0, state["tone"], 512, state["mark"])
            rgba = np.ones((512, 512, 4), np.float32)
            rgba[..., :3] = arr
            d["n"] = d.get("n", 0) + 1
            img = bpy.data.images.new(f"dial_{who}_{d['n']}", 512, 512, alpha=False)
            img.colorspace_settings.name = "sRGB"
            img.pixels.foreach_set(np.flipud(rgba).ravel())
            img.update()
            d["tex"].image = img
            old_img = d["img"]
            d["img"] = img
            d["key"] = key
            if old_img is not None and old_img.name != f"dial_{who}":
                bpy.data.images.remove(old_img)
        d["em"].inputs["Strength"].default_value = 0.8 + 0.1 * state["glow"]     # 0.8: a cream face at 1.0 clipped to white under the grade (flash)


def _make_dial(kit, who, ctx):
    img = bpy.data.images.new(f"dial_{who}", 512, 512, alpha=False)
    img.colorspace_settings.name = "sRGB"
    m = kit._new(f"dial_face_{who}")
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Linear"
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(em.outputs[0], out.inputs["Surface"])   # not fogged: the dial reads through smoke
    root = kit.empty(f"dial_{who}", (0, 0, -50))
    face = disc_mesh(kit, f"dial_{who}.face", DIAL_R, m, 64, root, (0, 0, 0.0))
    rim_m = kit.metal("#b8913e", 0.35, name="brass")
    rim = kit.cyl(f"dial_{who}.back", DIAL_R + 0.018, 0.03, (0, 0, -0.017), rim_m, root, n=48)
    lip = ring_mesh(kit, f"dial_{who}.lip", DIAL_R - 0.002, DIAL_R + 0.02, 0.016, rim_m, root)
    d = {"root": root, "objs": [root] + list(root.children_recursive), "img": None, "tex": tex, "em": em, "key": None}
    ctx["dials"][who] = d
    return d
