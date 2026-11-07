"""ep134 "five rooms": still sets, each at its own origin (layout.py). The hall of numbered doors is built seven times,
one still state each (which doors are open), and the edit cuts between them. Nothing grows, morphs or moves in the
set: the tenth door is already built and shut in the morning hall (M). The rule marker is the hall itself: big
teal numerals 1 to 9 on white doors. No lettering anywhere (the posters and crates carry our own glyphs).

Every extra (the duffel, the guitar, the portrait, the boxes) is made in build(). animate() only sits people down.
"""
import math
import sys
import tempfile
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
GBOOST = [1.0]    # set per hall: the last states glow harder so the doorways read in colour
LEAFCOL = {5: "#9a6ad8", 6: "#6fd9a8", 7: "#e8b83a", 8: "#a8aab2", 9: "#f4f7fa"}
LIGHT = 0.3       # one knob for how bright every steady practical light is


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


class Pl:
    """A place: everything is added at its origin and its names carry a tag, so nothing collides."""

    def __init__(self, kit, O, tag):
        self.kit, self.O, self.tag = kit, O, tag

    def p(self, loc):
        return (self.O[0] + loc[0], self.O[1] + loc[1], loc[2])

    def box(self, n, size, loc, mat, bevel=0.0, rot=(0, 0, 0), parent=None):
        return self.kit.box(f"{self.tag}.{n}", size, self.p(loc) if parent is None else loc, mat, parent, rot, bevel)

    def cyl(self, n, r, h, loc, mat, rot=(0, 0, 0), nseg=16, r2=None, parent=None):
        return self.kit.cyl(f"{self.tag}.{n}", r, h, self.p(loc) if parent is None else loc, mat, parent, rot, nseg, r2)

    def sph(self, n, r, loc, mat, seg=10, parent=None, scale=None):
        ob = self.kit.sphere(f"{self.tag}.{n}", r, self.p(loc) if parent is None else loc, mat, parent, seg)
        if scale:
            ob.scale = scale
        return ob

    def empty(self, n, loc, rot=(0, 0, 0), parent=None):
        return self.kit.empty(f"{self.tag}.{n}", self.p(loc) if parent is None else loc, parent, rot)

    def light(self, n, loc, energy, hexc="#fff2e0", size=0.8):
        return self.kit.light(f"{self.tag}.{n}", "POINT", self.p(loc), energy * LIGHT, hexc, size=size, shadow=True)

    def wall_y(self, n, x, y0, y1, z0, z1, th, mat, holes=()):
        """A wall along y at x. holes: (a0, a1, zb, zt) in y."""
        cur = y0
        for i, (a0, a1, zb, zt) in enumerate(sorted(holes)):
            if a0 > cur:
                self.box(f"{n}.f{i}", (th, a0 - cur, z1 - z0), (x, (cur + a0) / 2, (z0 + z1) / 2), mat)
            if zb > z0:
                self.box(f"{n}.b{i}", (th, a1 - a0, zb - z0), (x, (a0 + a1) / 2, (z0 + zb) / 2), mat)
            if zt < z1:
                self.box(f"{n}.t{i}", (th, a1 - a0, z1 - zt), (x, (a0 + a1) / 2, (zt + z1) / 2), mat)
            cur = a1
        if y1 > cur:
            self.box(f"{n}.e", (th, y1 - cur, z1 - z0), (x, (cur + y1) / 2, (z0 + z1) / 2), mat)

    def wall_x(self, n, y, x0, x1, z0, z1, th, mat, holes=()):
        cur = x0
        for i, (a0, a1, zb, zt) in enumerate(sorted(holes)):
            if a0 > cur:
                self.box(f"{n}.f{i}", (a0 - cur, th, z1 - z0), ((cur + a0) / 2, y, (z0 + z1) / 2), mat)
            if zb > z0:
                self.box(f"{n}.b{i}", (a1 - a0, th, zb - z0), ((a0 + a1) / 2, y, (z0 + zb) / 2), mat)
            if zt < z1:
                self.box(f"{n}.t{i}", (a1 - a0, th, z1 - zt), ((a0 + a1) / 2, y, (zt + z1) / 2), mat)
            cur = a1
        if x1 > cur:
            self.box(f"{n}.e", (x1 - cur, th, z1 - z0), ((cur + x1) / 2, y, (z0 + z1) / 2), mat)


# ----------------------------------------------------------------------------------------------- numerals
SEG = {"1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc", "8": "abcdefg",
       "9": "abcdfg"}


def seg7(add, ch, cy, cz, H, w, t):
    """A blocky digit made of bars. add(name, (su, sz), (u, z)) draws one bar, u along the door."""
    hv = H / 2
    pos = {"a": ((w, t), (0, H / 2 - t / 2)), "d": ((w, t), (0, -H / 2 + t / 2)), "g": ((w - 2 * t, t), (0, 0)),
           "b": ((t, hv), (w / 2 - t / 2, H / 4)), "c": ((t, hv), (w / 2 - t / 2, -H / 4)),
           "f": ((t, hv), (-w / 2 + t / 2, H / 4)), "e": ((t, hv), (-w / 2 + t / 2, -H / 4))}
    for s in SEG[ch]:
        sz, (x, y) = pos[s]
        add(f"seg{s}", sz, (cy + x, cz + y))


# ----------------------------------------------------------------------------------------------- the portrait
def make_portrait_png(path):
    """Me at 23: a flat framed photo. A square head, brown hair, a scruffy beard, my own drawn face, a navy hoodie."""
    from PIL import Image, ImageChops, ImageDraw
    from blocky import faces
    import random
    W, H = 640, 800
    skin_hex = "#d9ac84"
    skin = (217, 172, 132)
    im = Image.new("RGB", (W, H), (158, 190, 214))
    d = ImageDraw.Draw(im)
    for y in range(H):
        c = int(222 - 70 * y / H)
        d.line((0, y, W, y), fill=(c - 40, c - 8, min(255, c + 22)))
    d.rounded_rectangle((60, 610, 580, 860), 70, fill=(42, 58, 106))            # hoodie shoulders
    d.polygon([(250, 610), (390, 610), (320, 700)], fill=(30, 42, 80))
    d.rectangle((250, 520, 390, 640), fill=(190, 148, 110))                     # neck
    d.rounded_rectangle((128, 150, 512, 575), 74, fill=skin)                    # head
    d.ellipse((104, 330, 150, 430), fill=skin)
    d.ellipse((490, 330, 536, 430), fill=skin)
    hair = (88, 58, 34)
    d.rounded_rectangle((116, 96, 524, 262), 60, fill=hair)                     # hair
    d.rectangle((116, 200, 168, 340), fill=hair)
    d.rectangle((472, 200, 524, 340), fill=hair)
    for k in range(7):
        d.rectangle((150 + 52 * k, 235, 176 + 52 * k, 262 + 14 * (k % 3)), fill=hair)    # fringe
    beard = (92, 60, 36)
    d.polygon([(128, 360), (150, 520), (210, 585), (320, 612), (430, 585), (490, 520), (512, 360), (470, 408),
               (404, 436), (320, 420), (236, 436), (170, 408)], fill=beard)           # the beard
    rnd = random.Random(23)
    for _ in range(420):                                                       # stubble and stray bits
        x, y = rnd.randint(140, 500), rnd.randint(400, 610)
        if d.im.getpixel((x, y))[:3] == beard:
            c = rnd.choice([(120, 82, 50), (70, 44, 26)])
            d.rectangle((x, y, x + rnd.randint(2, 4), y + rnd.randint(4, 9)), fill=c)
    for k in range(6):
        x = 190 + 50 * k
        d.line((x, 585, x + rnd.randint(-14, 14), 625), fill=beard, width=6)
    d.ellipse((262, 432, 378, 492), fill=(150, 104, 70))                       # a lighter patch so the mouth reads
    tex = faces.face_image({"eyes": "round", "brows": True, "ink": "#1c120c", "brow_w": 1.7}, skin_hex, "neutral", 0.0,
                           (0.0, 0.0), 0.0)
    crop = tex.crop((faces.FX0, faces.FY0, faces.FX1, faces.FY1)).convert("RGB").resize((384, 372))
    diff = ImageChops.difference(crop, Image.new("RGB", crop.size, skin)).convert("L").point(lambda v: 255 if v > 16 else 0)
    im.paste(crop, (128, 190), diff)
    im.save(path)


def photo_material(kit, path, w, h):
    """The picture lit by itself (so it reads from the doorway), mapped by object coordinates on a thin box."""
    m = kit._new("portrait")
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(sep.outputs["Y"], comb.inputs["X"])
    nt.links.new(sep.outputs["Z"], comb.inputs["Y"])
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Location"].default_value = (0.5, 0.5, 0.0)
    mp.inputs["Scale"].default_value = (1.0 / w, 1.0 / h, 1.0)
    nt.links.new(comb.outputs[0], mp.inputs["Vector"])
    img = nt.nodes.new("ShaderNodeTexImage")
    img.extension = "EXTEND"
    img.image = bpy.data.images.load(str(path))
    img.image.colorspace_settings.name = "sRGB"
    nt.links.new(mp.outputs[0], img.inputs["Vector"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 0.55
    nt.links.new(img.outputs["Color"], em.inputs["Color"])
    kit._fogged(m, em.outputs[0])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    return m


# ----------------------------------------------------------------------------------------------- the rooms
class Room:
    """A room behind a left-wall door (side -1: depth runs to -x) or a right-wall door (side +1). d is the depth in
    from the doorway, l along the wall from the door's centre, z up."""

    def __init__(self, kit, pl, side, yc, tag, wall, floor, ceil, lit, light_col="#fff0d8", e=170, deep=3.0, half=0.95, glow=None, lamps=True, gstr=2.0):
        self.kit, self.pl, self.s, self.yc, self.t = kit, pl, side, yc, tag
        self.deep, self.half = deep, half
        x0 = side * (1.7 + 0.2)
        self.x0 = x0
        w = pl.box
        cx = x0 + side * deep / 2
        w(f"{tag}.floor", (deep + 0.3, 2 * half + 0.2, 0.1), (cx + side * 0.1, yc, -0.05), floor)
        w(f"{tag}.ceil", (deep + 0.3, 2 * half + 0.2, 0.1), (cx + side * 0.1, yc, G.HALL_H + 0.05), ceil)
        w(f"{tag}.far", (0.2, 2 * half + 0.2, G.HALL_H), (x0 + side * (deep + 0.1), yc, G.HALL_H / 2), wall)
        for sy in (-1, 1):
            w(f"{tag}.side{sy}", (deep + 0.3, 0.1, G.HALL_H), (cx + side * 0.1, yc + sy * (half + 0.05), G.HALL_H / 2), wall)
        if glow:      # lit panels on the inner faces and a ceiling glow, so a doorway seen from the hall is never black
            gm = kit.emit(glow, gstr * GBOOST[0], f"{tag}.wallglow")
            xi = x0 + side * (deep - 0.03)
            w(f"{tag}.gfar", (0.02, 2 * half - 0.02, G.HALL_H - 0.3), (xi, yc, G.HALL_H / 2), gm)
            for sy in (-1, 1):
                w(f"{tag}.gside{sy}", (deep - 0.3, 0.02, G.HALL_H - 0.3), (x0 + side * (deep / 2 + 0.1), yc + sy * (half - 0.03), G.HALL_H / 2), gm)
            w(f"{tag}.gceil", (1.2, 0.8, 0.03), (x0 + side * deep * 0.55, yc, G.HALL_H - 0.03), kit.emit("#fff0c8", 1.4, "ceilglow"))
        e = e * 3.5     # bright enough to read through the doorway from the hall
        if lamps:
            pl.light(f"{tag}.lamp", (x0 + side * deep * 0.55, yc, 2.3), e, light_col, size=0.9)
            pl.light(f"{tag}.lamp2", (x0 + side * 0.9, yc, 1.9), e * 0.5, light_col, size=0.6)

    def at(self, d, l, z=0.0):
        return (self.x0 + self.s * d, self.yc + l, z)

    def box(self, n, size, d, l, z, mat, bevel=0.0, rot=(0, 0, 0)):
        p = self.at(d, l, z + size[2] / 2)
        # size is given as (depth, along, height)
        return self.pl.box(f"{self.t}.{n}", (size[0], size[1], size[2]), p, mat, bevel=bevel, rot=rot)

    def poster(self, n, l, z, bg, ink, glyph):
        k, pl = self.kit, self.pl
        xf = self.x0 + self.s * (self.deep - 0.02)          # a hair proud of the far wall
        pl.box(f"{self.t}.{n}.bg", (0.04, 0.62, 0.84), (xf, self.yc + l, z), k.plastic(bg, 0.8))
        xg = xf - self.s * 0.03
        im = k.plastic(ink, 0.6)
        if glyph == 0:      # a bolt
            pl.box(f"{self.t}.{n}.g1", (0.03, 0.14, 0.4), (xg, self.yc + l + 0.07, z + 0.1), im, rot=(0, 0, 0))
            pl.box(f"{self.t}.{n}.g2", (0.03, 0.34, 0.12), (xg, self.yc + l, z - 0.02), im)
            pl.box(f"{self.t}.{n}.g3", (0.03, 0.14, 0.34), (xg, self.yc + l - 0.07, z - 0.18), im)
        elif glyph == 1:    # a ring and a dot
            pl.cyl(f"{self.t}.{n}.g1", 0.2, 0.03, (xg, self.yc + l, z + 0.06), im, rot=(0, math.pi / 2, 0), nseg=20)
            pl.cyl(f"{self.t}.{n}.g2", 0.11, 0.04, (xg + self.s * 0.0, self.yc + l, z + 0.06), k.plastic(bg, 0.8),
                   rot=(0, math.pi / 2, 0), nseg=16)
            pl.box(f"{self.t}.{n}.g3", (0.03, 0.4, 0.1), (xg, self.yc + l, z - 0.26), im)
        else:               # a big wedge and three bars
            for j in range(3):
                pl.box(f"{self.t}.{n}.g{j}", (0.03, 0.4 - 0.1 * j, 0.1), (xg, self.yc + l, z + 0.24 - 0.2 * j), im)
            pl.box(f"{self.t}.{n}.gw", (0.03, 0.1, 0.3), (xg, self.yc + l - 0.2, z - 0.18), im)


def room5(kit, pl, yc):
    purple = kit.plastic("#9a6ad8", 0.8, spec=0.05)
    r = Room(kit, pl, -1, yc, "r5", purple, kit.planks("#cbb2e8", "#bfa2e0", 1.0), kit.plastic("#e8dcf6", 0.9),
             True, "#ffe9ff", e=100, glow="#9a6ad8", gstr=1.3)
    for k, (bg, ink, g) in enumerate([("#ffd95a", "#2b1a4a", 0), ("#ff8fc8", "#2b1a4a", 1), ("#7fe0d0", "#2b1a4a", 2)]):
        r.poster(f"p{k}", -0.65 + 0.65 * k, 1.5, bg, ink, g)
    r.box("bed", (1.9, 0.9, 0.38), 2.2, -0.45, 0.0, kit.plastic("#f4e6ff", 0.8), bevel=0.04)
    r.box("bedtop", (1.9, 0.9, 0.12), 2.2, -0.45, 0.38, kit.plastic("#ff8fc8", 0.8), bevel=0.04)
    # the guitar on its floor stand, face to the door
    gx = 0.9
    dark = kit.plastic("#2a2230", 0.5, spec=0.3)
    for sy, rz in ((-1, 0.35), (1, -0.35)):
        pl.box(f"r5.gs{sy}", (0.04, 0.04, 0.5), r.at(gx, 0.28 + sy * 0.12, 0.25), dark, rot=(rz, 0, 0))
    pl.box("r5.gs3", (0.04, 0.04, 0.45), r.at(gx + 0.12, 0.28, 0.23), dark, rot=(0, 0.3, 0))
    body = kit.plastic("#e8602c", 0.35, spec=0.6)
    pl.cyl("r5.gb1", 0.22, 0.09, r.at(gx, 0.28, 0.62), body, rot=(0, math.pi / 2, 0), nseg=20)
    pl.cyl("r5.gb2", 0.16, 0.09, r.at(gx, 0.28, 0.93), body, rot=(0, math.pi / 2, 0), nseg=20)
    pl.cyl("r5.gh", 0.075, 0.1, r.at(gx - 0.0, 0.28, 0.78), dark, rot=(0, math.pi / 2, 0), nseg=16)
    pl.box("r5.gn", (0.05, 0.075, 0.62), r.at(gx, 0.28, 1.2), kit.plastic("#5a3a22", 0.5), bevel=0.01)
    pl.box("r5.gp", (0.06, 0.16, 0.26), r.at(gx, 0.28, 1.62), dark, bevel=0.015)
    r.box("rug", (1.4, 1.2, 0.02), 1.2, 0.0, 0.0, kit.plastic("#7fe0d0", 0.9))
    return r


def room6(kit, pl, yc):
    mint = kit.plastic("#9fe6c2", 0.8, spec=0.05)
    r = Room(kit, pl, -1, yc, "r6", mint, kit.planks("#e9d3a8", "#dcc596", 1.0), kit.plastic("#f2fff8", 0.9), True,
             "#f0fff6", e=90, glow="#3fcf90", gstr=1.3)
    wood = kit.plastic("#b98a56", 0.6)
    # a bunk bed along the far wall
    for k, (z, c) in enumerate(((0.45, "#ff8fa8"), (1.25, "#6fb4ff"))):
        r.box(f"mat{k}", (1.9, 0.95, 0.2), 1.7, 0.0, z, kit.plastic(c, 0.8), bevel=0.03)
        r.box(f"matb{k}", (1.9, 0.95, 0.05), 1.7, 0.0, z - 0.06, wood)
    for dd in (0.8, 2.6):
        for dl in (-0.5, 0.5):
            r.box(f"post{dd}{dl}", (0.08, 0.08, 1.75), dd, dl, 0.0, wood)
    r.box("ladder", (0.05, 0.4, 1.25), 0.82, 0.0, 0.0, wood)
    # stacked crates
    crate = kit.plastic("#d9a86a", 0.8, spec=0.05)
    slat = kit.plastic("#b98a56", 0.8)
    for k, (dd, dl, z) in enumerate(((0.55, 0.62, 0.0), (0.55, 0.62, 0.5), (0.5, -0.1, 0.0))):
        r.box(f"crate{k}", (0.5, 0.5, 0.48), dd, dl, z, crate, bevel=0.012)
        r.box(f"cr_s{k}", (0.52, 0.52, 0.07), dd, dl, z + 0.2, slat, bevel=0.01)
    pl.sph("r6.bean", 0.38, r.at(1.4, -0.55, 0.28), kit.plastic("#ff7a5c", 0.9), scale=(1.0, 1.0, 0.7))
    return r


def room7(kit, pl, yc, dark=False):
    mus = kit.plastic("#e8b83a", 0.8, spec=0.05)
    r = Room(kit, pl, -1, yc, "r7", mus, kit.planks("#f0d9a0", "#e6cb8c", 1.0), kit.plastic("#fff5d8", 0.9), True,
             "#fff0c8", e=200, glow="#e8b83a")
    if dark:     # a black backing inside the doorway, so the gap at the latch side reads as a dark slit
        pl.box("r7.void", (0.04, 1.0, 2.15), (r.x0 - 0.3, yc, 1.075), kit.plastic("#030303", 0.9, spec=0.0))
    r.box("bed", (1.9, 0.9, 0.38), 1.6, 0.55, 0.0, kit.plastic("#fff6e4", 0.8), bevel=0.04)
    r.box("bedtop", (1.9, 0.9, 0.12), 1.6, 0.55, 0.38, kit.plastic("#2fb8a8", 0.8), bevel=0.04)
    r.box("rug", (1.6, 1.3, 0.02), 1.7, -0.1, 0.0, kit.plastic("#b04a6a", 0.9))
    # the big framed portrait on the far wall, as big as a window
    png = Path(tempfile.gettempdir()) / "ep134-portrait.png"
    try:
        make_portrait_png(png)
        mat = photo_material(kit, png, 1.5, 1.88)
    except Exception:
        mat = kit.plastic("#9bb7d2", 0.8)
    xf = r.x0 - (r.deep - 0.1)
    frame = kit.plastic("#5a3a22", 0.5, spec=0.3)
    zc = 1.5
    pl.box("r7.frame", (0.08, 1.74, 2.12), (xf + 0.02, yc, zc), frame, bevel=0.015)
    pl.box("r7.photo", (0.04, 1.5, 1.88), (xf + 0.09, yc, zc), mat)
    return r


def room8(kit, pl, yc):
    gray = kit.plastic("#a8aab2", 0.85, spec=0.05)
    r = Room(kit, pl, -1, yc, "r8", gray, kit.planks("#c9c4bc", "#bdb8b0", 1.0), kit.plastic("#eceef2", 0.9), True,
             "#f4f4ff", e=90, glow="#a0a2b0", gstr=1.0)
    card = kit.plastic("#d9a86a", 0.85, spec=0.05)
    card2 = kit.plastic("#c99456", 0.85, spec=0.05)
    tape = kit.plastic("#4a3320", 0.6)
    k = 0
    for (dd, dl, z, sz, rot) in ((0.7, 0.55, 0.0, 0.62, 0.05), (0.75, -0.4, 0.0, 0.7, -0.04), (0.7, 0.55, 0.62, 0.55, -0.06),
                                 (0.75, -0.4, 0.7, 0.5, 0.05), (1.7, 0.5, 0.0, 0.7, 0.03), (1.65, 0.5, 0.7, 0.6, -0.04),
                                 (1.7, -0.5, 0.0, 0.65, -0.03), (2.5, 0.3, 0.0, 0.8, 0.0), (2.5, -0.5, 0.0, 0.7, 0.04),
                                 (2.45, 0.3, 0.8, 0.6, 0.03), (1.7, -0.5, 0.65, 0.5, 0.06)):
        r.box(f"bx{k}", (sz, sz, sz), dd, dl, z, card if k % 2 else card2, bevel=0.012, rot=(0, 0, rot))
        r.box(f"bt{k}", (sz + 0.05, 0.1, sz + 0.05), dd, dl, z - 0.025, tape, rot=(0, 0, rot))
        r.box(f"bu{k}", (sz + 0.05, sz + 0.05, 0.03), dd, dl, z + sz, tape, rot=(0, 0, rot))      # a strip along the top too
        k += 1
    return r


def room9(kit, pl, yc):
    white = kit.plastic("#f4f7fa", 0.85, spec=0.05)
    r = Room(kit, pl, -1, yc, "r9", white, kit.planks("#bcd6ee", "#b0cde8", 1.0), kit.plastic("#ffffff", 0.9), True,
             "#f0f6ff", e=100, glow="#f4f7fa", gstr=1.2)
    dk = kit.plastic("#3a4150", 0.5, spec=0.3)
    r.box("tbase", (1.6, 0.6, 0.18), 1.7, 0.4, 0.0, dk, bevel=0.03)
    r.box("belt", (1.5, 0.5, 0.05), 1.7, 0.4, 0.18, kit.plastic("#222630", 0.6), bevel=0.01)
    r.box("rail1", (0.06, 0.06, 1.15), 2.4, 0.12, 0.0, dk)
    r.box("rail2", (0.06, 0.06, 1.15), 2.4, 0.68, 0.0, dk)
    r.box("cons", (0.14, 0.7, 0.3), 2.4, 0.4, 1.05, kit.plastic("#ff7a5c", 0.5), bevel=0.02)
    r.box("bed", (1.9, 0.9, 0.38), 1.6, -0.5, 0.0, kit.plastic("#ffffff", 0.8), bevel=0.04)
    r.box("bedtop", (1.9, 0.9, 0.1), 1.6, -0.5, 0.38, kit.plastic("#9bc4e8", 0.8), bevel=0.04)
    pot = kit.plastic("#d9784a", 0.7)
    pl.cyl("r9.pot", 0.18, 0.32, r.at(0.75, 0.6, 0.16), pot, nseg=12)
    green = kit.plastic("#3fae5a", 0.7)
    for k in range(6):
        a = k * math.pi / 3
        pl.box(f"r9.lf{k}", (0.08, 0.1, 0.5), r.at(0.75 + 0.1 * math.cos(a), 0.6 + 0.1 * math.sin(a), 0.6), green,
               rot=(0.4 * math.sin(a), -0.4 * math.cos(a), a * 0.3), bevel=0.02)
    return r


def room_small(kit, pl, side, yc, tag, wall, bed_col, e=140, deep=2.6):
    r = Room(kit, pl, side, yc, tag, kit.plastic(wall, 0.85), kit.planks("#e8cfa6", "#dcc096", 1.0),
             kit.plastic("#fff8ec", 0.9), True, "#ffe2b0", e=e, deep=deep, glow=wall)
    r.box("bed", (1.9, 0.9, 0.38), 1.3, 0.4, 0.0, kit.plastic("#fff6e4", 0.8), bevel=0.04)
    r.box("bedtop", (1.9, 0.9, 0.12), 1.3, 0.4, 0.38, kit.plastic(bed_col, 0.8), bevel=0.04)
    r.box("rug", (1.2, 1.0, 0.02), 1.2, -0.3, 0.0, kit.plastic("#fff0c0", 0.9))
    return r


# ----------------------------------------------------------------------------------------------- the hall
def build_hall(kit, key):
    spec = G.HALLS[key]
    O = G.HALL_O[key]
    pl = Pl(kit, O, f"h{key}")
    morning = bool(spec.get("morning"))
    GBOOST[0] = 1.7 if key in ("F", "M") else 1.0
    opens = spec["o"]
    W_ = G.HALL_W / 2
    Y0, Y1, H = -3.0, G.HALL_L, G.HALL_H
    wall = kit.plastic("#f6c4a2", 0.85, spec=0.05)
    cream = kit.plastic("#f3e6cc", 0.85, spec=0.05)
    door_m = kit.plastic("#fbfaf6", 0.55, spec=0.2)
    teal = kit.plastic("#1fa39a", 0.5, spec=0.3)
    brass = kit.plastic("#e3b04b", 0.3, spec=0.8)
    # floor, runner rug, ceiling
    pl.box("floor", (G.HALL_W + 0.4, Y1 - 0.6 + 0.2, 0.1), (0, (Y1 + 0.6) / 2, -0.05), kit.planks("#c99a62", "#b88a54", 1.0))
    pl.box("rug", (1.3, Y1 - 1.2, 0.02), (0, (Y1 + 0.9) / 2, 0.01), kit.plastic("#f3e6cc", 0.9, spec=0.02))
    pl.box("rugedge", (1.4, Y1 - 1.2, 0.015), (0, (Y1 + 0.9) / 2, 0.008), kit.plastic("#d9b08a", 0.9, spec=0.02))
    pl.box("ceil", (G.HALL_W + 0.4, Y1 - Y0 + 0.2, 0.1), (0, (Y0 + Y1) / 2, H + 0.05), kit.plastic("#fbf3e4", 0.9, spec=0.02))
    # the stairwell: the floor ends at y 0.6, a banister, steps going down to a warm landing wall
    pl.box("stairwall", (G.HALL_W + 0.4, 0.2, H), (0, Y0 - 0.1, H / 2), kit.plastic("#f0b890", 0.85))
    pl.box("well", (G.HALL_W + 0.4, 3.0, 0.1), (0, -1.4, -0.9), kit.plastic("#d9b08a", 0.9))
    for k in range(4):
        pl.box(f"step{k}", (G.HALL_W, 0.4, 0.2), (0, 0.4 - 0.4 * k, -0.1 - 0.2 * k), kit.plastic("#c99a62", 0.8))
    rail = kit.plastic("#8a5a34", 0.5, spec=0.3)
    pl.box("handrail", (G.HALL_W, 0.07, 0.06), (0, 0.7, 1.0), rail)
    for k in range(9):
        pl.box(f"bal{k}", (0.05, 0.05, 0.95), (-1.5 + k * 0.375, 0.7, 0.5), rail)
    # the walls. Left (x -1.7): the doors 5 to 9 (and the tenth, in the morning); right: doors 1 to 4
    lh = [(y - 0.5, y + 0.5, 0.0, 2.15) for n, y in G.DOORY.items() if n < 10 or morning]
    rh = [(y - 0.5, y + 0.5, 0.0, 2.15) for y in G.RDOORY.values()]
    pl.wall_y("wl", G.LX - 0.1, Y0, Y1, 0, H, 0.2, wall, holes=lh)
    pl.wall_y("wr", G.RX + 0.1, Y0, Y1, 0, H, 0.2, wall, holes=rh)
    # the end wall with the window
    wx0, wx1 = -0.5, 1.1
    pl.wall_x("we", Y1 + 0.1, -W_ - 0.2, W_ + 0.2, 0, H, 0.2, wall, holes=[(wx0, wx1, 0.8, 2.3)])
    sky = kit.emit("#ffe6a0", 0.6, "sunsky") if morning else kit.emit("#5b6bb8", 1.0, "nightsky")
    pl.box("sky", (wx1 - wx0 + 0.2, 0.05, 1.6), ((wx0 + wx1) / 2, Y1 + 0.35, 1.55), sky)
    fw = kit.plastic("#ffffff", 0.6, spec=0.1)
    for nm, sz, lc in (("t", (wx1 - wx0 + 0.16, 0.14, 0.08), ((wx0 + wx1) / 2, Y1 - 0.02, 2.31)),
                       ("b", (wx1 - wx0 + 0.3, 0.26, 0.07), ((wx0 + wx1) / 2, Y1 - 0.06, 0.79)),
                       ("l", (0.07, 0.14, 1.5), (wx0 - 0.0, Y1 - 0.02, 1.55)), ("r", (0.07, 0.14, 1.5), (wx1, Y1 - 0.02, 1.55)),
                       ("m", (0.05, 0.14, 1.5), ((wx0 + wx1) / 2, Y1 - 0.02, 1.55))):
        pl.box(f"win{nm}", sz, lc, fw)
    # doors: the leaf hangs on a hinge, so an open door is just a different still state
    trim = kit.plastic("#fffdf4", 0.6, spec=0.1)

    def door(n, yc, left, ang, num=True, extra_open=True, lw=0.95, tint=None):
        xh = G.LX - 0.03 if left else G.RX + 0.03
        yh = yc - 0.475 if left else yc + 0.475
        hinge = pl.empty(f"hinge{n}", (xh, yh, 0.0), rot=(0, 0, ang * D2R))
        cy = lw / 2 if left else -lw / 2
        pl.box(f"leaf{n}", (0.05, lw, 2.1), (0, cy, 1.05), door_m, bevel=0.012, parent=hinge)
        fx = 0.0475 if left else -0.0475           # local x of the hall face's trim
        ky = (lw - 0.1) if left else -(lw - 0.1)
        pl.sph(f"knob{n}", 0.05, (fx * 1.6 + (0.02 if left else -0.02), ky, 1.0), brass, parent=hinge)
        if tint:       # an open door's room face is painted in its room's colour, so it reads from down the hall
            pl.box(f"paint{n}", (0.01, lw, 2.1), (-0.04 if left else 0.04, cy, 1.05), kit.plastic(tint, 0.8, spec=0.05), parent=hinge)
        if num:
            # digit bars: u runs along the door's face as the viewer reads it left to right
            def add(name, size, uz):
                u = uz[0]
                pl.box(f"n{n}.{name}", (0.025, size[0], size[1]), (fx, cy + (u if left else -u), uz[1]), teal, parent=hinge)
            seg7(add, str(n), 0.0, 1.62, 0.5, 0.3, 0.085)
        return hinge

    # frames (proud of the wall face by a hair so nothing shares a plane)
    for n, y in G.DOORY.items():
        if n == 10 and not morning:
            continue
        for sy in (-1, 1):
            pl.box(f"fl{n}{sy}", (0.05, 0.07, 2.2), (G.LX + 0.025, y + sy * 0.535, 1.1), trim)
        pl.box(f"fh{n}", (0.05, 1.14, 0.08), (G.LX + 0.025, y, 2.19), trim)
    for n, y in G.RDOORY.items():
        for sy in (-1, 1):
            pl.box(f"fr{n}{sy}", (0.05, 0.07, 2.2), (G.RX - 0.025, y + sy * 0.535, 1.1), trim)
        pl.box(f"frh{n}", (0.05, 1.14, 0.08), (G.RX - 0.025, y, 2.19), trim)
    rooms = {}
    for n in (5, 6, 7, 8, 9):
        ang = opens.get(n, 0)
        door(n, G.DOORY[n], True, ang, lw=0.84 if (n == 7 and 0 < ang < 30) else 0.95,
             tint=None)      # ajar: a leaf a hand narrower, a dark slit at the latch
        if ang >= 60:      # an open door hides its numeral, so the same numeral stands on the wall above the frame
            def addw(name, size, uz, n=n):
                pl.box(f"pn{n}.{name}", (0.025, size[0], size[1]), (G.LX + 0.0225, G.DOORY[n] + uz[0], uz[1]), teal)
            seg7(addw, str(n), 0.0, 2.55, 0.34, 0.22, 0.06)
        if ang >= 60 and key in ("F", "M"):      # a pool of the room's light on the hall floor, steady, 1 cm proud
            pl.box(f"pool{n}", (1.0, 1.0, 0.012), (G.LX + 0.55, G.DOORY[n], 0.006), kit.emit(LEAFCOL[n], 0.9, f"pool{n}"))
        if ang:
            if n == 7:
                rooms[n] = room7(kit, pl, G.DOORY[n], dark=ang < 30)      # ajar: a dark room, so the gap reads as a dark slit
            else:
                rooms[n] = {5: room5, 6: room6, 8: room8, 9: room9}[n](kit, pl, G.DOORY[n])
    if 0 < opens.get(7, 0) < 30:      # door seven ajar: a steady mustard spill on the hall floor from the gap (1 cm proud)
        pl.box("spill", (0.9, 0.32, 0.012), (G.LX + 0.55, G.DOORY[7] + 0.42, 0.006), kit.emit("#e8b83a", 1.1, "spill"))
        pl.box("spill2", (0.5, 0.16, 0.012), (G.LX + 1.2, G.DOORY[7] + 0.42, 0.006), kit.emit("#e8b83a", 0.6, "spill2"))
    if morning:
        door(10, G.DOORY[10], True, 0, num=False)
    # the right-hand doors: 1 to 3 open a crack on warm rooms, 4 open on the sky blue one
    rcol = {1: ("#ffd9a8", "#f08aa8"), 2: ("#ffe0b0", "#7fe0d0"), 3: ("#ffe8c0", "#b9a4f0")}
    for n, y in G.RDOORY.items():
        door(n, y, False, 22 if n < 4 else 78)
        if n == 4:
            r = Room(kit, pl, 1, y, "r4", kit.plastic("#8ec9f2", 0.85), kit.planks("#e8cfa6", "#dcc096", 1.0),
                     kit.plastic("#f4fbff", 0.9), True, "#f0f8ff", e=190, glow="#8ec9f2")
            r.box("bed", (1.9, 0.9, 0.38), 1.3, 0.4, 0.0, kit.plastic("#fff6e4", 0.8), bevel=0.04)
            r.box("bedtop", (1.9, 0.9, 0.12), 1.3, 0.4, 0.38, kit.plastic("#ff7a5c", 0.8), bevel=0.04)
            r.box("rug", (1.2, 1.0, 0.02), 1.2, -0.3, 0.0, kit.plastic("#fff0c0", 0.9))
        else:
            room_small(kit, pl, 1, y, f"r{n}", rcol[n][0], rcol[n][1])
    # the lamps: warm, steady, shadowed so a lit room doesn't spill through a wall
    warm = "#ffe3a8"
    for k, y in enumerate((1.5, 5.0, 8.5, 12.0)):
        pl.box(f"glow{k}", (0.9, 0.5, 0.04), (0, y, H - 0.02), kit.emit("#fff0c8", 1.4, "ceilglow"))
        pl.light(f"c{k}", (0, y, H - 0.35), 260, warm, size=0.9)
    pl.light("f1", (0.6, 2.2, 1.9), 150, "#fff0d8", size=1.0)
    pl.light("f2", (-0.4, 5.8, 2.0), 150, "#fff0d8", size=1.0)
    pl.light("f3", (0.5, 9.6, 2.0), 150, "#fff0d8", size=1.0)
    pl.light("stair", (0, -1.5, 2.3), 160, "#ffe3a8", size=0.9)
    if morning:
        pl.light("sun", (0.3, G.HALL_L - 0.5, 1.9), 420, "#fff0b8", size=0.9)
        pl.light("sun2", (0.3, G.HALL_L - 2.5, 2.1), 220, "#fff0b8", size=0.9)
    else:
        pl.light("win", (0.3, G.HALL_L - 0.6, 1.8), 70, "#9db0ff", size=0.8)
    return pl


# ----------------------------------------------------------------------------------------------- the other places
def glow_window(kit, pl, n, x, y, z, w, h, col="#ffe08a", axis="y"):
    fw = kit.plastic("#ffffff", 0.6, spec=0.1)
    if axis == "y":
        pl.box(f"{n}.f", (w + 0.16, 0.08, h + 0.16), (x, y - 0.03, z), fw)
        pl.box(f"{n}.g", (w, 0.05, h), (x, y - 0.075, z), kit.emit(col, 1.2, "winglow"))
        pl.box(f"{n}.m1", (0.05, 0.06, h), (x, y - 0.09, z), fw)
        pl.box(f"{n}.m2", (w, 0.06, 0.05), (x, y - 0.09, z), fw)


def ground(kit, pl, col, w=40, d=40, y0=-14):
    pl.box("ground", (w, d, 0.2), (0, y0 + d / 2, -0.1), kit.plastic(col, 0.9, spec=0.02))


def build_house(kit):
    pl = Pl(kit, G.HOUSE, "hs")
    ground(kit, pl, "#8ed67a")
    pl.box("path", (1.2, 6.0, 0.03), (0, -1.0, 0.015), kit.plastic("#f1e2c6", 0.9))
    pl.box("wall", (7.0, 0.3, 3.2), (0, 2.15, 1.6), kit.plastic("#fff0cf", 0.85, spec=0.05))
    pl.box("roof", (7.6, 1.6, 0.25), (0, 2.1, 3.3), kit.plastic("#d9604a", 0.8))
    pl.box("roof2", (7.6, 1.2, 0.2), (0, 2.5, 3.65), kit.plastic("#c8503c", 0.8))
    pl.box("step", (1.6, 0.8, 0.12), (0, 1.6, 0.06), kit.plastic("#d9d2c4", 0.9))
    pl.box("door", (1.0, 0.08, 2.1), (0, 1.97, 1.05), kit.plastic("#2fb8a8", 0.6, spec=0.2), bevel=0.02)
    pl.box("door_f", (1.2, 0.06, 2.3), (0, 1.99, 1.15), kit.plastic("#ffffff", 0.7))
    pl.sph("knob", 0.05, (0.34, 1.9, 1.0), kit.plastic("#e3b04b", 0.3, spec=0.8))
    glow_window(kit, pl, "w1", -2.2, 2.0, 1.55, 1.1, 1.3)
    glow_window(kit, pl, "w2", 2.2, 2.0, 1.55, 1.1, 1.3)
    for k, c in enumerate(("#ff8fc8", "#ffd95a", "#ff7a5c")):
        pl.box(f"fl{k}", (0.5, 0.35, 0.25), (-1.2 + 0.0 + 2.4 * (k % 2) * 0 + (-1.3 if k == 0 else 1.3 if k == 1 else 3.0), 1.7, 0.12),
               kit.plastic(c, 0.8))
    pl.light("sun", (-3.0, -4.0, 5.0), 1100, "#fff3d8", size=1.5)
    pl.light("fill", (2.5, -3.0, 2.2), 380, "#fff3e0", size=1.2)
    pl.light("face", (0.0, -2.0, 1.9), 320, "#fff3e0", size=1.0)


def build_board(kit):
    pl = Pl(kit, G.BOARD, "bh")
    ground(kit, pl, "#7fcf6a", w=80, d=60, y0=-20)
    pl.box("hill", (80, 22, 1.4), (0, 13, 0.7), kit.plastic("#6cc45c", 0.9))      # a flat terrace the house stands on
    wallc = kit.plastic("#f4e2c0", 0.85, spec=0.05)
    pl.box("bld", (34, 3.0, 6.0), (0, 9.0, 4.4), wallc)
    pl.box("bldbase", (34, 3.1, 1.6), (0, 9.0, 0.7), kit.plastic("#b9a58a", 0.9))
    pl.box("bld2", (34, 3.2, 0.4), (0, 9.0, 7.5), kit.plastic("#c8503c", 0.8))
    pl.box("tower", (4.0, 3.2, 3.6), (-3.0, 9.0, 9.1), wallc)
    pl.box("towerroof", (4.6, 3.6, 0.5), (-3.0, 9.0, 11.1), kit.plastic("#c8503c", 0.8))
    for r in range(3):
        for c in range(17):
            x = -15.0 + 1.9 * c
            glow_window(kit, pl, f"w{r}_{c}", x, 7.45, 2.4 + 1.8 * r, 0.9, 1.0, "#ffe08a" if (r + c) % 3 else "#bfe6ff")
    pl.light("sun", (-8.0, -3.0, 14.0), 3500, "#fff3d8", size=2.0)
    pl.light("fill", (6.0, 0.0, 6.0), 2600, "#fff6e8", size=2.0)


def build_theo(kit):
    pl = Pl(kit, G.THEO, "th")
    wall = kit.plastic("#ffe9a8", 0.85, spec=0.05)
    pl.box("floor", (6.0, 8.0, 0.1), (0, 2.0, -0.05), kit.plastic("#8a94b0", 0.9))
    pl.box("rug", (1.6, 6.0, 0.02), (0, 2.0, 0.01), kit.plastic("#f08aa8", 0.9))
    pl.box("ceil", (6.0, 8.0, 0.1), (0, 2.0, 2.85), kit.plastic("#fbf3e4", 0.9))
    pl.box("back", (6.0, 0.2, 2.8), (0, 4.0, 1.4), wall)
    for sx in (-1, 1):
        pl.box(f"side{sx}", (0.2, 8.0, 2.8), (sx * 3.0, 2.0, 1.4), wall)
    pl.box("front", (6.0, 0.2, 2.8), (0, -2.0, 1.4), wall)
    old = kit.plastic("#7a5a42", 0.6, spec=0.2)
    for x in (-2.2, -0.6, 2.2):
        pl.box(f"old{x}", (0.9, 0.08, 2.1), (x, 3.88, 1.05), old, bevel=0.02)
        pl.box(f"oldf{x}", (1.1, 0.04, 2.3), (x, 3.9, 1.15), kit.plastic("#fff8ec", 0.7))
        pl.sph(f"oldk{x}", 0.045, (x + 0.34, 3.82, 1.0), kit.plastic("#b0a090", 0.4, spec=0.6))
    pl.box("newf", (1.14, 0.05, 2.3), (1.0, 3.9, 1.15), kit.plastic("#ffd95a", 0.7))
    pl.box("new", (0.95, 0.08, 2.1), (1.0, 3.84, 1.05), kit.plastic("#ffffff", 0.35, spec=0.5), bevel=0.02)
    pl.sph("newk", 0.055, (1.34, 3.78, 1.0), kit.plastic("#e3b04b", 0.3, spec=0.8))
    for k, y in enumerate((0.0, 3.0)):
        pl.box(f"glow{k}", (0.9, 0.5, 0.04), (0, y, 2.83), kit.emit("#fff0c8", 1.4, "ceilglow"))
        pl.light(f"c{k}", (0, y, 2.4), 300, "#fff0d0", size=0.9)
    pl.light("face", (0.6, 0.0, 1.9), 220, "#fff6e8", size=1.0)


def build_kitchen(kit):
    pl = Pl(kit, G.KIT, "kc")
    wall = kit.plastic("#fff0cf", 0.85, spec=0.05)
    pl.box("floor", (7.0, 7.0, 0.1), (0, 1.5, -0.05), kit.planks("#e8cfa6", "#dcc096", 1.0))
    pl.box("ceil", (7.0, 7.0, 0.1), (0, 1.5, 2.85), kit.plastic("#fbf3e4", 0.9))
    pl.box("back", (7.0, 0.2, 2.8), (0, 4.0, 1.4), wall)
    for sx in (-1, 1):
        pl.box(f"side{sx}", (0.2, 7.0, 2.8), (sx * 3.5, 1.5, 1.4), wall)
    pl.box("front", (7.0, 0.2, 2.8), (0, -2.0, 1.4), wall)
    teal = kit.plastic("#2fb8a8", 0.5, spec=0.2)
    cream = kit.plastic("#fff6e4", 0.5, spec=0.2)
    pl.box("cab", (4.2, 0.7, 0.9), (-0.8, 3.55, 0.45), teal, bevel=0.02)
    pl.box("top", (4.3, 0.8, 0.06), (-0.8, 3.55, 0.93), cream, bevel=0.02)
    pl.box("upcab", (4.2, 0.4, 0.8), (-0.8, 3.7, 2.1), teal, bevel=0.02)
    pl.box("fridge", (0.9, 0.7, 1.9), (2.2, 3.55, 0.95), kit.plastic("#ffd95a", 0.45, spec=0.35), bevel=0.04)
    # the table (round) and two chairs; June sits behind it
    pl.cyl("table", 0.8, 0.06, (0, 1.9, 0.74), kit.plastic("#c58b57", 0.5, spec=0.2), nseg=24)
    pl.cyl("tleg", 0.07, 0.72, (0, 1.9, 0.36), kit.plastic("#c58b57", 0.5), nseg=10)
    for sx in (-1, 1):
        pl.box(f"ch{sx}", (0.45, 0.45, 0.06), (sx * 0.0 + (1.0 if sx > 0 else -1.0), 2.3, 0.44), kit.plastic("#f08aa8", 0.6))
        pl.box(f"chb{sx}", (0.06, 0.45, 0.5), (sx * 0.0 + (1.2 if sx > 0 else -1.2), 2.3, 0.7), kit.plastic("#f08aa8", 0.6))
    pl.box("chj", (0.5, 0.45, 0.06), (0.0, 2.75, 0.44), kit.plastic("#f08aa8", 0.6))
    pl.box("chjb", (0.5, 0.06, 0.5), (0.0, 2.95, 0.7), kit.plastic("#f08aa8", 0.6))
    for k, c in enumerate(("#ff7a5c", "#ffd95a", "#7cc4ff")):
        pl.box(f"pic{k}", (0.5, 0.04, 0.7), (-1.9 + 0.65 * k, 3.88, 1.75), kit.plastic(c, 0.7))
    pl.cyl("bowl", 0.18, 0.1, (0.1, 1.7, 0.8), kit.plastic("#ff7a5c", 0.5), nseg=14)
    pl.box("glow", (1.0, 0.5, 0.04), (0, 1.9, 2.83), kit.emit("#fff0c8", 1.4, "ceilglow"))
    pl.light("c1", (0, 1.9, 2.4), 340, "#fff0d0", size=1.0)
    pl.light("face", (0.8, -0.2, 1.8), 240, "#fff6e8", size=1.0)
    pl.light("face2", (-0.9, 0.6, 1.9), 160, "#fff6e8", size=1.0)


def build_living(kit):
    pl = Pl(kit, G.LIV, "lv")
    wall = kit.plastic("#e9c8f0", 0.85, spec=0.05)
    pl.box("floor", (7.0, 7.0, 0.1), (0, 1.5, -0.05), kit.planks("#d9ab72", "#c99a62", 1.0))
    pl.box("ceil", (7.0, 7.0, 0.1), (0, 1.5, 2.85), kit.plastic("#fbf3e4", 0.9))
    pl.box("back", (7.0, 0.2, 2.8), (0, 4.0, 1.4), wall)
    for sx in (-1, 1):
        pl.box(f"side{sx}", (0.2, 7.0, 2.8), (sx * 3.5, 1.5, 1.4), wall)
    pl.box("front", (7.0, 0.2, 2.8), (0, -2.0, 1.4), wall)
    c = kit.plastic("#2fb8a8", 0.6, spec=0.15)
    c2 = kit.plastic("#6fd6c8", 0.6, spec=0.15)
    cy = 2.2
    pl.box("cbase", (2.4, 0.9, 0.32), (0, cy, 0.16), c, bevel=0.04)
    pl.box("cseat", (2.0, 0.8, 0.12), (0, cy - 0.04, 0.38), c2, bevel=0.04)
    pl.box("cback", (2.4, 0.22, 0.62), (0, cy + 0.34, 0.62), c, bevel=0.05)
    for sx in (-1, 1):
        pl.box(f"carm{sx}", (0.22, 0.9, 0.3), (sx * 1.1, cy, 0.46), c, bevel=0.05)
    pl.box("pillow", (0.4, 0.14, 0.4), (-0.8, cy + 0.16, 0.66), kit.plastic("#ffd95a", 0.7), rot=(0, 0.2, 0.3), bevel=0.04)
    pl.box("rug", (3.0, 2.0, 0.02), (0, 0.8, 0.01), kit.plastic("#f6c453", 0.9))
    pl.box("rug2", (2.5, 1.5, 0.022), (0, 0.8, 0.011), kit.plastic("#ffd978", 0.9))
    pl.cyl("lamp", 0.03, 1.4, (1.9, 3.2, 0.7), kit.plastic("#555a66", 0.4), nseg=8)
    pl.cyl("shade", 0.28, 0.4, (1.9, 3.2, 1.55), kit.emit("#ffb54d", 0.8, "ambershade"), nseg=16, r2=0.18)
    for k, col in enumerate(("#ff7a5c", "#f6c453", "#2fb8a8")):
        pl.box(f"pic{k}", (0.5, 0.04, 0.7), (-0.8 + 0.7 * k, 3.88, 1.8), kit.plastic(col, 0.7))
    pl.box("glow", (1.0, 0.5, 0.04), (0, 1.5, 2.83), kit.emit("#fff0c8", 1.4, "ceilglow"))
    pl.light("c1", (0, 1.5, 2.4), 340, "#fff0d0", size=1.0)
    pl.light("face", (0.8, -0.4, 1.8), 260, "#fff6e8", size=1.0)
    pl.light("lampl", (1.7, 3.0, 1.6), 140, "#ffb25c", size=0.6)


def build_porch(kit):
    pl = Pl(kit, G.PORCH, "pc")
    ground(kit, pl, "#8ed67a")
    pl.box("deck", (6.0, 3.6, 0.2), (0, 0.7, 0.1), kit.planks("#c58b57", "#b87d4a", 1.0, axis="X"))
    wallc = kit.plastic("#fff0cf", 0.85, spec=0.05)
    pl.wall_x("wall", 2.65, -3.5, 3.5, 0.2, 3.4, 0.3, wallc, holes=[(-0.6, 0.6, 0.2, 2.35)])
    pl.box("roof", (7.6, 2.4, 0.25), (0, 1.5, 3.45), kit.plastic("#d9604a", 0.8))
    for sx in (-1, 1):
        pl.box(f"post{sx}", (0.16, 0.16, 3.2), (sx * 2.7, -0.9, 1.8), kit.plastic("#ffffff", 0.6))
    pl.box("door_f", (0.07, 0.08, 2.2), (-0.62, 2.45, 1.3), kit.plastic("#ffffff", 0.7))
    pl.box("door_f2", (0.07, 0.08, 2.2), (0.62, 2.45, 1.3), kit.plastic("#ffffff", 0.7))
    pl.box("door_h", (1.3, 0.08, 0.08), (0, 2.45, 2.38), kit.plastic("#ffffff", 0.7))
    # the door stands open, into the warm hall behind it (a still state for the whole film)
    hinge = pl.empty("dh", (-0.58, 2.6, 0.2), rot=(0, 0, -100 * D2R))
    pl.box("doorleaf", (1.16, 0.07, 2.15), (0.58, 0, 1.075), kit.plastic("#2fb8a8", 0.6, spec=0.2), bevel=0.02, parent=hinge)
    rw = kit.plastic("#ffe2b0", 0.85)
    pl.box("rfloor", (4.0, 3.2, 0.1), (0, 4.4, 0.15), kit.planks("#e8cfa6", "#dcc096", 1.0))
    pl.box("rback", (4.0, 0.2, 2.8), (0, 6.0, 1.6), rw)
    pl.box("rl", (0.2, 3.2, 2.8), (-2.0, 4.4, 1.6), rw)
    pl.box("rr", (0.2, 3.2, 2.8), (2.0, 4.4, 1.6), rw)
    pl.box("rceil", (4.0, 3.2, 0.1), (0, 4.4, 3.05), kit.plastic("#fff8ec", 0.9))
    for k, col in enumerate(("#ff7a5c", "#f6c453", "#2fb8a8")):
        pl.box(f"rpic{k}", (0.5, 0.04, 0.7), (-0.6 + 0.6 * k, 5.88, 1.8), kit.plastic(col, 0.7))
    pl.light("room", (0.0, 4.2, 2.4), 420, "#ffd9a0", size=1.0)
    # the duffel bag at my feet: a short rust canvas barrel on its side, a dark band, an arched handle and a strap
    bag = kit.plastic("#c4632c", 0.7, spec=0.1)
    bagd = kit.plastic("#3a2a22", 0.7)
    bx, by, bz = 0.55, 0.3, 0.39
    pl.cyl("bag", 0.17, 0.62, (bx, by, bz), bag, rot=(0, math.pi / 2, 0), nseg=16)
    pl.cyl("bagband", 0.18, 0.07, (bx, by, bz), bagd, rot=(0, math.pi / 2, 0), nseg=16)
    pl.cyl("bagcapl", 0.175, 0.04, (bx - 0.32, by, bz), bagd, rot=(0, math.pi / 2, 0), nseg=16)
    pl.cyl("bagcapr", 0.175, 0.04, (bx + 0.32, by, bz), bagd, rot=(0, math.pi / 2, 0), nseg=16)
    for dx in (-0.11, 0.11):
        pl.box(f"baghand{dx}", (0.035, 0.035, 0.12), (bx + dx, by, bz + 0.21), bagd)
    pl.box("baggrip", (0.28, 0.045, 0.045), (bx, by, bz + 0.29), bagd, bevel=0.01)
    pl.box("bagstrap", (0.05, 0.04, 0.37), (bx - 0.2, by - 0.15, bz + 0.03), bagd, rot=(0.5, 0, 0))
    pl.light("sun", (-3.0, -4.0, 5.0), 1000, "#fff3d8", size=1.5)
    pl.light("face", (0.0, -2.0, 1.9), 300, "#fff3e0", size=1.0)
    pl.light("fill", (2.5, -2.0, 2.0), 220, "#fff3e0", size=1.0)


def build(kit, story, tl):
    for key in G.HALLS:
        build_hall(kit, key)
    build_house(kit)
    build_board(kit)
    build_theo(kit)
    build_kitchen(kit)
    build_living(kit)
    build_porch(kit)
    return {}


def animate(kit, story, tl, t, ctx):
    # who sits: legs straight out forward, hips on the seat (the set itself never moves)
    sits = {}
    for c in sorted(tl["cues"], key=lambda c: c["t"]):
        if c["name"] == "sit" and c["t"] <= t:
            sits[c["who"]] = c
    for who, c in sits.items():
        root = bpy.data.objects.get(who)
        if c.get("on") and root is not None:
            root.location.z += c.get("z", 0.62) - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    return {}
