"""ep98 "town whistle": one bright summer street, a green pole with a brass whistle, and the Under below it all.

Built by hand from kit.py's parts (no text anywhere; the only marks are numerals on the brass step-counter tag).
Several small sets sit far apart in one scene, and each shot's camera is in one of them:
- STREET at the origin: the road along y, the pole and whistle at (0, 0), our white house (-14, 6), Grandpa's
  butter house on stone blocks (-14, -6, with a real room inside), the Dunns' blue house (14, 6), filler houses,
  trees, basement window wells, cellar bulkheads, a ball field far down the road.
- HOUSE at (100, 0): our kitchen and dining room, the basement door, the stairwell (up to 41 steps), the landing with
  its crack, the cavern and THE UNDER lying face up under it.
- KITCHEN (Grandpa's) is in the street house itself. BAKERY at (-200, 0) is a small stage. CUTAWAY at (0, 200) is a
  bright diagram of the street cut like a cake.
- THE TAG: a brass step-counter plate glued to the camera, top right, in every shot (the rule meter).
Cues (story.json "cues", each restates its whole state): steps, tag, puff, lamp, under, door, dust, kettle, cut.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import faces, rig

TMP = Path(tempfile.mkdtemp(prefix="townwhistle-"))
SX = 100.0            # the house set's x origin (the wall with the basement door)
RISE, RUN = 0.27, 0.28
MAXSTEPS = 41
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


def CY(parent, r, h, loc, mat, name="c", rot=(0, 0, 0), n=24, r2=None):
    return K.kit.cyl(nm(name), r, h, loc, mat, parent, rot, n, r2)


def E(parent, loc=(0, 0, 0), name="e", rot=(0, 0, 0)):
    return K.kit.empty(nm(name), loc, parent, rot)


def no_shadow(ob):
    try:
        ob.visible_shadow = False
    except Exception:
        pass
    for c in ob.children_recursive:
        try:
            c.visible_shadow = False
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


def eased(tl, name, t, key="pos"):
    """A cue with key and "to" over "dur": the value at t."""
    c = cue_at(tl, name, t)
    if not c or key not in c:
        return None
    a = c[key]
    if "to" in c:
        u = ss((t - c["t"]) / max(1e-3, c.get("dur", 1.0)))
        return [lerp(x, y, u) for x, y in zip(a, c["to"])]
    return a


# ------------------------------------------------------------------------------------------------ the look of each shot
# sun: (azimuth deg, elevation deg, energy, colour); sky: bottom, mid, top; world: strength; exp: exposure
LOOKS = {
    "day": {"sun": (35, 52, 5.2, "#fff4de"), "sky": ("#bfe4ff", "#8fd0ff", "#4aa8ff"), "world": 1.15, "exp": 0.15},
    "gold": {"sun": (80, 10, 4.6, "#ffb860"), "sky": ("#ffd9a0", "#ffc27a", "#8fb4ff"), "world": 0.95, "exp": 0.2},
    "morning": {"sun": (-60, 24, 3.4, "#ffe6bd"), "sky": ("#d7ecff", "#a8d8ff", "#62b2ff"), "world": 0.95, "exp": 0.0},
    "night": {"sun": (0, 5, 0.0, "#6a78c8"), "sky": ("#2b3a78", "#1b2656", "#0d1436"), "world": 0.6, "exp": 0.3},
    "in": {"sun": (35, 52, 0.0, "#fff4de"), "sky": ("#bfe4ff", "#8fd0ff", "#4aa8ff"), "world": 0.5, "exp": 0.15},
    "dawn": {"sun": (-70, 12, 4.2, "#ffd6a8"), "sky": ("#ffe4c4", "#ffd0a0", "#9cc8ff"), "world": 1.0, "exp": 0.2},
}


def mix_look(a, b, u):
    out = {}
    for k in a:
        va, vb = a[k], b[k]
        if k == "sky":
            out[k] = [mixhex(x, y, u) for x, y in zip(va, vb)]
        elif k == "sun":
            out[k] = (lerp(va[0], vb[0], u), lerp(va[1], vb[1], u), lerp(va[2], vb[2], u), mixhex(va[3], vb[3], u))
        else:
            out[k] = lerp(va, vb, u)
    return out


def look_at(ctx, tl, t):
    shots = tl["shots"]
    cur = next((s for s in shots if s["start"] <= t < s["end"]), shots[-1])
    i = shots.index(cur)
    A = LOOKS[ctx["shots"][cur["id"]].get("look", "day")]
    if i + 1 < len(shots) and t > cur["end"] - 0.4:
        nb = LOOKS[ctx["shots"][shots[i + 1]["id"]].get("look", "day")]
        if nb is not A:
            return mix_look(A, nb, ss((t - (cur["end"] - 0.4)) / 0.4)), cur
    return mix_look(A, A, 0.0), cur


# ------------------------------------------------------------------------------------------------ the tag (rule meter)
def tag_image(n):
    from PIL import Image, ImageDraw, ImageFont

    p = TMP / f"tag-{n}.png"
    if not p.exists():
        W, H = 280, 340
        im = Image.new("RGB", (W, H), hexrgb("#8a5a1c"))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([10, 10, W - 11, H - 11], 26, fill=hexrgb("#f0b84a"))
        d.rounded_rectangle([22, 22, W - 23, H - 23], 18, outline=hexrgb("#8a5a1c"), width=7)
        ink = hexrgb("#2a1608")
        # the stair glyph: four steps going down to the right
        x0, y0, sw, sh = 62, 44, 40, 24
        pts = [(x0, y0)]
        for k in range(4):
            pts += [(x0 + sw * (k + 1), y0 + sh * k), (x0 + sw * (k + 1), y0 + sh * (k + 1))]
        pts += [(x0, y0 + sh * 4)]
        d.polygon(pts, fill=ink)
        try:
            f = ImageFont.truetype("DejaVuSans-Bold.ttf", 150 if n < 100 else 110)
        except Exception:
            f = ImageFont.load_default()
        txt = str(n)
        bb = d.textbbox((0, 0), txt, font=f)
        d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], 150 - bb[1]), txt, fill=ink, font=f)
        im.save(p)
    return str(p)


def build_tag(kit, ctx):
    cam = kit.OBJ["cam"]
    m = kit._new(nm("tag"))
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    gc = nt.nodes.new("ShaderNodeTexCoord")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 0.9
    nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    pl = kit.plane(nm("tag"), (1.0, 1.0), (0, 0, -0.15), m, cam)
    no_shadow(pl)
    ctx["tag"] = (pl, tex)
    ctx["tag_imgs"] = {}


def place_tag(kit, ctx, n, lens, big=1.0):
    pl, tex = ctx["tag"]
    if n not in ctx["tag_imgs"]:
        im = bpy.data.images.load(tag_image(n))
        im.colorspace_settings.name = "sRGB"
        ctx["tag_imgs"][n] = im
    tex.image = ctx["tag_imgs"][n]
    d = 0.15
    unit = d / lens
    pw = 0.22 * 13.5 * unit * big
    ph = pw * 340 / 280
    if big > 1.0:
        pl.location = (0.0, 0.18 * 12.0 * unit, -d)
    else:
        pl.location = (0.66 * 6.75 * unit, 0.70 * 12.0 * unit, -d)
    pl.scale = (pw, ph, 1)


# ------------------------------------------------------------------------------------------------ the Under
def _limb(parent, a, b, w, mat, name):
    """A box w x w from point a to point b (local coords)."""
    d = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    ln = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
    th = math.acos(d[2] / ln)
    ph = math.atan2(d[1], d[0])
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)
    return B(parent, (w, w, ln), mid, mat, name, 0.06, rot=(0, th, ph))


EYY = 1.1   # eye height on the face (local y)
EX = 1.1    # eye half-spacing


def make_under(kit, parent, scale=1.0, pipe_h=5.3, body=True, dark=False):
    """A person built wrong, lying face up: a head as wide as the cellar, a thin long neck, shoulders wider than the
    room, one arm far too long that reaches up the wall and hooks its fingers over the crack edge. Local frame: the
    face looks +z, its width runs along x, the mouth/chin end is toward -y (the body goes that way)."""
    R = E(parent, (0, 0, 0), "under")
    skin = P("#2a201c" if dark else "#7a5638", 0.9, 0.02)
    skin_d = P("#120e0d" if dark else "#2b2019", 0.95, 0.0)
    clay = P("#2a201c" if dark else "#b98a5a", 0.9, 0.02)
    coat = P("#171b24", 0.9, 0.02)
    collar = P("#3a3630", 0.85, 0.02)
    hair = P("#08080a", 0.95, 0.0)
    W_, D_, T_ = 6.4, 4.6, 0.9
    B(R, (W_, D_, T_), (0, 0, -T_ / 2), skin, "uface", 0.14)
    # a cheek ridge on each side (warm clay, raked by the key) and a flat bridge of nose
    B(R, (0.5, 1.3, 0.25), (0, 0.15, 0.06), skin, "unose", 0.1)
    for sx in (-1, 1):
        B(R, (1.7, 1.9, 0.3), (sx * 2.3, -0.8, 0.05), clay, "ucheek", 0.1)
    # ears and jaw
    for sx in (-1, 1):
        B(R, (0.7, 1.5, 0.5), (sx * (W_ / 2 + 0.3), 0.2, -0.3), skin_d, "uear", 0.1)
    B(R, (4.6, 1.9, 0.6), (0, -D_ / 2 - 0.55, -0.2), (P("#2a201c", 0.9, 0.02) if dark else kit.emit("#4a3020", 0.45, name="uchinm")), "uchin", 0.1)
    # hair: a dark ragged slab over the crown (toward +y)
    B(R, (W_ + 0.2, 1.5, 0.5), (0, D_ / 2 + 0.55, -0.1), hair, "uhair", 0.1)
    for i, hx in enumerate((-2.4, -0.8, 1.0, 2.5)):
        B(R, (1.1, 0.9, 0.35), (hx, D_ / 2 - 0.35 - 0.12 * (i % 2), 0.06), hair, "uhair", 0.08)
    # a hard sooty brow block right above each eye
    soot = P("#0e0b0a", 0.95, 0.0)
    for sx in (-1, 1):
        B(R, (1.7, 0.55, 0.5), (sx * 1.15, EYY + 0.62, 0.2), soot, "ubrow", 0.04, rot=(0, 0, sx * 0.1))
    # soot seams across the clay face (kept off the eyes and the mouth)
    for sy_, w_ in ((0.25, 5.6), (-2.1, 5.0)):
        B(R, (w_, 0.09, 0.08), (0, sy_, 0.03), soot, "uscar", 0.0)
    for sx in (-1, 1):
        B(R, (0.09, 1.6, 0.08), (sx * 2.1, -0.9, 0.03), soot, "uscar", 0.0)
        B(R, (0.09, 2.0, 0.08), (sx * 2.7, 0.8, 0.03), soot, "uscar", 0.0)
    # eyes: square blocks sunk in dark sockets, two lamp-yellow glints (the brightest points in frame)
    ey = []
    eyes_mat = kit.emit("#ffd84a", 3.2, name="undereye")
    sock = P("#050404", 0.95, 0.0)
    halo = kit.emit("#a86a14", 0.9, name="uhalo")
    pup = P("#0a0807", 0.95, 0.0)
    for sx in (-1, 1):
        B(R, (1.4, 1.0, 0.12), (sx * EX, EYY, 0.04), sock, "usock", 0.06)
        B(R, (0.9, 0.62, 0.05), (sx * EX, EYY - 0.08, 0.075), halo, "uhalo", 0.0)
        d = B(R, (0.62, 0.4, 0.06), (sx * EX, EYY - 0.08, 0.11), eyes_mat, "ueye", 0.0)
        pu = CY(R, 0.001, 0.001, (sx * EX, EYY, 0.085), pup, "upup", n=6)
        ey.append((d, pu, sx * EX))
    # the mouth: a round coal-black hole inside a raised, lit clay lip ring
    dk = P("#020202", 0.95, 0.0)
    MY = -1.15
    CY(R, 1.0, 0.1, (0.0, MY, 0.06), dk, "umouth", n=16)
    lipm = P("#2a1f1a" if dark else "#9c7048", 0.8, 0.02)
    lipin = P("#1a110c", 0.9, 0.0)
    for i in range(12):
        an = 2 * math.pi * i / 12
        B(R, (0.78, 0.5, 0.34), (1.28 * math.cos(an), MY + 1.28 * math.sin(an), 0.2), lipm, "ulip", 0.1, rot=(0, 0, an + math.pi / 2))
        B(R, (0.62, 0.34, 0.3), (1.0 * math.cos(an), MY + 1.0 * math.sin(an), 0.22), lipin, "ulipin", 0.08, rot=(0, 0, an + math.pi / 2))
    prm = None
    if pipe_h:
        # the pipe: bright brass, wedged in the mouth; rake shots shorten it (scale z) so its tip stays in view
        brass = kit.emit("#e8b44a", 0.6, name="upipebrass")
        prm = E(R, (0.3, MY, 0.0), "upiper")
        pp = CY(prm, 0.2, pipe_h, (0, 0, pipe_h / 2), brass, "upipe")
        pp.rotation_euler = (0.1, 0.14, 0)
        CY(prm, 0.34, 0.2, (0, 0, 0.3), brass, "upipecol")
    bod = []
    if body:
        # neck: thin and too long; shoulders: wider than the room; the coat is near black
        bod.append(B(R, (1.7, 2.6, 1.0), (0, -D_ / 2 - 2.0, -0.4), skin_d, "uneck", 0.1))
        bod.append(B(R, (10.0, 2.4, 1.7), (0, -D_ / 2 - 4.2, 0.0), coat, "ushoulder", 0.25))
        # the one lit identity cue: a pale shirt collar and a dark tie at the neck
        for sx in (-1, 1):
            bod.append(B(R, (2.0, 1.9, 0.3), (sx * 1.15, -D_ / 2 - 3.0, 0.62), collar, "ucollar", 0.04, rot=(0, 0, sx * -0.5)))
        bod.append(B(R, (0.5, 1.8, 0.2), (0, -D_ / 2 - 3.3, 0.7), P("#2a1010", 0.9, 0.0), "utie", 0.03))
        # right arm: far too long, an extra joint, up the wall and hooked over the crack edge (land coords: x 2.0, y -0.55, z 0)
        sh = (4.6, -D_ / 2 - 4.2, 0.4)
        el = (4.0, -D_ / 2 - 3.4, 2.8)
        wr = (1.0, 0.45, 5.6)
        bod.append(_limb(R, sh, el, 1.0, coat, "uarm"))
        bod.append(_limb(R, el, wr, 0.7, skin_d, "uforearm"))
        bod.append(B(R, (0.9, 0.55, 0.3), (0.95, 0.5, 5.7), skin, "upalm", 0.05))
        for i in range(4):
            bod.append(B(R, (0.9, 0.2, 0.2), (1.8, 0.2 + 0.28 * i, 5.72 + 0.03 * (i % 2)), skin, "ufinger", 0.05))
        # left arm lies along the floor, the hand open and too long
        bod.append(_limb(R, (-4.6, -D_ / 2 - 4.2, 0.0), (-3.4, -D_ / 2 - 2.0, -0.55), 0.9, coat, "uarmL"))
        bod.append(B(R, (0.8, 2.2, 0.3), (-3.4, -D_ / 2 - 0.6, -0.55), skin_d, "uhandL", 0.05))
    R.scale = (scale, scale, scale)
    return {"root": R, "eyes": ey, "pipe_root": prm, "body": bod}



# ------------------------------------------------------------------------------------------------ people's extras
def late_extras(kit, ctx):
    """Called once the cast exists: mustaches, beard, shoulder dust."""
    C = rig.CHARS
    ink = {"dad": "#3a2e28", "me": "#2a1c14", "arlo": "#f4f4f2", "mr_dunn": "#3a3430"}
    for who, col in ink.items():
        ch = C.get(who)
        if ch is None:
            continue
        hg = ch.head.children[0] if ch.head.children else None
        hg = next((c for c in ch.head.children if c.name.endswith(".headg")), hg)
        m = P(col, 0.8, 0.05)
        R = faces.HEAD_R
        if who in ("dad", "arlo", "mr_dunn"):
            B(hg, (0.62, 0.1, 0.17), (0, -R + 0.005, -0.11), m, "must", 0.04)
            for sx in (-1, 1):
                B(hg, (0.2, 0.1, 0.15), (sx * 0.36, -R + 0.03, -0.14), m, "must", 0.04, rot=(0, 0, sx * -0.3))
        if who == "me":
            B(hg, (0.5, 0.09, 0.07), (0, -R + 0.01, -0.12), m, "must", 0.03)
            B(hg, (0.9, 0.11, 0.26), (0, -R + 0.0, -0.46), m, "beard", 0.06)
            for sx in (-1, 1):
                B(hg, (0.14, 0.1, 0.42), (sx * 0.5, -R + 0.1, -0.30), m, "beard", 0.05)
    dust = {}
    dm = kit.emit("#e8dcc0", 0.6, name="dustslab")
    for who, ch in C.items():
        d = E(ch.upper, (0, 0, 0), "dust")
        B(d, (3.5, 1.12, 0.3), (0, 0, 2.08), dm, "dsh", 0.08)
        B(d, (1.9, 1.0, 0.25), (0, 0, 2.3), dm, "dsh2", 0.08)
        B(d, (1.1, 0.8, 0.5), (0, 0, 2.55), dm, "dsh3", 0.12)
        hide(d, True)
        dust[who] = d
    ctx["dust"] = dust


# ------------------------------------------------------------------------------------------------ houses (street)
def clapboard(kit, parent, w, d, h, loc, base, name="wall"):
    """A house body with horizontal board lines (thin darker strips a hair proud)."""
    B(parent, (w, d, h), loc, P(base, 0.7, 0.1), name, 0.04)


def house(kit, x, y, face, color, trim="#ffffff", roof="#c0503a", w=7.0, d=6.0, h=3.2, floor_z=0.0, name="house"):
    """A plain house; face = +1 if its front looks toward +x (left-side houses), -1 toward -x. Front wall at x +- d/2."""
    G = E(None, (x, y, floor_z), name)
    body = P(color, 0.75, 0.1)
    B(G, (d, w, h), (0, 0, h / 2), body, "body", 0.04)
    # clapboard lines on the front
    for k in range(1, int(h / 0.45)):
        B(G, (0.02, w + 0.01, 0.025), (face * (d / 2 + 0.005), 0, k * 0.45), P("#000000", 0.9, 0.0) if False else P(trim, 0.7, 0.0), "lap", 0.0)
    # roof: two sloped slabs
    rs = P(roof, 0.7, 0.1)
    ang = math.radians(26)
    for s in (-1, 1):
        B(G, (d / 2 / math.cos(ang) + 0.6, w + 0.8, 0.22), (s * d / 4 * 0.98, 0, h + 0.72), rs, "roof", 0.04, rot=(0, -s * ang * 1.0 * -1, 0) if False else (0, s * ang, 0))
    # door and windows on the front
    fx = face * (d / 2 + 0.02)
    B(G, (0.08, 1.0, 2.1), (fx, w * 0.3, 1.05), P("#c0503a" if color != "#ffe27a" else "#3f78c8", 0.5, 0.2), "door", 0.02)
    B(G, (0.1, 0.1, 0.1), (fx + face * 0.03, w * 0.3 - 0.33, 1.05), P("#e8b44a", 0.3, 0.7), "knob", 0.03)
    for wy in (-w * 0.28,):
        B(G, (0.08, 1.2, 1.2), (fx, wy, 1.7), P("#fffaf0", 0.5, 0.2), "winframe", 0.02)
        B(G, (0.1, 1.0, 1.0), (fx + face * 0.02, wy, 1.7), kit.emit("#9fd4ff", 1.2, name="winglow"), "win", 0.0)
    # porch: a deck and two posts
    B(G, (1.4, w * 0.6, 0.18), (face * (d / 2 + 0.7), w * 0.12, 0.09), P("#efe6d4", 0.7, 0.1), "porch", 0.03)
    return G


def tree(kit, x, y, h=6.0, kind="commontree_1", tint="#8fe05a"):
    try:
        kit.prop(kind, (x, y, 0), rot=(x * 7 + y * 13) % 360, height=h, tint=tint)
    except Exception:
        pass


def bulkhead(kit, x, y, face, name="bulk"):
    """A cellar hatch house on a lawn: a low block with a dark doorway facing the street (face = +1: the house is at +x,
    the doorway looks toward -x) and a slanted open door laid on its roof."""
    G = E(None, (x, y, 0), name)
    wall = P("#b9b2a4", 0.85, 0.05)
    for sy in (-1, 1):
        B(G, (1.4, 0.25, 1.15), (0, sy * 0.65, 0.575), wall, "hwall", 0.02)
    B(G, (0.25, 1.55, 1.15), (face * 0.575, 0, 0.575), P("#0a0705", 0.95, 0.0), "hback", 0.0)
    B(G, (1.5, 1.55, 0.18), (0, 0, 1.24), wall, "hroof", 0.02)
    B(G, (1.3, 0.14, 0.6), (-face * 0.0, 0, 0.5), P("#0a0705", 0.95, 0.0), "hfloor", 0.0) if False else None
    B(G, (0.5, 1.2, 0.1), (-face * 0.95, 0, 0.05), P("#a09888", 0.8, 0.05), "hstep", 0.0)
    return G


def build_street(kit, ctx):
    lawn = P("#58c84a", 0.85, 0.08)
    B(None, (70, 150, 0.4), (0, -10, -0.2), lawn, "lawn")
    road = kit.texture("asphalt", 0.35, tint="#aab4c8")
    B(None, (7.0, 150, 0.12), (0, -10, 0.0), road, "road")
    for k in range(-14, 11):                                     # dashed centre line
        if abs(k * 5.5) > 1.5:
            B(None, (0.14, 2.4, 0.01), (0, k * 5.5, 0.065), P("#fff0b0", 0.7, 0.0), "dash")
    for sx in (-1, 1):
        B(None, (1.8, 150, 0.2), (sx * 4.4, -10, 0.0), P("#d8d6d0", 0.8, 0.05), "walk")
        B(None, (0.3, 150, 0.24), (sx * 3.55, -10, 0.0), P("#bdbab4", 0.8, 0.05), "curb")
    # the pole and the whistle
    green, brass, iron = P("#2f9a56", 0.4, 0.4), P("#f0b84a", 0.28, 0.8), P("#40454e", 0.5, 0.5)
    Pl = E(None, (0, 0, 0), "pole")
    CY(Pl, 0.3, 0.3, (0, 0, 0.15), iron, "polebase")
    CY(Pl, 0.14, 6.0, (0, 0, 3.0), green, "pole")
    CY(Pl, 0.2, 0.3, (0, 0, 5.9), green, "polecap")
    # the whistle: a brass drum with a slot mouth on its front (toward -y), a cap, a flared bell below
    CY(Pl, 0.5, 0.34, (0, 0, 6.2), brass, "wbase", r2=0.38)
    CY(Pl, 0.36, 0.9, (0, 0, 6.82), brass, "wbody")
    CY(Pl, 0.4, 0.14, (0, 0, 7.34), brass, "wcap")
    B(Pl, (0.46, 0.22, 0.34), (0, -0.33, 6.9), P("#1b130d", 0.9, 0.0), "wmouth", 0.02)          # the slot
    B(Pl, (0.58, 0.12, 0.1), (0, -0.38, 7.12), brass, "wlip", 0.02)
    CY(Pl, 0.07, 0.4, (0, 0, 7.62), brass, "wknob")
    # the pipe at the foot: out of the pole, out sideways, down into a round iron collar in the road
    CY(Pl, 0.1, 1.0, (0.55, 0, 0.9), brass, "pipeh", rot=(0, math.pi / 2, 0))
    CY(Pl, 0.1, 0.9, (1.05, 0, 0.5), brass, "pipev")
    CY(Pl, 0.5, 0.1, (1.05, 0, 0.07), iron, "collar", n=28)
    CY(Pl, 0.28, 0.12, (1.05, 0, 0.12), P("#101012", 0.9, 0.0), "collarhole", n=24)
    ctx["pole"] = Pl
    ctx["whistle_mouth"] = (0, -0.5, 6.9)
    ctx["collar_pos"] = (1.05, 0.0, 0.15)
    # houses
    ctx["house_our"] = house(kit, -14, 3.5, 1, "#f7f5ee", roof="#c8523c", name="ours")
    ctx["house_dunn"] = house(kit, 14, 6, -1, "#a9dcff", roof="#7a5ad0", name="dunns")
    for (x, y, f, c, r) in ((14, -8, -1, "#ffd0e0", "#4a8a7a"), (14, 21, -1, "#f7f5ee", "#3a70c8"),
                           (-14, 21, 1, "#c8f0d8", "#c8523c"), (14, -22, -1, "#ffe9a8", "#c8523c"),
                           (-14, -22, 1, "#d8c8ff", "#4a8a7a"), (-14, 34, 1, "#ffd0b0", "#3a70c8"),
                           (14, 34, -1, "#c8e8ff", "#c8523c"), (14, -36, -1, "#f7f5ee", "#7a5ad0"),
                           (-14, -36, 1, "#ffd0e0", "#3a70c8")):
        house(kit, x, y, f, c, roof=r, name="neighbor")
    for i, (x, y) in enumerate(((-8.4, 28.5), (8.4, 28.5), (-8.4, -15.5), (8.4, -15.5),
                                (8.4, -29.0), (-8.4, -29.0), (8.4, 45.0), (-8.4, 45.0), (8.4, -44.0), (-8.4, -44.0))):
        tree(kit, x, y, h=5.5 + (i % 3), kind="commontree_1" if i % 2 else "birchtree_1",
             tint="#8fe05a" if i % 2 else "#b9f090")
    # low white fence between our lawn and Grandpa's
    wh = P("#fbfaf4", 0.5, 0.15)
    for i in range(14):
        B(None, (0.08, 0.08, 0.9), (-8.0 - 0.7 * i, -0.8, 0.45), wh, "post", 0.01)
    B(None, (9.8, 0.05, 0.07), (-12.7, -0.8, 0.75), wh, "frail", 0.01)
    B(None, (9.8, 0.05, 0.07), (-12.7, -0.8, 0.35), wh, "frail", 0.01)
    # basement window wells (not at Grandpa's: he has no basement) and cellar bulkheads
    ctx["wells"] = []
    for (x, y) in ((-10.1, 1.8), (-10.1, 3.4), (10.1, 7.0), (10.1, 9.2), (-10.1, 22.0), (10.1, 22.0), (10.1, -8.0), (10.1, -22.0), (-10.1, -22.0),
                   (-10.1, 34.0), (10.1, 34.0)):
        W = E(None, (x, y, 0), "well")
        B(W, (0.5, 1.1, 0.1), (0, 0, 0.05), P("#7c7870", 0.8, 0.05), "wellrim", 0.02)
        B(W, (0.36, 0.9, 0.06), (0, 0, 0.1), P("#14110e", 0.9, 0.0), "welldark", 0.0)
        for yy in (-0.3, -0.1, 0.1, 0.3):
            B(W, (0.04, 0.04, 0.06), (0, yy, 0.13), P("#40454e", 0.5, 0.4), "grille", 0.0)
        ctx["wells"].append((x, y))
    ctx["bulk_dunn"] = (8.2, 3.6)
    for (x, y, f) in ((8.6, 3.6, 1), (-8.6, 11.5, -1), (8.6, 18.0, 1)):
        bulkhead(kit, x, y, f)
    # the ball field at the far end of the street
    B(None, (26, 26, 0.04), (0, -64, 0.02), P("#c89a62", 0.95, 0.0), "infield")
    for (x, y) in ((11, -57), (-11, -57), (11, -71), (-11, -71)):
        B(None, (0.6, 0.6, 0.06), (x * 0.5 + 0, y, 0.07), P("#f6f6f0", 0.7, 0.0), "base")
    B(None, (3.0, 0.5, 0.5), (-6, -57, 0.3), P("#9b6a3a", 0.8, 0.05), "bench", 0.02)
    # a street lamp by the kerb (lit at night) and a wooden ladder that leans on the pole for the last act
    B(None, (0.12, 0.12, 4.6), (4.9, -3.4, 2.3), iron, "lamppost", 0.02)
    B(None, (0.9, 0.1, 0.1), (4.5, -3.4, 4.55), iron, "lamparm", 0.02)
    B(None, (0.4, 0.3, 0.1), (4.1, -3.4, 4.45), kit.emit("#ffd28a", 10.0, name="lampbulb"), "lampbulb", 0.02)
    ctx["lamp_street"] = kit.light("streetl", "POINT", (4.1, -3.4, 4.2), 1400, "#ffcf80", size=0.2)
    lad = E(None, (0.0, -0.9, 0), "ladder")
    wood = P("#c8964e", 0.6, 0.1)
    ang = math.radians(-8)
    for sx in (-0.3, 0.3):
        B(lad, (0.08, 0.08, 5.6), (sx, -0.35, 2.75), wood, "rail", 0.01, rot=(math.radians(-7), 0, 0))
    for k in range(10):
        B(lad, (0.6, 0.06, 0.06), (0, -0.05 - 0.36 * (1 - (k * 0.55 + 0.3) / 5.4) * 0.0, 0.5 + k * 0.5), wood, "rung", 0.01)
    ctx["ladder"] = lad
    hide(lad, True)
    lf = B(None, (0.16, 0.1, 0.01), (0, 0, -20), P("#6aa83a", 0.8, 0.0), "leaf", 0.0)
    ctx["leaf"] = lf


# ------------------------------------------------------------------------------------------------ Grandpa's house (a real room)
def build_grandpa(kit, ctx):
    """Butter house on stone piers at (-14, -6). Floor top z = 0.9. Front wall faces +x at x=-11; window at y=-6."""
    FL = 0.9
    x0, y0 = -14.0, -6.0
    G = E(None, (0, 0, 0), "grandpa")
    stone = [P("#9c978c", 0.9, 0.05), P("#8a857b", 0.9, 0.05), P("#aaa59a", 0.9, 0.05)]
    # stone piers: stacked blocks (offset so they read as stacked), gaps between
    for i, (px, py) in enumerate(((-16.6, -9.0), (-16.6, -6.0), (-16.6, -3.0), (-14.0, -9.0), (-14.0, -3.0), (-11.4, -9.0),
                                  (-11.4, -6.0), (-11.4, -3.0), (-14.0, -6.0))):
        for c in range(2):
            B(G, (0.62, 0.62, 0.43), (px + 0.03 * ((i + c) % 3 - 1), py + 0.03 * ((i * 2 + c) % 3 - 1), 0.21 + c * 0.44),
              stone[(i + c) % 3], "pier", 0.03)
    B(G, (6.2, 7.2, 0.18), (x0, y0, FL - 0.09), P("#8a5a34", 0.7, 0.05), "floor", 0.01)
    wall = P("#ffe27a", 0.7, 0.1)
    h = 2.9
    cz = FL + h / 2
    B(G, (0.2, 7.2, h), (-17.0, y0, cz), wall, "wallB", 0.03)                  # back
    for sy in (-1, 1):
        B(G, (6.2, 0.2, h), (x0, y0 + sy * 3.5, cz), wall, "wallS", 0.03)       # sides
    # front wall at x=-11 with a window hole at y -7.2..-4.8, z FL+0.9..FL+2.2 and a door at y -3.6..-2.7
    B(G, (0.2, 2.3, h), (-11.0, -8.35, cz), wall, "wallF", 0.03)               # y -9.5..-7.2
    B(G, (0.2, 1.2, h), (-11.0, -4.2, cz), wall, "wallF", 0.03)                # y -4.8..-3.6
    B(G, (0.2, 2.4, 0.9), (-11.0, -6.0, FL + 0.45), wall, "wallF", 0.03)       # under the window
    B(G, (0.2, 2.4, 0.7), (-11.0, -6.0, FL + h - 0.35), wall, "wallF", 0.03)   # over the window
    B(G, (0.2, 0.9, h - 2.1), (-11.0, -3.15, FL + 2.1 + (h - 2.1) / 2), wall, "wallF", 0.03)   # over the door
    B(G, (0.2, 0.2, h), (-11.0, -2.6, cz), wall, "wallF", 0.03)                # y -2.7..-2.5
    B(G, (0.1, 2.6, 0.08), (-10.92, -6.0, FL + 0.9), P("#fffaf0", 0.5, 0.2), "sill", 0.01)
    B(G, (0.1, 2.6, 0.08), (-10.92, -6.0, FL + 2.2), P("#fffaf0", 0.5, 0.2), "head", 0.01)
    for sy in (-1, 1):
        B(G, (0.1, 0.1, 1.4), (-10.92, -6.0 + sy * 1.25, FL + 1.55), P("#fffaf0", 0.5, 0.2), "jamb", 0.01)
    B(G, (6.2, 7.2, 0.18), (x0, y0, FL + h + 0.09), P("#f4ecd6", 0.8, 0.05), "ceil", 0.01)
    # roof
    rs = P("#4a8a7a", 0.7, 0.1)
    ang = math.radians(24)
    for s in (-1, 1):
        B(G, (3.7, 7.8, 0.22), (x0 + s * 1.5, y0, FL + h + 0.65), rs, "roof", 0.04, rot=(0, s * ang, 0))
    # porch outside the front: a deck at z=FL, two chairs, steps
    B(G, (2.6, 5.6, 0.16), (-9.7, -5.4, FL - 0.08), P("#efe6d4", 0.7, 0.1), "porch", 0.02)
    B(G, (0.4, 1.4, 0.3), (-8.25, -5.4, 0.15), P("#e3d9c4", 0.7, 0.1), "pstep", 0.02)
    B(G, (0.4, 1.4, 0.3), (-8.55, -5.4, 0.45), P("#e3d9c4", 0.7, 0.1), "pstep", 0.02)
    for cy in (-7.4, -4.4):
        ch = E(G, (-9.9, cy, FL), "pchair")
        B(ch, (0.6, 0.6, 0.08), (0, 0, 0.45), P("#2f9a56", 0.6, 0.1), "seat", 0.02)
        B(ch, (0.08, 0.6, 0.55), (-0.26, 0, 0.78), P("#2f9a56", 0.6, 0.1), "back", 0.02)
        for sx in (-1, 1):
            for sy in (-1, 1):
                B(ch, (0.06, 0.06, 0.45), (sx * 0.25, sy * 0.25, 0.22), P("#f4f0e6", 0.6, 0.1), "leg", 0.0)
    # the room inside: counter along the back with a stove and kettle, a little round table with two chairs
    B(G, (0.7, 3.4, 0.9), (-16.55, -6.0, FL + 0.45), P("#f4f0e6", 0.6, 0.1), "counter", 0.03)
    B(G, (0.72, 3.4, 0.06), (-16.55, -6.0, FL + 0.93), P("#8a6a46", 0.6, 0.1), "ctop", 0.01)
    B(G, (0.62, 0.8, 0.06), (-16.5, -6.6, FL + 0.97), P("#2a2a30", 0.5, 0.3), "stove", 0.01)
    k = E(G, (-16.5, -6.6, FL + 1.0), "kettle")
    B(k, (0.34, 0.34, 0.26), (0, 0, 0.13), P("#e8b44a", 0.25, 0.8), "kbody", 0.05)
    CY(k, 0.05, 0.1, (0, -0.19, 0.2), P("#e8b44a", 0.25, 0.8), "kspout", rot=(math.pi / 2, 0, 0))
    B(k, (0.28, 0.04, 0.04), (0, 0, 0.31), P("#403020", 0.5, 0.2), "khandle", 0.01)
    ctx["kettle"] = (-16.5, -6.6, FL + 1.35)
    tb = E(G, (-14.6, -5.0, FL), "table")
    CY(tb, 0.55, 0.06, (0, 0, 0.74), P("#8a5a34", 0.55, 0.1), "ttop")
    CY(tb, 0.07, 0.72, (0, 0, 0.37), P("#6b4426", 0.6, 0.1), "tleg")
    for cyy in (-0.95, 0.95):
        ch = E(G, (-14.6, -5.0 + cyy, FL), "kchair")
        B(ch, (0.45, 0.45, 0.06), (0, 0, 0.45), P("#2f9a56", 0.6, 0.1), "seat", 0.02)
        B(ch, (0.45, 0.06, 0.45), (0, 0.2 * (1 if cyy < 0 else -1) * -1, 0.72), P("#2f9a56", 0.6, 0.1), "back", 0.02)
    # a cupboard with plain doors on the side wall
    B(G, (0.5, 1.6, 1.0), (-16.6, -3.0 - 0.2, FL + 1.9), P("#d8e8d0", 0.6, 0.1), "cupboard", 0.03)
    # lights inside
    ctx["gl_ceil"] = kit.light("gceil", "POINT", (-14.0, -6.0, FL + 2.6), 380, "#ffe9c4", size=0.5)
    ctx["gl_win"] = kit.light("gwin", "AREA", (-11.3, -6.0, FL + 1.6), 180, "#ffe6b8", size=1.4, shadow=False)
    ctx["gl_win"].data.size, ctx["gl_win"].data.size_y = 2.0, 1.2
    ctx["gl_win"].rotation_euler = (0, math.radians(-90), 0)
    ctx["gfloor"] = FL


# ------------------------------------------------------------------------------------------------ our house + stairwell
def build_house_set(kit, ctx):
    """Our kitchen and dining room (x 86..100), the basement door in the wall x=100 and the stairwell beyond."""
    wood, wall = P("#8a5a34", 0.65, 0.1), P("#fbf0dc", 0.8, 0.05)
    B(None, (14.4, 8.4, 0.3), (SX - 7.0, 0, -0.15), P("#b07a48", 0.6, 0.12), "kfloor", 0.01)
    B(None, (0.3, 8.4, 3.0), (SX - 14.1, 0, 1.5), wall, "kback", 0.01)
    for sy in (-1, 1):
        B(None, (14.4, 0.3, 3.0), (SX - 7.0, sy * 4.2, 1.5), wall, "kside", 0.01)
    B(None, (14.4, 8.4, 0.3), (SX - 7.0, 0, 3.15), P("#f6efe0", 0.8, 0.05), "kceil", 0.01)
    # front wall (x = SX) with the door opening y -0.5..0.5 and 2.1 high
    B(None, (0.3, 3.75, 3.0), (SX, -2.375, 1.5), wall, "kfront", 0.01)
    B(None, (0.3, 3.75, 3.0), (SX, 2.375, 1.5), wall, "kfront", 0.01)
    B(None, (0.3, 1.0, 0.9), (SX, 0, 2.55), wall, "klintel", 0.01)
    fr = P("#fffaf0", 0.5, 0.2)
    B(None, (0.12, 0.08, 2.2), (SX - 0.15, -0.54, 1.1), fr, "frame", 0.01)
    B(None, (0.12, 0.08, 2.2), (SX - 0.15, 0.54, 1.1), fr, "frame", 0.01)
    B(None, (0.12, 1.16, 0.08), (SX - 0.15, 0, 2.14), fr, "frame", 0.01)
    # two amber strokes scratched into the frame at shoulder height (the lore tally), a hair proud
    amber = kit.emit("#ffb347", 2.2, name="tally")
    for yy in (0.515, 0.565):
        B(None, (0.02, 0.03, 0.34), (SX - 0.228, yy, 1.45), amber, "tally", 0.0)
    # the door leaf, hinged at y=-0.5, opening into the room (toward -x)
    hinge = E(None, (SX - 0.05, -0.5, 0), "doorhinge")
    B(hinge, (0.07, 1.0, 2.1), (0, 0.5, 1.05), P("#c8a46e", 0.55, 0.15), "door", 0.02)
    B(hinge, (0.05, 0.8, 0.5), (-0.04, 0.5, 1.5), P("#b88a52", 0.55, 0.15), "panel", 0.01)
    B(hinge, (0.05, 0.8, 0.5), (-0.04, 0.5, 0.6), P("#b88a52", 0.55, 0.15), "panel", 0.01)
    kn = kit.sphere(nm("knob"), 0.06, (-0.09, 0.9, 1.05), P("#f0b84a", 0.25, 0.9), hinge, seg=12)
    ctx["doorhinge"] = hinge
    # furniture: a round table with three chairs, a couch, a lamp
    tb = E(None, (SX - 7.0, 0.0, 0), "dtable")
    CY(tb, 0.95, 0.07, (0, 0, 0.76), P("#9b6a3a", 0.5, 0.15), "ttop", n=32)
    CY(tb, 0.12, 0.74, (0, 0, 0.37), P("#6b4426", 0.6, 0.1), "tleg")
    CY(tb, 0.45, 0.04, (0, 0, 0.02), P("#6b4426", 0.6, 0.1), "tfoot")
    for i, a in enumerate((200, 90, 320)):
        ch = E(None, (SX - 7.0 + 1.35 * math.cos(math.radians(a)), 1.35 * math.sin(math.radians(a)), 0), "dchair")
        ch.rotation_euler = (0, 0, math.radians(a))
        B(ch, (0.5, 0.5, 0.07), (0, 0, 0.46), P("#3f78c8", 0.55, 0.15), "seat", 0.02)
        B(ch, (0.07, 0.5, 0.5), (0.22, 0, 0.74), P("#3f78c8", 0.55, 0.15), "back", 0.02)
        for sx in (-1, 1):
            for sy in (-1, 1):
                B(ch, (0.05, 0.05, 0.46), (sx * 0.2, sy * 0.2, 0.23), P("#f4f0e6", 0.6, 0.1), "leg", 0.0)
    cu = E(None, (SX - 12.2, 2.8, 0), "couch")
    B(cu, (1.1, 2.4, 0.45), (0, 0, 0.3), P("#d85a4a", 0.7, 0.05), "cseat", 0.08)
    B(cu, (0.3, 2.4, 0.5), (0.55, 0, 0.7), P("#c84a3a", 0.7, 0.05), "cback", 0.08)
    for sy in (-1, 1):
        B(cu, (1.1, 0.22, 0.28), (0, sy * 1.2, 0.52), P("#c84a3a", 0.7, 0.05), "carm", 0.06)
    # a window on the side wall and a rug
    B(None, (0.1, 1.5, 1.2), (SX - 9.0, -4.03, 1.8), kit.emit("#bfe4ff", 1.6, name="kwin"), "kwin", 0.0)
    B(None, (0.08, 1.7, 1.4), (SX - 9.0, -4.04, 1.8), fr, "kwinframe", 0.01)
    B(None, (3.2, 2.4, 0.02), (SX - 7.0, 0.0, 0.01), P("#e8b44a", 0.9, 0.0), "rug", 0.0)
    for i in range(0, 14):
        B(None, (14.2, 0.03, 0.01), (SX - 7.0, -4.0 + i * 0.6, 0.006), P("#8a5a34", 0.7, 0.05), "board", 0.0)
    for (px, py) in ((SX - 7.0 - 0.55, -0.15), (SX - 7.0 + 0.1, 0.55), (SX - 7.0 + 0.25, -0.5), (SX - 7.0 - 0.3, 0.5)):
        CY(None, 0.2, 0.025, (px, py, 0.8), P("#ffffff", 0.35, 0.3), "plate", n=20)
    ctx["kl_ceil"] = kit.light("kceil", "POINT", (SX - 7.0, 0, 2.8), 420, "#ffe9c4", size=0.5)
    ctx["kl_win"] = kit.light("kwinl", "AREA", (SX - 9.0, -3.7, 1.8), 200, "#d8ecff", size=1.2, shadow=False)
    ctx["kl_win"].rotation_euler = (math.radians(-90), 0, 0)
    # ---- the stairwell: width 1.5 (y -0.75..0.75); steps are hidden past the count
    ctx["steps"] = []
    wsteps, ssteps = P("#9a6a3c", 0.7, 0.1), P("#8d8378", 0.85, 0.05)
    newm = P("#6a4426", 0.7, 0.1)
    for k in range(1, MAXSTEPS + 1):
        m = wsteps if k <= 26 else ssteps
        s = B(None, (RUN, 1.5, 0.3), (SX + RUN * (k - 0.5), 0, -RISE * k - 0.15), m, "step", 0.012)
        s["k"] = k
        ctx["steps"].append((s, m, newm if k <= 26 else m))
    # side walls and a slanted ceiling follow the stairs: long slabs
    L = RUN * MAXSTEPS + 2.0
    ang = math.atan2(RISE, RUN)
    wm = P("#cdbba0", 0.85, 0.03)
    tilt = -ang
    ctx["stairwalls"] = []
    for sy in (-1, 1):
        # a wall slab along the stair line: tall enough to cover the steps' profile
        slab = B(None, (L / math.cos(ang), 0.2, 6.0), (SX + L / 2 - 1.0, sy * 0.85, 0), wm, "swall", 0.0)
        slab.rotation_euler = (0, -tilt * -1 * 1.0 * -1 if False else ang, 0)
        ctx["stairwalls"].append(slab)
    ceil = B(None, (L / math.cos(ang), 1.9, 0.2), (SX + L / 2 - 1.0, 0, 0), P("#bfa98a", 0.85, 0.03), "sceil", 0.0)
    ceil.rotation_euler = (0, ang, 0)
    ctx["stairceil"] = ceil
    # a landing group that rides the bottom of the stairs: the floor, the crack, the cavern and the Under
    land = E(None, (SX, 0, 0), "land")
    ctx["land"] = land
    stone = P("#8d8378", 0.85, 0.05)
    dark = P("#2a2018", 0.95, 0.0)
    # landing floor: front piece (x 0..0.9), back piece (x 2.0..4.0), the slot x 0.9..2.0 over the full cavern width
    ctx["landvis"] = [B(land, (0.9, 1.5, 0.4), (0.45, 0, -0.2), stone, "landA", 0.01),
                      B(land, (3.0, 1.5, 0.4), (3.5, 0, -0.2), stone, "landB", 0.01)]
    # cavern ceiling beyond the stairwell walls
    ctx["landC"] = []
    for sy in (-1, 1):
        ctx["landC"].append(B(land, (14.0, 12.25, 0.4), (2.4, sy * 6.875, -0.2), stone, "landC", 0.01))
    B(land, (1.2, 10.0, 0.4), (-0.6, 0, -0.2), stone, "landD", 0.01) if False else None
    # the landing is a small room: a flat ceiling and plain walls round it
    lw = P("#d8c6a6", 0.85, 0.03)
    B(land, (5.9, 10.0, 0.2), (2.65, 0, 2.3), P("#cdb894", 0.85, 0.03), "landceil", 0.0)
    for sy in (-1, 1):
        ctx["landvis"].append(B(land, (5.9, 0.2, 2.4), (2.65, sy * 5.0, 1.1), lw, "landwall", 0.0))
        ctx["landvis"].append(B(land, (0.2, 4.15, 2.4), (-0.3, sy * 2.925, 1.1), lw, "landwall", 0.0))
    ctx["landvis"].append(B(land, (0.2, 10.0, 2.4), (5.6, 0, 1.1), lw, "landwall", 0.0))
    # cavern walls and floor (dark clay)
    CD, CW = 14.0, 26.0
    B(land, (CD, CW, 0.4), (2.4, 0, -6.9), dark, "cfloor", 0.0)
    for sy in (-1, 1):
        B(land, (CD, 0.4, 6.8), (2.4, sy * (CW / 2), -3.5), dark, "cwall", 0.0)
    B(land, (0.4, CW, 6.8), (-4.8, 0, -3.5), dark, "cwall", 0.0)
    B(land, (0.4, CW, 6.8), (9.6, 0, -3.5), dark, "cwall", 0.0)
    # the crack's broken edge: black ragged teeth under the landing and two cross-beams, so the face is seen through a gap
    oldc = E(land, (0, 0, 0), "oldcrack")
    ctx["oldcrack"] = oldc
    blk = P("#020202", 0.95, 0.0)
    # a scorched black border round the hole on the landing floor, and black liners down its four sides
    B(oldc, (2.4, 0.9, 0.04), (1.45, -1.2, 0.03), blk, "crackrim", 0.0)
    B(oldc, (2.4, 0.9, 0.04), (1.45, 1.2, 0.03), blk, "crackrim", 0.0)
    B(oldc, (0.7, 1.5, 0.04), (0.55, 0, 0.03), blk, "crackrim", 0.0)
    B(oldc, (0.7, 1.5, 0.04), (2.35, 0, 0.03), blk, "crackrim", 0.0)
    for lx_, ly_, lw_, lh_ in ((0.89, 0, 0.04, 1.5), (2.01, 0, 0.04, 1.5), (1.45, -0.74, 1.1, 0.04), (1.45, 0.74, 1.1, 0.04)):
        B(oldc, (lw_, lh_, 0.6), (lx_, ly_, -0.2), blk, "crackliner", 0.0)
    for i, (ty, tw, tl_, side) in enumerate(((-0.6, 0.3, 0.1, -1), (-0.25, 0.25, 0.07, 1), (0.1, 0.3, 0.09, -1), (0.45, 0.25, 0.1, 1),
                                             (0.65, 0.2, 0.07, -1))):
        cx = 0.9 + 0.5 * tl_ if side < 0 else 2.0 - 0.5 * tl_
        B(oldc, (tl_, tw, 0.5), (cx, ty, -0.6 + 0.07 * (i % 3)), blk, "crackteeth", 0.04, rot=(0, 0, 0.12 * (i % 3 - 1)))
    # the face-through-the-crack shots (rake): a thin lamp-lit ragged edge of broken stone round the view
    rock = kit.emit("#d9a860", 0.8, name="crackstone")
    cfg = E(land, (0, 0, 0), "crackframe")
    CX_, CYY, OX, OY = 1.45, -0.3, 0.52, 0.95
    for i, (bx, by, bw, bh, bz) in enumerate((
            (-1, 0, 0.3, 3.6, -0.07), (1, 0, 0.3, 3.6, -0.08),
            (0, -1, 1.8, 0.3, -0.09), (0, 1, 1.8, 0.3, -0.06))):
        B(cfg, (bw, bh, 0.2), (CX_ + bx * (OX + bw / 2 - (0.0 if bx else 0)), CYY + by * (OY + bh / 2), bz), rock, "crackedge", 0.03)
    for i, (px, py, pw, ph) in enumerate(((-1, -0.45, 0.16, 0.3), (1, -0.2, 0.14, 0.26), (-1, 0.25, 0.13, 0.3), (1, 0.4, 0.15, 0.22),
                                          (-1, -0.05, 0.1, 0.18), (1, 0.1, 0.1, 0.2))):
        B(cfg, (pw, ph, 0.2), (CX_ + px * (OX - pw / 2 + 0.01), CYY + py, -0.04 - 0.01 * i), rock, "crackjag", 0.02, rot=(0, 0, 0.3 * px))
    for i, (py, pw, ph, sx) in enumerate(((-1, 0.3, 0.14, -0.2), (1, 0.26, 0.13, 0.15), (-1, 0.2, 0.12, 0.2), (1, 0.18, 0.1, -0.22))):
        B(cfg, (pw, ph, 0.2), (CX_ + sx, CYY + py * (OY - ph / 2 + 0.01), -0.05 - 0.01 * i), rock, "crackjag", 0.02)
    hide(cfg, True)
    ctx["crackframe"] = cfg
    # the Under lies on the cavern floor, face up, mouth end toward the stairs; the slot is above its middle
    ctx["under"] = make_under(kit, land, 1.0)
    ctx["under"]["root"].location = (1.45, -1.25, -6.7 + 0.9)
    ctx["under"]["root"].rotation_euler = (0, 0, 0)
    # the pipe from the cavern ceiling down to the mouth is inside make_under; a brass sleeve in the ceiling
    # lights: the lamp (cue "lamp") and the Under's key and rim
    ctx["lamp_ob"] = E(None, (SX + 1.0, 0, 0.8), "lamp")
    B(ctx["lamp_ob"], (0.1, 0.1, 0.15), (0, 0, 0.0), P("#6a4a2a", 0.5, 0.3), "lbody", 0.02)
    B(ctx["lamp_ob"], (0.075, 0.075, 0.09), (0, 0, 0.01), kit.emit("#ffcf80", 3.0, name="lampglow"), "lglow", 0.015)
    CY(ctx["lamp_ob"], 0.03, 0.02, (0, 0, 0.11), P("#6a4a2a", 0.5, 0.3), "lcap")
    ctx["lamp_light"] = kit.light("lamp", "POINT", (SX + 1.0, 0, 0.8), 150, "#ffb347", size=0.15)
    ctx["lamp_light2"] = kit.light("stairl", "POINT", (SX + 0.3, 0, 1.6), 90, "#ffd9a8", size=0.3)
    ctx["landl"] = kit.light("landl", "POINT", (SX, 0, 0), 160, "#ffcf90", size=0.3)
    ctx["ukey"] = kit.light("ukey", "SPOT", (SX, 0, 0), 700, "#ff9a50", size=0.5, spot=70, blend=0.6)
    ctx["urim"] = kit.light("urim", "SPOT", (SX, 0, 0), 1300, "#8ab8ff", size=0.5, spot=90, blend=0.7)
    ctx["urim2"] = kit.light("urim2", "SPOT", (SX, 0, 0), 3800, "#9cc4ff", size=0.5, spot=100, blend=0.7)
    ctx["ufill"] = kit.light("ufill", "POINT", (SX, 0, 0), 45, "#ffcf9a", size=1.0, shadow=False)
    # dust motes in the stairwell: a few pale specks
    ctx["motes"] = []
    mm = kit.emit("#ffd890", 3.0, name="mote")
    for i in range(14):
        o = kit.sphere(nm("mote"), 0.012, (0, 0, 0), mm, None, seg=6)
        no_shadow(o)
        ctx["motes"].append(o)


# ------------------------------------------------------------------------------------------------ bakery stage
def build_bakery(kit, ctx):
    ox = -200.0
    B(None, (8, 6, 0.3), (ox, 0, -0.15), P("#d8b88a", 0.7, 0.1), "bfloor", 0.01)
    B(None, (8, 0.3, 3.2), (ox, 3.0, 1.6), P("#fff0d0", 0.8, 0.05), "bback", 0.01)
    for sx in (-1, 1):
        B(None, (0.3, 6, 3.2), (ox + sx * 4.0, 0, 1.6), P("#ffe0b0", 0.8, 0.05), "bside", 0.01)
    B(None, (8, 6, 0.3), (ox, 0, 3.35), P("#f6efe0", 0.8, 0.05), "bceil", 0.01)
    # a big brick oven with an open door and a loaf inside
    ov = E(None, (ox, 2.3, 0), "oven")
    B(ov, (2.6, 1.2, 1.6), (0, 0, 0.8), P("#c8553a", 0.8, 0.05), "ovbody", 0.05)
    B(ov, (1.5, 0.1, 0.9), (0, -0.62, 0.8), P("#1a120c", 0.9, 0.0), "ovmouth", 0.02)
    B(ov, (0.6, 0.12, 0.25), (0, -0.66, 0.5), P("#d89a4a", 0.6, 0.05), "loaf", 0.08)
    B(ov, (1.6, 0.14, 0.14), (0, -0.7, 1.28), P("#3a3a42", 0.4, 0.5), "ovrail", 0.02)
    ctx["oven_glow"] = kit.light("ovenglow", "POINT", (ox, 1.6, 0.9), 200, "#ff9a4a", size=0.3)
    B(None, (3.2, 0.9, 1.0), (ox - 2.4, 0.2, 0.5), P("#f4f0e6", 0.6, 0.1), "bcounter", 0.03)
    for i in range(4):
        B(None, (0.5, 0.3, 0.22), (ox - 3.1 + i * 0.6, 0.2, 1.11), P("#d89a4a", 0.6, 0.05), "bread", 0.08)
    B(None, (1.2, 0.1, 1.0), (ox + 2.8, 2.8, 1.7), kit.emit("#bfe4ff", 1.6, name="bwin"), "bwin", 0.0)
    ctx["bl_ceil"] = kit.light("bceil", "POINT", (ox, 0, 2.8), 380, "#ffe9c4", size=0.5)


# ------------------------------------------------------------------------------------------------ the cutaway diagram
def build_cutaway(kit, ctx):
    """The street cut like a cake, seen from -y: houses on a green top, brown earth below, stairs as lit zigzags going
    down toward the middle, the pipe from the pole straight down, the Under at the bottom."""
    oy = 200.0
    G = E(None, (0, oy, 0), "cut")
    B(G, (60, 0.6, 0.5), (0, 0, -0.25), P("#58c84a", 0.8, 0.05), "ctop", 0.0)
    layers = ((-0.5, -6.0, "#9a6a3c"), (-6.0, -14.0, "#7a5230"), (-14.0, -22.0, "#563820"), (-22.0, -30.0, "#3a2618"))
    for z0, z1, c in layers:
        B(G, (60, 0.6, z0 - z1), (0, 0, (z0 + z1) / 2), P(c, 0.9, 0.0), "cearth", 0.0)
    B(G, (120, 0.5, 80), (0, 0.0, -70), P("#241810", 0.95, 0.0), "cdeep", 0.0)
    B(G, (200, 0.5, 60), (0, 0.0, 30), kit.emit("#9fd8ff", 1.0, name="csky2"), "csky2", 0.0)
    # sky behind
    B(G, (120, 0.2, 40), (0, 4.0, 12), kit.emit("#9fd8ff", 1.0, name="csky"), "csky", 0.0)
    # houses on top
    ctx["cut_stairs"] = []
    hs = ((-22, "#f7f5ee"), (-14, "#ffe27a"), (-7, "#a9dcff"), (7, "#ffd0e0"), (14, "#f7f5ee"), (22, "#c8f0d8"))
    for hx, hc in hs:
        B(G, (5.0, 0.7, 3.0), (hx, -0.1, 1.5), P(hc, 0.7, 0.1), "chouse", 0.04)
        B(G, (5.8, 0.8, 0.3), (hx, -0.1, 3.2), P("#c8523c", 0.7, 0.1), "croof", 0.04)
        B(G, (0.8, 0.1, 1.1), (hx + 1.2, -0.52, 0.8), P("#fffaf0", 0.5, 0.2), "cdoor", 0.01)
    # the Dunns-like stair zigzags: each house's stairs go down toward the middle; Grandpa's (x=-14) stands on blocks
    for hx, hc in hs:
        if hx == -14:
            for bx in (-16, -14, -12):
                B(G, (0.6, 0.7, 0.5), (bx, -0.1, 0.25), P("#9c978c", 0.9, 0.05), "cblock", 0.03)
            continue
        sgn = -1 if hx > 0 else 1
        steps = []
        n = 22
        for k in range(n):
            s = B(G, (0.75, 0.6, 0.55), (hx + sgn * (0.3 + 0.42 * k) * 0.0 + sgn * -0.0 - 0.0 + (-sgn) * 0.0 + (sgn * -1) * 0.0 + (-sgn) * (0.42 * k) * 0.0, -0.45, -0.3 - 0.34 * k),
                  kit.emit("#ffd890", 0.9, name="cstep"), "cstep", 0.0)
            s.location = (hx + sgn * 0.5 * k, -0.5, -0.3 - 0.5 * k)
            steps.append(s)
        ctx["cut_stairs"].append(steps)
    # the pole, the whistle and the long pipe straight down to the Under's mouth
    CY(G, 0.14, 6.0, (0, -0.3, 3.0), P("#2f9a56", 0.4, 0.4), "cpole")
    CY(G, 0.4, 0.9, (0, -0.3, 6.4), P("#f0b84a", 0.28, 0.8), "cwhistle")
    CY(G, 0.16, 25.0, (0, -0.45, -12.0), kit.emit("#b08040", 0.7, name="cpipe"), "cpipe")
    ctx["cut_shaft"] = B(G, (2.6, 0.3, 26.0), (0, -0.55, -40.0), kit.emit("#050403", 1.0, name="cshaft"), "cshaft", 0.0)
    ctx["cut_under"] = make_under(kit, G, 1.0, pipe_h=0, body=False, dark=True)
    u = ctx["cut_under"]["root"]
    u.location = (0, -0.8, -27.0)
    u.rotation_euler = (math.pi / 2, 0, 0)           # stood up toward the camera: its face looks -y
    u.scale = (2.4, 2.4, 2.4)
    # the sound running down the pipe: a travelling glow
    ctx["cut_pulse"] = CY(G, 0.3, 0.8, (0, -0.55, 0), kit.emit("#ffffff", 4.0, name="cpulse"), "cpulse")
    ctx["cut_light"] = kit.light("cutl", "AREA", (0, oy - 30, 8), 1600, "#ffffff", size=40, shadow=False)
    ctx["cut_light"].data.size, ctx["cut_light"].data.size_y = 60, 36
    kit.aim(ctx["cut_light"], (0, oy, -2))
    ctx["cut_light_low"] = kit.light("cutlow", "AREA", (0, oy - 24, -22), 2500, "#ffd8a0", size=30, shadow=False)
    ctx["cut_light_low"].data.size, ctx["cut_light_low"].data.size_y = 40, 20
    kit.aim(ctx["cut_light_low"], (0, oy, -22))


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    K.kit = kit
    ctx = {"story": story}
    ctx["shots"] = {s["id"]: s for s in story["shots"]}
    sc = bpy.context.scene
    # sky gradient on the world (the camera sees it)
    w = sc.world
    nt = w.node_tree
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
    ramp.color_ramp.elements.new(0.3)
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    ctx["ramp"], ctx["bg"] = ramp, bg
    ctx["sun"] = kit.light("sun", "SUN", (0, 0, 50), 5.0, "#fff4de", size=0.1)
    ctx["sun"].data.angle = 0.05
    ctx["fill"] = kit.light("camfill", "POINT", (0, 0, 2), 60, "#fff0dc", size=0.6, shadow=False)
    build_street(kit, ctx)
    build_grandpa(kit, ctx)
    build_house_set(kit, ctx)
    build_bakery(kit, ctx)
    build_cutaway(kit, ctx)
    # dust puffs: pools of soft pale spheres
    pm = kit._new(nm("puff"))
    n_ = pm.node_tree
    n_.nodes.remove(n_.nodes["Principled BSDF"])
    tr = n_.nodes.new("ShaderNodeBsdfTransparent")
    em = n_.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.86, 0.78, 0.6, 1)
    em.inputs["Strength"].default_value = 1.1
    mx = n_.nodes.new("ShaderNodeMixShader")
    mx.inputs["Fac"].default_value = 0.3
    n_.links.new(tr.outputs[0], mx.inputs[1])
    n_.links.new(em.outputs[0], mx.inputs[2])
    out = next(n for n in n_.nodes if n.type == "OUTPUT_MATERIAL")
    n_.links.new(mx.outputs[0], out.inputs["Surface"])
    ctx["puffmat"] = pm
    ctx["pools"] = {}

    def pool(key, n, r):
        lst = []
        for j in range(n):
            o = kit.sphere(nm("puff"), r, (0, 0, -50), pm, None, seg=12)
            no_shadow(o)
            o.hide_render = True
            lst.append(o)
        ctx["pools"][key] = lst
    pool("whistle", 12, 0.13)
    pool("collar", 8, 0.07)
    for i in range(len(ctx["wells"])):
        pool(f"well{i}", 6, 0.2)
    pool("shoulder", 10, 0.03)
    ctx["steam"] = [kit.sphere(nm("steam"), 0.06, (0, 0, -50), pm, None, seg=10) for _ in range(8)]
    for o in ctx["steam"]:
        no_shadow(o)
        o.hide_render = True
    ctx["late"] = False
    build_tag(kit, ctx)
    return ctx


# ------------------------------------------------------------------------------------------------ animate
def puff_pool(ctx, key, t, site, direction, amp, reach=1.4, spread=0.25, rate=0.9, up=(0, 0, 1)):
    lst = ctx["pools"][key]
    if amp == 0:
        for o in lst:
            o.hide_render = True
        return
    for j, o in enumerate(lst):
        ph = (t * rate + j / len(lst)) % 1.0
        env = math.sin(math.pi * ph) ** 0.8 * abs(amp)
        o.hide_render = env < 0.02
        u = ph if amp > 0 else 1.0 - ph
        jx, jy = math.sin(j * 2.3 + 0.4), math.cos(j * 1.7)
        o.location = (site[0] + spread * jx * (0.4 + u) + up[0] * reach * u,
                      site[1] + spread * jy * (0.4 + u) + up[1] * reach * u,
                      site[2] + up[2] * reach * u)
        s = (0.6 + 1.4 * (ph if amp > 0 else 1 - ph)) * env + 0.001
        o.scale = (s, s, s)


def animate(kit, story, tl, t, ctx):
    if not ctx["late"]:
        late_extras(kit, ctx)
        ctx["late"] = True
    sc = bpy.context.scene
    L, cur = look_at(ctx, tl, t)
    sd = ctx["shots"][cur["id"]]
    r = ctx["ramp"].color_ramp.elements
    for el, c in zip(r, L["sky"]):
        rgb = c
        el.color = (kit.srgb(rgb[0]), kit.srgb(rgb[1]), kit.srgb(rgb[2]), 1.0)
    ctx["bg"].inputs["Strength"].default_value = L["world"]
    az, el_, en, scol = L["sun"]
    azr, elr = math.radians(az), math.radians(el_)
    pos = V((math.sin(azr) * math.cos(elr), -math.cos(azr) * math.cos(elr), math.sin(elr)))
    sun = ctx["sun"]
    sun.rotation_euler = (-pos).to_track_quat("-Z", "Y").to_euler()
    sun.data.color = (kit.srgb(scol[0]), kit.srgb(scol[1]), kit.srgb(scol[2]))
    from blocky import bl_story
    cl, ct, cl_lens, _ = bl_story.cam_at(sd, cur, t, {}, tl)
    cam = kit.OBJ["cam"]
    # the camera's own fill sits just behind it, so each subject is lit toward the lens
    ctx["fill"].location = (cl[0], cl[1], cl[2])
    sc.view_settings.exposure = L["exp"] + sd.get("exp", 0.0)
    dof = sd.get("dof")
    cd = cam.data
    if dof:
        cd.dof.use_dof = True
        cd.dof.focus_distance = dof[0]
        cd.dof.aperture_fstop = dof[1]
    else:
        cd.dof.use_dof = False
    # ---- the stairwell: steps shown, the landing riding the bottom
    sc_ = cue_at(tl, "steps", t)
    n = int(sc_.get("n", 26))
    newest = sc_.get("new", 0)
    for s, m, nm_ in ctx["steps"]:
        k = s["k"]
        s.hide_render = k > n
        if k == newest and k <= n:
            s.data.materials[0] = nm_
        else:
            s.data.materials[0] = m
    Lx, Lz = RUN * n, -RISE * n
    ctx["land"].location = (SX + Lx, 0, Lz)
    # stair walls / ceiling follow the count: they end 0.3 m past the last step, where the landing room begins
    ang = math.atan2(RISE, RUN)
    base_x = RUN * MAXSTEPS + 2.0
    lenx = RUN * n + 0.3
    mid = lenx / 2
    for slab in ctx["stairwalls"]:
        slab.scale = (lenx / base_x, 1, 1)
        slab.location = (SX + mid, slab.location[1], -RISE * mid / RUN + 1.0)
    c = ctx["stairceil"]
    c.scale = (lenx / base_x, 1, 1)
    c.location = (SX + mid, 0, -RISE * mid / RUN + 2.5)
    ctx["landl"].location = (SX + Lx + 2.0, 0.0, Lz + 1.7)
    # ---- the lamp
    lp = eased(tl, "lamp", t) or [SX + 1.0, 0.0, 0.8]
    ctx["lamp_ob"].location = tuple(lp)
    ctx["lamp_ob"].hide_render = cue_at(tl, "lamp", t).get("off", False)
    ctx["lamp_light"].location = (lp[0], lp[1], lp[2] + 0.3)
    ctx["lamp_light2"].location = (SX + 0.4, 0, 1.5)
    # ---- the Under
    uc = cue_at(tl, "under", t)
    show = bool(uc.get("on", False))
    u = ctx["under"]
    hide(u["root"], not show)
    # the face shots look straight down through the crack: turn the head so the crown is toward the top of frame
    rk = bool(sd.get("rake"))
    u["root"].rotation_euler = (0, 0, math.pi if rk else 0)
    u["root"].location = (1.45, -2.9 if rk else -1.25, -6.7 + 0.9)
    hide(ctx["crackframe"], not (rk and show))
    hide(ctx["oldcrack"], rk)
    for o in ctx["landC"] + ctx["landvis"] + list(ctx["stairwalls"]) + [ctx["stairceil"]]:
        o.hide_render = rk
    for o in u["body"]:
        o.hide_render = rk
    if u["pipe_root"] is not None:
        u["pipe_root"].scale = (1.2, 1.2, 1.0) if rk else (1, 1, 1)
        u["pipe_root"].rotation_euler = (0, -0.42, 0) if rk else (0, 0, 0)
    lit = uc.get("light", 0.0)
    base = ctx["land"].location
    uo = u["root"].location
    ux, uy, uz = base[0] + uo[0], base[1] + uo[1], base[2] + uo[2]
    ctx["ukey"].location = (base[0] + 0.3, base[1] - 0.3, base[2] - 1.3)
    kit.aim(ctx["ukey"], (ux, uy, uz))
    if sd.get("rake"):
        # the lamp above at one side, raking across the face; a cool rim on the far edge
        ctx["ukey"].location = (ux - 4.3, uy + 0.4, uz + 1.7)
        kit.aim(ctx["ukey"], (ux + 0.2, uy, uz))
        ctx["ukey"].data.spot_size = math.radians(60)
        ctx["ukey"].data.spot_blend = 0.8
        ctx["ukey"].data.color = (1.0, 0.72, 0.42)
    ctx["urim"].location = (ux + 7.0, uy - 3.2, uz + 2.6)
    kit.aim(ctx["urim"], (ux, uy - 3.5, uz))
    if sd.get("rake"):
        ctx["urim"].location = (ux + 6.0, uy + 1.2, uz + 1.2)
        kit.aim(ctx["urim"], (ux + 3.1, uy + 0.4, uz))
        ctx["urim"].data.spot_size = math.radians(22)
    ctx["urim2"].location = (ux - 1.5, uy + 6.5, uz + 3.2)
    kit.aim(ctx["urim2"], (ux, uy - 2.0, uz))
    ctx["ufill"].location = (base[0] + 1.45, base[1], base[2] - 2.2)
    # the Under's eyes: pupils look up at us, or (cue "gaze") turn away
    gaze = uc.get("gaze", 0.0)
    for d, pu, ex in u["eyes"]:
        pu.location = (ex + 0.0, EYY - 0.12 * gaze, 0.085)
        d.location = (ex + (0.05 if ex > 0 else -0.05) * gaze, EYY - 0.08 - 0.12 * gaze, 0.11)
    # ---- the door
    dc = cue_at(tl, "door", t)
    open_ = dc.get("open", 0.0)
    if "to" in dc:
        open_ = lerp(open_, dc["to"], ss((t - dc["t"]) / max(1e-3, dc.get("dur", 0.6))))
    ctx["doorhinge"].rotation_euler = (0, 0, math.radians(95 * open_))
    # ---- the tag
    tg = cue_at(tl, "tag", t).get("n", 26)
    place_tag(kit, ctx, int(tg), cl_lens, sd.get("tagbig", 1.0))
    # ---- dust: on shoulders, puffs at the whistle, the wells, the collar
    dc_ = cue_at(tl, "dust", t).get("who", [])
    for who, d in ctx["dust"].items():
        hide(d, who not in dc_)
    pc = cue_at(tl, "puff", t)
    pulse = 0.55 + 0.45 * math.sin(t * 6.0)
    wm = ctx["whistle_mouth"]
    puff_pool(ctx, "whistle", t, (wm[0], wm[1] - 0.1, wm[2]), 1, pc.get("whistle", 0) * (0.7 + 0.3 * pulse), reach=1.6,
              spread=0.2, rate=1.2, up=(0, -0.5, 0.6))
    cp = ctx["collar_pos"]
    puff_pool(ctx, "collar", t, cp, 1, pc.get("collar", 0), reach=0.9, spread=0.2, rate=1.0)
    for i, (wx, wy) in enumerate(ctx["wells"]):
        puff_pool(ctx, f"well{i}", t, (wx, wy, 0.2), 1, pc.get("wells", 0) * (0.7 + 0.3 * pulse), reach=1.0, spread=0.2,
                  rate=1.0)
    # the pools keep their sign for "in" via negative amp
    sp = pc.get("shoulder")
    puff_pool(ctx, "shoulder", t, tuple(sp) if sp else (0, 0, -50), 1, 1 if sp else 0, reach=0.5, spread=0.1, rate=0.8)
    # ---- kettle steam
    kc = cue_at(tl, "kettle", t)
    kp = ctx["kettle"]
    for j, o in enumerate(ctx["steam"]):
        if not kc.get("on"):
            o.hide_render = True
            continue
        ph = (t * 0.7 + j / 8.0) % 1.0
        env = math.sin(math.pi * ph) ** 0.9
        o.hide_render = False
        o.location = (kp[0] + 0.04 * math.sin(j * 2.0 + t), kp[1] - 0.2 + 0.03 * math.cos(j * 1.3 + t), kp[2] - 0.1 + 0.55 * ph)
        s = (0.4 + 1.2 * ph) * env + 0.001
        o.scale = (s, s, s)
    # ---- the cutaway: stairs reaching one step further, the pulse down the pipe, the Under's gaze
    cc = cue_at(tl, "cut", t)
    ext = cc.get("ext", 0)
    for steps in ctx["cut_stairs"]:
        for k, s in enumerate(steps):
            s.hide_render = k >= 12 + ext
    pu = cc.get("pulse")
    pulse_ob = ctx["cut_pulse"]
    if pu is not None:
        u_ = ss((t - cc["t"]) / max(1e-3, cc.get("dur", 1.5)))
        pulse_ob.location = (0, 200.0 - 0.55, lerp(6.0, -25.0, u_ if pu else 1 - u_))
        pulse_ob.hide_render = not (0.0 <= (t - cc["t"]) <= cc.get("dur", 1.5))
    else:
        pulse_ob.hide_render = True
    cg = cc.get("gaze", 0.0)
    for d, pu_, ex in ctx["cut_under"]["eyes"]:
        pu_.location = (ex, 0.7 - 0.12 * cg, 0.085)
        d.location = (ex + (0.05 if ex > 0 else -0.05), 0.62 - 0.12 * cg, 0.11)
    # ---- the ladder, the leaf, the cutaway's shaft
    hide(ctx["ladder"], not cue_at(tl, "ladder", t).get("on", False))
    lc = cue_at(tl, "leaf", t)
    lf = ctx["leaf"]
    if lc and lc.get("pos"):
        lf.location = (lc["pos"][0] + 0.1 * math.sin(t * 2.0), lc["pos"][1], 0.08 + 0.02 * abs(math.sin(t * 3.0)))
        lf.rotation_euler = (0.4 * math.sin(t * 3.0), 0.3 * math.cos(t * 2.0), t * 1.5)
    else:
        lf.location = (0, 0, -20)
    gone_ = cc.get("gone", False)
    hide(ctx["cut_under"]["root"], gone_)
    hide(ctx["cut_shaft"], not gone_)
    # ---- motes in the stairwell
    for i, o in enumerate(ctx["motes"]):
        o.hide_render = True
        continue
        o.location = (SX + RUN * min(n, 8) * (0.2 + 0.8 * ((i * 0.37) % 1.0)) + 0.1 * math.sin(t * 0.7 + i), 0.5 * math.sin(i * 1.9 + t * 0.3),
                      -RISE * RUN * 0 + (-RISE * min(n, 8) * (0.2 + 0.8 * ((i * 0.37) % 1.0))) + 1.0 + 0.2 * math.sin(t * 0.5 + i * 2))
        o.hide_render = False
    # ---- light gains per shot
    gk = sd.get("key", 1.0)
    inh = sd.get("inside", 1.0)
    return {"sun": en * sd.get("sun", 1.0) / 5.0, "camfill": sd.get("fill", 1.0),
            "gceil": inh, "gwin": inh, "kceil": inh, "kwinl": inh, "bceil": inh, "ovenglow": inh,
            "lamp": sd.get("lamp", 1.0), "stairl": sd.get("stairl", 1.0), "landl": sd.get("stairl", 1.0),
            "ukey": lit * gk, "urim": lit * sd.get("rim", 1.0), "ufill": lit * sd.get("ufill", 1.0), "urim2": 0.0 if sd.get("rake") else lit * sd.get("rim", 1.0),
            "cutl": 1.0, "cutlow": 1.0}
