"""ep32 "sitter" (Never Paint A PERSON In Here): the set. Kofi's art class paints the town on pine panels, so whatever isn't
painted yet is bare pine with the pencil lines on it. Places (metres, floor z = 0, the car park at z = -0.45):

- the life room is centred on the dais at the origin (x -5.6 .. 5.6, y -5.2 .. 5.0, ceiling 3.2). Easel i stands at angle TH[i]
  on a curve of radius RE with its canvas facing out, its painter behind it at RP. The car park is outside the south window.
- the little daylight sets: the bus stop (x 80, with the pine bench), the cafe (x 120, flower box on the sill), the bakery
  (x 160, the cake), my bedroom (x -40, morning), Mom's hall (x 40: door end south, dining table, my door in the west wall,
  stairs up the east wall to the north).

Acting keys read here (acting.py ignores them): "sit": true seats a character (legs flat) on whatever is under them;
"fade" / "fade_h" / "fade_z": how far the body / the face has turned to raw pine (fade_z: Theo's colour reaches up to this
height in metres, so the colour climbs him from the boots); "bendto": [x, y, deg] leans the torso from the waist toward x, y.
Cues read here (all optional):
- time: {"set": warm | dusk | cold | day | bus | cafe | bake | bed | hall | hallnight | halleve | out} light of the moment
- dip: {"down", "hold", "up", "depth", "hold_to"} the room's lamps ramp to (1 - depth), hold, ramp back (never dark)
- day: {"d": 0..6} the week meter (camera-parented squares at the top of every frame)
- ramp: {"name": bench | cake | ear | nose, "v", "dur"} a colour fill moving from its last value to v over dur seconds
- easel: {"i", "img"}; prop: {"which", "on"}; hall: {"state": ...}
Shot flags: tally, turn8, noceil, hide_easels, hide_cast, fill, ev.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import bpy
import mathutils
from mathutils import Vector as V
from PIL import Image, ImageDraw, ImageFilter

from blocky import acting as _ac
from blocky import faces, rig

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
S = rig.S

X0, X1, Y0, Y1, CEIL = -5.6, 5.6, -5.2, 5.0, 3.2
GROUND = -0.45
DAIS_H = 0.22
GRAPHITE = (44, 42, 42)

# the hall: x HL0 .. HL1, y HY0 .. HY1, ceiling HH. Dining table at the south, stairs up the east wall to the north.
HL0, HL1, HY0, HY1, HH = 37.9, 42.1, -1.5, 7.5, 3.6
HX = 40.0
MYDOOR = (HL0, 3.85)              # my bedroom door in the west wall
TABLE = (39.5, 2.0)
BUS_, CAF_, BAK_, BED_ = (80.0, 0.2), (120.0, 1.5), (160.9, -0.15), (-40.0, 0.0)
DAYCOL = ["#ef5b5b", "#f59a3c", "#f2d04a", "#5fd068", "#4cc3f0", "#7a8cf0", "#c47ae8"]


# ------------------------------------------------------------------------------------------ small helpers

def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl["cues"] if c["name"] == name]


def _last(cs, t):
    out = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            out = c
    return out


def workdir(tl) -> Path:
    d = ROOT / "out" / "work" / tl.get("name", "ep32-sitter") / "art"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _wrap(a):
    return (a + 180.0) % 360.0 - 180.0


def img_mat(kit, name, im: Image.Image, wd: Path, rough=0.85, alpha=False, emit=0.0):
    """A PIL drawing as a material (the image is kept on the material for swapping)."""
    path = wd / f"{name}.png"
    im.save(path)
    img = bpy.data.images.load(str(path), check_existing=False)
    img.colorspace_settings.name = "sRGB"
    m = kit._new(f"img {name}")
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Linear"
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    if alpha:
        nt.links.new(tex.outputs["Alpha"], b.inputs["Alpha"])
        m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
    if emit:
        for k in ("Emission Color", "Emission"):
            if k in b.inputs:
                nt.links.new(tex.outputs["Color"], b.inputs[k])
                break
        if "Emission Strength" in b.inputs:
            b.inputs["Emission Strength"].default_value = emit
    kit._fogged(m, b.outputs[0])
    m["tex_name"] = tex.name
    return m


def uvplane(kit, name, size, loc, mat, parent, rot):
    """kit.plane with UVs (kit's planes have none, so a picture on one would sample a single pixel)."""
    ob = kit.plane(name, size, loc, mat, parent, rot)
    uv = ob.data.uv_layers.new(name="UVMap")
    corner = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (0, 1)}
    for poly in ob.data.polygons:
        for li in poly.loop_indices:
            uv.data[li].uv = corner[ob.data.loops[li].vertex_index]
    return ob


def set_img(m, im_path_img):
    m.node_tree.nodes[m["tex_name"]].image = im_path_img




# ------------------------------------------------------------------------------------------ the drawings

FACE_BOX = (100, 95, 280, 380)          # my canvases: where the guide lines go (x, y, w, h)
HEAD_OVAL = (240, 285, 150, 205)        # centre x, y and radii of the head


def paper(w, h, base=(239, 232, 214), seed=1):
    rnd = random.Random(seed)
    im = Image.new("RGB", (w, h), base)
    d = ImageDraw.Draw(im)
    for _ in range(int(w * h / 900)):
        x, y = rnd.randrange(w), rnd.randrange(h)
        v = rnd.randint(-7, 7)
        d.point((x, y), fill=tuple(max(0, min(255, c + v)) for c in base))
    return im


def pencil(d, pts, th, col=GRAPHITE):
    d.line(pts, fill=col, width=int(th), joint="curve")
    for x, y in (pts[0], pts[-1]):
        d.ellipse([x - th / 2, y - th / 2, x + th / 2, y + th / 2], fill=col)


def oval(d, cx, cy, rx, ry, th, fill=None, col=GRAPHITE):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill, outline=col, width=int(th))


def portrait_lines(d, ox, oy, W, H, stage, th, pale=(246, 240, 226), corners=True):
    """The half face I keep drawing, in a W x H box at (ox, oy). Faded Mum's face is exactly these lines.
    stage 0: guide cross, two empty ovals and the little lines at the eye corners; 1: + the short nose;
    2: + a mouth corner."""
    def P(u, v):
        return (ox + u * W, oy + v * H)

    pencil(d, [P(0.5, 0.06), P(0.5, 0.94)], th * 0.8)
    pencil(d, [P(0.1, 0.42), P(0.9, 0.42)], th * 0.8)
    for cx in (0.29, 0.71):
        oval(d, *P(cx, 0.42), 0.16 * W, 0.1 * H, th, fill=pale)
    if corners:
        for s_, ex in ((-1, 0.13), (1, 0.87)):
            for k in (-1, 0, 1):
                pencil(d, [P(ex, 0.42 + k * 0.012), P(ex + s_ * 0.085, 0.42 + k * 0.05)], th * 0.85)
    if stage >= 1:
        pencil(d, [P(0.5, 0.5), P(0.53, 0.56), P(0.555, 0.605)], th)
    if stage >= 2:
        pencil(d, [P(0.33, 0.775), P(0.375, 0.795), P(0.425, 0.8)], th)


def brown_eyes(d, ox, oy, W, H, scale=1.0):
    """The kind brown eyes, painted over the guide ovals."""
    for cx in (0.29, 0.71):
        x, y = ox + cx * W, oy + 0.42 * H
        rx, ry = 0.14 * W * scale, 0.085 * H * scale
        d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=(247, 241, 229), outline=(60, 40, 30), width=3)
        r = ry * 0.95
        d.ellipse([x - r, y - r, x + r, y + r], fill=(104, 62, 36))
        r2 = r * 0.45
        d.ellipse([x - r2, y - r2, x + r2, y + r2], fill=(24, 14, 10))
        d.ellipse([x + r * 0.25, y - r * 0.7, x + r * 0.6, y - r * 0.35], fill=(250, 246, 238))



# ------------------------------------------------------------------------------------------ the drawings (all pine and pencil)
PINE = (217, 186, 140)
SKIN = (232, 196, 160)


def pine_tex(w, h, seed=11, density=700):
    rnd = random.Random(seed)
    im = Image.new("RGB", (w, h), PINE)
    d = ImageDraw.Draw(im)
    for _ in range(int(w * h / density)):
        x, y0 = rnd.randrange(w), rnd.randrange(h)
        dk = rnd.randint(8, 26)
        d.line([(x, y0), (x + rnd.randint(-5, 5), min(h, y0 + rnd.randint(50, 300)))], fill=(PINE[0] - dk, PINE[1] - dk, PINE[2] - dk),
               width=rnd.choice((1, 2, 3)))
    for _ in range(2):          # two dark knots
        kx, ky = rnd.randrange(60, w - 60), rnd.randrange(60, h - 60)
        d.ellipse([kx - 14, ky - 9, kx + 14, ky + 9], fill=(150, 112, 70))
    return im.filter(ImageFilter.GaussianBlur(0.7))


def panel_half():
    """Frame 1: a face, its left half painted, its right half bare pine with the graphite cross and one empty eye oval."""
    im = pine_tex(480, 600, 3).convert("RGBA")
    d = ImageDraw.Draw(im)
    cx, cy, rx, ry = HEAD_OVAL
    ox, oy, fw, fh = FACE_BOX
    oval(d, cx, cy, rx, ry, 5, col=GRAPHITE)
    portrait_lines(d, ox, oy, fw, fh, 0, 8, pale=(238, 216, 172), corners=False)
    pencil(d, [(ox + 0.33 * fw, oy + 0.79 * fh), (ox + 0.67 * fw, oy + 0.79 * fh)], 7)
    ov = Image.new("RGBA", (480, 600), (0, 0, 0, 0))
    o = ImageDraw.Draw(ov)
    o.rounded_rectangle([30, 478, 260, 660], radius=40, fill=(56, 128, 78, 255))
    o.rectangle([200, 425, 260, 484], fill=SKIN + (255,))
    o.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=SKIN + (255,))
    o.pieslice([cx - rx - 12, cy - ry - 18, cx + rx + 12, cy + 18], 180, 360, fill=(98, 62, 38, 255))
    o.rectangle([cx - rx - 12, cy - 40, cx - rx + 20, cy + 70], fill=(98, 62, 38, 255))
    brown_eyes(o, ox, oy, fw, fh, 1.0)
    o.arc([ox + 0.3 * fw, oy + 0.7 * fh, ox + 0.7 * fw, oy + 0.86 * fh], 15, 165, fill=(168, 80, 80, 255), width=8)
    o.line([(ox + 0.12 * fw, oy + 0.3 * fh), (ox + 0.4 * fw, oy + 0.27 * fh)], fill=(70, 44, 28, 255), width=9)
    ov = ov.crop((0, 0, 238, 600))
    im.alpha_composite(ov, (0, 0))
    return im.convert("RGB")


def panel_cross():
    """A blank pine panel with only a pencil cross for a face."""
    im = pine_tex(480, 600, 6)
    d = ImageDraw.Draw(im)
    cx, cy, rx, ry = HEAD_OVAL
    oval(d, cx, cy, rx, ry, 5, col=GRAPHITE)
    pencil(d, [(cx, cy - ry + 20), (cx, cy + ry - 20)], 7)
    pencil(d, [(cx - rx + 30, cy - 20), (cx + rx - 30, cy - 20)], 7)
    return im


def panel_theo(stage):
    """Theo on my panel. stage 0: a young man's figure in pencil on pine with the jacket green and the hair brown going in;
    stage 1: the face painted, brown eyes, a wide grin, the nose a square of bare pine with a pencil nose outline."""
    im = pine_tex(480, 600, 5).convert("RGBA")
    d = ImageDraw.Draw(im)
    cx, cy, rx, ry = HEAD_OVAL
    ox, oy, fw, fh = FACE_BOX
    G, GL = (47, 95, 168, 255), (240, 232, 214, 255)
    if stage == 0:
        hy, hrx, hry = 190, 92, 112
        pencil(d, [(80, 600), (110, 420), (240, 360), (370, 420), (400, 600)], 7)
        d.polygon([(90, 600), (115, 428), (240, 370), (365, 428), (390, 600)], fill=G)
        d.polygon([(205, 372), (240, 440), (275, 372)], fill=GL)
        oval(d, 240, hy, hrx, hry, 6)
        d.pieslice([240 - hrx - 8, hy - hry - 12, 240 + hrx + 8, hy + 20], 180, 360, fill=(98, 62, 38, 255))
        d.polygon([(150, hy - 60), (330, hy - 100), (330, hy - 40), (150, hy - 20)], fill=(98, 62, 38, 255))
        pencil(d, [(240, hy - 40), (240, hy + hry - 14)], 6)
        pencil(d, [(240 - hrx + 20, hy + 10), (240 + hrx - 20, hy + 10)], 6)
        for sx in (-1, 1):
            oval(d, 240 + sx * 44, hy + 10, 30, 20, 5, fill=(238, 216, 172))
        pencil(d, [(200, hy + 74), (280, hy + 74)], 6)
        return im.convert("RGB")
    oval(d, cx, cy, rx, ry, 4, col=GRAPHITE)
    d.rounded_rectangle([30, 478, 450, 660], radius=40, fill=G)
    d.polygon([(190, 478), (290, 478), (240, 548)], fill=GL)
    d.rectangle([205, 425, 275, 484], fill=SKIN + (255,))
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=SKIN + (255,))
    d.pieslice([cx - rx - 12, cy - ry - 18, cx + rx + 12, cy + 18], 180, 360, fill=(98, 62, 38, 255))
    d.polygon([(cx - rx + 10, cy - ry + 40), (cx + rx - 10, cy - ry - 8), (cx + rx - 10, cy - ry + 70), (cx - rx + 20, cy - 60)], fill=(98, 62, 38, 255))
    brown_eyes(d, ox, oy, fw, fh, 1.0)
    for sx in (0.29, 0.71):
        d.line([(ox + (sx - 0.13) * fw, oy + 0.3 * fh), (ox + (sx + 0.13) * fw, oy + 0.28 * fh)], fill=(70, 44, 28, 255), width=9)
    d.chord([ox + 0.28 * fw, oy + 0.66 * fh, ox + 0.72 * fw, oy + 0.9 * fh], 0, 180, fill=(250, 246, 238, 255), outline=(150, 60, 60, 255), width=6)
    px, py = ox + 0.5 * fw, oy + 0.54 * fh
    d.rectangle([px - 30, py - 34, px + 30, py + 34], fill=PINE + (255,), outline=(190, 150, 100, 255), width=3)
    for k in range(5):
        d.line([(px - 24 + k * 12, py - 30), (px - 22 + k * 12, py + 30)], fill=(190, 156, 110, 255), width=2)
    pencil(d, [(px, py - 22), (px - 4, py + 10), (px + 14, py + 18)], 5)
    pencil(d, [(px - 16, py + 18), (px - 4, py + 24)], 5)
    return im.convert("RGB")


def panel_bench():
    """Monday's panel: a painted green bench on a sunny lawn."""
    im = Image.new("RGB", (480, 600), (160, 208, 240))
    d = ImageDraw.Draw(im)
    d.ellipse([340, 60, 420, 140], fill=(255, 232, 150))
    for cx, cy in ((120, 110), (230, 150)):
        for k in range(4):
            d.ellipse([cx + k * 34 - 40, cy - 22, cx + k * 34 + 22, cy + 24], fill=(252, 252, 250))
    d.rectangle([0, 360, 480, 600], fill=(112, 182, 92))
    G, GD = (95, 208, 104), (50, 140, 66)
    for k in range(3):
        d.rounded_rectangle([86, 262 + k * 30, 394, 286 + k * 30], radius=7, fill=G, outline=GD, width=4)
    for x in (92, 372):
        d.rectangle([x, 250, x + 20, 480], fill=GD)
    d.rounded_rectangle([70, 372, 410, 404], radius=7, fill=G, outline=GD, width=4)
    return im


def panel_bus():
    """A bus-stop panel in progress: the shelter painted, the rest still pencil on pine."""
    im = pine_tex(480, 600, 8)
    d = ImageDraw.Draw(im)
    d.rectangle([60, 190, 420, 232], fill=(110, 118, 126))
    d.rectangle([80, 232, 400, 450], fill=(159, 198, 214))
    for x in (60, 392):
        d.rectangle([x, 232, x + 18, 480], fill=(100, 108, 116))
    d.rectangle([0, 470, 480, 600], fill=(96, 98, 104))
    pencil(d, [(100, 420), (380, 420)], 6)
    pencil(d, [(120, 420), (120, 470)], 6)
    pencil(d, [(360, 420), (360, 470)], 6)
    pencil(d, [(100, 380), (380, 380), (380, 420)], 5)
    return im


def town_image(seed):
    """A background painter's town: a few coloured houses, a tree."""
    rnd = random.Random(seed)
    im = Image.new("RGB", (480, 600), (166, 208, 238))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 430, 480, 600], fill=(122, 176, 98))
    cols = [(197, 112, 78), (156, 181, 154), (217, 176, 74), (143, 176, 208), (234, 223, 195)]
    x = 20
    for k in range(3):
        w, h = rnd.randint(110, 150), rnd.randint(150, 260)
        c = cols[(seed + k) % 5]
        d.rectangle([x, 430 - h, x + w, 430], fill=c)
        d.polygon([(x - 8, 430 - h), (x + w + 8, 430 - h), (x + w / 2, 430 - h - 50)], fill=(120, 74, 60))
        for wx in (x + 20, x + w - 50):
            d.rectangle([wx, 430 - h + 30, wx + 30, 430 - h + 70], fill=(70, 90, 112))
        x += w + 14
    d.rectangle([440, 330, 454, 430], fill=(110, 78, 50))
    d.ellipse([410, 270, 484, 350], fill=(76, 146, 72))
    return im


def flowerbox_image():
    """The cafe window's flower box: red flowers on the left, graphite outlines on bare pine on the right."""
    W, H = 1024, 300
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pos = [(70, 0.5), (190, 0.8), (310, 0.4), (430, 0.7), (580, 0.55), (700, 0.8), (820, 0.45), (940, 0.7)]
    pine = pine_tex(W // 2, 130, 12).convert("RGBA")
    im.paste(pine, (W // 2, 170))
    d.rectangle([0, 170, W // 2, 300], fill=(196, 100, 72, 255))
    d.rectangle([0, 170, W // 2, 190], fill=(158, 74, 52, 255))
    for k in range(7):
        d.line([(k * 74 + 20, 195), (k * 74 + 20, 290)], fill=(166, 82, 58, 255), width=3)
    d.rectangle([W // 2, 170, W, 190], fill=(190, 150, 100, 255))
    pencil(d, [(W // 2, 170), (W - 4, 170), (W - 4, 298), (W // 2, 298)], 5)
    for x, hgt in pos:
        top = 170 - int(120 * hgt) - 30
        if x < W // 2:
            d.line([(x, 175), (x, top)], fill=(64, 140, 70, 255), width=8)
            d.ellipse([x - 30, top - 30, x + 30, top + 30], fill=(214, 52, 52, 255))
            d.ellipse([x - 11, top - 11, x + 11, top + 11], fill=(250, 214, 80, 255))
            d.ellipse([x + 4, 140, x + 40, 156], fill=(64, 140, 70, 255))
        else:
            pencil(d, [(x, 175), (x, top)], 6)
            oval(d, x, top, 30, 30, 6, col=GRAPHITE)
            oval(d, x, top, 11, 11, 4, col=GRAPHITE)
            pencil(d, [(x + 4, 150), (x + 40, 146)], 5)
    return im


def ear_patch_image():
    """The ear patch behind my left ear: raw pine with one faint graphite curve of an ear outline. Alpha-edged."""
    W = 256
    pine = pine_tex(W, W, 21, 380).convert("RGBA")
    mask = Image.new("L", (W, W), 0)
    ImageDraw.Draw(mask).rounded_rectangle([6, 6, W - 6, W - 6], radius=78, fill=255)
    pine.putalpha(mask)
    d = ImageDraw.Draw(pine)
    d.rounded_rectangle([6, 6, W - 6, W - 6], radius=78, outline=(150, 112, 70, 255), width=9)
    col = (52, 48, 46, 255)
    d.arc([76, 36, 196, 226], 200, 40, fill=col, width=9)
    d.arc([104, 82, 170, 170], 210, 20, fill=col, width=8)
    d.line([(112, 206), (128, 150)], fill=col, width=8)
    d.line([(150, 120), (164, 160)], fill=col, width=7)
    return pine


def nose_patch_image(ink=False):
    """Theo's nose: a small square of bare pine with a graphite nose outline (ink=True: only the finished ink stroke)."""
    W, H = 128, 160
    if ink:
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        col = (78, 46, 38, 255)
        d.line([(62, 38), (56, 100), (80, 112)], fill=col, width=8, joint="curve")
        d.ellipse([52, 34, 70, 52], fill=col)
        d.line([(34, 112), (56, 120)], fill=col, width=6)
        return im
    pine = pine_tex(W, H, 31, 300).convert("RGBA")
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([4, 4, W - 4, H - 4], radius=18, fill=255)
    pine.putalpha(mask)
    d = ImageDraw.Draw(pine)
    d.rounded_rectangle([4, 4, W - 4, H - 4], radius=18, outline=(58, 36, 22, 255), width=11)
    col = (40, 34, 32, 255)
    d.line([(62, 36), (56, 100), (80, 112)], fill=col, width=9, joint="curve")
    d.line([(34, 112), (56, 120)], fill=col, width=8)
    return pine


def pine_face_image(kind, stage):
    """A pine head's texture: raw pine with graphite guide lines, wrapped round the head (faces.py's layout).
    kind "theo": the cross, two empty eye ovals and one mouth line, no nose."""
    W, H = faces.TEX_W, faces.TEX_H
    rnd = random.Random(11)
    im = Image.new("RGB", (W, H), PINE)
    d = ImageDraw.Draw(im)
    for _ in range(260):
        x = rnd.randrange(W)
        y0 = rnd.randrange(H)
        dk = rnd.randint(8, 24)
        d.line([(x, y0), (x + rnd.randint(-6, 6), min(H, y0 + rnd.randint(80, 400)))], fill=(217 - dk, 186 - dk, 140 - dk), width=rnd.choice((1, 2, 3)))
    im = im.filter(ImageFilter.GaussianBlur(0.8))
    d = ImageDraw.Draw(im)
    s = faces.FX1 - faces.FX0
    fw = 1.048 * s
    fh = (faces.FY1 - faces.FY0) * 0.96
    ox, oy = W / 2 - fw / 2, faces.FY0 + (faces.FY1 - faces.FY0) * 0.02
    portrait_lines(d, ox, oy, fw, fh, 0, 22, pale=(247, 240, 224), corners=False)
    pencil(d, [(ox + 0.33 * fw, oy + 0.79 * fh), (ox + 0.67 * fw, oy + 0.79 * fh)], 22)
    return im


def sky_image():
    """The north window by day: a pale sky with soft clouds."""
    W, H = 512, 1024
    im = Image.new("RGB", (W, H), (170, 205, 238))
    d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=(int(150 + 60 * k), int(196 + 36 * k), int(238 + 8 * k)))
    rnd = random.Random(4)
    for _ in range(7):
        x, y = rnd.randrange(W), rnd.randrange(H)
        for j in range(4):
            d.ellipse([x + j * 36 - 40, y - 20, x + j * 36 + 40, y + 24], fill=(250, 250, 250))
    return im.filter(ImageFilter.GaussianBlur(3))


def art_image(seed, w=300, h=380):
    """A framed landscape or flowers for Mum's hall. No text."""
    rnd = random.Random(seed)
    sky = [(150, 190, 220), (230, 190, 150), (180, 200, 170), (200, 170, 190)][seed % 4]
    im = Image.new("RGB", (w, h), sky)
    d = ImageDraw.Draw(im)
    gr = [(90, 130, 80), (120, 100, 70), (70, 110, 120), (150, 120, 90)][(seed // 2) % 4]
    d.polygon([(0, h * 0.62), (w * 0.35, h * 0.45), (w * 0.7, h * 0.6), (w, h * 0.5), (w, h), (0, h)], fill=gr)
    for _ in range(14):
        x, y = rnd.randint(10, w - 10), rnd.randint(int(h * 0.65), h - 12)
        col = [(230, 90, 80), (240, 200, 70), (250, 250, 240), (200, 110, 200)][rnd.randint(0, 3)]
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=col)
    d.ellipse([w * 0.7, h * 0.12, w * 0.7 + 50, h * 0.12 + 50], fill=(250, 232, 150))
    return im


def tally_image():
    """Nine plain upright graphite strokes, no tenth, to scratch along the dais's front edge (1.2 x 0.2 m)."""
    W, H = 1200, 200
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rnd = random.Random(9)
    x0, gap = 200, 100
    for k in range(9):
        x = x0 + k * gap + rnd.randint(-4, 4)
        top, bot = 38 + rnd.randint(-5, 5), 168 + rnd.randint(-5, 5)
        d.line([(x, top), (x + rnd.randint(-4, 4), bot)], fill=(*GRAPHITE, 255), width=11)
        d.ellipse([x - 5, top - 5, x + 5, top + 5], fill=(*GRAPHITE, 255))
        d.ellipse([x - 5, bot - 5, x + 5, bot + 5], fill=(*GRAPHITE, 255))
    return im.filter(ImageFilter.GaussianBlur(0.9))


# ------------------------------------------------------------------------------------------ materials


def pine_mat(kit, name="pine", c1="#d6c3a0", c2="#a98c62", scale=11.0):
    if name in kit.MATS:
        return kit.MATS[name]
    m, N, L, b = kit._mat(name)
    v = kit._coords(N, L, (scale, scale * 0.35, scale * 0.35))
    wave = N.new("ShaderNodeTexWave")
    wave.bands_direction = "X"
    wave.inputs["Scale"].default_value = 1.0
    wave.inputs["Distortion"].default_value = 5.0
    wave.inputs["Detail"].default_value = 3.0
    L.new(v, wave.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    L.new(v, nz.inputs["Vector"])
    mix = N.new("ShaderNodeMath")
    mix.operation = "MULTIPLY_ADD"
    L.new(wave.outputs["Fac"], mix.inputs[0])
    mix.inputs[1].default_value = 0.6
    L.new(nz.outputs["Fac"], mix.inputs[2])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = kit.col(c2)
    ramp.color_ramp.elements[1].position = 0.9
    ramp.color_ramp.elements[1].color = kit.col(c1)
    L.new(mix.outputs[0], ramp.inputs["Fac"])
    L.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.72
    kit._bump(N, L, b, wave.outputs["Fac"], 0.25, 0.01)
    kit._fogged(m, b.outputs[0])
    return m


def clear_lens(kit):
    """The rig's glasses use kit.glass, which goes dark at our low sample counts and hides the eyes. Register a clear lens
    under the name the rig asks for, before the cast is built."""
    name = "glass #dde6ea"
    m = kit._new(name)
    nt = m.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    nt.links.new(tr.outputs[0], out.inputs["Surface"])
    return m


def materials(kit, wd):
    M = {}
    M["plaster"] = kit.grime("#ece3cd", 0.86, 2.0, "plaster", 0.92)
    M["floor"] = kit.planks("#cc9a54", "#9d7036", scale=1.0, axis="Y", name="honey boards", rough=0.55)
    M["brick"] = kit.bricks("#76605a", "#58463f", "#4f4842", scale=1.0)
    M["ground"] = kit.concrete("#1d1f24", scale=1.2, stains=0.35, name="car park", rough=0.28)
    M["step"] = kit.concrete("#4a4b50", scale=2.0, stains=0.3, name="steps", rough=0.5)
    M["ceilmat"] = kit.plastic("#8f897c", 0.95, "ceiling")
    M["roof"] = kit.plastic("#23262b", 0.8, "roof")
    M["pine"] = pine_mat(kit)
    M["dais"] = pine_mat(kit, "dais wood", "#caa56d", "#9c7a46", 9.0)
    M["cushion"] = kit.plastic("#8fb48b", 0.95, "sage cushion", 0.1)
    M["easel"] = kit.plastic("#b98a55", 0.6, "easel wood")
    M["dark"] = kit.plastic("#2b2c30", 0.45, "dark metal")
    M["white"] = kit.plastic("#f0ece2", 0.7, "white trim")
    M["lampglow"] = kit.emit("#ffc88a", 6.0, "lamp bulb")
    M["table"] = kit.plastic("#a9794a", 0.6, "table wood")
    M["floor2"] = kit.plastic("#b8a58a", 0.7, "hall floor")
    M["hallwall"] = kit.plastic("#c9c4b8", 0.9, "hall wall")
    M["square"] = kit.plastic("#d2cec2", 0.95, "pale squares")
    M["frame"] = kit.plastic("#5a3d24", 0.55, "frame wood")
    M["glass_door"] = kit.emit("#fff1d6", 2.0, "door glass")
    M["door"] = kit.plastic("#7a5636", 0.6, "door wood")
    M["jar"] = kit.plastic("#cfd8d4", 0.3, "jar")
    M["brush"] = kit.plastic("#9a6a3c", 0.6, "brush")
    M["bristle"] = kit.plastic("#2a2420", 0.7, "bristle")
    M["splash"] = [kit.plastic(h, 0.5, f"splash {h}") for h in ("#3a6fb5", "#c9423a", "#e0b23a", "#3f9a6a", "#d7d1c4")]
    M["bowl"] = kit.plastic("#8c5a3a", 0.55, "bowl")
    M["orange"] = kit.plastic("#e58a22", 0.4, "orange")
    M["pearf"] = kit.plastic("#b2c24a", 0.4, "pear")
    M["plum"] = kit.plastic("#5b2d62", 0.35, "plum")
    M["grape"] = kit.plastic("#6f3f6b", 0.3, "grape")
    M["curtain"] = kit.plastic("#31404f", 0.9, "frame trim")
    M["phone"] = kit.emit("#bfe4ff", 1.6, "phone glow")
    M["phone_off"] = kit.plastic("#16171a", 0.3, "phone")
    M["coat"] = kit.plastic("#2f3238", 0.9, "coat")
    M["bag"] = kit.plastic("#5b6b4a", 0.9, "bag")
    M["mug"] = kit.plastic("#d8d2c4", 0.4, "mug")
    M["canvas_back"] = kit.plastic("#d8c8a6", 0.9, "canvas back")
    M["post"] = kit.plastic("#2d2f33", 0.5, "lamp post")
    M["lamp_head"] = kit.emit("#ffd9a0", 14.0, "post lamp")
    M["win_day"] = kit.emit("#e6f2ff", 3.0, "window daylight")
    M["tall"] = kit.plastic("#d7d0c0", 0.8, "table cloth")
    return M

# ------------------------------------------------------------------------------------------ the room


def slab(kit, name, x0, x1, y0, y1, z0, z1, mat, parent=None):
    if x1 - x0 < 1e-4 or y1 - y0 < 1e-4 or z1 - z0 < 1e-4:
        return None
    return kit.box(name, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), mat, parent)


def wall(kit, M, name, axis, c, a0, a1, z0, z1, hole=None, inner_sign=1, T=0.3):
    """A wall along `axis` ('x' or 'y') at the other coordinate c; plaster inside (inner_sign is the way into the room),
    brick outside, T thick. hole = (a0, a1, z0, z1) is cut right through."""
    pieces = []
    if hole:
        h0, h1, hz0, hz1 = hole
        pieces = [(a0, h0, z0, z1), (h1, a1, z0, z1), (h0, h1, z0, hz0), (h0, h1, hz1, z1)]
    else:
        pieces = [(a0, a1, z0, z1)]
    for k, (p0, p1, q0, q1) in enumerate(pieces):
        for layer, (mat, t0, t1) in enumerate(((M["plaster"], 0.0, 0.06), (M["brick"], 0.06, T))):
            lo, hi = c + inner_sign * t0 * -1, c + inner_sign * t1 * -1
            lo, hi = min(lo, hi), max(lo, hi)
            if axis == "x":      # runs along x at y = c
                slab(kit, f"{name} {k}{layer}", p0, p1, lo, hi, q0, q1, mat)
            else:
                slab(kit, f"{name} {k}{layer}", lo, hi, p0, p1, q0, q1, mat)


def build_room(kit, ctx, M):
    zb = GROUND
    kit.box("floor", (X1 - X0 + 0.6, Y1 - Y0 + 0.6, 0.45), ((X0 + X1) / 2, (Y0 + Y1) / 2, -0.225), M["floor"])
    ctx["ceiling"] = slab(kit, "ceiling", X0, X1, Y0, Y1, CEIL, CEIL + 0.04, M["ceilmat"])
    ctx["roof"] = slab(kit, "roof", X0 - 0.35, X1 + 0.35, Y0 - 0.35, Y1 + 0.35, CEIL + 0.04, CEIL + 0.36, M["roof"])
    # south wall (inner face at y = Y0; room is to +y), big open window for the car park view
    wall(kit, M, "wall s", "x", Y0, X0 - 0.3, X1 + 0.3, zb, CEIL, hole=(-2.6, 2.6, 0.9, 2.5), inner_sign=1)
    # north wall, the rainy window behind the dais
    wall(kit, M, "wall n", "x", Y1, X0 - 0.3, X1 + 0.3, zb, CEIL, hole=(-1.7, 1.7, 0.8, 2.95), inner_sign=-1)
    # west wall: the door
    wall(kit, M, "wall w", "y", X0, Y0 - 0.3, Y1 + 0.3, zb, CEIL, hole=(-3.3, -2.4, zb, 2.15), inner_sign=1)
    wall(kit, M, "wall e", "y", X1, Y0 - 0.3, Y1 + 0.3, zb, CEIL, inner_sign=-1)
    # window frames
    for x in (-2.6, -0.87, 0.87, 2.6):
        slab(kit, "mullion s", x - 0.04, x + 0.04, Y0 - 0.05, Y0 + 0.05, 0.9, 2.5, M["white"])
    slab(kit, "sill s", -2.7, 2.7, Y0 - 0.1, Y0 + 0.12, 0.86, 0.92, M["white"])
    for x in (-1.7, 0.0, 1.7):
        slab(kit, "mullion n", x - 0.04, x + 0.04, Y1 - 0.05, Y1 + 0.05, 0.8, 2.95, M["white"])
    slab(kit, "transom n", -1.7, 1.7, Y1 - 0.05, Y1 + 0.05, 1.85, 1.92, M["white"])
    # the rain on the north window: a glowing dark pane with streaks
    pane = uvplane(kit, "north pane", (3.4, 2.15), (0, Y1 - 0.02, 1.875), None, None, (math.pi / 2, 0, 0))
    ctx["pane_mat"] = img_mat(kit, "sky", sky_image(), ctx["wd"], rough=0.3, emit=0.55)
    pane.data.materials.append(ctx["pane_mat"])
    ctx["pane"] = pane
    ctx["pane_uv"] = None
    # the door: open, with a pane of the dark outside
    hinge = kit.empty("door hinge", (X0 + 0.06, -2.4, 0))
    kit.box("door leaf", (0.06, 0.9, 2.1), (0, -0.45, 1.05), M["door"], hinge, bevel=0.01)
    hinge.rotation_euler = (0, 0, math.radians(-72))
    ctx["door"] = hinge
    # steps outside
    for k in range(3):
        slab(kit, f"step {k}", X0 - 0.3 - 0.45 * (k + 1), X0 - 0.3, -3.5, -2.2, zb, -0.15 - 0.1 * k + 0.0, M["step"])
    slab(kit, "stoop", X0 - 0.75, X0 - 0.3, -3.5, -2.2, zb, -0.02, M["step"])
    # the car park
    kit.box("ground", (160, 160, 0.2), (0, 0, GROUND - 0.1), M["ground"])
    # the lamp post
    kit.cyl("post", 0.06, 3.6, (-2.6, -9.4, GROUND + 1.8), M["post"])
    kit.box("post head", (0.5, 0.3, 0.12), (-2.6, -9.2, GROUND + 3.55), M["lamp_head"])


def build_dais(kit, ctx, M):
    d = kit.empty("dais", (0, 0, 0))
    kit.box("dais top", (2.0, 2.0, DAIS_H), (0, 0, DAIS_H / 2), M["dais"], d, bevel=0.02)
    # nine graphite strokes along the front edge (shown only in S39)
    mt = img_mat(kit, "tally", tally_image(), ctx["wd"], rough=0.9, alpha=True)
    pl = uvplane(kit, "tally", (1.2, 0.2), (0, -1.0 - 0.015, 0.11), mt, d, (math.pi / 2, 0, 0))
    ctx["dais"], ctx["tally"] = d, pl
    # the stool and the cushion
    top = DAIS_H + 0.35
    st = kit.empty("dais stool", (0, 0, 0))
    kit.box("seat", (0.52, 0.52, 0.05), (0, 0, top - 0.025), M["easel"], st, bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box("stool leg", (0.05, 0.05, 0.33), (sx * 0.2, sy * 0.2, DAIS_H + 0.165), M["easel"], st)
    ctx["dais_stool"] = st
    ctx["cushions"] = []
    for dent in (0.0, 1.0):
        n_r, n_a, T, R = 7, 28, 0.11, 0.43
        verts, fcs = [], []
        for i in range(n_r + 1):
            r = R * i / n_r
            z = T * (1.0 - 0.0)
            for j in range(n_a):
                a = 2 * math.pi * j / n_a
                zz = top + T * 0.92 - dent * 0.085 * math.exp(-((r / 0.2) ** 2)) * 1.0 - (T * 0.25) * (r / R) ** 4
                verts.append((r * math.cos(a), r * math.sin(a), zz))
        for j in range(n_a):
            verts.append((R * math.cos(2 * math.pi * j / n_a), R * math.sin(2 * math.pi * j / n_a), top))
        base = (n_r + 1) * n_a
        for i in range(n_r):
            for j in range(n_a):
                a, b = i * n_a + j, i * n_a + (j + 1) % n_a
                fcs.append((a, a + n_a, b + n_a, b))
        for j in range(n_a):
            a, b = n_r * n_a + j, n_r * n_a + (j + 1) % n_a
            fcs.append((a, base + j, base + (j + 1) % n_a, b))
        ob = kit.mesh_obj(f"cushion {dent}", verts, fcs, M["cushion"], None, smooth=True)
        ctx["cushions"].append(ob)


def build_easel(kit, ctx, M, i, th, wd):
    e = kit.empty(f"easel {i}", (0, 0, 0))
    for sx in (-0.34, 0.34):
        kit.box("easel leg", (0.05, 0.05, 1.9), (sx, 0, 0.95), M["easel"], e)
    kit.box("easel shelf", (0.8, 0.2, 0.04), (0, -0.07, 0.82), M["easel"], e)
    kit.box("easel top", (0.78, 0.06, 0.05), (0, 0, 1.82), M["easel"], e)
    kit.box("easel back leg", (0.05, 0.05, 1.7), (0, 0.4, 0.85), M["easel"], e, rot=(math.radians(-13), 0, 0))
    cv = kit.empty("canvas", (0, -0.05, 1.3), e)
    kit.box("canvas frame", (0.6, 0.03, 0.75), (0, 0, 0), M["canvas_back"], cv)
    face = uvplane(kit, "canvas face", (0.6, 0.75), (0, -0.0165, 0), None, cv, (math.pi / 2, 0, 0))
    mat = img_mat(kit, f"canvas {i}", pine_tex(480, 600, i), wd, rough=0.88)
    face.data.materials.append(mat)
    # the clamp lamp on the top bar
    kit.box("lamp arm", (0.03, 0.34, 0.03), (0.2, -0.17, 1.88), M["dark"], e, rot=(math.radians(-12), 0, 0))
    kit.cyl("lamp shade", 0.07, 0.1, (0.2, -0.36, 1.9), M["dark"], e, rot=(math.radians(100), 0, 0), r2=0.04)
    kit.sphere("lamp bulb", 0.035, (0.2, -0.36, 1.87), M["lampglow"], e)
    e.location = (RE_ * math.cos(math.radians(th)), RE_ * math.sin(math.radians(th)), 0)
    e.rotation_euler = (0, 0, math.radians(th + 90))
    # the spot light that is this lamp
    lamp = kit.light(f"lamp {i}", "SPOT", (0, 0, 0), 30.0, "#ffb870", spot=70, blend=0.5, size=0.04)
    lamp.parent = e
    lamp.location = (0.2, -0.38, 1.9)
    lamp.rotation_euler = (math.radians(168), 0, math.radians(0))   # aimed down and back at the canvas (set below)
    kit.aim(lamp, (0, 0, 0))
    tgt = V((0.0, -0.08, 1.15))
    d = tgt - V((0.2, -0.38, 1.9))
    lamp.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return e, mat


RE_ = 3.1


def build_stool(kit, ctx, M):
    """The paint-spattered spare stool (one, moved by the stool cue)."""
    st = kit.empty("spare stool", (0, 0, 0))
    kit.box("spare seat", (0.46, 0.46, 0.05), (0, 0, 0.425), M["easel"], st, bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box("spare leg", (0.05, 0.05, 0.4), (sx * 0.18, sy * 0.18, 0.2), M["easel"], st)
    rnd = random.Random(8)
    for k in range(16):
        m = M["splash"][k % 5]
        r = rnd.uniform(0.012, 0.03)
        kit.sphere("splash", r, (rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), 0.452), m, st, seg=8).scale = (1, 1, 0.25)
    ctx["stool"] = st
    st.hide_render = True


# ------------------------------------------------------------------------------------------ the fade (one look for everyone)
#
# A person who is looked at by nobody thins into raw pine grain, and the pencil lines they were drawn with show through.
# Every faded character (the bus-stop man, Mr Dobbs, Mum, the sting sitter) wears this one look. A cast member's own
# materials are copied once and a mix shader to pine is laid over them: `fade` (0..1) is the whole body, `fade_h` the face.
# The face wipes across from one side with a ragged edge, like grain creeping; the pine face is a texture with the guide lines.


def _pine_branch(nt, image=None):
    """A pine Principled BSDF inside material tree nt (procedural grain on bodies, a drawn texture on a head)."""
    N, Lk = nt.nodes, nt.links
    b = N.new("ShaderNodeBsdfPrincipled")
    b.inputs["Roughness"].default_value = 0.72
    if image is not None:
        t = N.new("ShaderNodeTexImage")
        t.image = image
        t.interpolation = "Linear"
        uv = N.new("ShaderNodeUVMap")
        Lk.new(uv.outputs["UV"], t.inputs["Vector"])
        Lk.new(t.outputs["Color"], b.inputs["Base Color"])
        return b, t
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (5.0, 1.6, 1.6)
    Lk.new(tc.outputs["Object"], mp.inputs["Vector"])
    wave = N.new("ShaderNodeTexWave")
    wave.bands_direction = "X"
    wave.inputs["Scale"].default_value = 1.0
    wave.inputs["Distortion"].default_value = 5.0
    wave.inputs["Detail"].default_value = 3.0
    Lk.new(mp.outputs["Vector"], wave.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    Lk.new(mp.outputs["Vector"], nz.inputs["Vector"])
    mix = N.new("ShaderNodeMath")
    mix.operation = "MULTIPLY_ADD"
    Lk.new(wave.outputs["Fac"], mix.inputs[0])
    mix.inputs[1].default_value = 0.6
    Lk.new(nz.outputs["Fac"], mix.inputs[2])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = (0.36, 0.26, 0.14, 1)
    ramp.color_ramp.elements[1].position = 0.9
    ramp.color_ramp.elements[1].color = (0.62, 0.49, 0.30, 1)
    Lk.new(mix.outputs[0], ramp.inputs["Fac"])
    Lk.new(ramp.outputs["Color"], b.inputs["Base Color"])
    return b, None


def _lay_over(m, branch, factor_socket):
    """Insert Mix(original surface, branch) before the material output."""
    nt = m.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    src = out.inputs["Surface"].links[0].from_socket
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(src, mx.inputs[1])
    nt.links.new(branch.outputs[0], mx.inputs[2])
    nt.links.new(factor_socket, mx.inputs[0])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])


def _math(N, Lk, op, a=None, b=None, clamp=False):
    n = N.new("ShaderNodeMath")
    n.operation = op
    n.use_clamp = clamp
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            Lk.new(v, n.inputs[i])
    return n


def _head_pine(ctx, m, who):
    """The face's pine layer: the pine face texture wherever u < edge (ragged), and all round the back of the head."""
    nt = m.node_tree
    N, Lk = nt.nodes, nt.links
    kind = ctx["story"]["geom"]["faders"][who]
    br, tex = _pine_branch(nt, ctx["pine_faces"][(kind, 0)])
    uv = N.new("ShaderNodeUVMap")
    sep = N.new("ShaderNodeSeparateXYZ")
    Lk.new(uv.outputs["UV"], sep.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 38.0
    Lk.new(uv.outputs["UV"], nz.inputs["Vector"])
    edge, kh = N.new("ShaderNodeValue"), N.new("ShaderNodeValue")
    sub = _math(N, Lk, "SUBTRACT", edge.outputs[0], sep.outputs["X"])
    rag = _math(N, Lk, "MULTIPLY_ADD", nz.outputs["Fac"], 0.07)
    Lk.new(sub.outputs[0], rag.inputs[2])
    sh = _math(N, Lk, "SUBTRACT", rag.outputs[0], 0.035)
    f1 = _math(N, Lk, "MULTIPLY", sh.outputs[0], 20.0, clamp=True)
    d1 = _math(N, Lk, "SUBTRACT", sep.outputs["X"], 0.5)
    d2 = _math(N, Lk, "ABSOLUTE", d1.outputs[0])
    o1 = _math(N, Lk, "SUBTRACT", d2.outputs[0], 0.17)
    o1b = _math(N, Lk, "MULTIPLY", o1.outputs[0], 50.0, clamp=True)
    o2 = _math(N, Lk, "MULTIPLY", o1b.outputs[0], kh.outputs[0], clamp=True)
    mx = _math(N, Lk, "MAXIMUM", f1.outputs[0], o2.outputs[0])
    _lay_over(m, br, mx.outputs[0])
    return edge, kh, tex


def fade_setup(ctx, who):
    """Copy the materials of `who` and lay the pine over them. Done once, the first frame the character exists."""
    root = bpy.data.objects.get(who)
    if root is None:
        return None
    F = {"body": [], "edge": [], "kh": [], "tex": [], "glasses": []}
    top = bpy.data.objects.get(f"{who}.glf1")
    hg = bpy.data.objects.get(f"{who}.headg")
    if top is not None and hg is not None:           # round tortoiseshell rims, centred on the eyes (z 0.08, x +-0.235)
        R_ = faces.HEAD_R
        fm = top.material_slots[0].material if top.material_slots else None
        for nm in ("glf-1", "glf1", "glb"):
            ob = bpy.data.objects.get(f"{who}.{nm}")
            if ob is not None:
                bpy.data.objects.remove(ob, do_unlink=True)
        NSEG, RAD = 14, 0.175
        for sx in (-1, 1):
            for i in range(NSEG):
                ph = 2 * math.pi * (i + 0.5) / NSEG
                x = sx * 0.235 + RAD * math.cos(ph)
                z = 0.08 + RAD * math.sin(ph)
                y = -math.sqrt(max(R_ * R_ - x * x, 0.01)) - 0.035
                ctx["kit"].box(f"{who}.glr{sx}_{i}", (2 * RAD * math.sin(math.pi / NSEG) + 0.012, 0.05, 0.05), (x, y, z), fm, hg,
                               rot=(0, -(ph + math.pi / 2), math.atan2(x, -y) * 0.0))
        ctx["kit"].box(f"{who}.glrbridge", (0.14, 0.05, 0.045), (0, -R_ - 0.035, 0.1), fm, hg)
    done = {}
    for ob in [root] + list(root.children_recursive):
        if ob.type != "MESH":
            continue
        if any(k in ob.name for k in (".earpatch", ".nosepatch", ".noseink")):
            continue
        if ".gl" in ob.name:                         # the lenses and frames go when the face does
            F["glasses"].append(ob)
            continue
        is_head = ob.name.endswith(".headm")
        for slot in ob.material_slots:
            om = slot.material
            if om is None or not om.use_nodes:
                continue
            key = (om.name, is_head)
            if key not in done:
                m = om.copy()
                if is_head:
                    edge, kh, tex = _head_pine(ctx, m, who)
                    F["edge"].append(edge)
                    F["kh"].append(kh)
                    F["tex"].append(tex)
                else:
                    br, _ = _pine_branch(m.node_tree)
                    N_, Lk_ = m.node_tree.nodes, m.node_tree.links
                    val = N_.new("ShaderNodeValue")
                    geo = N_.new("ShaderNodeNewGeometry")
                    sep = N_.new("ShaderNodeSeparateXYZ")
                    Lk_.new(geo.outputs["Position"], sep.inputs["Vector"])
                    sub = _math(N_, Lk_, "SUBTRACT", sep.outputs["Z"], val.outputs[0])
                    fac = _math(N_, Lk_, "MULTIPLY", sub.outputs[0], 14.0, clamp=True)
                    _lay_over(m, br, fac.outputs[0])
                    F["body"].append(val)
                done[key] = m
            slot.material = done[key]
    return F


def fade_update(ctx, tl, t, who):
    """Set one faded character's pine from its acting keys. Returns (body, head) levels."""
    keys = tl["acting"].get(who, [])
    fb = _ac._held(keys, "fade", t, 0.0)
    fh = _ac._held(keys, "fade_h", t, fb)
    if who not in ctx["fade"]:
        ctx["fade"][who] = fade_setup(ctx, who)
    F = ctx["fade"][who]
    if F is None:
        return 0.0, 0.0
    fz = _ac._held(keys, "fade_z", t, None)
    if fz is None:
        fz = -5.0 if fb > 0.5 else 9.0       # the colour reaches up to this height (m): below it colour, above it raw pine
    for v in F["body"]:
        v.outputs[0].default_value = float(fz)
    for e in F["edge"]:
        e.outputs[0].default_value = 0.33 + 0.37 * float(fh)
    for k in F["kh"]:
        k.outputs[0].default_value = min(1.0, max(0.0, float(fh) * 4.0))
    kind = ctx["story"]["geom"]["faders"][who]
    st = int(_ac._switch(keys, "stage", t, 0))
    for tex in F["tex"]:
        tex.image = ctx["pine_faces"][(kind, min(st, 2))]
    for g in F["glasses"]:
        g.hide_render = g.hide_render or fh > 0.55
    return fb, fh


# ------------------------------------------------------------------------------------------ colour fills, patches, the meter
#
# Things painted into town arrive as bare pine with the pencil lines still on, then the colour fills in. A "ramp" material is a
# plastic colour with the pine laid over it: mode "uniform" fades from pine to colour as a value runs 0 to 1; mode "x" or "z"
# is a front, colour on one side of a world coordinate (the cake filling in sideways, the colour climbing Theo from the boots).


def _lines_mask(nt):
    """Graphite construction lines: thin bands along two object axes, as a 0/1 mask."""
    N, Lk = nt.nodes, nt.links
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    Lk.new(tc.outputs["Object"], sep.inputs["Vector"])
    masks = []
    for comp, freq in (("Y", 7.0), ("Z", 6.0)):
        sc = _math(N, Lk, "MULTIPLY", sep.outputs[comp], freq)
        fr = _math(N, Lk, "FRACT", sc.outputs[0])
        sb = _math(N, Lk, "SUBTRACT", fr.outputs[0], 0.5)
        ab = _math(N, Lk, "ABSOLUTE", sb.outputs[0])
        lt = _math(N, Lk, "LESS_THAN", ab.outputs[0], 0.045)
        masks.append(lt)
    mx = _math(N, Lk, "MAXIMUM", masks[0].outputs[0], masks[1].outputs[0])
    return mx.outputs[0]


def ramp_mat(kit, ctx, name, hexc, rough=0.5, mode="uniform", lines=False, k=14.0):
    """Returns the material; its value node is kept in ctx["ramps"][name] (uniform: 0 pine .. 1 colour; x / z: the front)."""
    m = kit.plastic(hexc, rough, name)
    nt = m.node_tree
    N, Lk = nt.nodes, nt.links
    br, _ = _pine_branch(nt)
    if lines:
        bc = br.inputs["Base Color"]
        src = bc.links[0].from_socket
        mixc = N.new("ShaderNodeMixRGB")
        mixc.inputs[2].default_value = (0.17, 0.16, 0.16, 1.0)
        Lk.new(_lines_mask(nt), mixc.inputs[0])
        Lk.new(src, mixc.inputs[1])
        Lk.new(mixc.outputs[0], bc)
    val = N.new("ShaderNodeValue")
    if mode == "uniform":
        fac = _math(N, Lk, "SUBTRACT", 1.0, val.outputs[0], clamp=True)
    else:
        geo = N.new("ShaderNodeNewGeometry")
        sep = N.new("ShaderNodeSeparateXYZ")
        Lk.new(geo.outputs["Position"], sep.inputs["Vector"])
        sub = _math(N, Lk, "SUBTRACT", sep.outputs[mode.upper()], val.outputs[0])
        fac = _math(N, Lk, "MULTIPLY", sub.outputs[0], k, clamp=True)
    _lay_over(m, br, fac.outputs[0])
    ctx.setdefault("ramps", {})[name] = val
    return m


def curved_patch(kit, name, mat, parent, theta_c, span, zc, zh, off=0.03, sgn=1, nu=10, nv=6):
    """A curved decal on the side/front of a head (head units, 1 cm proud): theta_c degrees round from the front toward sgn * x."""
    R = faces.HEAD_R + off
    verts, uvs, fcs = [], [], []
    for j in range(nv + 1):
        z = zc + (j / nv - 0.5) * zh
        for i in range(nu + 1):
            th = math.radians(theta_c) + (i / nu - 0.5) * span
            verts.append((sgn * R * math.sin(th), -R * math.cos(th), z))
            uvs.append((i / nu if sgn > 0 else 1 - i / nu, j / nv))
    for j in range(nv):
        for i in range(nu):
            a = j * (nu + 1) + i
            fcs.append((a, a + 1, a + nu + 2, a + nu + 1))
    ob = kit.mesh_obj(name, verts, fcs, mat, parent, smooth=True)
    uv = ob.data.uv_layers.new(name="UVMap")
    for poly in ob.data.polygons:
        for li in poly.loop_indices:
            uv.data[li].uv = uvs[ob.data.loops[li].vertex_index]
    return ob


def patch_mat(kit, ctx, name, im, skin_hex, rough=0.7, ink=False):
    """A decal picture with alpha, mixed toward the skin colour by a value (0 raw pine .. 1 skin)."""
    path = ctx["wd"] / f"{name}.png"
    im.save(path)
    img = bpy.data.images.load(str(path), check_existing=False)
    img.colorspace_settings.name = "sRGB"
    m = kit._new(f"patch {name}")
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    nt.links.new(tex.outputs["Alpha"], b.inputs["Alpha"])
    val = nt.nodes.new("ShaderNodeValue")
    if ink:
        nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    else:
        mix = nt.nodes.new("ShaderNodeMixRGB")
        mix.inputs[2].default_value = tuple(kit.col(skin_hex))
        nt.links.new(val.outputs[0], mix.inputs[0])
        nt.links.new(tex.outputs["Color"], mix.inputs[1])
        nt.links.new(mix.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    kit._fogged(m, b.outputs[0])
    ctx.setdefault("ramps", {})[name] = val
    return m


def build_patches(kit, ctx, story):
    """The ear patch on me (left side, every shot until it is finished) and the nose patch on Theo."""
    ctx["patch"] = {}
    me, th = bpy.data.objects.get("me.headg"), bpy.data.objects.get("theo.headg")
    if me is not None:
        m = patch_mat(kit, ctx, "ear", ear_patch_image(), story["cast"]["me"]["skin"])
        ctx["patch"]["ear"] = [curved_patch(kit, "me.earpatch", m, me, 96, 0.62, -0.02, 0.36, sgn=1)]
    if th is not None:
        m = patch_mat(kit, ctx, "nose", nose_patch_image(), story["cast"]["theo"]["skin"])
        mi = patch_mat(kit, ctx, "noseink", nose_patch_image(True), story["cast"]["theo"]["skin"], ink=True)
        ctx["patch"]["nose"] = [curved_patch(kit, "theo.nosepatch", m, th, 0, 0.62, -0.10, 0.44, off=0.03),
                                curved_patch(kit, "theo.noseink", mi, th, 0, 0.36, -0.13, 0.25, off=0.036)]


def _ramp_value(tl, name, t, default=0.0):
    """A ramp cue's value at t: from the last value to v over dur seconds, eased."""
    v = default
    for c in _cues(tl, "ramp"):
        if c["name_"] != name or c["t"] > t + 1e-9:
            continue
        dur = c.get("dur", 0.0)
        p = 1.0 if dur <= 0 else _ss((t - c["t"]) / dur)
        v = v + (c["v"] - v) * p
        if p < 1.0:
            return v
    return v


def _lens_at(spec, shot, t):
    keys = spec["cam"]
    if len(keys) == 1:
        return keys[0][3]
    u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
    if u <= keys[0][0]:
        return keys[0][3]
    for a, b in zip(keys, keys[1:]):
        if u <= b[0]:
            v = _ss((u - a[0]) / max(1e-6, b[0] - a[0]))
            return a[3] + (b[3] - a[3]) * v
    return keys[-1][3]


def _emit_mat(hexc):
    m = bpy.data.materials.new(f"meter {hexc}")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    em = nt.nodes.new("ShaderNodeEmission")
    r, g, b = (int(hexc.lstrip("#")[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    em.inputs["Color"].default_value = (r ** 2.2, g ** 2.2, b ** 2.2, 1.0)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m, em


def build_meter(kit, ctx):
    """The week meter: seven rounded squares in a row at the top of the frame, Monday on the left. Camera-parented planes, drawn
    by animate each frame so they sit at the same place in the picture whatever the lens. Today's square is bare pine with a
    pencil outline, the days before it are filled with colour, and Thursday has a little graphite brush tick under it."""
    cam = kit.OBJ["cam"]
    mats = {}
    for key, hexc in {**{f"d{i}": c for i, c in enumerate(DAYCOL)}, "pine": "#e2c590", "pencil": "#2e2c2c", "empty": "#7d7a74",
                      "rim": "#2e2c2c"}.items():
        mats[key] = _emit_mat(hexc)
    ctx["meter"] = {"mats": mats, "sq": [], "tick": None}

    def plane(name, mat):
        ob = kit.plane(name, (1.0, 1.0), (0, 0, -1), mat, cam, (0, 0, 0))
        for a in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
            if hasattr(ob, a):
                setattr(ob, a, False)
        return ob

    for k in range(7):
        rim = plane(f"meter rim {k}", mats["rim"][0])
        inner = plane(f"meter sq {k}", mats["empty"][0])
        ctx["meter"]["sq"].append((rim, inner))
    ctx["meter"]["tick"] = plane("meter tick", mats["pencil"][0])


def update_meter(kit, ctx, tl, t, spec, shot):
    mt = ctx["meter"]
    lens = _lens_at(spec, shot, t)
    d = 0.5
    H = 2 * d * 12.0 / lens
    W = H * 9.0 / 16.0
    s, pitch = 0.074 * W, 0.104 * W
    yc = (0.5 - 0.115) * H
    ev = bpy.context.scene.view_settings.exposure
    gain = 2.2 * (2.0 ** (-ev * 0.7))
    cd = _last(_cues(tl, "day"), t)
    day = int(cd["d"]) if cd else 0
    for k, (rim, inner) in enumerate(mt["sq"]):
        x = (k - 3) * pitch
        key = f"d{k}" if k < day else ("pine" if k == day else "empty")
        for ob, sz, z, mk in ((rim, s * 1.2, -d, "rim"), (inner, s, -d + 0.002, key)):
            ob.location = (x, yc, z)
            ob.scale = (sz, sz, 1.0)
            ob.data.materials[0] = mt["mats"][mk][0]
        em = mt["mats"][key][1]
        em.inputs["Strength"].default_value = gain * (0.5 if key == "empty" else 1.0)
        mt["mats"]["rim"][1].inputs["Strength"].default_value = gain * 0.6
    tk = mt["tick"]
    tk.location = ((3 - 3) * pitch + s * 0.15, yc - s * 0.88, -d + 0.003)
    tk.scale = (s * 0.12, s * 0.5, 1.0)
    tk.rotation_euler = (0, 0, math.radians(-24))
    mt["mats"]["pencil"][1].inputs["Strength"].default_value = gain * 0.8


def _site_materials(kit, M):
    M["pave"] = kit.concrete("#bdb9b0", scale=2.0, stains=0.12, name="pavement", rough=0.8)
    M["road"] = kit.concrete("#55575d", scale=2.0, stains=0.2, name="street", rough=0.7)
    M["cream"] = kit.plastic("#eadfc3", 0.8, "facade cream")
    M["terra"] = kit.plastic("#c5704e", 0.8, "facade terracotta")
    M["sage"] = kit.plastic("#9cb59a", 0.8, "facade sage")
    M["sky"] = kit.plastic("#8fb0d0", 0.8, "facade blue")
    M["mustard"] = kit.plastic("#d9b04a", 0.8, "facade mustard")
    M["pane"] = kit.plastic("#3b5068", 0.25, "dark pane")
    M["shelter"] = kit.plastic("#9fc6d6", 0.5, "shelter panel")
    M["metal"] = kit.plastic("#5e646b", 0.4, "shelter metal")
    M["signdisc"] = kit.plastic("#d8b030", 0.5, "plain disc")
    M["cloth"] = kit.plastic("#f1ede2", 0.9, "table cloth white")
    M["toast"] = kit.plastic("#d0a05a", 0.7, "toast")
    M["plate"] = kit.plastic("#f4f1ea", 0.4, "plate")
    M["chair"] = kit.plastic("#8d4a3a", 0.6, "cafe chair")
    M["tile"] = kit.plastic("#d9cdb8", 0.6, "bakery tile")
    M["loaf"] = kit.plastic("#c98a4a", 0.7, "loaf")
    M["loaf2"] = kit.plastic("#b0733a", 0.7, "loaf dark")
    M["counter"] = kit.plastic("#a9794a", 0.55, "bakery counter")
    M["counter_top"] = kit.plastic("#ebe3d3", 0.4, "counter top")
    M["flatwall"] = kit.plastic("#d9dde0", 0.9, "flat wall")
    M["flatfloor"] = kit.planks("#b99a6a", "#8f7348", scale=1.0, axis="Y", name="flat boards", rough=0.6)
    M["win_cool"] = kit.emit("#dcecff", 5.0, "flat window")
    M["slate"] = kit.plastic("#3a3f4a", 0.9, "slate wall")
    M["win_morn"] = kit.emit("#fff0d0", 5.0, "morning window")
    M["quilt"] = kit.plastic("#2f7f82", 0.9, "quilt")
    M["greenpaint"] = kit.plastic("#5fd068", 0.4, "green paint")


def _room(kit, M, cx, cy, w, d, x_floor, wall, ceil=True, h=3.0, front=False, back_y=None):
    kit.box("site floor", (w, d, 0.1), (cx, cy, -0.05), x_floor)
    by = cy + d / 2
    kit.box("site back wall", (w, 0.1, h), (cx, by, h / 2), wall)
    for sx in (-1, 1):
        kit.box("site side wall", (0.1, d, h), (cx + sx * w / 2, cy, h / 2), wall)
    if ceil:
        kit.box("site ceiling", (w, d, 0.1), (cx, cy, h + 0.05), M["ceilmat"])
    if front:
        kit.box("site front wall", (w, 0.1, h), (cx, cy - d / 2, h / 2), wall)


# ------------------------------------------------------------------------------------------ Mom's hall


def chair(kit, M, name, x, y, facing):
    """A dining chair seat at (x, y); facing: 'w' | 'e' | 's' | 'n' is the way a sitter looks."""
    kit.box(f"{name} seat", (0.46, 0.46, 0.05), (x, y, 0.45), M["table"], bevel=0.01)
    for lx in (-0.2, 0.2):
        for ly in (-0.2, 0.2):
            kit.box(f"{name} leg", (0.045, 0.045, 0.43), (x + lx, y + ly, 0.215), M["table"])
    bx, by = {"w": (x + 0.22, y), "e": (x - 0.22, y), "s": (x, y + 0.22), "n": (x, y - 0.22)}[facing]
    sz = (0.05, 0.46, 0.55) if facing in ("w", "e") else (0.46, 0.05, 0.55)
    kit.box(f"{name} back", sz, (bx, by, 0.75), M["table"], bevel=0.01)


def build_hall(kit, ctx, M, wd):
    ctx["hall"] = {}
    cx, cy = (HL0 + HL1) / 2, (HY0 + HY1) / 2
    wx, wy = HL1 - HL0, HY1 - HY0
    kit.box("hall floor", (wx, wy, 0.1), (cx, cy, -0.05), M["floor2"])
    kit.box("hall ceil", (wx, wy, 0.1), (cx, cy, HH + 0.05), M["ceilmat"])
    kit.box("hall e", (0.1, wy, HH), (HL1 + 0.05, cy, HH / 2), M["hallwall"])
    kit.box("hall n", (wx + 0.2, 0.1, HH), (cx, HY1 + 0.05, HH / 2), M["hallwall"])
    # the west wall, with the hole of my door (y 3.4 .. 4.3) and the dark little room behind it
    dy0, dy1 = MYDOOR[1] - 0.45, MYDOOR[1] + 0.45
    kit.box("hall w a", (0.1, dy0 - HY0, HH), (HL0 - 0.05, (HY0 + dy0) / 2, HH / 2), M["hallwall"])
    kit.box("hall w b", (0.1, HY1 - dy1, HH), (HL0 - 0.05, (HY1 + dy1) / 2, HH / 2), M["hallwall"])
    kit.box("hall w c", (0.1, dy1 - dy0, HH - 2.1), (HL0 - 0.05, MYDOOR[1], 2.1 + (HH - 2.1) / 2), M["hallwall"])
    kit.box("my room floor", (1.6, 1.6, 0.1), (HL0 - 0.9, MYDOOR[1], -0.05), M["floor2"])
    kit.box("my room back", (0.1, 1.6, 2.6), (HL0 - 1.75, MYDOOR[1], 1.3), M["slate"])
    kit.box("my room n", (1.6, 0.1, 2.6), (HL0 - 0.9, MYDOOR[1] + 0.8, 1.3), M["slate"])
    kit.box("my room s", (1.6, 0.1, 2.6), (HL0 - 0.9, MYDOOR[1] - 0.8, 1.3), M["slate"])
    kit.box("my room ceil", (1.6, 1.6, 0.1), (HL0 - 0.9, MYDOOR[1], 2.65), M["slate"])
    kit.box("my door frame", (0.12, 0.06, 2.12), (HL0, dy0, 1.06), M["white"])
    kit.box("my door frame", (0.12, 0.06, 2.12), (HL0, dy1, 1.06), M["white"])
    kit.box("my door frame", (0.12, dy1 - dy0, 0.06), (HL0, MYDOOR[1], 2.12), M["white"])
    # the door end (south), with a pane of morning sun
    kit.box("hall s a", (cx - 0.45 - HL0, 0.1, HH), ((HL0 + cx - 0.45) / 2, HY0 - 0.05, HH / 2), M["hallwall"])
    kit.box("hall s b", (HL1 - cx - 0.45, 0.1, HH), ((HL1 + cx + 0.45) / 2, HY0 - 0.05, HH / 2), M["hallwall"])
    kit.box("hall s c", (0.9, 0.1, HH - 2.1), (cx, HY0 - 0.05, 2.1 + (HH - 2.1) / 2), M["hallwall"])
    ctx["hall"]["door_glass"] = kit.box("hall door", (0.9, 0.06, 2.1), (cx, HY0 - 0.12, 1.05), M["glass_door"])
    # the stairs up the east wall to the north, a window above the landing
    run, rise, n = 0.24, 0.143, 14
    for k in range(n):
        kit.box(f"stair {k}", (1.1, run, rise * (k + 1)), (HL1 - 0.55, 3.6 + run * k + run / 2, rise * (k + 1) / 2), M["table"])
    top = rise * n
    kit.box("landing", (1.1, HY1 - (3.6 + run * n), top), (HL1 - 0.55, (HY1 + 3.6 + run * n) / 2, top / 2), M["table"])
    kit.box("stair window", (1.0, 0.04, 1.2), (HL1 - 0.8, HY1 - 0.01, 2.9), M["win_cool"])
    # the frames (art) along the west wall
    frames = []
    for k, y in enumerate((-0.6, 0.35, 1.2, 2.55, 3.0, 5.05, 5.9, 6.75)):
        if abs(y - MYDOOR[1]) < 0.9:
            continue
        w, h = 0.36 + 0.05 * (k % 3), 0.44
        f = kit.empty("hall frame", (HL0 + 0.02, y, 1.55 + 0.08 * ((k * 5) % 3 - 1)))
        kit.box("frame", (0.04, w + 0.05, h + 0.05), (0, 0, 0), M["frame"], f)
        pm = img_mat(kit, f"art{k}", art_image(k), wd, rough=0.7)
        pl = uvplane(kit, "art", (w, h), (0.0215, 0, 0), None, f, (math.pi / 2, 0, math.pi / 2))
        pl.data.materials.append(pm)
        frames.append(f)
    ctx["hall"]["frames"] = frames
    # Mom's old folded easel and the panel turned to the wall, on the west wall near the door end
    ex = HL0 + 0.12
    for k, yy in enumerate((-0.55, -0.4, -0.25)):
        kit.box("old easel leg", (0.04, 0.05, 1.75), (ex + 0.06 * (k == 1), yy, 0.9), M["easel"], rot=(0, math.radians(8), 0))
    kit.box("old easel hinge", (0.06, 0.4, 0.05), (ex + 0.1, -0.4, 1.0), M["dark"])
    kit.box("old panel", (0.035, 0.66, 0.84), (HL0 + 0.05, -1.05, 0.44), M["pine"], bevel=0.004)
    kit.box("old panel back", (0.006, 0.6, 0.78), (HL0 + 0.076, -1.05, 0.44), M["canvas_back"])
    # the dining table (high enough for sitters' knees), three chairs, plates, the salt
    tx, ty = TABLE
    kit.box("dining top", (0.95, 1.5, 0.05), (tx, ty, 0.88), M["table"], bevel=0.01)
    for sx in (-0.42, 0.42):
        for sy in (-0.68, 0.68):
            kit.box("dining leg", (0.06, 0.06, 0.86), (tx + sx, ty + sy, 0.43), M["table"])
    chair(kit, M, "chair mom", tx, ty + 1.0, "s")
    chair(kit, M, "chair me", tx - 0.75, ty, "e")
    chair(kit, M, "chair theo", tx + 0.75, ty, "w")
    ctx["hall"]["plates"] = []
    for k, (px, py) in enumerate(((tx, ty + 0.5), (tx - 0.3, ty), (tx + 0.3, ty))):
        pl = kit.cyl("plate", 0.12, 0.02, (px, py, 0.915), M["plate"])
        pl.hide_render = k == 2
        ctx["hall"]["plates"].append(pl)
    ctx["hall"]["salt"] = kit.cyl("salt", 0.028, 0.08, (tx, ty - 0.1, 0.945), M["white"])
    # lights: day (sun at the door end, fill), night (a wall lamp, a cool rim from the stair window), evening (the lamp over the table)
    kit.light("hall sun", "AREA", (cx, HY0 + 0.1, 1.5), 260.0, "#ffe3b0", size=1.2).rotation_euler = (math.radians(90), 0, 0)
    kit.light("hall fill", "AREA", (cx, 2.5, 3.2), 520.0, "#fff2dc", size=3.0)
    kit.light("hall fill2", "AREA", (cx, 5.5, 3.2), 420.0, "#fff2dc", size=3.0)
    kit.box("hall lamp shade", (0.12, 0.16, 0.22), (HL0 + 0.1, 5.4, 1.85), M["lampglow"])
    kit.light("hall lamp", "POINT", (HL0 + 0.45, 5.4, 1.9), 220.0, "#ffb06a", size=0.25)
    kit.light("hall lamp b", "POINT", (HL0 + 0.45, 1.2, 1.9), 90.0, "#ffb06a", size=0.25)
    rim = kit.light("hall rim", "AREA", (HL1 - 1.1, HY1 - 0.4, 2.8), 600.0, "#78a0e8", size=1.6)
    rim.rotation_euler = V((-0.1, -1.0, -0.5)).to_track_quat("-Z", "Y").to_euler()
    kit.light("dine lamp", "POINT", (tx, ty, 2.3), 300.0, "#ffc890", size=0.3)
    kit.light("dine fill", "AREA", (cx, 3.0, 3.3), 380.0, "#ffd9b0", size=3.0)
    ctx["site_lights"]["hall"] = ["hall sun", "hall fill", "hall fill2"]
    ctx["site_lights"]["hallnight"] = ["hall lamp", "hall lamp b", "hall rim"]
    ctx["site_lights"]["halleve"] = ["dine lamp", "dine fill", "hall lamp b"]


def build_bus(kit, ctx, M):
    X, Y = BUS_[0], BUS_[1]
    kit.box("bus pavement", (22, 4.2, 0.2), (X, 1.0, -0.1), M["pave"])
    kit.box("bus road", (22, 7.0, 0.2), (X, -4.6, -0.22), M["road"])
    facades = [(X - 7.4, "cream"), (X - 4.2, "terra"), (X - 1.0, "sage"), (X + 2.2, "mustard"), (X + 5.4, "sky"), (X + 8.6, "cream")]
    for k, (fx, mk) in enumerate(facades):
        hgt = 4.6 + 0.8 * (k % 3)
        kit.box("bus facade", (3.2, 3.0, hgt), (fx, 4.7, hgt / 2), M[mk])
        for wx in (-0.8, 0.8):
            for wz in (1.9, 3.5):
                kit.box("bus window", (0.8, 0.04, 1.0), (fx + wx, 3.17, wz), M["pane"])
        kit.box("bus door", (0.9, 0.05, 2.0), (fx, 3.17, 1.0), M["door"])
    kit.box("bus roof", (3.8, 1.8, 0.1), (X, 1.25, 2.5), M["metal"])
    for sx in (-1.8, 1.8):
        for sy in (0.45, 2.05):
            kit.box("bus post", (0.08, 0.08, 2.5), (X + sx, sy, 1.25), M["metal"])
    kit.box("bus back panel", (3.6, 0.05, 1.8), (X, 2.07, 1.3), M["shelter"])
    # the new bench: pine slats with graphite construction lines, going bright grass green
    bm = ramp_mat(kit, ctx, "bench", "#5fd068", 0.45, "uniform", lines=True)
    bx, by = X + 0.1, 1.55
    for k, dy in enumerate((-0.2, 0.0, 0.2)):
        kit.box("bench seat", (1.9, 0.17, 0.045), (bx, by + dy, 0.48), bm, bevel=0.006)
    for k, z in enumerate((0.74, 0.9)):
        kit.box("bench back", (1.9, 0.04, 0.12), (bx, by + 0.4, z), bm, bevel=0.006)
    for sx in (-0.88, 0.88):
        kit.box("bench leg", (0.07, 0.62, 0.46), (bx + sx, by + 0.1, 0.23), bm)
        kit.box("bench arm", (0.07, 0.62, 0.05), (bx + sx, by + 0.1, 0.68), bm)
        kit.box("bench post", (0.07, 0.07, 0.4), (bx + sx, by + 0.4, 0.68), bm)
    kit.cyl("bus pole", 0.04, 2.6, (X + 2.9, -0.55, 1.3), M["metal"])
    kit.cyl("bus disc", 0.26, 0.04, (X + 2.9, -0.6, 2.45), M["signdisc"], rot=(math.pi / 2, 0, 0))
    kit.light("bus sun", "SUN", (X, 0, 12), 4.2, "#fff0d6", rot=(math.radians(58), 0, math.radians(-28)))
    ctx["site_lights"]["bus"] = ["bus sun"]


def build_cafe(kit, ctx, M, wd):
    X, Y = CAF_[0], CAF_[1]
    _room(kit, M, X, 0.6, 6.0, 5.0, M["floor"], M["plaster"], front=False)
    kit.box("cafe window", (3.4, 0.04, 1.5), (X, 3.02, 1.65), M["win_day"])
    for sx in (-1.7, 0.0, 1.7):
        kit.box("cafe mullion", (0.07, 0.06, 1.5), (X + sx, 2.99, 1.65), M["white"])
    kit.box("cafe sill", (3.6, 0.2, 0.05), (X, 2.9, 0.88), M["white"])
    # the window flower box on the sill: red flowers on the left, pencil outlines on bare pine on the right
    fb = uvplane(kit, "flower box", (2.6, 0.76), (X, 2.84, 1.28), None, None, (math.pi / 2, 0, 0))
    fb.data.materials.append(img_mat(kit, "flowerbox", flowerbox_image(), wd, rough=0.8, alpha=True))
    kit.box("cafe table top", (0.74, 0.9, 0.04), (X, Y - 0.6, 0.88), M["cloth"], bevel=0.01)
    kit.box("cafe table leg", (0.06, 0.06, 0.86), (X, Y - 0.6, 0.43), M["cloth"])
    for sx, sgn in ((-0.75, 1), (0.75, -1)):
        kit.box("cafe seat", (0.46, 0.46, 0.05), (X + sx, Y - 0.6, 0.425), M["chair"], bevel=0.01)
        kit.box("cafe chair back", (0.05, 0.46, 0.5), (X + sx - sgn * 0.26, Y - 0.6, 0.72), M["chair"], bevel=0.01)
    kit.light("cafe key", "AREA", (X, -0.6, 2.7), 190.0, "#fff1dc", size=2.5).rotation_euler = (math.radians(20), 0, 0)
    kit.light("cafe fill", "AREA", (X, 1.2, 2.8), 120.0, "#ffe8c8", size=2.5)
    ctx["site_lights"]["cafe"] = ["cafe key", "cafe fill"]


def build_bakery(kit, ctx, M):
    X = BAK_[0] - 0.4
    _room(kit, M, X, 0.6, 6.0, 5.2, M["tile"], M["cream"], front=True)
    kit.box("bake front window", (3.2, 0.04, 1.6), (X, -1.93, 1.6), M["win_day"])
    rnd = random.Random(4)
    for k, z in enumerate((1.0, 1.55, 2.1)):
        kit.box("bake shelf", (4.4, 0.34, 0.05), (X, 2.8, z), M["easel"])
        for j in range(8):
            mk = "loaf" if (j + k) % 2 else "loaf2"
            if (j + k) % 3 == 0:
                kit.box("bake loaf", (0.34, 0.14, 0.12), (X - 1.9 + j * 0.54, 2.8, z + 0.085), M[mk], bevel=0.05)
            else:
                kit.sphere("bake bun", 0.1, (X - 1.9 + j * 0.54, 2.8, z + 0.13), M[mk]).scale = (1.2, 0.9, 0.8)
    kit.box("bake counter", (3.4, 0.7, 1.0), (X + 0.4, 0.9, 0.5), M["counter"], bevel=0.01)
    kit.box("bake counter top", (3.6, 0.82, 0.05), (X + 0.4, 0.9, 1.025), M["counter_top"], bevel=0.01)
    # the cake: three tiers whose pink frosting is still filling in, from the left, with the pencil lines still on the pine side
    cm = ramp_mat(kit, ctx, "cake", "#f29ab5", 0.5, "x", lines=True, k=9.0)
    cx_, cy_ = BAK_[0] + 0.15, 0.9
    kit.cyl("cake plate", 0.36, 0.03, (cx_, cy_, 1.065), M["plate"])
    for z, r, h in ((1.08, 0.3, 0.17), (1.25, 0.22, 0.15), (1.4, 0.15, 0.13)):
        kit.cyl("cake tier", r, h, (cx_, cy_, z + h / 2), cm, n=32)
    kit.sphere("cake cherry", 0.04, (cx_ - 0.05, cy_, 1.57), M["splash"][1])
    kit.light("bake key", "AREA", (X + 0.4, -1.1, 2.7), 210.0, "#fff1dc", size=2.5).rotation_euler = (math.radians(15), 0, 0)
    kit.light("bake back", "AREA", (X + 0.4, 2.0, 2.9), 110.0, "#ffe8c8", size=2.5)
    ctx["site_lights"]["bake"] = ["bake key", "bake back"]


def build_bed(kit, ctx, M, wd):
    """My bedroom, in morning light: the bed's head against the north wall (the window behind my pillow), the foot to the south."""
    X = BED_[0]
    _room(kit, M, X, 0.0, 3.8, 3.8, M["flatfloor"], M["flatwall"], front=False)
    kit.box("bed window", (1.5, 0.04, 1.3), (X - 0.2, 1.83, 1.6), M["win_morn"])
    for sx in (-0.95, -0.2, 0.55):
        kit.box("bed mullion", (0.05, 0.06, 1.3), (X + sx, 1.80, 1.6), M["white"])
    kit.box("bed mattress", (1.0, 2.0, 0.22), (X, 0.0, 0.45), M["tall"], bevel=0.02)
    kit.box("bed quilt", (1.04, 1.4, 0.08), (X, -0.3, 0.6), M["quilt"], bevel=0.02)
    for sx in (-0.5, 0.5):
        for sy in (-0.95, 0.95):
            kit.box("bed leg", (0.07, 0.07, 0.34), (X + sx, sy, 0.17), M["table"])
    kit.box("bed headboard", (1.1, 0.07, 0.95), (X, 1.02, 0.7), M["table"], bevel=0.01)
    kit.box("bed footboard", (1.1, 0.07, 0.62), (X, -1.02, 0.56), M["table"], bevel=0.01)
    kit.box("bed pillow", (0.56, 0.36, 0.13), (X, 0.78, 0.62), M["tall"], bevel=0.04)
    kit.box("bed nightstand", (0.45, 0.4, 0.5), (X + 0.95, 0.85, 0.25), M["table"])
    kit.light("bed sun", "AREA", (X - 0.2, 1.4, 2.6), 260.0, "#fff0d0", size=2.4).rotation_euler = (math.radians(-80), 0, 0)
    kit.light("bed key", "AREA", (X + 0.2, -1.6, 2.5), 140.0, "#fff4e4", size=2.4).rotation_euler = (math.radians(20), 0, 0)
    ctx["site_lights"]["bed"] = ["bed sun", "bed key"]


def build_props(kit, ctx, M):
    P = {}
    P["canvas_carry"] = [kit.box("carried canvas", (0.5, 0.03, 0.62), (0, 0, 0), M["pine"])]
    # the brush tip on my panel (S11b): a handle and a bristle tip, set by animate against easel 8's canvas
    P["tipbrush"] = [kit.box("tip handle", (0.02, 0.3, 0.02), (0, 0, 0), M["brush"], rot=(0.5, 0, 0.2)),
                     kit.box("tip bristle", (0.03, 0.07, 0.03), (0, 0, 0), M["bristle"], rot=(0.5, 0, 0.2)),
                     kit.sphere("tip paint", 0.022, (0, 0, 0), M["greenpaint"])]
    # Mom's easel in the life room (back to the room, her old pine panel on it), beside mine
    e = kit.empty("mom easel", (0, 0, 0))
    for sx in (-0.34, 0.34):
        kit.box("me leg", (0.05, 0.05, 1.9), (sx, 0, 0.95), M["easel"], e)
    kit.box("me shelf", (0.8, 0.2, 0.04), (0, -0.07, 0.62), M["easel"], e)
    kit.box("me top", (0.78, 0.06, 0.05), (0, 0, 1.82), M["easel"], e)
    kit.box("me back leg", (0.05, 0.05, 1.7), (0, 0.4, 0.85), M["easel"], e, rot=(math.radians(-13), 0, 0))
    kit.box("me panel", (0.6, 0.035, 0.75), (0, -0.05, 1.1), M["pine"], e, bevel=0.004)
    th = math.radians(ctx["TH"][7] + 13)
    e.location = (RE_ * math.cos(th), RE_ * math.sin(th), 0)
    e.rotation_euler = (0, 0, th + math.pi / 2)
    ctx["mom_easel"] = e
    for objs in P.values():
        for o in objs:
            o.hide_render = True
    P["mom_easel"] = [e]
    e.hide_render = True
    return P


# ------------------------------------------------------------------------------------------ lights, build
def build_lights(kit, ctx):
    for k, th in enumerate(ctx["TH"]):
        x, y = 4.5 * math.cos(math.radians(th)), 4.5 * math.sin(math.radians(th))
        kit.light(f"room fill {k}", "POINT", (x, y, 2.7), 26.0, "#ffcf9a", size=0.4)
    for k, (x, y) in enumerate(((-1.4, -1.6), (1.4, -1.6), (0.0, 2.4))):
        kit.light(f"room fill c{k}", "POINT", (x, y, 2.9), 16.0, "#ffd7aa", size=0.4)
    for k, (x, y, z) in enumerate(((1.3, -1.3, 0.25), (-1.3, -1.2, 0.25))):
        kit.light(f"foot {k}", "POINT", (x, y, z), 14.0, "#ffa860", size=0.15)
    rim = kit.light("north rim", "AREA", (0.0, 4.6, 2.3), 260.0, "#9bb8e8", size=2.4)
    rim.rotation_euler = (V((0, -1.5, -1.2)).to_track_quat("-Z", "Y").to_euler())
    for nm in list(kit.LIGHTS):
        if nm.startswith(("hall ", "kit ", "north rim", "dine ", "cafe ", "bake ", "bed ")):
            kit.LIGHTS[nm]["obj"].visible_camera = False
    kit.light("post light", "POINT", (-2.6, -9.0, GROUND + 3.4), 700.0, "#ffd29a", size=0.3)
    kit.light("ext wash", "AREA", (-12.0, -20.0, 14.0), 1400.0, "#6f88b8", size=6.0).rotation_euler = (V((12, 20, -14)).to_track_quat("-Z", "Y").to_euler())
    kit.light("step fill", "POINT", (-8.0, -4.6, 1.6), 70.0, "#ffb878", size=0.3)
    kit.light("door spill", "POINT", (X0 + 0.5, -2.85, 1.7), 40.0, "#ffbf80", size=0.2)
    kit.light("day sun", "SUN", (-8, -6, 12), 3.2, "#fff0d6", rot=(math.radians(52), 0, math.radians(-62)))
    # the pine man's lights: a key from below and the side, a cool rim from behind. Front lights are dead.
    kit.light("unp key", "SPOT", (0, 0, 0), 240.0, "#ffa060", spot=34, blend=0.6, size=0.1)
    kit.light("unp rim", "SPOT", (0, 0, 0), 150.0, "#7ea0e0", spot=50, blend=0.5, size=0.2)
    kit.light("shot fill", "POINT", (0, 0, -30), 110.0, "#ffd7a8", size=0.3)


RP_ = 3.7


def build(kit, story, tl):
    global RE_
    g = story["geom"]
    RE_, ths = g["RE"], g["TH"]
    wd = workdir(tl)
    ctx = {"kit": kit, "story": story, "wd": wd, "TH": ths, "fade": {}, "site_lights": {}}
    clear_lens(kit)
    M = materials(kit, wd)
    _site_materials(kit, M)
    ctx["M"] = M
    build_room(kit, ctx, M)
    build_dais(kit, ctx, M)
    ctx["easels"], ctx["emat"] = [], {}
    for i, th in enumerate(ths, 1):
        e, mat = build_easel(kit, ctx, M, i, th, wd)
        ctx["easels"].append(e)
        ctx["emat"][i] = mat
    ctx["images"] = {}

    def load(path):
        im = bpy.data.images.load(str(path))
        im.colorspace_settings.name = "sRGB"
        return im

    pics = {"half": panel_half(), "cross": panel_cross(), "theo0": panel_theo(0), "theo1": panel_theo(1), "bench": panel_bench(),
            "bus": panel_bus(), "town1": town_image(1), "town2": town_image(2), "town3": town_image(3), "town4": town_image(4),
            "town5": town_image(5), "blank": pine_tex(480, 600, 9)}
    for name, im in pics.items():
        path = wd / f"panel-{name}.png"
        im.save(path)
        ctx["images"][name] = load(path)
    ctx["pine_faces"] = {}
    for st in range(3):
        path = wd / f"pine-theo-{st}.png"
        pine_face_image("theo", st).save(path)
        ctx["pine_faces"][("theo", st)] = load(path)
    default = {1: "town1", 2: "town2", 3: "town3", 4: "town4", 5: "town5", 6: "town2", 7: "half", 8: "blank"}
    for i, nm in default.items():
        set_img(ctx["emat"][i], ctx["images"][nm])
    build_stool(kit, ctx, M)
    build_hall(kit, ctx, M, wd)
    build_bus(kit, ctx, M)
    build_cafe(kit, ctx, M, wd)
    build_bakery(kit, ctx, M)
    build_bed(kit, ctx, M, wd)
    ctx["props"] = build_props(kit, ctx, M)
    build_lights(kit, ctx)
    build_meter(kit, ctx)
    ctx["lightsites"] = {}
    for site, names in ctx["site_lights"].items():
        for nm in names:
            ctx["lightsites"].setdefault(nm, set()).add(site)
    ctx["stool_done"] = False
    return ctx


# ------------------------------------------------------------------------------------------ animation
def _show(objs, on):
    for o in objs:
        o.hide_render = not on
        for c_ in o.children_recursive:
            c_.hide_render = not on


def dip_gain(tl, t):
    g = 1.0
    for c in _cues(tl, "dip"):
        a = c["t"]
        down, up, depth = c["down"], c["up"], c["depth"]
        hold = c["hold"]
        if "hold_to" in c:
            hold = max(0.0, _ref_time(tl, c["hold_to"]) - a - down)
        if t < a or t > a + down + hold + up:
            continue
        if t < a + down:
            p = _ss((t - a) / down)
        elif t < a + down + hold:
            p = 1.0
        else:
            p = 1.0 - _ss((t - a - down - hold) / up)
        g = min(g, 1.0 - depth * p)
    return g


def _ref_time(tl, ref):
    return tl["lines"][ref]["onset"]


# the light of each moment: exposure, sky colour, sky strength
STATES = {
    "warm": (0.55, "#cfe3f5", 1.0),       # the life room, a bright afternoon
    "dusk": (0.25, "#4b5f8c", 1.0),       # the car park, and the room as the lamps ramp down
    "cold": (0.15, "#7f93b3", 1.0),       # the life room, colder, the last shots
    "day": (0.2, "#a9d2f4", 1.1),         # the arts centre steps
    "bus": (0.1, "#a9d2f4", 1.1),
    "cafe": (0.3, "#a9d2f4", 1.0),
    "bake": (0.3, "#a9d2f4", 1.0),
    "bed": (-0.1, "#cfe0f2", 1.0),
    "hall": (0.45, "#a9d2f4", 1.0),
    "hallnight": (0.6, "#0c1018", 1.0),
    "halleve": (0.5, "#1a1d2a", 1.0),
}
SITES = ("bus", "cafe", "bake", "bed", "hall", "hallnight", "halleve")


def _seat_people(tl, t, kit):
    for who, keys in tl["acting"].items():
        root = bpy.data.objects.get(who)
        if root is None or root.hide_render:
            continue
        if _ac._switch(keys, "sit", t, False):
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (-math.pi / 2, 0, 0)
        bx, by, deg = _ac._held(keys, "bendto", t, [0.0, 0.0, 0.0])
        tor = bpy.data.objects.get(f"{who}.torso")
        if tor is not None and (deg or any("bendto" in k for k in keys)):
            yaw = root.rotation_euler.z
            wx, wy = bx - root.location.x, by - root.location.y
            n = math.hypot(wx, wy) or 1.0
            wx, wy = wx / n, wy / n
            lx = wx * math.cos(yaw) + wy * math.sin(yaw)
            ly = -wx * math.sin(yaw) + wy * math.cos(yaw)
            a = math.radians(deg)
            tor.rotation_euler = (-a * ly, a * lx, 0)


def animate(kit, story, tl, t, ctx):
    M = ctx["M"]
    over = {}
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next(s for s in story["shots"] if s["id"] == shot["id"])
    if not ctx.get("beard") and "ade.headg" in bpy.data.objects:
        R = faces.HEAD_R
        kit.box("ade.beard", (0.98, 0.34, 0.6), (0, -R + 0.1, -0.33), kit.plastic("#8d8d8a", 0.9, "beard"), bpy.data.objects["ade.headg"], bevel=0.14)
        ctx["beard"] = True
    if "patch" not in ctx and "me.headg" in bpy.data.objects:
        build_patches(kit, ctx, story)
    ts = _last(_cues(tl, "time"), t)
    state = ts["set"] if ts else "warm"
    ev, sky, sk_s = STATES.get(state, STATES["warm"])
    world = bpy.data.worlds[0].node_tree.nodes["Background"]
    world.inputs["Color"].default_value = kit.col(sky)
    world.inputs["Strength"].default_value = sk_s
    bpy.context.scene.view_settings.exposure = ev + float(spec.get("ev", 0.0))
    # the faded one (Theo): the pine look, from his acting keys
    active = None
    for who in story["geom"]["faders"]:
        root = bpy.data.objects.get(who)
        if root is None:
            continue
        fb, fh = fade_update(ctx, tl, t, who)
        if not root.hide_render and fh > 0.3 and (active is None or fh > active[1]):
            active = (who, fh)
    in_room = state not in SITES and state != "out"
    dip = dip_gain(tl, t)
    for name in kit.LIGHTS:
        g = 1.0
        if name.startswith(("lamp ", "room fill", "foot")):
            g = dip if in_room else 0.0
            if state == "warm":
                g *= {"lamp ": 0.9, "room fill": 1.6, "foot": 1.2}[next(k for k in ("lamp ", "room fill", "foot") if name.startswith(k))]
            if state == "cold":
                g *= 0.8
        if name in ("unp key", "unp rim"):
            g = 0.0
            if active is not None:
                g = min(1.0, active[1] * 1.2) * dip
                if name == "unp key" and spec.get("unp_gain") is not None:
                    g *= float(spec["unp_gain"])
        if name in ctx["lightsites"]:
            g = 1.0 if state in ctx["lightsites"][name] else 0.0
            if name == "hall lamp b" and state == "halleve":
                g = 0.5
        if name == "shot fill":
            fl = spec.get("fill")
            if fl:
                kit.LIGHTS[name]["obj"].location = tuple(fl)
            g = 1.0 if fl else 0.0
        if name == "north rim":
            g = 0.5 if state == "warm" else (1.0 if in_room else 0.0)
            if state == "cold":
                g = 1.2
        if name == "day sun":
            g = 1.0 if state == "day" else 0.0
        if name in ("post light", "ext wash", "step fill", "door spill"):
            g = {"dusk": 1.0, "day": 0.0}.get(state, 0.6 if state in ("warm", "cold") else 0.0)
            if state == "dusk" and name == "ext wash":
                g = 0.8
        over[name] = g
    if active is not None:
        who = active[0]
        root = bpy.data.objects[who]
        yaw = root.rotation_euler.z
        rot = mathutils.Matrix.Rotation(yaw, 3, "Z")
        for nm, off, aim_off in (("unp key", V((0.45, -0.75, 0.15)), V((0.0, 0.0, 1.4))), ("unp rim", V((-0.5, 1.1, 2.3)), V((0.0, -0.1, 1.5)))):
            ob = kit.LIGHTS[nm]["obj"]
            base = V((root.location.x, root.location.y, root.location.z))
            ob.location = base + rot @ off
            ob.rotation_euler = ((base + V((0, 0, aim_off.z)) + rot @ V((aim_off.x, aim_off.y, 0))) - ob.location).to_track_quat("-Z", "Y").to_euler()
    for e in ctx["easels"]:
        _show([e], True)
    for i in spec.get("hide_easels", []):
        _show([ctx["easels"][i - 1]], False)
    for who in spec.get("hide_cast", []):
        r = bpy.data.objects.get(who)
        if r is not None:
            r.hide_render = True
            for c_ in r.children_recursive:
                c_.hide_render = True
    ov = bool(spec.get("noceil"))
    ctx["easels"][7].rotation_euler = (0, 0, 0.0 if spec.get("turn8") else math.radians(ctx["TH"][7] + 90))
    ctx["easels"][6].rotation_euler = (0, 0, math.radians(ctx["TH"][6] + 90))
    for ch in ctx["easels"][6].children:
        if ch.name.startswith("easel back leg"):     # swung away with the turn: it would pass through Petra
            ch.hide_render = bool(spec.get("turn7"))
    if spec.get("turn7"):    # Petra swings her panel round to face the camera (S35)
        u = min(1.0, max(0.0, ((t - shot["start"]) / max(1e-6, shot["end"] - shot["start"]) - 0.1) / 0.6))
        u = u * u * (3 - 2 * u)
        a0, a1 = ctx["TH"][6] + 90, spec["turn7"]
        ctx["easels"][6].rotation_euler = (0, 0, math.radians(a0 + (a1 - a0) * u))
    ctx["ceiling"].hide_render = ov
    ctx["roof"].hide_render = ov
    ctx["tally"].hide_render = not spec.get("tally")
    for k, cu in enumerate(ctx["cushions"]):
        cu.hide_render = k != 0
    ctx["stool"].hide_render = True
    _seat_people(tl, t, kit)
    for c_ in _cues(tl, "easel"):
        if c_["t"] <= t:
            set_img(ctx["emat"][c_["i"]], ctx["images"][c_["img"]])
    # the hall
    hs = (_last(_cues(tl, "hall"), t) or {}).get("state", "on")
    pr = {}
    for c_ in _cues(tl, "prop"):
        if c_["t"] <= t:
            pr[c_["which"]] = c_["on"]
    for k, objs in ctx["props"].items():
        for o in objs:
            o.hide_render = not pr.get(k)
            for ch in o.children_recursive:
                ch.hide_render = not pr.get(k)
    ctx["hall"]["plates"][2].hide_render = not pr.get("plate3")
    ctx["hall"]["salt"].hide_render = False
    # the canvas carried under my arm, and the brush tip on easel 8's canvas
    if pr.get("canvas_carry") and "me.arm1" in bpy.data.objects:
        o = ctx["props"]["canvas_carry"][0]
        o.location = bpy.data.objects["me.arm1"].matrix_world @ V((0.0, -0.3, -0.55))
        o.rotation_euler = (0, 0, 0)
    if pr.get("tipbrush"):
        th8 = math.radians(ctx["TH"][7])
        n = V((math.cos(th8), math.sin(th8), 0))
        tg = V((-n.y, n.x, 0))
        base = V((RE_ * math.cos(th8), RE_ * math.sin(th8), 1.2)) + n * 0.06 - tg * 0.12
        h, bs, pd = ctx["props"]["tipbrush"]
        yaw8 = math.radians(ctx["TH"][7] + 90)
        for o, dist in ((bs, 0.0), (h, 0.17)):
            o.location = base + n * (dist * 0.7) + V((0, 0, dist * 0.5)) + tg * (dist * 0.3)
            o.rotation_euler = (0.5, 0, yaw8 + 0.2)
        pd.location = base - n * 0.04
    # colour fills: the bench, the cake, my ear, Theo's nose
    for nm in ("bench", "cake", "ear", "nose"):
        if nm in ctx["ramps"]:
            v = _ramp_value(tl, nm, t, 0.0)
            if nm == "cake":
                v = 160.7 + v * 0.8          # the front runs across the cake (x metres)
            ctx["ramps"][nm].outputs[0].default_value = v
    ev_ = _ramp_value(tl, "ear", t, 0.0)
    for o in ctx.get("patch", {}).get("ear", []):
        o.hide_render = ev_ >= 0.999 or spec.get("noear", False)
    nv = _ramp_value(tl, "nose", t, 0.0)
    th_root = bpy.data.objects.get("theo")
    th_hidden = th_root is None or th_root.hide_render
    pine_face = False
    if "theo" in story["geom"]["faders"]:
        pine_face = _ac._held(tl["acting"].get("theo", []), "fade_h", t, 0.0) > 0.4
    for o in ctx.get("patch", {}).get("nose", []):
        o.hide_render = th_hidden or pine_face
    if len(ctx.get("patch", {}).get("nose", [])) == 2:
        ctx["patch"]["nose"][0].hide_render = ctx["patch"]["nose"][0].hide_render or nv >= 0.999
        ctx["patch"]["nose"][1].hide_render = th_hidden or pine_face or nv < 0.5
    if "noseink" in ctx["ramps"]:
        ctx["ramps"]["noseink"].outputs[0].default_value = nv
    update_meter(kit, ctx, tl, t, spec, shot)
    return over
