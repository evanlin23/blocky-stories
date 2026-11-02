"""ep32 "sitter": the set (a community arts centre life room on a rainy Wednesday, Mum's bare hall, a kitchen, a car park).

Everything is built once in build() from kit's parts; animate() only moves and switches what the story's cues say.
The cast (rig.py) is posed by bl_story from the story's acting. Nothing here carries text: no signs, no lettering.

Places (metres, floor z = 0, the car park at z = -0.45): the life room is centred on the dais at the origin
(x -5.6 .. 5.6, y -5.2 .. 5.0, ceiling 3.2). Easel i stands at angle TH[i] on a curve of radius RE with its canvas
facing out, its painter behind it at RP. Mum's hall is at x = 40 (a corridor along y, the west wall x = 39 holds the
frames), the kitchen at x = -40. The car park lies south of the room (y < -5.5), the steps outside the west door.

Cues read here (all optional):
- time: {"set": "night" | "day" | "show"} the light of the moment (night is the class; show is the bright Saturday)
- dip: {"down", "hold", "up", "depth", "hold_to"} the room's lamps ramp to (1 - depth), hold, ramp back (never dark)
- unp: {"on", "pos", "yaw", "head" (degrees relative) | "look" [x, y], "dais", "stage"} the Unpainted. One model
  (build_unp), only posed. It is found where it already is: never seen moving.
- stool: {"on", "pos", "yaw"} the paint-spattered spare stool; canvas: {"stage"} my canvas; easel: {"i", "img"}
- hall: {"state": then | now | hung | lift}; drawer: {"open"}; cushion: {"dent"}; show: {"on"}; prop: {"which", "on"}
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import bpy
from mathutils import Vector as V
from PIL import Image, ImageDraw, ImageFilter

from blocky import faces, rig

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
S = rig.S

X0, X1, Y0, Y1, CEIL = -5.6, 5.6, -5.2, 5.0, 3.2
GROUND = -0.45
DAIS_H = 0.22
HX, KX = 40.0, -40.0
GRAPHITE = (44, 42, 42)


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


def portrait_lines(d, ox, oy, W, H, stage, th, pale=(246, 240, 226)):
    """My drawing, in a W x H box at (ox, oy). The Unpainted's face is exactly these lines.
    stage 0: guide cross and two empty ovals; 1: + the short nose; 2: + a mouth corner; 3: + one eyebrow."""
    def P(u, v):
        return (ox + u * W, oy + v * H)

    pencil(d, [P(0.5, 0.06), P(0.5, 0.94)], th * 0.8)
    pencil(d, [P(0.1, 0.42), P(0.9, 0.42)], th * 0.8)
    for cx in (0.29, 0.71):
        oval(d, *P(cx, 0.42), 0.16 * W, 0.1 * H, th, fill=pale)
    if stage >= 1:
        pencil(d, [P(0.5, 0.5), P(0.53, 0.56), P(0.555, 0.605)], th)
    if stage >= 2:
        pencil(d, [P(0.33, 0.775), P(0.375, 0.795), P(0.425, 0.8)], th)
    if stage >= 3:
        pencil(d, [P(0.17, 0.32), P(0.24, 0.28), P(0.33, 0.275), P(0.4, 0.29)], th)


def canvas_image(stage):
    W, H = 480, 600
    im = paper(W, H, seed=3)
    d = ImageDraw.Draw(im)
    if stage <= 4:
        # the head oval, faint, then the lines
        oval(d, W * 0.5, H * 0.5, W * 0.4, H * 0.45, 4, col=(150, 150, 150))
        portrait_lines(d, W * 0.1, H * 0.06, W * 0.8, H * 0.88, min(stage, 3), 9)
    if stage == 4:   # the kind brown eyes go in over the guide ovals
        for cx in (0.3, 0.7):
            x, y = W * 0.1 + cx * W * 0.8, H * 0.06 + 0.42 * H * 0.88
            oval(d, x, y, 0.12 * W * 0.8, 0.07 * H * 0.88, 5, fill=(246, 240, 228))
            d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=(104, 62, 36))
            d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(24, 14, 10))
            d.ellipse([x + 5, y - 12, x + 14, y - 3], fill=(250, 246, 238))
            for k in range(3):
                pencil(d, [(x + (cx - 0.5) * 2 * 40 * 1.0, y + 4 + 6 * k), (x + (cx - 0.5) * 2 * 62, y + 12 + 12 * k - 4)], 4, (96, 70, 52))
    if stage >= 5:
        im = finished_portrait()
    return im


def finished_portrait(w=480, h=600):
    im = Image.new("RGB", (w, h), (231, 205, 160))
    d = ImageDraw.Draw(im)
    for y in range(h):
        k = y / h
        d.line([(0, y), (w, y)], fill=(int(228 - 30 * k), int(200 - 28 * k), int(158 - 24 * k)))
    d.rounded_rectangle([60, 440, 420, 640], radius=60, fill=(47, 127, 130))             # the cardigan
    d.rectangle([205, 380, 275, 450], fill=(232, 196, 160))                              # neck
    d.ellipse([120, 90, 360, 420], fill=(232, 196, 160))                                 # face
    d.pieslice([100, 60, 380, 340], 180, 360, fill=(190, 194, 200))                      # silver hair top
    d.rectangle([100, 190, 140, 380], fill=(190, 194, 200))
    d.rectangle([340, 190, 380, 380], fill=(190, 194, 200))
    for cx in (200, 280):                                                                # the glasses
        d.ellipse([cx - 38, 210, cx + 38, 280], outline=(107, 74, 46), width=7)
    d.line([(238, 240), (242, 240)], fill=(107, 74, 46), width=6)
    for cx in (200, 280):                                                                # brown eyes, lines at the corners
        d.ellipse([cx - 16, 230, cx + 16, 262], fill=(246, 240, 228))
        d.ellipse([cx - 11, 233, cx + 11, 259], fill=(104, 62, 36))
        d.ellipse([cx - 4, 240, cx + 4, 252], fill=(24, 14, 10))
        s = 1 if cx > 240 else -1
        for k in range(3):
            d.line([(cx + s * 38, 244 + 6 * (k - 1)), (cx + s * 56, 238 + 14 * (k - 1))], fill=(120, 88, 70), width=3)
        d.arc([cx - 30, 188, cx + 30, 218], 200, 340, fill=(120, 120, 124), width=5)       # brows
    d.arc([212, 330, 270, 378], 15, 165, fill=(168, 80, 80), width=7)                    # a mouth about to say it
    d.line([(244, 280), (238, 318), (250, 320)], fill=(200, 150, 124), width=4)
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
    """A framed landscape or flowers for Mum's hall and the show wall. No text."""
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


def pine_face_image(stage):
    """The Unpainted's head texture: raw pine with the same pencil lines as my canvas. Wraps the head (faces.py)."""
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
    fh = (faces.FY1 - faces.FY0) * 0.96
    fw = fh * 0.8
    portrait_lines(d, W / 2 - fw / 2, faces.FY0 + (faces.FY1 - faces.FY0) * 0.02, fw, fh, min(stage, 3), 26, pale=(247, 240, 224))
    return im


def tally_image():
    """Nine plain upright graphite strokes, no tenth. Upright in the image (v down)."""
    W, H = 1024, 1024
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rnd = random.Random(9)
    x0, gap = 262, 62
    for k in range(9):
        x = x0 + k * gap + rnd.randint(-3, 3)
        top, bot = 390 + rnd.randint(-8, 8), 640 + rnd.randint(-8, 8)
        d.line([(x, top), (x + rnd.randint(-5, 5), bot)], fill=(*GRAPHITE, 255), width=17)
        d.ellipse([x - 8, top - 8, x + 8, top + 8], fill=(*GRAPHITE, 255))
        d.ellipse([x - 8, bot - 8, x + 8, bot + 8], fill=(*GRAPHITE, 255))
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
    # the tally under it (hidden unless the dais is on its edge): nine strokes
    mt = img_mat(kit, "tally", tally_image(), ctx["wd"], rough=0.9, alpha=True)
    pl = uvplane(kit, "tally", (1.7, 1.7), (0, 0, -0.002), mt, d, (math.pi, 0, math.radians(90)))
    pl.location = (0, 0, 0.0)
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


# ------------------------------------------------------------------------------------------ the Unpainted


def build_unp(kit, ctx, M, wd):
    """The Unpainted: an R6 body in raw pine, wrong in one dimension (its torso is 1.4 times too long, its arms too
    long). Seated, its head is level with the easel tops. Built once and only posed. Its face is a texture per week."""
    pine = M["pine"]
    root = kit.empty("unp", (0, 0, 0))
    hip = kit.empty("unp hip", (0, 0, 0.62), root)
    for sx in (-1, 1):
        kit.box("unp thigh", (0.33, 0.72, 0.33), (sx * 0.17, -0.34, 0), pine, hip, bevel=0.03)
        kit.box("unp shin", (0.33, 0.33, 0.62), (sx * 0.17, -0.55, -0.4), pine, hip, bevel=0.03)
        kit.box("unp foot", (0.33, 0.42, 0.13), (sx * 0.17, -0.67, -0.69), pine, hip, bevel=0.03)
    tp = kit.empty("unp torso pivot", (0, 0, 0), hip)
    kit.box("unp torso", (0.62, 0.32, 0.95), (0, 0, 0.305), pine, tp, bevel=0.035)
    # two dark knots on the chest
    knot = kit.plastic("#5a3d22", 0.7, "knot")
    for (kx, kz, r) in ((-0.13, 0.55, 0.06), (0.17, 0.3, 0.045)):
        kit.sphere("knot", r, (kx, -0.172, kz), knot, tp, seg=10).scale = (1, 0.25, 1)
    sh = 0.305 + 0.475 - 0.08
    for sx in (-1, 1):
        arm = kit.empty(f"unp arm{sx}", (sx * 0.46, 0, sh), tp)
        kit.box("unp arm", (0.26, 0.28, 1.08), (0, 0, -0.5), pine, arm, bevel=0.03)
        arm.rotation_euler = (math.radians(-14), 0, 0)
    neck = kit.empty("unp neck", (0, 0, 0.305 + 0.475), tp)
    kit.box("unp neckm", (0.2, 0.2, 0.1), (0, 0, 0.0), pine, neck)
    ns = kit.empty("unp head scale", (0, 0, 0.02), neck)
    ns.scale = (S, S, S)
    head = kit.empty("unp head", (0, 0, 0), ns)
    hg = kit.empty("unp headg", (0, 0, faces.HEAD_H / 2 + 0.02), head)
    mat, tex = rig.head_material("unp", "#d9ba8c")
    ob = rig.head_mesh("unp headm", mat, hg)
    imgs = []
    for st in range(4):
        path = wd / f"unp-face-{st}.png"
        pine_face_image(st).save(path)
        im = bpy.data.images.load(str(path))
        im.colorspace_settings.name = "sRGB"
        imgs.append(im)
    tex.image = imgs[0]
    hb = mat.node_tree.nodes["Principled BSDF"]
    mat.node_tree.links.new(tex.outputs["Color"], hb.inputs["Emission Color"])
    hb.inputs["Emission Strength"].default_value = 0.12
    ctx["unp"] = {"root": root, "hip": hip, "tp": tp, "neck": head, "tex": tex, "imgs": imgs}
    # lit for fear: a key from below and the side, a cold rim from behind. Front lights are dead
    key = kit.light("unp key", "SPOT", (0, 0, 0), 240.0, "#ffa060", spot=34, blend=0.6, size=0.1)
    key.parent = root
    key.location = (0.45, -0.75, 0.15)
    key.rotation_euler = (V((0.0, 0.0, 1.78)) - V((0.45, -0.75, 0.15))).to_track_quat("-Z", "Y").to_euler()
    rim = kit.light("unp rim", "SPOT", (0, 0, 0), 150.0, "#7ea0e0", spot=50, blend=0.5, size=0.2)
    rim.parent = root
    rim.location = (-0.5, 1.1, 2.3)
    rim.rotation_euler = (V((0.0, -0.1, 1.6)) - V((-0.5, 1.1, 2.3))).to_track_quat("-Z", "Y").to_euler()
    root.hide_render = True
    for o in root.children_recursive:
        o.hide_render = True


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
    pm = img_mat(kit, "portrait", finished_portrait(), wd, rough=0.7)
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


def build_kitchen(kit, ctx, M, wd):
    kit.box("kit floor", (3.6, 4.2, 0.1), (KX, 0.5, -0.05), M["floor2"])
    kit.box("kit ceil", (3.6, 4.2, 0.1), (KX, 0.5, 2.65), M["ceilmat"])
    for (sx, sy, w, d) in ((-1.85, 0.5, 0.1, 4.2), (1.85, 0.5, 0.1, 4.2), (0, -1.65, 3.6, 0.1)):
        kit.box("kit wall", (w, d, 2.6), (KX + sx, sy, 1.3), M["hallwall"])
    kit.box("kit wall n a", (1.0, 0.1, 2.6), (KX - 1.3, 2.65, 1.3), M["hallwall"])
    kit.box("kit wall n b", (1.0, 0.1, 2.6), (KX + 1.3, 2.65, 1.3), M["hallwall"])
    kit.box("kit wall n c", (1.6, 0.1, 0.8), (KX, 2.65, 0.4), M["hallwall"])
    kit.box("kit wall n d", (1.6, 0.1, 0.6), (KX, 2.65, 2.3), M["hallwall"])
    kit.box("kit window", (1.6, 0.06, 1.2), (KX, 2.72, 1.4), M["win_day"])
    kit.box("kit table", (1.1, 0.8, 0.05), (KX, 0.55, 0.75), M["table"], bevel=0.01)
    for sx in (-0.5, 0.5):
        for sy in (-0.35, 0.35):
            kit.box("kit leg", (0.05, 0.05, 0.75), (KX + sx, 0.55 + sy, 0.37), M["table"])
    kit.cyl("kit mug", 0.045, 0.1, (KX + 0.2, 0.55, 0.83), M["mug"])
    kit.light("kit lamp", "AREA", (KX, 0.6, 2.5), 220.0, "#ffe6c4", size=1.6)
    kit.light("kit window", "AREA", (KX, 2.5, 1.6), 140.0, "#fff2e0", size=1.2).rotation_euler = (math.radians(75), 0, 0)


def build_props(kit, ctx, M):
    P = {}
    P["canvas_carry"] = [kit.box("carried canvas", (0.5, 0.03, 0.62), (0, 0, 0), M["canvas_back"])]
    P["bag"] = [kit.box("bag", (0.5, 0.2, 0.4), (0, 0, 0), M["bag"], bevel=0.04)]
    P["mug"] = [kit.cyl("held mug", 0.04, 0.1, (0, 0, 0), M["mug"])]
    P["phone"] = [kit.box("phone glow", (0.1, 0.18, 0.012), (0, 0, 0), M["phone"], bevel=0.005)]
    P["phone_mum"] = [kit.box("phone at ear", (0.05, 0.1, 0.17), (0, 0, 0), M["phone_off"], bevel=0.01)]
    coat = [kit.box("coat", (0.5, 0.12, 0.6), (0, 0, 0), M["coat"], bevel=0.04),
            kit.box("coat sleeve", (0.12, 0.1, 0.5), (0.3, 0, -0.05), M["coat"], bevel=0.03, rot=(0, 0.2, 0)),
            kit.box("coat sleeve", (0.12, 0.1, 0.5), (-0.3, 0, -0.05), M["coat"], bevel=0.03, rot=(0, -0.2, 0))]
    P["coat"] = coat
    for objs in P.values():
        for o in objs:
            o.hide_render = True
    return P


def build_lights(kit, ctx):
    ctx["hide_lights"] = []
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
    # daylight, for the show: ceiling panels and the window
    for k, (x, y) in enumerate(((-2.5, -1.0), (2.5, -1.0), (0.0, 2.0), (0.0, -3.5))):
        kit.light(f"show ceil {k}", "AREA", (x, y, 2.9), 80.0, "#fff6e6", size=2.0).rotation_euler = (math.pi, 0, 0)
    kit.light("show day", "AREA", (0.0, 4.0, 2.0), 250.0, "#f2f6ff", size=3.0).rotation_euler = (V((0, -1, -0.5)).to_track_quat("-Z", "Y").to_euler())
    for nm in list(kit.LIGHTS):
        if nm.startswith(("show ", "hall ", "kit ", "north rim", "drawer")):
            kit.LIGHTS[nm]["obj"].visible_camera = False
    # outside: the lamp post, a cold wash on the building
    kit.light("post light", "POINT", (-2.6, -9.0, GROUND + 3.4), 700.0, "#ffd29a", size=0.3)
    kit.light("ext wash", "AREA", (-12.0, -20.0, 14.0), 1400.0, "#5a73a8", size=6.0).rotation_euler = (V((12, 20, -14)).to_track_quat("-Z", "Y").to_euler())
    kit.light("step fill", "POINT", (-8.0, -4.6, 1.6), 70.0, "#ffb878", size=0.3)
    kit.light("door spill", "POINT", (X0 + 0.5, -2.85, 1.7), 40.0, "#ffbf80", size=0.2)


def build(kit, story, tl):
    global RE_
    g = story["geom"]
    RE_, ths = g["RE"], g["TH"]
    wd = workdir(tl)
    ctx = {"story": story, "wd": wd, "TH": ths}
    clear_lens(kit)
    M = materials(kit, wd)
    ctx["M"] = M
    build_room(kit, ctx, M)
    build_dais(kit, ctx, M)
    ctx["easels"], ctx["emat"] = [], {}
    for i, th in enumerate(ths, 1):
        e, mat = build_easel(kit, ctx, M, i, th, wd)
        ctx["easels"].append(e)
        ctx["emat"][i] = mat
    ctx["images"] = {}
    for name, (style, seed) in {"pencil": ("pencil", 1), "bowl2": ("oil", 2), "pear": ("pear", 3), "bowlA": ("oil", 4), "bowlB": ("oil", 6),
                                "bowlC": ("oil", 7), "bowlD": ("oil", 9)}.items():
        path = wd / f"fruit-{name}.png"
        fruit_image(style, seed).save(path)
        im = bpy.data.images.load(str(path))
        im.colorspace_settings.name = "sRGB"
        ctx["images"][name] = im
    for st in range(6):
        path = wd / f"canvas-stage-{st}.png"
        canvas_image(st).save(path)
        im = bpy.data.images.load(str(path))
        im.colorspace_settings.name = "sRGB"
        ctx["images"][f"mine{st}"] = im
    default = {1: "bowl2", 2: "bowlA", 3: "bowlB", 4: "bowlC", 5: "bowlD", 6: "bowlA", 7: "pencil"}
    for i, nm in default.items():
        set_img(ctx["emat"][i], ctx["images"][nm])
    set_img(ctx["emat"][8], ctx["images"]["mine0"])
    build_stool(kit, ctx, M)
    build_unp(kit, ctx, M, wd)
    build_hall(kit, ctx, M, wd)
    build_kitchen(kit, ctx, M, wd)
    ctx["props"] = build_props(kit, ctx, M)
    for nm in list(kit.LIGHTS):
        if nm.startswith(("hall ", "kit ")):
            kit.LIGHTS[nm]["obj"].visible_camera = False
    # the show wall: framed pictures on the west wall, the portrait among them
    show = []
    for k, y in enumerate((-0.5 - 1.1, 0.9 + 0.6, 2.0 + 0.9, 3.4 + 0.2)):
        f = kit.empty("show frame", (X0 + 0.08, y, 1.55))
        kit.box("sf", (0.04, 0.5, 0.64), (0, 0, 0), M["frame"], f)
        pm = img_mat(kit, f"showart{k}", fruit_image("oil", 10 + k), wd, rough=0.7)
        pl = uvplane(kit, "sfp", (0.44, 0.58), (0.0215, 0, 0), None, f, (math.pi / 2, 0, math.pi / 2))
        pl.data.materials.append(pm)
        show.append(f)
    sp = kit.empty("show portrait", (X0 + 0.09, -0.9, 1.55))
    kit.box("spf", (0.05, 0.7, 0.85), (0, 0, 0), M["frame"], sp)
    pm = img_mat(kit, "showportrait", finished_portrait(), wd, rough=0.7)
    pl = uvplane(kit, "spp", (0.6, 0.75), (0.026, 0, 0), None, sp, (math.pi / 2, 0, math.pi / 2))
    pl.data.materials.append(pm)
    ctx["show_wall"] = show + [sp]
    build_lights(kit, ctx)
    ctx["base_world"] = None
    return ctx


# ------------------------------------------------------------------------------------------ animation


def _show(objs, on):
    for o in objs:
        o.hide_render = not on
        for c_ in o.children_recursive:
            c_.hide_render = not on


def unp_state(ctx, tl, t, kit, hide=False):
    cs = _last(_cues(tl, "unp"), t)
    u = ctx["unp"]
    on = bool(cs and cs.get("on"))
    _show([u["root"]], on and not hide)
    if not on:
        return
    x, y = cs["pos"]
    yaw = cs.get("yaw", 0.0)
    z = DAIS_H if cs.get("dais") else 0.0
    u["root"].location = (x, y, z)
    u["root"].rotation_euler = (0, 0, math.radians(yaw))
    if "look" in cs:
        lx, ly = cs["look"]
        want = math.degrees(math.atan2(lx - x, -(ly - y)))
        rel = _wrap(want - yaw)
    else:
        rel = cs.get("head", 0.0)
    u["neck"].rotation_euler = (0, 0, math.radians(rel))
    u["tp"].rotation_euler = (math.radians(cs.get("lean", 0.0)), 0, 0)
    st = min(int(cs.get("stage", 0)), 3)
    u["tex"].image = u["imgs"][st]
    # its lights go with it
    for o in (kit.LIGHTS["unp key"]["obj"], kit.LIGHTS["unp rim"]["obj"]):
        o.hide_render = False


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
    # time of day
    ts = _last(_cues(tl, "time"), t)
    state = ts["set"] if ts else "night"
    show_on = bool((_last(_cues(tl, "show"), t) or {}).get("on"))
    world = bpy.data.worlds[0].node_tree.nodes["Background"]
    if show_on:
        world.inputs["Color"].default_value = kit.col("#cfe0f4")
        world.inputs["Strength"].default_value = 0.6
        bpy.context.scene.view_settings.exposure = 1.1
    else:
        world.inputs["Color"].default_value = kit.col("#0c1018")
        world.inputs["Strength"].default_value = 1.0
        bpy.context.scene.view_settings.exposure = {"night": -0.2, "warm": 0.75, "end": 1.15}.get(state, 0.5)
    bpy.context.scene.view_settings.exposure += float(spec.get("ev", 0.0))
    ctx["pane_mat"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.4 if show_on else 0.55
    # the rain runs down the north window
    if "pane" in ctx:
        tex = ctx["pane_mat"].node_tree.nodes[ctx["pane_mat"]["tex_name"]]
        if not ctx.get("pane_map"):
            nt = ctx["pane_mat"].node_tree
            tc = nt.nodes.new("ShaderNodeTexCoord")
            mp = nt.nodes.new("ShaderNodeMapping")
            nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
            nt.links.new(mp.outputs["Vector"], tex.inputs["Vector"])
            ctx["pane_map"] = mp
        ctx["pane_map"].inputs["Location"].default_value = (0, (t * 0.35) % 1.0, 0)
    # the lamps and the dips
    dip = dip_gain(tl, t)
    for name in kit.LIGHTS:
        g = 1.0
        if name.startswith(("lamp ", "room fill", "foot", "unp ")):
            g = 0.0 if show_on and name.startswith(("lamp ", "foot")) else dip
            if show_on and name.startswith("room fill"):
                g = 0.25
            if state == "warm":
                g *= {"lamp ": 1.4, "room fill": 2.2, "foot": 1.8, "unp ": 1.0}[next(k for k in ("lamp ", "room fill", "foot", "unp ") if name.startswith(k))]
        if name.startswith("show "):
            g = 1.0 if show_on else 0.0
            over[name] = g
            continue
        if name == "unp key" and spec.get("unp_gain") is not None:
            g *= float(spec["unp_gain"])
        if name == "shot fill":
            fl = spec.get("fill")
            if fl:
                kit.LIGHTS[name]["obj"].location = tuple(fl)
            g = 1.0 if fl else 0.0
        if name == "north rim":
            g = 0.15 if show_on else (0.4 if state == "warm" else 1.0)
        over[name] = g
    ctx["lamp_objs"] = [e for e in ctx["easels"]]
    for e in ctx["easels"]:
        e.hide_render = show_on
        for c_ in e.children_recursive:
            c_.hide_render = show_on
    for name in kit.LIGHTS:
        if name.startswith("lamp "):
            kit.LIGHTS[name]["obj"].hide_render = show_on
    # a shot can hide what stands in front of its lens
    for i in spec.get("hide_easels", []):
        e = ctx["easels"][i - 1]
        e.hide_render = True
        for c_ in e.children_recursive:
            c_.hide_render = True
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
    # the dais: on its feet, or on its edge against the west wall for the show
    dpos = _last(_cues(tl, "show"), t)
    d = ctx["dais"]
    stood = show_on and t < _line_t(tl, "L74")
    if stood:
        d.location = (X0 + 0.3, 1.8, 1.0)
        d.rotation_euler = (0, math.radians(-90), 0)
    else:
        d.location = (0, 0, 0)
        d.rotation_euler = (0, 0, 0)
    ctx["tally"].hide_render = not stood
    _show([ctx["dais_stool"]], not stood)
    for o in ctx["show_wall"]:
        _show([o], show_on)
    dent = (_last(_cues(tl, "cushion"), t) or {}).get("dent", 0.0)
    for k, cu in enumerate(ctx["cushions"]):
        cu.hide_render = stood or (k != (1 if dent > 0.5 else 0))
    # the Unpainted, the spare stool, my canvas, the others
    unp_state(ctx, tl, t, kit, bool(spec.get("hide_unp")))
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
    # the hall and its drawer
    hs = (_last(_cues(tl, "hall"), t) or {}).get("state", "then")
    for f in ctx["hall"]["frames"]:
        _show([f], hs == "then")
    for sq in ctx["hall"]["squares"]:
        sq.hide_render = hs == "then"
    pf = ctx["hall"]["portrait"]
    _show([pf], hs in ("hung", "lift"))
    for o in ctx["hall"]["jar"]:
        o.hide_render = hs != "hung"
    if hs == "hung":
        t0 = tl["lines"]["L76"]["end"] - 0.04
        k = math.exp(-max(0.0, t - t0) * 7.0) * math.cos(max(0.0, t - t0) * 24.0) if t > t0 else 0.0
        pf.rotation_euler = (math.radians(4.0 * k), 0, 0)
        pf.location = (HX - 0.97, 1.2, 1.55)
    elif hs == "lift":
        pf.location = (HX - 0.55, 1.35, 1.0)
        pf.rotation_euler = (0, math.radians(-8), 0)
    ctx["hall"]["drawer"].location = (HX + 0.2, 3.0 - 0.4 * _last(_cues(tl, "drawer"), t)["open"], 0.55) if _cues(tl, "drawer") else (HX + 0.2, 3.0, 0.55)
    # the door swings after I run
    tl47 = _line_t(tl, "L47")
    ang = -72.0
    if t > tl47:
        ang = -72.0 + 38.0 * math.exp(-(t - tl47) * 1.6) * math.sin((t - tl47) * 5.0)
    ctx["door"].rotation_euler = (0, 0, math.radians(ang))
    # the props follow their holders
    pr = {}
    for c_ in _cues(tl, "prop"):
        if c_["t"] <= t:
            pr[c_["which"]] = c_["on"]
    ep = ctx["easels"][7]
    th8 = math.radians(ctx["TH"][7])
    n8, t8 = (math.cos(th8), math.sin(th8)), (-math.sin(th8), math.cos(th8))
    ex, ey = ep.location.x, ep.location.y
    place = {
        "bag": ((ex + n8[0] * 0.55 + t8[0] * 0.3, ey + n8[1] * 0.55 + t8[1] * 0.3, 0.2), (0, 0, th8 + 0.4)),
        "phone": ((ex + n8[0] * 0.1 + t8[0] * 0.15, ey + n8[1] * 0.1 + t8[1] * 0.15, 0.845), (0, 0, th8 + math.pi / 2 + 0.3)),
        "coat": None,
    }
    for k, objs in ctx["props"].items():
        on = bool(pr.get(k))
        for o in objs:
            o.hide_render = not on
    for k, v in place.items():
        if k == "coat":
            c0 = ctx["props"]["coat"]
            base = V((X0 + 0.12, -3.85, 1.45))
            for o, off in zip(c0, ((0, 0, 0), (0, 0.27, -0.05), (0, -0.27, -0.05))):
                o.location = base + V(off)
                o.rotation_euler = (0, 0, math.pi / 2)
            continue
        loc, rot = v
        for o in ctx["props"][k]:
            o.location = loc
            o.rotation_euler = rot
    # held and worn props: look the cast up by name
    for who, which, part, off in (("me", "canvas_carry", "me.arm1", (0.0, -0.3, -0.55)), ("kofi", "mug", "kofi.arm1", (0.0, -0.3, -0.7))):
        if pr.get(which) and part in bpy.data.objects:
            o = ctx["props"][which][0]
            o.location = bpy.data.objects[part].matrix_world @ V(off)
            o.rotation_euler = (0, 0, 0)
    if pr.get("phone_mum") and "mum.headg" in bpy.data.objects:
        o = ctx["props"]["phone_mum"][0]
        o.location = bpy.data.objects["mum.headg"].matrix_world @ V((0.85, 0.05, 0.0))
        o.rotation_euler = bpy.data.objects["mum.headg"].matrix_world.to_euler()
    return over


def _e8(ctx, a, b):
    e = ctx["easels"][7]
    return (e.location.x + a, e.location.y + b)


def _line_t(tl, lid):
    return tl["lines"][lid]["onset"]
