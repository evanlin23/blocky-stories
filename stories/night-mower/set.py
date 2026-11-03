"""Night Mower (revival): a bright cul-de-sac, Mr. Odell's floodlit striped lawn, and the lime yardstick staked in it.
Built from kit.py's parts and CC0 props. No text anywhere (the bedside clock shows digits only).

The places (metres, the ground is z = 0), shared with generator/make_story.py:
- the street y -4 .. 4 along x, our sidewalk y 4 .. 5.2, the yards y 5.2 .. 12
- our yard x -15 .. -0.2 (ordinary shaggy green), the low fence at x = 0
- Mr. Odell's lawn x 0.2 .. 15 (straight stripes), his mint house behind it, four floodlights
- the lime yardstick STK at (2.75, 7.0); the grass patch round its foot climbs it (track "stick", in ticks of 0.1 m)
- the mow strip x 3.0 .. 3.8: blades that stand tall behind the mower (reversed mowing) and short ahead of it
- the reversed clippings: a pool of small green chips that lift off the lawn ahead of the deck and arc up into it
- the coffee cart at CART (4.2, 4.9) facing the street, paper cups from story.json "cups"
- our butter-yellow house x -14 .. -4 (bedroom upstairs at z 2.8, window at x = -6, porch at (-8.2, 10.8))
- the south houses (front wall y = -9), the coral one straight
- the bedside clock at x = 130

story.json "tracks" (resolved here) drive: stick (ticks), slat, bend, vision, bw0 to bw2 (the south blinds).
story.json "looks" gives each shot's day, exposure, flood, mower (None | "park" | "none" | [x, y, yaw]), dir, strip,
clip, macro, ticks [a, b], chairs, warm.
"""

from __future__ import annotations

import hashlib
import math
import tempfile
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector as V
from PIL import Image, ImageDraw, ImageFont

from blocky import acting, timeline

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TMP = Path(tempfile.gettempdir()) / "night-mower-tex"
TMP.mkdir(parents=True, exist_ok=True)

LAWN = (0.2, 15.0, 5.2, 12.0)    # Mr. Odell's lawn x0, x1, y0, y1
STK = (2.75, 7.0)                 # the yardstick
STRIP = (3.0, 3.8, 5.6, 11.6)    # the mow strip x0, x1, y0, y1
CART = (4.2, 4.9)
PARK = (11.4, 10.7, 0.0)         # the parked mower
Z2 = 2.8
BX = 130.0                       # the bedside
MOWER_OFF = 1.45                 # the mower's centre this far in front of Mr. Odell
PORCH_ANCHOR = (9.6, 11.9)       # where the orange cord is plugged in
LIME = "#b6ff3b"
H_SHORT, H_TALL = 0.035, 0.24    # strip blade heights


# ------------------------------------------------------------------------------------------------ kept parts
def pil_image(name, im: Image.Image):
    h = hashlib.md5(im.tobytes()).hexdigest()[:10]
    path = TMP / f"{name}-{h}.png"
    if not path.exists():
        im.save(path)
    img = bpy.data.images.load(str(path), check_existing=True)
    img.colorspace_settings.name = "sRGB"
    return img


def image_mat(kit, name, im, rough=0.85, emit=0.0, turf=False, pale="#d4ae72", under=None, alpha=False):
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
    if alpha:
        nt.links.new(tex.outputs["Alpha"], b.inputs["Alpha"])
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


def clock_image():
    im = Image.new("RGB", (560, 280), (20, 6, 8))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(str(ROOT / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"), 210)
    tw = d.textlength("3:00", font=f)
    d.text(((560 - tw) / 2, 18), "3:00", font=f, fill=(255, 52, 40))
    return im


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


def build_fence(kit, ctx, M):
    y0, y1 = 5.3, 11.9
    n = 8
    for k in range(n + 1):
        y = y0 + (y1 - y0) * k / n
        kit.box(f"fpost{k}", (0.1, 0.1, 0.62), (0.0, y, 0.35), M["fence"], bevel=0.015)
    for z in (0.28, 0.5):
        kit.box(f"frail{z}", (0.05, y1 - y0, 0.07), (0.0, (y0 + y1) / 2, z + 0.04), M["fence"], bevel=0.01)


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
    for k, x in enumerate((-11.5, -9.5, -7.5, -5.5, -3.5)):
        root = kit.empty(f"mbox{k}", (x, 5.0, 0.05))
        kit.box(f"mpost{k}", (0.1, 0.1, 1.0), (0, 0, 0.5), M["wood"], root)
        kit.box(f"mbox_body{k}", (0.3, 0.5, 0.26), (0, 0, 1.12), kit.plastic(cols[k % len(cols)], 0.4), root, bevel=0.05)
        kit.box(f"mflag{k}", (0.04, 0.16, 0.04), (0.17, 0.1, 1.2), M["red"], root)
        ctx["mail"].append((root, x))


def build_odell_house(kit, ctx, M):
    for k, (x, y) in enumerate(((1.6, 14.5), (-2.2, 13.6), (4.4, 16.0))):
        kit.prop("sub_tree_large" if k % 2 == 0 else "sub_tree_small", (x, y, 0), rot=k * 41, scale=1.5)
    kit.prop("sub_building_type_c", (9.8, 14.95, 0), tint="#9ff0d6")
    kit.prop("sub_planter", (7.2, 12.5, 0), rot=0)
    kit.prop("flowers", (11.6, 11.6, 0), scale=0.9)
    kit.prop("bush_1", (13.4, 12.3, 0), scale=0.7)
    kit.prop("bush_2", (5.4, 12.4, 0), scale=0.6)
    for k, y in enumerate((11.2, 9.4, 7.6, 5.9)):
        kit.prop("sub_path_stones_long", (9.5, y - 0.9, 0), rot=90)


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
        wins.append(dict(window(kit, M, root, f"{name}.w{k}", wx, 3.9, 1.1, 1.2, tracks[k]), root=name))
    ctx["blinds"] += wins
    return root


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
    kit.box("o.lantern", (0.3, 0.3, 0.42), (0, 0, -0.68), M["bulb"], root, bevel=0.03)
    kit.box("o.lcap", (0.38, 0.38, 0.06), (0, 0, -0.44), M["dark"], root, bevel=0.01)
    kit.box("o.lbase", (0.36, 0.36, 0.05), (0, 0, -0.92), M["dark"], root, bevel=0.01)
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
    # the blinds: slats stacked in the window opening, inside
    slats = []
    for i in range(13):
        slats.append(kit.box(f"o.slat{i}", (1.9, 0.09, 0.012), (-6.0, Y0 + 0.3, Z2 + 2.14 - i * 0.092), M["white"]))
    ctx["bslats"] = slats
    kit.box("o.bhead", (2.0, 0.1, 0.06), (-6.0, Y0 + 0.3, Z2 + 2.25), M["white"])
    # the doorway's white frame
    for sx in (-1, 1):
        kit.box(f"o.df{sx}", (0.1, 0.08, 2.2), (-9.5 + sx * 0.6, Y1 - 0.22, Z2 + 1.12), M["white"])
    kit.box("o.dfh", (1.3, 0.08, 0.1), (-9.5, Y1 - 0.22, Z2 + 2.2), M["white"])


def build_bedside(kit, ctx, M):
    kit.box("b.floor", (5, 3, 0.1), (BX, -0.5, -0.05), M["floor"])
    kit.box("b.back", (5, 0.2, 3.0), (BX, 0.1, 1.5), kit.plastic("#8a94c8", 0.7))
    kit.box("b.stand", (1.0, 0.6, 0.55), (BX, -0.32, 0.275), M["wood"], bevel=0.02)
    kit.box("b.clock", (0.5, 0.16, 0.28), (BX, -0.3, 0.69), M["dark"], bevel=0.03)
    face = quad_uv(kit, "b.face", (0.4, 0.2), (BX, -0.3 - 0.0835, 0.69), M["clock"])
    face.rotation_euler = (math.pi / 2, 0, 0)
    kit.light("bs", "POINT", (BX - 0.5, -1.0, 1.2), 9.0, "#ffd0b0", size=0.2)
    kit.light("bsr", "POINT", (BX, -0.7, 0.8), 4.0, "#ff4030", size=0.1)


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
        kit.cyl(f"m.stroke{k}", 0.026, 0.012, (x - 0.006 + 0.014 * k, 0.9, 1.0), M["lime2"], root, rot=(0, math.pi / 2, 0), n=12)
    kit.box("m.bag", (0.4, 0.3, 0.3), (0, 0.38, 0.5), M["dark"], root, bevel=0.04)
    ctx["mower"] = root
    ctx["cord"] = []
    for k in range(16):
        ctx["cord"].append(kit.cyl(f"cord{k}", 0.02, 1.0, (0, 0, 0.03), M["orange"], n=8))


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


# ------------------------------------------------------------------------------------------------ materials and textures
def lawn_image():
    """Straight mown stripes running along y (toward the street), light and dark bands across x."""
    x0, x1, y0, y1 = LAWN
    w, h = 2220, 1020
    xs = x0 + (np.arange(w) + 0.5) / w * (x1 - x0)
    X = np.broadcast_to(xs[None, :], (h, w))
    r = (X - x0) / 0.55
    band = np.floor(r).astype(int)
    light = np.array([48, 214, 94], np.float32)
    dark = np.array([28, 172, 68], np.float32)
    im = np.where((band % 2 == 0)[..., None], light, dark).astype(np.float32)
    rng = np.random.default_rng(5)
    n = rng.normal(0, 1, (h // 3, w // 3)).astype(np.float32)
    n = np.asarray(Image.fromarray(((n * 0.25 + 0.5).clip(0, 1) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32) / 255 - 0.5
    im *= (1.0 + n * 0.10)[..., None]
    edge = np.abs(r % 1.0 - 0.5) > 0.47
    im[edge] *= 0.95
    return Image.fromarray(im.clip(0, 255).astype(np.uint8))


def mats(kit):
    P = kit.plastic
    M = {
        "yellow": P("#ffd970", 0.5), "cream": P("#fff0c8", 0.6), "white": P("#f4f1e8", 0.45), "roof": P("#2f8f9a", 0.5),
        "dark": P("#26262c", 0.5), "wood": P("#8a5a34", 0.6), "red": P("#ff3b30", 0.35, spec=0.6),
        "red_d": P("#c42a22", 0.4), "black": P("#141418", 0.5), "chrome": kit.metal("#cfd3d8", 0.25),
        "orange": P("#ff9a1f", 0.45), "lime": kit.emit(LIME, 0.9), "lime2": kit.emit(LIME, 4.0),
        "tan": P("#c49a5c", 0.95), "pole": P("#8a8f99", 0.4), "warm": kit.emit("#fff1c2", 6.0),
        "glass": kit.emit("#ffd9a0", 1.1), "conc": kit.texture("concrete", 1.0, tint="#d8d6d0"),
        "asphalt": kit.texture("asphalt", 0.5, tint="#8a8f9a"), "ours": P("#6cc24a", 0.9, spec=0.1),
        "ours_b": P("#5fb842", 0.9, spec=0.1), "ground": P("#4f9a3f", 0.95),
        "floor": kit.texture("wood", 0.7, tint="#d9b98a"), "bulb": kit.emit("#fff6dc", 2.2),
        "fence": P("#f4f1e8", 0.5), "mint": P("#8fe3c8", 0.5),
        "tick": P("#101014", 0.6), "stick": P(LIME, 0.5, spec=0.3),
        "blade_a": P("#3ce26b", 0.8, spec=0.1), "blade_b": P("#22c451", 0.8, spec=0.1),
        "blade_s": P("#7dff4a", 0.7, spec=0.1),
        "cart": P("#1fb5a8", 0.5), "cart_d": P("#168a80", 0.5), "cup": P("#fbfaf4", 0.5), "lid": P("#6b3e22", 0.55),
        "sleeve": P(LIME, 0.6), "chair_a": P("#ff9a1f", 0.55), "chair_b": P("#4fb3ff", 0.55),
        "chip_a": kit.emit("#2fe05a", 1.6), "chip_b": kit.emit("#6dff6a", 1.8), "chip_c": kit.emit("#9cff6a", 2.0),
        "streak": kit.emit("#58f06a", 0.8),
    }
    M["lawn"] = image_mat(kit, "odell lawn", lawn_image(), 0.9)
    M["clock"] = image_mat(kit, "clock", clock_image(), 0.4, emit=2.2)
    return M


# ------------------------------------------------------------------------------------------------ blades
def make_blades(kit, name, xs, ys, mat, seed, w=0.024, lean=0.18):
    """A field of single-triangle blades; set_heights(f, h) stands each one up to h metres."""
    rng = np.random.default_rng(seed)
    n = len(xs)
    yaw = rng.uniform(0, math.pi, n)
    la = rng.uniform(0, 2 * math.pi, n)
    f = {"n": n, "x": np.asarray(xs, float), "y": np.asarray(ys, float), "ux": np.cos(yaw) * w / 2, "uy": np.sin(yaw) * w / 2,
         "lx": np.cos(la) * lean * rng.uniform(0.3, 1.0, n), "ly": np.sin(la) * lean * rng.uniform(0.3, 1.0, n),
         "rnd": rng.uniform(0.7, 1.3, n)}
    verts = [(0.0, 0.0, 0.0)] * (3 * n)
    faces = [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(n)]
    f["obj"] = kit.mesh_obj(name, verts, faces, mat, None, (0, 0, 0))
    set_heights(f, np.full(n, 0.05))
    return f


def set_heights(f, h):
    h = np.asarray(h, float)
    n = f["n"]
    v = np.empty((n, 3, 3), np.float64)
    v[:, 0, 0] = f["x"] - f["ux"]
    v[:, 0, 1] = f["y"] - f["uy"]
    v[:, 0, 2] = 0.0
    v[:, 1, 0] = f["x"] + f["ux"]
    v[:, 1, 1] = f["y"] + f["uy"]
    v[:, 1, 2] = 0.0
    v[:, 2, 0] = f["x"] + f["lx"] * h
    v[:, 2, 1] = f["y"] + f["ly"] * h
    v[:, 2, 2] = h
    f["obj"].data.vertices.foreach_set("co", v.ravel())
    f["obj"].data.update()


def build_blades(kit, ctx, M):
    rng = np.random.default_rng(21)
    # the mow strip: two interleaved fields (two greens)
    x0, x1, y0, y1 = STRIP
    n = int((x1 - x0) * (y1 - y0) * 520)
    xs, ys = rng.uniform(x0, x1, n), rng.uniform(y0, y1, n)
    ctx["strip"] = [make_blades(kit, "strip_a", xs[::2], ys[::2], M["blade_a"], 1),
                    make_blades(kit, "strip_b", xs[1::2], ys[1::2], M["blade_b"], 2)]
    # the patch round the yardstick's foot
    m = 220
    r = 0.06 + 0.2 * np.sqrt(rng.uniform(0, 1, m))
    a = rng.uniform(0, 2 * math.pi, m)
    f = make_blades(kit, "stick_grass", STK[0] + r * np.cos(a), STK[1] + r * np.sin(a), M["blade_s"], 3, w=0.035, lean=0.12)
    f["r"] = r
    ctx["stickpatch"] = f
    # our yard: ordinary green, a bit shaggy, left alone
    m = 5200
    xs, ys = rng.uniform(-13.8, -0.5, m), rng.uniform(5.8, 11.6, m)
    keep = ~((xs > -10.8) & (xs < -5.6) & (ys > 9.6))
    xs, ys = xs[keep], ys[keep]
    f = make_blades(kit, "ours_grass", xs, ys, M["ours_b"], 4, w=0.03, lean=0.25)
    set_heights(f, 0.1 + 0.06 * f["rnd"])
    # a few patchy lawns up the street
    for k, (x, y, r) in enumerate(((-21, 8.6, 1.5), (-27, 9.6, 1.1), (-33, 8.0, 1.6), (-24, 7.2, 0.9), (26, 8.4, 1.4),
                                   (32, 9.6, 1.2), (38, 8.0, 1.5), (29, 7.0, 0.8))):
        kit.cyl(f"patch{k}", r, 0.03, (x, y, 0.015), M["tan"], n=24)


# ------------------------------------------------------------------------------------------------ the lawns and the floods
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
    kit.box("fencestrip", (0.4, 6.8, 0.04), (0.0, 8.6, 0.02), M["conc"])
    # Mr. Odell's lawn: one straight-striped quad (its box sits below, so nothing shares a plane)
    kit.box("odlawn_base", (14.8, 6.8, 0.2), (7.6, 8.6, -0.101), M["ground"])
    quad_uv(kit, "odlawn", (LAWN[1] - LAWN[0], LAWN[3] - LAWN[2]), ((LAWN[0] + LAWN[1]) / 2, (LAWN[2] + LAWN[3]) / 2, 0.004), M["lawn"])


def build_floods(kit, ctx, M):
    ctx["floods"] = []
    for k, (x, y) in enumerate(((0.9, 11.6), (6.0, 11.7), (11.5, 11.6), (14.2, 5.6), (14.2, 8.8))):
        kit.cyl(f"pole{k}", 0.06, 4.6, (x, y, 2.3), M["pole"], n=10)
        kit.box(f"head{k}", (0.55, 0.3, 0.28), (x, y, 4.7), M["pole"], bevel=0.02)
        kit.box(f"lamp{k}", (0.46, 0.04, 0.2), (x, y + (0.16 if y < 8 else -0.16), 4.7), M["warm"])
        L = kit.light(f"flood{k}", "SPOT", (x, y, 4.6), 520.0, "#fff1c2", size=0.35, spot=100, blend=0.7)
        kit.aim(L, (4.5, 8.2, 0.0))
        ctx["floods"].append(f"flood{k}")


# ------------------------------------------------------------------------------------------------ the yardstick
def build_stick(kit, ctx, M):
    root = kit.empty("yardstick", (STK[0], STK[1], 0.0))
    kit.box("stk.core", (0.06, 0.02, 0.9), (0, 0, 0.45), M["stick"], root, bevel=0.003)
    kit.box("stk.tip", (0.06, 0.02, 0.03), (0, 0, 0.915), M["stick"], root, bevel=0.003)
    for i in range(1, 10):                      # nine ticks, every 0.1 m: long on the odd ones, short between
        w = 0.052 if i % 2 else 0.032
        kit.box(f"stk.tick{i}", (w, 0.02, 0.016), (0, -0.012, 0.1 * i), M["tick"], root)
    ctx["stick"] = root


# ------------------------------------------------------------------------------------------------ the coffee cart and cups
def build_cart(kit, ctx, M):
    cx, cy = CART
    root = kit.empty("cart", (cx, cy, 0.0))
    kit.box("c.body", (1.7, 0.9, 0.95), (0, 0, 0.5), M["cart"], root, bevel=0.03)
    kit.box("c.skirt", (1.74, 0.94, 0.1), (0, 0, 0.12), M["cart_d"], root, bevel=0.02)
    kit.box("c.counter", (1.9, 1.05, 0.07), (0, -0.05, 1.0), M["white"], root, bevel=0.015)
    for sx in (-1, 1):
        kit.cyl(f"c.wheel{sx}", 0.17, 0.08, (sx * 0.75, 0.0, 0.17), M["black"], root, rot=(0, math.pi / 2, 0), n=14)
        kit.box(f"c.post{sx}", (0.06, 0.06, 1.3), (sx * 0.9, -0.45, 1.65), M["white"], root)
    kit.box("c.back", (1.8, 0.06, 1.2), (0, 0.46, 1.6), M["cart_d"], root, bevel=0.01)
    for k in range(8):
        kit.box(f"c.awn{k}", (0.24, 1.25, 0.05), (-0.84 + 0.24 * k, -0.2, 2.25), M["cart"] if k % 2 == 0 else M["white"], root,
                rot=(math.radians(-10), 0, 0))
    kit.box("c.machine", (0.5, 0.3, 0.42), (0.55, 0.2, 1.255), M["chrome"], root, bevel=0.02)
    kit.box("c.machine2", (0.4, 0.26, 0.1), (0.55, 0.2, 1.52), M["dark"], root, bevel=0.02)
    ctx["cart"] = root


def build_cups(kit, ctx, M, story):
    ctx["cups"] = []
    for i, c in enumerate(story.get("cups", [])):
        root = kit.empty(f"cup{i}", (0, 0, -20))
        kit.cyl(f"cup{i}.body", 0.036, 0.11, (0, 0, 0.055), M["cup"], root, n=14, r2=0.045)
        kit.cyl(f"cup{i}.lid", 0.047, 0.02, (0, 0, 0.12), M["lid"], root, n=14)
        sl = None
        if c.get("kind") == "lime":
            sl = kit.cyl(f"cup{i}.sleeve", 0.0445, 0.05, (0, 0, 0.05), M["sleeve"], root, n=14, r2=0.046)
        ctx["cups"].append({"root": root, "sleeve": sl, "spec": c})


def build_chairs(kit, ctx, M):
    ctx["chairs"] = []
    for k, (x, y, rot, mk) in enumerate(((-1.05, 8.4, 90, "chair_a"), (1.05, 8.4, -90, "chair_b"))):
        root = kit.empty(f"chair{k}", (x, y, -20))
        kit.box(f"ch{k}.seat", (0.5, 0.5, 0.06), (0, 0, 0.4), M[mk], root, bevel=0.01)
        kit.box(f"ch{k}.back", (0.5, 0.06, 0.55), (0, 0.22, 0.7), M[mk], root, rot=(math.radians(-12), 0, 0), bevel=0.01)
        for sx in (-1, 1):
            for sy in (-1, 1):
                kit.box(f"ch{k}.leg{sx}{sy}", (0.05, 0.05, 0.4), (sx * 0.21, sy * 0.21, 0.2), M["white"], root)
            kit.box(f"ch{k}.arm{sx}", (0.05, 0.5, 0.05), (sx * 0.25, 0.0, 0.62), M["white"], root)
        ctx["chairs"].append((root, (x, y), rot))


def build_chips(kit, ctx, M):
    rng = np.random.default_rng(8)
    ctx["chips"] = []
    mm = ["chip_a", "chip_b", "chip_c"]
    for k in range(60):
        s = rng.uniform(0.04, 0.065)
        body = kit.box(f"chip{k}", (s, s * 0.6, 0.012), (0, 0, -30), M[mm[k % 3]])
        gh = [kit.box(f"ghost{k}_{j}", (s * (0.72 - 0.25 * j), s * 0.45, 0.01), (0, 0, -30), M["streak"]) for j in range(2)]
        ctx["chips"].append({"body": body, "ghosts": gh, "ph": rng.uniform(0, 1), "a": rng.uniform(-0.5, 0.5),
                             "b": rng.uniform(0.15, 0.85), "pk": rng.uniform(0.28, 0.6), "sp": rng.uniform(0.9, 1.25),
                             "spin": rng.uniform(-6, 6), "k": k})


# ------------------------------------------------------------------------------------------------ the south houses
def build_south(kit, ctx, M):
    ctx["blinds"] = []
    south_house(kit, ctx, M, "coral", -6.0, 9.0, "#ff8f7a", 0.0, ["bw2", "bw1", "bw0"])
    south_house(kit, ctx, M, "lemon", 6.0, 9.0, "#ffd54a", 0.0, ["bw0", "bw1", "bw2"])
    south_house(kit, ctx, M, "lilac", -18.0, 8.0, "#b69cff", 0.0, ["bw1", "bw0", "bw2"])
    south_house(kit, ctx, M, "sky", 18.0, 8.0, "#6cc8ff", 0.0, ["bw2", "bw0", "bw1"])


def build_lights(kit, ctx, M):
    kit.light("sun", "SUN", (0, 0, 30), 4.0, "#fff1d0")
    kit.LIGHTS["sun"]["obj"].location = (-18, -14, 24)
    kit.aim(kit.LIGHTS["sun"]["obj"], (0, 4, 0))
    kit.light("dayfill", "AREA", (0, 8, 22), 5500.0, "#cfe6ff", size=60.0)
    kit.light("moon", "SUN", (-10, -18, 24), 1.5, "#a9c4ff")
    kit.aim(kit.LIGHTS["moon"]["obj"], (2, 6, 0))
    kit.light("streetfill", "AREA", (0.0, 3.0, 9.0), 4500.0, "#cfd8ff", size=26.0)
    kit.aim(kit.LIGHTS["streetfill"]["obj"], (0.0, -9.0, 3.0))
    kit.light("porchfill", "POINT", (-7.2, 10.2, 2.3), 140.0, "#ffd9a0", size=0.2)
    kit.light("faces", "AREA", (3.0, 2.0, 3.6), 330.0, "#fff1c2", size=5.0)
    kit.aim(kit.LIGHTS["faces"]["obj"], (3.0, 8.0, 0.8))
    kit.light("visionkey", "SPOT", (-3.2, 4.6, 4.2), 900.0, "#ffd9a0", size=0.4, spot=34, blend=0.5)
    kit.aim(kit.LIGHTS["visionkey"]["obj"], (0.5, 8.0, 1.0))


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    M = mats(kit)
    ctx = {"M": M}
    w = bpy.context.scene.world
    ctx["bg_nodes"] = [n for n in w.node_tree.nodes if n.type == "BACKGROUND"]
    build_ground(kit, ctx, M)
    build_fence(kit, ctx, M)
    build_floods(kit, ctx, M)
    build_trees(kit, ctx, M)
    build_mailboxes(kit, ctx, M)
    build_odell_house(kit, ctx, M)
    build_south(kit, ctx, M)
    build_ours(kit, ctx, M)
    build_bedside(kit, ctx, M)
    build_mower(kit, ctx, M)
    build_stick(kit, ctx, M)
    build_blades(kit, ctx, M)
    build_cart(kit, ctx, M)
    build_cups(kit, ctx, M, story)
    build_chairs(kit, ctx, M)
    build_chips(kit, ctx, M)
    build_lights(kit, ctx, M)
    return ctx


# ------------------------------------------------------------------------------------------------ animate
def hand_pos(st, hand):
    """Where a hand is: the shoulder, the arm's length out along the raised arm."""
    yaw = st["yaw"]
    d = (math.sin(yaw), -math.cos(yaw))
    rt = (-math.cos(yaw), -math.sin(yaw))
    right = hand == "r"
    a = st["arms"][1 if right else 0]
    lat = 0.40 if right else -0.40
    reach = 0.5 * math.sin(a) + 0.08
    return (st["x"] + rt[0] * lat + d[0] * reach, st["y"] + rt[1] * lat + d[1] * reach, st["z"] + 1.30 - 0.5 * math.cos(a) + 0.04)


def shot_ticks(look, tl, t, sh, at):
    a, b = look["ticks"]
    u = (t - sh["start"]) / max(1e-6, sh["end"] - sh["start"])
    return a + (b - a) * _ss(u)


def animate(kit, story, tl, t, ctx):
    _resolve(ctx, story, tl)
    at = ctx["at"]
    sh = timeline.shot_at(tl, t)
    sid = sh["id"]
    look = story["looks"].get(sid, {})
    day = float(look.get("day", 0))
    night = day < 0.01
    sky = [27 / 255, 42 / 255, 107 / 255], [126 / 255, 200 / 255, 255 / 255]
    skyc = tuple(a + (b - a) * min(1.0, day) for a, b in zip(*sky))
    for n in ctx["bg_nodes"]:
        if n.inputs["Color"].is_linked:
            n.inputs["Strength"].default_value = 0.6 * (1 - min(1.0, day)) + 0.25 * min(1.0, day)
        else:
            n.inputs["Color"].default_value = (*[kit.srgb(v) for v in skyc], 1.0)
    bpy.context.scene.view_settings.exposure = float(look.get("exposure", 0.0))
    warm = float(look.get("warm", 0.0))
    c0, c1 = (1.0, 0.945, 0.82), (1.0, 0.72, 0.5)
    kit.LIGHTS["sun"]["light"].color = tuple(a + (b - a) * warm for a, b in zip(c0, c1))

    # the blinds: ours (bslats, dipping slat) and the south houses
    sl = tv(ctx, "slat", t)
    for i, s in enumerate(ctx["bslats"]):
        dip = sl if i == 6 else 0.0
        s.rotation_euler = (math.radians(float(look.get("bopen", 72.0)) - 52.0 * dip), 0, 0)
        s.location.z = Z2 + 2.14 - i * 0.092 - 0.015 * dip
    bend = tv(ctx, "bend", t)
    for b in ctx["blinds"]:
        drop = tv(ctx, b["track"], t)
        n = len(b["slats"])
        pitch = 0.02 + (b["h"] / n - 0.02) * drop
        for i, s in enumerate(b["slats"]):
            s.location.z = b["ztop"] - i * pitch
            bent = (b["cx"] < -7.0 and i == 3 and b["root"] == "coral")
            s.rotation_euler = (math.radians(-40 * bend) if bent else 0.0, 0, 0)
            if bent:
                s.location.z -= 0.05 * bend

    # the mower: follows Mr. Odell while he is mowing, or parked, fixed, or away
    od = acting.state(tl, "odell", t)
    mode = look.get("mower")
    mower = ctx["mower"]
    shown, mx, my, myaw = False, 0.0, 0.0, 0.0
    if mode == "none":
        shown = False
    elif mode == "park":
        shown, mx, my, myaw = True, PARK[0], PARK[1], PARK[2]
    elif isinstance(mode, list):
        shown, mx, my, myaw = True, mode[0], mode[1], math.radians(mode[2])
    elif (not od["hidden"]) and od["expr"] in ("shut", "asleep"):
        d = (math.sin(od["yaw"]), -math.cos(od["yaw"]))
        shown, mx, my, myaw = True, od["x"] + d[0] * MOWER_OFF, od["y"] + d[1] * MOWER_OFF, od["yaw"]
    if shown:
        mower.location = (mx, my, 0.0)
        mower.rotation_euler = (0, 0, myaw)
    else:
        mower.location = (0, 0, -50)
    for c_ in ctx["cord"]:
        c_.hide_render = not shown
    if shown:
        p0 = V((mx, my, 0.06))
        p1 = V((PORCH_ANCHOR[0], PORCH_ANCHOR[1], 0.35))
        pts = []
        n = len(ctx["cord"])
        for k in range(n + 1):
            u = k / n
            pt = p0 + (p1 - p0) * u
            pts.append(V((pt.x, pt.y, 0.04 + 0.1 * math.sin(math.pi * u) * (1 - u) + (p1.z - 0.04) * u ** 3)))
        for k, c_ in enumerate(ctx["cord"]):
            _aim_y(c_, pts[k], pts[k + 1])

    # the yardstick's grass: ticks of 0.1 m
    if "ticks" in look:
        ticks = shot_ticks(look, tl, t, sh, at)
    else:
        ticks = tv(ctx, "stick", t)
    sp = ctx["stickpatch"]
    hs = ticks * 0.1 * (1.0 - 0.45 * (sp["r"] - 0.06) / 0.2) * (0.8 + 0.4 * (sp["rnd"] - 0.7) / 0.6)
    set_heights(sp, np.maximum(hs, 0.03))

    # the mow strip: tall behind the mower, short ahead of it (mowing, rewound)
    dirv = float(look.get("dir", -1))
    for f in ctx["strip"]:
        if "strip" in look:
            tall = np.full(f["n"], float(look["strip"]))
        elif shown and STRIP[0] - 0.3 < mx < STRIP[1] + 0.3:
            s = (f["y"] - my) * (-dirv) / 0.4 + 0.5
            tall = np.clip(s, 0.0, 1.0)
            tall = tall * tall * (3 - 2 * tall)
        else:
            tall = np.zeros(f["n"])
        set_heights(f, (H_SHORT + (H_TALL - H_SHORT) * tall) * f["rnd"] ** 0.5)

    # the reversed clippings: lift off the lawn ahead of the deck, arc up, and vanish under the skirt
    rate = float(look.get("clip", 1.0)) if shown and mode != "park" else 0.0
    macro = bool(look.get("macro"))
    if macro:
        rate = 1.0
    frac = float(look.get("fountain", 1.0))
    d = (math.sin(myaw), -math.cos(myaw))
    rt = (-math.cos(myaw), -math.sin(myaw))
    top = max(ticks * 0.1, 0.06)
    def chip_pos(c_, u):
        e = u * u * (3 - 2 * u) * 0.6 + u * 0.4
        if macro:
            ang = c_["ph"] * 6.283 + c_["a"]
            rr = 0.12 + 0.3 * c_["b"]
            sx, sy = STK[0] + rr * math.cos(ang), STK[1] + rr * math.sin(ang)
            ex, ey = STK[0] + 0.45 * rr * math.cos(ang), STK[1] + 0.45 * rr * math.sin(ang)
            z = 0.01 + (top * 0.9) * e + c_["pk"] * 0.3 * 4 * u * (1 - u)
        else:
            aa, bb = c_["a"], c_["b"]
            sx, sy = mx + d[0] * (0.55 + bb) + rt[0] * aa, my + d[1] * (0.55 + bb) + rt[1] * aa
            ex, ey = mx + d[0] * 0.2 + rt[0] * aa * 0.3, my + d[1] * 0.2 + rt[1] * aa * 0.3
            z = 0.03 + 0.15 * e + c_["pk"] * 4 * u * (1 - u)
        return sx + (ex - sx) * e, sy + (ey - sy) * e, z

    for c_ in ctx["chips"]:
        on = rate > 0.01 and c_["k"] < 60 * frac
        if not on:
            c_["body"].location = (0, 0, -30)
            for g_ in c_["ghosts"]:
                g_.location = (0, 0, -30)
            continue
        u = (t * c_["sp"] * 0.95 * (rate if rate < 1 else 1.0) + c_["ph"]) % 1.0
        px, py, z = chip_pos(c_, u)
        vis = u < 0.96
        c_["body"].location = (px, py, z if vis else -30)
        c_["body"].rotation_euler = (0.9 + 0.5 * math.sin(u * 5 + c_["ph"]), 0.4 * math.cos(u * 4 + c_["ph"]), c_["spin"] * u)
        for j, g_ in enumerate(c_["ghosts"]):
            ug = u - 0.07 * (j + 1)
            if ug < 0.0 or not vis:
                g_.location = (0, 0, -30)
                continue
            gx, gy, gz = chip_pos(c_, ug)
            g_.location = (gx, gy, gz)
            g_.rotation_euler = c_["body"].rotation_euler

    ctx["cart"].location = (CART[0], CART[1], 0.0 if day > 0.5 else -20.0)

    # chairs (S32 only)
    for root, (x, y), rot in ctx["chairs"]:
        root.location = (x, y, 0.0 if look.get("chairs") else -20)
        root.rotation_euler = (0, 0, math.radians(rot))

    # cups: in a hand, on the cart or rail, with an optional sleeve sliding on
    for c_ in ctx["cups"]:
        sp_ = c_["spec"]
        ok = (at(sp_.get("from", 0)) <= t < at(sp_.get("to", "end"))) and (not sp_.get("shots") or sid in sp_["shots"])
        if not ok:
            c_["root"].location = (0, 0, -20)
            continue
        if "pos" in sp_:
            c_["root"].location = tuple(sp_["pos"])
        else:
            st = acting.state(tl, sp_["who"], t)
            if st["hidden"]:
                c_["root"].location = (0, 0, -20)
                continue
            c_["root"].location = hand_pos(st, sp_["hand"])
        c_["root"].scale = (sp_.get("scale", 1.0),) * 3
        if c_["sleeve"] is not None:
            ss = sp_.get("slide")
            if ss:
                u = _ss((t - at(ss[0])) / max(1e-6, at(ss[1]) - at(ss[0])))
                c_["sleeve"].location.z = 0.05 + 0.22 * (1 - u)
                c_["sleeve"].hide_render = t < at(ss[0]) - 0.001
            else:
                c_["sleeve"].location.z = 0.05

    # light gains
    g = {}
    fl = float(look.get("flood", 1.0))
    g["sun"] = min(1.0, day)
    g["dayfill"] = min(1.0, day)
    g["moon"] = 1.0 - min(1.0, day)
    for f in ctx["floods"]:
        g[f] = fl if night else 0.0
    g["faces"] = float(look.get("faces", 1.0)) if night else 0.0
    g["streetfill"] = 1.0 if night else 0.0
    g["porchfill"] = float(look.get("porch", 1.0)) if night else 0.0
    g["visionkey"] = tv(ctx, "vision", t)
    return g
