"""ep35 Fire ring: a high autumn moor, an old stone fire ring with three seats, a moss-green tent, a drystone wall
and field gate down the hill, and Big Hands. Built from kit.py's parts; nothing here is shared with another set.

Coordinates (metres): the ring's middle is (0, 0), ground z = 0 there. Seats: Grandad's south (0, -1.9), mine north
(0, 1.9), the empty slab west (-1.9, 0). The tent is 3 m west of the ring (centre x = -4.6), its door facing south.
Three stepping stones run east into the bog: (4, 0), (6, 0.5), (8, 0.2). The hill falls away south to the wall at
y = -40; the gate is in the wall at x = -1.4. Grandad's front door is a separate set far east at (300, 0).
A character facing -y has yaw 0, facing +x yaw 90, facing -x yaw -90, facing +y yaw 180.

BIG HANDS (a cast member "bighands" posed from acting like everyone else; this file adds its two mitten hands to
its arm pivots, a tall tan block over its head so the face sits low, and two ember catch points): ordinary height,
R6 body, heather-purple jumper with a peat-brown diamond knit, a small calm face set low on a tall head, and hands
0.9 m tall and 0.6 m wide, block mittens with four finger blocks and a thumb, on normal sleeves.

Cues read here (all optional):
- look: {"id": ...} the whole light from here (LOOKS)
- fire: {"level": 1.0 | 0.0..1.0}   flames and light (0 = embers only)
- glow: {"v": strength, "mix": 0 orange .. 1 moon blue, "dur": s} the tent canvas
- shadow: {"mode": "hands" | "finger" | "none"} the hand shadows on the tent's west wall / the finger on the bag
- phone / flask / mug / pack / stick: {"pos": [x, y, z], "yaw": deg, "tilt": deg} or {"hand": "dad.arm1", "offset": [...]}
  or {"hidden": true}; pack also {"worn": true}
- turves: {"on": bool}      doorfrost: {"on": bool}      dry: {"on": bool} (the dry patch on the empty seat)
- handtilt: {"deg": n}      how far Big Hands' palms are tipped (default -75)
"""

from __future__ import annotations

import math

import bpy
import numpy as np
from mathutils import Vector as V

# ------------------------------------------------------------------------------------------------ places
SEAT_G = (0.0, -1.9)
SEAT_M = (0.0, 1.9)
SEAT_E = (-1.9, 0.0)
SEAT_TOP = 0.40
SLAB_TOP = 0.62
STONES = ((4.0, 0.0), (6.0, 0.5), (8.0, 0.2))
STONE_TOP = 0.05
TENT_X, TENT_Y = -4.6, 0.2
TENT_W, TENT_L, TENT_H = 2.8, 3.0, 1.75
WALL_Y = -40.0
GATE_X = -1.4
HOME = (300.0, 0.0)
FIRE = (0.3, 0.0)
POT = (-0.15, -0.05)
HEARTH_TOP = 0.07

FROST_NODES: list = []
GLOW = {}


def ground(x, y):
    """The moor's height: a slope falling south from the ring, a hollow of bog east of it, small lumps."""
    z = -0.09 * max(0.0, -y - 4.0)
    r = math.hypot(x, y)
    flat = 1.0 - _ss((r - 4.5) / 6.0)
    lump = 0.18 * math.sin(x * 0.41 + 1.3) * math.cos(y * 0.37) + 0.12 * math.sin(x * 0.17 - y * 0.23 + 2.0)
    z += lump * (1.0 - flat)
    # the bog: a shallow bowl east of the ring where the stepping stones cross
    bx = _ss((x - 2.4) / 1.6) * (1.0 - _ss((x - 17.0) / 5.0))
    by = 1.0 - _ss((abs(y - 0.3) - 5.0) / 5.0)
    z -= 0.62 * bx * by
    return z


WATER_Z = -0.2


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return sorted((c for c in tl.get("cues", []) if c["name"] == name), key=lambda c: c["t"])


def _last(cs, t):
    cur = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            cur = c
    return cur


def _switch(cs, attr, t, default):
    v = default
    for c in cs:
        if attr in c and c["t"] <= t + 1e-9:
            v = c[attr]
    return v


def _ease_to(cs, t, key, default):
    """A cue value that eases over the cue's `dur` from the previous cue's value."""
    prev, cur = default, None
    for c in cs:
        if key in c and c["t"] <= t + 1e-9:
            prev, cur = (cur[key] if cur else prev), c
    if cur is None:
        return default
    return prev + (cur[key] - prev) * (_ss((t - cur["t"]) / cur["dur"]) if cur.get("dur") else 1.0)


# ------------------------------------------------------------------------------------------------ materials


def _mk(kit, name):
    m = kit._new(name)
    nt = m.node_tree
    return m, nt.nodes, nt.links, nt.nodes["Principled BSDF"]


def _noise(N, L, scale, detail=4.0, rough=0.55, kind="Object"):
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = detail
    nz.inputs["Roughness"].default_value = rough
    L.new(tc.outputs[kind], nz.inputs["Vector"])
    return nz.outputs["Fac"]


def _ramp(N, L, fac, stops):
    r = N.new("ShaderNodeValToRGB")
    els = r.color_ramp.elements
    while len(els) < len(stops):
        els.new(0.5)
    for e, (p, c) in zip(els, stops):
        e.position = p
        e.color = c
    L.new(fac, r.inputs["Fac"])
    return r.outputs["Color"]


def _frosted(kit, m, N, L, b, color_out, up_only=True, amount=1.0):
    """Mix a frost-white over a colour on faces that look up, by a Value node the look sets."""
    v = N.new("ShaderNodeValue")
    v.outputs[0].default_value = 0.0
    FROST_NODES.append(v)
    g = N.new("ShaderNodeNewGeometry")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(g.outputs["Normal"], sep.inputs[0])
    up = N.new("ShaderNodeMapRange")
    up.inputs["From Min"].default_value = 0.35
    up.inputs["From Max"].default_value = 0.75
    L.new(sep.outputs["Z"], up.inputs["Value"])
    nz = _noise(N, L, 9.0, 3.0)
    thr = N.new("ShaderNodeMapRange")
    thr.inputs["From Min"].default_value = 0.18
    thr.inputs["From Max"].default_value = 0.34
    L.new(nz, thr.inputs["Value"])
    m1 = N.new("ShaderNodeMath")
    m1.operation = "MULTIPLY"
    L.new(up.outputs["Result"], m1.inputs[0])
    if amount != 1.0:
        am = N.new("ShaderNodeMath")
        am.operation = "MULTIPLY"
        am.inputs[1].default_value = amount
        L.new(v.outputs[0], am.inputs[0])
        L.new(am.outputs[0], m1.inputs[1])
    else:
        L.new(v.outputs[0], m1.inputs[1])
    m2 = N.new("ShaderNodeMath")
    m2.operation = "MULTIPLY"
    L.new(m1.outputs[0], m2.inputs[0])
    L.new(thr.outputs["Result"], m2.inputs[1])
    mix = N.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["B"].default_value = kit.col("#e4ebf2")
    L.new(color_out, mix.inputs["A"])
    L.new(m2.outputs[0], mix.inputs["Factor"])
    L.new(mix.outputs["Result"], b.inputs["Base Color"])
    return mix


def moor_mat(kit):
    m, N, L, b = _mk(kit, "moor")
    big = _noise(N, L, 0.35, 3.0)
    fine = _noise(N, L, 3.0, 4.0)
    col = _ramp(N, L, big, [(0.30, kit.col("#3a2a1f")), (0.5, kit.col("#4d3a52")), (0.72, kit.col("#4a4a2c"))])
    dark = N.new("ShaderNodeMapRange")
    dark.inputs["To Min"].default_value = 0.55
    dark.inputs["To Max"].default_value = 1.1
    L.new(fine, dark.inputs["Value"])
    mul = N.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    L.new(col, mul.inputs["A"])
    cc = N.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        L.new(dark.outputs["Result"], cc.inputs[k])
    L.new(cc.outputs["Color"], mul.inputs["B"])
    _frosted(kit, m, N, L, b, mul.outputs["Result"])
    b.inputs["Roughness"].default_value = 0.95
    bp = N.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.5
    bp.inputs["Distance"].default_value = 0.05
    L.new(fine, bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    kit._fogged(m, b.outputs[0])
    return m


def heather_mat(kit):
    m, N, L, b = _mk(kit, "heather")
    big = _noise(N, L, 0.5, 2.0)
    col = _ramp(N, L, big, [(0.30, kit.col("#4a2e55")), (0.55, kit.col("#6a4a7c")), (0.75, kit.col("#3f3424"))])
    _frosted(kit, m, N, L, b, col)
    b.inputs["Roughness"].default_value = 0.9
    kit._fogged(m, b.outputs[0])
    return m


def stone_mat(kit, name="stone", c0="#55575b", c1="#8d8e8b", scale=4.0, frost=True, amount=1.0):
    m, N, L, b = _mk(kit, name)
    n1 = _noise(N, L, scale, 5.0)
    n2 = _noise(N, L, scale * 0.35, 2.0)
    col = _ramp(N, L, n1, [(0.35, kit.col(c0)), (0.65, kit.col(c1))])
    mos = N.new("ShaderNodeMix")
    mos.data_type = "RGBA"
    mos.inputs["A"].default_value = kit.col("#5c6247")
    L.new(col, mos.inputs["A"])
    mos.inputs["B"].default_value = kit.col("#586040")
    th = N.new("ShaderNodeMapRange")
    th.inputs["From Min"].default_value = 0.55
    th.inputs["From Max"].default_value = 0.7
    th.inputs["To Max"].default_value = 0.55
    L.new(n2, th.inputs["Value"])
    L.new(th.outputs["Result"], mos.inputs["Factor"])
    if frost:
        _frosted(kit, m, N, L, b, mos.outputs["Result"], amount=amount)
    else:
        L.new(mos.outputs["Result"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.9
    bp = N.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.6
    bp.inputs["Distance"].default_value = 0.03
    L.new(n1, bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    kit._fogged(m, b.outputs[0])
    return m


def canvas_mat(kit):
    """Moss-green canvas that can glow from inside: principled + an emission whose colour and strength the glow cue sets."""
    m, N, L, b = _mk(kit, "canvas")
    b.inputs["Base Color"].default_value = kit.col("#5f7348")
    b.inputs["Roughness"].default_value = 0.85
    nz = _noise(N, L, 30.0, 2.0)
    bp = N.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.2
    bp.inputs["Distance"].default_value = 0.004
    L.new(nz, bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col("#ff8a3d")
    em.inputs["Strength"].default_value = 0.0
    GLOW["em"] = em
    add = N.new("ShaderNodeAddShader")
    L.new(b.outputs[0], add.inputs[0])
    L.new(em.outputs[0], add.inputs[1])
    kit._fogged(m, add.outputs[0])
    return m


def flat_emit(kit, name, hexc, strength):
    return kit.emit(hexc, strength, name)


def water_mat(kit):
    m, N, L, b = _mk(kit, "bog water")
    b.inputs["Base Color"].default_value = kit.col("#06080a")
    b.inputs["Roughness"].default_value = 0.04
    b.inputs["Metallic"].default_value = 0.0
    kit._fogged(m, b.outputs[0])
    return m


def steam_mat(kit):
    m = kit._new("steam")
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col("#d8c8b8")
    em.inputs["Strength"].default_value = 0.55
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.12
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def materials(kit):
    M = {}
    M["moor"] = moor_mat(kit)
    M["heather"] = heather_mat(kit)
    M["stone"] = stone_mat(kit)
    M["seat"] = stone_mat(kit, "seat", "#6b6c70", "#a09f98", 5.0)
    M["slab"] = stone_mat(kit, "slab", "#5d5e62", "#908f8a", 5.0, amount=0.45)
    M["hearth"] = stone_mat(kit, "hearth", "#4a4b4f", "#7a7a78", 6.0, frost=False)
    M["wallstone"] = stone_mat(kit, "wallstone", "#4c4e50", "#807f7a", 8.0)
    M["canvas"] = canvas_mat(kit)
    M["water"] = water_mat(kit)
    M["steam"] = steam_mat(kit)
    M["log"] = kit.plastic("#2a1c14", 0.9, "log")
    M["turf"] = kit.plastic("#2f3a1c", 0.95, "turf")
    M["pot"] = kit.plastic("#16161a", 0.5, "pot")
    M["stew"] = kit.plastic("#5a2e14", 0.6, "stew")
    M["tin"] = kit.metal("#9a9da0", 0.35, "tin")
    M["flask"] = kit.plastic("#2f6b3b", 0.35, "flask")
    M["flaskdark"] = kit.plastic("#16381d", 0.5, "flask dent")
    M["flasklip"] = kit.plastic("#b8dcb4", 0.25, "flask dent lip", spec=0.9)
    M["flaskcap"] = kit.plastic("#2a2a2c", 0.5, "flask cap")
    M["packm"] = kit.plastic("#7a3b22", 0.85, "pack")
    M["packin"] = kit.plastic("#120d0a", 0.9, "pack in")
    M["stroke"] = kit.plastic("#7a4f8c", 0.7, "stroke")
    M["groundsheet"] = kit.plastic("#2c3a2a", 0.9, "groundsheet")
    M["bagd"] = kit.plastic("#7d3a2e", 0.9, "bag dad")
    M["bagm"] = kit.plastic("#284468", 0.9, "bag me")
    M["shadow"] = kit.emit("#0a0706", 1.0, "shadow")
    M["flame"] = kit.emit("#ff9a3a", 6.0, "flame")
    M["flame2"] = kit.emit("#ffd27a", 9.0, "flame core")
    M["ember"] = kit.emit("#ff4a10", 3.0, "ember")
    M["phonebody"] = kit.emit("#3a5470", 1.4, "phone")
    M["screen"] = kit.emit("#a8d4ff", 3.5, "screen")
    M["wood"] = kit.planks("#6b5a40", "#4a3c28", 1.2, "X", "gate wood")
    M["gatepost"] = stone_mat(kit, "gatepost", "#5a5c5e", "#8b8a84", 7.0)
    M["track"] = kit.plastic("#6b5e46", 0.95, "track")
    M["field"] = kit.plastic("#5c6a3a", 0.95, "field")
    M["hill"] = kit.plastic("#2c2a38", 1.0, "hill")
    M["bighand"] = kit.plastic("#a8946e", 0.5)
    M["bigtop"] = kit.plastic("#b8a27c", 0.5)
    M["catch"] = kit.emit("#ffb060", 14.0, "catch light")
    M["frost"] = kit.plastic("#dfe6ee", 0.8, "frost sheet")
    M["dry"] = kit.plastic("#2e2c2a", 0.6, "dry patch")
    # Grandad's front door set
    M["brick"] = kit.bricks("#8a5a46", "#6e4636", "#7a756c", 1.0, "home bricks")
    M["door"] = kit.plastic("#1d3a78", 0.45, "blue door")
    M["step"] = stone_mat(kit, "step", "#8d8c88", "#b4b1a8", 3.0, frost=False)
    M["pave"] = stone_mat(kit, "pave", "#6e6c68", "#9a968c", 2.0, frost=False)
    M["glass"] = kit.plastic("#2a3440", 0.15, "window")
    M["curtain"] = kit.plastic("#c9b98a", 0.9, "curtain")
    M["plant"] = kit.plastic("#3e6a32", 0.9, "plant")
    M["pottery"] = kit.plastic("#a55a36", 0.8, "pottery")
    M["lawn"] = kit.plastic("#5f8a3c", 0.95, "lawn")
    return M


# ------------------------------------------------------------------------------------------------ shapes


def blocks_mesh(kit, name, boxes, mat, parent=None):
    """Many boxes as one mesh: boxes = [(cx, cy, cz, sx, sy, sz, yaw)]."""
    verts, faces = [], []
    for cx, cy, cz, sx, sy, sz, yaw in boxes:
        c, s = math.cos(yaw), math.sin(yaw)
        base = len(verts)
        for dx, dy, dz in ((-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)):
            x, y = dx * sx / 2, dy * sy / 2
            verts.append((cx + x * c - y * s, cy + x * s + y * c, cz + dz * sz / 2))
        faces += [tuple(base + i for i in f) for f in kit.BOX_FACES]
    return kit.mesh_obj(name, verts, faces, mat, parent)


def tuft_mesh(kit, name, pts, mat, rng):
    """Heather clumps: squashed six-sided blocks (one mesh)."""
    verts, faces = [], []
    for x, y, z, r, h in pts:
        base = len(verts)
        a0 = rng.uniform(0, math.tau)
        for k in range(5):
            a = a0 + k * math.tau / 5
            verts.append((x + r * math.cos(a), y + r * math.sin(a), z))
        for k in range(5):
            a = a0 + k * math.tau / 5 + 0.3
            verts.append((x + r * 0.7 * math.cos(a), y + r * 0.7 * math.sin(a), z + h * 0.8))
        verts.append((x + rng.uniform(-0.05, 0.05), y + rng.uniform(-0.05, 0.05), z + h))
        for k in range(5):
            j = (k + 1) % 5
            faces.append((base + k, base + j, base + 5 + j, base + 5 + k))
            faces.append((base + 5 + k, base + 5 + j, base + 10))
        faces.append(tuple(base + k for k in reversed(range(5))))
    return kit.mesh_obj(name, verts, faces, mat)


def terrain(kit, M):
    xs = np.arange(-46.0, 46.01, 1.0)
    ys = np.arange(-100.0, 36.01, 1.0)
    nx, ny = len(xs), len(ys)
    verts = [(float(x), float(y), ground(float(x), float(y))) for y in ys for x in xs]
    faces = [(j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i) for j in range(ny - 1) for i in range(nx - 1)]
    ob = kit.mesh_obj("moor", verts, faces, M["moor"], smooth=True)
    # far ground beyond the grid
    kit.plane("apron", (900, 900), (0, -200, -8.0), M["moor"])
    return ob


def build_land(kit, M, rng):
    terrain(kit, M)
    # bog water
    kit.plane("water", (22, 14), (9.0, 0.3, WATER_Z), M["water"])
    # heather tufts
    pts = []
    tries = 0
    while len(pts) < 1500 and tries < 9000:
        tries += 1
        x, y = rng.uniform(-44, 44), rng.uniform(-92, 34)
        r = math.hypot(x, y)
        if r < 3.0:
            continue
        if abs(x - TENT_X) < 2.0 and abs(y - TENT_Y) < 2.4:
            continue
        gz = ground(x, y)
        if gz < WATER_Z + 0.12:
            continue
        if abs(y - WALL_Y) < 1.0:
            continue
        if y < WALL_Y and abs(x - GATE_X) < 2.2:
            continue
        if y < WALL_Y - 0.5:
            continue            # the field beyond the wall is grass, no heather
        if 0.9 < abs(y) and 3.2 < x < 9.5 and abs(y) < 1.4:
            continue
        # thin out the far ground
        if r > 14 and rng.random() < 0.35:
            continue
        pts.append((x, y, gz - 0.02, rng.uniform(0.18, 0.4), rng.uniform(0.16, 0.34)))
    tuft_mesh(kit, "heather", pts, M["heather"], rng)
    # field beyond the wall
    kit.plane("field", (120, 60), (0, WALL_Y - 31.0, ground(0, WALL_Y - 3) - 0.02), M["field"])
    # the track from the gate
    for k in range(8):
        y0 = WALL_Y - 2 - k * 6
        kit.box(f"track{k}", (2.6, 6.2, 0.05), (GATE_X + 0.2 * math.sin(k), y0, ground(GATE_X, WALL_Y - 3) + 0.0), M["track"])
    # distant hills in the fog
    for k in range(18):
        a = k * math.tau / 18 + 0.15
        d = 190 + 30 * math.sin(k * 2.3)
        h = 28 + 22 * (0.5 + 0.5 * math.sin(k * 1.7 + 1))
        cx, cy = d * math.cos(a), d * math.sin(a) - 30
        verts = [(-70, -40, 0), (70, -40, 0), (70, 40, 0), (-70, 40, 0), (-24, -10, h), (24, -10, h), (24, 10, h), (-24, 10, h)]
        ob = kit.mesh_obj(f"hill{k}", verts, kit.BOX_FACES, M["hill"], loc=(cx, cy, -10), rot=(0, 0, a + 1.57))


def build_ring(kit, M, rng):
    ring = []
    for k in range(10):
        a = k * math.tau / 10 + 0.1
        r = 1.4 + 0.04 * math.sin(k * 3.1)
        x, y = r * math.cos(a), r * math.sin(a)
        sx, sy, sz = 0.5 + 0.1 * math.sin(k * 1.9), 0.38 + 0.06 * math.cos(k * 2.3), 0.28 + 0.05 * math.sin(k * 4.1)
        ob = kit.box(f"ringstone{k}", (sx, sy, sz), (x, y, sz / 2 - 0.02), M["stone"], rot=(0, 0, a + math.pi / 2 + 0.2 * math.sin(k)),
                     bevel=0.07)
    kit.box("hearth", (1.4, 1.05, HEARTH_TOP + 0.05), (-0.05, 0.0, (HEARTH_TOP - 0.05) / 2), M["hearth"], bevel=0.02)
    # three seat stones; the empty one is a taller flat slab on the uphill side
    kit.box("seat_g", (2.1, 0.55, SEAT_TOP + 0.05), (SEAT_G[0], SEAT_G[1], SEAT_TOP / 2 - 0.025), M["seat"], bevel=0.05)
    kit.box("seat_m", (2.1, 0.55, SEAT_TOP + 0.05), (SEAT_M[0], SEAT_M[1], SEAT_TOP / 2 - 0.025), M["seat"], bevel=0.05)
    kit.box("seat_e", (0.55, 1.0, SLAB_TOP + 0.05), (SEAT_E[0], SEAT_E[1], SLAB_TOP / 2 - 0.025), M["slab"], bevel=0.05)
    # the dry patch the shape of someone sitting (shown in the frost only)
    parts = [(SEAT_E[0] - 0.0, SEAT_E[1], SLAB_TOP + 0.004, 0.3, 0.42, 0.012, 0.0),
             (SEAT_E[0] + 0.22, SEAT_E[1] - 0.12, SLAB_TOP + 0.004, 0.2, 0.15, 0.012, 0.0),
             (SEAT_E[0] + 0.22, SEAT_E[1] + 0.12, SLAB_TOP + 0.004, 0.2, 0.15, 0.012, 0.0)]
    dry = blocks_mesh(kit, "dry", parts, M["dry"])
    # the three heather-purple strokes scratched into the hearth stone (the lore plant): upper left of the pot
    st = []
    for k in range(3):
        st.append((-0.62 + k * 0.1, 0.27, HEARTH_TOP + 0.002, 0.045, 0.36, 0.006, 0.0))
    strokes = blocks_mesh(kit, "strokes", st, M["stroke"])
    # logs, flames, embers
    for k, (dx, dy, yaw) in enumerate(((0.3, 0.0, 0.3), (0.3, 0.05, -0.5), (0.34, -0.08, 1.4))):
        kit.cyl(f"firelog{k}", 0.04, 0.5, (dx, dy, HEARTH_TOP + 0.06), M["log"], rot=(0, math.pi / 2, yaw), n=8)
    flames = []
    for k, (dx, dy, h, r) in enumerate(((0.28, 0.0, 0.34, 0.075), (0.38, 0.06, 0.26, 0.06), (0.22, -0.06, 0.22, 0.055), (0.33, -0.05, 0.3, 0.05))):
        f = kit.cyl(f"flame{k}", r, h, (dx, dy, HEARTH_TOP + 0.1 + h / 2), M["flame"], n=6, r2=0.012)
        c = kit.cyl(f"flamecore{k}", r * 0.5, h * 0.6, (dx, dy, HEARTH_TOP + 0.1 + h * 0.3), M["flame2"], n=6, r2=0.01)
        flames += [f, c]
    embers = []
    for k in range(7):
        embers.append(kit.box(f"ember{k}", (0.07, 0.06, 0.03), (0.18 + 0.07 * k % 0.4, -0.12 + 0.045 * k % 0.26, HEARTH_TOP + 0.045), M["ember"], rot=(0, 0, k)))
    # the pot and the stew
    kit.cyl("pot", 0.19, 0.26, (POT[0], POT[1], HEARTH_TOP + 0.13), M["pot"], n=20)
    kit.cyl("potrim", 0.2, 0.025, (POT[0], POT[1], HEARTH_TOP + 0.265), M["pot"], n=20)
    kit.cyl("stewtop", 0.175, 0.01, (POT[0], POT[1], HEARTH_TOP + 0.255), M["stew"], n=20)
    kit.box("potbail", (0.42, 0.015, 0.015), (POT[0], POT[1], HEARTH_TOP + 0.34), M["pot"])
    # steam: soft puffs that rise and fade, moved in animate
    steam = []
    for k in range(7):
        steam.append(kit.sphere(f"steam{k}", 0.03, (POT[0], POT[1], HEARTH_TOP + 0.3), M["steam"], seg=12))
    # the three stepping stones east
    for k, (x, y) in enumerate(STONES):
        kit.box(f"step{k}", (1.1 - 0.08 * k, 0.85, 0.7), (x, y, STONE_TOP - 0.35), M["seat"], rot=(0, 0, 0.25 * (k - 1)), bevel=0.06)
    # a flat turf stack for L21 (hidden until the turves cue)
    turves = []
    for k in range(8):
        a = k * math.tau / 8 + 0.4
        turves.append(kit.box(f"turf{k}", (0.42, 0.3, 0.14), (1.55 * math.cos(a), 1.55 * math.sin(a), 0.07), M["turf"],
                              rot=(0, 0, a + 1.57), bevel=0.04))
    return {"flames": flames, "embers": embers, "steam": steam, "turves": turves, "dry": dry, "strokes": strokes}


def build_tent(kit, M):
    w, l, h = TENT_W / 2, TENT_L / 2, TENT_H
    x0, y0 = TENT_X, TENT_Y
    vs = [(x0 - w, y0 - l, 0), (x0 + w, y0 - l, 0), (x0 + w, y0 + l, 0), (x0 - w, y0 + l, 0), (x0, y0 - l, h), (x0, y0 + l, h)]
    fs = [(0, 3, 5, 4), (1, 4, 5, 2), (0, 4, 1), (3, 2, 5)]
    tent = kit.mesh_obj("tent", vs, fs, M["canvas"])
    # door: a darker flap with a zip line, on the south gable
    kit.box("tentdoor", (0.9, 0.02, 1.0), (x0, y0 - l - 0.012, 0.55), kit.plastic("#43553a", 0.9, "tent door"))
    kit.box("tentzip", (0.02, 0.02, 1.0), (x0, y0 - l - 0.03, 0.55), kit.plastic("#1b1b1e", 0.5, "zip"))
    kit.box("groundsheet", (TENT_W - 0.1, TENT_L - 0.1, 0.04), (x0, y0, 0.0), M["groundsheet"])
    # guy lines' pegs are left out (nothing thin)
    # sleeping bags: Dad under the west wall, me by the ridge
    kit.box("bag_dad", (0.66, 1.3, 0.4), (x0 - 0.7, y0 - 0.1, 0.2), M["bagd"], bevel=0.12)
    kit.box("bag_me", (0.66, 1.3, 0.4), (x0, y0 - 0.1, 0.2), M["bagm"], bevel=0.12)
    # the frost on the inside of the door (L33): a speckled white sheet, hidden until the cue
    fr = kit.plane("doorfrost", (0.95, 1.05), (x0, y0 - l + 0.04, 0.55), M["frost"], rot=(math.pi / 2, 0, 0))
    fr.hide_render = True
    return tent


def hand_shadow_boxes(sx, sy, w, hgt, mirror=1):
    """A spread mitten silhouette as (u, v, du, dv, rot) boxes in panel space: a palm block, four fat fingers fanned
    a little with clear gaps between them, a thumb. Reads as an open hand, not a bar."""
    out = [(0.0, 0.0, w * 0.74, hgt * 0.34, 0.0)]
    for k in range(4):
        a = (-1.5 + k) * 0.11               # a gentle fan
        fl = hgt * (0.46, 0.62, 0.58, 0.42)[k if mirror > 0 else 3 - k]
        fx = (-1.5 + k) * (w * 0.215)
        base_v = hgt * 0.15
        out.append((fx + math.sin(a) * fl * 0.5, base_v + math.cos(a) * fl * 0.5, w * 0.17, fl, -a))
    out.append((mirror * w * 0.5, hgt * 0.04, w * 0.17, hgt * 0.32, mirror * -0.9))
    return out


def build_shadows(kit, M):
    """The hand shadows on the west wall's inside face and the finger on Dad's bag. The wall runs from (x0-w, y)
    at the ground up to the ridge (x0, y) at TENT_H: u along y, v up the slope."""
    w = TENT_W / 2
    sl = math.hypot(w, TENT_H)
    eu = V((0, 1, 0))
    ev = V((w, 0, TENT_H)) / sl
    n_in = V((TENT_H, 0, -w)) / sl     # inward normal of the west panel (points into the tent, down and east)
    origin = V((TENT_X - w, TENT_Y, 0))
    objs = []
    for hi, (uc, vc, mir) in enumerate(((0.25, 0.9, 1), (1.1, 1.0, -1))):
        verts, faces = [], []
        for (bu, bv, du, dv, rot) in hand_shadow_boxes(0, 0, 0.7, 0.85, mir):
            c, s = math.cos(rot), math.sin(rot)
            base = len(verts)
            for (px, py) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                u = uc + bu + (px * du / 2) * c - (py * dv / 2) * s
                v = vc + bv + (px * du / 2) * s + (py * dv / 2) * c
                p = origin + eu * u + ev * v + n_in * 0.012
                verts.append((p.x, p.y, p.z))
            faces.append((base, base + 1, base + 2, base + 3))
        ob = kit.mesh_obj(f"handshadow{hi}", verts, faces, M["shadow"])
        ob.hide_render = True
        objs.append(ob)
    fin = blocks_mesh(kit, "fingershadow", [(TENT_X - 0.65, TENT_Y + 0.4, 0.5, 1.1, 0.14, 0.01, 0.4)], M["shadow"])
    fin.hide_render = True
    return objs, fin


def build_home(kit, M):
    """Grandad's front door: a brick wall, a dark blue door, a step, a window, a pot of plants. At HOME."""
    hx, hy = HOME
    kit.plane("homelawn", (60, 60), (hx, hy - 6, -0.02), M["lawn"])
    kit.box("homewall", (9.0, 0.4, 3.4), (hx, hy + 0.2, 1.7), M["brick"])
    kit.box("doorframe", (1.3, 0.12, 2.4), (hx, hy - 0.02, 1.2), kit.plastic("#e9e3d6", 0.6, "frame"))
    kit.box("homedoor", (1.05, 0.08, 2.25), (hx, hy - 0.1, 1.13), M["door"], bevel=0.015)
    kit.box("doorknob", (0.08, 0.06, 0.08), (hx + 0.38, hy - 0.17, 1.05), kit.metal("#c9a24a", 0.3, "knob"), bevel=0.02)
    kit.box("homestep", (1.8, 0.8, 0.18), (hx, hy - 0.5, 0.09), M["step"], bevel=0.02)
    kit.box("homewindow", (1.3, 0.1, 1.2), (hx - 2.5, hy - 0.02, 1.7), M["glass"])
    kit.box("homecurtain", (1.1, 0.04, 1.0), (hx - 2.5, hy - 0.09, 1.7), M["curtain"])
    kit.box("homesill", (1.5, 0.22, 0.08), (hx - 2.5, hy - 0.1, 1.04), M["step"])
    kit.cyl("homepot", 0.2, 0.34, (hx + 1.6, hy - 0.5, 0.17), M["pottery"], n=12, r2=0.24)
    kit.sphere("homeplant", 0.3, (hx + 1.6, hy - 0.5, 0.52), M["plant"], seg=8)
    kit.box("homepath", (1.4, 8.0, 0.04), (hx, hy - 5.0, 0.0), M["pave"])
    kit.box("homeroof", (9.6, 1.0, 0.3), (hx, hy + 0.1, 3.5), kit.plastic("#3a3a40", 0.7, "roof"))


def build_gate(kit, M):
    gz = ground(GATE_X, WALL_Y)
    # the drystone wall: long cobbled blocks with a rough top
    for (x0, x1) in ((-46.0, GATE_X - 1.25), (GATE_X + 1.25, 46.0)):
        n = max(1, int((x1 - x0) / 9.0))
        step = (x1 - x0) / n
        for k in range(n):
            cx = x0 + step * (k + 0.5)
            cz = ground(cx, WALL_Y)
            kit.box(f"wall{x0:.0f}_{k}", (step + 0.05, 0.55, 1.25), (cx, WALL_Y, cz + 0.6), M["wallstone"], bevel=0.06)
    for k, sx in enumerate((-1, 1)):
        kit.box(f"gatepost{k}", (0.5, 0.5, 1.35), (GATE_X + sx * 0.95, WALL_Y, gz + 0.675), M["gatepost"], bevel=0.05)
    # the leaf hangs from the west post and swings uphill (a "gate" cue)
    hinge = kit.empty("gateleaf", (GATE_X - 0.7, WALL_Y + 0.05, gz))
    for k in range(4):
        kit.box(f"gatebar{k}", (1.4, 0.06, 0.09), (0.7, 0, 0.28 + 0.25 * k), M["wood"], hinge, bevel=0.01)
    for sx in (0.05, 0.7, 1.35):
        kit.box(f"gatestile{sx}", (0.08, 0.06, 0.95), (sx, 0, 0.55), M["wood"], hinge, bevel=0.01)
    return hinge


def build_props(kit, M):
    P = {}
    # the tin mug
    mug = kit.empty("mug")
    kit.cyl("mugbody", 0.055, 0.1, (0, 0, 0.05), M["tin"], mug, n=14)
    kit.cyl("mugstew", 0.05, 0.01, (0, 0, 0.098), M["stew"], mug, n=14)
    kit.box("mughandle", (0.02, 0.05, 0.06), (0.07, 0, 0.055), M["tin"], mug, bevel=0.005)
    P["mug"] = mug
    # the dented green flask: green body, a darker dent on one flank with a bright lip around it
    fl = kit.empty("flask")
    kit.cyl("flaskbody", 0.055, 0.26, (0, 0, 0.13), M["flask"], fl, n=14)
    kit.cyl("flaskcap", 0.05, 0.07, (0, 0, 0.295), M["flaskcap"], fl, n=14)
    kit.box("flaskdent", (0.065, 0.045, 0.1), (0.04, -0.035, 0.12), M["flaskdark"], fl, rot=(0, 0, 0.7), bevel=0.012)
    kit.box("flaskdent2", (0.04, 0.03, 0.06), (0.052, -0.03, 0.16), M["flaskdark"], fl, rot=(0.1, 0.2, 0.8), bevel=0.008)
    # the dent's bright lip catches the light (round 1): a pale crescent over the dark hollow, turned to the camera
    kit.box("flaskdentlip", (0.07, 0.012, 0.11), (0.046, -0.041, 0.125), M["flasklip"], fl, rot=(0, 0, 0.7), bevel=0.004)
    kit.box("flaskdentlip2", (0.04, 0.012, 0.06), (0.057, -0.037, 0.178), M["flasklip"], fl, rot=(0.1, 0.2, 0.8), bevel=0.004)
    kit.box("flaskband", (0.12, 0.12, 0.012), (0, 0, 0.06), M["flaskcap"], fl)
    P["flask"] = fl
    # the pack
    pk = kit.empty("pack")
    kit.box("packbody", (0.5, 0.3, 0.62), (0, 0, 0.31), M["packm"], pk, bevel=0.06)
    kit.box("packmouth", (0.4, 0.22, 0.02), (0, 0, 0.625), M["packin"], pk)
    kit.box("packflap", (0.5, 0.26, 0.05), (0, 0.17, 0.62), M["packm"], pk, rot=(0.7, 0, 0), bevel=0.01)
    P["pack"] = pk
    # the walking stick
    st = kit.empty("stick")
    kit.cyl("stickbody", 0.02, 1.0, (0, 0, 0.5), kit.plastic("#5a3f24", 0.7, "stick"), st, n=8)
    kit.box("stickhandle", (0.12, 0.04, 0.04), (0, 0, 1.0), kit.plastic("#5a3f24", 0.7, "stick"), st, bevel=0.01)
    P["stick"] = st
    # the phone: a slab with a lit screen, leaning back on whatever it rests against
    ph = kit.empty("phone")
    kit.box("phonebody", (0.075, 0.012, 0.15), (0, 0, 0.075), M["phonebody"], ph, bevel=0.006)
    sc = kit.plane("phonescreen", (0.064, 0.138), (0, -0.0075, 0.075), M["screen"], ph, rot=(math.pi / 2, 0, 0))
    P["phone"] = ph
    return P


# ------------------------------------------------------------------------------------------------ the creature
def mitten(kit, name, parent, M, side):
    """One block mitten, hanging from the sleeve's end (rig units: 0.34 m each): palm 1.76 wide, four finger blocks and
    a thumb block, about 0.9 m tall and 0.6 m wide in all. Its palm faces +y (the back of the arm)."""
    g = kit.empty(f"{name}.hand", (0, 0, -1.75), parent)
    mat = M["bighand"]
    kit.box(f"{name}.cuff", (1.02, 1.04, 0.3), (0, 0, -0.08), M["bighand"], g, bevel=0.06)
    kit.box(f"{name}.palm", (1.72, 0.56, 1.35), (0, 0, -0.9), mat, g, bevel=0.07)
    fw = 0.40
    for k in range(4):
        fx = (-1.5 + k) * 0.43
        fh = (1.2, 1.35, 1.25, 0.98)[k if side > 0 else 3 - k]
        kit.box(f"{name}.fing{k}", (fw, 0.5, fh), (fx, 0.0, -1.55 - fh / 2), mat, g, bevel=0.07)
    kit.box(f"{name}.thumb", (0.5, 0.5, 1.15), (side * 1.08, -0.05, -1.25), mat, g, rot=(0, side * 0.6, 0), bevel=0.07)
    return g


def dress_creature(kit, M, ctx):
    """Run once the cast exists: mittens on Big Hands' arms, the tall head, the catch points."""
    arms = {s: bpy.data.objects.get(f"bighands.arm{s}") for s in (-1, 1)}
    hg = bpy.data.objects.get("bighands.headg")
    if arms[-1] is None or hg is None:
        return False
    ctx["hands"] = {}
    for s in (-1, 1):
        ctx["hands"][s] = mitten(kit, f"bighands.m{s}", arms[s], M, s)
    top = 0.6
    kit.cyl("bighands.headtop", 0.615, 0.62, (0, 0, top + 0.16), M["bigtop"], hg, n=32, r2=0.58)
    for sx in (-1, 1):
        # the catch points sit in the eyes: 22 degrees round the head from the middle, a little above its centre
        a = math.radians(21.5)
        kit.sphere(f"bighands.catch{sx}", 0.06, (sx * 0.62 * math.sin(a), -0.62 * math.cos(a) - 0.003, 0.085), M["catch"], hg, seg=8)
    return True


# ------------------------------------------------------------------------------------------------ looks
LOOKS = {
    # warm golden dusk on the way up (the memory, L03 to L06)
    "memory": {"fog": "#d9a46a", "density": 0.012, "start": 8.0, "hor": "#e6a45e", "zen": "#6f78a8", "sky_s": 1.1, "exposure": 0.35,
               "sun": (3.6, "#ffb468", (14.0, 20.0)), "moon": (0.0, "#9db4d8", (50.0, 200.0)), "fire": 0.5, "rim": 0.0, "frost": 0.0},
    # Grandad's front door, a bright afternoon
    "home": {"fog": "#b9c6d6", "density": 0.004, "start": 20.0, "hor": "#b9c6d6", "zen": "#7fa6d6", "sky_s": 1.3, "exposure": 0.25,
             "sun": (4.0, "#fff1d6", (55.0, 150.0)), "moon": (0.0, "#9db4d8", (50.0, 200.0)), "fire": 0.0, "rim": 0.0, "frost": 0.0},
    # night one at dusk: blue, the fire the warm key
    "dusk": {"fog": "#2a3550", "density": 0.02, "start": 6.0, "hor": "#3f4f76", "zen": "#101830", "sky_s": 1.2, "exposure": 0.55,
             "sun": (0.0, "#ffd0a0", (60.0, 100.0)), "moon": (1.6, "#9db4e4", (45.0, 250.0)), "fire": 1.0, "rim": 1.0, "frost": 0.0, "fill": 0.45},
    # night two, later dusk
    "dusk2": {"fog": "#222c46", "density": 0.022, "start": 6.0, "hor": "#33426a", "zen": "#0c1228", "sky_s": 1.15, "exposure": 0.55,
              "sun": (0.0, "#ffd0a0", (60.0, 100.0)), "moon": (1.7, "#9db4e4", (45.0, 250.0)), "fire": 1.0, "rim": 1.0, "frost": 0.0, "fill": 0.45},
    # night three: a hard frost starting
    "frostdusk": {"fog": "#2b3a58", "density": 0.02, "start": 6.0, "hor": "#44587e", "zen": "#101a34", "sky_s": 1.25, "exposure": 0.55,
                  "sun": (0.0, "#ffd0a0", (60.0, 100.0)), "moon": (1.9, "#a8c0f0", (45.0, 250.0)), "fire": 1.0, "rim": 1.0, "frost": 0.6, "fill": 0.55},
    # the embers (L34) and the tent night
    "night": {"fog": "#1e2842", "density": 0.022, "start": 5.0, "hor": "#2a3858", "zen": "#0a1024", "sky_s": 1.0, "exposure": 0.6,
              "sun": (0.0, "#ffd0a0", (60.0, 100.0)), "moon": (1.4, "#a0b8ec", (45.0, 250.0)), "fire": 0.0, "rim": 1.0, "frost": 0.8, "fill": 0.6},
    # cold bright dawn, frost white on everything
    "dawn": {"fog": "#c3d0e0", "density": 0.012, "start": 8.0, "hor": "#d8e0ea", "zen": "#8fb0d8", "sky_s": 1.1, "exposure": -0.15,
             "sun": (2.0, "#fff0d8", (14.0, 100.0)), "moon": (0.0, "#9db4d8", (50.0, 200.0)), "fire": 0.0, "rim": 0.0, "frost": 1.0},
    # bright overcast morning at the gate
    "morning": {"fog": "#b8c0c4", "density": 0.008, "start": 12.0, "hor": "#c4cacc", "zen": "#9aa4aa", "sky_s": 1.5, "exposure": 0.5,
                "sun": (0.8, "#fff4e0", (50.0, 100.0)), "moon": (0.0, "#9db4d8", (50.0, 200.0)), "fire": 0.0, "rim": 0.0, "frost": 0.0},
    # sunset: low gold from the west, the fire bright
    "sunset": {"fog": "#d89a5c", "density": 0.012, "start": 8.0, "hor": "#f0a860", "zen": "#6a7ab0", "sky_s": 1.4, "exposure": 0.7,
               "sun": (6.0, "#ffb060", (9.0, 0.0)), "moon": (0.0, "#9db4d8", (50.0, 200.0)), "fire": 1.4, "rim": 0.0, "frost": 0.0},
}
# sun direction: (elevation degrees above the horizon, bearing the light travels toward, degrees from +x ccw): the
# light comes from the west at sunset, so it travels east (+x); bearing 90 here means "toward +x".


def _sun_rot(elev, bear):
    # a SUN lamp shines down its -Z; tilt it by (90 - elev) about x, then spin it round z so the light travels toward `bear`
    return (math.radians(90.0 - elev), 0.0, math.radians(bear - 90.0))


def kit_fog_nodes():
    out = []
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        for cam in [n for n in m.node_tree.nodes if n.type == "CAMERA"]:
            try:
                sub = cam.outputs["View Distance"].links[0].to_node
                mx = sub.outputs[0].links[0].to_node
                mul = mx.outputs[0].links[0].to_node
                ex = mul.outputs[0].links[0].to_node
                inv = ex.outputs[0].links[0].to_node
                mix = inv.outputs[0].links[0].to_node
                em = mix.inputs[2].links[0].from_node if mix.inputs[2].links else None
                out.append((sub, mul, em))
            except (IndexError, KeyError, AttributeError):
                continue
    return out


def build_world(kit, ctx):
    """A gradient sky: horizon colour up to a zenith, both set by the look."""
    w = bpy.data.worlds.new("sky")
    bpy.context.scene.world = w
    w.use_nodes = True
    N, L = w.node_tree.nodes, w.node_tree.links
    bg = N["Background"]
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Generated"], sep.inputs[0])
    mr = N.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -0.05
    mr.inputs["From Max"].default_value = 0.7
    L.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = N.new("ShaderNodeValToRGB")
    L.new(mr.outputs["Result"], ramp.inputs["Fac"])
    L.new(ramp.outputs["Color"], bg.inputs["Color"])
    ctx["sky_ramp"] = ramp
    ctx["sky_bg"] = bg


def apply_look(kit, ctx, name):
    if ctx.get("look") == name:
        return
    lk = LOOKS[name]
    c = kit.col(lk["fog"])
    for sub, mul, em in ctx.setdefault("fog_nodes", kit_fog_nodes()):
        sub.inputs[1].default_value = lk["start"]
        mul.inputs[1].default_value = -lk["density"]
        if em is not None:
            em.inputs["Color"].default_value = c
    r = ctx["sky_ramp"].color_ramp
    r.elements[0].color = kit.col(lk["hor"])
    r.elements[1].color = kit.col(lk["zen"])
    ctx["sky_bg"].inputs["Strength"].default_value = lk["sky_s"]
    bpy.context.scene.view_settings.exposure = lk["exposure"]
    e, col_, (el, br) = lk["sun"]
    kit.LIGHTS["sun"]["base"] = e
    kit.LIGHTS["sun"]["light"].color = kit.col(col_)[:3]
    kit.LIGHTS["sun"]["obj"].rotation_euler = _sun_rot(el, br)
    e, col_, (el, br) = lk["moon"]
    kit.LIGHTS["moon"]["base"] = e
    kit.LIGHTS["moon"]["light"].color = kit.col(col_)[:3]
    kit.LIGHTS["moon"]["obj"].rotation_euler = _sun_rot(el, br)
    kit.LIGHTS["fill"]["base"] = lk.get("fill", 0.0)
    kit.LIGHTS["fill"]["obj"].rotation_euler = _sun_rot(40.0, 80.0)
    for v in FROST_NODES:
        v.outputs[0].default_value = lk["frost"]
    ctx["look"] = name
    ctx["look_exp"] = lk["exposure"]
    ctx["look_fire"] = lk["fire"]
    ctx["look_rim"] = lk["rim"]


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    import numpy.random as npr

    ctx = {"story": story}
    rng = npr.default_rng(35)
    bpy.context.scene.cycles.transparent_max_bounces = 8
    M = materials(kit)
    ctx["M"] = M
    build_world(kit, ctx)
    build_land(kit, M, rng)
    ctx.update(build_ring(kit, M, rng))
    ctx["tent"] = build_tent(kit, M)
    ctx["hand_shadows"], ctx["finger"] = build_shadows(kit, M)
    ctx['gate'] = build_gate(kit, M)
    build_home(kit, M)
    ctx["props"] = build_props(kit, M)
    # lights
    kit.light("fire", "POINT", (FIRE[0], FIRE[1], 0.3), 110.0, "#ff8a3d", size=0.16,
              flicker={"rate": 2.2, "depth": 0.16, "seed": 4})
    kit.light("firefill", "POINT", (FIRE[0], FIRE[1], 0.9), 18.0, "#ffa860", size=0.4, shadow=False,
              flicker={"rate": 2.0, "depth": 0.12, "seed": 9})
    sun = kit.light("sun", "SUN", (0, 0, 60), 0.0, "#ffd0a0")
    sun.data.angle = math.radians(4)
    moon = kit.light("moon", "SUN", (0, 0, 60), 0.0, "#9db4e4")
    moon.data.angle = math.radians(6)
    fill = kit.light("fill", "SUN", (0, 0, 60), 0.0, "#8aa0d0")
    fill.data.angle = math.radians(20)
    kit.light("rim", "SPOT", (12, 3, 3), 900.0, "#a8c0f0", size=0.4, spot=22, blend=0.4)
    kit.light("hkey", "SPOT", (6, 0, 0.5), 110.0, "#ffa868", size=0.3, spot=30, blend=0.5, shadow=False)
    kit.light("tentglow", "POINT", (TENT_X - 0.3, TENT_Y - 1.0, 1.0), 40.0, "#ff8a3d", size=0.25)
    kit.light("tentfill", "POINT", (TENT_X + 0.3, TENT_Y - 0.3, 1.1), 45.0, "#9db4e4", size=0.3, shadow=False)
    kit.light("phoneglow", "POINT", (0, 0, 0), 10.0, "#a8d4ff", size=0.05, shadow=False)
    kit.light("doorlit", "POINT", (-3.2, -4.0, 1.4), 90.0, "#ffb878", size=0.5, shadow=False)
    kit.light("flare", "POINT", (-0.4, 0.0, 1.0), 60.0, "#ff8a3d", size=0.3, shadow=False)
    apply_look(kit, ctx, "dusk")
    return ctx


# ------------------------------------------------------------------------------------------------ animate


def place_prop(ob, c, home=None):
    """A prop at a cue: pos/yaw/tilt, or carried at an arm's end."""
    if c is None or c.get("hidden"):
        ob.hide_render = True
        for ch in ob.children_recursive:
            ch.hide_render = True
        return
    ob.hide_render = False
    for ch in ob.children_recursive:
        ch.hide_render = False
    hand = c.get("hand")
    if hand:
        arm = bpy.data.objects.get(hand)
        if arm is not None:
            end = arm.matrix_world @ V((0.0, 0.0, -1.75))
            off = c.get("offset", [0, 0, 0])
            ob.location = (end.x + off[0], end.y + off[1], end.z + off[2])
            rot = arm.matrix_world.to_euler()
            ob.rotation_euler = (math.radians(c.get("tilt", 0.0)), 0, rot.z + math.radians(c.get("yaw", 0.0)))
        return
    p = c.get("pos", [0, 0, 0])
    ob.location = (p[0], p[1], p[2])
    ob.rotation_euler = (math.radians(c.get("tilt", 0.0)), 0, math.radians(c.get("yaw", 0.0)))


def animate(kit, story, tl, t, ctx):
    from blocky import acting as ac

    over = {}
    if not ctx.get("dressed"):
        ctx["dressed"] = dress_creature(kit, ctx["M"], ctx)
    apply_look(kit, ctx, _switch(_cues(tl, "look"), "id", t, "dusk"))
    lk = LOOKS[ctx["look"]]
    # fire: flames and the light follow the level (a slow wobble in the flames, under 1 Hz)
    lvl = _ease_to(_cues(tl, "fire"), t, "level", 1.0) * 1.0
    fire_gain = lk["fire"] * (1.0 if lvl > 0.05 else 0.0)
    flame_on = lvl >= 0.5
    for k, f in enumerate(ctx["flames"]):
        f.hide_render = not flame_on
        sc = 1.0 + 0.08 * kit.noise1(t, 3.0 + k, 2.6)
        f.scale = (1.0, 1.0, sc)
    for e in ctx["embers"]:
        e.hide_render = lvl <= 0.0
    if lvl > 0.05:
        over["fire"] = lk["fire"] * min(1.0, lvl)
        over["firefill"] = lk["fire"] * min(1.0, lvl)
    else:
        over["fire"] = 0.07 if lvl > 0.0 else 0.0
        over["firefill"] = 0.0
    if 0.0 < lvl < 0.5:   # embers only: a dull red light
        over["fire"] = 0.05
        kit.LIGHTS["fire"]["light"].color = kit.col("#ff5a1a")[:3]
    else:
        kit.LIGHTS["fire"]["light"].color = kit.col("#ff8a3d")[:3]
    over["rim"] = lk["rim"]
    over["hkey"] = lk["rim"] * _ease_to(_cues(tl, "hkey"), t, "v", 1.0)
    over["sun"] = 1.0
    over["moon"] = 1.0
    # steam from the pot: puffs rising, widening and fading, slowly
    for k, s in enumerate(ctx["steam"]):
        ph = ((t * 0.28) + k / len(ctx["steam"])) % 1.0
        s.location = (POT[0] + 0.05 * math.sin(ph * 6 + k), POT[1] + 0.04 * math.cos(ph * 5 + k * 2), HEARTH_TOP + 0.3 + ph * 0.7)
        sc = 0.8 + ph * 1.0
        s.scale = (sc, sc, sc * 1.3)
        s.hide_render = False
    on = _switch(_cues(tl, "turves"), "on", t, False)
    for o in ctx["turves"]:
        o.hide_render = not on
    ctx["dry"].hide_render = not _switch(_cues(tl, "dry"), "on", t, False)
    ctx["strokes"].hide_render = False
    df = bpy.data.objects.get("doorfrost")
    if df is not None:
        df.hide_render = not _switch(_cues(tl, "doorfrost"), "on", t, False)
    # the tent canvas glow
    gv = _ease_to(_cues(tl, "glow"), t, "v", 0.0)
    gm = _ease_to(_cues(tl, "glow"), t, "mix", 0.0)
    br = 1.0 + 0.07 * math.sin(t * 2.2) if gv > 0.01 else 1.0
    em = GLOW["em"]
    c0, c1 = kit.col("#ff8a3d"), kit.col("#6f8fd8")
    em.inputs["Color"].default_value = tuple(c0[i] + (c1[i] - c0[i]) * gm for i in range(3)) + (1.0,)
    em.inputs["Strength"].default_value = gv * br
    over["tentglow"] = _ease_to(_cues(tl, "tentlight"), t, "v", 0.0) * (1 - gm) * br
    over["tentfill"] = _ease_to(_cues(tl, "tentlight"), t, "fill", 0.0)
    mode = _switch(_cues(tl, "shadow"), "mode", t, "none")
    for o in ctx["hand_shadows"]:
        o.hide_render = mode != "hands"
    ctx["finger"].hide_render = mode != "finger"
    # props
    P = ctx["props"]
    place_prop(P["mug"], _last(_cues(tl, "mug"), t))
    place_prop(P["flask"], _last(_cues(tl, "flask"), t))
    place_prop(P["stick"], _last(_cues(tl, "stick"), t))
    pc = _last(_cues(tl, "pack"), t)
    if pc is not None and pc.get("worn"):
        torso = bpy.data.objects.get("dad.torso")
        P["pack"].hide_render = False
        for ch in P["pack"].children_recursive:
            ch.hide_render = False
        if torso is not None:
            bpy.context.view_layer.update()
            w = torso.matrix_world @ V((0.0, 1.0, 1.0))
            P["pack"].location = (w.x, w.y, w.z - 0.2)
            P["pack"].rotation_euler = (0, 0, torso.matrix_world.to_euler().z)
    else:
        place_prop(P["pack"], pc)
    pcue = _last(_cues(tl, "phone"), t)
    place_prop(P["phone"], pcue)
    vis = pcue is not None and not pcue.get("hidden")
    ph = P["phone"].location
    over["phoneglow"] = (float(pcue.get("glow", 1.0)) if vis else 0.0)
    kit.LIGHTS["phoneglow"]["obj"].location = (ph.x, ph.y - 0.1, ph.z + 0.12) if vis else (0, 0, -50)
    # Big Hands: palms tipped, the rim light behind it, the whole thing posed by acting
    deg = _ease_to(_cues(tl, "handtilt"), t, "deg", -75.0)
    if ctx.get("hands"):
        for s, g in ctx["hands"].items():
            g.rotation_euler = (math.radians(deg), 0, 0)
    bh = ac.state(tl, "bighands", t)
    if not bh["hidden"]:
        hx, hy = bh["x"], bh["y"]
        kit.LIGHTS["rim"]["obj"].location = (hx + 3.0, hy + 1.6, 2.4)
        # aim at its head
        d = V((hx, hy, 1.5)) - kit.LIGHTS["rim"]["obj"].location
        kit.LIGHTS["rim"]["obj"].rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        # a warm low key from the fire's side, on the creature only (the firelight would never reach 8 m)
        ho = kit.LIGHTS["hkey"]["obj"]
        away = V((-hx, -hy, 0.0))
        away = away.normalized() if away.length > 0.1 else V((1, 0, 0))
        ho.location = (hx + away.x * 2.3, hy + away.y * 2.3, 0.45)
        ho.rotation_euler = (V((hx, hy, 1.15)) - ho.location).to_track_quat("-Z", "Y").to_euler()
    else:
        over["rim"] = 0.0
        over["hkey"] = 0.0
    fl = _ease_to(_cues(tl, "flare"), t, "v", 0.0)
    over["flare"] = fl
    # an optional exposure nudge on top of the look (cue "exposure", v in stops; default 0 changes nothing)
    bpy.context.scene.view_settings.exposure = ctx.get("look_exp", bpy.context.scene.view_settings.exposure) + _ease_to(_cues(tl, "exposure"), t, "v", 0.0)
    over["doorlit"] = _ease_to(_cues(tl, "doorlit"), t, "v", 0.0)
    fp = _last(_cues(tl, "flare"), t)
    if fp is not None and fp.get("pos"):
        kit.LIGHTS["flare"]["obj"].location = tuple(fp["pos"])
    else:
        kit.LIGHTS["flare"]["obj"].location = (-0.4, 0.0, 1.0)
    ctx["gate"].rotation_euler = (0, 0, math.radians(_ease_to(_cues(tl, "gate"), t, "deg", 0.0)))
    # sitting: both legs forward (an acting key "sit": true)
    for who in story.get("cast", {}):
        sit = _switch(tl["acting"].get(who, []), "sit", t, False)
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg is not None and sit:
                leg.rotation_euler = (-math.pi / 2, 0, 0)
    bpy.context.view_layer.update()
    return over
