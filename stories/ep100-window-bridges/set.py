"""ep100-window-bridges: three burnt bridges rise toward two windows; the stranger is Eli, my best friend.

One bright seaside alley (the "closer" look): terracotta, ochre and coral houses with teal shutters on both sides of a
3.2 m cobbled lane, dozens of little plank bridges between facing windows, the sea at the lane's end.
World (metres, z up): the lane runs along y (the sea at +y), my wall is x = -1.6 (faces +x), Eli's is x = +1.6.
Third-floor windows (floor 6.0, sill 6.9, head 8.3) open onto real rooms; every other window is painted on.
My window and Eli's are at y = 0; our bridge is at y = -0.5, z 6.93.  Burnt bridges lie at y = +0.55 (the oldest),
-1.6 and +1.75.  Our home (the hall and the dinner table) is a small room built at x = 40.
Cues (story.json): count, bridge, burnt, sea, pip, show, tray.  No text anywhere: only numerals and glyphs.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import bl_story, rig

TMP = Path(tempfile.mkdtemp(prefix="bridges-"))
_n = [0]


def nm(p):
    _n[0] += 1
    return f"{p}.{_n[0]}"


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mixhex(a, b, u):
    ra, rb = hexrgb(a), hexrgb(b)
    return tuple((lerp(x, y, u) / 255.0) for x, y in zip(ra, rb))


class K:
    kit = None


def P(hexc, rough=0.5, spec=0.35):
    return K.kit.plastic(hexc, rough, spec=spec)


def B(parent, size, loc, mat, name="b", bevel=0.0, rot=(0, 0, 0)):
    return K.kit.box(nm(name), size, loc, mat, parent, rot, bevel)


def E(parent, loc=(0, 0, 0), name="e", rot=(0, 0, 0)):
    return K.kit.empty(nm(name), loc, parent, rot)


def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


def no_shadow(ob):
    try:
        ob.visible_shadow = False
    except Exception:
        pass


# ----------------------------------------------------------------------------------------------- palette
TERRA, OCHRE, CORAL, PEACH, CREAMW = "#e07a52", "#e8b04a", "#f08a6a", "#f2b896", "#f4ead6"
TEAL, TEAL2 = "#1fa39a", "#2bbfb3"
PLANK = ["#e6c99a", "#ddbf8d", "#ecd2a6", "#d9b886"]
SOOT = ["#2b2624", "#342d2a", "#231f1e", "#3a312d"]
WALLS = [TERRA, OCHRE, CORAL, PEACH, "#d96a4a", "#f0c070"]
COLS = [k for k in range(-3, 11)]            # window columns, centred y = 3 k
BR_Y = {"old": 0.55, "mid": -1.6, "far": 1.75}
OURS_Y = -0.5
BR_L = 3.0
NPL = 22
PITCH = 3.0 / NPL
SEA_N = 520


# ----------------------------------------------------------------------------------------------- images
def counter_image(n):
    from PIL import Image, ImageDraw, ImageFont

    p = TMP / f"count-{n}.png"
    if p.exists():
        return str(p)
    W, H = 480, 250
    im = Image.new("RGB", (W, H), hexrgb("#12304a"))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, W - 7, H - 7], 36, outline=hexrgb("#2bd0c0"), width=12, fill=hexrgb("#12304a"))
    # the plank glyph: a pale slanted board with two nails
    pl = Image.new("RGBA", (200, 70), (0, 0, 0, 0))
    dd = ImageDraw.Draw(pl)
    dd.rounded_rectangle([0, 0, 199, 69], 12, fill=hexrgb("#f0d29c"), outline=hexrgb("#2bbfb3"), width=8)
    dd.ellipse([18, 27, 32, 41], fill=hexrgb("#7a5a30"))
    dd.ellipse([168, 27, 182, 41], fill=hexrgb("#7a5a30"))
    dd.line([(50, 20), (150, 20)], fill=hexrgb("#d3ad74"), width=5)
    dd.line([(50, 50), (150, 50)], fill=hexrgb("#d3ad74"), width=5)
    pl = pl.rotate(14, expand=True, resample=Image.BICUBIC)
    im.paste(pl, (36, 70), pl)
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", 150 if n < 100 else 118)
    except Exception:
        f = ImageFont.load_default()
    txt = str(n)
    bb = d.textbbox((0, 0), txt, font=f)
    cx = 345
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], H / 2 - (bb[3] - bb[1]) / 2 - bb[1]), txt, fill=hexrgb("#ffffff"), font=f)
    im.save(p)
    return str(p)


def hand_poly(cx, cy, s, mirror):
    """A hand print pointing +u (right): palm, four fingers, a thumb. Returns shapes as (kind, bbox/pts)."""
    sh = []
    sx = -1 if mirror else 1
    # palm
    sh.append(("rr", (cx - 70 * s, cy - 78 * s, cx + 50 * s, cy + 78 * s)))
    for i, fy in enumerate((-66, -22, 22, 64)):
        ln = (118, 138, 130, 104)[i]
        sh.append(("rr", (cx + 30 * s, cy + (fy - 17) * s, cx + (30 + ln) * s, cy + (fy + 17) * s)))
    # thumb
    ty = -1 if mirror else 1
    sh.append(("rr", (cx - 60 * s, cy + (92 if not mirror else -150) * s, cx + 20 * s, cy + (150 if not mirror else -92) * s)))
    return sh


def prints_image():
    from PIL import Image, ImageDraw, ImageFilter

    p = TMP / "prints.png"
    if p.exists():
        return str(p)
    W, H = 400, 1000                       # u along the bridge (x), v across it (y)
    im = Image.new("RGB", (W, H), hexrgb("#f0d29c"))
    d = ImageDraw.Draw(im)
    for yy in range(0, H, 100):            # faint grain
        d.line([(0, yy + 30), (W, yy + 30)], fill=hexrgb("#e6c58c"), width=3)
    soot = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(soot)
    for (cx, cy, s, mir) in ((150, 255, 1.0, False), (150, 745, 0.9, True)):
        for kind, bb in hand_poly(cx, cy, s, mir):
            sd.rounded_rectangle(bb, 20, fill=255)
    soot = soot.filter(ImageFilter.GaussianBlur(2.5))
    dark = Image.new("RGB", (W, H), hexrgb("#1c1816"))
    im = Image.composite(dark, im, soot)
    d = ImageDraw.Draw(im)
    # the date: notches along the edge, a nine, a crescent for the month
    for k in range(9):
        d.rectangle([W - 40, 60 + k * 30, W - 14, 72 + k * 30], fill=hexrgb("#7a5a30"))
    try:
        from PIL import ImageFont
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", 120)
    except Exception:
        f = None
    d.text((W - 150, 400), "9", fill=hexrgb("#5a3d1c"), font=f)
    d.ellipse([W - 150, 560, W - 40, 670], fill=hexrgb("#5a3d1c"))
    d.ellipse([W - 130, 548, W - 20, 658], fill=hexrgb("#f0d29c"))
    im.save(p)
    return str(p)


def glyph_image(kind):
    from PIL import Image, ImageDraw, ImageFont

    p = TMP / f"glyph-{kind}.png"
    if p.exists():
        return str(p)
    W, H = 300, 200
    if kind == "ticket":
        im = Image.new("RGB", (W, H), hexrgb("#f6efe0"))
        d = ImageDraw.Draw(im)
        d.rectangle([6, 6, W - 7, H - 7], outline=hexrgb("#1f7fa8"), width=6)
        d.polygon([(40, 120), (140, 120), (120, 150), (60, 150)], fill=hexrgb("#1f7fa8"))
        d.line([(90, 120), (90, 50)], fill=hexrgb("#1f7fa8"), width=6)
        d.polygon([(90, 52), (90, 112), (135, 112)], fill=hexrgb("#e0573f"))
        try:
            f = ImageFont.truetype("DejaVuSans-Bold.ttf", 100)
        except Exception:
            f = None
        d.text((175, 45), "10", fill=hexrgb("#1c1816"), font=f)
    elif kind == "clock":
        im = Image.new("RGB", (W, W), hexrgb("#fff8e8"))
        d = ImageDraw.Draw(im)
        d.ellipse([8, 8, W - 9, W - 9], fill=hexrgb("#fff8e8"), outline=hexrgb("#1c1816"), width=14)
        for k in range(12):
            a = k * math.pi / 6
            d.line([(150 + 105 * math.sin(a), 150 - 105 * math.cos(a)), (150 + 125 * math.sin(a), 150 - 125 * math.cos(a))],
                   fill=hexrgb("#1c1816"), width=8)
        d.line([(150, 150), (150, 55)], fill=hexrgb("#1c1816"), width=12)       # minute at 12
        d.line([(150, 150), (222, 150)], fill=hexrgb("#d7263d"), width=14)      # hour at 3
        d.ellipse([138, 138, 162, 162], fill=hexrgb("#1c1816"))
        im = im.resize((W, W))
    im.save(p)
    return str(p)


def img_mat(kit, path, strength=None, rough=0.7):
    m = kit._new(nm("img"))
    nt = m.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path)
    tex.image.colorspace_settings.name = "sRGB"
    gc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
    if strength is None:
        b = nt.nodes["Principled BSDF"]
        b.inputs["Roughness"].default_value = rough
        nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
        kit._fogged(m, b.outputs[0])
    else:
        nt.nodes.remove(nt.nodes["Principled BSDF"])
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = strength
        nt.links.new(tex.outputs["Color"], em.inputs["Color"])
        nt.links.new(em.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    return m, tex


# ----------------------------------------------------------------------------------------------- spans
def span(kit, a, b, width, deck_mat, rope_mat, rope_h=0.45, parent=None, deck_th=0.05, post_every=0):
    """A straight plank-and-rope bridge from point a to point b (decor and the web)."""
    a, b = V(a), V(b)
    d = b - a
    L = d.length
    yaw = math.atan2(d.y, d.x)
    pitch = -math.asin(d.z / L) if L else 0
    mid = (a + b) / 2
    R = E(parent, tuple(mid), "span", rot=(0, pitch, yaw))
    B(R, (L, width, deck_th), (0, 0, 0), deck_mat, "sdeck")
    for sy in (-1, 1):
        B(R, (L, 0.025, 0.025), (0, sy * width / 2, rope_h), rope_mat, "srope")
    for sx in (-1, 1):
        for sy in (-1, 1):
            B(R, (0.03, 0.03, rope_h), (sx * (L / 2 - 0.03), sy * width / 2, rope_h / 2), rope_mat, "spost")
    return R


# ----------------------------------------------------------------------------------------------- the alley
def window_dress(kit, s, y, z0, z1, shutter, painted, flowers=True, glass="#8fd0e4"):
    """Frame, shutters and a window box on the lane side of wall s (a 6 cm proud layer on the wall's face)."""
    xf = s * 1.57
    w = 2.0
    zc = (z0 + z1) / 2
    h = z1 - z0
    white = P("#fbf7ee", 0.5)
    if painted:
        B(None, (0.06, w, h), (xf, y, zc), P(glass, 0.15, 0.9), "pane")
        B(None, (0.08, 0.07, h + 0.1), (xf, y, zc), white, "mullion")
        B(None, (0.08, w, 0.07), (xf, y, zc), white, "transom")
        for sy in (-1, 1):
            B(None, (0.08, 0.08, h + 0.12), (xf, y + sy * (w / 2 + 0.02), zc), white, "jamb")
        B(None, (0.08, w + 0.2, 0.08), (xf, y, z1 + 0.04), white, "head")
    else:
        for sy in (-1, 1):
            B(None, (0.08, 0.1, h + 0.14), (xf, y + sy * (w / 2 + 0.04), zc), white, "jamb")
        B(None, (0.08, w + 0.3, 0.1), (xf, y, z1 + 0.05), white, "head")
    for sy in (-1, 1):                                   # shutters
        B(None, (0.06, 0.52, h), (s * 1.545, y + sy * (w / 2 + 0.32), zc), P(shutter, 0.5), "shutter")
        for k in range(4):
            B(None, (0.03, 0.46, 0.035), (s * 1.51, y + sy * (w / 2 + 0.32), z0 + (k + 0.5) * h / 4), P("#168a82", 0.5), "slat")
    B(None, (0.34, w + 0.3, 0.1), (s * 1.43, y, z0 - 0.05), P("#f1e6cf", 0.7), "sill")     # the sill ledge
    if flowers:
        B(None, (0.3, w - 0.1, 0.26), (s * 1.38, y, z0 - 0.23), P("#b5603a", 0.6), "wbox")
        for k in range(7):
            col = ("#ff6f9c", "#ffd23f", "#ffffff", "#ff8a3d")[k % 4]
            B(None, (0.14, 0.2, 0.14), (s * 1.36, y - 0.8 + 0.27 * k, z0 + 0.0), P("#3fae4a", 0.7), "leaf", 0.02)
            B(None, (0.08, 0.08, 0.08), (s * 1.36, y - 0.8 + 0.27 * k, z0 + 0.1), P(col, 0.5), "bloom", 0.02)


def build_wall(kit, s, ctx):
    n_col = len(COLS)
    y_a, y_b = 3 * COLS[0] - 1.5, 3 * COLS[-1] + 1.5
    xc = s * 1.75
    # interior strip (third floor): floor, back wall, ceiling, cream skin
    cream = P("#e6c9a2", 0.85, 0.1)
    floor = kit.texture("wood", 0.7, tint="#f1d8b0")
    B(None, (3.7, y_b - y_a, 0.1), (s * 3.75, (y_a + y_b) / 2, 5.95), floor, "rfloor")
    if s < 0:
        B(None, (0.2, y_b - y_a, 3.2), (s * 5.55, (y_a + y_b) / 2, 7.4), cream, "rback")
    else:                       # an opening behind Eli's window for the bridge that grows (y -1.6 .. 0.6)
        B(None, (0.2, -1.6 - y_a, 3.2), (s * 5.55, (y_a - 1.6) / 2, 7.4), cream, "rback")
        B(None, (0.2, y_b - 0.6, 3.2), (s * 5.55, (y_b + 0.6) / 2, 7.4), cream, "rback")
    B(None, (3.7, y_b - y_a, 0.15), (s * 3.75, (y_a + y_b) / 2, 9.07), cream, "rceil")
    for sy in (y_a + 0.05, y_b - 0.05):
        B(None, (3.7, 0.1, 3.2), (s * 3.75, sy, 7.4), cream, "rend")
    # the rest of the building behind the facade (so roofs seen from above are solid)
    B(None, (4.0, y_b - y_a, 3.0), (s * 3.9, (y_a + y_b) / 2, 10.5), P("#e9c49a", 0.8), "topfill")
    B(None, (4.0, y_b - y_a, 6.0), (s * 3.9, (y_a + y_b) / 2, 2.95), P("#d8b58a", 0.8), "lowfill")
    for k in COLS:
        y = 3 * k
        wall = WALLS[(k * 2 + (3 if s > 0 else 0) + 6) % len(WALLS)]
        wm = P(wall, 0.85, 0.1)
        shut = (TEAL, TEAL2, "#2b8fd0")[(k + (1 if s > 0 else 0)) % 3] if (k + s) % 4 else CORAL
        B(None, (0.3, 3.0, 3.0), (xc, y, 1.5), wm, "wg")
        B(None, (0.3, 3.0, 3.0), (xc, y, 4.5), wm, "w2")
        B(None, (0.3, 3.0, 0.9), (xc, y, 6.45), wm, "wsill")
        B(None, (0.3, 3.0, 0.7), (xc, y, 8.65), wm, "wlint")
        B(None, (0.3, 3.0, 3.0), (xc, y, 10.5), wm, "w4")
        B(None, (0.3, 1.0, 1.4), (xc, y + 1.5, 7.6), wm, "pier")
        B(None, (4.6, 3.05, 0.3), (s * 4.1, y, 12.15), P("#c8553a", 0.7), "roof")        # roof tiles
        B(None, (0.5, 3.1, 0.18), (s * 1.7, y, 12.05), P("#f1e6cf", 0.7), "eave")
        # windows: ground (with a door on some), second, third (open), fourth
        if k % 3 == 0:
            B(None, (0.1, 1.3, 2.3), (s * 1.55, y, 1.15), P("#168a82", 0.5), "door")
            B(None, (0.06, 1.5, 0.12), (s * 1.53, y, 2.36), P("#fbf7ee", 0.5), "doorhead")
            B(None, (0.04, 0.12, 0.12), (s * 1.49, y + 0.45, 1.15), P("#e8c34a", 0.3, 0.8), "knob")
        else:
            window_dress(kit, s, y, 0.9, 2.4, shut, True)
        window_dress(kit, s, y, 3.9, 5.4, shut, True)
        window_dress(kit, s, y, 6.9, 8.3, shut, False, flowers=False)
        window_dress(kit, s, y, 9.9, 11.3, shut, True, flowers=False)
        if k % 2 == 0:                       # laundry line on the second floor
            for j in range(4):
                B(None, (0.03, 0.4, 0.45), (s * 1.3, y - 1.0 + 0.55 * j, 5.95), P(("#ffffff", "#ff8fb0", "#7fc4ff", "#ffd23f")[j], 0.9), "laundry")
            B(None, (0.02, 3.0, 0.02), (s * 1.3, y, 6.2), P("#8a7a60", 0.7), "line")


def build_decor_bridges(kit, ctx):
    rope = P("#9a7a50", 0.8)
    pale = P("#e6c99a", 0.7)
    grey = P("#9c8e7c", 0.9)
    wood = kit.planks("#d8b888", "#b08a58", 1.0, "X")
    ys = [y for y in (-9, -6, -3, 3, 6, 9, 12, 15, 18, 24, 27, 30)]
    zs = (1.2, 4.1, 7.1, 10.1)
    import random
    rnd = random.Random(5)
    for y in ys:
        for z in zs:
            if rnd.random() < 0.5 and not (y in (-6, 21) and z == 7.1):
                continue
            if y == 3 and z == 7.1:
                continue
            dy = rnd.choice([-0.4, 0, 0.5, 1.0])
            dz = rnd.choice([-0.3, 0, 0.3])
            span(kit, (-1.5, y, z + dz * 0.0), (1.5, y + dy, z + dz), 0.55, wood if rnd.random() < 0.5 else (pale if rnd.random() < 0.6 else grey), rope,
                 rope_h=0.35)
    # the neighbours' pair at y = -6 (third floor), a real bridge between open windows
    span(kit, (-1.5, -6, 6.95), (1.5, -6, 6.95), 0.8, pale, P("#c87a50"), rope_h=0.45)
    # Mrs. Vega's web: from her window at y = 3 to many facing windows
    web = [(-4.5, 4.1), (-3.0, 7.1), (-1.5, 10.1), (0.0, 1.2), (1.5, 4.1), (3.0, 7.1), (4.5, 10.1), (6.0, 7.1), (7.5, 4.1), (9.0, 1.2),
           (1.5, 10.1), (6.0, 10.1), (-1.5, 1.2), (4.5, 1.2)]
    for (wy, wz) in web:
        span(kit, (-1.5, 3.0, 7.3), (1.5, wy, wz), 0.4, pale if wz > 5 else wood, rope, rope_h=0.3)
    # the old stone bridge at y = 21
    st = kit.checker("#a8a49c", "#8f8b83", 3.0, rough=0.9)
    B(None, (3.0, 0.9, 0.4), (0, 21, 6.7), st, "stone")
    B(None, (2.2, 0.9, 0.3), (0, 21, 6.35), st, "stonearch")
    for sy in (-1, 1):
        B(None, (3.0, 0.1, 0.35), (0, 21 + sy * 0.45, 7.05), st, "stonerail")
    # the stone bridge's ledge pieces are the windows' own sills


def build_ground(kit, ctx):
    cob = kit.cobbles("#a89b8c", "#c4b8a6", "#7a6e60", 2.4, 0.15)
    B(None, (3.2, 41.0, 0.2), (0, 11.5, -0.1), cob, "lane")
    B(None, (3.0, 6.0, 0.2), (0, 35.0, -0.1), P("#cdbfa8", 0.8, 0.1), "quay")
    B(None, (3.2, 0.3, 12.3), (0, -9.15, 6.15), P("#e8b04a", 0.85, 0.1), "alleyend")
    B(None, (1.3, 0.1, 2.3), (0, -9.0, 1.15), P("#168a82", 0.5), "enddoor")
    # the sea and the town beyond
    sea = P("#2fb3e6", 0.12, 0.9)
    B(None, (900, 700, 0.2), (0, 400, -0.6), sea, "sea")
    B(None, (200, 90, 0.4), (0, -50, -0.2), P("#d9c9ac", 0.9, 0.1), "hinterland")
    import random
    rnd = random.Random(11)
    cols = [TERRA, OCHRE, CORAL, PEACH, "#f6e0c0"]
    for i in range(60):
        sx = rnd.choice([-1, 1])
        x = sx * rnd.uniform(8, 60)
        y = rnd.uniform(-30, 120)
        if y > 36 and abs(x) < 7:
            continue
        # houses step down toward the sea
        h = max(3.0, 14.0 - y * 0.1 + rnd.uniform(-2, 2))
        w, d = rnd.uniform(5, 10), rnd.uniform(5, 10)
        B(None, (w, d, h), (x, y, h / 2 - 0.3), P(rnd.choice(cols), 0.85, 0.1), "town")
        B(None, (w + 0.6, d + 0.6, 0.35), (x, y, h - 0.15), P("#c8553a", 0.7), "townroof")
    for sx in (-1, 1):                      # the harbour-side houses by the lane's end
        for j, (y, h) in enumerate(((36, 8.0), (44, 6.0), (52, 4.5))):
            B(None, (6, 7, h), (sx * 5.5, y, h / 2 - 0.2), P(cols[(j + (1 if sx > 0 else 0)) % 5], 0.85, 0.1), "harbour")
            B(None, (6.6, 7.6, 0.35), (sx * 5.5, y, h - 0.05), P("#c8553a", 0.7), "harbroof")
    # the boat far out
    boat = E(None, (-6.0, 150.0, 0.0), "boat")
    B(boat, (3.2, 8.0, 1.4), (0, 0, 0.3), P("#f6f2e8", 0.4), "hull", 0.1)
    B(boat, (2.6, 3.0, 1.6), (0, -1.0, 1.7), P("#e0573f", 0.4), "cabin", 0.08)
    B(boat, (0.2, 0.2, 2.6), (0, 1.0, 2.6), P("#6a4a2a", 0.6), "mast")
    ctx["boat_light"] = B(boat, (0.5, 0.5, 0.5), (0, 1.0, 4.0), kit.emit("#ffe9a8", 14.0, name="boatlamp"), "lamp", 0.1)
    ctx["boat_pt"] = kit.light("boatlight", "POINT", (-6.0, 150.0, 4.2), 2500, "#ffd98a", size=0.3, shadow=False)


# ----------------------------------------------------------------------------------------------- the bridges
class Ours:
    """Our fourth bridge: 22 pale planks from my sill to Eli's, teal rope rails; vis planks are shown."""

    def __init__(self, kit):
        self.root = E(None, (0, OURS_Y, 6.935), "ours")
        self.planks, self.posts = [], []
        for i in range(NPL):
            c = PLANK[i % 4]
            x = -1.5 + (i + 0.5) * PITCH
            pl = B(self.root, (PITCH - 0.02, 0.9, 0.05), (x, 0, 0), P(c, 0.65), "oplank", 0.008)
            self.planks.append(pl)
            if i % 3 == 0:
                grp = []
                for sy in (-1, 1):
                    grp.append(B(self.root, (0.045, 0.045, 0.5), (x, sy * 0.44, 0.27), P(TEAL, 0.5), "opost", 0.01))
                self.posts.append((i, grp))
        self.ropes = []
        for sy in (-1, 1):
            for z in (0.5, 0.28):
                self.ropes.append((sy, z, B(self.root, (1.0, 0.03, 0.03), (0, sy * 0.44, z), P(TEAL2, 0.5), "orope")))
        # lore: two teal strokes on the first plank (1.2 cm proud)
        self.strokes = [B(self.root, (0.02, 0.18, 0.012), (-1.5 + 0.5 * PITCH + dx, 0.0, 0.031), P("#0f8a82", 0.5), "stroke") for dx in (-0.025, 0.025)]
        self.chalk = []

    def show(self, vis):
        vis = max(0, min(NPL, int(round(vis))))
        for i, pl in enumerate(self.planks):
            hide(pl, i >= vis)
        for i, grp in self.posts:
            for g in grp:
                hide(g, i >= vis)
        L = vis * PITCH
        for sy, z, r in self.ropes:
            hide(r, vis == 0)
            r.scale = (max(0.01, L), 1, 1)
            r.location = (-1.5 + L / 2, sy * 0.44, z)
        for s in self.strokes:
            hide(s, vis < 1)


class Burnt:
    """One charred bridge: 22 black planks, rust cracks, snapped posts and rope stubs, one pale unburnt middle plank."""

    def __init__(self, kit, name, y, prints_mat):
        self.name, self.y = name, y
        self.root = E(None, (0, y, 0.12), f"burnt-{name}")
        mid = NPL // 2
        for i in range(NPL):
            x = -1.5 + (i + 0.5) * PITCH
            if i == mid:
                B(self.root, (0.4, 0.9, 0.05), (x, 0, 0), P("#f0d29c", 0.7), "unburnt", 0.008)
                dec = kit.plane(nm("prints"), (0.38, 0.88), (x, 0, 0.0265), prints_mat, self.root)
                continue
            if (i + (2 if name == "mid" else 0)) % 7 == 3:
                continue                                  # a burnt-through gap
            B(self.root, (PITCH - 0.025, 0.9 - 0.03 * (i % 3), 0.05), (x, 0.015 * ((i * 5) % 3 - 1), 0.004 * (i % 4)),
              P(SOOT[i % 4], 0.92, 0.1), "bplank", 0.01, rot=(0, 0.02 * ((i % 5) - 2), 0.03 * ((i % 3) - 1)))
            if i % 3 == 0:
                B(self.root, (0.02, 0.5, 0.01), (x + 0.01, 0.1 * ((i % 2) * 2 - 1), 0.03), P("#8a3b22", 0.8), "crack")
        for i in (0, 6, 15, NPL - 1):
            x = -1.5 + (i + 0.5) * PITCH
            for sy in (-1, 1):
                hgt = 0.45 if i in (0, NPL - 1) else 0.2 + 0.1 * ((i + (sy > 0)) % 3)
                B(self.root, (0.05, 0.05, hgt), (x, sy * 0.44, hgt / 2 + 0.025), P("#1c1817", 0.95, 0.05), "bpost", 0.01,
                  rot=(0.15 * sy * ((i % 2) - 0.5), 0.1, 0))
        for sy in (-1, 1):                               # charred rope stubs
            B(self.root, (0.55, 0.025, 0.025), (-1.2, sy * 0.44, 0.4), P("#241f1d", 0.95, 0.05), "bstub", 0.005, rot=(0, 0.4, 0))
            B(self.root, (0.45, 0.025, 0.025), (1.25, sy * 0.44, 0.38), P("#241f1d", 0.95, 0.05), "bstub", 0.005, rot=(0, -0.5, 0))

    def place(self, h, t, sway, tilt=0.0):
        a = sway * math.sin(t * 0.9 + self.y * 2.0) if h > 0.3 else 0.0
        self.root.location = (0.0, self.y, 0.12 + h)
        self.root.rotation_euler = (a * 0.035, tilt + a * 0.012, 0)


class Sea:
    """The bridge that grows past Eli's window: planks along a curve over the roofs and out to sea."""

    def __init__(self, kit):
        pts = [(1.7, OURS_Y, 6.93), (6.5, OURS_Y, 7.2), (10.0, 0.5, 10.6), (12.0, 6.0, 15.5), (13.5, 20.0, 17.5), (12.0, 36.0, 17.0),
               (8.0, 58.0, 14.0), (4.0, 85.0, 10.0), (0.0, 112.0, 6.5), (-3.0, 142.0, 3.5)]
        # sample a smooth path (Catmull-Rom) at equal spacing
        def cr(p0, p1, p2, p3, u):
            return tuple(0.5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (-a + 3 * b - 3 * c + d) * u ** 3)
                         for a, b, c, d in zip(p0, p1, p2, p3))
        dense = []
        ext = [pts[0]] + pts + [pts[-1]]
        for i in range(1, len(ext) - 2):
            for k in range(60):
                dense.append(cr(ext[i - 1], ext[i], ext[i + 1], ext[i + 2], k / 60))
        dense.append(pts[-1])
        # equal spacing
        out = [dense[0]]
        acc = 0.0
        step = 0.0
        tgt = 0.36
        for a, b in zip(dense, dense[1:]):
            seg = math.dist(a, b)
            step += seg
            while step >= tgt and len(out) < SEA_N:
                step -= tgt
                u = 1 - step / seg if seg else 1
                out.append(tuple(lerp(x, y, u) for x, y in zip(a, b)))
        self.planks = []
        mats = [P(c, 0.6) for c in PLANK]
        grow = 1.0
        for i, p in enumerate(out):
            q = out[min(i + 1, len(out) - 1)]
            d = V(q) - V(p)
            if d.length < 1e-6 and i:
                d = V(p) - V(out[i - 1])
            yaw = math.atan2(d.y, d.x)
            pit = -math.asin(max(-1, min(1, d.z / max(d.length, 1e-6))))
            far = min(1.0, i / 140.0)
            wid = 0.9 + 1.0 * far                       # wider with distance so the line reads from high above
            th = 0.07 + 0.08 * far
            ob = B(None, (0.3 + 0.1 * far, wid, th), p, mats[i % 4], "splank", 0.01, rot=(0, pit, yaw))
            ob.hide_render = True
            self.planks.append(ob)
        self.rails = []

    def show(self, n):
        n = max(0, min(len(self.planks), int(n)))
        for i, ob in enumerate(self.planks):
            ob.hide_render = i >= n


# ----------------------------------------------------------------------------------------------- Pip
class Pip:
    SAND, DARK = "#d9aa66", "#8a5a2c"

    def __init__(self, kit):
        g, d = P(self.SAND, 0.7, 0.1), P(self.DARK, 0.7, 0.1)
        self.root = E(None, (0, 0, 0), "pip")
        self.bodyg = E(self.root, (0, 0, 0), "pbodyg")
        B(self.bodyg, (0.26, 0.5, 0.26), (0, 0, 0.33), g, "pbody", 0.06)
        B(self.bodyg, (0.2, 0.2, 0.18), (0, -0.2, 0.3), P("#f6e6c8", 0.7, 0.1), "pchest", 0.04)
        self.legs = []
        for sx in (-1, 1):
            for yy in (-0.18, 0.18):
                self.legs.append(B(self.root, (0.08, 0.09, 0.22), (sx * 0.08, yy, 0.11), g, "pleg", 0.03))
        self.headg = E(self.bodyg, (0, -0.3, 0.47), "pheadg")
        B(self.headg, (0.22, 0.22, 0.2), (0, 0, 0), g, "phead", 0.05)
        B(self.headg, (0.13, 0.14, 0.1), (0, -0.16, -0.04), P("#f6e6c8", 0.7, 0.1), "psnout", 0.03)
        B(self.headg, (0.06, 0.05, 0.05), (0, -0.235, -0.0), P("#1c1816", 0.4), "pnose", 0.015)
        for sx in (-1, 1):
            B(self.headg, (0.08, 0.04, 0.05), (sx * 0.065, -0.112, 0.04), P("#1c1816", 0.3), "peye", 0.01)
            B(self.headg, (0.06, 0.07, 0.15), (sx * 0.125, 0.0, 0.0), d, "pear", 0.02, rot=(0, sx * 0.25, 0))
        self.tail = E(self.bodyg, (0, 0.25, 0.42), "ptail")
        B(self.tail, (0.05, 0.05, 0.2), (0, 0, 0.1), d, "ptailb", 0.02)

    def place(self, x, y, z, yaw, t, hop=0.0, hidden=False):
        hide(self.root, hidden)
        self.root.location = (x, y, z)
        self.root.rotation_euler = (0, 0, math.radians(yaw))
        self.bodyg.rotation_euler = (-0.5 * hop, 0, 0)
        self.tail.rotation_euler = (-0.7, 0, math.sin(t * 22) * 0.6)


# ----------------------------------------------------------------------------------------------- rooms and props
def build_rooms(kit, ctx):
    wood = P("#c98d4d", 0.6)
    # Eli's room (east, y 0): bed, sea bag, rope coil on a hook, matches and plant on the sill, ticket
    try:
        kit.prop("bed_single", (4.6, -2.2, 6.03), rot=90, scale=1.15, tint="#7fb8e0")
        kit.prop("nightstand_1", (4.9, 0.9, 6.03), rot=90, scale=1.1)
    except Exception as ex:
        print("props:", ex)
    bag = E(None, (3.3, -1.1, 6.0), "seabag")
    B(bag, (0.9, 0.5, 0.5), (0, 0, 0.25), P("#1f3a68", 0.6), "bagbody", 0.12)
    B(bag, (0.5, 0.52, 0.12), (0, 0, 0.5), P("#e0573f", 0.6), "bagband", 0.04)
    B(None, (0.1, 0.06, 0.06), (5.45, 0.7, 7.8), P("#6a4a2a", 0.5), "hook", 0.01)
    for j in range(4):
        B(None, (0.12, 0.34 - 0.02 * j, 0.34 - 0.02 * j), (5.38, 0.7, 7.55 + 0.0), P("#d9b886", 0.9), "coil", 0.04) if j == 0 else B(None, (0.04, 0.36 - 0.03 * j, 0.36 - 0.03 * j), (5.33 - 0.04 * j, 0.7, 7.55), P(("#d9b886", "#c9a06a")[j % 2], 0.9), "coil", 0.02)
    # the matches box on Eli's sill ledge (outside), a potted plant
    mbox = E(None, (1.42, 0.55, 6.91), "matches")
    B(mbox, (0.1, 0.07, 0.03), (0, 0, 0.015), P("#c9302c", 0.6), "mbox", 0.006)
    B(mbox, (0.1, 0.07, 0.012), (0.0, 0.0, 0.035), P("#f2c14e", 0.6), "mlabel", 0.003)
    for k in range(5):
        B(mbox, (0.004, 0.004, 0.0), (0, 0, 0), P("#f0d29c", 0.8), "dummy")
    for k in range(6):                                  # loose match sticks laid beside it
        B(mbox, (0.005, 0.07, 0.005), (-0.06 + 0.012 * k, 0.09, 0.006), P("#e8c58a", 0.7), "stick")
        B(mbox, (0.011, 0.014, 0.011), (-0.06 + 0.012 * k, 0.12, 0.008), P("#d7263d", 0.5), "head")
    ctx["matches"] = mbox
    pot = E(None, (1.38, 0.15, 6.92), "plant")
    kit.cyl(nm("pot"), 0.07, 0.12, (0, 0, 0.06), P("#c8553a", 0.7), pot, n=14, r2=0.09)
    for k in range(5):
        B(pot, (0.05, 0.02, 0.16), (0.03 * math.cos(k * 1.26), 0.03 * math.sin(k * 1.26), 0.19), P("#3fae4a", 0.6), "frond", 0.005,
          rot=(0.5 * math.sin(k * 1.26), 0.5 * math.cos(k * 1.26), k))
    tk, tex = img_mat(kit, glyph_image("ticket"))
    ctx["ticket"] = kit.plane(nm("ticket"), (0.2, 0.133), (1.30, 0.55, 6.916), tk, None)
    B(None, (0.215, 0.148, 0.012), (1.30, 0.55, 6.906), P("#f6efe0", 0.7), "ticketcard")
    ctx["ticket"].hide_render = True
    # my room (west): bed, clock glyph, a lamp
    try:
        kit.prop("bed_single", (-4.7, 1.9, 6.03), rot=0, scale=1.25)
        kit.prop("nightstand_1", (-3.5, 2.9, 6.03), rot=90, scale=1.1)
        kit.prop("houseplant_1", (-3.0, -2.4, 6.03), scale=1.3)
    except Exception as ex:
        print("props:", ex)
    ck, _ = img_mat(kit, glyph_image("clock"), strength=1.0)
    ctx["clock"] = kit.plane(nm("clock"), (0.5, 0.5), (-5.43, 1.9, 7.6), ck, None, rot=(math.pi / 2, 0, math.pi / 2))
    # Mrs. Vega's, Eli's and my windows: a little flower-pot on each room is dressing enough
    # cards and mugs on the bridge
    cards = E(None, (0.0, OURS_Y, 6.97), "cards")
    for k, (dx, dy, rz) in enumerate(((-0.25, -0.15, 0.2), (0.0, 0.1, -0.3), (0.28, -0.05, 0.5), (0.1, -0.28, 0.1))):
        B(cards, (0.09, 0.13, 0.004), (dx, dy, 0.003 + 0.0 * k), P("#ffffff", 0.5), "card", 0.002, rot=(0, 0, rz))
        B(cards, (0.05, 0.07, 0.001), (dx + 0.005, dy, 0.0055), P(("#d7263d", "#2b6fb5")[k % 2], 0.5), "cardface", 0.0, rot=(0, 0, rz))
    ctx["cards"] = cards
    tray = E(None, (0, OURS_Y, 6.99), "tray")
    B(tray, (0.34, 0.2, 0.025), (0, 0, 0.0125), P("#f2e6c8", 0.6), "trayb", 0.01)
    for dx in (-0.08, 0.08):
        kit.cyl(nm("mug"), 0.045, 0.1, (dx, 0, 0.075), P(("#ff6f61", "#2bbfb3")[dx > 0], 0.4), tray, n=16)
        B(tray, (0.02, 0.02, 0.05), (dx + 0.058, 0, 0.075), P(("#ff6f61", "#2bbfb3")[dx > 0], 0.4), "handle", 0.005)
    ctx["tray"] = tray
    mp = E(None, (0.0, OURS_Y, 8.0), "matchpair")
    for sx in (-1, 1):
        B(mp, (0.14, 0.012, 0.012), (sx * 0.12, 0, 0), P("#e8c58a", 0.7), "mstick", 0.003)
        B(mp, (0.024, 0.02, 0.02), (sx * 0.2, 0, 0), P("#d7263d", 0.5), "mhead", 0.006)
    ctx["matchpair"] = mp
    fr = E(None, (-1.52, 0.0, 7.6), "frost")
    fm = P("#eaf6ff", 0.2, 0.9)
    for (sy, sz, wy, wz) in ((-1.0, 0, 0.12, 1.4), (1.0, 0, 0.12, 1.4), (0, 0.65, 2.1, 0.12), (0, -0.65, 2.1, 0.12)):
        B(fr, (0.03, wy, wz), (0, sy, sz), fm, "frostb", 0.01)
    for k in range(9):
        B(fr, (0.03, 0.2 + 0.05 * (k % 3), 0.05), (0, -0.9 + 0.22 * k, -0.55 + 0.05 * (k % 4)), fm, "frostc", 0.01)
        B(fr, (0.03, 0.05, 0.2 + 0.06 * (k % 3)), (0, -0.9 + 0.22 * k, 0.55 - 0.05 * (k % 3)), fm, "frostc", 0.01)
    ctx["frost"] = fr


def build_home(kit, ctx):
    """Our flat's hall and dinner table, at x = 40 (never seen from the lane)."""
    ox = 40.0
    cream, wood = P("#f8eedb", 0.8, 0.1), kit.texture("wood", 0.7, tint="#f1d8b0")
    B(None, (7.0, 5.6, 0.1), (ox, 0, -0.05), wood, "hfloor")
    B(None, (7.0, 0.2, 3.0), (ox, 2.8, 1.5), P("#f2c7a0", 0.8, 0.1), "hback")
    B(None, (0.2, 5.6, 3.0), (ox + 3.5, 0, 1.5), P("#f2c7a0", 0.8, 0.1), "hright")
    B(None, (0.2, 5.6, 3.0), (ox - 3.5, 0, 1.5), P("#f2c7a0", 0.8, 0.1), "hleft")
    B(None, (7.0, 0.2, 3.0), (ox, -2.8, 1.5), P("#f2c7a0", 0.8, 0.1), "hfront")
    B(None, (7.0, 5.6, 0.1), (ox, 0, 3.05), cream, "hceil")
    # the front door (open), at x ox-1.5 on the front wall
    B(None, (1.1, 0.12, 2.1), (ox - 1.5, -2.7, 1.05), P("#168a82", 0.5), "hdoor")
    B(None, (1.3, 0.06, 0.12), (ox - 1.5, -2.69, 2.17), P("#fbf7ee", 0.5), "hdoorhead")
    # a window on the back wall
    B(None, (1.6, 0.08, 1.2), (ox + 1.8, 2.68, 1.7), P("#bfe6f4", 0.15, 0.9), "hwin")
    B(None, (0.08, 0.1, 1.2), (ox + 1.8, 2.66, 1.7), P("#fbf7ee", 0.5), "hwinmid")
    for sx in (-1, 1):
        B(None, (0.4, 0.08, 1.2), (ox + 1.8 + sx * 1.0, 2.66, 1.7), P(TEAL, 0.6), "hshut")
    # table, three chairs, three plates
    try:
        kit.prop("table_roundlarge", (ox + 0.8, 0.4, 0), height=0.82, tint="#e8b36a")
        for k, (cx, cy, rot) in enumerate(((0.8, 1.6, 180), (-0.4, 0.4, 270), (2.0, 0.4, 90))):
            kit.prop("chair_1", (ox + cx, cy, 0), rot=rot, height=0.95, tint="#ff8a6a")
        kit.prop("kitchen_fridge", (ox + 3.0, 2.2, 0), height=1.9)
        kit.prop("houseplant_1", (ox - 3.0, 2.2, 0), height=1.2)
        kit.prop("carpet_1", (ox + 0.8, 0.4, 0.01), scale=1.6)
    except Exception as ex:
        print("props:", ex)
    ctx["plates"] = []
    for k, (px, py) in enumerate(((0.8, 1.08), (0.15, 0.4), (1.45, 0.4))):
        pl = kit.cyl(nm("plate"), 0.14, 0.02, (ox + px, py, 0.84), P("#ffffff", 0.3), None, n=20)
        ring = kit.cyl(nm("platering"), 0.12, 0.012, (ox + px, py, 0.855), P(TEAL2, 0.4), None, n=20)
        ctx["plates"].append((pl, ring))
    hide(ctx["plates"][2][0], True)                  # the third plate is shown by the "show" cue
    hide(ctx["plates"][2][1], True)
    ctx["home_light"] = kit.light("homelight", "POINT", (ox + 0.5, 0.2, 2.6), 520, "#fff0d8", size=0.5)
    ctx["home_light2"] = kit.light("homelight2", "POINT", (ox - 1.5, -1.5, 2.4), 260, "#fff0d8", size=0.5)


def build_strings(kit, ctx):
    """String lights across the lane (they're on at night; their bulbs are dull by day)."""
    ctx["bulbs"] = []
    bulb = kit.emit("#ffd27a", 9.0, name="bulbnight")
    ctx["bulbmat"] = bulb
    wire = P("#3b3330", 0.8)
    for (y, z0) in ((-3.5, 9.6), (-1.2, 9.8), (1.4, 9.9), (3.6, 9.6), (6.0, 9.8)):
        n = 11
        for j in range(n):
            u = j / (n - 1)
            x = -1.55 + 3.1 * u
            z = z0 - 0.85 * math.sin(math.pi * u)
            kit.sphere(nm("bulb"), 0.07, (x, y, z), bulb, None, seg=8)
            if j:
                u0 = (j - 1) / (n - 1)
                x0 = -1.55 + 3.1 * u0
                z_0 = z0 - 0.85 * math.sin(math.pi * u0)
                ln = math.hypot(x - x0, z - z_0)
                B(None, (ln, 0.012, 0.012), ((x + x0) / 2, y, (z + z_0) / 2), wire, "wire", 0.0, rot=(0, -math.atan2(z - z_0, x - x0), 0))
    ctx["strlights"] = [kit.light(f"str{k}", "POINT", (0, y, 8.9), 260, "#ffd27a", size=0.3, shadow=False) for k, y in enumerate((-2.5, 0.2, 2.6, 5.0))]


# ----------------------------------------------------------------------------------------------- looks
LOOKS = {
    "day": {"sky": ["#d9f1ff", "#b3e2ff", "#86caff", "#52a2f2"], "world": 1.1, "sun": (96, 62, 4.0, "#fff1d8"), "fill": 1.0,
            "str": 0.0, "room": 1.0, "exp": -0.3, "lane": 1.0, "boat": 0.0},
    "april": {"sky": ["#e8f6ff", "#c4e8ff", "#98d2ff", "#62aef5"], "world": 1.15, "sun": (88, 58, 4.2, "#fff3dc"), "fill": 1.0,
             "str": 0.0, "room": 1.1, "exp": -0.3, "lane": 1.0, "boat": 0.0},
    "autumn": {"sky": ["#ffc9a0", "#f09aa0", "#9a7ac0", "#4a4a90"], "world": 0.75, "sun": (96, 14, 3.5, "#ffb070"), "fill": 1.1,
               "str": 0.8, "room": 1.1, "exp": 0.1, "lane": 0.45, "boat": 0.0},
    "night": {"sky": ["#4a5a98", "#38477e", "#27356a", "#18224c"], "world": 0.5, "sun": (140, 30, 0.7, "#9aa8ff"), "fill": 1.0,
              "str": 1.0, "room": 0.5, "exp": 0.1, "lane": 0.35, "boat": 0.0},
    "dusk": {"sky": ["#ffb48a", "#ff7f5c", "#d35a9a", "#5a4ab0"], "world": 0.9, "sun": (96, 8, 5.5, "#ff9a60"), "fill": 0.8,
             "str": 0.6, "room": 1.0, "exp": 0.15, "lane": 0.7, "boat": 1.0},
    "winter": {"sky": ["#f0f4ff", "#d4e2fa", "#aac8f0", "#7ea6e0"], "world": 1.2, "sun": (96, 30, 4.0, "#e8f0ff"), "fill": 1.0,
               "str": 0.3, "room": 1.2, "exp": -0.25, "lane": 1.0, "boat": 0.0},
    "dawn": {"sky": ["#ffe6c0", "#ffd0b0", "#b8d0ff", "#86a8f4"], "world": 1.0, "sun": (88, 14, 4.5, "#ffe0b0"), "fill": 1.0,
             "str": 0.2, "room": 1.0, "exp": 0.05, "lane": 0.8, "boat": 0.0},
    "home": {"sky": ["#d9f1ff", "#b3e2ff", "#86caff", "#52a2f2"], "world": 1.0, "sun": (96, 62, 2.5, "#fff1d8"), "fill": 0.9,
             "str": 0.0, "room": 1.0, "exp": 0.0, "lane": 0.0, "boat": 0.0},
}


def mix_look(a, b, u):
    out = {}
    for k in a:
        va, vb = a[k], b[k]
        if k == "sky":
            out[k] = [mixhex(x, y, u) for x, y in zip(va, vb)]
        elif k == "sun":
            out[k] = (lerp(va[0], vb[0], u), lerp(va[1], vb[1], u), lerp(va[2], vb[2], u), va[3] if u < 0.5 else vb[3],
                      mixhex(va[3], vb[3], u))
        else:
            out[k] = lerp(va, vb, u)
    return out


def cue_at(tl, name, t):
    out = {}
    for c in tl.get("cues", []):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c
    return out


def anim_val(c, key, t, default):
    """A cue value that may move: key (start) and key+'_to' over c['dur']."""
    if not c:
        return default
    v = c.get(key, default)
    if key + "_to" in c:
        u = ss((t - c["t"]) / max(1e-3, c.get("dur", 1.0)))
        to = c[key + "_to"]
        if isinstance(v, list):
            return [lerp(a, b, u) for a, b in zip(v, to)]
        return lerp(v, to, u)
    return v


# ----------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    K.kit = kit
    ctx = {"story": story, "shots": {s["id"]: s for s in story["shots"]}}
    sc = bpy.context.scene
    nt = sc.world.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.55
    mr.clamp = True
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements.new(0.22)
    ramp.color_ramp.elements.new(0.55)
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    ctx["ramp"], ctx["bg"] = ramp, bg

    ctx["sun"] = kit.light("sun", "SUN", (0, 0, 50), 6.0, "#fff1d8", size=0.1)
    ctx["sun"].data.angle = 0.05
    ctx["fill"] = kit.light("camfill", "POINT", (0, 0, 2), 80, "#fff0dc", size=0.6, shadow=False)
    ctx["roomW"] = kit.light("roomW", "POINT", (-3.2, -0.3, 8.4), 70, "#fff0d8", size=0.5)
    ctx["roomE"] = kit.light("roomE", "POINT", (3.2, -0.3, 8.4), 70, "#fff0d8", size=0.5)
    ctx["roomX"] = [kit.light(f"roomX{k}", "POINT", (s * 3.2, y, 8.4), 70, "#fff0d8", size=0.5)
                    for k, (s, y) in enumerate(((-1, 3.0), (1, 3.0), (-1, -6.0), (1, -6.0), (-1, -3.0), (1, 21.0), (-1, 21.0), (1, -3.0)))]
    ctx["lane"] = [kit.light(f"lane{k}", "POINT", (0.0, y, 4.2), 300, "#fff0d8", size=0.7) for k, y in enumerate((-7.0, -3.0, 1.0, 5.0, 10.0, 16.0))]
    ctx["torch"] = kit.light("torch", "SPOT", (0, 0, 1.2), 900, "#fff2d0", size=0.15, spot=55, blend=0.5)
    build_ground(kit, ctx)
    for s in (-1, 1):
        build_wall(kit, s, ctx)
    build_decor_bridges(kit, ctx)
    build_strings(kit, ctx)
    ctx["ours"] = Ours(kit)
    pm, _ = img_mat(kit, prints_image(), rough=0.9)
    ctx["burnt"] = {k: Burnt(kit, k, y, pm) for k, y in BR_Y.items()}
    ctx["sea"] = Sea(kit)
    build_rooms(kit, ctx)
    build_home(kit, ctx)
    ctx["pip"] = Pip(kit)
    ctx["last_n"] = None
    build_inset(kit, ctx)
    return ctx


# ----------------------------------------------------------------------------------------------- the plank counter
def build_inset(kit, ctx):
    cam = kit.OBJ["cam"]
    m = kit._new(nm("inset"))
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    gc = nt.nodes.new("ShaderNodeTexCoord")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 0.95
    nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    pl = kit.plane(nm("inset"), (1.0, 1.0), (0, 0, -0.15), m, cam)
    no_shadow(pl)
    ctx["inset"] = (pl, tex)
    ctx["inset_imgs"] = {}


def place_inset(kit, ctx, n, lens):
    pl, tex = ctx["inset"]
    if n not in ctx["inset_imgs"]:
        im = bpy.data.images.load(counter_image(n))
        im.colorspace_settings.name = "sRGB"
        ctx["inset_imgs"][n] = im
    tex.image = ctx["inset_imgs"][n]
    d = 0.15
    unit = d / lens
    pw = 0.36 * 13.5 * unit
    ph = pw * 250 / 480
    x = 0.47 * 6.75 * unit
    y = 0.74 * 12.0 * unit
    pl.location, pl.scale = (x, y, -d), (pw, ph, 1)


# ----------------------------------------------------------------------------------------------- animate
def look_at(ctx, tl, t):
    shots = tl["shots"]
    cur = next((s for s in shots if s["start"] <= t < s["end"]), shots[-1])
    i = shots.index(cur)
    A = LOOKS[ctx["shots"][cur["id"]].get("look", "day")]
    if i + 1 < len(shots) and t > cur["end"] - 0.35:
        nb = LOOKS[ctx["shots"][shots[i + 1]["id"]].get("look", "day")]
        if nb is not A:
            return mix_look(A, nb, ss((t - (cur["end"] - 0.35)) / 0.35)), cur
    return mix_look(A, A, 0.0), cur


def animate(kit, story, tl, t, ctx):
    sc = bpy.context.scene
    L, cur = look_at(ctx, tl, t)
    sd = ctx["shots"][cur["id"]]
    r = ctx["ramp"].color_ramp.elements
    for el, c in zip(r, L["sky"]):
        el.color = (kit.srgb(c[0]), kit.srgb(c[1]), kit.srgb(c[2]), 1.0)
    ctx["bg"].inputs["Strength"].default_value = L["world"]
    az, el_, en, _, scol = L["sun"]
    azr, elr = math.radians(az), math.radians(el_)
    pos = V((math.sin(azr) * math.cos(elr), -math.cos(azr) * math.cos(elr), math.sin(elr)))
    sun = ctx["sun"]
    sun.rotation_euler = (-pos).to_track_quat("-Z", "Y").to_euler()
    sun.data.color = (kit.srgb(scol[0]), kit.srgb(scol[1]), kit.srgb(scol[2]))
    cl, _, cl_lens, _ = bl_story.cam_at(sd, cur, t, {}, tl)
    ctx["fill"].location = (cl[0], cl[1], cl[2])
    sc.view_settings.exposure = L["exp"] + sd.get("exp", 0.0)
    ov = {"sun": en / 6.0, "camfill": L["fill"] * sd.get("fill", 1.0), "roomW": L["room"], "roomE": L["room"], "boatlight": L["boat"],
          "homelight": 1.0 if sd.get("look") == "home" else 0.0, "homelight2": 1.0 if sd.get("look") == "home" else 0.0}
    for k in range(len(ctx["lane"])):
        ov[f"lane{k}"] = L["lane"]
    for k in range(len(ctx["roomX"])):
        ov[f"roomX{k}"] = L["room"] * 0.8
    for k in range(len(ctx["strlights"])):
        ov[f"str{k}"] = L["str"]
    for nd in ctx["bulbmat"].node_tree.nodes:
        if nd.type == "EMISSION":
            nd.inputs["Strength"].default_value = 0.6 + 8.5 * L["str"]
    tor = sd.get("torch")
    tl_ = ctx["torch"]
    if tor:
        me = cast_state(tl, "me", t)
        tl_.location = (me[0] + tor[3], me[1] + tor[4], me[2] + 1.15)
        kit.aim(tl_, tor[:3])
        ov["torch"] = 1.0
    else:
        ov["torch"] = 0.0
    cd = kit.OBJ["cam"].data
    dof = sd.get("dof")
    if dof:
        cd.dof.use_dof = True
        cd.dof.focus_distance = dof[0]
        cd.dof.aperture_fstop = dof[1]
    else:
        cd.dof.use_dof = False
    # the plank counter
    c = cue_at(tl, "count", t)
    n = int(round(anim_val(c, "n", t, 208))) if c else 208
    place_inset(kit, ctx, n, cl_lens)
    # our bridge
    bc = cue_at(tl, "bridge", t)
    ctx["ours"].show(anim_val(bc, "vis", t, NPL))
    # the burnt bridges
    bu = cue_at(tl, "burnt", t)
    hs = anim_val(bu, "h", t, [0.0, 0.0, 0.0])
    sw = anim_val(bu, "sway", t, 0.0)
    tls = anim_val(bu, "tilt", t, [0.0, 0.0, 0.0])
    for (k, b), h, tt in zip(ctx["burnt"].items(), hs, tls):
        b.place(h, t, sw, tt)
    # the sea bridge
    sb = cue_at(tl, "sea", t)
    ctx["sea"].show(anim_val(sb, "n", t, 0))
    # small things that come and go
    sh = cue_at(tl, "show", t).get("on", [])
    hide(ctx["ticket"], "ticket" not in sh)
    hide(ctx["matches"], "matches" not in sh)
    hide(ctx["matchpair"], "matchpair" not in sh)
    hide(ctx["frost"], not cue_at(tl, "frost", t).get("on", False))
    hide(ctx["cards"], "cards" not in sh)
    tr = cue_at(tl, "tray", t)
    if tr and not tr.get("off"):
        ctx["tray"].location = (anim_val(tr, "x", t, -1.4), OURS_Y, 6.99)
        hide(ctx["tray"], False)
    else:
        hide(ctx["tray"], True)
    hide(ctx["plates"][2][0], "plate3" not in sh)
    hide(ctx["plates"][2][1], "plate3" not in sh)
    pc = cue_at(tl, "pip", t)
    pip = ctx["pip"]
    if pc and not pc.get("hidden"):
        p = anim_val(pc, "pos", t, pc["pos"])
        u = ss((t - pc["t"]) / max(1e-3, pc.get("dur", 1.0))) if "pos_to" in pc else 0.0
        hop = pc.get("hop", 0.0) * math.sin(math.pi * u) if "pos_to" in pc else 0.0
        pip.place(p[0], p[1], p[2] + hop, pc.get("yaw", 0), t, hop=hop / max(pc.get("hop", 1.0), 0.01))
    else:
        pip.place(0, 0, -9, 0, t, hidden=True)
    return ov


def cast_state(tl, who, t):
    from blocky import acting
    s = acting.state(tl, who, t, 0)
    return (s["x"], s["y"], s["z"])
