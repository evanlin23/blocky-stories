"""ep121-blank-fortune: a bright highway gas station where every fortune cookie comes true by Friday, and a blank slip.

Places, far apart on the x axis so they never light each other (metres, z up, cameras look +y, characters face -y):
- THE STATION (origin): two red pumps under a white canopy, Grandpa's teal pickup, a small shop behind, fields, the road.
- THE SHOP (x 40): a counter with a jar of wrapped cookies, a register, the clerk's side of it.
- THE TIRE (x 80) and THE LOT (x 120): a wheel with forty dollars in its tread; a car park a woman crosses with geese.
- MY KITCHEN (x 160), MY BEDROOM (x 200): the window onto a quiet street; a bed, a nightstand.
- GRANDPA'S HOUSE (x 240) at night, with my car; GRANDPA'S KITCHEN (x 280) with the doorway to Grandma's chair.
- THE DASHBOARD (x 320): the taped slip.
No readable words anywhere: slips are blank, gray bars (printed) or blue scribble (handwriting).
The rule marker: a cream tag glued to the camera's top left (a cookie glyph and three dots W T F, a needle that moves
Wednesday -> Friday and back). Cues (story.json "cues", each restates its whole state): day, cookie, cookie2, slip_ck,
slip_mine, slip_gp, slip_tape, phone, soda, wallet, pen, bills, geese, car, snow.
Light: two looks ("day", "night"), ramped over the last 0.35 s of the shot before a cut, so no light ever switches.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import bl_story, faces, rig

TMP = Path(tempfile.mkdtemp(prefix="blankfortune-"))
GOLD = "#e8b85a"
PUMP = "#e2463f"
WHITE = "#f6f4ee"
TEAL = "#2fb7a8"
SLIP = "#fbf8f0"
OLD = "#f1dc92"
BLUE = "#2a56d6"
KY = "#ffd86b"
X_SHOP, X_TIRE, X_LOT, X_KIT, X_BED, X_HOUSE, X_GK, X_DASH = 40, 80, 120, 160, 200, 240, 280, 320

_n = [0]


def nm(p):
    _n[0] += 1
    return f"{p}.{_n[0]}"


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


class K:
    kit = None


def P(hexc, rough=0.5, spec=0.35):
    return K.kit.plastic(hexc, rough, spec=spec)


def M(hexc, rough=0.3):
    return K.kit.metal(hexc, rough)


def B(parent, size, loc, mat, name="b", bevel=0.006, rot=(0, 0, 0)):
    return K.kit.box(nm(name), size, loc, mat, parent, rot, bevel)


def E(parent, loc=(0, 0, 0), name="e", rot=(0, 0, 0)):
    return K.kit.empty(nm(name), loc, parent, rot)


def CY(parent, r, h, loc, mat, name="c", rot=(0, 0, 0), n=28, r2=None):
    return K.kit.cyl(nm(name), r, h, loc, mat, parent, rot, n, r2)


def SP(parent, r, loc, mat, name="s", scale=(1, 1, 1)):
    o = K.kit.sphere(nm(name), r, loc, mat, parent, 14)
    o.scale = scale
    return o


def EM(hexc, strength=1.0):
    return K.kit.emit(hexc, strength)


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


# ------------------------------------------------------------------------------------------------ the tag
def make_images():
    from PIL import Image, ImageDraw

    W, H = 1024, 640
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, W - 7, H - 7], 70, fill=(255, 244, 214, 255), outline=(60, 40, 20, 255), width=14)
    d.ellipse([W // 2 - 400, 40, W // 2 - 400 + 60, 100], fill=(0, 0, 0, 0), outline=(60, 40, 20, 255), width=10)
    # the cookie glyph: a gold folded crescent with a crack and a slip
    cx, cy = 235, 330
    d.ellipse([cx - 175, cy - 130, cx + 175, cy + 130], fill=(214, 150, 40, 255), outline=(90, 52, 12, 255), width=14)
    d.ellipse([cx - 175, cy - 40, cx + 175, cy + 230], fill=(255, 244, 214, 255))
    d.pieslice([cx - 175, cy - 130, cx + 175, cy + 130], 180, 360, fill=(232, 184, 90, 255), outline=(90, 52, 12, 255),
               width=14)
    d.line([cx - 120, cy + 10, cx + 130, cy + 10], fill=(90, 52, 12, 255), width=14)
    d.rectangle([cx - 20, cy - 175, cx + 170, cy - 120], fill=(255, 255, 255, 255), outline=(90, 52, 12, 255), width=8)
    # three dots: Wednesday, Thursday, Friday (a track and a bigger last dot)
    d.line([580, 395, 940, 395], fill=(90, 52, 12, 255), width=10)
    for i, (x, r) in enumerate(((590, 44), (760, 44), (930, 58))):
        d.ellipse([x - r, 395 - r, x + r, 395 + r], fill=(255, 255, 255, 255), outline=(90, 52, 12, 255), width=14)
    im.save(TMP / "tag.png")
    # the needle: a red downward triangle
    n = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    g = ImageDraw.Draw(n)
    g.polygon([(128, 250), (28, 40), (228, 40)], fill=(226, 56, 48, 255), outline=(90, 20, 14, 255))
    g.line([(128, 250), (28, 40), (228, 40), (128, 250)], fill=(90, 20, 14, 255), width=14)
    n.save(TMP / "needle.png")
    # a gold dot (a day done)
    f = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    ImageDraw.Draw(f).ellipse([20, 20, 236, 236], fill=(255, 190, 40, 255), outline=(90, 52, 12, 255), width=20)
    f.save(TMP / "fill.png")
    # the handset (a phone ringing): a green disc and a white handset
    h = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    g = ImageDraw.Draw(h)
    g.ellipse([8, 8, 248, 248], fill=(60, 200, 90, 255))
    g.arc([60, 60, 200, 200], 200, 340, fill=(255, 255, 255, 255), width=34)
    g.ellipse([46, 120, 92, 166], fill=(255, 255, 255, 255))
    g.ellipse([164, 120, 210, 166], fill=(255, 255, 255, 255))
    h.save(TMP / "handset.png")
    return {k: str(TMP / f"{k}.png") for k in ("tag", "needle", "fill", "handset")}


def rgba_mat(kit, name, path, strength=1.0):
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path)
    tex.image.alpha_mode = "STRAIGHT"
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["Generated"], tex.inputs["Vector"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    ms = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tex.outputs["Alpha"], ms.inputs["Fac"])
    nt.links.new(tr.outputs[0], ms.inputs[1])
    nt.links.new(em.outputs[0], ms.inputs[2])
    nt.links.new(ms.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    return m


# the tag in camera space (mm on the sensor, 13.5 wide x 24 tall): centre, size
TAG_C, TAG_S = (-3.75, 9.0), (5.2, 3.25)
DOT_X = (590 / 1024, 760 / 1024, 930 / 1024)


def build_tag(kit, ctx):
    cam = kit.OBJ["cam"]
    im = make_images()
    ctx["imgs"] = im
    parts = {}
    for key, strength in (("tag", 1.5), ("needle", 1.4), ("fill", 1.3)):
        parts[key] = rgba_mat(kit, nm("tag-" + key), im[key], strength)
    ctx["tag"] = {"bg": kit.plane(nm("tagbg"), (1, 1), (0, 0, -0.15), parts["tag"], cam),
                  "needle": kit.plane(nm("tagneedle"), (1, 1), (0, 0, -0.15), parts["needle"], cam),
                  "fills": [kit.plane(nm("tagfill"), (1, 1), (0, 0, -0.15), parts["fill"], cam) for _ in range(3)]}
    for o in [ctx["tag"]["bg"], ctx["tag"]["needle"]] + ctx["tag"]["fills"]:
        no_shadow(o)


def place_tag(ctx, lens, day):
    t = ctx["tag"]
    cx, cy = TAG_C
    sw, sh = TAG_S

    def put(ob, x, y, w, h, depth):
        u = depth / lens
        ob.location = (x * u, y * u, -depth)
        ob.scale = (w * u, h * u, 1)

    put(t["bg"], cx, cy, sw, sh, 0.15)
    ys = cy - sh * (0.62 - 0.5)          # the track y
    xs = [cx + sw * (f - 0.5) for f in DOT_X]
    nx = lerp(xs[0], xs[2], min(2.0, max(0.0, day)) / 2.0)
    put(t["needle"], nx, ys + sh * 0.17, sh * 0.2, sh * 0.2, 0.146)
    for i, f in enumerate(t["fills"]):
        f.hide_render = day < i - 0.02
        put(f, xs[i], ys, sh * 0.12, sh * 0.12, 0.148)


# ------------------------------------------------------------------------------------------------ small things
def cookie(parent, name="cookie"):
    """A fortune cookie: a folded gold crescent with a crack and a slip (gray bars) sticking out. Origin: bottom."""
    R = E(parent, (0, 0, 0), name)
    g1, g2 = P(GOLD, 0.55), P("#d89a3c", 0.6)
    SP(R, 0.1, (0, 0, 0.06), g1, "ckb", (1.15, 0.8, 0.62))
    SP(R, 0.075, (0.07, 0, 0.065), g2, "ckf", (1.0, 1.0, 0.75))
    B(R, (0.17, 0.014, 0.012), (-0.015, -0.002, 0.118), P("#8a5a1c", 0.7), "ckc", 0.004, rot=(0, 0.0, 0.15))
    sl = B(R, (0.16, 0.05, 0.006), (-0.15, -0.02, 0.075), P(SLIP, 0.6), "cks", 0.002, rot=(0, -0.25, 0.1))
    for i, ln in enumerate((0.12, 0.09, 0.06)):
        B(sl, (ln, 0.007, 0.004), (-0.012 - (0.12 - ln) / 2, 0.012 - 0.012 * i, 0.005), P("#9a9aa0", 0.7), "ckg", 0.001)
    return R


def slip_obj(parent, name, base, kind, lines=4):
    """A paper strip, 0.3 x 0.085 m. kind 'blue' draws scribble lines (shown progressively); returns (root, lines)."""
    R = E(parent, (0, 0, 0), name)
    B(R, (0.30, 0.085, 0.006), (0, 0, 0), P(base, 0.6), "slipb", 0.0015)
    rows = []
    for r in range(lines):
        row = E(R, (0, 0, 0.0045), "row")
        y = 0.028 - r * 0.018
        for k in range(15):
            x = -0.125 + k * 0.0175
            B(row, (0.022, 0.005, 0.0016), (x, y + (0.004 if k % 2 else -0.004), 0), P(BLUE, 0.6, 0.1), "sc", 0.0004,
              rot=(0, 0, (0.7 if k % 2 else -0.7)))
        rows.append(row)
    return R, rows


def phone_obj(parent, imgs):
    R = E(parent, (0, 0, 0), "phone")
    B(R, (0.1, 0.19, 0.012), (0, 0, 0), P("#22242e", 0.35), "ph", 0.01)
    scr = B(R, (0.088, 0.17, 0.002), (0, 0, 0.0075), EM("#1c2438", 1.0), "scr", 0.0)
    ring = K.kit.plane(nm("ring"), (0.085, 0.085), (0, 0.0, 0.0094), rgba_mat(K.kit, nm("hs"), imgs["handset"], 1.2), R)
    face = K.kit.plane(nm("callface"), (0.086, 0.086), (0, 0.0, 0.0095), None, R)
    return R, ring, face, scr


def goose(parent):
    R = E(parent, (0, 0, 0), "goose")
    w = P("#fafafa", 0.6)
    o = P("#f08a1e", 0.5)
    B(R, (0.3, 0.55, 0.28), (0, 0, 0.42), w, "gb", 0.08)
    B(R, (0.16, 0.2, 0.2), (0, -0.28, 0.6), w, "gt", 0.04)
    B(R, (0.1, 0.1, 0.38), (0, -0.33, 0.72), w, "gn", 0.03)
    B(R, (0.13, 0.13, 0.12), (0, -0.34, 0.94), w, "gh", 0.04)
    B(R, (0.07, 0.14, 0.04), (0, -0.44, 0.93), o, "gk", 0.01)
    B(R, (0.1, 0.1, 0.02), (0.0, 0.32, 0.5), P("#bdbdbd", 0.6), "gtail", 0.01, rot=(-0.4, 0, 0))
    for sx in (-1, 1):
        B(R, (0.03, 0.03, 0.28), (sx * 0.08, 0, 0.14), o, "gl", 0.008)
        B(R, (0.08, 0.14, 0.02), (sx * 0.08, -0.04, 0.01), o, "gf", 0.006)
    return R


# ------------------------------------------------------------------------------------------------ places
def room(kit, ox, w, d, h, wall, floor, floor_mat=None, front=False):
    """A room whose back wall is at y = d (camera side open). Returns nothing: the pieces are plain boxes."""
    B(None, (w, d + 2, 0.1), (ox, d / 2 - 1, -0.05), floor_mat or P(floor, 0.5), "floor", 0.0)
    B(None, (w, d + 2, 0.1), (ox, d / 2 - 1, h + 0.05), P("#fffaf0", 0.9), "ceil", 0.0)
    B(None, (0.2, d + 2, h), (ox - w / 2, d / 2 - 1, h / 2), P(wall, 0.7, 0.1), "wallL", 0.0)
    B(None, (0.2, d + 2, h), (ox + w / 2, d / 2 - 1, h / 2), P(wall, 0.7, 0.1), "wallR", 0.0)


def wall_with_holes(ox, y, h, w, wallc, holes):
    """The back wall at y with rectangular holes [(x0, x1, z0, z1)] (x relative to ox)."""
    m = P(wallc, 0.7, 0.1)
    xs = sorted({-w / 2, w / 2} | {a for hl in holes for a in hl[:2]})
    for x0, x1 in zip(xs, xs[1:]):
        hs = [hl for hl in holes if hl[0] <= x0 + 1e-6 and hl[1] >= x1 - 1e-6]
        zs = sorted({0, h} | {z for hl in hs for z in hl[2:]})
        for z0, z1 in zip(zs, zs[1:]):
            if any(hl[2] <= z0 + 1e-6 and hl[3] >= z1 - 1e-6 for hl in hs):
                continue
            B(None, (x1 - x0, 0.2, z1 - z0), (ox + (x0 + x1) / 2, y, (z0 + z1) / 2), m, "wallB", 0.0)


def build_station(kit, ctx):
    B(None, (300, 160, 0.1), (0, 40, -0.1), P("#6fcf72", 0.9, 0.05), "field", 0.0)
    B(None, (40, 18, 0.1), (0, 0.5, -0.04), P("#cfd0d2", 0.8, 0.05), "apron", 0.0)
    B(None, (300, 7, 0.1), (0, -9.5, -0.045), P("#4b4d55", 0.9, 0.05), "road", 0.0)
    for i in range(-14, 15):
        B(None, (1.6, 0.18, 0.02), (i * 3.2, -9.5, 0.0), P("#f5d44a", 0.6), "dash", 0.0)
    B(None, (300, 0.4, 14), (0, 80, 5.0), kit.emit("#9bd8ff", 1.2, name="stsky"), "stsky", 0.0)
    for x, y, s in ((-9, 26, 3.0), (7, 30, 3.4), (-20, 36, 3.0), (15, 24, 3.0), (-3, 40, 3.6)):
        try:
            kit.prop("commontree_1", (x, y, 0), height=s * 1.6)
        except Exception:
            pass
    # the shop: a small white box with a big window
    B(None, (8.0, 4.0, 3.4), (-0.5, 12.2, 1.7), P(WHITE, 0.6), "shop", 0.01)
    B(None, (8.4, 4.4, 0.3), (-0.5, 12.2, 3.5), P(PUMP, 0.5), "shoproof", 0.01)
    B(None, (5.0, 0.1, 1.8), (-0.5, 10.14, 1.6), kit.emit("#bfe3f2", 1.0, name="shopwin"), "shopwin", 0.0)
    B(None, (5.2, 0.12, 0.1), (-0.5, 10.12, 2.55), P("#dcdad2", 0.5), "swf", 0.0)
    B(None, (5.2, 0.12, 0.1), (-0.5, 10.12, 0.68), P("#dcdad2", 0.5), "swf", 0.0)
    B(None, (1.0, 0.12, 2.1), (2.6, 10.12, 1.05), P("#7fa8c8", 0.4), "shopdoor", 0.01)
    # canopy
    roof = B(None, (9.0, 5.4, 0.3), (0.0, 3.4, 4.3), P(WHITE, 0.6), "canopy", 0.01)
    no_shadow(roof)
    stripe = B(None, (9.0, 0.1, 0.34), (0.0, 0.66, 4.3), P(PUMP, 0.5), "cstripe", 0.0)
    no_shadow(stripe)
    for x, y in ((-4.2, 1.2), (4.2, 1.2), (-4.2, 5.6), (4.2, 5.6)):
        CY(None, 0.18, 4.2, (x, y, 2.1), P(WHITE, 0.6), "col")
    # pumps (pump two, at x 0.4, carries the holster with two gold strokes)
    for k, x in enumerate((-2.0, 0.4)):
        R = E(None, (x, 3.0, 0), "pump")
        B(R, (0.8, 0.55, 1.5), (0, 0, 0.75), P(PUMP, 0.4), "pumpb", 0.03)
        B(R, (0.86, 0.6, 0.1), (0, 0, 1.55), P("#d8d8d8", 0.4), "pumpt", 0.02)
        B(R, (0.6, 0.02, 0.4), (0, -0.28, 1.15), P("#20242c", 0.3), "pumpd", 0.0)
        CY(R, 0.17, 0.02, (0, -0.296, 1.15), P("#fffaf0", 0.4), "gauge", rot=(math.pi / 2, 0, 0))
        B(R, (0.012, 0.012, 0.13), (-0.055, -0.31, 1.17), P("#e23a3a", 0.4), "needle", 0.0, rot=(0, 0.9, 0))
        B(R, (0.6, 0.02, 0.2), (0, -0.28, 0.82), P("#f2f2ee", 0.5), "pumpp", 0.0)
        CY(R, 0.05, 0.1, (0.0, -0.3, 0.9), P("#20242c", 0.5), "pumpr", rot=(math.pi / 2, 0, 0))
        hol = B(R, (0.16, 0.14, 0.34), (0.28, -0.36, 0.78), M("#cfd6dc", 0.2), "holster", 0.02)
        if k == 1:
            for i in range(2):
                B(R, (0.03, 0.01, 0.17), (0.24 + 0.08 * i, -0.438, 0.78), P(GOLD, 0.35), "tally", 0.004, rot=(0, 0.2, 0))
        B(R, (0.04, 0.04, 0.5), (0.34, -0.2, 1.1), P("#20242c", 0.5), "hose", 0.01)
    # Grandpa's pickup: teal, cab at the pump end (x 3.4..5.3), bed behind (x 5.3..7.8)
    tr = E(None, (0, 3.0, 0), "truck")
    tm, dk = P(TEAL, 0.35), P("#17202a", 0.2, 0.7)
    B(tr, (4.4, 1.9, 0.8), (5.6, 0, 0.7), tm, "tbody", 0.05)
    B(tr, (1.7, 1.8, 0.75), (4.3, 0, 1.45), tm, "tcab", 0.06)
    B(tr, (0.06, 1.5, 0.5), (3.44, 0, 1.5), dk, "twin", 0.01)
    B(tr, (1.3, 0.06, 0.45), (4.3, -0.91, 1.55), dk, "twin2", 0.01)
    B(tr, (2.6, 1.8, 0.4), (6.5, 0, 1.1), tm, "tbed", 0.02)
    B(tr, (2.5, 1.6, 0.05), (6.5, 0, 1.0), P("#2b3a44", 0.6), "bedf", 0.0)
    B(tr, (0.1, 1.5, 0.16), (3.4, 0, 0.6), M("#d9e1e8", 0.2), "bumper", 0.02)
    for sx in (4.3, 6.9):
        for sy in (-0.95, 0.95):
            CY(tr, 0.38, 0.28, (sx, sy, 0.38), P("#14161c", 0.8), "wheel", rot=(math.pi / 2, 0, 0))
            CY(tr, 0.2, 0.3, (sx, sy * 1.02, 0.38), M("#cfd6dc", 0.3), "hub", rot=(math.pi / 2, 0, 0))
    for sy in (-0.7, 0.7):
        B(tr, (0.06, 0.2, 0.14), (3.38, sy, 0.95), EM("#fff6d0", 1.2), "head", 0.01)
    ctx["lamps_day"] = []
    ctx["sun"] = kit.light("sun", "SUN", (0, 0, 50), 1.5, "#fff1d0", size=0.1)
    ctx["sun"].data.angle = 0.06
    az, el = math.radians(20), math.radians(42)
    pos = V((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    ctx["sun"].rotation_euler = (-pos).to_track_quat("-Z", "Y").to_euler()
    kit.light("st-fill", "POINT", (0, 1.0, 3.6), 260, "#fff4e0", size=1.0, shadow=False)
    # the phone's gas-pump gauge zero for S40 is the pump gauge above (needle left)


def build_shop(kit, ctx):
    ox = X_SHOP
    room(kit, ox, 7.0, 6.0, 3.0, "#fff3d6", "#d8c8a8", kit.checker("#f4efe4", "#c9d8e0", 1.4))
    wall_with_holes(ox, 6.1, 3.0, 7.0, "#ffe9b8", [])
    B(None, (0.12, 3.6, 1.6), (ox + 3.45, 3.3, 1.5), kit.emit("#bfe6ff", 1.2, name="shopw2"), "wind", 0.0)
    B(None, (0.14, 3.8, 0.1), (ox + 3.44, 3.3, 2.35), P("#dcdad2", 0.5), "wf", 0.0)
    B(None, (0.14, 3.8, 0.1), (ox + 3.44, 3.3, 0.65), P("#dcdad2", 0.5), "wf", 0.0)
    # shelves of plain coloured boxes on the back wall
    for r, z in enumerate((0.9, 1.5, 2.1)):
        B(None, (4.6, 0.3, 0.05), (ox - 0.4, 5.9, z), P("#8a5a34", 0.6), "shelf", 0.0)
        for k in range(9):
            c = ("#e2463f", "#4f8fd8", "#f1c24a", "#6dbb6a", "#b49ae0")[(k + r) % 5]
            B(None, (0.34, 0.2, 0.34), (ox - 2.4 + k * 0.5, 5.9, z + 0.2), P(c, 0.5), "box", 0.01)
    # counter
    B(None, (3.6, 0.8, 1.05), (ox, 3.0, 0.52), P("#b87a45", 0.5), "counter", 0.01)
    B(None, (3.8, 0.9, 0.06), (ox, 3.0, 1.07), P("#fdfbf6", 0.4), "ctop", 0.01)
    # the register and the jar of wrapped cookies
    B(None, (0.5, 0.4, 0.3), (ox + 1.2, 3.0, 1.25), P("#d5d9de", 0.4), "reg", 0.02)
    B(None, (0.42, 0.04, 0.22), (ox + 1.2, 2.8, 1.42), kit.emit("#2a3a5a", 0.8, name="regscr"), "regs", 0.0)
    ctx["drawer"] = B(None, (0.46, 0.12, 0.08), (ox + 1.2, 2.82, 1.14), P("#9aa0a8", 0.4), "drawer", 0.01)
    jar = CY(None, 0.27, 0.62, (ox - 1.0, 3.1, 1.43), kit.glass("#d8eef5"), "jar")
    no_shadow(jar)
    for i in range(36):
        a, rr = i * 2.4, 0.19 * ((i * 37) % 10) / 10
        z = 1.2 + 0.4 * ((i * 53) % 9) / 8
        B(None, (0.11, 0.08, 0.05), (ox - 1.0 + rr * math.cos(a), 3.1 + rr * math.sin(a), z), P(GOLD if i % 3 else "#d89a3c", 0.5),
          "jc", 0.012, rot=(0.3 * (i % 3), 0.2 * (i % 4), a))
    CY(None, 0.25, 0.04, (ox - 1.0, 3.1, 1.76), P("#c9c4b8", 0.4), "jarlid")
    kit.light("shop-key", "POINT", (ox, 1.6, 2.7), 110, "#fff4e0", size=0.8, shadow=False)
    kit.light("shop-back", "POINT", (ox, 4.6, 2.6), 70, "#fff0d0", size=0.8, shadow=False)


def build_tire(kit, ctx):
    ox = X_TIRE
    B(None, (40, 24, 0.1), (ox, 8, -0.05), P("#6a6d75", 0.9, 0.05), "tground", 0.0)
    B(None, (24, 0.3, 4.5), (ox, 8.0, 2.25), P("#4f8fd8", 0.6), "twall", 0.0)
    for i in range(10):
        B(None, (0.04, 0.34, 4.5), (ox - 10 + 2.2 * i, 7.83, 2.25), P("#3f7cc4", 0.7), "rib", 0.0)
    B(None, (12, 0.1, 2.0), (ox, 7.8, 5.5), kit.emit("#9bd8ff", 1.2, name="tsky"), "tsky", 0.0)
    # the car (side on) and its front wheel with a heavy tread
    B(None, (4.6, 1.8, 0.8), (ox - 1.6, 5.2, 0.85), P("#c9c4b8", 0.4), "car", 0.05)
    B(None, (2.4, 1.7, 0.7), (ox - 1.7, 5.2, 1.55), P("#b8b3a6", 0.4), "carc", 0.05)
    B(None, (1.4, 0.04, 0.5), (ox - 1.7, 4.32, 1.55), P("#17202a", 0.2, 0.7), "carw", 0.01)
    w = E(None, (ox + 0.2, 4.15, 0.62), "tire")
    CY(w, 0.62, 0.34, (0, 0, 0), P("#14161c", 0.85, 0.1), "tyre", rot=(math.pi / 2, 0, 0), n=40)
    CY(w, 0.33, 0.36, (0, -0.01, 0), M("#cfd6dc", 0.3), "hub", rot=(math.pi / 2, 0, 0))
    for k in range(18):
        a = 2 * math.pi * k / 18
        B(w, (0.1, 0.36, 0.13), (0.62 * math.cos(a), 0, 0.62 * math.sin(a)), P("#23262e", 0.9, 0.05), "tread", 0.01,
          rot=(0, -a, 0))
    ctx["tire"] = w
    bills = []
    for k, (ang, tilt) in enumerate(((40, 0.3), (70, -0.2), (100, 0.4), (130, -0.3))):
        a = math.radians(ang)
        rr = 0.7
        b = E(w, (rr * math.cos(a), -0.1 + 0.06 * (k % 2), rr * math.sin(a)), "bill", rot=(0, -a + 0.2 * tilt, 0))
        B(b, (0.2, 0.012, 0.09), (0.0, 0, 0), P("#7fcf86", 0.6), "bl", 0.002)
        B(b, (0.13, 0.014, 0.05), (0.0, -0.002, 0), P("#bff0c4", 0.6), "bl2", 0.002)
        bills.append(b)
    ctx["bills"] = bills
    for b in bills:
        hide(b, True)
    kit.light("tire-key", "POINT", (ox, 0.5, 3.2), 300, "#fff4e0", size=0.8, shadow=False)
    sun = kit.light("tire-sun", "POINT", (ox - 3, -1, 5), 300, "#fff1d0", size=1.0, shadow=False)


def build_lot(kit, ctx):
    ox = X_LOT
    B(None, (50, 30, 0.1), (ox, 10, -0.05), P("#5a5d66", 0.9, 0.05), "lground", 0.0)
    for i in range(-5, 6):
        B(None, (0.12, 2.6, 0.02), (ox + i * 2.6, 9.4, 0.0), P("#f5f2e8", 0.6), "pline", 0.0)
    B(None, (50, 0.3, 4.0), (ox, 16.0, 2.0), P("#f1d8a8", 0.7), "lwall", 0.0)
    B(None, (50, 0.1, 4.0), (ox, 15.8, 6.0), kit.emit("#a8dcff", 1.2, name="lsky"), "lsky", 0.0)
    for x, c in ((-6.5, "#e2463f"), (-3.2, "#4f8fd8"), (6.5, "#f1c24a")):
        B(None, (3.6, 1.7, 0.8), (ox + x, 12.5, 0.65), P(c, 0.4), "pcar", 0.05)
        B(None, (2.0, 1.6, 0.6), (ox + x - 0.2, 12.5, 1.25), P(c, 0.4), "pcarc", 0.05)
    kit.light("lot-key", "POINT", (ox, 1.0, 4.0), 320, "#fff4e0", size=1.0, shadow=False)
    kit.light("lot-sun", "POINT", (ox - 4, 2, 6), 360, "#fff1d0", size=1.0, shadow=False)
    gs = []
    for i in range(5):
        g = goose(None)
        hide(g, True)
        gs.append(g)
    ctx["geese"] = gs


def build_kitchen(kit, ctx):
    ox = X_KIT
    room(kit, ox, 8.0, 3.0, 2.9, "#fff0d4", "#d8bf94", kit.texture("wood", 0.7, tint="#f6dcae"))
    wall_with_holes(ox, 3.1, 2.9, 8.0, "#fff0d4", [(-1.1, 1.1, 0.95, 2.15)])
    for sx in (-1, 1):
        B(None, (0.1, 0.12, 1.3), (ox + sx * 1.15, 2.98, 1.55), P("#ffffff", 0.5), "wfr", 0.0)
    B(None, (2.4, 0.12, 0.1), (ox, 2.98, 2.17), P("#ffffff", 0.5), "wfr", 0.0)
    B(None, (2.4, 0.2, 0.1), (ox, 2.95, 0.93), P("#ffffff", 0.5), "wsill", 0.0)
    # cabinets and a small table
    B(None, (2.6, 0.7, 0.9), (ox - 2.7, 2.6, 0.45), P("#f1c24a", 0.5), "cab", 0.01)
    B(None, (2.7, 0.76, 0.05), (ox - 2.7, 2.6, 0.92), P("#fdfbf6", 0.4), "cabt", 0.01)
    B(None, (2.6, 0.5, 0.8), (ox - 2.7, 2.7, 2.0), P("#f1c24a", 0.5), "cabu", 0.01)
    B(None, (1.0, 0.9, 0.06), (ox + 2.7, 2.2, 0.78), P("#e9c9b0", 0.5), "ktable", 0.01)
    B(None, (0.8, 0.7, 0.72), (ox + 2.7, 2.2, 0.36), P("#e9c9b0", 0.5), "ktab2", 0.01)
    # outside: a quiet street
    B(None, (80, 40, 0.1), (ox, 25, -0.1), P("#7ed27c", 0.9, 0.05), "klawn", 0.0)
    B(None, (80, 5.0, 0.1), (ox, 8.5, -0.04), P("#4b4d55", 0.9, 0.05), "kroad", 0.0)
    for i in range(-8, 9):
        B(None, (1.2, 0.14, 0.02), (ox + i * 2.4, 8.5, 0.01), P("#f5f2e8", 0.6), "kdash", 0.0)
    B(None, (80, 2.0, 0.08), (ox, 5.6, -0.02), P("#cfd0d2", 0.8, 0.05), "kwalk", 0.0)
    B(None, (80, 0.4, 20), (ox, 55, 8), kit.emit("#9bd8ff", 1.2, name="ksky"), "ksky", 0.0)
    for x, nmz, h in ((-7, "sub_building_type_a", 5.0), (-1.5, "sub_building_type_c", 5.0), (5.5, "sub_building_type_f", 5.0)):
        try:
            kit.prop(nmz, (ox + x, 14.5, 0), height=h)
        except Exception:
            B(None, (4, 4, 4), (ox + x, 14.5, 2), P("#e8c9a0", 0.6), "house", 0.02)
    try:
        kit.prop("sub_tree_large", (ox + 3.0, 6.8, 0), height=4.5)
    except Exception:
        pass
    B(None, (3.6, 1.6, 0.8), (ox - 4.0, 10.5, 0.55), P("#4f8fd8", 0.4), "kcar", 0.05)
    B(None, (2.0, 1.5, 0.6), (ox - 4.1, 10.5, 1.1), P("#4f8fd8", 0.4), "kcarc", 0.05)
    kit.light("kit-key", "POINT", (ox, 0.6, 2.6), 300, "#fff4e0", size=0.8, shadow=False)
    kit.light("kit-sun", "POINT", (ox, 7.0, 6), 500, "#fff1d0", size=1.0, shadow=False)


def build_bed(kit, ctx):
    ox = X_BED
    room(kit, ox, 6.0, 4.0, 2.8, "#c9d8f0", "#8a6a4a", kit.texture("wood", 0.7, tint="#c8a070"))
    wall_with_holes(ox, 4.1, 2.8, 6.0, "#c9d8f0", [(1.4, 2.6, 1.0, 2.2)])
    B(None, (1.2, 0.1, 1.2), (ox + 2.0, 4.3, 1.6), kit.emit("#2c3f78", 0.9, name="bnight"), "bsky", 0.0)
    CY(None, 0.2, 0.04, (ox + 2.1, 4.24, 1.9), kit.emit("#f6f2d0", 2.0, name="moon"), "moon", rot=(math.pi / 2, 0, 0))
    for sx in (1.35, 2.65):
        B(None, (0.1, 0.12, 1.3), (ox + sx, 3.98, 1.6), P("#ffffff", 0.5), "bwf", 0.0)
    # the bed runs along y, head at the wall; blanket and pillow
    B(None, (1.3, 2.1, 0.4), (ox, 2.9, 0.3), P("#8a5a34", 0.6), "bedbase", 0.02)
    B(None, (1.3, 0.12, 1.1), (ox, 3.98, 0.7), P("#8a5a34", 0.6), "headb", 0.03)
    B(None, (1.24, 1.12, 0.26), (ox, 2.57, 0.62), P("#7dd1c4", 0.6), "blanket", 0.05)
    B(None, (0.9, 0.35, 0.16), (ox, 3.65, 0.58), P("#fffaf0", 0.7), "pillow", 0.06)
    # the nightstand with a lamp (steady)
    B(None, (0.55, 0.5, 0.6), (ox + 1.2, 3.55, 0.3), P("#b87a45", 0.5), "ns", 0.01)
    B(None, (0.5, 0.01, 0.1), (ox + 1.2, 3.29, 0.42), P("#8a5a34", 0.5), "nsd", 0.0)
    CY(None, 0.08, 0.04, (ox + 1.4, 3.55, 0.62), P("#7a5a3a", 0.5), "lampb")
    CY(None, 0.2, 0.28, (ox + 1.4, 3.55, 0.86), kit.emit("#ffd9a0", 2.2, name="shade"), "shade", r2=0.12)
    kit.light("bed-lamp", "POINT", (ox + 1.4, 3.1, 1.0), 40, "#ffcf90", size=0.4, shadow=False)
    kit.light("bed-moon", "POINT", (ox + 1.5, 3.2, 2.0), 25, "#a8b8ff", size=0.6, shadow=False)
    kit.light("bed-key", "POINT", (ox, 0.4, 2.2), 55, "#d8e0ff", size=0.8, shadow=False)


def build_house(kit, ctx):
    ox = X_HOUSE
    B(None, (80, 50, 0.1), (ox, 20, -0.1), P("#3f8a4a", 0.9, 0.05), "hground", 0.0)
    B(None, (80, 5, 0.1), (ox, -1.0, -0.04), P("#4b4d55", 0.9, 0.05), "hroad", 0.0)
    B(None, (80, 0.6, 30), (ox, 50, 12), kit.emit("#8aa6e0", 1.0, name="hsky"), "hsky", 0.0)
    B(None, (5.0, 3.6, 2.7), (ox, 8.0, 1.35), P("#e8d6b0", 0.6), "house", 0.02)
    B(None, (5.4, 2.2, 0.16), (ox - 0.0, 8.4, 3.0), P("#a8473f", 0.6), "roofa", 0.02, rot=(0.0, 0.0, 0))
    B(None, (5.4, 2.0, 0.16), (ox, 7.4, 3.25), P("#a8473f", 0.6), "roofb", 0.02, rot=(0.5, 0, 0))
    B(None, (5.4, 2.0, 0.16), (ox, 8.6, 3.25), P("#a8473f", 0.6), "roofc", 0.02, rot=(-0.5, 0, 0))
    B(None, (1.4, 0.06, 1.2), (ox - 1.0, 6.18, 1.5), EM("#ffcf80", 2.4), "hwin", 0.0)
    B(None, (1.5, 0.08, 0.08), (ox - 1.0, 6.17, 2.12), P("#ffffff", 0.5), "hwf", 0.0)
    B(None, (1.5, 0.08, 0.08), (ox - 1.0, 6.17, 0.88), P("#ffffff", 0.5), "hwf", 0.0)
    B(None, (0.08, 0.08, 1.3), (ox - 1.0, 6.17, 1.5), P("#ffffff", 0.5), "hwf", 0.0)
    B(None, (0.9, 0.08, 2.0), (ox + 1.3, 6.18, 1.0), P("#7a5a3a", 0.6), "hdoor", 0.01)
    B(None, (0.3, 0.1, 0.2), (ox + 1.3, 6.1, 2.25), EM("#ffe0a0", 2.0), "porchl", 0.0)
    B(None, (2.0, 0.4, 0.15), (ox + 0.2, 5.8, 0.08), P("#a8a8a8", 0.8), "step", 0.0)
    B(None, (7.0, 0.5, 0.06), (ox - 1.0, 5.2, 0.0), P("#b8b8b0", 0.8), "path", 0.0)
    for x, s in ((-6, 4.5), (5.5, 4.2), (-3.5, 3.2)):
        try:
            kit.prop("commontree_2", (ox + x, 12, 0), height=s)
        except Exception:
            pass
    # my car: a small blue car that drives in along y = 1.6
    car = E(None, (ox - 6, 1.6, 0), "car")
    B(car, (3.6, 1.7, 0.7), (0, 0, 0.6), P("#4f8fd8", 0.35), "cb", 0.05)
    B(car, (2.0, 1.6, 0.6), (-0.2, 0, 1.15), P("#4f8fd8", 0.35), "cc", 0.05)
    B(car, (1.6, 0.04, 0.45), (-0.2, -0.81, 1.18), P("#17202a", 0.2, 0.7), "cw", 0.01)
    for sx in (-1.1, 1.1):
        for sy in (-0.85, 0.85):
            CY(car, 0.3, 0.22, (sx, sy, 0.3), P("#14161c", 0.8), "cwh", rot=(math.pi / 2, 0, 0))
    for sy in (-0.6, 0.6):
        B(car, (0.06, 0.3, 0.16), (1.82, sy, 0.62), EM("#fff6d0", 2.4), "hl", 0.01)
    ctx["car"] = car
    kit.light("house-moon", "POINT", (ox, 0.0, 6), 700, "#8aa0e8", size=1.5, shadow=False)
    kit.light("house-win", "POINT", (ox - 1.0, 4.8, 1.5), 120, "#ffcf80", size=0.6, shadow=False)
    kit.light("house-car", "POINT", (ox - 2, -1.0, 2.0), 150, "#d8e0ff", size=0.8, shadow=False)


def build_gkitchen(kit, ctx):
    ox = X_GK
    room(kit, ox, 8.0, 8.4, 2.9, "#fff0c8", "#c9a070", kit.texture("wood", 0.7, tint="#e8c890"))
    # the back wall between the kitchen and the living room (y 4.2): a doorway and the snowy window
    wall_with_holes(ox, 4.2, 2.9, 8.0, "#ffe9a8", [(-0.7, 1.0, 0, 2.25), (-2.7, -1.3, 0.95, 2.15)])
    B(None, (8.0, 0.2, 2.9), (ox, 8.5, 1.45), P("#e8d0f0", 0.7, 0.1), "lback", 0.0)
    B(None, (4.0, 0.12, 0.1), (ox - 2.0, 4.08, 2.2), P("#ffffff", 0.5), "wfr", 0.0)
    B(None, (1.4, 0.2, 0.08), (ox - 2.0, 4.05, 0.92), P("#ffffff", 0.5), "wsill", 0.0)
    for x in (-2.72, -1.28):
        B(None, (0.08, 0.1, 1.25), (ox + x, 4.08, 1.55), P("#ffffff", 0.5), "wfr", 0.0)
    for x in (-0.72, 1.02):
        B(None, (0.08, 0.1, 2.25), (ox + x, 4.08, 1.12), P("#ffffff", 0.5), "dfr", 0.0)
    B(None, (1.8, 0.1, 0.08), (ox + 0.15, 4.08, 2.27), P("#ffffff", 0.5), "dfr", 0.0)
    # outside the window: night, or the big storm
    ctx["snowmat"] = kit.emit("#0b1228", 1.0, name="gnight")
    ctx["snowpane"] = B(None, (1.6, 0.06, 1.3), (ox - 2.0, 4.8, 1.55), ctx["snowmat"], "snowp", 0.0)
    ctx["snowmat2"] = kit.emit("#eaf2ff", 2.4, name="gsnow")
    ctx["snowpane2"] = B(None, (1.6, 0.06, 1.3), (ox - 2.0, 4.7, 1.55), ctx["snowmat2"], "snowp2", 0.0)
    hide(ctx["snowpane2"], True)
    flakes = []
    for i in range(36):
        f = B(None, (0.035, 0.035, 0.035), (ox - 2.0, 4.55, 1.5), EM("#ffffff", 3.0), "flake", 0.0)
        no_shadow(f)
        hide(f, True)
        flakes.append(f)
    ctx["flakes"] = flakes
    # the table: a yellow block with a skirt (people sit behind it), two chairs, the lamp above
    B(None, (1.6, 0.95, 0.68), (ox, 1.9, 0.34), P(KY, 0.45), "tabl", 0.02)
    B(None, (1.7, 1.05, 0.06), (ox, 1.9, 0.71), P("#e3c06a", 0.5, 0.15), "tabt", 0.02)
    for sx in (-1, 1):
        B(None, (0.12, 0.7, 0.08), (ox + sx * 0.35, 1.9, 0.76), P("#ffb94d", 0.5), "runner", 0.0)
    B(None, (0.7, 0.08, 0.9), (ox, 3.45, 0.55), P("#b87a45", 0.5), "chairb", 0.03)
    B(None, (0.7, 0.7, 0.08), (ox, 3.1, 0.34), P("#b87a45", 0.5), "chairs", 0.03)
    B(None, (0.7, 0.08, 0.9), (ox, 0.6, 0.55), P("#b87a45", 0.5), "chairb2", 0.03)
    CY(None, 0.02, 0.9, (ox, 1.9, 2.45), P("#2a2a2a", 0.5), "cord")
    CY(None, 0.34, 0.2, (ox, 1.9, 1.95), kit.emit("#ffe3a0", 1.3, name="cshade"), "cshade", r2=0.12)
    kit.light("kit-lamp", "POINT", (ox, 1.9, 1.7), 60, "#ffe3b0", size=0.4, shadow=False)
    # the living room: Grandma's green armchair and the floor lamp
    B(None, (1.0, 0.95, 0.5), (ox + 0.2, 4.85, 0.25), P("#4f8f5a", 0.6), "armch", 0.06)
    B(None, (1.0, 0.22, 0.95), (ox + 0.2, 5.27, 0.7), P("#4f8f5a", 0.6), "armb", 0.06)
    for sx in (-1, 1):
        B(None, (0.2, 0.95, 0.65), (ox + 0.2 + sx * 0.5, 4.85, 0.42), P("#3f7a4a", 0.6), "arma", 0.05)
    B(None, (0.5, 0.06, 0.4), (ox + 0.2, 4.41, 0.58), P("#6fb07a", 0.6), "armcushion", 0.04)
    B(None, (2.6, 1.8, 0.03), (ox + 0.2, 4.3, 0.016), P("#d9758a", 0.8), "rug", 0.0)
    CY(None, 0.025, 1.5, (ox + 1.5, 5.2, 0.75), P("#2a2a2a", 0.5), "flpole")
    CY(None, 0.22, 0.34, (ox + 1.5, 5.2, 1.62), kit.emit("#ffe0b0", 2.2, name="fshade"), "fshade", r2=0.14)
    kit.light("floor-lamp", "POINT", (ox + 1.2, 4.8, 1.6), 70, "#ffd9a0", size=0.4, shadow=False)
    B(None, (1.4, 0.4, 0.9), (ox - 2.4, 8.2, 0.45), P("#c9a070", 0.5), "lshelf", 0.02)
    # on the table: the wallet, the pen
    ctx["wallet"] = B(None, (0.2, 0.14, 0.045), (ox - 0.3, 1.7, 0.77), P("#6a3f1f", 0.7), "wallet", 0.02)
    ctx["pen"] = B(None, (0.15, 0.014, 0.014), (ox + 0.3, 1.65, 0.77), P("#2a56d6", 0.4), "pen", 0.004)
    kit.light("gk-fill", "POINT", (ox, 0.3, 2.4), 40, "#ffe8c0", size=0.8, shadow=False)


def build_dash(kit, ctx):
    ox = X_DASH
    B(None, (14, 0.2, 7), (ox, 12, 2.5), kit.emit("#bde6ff", 1.3, name="dskyb"), "dsky", 0.0)
    B(None, (14, 8, 0.1), (ox, 8, -0.05), P("#6fcf72", 0.9, 0.05), "dgr", 0.0)
    B(None, (3.2, 0.7, 0.55), (ox, 0.55, 0.95), P("#1f6f68", 0.6), "dash", 0.03)
    B(None, (3.2, 0.5, 0.1), (ox, 0.45, 1.27), P("#14383a", 0.6), "dashtop", 0.03)
    B(None, (0.12, 0.6, 1.5), (ox - 1.5, 1.0, 1.7), P(TEAL, 0.4), "pillar", 0.02)
    B(None, (0.12, 0.6, 1.5), (ox + 1.5, 1.0, 1.7), P(TEAL, 0.4), "pillar", 0.02)
    B(None, (3.2, 1.2, 0.12), (ox, 1.0, 2.5), P(TEAL, 0.4), "droof", 0.02)
    wheel = E(None, (ox - 0.7, 0.2, 1.12), "wheel")
    for (dx, dz, sx, sz) in ((0, 0.22, 0.5, 0.07), (0, -0.22, 0.5, 0.07), (-0.22, 0, 0.07, 0.5), (0.22, 0, 0.07, 0.5)):
        B(wheel, (sx, 0.06, sz), (dx, 0, dz), P("#17202a", 0.5), "swh", 0.02)
    # the slip taped on the dashboard's face: two gold strips of tape
    kit.light("dash-key", "POINT", (ox, -1.2, 2.2), 140, "#fff4e0", size=0.8, shadow=False)
    kit.light("dash-sun", "POINT", (ox - 1, 3, 3.2), 150, "#fff1d0", size=1.0, shadow=False)


# ------------------------------------------------------------------------------------------------ characters' extras
def late_extras(kit, ctx):
    """After the cast exists: Grandpa's white mustache, the clerk's ponytail. (Set once.)"""
    c = rig.CHARS.get("grandpa")
    if c is not None:
        hg = c.head.children[0]
        B(hg, (0.62, 0.1, 0.13), (0, -faces.HEAD_R - 0.02, -0.17), P("#f4f4f4", 0.8), "must", 0.04)
        for sx in (-1, 1):
            B(hg, (0.14, 0.1, 0.1), (sx * 0.3, -faces.HEAD_R - 0.0, -0.24), P("#f4f4f4", 0.8), "mustc", 0.03)
    c = rig.CHARS.get("clerk")
    if c is not None:
        hg = c.head.children[0]
        B(hg, (0.3, 0.3, 0.7), (0, faces.HEAD_R + 0.2, 0.0), P("#5a3a22", 0.7), "pony", 0.08, rot=(0.3, 0, 0))
    ctx["extras"] = True


LOOKS = {"day": {"bg": 0.7, "sun": 1.5}, "night": {"bg": 0.12, "sun": 0.0}}


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


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    K.kit = kit
    ctx = {"story": story, "shots": {s["id"]: s for s in story["shots"]}, "extras": False}
    build_station(kit, ctx)
    build_shop(kit, ctx)
    build_tire(kit, ctx)
    build_lot(kit, ctx)
    build_kitchen(kit, ctx)
    build_bed(kit, ctx)
    build_house(kit, ctx)
    build_gkitchen(kit, ctx)
    build_dash(kit, ctx)
    # the movable props
    ctx["cookies"] = {}
    for key in ("cookie", "cookie2"):
        c = cookie(None, key)
        hide(c, True)
        ctx["cookies"][key] = c
    ctx["slips"] = {}
    for key, base, lines, strip in (("slip_ck", SLIP, 0, None), ("slip_mine", SLIP, 4, None), ("slip_gp", OLD, 4, None),
                                    ("slip_tape", SLIP, 4, None)):
        r, rows = slip_obj(None, key, base, "blue", lines)
        hide(r, True)
        ctx["slips"][key] = (r, rows)
    # the printed strip on a loose slip: gray bars
    ck_loose, _ = ctx["slips"]["slip_ck"]
    for i, ln in enumerate((0.22, 0.17, 0.1)):
        B(ck_loose, (ln, 0.01, 0.003), (-0.14 + ln / 2 - 0.0, 0.025 - 0.02 * i, 0.0045), P("#9a9aa0", 0.7), "grayb", 0.001)
    imgs = make_images()
    ph, ring, cface, scr = phone_obj(None, imgs)
    gp = story["cast"]["grandpa"]
    fim = faces.face_image(gp["face"], gp["skin"], "smile").crop((faces.FX0, faces.FY0, faces.FX1, faces.FY1))
    fim = fim.convert("RGBA").resize((512, int(512 * fim.height / fim.width)))
    fim.save(TMP / "callface.png")
    cface.data.materials.clear()
    cface.data.materials.append(rgba_mat(kit, nm("callface"), str(TMP / "callface.png"), 1.0))
    cface.scale = (1.0, fim.width / fim.height, 1.0)
    hide(ph, True)
    ctx["phone"] = (ph, ring, cface, scr)
    # a can of soda
    sd = E(None, (0, 0, 0), "soda")
    CY(sd, 0.045, 0.14, (0, 0, 0.07), P("#e2463f", 0.35), "sodab")
    CY(sd, 0.047, 0.04, (0, 0, 0.07), P("#fffaf0", 0.4), "sodaw")
    CY(sd, 0.036, 0.01, (0, 0, 0.145), M("#cfd6dc", 0.2), "sodat")
    hide(sd, True)
    ctx["soda"] = sd
    ctx["fill"] = kit.light("camfill", "POINT", (0, 0, 2), 40, "#fff0dc", size=0.6, shadow=False)
    build_tag(kit, ctx)
    ctx["bg"] = bpy.context.scene.world.node_tree.nodes["Background"]
    ctx["call_img"] = None
    return ctx


def mover(c, t):
    """Position / rotation of a cue-driven prop at t: pos -> pos2 over dur, rot -> rot2 likewise."""
    u = ss((t - c["t"]) / max(1e-3, c.get("dur", 1.0))) if "pos2" in c or "rot2" in c else 0.0
    p0, p1 = c["pos"], c.get("pos2", c["pos"])
    r0, r1 = c.get("rot", [0, 0, 0]), c.get("rot2", c.get("rot", [0, 0, 0]))
    return [lerp(a, b, u) for a, b in zip(p0, p1)], [math.radians(lerp(a, b, u)) for a, b in zip(r0, r1)]


def animate(kit, story, tl, t, ctx):
    if not ctx["extras"]:
        late_extras(kit, ctx)
    sc = bpy.context.scene
    gp = rig.CHARS.get("grandpa")
    if gp is not None:
        for ob in gp.head.children_recursive:
            if ob.name.startswith("must"):
                ob.hide_render = gp.root.hide_render
    L, cur = look_at(ctx, tl, t)
    sd = ctx["shots"][cur["id"]]
    ctx["bg"].inputs["Strength"].default_value = L["bg"]
    ctx["sun"].data.energy = L["sun"]
    cl, _, lens, _ = bl_story.cam_at(sd, cur, t, {}, tl)
    ctx["fill"].location = (cl[0], cl[1], cl[2])
    sc.view_settings.exposure = sd.get("exp", 0.0)
    ov = {"camfill": sd.get("fill", 1.0)}
    # ---- the tag
    dc = cue_at(tl, "day", t)
    day = dc.get("v", 0.0)
    if dc.get("v2") is not None:
        day = lerp(dc["v"], dc["v2"], ss((t - dc["t"]) / max(1e-3, dc.get("dur", 1.0))))
    place_tag(ctx, lens, day)
    # ---- cookies
    for key, c in ctx["cookies"].items():
        cu = cue_at(tl, key, t)
        if not cu.get("on"):
            hide(c, True)
            continue
        hide(c, False)
        p, r = mover(cu, t)
        c.location, c.rotation_euler = p, r
        c.scale = (cu.get("s", 1.0),) * 3
    # ---- slips
    for key, (root, rows) in ctx["slips"].items():
        cu = cue_at(tl, key, t)
        if not cu.get("on"):
            hide(root, True)
            continue
        hide(root, False)
        p, r = mover(cu, t)
        root.location, root.rotation_euler = p, r
        root.scale = (cu.get("s", 1.0),) * 3
        prog = cu.get("prog", 0.0)
        if "prog2" in cu:
            prog = lerp(prog, cu["prog2"], ss((t - cu["t"]) / max(1e-3, cu.get("dur", 1.0))))
        for i, row in enumerate(rows):
            hide(row, prog < (i + 0.5) / len(rows) - 1e-6)
    # ---- the phone
    ph, ring, cface, scr = ctx["phone"]
    pc = cue_at(tl, "phone", t)
    if not pc.get("on"):
        hide(ph, True)
    else:
        hide(ph, False)
        p, r = mover(pc, t)
        shake = 0.004 * math.sin(t * 38) if pc.get("mode") == "ring" else 0.0
        ph.location = (p[0] + shake, p[1], p[2])
        ph.rotation_euler = r
        ph.scale = (pc.get("s", 1.0),) * 3
        ring.hide_render = pc.get("mode") != "ring"
        cface.hide_render = pc.get("mode") != "call"
    # ---- the soda
    sc_ = cue_at(tl, "soda", t)
    if sc_.get("on"):
        hide(ctx["soda"], False)
        p, r = mover(sc_, t)
        ctx["soda"].location, ctx["soda"].rotation_euler = p, r
        ctx["soda"].scale = (sc_.get("s", 1.0),) * 3
    else:
        hide(ctx["soda"], True)
    # ---- wallet and pen
    hide(ctx["wallet"], not cue_at(tl, "wallet", t).get("on", True))
    hide(ctx["pen"], not cue_at(tl, "pen", t).get("on", False))
    # ---- the register drawer
    dc2 = cue_at(tl, "drawer", t)
    ctx["drawer"].location = (X_SHOP + 1.2, 2.82 - (0.14 * math.sin(math.pi * min(1.0, (t - dc2["t"]) / 0.4)) if dc2 and t - dc2["t"] < 0.4 else 0.0), 1.14)
    # ---- forty dollars in the tread
    on = cue_at(tl, "bills", t).get("on", False)
    for b in ctx["bills"]:
        hide(b, not on)
    # ---- the geese follow the woman
    gc = cue_at(tl, "geese", t)
    for i, g in enumerate(ctx["geese"]):
        if not gc.get("on"):
            hide(g, True)
            continue
        u = (t - gc["t"]) / max(1e-3, gc["dur"])
        lead = lerp(gc["x0"], gc["x1"], u)
        d = 1.0 if gc["x1"] > gc["x0"] else -1.0
        x = lead - d * (1.0 + 0.8 * i)
        y = gc["y"] + 0.12 * math.sin(i * 1.7 + t * 2.0)
        vis = (gc["x0"] - 0.1 <= x <= gc["x1"] + 0.1) or u > 0.0
        hide(g, not vis)
        g.location = (x, y, 0.03 * abs(math.sin(t * 7.0 + i)))
        g.rotation_euler = (0, 0.06 * math.sin(t * 7.0 + i), math.radians(-90 * d))
    # ---- my car drives up
    cc = cue_at(tl, "car", t)
    if cc:
        u = ss((t - cc["t"]) / max(1e-3, cc["dur"]))
        ctx["car"].location = (lerp(cc["x0"], cc["x1"], u), 1.6, 0)
    # ---- the snow (the big storm), only in the kitchen window
    sn = cue_at(tl, "snow", t).get("on", False)
    hide(ctx["snowpane2"], not sn)
    for i, f in enumerate(ctx["flakes"]):
        hide(f, not sn)
        if sn:
            ph_ = (t * 0.7 + i / len(ctx["flakes"])) % 1.0
            f.location = (X_GK - 2.0 + 0.7 * math.sin(i * 2.3 + t * 0.9), 4.55, 2.15 - 1.2 * ph_)
    cd = kit.OBJ["cam"].data
    cd.dof.use_dof = False
    return ov
