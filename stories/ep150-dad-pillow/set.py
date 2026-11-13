"""ep150 "my stepdad's pillow dreams of someone knocking": seven small bright stages, far apart (layout.py).

  GUEST   Dad's guest room: a bed with a striped quilt and two pillows (Dad's blue one), a window on a green yard,
          a bookshelf, a nightstand and lamp. Day-lit, or gold at dusk for the last shot (`mode` cue).
  HALL    Dad's front hall with its ceiling, stairs, rug and coat rack, and the white front door in the north wall.
          `mode` wake: the door is open on a sunny porch and the hall is daylit. `mode` dream: the door is shut,
          gold behind it (gold slivers round the leaf, gold side panels), the hall warm sunset gold, never dark.
  MEM     the porch at sixteen on a mild evening: the shut door, a side window with the lit room behind it.
  KITCH   the kitchen (a stove, counters, a sunny window) and the corridor outside its doorway.
  COUSIN / BUDDY  one shot each.

The rule meter is a cream tag on the camera: a pillow glyph and a moon with the night count (1, 2, 3), a sun by day.
A lavender glow sits on the pillow edge while I sleep: steady, never pulsing. Every light is constant per shot
(switched on the cut by `mode`), nothing blinks. Layered surfaces stand at least 1 cm proud of each other.
"""
import math
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="pillow-"))
W = {}
GOLD = "#ffc66a"
LAV = "#b8a0f0"


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def sample(name, tl, t, defaults):
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


# ---------------------------------------------------------------------------------------------- the tag (PIL)
def _tag_image(n):
    """n 0: a pillow and a moon with no number; 1..3: the night; 4: a sun (by day)."""
    from PIL import Image, ImageDraw, ImageFont
    p = TMP / f"tag-{n}.png"
    if not p.exists():
        Wd, Ht = 400, 300
        im = Image.new("RGB", (Wd, Ht), hx("#3a2a5a"))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([14, 14, Wd - 15, Ht - 15], 30, fill=hx("#fff1dc"))
        ink = hx("#3a2a5a")
        # the pillow glyph: a plump blue rounded pillow with a lavender edge, left
        d.rounded_rectangle([30, 70, 200, 190], 40, fill=hx(LAV), outline=ink, width=8)
        d.rounded_rectangle([42, 82, 188, 178], 32, fill=hx("#4a8fd8"), outline=ink, width=6)
        d.arc([62, 100, 168, 160], 200, 340, fill=hx("#cfe4ff"), width=7)
        # right: a moon (crescent) with the night count, or a sun by day
        if n == 4:
            cx, cy = 300, 130
            for k in range(8):
                a = k * math.pi / 4
                d.line([(cx + 52 * math.cos(a), cy + 52 * math.sin(a)), (cx + 82 * math.cos(a), cy + 82 * math.sin(a))],
                       fill=hx("#e08a10"), width=12)
            d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=hx("#ffc230"), outline=hx("#c26a00"), width=7)
        else:
            cx, cy = 292, 100
            d.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=hx("#ffd86a"), outline=ink, width=7)
            d.ellipse([cx - 22, cy - 66, cx + 66, cy + 34], fill=hx("#fff1dc"))
            if n:
                f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 110)
                d.text((338, 205), str(n), font=f, fill=ink, anchor="mm")
        im.save(p)
    return str(p)


def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    m, tex = imat(kit, "tag", _tag_image(0), 1.0)
    pl = kit.plane("tag.plane", (1.0, 0.75), (0, 0, 0), m, root)
    noshadow(pl)
    W["tagtex"] = tex
    W["tagimgs"] = {}
    W["tagn"] = 0


# ---------------------------------------------------------------------------------------------- building helpers
def wall_x(kit, name, x0, x1, y, th, h, mat, gaps=(), z0=0.0):
    """A wall along x at y (centre), thickness th, from z0 to h; gaps: [(g0, g1, gap_top)] doorways/windows from z0."""
    cuts = sorted(gaps)
    cur = x0
    k = 0
    for g0, g1, gh in cuts:
        if g0 > cur:
            kit.box(f"{name}.s{k}", (g0 - cur, th, h - z0), ((cur + g0) / 2, y, (z0 + h) / 2), mat)
            k += 1
        if gh < h:
            kit.box(f"{name}.l{k}", (g1 - g0, th, h - gh), ((g0 + g1) / 2, y, (gh + h) / 2), mat)
            k += 1
        cur = g1
    if cur < x1:
        kit.box(f"{name}.s{k}", (x1 - cur, th, h - z0), ((cur + x1) / 2, y, (z0 + h) / 2), mat)


def room(kit, name, x0, x1, y0, y1, h, wallm, floorm, ceilm, south_gaps=(), north_gaps=(), north=True):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    lx, ly = x1 - x0, y1 - y0
    kit.box(f"{name}.floor", (lx + 1.2, ly + 1.2, 0.1), (cx, cy, -0.05), floorm)
    wall_x(kit, f"{name}.ws", x0 - 0.4, x1 + 0.4, y0 - 0.2, 0.4, h + 0.3, wallm, south_gaps)
    if north:
        wall_x(kit, f"{name}.wn", x0 - 0.4, x1 + 0.4, y1 + 0.2, 0.4, h + 0.3, wallm, north_gaps)
    kit.box(f"{name}.ww", (0.4, ly + 0.8, h + 0.3), (x0 - 0.2, cy, h / 2 + 0.15), wallm)
    kit.box(f"{name}.we", (0.4, ly + 0.8, h + 0.3), (x1 + 0.2, cy, h / 2 + 0.15), wallm)
    kit.box(f"{name}.ceil", (lx + 1.2, ly + 1.2, 0.2), (cx, cy, h + 0.1), ceilm)


def fills(kit, prefix, pts, z, energy, color, size=2.5):
    names = []
    for i, (x, y) in enumerate(pts):
        a = kit.light(f"{prefix}{i}", "AREA", (x, y, z), energy, color, size=size, shadow=False)
        kit.aim(a, (x, y, 0.0))
        names.append(f"{prefix}{i}")
    return names


def facelight(kit, name, loc, tgt, energy, color, size=2.5):
    s = kit.light(name, "AREA", loc, energy, color, size=size, shadow=False)
    kit.aim(s, tgt)
    return name


def stripes_quilt(kit, root, w, ln, h, base, s1, s2):
    """A striped quilt block as children of `root`: stripes 1.5 cm proud of the top."""
    kit.box("quilt.base", (w, ln, h), (0, 0, 0), base, root, bevel=0.04)
    n = 7
    for i in range(n):
        y = -ln / 2 + (i + 0.5) * ln / n
        kit.box(f"quilt.st{i}", (w - 0.02, ln / n * 0.45, 0.015), (0, y, h / 2 + 0.005), s1 if i % 2 == 0 else s2, root)


# ---------------------------------------------------------------------------------------------- the guest room
def build_guest(kit):
    pl = kit.plastic
    wall = pl("#f7e9c8", 0.85, spec=0.03)
    wood = kit.texture("wood", 0.7, tint="#e8c890")
    ceil = kit.emit("#fff1dc", 0.65, "guestceil")
    room(kit, "guest", G.GX0, G.GX1, G.GY0, G.GY1, G.GH, wall, wood, ceil)
    # a sage band 1.5 cm proud of the north wall, west wall; a baseboard
    band = pl("#a8d4a0", 0.8, spec=0.03)
    kit.box("guest.band.n", (G.GX1 - G.GX0, 0.03, 0.9), ((G.GX0 + G.GX1) / 2, G.GY1 - 0.015, 0.45), band)
    kit.box("guest.band.w", (0.03, G.GY1 - G.GY0, 0.9), (G.GX0 + 0.015, (G.GY0 + G.GY1) / 2, 0.45), band)
    # the window on the north wall, on a green yard (a bright green-and-sky pane)
    fr = pl("#fffaf0", 0.6)
    wx, wz = 1.4, 1.5
    kit.box("guest.win.frame", (1.7, 0.05, 1.5), (wx, G.GY1 - 0.025, wz), fr)
    win = kit.emit("#bfe8ff", 1.0, "guestwin")
    noshadow(kit.box("guest.win.sky", (1.5, 0.02, 0.7), (wx, G.GY1 - 0.06, wz + 0.3), win))
    grass = kit.emit("#7fd870", 0.9, "guestgrass")
    noshadow(kit.box("guest.win.grass", (1.5, 0.02, 0.6), (wx, G.GY1 - 0.06, wz - 0.37), grass))
    kit.box("guest.win.bar", (0.04, 0.03, 1.4), (wx, G.GY1 - 0.085, wz), fr)
    kit.box("guest.win.bar2", (1.6, 0.03, 0.04), (wx, G.GY1 - 0.085, wz), fr)
    cur = pl("#f2a07a", 0.8)
    for sx in (-1, 1):
        kit.box(f"guest.curtain{sx}", (0.28, 0.06, 1.7), (wx + sx * 0.98, G.GY1 - 0.07, wz), cur)
    # the bed along the west wall: frame, mattress, headboard
    frame = pl("#b97f45", 0.6, spec=0.05)
    mt = pl("#f2f0ea", 0.9, spec=0.02)
    kit.box("bed.frame", (1.0, 2.1, 0.22), (G.BX, 2.55, 0.21), frame, bevel=0.02)
    kit.box("bed.mattress", (0.95, 2.0, 0.2), (G.BX, 2.55, 0.42), mt, bevel=0.04)
    kit.box("bed.head", (1.1, 0.08, 1.0), (G.BX, 3.58, 0.6), frame, bevel=0.02)
    # the quilt over my body, tilted a little toward the pillow, striped blue and yellow
    q = kit.empty("quilt", (G.BX, 2.1, 0.76), rot=(0.1, 0, 0))
    stripes_quilt(kit, q, 1.16, 1.3, 0.7, pl("#fff4d8", 0.9), pl("#3a6fd0", 0.8), pl("#f2c230", 0.8))
    W["quilt"] = q
    # an empty striped cover for the shots with nobody in bed (lower and flat)
    q2 = kit.empty("quilt.flat", (G.BX, 2.0, 0.6))
    stripes_quilt(kit, q2, 1.16, 1.6, 0.2, pl("#fff4d8", 0.9), pl("#3a6fd0", 0.8), pl("#f2c230", 0.8))
    W["quilt2"] = q2
    # Dad's pillow (blue) under my head, my white one (graded under 70%) behind it
    blue = pl("#4a8fd8", 0.8, spec=0.04)
    W["blue_day"], W["blue_dusk"] = blue, pl("#5a74ea", 0.8, spec=0.04)   # under the dusk gold it stays blue
    white = pl("#c4bfb2", 0.85, spec=0.03)
    W["bluepillow"] = kit.box("pillow.blue", (0.6, 0.5, 0.13), (G.BX, 3.1, 0.585), blue, bevel=0.05)
    W["whitepillow"] = kit.box("pillow.white", (0.55, 0.3, 0.12), (2.3, 0.45, 0.2), white, bevel=0.05)
    # the lavender glow along the blue pillow's edge: soft, steady, 1.5 cm proud
    gl = kit.emit(LAV, 1.4, "pillowglow")
    W["glow"] = noshadow(kit.box("pillow.glow", (0.62, 0.05, 0.03), (G.BX + 0.0, 2.8, 0.59), gl, bevel=0.01)) or None
    W["glow2"] = kit.box("pillow.glow2", (0.05, 0.5, 0.03), (G.BX + 0.32, 3.1, 0.59), gl, bevel=0.01)
    noshadow(W["glow2"])
    # the pillow Dad's is held up as: a second blue pillow, moved to my forearms by `animate`
    held = kit.empty("pillow.held", (0, 0, -40))
    W["held_body"] = kit.box("held.body", (0.64, 0.42, 0.14), (0, 0, 0), blue, held, bevel=0.06)
    kit.box("held.edge", (0.66, 0.04, 0.03), (0, 0.2, 0.0), pl("#cfe4ff", 0.8), held)
    W["held"] = held
    # nightstand with the desk lamp, a bookshelf, a chair with my duffel, a rug
    kit.prop("nightstand_1", (G.BX + 1.0, 3.2, 0), scale=1.0)
    kit.prop("light_desk", (G.BX + 1.0, 3.2, 0.41), scale=1.0)
    kit.prop("bookshelf", (-2.4, 0.3, 0), rot=90)
    kit.prop("chair_1", (2.3, 1.0, 0), rot=-90)
    kit.box("duffel", (0.7, 0.32, 0.34), (2.3, 1.0, 0.62), pl("#355a8a", 0.7), bevel=0.06)
    kit.box("guest.rug", (2.6, 1.7, 0.02), (0.8, -0.4, 0.01), pl("#f2c05a", 0.9, spec=0.02))
    kit.box("guest.rug.in", (2.2, 1.3, 0.012), (0.8, -0.4, 0.025), pl("#e8895a", 0.9, spec=0.02))
    kit.prop("houseplant_1", (2.3, -3.2, 0), scale=2.4)
    # lights: day (white-warm) and dusk (gold), switched with the cut by `mode`
    pts = ((-0.8, -1.5), (1.6, -1.5), (-0.8, 1.6), (1.6, 1.6), (0.4, -3.4))
    W["guest.day"] = fills(kit, "gd", pts, G.GH - 0.15, 330, "#fff3e0") + [
        facelight(kit, "gd.face", (0.6, -4.3, 2.2), (0.6, 0.0, 1.2), 380, "#fff6ec"),
        facelight(kit, "gd.bed", (1.2, 2.0, 2.3), (G.BX, 3.0, 0.8), 320, "#fff6ec", 2.0)]
    W["guest.dusk"] = fills(kit, "gu", pts, G.GH - 0.15, 330, "#ffdcb0") + [
        facelight(kit, "gu.face", (0.6, -4.3, 2.2), (0.6, 0.0, 1.2), 400, "#ffd890"),
        facelight(kit, "gu.bed", (1.2, 2.0, 2.3), (G.BX, 3.0, 0.8), 320, "#ffd890", 2.0)]


# ---------------------------------------------------------------------------------------------- the hall
def build_hall(kit):
    pl = kit.plastic
    wall = pl("#f0dcae", 0.85, spec=0.03)
    floor = kit.texture("wood", 0.7, tint="#d49a58")
    ceil = kit.emit("#ffeccc", 0.6, "hallceil")
    x0, x1, y0, y1, h = G.HX0, G.HX1, G.HY0, G.HY1, G.HH
    dx0, dx1 = G.HX - G.DOOR_W / 2, G.HX + G.DOOR_W / 2
    room(kit, "hall", x0, x1, y0, y1, h, wall, floor, ceil, north_gaps=[(dx0, dx1, G.DOOR_H)])
    # a wainscot band, 3 cm proud of the walls
    wood = pl("#c98a4b", 0.7, spec=0.04)
    kit.box("hall.dado.w", (0.03, y1 - y0, 0.9), (x0 + 0.015, (y0 + y1) / 2, 0.45), wood)
    kit.box("hall.dado.e", (0.03, y1 - y0, 0.9), (x1 - 0.015, (y0 + y1) / 2, 0.45), wood)
    kit.box("hall.dado.s", (x1 - x0, 0.03, 0.9), ((x0 + x1) / 2, y0 + 0.015, 0.45), wood)
    kit.box("hall.dado.n1", (dx0 - x0, 0.03, 0.9), ((x0 + dx0) / 2, y1 - 0.015, 0.45), wood)
    kit.box("hall.dado.n2", (x1 - dx1, 0.03, 0.9), ((dx1 + x1) / 2, y1 - 0.015, 0.45), wood)
    # the stairs up the west side, solid blocks
    sw = pl("#d99a58", 0.7, spec=0.05)
    sr = pl("#b97f45", 0.7, spec=0.05)
    for i in range(1, 9):
        ys = G.STEP_Y0 + G.STEP_DY * (i - 1)
        top = G.STEP_DZ * i
        sw_i = 1.65 - 0.008 * (i - 1)      # each step 8 mm narrower: no coplanar east faces shadowing each other
        kit.box(f"stair{i}", (sw_i, y1 - ys, top), (x0 + sw_i / 2, (ys + y1) / 2, top / 2), sw if i % 2 else sr, bevel=0.01)
    kit.box("newel", (0.14, 0.14, 0.9), (x0 + 1.55, G.STEP_Y0 - 0.1, 0.45), wood, bevel=0.02)
    # Dad's seat on the third stair: thighs, shins and slippers, static (Dad never moves in the dream)
    pants = pl("#4a5a7a", 0.8)
    slip = pl("#8a5a3a", 0.8)
    W["seat"] = []
    for sx in (-1, 1):
        W["seat"] += [
            kit.box(f"dad.thigh{sx}", (0.31, 0.62, 0.22), (G.DAD_X + sx * 0.175, G.DAD_Y - 0.36, G.STAIR3 + 0.12), pants, bevel=0.04),
            kit.box(f"dad.shin{sx}", (0.28, 0.22, 0.52), (G.DAD_X + sx * 0.2, G.DAD_Y - 0.82, G.STAIR3 - 0.09), pants, bevel=0.04),
            kit.box(f"dad.slip{sx}", (0.28, 0.34, 0.1), (G.DAD_X + sx * 0.21, G.DAD_Y - 0.88, 0.255), slip, bevel=0.03)]
    # a rug and a coat rack by the door, a plant
    kit.box("hall.rug", (1.6, 3.0, 0.02), (0.0 + G.HX, 1.6, 0.01), pl("#d9604a", 0.9, spec=0.02))
    kit.box("hall.rug.in", (1.3, 2.7, 0.012), (G.HX, 1.6, 0.025), pl("#f2c05a", 0.9, spec=0.02))
    kit.box("rack.pole", (0.06, 0.06, 1.7), (x1 - 0.5, 4.5, 0.85), wood)
    for k, c in enumerate(("#4a8fd8", "#e86a5a")):
        kit.box(f"rack.coat{k}", (0.3, 0.12, 0.7), (x1 - 0.5, 4.38 - k * 0.0, 1.2 - 0.0), pl(c, 0.8), rot=(0, 0, 0.2 * k))
    kit.prop("houseplant_1", (x1 - 0.6, 3.3, 0), scale=2.8)
    for k, c in enumerate(("#8ad0ff", "#ffb08a", "#b8e6a0")):
        kit.box(f"hall.picframe{k}", (0.03, 0.8, 0.65), (x1 - 0.045, 1.0 + k * 1.1, 1.7), pl("#fff8ea", 0.6))
        kit.box(f"hall.pic{k}", (0.03, 0.7, 0.55), (x1 - 0.065, 1.0 + k * 1.1, 1.7), pl(c, 0.6))
    # the front door: a casing (white-ish, graded under 70%), a leaf on a hinge, gold slivers and side panels (dream)
    wh = pl("#c4bfb2", 0.7, spec=0.04)
    for sx in (-1, 1):
        kit.box(f"door.case{sx}", (0.14, 0.04, G.DOOR_H + 0.14), (G.HX + sx * (G.DOOR_W / 2 + 0.07), y1 - 0.02, (G.DOOR_H + 0.14) / 2), wh)
    kit.box("door.case.t", (G.DOOR_W + 0.28, 0.04, 0.14), (G.HX, y1 - 0.02, G.DOOR_H + 0.07), wh)
    pv = kit.empty("door.pivot", (dx0 + 0.04, y1 + 0.12, 0))
    kit.box("door.leaf", (1.1, 0.07, 2.12), (0.55, 0.0, 1.07), wh, pv, bevel=0.01)
    kit.box("door.panel1", (0.78, 0.02, 0.8), (0.55, -0.04, 1.5), pl("#d8d3c4", 0.7), pv)
    kit.box("door.panel2", (0.78, 0.02, 0.8), (0.55, -0.04, 0.55), pl("#d8d3c4", 0.7), pv)
    kit.sphere("door.knob", 0.05, (0.98, -0.07, 1.0), pl("#e0b040", 0.3, spec=0.7), pv)
    W["pivot"] = pv
    gold = kit.emit("#ffc66a", 2.6, "doorgold")
    gp = noshadow(kit.box("door.glow", (G.DOOR_W + 0.04, 0.02, G.DOOR_H + 0.02), (G.HX, y1 + 0.3, G.DOOR_H / 2), gold)) or None
    W["doorgold"] = bpy.data.objects["door.glow"]
    # two pencil strokes on the dream door's frame at shoulder height (lore), 1.5 cm proud, only in the dream
    gr = pl("#4a4a56", 0.6)
    gs = kit.emit("#ff9a1a", 1.1, "doorstrip")     # saturated and modest, so the grade keeps it gold, not cream
    W["strips"] = []
    for sx in (-1, 1):
        W["strips"].append(kit.box(f"door.strip{sx}", (0.06, 0.012, G.DOOR_H), (G.HX + sx * (G.DOOR_W / 2 + 0.03), y1 - 0.046,
                                   G.DOOR_H / 2), gs))
    W["strips"].append(kit.box("door.strip.t", (G.DOOR_W + 0.12, 0.012, 0.06), (G.HX, y1 - 0.046, G.DOOR_H + 0.03), gs))
    for ob in W["strips"]:
        noshadow(ob)
    W["pencil"] = [kit.box("pencil1", (0.1, 0.012, 0.016), (G.HX + G.DOOR_W / 2 + 0.115, y1 - 0.046, 1.4), gr),
                   kit.box("pencil2", (0.1, 0.012, 0.016), (G.HX + G.DOOR_W / 2 + 0.115, y1 - 0.046, 1.55), gr)]
    # side panels, either gold (dream) or white (wake); 2 cm proud of the wall
    pg = kit.emit("#ffb040", 0.85, "sidegold")
    pw = kit.emit("#cfe2f2", 0.6, "sidewhite")
    W["sidegold"], W["sidewhite"] = [], []
    for sx in (-1, 1):
        a = kit.box(f"side.g{sx}", (0.45, 0.02, 1.5), (G.HX + sx * 1.65, y1 - 0.04, 1.5), pg)
        b = kit.box(f"side.w{sx}", (0.45, 0.02, 1.5), (G.HX + sx * 1.65, y1 - 0.04, 1.5), pw)
        b.location.y -= 0.002
        noshadow(a)
        noshadow(b)
        W["sidegold"].append(a)
        W["sidewhite"].append(b)
        kit.box(f"side.f{sx}", (0.55, 0.02, 1.6), (G.HX + sx * 1.65, y1 - 0.025, 1.5), wh)
    # the porch beyond the door, and the lawn
    deck = pl("#d9b27c", 0.8, spec=0.03)
    kit.box("porch.deck", (6.4, 4.0, 0.12), (G.HX, 7.4, -0.06), deck)
    for k in range(3):
        kit.box(f"porch.step{k}", (2.2, 0.35, 0.12), (G.HX, 9.55 + k * 0.33, -0.12 - k * 0.12), deck)
    kit.box("porch.duffel", (0.62, 0.3, 0.32), (G.HX + 0.75, 5.95, 0.17), pl("#355a8a", 0.7), bevel=0.06)
    kit.box("porch.duffel.strap", (0.05, 0.31, 0.2), (G.HX + 0.75, 5.95, 0.36), pl("#1e3456", 0.7))
    kit.box("porch.roof", (6.8, 4.4, 0.2), (G.HX, 7.4, 3.3), pl("#a8c8e8", 0.7))
    kit.box("porch.post1", (0.18, 0.18, 3.2), (G.HX - 2.9, 9.2, 1.6), wh)
    kit.box("porch.post2", (0.18, 0.18, 3.2), (G.HX + 2.9, 9.2, 1.6), wh)
    grass = kit.texture("grass", 0.5, tint="#8fe07a")
    kit.box("lawn", (60, 50, 0.3), (G.HX, 36.0, -0.5), grass)
    kit.box("walk", (1.7, 18, 0.05), (G.HX, 20.0, -0.3), pl("#e8e2d2", 0.8))
    for sx in (-1, 1):
        kit.prop("commontree_1", (G.HX + sx * 7.5, 16.0, -0.35), rot=40 * sx, scale=1.4)
        kit.prop("sub_fence_low", (G.HX + sx * 4.5, 14.0, -0.35), rot=0)
        kit.prop("bush_1", (G.HX + sx * 2.8, 10.6, -0.35), scale=1.0)
    kit.prop("sub_building_type_f", (G.HX - 14, 22.0, -0.35), rot=90, tint="#ffe39a")
    kit.prop("sub_building_type_a", (G.HX + 14, 24.0, -0.35), rot=-90, tint="#c8d8ff")
    kit.box("hall.far", (90, 4, 10), (G.HX, 62, 3.5), pl("#9fd29a", 0.9, spec=0.01))
    # hall lights: wake (white-warm, daylit) and dream (gold), switched by `mode`
    pts = ((G.HX - 1.2, 0.2), (G.HX + 1.2, 0.2), (G.HX - 1.2, 2.6), (G.HX + 1.2, 2.6), (G.HX, 4.2))
    W["hall.wake"] = fills(kit, "hw", pts, h - 0.15, 360, "#fff3e0", 2.8) + [
        facelight(kit, "hw.face", (G.HX + 0.3, -1.3, 2.4), (G.HX, 2.8, 1.2), 420, "#fff6ec"),
        facelight(kit, "hw.back", (G.HX, 3.2, 2.6), (G.HX, 0.0, 1.2), 200, "#fff6ec", 3.0)]
    W["hall.dream"] = fills(kit, "hd", pts, h - 0.15, 420, GOLD, 2.8) + [
        facelight(kit, "hd.face", (G.HX + 0.3, -1.3, 2.4), (G.HX, 2.8, 1.2), 480, "#ffd890"),
        facelight(kit, "hd.dad", (G.HX - 0.5, -0.6, 2.2), (G.DAD_X, G.DAD_Y, 1.1), 380, "#ffd890", 1.8),
        facelight(kit, "hd.door", (G.HX + 0.2, 2.2, 2.6), (G.HX, G.HY1, 1.2), 240, "#ffd890", 3.0)]
    # the stairs' east face is vertical and the fills point down: a low side fill so it never reads as a black block
    W["hall.wake"].append(facelight(kit, "hw.stair", (G.HX + 1.9, 2.6, 1.1), (G.HX - 1.0, 2.6, 0.6), 260, "#fff3e0", 3.0))
    W["hall.dream"].append(facelight(kit, "hd.stair", (G.HX + 1.9, 2.6, 1.1), (G.HX - 1.0, 2.6, 0.6), 260, "#ffd890", 3.0))
    # the sunny porch light (wake only)
    W["porch"] = [facelight(kit, "porch.sun", (G.HX, 12.0, 6.0), (G.HX, 6.6, 0.6), 2600, "#fff0d0", 7.0),
                  facelight(kit, "porch.face", (G.HX, 3.4, 2.8), (G.HX, 6.6, 1.2), 520, "#fff3e0", 3.0)]


# ---------------------------------------------------------------------------------------------- the memory porch
def build_mem(kit):
    pl = kit.plastic
    wall = pl("#d6b282", 0.85, spec=0.03)
    wh = pl("#a8a294", 0.7, spec=0.04)
    x, y = G.MX, G.MY
    deck = pl("#d9b27c", 0.8, spec=0.03)
    kit.box("mem.deck", (7, 4.6, 0.12), (x, y - 2.3, -0.06), deck)
    # the house wall facing south, with a window opening at x+0.95 (z 0.9..2.1), and the shut door
    wall_x(kit, "mem.wall", x - 3.5, x + 3.5, y + 0.15, 0.3, 3.2, wall, gaps=[(x + 0.5, x + 1.4, 2.1)], z0=0.0)
    kit.box("mem.sill", (0.9, 0.3, 0.9), (x + 0.95, y + 0.15, 0.45), wall)
    mul = pl("#b98a5a", 0.6)
    kit.box("mem.mull.v", (0.05, 0.05, 1.2), (x + 0.95, y + 0.05, 1.5), mul)
    kit.box("mem.mull.h", (0.9, 0.05, 0.05), (x + 0.95, y + 0.05, 1.22), mul)       # under the window
    # the window gap has no glass; behind it a lit room
    kit.box("mem.room.floor", (7, 3.2, 0.1), (x, y + 2.0, -0.05), kit.texture("wood", 0.7, tint="#d49a58"))
    kit.box("mem.room.back", (7, 0.2, 3.2), (x, y + 3.7, 1.6), pl("#f5d9a0", 0.85))
    kit.box("mem.room.ceil", (7, 3.4, 0.2), (x, y + 2.0, 3.3), kit.emit("#ffe7bd", 0.6, "memceil"))
    kit.box("mem.room.wl", (0.2, 3.4, 3.2), (x - 3.5, y + 2.0, 1.6), wall)
    kit.box("mem.room.wr", (0.2, 3.4, 3.2), (x + 3.5, y + 2.0, 1.6), wall)
    for sx in (-1, 1):
        kit.box(f"mem.case{sx}", (0.14, 0.04, 2.25), (x + sx * 0.67, y - 0.02, 1.125), wh)
    kit.box("mem.case.t", (1.48, 0.04, 0.14), (x, y - 0.02, 2.2), wh)
    kit.box("mem.door", (1.2, 0.07, 2.12), (x, y - 0.0, 1.06), wh, bevel=0.01)
    kit.box("mem.panel1", (0.84, 0.02, 0.8), (x, y - 0.05, 1.5), pl("#b8b2a4", 0.7))
    kit.box("mem.panel2", (0.84, 0.02, 0.8), (x, y - 0.05, 0.55), pl("#b8b2a4", 0.7))
    kit.sphere("mem.knob", 0.05, (x + 0.45, y - 0.08, 1.0), pl("#e0b040", 0.3, spec=0.7))
    for sx in (-1, 1):
        kit.box(f"mem.wcase{sx}", (0.05, 0.04, 1.3), (x + 0.95 + sx * 0.475, y - 0.02, 1.5), wh)
    kit.box("mem.wcase.t", (1.0, 0.04, 0.05), (x + 0.95, y - 0.02, 2.13), wh)
    kit.box("mem.wcase.b", (1.0, 0.04, 0.05), (x + 0.95, y - 0.02, 0.88), wh)
    # the porch lamp by the door, lit
    kit.box("mem.lamp.base", (0.16, 0.06, 0.24), (x - 0.88, y - 0.06, 1.95), pl("#3a3a44", 0.5))
    noshadow(kit.box("mem.lamp", (0.12, 0.1, 0.18), (x - 0.88, y - 0.12, 1.95), kit.emit("#ffd890", 2.0, "memlamp")))
    kit.light("mp.lamp", "POINT", (x - 0.88, y - 0.4, 1.95), 260, "#ffd890", size=0.2, shadow=False)
    # the evening sky past the porch's west end: dusky blue over a peach band
    noshadow(kit.box("mem.sky.hi", (0.2, 90, 30), (x - 30, y - 10, 19.0), kit.emit("#7f8fd6", 1.0, "memskyhi")))
    noshadow(kit.box("mem.sky.lo", (0.2, 90, 5.0), (x - 29.9, y - 10, 2.0), kit.emit("#ffb488", 1.0, "memskylo")))
    kit.box("mem.roof", (7.4, 4.8, 0.2), (x, y - 2.3, 3.4), pl("#a8c8e8", 0.7))
    kit.box("mem.post1", (0.18, 0.18, 3.3), (x - 3.2, y - 4.4, 1.65), wh)
    kit.box("mem.post2", (0.18, 0.18, 3.3), (x + 3.2, y - 4.4, 1.65), wh)
    kit.prop("houseplant_1", (x - 2.6, y - 0.7, 0), scale=2.6)
    kit.box("mem.lawn", (60, 40, 0.3), (x, y - 24, -0.4), kit.texture("grass", 0.5, tint="#a8d870"))
    kit.prop("commontree_2", (x - 7, y - 12, -0.3), scale=1.3)
    kit.prop("commontree_1", (x + 7, y - 10, -0.3), scale=1.2)
    kit.prop("sub_building_type_c", (x + 12, y - 16, -0.3), rot=-90, tint="#ffd0a0")
    # evening gold on the porch, warm light in the room (mild: bright, never dark)
    fills(kit, "mp", ((x - 1.2, y - 1.2), (x + 1.2, y - 1.2), (x - 1.2, y - 3.6), (x + 1.2, y - 3.6)), 3.2, 190, GOLD, 2.8)
    facelight(kit, "mp.face", (x, y - 5.5, 2.6), (x, y - 1.0, 1.3), 380, "#ffd890", 3.0)
    facelight(kit, "mp.sun", (x - 4, y - 12, 7), (x, y - 1.5, 1.0), 950, "#ffc66a", 6.0)
    fills(kit, "mr", ((x - 1.2, y + 1.6), (x + 1.2, y + 1.6)), 3.1, 260, "#fff0dc", 2.8)
    facelight(kit, "mr.face", (x + 1.1, y - 1.6, 2.0), (x + 1.15, y + 0.9, 1.6), 300, "#eef2ff", 1.6)


# ---------------------------------------------------------------------------------------------- the kitchen
def build_kitchen(kit):
    pl = kit.plastic
    x = G.KX
    wall = pl("#e6c995", 0.85, spec=0.03)
    wood = kit.texture("wood", 0.7, tint="#e8c890")
    ceil = kit.emit("#f6e2c0", 0.45, "kitceil")
    wh = pl("#c4bfb2", 0.7, spec=0.04)
    # the kitchen room y 0.3..4.6 with a doorway in the south wall; a corridor y -3..0 beyond
    room(kit, "kit", x - 2.4, x + 2.4, 0.3, 4.6, 2.7, wall, wood, ceil, south_gaps=[(x - 0.55, x + 0.55, 2.1)])
    room(kit, "cor", x - 2.4, x + 2.4, -3.0, -0.1, 2.7, pl("#dcc090", 0.85), wood, ceil, north=False)
    for sx in (-1, 1):
        kit.box(f"kit.case{sx}", (0.14, 0.04, 2.2), (x + sx * 0.62, 0.02, 1.1), wh)
    kit.box("kit.case.t", (1.38, 0.04, 0.14), (x, 0.02, 2.17), wh)
    # counters along the north wall, a stove between them, a sunny window on the east wall
    cab = pl("#9fcf9a", 0.7, spec=0.05)
    top = pl("#f4efe2", 0.5, spec=0.1)
    for sx in (-1, 1):
        kit.box(f"kit.cab{sx}", (1.5, 0.6, 0.88), (x + sx * 1.35, 4.28, 0.44), cab, bevel=0.02)
        kit.box(f"kit.top{sx}", (1.55, 0.64, 0.05), (x + sx * 1.35, 4.28, 0.9), top, bevel=0.01)
    kit.prop("kitchen_oven", (x, 4.3, 0), height=0.9, rot=0)
    kit.box("kit.hood", (1.0, 0.5, 0.3), (x, 4.34, 2.3), pl("#8a909c", 0.5, spec=0.3))
    kit.box("pan", (0.34, 0.34, 0.07), (x + 0.0, 4.2, 0.95), pl("#3a3a44", 0.4, spec=0.4))
    win = kit.emit("#fff6d8", 1.4, "kitwin")
    fr = pl("#fffaf0", 0.6)
    kit.box("kit.win.frame", (0.05, 1.6, 1.4), (x + 2.37, 2.4, 1.6), fr)
    noshadow(kit.box("kit.win.pane", (0.02, 1.44, 1.24), (x + 2.34, 2.4, 1.6), win))
    kit.box("kit.win.bar", (0.03, 0.04, 1.3), (x + 2.32, 2.4, 1.6), fr)
    kit.box("kit.table", (1.2, 0.8, 0.05), (x + 1.4, 1.5, 0.78), pl("#b97f45", 0.6))
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"kit.tl{sx}{sy}", (0.06, 0.06, 0.76), (x + 1.4 + sx * 0.52, 1.5 + sy * 0.32, 0.38), pl("#b97f45", 0.6))
    kit.prop("houseplant_1", (x - 2.0, 1.0, 0), scale=2.4)
    kit.box("kit.rug", (1.6, 1.0, 0.02), (x - 0.4, 1.7, 0.01), pl("#f2c05a", 0.9, spec=0.02))
    kit.box("cor.rug", (1.2, 2.2, 0.02), (x, -1.5, 0.01), pl("#e8895a", 0.9, spec=0.02))
    # the spatula in Dad's hand: a handle and a head, dropped by `animate`
    sp = kit.empty("spat", (0, 0, -40))
    kit.box("spat.handle", (0.03, 0.03, 0.34), (0, 0, 0.12), pl("#8a5a2a", 0.6), sp)
    kit.box("spat.head", (0.11, 0.015, 0.14), (0, 0, -0.1), pl("#c9ced6", 0.4, spec=0.5), sp)
    W["spat"] = sp
    fills(kit, "kf", ((x - 1.0, 1.4), (x + 1.0, 1.4), (x - 1.0, 3.4), (x + 1.0, 3.4)), 2.55, 300, "#fff3e0")
    facelight(kit, "kf.face", (x, 0.5, 2.3), (x, 4.0, 1.3), 360, "#fff6ec")
    facelight(kit, "kf.face2", (x, 3.9, 2.3), (x, 0.2, 1.3), 320, "#fff6ec")
    fills(kit, "cf", ((x - 1.0, -1.0), (x + 1.0, -1.0), (x, -2.4)), 2.55, 300, "#fff3e0")
    facelight(kit, "cf.face", (x, 2.6, 2.3), (x, -0.4, 1.3), 380, "#fff6ec")


# ---------------------------------------------------------------------------------------------- cousin and buddy
def build_cousin(kit):
    pl = kit.plastic
    x, y = G.CX, G.CY
    room(kit, "cz", x - 3, x + 3, y - 3.5, y + 3.0, 2.7, pl("#d9b48c", 0.85), kit.texture("wood", 0.7, tint="#e8c890"),
         kit.emit("#f6e2c0", 0.45, "czceil"))
    frame = pl("#b97f45", 0.6)
    kit.box("cz.frame", (1.0, 2.1, 0.22), (x, 2.0, 0.21), frame, bevel=0.02)
    kit.box("cz.matt", (0.95, 2.0, 0.2), (x, 2.0, 0.42), pl("#d4ccbc", 0.9), bevel=0.04)
    kit.box("cz.head", (1.1, 0.08, 1.1), (x, 3.0 - 0.0, 0.6), frame)
    kit.box("cz.pillow", (0.7, 0.3, 0.3), (x, 2.75, 0.8), pl("#c9b8e0", 0.9), bevel=0.08)
    q = kit.empty("cz.quilt", (x, 1.55, 0.64))
    stripes_quilt(kit, q, 1.16, 1.1, 0.5, pl("#ffe9d0", 0.9), pl("#8a6ad8", 0.8), pl("#f29ac0", 0.8))
    # crossword clues on the wall: a grid of black and white squares (no letters)
    kit.box("cz.grid", (1.2, 0.03, 1.2), (x + 1.8, 3.0 - 0.02, 1.7), pl("#fffaf0", 0.6))
    import random
    r = random.Random(5)
    for i in range(5):
        for j in range(5):
            if r.random() < 0.35:
                kit.box(f"cz.sq{i}{j}", (0.2, 0.012, 0.2), (x + 1.8 - 0.48 + i * 0.24, 3.0 - 0.045, 1.7 - 0.48 + j * 0.24),
                        pl("#2a2a34", 0.6))
    kit.box("cz.rug", (2.4, 1.6, 0.02), (x, -0.5, 0.01), pl("#ffd0a0", 0.9, spec=0.02))
    kit.prop("houseplant_1", (x - 2.4, 2.5, 0), scale=2.4)
    fills(kit, "cf_", ((x - 1.2, -1.6), (x + 1.2, -1.6), (x - 1.0, 1.4), (x + 1.0, 1.4)), 2.55, 300, "#fff3e0")
    facelight(kit, "cf_.face", (x, -3.2, 2.2), (x, 2.2, 1.2), 380, "#fff6ec")


def build_buddy(kit):
    pl = kit.plastic
    x, y = G.BDX, G.BDY
    room(kit, "bd", x - 3.2, x + 3.2, y - 6.5, y + 3.5, 2.7, pl("#bcd39a", 0.85),
         kit.texture("wood", 0.7, tint="#e8c890"), kit.emit("#f6e2c0", 0.45, "bdceil"))
    kit.prop("couch_medium1", (x, y + 2.9, 0), rot=180, tint="#e8a88a")
    # the big dog bed: a round-ish low block with a rim
    bed = pl("#c9605a", 0.9, spec=0.02)
    kit.box("bd.bed", (1.9, 1.5, 0.22), (x, y + 0.8, 0.11), bed, bevel=0.08)
    for sx in (-1, 1):
        kit.box(f"bd.rim{sx}", (0.18, 1.5, 0.36), (x + sx * 0.92, y + 0.8, 0.18), pl("#a84a48", 0.9), bevel=0.07)
    kit.box("bd.rimb", (1.9, 0.18, 0.36), (x, y + 1.5, 0.18), pl("#a84a48", 0.9), bevel=0.07)
    # the shaggy dog asleep beside him: a blocky body, head on paws, floppy ears (one twitches), a tail
    fur = pl("#c9a06a", 0.95, spec=0.02)
    dark = pl("#8a6a3a", 0.95, spec=0.02)
    dx, dy = x + 0.45, y + 0.55
    kit.box("dog.body", (0.5, 0.85, 0.38), (dx, dy, 0.4), fur, bevel=0.1)
    kit.box("dog.patch", (0.52, 0.4, 0.2), (dx, dy + 0.1, 0.5), dark, bevel=0.08)
    kit.box("dog.head", (0.36, 0.38, 0.32), (dx, dy - 0.55, 0.38), fur, bevel=0.09)
    kit.box("dog.snout", (0.2, 0.2, 0.15), (dx, dy - 0.76, 0.33), fur, bevel=0.05)
    kit.box("dog.nose", (0.08, 0.05, 0.06), (dx, dy - 0.87, 0.36), pl("#1c1c24", 0.4))
    kit.box("dog.paw1", (0.12, 0.3, 0.12), (dx - 0.12, dy - 0.8, 0.28), fur, bevel=0.04)
    kit.box("dog.paw2", (0.12, 0.3, 0.12), (dx + 0.12, dy - 0.8, 0.28), fur, bevel=0.04)
    kit.box("dog.tail", (0.12, 0.4, 0.12), (dx + 0.1, dy + 0.55, 0.32), dark, bevel=0.05, rot=(0, 0, 0.3))
    ears = []
    for sx in (-1, 1):
        piv = kit.empty(f"dog.earp{sx}", (dx + sx * 0.18, dy - 0.52, 0.54))
        kit.box(f"dog.ear{sx}", (0.1, 0.18, 0.22), (sx * 0.03, 0, -0.1), dark, piv, bevel=0.04)
        ears.append(piv)
    W["ears"] = ears
    kit.prop("houseplant_1", (x - 2.6, y + 2.6, 0), scale=2.6)
    kit.box("bd.rug", (3.0, 2.0, 0.02), (x, y - 0.8, 0.01), pl("#7fb0d8", 0.9, spec=0.02))
    fills(kit, "bf", ((x - 1.2, y - 1.6), (x + 1.2, y - 1.6), (x - 1.0, y + 1.4), (x + 1.0, y + 1.4)), 2.55, 300, "#fff3e0")
    facelight(kit, "bf.face", (x, y - 5.8, 2.2), (x, y + 1.0, 1.1), 380, "#fff6ec")


# ---------------------------------------------------------------------------------------------- build / animate
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    build_guest(kit)
    build_hall(kit)
    build_mem(kit)
    build_kitchen(kit)
    build_cousin(kit)
    build_buddy(kit)
    build_tag(kit)
    W["extras_done"] = False
    for nm, d in kit.LIGHTS.items():      # one global trim, so the bright grade never clips the sets
        d["light"].energy *= 0.28
        d["base"] = d["light"].energy
    return {}


def hand(who, sx):
    ob = bpy.data.objects.get(f"{who}.arm{sx}")
    if ob is None:
        return None
    return ob.matrix_world @ Vector((0, 0, -1.55))


def attach_extras(kit):
    """Heads wear the extras (idempotent): Dad's gray flat-top mustache, the young Dad's dark one, the cousin's pencil."""
    pl = kit.plastic
    if W.get("extras_done"):
        return
    dh, mh, ch = (bpy.data.objects.get(f"{n}.headg") for n in ("dad", "dadm", "cousin"))
    if dh is None or mh is None or ch is None:
        return
    for head, col in ((dh, "#b4b4bc"), (mh, "#2a2018")):
        m = pl(col, 0.8)
        n = head.name.split(".")[0]
        for sx in (-1, 1):
            kit.box(f"{n}.stache{sx}", (0.34, 0.1, 0.08), (sx * 0.19, -0.64, -0.08), m, head, rot=(0, sx * 0.3, 0), bevel=0.03)
        kit.box(f"{n}.stache.mid", (0.2, 0.1, 0.08), (0, -0.65, -0.06), m, head, bevel=0.03)
    pen = pl("#ffcc2a", 0.5)
    kit.box("cousin.pencil", (0.07, 0.5, 0.07), (-0.86, -0.1, 0.25), pen, ch, rot=(0, 0, 0.15), bevel=0.01)
    kit.box("cousin.pencil.tip", (0.065, 0.07, 0.065), (-0.88, -0.38, 0.25), pl("#e87a8a", 0.5), ch, bevel=0.01)
    W["extras_done"] = True


def animate(kit, story, tl, t, ctx):
    attach_extras(kit)
    bpy.context.view_layer.update()
    # ---- the tag
    n = int(round(sample("night", tl, t, {"n": 0})["n"]))
    n = max(0, min(4, n))
    if n != W["tagn"]:
        if n not in W["tagimgs"]:
            img = bpy.data.images.load(_tag_image(n))
            img.colorspace_settings.name = "sRGB"
            W["tagimgs"][n] = img
        W["tagtex"].image = W["tagimgs"][n]
        W["tagn"] = n
    mode = sample("mode", tl, t, {"m": "wake"})["m"]
    # ---- the front door and the dream's gold
    dr = sample("frontdoor", tl, t, {"v": 1.0})["v"]
    W["pivot"].rotation_euler = (0, 0, math.radians(120) * dr)
    dream = mode == "dream"
    seat = sample("seat", tl, t, {"v": 0.0})["v"] > 0.5
    for ob in W["seat"]:
        ob.hide_render = not seat
    W["doorgold"].hide_render = not dream
    for ob in W["sidegold"]:
        ob.hide_render = not dream
    for ob in W["sidewhite"]:
        ob.hide_render = dream
    for ob in W["pencil"] + W["strips"]:
        ob.hide_render = not dream
    pm = W["blue_dusk"] if mode == "dusk" else W["blue_day"]
    for ob in (W["bluepillow"], W["held_body"]):
        if ob.material_slots and ob.material_slots[0].material is not pm:
            ob.material_slots[0].material = pm
    # ---- the pillow: on the bed, or held flat on my forearms
    held = sample("pillow", tl, t, {"v": 0.0})["v"] > 0.5
    W["bluepillow"].hide_render = held
    W["held"].hide_render = not held
    for c in W["held"].children:
        c.hide_render = not held
    if held:
        a, b = hand("me", -1), hand("me", 1)
        if a is not None and b is not None:
            mid = (a + b) / 2
            W["held"].location = (mid.x, mid.y - 0.05, mid.z + 0.07)
            W["held"].rotation_euler = (0, 0, 0)
    else:
        W["held"].location = (0, 0, -40)
    # the quilt over my body only while I lie in bed (keys of `bed` v)
    inbed = sample("bed", tl, t, {"v": 0.0})["v"] > 0.5
    W["quilt"].hide_render = not inbed
    for c in W["quilt"].children:
        c.hide_render = not inbed
    W["quilt2"].hide_render = inbed
    for c in W["quilt2"].children:
        c.hide_render = inbed
    glow = inbed
    W["glow2"].hide_render = not glow
    bpy.data.objects["pillow.glow"].hide_render = not glow
    # ---- the dog's ear twitch
    tw = sample("ear", tl, t, {"v": 0.0})["v"]
    for i, e in enumerate(W["ears"]):
        e.rotation_euler = (0, 0, (0.45 * math.sin((t - 0.0) * 14.0) * tw) * (1 if i else 0))
    # ---- the spatula in Dad's right hand, dropped at the cue
    sp = W["spat"]
    ts = None
    for c in tl["cues"]:
        if c["name"] == "spat" and c.get("v", 0) >= 2:
            ts = c["t"]
    on = sample("spat", tl, t, {"v": 0.0})["v"]
    h = hand("dad", 1)
    if on >= 1 and h is not None:
        if ts is not None and t >= ts:
            dt = t - ts
            z = max(0.05, h.z - 4.9 * dt * dt) if dt < 0.5 else 0.05
            sp.location = (h.x, h.y - 0.05, z)
            sp.rotation_euler = (min(1.45, dt * 4.0), 0, 0.2 * min(dt, 0.4))
        else:
            sp.location = (h.x, h.y - 0.03, h.z + 0.02)
            sp.rotation_euler = (0.3, 0, 0)
    else:
        sp.location = (0, 0, -40)
    # ---- lights by mode (cut on the shot, no fade): returns light gains
    g = {}
    for nme in W["guest.day"]:
        g[nme] = 0.0 if mode == "dusk" else 1.0
    for nme in W["guest.dusk"]:
        g[nme] = 1.0 if mode == "dusk" else 0.0
    for nme in W["hall.wake"]:
        g[nme] = 0.0 if dream else 0.66
    for nme in W["hall.dream"]:
        g[nme] = 1.0 if dream else 0.0
    for ob in W["porch"]:
        g[ob] = 0.0 if dream else (0.8 if ob == "porch.sun" else 0.6)
    return g
