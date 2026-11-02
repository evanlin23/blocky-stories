"""The Face-Chest and the barber chairs it sits in (imported by set.py; runs inside Blender's Python).

Local frame for both: facing -y, the floor z = 0, the seat's top z = 0.55, the chair's pedestal at the origin.
The creature is an ordinary seated R6 body under a full barber's cape in teal and cream stripes, with the cape's high
round collar closing on nothing (flat black inside). Its face is drawn large on a cream bib panel on its chest.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from blocky import kit  # noqa: E402

SEAT_TOP = 0.55
TEAL, CREAM = "#2a8c8c", "#efe6d2"
PANEL_W, PANEL_H, PANEL_Z = 0.80, 0.64, 0.86

# the cape's loft: (z, half width, front reach, back reach, squareness)
CAPE = [(1.30, 0.29, 0.26, 0.26, 2.0),
        (1.26, 0.48, 0.32, 0.22, 3.0),
        (1.215, 0.60, 0.40, 0.26, 5.0),
        (1.05, 0.62, 0.435, 0.27, 6.0),
        (0.80, 0.64, 0.435, 0.27, 6.0),
        (0.56, 0.66, 0.44, 0.27, 5.0),
        (0.50, 0.68, 0.64, 0.27, 4.0),
        (0.43, 0.68, 0.78, 0.27, 3.5)]


# ------------------------------------------------------------------------------------------------ the face
def face_pil(opened: bool):
    """The chest face and its highlight mask (white where the glints are, so they can glow). Two big round eyes with
    heavy black rims, set wide, small dead-centre pupils, thin flat brows and a long flat mouth. Opened: a tall dark
    mouth onto black, nothing in it."""
    W = 1024
    H = int(W * PANEL_H / PANEL_W)
    rng = np.random.default_rng(4)
    im = Image.new("RGB", (W, H), (226, 218, 198))
    a = np.asarray(im).astype(np.float32) + rng.normal(0, 3.0, (H, W, 3))
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    hl = Image.new("RGB", (W, H), (0, 0, 0))
    d, dh = ImageDraw.Draw(im), ImageDraw.Draw(hl)
    ink = (8, 7, 8)
    ey = 0.33 * H
    rx = 0.125 * W
    # the hollows under the eyes: a tired grey, so the stare is not friendly
    sh = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(sh)
    for side in (-1, 1):
        cx = W / 2 + side * 0.26 * W
        sd.ellipse([cx - 0.17 * W, ey - 0.08 * W, cx + 0.17 * W, ey + 0.20 * W], fill=135)
    sh = sh.filter(ImageFilter.GaussianBlur(0.04 * W))
    im = Image.composite(Image.new("RGB", (W, H), (84, 86, 92)), im, sh)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(42, 140, 140), width=int(0.014 * W))      # teal piping round the bib
    for side in (-1, 1):
        cx = W / 2 + side * 0.26 * W
        d.ellipse([cx - rx, ey - rx, cx + rx, ey + rx], fill=(228, 227, 216), outline=ink, width=int(0.036 * W))
        pr = 0.080 * W
        px, py = cx - side * 0.002 * W, ey + 0.006 * W
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(3, 3, 4))
        r = 0.011 * W
        x, y = px + 0.027 * W, py - 0.029 * W
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))
        dh.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))
        # a heavy lid: the top of each eye cut flat, so the stare is hooded
        lid = ey - rx * 0.62
        d.polygon([(cx - rx - 8, ey - rx - 12), (cx + rx + 8, ey - rx - 12), (cx + rx + 8, lid + side * 0.0), (cx - rx - 8, lid)],
                  fill=(226, 218, 198))
        d.line([(cx - rx * 0.8, lid), (cx + rx * 0.8, lid)], fill=ink, width=int(0.03 * W))
        by = lid - 0.045 * W
        d.line([(cx - 0.14 * W, by + 0.008 * W * side), (cx + 0.14 * W, by - 0.008 * W * side)], fill=ink, width=int(0.012 * W))
    my = 0.845 * H
    if not opened:
        d.line([(W / 2 - 0.40 * W, my), (W / 2 + 0.40 * W, my)], fill=ink, width=int(0.014 * W))
    else:
        top, bot = 0.45 * H, 1.0 * H
        rx2 = 0.125 * W
        for k, c in ((0, (30, 24, 26)), (1, (14, 11, 12)), (2, (4, 3, 4)), (3, (0, 0, 0))):
            inset = k * 0.012 * W
            d.rounded_rectangle([W / 2 - rx2 + inset, top + inset * 1.3, W / 2 + rx2 - inset, bot - inset * 0.5], radius=rx2 - inset,
                                fill=c)
    im = im.filter(ImageFilter.GaussianBlur(0.7))
    return im, hl


def _img(name, pil):
    img = bpy.data.images.new(name, pil.width, pil.height, alpha=False)
    a = np.asarray(pil.convert("RGBA")).astype(np.float32)[::-1] / 255
    img.pixels.foreach_set(a.ravel())
    img.pack()
    return img


# ------------------------------------------------------------------------------------------------ materials
def striped(name="cape stripes"):
    """Vertical teal and cream stripes in object space (0.07 m each), satin."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.55
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 7.15
    nt.links.new(sep.outputs["X"], mul.inputs[0])
    fr = nt.nodes.new("ShaderNodeMath")
    fr.operation = "FRACT"
    nt.links.new(mul.outputs[0], fr.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = kit.col(TEAL)
    ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements[1].color = kit.col(CREAM)
    nt.links.new(fr.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m


def face_material():
    """The bib: the face image as colour, the glints as emission. Returns (material, colour node, glint node)."""
    m = kit._new("chest face")
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.6
    uvn = nt.nodes.new("ShaderNodeUVMap")
    t1 = nt.nodes.new("ShaderNodeTexImage")
    t2 = nt.nodes.new("ShaderNodeTexImage")
    for t in (t1, t2):
        t.interpolation = "Linear"
        nt.links.new(uvn.outputs["UV"], t.inputs["Vector"])
    nt.links.new(t1.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(t2.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 6.0
    kit._fogged(m, b.outputs[0])
    return m, t1, t2


# ------------------------------------------------------------------------------------------------ the creature
def _loft(name, rings, mat, parent, n=48):
    verts, faces = [], []
    for z, hx, yf, yb, e in rings:
        for j in range(n):
            th = 2 * math.pi * j / n
            c, s = math.cos(th), math.sin(th)
            x = hx * math.copysign(abs(c) ** (2 / e), c)
            y = (-yf if s < 0 else yb) * abs(s) ** (2 / e)
            fold = 0.016 * math.sin(7 * th + z * 3.0) * min(1.0, max(0.0, (abs(c) - 0.55) * 2.5 if s < 0 else 1.0))
            x, y = x * (1 + fold), y * (1 + fold)
            verts.append((x, y, z))
    for i in range(len(rings) - 1):
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            faces.append((a, a + n, b + n, b))   # outward for rings listed top to bottom
    ob = kit.mesh_obj(name, verts, faces, mat, parent, smooth=True)
    return ob


def build_creature(M):
    """The Face-Chest. Returns a dict: root (an empty at the chair's pedestal, facing -y), parts (every object), the face
    material's nodes and the two face images."""
    root = kit.empty("creature", (0, 0, 0))
    parts = []
    cape_m = striped()
    teal = kit.plastic(TEAL, 0.55, "cape teal")
    cape = _loft("creature.cape", CAPE, cape_m, root)
    # flip the winding so the faces point out (rings run top to bottom)
    parts.append(cape)
    # the high round collar: a tube, open at the top, with a flat black floor just under the rim
    n = 40
    ro, ri, z0, z1 = 0.30, 0.265, 1.27, 1.36
    verts, faces = [], []
    for z, r in ((z0, ro), (z1, ro), (z1, ri), (z0 + 0.02, ri)):
        for j in range(n):
            a = 2 * math.pi * j / n
            verts.append((r * math.cos(a), r * math.sin(a), z))
    for i in range(3):
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            faces.append((a, b, b + n, a + n))
    col = kit.mesh_obj("creature.collar", verts, faces, striped(), root, smooth=True)
    parts.append(col)
    parts.append(kit.cyl("creature.collar.floor", ri + 0.002, 0.012, (0, 0, 1.315), kit.plastic("#010101", 0.9, "void", 0.0), root, n=40))
    # a plain dark-brown boot under the hem each side, and the trouser shin above it
    boot = kit.plastic("#2e1b10", 0.5, "boot")
    trou = kit.plastic("#16161a", 0.8, "trousers")
    for sx in (-1, 1):
        parts.append(kit.box(f"creature.shin{sx}", (0.17, 0.17, 0.30), (sx * 0.19, -0.70, 0.31), trou, root, bevel=0.03))
        parts.append(kit.box(f"creature.boot{sx}", (0.19, 0.34, 0.13), (sx * 0.19, -0.80, 0.235), boot, root, bevel=0.04))
    # the bib with the face on it
    fm, t1, t2 = face_material()
    x, z0p, z1p = PANEL_W / 2, PANEL_Z - PANEL_H / 2, PANEL_Z + PANEL_H / 2
    y = -(0.4385)
    panel = kit.mesh_obj("creature.face", [(-x, y, z0p), (x, y, z0p), (x, y, z1p), (-x, y, z1p)], [(0, 1, 2, 3)], fm, root)
    uv = panel.data.uv_layers.new(name="UVMap")
    for p in panel.data.polygons:
        for li in p.loop_indices:
            uv.data[li].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][panel.data.loops[li].vertex_index]
    frame = panel
    parts += [panel]
    imgs = {}
    for opened in (False, True):
        c, h = face_pil(opened)
        imgs[opened] = (_img(f"face {opened}", c), _img(f"glint {opened}", h))
    t1.image, t2.image = imgs[False]
    return {"root": root, "parts": parts + list(root.children_recursive), "t1": t1, "t2": t2, "imgs": imgs, "bib": frame}


def set_mouth(cr, opened: bool):
    cr["t1"].image, cr["t2"].image = cr["imgs"][bool(opened)]


# ------------------------------------------------------------------------------------------------ the chairs
def build_chair(name, M, tally=False, waiting=False):
    """A barber chair (or a plain waiting chair) at the origin facing -y. Returns (root, swivel, parts): the swivel empty turns
    the seat, back, arms and footplate round the pedestal."""
    root = kit.empty(f"{name}", (0, 0, 0))
    sw = kit.empty(f"{name}.swivel", (0, 0, 0), root)
    leather, chrome, wood = M["leather"], M["chrome"], M["wood"]
    parts = []
    if not waiting:
        parts += [kit.cyl(f"{name}.disc", 0.30, 0.04, (0, 0, 0.02), chrome, root, n=28),
                  kit.cyl(f"{name}.column", 0.07, 0.42, (0, 0, 0.24), chrome, root, n=16),
                  kit.cyl(f"{name}.collar", 0.12, 0.05, (0, 0, 0.42), chrome, root, n=20)]
        parts += [kit.box(f"{name}.seat", (0.82, 0.70, 0.12), (0, 0, 0.49), leather, sw, bevel=0.04),
                  kit.box(f"{name}.back", (0.76, 0.12, 0.82), (0, 0.37, 0.96), leather, sw, bevel=0.04),
                  kit.box(f"{name}.head", (0.34, 0.10, 0.22), (0, 0.37, 1.33), leather, sw, bevel=0.04),
                  kit.box(f"{name}.neck", (0.05, 0.05, 0.14), (0, 0.37, 1.25), chrome, sw)]
        for sx in (-1, 1):
            parts += [kit.box(f"{name}.arm{sx}", (0.09, 0.58, 0.05), (sx * 0.50, -0.02, 0.78), leather, sw, bevel=0.02),
                      kit.box(f"{name}.armpost{sx}", (0.05, 0.05, 0.25), (sx * 0.50, 0.22, 0.65), chrome, sw)]
        parts += [kit.box(f"{name}.foot", (0.52, 0.30, 0.03), (0, -0.92, 0.17), chrome, sw, bevel=0.01),
                  kit.box(f"{name}.footarm", (0.07, 0.62, 0.03), (0, -0.55, 0.19), chrome, sw),
                  kit.box(f"{name}.footpost", (0.06, 0.06, 0.30), (0, -0.30, 0.36), chrome, sw)]
        if tally:
            tm = kit.emit(TEAL, 1.6, "tally teal")
            for k in (-1, 0, 1):
                parts.append(kit.box(f"{name}.tally{k}", (0.016, 0.20, 0.003), (k * 0.07, -0.92, 0.1535), tm, sw))
    else:
        parts += [kit.box(f"{name}.seat", (0.50, 0.50, 0.06), (0, 0, 0.52), wood, sw, bevel=0.015),
                  kit.box(f"{name}.back", (0.50, 0.05, 0.50), (0, 0.24, 0.80), wood, sw, bevel=0.015)]
        for sx in (-1, 1):
            for sy in (-1, 1):
                parts.append(kit.box(f"{name}.leg{sx}{sy}", (0.05, 0.05, 0.50), (sx * 0.21, sy * 0.21, 0.25), wood, sw))
    return root, sw, parts
