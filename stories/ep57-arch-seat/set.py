"""Arch Seat (ep57): a small hill town's square, the clock arch with its stone seat, and the Span. Built from kit.py's
parts; nothing here is shared with another story's set.

Coordinates (metres): x east, y north, z up. The square runs x -11 .. 11, y -5 .. 14. The clock arch is on its north
side: a deep stone archway, front face at y = ARCH_Y0, a closed back wall at y = ARCH_Y1. The arch seat is a stone
bench against the back wall (x -1.3 .. 1.3, top at 0.45 m) facing south into the square. A character faces -y at
yaw 0, +x at yaw 90.

THE SPAN: one cast member, "span". An ordinary R6 body in a faded rose knit jumper, whose torso is rebuilt 1.6 m wide
(its legs at the far ends, its arms hanging from the far shoulders), with one ordinary head in the middle. Only the
width is wrong. Its face is our own (eyes "pin": two round black eyes, one pin highlight each, a short flat mouth, no
brows). It is never seen moving, only nearer.

Acting keys read here (acting.py ignores them):
  place [x, y, z]  added to the character's pos (so a cut can move it with no walk and no footsteps)
  sit true         both legs forward 90 degrees
  bend deg         the torso forward at the hips
  ghost true       drawn for shadows only (the Span's shadow cast by nothing)
  cap false        the character's cap is off (and the stack sits lower)
Cues read here:
  env {state: day|dusk|rain|lowsun, dur}      the light grade, a ramp of dur seconds (never under 0.3)
  stack {who, n, mode: land|drop|set|arcin}   the number of gold blocks on a head from this time
  arc {from, to, dur}                         one block flying from one stack to another
  door {open: 0..1}                           the bakery door
  doors {open: 0..1}                          the doors of the painted houses, staggered
  shadow {kind: floor|wall|none}              the Span's shadow laid down (a flat dark shape)
  prop {name: ..., on: bool}                  small props (cap, bag, phone, loaf)
"""

from __future__ import annotations

import math

import bpy
from mathutils import Vector as V

from blocky import acting as ac
from blocky import kit, rig

S = rig.S

ARCH_Y0, ARCH_Y1 = 14.0, 17.2
OPEN_W, OPEN_H = 3.0, 4.6
SEAT_X, SEAT_Y0, SEAT_H = 1.3, 15.6, 0.45
SPAN_K = 3.15                      # torso half width in rig units: 2.1 m across, arms out to the arch walls
GOLD = "#e9b23a"
BLOCK_M = 0.13

# the light grades: (sun energy, sun colour, direction toward the sun, world colour, world strength, arch lamp gain)
ENV = {
    "day": (4.6, "#fff0d8", (-0.30, -0.70, 0.80), "#9fcaf0", 1.15, 0.45),
    "dusk": (2.6, "#ffb070", (0.62, -0.50, 0.28), "#e8a888", 0.55, 0.6),
    "rain": (1.1, "#c0ccdc", (-0.20, -0.50, 0.70), "#8c97a4", 1.7, 0.5),
    "raindim": (0.35, "#aab8c8", (-0.20, -0.50, 0.70), "#7d8590", 0.9, 0.12),
    "cold": (1.6, "#c4d0ff", (0.62, -0.50, 0.28), "#8393ad", 0.95, 0.4),
    "lowsun": (3.6, "#ffc890", (0.50, -0.62, 0.34), "#b4c4d8", 1.3, 0.55),
}


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _lin(c):
    return tuple(kit.srgb(v) for v in c)


def cues(tl, name):
    return sorted((c for c in tl["cues"] if c["name"] == name), key=lambda c: c["t"])


def bx(name, size, loc, mat, parent=None, rot=(0, 0, 0), bevel=0.02):
    return kit.box(name, size, loc, mat, parent, rot, bevel)


# ------------------------------------------------------------------------------------------------ materials


def mats():
    M = {}
    M["cob"] = kit.cobbles("#a98353", "#d9b57d", "#6a5238", 2.2, 0.0, "cob dry")
    M["cobw"] = kit.cobbles("#6f6b66", "#8d8984", "#3a3835", 2.2, 0.55, "cob wet")
    M["stone"] = kit.concrete("#a89880", 2.0, 0.28, "arch stone")
    M["stone2"] = kit.concrete("#b4a58d", 3.0, 0.2, "stone2")
    M["stonedark"] = kit.concrete("#8e8068", 2.0, 0.3, "stonedark")
    M["slab"] = kit.concrete("#9c917f", 1.6, 0.25, "slab")
    M["hollow"] = kit.plastic("#8a7c66", 0.9, "hollow")
    M["rose"] = kit.plastic("#c98d8f", 0.9, "rosestroke")
    M["roof"] = kit.plastic("#8b5a45", 0.8, "roof")
    M["dark"] = kit.plastic("#2a2824", 0.9, "dark")
    M["win"] = kit.plastic("#3b4a58", 0.25, "win")
    for key, hx, nm in (("cream", "#f3ead6", "cream"), ("mint", "#9fd8c0", "mint"), ("green", "#3f7a4a", "greenaw"),
                        ("terra", "#c96f4a", "terra")):
        m = kit.plastic(hx, 0.8, nm)
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Emission Color"].default_value = kit.col(hx)
        b.inputs["Emission Strength"].default_value = 0.22
        M[key] = m
    M["wood"] = kit.plastic("#7a5030", 0.75, "wood")
    M["wood2"] = kit.plastic("#5d3d24", 0.75, "wood2")
    M["metal"] = kit.metal("#8a8d90", 0.4, "metal1")
    M["tyre"] = kit.plastic("#1d1d1f", 0.9, "tyre")
    M["water"] = kit.plastic("#6fa8c0", 0.15, "water")
    M["puddle"] = kit.plastic("#424a56", 0.04, "puddle", spec=0.9)
    M["gold"] = kit.plastic("#f4a91c", 0.30, "gold", spec=0.6)
    M["gold2"] = kit.plastic("#c99a2e", 0.45, "gold2")
    M["clockface"] = kit.plastic("#efe6cf", 0.7, "clockface")
    M["clockbar"] = kit.plastic("#2b2824", 0.6, "clockbar")
    for i, h in enumerate(("#e8c9a0", "#c8d6a8", "#e6b9a8", "#a9c4d8", "#f0dfa0", "#d3b8d8", "#c9a38a", "#b8d4c4")):
        M[f"paint{i}"] = kit.plastic(h, 0.85, f"paint{i}")
    for i, h in enumerate(("#6b3f2a", "#2f4f6b", "#8a2f2f", "#3d5a3a")):
        M[f"door{i}"] = kit.plastic(h, 0.7, f"door{i}")
    M["shadow"] = shadow_mat()
    return M


def shadow_mat():
    m = kit._new("spanshadow")
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = nt.nodes["Material Output"]
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    bl = nt.nodes.new("ShaderNodeBsdfDiffuse")
    bl.inputs["Color"].default_value = (0.01, 0.008, 0.01, 1)
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.8
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(bl.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


# ------------------------------------------------------------------------------------------------ the set


def striped_awning(name, x0, x1, y_from, y_to, z_from, z_to, M, ca="mint", cb="cream", n=10, axis="x", parent=None):
    """An awning: n stripes across, sloping from the wall (z_from at y_from) out to the edge (z_to at y_to)."""
    L = (x1 - x0) / n
    ang = math.atan2(z_from - z_to, abs(y_to - y_from))
    depth = math.hypot(y_to - y_from, z_to - z_from)
    for i in range(n):
        xc = x0 + L * (i + 0.5)
        bx(f"{name}.s{i}", (L, depth, 0.05), (xc, (y_from + y_to) / 2, (z_from + z_to) / 2), M[ca if i % 2 == 0 else cb],
           parent, rot=(ang if y_to < y_from else -ang, 0, 0), bevel=0.01)
    # a scalloped valance
    for i in range(n):
        xc = x0 + L * (i + 0.5)
        bx(f"{name}.v{i}", (L, 0.04, 0.2), (xc, y_to, z_to - 0.1), M[ca if i % 2 == 0 else cb], parent, bevel=0.01)


def facade(name, cx, cy, face, w, h, d, M, paint, door_i=0, windows=2, door=True, roof=True, door_x=None):
    """A painted house front. Built facing -y at the origin, then the parent empty is turned to face `face` degrees
    (0: faces -y, 90: faces +x, 180: faces +y, -90: faces -x). Returns the empty and the door pivot."""
    e = kit.empty(name, (cx, cy, 0), rot=(0, 0, math.radians(face)))
    bx(f"{name}.body", (w, d, h), (0, d / 2, h / 2), M[paint], e, bevel=0.03)
    if roof:
        bx(f"{name}.roof", (w + 0.5, d + 0.4, 0.3), (0, d / 2, h + 0.15), M["roof"], e, bevel=0.05)
        bx(f"{name}.rid", (w + 0.3, 0.5, 0.35), (0, d / 2, h + 0.4), M["roof"], e, bevel=0.05)
    bx(f"{name}.plinth", (w + 0.06, 0.1, 0.4), (0, -0.04, 0.2), M["stonedark"], e, bevel=0.02)
    dp = None
    dx = door_x if door_x is not None else 0.0
    if door:
        bx(f"{name}.dframe", (1.2, 0.1, 2.3), (dx, -0.04, 1.15), M["cream"], e, bevel=0.02)
        dp = kit.empty(f"{name}.doorpivot", (dx - 0.5, -0.1, 0), e)
        bx(f"{name}.door", (1.0, 0.08, 2.2), (0.5, 0, 1.1), M[f"door{door_i % 4}"], dp, bevel=0.02)
        bx(f"{name}.knob", (0.08, 0.1, 0.08), (0.86, -0.06, 1.05), M["gold2"], dp)
        bx(f"{name}.dark", (0.9, 0.04, 2.1), (dx, -0.0, 1.1), M["dark"], e)
    nx = windows
    for k in range(nx):
        wx = (-w / 2 + w * (k + 0.5) / nx) if door_x is None else (-w / 2 + w * (k + 0.5) / nx)
        if door and abs(wx - dx) < 1.1:
            continue
        for zz in (1.6, 3.7) if h > 5 else (1.7,):
            bx(f"{name}.win{k}_{zz}", (0.95, 0.08, 1.2), (wx, -0.03, zz), M["win"], e, bevel=0.02)
            bx(f"{name}.wf{k}_{zz}", (1.1, 0.06, 1.35), (wx, -0.01, zz), M["cream"], e, bevel=0.02)
            bx(f"{name}.sill{k}_{zz}", (1.2, 0.2, 0.08), (wx, -0.1, zz - 0.7), M["stone2"], e)
    return e, dp


def build(kit_, story, tl):
    ctx = {"M": mats(), "doorpivots": [], "props": {}, "shadows": {}}
    M = ctx["M"]
    bpy.context.scene.world  # created by bl_story
    # ---- ground
    g = kit.plane("ground", (90, 90), (0, 6, 0), M["cob"])
    gw = kit.plane("groundwet", (90, 90), (0, 6, 0.0), M["cobw"])
    ctx["ground"], ctx["groundwet"] = g, gw
    ps = []
    for i, (px, py, sx, sy) in enumerate(((-1.0, 3.2, 2.2, 1.4), (3.4, 6.0, 1.8, 1.1), (-4.5, 10.0, 2.6, 1.2),
                                          (0.4, 11.4, 2.4, 1.0), (1.4, 12.6, 1.8, 0.7), (-0.3, 8.7, 1.9, 1.0),
                                          (5.5, 2.0, 2.0, 1.2), (-1.2, 9.5, 1.4, 0.8))):
        p = kit.plane(f"puddle{i}", (sx, sy), (px, py, 0.012), M["puddle"])
        ps.append(p)
    ctx["puddles"] = ps
    # ---- the arch
    ARCH_W = 4.4
    for sx in (-1, 1):
        x0 = sx * (OPEN_W / 2 + ARCH_W / 2)
        bx(f"arch.pier{sx}", (ARCH_W, ARCH_Y1 - ARCH_Y0 + 0.3, 5.8), (x0, (ARCH_Y0 + ARCH_Y1 + 0.3) / 2, 2.9), M["stone"], bevel=0.04)
        bx(f"arch.quoin{sx}", (0.5, 0.5, 5.8), (sx * (OPEN_W / 2 + 0.25), ARCH_Y0 - 0.05, 2.9), M["stone2"], bevel=0.04)
        # a stepped corbel at the head of the opening
        bx(f"arch.corbel{sx}", (0.5, ARCH_Y1 - ARCH_Y0, 0.4), (sx * (OPEN_W / 2 - 0.25), (ARCH_Y0 + ARCH_Y1) / 2, OPEN_H - 0.2), M["stone2"], bevel=0.04)
    bx("arch.lintel", (OPEN_W + 0.1, ARCH_Y1 - ARCH_Y0 + 0.3, 1.1), (0, (ARCH_Y0 + ARCH_Y1 + 0.3) / 2, OPEN_H + 0.55), M["stone"], bevel=0.04)
    bx("arch.back", (OPEN_W + 0.2, 0.4, OPEN_H + 1.1), (0, ARCH_Y1 + 0.2, (OPEN_H + 1.1) / 2), M["stone2"], bevel=0.03)
    bx("arch.floor", (OPEN_W, ARCH_Y1 - ARCH_Y0, 0.03), (0, (ARCH_Y0 + ARCH_Y1) / 2, 0.015), M["slab"], bevel=0.0)
    bx("arch.cornice", (OPEN_W + ARCH_W * 2 + 0.3, ARCH_Y1 - ARCH_Y0 + 0.6, 0.3), (0, (ARCH_Y0 + ARCH_Y1) / 2, 5.95), M["stone2"], bevel=0.05)
    # the clock tower
    bx("tower.body", (3.6, 3.4, 3.4), (0, 15.7, 7.85), M["stone"], bevel=0.05)
    bx("tower.cap", (4.0, 3.8, 0.3), (0, 15.7, 9.7), M["stone2"], bevel=0.05)
    roof = kit.cyl("tower.roof", 2.9, 1.7, (0, 15.7, 10.7), M["roof"], n=4, r2=0.12)
    roof.rotation_euler = (0, 0, math.pi / 4)
    ctx["clock"] = kit.empty("clock", (0, ARCH_Y0 - 0.08, 7.9))
    face = kit.cyl("clock.face", 1.15, 0.12, (0, 0.0, 0), M["clockface"], ctx["clock"], rot=(math.pi / 2, 0, 0), n=40)
    for k in range(12):
        a = 2 * math.pi * k / 12
        r = 0.92
        big = k % 3 == 0
        bx(f"clock.bar{k}", (0.07 if not big else 0.1, 0.06, 0.2 if not big else 0.3), (r * math.sin(a), -0.08, r * math.cos(a)), M["clockbar"], ctx["clock"], rot=(0, a, 0))
    ctx["hand_h"] = kit.empty("clock.hh", (0, -0.1, 0), ctx["clock"])
    bx("clock.hand1", (0.1, 0.05, 0.5), (0, 0, 0.22), M["clockbar"], ctx["hand_h"], bevel=0.01)
    ctx["hand_m"] = kit.empty("clock.hm", (0, -0.14, 0), ctx["clock"])
    bx("clock.hand2", (0.07, 0.05, 0.8), (0, 0, 0.36), M["clockbar"], ctx["hand_m"], bevel=0.01)
    ctx["hand_h"].rotation_euler = (0, math.radians(-100), 0)
    ctx["hand_m"].rotation_euler = (0, math.radians(120), 0)
    # ---- the arch seat: a stone bench cut into the back wall, worn into two hollows
    bx("seat.block", (2 * SEAT_X, ARCH_Y1 - SEAT_Y0, SEAT_H), (0, (SEAT_Y0 + ARCH_Y1) / 2, SEAT_H / 2), M["stone2"], bevel=0.04)
    for sx in (-1, 1):
        bx(f"seat.hollow{sx}", (0.95, 0.9, 0.02), (sx * 0.62, SEAT_Y0 + 0.75, SEAT_H + 0.0), M["hollow"], bevel=0.01)
    for k, sx in enumerate((-0.05, 0.05)):   # the lore plant: two faded-rose strokes scratched in the lip
        bx(f"seat.stroke{k}", (0.035, 0.03, 0.17), (sx, SEAT_Y0 - 0.008, SEAT_H - 0.1), M["rose"], bevel=0.005)
    # ---- the fountain
    kit.cyl("fountain.basin", 1.7, 0.55, (-2.8, 6.4, 0.275), M["stone2"], n=40)
    kit.cyl("fountain.water", 1.5, 0.03, (-2.8, 6.4, 0.5), M["water"], n=40)
    kit.cyl("fountain.post", 0.25, 1.9, (-2.8, 6.4, 0.95), M["stone"], n=16)
    kit.cyl("fountain.bowl", 0.7, 0.18, (-2.8, 6.4, 1.8), M["stone2"], n=24)
    kit.cyl("fountain.jet", 0.06, 0.4, (-2.8, 6.4, 2.0), M["water"], n=8)
    kit.cyl("fountain.step", 2.1, 0.12, (-2.8, 6.4, 0.06), M["stonedark"], n=40)
    # ---- west wall: bike repair stand (green awning), bakery (mint and cream awning), houses
    ctx["fac"] = []
    e_, _ = facade("bikeshop", -11.0, -0.1, 90, 4.2, 3.2, 2.0, M, "paint1", 2, windows=1, door=False, roof=False)
    striped_awning("bikeaw", -4.2 / 2, 4.2 / 2, -0.05, -1.6, 3.0, 2.6, M, "green", "cream", n=8, parent=None)
    for o in [o for o in bpy.data.objects if o.name.startswith("bikeaw")]:
        o.parent = e_
        o.location = (o.location.x, o.location.y, o.location.z)
    bakery_e, bakery_door = facade("bakery", -11.0, 4.6, 90, 5.2, 3.6, 3.0, M, "paint0", 0, windows=2, door=True, door_x=0.0)
    ctx["bakery_door"] = bakery_door
    for o in [o for o in bpy.data.objects if o.name.startswith("bkaw")]:
        pass
    striped_awning("bkaw", -2.6, 2.6, -0.15, -1.45, 3.4, 2.9, M, "mint", "cream", n=12, parent=None)
    for o in [o for o in bpy.data.objects if o.name.startswith("bkaw")]:
        o.parent = bakery_e
    for k, (yy, paint, di) in enumerate(((9.6, "paint2", 1), (13.0, "paint4", 3))):
        e, dp = facade(f"housew{k}", -11.0, yy, 90, 3.8, 5.0, 3.0, M, paint, di, windows=2)
        ctx["doorpivots"].append(dp)
    # ---- east wall: the cafe, houses
    cafe_e, _ = facade("cafe", 11.0, 4.6, -90, 5.4, 3.6, 3.0, M, "paint5", 1, windows=2, door=True, door_x=1.4)
    striped_awning("cafeaw", -2.7, 2.7, -0.15, -1.4, 3.3, 2.85, M, "terra", "cream", n=12, parent=None)
    for o in [o for o in bpy.data.objects if o.name.startswith("cafeaw")]:
        o.parent = cafe_e
    for k, (yy, paint, di) in enumerate(((9.2, "paint6", 2), (13.0, "paint7", 0), (0.9, "paint4", 1), (-3.4, "paint2", 3))):
        e, dp = facade(f"housee{k}", 11.0, yy, -90, 3.8, 5.0, 3.0, M, paint, di, windows=2)
        ctx["doorpivots"].append(dp)
    # ---- north wall beside the arch, and the south row
    for k, (xx, paint, di) in enumerate(((-8.8, "paint6", 0), (8.8, "paint3", 1), (-8.8, None, 0))):
        if paint is None:
            continue
        e, dp = facade(f"housen{k}", xx, 14.0, 0, 4.0, 5.2, 3.2, M, paint, di, windows=2, door=False)
    for k in range(7):
        xx = -9.0 + k * 3.0
        e, dp = facade(f"houses{k}", xx, -5.0, 180, 2.9, 4.6 + (k % 3) * 0.5, 3.0, M, f"paint{(k + 2) % 8}", k, windows=2)
    bx("bakery.counter", (0.7, 1.7, 1.0), (-10.1, 3.0, 0.5), M["mint"], bevel=0.03)
    bx("bakery.top", (0.85, 1.85, 0.06), (-10.1, 3.0, 1.03), M["cream"], bevel=0.02)
    for k in range(2):   # square steps (the wedding photo)
        bx(f"steps{k}", (7.0, 1.2 - k * 0.5, 0.17 * (k + 1)), (5.5, 12.2 + k * 0.25, 0.085 * (k + 1)), M["stone2"], bevel=0.02)
    # ---- the cafe: three round tables, umbrellas, a service counter
    ctx["umbrellas"] = []
    for k, ty in enumerate((3.6, 5.2, 6.8)):
        tx = 9.0
        kit.cyl(f"table{k}", 0.45, 0.04, (tx, ty, 0.75), M["cream"], n=24)
        kit.cyl(f"tleg{k}", 0.05, 0.75, (tx, ty, 0.375), M["metal"], n=8)
        kit.cyl(f"tbase{k}", 0.25, 0.04, (tx, ty, 0.02), M["metal"], n=16)
        kit.cyl(f"upole{k}", 0.035, 2.2, (tx, ty, 1.1), M["metal"], n=8)
        kit.cyl(f"umb{k}", 1.1, 0.35, (tx, ty, 2.3), M["terra" if k != 1 else "cream"], n=12, r2=0.1)
        for sx in (-1, 1):
            bx(f"chair{k}{sx}", (0.42, 0.42, 0.06), (tx - 0.2, ty + sx * 0.7, 0.45), M["wood"], bevel=0.02)
            bx(f"chairb{k}{sx}", (0.04, 0.42, 0.45), (tx - 0.2 + 0.2, ty + sx * 0.7, 0.7), M["wood"], bevel=0.02)
            for lx in (-0.17, 0.17):
                for ly in (-0.17, 0.17):
                    bx(f"chairl{k}{sx}{lx}{ly}", (0.04, 0.04, 0.45), (tx - 0.2 + lx, ty + sx * 0.7 + ly, 0.225), M["wood"])
    bx("counter", (0.8, 2.0, 1.05), (10.3, 2.0, 0.525), M["terra"], bevel=0.03)
    bx("countertop", (0.95, 2.1, 0.06), (10.2, 2.0, 1.08), M["cream"], bevel=0.02)
    for k in range(2):
        kit.cyl(f"cup{k}", 0.05, 0.1, (10.0, 1.6 + 0.5 * k, 1.16), M["cream"], n=12)
    for k, fy in enumerate((8.05, 9.3, 10.55)):
        bx(f"fence.post{k}", (0.1, 0.1, 1.0), (-4.7, fy, 0.5), M["wood"])
    for zz in (0.5, 0.88):
        bx(f"fence.rail{zz}", (0.07, 2.7, 0.07), (-4.7, 9.3, zz), M["wood"])
    # ---- the bus shelter
    for sx, sy in ((7.2, -1.6), (7.2, 0.8), (8.8, -1.6), (8.8, 0.8)):
        bx(f"shelter.post{sx}{sy}", (0.08, 0.08, 2.4), (sx, sy, 1.2), M["metal"])
    bx("shelter.roof", (2.1, 2.7, 0.1), (8.0, -0.4, 2.45), M["green"], bevel=0.03)
    bx("shelter.back", (0.05, 2.4, 1.5), (8.85, -0.4, 1.5), M["win"])
    bx("shelter.bench", (0.5, 2.0, 0.06), (8.5, -0.4, 0.5), M["wood"])
    # ---- the bike stand and a bike
    bx("stand.bench", (0.7, 1.5, 0.9), (-10.0, 0.0, 0.45), M["wood2"], bevel=0.02)
    ctx["bike"] = bike(M)
    # ---- a few props (cap, bun bag, phone, loaf)
    ctx["props"]["cap"] = prop_cap(M)
    ctx["props"]["bag"] = bx("bag", (0.16, 0.08, 0.2), (-0.12, SEAT_Y0 + 0.6, SEAT_H + 0.1), M["cream"], bevel=0.02)
    ctx["props"]["phone"] = bx("phone", (0.07, 0.15, 0.012), (-0.2, SEAT_Y0 + 0.4, SEAT_H + 0.01), M["dark"], bevel=0.004)
    ctx["props"]["loaf"] = bx("loaf", (0.34, 0.16, 0.14), (0, 0, -9), M["wood"], bevel=0.05)
    for p in ctx["props"].values():
        p.hide_render = True
    # ---- lights
    sun = kit.light("sun", "SUN", (0, 0, 20), 1.0, "#fff0d8")
    ctx["sun"] = sun
    kit.light("archlamp", "AREA", (0, 15.4, 4.3), 90, "#ffe2b0", rot=(0, 0, 0), size=2.4)
    rim = kit.light("spanrim", "SPOT", (0.0, 17.15, 1.3), 1.0, "#bcd2ff", rot=(math.pi / 2, 0, 0), size=0.6, spot=125, blend=1.0)
    key = kit.light("spankey", "AREA", (2.9, 14.2, 0.45), 1.0, "#ffd9b0", size=1.0)
    kit.aim(key, (-0.3, 16.6, 0.9))
    fr = kit.light("spanfront", "AREA", (0, 11.0, 1.6), 1.0, "#cfd8e8", size=3.0)
    kit.aim(fr, (0, 16.6, 1.0))
    il = kit.light("ilanface", "SPOT", (-1.4, 12.4, 0.9), 1.0, "#cfd8f0", size=0.3, spot=26, blend=0.8)
    kit.aim(il, (-0.62, 15.6, 0.85))
    fc = kit.light("spanface", "SPOT", (1.5, 12.5, 1.1), 1.0, "#ffd9b0", size=0.3, spot=14, blend=0.6)
    kit.aim(fc, (0.0, 16.9, 1.5))
    return ctx


def bike(M):
    e = kit.empty("bike", (-10.0, 0.3, 0.0), rot=(0, 0, math.radians(15)))
    for sy in (-0.55, 0.55):
        kit.cyl(f"bike.w{sy}", 0.34, 0.05, (0, sy, 0.36), M["tyre"], e, rot=(0, math.pi / 2, 0), n=24)
        kit.cyl(f"bike.r{sy}", 0.27, 0.06, (0, sy, 0.36), M["metal"], e, rot=(0, math.pi / 2, 0), n=24)
    bx("bike.f1", (0.04, 1.1, 0.04), (0, 0, 0.55), M["terra"], e, rot=(0.25, 0, 0))
    bx("bike.f2", (0.04, 0.6, 0.04), (0, -0.2, 0.7), M["terra"], e, rot=(-0.3, 0, 0))
    bx("bike.bar", (0.4, 0.04, 0.04), (0, -0.55, 0.88), M["metal"], e)
    bx("bike.seat", (0.1, 0.25, 0.05), (0, 0.4, 0.8), M["dark"], e)
    return e


def prop_cap(M):
    e = kit.empty("propcap", (-0.55, SEAT_Y0 + 0.6, SEAT_H))
    kit.box("propcap.c", (0.3, 0.3, 0.13), (0, 0, 0.07), kit.plastic("#d0473c", 0.6), e, bevel=0.05)
    kit.box("propcap.b", (0.2, 0.2, 0.025), (0, -0.2, 0.03), kit.plastic("#d0473c", 0.6), e, bevel=0.01)
    return e


# ------------------------------------------------------------------------------------------ cast extras


def _ensure(ctx, story, tl):
    """First frame: the Span's wide body, the gold stacks, the shadow shapes (the cast exists by now)."""
    if ctx.get("ready"):
        return
    ctx["ready"] = True
    M = ctx["M"]
    cast = story["cast"]
    # ---- the Span
    if "span" in cast:
        spec = cast["span"]
        k = SPAN_K
        for nm in ("span.torsom", "span.collar"):
            o = bpy.data.objects.get(nm)
            if o is not None:
                bpy.data.objects.remove(o, do_unlink=True)
        tor = bpy.data.objects["span.torso"]
        shirt = rig.cloth(spec, "shirt")
        kit.box("span.wide", (2.0 * k, 1.0, 2.0), (0, 0, 1.0), shirt, tor, bevel=0.28, seg=3)
        rib = kit.plastic("#b97d80", 0.95, "spanrib")
        kit.box("span.hem", (2.0 * k + 0.02, 1.04, 0.28), (0, 0, 0.12), rib, tor, bevel=0.05)
        edge = kit.plastic("#f6e3cc", 0.8, "spanedge")
        for sx in (-1, 1):
            kit.box(f"span.edge{sx}", (0.34, 1.05, 2.04), (sx * (k - 0.13), 0, 1.0), edge, tor, bevel=0.05)
        kit.box("span.neckroll", (1.1, 1.06, 0.3), (0, 0, 1.98), rib, tor, bevel=0.08)
        for sx in (-1, 1):
            a = bpy.data.objects[f"span.arm{sx}"]
            a.location.x = sx * (k + 0.5)
            lg = bpy.data.objects[f"span.leg{sx}"]
            lg.location.x = sx * (k - 0.45)
    # ---- the gold stacks
    ctx["stacks"] = {}
    for who, spec in cast.items():
        cap = spec.get("stack_cap", 0)
        if not cap:
            continue
        hg = bpy.data.objects[f"{who}.headg"]
        u = BLOCK_M / (S * spec.get("height", 1.0))
        st = kit.empty(f"{who}.stack", (0, 0, 0.72), hg)
        blocks = []
        for i in range(cap):
            b = kit.box(f"{who}.gb{i}", (u, u, u), (0.012 * ((i * 7) % 5 - 2) / 2, 0.01 * ((i * 3) % 3 - 1), u * (i + 0.5)), M["gold"], st, bevel=0.045 * u / 0.38)
            p = kit.box(f"{who}.gp{i}", (u * 0.52, 0.015, u * 0.52), (0, -u / 2 - 0.004, 0), M["gold2"], b, bevel=0.004)
            blocks.append(b)
        ctx["stacks"][who] = {"root": st, "blocks": blocks, "u": u, "events": [], "cap": cap, "h": spec.get("height", 1.0)}
    for c in cues(tl, "stack"):
        if c["who"] in ctx["stacks"]:
            ctx["stacks"][c["who"]]["events"].append(c)
    for s in ctx["stacks"].values():
        s["events"].sort(key=lambda c: c["t"])
        pn = 0
        for c in s["events"]:
            c["prev"] = pn
            c.setdefault("mode", "land" if c["n"] > pn else "drop" if c["n"] < pn else "set")
            pn = c["n"]
    ctx["arcpool"] = [kit.box(f"arcblock{i}", (BLOCK_M, BLOCK_M, BLOCK_M), (0, 0, -20), M["gold"], None, bevel=0.006)
                      for i in range(8)]
    # ---- the Span's shadow shapes (flat, dark, laid on the cobbles or the back wall)
    ctx["shadows"]["floor"] = shadow_shape("shfloor", M, "floor")
    ctx["shadows"]["wall"] = shadow_shape("shwall", M, "wall")


def shadow_shape(name, M, kind):
    """The Span's silhouette as flat dark convex pieces that only abut (so the alpha never doubles up): one small round
    head on a neck, sloped shoulders, a torso 1.6 m wide, an arm hung at each far end with a gap to the torso, and (on the
    cobbles) two legs. In (u across, v along): on the floor v runs away from the feet, on the wall v is up."""
    e = kit.empty(name, (0, 0, -30))
    mat = M["shadow"]

    def poly(nm, pts):
        verts = [(u, v, 0.0) for u, v in pts]
        ob = kit.mesh_obj(f"{name}.{nm}", verts, [tuple(range(len(pts)))], mat, e)
        ob.visible_shadow = False
        return ob

    k = 0.8
    v0, vs, vn, vh = 0.0, 0.72, 0.8, 1.0      # torso base, shoulder line, neck top, head centre (seated, so no legs)
    poly("torso", [(-k, v0), (k, v0), (k, vs), (-k, vs)])
    for sx in (-1, 1):
        poly(f"arm{sx}", [(sx * (k + 0.04), vs), (sx * (k + 0.36), vs), (sx * (k + 0.44), v0 + 0.05), (sx * (k + 0.12), v0 + 0.05)])
    poly("sh", [(-(k + 0.36), vs), (k + 0.36, vs), (k + 0.36, vs + 0.04), (0.7, vs + 0.16), (0.09, vn - 0.02),
                (-0.09, vn - 0.02), (-0.7, vs + 0.16), (-(k + 0.36), vs + 0.04)])
    poly("neck", [(-0.09, vn - 0.02), (0.09, vn - 0.02), (0.09, vn + 0.03), (-0.09, vn + 0.03)])
    hr = 0.21
    poly("head", [(hr * math.cos(2 * math.pi * i / 28), vh + hr * math.sin(2 * math.pi * i / 28)) for i in range(28)])
    return e


# ------------------------------------------------------------------------------------------------ animate


def _env(tl, t):
    """The light grade at t: the cues' states, each ramped in over its dur from the one before."""
    cs = sorted(cues(tl, "env"), key=lambda c: c["t"])
    cur = ENV[cs[0]["state"]] if cs else ENV["day"]
    prev = cur
    for c in cs:
        nxt = ENV[c["state"]]
        if t < c["t"]:
            break
        u = _ss((t - c["t"]) / max(0.3, c.get("dur", 0.3)))
        cur = tuple(_mixv(a, b, u) for a, b in zip(prev, nxt))
        if u >= 1.0:
            prev = nxt
    return cur, (cs and [c for c in cs if c["t"] <= t] or [{"state": "day"}])[-1]["state"]


def _mixv(a, b, u):
    if isinstance(a, str):
        ca, cb = _hex(a), _hex(b)
        return tuple(x + (y - x) * u for x, y in zip(ca, cb))
    if isinstance(a, tuple):
        return tuple(x + (y - x) * u for x, y in zip(a, b))
    return a + (b - a) * u


def _setrgb(v):
    return tuple(v) if not isinstance(v, str) else _hex(v)


def _stack_count(events, t):
    n, last = 0, None
    for c in events:
        if c["t"] <= t + 1e-9:
            last = c
            n = c["n"]
    return n, last


def st_hidden(states, who):
    s = states.get(who)
    return s is None or s["hidden"]


def animate_stacks(ctx, tl, t, states):
    for who, s in ctx["stacks"].items():
        hg = bpy.data.objects[f"{who}.headg"]
        root = bpy.data.objects.get(who)
        hidden = root.hide_render
        n, last = _stack_count(s["events"], t)
        st = states.get(who) or ac.state(tl, who, t)
        keys = tl["acting"].get(who, [])
        base = 0.72 if not _capon(keys, t, who) else 0.9
        s["root"].location = (0, 0, base)
        pitch = st["head_pitch"] + st["lean"] + math.radians(ac._held(keys, "bend", t, 0.0))
        sway = math.radians(2.6) * min(1.0, n / 10.0)
        ph = hash(who) % 7
        fol = ac._held(keys, "stackfollow", t, 0.0)
        s["root"].rotation_euler = (-pitch * (1.0 - fol) + sway * math.sin(t * 1.7 + ph) * 0.8, sway * math.sin(t * 1.3 + ph * 1.7), 0)
        u = s["u"]
        for i, b in enumerate(s["blocks"]):
            vis = (i < n) and not hidden
            z = u * (i + 0.5)
            x = 0.0
            sc = 1.0
            if last is not None and i == n - 1 and last.get("mode", "land") == "land":
                k = (t - last["t"]) / 0.25
                if 0 <= k < 1:
                    z += (0.30 / (S * s["h"])) * (1 - k)
            if not vis:
                # a block that dropped off in the last 0.5 s: slides off and shrinks away
                for c in s["events"]:
                    prev_n = c.get("prev", None)
                    if prev_n is None:
                        continue
                    if c["n"] <= i < prev_n and c["mode"] == "drop":
                        k = (t - c["t"] - (prev_n - 1 - i) * 0.05) / 0.5
                        if 0 <= k < 1 and not hidden:
                            vis = True
                            x = 0.9 * u * _ss(k) * 2.0
                            z -= 0.5 * u * _ss(k)
                            sc = max(0.01, 1.0 - _ss(k))
            b.hide_render = not vis
            b.location = (x, 0.0, z)
            b.scale = (sc, sc, sc)
            for ch in b.children:
                ch.hide_render = not vis


def _capon(keys, t, who):
    if who != "ilan":
        return False
    v = True
    for k in keys:
        if "cap" in k and k["t"] <= t + 1e-9:
            v = k["cap"]
    return v


def animate_arcs(ctx, tl, t):
    pool = ctx["arcpool"]
    for ab in pool:
        ab.hide_render = True
    k = 0
    for c in cues(tl, "arc"):
        dur = c.get("dur", 0.6)
        if c["t"] <= t < c["t"] + dur and k < len(pool):
            src, dst = ctx["stacks"][c["from"]], ctx["stacks"][c["to"]]
            if k == 0:
                bpy.context.view_layer.update()
            a = src["blocks"][max(0, c["si"])].matrix_world.translation.copy()
            b = dst["blocks"][max(0, c["di"])].matrix_world.translation.copy()
            u = (t - c["t"]) / dur
            p = a.lerp(b, _ss(u))
            p.z += 1.1 * math.sin(math.pi * u)
            ab = pool[k]
            ab.location = p
            ab.rotation_euler = (u * 3.0, u * 2.0, 0)
            ab.scale = (1.7, 1.7, 1.7)
            ab.hide_render = False
            k += 1


def animate(kit_, story, tl, t, ctx):
    _ensure(ctx, story, tl)
    M = ctx["M"]
    over = {}
    # ---- light grade
    (se, sc, sd, wc, ws, lamp), state = _env(tl, t)
    sun = ctx["sun"]
    d = V(sd).normalized()
    sun.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    ld = kit.LIGHTS["sun"]["light"]
    ld.color = _lin(_setrgb(sc))
    over["sun"] = se
    over["archlamp"] = lamp
    w = bpy.context.scene.world.node_tree.nodes["Background"]
    wcol = _lin(_setrgb(wc))
    w.inputs["Color"].default_value = (*wcol, 1)
    w.inputs["Strength"].default_value = ws
    wet = state == "rain" or (se < 1.0)
    # wet cobbles and puddles follow the grade (on from the rain's first frame; off at the clearing)
    rain_cs = [c for c in cues(tl, "env") if c["t"] <= t]
    rainy = bool(rain_cs) and rain_cs[-1]["state"] in ("rain", "raindim") or (bool(rain_cs) and rain_cs[-1].get("wet", False))
    ctx["ground"].hide_render = rainy
    ctx["groundwet"].hide_render = not rainy
    for p in ctx["puddles"]:
        p.hide_render = not rainy
    # ---- people: sitting, bending, caps, ghosts, placement
    states = {}
    for who, keys in tl["acting"].items():
        root = bpy.data.objects.get(who)
        if root is None:
            continue
        st = ac.state(tl, who, t)
        states[who] = st
        pl = ac._switch(keys, "place", t, [0, 0, 0])
        root.location = (root.location.x + pl[0], root.location.y + pl[1], root.location.z + pl[2])
        tor = bpy.data.objects.get(f"{who}.torso")
        if tor is not None:
            tor.rotation_euler = (math.radians(ac._held(keys, "bend", t, 0.0)), 0, 0)
        sitting = ac._switch(keys, "sit", t, False)
        for sx in (-1, 1):
            lg = bpy.data.objects.get(f"{who}.leg{sx}")
            if lg is not None and sitting:
                lg.rotation_euler = (-math.pi / 2, 0, 0)
        ghost = ac._switch(keys, "ghost", t, False)
        if ghost and not st["hidden"]:
            for ob in root.children_recursive:
                ob.hide_render = False
                ob.visible_camera = False
        else:
            for ob in root.children_recursive:
                ob.visible_camera = True
        if who == "ilan":
            on = _capon(keys, t, who)
            for nm in ("capc", "capb"):
                ob = bpy.data.objects.get(f"ilan.{nm}")
                if ob is not None:
                    ob.hide_render = (not on) or st["hidden"]
        if who == "span":
            for ob in root.children_recursive:
                if ob.name.startswith("span.gl"):
                    ob.hide_render = True
    animate_stacks(ctx, tl, t, states)
    animate_arcs(ctx, tl, t)
    # ---- the Span's light: dead front, a low side key, a cool rim
    sp = states.get("span")
    shown = bool(sp) and not sp["hidden"] and not ac._switch(tl["acting"].get("span", []), "ghost", t, False)
    spl = [c for c in cues(tl, "spanlight") if c["t"] <= t]
    on = shown and bool(spl) and spl[-1].get("on", True)
    mode = spl[-1] if spl else {}
    over["spanrim"] = (mode.get("rim", 700) if on else 0.0)
    over["spankey"] = (mode.get("key", 260) if on else 0.0)
    over["spanfront"] = (mode.get("front", 0) if on else 0.0)
    over["spanface"] = (mode.get("face", 0) if on else 0.0)
    if on:
        over["archlamp"] = lamp * 0.4
    sfl = [c for c in cues(tl, "seatfill") if c["t"] <= t]
    if sfl and not on:
        over["spanfront"] = sfl[-1].get("e", 0.0)
        if sfl[-1].get("e", 0.0):
            over["archlamp"] = lamp * 1.0
    il = [c for c in cues(tl, "ilanlight") if c["t"] <= t]
    over["ilanface"] = 320.0 if (il and il[-1].get("on", True) and not st_hidden(states, "ilan")) else 0.0
    # ---- the doors
    dc = [c for c in cues(tl, "door") if c["t"] <= t]
    if dc:
        c = dc[-1]
        prev = dc[-2]["open"] if len(dc) > 1 else 0.0
        u = 1.0 if c.get("init") else _ss((t - c["t"]) / max(0.3, c.get("dur", 0.4)))
        ctx["bakery_door"].rotation_euler = (0, 0, math.radians(-105 * (prev + (c["open"] - prev) * u)))
    else:
        ctx["bakery_door"].rotation_euler = (0, 0, 0)
    allh = cues(tl, "doors")
    for i, dp in enumerate(ctx["doorpivots"]):
        hc = [c for c in allh if c["t"] <= t and (c.get("only") is None or i in c["only"])]
        o = 0.0
        if hc:
            c = hc[-1]
            prev = hc[-2]["open"] if len(hc) > 1 else 0.0
            u = _ss((t - c["t"] - (0.0 if c.get("only") else 0.12 * i)) / 0.6)
            o = prev + (c["open"] - prev) * u
        dp.rotation_euler = (0, 0, math.radians(-100 * o))
    # ---- props
    pc = {}
    for c in cues(tl, "prop"):
        if c["t"] <= t:
            pc[c["item"]] = c
    for nm, ob in ctx["props"].items():
        c = pc.get(nm)
        ob.hide_render = not (c and c.get("on", True))
        for ch in ob.children:
            ch.hide_render = ob.hide_render
        if c and c.get("loc") and not ob.hide_render:
            ob.location = V(c["loc"]) if nm != "cap" else V(c["loc"])
    # ---- the Span's shadow
    sc_ = [c for c in cues(tl, "shadow") if c["t"] <= t]
    kind = sc_[-1]["kind"] if sc_ else "none"
    for k, e in ctx["shadows"].items():
        for ob in e.children:
            ob.hide_render = k != kind
    if kind == "floor":
        e = ctx["shadows"]["floor"]
        e.location = (sc_[-1].get("x", 0.0), sc_[-1].get("y", SEAT_Y0), 0.05)
        e.rotation_euler = (0, 0, math.radians(sc_[-1].get("yaw", 180)))
        e.scale = (1.0, sc_[-1].get("stretch", 1.0), 1.0)
    elif kind == "wall":
        e = ctx["shadows"]["wall"]
        e.location = (sc_[-1].get("x", 0.0), ARCH_Y1 - 0.02, SEAT_H + 0.0)
        e.rotation_euler = (math.pi / 2, 0, 0)
        e.scale = (1.0, 1.0, 1.0)
    return over
