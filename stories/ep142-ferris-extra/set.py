"""ep142 "Four Got On. FIVE Got Off": a sunny park Ferris wheel, its pale sand exit platform, an iron gate and an
ice cream cart. Everything is built from kit.py's parts; the only lettering is our own: the A to E tags over the five.

World (metres): the platform top is z = 0, the camera looks along +y, the cast faces -y, screen right is +x.
The five stand in a row at y = 0 (A -2.6 ... E 2.6). The wheel's hub is at (-1.3, 8, 7.1), radius 5.2, its sixteen
round gondolas hang from the rim and stay upright. The sun is low on the screen left, so every shadow lies to the
right ... except D's, which is the clue. The shadows are drawn shapes on the boards (the characters cast no real
shadow), so each one points exactly where the story says.

Cues read here:
  tag {who}        a tag pops in over a rider, easing in over 0.15 s
  ring {on}        the mint ring behind D, easing in over 0.3 s
  turn {on}        the corner wheel icon's red dot travels once round between the on and the off cue
  gate {open, dur} the iron gate's leaf swings open
  ride             the wheel stops the mint gondola at the platform here, then the ride up begins
  hat {up, dur}    the gate man lifts his hat
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V
from PIL import Image, ImageDraw, ImageFont

from blocky import rig

HERE = Path(__file__).resolve().parent
FONT = HERE.parent.parent / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"

HX, HY, HZ, R = -1.3, 8.0, 7.1, 5.2
NG = 16
KB, KD, KM = 1, 9, 9              # bottom cabin at t = 0, D's first cabin, the mint cabin
CAB_Z0 = -1.7                      # a cabin's floor below its pivot
MINT = "#3fd6b0"
ROW_X = {"a": -2.6, "b": -1.3, "c": 0.0, "d": 1.3, "e": 2.6}
SHADOW = "#4d5a78"
CAB_COLS = ["#ff6f61", "#7ff0c8", "#ffd23f", "#b79bff"]     # coral, mint, yellow, lilac
GATE_X = 5.0
W = {}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def cue_list(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def cue_t(tl, name, default=0.0):
    c = cue_list(tl, name)
    return c[0]["t"] if c else default


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def beam(kit, name, p0, p1, t, mat, parent=None):
    a, b = V(p0), V(p1)
    d = b - a
    q = V((0, 0, 1)).rotation_difference(d.normalized())
    return kit.box(name, (t, t, d.length), tuple((a + b) / 2), mat, parent, rot=tuple(q.to_euler()))


def hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


# ------------------------------------------------------------------------------------------------ pictures
def tag_png(path, letter):
    n = 256
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([6, 6, n - 7, n - 7], 52, fill=(255, 255, 255, 255), outline=(63, 214, 176, 255), width=18)
    f = ImageFont.truetype(str(FONT), 180)
    dr.text((n / 2, n / 2 + 6), letter, font=f, fill=(10, 10, 12, 255), anchor="mm")
    im.save(path)


def img_mat(kit, name, path, strength=1.4):
    """An unlit picture plane: the PNG's colour, its alpha cutting the shape out."""
    m = kit._new(name)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    N.remove(N["Principled BSDF"])
    tc = N.new("ShaderNodeTexCoord")
    tx = N.new("ShaderNodeTexImage")
    L.new(tc.outputs["Generated"], tx.inputs["Vector"])
    tx.image = bpy.data.images.load(str(path), check_existing=False)
    tx.image.colorspace_settings.name = "sRGB"
    em = N.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    L.new(tx.outputs["Color"], em.inputs["Color"])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader")
    L.new(tx.outputs["Alpha"], mx.inputs[0])
    L.new(tr.outputs[0], mx.inputs[1])
    L.new(em.outputs[0], mx.inputs[2])
    L.new(mx.outputs[0], out.inputs["Surface"])
    return m


def annulus(kit, name, rx, rz, w, mat, loc, n=64, parent=None):
    verts, faces = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        for k in (0, 1):
            verts.append(((rx - (w if k else 0)) * math.cos(a), 0, (rz - (w if k else 0)) * math.sin(a)))
    for i in range(n):
        j = (i + 1) % n
        faces.append((i * 2, j * 2, j * 2 + 1, i * 2 + 1))
    return kit.mesh_obj(name, verts, faces, mat, parent, loc)


# ------------------------------------------------------------------------------------------------ the cones
def build_cone(kit, root, kind, col):
    """A cone in rig units, tip at the origin, standing up (+z). kind 'melt': a squat scoop with big drips; 'swirl': D's."""
    P = kit.plastic
    waffle = P("#d8a05a", 0.7, spec=0.1)
    kit.cyl(f"{root.name}.waf", 0.06, 1.5, (0, 0, 0.75), waffle, root, n=14, r2=0.52)
    kit.cyl(f"{root.name}.waf2", 0.30, 0.07, (0, 0, 0.58), P("#b9803f", 0.7), root, n=14, r2=0.33)
    kit.cyl(f"{root.name}.waf3", 0.44, 0.07, (0, 0, 1.05), P("#b9803f", 0.7), root, n=14, r2=0.46)
    if kind == "melt":
        sm = P(col, 0.35, spec=0.5)
        sc = kit.sphere(f"{root.name}.scoop", 0.62, (0, 0, 1.62), sm, root, seg=16)
        sc.scale = (1.08, 1.08, 0.7)
        kit.cyl(f"{root.name}.skirt", 0.66, 0.16, (0, 0, 1.44), sm, root, n=16, r2=0.62)
        # big bright ribbons of melt down the cone: tilted to hug its slope
        kit.box(f"{root.name}.drip1", (0.26, 0.1, 1.15), (0.0, -0.45, 0.95), sm, root, rot=(0.30, 0, 0), bevel=0.04)
        kit.sphere(f"{root.name}.drip1b", 0.15, (0.0, -0.33, 0.36), sm, root, seg=8)
        kit.box(f"{root.name}.drip2", (0.22, 0.1, 0.8), (0.4, -0.18, 1.1), sm, root, rot=(0.0, -0.30, 0.0), bevel=0.04)
        kit.box(f"{root.name}.drip3", (0.2, 0.1, 0.6), (-0.4, -0.2, 1.2), sm, root, rot=(0.0, 0.30, 0.0), bevel=0.04)
    else:
        mint = P("#7ff0c8", 0.3, spec=0.5)
        white = P("#ffffff", 0.45, spec=0.3)
        for i, (z, r, h) in enumerate([(1.6, 0.6, 0.34), (1.9, 0.5, 0.3), (2.16, 0.38, 0.26), (2.38, 0.24, 0.22)]):
            kit.cyl(f"{root.name}.sw{i}", r, h, (0, 0, z), mint, root, n=18, r2=r * 0.92)
            kit.cyl(f"{root.name}.fr{i}", r + 0.03, 0.07, (0, 0, z - h / 2 + 0.03), white, root, n=18)
        kit.sphere(f"{root.name}.swtip", 0.12, (0, 0, 2.55), mint, root, seg=10)


def build_wrist(kit, arm, name, col):
    """The melt running down the top of the forearm: a bright ribbon 3 cm proud of the arm, and a drop at the fist."""
    sm = kit.plastic(col, 0.35, spec=0.5)
    kit.box(f"{name}.wr", (0.34, 0.07, 1.25), (0, -0.52, -1.05), sm, arm, bevel=0.03)
    kit.sphere(f"{name}.wrb", 0.2, (0, -0.55, -1.72), sm, arm, seg=8)


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    work = Path(tempfile.mkdtemp(prefix="ep142-"))
    ctx = {"work": work}
    kit.FLASH_SAFE = True
    P = kit.plastic
    white = P("#ffffff", 0.45, spec=0.2)
    pale = P("#dff0ff", 0.45, spec=0.2)
    iron = P("#2b3140", 0.5, spec=0.3)
    wheel_mats = [white, pale]

    # ---- lights: a low gold sun on the screen left (shadows point +x, a little away), a soft fill from the camera side
    sun_dir = V((-0.85, -0.4, 1.0)).normalized()
    sun = kit.light("sun", "SUN", tuple(sun_dir * 60), 3.4, "#fff0d4", size=0.06)
    sun.data.angle = 0.06
    kit.aim(sun, (0, 0, 0))
    fill = kit.light("fill", "SUN", (4, -40, 30), 0.9, "#fff4e6", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    front = kit.light("front", "SUN", (-6, -30, 14), 0.5, "#fff0e0", shadow=False)
    front.data.angle = 0.4
    kit.aim(front, (0, 0, 0))

    # ---- the ground and the platform (pale sand boards, graded to about 85%)
    kit.plane("ground", (900, 900), (0, 0, -0.45), P("#5fd068", 0.9, spec=0.02))
    boards = kit.planks("#d9ccaa", "#c9bb98", 1.0, "X", "boards", 0.75)
    kit.box("platform", (17.0, 24.5, 0.45), (0, -2.3, -0.225), boards)
    edge = P("#b08a58", 0.7, spec=0.1)
    kit.box("edge.r", (0.2, 24.5, 0.5), (8.6, -2.3, -0.22), edge)
    kit.box("edge.l", (0.2, 24.5, 0.5), (-8.6, -2.3, -0.22), edge)

    # ---- the wheel: two rings 2 m apart, cabins hang between them
    wg = kit.empty("wheelgrp", (HX, HY, HZ))
    ctx["wheel"] = wg
    rimm = white
    for sy in (-1, 1):
        y = sy * 1.0
        for i in range(32):
            a0, a1 = 2 * math.pi * i / 32, 2 * math.pi * (i + 1) / 32
            beam(kit, f"rim{sy}.{i}", (R * math.sin(a0), y, -R * math.cos(a0)), (R * math.sin(a1), y, -R * math.cos(a1)), 0.16, rimm, wg)
        for i in range(16):
            a0, a1 = 2 * math.pi * i / 16, 2 * math.pi * (i + 1) / 16
            r2_ = 2.7
            beam(kit, f"inner{sy}.{i}", (r2_ * math.sin(a0), y, -r2_ * math.cos(a0)), (r2_ * math.sin(a1), y, -r2_ * math.cos(a1)), 0.1, pale, wg)
        for i in range(16):
            a = 2 * math.pi * (i + 0.5) / 16
            beam(kit, f"spoke{sy}.{i}", (0, y * 0.6, 0), (R * math.sin(a), y, -R * math.cos(a)), 0.09, wheel_mats[i % 2], wg)
    for i in range(16):
        a = 2 * math.pi * i / 16
        beam(kit, f"axle.{i}", (R * math.sin(a), -1.0, -R * math.cos(a)), (R * math.sin(a), 1.0, -R * math.cos(a)), 0.1, iron, wg)
    kit.cyl("hub", 0.6, 1.8, (0, 0, 0), P("#e8f0fa", 0.4, spec=0.3), wg, rot=(math.pi / 2, 0, 0), n=20)
    kit.cyl("hubcap", 0.3, 2.3, (0, 0, 0), P("#ff6f61", 0.4), wg, rot=(math.pi / 2, 0, 0), n=16)
    # the A-frames
    for sy in (-1, 1):
        for sx in (-1, 1):
            beam(kit, f"leg{sy}{sx}", (HX, HY + sy * 1.3, HZ), (HX + sx * 3.8, HY + sy * 2.4, -0.4), 0.26, white)
            kit.box(f"foot{sy}{sx}", (0.9, 0.9, 0.12), (HX + sx * 3.8, HY + sy * 2.4, 0.06), iron)
        beam(kit, f"tie{sy}", (HX - 3.0, HY + sy * 2.1, 1.4), (HX + 3.0, HY + sy * 2.1, 1.4), 0.14, pale)
    # the cabins: round-ish buckets from a pivot, open on the camera (-y) side
    ctx["cabs"] = []
    for k in range(NG):
        g = kit.empty(f"cab{k}", (0, 0, 0))
        cm = P(CAB_COLS[k % 4], 0.35, spec=0.4)
        cm2 = P("#ffffff", 0.4, spec=0.2)
        z0 = CAB_Z0
        annulus(kit, f"cab{k}.floor", 0.9, 0.9, 0.22, cm, (0, 0, z0 - 0.05), n=16, parent=g).rotation_euler = (math.pi / 2, 0, 0)
        for j in range(8):
            th = math.radians(45 * j)
            if j == 6:
                continue                        # the open side, toward -y (angle 270)
            ap = 0.74
            kit.box(f"cab{k}.pan{j}", (0.62, 0.07, 0.9), (ap * math.cos(th), ap * math.sin(th), z0 + 0.45), cm, g,
                    rot=(0, 0, th + math.pi / 2), bevel=0.02)
        for j in range(8):
            th = math.radians(45 * j + 22.5)
            kit.box(f"cab{k}.post{j}", (0.08, 0.08, 1.75), (0.8 * math.cos(th), 0.8 * math.sin(th), z0 + 0.875), cm2, g, bevel=0.02)
        kit.box(f"cab{k}.rail", (0.9, 0.06, 0.06), (0, -0.7, z0 + 0.78), cm2, g, bevel=0.02)
        kit.cyl(f"cab{k}.roof", 1.0, 0.28, (0, 0, z0 + 1.89), cm, g, n=16, r2=0.45)
        kit.cyl(f"cab{k}.rod", 0.05, 0.3, (0, 0, z0 + 2.17), iron, g, n=8)
        kit.box(f"cab{k}.bench", (1.0, 0.4, 0.1), (0, 0.45, z0 + 0.42), cm2, g, bevel=0.02)
        ctx["cabs"].append(g)

    # ---- the fake shadows: the cast casts no real shadow; each one is a shape on the boards
    shm = P(SHADOW, 0.95, spec=0.0)
    cast = story["cast"]
    shadow_spec = [("a", 0.85, 0.4, 1.55), ("b", 0.85, 0.4, 1.55), ("c", 0.85, 0.4, 1.55), ("e", 0.85, 0.4, 1.55),
                   ("d", -0.9, -0.25, 2.1), ("man", 0.85, 0.4, 1.4)]
    for k, dx, dy, ctop in shadow_spec:
        h = cast[k].get("height", 1.0)
        cx, cy = (ROW_X[k], 0.0) if k in ROW_X else (5.75, -1.3)
        parts = [(-0.3, 0.3, -0.12, 0.12, 0.0, 0.78 * h), (-0.36, 0.36, -0.15, 0.15, 0.78 * h, 1.42 * h),
                 (-0.22, 0.22, -0.2, 0.2, 1.42 * h, 1.85 * h)]
        if k in ROW_X:
            parts.append((0.27, 0.75, -0.62, -0.2, 0.9 * h, ctop * h))
        pts = []
        for x0, x1, y0, y1, z0_, z1_ in parts:
            ph = []
            for x in (x0, x1):
                for y in (y0, y1):
                    for z in (z0_, z1_):
                        ph.append((round(cx + x + dx * z, 4), round(cy + y + dy * z, 4)))
            pts += [hull(ph)]
        for i, poly in enumerate(pts):
            if len(poly) >= 3:
                kit.mesh_obj(f"shadow.{k}.{i}", [(p[0], p[1], 0.012) for p in poly], [tuple(range(len(poly)))], shm)

    # ---- the iron gate and fence (screen right), the gate man's spot is just beyond it
    for y in (-2.2, -0.4):
        kit.box(f"gpost{y}", (0.2, 0.2, 1.5), (GATE_X, y, 0.75), iron, bevel=0.03)
        kit.sphere(f"gball{y}", 0.14, (GATE_X, y, 1.6), iron, seg=8)
    for y0, y1, nm in ((-9.0, -2.3, "f1"), (-0.3, 6.0, "f2")):
        n = int((y1 - y0) / 0.32)
        kit.box(f"{nm}.top", (0.07, y1 - y0, 0.07), (GATE_X, (y0 + y1) / 2, 1.1), iron)
        kit.box(f"{nm}.bot", (0.07, y1 - y0, 0.07), (GATE_X, (y0 + y1) / 2, 0.25), iron)
        for i in range(n + 1):
            yy = y0 + (y1 - y0) * i / n
            kit.box(f"{nm}.bar{i}", (0.05, 0.05, 1.1), (GATE_X, yy, 0.62), iron)
    leaf = kit.empty("gateleaf", (GATE_X, -0.4, 0))
    ctx["leaf"] = leaf
    kit.box("leaf.top", (0.07, 1.7, 0.07), (0, -0.9, 1.1), iron, leaf)
    kit.box("leaf.bot", (0.07, 1.7, 0.07), (0, -0.9, 0.25), iron, leaf)
    for i in range(6):
        kit.box(f"leaf.bar{i}", (0.05, 0.05, 1.1), (0, -0.2 - i * 0.3, 0.62), iron, leaf)
    kit.box("leaf.diag", (0.05, 0.05, 1.9), (0, -0.9, 0.68), iron, leaf, rot=(math.atan2(1.7, 0.85) - math.pi / 2 + math.pi / 2 - 1.1 * 0 + 0.0, 0, 0))

    # ---- the ice cream cart at the platform's end (plain stripes, no words)
    cx0, cy0 = -6.2, -0.5
    pink, cream = P("#ff8fb0", 0.5, spec=0.2), P("#fff6e4", 0.5, spec=0.2)
    kit.box("cart.body", (2.4, 1.2, 0.95), (cx0, cy0, 0.475), cream, bevel=0.03)
    for i in range(8):
        kit.box(f"cart.s{i}", (0.15, 0.02, 0.95), (cx0 - 1.05 + i * 0.3, cy0 - 0.61, 0.475), pink)
    kit.box("cart.top", (2.5, 1.3, 0.08), (cx0, cy0, 0.99), P("#e8b66a", 0.5, spec=0.2), bevel=0.02)
    for sx in (-1, 1):
        kit.cyl(f"cart.wheel{sx}", 0.3, 0.1, (cx0 + sx * 0.8, cy0 - 0.66, 0.3), iron, rot=(math.pi / 2, 0, 0), n=14)
        kit.box(f"cart.pole{sx}", (0.08, 0.08, 1.4), (cx0 + sx * 1.15, cy0 - 0.55, 1.7), iron)
        kit.box(f"cart.polb{sx}", (0.08, 0.08, 1.4), (cx0 + sx * 1.15, cy0 + 0.55, 1.7), iron)
    kit.box("cart.awn", (2.9, 1.9, 0.07), (cx0, cy0 + 0.0, 2.45), cream, rot=(-0.12, 0, 0))
    for i in range(9):
        kit.box(f"cart.a{i}", (0.16, 1.9, 0.02), (cx0 - 1.24 + i * 0.31, cy0 + 0.0, 2.5), pink, rot=(-0.12, 0, 0))
    for i in range(9):
        kit.box(f"cart.v{i}", (0.16, 0.05, 0.3), (cx0 - 1.24 + i * 0.31, cy0 - 0.95, 2.26 + 0.0), pink if i % 2 == 0 else cream)
    sunc = P("#ffd23f", 0.4, spec=0.3)
    kit.cyl("cart.sunplate", 0.34, 0.03, (cx0, cy0 - 0.99, 2.27), cream, rot=(math.pi / 2, 0, 0), n=20)
    kit.cyl("cart.sun", 0.2, 0.03, (cx0, cy0 - 1.01, 2.27), sunc, rot=(math.pi / 2, 0, 0), n=20)
    for j in range(8):
        th = math.radians(45 * j)
        kit.box(f"cart.ray{j}", (0.07, 0.03, 0.12), (cx0 + 0.28 * math.cos(th), cy0 - 1.01, 2.27 + 0.28 * math.sin(th)),
                sunc, rot=(0, -th + math.pi / 2, 0))
    kit.box("cart.holder", (1.2, 0.34, 0.12), (cx0 + 0.2, cy0 - 0.62, 1.08), P("#8a5a2e", 0.6), bevel=0.02)
    cols = ["#ff6fa8", "#ffa23a", "#4f7bff", "#ffe14a"]
    for i, c in enumerate(cols):
        r_ = kit.empty(f"cart.cone{i}", (cx0 - 0.25 + i * 0.3, cy0 - 0.62, 1.14))
        r_.scale = (0.3, 0.3, 0.3)
        build_cone(kit, r_, "melt" if i != 99 else "swirl", c)

    # ---- trees and bushes round the park, so no shot sees a void
    for i, (x, y, nm, h) in enumerate([(-24, 22, "commontree_1", 7.0), (-16, 26, "birchtree_1", 8.5), (-9, 24, "commontree_2", 7.5),
                                       (-2, 28, "willow_1", 7.0), (7, 25, "birchtree_1", 8.0), (15, 27, "commontree_1", 7.5),
                                       (23, 23, "commontree_2", 8.0), (-30, 12, "commontree_2", 7.5), (30, 14, "birchtree_1", 8.5),
                                       (-12, 14, "bush_1", 2.0), (13, 15, "bush_2", 2.2), (-17, 6, "commontree_1", 6.5),
                                       (18, 4, "commontree_2", 6.5), (-14, -12, "birchtree_1", 8.0), (15, -14, "commontree_1", 7.0),
                                       (-22, -22, "commontree_2", 8.0), (24, -20, "birchtree_1", 8.5), (2, -30, "commontree_1", 8.0),
                                       (-8, 17, "bush_2", 2.0), (9, 18, "bush_1", 2.1)]):
        kit.prop(nm, (x, y, -0.45), rot=(i * 47) % 360, height=h)
    cl = P("#ffffff", 0.9, spec=0.0)
    for i, (x, z, sc) in enumerate([(-30, 30, 1.0), (20, 38, 1.3), (-8, 44, 0.9), (40, 24, 0.8)]):
        for j, (dx_, dz_, rr) in enumerate([(0, 0, 4), (4, 0.5, 3.2), (-4, 0.3, 3.0), (1.5, 1.8, 3.0)]):
            s = kit.sphere(f"cloud{i}.{j}", rr * sc, (x + dx_ * sc, 90, z + dz_ * sc), cl, seg=10)
            s.scale = (1.4, 0.7, 0.6)

    # ---- tags over the heads
    ctx["tags"] = {}
    for L_ in "ABCDE":
        p = work / f"tag{L_}.png"
        tag_png(p, L_)
        m = img_mat(kit, f"tag {L_}", p, 1.4)
        x = ROW_X[L_.lower()]
        t = kit.plane(f"tag{L_}", (0.8, 0.8), (x, 0.0, 2.55), m, rot=(math.pi / 2, 0, 0))
        t.hide_render = True
        noshadow(t)
        ctx["tags"][L_] = t
    # ---- the mint ring behind D
    ring = annulus(kit, "ring", 0.85, 1.2, 0.1, kit.emit(MINT, 2.6, name="ring"), (ROW_X["d"], 0.5, 1.0))
    ring.hide_render = True
    noshadow(ring)
    ctx["ring"] = ring
    build_icon(kit, ctx)
    ctx["inited"] = False
    return ctx


def build_icon(kit, ctx):
    """The corner meter: a navy plate with a white eight-spoke wheel and one red gondola dot that travels once round."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    edge = kit.emit("#ffffff", 0.9, "ic_edge")
    plate = kit.emit("#1d3a66", 0.8, "ic_plate")
    wh = kit.emit("#ffffff", 1.0, "ic_white")
    red = kit.emit("#ff3b30", 1.0, "ic_red")

    def b(name, size, loc, mat, rot=(0, 0, 0)):
        ob = kit.box(name, size, loc, mat, root, rot=rot)
        noshadow(ob)
        return ob
    b("ic.edge", (1.06, 1.06, 0.004), (0, 0, 0.0), edge)
    b("ic.plate", (1.0, 1.0, 0.004), (0, 0, 0.004), plate)
    ring = annulus(kit, "ic.ring", 0.36, 0.36, 0.07, wh, (0, 0, 0.008), n=40, parent=root)
    ring.rotation_euler = (math.pi / 2, 0, 0)
    ring.location = (0, 0, 0.008)
    noshadow(ring)
    for i in range(4):
        th = i * math.pi / 4
        b(f"ic.sp{i}", (0.7, 0.04, 0.004), (0, 0, 0.012), wh, rot=(0, 0, th))
    b("ic.hub", (0.12, 0.12, 0.004), (0, 0, 0.016), wh)
    # little gondola blocks at the eight rim points
    for i in range(8):
        th = i * math.pi / 4
        b(f"ic.g{i}", (0.07, 0.07, 0.004), (0.36 * math.cos(th), 0.36 * math.sin(th), 0.016), wh)
    dot = kit.cyl("ic.dot", 0.085, 0.006, (0, -0.36, 0.024), red, root, rot=(0, 0, 0), n=16)
    noshadow(dot)
    ctx["dot"] = dot
    ctx["icon"] = root


# ------------------------------------------------------------------------------------------------ animate
def wheel_angle(tl, t):
    tr = cue_t(tl, "ride", 26.0)
    rate = 180.0 / tr
    if t <= tr:
        return rate * t
    tau = t - tr
    G = tau ** 3 - tau ** 4 / 2 if tau <= 1 else 0.5 + (tau - 1)
    return 180.0 + rate * tau + 48.0 * G


def cab_pos(k, a):
    psi = math.radians((k - KB) * 22.5 + a)
    return (HX + R * math.sin(psi), HY, HZ - R * math.cos(psi))


def first_frame(kit, story, ctx):
    ctx["inited"] = True
    flav = {"a": "#ff6fa8", "b": "#ffa23a", "c": "#4f7bff", "e": "#ffe14a"}
    ctx["cones"] = {}
    for k in "abcde":
        ch = rig.CHARS.get(k)
        if ch is None:
            continue
        arm = ch.P["arm1"]
        root = kit.empty(f"{k}.cone", (0, 0, -1.55), arm)
        root.scale = (1.2, 1.2, 1.2)
        build_cone(kit, root, "swirl" if k == "d" else "melt", flav.get(k, "#ffffff"))
        if k != "d":
            build_wrist(kit, arm, f"{k}.cone", flav[k])
        ctx["cones"][k] = (root, arm)
    for ch in rig.CHARS.values():
        noshadow(ch.root)
    ctx["hat"] = []
    for part in ("brim", "crown", "band"):
        ob = bpy.data.objects.get(f"man.{part}")
        if ob is not None:
            ctx["hat"].append((ob, V(ob.location)))


def animate(kit, story, tl, t, ctx):
    if not ctx.get("inited"):
        first_frame(kit, story, ctx)
    a = wheel_angle(tl, t)
    ctx["wheel"].rotation_euler = (0, -math.radians(a), 0)
    for k, g in enumerate(ctx["cabs"]):
        g.location = cab_pos(k, a)
    # D sits in a cabin: in the opening gondola (S01), and in the mint one from the ride on
    d = rig.CHARS.get("d")
    t_s02 = next((s["start"] for s in tl["shots"] if s["id"] == "S02"), 2.0)
    t_ride = cue_t(tl, "ride", 26.0) - 0.3
    if d is not None and not d.root.hide_render:
        k = KD if t < t_s02 else (KM if t >= t_ride else None)
        if k is not None:
            x, y, z = cab_pos(k, a)
            d.root.location = (x, y + 0.02, z + CAB_Z0 - 0.5)
            d.root.rotation_euler = (0, 0, 0)
    # cones stay upright in the raised hand
    for k, (root, arm) in ctx["cones"].items():
        root.rotation_euler = (-arm.rotation_euler.x, 0, 0)
    # tags
    for L_, obj in ctx["tags"].items():
        cs = [c for c in cue_list(tl, "tag") if c.get("who") == L_]
        if not cs:
            obj.hide_render = True
            continue
        u = ss((t - cs[0]["t"]) / 0.15)
        shot = next((x for x in tl["shots"] if x["start"] <= t < x["end"]), tl["shots"][-1])
        obj.hide_render = u <= 0.001 or shot["id"] in set(story.get("notags", []))
        sc = 0.3 + 0.7 * u
        obj.scale = (sc, sc, sc)
    # the ring behind D: in on the cue, out on the next
    on = [c for c in cue_list(tl, "ring") if c["t"] <= t]
    rg = ctx["ring"]
    if on and on[-1].get("on"):
        u = ss((t - on[-1]["t"]) / 0.3)
    elif len(on) >= 2:
        u = 1.0 - ss((t - on[-1]["t"]) / 0.3)
    else:
        u = 0.0
    rg.hide_render = u <= 0.001
    rg.scale = (0.5 + 0.5 * u,) * 3
    # the gate
    g = [c for c in cue_list(tl, "gate") if c["t"] <= t]
    op = 0.0
    if g:
        op = ss((t - g[-1]["t"]) / g[-1].get("dur", 1.5)) * g[-1]["open"]
    ctx["leaf"].rotation_euler = (0, 0, math.radians(95) * op)
    # the hat
    hc = [c for c in cue_list(tl, "hat") if c["t"] <= t]
    up = 0.0
    if hc:
        up = hc[-1]["up"] + (0.0 if hc[-1]["up"] else 0.0)
        u = ss((t - hc[-1]["t"]) / hc[-1].get("dur", 0.4))
        prev = hc[-2]["up"] if len(hc) > 1 else 0.0
        up = prev + (hc[-1]["up"] - prev) * u
    for ob, base in ctx["hat"]:
        ob.location = (base.x + 1.3 * up, base.y - 0.15 * up, base.z + 0.95 * up)
    # the corner meter's red dot: once round between the on and off cues
    ts = cue_list(tl, "turn")
    t0 = ts[0]["t"] if ts else 8.0
    t1 = ts[1]["t"] if len(ts) > 1 else t0 + 8.0
    p = min(1.0, max(0.0, (t - t0) / max(0.1, t1 - t0)))
    ang = -math.pi / 2 - p * 2 * math.pi
    ctx["dot"].location = (0.36 * math.cos(ang), 0.36 * math.sin(ang), 0.024)
    return {}
