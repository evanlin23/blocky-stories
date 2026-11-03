"""Night Mower (batch 6, P3): a bright cul-de-sac, Mr. Odell's floodlit striped lawn, and the Head under it.
Built from kit.py's parts and CC0 props (trees, bushes, flowers, bed, desk lamp, planter, path stones, trash cans).
No text anywhere: no lettering, numbers, signs or logos (the bedside clock shows digits only).

The places (metres, the ground is z = 0), shared with generator/make_story.py:
- the street y -4 .. 4 along x, our sidewalk y 4 .. 5.2, the yards y 5.2 .. 12
- our yard x -15 .. -0.2 with the bald circle at (-2.6, 8.4), the low fence at x = 0
- Mr. Odell's lawn x 0.2 .. 15 (a grid mesh with a low oval hump at HC), his mint house behind it, four floodlights
- THE HEAD: the lens-shaped patch of the lawn around HC is a separate lid (same stripes, hinged on its north edge).
  Under it, a shallow pit with ONE flat drawn eye (our own face style: off-white almond, thick black lid stroke, a huge
  rounded-square black pupil, one warm highlight). Three eye drawings are swapped by the "eye" track: 0 looks up, 1 at
  our porch (Dad), 2 at the lens. The lid's angle is the "lid" track (0 shut and flush, 1 open about 62 degrees).
- our butter-yellow house x -14 .. -4: the bedroom upstairs (floor z 2.8) with its window at x = -6, the porch
- the south houses (front wall y = -9), the coral one leaning 6 degrees toward his lawn
- the hall at x = 100 and the bedside clock at x = 130, each a little box room

story.json "tracks" (resolved here) drive: lid, eye, meter, pic (hall pictures), mail, chair, slat, sway, binos, sod,
sprink, hose, bw0 to bw2 (the south blinds). story.json "looks" gives each shot's "day" (0 night, 1 day, between: dawn).
"""

from __future__ import annotations

import hashlib
import math
import tempfile
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector as V
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from blocky import acting, timeline

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TMP = Path(tempfile.gettempdir()) / "night-mower-tex"
TMP.mkdir(parents=True, exist_ok=True)

HC = (7.2, 8.6)                  # the hump's and the lid's centre
HUMP_A, HUMP_B, HUMP_H = 3.6, 2.1, 0.3
LA, LB = 2.7, 1.5                # the lid's lens: half-length along x, half-depth along y
LAWN = (0.2, 15.0, 5.2, 12.0)    # Mr. Odell's lawn x0, x1, y0, y1
RES = 0.1
EYE_Z = -0.22
EW, EH = 5.6, 3.2                # the eye drawing's size
BALD = (-2.6, 8.4)
Z2 = 2.8
HX = 100.0                       # the hall
BX = 130.0                       # the bedside
MOWER_OFF = 1.45                 # the mower's centre this far in front of Mr. Odell
PORCH_ANCHOR = (9.6, 11.9)       # where the orange cord is plugged in

LIME = "#b6ff3b"


def hump(x, y):
    r2 = ((x - HC[0]) / HUMP_A) ** 2 + ((y - HC[1]) / HUMP_B) ** 2
    return HUMP_H * max(0.0, 1.0 - r2) ** 1.2


# ------------------------------------------------------------------------------------------------ materials
def pil_image(name, im: Image.Image):
    h = hashlib.md5(im.tobytes()).hexdigest()[:10]
    path = TMP / f"{name}-{h}.png"
    if not path.exists():
        im.save(path)
    img = bpy.data.images.load(str(path), check_existing=True)
    img.colorspace_settings.name = "sRGB"
    return img


def image_mat(kit, name, im, rough=0.85, emit=0.0, turf=False, pale="#d4ae72", under=None):
    """A drawing as a material. turf=True shows `pale` plastic on the underside (the lid's warm underside)."""
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = pil_image(name, im)
    tex.interpolation = "Linear"
    col = tex.outputs["Color"]
    if turf:
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        nt.links.new(geo.outputs["Backfacing"], mx.inputs["Factor"])
        nt.links.new(col, mx.inputs["A"])
        if under is not None:      # the underside is the same rings in warm pale plastic
            ut = nt.nodes.new("ShaderNodeTexImage")
            ut.image = pil_image(name + " under", under)
            nt.links.new(ut.outputs["Color"], mx.inputs["B"])
            ucol = ut.outputs["Color"]
        else:
            mx.inputs["B"].default_value = kit.col(pale)
            ucol = None
        col = mx.outputs["Result"]
        em = nt.nodes.new("ShaderNodeMix")
        em.data_type = "RGBA"
        nt.links.new(geo.outputs["Backfacing"], em.inputs["Factor"])
        em.inputs["A"].default_value = (0, 0, 0, 1)
        if ucol is not None:
            nt.links.new(ucol, em.inputs["B"])
        else:
            em.inputs["B"].default_value = kit.col(pale)
        nt.links.new(em.outputs["Result"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = 0.3
    nt.links.new(col, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = 0.15
            break
    if emit > 0:
        nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    kit._fogged(m, b.outputs[0])
    return m


def lawn_image(pale=False):
    """The stripes: long rings round the hump, light and dark, like hair combed over a brow."""
    x0, x1, y0, y1 = LAWN
    w, h = 2220, 1080
    xs = x0 + (np.arange(w) + 0.5) / w * (x1 - x0)
    ys = y1 - (np.arange(h) + 0.5) / h * (y1 - y0)
    X, Y = np.meshgrid(xs, ys)
    r = np.hypot((X - HC[0]) / 6.2, (Y - HC[1]) / 2.3)
    band = np.floor(r * 7.0).astype(int)
    light = np.array([60, 238, 104], np.float32)
    dark = np.array([34, 196, 76], np.float32)
    if pale:
        light = np.array([236, 205, 150], np.float32)
        dark = np.array([204, 164, 108], np.float32)
    im = np.where((band % 2 == 0)[..., None], light, dark).astype(np.float32)
    rng = np.random.default_rng(5)
    n = rng.normal(0, 1, (h // 3, w // 3)).astype(np.float32)
    n = np.asarray(Image.fromarray(((n * 0.25 + 0.5).clip(0, 1) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32) / 255 - 0.5
    im *= (1.0 + n * 0.16)[..., None]
    # a fine edge line where one band meets the next, so the rings read as mown lines
    edge = np.abs((r * 7.0) % 1.0 - 0.5) > 0.47
    im[edge] *= 0.93
    return Image.fromarray(im.clip(0, 255).astype(np.uint8))


def eye_image(look):
    """The Head's eye, flat and drawn like our faces: an off-white almond ringed by a thick black lid stroke, a huge
    rounded-square black pupil and one warm highlight (the brightest thing in its frames)."""
    s = 200
    w, h = int(EW * s), int(EH * s)
    im = Image.new("RGB", (w, h), (36, 26, 20))
    d = ImageDraw.Draw(im)
    cx, cy = w / 2, h / 2
    A, B = 2.72 * s, 1.5 * s

    def almond(scale, grow=0.0):
        pts = []
        n = 90
        for i in range(n + 1):
            u = -1 + 2 * i / n
            pts.append((cx + u * A * scale, cy - (B * scale + grow) * (1 - u * u) ** 0.8))
        for i in range(n, -1, -1):
            u = -1 + 2 * i / n
            pts.append((cx + u * A * scale, cy + (B * scale + grow) * (1 - u * u) ** 0.8))
        return pts

    d.polygon(almond(1.0, 0), fill=(11, 11, 15))                       # the thick lid stroke
    d.polygon(almond(0.955, -26), fill=(238, 232, 212))                 # the white
    px, py, hl = {0: (0, -6, 0), 1: (-150, -14, 1), 2: (6, 46, 2)}[look]
    pr = 1.0 * s                                                        # the pupil's half side: 2 m across
    d.rounded_rectangle((cx + px - pr, cy + py - pr * 0.96, cx + px + pr, cy + py + pr * 0.96), radius=int(0.5 * s),
                        fill=(11, 11, 15))
    d.rounded_rectangle((cx + px - pr * 1.0, cy + py - pr * 0.96, cx + px + pr * 1.0, cy + py + pr * 0.96),
                        radius=int(0.5 * s), fill=(86, 40, 20))        # a dark amber iris ring, so it reads as an eye
    pr *= 0.8
    d.rounded_rectangle((cx + px - pr, cy + py - pr * 0.96, cx + px + pr, cy + py + pr * 0.96), radius=int(0.4 * s),
                        fill=(11, 11, 15))
    if hl == 0:
        hx, hy, hs = cx + px - 0.36 * s, cy + py - 0.38 * s, 0.17 * s
    elif hl == 1:
        hx, hy, hs = cx + px - 0.34 * s, cy + py - 0.34 * s, 0.17 * s
    else:
        hx, hy, hs = cx + px - 0.18 * s, cy + py - 0.1 * s, 0.2 * s
    d.rounded_rectangle((hx - hs, hy - hs, hx + hs, hy + hs), radius=int(hs * 0.45), fill=(255, 246, 220))
    d.rounded_rectangle((cx + px + 0.3 * s, cy + py + 0.34 * s, cx + px + 0.42 * s, cy + py + 0.46 * s), radius=8,
                        fill=(255, 246, 220))
    # a heavy upper lid: a flat warm lid pressed down over the top of the eye, slanted, with its own thick stroke
    ly0, ly1 = cy - 0.50 * B, cy - 0.34 * B
    lid_poly = [(cx - A * 1.05, cy - B * 1.4), (cx + A * 1.05, cy - B * 1.4), (cx + A * 1.05, ly1), (cx - A * 1.05, ly0)]
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).polygon(almond(0.955, -26), fill=255)
    lidim = Image.new("RGB", im.size, (240, 216, 168))
    ld = ImageDraw.Draw(lidim)
    ld.line((cx - A * 1.05, ly0, cx + A * 1.05, ly1), fill=(11, 11, 15), width=int(0.16 * s))
    cut = Image.new("L", im.size, 0)
    ImageDraw.Draw(cut).polygon(lid_poly, fill=255)
    from PIL import ImageChops
    im.paste(lidim, (0, 0), ImageChops.multiply(mask, cut))
    d = ImageDraw.Draw(im)
    # two thick lashes at the outer end, like a drawn eye
    for sx in (-1, 1):
        for k, ang in enumerate((-0.22, 0.05)):
            x0, y0 = cx + sx * A * 0.93, cy - B * 0.34 - k * 22
            d.line((x0, y0, x0 + sx * 0.36 * s, y0 - 0.22 * s + ang * s * 0.4), fill=(11, 11, 15), width=int(0.13 * s))
    return im


def clock_image():
    im = Image.new("RGB", (560, 280), (20, 6, 8))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(str(ROOT / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"), 210)
    tw = d.textlength("3:00", font=f)
    d.text(((560 - tw) / 2, 18), "3:00", font=f, fill=(255, 52, 40))
    return im


def mats(kit):
    P = kit.plastic
    M = {
        "yellow": P("#ffd970", 0.5), "cream": P("#fff0c8", 0.6), "white": P("#f4f1e8", 0.45), "roof": P("#2f8f9a", 0.5),
        "dark": P("#26262c", 0.5), "wood": P("#8a5a34", 0.6), "red": P("#ff3b30", 0.35, spec=0.6),
        "red_d": P("#c42a22", 0.4), "black": P("#141418", 0.5), "chrome": kit.metal("#cfd3d8", 0.25),
        "orange": P("#ff9a1f", 0.45), "lime": kit.emit(LIME, 0.9), "soil": P("#2b1c14", 0.95),
        "tan": P("#c49a5c", 0.95), "pole": P("#8a8f99", 0.4), "warm": kit.emit("#fff1c2", 6.0),
        "glass": kit.emit("#ffd9a0", 1.1), "glow": kit.emit("#7dff98", 2.4), "conc": kit.texture("concrete", 1.0, tint="#d8d6d0"),
        "asphalt": kit.texture("asphalt", 0.5, tint="#8a8f9a"), "ours": P("#6cc24a", 0.9, spec=0.1),
        "ground": P("#4f9a3f", 0.95), "floor": kit.texture("wood", 0.7, tint="#d9b98a"), "bed": P("#1fb5a8", 0.6),
        "bulb": kit.emit("#fff6dc", 2.2), "level": P("#ffd23a", 0.4), "vial": P("#b6ff3b", 0.2, spec=0.7),
        "bubble": P("#ffffff", 0.2), "water": kit.emit("#bfe6ff", 0.8), "seed": P("#e8d9a8", 0.9),
        "sod": P("#7ccf3c", 0.9), "sod_y": P("#d8c84a", 0.9), "fence": P("#f4f1e8", 0.5), "mint": P("#8fe3c8", 0.5),
        "pic1": P("#4fb3ff", 0.6), "pic2": P("#ff8a3c", 0.6), "pic3": P("#e7458a", 0.6), "pic4": P("#b6ff3b", 0.6),
        "pic5": P("#fff1c2", 0.6),
    }
    M["lawn"] = image_mat(kit, "odell lawn", lawn_image(), 0.9, turf=True, under=lawn_image(True))
    for k in range(3):
        M[f"eye{k}"] = image_mat(kit, f"eye {k}", eye_image(k), 0.7, emit=0.22)
    M["clock"] = image_mat(kit, "clock", clock_image(), 0.4, emit=2.2)
    return M


# ------------------------------------------------------------------------------------------------ small helpers
def quad_uv(kit, name, size, loc, mat, uv=None):
    """A flat quad facing +z with UVs (0,0)-(1,1)."""
    x, y = size[0] / 2, size[1] / 2
    ob = kit.mesh_obj(name, [(-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0)], [(0, 1, 2, 3)], mat, None, loc)
    uvl = ob.data.uv_layers.new(name="uv")
    for lp in ob.data.loops:
        v = ob.data.vertices[lp.vertex_index].co
        uvl.data[lp.index].uv = (v.x / size[0] + 0.5, v.y / size[1] + 0.5)
    return ob


BOUNDARY: set = set()


def snap(i, j):
    """A grid vertex's place. Vertices on the lid's outline move onto the lens's ellipse, so its edge is smooth; the lawn
    mesh, the lid and the pit walls all call this, so they meet exactly."""
    x, y = LAWN[0] + i * RES, LAWN[2] + j * RES
    if (i, j) in BOUNDARY:
        q = math.sqrt(((x - HC[0]) / LA) ** 2 + ((y - HC[1]) / LB) ** 2)
        if q > 1e-6:
            x, y = HC[0] + (x - HC[0]) / q, HC[1] + (y - HC[1]) / q
    return x, y


def tex_grid(kit, name, cells, mat, origin, uv_fn, wall_mat=None):
    """A mesh of grid cells (each (ix, iy)), vertices lifted by hump(), UVs from world x y. Returns the object."""
    ox, oy, z0 = origin
    vid, verts, faces = {}, [], []

    def vtx(i, j):
        if (i, j) not in vid:
            x, y = snap(i, j)
            vid[(i, j)] = len(verts)
            verts.append((x - ox, y - oy, hump(x, y) - z0))
        return vid[(i, j)]

    for (i, j) in cells:
        faces.append((vtx(i, j), vtx(i + 1, j), vtx(i + 1, j + 1), vtx(i, j + 1)))
    ob = kit.mesh_obj(name, verts, faces, mat, None, (ox, oy, z0), smooth=True)
    uvl = ob.data.uv_layers.new(name="uv")
    for lp in ob.data.loops:
        v = ob.data.vertices[lp.vertex_index].co
        uvl.data[lp.index].uv = uv_fn(v.x + ox, v.y + oy)
    return ob


def build_lawn_and_lid(kit, ctx, M):
    nx = int(round((LAWN[1] - LAWN[0]) / RES))
    ny = int(round((LAWN[3] - LAWN[2]) / RES))
    inside, outside = [], []
    for i in range(nx):
        for j in range(ny):
            x, y = LAWN[0] + (i + 0.5) * RES, LAWN[2] + (j + 0.5) * RES
            if ((x - HC[0]) / LA) ** 2 + ((y - HC[1]) / LB) ** 2 < 1.0:
                inside.append((i, j))
            else:
                outside.append((i, j))
    ins = set(inside)
    BOUNDARY.clear()
    for (i, j) in inside:
        for a in (0, 1):
            for b in (0, 1):
                if any((i + a + da, j + b + db) not in ins and 0 <= i + a + da < nx and 0 <= j + b + db < ny
                       for da in (-1, 0) for db in (-1, 0)):
                    BOUNDARY.add((i + a, j + b))
    uv = lambda x, y: ((x - LAWN[0]) / (LAWN[1] - LAWN[0]), (y - LAWN[2]) / (LAWN[3] - LAWN[2]))
    tex_grid(kit, "lawn", outside, M["lawn"], (0.0, 0.0, 0.0), uv)
    hy = HC[1] + LB
    zh = hump(HC[0], hy)
    lid = tex_grid(kit, "lid", inside, M["lawn"], (HC[0], hy, zh), uv)
    ctx["lid"] = lid
    # the pit: walls round the lid's outline, down to the eye
    verts, faces = [], []
    for (i, j) in inside:
        for di, dj, a, b in ((-1, 0, (i, j), (i, j + 1)), (1, 0, (i + 1, j + 1), (i + 1, j)),
                             (0, -1, (i + 1, j), (i, j)), (0, 1, (i, j + 1), (i + 1, j + 1))):
            if (i + di, j + dj) in ins:
                continue
            p = []
            for (ii, jj) in (a, b):
                x, y = snap(ii, jj)
                p.append((x, y, hump(x, y)))
            n = len(verts)
            verts += [(p[0][0], p[0][1], p[0][2] - 0.004), (p[1][0], p[1][1], p[1][2] - 0.004),
                      (p[1][0], p[1][1], EYE_Z), (p[0][0], p[0][1], EYE_Z)]
            faces.append((n, n + 1, n + 2, n + 3))
    kit.mesh_obj("pit", verts, faces, M["soil"], None, (0, 0, 0))
    ctx["eyes"] = []
    for k in range(3):
        ob = quad_uv(kit, f"eye{k}", (EW, EH), (HC[0], HC[1], EYE_Z), M[f"eye{k}"])
        ctx["eyes"].append(ob)
    # a dark floor under the eye drawing (keeps the pit from showing the ground through a gap)
    kit.box("pitfloor", (EW + 0.4, EH + 0.4, 0.05), (HC[0], HC[1], EYE_Z - 0.06), M["soil"])


# ------------------------------------------------------------------------------------------------ the street and yards
def build_ground(kit, ctx, M):
    kit.plane("base", (400, 400), (0, 0, -0.25), M["ground"])
    kit.box("street", (120, 8, 0.2), (0, 0, -0.1), M["asphalt"])
    for y in (4.6, -4.6):
        kit.box(f"walk{y}", (120, 1.2, 0.14), (0, y, -0.02), M["conc"])
    for k in range(-5, 6):   # lane dashes
        kit.box(f"dash{k}", (2.0, 0.16, 0.012), (k * 6.0, 0.0, 0.006), M["white"])
    kit.box("ourlawn", (14.8, 6.8, 0.2), (-7.6, 8.6, -0.1), M["ours"])
    kit.box("farlawn", (80, 3.8, 0.2), (-45.0, 8.6, -0.1), M["ours"])
    kit.box("farlawn2", (60, 3.8, 0.2), (45.0, 8.6, -0.1), M["ours"])
    kit.box("backlawn", (120, 18, 0.2), (0, 21.0, -0.1), M["ours"])
    kit.box("southlawn", (120, 14, 0.2), (0, -12.0, -0.1), M["ours"])
    kit.cyl("bald", 1.2, 0.04, (BALD[0], BALD[1], 0.02), M["tan"], n=48)
    kit.box("fencestrip", (0.4, 6.8, 0.04), (0.0, 8.6, 0.02), M["conc"])


def build_fence(kit, ctx, M):
    y0, y1 = 5.3, 11.9
    n = 8
    for k in range(n + 1):
        y = y0 + (y1 - y0) * k / n
        kit.box(f"fpost{k}", (0.1, 0.1, 0.62), (0.0, y, 0.35), M["fence"], bevel=0.015)
    for z in (0.28, 0.5):
        kit.box(f"frail{z}", (0.05, y1 - y0, 0.07), (0.0, (y0 + y1) / 2, z + 0.04), M["fence"], bevel=0.01)


def build_floods(kit, ctx, M):
    ctx["floods"] = []
    for k, (x, y) in enumerate(((0.9, 5.6), (14.2, 5.6), (0.9, 11.6), (14.2, 11.6))):
        kit.cyl(f"pole{k}", 0.06, 4.6, (x, y, 2.3), M["pole"], n=10)
        head = kit.box(f"head{k}", (0.55, 0.3, 0.28), (x, y, 4.7), M["pole"], bevel=0.02)
        kit.box(f"lamp{k}", (0.46, 0.04, 0.2), (x + (0.17 if x < 7 else -0.17) * 0.0, y + (0.16 if y < 8 else -0.16), 4.7),
                M["warm"])
        L = kit.light(f"flood{k}", "SPOT", (x, y, 4.6), 1400.0, "#fff1c2", size=0.35, spot=95, blend=0.7)
        kit.aim(L, (HC[0], HC[1] - 0.5, 0.0))
        ctx["floods"].append(f"flood{k}")


def build_trees(kit, ctx, M):
    for k, (x, y) in enumerate(((-17, 6.5), (-12.5, 22.5), (18.5, 7.0), (22.0, 15.0), (-19, 14.0), (3.0, 26.0),
                                (-24, 8), (26, 9), (12, 24))):
        kit.prop("sub_tree_large" if k % 2 else "sub_tree_small", (x, y, 0), rot=k * 37, scale=1.4)
    for k, (x, y) in enumerate(((-16, -6), (-3, -6.5), (11, -6.2), (20, -6.5), (-24, -7))):
        kit.prop("sub_tree_large" if k % 2 == 0 else "sub_tree_small", (x, y, 0), rot=k * 53, scale=1.4)
    for k, (x, y) in enumerate(((-4.4, 5.9), (13.6, 5.9), (-13.5, 5.9))):
        kit.prop("trashcan_cylindric", (x, y, 0), rot=k * 20, height=0.95)


def build_mailboxes(kit, ctx, M):
    ctx["mail"] = []
    cols = ["#ff5a4f", "#4fb3ff", "#ffd23a", "#b6ff3b", "#e7458a", "#ff9a1f", "#8f7bff"]
    for k, x in enumerate((-14.0, -10.5, -6.0, -1.8)):
        root = kit.empty(f"mbox{k}", (x, 5.0, 0.05))
        kit.box(f"mpost{k}", (0.1, 0.1, 1.0), (0, 0, 0.5), M["wood"], root)
        kit.box(f"mbox_body{k}", (0.3, 0.5, 0.26), (0, 0, 1.12), kit.plastic(cols[k % len(cols)], 0.4), root, bevel=0.05)
        kit.box(f"mflag{k}", (0.04, 0.16, 0.04), (0.17, 0.1, 1.2), M["red"], root)
        ctx["mail"].append((root, x))


def build_odell_house(kit, ctx, M):
    kit.prop("sub_building_type_c", (9.8, 14.95, 0), tint="#9ff0d6")
    kit.prop("sub_planter", (7.2, 12.5, 0), rot=0)
    kit.prop("flowers", (11.6, 11.6, 0), scale=0.9)
    kit.prop("bush_1", (13.4, 12.3, 0), scale=0.7)
    kit.prop("bush_2", (5.4, 12.4, 0), scale=0.6)
    for k, y in enumerate((11.2, 9.4, 7.6, 5.9)):
        kit.prop("sub_path_stones_long", (9.5, y - 0.9, 0), rot=90)


# ------------------------------------------------------------------------------------------------ the south houses
def window(kit, M, root, name, cx, z, w, h, blind):
    """A window on a house root whose front face is local y = 0 facing +y: glass, white frame, a stack of blind slats."""
    kit.box(f"{name}.glass", (w, 0.03, h), (cx, 0.03, z), M["glass"], root)
    for sx in (-1, 1):
        kit.box(f"{name}.fr{sx}", (0.09, 0.09, h + 0.1), (cx + sx * (w / 2 + 0.03), 0.055, z), M["white"], root)
    for sz in (-1, 1):
        kit.box(f"{name}.fh{sz}", (w + 0.2, 0.09, 0.09), (cx, 0.055, z + sz * (h / 2 + 0.03)), M["white"], root)
    slats = []
    n = 9
    for i in range(n):
        sl = kit.box(f"{name}.slat{i}", (w - 0.04, 0.012, 0.075), (cx, 0.1, z + h / 2 - 0.05 - i * 0.1), M["white"], root)
        slats.append(sl)
    return {"slats": slats, "ztop": z + h / 2 - 0.05, "h": h - 0.1, "cx": cx, "track": blind}


def south_house(kit, ctx, M, name, cx, w, hexc, lean, tracks):
    root = kit.empty(name, (cx, -9.0, 0))
    wall = kit.plastic(hexc, 0.55)
    kit.box(f"{name}.body", (w, 7.0, 5.2), (0, -3.5, 2.6), wall, root, bevel=0.03)
    kit.box(f"{name}.band", (w + 0.1, 0.1, 0.18), (0, 0.05, 2.6), M["white"], root)
    for sgn, ang, ycen in ((1, -28.0, -1.75), (-1, 28.0, -5.25)):
        kit.box(f"{name}.roof{sgn}", (w + 0.9, 4.5, 0.2), (0, ycen, 5.2 + 0.95), M["roof"], root,
                rot=(math.radians(ang), 0, 0), bevel=0.03)
    kit.box(f"{name}.door", (1.0, 0.1, 2.0), (-w / 2 + 1.5, 0.05, 1.0), M["dark"], root)
    kit.box(f"{name}.lampbase", (0.1, 0.06, 0.4), (-w / 2 + 2.4, 0.08, 2.2), M["dark"], root)
    kit.box(f"{name}.lamp", (0.18, 0.18, 0.26), (-w / 2 + 2.4, 0.14, 1.9), M["bulb"], root)
    for sx in (-1, 1):
        kit.box(f"{name}.low{sx}", (1.2, 0.05, 1.0), (sx * (w / 2 - 1.2) + (0.8 if sx < 0 else 0), 0.03, 1.3), M["glass"], root)
    wins = []
    xs = [(-w / 2 + 1.3 + k * (w - 2.6) / 2) for k in range(3)]
    for k, wx in enumerate(xs):
        wins.append(window(kit, M, root, f"{name}.w{k}", wx, 3.9, 1.1, 1.2, tracks[k]))
    root.rotation_euler = (0, math.radians(lean), 0)
    ctx["blinds"] += wins
    return root


def build_south(kit, ctx, M):
    ctx["blinds"] = []
    ctx["coral"] = south_house(kit, ctx, M, "coral", -6.0, 9.0, "#ff8f7a", 6.0, [1, 1, 1])
    south_house(kit, ctx, M, "lemon", 6.0, 9.0, "#ffd54a", 0.0, ["bw0", "bw1", "bw2"])
    south_house(kit, ctx, M, "lilac", -18.0, 8.0, "#b69cff", 0.0, ["bw0", "bw1", "bw2"])
    south_house(kit, ctx, M, "sky", 18.0, 8.0, "#6cc8ff", 0.0, ["bw2", "bw0", "bw1"])


# ------------------------------------------------------------------------------------------------ our house and its bedroom
def build_ours(kit, ctx, M):
    X0, X1, Y0, Y1 = -14.0, -4.0, 12.0, 19.0
    cx = (X0 + X1) / 2
    kit.box("o.ground", (X1 - X0, Y1 - Y0, 2.6), (cx, (Y0 + Y1) / 2, 1.3), M["yellow"], bevel=0.03)
    kit.box("o.slab", (X1 - X0 + 0.2, Y1 - Y0 + 0.2, 0.2), (cx, (Y0 + Y1) / 2, 2.7), M["white"], bevel=0.02)
    # the upper walls: front with the window opening (x -7 .. -5, z 3.7 .. 5.0), back with a door, two sides
    zc, zh = Z2 + 1.2, 2.4
    kit.box("o.fL", (7.0, 0.2, zh), (-10.5, Y0 + 0.1, zc), M["yellow"])
    kit.box("o.fR", (1.0, 0.2, zh), (-4.5, Y0 + 0.1, zc), M["yellow"])
    kit.box("o.fB", (2.0, 0.2, 0.9), (-6.0, Y0 + 0.1, Z2 + 0.45), M["yellow"])
    kit.box("o.fT", (2.0, 0.2, 0.2), (-6.0, Y0 + 0.1, Z2 + 2.3), M["yellow"])
    kit.box("o.bL", (4.05, 0.2, zh), (-11.975, Y1 - 0.1, zc), M["yellow"])
    kit.box("o.bR", (4.95, 0.2, zh), (-6.475, Y1 - 0.1, zc), M["yellow"])
    kit.box("o.bT", (1.1, 0.2, 0.3), (-9.5, Y1 - 0.1, Z2 + 2.25), M["yellow"])
    kit.box("o.dark", (1.6, 1.4, 2.3), (-9.5, Y1 + 0.75, Z2 + 1.15), M["dark"])
    kit.box("o.sw", (0.2, Y1 - Y0 - 0.4, zh), (X0 + 0.1, (Y0 + Y1) / 2, zc), M["yellow"])
    kit.box("o.se", (0.2, Y1 - Y0 - 0.4, zh), (X1 - 0.1, (Y0 + Y1) / 2, zc), M["yellow"])
    kit.box("o.ceil", (X1 - X0, Y1 - Y0, 0.2), (cx, (Y0 + Y1) / 2, Z2 + 2.5), M["white"])
    for sgn, ang, ycen in ((1, -28.0, 14.2), (-1, 28.0, 17.8)):
        kit.box(f"o.roof{sgn}", (X1 - X0 + 1.2, 4.3, 0.22), (cx, ycen, Z2 + 2.6 + 0.9), M["roof"],
                rot=(math.radians(ang), 0, 0), bevel=0.03)
    # the bedroom's wooden floor, 4 cm proud of the slab
    kit.box("o.floor", (X1 - X0 - 0.4, Y1 - Y0 - 0.4, 0.04), (cx, (Y0 + Y1) / 2, Z2 + 0.02), M["floor"])
    # window frame outside and the sill
    for sx in (-1, 1):
        kit.box(f"o.wf{sx}", (0.1, 0.1, 1.5), (-6.0 + sx * 1.05, Y0 - 0.04, Z2 + 1.65), M["white"])
    for sz, zz in ((1, 5.05), (-1, 3.68)):
        kit.box(f"o.wh{sz}", (2.3, 0.14, 0.1), (-6.0, Y0 - 0.05, zz), M["white"])
    # the lower windows and the door and the porch
    for x in (-12.2, -4.9):
        kit.box(f"o.low{x}", (1.3, 0.05, 1.0), (x, Y0 - 0.03, 1.4), M["glass"])
    kit.box("o.door", (1.1, 0.1, 2.1), (-8.2, Y0 - 0.05, 1.05), M["wood"])
    kit.box("o.deck", (4.4, 1.9, 0.24), (-8.2, Y0 - 0.95, 0.12), M["floor"])
    kit.box("o.proof", (4.8, 2.1, 0.12), (-8.2, Y0 - 1.0, 2.45), M["white"])
    for sx in (-1, 1):
        kit.box(f"o.ppost{sx}", (0.14, 0.14, 2.2), (-8.2 + sx * 2.1, Y0 - 1.8, 1.35), M["white"])
    # the porch light, hanging from the roof, swung by "sway"
    root = kit.empty("o.porchlight", (-7.2, Y0 - 0.9, 2.4))
    kit.cyl("o.chain", 0.012, 0.5, (0, 0, -0.25), M["dark"], root, n=6)
    kit.box("o.lantern", (0.22, 0.22, 0.3), (0, 0, -0.62), M["bulb"], root, bevel=0.03)
    ctx["porchlight"] = root
    # --- the bedroom
    kit.prop("bed_single", (-12.6, 16.9, Z2 + 0.04), rot=0, scale=1.45)
    kit.box("o.desk", (1.7, 0.7, 0.06), (-8.4, 12.8, Z2 + 0.75), M["wood"], bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"o.dl{sx}{sy}", (0.06, 0.06, 0.74), (-8.4 + sx * 0.77, 12.8 + sy * 0.28, Z2 + 0.37), M["wood"])
    ctx["lamp"] = kit.prop("light_desk", (-9.0, 12.7, Z2 + 0.78), rot=180, scale=1.7)
    kit.light("lamp", "POINT", (-9.0, 12.85, Z2 + 1.25), 55.0, "#ffb45e", size=0.15)
    kit.light("roomfill", "AREA", (-9.0, 15.4, Z2 + 2.3), 520.0, "#cfd8ff", size=4.0)
    kit.light("greenglow", "SPOT", (-1.5, 9.5, 5.0), 1500.0, "#7dff98", size=0.3, spot=40, blend=0.3)
    kit.aim(kit.LIGHTS["greenglow"]["obj"], (-6.0, 13.6, Z2 + 1.2))
    # the chair on casters
    chair = kit.empty("o.chair", (-8.4, 14.6, Z2 + 0.04))
    kit.box("o.seat", (0.5, 0.5, 0.08), (0, 0, 0.52), M["dark"], chair, bevel=0.03)
    kit.box("o.cback", (0.5, 0.07, 0.55), (0, 0.24, 0.84), M["dark"], chair, bevel=0.03)
    kit.cyl("o.cpost", 0.03, 0.4, (0, 0, 0.3), M["chrome"], chair, n=10)
    for k in range(5):
        a = k * 2 * math.pi / 5
        kit.box(f"o.cspoke{k}", (0.32, 0.05, 0.04), (0.16 * math.cos(a), 0.16 * math.sin(a), 0.12), M["chrome"], chair,
                rot=(0, 0, a))
        kit.sphere(f"o.caster{k}", 0.045, (0.31 * math.cos(a), 0.31 * math.sin(a), 0.05), M["black"], chair, seg=8)
    ctx["chair"] = chair
    # the blinds: slats stacked in the window opening, inside
    slats = []
    for i in range(13):
        slats.append(kit.box(f"o.slat{i}", (1.9, 0.09, 0.012), (-6.0, Y0 + 0.3, Z2 + 2.14 - i * 0.092), M["white"]))
    ctx["bslats"] = slats
    kit.box("o.bhead", (2.0, 0.1, 0.06), (-6.0, Y0 + 0.3, Z2 + 2.25), M["white"])
    # Dad's yellow spirit level on the sill (z-lifted 5 mm), its bubble driven by the meter
    kit.box("o.shelf", (2.0, 0.25, 0.04), (-6.0, Y0 + 0.45, 3.68), M["white"])
    kit.box("level.body", (0.58, 0.075, 0.06), (-5.4, Y0 + 0.45, 3.7 + 0.035), M["level"], bevel=0.012)
    kit.box("level.vial", (0.16, 0.078, 0.034), (-5.4, Y0 + 0.45, 3.7 + 0.075), M["vial"], bevel=0.008)
    ctx["bubble"] = kit.sphere("level.bubble", 0.016, (-5.4, Y0 + 0.45, 3.7 + 0.09), M["bubble"], seg=8)
    # the doorway's white frame
    for sx in (-1, 1):
        kit.box(f"o.df{sx}", (0.1, 0.08, 2.2), (-9.5 + sx * 0.6, Y1 - 0.22, Z2 + 1.12), M["white"])
    kit.box("o.dfh", (1.3, 0.08, 0.1), (-9.5, Y1 - 0.22, Z2 + 2.2), M["white"])


def build_hall(kit, ctx, M):
    kit.box("h.floor", (6.8, 1.9, 0.1), (HX + 3.2, -0.75, -0.05), M["floor"])
    kit.box("h.back", (6.8, 0.2, 2.7), (HX + 3.2, 0.1, 1.3), M["cream"])
    kit.box("h.ceil", (6.8, 1.9, 0.1), (HX + 3.2, -0.75, 2.65), M["cream"])
    kit.box("h.end", (0.2, 1.9, 2.7), (HX + 6.7, -0.75, 1.3), M["cream"])
    kit.box("h.start", (0.2, 1.9, 2.7), (HX - 0.3, -0.75, 1.3), M["cream"])
    kit.box("h.glow", (0.04, 1.0, 1.5), (HX + 6.58, -0.75, 1.55), M["glow"])
    kit.box("h.rail", (6.8, 0.04, 0.08), (HX + 3.2, -0.04, 0.9), M["white"])
    ctx["pics"] = []
    cols = [("pic1", "pic4"), ("pic2", "pic5"), ("pic3", "pic1")]
    for k, x in enumerate((HX + 1.6, HX + 3.3, HX + 5.0)):
        root = kit.empty(f"h.pic{k}", (x, -0.07, 1.55))
        kit.box(f"h.frame{k}", (0.8, 0.06, 1.0), (0, 0, 0), M["wood"], root, bevel=0.01)
        kit.box(f"h.art{k}", (0.64, 0.02, 0.84), (0, -0.04, 0), M[cols[k][0]], root)
        kit.box(f"h.art2{k}", (0.3, 0.02, 0.3), (0.08, -0.058, -0.1), M[cols[k][1]], root)
        ctx["pics"].append(root)
    kit.light("hall", "POINT", (HX + 3.0, -0.8, 2.3), 70.0, "#ffe2b0", size=0.2)
    kit.light("hallglow", "POINT", (HX + 6.2, -0.8, 1.5), 60.0, "#7dff98", size=0.2)


def build_bedside(kit, ctx, M):
    kit.box("b.floor", (5, 3, 0.1), (BX, -0.5, -0.05), M["floor"])
    kit.box("b.back", (5, 0.2, 3.0), (BX, 0.1, 1.5), kit.plastic("#8a94c8", 0.7))
    kit.box("b.stand", (1.0, 0.6, 0.55), (BX, -0.32, 0.275), M["wood"], bevel=0.02)
    kit.box("b.clock", (0.5, 0.16, 0.28), (BX, -0.3, 0.69), M["dark"], bevel=0.03)
    face = quad_uv(kit, "b.face", (0.4, 0.2), (BX, -0.3 - 0.0835, 0.69), M["clock"])
    face.rotation_euler = (math.pi / 2, 0, 0)
    kit.light("bs", "POINT", (BX - 0.5, -1.0, 1.2), 9.0, "#ffd0b0", size=0.2)
    kit.light("bsr", "POINT", (BX, -0.7, 0.8), 4.0, "#ff4030", size=0.1)


# ------------------------------------------------------------------------------------------------ the mower, cord, props
def build_mower(kit, ctx, M):
    root = kit.empty("mower", (0, 0, 0))
    kit.box("m.deck", (0.62, 0.78, 0.2), (0, 0, 0.27), M["red"], root, bevel=0.05)
    kit.box("m.hood", (0.5, 0.5, 0.12), (0, -0.05, 0.43), M["red_d"], root, bevel=0.05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"m.wheel{sx}{sy}", 0.1 if sy < 0 else 0.13, 0.07, (sx * 0.34, sy * 0.28, 0.12 if sy < 0 else 0.13), M["black"],
                    root, rot=(0, math.pi / 2, 0), n=16)
    for sx in (-1, 1):
        rail = kit.box(f"m.rail{sx}", (0.03, 0.03, 0.95), (sx * 0.27, 0.62, 0.62), M["chrome"], root)
        rail.rotation_euler = (math.radians(-35), 0, 0)
    kit.cyl("m.bar", 0.017, 0.62, (0, 0.9, 1.0), M["chrome"], root, rot=(0, math.pi / 2, 0), n=12)
    for sx in (-1, 1):
        kit.cyl(f"m.grip{sx}", 0.024, 0.14, (sx * 0.28, 0.9, 1.0), M["black"], root, rot=(0, math.pi / 2, 0), n=10)
    for k, x in enumerate((0.19, 0.215)):     # the lore: two lime strokes scratched into the bar by the left grip
        kit.cyl(f"m.stroke{k}", 0.0215, 0.007, (x, 0.9, 1.0), M["lime"], root, rot=(0, math.pi / 2, 0), n=12)
    kit.box("m.bag", (0.4, 0.3, 0.3), (0, 0.38, 0.5), M["dark"], root, bevel=0.04)
    ctx["mower"] = root
    ctx["cord"] = []
    for k in range(16):
        ctx["cord"].append(kit.cyl(f"cord{k}", 0.02, 1.0, (0, 0, 0.03), M["orange"], n=8))


def build_misc(kit, ctx, M):
    # seeds, sod, sprinkler, hose water, binoculars
    rng = np.random.default_rng(3)
    ctx["seeds"] = []
    for k in range(28):
        a, r = rng.uniform(0, 2 * math.pi), 1.05 * math.sqrt(rng.uniform())
        ctx["seeds"].append((kit.box(f"seed{k}", (0.03, 0.03, 0.015), (0, 0, -5), M["seed"]),
                             (BALD[0] + r * math.cos(a), BALD[1] + r * math.sin(a))))
    sod = kit.empty("sod", (BALD[0], BALD[1], 0.0))
    kit.box("sod.slab", (2.0, 1.5, 0.05), (0, 0, 0.065), M["sod"], sod, bevel=0.01)
    for sx in (-1, 1):
        kit.box(f"sod.ey{sx}", (0.1, 1.5, 0.056), (sx * 0.95, 0, 0.068), M["sod_y"], sod)
    for sy in (-1, 1):
        kit.box(f"sod.ex{sy}", (2.0, 0.1, 0.056), (0, sy * 0.7, 0.068), M["sod_y"], sod)
    ctx["sod"] = sod
    kit.box("seedbag", (0.5, 0.2, 0.7), (-4.4, 8.9, 0.35), kit.plastic("#d9c08a", 0.8), bevel=0.04)
    kit.box("seedband", (0.52, 0.22, 0.12), (-4.4, 8.9, 0.55), M["lime"])
    spr = kit.empty("sprinkler", (BALD[0], BALD[1], 0.0))
    kit.cyl("spr.base", 0.1, 0.1, (0, 0, 0.09), M["black"], spr, n=12)
    kit.cyl("spr.head", 0.04, 0.2, (0, 0, 0.22), M["chrome"], spr, n=8)
    ctx["sprink"] = spr
    spr.location = (BALD[0], BALD[1], -9.0)
    ctx["drops"] = [kit.sphere(f"drop{k}", 0.035, (0, 0, -5), M["water"], seg=6) for k in range(26)]
    bino = kit.empty("binos", (0, 0, -9))
    kit.box("bn.bridge", (0.2, 0.06, 0.07), (0, 0.0, 0.0), M["black"], bino, bevel=0.015)
    for sx in (-1, 1):
        kit.cyl(f"bn.tube{sx}", 0.05, 0.2, (sx * 0.1, -0.06, 0.0), M["black"], bino, rot=(math.pi / 2, 0, 0), n=12)
        kit.cyl(f"bn.lens{sx}", 0.035, 0.02, (sx * 0.1, -0.17, 0.0), M["glass"], bino, rot=(math.pi / 2, 0, 0), n=10)
    ctx["binoculars"] = bino


def build_lights(kit, ctx, M):
    kit.light("sun", "SUN", (0, 0, 30), 4.0, "#fff1d0")
    kit.aim(kit.LIGHTS["sun"]["obj"], (4, 6, 0))
    kit.LIGHTS["sun"]["obj"].location = (-18, -14, 24)
    kit.aim(kit.LIGHTS["sun"]["obj"], (0, 4, 0))
    kit.light("dayfill", "AREA", (0, 8, 22), 5500.0, "#cfe6ff", size=60.0)
    kit.light("moon", "SUN", (-10, -18, 24), 1.5, "#a9c4ff")
    kit.aim(kit.LIGHTS["moon"]["obj"], (2, 6, 0))
    kit.light("eyelamp", "AREA", (HC[0], HC[1] - 0.5, 2.8), 150.0, "#ffe0a8", size=3.5)
    kit.light("lidrim", "SPOT", (HC[0] + 1.0, HC[1] + 4.5, 3.0), 800.0, "#a9c4ff", size=0.2, spot=60, blend=0.5)
    kit.aim(kit.LIGHTS["lidrim"]["obj"], (HC[0], HC[1] + 0.6, 0.5))
    kit.light("streetfill", "AREA", (0.0, 3.0, 9.0), 4500.0, "#cfd8ff", size=26.0)
    kit.aim(kit.LIGHTS["streetfill"]["obj"], (0.0, -9.0, 3.0))
    kit.light("porchfill", "POINT", (-7.2, 10.2, 2.3), 140.0, "#ffd9a0", size=0.2)
    kit.light("faces", "AREA", (HC[0] - 2, 3.0, 4.0), 260.0, "#fff1c2", size=5.0)
    kit.aim(kit.LIGHTS["faces"]["obj"], (HC[0] - 2, 8.0, 0.8))


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    M = mats(kit)
    ctx = {"M": M}
    w = bpy.context.scene.world
    nodes = [n for n in w.node_tree.nodes if n.type == "BACKGROUND"]
    ctx["bg_nodes"] = nodes
    build_ground(kit, ctx, M)
    build_fence(kit, ctx, M)
    build_lawn_and_lid(kit, ctx, M)
    build_floods(kit, ctx, M)
    build_trees(kit, ctx, M)
    build_mailboxes(kit, ctx, M)
    build_odell_house(kit, ctx, M)
    build_south(kit, ctx, M)
    build_ours(kit, ctx, M)
    build_hall(kit, ctx, M)
    build_bedside(kit, ctx, M)
    build_mower(kit, ctx, M)
    build_misc(kit, ctx, M)
    build_lights(kit, ctx, M)
    return ctx


# ------------------------------------------------------------------------------------------------ animate
def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _resolve(ctx, story, tl):
    if "tr" in ctx and ctx.get("tr_tl") is tl:
        return
    at = timeline.resolver(tl["lines"], tl["duration"])
    ctx["at"] = at
    ctx["tr"] = {name: [(at(r), v) for r, v in ks] for name, ks in story["tracks"].items()}
    ctx["tr_tl"] = tl


def tv(ctx, name, t, stepped=False):
    ks = ctx["tr"][name]
    if t <= ks[0][0]:
        return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t < t1:
            if stepped:
                return v0
            return v0 + (v1 - v0) * _ss((t - t0) / max(1e-6, t1 - t0))
    return ks[-1][1]


def _aim_y(ob, p0, p1, r=0.02):
    """Stretch a unit-length cylinder (z axis) between two world points."""
    a, b = V(p0), V(p1)
    d = b - a
    ob.location = (a + b) / 2
    ob.scale = (1, 1, max(d.length, 1e-4))
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()


def animate(kit, story, tl, t, ctx):
    _resolve(ctx, story, tl)
    at = ctx["at"]
    sid = timeline.shot_at(tl, t)["id"]
    look = story["looks"].get(sid, {})
    day = float(look.get("day", 0))
    night = day < 0.01
    # the sky and the world's light
    sky = [27 / 255, 42 / 255, 107 / 255], [126 / 255, 200 / 255, 255 / 255]
    skyc = tuple(a + (b - a) * min(1.0, day) for a, b in zip(*sky))
    for n in ctx["bg_nodes"]:
        if n.inputs["Color"].is_linked:
            n.inputs["Strength"].default_value = 0.6 * (1 - min(1.0, day)) + 0.25 * min(1.0, day)
        else:
            c = kit.col("#000000")
            n.inputs["Color"].default_value = (*[kit.srgb(v) for v in skyc], 1.0)
    bpy.context.scene.view_settings.exposure = float(look.get("exposure", 0.0))
    # the Head: lid, eye, lights
    lid = tv(ctx, "lid", t)
    ctx["lid"].rotation_euler = (-math.radians(70.0 * lid), 0, 0)
    ey = int(tv(ctx, "eye", t, stepped=True))
    for k, ob in enumerate(ctx["eyes"]):
        ob.hide_render = (k != ey) or lid < 0.002
    # the rule meter's twin: Dad's level
    m = tl.get("meter")
    if m:
        v = _meter(tl, t)
        ctx["bubble"].location.x = -5.4 + 0.045 * v
    # the hall, the street, the room
    for k, p in enumerate(ctx["pics"]):
        p.rotation_euler = (0, math.radians(9.0 * tv(ctx, "pic", t)), 0)
    ml = tv(ctx, "mail", t)
    for root, x in ctx["mail"]:
        sgn = -1.0 if x > -8.0 else 1.0
        root.rotation_euler = (0, math.radians(9.0 * ml) * sgn, 0)
    c = tv(ctx, "chair", t)
    ctx["chair"].location = (-8.4 + (-6.15 + 8.4) * c, 14.6 + (12.78 - 14.6) * c, Z2 + 0.04)
    ctx["chair"].rotation_euler = (0, 0, math.radians(-25) * c)
    sl = tv(ctx, "slat", t)
    for i, s in enumerate(ctx["bslats"]):
        dip = sl if i == 6 else 0.0
        s.rotation_euler = (math.radians(float(look.get("bopen", 72.0)) - 52.0 * dip), 0, 0)
        s.location.z = Z2 + 2.14 - i * 0.092 - 0.015 * dip
    sw = tv(ctx, "sway", t)
    ctx["lamp"].rotation_euler = (0, 0.09 * sw * math.sin(2 * math.pi * 1.7 * t), math.radians(180))
    ctx["porchlight"].rotation_euler = (0, -0.28 * tv(ctx, "sway", t) * (1 + 0.12 * math.sin(2 * math.pi * 0.8 * t)), 0)
    # the south blinds
    for b in ctx["blinds"]:
        tr = b["track"]
        drop = 1.0 if tr == 1 else tv(ctx, tr, t)
        n = len(b["slats"])
        pitch = 0.02 + (b["h"] / n - 0.02) * drop
        for i, s in enumerate(b["slats"]):
            s.location.z = b["ztop"] - i * pitch
            bent = (tr == 1 and b["cx"] < -7.0 and i == 3)
            s.rotation_euler = (math.radians(-40) if bent else 0.0, 0, 0)
            if bent:
                s.location.z -= 0.05
    # people-driven props
    od = acting.state(tl, "odell", t)
    show_m = (not od["hidden"]) and od["expr"] == "shut"
    mower = ctx["mower"]
    if not show_m:
        mower.location = (0, 0, -50)
    for k, c_ in enumerate(ctx["cord"]):
        c_.hide_render = not show_m
    if show_m:
        d = (math.sin(od["yaw"]), -math.cos(od["yaw"]))
        mx, my = od["x"] + d[0] * MOWER_OFF, od["y"] + d[1] * MOWER_OFF
        mower.location = (mx, my, hump(mx, my) if 0.2 < mx < 15 and 5.2 < my < 12 else 0.0)
        mower.rotation_euler = (0, 0, od["yaw"])
        ax, ay = PORCH_ANCHOR
        # the cord leaves the handle's rear and runs along the grass to the porch
        sx, sy = mx - d[0] * 0.0 - d[0] * (-0.0), my
        p0 = V((mx, my, 0.06))
        p1 = V((ax, ay, 0.35))
        pts = []
        n = len(ctx["cord"])
        for k in range(n + 1):
            u = k / n
            pt = p0 + (p1 - p0) * u
            pts.append(V((pt.x, pt.y, 0.04 + 0.1 * math.sin(math.pi * u) * (1 - u) + (p1.z - 0.04) * u ** 3)))
        for k, c_ in enumerate(ctx["cord"]):
            _aim_y(c_, pts[k], pts[k + 1])
    dn = acting.state(tl, "dadn", t)
    bv = tv(ctx, "binos", t)
    bn = ctx["binoculars"]
    if bv > 0.01 and not dn["hidden"]:
        d = (math.sin(dn["yaw"]), -math.cos(dn["yaw"]))
        bn.location = (dn["x"] + d[0] * 0.5, dn["y"] + d[1] * 0.5, dn["z"] + 1.0 + 0.55 * min(1.0, bv))
        bn.rotation_euler = (0, 0, dn["yaw"])
    else:
        bn.location = (0, 0, -9)
    # seeds, sod, sprinkler and the hose
    t0, t1, t2 = at("L10"), at("L10.1"), at("L11")
    ctx["sod"].location = (BALD[0], BALD[1], 0.0 if tv(ctx, "sod", t) > 0.5 else -9.0)
    for k, (ob, (ex, ey_)) in enumerate(ctx["seeds"]):
        if t0 <= t < t2:
            u = min(1.0, max(0.0, (t - t0 - 0.02 * k % 0.4) / max(0.3, t1 - t0 - 0.4)))
            sx, sy = -3.6, 7.9
            ob.location = (sx + (ex - sx) * u, sy + (ey_ - sy) * u, 0.05 + 1.0 * (1 - u) * u * 1.6 + (0.9 * (1 - u)))
            if u >= 1.0:
                ob.location.z = 0.05
        else:
            ob.location = (0, 0, -5)
    sp = tv(ctx, "sprink", t)
    ctx["sprink"].location = (BALD[0], BALD[1], 0.0 if sp > 0.5 else -9.0)
    hs = tv(ctx, "hose", t)
    drops = ctx["drops"]
    for k, ob in enumerate(drops):
        if sp > 0.5 and k < 12:
            ang = math.floor(t * 5) * 0.55 + k * 2 * math.pi / 12
            u = (t * 1.6 + k / 12.0) % 1.0
            r = 1.0 * u
            ob.location = (BALD[0] + r * math.cos(ang), BALD[1] + r * math.sin(ang), 0.22 + 0.9 * 4 * u * (1 - u))
        elif hs > 0.5 and k >= 12:
            u = (t * 1.5 + (k - 12) / 14.0) % 1.0
            o = (-3.35, 8.45, 0.95)
            tg = (BALD[0] + 0.2 * math.sin(k), BALD[1] + 0.2 * math.cos(k), 0.05)
            ob.location = (o[0] + (tg[0] - o[0]) * u, o[1] + (tg[1] - o[1]) * u, o[2] + (tg[2] - o[2]) * u + 0.6 * 4 * u * (1 - u))
        else:
            ob.location = (0, 0, -5)
    # light gains: the day and night rigs and the Head's own lights
    g = {}
    g["sun"] = min(1.0, day)
    g["dayfill"] = min(1.0, day)
    g["moon"] = 1.0 - min(1.0, day)
    for f in ctx["floods"]:
        g[f] = float(look.get("flood", 1.0)) if night else 0.0
    open_ = _ss(min(1.0, lid * 2.5))
    g["eyelamp"] = open_ if night else 0.0
    g["lidrim"] = open_ if night else 0.0
    g["faces"] = float(look.get("faces", 1.0)) if night else 0.0
    g["greenglow"] = 1.0 if night else 0.0
    g["streetfill"] = 1.0 if night else 0.0
    g["porchfill"] = 1.0 if night else 0.0
    return g


def _meter(tl, t):
    ks = tl["meter"]
    if t <= ks[0][0]:
        return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t < t1:
            return v0 + (v1 - v0) * _ss((t - t0) / max(1e-6, t1 - t0))
    return ks[-1][1]
