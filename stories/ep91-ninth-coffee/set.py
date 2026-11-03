"""ep91-ninth-coffee: every coffee makes you twice as fast; the ten-cuppers are the frozen cyan streaks doing the work.

One bright open-plan office in afternoon sun (the "closer" look): a tan carpet, cream walls, big windows, cream standing
desks in three rows, espresso chairs, plants, a wall clock with hands only and a shiny two-spout coffee machine on an
island counter. No text anywhere: the machine's spouts, the monitors, the notes and the meter use glyphs and numerals.

Built here from kit.py's parts:
- THE METER: a panel glued to the camera, top right, in every shot. A cup glyph, a big multiplier (x1 ... x1024) and
  nine (or ten) cup ticks. A second row (cue "meter" with "other") shows a ten-cupper's or Kai's meter.
- CUPS: a pool of twenty paper cups (c0..c9 brown sleeve, d0..d9 sage sleeve) placed by the "cups" cue, with frozen steam.
- THE STREAKS: one frozen smear of electric cyan behind each ten-cupper (tc1..tc5 and Kai). It is placed from the
  character's own acting (position and facing), so it always trails behind them. Length comes from the "streaks" cue.
- THE OFFICE: desks with trays, monitors showing colour blocks, my monitor's scorched sticky notes in Kai's hand, Kai's
  neat desk (jacket on the chair, photo, pens in a line), a mess group, a clock, an elevator, a lunch table.
Cues (story.json "cues", each restates its whole state): meter, cups, pour, typing, streaks, screen, clock, elev, mess,
paper, sneeze, note, jacket, beard, cal, drop.
"""

from __future__ import annotations

import math
import random
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import acting as actmod
from blocky import bl_story, faces, rig

TMP = Path(tempfile.mkdtemp(prefix="ninthcoffee-"))
FONT = Path(faces.__file__).resolve().parent / "fonts" / "SchibstedGrotesk-Black.ttf"

CREAM, ESP, CYAN, TEAL, MUST = "#f6e6c8", "#5a3a24", "#22e6ff", "#2fa59a", "#e7b53b"
DESKZ = 1.005          # the top of every desk
MX, MY = 4.4, -4.0     # the coffee machine (on the island counter)
CTOP = 0.95            # the island counter's top
TC = ("tc1", "tc2", "tc3", "tc4", "tc5", "kai")

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


class K:
    kit = None


def P(hexc, rough=0.5, spec=0.35):
    return K.kit.plastic(hexc, rough, spec=spec)


def B(parent, size, loc, mat, name="b", bevel=0.01, rot=(0, 0, 0)):
    return K.kit.box(nm(name), size, loc, mat, parent, rot, bevel)


def E(parent, loc=(0, 0, 0), name="e", rot=(0, 0, 0)):
    return K.kit.empty(nm(name), loc, parent, rot)


def no_shadow(ob):
    try:
        ob.visible_shadow = False
    except Exception:
        pass


def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


def cue_at(tl, name, t):
    out = {}
    for c in tl.get("cues", []):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c
    return out


def keyed(tl, name, t, field, default):
    """A value keyed by cues of one name: linear between the cue before t and the next one."""
    cs = [c for c in tl.get("cues", []) if c["name"] == name and field in c]
    if not cs:
        return default
    prev = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            prev = c
        else:
            if prev is None:
                return c[field]
            u = (t - prev["t"]) / max(1e-6, c["t"] - prev["t"])
            return lerp(prev[field], c[field], u)
    return prev[field] if prev else default


# ------------------------------------------------------------------------------------------------ materials
def clear_nodes(m):
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    return nt, next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")


def img_mat(path, emit=0.0, rough=0.6):
    """A material that shows a picture: lit plastic, or glowing (screens, the meter)."""
    kit = K.kit
    m = kit._new(nm("img"))
    nt = m.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    gc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
    im = bpy.data.images.load(str(path))
    im.colorspace_settings.name = "sRGB"
    tex.image = im
    if emit:
        nt, out = clear_nodes(m)
        tex = nt.nodes.new("ShaderNodeTexImage")
        gc = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
        tex.image = im
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = emit
        nt.links.new(tex.outputs["Color"], em.inputs["Color"])
        nt.links.new(em.outputs[0], out.inputs["Surface"])
    else:
        b = nt.nodes["Principled BSDF"]
        b.inputs["Roughness"].default_value = rough
        nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
        kit._fogged(m, b.outputs[0])
    return m, tex, im


def ghost(hexc, alpha, emit=0.9):
    """A soft see-through glow (steam, a sneeze cloud, smoke)."""
    kit = K.kit
    m = kit._new(nm("ghost"))
    nt, out = clear_nodes(m)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col(hexc)
    em.inputs["Strength"].default_value = emit
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs[0].default_value = alpha
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return m


def streak_material():
    """Electric cyan fading to pale cyan and to nothing along the mesh's local +y (0 at the head, 1 at the tail), with
    soft bands across it like afterimages. Smooth and still: nothing here changes with time."""
    kit = K.kit
    m = kit._new(nm("streak"))
    nt, out = clear_nodes(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.clamp = True
    nt.links.new(sep.outputs["Y"], mr.inputs["Value"])

    def mth(op, a=None, b=None):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                nt.links.new(v, n.inputs[i])
        return n.outputs[0]

    u = mr.outputs["Result"]
    inv = mth("SUBTRACT", 1.0, u)
    fall = mth("POWER", inv, 0.55)
    band = mth("ADD", mth("MULTIPLY", mth("SINE", mth("MULTIPLY", u, 38.0)), 0.1), 0.9)
    alpha = mth("MULTIPLY", mth("MULTIPLY", fall, band), 0.9)
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs[6].default_value = kit.col("#00d8ff")
    mix.inputs[7].default_value = kit.col("#7aeeff")
    nt.links.new(mth("MULTIPLY", u, u), mix.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 0.65
    nt.links.new(mix.outputs[2], em.inputs["Color"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(alpha, mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return m


def frustum(verts, faces_, x0, x1, z0, z1, xt0, xt1, zt0, zt1):
    """A box-like smear: the head end at y 0, the tail end at y 1, narrower at the tail."""
    b = len(verts)
    verts += [(x0, 0, z0), (x1, 0, z0), (x1, 0, z1), (x0, 0, z1), (xt0, 1, zt0), (xt1, 1, zt0), (xt1, 1, zt1), (xt0, 1, zt1)]
    faces_ += [(b, b + 3, b + 2, b + 1), (b + 4, b + 5, b + 6, b + 7), (b, b + 1, b + 5, b + 4),
               (b + 1, b + 2, b + 6, b + 5), (b + 2, b + 3, b + 7, b + 6), (b + 3, b, b + 4, b + 7)]


def make_streak(mat):
    """Slender light-trail ribbons from the head, chest, arms, waist and legs (gaps between them, so it reads as a smear
    of motion and not a glass box). Head end at y 0, tail at y 1."""
    v, f = [], []
    for (x0, x1, z0, z1, xt0, xt1, zt0, zt1) in (
            (-0.27, 0.27, 1.98, 2.34, -0.33, 0.33, 2.06, 2.22),     # head
            (-0.52, 0.52, 1.52, 1.92, -0.62, 0.62, 1.62, 1.8),      # chest
            (-1.0, -0.5, 1.28, 1.62, -1.25, -0.7, 1.4, 1.5),        # left arm
            (0.5, 1.0, 1.28, 1.62, 0.7, 1.25, 1.4, 1.5),            # right arm
            (-0.46, 0.46, 0.92, 1.3, -0.56, 0.56, 1.0, 1.18),       # waist
            (-0.46, -0.04, 0.0, 0.88, -0.62, -0.1, 0.3, 0.55),      # left leg
            (0.04, 0.46, 0.0, 0.88, 0.1, 0.62, 0.3, 0.55)):         # right leg
        frustum(v, f, x0, x1, z0, z1, xt0, xt1, zt0, zt1)
    ob = K.kit.mesh_obj(nm("streak"), v, f, mat, None)
    no_shadow(ob)
    return ob


# ------------------------------------------------------------------------------------------------ pictures (PIL)
def _font(sz):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(str(FONT), sz)
    except Exception:
        return ImageFont.load_default()


def draw_cup(d, cx, cy, s, fill, outline=None, w=0):
    """A paper cup glyph, s wide, 1.1 s tall, with a sleeve band."""
    top, bot = s * 0.50, s * 0.38
    h = s * 0.55
    pts = [(cx - top, cy - h), (cx + top, cy - h), (cx + bot, cy + h), (cx - bot, cy + h)]
    d.polygon(pts, fill=fill, outline=outline, width=w)


def draw_star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def meter_png(e, ticks, other=None):
    from PIL import Image, ImageDraw
    key = f"meter-{e}-{ticks}-{other}"
    p = TMP / f"{key}.png"
    if p.exists():
        return str(p), (640, 300 * (2 if other else 1))
    rows = [("me", e, ticks)] + ([other] if other else [])
    W, RH = 640, 300
    im = Image.new("RGB", (W, RH * len(rows)), hexrgb("#3a2314"))
    d = ImageDraw.Draw(im)
    for i, (kind, ee, tk) in enumerate(rows):
        y0 = i * RH
        edge = {"me": "#fff3dc", "kai": TEAL, "ten": CYAN}[kind]
        d.rectangle([4, y0 + 4, W - 5, y0 + RH - 5], outline=hexrgb(edge), width=9)
        gcx, gcy = 112, y0 + 108
        if kind == "me":
            draw_cup(d, gcx, gcy, 118, hexrgb("#fff3dc"))
            d.rectangle([gcx - 52, gcy - 14, gcx + 52, gcy + 28], fill=hexrgb("#c97a3c"))
        elif kind == "kai":
            draw_star(d, gcx, gcy, 74, hexrgb(TEAL))
        else:
            d.polygon([(gcx - 78, gcy), (gcx + 12, gcy - 54), (gcx + 12, gcy + 54)], fill=hexrgb(CYAN))
            d.ellipse([gcx + 8, gcy - 34, gcx + 76, gcy + 34], fill=hexrgb("#e6fbff"))
        txt = "x" + str(2 ** ee)
        sz = 190
        f = _font(sz)
        while d.textlength(txt, font=f) > 410 and sz > 60:
            sz -= 8
            f = _font(sz)
        bb = d.textbbox((0, 0), txt, font=f)
        tx = 210 + (410 - (bb[2] - bb[0])) / 2 - bb[0]
        ty = y0 + 108 - (bb[3] - bb[1]) / 2 - bb[1]
        col = {"me": CYAN, "kai": "#ffffff", "ten": CYAN}[kind]
        d.text((tx, ty), txt, fill=hexrgb(col), font=f)
        n_slots = 10 if (tk > 9 or kind != "me") else 9
        step = 56
        x0 = (W - step * n_slots) / 2 + step / 2
        for k in range(n_slots):
            cx, cy = x0 + k * step, y0 + 232
            lit = k < tk
            if lit:
                draw_cup(d, cx, cy, 38, hexrgb(CYAN if kind != "kai" else "#ffffff"))
            else:
                draw_cup(d, cx, cy, 38, hexrgb("#3a2314"), hexrgb("#8a6a4a"), 3)
    im.save(p)
    return str(p), im.size


def glyph_png(kind):
    from PIL import Image, ImageDraw
    p = TMP / f"glyph-{kind}.png"
    if p.exists():
        return str(p)
    S = 256
    if kind == "brown":
        im = Image.new("RGB", (S, S), hexrgb("#fff3dc"))
        d = ImageDraw.Draw(im)
        draw_cup(d, 118, 128, 150, hexrgb(ESP))
        d.arc([158, 98, 222, 170], -90, 90, fill=hexrgb(ESP), width=14)
    elif kind == "hollow":
        im = Image.new("RGB", (S, S), hexrgb("#fff3dc"))
        d = ImageDraw.Draw(im)
        draw_cup(d, 118, 128, 150, hexrgb("#fff3dc"), hexrgb("#7ab58a"), 14)
        d.arc([158, 98, 222, 170], -90, 90, fill=hexrgb("#7ab58a"), width=14)
    elif kind == "deadline":
        im = Image.new("RGB", (S, S), hexrgb("#ff6a3d"))
        d = ImageDraw.Draw(im)
        d.polygon([(70, 40), (186, 40), (128, 128)], fill=hexrgb("#ffffff"))
        d.polygon([(70, 216), (186, 216), (128, 128)], fill=hexrgb("#ffffff"))
        d.rectangle([60, 28, 196, 42], fill=hexrgb("#ffffff"))
        d.rectangle([60, 214, 196, 228], fill=hexrgb("#ffffff"))
    elif kind == "blank":
        im = Image.new("RGB", (S, S), hexrgb("#eaf6ff"))
        d = ImageDraw.Draw(im)
        d.rectangle([30, 30, 36, 70], fill=hexrgb("#5a7a95"))
    elif kind == "arrow":
        im = Image.new("RGB", (S, S), hexrgb("#ffe27a"))
        d = ImageDraw.Draw(im)
        d.rectangle([100, 30, 156, 130], fill=hexrgb("#d6341f"))
        d.polygon([(52, 120), (204, 120), (128, 226)], fill=hexrgb("#d6341f"))
    elif kind.startswith("blocks"):
        k = int(kind[6:])
        rnd = random.Random(k * 7 + 1)
        im = Image.new("RGB", (S, S), hexrgb(["#dff3ff", "#fdf0d8", "#e3f6e8", "#f5e6ff"][k % 4]))
        d = ImageDraw.Draw(im)
        for _ in range(7):
            x, y = rnd.randint(8, 150), rnd.randint(8, 190)
            d.rectangle([x, y, x + rnd.randint(40, 100), y + rnd.randint(20, 60)],
                        fill=hexrgb(rnd.choice(["#ff8a3d", "#2fa59a", "#ffd23f", "#6aa8ff", "#ff5d8f", "#5fbf5a"])))
    elif kind == "scorch":
        im = Image.new("RGB", (S, S), hexrgb("#ffe27a"))
        d = ImageDraw.Draw(im)
        rnd = random.Random(5)
        for r_ in range(4):
            y = 54 + r_ * 36
            pts = [(30 + i * 22, y + rnd.randint(-10, 10)) for i in range(8)]
            d.line(pts, fill=hexrgb("#33261c"), width=6)
        draw_star(d, 190, 200, 24, hexrgb("#33261c"))
        for i in range(S):
            for j in range(0, 22):                                     # scorched right and bottom edges
                a = int(255 * (1 - j / 22) * 0.9)
                for (x, y) in ((S - 1 - j, i), (i, S - 1 - j)):
                    c = im.getpixel((x, y))
                    im.putpixel((x, y), tuple(int(c[k] * (1 - a / 255) + (60, 30, 12)[k] * (a / 255)) for k in range(3)))
    elif kind == "sheet":
        im = Image.new("RGB", (S, S), hexrgb("#ffffff"))
        d = ImageDraw.Draw(im)
        rnd = random.Random(9)
        for r_ in range(5):
            y = 40 + r_ * 34
            pts = [(24 + i * 26, y + rnd.randint(-9, 9)) for i in range(9)]
            d.line(pts, fill=hexrgb("#2b3f78"), width=5)
        draw_star(d, 206, 210, 22, hexrgb("#2b3f78"))
    elif kind == "photo":
        im = Image.new("RGB", (S, S), hexrgb("#ffe9b8"))
        d = ImageDraw.Draw(im)
        for (cx, skin, hair, shirt, glasses) in ((78, "#c68b5e", "#161416", TEAL, True), (178, "#f1c9a0", "#d4452c", "#f7f7f2", False)):
            d.rectangle([cx - 44, 150, cx + 44, 256], fill=hexrgb(shirt))
            d.ellipse([cx - 40, 52, cx + 40, 150], fill=hexrgb(skin))
            d.rectangle([cx - 42, 46, cx + 42, 86], fill=hexrgb(hair))
            if glasses:
                d.ellipse([cx - 30, 92, cx - 6, 116], outline=hexrgb("#222222"), width=4)
                d.ellipse([cx + 6, 92, cx + 30, 116], outline=hexrgb("#222222"), width=4)
            else:
                d.ellipse([cx - 22, 98, cx - 12, 110], fill=hexrgb("#222222"))
                d.ellipse([cx + 12, 98, cx + 22, 110], fill=hexrgb("#222222"))
            d.pieslice([cx - 20, 108, cx + 20, 142], 0, 180, fill=hexrgb("#7a1f1f"))
        draw_cup(d, 128, 226, 34, hexrgb("#fff3dc"))
    elif kind.startswith("cal"):
        k = int(kind[3:])
        im = Image.new("RGB", (S, S), hexrgb("#fffaf0"))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, S, 52], fill=hexrgb("#d6341f"))
        for r_ in range(6):
            for c_ in range(7):
                x, y = 14 + c_ * 33, 66 + r_ * 30
                done = r_ < k
                d.rectangle([x, y, x + 24, y + 20], fill=hexrgb("#2fa59a" if done else "#ddd2bd"))
    else:
        im = Image.new("RGB", (S, S), hexrgb("#ffffff"))
    im.save(p)
    return str(p)


# ------------------------------------------------------------------------------------------------ parts
def cup_obj(sleeve):
    """A paper cup, origin at the middle of its base."""
    kit = K.kit
    g = E(None, (0, 0, 0), "cup")
    kit.cyl(nm("cupbody"), 0.034, 0.13, (0, 0, 0.065), P("#fff8ea", 0.5), g, n=18, r2=0.048)
    kit.cyl(nm("cupsleeve"), 0.0415, 0.06, (0, 0, 0.062), P(sleeve, 0.6), g, n=18, r2=0.0475)
    kit.cyl(nm("cuplid"), 0.052, 0.014, (0, 0, 0.137), P("#4a2e1c", 0.5), g, n=18)
    st = []
    gh = ghost("#ffffff", 0.55, 1.1)
    for i in range(7):
        w = 0.03 - 0.002 * i
        o = kit.box(nm("steam"), (w, w, 0.06), (0.025 * math.sin(i * 1.3), 0.02 * math.cos(i * 1.7), 0.18 + 0.05 * i), gh, g,
                    (0.2 * math.sin(i), 0.15 * i, 0.3 * i), bevel=0.01)
        no_shadow(o)
        st.append(o)
    g["steam"] = [o.name for o in st]
    return g, st


def desk(x, y, idx, tray_top=False):
    kit = K.kit
    d = {}
    B(None, (1.5, 0.8, 0.05), (x, y, 0.98), P(CREAM, 0.5), "dtop", 0.012)
    B(None, (1.5, 0.03, 0.05), (x, y - 0.415, 0.98), P(ESP, 0.5), "dtrim", 0.006)
    for sx in (-1, 1):
        B(None, (0.04, 0.7, 0.95), (x + sx * 0.71, y, 0.475), P(ESP, 0.5), "dleg", 0.01)
    B(None, (1.42, 0.03, 0.4), (x, y + 0.36, 0.76), P(ESP, 0.5), "dback", 0.006)
    # the monitor: a stand, a frame and a glowing screen picture 1 cm proud of it
    mx, my = x + 0.1, y + 0.2
    B(None, (0.28, 0.18, 0.02), (mx, my, DESKZ + 0.005), P("#2a2a30", 0.4), "mbase", 0.005)
    B(None, (0.05, 0.04, 0.2), (mx, my, DESKZ + 0.11), P("#2a2a30", 0.4), "mneck", 0.005)
    B(None, (0.72, 0.05, 0.46), (mx, my, DESKZ + 0.39), P("#2a2a30", 0.4), "mframe", 0.01)
    m, tex, im = img_mat(glyph_png(f"blocks{idx}"), emit=0.9)
    scr = kit.plane(nm("screen"), (0.66, 0.4), (mx, my - 0.036, DESKZ + 0.39), m, None, rot=(math.pi / 2, 0, 0))
    no_shadow(scr)
    d["screen"] = (scr, tex)
    B(None, (0.42, 0.15, 0.02), (x - 0.05, y - 0.15, DESKZ + 0.005), P("#e8e8ee", 0.5), "kbd", 0.005)
    # the in-tray: an espresso tray with a stack of papers
    tx, ty = x + 0.58, y - 0.08
    B(None, (0.3, 0.24, 0.02), (tx, ty, DESKZ + 0.005), P(ESP, 0.5), "tray", 0.004)
    rnd = random.Random(idx * 13 + 3)
    for k in range(6):
        B(None, (0.21, 0.297, 0.018), (tx + rnd.uniform(-0.012, 0.012), ty + rnd.uniform(-0.012, 0.012), DESKZ + 0.025 + 0.019 * k),
          P(rnd.choice(["#ffffff", "#fffbe8", "#f2f8ff"]), 0.7, 0.1), "sheet", 0.002, rot=(0, 0, rnd.uniform(-0.05, 0.05)))
    if tray_top:
        sh = kit.plane(nm("topsheet"), (0.2, 0.28), (tx, ty, DESKZ + 0.025 + 0.019 * 6 + 0.012), img_mat(glyph_png("sheet"))[0], None)
        no_shadow(sh)
    return d


def chair(x, y, name="chair"):
    kit = K.kit
    g = E(None, (x, y, 0), name)
    esp = P(ESP, 0.5)
    B(g, (0.5, 0.5, 0.08), (0, 0, 0.5), esp, "seat", 0.025)
    B(g, (0.5, 0.07, 0.5), (0, -0.23, 0.82), esp, "cback", 0.025)
    kit.cyl(nm("cpole"), 0.03, 0.4, (0, 0, 0.26), kit.metal("#9a9da3"), g)
    kit.cyl(nm("cbase"), 0.27, 0.04, (0, 0, 0.04), P("#2a2a30", 0.5), g, n=5)
    return g


def clock(x, y, z, yaw=0.0):
    """A wall clock with hands only, face toward -y (turned by yaw about z)."""
    kit = K.kit
    g = E(None, (x, y, z), "clock", (0, 0, math.radians(yaw)))
    kit.cyl(nm("crim"), 0.31, 0.04, (0, -0.02, 0), P(ESP, 0.5), g, rot=(math.pi / 2, 0, 0), n=32)
    kit.cyl(nm("cface"), 0.27, 0.02, (0, -0.045, 0), P("#fffaf0", 0.5), g, rot=(math.pi / 2, 0, 0), n=32)
    for k in range(12):
        a = k * math.pi / 6
        big = k % 3 == 0
        B(g, (0.03 if big else 0.018, 0.012, 0.07 if big else 0.04), (0.22 * math.sin(a), -0.06, 0.22 * math.cos(a)), P("#2a2a30"), "tick",
          0.002, rot=(0, a, 0))
    hands = {}
    for nm_, ln, wd, dy, c in (("h", 0.15, 0.034, -0.075, "#2a2a30"), ("m", 0.23, 0.026, -0.09, "#2a2a30"), ("s", 0.25, 0.012, -0.105, "#d6341f")):
        piv = E(g, (0, dy, 0), "pivot")
        B(piv, (wd, 0.012, ln), (0, 0, ln / 2 - 0.02), P(c, 0.4), "hand", 0.003)
        hands[nm_] = piv
    return g, hands


def sticky(path, loc, rot_y):
    m = img_mat(path)[0]
    ob = K.kit.plane(nm("note"), (0.1, 0.1), loc, m, None, rot=(math.pi / 2, rot_y, 0))
    no_shadow(ob)
    return ob


def build(kit, story, tl):
    K.kit = kit
    ctx = {"story": story, "shots": {s["id"]: s for s in story["shots"]}}
    sc = bpy.context.scene
    cream = P("#fff0d4", 0.7, 0.1)
    espm = P(ESP, 0.5)

    # ---- lights: a sun through the walls, a soft area light overhead and a fill that follows the camera
    ctx["sun"] = kit.light("sun", "SUN", (0, 0, 50), 1.9, "#fff1d8", size=0.1)
    ctx["sun"].data.angle = 0.08
    ctx["fill"] = kit.light("camfill", "POINT", (0, 0, 2), 22, "#fff0dc", size=0.5, shadow=False)
    ctx["roomfill"] = kit.light("roomfill", "AREA", (0, 3.0, 3.3), 160, "#fff4e4", size=10.0)
    ctx["roomfill"].data.size_y = 16.0

    # ---- the room
    B(None, (22, 20, 0.2), (0, 2.5, -0.1), P("#e2c08c", 0.6, 0.2), "floor", 0.0)
    for k in range(-5, 6):                                                       # carpet tile lines
        B(None, (0.03, 19, 0.004), (k * 2.0, 2.5, 0.002), P("#d4af78", 0.7, 0.1), "tile", 0.0)
    B(None, (21, 0.3, 3.5), (0, 12.15, 1.75), cream, "wallB", 0.0)
    B(None, (21, 0.3, 3.5), (0, -7.15, 1.75), cream, "wallF", 0.0)
    B(None, (0.3, 20, 3.5), (-10.15, 2.5, 1.75), cream, "wallL", 0.0)
    B(None, (0.3, 7.2, 3.5), (10.15, -3.5, 1.75), cream, "wallR1", 0.0)         # right wall, with the elevator gap y 1.1..2.9
    B(None, (0.3, 9.1, 3.5), (10.15, 7.45, 1.75), cream, "wallR2", 0.0)
    B(None, (0.3, 1.8, 1.1), (10.15, 2.0, 2.95), cream, "wallR3", 0.0)
    ceil = B(None, (21, 20, 0.1), (0, 2.5, 3.55), kit.emit("#fff6e6", 0.45, name="ceiling"), "ceil", 0.0)
    no_shadow(ceil)
    for bx in (-6.0, -2.0, 2.0, 6.0):
        lb = B(None, (0.35, 16, 0.03), (bx, 3.0, 3.485), kit.emit("#fffdf5", 1.2, name="ceilbar"), "ceilbar", 0.0)
        no_shadow(lb)
    for ob in ctx.get("walls", []):
        no_shadow(ob)
    for o in bpy.data.objects:
        if o.name.startswith(("wallB", "wallF", "wallL", "wallR")):
            no_shadow(o)
    for sx in (-1, 1):                                                           # baseboards
        B(None, (0.04, 19, 0.12), (sx * 9.98, 2.5, 0.06), espm, "base", 0.0)
    B(None, (20, 0.04, 0.12), (0, 11.98, 0.06), espm, "base", 0.0)
    # windows: a sky picture 1 cm proud of the wall, white mullions 2 cm proud
    ctx["winmat"] = kit.emit("#a9dcff", 0.85, name="window")
    white = P("#ffffff", 0.5)

    def window(wall, c, w):
        h, zc = 1.9, 1.9
        if wall == "B":
            B(None, (w, 0.01, h), (c, 11.99, zc), ctx["winmat"], "win", 0.0)
            B(None, (0.06, 0.03, h + 0.08), (c, 11.975, zc), white, "mull", 0.0)
            B(None, (w + 0.08, 0.03, 0.06), (c, 11.975, zc), white, "mull", 0.0)
            B(None, (w + 0.2, 0.12, 0.05), (c, 11.93, zc - h / 2 - 0.03), white, "sill", 0.0)
        else:
            sx = -1 if wall == "L" else 1
            B(None, (0.01, w, h), (sx * 9.99, c, zc), ctx["winmat"], "win", 0.0)
            B(None, (0.03, 0.06, h + 0.08), (sx * 9.975, c, zc), white, "mull", 0.0)
            B(None, (0.03, w + 0.08, 0.06), (sx * 9.975, c, zc), white, "mull", 0.0)
            B(None, (0.12, w + 0.2, 0.05), (sx * 9.93, c, zc - h / 2 - 0.03), white, "sill", 0.0)

    for c in (-6.5, 6.5):
        window("B", c, 5.0)
    for c in (-3.0, 4.0, 9.0):
        window("L", c, 4.2)
    for c in (-4.0, 7.0):
        window("R", c, 4.2)

    # ---- the desks (three rows facing +y), their chairs, the plants
    ctx["desks"] = {}
    idx = 0
    for ry, xs in ((0.0, (-5.2, -2.6, 0.0, 2.6, 5.2)), (4.2, (-3.9, -1.3, 1.3, 3.9)), (8.4, (-5.2, -2.6, 0.0, 2.6, 5.2))):
        for x in xs:
            ctx["desks"][(x, ry)] = desk(x, ry, idx, tray_top=(x == 0.0 and ry == 0.0))
            if ry < 5:
                chair(x + (0.9 if ry == 0 else -0.9), ry - 1.45 if ry == 0 else ry - 1.6, "chr")
            idx += 1
    # my screen swaps picture: work / blank / deadline
    scr, tex = ctx["desks"][(0.0, 0.0)]["screen"]
    ctx["mscr"] = tex
    ctx["mscr_imgs"] = {}
    # chairs to the side of mine and Kai's: Kai's carries the jacket
    ctx["kchair"] = chair(2.6, -1.4, "kchair")
    jg = E(None, (2.6, -1.4, 0), "jacket")
    jc = P("#238a80", 0.7, 0.1)
    B(jg, (0.54, 0.1, 0.56), (0, -0.28, 0.84), jc, "jback", 0.04)
    B(jg, (0.52, 0.42, 0.05), (0, -0.02, 0.57), jc, "jseat", 0.03)
    for sx in (-1, 1):
        B(jg, (0.13, 0.1, 0.42), (sx * 0.3, -0.3, 0.78), jc, "jsleeve", 0.04)
    ctx["jacket"] = jg
    chair(0.0, -1.4, "mchair")
    # Kai's desk: the photo, the pens in a line
    pf = E(None, (2.05, 0.18, DESKZ), "photo")
    B(pf, (0.26, 0.03, 0.22), (0, 0, 0.12), espm, "pframe", 0.006, rot=(-0.12, 0, 0))
    ph = kit.plane(nm("photo"), (0.2, 0.17), (0, -0.0225, 0.12), img_mat(glyph_png("photo"), rough=0.4)[0], pf, rot=(math.pi / 2 - 0.12, 0, 0))
    no_shadow(ph)
    for i, c in enumerate(("#2b3f78", "#d6341f", "#2b3f78", "#d6341f", "#2b3f78", "#d6341f")):
        kit.cyl(nm("pen"), 0.007, 0.15, (2.25 + 0.03 * i, -0.22, DESKZ + 0.008), P(c, 0.4), None, rot=(math.pi / 2, 0, 0), n=8)
    # my sticky notes, in Kai's hand, scorched at the edge: on my monitor's lower left
    for (nx, nz, ry) in ((-0.13, 1.33, 0.08), (-0.02, 1.27, -0.1), (-0.17, 1.45, -0.05)):
        sticky(glyph_png("scorch"), (0.1 + nx, 0.2 - 0.059, nz), ry)
    # the new note (S35): arrow, appears by cue
    ctx["note"] = sticky(glyph_png("arrow"), (0.1 + 0.2, 0.2 - 0.059, 1.52), 0.04)
    ctx["note"].scale = (1.5, 1.5, 1.5)
    gh = ghost("#8a8f98", 0.5, 0.45)
    ctx["smoke"] = []
    for i in range(6):
        o = kit.sphere(nm("smoke"), 0.03, (0.3, 0.12, 1.6), gh, None, seg=8)
        no_shadow(o)
        ctx["smoke"].append(o)
    # a mess group at the desk to my left (x -2.6): papers, a tipped cup, shown by cue
    mg = E(None, (-2.6, 0.0, DESKZ), "mess")
    rnd = random.Random(21)
    for i in range(9):
        B(mg, (0.21, 0.297, 0.004), (rnd.uniform(-0.6, 0.5), rnd.uniform(-0.28, 0.25), 0.003 * i + 0.01),
          P(rnd.choice(["#ffffff", "#fffbe8", "#f2f8ff"]), 0.7, 0.1), "mpaper", 0.0, rot=(0, 0, rnd.uniform(-1.2, 1.2)))
    B(mg, (0.12, 0.2, 0.012), (0.2, -0.18, 0.02), P(ESP), "mcup", 0.004)
    ctx["mess"] = mg
    # plants
    for (px, py, hh) in ((-9.2, -5.8, 1.3), (9.2, -5.8, 1.3), (-9.2, 11.0, 1.4), (9.2, 11.0, 1.4), (-7.6, 4.2, 1.1), (7.6, 4.2, 1.1),
                         (-8.2, -1.2, 1.0), (7.6, -1.4, 1.0), (-1.3, 11.2, 1.2), (1.3, 11.2, 1.2), (6.5, 8.4, 1.1)):
        try:
            kit.prop("houseplant_1", (px, py, 0), height=hh)
        except Exception:
            kit.cyl(nm("plant"), 0.2, hh, (px, py, hh / 2), P("#5fbf5a", 0.7), None)
    # a filing cabinet on the left wall
    fc = P("#8fa6b8", 0.4)
    B(None, (0.5, 0.7, 1.3), (-9.6, 3.0, 0.65), fc, "cabinet", 0.02)
    for k in range(3):
        B(None, (0.02, 0.5, 0.3), (-9.34, 3.0, 0.25 + 0.4 * k), P("#6f8497", 0.4), "drawer", 0.01)
        B(None, (0.02, 0.2, 0.03), (-9.32, 3.0, 0.3 + 0.4 * k), kit.metal("#cfd3d8"), "handle", 0.005)

    # ---- the clocks (hour 3:00 at the back wall, a small one at the lunch spot)
    g, ctx["hands"] = clock(0.0, 11.99, 2.55)
    g2, ctx["hands2"] = clock(9.97, 7.5, 2.4, yaw=-90)

    # ---- the coffee machine on its island
    B(None, (2.6, 0.9, CTOP), (MX, MY, CTOP / 2), P("#8fd0c8", 0.5), "island", 0.02)
    B(None, (2.7, 1.0, 0.05), (MX, MY, CTOP + 0.0), P("#fff3dc", 0.4), "islandtop", 0.01)
    chrome = kit.metal("#cfd5dc", 0.18)
    B(None, (0.95, 0.6, 0.85), (MX, MY + 0.05, CTOP + 0.025 + 0.425), chrome, "machine", 0.025)
    B(None, (1.0, 0.64, 0.12), (MX, MY + 0.05, CTOP + 0.025 + 0.91), P(ESP, 0.4), "mtop", 0.02)
    fy = MY + 0.05 - 0.3                                                         # the machine's front face
    B(None, (0.8, 0.22, 0.34), (MX, fy - 0.1, CTOP + 0.025 + 0.58), P("#2a2a30", 0.35), "head", 0.02)     # the brew head
    for sx in (-1, 1):
        B(None, (0.1, 0.12, 0.1), (MX + sx * 0.2, fy - 0.17, CTOP + 0.025 + 0.4), chrome, "spout", 0.02)
        B(None, (0.03, 0.03, 0.06), (MX + sx * 0.2, fy - 0.17, CTOP + 0.025 + 0.31), chrome, "nozzle", 0.008)
    ctx["spouts"] = (MX - 0.2, fy - 0.17, CTOP + 0.025 + 0.28)
    for sx, gk in ((-1, "brown"), (1, "hollow")):                                  # the glyph plates, 1.2 cm proud
        pl = kit.plane(nm("gplate"), (0.3, 0.3), (MX + sx * 0.2, fy - 0.012, CTOP + 0.025 + 0.64), img_mat(glyph_png(gk), rough=0.35)[0], None,
                       rot=(math.pi / 2, 0, 0))
        no_shadow(pl)
    B(None, (0.9, 0.36, 0.04), (MX, fy - 0.19, CTOP + 0.045), P("#6f7378", 0.3), "tray", 0.01)        # the drip tray
    ctx["tray_top"] = CTOP + 0.065
    cy_ = P(CYAN, 0.4)
    for i in range(2):                                                           # lore: two cyan strokes on the tray's lip
        o = kit.box(nm("tally"), (0.012, 0.012, 0.045), (MX + 0.32 + 0.032 * i, fy - 0.19 - 0.18 - 0.006, CTOP + 0.045), kit.emit(CYAN, 1.6, name="tally"), None)
        no_shadow(o)
    # a counter plant
    # ---- the pour stream
    ctx["pour"] = kit.box(nm("pour"), (0.012, 0.012, 1.0), (0, 0, 0), P("#3a2314", 0.3), None)
    no_shadow(ctx["pour"])
    ctx["drop"] = kit.sphere(nm("drop"), 0.014, (0, 0, 0), P("#3a2314", 0.3), None, seg=8)
    no_shadow(ctx["drop"])

    # ---- the elevator on the right wall (y 1.1..2.9)
    ctx["elev"] = []
    steel = kit.metal("#b8bfc8", 0.3)
    B(None, (0.3, 0.1, 2.5), (9.88, 1.05, 1.25), espm, "eframe", 0.01)
    B(None, (0.3, 0.1, 2.5), (9.88, 2.95, 1.25), espm, "eframe", 0.01)
    B(None, (0.3, 2.0, 0.1), (9.88, 2.0, 2.5), espm, "eframe", 0.01)
    B(None, (1.2, 1.9, 2.4), (10.8, 2.0, 1.2), kit.emit("#fff0d0", 0.9, name="shaft"), "shaft", 0.0)
    for s_ in (-1, 1):
        dr = B(None, (0.06, 0.9, 2.4), (9.8, 2.0 + s_ * 0.45, 1.2), steel, "edoor", 0.01)
        ctx["elev"].append((dr, s_))
    btn = kit.cyl(nm("ebtn"), 0.05, 0.02, (9.86, 3.15, 1.2), kit.emit(CYAN, 1.5, name="ebtn"), None, rot=(0, math.pi / 2, 0), n=16)

    # ---- the lunch spot: a round table by the right-hand window, two sandwiches, the calendar glyph
    kit.cyl(nm("ltop"), 0.62, 0.05, (7.2, 7.5, 0.76), P("#fff3dc", 0.4), None, n=32)
    kit.cyl(nm("lpole"), 0.07, 0.75, (7.2, 7.5, 0.375), kit.metal("#9a9da3"), None)
    kit.cyl(nm("lbase"), 0.32, 0.04, (7.2, 7.5, 0.02), P("#2a2a30", 0.5), None, n=24)
    bread, fill = P("#e2b374", 0.7, 0.1), P("#6fc15a", 0.7, 0.1)
    for (sx_, sy_) in ((6.6, 7.5), (7.8, 7.5)):
        sg = E(None, (sx_, sy_, 0.8), "sandwich")
        B(sg, (0.2, 0.16, 0.04), (0, 0, 0.0), bread, "bread", 0.012)
        B(sg, (0.21, 0.17, 0.025), (0, 0, 0.032), fill, "filling", 0.01)
        B(sg, (0.2, 0.16, 0.04), (0, 0, 0.064), bread, "bread", 0.012)
    ctx["cal"] = []
    cm = E(None, (7.2, 7.5, 0.79), "cal")
    for k in range(7):
        pl = kit.plane(nm("calpage"), (0.3, 0.3), (0, 0, 0.0), img_mat(glyph_png(f"cal{k}"), rough=0.5)[0], cm)
        pl.rotation_euler = (math.radians(-80), 0, 0)
        pl.location = (0, 0, 0.16)
        no_shadow(pl)
        ctx["cal"].append(pl)

    # ---- the cups, the sneeze cloud, the paper in the air
    ctx["cups"] = {}
    for i in range(10):
        ctx["cups"][f"c{i}"] = cup_obj("#8a5a34")
        ctx["cups"][f"d{i}"] = cup_obj("#7ab58a")
    ctx["cloud"] = []
    gc = ghost("#ffffff", 0.5, 1.0)
    rnd = random.Random(2)
    for i in range(10):
        o = kit.sphere(nm("cloud"), rnd.uniform(0.03, 0.07), (0, 0, 0), gc, None, seg=8)
        no_shadow(o)
        ctx["cloud"].append((o, (rnd.uniform(-0.18, 0.18), rnd.uniform(0.12, 0.5), rnd.uniform(-0.12, 0.14))))
    ctx["paper"] = []
    for i in range(3):
        o = B(None, (0.21, 0.297, 0.003), (0, 0, 0), P("#ffffff", 0.6, 0.1), "flypaper", 0.0, rot=(0.3 * i + 0.2, 0.5 - 0.3 * i, 0.4 * i))
        ctx["paper"].append((o, (0.22 * i - 0.22, 0.05 * i, 0.12 * i - 0.1)))

    # ---- the streaks (one per ten-cupper, placed from their acting each frame)
    smat = streak_material()
    ctx["streaks"] = {n: make_streak(smat) for n in TC}
    ctx["tclights"] = {n: kit.light(f"tcglow_{n}", "POINT", (0, 0, 2), 60, CYAN, size=0.4, shadow=False) for n in TC}
    # a beard for me (S42a), hidden until the cue
    ctx["late"] = False
    ctx["inset_imgs"] = {}
    build_inset(kit, ctx)
    ctx["mscr_cur"] = None
    return ctx


def late_init(kit, ctx):
    """Things that need the cast built (the rig is made after build)."""
    ch = rig.CHARS.get("me")
    ctx["beard"] = []
    if ch is not None:
        hg = bpy.data.objects.get("me.headg")
        if hg is not None:
            R, H = faces.HEAD_R, faces.HEAD_H
            bm = P("#7a3a22", 0.8, 0.1)
            for sx in (-1, 1):
                ctx["beard"].append(kit.box(nm("beard"), (0.2, 0.36, 0.5), (sx * (R - 0.12), -R + 0.34, -0.12), bm, hg, bevel=0.05))
            ctx["beard"].append(kit.box(nm("beard"), (0.55, 0.26, 0.22), (0.0, -R + 0.07, -0.5), bm, hg, bevel=0.06))
            for o in ctx["beard"]:
                o.hide_render = True


# ------------------------------------------------------------------------------------------------ the looks
LOOKS = {
    "day": {"az": -35, "el": 52, "sun": 1.0, "col": "#fff1d8", "win": "#a9dcff", "winst": 0.85, "exp": 0.0, "room": 1.0},
    "eve": {"az": -75, "el": 14, "sun": 0.9, "col": "#ffb36b", "win": "#ffb070", "winst": 1.3, "exp": 0.0, "room": 0.85},
    "year": {"az": -55, "el": 30, "sun": 0.95, "col": "#ffd9a0", "win": "#ffe0b0", "winst": 1.2, "exp": 0.0, "room": 0.95},
}


def mixc(a, b, u):
    ra, rb = hexrgb(a), hexrgb(b)
    return tuple(lerp(x, y, u) / 255.0 for x, y in zip(ra, rb))


def look_at(ctx, tl, t):
    shots = tl["shots"]
    cur = next((s for s in shots if s["start"] <= t < s["end"]), shots[-1])
    i = shots.index(cur)
    A = LOOKS[ctx["shots"][cur["id"]].get("look", "day")]
    if i + 1 < len(shots) and t > cur["end"] - 0.3:
        nb = LOOKS[ctx["shots"][shots[i + 1]["id"]].get("look", "day")]
        if nb is not A:
            u = ss((t - (cur["end"] - 0.3)) / 0.3)
            return {k: (mixc(A[k], nb[k], u) if isinstance(A[k], str) else lerp(A[k], nb[k], u)) for k in A}, cur
    return {k: (hexrgb(A[k]) and tuple(c / 255.0 for c in hexrgb(A[k])) if isinstance(A[k], str) else A[k]) for k in A}, cur


def srgb3(kit, c):
    return (kit.srgb(c[0]), kit.srgb(c[1]), kit.srgb(c[2]))


def animate(kit, story, tl, t, ctx):
    if not ctx["late"]:
        late_init(kit, ctx)
        ctx["late"] = True
    sc = bpy.context.scene
    L, cur = look_at(ctx, tl, t)
    sd = ctx["shots"][cur["id"]]
    # ---- sun and windows
    azr, elr = math.radians(L["az"]), math.radians(L["el"])
    pos = V((math.sin(azr) * math.cos(elr), -math.cos(azr) * math.cos(elr), math.sin(elr)))
    sun = ctx["sun"]
    sun.rotation_euler = (-pos).to_track_quat("-Z", "Y").to_euler()
    sun.data.color = srgb3(kit, L["col"])
    for nd in ctx["winmat"].node_tree.nodes:
        if nd.type == "EMISSION":
            nd.inputs["Color"].default_value = (*srgb3(kit, L["win"]), 1.0)
            nd.inputs["Strength"].default_value = L["winst"]
    cl, _, cl_lens, _ = bl_story.cam_at(sd, cur, t, {}, tl)
    ctx["fill"].location = (cl[0], cl[1], cl[2] + 0.2)
    sc.view_settings.exposure = L["exp"] + sd.get("exp", 0.0)
    ov = {"sun": L["sun"] * sd.get("sun", 1.0), "camfill": sd.get("fill", 1.0), "roomfill": L["room"]}
    cd = kit.OBJ["cam"].data
    cd.dof.use_dof = False

    # ---- the meter
    mc = cue_at(tl, "meter", t)
    e, tk = mc.get("e", 0), mc.get("ticks", 0)
    other = None
    oe = keyed(tl, "meter", t, "oe", None)
    if mc.get("other"):
        oe_ = mc.get("oe", 10)
        # the second row steps down by cues (oe, oticks), each one restating the whole meter
        other = (mc["other"], int(round(oe_)), int(mc.get("oticks", 10)))
    place_inset(kit, ctx, e, tk, other, cl_lens)

    # ---- my screen
    sn = cue_at(tl, "screen", t).get("pic", "blocks0")
    if sn != ctx["mscr_cur"]:
        if sn not in ctx["mscr_imgs"]:
            im = bpy.data.images.load(glyph_png(sn))
            im.colorspace_settings.name = "sRGB"
            ctx["mscr_imgs"][sn] = im
        ctx["mscr"].image = ctx["mscr_imgs"][sn]
        ctx["mscr_cur"] = sn

    # ---- the cups and their steam
    cc = cue_at(tl, "cups", t)
    for name, (g, st) in ctx["cups"].items():
        spec = cc.get(name)
        if not spec:
            hide(g, True)
            continue
        hide(g, False)
        g.location = tuple(spec[:3])
        g.rotation_euler = (0, 0, 0)
        steam = len(spec) > 3 and spec[3]
        for o in st:
            o.hide_render = not steam
    # ---- the pour stream, and the drop at the decaf spout
    pc = cue_at(tl, "pour", t)
    po = ctx["pour"]
    if pc.get("on"):
        sx, sy, sz = ctx["spouts"]
        ox = 0.4 if pc.get("side") == "decaf" else 0.0
        top, bot = sz, pc.get("to", ctx["tray_top"] + 0.1)
        po.hide_render = False
        po.location = (sx + ox, sy, (top + bot) / 2)
        po.scale = (1, 1, max(0.01, top - bot))
    else:
        po.hide_render = True
    dc = cue_at(tl, "drop", t)
    dr = ctx["drop"]
    if dc.get("on"):
        sx, sy, sz = ctx["spouts"]
        ph = ((t - dc["t"]) % 0.8) / 0.8
        z = sz - 0.02 - 0.5 * 9.8 * (ph * 0.45) ** 2 * (1.0 if ph > 0.25 else 0.0) - (0.0 if ph > 0.25 else 0.0)
        if ph < 0.25:
            dr.scale = (ph * 4, ph * 4, ph * 4 * 1.3)
            z = sz - 0.015
        else:
            dr.scale = (1, 1, 1.4)
            z = sz - 0.015 - 0.5 * 9.8 * ((ph - 0.25) * 0.5) ** 2
        dr.hide_render = z < ctx["tray_top"]
        dr.location = (sx + 0.4, sy, max(z, ctx["tray_top"]))
    else:
        dr.hide_render = True

    # ---- typing: arms jitter on top of the keyed pose
    ty = cue_at(tl, "typing", t)
    for who in ty.get("who", []):
        ch = rig.CHARS.get(who)
        if ch is None:
            continue
        w = 0.1 * math.sin(t * 2 * math.pi * 7.3 + hash(who) % 5)
        ch.P["arm-1"].rotation_euler.x += w
        ch.P["arm1"].rotation_euler.x -= w * 0.8
    # ---- the beard
    bd = cue_at(tl, "beard", t).get("on", False)
    for o in ctx.get("beard", []):
        o.hide_render = not bd

    # ---- the streaks: behind each ten-cupper, from their own acting
    sk = cue_at(tl, "streaks", t)
    for who, ob in ctx["streaks"].items():
        ln = sk.get(who, 0.0)
        s = actmod.state(tl, who, t) if who in tl.get("acting", {}) or True else None
        try:
            hid = s["hidden"]
        except Exception:
            hid = True
        if not ln or hid:
            ob.hide_render = True
            ov[f"tcglow_{who}"] = 0.0
            continue
        ov[f"tcglow_{who}"] = 1.0
        ob.hide_render = False
        yaw = s["yaw"] if "yaw" in s else 0.0
        fx, fy = math.sin(yaw), -math.cos(yaw)
        sc_ = rig.CHARS[who].spec.get("height", 1.0) if who in rig.CHARS else 1.0
        ob.location = (s["x"] - fx * 0.2, s["y"] - fy * 0.2, s["z"])
        ctx["tclights"][who].location = (s["x"] - fx * 0.9, s["y"] - fy * 0.9 + 0.0, 1.9)
        ob.rotation_euler = (0, 0, yaw)
        ob.scale = (sc_ * rig.CHARS[who].spec.get("width", 1.0), ln, sc_)

    # ---- sneeze cloud and paper in the air
    sn_ = cue_at(tl, "sneeze", t)
    s = actmod.state(tl, "boss", t)
    for o, off in ctx["cloud"]:
        if sn_.get("on") and not s["hidden"]:
            yaw = s["yaw"]
            fx, fy = math.sin(yaw), -math.cos(yaw)
            o.hide_render = False
            o.location = (s["x"] + fx * (0.3 + off[1]) - fy * off[0], s["y"] + fy * (0.3 + off[1]) + fx * off[0], 1.45 + off[2])
        else:
            o.hide_render = True
    pp = cue_at(tl, "paper", t)
    for o, off in ctx["paper"]:
        if pp.get("pos"):
            o.hide_render = False
            o.location = (pp["pos"][0] + off[0], pp["pos"][1] + off[1], pp["pos"][2] + off[2])
        else:
            o.hide_render = True
    # ---- the new sticky note and its smoke
    nn = cue_at(tl, "note", t)
    on = nn.get("on", False)
    ctx["note"].hide_render = not on
    for i, o in enumerate(ctx["smoke"]):
        if on and nn.get("smoke", True):
            ph = ((t * 0.7 + i / len(ctx["smoke"])) % 1.0)
            o.hide_render = False
            o.location = (0.3 + 0.08 + 0.04 * math.sin(i * 2.0 + t * 2.0), 0.12, 1.5 + 0.28 * ph)
            sz = 0.2 + 1.8 * ph
            o.scale = (sz, sz, sz * 1.3)
        else:
            o.hide_render = True
    # ---- the jacket, the mess, the elevator, the clocks, the calendar
    ctx["jacket"].location = (2.6 + cue_at(tl, "jacket", t).get("dx", 0.0), -1.4, 0)
    hide(ctx["mess"], not cue_at(tl, "mess", t).get("on", False))
    op = keyed(tl, "elev", t, "open", 1.0)
    for dr_, s_ in ctx["elev"]:
        dr_.location = (9.8, 2.0 + s_ * (0.45 + 0.88 * ss(op)), 1.2)
    for key, hands in (("main", ctx["hands"]), ("lunch", ctx["hands2"])):
        cc_ = cue_at(tl, "clock", t)
        hv = keyed(tl, f"clock_{key}", t, "h", 3.0)
        sv = keyed(tl, f"clock_{key}", t, "s", 0.0)
        hands["h"].rotation_euler.y = math.radians((hv % 12) * 30)
        hands["m"].rotation_euler.y = math.radians((hv % 1) * 360)
        hands["s"].rotation_euler.y = math.radians((sv % 60) * 6)
    cl_ = cue_at(tl, "cal", t)
    for k, pl in enumerate(ctx["cal"]):
        if cl_.get("on"):
            pg = min(6, int((t - cl_["t"]) * cl_.get("rate", 5.0)))
            pl.hide_render = k != pg
        else:
            pl.hide_render = True
    return ov


# ------------------------------------------------------------------------------------------------ the meter inset
def build_inset(kit, ctx):
    """The meter panel glued to the camera, top right, so the rule is in every shot."""
    cam = kit.OBJ["cam"]
    m = kit._new(nm("inset"))
    nt, out = clear_nodes(m)
    tex = nt.nodes.new("ShaderNodeTexImage")
    gc = nt.nodes.new("ShaderNodeTexCoord")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 0.9
    nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    pl = kit.plane(nm("inset"), (1.0, 1.0), (0, 0, -0.15), m, cam)
    no_shadow(pl)
    ctx["inset"] = (pl, tex)


def place_inset(kit, ctx, e, tk, other, lens):
    pl, tex = ctx["inset"]
    key = (e, tk, other)
    if key not in ctx["inset_imgs"]:
        p, size = meter_png(e, tk, other)
        im = bpy.data.images.load(p)
        im.colorspace_settings.name = "sRGB"
        ctx["inset_imgs"][key] = (im, size)
    im, size = ctx["inset_imgs"][key]
    tex.image = im
    d = 0.15
    unit = d / lens
    pw = 4.3 * unit
    ph = pw * size[1] / size[0]
    x = (5.45 - 4.3 / 2) * unit
    y = (9.9 - ph / unit / 2) * unit
    pl.location, pl.scale = (x, y, -d), (pw, ph, 1)
