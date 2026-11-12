"""ep143 "my old house key went warm": five small stages, all bright and sunny, far apart so their lights never mix.

  APT     my apartment entry (origin): a sunny hallway with a row of key hooks, a framed photo, a hall table and a ceiling.
  HILL    a sloped street of small painted houses, running north up to the old blue house; HOUSE is that house: a white
          porch with a roof, three steps, a white door with a green dinosaur sticker, windows glowing warm, a hall behind
          the door with a ceiling, stairs, a cake and streamers.
  PIZZA   a front door (the pizza guy); GYM a locker row (the buddy); INSERT the old door's lock with the pencil tally.

The rule meter is a cream tag on the camera (a key glyph and five pips), swapped by the `pips` cue. The key and its green
dinosaur are two small props that follow the `key` cue (hang on a hook, stand on a palm, sit in a lock, hang inside the old
house). The key's tip warms with the `heat` cue: steady, never a blink. Every extra is made in build(); animate only moves,
shows and hides them. Nothing ever blinks, flickers or switches fast.
"""
import math
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="warmkey-"))
W = {}
KS, DS = 1.6, 1.25           # the key's and the dinosaur's size
ORANGE = "#ff9a3a"


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def sample(name, tl, t, defaults):
    """The state of cue track `name` at t: numeric fields eased over a cue's own "dur"."""
    cur, prev = dict(defaults), dict(defaults)
    for c in tl["cues"]:
        if c["name"] != name:
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


# ---------------------------------------------------------------------------------------------- pictures (PIL)
def _tag_image(n):
    from PIL import Image, ImageDraw
    p = TMP / f"tag-{n}.png"
    if not p.exists():
        Wd, Ht = 400, 300
        im = Image.new("RGB", (Wd, Ht), hx("#5a3410"))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([14, 14, Wd - 15, Ht - 15], 30, fill=hx("#fff1cf"))
        ink = hx("#4a2a08")
        brass = hx("#e0a830")
        # the key glyph, pointing right: a ring, a shaft and two teeth
        d.ellipse([34, 40, 134, 140], fill=brass, outline=ink, width=10)
        d.ellipse([66, 72, 102, 108], fill=hx("#fff1cf"), outline=ink, width=7)
        d.rectangle([128, 78, 350, 104], fill=brass, outline=ink, width=8)
        d.rectangle([278, 102, 304, 142], fill=brass, outline=ink, width=8)
        d.rectangle([318, 102, 344, 130], fill=brass, outline=ink, width=8)
        for i in range(5):
            cx = 62 + i * 69
            on = i < n
            d.ellipse([cx - 28, 196, cx + 28, 252], fill=hx("#ff7a1a") if on else hx("#d9cba8"),
                      outline=hx("#7a2a00") if on else hx("#8a7650"), width=7)
            if on:
                d.ellipse([cx - 11, 207, cx + 7, 225], fill=hx("#ffd08a"))
        im.save(p)
    return str(p)


def _phone_image():
    from PIL import Image, ImageDraw
    p = TMP / "phone.png"
    if not p.exists():
        im = Image.new("RGB", (200, 400), hx("#1c2744"))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([8, 8, 191, 391], 22, fill=hx("#dfeaff"))
        d.rounded_rectangle([28, 70, 172, 230], 34, fill=hx("#ffffff"), outline=hx("#3a5a9a"), width=7)
        d.polygon([(52, 224), (52, 270), (98, 226)], fill=hx("#ffffff"), outline=hx("#3a5a9a"))
        d.rectangle([48, 220, 98, 228], fill=hx("#ffffff"))
        ink = hx("#2a3f7a")
        d.arc([72, 100, 128, 154], 180, 40, fill=ink, width=12)      # the "?" hook
        d.line([(110, 140), (100, 168)], fill=ink, width=12)
        d.ellipse([92, 178, 110, 196], fill=ink)
        d.rounded_rectangle([40, 300, 160, 330], 12, fill=hx("#9ab8e8"))
        im.save(p)
    return str(p)


def _face(d, cx, cy, r, skin, ink):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hx(skin), outline=hx("#8a6a48"), width=3)
    for sx in (-1, 1):
        d.ellipse([cx + sx * r * 0.42 - r * 0.1, cy - r * 0.15, cx + sx * r * 0.42 + r * 0.1, cy + r * 0.12], fill=hx(ink))
        d.line([(cx + sx * r * 0.62, cy - r * 0.38), (cx + sx * r * 0.22, cy - r * 0.34)], fill=hx(ink), width=5)
    d.arc([cx - r * 0.5, cy - r * 0.05, cx + r * 0.5, cy + r * 0.58], 15, 165, fill=hx(ink), width=6)


def _photo_image():
    from PIL import Image, ImageDraw
    p = TMP / "photo.png"
    if not p.exists():
        Wd, Ht = 640, 480
        im = Image.new("RGB", (Wd, Ht), hx("#9fd8ff"))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 330, Wd, Ht], fill=hx("#6fcf62"))
        d.ellipse([480, 30, 570, 120], fill=hx("#ffe58a"))
        ink = "#2a1a12"
        # me (left): navy jacket, spiky hair; Jess (right): red sweater, long hair
        d.rectangle([90, 250, 290, 480], fill=hx("#26386a"))
        d.rectangle([350, 250, 550, 480], fill=hx("#d8322f"))
        d.rectangle([330, 150, 570, 380], fill=hx("#15151a"))        # her hair behind the head
        _face(d, 190, 175, 95, "#d9b48a", ink)
        d.polygon([(95, 110), (120, 40), (150, 100), (180, 30), (210, 100), (250, 40), (285, 110)], fill=hx("#15151a"))
        d.rectangle([98, 70, 282, 112], fill=hx("#15151a"))
        _face(d, 450, 175, 95, "#d9b48a", ink)
        d.rectangle([358, 68, 542, 118], fill=hx("#15151a"))
        im.save(p)
    return str(p)


def _dino_image():
    from PIL import Image, ImageDraw
    p = TMP / "sticker.png"
    if not p.exists():
        S = 400
        im = Image.new("RGB", (S, S), hx("#fff6dc"))
        d = ImageDraw.Draw(im)
        d.ellipse([6, 6, S - 7, S - 7], fill=hx("#fff6dc"), outline=hx("#2a7a36"), width=14)
        g, dg, ink = hx("#4ccf5a"), hx("#2f9a3e"), hx("#1c5a26")
        d.ellipse([80, 170, 290, 290], fill=g, outline=ink, width=7)                                   # body
        d.polygon([(250, 190), (300, 120), (330, 120), (330, 160), (290, 210)], fill=g, outline=ink)  # neck
        d.rounded_rectangle([290, 95, 370, 150], 18, fill=g, outline=ink, width=7)                     # head
        d.polygon([(100, 210), (30, 250), (60, 280), (130, 270)], fill=g, outline=ink)                 # tail
        for x in (110, 150, 220, 258):
            d.rectangle([x, 270, x + 30, 330], fill=g, outline=ink, width=6)                           # legs
        for i, x in enumerate((120, 165, 210, 250)):
            d.polygon([(x, 175), (x + 22, 120 + i * 6), (x + 44, 175)], fill=dg, outline=ink)         # plates
        d.ellipse([340, 108, 354, 122], fill=ink)
        im.save(p)
    return str(p)


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


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


# ---------------------------------------------------------------------------------------------- the apartment
def build_apt(kit):
    pl = kit.plastic
    wall = pl("#f6e2b8", 0.85, spec=0.03)
    wood = kit.texture("wood", 0.7, tint="#e8c890")
    ceil = kit.emit("#fff1dc", 0.7, "aptceil")
    cx = (G.AX0 + G.AX1) / 2
    cy = (G.AY0 + G.AY1) / 2
    lx, ly = G.AX1 - G.AX0, G.AY1 - G.AY0
    kit.box("apt.floor", (lx + 1, ly + 1, 0.1), (cx, cy, -0.05), wood)
    kit.box("apt.wall.n", (lx + 0.8, 0.4, G.AH + 0.3), (cx, G.AY1 + 0.2, G.AH / 2 - 0.05), wall)
    kit.box("apt.wall.s", (lx + 0.8, 0.4, G.AH + 0.3), (cx, G.AY0 - 0.2, G.AH / 2 - 0.05), wall)
    kit.box("apt.wall.w", (0.4, ly + 0.8, G.AH + 0.3), (G.AX0 - 0.2, cy, G.AH / 2 - 0.05), wall)
    kit.box("apt.wall.e", (0.4, ly + 0.8, G.AH + 0.3), (G.AX1 + 0.2, cy, G.AH / 2 - 0.05), wall)
    kit.box("apt.ceiling", (lx + 1, ly + 1, 0.2), (cx, cy, G.AH + 0.1), ceil)
    # a sage wainscot band, 1.5 cm proud of the north wall, and a baseboard
    band = pl("#9fcf9a", 0.8, spec=0.03)
    kit.box("apt.band.n", (lx, 0.03, 0.9), (cx, G.AY1 - 0.015, 0.45), band)
    kit.box("apt.band.w", (0.03, ly, 0.9), (G.AX0 + 0.015, cy, 0.45), band)
    kit.box("apt.band.e", (0.03, ly, 0.9), (G.AX1 - 0.015, cy, 0.45), band)
    # the sunny window on the east wall
    win = kit.emit("#cfeaff", 1.2, "aptwin")
    fr = pl("#fffaf0", 0.6)
    kit.box("apt.win.frame", (0.05, 1.5, 1.5), (G.AX1 - 0.025, 0.4, 1.55), fr)
    ob = kit.box("apt.win.pane", (0.02, 1.34, 1.34), (G.AX1 - 0.06, 0.4, 1.55), win)
    noshadow(ob)
    for k, (dy, dz, sy, sz) in enumerate(((0, 0, 0.04, 1.34), (0, 0, 1.34, 0.04))):
        kit.box(f"apt.win.bar{k}", (0.03, sy, sz), (G.AX1 - 0.08, 0.4 + dy, 1.55 + dz), fr)
    # the ceiling lamp panel
    lamp = kit.emit("#fff4dc", 1.5, "aptlamp")
    noshadow(kit.box("apt.lamp", (1.4, 0.8, 0.02), (0.0, 1.2, G.AH - 0.01), lamp))
    # the key hooks: a wooden board, five brass hooks, other keys on three of them
    board = pl("#a8703a", 0.6)
    bx, by, bz = G.HOOK
    kit.box("apt.hookboard", (1.25, 0.05, 0.2), (bx, G.AY1 - 0.025, bz + 0.1), board, bevel=0.01)
    brass = pl("#d8a83a", 0.3, spec=0.7)
    steel = pl("#c9ced6", 0.3, spec=0.7)
    for k, x in enumerate([bx + d_ for d_ in (-0.5, -0.25, 0.0, 0.25, 0.5)]):
        kit.box(f"apt.hook{k}", (0.03, 0.09, 0.03), (x, G.AY1 - 0.09, bz + 0.07), brass)
        if k in (0, 3):
            kit.box(f"apt.otherkey{k}", (0.012, 0.045, 0.13), (x, G.AY1 - 0.13, bz - 0.0), steel)
            kit.cyl(f"apt.otherring{k}", 0.035, 0.012, (x, G.AY1 - 0.13, bz + 0.09), steel, rot=(math.pi / 2, 0, 0), n=12)
        if k == 4:
            kit.box("apt.lanyard", (0.03, 0.02, 0.28), (x, G.AY1 - 0.125, bz - 0.06), pl("#4a8fd8", 0.7))
    # the framed photo of me and Jess
    px, py, pz = G.PHOTO
    kit.box("apt.photoframe", (0.9, 0.04, 0.7), (px, G.AY1 - 0.02, pz), pl("#fff8ea", 0.5), bevel=0.01)
    m, _ = imat(kit, "photo", _photo_image(), 1.0)
    ph = kit.plane("apt.photo", (0.78, 0.585), (px, G.AY1 - 0.045, pz), m, rot=(math.pi / 2, 0, 0))
    noshadow(ph)
    # the hall table with a drawer, a plant and the phone
    table = pl("#b97f45", 0.6)
    tx, ty = G.TABLE
    kit.box("apt.table.top", (0.95, 0.5, 0.05), (tx, ty, 0.76), table, bevel=0.01)
    for sx in (-0.42, 0.42):
        for sy in (-0.2, 0.2):
            kit.box(f"apt.table.leg{sx}{sy}", (0.05, 0.05, 0.74), (tx + sx, ty + sy, 0.37), table)
    kit.prop("houseplant_1", (tx - 0.3, ty + 0.05, 0.785), scale=0.9)
    # the phone, propped up on the table, its screen toward the camera
    pm, _ = imat(kit, "phone", _phone_image(), 0.8)
    case = pl("#1c2744", 0.4, spec=0.3)
    root = kit.empty("phone", (G.PHONE[0], G.PHONE[1], G.PHONE[2]), rot=(math.radians(-62), 0, 0))
    kit.box("phone.body", (0.2, 0.012, 0.4), (0, 0, 0), case, root, bevel=0.01)
    scr = kit.plane("phone.screen", (0.18, 0.37), (0, -0.0095, 0), pm, root, rot=(math.pi / 2, 0, 0))
    noshadow(scr)
    W["phone"] = root
    # a rug, a shoe rack, a plant and a coat hook rail for the lived-in look
    kit.box("apt.rug", (2.2, 1.3, 0.02), (-0.2, 1.6, 0.01), pl("#f2c05a", 0.9, spec=0.02))
    kit.box("apt.rug.edge", (2.0, 1.1, 0.012), (-0.2, 1.6, 0.025), pl("#e8895a", 0.9, spec=0.02))
    kit.box("apt.shoes", (0.8, 0.3, 0.12), (-2.3, 3.2, 0.06), pl("#8a6a48", 0.7))
    kit.prop("houseplant_1", (-2.45, 2.5, 0), scale=2.2)
    # soft constant light: no shadow, nothing flickers
    for i, (x, y) in enumerate(((0.0, 1.0), (-1.5, -0.5), (1.5, -0.5), (0.0, 2.8))):
        a = kit.light(f"apt.fill{i}", "AREA", (x, y, G.AH - 0.15), 260, "#fff3e0", size=2.5, shadow=False)
        kit.aim(a, (x, y, 0.0))
    s = kit.light("apt.face", "AREA", (0.2, -2.0, 2.2), 240, "#fff6ec", size=2.5, shadow=False)
    kit.aim(s, (0.2, 2.5, 1.4))


# ---------------------------------------------------------------------------------------------- the hill
def build_hill(kit):
    pl = kit.plastic
    a = math.atan(G.SLOPE)
    grass = kit.texture("grass", 0.5, tint="#8fe07a")
    road = pl("#6a6e78", 0.8, spec=0.04)
    walk = pl("#e8e2d2", 0.8, spec=0.03)
    L = 42.0 / math.cos(a)
    kit.box("hill.terrain", (60, L, 0.3), (G.HX, 9.0, 0.07 * 9.0 - 0.15 / math.cos(a)), grass, rot=(a, 0, 0))
    kit.box("hill.plateau", (60, 26, 0.3), (G.HX, 43.0, G.ZH - 0.15), grass)
    kit.box("hill.road", (6.4, L, 0.1), (G.HX, 9.0, 0.07 * 9.0 - 0.05 + 0.025), road, rot=(a, 0, 0))
    for sx in (-1, 1):
        kit.box(f"hill.walk{sx}", (1.7, L, 0.12), (G.HX + sx * 4.05, 9.0, 0.07 * 9.0 - 0.06 + 0.06), walk, rot=(a, 0, 0))
        kit.box(f"hill.curb{sx}", (0.2, L, 0.18), (G.HX + sx * 3.25, 9.0, 0.07 * 9.0 + 0.02), pl("#c8c2b2", 0.8), rot=(a, 0, 0))
    # lane dashes down the middle
    dash = pl("#fff1b0", 0.7)
    for k in range(10):
        y = -6 + k * 3.8
        kit.box(f"hill.dash{k}", (0.14, 1.6, 0.02), (G.HX, y, 0.07 * y + 0.045), dash, rot=(a, 0, 0))
    # the path and the front lawn to the porch steps
    kit.box("hill.path", (1.8, 3.4, 0.05), (G.HX, 31.2, G.ZH + 0.025), walk)
    # painted houses on both sides, fronts to the street
    cols = ["#ffc9a8", "#ffe39a", "#b8e6b0", "#f2b8d8", "#c8d8ff", "#ffd0a0"]
    houses = [("sub_building_type_a", 5.0), ("sub_building_type_f", 13.0), ("sub_building_type_p", 21.5),
              ("sub_building_type_f", 29.0)]
    for i, (name, y) in enumerate(houses):
        for sx in (-1, 1):
            z = 0.07 * min(y, 30)
            nm = name if (i + (sx > 0)) % 2 == 0 else ("sub_building_type_p" if name != "sub_building_type_p" else "sub_building_type_a")
            kit.prop(nm, (G.HX + sx * 11.0, y, z), rot=-90 * sx, tint=cols[(i * 2 + (sx > 0)) % len(cols)])
            kit.prop("sub_fence_low", (G.HX + sx * 6.2, y, z), rot=90)
    for y in (2.0, 9.0, 17.0, 25.0):
        for sx in (-1, 1):
            kit.prop("commontree_1", (G.HX + sx * 6.0, y, 0.07 * y), rot=40 * y, scale=0.9)
    for sx in (-1, 1):
        for y in (-8.0, -12.0):
            kit.prop("commontree_2", (G.HX + sx * 7.0, y, 0.07 * y), rot=33 * y, scale=1.2)
    kit.box("hill.far", (80, 4, 8), (G.HX, -22, 2.5), pl("#9fd29a", 0.9, spec=0.01))
    kit.box("hill.far2", (80, 4, 12), (G.HX, -30, 4.5), pl("#b8d8e8", 0.9, spec=0.01))
    # the sun, gold in the late afternoon, and a soft sky fill
    sun = kit.light("sun", "SUN", (G.HX - 14, 8, 22), 2.6, "#ffd89a", size=0.06)
    sun.data.angle = 0.06
    kit.aim(sun, (G.HX + 0.5, 35, 2.0))
    W["sun"] = sun


# ---------------------------------------------------------------------------------------------- the old blue house
def build_house(kit):
    pl = kit.plastic
    HXc, HY = G.HOUSE
    ZP = G.ZP
    blue = pl("#4a8fd8", 0.7, spec=0.04)
    white = pl("#c9c4b4", 0.7, spec=0.04)           # graded under 70% by the light: never a clipped wall
    trim = pl("#dedacb", 0.7, spec=0.04)
    warm = kit.emit("#ffd58a", 1.6, "warmpane")
    x0, x1, y1 = 56.0, 64.0, 41.8
    H = 5.4
    dx0, dx1 = HXc - G.DOOR_W / 2, HXc + G.DOOR_W / 2
    zb = G.ZH - 0.2
    # shell: front wall in pieces around the door, sides, back
    kit.box("h.front.l", (dx0 - x0, 0.3, H + 0.2), ((x0 + dx0) / 2, HY + 0.15, zb + (H + 0.2) / 2), blue)
    kit.box("h.front.r", (x1 - dx1, 0.3, H + 0.2), ((x1 + dx1) / 2, HY + 0.15, zb + (H + 0.2) / 2), blue)
    top = H - (ZP - zb) - G.DOOR_H
    kit.box("h.front.top", (G.DOOR_W, 0.3, top), (HXc, HY + 0.15, ZP + G.DOOR_H + top / 2), blue)
    kit.box("h.side.w", (0.3, y1 - HY, H + 0.2), (x0 + 0.15, (HY + y1) / 2, zb + (H + 0.2) / 2), blue)
    kit.box("h.side.e", (0.3, y1 - HY, H + 0.2), (x1 - 0.15, (HY + y1) / 2, zb + (H + 0.2) / 2), blue)
    kit.box("h.back", (x1 - x0, 0.3, H + 0.2), (HXc, y1 - 0.15, zb + (H + 0.2) / 2), blue)
    # white corner boards, a belt line and the roof
    for sx in (x0, x1):
        kit.box(f"h.corner{sx}", (0.22, 0.22, H + 0.2), (sx, HY - 0.02, zb + (H + 0.2) / 2), trim)
    kit.box("h.belt", (x1 - x0, 0.08, 0.16), (HXc, HY - 0.04, ZP + 2.9), trim)
    ridge = ZP + 7.3
    eave = zb + H + 0.2
    ry0, ry1 = HY - 0.7, y1 + 0.5
    rv = [(x0 - 0.4, ry0, eave), (x1 + 0.4, ry0, eave), (x1 + 0.4, ry1, eave), (x0 - 0.4, ry1, eave)]
    rm = pl("#a85a48", 0.8, spec=0.03)
    # a roof as a hip-less gable: ridge runs east-west; front and back slabs
    mid = (ry0 + ry1) / 2
    rh = ridge - eave
    half = (ry1 - ry0) / 2
    verts = [(x0 - 0.4, ry0, eave), (x1 + 0.4, ry0, eave), (x1 + 0.4, mid, ridge), (x0 - 0.4, mid, ridge),
             (x0 - 0.4, ry1, eave), (x1 + 0.4, ry1, eave)]
    faces = [(0, 1, 2, 3), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2), (0, 4, 5, 1)]
    ob = kit.mesh_obj("h.roof", verts, faces, rm)
    # windows: ground floor pair and three upstairs
    def window(name, wx, wz, w=1.1, h=1.2):
        kit.box(f"{name}.frame", (w + 0.24, 0.05, h + 0.24), (wx, HY - 0.025, wz), trim)
        p = kit.box(f"{name}.pane", (w, 0.02, h), (wx, HY - 0.06, wz), warm)
        noshadow(p)
        kit.box(f"{name}.barv", (0.05, 0.03, h), (wx, HY - 0.075, wz), trim)
        kit.box(f"{name}.barh", (w, 0.03, 0.05), (wx, HY - 0.075, wz), trim)
        kit.box(f"{name}.sill", (w + 0.4, 0.14, 0.06), (wx, HY - 0.07, wz - h / 2 - 0.15), trim)
    window("h.win.gl", HXc - 2.7, ZP + 1.5)
    window("h.win.gr", HXc + 2.7, ZP + 1.5)
    window("h.win.ul", HXc - 2.7, ZP + 3.9)
    window("h.win.uc", HXc, ZP + 3.9)
    window("h.win.ur", HXc + 2.7, ZP + 3.9)
    # the curtain in the upstairs middle window: two panels that sway
    cur = pl("#e0685a", 0.9)
    W["curtain"] = [kit.box(f"h.curtain{s}", (0.42, 0.03, 1.2), (HXc + s * 0.34, HY - 0.095, ZP + 3.9), cur) for s in (-1, 1)]
    # porch: platform, two steps, posts, roof, rails
    wood = kit.texture("wood", 0.8, tint="#d9c9a8")
    kit.box("p.floor", (5.6, 2.7, 0.45), (HXc, HY - 1.35, G.ZH + 0.225), wood)
    kit.box("p.step2", (2.6, 0.4, 0.3), (HXc, HY - 2.9, G.ZH + 0.15), wood)
    kit.box("p.step1", (2.6, 0.4, 0.15), (HXc, HY - 3.3, G.ZH + 0.075), wood)
    for sx in (-2.7, 2.7):
        kit.box(f"p.post{sx}", (0.2, 0.2, 2.75), (HXc + sx, HY - 2.55, ZP + 1.375), white, bevel=0.02)
    kit.box("p.roof", (6.2, 3.8, 0.16), (HXc, HY - 1.5, ZP + 2.83), white, bevel=0.02)
    kit.box("p.fascia", (6.2, 0.08, 0.3), (HXc, HY - 3.42, ZP + 2.72), trim)
    for sx in (-1, 1):
        kit.box(f"p.rail{sx}", (0.1, 2.5, 0.08), (HXc + sx * 2.7, HY - 1.3, ZP + 0.9), white)
        for k in range(5):
            kit.box(f"p.bal{sx}{k}", (0.06, 0.06, 0.85), (HXc + sx * 2.7, HY - 2.4 + k * 0.5, ZP + 0.46), white)
        for xx in (1.45, 2.0):
            pass
        kit.box(f"p.railf{sx}", (1.5, 0.1, 0.08), (HXc + sx * 1.95, HY - 2.55, ZP + 0.9), white)
    # lanterns beside the door, lit
    lant = kit.emit("#ffe3a0", 4.0, "lantern")
    for sx in (-1, 1):
        noshadow(kit.box(f"p.lantern{sx}", (0.16, 0.16, 0.3), (HXc + sx * 1.05, HY - 0.16, ZP + 1.95), lant, bevel=0.03))
        kit.box(f"p.lantern.cap{sx}", (0.2, 0.2, 0.05), (HXc + sx * 1.05, HY - 0.16, ZP + 2.12), pl("#3a3a42", 0.5))
    # the door: a pivot at the west hinge; the door is its child; the sticker rides on the door
    pv = kit.empty("h.doorpivot", (G.DOOR_X0, HY + 0.15, ZP))
    dm = pl("#d4cebd", 0.6, spec=0.06)
    kit.box("h.door", (G.DOOR_W, 0.07, G.DOOR_H), (G.DOOR_W / 2, 0.0, G.DOOR_H / 2), dm, pv, bevel=0.01)
    for k, (zz, hh) in enumerate(((0.45, 0.8), (1.55, 0.8))):
        kit.box(f"h.door.panel{k}", (0.8, 0.02, hh), (G.DOOR_W / 2, -0.045, zz + hh / 2 + 0.0), pl("#c2bcab", 0.6), pv)
    kit.cyl("h.knob", 0.05, 0.05, (G.DOOR_W - 0.14, -0.07, 1.05), pl("#d8a83a", 0.3, spec=0.7), pv, rot=(math.pi / 2, 0, 0), n=14)
    sm, _ = imat(kit, "sticker", _dino_image(), 1.0)
    st = kit.plane("h.sticker", (0.34, 0.34), (G.DOOR_W / 2 + 0.12, -0.05, 1.3 - 0.0), sm, pv, rot=(math.pi / 2, 0, 0))
    noshadow(st)
    W["doorpivot"], W["sticker"] = pv, st
    kit.box("h.jamb.l", (0.1, 0.2, G.DOOR_H + 0.1), (dx0 - 0.05, HY - 0.0, ZP + G.DOOR_H / 2 + 0.05), trim)
    kit.box("h.jamb.r", (0.1, 0.2, G.DOOR_H + 0.1), (dx1 + 0.05, HY - 0.0, ZP + G.DOOR_H / 2 + 0.05), trim)
    kit.box("h.jamb.t", (G.DOOR_W + 0.2, 0.2, 0.1), (HXc, HY - 0.0, ZP + G.DOOR_H + 0.05), trim)
    # the stranger's bike on the porch (plain, no marks)
    bm = pl("#e84a4a", 0.5)
    tire = pl("#2a2a30", 0.8)
    bx, by = HXc - 1.9, HY - 1.2
    for dy in (-0.45, 0.45):
        kit.cyl(f"bike.w{dy}", 0.3, 0.05, (bx, by + dy, ZP + 0.3), tire, rot=(0, math.pi / 2, 0), n=18)
    kit.box("bike.frame", (0.05, 0.9, 0.05), (bx, by, ZP + 0.45), bm, rot=(0.0, 0, 0))
    kit.box("bike.bar", (0.5, 0.05, 0.05), (bx, by + 0.42, ZP + 0.85), bm)
    kit.box("bike.post", (0.05, 0.05, 0.5), (bx, by + 0.42, ZP + 0.6), bm)
    # --- the hall: warm cream walls, wood floor, ceiling, stairs, the cake, streamers
    x0h, x1h, y0h, y1h = G.HALL
    cream = pl("#f6dcb0", 0.85, spec=0.03)
    kit.box("hall.floor", (x1h - x0h, y1h - y0h, 0.1), ((x0h + x1h) / 2, (y0h + y1h) / 2, ZP - 0.05),
            kit.texture("wood", 0.8, tint="#e8c48a"))
    kit.box("hall.ceil", (x1h - x0h, y1h - y0h, 0.25), ((x0h + x1h) / 2, (y0h + y1h) / 2, ZP + G.HALL_H + 0.125), kit.emit("#ffeed0", 1.6, "hallceil"))
    kit.box("hall.wall.back", (x1h - x0h, 0.04, G.HALL_H), (HXc, y1h - 0.02, ZP + G.HALL_H / 2), cream)
    kit.box("hall.wall.w", (0.04, y1h - y0h, G.HALL_H), (x0h + 0.02, (y0h + y1h) / 2, ZP + G.HALL_H / 2), cream)
    kit.box("hall.wall.e", (0.04, y1h - y0h, G.HALL_H), (x1h - 0.02, (y0h + y1h) / 2, ZP + G.HALL_H / 2), cream)
    # the inside of the front wall, with the door gap cut out
    kit.box("hall.wall.front.l", (dx0 - x0h, 0.04, G.HALL_H), ((x0h + dx0) / 2, y0h + 0.02, ZP + G.HALL_H / 2), cream)
    kit.box("hall.wall.front.r", (x1h - dx1, 0.04, G.HALL_H), ((x1h + dx1) / 2, y0h + 0.02, ZP + G.HALL_H / 2), cream)
    kit.box("hall.wall.front.t", (G.DOOR_W, 0.04, G.HALL_H - G.DOOR_H), (HXc, y0h + 0.02, ZP + G.DOOR_H + (G.HALL_H - G.DOOR_H) / 2), cream)
    kit.box("hall.rug", (2.6, 3.4, 0.02), (HXc, 38.7, ZP + 0.01), pl("#e8695a", 0.9, spec=0.02))
    kit.box("hall.rug.in", (2.2, 3.0, 0.012), (HXc, 38.7, ZP + 0.025), pl("#f2c05a", 0.9, spec=0.02))
    # wainscot
    kit.box("hall.wain.back", (x1h - x0h, 0.03, 0.9), (HXc, y1h - 0.055, ZP + 0.45), pl("#9fcf9a", 0.8, spec=0.03))
    kit.box("hall.wain.w", (0.03, y1h - y0h, 0.9), (x0h + 0.055, (y0h + y1h) / 2, ZP + 0.45), pl("#9fcf9a", 0.8, spec=0.03))
    # stairs along the east wall, rising north
    sw = pl("#c58a50", 0.6)
    for k in range(9):
        y = 38.2 + k * 0.36
        kit.box(f"hall.stair{k}", (1.4, 0.36, 0.2 * (k + 1)), (x1h - 0.74, y + 0.18, ZP + 0.1 * (k + 1)), sw)
    kit.box("hall.rail", (0.08, 3.4, 0.08), (x1h - 1.5, 39.9, ZP + 1.1), pl("#8a5a2a", 0.6), rot=(0.55, 0, 0))
    # the side table with a cake (no lettering), against the back wall
    table = pl("#b97f45", 0.6)
    kit.box("hall.table.top", (1.2, 0.6, 0.06), (HXc + 0.1, 41.0, ZP + 1.0), table, bevel=0.01)
    for sx in (-0.5, 0.5):
        for sy in (-0.2, 0.2):
            kit.box(f"hall.table.leg{sx}{sy}", (0.06, 0.06, 1.0), (HXc + 0.1 + sx, 41.0 + sy, ZP + 0.5), table)
    cakey = pl("#fff0f0", 0.6)
    kit.cyl("cake.l1", 0.32, 0.18, (HXc + 0.1, 41.0, ZP + 1.12), pl("#f8c8d8", 0.6), n=24)
    kit.cyl("cake.l2", 0.22, 0.16, (HXc + 0.1, 41.0, ZP + 1.3), cakey, n=24)
    for k in range(5):
        ang = k * 2 * math.pi / 5
        kit.box(f"cake.candle{k}", (0.025, 0.025, 0.12), (HXc + 0.1 + 0.12 * math.cos(ang), 41.0 + 0.12 * math.sin(ang), ZP + 1.44),
                pl(["#ff6a6a", "#6a9aff", "#ffd84a", "#6adf8a", "#d98aff"][k], 0.5))
        noshadow(kit.sphere(f"cake.flame{k}", 0.02, (HXc + 0.1 + 0.12 * math.cos(ang), 41.0 + 0.12 * math.sin(ang), ZP + 1.52),
                            kit.emit(ORANGE, 3.0, "flame")))
    # a plant, a coat rack by the door, a picture frame or two (plain colour fields)
    kit.prop("houseplant_1", (x0h + 0.6, 40.8, ZP), scale=2.6)
    kit.prop("light_floor1", (x0h + 0.5, 38.4, ZP), height=1.5)
    for k, c in enumerate(("#8ad0ff", "#ffb08a", "#b8e6a0")):
        kit.box(f"hall.pic{k}", (0.04, 0.7, 0.55), (x0h + 0.07, 38.0 + k * 1.1, ZP + 1.5), pl(c, 0.6))
        kit.box(f"hall.picframe{k}", (0.03, 0.8, 0.65), (x0h + 0.055, 38.0 + k * 1.1, ZP + 1.5), pl("#fff8ea", 0.6))
    # streamers: coloured ribbons draped across the ceiling, plus balloons in the back corners
    cols = ["#ff6a6a", "#ffd84a", "#6adf8a", "#6a9aff", "#d98aff"]
    for k, c in enumerate(cols):
        zz = ZP + G.HALL_H - 0.12 - 0.04 * (k % 2)
        kit.box(f"streamer{k}", (x1h - x0h - 0.4, 0.07, 0.04), (HXc, 37.3 + k * 0.9, zz), pl(c, 0.7), rot=(0, 0.04 * (k % 3 - 1), 0))
        for j in range(4):
            kit.box(f"streamer{k}.t{j}", (0.07, 0.07, 0.3 + 0.05 * (j % 2)), (x0h + 0.9 + j * 1.7, 37.3 + k * 0.9, zz - 0.17), pl(c, 0.7))
    for k, (bx2, by2, c) in enumerate(((x0h + 0.5, 41.0, "#ff6a6a"), (x0h + 0.9, 41.1, "#ffd84a"), (x1h - 0.5, 41.0, "#6a9aff"))):
        kit.sphere(f"balloon{k}", 0.24, (bx2, by2, ZP + 2.0), pl(c, 0.3, spec=0.6))
    # the hook by the door, inside, where the key finally hangs
    hb = pl("#a8703a", 0.6)
    hxp = HXc + 1.45
    kit.box("hall.hookboard", (0.5, 0.05, 0.2), (hxp, y0h + 0.065, ZP + 1.4), hb, bevel=0.01)
    kit.box("hall.hook", (0.03, 0.1, 0.03), (hxp, y0h + 0.14, ZP + 1.45), pl("#d8a83a", 0.3, spec=0.7))
    W["hook2"] = (hxp, y0h + 0.16, ZP + 1.45)
    # lights: warm ceiling fills inside, fill at the door, golden porch fill
    for i, (x, y) in enumerate(((HXc - 1.8, 37.8), (HXc + 1.8, 37.8), (HXc - 1.5, 40.0), (HXc + 1.0, 40.0), (HXc, 38.8))):
        a = kit.light(f"hall.fill{i}", "AREA", (x, y, ZP + G.HALL_H - 0.15), 380, "#ffe2b0", size=2.5, shadow=False)
        kit.aim(a, (x, y, ZP))
    lamp = kit.emit("#fff0cc", 2.5, "halllamp")
    for i, (x, y) in enumerate(((HXc - 1.8, 37.8), (HXc + 1.8, 37.8), (HXc - 1.0, 40.2), (HXc + 1.0, 40.2))):
        noshadow(kit.box(f"hall.lamp{i}", (0.7, 0.5, 0.02), (x, y, ZP + G.HALL_H - 0.012), lamp))
    fd = kit.light("hall.door", "AREA", (HXc, 36.8, ZP + 2.0), 330, "#ffe8c0", size=2.5, shadow=False)
    kit.aim(fd, (HXc, 39.5, ZP + 1.0))
    # porch fill: gold light under the roof so the porch faces read; and a soft face light toward the steps
    pf = kit.light("porch.fill", "AREA", (HXc, HY - 3.6, ZP + 2.3), 520, "#ffe0a8", size=3.5, shadow=False)
    kit.aim(pf, (HXc, HY - 0.8, ZP + 1.0))
    pf2 = kit.light("porch.door", "AREA", (HXc - 1.2, HY - 2.4, ZP + 2.5), 320, "#ffe6bc", size=3.0, shadow=False)
    kit.aim(pf2, (HXc + 0.3, HY - 0.1, ZP + 1.2))
    # a gold kicker on the lawn and the facade from the south
    lw = kit.light("lawn.fill", "AREA", (HXc, 24.0, G.ZH + 4.0), 1800, "#fff0d0", size=8.0, shadow=False)
    kit.aim(lw, (HXc, 36.0, G.ZH + 2.0))


# ---------------------------------------------------------------------------------------------- montage and insert stages
def build_pizza(kit):
    pl = kit.plastic
    px, py = G.PIZZA
    kit.box("pz.ground", (14, 12, 0.2), (px, py - 4, -0.1), kit.texture("grass", 0.5, tint="#9fe08a"))
    kit.box("pz.stoop", (3.4, 2.0, 0.12), (px, py - 1.0, 0.06), pl("#e8e2d2", 0.8))
    kit.box("pz.wall", (8, 0.3, 3.6), (px, py + 0.15, 1.8), pl("#f2b8d8", 0.7, spec=0.04))
    kit.box("pz.wall.l", (0.3, 5, 3.6), (px - 4.0, py - 2.4, 1.8), pl("#f2b8d8", 0.7, spec=0.04))
    kit.box("pz.wall.r", (0.3, 5, 3.6), (px + 4.0, py - 2.4, 1.8), pl("#f2b8d8", 0.7, spec=0.04))
    kit.box("pz.roof", (8.4, 5.6, 0.3), (px, py - 2.4, 3.75), pl("#a85a48", 0.8))
    kit.box("pz.door", (1.1, 0.06, 2.1), (px, py - 0.04, 1.11), pl("#2fb5a8", 0.6, spec=0.06), bevel=0.01)
    kit.box("pz.door.frame", (1.4, 0.04, 2.35), (px, py - 0.015, 1.18), pl("#fffaf0", 0.6))
    kit.cyl("pz.knob", 0.05, 0.05, (px + 0.38, py - 0.09, 1.05), pl("#d8a83a", 0.3, spec=0.7), rot=(math.pi / 2, 0, 0), n=14)
    for sx in (-1, 1):
        kit.box(f"pz.win{sx}", (1.2, 0.04, 1.2), (px + sx * 2.6, py - 0.02, 1.7), pl("#fffaf0", 0.6))
        noshadow(kit.box(f"pz.pane{sx}", (1.0, 0.02, 1.0), (px + sx * 2.6, py - 0.05, 1.7), kit.emit("#ffe3a0", 1.4, "pzpane")))
    kit.prop("bush_1", (px - 3.2, py - 1.0, 0), scale=0.5)
    # pizza boxes on his flat palms (shown by the `boxes` cue), a glowing key ring on his belt
    box_m = pl("#e8c88a", 0.8)
    stripe = pl("#d8322f", 0.6)
    W["boxes"] = []
    for sx in (-1, 1):
        root = kit.empty(f"pz.boxes{sx}", (0, 0, -30))
        for k in range(3):
            kit.box(f"pz.box{sx}{k}", (0.44, 0.44, 0.07), (0, 0, k * 0.075), box_m, root, bevel=0.01)
            kit.box(f"pz.boxs{sx}{k}", (0.12, 0.45, 0.075), (0, 0, k * 0.075), stripe, root)
        W["boxes"].append((root, sx))
    gm = kit.emit(ORANGE, 5.0, "pzglow")
    W["pzkeys"] = []
    kit.cyl("pz.belt.ring", 0.05, 0.015, (px + 0.4, 2.55, 0.92), pl("#c9ced6", 0.3, spec=0.7), rot=(math.pi / 2, 0, 0), n=14)
    kit.box("pz.belt.key", (0.03, 0.012, 0.16), (px + 0.4, 2.52, 0.8), pl("#d8a83a", 0.3, spec=0.7))
    noshadow(kit.sphere("pz.belt.glow", 0.075, (px + 0.4, 2.5, 0.82), gm))
    for i, (x, y) in enumerate(((px, py - 1.5), (px - 2.5, py - 3.0), (px + 2.5, py - 3.0))):
        a = kit.light(f"pz.fill{i}", "AREA", (x, y, 3.4), 520, "#fff3e0", size=3.0, shadow=False)
        kit.aim(a, (x, y, 0))
    f = kit.light("pz.face", "AREA", (px, py - 6.0, 2.4), 520, "#fff6ec", size=3.0, shadow=False)
    kit.aim(f, (px, py - 1.5, 1.3))


def build_gym(kit):
    pl = kit.plastic
    bx, by = G.BUDDY
    kit.box("gy.floor", (9, 9, 0.2), (bx, by - 4.0, -0.1), pl("#e8e0c8", 0.6, spec=0.08))
    kit.box("gy.wall.n", (9, 0.3, 3.3), (bx, by + 0.15, 1.65), pl("#cfe4f2", 0.8))
    kit.box("gy.wall.l", (0.3, 8, 3.3), (bx - 4.2, by - 4.0, 1.65), pl("#cfe4f2", 0.8))
    kit.box("gy.wall.r", (0.3, 8, 3.3), (bx + 4.2, by - 4.0, 1.65), pl("#cfe4f2", 0.8))
    kit.box("gy.ceil", (9, 9, 0.2), (bx, by - 4.0, 3.4), kit.emit("#fff6e4", 0.7, "gyceil"))
    kit.box("gy.wall.s", (9, 0.3, 3.3), (bx, by - 8.2, 1.65), pl("#cfe4f2", 0.8))
    cols = ["#5b8fb9", "#6fb06a", "#5b8fb9", "#d98a4a"]
    for k in range(14):
        lx = bx - 3.25 + k * 0.5
        kit.box(f"gy.locker{k}", (0.48, 0.45, 2.0), (lx, by - 0.225, 1.0), pl(cols[k % 4], 0.5, spec=0.12), bevel=0.01)
        kit.box(f"gy.vent{k}", (0.3, 0.02, 0.05), (lx, by - 0.46, 1.75), pl("#2a2a30", 0.6))
        kit.box(f"gy.handle{k}", (0.04, 0.04, 0.16), (lx + 0.14, by - 0.47, 1.28), pl("#c9ced6", 0.3, spec=0.7))
    kit.box("gy.bench", (0.4, 3.0, 0.45), (bx + 2.5, by - 3.0, 0.22), pl("#b97f45", 0.6))
    # the buddy's locker key: plain, gray, on a gray band, in the lock of the locker at x = bx
    gray = pl("#9a9fa8", 0.4, spec=0.5)
    kit.cyl("gy.lockplate", 0.06, 0.02, (bx - 0.25, by - 0.47, 1.4), pl("#c9ced6", 0.3, spec=0.7), rot=(math.pi / 2, 0, 0), n=16)
    kit.cyl("gy.keybow", 0.08, 0.02, (bx - 0.25, by - 0.56, 1.36), gray, rot=(math.pi / 2, 0, 0), n=16)
    kit.box("gy.keyshaft", (0.05, 0.02, 0.22), (bx - 0.25, by - 0.56, 1.2), gray)
    kit.box("gy.keyband", (0.02, 0.012, 0.3), (bx - 0.19, by - 0.575, 1.18), pl("#4a8fd8", 0.7))
    for i, (x, y) in enumerate(((bx - 1.5, by - 2.0), (bx + 1.5, by - 2.0), (bx, by - 4.5))):
        a = kit.light(f"gy.fill{i}", "AREA", (x, y, 3.2), 420, "#fff6ec", size=3.0, shadow=False)
        kit.aim(a, (x, y, 0))
    f = kit.light("gy.face", "AREA", (bx, by - 6.5, 2.3), 520, "#fff6ec", size=3.0, shadow=False)
    kit.aim(f, (bx, by - 1.5, 1.3))


def build_insert(kit):
    """The old front door close-up: a blue wall, a white door with a brass lock, a white jamb on the latch side
    carrying four pencil strokes (the height marks of the four of us who lived here), and a ceiling above."""
    pl = kit.plastic
    ix, iy = G.INS
    kit.box("in.floor", (8, 6, 0.2), (ix, iy - 3.0, -0.1), pl("#c9b48a", 0.7))
    kit.box("in.wall", (7, 0.3, 4.2), (ix, iy + 0.15, 2.1), pl("#4a8fd8", 0.7, spec=0.04))
    kit.box("in.ceil", (7, 4, 0.2), (ix, iy - 2.0, 3.3), kit.emit("#fff1dc", 0.7, "inceil"))
    kit.box("in.wall.l", (0.3, 4, 3.4), (ix - 3.5, iy - 2.0, 1.7), pl("#4a8fd8", 0.7))
    kit.box("in.door", (1.3, 0.07, 2.15), (ix, iy - 0.04, 1.1), pl("#d4cebd", 0.6, spec=0.06), bevel=0.01)
    for k, (zz, hh) in enumerate(((0.45, 0.8), (1.55, 0.8))):
        kit.box(f"in.door.panel{k}", (0.8, 0.02, hh), (ix, iy - 0.085, zz + hh / 2), pl("#c2bcab", 0.6))
    trim = pl("#ddd8c9", 0.7)
    for k, sx in enumerate((-1, 1)):
        kit.box(f"in.jamb{k}", (0.14, 0.06, 2.3), (ix + sx * 0.72, iy - 0.03, 1.15), trim)
    kit.box("in.jamb.t", (1.58, 0.06, 0.14), (ix, iy - 0.03, 2.2), trim)
    # four pencil strokes on the east jamb at chest height, one stroke each (1.1 cm proud of the trim)
    pencil = pl("#555a62", 0.9, spec=0.02)
    for k, dz in enumerate((-0.08, 0.0, 0.08, 0.16)):
        kit.box(f"in.tally{k}", (0.075, 0.02, 0.012), (ix + 0.72, iy - 0.07, 1.04 + dz + k * 0.0), pencil)
    # the lock: a brass plate, a keyhole and a deadbolt knob, on the door's east edge
    brass = pl("#d8a83a", 0.3, spec=0.7)
    lx, lz = ix + 0.42, 1.3
    kit.cyl("in.lockplate", 0.085, 0.03, (lx, iy - 0.09, lz), brass, rot=(math.pi / 2, 0, 0), n=20)
    kit.cyl("in.lockface", 0.05, 0.03, (lx, iy - 0.1, lz), pl("#b8861c", 0.35, spec=0.7), rot=(math.pi / 2, 0, 0), n=20)
    kit.cyl("in.lockhole", 0.016, 0.034, (lx, iy - 0.11, lz), pl("#201c18", 0.7), rot=(math.pi / 2, 0, 0), n=10)
    kit.cyl("in.knob", 0.05, 0.06, (lx, iy - 0.1, lz + 0.3), brass, rot=(math.pi / 2, 0, 0), n=16)
    W["lock"] = (lx, iy - 0.115, lz)
    for i, (x, y) in enumerate(((ix, iy - 1.5), (ix + 1.5, iy - 2.5), (ix - 1.5, iy - 2.5))):
        a = kit.light(f"in.fill{i}", "AREA", (x, y, 3.0), 60, "#fff3e0", size=2.5, shadow=False)
        kit.aim(a, (ix, iy, 1.3))
    f = kit.light("in.face", "AREA", (ix + 0.6, iy - 2.2, 1.9), 70, "#ffe6bc", size=1.5, shadow=False)
    kit.aim(f, (ix + 0.3, iy, 1.3))


# ---------------------------------------------------------------------------------------------- the key and its dinosaur
def build_key(kit):
    pl = kit.plastic
    brass = pl("#d8a83a", 0.3, spec=0.7)
    dark = pl("#2a2a30", 0.7)
    steel = pl("#c9ced6", 0.3, spec=0.7)
    W["glowmat"] = kit.emit(ORANGE, 2.0, "keyglow")
    key = kit.empty("key", (0, 0, -40))
    kit.cyl("key.bow", 0.062, 0.025, (0, 0, -0.065), brass, key, rot=(0, math.pi / 2, 0), n=20)
    kit.cyl("key.hole", 0.026, 0.05, (0, 0, -0.065), dark, key, rot=(0, math.pi / 2, 0), n=14)
    kit.box("key.shaft", (0.022, 0.034, 0.19), (0, 0, -0.225), brass, key, bevel=0.005)
    kit.box("key.tooth1", (0.022, 0.07, 0.04), (0, 0.045, -0.29), brass, key)
    kit.box("key.tooth2", (0.022, 0.055, 0.032), (0, 0.04, -0.235), brass, key)
    g = kit.sphere("key.glow", 0.05, (0, 0.03, -0.3), W["glowmat"], key)
    noshadow(g)
    W["key"], W["glow"] = key, g
    for ob in [key] + list(key.children):
        ob.scale = (KS, KS, KS) if ob is key else ob.scale
    # the ring: 14 small blocks round a circle in the y-z plane
    ring = kit.empty("keyring", (0, 0, -40))
    for k in range(14):
        a = 2 * math.pi * k / 14
        kit.box(f"keyring.{k}", (0.016, 0.052, 0.016), (0, 0.085 * math.cos(a), 0.085 * math.sin(a)), steel, ring, rot=(a + math.pi / 2, 0, 0))
    W["ring"] = ring
    # the green dinosaur on a short chain: the pivot sits at its attach point, the body hangs under it
    green, dg = pl("#4ccf5a", 0.5), pl("#2f9a3e", 0.5)
    dp = kit.empty("dino.pivot", (0, 0, -40))
    d = kit.empty("dino", (0, 0, -0.2 * DS), dp)
    d.scale = (DS, DS, DS)

    def b(n, size, loc, mat=green, rot=(0, 0, 0)):
        return kit.box(f"dino.{n}", size, loc, mat, d, rot=rot, bevel=0.006)
    b("body", (0.03, 0.17, 0.09), (0, 0, 0.095))
    for k, y in enumerate((-0.065, -0.02, 0.035, 0.075)):
        b(f"leg{k}", (0.03, 0.036, 0.055), (0, y, 0.027))
    b("neck", (0.03, 0.05, 0.1), (0, 0.085, 0.17))
    b("head", (0.03, 0.085, 0.055), (0, 0.115, 0.235))
    b("tail", (0.03, 0.1, 0.045), (0, -0.13, 0.085))
    b("tail2", (0.03, 0.06, 0.025), (0, -0.2, 0.075))
    for k, (y, z) in enumerate(((-0.06, 0.165), (-0.02, 0.175), (0.02, 0.175), (0.06, 0.165))):
        b(f"plate{k}", (0.038, 0.045, 0.045), (0, y, z), dg, rot=(math.pi / 4, 0, 0))
    b("eye", (0.036, 0.016, 0.016), (0, 0.135, 0.245), dark)
    chain = kit.box("dino.chain", (0.012, 0.012, 0.09), (0, 0, 0.0), steel, dp)
    W["dino"], W["dinopivot"], W["chain"] = d, dp, chain
    chain.location = (0, 0, 0.045)


def build_mitt(kit):
    pl = kit.plastic
    red = pl("#e8572a", 0.6)
    rt = pl("#fff0d0", 0.6)
    root = kit.empty("mitt", (0, 0, -40))
    kit.box("mitt.body", (0.3, 0.34, 0.24), (0, 0, 0.0), red, root, bevel=0.05)
    kit.box("mitt.thumb", (0.14, 0.12, 0.16), (0, 0.2, 0.02), red, root, bevel=0.04)
    kit.box("mitt.band", (0.32, 0.36, 0.05), (0, 0, -0.08), rt, root, bevel=0.01)
    kit.box("mitt.dot", (0.31, 0.1, 0.1), (0, 0, 0.03), rt, root, bevel=0.03)
    W["mitt"] = root


def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    m, tex = imat(kit, "tag", _tag_image(1), 1.0)
    pl = kit.plane("tag.plane", (1.0, 0.75), (0, 0, 0), m, root)
    noshadow(pl)
    W["tagtex"] = tex
    W["tagimgs"] = {}
    W["tagn"] = 1


# ---------------------------------------------------------------------------------------------- build / animate
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    build_apt(kit)
    build_hill(kit)
    build_house(kit)
    build_pizza(kit)
    build_gym(kit)
    build_insert(kit)
    build_key(kit)
    build_mitt(kit)
    build_tag(kit)
    W["extras_done"] = False
    for nm, d in kit.LIGHTS.items():      # one global trim, so the bright grade never clips the sets
        f = 0.55 if nm == "sun" else 0.28
        d["light"].energy *= f
        d["base"] = d["light"].energy
    return {}


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


def hand(who, sx):
    ob = bpy.data.objects.get(f"{who}.arm{sx}")
    if ob is None:
        return None
    return ob.matrix_world @ Vector((0, 0, -1.55))


def attach_extras(kit):
    """Heads wear the extras (idempotent): Dad's gray beard, Jess's ponytail and earrings."""
    pl = kit.plastic
    if W.get("extras_done"):
        return
    dh, jh = bpy.data.objects.get("dad.headg"), bpy.data.objects.get("jess.headg")
    if dh is None or jh is None:
        return
    gray = pl("#b4b4bc", 0.8)
    kit.box("dad.chin", (0.62, 0.16, 0.26), (0, -0.55, -0.5), gray, dh, bevel=0.06)
    for sx in (-1, 1):
        kit.box(f"dad.cheek{sx}", (0.2, 0.3, 0.4), (sx * 0.4, -0.45, -0.34), gray, dh, rot=(0, 0, sx * 0.55), bevel=0.05)
        kit.box(f"dad.stache{sx}", (0.3, 0.09, 0.1), (sx * 0.17, -0.64, -0.2), gray, dh, rot=(0, sx * 0.3, 0), bevel=0.03)
    hair = pl("#15151a", 0.65)
    kit.box("jess.tie", (0.2, 0.2, 0.12), (0, 0.66, 0.2), pl("#d8322f", 0.6), jh, bevel=0.04)
    kit.box("jess.tail1", (0.26, 0.24, 0.6), (0, 0.8, 0.0), hair, jh, bevel=0.08)
    kit.box("jess.tail2", (0.22, 0.2, 0.5), (0, 0.84, -0.5), hair, jh, bevel=0.08)
    gold = pl("#f2c230", 0.3, spec=0.7)
    for sx in (-1, 1):
        kit.cyl(f"jess.ear{sx}", 0.1, 0.05, (sx * 0.6, -0.12, -0.3), gold, jh, rot=(0, math.pi / 2, 0), n=14)
    W["extras_done"] = True


def animate(kit, story, tl, t, ctx):
    attach_extras(kit)
    bpy.context.view_layer.update()
    camloc, _, _ = cam_now(story, tl, t)
    # ---- the tag
    pips = int(round(sample("pips", tl, t, {"n": 1})["n"]))
    pips = max(1, min(5, pips))
    if pips != W["tagn"]:
        if pips not in W["tagimgs"]:
            img = bpy.data.images.load(_tag_image(pips))
            img.colorspace_settings.name = "sRGB"
            W["tagimgs"][pips] = img
        W["tagtex"].image = W["tagimgs"][pips]
        W["tagn"] = pips
    # ---- the door and the sticker
    dr = sample("door", tl, t, {"v": 0.0})["v"]
    W["doorpivot"].rotation_euler = (0, 0, math.radians(104) * dr)
    W["sticker"].hide_render = sample("sticker", tl, t, {"v": 0.0})["v"] < 0.5
    # ---- the curtain sways slowly once it starts (eased in and out), and rests otherwise
    cv = sample("curtain", tl, t, {"v": 0.0})["v"]
    for i, ob in enumerate(W["curtain"]):
        sx = (-1, 1)[i]
        sway = 0.1 * math.sin(t * 2.2 + i) * cv
        ob.location.x = 60.0 + sx * 0.34 - sx * 0.06 * cv + sway
    # ---- boxes on the pizza guy's palms
    bx = sample("boxes", tl, t, {"v": 0.0})["v"] > 0.5
    for root, sx in W["boxes"]:
        h = hand("pizza", sx)
        root.hide_render = not bx or h is None
        for c in root.children:
            c.hide_render = root.hide_render
        if h is not None and bx:
            root.location = h + Vector((0, 0, 0.2))
    # ---- the key and the dinosaur
    kc = sample("key", tl, t, {"mode": "hang", "who": "me", "drop": 0.0})
    mode, who, drop = kc["mode"], kc["who"], kc["drop"]
    heat = sample("heat", tl, t, {"v": 0.8})["v"]
    sw = sample("swing", tl, t, {"v": 0.0})["v"]
    mt = sample("mitt", tl, t, {"v": 0.0})["v"] > 0.5
    key, ring, dp, chain, mitt = W["key"], W["ring"], W["dinopivot"], W["chain"], W["mitt"]
    show_key = mode in ("hang", "hand", "lock", "hook2")
    for ob in [key, ring, dp, chain] + list(key.children) + list(ring.children) + list(W["dino"].children):
        ob.hide_render = not (show_key or (mode == "jess" and ob in [dp, chain] + list(W["dino"].children)))
    if mode in ("hand", "jess"):
        ring.hide_render = True
        for c in ring.children:
            c.hide_render = True
        chain.hide_render = mode != "jess"
    if mode == "jess":
        key.hide_render = True
        for c in key.children:
            c.hide_render = True
    mitt.hide_render = not (mt and mode == "hand")
    for c in mitt.children:
        c.hide_render = mitt.hide_render
    # the warmth: steady, rising with the pips, never a blink
    W["glowmat"].node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.9 + 0.35 * heat
    r = 0.026 + 0.004 * heat
    W["glow"].scale = (r / 0.05 / KS * KS, r / 0.05, r / 0.05)
    if not show_key and mode != "jess":
        key.location = ring.location = dp.location = (0, 0, -40)
        return {}
    # which way the camera is: the pieces face it
    if mode == "hang":
        px, py, pz = G.HOOK
    elif mode == "hook2":
        px, py, pz = W["hook2"]
        pz += 0.5 * drop
    cx, cy = camloc[0], camloc[1]
    if mode in ("hang", "hook2"):
        ph = math.atan2(cy - py, cx - px)
        rx, ry = math.cos(ph + math.pi / 2), math.sin(ph + math.pi / 2)
        fx, fy = math.cos(ph), math.sin(ph)
        ring.hide_render = False
        ring.location = (px + fx * 0.04, py + fy * 0.04, pz - 0.085)
        ring.rotation_euler = (0, 0, ph)
        key.location = (px + rx * -0.055 + fx * 0.045, py + ry * -0.055 + fy * 0.045, pz - 0.15)
        key.rotation_euler = (0, 0, ph)
        dp.location = (px + rx * 0.07 + fx * 0.045, py + ry * 0.07 + fy * 0.045, pz - 0.15)
        dp.rotation_euler = (math.radians(14) * sw * math.sin(t * 3.4), 0, ph)
        chain.hide_render = False
    elif mode in ("hand", "jess"):
        wh = who
        hnd = hand(wh, 1)
        if hnd is None:
            return {}
        lift = 0.19 + (0.05 if mt else 0.0)
        px, py, pz = hnd.x, hnd.y, hnd.z + lift
        ph = math.atan2(cy - py, cx - px)
        rx, ry = math.cos(ph + math.pi / 2), math.sin(ph + math.pi / 2)
        if mode == "hand":
            key.location = (px - rx * 0.06, py - ry * 0.06, pz + 0.31 * KS)
            key.rotation_euler = (0, 0, ph)
            dp.location = (px + rx * 0.1, py + ry * 0.1, pz + 0.2 * DS)
            dp.rotation_euler = (0, 0, ph)
        else:
            dp.location = (px, py, pz + 0.2 * DS + 0.07)
            dp.rotation_euler = (0, 0, ph)
        mitt.location = (hnd.x, hnd.y, hnd.z + 0.04)
        mitt.rotation_euler = (0, 0, ph)
    elif mode == "lock":
        lx, ly, lz = W["lock"]
        L = 0.3 * KS
        key.location = (lx, ly - L, lz)
        key.rotation_euler = (math.pi / 2, 0, 0)
        ph = math.atan2(cy - ly, cx - lx)
        dp.location = (lx, ly - L + 0.065 * KS, lz - 0.02)
        dp.rotation_euler = (math.radians(10) * math.sin(t * 2.0), 0, ph)
        chain.hide_render = False
    return {}
