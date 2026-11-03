"""ep83-free-fries: a bright retro diner whose free fries are cooked, eyes shut, by whoever cooks for you most.

Four places, far apart on the x axis so they never light each other (metres, z up, cameras look +y):
- THE DINER (origin): mint booth by the back wall, an order hatch with a steel shelf and a brass bell, the round
  `0.00` sign above it, a swinging kitchen door with one round window, a counter, a wall clock, tall front windows.
- MOM'S KITCHEN (x 60) and OUR KITCHEN (x 100): one builder, two dressings. A stove island with two pots, a table
  with a bench, a couch, a fridge, a sink window with a hook for the yellow gloves.
- THE STOCKROOM (x 140): shelves and boxes where Omar and I work.
Built here from kit.py's parts. No text anywhere: the only marks are the numerals `0.00` and a fry glyph.
The rule marker: the sign over the hatch (chrome housing, glowing pink digits), and a small copy of it glued to the
camera's top left corner in every shot (so it is in the frame even inside Mom's kitchen). At L28 the digits ramp gold.
Cues (story.json "cues", each restates its whole state): hatch, bell, sign, tb (table baskets), dollar, stove,
smell, mgloves, mbA, mbB, dish, cal, srbox, mompos.
Light: two looks ("day", "eve"), ramped over the last 0.35 s of the shot before a cut, so no light ever switches.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import bl_story, faces, rig

TMP = Path(tempfile.mkdtemp(prefix="freefries-"))
KM, HM, SR = 60.0, 100.0, 140.0          # x of Mom's kitchen, our kitchen, the stockroom
PINK, GOLD = "#ff6fb5", "#ffc21a"
MINT, BUBBLE, CHROME = "#8de3c4", "#ff9ccf", "#d9e1e8"
YEL = "#ffd21a"

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


def P(hexc, rough=0.45, spec=0.4):
    return K.kit.plastic(hexc, rough, spec=spec)


def M(hexc, rough=0.25):
    return K.kit.metal(hexc, rough)


def B(parent, size, loc, mat, name="b", bevel=0.006, rot=(0, 0, 0)):
    return K.kit.box(nm(name), size, loc, mat, parent, rot, bevel)


def E(parent, loc=(0, 0, 0), name="e", rot=(0, 0, 0)):
    return K.kit.empty(nm(name), loc, parent, rot)


def CY(parent, r, h, loc, mat, name="c", rot=(0, 0, 0), n=28, r2=None):
    return K.kit.cyl(nm(name), r, h, loc, mat, parent, rot, n, r2)


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


# ------------------------------------------------------------------------------------------------ images
def make_images():
    from PIL import Image, ImageDraw, ImageFont

    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", 150)
    except Exception:
        f = ImageFont.load_default()
    # digits and the fry glyph: white on transparent, tinted in the material
    W = 512
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    txt = "0.00"
    bb = d.textbbox((0, 0), txt, font=f)
    d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], 275 - bb[1]), txt, fill=(255, 255, 255, 255), font=f)
    # fry glyph: a little basket with five sticks
    d.polygon([(190, 235), (322, 235), (302, 150), (210, 150)], fill=(255, 255, 255, 255))
    for i, x in enumerate((205, 232, 256, 280, 307)):
        d.rounded_rectangle([x - 9, 60 + 8 * (i % 2), x + 9, 160], 5, fill=(255, 255, 255, 255))
    d.rectangle([205, 190, 307, 200], fill=(0, 0, 0, 0))
    im.save(TMP / "digits.png")
    # the inset's ring and plate: chrome rim, dark plate, transparent outside
    R = 256
    ring = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
    g = ImageDraw.Draw(ring)
    g.ellipse([0, 0, 2 * R - 1, 2 * R - 1], fill=(222, 230, 238, 255))
    g.ellipse([22, 22, 2 * R - 23, 2 * R - 23], fill=(160, 170, 182, 255))
    g.ellipse([34, 34, 2 * R - 35, 2 * R - 35], fill=(24, 28, 52, 255))
    ring.save(TMP / "ring.png")
    return str(TMP / "digits.png"), str(TMP / "ring.png")


def rgba_mat(kit, name, path, strength=2.0, tint=None):
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path)
    tex.image.alpha_mode = "STRAIGHT"
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["Generated"], tex.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MULTIPLY"
    mix.inputs["Fac"].default_value = 1.0
    nt.links.new(tex.outputs["Color"], mix.inputs["Color1"])
    c = kit.col(tint or "#ffffff")
    mix.inputs["Color2"].default_value = c
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    nt.links.new(mix.outputs["Color"], em.inputs["Color"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    ms = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tex.outputs["Alpha"], ms.inputs["Fac"])
    nt.links.new(tr.outputs[0], ms.inputs[1])
    nt.links.new(em.outputs[0], ms.inputs[2])
    nt.links.new(ms.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    return m, mix


# ------------------------------------------------------------------------------------------------ small things
def basket(parent, loc=(0, 0, 0), name="basket"):
    """A fry basket: steel tub, gold fries sticking out, a handle toward +y. Origin: bottom centre."""
    R = E(parent, loc, name)
    st = M("#c9d0d6", 0.3)
    B(R, (0.34, 0.24, 0.02), (0, 0, 0.01), st, "bk", 0.004)
    for sx in (-1, 1):
        B(R, (0.012, 0.24, 0.1), (sx * 0.164, 0, 0.05), st, "bkw", 0.003)
    for sy in (-1, 1):
        B(R, (0.34, 0.012, 0.1), (0, sy * 0.114, 0.05), st, "bkw", 0.003)
    B(R, (0.03, 0.34, 0.03), (0, 0.27, 0.09), P("#2b2b33", 0.6), "bkh", 0.006)
    g1, g2 = P(GOLD, 0.5), P("#ffd54d", 0.5)
    for i in range(22):
        x = -0.14 + 0.28 * ((i * 37) % 11) / 10
        y = -0.09 + 0.18 * ((i * 53) % 9) / 8
        h = 0.14 + 0.03 * (i % 3)
        B(R, (0.03, 0.03, h), (x, y, 0.06 + h / 2 - 0.02), g1 if i % 2 else g2, "fry", 0.007,
          rot=(0.12 * math.sin(i * 2.1), 0.12 * math.cos(i * 1.7), 0.3 * i))
    return R


def glove_pair(parent, kind):
    """Two gloves and their sleeves reaching back into the dark (+y). Origin: the gloves' front edge, between them."""
    spec = {"yellow": (YEL, "#fff2a8", "#2c3652", 1.0), "pink": ("#ff5fa8", "#ffc4e0", "#2c3652", 1.0),
            "green": ("#4fc05a", "#2f8f3e", "#6a5a3a", 1.0), "mitt": ("#e8453c", "#ffe8e0", "#2c3652", 1.5),
            "ours": ("#d99a6c", "#d99a6c", "#e8b923", 1.0)}[kind]
    hand, cuff, sleeve, big = spec
    R = E(parent, (0, 0, 0), f"gl-{kind}")
    for sx in (-1, 1):
        xc = sx * 0.24
        sl = sleeve if kind != "ours" else ("#e8b923" if sx > 0 else "#4a6fa5")
        cf = cuff if kind != "ours" else ("#e8b923" if sx > 0 else "#4a6fa5")
        B(R, (0.17, 1.3, 0.17), (xc, 0.78, 0), P(sl, 0.7), "slv", 0.02)
        B(R, (0.2, 0.1, 0.2), (xc, 0.1, 0), P(cf, 0.6), "cuff", 0.02)
        hw = 0.15 * big
        B(R, (hw, 0.27 * big, 0.1 * big), (xc, -0.08 * big, 0), P(hand, 0.5, spec=0.5), "hand", 0.03)
        B(R, (0.055 * big, 0.12 * big, 0.06 * big), (xc - sx * 0.1 * big, -0.1 * big, 0.01), P(hand, 0.5, spec=0.5),
          "thumb", 0.02, rot=(0, 0, sx * 0.5))
        if kind == "mitt":
            B(R, (0.05, 0.02, 0.05), (xc, -0.22 * big, 0.06), P("#ffd0e4", 0.5), "heart", 0.01, rot=(0, 0.78, 0))
        if kind == "yellow":
            for fx in (-0.045, -0.015, 0.015, 0.045):
                B(R, (0.024, 0.1, 0.1), (xc + fx, -0.2, 0), P(hand, 0.5, spec=0.5), "fing", 0.01)
    return R


# ------------------------------------------------------------------------------------------------ the diner
def build_diner(kit, ctx):
    D = {}
    mint, bub = P(MINT, 0.55), P(BUBBLE, 0.5)
    # floor, walls, windows
    B(None, (16, 8.9, 0.1), (0, -0.55, -0.05), kit.checker("#fbfbf8", "#2a2d3a", 2.0), "floor", 0.0)
    # the order-hatch wall as pieces around the opening (x -0.65..0.65, z 1.0..1.8), y 3.9..4.2
    for x0, x1, z0, z1 in ((-8, -0.65, 0, 3.4), (0.65, 8, 0, 3.4), (-0.65, 0.65, 1.8, 3.4), (-0.65, 0.65, 0, 1.0)):
        B(None, (x1 - x0, 0.3, z1 - z0), ((x0 + x1) / 2, 4.05, (z0 + z1) / 2), mint, "wallF", 0.0)
    B(None, (16, 0.02, 0.18), (0, 3.89, 1.0), bub, "stripe", 0.0)                # pink stripe, proud of the wall
    B(None, (0.3, 9.0, 3.4), (-8.1, -0.4, 1.7), mint, "wallL", 0.0)
    B(None, (0.3, 9.0, 3.4), (8.1, -0.4, 1.7), mint, "wallR", 0.0)
    for x0, x1, z0, z1 in ((-8, 8, 0, 0.9), (-8, 8, 2.5, 3.4), (-8, -6.5, 0.9, 2.5), (-3, -2, 0.9, 2.5), (2, 3, 0.9, 2.5),
                           (6.5, 8, 0.9, 2.5)):
        B(None, (x1 - x0, 0.2, z1 - z0), ((x0 + x1) / 2, -5.1, (z0 + z1) / 2), mint, "wallW", 0.0)
    B(None, (16, 0.02, 0.1), (0, -4.99, 0.95), bub, "wstripe", 0.0)
    B(None, (60, 0.4, 14), (0, -14.0, 4.0), kit.emit("#cfeeff", 1.1, name="outsky"), "outsky", 0.0)
    B(None, (60, 9.0, 0.1), (0, -9.8, -0.05), P("#9be05a", 0.8), "outlawn", 0.0)
    # the dark kitchen behind the hatch (the cook is never seen)
    dark = P("#32405c", 0.8, 0.05)
    B(None, (3.0, 3.0, 0.1), (0, 5.5, -0.05), dark, "kfloor", 0.0)
    B(None, (3.2, 0.2, 3.4), (0, 7.1, 1.7), dark, "kback", 0.0)
    for sx in (-1, 1):
        B(None, (0.2, 3.1, 3.4), (sx * 1.6, 5.55, 1.7), dark, "kside", 0.0)
    B(None, (3.2, 3.1, 0.2), (0, 5.55, 3.4), dark, "kceil", 0.0)
    ctx["kin"] = kit.light("kin", "POINT", (0, 4.9, 1.9), 60, "#ffd6a0", size=0.3, shadow=False)
    # the order hatch: steel shelf, brass bell, sign housing
    B(None, (1.7, 0.55, 0.06), (0, 3.72, 0.97), M("#cfd6dc", 0.2), "shelf", 0.01)
    for sx in (-1, 1):
        B(None, (0.06, 0.6, 0.86), (sx * 0.68, 4.0, 1.4), M("#cfd6dc", 0.3), "hframe", 0.01)
    B(None, (1.42, 0.6, 0.06), (0, 4.0, 1.83), M("#cfd6dc", 0.3), "htop", 0.01)
    bell = E(None, (0.78, 3.7, 1.0), "bell")
    CY(bell, 0.075, 0.02, (0, 0, 0.01), M("#d9a521", 0.25), "bellb")
    CY(bell, 0.06, 0.07, (0, 0, 0.055), M("#e8b83a", 0.2), "belld", r2=0.035)
    B(bell, (0.02, 0.02, 0.03), (0, 0, 0.1), M("#d9a521", 0.25), "bellk", 0.005)
    D["bell"] = bell
    # the sign: chrome housing, dark plate, glowing digits (the rule marker)
    CY(None, 0.5, 0.1, (0, 3.84, 2.5), M(CHROME, 0.18), "signh", rot=(math.pi / 2, 0, 0), n=40)
    CY(None, 0.39, 0.03, (0, 3.78, 2.5), P("#181c34", 0.4), "signp", rot=(math.pi / 2, 0, 0), n=40)
    digits, ring = make_images()
    dm, dmix = rgba_mat(kit, nm("digits"), digits, 3.0, PINK)
    pl = kit.plane(nm("digits"), (0.72, 0.72), (0, 3.755, 2.5), dm, None, rot=(math.pi / 2, 0, 0))
    no_shadow(pl)
    ctx["sign_mix"] = [dmix]
    ctx["digits_path"], ctx["ring_path"] = digits, ring
    ctx["signlight"] = kit.light("signlight", "POINT", (0, 3.0, 2.3), 130, PINK, size=0.3, shadow=False)
    # the kitchen door: a swinging door with one round window, dark glass and a pink reflection
    B(None, (0.95, 0.08, 2.1), (1.4, 3.86, 1.05), P("#3aa89b", 0.45), "door", 0.01)
    for sx in (-1, 1):
        B(None, (0.04, 0.1, 2.14), (1.4 + sx * 0.5, 3.86, 1.07), bub, "doorf", 0.01)
    B(None, (1.04, 0.1, 0.04), (1.4, 3.86, 2.14), bub, "doorf", 0.01)
    CY(None, 0.22, 0.04, (1.4, 3.80, 1.58), M(CHROME, 0.2), "rim", rot=(math.pi / 2, 0, 0))
    CY(None, 0.175, 0.05, (1.4, 3.795, 1.58), P("#10182a", 0.1, 0.9), "glass", rot=(math.pi / 2, 0, 0))
    for rr, (gx, gz) in ((0.045, (1.33, 1.65)), (0.02, (1.29, 1.6))):
        refl = CY(None, rr, 0.004, (gx, 3.762, gz), kit.emit(PINK, 1.6, name="refl"), "refl", rot=(math.pi / 2, 0, 0))
    no_shadow(refl)
    # the counter, stools, bottles
    B(None, (5.4, 0.7, 1.0), (-4.7, 2.9, 0.5), P(MINT, 0.5), "counter", 0.01)
    B(None, (5.5, 0.8, 0.06), (-4.7, 2.9, 1.03), M(CHROME, 0.25), "ctop", 0.01)
    B(None, (5.45, 0.02, 0.1), (-4.7, 2.54, 0.6), bub, "cstripe", 0.0)
    for x in (-6.6, -5.7, -2.7):
        CY(None, 0.05, 0.6, (x, 1.7, 0.3), M(CHROME, 0.2), "stoolp")
        CY(None, 0.22, 0.08, (x, 1.7, 0.64), P(BUBBLE, 0.4), "stools")
    for i, (x, c) in enumerate(((-6.3, "#e23a3a"), (-6.0, "#ffd21a"), (-1.4, "#e23a3a"))):
        if i < 2:
            CY(None, 0.035, 0.18, (x, 3.05, 1.15), P(c, 0.4), "bottle")
            CY(None, 0.012, 0.05, (x, 3.05, 1.27), P(c, 0.4), "bottip", r2=0.004)
    B(None, (0.3, 0.16, 0.2), (-5.2, 3.05, 1.16), M(CHROME, 0.12), "napkin", 0.02)
    # wall clock (hands only) at four
    clk = E(None, (-2.4, 3.8, 2.6), "clock")
    CY(clk, 0.34, 0.05, (0, 0, 0), P(BUBBLE, 0.4), "clockr", rot=(math.pi / 2, 0, 0))
    CY(clk, 0.28, 0.06, (0, -0.005, 0), P("#fffaf0", 0.5), "clockf", rot=(math.pi / 2, 0, 0))
    for ang, ln, w in ((120, 0.17, 0.035), (0, 0.24, 0.025)):
        a = math.radians(ang)
        B(clk, (w, 0.012, ln), (math.sin(a) * ln / 2, -0.036, math.cos(a) * ln / 2), P("#2a2d3a", 0.5), "hand", 0.003,
          rot=(0, a, 0))
    for k in range(12):
        a = math.radians(30 * k)
        B(clk, (0.02, 0.012, 0.035), (math.sin(a) * 0.24, -0.036, math.cos(a) * 0.24), P("#2a2d3a", 0.5), "tick", 0.002,
          rot=(0, a, 0))
    # the booth: bench against the wall, pink piping, the table with its chrome edge and two gold strokes
    B(None, (3.6, 0.7, 0.45), (5.2, 3.45, 0.225), mint, "bench", 0.04)
    B(None, (3.6, 0.1, 1.0), (5.2, 3.84, 0.95), mint, "benchb", 0.04)
    B(None, (3.64, 0.02, 0.06), (5.2, 3.09, 0.3), bub, "pipe", 0.0)
    B(None, (1.9, 0.92, 0.05), (5.1, 2.3, 0.76), P("#fff6ea", 0.4), "table", 0.01)
    B(None, (1.94, 0.04, 0.052), (5.1, 1.84, 0.76), M(CHROME, 0.15), "tedge", 0.0)
    B(None, (0.014, 0.034, 0.012), (4.92, 1.84, 0.792), P(GOLD, 0.4), "tally", 0.0)
    B(None, (0.014, 0.034, 0.012), (4.96, 1.84, 0.792), P(GOLD, 0.4), "tally", 0.0)
    CY(None, 0.07, 0.74, (5.1, 2.3, 0.37), M(CHROME, 0.2), "tpost")
    CY(None, 0.035, 0.18, (5.7, 2.55, 0.875), P("#e23a3a", 0.4), "bottle")
    CY(None, 0.035, 0.18, (5.8, 2.55, 0.875), P("#ffd21a", 0.4), "bottle")
    basket(None, (-3.35, 2.85, 1.06), "cbask")
    tb = []
    for x in (4.65, 5.55):
        bk = basket(None, (x, 2.2, 0.785), "tbask")
        hide(bk, True)
        tb.append(bk)
    ctx["tb"] = tb
    dol = B(None, (0.34, 0.16, 0.008), (5.1, 2.35, 0.789), P("#7fcf86", 0.6), "dollar", 0.0)
    dol2 = B(dol, (0.24, 0.1, 0.004), (0, 0, 0.006), P("#a8e6ae", 0.6), "dollar2", 0.0)
    hide(dol, True)
    ctx["dollar"] = dol
    # a jukebox of coloured lights only
    jb = P("#7a5cff", 0.4)
    B(None, (0.9, 0.5, 1.6), (-7.2, 3.5, 0.8), jb, "juke", 0.04)
    for i, c in enumerate(("#ff6fb5", "#ffd21a", "#4fe0ff", "#7fff9a")):
        B(None, (0.7, 0.02, 0.08), (-7.2, 3.24, 1.1 + 0.18 * i), kit.emit(c, 2.2, name=f"jl{i}"), "jlight", 0.0)
    # the hatch's gloves, in variants, and the baskets
    ctx["gloves"] = {k: glove_pair(None, k) for k in ("yellow", "pink", "green", "mitt", "ours")}
    for g in ctx["gloves"].values():
        hide(g, True)
    ctx["hbasket"] = basket(None, (0, 3.7, 1.0), "hbask")
    ctx["hbasket2"] = basket(None, (0.42, 3.66, 1.0), "hbask2")
    hide(ctx["hbasket"], True)
    hide(ctx["hbasket2"], True)
    # lights
    for x in (-4.5, 0.0, 4.5):
        kit.light(f"dl{x}", "POINT", (x, 1.2, 3.1), 170, "#fff4e0", size=0.5, shadow=False)
    ctx["sun"] = kit.light("sun", "SUN", (0, 0, 50), 2.5, "#fff1d0", size=0.1)
    ctx["sun"].data.angle = 0.06
    az, el = math.radians(20), math.radians(38)
    pos = V((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    ctx["sun"].rotation_euler = (-pos).to_track_quat("-Z", "Y").to_euler()
    ctx["D"] = D


# ------------------------------------------------------------------------------------------------ a home kitchen
def build_kitchen(kit, ox, home, ctx):
    wall = "#ffd9a8" if home else "#ffe58a"
    trim = "#ff9ccf" if home else "#ffb35c"
    W = P(wall, 0.7, 0.1)
    kit_ = kit
    B(None, (8.6, 6.2, 0.1), (ox - 0.3, 1.0, -0.05), kit.texture("wood", 0.7, tint="#f6dcae"), "kfloor", 0.0)
    # back wall with the sink window (x ox+2.3..3.1, z 1.3..2.2)
    for x0, x1, z0, z1 in ((-4.2, 2.3, 0, 2.9), (3.1, 3.6, 0, 2.9), (2.3, 3.1, 0, 1.3), (2.3, 3.1, 2.2, 2.9)):
        B(None, (x1 - x0, 0.2, z1 - z0), (ox + (x0 + x1) / 2, 3.5, (z0 + z1) / 2), W, "kwallB", 0.0)
    B(None, (8, 0.02, 0.12), (ox - 0.3, 3.39, 1.0), P(trim, 0.5), "ktrim", 0.0)
    B(None, (1.0, 0.1, 1.2), (ox + 2.7, 3.7, 1.75), kit.emit("#bfe6ff" if not home else "#ffe2b0", 1.3, name="kview"),
      "kview", 0.0)
    B(None, (0.3, 6.2, 2.9), (ox - 4.35, 1.0, 1.45), W, "kwallL", 0.0)
    B(None, (0.3, 6.2, 2.9), (ox + 3.75, 1.0, 1.45), W, "kwallR", 0.0)
    # sink counter under the window
    B(None, (1.8, 0.7, 0.9), (ox + 2.6, 3.0, 0.45), P("#fff6ea", 0.5), "kcnt", 0.01)
    B(None, (1.84, 0.74, 0.05), (ox + 2.6, 3.0, 0.925), M(CHROME, 0.25), "kctop", 0.01)
    B(None, (0.5, 0.35, 0.02), (ox + 2.7, 2.98, 0.955), M("#aab3ba", 0.2), "ksink", 0.0)
    # fridge with plain magnets
    B(None, (0.95, 0.8, 1.85), (ox - 3.45, 3.0, 0.925), P("#fbfbf8", 0.35), "fridge", 0.03)
    B(None, (0.9, 0.012, 0.02), (ox - 3.45, 2.597, 1.15), P("#cfd6dc", 0.4), "fseam", 0.0)
    B(None, (0.04, 0.04, 0.5), (ox - 3.0, 2.585, 1.4), M(CHROME, 0.2), "fhandle", 0.01)
    for i, (dx, dz, c) in enumerate(((-0.25, 1.55, "#e23a3a"), (0.0, 1.62, "#4fa8ff"), (-0.12, 1.4, "#ffd21a"))):
        B(None, (0.08, 0.02, 0.08), (ox - 3.45 + dx, 2.59, dz), P(c, 0.5), "magnet", 0.01)
    # the stove island, two pots with calm oil, burners
    B(None, (1.3, 0.7, 0.9), (ox, 1.0, 0.45), P("#fbfbf8", 0.35), "stove", 0.02)
    B(None, (1.32, 0.72, 0.04), (ox, 1.0, 0.92), P("#2a2d3a", 0.3), "stovetop", 0.0)
    B(None, (1.1, 0.02, 0.18), (ox, 0.645, 0.5), P("#2a2d3a", 0.4), "oven", 0.0)
    burn = []
    for px in (-0.2, 0.25):
        pot = E(None, (ox + px, 1.15, 0.94), "pot")
        CY(pot, 0.2, 0.24, (0, 0, 0.12), P("#454c5c", 0.35, 0.6), "potb")
        CY(pot, 0.185, 0.012, (0, 0, 0.222), P("#d6962a", 0.15, 0.8), "oil")
        burn.append(CY(pot, 0.12, 0.006, (0, 0, 0.003), kit.emit("#ff7a2a", 1.8, name="burn"), "burner"))
    for b in burn:
        hide(b, True)
    ctx.setdefault("burn", {})[ox] = burn
    # table with a bench, plates
    B(None, (2.6, 0.9, 0.05), (ox - 2.4, 1.4, 0.76), P("#fff6ea", 0.45), "ktable", 0.01)
    for sx in (-1, 1):
        B(None, (0.08, 0.7, 0.74), (ox - 2.4 + sx * 1.2, 1.4, 0.37), P("#c98d4d", 0.6), "tleg", 0.01)
    B(None, (2.8, 0.5, 0.45), (ox - 2.4, 2.25, 0.225), P("#c98d4d" if not home else "#ff9ccf", 0.6), "kbench", 0.03)
    for i, c in enumerate(("#fbfbf8", "#8de3c4", "#fbfbf8")):
        CY(None, 0.13, 0.015, (ox - 3.15 + 0.75 * i, 1.35, 0.79), P(c, 0.4), "plate")
    # couch against the back wall
    cc = P("#ff8fa3", 0.65, 0.15)
    B(None, (1.8, 0.8, 0.45), (ox + 0.4, 3.0, 0.225), cc, "couch", 0.05)
    B(None, (1.8, 0.2, 0.55), (ox + 0.4, 3.33, 0.72), cc, "couchb", 0.05)
    for sx in (-1, 1):
        B(None, (0.2, 0.8, 0.62), (ox + 0.4 + sx * 0.9, 3.0, 0.31), cc, "couchA", 0.05)
    # the hook beside the window, with the yellow gloves hanging (hidden while Mom wears them)
    B(None, (0.04, 0.06, 0.04), (ox + 1.95, 3.37, 1.9), M("#aab3ba", 0.3), "hook", 0.005)
    hang = E(None, (ox + 1.95, 3.34, 1.82), "hang")
    for sx in (-1, 1):
        B(hang, (0.12, 0.05, 0.3), (sx * 0.07, 0, -0.1), P(YEL, 0.5), "hglove", 0.02)
        B(hang, (0.14, 0.055, 0.08), (sx * 0.07, 0, 0.07), P("#fff2a8", 0.5), "hcuff", 0.02)
    ctx.setdefault("hang", {})[ox] = hang
    # lights
    ctx.setdefault("klamp", []).append(kit.light(f"klamp{int(ox)}", "POINT", (ox, 1.4, 2.9), 200, "#ffe1b0", size=0.5, shadow=False))
    kit.light(f"kl2{int(ox)}", "POINT", (ox - 2.4, 0.6, 2.6), 120, "#ffe1b0", size=0.5, shadow=False)
    if home:
        # a wall calendar and the dishes (cue "dish"), a card that flips (cue "cal")
        cal = E(None, (ox + 1.2, 3.38, 1.6), "cal")
        B(cal, (0.55, 0.02, 0.5), (0, 0, 0), P("#fffaf0", 0.6), "calb", 0.0)
        B(cal, (0.55, 0.022, 0.1), (0, -0.002, 0.2), P("#e23a3a", 0.5), "calt", 0.0)
        for r in range(4):
            for c in range(5):
                B(cal, (0.06, 0.022, 0.05), (-0.2 + 0.1 * c, -0.003, 0.08 - 0.09 * r), P("#8aa0b8", 0.6), "cald", 0.0)
        flip = E(cal, (0, -0.04, 0.25), "flip")
        B(flip, (0.55, 0.012, 0.5), (0, 0, -0.25), P("#fffaf0", 0.6), "flipb", 0.0)
        B(flip, (0.55, 0.014, 0.1), (0, -0.002, -0.05), P("#e23a3a", 0.5), "flipt", 0.0)
        for c in range(5):
            B(flip, (0.06, 0.014, 0.05), (-0.2 + 0.1 * c, -0.004, -0.2), P("#ff9ccf", 0.6), "flipd", 0.0)
        ctx["cal"] = (cal, flip)
        pan = E(None, (ox - 0.2, 0.95, 0.94), "pan")
        CY(pan, 0.24, 0.07, (0, 0, 0.035), P("#454c5c", 0.35, 0.6), "panb")
        for i in range(14):
            a = i * 0.9
            B(pan, (0.26, 0.03, 0.03), (0.07 * math.cos(a * 1.3), 0.07 * math.sin(a * 1.3), 0.085 + 0.012 * (i % 3)),
              P("#ffe08a", 0.6), "noodle", 0.01, rot=(0, 0, a))
        tray = E(None, (ox + 0.3, 0.95, 0.94), "tray")
        B(tray, (0.6, 0.4, 0.03), (0, 0, 0.015), M("#aab3ba", 0.4), "trayb", 0.005)
        for i in range(6):
            B(tray, (0.15, 0.15, 0.09), (-0.2 + 0.2 * (i % 3), -0.1 + 0.2 * (i // 3), 0.075), P("#c98d4d", 0.6), "bake", 0.04)
        ctx["hbk"] = basket(None, (ox + 0.35, 1.22, 0.98), "hbk")
        hide(ctx["hbk"], True)
        ctx["dishes"] = {"pan": pan, "tray": tray}
        hide(pan, True)
        hide(tray, True)
    else:
        ctx["mbask"] = [basket(None, (ox - 0.2, 1.15, 1.3), "mbA"), basket(None, (ox + 0.25, 1.15, 1.3), "mbB")]
        for b in ctx["mbask"]:
            hide(b, True)
        # the smell: soft gold puffs over the pots
        sm = kit._new(nm("smell"))
        nt = sm.node_tree
        nt.nodes.remove(nt.nodes["Principled BSDF"])
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = kit.col(GOLD)
        em.inputs["Strength"].default_value = 1.8
        mx = nt.nodes.new("ShaderNodeMixShader")
        mx.inputs["Fac"].default_value = 0.22
        nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(em.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
        ctx["smell"] = []
        for j in range(16):
            o = kit.sphere(nm("smell"), 0.05, (0, 0, 0), sm, None, seg=12)
            no_shadow(o)
            o.hide_render = True
            ctx["smell"].append(o)


def build_stockroom(kit, ctx):
    ox = SR
    B(None, (8, 6, 0.1), (ox, 1.5, -0.05), P("#b9bfc9", 0.8, 0.1), "sfloor", 0.0)
    wl = P("#f0e4cf", 0.8, 0.05)
    B(None, (8, 0.2, 3.0), (ox, 4.0, 1.5), wl, "swallB", 0.0)
    B(None, (0.2, 6, 3.0), (ox - 4.1, 1.5, 1.5), wl, "swallL", 0.0)
    B(None, (0.2, 6, 3.0), (ox + 4.1, 1.5, 1.5), wl, "swallR", 0.0)
    B(None, (8, 0.02, 0.15), (ox, 3.89, 1.0), P("#ffb35c", 0.5), "sstripe", 0.0)
    for sx in (-1, 1):                      # two shelf units along the back wall with boxes
        for lv in range(3):
            B(None, (2.6, 0.6, 0.05), (ox + sx * 2.3, 3.55, 0.35 + 0.7 * lv), P("#6b86b0", 0.5), "shelf", 0.01)
            for k in range(3):
                B(None, (0.6, 0.45, 0.5 - 0.05 * ((k + lv) % 2)), (ox + sx * 2.3 - 0.85 + 0.85 * k, 3.55, 0.65 + 0.7 * lv - 0.03),
                  P("#d9a566" if (k + lv) % 2 else "#e4b97c", 0.8), "sbox", 0.02)
    ctx["srbox"] = B(None, (0.6, 0.45, 0.4), (ox, 1.0, 0.9), P("#e4b97c", 0.8), "carry", 0.02)
    hide(ctx["srbox"], True)
    kit.light("srl1", "POINT", (ox - 1.5, 1.5, 2.9), 200, "#fff1d8", size=0.5, shadow=False)
    kit.light("srl2", "POINT", (ox + 1.5, 1.5, 2.9), 200, "#fff1d8", size=0.5, shadow=False)


# ------------------------------------------------------------------------------------------------ camera inset / porthole
def build_overlays(kit, ctx):
    cam = kit.OBJ["cam"]
    # the porthole: a dark door with a round hole, a chrome rim, glued to the camera (cue: shot key "ring")
    n = 64
    ri = 6.1
    rim_in, rim_out = ri, ri + 0.35

    def rect_pt(dx, dy, hw, hh):
        s = max(abs(dx) / hw, abs(dy) / hh)
        return (dx / s, dy / s)

    inner, outer = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        dx, dy = math.cos(a), math.sin(a)
        inner.append((ri * dx, ri * dy + 0.5))
        ox_, oy_ = rect_pt(dx, dy, 7.6, 13.0)
        outer.append((ox_, oy_ + 0.5))
    verts = [(x, y, 0) for x, y in inner] + [(x, y, 0) for x, y in outer]
    fcs = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    door = kit.emit("#2a8a86", 0.95, name="porthole")
    rimm = kit.emit("#e4eaf0", 1.0, name="portrim")
    ctx["port"] = kit.mesh_obj(nm("porthole"), verts, fcs, door, cam, (0, 0, -0.2))
    rv = [(x * rim_out / ri, (y - 0.5) * rim_out / ri + 0.5, 0) for x, y in inner] + [(x, y, 0) for x, y in inner]
    rf = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    ctx["portrim"] = kit.mesh_obj(nm("portrim"), rv, rf, rimm, cam, (0, 0, -0.1995))
    for o in (ctx["port"], ctx["portrim"]):
        no_shadow(o)
    # the rule marker, small, top left of every frame
    rm, _ = rgba_mat(kit, nm("insetring"), ctx["ring_path"], 1.0, None)
    dm, dmix = rgba_mat(kit, nm("insetdig"), ctx["digits_path"], 3.0, PINK)
    ctx["sign_mix"].append(dmix)
    pr = kit.plane(nm("insetring"), (1.0, 1.0), (0, 0, -0.15), rm, cam)
    pd = kit.plane(nm("insetdig"), (1.0, 1.0), (0, 0, -0.1498), dm, cam)
    for o in (pr, pd):
        no_shadow(o)
    ctx["inset"] = (pr, pd)


def place_overlays(ctx, lens, ring_on):
    unit = 0.2 / lens
    ctx["port"].scale = (unit, unit, 1)
    ctx["portrim"].scale = (unit, unit, 1)
    ctx["port"].hide_render = not ring_on
    ctx["portrim"].hide_render = not ring_on
    pr, pd = ctx["inset"]
    u2 = 0.15 / lens
    s = 3.9                               # mm: the disc is a little under a third of the frame width
    x, y = -3.7, 8.0
    pr.location, pr.scale = (x * u2, y * u2, -0.15), (s * u2, s * u2, 1)
    pd.location, pd.scale = (x * u2, (y - 0.05) * u2, -0.1498), (s * 0.84 * u2, s * 0.84 * u2, 1)


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    K.kit = kit
    ctx = {"story": story, "shots": {s["id"]: s for s in story["shots"]}, "late": False}
    build_diner(kit, ctx)
    build_kitchen(kit, KM, False, ctx)
    kh = ctx.pop("klamp")
    build_kitchen(kit, HM, True, ctx)
    ctx["klamp"] = kh + ctx.get("klamp", [])
    build_stockroom(kit, ctx)
    ctx["fill"] = kit.light("camfill", "POINT", (0, 0, 2), 30, "#fff0dc", size=0.6, shadow=False)
    build_overlays(kit, ctx)
    ctx["bg"] = bpy.context.scene.world.node_tree.nodes["Background"]
    return ctx


def mom_late(kit, ctx):
    ch = rig.CHARS.get("mom")
    ctx["mgl"] = []
    if ch is None:
        return
    for k in ("arm-1", "arm1"):
        g = B(ch.P[k], (1.14, 1.14, 0.95), (0, 0, -1.72), P(YEL, 0.5, 0.5), "mglove", 0.06)
        c = B(ch.P[k], (1.2, 1.2, 0.3), (0, 0, -1.2), P("#fff2a8", 0.5), "mcuff", 0.05)
        ctx["mgl"] += [g, c]


LOOKS = {"day": {"bg": 0.8, "sun": 2.5, "lamp": 1.0}, "eve": {"bg": 0.4, "sun": 0.0, "lamp": 1.1}}


def look_of(ctx, sid):
    return LOOKS[ctx["shots"][sid].get("look", "day")]


def look_at(ctx, tl, t):
    shots = tl["shots"]
    cur = next((s for s in shots if s["start"] <= t < s["end"]), shots[-1])
    i = shots.index(cur)
    A = look_of(ctx, cur["id"])
    if i + 1 < len(shots) and t > cur["end"] - 0.35:
        nb = look_of(ctx, shots[i + 1]["id"])
        if nb is not A:
            u = ss((t - (cur["end"] - 0.35)) / 0.35)
            return {k: lerp(A[k], nb[k], u) for k in A}, cur
    return dict(A), cur


def animate(kit, story, tl, t, ctx):
    if not ctx["late"]:
        mom_late(kit, ctx)
        ctx["late"] = True
    sc = bpy.context.scene
    L, cur = look_at(ctx, tl, t)
    sd = ctx["shots"][cur["id"]]
    ctx["bg"].inputs["Strength"].default_value = L["bg"]
    ctx["sun"].data.energy = L["sun"]
    cl, _, lens, _ = bl_story.cam_at(sd, cur, t, {}, tl)
    ctx["fill"].location = (cl[0], cl[1], cl[2])
    sc.view_settings.exposure = sd.get("exp", 0.0)
    ov = {"camfill": sd.get("fill", 1.0)}
    for lt in ctx["klamp"]:
        ov[lt.name] = L["lamp"]
    cd = kit.OBJ["cam"].data
    dof = sd.get("dof")
    if dof:
        cd.dof.use_dof = True
        cd.dof.focus_distance = dof[0]
        cd.dof.aperture_fstop = dof[1]
    else:
        cd.dof.use_dof = False
    place_overlays(ctx, lens, bool(sd.get("ring")))
    # ---- the sign: pink, then gold
    sg = cue_at(tl, "sign", t)
    u = ss((t - sg["t"]) / max(1e-3, sg.get("dur", 0.5))) if sg.get("tint") == "gold" else 0.0
    pk, gd = kit.col(PINK), kit.col(GOLD)
    for mix in ctx["sign_mix"]:
        mix.inputs["Color2"].default_value = tuple(lerp(a, b, u) for a, b in zip(pk, gd))
    sl = ctx["signlight"].data
    sl.color = tuple(lerp(a, b, u) for a, b in zip(pk[:3], gd[:3]))
    # ---- the hatch: gloves slide a basket out, the bell rings
    hc = cue_at(tl, "hatch", t)
    kind = hc.get("kind")
    for k, g in ctx["gloves"].items():
        hide(g, k != kind)
    hb, hb2 = ctx["hbasket"], ctx["hbasket2"]
    if kind:
        s = lerp(hc.get("s0", 0.0), hc.get("s1", 1.0), ss((t - hc["t"]) / max(1e-3, hc.get("dur", 1.0))))
        gy = lerp(4.95, 3.98, s)
        wig = hc.get("wig", 0.0)
        gl = ctx["gloves"][kind]
        gl.location = (wig * 0.05 * math.sin(t * 5.0), gy, 1.27 + wig * 0.03 * math.sin(t * 7.0))
        hide(hb, not hc.get("basket", True))
        hb.location = (0, gy - 0.46, 1.0)
        hide(hb2, not hc.get("second", False))
    else:
        hide(hb, True)
        hide(hb2, True)
    bc = cue_at(tl, "bell", t)
    bell = ctx["D"]["bell"]
    ang = 0.0
    if bc:
        u2 = t - bc["t"]
        if 0 <= u2 < 0.9:
            ang = math.exp(-3.5 * u2) * 0.35 * math.sin(u2 * 34)
    bell.rotation_euler = (ang, ang * 0.6, 0)
    # ---- table baskets and the dollar
    on = cue_at(tl, "tb", t).get("on", False)
    for b in ctx["tb"]:
        hide(b, not on)
    hide(ctx["dollar"], not cue_at(tl, "dollar", t).get("on", False))
    # ---- kitchens: burners, the smell, Mom's gloves, the hook gloves, the baskets
    stv = cue_at(tl, "stove", t).get("on", False)
    for b in ctx["burn"][KM]:
        hide(b, not stv)
    mg = cue_at(tl, "mgloves", t).get("on", False)
    for o in ctx.get("mgl", []):
        hide(o, not mg)
    hide(ctx["hang"][KM], mg)
    sm = cue_at(tl, "smell", t).get("on", False)
    for j, o in enumerate(ctx["smell"]):
        if not sm:
            o.hide_render = True
            continue
        pot = j % 2
        ph = (t * 0.45 + j / len(ctx["smell"])) % 1.0
        env = math.sin(math.pi * ph) ** 0.9
        o.hide_render = False
        o.location = (KM + (-0.2 if pot == 0 else 0.25) + 0.09 * math.sin(j * 1.9 + t), 1.15 + 0.06 * math.cos(j * 1.3),
                      1.2 + 0.9 * ph)
        o.scale = (0.5 * env + 0.001, 0.5 * env + 0.001, (1.4 + ph) * env + 0.001)
    for i, key in enumerate(("mbA", "mbB")):
        c = cue_at(tl, key, t)
        b = ctx["mbask"][i]
        if not c.get("on"):
            hide(b, True)
            continue
        hide(b, False)
        u3 = ss((t - c["t"]) / max(1e-3, c.get("dur", 1.0)))
        z = lerp(c.get("z0", 1.3), c.get("z1", 1.13), u3)
        yy = lerp(c.get("y0", 1.15), 1.15, u3)
        b.location = (KM + (-0.2 if i == 0 else 0.25), yy, z)
    # ---- our kitchen: dishes and the flipping calendar
    dsh = cue_at(tl, "dish", t).get("which")
    for k, o in ctx["dishes"].items():
        hide(o, k != dsh)
    cal, flip = ctx["cal"]
    cc = cue_at(tl, "cal", t)
    if cc:
        flip.rotation_euler = (-math.pi * 0.95 * ss((t - cc["t"]) / max(1e-3, cc.get("dur", 0.8))), 0, 0)
    else:
        flip.rotation_euler = (0, 0, 0)
    hide(ctx["hbk"], not cue_at(tl, "hbask", t).get("on", False))
    # ---- the stockroom box carried across
    sb = cue_at(tl, "srbox", t)
    if sb:
        hide(ctx["srbox"], False)
        u4 = min(1.0, max(0.0, (t - sb["t"]) / max(1e-3, sb["dur"])))
        ctx["srbox"].location = (lerp(sb["x0"], sb["x1"], u4), lerp(sb["y0"], sb["y1"], u4), 0.95)
    else:
        hide(ctx["srbox"], True)
    return ov
