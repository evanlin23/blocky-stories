"""ep94-today-again: a frosting-pink corner bakery, its sunny street, a green yard behind a hedge, and the small rooms the
montage visits. Built from kit.py's parts. No letters anywhere: only numerals (the clocks, the calendar page) and glyphs.

Zones (metres): BAKERY x -4..4, y 0..7 (front wall at y 0 to -0.3, the street runs along x at y < 0); YARD x 6..22, y 0..13
behind the hedge at x 5.6; GARDEN (60,0); KITCHEN (100,0); BEDROOM (140,0); PRINT NOOK (180,0).

THE RULE METER is the calendar page in the top-left corner of every shot, parented to the camera: a big 12 and a yellow badge
with the count of todays (x1..x5). The "badge" cue changes the count (a quick pop); "tagbig" brings it to the middle.

Cues read here: clock, kclock, alarm (v=[h, m], dur eases from the last value), rain, hose, rainbow, badge, tagbig, bell,
wcake, wtilt, toast, puff, candle, letters, letters_off, glit, muff, cup, spill, spill_off, pour, bdoor, wet, balloons, jar,
clip, stopw, pen.
"""

from __future__ import annotations

import math
import random
import tempfile
from pathlib import Path

import bpy
from mathutils import Matrix, Vector as V
from PIL import Image, ImageDraw

from blocky import rig, faces

NAVY = "#23305e"
PINK = "#ffb3d4"
PISTA = "#a8e07a"
CREAM = "#fff3dc"
BLUEB = "#5a6fd6"
BRASS = "#d2a54a"
TMP = Path(tempfile.mkdtemp(prefix="ep94"))
BR = 140.0
K0 = 100.0
G0 = 60.0
NN = 180.0
TBL = (13.0, 6.0)
CLOCKP = (-0.7, 0.0, 2.4)


# ------------------------------------------------------------------------------------------------ small helpers
def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lin(h):
    h = h.lstrip("#")
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def lerp(a, b, u):
    return a + (b - a) * u


def cues_of(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def latest(tl, name, t):
    out = None
    for c in cues_of(tl, name):
        if c["t"] <= t + 1e-9:
            out = c
    return out


def eased(tl, name, t, key="v", default=None):
    """A value track: each cue eases from the one before it over its `dur` (0 or none: a step)."""
    cs = [c for c in cues_of(tl, name) if key in c and c["t"] <= t + 1e-9]
    if not cs:
        return default
    cur = cs[-1]
    cv = cur[key]
    if len(cs) == 1:
        return cv
    pv = cs[-2][key]
    d = cur.get("dur", 0.0)
    u = 1.0 if d <= 0 else ss((t - cur["t"]) / d)
    if isinstance(cv, (list, tuple)):
        return [lerp(a, b, u) for a, b in zip(pv, cv)]
    return lerp(pv, cv, u)


def track(tl, name, t, key="v"):
    cs = [c for c in cues_of(tl, name) if isinstance(c.get(key), (list, tuple))]
    if not cs:
        return None
    prev = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            prev = c
        else:
            if prev is None:
                return list(c[key])
            u = ss((t - prev["t"]) / max(1e-6, c["t"] - prev["t"]))
            return [lerp(a, b, u) for a, b in zip(prev[key], c[key])]
    return list(prev[key]) if prev else None


def on_at(tl, name, t, default=False):
    c = latest(tl, name, t)
    return default if c is None else bool(c.get("on"))


def since(tl, name, t):
    """Seconds since the latest cue of this name, or None."""
    c = latest(tl, name, t)
    return None if c is None else t - c["t"]


def basis(right, up):
    r, u = V(right).normalized(), V(up).normalized()
    n = r.cross(u)
    return Matrix(((r.x, u.x, n.x), (r.y, u.y, n.y), (r.z, u.z, n.z)))


def hide_tree(ob, hidden):
    ob.hide_render = hidden
    for c in ob.children_recursive:
        c.hide_render = hidden


def no_shadow(ob):
    try:
        ob.visible_shadow = False
    except Exception:
        pass


def seg(ob, a, b, r=None):
    """Stand a unit cylinder (built 1 m long along z) between two points."""
    a, b = V(a), V(b)
    d = b - a
    L = max(1e-4, d.length)
    ob.location = (a + b) / 2
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    ob.scale = (1, 1, L) if r is None else (r, r, L)


# ------------------------------------------------------------------------------------------------ drawn images
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc",
       "8": "abcdefg", "9": "abcdfg"}


def digit(d, ch, x, y, w, h, color, t=None):
    t = t or h / 6.5
    r = t / 2.2
    hh = (h - 3 * t) / 2
    rects = {"a": (x + t * 0.35, y, w - t * 0.7, t), "g": (x + t * 0.35, y + t + hh, w - t * 0.7, t),
             "d": (x + t * 0.35, y + h - t, w - t * 0.7, t),
             "f": (x, y + t * 0.5, t, t + hh + t * 0.5), "b": (x + w - t, y + t * 0.5, t, t + hh + t * 0.5),
             "e": (x, y + t + hh + t * 0.5, t, t + hh + t * 0.5), "c": (x + w - t, y + t + hh + t * 0.5, t, t + hh + t * 0.5)}
    for s in SEG[ch]:
        a, b, c, e = rects[s]
        d.rounded_rectangle((a, b, a + c, b + e), radius=r, fill=color)


def number(d, text, cx, y, h, color=NAVY, t=None):
    w = h * 0.5
    gap = h * 0.16
    total = len(text) * w + (len(text) - 1) * gap
    x = cx - total / 2
    for ch in text:
        digit(d, ch, x, y, w, h, color, t)
        x += w + gap


def times_mark(d, cx, cy, s, color=NAVY):
    """A fat multiplication sign."""
    w = max(6, int(s * 0.3))
    d.line((cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2), fill=color, width=w)
    d.line((cx - s / 2, cy + s / 2, cx + s / 2, cy - s / 2), fill=color, width=w)
    for sx in (-1, 1):
        for sy in (-1, 1):
            d.ellipse((cx + sx * s / 2 - w / 2, cy + sy * s / 2 - w / 2, cx + sx * s / 2 + w / 2, cy + sy * s / 2 + w / 2), fill=color)


def page_image():
    """The calendar page: coral header with two rings, a big 12."""
    W, H = 360, 440
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 14, W - 6, H - 6), radius=30, fill=NAVY)
    d.rounded_rectangle((12, 20, W - 12, H - 12), radius=26, fill="#fffaf0")
    d.rounded_rectangle((12, 20, W - 12, 128), radius=26, fill="#ff5c9a")
    d.rectangle((12, 90, W - 12, 128), fill="#ff5c9a")
    for x in (96, W - 96):
        d.ellipse((x - 20, 0, x + 20, 40), fill="#fffaf0", outline=NAVY, width=7)
    number(d, "12", W / 2, 150, 250, NAVY, t=44)
    return im


def badge_image(n):
    W = H = 200
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((4, 4, W - 4, H - 4), fill=NAVY)
    d.ellipse((14, 14, W - 14, H - 14), fill="#ffd23f")
    times_mark(d, 66, 100, 46)
    number(d, str(n), 132, 46, 108, NAVY, t=20)
    return im


def clock_decal(faceless_numbers=True):
    """Numerals 12, 3, 6, 9 and ticks on a transparent square, drawn dark navy (clock face colour is the cylinder under it)."""
    W = 600
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = W / 2
    for k in range(12):
        a = k * math.pi / 6
        big = k % 3 == 0
        r0, r1 = (232, 262) if not big else (240, 262)
        if big:
            continue
        d.line((c + r0 * math.sin(a), c - r0 * math.cos(a), c + r1 * math.sin(a), c - r1 * math.cos(a)), fill=NAVY, width=12)
    number(d, "12", c, 48, 88, NAVY, t=16)
    number(d, "6", c, W - 48 - 88, 88, NAVY, t=16)
    number(d, "3", W - 80, c - 44, 88, NAVY, t=16)
    number(d, "9", 80, c - 44, 88, NAVY, t=16)
    return im


def digital_image(h, m):
    """A small navy readout with bright numerals, 9:02 style, for the wall clock's face."""
    W, H = 460, 200
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, W - 1, H - 1), radius=34, fill=NAVY)
    col = "#fff3a0"
    hh = 128
    y0 = (H - hh) // 2
    number(d, str(h), 92, y0, hh, col, t=22)
    for yy in (y0 + hh * 0.3, y0 + hh * 0.7):
        d.ellipse((W / 2 - 11, yy - 11, W / 2 + 11, yy + 11), fill=col)
    number(d, f"{m:02d}", 330, y0, hh, col, t=22)
    return im


def ghost_image():
    """My huge surprised face for the cake-case glass: skin, dark curls, wide eyes, raised brows, an O mouth."""
    W = H = 512
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ink = "#24131f"
    d.rounded_rectangle((90, 110, 422, 450), radius=110, fill="#f0bd92", outline=ink, width=8)
    for k in range(11):
        a = math.pi + k * math.pi / 10
        d.ellipse((256 + 190 * math.cos(a) - 52, 190 + 140 * math.sin(a) - 52, 256 + 190 * math.cos(a) + 52, 190 + 140 * math.sin(a) + 52), fill="#1a1512")
    d.rounded_rectangle((100, 100, 412, 190), radius=40, fill="#1a1512")
    for sx in (-1, 1):
        cx = 256 + sx * 88
        d.ellipse((cx - 52, 230 - 52, cx + 52, 230 + 52), fill="#ffffff", outline=ink, width=8)
        d.ellipse((cx - 18, 230 - 18, cx + 18, 230 + 18), fill=ink)
        d.line((cx - 56, 148, cx + 56, 138 if sx < 0 else 138), fill=ink, width=14)
    d.ellipse((206, 336, 306, 436), fill="#7a2a3a", outline=ink, width=8)
    for sx in (-1, 1):
        d.ellipse((256 + sx * 150 - 26, 320 - 16, 256 + sx * 150 + 26, 320 + 16), fill="#ff9e8a")
    return im


def newspaper_image():
    W, H = 400, 520
    im = Image.new("RGB", (W, H), "#f3ecd9")
    d = ImageDraw.Draw(im)
    d.rectangle((24, 24, W - 24, 92), fill="#2a2a34")
    d.rectangle((24, 110, 210, 260), fill="#9aa7b8")
    d.ellipse((92, 130, 150, 190), fill="#d7b79a")
    d.rectangle((75, 190, 170, 255), fill="#566a8a")
    rng = random.Random(4)
    for col in range(2):
        x0 = 230 if col == 0 else 24
        y = 110 if col == 0 else 280
        while y < (250 if col == 0 else H - 30):
            d.rounded_rectangle((x0, y, x0 + (150 if col == 0 else 352) - rng.randint(0, 50), y + 14), radius=5, fill="#4a4a54")
            y += 28
    for y in range(280, H - 30, 28):
        pass
    return im


def clip_image():
    """The clipboard sheet: three rows of glyph ticks and a doodle of my face (curly hair, two dots, a smile). No words."""
    W, H = 360, 480
    im = Image.new("RGB", (W, H), "#fffdf4")
    d = ImageDraw.Draw(im)
    rng = random.Random(8)
    for r in range(3):
        y = 36 + r * 62
        d.line((24, y + 40, W - 24, y + 40), fill="#cdd5e6", width=3)
        for k in range(7):
            x = 34 + k * 44
            if rng.random() < 0.8:
                d.line((x, y + 20, x + 12, y + 36), fill="#2f9d57", width=7)
                d.line((x + 12, y + 36, x + 32, y + 4), fill="#2f9d57", width=7)
            else:
                d.ellipse((x + 4, y + 6, x + 26, y + 32), outline="#e0457b", width=6)
    cx, cy = 180, 345
    d.ellipse((cx - 62, cy - 62, cx + 62, cy + 62), fill="#f3c9a0", outline="#23305e", width=6)
    for k in range(9):   # curly hair
        a = math.pi + k * math.pi / 8
        d.ellipse((cx + 62 * math.cos(a) - 17, cy + 62 * math.sin(a) - 17, cx + 62 * math.cos(a) + 17, cy + 62 * math.sin(a) + 17), fill="#1a1512")
    d.ellipse((cx - 28, cy - 10, cx - 14, cy + 6), fill="#23305e")
    d.ellipse((cx + 14, cy - 10, cx + 28, cy + 6), fill="#23305e")
    d.arc((cx - 28, cy + 6, cx + 28, cy + 42), 20, 160, fill="#23305e", width=6)
    d.line((300, 300, 300, 400), fill="#e0457b", width=6)
    d.polygon([(300, 296), (286, 322), (314, 322)], fill="#e0457b")
    return im


_IMG_N = [0]


def img_material(kit, name, im, rough=0.6, emit=0.0, alpha=False):
    _IMG_N[0] += 1
    p = TMP / f"{name}{_IMG_N[0]}.png"
    im.save(p)
    m = kit._new(f"img {name} {_IMG_N[0]}")
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(p))
    tex.image.colorspace_settings.name = "sRGB"
    tex.interpolation = "Linear"
    uv = nt.nodes.new("ShaderNodeUVMap")
    nt.links.new(uv.outputs["UV"], tex.inputs["Vector"])
    if emit:
        for n in list(nt.nodes):
            if n.type == "BSDF_PRINCIPLED":
                nt.nodes.remove(n)
        e = nt.nodes.new("ShaderNodeEmission")
        e.inputs["Strength"].default_value = emit
        nt.links.new(tex.outputs["Color"], e.inputs["Color"])
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(tex.outputs["Alpha"], mix.inputs["Fac"])
        nt.links.new(tr.outputs[0], mix.inputs[1])
        nt.links.new(e.outputs[0], mix.inputs[2])
        out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
        return m
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    if alpha:
        nt.links.new(tex.outputs["Alpha"], b.inputs["Alpha"])
    kit._fogged(m, b.outputs[0])
    return m


def img_plane(kit, name, w, h, mat, loc=(0, 0, 0), parent=None, right=(1, 0, 0), up=(0, 1, 0)):
    x, y = w / 2, h / 2
    ob = kit.mesh_obj(name, [(-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0)], [(0, 1, 2, 3)], mat, parent, loc)
    uv = ob.data.uv_layers.new(name="UV")
    for lp in ob.data.loops:
        v = ob.data.vertices[lp.vertex_index].co
        uv.data[lp.index].uv = ((v.x + x) / w, (v.y + y) / h)
    ob.rotation_euler = basis(right, up).to_euler()
    return ob


def film(kit, name, tint="#eaf6ff", a=0.16):
    """Thin glass: mostly clear, a little glossy."""
    m = kit._new(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type == "BSDF_PRINCIPLED":
            nt.nodes.remove(n)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Color"].default_value = (*lin(tint), 1)
    gl.inputs["Roughness"].default_value = 0.08
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = a
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(gl.outputs[0], mix.inputs[2])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


# ------------------------------------------------------------------------------------------------ materials
def materials(kit):
    P = kit.plastic
    M = {}
    M["pink"] = P(PINK, 0.8, "wall pink")
    M["pink2"] = P("#ff9fc9", 0.8, "wall pink deep")
    M["pista"] = P(PISTA, 0.55, "pistachio")
    M["cream"] = P(CREAM, 0.7, "cream")
    M["white"] = P("#fbf8f2", 0.6, "white")
    M["blue"] = P(BLUEB, 0.55, "blueberry")
    M["brass"] = kit.metal(BRASS, 0.3, "brass")
    M["dark"] = P("#2a2a34", 0.7, "dark")
    M["tile"] = kit.checker("#fff3dc", "#ffd9e8", 2.0, "bakery tile", 0.4)
    M["glass"] = film(kit, "glass film")
    M["water"] = kit.emit("#86bdf0", 0.55, "water streak")
    M["drop"] = kit.emit("#8fc4f2", 0.6, "spray drop")
    M["road"] = kit.texture("asphalt", 0.6, tint="#a8aebb", rough=0.8, mat_name="road")
    M["grass"] = kit.texture("grass", 1.0, tint="#8fe56e", rough=0.9, mat_name="lawn")
    M["walk"] = P("#e6e2da", 0.85, "sidewalk")
    M["leaf"] = P("#4cc25a", 0.8, "hedge")
    M["dirt"] = P("#8a5a3a", 0.95, "dirt")
    M["wood"] = kit.texture("wood", 1.2, tint="#e0b890", rough=0.6, mat_name="plank")
    M["steel"] = kit.metal("#cfd3d8", 0.3, "steel")
    M["coffee"] = P("#5a3320", 0.4, "coffee")
    M["gold"] = P("#f4c542", 0.4, "gold")
    return M


def mat_hex(kit, hexc, rough=0.6):
    return kit.plastic(hexc, rough)


# ------------------------------------------------------------------------------------------------ clocks
def make_clock(kit, M, name, c, facing, r=0.5, hands=("hour", "min", "sec"), ctx=None):
    """A round wall clock at c, facing +y (viewer at +y) or -y. Returns (hour, minute, second pivots, sign)."""
    sgn = -1.0 if facing > 0 else 1.0     # rotation about y: clockwise for the viewer
    cx, cy, cz = c
    d = 1.0 if facing > 0 else -1.0
    k = r / 0.5
    kit.cyl(f"{name}.rim", r + 0.06 * k, 0.08 * k, (cx, cy + d * 0.04 * k, cz), M["brass"], rot=(math.pi / 2, 0, 0), n=40)
    kit.cyl(f"{name}.face", r, 0.08 * k, (cx, cy + d * 0.052 * k, cz), kit.plastic("#fffaf0", 0.5, "clock face"), rot=(math.pi / 2, 0, 0), n=40)
    dec = img_material(kit, f"{name}_decal", clock_decal(), 0.5, alpha=True)
    img_plane(kit, f"{name}.decal", 2 * r * 0.98, 2 * r * 0.98, dec, (cx, cy + d * 0.105 * k, cz), None,
              right=(-d, 0, 0), up=(0, 0, 1))
    ph = kit.empty(f"{name}.hpiv", (cx, cy + d * 0.125 * k, cz))
    pm = kit.empty(f"{name}.mpiv", (cx, cy + d * 0.145 * k, cz))
    pc = kit.empty(f"{name}.spiv", (cx, cy + d * 0.165 * k, cz))
    kit.box(f"{name}.hour", (0.06 * k, 0.02 * k, 0.62 * r), (0, 0, 0.31 * r), M["dark"], ph, bevel=0.01 * k)
    kit.box(f"{name}.min", (0.045 * k, 0.02 * k, 0.86 * r), (0, 0, 0.43 * r), M["dark"], pm, bevel=0.01 * k)
    kit.box(f"{name}.sec", (0.02 * k, 0.02 * k, 0.92 * r), (0, 0, 0.36 * r), kit.plastic("#e0304a", 0.5, "second hand"), pc)
    kit.sphere(f"{name}.cap", 0.04 * k, (cx, cy + d * 0.185 * k, cz), M["brass"])
    return {"h": ph, "m": pm, "s": pc, "sgn": sgn}


def set_hands(cl, h, m, sec=None):
    sg = cl["sgn"]
    cl["h"].rotation_euler = (0, sg * (((h % 12) + m / 60.0) / 12.0) * 2 * math.pi, 0)
    cl["m"].rotation_euler = (0, sg * (m / 60.0) * 2 * math.pi, 0)
    if sec is not None:
        cl["s"].rotation_euler = (0, sg * (sec / 60.0) * 2 * math.pi, 0)


# ------------------------------------------------------------------------------------------------ the bakery
def build_bakery(kit, M, ctx):
    B = kit.box
    # floor, side walls, ceiling, roof
    B("bk.floor", (8.8, 7.6, 0.2), (0, 3.5, -0.1), M["tile"])
    B("bk.left", (0.3, 7.6, 3.6), (-4.15, 3.5, 1.8), M["pink"])
    B("bk.right", (0.3, 7.6, 3.6), (4.15, 3.5, 1.8), M["pink"])
    B("bk.ceil", (8.6, 7.4, 0.1), (0, 3.5, 3.65), M["cream"])
    B("bk.roof", (9.0, 7.8, 0.25), (0, 3.6, 3.85), M["pink2"], bevel=0.04)
    # the back wall with the back door cut out (door x 2.3..3.7)
    B("bk.back.l", (6.45, 0.3, 3.6), (-0.875, 7.15, 1.8), M["pink"])
    B("bk.back.r", (0.45, 0.3, 3.6), (3.925, 7.15, 1.8), M["pink"])
    B("bk.back.t", (1.4, 0.3, 1.2), (3.0, 7.15, 3.0), M["pink"])
    # the front wall around the door (x -3.3..-1.9, z 0..2.4) and the window (x 0.5..3.5, z 0.9..2.9)
    fw = lambda nm, x0, x1, z0, z1: B(nm, (x1 - x0, 0.3, z1 - z0), ((x0 + x1) / 2, -0.15, (z0 + z1) / 2), M["pink"])
    fw("bk.f1", -4.3, -3.3, 0, 3.6)
    fw("bk.f2", -3.3, -1.9, 2.4, 3.6)
    fw("bk.f3", -1.9, 0.5, 0, 3.6)
    fw("bk.f4", 0.5, 3.5, 0, 0.9)
    fw("bk.f5", 0.5, 3.5, 2.9, 3.6)
    fw("bk.f6", 3.5, 4.3, 0, 3.6)
    # window frame and sill (cream, proud of the wall faces)
    for nm, sz, loc in (("t", (3.2, 0.36, 0.1), (2.0, -0.15, 2.95)), ("b", (3.2, 0.36, 0.1), (2.0, -0.15, 0.85)),
                        ("l", (0.1, 0.36, 2.1), (0.45, -0.15, 1.9)), ("r", (0.1, 0.36, 2.1), (3.55, -0.15, 1.9))):
        B(f"win.{nm}", sz, loc, M["cream"], bevel=0.015)
    B("win.sill", (3.4, 0.5, 0.07), (2.0, -0.45, 0.82), M["cream"], bevel=0.02)
    # door frame, the door on its hinge (opens into the shop), a blueberry slab with a brass knob
    B("door.top", (1.6, 0.36, 0.1), (-2.6, -0.15, 2.45), M["cream"], bevel=0.015)
    for s in (-1, 1):
        B(f"door.side{s}", (0.1, 0.36, 2.4), (-2.6 + s * 0.75, -0.15, 1.2), M["cream"], bevel=0.015)
    hinge = kit.empty("door.hinge", (-3.3, -0.15, 0))
    B("door.slab", (1.4, 0.07, 2.35), (0.7, 0, 1.18), M["blue"], hinge, bevel=0.02)
    B("door.glass", (0.8, 0.08, 1.0), (0.7, 0, 1.5), M["glass"], hinge)
    kit.sphere("door.knob", 0.05, (1.2, 0.07, 1.0), M["brass"], hinge)
    ctx["door"] = hinge
    # an awning over the door (stripes) and the doormat (raised edge)
    for i in range(6):
        c = "#ff7fb2" if i % 2 == 0 else "#fff8ee"
        B(f"awn{i}", (0.28, 0.9, 0.06), (-3.15 + i * 0.28 + 0.14, -0.7, 2.62), kit.plastic(c, 0.7), rot=(0.25, 0, 0))
    B("mat", (1.2, 0.7, 0.07), (-2.6, 0.9, 0.035), M["blue"], bevel=0.02)
    B("mat.in", (1.0, 0.5, 0.075), (-2.6, 0.9, 0.04), M["cream"], bevel=0.02)
    # the bell on a bracket over the door (inside): swings on the bell cue
    kit.box("bell.bracket", (0.05, 0.35, 0.05), (-2.6, 0.2, 2.62), M["brass"])
    bp = kit.empty("bell.piv", (-2.6, 0.3, 2.6))
    kit.cyl("bell.cup", 0.12, 0.16, (0, 0, -0.09), M["brass"], bp, n=16, r2=0.04)
    kit.sphere("bell.clap", 0.035, (0, 0, -0.19), M["brass"], bp)
    ctx["bell"] = bp
    # the wall clock, left of the window (face to +y)
    ctx["clock"] = make_clock(kit, M, "wall clock", CLOCKP, +1, 0.5)
    ctx["dig"] = {}
    for hm_ in ((9, 2), (9, 15), (9, 30), (9, 1), (9, 0)):
        dm = img_material(kit, f"dig{hm_[0]}{hm_[1]}", digital_image(*hm_), 0.5, emit=1.0)
        ctx["dig"][hm_] = img_plane(kit, f"dig{hm_[1]}", 0.46, 0.2, dm, (CLOCKP[0], CLOCKP[1] + 0.116, CLOCKP[2] - 0.2),
                                    None, right=(-1, 0, 0), up=(0, 0, 1))
    # the counter: pistachio, with a cream top; a brass edge plate by the till with two pink tally strokes
    B("counter", (6.2, 1.0, 1.0), (-0.5, 4.3, 0.5), M["pista"], bevel=0.02)
    B("counter.top", (6.4, 1.2, 0.07), (-0.5, 4.3, 1.035), M["cream"], bevel=0.02)
    B("counter.plate", (1.0, 0.03, 0.16), (2.0, 3.69, 0.96), M["brass"], bevel=0.005)
    for k in range(2):
        B(f"tally{k}", (0.035, 0.012, 0.12), (1.88 + k * 0.24, 3.664, 0.96), kit.emit("#ff7fb8", 1.2, "tally pink"), rot=(0, 0.25, 0))
    # the glass case on the left of the counter, cakes and muffins inside
    B("case.base", (2.3, 0.9, 0.22), (-2.4, 4.3, 1.18), M["white"], bevel=0.02)
    cake_cols = ["#ff9fc9", "#fff8ee", "#c8895a", "#ffe58a", "#a8e07a"]
    for i in range(5):
        x = -3.2 + i * 0.4
        cc = kit.plastic(cake_cols[i], 0.5)
        kit.cyl(f"case.cake{i}", 0.17, 0.2, (x, 4.1, 1.39), cc, n=18)
        kit.cyl(f"case.top{i}", 0.17, 0.03, (x, 4.1, 1.505), kit.plastic("#fff8ee", 0.4), n=18)
        kit.sphere(f"case.cherry{i}", 0.04, (x, 4.1, 1.55), kit.plastic("#e0304a", 0.35, "cherry"), seg=10)
        kit.cyl(f"case.cup{i}", 0.09, 0.09, (x, 4.55, 1.34), kit.plastic("#fff3dc", 0.6), n=14, r2=0.07)
        kit.sphere(f"case.muff{i}", 0.1, (x, 4.55, 1.42), kit.plastic(["#c8895a", "#5a6fd6", "#c8895a", "#5a6fd6", "#c8895a"][i], 0.6), seg=12)
    case_glass = M["glass"]
    for nm, sz, loc in (("f", (2.3, 0.03, 0.55), (-2.4, 3.86, 1.5)), ("t", (2.3, 0.9, 0.03), (-2.4, 4.3, 1.8)),
                        ("l", (0.03, 0.9, 0.55), (-3.55, 4.3, 1.5)), ("r", (0.03, 0.9, 0.55), (-1.25, 4.3, 1.5)),
                        ("b", (2.3, 0.03, 0.55), (-2.4, 4.72, 1.5))):
        o = B(f"case.glass{nm}", sz, loc, case_glass)
        no_shadow(o)
    for x in (-3.55, -1.25):
        for y in (3.86, 4.74):
            B(f"case.post{x}{y}", (0.04, 0.04, 0.58), (x, y, 1.5), M["brass"])
    # the register, the pink bag, the candle muffin
    B("reg", (0.5, 0.4, 0.26), (1.75, 4.45, 1.2), M["white"], bevel=0.03)
    B("reg.screen", (0.3, 0.03, 0.18), (1.75, 4.28, 1.42), M["dark"], rot=(-0.35, 0, 0))
    B("bag", (0.22, 0.12, 0.3), (-0.5, 4.45, 1.22), kit.plastic("#ff7fb2", 0.6, "bag pink"), bevel=0.01)
    mf = kit.empty("muffin", (-0.6, 4.3, 1.07))
    kit.cyl("muffin.cup", 0.08, 0.1, (0, 0, 0.05), kit.plastic("#fff3dc", 0.6), mf, n=14, r2=0.1)
    kit.sphere("muffin.top", 0.11, (0, 0, 0.13), kit.plastic("#7a86e8", 0.55, "blueberry muffin"), mf, seg=12)
    ctx["muffin"] = mf
    cm = kit.empty("candle.muffin", (2.4, 4.4, 1.07))
    kit.cyl("cm.cup", 0.08, 0.1, (0, 0, 0.05), kit.plastic("#fff3dc", 0.6), cm, n=14, r2=0.1)
    kit.sphere("cm.top", 0.11, (0, 0, 0.13), kit.plastic("#c8895a", 0.6, "choc muffin"), cm, seg=12)
    can = kit.empty("candle", (0, 0, 0.24), cm)
    kit.cyl("candle.stick", 0.012, 0.14, (0, 0, 0), kit.plastic("#ff6fa8", 0.5), can, n=8)
    flame = kit.sphere("candle.flame", 0.022, (0, 0, 0.09), kit.emit("#ffb347", 4.0, "flame"), can, seg=8)
    ctx["candle"] = can
    ctx["flame"] = flame
    # shelves with loaves on the back wall
    for i, z in enumerate((1.3, 2.0, 2.7)):
        B(f"shelf{i}", (3.4, 0.4, 0.06), (-1.8, 6.8, z), M["wood"])
        for j in range(5):
            kit.cyl(f"loaf{i}{j}", 0.1, 0.4, (-3.0 + j * 0.62, 6.8, z + 0.14), kit.plastic("#d49a5a", 0.6, "bread"), rot=(0, math.pi / 2, 0), n=12)
    # the back door (a slab on a hinge) and the bright alley behind it
    bh = kit.empty("bdoor.hinge", (2.3, 7.15, 0))
    B("bdoor.slab", (1.4, 0.07, 2.3), (0.7, 0, 1.15), M["pista"], bh, bevel=0.02)
    kit.sphere("bdoor.knob", 0.05, (1.2, -0.07, 1.0), M["brass"], bh)
    ctx["bdoor"] = bh
    B("alley.floor", (12, 6.0, 0.2), (0, 10.5, -0.1), M["walk"])
    B("alley.wall", (12, 0.4, 5.0), (0, 13.7, 2.5), kit.texture("brick", 1.0, tint="#f7c8c0", mat_name="alley brick"))
    kit.prop("trashcan_cylindric", (1.0, 8.4, 0), height=0.8, tint="#9ad0f0")
    kit.prop("houseplant_1", (4.4, 8.0, 0), height=0.8)
    # tables: stand-up tables with a cup or a muffin, for the customers
    for i, (x, y) in enumerate(((-1.9, 1.6), (-0.7, 2.4), (0.5, 1.7), (2.9, 1.8), (1.1, 3.2), (-2.1, 3.2))):
        kit.cyl(f"tbl{i}.top", 0.34, 0.05, (x, y, 1.0), M["white"], n=20)
        kit.cyl(f"tbl{i}.pole", 0.04, 0.98, (x, y, 0.5), M["steel"], n=8)
        kit.cyl(f"tbl{i}.base", 0.2, 0.04, (x, y, 0.02), M["steel"], n=14)
        kit.cyl(f"tbl{i}.cup", 0.045, 0.09, (x + 0.1, y - 0.1, 1.075), kit.plastic("#ff9fc9", 0.5), n=10)
    # lights: soft area light overhead, a face fill, and the sun through the window
    kit.light("bk area", "AREA", (0, 3.4, 3.45), 380.0, "#fff4e6", size=6.0)
    kit.light("bk face", "POINT", (0.8, 2.0, 2.4), 70.0, "#fff0dc", size=0.8)
    kit.light("bk back", "POINT", (0.0, 6.2, 2.8), 60.0, "#ffe9d0", size=0.8)
    # the pour: a coffee pot in n1's hands and a stream hanging in the air
    pot = kit.empty("pot", (0, 0, -40))
    kit.cyl("pot.body", 0.07, 0.16, (0, 0, 0), kit.plastic("#c9ccd6", 0.3, "pot steel"), pot, n=14, r2=0.09)
    kit.box("pot.spout", (0.05, 0.1, 0.03), (0, -0.1, 0.06), kit.plastic("#c9ccd6", 0.3, "pot steel"), pot)
    kit.box("pot.handle", (0.03, 0.03, 0.14), (0, 0.1, 0.0), M["dark"], pot)
    ctx["pot"] = pot
    stream = kit.cyl("pour.stream", 0.012, 1.0, (0, 0, -40), M["coffee"], n=8)
    ctx["stream"] = stream
    # Mom's cup, the spill, the pink bag's muffin lives above
    cup = kit.empty("cup", (0, 0, -40))
    kit.cyl("cup.body", 0.05, 0.1, (0, 0, 0), kit.plastic("#ffffff", 0.35, "mug"), cup, n=14, r2=0.04)
    kit.cyl("cup.coffee", 0.044, 0.01, (0, 0, 0.05), M["coffee"], cup, n=14)
    ctx["cup"] = cup
    sp = kit.box("spill", (0.62, 0.42, 0.02), (-0.1, 4.0, -40), kit.plastic("#7a3f1c", 0.25, "spill coffee"), bevel=0.005)
    ctx["spill"] = sp
    # my surprised face "reflected" in the cake case glass (shown by the "ghost" cue), 1.5 cm proud of the glass
    gm = img_material(kit, "ghost", ghost_image(), 0.4, emit=1.0)
    ctx["ghost"] = img_plane(kit, "ghost", 0.9, 0.9, gm, (-2.0, 3.835, 1.52), None, right=(-1, 0, 0), up=(0, 0, 1))
    ctx["ghost"].hide_render = True
    ctx["ghost_alpha"] = gm
    kit.light("alley fill", "POINT", (3.0, 10.4, 3.2), 420.0, "#fff4e6", size=1.0)
    # the coffee splash: blobs thrown up from the spill
    ctx["splash"] = [kit.sphere(f"splash{i}", 0.035 + 0.01 * (i % 3), (0, 0, -40), M["coffee"], seg=8) for i in range(12)]
    # the rain on the window: streaks hung in the opening (centre plane y = -0.1)
    rng = random.Random(11)
    ctx["streaks"] = []
    for i in range(44):
        x = 0.62 + (i + rng.random() * 0.6) * (2.76 / 44)
        ln = rng.uniform(0.22, 0.6)
        o = B(f"streak{i}", (0.017, 0.014, ln), (x, -0.1, 2.0), M["water"], bevel=0.004)
        ctx["streaks"].append((o, rng.uniform(0.35, 0.8), rng.random() * 2.2, ln))
        no_shadow(o)


# ------------------------------------------------------------------------------------------------ the street and the yard
def build_street(kit, M, ctx):
    B = kit.box
    kit.plane("ground", (300, 300), (0, 0, -0.02), M["grass"])
    B("walk", (70, 2.8, 0.1), (0, -1.7, -0.03), M["walk"])
    B("curb", (70, 0.2, 0.14), (0, -3.15, -0.02), kit.plastic("#cfcac2", 0.8, "curb"))
    B("road", (70, 6.4, 0.06), (0, -6.4, -0.04), M["road"])
    for k in range(14):
        B(f"dash{k}", (1.6, 0.14, 0.012), (-24 + k * 4.0, -6.4, -0.005), kit.plastic("#fff3c2", 0.7, "dash"))
    B("walk2", (70, 3.0, 0.1), (0, -11.0, -0.03), M["walk"])
    # houses on the far side and either side of the bakery
    bl = ["sub_building_type_a", "sub_building_type_c", "sub_building_type_f", "sub_building_type_a", "sub_building_type_c"]
    tints = ["#ffd9a8", "#bfe6ff", "#d9f2c4", "#ffc9d9", "#fff0b3"]
    for i, x in enumerate((-18, -8, 2, 12, 22)):
        kit.prop(bl[i], (x, -17.5, 0), rot=0, height=5.6, tint=tints[i])
    for i, x in enumerate((-12, -20)):   # the row to the left of the bakery
        kit.prop(bl[(i + 2) % 5], (x, 3.5, 0), rot=-90 + 90, height=5.0, tint=tints[(i + 1) % 5])
    for i, (x, y) in enumerate(((-14, -4.8), (-6, -4.8), (9, -4.8), (17, -4.8), (-3, -13), (6, -13))):
        kit.prop("sub_tree_large" if i % 2 else "sub_tree_small", (x, y, 0), height=4.2 if i % 2 else 3.2)
    # the flower bed under the front-right corner, where the ladder stands
    B("bed", (1.6, 1.0, 0.16), (3.85, -1.0, 0.08), M["dirt"], bevel=0.03)
    for i in range(7):
        c = ["#ff6fa8", "#ffd23f", "#ffffff", "#ff8a3d", "#b69be0", "#ff6fa8", "#ffd23f"][i]
        kit.sphere(f"fl{i}", 0.09, (3.2 + i * 0.22, -1.0 + (i % 2) * 0.3 - 0.15, 0.3), kit.plastic(c, 0.5), seg=8)
        kit.cyl(f"fl{i}.stem", 0.012, 0.22, (3.2 + i * 0.22, -1.0 + (i % 2) * 0.3 - 0.15, 0.19), kit.plastic("#3a9a48", 0.7, "stem"), n=6)
    # the ladder: two rails and rungs, leaning on the front wall right of the window (top y -0.35, foot y -1.05)
    ang = math.atan2(0.7, 5.2)
    lr = kit.empty("ladder.rot", (3.85, -0.7, 2.6), rot=(-ang, 0, 0))
    alu = kit.metal("#d8dde6", 0.35, "ladder alu")
    for sx in (-1, 1):
        B(f"rail{sx}", (0.06, 0.06, 5.2), (sx * 0.42, 0, 0), alu, lr)
    for k in range(17):
        B(f"rung{k}", (0.84, 0.05, 0.05), (0, 0, -2.5 + k * 0.3), alu, lr)
    ctx["ladder"] = lr
    # a second, free-standing ladder in the yard for the reveal picture (shown by the "ladder2" cue)
    l2 = kit.empty("ladder2", (7.4, 5.4, 0.0))
    for sx in (-1, 1):
        for sy, a in ((-1, -0.17), (1, 0.17)):
            B(f"l2rail{sx}{sy}", (0.06, 0.06, 2.5), (sx * 0.36, sy * 0.22, 1.2), alu, l2, rot=(a, 0, 0))
    for k in range(7):
        B(f"l2rung{k}", (0.72, 0.05, 0.05), (0, -0.2 + 0.0 * k, 0.3 + k * 0.32), alu, l2)
    B("l2top", (0.8, 0.5, 0.06), (0, 0, 2.42), kit.plastic("#ff6fa8", 0.5, "l2 top"), l2)
    ctx["ladder2"] = l2
    # the hose: five green tubes from Okafor's hand to the ground (placed each frame), a nozzle, and the spray drops
    hose_m = kit.plastic("#3fb36b", 0.5, "hose")
    ctx["hose"] = [kit.cyl(f"hose{i}", 0.025, 1.0, (0, 0, -40), hose_m, n=8) for i in range(5)]
    ctx["nozzle"] = kit.cyl("nozzle", 0.03, 0.12, (0, 0, -40), kit.plastic("#ffd23f", 0.4, "nozzle"), n=10, r2=0.04)
    rng = random.Random(5)
    ctx["drops"] = []
    for i in range(60):
        o = kit.box(f"spray{i}", (0.011, 0.011, 0.3), (0, 0, -40), M["drop"])
        no_shadow(o)
        ctx["drops"].append((o, rng.uniform(1.8, 3.0), rng.random() * 3.4, rng.uniform(-1, 1), rng.uniform(-0.12, 0.12)))
    # a rainbow: seven thin arcs, facing the street (y = -1.0 plane)
    ctx["rainbow"] = kit.empty("rainbow", (2.0, -0.85, 3.4))
    cols = ["#ff4d4d", "#ff9f40", "#ffe14d", "#58d86a", "#4db8ff", "#5a6fd6", "#b06af0"]
    for i, c in enumerate(cols):
        r0, r1 = 0.62 + i * 0.045, 0.62 + (i + 1) * 0.045
        verts, faces_ = [], []
        n = 18
        for k in range(n + 1):
            a = math.radians(20 + 140 * k / n)
            verts += [(r0 * math.cos(a), 0, r0 * math.sin(a) - 0.4), (r1 * math.cos(a), 0, r1 * math.sin(a) - 0.4)]
        for k in range(n):
            faces_.append((2 * k, 2 * k + 1, 2 * k + 3, 2 * k + 2))
        o = kit.mesh_obj(f"rb{i}", verts, faces_, kit.emit(c, 0.9, f"rb {c}"), ctx["rainbow"])
        no_shadow(o)
    # the sun
    kit.light("sun", "SUN", (30, -40, 60), 3.0, "#fff1dc")
    kit.aim(kit.LIGHTS["sun"]["obj"], (0, 0, 0))
    kit.light("street fill", "POINT", (0.0, -6.0, 4.0), 400.0, "#fff4e6", size=1.0)


def build_yard(kit, M, ctx):
    B = kit.box
    kit.plane("yard", (30, 30), (14, 7, -0.01), M["grass"])
    # hedges: along x = 5.6 (the hedge to peek past, 1.1 m), along the street side, along the back
    B("hedge.w", (0.9, 14.0, 1.1), (5.7, 6.5, 0.55), M["leaf"], bevel=0.25)
    B("hedge.s", (17.0, 0.9, 1.5), (14.0, -0.6, 0.75), M["leaf"], bevel=0.25)
    B("hedge.n", (17.0, 0.9, 1.5), (14.0, 13.6, 0.75), M["leaf"], bevel=0.25)
    B("hedge.e", (0.9, 14.0, 1.5), (22.4, 6.5, 0.75), M["leaf"], bevel=0.25)
    # the cake table: a folding table with a cream cloth, a three-layer cake, a candle
    tx, ty = TBL
    B("ytbl.top", (1.8, 0.9, 0.05), (tx, ty, 0.8), M["white"], bevel=0.01)
    B("ytbl.cloth", (1.9, 1.0, 0.5), (tx, ty, 0.58), kit.plastic("#fff3dc", 0.8, "cloth"), bevel=0.04)
    for i, (r, h, c) in enumerate(((0.42, 0.2, "#ff9fc9"), (0.32, 0.2, "#fff8ee"), (0.22, 0.2, "#a8e07a"))):
        kit.cyl(f"ycake{i}", r, h, (tx, ty, 0.9 + i * 0.2), kit.plastic(c, 0.5), n=22)
        kit.cyl(f"ycake{i}.t", r + 0.01, 0.03, (tx, ty, 1.0 + i * 0.2), kit.plastic("#ffffff", 0.4), n=22)
    kit.sphere("ycake.cherry", 0.05, (tx, ty, 1.55), kit.plastic("#e0304a", 0.35, "cherry"), seg=10)
    # the glitter on the cake appears with the jar
    ctx["glitter_cake"] = []
    rng = random.Random(9)
    for i in range(40):
        a = rng.random() * 6.28
        r = rng.random() * 0.4
        o = B(f"gc{i}", (0.02, 0.02, 0.01), (tx + r * math.cos(a), ty + r * math.sin(a), 1.62 - 0.2 * (r / 0.4)),
              kit.emit(["#ffe14d", "#ff7fb2", "#7fe0ff"][i % 3], 2.0, f"gl{i % 3}"))
        ctx["glitter_cake"].append(o)
    # tape marks on the grass: a little X per person, and a rectangle round the table
    cols = ["#ffd23f", "#ff6fa8", "#4db8ff"]
    ring = [(-3.0, 0.0), (-2.2, -2.3), (0.0, -3.2), (2.2, -2.3), (3.0, 0.0), (2.2, 2.4), (0.0, 3.3), (-2.2, 2.4)]
    spots = [(tx + x * 1.15, ty + y * 1.15) for x, y in ring] + [(tx + 1.2, ty + 3.9), (tx - 1.2, ty + 1.8)]
    for i, (x, y) in enumerate(spots):
        c = kit.plastic(cols[i % 3], 0.6, f"tape{i % 3}")
        for s in (-1, 1):
            B(f"tape{i}.{s}", (0.04, 0.5, 0.008), (x, y, 0.004), c, rot=(0, 0, s * 0.7))
    for nm, sz, loc in (("n", (2.4, 0.04, 0.008), (tx, ty + 0.9, 0.004)), ("s", (2.4, 0.04, 0.008), (tx, ty - 0.9, 0.004)),
                        ("e", (0.04, 1.8, 0.008), (tx + 1.2, ty, 0.004)), ("w", (0.04, 1.8, 0.008), (tx - 1.2, ty, 0.004))):
        B(f"trect.{nm}", sz, loc, kit.plastic("#ffd23f", 0.6, "tape0"))
    # balloons on strings, bobbing
    ctx["balloons"] = []
    bcols = ["#ff6fa8", "#ffd23f", "#4db8ff", "#58d86a", "#b06af0", "#ff8a3d", "#ff6fa8", "#4db8ff"]
    anchors = [(tx - 0.9, ty - 0.4), (tx + 0.9, ty - 0.4), (tx - 0.9, ty + 0.4), (tx + 0.9, ty + 0.4), (tx - 5.2, ty - 1.0),
               (tx + 5.2, ty + 1.0), (tx - 1.0, ty + 5.6), (tx + 1.0, ty - 5.2)]
    for i, (x, y) in enumerate(anchors):
        z = 2.3 + (i % 3) * 0.35
        z0 = 0.8 if i < 4 else 0.0
        root = kit.empty(f"bal{i}", (x, y, z0))
        s = kit.sphere(f"bal{i}.b", 0.28, (0, 0, z - z0), kit.plastic(bcols[i], 0.25, f"balloon{i}"), root, seg=14)
        s.scale = (1, 1, 1.25)
        kit.cyl(f"bal{i}.s", 0.004, z - z0 - 0.3, (0, 0, (z - z0 - 0.3) / 2), M["dark"], root, n=4)
        ctx["balloons"].append((root, i, z0))
    # bunting on the hedge: little coloured flags
    for i in range(12):
        B(f"flag{i}", (0.18, 0.02, 0.24), (6.3, 1.0 + i * 0.95, 1.55), kit.plastic(bcols[i % 8], 0.6, f"flagc{i % 8}"), rot=(0, 0, 0.0))
    kit.light("yard key", "AREA", (tx, ty, 9.0), 1400.0, "#fff4e6", size=12.0)
    kit.light("yard side", "POINT", (8.5, 5.0, 3.0), 300.0, "#fff4e6", size=1.0)
    # glitter jar
    jar = kit.empty("jar", (0, 0, -40))
    kit.cyl("jar.body", 0.05, 0.12, (0, 0, 0), kit.plastic("#cfeaff", 0.2, "jar glass"), jar, n=14)
    kit.cyl("jar.lid", 0.052, 0.03, (0, 0, 0.075), kit.plastic("#ff6fa8", 0.4), jar, n=14)
    ctx["jar"] = jar
    rng = random.Random(12)
    ctx["jar_flakes"] = []
    for i in range(36):
        o = B(f"jf{i}", (0.015, 0.015, 0.008), (0, 0, -40), kit.emit(["#ffe14d", "#ff7fb2", "#7fe0ff", "#ffffff"][i % 4], 2.0, f"jfm{i % 4}"))
        ctx["jar_flakes"].append((o, rng.random() * 1.5, rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2)))


# ------------------------------------------------------------------------------------------------ the small rooms
def build_garden(kit, M, ctx):
    B = kit.box
    kit.plane("garden", (40, 30), (G0, 6, -0.01), M["grass"])
    B("g.hedge", (16, 0.9, 1.5), (G0, 11.5, 0.75), M["leaf"], bevel=0.25)
    B("g.hedge2", (0.9, 12, 1.5), (G0 - 8, 5.5, 0.75), M["leaf"], bevel=0.25)
    B("g.hedge3", (0.9, 12, 1.5), (G0 + 8, 5.5, 0.75), M["leaf"], bevel=0.25)
    for i, x in enumerate((G0 - 2.2, G0 + 2.4)):
        B(f"g.tbl{i}", (1.8, 0.9, 0.75), (x, 8.5, 0.375), kit.plastic("#fff8ee", 0.7, "g cloth"), bevel=0.03)
        for k in range(4):
            kit.cyl(f"g.cup{i}{k}", 0.05, 0.1, (x - 0.6 + k * 0.4, 8.5, 0.8), kit.plastic(["#ff9fc9", "#ffd23f", "#4db8ff", "#58d86a"][k], 0.5), n=10)
    for i in range(9):
        B(f"g.flag{i}", (0.2, 0.02, 0.26), (G0 - 7 + i * 1.75, 11.0, 2.4 - 0.2 * math.sin(i * 0.7)), kit.plastic(["#ff6fa8", "#ffd23f", "#4db8ff"][i % 3], 0.6, f"gf{i % 3}"))
    # the tall white wedding cake (carried by Lund): four tiers, pearls, two toppers
    cake = kit.empty("wcake", (0, 0, -40))
    wc = kit.plastic("#fffdf8", 0.45, "wedding white")
    for i, (r, h) in enumerate(((0.32, 0.2), (0.26, 0.2), (0.2, 0.2), (0.14, 0.18))):
        kit.cyl(f"wc{i}", r, h, (0, 0, 0.1 + i * 0.2), wc, cake, n=20)
        kit.cyl(f"wc{i}.r", r + 0.012, 0.03, (0, 0, 0.19 + i * 0.2), kit.plastic("#ffb3d4", 0.4, "wc pink"), cake, n=20)
    kit.sphere("wc.top1", 0.04, (-0.03, 0, 0.9), kit.plastic("#ff6fa8", 0.4), cake, seg=8)
    kit.sphere("wc.top2", 0.04, (0.03, 0, 0.9), kit.plastic("#4db8ff", 0.4), cake, seg=8)
    ctx["wcake"] = cake
    kit.light("garden key", "AREA", (G0, 5.0, 9.0), 1100.0, "#fff4e6", size=12.0)


def build_kitchen(kit, M, ctx):
    B = kit.box
    yel = kit.plastic("#ffe9a8", 0.8, "kitchen wall")
    B("k.floor", (9.0, 6.0, 0.2), (K0, 2.5, -0.1), kit.checker("#ffffff", "#ffd9e8", 2.0, "kitchen tile", 0.4))
    B("k.back", (9.0, 0.3, 3.4), (K0, 5.15, 1.7), yel)
    B("k.left", (0.3, 6.0, 3.4), (K0 - 4.5, 2.5, 1.7), yel)
    B("k.right", (0.3, 6.0, 3.4), (K0 + 4.5, 2.5, 1.7), yel)
    for i, x in enumerate((-3.2, -2.6, -2.0)):
        kit.prop("kitchen_cabinet1" if i != 1 else "kitchen_sink", (K0 + x, 4.7, 0), rot=0, height=0.95)
    kit.prop("kitchen_fridge", (K0 + 3.6, 4.6, 0), rot=0, height=1.9)
    # the island and the toaster
    B("k.island", (2.4, 0.9, 0.95), (K0, 2.6, 0.475), M["pista"], bevel=0.02)
    B("k.island.top", (2.5, 1.0, 0.05), (K0, 2.6, 0.975), M["cream"], bevel=0.015)
    B("toaster", (0.5, 0.26, 0.22), (K0, 2.6, 1.12), kit.plastic("#ff8fc7", 0.35, "toaster pink"), bevel=0.03)
    B("toaster.slot", (0.34, 0.07, 0.02), (K0, 2.6, 1.23), M["dark"])
    ctx["toast"] = []
    for i, dx in enumerate((-0.09, 0.09)):
        b = B(f"toast{i}", (0.12, 0.03, 0.16), (K0 + dx, 2.6, 1.3), kit.plastic("#2a1d15", 0.8, "burnt toast"), bevel=0.01)
        g = B(f"toastg{i}", (0.12, 0.03, 0.16), (K0 + dx, 2.6, 1.3), kit.plastic("#e8b04a", 0.7, "golden toast"), bevel=0.01)
        ctx["toast"].append((b, g))
    ctx["puffs"] = []
    rng = random.Random(3)
    for i in range(7):
        o = kit.sphere(f"puff{i}", 0.12, (K0, 2.6, 1.4), kit.plastic("#b8b8c4", 0.9, "smoke"), seg=10)
        ctx["puffs"].append((o, rng.random(), rng.uniform(-0.15, 0.15), rng.uniform(-0.1, 0.1)))
    # the kitchen wall clock (face to -y) and a step stool
    ctx["kclock"] = make_clock(kit, M, "kitchen clock", (K0, 5.0, 2.4), -1, 0.4)
    B("stool", (0.5, 0.4, 0.45), (K0, 4.3, 0.225), M["blue"], bevel=0.03)
    kit.light("kitchen key", "AREA", (K0, 2.5, 3.4), 400.0, "#fff4e6", size=6.0)
    kit.light("kitchen face", "POINT", (K0, 0.8, 2.2), 70.0, "#fff0dc", size=0.8)
    # toast smoke is driven in animate


def build_bedroom(kit, M, ctx):
    B = kit.box
    lav = kit.plastic("#e5d9ff", 0.8, "bedroom wall")
    B("b.floor", (9.0, 6.0, 0.2), (BR, 2.5, -0.1), M["wood"])
    B("b.back", (9.0, 0.3, 3.4), (BR, 5.15, 1.7), lav)
    B("b.left", (0.3, 6.0, 3.4), (BR - 4.5, 2.5, 1.7), lav)
    B("b.right", (0.3, 6.0, 3.4), (BR + 4.5, 2.5, 1.7), lav)
    kit.prop("bed_single", (BR + 1.4, 3.5, 0), rot=0, tint="#ffd9e8")
    kit.prop("carpet_1", (BR + 1.0, 1.5, 0.01), rot=0, tint="#a8e07a")
    kit.prop("nightstand_1", (BR + 3.05, 4.5, 0), rot=0, height=0.55, tint="#e0b890")
    ac = (BR + 3.05, 4.3, 0.95)
    kit.cyl("alarm.body", 0.17, 0.09, ac, kit.plastic("#ff6fa8", 0.4, "alarm"), rot=(math.pi / 2, 0, 0), n=24)
    for s in (-1, 1):
        kit.sphere(f"alarm.bell{s}", 0.05, (ac[0] + s * 0.11, ac[1], ac[2] + 0.17), M["brass"], seg=10)
    cl = make_clock(kit, M, "alarm", (ac[0], ac[1] - 0.045, ac[2]), -1, 0.14)
    ctx["alarm"] = cl
    kit.light("bedroom key", "AREA", (BR, 2.5, 3.4), 400.0, "#fff4e6", size=6.0)
    kit.light("bedroom face", "POINT", (BR + 2.0, 0.8, 2.2), 70.0, "#fff0dc", size=0.8)


def build_nook(kit, M, ctx):
    B = kit.box
    wall = kit.plastic("#d9f2c4", 0.8, "nook wall")
    B("n.floor", (8.0, 6.0, 0.2), (NN, 2.5, -0.1), M["wood"])
    B("n.back", (8.0, 0.3, 3.4), (NN, 5.15, 1.7), wall)
    B("n.left", (0.3, 6.0, 3.4), (NN - 4.0, 2.5, 1.7), wall)
    B("n.right", (0.3, 6.0, 3.4), (NN + 4.0, 2.5, 1.7), wall)
    B("n.table", (2.4, 1.0, 0.06), (NN, 3.0, 0.78), M["white"], bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            B(f"n.leg{sx}{sy}", (0.06, 0.06, 0.78), (NN + sx * 1.1, 3.0 + sy * 0.4, 0.39), M["steel"])
    B("printer", (0.7, 0.5, 0.3), (NN - 0.7, 3.1, 0.96), kit.plastic("#e8edf5", 0.5, "printer"), bevel=0.03)
    B("printer.slot", (0.5, 0.05, 0.03), (NN - 0.7, 2.83, 1.05), M["dark"])
    B("printer.paper", (0.4, 0.3, 0.012), (NN - 0.7, 2.7, 1.05), M["white"])
    npm = img_material(kit, "paper", newspaper_image(), 0.7)
    for i in range(6):
        B(f"np{i}", (0.42, 0.55, 0.012), (NN + 0.5 + 0.012 * (i % 2), 3.0 + 0.02 * (i % 3), 0.84 + i * 0.013), kit.plastic("#f3ecd9", 0.8, "np base"), rot=(0, 0, 0.05 * (i % 3) - 0.04))
    img_plane(kit, "np.top", 0.42, 0.55, npm, (NN + 0.5, 3.0, 0.925), None, right=(1, 0, 0), up=(0, 1, 0))
    kit.light("nook key", "AREA", (NN, 2.5, 3.4), 400.0, "#fff4e6", size=6.0)
    kit.light("nook warm", "POINT", (NN - 0.7, 2.4, 1.6), 40.0, "#ffb070", size=0.5)


# ------------------------------------------------------------------------------------------------ the rule meter
def build_tag(kit, ctx):
    cam = kit.OBJ["cam"]
    piv = kit.empty("tag.pivot", (0, 0, -0.4), cam)
    pm = img_material(kit, "tag_page", page_image(), emit=1.0)
    page = img_plane(kit, "tag.page", 1.0, 1.0, pm, (0, 0, 0), piv)
    badges = {}
    for n in range(1, 6):
        bm = img_material(kit, f"tag_badge{n}", badge_image(n), emit=1.0)
        badges[n] = img_plane(kit, f"tag.badge{n}", 1.0, 1.0, bm, (0, 0, 0.002), piv)
    allp = [page] + list(badges.values())
    for o in allp:
        no_shadow(o)
        try:
            o.visible_glossy = False
            o.visible_diffuse = False
            o.visible_transmission = False
        except Exception:
            pass
    ctx["tag"] = (piv, page, badges)


def lens_at(story, tl, t):
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next(s for s in story["shots"] if s["id"] == shot["id"])
    keys = spec["cam"]
    if len(keys) == 1:
        return keys[0][3]
    u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
    return lerp(keys[0][3], keys[1][3], ss(u))


# ------------------------------------------------------------------------------------------------ the cast's extras
def _hg(name):
    return bpy.data.objects[f"{name}.headg"]


def dress_mom(kit, name):
    c = rig.CHARS[name]
    arm = c.P["arm-1"]
    # a big watch on the wrist: a band all round and a gold face with a cream dial on top (front side of the raised arm)
    kit.box(f"{name}.wband", (1.1, 1.1, 0.34), (0, 0, -1.5), kit.plastic("#6a4a3a", 0.6, "watch band"), arm, bevel=0.04)
    kit.cyl(f"{name}.wcase", 0.46, 0.14, (0, -0.58, -1.5), kit.plastic("#f4c542", 0.3, "watch gold"), arm, rot=(math.pi / 2, 0, 0), n=20)
    kit.cyl(f"{name}.wdial", 0.36, 0.05, (0, -0.68, -1.5), kit.plastic("#fffaf0", 0.4, "watch dial"), arm, rot=(math.pi / 2, 0, 0), n=20)
    kit.box(f"{name}.wh1", (0.05, 0.03, 0.26), (0, -0.72, -1.4), kit.plastic("#23305e", 0.5, "ink"), arm)
    kit.box(f"{name}.wh2", (0.2, 0.03, 0.05), (0.08, -0.72, -1.5), kit.plastic("#23305e", 0.5, "ink"), arm)


def dress_pearl(kit, name, ctx):
    c = rig.CHARS[name]
    hip = c.upper
    mail = kit.plastic("#2f6fd6", 0.6, "mailbag")
    kit.box(f"{name}.bag", (1.3, 0.6, 1.0), (1.25, -0.2, 0.6), mail, hip, bevel=0.08)
    kit.box(f"{name}.flap", (1.3, 0.64, 0.3), (1.25, -0.2, 1.05), kit.plastic("#fff3dc", 0.6, "bag flap"), hip, bevel=0.05)
    kit.box(f"{name}.strap", (0.16, 1.08, 2.0), (0.2, 0.0, 1.0), mail, hip, rot=(0, 0.6, 0), bevel=0.03)
    # glitter specks on her hands: they appear with the "glit" cue (more each today)
    rng = random.Random(21)
    ctx["specks"] = []
    cols = ["#ffe14d", "#ff7fb2", "#7fe0ff", "#ffffff"]
    for i in range(70):
        arm = c.P["arm-1" if i % 2 == 0 else "arm1"]
        face = rng.choice(["x+", "x-", "y-", "y+", "z-"])
        u, v = rng.uniform(-0.45, 0.45), rng.uniform(-1.95, -1.15)
        pos = {"x+": (0.51, u, v), "x-": (-0.51, u, v), "y-": (u, -0.51, v), "y+": (u, 0.51, v), "z-": (u, rng.uniform(-0.45, 0.45), -2.0)}[face]
        o = kit.box(f"{name}.speck{i}", (0.07, 0.07, 0.07), pos, kit.emit(cols[i % 4], 2.5, f"sp{i % 4}"), arm)
        ctx["specks"].append(o)


def dress_me(kit, name):
    """Dark curls: a cluster of little round locks on the mop, so my hair reads as curls and stays black."""
    hg = _hg(name)
    hair = kit.plastic("#1a1512", 0.65)
    top = faces.HEAD_H / 2
    k = 0
    for i, (cx, cy) in enumerate(((-0.42, -0.35), (0.0, -0.4), (0.42, -0.35), (-0.45, 0.05), (0.0, 0.0), (0.45, 0.05), (-0.4, 0.4), (0.0, 0.42), (0.4, 0.4))):
        kit.sphere(f"{name}.curl{k}", 0.24, (cx, cy, top + 0.4), hair, hg, seg=10)
        k += 1
    for sx in (-1, 1):
        for j, (cy, cz) in enumerate(((-0.15, top - 0.2), (0.25, top - 0.5), (0.3, top - 0.05))):
            kit.sphere(f"{name}.curls{sx}{j}", 0.2, (sx * (faces.HEAD_R + 0.08), cy, cz), hair, hg, seg=10)


def dress_oka(kit, name):
    hg = _hg(name)
    kit.box(f"{name}.beard", (0.95, 0.36, 0.5), (0, -0.5, -0.36), kit.plastic("#f2f2f2", 0.85, "beard"), hg, bevel=0.1)
    kit.box(f"{name}.stache", (0.7, 0.14, 0.14), (0, -0.62, -0.12), kit.plastic("#f2f2f2", 0.85, "beard"), hg, bevel=0.05)


def dress_lund(kit, name, ctx):
    c = rig.CHARS[name]
    arm = c.P["arm-1"]
    sw = kit.empty("stopwatch", (0, 0, -40))
    kit.cyl("sw.body", 0.07, 0.03, (0, 0, 0), kit.plastic("#d8dde6", 0.25, "stopwatch"), sw, rot=(math.pi / 2, 0, 0), n=20)
    kit.cyl("sw.face", 0.055, 0.01, (0, -0.02, 0), kit.plastic("#fffaf0", 0.4), sw, rot=(math.pi / 2, 0, 0), n=20)
    kit.box("sw.button", (0.02, 0.02, 0.03), (0, 0, 0.085), kit.plastic("#d8dde6", 0.25, "stopwatch"), sw)
    ctx["stopw"] = sw


def dress_extra(kit, name, ctx):
    pen = kit.box("pen", (0.2, 0.012, 0.012), (0, 0, -40), kit.plastic("#4db8ff", 0.4, "pen"))
    ctx["pen"] = pen
    clip = kit.empty("clip.root", (0, 0, -40))
    kit.box("clip.board", (0.32, 0.03, 0.42), (0, 0, 0), kit.plastic("#b07a4a", 0.6, "clipboard"), clip, bevel=0.01)
    kit.box("clip.clip", (0.12, 0.04, 0.05), (0, -0.002, 0.2), kit.plastic("#d8dde6", 0.25, "clip steel"), clip)
    cm = img_material(kit, "clip_paper", clip_image(), 0.7)
    pl = img_plane(kit, "clip.paper", 0.28, 0.37, cm, (0, -0.024, -0.01), clip, right=(1, 0, 0), up=(0, 0, 1))
    ctx["clip"] = clip


# ------------------------------------------------------------------------------------------------ build / animate
def build(kit, story, tl):
    ctx = {"inited": False}
    M = materials(kit)
    ctx["M"] = M
    build_bakery(kit, M, ctx)
    build_street(kit, M, ctx)
    build_yard(kit, M, ctx)
    build_garden(kit, M, ctx)
    build_kitchen(kit, M, ctx)
    build_bedroom(kit, M, ctx)
    build_nook(kit, M, ctx)
    build_tag(kit, ctx)
    # letters for Pearl's trip: six envelopes
    ctx["letters"] = []
    for i in range(6):
        ctx["letters"].append(kit.box(f"letter{i}", (0.16, 0.11, 0.012), (0, 0, -40), kit.plastic(["#ffffff", "#fff3dc", "#ffd9e8", "#d9f2ff"][i % 4], 0.6, f"env{i % 4}"), bevel=0.003))
    return ctx


def hand_pos(name, side=0, local=(0, -0.1, -1.72)):
    c = rig.CHARS[name]
    arm = c.P["arm-1" if side == 0 else "arm1"]
    return arm.matrix_world @ V(local)


def animate(kit, story, tl, t, ctx):
    bpy.context.view_layer.update()
    M = ctx["M"]
    if not ctx["inited"]:
        ctx["inited"] = True
        if "mom" in rig.CHARS:
            dress_mom(kit, "mom")
        if "pearl" in rig.CHARS:
            dress_pearl(kit, "pearl", ctx)
        if "oka" in rig.CHARS:
            dress_oka(kit, "oka")
        if "me" in rig.CHARS:
            dress_me(kit, "me")
        if "lund" in rig.CHARS:
            dress_lund(kit, "lund", ctx)
        dress_extra(kit, "mom", ctx)
        bpy.context.view_layer.update()
    # ---- the clocks (hands ease between cues; the second hand ticks)
    v = eased(tl, "clock", t, default=[9, 2])
    sec = (math.floor(t) + ss((t % 1.0) * 6.0)) * 1.0
    set_hands(ctx["clock"], v[0], v[1], sec)
    cc_ = latest(tl, "clock", t)
    tgt = tuple(cc_["v"]) if cc_ else (9, 2)
    for k_, o_ in ctx["dig"].items():
        o_.hide_render = k_ != tgt
    kv = eased(tl, "kclock", t, default=[9, 30])
    set_hands(ctx["kclock"], kv[0], kv[1], sec)
    av = eased(tl, "alarm", t, default=[7, 0])
    set_hands(ctx["alarm"], av[0], av[1], sec)
    # ---- doors: the front door stands open into the shop; the back door swings on its cues
    ctx["door"].rotation_euler = (0, 0, math.radians(80))
    bd = eased(tl, "bdoor", t, default=[0])
    ctx["bdoor"].rotation_euler = (0, 0, math.radians(-bd[0]))
    # ---- the bell
    bs = since(tl, "bell", t)
    ang = 0.0
    if bs is not None and bs < 1.2:
        ang = 0.5 * math.exp(-bs * 3.2) * math.sin(bs * 24.0)
    ctx["bell"].rotation_euler = (ang, 0, 0)
    # ---- the rain streaks on the window
    rc = latest(tl, "rain", t)
    ron = bool(rc and rc.get("on"))
    ramp = ss((t - rc["t"]) / 0.5) if (rc and ron) else 0.0
    for o, v_, ph, ln in ctx["streaks"]:
        if ramp <= 0.001:
            o.hide_render = True
            continue
        o.hide_render = False
        z = 2.9 - ((t * v_ * 0.45 + ph) % 2.1)
        o.location = (o.location.x, -0.1, z)
        o.scale = (1.0, 1.0, max(0.05, ramp))
    # ---- the candle and its flame
    can = on_at(tl, "candle", t, False)
    ctx["candle"].hide_render = not can
    for c in ctx["candle"].children_recursive:
        c.hide_render = not can
    if can:
        ctx["flame"].scale = (1 + 0.1 * math.sin(t * 17), 1 + 0.18 * math.sin(t * 13), 1.3 + 0.2 * math.sin(t * 11))
    # ---- the muffin that goes into the bag
    mp = track(tl, "muff", t)
    ctx["muffin"].location = tuple(mp) if mp else (-0.6, 4.3, 1.07)
    # ---- Mom's cup, tipping, and the spill
    cc = latest(tl, "cup", t)
    cup = ctx["cup"]
    if cc and cc.get("mode") == "hand" and "mom" in rig.CHARS and not rig.CHARS["mom"].root.hide_render:
        tilts = [c for c in cues_of(tl, "cup") if c["t"] <= t + 1e-9]
        nxt = [c for c in cues_of(tl, "cup") if c["t"] > t]
        tilt = tilts[-1].get("tilt", 0.0)
        if nxt and nxt[0].get("mode") == "hand":
            u = ss((t - tilts[-1]["t"]) / max(1e-6, nxt[0]["t"] - tilts[-1]["t"]))
            tilt = lerp(tilt, nxt[0].get("tilt", 0.0), u)
        hp = hand_pos("mom", 0, (0, -0.1, -1.75))
        cup.location = (hp.x, hp.y, hp.z + 0.04)
        cup.rotation_euler = (math.radians(tilt), 0, 0)
    else:
        cup.location = (0, 0, -40)
    sp = latest(tl, "spill", t)
    soff = latest(tl, "spill_off", t)
    shown = bool(sp and not (soff and soff["t"] > sp["t"]))
    if shown:
        u = ss((t - sp["t"]) / 0.25)
        ctx["spill"].location = (-0.3, 3.98, 1.075)
        ctx["spill"].scale = (max(0.05, u), max(0.05, u), 1)
    else:
        ctx["spill"].location = (0, 0, -40)
    # ---- the pour (hanging in the air) from the pot in n1's hands
    if on_at(tl, "pour", t, False) and "n1" in rig.CHARS:
        hp = hand_pos("n1", 0, (0, -0.1, -1.75))
        ctx["pot"].location = (hp.x, hp.y - 0.04, hp.z + 0.04)
        ctx["pot"].rotation_euler = (math.radians(-55), 0, 0)
        sx, sy, sz = hp.x, hp.y - 0.2, hp.z - 0.02
        seg(ctx["stream"], (sx, sy, sz), (sx, sy, 1.05), r=1.0)
    else:
        ctx["pot"].location = (0, 0, -40)
        ctx["stream"].location = (0, 0, -40)
    # ---- Pearl's letters: they fan out of the bag and settle on the mat
    lc = latest(tl, "letters", t)
    off = latest(tl, "letters_off", t)
    for i, o in enumerate(ctx["letters"]):
        if lc is None or (off and off["t"] > lc["t"]) or "pearl" not in rig.CHARS:
            o.location = (0, 0, -40)
            continue
        s = t - lc["t"]
        rng = random.Random(40 + i)
        ang = rng.uniform(-1.2, 1.2)
        dx, dy = math.sin(ang) * rng.uniform(0.4, 1.0), rng.uniform(0.3, 1.0)
        x0, y0, z0 = -2.45, 0.7, 1.15
        k = min(1.0, s / 0.8)
        z = max(0.08 + 0.012 * i, z0 + 1.6 * s - 4.4 * s * s)
        o.location = (x0 + dx * k, y0 + dy * k, z)
        o.rotation_euler = (3.0 * k * (1 if i % 2 else -1), 2.0 * k, ang * k * 3)
    # ---- Pearl's glitter count
    gl = latest(tl, "glit", t)
    n = gl["n"] if gl else 0
    counts = {0: 0, 1: 6, 2: 18, 3: 42, 4: 70}
    for i, o in enumerate(ctx.get("specks", [])):
        o.hide_render = i >= counts[n]
    # ---- the hose, the spray and the rainbow
    hose = on_at(tl, "hose", t, False) and "oka" in rig.CHARS and not rig.CHARS["oka"].root.hide_render
    if hose:
        # the hand that holds the nozzle is arm1 (his arms are out toward the window)
        hp = hand_pos("oka", 1, (0, -0.1, -1.9))
        N = (hp.x, hp.y, hp.z)
        pts = [N, (N[0] + 0.5, N[1] - 0.2, N[2] - 0.25), (3.95, -0.75, 3.0), (4.15, -1.1, 0.12), (3.0, -2.0, 0.05), (1.5, -2.2, 0.05)]
        for i, o in enumerate(ctx["hose"]):
            seg(o, pts[i], pts[i + 1], r=1.0)
        ctx["nozzle"].location = (N[0], N[1], N[2] - 0.02)
        ctx["nozzle"].rotation_euler = (0, 0, 0)
        hc = latest(tl, "hose", t)
        k = ss((t - hc["t"]) / 0.3)
        for o, vel, ph, fan, jit in ctx["drops"]:
            f = (t * vel + ph) % 3.4
            z = N[2] - f
            if z < 0.9 or k <= 0.01:
                o.location = (0, 0, -40)
                continue
            o.location = (N[0] + fan * 0.16 * f, -0.5 + jit, z)
            o.scale = (1, 1, 0.6 + 0.4 * k)
        ctx["rainbow"].location = (N[0] - 0.4, -0.85, N[2] - 0.55)
        rb = on_at(tl, "rainbow", t, False)
    else:
        for o in ctx["hose"]:
            o.location = (0, 0, -40)
        ctx["nozzle"].location = (0, 0, -40)
        for o, *_ in ctx["drops"]:
            o.location = (0, 0, -40)
        rb = False
    hide_tree(ctx["rainbow"], not rb)
    # ---- wet hair: my hair goes dark blue-grey and glossy
    hm = bpy.data.materials.get("plastic #1a1512 0.65")
    if hm is not None:
        wet = on_at(tl, "wet", t, False)
        bsdf = next((n for n in hm.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*lin("#120e0c" if wet else "#1a1512"), 1)
            bsdf.inputs["Roughness"].default_value = 0.3 if wet else 0.65
    # ---- the wedding cake in Lund's hands
    wc = latest(tl, "wcake", t)
    cake = ctx["wcake"]
    if wc and wc.get("mode") == "hand" and "lund" in rig.CHARS and not rig.CHARS["lund"].root.hide_render:
        h0, h1 = hand_pos("lund", 0), hand_pos("lund", 1)
        mid = (h0 + h1) / 2
        tilt = eased(tl, "wtilt", t, default=[0])[0]
        cake.location = (mid.x, mid.y, mid.z - 0.05)
        yaw = rig.CHARS["lund"].root.rotation_euler[2]
        cake.rotation_euler = (math.radians(tilt) * math.cos(yaw), math.radians(tilt) * math.sin(yaw), yaw)
    else:
        cake.location = (0, 0, -40)
    # ---- the toaster: burnt or golden toast, and the smoke
    tn = latest(tl, "toast", t)
    burnt = not tn or tn.get("n") == "burnt"
    for b, g in ctx["toast"]:
        b.hide_render = not burnt
        g.hide_render = burnt
    pf = latest(tl, "puff", t)
    pon = bool(pf and pf.get("on"))
    for o, ph, dx, dy in ctx["puffs"]:
        if not pon:
            o.location = (0, 0, -40)
            continue
        s = (t - pf["t"]) * 0.6 + ph
        s = s % 1.6
        o.location = (K0 + dx + 0.1 * math.sin(s * 4 + ph * 6), 2.6 + dy, 1.4 + s * 0.8)
        r = 0.5 + 1.8 * s
        o.scale = (r, r, r)
    # ---- balloons bob; the glitter jar
    for root, i, z0 in ctx["balloons"]:
        root.location = (root.location.x, root.location.y, z0 + 0.05 * math.sin(t * 1.6 + i * 1.3))
    jon = on_at(tl, "jar", t, False) and "pearl" in rig.CHARS
    if jon:
        hp = hand_pos("pearl", 0, (0, -0.1, -1.8))
        ctx["jar"].location = (hp.x, hp.y, hp.z + 0.04)
        ctx["jar"].rotation_euler = (math.radians(130 + 18 * math.sin(t * 9.0)), 0, 0)
        jc = latest(tl, "jar", t)
        for o, ph, dx, dy in ctx["jar_flakes"]:
            f = ((t - jc["t"]) * 1.1 + ph) % 1.5
            o.location = (hp.x + dx * f, hp.y - 0.1 + dy * f, hp.z + 0.02 - f * 0.55)
        for i, o in enumerate(ctx["glitter_cake"]):
            o.hide_render = (t - jc["t"]) < 0.2 + i * 0.015
    else:
        ctx["jar"].location = (0, 0, -40)
        for o, *_ in ctx["jar_flakes"]:
            o.location = (0, 0, -40)
        done = latest(tl, "jar", t)
        for o in ctx["glitter_cake"]:
            o.hide_render = not (done and not done.get("on"))
    # ---- the clipboard, the stopwatch and the pen
    cl = ctx["clip"]
    csc = eased(tl, "clipscale", t, default=[1.5])
    csc = csc[0] if isinstance(csc, list) else csc
    cl.scale = (csc, csc, csc)
    cm = latest(tl, "clip", t)
    if cm and cm.get("mode") in ("hand", "chest") and "mom" in rig.CHARS and not rig.CHARS["mom"].root.hide_render:
        up = rig.CHARS["mom"].upper
        local = (0.0, -0.95, 1.05) if cm["mode"] == "hand" else (0.0, -0.66, 0.62)
        cl.location = up.matrix_world @ V(local)
        e = up.matrix_world.to_euler()
        # paper side faces her when held out (so we see it over her shoulder); chest: board's back out
        cl.rotation_euler = e
        if cm["mode"] == "hand":
            cl.rotation_euler = (e[0] + 0.0, e[1], e[2])
    else:
        cl.location = (0, 0, -40)
    sw = ctx["stopw"]
    if on_at(tl, "stopw", t, False) and "lund" in rig.CHARS and not rig.CHARS["lund"].root.hide_render:
        hp = hand_pos("lund", 0, (0, -0.1, -1.8))
        sw.location = (hp.x, hp.y - 0.05, hp.z + 0.05)
    else:
        sw.location = (0, 0, -40)
    pn = ctx["pen"]
    if on_at(tl, "pen", t, False) and "mom" in rig.CHARS:
        hg = _hg("mom")
        wp = hg.matrix_world @ V((0.0, -0.72, -0.28))
        pn.location = (wp.x, wp.y, wp.z)
        pn.rotation_euler = hg.matrix_world.to_euler()
    else:
        pn.location = (0, 0, -40)
    # ---- my face in the cake case glass, the yard's second ladder
    ctx["ghost"].hide_render = not on_at(tl, "ghost", t, False)
    hide_tree(ctx["ladder2"], not on_at(tl, "ladder2", t, False))
    # ---- the coffee splash: blobs thrown up and out of the spill, falling back in about 0.7 s
    spc = latest(tl, "spill", t)
    ss_ = None if spc is None else t - spc["t"]
    soff2 = latest(tl, "spill_off", t)
    live = ss_ is not None and 0 <= ss_ < 0.8 and not (soff2 and soff2["t"] > spc["t"])
    for i, o in enumerate(ctx["splash"]):
        if not live:
            o.location = (0, 0, -40)
            continue
        a = i * 2.4 + 0.5
        vx, vy, vz = 0.55 * math.cos(a) * (0.5 + 0.5 * ((i * 7) % 5) / 4), 0.35 * math.sin(a), 1.9 + 0.5 * ((i * 3) % 4)
        o.location = (-0.3 + vx * ss_, 3.98 + vy * ss_, 1.1 + vz * ss_ - 4.4 * ss_ * ss_ + 0.02)
        o.scale = (1, 1, 1.4)
    # ---- the rule meter: the calendar page in the top-left corner of every shot, parented to the camera
    piv, page, badges = ctx["tag"]
    lens = lens_at(story, tl, t)
    dist = 0.4
    half_h = dist * 12.0 / lens
    half_w = half_h * 9 / 16
    bc = latest(tl, "badge", t)
    n = bc["n"] if bc else 5
    pop = 1.0
    if bc:
        s = t - bc["t"]
        if 0 <= s < 0.35 and bc["t"] > 0.05:
            pop = 1.0 + 0.32 * math.sin(math.pi * s / 0.35)
    big = eased(tl, "tagbig", t, key="v", default=0.0)
    big = big if not isinstance(big, list) else big[0]
    tw = 0.27 * 2 * half_w * (1 + 1.3 * big)
    th = tw * 440 / 360
    px0 = -half_w + 0.075 * 2 * half_w + tw / 2
    py0 = half_h - 0.085 * 2 * half_h - th / 2
    px = lerp(px0, 0.0, big)
    py = lerp(py0, half_h * 0.35, big)
    piv.location = (px, py, -dist)
    page.scale = (tw, th, 1)
    for k, o in badges.items():
        o.hide_render = k != n
        bw = tw * 0.46 * pop
        o.scale = (bw, bw, 1)
        o.location = (tw * 0.34, -th * 0.34, 0.002)
    return {}
