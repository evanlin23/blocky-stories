"""ep81-eleven-steps: our stairs have ten steps by day and eleven at night, because Dad sets a carpeted box at the bottom.

One bright, warm, plastic house (the "closer" look): a straight run of nine honey-oak treads under a plum runner with
brass rods, a white banister on one side and a cream wall with framed shapes on the other, a landing with a round
window and an amber nightlight, my door at the top (white, a small gap under it), Dad's navy door and a hall with a
mustard lamp at the bottom, a kitchen beside it.

World (metres, z up): stairs climb +y. Treads 1..9 at y 0.28(k-1)..0.28k, top z 0.19k, x -0.8..0.8; the landing floor
(step ten) is z 1.9 from y 2.52; my door is in the wall at y 4.9 (x 0). The hall runs -y from the foot of the stairs
to the front door at y -5. Acting yaw: 0 faces -y, 180 faces +y, 90 faces +x, -90 faces -x.

Built here, by hand, from kit.py's parts (no text anywhere; the only marks are the numerals and tick marks of the
counter tag, glued to the camera, top left):
- THE BOX: the carpeted eleventh step, placed by the "box" cue.
- THE CLIMBER: one model, posed by fold, head roll, reach and where it stands ("climber" cue).
- LIGHT: looks (day, evening, night, dim, dawn), each shot names one; the light ramps into the next look over the
  last 0.4 s of the shot before a cut, so no light ever switches (flash bar).
Cues (story.json "cues", each restates its whole state): count, box, climber, dip, mydoor, ddoor, torch, props, car.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import bl_story, faces, rig

TMP = Path(tempfile.mkdtemp(prefix="elevensteps-"))
RISE, RUN, NT = 0.19, 0.28, 9
LAND_Y, LAND_Z = 0.28 * 9, 1.9
CEIL = 4.9
HALL_CEIL = 2.6
FONT = Path(__file__).resolve().parents[2] / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"

OAK, PLUM, PLUM_BOX, CREAM, WHITE, MUSTARD, BRASS = "#d6a15f", "#8e3f8f", "#a64fa8", "#f6ead2", "#ffffff", "#e8b13a", "#c9a24c"

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


def B(parent, size, loc, mat, name="b", bevel=0.006, rot=(0, 0, 0)):
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


# ------------------------------------------------------------------------------------------------ the counter tag
def tag_image(n, ticks):
    """The torn cream tape step counter: a big plum numeral, and (during the creaks) a row of ten tick marks."""
    from PIL import Image, ImageDraw, ImageFont

    key = f"tag-{n}-{ticks}"
    p = TMP / f"{key}.png"
    if p.exists():
        return str(p), (300, 460 if ticks is not None else 340)
    W, H = 300, (460 if ticks is not None else 340)
    im = Image.new("RGB", (W, H), hexrgb("#f7ebcf"))
    d = ImageDraw.Draw(im)
    # torn edges: a darker jagged strip at the top and bottom
    for i in range(0, W, 12):
        d.polygon([(i, 0), (i + 12, 0), (i + 12, 9 + (i * 53) % 9)], fill=hexrgb("#d9c79a"))
        d.polygon([(i, H), (i + 12, H), (i, H - 9 - (i * 37) % 9)], fill=hexrgb("#d9c79a"))
    # a darker band where the tape overlaps itself
    d.rectangle([0, 150, W, 156], fill=hexrgb("#efdfb8"))
    f = ImageFont.truetype(str(FONT), 270 if n < 10 else 230)
    txt = str(n)
    bb = d.textbbox((0, 0), txt, font=f)
    cy = 170 if ticks is not None else 172
    d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]), txt, fill=hexrgb(PLUM), font=f)
    if ticks is not None:
        for i in range(10):
            x = 24 + i * 28
            on = i < ticks
            d.rounded_rectangle([x, 330, x + 14, 420], 5, fill=hexrgb(PLUM) if on else hexrgb("#e3d2a8"))
    im.save(p)
    return str(p), (W, H)


def build_inset(kit, ctx):
    cam = kit.OBJ["cam"]
    m = kit._new(nm("inset"))
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    gc = nt.nodes.new("ShaderNodeTexCoord")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 0.8
    nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    pl = kit.plane(nm("inset"), (1.0, 1.0), (0, 0, -0.15), m, cam)
    no_shadow(pl)
    ctx["inset"] = (pl, tex)
    ctx["inset_imgs"] = {}


def place_inset(kit, ctx, n, ticks, lens):
    pl, tex = ctx["inset"]
    key = (n, ticks)
    if key not in ctx["inset_imgs"]:
        path, size = tag_image(n, ticks)
        im = bpy.data.images.load(path)
        im.colorspace_settings.name = "sRGB"
        ctx["inset_imgs"][key] = (im, size)
    im, (iw, ih) = ctx["inset_imgs"][key]
    tex.image = im
    d = 0.15
    unit = d / lens                       # metres per mm of sensor at the panel's distance
    pw = 0.2 * 13.5 * unit
    ph = pw * ih / iw
    x = -6.75 * unit + 0.07 * 13.5 * unit + pw / 2
    y = 0.88 * 12.0 * unit - ph / 2
    pl.location, pl.scale = (x, y, -d), (pw, ph, 1)


# ------------------------------------------------------------------------------------------------ the Climber
class Climber:
    """The Climber: a stooped man of Dad's height in a near-black coat who climbs BACKWARDS. His chest and buttons face
    -y at yaw 0 (down the stairs), his knees bend the wrong way (back, toward +y, the shin coming forward), his arms are
    long with flat hands, and his face is on the BACK of his head (it looks toward +y and a little up). The front of
    his head is short dark hair. Eyes: two pinprick glints in a cream face, set far apart under a brow ridge."""

    L = 0.46                                                    # thigh and shin length

    def __init__(self, kit):
        self.kit = kit
        coat = P("#15191a", 0.85, 0.12)
        coat2 = P("#1c2222", 0.85, 0.1)
        trou = P("#15191a", 0.9, 0.05)
        brass = P("#a8874a", 0.4, 0.6)
        cream = P("#efe3c4", 0.7, 0.12)
        hair = P("#2a2420", 0.9, 0.05)
        hand = P("#a99c80", 0.8, 0.08)
        self.root = E(None, (0, 0, 0), "climber")
        self.hips = E(self.root, (0, 0, 0.9), "clhips")
        # legs: a thigh that goes BACK from the hip, a shin that comes forward again, a bare foot with its toes to the back
        self.knees, self.ankles = [], []
        self.hipj = []
        for sx in (-1, 1):
            hj = E(self.hips, (sx * 0.1, 0, 0), "clhipj")
            B(hj, (0.15, 0.16, self.L), (0, 0, -self.L / 2), trou, "clthigh", 0.04)
            kn = E(hj, (0, 0, -self.L), "clknee")
            B(kn, (0.115, 0.12, self.L), (0, 0, -self.L / 2), trou, "clshin", 0.035)
            B(kn, (0.13, 0.14, 0.06), (0, 0.0, 0.0), trou, "clkneecap", 0.03)
            an = E(kn, (0, 0, -self.L), "clankle")
            B(an, (0.1, 0.30, 0.06), (0, 0.1, -0.03), cream, "clfoot", 0.025)
            for i in range(5):
                B(an, (0.018, 0.04, 0.035), (-0.04 + 0.02 * i, 0.26, -0.04), cream, "cltoe", 0.006)
            self.hipj.append(hj)
            self.knees.append(kn)
            self.ankles.append(an)
        self.skirt = B(self.hips, (0.44, 0.27, 0.46), (0, 0, -0.2), coat, "clskirt", 0.06)
        # the upper body, stooped forward about the hips
        self.upper = E(self.hips, (0, 0, 0), "clupper")
        B(self.upper, (0.38, 0.23, 0.58), (0, 0, 0.27), coat, "cltorso", 0.06)
        B(self.upper, (0.52, 0.25, 0.14), (0, 0.0, 0.56), coat2, "clshoulders", 0.06)
        B(self.upper, (0.24, 0.2, 0.09), (0, 0.01, 0.65), coat, "clcollar", 0.03)
        B(self.upper, (0.07, 0.04, 0.2), (-0.09, -0.12, 0.54), coat2, "cllapel", 0.012, rot=(0, 0.35, 0))
        B(self.upper, (0.07, 0.04, 0.2), (0.09, -0.12, 0.54), coat2, "cllapel", 0.012, rot=(0, -0.35, 0))
        for i in range(5):
            kit.cyl(nm("clbutton"), 0.022, 0.016, (0.0, -0.124, 0.46 - 0.095 * i), brass, self.upper, rot=(math.pi / 2, 0, 0), n=14)
        # arms: long sleeves, flat pale hands with separate fingers, hanging past the knees
        self.arms = []
        for sx in (-1, 1):
            hg = E(self.upper, (sx * 0.31, 0.0, 0.55), "clarm")
            B(hg, (0.11, 0.13, 1.0), (0, 0, -0.5), coat2, "clsleeve", 0.03)
            B(hg, (0.05, 0.14, 0.1), (0, 0, -1.02), hand, "clpalm", 0.012)
            for i in range(4):
                B(hg, (0.034, 0.026, 0.27 - 0.02 * (i % 2)), (0, -0.054 + 0.036 * i, -1.16), hand, "clfinger", 0.008)
            self.arms.append(hg)
        # the neck, long, and the head set too far back. Local head axes: front (hair) -y, face +y.
        self.neck = E(self.upper, (0, 0.04, 0.66), "clneck")
        B(self.neck, (0.08, 0.08, 0.2), (0, 0.02, 0.1), P("#3e342c", 0.85, 0.05), "clneckb", 0.02)
        self.hyaw = E(self.neck, (0, 0.06, 0.2), "clhyaw")
        self.hpitch = E(self.hyaw, (0, 0, 0), "clhpitch")
        self.hroll = E(self.hpitch, (0, 0, 0), "clhroll")
        hg = E(self.hroll, (0, 0, 0.13), "clheadg")
        self.headg = hg
        sk = kit.sphere(nm("cheadskull"), 0.165, (0, 0, 0), cream, hg, seg=20)
        sk.scale = (0.92, 0.97, 1.08)
        B(hg, (0.35, 0.2, 0.37), (0, -0.14, 0.0), hair, "clhairf", 0.05)
        B(hg, (0.34, 0.3, 0.07), (0, -0.04, 0.16), hair, "clhairt", 0.03)
        for sx in (-1, 1):
            B(hg, (0.02, 0.05, 0.08), (sx * 0.16, 0.0, -0.02), cream, "clear", 0.006)
        # the face: a brow ridge, a nose bridge, and two dark sockets each holding a pinprick glint
        B(hg, (0.25, 0.06, 0.045), (0, 0.145, 0.065), cream, "clbrow", 0.015)
        B(hg, (0.035, 0.05, 0.1), (0, 0.15, -0.02), cream, "clnose", 0.01)
        dark = P("#1a1410", 0.9, 0.0)
        self.eyes = []
        for sx in (-1, 1):
            B(hg, (0.05, 0.03, 0.04), (sx * 0.075, 0.146, 0.02), dark, "clsocket", 0.018, rot=(0, 0.25 * sx, 0))
            e = kit.sphere(nm("cleye"), 0.009, (sx * 0.075, 0.163, 0.02), kit.emit("#fff0cc", 12.0, name="cleyeem"), hg, seg=14)
            no_shadow(e)
            self.eyes.append(e)

    def place(self, x, y, z, yaw=0.0, k=28.0, stoop=14.0, al=6.0, ar=11.0, hy=0.0, hp=18.0, hr=0.0, hidden=False,
              hipz=None, sit=0.0):
        r = self.root
        r.location = (x, y, z)
        r.rotation_euler = (0, 0, math.radians(yaw))
        hide(r, hidden)
        if hidden:
            return
        L = self.L
        ka = math.radians(k)
        hz = 0.06 + 2 * L * math.cos(ka) if hipz is None else hipz
        self.hips.location = (0, 0, hz)
        for hj, kn, an in zip(self.hipj, self.knees, self.ankles):
            hj.rotation_euler = (ka, 0, 0)
            kn.rotation_euler = (-2 * ka, 0, 0)
            an.rotation_euler = (ka, 0, 0)
        self.skirt.location = (0, 0, -0.2)
        self.upper.rotation_euler = (math.radians(stoop), 0, 0)
        for hg, a in zip(self.arms, (al, ar)):
            hg.rotation_euler = (math.radians(a) - math.radians(stoop), 0, 0)
        self.hyaw.rotation_euler = (0, 0, math.radians(hy))
        self.hpitch.rotation_euler = (math.radians(hp) - math.radians(stoop), 0, 0)
        self.hroll.rotation_euler = (0, math.radians(hr), 0)


# ------------------------------------------------------------------------------------------------ looks
# gains for each light, the sky of the round window, the world's strength and exposure
LOOKS = {
    "day": {"hall": 0.7, "hallceil": 1.0, "stairs": 1.0, "landing": 1.0, "nl": 0.0, "kitchen": 1.2, "room": 1.0, "moon": 0.0,
            "world": 0.8, "win": ("#8fd0ff", 0.0), "exp": 0.0},
    "evening": {"hall": 1.0, "hallceil": 0.5, "stairs": 0.55, "landing": 0.45, "nl": 1.0, "kitchen": 0.0, "room": 0.0, "moon": 0.5,
                "world": 0.3, "win": ("#24306e", 1.0), "exp": 0.0},
    "night": {"hall": 1.0, "hallceil": 0.25, "stairs": 0.3, "landing": 0.3, "nl": 1.0, "kitchen": 0.0, "room": 0.0, "moon": 0.9,
              "world": 0.18, "win": ("#24306e", 1.0), "exp": 0.0},
    "dim": {"hall": 0.0, "hallceil": 0.0, "stairs": 0.0, "landing": 0.12, "nl": 1.0, "kitchen": 0.0, "room": 0.0, "moon": 1.0,
            "world": 0.12, "win": ("#24306e", 1.0), "exp": 0.3},
    "roomdim": {"hall": 0.0, "hallceil": 0.0, "stairs": 0.0, "landing": 0.0, "nl": 1.0, "kitchen": 0.0, "room": 0.07, "moon": 0.5,
                "world": 0.12, "win": ("#24306e", 1.0), "exp": 0.3},
    "creature": {"hall": 0.0, "hallceil": 0.0, "stairs": 0.0, "landing": 0.0, "nl": 1.0, "kitchen": 0.0, "room": 0.0, "moon": 0.12,
                 "world": 0.025, "win": ("#24306e", 1.0), "exp": 0.5},
    "dawn": {"hall": 0.4, "hallceil": 0.4, "stairs": 0.6, "landing": 0.8, "nl": 0.2, "kitchen": 0.9, "room": 0.5, "moon": 0.0,
             "world": 0.5, "win": ("#ffc6a0", 0.5), "exp": 0.0},
}
NUM = ("hall", "hallceil", "stairs", "landing", "nl", "kitchen", "room", "moon", "world", "exp")


def mix_look(a, b, u):
    out = {k: lerp(a[k], b[k], u) for k in NUM}
    ca, cb = a["win"], b["win"]
    out["win"] = (tuple(lerp(x, y, u) for x, y in zip(mixhex(ca[0], "#000000", 0), mixhex(cb[0], "#000000", 0))), lerp(ca[1], cb[1], u))
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


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    K.kit = kit
    ctx = {"story": story, "shots": {s["id"]: s for s in story["shots"]}, "late": False}
    sc = bpy.context.scene

    # ---- the world: a flat colour the lights are tinted by (the rooms are closed)
    w = sc.world
    ctx["bg"] = w.node_tree.nodes["Background"]
    ctx["bg"].inputs["Color"].default_value = (0.55, 0.62, 0.8, 1.0)

    # ---- lights (base energies; the look's gain scales each)
    ctx["lights"] = {}
    for nme, kind, loc, en, colr, size in (
            ("hall", "POINT", (0.45, -2.75, 1.25), 80, "#ffcf7a", 0.3),
            ("hallceil", "POINT", (0.0, -2.2, 2.35), 260, "#fff0d8", 0.5),
            ("stairs", "POINT", (0.0, 1.2, 3.7), 420, "#fff0d8", 0.5),
            ("landing", "POINT", (1.2, 3.5, 3.9), 380, "#fff0d8", 0.5),
            ("nl", "POINT", (1.0, 4.72, 2.35), 26, "#ffb24d", 0.06),
            ("kitchen", "POINT", (2.8, -0.8, 2.35), 520, "#fff4e0", 0.6),
            ("room", "POINT", (0.0, 7.0, 4.0), 380, "#fff0d8", 0.5)):
        ctx["lights"][nme] = kit.light(nme, kind, loc, en, colr, size=size)
    moon = kit.light("moon", "AREA", (2.4, 3.5, 3.4), 40, "#9fb4ff", size=1.4)
    moon.data.size, moon.data.size_y = 1.2, 1.2
    kit.aim(moon, (0.2, 3.6, 2.2))
    ctx["moon"] = moon
    ctx["camfill"] = kit.light("camfill", "POINT", (0, 0, 2), 14, "#ffe9cf", size=0.5, shadow=False)
    ctx["torch"] = kit.light("torch", "SPOT", (0, 0, 0), 6, "#dbe8ff", size=0.06, spot=60, blend=0.9)
    ctx["clkey"] = kit.light("clkey", "SPOT", (0, 0, 0), 40, "#ffb050", size=0.2, spot=70, blend=0.6)
    ctx["clrim"] = kit.light("clrim", "SPOT", (0, 0, 0), 40, "#8fa8ff", size=0.2, spot=70, blend=0.6)

    # ---- materials
    cream, white = P(CREAM, 0.85, 0.05), P(WHITE, 0.5)
    oak = P(OAK, 0.55)
    plum = P(PLUM, 0.9, 0.05)
    brass = P(BRASS, 0.35, 0.8)
    floorw = kit.texture("wood", 0.7, tint="#f1d8b0")

    # ---- ground floor: hall and kitchen
    B(None, (7.4, 9.2, 0.2), (2.0, -0.4, -0.1), floorw, "gfloor", 0.0)
    B(None, (1.9, 5.2, 0.014), (0, -2.5, 0.007), P("#c9923f", 0.9, 0.05), "hallrug", 0.0)       # a runner in the hall
    # hall walls, ceiling
    wl_y0, wl_y1 = -5.1, 0.0
    B(None, (0.2, 5.2, HALL_CEIL), (-0.9, -2.6, HALL_CEIL / 2), cream, "wallL", 0.0)                     # the hall's left wall
    B(None, (1.8, 0.2, HALL_CEIL), (0, -5.1, HALL_CEIL / 2), cream, "wallF", 0.0)                         # the front wall
    B(None, (0.2, 1.4, HALL_CEIL), (0.9, -4.5, HALL_CEIL / 2), cream, "wallR", 0.0)                       # hall right wall, y -5.2..-3.8
    B(None, (0.2, 1.4, HALL_CEIL - 2.1), (0.9, -3.4, 2.1 + (HALL_CEIL - 2.1) / 2), cream, "kopen", 0.0)   # lintel over the opening
    B(None, (5.0, 6.4, 0.2), (3.4, -1.0, HALL_CEIL + 0.1), P("#fbf4e4", 0.9, 0.02), "gceil", 0.0)         # kitchen ceiling
    B(None, (1.8, 5.2, 0.2), (0, -2.6, HALL_CEIL + 0.1), P("#fbf4e4", 0.9, 0.02), "hceil", 0.0)
    # kitchen shell
    B(None, (0.2, 6.4, HALL_CEIL), (5.9, -1.0, HALL_CEIL / 2), cream, "kwallE", 0.0)
    B(None, (5.8, 0.2, HALL_CEIL), (3.0, -4.3, HALL_CEIL / 2), cream, "kwallF", 0.0)
    B(None, (5.8, 0.2, HALL_CEIL), (3.0, 2.62, HALL_CEIL / 2), cream, "kwallB", 0.0)
    # the stairwell: left wall, the end wall above the hall ceiling, the wall above the kitchen opening
    B(None, (0.2, 5.0, CEIL), (-0.9, 2.5, CEIL / 2), cream, "wallS", 0.0)
    B(None, (1.8, 0.2, CEIL - HALL_CEIL), (0, -0.1, HALL_CEIL + (CEIL - HALL_CEIL) / 2), cream, "stwallF", 0.0)
    B(None, (0.2, 2.52, CEIL - HALL_CEIL), (0.9, 1.26, HALL_CEIL + (CEIL - HALL_CEIL) / 2), cream, "stwallR", 0.0)
    # the stairs: nine solid oak treads, a plum runner held by brass rods, white spindles and a handrail
    ctx["treads"] = []
    for k in range(1, NT + 1):
        grp = E(None, (0, 0, 0), f"tread{k}")
        top = RISE * k
        y0 = RUN * (k - 1)
        B(grp, (1.6, RUN, top), (0, y0 + RUN / 2, top / 2), oak, "tread", 0.01)
        B(grp, (0.95, RUN - 0.01, 0.012), (0, y0 + RUN / 2 + 0.005, top + 0.006), plum, "runtop", 0.004)
        B(grp, (0.95, 0.012, RISE), (0, y0 - 0.006, top - RISE / 2), plum, "runriser", 0.004)
        kit.cyl(nm("rod"), 0.013, 1.08, (0, y0 - 0.025, top - RISE + 0.03), brass, grp, rot=(0, math.pi / 2, 0), n=10)
        ctx["treads"].append(grp)
        # a white spindle at the banister side on every tread
        B(grp, (0.04, 0.04, 0.85), (0.74, y0 + RUN * 0.5, top + 0.425), white, "spindle", 0.005)
    ang = math.atan2(RISE, RUN)
    rail_len = math.hypot(LAND_Y, RISE * NT)
    B(None, (0.08, rail_len, 0.06), (0.74, LAND_Y / 2, (RISE * NT) / 2 + 0.9 + RISE * 0.5), white, "handrail", 0.012, rot=(ang, 0, 0))
    B(None, (0.1, 0.1, 1.0), (0.74, -0.05, 0.5 + 0.0), white, "newel", 0.01)
    # the landing: a solid block, a plum runner to my door, the end wall with my door's frame
    B(None, (3.4, 2.38, LAND_Z), (0.9, LAND_Y + 1.19, LAND_Z / 2), floorw, "landing", 0.0)
    B(None, (0.95, 2.38, 0.012), (0, LAND_Y + 1.19, LAND_Z + 0.006), plum, "landrun", 0.004)
    B(None, (0.2, 2.38, CEIL - LAND_Z), (2.7, LAND_Y + 1.19, LAND_Z + (CEIL - LAND_Z) / 2), cream, "landwallE", 0.0)
    B(None, (3.6, 0.2, CEIL - LAND_Z - 2.1), (0.9, 5.0, LAND_Z + 2.1 + (CEIL - LAND_Z - 2.1) / 2), cream, "doorhead", 0.0)
    B(None, (0.4, 0.2, 2.1), (-0.7, 5.0, LAND_Z + 1.05), cream, "wallBL", 0.0)
    B(None, (0.95, 0.2, 2.1), (0.975, 5.0, LAND_Z + 1.05), cream, "wallBR", 0.0)
    B(None, (0.25, 0.2, 2.1), (2.575, 5.0, LAND_Z + 1.05), cream, "wallBR2", 0.0)
    B(None, (3.6, 5.2, 0.2), (0.9, 2.5, CEIL + 0.1), P("#fbf4e4", 0.9, 0.02), "stairceil", 0.0)
    # my door: frame, hinge pivot, bow pivot, panel with a gap under it, a brass knob
    fr = P("#f1ece0", 0.5)
    B(None, (0.1, 0.24, 2.1), (-0.5, 4.97, LAND_Z + 1.05), fr, "dframe", 0.006)
    B(None, (0.1, 0.24, 2.1), (0.5, 4.97, LAND_Z + 1.05), fr, "dframe", 0.006)
    B(None, (1.1, 0.24, 0.1), (0, 4.97, LAND_Z + 2.1), fr, "dframe", 0.006)
    ctx["mydoor"] = E(None, (-0.45, 4.93, LAND_Z), "mydoor")
    bow = E(ctx["mydoor"], (0.45, 0, 2.0), "mydoorbow")
    ctx["doormat"] = P("#fdfdfd", 0.5)
    B(bow, (0.9, 0.045, 1.9), (0, 0, -0.95), ctx["doormat"], "doorpanel", 0.008)
    B(bow, (0.07, 0.07, 0.07), (0.34, -0.05, -1.0), brass, "knob", 0.02)
    ctx["mybow"] = bow
    # the room behind it (x -2.5..1.25), a partition at x 1.35, and Dad's room beyond (x 1.45..4.5) behind his door
    B(None, (3.75, 4.4, 0.2), (-0.625, 7.2, LAND_Z - 0.1), floorw, "roomfloor", 0.0)
    B(None, (3.75, 4.4, 0.2), (-0.625, 7.2, CEIL + 0.1), P("#fbf4e4", 0.9, 0.02), "roomceil", 0.0)
    B(None, (0.2, 4.4, CEIL - LAND_Z), (-2.5, 7.2, LAND_Z + (CEIL - LAND_Z) / 2), cream, "roomwL", 0.0)
    B(None, (0.2, 4.4, CEIL - LAND_Z), (1.35, 7.2, LAND_Z + (CEIL - LAND_Z) / 2), cream, "roomwR", 0.0)
    B(None, (3.95, 0.2, CEIL - LAND_Z), (-0.525, 9.5, LAND_Z + (CEIL - LAND_Z) / 2), cream, "roomwB", 0.0)
    B(None, (2.2, 2.0, 0.02), (-0.3, 7.4, LAND_Z + 0.011), P("#9a4a9b", 0.95, 0.02), "roomrug", 0.0)
    dr = P("#6a5a78", 0.9, 0.03)
    B(None, (3.05, 4.4, 0.2), (2.975, 7.2, LAND_Z - 0.1), P("#8a6a4a", 0.8, 0.03), "droomfloor", 0.0)
    B(None, (3.05, 4.4, 0.2), (2.975, 7.2, CEIL + 0.1), P("#fbf4e4", 0.9, 0.02), "droomceil", 0.0)
    B(None, (0.2, 4.4, CEIL - LAND_Z), (4.6, 7.2, LAND_Z + (CEIL - LAND_Z) / 2), dr, "droomwR", 0.0)
    B(None, (3.25, 0.2, CEIL - LAND_Z), (3.075, 9.5, LAND_Z + (CEIL - LAND_Z) / 2), dr, "droomwB", 0.0)
    B(None, (1.2, 2.0, 0.5), (3.8, 7.6, LAND_Z + 0.25), P("#5a4a8a", 0.8, 0.05), "dbed", 0.04)
    try:
        kit.prop("bed_single", (-1.7, 8.2, LAND_Z), rot=0, scale=1.25)
        kit.prop("nightstand_1", (-0.7, 9.2, LAND_Z), rot=180, scale=1.2)
        kit.prop("drawer_1", (0.5, 9.2, LAND_Z), rot=180, scale=1.1)
        kit.prop("houseplant_1", (0.85, 5.55, LAND_Z), scale=1.3)
    except Exception as ex:
        print("props:", ex)
    # the threshold under my door, and the amber glow of the nightlight along the gap on my side
    B(None, (1.1, 0.3, 0.2), (0, 5.0, LAND_Z - 0.1), floorw, "threshold", 0.0)
    gl = B(None, (0.92, 0.14, 0.004), (0, 5.07, LAND_Z + 0.002), kit.emit("#ffb24d", 1.6, name="gapglow"), "gapglow", 0.0)
    no_shadow(gl)
    # the round window and the amber nightlight on the landing
    ring = kit.cyl(nm("winring"), 0.5, 0.06, (2.57, 3.6, LAND_Z + 1.5), white, None, rot=(0, math.pi / 2, 0), n=40)
    ctx["win"] = kit.cyl(nm("winglass"), 0.42, 0.02, (2.545, 3.6, LAND_Z + 1.5), kit.emit("#24306e", 1.0, name="winemit"), None,
                         rot=(0, math.pi / 2, 0), n=40)
    ctx["moondisc"] = kit.cyl(nm("moondisc"), 0.09, 0.01, (2.535, 3.35, LAND_Z + 1.72), kit.emit("#fff2d0", 1.0, name="moonemit"),
                              None, rot=(0, math.pi / 2, 0), n=24)
    ctx["winmat"] = ctx["win"].data.materials[0]
    no_shadow(ctx["win"]), no_shadow(ctx["moondisc"])
    B(None, (0.1, 0.1, 0.16), (1.0, 4.83, LAND_Z + 0.35), P("#f4efe6", 0.5), "nlbody", 0.02)
    kit.cyl(nm("nlbulb"), 0.045, 0.03, (1.0, 4.775, LAND_Z + 0.37), kit.emit("#ffb24d", 5.0, name="nlemit"), None, rot=(math.pi / 2, 0, 0), n=16)
    # a few framed shapes on the stair wall (no text, no faces)
    for k, (yy, zz, colr, shape) in enumerate(((0.7, 1.75, "#4c8fd0", "sq"), (1.5, 2.2, "#e0573f", "circ"), (2.2, 2.65, "#6cc24a", "sq"))):
        B(None, (0.04, 0.5, 0.6), (-0.775, yy, zz), P("#f6f3ec", 0.5), "frame", 0.01)
        if shape == "circ":
            kit.cyl(nm("art"), 0.19, 0.02, (-0.75, yy, zz), P(colr, 0.7), None, rot=(0, math.pi / 2, 0), n=24)
        else:
            B(None, (0.02, 0.36, 0.42), (-0.755, yy, zz), P(colr, 0.7), "art", 0.004)
    # ---- Dad's door on the landing (navy, a stride right of mine, opens into his room), the front door with a glass pane
    B(None, (0.1, 0.24, 2.1), (1.4, 4.97, LAND_Z + 1.05), fr, "ddframe", 0.006)
    B(None, (0.1, 0.24, 2.1), (2.5, 4.97, LAND_Z + 1.05), fr, "ddframe", 0.006)
    B(None, (1.2, 0.24, 0.1), (1.95, 4.97, LAND_Z + 2.1), fr, "ddframe", 0.006)
    ctx["ddoor"] = E(None, (2.44, 4.935, LAND_Z), "ddoor")
    B(ctx["ddoor"], (0.98, 0.045, 2.0), (-0.49, 0, 1.02), P("#22306a", 0.45), "ddpanel", 0.008)
    B(ctx["ddoor"], (0.07, 0.07, 0.07), (-0.88, -0.05, 1.0), brass, "ddknob", 0.02)
    B(None, (0.9, 0.12, 2.05), (0.0, -4.95, 1.03), white, "fdoor", 0.01)                              # the front door
    ctx["fpane"] = B(None, (0.5, 0.012, 1.1), (0.0, -4.878, 1.2), kit.emit("#1c2748", 0.6, name="fpane"), "fpane", 0.0)   # its glass, 2 cm proud
    B(None, (0.07, 0.07, 0.07), (0.3, -4.86, 1.0), brass, "fknob", 0.02)
    ctx["tails"] = [B(None, (0.12, 0.05, 0.08), (sx * 0.12, -4.868, 1.05), kit.emit("#ff2a2a", 3.0, name="tail"), "tail", 0.01) for sx in (-1, 1)]
    for o in ctx["tails"]:
        o.hide_render = True
    # the hall table and its mustard lamp, a clock that reads ten
    B(None, (0.4, 0.8, 0.7), (0.62, -2.75, 0.35), P("#c98d4d", 0.6), "htable", 0.012)
    kit.cyl(nm("lampbase"), 0.07, 0.34, (0.62, -2.75, 0.87), P("#f4efe6", 0.5), None, n=14)
    kit.cyl(nm("lampshade"), 0.17, 0.26, (0.62, -2.75, 1.17), P(MUSTARD, 0.6, 0.1), None, n=20, r2=0.11)
    kit.cyl(nm("clockface"), 0.24, 0.04, (-0.78, -3.4, 1.7), P("#fffaf0", 0.5), None, rot=(0, math.pi / 2, 0), n=32)
    ch = E(None, (-0.755, -3.4, 1.7), "clock")
    B(ch, (0.012, 0.02, 0.17), (0, 0.0, 0.085), P("#1a1a22", 0.5), "mhand", 0.003)          # the minute hand, at twelve
    hh = E(ch, (0, 0, 0), "hhandp", rot=(math.radians(60), 0, 0))                          # the hour hand, at ten
    B(hh, (0.012, 0.025, 0.11), (0, 0, 0.055), P("#1a1a22", 0.5), "hhand", 0.003)
    ctx["clock"] = ch
    for k in range(12):
        a = math.radians(30 * k)
        B(None, (0.014, 0.012, 0.03), (-0.752, -3.4 + 0.2 * math.sin(a), 1.7 + 0.2 * math.cos(a)), P("#1a1a22", 0.5), "tick", 0.002,
          rot=(a, 0, 0))
    # the cupboard under the stairs is just a door in the hall wall: not shown. The box lives there by day.
    # ---- kitchen
    try:
        kit.prop("kitchen_fridge", (5.3, 1.7, 0), rot=90, scale=1.05)
        kit.prop("kitchen_cabinet1", (5.3, 0.1, 0), rot=90, scale=1.1)
        kit.prop("kitchen_sink", (3.0, 2.3, 0), rot=180, scale=1.1)
    except Exception as ex:
        print("props:", ex)
    B(None, (1.5, 1.0, 0.06), (3.0, -1.2, 0.74), P("#e0a45a", 0.5), "ktable", 0.012)
    for sx in (-1, 1):
        for sy in (-1, 1):
            B(None, (0.07, 0.07, 0.72), (3.0 + sx * 0.65, -1.2 + sy * 0.4, 0.36), P("#b97d3c", 0.6), "klegs", 0.01)
    for sx in (-1, 1):
        B(None, (0.45, 0.45, 0.05), (3.0 + sx * 1.05, -1.2, 0.45), P("#4c8fd0", 0.5), "kchair", 0.01)
        B(None, (0.45, 0.05, 0.5), (3.0 + sx * 1.05 + sx * 0.22, -1.2, 0.75), P("#4c8fd0", 0.5), "kchairb", 0.01, rot=(0, 0, math.pi / 2))
    B(None, (0.6, 0.03, 0.8), (5.78, -1.3, 1.5), P("#cfe8ff", 0.6), "kwin", 0.01)
    # a plum picture-shape or two in the hall, no text
    B(None, (0.04, 0.5, 0.6), (-0.775, -4.0, 1.55), P("#f6f3ec", 0.5), "frame", 0.01)
    B(None, (0.02, 0.36, 0.42), (-0.755, -4.0, 1.55), P("#e8b13a", 0.7), "art", 0.004)

    # ---- the box: the carpeted eleventh step, with two plum strokes scratched into its underside
    box = E(None, (0, -0.25, 0.06), "box")
    B(box, (1.6, 0.46, 0.12), (0, 0, 0), P("#7a4a22", 0.55), "boxoak", 0.012)
    B(box, (1.32, 0.46, 0.014), (0, 0.0, 0.067), P(PLUM_BOX, 0.9, 0.05), "boxtop", 0.004)
    B(box, (1.32, 0.014, 0.12), (0, -0.237, 0.0), P(PLUM_BOX, 0.9, 0.05), "boxfront", 0.004)
    kit.cyl(nm("boxrod"), 0.013, 1.08, (0, -0.215, 0.045), brass, box, rot=(0, math.pi / 2, 0), n=10)
    for dx in (-0.06, 0.06):
        B(box, (0.025, 0.2, 0.012), (dx, 0.0, -0.066), P("#d5a3e0", 0.8, 0.05), "tally", 0.003)
    ctx["box"] = box
    # ---- the Climber
    ctx["cl"] = Climber(kit)
    # ---- props that come and go (glass, bowl of popcorn, flashlight and mug ride the characters' hands)
    ctx["props"] = build_props(kit)
    build_inset(kit, ctx)
    return ctx


def build_props(kit):
    pr = {}
    glass = E(None, (0, 0, 0), "glass")
    kit.cyl(nm("tumbler"), 0.04, 0.11, (0, 0, 0.055), P("#cfe8ff", 0.1, 0.9), glass, n=14)
    hide(glass, True)
    pr["glass"] = glass
    bowl = E(None, (0, 0, 0), "bowl")
    kit.cyl(nm("bowlo"), 0.1, 0.08, (0, 0, 0.04), P("#e2402f", 0.4), bowl, n=18, r2=0.13)
    for i in range(9):
        B(bowl, (0.045, 0.045, 0.045), (0.05 * math.sin(i * 2.4), 0.05 * math.cos(i * 2.4), 0.095 + 0.01 * (i % 3)),
          P("#fff3c4", 0.8), "pop", 0.015)
    hide(bowl, True)
    pr["bowl"] = bowl
    ch = E(None, (0, 0, 0), "chand")                          # a long flat hand lying on the floor, fingers to +y, the sleeve to -y
    cream = P("#efe3c4", 0.7, 0.12)
    B(ch, (0.11, 0.12, 0.03), (0, 0.0, 0.015), cream, "chpalm", 0.01)
    for i, dx in enumerate((-0.042, -0.014, 0.014, 0.042)):
        ln = (0.27, 0.31, 0.29, 0.22)[i]
        B(ch, (0.024, ln, 0.022), (dx * 1.15, 0.06 + ln / 2, 0.011), cream, "chfinger", 0.007, rot=(0, 0, 0.05 * (i - 1.5)))
    B(ch, (0.1, 0.1, 0.034), (0, -0.1, 0.017), cream, "chwrist", 0.01)
    B(ch, (0.13, 0.6, 0.05), (0, -0.4, 0.027), P("#15191a", 0.85, 0.1), "chsleeve", 0.015)
    hide(ch, True)
    pr["chand"] = ch
    mug = E(None, (0, 0, 0), "mug")
    kit.cyl(nm("mugb"), 0.045, 0.09, (0, 0, 0.045), P("#e8503a", 0.4), mug, n=14)
    hide(mug, True)
    pr["mug"] = mug
    return pr


def late_init(kit, ctx):
    """Called on the first frame, once the cast exists: Dad's beard, the mug, my flashlight."""
    dad, me = rig.CHARS.get("dad"), rig.CHARS.get("me")
    ctx["handprops"] = {}
    if dad is not None:
        hg = dad.head.children[0]
        beard = P("#8e8e96", 0.9, 0.05)
        B(hg, (1.3, 1.3, 0.3), (0, 0.0, -0.46), beard, "dbeard", 0.05)
        B(hg, (1.36, 0.5, 0.42), (0, 0.38, -0.36), beard, "dbeardb", 0.05)
        mug = P("#e8503a", 0.4)
        o = K.kit.cyl(nm("dmug"), 0.17, 0.3, (0, -0.55, -1.75), mug, dad.P["arm1"], n=14)
        o.hide_render = True
        ctx["handprops"]["mug"] = o
    if me is not None:
        o = K.kit.cyl(nm("flash"), 0.13, 0.9, (0, -0.5, -1.75), P("#c9ced6", 0.3, 0.8), me.P["arm-1"], rot=(math.pi / 2, 0, 0), n=14)
        o.hide_render = True
        ctx["handprops"]["flash"] = o
        g = K.kit.cyl(nm("mgl"), 0.1, 0.3, (0, -0.55, -1.75), P("#cfe8ff", 0.1, 0.9), me.P["arm1"], n=12)
        g.hide_render = True
        ctx["handprops"]["glass"] = g


# ------------------------------------------------------------------------------------------------ animate
def animate(kit, story, tl, t, ctx):
    if not ctx["late"]:
        late_init(kit, ctx)
        ctx["late"] = True
    sc = bpy.context.scene
    L, cur = look_at(ctx, tl, t)
    sd = ctx["shots"][cur["id"]]
    ctx["bg"].inputs["Strength"].default_value = L["world"] * sd.get("world_g", 1.0)
    sc.view_settings.exposure = L["exp"] + sd.get("exp", 0.0)
    # ---- the round window
    col_, strength = L["win"]
    wm = ctx["winmat"]
    for nd in wm.node_tree.nodes:
        if nd.type == "EMISSION":
            nd.inputs["Color"].default_value = (col_[0] ** 2.2, col_[1] ** 2.2, col_[2] ** 2.2, 1.0)
            nd.inputs["Strength"].default_value = 1.4
    ctx["moondisc"].hide_render = strength < 0.7
    # ---- camera-following fill, the torch, the Climber's key and rim
    cl, _, cl_lens, _ = bl_story.cam_at(sd, cur, t, {}, tl)
    ctx["camfill"].location = (cl[0], cl[1], cl[2])
    fill = sd.get("fill", 1.0)
    # ---- the count tag
    cn = cue_at(tl, "count", t)
    place_inset(kit, ctx, cn.get("n", 11), cn.get("ticks"), cl_lens)
    # ---- the treads' dips (a creak: the tread sinks 1.8 cm and returns)
    dips = {}
    for c in tl.get("cues", []):
        if c["name"] == "dip":
            u = (t - c["t"]) / c.get("dur", 0.6)
            if 0 <= u <= 1:
                dips[c["k"]] = max(dips.get(c["k"], 0.0), math.sin(math.pi * u) ** 0.7 * c.get("amp", 0.022))
    for k, grp in enumerate(ctx["treads"], start=1):
        grp.location = (0, 0, -dips.get(k, 0.0))
    # ---- the box
    bx = cue_at(tl, "box", t)
    if bx and bx.get("on", True):
        hide(ctx["box"], False)
        pos_ = bx["pos"]
        if "to" in bx:
            u = ss((t - bx["t"]) / max(1e-3, bx.get("dur", 1.0)))
            pos_ = [lerp(a, b, u) for a, b in zip(bx["pos"], bx["to"])]
        ctx["box"].location = tuple(pos_)
        ctx["box"].rotation_euler = (math.radians(bx.get("pitch", 0)), math.radians(bx.get("roll", 0)), math.radians(bx.get("yaw", 0)))
    else:
        hide(ctx["box"], True)
    # ---- my door and Dad's door
    md = cue_at(tl, "mydoor", t)
    op, bw = md.get("open", 0.0), md.get("bow", 0.0)
    if "to" in md:
        u = ss((t - md["t"]) / max(1e-3, md.get("dur", 1.0)))
        op = lerp(op, md["to"], u)
        bw = lerp(bw, md.get("bow_to", bw), u)
    ctx["mydoor"].rotation_euler = (0, 0, math.radians(op))
    ctx["mybow"].rotation_euler = (math.radians(3.2 * bw), 0, 0)
    ctx["mybow"].location = (0.45, 0.02 * bw, 2.0)
    dd = cue_at(tl, "ddoor", t)
    dop = dd.get("open", 0.0)
    if "to" in dd:
        dop = lerp(dop, dd["to"], ss((t - dd["t"]) / max(1e-3, dd.get("dur", 0.8))))
    ctx["ddoor"].rotation_euler = (0, 0, math.radians(-dop))
    # ---- the Climber
    cc = cue_at(tl, "climber", t)
    cl_ = ctx["cl"]
    if cc and cc.get("on", True):
        p = cc["pos"]
        cl_.place(p[0], p[1], p[2], cc.get("yaw", 0.0), cc.get("k", 28.0), cc.get("stoop", 14.0), cc.get("al", 6.0),
                  cc.get("ar", 11.0), cc.get("hy", 0.0), cc.get("hp", 18.0), cc.get("hr", 0.0), False, cc.get("hipz"))
        # amber from below, a cool rim from behind: placed round the creature at its yaw
        ctx["clkey"].location = (p[0] + cc.get("kx", 0.0), p[1] + cc.get("ky", -1.2), p[2] + cc.get("kz", 0.25))
        kit.aim(ctx["clkey"], (p[0] + cc.get("ax", 0.0), p[1] + cc.get("ay", 0.3), p[2] + cc.get("az", 1.0)))
        ctx["clrim"].location = (p[0] + cc.get("rx", 1.6), p[1] + cc.get("ry", 0.4), p[2] + cc.get("rz", 2.3))
        kit.aim(ctx["clrim"], (p[0], p[1], p[2] + 1.2))
        on_ = 1.0
    else:
        cl_.place(0, 0, -9, 0, hidden=True)
        on_ = 0.0
    # ---- the torch
    tc = cue_at(tl, "torch", t)
    if tc and tc.get("on", True):
        ctx["torch"].location = tuple(tc["pos"])
        kit.aim(ctx["torch"], tuple(tc["target"]))
        torch = 1.0
    else:
        torch = 0.0
    # ---- props (a glass, a bowl) and what the characters hold
    pp = cue_at(tl, "props", t)
    for k, o in ctx["props"].items():
        s = pp.get(k)
        if not s:
            hide(o, True)
            continue
        hide(o, False)
        o.location = tuple(s["pos"])
        o.rotation_euler = (0, 0, math.radians(s.get("yaw", 0)))
    for k, o in ctx["handprops"].items():
        o.hide_render = not pp.get("hold_" + k)
    # ---- the car's tail lights beyond the front door
    cs = cue_at(tl, "car", t)
    for i, o in enumerate(ctx["tails"]):
        on = bool(cs.get("on"))
        o.hide_render = not on
        if on:
            u = ss((t - cs["t"]) / max(1e-3, cs.get("dur", 1.6))) if cs.get("go") else 0.0
            o.location = ((-1 if i == 0 else 1) * lerp(0.12, 0.03, u), -4.868, 1.05)
            o.scale = (lerp(1.0, 0.25, u),) * 3
    dm = ctx["doormat"].node_tree.nodes["Principled BSDF"].inputs["Base Color"]
    dk = sd.get("door", 1.0)
    dm.default_value = (dk, dk, dk, 1.0)
    ov = {n: L[n] for n in ("hall", "hallceil", "stairs", "landing", "nl", "kitchen", "room", "moon")}
    ov["moon"] *= sd.get("moon_g", 1.0)
    ov["nl"] *= sd.get("nl_g", 1.0)
    ov["camfill"] = fill
    ov["torch"] = torch
    ov["clkey"] = on_ * sd.get("clkey", 1.0)
    ov["clrim"] = on_ * sd.get("clrim", 1.0)
    for k in ("hall", "hallceil", "stairs", "landing", "kitchen", "room"):
        ov[k] = ov[k] * sd.get(k + "_g", 1.0)
    return ov
