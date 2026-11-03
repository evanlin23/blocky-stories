"""ep96 friend card: one scene, nineteen small stages 100 m apart (layout.py). The rooftop wedding at sunset is the
main one; the rest are the ten years in sunny pieces. All set pieces are built from kit.py's blocks and a few CC0
props. There is no lettering anywhere: times, dates and the gate number are numerals, every "writing" is a row of
abstract glyph shapes drawn here.

Cues read in animate():
  ring {p}          the card inset's ring fills linearly from one cue to the next (0..1)
  card {face, rz}   the hand rig's card: front picture (mine / sealed / hers) and its turn about the vertical (deg),
                    eased over `dur`
  hand {who}        which hand is on screen: me / hers / palm (the ring box on an open palm)
  watch {time}      the digital watch face on the hand rig: 9:00 / 9:11 / 9:12 / 9:13 / 9:14
  wbar {p0, p1, dur}  the watch's seconds bar sweeps from p0 to p1
  calflip {i}       calendar page i flips up and away over 0.4 s
  drop              the sealed card falls through the mail slot
  door {id, open, dur}  the diner / porch door
  show {id, on}     a named group shows or hides (balloons, cake, dinner)
  sit {who, z, on}  seated: hips at z metres, legs forward
  held {obj, who, off, yaw, dur, on}  a prop carried by a character; off is in the character's frame (y < 0 forward)
  petals {on}       petals falling over the roof guests
"""
from __future__ import annotations

import math
import random
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from blocky import bl_story, polish, rig

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import layout as LY  # noqa: E402

FONT = HERE.parent.parent / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"

CREAM = (244, 234, 210)
NAVY = (40, 50, 79)
GOLD = (255, 176, 46)


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def cue_list(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def cue_at(tl, name, t):
    out = {}
    for c in tl.get("cues", []):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c
    return out


def shot_at(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


# ------------------------------------------------------------------------------------------------ pictures
def font(n):
    return ImageFont.truetype(str(FONT), n)


def glyph_row(dr, x0, y, n, step, size, color, seed):
    """A row of abstract marks (circles, squares, triangles, bars, diamonds): never letters."""
    rnd = random.Random(seed)
    for i in range(n):
        x = x0 + i * step
        k = rnd.randrange(6)
        s = size
        if k == 0:
            dr.ellipse([x, y, x + s, y + s], fill=color)
        elif k == 1:
            dr.rectangle([x, y, x + s, y + s], outline=color, width=max(2, s // 6))
        elif k == 2:
            dr.polygon([(x + s / 2, y), (x + s, y + s), (x, y + s)], fill=color)
        elif k == 3:
            dr.rectangle([x, y, x + s / 3, y + s], fill=color)
            dr.rectangle([x + 2 * s / 3, y, x + s, y + s], fill=color)
        elif k == 4:
            dr.polygon([(x + s / 2, y), (x + s, y + s / 2), (x + s / 2, y + s), (x, y + s / 2)], fill=color)
        else:
            dr.arc([x, y, x + s, y + s], 200, 340, fill=color, width=max(2, s // 5))


def card_png(path, kind):
    W, H = 800, 500
    im = Image.new("RGBA", (W, H), CREAM + (255,))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([14, 14, W - 15, H - 15], 26, outline=(224, 204, 164, 255), width=8)
    if kind == "sealed":
        dr.ellipse([W / 2 - 90, H / 2 - 90, W / 2 + 90, H / 2 + 90], fill=(214, 72, 70, 255))
        dr.ellipse([W / 2 - 62, H / 2 - 62, W / 2 + 62, H / 2 + 62], outline=(240, 150, 140, 255), width=8)
        glyph_row(dr, 150, 420, 14, 36, 22, (190, 160, 110, 255), 3)
    elif kind in ("mine", "hers"):
        f = font(300)
        txt = "9:14"
        w = dr.textlength(txt, font=f)
        dr.text((W / 2 - w / 2, 215), txt, font=f, fill=NAVY + (255,), anchor="lm")
        f2 = font(54)
        dr.text((52, 66), "6/12", font=f2, fill=(120, 100, 70, 255), anchor="lm")
        glyph_row(dr, 130, 392, 16, 36, 24, (220, 120, 60, 255) if kind == "mine" else (214, 90, 130, 255), 11)
    else:  # back: two rows of tiny marks and a small round stamp
        dr.ellipse([W / 2 - 38, 70, W / 2 + 38, 146], outline=(200, 160, 110, 255), width=6)
        glyph_row(dr, 110, 230, 22, 27, 13, (90, 76, 60, 255), 21)
        glyph_row(dr, 110, 290, 22, 27, 13, (90, 76, 60, 255), 22)
        glyph_row(dr, 200, 350, 14, 27, 13, (90, 76, 60, 255), 23)
    im.save(path)


def watch_png(path, txt):
    W = 400
    im = Image.new("RGBA", (W, W), (30, 34, 46, 255))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([14, 14, W - 15, W - 15], 40, fill=(8, 22, 24, 255), outline=(120, 130, 150, 255), width=10)
    f = font(150)
    w = dr.textlength(txt, font=f)
    dr.text((W / 2 - w / 2, 190), txt, font=f, fill=(120, 255, 220, 255), anchor="lm")
    dr.rounded_rectangle([60, 300, W - 60, 322], 8, outline=(60, 120, 110, 255), width=4)
    im.save(path)


def inset_png(path, k, n=16):
    """The rule marker: a navy disc, a ring that fills clockwise to k/n, and the 9:14 card inside."""
    W = 512
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse([6, 6, W - 7, W - 7], fill=(36, 44, 76, 245))
    box = [38, 38, W - 39, W - 39]
    dr.ellipse(box, outline=(255, 255, 255, 70), width=34)
    if k > 0:
        dr.arc(box, -90, -90 + 360.0 * k / n, fill=GOLD + (255,), width=34)
    dr.rounded_rectangle([96, 156, W - 97, W - 157], 26, fill=CREAM + (255,))
    f = font(150)
    txt = "9:14"
    w = dr.textlength(txt, font=f)
    sc = min(1.0, 296 / w)
    f = font(int(150 * sc))
    w = dr.textlength(txt, font=f)
    dr.text((W / 2 - w / 2, W / 2 + 4), txt, font=f, fill=NAVY + (255,), anchor="lm")
    im.save(path)


def calendar_png(path, crossed):
    W, H = 700, 880
    im = Image.new("RGBA", (W, H), (252, 250, 244, 255))
    dr = ImageDraw.Draw(im)
    dr.rectangle([0, 0, W, 150], fill=(156, 197, 154, 255))
    for x in (160, 540):
        dr.ellipse([x - 20, 60, x + 20, 100], fill=(60, 80, 70, 255))
    f = font(54)
    cw, ch = 96, 120
    x0, y0 = 14, 200
    n = 1
    for r in range(5):
        for c in range(7):
            if n > 30:
                break
            cx, cy = x0 + c * cw + cw / 2, y0 + r * ch + ch / 2
            dr.rectangle([x0 + c * cw + 3, y0 + r * ch + 3, x0 + (c + 1) * cw - 3, y0 + (r + 1) * ch - 3], outline=(214, 208, 190, 255), width=3)
            dr.text((cx, cy), str(n), font=f, fill=NAVY + (255,), anchor="mm")
            if n == 12 and crossed:
                dr.line([(cx - 52, cy - 62), (cx + 52, cy + 62)], fill=(206, 54, 54, 255), width=16)
                dr.line([(cx - 52, cy + 62), (cx + 52, cy - 62)], fill=(206, 54, 54, 255), width=16)
            n += 1
    im.save(path)


def gate_png(path):
    W, H = 640, 320
    im = Image.new("RGBA", (W, H), (28, 52, 98, 255))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([8, 8, W - 9, H - 9], 28, outline=(255, 210, 90, 255), width=10)
    f = font(300)
    dr.text((W / 2 + 60, H / 2 + 14), "9", font=f, fill=(255, 255, 255, 255), anchor="mm")
    dr.polygon([(70, H / 2 - 60), (150, H / 2 - 60), (150, H / 2 - 100), (230, H / 2), (150, H / 2 + 100), (150, H / 2 + 60), (70, H / 2 + 60)], fill=(255, 210, 90, 255))
    im.save(path)


def movie_png(path):
    pass


def img_mat(kit, name, path, strength=1.0, alpha=True):
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
    return m


def torus(kit, name, R, r, mat, loc, parent, nu=28, nv=8):
    verts, faces = [], []
    for i in range(nu):
        a = 2 * math.pi * i / nu
        for j in range(nv):
            b = 2 * math.pi * j / nv
            rr = R + r * math.cos(b)
            verts.append((rr * math.cos(a), rr * math.sin(a), r * math.sin(b)))
    for i in range(nu):
        for j in range(nv):
            a, b = i * nv + j, i * nv + (j + 1) % nv
            c, d = ((i + 1) % nu) * nv + (j + 1) % nv, ((i + 1) % nu) * nv + j
            faces.append((a, b, c, d))
    return kit.mesh_obj(name, verts, faces, mat, parent, loc, smooth=True)


# ------------------------------------------------------------------------------------------------ build
W = {}   # named things animate() moves


def build(kit, story, tl):
    work = Path(tempfile.mkdtemp(prefix="ep96-"))
    kit.FLASH_SAFE = True
    M = kit.plastic
    box = kit.box
    cyl = kit.cyl

    def at(stage, x, y, z=0.0):
        ox, oy = LY.ST[stage]
        return (ox + x, oy + y, z)

    # ---- the sun: one low warm key from the camera side for every stage (golden hour), the sky does the rest
    sun = kit.light("sun", "SUN", (0, 0, 20), 2.8, "#ffcf9e", size=0.4)
    sun.rotation_euler = (math.radians(52), math.radians(-18), math.radians(-20))
    for st in LY.ST:
        pass

    build_inset(kit, work)
    build_roof(kit, work, at)
    build_hand(kit, work, at)
    build_hall(kit, work, at)
    build_park(kit, work, at)
    build_lawn(kit, work, at)
    build_gate(kit, work, at)
    build_curb(kit, work, at)
    build_cal(kit, work, at)
    build_living(kit, work, at)
    build_diner(kit, work, at)
    build_porch(kit, work, at)
    build_yard(kit, work, at)
    build_garage(kit, work, at)
    build_bowl(kit, work, at)
    build_beach(kit, work, at)
    build_van(kit, work, at)
    build_bench(kit, work, at)
    build_street(kit, work, at)
    build_win(kit, work, at)
    build_helds(kit, work)
    W["tl_built"] = False
    return {"work": work}


# ---------------------------------------------------------------------------- the rule marker (camera-parented)
def build_inset(kit, work):
    W["inset_mats"] = []
    for k in range(17):
        p = work / f"inset{k}.png"
        inset_png(p, k)
        W["inset_mats"].append(img_mat(kit, f"inset {k}", p, 1.25))
    pl = kit.plane("inset", (1, 1), (0, 0, -1), W["inset_mats"][4])
    pl.parent = kit.OBJ["cam"]
    pl.visible_shadow = False
    W["inset"] = pl


# ---------------------------------------------------------------------------- the rooftop wedding
def build_roof(kit, work, at):
    M, box, cyl = kit.plastic, kit.box, kit.cyl
    rnd = random.Random(96)
    tile = kit.checker("#f1e3cf", "#ead8c0", 1.0, name="roof tile")
    box("roof.floor", (16, 24, 0.3), (0, 6, -0.15), tile)
    wallm = M("#fbf4ea", 0.6, spec=0.2)
    for sx in (-1, 1):
        box(f"roof.par{sx}", (0.3, 24.3, 0.9), (sx * 8.0, 6, 0.45), wallm)
    box("roof.parF", (16.3, 0.3, 0.9), (0, 18.0, 0.45), wallm)
    box("roof.parB", (16.3, 0.3, 0.9), (0, -6.0, 0.45), wallm)
    # the stair bulkhead behind the entrance
    box("roof.bulk", (3.4, 2.6, 2.8), (3.5, -4.6, 1.4), M("#f2d5b8", 0.7))
    box("roof.bulkdoor", (1.0, 0.06, 2.0), (3.5, -5.93, 1.0), M("#9cc59a", 0.5))
    # the aisle runner and petals
    box("roof.runner", (1.5, 12.2, 0.02), (0, 6.2, 0.01), M("#ffc1cc", 0.8, spec=0.1))
    rp = M("#ffa5b8", 0.8)
    for i in range(46):
        box(f"roof.pet{i}", (0.07, 0.05, 0.01), (rnd.uniform(-0.65, 0.65), rnd.uniform(0.6, 11.5), 0.03), rp, rot=(0, 0, rnd.uniform(0, 3)))
    # chairs: seat, back and a block base, 7 rows each side
    chm, chb = M("#fafafa", 0.5, spec=0.3), M("#e6e6e6", 0.6)
    for row in range(7):
        y = 2.2 + row * 1.2
        for side in (-1, 1):
            for i in range(4):
                x = side * (1.25 + 0.62 * i)
                box(f"roof.ch{row}{side}{i}.s", (0.46, 0.46, 0.05), (x, y, 0.47), chm, bevel=0.012)
                box(f"roof.ch{row}{side}{i}.b", (0.46, 0.05, 0.46), (x, y - 0.21, 0.72), chm, bevel=0.012)
                box(f"roof.ch{row}{side}{i}.l", (0.40, 0.40, 0.45), (x, y, 0.225), chb)
    # the arch
    ay = LY.ARCH_Y
    arch_w = M("#fafafa", 0.5)
    brass = M("#d6a843", 0.28, spec=0.7)
    for sx in (-1, 1):
        box(f"roof.post{sx}", (0.16, 0.16, 2.2), (sx * 1.35, ay, 1.1), arch_w, bevel=0.02)
        box(f"roof.plinth{sx}", (0.7, 0.5, 0.22), (sx * 1.35, ay, 0.11), brass, bevel=0.02)
    # the tally: two string-light-gold strokes scratched into the left brass base, proud of its front face
    gold = kit.emit("#ffd98a", 2.2, name="tally")
    box("roof.tally0", (0.022, 0.012, 0.13), (-1.35 - 0.1, ay - 0.256, 0.11), gold)
    box("roof.tally1", (0.022, 0.012, 0.13), (-1.35 + 0.1, ay - 0.256, 0.11), gold)
    petal_cols = ["#ffc1cc", "#fafafa", "#9cc59a", "#ffb38a", "#ffe08a"]
    for i in range(23):
        a = math.pi * i / 22
        x, z = 1.35 * math.cos(a), 2.2 + 1.0 * math.sin(a)
        c = petal_cols[i % 5]
        box(f"roof.fl{i}", (0.3, 0.3, 0.3), (x, ay, z), M(c, 0.7, spec=0.1), rot=(0, 0, rnd.uniform(0, 1.5)), bevel=0.05)
        box(f"roof.lf{i}", (0.2, 0.2, 0.22), (x * 1.0, ay - 0.1, z - 0.05), M("#7bb07a", 0.7), bevel=0.05)
    for sx in (-1, 1):
        for k in range(5):
            box(f"roof.vn{sx}{k}", (0.26, 0.26, 0.26), (sx * 1.35, ay - 0.05, 0.5 + k * 0.42), M(petal_cols[(k + 1) % 5], 0.7), bevel=0.05, rot=(0, 0, k))
    # olive trees in pots
    for x, y in ((-5.5, 3), (5.5, 3), (-5.5, 9), (5.5, 9), (-3.4, 13.4), (3.4, 13.4)):
        box(f"roof.pot{x}{y}", (0.7, 0.7, 0.55), (x, y, 0.275), M("#e9c9a3", 0.7), bevel=0.05)
        cyl(f"roof.trunk{x}{y}", 0.07, 1.3, (x, y, 1.2), M("#8a6a4a", 0.8))
        kit.sphere(f"roof.crown{x}{y}", 0.62, (x, y, 2.05), M("#8fb98a", 0.7))
        kit.sphere(f"roof.crownb{x}{y}", 0.45, (x + 0.35, y + 0.1, 1.8), M("#7aa876", 0.7))
    # string lights: poles and three strands across
    pole = M("#d8c3a5", 0.7)
    bulb = kit.emit("#ffd98a", 7.0, name="bulb")
    for y in (3.0, 6.8, 10.6):
        for sx in (-1, 1):
            box(f"roof.pole{y}{sx}", (0.12, 0.12, 3.5), (sx * 6.6, y, 1.75), pole)
        for i in range(17):
            u = i / 16
            x = -6.6 + 13.2 * u
            z = 3.4 - 0.55 * math.sin(math.pi * u)
            kit.sphere(f"roof.bulb{y}{i}", 0.075, (x, y, z), bulb, seg=8)
    # the skyline: a ring of blocks well below and a few above the roof line, water towers on some
    cols = ["#f0b9a2", "#dba7c6", "#f6d3a6", "#b8a9d8", "#f8dcb8", "#cfa59c", "#e9c0d0"]
    for k in range(36):
        a = 2 * math.pi * k / 36 + rnd.uniform(-0.05, 0.05)
        r = rnd.uniform(26, 44)
        cx, cy = 0 + r * math.cos(a), 6 + r * math.sin(a) * 1.25
        w, d = rnd.uniform(6, 11), rnd.uniform(6, 11)
        top = rnd.uniform(-4.0, 4.0) if k % 4 else rnd.uniform(5.0, 9.0)
        box(f"roof.bld{k}", (w, d, top + 40), (cx, cy, (top - 40) / 2), M(cols[k % len(cols)], 0.8, spec=0.1))
        if k % 6 == 1:
            tz = top
            for lx in (-1, 1):
                for ly in (-1, 1):
                    box(f"roof.tl{k}{lx}{ly}", (0.2, 0.2, 1.4), (cx + lx * 0.9, cy + ly * 0.9, tz + 0.7), M("#7a6a62", 0.8))
            cyl(f"roof.tank{k}", 1.4, 2.4, (cx, cy, tz + 2.5), M("#c98a64", 0.7), n=16)
            cyl(f"roof.tcap{k}", 1.5, 0.9, (cx, cy, tz + 4.1), M("#a8694a", 0.7), n=16, r2=0.15)
    # the back wall of sky: nothing. Lights: a warm low fill from the arch end and a soft one from the entrance end
    kit.light("roof.fillA", "AREA", (0, 17.0, 3.2), 520, "#ffcf9e", rot=(math.radians(-100), 0, 0), size=8)
    kit.light("roof.fillB", "AREA", (0, -4.0, 3.0), 360, "#ffe6c8", rot=(math.radians(100), 0, 0), size=8)
    # petals falling (hidden until the cue)
    W["petals"] = []
    pm = M("#ffa5b8", 0.7)
    for i in range(44):
        ob = box(f"petal.{i}", (0.07, 0.05, 0.012), (0, 0, -9), pm)
        ob.hide_render = True
        W["petals"].append((ob, rnd.uniform(-3.6, 3.6), rnd.uniform(5.4, 11.2), rnd.random(), rnd.uniform(1.8, 2.6)))


# ---------------------------------------------------------------------------- close hands: card, watch, ring box
def build_hand(kit, work, at):
    M, box, cyl = kit.plastic, kit.box, kit.cyl
    ox, oy, _ = at("hand", 0, 0)
    root = kit.empty("hand.root", (ox, oy, 1.2))
    W["handroot"] = root
    # the back: warm peach plane and soft gold lights well behind, like string lights out of focus
    bg = M("#ffb98c", 0.9, spec=0.05)
    kit.plane("hand.bg", (60, 40), (ox, oy + 5.0, 1.2), bg, rot=(math.pi / 2, 0, 0))
    rnd = random.Random(7)
    for i in range(26):
        r = rnd.uniform(0.12, 0.34)
        c = rnd.choice(["#ffd98a", "#ffe9a8", "#ffc9a0", "#ffb8c0"])
        d = cyl(f"hand.bok{i}", r, 0.01, (ox + rnd.uniform(-2.1, 2.1), oy + rnd.uniform(3.2, 3.9), 1.2 + rnd.uniform(-1.2, 1.9)),
                kit.emit(c, rnd.uniform(2.2, 4.5), name=f"bok{i}"), None, rot=(math.pi / 2, 0, 0), n=24)
    skin_me, skin_hr = "#d9a577", "#b57a53"

    def card_group(parent, name, loc):
        g = kit.empty(name, loc, parent)
        box(f"{name}.body", (0.16, 0.004, 0.10), (0, 0, 0), M("#f4ead2", 0.6, spec=0.2), g, bevel=0.0015)
        mats = {}
        for k in ("mine", "sealed", "hers", "back"):
            p = work / f"card_{k}.png"
            card_png(p, k)
            mats[k] = img_mat(kit, f"card {k}", p, 0.95, alpha=False)
        front = kit.plane(f"{name}.front", (0.16, 0.10), (0, -0.0034, 0), mats["mine"], g, rot=(math.pi / 2, 0, 0))
        back = kit.plane(f"{name}.back", (0.16, 0.10), (0, 0.0034, 0), mats["back"], g, rot=(math.pi / 2, 0, math.pi))
        return g, front, mats

    def sleeve_arm(parent, tag, skin, sleeve_c, cuff_c):
        # a vertical forearm from the lower right; the palm sits behind the card's bottom corner, the thumb in front
        b = kit.empty(f"{tag}.arm", (0, 0, 0), parent)
        box(f"{tag}.palm", (0.07, 0.034, 0.088), (0.052, 0.024, -0.016), M(skin, 0.5), b, bevel=0.008)
        box(f"{tag}.thumb", (0.02, 0.02, 0.062), (0.05, -0.012, 0.0), M(skin, 0.5), b, rot=(0, 0.25, 0), bevel=0.006)
        box(f"{tag}.fing", (0.052, 0.014, 0.02), (0.034, -0.002, 0.036), M(skin, 0.5), b, bevel=0.005)
        box(f"{tag}.wrist", (0.056, 0.05, 0.05), (0.055, 0.028, -0.082), M(skin, 0.5), b, bevel=0.008)
        box(f"{tag}.cuff", (0.074, 0.074, 0.03), (0.057, 0.03, -0.125), M(cuff_c, 0.6), b, bevel=0.006)
        box(f"{tag}.sleeve", (0.082, 0.082, 0.36), (0.058, 0.032, -0.32), M(sleeve_c, 0.7), b, rot=(0, 0.06, 0), bevel=0.01)
        return b

    # mine: navy suit sleeve, white cuff
    me_arm = sleeve_arm(root, "hand.me", skin_me, "#28324f", "#fafafa")
    hr_arm = sleeve_arm(root, "hand.hers", skin_hr, "#f6f2ec", "#fffaf2")
    g, front, mats = card_group(root, "hand.card", (0, 0, 0.074))
    W["card"] = g
    W["card_front"] = front
    W["card_mats"] = mats
    # the watch on my wrist, face to the camera, 1.5 cm proud of the wrist box's front
    wg = kit.empty("hand.watch", (0.051, -0.006, -0.083), root)
    box("hand.watch.strap", (0.062, 0.062, 0.07), (0, 0.032, 0), M("#3a2f2a", 0.6), wg, bevel=0.006)
    box("hand.watch.case", (0.078, 0.022, 0.082), (0, -0.008, 0), M("#c9ccd2", 0.3, spec=0.7), wg, bevel=0.006)
    W["watch_mats"] = {}
    for t in ("9:00", "9:11", "9:12", "9:13", "9:14"):
        p = work / f"watch_{t.replace(':', '')}.png"
        watch_png(p, t)
        W["watch_mats"][t] = img_mat(kit, f"watch {t}", p, 1.15, alpha=False)
    W["watch_face"] = kit.plane("hand.watch.face", (0.066, 0.066), (0, -0.0205, 0), W["watch_mats"]["9:11"], wg, rot=(math.pi / 2, 0, 0))
    bar = box("hand.watch.bar", (0.044, 0.002, 0.0045), (0, -0.0212, -0.0155), kit.emit("#7dffe0", 3.0, name="wbar"), wg)
    W["wbar"] = bar
    W["me_arm"], W["hers_arm"] = me_arm, hr_arm
    # an open palm with the ring box: the arm comes from the camera side, the box rests on the palm (no gripping)
    pg = kit.empty("hand.palm", (0, 0, 0), root)
    box("hand.palm.p", (0.088, 0.088, 0.022), (0, 0.0, -0.011), M(skin_me, 0.5), pg, bevel=0.008)
    for i in range(4):
        box(f"hand.palm.f{i}", (0.017, 0.045, 0.016), (-0.033 + i * 0.022, 0.066, -0.014), M(skin_me, 0.5), pg, bevel=0.005)
    box("hand.palm.th", (0.022, 0.05, 0.018), (-0.058, 0.008, -0.008), M(skin_me, 0.5), pg, rot=(0, 0, 0.5), bevel=0.005)
    box("hand.palm.w", (0.06, 0.1, 0.05), (0, -0.095, -0.03), M(skin_me, 0.5), pg, bevel=0.008)
    box("hand.palm.cuff", (0.076, 0.03, 0.074), (0, -0.16, -0.032), M("#fafafa", 0.6), pg, bevel=0.006)
    box("hand.palm.sl", (0.084, 0.3, 0.08), (0, -0.325, -0.034), M("#28324f", 0.7), pg, bevel=0.01)
    navy = M("#2b3a68", 0.45, spec=0.5)
    box("hand.palm.rb", (0.056, 0.05, 0.03), (0, 0.0, 0.015), navy, pg, bevel=0.006)
    lid = kit.empty("hand.palm.lidp", (0, 0.025, 0.03), pg)
    lid.rotation_euler = (math.radians(-100), 0, 0)
    box("hand.palm.lid", (0.056, 0.05, 0.012), (0, -0.025, 0.0), navy, lid, bevel=0.004)
    box("hand.palm.cush", (0.046, 0.04, 0.006), (0, 0.0, 0.031), M("#fffaf4", 0.9), pg)
    gold = M("#f2c14e", 0.25, spec=0.9)
    torus(kit, "hand.palm.ring", 0.0125, 0.0042, gold, (0, 0.0, 0.043), pg)
    kit.sphere("hand.palm.gem", 0.007, (0, 0.0, 0.056), M("#e8f8ff", 0.1, spec=1.0), pg, seg=8)
    pg.location = (0, 0, -0.01)
    W["palm"] = pg
    kit.light("hand.fill", "AREA", (ox + 0.2, oy - 1.6, 2.1), 8, "#fff0dc", rot=(math.radians(75), 0, math.radians(8)), size=1.2)


# ---------------------------------------------------------------------------- mail slot hall
def build_hall(kit, work, at):
    M, box = kit.plastic, kit.box
    ox, oy, _ = at("hall", 0, 0)
    box("hall.floor", (8, 8, 0.2), (ox, oy + 2, -0.1), kit.planks("#d9a76a", "#c8955a", 1.0, "X"))
    box("hall.wall", (8, 0.2, 3.2), (ox, oy + 4.1, 1.6), M("#fce8cc", 0.7))
    box("hall.wallL", (0.2, 8, 3.2), (ox - 4, oy + 2, 1.6), M("#f7dcbc", 0.7))
    box("hall.wallR", (0.2, 8, 3.2), (ox + 4, oy + 2, 1.6), M("#f7dcbc", 0.7))
    box("hall.door", (1.1, 0.08, 2.1), (ox, oy + 3.96, 1.05), M("#9cc59a", 0.5), bevel=0.02)
    box("hall.frame", (1.3, 0.04, 2.25), (ox, oy + 3.98, 1.1), M("#fafafa", 0.5))
    box("hall.slot", (0.34, 0.03, 0.07), (ox, oy + 3.9, 1.0), M("#9a8a2a", 0.3, spec=0.9))
    box("hall.slotd", (0.28, 0.02, 0.025), (ox, oy + 3.88, 1.0), M("#0c0c10", 0.8))
    box("hall.knob", (0.08, 0.05, 0.08), (ox + 0.4, oy + 3.88, 1.0), M("#d6a843", 0.3, spec=0.9), bevel=0.02)
    box("hall.mat", (1.4, 0.9, 0.03), (ox, oy + 3.2, 0.015), M("#ff8f7a", 0.8))
    box("hall.rug", (3.6, 2.2, 0.02), (ox, oy + 1.4, 0.01), M("#fff3d6", 0.9))
    kit.light("hall.fill", "AREA", (ox, oy - 0.5, 3.0), 260, "#fff0dc", rot=(math.radians(60), 0, 0), size=4)
    # the card that drops through: starts in the slot (hidden), lands on the mat
    cm = img_mat(kit, "dropcard", _png(work, "dropcard", lambda p: card_png(p, "sealed")), 0.95, alpha=False)
    cg = kit.empty("hall.drop", (ox, oy + 3.85, 1.0))
    box("hall.drop.b", (0.16, 0.012, 0.1), (0, 0, 0), M("#f4ead2", 0.6), cg, bevel=0.003)
    kit.plane("hall.drop.f", (0.16, 0.10), (0, -0.0075, 0), cm, cg, rot=(math.pi / 2, 0, 0))
    W["drop"] = cg
    W["drop_o"] = (ox, oy)
    cg.hide_render = True


def _png(work, name, fn):
    p = work / f"{name}.png"
    fn(p)
    return p


# ---------------------------------------------------------------------------- parking lot: two cars, one bay
def car(kit, name, loc, hexc, yaw=0.0):
    M = kit.plastic
    g = kit.empty(name, loc, None, (0, 0, math.radians(yaw)))
    kit.box(f"{name}.body", (1.8, 4.3, 0.7), (0, 0, 0.62), M(hexc, 0.3, spec=0.7), g, bevel=0.1)
    kit.box(f"{name}.cab", (1.62, 2.3, 0.62), (0, -0.2, 1.28), M(hexc, 0.3, spec=0.7), g, bevel=0.12)
    kit.box(f"{name}.glass", (1.66, 2.0, 0.42), (0, -0.2, 1.3), M("#5a7a96", 0.15, spec=0.9), g, bevel=0.06)
    kit.box(f"{name}.roof", (1.6, 2.1, 0.06), (0, -0.2, 1.62), M(hexc, 0.3, spec=0.7), g, bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1.4, 1.4):
            kit.cyl(f"{name}.wh{sx}{sy}", 0.34, 0.24, (sx * 0.9, sy, 0.34), M("#1c1c22", 0.8), g, rot=(0, math.pi / 2, 0), n=16)
        kit.box(f"{name}.hl{sx}", (0.32, 0.06, 0.16), (sx * 0.6, -2.17, 0.7), kit.emit("#fff6d0", 2.0, name="hl"), g)
    return g


def build_park(kit, work, at):
    M, box = kit.plastic, kit.box
    ox, oy, _ = at("park", 0, 0)
    box("park.ground", (30, 24, 0.2), (ox, oy + 4, -0.1), kit.texture("asphalt", 0.5, tint="#c9c2bd"))
    for i, x in enumerate((-4.0, -1.3, 1.3, 4.0)):
        box(f"park.line{i}", (0.12, 5.2, 0.015), (ox + x, oy + 2.6, 0.01), M("#fafafa", 0.7))
    box("park.stop", (3.4, 0.3, 0.2), (ox, oy + 5.5, 0.1), M("#ffd23f", 0.7))
    box("park.curb", (30, 1.2, 0.28), (ox, oy + 7.0, 0.14), M("#d8d2c8", 0.8))
    box("park.wall", (30, 0.4, 4.2), (ox, oy + 8.0, 2.1), M("#f6d7b0", 0.8))
    for i in range(4):
        box(f"park.win{i}", (1.6, 0.05, 1.5), (ox - 9 + i * 6, oy + 7.78, 2.3), M("#8fc2e0", 0.2, spec=0.8))
    car(kit, "park.carA", (ox - 2.2, oy + 3.0, 0), "#3f78d9", 0)
    car(kit, "park.carB", (ox + 2.2, oy + 3.0, 0), "#e4573d", 0)
    kit.light("park.fill", "AREA", (ox, oy - 3.0, 4.0), 300, "#fff0dc", rot=(math.radians(55), 0, 0), size=6)


# ---------------------------------------------------------------------------- two lawns and a fence
def build_lawn(kit, work, at):
    M, box = kit.plastic, kit.box
    ox, oy, _ = at("lawn", 0, 0)
    box("lawn.gL", (14, 20, 0.2), (ox - 7, oy + 4, -0.1), M("#8fd16e", 0.9, spec=0.1))
    box("lawn.gR", (14, 20, 0.2), (ox + 7, oy + 4, -0.1), M("#7cc660", 0.9, spec=0.1))
    for i in range(6):
        box(f"lawn.st{i}", (14, 0.9, 0.012), (ox - 7, oy - 4 + i * 2.6, 0.005), M("#9fdd7c", 0.9))
        box(f"lawn.sr{i}", (14, 0.9, 0.012), (ox + 7, oy - 4 + i * 2.6, 0.005), M("#6eb853", 0.9))
    fm = M("#fafafa", 0.55, spec=0.2)
    box("lawn.rail1", (0.07, 20, 0.07), (ox, oy + 4.0, 0.35), fm)
    box("lawn.rail2", (0.07, 20, 0.07), (ox, oy + 4.0, 0.75), fm)
    for k in range(60):
        box(f"lawn.pk{k}", (0.07, 0.09, 0.95), (ox, oy - 5.5 + k * 0.33, 0.47), fm, bevel=0.01)
    kit.prop("sub_building_type_c", (ox - 5.5, oy + 9.5, 0), rot=0, tint="#f6d9b8")
    kit.prop("sub_building_type_a", (ox + 5.5, oy + 9.5, 0), rot=0, tint="#cfe6f4")
    kit.prop("sub_tree_large", (ox - 10, oy + 4, 0), tint="#8fc58a")
    kit.prop("sub_tree_large", (ox + 10, oy + 5, 0), tint="#8fc58a")
    kit.light("lawn.fill", "AREA", (ox, oy - 3.0, 4.0), 280, "#fff0dc", rot=(math.radians(55), 0, 0), size=6)
    # the two hoses: eight drops each, moving in animate()
    wm = M("#8fd8ff", 0.1, spec=0.9)
    W["spray"] = []
    for side in (-1, 1):
        for i in range(10):
            W["spray"].append((side, i, kit.sphere(f"lawn.drop{side}{i}", 0.05, (ox, oy, -5), wm, seg=8)))
    W["lawn_o"] = (ox, oy)


# ---------------------------------------------------------------------------- airport gate
def build_gate(kit, work, at):
    M, box, cyl = kit.plastic, kit.box, kit.cyl
    ox, oy, _ = at("gate", 0, 0)
    box("gate.floor", (22, 20, 0.2), (ox, oy + 4, -0.1), kit.checker("#e7ecf0", "#dde4ea", 0.8, name="gate floor", rough=0.25))
    box("gate.back", (22, 0.3, 5.0), (ox, oy + 9.0, 2.5), M("#f4efe6", 0.7))
    # the big glass wall onto the apron, left half
    box("gate.sky", (11, 0.1, 3.6), (ox - 5.4, oy + 8.8, 2.4), kit.emit("#ffcfa6", 1.2, name="gate sky"))
    for i in range(5):
        box(f"gate.mull{i}", (0.14, 0.2, 3.7), (ox - 10.8 + i * 2.7, oy + 8.7, 2.4), M("#e9e3d8", 0.5))
    box("gate.mullT", (11, 0.2, 0.14), (ox - 5.4, oy + 8.7, 4.2), M("#e9e3d8", 0.5))
    box("gate.mullB", (11, 0.2, 0.14), (ox - 5.4, oy + 8.7, 0.6), M("#e9e3d8", 0.5))
    # a plane outside
    pm = M("#fbfbfb", 0.4, spec=0.5)
    box("gate.apron", (24, 16, 0.2), (ox - 4, oy + 18, 0.0), M("#b9b2ad", 0.9))
    cyl("gate.fus", 1.1, 14, (ox - 6, oy + 15, 2.2), pm, rot=(math.pi / 2, 0, math.radians(8)), n=20)
    box("gate.wing", (11, 2.0, 0.22), (ox - 6, oy + 14.3, 1.9), pm, bevel=0.05)
    box("gate.tail", (0.2, 1.8, 2.6), (ox - 6.9, oy + 21.5, 3.6), M("#e4573d", 0.4), bevel=0.04)
    # the sign: a navy board with a big 9, lit
    p = _png(work, "gate9", gate_png)
    box("gate.sign", (3.0, 0.12, 1.5), (ox + 3.6, oy + 8.6, 3.6), M("#1c3462", 0.5), bevel=0.04)
    kit.plane("gate.sign9", (2.8, 1.4), (ox + 3.6, oy + 8.5, 3.6), img_mat(kit, "gate9", p, 1.1, alpha=False), rot=(math.pi / 2, 0, 0))
    # the door the passengers go through: a dark doorway with a frame, desk beside it
    box("gate.door", (2.0, 0.2, 2.8), (ox + 3.6, oy + 8.85, 1.4), M("#4e6a86", 0.6))
    box("gate.doorf", (2.5, 0.12, 3.1), (ox + 3.6, oy + 8.78, 1.55), M("#fafafa", 0.5))
    box("gate.desk", (2.6, 0.9, 1.05), (ox + 0.4, oy + 7.2, 0.52), M("#c8946a", 0.5), bevel=0.04)
    box("gate.desktop", (2.8, 1.0, 0.06), (ox + 0.4, oy + 7.2, 1.08), M("#fafafa", 0.4))
    for r in range(2):
        for i in range(4):
            x = ox - 5.5 + i * 0.62
            y = oy + 1.2 + r * 1.8
            box(f"gate.seat{r}{i}", (0.55, 0.55, 0.12), (x, y, 0.5), M("#2f7fd0", 0.5), bevel=0.03)
            box(f"gate.seatb{r}{i}", (0.55, 0.1, 0.5), (x, y + 0.26, 0.78), M("#2f7fd0", 0.5), bevel=0.03)
            box(f"gate.seatl{r}{i}", (0.1, 0.1, 0.46), (x, y, 0.23), M("#8a929c", 0.4, spec=0.7))
    kit.light("gate.fill", "AREA", (ox, oy - 1.0, 4.4), 420, "#fff6ea", rot=(math.radians(60), 0, 0), size=8)


# ---------------------------------------------------------------------------- curb, fries and a shop front
def build_curb(kit, work, at):
    M, box = kit.plastic, kit.box
    ox, oy, _ = at("curb", 0, 0)
    box("curb.road", (30, 14, 0.2), (ox, oy - 4, -0.1), kit.texture("asphalt", 0.5, tint="#cfc8c2"))
    box("curb.side", (30, 10, 0.25), (ox, oy + 8.0, 0.0), kit.texture("concrete", 1.0, tint="#f1e6d6"))
    box("curb.edge", (30, 0.5, 0.28), (ox, oy + 3.0, 0.125), M("#e4dccf", 0.8))
    box("curb.shop", (30, 0.4, 4.6), (ox, oy + 12.0, 2.3), M("#f9d9c0", 0.8))
    for i, c in enumerate(("#ff8f7a", "#fafafa") * 5):
        box(f"curb.awn{i}", (1.5, 1.4, 0.14), (ox - 6.6 + i * 1.5, oy + 11.1, 3.3 - i % 1 * 0), M(c, 0.7), rot=(math.radians(-14), 0, 0))
    for i in range(3):
        box(f"curb.win{i}", (3.0, 0.05, 1.6), (ox - 5 + i * 5, oy + 11.78, 1.5), M("#8fc2e0", 0.2, spec=0.8))
    box("curb.door", (1.2, 0.06, 2.1), (ox + 8.5, oy + 11.78, 1.05), M("#6fb8a0", 0.5))
    # a paper tray with fries between them, on the curb
    tray = kit.empty("curb.tray", (ox + 0.4, oy + 3.3, 0.34))
    box("curb.tray.b", (0.3, 0.2, 0.12), (0, 0, 0), M("#e4573d", 0.6), tray, bevel=0.02)
    fm = M("#ffd966", 0.6)
    rnd = random.Random(5)
    for i in range(9):
        box(f"curb.fry{i}", (0.026, 0.026, 0.2), (rnd.uniform(-0.1, 0.1), rnd.uniform(-0.05, 0.05), 0.12), fm, tray, rot=(rnd.uniform(-.3, .3), rnd.uniform(-.3, .3), 0))
    W["lastfry"] = box("curb.lastfry", (0.026, 0.026, 0.22), (ox + 0.4, oy + 3.3, 0.5), fm, bevel=0.005)
    W["lastfry"].hide_render = True
    kit.light("curb.fill", "AREA", (ox, oy - 2.0, 4.0), 260, "#fff0dc", rot=(math.radians(55), 0, 0), size=6)


# ---------------------------------------------------------------------------- the wall calendar
def build_cal(kit, work, at):
    M, box = kit.plastic, kit.box
    ox, oy, _ = at("cal", 0, 0)
    box("cal.wall", (10, 0.3, 6), (ox, oy + 3.1, 2.4), M("#fbe0c4", 0.8))
    box("cal.floor", (10, 8, 0.2), (ox, oy, -0.1), M("#d8a66e", 0.7))
    box("cal.desk", (3.2, 1.2, 0.08), (ox - 3.0, oy + 2.4, 0.9), M("#c8946a", 0.5))
    W["cal_pages"] = []
    plain = img_mat(kit, "cal plain", _png(work, "cal0", lambda p: calendar_png(p, False)), 1.0, alpha=False)
    crossed = img_mat(kit, "cal crossed", _png(work, "cal1", lambda p: calendar_png(p, True)), 1.0, alpha=False)
    box("cal.board", (1.5, 0.04, 1.84), (ox, oy + 2.9, 2.4), M("#6b4a32", 0.6))
    for i in range(4):
        hinge = kit.empty(f"cal.hinge{i}", (ox, oy + 2.87 - i * 0.012, 3.3))
        pl = kit.plane(f"cal.page{i}", (1.4, 1.76), (0, 0, -0.88), plain if i == 0 else crossed, hinge, rot=(math.pi / 2, 0, 0))
        W["cal_pages"].append(hinge)
    # an orange pencil on a cord
    kit.light("cal.fill", "AREA", (ox, oy - 1.0, 4.4), 220, "#fff0dc", rot=(math.radians(60), 0, 0), size=4)


# ---------------------------------------------------------------------------- living room
def build_living(kit, work, at):
    M, box = kit.plastic, kit.box
    ox, oy, _ = at("living", 0, 0)
    box("liv.floor", (9, 9, 0.2), (ox, oy + 1, -0.1), kit.planks("#d9a76a", "#c8955a", 1.2, "X"))
    box("liv.wall", (9, 0.3, 3.2), (ox, oy + 3.6, 1.6), M("#bfe3d2", 0.8))
    box("liv.wallL", (0.3, 9, 3.2), (ox - 4.4, oy + 1, 1.6), M("#cdeadb", 0.8))
    box("liv.wallR", (0.3, 9, 3.2), (ox + 4.4, oy + 1, 1.6), M("#cdeadb", 0.8))
    box("liv.rug", (3.6, 2.4, 0.02), (ox, oy + 1.0, 0.01), M("#ff9f8a", 0.9))
    # sofa: seat, back, arms (blocky), facing -y
    sf = M("#ffb04a", 0.7, spec=0.15)
    box("liv.seat", (2.5, 0.95, 0.4), (ox, oy + 2.3, 0.3), sf, bevel=0.06)
    box("liv.back", (2.5, 0.28, 0.72), (ox, oy + 2.82, 0.76), sf, bevel=0.06)
    for sx in (-1, 1):
        box(f"liv.arm{sx}", (0.3, 1.0, 0.64), (ox + sx * 1.3, oy + 2.35, 0.5), sf, bevel=0.06)
    box("liv.pil1", (0.5, 0.18, 0.5), (ox - 0.8, oy + 2.6, 0.78), M("#fafafa", 0.8), bevel=0.06, rot=(0, 0.2, 0.3))
    box("liv.pil2", (0.5, 0.18, 0.5), (ox + 0.9, oy + 2.6, 0.78), M("#9cc59a", 0.8), bevel=0.06, rot=(0, -0.2, -0.3))
    kit.prop("houseplant_1", (ox - 3.6, oy + 3.0, 0), height=1.2)
    kit.prop("window_large1", (ox + 2.8, oy + 3.4, 1.6), rot=0, scale=1.6)
    kit.prop("bookshelf", (ox + 3.8, oy + 3.0, 0), rot=0, height=2.0, tint="#f0d8b8")
    box("liv.table", (1.2, 0.6, 0.06), (ox, oy - 0.6, 0.42), M("#c8946a", 0.5))
    box("liv.tablel", (1.0, 0.5, 0.4), (ox, oy - 0.6, 0.2), M("#a97850", 0.6))
    kit.light("liv.fill", "AREA", (ox, oy - 2.5, 3.2), 360, "#fff0dc", rot=(math.radians(60), 0, 0), size=5)


# ---------------------------------------------------------------------------- diner
def build_diner(kit, work, at):
    M, box = kit.plastic, kit.box
    ox, oy, _ = at("diner", 0, 0)
    box("din.floor", (10, 9, 0.2), (ox, oy + 1, -0.1), kit.checker("#2a2a30", "#f4f4f4", 1.4, name="din floor", rough=0.3))
    box("din.wall", (10, 0.3, 3.2), (ox, oy + 4.0, 1.6), M("#8fd8d0", 0.7))
    box("din.stripe", (10, 0.34, 0.25), (ox, oy + 3.99, 1.1), M("#ff6f7a", 0.6))
    box("din.wallL", (0.3, 9, 3.2), (ox - 5, oy + 1, 1.6), M("#a6e2da", 0.7))
    box("din.wallR1", (0.3, 3.0, 3.2), (ox + 5, oy + 3.0, 1.6), M("#a6e2da", 0.7))
    box("din.wallR2", (0.3, 3.0, 3.2), (ox + 5, oy - 2.0, 1.6), M("#a6e2da", 0.7))
    box("din.lintel", (0.3, 2.0, 1.1), (ox + 5, oy + 0.5, 2.65), M("#a6e2da", 0.7))
    # the booth: bench each side (x = -1.0 and +1.0), a table between
    red = M("#e8454f", 0.55, spec=0.3)
    box("din.table", (1.3, 1.0, 0.07), (ox, oy + 1.6, 0.76), M("#fafafa", 0.35, spec=0.5), bevel=0.02)
    box("din.tabl", (0.18, 0.18, 0.7), (ox, oy + 1.6, 0.36), M("#9aa2aa", 0.4, spec=0.7))
    for sx in (-1, 1):
        box(f"din.bench{sx}", (0.55, 1.5, 0.45), (ox + sx * 1.15, oy + 1.6, 0.225), red, bevel=0.05)
        box(f"din.back{sx}", (0.18, 1.5, 0.85), (ox + sx * 1.5, oy + 1.6, 0.85), red, bevel=0.05)
    box("din.bench3", (2.4, 0.5, 0.45), (ox, oy + 3.2, 0.225), red, bevel=0.05)
    for i in range(3):
        box(f"din.stool{i}", (0.4, 0.4, 0.08), (ox - 3.2 + i * 0.9, oy + 3.0, 0.72), red)
        box(f"din.stoolp{i}", (0.1, 0.1, 0.68), (ox - 3.2 + i * 0.9, oy + 3.0, 0.34), M("#9aa2aa", 0.4, spec=0.7))
    box("din.counter", (3.4, 0.7, 1.0), (ox - 2.2, oy + 3.8, 0.5), M("#fafafa", 0.4, spec=0.4), bevel=0.04)
    # the door: a frame in the right wall, a glass panel that swings about its hinge (the near edge)
    hinge = kit.empty("din.hinge", (ox + 4.98, oy - 0.5, 0))
    box("din.door", (0.06, 1.0, 2.1), (0, 0.5, 1.05), M("#c8e8f4", 0.15, spec=0.9), hinge, bevel=0.01)
    box("din.doorf", (0.1, 1.0, 0.08), (0, 0.5, 2.06), M("#fafafa", 0.4), hinge)
    box("din.doorh", (0.1, 0.05, 0.4), (-0.0, 0.88, 1.05), M("#c9ccd2", 0.3, spec=0.8), hinge)
    W["din_hinge"] = hinge
    kit.light("din.fill", "AREA", (ox, oy - 2.0, 3.2), 330, "#fff0dc", rot=(math.radians(60), 0, 0), size=5)


# ---------------------------------------------------------------------------- porch with a front door
def build_porch(kit, work, at):
    M, box = kit.plastic, kit.box
    ox, oy, _ = at("porch", 0, 0)
    box("por.yard", (20, 10, 0.2), (ox, oy - 4, -0.1), M("#8fd16e", 0.9, spec=0.1))
    box("por.path", (1.8, 8, 0.03), (ox, oy - 3.5, 0.015), M("#e4dccf", 0.8))
    box("por.step", (2.4, 1.0, 0.18), (ox, oy - 0.5, 0.09), M("#e4dccf", 0.8))
    # the house wall with the doorway (1.1 wide, 2.2 high): left, right, lintel
    wall = M("#ffe0a8", 0.8)
    box("por.wL", (4.2, 0.4, 3.6), (ox - 2.85, oy + 0.2, 1.8), wall)
    box("por.wR", (4.2, 0.4, 3.6), (ox + 2.85, oy + 0.2, 1.8), wall)
    box("por.wT", (1.5, 0.4, 1.4), (ox, oy + 0.2, 2.9), wall)
    box("por.frame", (1.58, 0.1, 0.1), (ox, oy - 0.05, 2.2), M("#fafafa", 0.5))
    for sx in (-1, 1):
        box(f"por.fr{sx}", (0.1, 0.1, 2.2), (ox + sx * 0.74, oy - 0.05, 1.1), M("#fafafa", 0.5))
        box(f"por.wlong{sx}", (0.4, 0.4, 3.6), (ox + sx * 6.0, oy + 0.2, 1.8), wall)
    box("por.roof", (12, 2.4, 0.3), (ox, oy - 0.9, 3.9), M("#e4573d", 0.6), bevel=0.05)
    # inside: a hall floor, back wall and side walls so the open door shows a room
    box("por.hfloor", (8, 6, 0.2), (ox, oy + 3.4, -0.1), kit.planks("#d9a76a", "#c8955a", 1.2, "Y"))
    box("por.hback", (8, 0.3, 3.4), (ox, oy + 6.5, 1.7), M("#cdeadb", 0.8))
    box("por.hL", (0.3, 6, 3.4), (ox - 4, oy + 3.4, 1.7), M("#d8f0e2", 0.8))
    box("por.hR", (0.3, 6, 3.4), (ox + 4, oy + 3.4, 1.7), M("#d8f0e2", 0.8))
    box("por.hrug", (1.5, 4.0, 0.02), (ox, oy + 3.4, 0.01), M("#ff9f8a", 0.9))
    kit.prop("window_large1", (ox - 2.5, oy + 6.3, 1.6), scale=1.6)
    kit.prop("houseplant_1", (ox + 3.0, oy + 5.5, 0), height=1.3)
    # the door, swung open against the inside wall (hinge on the left jamb)
    hinge = kit.empty("por.hinge", (ox - 0.7, oy + 0.15, 0))
    box("por.door", (1.35, 0.07, 2.15), (0.675, 0, 1.075), M("#4f9bd6", 0.45, spec=0.5), hinge, bevel=0.02)
    box("por.knob", (0.08, 0.1, 0.08), (1.2, -0.05, 1.0), M("#d6a843", 0.3, spec=0.9), hinge)
    hinge.rotation_euler = (0, 0, math.radians(100))
    W["por_hinge"] = hinge
    kit.light("por.fill", "AREA", (ox, oy - 3.5, 3.6), 340, "#fff0dc", rot=(math.radians(60), 0, 0), size=5)
    kit.light("por.in", "AREA", (ox, oy + 2.5, 3.0), 300, "#fff0dc", rot=(math.radians(-10), 0, 0), size=4)


# ---------------------------------------------------------------------------- backyard (party, then dinner a year on)
def build_yard(kit, work, at):
    M, box, cyl = kit.plastic, kit.box, kit.cyl
    ox, oy, _ = at("yard", 0, 0)
    box("yard.ground", (30, 24, 0.2), (ox, oy + 4, -0.1), M("#8fd16e", 0.9, spec=0.1))
    for k in range(7):
        kit.prop("nat_fence_planks", (ox - 9 + k * 3, oy + 10, 0), rot=0, height=1.6, tint="#fff0d8")
    kit.prop("sub_building_type_k", (ox - 6.5, oy + 14.5, 0), tint="#f6d9b8")
    kit.prop("sub_tree_large", (ox + 7, oy + 11, 0), tint="#8fc58a")
    kit.prop("sub_tree_large", (ox + 9, oy + 9, 0), tint="#8fc58a")
    # a long table, white cloth, with chairs; plates and dinner on it
    box("yard.table", (3.4, 1.1, 0.06), (ox, oy + 4.4, 0.78), M("#fafafa", 0.7), bevel=0.02)
    box("yard.cloth", (3.5, 1.2, 0.5), (ox, oy + 4.4, 0.5), M("#fff6e6", 0.85))
    for sx in (-1, 1):
        for i in range(3):
            x = ox + (i - 1) * 1.0
            box(f"yard.chs{sx}{i}", (0.46, 0.46, 0.05), (x, oy + 4.4 + sx * 1.0, 0.47), M("#d8a66e", 0.6), bevel=0.01)
            box(f"yard.chb{sx}{i}", (0.46, 0.05, 0.46), (x, oy + 4.4 + sx * 1.22, 0.72), M("#d8a66e", 0.6), bevel=0.01)
            box(f"yard.chl{sx}{i}", (0.4, 0.4, 0.45), (x, oy + 4.4 + sx * 1.0, 0.225), M("#b98a56", 0.7))
    dinner = kit.empty("yard.dinner", (ox, oy + 4.4, 0.82))
    for i in range(6):
        cyl(f"yard.plate{i}", 0.17, 0.02, ((i - 2.5) * 0.5, 0.25 if i % 2 else -0.25, 0.01), M("#fafafa", 0.3), dinner, n=14)
    cyl("yard.bowl", 0.22, 0.14, (0, 0, 0.07), M("#ff8f7a", 0.5), dinner, n=14)
    box("yard.loaf", (0.4, 0.14, 0.1), (0.7, 0, 0.05), M("#d9a76a", 0.7), dinner, bevel=0.03)
    W["dinner"] = dinner
    cake = kit.empty("yard.cake", (ox, oy + 4.4, 0.82))
    cyl("yard.cakeb", 0.28, 0.2, (0, 0, 0.1), M("#fff6e6", 0.6), cake, n=18)
    cyl("yard.cakec", 0.2, 0.12, (0, 0, 0.26), M("#ff9fb8", 0.6), cake, n=18)
    for i in range(5):
        a = i * 1.26
        box(f"yard.cand{i}", (0.02, 0.02, 0.1), (0.1 * math.cos(a), 0.1 * math.sin(a), 0.38), M("#ffe08a", 0.5), cake)
        kit.sphere(f"yard.flame{i}", 0.018, (0.1 * math.cos(a), 0.1 * math.sin(a), 0.45), kit.emit("#ffb02e", 6.0, name="flame"), cake, seg=6)
    W["cake"] = cake
    # balloons on strings
    balloons = kit.empty("yard.balloons", (ox, oy, 0))
    bc = ["#ff6f7a", "#ffd23f", "#4fb0ff", "#9cc59a", "#ff9fb8", "#b88cff"]
    for i in range(9):
        x = ox - 3.3 + i * 0.8
        y = oy + 6.6 + (i % 3) * 0.3
        z = 2.5 + (i % 4) * 0.25
        bpy_o = kit.sphere(f"yard.bal{i}", 0.34, (x, y, z), M(bc[i % 6], 0.2, spec=0.9), balloons, seg=14)
        bpy_o.scale = (1, 1, 1.18)
        box(f"yard.str{i}", (0.01, 0.01, z - 0.3), (x, y, (z - 0.3) / 2 + 0.05), M("#fafafa", 0.8), balloons)
    W["balloons"] = balloons
    # string lights low over the table
    bulb = kit.emit("#ffd98a", 6.0, name="bulb")
    for sx in (-1, 1):
        box(f"yard.pole{sx}", (0.1, 0.1, 3.0), (ox + sx * 3.4, oy + 4.4, 1.5), M("#d8c3a5", 0.7))
    for i in range(15):
        u = i / 14
        kit.sphere(f"yard.bulb{i}", 0.07, (ox - 3.4 + 6.8 * u, oy + 4.4, 3.0 - 0.45 * math.sin(math.pi * u)), bulb, seg=8)
    kit.light("yard.fill", "AREA", (ox, oy - 2.5, 4.0), 360, "#fff0dc", rot=(math.radians(55), 0, 0), size=6)


# ---------------------------------------------------------------------------- garage band
def build_garage(kit, work, at):
    M, box, cyl = kit.plastic, kit.box, kit.cyl
    ox, oy, _ = at("garage", 0, 0)
    box("gar.floor", (10, 9, 0.2), (ox, oy + 1, -0.1), kit.texture("concrete", 1.0, tint="#e8dccb"))
    box("gar.wall", (10, 0.3, 3.4), (ox, oy + 4.6, 1.7), M("#d8c2a0", 0.8))
    for i in range(9):
        box(f"gar.slat{i}", (4.4, 0.06, 0.2), (ox, oy + 4.4, 0.4 + i * 0.3), M("#f4efe6", 0.6))
    box("gar.wallL", (0.3, 9, 3.4), (ox - 5, oy + 1, 1.7), M("#e4cfae", 0.8))
    box("gar.wallR", (0.3, 9, 3.4), (ox + 5, oy + 1, 1.7), M("#e4cfae", 0.8))
    # the kit: kick drum facing us, two toms, a snare, a hi-hat and two cymbals, all around (0, 2.6)
    rm = M("#e4453d", 0.35, spec=0.6)
    sk = M("#f4f4f4", 0.3, spec=0.7)
    gm = M("#f2c14e", 0.25, spec=0.9)
    cyl("gar.kick", 0.5, 0.45, (ox, oy + 3.0, 0.5), rm, rot=(math.pi / 2, 0, 0), n=24)
    cyl("gar.kickf", 0.46, 0.02, (ox, oy + 2.76, 0.5), sk, rot=(math.pi / 2, 0, 0), n=24)
    for sx in (-0.34, 0.34):
        cyl(f"gar.tom{sx}", 0.2, 0.22, (ox + sx, oy + 2.95, 1.1), rm, rot=(0.25, 0, 0), n=18)
    cyl("gar.snare", 0.22, 0.16, (ox - 0.7, oy + 2.4, 0.78), sk, n=18)
    box("gar.snarel", (0.04, 0.04, 0.5), (ox - 0.7, oy + 2.4, 0.4), M("#8a929c", 0.4, spec=0.7))
    cyl("gar.floorTom", 0.26, 0.4, (ox + 0.8, oy + 2.55, 0.6), rm, n=18)
    for (x, y, z) in ((-0.8, 3.1, 1.5), (0.9, 3.1, 1.45), (-1.1, 2.6, 1.0)):
        cyl(f"gar.cym{x}", 0.32, 0.015, (ox + x, oy + y, z), gm, n=20, rot=(0.15, 0.1, 0))
        box(f"gar.cymp{x}", (0.03, 0.03, z), (ox + x, oy + y, z / 2), M("#8a929c", 0.4, spec=0.7))
    box("gar.stool", (0.38, 0.38, 0.06), (ox, oy + 3.7, 0.6), M("#2f3548", 0.5))
    box("gar.stoolp", (0.08, 0.08, 0.58), (ox, oy + 3.7, 0.3), M("#8a929c", 0.4, spec=0.7))
    # amps and a speaker stack behind, a strip of fairy lights on the wall
    for sx in (-3.2, 3.2):
        box(f"gar.amp{sx}", (1.0, 0.6, 1.2), (ox + sx, oy + 3.9, 0.6), M("#2a2a32", 0.6), bevel=0.04)
        cyl(f"gar.sp{sx}", 0.32, 0.02, (ox + sx, oy + 3.58, 0.7), M("#4a4a52", 0.7), rot=(math.pi / 2, 0, 0), n=18)
    bulb = kit.emit("#ffd98a", 5.0, name="bulb")
    for i in range(13):
        u = i / 12
        kit.sphere(f"gar.bulb{i}", 0.06, (ox - 4.4 + 8.8 * u, oy + 4.35, 3.0 - 0.3 * math.sin(math.pi * u)), bulb, seg=8)
    box("gar.chair", (0.5, 0.5, 0.05), (ox - 1.6, oy + 0.4, 0.45), M("#4fb0ff", 0.5))
    box("gar.chairb", (0.5, 0.05, 0.45), (ox - 1.6, oy + 0.65, 0.7), M("#4fb0ff", 0.5))
    box("gar.chairl", (0.4, 0.4, 0.43), (ox - 1.6, oy + 0.4, 0.215), M("#8a929c", 0.5))
    kit.light("gar.fill", "AREA", (ox, oy - 2.0, 3.2), 340, "#fff0dc", rot=(math.radians(60), 0, 0), size=5)


# ---------------------------------------------------------------------------- bowling lane
def build_bowl(kit, work, at):
    M, box, cyl = kit.plastic, kit.box, kit.cyl
    ox, oy, _ = at("bowl", 0, 0)
    box("bowl.floor", (14, 30, 0.2), (ox, oy + 10, -0.1), M("#7a5ad8", 0.5, spec=0.3))
    box("bowl.lane", (2.2, 22, 0.1), (ox, oy + 11.5, 0.0), M("#f0c888", 0.25, spec=0.7))
    for sx in (-1, 1):
        box(f"bowl.gut{sx}", (0.4, 22, 0.1), (ox + sx * 1.3, oy + 11.5, -0.04), M("#2a2a32", 0.5))
        box(f"bowl.rail{sx}", (0.5, 22, 0.35), (ox + sx * 1.75, oy + 11.5, 0.12), M("#ff5a6e", 0.45))
    box("bowl.appr", (6, 5.0, 0.05), (ox, oy + 0.0, 0.0), M("#e8a85a", 0.35, spec=0.6))
    box("bowl.foul", (2.2, 0.08, 0.01), (ox, oy + 2.55, 0.06), M("#fafafa", 0.5))
    pm, red = M("#fafafa", 0.25, spec=0.7), M("#e4453d", 0.4)
    rows = [(0, 22.0)] + [(sx, 22.3 + 0.35 * (1 - abs(sx))) for sx in ()]
    spots = []
    for r in range(4):
        for i in range(r + 1):
            spots.append((ox + (i - r / 2) * 0.3, oy + 22.0 + r * 0.26))
    for k, (x, y) in enumerate(spots):
        cyl(f"bowl.pin{k}", 0.06, 0.32, (x, y, 0.2), pm, n=12, r2=0.045)
        kit.sphere(f"bowl.pinh{k}", 0.05, (x, y, 0.4), pm, seg=8)
        cyl(f"bowl.pinr{k}", 0.058, 0.03, (x, y, 0.3), red, n=12)
    box("bowl.back", (14, 0.4, 5), (ox, oy + 25, 2.5), M("#5a3cc0", 0.7))
    box("bowl.neon", (6, 0.1, 0.3), (ox, oy + 24.7, 3.4), kit.emit("#ff7ad9", 3.0, name="neon"))
    box("bowl.neon2", (6, 0.1, 0.3), (ox, oy + 24.7, 3.0), kit.emit("#6fe8ff", 3.0, name="neon2"))
    for i, c in enumerate(("#ff5a6e", "#4fb0ff", "#ffd23f")):
        kit.sphere(f"bowl.ball{i}", 0.12, (ox - 2.4 + i * 0.3, oy + 1.2, 0.12), M(c, 0.15, spec=0.9))
    box("bowl.backA", (14, 0.4, 5), (ox, oy - 4.5, 2.5), M("#5a3cc0", 0.7))
    box("bowl.neonA", (6, 0.1, 0.3), (ox, oy - 4.25, 3.4), kit.emit("#ff7ad9", 3.0, name="neon"))
    box("bowl.rack", (1.2, 0.5, 0.1), (ox - 2.1, oy + 1.2, 0.0), M("#2a2a32", 0.6))
    kit.light("bowl.fill", "AREA", (ox, oy + 6.0, 4.0), 700, "#fff0f6", rot=(math.radians(0), 0, 0), size=10)
    kit.light("bowl.fill2", "AREA", (ox, oy + 14.0, 4.5), 500, "#fff6ea", rot=(0, 0, 0), size=10)


# ---------------------------------------------------------------------------- beach
def build_beach(kit, work, at):
    M, box, cyl = kit.plastic, kit.box, kit.cyl
    ox, oy, _ = at("beach", 0, 0)
    box("beach.sand", (60, 30, 0.2), (ox, oy, -0.1), M("#f7dcab", 0.95, spec=0.05))
    box("beach.wet", (60, 3, 0.12), (ox, oy + 9.5, -0.07), M("#d8b88a", 0.6, spec=0.3))
    box("beach.sea", (140, 80, 0.3), (ox, oy + 51, -0.12), kit.emit("#2db0dc", 1.1, name="sea"))
    for i in range(6):
        box(f"beach.wave{i}", (30, 0.5, 0.04), (ox - 10 + i * 6, oy + 11.2 + (i % 2) * 1.6, -0.01), M("#fafafa", 0.6))
    # umbrella and towels
    cyl("beach.pole", 0.04, 2.3, (ox + 1.0, oy + 7.2, 1.15), M("#e4dccf", 0.6))
    cyl("beach.canopy", 1.5, 0.45, (ox + 1.0, oy + 7.2, 2.3), M("#ff5a6e", 0.6), n=16, r2=0.05)
    box("beach.towel1", (1.0, 2.0, 0.02), (ox - 2.6, oy + 4.5, 0.01), M("#4fb0ff", 0.9))
    box("beach.towel2", (1.0, 2.0, 0.02), (ox + 0.2, oy + 7.5, 0.01), M("#ffd23f", 0.9))
    cyl("beach.ball", 0.25, 0.5, (ox - 1.0, oy + 7.0, 0.25), M("#ff9fb8", 0.3), n=14)
    kit.sphere("beach.ball2", 0.25, (ox - 1.0, oy + 7.2, 0.25), M("#ff9fb8", 0.2, spec=0.8))
    kit.light("beach.fill", "AREA", (ox, oy - 2.0, 4.0), 280, "#fff0dc", rot=(math.radians(55), 0, 0), size=6)


# ---------------------------------------------------------------------------- moving van
def build_van(kit, work, at):
    M, box, cyl = kit.plastic, kit.box, kit.cyl
    ox, oy, _ = at("van", 0, 0)
    box("van.road", (40, 24, 0.2), (ox, oy + 4, -0.1), kit.texture("asphalt", 0.5, tint="#cfc8c2"))
    box("van.side", (40, 6, 0.22), (ox, oy + 14, 0.0), kit.texture("concrete", 1.0, tint="#f1e6d6"))
    # a box truck, rear toward us: the cargo box with its back open, a cab behind it
    wh = M("#fafafa", 0.35, spec=0.5)
    box("van.cfloor", (2.6, 5.0, 0.15), (ox, oy + 5.2, 0.98), wh, bevel=0.03)
    box("van.croof", (2.6, 5.0, 0.15), (ox, oy + 5.2, 3.0), wh, bevel=0.03)
    for sx in (-1, 1):
        box(f"van.cside{sx}", (0.15, 5.0, 2.0), (ox + sx * 1.225, oy + 5.2, 1.99), wh, bevel=0.03)
    box("van.cfront", (2.6, 0.15, 2.0), (ox, oy + 7.62, 1.99), M("#caa87c", 0.8), bevel=0.03)
    box("van.cab", (2.4, 1.8, 1.8), (ox, oy + 8.6, 1.35), M("#4fb0ff", 0.35, spec=0.5), bevel=0.06)
    box("van.chassis", (2.0, 8.2, 0.3), (ox, oy + 6.0, 0.55), M("#2a2a32", 0.6))
    for sy in (3.8, 8.4):
        for sx in (-1, 1):
            cyl(f"van.wh{sy}{sx}", 0.45, 0.3, (ox + sx * 1.15, oy + sy, 0.45), M("#1c1c22", 0.8), rot=(0, math.pi / 2, 0), n=16)
    # the open rear: a dark interior and stacked moving boxes inside and on the ground
    cardb = M("#c99a5e", 0.8)
    for i, (x, y, z, s) in enumerate(((-0.6, 3.6, 0, 0.7), (0.3, 3.7, 0, 0.6), (-0.4, 3.6, 1, 0.6), (0.5, 4.3, 0, 0.7), (-0.5, 4.5, 0, 0.8))):
        box(f"van.box{i}", (s, s, s * 0.9), (ox + x, oy + y, 1.06 + s * 0.45 + z * 0.65), cardb, bevel=0.01)
    box("van.crate1", (0.6, 0.6, 0.5), (ox + 3.0, oy + 2.0, 0.25), cardb, bevel=0.01)
    box("van.crate2", (0.6, 0.6, 0.5), (ox + 3.2, oy + 2.2, 0.75), M("#d8a86e", 0.8), bevel=0.01)
    kit.light("van.fill", "AREA", (ox, oy - 3.0, 4.0), 300, "#fff0dc", rot=(math.radians(55), 0, 0), size=6)


# ---------------------------------------------------------------------------- park bench in the rain
def umbrella(kit, name, loc, hexc, r=1.0):
    M = kit.plastic
    g = kit.empty(name, loc)
    kit.cyl(f"{name}.stick", 0.02, 1.2, (0, 0, -0.5), M("#2a2a32", 0.5), g)
    kit.cyl(f"{name}.dome", r, 0.4, (0, 0, 0.1), M(hexc, 0.4, spec=0.5), g, n=18, r2=0.06)
    return g


def build_bench(kit, work, at):
    M, box = kit.plastic, kit.box
    ox, oy, _ = at("bench", 0, 0)
    box("bn.ground", (30, 24, 0.2), (ox, oy + 4, -0.1), M("#7fc19a", 0.9, spec=0.2))
    box("bn.path", (30, 3.0, 0.04), (ox, oy + 0.0, 0.01), M("#dcd2c2", 0.5, spec=0.3))
    wd = M("#b98a56", 0.6)
    box("bn.seat", (2.0, 0.55, 0.07), (ox, oy + 3.3, 0.5), wd, bevel=0.02)
    box("bn.back", (2.0, 0.07, 0.5), (ox, oy + 3.62, 0.88), wd, bevel=0.02)
    for sx in (-1, 1):
        box(f"bn.leg{sx}", (0.08, 0.55, 0.5), (ox + sx * 0.9, oy + 3.3, 0.25), M("#2a2a32", 0.5))
    umbrella(kit, "bn.u1", (ox, oy + 3.3, 2.3), "#ff5a6e", 1.05)
    umbrella(kit, "bn.u2", (ox - 0.79, oy + 6.5, 2.35), "#4fb0ff", 0.95)
    kit.prop("sub_tree_large", (ox - 6, oy + 9, 0), tint="#7fc19a")
    kit.prop("sub_tree_large", (ox + 5, oy + 10, 0), tint="#7fc19a")
    kit.prop("sub_tree_small", (ox + 8, oy + 8, 0), tint="#8fc58a")
    kit.prop("sub_tree_large", (ox - 9, oy + 12, 0), tint="#8fc58a")
    kit.light("bn.fill", "AREA", (ox, oy - 2.0, 4.0), 300, "#e8f0ff", rot=(math.radians(55), 0, 0), size=6)


# ---------------------------------------------------------------------------- shop street (Maya rushes past)
def build_street(kit, work, at):
    M, box = kit.plastic, kit.box
    ox, oy, _ = at("street", 0, 0)
    box("st.road", (50, 8, 0.2), (ox, oy - 3, -0.1), kit.texture("asphalt", 0.5, tint="#cfc8c2"))
    box("st.walk", (50, 7, 0.16), (ox, oy + 4.5, -0.02), kit.texture("concrete", 1.0, tint="#f1e6d6"))
    box("st.edge", (50, 0.4, 0.2), (ox, oy + 1.0, 0.0), M("#e4dccf", 0.8))
    shopc = ["#ffd9a8", "#ffb8c0", "#bfe6d6", "#fff0b0", "#c8d8f8"]
    for i in range(6):
        x = ox - 12.5 + i * 5.0
        box(f"st.shop{i}", (5.0, 0.5, 5.0), (x, oy + 8.2, 2.5), M(shopc[i % 5], 0.8))
        box(f"st.win{i}", (3.2, 0.06, 2.0), (x, oy + 7.92, 1.6), M("#8fc2e0", 0.2, spec=0.8))
        box(f"st.awn{i}", (4.2, 1.2, 0.12), (x, oy + 7.3, 3.1), M(["#ff5a6e", "#4fb0ff", "#ffd23f"][i % 3], 0.6), rot=(math.radians(-14), 0, 0))
    kit.prop("sub_tree_small", (ox - 4, oy + 2.0, 0), tint="#8fc58a")
    kit.prop("sub_tree_small", (ox + 6, oy + 2.0, 0), tint="#8fc58a")
    kit.light("st.fill", "AREA", (ox, oy - 3.0, 4.0), 300, "#fff0dc", rot=(math.radians(55), 0, 0), size=6)


# ---------------------------------------------------------------------------- the window (rain) room
def build_win(kit, work, at):
    M, box = kit.plastic, kit.box
    ox, oy, _ = at("win", 0, 0)
    box("win.floor", (9, 8, 0.2), (ox, oy + 1, -0.1), kit.planks("#d9a76a", "#c8955a", 1.2, "X"))
    box("win.wall", (9, 0.3, 3.4), (ox, oy + 3.0, 1.7), M("#fbe0c4", 0.8))
    # the window: a lit sky pane in a white frame, centred behind where I stand
    box("win.pane", (2.6, 0.06, 1.9), (ox, oy + 2.84, 1.7), kit.emit("#d4e6f6", 1.6, name="win sky"))
    for (w, h, x, z) in ((2.9, 0.12, 0, 2.72), (2.9, 0.12, 0, 0.68), (0.12, 2.1, -1.4, 1.7), (0.12, 2.1, 1.4, 1.7), (0.08, 2.0, 0, 1.7)):
        box(f"win.fr{x}{z}", (w, 0.14, h), (ox + x, oy + 2.8, z), M("#fafafa", 0.5))
    box("win.sill", (3.2, 0.3, 0.08), (ox, oy + 2.72, 0.62), M("#fafafa", 0.5))
    kit.prop("houseplant_1", (ox - 2.8, oy + 2.4, 0), height=1.2)
    box("win.rug", (3.0, 2.0, 0.02), (ox, oy + 0.8, 0.01), M("#9cc59a", 0.9))
    kit.light("win.fill", "AREA", (ox, oy - 1.0, 3.0), 300, "#f2f6ff", rot=(math.radians(60), 0, 0), size=4)


# ---------------------------------------------------------------------------- props people carry
def build_helds(kit, work):
    M, box = kit.plastic, kit.box
    W["held"] = {}

    def grp(name):
        g = kit.empty(f"held.{name}", (0, 0, -50))
        g.hide_render = True
        W["held"][name] = g
        return g

    # a card, drawn bigger than life so it reads: 0.2 x 0.125
    g = grp("card")
    box("held.card.b", (0.2, 0.006, 0.125), (0, 0, 0), M("#f4ead2", 0.6), g, bevel=0.002)
    pm = img_mat(kit, "held card mine", _png(work, "heldcard", lambda p: card_png(p, "mine")), 0.95, alpha=False)
    kit.plane("held.card.f", (0.2, 0.125), (0, -0.0045, 0), pm, g, rot=(math.pi / 2, 0, 0))
    bm = img_mat(kit, "held card back", _png(work, "heldcardb", lambda p: card_png(p, "back")), 0.95, alpha=False)
    kit.plane("held.card.k", (0.2, 0.125), (0, 0.0045, 0), bm, g, rot=(math.pi / 2, 0, math.pi))
    # hers (a pink glyph row), same size
    g = grp("cardhers")
    box("held.cardh.b", (0.2, 0.006, 0.125), (0, 0, 0), M("#f4ead2", 0.6), g, bevel=0.002)
    pm = img_mat(kit, "held card hers", _png(work, "heldcardh", lambda p: card_png(p, "hers")), 0.95, alpha=False)
    kit.plane("held.cardh.f", (0.2, 0.125), (0, -0.0045, 0), pm, g, rot=(math.pi / 2, 0, 0))
    kit.plane("held.cardh.k", (0.2, 0.125), (0, 0.0045, 0), bm, g, rot=(math.pi / 2, 0, math.pi))
    # a bouquet: stems, a ball of flowers and leaves
    g = grp("bouquet")
    box("held.bq.stem", (0.04, 0.04, 0.3), (0, 0, -0.1), M("#6fae6c", 0.7), g)
    rnd = random.Random(2)
    cols = ["#ff9fb8", "#fafafa", "#ffd23f", "#ff6f9a", "#fafafa"]
    for i in range(14):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.0, 0.13)
        kit.sphere(f"held.bq.f{i}", 0.06, (r * math.cos(a), r * math.sin(a) * 0.6, 0.1 + rnd.uniform(-0.04, 0.07)), M(cols[i % 5], 0.7), g, seg=8)
    for i in range(5):
        box(f"held.bq.l{i}", (0.1, 0.03, 0.14), (0.14 * math.cos(i * 1.26), 0.1 * math.sin(i * 1.26), 0.02), M("#7bb07a", 0.7), g, rot=(0.4, 0, i))
    # swatches: a fan of coloured strips
    g = grp("swatches")
    for i, c in enumerate(("#ff9fb8", "#ffd23f", "#9cc59a", "#4fb0ff", "#b88cff", "#ff8f7a")):
        box(f"held.sw{i}", (0.05, 0.01, 0.28), (0.0, 0.0, 0.0), M(c, 0.8), g, rot=(0, math.radians(-40 + i * 16), 0))
    # a remote, a phone
    g = grp("remote")
    box("held.rem", (0.05, 0.03, 0.18), (0, 0, 0), M("#2a2a32", 0.5), g, bevel=0.01)
    box("held.rem.btn", (0.03, 0.01, 0.03), (0, -0.018, 0.04), M("#ff5a6e", 0.5), g)
    g = grp("phone")
    box("held.ph", (0.07, 0.01, 0.14), (0, 0, 0), M("#2a2a32", 0.5), g, bevel=0.01)
    box("held.ph.s", (0.06, 0.004, 0.12), (0, -0.007, 0), kit.emit("#aee4ff", 3.0, name="phone scr"), g)
    g = grp("bowlball")
    kit.sphere("held.bb", 0.13, (0, 0, 0), M("#c23a9a", 0.15, spec=0.9), g, seg=14)
    for i, (hx, hz) in enumerate(((-0.04, 0.09), (0.04, 0.09), (0.0, 0.04))):
        kit.sphere(f"held.bbh{i}", 0.018, (hx, -0.12, hz), M("#1a1020", 0.5), g, seg=6)
    # moving boxes
    g = grp("movebox")
    box("held.mb", (0.55, 0.45, 0.4), (0, 0, 0), M("#c99a5e", 0.8), g, bevel=0.01)
    box("held.mb.tape", (0.08, 0.46, 0.402), (0, 0, 0), M("#e8d8b8", 0.8), g)
    # the ring box (closed) for the roof, in a hand at hip height
    # fries
    g = grp("fries")
    box("held.fr.b", (0.2, 0.14, 0.09), (0, 0, 0), M("#e4573d", 0.6), g, bevel=0.015)
    for i in range(6):
        box(f"held.fr.f{i}", (0.022, 0.022, 0.15), (-0.07 + i * 0.028, 0, 0.1), M("#ffd966", 0.6), g, rot=(0.1 * (i % 3 - 1), 0.08 * (i % 2), 0))
    # a wrapped gift? no. A white sheet of paper (the dinner card holder)? no.


# ------------------------------------------------------------------------------------------------ animate
def _interp_cue(tl, name, t, key, default):
    """The value of a keyed number between cues of `name`: held before the first, linear to the next."""
    cs = cue_list(tl, name)
    if not cs:
        return default
    if t <= cs[0]["t"]:
        return cs[0][key]
    for a, b in zip(cs, cs[1:]):
        if t < b["t"]:
            u = (t - a["t"]) / max(1e-6, b["t"] - a["t"])
            return a[key] + (b[key] - a[key]) * u
    return cs[-1][key]


def _attach(kit):
    """Parts that belong to a character and so can only be made once the cast exists (first frame of animate)."""
    if W.get("attached"):
        return
    W["attached"] = True
    M, box = kit.plastic, kit.box
    R, H = 0.62, 1.2
    for nm in ("nate", "nate_s"):
        ch = rig.CHARS.get(nm)
        if ch is None:
            continue
        hg = bpy.data.objects.get(f"{nm}.headg")
        bm = M("#3a2a20", 0.7)
        # a short beard: a chin cap and two cheek strips, proud of the face
        box(f"{nm}.beardc", (1.0, 0.34, 0.34), (0, -R + 0.14, -0.56), bm, hg, bevel=0.1)
        for sx in (-1, 1):
            box(f"{nm}.beards{sx}", (0.22, 0.4, 0.58), (sx * (R - 0.08), -R + 0.3, -0.34), bm, hg, bevel=0.08)
    ch = rig.CHARS.get("maya_w")
    if ch is not None:
        hips = bpy.data.objects.get("maya_w.hips")
        sk = M("#fffaf2", 0.55, spec=0.3)
        box("maya_w.skirt", (2.2, 1.32, 1.85), (0, 0, -0.98), sk, hips, bevel=0.14)
        box("maya_w.skirt2", (2.5, 1.5, 0.5), (0, 0, -1.55), sk, hips, bevel=0.14)
        box("maya_w.sash", (2.04, 1.06, 0.2), (0, 0, -0.1), M("#9cc59a", 0.6), hips, bevel=0.04)
        # a veil down her back
        hg = bpy.data.objects.get("maya_w.headg")
        box("maya_w.veil", (1.1, 0.12, 1.9), (0, R + 0.08, -0.55), M("#fffaf2", 0.7), hg, bevel=0.04)
    # a watch on my left wrist for the family photo and the hug (face forward, proud of the arm)
    for nm in ("me", "me_d"):
        arm = bpy.data.objects.get(f"{nm}.arm-1")
        if arm is not None:
            box(f"{nm}.watch", (0.5, 0.12, 0.5), (0, -0.54, -1.5), M("#c9ccd2", 0.3, spec=0.7), arm, bevel=0.03)
            kit.plane(f"{nm}.watchf", (0.34, 0.34), (0, -0.62, -1.5), W["watch_mats"]["9:14"], arm, rot=(math.pi / 2, 0, 0))


def animate(kit, story, tl, t, ctx):
    _attach(kit)
    shot = shot_at(tl, t)
    cam = kit.OBJ["cam"]

    # ---- the rule marker: sits at the same spot of the picture in every shot (camera-parented)
    if "shots_spec" not in W:
        W["shots_spec"] = polish.cam_specs(story, tl, polish.spec(story))
    lens = bl_story.cam_at(W["shots_spec"][shot["id"]], shot, t, rig.CHARS, tl)[2]
    dist = 0.9
    H = dist * 12.0 / lens
    p = _interp_cue(tl, "ring", t, "p", 0.25)
    k = max(0, min(16, int(round(p * 16))))
    ins = W["inset"]
    ins.data.materials[0] = W["inset_mats"][k]
    side = 0.34 * H
    ins.location = (-0.325 * H, 0.735 * H, -dist)
    ins.scale = (side, side, 1)

    # ---- the hand stage
    hand = cue_at(tl, "hand", t).get("who", "me")
    W["me_arm"].hide_render = hand != "me"
    for ob in W["me_arm"].children_recursive:
        ob.hide_render = hand != "me"
    for ob in [W["hers_arm"]] + list(W["hers_arm"].children_recursive):
        ob.hide_render = hand != "hers"
    for ob in [W["palm"]] + list(W["palm"].children_recursive):
        ob.hide_render = hand != "palm"
    palm_on = hand == "palm"
    for ob in [W["card"]] + list(W["card"].children_recursive):
        ob.hide_render = palm_on
    wg = bpy.data.objects["hand.watch"]
    for ob in [wg] + list(wg.children_recursive):
        ob.hide_render = hand != "me"
    cd = cue_at(tl, "card", t)
    face = cd.get("face", "mine") if cd else "mine"
    if hand == "hers" and face == "mine":
        face = "hers"
    W["card_front"].data.materials[0] = W["card_mats"][face]
    # the turn: eased over dur from the previous cue's rz
    cs = [c for c in cue_list(tl, "card")]
    rz = 0.0
    prev = 0.0
    for c in cs:
        if "rz" not in c:
            continue
        if t >= c["t"] + c.get("dur", 0.01):
            prev = c["rz"]
            rz = prev
        elif t > c["t"]:
            rz = prev + (c["rz"] - prev) * ss((t - c["t"]) / c.get("dur", 0.01))
            break
        else:
            break
    W["card"].rotation_euler = (0, 0, math.radians(rz))
    W["card"].location = (0, 0, 0.074)
    # a faint tremble when the cue says so (the ring box, the shaking hands)
    shake = cue_at(tl, "tremble", t).get("amp", 0.0)
    tr = shake * 0.004
    if shake:
        W["palm"].location = (tr * math.sin(t * 38), tr * math.sin(t * 31 + 1), -0.01 + tr * 0.6 * math.sin(t * 43))
        W["me_arm"].location = (tr * math.sin(t * 38), 0, tr * math.sin(t * 29))
    else:
        W["palm"].location = (0, 0, -0.01)
        W["me_arm"].location = (0, 0, 0)
    wt = cue_at(tl, "watch", t).get("time", "9:11")
    W["watch_face"].data.materials[0] = W["watch_mats"][wt]
    wb = cue_at(tl, "wbar", t)
    if wb:
        u = min(1.0, max(0.0, (t - wb["t"]) / max(1e-6, wb.get("dur", 1.0))))
        pb = wb["p0"] + (wb["p1"] - wb["p0"]) * u
    else:
        pb = 0.0
    W["wbar"].hide_render = pb <= 0.01 or hand != "me"
    W["wbar"].scale = (max(0.01, pb), 1, 1)
    W["wbar"].location = (-0.022 * (1 - pb), 0, 0)

    # ---- the mail slot card
    dc = cue_list(tl, "drop")
    g = W["drop"]
    if dc and t >= dc[0]["t"]:
        u = t - dc[0]["t"]
        ox, oy = W["drop_o"]
        g.hide_render = u > 3.5
        fall = min(1.0, u / 0.55)
        z = 1.0 - (1.0 - 0.06) * fall * fall
        g.location = (ox, oy + 3.85 - 0.25 * fall - 0.0, z)
        g.rotation_euler = (math.radians(-12 * fall), 0, math.radians(10 * ss(u / 0.5)))
        if fall >= 1.0:
            g.location = (ox, oy + 3.55, 0.07)
            g.rotation_euler = (math.radians(-80), 0, math.radians(10))
    else:
        g.hide_render = True

    # ---- the calendar: page i flips up and away
    for i, hinge in enumerate(W["cal_pages"]):
        fl = [c for c in cue_list(tl, "calflip") if c.get("i") == i]
        if fl and t >= fl[0]["t"]:
            u = min(1.0, (t - fl[0]["t"]) / 0.4)
            hinge.rotation_euler = (-math.radians(175) * ss(u), 0, 0)
            hinge.hide_render = u >= 1.0
            for ob in hinge.children:
                ob.hide_render = u >= 1.0
        else:
            hinge.rotation_euler = (0, 0, 0)
            hinge.hide_render = False
            for ob in hinge.children:
                ob.hide_render = False

    # ---- doors
    dd = cue_at(tl, "door", t) if False else None
    for did, hinge, closed, opened in (("diner", W["din_hinge"], 0.0, -95.0),):
        _door(tl, t, did, hinge, closed, opened)

    # ---- named groups
    for gid, grp_ in (("balloons", W["balloons"]), ("cake", W["cake"]), ("dinner", W["dinner"])):
        cs = [c for c in cue_list(tl, "show") if c.get("id") == gid]
        on = bool(cs[-1:] and False)
        on = False
        for c in cs:
            if c["t"] <= t + 1e-9:
                on = bool(c["on"])
        for ob in [grp_] + list(grp_.children_recursive):
            ob.hide_render = not on
    lf = [c for c in cue_list(tl, "show") if c.get("id") == "lastfry"]
    W["lastfry"].hide_render = not (lf and any(c["t"] <= t and c["on"] for c in lf[-1:]))

    # ---- the sprinklers
    ox, oy = W["lawn_o"]
    for side, i, ob in W["spray"]:
        u = (t * 1.3 + i / 10.0) % 1.0
        sx0 = ox + side * 1.5
        x = sx0 + side * 2.6 * u
        z = 1.05 + 0.9 * u - 1.9 * u * u
        ob.location = (x, oy + 2.2, max(0.02, z))

    # ---- petals over the roof
    pc = cue_at(tl, "petals", t)
    pon = bool(pc.get("on")) if pc else False
    for ob, x0, y0, ph, per in W["petals"]:
        if not pon:
            ob.hide_render = True
            continue
        u = ((t - pc["t"]) / per + ph) % 1.0
        ob.hide_render = False
        ob.location = (x0 + 0.5 * math.sin(u * 6 + ph * 9), y0 + 0.3 * math.cos(u * 5 + ph * 7), 3.4 - 3.3 * u)
        ob.rotation_euler = (u * 9 + ph, u * 7, u * 5)

    # ---- sitting
    for ch_name, ch in rig.CHARS.items():
        cs = [c for c in cue_list(tl, "sit") if c.get("who") == ch_name]
        cur = None
        for c in cs:
            if c["t"] <= t + 1e-9:
                cur = c
        if cur and cur.get("on", True) and not ch.root.hide_render:
            ch.root.location.z += cur.get("z", 0.62) - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{ch_name}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
            for hinge, sx in ch.coat:
                hinge.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)

    # ---- held props
    _held(tl, t)
    return {}


def _door(tl, t, did, hinge, closed, opened):
    cs = [c for c in cue_list(tl, "door") if c.get("id") == did]
    ang = closed
    prev = closed
    for c in cs:
        tgt = opened if c["open"] else closed
        dur = c.get("dur", 0.5)
        if t >= c["t"] + dur:
            prev = tgt
            ang = tgt
        elif t > c["t"]:
            ang = prev + (tgt - prev) * ss((t - c["t"]) / dur)
            break
        else:
            break
    hinge.rotation_euler = (0, 0, math.radians(ang))


def _held(tl, t):
    cs_all = cue_list(tl, "held")
    objs = {}
    for c in cs_all:
        objs.setdefault(c["obj"], []).append(c)
    for name, g in W["held"].items():
        cs = objs.get(name, [])
        cur_i = -1
        for i, c in enumerate(cs):
            if c["t"] <= t + 1e-9:
                cur_i = i
        if cur_i < 0 or not cs[cur_i].get("on", True):
            g.hide_render = True
            for ob in g.children_recursive:
                ob.hide_render = True
            continue
        c = cs[cur_i]
        who = rig.CHARS.get(c["who"])
        if who is None or who.root.hide_render:
            g.hide_render = True
            for ob in g.children_recursive:
                ob.hide_render = True
            continue
        off = list(c["off"])
        yaw_off = c.get("yaw", 0.0)
        tilt = c.get("tilt", 0.0)
        dur = c.get("dur", 0.0)
        if cur_i > 0 and dur > 0 and cs[cur_i - 1].get("on", True) and cs[cur_i - 1]["who"] == c["who"] and t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            po = cs[cur_i - 1]["off"]
            off = [po[j] + (off[j] - po[j]) * u for j in range(3)]
            yaw_off = cs[cur_i - 1].get("yaw", 0.0) + (yaw_off - cs[cur_i - 1].get("yaw", 0.0)) * u
            tilt = cs[cur_i - 1].get("tilt", 0.0) + (tilt - cs[cur_i - 1].get("tilt", 0.0)) * u
        ry = who.root.rotation_euler[2]
        lx, ly = off[0], off[1]
        wx = who.root.location.x + lx * math.cos(ry) - ly * math.sin(ry)
        wy = who.root.location.y + lx * math.sin(ry) + ly * math.cos(ry)
        g.location = (wx, wy, who.root.location.z + off[2])
        g.rotation_euler = (math.radians(tilt), 0, ry + math.radians(yaw_off))
        sc = c.get("s", 1.0)
        g.scale = (sc, sc, sc)
        g.hide_render = False
        for ob in g.children_recursive:
            ob.hide_render = False
