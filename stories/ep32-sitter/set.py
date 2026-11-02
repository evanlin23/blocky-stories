"""ep32 "sitter": the set (the faded-wood town: a sunny bus stop, a cafe, a bakery, my flat, a community arts centre life room on
a rainy Wednesday, Mum's bare hall, a car park, and the reveal pair).

Everything is built once in build() from kit's parts; animate() only moves and switches what the story's cues and acting say.
The cast (rig.py) is posed by bl_story from the story's acting. Nothing here carries text: no signs, no lettering.

Places (metres, floor z = 0, the car park at z = -0.45): the life room is centred on the dais at the origin
(x -5.6 .. 5.6, y -5.2 .. 5.0, ceiling 3.2). Easel i stands at angle TH[i] on a curve of radius RE with its canvas
facing out, its painter behind it at RP. Mum's hall is at x = 40 (a corridor along y, the west wall x = 39 holds the
frames), my flat at x = -40, the bus stop at x = 80, the cafe at x = 120, the bakery at x = 160, the reveal pair at x = 200.

Acting keys read here (acting.py ignores them): "sit": true seats a character (legs flat) on whatever is under them;
"fade" / "fade_h": how far the body / the face has faded to raw pine (0..1); "stage": which pencil face a faded head wears;
"bendto": [x, y, deg] leans the torso from the waist toward x, y.
Cues read here (all optional):
- time: {"set": night | cold | warm | end | bus | cafe | bake | flat | pair} the light of the moment (and which little set's lights are on)
- dip: {"down", "hold", "up", "depth", "hold_to"} the room's lamps ramp to (1 - depth), hold, ramp back (never dark)
- stool: {"on", "pos", "yaw"} the paint-spattered spare stool; canvas: {"stage"} my canvas; easel: {"i", "img"}
- hall: {"state": now | hung}; prop: {"which", "on"}
Shot flags: tally (the nine strokes on the dais edge), turn8, noceil, hide_easels, hide_cast, fill, ev.
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
HX, KX = 40.0, -40.0
GRAPHITE = (44, 42, 42)

BUS_, CAF_, BAK_, FLAT_, FLAT_EASEL_, PAIR_ = (80.0, 0.2), (120.0, 1.5), (160.9, -0.15), (-40.0, 0.0), (-40.25, 0.7), (200.0, 0.0)



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


def _plaid(d, box, base, line, gap=14):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=base)
    for x in range(x0, x1, gap):
        d.line([(x, y0), (x, y1)], fill=line, width=3)
    for y in range(y0, y1, gap):
        d.line([(x0, y), (x1, y)], fill=line, width=3)


def portrait_of_mum(finished, w=480, h=600):
    """Mum in oils: the silver bob, round tortoiseshell glasses, the teal check cardigan over cream. At home (finished=False)
    her face is only the guide lines I always stop on; finished, it is painted."""
    ox, oy, W, H = FACE_BOX
    cx, cy, rx, ry = HEAD_OVAL
    im = Image.new("RGB", (w, h), (214, 190, 150))
    d = ImageDraw.Draw(im)
    for y in range(h):
        k = y / h
        d.line([(0, y), (w, y)], fill=(int(214 - 24 * k), int(190 - 26 * k), int(150 - 24 * k)))
    _plaid(d, (50, 470, 430, 640), (47, 127, 130), (36, 100, 104))
    d.polygon([(190, 470), (290, 470), (240, 540)], fill=(240, 232, 214))                    # cream top
    d.rectangle([205, 430, 275, 480], fill=(232, 196, 160))                                  # neck
    d.ellipse([cx - rx - 22, cy - ry - 18, cx + rx + 22, cy + ry - 40], fill=(196, 200, 206))  # silver bob behind
    d.rectangle([cx - rx - 22, cy - 40, cx - rx + 26, cy + 120], fill=(196, 200, 206))
    d.rectangle([cx + rx - 26, cy - 40, cx + rx + 22, cy + 120], fill=(196, 200, 206))
    face = (232, 196, 160) if finished else (240, 233, 216)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=face)
    d.pieslice([cx - rx - 8, cy - ry - 10, cx + rx + 8, cy + 20], 180, 360, fill=(196, 200, 206))   # fringe
    if finished:
        brown_eyes(d, ox, oy, W, H, 1.0)
        for s_, ex in ((-1, 0.13), (1, 0.87)):
            for k in (-1, 0, 1):
                pencil(d, [(ox + ex * W, oy + (0.42 + k * 0.012) * H), (ox + (ex + s_ * 0.085) * W, oy + (0.42 + k * 0.05) * H)], 3, (120, 88, 70))
        for cxx in (0.29, 0.71):
            d.arc([ox + cxx * W - 40, oy + 0.42 * H - 70, ox + cxx * W + 40, oy + 0.42 * H - 28], 200, 340, fill=(120, 120, 124), width=5)
        pencil(d, [(ox + 0.5 * W, oy + 0.5 * H), (ox + 0.46 * W, oy + 0.6 * H), (ox + 0.52 * W, oy + 0.62 * H)], 3, (200, 150, 124))
        d.arc([ox + 0.3 * W, oy + 0.7 * H, ox + 0.7 * W, oy + 0.86 * H], 15, 165, fill=(168, 80, 80), width=7)   # about to say it
    else:
        portrait_lines(d, ox, oy, W, H, 2, 7)
    for cxx in (0.29, 0.71):                                                                 # round tortoiseshell glasses
        x, y = ox + cxx * W, oy + 0.42 * H
        d.ellipse([x - 55, y - 55, x + 55, y + 55], outline=(112, 76, 44), width=9)
    d.line([(ox + 0.29 * W + 55, oy + 0.42 * H - 8), (ox + 0.71 * W - 55, oy + 0.42 * H - 8)], fill=(112, 76, 44), width=8)
    return im


def canvas_image(stage):
    W, H = 480, 600
    if stage >= 5:
        return portrait_of_mum(True)
    im = paper(W, H, seed=3)
    d = ImageDraw.Draw(im)
    cx, cy, rx, ry = HEAD_OVAL
    oval(d, cx, cy, rx, ry, 4, col=(150, 150, 150))
    ox, oy, fw, fh = FACE_BOX
    portrait_lines(d, ox, oy, fw, fh, min(stage, 2), 7)
    if stage == 4:                       # the kind brown eyes go in over the guide ovals
        brown_eyes(d, ox, oy, fw, fh, 1.0)
    return im


def ade_image(w=480, h=600):
    """Mr Dobbs being painted: brown flat cap, grey beard, olive tweed."""
    im = Image.new("RGB", (w, h), (206, 192, 164))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([60, 460, 420, 640], radius=50, fill=(120, 128, 60))
    d.rectangle([205, 410, 275, 470], fill=(217, 166, 126))
    d.ellipse([120, 120, 360, 450], fill=(217, 166, 126))
    d.pieslice([108, 40, 372, 300], 180, 360, fill=(107, 74, 46))
    d.rectangle([108, 150, 372, 190], fill=(107, 74, 46))
    d.chord([116, 300, 364, 520], 0, 180, fill=(140, 140, 138))                               # grey beard
    for cxx in (200, 280):
        d.ellipse([cxx - 18, 230, cxx + 18, 262], fill=(246, 240, 228))
        d.ellipse([cxx - 10, 234, cxx + 10, 258], fill=(60, 44, 34))
    d.line([(238, 280), (232, 322), (246, 324)], fill=(190, 140, 112), width=4)
    return im


def fruit_image(style, seed=0):
    W, H = 400, 500
    pencil_only = style == "pencil"
    im = paper(W, H, base=(240, 233, 216) if pencil_only else (206, 190, 160), seed=seed)
    d = ImageDraw.Draw(im)
    rnd = random.Random(seed + 5)
    bowl = [(70, 330), (330, 330), (300, 420), (100, 420)]
    if pencil_only:
        pencil(d, [(60, 330), (340, 330)], 5)
        pencil(d, [(60, 330), (95, 425), (305, 425), (340, 330)], 5)
        oval(d, 200, 330, 140, 16, 5)
        for cx, cy, r in ((150, 292, 34), (225, 300, 30), (275, 288, 24)):
            oval(d, cx, cy, r, r, 4)
        pencil(d, [(110, 300), (125, 270), (140, 300)], 4)
        return im
    tint = [(0, 0, 0), (12, 8, -10), (-10, 6, 14), (8, -6, 4)][seed % 4]
    c = lambda r, g, b: (max(0, min(255, r + tint[0])), max(0, min(255, g + tint[1])), max(0, min(255, b + tint[2])))
    d.rectangle([0, 360, W, H], fill=c(120, 84, 54))
    d.polygon(bowl, fill=c(150, 96, 60))
    d.ellipse([60, 316, 340, 348], fill=c(176, 118, 76))
    if style == "pear":
        d.ellipse([140, 200, 260, 330], fill=(150, 176, 70))
        d.ellipse([165, 130, 235, 230], fill=(158, 184, 76))
        d.line([(200, 135), (206, 108)], fill=(90, 62, 36), width=7)
        d.ellipse([172, 150, 190, 172], fill=(200, 216, 130))
        return im
    d.ellipse([105, 262, 185, 336], fill=c(226, 134, 34))                                 # orange
    d.ellipse([200, 236, 276, 330], fill=c(170, 190, 78))                                 # pear
    d.ellipse([225, 200, 258, 250], fill=c(176, 196, 84))
    for cx in (140, 175):
        d.ellipse([cx - 22, 244, cx + 22, 286], fill=c(98, 52, 98))                       # plums
    for k in range(9):
        d.ellipse([270 + rnd.randint(-8, 18) + (k % 3) * 14, 264 + (k // 3) * 16, 292 + (k % 3) * 14, 286 + (k // 3) * 16],
                  fill=c(120, 64, 110))                                                   # grapes
    return im


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


def pine_face_image(kind, stage):
    """A faded head's texture: raw pine with graphite guide lines, wrapped round the head (faces.py's layout).
    kind "mum": the lines end in little corner lines (plant 1) and at stage 3 the brown eyes are in. kind "plain": the
    cross and ovals only (the montage faces). kind "plain2": the same, a touch smaller (the sting sitter)."""
    W, H = faces.TEX_W, faces.TEX_H
    rnd = random.Random(11)
    im = Image.new("RGB", (W, H), (217, 186, 140))
    d = ImageDraw.Draw(im)
    for _ in range(260):          # grain, long and vertical
        x = rnd.randrange(W)
        y0 = rnd.randrange(H)
        dk = rnd.randint(8, 24)
        d.line([(x, y0), (x + rnd.randint(-6, 6), min(H, y0 + rnd.randint(80, 400)))], fill=(217 - dk, 186 - dk, 140 - dk), width=rnd.choice((1, 2, 3)))
    im = im.filter(ImageFilter.GaussianBlur(0.8))
    d = ImageDraw.Draw(im)
    s = faces.FX1 - faces.FX0
    fw = 1.048 * s * (0.9 if kind == "plain2" else 1.0)
    fh = (faces.FY1 - faces.FY0) * 0.96
    ox, oy = W / 2 - fw / 2, faces.FY0 + (faces.FY1 - faces.FY0) * 0.02
    portrait_lines(d, ox, oy, fw, fh, min(stage, 2), 22, pale=(247, 240, 224), corners=(kind == "mum"))
    if stage >= 3 and kind == "mum":
        brown_eyes(d, ox, oy, fw, fh, 0.62)
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


def rain_image():
    """The north window: dark blue night with streaks of rain running down it."""
    W, H = 512, 1024
    rnd = random.Random(4)
    im = Image.new("RGB", (W, H), (22, 34, 58))
    d = ImageDraw.Draw(im)
    for _ in range(170):
        x, y = rnd.randrange(W), rnd.randrange(H)
        ln = rnd.randint(60, 340)
        v = rnd.randint(14, 44)
        d.line([(x, y), (x + rnd.randint(-5, 5), y + ln)], fill=(22 + v, 34 + v, 58 + v + 10), width=rnd.choice((2, 3, 4)))
    for _ in range(120):
        x, y = rnd.randrange(W), rnd.randrange(H)
        d.ellipse([x - 4, y - 4, x + 4, y + 7], fill=(80, 100, 140))
    return im.filter(ImageFilter.GaussianBlur(1.2))



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
    ctx["pane_mat"] = img_mat(kit, "rain", rain_image(), ctx["wd"], rough=0.3, emit=0.55)
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
    # the fruit table by the door
    kit.box("fruit table", (0.9, 1.3, 0.05), (X0 + 0.55, -1.6, 0.78), M["table"], bevel=0.01)
    for sx in (-0.4, 0.4):
        for sy in (-0.55, 0.55):
            kit.box("fruit table leg", (0.05, 0.05, 0.78), (X0 + 0.55 + sx, -1.6 + sy, 0.39), M["table"])
    bx, by, bz = X0 + 0.55, -1.6, 0.805
    kit.cyl("fruit bowl", 0.2, 0.1, (bx, by, bz + 0.05), M["bowl"], r2=0.14)
    for (dx, dy, r, k) in ((-0.05, -0.05, 0.065, "orange"), (0.07, 0.04, 0.055, "pearf"), (-0.08, 0.07, 0.04, "plum"),
                            (0.03, -0.09, 0.04, "plum")):
        kit.sphere("fruit", r, (bx + dx, by + dy, bz + 0.16), M[k])
    for k in range(7):
        kit.sphere("grape", 0.022, (bx + 0.03 + 0.03 * (k % 3), by - 0.02 + 0.025 * (k // 3), bz + 0.2 + 0.01 * (k % 2)), M["grape"])



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
    mat = img_mat(kit, f"canvas {i}", fruit_image("oil", i), wd, rough=0.88)
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
    if top is not None and hg is not None:           # seat the frames round the eyes (full rings, not one bar above them)
        R_ = faces.HEAD_R
        for sx in (-1, 1):
            bpy.data.objects[f"{who}.glf{sx}"].location.z = 0.13
            for nm, size, loc in ((f"glb{sx}", (0.46, 0.04, 0.05), (sx * 0.24, -R_ - 0.05, -0.13)),
                                  (f"gls{sx}a", (0.05, 0.04, 0.26), (sx * 0.24 - 0.21, -R_ - 0.05, 0.0)),
                                  (f"gls{sx}b", (0.05, 0.04, 0.26), (sx * 0.24 + 0.21, -R_ - 0.05, 0.0))):
                ctx["kit"].box(f"{who}.gl{nm}", size, loc, top.material_slots[0].material if top.material_slots else None, hg)
        bpy.data.objects[f"{who}.glb"].location.z = 0.0
    done = {}
    for ob in [root] + list(root.children_recursive):
        if ob.type != "MESH":
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
                    val = m.node_tree.nodes.new("ShaderNodeValue")
                    _lay_over(m, br, val.outputs[0])
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
    for v in F["body"]:
        v.outputs[0].default_value = float(fb)
    for e in F["edge"]:
        e.outputs[0].default_value = 0.33 + 0.37 * float(fh)
    for k in F["kh"]:
        k.outputs[0].default_value = min(1.0, max(0.0, float(fh) * 4.0))
    kind = ctx["story"]["geom"]["faders"][who]
    st = int(_ac._switch(keys, "stage", t, 0))
    for tex in F["tex"]:
        tex.image = ctx["pine_faces"][(kind, min(st, 3 if kind == "mum" else 2))]
    for g in F["glasses"]:
        g.hide_render = g.hide_render or fh > 0.55
    return fb, fh



# ------------------------------------------------------------------------------------------ hall and kitchen


def build_hall(kit, ctx, M, wd):
    # a corridor along y: x 39 .. 41.2, y -1.5 .. 3.5, high 2.6
    ctx["hall"] = {}
    kit.box("hall floor", (2.2, 5.0, 0.1), (HX + 0.1, 1.0, -0.05), M["floor2"])
    kit.box("hall ceil", (2.2, 5.0, 0.1), (HX + 0.1, 1.0, 2.65), M["ceilmat"])
    kit.box("hall w", (0.1, 5.0, 2.6), (HX - 1.05, 1.0, 1.3), M["hallwall"])
    kit.box("hall e", (0.1, 5.0, 2.6), (HX + 1.25, 1.0, 1.3), M["hallwall"])
    kit.box("hall n", (2.2, 0.1, 2.6), (HX + 0.1, 3.55, 1.3), M["hallwall"])
    # the door end, y = -1.5, with a pane of morning sun
    kit.box("hall s a", (0.55, 0.1, 2.6), (HX - 0.77, -1.55, 1.3), M["hallwall"])
    kit.box("hall s b", (0.55, 0.1, 2.6), (HX + 0.97, -1.55, 1.3), M["hallwall"])
    kit.box("hall s c", (0.9, 0.1, 0.5), (HX + 0.1, -1.55, 2.35), M["hallwall"])
    kit.box("hall door", (0.9, 0.06, 2.0), (HX + 0.1, -1.56, 1.0), M["glass_door"])
    # the frames (then), the pale squares (now), the hooks (always)
    rnd = random.Random(21)
    slots = []
    for col, y in enumerate((-0.55, 0.0, 0.55, 1.1, 1.65, 2.2, 2.75)):
        for row, z in enumerate((0.95, 1.45, 1.95)):
            if (col + row) % 3 == 2 and col not in (3,):
                continue
            slots.append((y + rnd.uniform(-0.04, 0.04), z + rnd.uniform(-0.03, 0.03), 0.34 + 0.06 * rnd.random(), 0.42))
    slots = slots[:14]
    frames, squares = [], []
    for k, (y, z, w, h) in enumerate(slots):
        f = kit.empty("hall frame", (HX - 0.995, y, z))
        kit.box("frame", (0.04, w + 0.05, h + 0.05), (0, 0, 0), M["frame"], f)
        pm = img_mat(kit, f"art{k}", art_image(k), wd, rough=0.7)
        pl = uvplane(kit, "art", (w, h), (0.0215, 0, 0), None, f, (math.pi / 2, 0, math.pi / 2))
        pl.data.materials.append(pm)
        frames.append(f)
        sq = kit.box("pale square", (0.005, w + 0.06, h + 0.06), (HX - 0.998, y, z), M["square"])
        squares.append(sq)
        hook = kit.box("hook", (0.03, 0.02, 0.02), (HX - 0.985, y, z + h / 2 - 0.03), M["dark"])
    ctx["hall"].update(frames=frames, squares=squares)
    # the portrait for the last shots, one of the hooks
    pf = kit.empty("hall portrait", (HX - 0.97, 1.2, 1.55))
    kit.box("portrait frame", (0.04, 0.66, 0.81), (0, 0, 0), M["frame"], pf)
    pm = img_mat(kit, "portrait", portrait_of_mum(True), wd, rough=0.7)
    pl = uvplane(kit, "portrait face", (0.6, 0.75), (0.0215, 0, 0), None, pf, (math.pi / 2, 0, math.pi / 2))
    pl.data.materials.append(pm)
    ctx["hall"]["portrait"] = pf
    # the table and the jar of brushes below it; the drawer at the north end
    kit.box("hall table", (0.4, 0.9, 0.04), (HX - 0.75, 1.2, 0.8), M["table"])
    for sx in (-0.15, 0.15):
        for sy in (-0.4, 0.4):
            kit.box("table leg", (0.04, 0.04, 0.8), (HX - 0.75 + sx, 1.2 + sy, 0.4), M["table"])
    jar = kit.cyl("jar", 0.05, 0.14, (HX - 0.8, 1.25, 0.89), M["jar"])
    for k in range(5):
        kit.box("brush", (0.012, 0.012, 0.18), (HX - 0.8 + 0.02 * (k - 2), 1.25 + 0.01 * (k % 2), 1.0), M["brush"], rot=(0.15 * (k - 2), 0.1, 0))
    ctx["hall"]["jar"] = [o for o in bpy.data.objects if o.name.startswith(("jar", "brush"))]
    for o in ctx["hall"]["jar"]:
        o.hide_render = True
    kit.box("chest", (0.9, 0.5, 0.78), (HX + 0.2, 3.25, 0.39), M["table"], bevel=0.01)
    dr = kit.empty("drawer", (HX + 0.2, 3.0, 0.55))
    kit.box("drawer front", (0.78, 0.04, 0.2), (0, 0, 0), M["frame"], dr)
    kit.box("drawer floor", (0.74, 0.4, 0.02), (0, 0.2, -0.09), M["frame"], dr)
    kit.box("drawer side", (0.02, 0.4, 0.16), (-0.36, 0.2, 0), M["frame"], dr)
    kit.box("drawer side", (0.02, 0.4, 0.16), (0.36, 0.2, 0), M["frame"], dr)
    kit.cyl("jar lying", 0.05, 0.16, (-0.1, 0.1, -0.03), M["jar"], dr, rot=(0, math.pi / 2, 0.3))
    for k in range(5):
        kit.box("brush", (0.012, 0.012, 0.22), (0.1, 0.07 + 0.03 * (k - 2), -0.07), M["brush"], dr, rot=(0, math.pi / 2, 0.3 + 0.05 * k))
    ctx["hall"]["drawer"] = dr
    kit.light("hall sun", "AREA", (HX + 0.1, -1.3, 1.3), 14.0, "#ffe3b0", size=1.0).rotation_euler = (math.radians(-90), 0, 0)
    kit.light("shot fill", "POINT", (0, 0, -30), 110.0, "#ffd7a8", size=0.3)
    kit.light("drawer lamp", "POINT", (HX + 0.4, 2.2, 1.3), 20.0, "#fff0d8", size=0.2)
    kit.light("hall fill", "AREA", (HX + 0.1, 1.0, 1.9), 34.0, "#fff2dc", size=2.0).rotation_euler = (math.pi, 0, 0)


# ------------------------------------------------------------------------------------------ the little daylight sets


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
    M["slate"] = kit.plastic("#2c2f37", 0.9, "slate wall")


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


def build_bus(kit, ctx, M):
    X, Y = BUS_[0], BUS_[1]
    kit.box("bus pavement", (22, 4.2, 0.2), (X, 1.0, -0.1), M["pave"])
    kit.box("bus road", (22, 7.0, 0.2), (X, -4.6, -0.22), M["road"])
    # the buildings behind the shelter, flat-faced and plain: no signs, no lettering
    facades = [(X - 7.4, "cream"), (X - 4.2, "terra"), (X - 1.0, "sage"), (X + 2.2, "mustard"), (X + 5.4, "sky"), (X + 8.6, "cream")]
    for k, (fx, mk) in enumerate(facades):
        hgt = 4.6 + 0.8 * (k % 3)
        kit.box("bus facade", (3.2, 3.0, hgt), (fx, 4.7, hgt / 2), M[mk])
        for wx in (-0.8, 0.8):
            for wz in (1.9, 3.5):
                kit.box("bus window", (0.8, 0.04, 1.0), (fx + wx, 3.17, wz), M["pane"])
        kit.box("bus door", (0.9, 0.05, 2.0), (fx, 3.17, 1.0), M["door"])
    # the shelter
    kit.box("bus roof", (3.8, 1.8, 0.1), (X, 1.25, 2.5), M["metal"])
    for sx in (-1.8, 1.8):
        for sy in (0.45, 2.05):
            kit.box("bus post", (0.08, 0.08, 2.5), (X + sx, sy, 1.25), M["metal"])
    kit.box("bus back panel", (3.6, 0.05, 1.8), (X, 2.07, 1.3), M["shelter"])
    kit.box("bus bench seat", (1.8, 0.42, 0.06), (X + 0.4, 1.7, 0.5), M["easel"], bevel=0.01)
    for sx in (-0.8, 0.8):
        kit.box("bus bench leg", (0.06, 0.36, 0.5), (X + 0.4 + sx, 1.7, 0.25), M["metal"])
    # a plain stop sign: a pole and a blank disc
    kit.cyl("bus pole", 0.04, 2.6, (X + 2.9, -0.55, 1.3), M["metal"])
    kit.cyl("bus disc", 0.26, 0.04, (X + 2.9, -0.6, 2.45), M["signdisc"], rot=(math.pi / 2, 0, 0))
    kit.light("bus sun", "SUN", (X, 0, 12), 4.2, "#fff0d6", rot=(math.radians(58), 0, math.radians(-28)))
    ctx["site_lights"]["bus"] = ["bus sun"]


def build_cafe(kit, ctx, M):
    X, Y = CAF_[0], CAF_[1]
    _room(kit, M, X, 0.6, 6.0, 5.0, M["floor"], M["plaster"], front=False)
    kit.box("cafe window", (3.4, 0.04, 1.5), (X, 3.02, 1.65), M["win_day"])
    for sx in (-1.7, 0.0, 1.7):
        kit.box("cafe mullion", (0.07, 0.06, 1.5), (X + sx, 2.99, 1.65), M["white"])
    kit.box("cafe sill", (3.6, 0.2, 0.05), (X, 3.0, 0.88), M["white"])
    # the table for two: a cloth to the knees, so the sitters' legs are under it
    kit.box("cafe cloth", (0.72, 0.84, 0.44), (X, Y, 0.65), M["cloth"], bevel=0.01)
    kit.box("cafe table top", (0.74, 0.9, 0.04), (X, Y, 0.88), M["cloth"], bevel=0.01)
    for sx in (-0.18, 0.18):
        kit.cyl("cafe plate", 0.11, 0.02, (X + sx, Y - 0.05, 0.91), M["plate"])
        kit.box("cafe toast", (0.1, 0.1, 0.025), (X + sx, Y - 0.05, 0.935), M["toast"], rot=(0, 0, 0.3 * sx))
        kit.cyl("cafe mug", 0.04, 0.09, (X + sx * 1.1, Y + 0.28, 0.955), M["mug"])
    for sx, sgn in ((-0.55, 1), (0.55, -1)):
        kit.box("cafe seat", (0.46, 0.46, 0.05), (X + sx, Y, 0.425), M["chair"], bevel=0.01)
        kit.box("cafe chair back", (0.05, 0.46, 0.5), (X + sx - sgn * 0.26, Y, 0.72), M["chair"], bevel=0.01)
        for lx in (-0.2, 0.2):
            for ly in (-0.2, 0.2):
                kit.box("cafe chair leg", (0.04, 0.04, 0.4), (X + sx + lx, Y + ly, 0.2), M["chair"])
    kit.light("cafe key", "AREA", (X, -0.6, 2.7), 190.0, "#fff1dc", size=2.5).rotation_euler = (math.radians(20), 0, 0)
    kit.light("cafe fill", "AREA", (X, 1.2, 2.8), 120.0, "#ffe8c8", size=2.5)
    ctx["site_lights"]["cafe"] = ["cafe key", "cafe fill"]


def build_bakery(kit, ctx, M):
    X = BAK_[0] - 0.4
    _room(kit, M, X, 0.6, 6.0, 5.2, M["tile"], M["cream"], front=True)
    kit.box("bake front window", (3.2, 0.04, 1.6), (X, -1.93, 1.6), M["win_day"])
    # shelves of bread behind the counter
    rnd = random.Random(4)
    for k, z in enumerate((1.0, 1.55, 2.1)):
        kit.box("bake shelf", (4.4, 0.34, 0.05), (X, 2.8, z), M["easel"])
        for j in range(8):
            mk = "loaf" if (j + k) % 2 else "loaf2"
            if (j + k) % 3 == 0:
                kit.box("bake loaf", (0.34, 0.14, 0.12), (X - 1.9 + j * 0.54, 2.8, z + 0.085), M[mk], bevel=0.05)
            else:
                kit.sphere("bake bun", 0.1, (X - 1.9 + j * 0.54, 2.8, z + 0.13), M[mk]).scale = (1.2, 0.9, 0.8)
    # the counter and the glass case
    kit.box("bake counter", (3.4, 0.7, 1.0), (X + 0.4, 0.9, 0.5), M["counter"], bevel=0.01)
    kit.box("bake counter top", (3.6, 0.82, 0.05), (X + 0.4, 0.9, 1.025), M["counter_top"], bevel=0.01)
    kit.box("bake tray", (0.9, 0.4, 0.05), (X - 0.3, 0.9, 1.075), M["plate"])
    for j in range(5):
        kit.sphere("bake roll", 0.07, (X - 0.55 + j * 0.12, 0.9, 1.15), M["loaf"]).scale = (1.3, 0.9, 0.8)
    kit.light("bake key", "AREA", (X + 0.4, -1.1, 2.7), 210.0, "#fff1dc", size=2.5).rotation_euler = (math.radians(15), 0, 0)
    kit.light("bake back", "AREA", (X + 0.4, 2.0, 2.9), 110.0, "#ffe8c8", size=2.5)
    ctx["site_lights"]["bake"] = ["bake key", "bake back"]


def build_flat(kit, ctx, M, wd):
    X = FLAT_[0]
    _room(kit, M, X, 0.0, 3.8, 3.8, M["flatfloor"], M["flatwall"], front=False)
    kit.box("flat window", (1.5, 0.04, 1.3), (X - 0.2, 1.83, 1.6), M["win_cool"])
    for sx in (-0.95, -0.2, 0.55):
        kit.box("flat mullion", (0.05, 0.06, 1.3), (X + sx, 1.80, 1.6), M["white"])
    # my easel with Mum's portrait
    ex, ey = FLAT_EASEL_
    for sx in (-0.38, 0.38):
        kit.box("flat easel leg", (0.05, 0.05, 1.9), (ex + sx, ey, 0.95), M["easel"])
    kit.box("flat easel shelf", (0.84, 0.2, 0.04), (ex, ey - 0.08, 0.7), M["easel"])
    kit.box("flat easel back leg", (0.05, 0.05, 1.7), (ex, ey + 0.4, 0.85), M["easel"], rot=(math.radians(-13), 0, 0))
    kit.box("flat canvas frame", (0.74, 0.03, 0.92), (ex, ey - 0.05, 1.3), M["canvas_back"])
    face = uvplane(kit, "flat canvas face", (0.74, 0.92), (ex, ey - 0.0765, 1.3), None, None, (math.pi / 2, 0, 0))
    ctx["flat_mat"] = img_mat(kit, "flat canvas", portrait_of_mum(False), wd, rough=0.88)
    face.data.materials.append(ctx["flat_mat"])
    # the shelf with my phone face down
    sx_ = X + 1.7
    kit.box("flat shelf", (0.3, 1.0, 0.04), (sx_, 0.2, 1.0), M["easel"])
    kit.box("flat shelf bracket", (0.2, 0.04, 0.16), (sx_ + 0.04, -0.2, 0.9), M["dark"])
    kit.box("flat shelf bracket", (0.2, 0.04, 0.16), (sx_ + 0.04, 0.6, 0.9), M["dark"])
    kit.box("flat phone", (0.078, 0.158, 0.011), (sx_, 0.15, 1.027), M["phone_off"], bevel=0.004, rot=(0, 0, 0.1))
    kit.cyl("flat mug", 0.04, 0.09, (sx_, 0.5, 1.065), M["mug"])
    kit.light("flat sun", "AREA", (X - 0.2, 1.4, 2.6), 260.0, "#d7e8ff", size=2.0).rotation_euler = (math.radians(-80), 0, 0)
    kit.light("flat key", "AREA", (X + 0.2, -1.4, 2.5), 150.0, "#f1f2ff", size=2.0).rotation_euler = (math.radians(20), 0, 0)
    ctx["site_lights"]["flat"] = ["flat sun", "flat key"]


def build_pair(kit, ctx, M, wd):
    X = PAIR_[0]
    kit.box("pair wall", (7.0, 0.1, 4.0), (X, 1.5, 1.9), M["slate"])
    kit.box("pair floor", (7.0, 5.0, 0.1), (X, -0.8, -0.05), M["floor"])
    ctx["pair_mats"] = []
    for sx, nm, im in ((-0.58, "home", portrait_of_mum(False)), (0.58, "class", canvas_image(2))):
        x = X + sx
        for lx in (-0.5, 0.5):
            kit.box("pair easel leg", (0.05, 0.05, 2.1), (x + lx, 1.1, 1.05), M["easel"])
        kit.box("pair easel shelf", (1.1, 0.2, 0.04), (x, 1.0, 0.75), M["easel"])
        kit.box("pair frame", (1.04, 0.04, 1.3), (x, 1.0, 1.5), M["canvas_back"])
        pl = uvplane(kit, f"pair {nm}", (1.0, 1.25), (x, 0.965, 1.5), None, None, (math.pi / 2, 0, 0))
        mt = img_mat(kit, f"pair {nm}", im, wd, rough=0.88)
        pl.data.materials.append(mt)
    kit.light("pair key", "AREA", (X, -1.6, 3.3), 330.0, "#fff3e2", size=3.0).rotation_euler = (math.radians(30), 0, 0)
    ctx["site_lights"]["pair"] = ["pair key"]


# ------------------------------------------------------------------------------------------ props, lights, build


def build_props(kit, ctx, M):
    P = {}
    P["canvas_carry"] = [kit.box("carried canvas", (0.5, 0.03, 0.62), (0, 0, 0), M["canvas_back"])]
    P["coat"] = [kit.box("coat", (0.5, 0.12, 0.6), (0, 0, 0), M["coat"], bevel=0.04),
                 kit.box("coat sleeve", (0.12, 0.1, 0.5), (0.3, 0, -0.05), M["coat"], bevel=0.03, rot=(0, 0.2, 0)),
                 kit.box("coat sleeve", (0.12, 0.1, 0.5), (-0.3, 0, -0.05), M["coat"], bevel=0.03, rot=(0, -0.2, 0))]
    th7 = math.radians(ctx["TH"][6])
    p7 = (RP_ * math.cos(th7), RP_ * math.sin(th7))
    P["brushdrop"] = [kit.box("dropped brush", (0.03, 0.3, 0.03), (p7[0] + 0.05, p7[1] - 0.25, 0.012), M["brush"], rot=(0, 0, 0.6)),
                      kit.box("dropped bristles", (0.04, 0.09, 0.04), (p7[0] + 0.1, p7[1] - 0.13, 0.014), M["bristle"], rot=(0, 0, 0.6))]
    for objs in P.values():
        for o in objs:
            o.hide_render = True
    return P


def build_lights(kit, ctx):
    # the room: dim warm fill from the ceiling, floor-level work lights round the dais, a cold rim from the north window
    for k, th in enumerate(ctx["TH"]):
        x, y = 4.5 * math.cos(math.radians(th)), 4.5 * math.sin(math.radians(th))
        kit.light(f"room fill {k}", "POINT", (x, y, 2.7), 26.0, "#ffcf9a", size=0.4)
    for k, (x, y) in enumerate(((-1.4, -1.6), (1.4, -1.6), (0.0, 2.4))):
        kit.light(f"room fill c{k}", "POINT", (x, y, 2.9), 16.0, "#ffd7aa", size=0.4)
    for k, (x, y, z) in enumerate(((1.3, -1.3, 0.25), (-1.3, -1.2, 0.25))):
        kit.light(f"foot {k}", "POINT", (x, y, z), 14.0, "#ffa860", size=0.15)
    rim = kit.light("north rim", "AREA", (0.0, 4.6, 2.3), 260.0, "#6f93d8", size=2.4)
    rim.rotation_euler = (V((0, -1.5, -1.2)).to_track_quat("-Z", "Y").to_euler())
    for nm in list(kit.LIGHTS):
        if nm.startswith(("hall ", "kit ", "north rim", "drawer", "cafe ", "bake ", "flat ", "pair ")):
            kit.LIGHTS[nm]["obj"].visible_camera = False
    # outside: the lamp post, a cold wash on the building
    kit.light("post light", "POINT", (-2.6, -9.0, GROUND + 3.4), 700.0, "#ffd29a", size=0.3)
    kit.light("ext wash", "AREA", (-12.0, -20.0, 14.0), 1400.0, "#5a73a8", size=6.0).rotation_euler = (V((12, 20, -14)).to_track_quat("-Z", "Y").to_euler())
    kit.light("step fill", "POINT", (-8.0, -4.6, 1.6), 70.0, "#ffb878", size=0.3)
    kit.light("door spill", "POINT", (X0 + 0.5, -2.85, 1.7), 40.0, "#ffbf80", size=0.2)
    # the faded one's lights: a key from below and the side, a cold rim from behind. Front lights are dead.
    # They travel to whichever faded character is on screen (animate)
    kit.light("unp key", "SPOT", (0, 0, 0), 240.0, "#ffa060", spot=34, blend=0.6, size=0.1)
    kit.light("unp rim", "SPOT", (0, 0, 0), 150.0, "#7ea0e0", spot=50, blend=0.5, size=0.2)


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

    for name, (style, seed) in {"pencil": ("pencil", 1), "bowl2": ("oil", 2), "pear": ("pear", 3), "bowlA": ("oil", 4), "bowlB": ("oil", 6),
                                "bowlC": ("oil", 7), "bowlD": ("oil", 9)}.items():
        path = wd / f"fruit-{name}.png"
        fruit_image(style, seed).save(path)
        ctx["images"][name] = load(path)
    path = wd / "canvas-ade.png"
    ade_image().save(path)
    ctx["images"]["ade"] = load(path)
    for st in (0, 1, 2, 4, 5):
        path = wd / f"canvas-stage-{st}.png"
        canvas_image(st).save(path)
        ctx["images"][f"mine{st}"] = load(path)
    ctx["pine_faces"] = {}
    for kind, stages in (("mum", 4), ("plain", 3), ("plain2", 3)):
        for st in range(stages):
            path = wd / f"pine-{kind}-{st}.png"
            pine_face_image(kind, st).save(path)
            ctx["pine_faces"][(kind, st)] = load(path)
    default = {1: "bowl2", 2: "bowlA", 3: "bowlB", 4: "bowlC", 5: "bowlD", 6: "bowlA", 7: "pencil"}
    for i, nm in default.items():
        set_img(ctx["emat"][i], ctx["images"][nm])
    set_img(ctx["emat"][8], ctx["images"]["mine0"])
    build_stool(kit, ctx, M)
    build_hall(kit, ctx, M, wd)
    build_bus(kit, ctx, M)
    build_cafe(kit, ctx, M)
    build_bakery(kit, ctx, M)
    build_flat(kit, ctx, M, wd)
    build_pair(kit, ctx, M, wd)
    ctx["props"] = build_props(kit, ctx, M)
    build_lights(kit, ctx)
    return ctx


RP_ = 3.7


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


def _line_t(tl, lid):
    return tl["lines"][lid]["onset"]


# the light of each moment: exposure, sky colour, sky strength
STATES = {
    "night": (-0.2, "#0c1018", 1.0),
    "cold": (-0.4, "#0c1018", 1.0),
    "warm": (0.75, "#0c1018", 1.0),
    "end": (1.15, "#0c1018", 1.0),
    "bus": (0.1, "#a9d2f4", 1.1),
    "cafe": (0.3, "#a9d2f4", 1.0),
    "bake": (0.3, "#a9d2f4", 1.0),
    "flat": (0.45, "#a9d2f4", 1.0),
    "pair": (0.25, "#0c1018", 1.0),
}
SITES = ("bus", "cafe", "bake", "flat", "pair")


def _seat_people(tl, t, kit):
    """Seated characters bend their legs flat; a bend key leans the torso toward a point."""
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
    # beards (once the cast exists)
    if not ctx.get("beard") and "ade.headg" in bpy.data.objects:
        R = faces.HEAD_R
        kit.box("ade.beard", (0.98, 0.34, 0.6), (0, -R + 0.1, -0.33), kit.plastic("#8d8d8a", 0.9, "beard"), bpy.data.objects["ade.headg"], bevel=0.14)
        ctx["beard"] = True
    # time of day, and which little set is on
    ts = _last(_cues(tl, "time"), t)
    state = ts["set"] if ts else "night"
    ev, sky, sk_s = STATES.get(state, STATES["night"])
    world = bpy.data.worlds[0].node_tree.nodes["Background"]
    world.inputs["Color"].default_value = kit.col(sky)
    world.inputs["Strength"].default_value = sk_s
    bpy.context.scene.view_settings.exposure = ev + float(spec.get("ev", 0.0))
    ctx["pane_mat"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.55
    # the rain runs down the north window
    tex = ctx["pane_mat"].node_tree.nodes[ctx["pane_mat"]["tex_name"]]
    if not ctx.get("pane_map"):
        nt = ctx["pane_mat"].node_tree
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], tex.inputs["Vector"])
        ctx["pane_map"] = mp
    ctx["pane_map"].inputs["Location"].default_value = (0, (t * 0.35) % 1.0, 0)
    # the faded ones: the pine look, from their acting keys
    active = None
    for who in story["geom"]["faders"]:
        root = bpy.data.objects.get(who)
        if root is None:
            continue
        fb, fh = fade_update(ctx, tl, t, who)
        if not root.hide_render and fh > 0.3 and (active is None or fh > active[1]):
            active = (who, fh)
    # the lamps and the dips
    in_room = state not in SITES
    dip = dip_gain(tl, t)
    for name in kit.LIGHTS:
        g = 1.0
        if name.startswith(("lamp ", "room fill", "foot")):
            g = dip if in_room else 0.0
            if state == "warm":
                g *= {"lamp ": 1.4, "room fill": 2.2, "foot": 1.8}[next(k for k in ("lamp ", "room fill", "foot") if name.startswith(k))]
            if state == "cold":
                g *= 0.7
        if name in ("unp key", "unp rim"):
            g = 0.0
            if active is not None and in_room:
                g = min(1.0, active[1] * 1.2) * dip
                if name == "unp key" and spec.get("unp_gain") is not None:
                    g *= float(spec["unp_gain"])
        for site, names in ctx["site_lights"].items():
            if name in names:
                g = 1.0 if state == site else 0.0
        if name == "shot fill":
            fl = spec.get("fill")
            if fl:
                kit.LIGHTS[name]["obj"].location = tuple(fl)
            g = 1.0 if fl else 0.0
        if name == "north rim":
            g = 0.4 if state == "warm" else (1.0 if in_room else 0.0)
            if state == "cold":
                g = 1.25
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
    ctx["lamp_objs"] = ctx["easels"]
    # a shot can hide what stands in front of its lens
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
    # the ceiling and roof come off for overhead shots
    ov = bool(spec.get("noceil"))
    ctx["easels"][7].rotation_euler = (0, 0, 0.0 if spec.get("turn8") else math.radians(ctx["TH"][7] + 90))
    ctx["ceiling"].hide_render = ov
    ctx["roof"].hide_render = ov
    ctx["tally"].hide_render = not spec.get("tally")
    for k, cu in enumerate(ctx["cushions"]):
        cu.hide_render = k != 0
    # the people sit and lean
    _seat_people(tl, t, kit)
    # the spare stool, my canvas, the others
    sc = _last(_cues(tl, "stool"), t)
    st = ctx["stool"]
    _show([st], bool(sc and sc.get("on")))
    if sc and sc.get("on"):
        st.location = (sc["pos"][0], sc["pos"][1], 0)
        st.rotation_euler = (0, 0, math.radians(sc.get("yaw", 0)))
    cv = _last(_cues(tl, "canvas"), t)
    set_img(ctx["emat"][8], ctx["images"][f"mine{int((cv or {}).get('stage', 0))}"])
    for c_ in _cues(tl, "easel"):
        if c_["t"] <= t:
            set_img(ctx["emat"][c_["i"]], ctx["images"][c_["img"]])
    # the hall
    hs = (_last(_cues(tl, "hall"), t) or {}).get("state", "now")
    for f in ctx["hall"]["frames"]:
        _show([f], hs == "then")
    for sq in ctx["hall"]["squares"]:
        sq.hide_render = hs == "then"
    _show([ctx["hall"]["portrait"]], hs in ("hung", "lift"))
    for o in ctx["hall"]["jar"]:
        o.hide_render = hs != "hung"
    ctx["hall"]["drawer"].location = (HX + 0.2, 3.0, 0.55)
    # the door swings after I run
    tl25 = _line_t(tl, "L25")
    ang = -72.0
    if t > tl25:
        ang = -72.0 + 38.0 * math.exp(-(t - tl25) * 1.6) * math.sin((t - tl25) * 5.0)
    ctx["door"].rotation_euler = (0, 0, math.radians(ang))
    # the props
    pr = {}
    for c_ in _cues(tl, "prop"):
        if c_["t"] <= t:
            pr[c_["which"]] = c_["on"]
    for k, objs in ctx["props"].items():
        for o in objs:
            o.hide_render = not pr.get(k)
    c0 = ctx["props"]["coat"]
    base = V((X0 + 0.12, -3.85, 1.45))
    for o, off in zip(c0, ((0, 0, 0), (0, 0.27, -0.05), (0, -0.27, -0.05))):
        o.location = base + V(off)
        o.rotation_euler = (0, 0, math.pi / 2)
    if pr.get("canvas_carry") and "me.arm1" in bpy.data.objects:
        o = ctx["props"]["canvas_carry"][0]
        o.location = bpy.data.objects["me.arm1"].matrix_world @ V((0.0, -0.3, -0.55))
        o.rotation_euler = (0, 0, 0)
    return over
