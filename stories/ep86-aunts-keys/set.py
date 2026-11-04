"""ep86-aunts-keys: Aunt Lou has a key to every house on the court; the thing trying the handles at midnight is me, asleep.

One bright, saturated, plastic world (the "closer" look): a horseshoe of twelve narrow red-brick houses round a stone
fountain, four iron lamps, ivy, brass handles and numeral plates (numbers only, no words anywhere).

Built here, from kit.py's parts:
- THE COURT: house k (1..12) stands at angle A0 + (k-1)*DA on a ring of radius R, its door facing the fountain. The
  house frame is local: origin at the door's foot, front toward -y, so make_story.py's helpers (same constants)
  can put a camera or a character in front of any door.
- THE RING: Aunt Lou's brass key ring (a hand in a mustard sleeve, a key turning in a lock, eleven numbered tags).
  The "ring" cue places it at a keyhole (or in the air) and turns the key.
- THE MARKER: the same ring as a round inset in the top-left of every frame, glued to the camera, with a teal glow
  on the tags of the doors she has locked ("tags" cue), and the porch-camera frame (brackets and a clock) on the
  footage shots ("clock" cue). Both are one transparent overlay plane.
- THE ROOM: one interior at (40, 0), re-dressed by the "room" cue (armchair, bed, table, stairs, lamp, blanket).
- LIGHT: day, night, dawn and indoor looks; each shot names one and the light ramps into the next look over the last
  0.35 s of the shot before a cut, so no light ever switches (flash bar).
Cues (story.json "cues", each restates its whole state): ring, tags, clock, room, pocket.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import bl_story, polish, rig

R = 11.0
A0 = -125.0
DA = 250.0 / 11
TMP = Path(tempfile.mkdtemp(prefix="auntskeys-"))
BRASS, TEAL, WARM = "#d8a93b", "#2ec4b6", "#ffcf7a"
ROOM = (40.0, 0.0)
MICRO = (60.0, 0.0)

_n = [0]


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


def mixhex(a, b, u):
    return tuple(lerp(x, y, u) / 255.0 for x, y in zip(hexrgb(a), hexrgb(b)))


class K:
    kit = None


def P(hexc, rough=0.45, spec=0.4):
    return K.kit.plastic(hexc, rough, spec=spec)


def B(parent, size, loc, mat, name="b", bevel=0.0, rot=(0, 0, 0)):
    return K.kit.box(nm(name), size, loc, mat, parent, rot, bevel)


def E(parent, loc=(0, 0, 0), name="e", rot=(0, 0, 0)):
    return K.kit.empty(nm(name), loc, parent, rot)


def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


def no_shadow(ob):
    try:
        ob.visible_shadow = False
    except Exception:
        pass


def house_xf(k):
    a = math.radians(A0 + (k - 1) * DA)
    return R * math.sin(a), R * math.cos(a), -a


# ---------------------------------------------------------------------------------------------------- images
def _font(size, bold=True):
    from PIL import ImageFont

    for f in ("DejaVuSans-Bold.ttf", "DejaVuSansMono-Bold.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except Exception:
            continue
    return ImageFont.load_default()


def numeral_image(n, bg, fg, size=128, name="num"):
    from PIL import Image, ImageDraw

    p = TMP / f"{name}-{n}-{bg[1:]}.png"
    if not p.exists():
        im = Image.new("RGB", (size, size), hexrgb(bg))
        d = ImageDraw.Draw(im)
        f = _font(int(size * (0.62 if n < 10 else 0.52)))
        txt = str(n)
        bb = d.textbbox((0, 0), txt, font=f)
        d.text(((size - (bb[2] - bb[0])) / 2 - bb[0], (size - (bb[3] - bb[1])) / 2 - bb[1]), txt, fill=hexrgb(fg), font=f)
        im.save(p)
    return str(p)


def imgmat(path, rough=0.5, emit=0.0):
    kit = K.kit
    key = f"img {path} {rough} {emit}"
    if key in kit.MATS:
        return kit.MATS[key]
    m = kit._new(key)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tex = nt.nodes.new("ShaderNodeTexImage")
    im = bpy.data.images.load(path, check_existing=True)
    im.colorspace_settings.name = "sRGB"
    tex.image = im
    gc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    if emit:
        for k in ("Emission Color", "Emission"):
            if k in b.inputs:
                nt.links.new(tex.outputs["Color"], b.inputs[k])
                break
        if "Emission Strength" in b.inputs:
            b.inputs["Emission Strength"].default_value = emit
    kit._fogged(m, b.outputs[0])
    return m


# ---------------------------------------------------------------------------------------------------- looks
LOOKS = {
    "day": {"sky": "#8fd0ff", "world": 1.0, "sun": 4.5, "moon": 0.0, "fill": 0.30, "lamp": 0.0, "water": 0.7, "exp": 0.0, "room": 0.0},
    "dusk": {"sky": "#7a8fc8", "world": 0.7, "sun": 0.0, "moon": 1.2, "fill": 0.55, "lamp": 1.0, "water": 2.0, "exp": 0.35, "room": 0.0},
    "night": {"sky": "#2a5478", "world": 0.32, "sun": 0.0, "moon": 0.8, "fill": 0.55, "lamp": 1.0, "water": 2.6, "exp": 0.45, "room": 0.0},
    "dawn": {"sky": "#ffc9a0", "world": 0.9, "sun": 2.4, "moon": 0.0, "fill": 0.4, "lamp": 0.45, "water": 1.4, "exp": 0.1, "room": 0.0},
    "int": {"sky": "#9cb8d8", "world": 0.55, "sun": 0.0, "moon": 0.0, "fill": 0.5, "lamp": 0.0, "water": 0.7, "exp": 0.2, "room": 1.0},
    "intn": {"sky": "#35688c", "world": 0.35, "sun": 0.0, "moon": 0.0, "fill": 0.42, "lamp": 0.0, "water": 0.7, "exp": 0.3, "room": 0.75},
}


def mix_look(a, b, u):
    out = {}
    for k in a:
        if k == "sky":
            out[k] = mixhex(a[k], b[k], u)
        else:
            out[k] = lerp(a[k], b[k], u)
    return out


def look_at(ctx, tl, t):
    shots = tl["shots"]
    cur = next((s for s in shots if s["start"] <= t < s["end"]), shots[-1])
    i = shots.index(cur)
    A = LOOKS[ctx["shots"][cur["id"]].get("look", "day")]
    if i + 1 < len(shots) and t > cur["end"] - 0.35:
        nb = LOOKS[ctx["shots"][shots[i + 1]["id"]].get("look", "day")]
        if nb is not A:
            return mix_look(A, nb, ss((t - (cur["end"] - 0.35)) / 0.35)), cur
    return mix_look(A, A, 0.0), cur


# ---------------------------------------------------------------------------------------------------- the court
BRICKS = ["#e0735a", "#cf5f48", "#d96a4e", "#c9573f"]
DOORS = {1: "#a9713c", 2: "#2a9d9a", 3: "#2c4a8a", 4: "#c0272d", 5: "#3f8f4a", 6: "#7a3b6e", 7: "#f4efe4", 8: "#e8782a",
         9: "#3a7fd0", 10: "#e8c040", 11: "#d96a8c", 12: "#2f6f55"}
IVY = {3: (-1.2, 2.2, 1.0, 3.6), 6: (1.3, 1.5, 1.0, 4.2), 9: (-1.3, 1.8, 1.0, 3.0), 11: (1.2, 1.4, 1.1, 3.8), 2: (1.4, 1.2, 0.9, 2.6),
       12: (-1.2, 1.4, 1.0, 3.2)}


def build_house(kit, ctx, k):
    ox, oy, rz = house_xf(k)
    H = E(None, (ox, oy, 0), f"house{k}", (0, 0, rz))
    brick = kit.texture("brick", 0.8, tint=BRICKS[k % 4])
    roof = P("#58485a", 0.7, 0.1)
    white = P("#f6f1e6", 0.5)
    brass = P(BRASS, 0.3, 0.9)
    B(H, (3.7, 4.2, 6.2), (0, 2.1, 3.1), brick, "body")
    B(H, (4.0, 4.6, 0.3), (0, 2.2, 6.35), roof, "roof")
    B(H, (0.5, 0.5, 1.0), (1.1, 3.0, 7.0), brick, "chimney")
    B(H, (3.9, 0.3, 0.12), (0, -0.15, 0.06), P("#bdb5a6", 0.8), "plinth")
    # door (hinged at its left edge so it can open), frame, step, handle plate and knob; a lit or dark recess behind it
    B(H, (1.2, 0.07, 2.28), (0, -0.035, 1.14), white, "frame")
    glowdoor = k in (1, 7)
    B(H, (0.96, 0.012, 2.06), (0, -0.024, 1.03), kit.emit("#ffcf8a", 1.3, name="recess warm") if glowdoor else P("#2a2230", 0.9), "recess")
    Hg = E(H, (-0.5, 0, 0), f"hinge{k}")
    ctx["hinges"][k] = Hg
    B(Hg, (1.0, 0.09, 2.1), (0.5, -0.075, 1.05), P(DOORS[k], 0.4), "door")
    B(H, (1.6, 0.55, 0.14), (0, -0.45, 0.07), P("#cfc7b8", 0.8), "step")
    if k == 1:   # a plain latch, no lock
        B(Hg, (0.04, 0.06, 0.22), (0.88, -0.14, 1.0), brass, "latch")
        B(Hg, (0.14, 0.04, 0.03), (0.88, -0.17, 1.08), brass, "lever")
    else:
        B(Hg, (0.10, 0.02, 0.22), (0.88, -0.13, 0.78), brass, "lockplate")
        B(Hg, (0.018, 0.012, 0.05), (0.88, -0.145, 0.78), P("#15131a", 0.9), "keyhole")
        kit.sphere(nm("knob"), 0.05, (0.88, -0.17, 0.96), brass, Hg, seg=12)
        # a deadbolt above the knob (its keyhole is where the hook's key goes): a round brass plate, a dark slot
        kit.cyl(nm("dbplate"), 0.075, 0.022, (0.88, -0.14, 1.3), brass, Hg, rot=(math.pi / 2, 0, 0), n=18)
        B(Hg, (0.016, 0.012, 0.05), (0.88, -0.155, 1.3), P("#15131a", 0.9), "dbhole")
    # number plate (numerals only), 2 cm proud of the wall
    pl = kit.plane(nm("plate"), (0.36, 0.24), (0, -0.02, 2.6), imgmat(numeral_image(k, BRASS, "#3a2a14", name="plate"), 0.4), H,
                   rot=(math.pi / 2, 0, 0))
    # windows
    for (wx, wz, ww, wh) in ((-0.95, 4.3, 0.8, 1.0), (0.95, 4.3, 0.8, 1.0), (-1.3, 1.5, 0.55, 0.8), (1.3, 1.5, 0.55, 0.8)):
        if k == 1 and wx < -1.0 and wz < 2:
            continue
        B(H, (ww + 0.14, 0.06, wh + 0.14), (wx, -0.03, wz), white, "wframe")
        pane = P("#bfe3f5", 0.1, 0.8)
        if k == 1 and wx < 0 and wz > 3:
            pane = ctx["lou_win"]
        B(H, (ww, 0.05, wh), (wx, -0.06, wz), pane, "pane")
        B(H, (0.04, 0.07, wh), (wx, -0.075, wz), white, "mullion")
        B(H, (ww, 0.07, 0.04), (wx, -0.075, wz), white, "transom")
    # porch lamp
    B(H, (0.12, 0.16, 0.12), (0.95, -0.1, 2.5), P("#2b2f3a", 0.5), "lampbracket")
    B(H, (0.14, 0.14, 0.2), (0.95, -0.2, 2.45), kit.emit(WARM, 6.0, name="porchbulb"), "porchbulb")
    ctx["porch"].append(kit.light(f"porch{k}", "POINT", (0.95, -0.4, 2.4), 70 if k in (1, 7) else 30, WARM, size=0.15,
                                  parent=H, shadow=k in (1, 7)))
    if k in IVY:
        x0, w, z0, z1 = IVY[k]
        gcol = ["#4fae5a", "#3f9a4c", "#5cbf62"]
        for i in range(14):
            sx = x0 + 0.38 * ((i * 7) % 5) * (0.9 if x0 < 0 else -0.9) * 0.6
            B(H, (0.45, 0.07, 0.42), (sx, -0.05 - 0.02 * (i % 3), z0 + (z1 - z0) * ((i * 3) % 7) / 7.0), P(gcol[i % 3], 0.8), "ivy")
    if k == 1:   # the key shop window: a display board with blank keys on hooks
        wood = P("#6b4a2e", 0.6)
        B(H, (1.3, 0.1, 1.5), (-1.25, -0.06, 1.55), wood, "shopframe")
        B(H, (1.15, 0.05, 1.35), (-1.25, -0.115, 1.55), P("#2c6b72", 0.7), "shopboard")
        bk = P(BRASS, 0.3, 0.9)
        for r in range(3):
            for c in range(5):
                x, z = -1.7 + 0.2 * c, 1.15 + 0.4 * r + 0.08 * (c % 2)
                B(H, (0.02, 0.012, 0.2), (x, -0.15, z), bk, "blankkey")
                B(H, (0.07, 0.012, 0.07), (x, -0.15, z + 0.13), bk, "blankbow")
    if k == 7:   # my new doormat and the porch camera on its bracket
        B(H, (0.95, 0.6, 0.03), (0, -1.0, 0.015), P("#2fb5a8", 0.9, 0.05), "mat")
        B(H, (0.7, 0.4, 0.035), (0, -1.0, 0.03), P("#f2c14e", 0.9, 0.05), "matinner")
        B(H, (0.08, 0.25, 0.08), (-0.9, -0.2, 3.05), P("#2b2f3a", 0.5), "camarm")
        cam = B(H, (0.2, 0.26, 0.14), (-0.9, -0.42, 3.0), P("#d9dce2", 0.35, 0.6), "porchcam", 0.02)
        kit.cyl(nm("camlens"), 0.045, 0.06, (-0.9, -0.58, 3.0), P("#15131a", 0.2), H, rot=(math.pi / 2, 0, 0), n=14)
    return H


def build_court(kit, ctx):
    lawn = kit.texture("grass", 0.6, tint="#7ed25a")
    B(None, (500, 500, 0.4), (0, 0, -0.25), lawn, "lawn")
    kit.cyl("courtfloor", 14.2, 0.12, (0, 0, -0.03), kit.texture("concrete", 0.5, tint="#e6d8bd"), None, n=48)
    kit.cyl("courtring", 6.6, 0.125, (0, 0, -0.025), P("#d3c4a8", 0.8), None, n=48)
    ctx["porch"] = []
    ctx["hinges"] = {}
    ctx["lou_win"] = kit.emit("#ffcf7a", 0.8, name="louwindow")
    ctx["houses"] = [build_house(kit, ctx, k) for k in range(1, 13)]
    # the fountain: a stone basin with a teal-lit pool, a column and a bowl
    stone, stone2 = P("#d8d2c4", 0.75, 0.1), P("#bdb6a6", 0.75, 0.1)
    kit.cyl("basin", 2.4, 0.62, (0, 0, 0.31), stone, None, n=40)
    kit.cyl("basinrim", 2.55, 0.12, (0, 0, 0.62), stone2, None, n=40)
    ctx["water"] = kit.emit(TEAL, 1.0, name="water")
    kit.cyl("pool", 2.2, 0.04, (0, 0, 0.62), ctx["water"], None, n=40)
    kit.cyl("column", 0.32, 1.5, (0, 0, 1.2), stone, None, n=20)
    kit.cyl("bowl", 0.5, 0.28, (0, 0, 1.95), stone2, None, n=28, r2=1.0)
    kit.sphere("fball", 0.28, (0, 0, 2.28), stone, None, seg=16)
    ctx["fountainlight"] = kit.light("fountain", "POINT", (0, 0, 1.6), 260, TEAL, size=0.5, shadow=False)
    # the drain hatch's tally: two brass strokes (lore), low on the basin facing -y
    B(None, (0.5, 0.04, 0.32), (0.0, -2.32, 0.3), P("#3b3f4a", 0.5), "hatch")
    for sx in (-1, 1):
        B(None, (0.03, 0.02, 0.2), (sx * 0.07, -2.35, 0.3), P(BRASS, 0.3, 0.9), "tally")
    # two benches
    wood = P("#7a5230", 0.6)
    for sx in (-1, 1):
        B(None, (0.5, 1.9, 0.08), (sx * 3.7, 0, 0.5), wood, "bench")
        B(None, (0.5, 0.1, 0.5), (sx * 3.7, 0.8, 0.25), stone2, "benchleg")
        B(None, (0.5, 0.1, 0.5), (sx * 3.7, -0.8, 0.25), stone2, "benchleg")
    # four iron lamps
    iron = P("#2b2f3a", 0.5, 0.3)
    ctx["lamps"] = []
    for i, (lx, ly) in enumerate(((-5.5, 5.5), (5.5, 5.5), (-5.5, -5.5), (5.5, -5.5))):
        kit.cyl(nm("lamppost"), 0.06, 3.2, (lx, ly, 1.6), iron, None, n=10)
        B(None, (0.34, 0.34, 0.1), (lx, ly, 3.25), iron, "lampcap")
        B(None, (0.28, 0.28, 0.42), (lx, ly, 3.05), kit.emit(WARM, 7.0, name="lampbulb"), "lanternbulb")
        ctx["lamps"].append(kit.light(f"lamp{i}", "POINT", (lx, ly, 2.8), 520, WARM, size=0.2, shadow=(i < 2)))
    # trees round the open side and behind the houses
    for i, (x, y, h) in enumerate(((-20, -20, 6.5), (15, -13, 7.0), (-20, 4, 7.5), (21, 6, 7.0), (0, 24, 8.0), (-9, -26, 7.0), (10, -28, 7.5))):
        try:
            kit.prop("commontree_1" if i % 2 == 0 else "birchtree_1", (x, y, 0), rot=37 * i, height=h, tint="#8fd860")
        except Exception:
            pass
    for (x, y) in ((-8.2, 7.0), (8.6, 4.4), (-12.5, -1.0), (12.8, -2.0)):
        try:
            kit.prop("bush_1", (x, y, 0), rot=x * 9, height=1.1, tint="#58c24a")
        except Exception:
            pass


# ---------------------------------------------------------------------------------------------------- Aunt Lou's ring
def build_ring(kit, ctx):
    """The ring group, origin at the keyhole, the key sticking out toward -y. Parts: keyg (key and bow, turns about y),
    ring and eleven tagged keys (hang from the bow), the sleeve and hand (mustard cuff)."""
    brass = P(BRASS, 0.28, 0.9)
    dark = P("#8a6a1e", 0.4, 0.8)
    root = E(None, (0, 0, -20), "ringroot")
    keyg = E(root, (0, 0, 0), "keyg")
    B(keyg, (0.010, 0.07, 0.016), (0, -0.03, 0.0), brass, "blade", 0.002)
    B(keyg, (0.010, 0.014, 0.010), (0, -0.015, -0.012), brass, "tooth", 0.002)
    B(keyg, (0.010, 0.012, 0.007), (0, -0.04, -0.011), brass, "tooth", 0.002)
    by = -0.075
    B(keyg, (0.056, 0.012, 0.009), (0, by, 0.019), brass, "bowt", 0.003)
    B(keyg, (0.056, 0.012, 0.009), (0, by, -0.019), brass, "bowb", 0.003)
    for sx in (-1, 1):
        B(keyg, (0.009, 0.012, 0.047), (sx * 0.0235, by, 0.0), brass, "bows", 0.003)
    # the big ring hangs through the bow's lower bar
    rc = (0.0, by - 0.002, -0.019 - 0.047)
    rr = 0.047
    for i in range(20):
        a = 2 * math.pi * i / 20
        B(root, (0.018, 0.009, 0.009), (rc[0] + rr * math.sin(a), rc[1], rc[2] + rr * math.cos(a)), dark, "ringseg", 0.002,
          rot=(0, math.pi / 2 - a, 0)) if False else B(root, (0.017, 0.008, 0.008), (rc[0] + rr * math.sin(a), rc[1], rc[2] + rr * math.cos(a)), dark,
                                                         "ringseg", 0.002, rot=(0, a + math.pi / 2, 0))
    # eleven keys with numbered round tags, 2..12, fanned below the ring
    ctx["tags3d"] = []
    for i in range(11):
        th = math.radians(-62 + i * 12.4)
        ang = math.pi - th
        ln = 0.07
        yy = by - 0.012 - 0.007 * (i % 3)
        ax, az = rc[0] + rr * math.sin(th), rc[2] - rr * math.cos(th)
        cx, cz = ax + math.sin(th) * ln / 2, az - math.cos(th) * ln / 2
        B(root, (0.008, 0.005, ln), (cx, yy, cz), brass, "tkey", 0.001, rot=(0, ang, 0))
        tx, tz = ax + math.sin(th) * (ln + 0.014), az - math.cos(th) * (ln + 0.014)
        n = i + 2
        tag = kit.cyl(nm("tag"), 0.021, 0.005, (tx, yy, tz), brass, root, rot=(math.pi / 2, 0, 0), n=18)
        kit.plane(nm("tagnum"), (0.034, 0.034), (tx, yy - 0.0065, tz), imgmat(numeral_image(n, BRASS, "#3a2a14", 96, "tag"), 0.4), root,
                  rot=(math.pi / 2, 0, 0))
    # the sleeve (mustard raincoat), a cardigan cuff and the hand block, coming in from +x
    mus = P("#ffc23a", 0.5, 0.2)
    B(root, (0.46, 0.15, 0.15), (0.35, by - 0.015, 0.07), mus, "sleeve", 0.02, rot=(0, 0, 0))
    B(root, (0.045, 0.125, 0.125), (0.105, by - 0.015, 0.07), P("#8a5a3a", 0.8), "cuff", 0.01)
    B(root, (0.07, 0.09, 0.075), (0.055, by - 0.012, 0.045), P("#f1c9a0", 0.5), "hand", 0.015)
    ctx["ring"] = (root, keyg)
    ctx["ring_hand"] = [o for o in root.children if o.name.startswith(("sleeve", "cuff", "hand"))]


def build_handarm(kit, ctx):
    """My green sleeve and hand on a knob (origin at the knob, reaching in from -y), for the rattling inserts."""
    grn = P("#2f7a4a", 0.8, 0.05)
    root = E(None, (0, 0, -20), "handroot")
    B(root, (0.17, 0.6, 0.17), (0.0, -0.42, 0.03), grn, "hsleeve", 0.03)
    B(root, (0.12, 0.12, 0.14), (0.0, -0.1, 0.0), P("#e8b88a", 0.5), "hhandb", 0.03)
    ctx["handarm"] = root
    pad = E(None, (0, 0, -20), "padroot")
    chrome = P("#e9edf2", 0.12, 0.95)
    B(pad, (0.12, 0.05, 0.1), (0, 0, 0), chrome, "padbody", 0.01)
    for sx in (-1, 1):
        B(pad, (0.016, 0.02, 0.07), (sx * 0.04, 0, 0.08), chrome, "padarm", 0.004)
    B(pad, (0.096, 0.02, 0.016), (0, 0, 0.12), chrome, "padtop", 0.004)
    ctx["padlock"] = pad


def place_ring(ctx, cue, t):
    root, keyg = ctx["ring"]
    if not cue or not cue.get("on"):
        root.location = (0, 0, -20)
        return
    px, py, pz = cue["pos"]
    root.location = (px, py, pz)
    root.scale = (cue.get("scale", 1.0),) * 3
    root.rotation_euler = (0, 0, math.radians(cue.get("yaw", 0)))
    a0, a1 = cue.get("turn", [0, 0])
    u = ss((t - cue["t"]) / max(1e-3, cue.get("dur", 1.0)))
    keyg.rotation_euler = (0, math.radians(lerp(a0, a1, u)), 0)
    for o in ctx["ring_hand"]:
        o.hide_render = not cue.get("hand", True)
    # a tiny sway of the ring while it hangs
    root.rotation_euler = (0.04 * math.sin(t * 2.1) + math.radians(cue.get("tilt", 0)), 0, math.radians(cue.get("yaw", 0)))


# ---------------------------------------------------------------------------------------------------- the overlay
def draw_keys(d, x0, y0, zoom, S, glow):
    """key ring: a wide brass loop across the top and eleven keys hanging from it, each a round numbered bow over a toothed blade"""
    z=zoom*S
    brass=hexrgb(BRASS)+(255,); dark=(90,62,20,255)
    pw,ph=214*z,100*z
    d.rounded_rectangle([x0,y0,x0+pw,y0+ph],16*z,fill=(22,30,46,215),outline=brass,width=max(2,int(4*z)))
    # the loop
    lx0,ly0,lx1,ly1=x0+10*z,y0+10*z,x0+pw-10*z,y0+40*z
    d.ellipse([lx0,ly0,lx1,ly1],outline=brass,width=int(6*z))
    d.ellipse([lx0-1*z,ly0-1*z,lx1+1*z,ly1+1*z],outline=dark,width=max(1,int(1.5*z)))
    f=_font(int(12.5*z))
    n=11; sp=18.2*z
    for i in range(n):
        nn=i+2
        bx=x0+pw/2+(i-(n-1)/2)*sp
        t=(i-(n-1)/2)/((n-1)/2)           # -1..1
        by=y0+ly1-y0-4*z+ 0*z + (abs(t)**2)*(-0)  # bow centre y: just under the loop
        # the loop's lower edge follows the ellipse
        cx,cy=(lx0+lx1)/2,(ly0+ly1)/2
        ey=cy+ (ly1-ly0)/2*math.sqrt(max(0,1-((bx-cx)/((lx1-lx0)/2))**2))
        by=ey+9*z
        r=9.4*z
        # blade
        bl=26*z+ (5*z if i%3==1 else 0)
        w=3.4*z
        d.rectangle([bx-w,by+r-2*z,bx+w,by+r+bl],fill=brass,outline=dark)
        for k in (0.4,0.7):
            yy=by+r+bl*k
            d.rectangle([bx+w,yy,bx+w+4*z,yy+5*z],fill=brass,outline=dark)
        lit=nn in glow
        if lit:
            d.ellipse([bx-r-5*z,by-r-5*z,bx+r+5*z,by+r+5*z],fill=(46,196,182,130))
            d.ellipse([bx-r,by-r,bx+r,by+r],fill=(60,235,215,255),outline=(255,255,255,255),width=max(2,int(2*z)))
        else:
            d.ellipse([bx-r,by-r,bx+r,by+r],fill=brass,outline=dark,width=max(2,int(2*z)))
        tx=str(nn); bb=d.textbbox((0,0),tx,font=f)
        d.text((bx-(bb[2]-bb[0])/2-bb[0],by-(bb[3]-bb[1])/2-bb[1]),tx,fill=(24,30,40,255),font=f)


def ring_marker_image(glow, clock, day, big=False):
    """RGBA, 540 x 960: the key-ring inset (top left) with glowing tags, and the porch camera's brackets and clock."""
    from PIL import Image, ImageDraw

    key = (tuple(sorted(glow)), clock, day)
    p = TMP / ("ov-" + "-".join(map(str, key[0])) + f"-{(clock or 'x').replace(':', '')}-{day or 0}{'-big' if big else ''}.png")
    if p.exists():
        return str(p)
    W, H = 540, 960
    S = 2
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    zoom = 2.0 if big else 1.0
    x0 = (270 - 107 * zoom) * S if big else 16 * S
    y0 = (400 - 66 * zoom) * S if big else 34 * S
    draw_keys(d, x0, y0, zoom, S, glow)
    if clock and not big:
        m, L, w = 26 * S, 54 * S, 5 * S
        wh = (255, 255, 255, 235)
        for (x0, y0, sx, sy) in ((m, m, 1, 1), (W * S - m, m, -1, 1), (m, H * S - m, 1, -1), (W * S - m, H * S - m, -1, -1)):
            d.line([(x0, y0), (x0 + sx * L, y0)], fill=wh, width=w)
            d.line([(x0, y0), (x0, y0 + sy * L)], fill=wh, width=w)
        cf = _font(40 * S)
        bb = d.textbbox((0, 0), clock, font=cf)
        x1 = W * S - m - 12 * S - (bb[2] - bb[0])
        y1 = m + 14 * S
        d.rounded_rectangle([x1 - 10 * S, y1 - 6 * S, x1 + (bb[2] - bb[0]) + 10 * S, y1 + (bb[3] - bb[1]) + 14 * S], 8 * S, fill=(10, 16, 26, 170))
        d.text((x1 - bb[0], y1 - bb[1]), clock, fill=(255, 255, 255, 255), font=cf)
        if day:
            dx = x1 - 62 * S
            d.rounded_rectangle([dx, y1 - 6 * S, dx + 48 * S, y1 + (bb[3] - bb[1]) + 14 * S], 8 * S, fill=(10, 16, 26, 170),
                                outline=(255, 255, 255, 230), width=3 * S)
            f2 = _font(36 * S)
            b2 = d.textbbox((0, 0), str(day), font=f2)
            d.text((dx + 24 * S - (b2[2] - b2[0]) / 2 - b2[0], y1 + 4 * S - b2[1]), str(day), fill=(255, 255, 255, 255), font=f2)
    im = im.resize((W, H), Image.LANCZOS)
    im.save(p)
    return str(p)


def build_overlay(kit, ctx):
    cam = kit.OBJ["cam"]
    m = kit._new(nm("overlay"))
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 1.15
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tc.outputs["Generated"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    nt.links.new(tex.outputs["Alpha"], mx.inputs["Fac"])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    pl = kit.plane(nm("overlay"), (1.0, 1.0), (0, 0, -0.15), m, cam)
    no_shadow(pl)
    try:
        pl.visible_glossy = False
        pl.visible_transmission = False
    except Exception:
        pass
    ctx["overlay"] = (pl, tex)
    ctx["ov_imgs"] = {}


def place_overlay(kit, ctx, tl, t, lens):
    pl, tex = ctx["overlay"]
    tg = cue_at(tl, "tags", t)
    glow, big = tg.get("glow", []), bool(tg.get("big"))
    ck = cue_at(tl, "clock", t)
    clock, day = ck.get("text"), ck.get("day")
    key = (tuple(sorted(glow)), clock, day, big)
    if key not in ctx["ov_imgs"]:
        im = bpy.data.images.load(ring_marker_image(glow, clock, day, big))
        im.colorspace_settings.name = "sRGB"
        im.alpha_mode = "STRAIGHT"
        ctx["ov_imgs"][key] = im
    tex.image = ctx["ov_imgs"][key]
    d = 0.15
    unit = d / lens
    pl.location = (0, 0, -d)
    pl.scale = (13.5 * unit, 24.0 * unit, 1)


def cue_at(tl, name, t):
    out = {}
    for c in tl.get("cues", []):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c
    return out


# ---------------------------------------------------------------------------------------------------- interior + micro set
def armchair(parent, fabric):
    g = E(parent, (0, 0, 0), "armchair")
    f = P(fabric, 0.8, 0.1)
    B(g, (1.0, 0.95, 0.4), (0, 0, 0.3), f, "seat", 0.05)
    B(g, (1.0, 0.22, 1.1), (0, 0.45, 0.85), f, "back", 0.05, rot=(-0.18, 0, 0))
    for sx in (-1, 1):
        B(g, (0.2, 0.95, 0.65), (sx * 0.6, 0, 0.5), f, "arm", 0.05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            B(g, (0.08, 0.08, 0.12), (sx * 0.45, sy * 0.4, 0.06), P("#4a3220", 0.6), "foot")
    return g


def build_room(kit, ctx):
    rx, ry = ROOM
    parts = {}
    wall = P("#f3e3c8", 0.9, 0.05)
    floor = kit.texture("wood", 0.7, tint="#f1d8b0")
    B(None, (7.0, 6.0, 0.1), (rx, ry, -0.05), floor, "rfloor")
    ctx["room_wall"] = P("#f3e3c8", 0.9, 0.05)
    parts["back"] = B(None, (7.0, 0.12, 3.0), (rx, ry + 3.0, 1.5), wall, "rback")
    parts["left"] = B(None, (0.12, 6.0, 3.0), (rx - 3.5, ry, 1.5), P("#efd9b4", 0.9, 0.05), "rleft")
    parts["right"] = B(None, (0.12, 6.0, 3.0), (rx + 3.5, ry, 1.5), P("#efd9b4", 0.9, 0.05), "rright")
    B(None, (7.0, 0.14, 0.14), (rx, ry + 2.93, 0.07), P("#ffffff", 0.5), "rbase")
    # the door on the back wall (a house door seen from inside) and a window on the left wall
    for key, colr in (("door_a", "#2c4a8a"), ("door_b", "#f4efe4")):
        g = parts[key] = E(None, (rx, ry, 0), "r" + key)
        B(g, (1.2, 0.07, 2.25), (0.4, 2.92, 1.13), P("#f6f1e6", 0.5), "rdframe")
        B(g, (1.0, 0.08, 2.1), (0.4, 2.88, 1.05), P(colr, 0.4), "rdoor")
        B(g, (0.1, 0.03, 0.2), (0.7, 2.82, 0.8), P(BRASS, 0.3, 0.9), "rdplate")
        B(g, (0.03, 0.03, 0.09), (0.7, 2.79, 0.8), P(BRASS, 0.3, 0.9), "rdbolt")
        if key == "door_b":   # my brass thumb-turn: a round base and a bar that turns about the y axis
            kit.cyl(nm("tbase"), 0.06, 0.03, (0.7, 2.815, 1.1), P(BRASS, 0.3, 0.9), g, rot=(math.pi / 2, 0, 0), n=18)
            parts["thumb"] = E(g, (0.7, 2.79, 1.1), "thumb")
            B(parts["thumb"], (0.22, 0.04, 0.06), (0, 0, 0), P(BRASS, 0.3, 0.9), "tbar", 0.015)
        kit.sphere(nm("rdknob"), 0.05, (0.7, 2.8, 0.98), P(BRASS, 0.3, 0.9), g, seg=12)
    parts["clock"] = E(None, (0, 0, 0), "rclock")
    kit.cyl(nm("clockface"), 0.24, 0.04, (rx - 1.2, ry + 2.88, 2.1), P("#f6f1e6", 0.4), parts["clock"], rot=(math.pi / 2, 0, 0), n=24)
    B(parts["clock"], (0.02, 0.02, 0.17), (rx - 1.2, ry + 2.85, 2.16), P("#2b2f3a", 0.5), "hhand")
    B(parts["clock"], (0.13, 0.02, 0.02), (rx - 1.14, ry + 2.85, 2.1), P("#2b2f3a", 0.5), "mhand")
    parts["grass"] = E(None, (0, 0, 0), "rgrass")
    for i in range(16):
        B(parts["grass"], (0.06, 0.4, 0.02), (rx + 0.9 + 0.12 * ((i * 5) % 7) - 0.3, ry + 0.2 + 0.14 * ((i * 3) % 6), 0.01 + 0.002 * i),
          P("#4fae5a" if i % 2 else "#3f9a4c", 0.8), "blade", rot=(0, 0, 0.5 * ((i * 7) % 6) - 1.2))
    for i, (gx, gy) in enumerate(((1.15, 0.5), (1.7, 0.3), (1.35, 0.9))):
        kit.cyl(nm("wet"), 0.16 - 0.02 * i, 0.006, (rx + gx, ry + gy, 0.012), P("#8a7a62", 0.12, 0.9), parts["grass"], n=16)
    parts["window"] = E(None, (rx, ry, 0), "rwindow")
    B(parts["window"], (0.08, 1.3, 1.5), (-3.42, 0.8, 1.6), P("#ffffff", 0.5), "rwframe")
    B(parts["window"], (0.05, 1.1, 1.3), (-3.38, 0.8, 1.6), kit.emit("#ffcf7a", 0.4, name="rwpane"), "rwpane")
    # a second lit window on the back wall (behind Lou when she laughs at it), proud of the wall by 2.5 cm
    B(parts["window"], (1.3, 0.04, 1.5), (-2.4, 2.91, 1.7), P("#7a4a28", 0.5), "rwframe2")
    B(parts["window"], (1.1, 0.03, 1.3), (-2.4, 2.88, 1.7), kit.emit("#ffcf7a", 0.7, name="rwpane2"), "rwpane2")
    # furniture
    parts["armchair"] = armchair(None, "#c48a3a")
    parts["armchair"].location = (rx + 0.0, ry + 0.95, 0)
    parts["armchair"].rotation_euler = (0, 0, math.pi)       # its back toward the front of the room... turned later by cue
    parts["bed"] = kit.prop("bed_single", (rx + 1.9, ry + 1.6, 0), rot=0, scale=1.0, tint="#e8b8a0")
    parts["table"] = E(None, (0, 0, 0), "rtable")
    kit.prop("table_roundsmall", (rx + 1.2, ry + 1.0, 0), rot=0, scale=1.3, parent=parts["table"])
    kit.cyl(nm("mug"), 0.05, 0.1, (rx + 1.05, ry + 0.95, 0.86), P("#f2f2ee", 0.4), parts["table"], n=14)
    parts["lamp"] = E(None, (0, 0, 0), "rlamp")
    B(parts["lamp"], (0.3, 0.3, 0.05), (rx + 2.9, ry + 2.3, 0.72), P("#7a5230", 0.6), "lampbase")
    kit.cyl(nm("lampshade"), 0.18, 0.28, (rx + 2.9, ry + 2.3, 0.95), kit.emit("#ffd9a0", 3.0, name="shade"), parts["lamp"], n=16, r2=0.12)
    B(parts["lamp"], (0.55, 0.55, 0.7), (rx + 2.9, ry + 2.3, 0.35), P("#a0714a", 0.6), "nightstand")
    parts["stairs"] = E(None, (0, 0, 0), "rstairs")
    for i in range(7):
        B(parts["stairs"], (1.0, 0.4, 0.22 * (i + 1)), (rx + 2.7, ry - 0.8 + 0.4 * i, 0.11 * (i + 1)), P("#b98a5a" if i % 2 else "#a97a4a", 0.6), "stair")
    parts["rail"] = B(parts["stairs"], (0.08, 3.0, 0.1), (rx + 2.15, ry + 0.6, 1.1), P("#7a5230", 0.6), "stairrail", 0.01, rot=(0.0, 0.0, 0.0))
    # a moving box, a kitchen table for the morning scenes
    parts["kitchen"] = E(None, (0, 0, 0), "rkitchen")
    kit.prop("table_roundlarge", (rx - 0.2, ry + 0.4, 0), scale=1.0, parent=parts["kitchen"])
    kit.cyl(nm("kmug"), 0.06, 0.11, (rx - 0.5, ry + 0.2, 0.8), P("#f2f2ee", 0.4), parts["kitchen"], n=14)
    B(parts["kitchen"], (0.55, 0.55, 0.05), (rx + 2.9, ry - 1.0, 0.025), P("#2fb5a8", 0.9, 0.05), "rug")
    parts["kitchen_ring"] = None
    ctx["room_parts"] = parts
    ctx["roomlights"] = [
        kit.light("roomkey", "POINT", (rx - 1.0, ry - 1.5, 2.7), 260, "#fff0d8", size=0.4, shadow=False),
        kit.light("roomwarm", "POINT", (rx + 2.6, ry + 1.8, 1.5), 25, "#ffb866", size=0.3, shadow=False),
    ]


ROOM_ITEMS = ("armchair", "bed", "table", "lamp", "stairs", "door_a", "door_b", "window", "kitchen", "clock", "grass")


def build_micro(kit, ctx):
    """S13: a green sleeve and hand putting one key into a hoodie pocket."""
    mx, my = MICRO
    g = E(None, (mx, my, 0), "micro")
    grn = P("#2f7a4a", 0.8, 0.05)
    B(g, (0.9, 0.35, 1.3), (0, 0.25, 0.9), grn, "mtorso", 0.04)
    B(g, (0.62, 0.05, 0.3), (0, 0.06, 0.58), P("#276540", 0.8), "mpocket", 0.015)
    B(g, (0.52, 0.05, 0.05), (0, 0.035, 0.7), P("#16121a", 0.9), "mslit")
    ctx["micro_arm"] = E(g, (0.3, -0.3, 0.9), "marm")
    B(ctx["micro_arm"], (0.17, 0.5, 0.17), (0, -0.1, 0.0), grn, "msleeve", 0.03)
    B(ctx["micro_arm"], (0.12, 0.12, 0.14), (0, -0.4, 0.0), P("#e8b88a", 0.5), "mhand", 0.03)
    B(ctx["micro_arm"], (0.012, 0.09, 0.03), (0, -0.52, 0.0), P(BRASS, 0.3, 0.9), "mkey", 0.003)
    B(ctx["micro_arm"], (0.012, 0.03, 0.05), (0, -0.58, 0.0), P(BRASS, 0.3, 0.9), "mkeybow", 0.003)
    B(g, (1.6, 0.3, 0.4), (0.0, 0.3, 0.2), P("#8a8d96", 0.8), "mhips")
    ctx["micro"] = g


# ---------------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    K.kit = kit
    ctx = {"story": story}
    ctx["shots"] = {s["id"]: s for s in story["shots"]}
    sc = bpy.context.scene
    ctx["bg"] = sc.world.node_tree.nodes["Background"]
    # lights
    ctx["sun"] = kit.light("sun", "SUN", (0, 0, 50), 4.5, "#fff1d8", size=0.1)
    ctx["sun"].data.angle = 0.06
    ctx["sun"].rotation_euler = (math.radians(50), math.radians(8), math.radians(-30))
    ctx["moon"] = kit.light("moon", "SUN", (0, 0, 50), 1.0, "#9fc4ff", size=0.1)
    ctx["moon"].data.angle = 0.3
    ctx["moon"].rotation_euler = (math.radians(55), math.radians(-10), math.radians(150))
    ctx["facekey"] = kit.light("facekey", "POINT", (0, 0, 5), 70, "#ffcf7a", size=0.3, shadow=False)
    ctx["facetea"] = kit.light("facetea", "POINT", (0, 0, 5), 30, "#2ec4b6", size=0.3, shadow=False)
    ctx["fill"] = kit.light("camfill", "POINT", (0, 0, 2), 60, "#fff0dc", size=0.6, shadow=False)
    build_court(kit, ctx)
    build_ring(kit, ctx)
    build_handarm(kit, ctx)
    build_room(kit, ctx)
    build_micro(kit, ctx)
    build_overlay(kit, ctx)
    ctx["late"] = False
    pol = polish.spec(story)
    ctx["camspecs"] = polish.cam_specs(story, tl, pol)
    return ctx


def late(kit, ctx):
    """Once the cast exists: Lou's blanket."""
    lou = rig.CHARS.get("lou")
    ctx["blanket"] = []
    me = rig.CHARS.get("me")
    ctx["mebox"], ctx["phone"] = [], []
    if me is not None:
        ctx["mebox"].append(B(me.torso, (1.7, 1.2, 1.3), (0.0, -1.15, 0.15), P("#c8995a", 0.85, 0.05), "mebox", 0.05))
        ctx["mebox"].append(B(me.torso, (1.72, 0.2, 0.16), (0.0, -1.15, 0.8), P("#e8d0a0", 0.85, 0.05), "meboxtape"))
        ctx["phone"].append(B(me.torso, (0.55, 0.06, 0.95), (0.0, -1.02, 1.0), kit.emit("#bfe3ff", 2.0, name="phonescreen"), "phone", 0.03,
                              rot=(-0.35, 0, 0)))
    if lou is not None:
        b = B(lou.torso, (1.7, 0.7, 1.0), (0.0, -0.8, 0.2), P("#c85a5a", 0.9, 0.05), "blanket", 0.08)
        b2 = B(lou.torso, (1.7, 0.72, 0.2), (0.0, -0.8, 0.45), P("#f2c14e", 0.9, 0.05), "blanketstripe", 0.03)
        ctx["blanket"] = [b, b2]


def animate(kit, story, tl, t, ctx):
    if not ctx["late"]:
        late(kit, ctx)
        ctx["late"] = True
    sc = bpy.context.scene
    L, cur = look_at(ctx, tl, t)
    sd = ctx["shots"][cur["id"]]
    ctx["bg"].inputs["Color"].default_value = (*(kit.srgb(c) for c in L["sky"]), 1.0)
    ctx["bg"].inputs["Strength"].default_value = L["world"]
    cl, ct, cl_lens, _ = bl_story.cam_at(ctx["camspecs"][cur["id"]], cur, t, {}, tl)
    ctx["fill"].location = (cl[0], cl[1], cl[2])
    dist = (V(cl) - V(ct)).length
    fgain = min(2.0, max(0.06, (dist / 3.0) ** 2))
    sc.view_settings.exposure = L["exp"] + sd.get("exp", 0.0)
    ov = {"sun": L["sun"] / 4.5, "moon": L["moon"], "camfill": L["fill"] * sd.get("fill", 1.0) * fgain, "fountain": 0.25 + 0.75 * min(1.0, L["lamp"] + 0.0),
          "roomkey": L["room"] * sd.get("rkey", 1.0), "roomwarm": L["room"]}
    for i in range(4):
        ov[f"lamp{i}"] = L["lamp"]
    for k in range(1, 13):
        ov[f"porch{k}"] = max(L["lamp"], 0.0) if k != 1 else max(L["lamp"], 0.0)
    # emissive things: lantern bulbs and the pool glow with the look, Lou's window is lit at night
    for nd in ctx["water"].node_tree.nodes:
        if nd.type == "EMISSION":
            nd.inputs["Strength"].default_value = L["water"]
    for nd in ctx["lou_win"].node_tree.nodes:
        if nd.type == "EMISSION":
            nd.inputs["Strength"].default_value = 0.45 + 0.5 * L["lamp"]
    # the sleepwalker's face: a warm lamp from the side and above, the fountain's teal from below, no flat frontal fill
    if sd.get("face"):
        fx, fy = ct[0] - cl[0], ct[1] - cl[1]
        n = max(1e-6, math.hypot(fx, fy))
        rx_, ry_ = fy / n, -fx / n
        ctx["facekey"].location = (ct[0] + rx_ * 1.0 - fx / n * 0.2, ct[1] + ry_ * 1.0 - fy / n * 0.2, ct[2] + 0.9)
        ctx["facetea"].location = (ct[0] - rx_ * 0.4 - fx / n * 0.8, ct[1] - ry_ * 0.4 - fy / n * 0.8, ct[2] - 1.0)
        ov["facekey"], ov["facetea"] = 1.0, 1.0
    else:
        ov["facekey"], ov["facetea"] = 0.0, 0.0
    # focus
    dof = sd.get("dof")
    cd = kit.OBJ["cam"].data
    if dof:
        cd.dof.use_dof = True
        cd.dof.focus_distance = dof[0]
        cd.dof.aperture_fstop = dof[1]
    else:
        cd.dof.use_dof = False
    # the ring
    place_ring(ctx, cue_at(tl, "ring", t), t)
    # the room's dressing
    rc = cue_at(tl, "room", t)
    parts = ctx["room_parts"]
    show = set(rc.get("show", []))
    for k in ROOM_ITEMS:
        hide(parts[k], k not in show)
    if "armchair" in show:
        parts["armchair"].rotation_euler = (0, 0, math.radians(rc.get("chair_yaw", 180)))
    if "bed" in show:
        parts["bed"].rotation_euler = (0, 0, math.radians(rc.get("bed_yaw", 0)))
    bl = cue_at(tl, "blanket", t)
    for o in ctx["blanket"]:
        hide(o, not bl.get("on"))
    for o in ctx["mebox"]:
        hide(o, not cue_at(tl, "box", t).get("on"))
    for o in ctx["phone"]:
        hide(o, not cue_at(tl, "phone", t).get("on"))
    bc = cue_at(tl, "bed", t)
    if bc.get("on"):
        hide(parts["bed"], False)
        pos_ = bc["pos"]
        if "to" in bc:
            u_ = ss((t - bc["t"]) / max(1e-3, bc["dur"]))
            pos_ = [lerp(a, b, u_) for a, b in zip(bc["pos"], bc["to"])]
        parts["bed"].location = tuple(pos_)
        parts["bed"].rotation_euler = (0, 0, math.radians(bc.get("yaw", 0)))
    # every door on the court swings on its hinge (cue "door<k>": a0 -> a1 degrees over dur)
    for k, hg in ctx["hinges"].items():
        dc = cue_at(tl, f"door{k}", t)
        ang_ = lerp(dc["a0"], dc["a1"], ss((t - dc["t"]) / max(1e-3, dc["dur"]))) if dc else 0.0
        hg.rotation_euler = (0, 0, -math.radians(ang_))
    # a hand on a knob (rattling or turning), a padlock
    hc = cue_at(tl, "hand", t)
    ha = ctx["handarm"]
    if hc.get("on"):
        sh = hc.get("shake", 0.0)
        ha.location = tuple(hc["pos"])
        ha.rotation_euler = (0.03 * sh * math.sin(t * 38.0), math.radians(lerp(hc.get("a0", 0), hc.get("a1", 0), ss((t - hc["t"]) / max(1e-3, hc.get("dur", 1.0))))) + 0.05 * sh * math.sin(t * 31.0), math.radians(hc.get("yaw", 0)))
    else:
        ha.location = (0, 0, -20)
    th = ctx["room_parts"].get("thumb")
    if th is not None:
        u_ = ss((t - hc["t"]) / max(1e-3, hc.get("dur", 1.0))) if hc.get("on") else 0.0
        th.rotation_euler = (0, math.radians(lerp(hc.get("a0", 0), hc.get("a1", 0), u_)) if hc.get("on") else 0.0, 0)
    pc = cue_at(tl, "padlock", t)
    ctx["padlock"].location = tuple(pc["pos"]) if pc.get("on") else (0, 0, -20)
    # the pocket scene (S13)
    pk = cue_at(tl, "pocket", t)
    mic = ctx["micro"]
    hide(mic, not pk.get("on"))
    if pk.get("on"):
        u = ss((t - pk["t"]) / max(1e-3, pk["dur"]))
        arm = ctx["micro_arm"]
        arm.location = (lerp(0.3, 0.12, u), lerp(-0.3, -0.02, u), lerp(0.95, 0.6, u))
        arm.rotation_euler = (0.0, 0.0, lerp(0.35, 0.0, u))
    place_overlay(kit, ctx, tl, t, cl_lens)
    return ov
