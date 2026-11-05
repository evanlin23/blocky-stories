"""ep125-aunts-keys: Aunt Lou has a key to every house on the court; the one walking it at midnight is me, asleep.

One bright, warm, plastic world (the "closer" look). A horseshoe of twelve narrow red-brick houses round a stone
fountain, a steady brass carriage lamp on every door, ivy, painted doors. Number one (Aunt Lou's) is a teal door with a
brass knocker, a brass numeral plate and two amber strokes under it, red geraniums, a striped mat, a carriage lamp and
a hall behind the door; number seven is butter yellow. Indoors is one closed room (the ROOM) with five stages along its
walls, each lit by its own steady lamp, and Mr. Ames's window.

NOTHING BLINKS, PULSES OR FLICKERS: every carriage lamp and every room lamp is on at the same strength in every frame.
The only light change in the film is the slow sunrise at L48; the other looks (day, night, indoors) swap over the last
0.4 s of the shot before a cut.

THE RULE TAG is a cream tag hung on the camera, top-left: a key glyph and 12 (keys on her ring), a padlock glyph and
the locks clicked tonight (0 to 10), and, on the footage, the camera's clock (12:01) in a second row. Numerals and
glyphs only.

Cues (story.json "cues"): look {id, dur}, tag {n, clock}, key {on, k, lx, lz, a0, a1, dur, hand} (Lou's key turning in
house k's lock), door<k> {a0, a1, dur}, blanket {where: arm|shoulders|none}, box, wet, sneaks, mycam.
"""
from __future__ import annotations

import math
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
TMP = Path(tempfile.mkdtemp(prefix="auntskeys-"))
BRASS = "#d8a93b"
WARM = "#ffb347"
LAND = G.LAND
W = {}
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


def lin(h):
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(v / 255) for v in hexrgb(h))


def P(hexc, rough=0.5, spec=0.35):
    return W["kit"].plastic(hexc, rough, spec=spec)


def B(parent, size, loc, mat, name="b", bevel=0.0, rot=(0, 0, 0)):
    return W["kit"].box(nm(name), size, loc, mat, parent, rot, bevel)


def E(parent, loc=(0, 0, 0), name="e", rot=(0, 0, 0)):
    return W["kit"].empty(nm(name), loc, parent, rot)


def C(parent, r, h, loc, mat, name="c", rot=(0, 0, 0), n=20, r2=None):
    return W["kit"].cyl(nm(name), r, h, loc, mat, parent, rot, n, r2)


def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


def noshadow(ob):
    try:
        ob.visible_shadow = False
    except Exception:
        pass
    for c in ob.children_recursive:
        try:
            c.visible_shadow = False
        except Exception:
            pass


# ---------------------------------------------------------------------------------------------------- numerals
def _font(size):
    from PIL import ImageFont

    for f in ("DejaVuSans-Bold.ttf", "DejaVuSansMono-Bold.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except Exception:
            continue
    return ImageFont.load_default()


def numeral_image(n, bg, fg, size=128):
    from PIL import Image, ImageDraw

    p = TMP / f"plate-{n}-{bg[1:]}.png"
    if not p.exists():
        im = Image.new("RGB", (size, size), hexrgb(bg))
        d = ImageDraw.Draw(im)
        f = _font(int(size * (0.66 if n < 10 else 0.54)))
        txt = str(n)
        bb = d.textbbox((0, 0), txt, font=f)
        d.text(((size - (bb[2] - bb[0])) / 2 - bb[0], (size - (bb[3] - bb[1])) / 2 - bb[1]), txt, fill=hexrgb(fg), font=f)
        im.save(p)
    return str(p)


def imgmat(path, rough=0.4):
    kit = W["kit"]
    key = f"img {path}"
    if key in kit.MATS:
        return kit.MATS[key]
    m = kit._new(key)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tex = nt.nodes.new("ShaderNodeTexImage")
    im = bpy.data.images.load(path, check_existing=True)
    im.colorspace_settings.name = "sRGB"
    tex.image = im
    gc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m


# ---------------------------------------------------------------------------------------------------- looks
# sun / moon / fill are 0..1 gains on their lights; the camera's key light follows the shot ("face").
LOOKS = {
    "day": dict(sky="#8fd0ff", world=0.8, sun=0.6, moon=0.0, fill=0.25, exp=-0.1, stars=0.0, win="#9fd8ff", wins=2.5),
    "dusk": dict(sky="#ffb27a", world=0.85, sun=0.7, moon=0.0, fill=0.35, exp=0.12, stars=0.0, win="#ffb88a", wins=2.5),
    "night": dict(sky="#1d3f5a", world=0.55, sun=0.0, moon=1.0, fill=0.55, exp=0.35, stars=1.0, win="#2a6a8c", wins=1.2),
    "dawn": dict(sky="#ffc9a0", world=0.9, sun=0.55, moon=0.0, fill=0.4, exp=0.1, stars=0.0, win="#ffc9a0", wins=2.5),
    "int": dict(sky="#9cb8d8", world=0.55, sun=0.0, moon=0.0, fill=0.5, exp=0.3, stars=0.0, win="#2a6a8c", wins=1.2),
}


def mixed(a, b, u):
    out = {}
    for k in a:
        if isinstance(a[k], str):
            ca, cb = lin(a[k]), lin(b[k])
            out[k] = tuple(ca[i] + (cb[i] - ca[i]) * u for i in range(3))
        else:
            out[k] = lerp(a[k], b[k], u)
    return out


def look_at(tl, t):
    cues = sorted((c for c in tl["cues"] if c["name"] == "look"), key=lambda c: c["t"])
    cur = LOOKS[cues[0]["id"]] if cues else LOOKS["night"]
    prev = cur
    for c in cues:
        if c["t"] > t:
            break
        prev, cur = cur, LOOKS[c["id"]]
        dur = c.get("dur", 0.0)
        dur = 0.0 if dur <= 0 else max(0.3, dur)      # house bar: no light change faster than 0.3 s
        if t < c["t"] + dur:
            return mixed(prev, cur, ss((t - c["t"]) / dur))
    return mixed(cur, cur, 0.0)


def sample(tl, name, t, defaults):
    cur = dict(defaults)
    for c in sorted(tl["cues"], key=lambda c: c["t"]):
        if c["name"] == name and c["t"] <= t + 1e-9:
            cur.update({k: v for k, v in c.items() if k in defaults})
    return cur


def cue_at(tl, name, t):
    out = {}
    for c in sorted(tl["cues"], key=lambda c: c["t"]):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c
    return out


# ---------------------------------------------------------------------------------------------------- the court
BRICKS = ["#e0735a", "#cf5f48", "#d96a4e", "#c9573f"]
DOORS = {1: "#1f8a8a", 2: "#6ab8f0", 3: "#ff7a5c", 4: "#3fa35a", 5: "#8a4a8a", 6: "#e8782a", 7: "#ffd86b", 8: "#c0272d",
         9: "#3a7fd0", 10: "#e8c040", 11: "#d96a8c", 12: "#2f6f55"}
IVY = {3: (-1.2, 2.2, 1.0, 3.6), 6: (1.3, 1.5, 1.0, 4.2), 9: (-1.3, 1.8, 1.0, 3.0), 11: (1.2, 1.4, 1.1, 3.8),
       2: (1.4, 1.2, 0.9, 2.6), 12: (-1.2, 1.4, 1.0, 3.2)}


def house_xf(k):
    a = math.radians(G.ang(k))
    return G.R * math.sin(a), G.R * math.cos(a), -a


def carriage_lamp(kit, H, k, lx):
    """A brass-and-black carriage lamp on a bracket beside the door, on at the same strength in every frame."""
    iron = P("#23262e", 0.5, 0.3)
    z = LAND + 2.4
    B(H, (0.06, 0.2, 0.05), (lx, -0.1, z + 0.12), iron, "lampbracket")
    B(H, (0.16, 0.16, 0.04), (lx, -0.24, z + 0.02), iron, "lampbase")
    B(H, (0.11, 0.11, 0.2), (lx, -0.24, z + 0.14), kit.emit("#ffc766", 3.0, name="carriagebulb"), "lampglass")
    for sx in (-1, 1):
        for sy in (-1, 1):
            B(H, (0.02, 0.02, 0.22), (lx + sx * 0.065, -0.24 + sy * 0.065, z + 0.14), iron, "lampcage")
    B(H, (0.2, 0.2, 0.04), (lx, -0.24, z + 0.27), iron, "lampcap")
    B(H, (0.1, 0.1, 0.07), (lx, -0.24, z + 0.32), iron, "lampcap2")
    big = k in (1, 7)
    W["lamps"].append(kit.light(f"porch{k}", "POINT", (lx, -0.5, z + 0.1), 55 if big else 22, WARM, size=0.12, parent=H,
                                shadow=big))


def geranium_pot(kit, H, lx, d):
    terr = P("#c4623a", 0.7, 0.1)
    z0 = LAND
    C(H, 0.2, 0.3, (lx, -d, z0 + 0.15), terr, "pot", n=16, r2=0.24)
    C(H, 0.255, 0.05, (lx, -d, z0 + 0.32), terr, "potrim", n=16)
    leaf = P("#3f9a4c", 0.8, 0.05)
    B(H, (0.42, 0.36, 0.2), (lx, -d, z0 + 0.45), leaf, "geraniumleaf", 0.05)
    for i in range(9):
        a = i * 2.4
        r = 0.16 * ((i % 3) + 1) / 3.0
        kit.sphere(nm("geranium"), 0.075, (lx + r * math.cos(a), -d + r * math.sin(a), z0 + 0.58 + 0.04 * (i % 3)),
                   P("#e2463b", 0.55, 0.15), H, seg=10)


def knocker(kit, H, lx, z):
    b = P(BRASS, 0.3, 0.9)
    B(H, (0.09, 0.03, 0.12), (lx, -0.13, z + 0.1), b, "knockerplate", 0.01)
    for i in range(16):
        a = 2 * math.pi * i / 16
        B(H, (0.02, 0.018, 0.02), (lx + 0.07 * math.sin(a), -0.15, z - 0.04 + 0.07 * math.cos(a)), b, "knockerring")
    B(H, (0.05, 0.03, 0.04), (lx, -0.15, z - 0.11), b, "knockerstrike")


def build_house(kit, k):
    ox, oy, rz = house_xf(k)
    H = E(None, (ox, oy, 0), f"house{k}", (0, 0, rz))
    brick = kit.texture("brick", 0.8, tint=BRICKS[k % 4])
    roof = P("#58485a", 0.7, 0.1)
    white = P("#f6f1e6", 0.5)
    brass = P(BRASS, 0.3, 0.9)
    zt = LAND + 2.1       # the door's top
    if k == G.LOU:
        # the body in pieces round a real doorway, with a warm hall behind the door
        B(H, (1.25, 4.2, 6.2), (-1.225, 2.1, 3.1), brick, "body")
        B(H, (1.25, 4.2, 6.2), (1.225, 2.1, 3.1), brick, "body")
        B(H, (1.2, 4.2, 6.2 - zt - 0.12), (0, 2.1, (zt + 0.12 + 6.2) / 2), brick, "lintelbrick")
        B(H, (1.2, 2.2, LAND), (0, 1.1, LAND / 2), P("#d9c9a6", 0.8), "hallfloor")
        B(H, (1.2, 0.2, 2.3), (0, 2.3, LAND + 1.15), P("#f3e3c8", 0.9, 0.05), "hallback")
        for sx in (-1, 1):
            B(H, (0.03, 2.1, 2.2), (sx * 0.585, 1.1, LAND + 1.1), P("#f3e3c8", 0.9, 0.05), "hallwall")
        B(H, (0.5, 2.0, 0.02), (0, 1.1, LAND + 0.011), P("#a8e6c8", 0.9, 0.05), "hallrunner")
        W["hall_light"] = kit.light("halllight", "POINT", (0, 1.0, LAND + 2.0), 22, "#ffc680", size=0.3, parent=H, shadow=False)
        # jambs and a lintel round the door
        for sx in (-1, 1):
            B(H, (0.1, 0.14, 2.2), (sx * 0.55, -0.02, LAND + 1.1), white, "jamb")
        B(H, (1.2, 0.14, 0.12), (0, -0.02, zt + 0.06), white, "doorlintel")
    else:
        B(H, (3.7, 4.2, 6.2), (0, 2.1, 3.1), brick, "body")
        B(H, (1.2, 0.07, 2.28), (0, -0.035, LAND + 1.14), white, "frame")
    B(H, (4.0, 4.6, 0.3), (0, 2.2, 6.35), roof, "roof")
    B(H, (0.5, 0.5, 1.0), (1.1, 3.0, 7.0), brick, "chimney")
    B(H, (3.9, 0.3, 0.12), (0, -0.15, 0.06), P("#bdb5a6", 0.8), "plinth")
    # the porch: a landing and two steps
    stone = P("#cfc7b8", 0.85, 0.05)
    B(H, (1.9, 0.9, LAND), (0, -0.45, LAND / 2), stone, "landing")
    B(H, (1.9, 0.4, 0.30), (0, -1.1, 0.15), P("#c3bbab", 0.85, 0.05), "step")
    B(H, (1.9, 0.4, 0.15), (0, -1.5, 0.075), P("#b9b1a1", 0.85, 0.05), "step")
    # the door, hinged on its left edge
    Hg = E(H, (-0.5, 0, LAND), f"hinge{k}")
    W["hinges"][k] = Hg
    B(Hg, (1.0, 0.09, 2.1), (0.5, -0.075, 1.05), P(DOORS[k], 0.4, 0.3), "door")
    for dx in (-0.22, 0.22):
        B(Hg, (0.36, 0.015, 0.8), (0.5 + dx, -0.125, 1.45), P(DOORS[k], 0.4, 0.3), "doorpanel", 0.01)
        B(Hg, (0.36, 0.015, 0.8), (0.5 + dx, -0.125, 0.5), P(DOORS[k], 0.4, 0.3), "doorpanel", 0.01)
    if k == G.LOU:
        B(Hg, (0.05, 0.07, 0.24), (0.88, -0.15, 1.0), brass, "latch")
        B(Hg, (0.16, 0.05, 0.035), (0.88, -0.19, 1.07), brass, "lever")
        knocker(kit, Hg, 0.3, 1.6 + 0.0)      # on the door (hinge-local x)
    else:
        B(Hg, (0.10, 0.02, 0.22), (0.88, -0.13, 0.78), brass, "lockplate")
        B(Hg, (0.018, 0.012, 0.05), (0.88, -0.145, 0.78), P("#15131a", 0.9), "keyhole")
        kit.sphere(nm("knob"), 0.05, (0.88, -0.17, 0.96), brass, Hg, seg=12)
        C(Hg, 0.075, 0.022, (0.88, -0.14, 1.3), brass, "dbplate", rot=(math.pi / 2, 0, 0), n=18)
        B(Hg, (0.016, 0.012, 0.05), (0.88, -0.155, 1.3), P("#15131a", 0.9), "dbhole")
        if k != G.ME:
            knocker(kit, Hg, 0.3, 1.6)
        if k == G.HADDAD:    # her new shiny lock, twice changed
            chrome = P("#f4f6f8", 0.12, 0.95)
            lx_, lz_ = 0.6, 1.5
            B(Hg, (0.24, 0.05, 0.5), (lx_, -0.16, lz_), chrome, "newlockplate", 0.012)
            C(Hg, 0.09, 0.06, (lx_, -0.21, lz_ + 0.1), chrome, "newlockcyl", rot=(math.pi / 2, 0, 0), n=18)
            B(Hg, (0.025, 0.012, 0.08), (lx_, -0.245, lz_ + 0.1), P("#15131a", 0.9), "newlockhole")
            B(Hg, (0.16, 0.06, 0.2), (lx_, -0.21, lz_ - 0.14), P("#ffe27a", 0.15, 1.0), "newlockbolt", 0.01)
        if k == G.ME:
            B(Hg, (0.3, 0.015, 0.1), (0.5, -0.125, 1.75), P("#c28a1c", 0.4, 0.3), "mydoorstripe")
    # the numeral plate above the door, 2 cm proud of the wall
    kit.plane(nm("plate"), (0.36, 0.24), (0, -0.02, zt + 0.45), imgmat(numeral_image(k, BRASS, "#3a2a14"), 0.4), H,
              rot=(math.pi / 2, 0, 0))
    B(H, (0.42, 0.03, 0.30), (0, -0.005, zt + 0.45), P("#8a6a1e", 0.4, 0.5), "plateback")
    if k == G.LOU:     # two amber strokes scratched under the numeral (the court's lore tally)
        for sx in (-1, 1):
            B(H, (0.025, 0.02, 0.1), (sx * 0.06, -0.04, zt + 0.21), P("#ffb347", 0.4, 0.4), "tally")
    # windows
    for (wx, wz, ww, wh) in ((-0.95, LAND + 3.9, 0.8, 1.0), (0.95, LAND + 3.9, 0.8, 1.0), (-1.3, 1.9, 0.55, 0.8),
                             (1.3, 1.9, 0.55, 0.8)):
        B(H, (ww + 0.14, 0.06, wh + 0.14), (wx, -0.03, wz), white, "wframe")
        B(H, (ww, 0.05, wh), (wx, -0.06, wz), P("#bfe3f5", 0.1, 0.8) if wz > 3 else P("#ffd9a0", 0.3, 0.3), "pane")
        B(H, (0.04, 0.07, wh), (wx, -0.075, wz), white, "mullion")
        B(H, (ww, 0.07, 0.04), (wx, -0.075, wz), white, "transom")
    carriage_lamp(kit, H, k, 1.0)
    if k in IVY:
        x0, w, z0, z1 = IVY[k]
        gcol = ["#4fae5a", "#3f9a4c", "#5cbf62"]
        for i in range(14):
            sx = x0 + 0.38 * ((i * 7) % 5) * (0.9 if x0 < 0 else -0.9) * 0.6
            B(H, (0.45, 0.07, 0.42), (sx, -0.05 - 0.02 * (i % 3), z0 + (z1 - z0) * ((i * 3) % 7) / 7.0), P(gcol[i % 3], 0.8),
              "ivy")
    if k == G.LOU:
        geranium_pot(kit, H, -0.72, 0.42)
        # the striped doormat, 1.2 cm proud of the landing
        for i in range(8):
            B(H, (0.11, 0.55, 0.024), (-0.385 + i * 0.11, -0.55, LAND + 0.012), P("#e8604a" if i % 2 else "#f6ead0", 0.9, 0.05),
              "stripedmat")
        # a shopfront: the key shop's window board with hanging keys, left of the door on the ground floor
    if k == G.ME:
        B(H, (0.95, 0.6, 0.024), (0, -0.55, LAND + 0.012), P("#2fb5a8", 0.9, 0.05), "mat")
    return H


def build_court(kit):
    lawn = kit.texture("grass", 0.6, tint="#7ed25a")
    B(None, (500, 500, 0.4), (0, 0, -0.25), lawn, "lawn")
    C(None, 14.2, 0.12, (0, 0, -0.03), kit.texture("concrete", 0.5, tint="#d6c6b0"), "courtfloor", n=48)
    C(None, 6.6, 0.125, (0, 0, -0.025), P("#cdbb9c", 0.8, 0.05), "courtring", n=48)
    W["lamps"], W["hinges"] = [], {}
    for k in range(1, 13):
        build_house(kit, k)
    # the fountain: a stone basin, a plain column and bowl, a steady stream
    stone, stone2 = P("#d8d2c4", 0.75, 0.1), P("#bdb6a6", 0.75, 0.1)
    C(None, 2.4, 0.62, (0, 0, 0.31), stone, "fountain.basin", n=40)
    C(None, 2.55, 0.12, (0, 0, 0.62), stone2, "fountain.rim", n=40)
    C(None, 2.2, 0.04, (0, 0, 0.62), P("#4fb8c8", 0.1, 0.9), "fountain.water", n=40)
    C(None, 0.32, 1.5, (0, 0, 1.2), stone, "fountain.column", n=20)
    C(None, 0.5, 0.28, (0, 0, 1.95), stone2, "fountain.bowl", n=28, r2=1.0)
    kit.sphere("fountain.ball", 0.28, (0, 0, 2.28), stone, None, seg=16)
    C(None, 0.04, 0.5, (0, 0, 2.5), P("#bfeaf4", 0.1, 0.6), "fountain.spout", n=10)
    wood = P("#7a5230", 0.6)
    for sx in (-1, 1):
        B(None, (0.5, 1.9, 0.08), (sx * 3.7, 0, 0.5), wood, "bench")
        B(None, (0.5, 0.1, 0.5), (sx * 3.7, 0.8, 0.25), stone2, "benchleg")
        B(None, (0.5, 0.1, 0.5), (sx * 3.7, -0.8, 0.25), stone2, "benchleg")
    for i, (x, y, h) in enumerate(((-20, -20, 6.5), (15, -13, 7.0), (-20, 4, 7.5), (21, 6, 7.0), (0, 24, 8.0), (-9, -26, 7.0),
                                    (10, -28, 7.5))):
        try:
            kit.prop("commontree_1" if i % 2 == 0 else "birchtree_1", (x, y, 0), rot=37 * i, height=h, tint="#8fd860")
        except Exception:
            pass
    for (x, y) in ((-8.2, 7.0), (8.6, 4.4), (-12.5, -1.0), (12.8, -2.0)):
        try:
            kit.prop("bush_1", (x, y, 0), rot=x * 9, height=1.1, tint="#58c24a")
        except Exception:
            pass
    # stars: small emissive blocks high over the court, one shared material (strength set by the look)
    stm = kit.emit("#fff6d8", 6.0, name="starmat")
    W["stars"] = stm
    W["starroot"] = E(None, (0, 0, 0), "starroot")
    for i in range(130):
        a = (i * 137.5) % 360 * D2R
        el = 18 + (i * 53) % 62
        r = 90.0
        x, y, z = r * math.cos(el * D2R) * math.sin(a), r * math.cos(el * D2R) * math.cos(a), r * math.sin(el * D2R)
        s = 0.5 + 0.35 * (i % 3)
        b = B(W["starroot"], (s, s, s), (x, y, z), stm, "star")
        noshadow(b)


# ---------------------------------------------------------------------------------------------------- the key and the ring
def build_key(kit):
    """The key in a lock: origin at the keyhole, the key sticking out toward -y (the court), a yellow cuff and a hand
    coming in from +x. keyg turns about y."""
    brass = P(BRASS, 0.28, 0.9)
    root = E(None, (0, 0, -20), "keyroot")
    keyg = E(root, (0, 0, 0), "keyg")
    B(keyg, (0.010, 0.07, 0.016), (0, -0.03, 0.0), brass, "blade", 0.002)
    B(keyg, (0.010, 0.014, 0.010), (0, -0.015, -0.012), brass, "tooth", 0.002)
    B(keyg, (0.010, 0.012, 0.007), (0, -0.04, -0.011), brass, "tooth", 0.002)
    by = -0.075
    B(keyg, (0.056, 0.012, 0.009), (0, by, 0.019), brass, "bowt", 0.003)
    B(keyg, (0.056, 0.012, 0.009), (0, by, -0.019), brass, "bowb", 0.003)
    for sx in (-1, 1):
        B(keyg, (0.009, 0.012, 0.047), (sx * 0.0235, by, 0.0), brass, "bows", 0.003)
    mus = P("#ffd23f", 0.5, 0.2)
    B(root, (0.46, 0.15, 0.15), (0.35, by - 0.015, 0.07), mus, "keysleeve", 0.02)
    B(root, (0.045, 0.125, 0.125), (0.105, by - 0.015, 0.07), P("#4a9a5a", 0.8), "keycuff", 0.01)
    B(root, (0.07, 0.09, 0.075), (0.055, by - 0.012, 0.045), P("#f1c9a0", 0.5), "keyhand", 0.015)
    W["key"] = (root, keyg)


def build_waist_ring(kit, lou):
    """The key ring on a belt clip at Lou's waist: twelve brass keys with plain brass tags (key 7's tag is butter yellow,
    key 12 is the new shiny one). Dimensions in metres under an empty scaled to the torso's units."""
    h = float(W["story"]["cast"]["lou"].get("height", 1.0))
    unit = 0.34 * h
    root = E(lou, (0.82, -0.6, 0.02), "waistring")
    root.scale = (1 / unit, 1 / unit, 1 / unit)
    sw = E(root, (0, 0, 0), "ringswing")
    old = P("#b88a2a", 0.45, 0.8)
    new = P("#ffe27a", 0.12, 1.0)
    dark = P("#6a4e14", 0.4, 0.8)
    B(sw, (0.05, 0.025, 0.07), (0, 0, 0.0), dark, "beltclip", 0.006)
    rc, rr = (0.0, -0.01, -0.075), 0.055
    for i in range(20):
        a = 2 * math.pi * i / 20
        B(sw, (0.02, 0.012, 0.012), (rc[0] + rr * math.sin(a), rc[1], rc[2] + rr * math.cos(a)), dark, "ringseg", 0.002,
          rot=(0, a + math.pi / 2, 0))
    for i in range(12):
        th = math.radians(-64 + i * (128 / 11))
        ax, az = rc[0] + rr * math.sin(th), rc[2] - rr * math.cos(th)
        ln = 0.088 + 0.008 * (i % 3) + (0.02 if i == 11 else 0.0)
        mat = new if i == 11 else old
        ang = th * 0.55
        yy = rc[1] - 0.012 - 0.006 * (i % 4)
        cx, cz = ax + math.sin(ang) * ln / 2, az - math.cos(ang) * ln / 2
        B(sw, (0.009, 0.007, ln), (cx, yy, cz), mat, "ringkey", 0.0015, rot=(0, -ang, 0))
        ex, ez = ax + math.sin(ang) * ln, az - math.cos(ang) * ln
        B(sw, (0.02, 0.007, 0.008), (ex - math.cos(ang) * 0.011, yy, ez - math.sin(ang) * 0.011), mat, "ringtooth", 0.0015)
        tx, tz = ax + math.sin(ang) * 0.012, az - math.cos(ang) * 0.012
        tagm = P("#ffd86b", 0.35, 0.3) if i == 6 else (mat if i == 11 else old)
        C(sw, 0.019, 0.006, (tx, yy - 0.008, tz), tagm, "ringtag", rot=(math.pi / 2, 0, 0), n=16)
    W["ring"] = sw


# ---------------------------------------------------------------------------------------------------- the rooms
def lamp(kit, x, y, z, name, energy=60, col="#ffc680", shade="#ffdc9c", wall=None):
    """A shaded table or wall lamp and its light, steady."""
    C(None, 0.17, 0.26, (x, y, z), kit.emit(shade, 3.0, name="shade"), "lampshade", n=16, r2=0.11)
    C(None, 0.025, 0.2, (x, y, z - 0.2), P("#5a3a22", 0.5), "lampstem", n=8)
    C(None, 0.1, 0.03, (x, y, z - 0.31), P("#5a3a22", 0.5), "lampfoot", n=12)
    W["rlights"].append(kit.light(name, "POINT", (x, y, z + 0.1), energy, col, size=0.3, shadow=False))


def build_room(kit):
    rx, ry = G.ROOM
    W["rlights"] = []
    floor = kit.texture("wood", 0.7, tint="#f1d8b0")
    B(None, (16.4, 14.4, 0.1), (rx, ry, -0.05), floor, "rfloor")
    B(None, (16.6, 14.6, 0.2), (rx, ry, 3.3), P("#fbf0dc", 0.9, 0.05), "rceiling")
    t = 0.2
    cream = "#f6e6c4"
    # north wall: shop (teal) and kitchen (cream); south: my room (sky) and the old room (buttery); east: hall (mint)
    B(None, (8.0, t, 3.2), (rx - 4, G.WALL_N + t / 2, 1.6), P("#3f8f94", 0.85, 0.05), "wall.shop")
    B(None, (8.0, t, 3.2), (rx + 4, G.WALL_N + t / 2, 1.6), P("#f8e8c8", 0.85, 0.05), "wall.kitchen")
    B(None, (8.0, t, 3.2), (rx - 4, G.WALL_S - t / 2, 1.6), P("#a9cce8", 0.85, 0.05), "wall.mine")
    B(None, (8.0, t, 3.2), (rx + 4, G.WALL_S - t / 2, 1.6), P("#f6dc8a", 0.85, 0.05), "wall.old")
    B(None, (t, 12.4, 3.2), (G.WALL_E + t / 2, ry, 1.6), P("#cdebd8", 0.85, 0.05), "wall.hall")
    B(None, (t, 12.4, 3.2), (rx - 8 - t / 2, ry, 1.6), P("#f1dcc0", 0.85, 0.05), "wall.west")
    base = P("#ffffff", 0.5)
    for sx in (-1, 1):
        B(None, (7.9, 0.06, 0.14), (rx + sx * 4, G.WALL_N - 0.03, 0.07), base, "skirt")
        B(None, (7.9, 0.06, 0.14), (rx + sx * 4, G.WALL_S + 0.03, 0.07), base, "skirt")
    brass = P(BRASS, 0.3, 0.9)
    # ------------------------------------------------------------------ the shop corner (the key-cutting bench)
    sx0, sy0 = G.STAGE["shop"]
    B(None, (3.6, 0.05, 1.7), (sx0, sy0 - 0.03, 1.55), P("#8a6a44", 0.6), "pegboard")
    for r in range(3):
        for c in range(8):
            x, z = sx0 - 1.4 + 0.4 * c, 0.95 + 0.42 * r + 0.06 * (c % 2)
            B(None, (0.02, 0.012, 0.22), (x, sy0 - 0.09, z), brass, "blankkey")
            B(None, (0.075, 0.012, 0.075), (x, sy0 - 0.09, z + 0.15), brass, "blankbow")
    B(None, (2.8, 0.75, 1.0), (sx0, sy0 - 2.1, 0.5), P("#7a5230", 0.6), "counter")
    B(None, (3.0, 0.85, 0.07), (sx0, sy0 - 2.1, 1.035), P("#a97b4a", 0.55), "countertop")
    B(None, (0.55, 0.4, 0.34), (sx0 + 0.9, sy0 - 2.1, 1.24), P("#8a8d96", 0.35, 0.7), "keymachine")
    C(None, 0.12, 0.05, (sx0 + 0.9, sy0 - 2.28, 1.3), P("#d9dce2", 0.2, 0.9), "keywheel", rot=(math.pi / 2, 0, 0), n=18)
    lamp(kit, sx0 - 1.0, sy0 - 2.05, 1.35, "shoplamp", 70)
    # ------------------------------------------------------------------ the kitchen corner
    kx0, ky0 = G.STAGE["kitchen"]
    tab = P("#c98f55", 0.55, 0.15)
    C(None, 0.7, 0.05, (kx0, ky0 - 2.3, 0.77), tab, "kitchentable", n=32)
    C(None, 0.07, 0.75, (kx0, ky0 - 2.3, 0.38), P("#8a5a32", 0.6), "tableleg", n=10)
    C(None, 0.3, 0.04, (kx0, ky0 - 2.3, 0.02), P("#8a5a32", 0.6), "tablefoot", n=16)
    C(None, 2.0, 0.012, (kx0, ky0 - 2.3, 0.008), P("#f4e2c0", 0.9, 0.05), "kitchenrug", n=40)
    cloth = P("#f2d8d0", 0.8, 0.05)
    lad = P("#c8ced8", 0.25, 0.9)
    B(None, (0.5, 0.03, 0.025), (kx0 + 0.15, ky0 - 2.62, 0.838), lad, "ladlehandle", 0.008)
    C(None, 0.07, 0.04, (kx0 + 0.43, ky0 - 2.62, 0.845), lad, "ladlebowl", n=16)
    C(None, 0.72, 0.012, (kx0, ky0 - 2.3, 0.802), cloth, "tablecloth", n=32)
    for sx in (-1, 1):
        px = kx0 + sx * 0.42
        C(None, 0.17, 0.02, (px, ky0 - 2.3, 0.82), P("#fbfbf6", 0.35, 0.5), "plate", n=20)
        C(None, 0.09, 0.05, (px, ky0 - 2.3, 0.855), P("#e8604a", 0.4, 0.4), "bowl", n=16, r2=0.12)
        # a chair behind each place, backs outward
        cx = kx0 + sx * 1.0
        B(None, (0.45, 0.45, 0.06), (cx, ky0 - 2.3, 0.45), P("#e0aa62", 0.6), "chairseat", 0.01)
        B(None, (0.06, 0.45, 0.5), (cx + sx * 0.2, ky0 - 2.3, 0.75), P("#e0aa62", 0.6), "chairback", 0.01)
        for lx_ in (-1, 1):
            for ly_ in (-1, 1):
                B(None, (0.05, 0.05, 0.42), (cx + lx_ * 0.19, ky0 - 2.3 + ly_ * 0.19, 0.21), P("#c08a48", 0.6), "chairleg")
    B(None, (1.0, 0.7, 0.9), (kx0 + 2.5, ky0 - 0.45, 0.45), P("#e8e4dc", 0.4, 0.3), "stove", 0.02)
    B(None, (0.8, 0.55, 0.04), (kx0 + 2.5, ky0 - 0.45, 0.92), P("#2a2a30", 0.4, 0.5), "stovetop")
    C(None, 0.26, 0.32, (kx0 + 2.5, ky0 - 0.45, 1.1), P("#b8c0cc", 0.25, 0.9), "soup.pot", n=24)
    C(None, 0.27, 0.03, (kx0 + 2.5, ky0 - 0.45, 1.27), P("#9aa3b0", 0.25, 0.9), "soup.lid", n=24)
    C(None, 0.03, 0.04, (kx0 + 2.5, ky0 - 0.45, 1.31), P("#2a2a30", 0.4), "soup.knob", n=8)
    B(None, (0.5, 0.5, 0.9), (kx0 - 2.6, ky0 - 0.35, 0.45), P("#a9754a", 0.6), "kitchencab")
    B(None, (0.55, 0.55, 0.05), (kx0 - 2.6, ky0 - 0.35, 0.92), P("#e8dcc8", 0.5), "kitchencabtop")
    lamp(kit, kx0 - 2.6, ky0 - 0.4, 1.27, "kitchenlamp", 70)
    # ------------------------------------------------------------------ my room (number seven, upstairs)
    mx0, my0 = G.STAGE["mine"]
    wx = mx0 - 1.5
    B(None, (1.6, 0.14, 1.6), (wx, my0 + 0.06, 1.7), P("#ffffff", 0.5), "windowframe")
    glass = kit.emit("#2a6a8c", 1.2, name="windowglass")
    W["winglass"] = glass
    B(None, (1.35, 0.04, 1.35), (wx, my0 + 0.0, 1.7), glass, "windowglass")
    B(None, (0.05, 0.16, 1.35), (wx, my0 + 0.09, 1.7), P("#ffffff", 0.5), "windowmullion")
    B(None, (1.35, 0.16, 0.05), (wx, my0 + 0.09, 1.7), P("#ffffff", 0.5), "windowtransom")
    B(None, (1.9, 0.38, 0.07), (wx, my0 + 0.3, 0.98), P("#ffffff", 0.5), "windowsill")
    cam = E(None, (wx, my0 + 0.3, 1.06), "mycam")
    W["mycam"] = cam
    B(cam, (0.18, 0.1, 0.12), (0, 0, 0.06), P("#f4f6f8", 0.3, 0.6), "camerabody", 0.012)
    C(cam, 0.035, 0.05, (0, 0.07, 0.06), P("#15131a", 0.2, 0.5), "cameralens", rot=(math.pi / 2, 0, 0), n=14)
    B(cam, (0.05, 0.05, 0.05), (0, -0.01, 0.0), P("#8a8d96", 0.4), "camerafoot")
    # a curtain pair
    for sx in (-1, 1):
        B(None, (0.4, 0.1, 1.9), (wx + sx * 1.05, my0 + 0.16, 1.55), P("#f2c14e", 0.9, 0.05), "curtain", 0.04)
    # the bed, a nightstand and a lamp
    bx = mx0 + 1.5
    B(None, (1.1, 2.0, 0.28), (bx, my0 + 1.2, 0.3), P("#8a5a32", 0.6), "bedframe")
    B(None, (1.0, 1.9, 0.2), (bx, my0 + 1.2, 0.54), P("#f4f0e8", 0.8, 0.05), "mattress", 0.04)
    B(None, (1.04, 1.2, 0.12), (bx, my0 + 0.85, 0.66), P("#7fa8d8", 0.85, 0.05), "bedblanket", 0.04)
    B(None, (0.8, 0.4, 0.14), (bx, my0 + 0.34, 0.69), P("#ffffff", 0.8, 0.05), "pillow", 0.05)
    B(None, (1.1, 0.1, 0.9), (bx, my0 + 0.12, 0.7), P("#8a5a32", 0.6), "headboard")
    B(None, (0.5, 0.5, 0.55), (bx + 1.05, my0 + 0.35, 0.28), P("#a9754a", 0.6), "nightstand")
    lamp(kit, bx + 1.05, my0 + 0.35, 0.92, "myroomlamp", 45)
    # the front door (inside): a butter door with a brass thumb-turn bolt and a knob
    dx = mx0 + 3.4
    g = E(None, (dx, my0, 0), "mydoorin")
    W["mydoor"] = g
    B(g, (1.2, 0.07, 2.25), (0, 0.04, 1.13), P("#f6f1e6", 0.5), "indoorframe")
    B(g, (1.0, 0.08, 2.1), (0, 0.10, 1.05), P("#ffd86b", 0.4, 0.3), "indoor")
    C(g, 0.06, 0.03, (0.3, 0.16, 1.15), brass, "tbase", rot=(math.pi / 2, 0, 0), n=18)
    th = E(g, (0.3, 0.18, 1.15), "thumb")
    W["thumb"] = th
    B(th, (0.22, 0.04, 0.06), (0, 0, 0), brass, "tbar", 0.015)
    kit.sphere(nm("indoorknob"), 0.05, (0.3, 0.16, 0.96), brass, g, seg=12)
    # wet marks and leaves on the floor, shown on the mornings (cue wet)
    wet = E(None, (0, 0, 0), "wetmarks")
    W["wetmarks"] = wet
    for i, (gx, gy) in enumerate(((-0.4, 0.2), (0.15, -0.1), (0.5, 0.35), (-0.15, 0.7))):
        C(wet, 0.2 - 0.025 * i, 0.006, (mx0 + gx, my0 + 3.3 + gy + 0.0, 0.012), P("#6f7f90", 0.1, 0.9), "wetspot", n=16)
        B(wet, (0.08, 0.2, 0.012), (mx0 + gx + 0.2, my0 + 3.3 + gy - 0.15, 0.016), P("#4fae5a", 0.8), "grassblade",
          rot=(0, 0, 0.5 * i))
    # a pair of white sneakers by the door (cue sneaks)
    sn = E(None, (0, 0, 0), "sneakerpair")
    W["sneaks"] = sn
    for sx in (-1, 1):
        B(sn, (0.1, 0.27, 0.09), (dx - 0.55 + sx * 0.08, my0 + 0.55, 0.05), P("#f6f6f6", 0.5, 0.3), "sneaker", 0.025)
        B(sn, (0.105, 0.28, 0.025), (dx - 0.55 + sx * 0.08, my0 + 0.55, 0.0125), P("#d9d9d9", 0.7), "sneakersole")
    # ------------------------------------------------------------------ the old room (a made bed, a lamp on low)
    ox0, oy0 = G.STAGE["old"]
    obx = ox0 + 1.0
    B(None, (1.1, 2.0, 0.28), (obx, oy0 + 1.2, 0.3), P("#8a5a32", 0.6), "oldbedframe")
    B(None, (1.0, 1.9, 0.2), (obx, oy0 + 1.2, 0.54), P("#f4f0e8", 0.8, 0.05), "oldmattress", 0.04)
    B(None, (1.06, 1.7, 0.12), (obx, oy0 + 1.1, 0.67), P("#e8a0a8", 0.85, 0.05), "oldquilt", 0.04)
    B(None, (0.8, 0.4, 0.14), (obx, oy0 + 0.34, 0.69), P("#ffffff", 0.8, 0.05), "oldpillow", 0.05)
    B(None, (1.1, 0.1, 0.9), (obx, oy0 + 0.12, 0.7), P("#8a5a32", 0.6), "oldheadboard")
    B(None, (0.5, 0.5, 0.55), (obx - 1.0, oy0 + 0.35, 0.28), P("#a9754a", 0.6), "oldnightstand")
    lamp(kit, obx - 1.0, oy0 + 0.35, 0.92, "oldroomlamp", 38, shade="#ffc27a")
    B(None, (1.3, 0.12, 2.25), (ox0 - 1.5, oy0 + 0.07, 1.13), P("#f6f1e6", 0.5), "olddoorframe")
    B(None, (1.0, 0.1, 2.1), (ox0 - 1.5, oy0 + 0.12, 1.05), P("#c9873a", 0.5), "olddoor")
    B(None, (1.0, 0.6, 0.02), (ox0 - 0.2, oy0 + 1.6, 0.011), P("#f2c14e", 0.9, 0.05), "oldrug")
    # ------------------------------------------------------------------ the hall (the stair, a mint runner, coat hooks)
    hx, hy = G.STAGE["hall"]
    steps = 8
    for i in range(steps):
        B(None, (1.3, 0.4, 0.22 * (i + 1)), (hx - 0.65, hy - 2.5 + 0.4 * i + 0.2, 0.11 * (i + 1)),
          P("#b98a5a" if i % 2 else "#a97a4a", 0.6), "stair")
    B(None, (0.06, 3.4, 0.08), (hx - 1.3, hy - 1.2, 1.15), P("#7a5230", 0.6), "stairrail", rot=(0, -0.45, 0))
    B(None, (0.9, 8.4, 0.024), (hx - 2.2, hy, 0.012), P("#a8e6c8", 0.9, 0.05), "hallrunner")
    B(None, (0.06, 1.6, 0.12), (hx - 0.03, hy + 3.4, 1.7), P("#7a5230", 0.6), "coathook")
    for i, c in enumerate(("#c0504a", "#4a6a9a", "#d9a441")):
        B(None, (0.14, 0.5, 0.95), (hx - 0.12, hy + 2.9 + 0.5 * i, 1.2), P(c, 0.9, 0.05), "coat", 0.04)
    lamp(kit, hx - 0.5, hy - 3.2, 1.9, "halllamp", 70)
    W["room_ok"] = True


def build_window(kit):
    """Mr. Ames's window and armchair: a brick front with an opening, a lit room behind (seen from outside, y < 0)."""
    wx, wy = G.WIN
    brick = kit.texture("brick", 0.8, tint="#cf5f48")
    white = P("#f6f1e6", 0.5)
    B(None, (7.0, 0.3, 0.9), (wx, wy - 0.15, 0.45), brick, "ameswall_low")
    B(None, (7.0, 0.3, 0.9), (wx, wy - 0.15, 2.75), brick, "ameswall_top")
    for sx in (-1, 1):
        B(None, (2.8, 0.3, 1.4), (wx + sx * 2.1, wy - 0.15, 1.6), brick, "ameswall_side")
    B(None, (1.6, 0.2, 0.07), (wx, wy - 0.25, 0.93), white, "amessill")
    for pz in (0.93, 2.27):
        B(None, (1.5, 0.12, 0.1), (wx, wy - 0.08, pz), white, "ameswindowframe")
    for sx in (-1, 1):
        B(None, (0.1, 0.12, 1.4), (wx + sx * 0.7, wy - 0.08, 1.6), white, "ameswindowframe")
    # the coral front door beside the window (outside face)
    B(None, (1.0, 0.09, 2.1), (wx - 2.4, wy - 0.345, 1.05), P(DOORS[3], 0.4, 0.3), "amesdoor")
    B(None, (0.10, 0.02, 0.22), (wx - 2.1, wy - 0.4, 0.78), P(BRASS, 0.3, 0.9), "ameslock")
    # the room
    floor = P("#c9a06a", 0.7, 0.1)
    B(None, (7.0, 4.0, 0.1), (wx, wy + 2.0, -0.05), floor, "amesfloor")
    B(None, (7.0, 0.2, 3.2), (wx, wy + 4.0, 1.6), P("#f3dcc0", 0.85, 0.05), "amesback")
    for sx in (-1, 1):
        B(None, (0.2, 4.0, 3.2), (wx + sx * 3.5, wy + 2.0, 1.6), P("#f3dcc0", 0.85, 0.05), "amesside")
    B(None, (7.2, 4.4, 0.2), (wx, wy + 2.0, 3.3), P("#fbf0dc", 0.9, 0.05), "amesceiling")
    # the inner face of his door (brown) in the left of the back wall
    B(None, (1.0, 0.08, 2.1), (wx - 1.9, wy + 3.86, 1.05), P("#8a5a32", 0.5), "amesindoor")
    B(None, (1.2, 0.07, 2.25), (wx - 1.9, wy + 3.88, 1.13), white, "amesindoorframe")
    # the armchair, facing the back (his door) with his back... he sits in profile-free: turned to the window
    ch = E(None, (wx + 0.1, wy + 1.3, 0), "armchair")
    W["armchair"] = ch
    f = P("#c48a3a", 0.8, 0.1)
    B(ch, (1.0, 0.95, 0.4), (0, 0, 0.3), f, "armchair.seat", 0.05)
    B(ch, (0.94, 0.9, 0.12), (0, 0, 0.06), f, "armchair.base", 0.02)
    B(ch, (1.0, 0.22, 1.1), (0, 0.45, 0.85), f, "armchair.back", 0.05, rot=(-0.12, 0, 0))
    for sx in (-1, 1):
        B(ch, (0.2, 0.95, 0.65), (sx * 0.6, 0, 0.5), f, "armchair.arm", 0.05)
    lamp(kit, wx + 2.2, wy + 1.2, 1.35, "ameslamp", 60)
    B(None, (0.5, 0.5, 0.9), (wx + 2.2, wy + 1.2, 0.45), P("#a9754a", 0.6), "amesstand")
    B(None, (0.9, 0.5, 0.04), (wx - 1.9, wy + 3.55, 0.02), P("#a8e6c8", 0.9, 0.05), "amesmat")


# ---------------------------------------------------------------------------------------------------- the rule tag
DIGIT_SEGS = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd", 6: "afgedc", 7: "abc", 8: "abcdefg",
              9: "abcdfg"}


def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    edge = kit.emit("#2b2118", 0.6, "tagedge")
    plate = kit.emit("#f2e6c8", 0.85, "tagplate")
    ink = kit.emit("#2b2118", 0.6, "tagink")
    gold = kit.emit("#c9902a", 0.9, "taggold")

    def b(name, size, loc, mat, parent=None):
        ob = kit.box(name, size, loc, mat, parent or root)
        noshadow(ob)
        return ob

    b("tag.edge", (1.62, 0.86, 0.006), (0, 0, 0), edge)
    b("tag.plate", (1.56, 0.8, 0.006), (0, 0, 0.007), plate)
    z = 0.016
    # the key glyph: a ring bow, a shaft and two teeth
    bow = kit.cyl("tag.bow", 0.105, 0.006, (-0.6, 0.0, z), gold, root, n=18)
    noshadow(bow)
    hole = kit.cyl("tag.bowhole", 0.04, 0.006, (-0.6, 0.0, z + 0.002), plate, root, n=14)
    noshadow(hole)
    b("tag.shaft", (0.34, 0.07, 0.006), (-0.41, 0.0, z), gold)
    b("tag.tooth1", (0.06, 0.12, 0.006), (-0.34, -0.08, z), gold)
    b("tag.tooth2", (0.06, 0.09, 0.006), (-0.44, -0.065, z), gold)
    # the padlock glyph
    b("tag.lockbody", (0.24, 0.2, 0.006), (0.26, -0.07, z), ink)
    b("tag.shackleL", (0.04, 0.17, 0.006), (0.18, 0.1, z), ink)
    b("tag.shackleR", (0.04, 0.17, 0.006), (0.34, 0.1, z), ink)
    b("tag.shackleT", (0.2, 0.04, 0.006), (0.26, 0.175, z), ink)
    b("tag.lockhole", (0.04, 0.07, 0.006), (0.26, -0.07, z + 0.002), plate)
    W["digits"] = {}

    def digit_set(label, cx, cy, dw=0.15, dh=0.48, t=0.055):
        pos = {"a": (0, dh / 2 - t / 2, dw, t), "g": (0, 0, dw, t), "d": (0, -dh / 2 + t / 2, dw, t),
               "f": (-dw / 2 + t / 2, dh / 4, t, dh / 2), "b": (dw / 2 - t / 2, dh / 4, t, dh / 2),
               "e": (-dw / 2 + t / 2, -dh / 4, t, dh / 2), "c": (dw / 2 - t / 2, -dh / 4, t, dh / 2)}
        d = {}
        for k, (px, py, sw, sh) in pos.items():
            d[k] = b(f"tag.{label}{k}", (sw, sh, 0.006), (cx + px, cy + py, z), ink)
        return d

    W["digits"]["keys"] = [digit_set("k0", -0.17, 0.0), digit_set("k1", 0.0, 0.0)]
    W["digits"]["locks"] = [digit_set("l0", 0.5, 0.0), digit_set("l1", 0.67, 0.0)]
    # the clock row (the footage): a second plate under the first, with 12:01
    W["clockrow"] = []
    p2 = b("tag.edge2", (1.62, 0.7, 0.006), (0, -0.74, 0.0), edge)
    p3 = b("tag.plate2", (1.56, 0.64, 0.006), (0, -0.74, 0.007), plate)
    W["clockrow"] += [p2, p3]
    cdig = [digit_set("c0", -0.42, -0.74, 0.15, 0.4, 0.05), digit_set("c1", -0.22, -0.74, 0.15, 0.4, 0.05),
            digit_set("c2", 0.22, -0.74, 0.15, 0.4, 0.05), digit_set("c3", 0.42, -0.74, 0.15, 0.4, 0.05)]
    dots = [b("tag.colon1", (0.06, 0.06, 0.006), (0.0, -0.66, z), ink), b("tag.colon2", (0.06, 0.06, 0.006), (0.0, -0.82, z), ink)]
    W["digits"]["clock"] = cdig
    W["clockrow"] += dots
    W["tagparts"] = [ob for ob in root.children_recursive]


def _digit(d, n):
    segs = DIGIT_SEGS.get(n, "") if n is not None else ""
    for k, ob in d.items():
        ob.hide_render = k not in segs


def set_tag(tl, t, lens):
    tg = sample(tl, "tag", t, {"n": 0, "clock": 0, "keys": 12})
    keys, n, clock = int(tg["keys"]), int(tg["n"]), int(tg["clock"])
    _digit(W["digits"]["keys"][0], keys // 10 if keys >= 10 else None)
    _digit(W["digits"]["keys"][1], keys % 10)
    _digit(W["digits"]["locks"][0], n // 10 if n >= 10 else None)
    _digit(W["digits"]["locks"][1], n % 10)
    on = clock > 0
    for ob in W["clockrow"]:
        ob.hide_render = not on
    hh, mm = clock // 100, clock % 100
    vals = [hh // 10, hh % 10, mm // 10, mm % 10]
    for d, v in zip(W["digits"]["clock"], vals):
        _digit(d, v if on else None)
    dist = 1.0
    h2 = dist * 12.0 / lens
    w2 = h2 * 9.0 / 16.0
    s = 0.37 * w2
    tag = W["tag"]
    tag.scale = (s, s, s)
    # top-left, inside the 18% crop the polish pack can add (its top-left corner stays in frame)
    tag.location = (-0.69 * w2 + 0.81 * s, 0.70 * h2 - 0.43 * s, -dist)


# ---------------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    W.clear()
    W.update(kit=kit, story=story, inited=False)
    W["shots"] = {s["id"]: s for s in story["shots"]}
    sc = bpy.context.scene
    try:
        W["bg"] = sc.world.node_tree.nodes["Background"]
    except Exception:
        W["bg"] = None
    W["sun"] = kit.light("sun", "SUN", (0, 0, 50), 4.5, "#fff1d8", size=0.1)
    W["sun"].data.angle = 0.06
    W["sun"].rotation_euler = (math.radians(50), math.radians(8), math.radians(-30))
    W["moon"] = kit.light("moon", "SUN", (0, 0, 50), 1.1, "#9fc4ff", size=0.1)
    W["moon"].data.angle = 0.3
    W["moon"].rotation_euler = (math.radians(55), math.radians(-10), math.radians(150))
    W["key"] = None
    W["camkey"] = kit.light("camkey", "POINT", (0, 0, 5), 60, "#ffc27a", size=0.5, shadow=False)
    W["camfill"] = kit.light("camfill", "POINT", (0, 0, 5), 40, "#fff0dc", size=0.8, shadow=False)
    W["loulight"] = kit.light("loulight", "POINT", (0, 0, 5), 34, "#ffd2a0", size=0.5, shadow=False)
    W["tablelight"] = kit.light("tablelight", "POINT", (G.STAGE["kitchen"][0], G.STAGE["kitchen"][1] - 2.3, 2.5), 260, "#ffd9a8",
                                size=0.6, shadow=False)
    W["stairlight"] = kit.light("stairlight", "POINT", (G.STAGE["hall"][0] - 1.4, G.STAGE["hall"][1] - 1.2, 1.9), 120, "#ffc680",
                                size=0.5, shadow=False)
    for nmx in ("sun", "moon", "camkey", "camfill", "loulight", "tablelight", "stairlight"):
        kit.LIGHTS[nmx]["obj"].visible_camera = False
    build_court(kit)
    build_key(kit)
    build_room(kit)
    build_window(kit)
    build_tag(kit)
    try:
        from blocky import polish
        W["camspecs"] = polish.cam_specs(story, tl, polish.spec(story))
    except Exception:
        W["camspecs"] = None
    return {}


def late(kit):
    """Once the cast exists: Lou's key ring and blanket, my box and wet toes, Mr. Ames's moustache, Mrs. Haddad's ponytail."""
    g = bpy.data.objects.get
    W["late"] = {}
    lt = g("lou.torso")
    if lt is not None:
        build_waist_ring(kit, lt)
    la = g("lou.arm1")
    W["blanket_arm"], W["blanket_sh"], W["mebox"], W["wet"] = [], [], [], []
    blue, stripe = P("#4f7fd8", 0.9, 0.05), P("#a9c2f0", 0.9, 0.05)
    if la is not None:
        W["blanket_arm"] = [B(la, (1.5, 1.7, 0.55), (0, -0.55, -1.15), blue, "blanketfold", 0.1),
                            B(la, (1.52, 1.72, 0.12), (0, -0.55, -1.0), stripe, "blanketstripe", 0.04)]
    mt = g("me.torso")
    if mt is not None:
        W["blanket_sh"] = [B(mt, (3.0, 1.9, 0.75), (0, 0.0, 1.62), blue, "shoulderblanket", 0.14),
                           B(mt, (3.0, 0.45, 3.0), (0, 0.8, 0.5), blue, "backblanket", 0.1),
                           B(mt, (1.1, 0.3, 2.2), (-0.95, -0.82, 0.85), blue, "frontflap", 0.1),
                           B(mt, (1.1, 0.3, 2.2), (0.95, -0.82, 0.85), blue, "frontflap", 0.1),
                           B(mt, (1.12, 0.32, 0.18), (-0.95, -0.82, -0.1), stripe, "flapstripe", 0.04),
                           B(mt, (1.12, 0.32, 0.18), (0.95, -0.82, -0.1), stripe, "flapstripe", 0.04),
                           B(mt, (3.02, 0.47, 0.18), (0, 0.8, -0.9), stripe, "backstripe", 0.04),
                           B(mt, (3.02, 1.92, 0.12), (0, 0.0, 1.99), stripe, "shoulderstripe", 0.03)]
        W["mebox"] = [B(mt, (1.7, 1.2, 1.3), (0.0, -1.15, 0.15), P("#c8995a", 0.85, 0.05), "mebox", 0.05),
                      B(mt, (1.72, 0.2, 0.16), (0.0, -1.15, 0.8), P("#e8d0a0", 0.85, 0.05), "meboxtape")]
    for sx in (-1, 1):
        leg = g(f"me.leg{sx}")
        if leg is not None:
            W["wet"].append(B(leg, (0.86, 0.06, 0.17), (0, -0.535, -1.85), P("#5b6f86", 0.1, 0.8), "wettoe", 0.04))
    ma = g("me.arm1")
    W["mekey"] = []
    if ma is not None:
        kb = P("#ffd24a", 0.2, 1.0)
        W["mekey"] = [B(ma, (0.1, 0.07, 0.62), (0, -0.14, -1.9), kb, "mekeyshaft", 0.01),
                      B(ma, (0.34, 0.07, 0.34), (0, -0.14, -1.5), kb, "mekeybow", 0.05),
                      B(ma, (0.2, 0.07, 0.08), (0.12, -0.14, -2.12), kb, "mekeytooth", 0.01)]
    ah = g("ames.headg")
    if ah is not None:
        wm = P("#f4f4f2", 0.8)
        B(ah, (0.5, 0.1, 0.12), (0, -0.63, -0.2), wm, "amesmoustache", 0.04)
        for sx in (-1, 1):
            B(ah, (0.12, 0.1, 0.14), (sx * 0.28, -0.6, -0.22), wm, "amesmoustache", 0.04)
    lh = g("lou.headg")
    import re as _re
    for o in bpy.data.objects:      # clear lenses: frames only, so her eyes show at phone size
        if _re.match(r"^lou\.gl-?1(\.\d+)?$", o.name):
            o.hide_render = True
            o.scale = (0.001, 0.001, 0.001)     # the pose re-shows hidden parts, so shrink the lens away too
    if lh is not None:
        pr = P("#f8f4ee", 0.2, 0.9)
        for sx in (-1, 1):
            kit.sphere(nm("pearl"), 0.1, (sx * 0.69, 0.0, -0.32), pr, lh, seg=10)
            B(lh, (0.05, 0.05, 0.18), (sx * 0.66, 0.0, -0.18), P(BRASS, 0.3, 0.9), "earringpost")
    hh = g("haddad.headg")
    if hh is not None:
        B(hh, (0.34, 0.34, 0.6), (0, 0.62, -0.1), P("#241a16", 0.7), "haddadponytail", 0.12)
    W["inited"] = True


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        late(kit)
    L = look_at(tl, t)
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    sd = W["shots"].get(shot["id"], {})
    cl = ct = None
    lens = 36.0
    try:
        from blocky import bl_story
        cl, ct, lens, _ = bl_story.cam_at(W["camspecs"][shot["id"]], shot, t, {}, tl)
    except Exception:
        k0 = sd.get("cam", [[0, [0, -3, 1.5], [0, 0, 1.5], 36]])[0]
        cl, ct, lens = k0[1], k0[2], k0[3]
    sc = bpy.context.scene
    if W["bg"] is not None:
        W["bg"].inputs["Color"].default_value = (*L["sky"], 1.0)
        W["bg"].inputs["Strength"].default_value = L["world"]
    sc.view_settings.exposure = L["exp"] + sd.get("exp", 0.0)
    hide(W["starroot"], L["stars"] < 0.08)
    for nd in W["stars"].node_tree.nodes:
        if nd.type == "EMISSION":
            nd.inputs["Strength"].default_value = 6.0 * L["stars"]
    for nd in W["winglass"].node_tree.nodes:
        if nd.type == "EMISSION":
            nd.inputs["Color"].default_value = (*L["win"], 1.0)
            nd.inputs["Strength"].default_value = L["wins"]
    # the camera's own soft warm key and fill: on faces, scaled by distance so a close-up is not blown out
    f = V(ct) - V(cl)
    dist = max(0.3, f.length)
    f.normalize()
    r = f.cross(V((0, 0, 1)))
    r = r.normalized() if r.length > 1e-6 else V((1, 0, 0))
    kpos = V(cl) - r * 0.7 + V((0, 0, 0.6))
    W["camkey"].location = (kpos.x, kpos.y, kpos.z)
    fpos = V(cl) + r * 0.9 + V((0, 0, 0.1))
    W["camfill"].location = (fpos.x, fpos.y, fpos.z)
    fg = min(2.2, max(0.05, (dist / 3.0) ** 2))
    face = 1.0 if sd.get("face", True) else 0.0
    # a steady soft warm light in front of Lou's face, whenever she is near the camera
    lg = 0.0
    lh_ = bpy.data.objects.get("lou.headg")
    if lh_ is not None:
        bpy.context.view_layer.update()
        hp = lh_.matrix_world.translation
        dv = V(cl) - hp
        if dv.length < 8.0 and hp.z > -5 and hp.y > -30:
            dv.normalize()
            q = hp + dv * 1.0 + V((0, 0, 0.15))
            W["loulight"].location = (q.x, q.y, q.z)
            lg = 1.0
    gains = {"loulight": lg, "sun": L["sun"], "moon": L["moon"],
             "camkey": face * sd.get("key", 1.0) * fg * (0.55 if L["sun"] > 0.3 else 1.0),
             "camfill": L["fill"] * sd.get("fill", 1.0) * fg * (1.0 if face else 0.4)}
    # the key in a lock
    kc = cue_at(tl, "key", t)
    root, keyg = W["key"]
    if kc.get("on"):
        px, py, pz = G.hw(kc["k"], kc.get("lx", 0.38), 0.145, LAND + kc.get("lz", 0.78))
        root.location = (px, py, pz)
        root.rotation_euler = (0, 0, math.radians(-G.ang(kc["k"])))
        a0, a1 = kc.get("a0", 0), kc.get("a1", 0)
        u = ss((t - kc["t"]) / max(1e-3, kc.get("dur", 0.5)))
        keyg.rotation_euler = (0, math.radians(lerp(a0, a1, u)), 0)
        for o in root.children:
            if o.name.startswith(("keysleeve", "keycuff", "keyhand")):
                o.hide_render = not kc.get("hand", True)
    else:
        root.location = (0, 0, -20)
    # doors
    for k, hg in W["hinges"].items():
        dc = cue_at(tl, f"door{k}", t)
        a = lerp(dc["a0"], dc["a1"], ss((t - dc["t"]) / max(1e-3, dc["dur"]))) if dc else 0.0
        hg.rotation_euler = (0, 0, math.radians(a))
    # the ring swings softly at her waist
    if W.get("ring") is not None:
        W["ring"].rotation_euler = (0.05 * math.sin(t * 2.3), 0.0, 0.09 * math.sin(t * 1.7 + 0.8))
    bl = cue_at(tl, "blanket", t).get("where", "none")
    for o in W.get("blanket_arm", []):
        hide(o, bl != "arm")
    for o in W.get("blanket_sh", []):
        hide(o, bl != "shoulders")
    for o in W.get("mebox", []):
        hide(o, not cue_at(tl, "box", t).get("on"))
    for o in W.get("mekey", []):
        hide(o, not cue_at(tl, "mekey", t).get("on"))
    wet = bool(cue_at(tl, "wet", t).get("on"))
    for o in W.get("wet", []):
        hide(o, not wet)
    hide(W["wetmarks"], not wet)
    hide(W["sneaks"], not cue_at(tl, "sneaks", t).get("on"))
    hide(W["mycam"], not cue_at(tl, "mycam", t).get("on"))
    # my thumb-turn bolt
    th = cue_at(tl, "bolt", t)
    if th:
        W["thumb"].rotation_euler = (0, math.radians(lerp(th.get("a0", 0), th.get("a1", 0), ss((t - th["t"]) / max(1e-3, th.get("dur", 0.6))))), 0)
    else:
        W["thumb"].rotation_euler = (0, 0, 0)
    set_tag(tl, t, lens)
    return gains
