"""ep85 Early Alarm: a peach-and-lavender suburban dawn, a backyard with the Sun asleep on the lawn.

Everything is built from kit.py's parts and our own blocks. No lettering anywhere: the clock is numerals only.
Stages sit far apart so their lights never meet; every shot names its stage (story.json shots[].stage) and its sky.

  yard   origin (0, 0): the house's back wall at y = -1, the lawn, the bare patch, the Sun at (0, 7, 2.1), the shed at
         (-5, 12.5). Acting yaw: 0 faces -y, 180 faces +y, 90 faces +x.
  bed    (100, 0)   my bedroom        kit   (140, 0)  our kitchen      pkit (170, 0)  Mr. Pruitt's kitchen
  liv    (200, 0)   the living room   hall  (230, 0)  the hallway      shed (260, 0)  the shed inside
  street (320, 0)   a row of five houses facing -y (ours is the middle one, Mr. Pruitt's is next)

THE SUN (the creature): a 3 x 3 x 3 lattice of soft rounded marigold blocks, the corners left out, a hot core showing
through the seams, one huge gold eye on its front under a heavy lid. Asleep: a closed-lid disc over the eye. It only
swells a little as it breathes. Steady light, never a flicker.

Cues read here (all optional; every ramp is a "dur" in seconds, at least 0.3 s on anything bright):
  clock {s, up, ring, two, dur}   the round clock inset on the camera (digits, glyph up 0..1, ringing, two alarms)
  eye {v, dur}                    the Sun's lid: 0 closed, 1 open
  glow {v, dur}                   the Sun's own light, 1 = asleep, 1.7 = awake
  sunpos {p, s, dur, face}        the Sun's centre, scale, and whether its eye shows (0 for an ordinary sun)
  rope {mode: slack|taut}         the rope from the shed to the Sun
  fridge {v, dur}                 Mr. Pruitt's fridge door (0 shut, 1 open)
  crank {v, dur}                  turns of the winch crank
  street {lit: ours|all|none}     the windows on the street
  car {x, dur}                    the car on the street
  curtain {v, dur}                my bedroom curtains (0 shut, 1 open)
  blanket {v, dur}                my blanket pulled off (0 on, 1 off)
  pillow {v, dur}                 my pillow pulled over my face
"""

from __future__ import annotations

import math
import os
import tempfile
from pathlib import Path

import bmesh
import bpy
import random
from mathutils import Vector as V
from PIL import Image, ImageDraw, ImageFont

import blocky as _blocky

FONT = os.path.join(os.path.dirname(_blocky.__file__), "fonts", "SchibstedGrotesk-Black.ttf")
OR = {"yard": (0, 0), "bed": (100, 0), "kit": (140, 0), "pkit": (170, 0), "liv": (200, 0), "hall": (230, 0),
      "shed": (260, 0), "street": (320, 0)}
SUN = (0.0, 7.0, 2.1)
PITCH = 1.65
FRONT = SUN[1] - PITCH * 1.5 + 0.05
EYE = (0.05, FRONT - 0.02, 1.8)
SHED = (-5.0, 12.5)
PULLEY = (SHED[0], SHED[1] - 0.25, 4.7)
HOUSES = [-16, -8, 0, 8, 16]      # street: ours is index 2, Mr. Pruitt's index 3
SKY = {   # world colour, strength, window pane colour
    "dawn": ("#f4c7d6", 1.0, "#ffd6b8"),
    "dark": ("#2a3190", 1.0, "#1f2a86"),
    "night": ("#232d86", 0.8, "#1f2a86"),
    "day": ("#ffc9a8", 1.2, "#cfe8ff"),
    "peach": ("#ffbf9a", 1.1, "#ffd6b8"),
}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------------------------------------ cues
def cl(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def latest(tl, name, t):
    out = None
    for c in cl(tl, name):
        if c["t"] <= t + 1e-9:
            out = c
    return out


def ramp(tl, name, t, key="v", default=0.0):
    """A value that eases from the previous cue's value to this cue's over its dur."""
    cs = [c for c in cl(tl, name) if c["t"] <= t + 1e-9]
    if not cs:
        return default
    c = cs[-1]
    prev = cs[-2].get(key, default) if len(cs) > 1 else default
    v = c.get(key, default)
    d = max(c.get("dur", 0.0), 1e-3)
    u = ss((t - c["t"]) / d) if c.get("dur", 0.0) > 0 else 1.0
    if isinstance(v, (list, tuple)):
        return [p + (q - p) * u for p, q in zip(prev if isinstance(prev, (list, tuple)) else v, v)]
    return prev + (v - prev) * u


def shot_of(story, tl, t):
    s = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    return s, next((x for x in story["shots"] if x["id"] == s["id"]), {})


def lens_at(story, tl, t):
    s, spec = shot_of(story, tl, t)
    keys = spec.get("cam") or [[0, 0, 0, 24]]
    if len(keys) == 1:
        return keys[0][3]
    u = (t - s["start"]) / max(1e-6, s["end"] - s["start"])
    a, b = keys[0], keys[-1]
    return a[3] + (b[3] - a[3]) * ss(u)


# ------------------------------------------------------------------------------------------------ pictures
def disc_png(path, s, two=False):
    """The round clock face: a cream rim, a navy face, big red numerals (or two little alarm clocks)."""
    im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([6, 6, 505, 505], fill=(255, 241, 214, 255))
    d.ellipse([40, 40, 471, 471], fill=(24, 27, 78, 255))
    red = (255, 70, 60, 255)
    if two:
        for cx in (150, 362):
            d.ellipse([cx - 78, 212 - 78 + 40, cx + 78, 212 + 78 + 40], fill=red)
            d.ellipse([cx - 56, 212 - 56 + 40, cx + 56, 212 + 56 + 40], fill=(255, 241, 214, 255))
            d.line([(cx, 252), (cx, 214)], fill=(24, 27, 78, 255), width=12)
            d.line([(cx, 252), (cx + 30, 266)], fill=(24, 27, 78, 255), width=12)
            d.ellipse([cx - 62 - 16, 150 + 30, cx - 62 + 16, 150 + 62], fill=(255, 176, 0, 255))
            d.ellipse([cx + 62 - 16, 150 + 30, cx + 62 + 16, 150 + 62], fill=(255, 176, 0, 255))
    else:
        size = 150 if len(s) <= 4 else 118
        f = ImageFont.truetype(FONT, size)
        w = d.textlength(s, font=f)
        d.text((256 - w / 2 + 4, 262), s, font=f, fill=red, anchor="lm")
    im.save(path)


def sun_png(path):
    im = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(8):
        a = k * math.pi / 4
        pts = [(128 + 112 * math.cos(a), 128 + 112 * math.sin(a)),
               (128 + 62 * math.cos(a + 0.28), 128 + 62 * math.sin(a + 0.28)),
               (128 + 62 * math.cos(a - 0.28), 128 + 62 * math.sin(a - 0.28))]
        d.polygon(pts, fill=(255, 176, 0, 255))
    d.ellipse([128 - 62, 128 - 62, 128 + 62, 128 + 62], fill=(255, 176, 0, 255))
    d.ellipse([128 - 40, 128 - 40, 128 + 40, 128 + 40], fill=(255, 224, 120, 255))
    im.save(path)


def arcs_png(path):
    """Ringing: two short arcs each side of the clock."""
    im = Image.new("RGBA", (768, 512), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for side in (-1, 1):
        for r in (270, 320):
            cx = 384
            d.arc([cx - r, 256 - r, cx + r, 256 + r], 180 - 28 if side < 0 else -28, 180 + 28 if side < 0 else 28,
                  fill=(255, 176, 0, 255), width=22)
    im.save(path)


def frost_png(path):
    rnd = random.Random(5)
    im = Image.new("RGBA", (512, 512), (214, 236, 252, 255))
    d = ImageDraw.Draw(im)
    for _ in range(60):
        x, y = rnd.uniform(0, 512), rnd.uniform(0, 512)
        a = rnd.uniform(0, math.tau)
        for _k in range(6):
            a2 = a + rnd.uniform(-0.4, 0.4)
            L = rnd.uniform(30, 80)
            nx, ny = x + L * math.cos(a2), y + L * math.sin(a2)
            d.line([(x, y), (nx, ny)], fill=(255, 255, 255, 255), width=rnd.choice((3, 5, 7)))
            for s_ in (-1, 1):
                d.line([(nx, ny), (nx + 24 * math.cos(a2 + s_ * 0.8), ny + 24 * math.sin(a2 + s_ * 0.8))],
                       fill=(240, 250, 255, 255), width=3)
            x, y, a = nx, ny, a2
    d.rectangle([0, 0, 511, 511], outline=(255, 255, 255, 255), width=26)
    im.save(path)


def calendar_png(path):
    """A wall calendar of our own glyphs: a marigold band and a grid of dots in two alternating colours."""
    im = Image.new("RGB", (360, 400), (255, 248, 236))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 359, 70], fill=(255, 176, 0))
    d.ellipse([150, 10, 210, 60], fill=(255, 224, 120))
    for r in range(5):
        for c in range(7):
            cx, cy = 28 + c * 50, 112 + r * 56
            on = (r * 7 + c) % 2 == 0
            d.ellipse([cx - 17, cy - 17, cx + 17, cy + 17], fill=(255, 150, 20) if on else (150, 120, 255))
    d.rectangle([0, 0, 359, 399], outline=(214, 58, 48), width=8)
    im.save(path)


def img_mat(kit, name, path, strength=1.4, alpha=True):
    m = kit._new(name)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    N.remove(N["Principled BSDF"])
    tc = N.new("ShaderNodeTexCoord")
    tx = N.new("ShaderNodeTexImage")
    L.new(tc.outputs["Generated"], tx.inputs["Vector"])
    tx.image = bpy.data.images.load(str(path), check_existing=False)
    tx.image.colorspace_settings.name = "sRGB"
    tx.interpolation = "Linear"
    em = N.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    L.new(tx.outputs["Color"], em.inputs["Color"])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    if alpha:
        tr = N.new("ShaderNodeBsdfTransparent")
        mx = N.new("ShaderNodeMixShader")
        L.new(tx.outputs["Alpha"], mx.inputs[0])
        L.new(tr.outputs[0], mx.inputs[1])
        L.new(em.outputs[0], mx.inputs[2])
        L.new(mx.outputs[0], out.inputs["Surface"])
    else:
        L.new(em.outputs[0], out.inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    return m, em


# ------------------------------------------------------------------------------------------------ the build
class Stage:
    def __init__(self, kit, name, ctx):
        self.kit, self.name, self.ox, self.oy = kit, name, *OR[name]
        self.ctx = ctx
        self.lights = []

    def p(self, loc):
        return (self.ox + loc[0], self.oy + loc[1], loc[2])

    def box(self, name, size, loc, mat, **kw):
        return self.kit.box(f"{self.name}.{name}", size, self.p(loc), mat, **kw)

    def cyl(self, name, r, h, loc, mat, **kw):
        return self.kit.cyl(f"{self.name}.{name}", r, h, self.p(loc), mat, **kw)

    def light(self, name, kind, loc, energy, hexc, **kw):
        ob = self.kit.light(f"{self.name}.{name}", kind, self.p(loc), energy, hexc, **kw)
        self.lights.append(f"{self.name}.{name}")
        return ob

    def room(self, w, d, h, wall, floor, ceil, doorway=None):
        """A closed room: x in -w/2..w/2, y in 0..d. doorway = (wall "x+" , y0, y1) leaves a gap in that wall."""
        K = self.kit
        self.box("floor", (w + 0.4, d + 0.4, 0.1), (0, d / 2, -0.05), floor)
        self.box("ceil", (w + 0.4, d + 0.4, 0.1), (0, d / 2, h + 0.05), ceil)
        self.box("wback", (w + 0.4, 0.2, h), (0, d + 0.1, h / 2), wall)
        self.box("wfront", (w + 0.4, 0.2, h), (0, -0.1, h / 2), wall)
        self.box("wleft", (0.2, d, h), (-w / 2 - 0.1, d / 2, h / 2), wall)
        if doorway:
            y0, y1 = doorway
            self.box("wright_a", (0.2, y0, h), (w / 2 + 0.1, y0 / 2, h / 2), wall)
            self.box("wright_b", (0.2, d - y1, h), (w / 2 + 0.1, y1 + (d - y1) / 2, h / 2), wall)
            self.box("wright_h", (0.2, y1 - y0, h - 2.15), (w / 2 + 0.1, (y0 + y1) / 2, 2.15 + (h - 2.15) / 2), wall)
        else:
            self.box("wright", (0.2, d, h), (w / 2 + 0.1, d / 2, h / 2), wall)


def build(kit, story, tl):
    kit.FLASH_SAFE = True
    work = Path(tempfile.mkdtemp(prefix="ep85-"))
    ctx = {"work": work, "st": {}}
    M = {}

    def P(hexc, rough=0.6, spec=0.3):
        return kit.plastic(hexc, rough, spec=spec)

    # palette
    cream = P("#fff1e2")
    peach = P("#ffc3a0")
    lav = P("#cdbcff")
    sky_b = P("#a9d8ff")
    mint = P("#b6ecc9")
    butter = P("#ffe39a")
    white = P("#f7f5f2")
    redd = P("#d63a30")
    wood = P("#b9824f")
    wood_d = P("#8a5a3a")
    barn = P("#c4473a")
    barn_d = P("#8e3027")
    grey = P("#6d7380")
    iron = P("#4a525c", 0.45, 0.5)
    steel = kit.metal("#9aa0a6", 0.35)
    ink = P("#241a22")

    # ---------------------------------------------------------------- the clock inset (on the camera)
    cam = kit.OBJ["cam"]
    ctx["disc_mats"] = {}
    for s in ("5:00", "5:30", "5:58", "6:00", "7:00", "8:00", "9:00", "11:00", "two"):
        p = work / f"disc_{s.replace(':', '_')}.png"
        disc_png(p, s, two=(s == "two"))
        ctx["disc_mats"][s] = img_mat(kit, f"disc {s}", p, 1.25)[0]
    sunp = work / "sunglyph.png"
    sun_png(sunp)
    ctx["glyph_mat"], ctx["glyph_em"] = img_mat(kit, "glyph", sunp, 1.2)
    arcp = work / "arcs.png"
    arcs_png(arcp)
    ctx["arc_mat"] = img_mat(kit, "arcs", arcp, 1.4)[0]
    grp = kit.empty("clockhud", (0, 0, -0.4), cam)
    ctx["hud"] = grp
    ctx["hud_disc"] = kit.plane("hud.disc", (1, 1), (0, 0, 0), ctx["disc_mats"]["5:00"], grp)
    ctx["hud_glyph"] = kit.plane("hud.glyph", (1, 1), (0, 0, 0.0004), ctx["glyph_mat"], grp)
    ctx["hud_arcs"] = kit.plane("hud.arcs", (1.5, 1), (0, 0, -0.0004), ctx["arc_mat"], grp)

    # ---------------------------------------------------------------- lights that follow the camera
    kit.light("key", "POINT", (-0.35, 0.3, -0.25), 55.0, "#fff0e0", size=0.4, parent=cam, shadow=False)
    kit.light("kfill", "POINT", (0.4, -0.1, -0.1), 14.0, "#ffe6d4", size=0.5, parent=cam, shadow=False)

    # ================================================================ the yard
    Y = Stage(kit, "yard", ctx)
    frost = P("#e3eef8", 0.9)
    lawn = P("#58b866", 0.95)
    ctx["lawn_mat"], ctx["frost_mat"] = lawn, frost
    bare = P("#c9a27a", 0.95)
    kit.plane("ground", (400, 400), (0, 20, 0), frost)
    kit.box("lawn", (16, 20, 0.04), (-1, 9, 0.02), lawn)
    kit.cyl("bare", 4.6, 0.02, (0, 7.0, 0.045), bare, n=48)
    for i in range(-9, 8):
        kit.box(f"bfence{i}", (0.9, 0.08, 1.5), (i + 0.5, 19.0, 0.75), wood_d, bevel=0.02)
    for sx in (-9.0, 7.0):    # low white fences between the yards
        for j in range(0, 19):
            kit.box(f"sfence{sx}{j}", (0.08, 0.9, 0.9), (sx, j + 0.5, 0.45), white, bevel=0.02)
    kit.box("gate", (0.08, 1.4, 1.0), (7.0, 12.0, 0.5), butter, bevel=0.02)
    # our house, seen from behind
    kit.box("house", (13, 9, 6.4), (-0.5, -5.5, 3.2), cream, bevel=0.04)
    kit.box("house.roof", (13.8, 9.8, 0.3), (-0.5, -5.5, 6.55), P("#8d6aa8"), bevel=0.04)
    kit.box("house.door", (1.0, 0.06, 2.1), (0.0, -0.95, 1.05), redd, bevel=0.02)
    kit.box("house.doorframe", (1.3, 0.04, 2.3), (0.0, -0.97, 1.15), white, bevel=0.02)
    kit.box("house.step", (2.4, 1.0, 0.25), (0.0, -0.5, 0.125), P("#d3cdc6"), bevel=0.03)
    kit.box("house.kwin", (1.6, 0.05, 1.2), (-3.6, -0.97, 1.7), kit.emit("#ffd18a", 1.5, "kwin"))
    kit.box("house.kwinf", (1.8, 0.04, 1.4), (-3.6, -0.96, 1.7), white)
    kit.box("house.mwin", (1.4, 0.05, 1.2), (3.5, -0.97, 4.3), kit.emit("#2f3fb0", 1.0, "mwin"))
    for x, z in ((-3.5, 4.3), (0.0, 4.3)):
        kit.box(f"house.uw{x}", (1.4, 0.05, 1.2), (x, -0.97, z), kit.emit("#2f3fb0", 1.0, f"uw{x}"))
    # trees and bushes
    for i, (x, y) in enumerate(((-14, 12), (14, 10), (-12, 26), (12, 28), (0, 34), (-26, 22), (26, 20))):
        kit.prop("sub_tree_large", (x, y, 0), height=5.5)
    for i, (x, y) in enumerate(((5.8, 3.0), (-8.0, 2.0), (-8.0, 16), (5.8, 16))):
        kit.prop("bush_1", (x, y, 0), height=1.2)
    # the shed
    sx, sy = SHED
    kit.box("shed.l", (1.5, 3.4, 3.6), (sx - 1.35, sy, 1.8), barn, bevel=0.04)
    kit.box("shed.r", (1.5, 3.4, 3.6), (sx + 1.35, sy, 1.8), barn, bevel=0.04)
    kit.box("shed.h", (1.3, 3.4, 1.3), (sx, sy, 2.95), barn, bevel=0.04)
    kit.box("shed.back", (4.2, 0.2, 3.6), (sx, sy + 1.7, 1.8), barn_d, bevel=0.04)
    kit.box("shed.inside", (1.3, 0.1, 2.3), (sx, sy + 1.0, 1.15), kit.emit("#ffd18a", 2.2, "shed light"))
    kit.box("shed.roof", (4.8, 4.0, 0.25), (sx, sy, 3.75), P("#7a3b4e"), bevel=0.03)
    kit.box("shed.mast", (0.15, 0.15, 0.8), (sx, sy, 4.3), wood_d)
    kit.cyl("shed.pulley", 0.34, 0.12, PULLEY, steel, rot=(math.pi / 2, 0, 0), n=24)
    ctx["shed_door"] = kit.box("shed.leaf", (1.3, 0.08, 2.3), (sx - 0.65 - 0.55, sy - 2.15, 1.15), barn_d,
                               rot=(0, 0, math.radians(-50)))
    # the rope: slack along the grass, or taut from the pulley to the Sun
    rope = P("#e0b878", 0.9)
    a, b = V((sx, sy - 1.8, 0.07)), V((-1.4, SUN[1] - 3.0, 0.07))
    ctx["rope_slack"] = []
    n = 26
    for i in range(n):
        u0, u1 = i / n, (i + 1) / n
        p0, p1 = a.lerp(b, u0), a.lerp(b, u1)
        p0.x += 0.6 * math.sin(u0 * 3.0)
        p1.x += 0.6 * math.sin(u1 * 3.0)
        m = (p0 + p1) / 2
        seg = kit.cyl(f"rope{i}", 0.07, (p1 - p0).length * 1.05, tuple(m), rope, n=8)
        seg.rotation_euler = (p1 - p0).to_track_quat("Z", "Y").to_euler()
        ctx["rope_slack"].append(seg)
    ctx["rope_taut"] = kit.cyl("rope.taut", 0.08, 1.0, (0, 0, -50), rope, n=8)
    # the Sun
    gold = kit.emit("#ffb000", 1.1, "sun shell")
    core = kit.emit("#ffd25e", 3.2, "sun core")
    sclera = kit.emit("#ffeeb0", 1.1, "eye sclera")
    iris = kit.emit("#ff9d00", 1.2, "eye iris")
    ring = kit.emit("#f09000", 1.2, "eye ring")
    pupil = kit.emit("#3a1600", 0.1, "eye pupil")
    glint = kit.emit("#ffffff", 3.0, "eye glint")
    lidm = kit.emit("#e88e00", 0.9, "sun lid")
    sroot = kit.empty("sun", SUN)
    ctx["sun"] = sroot
    kit.sphere("sun.core", 2.35, (0, 0, 0), core, sroot, seg=24)
    k = 0
    for ix in (-1, 0, 1):
        for iy in (-1, 0, 1):
            for iz in (-1, 0, 1):
                if abs(ix) + abs(iy) + abs(iz) == 3:
                    continue
                kit.box(f"sun.blk{k}", (1.55, 1.55, 1.55), (ix * PITCH, iy * PITCH, iz * PITCH), gold, sroot, bevel=0.42, seg=4)
                k += 1
    ex, ey, ez = EYE[0] - SUN[0], EYE[1] - SUN[1], EYE[2] - SUN[2]
    eye_parts = []

    def disc(name, r, y, x, z, mat, sx_=1.0, sz_=1.0, h=0.02):
        ob = kit.cyl(name, r, h, (x, y, z), mat, sroot, rot=(math.pi / 2, 0, 0), n=40)
        ob.scale = (sx_, sz_, 1.0)
        eye_parts.append(ob)
        return ob

    disc("sun.socket", 1.12, ey - 0.02, ex, ez, kit.emit("#f0a000", 1.25, "socket"), 1.0, 0.95, 0.06)
    EY0 = ey + 0.1
    ball = kit.sphere("sun.ball", 0.8, (ex, EY0, ez), sclera, sroot, seg=40)
    ball.scale = (1.0, 0.5, 0.95)
    eye_parts.append(ball)
    disc("sun.ring", 0.56, ey - 0.205, ex, ez - 0.02, ring, h=0.03)
    disc("sun.iris", 0.5, ey - 0.225, ex, ez - 0.02, iris, h=0.03)
    disc("sun.pupil", 0.27, ey - 0.285, ex, ez - 0.02, pupil, 0.62, 1.0, 0.03)
    eye_parts.append(kit.sphere("sun.glint", 0.07, (ex + 0.2, ey - 0.31, ez + 0.12), glint, sroot, seg=10))

    def shell(name, r, edge, above, mat):
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=72, v_segments=48, radius=r)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > 0.05], context="VERTS")
        for v in bm.verts:
            e = edge(v.co.x / 0.8) * r
            if (above and v.co.z < e) or (not above and v.co.z > e):
                v.co.z = e
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(name, me)
        ob.data.materials.append(mat)
        ob.location = (ex, EY0, ez)
        ob.scale = (1.0, 0.5, 0.95)
        for p_ in me.polygons:
            p_.use_smooth = True
        eye_parts.append(ob)
        return kit.link(ob, sroot)

    up = lambda x: 0.22 - 0.30 * x * x
    lo = lambda x: -0.62 + 0.35 * x * x
    glow = kit.emit("#ffc040", 1.6, "lid seam")
    shell("sun.seamup", 0.84, lambda x: up(x) - 0.05, True, glow)
    shell("sun.seamlo", 0.84, lambda x: lo(x) + 0.04, False, glow)
    shell("sun.lid", 0.85, up, True, lidm)
    shell("sun.lidlow", 0.85, lo, False, lidm)
    # the closed lid: a disc over the whole eye that lifts (scales away from its top edge) as the eye opens
    shut = kit.emit("#f29a00", 1.15, "eye shut")
    crease = kit.emit("#a85a00", 0.5, "eye crease")
    top = ez + 1.0
    lidg = kit.empty("sun.lidgrp", (ex, ey - 0.4, top), sroot)
    shutd = kit.cyl("sun.shut", 1.12, 0.03, (0, 0, -1.0), shut, lidg, rot=(math.pi / 2, 0, 0), n=40)
    shutd.scale = (1.0, 0.95, 1.0)
    cr = kit.cyl("sun.crease", 0.9, 0.02, (0, -0.03, -1.12), crease, lidg, rot=(math.pi / 2, 0, 0), n=40)
    cr.scale = (1.0, 0.12, 1.0)
    kit.cyl("sun.crease2", 0.9, 0.02, (0, -0.045, -1.14), shut, lidg, rot=(math.pi / 2, 0, 0), n=40).scale = (1.0, 0.1, 1.0)
    ctx["lidg"] = lidg
    ctx["eye_parts"] = eye_parts
    # lights: the Sun's own warm light, a sky fill, the shed lamp, a day key
    Y.light("sunlit", "POINT", (0.3, FRONT - 0.9, 2.0), 120.0, "#ffb347", size=0.9)
    Y.light("sunfill", "AREA", (0.0, FRONT - 3.5, 3.5), 40.0, "#ffc060", rot=(math.radians(-15), 0, 0), size=6.0)
    Y.light("shedlamp", "POINT", (sx, sy - 2.4, 1.6), 250.0, "#ffd18a", size=0.5)
    ob = Y.light("rim", "SPOT", (-5.0, 0.5, 5.0), 500.0, "#9fb8ff", size=0.5, spot=60, blend=0.6)
    kit.aim(ob, (-0.5, 5.5, 1.6))
    ob = Y.light("daykey", "SUN", (0, 0, 20), 3.0, "#ffe2c8", rot=(math.radians(35), 0, math.radians(20)))
    Y.light("stepl", "POINT", (0.0, -0.3, 2.6), 35.0, "#ffd9a8", size=0.4)
    ctx["st"]["yard"] = Y

    # ================================================================ rooms
    def bed():
        S = Stage(kit, "bed", ctx)
        floor = P("#d9a672", 0.5)
        S.room(4.4, 4.4, 2.7, lav, floor, cream, doorway=(1.2, 2.1))
        S.box("rug", (1.8, 1.3, 0.02), (0.5, 2.0, 0.01), P("#ff9fb5"))
        # the window (a pane inside the back wall) and curtains
        pm = kit._new("bedpane")
        nt = pm.node_tree
        nt.nodes.remove(nt.nodes["Principled BSDF"])
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = 1.6
        em.inputs["Color"].default_value = kit.col("#2f3fb0")
        out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
        nt.links.new(em.outputs[0], out.inputs["Surface"])
        ctx["bedpane_em"] = em
        S.box("pane", (1.5, 0.03, 1.1), (-0.3, 4.37, 1.75), pm)
        for dx, dz in ((0, 0.6), (0, -0.6)):
            S.box(f"winf{dz}", (1.7, 0.05, 0.08), (-0.3, 4.35, 1.75 + dz), white)
        for dx in (-0.8, 0.8):
            S.box(f"winv{dx}", (0.08, 0.05, 1.2), (-0.3 + dx, 4.35, 1.75), white)
        S.box("winmid", (0.05, 0.05, 1.1), (-0.3, 4.35, 1.75), white)
        ctx["curt"] = []
        for sg in (-1, 1):
            c = S.box(f"curt{sg}", (0.8, 0.08, 1.7), (-0.3 + sg * 1.1, 4.28, 1.8), P("#ff9aa8"), bevel=0.02)
            ctx["curt"].append((c, sg))
        # nightstand and the clock
        S.box("nst", (0.55, 0.5, 0.55), (-0.55, 4.1, 0.275), wood, bevel=0.03)
        S.box("nst.top", (0.6, 0.55, 0.04), (-0.55, 4.1, 0.57), wood_d, bevel=0.02)
        cg = kit.empty("realclock", (OR["bed"][0] - 0.55, 4.0, 0.74))
        ctx["clock3d"] = cg
        kit.cyl("rc.body", 0.15, 0.1, (0, 0, 0), redd, cg, rot=(math.pi / 2, 0, 0), n=36)
        ctx["rc_face"] = kit.plane("rc.face", (0.27, 0.27), (0, -0.056, 0), ctx["disc_mats"]["5:00"], cg, rot=(math.pi / 2, 0, 0))
        for sgn in (-1, 1):
            kit.sphere(f"rc.bell{sgn}", 0.05, (sgn * 0.09, 0, 0.15), P("#c8ccd2", 0.3), cg, seg=12)
            kit.box(f"rc.leg{sgn}", (0.03, 0.04, 0.05), (sgn * 0.09, 0, -0.16), P("#c8ccd2"), cg)
        S.box("lamp", (0.18, 0.18, 0.18), (-0.45, 4.2, 0.66), butter, bevel=0.04)
        # bed (head toward +y) with blanket and pillow
        S.box("bedframe", (1.05, 2.1, 0.3), (-1.5, 3.3, 0.15), wood_d, bevel=0.03)
        S.box("mattress", (1.0, 2.0, 0.2), (-1.5, 3.3, 0.4), white, bevel=0.05)
        ctx["blanket"] = S.box("blanket", (1.04, 1.15, 0.16), (-1.5, 2.85, 0.55), P("#6aa8ff"), bevel=0.06)
        ctx["pillow"] = S.box("pillow", (0.62, 0.38, 0.12), (-1.5, 4.15, 0.56), P("#fff5f5"), bevel=0.05)
        cp = work / "calendar.png"
        calendar_png(cp)
        cm, _ = img_mat(kit, "calendar", cp, 1.1, alpha=False)
        kit.plane("calendar", (0.9, 1.0), S.p((1.45, 4.355, 1.55)), cm, rot=(math.pi / 2, 0, 0))
        # the hall behind the doorway
        S.box("hallpane", (0.05, 1.6, 2.2), (2.9, 1.65, 1.1), kit.emit("#ffe0b0", 1.4, "bhall"))
        S.box("hallfloor", (1.4, 1.6, 0.05), (2.7, 1.65, 0.0), floor)
        S.light("lamp", "POINT", (0.3, 2.0, 2.4), 170.0, "#ffe2c0", size=0.4)
        S.light("lamp2", "POINT", (-0.5, 4.0, 1.2), 25.0, "#ffd18a", size=0.2)
        S.light("hall", "POINT", (2.6, 1.65, 2.2), 60.0, "#ffd9a8", size=0.3)
        ctx["st"]["bed"] = S

    def kitchen(name, palette):
        S = Stage(kit, name, ctx)
        wall, floorc, cab, accent = palette
        S.room(5.0, 4.6, 2.7, P(wall), P(floorc, 0.5), cream, doorway=(0.4, 1.4))
        # window on the back wall: frost (ours) or a bright dawn pane
        pm = kit._new(f"{name}pane")
        if name == "kit":
            fp = work / "frost.png"
            frost_png(fp)
            fm, _ = img_mat(kit, "frost", fp, 1.35, alpha=False)
            pane_mat = fm
        else:
            pane_mat = kit.emit("#bfe0ff", 1.4, "pkpane")
        S.box("pane", (1.8, 0.03, 1.1), (-0.0, 4.57, 1.75), pane_mat)
        for dz in (-0.58, 0.58):
            S.box(f"wf{dz}", (2.0, 0.05, 0.08), (0.0, 4.55, 1.75 + dz), white)
        for dx in (-0.94, 0.94):
            S.box(f"wv{dx}", (0.08, 0.05, 1.2), (dx, 4.55, 1.75), white)
        # counter along the left wall
        S.box("counter", (0.65, 3.4, 0.9), (-2.15, 2.2, 0.45), P(cab), bevel=0.02)
        S.box("ctop", (0.7, 3.45, 0.05), (-2.15, 2.2, 0.925), white)
        S.box("sink", (0.4, 0.6, 0.02), (-2.15, 1.2, 0.955), steel)
        # table, chair, mug
        S.cyl("table", 0.62, 0.05, (0.4, 2.6, 0.75), P(accent), n=32)
        S.cyl("tleg", 0.07, 0.72, (0.4, 2.6, 0.37), white, n=12)
        S.box("chair", (0.42, 0.42, 0.05), (0.4, 3.35, 0.45), wood, bevel=0.02)
        S.box("chairback", (0.42, 0.05, 0.45), (0.4, 3.57, 0.7), wood, bevel=0.02)
        for sx_, sy_ in ((-0.17, -0.17), (0.17, -0.17), (-0.17, 0.17), (0.17, 0.17)):
            S.box(f"cleg{sx_}{sy_}", (0.04, 0.04, 0.43), (0.4 + sx_, 3.35 + sy_, 0.215), wood)
        S.cyl("mug", 0.05, 0.1, (0.55, 2.4, 0.83), P("#fff1e2"), n=16)
        # fridge on the back wall, its door on a hinge (the door swings toward the camera)
        fx, fy = (1.7, 4.2)
        for nm, sz, lc in (("back", (0.7, 0.04, 1.7), (0, 0.33, 0.85)), ("l", (0.04, 0.66, 1.7), (-0.33, 0, 0.85)),
                           ("r", (0.04, 0.66, 1.7), (0.33, 0, 0.85)), ("top", (0.7, 0.66, 0.04), (0, 0, 1.7)),
                           ("bot", (0.7, 0.66, 0.04), (0, 0, 0.02)), ("s1", (0.66, 0.62, 0.03), (0, 0, 0.6)),
                           ("s2", (0.66, 0.62, 0.03), (0, 0, 1.15))):
            S.box(f"fr.{nm}", sz, (fx + lc[0], fy + lc[1] - 0.0, lc[2]), P("#eef2f6"))
        hinge = kit.empty(f"{name}.fhinge", S.p((fx + 0.35, fy - 0.34, 0)))
        kit.box(f"{name}.fdoor", (0.7, 0.06, 1.7), (-0.35, -0.03, 0.85), P("#f4f7fa"), hinge, bevel=0.02)
        kit.box(f"{name}.fhandle", (0.04, 0.05, 0.5), (-0.6, -0.09, 1.0), steel, hinge)
        ctx[f"{name}.hinge"] = hinge
        S.box("milk", (0.1, 0.1, 0.22), (fx - 0.2, fy - 0.1, 1.26), white, bevel=0.01)
        S.box("milkc", (0.1, 0.1, 0.06), (fx - 0.2, fy - 0.1, 1.38), sky_b)
        S.box("eggs", (0.2, 0.12, 0.08), (fx + 0.2, fy - 0.1, 1.2), P("#f6e8c8"), bevel=0.02)
        cg = kit.empty(f"{name}.fclock", S.p((fx, fy - 0.12, 1.22)))
        kit.cyl(f"{name}.fc.body", 0.07, 0.05, (0, 0, 0.07), redd, cg, rot=(math.pi / 2, 0, 0), n=20)
        kit.cyl(f"{name}.fc.face", 0.05, 0.01, (0, -0.03, 0.07), P("#fff1d6"), cg, rot=(math.pi / 2, 0, 0), n=20)
        # the hall behind the doorway
        S.box("hallpane", (0.05, 1.4, 2.3), (3.2, 0.9, 1.15), kit.emit("#ffe0b0", 1.3, f"{name}hall"))
        S.light("lamp", "POINT", (0.2, 2.2, 2.4), 170.0, "#ffe2c0", size=0.4)
        S.light("lamp2", "POINT", (-1.5, 1.2, 2.3), 60.0, "#ffe2c0", size=0.4)
        ctx["st"][name] = S
        return S

    def living():
        S = Stage(kit, "liv", ctx)
        S.room(6.0, 4.8, 2.7, P("#ffd7bf"), P("#c99a6c", 0.5), cream)
        S.box("rug", (3.0, 2.0, 0.02), (0.3, 2.2, 0.01), P("#7fc6c9"))
        teal = P("#4aa3a8")
        S.box("couch", (2.3, 0.95, 0.45), (0.3, 4.1, 0.225), teal, bevel=0.06)
        S.box("couchback", (2.3, 0.25, 0.8), (0.3, 4.55, 0.65), teal, bevel=0.06)
        for sg in (-1, 1):
            S.box(f"carm{sg}", (0.25, 0.95, 0.65), (0.3 + sg * 1.2, 4.1, 0.33), teal, bevel=0.06)
        ctx["heatpad"] = S.box("heatpad", (0.5, 0.36, 0.05), (0.8, 3.95, 0.5), P("#ff8f5a"), bevel=0.02)
        S.box("remote", (0.06, 0.18, 0.03), (-0.2, 3.9, 0.48), ink)
        S.box("door", (0.95, 0.08, 2.05), (-2.2, 4.76, 1.03), P("#d96a4a"), bevel=0.02)
        S.box("doorf", (1.15, 0.06, 2.2), (-2.2, 4.74, 1.1), white)
        S.box("knob", (0.07, 0.07, 0.07), (-1.85, 4.7, 1.0), steel)
        S.box("table", (0.9, 0.6, 0.4), (-1.0, 2.2, 0.2), wood, bevel=0.03)
        S.box("lampf", (0.4, 0.4, 1.4), (2.5, 4.3, 0.7), butter, bevel=0.1)
        S.box("window", (1.6, 0.03, 1.1), (1.6, 4.77, 1.7), kit.emit("#bfe0ff", 1.3, "livpane"))
        S.light("lamp", "POINT", (0.3, 2.0, 2.4), 190.0, "#ffe2c0", size=0.4)
        S.light("lamp2", "POINT", (2.4, 3.8, 1.5), 60.0, "#ffd18a", size=0.3)
        ctx["st"]["liv"] = S

    def hallway():
        S = Stage(kit, "hall", ctx)
        S.room(2.0, 6.0, 2.6, P("#ffe9cf"), P("#c99a6c", 0.5), cream)
        S.box("mydoor", (0.9, 0.08, 2.05), (0.0, 5.95, 1.03), P("#d96a4a"), bevel=0.02)
        S.box("mydoorf", (1.1, 0.06, 2.2), (0.0, 5.93, 1.1), white)
        for y in (1.6, 3.6):
            S.box(f"sd{y}", (0.08, 0.9, 2.05), (-0.96, y, 1.03), P("#8fd0a8"), bevel=0.02)
            S.box(f"sd2{y}", (0.08, 0.9, 2.05), (0.96, y, 1.03), P("#8fb8ff"), bevel=0.02)
        S.box("hrug", (0.8, 4.5, 0.02), (0.0, 3.0, 0.01), P("#ff9fb5"))
        S.light("lamp", "POINT", (0.0, 2.2, 2.3), 150.0, "#ffe2c0", size=0.4)
        S.light("lamp2", "POINT", (0.0, 4.6, 2.3), 100.0, "#ffe2c0", size=0.4)
        ctx["st"]["hall"] = S

    def shed():
        S = Stage(kit, "shed", ctx)
        plank = P("#9c6a45")
        S.room(4.2, 5.0, 3.4, plank, P("#6f4a30"), P("#6f4a30"))
        S.box("shelf", (1.4, 0.3, 0.05), (-1.3, 4.8, 1.6), wood_d)
        S.box("crate", (0.5, 0.5, 0.4), (-1.5, 4.6, 0.2), wood, bevel=0.02)
        S.box("window", (0.8, 0.03, 0.6), (1.2, 4.97, 2.3), kit.emit("#bfe0ff", 1.2, "shedpane"))
        # the winch: iron housing facing -y, a drum, a crank on the right, a brake lever on the left
        S.box("housing", (0.9, 0.7, 1.1), (0.0, 3.6, 0.55), iron, bevel=0.03)
        S.box("housing.top", (1.0, 0.8, 0.08), (0.0, 3.6, 1.14), iron, bevel=0.02)
        S.cyl("drum", 0.26, 0.9, (0.0, 3.6, 1.42), steel, rot=(0, math.pi / 2, 0), n=24)
        S.cyl("coil", 0.3, 0.55, (0.0, 3.6, 1.42), P("#e0b878", 0.9), rot=(0, math.pi / 2, 0), n=24)
        # two marigold strokes scratched into the housing, 1 cm proud of its face
        for dx in (-0.12, 0.12):
            S.box(f"tally{dx}", (0.035, 0.012, 0.3), (dx, 3.244, 0.7), kit.emit("#ffb000", 1.6, "tally"))
        S.cyl("axle", 0.04, 0.5, (0.65, 3.6, 1.42), steel, rot=(0, math.pi / 2, 0), n=12)
        ctx["crank"] = kit.empty("crankg", S.p((0.85, 3.6, 1.42)))
        kit.box("crank.arm", (0.05, 0.05, 0.4), (0, 0, -0.18), steel, ctx["crank"])
        kit.cyl("crank.handle", 0.035, 0.26, (0, 0, -0.38), P("#ff9d3a"), ctx["crank"], rot=(0, math.pi / 2, 0), n=12)
        kit.cyl("brake.pivot", 0.04, 0.08, S.p((-0.55, 3.6, 0.6)), steel, rot=(0, math.pi / 2, 0), n=12)
        th = math.atan2(0.45, 0.6)
        bl = kit.box("brake.lever", (0.05, 0.05, 0.75), S.p((-0.6, 3.38, 0.88)), P("#d63a30"), rot=(th, 0, 0))
        # the rope from the drum up to the roof
        ctx["rope_in"] = []
        for i in range(8):
            ctx["rope_in"].append(kit.cyl(f"shed.rope{i}", 0.05, 0.4, S.p((0, 3.6, 2.0)), P("#e0b878", 0.9), n=8))
        S.light("lamp", "POINT", (0.0, 2.4, 2.7), 220.0, "#ffd9a8", size=0.4)
        S.light("lamp2", "POINT", (0.0, 1.4, 1.6), 90.0, "#ffd9a8", size=0.3)
        ctx["st"]["shed"] = S

    bed()
    kitchen("kit", ("#ffcfb0", "#d9a672", "#ff9d6e", "#ffe39a"))
    kitchen("pkit", ("#bdeed0", "#c9b8a0", "#7fc99a", "#ffb07a"))
    living()
    hallway()
    shed()
    # Mr. Pruitt's dog in a basket, in his kitchen
    S = ctx["st"]["pkit"]
    S.box("basket", (0.7, 0.55, 0.16), (1.4, 1.2, 0.08), wood_d, bevel=0.04)
    S.box("basketin", (0.6, 0.45, 0.04), (1.4, 1.2, 0.17), P("#ff8fa8"))
    dogm = P("#8a5530")
    S.box("dog.body", (0.4, 0.22, 0.16), (1.4, 1.2, 0.27), dogm, bevel=0.04)
    S.box("dog.head", (0.2, 0.2, 0.18), (1.4 - 0.26, 1.2, 0.33), dogm, bevel=0.04)
    S.box("dog.snout", (0.1, 0.1, 0.08), (1.4 - 0.37, 1.2, 0.3), P("#5e3a20"), bevel=0.02)
    for sg in (-1, 1):
        S.box(f"dog.ear{sg}", (0.06, 0.07, 0.14), (1.4 - 0.25, 1.2 + sg * 0.11, 0.4), P("#5e3a20"), bevel=0.02)
        S.box(f"dog.eye{sg}", (0.025, 0.025, 0.03), (1.4 - 0.375, 1.2 + sg * 0.06, 0.37), ink)
    S.box("dog.tail", (0.16, 0.06, 0.06), (1.4 + 0.25, 1.2, 0.34), dogm, bevel=0.02)

    # ================================================================ the street
    T = Stage(kit, "street", ctx)
    T.box("road", (80, 9, 0.06), (0, -7.5, 0.03), P("#7b7a98", 0.9))
    T.box("walk", (80, 2.0, 0.08), (0, -2.8, 0.04), P("#d9d4cf", 0.9))
    T.box("grass", (80, 12, 0.05), (0, 4.0, 0.025), lawn)
    T.box("lawnfront", (80, 3.0, 0.05), (0, -1.5, 0.03), P("#6cc47a", 0.95))
    cols = ["#ffb98f", "#b9a6ff", "#fff1e2", "#9fd4ff", "#ffe08a"]
    ctx["win"] = {}
    ctx["win_mats"] = {}
    for hi, hx in enumerate(HOUSES):
        c = cols[hi]
        T.box(f"h{hi}", (6.2, 5.0, 4.2), (hx, 2.5, 2.1), P(c), bevel=0.04)
        T.box(f"h{hi}.roof", (6.8, 5.6, 0.3), (hx, 2.5, 4.35), P("#8d6aa8" if hi % 2 else "#c4473a"), bevel=0.04)
        T.box(f"h{hi}.porch", (2.0, 1.5, 0.25), (hx, -0.75, 0.125), P("#d9d4cf"), bevel=0.03)
        T.box(f"h{hi}.door", (0.95, 0.08, 2.0), (hx, -0.04, 1.0), redd if hi == 2 else P("#5a8f6a"), bevel=0.02)
        T.box(f"h{hi}.lamp", (0.18, 0.18, 0.24), (hx + 0.9, -0.1, 2.3), kit.emit("#ffd18a", 2.4, "porch"))
        for wi, (wx, wz) in enumerate(((-1.9, 1.5), (-1.9, 3.3), (1.9, 3.3), (1.9, 1.5))):
            if hi == 2 and wi == 0:
                lit_default = True
            lit_m = kit.emit("#ffd18a", 1.6, "winlit")
            dark_m = kit.emit("#4a5aa8", 0.5, "windark")
            w = T.box(f"h{hi}.w{wi}", (1.1, 0.06, 1.0), (hx + wx * (1 if hi != 2 else 1), -0.03, wz), dark_m)
            T.box(f"h{hi}.wf{wi}", (1.3, 0.04, 1.2), (hx + wx, -0.01, wz), white)
            ctx["win"][(hi, wi)] = w
        ctx["win_mats"] = {"lit": lit_m, "dark": dark_m}
    # the rooster on Mr. Pruitt's roof
    rx = HOUSES[3]
    rm = P("#e08a2e")
    base = 4.5
    T.box("roo.body", (0.62, 0.42, 0.42), (rx, 2.0, base + 0.21), rm, bevel=0.1)
    T.box("roo.neck", (0.2, 0.2, 0.36), (rx, 1.75, base + 0.5), rm, bevel=0.06)
    T.box("roo.head", (0.28, 0.26, 0.26), (rx, 1.68, base + 0.76), rm, bevel=0.08)
    for k_ in range(3):
        T.box(f"roo.comb{k_}", (0.06, 0.1, 0.1), (rx, 1.68 + (k_ - 1) * 0.08, base + 0.96), redd)
    T.box("roo.beak", (0.08, 0.14, 0.07), (rx, 1.5, base + 0.74), butter)
    T.box("roo.wattle", (0.05, 0.05, 0.1), (rx, 1.52, base + 0.64), redd)
    for sg in (-1, 1):
        T.box(f"roo.eye{sg}", (0.03, 0.03, 0.04), (rx + sg * 0.14, 1.58, base + 0.8), ink)
        T.box(f"roo.wing{sg}", (0.06, 0.34, 0.24), (rx + sg * 0.34, 2.0, base + 0.22), P("#b8651f"), bevel=0.04)
    for k_, (dz, cc) in enumerate(((0.5, "#2d6a5a"), (0.64, "#3a8f7a"), (0.4, "#2a5aa0"))):
        T.box(f"roo.tail{k_}", (0.08, 0.18, 0.4), (rx + (k_ - 1) * 0.08, 2.35, base + dz), P(cc), rot=(math.radians(-25), 0, 0), bevel=0.03)
    # the car
    car = kit.empty("car", T.p((-20, -7.0, 0)))
    kit.box("car.body", (1.8, 4.0, 0.7), (0, 0, 0.55), P("#4fc3c8"), car, bevel=0.1)
    kit.box("car.cab", (1.5, 2.0, 0.6), (0, -0.2, 1.15), P("#4fc3c8"), car, bevel=0.1)
    kit.box("car.glass", (1.52, 1.6, 0.4), (0, -0.2, 1.2), P("#bfe0ff"), car, bevel=0.05)
    for sx_ in (-0.95, 0.95):
        for sy_ in (-1.2, 1.2):
            kit.cyl(f"car.w{sx_}{sy_}", 0.3, 0.2, (sx_, sy_, 0.3), ink, car, rot=(0, math.pi / 2, 0), n=16)
    for sg in (-0.6, 0.6):
        kit.box(f"car.hl{sg}", (0.3, 0.06, 0.2), (sg, 2.0, 0.6), kit.emit("#fff6c8", 4.0, "headlight"), car)
    ctx["car"] = car
    # a mower and a flashlight for Mr. Pruitt
    mow = kit.empty("mower", T.p((HOUSES[3] - 1.2, -2.0, 0)))
    kit.box("mow.body", (0.6, 0.8, 0.3), (0, 0, 0.3), redd, mow, bevel=0.05)
    kit.box("mow.handle", (0.6, 0.05, 0.05), (0, 0.55, 1.0), grey, mow)
    ctx["mower"] = mow
    kit.box("flash", (0.08, 0.2, 0.08), T.p((HOUSES[3] - 0.6, -2.6, 1.0)), kit.emit("#fff6c8", 3.0, "flash"))
    T.light("flashl", "SPOT", (HOUSES[3] - 0.6, -2.6, 1.0), 120.0, "#fff2d0", spot=40, blend=0.5, size=0.1)
    kit.aim(kit.LIGHTS[f"street.flashl"]["obj"], T.p((HOUSES[3] - 1.2, -0.5, 0.0)))
    T.light("skyfill", "AREA", (0, -10, 14), 900.0, "#ffe6e0", rot=(math.radians(20), 0, 0), size=20.0)
    T.light("porch", "POINT", (0, -2.0, 3.0), 300.0, "#ffd18a", size=0.6)
    T.light("porch2", "POINT", (-12, -2.0, 3.0), 200.0, "#ffd18a", size=0.6)
    T.light("porch3", "POINT", (12, -2.0, 3.0), 200.0, "#ffd18a", size=0.6)
    ctx["st"]["street"] = T

    # dad's work gloves on the counter (our kitchen) and the beard/gloves on the cast
    S = ctx["st"]["kit"]
    gl = P("#d9a05a")
    for sg in (-1, 1):
        gx = -2.15 + sg * 0.16
        S.box(f"glove{sg}.palm", (0.14, 0.15, 0.05), (gx, 2.3, 0.975), gl, bevel=0.02)
        for fi in range(4):
            S.box(f"glove{sg}.f{fi}", (0.028, 0.11, 0.035), (gx - 0.05 + fi * 0.034, 2.43, 0.97), gl, bevel=0.01)
        S.box(f"glove{sg}.th", (0.1, 0.03, 0.035), (gx + sg * 0.1, 2.28, 0.97), gl, rot=(0, 0, math.radians(sg * 30)), bevel=0.01)
        S.box(f"glove{sg}.cuff", (0.15, 0.1, 0.06), (gx, 2.18, 0.98), P("#ff8f3a"), bevel=0.02)
    for k_ in range(3):
        S.box(f"steam{k_}", (0.05, 0.05, 0.12), (-2.25 + k_ * 0.1, 2.35, 1.1 + k_ * 0.05), kit.emit("#ffe3b0", 0.6, "steamp"), bevel=0.02)
    ctx["cast_extras"] = False
    ctx["P"] = P
    return ctx


def _extras(kit, ctx):
    """Cast dressing that needs the rigs: Dad's chin beard and work gloves."""
    P = ctx["P"]
    gl = P("#d9a05a")
    for who in ("dad", "dadr", "dady"):
        hg = bpy.data.objects.get(f"{who}.headg")
        if hg is None:
            continue
        if who != "dady":
            kit.box(f"{who}.beard", (0.86, 0.3, 0.2), (0, -0.5, -0.62), P("#8d8f98", 0.9), hg, bevel=0.08)
            kit.box(f"{who}.mst", (0.5, 0.1, 0.1), (0, -0.6, -0.3), P("#8d8f98", 0.9), hg, bevel=0.03)
        if who != "dad":
            for sx in (-1, 1):
                arm = bpy.data.objects.get(f"{who}.arm{sx}")
                if arm is not None:
                    kit.box(f"{who}.glove{sx}", (1.08, 1.08, 0.6), (0, 0, -1.72), gl, arm, bevel=0.1)
    ctx["cast_extras"] = True


def set_sky(kit, name):
    col, strength, _ = SKY[name]
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = kit.col(col)
    bg.inputs["Strength"].default_value = strength


def animate(kit, story, tl, t, ctx):
    from blocky import kit as K

    if not ctx["cast_extras"]:
        _extras(kit, ctx)
    shot, spec = shot_of(story, tl, t)
    stage = spec.get("stage", "yard")
    sky = spec.get("sky", "dawn")
    set_sky(kit, sky)
    dk = sky in ("dark", "night")
    for mat, c_day, c_dark in ((ctx["lawn_mat"], "#58b866", "#1f6a58"), (ctx["frost_mat"], "#e3eef8", "#6f86b8")):
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = kit.col(c_dark if dk else c_day)
    over = {}
    keys_on = {"key": spec.get("key", 1.0), "kfill": spec.get("kfill", 1.0)}
    over.update(keys_on)
    # per-stage lights: only the active stage's lights are drawn
    for nm, S in ctx["st"].items():
        on = nm == stage
        for ln in S.lights:
            K.LIGHTS[ln]["obj"].hide_render = not on
    # sky-dependent yard lights
    sun_far = ctx.get("sun_far", False)
    # ---- the Sun
    pos = ramp(tl, "sunpos", t, "p", list(SUN))
    sc = ramp(tl, "sunpos", t, "s", 1.0)
    face = ramp(tl, "sunpos", t, "face", 1.0)
    root = ctx["sun"]
    breathe = 1.0 + 0.012 * math.sin(2 * math.pi * t / 4.0)
    root.location = tuple(pos)
    root.scale = (sc * breathe,) * 3
    far = pos[1] > 25
    for ob in ctx["eye_parts"] + [ctx["lidg"]] + list(ctx["lidg"].children):
        ob.hide_render = face < 0.5
    eye = ramp(tl, "eye", t, "v", 0.0)
    lidg = ctx["lidg"]
    lidg.scale = (1.0, 1.0, max(0.001, 1.0 - eye))
    lidg.hide_render = face < 0.5 or eye >= 0.999
    for ob in lidg.children:
        ob.hide_render = lidg.hide_render
    g = ramp(tl, "glow", t, "v", 1.0)
    sl = ctx["st"]["yard"]
    near = ss((45.0 - pos[1]) / 25.0)
    over["yard.sunlit"] = g * near
    over["yard.sunfill"] = g * near
    # follow the Sun with its light
    kit.LIGHTS["yard.sunlit"]["obj"].location = (pos[0] + 0.3, pos[1] - 5.0 * sc, pos[2] - 0.1)
    kit.LIGHTS["yard.sunfill"]["obj"].location = (pos[0], pos[1] - 8.0 * sc, pos[2] + 1.5)
    daylevel = {"dawn": 1.0, "peach": 1.0, "day": 1.0}.get(sky, 0.0)
    over["yard.daykey"] = daylevel * ss((pos[1] - 15.0) / 25.0)
    over["yard.rim"] = 1.0 if sky in ("night", "dark") else 0.0
    over["yard.shedlamp"] = 1.0
    over["yard.stepl"] = 1.0 if sky in ("night", "dark") else 0.0
    # ---- the rope
    mode = (latest(tl, "rope", t) or {}).get("mode", "slack")
    taut = ctx["rope_taut"]
    for seg in ctx["rope_slack"]:
        seg.hide_render = mode == "taut"
    taut.hide_render = mode != "taut"
    if mode == "taut":
        a = V(PULLEY)
        b = V(pos) + V((0, -2.2 * sc if not far else -1.0, 0))
        b = V(pos) - (V(pos) - a).normalized() * (2.3 * sc)
        taut.location = tuple((a + b) / 2)
        taut.scale = (1, 1, (b - a).length)
        taut.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    # shed door ajar
    ctx["shed_door"].hide_render = False
    # ---- fridge and crank, curtains
    f = ramp(tl, "fridge", t, "v", 0.0)
    ctx["pkit.hinge"].rotation_euler = (0, 0, math.radians(105) * f)
    ctx["kit.hinge"].rotation_euler = (0, 0, 0)
    ctx["crank"].rotation_euler = (math.tau * ramp(tl, "crank", t, "v", 0.0), 0, 0)
    n = len(ctx["rope_in"])
    slack = 1.0 - ramp(tl, "tight", t, "v", 0.0)
    for i, seg in enumerate(ctx["rope_in"]):
        u0, u1 = i / n, (i + 1) / n
        a = V((0, 3.6, 1.7 + 1.5 * u0)) + V((0.12 * slack * math.sin(u0 * 6), 0, 0))
        b = V((0, 3.6, 1.7 + 1.5 * u1)) + V((0.12 * slack * math.sin(u1 * 6), 0, 0))
        a.x += OR["shed"][0]; b.x += OR["shed"][0]; a.y += OR["shed"][1]; b.y += OR["shed"][1]
        seg.location = tuple((a + b) / 2)
        seg.scale = (1, 1, (b - a).length / 0.4)
        seg.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    cv = ramp(tl, "curtain", t, "v", 0.0)
    for c, sg in ctx["curt"]:
        c.scale = (1.0 - 0.7 * cv, 1, 1)
        c.location.x = OR["bed"][0] - 0.3 + sg * (1.1 + 0.5 * cv)
    bl = ramp(tl, "blanket", t, "v", 0.0)
    ctx["blanket"].location = (OR["bed"][0] - 1.5 + 0.9 * bl, 2.85 + 0.6 * bl * 0, 0.55 + 0.35 * bl)
    ctx["blanket"].rotation_euler = (0, math.radians(-40) * bl, 0)
    pv = ramp(tl, "pillow", t, "v", 0.0)
    ctx["pillow"].location = (OR["bed"][0] - 1.5, 4.15 - 0.2 * pv, 0.56 + 0.45 * pv)
    # ---- bedroom window and street windows
    pane = SKY[sky][2]
    ctx["bedpane_em"].inputs["Color"].default_value = kit.col(pane)
    curtain_sky = sky
    lit = (latest(tl, "street", t) or {}).get("lit", "ours")
    for (hi, wi), w in ctx["win"].items():
        on = (lit == "all") or (lit == "ours" and hi == 2 and wi == 0)
        w.data.materials[0] = ctx["win_mats"]["lit" if on else "dark"]
    car = ctx["car"]
    cx = ramp(tl, "car", t, "x", -20.0)
    car.location = (OR["street"][0] + cx, -7.0, 0)
    car.rotation_euler = (0, 0, math.radians(-90))
    # ---- the clock inset, top right of the frame
    c = latest(tl, "clock", t) or {"s": "5:00", "up": 0, "ring": 0, "two": 0}
    s = "two" if ramp(tl, "clock", t, "two", 0.0) > 0.5 else c.get("s", "5:00")
    dm = ctx["disc_mats"].get(s) or ctx["disc_mats"]["5:00"]
    hud = ctx["hud"]
    lens = lens_at(story, tl, t)
    dist = 0.4
    half_h = dist * 12.0 / lens
    half_w = half_h * 9 / 16
    big = ramp(tl, "clock", t, "big", 0.0)
    dia = 0.44 * 2 * half_w * (1 + 0.5 * big)
    cxp = (0.40 - 0.2 * big) * half_w
    cyp = (0.56 - 0.1 * big) * half_h
    hud.location = (cxp, cyp, -dist)
    ring = ramp(tl, "clock", t, "ring", 0.0)
    hud.rotation_euler = (0, 0, math.radians(5.0 * ring * math.sin(t * math.tau * 2.2)))
    disc = ctx["hud_disc"]
    disc.data.materials[0] = dm
    disc.scale = (dia, dia, 1)
    up = ramp(tl, "clock", t, "up", 0.0)
    gl = ctx["hud_glyph"]
    gs = dia * 0.62
    gl.scale = (gs, gs, 1)
    gl.location = (0, dia * (0.15 + 0.35 * up), -0.0006)     # up: half a sun over the rim; down: hidden behind the face
    ctx["glyph_em"].inputs["Strength"].default_value = 1.6
    ar = ctx["hud_arcs"]
    ar.hide_render = ring < 0.5
    ar.scale = (dia * 1.5, dia, 1)
    ar.location = (0, dia * 0.1, -0.0008)
    # the real clock on the nightstand shows the same face
    ctx["rc_face"].data.materials[0] = ctx["disc_mats"].get(s) or ctx["disc_mats"]["5:00"]
    ctx["clock3d"].rotation_euler = (0, math.radians(4.0 * ring * math.sin(t * math.tau * 2.2)), 0)
    return over
