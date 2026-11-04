"""ep107 "returned days": Tulley's, a cheerful mint-and-cream returns shop with a back room of little gray boxes, plus
a handful of small places (Dad's kitchen, a roadside, a rainy step, a driveway, a lobby, my apartment).

The rule meter is a cream receipt tag in the top-left of every frame (a gray box glyph, 47 and a lit red "sold" ring,
and from L64 a second line: a key glyph and 1). It is a child of the camera.

Everything that moves is driven by cues in story.json (see animate): the look (sun, fill, sky), the shop lamps, the
doors, the bell, the bulb, objects that are carried or placed (gray boxes, a receipt, a stamp, a phone), the mailbox,
the coffee stain, the shimmer that comes off my shoulders, the flicking receipts and the tag.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {}
APZ = 3.4          # my apartment floor height (the street is below the window)


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def _L(**kw):
    base = dict(sun=1.8, sun_col="#fff0d8", el=50.0, az=150.0, fill=0.55, fill_col="#fff0e0", sky="#8fd3ff", sky_str=0.85,
                front=0.3, st=0.0)
    base.update(kw)
    return base


LOOKS = {
    "day": _L(),
    # closing time: low orange sun, the shop lamps still on
    "eve": _L(sun=1.5, sun_col="#ffb27a", el=12.0, az=150.0, fill=0.8, fill_col="#ffd8b8", sky="#f4a77f", sky_str=0.85,
              front=0.5, st=0.4),
    # night outside, and the shop at night
    "night": _L(sun=0.5, sun_col="#a9bcff", el=35.0, az=140.0, fill=0.6, fill_col="#9fb2f0", sky="#2e3d66", sky_str=0.6,
                front=0.6, st=1.0),
    # the back room: dim, one bulb, a pool of door glow
    "dim": _L(sun=0.55, sun_col="#b4c2ff", el=40.0, az=140.0, fill=0.55, fill_col="#a6b6f2", sky="#26335a", sky_str=0.55,
              front=0.9, st=1.0),
    "rain": _L(sun=1.0, sun_col="#c8d4e0", el=60.0, az=150.0, fill=1.1, fill_col="#c4d2e4", sky="#a3b4c8", sky_str=0.9,
               front=0.5, st=0.0),
}


def look_at(tl, t):
    cues = [c for c in tl["cues"] if c["name"] == "look"]
    cur = LOOKS[cues[0]["id"]] if cues else LOOKS["day"]
    prev = cur
    for c in cues:
        if c["t"] > t:
            break
        prev, cur = cur, LOOKS[c["id"]]
        dur = c.get("dur", 0.0)
        dur = 0.0 if dur <= 0 else max(0.4, dur)       # house bar: no switch faster than 0.3 s, unless set on a cut
        if t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            out = {}
            for k in cur:
                a, b = prev[k], cur[k]
                if isinstance(a, str):
                    ca, cb = kit_col(a), kit_col(b)
                    out[k] = tuple(ca[i] + (cb[i] - ca[i]) * u for i in range(3))
                else:
                    out[k] = a + (b - a) * u
            return out
    return {k: (kit_col(v) if isinstance(v, str) else v) for k, v in cur.items()}


def sample(name, tl, t, defaults):
    """The state of cue track `name` at t: numeric fields eased over a cue's own "dur"."""
    cues = [c for c in tl["cues"] if c["name"] == name]
    cur, prev = dict(defaults), dict(defaults)
    for c in cues:
        if c["t"] > t:
            break
        prev = dict(cur)
        cur.update({k: v for k, v in c.items() if k in defaults})
        dur = c.get("dur", 0.0)
        if dur > 0 and t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            return {k: (prev[k] + (cur[k] - prev[k]) * u if isinstance(cur[k], (int, float)) else cur[k]) for k in cur}
    return cur


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def merged(kit, name, boxes, mat, shadow=True):
    """Many boxes (cx, cy, cz, sx, sy, sz) as one mesh."""
    verts, faces = [], []
    for (cx, cy, cz, sx, sy, sz) in boxes:
        b = len(verts)
        verts += kit.box_verts(sx, sy, sz, (cx, cy, cz))
        faces += [tuple(i + b for i in f) for f in kit.BOX_FACES]
    ob = kit.mesh_obj(name, verts, faces, mat)
    return ob


def bx(kit, name, x0, x1, y0, y1, z0, z1, mat, parent=None, bevel=0.0):
    return kit.box(name, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), mat, parent, bevel=bevel)


def prop(kit, name, loc, **kw):
    try:
        return kit.prop(name, loc, **kw)
    except Exception:
        return None


def tree(kit, name, x, y, h=6.0, tint="#cfe8c0"):
    if prop(kit, "commontree_1", (x, y, 0), height=h, tint=tint) is None:
        kit.cyl(f"{name}.trunk", 0.3, h * 0.45, (x, y, h * 0.22), kit.plastic("#7a5230", 0.8), n=8)
        kit.sphere(f"{name}.crown", h * 0.28, (x, y, h * 0.68), kit.plastic("#5fae4a", 0.8), seg=10)


def bldg(kit, name, x, y, w, d, h, col, roof="#c4624a", face=-1, windows=True):
    wall = kit.grime(col, 0.9, 2.0, f"wall{col}", 0.9)
    kit.box(f"{name}.body", (w, d, h), (x, y, h / 2), wall)
    kit.box(f"{name}.roof", (w + 0.5, d + 0.5, 0.45), (x, y, h + 0.22), kit.plastic(roof, 0.7, spec=0.1))
    if windows:
        glass = kit.plastic("#6a9cc4", 0.2, spec=0.8)
        fr = kit.plastic("#fff4e0", 0.7)
        fy = y + face * (d / 2)
        n = max(1, int(w // 2.8))
        for i in range(n):
            wx = x - w / 2 + (i + 0.5) * w / n
            for wz in ([1.6, 3.6] if h > 4.6 else [1.8]):
                kit.box(f"{name}.fr{i}_{wz}", (1.3, 0.06, 1.4), (wx, fy + face * 0.03, wz), fr)
                kit.box(f"{name}.wn{i}_{wz}", (1.0, 0.06, 1.1), (wx, fy + face * 0.07, wz), glass)


def car(kit, name, x, y, yaw, colr, hood_up=False, lights=False):
    """A blocky car, nose toward +y at yaw 0 (its hood hinge at the front of the cabin)."""
    root = kit.empty(name, (x, y, 0), rot=(0, 0, yaw * D2R))
    body = kit.plastic(colr, 0.35, spec=0.5)
    glass = kit.plastic("#7fb2cc", 0.15, spec=0.9)
    dark = kit.plastic("#2a2c33", 0.6)
    kit.box(f"{name}.low", (1.8, 4.0, 0.55), (0, 0, 0.55), body, root, bevel=0.07)
    kit.box(f"{name}.cab", (1.6, 1.8, 0.62), (0, -0.55, 1.12), glass, root, bevel=0.07)
    kit.box(f"{name}.roof", (1.66, 1.9, 0.08), (0, -0.55, 1.46), body, root, bevel=0.03)
    kit.box(f"{name}.trunk", (1.76, 0.9, 0.12), (0, -1.55, 0.9), body, root, bevel=0.04)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"{name}.wh{sx}{sy}", 0.34, 0.22, (sx * 0.92, sy * 1.3, 0.34), dark, root, rot=(0, math.pi / 2, 0), n=14)
        kit.box(f"{name}.hl{sx}", (0.3, 0.06, 0.18), (sx * 0.62, 2.0, 0.62), kit.emit("#fff4cc", 3.0 if lights else 0.9), root)
        kit.box(f"{name}.tl{sx}", (0.3, 0.06, 0.16), (sx * 0.62, -2.0, 0.62), kit.emit("#e2463c", 1.2), root)
    hinge = kit.empty(f"{name}.hood", (0, 0.32, 0.84), root)
    kit.box(f"{name}.hoodp", (1.7, 1.55, 0.1), (0, 0.78, 0.0), body, hinge, bevel=0.04)
    if hood_up:
        hinge.rotation_euler = (-62 * D2R, 0, 0)
    return root


# ---------------------------------------------------------------------------------------------- gray boxes
def gray_box(kit, name, mat, mat2, sticker):
    """A little gray box with a lid hinged at its back edge, a date sticker and a string. Local -y is its front."""
    root = kit.empty(name, (0, 0, -50))
    kit.box(f"{name}.body", (0.34, 0.26, 0.2), (0, 0, 0.1), mat, root, bevel=0.015)
    hinge = kit.empty(f"{name}.hinge", (0, 0.13, 0.2), root)
    kit.box(f"{name}.lid", (0.36, 0.28, 0.05), (0, -0.13, 0.0), mat2, hinge, bevel=0.012)
    kit.box(f"{name}.stk", (0.12, 0.012, 0.075), (0, -0.136, 0.1), sticker, root)
    kit.box(f"{name}.str", (0.012, 0.012, 0.16), (0.08, -0.14, 0.13), kit.plastic("#f6efdc", 0.8), root)
    W["lids"][name] = hinge
    return root


# ---------------------------------------------------------------------------------------------- the shop
def shop(kit, P):
    mint, cream, brass, red, tan = P["mint"], P["cream"], P["brass"], P["red"], P["tan"]
    plastic = kit.plastic
    wallm = plastic("#b4ecd6", 0.85, spec=0.05)
    trim = plastic("#fff7e6", 0.7)
    kit.plane("sfloor", (16, 14), (0, 3, 0.02), kit.checker("#f6efdc", "#c9ecda", 1.0))
    H = 4.4
    # side walls and the back wall with the door
    bx(kit, "swl", -7.2, -7.0, -4.2, 10.2, 0, H, wallm)
    bx(kit, "swr", 7.0, 7.2, -4.2, 10.2, 0, H, wallm)
    bx(kit, "sbk0", -7.2, 1.87, 10.0, 10.2, 0, H, wallm)
    bx(kit, "sbk1", 3.27, 7.2, 10.0, 10.2, 0, H, wallm)
    bx(kit, "sbk2", 1.87, 3.27, 10.0, 10.2, 2.4, H, wallm)
    # the front wall: door gap at x -3.7..-2.3, window gap x 1..4, z 1..3
    bx(kit, "sf0", -7.2, -3.7, -4.2, -4.0, 0, H, wallm)
    bx(kit, "sf1", -2.3, 1.0, -4.2, -4.0, 0, H, wallm)
    bx(kit, "sf2", 4.0, 7.2, -4.2, -4.0, 0, H, wallm)
    bx(kit, "sf3", 1.0, 4.0, -4.2, -4.0, 0, 1.0, wallm)
    bx(kit, "sf4", 1.0, 4.0, -4.2, -4.0, 3.0, H, wallm)
    bx(kit, "sf5", -3.7, -2.3, -4.2, -4.0, 2.5, H, wallm)
    for nm, (sx, sz, px, pz) in {"a": (3.2, 0.1, 2.5, 2.0), "b": (0.1, 2.1, 2.5, 2.0), "c": (3.2, 0.1, 2.5, 1.0), "d": (3.2, 0.1, 2.5, 3.0)}.items():
        kit.box(f"swf{nm}", (sx, 0.08, sz), (px, -4.14, pz), trim)
    # the sign board above the door and window (a brass ring, no words)
    kit.box("sign", (4.4, 0.12, 0.9), (0.0, -4.26, 3.85), mint, bevel=0.03)
    kit.cyl("sign.ring", 0.3, 0.05, (0.0, -4.36, 3.85), brass, rot=(math.pi / 2, 0, 0), n=20)
    kit.cyl("sign.ringin", 0.2, 0.06, (0.0, -4.37, 3.85), mint, rot=(math.pi / 2, 0, 0), n=20)
    # the awning: mint and cream stripes
    sa, sb = plastic("#8fe0bf", 0.6), plastic("#fffaf0", 0.6)
    for i in range(14):
        kit.box(f"awn{i}", (1.0, 2.3, 0.08), (-6.5 + i * 1.0, -5.2, 3.3), sa if i % 2 else sb, rot=(-18 * D2R, 0, 0))
    # the front door (hinged at x = -3.7)
    fd = kit.empty("fdoor", (-3.7, -4.1, 0))
    kit.box("fdoor.leaf", (1.4, 0.1, 2.45), (0.7, 0, 1.225), plastic("#4fb894", 0.5, spec=0.3), fd)
    kit.box("fdoor.glass", (0.8, 0.12, 0.9), (0.7, 0, 1.6), kit.emit("#ffeab0", 0.9, "fdglow"), fd)
    kit.sphere("fdoor.knob", 0.07, (1.25, -0.08, 1.05), brass, fd, seg=8)
    W["fdoor"] = fd
    # the front bell over the door, on a bracket
    bell = kit.empty("fbell", (-3.0, -3.7, 2.8))
    kit.cyl("fbell.cup", 0.13, 0.16, (0, 0, -0.1), brass, bell, n=14, r2=0.05)
    kit.sphere("fbell.clap", 0.045, (0, 0, -0.2), brass, bell, seg=8)
    kit.box("fbell.arm", (0.04, 0.04, 0.2), (0, 0, 0.1), brass, bell)
    W["fbell"] = bell
    # the back-room door (hinged at x = 3.27, swings into the back room)
    bd = kit.empty("bdoor", (3.27, 10.06, 0))
    kit.box("bdoor.leaf", (1.4, 0.08, 2.4), (-0.7, 0, 1.2), plastic("#b98b5a", 0.7, spec=0.1), bd)
    kit.sphere("bdoor.knob", 0.06, (-1.2, -0.07, 1.05), brass, bd, seg=8)
    W["bdoor"] = bd
    # the counter, the brass bell, the stamp, the register
    kit.box("ctr", (9.0, 1.0, 0.92), (-1.0, G.COUNTER_Y, 0.46), mint, bevel=0.03)
    kit.box("ctr.top", (9.3, 1.3, 0.08), (-1.0, G.COUNTER_Y, 0.96), cream, bevel=0.02)
    for k in range(9):
        kit.box(f"ctr.stripe{k}", (0.5, 0.02, 0.5), (-4.8 + k * 1.1, G.COUNTER_Y - 0.51, 0.46), cream)
    bx_, by_ = G.BELL
    kit.cyl("cbell.base", 0.2, 0.05, (bx_, by_, 1.02), brass, n=16)
    kit.cyl("cbell.dome", 0.17, 0.14, (bx_, by_, 1.12), brass, n=16, r2=0.05)
    kit.sphere("cbell.knob", 0.05, (bx_, by_, 1.2), brass, seg=8)
    kit.box("reg", (0.9, 0.7, 0.45), (2.2, G.COUNTER_Y + 0.05, 1.26), plastic("#d9d4c8", 0.4), bevel=0.04)
    kit.box("reg.scr", (0.7, 0.05, 0.22), (2.2, G.COUNTER_Y - 0.3, 1.55), kit.emit("#bfe8d6", 0.8, "regscr"))
    for k in range(6):
        kit.box(f"reg.key{k}", (0.12, 0.05, 0.1), (2.0 + (k % 3) * 0.2, G.COUNTER_Y - 0.31, 1.28 - (k // 3) * 0.14), plastic("#e2463c" if k == 5 else "#8d939b", 0.5))
    # shop lamps
    W["lampmats"] = []
    for i, lx in enumerate((-4.0, 0.0, 4.0)):
        m = kit.emit("#fff0c8", 5.0, f"lampmat{i}")
        W["lampmats"].append(m)
        kit.cyl(f"lamp{i}.cord", 0.012, 1.1, (lx, 1.5, 3.85), plastic("#444444", 0.6), n=6)
        kit.sphere(f"lamp{i}.bulb", 0.2, (lx, 1.5, 3.2), m, seg=10)
        kit.light(f"pl{i}", "POINT", (lx, 1.5, 3.1), 240.0, "#ffe9c4", size=0.3, shadow=False)
    kit.light("ctr", "POINT", (-1.0, 2.2, 2.4), 110.0, "#fff0d8", size=0.4, shadow=False)
    kit.light("shopfill", "POINT", (0.0, 6.5, 3.4), 110.0, "#fff4e0", size=0.5, shadow=False)
    kit.light("shopfill2", "POINT", (0.0, -1.5, 2.8), 70.0, "#fff4e0", size=0.5, shadow=False)
    # shelf behind the counter with a few little boxes already on it
    wood = plastic("#b78456", 0.7, spec=0.1)
    for z in (1.3, 1.95):
        kit.box(f"bsh{z}", (6.8, 0.5, 0.08), (-3.2, 9.7, z), wood)
    boxes = []
    for k in range(18):
        boxes.append((-6.2 + k * 0.38, 9.65, 1.3 + 0.04 + 0.1, 0.3, 0.3, 0.2))
    for k in range(14):
        if 4 <= k <= 7:
            continue                                 # an empty stretch for the box that slides onto the shelf
        boxes.append((-5.9 + k * 0.4, 9.65, 1.95 + 0.04 + 0.1, 0.3, 0.3, 0.2))
    merged(kit, "bshboxes", boxes, P["gray"])
    # the returns shelf: a bookshelf of returned things (sweaters, a lamp, boxes)
    prop(kit, "bookshelf", (-6.4, 7.2, 0), rot=90, height=2.1)
    for k, c in enumerate(("#e8845a", "#5fb0d8", "#ffd23f", "#9a6bd0")):
        kit.box(f"ret{k}", (0.5, 0.4, 0.2), (-6.4, 6.4 + k * 0.5, 0.35 + (k % 2) * 0.55), plastic(c, 0.8), bevel=0.05)
    # a sweater display on the right wall
    # the stair up (x 5.2..6.8), bead curtain, trash bin
    for k in range(8):
        kit.box(f"stair{k}", (1.6, 0.5, 0.33 * (k + 1)), (6.0, 5.25 + 0.5 * k, 0.165 * (k + 1)), wood)
    bx(kit, "stairlanding", 5.2, 6.8, 8.7, 10.0, 0.0, 2.64, wood)
    prop(kit, "trashcan_cylindric", (-5.4, 1.6, 0), height=0.8, tint="#8fb8a8")
    W["trash"] = (-5.4, 1.6, 0.85)
    beads = [plastic(c, 0.4, spec=0.5) for c in ("#e2463c", "#ffd23f", "#4fb894", "#5fb0d8")]
    for i in range(14):
        for j in range(7):
            kit.sphere(f"bead{i}_{j}", 0.055, (-2.7 + i * 0.12, 8.1, 2.3 - j * 0.3), beads[(i + j) % 4], seg=6)
        kit.cyl(f"beadstr{i}", 0.006, 2.1, (-2.7 + i * 0.12, 8.1, 1.3), plastic("#dddddd", 0.6), n=4)
    bx(kit, "bhead", -2.9, -0.8, 8.0, 8.2, 2.35, 2.5, wood)
    # the street outside
    kit.plane("walk", (120, 4.2), (0, -6.0, 0.03), plastic("#efe6d4", 0.9, spec=0.05))
    kit.plane("road", (120, 10), (0, -13.0, 0.025), plastic("#5a606c", 0.9, spec=0.05))
    for k in range(10):
        kit.box(f"dash{k}", (1.6, 0.18, 0.02), (-24 + k * 5.4, -13.0, 0.04), plastic("#f6efdc", 0.8))
    kit.box("curb", (120, 0.3, 0.12), (0, -8.1, 0.06), plastic("#d8d4c8", 0.8))
    for i, (x, w, h, c) in enumerate([(-14.0, 14.0, 5.5, "#f2c9a8"), (14.0, 14.0, 5.0, "#e8a48c"), (-30, 16, 6.0, "#f6d8b8"), (30, 16, 5.5, "#ee9c86")]):
        bldg(kit, f"nb{i}", x, 3.0, w, 14.0, h, c, face=-1)
    for i, x in enumerate(range(-60, 61, 13)):
        bldg(kit, f"opp{i}", x, -34.0, 11.0, 9.0, 5.0 + (i % 3), ["#f2c9a8", "#e8b49c", "#f6d8b8", "#ee9c86", "#e8a48c"][i % 5], face=+1)
    for x in (-10, 9, 22, -22):
        tree(kit, f"st_tree{x}", x, -8.6, 4.2)
    # a street light across from the door (lit at night)
    kit.cyl("slamp.pole", 0.06, 4.2, (-3.0, -8.8, 2.1), plastic("#444a52", 0.5), n=8)
    kit.sphere("slamp.bulb", 0.2, (-3.0, -8.8, 4.3), kit.emit("#ffe2a0", 3.0, "slampmat"), seg=10)
    kit.light("street", "POINT", (-3.0, -8.2, 4.1), 900.0, "#ffe2b0", size=0.3, shadow=True)


# ---------------------------------------------------------------------------------------------- the back room
def backroom(kit, P):
    plastic = kit.plastic
    dark = plastic("#6a4a30", 0.8, spec=0.05)
    wall = plastic("#8a7a6a", 0.9, spec=0.05)
    kit.plane("bfloor", (12, 20), (0, 20.0, 0.02), kit.planks("#7a5a3a", "#6a4a30", 1.0))
    bx(kit, "bwl", -5.7, -5.5, 10.0, 30.2, 0, 7.0, wall)
    bx(kit, "bwr", 5.5, 5.7, 10.0, 30.2, 0, 7.0, wall)
    bx(kit, "bwb", -5.7, 5.7, 30.0, 30.2, 0, 7.0, wall)
    levels = 10
    pitch = 0.3
    ys = [G.ROW_Y0 + pitch * k for k in range(47)]
    zs = [0.14 + 0.55 * k for k in range(levels)]
    # shelf structure: back panels, boards, uprights
    for name, px in (("bkl", -5.0), ("bkr", 5.0)):
        bx(kit, f"{name}.panel", px - 0.1, px + 0.1, 12.0, 26.8, 0, 5.8, dark)
    bx(kit, "bkm.p0", -0.1, 0.1, 12.0, 25.5, 0, 5.8, dark)
    bx(kit, "bkm.p1", -0.1, 0.1, 26.1, 26.8, 0, 5.8, dark)
    bx(kit, "bkm.p2", -0.1, 0.1, 25.5, 26.1, 0, 1.55, dark)
    bx(kit, "bkm.p3", -0.1, 0.1, 25.5, 26.1, 2.05, 5.8, dark)
    for name, x0, x1 in (("bl", -5.0, -4.05), ("br", 4.05, 5.0), ("bml", -0.95, 0.0), ("bmr", 0.0, 0.95)):
        for k in range(levels + 1):
            bx(kit, f"{name}.bd{k}", x0, x1, 12.0, 26.8, 0.04 + 0.55 * k, 0.1 + 0.55 * k, dark)
        for yy in (12.0, 19.4, 26.8):
            bx(kit, f"{name}.up{int(yy)}", x0, x1, yy - 0.04, yy + 0.04, 0, 5.8, dark)
    gray1 = plastic("#8d939b", 0.65, spec=0.15)
    gray2 = plastic("#7b828c", 0.65, spec=0.15)
    stk = plastic("#f6efdc", 0.8)
    stk_mine = plastic("#bff0d8", 0.8)
    faces = [("bl", -4.3, +1, "L"), ("br", 4.3, -1, "R"), ("bml", -0.85, -1, "ML"), ("bmr", 0.85, +1, "MR")]
    # (face x, direction the label looks toward: +1 means the box front faces +x)
    gaps = {("ML", 25.6, 3), ("ML", 25.9, 3), ("MR", 25.6, 3), ("MR", 25.9, 3)}
    for nm, fx, d, tag in faces:
        a, b, s = [], [], []
        for lv, z in enumerate(zs):
            if tag == "R" and lv == 0:
                continue                                      # my row is built below
            for k, y in enumerate(ys):
                if any(abs(y - gy) < 0.16 and lv == gl and tag == gt for (gt, gy, gl) in gaps):
                    continue
                h = 0.22 + 0.04 * kit.hash01(k, lv, 3, 1)
                cx = fx - d * 0.25
                (a if (k + lv) % 3 else b).append((cx, y, z + h / 2, 0.5, 0.26, h))
                s.append((fx + d * 0.006, y, z + h / 2, 0.012, 0.12, 0.075))
        merged(kit, f"gb.{nm}.a", a, gray1)
        merged(kit, f"gb.{nm}.b", b, gray2)
        merged(kit, f"gb.{nm}.s", s, stk)
    # my bottom shelf: 46 empty spots (a dust-free square in the dust where each box stood); the 47th, the last box with
    # the hold slip, is the hand-held "gb2", standing in its slot until it is lifted (see animate)
    dust = plastic("#a89c8a", 0.95)
    clean = plastic("#5a3e28", 0.7)
    kit.box("dust", (0.5, ys[45] - ys[0] + 0.3, 0.01), (4.3 + 0.28, (ys[0] + ys[45]) / 2, 0.105), dust)
    tiles = [(4.3 + 0.26, y, 0.114, 0.44, 0.25, 0.008) for y in ys[:46]]
    merged(kit, "cleansq", tiles, clean)
    # the party box (light leaking from its lid) and the rain box (a damp spot under it), both on the left bank
    pz = zs[4] + 0.22
    kit.box("party.glow", (0.3, 0.2, 0.02), (-4.3 + 0.02, 17.6, pz + 0.01), kit.emit("#ffb0d8", 2.5, "partyglow"))
    kit.box("party.glow2", (0.3, 0.2, 0.02), (-4.3 + 0.02, 17.6, pz + 0.04), kit.emit("#9fd8ff", 1.6, "partyglow2"), rot=(0, 0.0, 0.5))
    kit.light("partyl", "POINT", (-3.9, 17.6, pz + 0.3), 18.0, "#ffb0d8", size=0.1, shadow=False)
    rz = zs[3]
    kit.box("rain.spot", (0.4, 0.3, 0.012), (-4.3 + 0.2, 19.4, rz - 0.004), plastic("#2a3550", 0.5, spec=0.4))
    for k in range(3):
        kit.sphere(f"rain.drop{k}", 0.025, (-4.0 + 0.1 * k, 19.3 + 0.1 * k, rz - 0.04 - 0.09 * k), plastic("#9fd0f0", 0.2, spec=0.8), seg=6)
    # the bulb on its cord, swinging from a pivot high up
    piv = kit.empty("bulbpiv", (G.BULB[0], G.BULB[1], 7.0))
    W["bulbpiv"] = piv
    kit.cyl("bulb.cord", 0.01, 3.4, (0, 0, -1.7), plastic("#222222", 0.6), piv, n=6)
    kit.sphere("bulb.glass", 0.13, (0, 0, -3.4), kit.emit("#ffe2a8", 9.0, "bulbmat"), piv, seg=10)
    kit.cyl("bulb.cap", 0.07, 0.1, (0, 0, -3.25), plastic("#555555", 0.5), piv, n=8)
    kit.light("bulb", "POINT", (0, 0, -3.4), 1500.0, "#ffd9a0", size=0.2, shadow=True, parent=piv)
    kit.light("bdoorglow", "POINT", (2.57, 11.0, 2.2), 260.0, "#e8f0ff", size=0.5, shadow=False)
    kit.light("bfill", "POINT", (0.0, 19.0, 5.0), 450.0, "#c8d6ff", size=0.6, shadow=False)
    kit.light("bfill2", "POINT", (0.0, 24.5, 3.0), 260.0, "#ffe0b8", size=0.6, shadow=False)
    # the four coins on the bottom shelf by the newest box
    W["coins"] = [kit.cyl(f"coin{k}", 0.05, 0.012, (4.3 + 0.3, 26.55 - 0.04, 0.15 + k * 0.0), P["brass"], n=10) for k in range(4)]
    for k, c in enumerate(W["coins"]):
        c.location = (4.3 + 0.12 + (k % 2) * 0.13, 26.46 - (k // 2) * 0.13, 0.108)
        c.hide_render = True
    # a floor lamp-free corner: scattered crates at the far end
    for k, x in enumerate((-3.0, 3.0)):
        kit.box(f"cr{k}", (0.9, 0.7, 0.6), (x, 28.8, 0.3), dark)


# ---------------------------------------------------------------------------------------------- other places
def kitchen(kit, P):
    plastic = kit.plastic
    kx = G.KX
    wall = plastic("#ffe89a", 0.85, spec=0.05)
    kit.plane("kfloor", (12, 9), (kx, 4.5, 0.02), kit.planks("#c9976a", "#b78456", 1.0))
    bx(kit, "kbk", kx - 6, kx + 6, 9.0, 9.2, 0, 3.6, wall)
    bx(kit, "kwl", kx - 6.2, kx - 6.0, 0, 9.2, 0, 3.6, wall)
    bx(kit, "kwr", kx + 6.0, kx + 6.2, 0, 9.2, 0, 3.6, wall)
    yel2 = plastic("#f2c14e", 0.6, spec=0.1)
    kit.box("kc.low", (6.0, 0.7, 0.9), (kx - 3.0, 8.62, 0.45), yel2, bevel=0.03)
    kit.box("kc.top", (6.1, 0.8, 0.06), (kx - 3.0, 8.6, 0.93), P["cream"])
    kit.box("kc.up", (5.0, 0.4, 0.8), (kx - 3.2, 8.78, 2.5), yel2, bevel=0.03)
    kit.box("stove", (1.0, 0.7, 0.9), (kx - 4.4, 8.55, 0.45), plastic("#d9d4c8", 0.4), bevel=0.04)
    kit.cyl("kettle.b", 0.2, 0.24, (kx - 4.4, 8.5, 1.05), plastic("#c9ced6", 0.3, spec=0.7), n=14, r2=0.16)
    kit.box("kettle.sp", (0.06, 0.2, 0.05), (kx - 4.4, 8.3, 1.08), plastic("#c9ced6", 0.3, spec=0.7))
    kit.box("kwin", (2.2, 0.06, 1.5), (kx - 6.0 + 0.0, 4.5, 1.9), kit.emit("#d4ecff", 0.9, "kwinglow"), rot=(0, 0, math.pi / 2))
    # table, chairs, mugs
    tab = plastic("#9a6b44", 0.6, spec=0.1)
    kit.box("ktab", (1.7, 1.0, 0.08), (kx - 1.0, 4.8, 0.78), tab, bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"ktl{sx}{sy}", (0.08, 0.08, 0.76), (kx - 1.0 + sx * 0.76, 4.8 + sy * 0.42, 0.38), tab)
    for sy in (-1, 1):
        kit.box(f"kch{sy}", (0.5, 0.5, 0.08), (kx - 1.0, 4.8 + sy * 1.0, 0.5), tab)
        kit.box(f"kchb{sy}", (0.5, 0.06, 0.5), (kx - 1.0, 4.8 + sy * 1.24, 0.8), tab)
        for lx in (-0.2, 0.2):
            kit.box(f"kchl{sy}{lx}", (0.06, 0.06, 0.48), (kx - 1.0 + lx, 4.8 + sy * 1.0, 0.24), tab)
    for sx, c in ((-0.35, "#e2463c"), (0.35, "#fffaf0")):
        kit.cyl(f"mug{sx}", 0.1, 0.13, (kx - 1.0 + sx, 4.8, 0.88), plastic(c, 0.4), n=12)
    # the clock at two: ticks, hour hand toward 2, minute hand toward 12
    cl = plastic("#fffaf0", 0.5)
    cxk, cyk, czk = kx + 0.9, 8.95, 2.35
    kit.cyl("clock", 0.32, 0.05, (cxk, cyk, czk), cl, rot=(math.pi / 2, 0, 0), n=24)
    for k in range(12):
        a = k * 30 * D2R
        kit.box(f"clk.t{k}", (0.025, 0.02, 0.07), (cxk + math.sin(a) * 0.26, cyk - 0.035, czk + math.cos(a) * 0.26), plastic("#2b2b33", 0.6), rot=(0, a, 0))
    a = 60 * D2R
    kit.box("clk.h", (0.035, 0.02, 0.17), (cxk + math.sin(a) * 0.085, cyk - 0.045, czk + math.cos(a) * 0.085), plastic("#2b2b33", 0.6), rot=(0, a, 0))
    kit.box("clk.m", (0.025, 0.02, 0.25), (cxk, cyk - 0.052, czk + 0.12), plastic("#2b2b33", 0.6))
    # the old wall phone: body, cradle with two stamp-red strokes scratched on it
    px, pz = kx + 2.4, 1.5
    kit.box("ph.body", (0.26, 0.1, 0.36), (px, 8.9, pz), plastic("#e8dcc0", 0.5, spec=0.3), bevel=0.02)
    kit.box("ph.dial", (0.14, 0.02, 0.14), (px, 8.84, pz - 0.04), plastic("#6a6a70", 0.5))
    kit.box("cradle", (0.12, 0.07, 0.14), (px, 8.86, pz + 0.26), plastic("#c9b898", 0.5), bevel=0.01)
    kit.box("cradle.s1", (0.012, 0.012, 0.09), (px - 0.02, 8.82, pz + 0.26), plastic("#e2463c", 0.6), rot=(0, 0.3, 0))
    kit.box("cradle.s2", (0.012, 0.012, 0.09), (px + 0.02, 8.82, pz + 0.26), plastic("#e2463c", 0.6), rot=(0, 0.3, 0))
    W["phone_base"] = Vector((px, 8.84, pz + 0.05))
    # a little mug rack beside the phone: two mugs, one turned upside down
    kit.box("krack", (0.9, 0.2, 0.04), (kx + 1.4, 8.85, 1.05), plastic("#b78456", 0.7, spec=0.1))
    kit.cyl("krack.m1", 0.1, 0.13, (kx + 1.15, 8.85, 1.075 + 0.065), plastic("#e2463c", 0.4), n=12)
    kit.cyl("krack.m2", 0.1, 0.13, (kx + 1.6, 8.85, 1.075 + 0.065), plastic("#fffaf0", 0.4), rot=(math.pi, 0, 0), n=12)
    # the shelf of Dad's 46 boxes beside the phone
    sh = plastic("#b78456", 0.7, spec=0.1)
    boxes = []
    for lv in range(4):
        z = 1.0 + 0.45 * lv
        kit.box(f"ksh{lv}", (2.6, 0.34, 0.05), (kx + 4.7, 8.82, z), sh)
        n = 11 if lv in (0, 3) else 12
        for k in range(n):
            boxes.append((kx + 3.6 + k * 0.2 + (0.1 if n == 11 else 0.0), 8.82, z + 0.025 + 0.11, 0.17, 0.28, 0.22))
    merged(kit, "kboxes", boxes, P["gray"])
    kit.light("kitl", "POINT", (kx, 3.5, 3.0), 190.0, "#ffe6c0", size=0.5, shadow=False)
    kit.light("kitl2", "POINT", (kx + 2.4, 5.0, 2.6), 120.0, "#fff0d8", size=0.5, shadow=False)


def house_out(kit, P):
    plastic = kit.plastic
    hx = G.HX
    kit.plane("hlawn", (60, 24), (hx, 8.0, 0.02), plastic("#9cc98a", 0.9, spec=0.05))
    kit.plane("hroad", (80, 8), (hx, -6.0, 0.025), plastic("#5a606c", 0.9, spec=0.05))
    kit.plane("hwalkway", (1.6, 8), (hx + 1.0, 2.0, 0.04), plastic("#efe6d4", 0.9))
    wall = kit.grime("#e8c9a0", 0.9, 2.0, "hhwall", 0.9)
    bx(kit, "hh.w", hx - 4, hx + 4, 6.0, 6.4, 0, 3.4, wall)
    kit.box("hh.roof", (8.8, 3.2, 0.5), (hx, 6.4, 3.6), plastic("#c4624a", 0.7), rot=(0.0, 0, 0))
    kit.box("hh.door", (1.1, 0.1, 2.3), (hx + 1.0, 5.94, 1.15), plastic("#5fb0d8", 0.5, spec=0.3))
    for sx in (-1, 1):
        kit.box(f"hh.win{sx}", (1.3, 0.06, 1.2), (hx + sx * 2.6 - (1.0 if sx > 0 else 0.0), 5.96, 1.6), kit.emit("#ffe3a0", 1.0, f"hhwin{sx}"))
    kit.box("hh.porch", (2.4, 1.2, 0.18), (hx + 1.0, 5.2, 0.09), plastic("#efe6d4", 0.8))
    kit.sphere("hh.lamp", 0.14, (hx + 2.0, 5.85, 2.7), kit.emit("#ffe2a0", 4.0, "hhlamp"), seg=10)
    kit.light("porch", "POINT", (hx + 2.0, 5.2, 2.7), 220.0, "#ffd9a0", size=0.3, shadow=False)
    kit.light("hhfill", "POINT", (hx, -1.5, 3.0), 130.0, "#fff0d8", size=0.6, shadow=False)
    for i, x in enumerate((-18, -9, 10, 19)):
        bldg(kit, f"hhn{i}", hx + x, 9.0, 7.0, 6.0, 4.2 + (i % 2), ["#f2c9a8", "#e8b49c", "#f6d8b8", "#ee9c86"][i], face=-1)
    tree(kit, "hhtree", hx - 5.5, 3.0, 4.8)
    car(kit, "car2", hx - 1.0, -3.0, 90, "#4a7fc8", lights=False)


def road(kit, P):
    plastic = kit.plastic
    cx = G.CX
    kit.plane("rgrass", (90, 40), (cx, 0, 0.0), plastic("#9cc98a", 0.9, spec=0.05))
    kit.plane("rroad", (90, 8), (cx, 0, 0.03), plastic("#5a606c", 0.9, spec=0.05))
    kit.box("rline", (90, 0.16, 0.02), (cx, -3.2, 0.05), plastic("#f6efdc", 0.8))
    for k in range(10):
        kit.box(f"rdash{k}", (2.0, 0.14, 0.02), (cx - 22 + k * 5.0, 0.4, 0.05), plastic("#ffd23f", 0.8))
    kit.plane("rshoulder", (90, 2.2), (cx, -4.4, 0.035), plastic("#8a8f98", 0.9))
    tree(kit, "rt1", cx - 9, 8, 6.0)
    tree(kit, "rt2", cx + 11, 9, 7.0)
    tree(kit, "rt3", cx + 3, 12, 6.0)
    kit.box("rhill", (60, 6, 3), (cx, 22, 1.5), plastic("#8ec47a", 0.9))
    W["car1"] = car(kit, "car1", cx + 0.5, -4.5, 90, "#e2463c", hood_up=True)
    W["steam"] = []
    wm = plastic("#fafafa", 0.9, spec=0.0)
    for k in range(6):
        W["steam"].append(kit.sphere(f"steam{k}", 0.2, (cx + 1.9, -4.5, 1.2), wm, seg=8))
    kit.light("rfill", "POINT", (cx, -8.0, 3.0), 100.0, "#fff0d8", size=0.6, shadow=False)


def hall(kit, P):
    plastic = kit.plastic
    hx = G.HALLX
    kit.plane("hlfloor", (9, 16), (hx, 5, 0.02), plastic("#8a94a8", 0.7, spec=0.2))
    wl = plastic("#efe9da", 0.85, spec=0.05)
    bx(kit, "hlb", hx - 4.5, hx + 4.5, 12.0, 12.2, 0, 3.6, wl)
    bx(kit, "hll", hx - 4.7, hx - 4.5, -4.0, 12.2, 0, 3.6, wl)
    bx(kit, "hlr", hx + 4.5, hx + 4.7, -4.0, 12.2, 0, 3.6, wl)
    for sx in (-1, 1):
        for k in range(3):
            y = 2.5 + k * 3.4
            kit.box(f"hld{sx}{k}", (0.08, 1.1, 2.3), (hx + sx * 4.44, y, 1.15), plastic("#b88a5a", 0.6))
    kit.box("hlwin", (3.0, 0.06, 2.2), (hx, 11.95, 1.9), kit.emit("#dff2ff", 1.4, "hlwinglow"))
    kit.box("hlwinfr", (3.3, 0.04, 2.5), (hx, 11.93, 1.9), plastic("#fffaf0", 0.7))
    kit.light("halll", "POINT", (hx, 5.0, 3.0), 220.0, "#fff4e0", size=0.6, shadow=False)
    kit.light("halll2", "POINT", (hx, -1.0, 2.6), 120.0, "#fff4e0", size=0.6, shadow=False)


def rainstep(kit, P):
    plastic = kit.plastic
    rx = G.RAINX
    kit.plane("rsgnd", (60, 30), (rx, 0, 0.0), plastic("#6d7580", 0.4, spec=0.5))
    wall = kit.grime("#c9a98a", 0.9, 2.0, "rswall", 0.9)
    bx(kit, "rsw", rx - 6, rx + 6, 6.0, 6.4, 0, 4.2, wall)
    kit.box("rs.door", (1.3, 0.1, 2.4), (rx, 5.94, 1.2), plastic("#c8553d", 0.5, spec=0.3))
    kit.box("rs.frame", (1.6, 0.06, 2.65), (rx, 5.97, 1.32), plastic("#fff4e0", 0.7))
    kit.box("rs.step", (2.4, 1.0, 0.2), (rx, 5.4, 0.1), plastic("#bfc4cc", 0.5))
    kit.box("rs.step2", (2.0, 0.7, 0.4), (rx, 5.7, 0.2), plastic("#c8ccd4", 0.5))
    kit.sphere("rs.lamp", 0.14, (rx + 1.4, 5.85, 2.8), kit.emit("#ffe2a0", 2.0, "rslamp"), seg=10)
    kit.light("rsl", "POINT", (rx + 1.4, 5.0, 2.8), 120.0, "#ffd9a0", size=0.3, shadow=False)
    kit.light("rsfill", "POINT", (rx, 0.5, 3.0), 140.0, "#e8f0ff", size=0.6, shadow=False)
    for i, x in enumerate((-9, 9)):
        bldg(kit, f"rsn{i}", rx + x, 8.0, 7.0, 6.0, 4.5, ["#e8b49c", "#f2c9a8"][i], face=-1)
    tree(kit, "rstree", rx - 4.5, 3.0, 5.0, tint="#a8c4a0")


def driveway(kit, P):
    plastic = kit.plastic
    ox = G.ODX
    kit.plane("odlawn", (70, 36), (ox, 8, 0.0), plastic("#9cc98a", 0.9, spec=0.05))
    kit.plane("odroad", (90, 8), (ox, -8.0, 0.025), plastic("#5a606c", 0.9, spec=0.05))
    kit.plane("odwalk", (90, 2.2), (ox, -3.6, 0.03), plastic("#efe6d4", 0.9))
    kit.plane("oddrive", (2.7, 14), (ox + 3.0, 3.0, 0.035), plastic("#b9b9b4", 0.9))
    bldg(kit, "odh", ox - 2.0, 13.0, 11.0, 6.0, 4.6, "#f2c9a8", face=-1)
    kit.box("odh.door", (1.2, 0.1, 2.3), (ox - 2.0, 9.94, 1.15), plastic("#4fb894", 0.5, spec=0.3))
    bldg(kit, "odh2", ox + 12.0, 13.0, 9.0, 6.0, 4.2, "#f6d8b8", face=-1)
    bldg(kit, "odh3", ox - 14.0, 13.0, 9.0, 6.0, 4.4, "#ee9c86", face=-1)
    tree(kit, "odt1", ox + 7.0, 6.0, 5.5)
    tree(kit, "odt2", ox - 8.0, 5.0, 5.0)
    # the mailbox: a post, a box and a flag, hinged at its foot so it can fold forward (toward -y)
    mb = kit.empty("mbx", (ox + 3.0, -4.9, 0))
    kit.box("mbx.post", (0.12, 0.12, 1.0), (0, 0, 0.5), plastic("#8a5a3a", 0.7), mb)
    kit.box("mbx.box", (0.36, 0.6, 0.3), (0, 0, 1.1), plastic("#4a7fc8", 0.45, spec=0.4), mb, bevel=0.04)
    kit.box("mbx.flag", (0.04, 0.04, 0.22), (0.2, 0.1, 1.28), plastic("#e2463c", 0.5), mb)
    W["mbx"] = mb
    # the minivan follows Mrs. Oduya (she sits in it): an open-topped body so she shows
    van = kit.empty("van", (ox + 3.0, 6.0, 0))
    body = plastic("#e8a63a", 0.35, spec=0.5)
    kit.box("van.low", (1.9, 4.6, 0.7), (0, 0, 0.55), body, van, bevel=0.07)
    kit.box("van.nose", (1.9, 1.2, 0.95), (0, 1.7, 0.7), body, van, bevel=0.07)
    kit.box("van.rear", (1.9, 0.1, 0.9), (0, -2.3, 0.9), body, van, bevel=0.03)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"van.wh{sx}{sy}", 0.36, 0.22, (sx * 0.98, sy * 1.5, 0.36), plastic("#2a2c33", 0.6), van, rot=(0, math.pi / 2, 0), n=14)
        kit.box(f"van.tl{sx}", (0.3, 0.06, 0.16), (sx * 0.65, -2.33, 0.75), kit.emit("#e2463c", 1.4), van)
    kit.box("van.seat", (0.7, 0.5, 0.3), (0, 0.15, 0.8), plastic("#444a52", 0.8), van)
    W["van"] = van
    kit.light("odfill", "POINT", (ox + 3.0, -2.0, 3.0), 100.0, "#fff0d8", size=0.6, shadow=False)


def lobby(kit, P):
    plastic = kit.plastic
    lx = G.LOBX
    kit.plane("lbfloor", (16, 14), (lx, 4, 0.02), plastic("#8aa0c0", 0.5, spec=0.3))
    wl = plastic("#f1ece0", 0.85, spec=0.05)
    bx(kit, "lbb0", lx - 8, lx + 3.7, 10.0, 10.2, 0, 4.0, wl)
    bx(kit, "lbb1", lx + 6.7, lx + 8, 10.0, 10.2, 0, 4.0, wl)
    bx(kit, "lbb2", lx + 3.7, lx + 6.7, 10.0, 10.2, 2.8, 4.0, wl)
    bx(kit, "lbl", lx - 8.2, lx - 8.0, -3.0, 10.2, 0, 4.0, wl)
    bx(kit, "lbr", lx + 8.0, lx + 8.2, -3.0, 10.2, 0, 4.0, wl)
    kit.box("lb.win", (4.2, 0.06, 2.4), (lx - 3.0, 9.94, 2.0), kit.emit("#dff2ff", 1.3, "lbwinglow"))
    kit.box("lb.desk", (2.8, 0.9, 1.0), (lx - 5.0, 7.6, 0.5), plastic("#c9a47a", 0.5, spec=0.2), bevel=0.04)
    kit.box("lb.desktop", (3.0, 1.1, 0.06), (lx - 5.0, 7.6, 1.03), plastic("#fffaf0", 0.6))
    prop(kit, "houseplant_1", (lx + 2.0, 8.8, 0), height=1.3)
    prop(kit, "houseplant_1", (lx - 7.0, 3.0, 0), height=1.2)
    # the elevator: an alcove in the back wall at x = lx + 5.2, doors slid aside
    ex = lx + 5.2
    bx(kit, "el.inL", ex - 1.1, ex - 1.0, 10.2, 12.4, 0, 2.7, plastic("#c9ced6", 0.4, spec=0.6))
    bx(kit, "el.inR", ex + 1.0, ex + 1.1, 10.2, 12.4, 0, 2.7, plastic("#c9ced6", 0.4, spec=0.6))
    bx(kit, "el.inB", ex - 1.1, ex + 1.1, 12.3, 12.4, 0, 2.7, plastic("#d8dce2", 0.4, spec=0.6))
    bx(kit, "el.top", ex - 1.1, ex + 1.1, 10.2, 12.4, 2.7, 2.78, plastic("#fffaf0", 0.6))
    bx(kit, "el.flr", ex - 1.1, ex + 1.1, 10.2, 12.4, 0.0, 0.04, plastic("#8d939b", 0.5))
    kit.box("el.lamp", (1.6, 1.4, 0.04), (ex, 11.3, 2.66), kit.emit("#fff4e0", 2.5, "ellamp"))
    bx(kit, "el.dL", ex - 1.5, ex - 1.1, 10.1, 10.25, 0, 2.7, plastic("#b4bac4", 0.4, spec=0.6))
    bx(kit, "el.dR", ex + 1.1, ex + 1.5, 10.1, 10.25, 0, 2.7, plastic("#b4bac4", 0.4, spec=0.6))
    kit.light("lobl", "POINT", (lx, 3.0, 3.2), 220.0, "#fff4e0", size=0.6, shadow=False)
    kit.light("lobl2", "POINT", (lx + 4.0, 5.0, 3.0), 120.0, "#fff4e0", size=0.6, shadow=False)


def apartment(kit, P):
    plastic = kit.plastic
    ax = G.APX
    z0 = APZ
    wl = plastic("#f2dcc4", 0.85, spec=0.05)
    kit.box("apslab", (12, 10, 0.4), (ax, 3.0, z0 - 0.2), plastic("#c9b49a", 0.8))
    kit.plane("apfloor", (12, 10), (ax, 3.0, z0 + 0.02), kit.planks("#c9976a", "#b78456", 1.0))
    # back wall with the window gap x -1.6..1.6, z 1.0..3.0 (above the floor)
    bx(kit, "apb0", ax - 6, ax - 1.6, 8.0, 8.2, z0, z0 + 3.6, wl)
    bx(kit, "apb1", ax + 1.6, ax + 6, 8.0, 8.2, z0, z0 + 3.6, wl)
    bx(kit, "apb2", ax - 1.6, ax + 1.6, 8.0, 8.2, z0, z0 + 1.0, wl)
    bx(kit, "apb3", ax - 1.6, ax + 1.6, 8.0, 8.2, z0 + 3.0, z0 + 3.6, wl)
    bx(kit, "apl", ax - 6.2, ax - 6.0, -3.0, 8.2, z0, z0 + 3.6, wl)
    bx(kit, "apr", ax + 6.0, ax + 6.2, -3.0, 8.2, z0, z0 + 3.6, wl)
    kit.box("apwf", (3.4, 0.1, 0.1), (ax, 8.0, z0 + 1.0), plastic("#fffaf0", 0.7))
    # the street below the window: sidewalk, road, houses across
    kit.plane("apgnd", (160, 80), (ax, 40, 0.0), plastic("#9cc98a", 0.9))
    kit.plane("apwalk", (120, 4), (ax, 12.0, 0.03), plastic("#efe6d4", 0.9))
    kit.plane("aproad", (120, 8), (ax, 18.0, 0.025), plastic("#5a606c", 0.9))
    for i, x in enumerate(range(-50, 51, 12)):
        bldg(kit, f"apo{i}", ax + x, 30.0, 10.0, 8.0, 5.0 + (i % 3), ["#f2c9a8", "#e8b49c", "#f6d8b8", "#ee9c86", "#e8a48c"][i % 5], face=-1)
    tree(kit, "aptree", ax - 5, 11.0, 5.0)
    # furniture: table, chair, dresser with an open drawer of receipts
    tab = plastic("#9a6b44", 0.6, spec=0.1)
    kit.box("aptab", (2.0, 1.2, 0.08), (ax - 2.2, 3.6, z0 + 0.78), tab, bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"aptl{sx}{sy}", (0.08, 0.08, 0.76), (ax - 2.2 + sx * 0.9, 3.6 + sy * 0.5, z0 + 0.38), tab)
    kit.box("apch", (0.5, 0.5, 0.08), (ax - 2.2, 2.4, z0 + 0.5), tab)
    kit.box("apchb", (0.5, 0.06, 0.5), (ax - 2.2, 2.15, z0 + 0.8), tab)
    for lx in (-0.2, 0.2):
        kit.box(f"apchl{lx}", (0.06, 0.06, 0.48), (ax - 2.2 + lx, 2.4, z0 + 0.24), tab)
    kit.box("drs", (1.8, 0.7, 1.0), (ax + 3.8, 7.5, z0 + 0.5), plastic("#a3b8d0", 0.6, spec=0.1), bevel=0.03)
    kit.box("drs.top", (1.9, 0.78, 0.05), (ax + 3.8, 7.5, z0 + 1.02), plastic("#fffaf0", 0.6))
    kit.box("drs.dr", (1.5, 0.7, 0.34), (ax + 3.8, 6.85, z0 + 0.55), plastic("#8aa0bc", 0.6, spec=0.1))
    kit.box("drs.dr.in", (1.3, 0.55, 0.08), (ax + 3.8, 6.9, z0 + 0.72), plastic("#5a6a80", 0.8))
    kit.box("stack", (0.24, 0.5, 0.2), (ax + 3.8, 6.9, z0 + 0.84), P["cream"], bevel=0.01)
    kit.box("stack.b1", (0.26, 0.04, 0.22), (ax + 3.8, 6.8, z0 + 0.84), plastic("#e2463c", 0.6))
    kit.box("stack.b2", (0.26, 0.04, 0.22), (ax + 3.8, 7.02, z0 + 0.84), plastic("#e2463c", 0.6))
    prop(kit, "houseplant_1", (ax + 5.2, 7.2, z0), height=1.2)
    kit.light("apl", "POINT", (ax, 3.0, z0 + 3.0), 200.0, "#fff4e0", size=0.6, shadow=False)
    kit.light("apl2", "POINT", (ax - 2.0, 6.0, z0 + 2.6), 110.0, "#fff4e0", size=0.6, shadow=False)
    kit.light("apst", "POINT", (ax, 13.0, 3.0), 150.0, "#fff4e0", size=0.8, shadow=False)
    # the fan of stamped receipts on the table (seven, each with a red ring)
    for k in range(7):
        a = (k - 3) * 17
        rc = kit.box(f"fanr{k}", (0.2, 0.42, 0.006), (ax - 2.2 + (k - 3) * 0.17, 3.45 + abs(k - 3) * 0.02, z0 + 0.832 + k * 0.007), P["cream"], rot=(0, 0, -a * D2R))
        kit.cyl(f"fanring{k}", 0.055, 0.004, (ax - 2.2 + (k - 3) * 0.17 + math.sin(a * D2R) * 0.12, 3.45 + abs(k - 3) * 0.02 + math.cos(a * D2R) * 0.12, z0 + 0.839 + k * 0.007), P["red"], n=14)
    # the flicking receipts: eight sheets hinged at one edge, over a stack, in the drawer
    W["sheets"] = []
    for k in range(8):
        hg = kit.empty(f"sheet{k}", (ax + 3.8 - 0.1, 6.9, z0 + 0.945 + 0.006 * k))
        kit.box(f"sheet{k}.p", (0.2, 0.5, 0.004), (0.1, 0, 0.0), P["cream"], hg)
        kit.cyl(f"sheet{k}.r", 0.04, 0.003, (0.1, 0.1, 0.004), P["red"], hg, n=10)
        W["sheets"].append(hg)
    W["thumb"] = kit.box("thumb", (0.07, 0.11, 0.05), (ax + 3.8, 6.4, z0 + 1.1), kit.plastic("#e8b88a", 0.5), bevel=0.02)


def macro(kit, P):
    """The receipt backs seen close: a big plate of glyph rows, a row of stamped backs, and a magnifier."""
    plastic = kit.plastic
    bx_ = G.BACKX
    ink = plastic("#2b2b33", 0.7)
    kit.plane("mfl", (40, 40), (bx_, 0, -0.5), plastic("#d9c8a8", 0.9))
    kit.box("mplate", (1.5, 0.02, 2.2), (bx_, 0, 1.2), P["cream"])
    rs = lambda a, b, c: kit.hash01(a, b, c, 7)
    for r in range(13):
        for c in range(5):
            k = int(rs(r, c, 1) * 4)
            x = bx_ - 0.55 + c * 0.27 + (rs(r, c, 2) - 0.5) * 0.04
            z = 1.2 + 0.95 - r * 0.15
            if k == 0:
                kit.box(f"g{r}_{c}", (0.09, 0.006, 0.09), (x, -0.012, z), ink)
            elif k == 1:
                kit.cyl(f"g{r}_{c}", 0.05, 0.006, (x, -0.012, z), ink, rot=(math.pi / 2, 0, 0), n=12)
            elif k == 2:
                kit.box(f"g{r}_{c}", (0.14, 0.006, 0.03), (x, -0.012, z), ink)
            else:
                kit.box(f"g{r}_{c}", (0.03, 0.006, 0.12), (x, -0.012, z), ink)
    # a row of stamped backs, for the camera to slide along
    for k in range(7):
        x = bx_ + 3.0 + k * 1.2
        kit.box(f"bk{k}", (0.9, 0.02, 1.4), (x, 0, 1.2), P["cream"])
        for r in range(6):
            kit.box(f"bk{k}.l{r}", (0.5 + 0.1 * ((r + k) % 3), 0.006, 0.04), (x - 0.05, -0.012, 1.7 - r * 0.1), ink)
        a = (k * 37 % 20 - 10) * D2R
        kit.cyl(f"bk{k}.ring", 0.3, 0.012, (x + 0.1, -0.02, 0.7), P["red"], rot=(math.pi / 2, 0, 0), n=24)
        kit.cyl(f"bk{k}.ringin", 0.2, 0.014, (x + 0.1, -0.025, 0.7), P["cream"], rot=(math.pi / 2, 0, 0), n=24)
        kit.box(f"bk{k}.bar", (0.55, 0.014, 0.07), (x + 0.1, -0.03, 0.7), P["red"], rot=(0, a, 0))
    # the big ring glyph
    kit.box("bigplate", (1.8, 0.02, 2.4), (bx_ + 14.0, 0, 1.2), P["cream"])
    kit.cyl("bigring", 0.62, 0.016, (bx_ + 14.0, -0.02, 1.2), P["red"], rot=(math.pi / 2, 0, 0), n=32)
    kit.cyl("bigringin", 0.44, 0.018, (bx_ + 14.0, -0.025, 1.2), P["cream"], rot=(math.pi / 2, 0, 0), n=32)
    kit.box("bigbar", (1.0, 0.02, 0.1), (bx_ + 14.0, -0.03, 1.2), P["red"], rot=(0, 0.35, 0))
    # the magnifier: a ring and a handle, a pale lens
    mg = kit.empty("mag", (bx_, -0.3, 1.2))
    kit.cyl("mag.rim", 0.4, 0.04, (0, 0, 0), plastic("#d9a441", 0.35, spec=0.6), mg, rot=(math.pi / 2, 0, 0), n=28)
    kit.cyl("mag.hole", 0.34, 0.06, (0, 0, 0), kit.plastic("#fffdf0", 0.2, spec=0.9), mg, rot=(math.pi / 2, 0, 0), n=28)
    kit.box("mag.handle", (0.08, 0.06, 0.6), (0.28, 0, -0.62), plastic("#8a5a3a", 0.6), mg, rot=(0, 0.45, 0))
    W["mag"] = mg
    kit.light("macl", "POINT", (bx_ + 3.0, -3.0, 3.0), 110.0, "#fff4e0", size=0.8, shadow=False)
    kit.light("macl2", "POINT", (bx_ + 14.0, -3.0, 3.0), 90.0, "#fff4e0", size=0.8, shadow=False)
    kit.light("macl3", "POINT", (bx_, -3.0, 3.0), 90.0, "#fff4e0", size=0.8, shadow=False)


# ---------------------------------------------------------------------------------------------- the tag
def build_tag(kit):
    """The rule meter: a cream receipt tag on a dark edge. A gray box glyph, 47 in big seven-segment digits and a lit
    red ring (sold). From L64 a second line grows below it: a brass key glyph and 1."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    paper = kit.emit("#fbf4e0", 1.0, "tagpaper")
    edge = kit.emit("#2a2a33", 0.5, "tagedge")
    ink = kit.emit("#1c1c24", 0.5, "tagink")
    redm = kit.emit("#e8281e", 1.0, "tagred")
    grayg = kit.emit("#8d939b", 0.9, "taggray")
    grayd = kit.emit("#4d535c", 0.6, "taggraydark")
    brassm = kit.emit("#f0b53c", 1.2, "tagbrass")

    def b(name, size, loc, mat, parent=root):
        ob = kit.box(name, size, loc, mat, parent)
        noshadow(ob)
        return ob

    def cyl(name, r, loc, mat, parent=root):
        ob = kit.cyl(name, r, 0.004, loc, mat, parent, n=24)
        noshadow(ob)
        return ob

    # row 1
    b("tag.edge", (1.56, 0.68, 0.004), (0, 0, 0.0), edge)
    b("tag.paper", (1.48, 0.6, 0.004), (0, 0, 0.004), paper)
    # the box glyph: a gray box with a lighter overhanging lid (a little tied-up shoebox)
    b("tag.bx", (0.36, 0.3, 0.004), (-0.54, -0.07, 0.008), grayd)
    b("tag.bxlid", (0.44, 0.12, 0.004), (-0.54, 0.12, 0.012), grayg)
    b("tag.bxstk", (0.14, 0.1, 0.004), (-0.54, -0.07, 0.016), paper)
    # the digits "47" in seven segments
    def seg7(prefix, x, segs, y=0.0, root_=root, mat=ink, hh=0.48, ww=0.27, t=0.075):
        pos = {"a": (0, hh / 2 - t / 2, ww - t, t), "g": (0, 0, ww - t, t), "d": (0, -hh / 2 + t / 2, ww - t, t),
               "f": (-ww / 2 + t / 2, hh / 4, t, hh / 2), "b": (ww / 2 - t / 2, hh / 4, t, hh / 2),
               "e": (-ww / 2 + t / 2, -hh / 4, t, hh / 2), "c": (ww / 2 - t / 2, -hh / 4, t, hh / 2)}
        for s in segs:
            dx, dy, sx, sy = pos[s]
            b(f"{prefix}.{s}", (sx, sy, 0.004), (x + dx, y + dy, 0.02), mat, root_)

    seg7("tag.d4", -0.14, "fgbc")
    seg7("tag.d7", 0.2, "abc")
    # the lit red ring
    ringg = kit.empty("tag.ringg", (0.56, 0.0, 0.0), root)
    W["ring"] = ringg
    cyl("tag.ring", 0.24, (0, 0, 0.008), redm, ringg)
    cyl("tag.ringin", 0.13, (0, 0, 0.012), paper, ringg)
    b("tag.ringbar", (0.4, 0.07, 0.004), (0, 0, 0.016), redm, ringg)
    # row 2 (grows in at L64): a key and 1
    r2 = kit.empty("tag.r2", (0, 0, 0), root)
    W["r2"] = r2
    b("tag.r2.edge", (1.56, 0.68, 0.004), (0, -0.72, 0.0), edge, r2)
    b("tag.r2.paper", (1.48, 0.6, 0.004), (0, -0.72, 0.004), paper, r2)
    cyl("tag.key.head", 0.19, (-0.6, -0.72, 0.008), brassm, r2)
    cyl("tag.key.hole", 0.08, (-0.6, -0.72, 0.012), paper, r2)
    b("tag.key.shaft", (0.5, 0.09, 0.004), (-0.3, -0.72, 0.008), brassm, r2)
    b("tag.key.t1", (0.08, 0.17, 0.004), (-0.12, -0.8, 0.008), brassm, r2)
    b("tag.key.t2", (0.08, 0.14, 0.004), (-0.26, -0.79, 0.008), brassm, r2)
    seg7("tag.d1", 0.2, "bc", y=-0.72, root_=r2)


# ---------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    W["lids"] = {}
    plastic = kit.plastic
    P = {
        "mint": plastic("#9fe3c7", 0.5, spec=0.15), "cream": plastic("#f6efdc", 0.7, spec=0.1),
        "brass": plastic("#d9a441", 0.35, spec=0.6), "red": plastic("#e2463c", 0.55, spec=0.1),
        "tan": plastic("#c09a6b", 0.6), "gray": plastic("#8d939b", 0.65, spec=0.15),
    }
    sun = kit.light("sun", "SUN", (0, -30, 40), 1.0, "#fff0d8", size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#cfe6ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    front = kit.light("front", "SUN", (-10, -30, 20), 1.0, "#ffd2ae", shadow=False)
    front.data.angle = 0.4
    kit.aim(front, (0, 0, 0))
    kit.plane("ground", (900, 900), (0, 0, -0.01), plastic("#a5d08f", 0.9, spec=0.05))
    kit.light("glow", "POINT", (0, 0, -50), 1.0, "#ffe0a0", size=0.3, shadow=False)
    shop(kit, P)
    backroom(kit, P)
    kitchen(kit, P)
    house_out(kit, P)
    road(kit, P)
    hall(kit, P)
    rainstep(kit, P)
    driveway(kit, P)
    lobby(kit, P)
    apartment(kit, P)
    macro(kit, P)
    # the portable things (placed by "obj" cues)
    gm, gl, gs = plastic("#8d939b", 0.65, spec=0.15), plastic("#7b828c", 0.65, spec=0.15), plastic("#f6efdc", 0.8)
    W["objs"] = {}
    for n in ("gb1", "gb2", "gb3", "gb4", "gb5"):
        W["objs"][n] = gray_box(kit, n, gm, gl, gs)
    # the hold slip hangs on the last box's string, with a glyph I can't read
    g2 = W["objs"]["gb2"]
    ink = plastic("#2b2b33", 0.8)
    kit.box("slip", (0.09, 0.012, 0.15), (0.11, -0.152, 0.1), gs, g2)
    kit.box("slip.g1", (0.05, 0.012, 0.02), (0.11, -0.16, 0.14), ink, g2)
    kit.box("slip.g2", (0.02, 0.012, 0.05), (0.11, -0.16, 0.08), ink, g2)
    kit.cyl("slip.ring", 0.025, 0.006, (0.14, -0.16, 0.06), plastic("#e2463c", 0.6), g2, rot=(math.pi / 2, 0, 0), n=12)
    rc = kit.empty("rcp", (0, 0, -50))
    kit.box("rcp.p", (0.2, 0.44, 0.008), (0, 0, 0.0), P["cream"], rc)
    for r in range(5):
        kit.box(f"rcp.l{r}", (0.12 + 0.03 * (r % 2), 0.012, 0.002), (0, -0.15 + r * 0.055, 0.0055), plastic("#2b2b33", 0.7), rc)
    W["rcp_ring"] = kit.cyl("rcp.ring", 0.05, 0.003, (0, 0.12, 0.0075), P["red"], rc, n=14)
    W["objs"]["rcp"] = rc
    st = kit.empty("stamp", (0, 0, -50))
    kit.cyl("stamp.h", 0.04, 0.16, (0, 0, 0.12), plastic("#a0674a", 0.6), st, n=10)
    kit.cyl("stamp.b", 0.07, 0.04, (0, 0, 0.02), P["red"], st, n=14)
    W["objs"]["stamp"] = st
    hs = kit.empty("handset", (0, 0, -50))
    kit.box("handset.b", (0.08, 0.08, 0.3), (0, 0, 0), plastic("#e8dcc0", 0.5, spec=0.3), hs, bevel=0.02)
    kit.box("handset.e1", (0.1, 0.1, 0.06), (0, 0, 0.14), plastic("#c9b898", 0.5), hs)
    kit.box("handset.e2", (0.1, 0.1, 0.06), (0, 0, -0.14), plastic("#c9b898", 0.5), hs)
    W["objs"]["handset"] = hs
    ph = kit.empty("phone", (0, 0, -50))
    kit.box("phone.b", (0.07, 0.02, 0.15), (0, 0, 0), plastic("#2a2c33", 0.4, spec=0.5), ph, bevel=0.006)
    kit.box("phone.s", (0.055, 0.004, 0.12), (0, -0.012, 0), kit.emit("#8fd3ff", 1.2, "phonescr"), ph)
    W["objs"]["phone"] = ph
    cb = kit.empty("cbox", (0, 0, -50))
    brn = plastic("#b98b5a", 0.8)
    kit.box("cbox.b", (0.5, 0.4, 0.28), (0, 0, 0), brn, cb, bevel=0.01)
    for k, (c, sx, sy, sz, px, py, pz) in enumerate([("#ffd23f", 0.14, 0.14, 0.18, -0.1, 0.0, 0.2), ("#e2463c", 0.1, 0.1, 0.12, 0.12, 0.05, 0.18)]):
        kit.box(f"cbox.i{k}", (sx, sy, sz), (px, py, pz), plastic(c, 0.6), cb)
    W["objs"]["cbox"] = cb
    cu = kit.empty("cup", (0, 0, -50))
    kit.cyl("cup.b", 0.05, 0.12, (0, 0, 0), plastic("#fffaf0", 0.6), cu, n=10, r2=0.04)
    W["objs"]["cup"] = cu
    sh = kit.empty("shim", (0, 0, -50))
    kit.box("shim.p", (1.0, 0.3, 0.7), (0, 0, 0), plastic("#b8bec8", 0.4, spec=0.5), sh, bevel=0.05)
    for k in range(5):
        kit.sphere(f"shim.s{k}", 0.04, (-0.4 + k * 0.2, -0.18, 0.3 - (k % 2) * 0.5), kit.emit("#fafcff", 3.0, "shimspark"), sh, seg=6)
    W["objs"]["shim"] = sh
    cn = kit.empty("coins2", (0, 0, -50))
    for k in range(4):
        kit.cyl(f"coins2.{k}", 0.05, 0.012, ((k % 2) * 0.11, (k // 2) * 0.11, 0.006 + (k > 1) * 0.0), P["brass"], cn, n=10)
    W["objs"]["coins2"] = cn
    cord = kit.cyl("cord", 0.012, 1.0, (0, 0, -50), plastic("#2b2b33", 0.6), n=6)
    W["cord"] = cord
    # the coffee stain on the man's shirt, a droplet on the other
    W["inited"] = False
    build_tag(kit)
    return {}


def _first_frame(kit, story):
    dh = bpy.data.objects.get("dad.headg")
    if dh is not None:
        m = kit.plastic("#b9b9bf", 0.8)
        kit.box("dad.stache", (0.6, 0.07, 0.13), (0, -0.62 - 0.02, -0.22), m, dh, bevel=0.03)
        kit.box("dad.brow", (0.82, 0.05, 0.05), (0, -0.62 - 0.02, 0.14), m, dh)
    th = bpy.data.objects.get("tulley.headg")
    if th is not None:
        kit.box("tulley.pencil", (0.05, 0.05, 0.42), (0.66, -0.05, 0.22), kit.plastic("#ffd23f", 0.5), th)
        kit.box("tulley.pencilt", (0.05, 0.05, 0.08), (0.66, -0.05, 0.47), kit.plastic("#e2463c", 0.5), th)
    mt = bpy.data.objects.get("man.torso")
    if mt is not None:
        W["stain"] = kit.box("man.stain", (0.9, 0.05, 0.8), (0.0, -0.54, 0.9), kit.plastic("#5a3a22", 0.6), mt)
    W["inited"] = True


def _hide(ob, hide):
    ob.hide_render = hide
    for c in ob.children_recursive:
        c.hide_render = hide


def _obj_state(c, t):
    if "who" in c:
        r = bpy.data.objects.get(c["who"])
        if r is None:
            return None
        yaw = r.rotation_euler.z
        ox, oy, oz = c["off"]
        cs, sn = math.cos(yaw), math.sin(yaw)
        p = Vector((r.location.x + ox * cs - oy * sn, r.location.y + ox * sn + oy * cs, r.location.z + oz))
        return p, yaw / D2R + c.get("rz", 0.0), c.get("s", 1.0), not r.hide_render
    return Vector(c["p"]), c.get("rz", 0.0), c.get("s", 1.0), True


def place_objects(tl, t):
    tracks = W.get("tracks")
    if tracks is None:
        tracks = {}
        for c in tl["cues"]:
            if c["name"] == "obj":
                tracks.setdefault(c["obj"], []).append(c)
        W["tracks"] = tracks
    for name, ob in W["objs"].items():
        cs = [c for c in tracks.get(name, []) if c["t"] <= t]
        if not cs:
            _hide(ob, True)
            continue
        c1 = cs[-1]
        if not c1.get("vis", True):
            _hide(ob, True)
            continue
        s1 = _obj_state(c1, t)
        if s1 is None:
            _hide(ob, True)
            continue
        pos, rz, sc, vis = s1
        dur = c1.get("dur", 0.0)
        if dur > 0 and len(cs) > 1 and t < c1["t"] + dur and cs[-2].get("vis", True):
            s0 = _obj_state(cs[-2], t)
            if s0 is not None:
                u = ss((t - c1["t"]) / dur)
                pos = s0[0].lerp(pos, u)
                rz = s0[1] + (rz - s0[1]) * u
                sc = s0[2] + (sc - s0[2]) * u
        if c1.get("swing"):
            pos = pos + Vector((c1["swing"] * math.sin(2 * math.pi * 0.55 * (t - c1["t"])), 0, 0))
        if c1.get("hop"):
            # a short arc: lift mid-way through the blend
            u = ss((t - c1["t"]) / max(dur, 1e-6)) if dur > 0 else 1.0
            pos = pos + Vector((0, 0, c1["hop"] * math.sin(math.pi * min(1.0, u))))
        ob.location = pos
        ob.rotation_euler = (c1.get("rx", 0.0) * D2R, 0, rz * D2R)
        ob.scale = sc if isinstance(sc, (tuple, list)) else (sc, sc, sc)
        _hide(ob, not vis)


def _seg(ob, a, b):
    d = b - a
    ln = max(0.01, d.length)
    ob.location = (a + b) / 2
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    ob.scale = (1, 1, ln)


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    look = look_at(tl, t)
    gains = {}
    az, el = look["az"] * math.pi / 180, look["el"] * math.pi / 180
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    so = kit.LIGHTS["sun"]["obj"]
    so.location = d * 60
    kit.aim(so, (0, 0, 0))
    kit.LIGHTS["sun"]["light"].color = look["sun_col"]
    kit.LIGHTS["fill"]["light"].color = look["fill_col"]
    gains["sun"], gains["fill"], gains["front"] = look["sun"], look["fill"], look["front"]
    gains["street"] = look["st"]
    gains["porch"] = 0.4 + 0.6 * look["st"]
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*look["sky"], 1.0)
    bg.inputs["Strength"].default_value = look["sky_str"]
    # the shop lamps (0..1 each), eased by their cue
    lm = sample("lamps", tl, t, {"a": 1.0, "b": 1.0, "c": 1.0})
    for i, k in enumerate("abc"):
        gains[f"pl{i}"] = lm[k]
        em = W["lampmats"][i].node_tree.nodes.get("Emission")
        if em is not None:
            em.inputs["Strength"].default_value = 0.2 + 5.0 * lm[k]
    gains["ctr"] = 0.3 + 0.7 * max(lm.values())
    gains["shopfill"] = 0.25 + 0.75 * max(lm.values())
    gains["shopfill2"] = 0.25 + 0.75 * max(lm.values())
    # doors
    fd = sample("fdoor", tl, t, {"a": 0.0})
    W["fdoor"].rotation_euler = (0, 0, -fd["a"] * D2R)
    bd = sample("bdoor", tl, t, {"a": 0.0})
    W["bdoor"].rotation_euler = (0, 0, bd["a"] * D2R)
    # the front bell: swings and rings down after its cue
    bc = [c for c in tl["cues"] if c["name"] == "bell" and c["t"] <= t]
    if bc:
        dt = t - bc[-1]["t"]
        W["fbell"].rotation_euler = (0.0, 0.55 * math.exp(-dt * 1.2) * math.sin(dt * 11.0), 0.0)
    else:
        W["fbell"].rotation_euler = (0, 0, 0)
    # the bulb sways, more when the cue says so
    bu = sample("bulb", tl, t, {"a": 0.06})
    W["bulbpiv"].rotation_euler = (bu["a"] * math.sin(2 * math.pi * t / 2.6), bu["a"] * 0.6 * math.sin(2 * math.pi * t / 3.1 + 1.0), 0.0)
    # the mailbox folds
    mb = sample("mbx", tl, t, {"f": 0.0})
    W["mbx"].rotation_euler = (mb["f"] * 85 * D2R, 0, 0)
    # the van follows Mrs. Oduya
    od = bpy.data.objects.get("oduya")
    if od is not None:
        W["van"].location = (od.location.x, od.location.y, 0.0)
        W["van"].hide_render = od.hide_render
        for c in W["van"].children_recursive:
            c.hide_render = od.hide_render
        W["van"].rotation_euler = (0, 0, od.rotation_euler.z + math.pi)
    # the coffee stain
    stc = sample("stain", tl, t, {"v": 1.0})
    if W.get("stain") is not None:
        W["stain"].scale = (max(0.001, stc["v"]), 1.0, max(0.001, stc["v"]))
        W["stain"].hide_render = stc["v"] < 0.02
    # the rubber stamp's ring on the receipt
    rg = sample("ring", tl, t, {"v": 0.0})
    W["rcp_ring"].hide_render = rg["v"] < 0.5
    # the coins by the newest box
    cv = sample("coins", tl, t, {"v": 0.0})
    for c in W["coins"]:
        c.hide_render = cv["v"] < 0.5
    # the tag: the ring pulses, the second line grows in
    pu = sample("pulse", tl, t, {"p": 0.0})
    W["ring"].scale = (1 + 0.4 * pu["p"], 1.0, 1 + 0.4 * pu["p"])
    kp = sample("kept", tl, t, {"k": 0.0})
    W["r2"].scale = (max(0.001, kp["k"]), max(0.001, kp["k"]), 1.0)
    W["r2"].hide_render = kp["k"] < 0.02
    # sitting (hips at z, legs forward)
    sits = {}
    for c in tl["cues"]:
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
    # carried and placed things
    place_objects(tl, t)
    lids = sample("lid", tl, t, {"a": 0.0, "b": 0.0, "c": 0.0})
    # lid angles per box: gb1 -> a, gb3 -> b, gb2 -> c
    for nm, k in (("gb1", "a"), ("gb3", "b"), ("gb2", "c")):
        W["lids"][nm].rotation_euler = (-lids[k] * D2R, 0, 0)
    # the glow of an opened box
    gl = sample("glow", tl, t, {"x": 0.0, "y": 0.0, "z": -50.0, "g": 0.0})
    kit.LIGHTS["glow"]["obj"].location = (gl["x"], gl["y"], gl["z"])
    gains["glow"] = gl["g"] * 40.0
    # the phone cord runs from the wall phone to the handset
    hs = W["objs"]["handset"]
    if not hs.hide_render:
        _seg(W["cord"], W["phone_base"], hs.location.copy())
        W["cord"].hide_render = False
    else:
        W["cord"].hide_render = True
    # steam rises off the roadside car
    for i, s in enumerate(W["steam"]):
        u = ((t * 0.45 + i / 6.0) % 1.0)
        s.location = (G.CX + 1.9 + 0.15 * math.sin(u * 6 + i), -4.5 + 0.2 * math.cos(u * 5 + i), 1.1 + u * 1.5)
        k = 0.5 + 1.1 * u
        s.scale = (k, k, k)
        s.hide_render = u > 0.92 or u < 0.04
    # the flicking receipts and my thumb
    fl = sample("flick", tl, t, {"u": 0.0})
    for i, sh in enumerate(W["sheets"]):
        v = ss(fl["u"] * 9.0 - i * 0.9) if fl["u"] > 0 else 0.0
        sh.rotation_euler = (0, -v * 170 * D2R, 0)
    th = W["thumb"]
    th.location = (G.APX + 3.8 - 0.1 + 0.2 * fl["u"], 6.55 - 0.0, APZ + 1.12 + 0.03 * math.sin(fl["u"] * 40))
    th.hide_render = fl["u"] <= 0.001
    # the magnifier slides over the plate
    mg = sample("mag", tl, t, {"u": 0.0})
    W["mag"].location = (G.BACKX - 0.35 + 0.7 * mg["u"], -0.3, 1.2 + 0.9 - 1.3 * mg["u"])
    # the plate sits in the top-left corner at a fixed angular size, whatever the lens
    lens = 40.0
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next((s for s in story["shots"] if s["id"] == shot["id"]), None)
    if spec:
        keys = spec["cam"]
        u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
        lens = keys[0][3]
        if len(keys) > 1:
            for a, b in zip(keys, keys[1:]):
                if u <= b[0]:
                    lens = a[3] + (b[3] - a[3]) * ss((u - a[0]) / max(1e-6, b[0] - a[0]))
                    break
            else:
                lens = keys[-1][3]
    dist = 1.0
    h2 = dist * 12.0 / lens
    w2 = h2 * 9.0 / 16.0
    tag = W["tag"]
    # inset so the polish pack's crop (up to 1.18x, plus a slide) never cuts it: its left edge sits at 0.76 of the half
    # width and its top at 0.78 of the half height
    s = 0.42 * w2
    tag.scale = (s, s, s)
    tag.location = (-0.432 * w2, 0.70 * h2, -dist)
    return gains
