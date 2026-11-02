"""Night Market (ep40): a Friday night market in an open-air car park. Two facing rows of striped-awning food stalls
under strings of round paper lanterns, an arch of lanterns where the market begins, wet tarmac, a gold luck coin
floating over every head, and the Half. Built from kit.py's parts; nothing here is shared with another story's set.
There is no lettering anywhere: no signs, menus, prices or numbers. No money is shown. The only coins are the luck coins.

Coordinates (metres, z up). The walkway runs along +y between the rows: the left row's counters front x = -2.2, the
right row's x = +2.2. Six stalls a side, centres y = 2.2 + 2.6 i. Ours is the left row's i = 3 (y 10.0), the noodle
stall next door is i = 4 (y 12.6), the stall opposite ours is the right row's i = 3. The arch is at y = -0.8, with the
bell on its left pole. A character faces -y at yaw 0, +x at 90, +y at 180, -x at -90.

THE COINS. A gold disc 0.4 m across, one even matte gold on rim and faces (no emission, no sparkle), a sun face on its
-y side and a moon face on its +y side in low relief (a bump, with a hair of albedo shading, so it reads by shadow
and not by bright and dark). Every frame it turns to the camera by its own rule: a face coin shows the face it should
(sun or moon) tilted a little toward the lens and rocks a few degrees; mine shows its edge to the camera whichever
way the camera looks. A flip is a slow spin, at most one turn a second, over 2.4 s. Bea's coin only ever shows the moon.

THE HALF (the creature). One model, built once, posed by the "half" cue: the anatomical left half of an ordinary
adult R6 person (the half that is on the viewer's right when it faces you), cut down the exact middle. The cut is one
smooth lacquered indigo plane, the same material top to bottom, flush to the head, torso and leg. Its one eye is a round
black eye with a small highlight, and half a wide flat smile ends at the plane. It has no coin. It is lit for fear:
nothing lights its face from the camera side; a warm key from the side, a cool rim behind it (both follow the
camera), and its eye glint is the brightest thing on it.

Story keys read here (all optional): "equal_coins": [shot ids] where every coin is drawn the same size on screen.
Cues read here: mood (the lantern level, ramped), flip, merge, bell, half, queue, shadow_light.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V
from PIL import Image, ImageDraw

from blocky import acting, faces, rig

S = rig.S
WORK = Path(tempfile.mkdtemp(prefix="ep40-"))

GOLD = "#c9a24a"
LANTERN_RED, LANTERN_GLOW = "#c8352a", "#ffb060"
INDIGO = "#2b2f6b"
ROWS_Y = [2.2 + 2.6 * i for i in range(6)]
ARCH_Y = -0.8
COIN_R, COIN_T = 0.2, 0.045
BEA = (-3.35, 9.45)
SPOT = (-3.35, 10.75)

STALL_COLORS = {          # awning stripe colours (the first is cream)
    ("L", 3): ("#c8352a", "ours"), ("L", 4): ("#2f6fa8", "noodle"),
    ("L", 0): ("#2d7f7a", ""), ("L", 1): ("#d5a32b", ""), ("L", 2): ("#7d4a8a", ""), ("L", 5): ("#a05a2a", ""),
    ("R", 0): ("#3d6ea6", ""), ("R", 1): ("#c8352a", ""), ("R", 2): ("#2d7f7a", ""), ("R", 3): ("#d5a32b", ""),
    ("R", 4): ("#7d4a8a", ""), ("R", 5): ("#2f6fa8", ""),
}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------------------------------------ materials
def pbr(kit, name, hexc, rough=0.6, spec=0.3):
    return kit.plastic(hexc, rough, name=name, spec=spec)


def stripes(kit, c1, c2, scale=3.0, name=None):
    """Even stripes along the object's own Y (an awning's width): fract(y * scale) < 0.5 is c1."""
    name = name or f"stripes {c1} {c2}"
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.85
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = scale
    nt.links.new(sep.outputs["Y"], mul.inputs[0])
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


def image_mat(kit, name, path, rough=0.8, noncolor=False):
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tex = nt.nodes.new("ShaderNodeTexImage")
    img = bpy.data.images.load(str(path))
    img.colorspace_settings.name = "Non-Color" if noncolor else "sRGB"
    tex.image = img
    tex.interpolation = "Linear"
    uv = nt.nodes.new("ShaderNodeUVMap")
    nt.links.new(uv.outputs["UV"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m


def textured_quad(kit, name, w, h, mat, loc, rot=(0, 0, 0), parent=None):
    """A flat quad in its own XZ plane facing -y, UVs 0..1 (u along +x, v up)."""
    x, z = w / 2, h / 2
    verts = [(-x, 0, -z), (x, 0, -z), (x, 0, z), (-x, 0, z)]
    ob = kit.mesh_obj(name, verts, [(0, 1, 2, 3)], mat, parent, loc, rot)
    uv = ob.data.uv_layers.new(name="UVMap")
    uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for poly in ob.data.polygons:
        for li in poly.loop_indices:
            uv.data[li].uv = uvs[ob.data.loops[li].vertex_index]
    return ob


# ------------------------------------------------------------------------------------------------ the coin
def coin_images():
    """Height maps for the two faces (PIL 'L', top = up): sun on the -y side, moon on the +y side."""
    N = 512
    c = N / 2

    def ring(d, r0, r1, v):
        d.ellipse([c - r1 * c, c - r1 * c, c + r1 * c, c + r1 * c], fill=v)
        d.ellipse([c - r0 * c, c - r0 * c, c + r0 * c, c + r0 * c], fill=110)

    sun = Image.new("L", (N, N), 110)
    d = ImageDraw.Draw(sun)
    ring(d, 0.86, 0.97, 200)
    for k in range(8):
        a = k * math.pi / 4
        pts = []
        for r, w in ((0.58, 0.075), (0.84, 0.0)):
            pts.append((c + r * c * math.cos(a) - w * c * math.sin(a), c - r * c * math.sin(a) - w * c * math.cos(a)))
        for r, w in ((0.84, 0.0), (0.58, -0.075)):
            pts.append((c + r * c * math.cos(a) - w * c * math.sin(a), c - r * c * math.sin(a) - w * c * math.cos(a)))
        d.polygon(pts, fill=205)
    d.ellipse([c - 0.5 * c, c - 0.5 * c, c + 0.5 * c, c + 0.5 * c], fill=190)
    for ex in (-0.18, 0.18):
        d.ellipse([c + ex * c - 0.055 * c, c - 0.12 * c - 0.055 * c, c + ex * c + 0.055 * c, c - 0.12 * c + 0.055 * c], fill=60)
    d.arc([c - 0.3 * c, c - 0.2 * c, c + 0.3 * c, c + 0.28 * c], 25, 155, fill=60, width=int(0.055 * N))
    moon = Image.new("L", (N, N), 110)
    d = ImageDraw.Draw(moon)
    ring(d, 0.86, 0.97, 200)
    d.ellipse([c - 0.64 * c, c - 0.64 * c, c + 0.64 * c, c + 0.64 * c], fill=205)
    d.ellipse([c - 0.44 * c + 0.3 * c, c - 0.5 * c - 0.1 * c, c + 0.66 * c + 0.3 * c, c + 0.52 * c - 0.1 * c], fill=110)
    d.arc([c - 0.45 * c, c - 0.1 * c, c - 0.15 * c, c + 0.12 * c], 20, 160, fill=60, width=int(0.045 * N))
    p1, p2 = WORK / "coin-sun.png", WORK / "coin-moon.png"
    sun.save(p1)
    moon.save(p2)
    return p1, p2


def coin_material(kit, name, path):
    """Even matte gold. The relief is a bump from the face's height map; the albedo shifts by at most 12%."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.6
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = 0.2
            break
    tex = nt.nodes.new("ShaderNodeTexImage")
    img = bpy.data.images.load(str(path))
    img.colorspace_settings.name = "Non-Color"
    tex.image = img
    uv = nt.nodes.new("ShaderNodeUVMap")
    nt.links.new(uv.outputs["UV"], tex.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.9
    bp.inputs["Distance"].default_value = 0.012
    nt.links.new(tex.outputs["Color"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    mix = nt.nodes.new("ShaderNodeMath")          # albedo: 0.88 + 0.12 * height
    mix.operation = "MULTIPLY_ADD"
    mix.inputs[1].default_value = 0.12
    mix.inputs[2].default_value = 0.88
    nt.links.new(tex.outputs["Color"], mix.inputs[0])
    mul = nt.nodes.new("ShaderNodeMixRGB")
    mul.blend_type = "MULTIPLY"
    mul.inputs["Fac"].default_value = 1.0
    mul.inputs["Color1"].default_value = kit.col(GOLD)
    nt.links.new(mix.outputs[0], mul.inputs["Color2"])
    nt.links.new(mul.outputs["Color"], b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m


def build_coin(kit, name, mats, parent=None):
    """The coin: a ridged gold rim and two relief plates. Returns the root empty (its disc is in the XZ plane,
    the sun face toward -y)."""
    root = kit.empty(name, (0, 0, 2), parent)
    n = 96
    r0, r1 = COIN_R, COIN_R * 0.975
    verts, fcs = [], []
    for side in (-1, 1):
        for i in range(n):
            a = 2 * math.pi * i / n
            r = r0 if (i % 2) == 0 else r1
            verts.append((r * math.cos(a), side * COIN_T / 2, r * math.sin(a)))
    for i in range(n):
        j = (i + 1) % n
        fcs.append((i, n + i, n + j, j))
    fcs.append(tuple(range(n)))
    fcs.append(tuple(reversed(range(n, 2 * n))))
    kit.mesh_obj(f"{name}.rim", verts, fcs, mats["rim"], root, smooth=False)
    for side, key in ((-1, "sun"), (1, "moon")):
        k = 36
        rr = COIN_R * 0.93
        v = [(0, side * (COIN_T / 2 + 0.0015), 0)]
        for i in range(k):
            a = 2 * math.pi * i / k
            v.append((rr * math.cos(a), side * (COIN_T / 2 + 0.0015), rr * math.sin(a)))
        f = [(0, 1 + i, 1 + (i + 1) % k) for i in range(k)]
        if side > 0:
            f = [tuple(reversed(t)) for t in f]
        ob = kit.mesh_obj(f"{name}.{key}", v, f, mats[key], root)
        uv = ob.data.uv_layers.new(name="UVMap")
        for poly in ob.data.polygons:
            for li in poly.loop_indices:
                x, _, z = v[ob.data.loops[li].vertex_index]
                u = 0.5 + (x if side < 0 else -x) / (2 * rr)
                uv.data[li].uv = (u, 0.5 + z / (2 * rr))
    return root


# ------------------------------------------------------------------------------------------------ the market
def lantern(kit, ctx, name, loc, color, strength, sway=1.0, size=1.0):
    mat = ctx["lantern_mats"].setdefault(color, kit.emit(color, strength, name=f"lantern {color}"))
    ob = kit.sphere(name, 0.15 * size, loc, mat, seg=12)
    ob.scale = (1.0, 1.0, 1.25)
    cap = kit.cyl(name + ".cap", 0.05 * size, 0.04 * size, (loc[0], loc[1], loc[2] + 0.2 * size), ctx["M"]["dark"], n=8)
    ctx["lanterns"].append({"ob": ob, "cap": cap, "home": tuple(loc), "sway": sway, "seed": len(ctx["lanterns"]) * 1.7 + 0.3})
    return ob


def stall(kit, ctx, M, side, i):
    s = -1 if side == "L" else 1
    yc = ROWS_Y[i]
    stripe_c, kind = STALL_COLORS[(side, i)]
    nm = f"stall{side}{i}"
    X = lambda d: s * d         # a depth d behind the counter front becomes a world x
    # counter: front panel, top, ends, a shelf under
    kit.box(nm + ".front", (0.05, 2.5, 0.98), (X(2.225), yc, 0.49), M["wood"])
    kit.box(nm + ".top", (0.85, 2.56, 0.06), (X(2.62), yc, 1.01), M["wood_top"], bevel=0.015)
    for e in (-1, 1):
        kit.box(nm + f".end{e}", (0.8, 0.05, 0.98), (X(2.62), yc + e * 1.25, 0.49), M["wood"])
    kit.box(nm + ".shelf", (0.7, 2.4, 0.04), (X(2.6), yc, 0.45), M["wood_top"])
    # posts, awning (red-and-cream stripes sloping up toward the back), valance, back wall
    for e in (-1, 1):
        kit.cyl(nm + f".pf{e}", 0.035, 2.7, (X(2.12), yc + e * 1.27, 1.35), M["dark"], n=8)
        kit.cyl(nm + f".pb{e}", 0.035, 3.3, (X(4.3), yc + e * 1.27, 1.65), M["dark"], n=8)
    ang = math.atan2(0.5, 2.3)
    L = math.hypot(2.3, 0.5)
    sm = stripes(kit, "#efe2c4", stripe_c, 2.0, name=f"awning {side}{i}")
    aw = kit.box(nm + ".awning", (L, 2.7, 0.04), (X(3.25), yc, 2.95), sm)
    aw.rotation_euler = (0, ang if s < 0 else -ang, 0)
    val = kit.box(nm + ".valance", (0.03, 2.7, 0.3), (X(2.06), yc, 2.58), sm)
    back = kit.box(nm + ".back", (0.04, 2.7, 3.3), (X(4.35), yc, 1.65), M["canvas"])
    if kind == "ours":
        ctx["our_awning"] = [aw, val]
    # steam lamp on a short pole at the counter's end, with its light
    lamp_y = yc + 1.1
    kit.cyl(nm + ".lamppole", 0.02, 0.6, (X(2.5), lamp_y, 1.34), M["dark"], n=6)
    kit.sphere(nm + ".lamp", 0.07, (X(2.5), lamp_y, 1.68), M["lampglow"], seg=10)
    kit.light(f"lamp{side}{i}", "POINT", (X(2.4), lamp_y, 1.7), 90.0, LANTERN_GLOW, size=0.12)
    # wares
    if kind == "noodle":
        kit.cyl(nm + ".pot", 0.34, 0.42, (X(2.7), yc, 1.27), M["steel"], n=20)
        kit.cyl(nm + ".potlid", 0.355, 0.05, (X(2.7), yc, 1.5), M["steel"], n=20)
        ctx["noodle_pot"] = (X(2.7), yc)
    else:
        for k in range(4):
            kit.cyl(nm + f".st{k}", 0.2, 0.1, (X(2.65), yc - 0.55, 1.09 + 0.1 * k), M["bamboo"], n=16)
        kit.cyl(nm + ".stlid", 0.21, 0.04, (X(2.65), yc - 0.55, 1.5), M["bamboo_d"], n=16)
    kit.box(nm + ".board", (0.3, 0.42, 0.03), (X(2.55), yc + 0.15 if kind != "noodle" else yc + 0.7, 1.06), M["board"], bevel=0.008)
    kit.box(nm + ".bowl", (0.14, 0.14, 0.08), (X(2.5), yc + 0.9, 1.08), M["cream"], bevel=0.02)


def build_stalls(kit, ctx, M):
    for side in ("L", "R"):
        for i in range(6):
            stall(kit, ctx, M, side, i)
    # the glyph on our front board: a coin split down the middle, the sun half at the viewer's right (+y), the moon at its left
    im = Image.new("RGB", (640, 360), "#efe2c4")
    d = ImageDraw.Draw(im)
    d.rectangle([6, 6, 633, 353], outline="#8a6a3a", width=8)
    cx, cy, R = 320, 180, 138
    d.pieslice([cx - R, cy - R, cx + R, cy + R], 270, 90, fill="#e8a020")        # right half: sun
    d.pieslice([cx - R, cy - R, cx + R, cy + R], 90, 270, fill="#33407f")        # left half: moon
    for k in range(-3, 4):                                                           # the sun's short rays
        a = math.radians(k * 24)
        d.line([(cx + (R + 8) * math.cos(a), cy - (R + 8) * math.sin(a)), (cx + (R + 34) * math.cos(a), cy - (R + 34) * math.sin(a))],
               fill="#e8a020", width=14)
    d.line([(cx, cy - R - 4), (cx, cy + R + 4)], fill="#3b2a1a", width=8)
    d.arc([cx + 25, cy - 20, cx + 100, cy + 60], 20, 160, fill="#3b2a1a", width=9)   # sun's smile
    d.ellipse([cx + 40, cy - 52, cx + 56, cy - 36], fill="#3b2a1a")
    d.ellipse([cx + 78, cy - 52, cx + 94, cy - 36], fill="#3b2a1a")
    d.ellipse([cx - 120, cy - 60, cx - 30, cy + 40], fill="#efe2c4")                   # the moon's crescent (a bite out)
    d.ellipse([cx - 90, cy - 70, cx - 5, cy + 30], fill="#33407f")
    d.arc([cx - 100, cy - 5, cx - 60, cy + 20], 20, 160, fill="#efe2c4", width=7)
    p = WORK / "glyph.png"
    im.save(p)
    gm = image_mat(kit, "glyph", p, 0.8)
    textured_quad(kit, "glyph", 1.2, 0.675, gm, (-2.196, 10.0, 0.5), (0, 0, math.radians(90)))
    # the old float tin on our shelf (S70): a dented lid with two short indigo strokes
    shelf_z = 0.47
    tin = kit.cyl("tin", 0.115, 0.085, (-2.78, 10.2, shelf_z + 0.0425), M["tin"], n=24)
    lid_im = Image.new("RGB", (256, 256), "#7d8087")
    d = ImageDraw.Draw(lid_im)
    d.ellipse([20, 20, 236, 236], outline="#5a5d63", width=8)
    d.ellipse([60, 150, 130, 200], fill="#6a6d74")                                       # the dent
    for x in (96, 150):
        d.line([(x, 70), (x + 6, 150)], fill=INDIGO, width=16)                          # two short indigo strokes
    lp = WORK / "lid.png"
    lid_im.save(lp)
    lm = image_mat(kit, "tin lid", lp, 0.5)
    k = 32
    rr = 0.118
    v = [(0, 0, 0)] + [(rr * math.cos(2 * math.pi * j / k), rr * math.sin(2 * math.pi * j / k), 0) for j in range(k)]
    f = [(0, 1 + j, 1 + (j + 1) % k) for j in range(k)]
    lid = kit.mesh_obj("tin.lid", v, f, lm, None, (-2.78, 10.2, shelf_z + 0.088), (math.radians(4), math.radians(3), 0))
    uv = lid.data.uv_layers.new(name="UVMap")
    for poly in lid.data.polygons:
        for li in poly.loop_indices:
            x, y, _ = v[lid.data.loops[li].vertex_index]
            uv.data[li].uv = (0.5 + x / (2 * rr), 0.5 + y / (2 * rr))
    # a folded mustard apron on the shelf beside it
    kit.box("apron.folded", (0.34, 0.42, 0.08), (-2.7, 9.5, shelf_z + 0.06), M["mustard"], bevel=0.03)


def build_lanterns(kit, ctx, M):
    pole_ys = [0.9 + 2.6 * i for i in range(7)]
    for yb in pole_ys:
        for s in (-1, 1):
            kit.cyl(f"pole{s}{yb}", 0.03, 4.0, (s * 2.15, yb, 2.0), M["dark"], n=6)
        # a cross string with a sag, lanterns hung along it
        n = 7
        for k in range(n):
            u = (k + 0.5) / n
            x = -2.15 + 4.3 * u
            z = 3.97 - 0.34 * math.sin(math.pi * u)
            lantern(kit, ctx, f"ln{yb:.1f}.{k}", (x, yb, z - 0.2), LANTERN_RED if (k + int(yb)) % 2 else LANTERN_GLOW, 1.8)
        kit.box(f"string{yb}", (4.3, 0.012, 0.012), (0, yb, 3.8), M["dark"])
    # a long string down each side of the walkway too
    for s in (-1, 1):
        for k in range(14):
            y = 0.3 + 1.2 * k
            lantern(kit, ctx, f"lns{s}.{k}", (s * 1.2, y, 3.6 + 0.06 * math.sin(k)), LANTERN_GLOW if k % 2 else LANTERN_RED, 1.7, size=0.9)


def build_arch(kit, ctx, M):
    for s in (-1, 1):
        kit.cyl(f"archpole{s}", 0.07, 3.8, (s * 2.6, ARCH_Y, 1.9), M["dark"], n=10)
    n = 13
    for k in range(n):
        a = math.pi * k / (n - 1)
        x, z = 2.6 * math.cos(a), 3.8 + 0.75 * math.sin(a)
        lantern(kit, ctx, f"arch.{k}", (x, ARCH_Y, z), LANTERN_RED if k % 2 else LANTERN_GLOW, 1.9, size=1.25)
    # the bell: a bracket off the left pole, a dark iron bell hung from a pivot
    kit.box("bell.bracket", (0.4, 0.05, 0.05), (-2.4, ARCH_Y, 2.65), M["dark"])
    pivot = kit.empty("bell.pivot", (-2.2, ARCH_Y, 2.62))
    kit.cyl("bell.body", 0.19, 0.34, (0, 0, -0.26), M["iron"], parent=pivot, n=20, r2=0.09)
    kit.cyl("bell.lip", 0.205, 0.04, (0, 0, -0.44), M["iron"], parent=pivot, n=20)
    kit.sphere("bell.clapper", 0.05, (0, 0, -0.5), M["iron"], parent=pivot, seg=8)
    ctx["bell"] = pivot


def build_ground(kit, ctx, M):
    kit.plane("tarmac", (90, 90), (0, 8, 0), M["tarmac"])
    # faded bay lines (no numbers, no words) in the car park outside the market
    for k in range(-5, 6):
        kit.box(f"bay{k}", (0.1, 5.0, 0.004), (k * 2.7, -8.0, 0.003), M["line"])
    for k in range(-2, 4):
        kit.box(f"bayend{k}", (5.0, 0.1, 0.004), (11.5 + 0, 3 + k * 2.7, 0.003), M["line"])
        kit.box(f"bayendl{k}", (5.0, 0.1, 0.004), (-11.5 + 0, 3 + k * 2.7, 0.003), M["line"])
    # parked cars, plain blocks, out in the dark
    cars = [(-9.5, 2.0, "#2a3340"), (-9.5, 6.4, "#4a2a2a"), (9.5, 14.0, "#2a3a34"), (9.5, 18.0, "#33323a"),
            (-9.5, 15.0, "#3a3a40"), (5.0, -12.0, "#2a2a34"), (-4.0, -13.0, "#4a3a2a"), (14.0, 9.0, "#2a3340")]
    for k, (x, y, c) in enumerate(cars):
        m = pbr(kit, f"car{c}", c, 0.4, 0.5)
        kit.box(f"car{k}", (2.0, 4.2, 0.9), (x, y, 0.65), m, bevel=0.15)
        kit.box(f"car{k}c", (1.8, 2.2, 0.7), (x, y - 0.1, 1.3), m, bevel=0.2)
    # lamp posts out at the car park's edge
    for k, (x, y) in enumerate([(-14, -4), (14, -4), (-14, 20), (14, 20), (0, 28)]):
        kit.cyl(f"post{k}", 0.08, 7.0, (x, y, 3.5), M["dark"], n=8)
        kit.sphere(f"postglow{k}", 0.3, (x, y, 7.1), M["postglow"], seg=10)


def build_vignettes(kit, ctx, M):
    """The three small montage sets and the office, each far from the market with its own light."""
    # the picnic table at the market's edge
    px, py = 9.0, 6.0
    kit.box("pic.top", (1.8, 0.8, 0.05), (px, py, 0.76), M["wood_top"])
    for e in (-0.8, 0.8):
        kit.box(f"pic.leg{e}", (0.08, 0.7, 0.74), (px + e, py, 0.37), M["wood"])
        kit.box(f"pic.bench{e}", (0.28, 0.34, 0.05), (px + e, py - 1.0, 0.47), M["wood"])
    kit.box("pic.benchA", (1.8, 0.28, 0.05), (px, py - 1.05, 0.46), M["wood"])
    kit.box("pic.benchB", (1.8, 0.28, 0.05), (px, py + 1.05, 0.46), M["wood"])
    kit.box("pic.box", (0.1, 0.1, 0.06), (px, py - 0.35, 1.2), M["redbox"], bevel=0.01)
    kit.cyl("pic.pole", 0.035, 3.0, (px + 2.2, py + 1.2, 1.5), M["dark"], n=6)
    lantern(kit, ctx, "pic.l1", (px + 1.5, py + 1.2, 2.9), LANTERN_GLOW, 1.8, sway=0.0)
    lantern(kit, ctx, "pic.l2", (px - 1.5, py + 1.2, 2.9), LANTERN_RED, 1.8, sway=0.0)
    kit.light("pic.key", "POINT", (px, py + 0.2, 2.6), 600.0, LANTERN_GLOW, size=0.4)
    kit.light("pic.fill", "POINT", (px - 2.4, py - 2.2, 1.8), 160.0, "#9db4ff", size=0.5, shadow=False)
    # the back of a stall: a canvas wall, crates, a hanging lantern
    bx, by = -11.0, 8.0
    kit.box("back.wall", (6.0, 0.05, 2.8), (bx, by + 2.2, 1.4), M["canvas"])
    kit.box("back.wallL", (0.05, 4.4, 2.8), (bx - 3.0, by + 0.0, 1.4), M["canvas"])
    for k, (dx, dz) in enumerate([(2.2, 0.0), (2.2, 0.4), (1.6, 0.0)]):
        kit.box(f"back.crate{k}", (0.5, 0.5, 0.4), (bx + dx, by + 1.5 - 0.1 * k, 0.2 + dz), M["wood_top"], bevel=0.02)
    kit.cyl("back.pole", 0.035, 3.0, (bx + 2.8, by + 1.2, 1.5), M["dark"], n=6)
    lantern(kit, ctx, "back.l1", (bx, by + 1.3, 2.7), LANTERN_GLOW, 1.8, sway=0.0)
    kit.light("back.key", "POINT", (bx, by - 0.4, 2.5), 600.0, LANTERN_GLOW, size=0.4)
    kit.light("back.fill", "POINT", (bx + 3.0, by - 2.4, 1.6), 160.0, "#9db4ff", size=0.5, shadow=False)
    # the home kitchen: pale walls, a lit window, a table with two steaming bowls
    kx, ky = 20.0, 22.0
    kit.plane("kit.floor", (6, 6), (kx, ky, 0.0), M["kfloor"])
    kit.box("kit.back", (6.0, 0.1, 2.7), (kx, ky + 3.0, 1.35), M["kwall"])
    kit.box("kit.left", (0.1, 6.0, 2.7), (kx - 3.0, ky, 1.35), M["kwall"])
    kit.box("kit.right", (0.1, 6.0, 2.7), (kx + 3.0, ky, 1.35), M["kwall"])
    kit.box("kit.window", (1.4, 0.04, 1.0), (kx - 1.0, ky + 2.94, 1.5), M["windowglow"])
    kit.box("kit.counter", (2.2, 0.6, 0.9), (kx + 1.5, ky + 2.6, 0.45), M["wood"])
    kit.box("kit.table", (1.0, 1.0, 0.05), (kx, ky, 0.76), M["wood_top"])
    for dx in (-0.42, 0.42):
        for dy in (-0.42, 0.42):
            kit.box(f"kit.leg{dx}{dy}", (0.06, 0.06, 0.74), (kx + dx, ky + dy, 0.37), M["wood"])
    for dx in (-0.25, 0.25):
        kit.cyl(f"kit.bowl{dx}", 0.12, 0.08, (kx + dx, ky, 0.83), M["cream"], n=16)
        kit.cyl(f"kit.soup{dx}", 0.105, 0.01, (kx + dx, ky, 0.872), M["soup"], n=16)
        ctx["steam"].append(kit.sphere(f"kit.steam{dx}", 0.07, (kx + dx, ky, 1.0), M["steam"], seg=8))
    kit.light("kit.key", "POINT", (kx, ky - 0.6, 2.3), 500.0, LANTERN_GLOW, size=0.4)
    kit.light("kit.win", "AREA", (kx - 1.0, ky + 2.8, 1.5), 150.0, "#9db4ff", size=1.0, rot=(math.radians(90), 0, 0), shadow=False)
    # the office: a plain grey desk, a blank monitor, a chair, a pale wall, a cold ceiling light
    ox, oy = -20.0, 22.0
    kit.plane("off.floor", (7, 7), (ox, oy, 0.0), M["ofloor"])
    kit.box("off.wall", (7.0, 0.1, 2.8), (ox, oy + 3.0, 1.4), M["owall"])
    kit.box("off.wallL", (0.1, 7.0, 2.8), (ox - 3.2, oy, 1.4), M["owall"])
    kit.box("off.desk", (1.6, 0.8, 0.04), (ox, oy + 0.85, 0.74), M["desk"])
    for dx in (-0.75, 0.75):
        kit.box(f"off.dl{dx}", (0.05, 0.7, 0.72), (ox + dx, oy + 0.85, 0.36), M["desk"])
    kit.box("off.mon", (0.7, 0.04, 0.42), (ox, oy + 1.05, 1.1), M["monitor"], bevel=0.01)
    kit.box("off.stand", (0.1, 0.1, 0.18), (ox, oy + 1.08, 0.86), M["monitor"])
    kit.box("off.chair", (0.5, 0.5, 0.06), (ox, oy - 0.1, 0.45), M["monitor"], bevel=0.02)
    kit.box("off.chairb", (0.5, 0.06, 0.5), (ox, oy - 0.38, 0.75), M["monitor"], bevel=0.02)
    kit.light("off.key", "AREA", (ox, oy + 0.2, 2.6), 500.0, "#dfe8f0", size=2.0, shadow=True)
    kit.light("off.fill", "POINT", (ox + 2.5, oy - 2.0, 1.6), 160.0, "#d6e0ee", size=0.5, shadow=False)


# ------------------------------------------------------------------------------------------------ the Half
def half_head(kit, name, mat, cap_mat, parent):
    """The x >= 0 half of rig.py's rounded-cylinder head (the same UVs), with one flat cap in the plane x = 0."""
    R, H, b = faces.HEAD_R, faces.HEAD_H, 0.16
    n, arc = 48, 5
    prof = [(0.0, 0.0)]
    for k in range(arc + 1):
        a = -math.pi / 2 + (math.pi / 2) * k / arc
        prof.append((R - b + b * math.cos(a), b + b * math.sin(a)))
    for k in range(arc + 1):
        a = (math.pi / 2) * k / arc
        prof.append((R - b + b * math.cos(a), H - b + b * math.sin(a)))
    prof.append((0.0, H))
    verts, uvs = [], []
    for j in range(n // 2, n + 1):
        th = 2 * math.pi * j / n
        ang = th - math.pi / 2 - math.pi
        for r, z in prof:
            verts.append((r * math.cos(ang), r * math.sin(ang), z - H / 2))
            uvs.append((j / n, min(1.0, max(0.0, (z - b * 0.5) / (H - b)))))
    m = len(prof)
    fcs = []
    for j in range(n // 2):
        for i in range(m - 1):
            a, c = j * m + i, (j + 1) * m + i
            fcs.append((a, c, c + 1, a + 1))
    ob = kit.mesh_obj(name, verts, fcs, mat, parent, smooth=True)
    uv = ob.data.uv_layers.new(name="UVMap")
    for poly in ob.data.polygons:
        for li in poly.loop_indices:
            uv.data[li].uv = uvs[ob.data.loops[li].vertex_index]
    # the cap: the outline in the plane x = 0 (front column then back column), one flat polygon
    front = [(-r, z - H / 2) for r, z in prof]       # j = n/2 column (y = -r)
    back = [(r, z - H / 2) for r, z in prof]         # j = n   column (y = +r)
    outline = front[1:] + back[::-1][:-1] if False else front + back[::-1]
    # drop the duplicate axis points (r = 0) so the polygon has no repeated vertices
    pts = [(y, z) for y, z in outline]
    clean = []
    for p in pts:
        if not clean or (abs(p[0] - clean[-1][0]) > 1e-6 or abs(p[1] - clean[-1][1]) > 1e-6):
            clean.append(p)
    if abs(clean[0][0] - clean[-1][0]) < 1e-6 and abs(clean[0][1] - clean[-1][1]) < 1e-6:
        clean.pop()
    cv = [(0.0, y, z) for y, z in clean]
    kit.mesh_obj(name + ".cap", cv, [tuple(range(len(cv)))], cap_mat, parent, loc=(-0.003, 0, 0))
    return ob


def half_face_image(path):
    W, Hh = faces.TEX_W, faces.TEX_H
    im = Image.new("RGB", (W, Hh), "#a98672")
    d = ImageDraw.Draw(im)
    cx = int(W * (0.5 + 17 / 360))
    cy = int(Hh * 0.40)
    d.ellipse([cx - 56, cy - 80, cx + 56, cy + 80], fill=(8, 7, 10))
    d.ellipse([cx - 28, cy - 56, cx - 6, cy - 34], fill=(252, 252, 255))             # the highlight: the brightest thing
    x0 = int(W * 0.5)
    pts = [(x0, int(Hh * 0.72)), (x0 + 90, int(Hh * 0.73)), (x0 + 190, int(Hh * 0.72)), (x0 + 270, int(Hh * 0.69))]
    d.line(pts, fill=(14, 10, 12), width=20, joint="curve")
    d.ellipse([pts[-1][0] - 10, pts[-1][1] - 10, pts[-1][0] + 10, pts[-1][1] + 10], fill=(14, 10, 12))
    im.save(path)


def build_half(kit, ctx, M):
    root = kit.empty("half", (0, 0, 0))
    root.scale = (S, S, S)
    jacket, trousers, lacquer = M["quilt"], M["trousers"], M["lacquer"]
    # the right-hand column (x >= 0 in its own space, facing -y): leg, torso, arm, head, hair
    kit.box("half.leg", (0.98, 1.0, 1.72), (0.5, 0, 1.14), trousers, root, bevel=0.06)
    kit.box("half.shoe", (0.99, 1.01, 0.3), (0.5, 0, 0.15), M["shoe"], root, bevel=0.06)
    kit.box("half.torso", (0.98, 1.0, 2.0), (0.5, 0, 3.0), jacket, root, bevel=0.06)
    kit.box("half.sleeve", (0.98, 1.0, 1.75), (1.5, 0, 3.125), jacket, root, bevel=0.06)
    kit.box("half.hand", (0.96, 0.98, 0.25), (1.5, 0, 2.125), M["skin"], root, bevel=0.04)
    # the cut: a slab of lacquer over the whole inner face (leg to hip, torso), one material, no edge detail
    kit.box("half.plane.lower", (0.012, 1.0, 2.0), (-0.006, 0, 1.0), lacquer, root)
    kit.box("half.plane.upper", (0.012, 1.0, 2.0), (-0.006, 0, 3.0), lacquer, root)
    neck = kit.empty("half.neck", (0, 0, 4.0), root)
    headg = kit.empty("half.headg", (0, 0, faces.HEAD_H / 2 + 0.02), neck)
    fp = WORK / "half-face.png"
    half_face_image(fp)
    hm = image_mat(kit, "half face", fp, 0.5)
    half_head(kit, "half.head", hm, lacquer, headg)
    top = faces.HEAD_H / 2
    R = faces.HEAD_R
    hair = M["hair_black"]
    kit.box("half.hcap", (R + 0.04, 2 * R + 0.08, 0.3), ((R + 0.04) / 2, 0.02, top - 0.05), hair, headg, bevel=0.08)
    kit.box("half.hback", (R + 0.04, 0.32, faces.HEAD_H * 0.75), ((R + 0.04) / 2, R - 0.08, top - faces.HEAD_H * 0.36), hair, headg, bevel=0.08)
    kit.box("half.hside", (0.2, 0.9, 0.5), (R - 0.02, 0.2, top - 0.25), hair, headg, bevel=0.06)
    ctx["half"] = root


# ------------------------------------------------------------------------------------------------ crowd
CROWD_LOOKS = [
    ("#d9a67a", "#5b6f8f", "#2a2c34", "cap", "#1c1512", "solid"),
    ("#8c5a3c", "#8a4a3a", "#34363e", "swoop", "#14100e", "plaid"),
    ("#f0c8a0", "#3d7a6a", "#2c2f3a", "long", "#4a3020", "solid"),
    ("#b07a55", "#c9a24a", "#2a2a30", "bun", "#1a1412", "solid"),
    ("#e8b98e", "#6a4a8a", "#3a3d46", "buzz", "#2a2420", "knit"),
    ("#c98f6a", "#4a4a52", "#26282e", "spiky", "#3a2a22", "solid"),
]


def crowd_spec(k):
    skin, shirt, pants, hair, hair_c, pat = CROWD_LOOKS[k % len(CROWD_LOOKS)]
    return {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pat, "pattern_c": "#2a2a30", "pants": pants,
            "shoes": "#222428", "sleeves": "long", "hair": hair, "hair_c": hair_c, "hat": "none",
            "height": 0.96 + 0.03 * (k % 4), "face": {"eyes": ["round", "dot", "tired", "lashes", "round", "button"][k % 6], "brows": True,
                                                       "ink": "#161012"}}


QUEUE_NOODLE = [(-1.5, 12.3), (-1.5, 11.45), (-0.6, 10.75), (0.5, 10.0), (0.5, 9.15), (-0.6, 8.4), (-1.5, 7.6), (-1.5, 6.75),
                (-1.5, 5.9), (-1.5, 5.05), (-1.5, 4.2), (-1.5, 3.35), (-1.5, 2.5), (-1.5, 1.65), (-1.5, 0.8), (-1.5, -0.05)]
QUEUE_OURS = [(-1.5, 9.45 - 0.85 * k) for k in range(12)]
STALL_CUSTOMERS = [("L", 0, -0.35), ("L", 0, 0.45), ("L", 1, 0.0), ("L", 5, -0.3), ("L", 5, 0.5),
                   ("R", 0, -0.4), ("R", 0, 0.45), ("R", 1, 0.0), ("R", 4, -0.35), ("R", 4, 0.4), ("R", 5, 0.0)]
ARCH_CROWD = [(0.75, 0.05, 180), (1.05, -1.25, 180), (-1.2, -2.2, 90), (2.0, -2.4, 180), (-0.2, 0.9, 0)]


def build_crowd(kit, ctx, wd):
    ctx["crowd"] = []

    def add(name, k, home, yaw, hue=0):
        ch = rig.Character(f"{name}{len(ctx['crowd'])}", crowd_spec(k), wd)
        ctx["crowd"].append({"ch": ch, "home": home, "yaw": yaw, "k": k, "tag": name})
        return ctx["crowd"][-1]

    for k in range(len(QUEUE_NOODLE)):
        m = add("qn", k, QUEUE_NOODLE[k], -90 if k == 0 else 180)
        m["queue"] = k
    for k in range(12):
        pass
    for j, (side, i, dy) in enumerate(STALL_CUSTOMERS):
        s = -1 if side == "L" else 1
        add("sc", j + 3, (s * 1.45, ROWS_Y[i] + dy), -90 * s * -1 if False else (-90 if s < 0 else 90))
        ctx["crowd"][-1]["stall"] = True
    for j, (x, y, yaw) in enumerate(ARCH_CROWD):
        add("ac", j + 1, (x, y), yaw)
        ctx["crowd"][-1]["arch"] = True


# ------------------------------------------------------------------------------------------------ build
def materials(kit):
    M = {}
    M["tarmac"] = kit.grime("#2e3034", 0.65, 0.8, name="tarmac", rough=0.32)
    M["line"] = pbr(kit, "bayline", "#c9c9c0", 0.7, 0.1)
    M["wood"] = kit.planks("#6b4a2e", "#4e3520", 1.2, "Y", name="wood", rough=0.6)
    M["wood_top"] = kit.planks("#8a6238", "#6a4a2a", 1.0, "Y", name="woodtop", rough=0.55)
    M["dark"] = pbr(kit, "darkpole", "#26262c", 0.5, 0.4)
    M["canvas"] = pbr(kit, "canvas", "#2b2b32", 0.95, 0.05)
    M["steel"] = kit.metal("#8a8d90", 0.4)
    M["iron"] = kit.metal("#2a2a2e", 0.45, name="iron")
    M["bamboo"] = pbr(kit, "bamboo", "#b58a4a", 0.6, 0.2)
    M["bamboo_d"] = pbr(kit, "bamboo d", "#8a6a36", 0.6, 0.2)
    M["board"] = pbr(kit, "choppingboard", "#c9a878", 0.7, 0.2)
    M["cream"] = pbr(kit, "cream", "#efe2c4", 0.5, 0.3)
    M["mustard"] = pbr(kit, "mustard", "#d5a32b", 0.85, 0.1)
    M["tin"] = kit.metal("#6d7077", 0.45, name="tin")
    M["lampglow"] = kit.emit(LANTERN_GLOW, 6.0, name="lampglow")
    M["postglow"] = kit.emit("#ffcf9a", 5.0, name="postglow")
    M["redbox"] = pbr(kit, "redbox", "#a02a2a", 0.5)
    M["kfloor"] = kit.planks("#a98b64", "#8d7050", 1.0, "X", name="kfloor", rough=0.5)
    M["kwall"] = pbr(kit, "kwall", "#d9cfc0", 0.8, 0.1)
    M["windowglow"] = kit.emit("#bcd2ff", 2.2, name="windowglow")
    M["soup"] = pbr(kit, "soup", "#b8742a", 0.3, 0.4)
    M["steam"] = pbr(kit, "steamp", "#e9edf2", 1.0, 0.0)
    M["ofloor"] = pbr(kit, "ofloor", "#5a5d63", 0.7, 0.2)
    M["owall"] = pbr(kit, "owall", "#b9bdc2", 0.85, 0.1)
    M["desk"] = pbr(kit, "desk", "#8c9096", 0.55, 0.3)
    M["monitor"] = pbr(kit, "monitor", "#1c1d21", 0.35, 0.5)
    # the Half
    M["quilt"] = quilt_material(kit)
    M["trousers"] = pbr(kit, "half trousers", "#1d2150", 0.8, 0.1)
    M["shoe"] = pbr(kit, "half shoe", "#16161a", 0.6, 0.2)
    M["skin"] = pbr(kit, "half skin", "#a98672", 0.5, 0.3)
    M["hair_black"] = pbr(kit, "half hair", "#0d0b0e", 0.6, 0.2)
    M["lacquer"] = kit.plastic("#262a62", 0.1, name="half lacquer", spec=0.9)
    return M


def quilt_material(kit):
    """Lantern-red quilted cloth: a diamond pillow bump, sin(u) * sin(v) with u, v on the 45 degree axes."""
    name = "half quilt"
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(LANTERN_RED)
    b.inputs["Roughness"].default_value = 0.7
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])

    def comb(op_b):
        a = nt.nodes.new("ShaderNodeMath")
        a.operation = op_b
        nt.links.new(sep.outputs["X"], a.inputs[0])
        nt.links.new(sep.outputs["Z"], a.inputs[1])
        k = nt.nodes.new("ShaderNodeMath")
        k.operation = "MULTIPLY"
        k.inputs[1].default_value = 3.2
        nt.links.new(a.outputs[0], k.inputs[0])
        s = nt.nodes.new("ShaderNodeMath")
        s.operation = "SINE"
        nt.links.new(k.outputs[0], s.inputs[0])
        return s
    u, v = comb("ADD"), comb("SUBTRACT")
    h = nt.nodes.new("ShaderNodeMath")
    h.operation = "MULTIPLY"
    nt.links.new(u.outputs[0], h.inputs[0])
    nt.links.new(v.outputs[0], h.inputs[1])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.5
    bp.inputs["Distance"].default_value = 0.05
    nt.links.new(h.outputs[0], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    kit._fogged(m, b.outputs[0])
    return m


def build_lights(kit, ctx):
    for k, y in enumerate([0.5, 3.5, 6.5, 9.5, 12.5, 15.5]):
        kit.light(f"walk{k}", "POINT", (0.0, y, 3.4), 520.0, LANTERN_GLOW, size=0.5)
    kit.light("arch", "POINT", (0.0, ARCH_Y - 0.6, 3.4), 400.0, LANTERN_GLOW, size=0.5)
    kit.light("cool", "AREA", (0.0, 8.0, 7.0), 1000.0, "#7f9cff", size=9.0, rot=(0, 0, 0), shadow=False)
    kit.light("shadowlamp", "SPOT", (0.2, 7.2, 3.4), 0.0, "#ffe2b8", spot=60, blend=0.3, size=0.03,
              rot=(0, 0, 0))
    ctx["shadowlamp"] = kit.LIGHTS["shadowlamp"]["obj"]
    kit.aim(ctx["shadowlamp"], (0.2, 7.2, 0.0))
    # the Half's lights follow the camera: a warm key from the side, a cool rim from behind it
    kit.light("half_key", "SPOT", (0, 0, 1.5), 0.0, "#ffb060", spot=34, blend=0.5, size=0.05)
    kit.light("half_rim", "SPOT", (0, 0, 1.8), 0.0, "#8fb0ff", spot=26, blend=0.5, size=0.05)


def build(kit, story, tl):
    M = materials(kit)
    ctx = {"M": M, "lanterns": [], "lantern_mats": {}, "steam": [], "coins": []}
    build_ground(kit, ctx, M)
    build_stalls(kit, ctx, M)
    build_lanterns(kit, ctx, M)
    build_arch(kit, ctx, M)
    build_vignettes(kit, ctx, M)
    build_lights(kit, ctx)
    build_half(kit, ctx, M)
    wd = WORK / "faces"
    wd.mkdir(exist_ok=True)
    build_crowd(kit, ctx, wd)
    # the coins: one for every cast member and every crowd figure, one shared coin for the end
    sun_p, moon_p = coin_images()
    cm = {"rim": coin_material(kit, "coin rim", sun_p), "sun": coin_material(kit, "coin sun", sun_p),
          "moon": coin_material(kit, "coin moon", moon_p)}
    for name in story.get("cast", {}):
        ctx["coins"].append({"name": name, "ob": build_coin(kit, f"coin.{name}", cm), "kind": "cast"})
    for j, m in enumerate(ctx["crowd"]):
        ctx["coins"].append({"name": f"crowd{j}", "ob": build_coin(kit, f"coin.crowd{j}", cm), "kind": "crowd", "m": m, "j": j})
    ctx["shared"] = build_coin(kit, "coin.shared", cm)
    ctx["wd"] = wd
    ctx["posed_crowd"] = None
    ctx["lantern_nodes"] = []
    for mat in ctx["lantern_mats"].values():
        n = mat.node_tree.nodes["Emission"]
        ctx["lantern_nodes"].append((n, n.inputs["Strength"].default_value))
    for key in ("lampglow", "postglow"):
        pass
    ctx["lamp_nodes"] = []
    for key in ("lampglow",):
        n = M[key].node_tree.nodes["Emission"]
        ctx["lamp_nodes"].append((n, n.inputs["Strength"].default_value))
    return ctx


# ------------------------------------------------------------------------------------------------ animate
def cues(tl, name):
    return sorted((c for c in tl["cues"] if c["name"] == name), key=lambda c: c["t"])


def last(cs, t):
    out = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            out = c
    return out


def mood(tl, t):
    lv = 1.0
    for c in cues(tl, "mood"):
        if c["t"] > t:
            break
        d = max(0.3, c.get("dur", 1.0))
        if t < c["t"] + d:
            return lv + (c["to"] - lv) * ss((t - c["t"]) / d)
        lv = c["to"]
    return lv


COIN_FACES = {            # [before the first flip, between the flips, after the second]
    "bea": ["moon"] * 3, "noodle": ["sun", "sun", "moon"], "ca": ["moon", "sun", "moon"], "cb": ["sun", "moon", "sun"],
    "cw": ["sun"] * 3, "co": ["sun"] * 3, "g1": ["moon"] * 3, "g2": ["moon"] * 3,
}
SHOT_COINS = {            # one shot's own faces (a different person in a different place)
    "S05": {"ca": "sun", "cb": "sun"}, "S06": {"cw": "sun", "co": "sun"}, "S07": {"g1": "moon", "g2": "moon"},
    "S09": {"ca": "sun", "cb": "sun", "g1": "sun"}, "S10": {"ca": "sun", "cb": "moon"}, "S24": {"ca": "sun"},
    "S36": {"ca": "sun", "cb": "sun"},
}
EDGE = ("me", "me_office", "me_apron")


def crowd_face(m, phase, queue):
    if queue:
        return "sun"
    h = (m["k"] * 7 + m["j"] * 13 + phase * 5) % 10
    return "moon" if h < 4 else "sun"


def face_angle(face):
    return {"sun": 0.0, "moon": math.pi, "edge": math.pi / 2}[face]


def coin_pose(kit, ctx, co, pos, face_seq, t, flips, cam, tilt_on, scale=1.0):
    """face_seq: the coin's face before the first flip, between and after (3 values). Returns nothing; poses the object."""
    ob = co
    # which phase, and is a flip running
    ang = None
    phase = 0
    for j, f in enumerate(flips):
        if t >= f["t"] + f["dur"]:
            phase = j + 1
        elif t >= f["t"]:
            a, b = face_seq[j], face_seq[j + 1]
            if a == "edge":
                ang = face_angle(a)
            else:
                delta = 2 * math.pi * 1 + (math.pi if a != b else 0.0)
                ang = face_angle(a) + delta * ss((t - f["t"]) / f["dur"])
            phase = j
            break
    if ang is None:
        ang = face_angle(face_seq[min(phase, len(face_seq) - 1)])
    dx, dy = cam.x - pos[0], cam.y - pos[1]
    yaw = math.atan2(dx, -dy)
    seed = pos[0] * 1.3 + pos[1] * 0.7
    rock = 0.07 * math.sin(0.9 * t + seed)
    tilt = (0.24 + 0.05 * math.sin(1.1 * t + seed * 1.7)) if tilt_on else 0.0
    ob.location = pos
    ob.rotation_euler = (tilt, 0, yaw + ang + rock)
    ob.scale = (scale, scale, scale)


def animate(kit, story, tl, t, ctx):
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    sid = shot["id"]
    cam = kit.OBJ["cam"]
    camp = cam.location
    M = ctx["M"]
    # ---- lights
    m = mood(tl, t)
    for n, base in ctx["lantern_nodes"] + ctx["lamp_nodes"]:
        n.inputs["Strength"].default_value = base * (0.08 + 0.92 * m)
    over = {}
    for name in list(kit.LIGHTS):
        if name.startswith("lamp") or name.startswith("walk") or name == "arch":
            over[name] = m
    over["cool"] = 0.25 + 0.55 * (1 - m) + 0.1
    # ---- one-time bits
    if not ctx.get("fitted"):
        ctx["fitted"] = True
        band = bpy.data.objects.get("noodle.headg")
        if band:
            kit.cyl("noodle.band", faces.HEAD_R + 0.04, 0.2, (0, 0, faces.HEAD_H / 2 - 0.34), kit.plastic("#2f6fa8", 0.7), band, n=28)
    # ---- lantern sway (position only)
    for ln in ctx["lanterns"]:
        h = ln["home"]
        sw = ln["sway"]
        dx = 0.035 * sw * math.sin(0.8 * t + ln["seed"])
        dy = 0.035 * sw * math.sin(0.65 * t + ln["seed"] * 1.3)
        ln["ob"].location = (h[0] + dx, h[1] + dy, h[2])
        ln["cap"].location = (h[0] + dx * 0.5, h[1] + dy * 0.5, h[2] + 0.2)
    # ---- the bell swings after the cue
    bc = last(cues(tl, "bell"), t)
    sw = 0.0
    if bc:
        u = t - bc["t"]
        sw = 0.5 * math.exp(-1.0 * u) * math.sin(2 * math.pi * 1.4 * u) if 0 <= u < 6 else 0.0
    ctx["bell"].rotation_euler = (0, sw, 0)
    # ---- our awning is lifted for the high shot over the stall
    for ob in ctx.get("our_awning", []):
        ob.hide_render = (sid == "S74")
    # ---- the steam in the kitchen drifts (position only)
    for k, st in enumerate(ctx["steam"]):
        st.location.z = 1.0 + 0.12 * ((t * 0.35 + k * 0.5) % 1.0)
    # ---- the shadow lamp (S36 only)
    sl = last(cues(tl, "shadow_light"), t)
    over["shadowlamp"] = 1.0 if (sl and sl.get("on")) else 0.0
    kit.LIGHTS["shadowlamp"]["base"] = 3800.0
    # ---- the queues
    qc = last(cues(tl, "queue"), t)
    which = qc["which"] if qc else "noodle"
    key = which
    if ctx["posed_crowd"] != key:
        ctx["posed_crowd"] = key
        for mem in ctx["crowd"]:
            ch = mem["ch"]
            if "queue" in mem:
                k = mem["queue"]
                tab = QUEUE_OURS if which == "ours" else QUEUE_NOODLE
                hide = k >= len(tab) or (which == "far" and 2 <= k <= 5)
                if which in ("noodle", "far"):
                    pos = tab[min(k, len(tab) - 1)]
                    yaw = -90 if k == 0 else 180
                else:
                    pos = tab[min(k, len(tab) - 1)]
                    yaw = -90 if k == 0 else 180
                mem["pos"] = pos
                mem["yaw"] = yaw
                mem["hidden"] = hide
            else:
                mem["pos"] = mem["home"]
                mem["hidden"] = False
            ch.pose(mem["pos"][0], mem["pos"][1], 0.0, math.radians(mem["yaw"]), 0.0, (0, 0), (0, 0), 0.0, 0.0, 0.0, 0.0,
                    "neutral", 0.0, (0, 0), 0.0, mem["hidden"])
    # ---- the Half
    hc = last(cues(tl, "half"), t)
    root = ctx["half"]
    on = bool(hc and hc.get("on"))
    for ob in [root] + list(root.children_recursive):
        ob.hide_render = not on
    hp = None
    if on:
        root.location = (hc["pos"][0], hc["pos"][1], 0.0)
        root.rotation_euler = (0, 0, math.radians(hc["yaw"]))
        hp = V((hc["pos"][0], hc["pos"][1], 1.45))
    for nm, base, gain_on in (("half_key", 120.0, 1.0), ("half_rim", 2600.0, 1.0)):
        kit.LIGHTS[nm]["base"] = base
        over[nm] = 0.0
    if on:
        to_cam = V((camp.x - hp.x, camp.y - hp.y, 0.0))
        if to_cam.length < 1e-3:
            to_cam = V((0, -1, 0))
        to_cam.normalize()
        side = V((-to_cam.y, to_cam.x, 0.0))
        # the key sits out to the side of the camera line, warm and low; the rim behind the Half, cool and high
        kt = kit.LIGHTS["half_key"]["obj"]
        kt.location = hp + side * 1.5 + to_cam * 0.3 + V((0, 0, -0.75))
        kit.aim(kt, hp)
        rm = kit.LIGHTS["half_rim"]["obj"]
        rm.location = hp - to_cam * 2.0 + side * (-0.5) + V((0, 0, 0.9))
        kit.aim(rm, hp + V((0, 0, 0.1)))
        over["half_key"] = 0.5 + 0.6 * (1 - m)
        over["half_rim"] = 1.0
    # ---- the coins
    flips = cues(tl, "flip")
    merge = last(cues(tl, "merge"), t)
    mt = merge["t"] if merge else None
    mdur = merge["dur"] if merge else 1.2
    equal = sid in story.get("equal_coins", [])
    phase_face = lambda seq: seq
    # shared coin
    sh = ctx["shared"]
    if mt is not None and t >= mt + mdur:
        mid = (-3.35, 10.1, 2.14)
        u = t - (mt + mdur)
        spin_until = 3.0
        if u < spin_until:
            ang = math.pi + 3 * math.pi * ss(u / spin_until)       # moon to sun, one slow turn and a half
        else:
            ang = 4 * math.pi
            sp = last(cues(tl, "queue"), t)
            if sp and sp.get("which") == "ours":
                ang += 2 * math.pi * 0.22 * (t - sp["t"])
        dx, dy = camp.x - mid[0], camp.y - mid[1]
        sh.hide_render = False
        for ob in sh.children_recursive:
            ob.hide_render = False
        sh.location = mid
        sh.rotation_euler = (0.24 if u >= 0 else 0.0, 0, math.atan2(dx, -dy) + ang + 0.05 * math.sin(0.9 * t))
        sh.scale = (1, 1, 1)
    else:
        sh.hide_render = True
        for ob in sh.children_recursive:
            ob.hide_render = True
    ov = SHOT_COINS.get(sid, {})
    for c in ctx["coins"]:
        ob = c["ob"]
        vis = True
        if c["kind"] == "cast":
            name = c["name"]
            st = acting.state(tl, name, t)
            vis = not st["hidden"]
            hh = story["cast"][name].get("height", 1.0)
            pos = (st["x"], st["y"], st["z"] + hh * 1.87 + 0.26)
            if name in EDGE:
                seq = ["edge"] * 3
            elif name in ov:
                seq = [ov[name]] * 3
            else:
                seq = COIN_FACES.get(name, ["sun"] * 3)
            if name == "bea" and mt is not None and t >= mt:
                u = min(1.0, (t - mt) / mdur)
                pos = (pos[0], pos[1] + (10.1 - pos[1]) * ss(u), pos[2])
                vis = vis and t < mt + mdur
            if name in EDGE and mt is not None and t >= mt:
                u = min(1.0, (t - mt) / mdur)
                pos = (pos[0], pos[1] + (10.1 - pos[1]) * ss(u), pos[2])
                vis = vis and t < mt + mdur
            scale = 1.0
            if equal:
                scale = max(0.6, min(1.4, (V(pos) - camp).length / 4.4))
            coin_pose(kit, ctx, ob, pos, seq, t, [] if (name in ov or name in EDGE) else flips, camp,
                      tilt_on=(name not in EDGE), scale=scale)
        else:
            mem = c["m"]
            vis = not mem.get("hidden", False)
            pos = (mem["pos"][0], mem["pos"][1], mem["ch"].root.scale[2] / S * 1.87 + 0.26)
            q = "queue" in mem
            seq = [crowd_face(mem | {"j": c["j"]}, p, q) for p in range(3)]
            scale = 1.0
            if equal:
                scale = max(0.6, min(1.4, (V(pos) - camp).length / 4.4))
            coin_pose(kit, ctx, ob, pos, seq, t, flips, camp, True, scale)
        ob.hide_render = not vis
        for ch in ob.children:
            ch.hide_render = not vis
    return over
