"""rule-three (batch 6, the Rulebook Keeper pilot): a bright hill town and its town hall, built from kit.py's parts.

THE RECURRING HOST LIVES HERE (and in stories/lore.md, "The Rulebook Keeper"). Later episodes copy these builders:
  dress_otis()     the Buhkeeper's ink-blue thumb on the rig (the look itself is the rig spec in make_story)
  build_book()     the door-sized red leather rulebook (open on the lectern, closed to carry, open on a table)
  build_stamp()    his brass stamp with the cherry-red knob (glued to his right hand by the "stamp" cue)
  build_lectern()  the one seamless block of pale old stone
  spread_image()   the book's pages: ink-blue numerals and glyphs, drawn here with PIL (no letters anywhere)
  build_tag()      the RULE METER: a cream torn-paper tag in the top-left corner of every shot, parented to the
                   camera, with the story's rule number. It flips to a new number on the "tag" cue.
Nothing in the set has letters: only numerals and our own glyphs.

Zones (metres): the hall's record room x -5..5, y 0..7.5 (front wall at y 0, the street runs from it toward -y);
DINER (200,0), PET SHOP (300,0), BRIDGE (400,0), MOM'S (500,0), OTIS'S KITCHEN (600,0).
Cues read here: tod, spread, clock, stamp, slip, slipface, ppage (mode pocket|hand|world), ppage_unfold, ppage_face,
door, book (mode open|carry|table), bookpath, plate, sleeve, tag.
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

S = rig.S
INK = "#2b4bd8"
CREAM = "#f4ecd8"
BRASS = "#d9a441"
BOOK_RED = "#c8202f"
MINT = "#bfe8d6"
LECT = (0.0, 5.15)
OT_Y = 6.05
TMP = Path(tempfile.mkdtemp(prefix="rule3"))


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


def lerp3(a, b, u):
    return tuple(lerp(x, y, u) for x, y in zip(a, b))


def cues_of(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def latest(tl, name, t):
    out = None
    for c in cues_of(tl, name):
        if c["t"] <= t + 1e-9:
            out = c
    return out


def track(tl, name, t, key="v"):
    """A vector track: between two consecutive cues of this name it eases from one value to the next."""
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


def basis(right, up):
    """A rotation whose local x is `right`, local y is `up`, local z (the plane normal) is right x up."""
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


def number(d, text, cx, y, h, color=INK):
    w = h * 0.5
    gap = h * 0.16
    total = len(text) * w + (len(text) - 1) * gap
    x = cx - total / 2
    for ch in text:
        digit(d, ch, x, y, w, h, color)
        x += w + gap


def glyph_row(d, x0, x1, y, rng, color=INK, size=34):
    x = x0
    while x < x1 - size:
        k = rng.random()
        s = size * rng.uniform(0.8, 1.15)
        if k < 0.3:
            d.ellipse((x, y, x + s * 0.8, y + s), outline=color, width=int(size * 0.2))
        elif k < 0.55:
            d.rounded_rectangle((x + s * 0.3, y - 2, x + s * 0.3 + size * 0.22, y + s + 2), radius=4, fill=color)
        elif k < 0.75:
            d.rounded_rectangle((x, y + s * 0.4, x + s * 0.95, y + s * 0.4 + size * 0.22), radius=4, fill=color)
            d.ellipse((x + s * 0.3, y, x + s * 0.65, y + s * 0.3), fill=color)
        elif k < 0.9:
            d.arc((x, y, x + s, y + s * 1.4), 200, 340, fill=color, width=int(size * 0.22))
            d.ellipse((x + s * 0.4, y + s * 0.8, x + s * 0.6, y + s), fill=color)
        else:
            for j in range(3):
                d.ellipse((x + j * s * 0.34, y + s * 0.3, x + j * s * 0.34 + size * 0.2, y + s * 0.3 + size * 0.2), fill=color)
        x += s * 1.35


def glyph_rows(d, x0, x1, y0, n, seed, color=INK, gap=88):
    rng = random.Random(seed)
    for i in range(n):
        glyph_row(d, x0, x1 - rng.randint(0, 150), y0 + i * gap, rng, color)


def bridge_glyph(d, cx, cy, color=INK):
    d.arc((cx - 60, cy - 40, cx + 60, cy + 80), 180, 360, fill=color, width=14)
    d.rounded_rectangle((cx - 78, cy + 20, cx + 78, cy + 32), radius=5, fill=color)
    for k in range(3):
        d.arc((cx - 70 + k * 50, cy + 44, cx - 30 + k * 50, cy + 70), 20, 160, fill=color, width=7)


def cake_glyph(d, cx, cy, color=INK):
    d.polygon([(cx - 60, cy + 40), (cx + 60, cy + 40), (cx + 60, cy - 10), (cx - 60, cy - 50)], outline=color, width=10)
    d.rounded_rectangle((cx - 60, cy + 40, cx + 60, cy + 54), radius=5, fill=color)
    d.ellipse((cx - 14, cy - 76, cx + 14, cy - 48), fill=color)


def torn_profile(seed, n, a, b, amp=14):
    rng = random.Random(seed)
    return [rng.uniform(-amp, amp) for _ in range(n)]


def spread_image(name):
    """The open book, 1600 x 1100 px for 1.6 x 1.1 m (the gutter at x = 800)."""
    W, H = 1600, 1100
    im = Image.new("RGB", (W, H), "#e4d9bc")
    d = ImageDraw.Draw(im)
    for i in range(70):   # the page curve toward the gutter
        u = i / 70
        c = int(228 - 38 * (1 - u) ** 2)
        d.line((800 - i, 0, 800 - i, H), fill=(c, int(219 - 40 * (1 - u) ** 2), int(188 - 52 * (1 - u) ** 2)))
        d.line((800 + i, 0, 800 + i, H), fill=(c, int(219 - 40 * (1 - u) ** 2), int(188 - 52 * (1 - u) ** 2)))
    pages = {"stub": ("2", "5", 11), "fresh": ("5112", "5113", 12), "last": ("5111", "5112", 13),
             "old": ("26", "27", 14), "cake": ("5113", "5114", 15)}
    ln, rn, seed = pages[name]
    ink = "#3a5be0" if name == "fresh" else INK
    number(d, ln, 460, 90, 190, ink)
    number(d, rn, 1130, 90, 190, ink)
    if name == "stub":
        glyph_rows(d, 100, 640, 360, 7, 21)
    else:
        glyph_rows(d, 90, 700, 360, 7, seed)
    glyph_rows(d, 900, 1500, 360, 7, seed + 40)
    if name == "last":
        bridge_glyph(d, 1100, 910)
    if name == "fresh":   # the wet ink: a soft shine on the top row
        for k in range(8):
            d.line((920 + k * 70, 352, 960 + k * 70, 352), fill="#9fb4ff", width=4)
    if name == "cake":
        cake_glyph(d, 1100, 900)
    if name == "stub":
        # the stub: where leaf 3 and 4 were torn out. A ragged strip at the gutter, a dark gap, a thumbprint.
        prof = torn_profile(3, 52, 0, 0, 14)
        pts = [(738 + prof[i], 20 + i * 20.8) for i in range(52)]
        d.rectangle((706, 0, 760, H), fill="#a79a78")          # the gap: the edges of the leaves left in the book
        for k in range(9):
            d.line((708 + k * 6, 0, 708 + k * 6, H), fill="#8f8362", width=2)
        d.polygon([(738, 0)] + [(738 + prof[i] * 1.0, 20 + i * 20.8) for i in range(52)] + [(738, H), (800, H), (800, 0)], fill="#eadfc0")
        d.polygon([(700, 0), (738, 0)] + [(738 + prof[i] * 1.0, 20 + i * 20.8) for i in range(52)] + [(738, H), (700, H)], fill="#a79a78")
        d.rectangle((700, 0, 706, H), fill="#f4ecd8")
        for i in range(0, 51, 2):   # pale paper fibres along the tear
            d.line((pts[i][0] - 4, pts[i][1], pts[i][0] + 6, pts[i + 1][1]), fill="#fbf6e6", width=3)
        # the thumbprint on the torn edge
        tx, ty = 770, 560
        d.ellipse((tx - 52, ty - 68, tx + 52, ty + 68), fill=INK)
        for k in range(1, 6):
            d.ellipse((tx - 52 + k * 8, ty - 68 + k * 10, tx + 52 - k * 8, ty + 68 - k * 10), outline="#7d93f0", width=3)
        d.ellipse((tx - 10, ty - 16, tx + 10, ty + 16), fill=INK)
    return im


def leaf_shape(W, H, seed_right=3, top_ragged=True):
    """The torn-out leaf's outline mask: the right edge is the stub's tear, mirrored; the top is torn too."""
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    prof = torn_profile(seed_right, 52, 0, 0, 14)
    right = [(W - 24 - prof[i] * 0.9, 20 + i * (H - 40) / 51) for i in range(52)]
    rng = random.Random(8)
    top = [(30 + i * (W - 60) / 24, (46 if top_ragged else 6) + (rng.uniform(-18, 18) if top_ragged else 0)) for i in range(25)]
    poly = top + right[:] + [(30, H - 8)]
    d.polygon(poly, fill=255)
    return m


def page_image(face):
    W, H = 680, 920
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    base = Image.new("RGB", (W, H), "#f2e8cc" if face == "front" else "#6f6648")   # the back sits under the lamp: darker paper so it doesn't clip
    d = ImageDraw.Draw(base)
    if face == "front":
        number(d, "3", 150, 6, 260)          # the torn top cuts through the numeral: half a 3
        glyph_rows(d, 70, 600, 340, 6, 31, gap=88)
    else:
        number(d, "4", 150, 70, 250)
        glyph_rows(d, 70, 600, 380, 5, 77, gap=88)
    mask = leaf_shape(W, H)
    im.paste(base, (0, 0), mask)
    return im


def slip_image(face):
    W, H = 420, 560
    im = Image.new("RGB", (W, H), "#f7f0dc")
    d = ImageDraw.Draw(im)
    d.line((0, H // 2, W, H // 2), fill="#e3d8b8", width=3)
    if face == "three":
        pts1 = [(120, 140), (210, 105), (300, 150), (270, 215), (190, 250)]
        pts2 = [(190, 250), (290, 290), (320, 380), (250, 450), (130, 440)]
        d.line(pts1 + pts2[1:], fill="#55555e", width=26, joint="curve")
        for p in pts1 + pts2:
            d.ellipse((p[0] - 13, p[1] - 13, p[0] + 13, p[1] + 13), fill="#55555e")
    return im


def photo_image():
    W, H = 480, 600
    im = Image.new("RGB", (W, H), "#cfe6f5")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 470, W, H), fill="#b69be0")
    d.rounded_rectangle((110, 130, 370, 440), radius=70, fill="#f0c6a4")
    d.rounded_rectangle((150, 30, 330, 150), radius=50, fill="#c7cbd6")
    d.ellipse((190, 6, 290, 80), fill="#c7cbd6")
    d.ellipse((160, 270, 215, 340), fill="#f4a8a0")
    d.ellipse((265, 270, 320, 340), fill="#f4a8a0")
    for x in (190, 290):
        d.ellipse((x - 20, 240, x + 20, 290), fill="white")
        d.ellipse((x - 9, 252, x + 9, 280), fill="#24131f")
    d.arc((190, 320, 290, 400), 20, 160, fill="#24131f", width=9)
    return im


def calendar_image():
    W, H = 560, 720
    im = Image.new("RGB", (W, H), "#f7f2e2")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 150), fill="#d6283b")
    for k in range(5):
        d.ellipse((60 + k * 110, 40, 90 + k * 110, 70), fill="#f7f2e2")
    for r in range(5):
        for c in range(7):
            x, y = 24 + c * 74, 190 + r * 100
            d.rounded_rectangle((x, y, x + 58, y + 78), radius=10, fill="#dbe4ee")
    d.ellipse((24 + 3 * 74 - 14, 190 + 2 * 100 - 14, 24 + 3 * 74 + 72, 190 + 2 * 100 + 92), outline="#d6283b", width=12)
    return im


def tag_image(face):
    """The rule meter's two faces. front: the top half of a 3 over a ragged bottom edge. back: a whole 4."""
    if face == "front":
        W, H = 360, 240
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        base = Image.new("RGB", (W, H), "#f4ecd8")
        d = ImageDraw.Draw(base)
        number(d, "3", W / 2, 16, 250, INK)
        m = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(m)
        rng = random.Random(5)
        pts = [(0, 0), (W, 0)]
        for i in range(13, -1, -1):
            pts.append((i * W / 13, H - 24 + rng.choice((-18, -6, 4, 14, 22)) * (1 if i % 2 else 0.5)))
        md.polygon(pts, fill=255)
        im.paste(base, (0, 0), m)
    else:
        W, H = 360, 300
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        base = Image.new("RGB", (W, H), "#f4ecd8")
        d = ImageDraw.Draw(base)
        number(d, "4", W / 2, 24, 240, INK)
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, W, H), radius=14, fill=255)
        im.paste(base, (0, 0), m)
    return im


_IMG_N = [0]


def img_path(im, name):
    _IMG_N[0] += 1
    p = TMP / f"{name}{_IMG_N[0]}.png"
    im.save(p)
    return p


def img_material(kit, name, im, rough=0.6, emit=0.0, alpha=False):
    p = img_path(im, name)
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


def cut(ob, cutters):
    for i, c in enumerate(cutters):
        m = ob.modifiers.new(f"cut{i}", "BOOLEAN")
        m.operation = "DIFFERENCE"
        m.object = c
        m.solver = "EXACT"
        with bpy.context.temp_override(object=ob, active_object=ob):
            bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.data.objects.remove(c)
    return ob


def prism(kit, name, w, d, h, loc, mat, rot=(0, 0, 0)):
    """A gable roof: a triangular prism, ridge along y, w wide, d deep, h tall (base at the origin plane z = 0)."""
    x, y = w / 2, d / 2
    v = [(-x, -y, 0), (x, -y, 0), (0, -y, h), (-x, y, 0), (x, y, 0), (0, y, h)]
    f = [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)]
    return kit.mesh_obj(name, v, f, mat, None, loc, rot)


# ------------------------------------------------------------------------------------------------ time of day
TODS = {
    "day": dict(sun=3.4, sunc="#fff1dc", hdri=1.0, sky="#7cc6ff", fog="#cfe6f5", fogb=1.0, win=0.0, lamp=0.05, glow=0.0, exp=0.0),
    "dusk": dict(sun=1.6, sunc="#ffb27a", hdri=0.55, sky="#f4a47a", fog="#e9b59a", fogb=0.6, win=0.8, lamp=0.6, glow=0.5, exp=0.0),
    "night": dict(sun=0.7, sunc="#9fb4ff", hdri=0.16, sky="#1d2a5a", fog="#26356c", fogb=0.35, win=1.5, lamp=1.0, glow=1.0, exp=0.0),
}


def tod_state(tl, t):
    cs = [c for c in cues_of(tl, "tod") if c["t"] <= t + 1e-9]
    if not cs:
        return TODS["night"]
    cur = cs[-1]
    prev = cs[-2] if len(cs) > 1 else cur
    u = ss((t - cur["t"]) / max(0.05, cur.get("dur", 0.45)))
    a, b = TODS[prev["n"]], TODS[cur["n"]]
    out = {}
    for k in a:
        if k in ("sunc", "sky", "fog"):
            out[k] = tuple(lerp(x, y, u) for x, y in zip(lin(a[k]), lin(b[k])))
        else:
            out[k] = lerp(a[k], b[k], u)
    return out


# ------------------------------------------------------------------------------------------------ materials
def materials(kit):
    P = kit.plastic
    M = {}
    M["white"] = P("#f6f3ea", 0.8, "white wall")
    M["mint"] = P(MINT, 0.85, "mint wall")
    M["cream"] = P(CREAM, 0.8, "cream")
    M["brass"] = kit.metal(BRASS, 0.3, "brass")
    M["stone"] = P("#ddd7ca", 0.9, "old stone", spec=0.15)
    M["red"] = P(BOOK_RED, 0.5, "book red")
    M["oak"] = kit.texture("wood", 1.4, tint="#a89888", rough=0.55, mat_name="oak door")
    M["floor"] = kit.checker("#f4f2ea", "#26262c", 2.0, "hall checker", 0.35)
    M["brick"] = kit.texture("brick", 1.2, tint="#f0c8b0", mat_name="hall brick")
    M["road"] = kit.texture("asphalt", 0.6, tint="#9aa0ac", rough=0.8, mat_name="road")
    M["grass"] = kit.texture("grass", 1.0, tint="#8be06a", rough=0.9, mat_name="lawn")
    M["walk"] = P("#d4d7de", 0.85, "sidewalk")
    M["blue"] = P(INK, 0.5, "ink blue")
    M["dark"] = P("#1a1a1f", 0.7, "dark")
    M["wicker"] = P("#c89a5a", 0.8, "wicker")
    M["ceiling"] = P("#f1ead6", 0.9, "ceiling")
    M["roof"] = P("#d6563b", 0.6, "roof tiles")
    M["glass"] = kit.glass("#cfe9f7", "window glass")
    M["tile"] = P("#8ad0e8", 0.3, "water")
    M["cobalt"] = P("#2f5fd0", 0.55, "waistcoat")
    # house windows: a plastic that glows warm at night (animate sets the emission)
    w = P("#9fd0ee", 0.2, "window pane")
    b = w.node_tree.nodes["Principled BSDF"]
    b.inputs["Emission Color"].default_value = (*lin("#ffcf7a"), 1)
    b.inputs["Emission Strength"].default_value = 0.0
    M["win"] = w
    M["lampglow"] = kit.emit("#ffe2a8", 6.0, "lamp glow")
    M["sconce"] = kit.emit("#ffe2b0", 3.0, "sconce glow")
    return M


# ------------------------------------------------------------------------------------------------ the hall
def build_hall(kit, M, ctx):
    X0, X1, Y1, H = -5.0, 5.0, 7.5, 4.5
    # floor, walls, ceiling
    kit.box("hall.floor", (10.8, 8.4, 0.2), (0, 3.7, -0.1), M["floor"])
    kit.box("hall.back", (10.8, 0.4, H), (0, Y1 + 0.2, H / 2), M["mint"])
    kit.box("hall.left", (0.4, 8.0, H), (X0 - 0.2, 3.5, H / 2), M["mint"])
    kit.box("hall.right", (0.4, 8.0, H), (X1 + 0.2, 3.5, H / 2), M["mint"])
    kit.box("hall.ceil", (10.8, 8.4, 0.06), (0, 3.7, H - 0.03), M["ceiling"])
    kit.box("hall.roof", (11.4, 8.8, 0.3), (0, 3.6, H + 0.15), M["roof"])
    # wainscot trim and a brick chimney breast behind the lectern (the old stone's neighbour)
    kit.box("hall.rail", (10.0, 0.04, 0.1), (0, Y1 - 0.02, 1.1), M["cream"])
    kit.box("hall.brick", (6.4, 0.06, H - 0.1), (0, Y1 - 0.03, H / 2), M["brick"])
    # the front wall: white outside, mint inside, with the oak door and the arched window cut through both
    inner = kit.box("hall.front.in", (10.8, 0.2, H), (0, -0.1, H / 2), M["mint"])
    outer = kit.box("hall.front.out", (11.0, 0.3, H + 0.2), (0, -0.35, H / 2 + 0.1), M["white"])
    for ob in (inner, outer):
        c1 = kit.box("c1", (2.0, 1.2, 2.1), (2.0, -0.2, 1.95), None)
        c2 = kit.cyl("c2", 1.0, 1.2, (2.0, -0.2, 3.0), None, rot=(math.pi / 2, 0, 0), n=40)
        c3 = kit.box("c3", (1.6, 1.2, 2.8), (-2.6, -0.2, 1.3), None)
        cut(ob, [c1, c2, c3])
    # facade: pilasters, cornice, steps, tower and clock face
    for x in (-5.2, -0.4, 5.2):
        kit.box(f"fac.pil{x}", (0.55, 0.3, H), (x, -0.62, H / 2), M["white"], bevel=0.04)
    kit.box("fac.corn", (11.6, 0.9, 0.35), (0, -0.55, H + 0.1), M["white"], bevel=0.05)
    kit.box("fac.step1", (7.0, 1.0, 0.18), (-1.0, -1.1, 0.09), M["white"], bevel=0.03)
    kit.box("fac.step2", (6.0, 0.5, 0.18), (-1.0, -1.6, 0.0), M["white"], bevel=0.03)
    kit.box("hall.tower", (4.2, 3.2, 4.6), (0, 1.6, H + 2.3), M["white"], bevel=0.04)
    kit.cyl("tower.clock.rim", 1.05, 0.12, (0, -0.07, H + 2.6), M["brass"], rot=(math.pi / 2, 0, 0), n=40)
    kit.cyl("tower.clock", 0.92, 0.1, (0, -0.1, H + 2.6), M["cream"], rot=(math.pi / 2, 0, 0), n=40)
    kit.box("tower.hand1", (0.08, 0.04, 0.6), (0, -0.17, H + 2.82), M["dark"])
    kit.box("tower.hand2", (0.5, 0.04, 0.08), (0.2, -0.17, H + 2.6), M["dark"])
    kit.cyl("tower.roof", 3.3, 2.4, (0, 1.6, H + 5.8), M["roof"], rot=(0, 0, math.pi / 4), n=4, r2=0.05)
    # window furniture: mullions and a sill
    kit.box("win.sill", (2.5, 0.5, 0.1), (2.0, -0.2, 0.85), M["white"], bevel=0.02)
    # the oak door on its hinge, with the brass letter slot (the slot stands 2 cm proud on each face)
    hinge = kit.empty("door.hinge", (-3.38, -0.17, 0))
    kit.box("door.slab", (1.56, 0.1, 2.66), (0.78, 0, 1.33), M["oak"], hinge, bevel=0.02)
    kit.box("door.plate", (0.4, 0.14, 0.1), (0.78, 0, 1.2), M["brass"], hinge, bevel=0.01)
    kit.box("door.slot", (0.3, 0.146, 0.03), (0.78, 0, 1.2), M["dark"], hinge)
    kit.sphere("door.knob", 0.06, (1.4, -0.09, 1.0), M["brass"], hinge)
    kit.sphere("door.knob2", 0.06, (1.4, 0.09, 1.0), M["brass"], hinge)
    ctx["door"] = hinge
    # the basket of slips under the slot
    kit.box("basket", (0.56, 0.36, 0.28), (-2.6, 0.5, 0.14), M["wicker"], bevel=0.03)
    rng = random.Random(4)
    for i in range(9):
        kit.box(f"basket.slip{i}", (0.1, 0.12, 0.012), (-2.6 + rng.uniform(-0.2, 0.2), 0.5 + rng.uniform(-0.1, 0.1), 0.29 + 0.012 * (i % 3)),
                M["cream"], rot=(rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), rng.uniform(0, 3)))
    # the brass wall clock (numerals only), on the left wall; hands are driven by the "clock" cue
    cx, cy, cz = -4.93, 4.0, 3.15
    kit.cyl("clock.rim", 0.66, 0.06, (cx - 0.015, cy, cz), M["brass"], rot=(0, math.pi / 2, 0), n=40)
    kit.cyl("clock.face", 0.58, 0.06, (cx + 0.02, cy, cz), M["cream"], rot=(0, math.pi / 2, 0), n=40)
    for h in range(12):
        a = h * math.pi / 6
        big = h % 3 == 0
        kit.box(f"clock.tick{h}", (0.03, 0.05 if big else 0.03, 0.14 if big else 0.08),
                (cx + 0.055, cy + 0.47 * math.sin(a), cz + 0.47 * math.cos(a)), M["dark"], rot=(-a, 0, 0))
    ph = kit.empty("clock.hpiv", (cx + 0.07, cy, cz))
    pm = kit.empty("clock.mpiv", (cx + 0.085, cy, cz))
    kit.box("clock.hour", (0.03, 0.08, 0.3), (0, 0, 0.15), M["dark"], ph)
    kit.box("clock.min", (0.03, 0.06, 0.45), (0, 0, 0.225), M["dark"], pm)
    kit.sphere("clock.cap", 0.045, (cx + 0.1, cy, cz), M["brass"])
    ctx["clock"] = (ph, pm)
    # a calendar on the right wall, one date circled
    cal = img_material(kit, "calendar", calendar_image(), 0.7)
    img_plane(kit, "calendar", 0.7, 0.9, cal, (4.985, 3.5, 1.95), None, right=(0, -1, 0), up=(0, 0, 1))
    # sconces and lights
    for i, (x, y, rt) in enumerate(((-3.6, Y1 - 0.2, (1, 0, 0)), (3.6, Y1 - 0.2, (1, 0, 0)))):
        kit.box(f"sconce{i}.arm", (0.1, 0.3, 0.08), (x, y, 2.5), M["brass"])
        kit.cyl(f"sconce{i}.shade", 0.2, 0.34, (x, y - 0.12, 2.75), M["sconce"], n=12, r2=0.1)
    kit.light("hall area", "AREA", (0, 3.4, 4.35), 1.0, "#ffe6c0", rot=(0, 0, 0), size=5.0)
    kit.light("hall book lamp", "SPOT", (0.2, 3.0, 3.8), 1.0, "#ffe9c8", size=0.6, spot=50, blend=0.5)
    kit.aim(kit.LIGHTS["hall book lamp"]["obj"], (0.0, LECT[1], 1.0))
    kit.light("hall sconce L", "POINT", (-3.6, 6.9, 2.6), 1.0, "#ffd9a0", size=0.4)
    kit.light("hall sconce R", "POINT", (3.6, 6.9, 2.6), 1.0, "#ffd9a0", size=0.4)
    kit.light("hall face", "POINT", (0.4, 2.2, 2.3), 1.0, "#fff0d8", size=0.8)
    kit.light("hall window", "POINT", (2.0, 1.4, 2.2), 1.0, "#ffe2b8", size=0.5)
    kit.light("hall outside", "POINT", (2.0, -3.0, 2.4), 1.0, "#ffd9a0", size=0.5)


def build_lectern(kit, M, ctx):
    """One seamless block of pale old stone: no joints, no mortar (the lore plant, stories/lore.md)."""
    kit.box("lectern", (2.0, 1.1, 0.95), (LECT[0], LECT[1], 0.475), M["stone"], bevel=0.025)
    for i, (dx, dy) in enumerate(((-0.4, 0.2), (0.7, -0.3))):   # weathering: a few soft pits, still one block
        kit.sphere(f"lectern.pit{i}", 0.05, (LECT[0] + dx - 0.9, LECT[1] - 0.552, 0.4 + 0.2 * i), kit.plastic("#c9c2b2", 0.95, "pit"), seg=8)


def build_book(kit, M, ctx):
    """The door-sized red leather rulebook: open (1.84 m across the cover), thick cream pages, brass corners, a clasp."""
    root = kit.empty("book.open", (LECT[0], LECT[1], 0))
    z0 = 0.95
    kit.box("book.cover", (1.86, 1.26, 0.06), (0, 0, z0 + 0.03), M["red"], root, bevel=0.015)
    for sx in (-1, 1):
        kit.box(f"book.pages{sx}", (0.81, 1.1, 0.17), (sx * 0.41, 0, z0 + 0.145), M["cream"], root, bevel=0.01)
        for sy in (-1, 1):
            kit.box(f"book.corner{sx}{sy}", (0.14, 0.14, 0.012), (sx * 0.86, sy * 0.58, z0 + 0.066), M["brass"], root)
    kit.box("book.spine", (0.04, 1.14, 0.2), (0, 0, z0 + 0.1), M["red"], root)
    kit.box("book.clasp", (0.07, 0.3, 0.012), (0.9, 0.0, z0 + 0.066), M["brass"], root)
    ctx["spreads"] = {}
    for nm in ("stub", "fresh", "last", "old", "cake"):
        mat = img_material(kit, f"spread_{nm}", spread_image(nm), 0.55)
        ob = img_plane(kit, f"spread.{nm}", 1.6, 1.1, mat, (0, 0, z0 + 0.25), root, right=(1, 0, 0), up=(0, 1, 0))
        ctx["spreads"][nm] = ob
    ctx["book_open"] = root
    # the closed book, to carry: upright, 0.3 thick, 0.93 long, 1.26 tall
    cl = kit.empty("book.closed", (0, 0, -40))
    kit.box("bookc.cover", (0.34, 0.93, 1.26), (0, 0, 0), M["red"], cl, bevel=0.025)
    kit.box("bookc.pages", (0.3, 0.86, 1.18), (0, 0.0, 0), M["cream"], cl, bevel=0.01)
    kit.box("bookc.pages2", (0.352, 0.88, 1.2), (0, 0.0, 0), M["red"], cl, bevel=0.02)
    for sy in (-1, 1):
        for sz in (-1, 1):
            for sx in (-1, 1):
                kit.box(f"bookc.corner{sx}{sy}{sz}", (0.02, 0.12, 0.12), (sx * 0.175, sy * 0.44, sz * 0.62), M["brass"], cl)
    for sx in (-1, 1):   # the brass hexagon of the Buhkeeper's red book, on both covers
        kit.cyl(f"bookc.hex{sx}", 0.17, 0.012, (sx * 0.175, 0.0, 0.1), M["brass"], cl, rot=(0, math.pi / 2, 0), n=6)
    kit.box("bookc.clasp", (0.02, 0.12, 0.3), (-0.185, 0.0, 0.0), M["brass"], cl)
    kit.box("bookc.clasp2", (0.02, 0.12, 0.3), (0.185, 0.0, 0.0), M["brass"], cl)
    ctx["book_closed"] = cl


def build_stamp(kit, M, ctx):
    """Otis's brass hand stamp: a mug-sized brass cylinder with a round cherry-red wooden knob. Ink-blue ink."""
    g = kit.empty("stamp", (0.82, LECT[1] + 0.15, 1.19))
    kit.cyl("stamp.pad", 0.085, 0.03, (0, 0, 0.0), M["blue"], g, n=20)
    kit.cyl("stamp.base", 0.085, 0.06, (0, 0, 0.045), M["brass"], g, n=20)
    kit.cyl("stamp.neck", 0.04, 0.1, (0, 0, 0.125), M["brass"], g, n=14)
    kit.sphere("stamp.knob", 0.062, (0, 0, 0.22), kit.plastic("#d6283b", 0.4, "cherry knob"), g, seg=14)
    ctx["stamp"] = g


def build_props_small(kit, M, ctx):
    # slip (a folded slip) and the big unfolded slip with the scrawled 3
    ctx["slip"] = kit.box("slip", (0.1, 0.13, 0.012), (0, 0, -40), M["cream"])
    pen = kit.empty("pencil", (0, 0, -40))
    kit.box("pencil.body", (0.025, 0.025, 0.3), (0, 0, 0), kit.plastic("#f2c230", 0.5, "pencil"), pen, bevel=0.004)
    kit.box("pencil.tip", (0.02, 0.02, 0.05), (0, 0, -0.17), kit.plastic("#3a3a3a", 0.5, "lead"), pen)
    ctx["pencil"] = pen
    sm = img_material(kit, "slip3", slip_image("three"), 0.7)
    ctx["slip3"] = img_plane(kit, "slip3", 0.22, 0.29, sm, (0, 0, -40))
    # the torn leaf (rule three on the front, rule four on the back)
    fm = img_material(kit, "page_front", page_image("front"), 0.7, alpha=True)
    bm = img_material(kit, "page_back", page_image("back"), 0.7, alpha=True)
    root = kit.empty("ppage", (0, 0, -40))
    front = img_plane(kit, "ppage.front", 0.34, 0.46, fm, (0, 0, 0.002), root)
    back = img_plane(kit, "ppage.back", 0.34, 0.46, bm, (0, 0, -0.002), root)
    back.rotation_euler = (math.pi, 0, 0)
    ctx["ppage"] = (root, front, back)
    # the folded page sticking out of the waistcoat pocket
    fold = kit.box("ppage.fold", (0.1, 0.012, 0.09), (0, 0, -40), M["cream"], bevel=0.004)
    ctx["ppage_fold"] = fold
    # mom's photo on the lectern
    pm = img_material(kit, "photo", photo_image(), 0.4)
    wood = kit.plastic("#8a5a30", 0.5, "frame wood")
    kit.box("photo.frame", (0.3, 0.04, 0.36), (0.78, LECT[1] - 0.4, 1.62), wood, bevel=0.01)
    kit.box("photo.post", (0.05, 0.04, 0.5), (0.78, LECT[1] - 0.4, 1.2), wood, bevel=0.005)
    img_plane(kit, "photo", 0.24, 0.3, pm, (0.78, LECT[1] - 0.425, 1.62), None, right=(1, 0, 0), up=(0, 0, 1))
    # the party plate with a slice
    pl = kit.empty("plate", (0, 0, -40))
    kit.cyl("plate.disc", 0.14, 0.015, (0, 0, 0), kit.plastic("#fafafa", 0.5, "plate"), pl, n=24)
    kit.box("plate.slice", (0.11, 0.1, 0.08), (0, 0, 0.05), kit.plastic("#f6a8c0", 0.6, "cake"), pl, bevel=0.012)
    kit.box("plate.cream", (0.11, 0.1, 0.02), (0, 0, 0.07), kit.plastic("#fff6e0", 0.6, "icing"), pl, bevel=0.008)
    kit.sphere("plate.cherry", 0.022, (0, 0, 0.1), kit.plastic("#d6283b", 0.3, "cherry"), pl, seg=8)
    ctx["plate"] = pl
    # an orange sleeve, pushing a slip through the slot (outside the door)
    sl = kit.empty("sleeve", (0, 0, -40))
    kit.box("sleeve.arm", (0.12, 0.4, 0.12), (0, -0.22, 0), kit.plastic("#ff8a1f", 0.7, "orange"), sl, bevel=0.03)
    kit.box("sleeve.cuff", (0.13, 0.05, 0.13), (0, 0.0, 0), kit.plastic("#ffffff", 0.7, "cuff"), sl)
    kit.box("sleeve.hand", (0.08, 0.1, 0.08), (0, 0.07, 0), kit.plastic("#e6b48a", 0.5, "hand"), sl, bevel=0.02)
    ctx["sleeve"] = sl


# ------------------------------------------------------------------------------------------------ the street
def build_street(kit, M, ctx):
    kit.plane("ground", (300, 330), (0, -120, -0.02), M["grass"])
    kit.plane("ground2", (900, 500), (500, 0, -0.02), M["grass"])
    kit.box("road", (6.4, 125, 0.06), (0, -66, -0.03 + 0.03), M["road"])
    for s in (-1, 1):
        kit.box(f"walk{s}", (2.0, 125, 0.1), (s * 4.4, -66, 0.0), M["walk"])
    kit.box("plaza", (16, 6.4, 0.08), (0, -3.2, 0.0), M["walk"])
    for k in range(10):   # dashes down the road
        kit.box(f"dash{k}", (0.14, 1.6, 0.012), (0, -9 - 8 * k, 0.034), kit.plastic("#fff3c2", 0.7, "dash"))
    cols = ["#8fe0b8", "#ffd95a", "#ff8a6b", "#7cc6ff"]
    roofs = ["#d6563b", "#4a6fb0", "#8a5a3c", "#3f8f5a"]
    rng = random.Random(9)
    k = 0
    for s in (-1, 1):
        y = -9.0
        i = s == 1
        while y > -100:
            w = rng.uniform(5.4, 6.4)
            h = rng.uniform(4.2, 5.6)
            c = cols[k % 4]
            body = kit.box(f"house{k}", (6.0, w, h), (s * 8.7, y, h / 2), kit.plastic(c, 0.7, f"house {c}"), bevel=0.04)
            prism(kit, f"roof{k}", 6.8, w + 0.5, 2.0, (s * 8.7, y, h), kit.plastic(roofs[(k + s) % 4], 0.6, f"roofmat{(k + s) % 4}"))
            fx = s * 5.7   # the front face x
            wx = fx - s * 0.012
            kit.box(f"door{k}", (0.1, 1.1, 2.1), (fx - s * 0.04, y + w / 4, 1.05), kit.plastic("#fff7e6", 0.6, "doorpaint"))
            for r in range(2):
                for cidx in range(2):
                    if cidx == 1 and r == 0:
                        continue   # the door
                    kit.box(f"win{k}_{r}{cidx}", (0.1, 1.0, 1.1), (fx - s * 0.04, y + (-1.3 if cidx == 0 else 1.3), 1.5 + 2.0 * r), M["win"])
                    kit.box(f"winf{k}_{r}{cidx}", (0.06, 1.2, 1.3), (fx - s * 0.02, y + (-1.3 if cidx == 0 else 1.3), 1.5 + 2.0 * r), M["white"])
            if k % 3 == 1:
                kit.box(f"chim{k}", (0.7, 0.7, 1.4), (s * 10.2, y - 1.0, h + 1.6), kit.plastic("#b86a50", 0.8, "chimney"))
            y -= w + 1.4
            k += 1
    # lamps and trees along the sidewalks
    ctx["lamps"] = []
    for j, yv in enumerate((-4.5, -12.5, -20.5, -28.5, -36.5, -48.5)):
        for s in (-1, 1):
            x = s * 3.6
            kit.cyl(f"lamp{j}{s}.post", 0.07, 3.6, (x, yv, 1.8), M["dark"], n=10)
            kit.sphere(f"lamp{j}{s}.glass", 0.2, (x, yv, 3.7), M["lampglow"], seg=12)
            nm = f"street lamp {j}{s}"
            if j < 4:
                kit.light(nm, "POINT", (x, yv, 3.5), 1.0, "#ffd9a0", size=0.25)
                ctx["lamps"].append(nm)
    for j, yv in enumerate((-8.5, -16.5, -24.5, -33.0, -42.0, -52.0)):
        kit.prop("commontree_1" if j % 2 else "birchtree_1", (-4.6 if j % 2 else 4.6, yv, 0), rot=j * 40, height=4.6)
    kit.light("sun", "SUN", (40, -50, 70), 1.0, "#fff1dc")
    kit.aim(kit.LIGHTS["sun"]["obj"], (0, 0, 0))
    kit.light("hall glow", "POINT", (0.0, -4.0, 3.6), 1.0, "#ffd9a0", size=1.0)
    kit.light("plaza fill", "POINT", (-1.0, -9.0, 5.0), 1.0, "#ffe9c8", size=1.0)
    # distant green hills for the horizon
    for i, (x, y, r) in enumerate(((-60, -150, 30), (10, -170, 40), (70, -145, 26), (-10, -135, 18))):
        kit.cyl(f"hill{i}", r, 14, (x, y, 3.0), kit.plastic("#6fcf62", 0.9, "hill"), n=20, r2=r * 0.3)


# ------------------------------------------------------------------------------------------------ the other rooms
def room_shell(kit, M, name, cx, y0, y1, w, h, wall_mat, floor_mat, front=None, ceil=False):
    kit.box(f"{name}.floor", (w + 0.8, y1 - y0 + 0.8, 0.2), (cx, (y0 + y1) / 2, -0.1), floor_mat)
    back = kit.box(f"{name}.back", (w + 0.8, 0.4, h), (cx, y1 + 0.2, h / 2), wall_mat)
    left = kit.box(f"{name}.left", (0.4, y1 - y0 + 0.4, h), (cx - w / 2 - 0.2, (y0 + y1) / 2, h / 2), wall_mat)
    right = kit.box(f"{name}.right", (0.4, y1 - y0 + 0.4, h), (cx + w / 2 + 0.2, (y0 + y1) / 2, h / 2), wall_mat)
    if ceil:
        kit.box(f"{name}.ceil", (w + 0.8, y1 - y0 + 0.8, 0.1), (cx, (y0 + y1) / 2, h + 0.05), M["ceiling"])
    return back, left, right


def build_diner(kit, M, ctx):
    cx = 200.0
    butter = kit.plastic("#ffd95a", 0.8, "diner wall")
    tile = kit.checker("#fff6e0", "#e8795a", 2.0, "diner checker", 0.35)
    room_shell(kit, M, "diner", cx, -0.5, 5.0, 7.0, 3.4, butter, tile)
    counter = kit.texture("wood", 1.2, tint="#e0a066", rough=0.5, mat_name="counter wood")
    kit.box("counter", (3.4, 0.8, 1.0), (cx, 2.25, 0.5), counter, bevel=0.02)
    kit.box("counter.top", (3.6, 0.95, 0.07), (cx, 2.25, 1.035), kit.plastic("#fafafa", 0.35, "counter top"), bevel=0.02)
    kit.box("shelf", (3.0, 0.3, 0.07), (cx, 4.75, 1.9), counter)
    for i in range(5):
        kit.cyl(f"cup{i}", 0.07, 0.11, (cx - 1.2 + i * 0.6, 4.75, 1.985), kit.plastic("#ffffff", 0.4, "cup"), n=14)
    # the painted cup sign, no letters
    kit.cyl("sign.disc", 0.5, 0.04, (cx, 4.96, 2.75), kit.plastic("#e8795a", 0.6, "sign coral"), rot=(math.pi / 2, 0, 0), n=32)
    kit.cyl("sign.cup", 0.17, 0.26, (cx, 4.93, 2.72), kit.plastic("#ffffff", 0.4, "sign cup"), rot=(math.pi / 2, 0, 0), n=20, r2=0.13)
    kit.cyl("sign.handle", 0.07, 0.03, (cx + 0.19, 4.93, 2.75), kit.plastic("#ffffff", 0.4, "sign cup"), rot=(math.pi / 2, 0, 0), n=14)
    # the radio: a chunky red box with a grille and two knobs, an aerial
    red = kit.plastic("#e8473b", 0.45, "radio red")
    kit.box("radio", (0.4, 0.2, 0.26), (cx + 0.7, 2.05, 1.2), red, bevel=0.03)
    kit.box("radio.grille", (0.22, 0.012, 0.16), (cx + 0.64, 1.943, 1.2), kit.plastic("#2a2a30", 0.6, "grille"))
    for i, dx in enumerate((0.8, 0.88)):
        kit.cyl(f"radio.knob{i}", 0.025, 0.02, (cx + dx - 0.04, 1.935, 1.25 - 0.06 * i), kit.plastic("#fff6e0", 0.5, "knob"), rot=(math.pi / 2, 0, 0), n=10)
    kit.cyl("radio.aerial", 0.006, 0.5, (cx + 0.82, 2.05, 1.6), kit.metal("#cfd3d8", 0.3, "aerial"), rot=(0, 0.3, 0), n=6)
    for dx in (-1.2, 0.0, 1.2):
        kit.prop("stool", (cx + dx, 0.8, 0), height=0.72, tint="#e8795a")
    kit.prop("houseplant_1", (cx - 2.6, 4.2, 0), height=1.4)
    kit.light("diner key", "AREA", (cx, 0.5, 3.2), 1.0, "#fff0d8", size=4.0)
    kit.light("diner face", "POINT", (cx + 0.3, 0.3, 2.0), 1.0, "#fff4e0", size=0.6)


def build_pet(kit, M, ctx):
    cx = 300.0
    coral = kit.plastic("#ff8a6b", 0.75, "pet wall")
    woodf = kit.texture("wood", 1.0, tint="#e8c090", rough=0.6, mat_name="pet floor")
    back, left, right = room_shell(kit, M, "pet", cx, 0.4, 5.0, 9.0, 3.6, coral, woodf, ceil=True)
    front = kit.box("pet.front", (9.8, 0.4, 3.6), (cx, 0.2, 1.8), coral)
    cut(front, [kit.box("pc1", (3.2, 1.0, 1.8), (cx, 0.2, 1.75), None), kit.box("pc2", (1.2, 1.0, 2.5), (cx + 3.2, 0.2, 1.25), None)])
    kit.box("pet.sill", (3.5, 0.6, 0.1), (cx, -0.05, 0.85), M["white"], bevel=0.02)
    kit.box("pet.header", (3.6, 0.1, 0.12), (cx, -0.01, 2.68), M["white"])
    for sx in (-1, 1):
        kit.box(f"pet.jamb{sx}", (0.12, 0.1, 1.9), (cx + sx * 1.66, -0.01, 1.75), M["white"])
    # the painted feather sign, no letters
    kit.cyl("pet.sign", 0.46, 0.05, (cx, -0.04, 3.1), kit.plastic("#fff6e0", 0.6, "pet sign"), rot=(math.pi / 2, 0, 0), n=32)
    green = kit.plastic("#58c24a", 0.5, "feather green")
    kit.box("pet.feather", (0.2, 0.03, 0.62), (cx, -0.075, 3.1), green, rot=(0, 0.45, 0), bevel=0.04)
    kit.box("pet.rachis", (0.025, 0.035, 0.7), (cx, -0.095, 3.1), kit.plastic("#2f7a2a", 0.5, "rachis"), rot=(0, 0.45, 0))
    # the display: a low stage, the plants, and the perch
    kit.box("pet.stage", (3.0, 1.3, 0.3), (cx, 1.1, 0.15), kit.plastic("#fff0cc", 0.8, "stage"), bevel=0.02)
    kit.prop("houseplant_1", (cx - 1.2, 1.2, 0.3), height=1.1)
    kit.prop("houseplant_1", (cx + 1.2, 1.3, 0.3), height=0.9, rot=90)
    kit.prop("shelf_1", (cx - 3.4, 4.4, 0), height=2.0)
    wood = kit.plastic("#a06a3a", 0.6, "perch wood")
    kit.cyl("perch.pole", 0.03, 0.9, (cx + 0.05, 1.1, 0.75), wood, n=8)
    kit.box("perch.bar", (0.7, 0.05, 0.05), (cx + 0.05, 1.1, 1.21), wood, bevel=0.01)
    kit.cyl("perch.base", 0.18, 0.05, (cx + 0.05, 1.1, 0.325), wood, n=16)
    # the parrot: a green blocky bird, red cheek patch, beak open, head cocked
    grn, dg = kit.plastic("#58c24a", 0.5, "parrot green"), kit.plastic("#2f8f3a", 0.5, "parrot dark")
    orange, red = kit.plastic("#ff9a2a", 0.5, "beak"), kit.plastic("#e8302f", 0.5, "cheek")
    p = kit.empty("parrot", (cx + 0.05, 1.08, 1.24))
    kit.box("parrot.body", (0.2, 0.17, 0.32), (0, 0.0, 0.16), grn, p, bevel=0.04)
    kit.box("parrot.wingL", (0.04, 0.15, 0.24), (-0.115, 0.03, 0.17), dg, p, bevel=0.015)
    kit.box("parrot.wingR", (0.04, 0.15, 0.24), (0.115, 0.03, 0.17), dg, p, bevel=0.015)
    kit.box("parrot.tail", (0.07, 0.06, 0.36), (0, 0.1, -0.04), dg, p, rot=(-0.25, 0, 0), bevel=0.02)
    hd = kit.empty("parrot.head", (0, -0.01, 0.38), p, rot=(0, 0.36, 0))
    kit.box("parrot.skull", (0.2, 0.18, 0.18), (0, 0, 0.04), grn, hd, bevel=0.05)
    for sx in (-1, 1):
        kit.box(f"parrot.eyew{sx}", (0.05, 0.02, 0.06), (sx * 0.06, -0.093, 0.075), kit.plastic("#ffffff", 0.3, "eyew"), hd, bevel=0.01)
        kit.box(f"parrot.eye{sx}", (0.025, 0.02, 0.035), (sx * 0.06, -0.103, 0.075), kit.plastic("#111114", 0.3, "eyeb"), hd)
        kit.box(f"parrot.cheek{sx}", (0.06, 0.02, 0.05), (sx * 0.093, -0.06, 0.0), red, hd, bevel=0.01)
    kit.box("parrot.beakU", (0.09, 0.11, 0.05), (0, -0.14, 0.03), orange, hd, rot=(0.2, 0, 0), bevel=0.012)
    kit.box("parrot.beakL", (0.07, 0.08, 0.03), (0, -0.115, -0.03), orange, hd, rot=(-0.25, 0, 0), bevel=0.01)
    kit.light("pet key", "AREA", (cx, -1.0, 3.2), 1.0, "#fff4e0", size=3.0)
    kit.light("pet inside", "AREA", (cx, 2.2, 2.8), 1.0, "#fff0d8", size=2.0)


def build_bridge(kit, M, ctx):
    cx = 400.0
    stone = kit.plastic("#c9c4b8", 0.9, "bridge stone")
    lawn = M["grass"]
    for sx in (-1, 1):
        kit.box(f"bank{sx}", (8.0, 12, 0.8), (cx + sx * 6.0, 0, 0.4), lawn)
    kit.plane("channel", (4.2, 12.0), (cx, 0, 0.0), kit.plastic("#7a6a50", 0.9, "mud"))
    kit.plane("water", (4.1, 12.0), (cx, 0, 0.25), M["tile"], rot=(0, 0, 0))
    deck = kit.box("bridge.deck", (4.2, 2.6, 1.0), (cx, 0, 0.3), stone, bevel=0.03)
    cut(deck, [kit.cyl("bc", 0.95, 3.4, (cx, 0, -0.3), None, rot=(math.pi / 2, 0, 0), n=32)])
    kit.box("bridge.top", (4.4, 2.5, 0.06), (cx, 0, 0.83), kit.plastic("#b2aea2", 0.9, "bridge top"))
    for sy in (-1, 1):
        kit.box(f"bridge.wall{sy}", (4.4, 0.3, 0.3), (cx, sy * 1.1, 1.01), stone, bevel=0.04)
    for i, (x, y) in enumerate(((-6.8, 3.4), (6.0, 4.5), (-4.5, 5.2), (7.6, -3.0))):
        kit.prop("commontree_1", (cx + x, y, 0.8), rot=i * 55, height=4.2)
    kit.prop("bush_1", (cx - 3.0, -2.6, 0.8), height=0.8)
    kit.prop("flowers", (cx + 3.4, -2.4, 0.8), height=0.4)
    kit.light("bridge key", "AREA", (cx, -3.0, 4.0), 1.0, "#fff4e0", size=5.0)
    kit.plane("bridge.sky", (80, 40), (cx, 14, 8), kit.plastic("#cfe9f7", 1.0, "back sky"), rot=(math.pi / 2, 0, 0))


def party_room(kit, M, ctx):
    cx = 500.0
    lilac = kit.plastic("#cdbfe6", 0.85, "mom wall")
    wood = kit.texture("wood", 1.0, tint="#e8c090", rough=0.55, mat_name="mom floor")
    back, left, right = room_shell(kit, M, "mom", cx, 0.0, 6.0, 7.0, 3.0, lilac, wood, ceil=True)
    front = kit.box("mom.front", (7.8, 0.3, 3.0), (cx, -0.15, 1.5), M["white"])
    cut(front, [kit.box("mw", (4.0, 1.0, 1.5), (cx, -0.15, 1.65), None)])
    kit.box("mom.sill", (4.4, 0.5, 0.08), (cx, -0.2, 0.9), M["white"])
    kit.box("mom.lawn", (30, 16, 0.1), (cx, -10, -0.05), M["grass"])
    kit.box("mom.path", (1.6, 8, 0.06), (cx, -4.2, 0.0), M["walk"])
    for sx in (-1, 1):
        kit.prop("bush_1", (cx + sx * 3.4, -1.0, 0), height=0.9)
        kit.prop("commontree_1", (cx + sx * 6.0, -3.0, 0), height=4.4)
    # the party: table with cloth, cake, plates; bunting; shelf and plant
    cloth = kit.plastic("#eac3d3", 0.9, "cloth")
    kit.box("mom.table.top", (3.2, 1.1, 0.06), (cx, 3.6, 0.78), cloth, bevel=0.01)
    kit.box("mom.table.skirt", (3.26, 1.16, 0.62), (cx, 3.6, 0.45), cloth, bevel=0.02)
    cake = kit.empty("cake", (cx + 1.2, 3.8, 0.81))
    kit.cyl("cake.a", 0.24, 0.12, (0, 0, 0.06), kit.plastic("#f6a8c0", 0.6, "cake pink"), cake, n=24)
    kit.cyl("cake.b", 0.18, 0.1, (0, 0, 0.17), kit.plastic("#fff6e0", 0.6, "icing"), cake, n=24)
    kit.sphere("cake.cherry", 0.03, (0, 0, 0.24), kit.plastic("#d6283b", 0.3, "cherry"), cake, seg=8)
    ctx["cake"] = cake
    for i, (dx, dy) in enumerate(((-1.35, 3.3), (-1.0, 3.95), (1.6, 4.0), (1.55, 3.3))):
        kit.cyl(f"mom.plate{i}", 0.13, 0.015, (cx + dx, dy, 0.82), kit.plastic("#ffffff", 0.5, "plate"), n=20)
    for i, c in enumerate(("#ff6a6a", "#ffd95a", "#58c2c2", "#9ad06a", "#b69be0", "#ff9ec8", "#7cc6ff", "#ff8a1f", "#ffd95a")):
        kit.box(f"bunt{i}", (0.28, 0.02, 0.28), (cx - 3.2 + i * 0.8, 5.92, 2.55 + 0.1 * math.sin(i * 0.8)), kit.plastic(c, 0.6, f"bunt{i}"), rot=(0, math.pi / 4, 0))
    kit.prop("bookshelf", (cx - 3.0, 5.5, 0), height=1.9)
    kit.prop("houseplant_1", (cx + 3.0, 5.4, 0), height=1.3)
    kit.light("mom key", "AREA", (cx, 2.5, 2.9), 0.55, "#fff0d8", size=5.0)
    kit.light("mom face", "POINT", (cx, 0.8, 2.2), 0.6, "#fff4e0", size=0.6)
    kit.light("mom back", "POINT", (cx, 5.0, 2.4), 0.6, "#ffe9c8", size=0.5)


def kitchen(kit, M, ctx):
    cx = 600.0
    wall = kit.plastic("#7a8fb8", 0.9, "kit wall")
    wood = kit.texture("wood", 1.0, tint="#b88a5a", rough=0.55, mat_name="kit floor")
    room_shell(kit, M, "kit", cx, -3.0, 3.2, 5.0, 3.0, wall, wood, ceil=True)
    kit.box("kit.window", (1.6, 0.06, 1.2), (cx - 1.0, 3.17, 1.7), kit.emit("#2a3f8a", 0.8, "night window"))
    kit.box("kit.winframe", (1.8, 0.05, 1.4), (cx - 1.0, 3.19, 1.7), M["white"])
    kit.prop("kitchen_cabinet1", (cx + 1.4, 2.85, 0), height=1.0)
    kit.prop("kitchen_fridge", (cx + 2.1, 2.8, 0), height=1.9)
    tablem = kit.plastic("#e0b074", 0.45, "kit table")
    kit.cyl("kit.table", 0.6, 0.05, (cx, 0.95, 0.76), tablem, n=28)
    kit.cyl("kit.tablestem", 0.07, 0.74, (cx, 0.95, 0.37), tablem, n=12)
    kit.cyl("kit.tablefoot", 0.28, 0.04, (cx, 0.95, 0.02), tablem, n=20)
    kit.prop("chair_1", (cx - 0.9, 1.7, 0), rot=60, height=0.9)
    # a warm lamp on the table: the one warm light, the rest blue night
    kit.cyl("lamp.base", 0.07, 0.03, (cx + 0.38, 1.12, 0.805), M["brass"], n=12)
    kit.cyl("lamp.stem", 0.012, 0.3, (cx + 0.38, 1.12, 0.96), M["brass"], n=8)
    kit.cyl("lamp.shade", 0.13, 0.16, (cx + 0.38, 1.12, 1.18), kit.emit("#ffcf8a", 2.5, "lamp shade"), n=16, r2=0.07)
    kit.light("kit lamp", "POINT", (cx + 0.38, 1.0, 1.2), 1.0, "#ffc680", size=0.15)
    kit.light("kit fill", "AREA", (cx, 0.0, 2.8), 1.0, "#8aa4e0", size=3.0)
    kit.light("kit face", "POINT", (cx + 0.5, 0.2, 1.8), 1.0, "#ffd7a0", size=0.4)


# ------------------------------------------------------------------------------------------------ the rule meter
def build_tag(kit, ctx):
    cam = kit.OBJ["cam"]
    piv = kit.empty("tag.pivot", (0, 0, -0.4), cam)
    fm = img_material(kit, "tag_front", tag_image("front"), emit=1.0)
    bm = img_material(kit, "tag_back", tag_image("back"), emit=1.0)
    front = img_plane(kit, "tag.front", 1.0, 1.0, fm, (0, -0.5, 0), piv)
    back = img_plane(kit, "tag.back", 1.0, 1.0, bm, (0, 0.5, 0), piv)
    back.rotation_euler = (math.pi, 0, 0)
    for o in (front, back):
        no_shadow(o)
        try:
            o.visible_glossy = False
            o.visible_diffuse = False
            o.visible_transmission = False
        except Exception:
            pass
    ctx["tag"] = (piv, front, back)


def lens_at(story, tl, t):
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next(s for s in story["shots"] if s["id"] == shot["id"])
    keys = spec["cam"]
    if len(keys) == 1:
        return keys[0][3]
    u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
    return lerp(keys[0][3], keys[1][3], ss(u))


# ------------------------------------------------------------------------------------------------ the cast's extras
def _head(name):
    return bpy.data.objects[f"{name}.headg"]


def dress_otis(kit, name="me"):
    """The Buhkeeper (the channel's avatar; rig spec in make_story): the rig gives the top hat, fringe, teal coat, scarf.
    Here only the ink-blue thumb (the stamp's mark)."""
    c = rig.CHARS[name]
    P = kit.plastic
    arm = c.P["arm-1"]
    kit.box(f"{name}.thumb", (0.2, 0.2, 0.3), (0.0, -0.38, -1.62), P(INK, 0.4, "ink thumb"), arm, bevel=0.05)
    kit.box(f"{name}.inkpalm", (0.99, 0.99, 0.18), (0.0, 0.0, -1.7), P("#4a6bec", 0.4, "ink palm"), arm, bevel=0.04)


def dress_milo(kit, name):
    c = rig.CHARS[name]
    if name == "milo":   # short shaggy crop above the ears: a ragged fringe and tufts on top (no bob)
        hg = _head(name)
        hair = kit.plastic("#c99a4e", 0.65, "milo hair")
        top = faces.HEAD_H / 2
        kit.box(f"{name}.fringe", (2 * faces.HEAD_R + 0.04, 0.4, 0.3), (0, -faces.HEAD_R + 0.15, top - 0.12), hair, hg, rot=(0, 0.1, 0), bevel=0.1)
        for i, (x, y, h, r) in enumerate(((-0.45, -0.1, 0.34, 0.3), (0.05, 0.1, 0.42, -0.2), (0.45, -0.05, 0.3, 0.35), (-0.1, -0.35, 0.28, -0.3))):
            kit.box(f"{name}.tuft{i}", (0.3, 0.3, h), (x, y, top + h / 2 - 0.05), hair, hg, rot=(0.1, r, r * 0.6), bevel=0.06)
    kit.box(f"{name}.stripe", (2.04, 1.04, 0.2), (0, 0, 1.1), kit.plastic("#ffffff", 0.7, "milo stripe"), c.upper, bevel=0.03)
    kit.box(f"{name}.pouch", (1.2, 1.06, 0.5), (0, 0, 0.3), kit.plastic("#e87a10", 0.7, "pouch"), c.upper, bevel=0.05)


def dress_mom(kit, name):
    c = rig.CHARS[name]
    hg = _head(name)
    gold = kit.plastic("#ffd95a", 0.5, "crown")
    top = faces.HEAD_H / 2
    kit.box(f"{name}.crown", (1.0, 1.0, 0.14), (0, 0.0, top + 0.09), gold, hg, bevel=0.03)
    for i, x in enumerate((-0.4, -0.2, 0.0, 0.2, 0.4)):
        kit.box(f"{name}.prong{i}", (0.14, 0.14, 0.34 if i % 2 == 0 else 0.24), (x, -0.4, top + 0.25), gold, hg, rot=(0, 0, 0.0), bevel=0.02)
        kit.box(f"{name}.prongb{i}", (0.14, 0.14, 0.3 if i % 2 == 0 else 0.22), (x, 0.4, top + 0.24), gold, hg, bevel=0.02)
    for i, (x, y) in enumerate(((-0.4, 0.0), (0.4, 0.0))):
        kit.box(f"{name}.prongs{i}", (0.14, 0.14, 0.3), (x, y, top + 0.24), gold, hg, bevel=0.02)
    kit.sphere(f"{name}.jewel", 0.07, (0, -0.52, top + 0.1), kit.plastic("#ff6a6a", 0.3, "jewel"), hg, seg=8)
    for i in range(3):
        kit.sphere(f"{name}.cbtn{i}", 0.06, (0, -0.52, 0.5 + 0.45 * i), kit.plastic("#f4ecd8", 0.4, "cardi button"), c.upper, seg=8)


def dress_cook(kit, name):
    hg = _head(name)
    kit.box(f"{name}.cap", (1.3, 1.3, 0.5), (0, 0.0, faces.HEAD_H / 2 + 0.15), kit.plastic("#ffffff", 0.8, "paper cap"), hg, bevel=0.1)
    kit.box(f"{name}.capband", (1.3, 1.32, 0.14), (0, 0.0, faces.HEAD_H / 2 - 0.04), kit.plastic("#f0f0f0", 0.8, "paper cap"), hg, bevel=0.03)


def dress_mailman(kit, name):
    c = rig.CHARS[name]
    hg = _head(name)
    navy = kit.plastic("#243a7a", 0.6, "mail navy")
    kit.box(f"{name}.cap", (1.3, 1.3, 0.36), (0, 0.0, faces.HEAD_H / 2 + 0.06), navy, hg, bevel=0.1)
    kit.box(f"{name}.peak", (1.0, 0.6, 0.06), (0, -faces.HEAD_R - 0.2, faces.HEAD_H / 2 - 0.08), navy, hg, bevel=0.02)
    tan = kit.plastic("#c8a066", 0.75, "mail bag")
    kit.box(f"{name}.strap", (0.16, 0.08, 2.5), (0, -0.54, 1.0), tan, c.upper, rot=(0, 0.6, 0), bevel=0.02)
    kit.box(f"{name}.bag", (0.5, 1.2, 1.0), (2.3, 0.1, 0.3), tan, c.upper, bevel=0.06)
    kit.box(f"{name}.flap", (0.52, 1.22, 0.3), (2.3, 0.1, 0.72), kit.plastic("#b08850", 0.75, "bag flap"), c.upper, bevel=0.04)


def dress_jogger(kit, name):
    hg = _head(name)
    kit.cyl(f"{name}.band", faces.HEAD_R + 0.045, 0.2, (0, 0, 0.3), kit.plastic("#ffffff", 0.7, "headband"), hg, n=28)


DRESS = {"me": dress_otis, "milo": dress_milo, "milo_h": dress_milo, "mom": dress_mom, "cook": dress_cook,
         "mailman": dress_mailman, "jogger": dress_jogger}


# ------------------------------------------------------------------------------------------------ build / animate
def build(kit, story, tl):
    ctx = {"inited": False}
    M = materials(kit)
    ctx["M"] = M
    build_hall(kit, M, ctx)
    build_lectern(kit, M, ctx)
    build_book(kit, M, ctx)
    build_stamp(kit, M, ctx)
    build_props_small(kit, M, ctx)
    build_street(kit, M, ctx)
    build_diner(kit, M, ctx)
    build_pet(kit, M, ctx)
    build_bridge(kit, M, ctx)
    party_room(kit, M, ctx)
    kitchen(kit, M, ctx)
    build_tag(kit, ctx)
    return ctx


def _world_nodes():
    w = bpy.context.scene.world
    plain = lit = None
    for n in w.node_tree.nodes:
        if n.type == "BACKGROUND":
            if n.name == "Background":
                plain = n
            else:
                lit = n
    return plain, lit


def hand_pos(name, side=0, local=(0, 0, -1.6)):
    c = rig.CHARS[name]
    arm = c.P["arm-1" if side == 0 else "arm1"]
    return arm.matrix_world @ V(local)


def place(ob, pos, rot=None):
    ob.location = pos
    if rot is not None:
        ob.rotation_euler = rot


def animate(kit, story, tl, t, ctx):
    bpy.context.view_layer.update()
    if not ctx["inited"]:
        ctx["inited"] = True
        for nm, fn in DRESS.items():
            if nm in rig.CHARS:
                fn(kit, nm)
        ctx["plain"], ctx["lit"] = _world_nodes()
        fc = kit.FOG["color"]
        ctx["fog_nodes"] = []
        for m in bpy.data.materials:
            if m.use_nodes:
                for n in m.node_tree.nodes:
                    if n.type == "EMISSION" and all(abs(n.inputs["Color"].default_value[i] - fc[i]) < 1e-4 for i in range(3)):
                        ctx["fog_nodes"].append(n)
        for nm in DRESS:
            if nm in rig.CHARS:
                hide_tree(rig.CHARS[nm].root, rig.CHARS[nm].root.hide_render)
        bpy.context.view_layer.update()
    M = ctx["M"]
    # ---- time of day: every change is a slow ramp
    s = tod_state(tl, t)
    if ctx["plain"] is not None:
        ctx["plain"].inputs["Color"].default_value = (*s["sky"], 1)
    if ctx["lit"] is not None:
        ctx["lit"].inputs["Strength"].default_value = 0.45 * s["hdri"]
    for n in ctx["fog_nodes"]:
        n.inputs["Color"].default_value = (*s["fog"], 1)
        n.inputs["Strength"].default_value = s["fogb"]
    sun = kit.LIGHTS["sun"]["light"]
    sun.color = s["sunc"]
    pane = M["win"].node_tree.nodes["Principled BSDF"]
    pane.inputs["Emission Strength"].default_value = s["win"]
    over = {"sun": s["sun"]}
    for nm in ctx["lamps"]:
        over[nm] = 520.0 * s["lamp"]
    over["hall glow"] = 170.0 * s["glow"]
    over["plaza fill"] = 130.0 * s["glow"]
    over["hall outside"] = 160.0 * s["glow"]
    over["hall area"] = 80.0
    over["hall book lamp"] = 18.0
    over["hall sconce L"] = 90.0
    over["hall sconce R"] = 90.0
    over["hall face"] = 70.0
    over["hall window"] = 120.0
    over["diner key"] = 420.0
    over["diner face"] = 60.0
    over["pet key"] = 300.0
    over["pet inside"] = 160.0
    over["bridge key"] = 500.0
    over["mom key"] = 420.0
    over["mom face"] = 80.0
    over["mom back"] = 90.0
    over["kit lamp"] = 60.0
    over["kit fill"] = 150.0
    over["kit face"] = 40.0
    # ---- the clock
    c = latest(tl, "clock", t)
    if c:
        h, m = c["v"]
        ph, pm = ctx["clock"]
        ph.rotation_euler = (-(((h % 12) + m / 60.0) / 12.0) * 2 * math.pi, 0, 0)
        pm.rotation_euler = (-(m / 60.0) * 2 * math.pi, 0, 0)
    # ---- the book: open on the lectern, carried closed, or open on the table
    c = latest(tl, "book", t)
    mode = c["mode"] if c else "open"
    bo, bc = ctx["book_open"], ctx["book_closed"]
    if mode == "open":
        hide_tree(bo, False)
        bo.location = (LECT[0], LECT[1], 0)
        bo.rotation_euler = (0, 0, 0)
        bc.location = (0, 0, -40)
    elif mode == "table":
        hide_tree(bo, False)
        bo.location = (500.0, 3.6, 0.81 - 0.95)
        bo.rotation_euler = (0, 0, 0)
        bc.location = (0, 0, -40)
    else:
        hide_tree(bo, True)
        p = track(tl, "bookpath", t)
        if p is None:
            p = [-2.6, 1.2, 1.05]
        bc.location = (p[0], p[1], p[2])
        bc.rotation_euler = (0, 0, 0)
    # ---- the book's spread
    c = latest(tl, "spread", t)
    for nm, ob in ctx["spreads"].items():
        ob.hide_render = not (c and c["n"] == nm)
    # ---- the stamp: on the lectern, or in Otis's right hand
    c = latest(tl, "stamp", t)
    st = ctx["stamp"]
    if c and c["mode"] == "hand" and "me" in rig.CHARS and not rig.CHARS["me"].root.hide_render:
        hp = hand_pos("me", 0, (0, -0.1, -1.72))
        st.location = (hp.x, hp.y, hp.z - 0.1)
        st.rotation_euler = (0, 0, 0)
        hide_tree(st, False)
    elif c and c["mode"] == "path" and track(tl, "stamppos", t):
        sp = track(tl, "stamppos", t)
        st.location = (sp[0], sp[1], sp[2])
        st.rotation_euler = (0, 0, 0)
        hide_tree(st, False)
    else:
        st.location = (0.82, LECT[1] + 0.15, 1.19)
        hide_tree(st, False)
        if mode != "open":
            st.location = (0, 0, -40)
    # ---- Milo's pencil
    pc = latest(tl, "pencil", t)
    pen = ctx["pencil"]
    if pc and pc["on"] and "milo" in rig.CHARS:
        hp = hand_pos("milo", 0, (0, -0.1, -1.7))
        pen.location = (hp.x, hp.y, hp.z)
        pen.rotation_euler = (0.5, 0, 0)
    else:
        pen.location = (0, 0, -40)
    # ---- the slip
    c = latest(tl, "slip", t)
    slip, slip3 = ctx["slip"], ctx["slip3"]
    slip.location = (0, 0, -40)
    slip.scale = (1.0, 1.0, 1.0)
    slip3.location = (0, 0, -40)
    face = latest(tl, "slipface", t)
    if c and c["mode"] == "path":
        p = track(tl, "slip", t) or c["v"]
        slip.location = (p[0], p[1], p[2])
        slip.rotation_euler = (0, 0, 0)
        slip.scale = (1.9, 1.9, 1.0) if p[0] > 450 else (1.0, 1.0, 1.0)
    elif c and c["mode"] == "hand" and "me" in rig.CHARS and not rig.CHARS["me"].root.hide_render:
        hp = hand_pos("me", 0, (0, -0.1, -1.72))
        if face and face["n"] == "three":
            slip3.location = (hp.x - 0.04, hp.y - 0.08, hp.z + 0.1)
            slip3.rotation_euler = basis((1, 0, 0), (0, 0, 1)).to_euler()
        else:
            slip.location = (hp.x, hp.y, hp.z + 0.02)
            slip.rotation_euler = (0, 0, 0)
    # ---- the torn leaf (rule three / four) and the folded one in the pocket
    c = latest(tl, "ppage", t)
    root, front, back = ctx["ppage"]
    fold = ctx["ppage_fold"]
    root.location = (0, 0, -40)
    fold.location = (0, 0, -40)
    me_ok = "me" in rig.CHARS and not rig.CHARS["me"].root.hide_render
    mode_p = c["mode"] if c else "pocket"
    unf = latest(tl, "ppage_unfold", t)
    uf = 1.0
    if unf:
        nxt = [x for x in cues_of(tl, "ppage_unfold") if x["t"] > unf["t"]]
        if nxt:
            u = ss((t - unf["t"]) / max(1e-6, nxt[0]["t"] - unf["t"]))
            uf = lerp(unf["u"], nxt[0]["u"], u)
        else:
            uf = unf["u"]
    fc = latest(tl, "ppage_face", t)
    showback = bool(fc and fc["n"] == "back")
    front.hide_render = showback
    back.hide_render = not showback
    if mode_p == "pocket":
        if me_ok:
            m = rig.CHARS["me"].upper.matrix_world
            fold.location = m @ V((0.6, -0.58, 1.3))
            fold.rotation_euler = rig.CHARS["me"].upper.matrix_world.to_euler()
    else:
        if mode_p == "hand" and me_ok:
            hp = hand_pos("me", 0, (0, -0.1, -1.72))
            root.location = (hp.x, hp.y - 0.12, hp.z + 0.16)
            root.rotation_euler = basis((1, 0, 0), (0, 0, 1)).to_euler()
        elif mode_p == "world":
            p = track(tl, "ppage", t) or c["v"]
            root.location = (p[0], p[1], p[2])
            root.rotation_euler = (math.radians(90 + p[4]), 0, math.radians(p[3]))
            if showback:   # lying flat, face up: turn the sheet over so the back (the 4) is the face we see
                root.rotation_euler = (math.radians(90 + p[4]) + math.pi, 0, math.radians(p[3]))
        root.scale = (0.28 + 0.72 * uf, 1.0, 1.0)
    if mode_p == "pocket":
        root.scale = (1, 1, 1)
    # ---- the whole cake is gone once the last slice is on its plate
    if "cake" in ctx:
        ctx["cake"].location = (500.0 + 1.2, 3.8, -40 if latest(tl, "cakegone", t) else 0.81)
    # ---- the plate
    c = latest(tl, "plate", t)
    pl = ctx["plate"]
    pv = track(tl, "plate", t)
    pl.location = tuple(pv) if (c and c.get("v") is not None and pv) else (0, 0, -40)
    pl.scale = (2.0, 2.0, 2.0)
    # ---- the sleeve pushing a slip through the slot
    c = latest(tl, "sleeve", t)
    sl = ctx["sleeve"]
    if c and c["on"]:
        p = track(tl, "slip", t)
        y = (p[1] if p else -0.34) - 0.1
        sl.location = (-2.6, y, 1.1)
    else:
        sl.location = (0, 0, -40)
    # ---- the door
    d = track(tl, "door", t)
    ctx["door"].rotation_euler = (0, 0, math.radians(d[0] if d else 0.0)) if isinstance(d, list) else (0, 0, 0)
    # ---- the rule meter: a cream tag in the top-left corner of every shot, parented to the camera
    piv, front, back = ctx["tag"]
    lens = lens_at(story, tl, t)
    dist = 0.4
    half_h = dist * 12.0 / lens
    half_w = half_h * 9 / 16
    tc = latest(tl, "tag", t)
    flip = 0.0
    if tc:
        flip = ss((t - tc["t"]) / max(0.05, tc.get("dur", 0.4))) * tc["v"]
    tw = 0.26 * 2 * half_w
    front.scale = (tw, tw * 240 / 360, 1)
    back.scale = (tw, tw * 300 / 360, 1)
    front.location = (0, -tw * 240 / 360 / 2, 0)
    back.location = (0, tw * 300 / 360 / 2, 0)
    px = -half_w + 0.04 * 2 * half_w + tw / 2
    py = half_h - 0.075 * 2 * half_h
    piv.location = (px, py, -dist)
    piv.rotation_euler = (math.pi * flip, 0, 0)
    front.hide_render = flip > 0.5
    back.hide_render = flip <= 0.5
    return over
