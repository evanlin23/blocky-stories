"""Ferry crossing (ep52): a small car ferry between a grey harbour town and an island, late autumn. Built from kit.py's
parts. There is no text anywhere in the set.

Zones (metres, all with the floor at z = 0 unless said, water at z = -0.35 everywhere):
  TOWN   (0, 0)      the town slipway: concrete ramp y -15 .. 6, ticket hut, bollards, lamps, houses at y = 24, the ferry's
                     bow and ramp at y = -16 (docked), the island hill far off at y = -100
  STREET (150, 0)    a harbour street with a bin at (150, 6.5)
  FLAT   (200, 0)    my flat: a room x 197.5 .. 202.5, y -2.5 .. 2.5, window in the -y wall
  ISLAND (300, 0)    stone slipway y -12 .. 0, the lane x 298.2 .. 301.8 up to y = 34, Gran's cottage x 295 .. 305,
                     y 35 .. 47 (door at x = 300, hall to y = 43.3, the back room beyond), a blue door at (309, -3)
  KITCHEN(400, 0)    Gran's kitchen (the phone calls look into it from -y)
  DOOR   (500, 0)    a town doorstep under a lamp
  BEDJ   (600, 0)    the jumper man's bedroom
  HUT    (700, 0)    the ticket hut inside
  KITE   (800, 0)    the kite woman's house and gate
  BEACH  (900, 0)    grey sand
  FERRY  (1000, 0)   the ferry on open water, bow toward -y. Car deck z = 0.9, lounge floor z = 3.9, the window bench on
                     the +x wall: seats at y = 3.25 (right, Gran) and y = 4.75 (left, mine), seat top z = 4.4

THE SHRUG (the creature) is one model built once, posed by the "shrug" cues: shoulder height u (0 normal, 1 high), head
yaw, a sideways lean, a slide toward Gran. It only sits. Every change of place is across a cut or slow (2 s or more).
All lights are steady; the only light changes are slow ramps (time of day, the phone screen, a sunbeam).
"""

from __future__ import annotations

import math
import random
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import acting as ac
from blocky import faces, rig

S = rig.S
FOGC = "#b4babd"
TOWN = (0.0, 0.0)
ISL = 300.0
FER = 1000.0
SEAT_TOP = 4.4
SEAT_Y = {"gran": 3.25, "me": 4.75}
BENCH_X = 1.7

TOD = {
    "day":    dict(sun=2.4, sunc="#f4f1ea", fill=1.5, fillc="#c9d4de", sky=1.25, hor="#c4ccd0", zen="#a9b6bf", fogd=0.006, fogb=1.0),
    "sunny":  dict(sun=4.0, sunc="#ffe3b4", fill=1.4, fillc="#c9d4de", sky=1.3, hor="#d3d6d0", zen="#9db8d4", fogd=0.008, fogb=1.0),
    "dusk1":  dict(sun=0.9, sunc="#9fb4e0", fill=1.1, fillc="#8ea0d0", sky=0.7, hor="#7f90b4", zen="#3c4c7a", fogd=0.012, fogb=0.55),
    "dusk2":  dict(sun=0.6, sunc="#8a9fd2", fill=0.9, fillc="#7587c0", sky=0.5, hor="#53638c", zen="#243256", fogd=0.013, fogb=0.35),
    "dusk3":  dict(sun=0.8, sunc="#7e92c8", fill=1.2, fillc="#7588c2", sky=0.45, hor="#3a4870", zen="#18223f", fogd=0.014, fogb=0.24),
    "night":  dict(sun=1.1, sunc="#8ea4dc", fill=1.6, fillc="#7f94cc", sky=0.5, hor="#202b4a", zen="#0b1226", fogd=0.014, fogb=0.14),
}
SUN_DIR = V((0.55, 0.45, 0.7)).normalized()
FILL_DIR = V((-0.6, -0.4, 0.5)).normalized()


# ------------------------------------------------------------------------------------------------ helpers
def _cues(tl, name):
    return sorted((c for c in tl.get("cues", []) if c["name"] == name), key=lambda c: c["t"])


def _last(cs, t):
    cs = [c for c in cs if c["t"] <= t + 1e-9]
    return cs[-1] if cs else None


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _eased(cs, key, t, default):
    level = prev = default
    for c in cs:
        if c["t"] > t + 1e-9 or key not in c:
            continue
        prev, level = level, c[key]
        d = float(c.get("dur", 0.0))
        if d > 0 and t < c["t"] + d and isinstance(level, (int, float)) and isinstance(prev, (int, float)):
            level = prev + (level - prev) * _ss((t - c["t"]) / d)
    return level


def _show(objs, on):
    for o in objs:
        for oo in [o] + list(o.children_recursive):
            oo.hide_render = not on


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _lin(c):
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def _mixc(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


def rod(kit, name, p0, p1, r, mat, parent=None, n=8):
    a, b = V(p0), V(p1)
    d = b - a
    ob = kit.cyl(name, r, d.length, tuple((a + b) / 2), mat, parent, n=n)
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return ob


def torus(kit, name, R, r, loc, mat, parent=None, rot=(0, 0, 0), n=24, m=6, scale=(1, 1, 1)):
    verts, fcs = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        for j in range(m):
            b = 2 * math.pi * j / m
            rr = R + r * math.cos(b)
            verts.append((rr * math.cos(a), rr * math.sin(a), r * math.sin(b)))
    for i in range(n):
        for j in range(m):
            i2, j2 = (i + 1) % n, (j + 1) % m
            fcs.append((i * m + j, i2 * m + j, i2 * m + j2, i * m + j2))
    ob = kit.mesh_obj(name, verts, fcs, mat, parent, loc, rot, smooth=True)
    ob.scale = scale
    return ob


def pbr(kit, name, hexc, rough=0.6, metal=0.0, spec=0.4, alpha=None):
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = spec
            break
    if alpha is not None:
        b.inputs["Alpha"].default_value = alpha
    m.diffuse_color = kit.col(hexc)
    kit._fogged(m, b.outputs[0])
    return m


def materials(kit):
    P, M = kit.plastic, {}
    M["concrete"] = kit.concrete("#a7a39b", 1.2, 0.4)
    M["quay"] = kit.concrete("#97958e", 0.9, 0.35)
    M["road"] = kit.grime("#55575a", 0.7, 2.0)
    M["stone"] = kit.concrete("#7b7a70", 2.2, 0.5)
    M["wall"] = kit.bricks("#7d7b72", "#6b6a62", "#4c4b45", 1.6, name="dry stone", rough=0.95, row=0.22, width=0.5)
    M["brick"] = kit.bricks("#8a5a48", "#74493a", "#4f4a45", 1.0, name="town brick")
    M["grass"] = kit.grime("#566246", 0.7, 2.5)
    M["sand"] = kit.grime("#9a9588", 0.8, 2.0)
    M["water"] = pbr(kit, "sea", "#5d6b73", 0.18, spec=0.6)
    M["hull"] = P("#e8e6df", 0.55, "hull white")
    M["rust"] = P("#8a4b2e", 0.8, "rust")
    M["rustdark"] = P("#6e3b25", 0.85, "rust dark")
    M["hut"] = P("#8a3f2a", 0.8, "hut red")
    M["slate"] = P("#3b4046", 0.7, "slate roof")
    M["iron"] = pbr(kit, "iron", "#2f3034", 0.45, metal=0.8)
    M["steel"] = pbr(kit, "steel", "#9aa2a6", 0.4, metal=0.85)
    M["teal"] = P("#3f6f7a", 0.5, "teal vinyl")
    M["tealdk"] = P("#2c525b", 0.55, "teal dark")
    M["cream"] = P("#d9d2bf", 0.8, "cream")
    M["white"] = P("#e6e2d8", 0.8, "white wall")
    M["floor"] = P("#4b4f52", 0.7, "lounge floor")
    M["deck"] = kit.concrete("#5a5d5e", 1.5, 0.5, "car deck")
    M["wood"] = kit.planks("#8a6a47", "#6a4d33", 1.0, "X", "wood floor")
    M["wood2"] = kit.planks("#6a4d33", "#4e3822", 1.2, "Z", "dark planks")
    M["shelf"] = P("#7a5a3a", 0.8, "shelf")
    M["green"] = P("#2f6a40", 0.55, "cottage green")
    M["blue"] = P("#2f5f9a", 0.5, "island blue")
    M["coir"] = P("#8a6f45", 1.0, "coir")
    M["plum"] = P("#5e3550", 0.8, "plum")
    M["heather"] = P("#8a6f9a", 0.8, "heather")
    M["quilt"] = P("#9b8aa8", 0.9, "quilt")
    M["hook"] = pbr(kit, "hook", "#6f7478", 0.4, metal=0.8)
    M["peg"] = P("#8d7a5e", 0.9, "pegboard")
    M["mustard"] = P("#d9a531", 0.7, "mustard")
    M["navy"] = P("#2a3550", 0.7, "navy")
    M["grey"] = P("#8a8f94", 0.8, "grey")
    M["black"] = P("#101114", 0.6, "black")
    M["horn"] = P("#d8cdb0", 0.5, "horn")
    M["hat1"] = P("#3f8f8a", 0.9, "hat teal")
    M["hat2"] = P("#efe6cf", 0.9, "hat cream")
    M["lamp"] = kit.emit("#ffd9a0", 6.0, "lamp glow")
    M["strip"] = kit.emit("#eef2f0", 0.9, "fluorescent")
    M["port"] = kit.emit("#ffcf90", 3.5, "port glow")
    M["screen"] = kit.emit("#bcd6ff", 1.0, "screen")
    M["far"] = kit.emit("#ffcf8a", 4.0, "far lights")
    M["wake"] = kit.emit("#aebbc2", 0.6, "wake")
    M["dot"] = P("#5d6468", 0.5, "hop dot")
    M["web"] = P("#c8c8c4", 0.9, "cobweb")
    M["dust"] = P("#b7a98a", 0.95, "dust")
    M["hill"] = kit.grime("#4f5a48", 0.6, 0.15)
    M["car1"] = P("#566b86", 0.45, "car blue")
    M["car2"] = P("#a8895a", 0.45, "car ochre")
    M["tyre"] = P("#141414", 0.9, "tyre")
    M["bin"] = P("#4d5a52", 0.6, "bin")
    M["bike"] = P("#3a6fb0", 0.4, "bike blue")
    M["glass"] = pbr(kit, "window glass", "#1b2430", 0.1, spec=0.8)
    M["smudge"] = pbr(kit, "smudge", "#e0782c", 0.5, alpha=0.32)
    return M


# ------------------------------------------------------------------------------------------------ small things
def glove(kit, name, mat, parent=None, hole=False, scale=1.0):
    g = kit.empty(name, (0, 0, 0), parent)
    kit.box(f"{name}.palm", (0.13, 0.05, 0.14), (0, 0, 0), mat, g, bevel=0.012)
    for k, (x, l) in enumerate(((-0.048, 0.12), (-0.016, 0.145), (0.016, 0.14), (0.048, 0.11))):
        kit.box(f"{name}.f{k}", (0.03, 0.045, l), (x, 0, 0.07 + l / 2 - 0.01), mat, g, bevel=0.01)
    th = kit.box(f"{name}.th", (0.035, 0.045, 0.085), (0.086, 0, 0.03), mat, g, rot=(0, -0.5, 0), bevel=0.01)
    if hole:
        kit.box(f"{name}.hole", (0.026, 0.049, 0.026), (0.099, 0, 0.05), kit.plastic("#2a1a08", 0.9, "glove hole"), g)
    g.scale = (scale, scale, scale)
    return g


def hat_stripes(kit, M, name, parent=None):
    g = kit.empty(name, (0, 0, 0), parent)
    for k in range(5):
        kit.box(f"{name}.s{k}", (0.26 - 0.014 * k, 0.26 - 0.014 * k, 0.05), (0, 0, 0.025 + 0.05 * k),
                M["hat1" if k % 2 == 0 else "hat2"], g, bevel=0.012)
    kit.sphere(f"{name}.bob", 0.04, (0, 0, 0.29), M["hat2"], g, seg=10)
    return g


def make_hopper(kit, M, name, kind, colour):
    mat = kit.plastic(colour, 0.6, f"hop {colour}")
    g = kit.empty(name, (0, 0, -50))
    if kind == "glove":
        glove(kit, f"{name}.g", mat, g, scale=1.8).rotation_euler = (math.radians(90), 0, 0)
    elif kind == "umbrella":
        kit.cyl(f"{name}.shaft", 0.032, 0.8, (0, 0, 0.4), kit.plastic("#16171b", 0.6, "umb"), g, n=10, r2=0.05)
        kit.box(f"{name}.crook", (0.12, 0.035, 0.035), (0.06, 0, 0.03), kit.plastic("#2a1d15", 0.5, "umbh"), g, bevel=0.01)
        kit.sphere(f"{name}.tip", 0.034, (0, 0, 0.8), kit.plastic("#16171b", 0.6, "umb"), g, seg=8)
    elif kind == "sock":
        kit.box(f"{name}.leg", (0.1, 0.07, 0.24), (0, 0, 0.12), mat, g, bevel=0.02)
        kit.box(f"{name}.foot", (0.1, 0.19, 0.08), (0, -0.07, 0.04), mat, g, bevel=0.02)
        kit.box(f"{name}.band", (0.104, 0.074, 0.04), (0, 0, 0.22), kit.plastic("#e8e0cf", 0.7, "sockb"), g, bevel=0.01)
    elif kind == "keys":
        torus(kit, f"{name}.ring", 0.07, 0.012, (0, 0, 0.1), kit.metal("#9aa2a6", 0.35), g, rot=(math.radians(90), 0, 0))
        for k in range(3):
            kit.box(f"{name}.k{k}", (0.03, 0.01, 0.12), (-0.04 + 0.04 * k, 0, 0.03), kit.metal("#b0a46a", 0.35), g, bevel=0.004)
    elif kind == "scarf":
        kit.box(f"{name}.sc", (0.12, 0.05, 0.5), (0, 0, 0.25), mat, g, bevel=0.015)
        kit.box(f"{name}.sc2", (0.12, 0.3, 0.05), (0, 0.12, 0.03), mat, g, bevel=0.015)
    return g


def round_glasses(kit, M, name, parent, R):
    g = kit.empty(name, (0, 0, 0), parent)
    fm = kit.plastic("#5a3a20", 0.5, "brown frame")
    for sx in (-1, 1):
        torus(kit, f"{name}.r{sx}", 0.2, 0.026, (sx * 0.26, -R - 0.04, -0.02), fm, g, rot=(math.radians(90), 0, 0), n=20, m=5)
    kit.box(f"{name}.br", (0.14, 0.04, 0.04), (0, -R - 0.04, 0.0), fm, g)
    for sx in (-1, 1):
        kit.box(f"{name}.arm{sx}", (0.03, 0.9, 0.04), (sx * 0.5, -R + 0.38, 0.0), fm, g)
    return g


def make_glasses_prop(kit, M, name):
    g = kit.empty(name, (0, 0, -50))
    fm = kit.plastic("#5a3a20", 0.5, "brown frame")
    for sx in (-1, 1):
        torus(kit, f"{name}.r{sx}", 0.05, 0.007, (sx * 0.065, 0, 0.0), fm, g, n=18, m=5)
    kit.box(f"{name}.br", (0.03, 0.01, 0.01), (0, 0, 0), fm, g)
    for sx in (-1, 1):
        kit.box(f"{name}.a{sx}", (0.008, 0.12, 0.01), (sx * 0.12, 0.06, 0), fm, g)
    return g


# ------------------------------------------------------------------------------------------------ the Shrug
def shrug_face(path):
    from PIL import Image, ImageDraw
    W, H = faces.TEX_W, faces.TEX_H
    im = Image.new("RGB", (W, H), (184, 146, 90))
    d = ImageDraw.Draw(im)
    cx = W // 2
    ink = (14, 10, 8)
    s = faces.FX1 - faces.FX0

    def deg(a):
        return W * a / 360.0
    ey = faces._fy(0.42)
    for side in (-1, 1):
        x = cx + side * deg(34)
        d.ellipse([x - 46, ey - 50, x + 46, ey + 50], fill=ink)
        d.ellipse([x - 22, ey - 30, x - 4, ey - 12], fill=(250, 244, 226))
    my = faces._fy(0.72)
    th = max(16, int(0.06 * s))
    half = deg(66)
    d.line([(cx - half, my), (cx + half, my)], fill=ink, width=th)
    im.save(path)


def build_shrug(kit, M, ctx):
    orange = kit.plastic("#f0762a", 0.62, "shrug orange")
    orange2 = kit.plastic("#d9631c", 0.7, "shrug orange dark")
    cream = kit.plastic("#efe3c4", 0.7, "shrug cream")
    root = kit.empty("shrug", (0, 0, -60))
    root.scale = (S * 1.22, S * 1.22, S * 1.22)   # taller than the cast
    hips = kit.empty("shrug.hips", (0, 0, 2.0), root)
    ctx["shrug"] = {"root": root, "hips": hips}
    legs = []
    for sx in (-1, 1):
        leg = kit.empty(f"shrug.leg{sx}", (sx * 0.55, 0, 0), hips)
        kit.box(f"shrug.legm{sx}", (1.05, 1.1, 1.72), (0, 0, -0.86), orange2, leg, bevel=0.08)
        kit.box(f"shrug.shoe{sx}", (1.06, 1.12, 0.3), (0, 0, -1.85), kit.plastic("#2a2a2c", 0.6, "shrug boot"), leg, bevel=0.08)
        legs.append(leg)
    ctx["shrug"]["legs"] = legs
    up = kit.empty("shrug.upper", (0, 0, 0), hips)       # pivot at the hips: the lean
    ctx["shrug"]["upper"] = up
    kit.box("shrug.torso", (2.3, 1.24, 2.05), (0, 0, 1.02), orange, up, bevel=0.14)
    for z in (0.7, 1.32):
        kit.box(f"shrug.stripe{z}", (2.34, 1.28, 0.2), (0, 0, z), cream, up, bevel=0.03)
    # shoulders: humps that rise with u
    hump = {}
    arms = {}
    for sx in (-1, 1):
        h = kit.empty(f"shrug.hump{sx}", (sx * 1.22, 0, 1.6), up)
        kit.box(f"shrug.humpm{sx}", (1.05, 1.1, 1.0), (0, 0, 0), orange, h, bevel=0.2)
        hump[sx] = h
        arm = kit.empty(f"shrug.arm{sx}", (0, 0, 0.35), h)
        kit.box(f"shrug.armm{sx}", (0.98, 0.98, 2.7), (0, 0, -1.35), orange, arm, bevel=0.14)
        kit.box(f"shrug.cuff{sx}", (1.04, 1.04, 0.18), (0, 0, -1.9), cream, arm, bevel=0.03)
        kit.box(f"shrug.mitt{sx}", (1.04, 1.1, 0.95), (0, 0, -3.0), orange2, arm, bevel=0.2)
        kit.box(f"shrug.thumb{sx}", (0.4, 0.5, 0.5), (sx * 0.55, -0.15, -2.8), orange2, arm, bevel=0.1)
        arms[sx] = arm
    ctx["shrug"]["hump"], ctx["shrug"]["arm"] = hump, arms
    # head: ochre, custom face
    neck = kit.empty("shrug.neck", (0, 0, 2.0), up)
    head = kit.empty("shrug.head", (0, 0, 0), neck)
    mat, tex = rig.head_material("shrug", "#b8925a")
    d = Path(tempfile.mkdtemp(prefix="shrugface"))
    shrug_face(d / "face.png")
    img = bpy.data.images.load(str(d / "face.png"))
    img.colorspace_settings.name = "sRGB"
    tex.image = img
    headg = kit.empty("shrug.headg", (0, 0, faces.HEAD_H / 2 + 0.02), head)
    rig.head_mesh("shrug.headm", mat, headg)
    hood = kit.box("shrug.hood", (1.34, 1.3, 0.3), (0, 0.05, 0.62), orange, headg, bevel=0.12)
    collar = kit.box("shrug.collar", (1.5, 0.9, 0.5), (0, 0.15, -0.95), orange2, headg, bevel=0.16)
    ctx["shrug"].update(neck=neck, head=head, hood=hood, collar=collar, headg=headg)
    ctx["shrug_parts"] = [root]


def pose_shrug(ctx, c):
    sg = ctx["shrug"]
    hide = bool(c.get("hidden", False))
    _show([sg["root"]], not hide)
    if hide:
        return
    sx_, sy_, sz_ = c["pos"]
    sg["root"].location = (sx_, sy_, sz_)
    sg["root"].rotation_euler = (0, 0, math.radians(c.get("yaw", 90)))
    for leg in sg["legs"]:
        leg.rotation_euler = (-math.pi / 2, 0, 0)
    u = float(c.get("u", 0.0))
    lean = math.radians(float(c.get("lean", 0.0)))     # about the hips; positive leans toward world -y (toward Gran)
    sg["upper"].rotation_euler = (0, -lean, 0)
    for sx in (-1, 1):
        sg["hump"][sx].location = (sx * (1.5 - 0.35 * u), 0, 1.62 + 0.45 * u)
        sg["arm"][sx].location = (sx * (0.55 * u + 0.1), 0, 0.35)
        sg["arm"][sx].rotation_euler = (math.radians(c.get("armfwd", 0.0)), lean, 0)
    sg["neck"].location = (0, 0, 2.0 - 0.2 * u)
    sg["neck"].rotation_euler = (0, 0, math.radians(c.get("head", 0.0)))
    sg["head"].rotation_euler = (math.radians(c.get("tilt", 0.0)), 0, 0)
    sg["hood"].location = (0, 0.05, 0.62)
    sg["collar"].location = (0, 0.15, -0.95 + 0.1 * u)


# ------------------------------------------------------------------------------------------------ the dog
def build_dog(kit, M, ctx):
    fur = kit.plastic("#c8955a", 0.7, "dog fur")
    dark = kit.plastic("#5b3a22", 0.7, "dog ear")
    blk = kit.plastic("#121214", 0.5, "dog dark")
    root = kit.empty("dog", (0, 0, -50))
    kit.box("dog.body", (0.3, 0.72, 0.3), (0, 0, 0.36), fur, root, bevel=0.05)
    head = kit.empty("dog.head", (0, -0.4, 0.5), root)
    kit.box("dog.skull", (0.26, 0.26, 0.26), (0, -0.02, 0.04), fur, head, bevel=0.05)
    kit.box("dog.snout", (0.15, 0.17, 0.12), (0, -0.2, -0.02), fur, head, bevel=0.03)
    kit.box("dog.nose", (0.07, 0.03, 0.05), (0, -0.29, 0.0), blk, head, bevel=0.01)
    for sx in (-1, 1):
        kit.box(f"dog.ear{sx}", (0.06, 0.12, 0.2), (sx * 0.15, 0.04, 0.05), dark, head, rot=(0, sx * 0.3, 0), bevel=0.02)
        kit.box(f"dog.eye{sx}", (0.04, 0.02, 0.05), (sx * 0.07, -0.145, 0.08), blk, head)
    legs = []
    for i, (x, y) in enumerate(((-0.1, -0.27), (0.1, -0.27), (-0.1, 0.27), (0.1, 0.27))):
        lg = kit.empty(f"dog.leg{i}", (x, y, 0.24), root)
        kit.box(f"dog.legm{i}", (0.09, 0.09, 0.24), (0, 0, -0.12), fur, lg, bevel=0.02)
        legs.append(lg)
    kit.box("dog.tail", (0.07, 0.07, 0.3), (0, 0.4, 0.52), fur, root, rot=(0.5, 0, 0), bevel=0.02)
    lead = kit.plastic("#8a3a2a", 0.6, "dog lead")
    kit.box("dog.lead", (0.025, 1.4, 0.02), (0, 1.0, 0.04), lead, root)
    kit.box("dog.collar", (0.3, 0.07, 0.31), (0, -0.3, 0.42), lead, root, bevel=0.02)
    ctx["dog"] = {"root": root, "legs": legs}


# ------------------------------------------------------------------------------------------------ the town
def building_row(kit, M, x0, y, n, rng, base_x=0.0, flat=False):
    cols = ["#8d8f8b", "#9a9288", "#7f8a8c", "#a29a8a", "#7e7c78", "#8f8470"]
    for k in range(n):
        w = rng.uniform(5.0, 7.0)
        h = rng.uniform(6.5, 9.0)
        x = x0 + k * 6.6
        b = kit.box(f"bld{x0}_{k}", (w, 5.0, h), (x, y, h / 2), kit.plastic(rng.choice(cols), 0.9, f"bldmat{k % 6}"), None)
        kit.box(f"bldroof{x0}_{k}", (w + 0.3, 5.3, 0.3), (x, y, h + 0.1), M["slate"])
        for r in range(2):
            for c in range(2):
                kit.box(f"bldw{x0}_{k}_{r}{c}", (0.9, 0.08, 1.2), (x - w / 4 + c * w / 2, y - 2.52, 2.6 + r * 2.8),
                        M["glass"], None)


def _obj(n):
    return bpy.data.objects.get(n)


def build_bow(kit, M, x, y, tag):
    """The docked ferry's front: hull block, deck, rails and a ramp down to the slip (ramp end at (x, y))."""
    g = kit.empty(f"bow{tag}", (x, y, 0))
    kit.box(f"bow{tag}.hull", (6.8, 8.9, 2.5), (0, -7.75, -0.35), M["hull"], g, bevel=0.05)
    kit.box(f"bow{tag}.band", (6.84, 8.94, 0.7), (0, -7.75, -1.15), M["rust"], g)
    for k in range(5):
        kit.box(f"bow{tag}.streak{k}", (0.1, 0.05, 1.0 + 0.2 * (k % 3)), (-3.41 + 6.82 * (k % 2), -4.6 - 1.6 * k, 0.2), M["rustdark"], g)
    kit.box(f"bow{tag}.deck", (6.4, 8.6, 0.1), (0, -7.6, 0.9), M["deck"], g)
    for sx in (-1, 1):
        for z in (1.5, 2.0):
            rod(kit, f"bow{tag}.rail{sx}{z}", (sx * 3.2, -3.6, z), (sx * 3.2, -11.8, z), 0.035, M["steel"], g)
        for k in range(4):
            kit.box(f"bow{tag}.post{sx}{k}", (0.07, 0.07, 1.1), (sx * 3.2, -4.2 - 2.4 * k, 1.45), M["steel"], g)
    ramp = kit.box(f"bow{tag}.ramp", (4.4, 3.4, 0.14), (0, -1.6, 0.42), M["steel"], g, rot=(math.atan2(0.9, 3.3), 0, 0))
    ramp.rotation_euler = (-math.atan2(0.9, 3.3), 0, 0)
    ramp.location = (0, -1.7, 0.45)
    return g


def hop_dot_pool(kit, M, ctx, nh):
    ctx["dots"] = []
    for h in range(nh):
        row = []
        for j in range(4):
            row.append(kit.cyl(f"hopdot{h}_{j}", 0.07, 0.006, (0, 0, -50), M["dot"], n=10))
        ctx["dots"].append(row)


def build_town(kit, M, ctx):
    rng = random.Random(11)
    kit.plane("slip", (10, 21), (0, -4.5, 0.0), M["concrete"])
    kit.mesh_obj("slip.down", [(-5, -15, 0), (5, -15, 0), (5, -21, -1.0), (-5, -21, -1.0)], [(0, 3, 2, 1)], M["concrete"], smooth=False)
    for sx in (-1, 1):
        kit.plane(f"quay{sx}", (30, 21), (sx * 20, -4.5, -0.005), M["quay"])
    kit.plane("front", (90, 17), (0, 14.5, -0.004), M["quay"])
    building_row(kit, M, -30, 24, 10, rng)
    # ticket hut, window blank, facing -x
    kit.box("hut", (2.6, 2.4, 2.5), (7.0, -4.0, 1.25), M["hut"], None, bevel=0.03)
    kit.box("hut.roof", (3.0, 2.8, 0.18), (7.0, -4.0, 2.6), M["slate"])
    kit.box("hut.win", (0.06, 1.2, 0.8), (5.68, -4.0, 1.5), M["glass"])
    kit.box("hut.sill", (0.2, 1.4, 0.08), (5.62, -4.0, 1.08), M["cream"])
    kit.box("hut.door", (0.9, 0.06, 1.9), (7.0, -5.22, 0.95), M["rustdark"])
    for sx in (-1, 1):
        for y in (-1.0, -9.0):
            kit.cyl(f"bollard{sx}{y}", 0.17, 0.62, (sx * 4.7, y, 0.31), M["iron"], n=12, r2=0.14)
            kit.sphere(f"bollcap{sx}{y}", 0.15, (sx * 4.7, y, 0.62), M["iron"], seg=10)
        for y, nm in ((3.0, "a"), (-11.0, "b")):
            kit.cyl(f"lamp{sx}{nm}", 0.07, 4.2, (sx * 5.5, y, 2.1), M["iron"], n=8)
            kit.box(f"lamphead{sx}{nm}", (0.5, 0.3, 0.14), (sx * 5.3, y, 4.2), M["iron"])
            kit.box(f"lampglow{sx}{nm}", (0.34, 0.2, 0.05), (sx * 5.3, y, 4.12), M["lamp"])
            kit.light(f"town lamp {sx}{nm}", "POINT", (sx * 5.3, y, 3.8), 1.0, "#ffe2b0", size=0.3)
    # the island, far across the water
    h = kit.cyl("island.hill", 46.0, 15.0, (-6, -108, 2.0), M["hill"], n=18, r2=16.0)
    kit.box("island.cottage", (8.0, 6.0, 5.0), (-8.0, -108, 11.6), M["white"], None, bevel=0.1)
    kit.box("island.roof", (8.8, 6.8, 1.6), (-8.0, -108, 14.6), M["slate"])
    kit.box("island.door", (1.4, 0.2, 2.6), (-8.0, -111.1, 10.4), M["green"])
    kit.box("island.porchglow", (1.0, 0.4, 1.0), (-5.6, -111.4, 11.8), kit.emit("#ffcb80", 40.0, "porch glow"))
    for k in range(5):
        kit.cyl(f"island.rock{k}", 5 + 2 * k, 4 + k, (-60 + 25 * k, -120 - 4 * k, 0), M["hill"], n=10, r2=2.5)
    # the ferry's bow, docked
    build_bow(kit, M, 0.0, -15.2, "T")
    ctx["_bowT"] = True
    ctx["vis"]["bowT"] = {"objs": [_obj("bowT")], "default": True}
    ff = kit.empty("farferry", (22, -82, 0))
    kit.box("ff.hull", (9.0, 3.6, 2.0), (0, 0, 0.3), M["hull"], ff, bevel=0.1)
    kit.box("ff.band", (9.04, 3.64, 0.6), (0, 0, -0.5), M["rust"], ff)
    kit.box("ff.lounge", (5.0, 3.0, 1.6), (-1.0, 0, 2.0), M["hull"], ff, bevel=0.1)
    kit.box("ff.windows", (5.04, 3.04, 0.5), (-1.0, 0, 2.2), M["port"], ff)
    kit.box("ff.bridge", (2.0, 2.0, 1.0), (-1.0, 0, 3.3), M["hull"], ff)
    kit.box("ff.deckglow", (8.0, 3.0, 0.1), (0, 0, 1.35), M["lamp"], ff)
    # the street: bin and kerb, a long way off to the side
    kit.plane("street.road", (90, 8), (150, 0, -0.003), M["road"])
    kit.plane("street.pave", (90, 6), (150, 6.5, 0.0), M["quay"])
    kit.box("street.kerb", (90, 0.2, 0.14), (150, 3.5, 0.07), M["stone"])
    building_row(kit, M, 120, 14, 10, rng)
    bin_ = kit.empty("bin", (150, 6.6, 0))
    kit.cyl("bin.body", 0.46, 1.0, (0, 0, 0.5), M["bin"], bin_, n=16, r2=0.52)
    kit.cyl("bin.lid", 0.54, 0.07, (0, 0, 1.03), M["iron"], bin_, n=16)
    kit.box("bin.slot", (0.6, 0.18, 0.02), (0, -0.2, 1.075), M["black"], bin_)
    kit.cyl("street.lamp", 0.07, 4.2, (153.5, 7.5, 2.1), M["iron"], n=8)
    kit.box("street.lamphead", (0.5, 0.3, 0.14), (153.3, 7.5, 4.2), M["iron"])
    ctx["mdots"] = [kit.cyl(f"mdot{k}", 0.06, 0.006, (0.3 - 0.04 * k, -1.0 - 1.15 * k, 0.012), M["dot"], n=10) for k in range(9)]
    # the beach
    kit.plane("beach", (60, 60), (900, 25, 0.0), M["sand"])
    for k in range(10):
        kit.box(f"beach.rock{k}", (0.5 + 0.1 * k, 0.4, 0.3), (880 + 4 * k, 12 + (k % 3) * 6, 0.12), M["stone"], bevel=0.1)
    kit.plane("beach.sea", (200, 80), (900, -45, -0.2), M["water"])
    # the kite woman's house
    kit.plane("kite.ground", (40, 30), (800, 4, 0.0), M["grass"])
    kit.plane("kite.path", (1.6, 8), (800, -3.0, 0.004), M["quay"])
    kit.box("kite.house", (9.0, 6.0, 3.4), (800, 8, 1.7), M["white"], None, bevel=0.04)
    for sg in (-1, 1):
        sl = kit.box(f"kite.roof{sg}", (9.8, 3.6, 0.2), (800, 8 - sg * 1.55, 4.45), M["slate"], None)
        sl.rotation_euler = (sg * 0.6, 0, 0)
    kit.box("kite.door", (1.0, 0.1, 2.1), (800, 4.97, 1.05), M["green"])
    kit.box("kite.win1", (1.2, 0.08, 1.1), (797, 4.97, 1.9), M["glass"])
    kit.box("kite.win2", (1.2, 0.08, 1.1), (803, 4.97, 1.9), M["glass"])
    for sx in (-1, 1):
        kit.box(f"kite.gatepost{sx}", (0.14, 0.14, 1.1), (800 + sx * 0.8, -4.4, 0.55), M["iron"])
    kit.box("kite.gate", (1.5, 0.05, 0.8), (800, -4.4, 0.65), M["iron"])
    for sx in (-1, 1):
        kit.box(f"kite.fence{sx}", (5.0, 0.08, 0.9), (800 + sx * 3.4, -4.4, 0.5), M["shelf"])


def build_flat(kit, M, ctx):
    x = 200.0
    kit.box("flat.floor", (5.0, 5.0, 0.1), (x, 0, -0.05), M["wood"])
    kit.box("flat.ceil", (5.0, 5.0, 0.1), (x, 0, 2.65), M["white"])
    kit.box("flat.back", (5.0, 0.12, 2.6), (x, 2.5, 1.3), M["white"])
    kit.box("flat.w1", (5.0, 0.12, 0.9), (x, -2.5, 0.45), M["white"])
    kit.box("flat.w2", (5.0, 0.12, 0.4), (x, -2.5, 2.45), M["white"])
    for sx in (-1, 1):
        kit.box(f"flat.w3{sx}", (1.7, 0.12, 1.3), (x + sx * 1.65, -2.5, 1.55), M["white"])
        kit.box(f"flat.side{sx}", (0.12, 5.0, 2.6), (x + sx * 2.5, 0, 1.3), M["white"])
    kit.box("flat.sill", (1.7, 0.3, 0.06), (x, -2.55, 0.9), M["cream"])
    kit.box("flat.table", (1.1, 0.7, 0.05), (x + 0.9, 0.1, 0.74), M["shelf"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"flat.tl{sx}{sy}", (0.06, 0.06, 0.72), (x + 0.9 + sx * 0.5, 0.1 + sy * 0.3, 0.36), M["shelf"])
    ch = kit.empty("flat.chair", (x - 0.1, 0.1, 0))
    kit.box("flat.seat", (0.46, 0.46, 0.05), (0, 0, 0.46), M["shelf"], ch)
    kit.box("flat.cback", (0.46, 0.05, 0.5), (0, 0.22, 0.72), M["shelf"], ch)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"flat.cl{sx}{sy}", (0.04, 0.04, 0.46), (sx * 0.2, sy * 0.2, 0.23), M["shelf"], ch)
    # door on the +y wall, ajar (a hinge group we turn)
    hinge = kit.empty("flat.hinge", (x - 1.9, 2.44, 0))
    kit.box("flat.doorleaf", (0.95, 0.05, 2.0), (0.48, 0, 1.0), M["cream"], hinge)
    ctx["flat_door"] = hinge
    kit.box("flat.doorframe", (1.1, 0.14, 2.1), (x - 1.42, 2.5, 1.05), M["black"])
    # the dark far island line, out the window (the -y direction)
    kit.box("flat.farisland", (60, 8, 3.0), (x + 10, -140, 1.0), kit.plastic("#2a3140", 1.0, "far dark"))
    kit.plane("flat.sea", (400, 300), (x, -150, -0.3), M["water"])
    kit.light("flat lamp", "POINT", (x + 0.3, 0.3, 2.35), 1.0, "#ffd9a8", size=0.3)
    # the phone, on the table
    ph = kit.empty("phone", (x + 1.1, 0.15, 0.77))
    kit.box("phone.body", (0.075, 0.012, 0.15), (0, 0, 0.075), M["black"], ph, rot=(0.0, 0, 0), bevel=0.01)
    scr = kit.box("phone.screen", (0.065, 0.004, 0.135), (0, -0.007, 0.078), M["screen"], ph)
    ph.rotation_euler = (math.radians(-12), 0, math.radians(-20))
    ctx["phone"] = ph
    # the phone in the back room, same object placed by cue
    # rain, no: the flat is plain


def build_kitchen(kit, M, ctx):
    x = 400.0
    kit.box("k.floor", (8.0, 6.0, 0.1), (x, 0, -0.05), M["wood"])
    kit.box("k.ceil", (8.0, 6.0, 0.1), (x, 0, 2.65), M["white"])
    kit.box("k.back", (8.0, 0.12, 2.6), (x, 2.2, 1.3), M["cream"])
    kit.box("k.left", (0.12, 6.0, 2.6), (x - 4.0, 0, 1.3), M["cream"])
    kit.box("k.right", (0.12, 6.0, 2.6), (x + 4.0, 0, 1.3), M["cream"])
    kit.box("k.front", (8.0, 0.12, 2.6), (x, -2.9, 1.3), M["cream"])
    kit.box("k.win", (1.2, 0.05, 1.0), (x - 1.8, 2.12, 1.55), kit.emit("#dfe8f0", 2.0, "kitchen window"))
    kit.box("k.winframe", (1.4, 0.06, 1.2), (x - 1.8, 2.13, 1.55), M["cream"])
    kit.box("k.counter", (2.2, 0.7, 0.9), (x + 2.6, 1.7, 0.45), M["shelf"])
    kit.cyl("k.kettle", 0.1, 0.18, (x + 2.2, 1.7, 1.0), M["steel"], n=10, r2=0.08)
    kit.box("k.rail", (1.4, 0.05, 0.1), (x + 1.0, 2.1, 1.65), M["shelf"])
    for k in range(3):
        kit.cyl(f"k.peg{k}", 0.02, 0.1, (x + 0.55 + 0.45 * k, 2.04, 1.65), M["hook"], rot=(math.radians(90), 0, 0), n=6)
    h = hat_stripes(kit, M, "k.hat")
    h.location = (x + 1.0, 1.99, 1.6)
    h.rotation_euler = (math.radians(100), 0, 0)
    kit.box("k.table", (1.4, 0.9, 0.05), (x - 1.0, 1.0, 0.75), M["shelf"])
    kit.light("k lamp", "POINT", (x, 0.3, 2.4), 1.0, "#ffe0b0", size=0.4)
    kit.light("k fill", "POINT", (x + 0.6, -1.2, 1.9), 1.0, "#ffe6c4", size=0.5)


def build_door(kit, M, ctx):
    x = 500.0
    kit.plane("d.ground", (30, 20), (x, -3, 0.0), M["quay"])
    kit.plane("d.wallplane", (30, 1), (x, 1.5, 0.0), M["quay"])
    kit.box("d.wall", (12, 0.6, 5.0), (x, 1.7, 2.5), M["brick"])
    kit.box("d.door", (1.1, 0.1, 2.2), (x, 1.36, 1.1), kit.plastic("#2a3a4a", 0.5, "flat door"))
    kit.box("d.step", (1.8, 0.7, 0.18), (x, 0.9, 0.09), M["stone"])
    kit.cyl("d.lamp", 0.05, 0.4, (x + 1.35, 1.3, 2.5), M["iron"], n=8)
    kit.box("d.lamphead", (0.3, 0.3, 0.3), (x + 1.35, 1.1, 2.4), M["lamp"])
    kit.light("d lamp", "POINT", (x + 1.3, 0.7, 2.3), 1.0, "#ffd9a0", size=0.2)
    kit.light("d fill", "POINT", (x - 0.3, -1.4, 2.0), 1.0, "#ffd9b8", size=0.6)
    for k in range(3):
        kit.box(f"d.win{k}", (1.0, 0.06, 1.2), (x - 4.2 + k * 2.2 + (k > 0) * 3, 1.38, 2.8), M["glass"])


def build_bedj(kit, M, ctx):
    x = 600.0
    kit.box("b.floor", (6, 6, 0.1), (x, 0, -0.05), M["wood"])
    kit.box("b.ceil", (6, 6, 0.1), (x, 0, 2.65), M["white"])
    kit.box("b.back", (6, 0.12, 2.6), (x, 2.3, 1.3), M["cream"])
    kit.box("b.front", (6, 0.12, 2.6), (x, -3.0, 1.3), M["cream"])
    for sx in (-1, 1):
        kit.box(f"b.side{sx}", (0.12, 6, 2.6), (x + sx * 3, 0, 1.3), M["cream"])
    kit.box("b.bed", (1.6, 2.1, 0.45), (x, 1.2, 0.3), M["shelf"])
    kit.box("b.mattress", (1.5, 2.0, 0.22), (x, 1.2, 0.58), M["white"], bevel=0.04)
    kit.box("b.head", (1.7, 0.1, 1.1), (x, 2.2, 0.75), M["shelf"])
    kit.box("b.pillow", (0.7, 0.4, 0.14), (x, 1.9, 0.76), M["cream"], bevel=0.05)
    kit.box("b.duvet", (1.58, 1.15, 0.2), (x, 0.55, 0.78), M["blue"], bevel=0.06)
    kit.light("b lamp", "POINT", (x + 0.2, -0.6, 2.3), 1.0, "#ffd9a8", size=0.4)


def build_hut(kit, M, ctx):
    x = 700.0
    kit.box("h.floor", (3.2, 3.2, 0.1), (x, 0, -0.05), M["wood2"])
    kit.box("h.ceil", (3.2, 3.2, 0.1), (x, 0, 2.5), M["white"])
    kit.box("h.back", (3.2, 0.1, 2.5), (x, 1.6, 1.25), M["cream"])
    kit.box("h.front", (3.2, 0.1, 2.5), (x, -1.6, 1.25), M["cream"])
    for sx in (-1, 1):
        kit.box(f"h.side{sx}", (0.1, 3.2, 2.5), (x + sx * 1.6, 0, 1.25), M["cream"])
    for z in (0.5, 1.15, 1.8):
        kit.box(f"h.shelf{z}", (2.4, 0.4, 0.05), (x, 1.38, z), M["shelf"])
    for sx in (-1, 1):
        kit.box(f"h.bracket{sx}", (0.05, 0.4, 1.4), (x + sx * 1.2, 1.38, 1.1), M["shelf"])
    for k in range(7):
        a = k * 0.8
        kit.box(f"h.web{k}", (0.012, 0.012, 0.5 + 0.05 * k), (x - 1.15 + 0.1 * k, 1.34, 1.95 - 0.02 * k), M["web"], rot=(0, 0.6 * (1 if k % 2 else -1), 0.2))
    kit.box("h.dust", (2.3, 0.3, 0.012), (x, 1.4, 1.83), M["dust"])
    kit.box("h.dust2", (2.3, 0.3, 0.012), (x, 1.4, 1.18), M["dust"])
    kit.light("h lamp", "POINT", (x, 0.0, 2.3), 1.0, "#ffe0b0", size=0.4)


def build_island(kit, M, ctx):
    X = ISL
    kit.plane("isl.ground", (90, 100), (X, 30, -0.01), M["grass"])
    kit.plane("isl.slip", (10, 12), (X, -6, 0.0), M["stone"])
    kit.mesh_obj("isl.slip.down", [(X - 5, -12, 0), (X + 5, -12, 0), (X + 5, -18, -1.0), (X - 5, -18, -1.0)], [(0, 3, 2, 1)], M["stone"])
    kit.plane("isl.lane", (3.6, 34), (X, 17, 0.004), kit.grime("#8c826e", 0.7, 2.0, "lane dirt"))
    rng = random.Random(4)
    for sx in (-1, 1):
        kit.box(f"isl.wall{sx}", (0.5, 33.0, 1.05), (X + sx * 2.05, 17.5, 0.52), M["wall"])
        for k in range(55):
            kit.box(f"isl.cope{sx}{k}", (0.6, rng.uniform(0.4, 0.7), 0.16), (X + sx * 2.05, 1.3 + k * 0.6, 1.1),
                    M["stone"], rot=(0, 0, rng.uniform(-0.15, 0.15)), bevel=0.04)
    # the cottage
    cx = X
    kit.box("c.floor", (10, 12.0, 0.1), (cx, 41, -0.05), M["wood2"])
    t = 0.3
    kit.box("c.front.l", (4.4, t, 3.2), (cx - 2.75, 35.15, 1.6), M["white"])
    kit.box("c.front.r", (4.4, t, 3.2), (cx + 2.75, 35.15, 1.6), M["white"])
    kit.box("c.front.top", (1.1, t, 1.1), (cx, 35.15, 2.65), M["white"])
    kit.box("c.back", (10, t, 3.2), (cx, 46.85, 1.6), M["white"])
    for sx in (-1, 1):
        kit.box(f"c.side{sx}", (t, 12, 3.2), (cx + sx * 4.85, 41, 1.6), M["white"])
    kit.box("c.ceil", (10, 12, 0.12), (cx, 41, 3.2), M["white"])
    for sg in (-1, 1):
        sl = kit.box(f"c.roof{sg}", (10.8, 7.4, 0.2), (cx, 41 + sg * 3.0, 4.15), M["slate"])
        sl.rotation_euler = (sg * 0.42, 0, 0)
    kit.box("c.gablefront", (9.8, 0.2, 1.0), (cx, 35.1, 3.7), M["white"])
    kit.box("c.sill", (1.4, 0.45, 0.05), (cx - 3.2, 34.9, 0.9), M["stone"])
    for sx in (-1, 1):
        kit.box(f"c.win{sx}", (1.0, 0.06, 1.0), (cx + sx * 3.2, 34.98, 1.5), M["glass"])
    # door frame and leaf (opens inward on a hinge)
    kit.box("c.frame.l", (0.1, 0.4, 2.15), (cx - 0.6, 35.15, 1.07), M["white"])
    kit.box("c.frame.r", (0.1, 0.4, 2.15), (cx + 0.6, 35.15, 1.07), M["white"])
    hinge = kit.empty("c.hinge", (cx - 0.55, 35.3, 0))
    kit.box("c.door", (1.1, 0.07, 2.1), (0.55, 0, 1.05), M["green"], hinge, bevel=0.01)
    kit.box("c.doorknob", (0.07, 0.07, 0.07), (0.95, -0.07, 1.0), M["steel"], hinge)
    ctx["cdoor"] = hinge
    kit.box("c.mat", (1.0, 0.65, 0.04), (cx, 34.35, 0.02), M["coir"], bevel=0.01)
    kit.box("c.step", (1.6, 0.5, 0.1), (cx, 34.7, 0.05), M["stone"])
    kit.box("c.porch", (0.16, 0.14, 0.22), (cx + 0.95, 34.8, 2.45), M["iron"])
    kit.box("c.porchglow", (0.1, 0.1, 0.14), (cx + 0.95, 34.8, 2.36), M["lamp"])
    kit.light("porch lamp", "POINT", (cx + 0.95, 34.5, 2.3), 1.0, "#ffd9a0", size=0.15)
    kit.light("mat lamp", "POINT", (cx - 0.5, 33.0, 1.1), 1.0, "#ffd9a0", size=0.2)
    # hall: x +-1.2, y 35.3 .. 43.3
    for sx in (-1, 1):
        kit.box(f"c.hall{sx}", (0.12, 8.0, 2.6), (cx + sx * 1.2, 39.3, 1.3), M["cream"])
    kit.box("c.hallceil", (2.4, 8, 0.1), (cx, 39.3, 2.62), M["white"])
    kit.box("c.hallend.l", (1.0, 0.12, 2.6), (cx - 0.9, 43.3, 1.3), M["cream"])
    kit.box("c.hallend.r", (1.0, 0.12, 2.6), (cx + 0.9, 43.3, 1.3), M["cream"])
    kit.box("c.hallend.t", (0.8, 0.12, 0.5), (cx, 43.3, 2.35), M["cream"])
    kit.box("c.hallfloor", (2.4, 8, 0.04), (cx, 39.3, 0.02), M["wood"])
    bh = kit.empty("c.backhinge", (cx - 0.4, 43.3, 0))
    kit.box("c.backdoor", (0.8, 0.05, 2.1), (0.4, 0, 1.05), M["cream"], bh)
    ctx["backdoor"] = bh
    kit.box("c.coathook", (0.05, 0.3, 0.05), (cx - 1.12, 36.9, 1.7), M["hook"])
    kit.box("c.coatpatch", (0.02, 0.5, 1.1), (cx - 1.135, 36.9, 1.15), kit.plastic("#d6cfbc", 0.9, "coat outline"))
    # bedroom (x +1.2 .. +4.7, y 35.3 .. 42), reached by a door gap in the hall's east wall
    kit.box("c.bedwall", (0.12, 1.4, 2.6), (cx + 1.2, 35.9, 1.3), M["cream"]) if False else None
    kit.box("c.bed", (1.6, 2.1, 0.45), (cx + 3.6, 38.3, 0.3), M["shelf"])
    kit.box("c.mattress", (1.5, 2.0, 0.22), (cx + 3.6, 38.3, 0.58), M["white"], bevel=0.04)
    kit.box("c.quilt", (1.56, 1.5, 0.12), (cx + 3.6, 37.9, 0.74), M["quilt"], bevel=0.04)
    kit.box("c.pillow", (0.7, 0.4, 0.14), (cx + 3.6, 39.1, 0.75), M["cream"], bevel=0.05)
    kit.box("c.bedhead", (1.7, 0.1, 1.0), (cx + 3.6, 39.4, 0.7), M["shelf"])
    kit.box("c.bedfloor", (3.4, 6.5, 0.04), (cx + 2.9, 38.5, 0.02), M["wood"])
    kit.box("c.bedwall2", (0.12, 6.5, 2.6), (cx + 1.2, 38.5, 1.3), M["cream"]) if False else None
    kit.light("hall light", "POINT", (cx, 39.5, 2.3), 1.0, "#ffd0a0", size=0.3)
    kit.light("hall light2", "POINT", (cx, 36.5, 2.3), 1.0, "#ffd0a0", size=0.3)
    kit.light("bed light", "POINT", (cx + 3.0, 37.5, 2.3), 1.0, "#ffd9b0", size=0.3)
    # the back room: x 296 .. 304, y 43.3 .. 46.9, hung with hooks
    kit.box("br.floor", (8.4, 3.8, 0.04), (cx, 45.1, 0.02), M["wood"])
    kit.box("br.front.l", (3.4, 0.12, 2.6), (cx - 2.5, 43.3, 1.3), M["peg"]) if False else None
    for sx in (-1, 1):
        kit.box(f"br.board{sx}", (0.06, 3.6, 2.6), (cx + sx * 4.0, 45.1, 1.3), M["peg"])
    kit.box("br.boardback", (8.0, 0.06, 2.6), (cx, 46.62, 1.3), M["peg"])
    kit.box("br.boardfront.l", (3.4, 0.06, 2.6), (cx - 2.3, 43.33, 1.3), M["peg"])
    kit.box("br.boardfront.r", (3.4, 0.06, 2.6), (cx + 2.3, 43.33, 1.3), M["peg"])
    kit.light("tbl lamp", "POINT", (cx - 0.3, 43.9, 1.7), 1.0, "#ffd9a8", size=0.3)
    kit.light("br bulb", "POINT", (cx, 45.2, 2.45), 1.0, "#ffe2b8", size=0.3)
    kit.sphere("br.bulbglow", 0.07, (cx, 45.2, 2.5), M["lamp"], seg=8)
    cols = ["#d9a531", "#2a3550", "#8a8f94", "#8a3f2a", "#3f6f7a", "#5e3550", "#c9c2ae", "#3a6fb0", "#6b4a2e"]
    mats = [kit.plastic(c, 0.8, f"lost {c}") for c in cols]
    rng = random.Random(21)
    ctx["keys"] = []
    ctx["lost"] = []

    def hung(px, py, z, rot, kind):
        g = kit.empty(f"lost.{px:.2f}.{py:.2f}.{z:.2f}", (px, py, z), None, rot=rot)
        kit.cyl(f"{g.name}.pin", 0.012, 0.06, (0, 0.03, 0.0), M["hook"], g, rot=(math.radians(90), 0, 0), n=6)
        m = rng.choice(mats)
        if kind == 0:
            m = rng.choice(mats[:3])
            gv = glove(kit, f"{g.name}.g", m, g, scale=1.3)
            gv.location = (0, 0.03, -0.17)
            gv.rotation_euler = (math.radians(180), 0, 0)
        elif kind == 1:
            r = torus(kit, f"{g.name}.ring", 0.05, 0.009, (0, 0.03, -0.06), M["hook"], g, rot=(math.radians(90), 0, 0), n=14, m=5)
            for k in range(3):
                kit.box(f"{g.name}.k{k}", (0.025, 0.008, 0.1), (-0.03 + 0.03 * k, 0.03, -0.17), kit.metal("#b0a46a", 0.35), g)
            ctx["keys"].append(g)
        elif kind == 2:
            kit.sphere(f"{g.name}.hat", 0.12, (0, 0.1, -0.1), m, g, seg=10).scale = (1, 1, 0.8)
        elif kind == 3:
            kit.box(f"{g.name}.sc", (0.13, 0.05, 0.5), (0, 0.04, -0.26), m, g, bevel=0.015)
        else:
            kit.box(f"{g.name}.bag", (0.2, 0.08, 0.26), (0, 0.06, -0.14), m, g, bevel=0.03)
        ctx["lost"].append(g)
        return g
    for z in [0.55 + 0.4 * r for r in range(5)]:
        for k in range(18):
            xx = cx - 3.8 + 0.43 * k
            if abs(xx - (cx + 1.3)) < 0.8 and 1.3 < z < 2.0:
                continue
            hung(xx, 46.5, z + rng.uniform(0, 0.05), (0, 0, 0), rng.choice((0, 0, 1, 2, 3, 4)))
        for k in range(7):
            hung(cx - 3.93, 43.7 + 0.45 * k, z, (0, 0, math.radians(90)), rng.choice((0, 0, 1, 2, 3, 4)))
            hung(cx + 3.93, 43.7 + 0.45 * k, z, (0, 0, math.radians(-90)), rng.choice((0, 0, 1, 2, 3, 4)))
    for k in range(4):
        hung(cx + 0.75 + 0.3 * k, 46.5, 1.72, (0, 0, 0), 1)
    # the umbrella and the bike, the striped hat by the door, the table and the phone place
    kit.cyl("br.umb", 0.04, 1.0, (cx + 3.0, 44.0, 0.52), kit.plastic("#16171b", 0.6, "umb2"), None, rot=(0.12, 0.1, 0), n=10)
    hat_stripes(kit, M, "br.hat").location = (cx - 0.9, 43.4, 1.7)
    bike = kit.empty("bike", (cx + 2.0, 46.2, 0))
    for y in (-0.55, 0.55):
        torus(kit, f"bike.tyre{y}", 0.31, 0.025, (0, y, 0.34), M["tyre"], bike, rot=(0, math.radians(90), 0), n=24, m=6)
    rod(kit, "bike.top", (0, -0.5, 0.78), (0, 0.3, 0.75), 0.015, M["bike"], bike)
    rod(kit, "bike.down", (0, -0.5, 0.78), (0, 0.05, 0.38), 0.015, M["bike"], bike)
    rod(kit, "bike.seat", (0, 0.3, 0.75), (0, 0.05, 0.38), 0.015, M["bike"], bike)
    rod(kit, "bike.fork", (0, -0.55, 0.34), (0, -0.5, 0.95), 0.012, M["bike"], bike)
    rod(kit, "bike.rear", (0, 0.05, 0.38), (0, 0.55, 0.34), 0.012, M["bike"], bike)
    kit.box("bike.bars", (0.5, 0.03, 0.03), (0, -0.5, 0.97), M["iron"], bike, bevel=0.008)
    kit.box("bike.saddle", (0.12, 0.26, 0.05), (0, 0.32, 0.8), M["tyre"], bike, bevel=0.015)
    bike.rotation_euler = (0, math.radians(8), math.radians(90))
    bike.location = (cx + 3.4, 45.4, 0.0)
    kit.box("br.table", (1.0, 0.7, 0.05), (cx - 0.6, 44.6, 0.78), M["shelf"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"br.tl{sx}{sy}", (0.06, 0.06, 0.76), (cx - 0.6 + sx * 0.45, 44.6 + sy * 0.3, 0.38), M["shelf"])
    kit.light("isl lamp", "POINT", (X + 3.0, -9.0, 3.6), 1.0, "#ffe2b0", size=0.4)
    kit.light("board fill", "POINT", (X + 1.6, -13.0, 2.2), 1.0, "#ffe2b0", size=0.4)
    kit.light("blue fill", "POINT", (X + 6.0, -5.6, 1.4), 1.0, "#ffe6c0", size=0.4)
    kit.box("isl.lamppost", (0.12, 0.12, 3.6), (X + 3.2, -9.0, 1.8), M["iron"])
    build_bow(kit, M, X, -13.2, "I")
    ctx["vis"]["bowI"] = {"objs": [_obj("bowI")], "default": False}
    # the neighbour's blue door
    kit.box("blue.house", (6.0, 6.0, 3.0), (X + 12.2, -3.0, 1.5), M["white"], bevel=0.04)
    kit.box("blue.door", (0.08, 1.0, 2.1), (X + 9.14, -3.0, 1.05), M["blue"])
    kit.box("blue.step", (0.7, 1.6, 0.14), (X + 8.8, -3.0, 0.07), M["stone"])
    kit.box("blue.roof", (6.6, 6.6, 0.3), (X + 12.2, -3.0, 3.1), M["slate"])
    kit.light("blue lamp", "POINT", (X + 8.2, -2.4, 2.3), 1.0, "#ffe0b0", size=0.3)


# ------------------------------------------------------------------------------------------------ the ferry
def build_ferry(kit, M, ctx):
    F = FER
    kit.plane("sea", (3000, 3000), (F, 0, -0.35), M["water"])
    g = kit.empty("ferry", (F, 0, 0))
    B = lambda n, sz, loc, m, rot=(0, 0, 0), bev=0.0: kit.box(f"fe.{n}", sz, loc, m, g, rot=rot, bevel=bev)
    B("hull", (6.8, 16.0, 2.5), (0, 0, -0.35), M["hull"], bev=0.05)
    B("band", (6.84, 16.04, 0.7), (0, 0, -1.15), M["rust"])
    for k in range(10):
        B(f"streak{k}", (0.08, 0.05, 1.0 + 0.25 * (k % 3)), (-3.42 + 6.84 * (k % 2), -6.5 + 1.4 * k, 0.2), M["rustdark"])
    B("deck", (6.4, 15.4, 0.1), (0, 0, 0.9), M["deck"])
    for sx in (-1, 1):
        for z in (1.5, 2.0):
            rod(kit, f"fe.rail{sx}{z}", (sx * 3.2, -7.6, z), (sx * 3.2, 7.6, z), 0.035, M["steel"], g)
        for k in range(9):
            B(f"post{sx}{k}", (0.07, 0.07, 1.1), (sx * 3.2, -7.0 + 1.75 * k, 1.45), M["steel"])
    B("bowdoor", (5.0, 0.12, 2.6), (0, -7.9, 2.1), M["hull"], rot=(0.2, 0, 0))
    # car deck lamps and a roof slab (the stair column stays open)
    B("roof", (4.9, 8.6, 0.14), (0.9, -3.7, 3.65), M["hull"])
    for k in range(3):
        B(f"cdstrip{k}", (0.1, 1.4, 0.05), (0.9, -6.0 + 2.5 * k, 3.55), M["strip"])
        kit.light(f"deck lamp {k}", "POINT", (g.location.x + 0.9, -6.0 + 2.5 * k, 3.3), 1.0, "#ffe9c8", size=0.5)
    # cars
    for nm, mat, x, y in (("carA", M["car1"], -1.4, -5.0), ("carB", M["car2"], 1.5, -1.8)):
        B(nm + "body", (1.75, 3.7, 0.85), (x, y, 1.45), mat, bev=0.12)
        B(nm + "cab", (1.55, 2.0, 0.7), (x, y + 0.3, 2.15), mat, bev=0.14)
        B(nm + "win", (1.58, 1.8, 0.4), (x, y + 0.3, 2.2), M["glass"])
        for sx in (-1, 1):
            for sy in (-1.2, 1.2):
                kit.cyl(f"fe.{nm}w{sx}{sy}", 0.3, 0.2, (x + sx * 0.88, y + sy, 1.25), M["tyre"], g, rot=(0, math.radians(90), 0), n=14)
    # the stair: x -2.8 .. -1.8, y -3.4 .. -0.2, 12 steps up to z = 3.9
    for k in range(12):
        B(f"step{k}", (1.0, 0.34, 0.12), (-2.3, -3.4 + 0.27 * k + 0.17, 0.96 + 0.25 * k), M["steel"])
        B(f"riser{k}", (1.0, 0.04, 0.25), (-2.3, -3.4 + 0.27 * k + 0.02, 0.84 + 0.25 * k), M["hull"])
    for z0, nm in ((1.0, "lo"), (1.9, "hi")):
        rod(kit, f"fe.stairrail{nm}", (-1.78, -3.4, 0.9 + z0), (-1.78, -0.2, 3.9 + z0 - 0.05), 0.03, M["steel"], g)
    # the lounge: x -3.1 .. 3.4, y 0.6 .. 7.6, floor top z = 3.9, ceiling z = 6.5
    L0, L1, W0, W1 = 0.6, 7.6, -3.1, 3.4
    B("lfloor", (6.5, 7.0, 0.2), ((W0 + W1) / 2, (L0 + L1) / 2, 3.8), M["hull"])
    B("lfloor2", (6.2, 6.8, 0.04), ((W0 + W1) / 2, (L0 + L1) / 2, 3.92), M["floor"])
    B("lceil", (6.6, 7.2, 0.16), ((W0 + W1) / 2, (L0 + L1) / 2, 6.58), M["hull"])
    # walls: +x wall with the big window, the others plain with a door in the -y wall
    B("wallx.low", (0.14, 7.0, 0.9), (W1, 4.1, 4.4), M["hull"])
    B("wallx.top", (0.14, 7.0, 0.4), (W1, 4.1, 6.35), M["hull"])
    for y in (0.7, 7.5):
        B(f"wallx.end{y}", (0.14, 0.4, 1.3), (W1, y, 5.5), M["hull"])
    for y in (2.0, 6.0):
        B(f"mullion{y}", (0.1, 0.1, 1.3), (W1, y, 5.5), M["hull"])
    B("wallnx.low", (0.14, 7.0, 1.0), (W0, 4.1, 4.4), M["cream"])
    B("wallnx.top", (0.14, 7.0, 0.4), (W0, 4.1, 6.3), M["cream"])
    for y0, y1 in ((0.6, 1.6), (3.2, 5.0), (6.6, 7.6)):
        B(f"nxpier{y0}", (0.14, y1 - y0, 1.3), (W0, (y0 + y1) / 2, 5.55), M["cream"])
    B("wally.far", (6.5, 0.14, 2.7), ((W0 + W1) / 2, L1, 5.2), M["cream"])
    B("wally.l", (0.3, 0.14, 2.7), (-2.95, L0, 5.2), M["cream"])
    B("wally.m", (5.2, 0.14, 2.7), (0.8, L0, 5.2), M["cream"])
    B("wally.top", (1.0, 0.14, 0.5), (-2.3, L0, 6.25), M["cream"])
    B("landing", (1.2, 1.0, 0.12), (-2.3, 0.15, 3.86), M["steel"])
    # the door leaf, open, with its round window
    dh = kit.empty("fe.doorhinge", (-1.8, L0, 3.92), g)
    kit.box("fe.doorleaf", (1.0, 0.06, 2.05), (-0.5, 0, 1.03), M["hull"], dh)
    kit.cyl("fe.doorport", 0.2, 0.05, (-0.5, -0.03, 1.4), M["port"], dh, rot=(math.radians(90), 0, 0), n=18)
    torus(kit, "fe.doorring", 0.2, 0.03, (-0.5, -0.04, 1.4), M["steel"], dh, rot=(math.radians(90), 0, 0), n=18, m=5)
    dh.rotation_euler = (0, 0, math.radians(-70))
    # steady strips
    for x in (-1.7, 0.2, 1.8):
        B(f"strip{x}", (0.16, 5.4, 0.05), (x, 4.1, 6.46), M["strip"])
    kit.light("lounge a", "POINT", (F - 1.2, 2.8, 6.1), 1.0, "#f2f4ee", size=0.6)
    kit.light("lounge b", "POINT", (F - 1.2, 5.6, 6.1), 1.0, "#f2f4ee", size=0.6)
    # the window bench, a group so it can tilt a hair
    bn = kit.empty("fe.bench", (F + BENCH_X, 4.0, 3.9))
    for yy in (SEAT_Y["gran"], SEAT_Y["me"]):
        c = kit.box(f"fe.cushion{yy}", (1.0, 1.1, 0.5), (0, yy - 4.0, 0.25), M["teal"], bn, bevel=0.08)
        kit.box(f"fe.back{yy}", (0.18, 1.15, 0.95), (-0.55, yy - 4.0, 0.95), M["teal"], bn, bevel=0.08)
        kit.box(f"fe.legbar{yy}", (0.9, 0.06, 0.05), (0.1, yy - 4.0 - 0.5, 0.05), M["steel"], bn)
    arm = kit.box("fe.armrest", (0.95, 0.12, 0.2), (0.05, 0, 0.62), M["steel"], bn, bevel=0.03)
    kit.box("fe.armpost", (0.1, 0.1, 0.4), (0.05, 0, 0.35), M["steel"], bn)
    kit.box("fe.benchbase", (1.2, 3.5, 0.16), (0, 0, 0.1), M["tealdk"], bn)
    # the two upright strokes scratched into the armrest top (shown by a cue)
    strokes = [kit.box(f"fe.stroke{k}", (0.14, 0.014, 0.006), (0.05, -0.03 + 0.06 * k, 0.725), kit.plastic("#f0762a", 0.5, "scratch"), bn) for k in range(2)]
    ctx["strokes"] = strokes
    # the dent in the right seat's cushion (Gran's seat is the left in the script; this is my seat's)
    dent = kit.sphere("fe.dent", 0.45, (0, SEAT_Y["gran"] - 4.0, 0.5), kit.plastic("#1d3a42", 0.8, "dent"), bn, seg=14)
    dent.scale = (0.9, 1.0, 0.07)
    ctx["dent"] = dent
    ctx["bench"] = bn
    # the folded seat for L22: an extra seat flap, kept as the same cushion; nothing extra
    # plain rows facing the bow
    for yy in (2.6, 4.4, 6.2):
        B(f"row{yy}", (2.4, 0.8, 0.45), (-1.9, yy, 4.15), M["teal"], bev=0.06)
        B(f"rowback{yy}", (2.4, 0.16, 0.8), (-1.9, yy + 0.4, 4.6), M["teal"], bev=0.06)
    # the smudge on the glass (a thin pane in the window, only the smudge shows)
    sm = kit.sphere("fe.smudge", 0.2, (W1 - 0.02, 3.7, 5.25), M["smudge"], g, seg=12)
    sm.scale = (0.03, 1.0, 1.5)
    ctx["smudge"] = sm
    # the upper works: bridge and funnel
    B("bridge", (3.0, 2.4, 1.3), (0, 5.8, 7.3), M["hull"], bev=0.05)
    B("bridgewin", (3.04, 2.0, 0.4), (0, 5.8, 7.45), M["glass"])
    B("funnel", (1.0, 1.2, 1.7), (0, 3.0, 7.5), M["rust"], bev=0.1)
    B("funnelband", (1.04, 1.24, 0.3), (0, 3.0, 8.1), M["hull"])
    # sea lights
    rng = random.Random(8)
    for k in range(34):   # the town, +y far
        kit.box(f"town.l{k}", (1.6, 1.0, 1.4), (F + rng.uniform(-120, 120), 420 + rng.uniform(-6, 10), rng.uniform(1.2, 9)), M["far"])
    for k in range(18):   # the island, -x far, behind the lounge
        kit.box(f"isl.l{k}", (1.4, 1.0, 1.2), (F - 150 - rng.uniform(0, 12), 5 + rng.uniform(-28, 28), rng.uniform(1.2, 9)), M["far"])
    kit.box("isl.dark", (30, 80, 14), (F - 175, 5, 2.0), kit.plastic("#161c28", 1.0, "far island"))
    for k in range(10):   # warm lights low off the +x side, out the window
        kit.box(f"star.l{k}", (1.4, 1.0, 1.0), (F + 90 + rng.uniform(0, 14), 10 + rng.uniform(-30, 40), rng.uniform(1.2, 4)), M["far"])
    # the wake: three pale strips trailing back (+y) from the stern
    for nm, a, w, e in (("m", 0.0, 3.2, 0.7), ("l", 0.05, 1.6, 0.5), ("r", -0.05, 1.6, 0.5)):
        s = kit.box(f"wake{nm}", (w, 240.0, 0.02), (F + math.sin(a) * 120, 8 + 120.0, -0.33), M["wake"])
        s.rotation_euler = (0, 0, -a)
    # lounge key and rim (steady): a warm low lamp off the window's harbour lights, a cool rim behind
    kit.light("harbour key", "POINT", (F + 2.2, 6.9, 4.7), 1.0, "#ffb26a", size=0.2)
    kit.light("window rim", "POINT", (F + 3.1, 5.6, 6.1), 1.0, "#9fc4ff", size=0.2)
    kit.light("window rim2", "POINT", (F + 3.1, 3.2, 6.1), 1.0, "#9fc4ff", size=0.2)
    kit.light("shrug key", "SPOT", (F + 3.6, 6.4, 4.7), 1.0, "#ffb070", spot=45, blend=0.6, size=0.3)
    kit.aim(kit.LIGHTS["shrug key"]["obj"], (F + 1.7, 4.75, 5.1))
    kit.light("bench fill", "POINT", (F + 0.6, 4.0, 6.0), 1.0, "#cfd8f0", size=0.4)
    kit.box("isl.hill", (16, 70, 9), (F + 112, 12, 2.0), kit.plastic("#161c28", 1.0, "far island 2"))
    kit.light("shrug rim", "POINT", (F + 0.2, 4.75, 6.2), 1.0, "#9fc4ff", size=0.3)
    kit.light("sunbeam", "SPOT", (F + 5.5, 4.0, 6.6), 1.0, "#ffd89a", spot=70, blend=0.5, size=0.6)
    kit.aim(kit.LIGHTS["sunbeam"]["obj"], (F + 1.7, 4.0, 4.5))


def build_phone_bezel(kit, M, ctx):
    cam = kit.OBJ["cam"]
    g = kit.empty("bezel", (0, 0, 0), cam)
    d = 0.8
    hh = 12.0 / 28.0 * d
    hw = hh * 9 / 16
    ih, iw = hh * 0.86, hw * 0.88
    blk = kit.plastic("#08090b", 0.4, "phone black")
    big = 0.6
    pieces = [((0, (ih + hh + big) / 2), (2 * (hw + big), hh + big - ih)),      # top
              ((0, -(ih + hh + big) / 2), (2 * (hw + big), hh + big - ih)),     # bottom
              (((iw + hw + big) / 2, 0), (hw + big - iw, 2 * ih)),               # right
              ((-(iw + hw + big) / 2, 0), (hw + big - iw, 2 * ih))]             # left
    for k, ((px, py), (sx, sy)) in enumerate(pieces):
        kit.box(f"bezel{k}", (sx, sy, 0.01), (px, py, -d), blk, g)
    # rounded-ish corners: four small blocks
    for k, (cx_, cy_) in enumerate(((1, 1), (-1, 1), (1, -1), (-1, -1))):
        kit.box(f"bezelc{k}", (hw * 0.08, ih * 0.05, 0.01), (cx_ * (iw - hw * 0.04), cy_ * (ih - ih * 0.025), -d + 0.001), blk, g)
    ctx["bezel"] = g
    _show([g], False)


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    M = materials(kit)
    ctx = {"M": M, "inited": False, "vis": {}}
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
    build_town(kit, M, ctx)
    build_flat(kit, M, ctx)
    build_island(kit, M, ctx)
    build_kitchen(kit, M, ctx)
    build_door(kit, M, ctx)
    build_bedj(kit, M, ctx)
    build_hut(kit, M, ctx)
    build_ferry(kit, M, ctx)
    build_shrug(kit, M, ctx)
    build_dog(kit, M, ctx)
    hops = story.get("hoppers", [])
    ctx["hoppers"] = {h["id"]: make_hopper(kit, M, f"hop.{h['id']}", h["kind"], h["color"]) for h in hops}
    hop_dot_pool(kit, M, ctx, len(hops))
    # loose props
    P = {}
    P["binglove"] = glove(kit, "p.binglove", M["mustard"], None, hole=True, scale=1.3)
    P["mglove"] = glove(kit, "p.mglove", M["mustard"], None, hole=True, scale=1.3)
    P["glasses"] = make_glasses_prop(kit, M, "p.glasses")
    kite = kit.empty("p.kite", (0, 0, -50))
    kk = kit.box("p.kite.d", (0.7, 0.7, 0.025), (0, 0, 0), kit.plastic("#f0c020", 0.6, "kite"), kite, rot=(0, 0, math.radians(45)), bevel=0.01)
    for k in range(5):
        kit.box(f"p.kite.t{k}", (0.1, 0.06, 0.02), (0.0, 0.5 + 0.22 * k, 0), kit.plastic("#e04a3a" if k % 2 else "#f2f0ea", 0.6, f"kt{k}"), kite)
    P["kite"] = kite
    jum = kit.empty("p.jumper", (0, 0, -50))
    kit.box("p.jumper.b", (0.7, 0.5, 0.18), (0, 0, 0), kit.plastic("#e48aa8", 0.95, "jumper pink"), jum, bevel=0.07)
    kit.box("p.jumper.s", (0.2, 0.55, 0.14), (0.4, 0.1, 0.0), kit.plastic("#e48aa8", 0.95, "jumper pink"), jum, bevel=0.05, rot=(0, 0, 0.5))
    P["jumper"] = jum
    ctx["props"] = P
    build_phone_bezel(kit, M, ctx)
    # lights
    sun = kit.light("sun", "SUN", tuple(SUN_DIR * 40), 1.0, "#f4f1ea", size=0.02)
    kit.aim(sun, (0, 0, 0))
    sun.data.angle = 0.25
    ctx["sun"] = sun
    fill = kit.light("fill", "SUN", tuple(FILL_DIR * 40), 1.0, "#c9d4de", size=0.02)
    kit.aim(fill, (0, 0, 0))
    fill.data.angle = 0.4
    ctx["fill"] = fill
    return ctx


# ------------------------------------------------------------------------------------------------ decorate
def _obj(n):
    return bpy.data.objects.get(n)


def decorate(kit, story, ctx):
    M = ctx["M"]
    vis = ctx["vis"]
    # me: gloves, toggles
    for sx, hid, hole in ((-1, "rglove_me", False), (1, "lglove_me", True)):
        arm = _obj(f"me.arm{sx}")
        if arm is not None:
            g = kit.box(f"me.glove{sx}", (1.05, 1.07, 0.5), (0, 0, -1.55), M["mustard"], arm, bevel=0.1)
            vis[hid] = {"objs": [g], "default": True}
    tor = _obj("me.torso")
    if tor is not None:
        for k in range(3):
            kit.box(f"me.horn{k}", (0.16, 0.07, 0.24), (0, -0.55, 1.65 - 0.5 * k), M["horn"], tor, bevel=0.03)
    # gran: glove on the left hand, glasses, plum coat
    arm = _obj("gran.arm1")
    if arm is not None:
        g = kit.box("gran.glove", (1.05, 1.07, 0.5), (0, 0, -1.55), M["mustard"], arm, bevel=0.1)
        h = kit.box("gran.gloveholes", (0.2, 0.2, 0.2), (0.45, -0.45, -1.62), kit.plastic("#2a1a08", 0.9, "glove hole"), arm)
        vis["gglove"] = {"objs": [g, h], "default": False}
    hg = _obj("gran.headg")
    if hg is not None:
        gl = round_glasses(kit, M, "gran.glasses", hg, faces.HEAD_R)
        vis["gglasses"] = {"objs": [gl], "default": True}
    plum = []
    t2 = _obj("gran.torso")
    if t2 is not None:
        plum.append(kit.box("gran.pt", (2.14, 1.14, 2.12), (0, 0, 1.0), M["plum"], t2, bevel=0.08))
        plum.append(kit.box("gran.pcol", (1.5, 1.2, 0.3), (0, 0, 1.95), M["plum"], t2, bevel=0.08))
    for sx in (-1, 1):
        a2 = _obj(f"gran.arm{sx}")
        l2 = _obj(f"gran.leg{sx}")
        if a2 is not None:
            plum.append(kit.box(f"gran.ps{sx}", (1.08, 1.1, 1.8), (0, 0, 0.25 - 0.9), M["plum"], a2, bevel=0.08))
        if l2 is not None:
            plum.append(kit.box(f"gran.pk{sx}", (1.08, 1.16, 1.5), (0, 0, -0.75), M["plum"], l2, bevel=0.08))
    vis["plum"] = {"objs": plum, "default": False}
    pink = kit.plastic("#e48aa8", 0.95, "jumper pink")
    jw = []
    jt = _obj("jumper_man.torso")
    if jt is not None:
        jw.append(kit.box("jm.jt", (2.12, 1.12, 2.1), (0, 0, 1.0), pink, jt, bevel=0.12))
    for sx in (-1, 1):
        ja = _obj(f"jumper_man.arm{sx}")
        if ja is not None:
            jw.append(kit.box(f"jm.js{sx}", (1.08, 1.1, 1.8), (0, 0, 0.25 - 0.9), pink, ja, bevel=0.12))
    vis["jumperworn"] = {"objs": jw, "default": False}
    # fog nodes
    d0 = story["look"]["fog_density"]
    fc = _lin(_hex(FOGC))
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
    cur = cs[-1]["set"] if cs else "day"
    prev = cs[-2]["set"] if len(cs) > 1 else cur
    u = 1.0
    if cs and float(cs[-1].get("dur", 0)) > 0:
        u = _ss((t - cs[-1]["t"]) / float(cs[-1]["dur"]))
    a, b = TOD[prev], TOD[cur]
    out = {}
    for k in a:
        out[k] = _mixc(_hex(a[k]), _hex(b[k]), u) if isinstance(a[k], str) else a[k] + (b[k] - a[k]) * u
    return out


def _pos_at(tl, who, t):
    s = ac.state(tl, who, t)
    return s


def _interp_cues(cs, t, keys):
    """Smoothly move between consecutive cue points (each holds the values in keys)."""
    prev = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            prev = c
            continue
        if prev is None:
            return c
        u = _ss((t - prev["t"]) / max(1e-6, c["t"] - prev["t"]))
        if c.get("snap"):
            return prev
        out = dict(prev)
        for k in keys:
            if k in prev and k in c:
                out[k] = [x + (y - x) * u for x, y in zip(prev[k], c[k])]
        return out
    return prev


def animate(kit, story, tl, t, ctx):
    bpy.context.view_layer.update()
    if not ctx["inited"]:
        decorate(kit, story, ctx)
    M = ctx["M"]
    # ---------------------------------------------------------------- light: every change is a slow ramp
    s = tod_state(tl, t)
    ctx["sun"].data.color = _lin(s["sunc"])
    ctx["fill"].data.color = _lin(s["fillc"])
    ramp, bg = ctx["sky"]
    ramp.color_ramp.elements[0].color = (*_lin(s["hor"]), 1)
    ramp.color_ramp.elements[1].color = (*_lin(s["zen"]), 1)
    bg.inputs["Strength"].default_value = s["sky"] * 0.55
    for n in ctx["fog_dens"]:
        n.inputs[1].default_value = -s["fogd"]
    for n in ctx["fog_ems"]:
        n.inputs["Strength"].default_value = s["fogb"]
    night = max(0.0, min(1.0, 1.0 - s["sky"] / 1.2))      # 0 in the day, toward 1 at night
    over = {"sun": s["sun"], "fill": s["fill"]}
    # steady lamps: off a touch in the day, full at dusk and night, ramped with the sky
    lamp = 0.25 + 1.4 * night
    for nm in kit.LIGHTS:
        if nm.startswith("town lamp"):
            over[nm] = 55.0 * lamp
    over["porch lamp"] = 110.0
    over["isl lamp"] = 260.0
    over["hall light"] = 34.0
    over["hall light2"] = 30.0
    over["bed light"] = 30.0
    over["br bulb"] = 190.0
    over["flat lamp"] = 105.0
    over["k lamp"] = 150.0
    over["k fill"] = 60.0
    over["d lamp"] = 28.0
    over["d fill"] = 55.0
    over["b lamp"] = 200.0
    over["h lamp"] = 240.0
    over["blue lamp"] = 60.0
    over["deck lamp 0"] = over["deck lamp 1"] = over["deck lamp 2"] = 90.0
    over["lounge a"] = 50.0
    over["lounge b"] = 50.0
    over["board fill"] = 220.0
    over["blue fill"] = 40.0
    over["mat lamp"] = 28.0
    over["bench fill"] = 70.0
    over["tbl lamp"] = 45.0
    over["harbour key"] = 55.0
    over["shrug key"] = 380.0
    over["shrug rim"] = 70.0
    over["window rim"] = 90.0
    over["window rim2"] = 70.0
    sb = float(_eased(_cues(tl, "sunbeam"), "v", t, 0.0))
    over["sunbeam"] = 1500.0 * sb
    # ---------------------------------------------------------------- visibility toggles
    for vid, info in ctx["vis"].items():
        cs = [c for c in _cues(tl, "vis") if c.get("id") == vid]
        c = _last(cs, t)
        on = c["on"] if c else info["default"]
        if not info["objs"]:
            continue
        top = info["objs"][0]
        while top.parent is not None:
            top = top.parent
        if top.hide_render and top.name in ("me", "gran", "jumper_man"):
            on = False
        _show(info["objs"], on)
    # ---------------------------------------------------------------- doors
    ctx["cdoor"].rotation_euler = (0, 0, math.radians(float(_eased(_cues(tl, "cdoor"), "deg", t, 0.0))))
    ctx["backdoor"].rotation_euler = (0, 0, math.radians(float(_eased(_cues(tl, "backdoor"), "deg", t, 0.0))))
    ctx["flat_door"].rotation_euler = (0, 0, math.radians(float(_eased(_cues(tl, "flatdoor"), "deg", t, 0.0))))
    # ---------------------------------------------------------------- the bench: tilt, dent, strokes, smudge, shrug
    tv = float(_eased(_cues(tl, "dent"), "v", t, 0.0))
    dy = _last(_cues(tl, "dent"), t)
    yy = (dy or {}).get("y", SEAT_Y["gran"])
    ctx["dent"].scale = (0.25 + 0.65 * tv, 0.3 + 0.7 * tv, 0.06)
    ctx["dent"].location = (0, yy - 4.0, 0.5)
    _show([ctx["dent"]], tv > 0.02)
    rv = float(_eased(_cues(tl, "rattle"), "v", t, 0.0))
    for i, kg in enumerate(ctx["keys"]):
        kg.rotation_euler = (0, math.sin(t * 13.0 + i * 1.7) * 0.06 * rv, 0)
    ctx["bench"].rotation_euler = (math.radians(3.0 * float(_eased(_cues(tl, "dent"), "tilt", t, 0.0))), 0, 0)
    _show(ctx["strokes"], bool((_last(_cues(tl, "strokes"), t) or {}).get("on")))
    _show([ctx["smudge"]], bool((_last(_cues(tl, "smudge"), t) or {}).get("on")))
    shc = [c for c in _cues(tl, "shrug")]
    c = _interp_cues(shc, t, ("pos",)) if shc else None
    if c:
        cc = dict(c)
        for k in ("u", "lean", "head", "tilt", "armfwd"):
            if k in c:
                cc[k] = _eased(shc, k, t, c[k])
        pose_shrug(ctx, cc)
    else:
        pose_shrug(ctx, {"hidden": True})
    over["shrug fill"] = 0.0
    # ---------------------------------------------------------------- seated people: legs forward, coat flaps with them
    for who, keys in tl["acting"].items():
        sit = False
        for k in keys:
            if k["t"] <= t + 1e-9 and "sit" in k:
                sit = bool(k["sit"])
        for sx in (-1, 1):
            for nm in (f"{who}.leg{sx}", f"{who}.coat{sx}"):
                ob = _obj(nm)
                if ob is not None and sit:
                    ob.rotation_euler = (-math.pi / 2, 0, 0)
    for who, keys in tl["acting"].items():
        tor = _obj(f"{who}.torso")
        if tor is not None:
            tor.rotation_euler = (0, math.radians(ac._held(keys, "roll", t, 0.0)), 0)
    # ---------------------------------------------------------------- phone: screen strength ramp, place
    pc = _last(_cues(tl, "phone"), t)
    ph = ctx["phone"]
    if pc and pc.get("on"):
        ph.location = tuple(pc.get("pos", (201.1, 0.15, 0.77)))
        ph.rotation_euler = tuple(math.radians(v) for v in pc.get("rot", (-12, 0, -20)))
    else:
        ph.location = (0, 0, -50)
    scr = _obj("phone.screen")
    glow = float(_eased(_cues(tl, "phone"), "glow", t, 0.2))
    if scr is not None:
        for sl in scr.material_slots:
            for n in sl.material.node_tree.nodes:
                if n.type == "EMISSION":
                    n.inputs["Strength"].default_value = 3.0 * glow
    # the phone bezel for the calls
    bz = _last(_cues(tl, "bezel"), t)
    _show([ctx["bezel"]], bool(bz and bz.get("on")))
    # ---------------------------------------------------------------- props by cue (smooth between points)
    for pid, ob in ctx["props"].items():
        cs = [c for c in _cues(tl, "prop") if c.get("id") == pid]
        c = _interp_cues(cs, t, ("pos", "rot")) if cs else None
        if not c or c.get("hide"):
            ob.location = (0, 0, -50)
            continue
        ob.location = tuple(c["pos"])
        r = c.get("rot", (0, 0, 0))
        ob.rotation_euler = tuple(math.radians(v) for v in r)
    # ---------------------------------------------------------------- the dog
    dg = ctx["dog"]
    dc = [c for c in _cues(tl, "dog")]
    c = _interp_cues(dc, t, ("pos", "yaw")) if dc else None
    if c and not c.get("hide"):
        yaw = c.get("yaw", [0.0])
        moving = c.get("gait", 0)
        ph_ = t * 9.0
        z0 = c["pos"][2] if len(c["pos"]) > 2 else 0.0
        dg["root"].location = (c["pos"][0], c["pos"][1], z0 + abs(math.sin(ph_)) * 0.02 * moving)
        dg["root"].rotation_euler = (0, 0, math.radians(yaw[0] if isinstance(yaw, (list, tuple)) else yaw))
        for i, lg in enumerate(dg["legs"]):
            lg.rotation_euler = (math.sin(ph_ + (math.pi if i in (1, 2) else 0)) * 0.6 * moving, 0, 0)
    else:
        dg["root"].location = (0, 0, -50)
    # ---------------------------------------------------------------- hoppers: small low hops and fading dots
    P = 0.52
    for hi, hdef in enumerate(story.get("hoppers", [])):
        ob = ctx["hoppers"][hdef["id"]]
        row = ctx["dots"][hi]
        cs = [c for c in _cues(tl, "hop") if c.get("id") == hdef["id"]]
        st = _last(cs, t)
        owner = hdef["owner"]

        def hop_pos(tt):
            so = ac.state(tl, owner, tt)
            fwd = (math.sin(so["yaw"]), -math.cos(so["yaw"]))
            side = (math.cos(so["yaw"]), math.sin(so["yaw"]))
            d, sd = hdef.get("behind", 0.7), hdef.get("side", 0.0)
            return (so["x"] - fwd[0] * d + side[0] * sd, so["y"] - fwd[1] * d + side[1] * sd), so
        if not st or not st.get("on"):
            ob.location = (0, 0, -50)
            for d in row:
                d.location = (0, 0, -50)
            continue
        (hx, hy), so = hop_pos(t)
        if so["hidden"]:
            ob.location = (0, 0, -50)
            for d in row:
                d.location = (0, 0, -50)
            continue
        ph_ = ((t + hdef.get("phase", 0.0)) % P) / P
        hz = 0.13 * abs(math.sin(math.pi * ph_))
        ob.location = (hx, hy, hz)
        ob.rotation_euler = (0, 0, so["yaw"] + math.radians(hdef.get("turn", 0)))
        n0 = math.floor((t + hdef.get("phase", 0.0)) / P)
        for j, d in enumerate(row):
            tl_ = (n0 - j) * P - hdef.get("phase", 0.0)
            if tl_ < st["t"] or t - tl_ > 1.3:
                d.location = (0, 0, -50)
                continue
            (dx, dy), _ = hop_pos(tl_)
            f = max(0.05, 1.0 - (t - tl_) / 1.3)
            d.location = (dx, dy, 0.012)
            d.scale = (f, f, 1.0)
    # the town's faint hop-dots under my feet (a cue sets their strength)
    lv = float(_eased(_cues(tl, "mdots"), "v", t, 0.0))
    for k, d in enumerate(ctx["mdots"]):
        sc = lv * (1.0 - 0.05 * k)
        d.scale = (max(0.01, sc), max(0.01, sc), 1.0)
        d.hide_render = lv < 0.02
    return over
