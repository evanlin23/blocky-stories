"""ep155 "good boy": a butter-yellow house on a sunny street, three small stages far apart so their lights never mix.

  DALES   the Dales' street, front yard and picket gate, the house with its deck ("the step"), the front door with
          Pepper's photo and squiggles, his peg and blue leash, his teal bowl, a front room behind the wall with a
          ceiling and a window; day, then golden hour, then a blue dusk with the porch light on (the `tod` cue).
  ORTIZ   Mrs. Ortiz's lilac front room (the poodle in a fur coat).
  CORNER  a street corner with a blank sign (the man who can't read).
  DOG     Pepper the spaniel, built from kit blocks, shown only at the reveal (the `dog` cue).

The rule meter is a cream tag on the camera (a paw glyph and the clock), swapped by the `clock` cue. Cues read here:
clock (s), tod (v: day|gold|dusk), door (v 0..1), photo (v), wiggle (v), leash (v: on the peg), sausage (v), vac (v),
mug (v: in Dale's right hand), strap (v: the leash across Dale's hands), curtain (v), pose (who, sit, kneel, dur),
dog (v, sit, wag), thump. Nothing ever blinks: every light change is on a cut or eased over a long time.
"""
import math
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="goodboy-"))
FONT = Path(__file__).resolve().parents[2] / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"
W = {}
D2R = math.pi / 180


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def sample(name, tl, t, defaults, who=None):
    """The state of cue track `name` at t: numeric fields eased over a cue's own "dur"."""
    cur, prev = dict(defaults), dict(defaults)
    for c in tl["cues"]:
        if c["name"] != name or (who is not None and c.get("who") != who):
            continue
        if c["t"] > t:
            break
        prev = dict(cur)
        cur.update({k: v for k, v in c.items() if k in defaults})
        dur = c.get("dur", 0.0)
        if dur > 0 and t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            return {k: (prev[k] + (cur[k] - prev[k]) * u if isinstance(cur[k], (int, float)) else cur[k]) for k in cur}
    return cur


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def imat(kit, name, path, strength=1.0):
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    gc = nt.nodes.new("ShaderNodeTexCoord")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    img = bpy.data.images.load(path)
    img.colorspace_settings.name = "sRGB"
    tex.image = img
    return m, tex


def place_seg(ob, p, q):
    """Stretch a unit-length (z) box between two points."""
    p, q = Vector(p), Vector(q)
    d = q - p
    ob.location = (p + q) / 2
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    ob.scale = (1, 1, max(0.001, d.length))


# ---------------------------------------------------------------------------------------------- pictures (PIL)
def _paw(d, cx, cy, s, fill, ink=None):
    """A paw glyph: a pad and four toes."""
    ol = dict(outline=ink, width=max(2, int(s * 0.06))) if ink else {}
    d.ellipse([cx - s * 0.42, cy - s * 0.02, cx + s * 0.42, cy + s * 0.46], fill=fill, **ol)
    for (dx, dy, r) in ((-0.5, -0.12, 0.17), (-0.2, -0.38, 0.18), (0.2, -0.38, 0.18), (0.5, -0.12, 0.17)):
        d.ellipse([cx + dx * s - r * s, cy + dy * s - r * s * 1.2, cx + dx * s + r * s, cy + dy * s + r * s * 1.2],
                  fill=fill, **ol)


def _tag_image(clock):
    from PIL import Image, ImageDraw, ImageFont
    p = TMP / f"tag-{clock.replace(':', '')}.png"
    if not p.exists():
        Wd, Ht = 440, 260
        im = Image.new("RGB", (Wd, Ht), hx("#6a3d12"))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([12, 12, Wd - 13, Ht - 13], 34, fill=hx("#fff1cf"))
        _paw(d, 100, 128, 120, hx("#3a6fd8"), hx("#1c3a82"))
        f = ImageFont.truetype(str(FONT), 112 if len(clock) < 5 else 96)
        d.text((Wd - 30, Ht // 2 + 6), clock, font=f, fill=hx("#4a2a08"), anchor="rm")
        im.save(p)
    return str(p)


def _paw_image():
    from PIL import Image, ImageDraw
    p = TMP / "paw.png"
    if not p.exists():
        im = Image.new("RGB", (240, 240), hx("#f4ecd8"))
        d = ImageDraw.Draw(im)
        _paw(d, 120, 128, 150, hx("#3a6fd8"), hx("#1c3a82"))
        im.save(p)
    return str(p)


def _bowlpaw_image():
    from PIL import Image, ImageDraw
    p = TMP / "bowlpaw.png"
    if not p.exists():
        im = Image.new("RGB", (240, 240), hx("#2fa3a0"))
        d = ImageDraw.Draw(im)
        _paw(d, 120, 124, 150, hx("#fff4dc"), hx("#1c6a68"))
        im.save(p)
    return str(p)


def _photo_image():
    """A black and white photo of a spaniel on this porch's top step, on a red-check blanket (grey checks)."""
    from PIL import Image, ImageDraw
    p = TMP / "photo.png"
    if not p.exists():
        Wd, Ht = 400, 500
        im = Image.new("L", (Wd, Ht), 235)
        d = ImageDraw.Draw(im)
        d.rectangle([22, 22, Wd - 23, Ht - 23], fill=200)                 # the sky and house
        d.rectangle([22, 300, Wd - 23, Ht - 23], fill=150)                # the deck
        d.rectangle([22, 330, Wd - 23, 342], fill=110)
        for k in range(5):                                               # the house boards behind
            d.rectangle([22, 60 + k * 48, Wd - 23, 64 + k * 48], fill=185)
        for ix in range(6):                                              # the blanket's checks
            for iy in range(3):
                col = 235 if (ix + iy) % 2 == 0 else 95
                x0, y0 = 70 + ix * 44, 360 + iy * 34
                d.rectangle([x0, y0, x0 + 44, y0 + 34], fill=col)
        dog, dk = 250, 20
        d.rounded_rectangle([140, 250, 260, 372], 36, fill=dog)           # the body
        d.rounded_rectangle([156, 346, 244, 378], 14, fill=dog)           # the haunch
        d.rounded_rectangle([156, 150, 244, 252], 34, fill=dog)           # the head
        d.rounded_rectangle([188, 150, 212, 252], 8, fill=dk)             # the black streak
        d.rounded_rectangle([128, 160, 158, 262], 14, fill=dk)            # the long black ear
        d.rounded_rectangle([244, 166, 268, 236], 12, fill=215)           # the other ear
        d.rounded_rectangle([176, 220, 224, 260], 14, fill=dog, outline=170, width=2)   # the muzzle
        d.rectangle([194, 224, 206, 234], fill=dk)                        # the nose
        for ex in (176, 224):
            d.ellipse([ex - 7, 186, ex + 7, 200], fill=dk)
        d.rectangle([150, 320, 168, 372], fill=dog)
        d.rectangle([232, 320, 250, 372], fill=dog)
        d.rectangle([150, 255, 250, 262], fill=120)                       # the collar
        im.convert("RGB").save(p)
    return str(p)


def _squiggle_image():
    """Two rows of made-up squiggles on a paper strip. Never letters."""
    import random

    from PIL import Image, ImageDraw
    p = TMP / "squiggle.png"
    if not p.exists():
        Wd, Ht = 400, 150
        im = Image.new("RGB", (Wd, Ht), hx("#fff6e0"))
        d = ImageDraw.Draw(im)
        rnd = random.Random(7)
        for row, y0 in enumerate((46, 108)):
            x = 26
            while x < Wd - 60:
                wl = rnd.randint(40, 86)
                pts = []
                for i in range(wl):
                    u = i / wl
                    pts.append((x + i, y0 + 15 * math.sin(u * rnd.uniform(5, 9) * math.pi + row) * (1 - 0.3 * u)))
                d.line(pts, fill=hx("#2a2a30"), width=7, joint="curve")
                x += wl + rnd.randint(16, 26)
        im.save(p)
    return str(p)


def _sign_image():
    """A street sign: a blue border, a big arrow glyph and two rows of made-up squiggles. Never letters."""
    import random

    from PIL import Image, ImageDraw
    p = TMP / "sign.png"
    if not p.exists():
        Wd, Ht = 600, 400
        im = Image.new("RGB", (Wd, Ht), hx("#2f6aa8"))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([22, 22, Wd - 23, Ht - 23], 26, fill=hx("#fbf8ee"))
        d.polygon([(70, 110), (230, 110), (230, 60), (360, 150), (230, 240), (230, 190), (70, 190)], fill=hx("#1d4f8a"))
        rnd = random.Random(11)
        for row, y0 in enumerate((290, 346)):
            x = 70
            while x < Wd - 120:
                wl = rnd.randint(50, 100)
                pts = [(x + i, y0 + 11 * math.sin(i / wl * rnd.uniform(5, 9) * math.pi + row)) for i in range(wl)]
                d.line(pts, fill=hx("#2a2a30"), width=8, joint="curve")
                x += wl + rnd.randint(18, 30)
        d.rectangle([400, 90, 530, 130], fill=hx("#d8503a"))
        d.rectangle([400, 150, 500, 190], fill=hx("#d8503a"))
        im.save(p)
    return str(p)


def _blanket_image():
    from PIL import Image, ImageDraw
    p = TMP / "blanket.png"
    if not p.exists():
        im = Image.new("RGB", (390, 300), hx("#fff0d8"))
        d = ImageDraw.Draw(im)
        for ix in range(13):
            for iy in range(10):
                if (ix + iy) % 2 == 0:
                    d.rectangle([ix * 30, iy * 30, ix * 30 + 30, iy * 30 + 30], fill=hx("#d8322f"))
        d.rectangle([0, 0, 389, 299], outline=hx("#f2e4c8"), width=12)
        im.save(p)
    return str(p)


# ---------------------------------------------------------------------------------------------- the Dales
def build_street(kit):
    pl = kit.plastic
    HX = G.HX
    grass = kit.texture("grass", 0.5, tint="#86e27a")
    kit.box("g.lawn", (110, 70, 0.2), (HX, 8.0, -0.1), grass)
    asphalt = pl("#6a6e78", 0.8, spec=0.04)
    kit.box("g.road", (110, 7.0, 0.1), (HX, 0.0, -0.03), asphalt)
    dash = pl("#fff1b0", 0.7)
    for k in range(18):
        kit.box(f"g.dash{k}", (1.6, 0.14, 0.02), (HX - 40 + k * 4.6, 0.0, 0.03), dash)
    walk = pl("#e8e2d2", 0.8, spec=0.03)
    for sy, nm in ((4.3, "n"), (-4.3, "s")):
        kit.box(f"g.walk{nm}", (110, 1.6, 0.1), (HX, sy, -0.01), walk)
        kit.box(f"g.curb{nm}", (110, 0.2, 0.14), (HX, sy - math.copysign(0.9, sy), 0.0), pl("#c8c2b2", 0.8))
    kit.box("g.path", (1.4, 3.4, 0.07), (HX, 7.1, 0.01), walk)
    # the picket fence with a gate
    white = pl("#cfc8b6", 0.7, spec=0.03)
    for x0, x1 in ((G.HX - 9.0, G.GATE[0] - 0.65), (G.GATE[0] + 0.65, G.HX + 9.0)):
        n = int((x1 - x0) / 0.22)
        for k in range(n):
            kit.box(f"fence{x0:.0f}.{k}", (0.07, 0.03, 0.78), (x0 + 0.11 + k * 0.22, G.GATE[1], 0.39), white)
        for zr in (0.2, 0.6):
            kit.box(f"fence{x0:.0f}.r{zr}", (x1 - x0, 0.04, 0.06), (x0 + (x1 - x0) / 2, G.GATE[1] - 0.03, zr), white)
    for sx in (-1, 1):
        kit.box(f"gate.post{sx}", (0.14, 0.14, 1.0), (G.GATE[0] + sx * 0.68, G.GATE[1], 0.5), white, bevel=0.02)
    for k in range(5):
        kit.box(f"gate.p{k}", (0.07, 0.03, 0.72), (G.GATE[0] - 0.44 + k * 0.22, G.GATE[1], 0.36), white)
    for zr in (0.2, 0.55):
        kit.box(f"gate.r{zr}", (1.2, 0.04, 0.06), (G.GATE[0], G.GATE[1] - 0.03, zr), white)
    # houses across the street and on both sides (their fronts face the street), trees, far hills
    cols = ["#ffc9a8", "#a8e6cf", "#9cd3ff", "#f2b8d8", "#ffe39a", "#c8d8ff"]
    names = ["sub_building_type_a", "sub_building_type_f", "sub_building_type_p", "sub_building_type_c"]
    for i, x in enumerate((HX - 30, HX - 20, HX - 10, HX + 2, HX + 12, HX + 22, HX + 32)):
        kit.prop(names[i % 4], (x, -11.0, 0), rot=W.get("front_rot", 180), tint=cols[i % 6])
    for i, x in enumerate((HX - 26, HX - 14, HX + 24)):
        kit.prop(names[(i + 1) % 4], (x, 11.0, 0), rot=W.get("front_rot", 180), tint=cols[(i + 3) % 6])
    for x, y, s in ((HX - 6.5, 7.5, 1.2), (HX + 7.5, 8.0, 1.1), (HX - 16, 3.8, 1.0), (HX + 16, 3.8, 1.1),
                    (HX - 4, -6.2, 1.0), (HX + 9, -6.2, 1.0)):
        kit.prop("commontree_1", (x, y, 0), rot=37 * x, scale=s * 1.0)
    for x in (HX - 22, HX + 26):
        kit.prop("bush_1", (x, 6.0, 0), scale=1.0)
    kit.box("far.a", (160, 5, 7), (HX, -34, 2.5), pl("#9fd29a", 0.9, spec=0.01))
    kit.box("far.b", (160, 5, 11), (HX, -42, 4.5), pl("#b8d8e8", 0.9, spec=0.01))
    # the sun
    sun = kit.light("sun", "SUN", (HX - 14, -8, 22), 2.6, "#ffd89a", size=0.06)
    sun.data.angle = 0.06
    kit.aim(sun, (HX + 0.5, 11, 2.0))
    W["sun"] = sun


def build_house(kit):
    pl = kit.plastic
    HX, FY, DECK = G.HX, G.FY, G.DECK
    yellow = pl("#ffd966", 0.7, spec=0.04)
    trim = pl("#c4bcab", 0.7, spec=0.04)       # graded under 70% by the light: never a clipped wall
    x0, x1, y1 = 53.0, 67.0, 19.3
    zb = -0.2
    H = 5.6
    top = zb + H
    dx0, dx1 = HX - G.DOOR_W / 2, HX + G.DOOR_W / 2
    wx0, wx1 = G.WIN_X - G.WIN_W / 2, G.WIN_X + G.WIN_W / 2

    def wall(nm, xa, xb, za, zc, mat=yellow):
        kit.box(nm, (xb - xa, 0.3, zc - za), ((xa + xb) / 2, FY + 0.15, (za + zc) / 2), mat)
    wall("h.f.l", x0, wx0, zb, top)
    wall("h.f.wb", wx0, wx1, zb, G.WIN_Z0)
    wall("h.f.wt", wx0, wx1, G.WIN_Z1, top)
    wall("h.f.m", wx1, dx0, zb, top)
    wall("h.f.r", dx1, x1, zb, top)
    wall("h.f.dt", dx0, dx1, DECK + G.DOOR_H, top)
    kit.box("h.side.w", (0.3, y1 - FY, H), (x0 + 0.15, (FY + y1) / 2, zb + H / 2), yellow)
    kit.box("h.side.e", (0.3, y1 - FY, H), (x1 - 0.15, (FY + y1) / 2, zb + H / 2), yellow)
    kit.box("h.back", (x1 - x0, 0.3, H), (HX, y1 - 0.15, zb + H / 2), yellow)
    for sx in (x0, x1):
        kit.box(f"h.corner{sx}", (0.22, 0.22, H), (sx, FY - 0.02, zb + H / 2), trim)
    kit.box("h.belt", (x1 - x0, 0.08, 0.16), (HX, FY - 0.04, DECK + 3.4), trim)
    # the roof: a gable, ridge east-west
    eave = top
    ridge = top + 2.2
    ry0, ry1 = FY - 0.7, y1 + 0.5
    mid = (ry0 + ry1) / 2
    verts = [(x0 - 0.4, ry0, eave), (x1 + 0.4, ry0, eave), (x1 + 0.4, mid, ridge), (x0 - 0.4, mid, ridge),
             (x0 - 0.4, ry1, eave), (x1 + 0.4, ry1, eave)]
    faces = [(0, 1, 2, 3), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2), (0, 4, 5, 1)]
    kit.mesh_obj("h.roof", verts, faces, pl("#b8604a", 0.8, spec=0.03))
    # windows: the ground-floor front window (cream pane, bars), three upstairs
    pane = kit.emit("#dff0ff", 1.3, "winpane")
    W["pane_mat"] = pane

    def window(name, wx, wz, w, h, sill=True):
        kit.box(f"{name}.frame", (w + 0.24, 0.05, h + 0.24), (wx, FY - 0.025, wz), trim)
        p = kit.box(f"{name}.pane", (w, 0.02, h), (wx, FY - 0.05, wz), pane)
        noshadow(p)
        kit.box(f"{name}.barv", (0.05, 0.03, h), (wx, FY - 0.07, wz), trim)
        kit.box(f"{name}.barh", (w, 0.03, 0.05), (wx, FY - 0.07, wz), trim)
        if sill:
            kit.box(f"{name}.sill", (w + 0.4, 0.14, 0.06), (wx, FY - 0.07, wz - h / 2 - 0.15), trim)
    # the front window sits IN its gap: the pane fills the opening so the room shows light from outside
    zc = (G.WIN_Z0 + G.WIN_Z1) / 2
    hh = G.WIN_Z1 - G.WIN_Z0
    p = kit.box("h.win.pane", (G.WIN_W, 0.02, hh), (G.WIN_X, FY + 0.15, zc), pane)
    noshadow(p)
    for nm, sz, loc in (("v", (0.05, 0.08, hh), (G.WIN_X, FY + 0.12, zc)), ("h", (G.WIN_W, 0.08, 0.05), (G.WIN_X, FY + 0.12, zc))):
        kit.box(f"h.win.bar{nm}", sz, loc, trim)
    kit.box("h.win.frame.t", (G.WIN_W + 0.3, 0.1, 0.12), (G.WIN_X, FY - 0.04, G.WIN_Z1 + 0.06), trim)
    kit.box("h.win.frame.b", (G.WIN_W + 0.3, 0.1, 0.12), (G.WIN_X, FY - 0.04, G.WIN_Z0 - 0.06), trim)
    for sx in (-1, 1):
        kit.box(f"h.win.frame.s{sx}", (0.12, 0.1, hh + 0.24), (G.WIN_X + sx * (G.WIN_W / 2 + 0.06), FY - 0.04, zc), trim)
    kit.box("h.win.sill", (G.WIN_W + 0.5, 0.2, 0.06), (G.WIN_X, FY - 0.1, G.WIN_Z0 - 0.15), trim)
    for k, wx_ in enumerate((G.WIN_X, HX, 63.3)):
        window(f"h.win.u{k}", wx_, DECK + 3.95, 1.1, 1.2)
    # curtains inside the window, cream, two panels that sway
    cur = pl("#fff4e0", 0.9)
    W["curtain"] = [kit.box(f"h.curtain{s}", (0.5, 0.03, 1.45), (G.WIN_X + s * 0.62, FY + 0.34, zc), cur) for s in (-1, 1)]
    # the deck, two steps, rails
    wood = kit.texture("wood", 0.8, tint="#d9c9a8")
    kit.box("p.deck", (G.DECK_X1 - G.DECK_X0, FY - G.DECK_Y0, DECK + 0.1), ((G.DECK_X0 + G.DECK_X1) / 2, (FY + G.DECK_Y0) / 2, (DECK - 0.1) / 2), wood)
    kit.box("p.step2", (5.0, 1.2, 0.3), (HX - 0.6, G.DECK_Y0 - 0.6, 0.15), wood)
    kit.box("p.step3", (5.0, 0.6, 0.15), (HX - 0.6, G.DECK_Y0 - 1.5, 0.075), wood)
    for sx, xx in ((-1, G.DECK_X0 + 0.1), (1, G.DECK_X1 - 0.1)):
        kit.box(f"p.rail{sx}", (0.08, 1.9, 0.08), (xx, 11.0, DECK + 0.9), trim)
        kit.box(f"p.railb{sx}", (0.08, 1.9, 0.06), (xx, 11.0, DECK + 0.15), trim)
        for k in range(5):
            kit.box(f"p.bal{sx}{k}", (0.05, 0.05, 0.8), (xx, 10.3 + k * 0.42, DECK + 0.5), trim)
        kit.box(f"p.post{sx}", (0.14, 0.14, 1.1), (xx, 10.1, DECK + 0.55), trim, bevel=0.02)
        kit.box(f"p.postcap{sx}", (0.2, 0.2, 0.06), (xx, 10.1, DECK + 1.13), trim, bevel=0.02)
    # the porch rug (for the vacuum) and the red-check blanket on the top step
    kit.box("p.rug", (1.9, 1.1, 0.02), (HX + 0.2, 10.95, DECK + 0.011), pl("#7aa8e8", 0.9, spec=0.02))
    kit.box("p.rug.in", (1.6, 0.8, 0.012), (HX + 0.2, 10.95, DECK + 0.025), pl("#fff0c8", 0.9, spec=0.02))
    bm, _ = imat(kit, "blanket", _blanket_image(), 0.85)
    bl = kit.box("p.blanket", (1.3, 0.72, 0.025), (G.SEAT_ME[0], G.SEAT_ME[1] + 0.2, DECK + 0.0125 + 0.012), bm)
    noshadow(bl)
    # the door: a pivot at the west hinge, opening inward
    pv = kit.empty("h.doorpivot", (dx0, FY + 0.15, DECK))
    dm = pl("#d4c18c", 0.6, spec=0.06)
    kit.box("h.door", (G.DOOR_W, 0.07, G.DOOR_H), (G.DOOR_W / 2, 0.0, G.DOOR_H / 2), dm, pv, bevel=0.01)
    for k, (zz, h_) in enumerate(((0.3, 0.8), (1.25, 0.7))):
        kit.box(f"h.door.panel{k}", (0.9, 0.02, h_), (G.DOOR_W / 2, -0.045, zz + h_ / 2), pl("#c8b47e", 0.6), pv)
    kit.cyl("h.knob", 0.05, 0.05, (G.DOOR_W - 0.14, -0.07, 1.0), pl("#d8a83a", 0.3, spec=0.7), pv, rot=(math.pi / 2, 0, 0), n=14)
    kit.box("h.door.inside", (G.DOOR_W - 0.1, 0.02, G.DOOR_H - 0.1), (G.DOOR_W / 2, 0.045, G.DOOR_H / 2), pl("#d8c898", 0.7), pv)
    W["doorpivot"] = pv
    for sx, xx in ((-1, dx0 - 0.05), (1, dx1 + 0.05)):
        kit.box(f"h.jamb{sx}", (0.1, 0.2, G.DOOR_H + 0.1), (xx, FY, DECK + G.DOOR_H / 2 + 0.05), trim)
    kit.box("h.jamb.t", (G.DOOR_W + 0.2, 0.2, 0.1), (HX, FY, DECK + G.DOOR_H + 0.05), trim)
    # Pepper's photo and the squiggles under it, taped on the door (children of the pivot: they go with the door)
    ph, _ = imat(kit, "photo", _photo_image(), 0.95)
    sq, _ = imat(kit, "squiggle", _squiggle_image(), 0.95)
    pz = 1.55
    photo = kit.plane("h.photo", (0.52, 0.65), (G.DOOR_W / 2, -0.075, pz), ph, pv, rot=(math.pi / 2, 0, 0))
    tape = pl("#f0e08a", 0.5)
    tp = [kit.box(f"h.tape{s}", (0.1, 0.012, 0.045), (G.DOOR_W / 2 + s * 0.2, -0.07, pz + 0.31), tape, pv, rot=(0, s * 0.5, 0)) for s in (-1, 1)]
    sqs = kit.plane("h.squig", (0.5, 0.19), (G.DOOR_W / 2, -0.075, pz - 0.5), sq, pv, rot=(math.pi / 2, 0, 0))
    sqe = kit.empty("h.squigpivot", (G.DOOR_W / 2, -0.075, pz - 0.5), pv)
    sqs.parent = sqe
    sqs.location = (0, 0, 0)
    noshadow(photo)
    noshadow(sqs)
    W["photo"] = [photo, sqs] + tp
    W["squig"] = sqe
    # Pepper's peg board right of the door: a paw glyph above it, three cream tally strokes under it
    wd = pl("#a8703a", 0.6)
    kit.box("peg.board", (0.5, 0.05, 0.28), (G.PEG_X, FY - 0.025, G.PEG_Z), wd, bevel=0.01)
    kit.cyl("peg.peg", 0.03, 0.12, (G.PEG_X, FY - 0.11, G.PEG_Z - 0.02), pl("#6a4220", 0.6), rot=(math.pi / 2, 0, 0), n=12)
    pm, _ = imat(kit, "pawwall", _paw_image(), 0.9)
    pw = kit.plane("peg.paw", (0.34, 0.34), (G.PEG_X, FY - 0.012, G.PEG_Z + 0.43), pm, rot=(math.pi / 2, 0, 0))
    noshadow(pw)
    cream = pl("#fff6d8", 0.5)
    kit.box("peg.tallyboard", (0.36, 0.02, 0.34), (G.PEG_X + 0.32, FY - 0.02, G.PEG_Z - 0.4), pl("#6a3f1c", 0.6), bevel=0.005)
    for k in range(3):
        kit.box(f"peg.tally{k}", (0.045, 0.014, 0.24), (G.PEG_X + 0.2 + k * 0.12, FY - 0.04, G.PEG_Z - 0.4), cream, bevel=0.006)
    # the blue leash on the peg: a strap down from the peg and a handle loop (hidden when the `leash` cue is 0)
    blue = pl("#3a6fd8", 0.5)
    ls = [kit.box("leash.strap", (0.04, 0.012, 0.85), (G.PEG_X, FY - 0.14, G.PEG_Z - 0.46), blue, bevel=0.004)]
    for nm, sz, loc in (("t", (0.2, 0.012, 0.04), (G.PEG_X, FY - 0.14, G.PEG_Z - 0.88)),
                        ("b", (0.2, 0.012, 0.04), (G.PEG_X, FY - 0.14, G.PEG_Z - 1.16)),
                        ("l", (0.04, 0.012, 0.32), (G.PEG_X - 0.08, FY - 0.14, G.PEG_Z - 1.02)),
                        ("r", (0.04, 0.012, 0.32), (G.PEG_X + 0.08, FY - 0.14, G.PEG_Z - 1.02))):
        ls.append(kit.box(f"leash.{nm}", sz, loc, blue, bevel=0.004))
    ls.append(kit.box("leash.clip", (0.06, 0.03, 0.07), (G.PEG_X, FY - 0.13, G.PEG_Z - 0.03), pl("#cfd2d6", 0.3, spec=0.8)))
    W["leash"] = ls
    # a dusk porch lantern beside the door (warm, steady) and a fern
    lant = kit.emit("#ffe3a0", 1.0, "lantern")
    W["lantern_mat"] = lant
    noshadow(kit.box("p.lantern", (0.18, 0.18, 0.32), (HX - 1.1, FY - 0.14, DECK + 1.95), lant, bevel=0.03))
    kit.box("p.lantern.cap", (0.22, 0.22, 0.05), (HX - 1.1, FY - 0.14, DECK + 2.14), pl("#3a3a42", 0.5))
    kit.box("p.lantern.arm", (0.04, 0.16, 0.04), (HX - 1.1, FY - 0.05, DECK + 1.96), pl("#3a3a42", 0.5))
    noshadow(kit.box("p.lantern2", (0.18, 0.18, 0.32), (61.05, FY - 0.14, DECK + 1.95), lant, bevel=0.03))
    kit.box("p.lantern2.cap", (0.22, 0.22, 0.05), (61.05, FY - 0.14, DECK + 2.14), pl("#3a3a42", 0.5))
    kit.box("p.lantern2.arm", (0.04, 0.16, 0.04), (61.05, FY - 0.05, DECK + 1.96), pl("#3a3a42", 0.5))
    kit.prop("houseplant_1", (G.DECK_X1 - 0.8, 11.3, DECK), scale=2.4)
    kit.prop("houseplant_1", (G.DECK_X0 + 0.8, 11.3, DECK), scale=2.0)
    # Pepper's teal bowl with the paw glyph, and the plate (the sausage lies on it)
    bx, by = 61.6, 10.35
    kit.cyl("bowl.body", 0.2, 0.1, (bx, by, DECK + 0.05), pl("#2fa3a0", 0.4), n=24)
    kit.cyl("bowl.food", 0.15, 0.02, (bx, by, DECK + 0.1), pl("#c88a4a", 0.7), n=20)
    bpm, _ = imat(kit, "bowlpaw", _bowlpaw_image(), 0.9)
    bp = kit.plane("bowl.paw", (0.13, 0.13), (bx, by - 0.2 - 0.003, DECK + 0.05), bpm, rot=(math.pi / 2, 0, 0))
    noshadow(bp)
    px, py = 59.75, 10.28
    kit.cyl("plate.disc", 0.15, 0.02, (px, py, DECK + 0.01), pl("#f4f0e6", 0.4, spec=0.5), n=24)
    sa = kit.cyl("saus.body", 0.032, 0.2, (px, py, DECK + 0.05), pl("#b5502e", 0.5), rot=(0, math.pi / 2, 0.3), n=14)
    se = [kit.sphere("saus.e1", 0.032, (px - 0.09, py - 0.03, DECK + 0.05), pl("#a04526", 0.5), seg=10),
          kit.sphere("saus.e2", 0.032, (px + 0.09, py + 0.03, DECK + 0.05), pl("#a04526", 0.5), seg=10)]
    W["sausage"] = [sa] + se
    # the vacuum: a body, a wand to Dale's hands, a nozzle on the rug, a hose (placed each frame)
    red = pl("#d8503a", 0.5)
    dark = pl("#2a2a30", 0.7)
    vroot = kit.empty("vac.root", (0, 0, -40))
    kit.box("vac.body", (0.36, 0.5, 0.26), (0, 0, 0.17), red, vroot, bevel=0.04)
    kit.box("vac.lid", (0.3, 0.36, 0.06), (0, 0, 0.33), pl("#f2c85a", 0.5), vroot, bevel=0.02)
    for sx in (-1, 1):
        kit.cyl(f"vac.wheel{sx}", 0.07, 0.04, (sx * 0.2, 0.12, 0.07), dark, vroot, rot=(0, math.pi / 2, 0), n=14)
    W["vacroot"] = vroot
    W["wand"] = kit.box("vac.wand", (0.035, 0.035, 1.0), (0, 0, -40), pl("#c9ced6", 0.3, spec=0.7))
    W["nozzle"] = kit.box("vac.nozzle", (0.34, 0.14, 0.05), (0, 0, -40), dark, bevel=0.01)
    W["hose"] = [kit.box(f"vac.hose{i}", (0.05, 0.05, 1.0), (0, 0, -40), pl("#4a4a56", 0.7)) for i in range(7)]
    # the strap (Pepper's leash across Dale's hands) and the mug in Dale's right hand
    W["strap"] = kit.box("strap.leash", (0.045, 0.014, 1.0), (0, 0, -40), blue, bevel=0.004)
    W["strap2"] = kit.box("strap.leash2", (0.045, 0.014, 1.0), (0, 0, -40), blue, bevel=0.004)
    mug = kit.empty("mug", (0, 0, -40))
    kit.cyl("mug.cup", 0.065, 0.1, (0, 0, 0.05), pl("#fff6e6", 0.4, spec=0.5), mug, n=16)
    kit.box("mug.handle", (0.025, 0.07, 0.06), (0.08, 0, 0.05), pl("#fff6e6", 0.4), mug)
    kit.cyl("mug.tea", 0.055, 0.01, (0, 0, 0.098), pl("#8a4a22", 0.5), mug, n=14)
    W["mug"] = mug
    # lights: the sun is the key; soft fills to read faces; the dusk lamp
    fy = kit.light("yard.face", "AREA", (G.HX + 1.5, 3.2, 3.2), 1500, "#fff0d8", size=3.0, shadow=False)
    kit.aim(fy, (G.HX, 10.3, 1.5))
    fl = kit.light("porch.fill", "AREA", (G.HX - 1.0, 6.0, 3.0), 900, "#fff0d8", size=3.5, shadow=False)
    kit.aim(fl, (G.HX, 10.8, 1.2))
    fd = kit.light("porch.door", "AREA", (G.HX + 2.5, 7.5, 2.8), 500, "#fff2dc", size=3.0, shadow=False)
    kit.aim(fd, (G.HX - 0.5, 11.5, 1.6))
    lw = kit.light("wall.fill", "AREA", (G.HX, 3.0, 4.5), 2200, "#fff0d0", size=8.0, shadow=False)
    kit.aim(lw, (G.HX, 12.0, 2.0))
    kit.light("dusk.lamp", "POINT", (G.HX - 1.1, G.FY - 0.8, G.DECK + 2.0), 120, "#ffd27a", size=0.3, shadow=False)
    df = kit.light("dusk.fill", "AREA", (G.HX, 4.0, 3.5), 900, "#a8bfff", size=5.0, shadow=False)
    kit.aim(df, (G.HX, 11.0, 1.2))
    dk = kit.light("dusk.key", "AREA", (G.HX - 2.2, 6.0, 2.8), 1500, "#ffe9cc", size=3.0, shadow=False)
    kit.aim(dk, (G.HX - 0.7, 10.4, 1.4))
    dk2 = kit.light("dusk.key2", "AREA", (G.HX - 0.2, 11.2, 3.0), 1300, "#fff4e4", size=2.0, shadow=False)
    kit.aim(dk2, (G.HX - 0.7, 9.3, 1.3))


def build_room(kit):
    pl = kit.plastic
    HX, FY, DECK = G.HX, G.FY, G.DECK
    x0, x1, y0, y1 = G.ROOM
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    peach = pl("#ffdcb8", 0.85, spec=0.03)
    kit.box("r.floor", (x1 - x0, y1 - y0, 0.1), (cx, cy, DECK - 0.05), kit.texture("wood", 0.8, tint="#e8c48a"))
    kit.box("r.ceil", (x1 - x0, y1 - y0, 0.25), (cx, cy, DECK + G.ROOM_H + 0.125), kit.emit("#ffeed8", 1.6, "roomceil"))
    kit.box("r.back", (x1 - x0, 0.04, G.ROOM_H), (cx, y1 - 0.02, DECK + G.ROOM_H / 2), peach)
    kit.box("r.side.w", (0.04, y1 - y0, G.ROOM_H), (x0 + 0.02, cy, DECK + G.ROOM_H / 2), peach)
    kit.box("r.side.e", (0.04, y1 - y0, G.ROOM_H), (x1 - 0.02, cy, DECK + G.ROOM_H / 2), peach)
    dx0, dx1 = HX - G.DOOR_W / 2, HX + G.DOOR_W / 2
    wx0, wx1 = G.WIN_X - G.WIN_W / 2, G.WIN_X + G.WIN_W / 2
    yy = y0 + 0.02
    top = DECK + G.ROOM_H

    def seg(nm, xa, xb, za, zc):
        kit.box(nm, (xb - xa, 0.04, zc - za), ((xa + xb) / 2, yy, (za + zc) / 2), peach)
    seg("r.f.l", x0, wx0, DECK, top)
    seg("r.f.wb", wx0, wx1, DECK, G.WIN_Z0)
    seg("r.f.wt", wx0, wx1, G.WIN_Z1, top)
    seg("r.f.m", wx1, dx0, DECK, top)
    seg("r.f.r", dx1, x1, DECK, top)
    seg("r.f.dt", dx0, dx1, DECK + G.DOOR_H, top)
    kit.box("r.rug", (3.0, 2.2, 0.02), (58.8, 15.2, DECK + 0.01), pl("#e8695a", 0.9, spec=0.02))
    kit.box("r.rug.in", (2.6, 1.8, 0.012), (58.8, 15.2, DECK + 0.025), pl("#f2c05a", 0.9, spec=0.02))
    kit.box("r.wain", (x1 - x0, 0.03, 0.9), (cx, y1 - 0.055, DECK + 0.45), pl("#9fcf9a", 0.8, spec=0.03))
    kit.prop("couch_medium1", (58.6, 14.2, DECK), rot=W.get("couch_rot", 0), tint="#9fd3e8")
    kit.prop("houseplant_1", (x0 + 0.6, y1 - 0.6, DECK), scale=2.6)
    kit.prop("light_floor1", (x1 - 0.7, 17.5, DECK), height=1.6)
    for k, c in enumerate(("#8ad0ff", "#ffb08a", "#b8e6a0")):
        kit.box(f"r.picframe{k}", (0.9, 0.03, 0.7), (56.5 + k * 1.5, y1 - 0.07, DECK + 1.7), pl("#fff8ea", 0.6))
        kit.box(f"r.pic{k}", (0.78, 0.03, 0.58), (56.5 + k * 1.5, y1 - 0.09, DECK + 1.7), pl(c, 0.6))
    for i, (x, y) in enumerate(((57.5, 14.0), (62.0, 14.0), (57.5, 17.5), (62.0, 17.5), (60.0, 15.8))):
        a = kit.light(f"room.fill{i}", "AREA", (x, y, DECK + G.ROOM_H - 0.15), 60, "#ffe8c0", size=2.5, shadow=False)
        kit.aim(a, (x, y, DECK))
    rf = kit.light("room.face", "AREA", (63.5, 17.5, DECK + 2.2), 90, "#fff0dc", size=2.0, shadow=False)
    kit.aim(rf, (G.WIN_X, 12.9, DECK + 1.2))


def build_ortiz(kit):
    pl = kit.plastic
    ox, oy = G.ORT
    lil = pl("#cdb4f0", 0.85, spec=0.03)
    kit.box("o.floor", (9, 14, 0.2), (ox, oy - 6.5, -0.1), kit.texture("wood", 0.8, tint="#e8c890"))
    kit.box("o.back", (9, 0.3, 3.2), (ox, oy + 0.15, 1.6), lil)
    kit.box("o.wall.l", (0.3, 14, 3.2), (ox - 4.4, oy - 6.5, 1.6), lil)
    kit.box("o.wall.r", (0.3, 14, 3.2), (ox + 4.4, oy - 6.5, 1.6), lil)
    kit.box("o.wall.s", (9, 0.3, 3.2), (ox, oy - 13.6, 1.6), lil)
    kit.box("o.ceil", (9, 14, 0.2), (ox, oy - 6.5, 3.3), kit.emit("#fff4e4", 0.8, "oceil"))
    kit.box("o.rug", (3.4, 2.2, 0.02), (ox, oy - 3.0, 0.01), pl("#f2b8d8", 0.9, spec=0.02))
    kit.box("o.rug.in", (3.0, 1.8, 0.012), (ox, oy - 3.0, 0.025), pl("#fff0d8", 0.9, spec=0.02))
    kit.prop("couch_medium1", (ox, oy - 0.7, 0), rot=W.get("couch_rot", 0), tint="#7ad08a", scale=1.25)
    kit.box("o.win", (1.6, 0.04, 1.3), (ox + 2.8, oy - 0.01, 1.7), pl("#fffaf0", 0.6))
    p = kit.box("o.pane", (1.4, 0.02, 1.1), (ox + 2.8, oy - 0.04, 1.7), kit.emit("#dff0ff", 1.3, "opane"))
    noshadow(p)
    kit.box("o.curt", (0.4, 0.03, 1.6), (ox + 1.85, oy - 0.07, 1.65), pl("#f0d0f0", 0.9))
    kit.box("o.curt2", (0.4, 0.03, 1.6), (ox + 3.75, oy - 0.07, 1.65), pl("#f0d0f0", 0.9))
    for i, c in enumerate(("#ffd0a0", "#a0d8ff")):
        kit.box(f"o.picf{i}", (0.8, 0.03, 0.6), (ox - 2.4 + i * 0.1 - 0.6 * i, oy - 0.03, 1.8), pl("#fff8ea", 0.6))
        kit.box(f"o.pic{i}", (0.68, 0.03, 0.48), (ox - 2.4 + i * 0.1 - 0.6 * i, oy - 0.05, 1.8), pl(c, 0.6))
    kit.prop("houseplant_1", (ox - 3.4, oy - 0.7, 0), scale=2.4)
    kit.prop("light_floor1", (ox + 3.6, oy - 1.6, 0), height=1.7)
    for i, (x, y) in enumerate(((ox - 1.8, oy - 2.0), (ox + 1.8, oy - 2.0), (ox, oy - 5.0))):
        a = kit.light(f"o.fill{i}", "AREA", (x, y, 3.1), 300, "#fff3e0", size=3.0, shadow=False)
        kit.aim(a, (x, y, 0))
    f = kit.light("o.face", "AREA", (ox, oy - 7.0, 2.4), 420, "#fff6ec", size=3.0, shadow=False)
    kit.aim(f, (ox, oy - 1.8, 1.4))


def build_corner(kit):
    pl = kit.plastic
    cx, cy = G.COR
    kit.box("c.ground", (60, 60, 0.2), (cx, cy, -0.1), kit.texture("grass", 0.5, tint="#86e27a"))
    kit.box("c.road", (60, 6.0, 0.1), (cx, cy + 6.0, -0.03), pl("#6a6e78", 0.8, spec=0.04))
    kit.box("c.road2", (6.0, 30, 0.1), (cx + 6.0, cy + 16, -0.03), pl("#6a6e78", 0.8, spec=0.04))
    kit.box("c.walk", (60, 2.0, 0.1), (cx, cy + 1.9, -0.01), pl("#e8e2d2", 0.8, spec=0.03))
    cols = ["#ffc9a8", "#a8e6cf", "#9cd3ff", "#f2b8d8"]
    for i, x in enumerate((cx - 14, cx - 6, cx + 14, cx + 22)):
        kit.prop(["sub_building_type_a", "sub_building_type_f", "sub_building_type_p", "sub_building_type_c"][i],
                 (x, cy + 15.0, 0), rot=W.get("front_rot", 180) + 180, tint=cols[i])
    kit.prop("commontree_1", (cx - 3.4, cy - 1.5, 0), scale=1.2)
    kit.prop("commontree_1", (cx + 5.0, cy - 3.0, 0), scale=1.1)
    # the sign: a grey post and a plain white board with a dull border and nothing on it
    sx_, sy_ = cx + 1.0, cy + 0.9
    kit.box("c.post", (0.1, 0.1, 2.9), (sx_, sy_ + 0.1, 1.45), pl("#8a8f9a", 0.4, spec=0.5))
    kit.box("c.board.b", (1.5, 0.06, 1.0), (sx_, sy_ + 0.06, 2.35), pl("#2f6aa8", 0.5))
    sm_, _ = imat(kit, "sign", _sign_image(), 0.9)
    sg = kit.plane("c.board.face", (1.5, 1.0), (sx_, sy_ + 0.02, 2.35), sm_, rot=(math.pi / 2, 0, 0))
    noshadow(sg)
    kit.box("c.lamp", (0.1, 0.1, 3.4), (cx - 3.0, cy + 1.2, 1.7), pl("#3a3a42", 0.5))
    kit.box("c.lamphead", (0.5, 0.3, 0.2), (cx - 3.0, cy + 1.2, 3.45), pl("#3a3a42", 0.5))
    for i, (x, y) in enumerate(((cx, cy - 2.0), (cx - 3, cy - 4), (cx + 4, cy - 4))):
        a = kit.light(f"c.fill{i}", "AREA", (x, y, 4.0), 700, "#fff3e0", size=4.0, shadow=False)
        kit.aim(a, (x, y + 4, 0))
    f = kit.light("c.face", "AREA", (cx + 1.5, cy - 4.0, 2.8), 900, "#fff6ec", size=3.0, shadow=False)
    kit.aim(f, (cx, cy + 1.6, 1.5))
    sun = kit.light("c.sun", "SUN", (cx - 14, cy - 12, 20), 2.0, "#ffd89a", size=0.06)
    kit.aim(sun, (cx, cy + 2, 1.0))


# ---------------------------------------------------------------------------------------------- Pepper
def build_dog(kit, name="dog"):
    """A blocky spaniel (white, one long black ear, a black streak down his face, a blue collar), about 0.55 m at the
    back, facing -y. Returns the parts pose_dog moves."""
    pl = kit.plastic
    white = pl("#f6f1e6", 0.6)
    cream = pl("#e8dfcc", 0.6)
    black = pl("#17120e", 0.45, spec=0.5)
    blue = pl("#3a6fd8", 0.5)
    pink = pl("#e8788a", 0.5)
    root = kit.empty(name, (0, -80, 0))
    PV = (0.0, 0.25, 0.15)
    bg = kit.empty(f"{name}.bodyg", PV, root)

    def B(nm, size, loc, mat, par=None, rot=(0, 0, 0), bevel=0.0):
        p = par or bg
        if par is None:
            loc = (loc[0] - PV[0], loc[1] - PV[1], loc[2] - PV[2])
        return kit.box(f"{name}.{nm}", size, loc, mat, p, rot, bevel)

    B("body", (0.24, 0.56, 0.26), (0, 0.0, 0.34), white, bevel=0.05)
    B("patch", (0.245, 0.2, 0.12), (0, 0.1, 0.4), black, bevel=0.03)
    B("chest", (0.22, 0.14, 0.24), (0, -0.2, 0.35), white, bevel=0.05)
    B("collar", (0.255, 0.05, 0.27), (0, -0.28, 0.36), blue, bevel=0.015)
    B("tag", (0.05, 0.02, 0.05), (0, -0.31, 0.3), pl("#f2c230", 0.3, spec=0.7))
    tail = kit.empty(f"{name}.tail", (0, 0.28 - PV[1], 0.42 - PV[2]), bg)
    kit.box(f"{name}.tailb", (0.05, 0.05, 0.26), (0, 0.0, 0.11), white, tail, bevel=0.012)
    kit.box(f"{name}.tailtip", (0.056, 0.056, 0.08), (0, 0.0, 0.26), cream, tail, bevel=0.012)
    tail.rotation_euler = (-0.35, 0, 0)
    head = kit.empty(f"{name}.headg", (0, -0.29 - PV[1], 0.48 - PV[2]), bg)
    kit.box(f"{name}.head", (0.22, 0.24, 0.22), (0, -0.09, 0.02), white, head, bevel=0.05)
    kit.box(f"{name}.streak", (0.06, 0.02, 0.23), (0, -0.211, 0.02), black, head, bevel=0.01)
    kit.box(f"{name}.streakt", (0.06, 0.2, 0.012), (0, -0.09, 0.136), black, head, bevel=0.004)
    kit.box(f"{name}.snout", (0.13, 0.17, 0.11), (0, -0.26, -0.035), white, head, bevel=0.03)
    kit.box(f"{name}.nose", (0.075, 0.04, 0.055), (0, -0.35, -0.005), black, head, bevel=0.015)
    kit.box(f"{name}.mouth", (0.1, 0.012, 0.014), (0, -0.345, -0.065), black, head)
    tongue = kit.box(f"{name}.tongue", (0.055, 0.1, 0.016), (0, -0.315, -0.09), pink, head, bevel=0.005)
    ears = []
    for sx in (-1, 1):
        ep = kit.empty(f"{name}.earp{sx}", (sx * 0.115, -0.06, 0.1), head)
        kit.box(f"{name}.ear{sx}", (0.045, 0.13, 0.26), (sx * 0.014, 0.0, -0.12), black if sx < 0 else cream, ep, bevel=0.012)
        ears.append(ep)
        eye = kit.sphere(f"{name}.eye{sx}", 0.023, (sx * 0.065, -0.215, 0.05), black, head, seg=10)
        eye.scale = (0.9, 0.6, 1.15)
        kit.sphere(f"{name}.glint{sx}", 0.008, (sx * 0.06, -0.228, 0.06), white, head, seg=6)
        kit.box(f"{name}.brow{sx}", (0.055, 0.01, 0.013), (sx * 0.065, -0.22, 0.092), black, head, rot=(0, 0.25 * sx, 0))
    legs = []
    for nm, (lx, ly) in (("fl", (-0.075, -0.2)), ("fr", (0.075, -0.2)), ("hl", (-0.075, 0.2)), ("hr", (0.075, 0.2))):
        lp = kit.empty(f"{name}.{nm}", (lx - PV[0], ly - PV[1], 0.2 - PV[2]), bg)
        kit.box(f"{name}.{nm}b", (0.07, 0.07, 0.14), (0, 0, -0.07), white, lp, bevel=0.015)
        kit.box(f"{name}.{nm}p", (0.075, 0.09, 0.07), (0, -0.008, -0.165), cream, lp, bevel=0.015)
        legs.append(lp)
    haunch = kit.box(f"{name}.haunch", (0.22, 0.26, 0.22), (0, 0.3, 0.11), white, root, bevel=0.05)
    haunch.scale = (0.001, 0.001, 0.001)
    root.scale = (1.45, 1.45, 1.45)
    return {"root": root, "bodyg": bg, "head": head, "ears": ears, "legs": legs, "tail": tail, "tongue": tongue,
            "haunch": haunch, "PV": PV}


def pose_dog(d, st, t, thump):
    root, bg = d["root"], d["bodyg"]
    root.location = (st["x"], st["y"], st["z"])
    root.rotation_euler = (0, 0, st["yaw"] * D2R)
    sit = st["sit"]
    pitch = -0.78 * sit
    bg.rotation_euler = (pitch, 0, 0)
    bg.location = (d["PV"][0], d["PV"][1], d["PV"][2])
    hs = d["haunch"]
    hv = max(0.001, sit)
    hs.scale = (hv, hv, hv)
    hs.location = (0, 0.3, 0.11 * hv)
    d["head"].rotation_euler = (-pitch * 0.9 + 0.05 * math.sin(t * 1.3), 0, 0.08 * math.sin(t * 0.9))
    for k, ep in enumerate(d["ears"]):
        ep.rotation_euler = (0, 0.12 * (1 if k else -1), 0)
    d["tongue"].hide_render = st["tongue"] < 0.5
    wag = st["wag"]
    d["tail"].rotation_euler = (-0.35 - 0.1 * sit + 0.5 * thump, 0, 0.35 * math.sin(t * 9.0) * wag)
    fl, fr, hl, hr = d["legs"]
    pivz = d["PV"][2]
    zf = pivz + (-0.45) * math.sin(pitch) + 0.05 * math.cos(pitch)
    for lg in (fl, fr):
        lg.rotation_euler = (-pitch, 0, 0)
        sc = 1.0 + (zf / 0.2 - 1.0) * sit
        lg.scale = (1, 1, max(0.3, sc * (1 - 0.3 * sit)))
    for lg in (hl, hr):
        lg.rotation_euler = (-1.35 * sit, 0, 0)
        lg.scale = (1, 1, 1 - 0.5 * sit)


DOGKEYS = {"v": 0.0, "x": 58.9, "y": 10.55, "z": 0.0, "yaw": 0.0, "sit": 1.0, "wag": 0.0, "tongue": 1.0}


# ---------------------------------------------------------------------------------------------- build / animate
def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    m, tex = imat(kit, "tag", _tag_image("8:00"), 1.0)
    pl = kit.plane("tag.plane", (1.0, 0.5909), (0, 0, 0), m, root)
    pl.scale = (1.0, 1.0, 1.0)
    noshadow(pl)
    W["tagtex"] = tex
    W["tagimgs"] = {}
    W["clock"] = "8:00"


def attach_extras(kit):
    """Heads and bodies wear the extras once: Dale's moustache, my streak and ear patch, Rory's flat-top, the poodle's fur."""
    if W.get("extras_done"):
        return
    pl = kit.plastic
    dh = bpy.data.objects.get("dale.headg")
    mh = bpy.data.objects.get("me.headg")
    rh = bpy.data.objects.get("rory.headg")
    pm = bpy.data.objects.get("poodleman")
    if None in (dh, mh, rh, pm):
        return
    from blocky import faces
    R, H = faces.HEAD_R, faces.HEAD_H
    top = H / 2
    gray = pl("#b4b4bc", 0.8)
    for sx in (-1, 1):
        kit.box(f"dale.stache{sx}", (0.26, 0.06, 0.08), (sx * 0.14, -0.625, -0.2), gray, dh, rot=(0, sx * 0.3, 0), bevel=0.03)
    black = pl("#15151a", 0.6)
    kit.box("me.streak", (0.2, 2 * R * 0.95, 0.04), (0.0, 0.02, top + 0.115), black, mh, bevel=0.02)
    kit.box("me.streakf", (0.2, 0.04, 0.3), (0.0, -R - 0.075, top - 0.05), black, mh, bevel=0.02)
    kit.box("me.patch", (0.07, 0.6, 0.36), (R + 0.1, 0.2, top - 0.28), black, mh, bevel=0.03)
    for nm, hd, colr in (("dale", dh, "#3a2a1a"), ("ortiz", bpy.data.objects.get("ortiz.headg"), "#b04a8a")):
        fm = pl(colr, 0.4)
        for sx in (-1, 1):
            cx_ = sx * 0.25
            kit.box(f"{nm}.gt{sx}", (0.4, 0.03, 0.035), (cx_, -R - 0.04, 0.1), fm, hd)
            kit.box(f"{nm}.gb{sx}", (0.4, 0.03, 0.035), (cx_, -R - 0.04, -0.12), fm, hd)
            for ex_ in (-1, 1):
                kit.box(f"{nm}.gs{sx}{ex_}", (0.035, 0.03, 0.25), (cx_ + ex_ * 0.2, -R - 0.04, -0.01), fm, hd)
        kit.box(f"{nm}.gbridge", (0.1, 0.03, 0.035), (0, -R - 0.04, 0.06), fm, hd)
    for who_ in ("me", "rory", "dale", "poodleman"):
        root = bpy.data.objects.get(who_)
        lm = bpy.data.objects.get(f"{who_}.legm1")
        sh = bpy.data.objects.get(f"{who_}.shoe1")
        if root is None or lm is None or sh is None:
            continue
        pm_, sm2 = lm.active_material, sh.active_material
        sdim = (lm.dimensions.x, 1.0, 0.62)
        W.setdefault("shins", {})[who_] = []
        for sx in (-1, 1):
            a = kit.box(f"{who_}.shin{sx}", sdim, (0, 0, -60), pm_, root, bevel=0.08)
            b = kit.box(f"{who_}.shinfoot{sx}", (sdim[0], 1.01, 0.3), (0, 0, -60), sm2, root, bevel=0.08)
            W["shins"][who_].append((sx, a, b))
    kit.box("rory.flat", (2 * R + 0.02, 2 * R + 0.0, 0.36), (0, 0.0, top + 0.12), pl("#15151a", 0.65), rh, bevel=0.06)
    fur = pl("#f4efe2", 0.9, spec=0.02)
    fur2 = pl("#ebe4d4", 0.9, spec=0.02)
    for k, (x, y, z, sx, sy, sz) in enumerate((
            (0, -0.62, 3.9, 2.6, 1.0, 0.5), (-1.15, -0.5, 3.5, 0.7, 0.8, 0.6), (1.15, -0.5, 3.5, 0.7, 0.8, 0.6),
            (-0.7, -0.62, 2.9, 0.8, 0.45, 0.6), (0.7, -0.62, 2.9, 0.8, 0.45, 0.6), (0, -0.64, 2.4, 1.0, 0.5, 0.6),
            (-0.5, -0.64, 3.4, 0.7, 0.4, 0.5), (0.5, -0.64, 3.4, 0.7, 0.4, 0.5), (0, 0.6, 3.5, 2.4, 0.5, 1.4),
            (-1.5, 0, 3.5, 0.7, 1.1, 0.7), (1.5, 0, 3.5, 0.7, 1.1, 0.7))):
        kit.box(f"fur{k}", (sx, sy, sz), (x, y, z), fur if k % 2 == 0 else fur2, pm, bevel=0.16, seg=3)
    W["extras_done"] = True


def hand(who, sx):
    ob = bpy.data.objects.get(f"{who}.arm{sx}")
    if ob is None:
        return None
    return ob.matrix_world @ Vector((0, 0, -1.55))


def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    W["front_rot"] = story.get("set_args", {}).get("front_rot", 180)
    W["couch_rot"] = story.get("set_args", {}).get("couch_rot", 0)
    build_street(kit)
    build_house(kit)
    build_room(kit)
    build_ortiz(kit)
    build_corner(kit)
    W["dog"] = build_dog(kit)
    build_tag(kit)
    W["extras_done"] = False
    for nm, d in kit.LIGHTS.items():      # one global trim, so the bright grade never clips the sets
        f = 0.55 if nm in ("sun", "c.sun") else 0.28
        d["light"].energy *= f
        d["base"] = d["light"].energy
    return {}


TOD = {
    # sky colour, sky strength, sun colour, sun gain, face gains, lantern emission, dusk lamp gain, dusk fill gain, sun aim
    "day": dict(sky="#8fd0ff", ss=1.0, sun="#ffd89a", sg=1.0, face=1.0, lant=0.8, lamp=0.0, dfill=0.0, key=0.0, wall=1.0,
                pane=("#dff0ff", 1.3), pos=(46, -8, 22)),
    "gold": dict(sky="#ffcf94", ss=0.9, sun="#ffb064", sg=0.9, face=1.0, lant=0.8, lamp=0.0, dfill=0.0, key=0.0, wall=1.0,
                 pane=("#dff0ff", 1.3), pos=(40, -12, 6)),
    "dusk": dict(sky="#5a74c8", ss=0.3, sun="#ffb890", sg=0.1, face=0.2, lant=4.0, lamp=0.6, dfill=0.45, key=1.0, wall=0.16,
                 pane=("#5f7fd6", 0.9), pos=(40, -12, 4)),
}


def cam_now(story, tl, t):
    from blocky import polish
    if "specs" not in W:
        W["specs"] = polish.cam_specs(story, tl, polish.spec(story))
    shot = next((x for x in tl["shots"] if x["start"] <= t < x["end"]), tl["shots"][-1])
    keys = W["specs"][shot["id"]]["cam"]
    u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
    if u <= keys[0][0] or len(keys) == 1:
        k = keys[0]
        return k[1], k[2], k[3]
    for a, b in zip(keys, keys[1:]):
        if u <= b[0]:
            v = ss((u - a[0]) / max(1e-6, b[0] - a[0]))
            lerp = lambda p, q: [p[i] + (q[i] - p[i]) * v for i in range(3)]
            return lerp(a[1], b[1]), lerp(a[2], b[2]), a[3] + (b[3] - a[3]) * v
    k = keys[-1]
    return k[1], k[2], k[3]


def animate(kit, story, tl, t, ctx):
    attach_extras(kit)
    bpy.context.view_layer.update()
    # ---- the tag
    clock = sample("clock", tl, t, {"s": "8:00"})["s"]
    if clock != W["clock"]:
        if clock not in W["tagimgs"]:
            img = bpy.data.images.load(_tag_image(clock))
            img.colorspace_settings.name = "sRGB"
            W["tagimgs"][clock] = img
        W["tagtex"].image = W["tagimgs"][clock]
        W["clock"] = clock
    # ---- the time of day: the sky, the sun, the lamp
    tod = TOD[sample("tod", tl, t, {"v": "day"})["v"]]
    wd = bpy.context.scene.world
    bg = wd.node_tree.nodes["Background"]
    c = kit.col(tod["sky"])
    bg.inputs["Color"].default_value = c
    bg.inputs["Strength"].default_value = tod["ss"]
    sun = kit.LIGHTS["sun"]["light"]
    sun.color = kit.col(tod["sun"])[:3]
    W["sun"].location = tod["pos"]
    kit.aim(W["sun"], (G.HX + 0.5, 11, 2.0))
    W["lantern_mat"].node_tree.nodes["Emission"].inputs["Strength"].default_value = tod["lant"]
    pe = W["pane_mat"].node_tree.nodes["Emission"]
    pe.inputs["Color"].default_value = kit.col(tod["pane"][0])
    pe.inputs["Strength"].default_value = tod["pane"][1]
    # ---- the door, the photo, the squiggles, the leash on its peg, the curtain
    dr = sample("door", tl, t, {"v": 0.0})["v"]
    W["doorpivot"].rotation_euler = (0, 0, math.radians(100) * dr)
    ph = sample("photo", tl, t, {"v": 0.0})["v"] > 0.5
    for ob in W["photo"]:
        ob.hide_render = not ph
    wig = sample("wiggle", tl, t, {"v": 0.0})["v"]
    W["squig"].rotation_euler = (0, 0, 0.05 * wig * math.sin(t * 9.0))
    W["squig"].scale = (1 + 0.05 * wig * math.sin(t * 7.0 + 1), 1 + 0.12 * wig * math.sin(t * 8.0), 1)
    lv = sample("leash", tl, t, {"v": 1.0})["v"] > 0.5
    for ob in W["leash"]:
        ob.hide_render = not lv
    sv = sample("sausage", tl, t, {"v": 1.0})["v"] > 0.5
    for ob in W["sausage"]:
        ob.hide_render = not sv
    cv = sample("curtain", tl, t, {"v": 0.0})["v"]
    zc = (G.WIN_Z0 + G.WIN_Z1) / 2
    for i, ob in enumerate(W["curtain"]):
        sx = (-1, 1)[i]
        ob.location.x = G.WIN_X + sx * 0.62 - sx * 0.12 * cv + 0.12 * math.sin(t * 3.0 + i) * cv
    # ---- who sits, who kneels: a two-part leg (a thigh, then a shin that hangs down or lies back)
    for who in ("me", "rory", "dale", "poodleman"):
        root = bpy.data.objects.get(who)
        if root is None:
            continue
        ps = sample("pose", tl, t, {"sit": 0.0, "kneel": 0.0, "up": 0.0}, who)
        s_, k_, up_ = ps["sit"], ps["kneel"], ps["up"]
        f = root.scale.z
        shins = W.get("shins", {}).get(who, [])
        bent = (s_ > 0 or k_ > 0) and bool(shins)
        if s_ > 0 or k_ > 0:
            root.location.z += f * (s_ * (0.5 - 2.0) + k_ * (1.43 - 2.0))
        for sx, a, b in shins:
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            shoe = bpy.data.objects.get(f"{who}.shoe{sx}")
            if not bent:
                leg.scale = (1, 1, 1)
                a.location = b.location = (0, 0, -60)
                continue
            a1 = -math.acos(min(1.0, max(0.0, (1.1 - 1.1 * s_) / 0.93))) if s_ > 0 else 0.0
            a2 = 0.9 * up_ * s_ + (math.pi / 2) * k_
            T = 0.93
            leg.rotation_euler = (a1, 0, 0)
            leg.scale = (1, 1, T / 1.72)
            shoe.hide_render = True
            hx_ = leg.location.x
            d1 = Vector((0, math.sin(a1), -math.cos(a1)))
            d2 = Vector((0, math.sin(a2), -math.cos(a2)))
            K = Vector((hx_, 0, 2.0)) + d1 * T
            a.location = K + d2 * 0.31
            b.location = K + d2 * 0.77
            a.rotation_euler = b.rotation_euler = (a2, 0, 0)
    # ---- the vacuum
    vv = sample("vac", tl, t, {"v": 0.0})["v"] > 0.5
    vroot, wand, noz, hose = W["vacroot"], W["wand"], W["nozzle"], W["hose"]
    hl, hr = hand("dale", -1), hand("dale", 1)
    if vv and hl is not None and hr is not None:
        top = (hl + hr) / 2
        sl = 0.22 * math.sin(t * 3.2)
        nz = Vector((top.x, top.y - 0.85 + sl, G.DECK + 0.05))
        vroot.location = (G.HX + 1.0, 11.35, G.DECK)
        vroot.rotation_euler = (0, 0, 0)
        wand.hide_render = noz.hide_render = False
        place_seg(wand, top, nz + Vector((0, 0.02, 0.03)))
        noz.location = nz
        noz.rotation_euler = (0, 0, 0)
        noz.scale = (1, 1, 1)
        a, b = Vector((vroot.location.x - 0.15, vroot.location.y - 0.25, G.DECK + 0.15)), nz + Vector((0.0, 0.05, 0.06))
        pts = []
        for i in range(8):
            u = i / 7
            p = a.lerp(b, u)
            p.z = G.DECK + 0.03 + 0.12 * math.sin(u * math.pi) + (1 - u) * 0.1
            p.x += 0.3 * math.sin(u * math.pi) * (1 if i % 1 == 0 else 0)
            pts.append(p)
        for i, ob in enumerate(hose):
            ob.hide_render = False
            place_seg(ob, pts[i], pts[i + 1])
    else:
        vroot.location = (0, 0, -40)
        wand.hide_render = noz.hide_render = True
        for ob in hose:
            ob.hide_render = True
        noz.location = (0, 0, -40)
    # ---- the strap across Dale's hands, the mug
    sv2 = sample("strap", tl, t, {"v": 0.0})["v"] > 0.5
    hl, hr = hand("dale", -1), hand("dale", 1)
    if sv2 and hl is not None and hr is not None:
        ly = (hl.y + hr.y) / 2 - 0.1
        pl_, pr_ = Vector((hl.x, ly, G.DECK + 0.64)), Vector((hr.x, ly, G.DECK + 0.64))
        mid = (pl_ + pr_) / 2 + Vector((0, -0.05, -0.05))
        W["strap"].hide_render = W["strap2"].hide_render = False
        place_seg(W["strap"], pl_, mid)
        place_seg(W["strap2"], mid, pr_)
    else:
        W["strap"].hide_render = W["strap2"].hide_render = True
        W["strap"].location = W["strap2"].location = (0, 0, -40)
    mg = sample("mug", tl, t, {"v": 0.0})["v"] > 0.5
    h1 = hand("dale", 1)
    if mg and h1 is not None:
        W["mug"].location = h1 + Vector((0, 0, 0.0))
        for c_ in W["mug"].children:
            c_.hide_render = False
    else:
        W["mug"].location = (0, 0, -40)
    # ---- Pepper
    dg = sample("dog", tl, t, DOGKEYS)
    th = 0.0
    for c_ in tl["cues"]:
        if c_["name"] == "thump" and c_["t"] <= t < c_["t"] + 0.3:
            u = (t - c_["t"]) / 0.3
            th = max(th, math.sin(math.pi * u) ** 2)
    if dg["v"] > 0.5:
        pose_dog(W["dog"], dg, t, th)
    else:
        W["dog"]["root"].location = (0, -80, 0)
    kb = sample("keyb", tl, t, {"v": 0.0})["v"]
    # ---- the lights by time of day
    lights = {"sun": tod["sg"], "yard.face": tod["face"], "porch.fill": tod["face"], "porch.door": tod["face"],
              "wall.fill": tod["wall"], "dusk.lamp": tod["lamp"], "dusk.fill": tod["dfill"], "dusk.key": tod["key"] * (1 - 0.7 * kb),
              "dusk.key2": tod["key"] * kb}
    return lights
