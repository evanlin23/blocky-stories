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
import os
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
def face_image(path):
    from PIL import Image, ImageDraw

    S = 512
    im = Image.new("RGB", (S, S), hexrgb("#efe3c4"))
    d = ImageDraw.Draw(im)
    # a faint darker rim, and a soft shade under the cheeks (no mouth, no nose)
    d.ellipse([6, 6, S - 6, S - 6], outline=hexrgb("#cdbb94"), width=14)
    for sx in (-1, 1):
        cx, cy, r = S / 2 + sx * 150, S * 0.46, 40
        d.ellipse([cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14], fill=hexrgb("#d9c9a0"))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(10, 9, 12))
        d.ellipse([cx - r * 0.55, cy - r * 0.62, cx - r * 0.1, cy - r * 0.18], fill=(255, 252, 240))
    im.save(path)
    return path


class Climber:
    """The Climber: far too tall (3.2 m standing), a heavy moss coat to the shins, wide shoulders, long arms with flat
    hands, a round cream head rolled flat onto its left shoulder, so its face is turned 90 degrees. Front is -y at yaw 0."""

    def __init__(self, kit):
        self.kit = kit
        moss, brass, cream = P("#6f8f6a", 0.85, 0.08), P("#a8874a", 0.45, 0.5), P("#efe3c4", 0.7, 0.1)
        dark = P("#3f5a40", 0.9, 0.05)
        self.root = E(None, (0, 0, 0), "climber")
        # legs and the lower coat are scaled to the hip height by place()
        self.legs = [B(self.root, (0.36, 0.4, 1.0), (sx * 0.27, 0, 0.5), dark, "clleg", 0.05) for sx in (-1, 1)]
        self.shoes = [B(self.root, (0.4, 0.8, 0.16), (sx * 0.27, -0.18, 0.08), P("#26231f", 0.6), "clshoe", 0.05) for sx in (-1, 1)]
        self.skirt = B(self.root, (1.1, 0.72, 1.0), (0, 0, 1.0), moss, "clskirt", 0.1)
        self.hips = E(self.root, (0, 0, 1.4), "clhips")
        self.upper = E(self.hips, (0, 0, 0), "clupper")
        B(self.upper, (1.05, 0.66, 1.25), (0, 0, 0.55), moss, "cltorso", 0.1)
        B(self.upper, (1.6, 0.74, 0.42), (0, 0, 1.22), moss, "clshoulders", 0.12)
        B(self.upper, (0.5, 0.5, 0.2), (0, 0, 1.5), dark, "clcollar", 0.07)
        for i in range(4):
            kit.cyl(nm("clbutton"), 0.055, 0.04, (0, -0.35, 0.0 + 0.32 * i), brass, self.upper, rot=(math.pi / 2, 0, 0), n=14)
        # arms: a hinge at each shoulder, a long sleeve, a flat hand
        self.arms = []
        for sx in (-1, 1):
            hinge = E(self.upper, (sx * 0.95, 0, 1.25), "clarm")
            B(hinge, (0.3, 0.34, 1.95), (0, 0, -0.97), P("#56724f", 0.85, 0.08), "clsleeve", 0.08)
            B(hinge, (0.3, 0.44, 0.08), (0, -0.04, -2.0), cream, "clhand", 0.025)
            B(hinge, (0.32, 0.32, 0.05), (0, 0, -1.93), brass, "clcuff", 0.015)
            self.arms.append((hinge, sx))
        # the head: a round cream drum rolled about the neck, the face a disc 1.2 cm proud of its front
        self.neck = E(self.upper, (0, -0.03, 1.55), "clneck")
        self.hroot = E(self.root, (0, 0, 1.5), "clhroot")      # the head hangs off the root, so its facing is set directly
        self.hyaw = E(self.hroot, (0, 0, 0), "clhyaw")
        self.hpitch = E(self.hyaw, (0, 0, 0), "clhpitch")
        self.rollg = E(self.hpitch, (0, 0, 0), "clroll")
        self.headg = E(self.rollg, (0, 0, 0.42), "clheadg")
        R = 0.5
        kit.cyl(nm("clhead"), R, 0.4, (0, 0, 0), P("#e2d3ad", 0.7, 0.1), self.headg, rot=(math.pi / 2, 0, 0), n=32)
        self.face_mat = kit._new(nm("clface"))
        nt = self.face_mat.node_tree
        b = nt.nodes["Principled BSDF"]
        b.inputs["Roughness"].default_value = 0.7
        tex = nt.nodes.new("ShaderNodeTexImage")
        gc = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
        nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = 0.22
        nt.links.new(tex.outputs["Color"], em.inputs["Color"])
        ad = nt.nodes.new("ShaderNodeAddShader")
        nt.links.new(b.outputs[0], ad.inputs[0])
        nt.links.new(em.outputs[0], ad.inputs[1])
        kit._fogged(self.face_mat, ad.outputs[0])
        im = bpy.data.images.load(face_image(str(TMP / "climber-face.png")))
        im.colorspace_settings.name = "sRGB"
        tex.image = im
        self.face = kit.cyl(nm("clfaced"), R - 0.004, 0.012, (0, -0.206, 0), self.face_mat, self.headg, rot=(math.pi / 2, 0, 0), n=48)
        self.moss = moss

    def place(self, x, y, z, yaw, fold=1.0, roll=80.0, reach=50.0, reach2=None, hidden=False, hp=0.0, hy=0.0, hoff=0.42):
        r = self.root
        r.location = (x, y, z)
        r.rotation_euler = (0, 0, math.radians(yaw))
        hide(r, hidden)
        if hidden:
            return
        beta = math.radians(78.0 * fold)
        hipz = 1.5 - 0.55 * fold
        self.hips.location = (0, 0, hipz)
        self.upper.rotation_euler = (beta, 0, 0)
        for lg in self.legs:
            lg.scale = (1, 1, hipz)
            lg.location = (lg.location.x, 0, hipz / 2)
        h = hipz - 0.2
        self.skirt.scale = (1, 1, h)
        self.skirt.location = (0, 0, 0.3 + h / 2)
        # arms hang to the world's vertical, then swing forward by `reach` (and `reach2` for the left one)
        for (hinge, sx), rch in zip(self.arms, (reach, reach if reach2 is None else reach2)):
            hinge.rotation_euler = (-math.radians(rch) - beta, 0, 0)
        # the head: anchored at the neck (it follows the bend), its facing set from the creature's own frame:
        # hy turns it about the vertical (+ toward the creature's left), hp lifts it, roll tips it onto a shoulder
        bpy.context.view_layer.update()
        self.hroot.location = self.root.matrix_world.inverted() @ self.neck.matrix_world.translation
        self.hyaw.rotation_euler = (0, 0, math.radians(hy))
        self.hpitch.rotation_euler = (math.radians(hp), 0, 0)
        self.rollg.rotation_euler = (0, math.radians(roll), 0)
        self.headg.location = (0, 0, hoff)
        if os.environ.get("CL_DEBUG"):
            bpy.context.view_layer.update()
            print("HEAD", tuple(round(v, 2) for v in self.headg.matrix_world.translation),
                  "HAND", [tuple(round(v, 2) for v in (h.matrix_world @ V((0, 0, -2.0))))  for h, _ in self.arms], flush=True)


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
            ("nl", "POINT", (1.65, 4.72, 2.35), 26, "#ffb24d", 0.06),
            ("kitchen", "POINT", (2.8, -0.8, 2.35), 520, "#fff4e0", 0.6),
            ("room", "POINT", (0.0, 7.0, 4.0), 380, "#fff0d8", 0.5)):
        ctx["lights"][nme] = kit.light(nme, kind, loc, en, colr, size=size)
    moon = kit.light("moon", "AREA", (2.4, 3.5, 3.4), 40, "#9fb4ff", size=1.4)
    moon.data.size, moon.data.size_y = 1.2, 1.2
    kit.aim(moon, (0.2, 3.6, 2.2))
    ctx["moon"] = moon
    ctx["camfill"] = kit.light("camfill", "POINT", (0, 0, 2), 14, "#ffe9cf", size=0.5, shadow=False)
    ctx["torch"] = kit.light("torch", "SPOT", (0, 0, 0), 6, "#dbe8ff", size=0.06, spot=60, blend=0.9)
    ctx["clkey"] = kit.light("clkey", "SPOT", (0, 0, 0), 16, "#ffb050", size=0.2, spot=70, blend=0.6)
    ctx["clrim"] = kit.light("clrim", "SPOT", (0, 0, 0), 22, "#8fa8ff", size=0.2, spot=70, blend=0.6)

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
    B(None, (0.2, 2.9, HALL_CEIL), (-0.9, -3.65, HALL_CEIL / 2), cream, "wallL", 0.0)                     # y -5.1..-2.2
    B(None, (0.2, 0.9, HALL_CEIL - 2.05), (-0.9, -1.8, 2.05 + (HALL_CEIL - 2.05) / 2), cream, "lintel", 0.0)
    # y -2.25..-1.35 is Dad's door; the wall fills -1.35..0 with this piece:
    B(None, (0.2, 1.35, HALL_CEIL), (-0.9, -0.675, HALL_CEIL / 2), cream, "wallL", 0.0)
    B(None, (1.8, 0.2, HALL_CEIL), (0, -5.1, HALL_CEIL / 2), cream, "wallF", 0.0)                         # the front wall
    B(None, (0.2, 1.4, HALL_CEIL), (0.9, -4.5, HALL_CEIL / 2), cream, "wallR", 0.0)                       # hall right wall, y -5.2..-3.8
    B(None, (0.2, 1.4, HALL_CEIL - 2.1), (0.9, -3.4, 2.1 + (HALL_CEIL - 2.1) / 2), cream, "kopen", 0.0)   # lintel over the opening
    B(None, (5.8, 6.4, 0.2), (3.0, -1.0, HALL_CEIL + 0.1), P("#fbf4e4", 0.9, 0.02), "gceil", 0.0)         # kitchen ceiling
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
    B(None, (2.2, 0.2, 2.1), (1.6, 5.0, LAND_Z + 1.05), cream, "wallBR", 0.0)
    B(None, (3.6, 5.2, 0.2), (0.9, 2.5, CEIL + 0.1), P("#fbf4e4", 0.9, 0.02), "stairceil", 0.0)
    # my door: frame, hinge pivot, bow pivot, panel with a gap under it, a brass knob
    fr = P("#f1ece0", 0.5)
    B(None, (0.1, 0.24, 2.1), (-0.5, 4.97, LAND_Z + 1.05), fr, "dframe", 0.006)
    B(None, (0.1, 0.24, 2.1), (0.5, 4.97, LAND_Z + 1.05), fr, "dframe", 0.006)
    B(None, (1.1, 0.24, 0.1), (0, 4.97, LAND_Z + 2.1), fr, "dframe", 0.006)
    ctx["mydoor"] = E(None, (-0.45, 4.93, LAND_Z), "mydoor")
    bow = E(ctx["mydoor"], (0.45, 0, 2.0), "mydoorbow")
    B(bow, (0.9, 0.045, 1.9), (0, 0, -0.95), white, "doorpanel", 0.008)
    B(bow, (0.07, 0.07, 0.07), (0.34, -0.05, -1.0), brass, "knob", 0.02)
    ctx["mybow"] = bow
    # the room behind it
    B(None, (5.0, 4.4, 0.2), (0, 7.2, LAND_Z - 0.1), floorw, "roomfloor", 0.0)
    B(None, (5.0, 4.4, 0.2), (0, 7.2, CEIL + 0.1), P("#fbf4e4", 0.9, 0.02), "roomceil", 0.0)
    B(None, (0.2, 4.4, CEIL - LAND_Z), (-2.5, 7.2, LAND_Z + (CEIL - LAND_Z) / 2), cream, "roomwL", 0.0)
    B(None, (0.2, 4.4, CEIL - LAND_Z), (2.5, 7.2, LAND_Z + (CEIL - LAND_Z) / 2), cream, "roomwR", 0.0)
    B(None, (5.0, 0.2, CEIL - LAND_Z), (0, 9.5, LAND_Z + (CEIL - LAND_Z) / 2), cream, "roomwB", 0.0)
    B(None, (2.8, 2.0, 0.02), (0.0, 7.4, LAND_Z + 0.011), P("#9a4a9b", 0.95, 0.02), "roomrug", 0.0)
    try:
        kit.prop("bed_single", (-1.7, 8.2, LAND_Z), rot=0, scale=1.25)
        kit.prop("nightstand_1", (-0.7, 9.2, LAND_Z), rot=180, scale=1.2)
        kit.prop("drawer_1", (1.6, 9.2, LAND_Z), rot=180, scale=1.1)
        kit.prop("houseplant_1", (2.0, 5.5, LAND_Z), scale=1.3)
    except Exception as ex:
        print("props:", ex)
    # the threshold under my door, and the amber glow of the nightlight along the gap on my side
    B(None, (1.1, 0.3, 0.2), (0, 5.0, LZ - 0.1), floorw, "threshold", 0.0)
    gl = B(None, (0.92, 0.14, 0.004), (0, 5.07, LZ + 0.002), kit.emit("#ffb24d", 1.6, name="gapglow"), "gapglow", 0.0)
    no_shadow(gl)
    # the round window and the amber nightlight on the landing
    ring = kit.cyl(nm("winring"), 0.5, 0.06, (2.57, 3.6, LAND_Z + 1.5), white, None, rot=(0, math.pi / 2, 0), n=40)
    ctx["win"] = kit.cyl(nm("winglass"), 0.42, 0.02, (2.545, 3.6, LAND_Z + 1.5), kit.emit("#24306e", 1.0, name="winemit"), None,
                         rot=(0, math.pi / 2, 0), n=40)
    ctx["moondisc"] = kit.cyl(nm("moondisc"), 0.09, 0.01, (2.535, 3.35, LAND_Z + 1.72), kit.emit("#fff2d0", 1.0, name="moonemit"),
                              None, rot=(0, math.pi / 2, 0), n=24)
    ctx["winmat"] = ctx["win"].data.materials[0]
    no_shadow(ctx["win"]), no_shadow(ctx["moondisc"])
    B(None, (0.1, 0.1, 0.16), (1.65, 4.83, LAND_Z + 0.35), P("#f4efe6", 0.5), "nlbody", 0.02)
    kit.cyl(nm("nlbulb"), 0.045, 0.03, (1.65, 4.775, LAND_Z + 0.37), kit.emit("#ffb24d", 7.0, name="nlemit"), None, rot=(math.pi / 2, 0, 0), n=16)
    # a few framed shapes on the stair wall (no text, no faces)
    for k, (yy, zz, colr, shape) in enumerate(((0.7, 1.75, "#4c8fd0", "sq"), (1.5, 2.2, "#e0573f", "circ"), (2.2, 2.65, "#6cc24a", "sq"))):
        B(None, (0.04, 0.5, 0.6), (-0.775, yy, zz), P("#f6f3ec", 0.5), "frame", 0.01)
        if shape == "circ":
            kit.cyl(nm("art"), 0.19, 0.02, (-0.75, yy, zz), P(colr, 0.7), None, rot=(0, math.pi / 2, 0), n=24)
        else:
            B(None, (0.02, 0.36, 0.42), (-0.755, yy, zz), P(colr, 0.7), "art", 0.004)
    # ---- Dad's door (navy, opens on the left wall), the front door with a glass pane, the hall lamp and clock
    ctx["ddoor"] = E(None, (-0.88, -1.35, 0), "ddoor")
    B(ctx["ddoor"], (0.05, 0.86, 2.02), (0, -0.43, 1.01), P("#22306a", 0.45), "ddpanel", 0.008)
    B(ctx["ddoor"], (0.07, 0.07, 0.07), (0.05, -0.78, 1.0), brass, "ddknob", 0.02)
    B(None, (0.12, 0.08, 2.1), (-0.9, -1.31, 1.05), fr, "ddframe", 0.006)
    B(None, (0.12, 0.08, 2.1), (-0.9, -2.29, 1.05), fr, "ddframe", 0.006)
    B(None, (1.4, 3.0, 0.1), (-1.55, -1.8, 0.05), P("#6a4a3a", 0.9, 0.02), "droomfloor", 0.0)       # Dad's room, just a hint
    B(None, (0.2, 3.0, 2.6), (-2.3, -1.8, 1.3), P("#5a4a58", 0.9, 0.02), "droomwall", 0.0)
    B(None, (0.7, 1.6, 0.5), (-1.7, -1.7, 0.3), P("#7a6a9a", 0.8, 0.05), "dbed", 0.04)
    B(None, (0.9, 0.12, 2.05), (0.0, -4.95, 1.03), white, "fdoor", 0.01)                              # the front door
    ctx["fpane"] = B(None, (0.5, 0.03, 1.1), (0.0, -5.0, 1.2), kit.emit("#1c2748", 0.6, name="fpane"), "fpane", 0.004)
    B(None, (0.07, 0.07, 0.07), (0.3, -4.86, 1.0), brass, "fknob", 0.02)
    ctx["tails"] = [B(None, (0.12, 0.05, 0.08), (sx * 0.12, -5.5, 1.05), kit.emit("#ff2a2a", 3.0, name="tail"), "tail", 0.01) for sx in (-1, 1)]
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
    ch = E(None, (0, 0, 0), "chand")
    cream = P("#efe3c4", 0.7, 0.1)
    B(ch, (0.36, 0.34, 0.07), (0, 0.0, 0.035), cream, "chpalm", 0.02)
    for i, dx in enumerate((-0.12, -0.04, 0.04, 0.12)):
        B(ch, (0.06, 0.34, 0.06), (dx, -0.3 - 0.02 * (i % 2), 0.03), cream, "chfinger", 0.02)
    B(ch, (0.16, 0.2, 0.07), (0.0, 0.3, 0.035), P("#6f8f6a", 0.85, 0.08), "chcuff", 0.02)
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
    ctx["bg"].inputs["Strength"].default_value = L["world"]
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
    ctx["ddoor"].rotation_euler = (0, 0, math.radians(dop))
    # ---- the Climber
    cc = cue_at(tl, "climber", t)
    cl_ = ctx["cl"]
    if cc and cc.get("on", True):
        p = cc["pos"]
        cl_.place(p[0], p[1], p[2], cc.get("yaw", 180), cc.get("fold", 1.0), cc.get("roll", 80.0), cc.get("reach", 50.0),
                  cc.get("reach2"), False, cc.get("hp", 0.0), cc.get("hy", 0.0), cc.get("hoff", 0.42))
        # amber from below, a cool rim from behind: placed round the creature at its yaw
        a = math.radians(cc.get("yaw", 180))
        ctx["clkey"].location = (p[0] + cc.get("kx", 0.0), p[1] + cc.get("ky", -1.2), p[2] + cc.get("kz", 0.25))
        kit.aim(ctx["clkey"], (p[0] + cc.get("ax", 0.0), p[1] + cc.get("ay", 0.3), p[2] + cc.get("az", 1.0)))
        ctx["clrim"].location = (p[0] + 1.6, p[1] + 0.4, p[2] + 2.3)
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
            o.location = ((-1 if i == 0 else 1) * lerp(0.12, 0.04, u), lerp(-5.5, -9.5, u), 1.05)
    ov = {n: L[n] for n in ("hall", "hallceil", "stairs", "landing", "nl", "kitchen", "room", "moon")}
    ov["camfill"] = fill
    ov["torch"] = torch
    ov["clkey"] = on_ * sd.get("clkey", 1.0)
    ov["clrim"] = on_ * sd.get("clrim", 1.0)
    for k in ("hall", "hallceil", "stairs", "landing", "kitchen", "room"):
        ov[k] = ov[k] * sd.get(k + "_g", 1.0)
    return ov
