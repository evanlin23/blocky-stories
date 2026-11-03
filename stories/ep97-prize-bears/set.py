"""ep97 "prize bears": a bright arcade on a sunny afternoon, its prize counter and the closet of forty bears.

One place (plus a couch corner and a car cabin far off to the side for L39/L40). Everything the story moves is driven
by cues in story.json (see animate): "obj" (any prop: show, hide, move over `dur`), "shimmer" (the soft orange slide
off a person at the door), "fdoor" and "cdoor" (the front and closet door angles), "look" (sun/sky, eased 0.4 s),
"tickets" (the rule meter's number). The rule meter is a ticket strip glued to the camera, top left, in every shot.
No lettering anywhere but the three letters CAL on the boards and numerals.
"""
from __future__ import annotations

import math
import random
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import bl_story, faces, rig

TMP = Path(tempfile.mkdtemp(prefix="prizebears-"))
FONT = "DejaVuSans-Bold.ttf"
_n = [0]
NODES = {}


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


class K:
    kit = None


def P(hexc, rough=0.45, spec=0.4):
    return K.kit.plastic(hexc, rough, spec=spec)


def B(parent, size, loc, mat, name="b", bevel=0.01, rot=(0, 0, 0)):
    return K.kit.box(nm(name), size, loc, mat, parent, rot, bevel)


def E(parent=None, loc=(0, 0, 0), name="e", rot=(0, 0, 0)):
    return K.kit.empty(nm(name), loc, parent, rot)


def no_shadow(ob):
    try:
        ob.visible_shadow = False
        ob.visible_glossy = False
        ob.visible_diffuse = False
        ob.visible_transmission = False
    except Exception:
        pass


def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


def font(sz):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(FONT, sz)
    except Exception:
        return ImageFont.load_default()


# ------------------------------------------------------------------------------------------------ image materials
def img_mat(kit, name, path, emit=0.0, rough=0.8, tile=None, alpha=False):
    m = kit._new(nm(name))
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tex = nt.nodes.new("ShaderNodeTexImage")
    im = bpy.data.images.load(str(path))
    im.colorspace_settings.name = "sRGB"
    tex.image = im
    src = tc.outputs["Generated"]
    if tile:
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (tile[0], tile[1], 1)
        nt.links.new(src, mp.inputs["Vector"])
        src = mp.outputs[0]
    nt.links.new(src, tex.inputs["Vector"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    if emit > 0:
        nt.nodes.remove(b)
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = emit
        nt.links.new(tex.outputs["Color"], em.inputs["Color"])
        last = em.outputs[0]
        if alpha:
            tr = nt.nodes.new("ShaderNodeBsdfTransparent")
            mx = nt.nodes.new("ShaderNodeMixShader")
            nt.links.new(tex.outputs["Alpha"], mx.inputs[0])
            nt.links.new(tr.outputs[0], mx.inputs[1])
            nt.links.new(em.outputs[0], mx.inputs[2])
            last = mx.outputs[0]
        nt.links.new(last, out.inputs["Surface"])
        NODES[m.name] = {"em": em, "tex": tex}
    else:
        b.inputs["Roughness"].default_value = rough
        nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    NODES.setdefault(m.name, {})["tex"] = tex
    return m


def uvplane(kit, name, size, loc, mat, parent=None, rot=(0, 0, 0)):
    return kit.plane(nm(name), size, loc, mat, parent, rot)


FACE = (math.pi / 2, 0, 0)       # a plane standing up, facing -y


# ------------------------------------------------------------------------------------------------ pictures
def save(im, name):
    p = TMP / f"{name}.png"
    im.save(p)
    return p


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def bolt(d, cx, cy, s, fill):
    d.polygon([(cx + 0.1 * s, cy - s), (cx - 0.55 * s, cy + 0.1 * s), (cx - 0.05 * s, cy + 0.1 * s),
               (cx - 0.2 * s, cy + s), (cx + 0.55 * s, cy - 0.15 * s), (cx + 0.05 * s, cy - 0.15 * s)], fill=fill)


def carpet_png():
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (512, 512), hexrgb("#5b2bbf"))
    d = ImageDraw.Draw(im)
    for (x, y, k) in ((70, 70, 0), (326, 70, 1), (198, 198, 2), (454, 198, 0), (70, 326, 1), (326, 326, 0),
                      (198, 454, 1), (454, 454, 2)):
        if k == 0:
            star(d, x, y, 34, hexrgb("#7a4fe0"))
        elif k == 1:
            bolt(d, x, y, 34, hexrgb("#46a8e8"))
        else:
            d.ellipse((x - 22, y - 22, x + 22, y + 22), outline=hexrgb("#f08a2a"), width=8)
    return save(im, "carpet")


def board_png(rows, blank=False):
    from PIL import Image, ImageDraw
    W, H = 440, 600
    im = Image.new("RGB", (W, H), hexrgb("#0c1c3a"))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W - 1, H - 1), outline=hexrgb("#3fe7ff"), width=14)
    for i in range(7):
        star(d, 50 + i * 57, 54, 20, hexrgb("#ff9a1f"))
    top = 110
    rh = 66
    f = font(52)
    for i in range(rows):
        y = top + i * rh
        col = hexrgb("#3fe7ff") if i else hexrgb("#ffffff")
        if blank:
            d.rectangle((60, y + 28, 380, y + 38), fill=hexrgb("#1d3a66"))
            continue
        d.text((30, y), str(i + 1), font=f, fill=hexrgb("#ff9a1f"))
        d.text((105, y), "CAL", font=f, fill=col)
        d.text((255, y), str(99990 - i * 970), font=f, fill=col)
    return save(im, f"board-{rows}-{blank}")


def row1_png():
    from PIL import Image, ImageDraw
    W, H = 440, 66
    im = Image.new("RGB", (W, H), hexrgb("#12406a"))
    d = ImageDraw.Draw(im)
    f = font(52)
    d.text((30, 0), "1", font=f, fill=hexrgb("#ff9a1f"))
    d.text((105, 0), "CAL", font=f, fill=hexrgb("#ffffff"))
    d.text((255, 0), "99990", font=f, fill=hexrgb("#ffffff"))
    return save(im, "row1")


def screen_png(k):
    from PIL import Image, ImageDraw
    rnd = random.Random(k * 7 + 1)
    W, H = 280, 220
    base = ["#10244f", "#2a1065", "#0b3a5a", "#401060"][k % 4]
    im = Image.new("RGB", (W, H), hexrgb(base))
    d = ImageDraw.Draw(im)
    cols = ["#3fe7ff", "#ff9a1f", "#ffffff", "#ff4fa0" if False else "#ffd23f", "#7a4fe0"]
    for _ in range(11):
        c = hexrgb(rnd.choice(cols))
        x, y = rnd.randint(10, W - 60), rnd.randint(10, H - 60)
        s = rnd.randint(22, 60)
        kind = rnd.randint(0, 2)
        if kind == 0:
            d.ellipse((x, y, x + s, y + s), fill=c)
        elif kind == 1:
            d.rectangle((x, y, x + s, y + s * 0.6), fill=c)
        else:
            d.polygon([(x, y + s), (x + s, y + s), (x + s / 2, y)], fill=c)
    return save(im, f"screen{k}")


def win_png():
    from PIL import Image, ImageDraw
    W, H = 280, 220
    im = Image.new("RGB", (W, H), hexrgb("#ff9a1f"))
    d = ImageDraw.Draw(im)
    d.ellipse((30, 10, 250, 210), fill=hexrgb("#ffc45a"))
    star(d, 140, 112, 78, hexrgb("#ffffff"))
    return save(im, "win")


def tag_png():
    from PIL import Image, ImageDraw
    W, H = 240, 340
    im = Image.new("RGB", (W, H), hexrgb("#ff9a1f"))
    d = ImageDraw.Draw(im)
    d.ellipse((96, 12, 144, 60), fill=hexrgb("#f3e2c4"))
    rnd = random.Random(5)
    ink = hexrgb("#1e3fd8")
    # a scribbled name: loops and strokes that read as handwriting, never as letters
    x = 28
    pts = []
    for i in range(46):
        x += 4.2
        y = 150 + 34 * math.sin(i * 0.9) * (1 if i % 5 else 0.3) + rnd.randint(-8, 8)
        pts.append((x, y))
    d.line(pts, fill=ink, width=9, joint="curve")
    pts = []
    x = 40
    for i in range(34):
        x += 5
        y = 240 + 26 * math.sin(i * 1.2 + 1) + rnd.randint(-6, 6)
        pts.append((x, y))
    d.line(pts, fill=ink, width=9, joint="curve")
    return save(im, "tag")


def card_png():
    from PIL import Image, ImageDraw
    W, H = 400, 240
    im = Image.new("RGB", (W, H), hexrgb("#3fe7ff"))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W - 1, H - 1), outline=hexrgb("#ffffff"), width=10)
    f = font(100)
    d.text((24, 62), "10,000", font=f, fill=hexrgb("#0c1c3a"))
    bear_glyph(d, 340, 40, 30, hexrgb("#0c1c3a"))
    return save(im, "card")


def bear_glyph(d, cx, cy, r, c):
    d.ellipse((cx - r, cy - r * 0.8, cx + r, cy + r * 1.2), fill=c)
    d.ellipse((cx - r * 1.1, cy - r * 1.2, cx - r * 0.35, cy - r * 0.45), fill=c)
    d.ellipse((cx + r * 0.35, cy - r * 1.2, cx + r * 1.1, cy - r * 0.45), fill=c)


def hud_png(n, bear=False):
    from PIL import Image, ImageDraw
    key = f"hud-{n}-{bear}"
    p = TMP / f"{key}.png"
    if p.exists():
        return str(p)
    W, H = 360, 200
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, W - 7, H - 7), radius=26, fill=hexrgb("#ff9a1f") + (255,),
                        outline=hexrgb("#ffffff") + (255,), width=6)
    for y in (6, H - 7):                       # ticket notches
        pass
    for x in (6, W - 7):
        d.ellipse((x - 20, H // 2 - 20, x + 20, H // 2 + 20), fill=(0, 0, 0, 0))
    for x in range(40, W - 30, 30):            # perforation along the bottom
        d.rectangle((x, H - 40, x + 16, H - 32), fill=hexrgb("#2a1450") + (255,))
    txt = f"{n:,}"
    sz = 118
    while True:
        f = font(sz)
        bb = d.textbbox((0, 0), txt, font=f)
        avail = W - (150 if bear else 70)
        if bb[2] - bb[0] <= avail or sz < 30:
            break
        sz -= 4
    x0 = (W - 14 - (bb[2] - bb[0]) - bb[0]) if bear else (W - (bb[2] - bb[0])) / 2 - bb[0]
    d.text((x0, 20 - bb[1] + (H - 70 - (bb[3] - bb[1])) / 2), txt, font=f, fill=hexrgb("#2a1450") + (255,))
    if bear:
        bear_glyph(d, 62, 78, 34, hexrgb("#2a1450") + (255,))
        d.ellipse((50, 70, 58, 78), fill=hexrgb("#ff9a1f") + (255,))
        d.ellipse((68, 70, 76, 78), fill=hexrgb("#ff9a1f") + (255,))
    im.save(p)
    return str(p)


# ------------------------------------------------------------------------------------------------ the bear
def bear(kit, name, loc, yaw=0.0, scale=1.0, bow=True, parent=None, black_eyes=True):
    e = E(parent, loc, name, rot=(0, 0, yaw * math.pi / 180))
    e.scale = (scale, scale, scale)
    cream, pale, dark = P("#e2cba6", 0.8, 0.15), P("#f0e0c4", 0.8, 0.15), P("#050507", 0.12, 1.0)
    s = kit.sphere
    b = s(nm("bb"), 0.33, (0, 0, 0.38), cream, e, 10)
    b.scale = (1, 0.85, 1.1)
    h = s(nm("bh"), 0.27, (0, -0.02, 0.9), cream, e, 12)
    for sx in (-1, 1):
        s(nm("be"), 0.1, (sx * 0.19, 0.0, 1.12), cream, e, 8)
        s(nm("bi"), 0.055, (sx * 0.19, -0.07, 1.12), pale, e, 6)
        s(nm("bk"), 0.058, (sx * 0.1, -0.225, 0.96), dark, e, 10)          # button eyes
        s(nm("bg"), 0.013, (sx * 0.1 + 0.022, -0.275, 0.985), kit.emit("#ffffff", 10.0, "glint"), e, 4)
        a = s(nm("ba"), 0.12, (sx * 0.36, -0.06, 0.42), cream, e, 8)
        a.scale = (0.8, 0.8, 1.35)
        l = s(nm("bl"), 0.15, (sx * 0.2, -0.2, 0.1), cream, e, 8)
        l.scale = (0.9, 1.1, 0.9)
        s(nm("bf"), 0.07, (sx * 0.2, -0.33, 0.1), pale, e, 6)
    s(nm("bm"), 0.11, (0, -0.2, 0.86), pale, e, 8)
    s(nm("bn"), 0.04, (0, -0.3, 0.9), dark, e, 6)
    if bow:
        ob = P("#ff8a00", 0.5)
        for sx in (-1, 1):
            B(e, (0.14, 0.05, 0.1), (sx * 0.09, -0.2, 0.66), ob, "bow", 0.015, rot=(0, sx * 0.4, 0))
        B(e, (0.06, 0.06, 0.06), (0, -0.2, 0.66), ob, "bowc", 0.01)
    return e


def tag_obj(kit, parent, loc, mat_tag):
    t = B(parent, (0.09, 0.012, 0.13), loc, P("#ff9a1f", 0.5), "tag", 0.004)
    p = kit.plane(nm("tagp"), (0.08, 0.115), (loc[0], loc[1] - 0.008, loc[2]), mat_tag, parent, FACE)
    no_shadow(p)
    return t


# ------------------------------------------------------------------------------------------------ build
LOOKS = {
    "sun": dict(sky="#bfe3ff", sun=4.2, sun_c="#fff0d0", el=36, sky_s=1.0),
    "rain": dict(sky="#8ea0b6", sun=0.9, sun_c="#cfd8e8", el=50, sky_s=0.8),
    "leaf": dict(sky="#f2cf94", sun=3.4, sun_c="#ffc27a", el=20, sky_s=0.95),
}


def build(kit, story, tl):
    K.kit = kit
    ctx = {"late": False, "objs": {}, "texn": {}, "scr_ob": {}}
    P_ = P
    CARPET = img_mat(kit, "carpet", carpet_png(), tile=(11, 9.5), rough=0.95)
    wall = P_("#d9c8ff", 0.9, 0.1)
    wall2 = P_("#bda4f5", 0.9, 0.1)
    white = P_("#f5f5f0", 0.5)
    chrome = P("#cfd6de", 0.3, 0.8)
    blue = P_("#2a5bd7", 0.4)
    orange = P_("#ff9a1f", 0.45)
    cyan_e = kit.emit("#3fe7ff", 3.0, "cyan neon")
    org_e = kit.emit("#ff9a1f", 3.0, "orange neon")
    # ---- floors, walls, ceiling
    kit.box("floor", (16.6, 12.4, 0.2), (0, 5.4, -0.1), CARPET)
    # the carpet's glyph tile: stretch is fine, it is a printed pattern
    kit.box("ceil", (16.6, 12.4, 0.2), (0, 5.4, 3.7), P_("#f4eefc", 0.9))
    kit.box("wallL", (0.3, 12.4, 3.6), (-8.15, 5.4, 1.8), wall)
    kit.box("wallR", (0.3, 12.4, 3.6), (8.15, 5.4, 1.8), wall)
    # back wall in three bits, with the closet door opening at x 3.55..4.65
    kit.box("wallB1", (11.55, 0.3, 3.6), (-8.0 + 11.55 / 2 - 0.0, 11.0, 1.8), wall)
    kit.box("wallB2", (3.35, 0.3, 3.6), (4.65 + 3.35 / 2, 11.0, 1.8), wall)
    kit.box("wallB3", (1.1, 0.3, 1.3), (4.1, 11.0, 2.95), wall)
    # front wall with the glass door opening x -0.9..0.9
    kit.box("wallF1", (7.1, 0.3, 3.6), (-4.45, -1.0, 1.8), wall)
    kit.box("wallF2", (7.1, 0.3, 3.6), (4.45, -1.0, 1.8), wall)
    kit.box("wallF3", (1.8, 0.3, 1.2), (0, -1.0, 3.0), wall)
    for sx in (-1, 1):                                  # the facade, a bright outer skin
        kit.box(f"facade{sx}", (7.1, 0.12, 3.6), (sx * 4.45, -1.21, 1.8), P_("#ff9a1f", 0.6))
    kit.box("facadeT", (1.8, 0.12, 1.2), (0, -1.21, 3.0), P_("#ff9a1f", 0.6))
    for k in range(7):                                  # an awning of stripes over the door
        B(None, (0.6, 1.4, 0.06), (-1.8 + k * 0.6, -1.9, 2.55 - 0.0), P_("#ffffff" if k % 2 else "#2a5bd7", 0.6), "awn",
          0.01, rot=(0.25, 0, 0))
    # neon strips round the top of the room
    kit.box("neonL", (0.04, 11.8, 0.06), (-7.97, 5.4, 3.35), cyan_e)
    kit.box("neonR", (0.04, 11.8, 0.06), (7.97, 5.4, 3.35), org_e)
    kit.box("neonB", (15.6, 0.04, 0.06), (0, 10.84, 3.35), cyan_e)
    # skirting bands
    kit.box("bandL", (0.06, 11.8, 0.35), (-7.97, 5.4, 0.2), wall2)
    kit.box("bandR", (0.06, 11.8, 0.35), (7.97, 5.4, 0.2), wall2)
    # ---- outside
    kit.box("street", (60, 40, 0.2), (0, -22, -0.1), P_("#d3d1cc", 0.9))
    kit.box("curb", (60, 1.2, 0.18), (0, -3.2, 0.0), P_("#ece6dc", 0.9))
    kit.box("lawn", (60, 14, 0.15), (0, -36, -0.02), P_("#7ac25a", 0.9))
    for i, (x, kind) in enumerate(((-10, "sub_building_type_a"), (-2, "sub_building_type_c"), (7, "sub_building_type_f"),
                                   (16, "sub_building_type_k"))):
        try:
            kit.prop(kind, (x, -30, 0), rot=0, height=7.0)
        except Exception:
            pass
    for x in (-14, -6, 4, 12):
        try:
            kit.prop("sub_tree_large", (x, -17, 0), height=5.5)
        except Exception:
            pass
    # ---- the glass doors
    glass = kit.glass("#cfe6f0")
    ctx["fdoor"] = []
    for sx in (-1, 1):
        hinge = E(None, (sx * 0.9, -1.0, 0), "hinge")
        leaf = E(hinge, (0, 0, 0), "leaf")
        w = 0.9
        cx = -sx * w / 2
        B(leaf, (w, 0.05, 2.35), (cx, 0, 1.17), glass, "pane", 0.0)
        for (sz, lc) in (((w, 0.07, 0.07), (cx, 0, 2.38)), ((w, 0.07, 0.1), (cx, 0, 0.05)),
                         ((0.07, 0.07, 2.4), (-sx * 0.035, 0, 1.2)), ((0.07, 0.07, 2.4), (-sx * (w - 0.035), 0, 1.2))):
            B(leaf, sz, lc, chrome, "frm", 0.01)
        kit.cyl(nm("bar"), 0.022, 0.8, (-sx * (w - 0.12), -0.07, 1.1), chrome, leaf, n=10)
        ctx["fdoor"].append((hinge, sx))
    # ---- carpet-level things: cabinets
    scr = [img_mat(kit, f"scr{k}", screen_png(k), emit=1.3) for k in range(4)]
    winm = img_mat(kit, "win", win_png(), emit=1.6)
    ctx["winm"] = winm
    ctx["scr"] = scr

    def cabinet(name, x, y, yaw, k, win_slot=False):
        e = E(None, (x, y, 0), name, rot=(0, 0, yaw * math.pi / 180))
        body = P_("#2a5bd7", 0.4)
        B(e, (0.9, 0.8, 1.0), (0, 0, 0.5), body, "cb", 0.03)
        B(e, (0.9, 0.55, 0.12), (0, -0.5, 1.05), P_("#1c3f9e", 0.4), "deck", 0.03)
        B(e, (0.9, 0.62, 0.85), (0, 0.09, 1.52), body, "cu", 0.03)
        B(e, (0.9, 0.5, 0.26), (0, 0.06, 2.07), org_e if k % 2 else cyan_e, "marq", 0.02)
        B(e, (0.04, 0.8, 0.5), (0.46, 0, 0.55), orange, "stripe", 0.01)
        B(e, (0.04, 0.8, 0.5), (-0.46, 0, 0.55), orange, "stripe", 0.01)
        sc = uvplane(kit, "screen", (0.72, 0.56), (0, -0.226, 1.52), scr[k % 4], e, FACE)
        no_shadow(sc)
        if win_slot:
            ctx["scr_ob"][name] = sc
        kit.cyl(nm("btn"), 0.05, 0.04, (-0.15, -0.55, 1.14), P_("#ff3b3b", 0.3), e, n=12)
        kit.cyl(nm("btn"), 0.05, 0.04, (0.05, -0.55, 1.14), P_("#ffd23f", 0.3), e, n=12)
        kit.cyl(nm("stk"), 0.015, 0.14, (0.28, -0.5, 1.17), chrome, e, n=8)
        kit.sphere(nm("knob"), 0.04, (0.28, -0.5, 1.26), P_("#101014", 0.3), e, 8)
        return e

    ctx["cabs"] = []
    for i, y in enumerate((2.0, 3.4, 4.8, 6.2, 7.6)):
        ctx["cabs"].append(cabinet(f"cabL{i}", -7.0, y, 90, i, win_slot=(i == 2)))
    # a back-to-back island on the right of the middle
    for i, y in enumerate((8.0, 9.3)):
        cabinet(f"cabR{i}", 6.4, y, -90, i + 1)
    # ---- skee-ball lanes (run along y, the player stands at the low end)
    for i, x in enumerate((3.4, 4.6)):
        e = E(None, (x, 0, 0), f"lane{i}")
        B(e, (0.92, 5.6, 0.3), (0, 4.0, 0.15), P_("#c28a4b", 0.55), "lane", 0.02)
        B(e, (0.92, 1.2, 0.26), (0, 6.2, 0.4), P_("#c28a4b", 0.55), "ramp", 0.02, rot=(-0.22, 0, 0))
        B(e, (0.1, 5.6, 0.2), (-0.48, 4.0, 0.4), blue, "rail", 0.02)
        B(e, (0.1, 5.6, 0.2), (0.48, 4.0, 0.4), blue, "rail", 0.02)
        B(e, (0.92, 0.5, 1.7), (0, 6.95, 0.85), blue, "back", 0.03)
        for j, (r, c) in enumerate(((0.26, "#ff9a1f"), (0.18, "#3fe7ff"), (0.1, "#ffffff"))):
            kit.cyl(nm("tgt"), r, 0.03, (0, 6.69, 1.0 + j * 0.0), kit.emit(c, 1.6, f"tgt{c}"), e, rot=(math.pi / 2, 0, 0), n=20)
        B(e, (0.92, 0.5, 0.3), (0, 0.4, 0.75), blue, "ret", 0.03)
    # ---- air hockey
    ah = E(None, (-1.6, 4.2, 0), "airhockey")
    B(ah, (1.2, 2.3, 0.7), (0, 0, 0.35), P_("#e8f4ff", 0.4), "ahb", 0.03)
    B(ah, (1.0, 2.1, 0.04), (0, 0, 0.72), P_("#3fa9f5", 0.25, 0.8), "aht", 0.01)
    for sx in (-1, 1):
        B(ah, (0.1, 2.3, 0.14), (sx * 0.55, 0, 0.8), chrome, "rim", 0.03)
    for sy in (-1, 1):
        B(ah, (0.4, 0.1, 0.14), (-0.35, sy * 1.1, 0.8), chrome, "rim", 0.03)
        B(ah, (0.4, 0.1, 0.14), (0.35, sy * 1.1, 0.8), chrome, "rim", 0.03)
    B(ah, (1.0, 0.02, 0.005), (0, 0, 0.745), P_("#ff4f4f", 0.4), "line", 0.0)
    # the lore tally: two ticket-orange strokes scratched on the chrome rim, low near a goal slot, at least 1 cm proud
    for k in range(2):
        B(ah, (0.012, 0.075, 0.02), (0.575, -0.78 + k * 0.05, 0.795), P_("#ff9a1f", 0.4), "tally", 0.002)
    ctx["lore_ah"] = ah
    # ---- coin pusher
    cp = E(None, (1.7, 4.4, 0), "pusher")
    B(cp, (1.1, 1.3, 1.0), (0, 0, 0.5), P_("#e07a1f", 0.4), "cpb", 0.03)
    B(cp, (1.0, 1.1, 0.4), (0, 0, 1.2), kit.glass("#e8f4ff"), "cpg", 0.02)
    B(cp, (0.9, 1.0, 0.04), (0, 0, 1.03), P_("#fff1b8", 0.4), "cpf", 0.01)
    for j in range(8):
        kit.cyl(nm("coin"), 0.07, 0.015, (-0.3 + (j % 4) * 0.2, -0.2 + (j // 4) * 0.25, 1.06), P_("#ffd23f", 0.3), cp, n=12)
    B(cp, (0.2, 0.2, 0.2), (0, 0.4, 1.5), P_("#2a5bd7", 0.4), "cpt", 0.02)
    ctx["beacon"] = E(cp, (0, 0.4, 1.78), "beacon")
    kit.sphere(nm("jp"), 0.12, (0, 0, 0), kit.emit("#ffb347", 3.0, "jackpot"), ctx["beacon"], 10)
    for sx in (-1, 1):
        B(ctx["beacon"], (0.5, 0.05, 0.05), (sx * 0.3, 0, 0), kit.emit("#ffd23f", 2.5, "jpbeam"), "beam", 0.01)
    # ---- ring drop game (a post and a table)
    rg = E(None, (-4.3, 3.2, 0), "ringgame")
    B(rg, (0.9, 1.1, 0.9), (0, 0, 0.45), P_("#ff9a1f", 0.5), "rgb", 0.03)
    kit.cyl(nm("post"), 0.03, 0.55, (0.0, 0.0, 1.18), chrome, rg, n=10)
    kit.cyl(nm("postb"), 0.07, 0.05, (0.0, 0.0, 0.93), P_("#2a5bd7", 0.4), rg, n=12)
    # ---- stools by the skee lanes
    for sx in (1.2, 2.3):
        e = E(None, (sx, 0.6, 0), "stool")
        kit.cyl(nm("sl"), 0.04, 0.55, (0, 0, 0.28), chrome, e, n=8)
        kit.cyl(nm("st"), 0.2, 0.08, (0, 0, 0.58), P_("#ff9a1f", 0.4), e, n=16)
        kit.cyl(nm("sb"), 0.17, 0.03, (0, 0, 0.02), chrome, e, n=16)
    # ---- the high-score boards on the back wall
    ctx["boards"] = []
    for i, x in enumerate((-7.0, -5.7, -4.4, -3.1)):
        blank = i < 3
        bm = img_mat(kit, f"board{i}", board_png(7, blank), emit=1.1 if not blank else 0.55)
        B(None, (1.2, 0.08, 1.6), (x, 10.78, 1.9), P_("#0c1c3a", 0.4), "bf", 0.02)
        uvplane(kit, "board", (1.1, 1.5), (x, 10.73, 1.9), bm, None, FACE)
    r1 = img_mat(kit, "row1", row1_png(), emit=1.4)
    ctx["row1m"] = r1
    uvplane(kit, "row1", (1.1, 1.5 * 66 / 600), (-3.1, 10.715, 2.2925), r1, None, FACE)
    # ---- the prize wall and the counter
    B(None, (7.0, 0.1, 3.4), (0, 10.82, 1.7), P_("#7a4fe0", 0.6), "pw", 0.02)
    for z in (0.9, 1.5, 2.1):
        B(None, (5.6, 0.7, 0.06), (0, 10.5, z), P_("#f5f5f0", 0.5), "shelf", 0.01)
    rnd = random.Random(9)
    plush_cols = ["#ff5b6e", "#3fe7ff", "#ffd23f", "#6be37a", "#ff9a1f", "#b58cff", "#4a8bff"]
    for z in (0.96, 1.56):
        for k in range(14):
            x = -2.5 + k * 0.385
            c = rnd.choice(plush_cols)
            pm = P_(c, 0.8, 0.1)
            kit.sphere(nm("pl"), 0.14, (x, 10.5, z + 0.14), pm, None, 8)
            kit.sphere(nm("pl"), 0.09, (x, 10.5, z + 0.34), pm, None, 8)
    ctx["tagm"] = img_mat(kit, "tag", tag_png(), emit=0.0, rough=0.7)
    ctx["tagm_em"] = ctx["tagm"]
    gb = bear(kit, "giantbear", (0, 10.5, 2.16), 0, 1.1)
    tag_obj(kit, gb, (-0.19, -0.08, 1.02), ctx["tagm"])
    ctx["giant"] = gb
    # the counter
    B(None, (4.2, 0.8, 1.05), (0, 9.0, 0.525), white, "counter", 0.03)
    B(None, (4.3, 0.9, 0.06), (0, 9.0, 1.08), chrome, "ctop", 0.01)
    for sx in (-1.45, 1.45):
        B(None, (1.1, 0.55, 0.36), (sx, 9.05, 1.29), kit.glass("#eaf6ff"), "case", 0.02)
        for j in range(3):
            B(None, (0.18, 0.18, 0.18), (sx - 0.3 + j * 0.3, 9.05, 1.2), P_(rnd.choice(plush_cols), 0.5), "prz", 0.02)
    B(None, (0.5, 0.35, 0.3), (-0.6, 9.15, 1.26), P_("#2b2f3a", 0.5), "punch", 0.03)
    B(None, (0.3, 0.02, 0.012), (-0.6, 8.97, 1.3), P_("#101014", 0.5), "slot", 0.0)
    # the number card on its foot
    cardm = img_mat(kit, "cardimg", card_png(), emit=1.0)
    ctx["card"] = E(None, (0.35, 8.82, 1.11), "card")
    ctx["objs"]["card"] = ctx["card"]
    B(ctx["card"], (0.46, 0.04, 0.05), (0, 0.02, 0.0), chrome, "cf", 0.01)
    uvplane(kit, "cardp", (0.46, 0.276), (0, 0.0, 0.17), cardm, ctx["card"], FACE)
    hide(ctx["card"], True)
    # the plain closet door (hinge at x 3.55) and the closet
    cd_h = E(None, (3.55, 11.0, 0), "cdoorh")
    B(cd_h, (1.1, 0.06, 2.3), (0.55, 0, 1.15), P_("#d8cfc0", 0.7), "cdoor", 0.01)
    kit.sphere(nm("kn"), 0.04, (0.95, -0.06, 1.1), chrome, cd_h, 8)
    ctx["cdoor"] = cd_h
    # closet: x 1.6..6.6, y 11.15..16.4, ceiling 3.6
    cream_w = P_("#6f604a", 0.9)
    kit.box("clfloor", (5.2, 5.4, 0.2), (4.1, 13.9, -0.1), P_("#5f4e38", 0.85))
    kit.box("clceil", (5.2, 5.4, 0.2), (4.1, 13.9, 3.7), cream_w)
    kit.box("clL", (0.2, 5.4, 3.6), (1.5, 13.9, 1.8), cream_w)
    kit.box("clR", (0.2, 5.4, 3.6), (6.7, 13.9, 1.8), cream_w)
    kit.box("clB", (5.2, 0.2, 3.6), (4.1, 16.6, 1.8), cream_w)
    shelf_m = P_("#8a6a45", 0.7)
    levels = (0.0, 1.2, 2.4)
    for z in levels:
        B(None, (0.9, 5.0, 0.06), (2.05, 13.9, z + 0.03), shelf_m, "shL", 0.01)
        B(None, (0.9, 5.0, 0.06), (6.15, 13.9, z + 0.03), shelf_m, "shR", 0.01)
        B(None, (5.0, 0.9, 0.06), (4.1, 16.1, z + 0.03), shelf_m, "shB", 0.01)
    # forty bears: 12 + 12 on the sides, 15 on the back wall, 1 in the corridor facing the door
    nb = 0
    ctx["closet_bears"] = []
    for z in levels:
        for y in (12.0, 13.1, 14.2, 15.3):
            b1 = bear(kit, f"cb{nb}", (2.05, y, z + 0.06), -90 + 38, 0.95)
            tag_obj(kit, b1, (-0.19, -0.08, 1.02), ctx["tagm"])
            b2 = bear(kit, f"cb{nb + 1}", (6.15, y, z + 0.06), 90 - 38, 0.95)
            tag_obj(kit, b2, (-0.19, -0.08, 1.02), ctx["tagm"])
            nb += 2
        for x in (2.9, 3.5, 4.1, 4.7, 5.3):
            b3 = bear(kit, f"cb{nb}", (x, 16.1, z + 0.06), 0, 0.95)
            tag_obj(kit, b3, (-0.19, -0.08, 1.02), ctx["tagm"])
            nb += 1
    b4 = bear(kit, f"cb{nb}", (4.1, 14.6, 0.0), 0, 0.95)
    tag_obj(kit, b4, (-0.19, -0.08, 1.02), ctx["tagm"])
    nb += 1
    ctx["n_bears"] = nb
    # the bare bulb on its cord, swinging
    ctx["bulbp"] = E(None, (4.1, 12.8, 3.6), "bulbpivot")
    kit.cyl(nm("cord"), 0.01, 0.9, (0, 0, -0.45), P_("#222222", 0.5), ctx["bulbp"], n=6)
    kit.sphere(nm("bulb"), 0.09, (0, 0, -0.55), kit.emit("#ffe2b0", 6.0, "bulb"), ctx["bulbp"], 10)
    kit.light("bulb", "POINT", (3.0, 12.8, 3.1), 330, "#ffc88a", size=0.1)
    kit.light("bulbfill", "AREA", (4.1, 14.0, 3.3), 25, "#ffe7c0", size=3.0, rot=(0, 0, 0))
    kit.light("rimlow", "AREA", (4.1, 15.4, 0.05), 90, "#ffe9c8", size=2.5, rot=(math.pi, 0, 0))
    kit.light("rimside", "AREA", (6.3, 14.0, 1.2), 50, "#ffd9b0", size=1.5, rot=(0, math.pi / 2, 0))
    # ---- lights
    sun = kit.light("sun", "SUN", (0, -30, 30), 4.2, "#fff0d0")
    kit.aim(sun, (0, 3, 0))
    sun.data.angle = math.radians(2.5)
    ctx["sun"] = sun
    for i, (x, y) in enumerate(((-4.5, 3), (0, 3), (4.5, 3), (-4, 8.4), (0.5, 8.0), (5, 7))):
        kit.light(f"ceil{i}", "AREA", (x, y, 3.5), 200, "#fff1dc", size=3.2, rot=(0, 0, 0))
    kit.light("cyanboard", "POINT", (-3.1, 8.7, 2.0), 70, "#3fe7ff", size=0.5)
    kit.light("camfill", "AREA", (0, 0, 2), 60, "#fff4e6", size=1.6)
    # ---- the car (a teal hatchback, nose to the arcade)
    car = E(None, (3.2, -6.4, 0), "car")
    teal = P_("#2fb7a6", 0.35)
    B(car, (1.7, 3.8, 0.7), (0, 0, 0.58), teal, "cbody", 0.08)
    B(car, (1.56, 2.1, 0.62), (0, -0.35, 1.2), teal, "ccab", 0.1)
    B(car, (1.58, 0.9, 0.5), (0, 0.45, 1.15), P_("#143b44", 0.2, 0.8), "cwind", 0.04)
    for sx in (-1, 1):
        B(car, (0.02, 1.8, 0.4), (sx * 0.79, -0.35, 1.25), P_("#143b44", 0.2, 0.8), "cside", 0.01)
        for sy in (-1.2, 1.2):
            kit.cyl(nm("wh"), 0.3, 0.2, (sx * 0.8, sy, 0.3), P_("#1b1b22", 0.7), car, rot=(0, math.pi / 2, 0), n=16)
    B(car, (1.3, 0.02, 0.4), (0, -1.41, 1.3), P_("#143b44", 0.2, 0.8), "crear", 0.0)
    for sx in (-1, 1):
        B(car, (0.2, 0.05, 0.1), (sx * 0.7, -1.93, 0.72), P_("#ff4f4f", 0.3), "tail", 0.02)
        B(car, (0.2, 0.05, 0.1), (sx * 0.7, 1.93, 0.72), P_("#fff4c0", 0.3), "head", 0.02)
    cream = P_("#f3e2c4", 0.8, 0.15)
    kit.sphere(nm("foot"), 0.12, (0.18, -1.435, 1.14), cream, car, 8)
    for k in range(3):
        kit.sphere(nm("toe"), 0.04, (0.1 + k * 0.08, -1.45, 1.27), P_("#fff3dc", 0.8, 0.1), car, 6)
    ctx["car"] = car
    ctx["objs"]["car"] = car
    # leaves and rain (shown by cues)
    rnd2 = random.Random(3)
    ctx["leaves"] = E(None, (0, 0, 0), "leaves")
    for k in range(40):
        c = rnd2.choice(["#e0661f", "#c43c1c", "#f0a020", "#d98d1a"])
        B(ctx["leaves"], (0.22, 0.18, 0.02), (rnd2.uniform(0.5, 6.2), rnd2.uniform(-8.8, -3.8), 0.03), P_(c, 0.8), "leaf", 0.0,
          rot=(0, 0, rnd2.uniform(0, 3)))
    hide(ctx["leaves"], True)
    ctx["rain"] = []
    rm = kit.emit("#dbe8ff", 0.8, "rain")
    for k in range(70):
        r = B(None, (0.012, 0.012, 0.55), (rnd2.uniform(-2, 7), rnd2.uniform(-9, -3), 2), rm, "rn", 0.0)
        no_shadow(r)
        ctx["rain"].append((r, rnd2.random(), r.location.x, r.location.y))
        hide(r, True)
    # ---- the loose props (cue-driven)
    def reg(key, ob, hidden=True):
        ctx["objs"][key] = ob
        if hidden:
            hide(ob, True)
        return ob

    tok = E(None, (0, 0, 0), "token")
    kit.cyl(nm("tk"), 0.045, 0.012, (0, 0, 0.008), kit.emit("#ff9a1f", 1.2, "token"), tok, n=16)
    kit.cyl(nm("tkr"), 0.035, 0.014, (0, 0, 0.008), P_("#ffd23f", 0.3), tok, n=16)
    reg("token", tok)
    puck = E(None, (0, 0, 0), "puck")
    kit.cyl(nm("pk"), 0.05, 0.02, (0, 0, 0.01), P_("#ff3b3b", 0.3), puck, n=14)
    reg("puck", puck)
    ball = E(None, (0, 0, 0), "ball")
    kit.sphere(nm("bl"), 0.07, (0, 0, 0.07), P_("#f5f5f0", 0.3), ball, 10)
    reg("ball", ball)
    ring = E(None, (0, 0, 0), "ring")
    kit.cyl(nm("rg"), 0.08, 0.02, (0, 0, 0), P_("#ff3b9a" if False else "#ff6a3b", 0.4), ring, n=18)
    kit.cyl(nm("rgi"), 0.058, 0.03, (0, 0, 0), P_("#101010", 0.9), ring, n=18) if False else None
    reg("ring", ring)
    duck = E(None, (0, 0, 0), "duck")
    duck_parts(kit, duck, 1.0)
    reg("duck", duck)
    # a strip of tickets sliding across the counter
    tix = E(None, (0, 0, 0), "tix")
    for k in range(6):
        B(tix, (0.18, 0.5, 0.012), (k * 0.2 - 0.5, 0, 0.01 + k * 0.001), P_("#ff9a1f" if k % 2 else "#ffc45a", 0.5), "tx", 0.002,
          rot=(0, 0, 0.1 * (k % 3 - 1)))
    reg("tix", tix)
    # a long ribbon spilling out of a cabinet slot
    rib = E(None, (0, 0, 0), "ribbon")
    for k in range(14):
        B(rib, (0.12, 0.2, 0.006), (math.sin(k * 0.5) * 0.12, -0.12 - k * 0.19, -0.02 * k * 0.0 - 0.015 * k), P_("#ff9a1f" if k % 2 else "#ffc45a", 0.5), "rb", 0.001)
    reg("ribbon", rib)
    # props held on the cast (parented on the first animate, when the rig exists)
    # the shimmer: soft orange bits
    sh = E(None, (0, 0, 0), "shimmer")
    sm = kit.emit("#ff9a1f", 2.2, "shim")
    ctx["shim"] = []
    for k in range(10):
        o = B(sh, (0.09, 0.09, 0.09), (0, 0, 0), sm, "sh", 0.02)
        no_shadow(o)
        ctx["shim"].append((o, random.Random(k).uniform(-0.35, 0.35), random.Random(k + 40).uniform(-0.2, 0.2),
                            random.Random(k + 80).uniform(-0.3, 0.4)))
    ctx["shimp"] = sh
    hide(sh, True)
    build_home(kit, ctx)
    build_cabin(kit, ctx)
    build_hud(kit, ctx)
    ctx["held"] = {}
    # world background
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    ctx["bg"] = bg
    return ctx


def duck_parts(kit, parent, s):
    y = P("#ffd23f", 0.35, 0.5)
    b = kit.sphere(nm("db"), 0.05 * s, (0, 0, 0.05 * s), y, parent, 10)
    b.scale = (1, 1.25, 0.9)
    kit.sphere(nm("dh"), 0.035 * s, (0, -0.045 * s, 0.11 * s), y, parent, 10)
    B(parent, (0.03 * s, 0.03 * s, 0.012 * s), (0, -0.085 * s, 0.105 * s), P("#ff8a00", 0.4), "bill", 0.003)
    for sx in (-1, 1):
        kit.sphere(nm("de"), 0.006 * s, (sx * 0.016 * s, -0.07 * s, 0.125 * s), P("#101014", 0.3), parent, 4)


def build_home(kit, ctx):
    ox = 40.0
    B(None, (7, 6, 0.2), (ox, 1.5, -0.1), P("#e6c9a0", 0.7), "hfloor", 0.01)
    B(None, (7, 0.2, 3.0), (ox, 4.6, 1.5), P("#9fd3c8", 0.9), "hwall", 0.01)
    B(None, (0.2, 6, 3.0), (ox - 3.4, 1.5, 1.5), P("#9fd3c8", 0.9), "hwall", 0.01)
    B(None, (0.2, 6, 3.0), (ox + 3.4, 1.5, 1.5), P("#9fd3c8", 0.9), "hwall", 0.01)
    B(None, (7, 6, 0.2), (ox, 1.5, 3.1), P("#f4eefc", 0.9), "hceil", 0.01)
    B(None, (1.6, 0.05, 1.2), (ox - 1.6, 4.47, 1.7), kit.emit("#cfeaff", 2.0, "hwin"), "hwin", 0.01)
    B(None, (1.8, 0.04, 1.4), (ox - 1.6, 4.5, 1.7), P("#ffffff", 0.5), "hwinf", 0.01)
    B(None, (2.0, 1.2, 0.04), (ox + 0.5, 3.0, 0.02), P("#ff9a1f", 0.8), "hrug", 0.01)
    try:
        kit.prop("couch_medium1", (ox, 3.9, 0), rot=180, height=0.9)
    except Exception:
        B(None, (2.0, 0.9, 0.5), (ox, 3.9, 0.25), P("#2a5bd7", 0.6), "couch", 0.05)
    kit.light("homefill", "AREA", (ox, 1.5, 2.9), 260, "#fff1dc", size=3.0)


def build_cabin(kit, ctx):
    ox, oy = 70.0, 0.0
    skin = P("#e8e4dc", 0.6)
    B(None, (3.2, 0.1, 0.9), (ox, oy + 1.1, 0.45), P("#2b2f3a", 0.6), "dash", 0.04)
    B(None, (3.2, 0.5, 0.15), (ox, oy + 0.9, 0.95), P("#3a3f4c", 0.6), "dashtop", 0.04)
    B(None, (0.1, 2.6, 1.0), (ox - 1.5, oy - 0.2, 0.5), P("#2fb7a6", 0.4), "doorpanel", 0.04)
    B(None, (0.1, 2.6, 1.0), (ox + 1.5, oy - 0.2, 0.5), P("#2fb7a6", 0.4), "doorpanel", 0.04)
    B(None, (0.1, 0.1, 1.2), (ox - 1.42, oy + 1.0, 1.55), P("#2fb7a6", 0.4), "apillar", 0.02, rot=(0.0, 0.1, 0))
    B(None, (0.1, 0.1, 1.2), (ox + 1.42, oy + 1.0, 1.55), P("#2fb7a6", 0.4), "apillar", 0.02, rot=(0.0, -0.1, 0))
    B(None, (3.2, 1.6, 0.1), (ox, oy + 0.4, 2.2), P("#2fb7a6", 0.4), "croof", 0.02)
    kit.cyl(nm("wheel"), 0.17, 0.03, (ox - 0.5, oy + 0.78, 1.0), P("#101014", 0.5), None, rot=(1.2, 0, 0), n=20)
    d = E(None, (ox - 0.1, oy + 0.95, 1.03), "cabduck")
    duck_parts(kit, d, 1.2)
    ctx["cabduck"] = d
    B(None, (3.2, 0.1, 0.9), (ox, oy - 1.6, 0.5), P("#3a3f4c", 0.6), "seatback", 0.04)
    kit.light("cabfill", "AREA", (ox, oy - 0.6, 2.0), 90, "#fff4e6", size=2.4)
    kit.light("cabsun", "AREA", (ox, oy + 2.0, 2.5), 80, "#ffe8bd", size=2.0)


def build_hud(kit, ctx):
    cam = kit.OBJ["cam"]
    m = img_mat(kit, "hud", hud_png(0), emit=1.0, alpha=True)
    ctx["hud_mat"] = m
    pl = kit.plane("hud", (1.0, 1.0), (0, 0, -0.15), m, cam)
    no_shadow(pl)
    ctx["hud"] = pl
    ctx["hud_imgs"] = {}


def place_hud(kit, ctx, n, bear_, lens, big):
    pl = ctx["hud"]
    key = (n, bear_)
    if key not in ctx["hud_imgs"]:
        im = bpy.data.images.load(hud_png(n, bear_))
        im.colorspace_settings.name = "sRGB"
        ctx["hud_imgs"][key] = im
    NODES[ctx["hud_mat"].name]["tex"].image = ctx["hud_imgs"][key]
    d = 0.15
    unit = d / lens
    pw = (0.30 if not big else 0.80) * 13.5 * unit
    ph = pw * 200 / 360
    x = (-0.52 if not big else 0.0) * 6.75 * unit
    y = (0.74 if not big else 0.05) * 12.0 * unit
    pl.location, pl.scale = (x, y, -d), (pw, ph, 1)


# ------------------------------------------------------------------------------------------------ cues
def cue_at(tl, name, t):
    out = {}
    for c in tl.get("cues", []):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c
    return out


def track(tl, name, key="id"):
    out = {}
    for c in tl.get("cues", []):
        if c["name"] == name:
            out.setdefault(c.get(key), []).append(c)
    return out


def obj_state(cues, t):
    """(hidden, pos, yaw, scale) of a cue-driven prop at t: each cue moves it from where it was over its dur."""
    hid, pos, yaw, scl = True, (0.0, 0.0, 0.0), 0.0, 1.0
    for c in cues:
        if c["t"] > t:
            break
        hid = bool(c.get("hide", False))
        ns = c.get("scale", scl)
        if "pos" in c:
            dur = c.get("dur", 0.0)
            np_ = tuple(c["pos"])
            ny = c.get("yaw", yaw)
            if dur > 0 and t < c["t"] + dur:
                u = ss((t - c["t"]) / dur)
                return hid, tuple(lerp(a, b, u) for a, b in zip(pos, np_)), lerp(yaw, ny, u), lerp(scl, ns, u)
            pos, yaw = np_, ny
        scl = ns
    return hid, pos, yaw, scl


def dress_all(kit, ctx):
    R = rig.CHARS
    held = ctx["held"]
    # Tess: a high ponytail, a paper crown, keys on a ring with an orange tag, the duck in her hand, the jacket
    c = R["tess"]
    hg = bpy.data.objects[f"tess.headg"]
    cop = P("#c0602a", 0.6)
    top = faces.HEAD_H / 2
    kit.box("tess.pony1", (0.5, 0.5, 0.5), (0, faces.HEAD_R * 0.9, top - 0.1), cop, hg, bevel=0.1)
    kit.box("tess.pony2", (0.36, 0.36, 1.5), (0, faces.HEAD_R * 1.05, top - 0.8), cop, hg, bevel=0.1)
    kit.box("tess.tie", (0.55, 0.12, 0.12), (0, faces.HEAD_R * 0.75, top - 0.12), P("#ff9a1f", 0.5), hg, bevel=0.02)
    crown = E(hg, (0, 0, top + 0.08), "crown")
    cm = P("#ffd23f", 0.4)
    kit.box(nm("crb"), (1.1, 1.1, 0.16), (0, 0, 0), cm, crown, bevel=0.03)
    for i, x in enumerate((-0.4, -0.2, 0.0, 0.2, 0.4)):
        kit.box(nm("crp"), (0.14, 0.14, 0.3 if i % 2 == 0 else 0.2), (x, -0.4, 0.2), cm, crown, bevel=0.02)
        kit.box(nm("crq"), (0.14, 0.14, 0.3 if i % 2 == 0 else 0.2), (x, 0.4, 0.2), cm, crown, bevel=0.02)
    held["crown"] = crown
    keys = E(c.P["arm1"], (0, -0.2, -1.75), "keys")
    kit.cyl(nm("kr"), 0.2, 0.05, (0, 0, 0), P("#cfd6de", 0.3, 0.8), keys, rot=(math.pi / 2, 0, 0), n=14)
    kit.box(nm("kt"), (0.22, 0.05, 0.34), (0, 0, -0.3), P("#ff9a1f", 0.5), keys, bevel=0.02)
    kit.box(nm("kk"), (0.1, 0.03, 0.4), (0.14, 0, -0.16), P("#cfd6de", 0.3, 0.8), keys, bevel=0.01)
    held["keys"] = keys
    d = E(c.P["arm1"], (0, -0.1, -1.95), "handduck")
    duck_parts(kit, d, 3.4)
    held["handduck"] = d
    jk = E(c.upper, (0, -0.6, 0.0), "jacket")
    kit.box(nm("jk"), (1.9, 0.7, 0.9), (0, -0.1, 0.2), P("#6b7a3a", 0.8), jk, bevel=0.1)
    kit.box(nm("jk"), (0.8, 0.5, 0.8), (0.0, -0.3, 0.6), P("#f2f2f2", 0.8), jk, bevel=0.1)
    held["jacket"] = jk
    # carried bears, one for each of me, Tess and the prize man (scaled into the rig's units)
    for who in ("me", "tess", "prize"):
        cr = R[who]
        b = bear(kit, f"carry_{who}", (0, -1.0, -0.2), 0, 0.5 / 1.2 / 0.34, parent=cr.upper)
        held[f"bear_{who}"] = b
    # the ticket man's fistful of tickets (arm1 end)
    tm = R["ticket_man"]
    fist = E(tm.P["arm1"], (0, -0.2, -1.8), "fist")
    for k in range(5):
        kit.box(nm("ft"), (0.16, 0.5, 0.08), (0.05 * (k - 2), -0.1, 0.2 + 0.03 * k), P("#ff9a1f" if k % 2 else "#ffc45a", 0.5),
                fist, rot=(0, 0.2 * (k - 2), 0.15 * (k - 2)), bevel=0.01)
    held["fist"] = fist
    jl = R["jackpot_lady"]
    fl = E(jl.P["arm1"], (0, -0.2, -1.8), "ladytix")
    for k in range(4):
        kit.box(nm("lt"), (0.16, 0.5, 0.08), (0.05 * (k - 2), -0.1, 0.2 + 0.03 * k), P("#ffc45a" if k % 2 else "#ff9a1f", 0.5),
                fl, rot=(0, 0.2 * (k - 2), 0.15 * (k - 2)), bevel=0.01)
    held["ladytix"] = fl
    # the prize man's lanyard and ticket punch
    pm = R["prize"]
    B(pm.upper, (0.1, 0.05, 1.5), (0, -0.52, 1.0), P("#ff9a1f", 0.5), "lan", 0.01)
    B(pm.upper, (0.5, 0.2, 0.5), (0, -0.58, 0.28), P("#2b2f3a", 0.5), "pun", 0.03)
    # my cowlick is the mop's tuft; a bomber's cuff band
    for hh in held.values():
        hide(hh, True)


# ------------------------------------------------------------------------------------------------ animate
def look_state(tl, t):
    cur = LOOKS["sun"]
    prev = cur
    for c in tl.get("cues", []):
        if c["name"] != "look":
            continue
        if c["t"] > t:
            break
        prev, cur = cur, LOOKS[c["id"]]
        dur = max(0.4, c.get("dur", 0.4))
        if t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            out = {}
            for k in cur:
                if isinstance(cur[k], str):
                    a, b = hexrgb(prev[k]), hexrgb(cur[k])
                    out[k] = tuple(lerp(x, y, u) / 255 for x, y in zip(a, b))
                else:
                    out[k] = lerp(prev[k], cur[k], u)
            return out
    return {k: (tuple(x / 255 for x in hexrgb(v)) if isinstance(v, str) else v) for k, v in cur.items()}


def lin(c):
    f = lambda x: x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    return tuple(f(x) for x in c)


def animate(kit, story, tl, t, ctx):
    if not ctx["late"]:
        dress_all(kit, ctx)
        ctx["late"] = True
    sc = bpy.context.scene
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next(s for s in story["shots"] if s["id"] == shot["id"])
    loc, tgt, lens, _ = bl_story.cam_at(spec, shot, t, {}, tl)
    # ---- looks
    L = look_state(tl, t)
    ctx["bg"].inputs["Color"].default_value = (*lin(L["sky"]), 1)
    ctx["bg"].inputs["Strength"].default_value = L["sky_s"]
    el = math.radians(L["el"])
    s = V((0.0, -math.cos(el), math.sin(el)))
    ctx["sun"].rotation_euler = (-s).to_track_quat("-Z", "Y").to_euler()
    ctx["sun"].data.color = lin(L["sun_c"])
    kit.LIGHTS["sun"]["base"] = L["sun"]
    # ---- camera fill
    cam = V(loc)
    fw = V(tgt) - cam
    d = max(1.2, min(fw.length, 8.0))
    cf = kit.LIGHTS["camfill"]
    cf["obj"].location = cam + V((0, 0, 0.2))
    cf["obj"].rotation_euler = fw.to_track_quat("-Z", "Y").to_euler()
    cf["base"] = 8 * d * d * spec.get("cfill", 1.0)
    ov = {}
    # the cyan board light follows only the shots that need it
    ov["cyanboard"] = spec.get("cyan", 1.0)
    # ---- doors
    fd = cue_at(tl, "fdoor", t)
    ang = 95.0
    if fd:
        a1 = fd.get("angle", 95.0)
        prev_a = fd.get("from", 95.0)
        dur = max(0.4, fd.get("dur", 0.4))
        ang = lerp(prev_a, a1, ss((t - fd["t"]) / dur))
    for hinge, sx in ctx["fdoor"]:
        hinge.rotation_euler = (0, 0, -sx * math.radians(ang))
    cd = cue_at(tl, "cdoor", t)
    ca = 0.0
    if cd:
        dur = max(0.4, cd.get("dur", 0.4))
        ca = lerp(cd.get("from", 0.0), cd.get("angle", 0.0), ss((t - cd["t"]) / dur))
    ctx["cdoor"].rotation_euler = (0, 0, math.radians(ca))
    # ---- the bulb swings a little
    ctx["bulbp"].rotation_euler = (0.05 * math.sin(t * 2.1), 0.06 * math.sin(t * 1.7 + 1.0), 0)
    kit.LIGHTS["bulb"]["obj"].location = (4.1 + 0.05 * math.sin(t * 1.7 + 1.0) * 0.9, 12.8 + 0.05 * math.sin(t * 2.1) * 0.9, 2.6)
    # ---- beacon turns slowly; board row 1 breathes
    ctx["beacon"].rotation_euler = (0, 0, t * 0.9)
    NODES[ctx["row1m"].name]["em"].inputs["Strength"].default_value = 1.3 + 0.55 * math.sin(t * 3.4)
    # ---- cabinet 2 can bloom orange on a "win" cue
    wn = cue_at(tl, "win", t)
    on = bool(wn.get("on")) if wn else False
    NODES[ctx["winm"].name]["em"].inputs["Strength"].default_value = 0.3 + 1.4 * ss((t - wn["t"]) / 0.6) if wn else 1.6
    ob = ctx["scr_ob"].get("cabL2")
    if ob:
        ob.data.materials[0] = ctx["winm"] if on else ctx["scr"][2]
    # ---- the loose props
    tr = track(tl, "obj")
    for key, cs in tr.items():
        o = ctx["objs"].get(key)
        if o is None:
            continue
        hid, pos, yaw, scl = obj_state(cs, t)
        hide(o, hid)
        o.location = pos
        o.rotation_euler = (0, 0, math.radians(yaw))
        o.scale = (scl, scl, scl)
    for key, o in ctx["held"].items():
        owner = {"crown": "tess", "keys": "tess", "handduck": "tess", "jacket": "tess", "fist": "ticket_man",
                 "ladytix": "jackpot_lady"}.get(key, key.replace("bear_", ""))
        hid = obj_state(tr[key], t)[0] if key in tr else True
        hide(o, hid or rig.CHARS[owner].root.hide_render)
    if "held" in ctx:
        pass
    # ---- weather
    wcue = cue_at(tl, "weather", t)
    kind = wcue.get("kind", "") if wcue else ""
    hide(ctx["leaves"], kind != "leaf")
    for r, ph, x, y in ctx["rain"]:
        hide(r, kind != "rain")
        if kind == "rain":
            r.location = (x, y, 3.0 - ((t * 4.0 + ph) % 1.0) * 3.0)
    # ---- the shimmer
    shown = False
    for c in tl.get("cues", []):
        if c["name"] == "shimmer" and c["t"] <= t < c["t"] + c["dur"]:
            u = (t - c["t"]) / c["dur"]
            env = math.sin(math.pi * u) ** 0.7
            base = V(c["pos"])
            dr = V(c["dir"])
            for i, (o, jx, jy, jz) in enumerate(ctx["shim"]):
                p = base + dr * u + V((jx, jy * 0.5, jz * 0.5 + 0.2 * (i % 3)))
                o.location = p
                o.rotation_euler = (u * 3 + i, u * 2, i)
                sz = 0.7 * env + 0.001
                o.scale = (sz, sz, sz)
            shown = True
    hide(ctx["shimp"], not shown)
    # ---- the rule meter
    tk = cue_at(tl, "tickets", t)
    n = tk.get("n", 0) if tk else 0
    b = bool(tk.get("bear")) if tk else False
    place_hud(kit, ctx, n, b, lens, spec.get("hud") == "big")
    return ov
