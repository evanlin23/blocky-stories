"""ep156 "Miss Your Old House, Turn Its COLORS": five small bright stages, far apart so their lights never mix.

  KIT     Mom's new kitchen (origin): cream walls, white cabinets, terracotta tiles, a wooden table with two chairs, a big
          sunny window with the old house's yellow stripy curtains (shown by the `curtain` cue), a back door, three moving
          boxes and a tall white fridge with a tear-off day calendar. Three sky-blue fingerprints show on the fridge door
          at the `prints` cue.
  PORCH   the old sky-blue porch swing on two chains and a pot of red geraniums.
  PRATT   Mr. Pratt's porch over a low white fence.
  STREET  a bench in front of a terracotta-and-white checked house, and a green plaid house with a path.
  ROOM    my room: a bed with a white pillowcase and one soft yellow stripe.

The rule meter is the tear-off calendar page: a kraft card with one big numeral, on the fridge door and as a small copy on
the camera (the HUD tag), both swapped by the `day` cue. Nothing blinks, flickers or switches fast: the only light
changes are people's colours, stepped through cast variants by story.json.
"""
import math
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="oldcolors-"))
W = {}
BLUE, YELLOW = "#7fc8f8", "#f7d046"
SKIN = "#c98f62"
FONT = Path(__file__).resolve().parents[2] / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def sample(name, tl, t, defaults):
    cur, prev = dict(defaults), dict(defaults)
    for c in tl["cues"]:
        if c["name"] != name:
            continue
        if c["t"] > t:
            break
        prev = dict(cur)
        cur.update({k: v for k, v in c.items() if k in defaults})
        dur = c.get("dur", 0.0)
        if dur > 0 and t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            return {k: (prev[k] + (cur[k] - prev[k]) * u if isinstance(cur[k], (int, float)) else cur[k]) for k in cur}
    return cur


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def mix(a, b, u):
    ca, cb = hx(a), hx(b)
    return "#%02x%02x%02x" % tuple(int(round(ca[i] + (cb[i] - ca[i]) * u)) for i in range(3))


# ---------------------------------------------------------------------------------------------- pictures (PIL)
def _cal_image(n):
    from PIL import Image, ImageDraw, ImageFont
    p = TMP / f"cal-{n}.png"
    if not p.exists():
        Wd, Ht = 420, 520
        im = Image.new("RGB", (Wd, Ht), hx("#3a2410"))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([10, 10, Wd - 11, Ht - 11], 26, fill=hx("#d8b98a"))
        d.rectangle([10, 10, Wd - 11, 70], fill=hx("#b3431f"))                     # the red header strip
        for cx in (110, 210, 310):
            d.ellipse([cx - 14, 26, cx + 14, 54], fill=hx("#fff4dc"), outline=hx("#3a2410"), width=4)
        d.rounded_rectangle([34, 96, Wd - 35, Ht - 36], 22, fill=hx("#fff4dc"), outline=hx("#3a2410"), width=6)
        size = 300 if n < 10 else 230
        font = ImageFont.truetype(str(FONT), size)
        txt = str(n)
        bb = d.textbbox((0, 0), txt, font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        d.text(((Wd - tw) / 2 - bb[0], 96 + (Ht - 36 - 96 - th) / 2 - bb[1]), txt, font=font, fill=hx("#c8441a"))
        im.save(p)
    return str(p)


def _tile_image():
    from PIL import Image, ImageDraw
    p = TMP / "tile.png"
    if not p.exists():
        n_x, n_y, s = 21, 19, 48
        im = Image.new("RGB", (n_x * s, n_y * s), hx("#8a4a30"))
        d = ImageDraw.Draw(im)
        for i in range(n_x):
            for j in range(n_y):
                shade = ((i * 7 + j * 13) % 5) / 5.0
                c = mix("#c96f4a", "#d98a5a", shade * 0.7)
                d.rectangle([i * s + 3, j * s + 3, (i + 1) * s - 3, (j + 1) * s - 3], fill=hx(c))
        im.save(p)
    return str(p)


def _stripes_image(c1, c2, name, n=12, horizontal=False):
    from PIL import Image, ImageDraw
    p = TMP / f"{name}.png"
    if not p.exists():
        im = Image.new("RGB", (n * 20, n * 20), hx(c2))
        d = ImageDraw.Draw(im)
        for i in range(0, n, 2):
            if horizontal:
                d.rectangle([0, i * 20, n * 20, i * 20 + 19], fill=hx(c1))
            else:
                d.rectangle([i * 20, 0, i * 20 + 19, n * 20], fill=hx(c1))
        im.save(p)
    return str(p)


def _checks_image(c1, c2, name, n=12):
    from PIL import Image, ImageDraw
    p = TMP / f"{name}.png"
    if not p.exists():
        s = 40
        im = Image.new("RGB", (n * s, n * s), hx(c2))
        d = ImageDraw.Draw(im)
        for i in range(n):
            for j in range(n):
                if (i + j) % 2 == 0:
                    d.rectangle([i * s, j * s, (i + 1) * s - 1, (j + 1) * s - 1], fill=hx(c1))
        im.save(p)
    return str(p)


def _plaid_image(name, c1, c2, c3, n=10):
    from PIL import Image, ImageDraw
    p = TMP / f"{name}.png"
    if not p.exists():
        s = 40
        im = Image.new("RGB", (n * s, n * s), hx(c1))
        d = ImageDraw.Draw(im)
        for i in range(0, n, 2):
            d.rectangle([i * s, 0, i * s + s - 1, n * s], fill=hx(c2))
            d.rectangle([0, i * s, n * s, i * s + s - 1], fill=hx(c2))
        for i in range(1, n, 4):
            d.rectangle([i * s, 0, i * s + 8, n * s], fill=hx(c3))
            d.rectangle([0, i * s, n * s, i * s + 8], fill=hx(c3))
        im.save(p)
    return str(p)


def _photo_image():
    """The old house: sky blue with yellow stripes, a white door, a red-brown roof, a green lawn. No text."""
    from PIL import Image, ImageDraw
    p = TMP / "photo.png"
    if not p.exists():
        Wd, Ht = 640, 480
        im = Image.new("RGB", (Wd, Ht), hx("#bfe6ff"))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 360, Wd, Ht], fill=hx("#78c860"))
        d.rectangle([110, 190, 530, 380], fill=hx("#4fb0f2"))
        for x in range(134, 530, 70):
            d.rectangle([x, 190, x + 16, 380], fill=hx(YELLOW))
        d.polygon([(80, 195), (320, 70), (560, 195)], fill=hx("#b3431f"))
        d.rectangle([290, 270, 350, 380], fill=hx("#fffaf0"), outline=hx("#5a3a22"), width=5)
        for x in (160, 430):
            d.rectangle([x, 240, x + 60, 300], fill=hx("#fffaf0"), outline=hx("#5a3a22"), width=5)
        d.ellipse([500, 20, 590, 110], fill=hx("#ffe58a"))
        d.rectangle([0, 0, Wd - 1, Ht - 1], outline=hx("#fffaf0"), width=14)
        im.save(p)
    return str(p)


def imat(kit, name, path, strength=1.0):
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    gc = nt.nodes.new("ShaderNodeTexCoord")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    img = bpy.data.images.load(path)
    img.colorspace_settings.name = "sRGB"
    tex.image = img
    return m, tex


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def wallbox(kit, name, x0, x1, y0, y1, z0, z1, mat):
    return kit.box(name, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), mat)


def chair(kit, name, x, y, yaw_deg, wood):
    """A plain wooden chair; it faces -y at yaw 0 (the back is at +y)."""
    root = kit.empty(name, (x, y, 0), rot=(0, 0, math.radians(yaw_deg)))
    kit.box(name + ".seat", (0.46, 0.46, 0.05), (0, 0, 0.46), wood, root, bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"{name}.leg{sx}{sy}", (0.05, 0.05, 0.44), (sx * 0.2, sy * 0.2, 0.22), wood, root)
    kit.box(name + ".back", (0.46, 0.05, 0.5), (0, 0.21, 0.74), wood, root, bevel=0.01)
    return root


# ---------------------------------------------------------------------------------------------- the kitchen
def build_kit(kit):
    pl = kit.plastic
    wall = pl("#f3e6d0", 0.85, spec=0.03)
    trim = pl("#fffaf0", 0.6)
    cab = pl("#f4f1ea", 0.7, spec=0.05)
    wood = pl("#a8743f", 0.6)
    cx, cy = (G.AX0 + G.AX1) / 2, (G.AY0 + G.AY1) / 2
    lx, ly = G.AX1 - G.AX0, G.AY1 - G.AY0
    kit.box("kit.floor", (lx + 1, ly + 1, 0.1), (cx, cy, -0.05), pl("#c96f4a", 0.7))
    m, _ = imat(kit, "kit.tiles", _tile_image(), 0.5)
    noshadow(kit.plane("kit.tiles", (lx, ly), (cx, cy, 0.004), m))
    kit.box("kit.ceiling", (lx + 1, ly + 1, 0.2), (cx, cy, G.AH + 0.1), kit.emit("#fff1dc", 0.3, "kitceil"))
    H = G.AH + 0.3
    kit.box("kit.wall.s", (lx + 0.8, 0.4, H), (cx, G.AY0 - 0.2, H / 2 - 0.05), wall)
    kit.box("kit.wall.n", (lx + 0.8, 0.4, H), (cx, G.AY1 + 0.2, H / 2 - 0.05), wall)
    # west wall with the window: y -0.5..1.1, z 1.0..2.3
    wy0, wy1, wz0, wz1 = G.WINDOW_Y - 0.8, G.WINDOW_Y + 0.8, 1.0, 2.3
    for nm, (a, b, c, d_) in {"low": (G.AY0 - 0.4, G.AY1 + 0.4, 0.0, wz0), "high": (G.AY0 - 0.4, G.AY1 + 0.4, wz1, H),
                              "s": (G.AY0 - 0.4, wy0, wz0, wz1), "n": (wy1, G.AY1 + 0.4, wz0, wz1)}.items():
        wallbox(kit, f"kit.wall.w.{nm}", G.AX0 - 0.4, G.AX0, a, b, c, d_, wall)
    # east wall with the back door: y -1.7..-0.6, z 0..2.1
    dy0, dy1, dz = G.DOOR_Y - 0.55, G.DOOR_Y + 0.55, 2.1
    for nm, (a, b, c, d_) in {"s": (G.AY0 - 0.4, dy0, 0.0, H), "n": (dy1, G.AY1 + 0.4, 0.0, H),
                              "lintel": (dy0, dy1, dz, H)}.items():
        wallbox(kit, f"kit.wall.e.{nm}", G.AX1, G.AX1 + 0.4, a, b, c, d_, wall)
    # daylight beyond the window and the door (bright, flat, nothing to read)
    sky = kit.emit("#cfeaff", 0.9, "kitsky")
    noshadow(kit.box("kit.sky.w", (0.1, 8, 5), (G.AX0 - 1.6, G.WINDOW_Y, 1.8), sky))
    noshadow(kit.box("kit.sky.e", (0.1, 8, 4), (G.AX1 + 2.0, G.DOOR_Y, 1.6), kit.emit("#cfeaff", 0.9, "kitsky2")))
    noshadow(kit.box("kit.lawn.e", (3.0, 8, 0.1), (G.AX1 + 1.5, G.DOOR_Y, -0.05), pl("#78c860", 0.9)))
    # window frame, sill and the door frame
    for nm, (sx, sy, sz, x, y, z) in {
            "top": (0.12, 1.7, 0.08, G.AX0 + 0.06, G.WINDOW_Y, wz1 + 0.04), "bot": (0.2, 1.8, 0.07, G.AX0 + 0.1, G.WINDOW_Y, wz0 - 0.03),
            "l": (0.12, 0.08, 1.3, G.AX0 + 0.06, wy0 - 0.04, 1.65), "r": (0.12, 0.08, 1.3, G.AX0 + 0.06, wy1 + 0.04, 1.65),
            }.items():
        kit.box("kit.win." + nm, (sx, sy, sz), (x, y, z), trim)
    for nm, (sx, sy, sz, x, y, z) in {
            "top": (0.14, 1.2, 0.08, G.AX1 - 0.07, G.DOOR_Y, dz + 0.04), "l": (0.14, 0.08, dz, G.AX1 - 0.07, dy0 - 0.04, dz / 2),
            "r": (0.14, 0.08, dz, G.AX1 - 0.07, dy1 + 0.04, dz / 2)}.items():
        kit.box("kit.door." + nm, (sx, sy, sz), (x, y, z), trim)
    # a low wooden cupboard under the window (so the wall below the sill is not a blank white field)
    kit.box("kit.winbase", (0.5, 2.1, 0.9), (G.AX0 + 0.25, G.WINDOW_Y, 0.45), pl("#c58a50", 0.6), bevel=0.01)
    kit.box("kit.winbase.top", (0.56, 2.16, 0.05), (G.AX0 + 0.28, G.WINDOW_Y, 0.925), wood)
    for i, yy in enumerate((-0.4, 0.3, 1.0)):
        kit.box(f"kit.winbase.door{i}", (0.02, 0.62, 0.7), (G.AX0 + 0.51, G.WINDOW_Y + (yy - 0.3), 0.45), pl("#a8743f", 0.6), bevel=0.01)
        kit.box(f"kit.winbase.knob{i}", (0.03, 0.03, 0.03), (G.AX0 + 0.53, G.WINDOW_Y + (yy - 0.3) + 0.2, 0.7), pl("#c98a18", 0.3, spec=0.7))
    # cabinets along the north wall, with a wooden worktop, and uppers
    kit.box("kit.cab.low", (5.9, 0.62, 0.88), (-1.25, G.AY1 - 0.31, 0.44), cab, bevel=0.01)
    kit.box("kit.cab.top", (5.96, 0.66, 0.05), (-1.25, G.AY1 - 0.33, 0.905), wood)
    kit.box("kit.cab.up", (5.9, 0.36, 0.8), (-1.25, G.AY1 - 0.18, 2.0), cab, bevel=0.01)
    for i in range(10):
        x = -4.0 + i * 0.58
        kit.box(f"kit.cab.seam{i}", (0.015, 0.02, 0.8), (x, G.AY1 - 0.62, 0.44), pl("#bfb8a8", 0.7))
        kit.box(f"kit.cab.knob{i}", (0.03, 0.03, 0.03), (x + 0.2, G.AY1 - 0.64, 0.75), pl("#c98a18", 0.3, spec=0.7))
    # the fridge: tall and white, a seam, a handle, the calendar and (on the cue) the fingerprints
    fx, fy = G.FRIDGE
    white = pl("#e9ecef", 0.5, spec=0.15)
    kit.box("kit.fridge", (0.95, 0.75, 1.95), (fx, fy, 0.975), white, bevel=0.02)
    kit.box("kit.fridge.seam", (0.93, 0.01, 0.015), (fx, G.FRIDGE_FACE - 0.005, 1.28), pl("#9aa0a8", 0.5))
    kit.box("kit.fridge.handle", (0.035, 0.05, 0.5), (fx - 0.36, G.FRIDGE_FACE - 0.035, 1.55), pl("#aeb4bc", 0.3, spec=0.7))
    kit.box("kit.fridge.handle2", (0.035, 0.05, 0.4), (fx - 0.36, G.FRIDGE_FACE - 0.035, 0.85), pl("#aeb4bc", 0.3, spec=0.7))
    # the calendar page, on a dark backing, 1.5 cm proud of the door
    cxx, cyy, czz = G.CAL
    cb_ = kit.box("kit.cal.back", (0.36, 0.02, 0.44), (cxx, G.FRIDGE_FACE - 0.012, czz), pl("#3a2410", 0.6))
    m, tex = imat(kit, "kit.cal", _cal_image(1), 1.0)
    cp_ = kit.plane("kit.cal.page", (0.33, 0.41), (cxx, G.FRIDGE_FACE - 0.026, czz), m, rot=(math.pi / 2, 0, 0))
    noshadow(cp_)
    W["calfridge"] = [cb_, cp_]
    W["caltex"] = tex
    # the fingerprints: three sky-blue ovals, at a teen's shoulder height
    pm = pl(BLUE, 0.5)
    W["prints"] = []
    for i, (px, pz) in enumerate(G.PRINTS):
        ob = kit.cyl(f"kit.print{i}", 0.07, 0.012, (px, G.FRIDGE_FACE - 0.009, pz), pm, rot=(math.pi / 2, 0, 0.0), n=20)
        ob.scale = (1.0, 1.4, 1.0)
        ob.hide_render = True
        W["prints"].append(ob)
    # the tally: two short pencil strokes low on the fridge's west side
    for i in range(2):
        kit.box(f"kit.tally{i}", (0.012, 0.02, 0.2), (fx - 0.481, fy - 0.1 - 0.07 * i, 0.95), pl("#3a3a40", 0.8))
    # the table, its two chairs, and the old house's photo propped on it
    tx, ty = G.TABLE
    kit.box("kit.table.top", (G.TABLE_W, G.TABLE_D, 0.05), (tx, ty, G.TABLE_H), wood, bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"kit.table.leg{sx}{sy}", (0.06, 0.06, G.TABLE_H), (tx + sx * 0.3, ty + sy * 0.68, G.TABLE_H / 2), wood)
    chair(kit, "kit.chair.leo", G.LEO[0], G.LEO[1] - 0.95, 180, wood)       # backs away from the table, facing north
    chair(kit, "kit.chair.mom", G.MOM[0], G.MOM[1] + 0.95, 0, wood)
    root = kit.empty("kit.photo", (tx, ty - 0.2, G.TABLE_H + 0.035))
    kit.box("kit.photo.frame", (0.66, 0.5, 0.02), (0, 0, 0.01), pl("#fffaf0", 0.5), root, bevel=0.008)
    m, _ = imat(kit, "kit.photo", _photo_image(), 0.8)
    noshadow(kit.plane("kit.photo.img", (0.6, 0.45), (0, 0, 0.0225), m, root))
    W["photo"] = [root] + list(root.children_recursive)
    # three plain moving boxes by the east wall, the curtains (hidden until the cue), a plant, a rug
    boxm = pl("#c49a6c", 0.8, spec=0.02)
    tape = pl("#e8d3a8", 0.6)
    for i, (x, y, s, z0) in enumerate(((-3.65, -1.5, 0.62, 0.0), (-3.7, -2.25, 0.55, 0.0), (-3.65, -1.55, 0.5, 0.62))):
        kit.box(f"kit.moving{i}", (s, s, s), (x, y, z0 + s / 2), boxm, bevel=0.01)
        kit.box(f"kit.moving{i}.tape", (0.1, s + 0.01, s + 0.01), (x, y, z0 + s / 2), tape)
    kit.box("kit.rug", (2.6, 1.7, 0.02), (0.0, 0.35, 0.012), pl("#f2e2b8", 0.9, spec=0.02))
    kit.prop("houseplant_1", (-3.7, 2.6, 0), scale=2.0)
    cmat, _ = imat(kit, "kit.curtain", _stripes_image(YELLOW, "#fffaf0", "curtain", 12), 0.95)
    W["curtain"] = []
    for i, yc in enumerate((G.WINDOW_Y - 0.7, G.WINDOW_Y + 0.7)):
        ob = kit.plane(f"kit.curtain{i}", (0.8, 1.9), (G.AX0 + 0.16, yc, 1.55), cmat, rot=(math.pi / 2, 0, math.pi / 2))
        ob.hide_render = True
        noshadow(ob)
        W["curtain"].append(ob)
    kit.box("kit.rod", (0.04, 2.6, 0.04), (G.AX0 + 0.2, G.WINDOW_Y, 2.55), pl("#8a6a48", 0.5))
    # Mom's two flat palms on the table (shown by the `palms` cue): skin, palm down, fingers to the middle, a coral cuff
    skin, cuff = pl(SKIN, 0.6), pl("#f08a74", 0.7)
    W["palms"] = []
    zt = G.TABLE_H + 0.025
    for k, yoff in enumerate((-0.2, 0.2)):
        hx_, hy_ = 0.02, G.TABLE[1] + yoff
        parts = [kit.box(f"kit.palm{k}", (0.17, 0.2, 0.04), (hx_, hy_, zt + 0.022), skin, bevel=0.012)]
        for j, (dy, ln) in enumerate(((-0.078, 0.13), (-0.026, 0.16), (0.026, 0.17), (0.078, 0.14))):
            parts.append(kit.box(f"kit.palm{k}.f{j}", (ln, 0.042, 0.034), (hx_ - 0.085 - ln / 2 + 0.01, hy_ + dy, zt + 0.019), skin, bevel=0.012))
        sgn = 1 if k else -1
        parts.append(kit.box(f"kit.palm{k}.th", (0.13, 0.05, 0.034), (hx_ - 0.07, hy_ + sgn * 0.13, zt + 0.019), skin, rot=(0, 0, sgn * 0.5), bevel=0.012))
        parts.append(kit.box(f"kit.palm{k}.cuff", (0.34, 0.17, 0.1), (hx_ + 0.255, hy_, zt + 0.05), cuff, bevel=0.02))
        for ob in parts:
            ob.hide_render = True
        W["palms"] += parts
    # Leo's two flat hands resting on Mom's palms (the `leohands` cue: 1 skin, 2 blue): fingers toward Mom, a plum cuff on his side
    W["lh1"], W["lh2"] = [], []
    for which, col in (("lh1", SKIN), ("lh2", BLUE)):
        hm, cm = pl(col, 0.6), pl("#7a4a78", 0.7)
        for k, yoff in enumerate((-0.2, 0.2)):
            hx_, hy_ = 0.02 - 0.03, G.TABLE[1] + yoff
            zh = zt + 0.06
            parts = [kit.box(f"kit.{which}{k}", (0.17, 0.2, 0.04), (hx_, hy_, zh), hm, bevel=0.012)]
            for j, (dy, ln) in enumerate(((-0.078, 0.13), (-0.026, 0.16), (0.026, 0.17), (0.078, 0.14))):
                parts.append(kit.box(f"kit.{which}{k}.f{j}", (ln, 0.042, 0.034), (hx_ + 0.085 + ln / 2 - 0.01, hy_ + dy, zh - 0.003), hm, bevel=0.012))
            parts.append(kit.box(f"kit.{which}{k}.cuff", (0.3, 0.17, 0.1), (hx_ - 0.235, hy_, zh + 0.01), cm, bevel=0.02))
            for ob in parts:
                ob.hide_render = True
            W[which] += parts
    # a white window frame in the near plane of S01b (the `pratframe` cue), so Mr. Pratt is seen through a window
    W["pratframe"] = []
    fw = pl("#fffaf0", 0.5)
    for nm, (sx, sy, sz, y, z) in {"top": (0.08, 1.2, 0.12, G.WINDOW_Y, 2.4), "sill": (0.2, 1.2, 0.08, G.WINDOW_Y, 1.02),
                                   "l": (0.08, 0.14, 1.4, G.WINDOW_Y - 0.52, 1.7), "r": (0.08, 0.14, 1.4, G.WINDOW_Y + 0.52, 1.7),
                                   }.items():
        ob = kit.box("kit.pf." + nm, (sx, sy, sz), (-3.95, y, z), fw, bevel=0.008)
        ob.hide_render = True
        W["pratframe"].append(ob)
    # the lawn outside the west window, a soft light on whoever stands there (Mr. Pratt, in the opening)
    kit.box("kit.lawn.w", (4.0, 8, 0.1), (G.AX0 - 2.6, G.WINDOW_Y, -0.05), pl("#78c860", 0.9))
    pw = kit.light("kit.prattwin", "AREA", (-2.6, G.WINDOW_Y, 2.3), 160, "#fff3e0", size=2.0, shadow=False)
    kit.aim(pw, (-5.0, G.WINDOW_Y, 1.3))
    # soft constant light: no shadow, nothing flickers
    for i, (x, y) in enumerate(((0.0, 0.3), (-2.4, -1.5), (2.4, -1.5), (2.2, 1.0), (-2.4, 1.6))):
        a = kit.light(f"kit.fill{i}", "AREA", (x, y, G.AH - 0.15), 95, "#fff3e0", size=2.8, shadow=False)
        kit.aim(a, (x, y, 0.0))
    s = kit.light("kit.face", "AREA", (0.2, -3.8, 2.3), 85, "#fff6ec", size=2.5, shadow=False)
    kit.aim(s, (0.2, 0.3, 1.3))
    n = kit.light("kit.face2", "AREA", (0.2, 3.0, 2.3), 40, "#fff6ec", size=2.5, shadow=False)
    kit.aim(n, (0.2, 0.0, 1.3))


# ---------------------------------------------------------------------------------------------- outdoors helpers
def lawn(kit, x, y, sx, sy, tint="#8fe07a"):
    return kit.box(f"lawn{x}{y}", (sx, sy, 0.3), (x, y, -0.15), kit.texture("grass", 0.5, tint=tint))


def outdoor_lights(kit, name, x, y, face_at, size=3.0, energy=900):
    a = kit.light(f"{name}.face", "AREA", (x, y - 5.0, 3.6), energy, "#fff3e0", size=size, shadow=False)
    kit.aim(a, face_at)
    b = kit.light(f"{name}.top", "AREA", (x, y, 5.5), energy * 0.6, "#fff8ee", size=6.0, shadow=False)
    kit.aim(b, (x, y, 0.0))


def build_porch(kit):
    pl = kit.plastic
    px, py = G.PORCH
    lawn(kit, px, py, 30, 24)
    deck = kit.texture("wood", 0.7, tint="#e0b078")
    kit.box("porch.deck", (6.4, 4.4, 0.3), (px, py + 0.3, 0.15), deck)
    siding = pl("#f6e8c8", 0.8, spec=0.03)
    kit.box("porch.wall", (7.4, 0.3, 3.3), (px, py + 2.65, 1.65), siding)
    kit.box("porch.door", (1.0, 0.06, 2.1), (px + 2.2, py + 2.47, 1.35), pl("#fffaf0", 0.6))
    kit.box("porch.doorknob", (0.05, 0.06, 0.05), (px + 1.8, py + 2.43, 1.35), pl("#c98a18", 0.3, spec=0.7))
    kit.box("porch.win", (1.1, 0.06, 1.0), (px - 2.0, py + 2.47, 1.7), kit.emit("#cfeaff", 0.8, "porchwin"))
    for sx in (-1, 1):
        kit.box(f"porch.post{sx}", (0.18, 0.18, 3.0), (px + sx * 2.1, py - 1.7, 1.8), pl("#fffaf0", 0.6))
    kit.box("porch.beam", (4.7, 0.2, 0.2), (px, py - 1.7, 2.85), pl("#fffaf0", 0.6))
    kit.box("porch.roof", (7.0, 4.6, 0.15), (px, py + 0.4, 3.45), pl("#b3431f", 0.8))
    # the swing: a pivot on a beam under the roof, two chains, a sky-blue seat and back (1.3 m wide)
    piv = kit.empty("porch.pivot", (px, py - 0.3, 3.3))
    W["swing"] = piv
    kit.box("porch.swingbeam", (1.8, 0.2, 0.2), (px, py - 0.3, 3.3), pl("#fffaf0", 0.6))
    blue = pl("#7fc8f8", 0.55, spec=0.1)
    for sx in (-1, 1):
        kit.box(f"porch.chain{sx}", (0.03, 0.03, 2.6), (sx * 0.58, 0, -1.3), pl("#6a6e78", 0.4, spec=0.6), piv)
    kit.box("porch.seat", (1.3, 0.62, 0.09), (0, 0, -2.6), blue, piv, bevel=0.02)
    kit.box("porch.back", (1.3, 0.07, 0.6), (0, 0.3, -2.28), blue, piv, rot=(math.radians(-8), 0, 0), bevel=0.02)
    for sx in (-1, 1):
        kit.box(f"porch.arm{sx}", (0.07, 0.62, 0.07), (sx * 0.65, 0, -2.35), blue, piv)
        kit.box(f"porch.armpost{sx}", (0.07, 0.07, 0.3), (sx * 0.65, -0.25, -2.47), blue, piv)
    # red geraniums in a clay pot, bushes and a tree for depth
    kit.cyl("porch.pot", 0.24, 0.34, (px - 2.5, py - 1.2, 0.47), pl("#c96f4a", 0.8), n=16, r2=0.3)
    for i in range(6):
        a = i * 1.05
        kit.sphere(f"porch.gera{i}", 0.13, (px - 2.5 + 0.18 * math.cos(a), py - 1.2 + 0.18 * math.sin(a), 0.78 + 0.05 * (i % 2)),
                   pl("#e04a5a", 0.6))
    kit.sphere("porch.geramid", 0.15, (px - 2.5, py - 1.2, 0.9), pl("#e04a5a", 0.6))
    for i, x in enumerate((-9.0, -6.0, 6.0, 9.0)):
        kit.prop("bush_1", (px + x, py + 4.0, 0), scale=1.6)
    kit.prop("commontree_1", (px + 8.5, py + 1.5, 0), scale=1.4)
    kit.prop("commontree_2", (px - 9.5, py + 2.0, 0), scale=1.4)
    outdoor_lights(kit, "porch", px, py - 1.0, (px, py - 1.0, 1.3), 3.0, 450)


def build_pratt(kit):
    pl = kit.plastic
    px, py = G.PRATT
    lawn(kit, px, py + 2, 30, 24)
    wall = pl("#f3e6d0", 0.85, spec=0.03)
    kit.box("pratt.deck", (4.2, 2.4, 0.3), (px + 0.4, py + 3.4, 0.15), kit.texture("wood", 0.7, tint="#e0b078"))
    kit.box("pratt.wall", (8.0, 0.3, 3.4), (px, py + 4.75, 1.7), wall)
    kit.box("pratt.door", (1.0, 0.06, 2.1), (px + 1.6, py + 4.57, 1.35), pl("#e04a5a", 0.6))
    # a round porthole window with a ring (the houseboat joke), a roof over the deck, two posts
    kit.cyl("pratt.ring", 0.52, 0.08, (px - 1.5, py + 4.57, 1.8), pl("#fffaf0", 0.4), rot=(math.pi / 2, 0, 0), n=24)
    kit.cyl("pratt.glass", 0.4, 0.1, (px - 1.5, py + 4.54, 1.8), kit.emit("#cfeaff", 1.0, "prattglass"), rot=(math.pi / 2, 0, 0), n=24)
    for sx in (-1, 1):
        kit.box(f"pratt.post{sx}", (0.16, 0.16, 2.9), (px + 0.4 + sx * 1.9, py + 2.3, 1.75), pl("#fffaf0", 0.6))
    kit.box("pratt.roof", (4.8, 3.0, 0.14), (px + 0.4, py + 3.5, 3.25), pl("#4a7fb0", 0.8))
    # the low white fence across the foreground, with a rail
    fence = pl("#d6cdb8", 0.6)
    for i in range(-8, 9):
        if -1 <= i <= 3:
            continue
        kit.box(f"pratt.fence{i}", (0.14, 0.05, 0.7), (px + i * 0.4 + 0.2, py + 0.9, 0.35), fence)
    for z in (0.25, 0.6):
        kit.box(f"pratt.rail{z}", (3.1, 0.05, 0.06), (px - 2.4, py + 0.86, z), fence)
        kit.box(f"pratt.railb{z}", (3.1, 0.05, 0.06), (px + 3.0, py + 0.86, z), fence)
    kit.prop("commontree_1", (px - 6.5, py + 3.0, 0), scale=1.4)
    kit.prop("commontree_2", (px + 7.0, py + 2.0, 0), scale=1.4)
    for x in (-3.5, 3.5):
        kit.prop("bush_1", (px + x, py + 1.7, 0), scale=0.9)
    outdoor_lights(kit, "pratt", px + 0.4, py + 1.5, (px + 0.4, py + 3.0, 1.3), 3.0, 450)
    n_ = kit.light("pratt.leo", "AREA", (px + 0.4, py + 6.0, 3.6), 650, "#fff3e0", size=3.0, shadow=False)
    kit.aim(n_, (px, py - 0.1, 1.4))


def build_street(kit):
    pl = kit.plastic
    sx, sy = G.STREET
    lawn(kit, sx + 7, sy + 3, 50, 30)
    walk = pl("#b3a68a", 0.85, spec=0.02)
    kit.box("street.path", (50, 4.4, 0.08), (sx + 7, sy + 0.5, 0.04), walk)
    # the checked house (terracotta and white), with a white door
    m, _ = imat(kit, "street.checks", _checks_image("#c96f4a", "#fffaf0", "checks", 12), 0.95)
    kit.box("street.checkwall", (6.0, 0.3, 3.0), (sx, sy + 6.0, 1.5), kit.plastic("#fffaf0", 0.8))
    noshadow(kit.plane("street.checks", (6.0, 3.0), (sx, sy + 5.84, 1.5), m, rot=(math.pi / 2, 0, 0)))
    kit.box("street.roof", (6.6, 1.6, 0.2), (sx, sy + 6.0, 3.15), pl("#7a3b2a", 0.8))
    kit.box("street.door", (1.0, 0.06, 2.1), (sx + 1.8, sy + 5.8, 1.05), pl("#fffaf0", 0.6))
    # the bench in front of it
    wood = pl("#a8743f", 0.6)
    kit.box("street.bench.seat", (1.8, 0.5, 0.07), (sx, sy + 3.3, 0.46), wood)
    kit.box("street.bench.back", (1.8, 0.06, 0.5), (sx, sy + 3.55, 0.75), wood)
    for sxx in (-1, 1):
        kit.box(f"street.bench.leg{sxx}", (0.07, 0.5, 0.46), (sxx * 0.8 + sx, sy + 3.3, 0.23), pl("#4a4a50", 0.5))
    # the checked print the touch leaves on the bench (shown by the `print` cue)
    pr = kit.plane("street.print", (0.9, 0.44), (sx + 0.3, sy + 3.3, 0.512), imat(kit, "street.printm", _checks_image("#c96f4a", "#fffaf0", "checks3", 6), 0.95)[0])
    pr.hide_render = True
    noshadow(pr)
    W["benchprint"] = pr
    # the green plaid house at x + 14
    m2, _ = imat(kit, "street.plaid", _plaid_image("plaidgreen", "#3f9a5a", "#2f7a46", "#f2f2c0"), 0.95)
    hx2 = sx + 14.0
    kit.box("street.plaidwall", (6.0, 0.3, 3.0), (hx2, sy + 6.0, 1.5), kit.plastic("#3f9a5a", 0.8))
    noshadow(kit.plane("street.plaid", (6.0, 3.0), (hx2, sy + 5.84, 1.5), m2, rot=(math.pi / 2, 0, 0)))
    kit.box("street.roof2", (6.6, 1.6, 0.2), (hx2, sy + 6.0, 3.15), pl("#4a5a3a", 0.8))
    kit.box("street.door2", (1.0, 0.06, 2.1), (hx2 - 1.8, sy + 5.8, 1.05), pl("#fffaf0", 0.6))
    for x in (-5.5, 4.5, 9.0, 19.0):
        kit.prop("commontree_1", (sx + x, sy + 8.0, 0), scale=1.3)
    for x in (-3.5, 3.5, 11.0, 17.0):
        kit.prop("bush_1", (sx + x, sy + 5.0, 0), scale=1.0)
    outdoor_lights(kit, "street1", sx, sy + 1.0, (sx, sy + 2.5, 1.3), 3.5, 450)
    outdoor_lights(kit, "street2", hx2, sy + 1.0, (hx2, sy + 2.5, 1.3), 3.5, 450)


def build_room(kit):
    pl = kit.plastic
    rx, ry = G.ROOM
    wall = pl("#e9efe0", 0.85, spec=0.03)
    kit.box("room.floor", (8, 8, 0.1), (rx, ry, -0.05), kit.texture("wood", 0.7, tint="#e8c890"))
    kit.box("room.ceiling", (8, 8, 0.2), (rx, ry, 2.9 + 0.1), kit.emit("#fff1dc", 0.3, "roomceil"))
    kit.box("room.wall.n", (8, 0.4, 3.2), (rx, ry + 3.7, 1.55), wall)
    kit.box("room.wall.s", (8, 0.4, 3.2), (rx, ry - 3.7, 1.55), wall)
    kit.box("room.wall.w", (0.4, 8, 3.2), (rx - 3.7, ry, 1.55), wall)
    kit.box("room.wall.e", (0.4, 8, 3.2), (rx + 3.7, ry, 1.55), wall)
    # the bed: head against the north wall
    bx, by = rx + 0.3, ry + 2.35
    kit.box("room.bed.frame", (1.1, 2.0, 0.28), (bx, by, 0.17), pl("#a8743f", 0.6))
    kit.box("room.bed.mattress", (1.0, 1.9, 0.22), (bx, by, 0.42), pl("#efece4", 0.8))
    kit.box("room.bed.blanket", (1.04, 1.2, 0.1), (bx, by - 0.35, 0.57), pl("#eeeae2", 0.8), bevel=0.02)
    kit.box("room.bed.head", (1.2, 0.08, 0.9), (bx, ry + 3.46, 0.7), pl("#a8743f", 0.6))
    pillow = kit.box("room.pillow", (0.64, 0.42, 0.16), (bx, by + 0.7, 0.62), pl("#f1efea", 0.9, spec=0.02), bevel=0.06, seg=3)
    # one soft yellow stripe across the pillowcase, 1 cm proud on top and at the front
    kit.box("room.pillow.stripe", (0.17, 0.44, 0.18), (bx + 0.02, by + 0.7, 0.62), pl(YELLOW, 0.7), bevel=0.04, seg=3)
    kit.box("room.window", (0.06, 1.4, 1.2), (rx - 3.48, ry + 0.5, 1.7), kit.emit("#cfeaff", 0.8, "roomwin"))
    kit.box("room.rug", (2.2, 1.4, 0.02), (rx - 0.4, ry - 0.2, 0.012), pl("#f2c05a", 0.9, spec=0.02))
    kit.box("room.shelf", (1.2, 0.3, 0.05), (rx + 2.4, ry + 3.4, 1.6), pl("#a8743f", 0.6))
    for i, c in enumerate(("#e04a5a", "#4a8fd8", "#f2c05a")):
        kit.box(f"room.book{i}", (0.1, 0.2, 0.3), (rx + 2.1 + 0.2 * i, ry + 3.4, 1.78), pl(c, 0.7))
    for i, (x, y) in enumerate(((0, 0), (-2, 1.5), (2, -1.5))):
        a = kit.light(f"room.fill{i}", "AREA", (rx + x, ry + y, 2.75), 90, "#fff3e0", size=2.8, shadow=False)
        kit.aim(a, (rx + x, ry + y, 0.0))
    s = kit.light("room.face", "AREA", (rx + 1.5, ry - 3.2, 2.3), 85, "#fff6ec", size=2.5, shadow=False)
    kit.aim(s, (rx + 0.5, ry + 2.0, 1.3))


def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    m, tex = imat(kit, "tag", _cal_image(1), 1.0)
    pl = kit.plane("tag.plane", (0.83, 1.0), (0, 0, 0), m, root)
    noshadow(pl)
    W["tagtex"] = tex
    W["imgs"] = {}
    W["day"] = 1


# ---------------------------------------------------------------------------------------------- build / animate
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    build_kit(kit)
    build_porch(kit)
    build_pratt(kit)
    build_street(kit)
    build_room(kit)
    build_tag(kit)
    W["extras_done"] = False
    return {}


def _head_stripe(kit, who, u):
    """A tall brown block quiff (and, for the blue Leos, a yellow stripe through it at strength u)."""
    pl = kit.plastic
    hg = bpy.data.objects.get(f"{who}.headg")
    if hg is None:
        return False
    hair = "#5a3a22"
    kit.box(f"{who}.quiff", (0.86, 0.78, 0.5), (0, -0.2, 0.92), pl(hair, 0.65), hg, rot=(0.12, 0, 0), bevel=0.14)
    if u > 0:
        kit.box(f"{who}.quiffstripe", (0.2, 0.82, 0.54), (0.0, -0.2, 0.93), pl(mix(hair, YELLOW, u), 0.65), hg, rot=(0.12, 0, 0), bevel=0.08)
    return True


def _sweaters(kit, who):
    """Three sweaters: the plum one on top, an orange one and an oat one showing at the hem, the cuffs and the neck."""
    pl = kit.plastic
    orange, oat = pl("#f29b4b", 0.8), pl("#d9cdb4", 0.8)
    bw = 1.1
    t = bpy.data.objects[f"{who}.torso"]
    kit.box(f"{who}.hem.oat", (2.0 * bw + 0.05, 1.05, 0.22), (0, 0, 0.11), oat, t, bevel=0.04)
    kit.box(f"{who}.hem.orange", (2.0 * bw + 0.05, 1.05, 0.2), (0, 0, 0.32), orange, t, bevel=0.04)
    kit.box(f"{who}.neck.orange", (1.3 * bw, 1.06, 0.2), (0, 0, 1.97), orange, t, bevel=0.05)
    kit.box(f"{who}.neck.oat", (1.0 * bw, 1.08, 0.12), (0, 0, 2.08), oat, t, bevel=0.04)
    for sx in (-1, 1):
        arm = bpy.data.objects[f"{who}.arm{sx}"]
        kit.box(f"{who}.cuff.orange{sx}", (0.98 * bw + 0.04, 1.04, 0.2), (0, 0, -1.4), orange, arm, bevel=0.04)
        kit.box(f"{who}.cuff.oat{sx}", (0.98 * bw + 0.06, 1.06, 0.2), (0, 0, -1.58), oat, arm, bevel=0.04)


def attach_extras(kit):
    pl = kit.plastic
    if W.get("extras_done"):
        return
    names = ("me", "sw", "mf1", "mf2", "meb", "mom", "pratt")
    if any(bpy.data.objects.get(f"{n}.headg") is None for n in names):
        return
    for who, u in (("me", 0.0), ("sw", 0.0), ("mf1", 0.66), ("mf2", 0.33), ("meb", 1.0)):
        _head_stripe(kit, who, u)
        if who != "me":
            _sweaters(kit, who)
    # Mom: a big curly black bun
    black = pl("#15151a", 0.7)
    mh = bpy.data.objects["mom.headg"]
    for i, (x, y, z, r) in enumerate(((0, 0.18, 0.98, 0.34), (-0.3, 0.2, 0.86, 0.25), (0.3, 0.2, 0.86, 0.25),
                                       (-0.16, 0.2, 1.2, 0.22), (0.16, 0.2, 1.2, 0.22), (0, 0.22, 1.3, 0.2))):
        kit.sphere(f"mom.curl{i}", r, (x, y, z), black, mh)
    # Mom's cardigan: a navy shirt panel down the open front, and (shown at the end) a little blue rubbed onto it
    mt = bpy.data.objects["mom.torso"]
    kit.box("mom.navy", (0.7, 0.03, 1.6), (0, -0.505, 0.95), pl("#2e3f73", 0.7), mt, bevel=0.01)
    pat = kit.box("mom.rub", (0.42, 0.03, 0.42), (-0.55, -0.52, 1.2), pl("#9fc6dc", 0.7), mt, rot=(0, 0.2, 0.5), bevel=0.12)
    pat.hide_render = True
    W["rub"] = [pat]
    for sx in (-1, 1):
        ma = bpy.data.objects[f"mom.arm{sx}"]
        sm = kit.box(f"mom.rub.arm{sx}", (0.04, 0.62, 0.62), (sx * 0.52, 0, -0.75), pl("#8cc4ee", 0.7), ma, bevel=0.14)
        sm.hide_render = True
        W["rub"].append(sm)
    sm = kit.box("mom.rub.back", (0.5, 0.04, 0.5), (0.3, 0.52, 1.1), pl("#8cc4ee", 0.7), mt, bevel=0.14)
    sm.hide_render = True
    W["rub"].append(sm)
    # Mr. Pratt: a white mustache, a darker waterline across his middle and three navy portholes on the chest
    ph = bpy.data.objects["pratt.headg"]
    white = pl("#f4f4f4", 0.8)
    for sx in (-1, 1):
        kit.box(f"pratt.stache{sx}", (0.34, 0.1, 0.12), (sx * 0.17, -0.64, -0.2), white, ph, rot=(0, sx * 0.25, 0), bevel=0.03)
    pt = bpy.data.objects["pratt.torso"]
    kit.box("pratt.water", (2.05, 1.05, 1.0), (0, 0, 0.5), pl("#137082", 0.7), pt, bevel=0.02)
    for i, x in enumerate((-0.6, 0.0, 0.6)):
        kit.cyl(f"pratt.port{i}", 0.2, 0.04, (x, -0.51, 1.5), pl("#1c2a52", 0.5), pt, rot=(math.pi / 2, 0, 0), n=16)
        kit.cyl(f"pratt.portin{i}", 0.12, 0.05, (x, -0.52, 1.5), pl("#e8f4f8", 0.5), pt, rot=(math.pi / 2, 0, 0), n=16)
    W["extras_done"] = True


def animate(kit, story, tl, t, ctx):
    attach_extras(kit)
    # ---- the calendar (fridge page and the HUD copy)
    day = int(round(sample("day", tl, t, {"n": 1})["n"]))
    if day != W["day"]:
        if day not in W["imgs"]:
            img = bpy.data.images.load(_cal_image(day))
            img.colorspace_settings.name = "sRGB"
            W["imgs"][day] = img
        W["tagtex"].image = W["imgs"][day]
        W["caltex"].image = W["imgs"][day]
        W["day"] = day
    # ---- the things the cues show
    on = sample("prints", tl, t, {"v": 0.0})["v"] > 0.5
    for ob in W.get("prints", []):
        ob.hide_render = not on
    cv = sample("curtain", tl, t, {"v": 0.0})["v"] > 0.5
    for ob in W.get("curtain", []):
        ob.hide_render = not cv
    if "photo" in W:
        pv = sample("photo", tl, t, {"v": 0.0})["v"] < 0.5
        for ob in W["photo"]:
            ob.hide_render = pv
    if "benchprint" in W:
        W["benchprint"].hide_render = sample("print", tl, t, {"v": 0.0})["v"] < 0.5
    if W.get("rub") is not None:
        for ob in W["rub"]:
            ob.hide_render = sample("rub", tl, t, {"v": 0.0})["v"] < 0.5
    pv = sample("palms", tl, t, {"v": 0.0})["v"] < 0.5
    for ob in W.get("palms", []):
        ob.hide_render = pv
    lv = sample("leohands", tl, t, {"v": 0.0})["v"]
    for key_, want in (("lh1", 1), ("lh2", 2)):
        for ob in W.get(key_, []):
            ob.hide_render = int(round(lv)) != want
    pf = sample("pratframe", tl, t, {"v": 0.0})["v"] < 0.5
    for ob in W.get("pratframe", []):
        ob.hide_render = pf
    cf = sample("calfridge", tl, t, {"v": 1.0})["v"] < 0.5
    for ob in W.get("calfridge", []):
        ob.hide_render = cf
    # ---- the swing sways slowly, once it is back on its chains
    if "swing" in W:
        W["swing"].rotation_euler = (math.radians(3.5) * math.sin(t * 1.3), 0, 0)
    return {}
