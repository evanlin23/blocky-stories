"""ep108 "scarecrow swap": Grandpa's pumpkin patch (orange pumpkins, a gold cornfield, a red barn, two black-with-crows
neighbor fields), the white farmhouse (porch, back door with three straw-gold strokes, Rufus on the mat), a yellow
kitchen with a long table and a living room with a couch.

Everything the story moves is driven by cues in story.json (see animate): the look (sun, fill, sky, the dusk band),
the flashlight beam, the mail jeep and its waving driver, the crow that flaps away, the crossword on the crossbar,
who sits, the remote under Grandma's hand and the rule meter. The tag (crow count 0 and the wave glyph) is a child of
the camera.
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {}
PX, PY = G.POST
STEP = G.STEP
MASK_UP = 0.85
MASK_TILT = -0.4
BAR_Z = 1.40          # the crossbar's centre (the arms rest along it)


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def _L(**kw):
    base = dict(sun=3.6, sun_col="#fff0d8", el=46.0, az=205.0, fill=0.9, fill_col="#e8f0ff", sky="#8fd3ff",
                sky_str=1.0, band=0.0)
    base.update(kw)
    return base


LOOKS = {
    "day": _L(),
    # sunset brightness: warm gold, low sun in front of the camera, never dim
    "gold": _L(sun=3.0, sun_col="#ffb45a", el=14.0, az=205.0, fill=1.1, fill_col="#ffd8b0", sky="#ffc48c", sky_str=1.1),
    # the one dim scene: violet sky, orange band at the horizon behind the post, the flashlight is the key
    "dusk": _L(sun=2.0, sun_col="#ff9a50", el=4.0, az=8.0, fill=1.25, fill_col="#b4a4ff", sky="#6a58b8",
               sky_str=1.2, band=1.0),
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
        dur = 0.0 if dur <= 0 else max(0.4, dur)
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


def _hide(ob, hide):
    ob.hide_render = hide
    for c in ob.children_recursive:
        c.hide_render = hide


# ---------------------------------------------------------------------------------------------- parts
def pumpkin(kit, name, x, y, r, mats, rng):
    m = mats[rng.randrange(len(mats))]
    ob = kit.sphere(name, r, (x, y, r * 0.78), m, seg=10)
    ob.scale = (1.0, 1.0, 0.82)
    kit.box(f"{name}.stem", (0.07, 0.07, 0.12), (x, y, r * 1.52), kit.plastic("#4f8f3a", 0.8, spec=0.05))


def crow(kit, name, x, y, z, yaw=0.0, wings=False, sc=1.5):
    """A blocky crow facing +y (local), turned by yaw about z."""
    root = kit.empty(name, (x, y, z))
    root.rotation_euler = (0, 0, yaw * D2R)
    root.scale = (sc, sc, sc)
    m = kit.plastic("#262840", 0.55, spec=0.25)
    kit.box(f"{name}.body", (0.2, 0.4, 0.2), (0, 0, 0.12), m, root, bevel=0.03)
    kit.box(f"{name}.head", (0.14, 0.15, 0.14), (0, 0.24, 0.26), m, root, bevel=0.03)
    kit.box(f"{name}.beak", (0.05, 0.11, 0.05), (0, 0.36, 0.24), kit.plastic("#8d8aa8", 0.5), root)
    kit.box(f"{name}.tail", (0.12, 0.22, 0.04), (0, -0.28, 0.14), m, root, rot=(0.25, 0, 0))
    W.setdefault("crows", []).append(root)
    if wings:
        W["wings"] = []
        for sx in (-1, 1):
            piv = kit.empty(f"{name}.wing{sx}", (sx * 0.1, 0.0, 0.2), root)
            kit.box(f"{name}.wingb{sx}", (0.34, 0.26, 0.04), (sx * 0.17, 0, 0), m, piv, bevel=0.01)
            W["wings"].append((piv, sx))
    return root


def scarecrow_plain(kit, name, x, y, hatcrow=False):
    """An ordinary neighbor scarecrow facing -y."""
    wood = kit.plastic("#8a5a34", 0.8, spec=0.05)
    sack = kit.plastic("#d8b878", 0.9, spec=0.05)
    straw = kit.plastic("#e8c04a", 0.9, spec=0.05)
    kit.box(f"{name}.pole", (0.09, 0.09, 2.3), (x, y + 0.25, 1.15), wood)
    kit.box(f"{name}.bar", (2.0, 0.08, 0.09), (x, y + 0.25, 1.42), wood)
    kit.box(f"{name}.shirt", (0.62, 0.3, 0.8), (x, y, 1.1), kit.plastic("#4f8fd6", 0.8, spec=0.05), bevel=0.04)
    for sx in (-1, 1):
        kit.box(f"{name}.sleeve{sx}", (0.5, 0.22, 0.22), (x + sx * 0.52, y + 0.08, 1.42), kit.plastic("#4f8fd6", 0.8), bevel=0.04)
        kit.box(f"{name}.tuft{sx}", (0.16, 0.2, 0.2), (x + sx * 0.84, y + 0.08, 1.42), straw)
    kit.box(f"{name}.head", (0.42, 0.4, 0.42), (x, y, 1.78), sack, bevel=0.06)
    kit.box(f"{name}.eyeL", (0.07, 0.03, 0.07), (x - 0.1, y - 0.2, 1.82), kit.plastic("#2a2218", 0.8))
    kit.box(f"{name}.eyeR", (0.07, 0.03, 0.07), (x + 0.1, y - 0.2, 1.82), kit.plastic("#2a2218", 0.8))
    kit.box(f"{name}.brim", (0.7, 0.6, 0.05), (x, y, 2.0), kit.plastic("#7a4a2a", 0.8), bevel=0.02)
    kit.box(f"{name}.crown", (0.4, 0.4, 0.26), (x, y, 2.15), kit.plastic("#7a4a2a", 0.8), bevel=0.03)
    if hatcrow:
        W["hatcrow"] = crow(kit, f"{name}.crow", x + 0.03, y - 0.02, 2.22, yaw=180, sc=1.0)
    kit.box(f"{name}.legs", (0.4, 0.22, 0.7), (x, y, 0.4), kit.plastic("#5b7a9a", 0.8), bevel=0.04)


def corn(kit, rng, x0, x1, y0, y1, gap=None):
    gold = [kit.plastic(c, 0.85, spec=0.05) for c in ("#e8c04a", "#dcb23c", "#f0cd5c")]
    leaf = kit.plastic("#b8b43c", 0.85, spec=0.05)
    n = 0
    y = y0
    while y < y1:
        x = x0 + rng.random() * 0.2
        while x < x1:
            if not (gap and gap[0] < x < gap[1] and y < gap[2]):
                h = 2.3 + rng.random() * 0.6
                kit.box(f"corn{n}", (0.2, 0.2, h), (x, y, h / 2), gold[n % 3], bevel=0.02)
                kit.box(f"cornl{n}", (0.5, 0.05, 0.06), (x, y - 0.1, h * 0.55), leaf, rot=(0, (20 + n % 3 * 8) * D2R, 0))
                n += 1
            x += 0.5
        y += 0.5


def fence(kit, x0, x1, y, white, gap=None, crows=None, rng=None):
    n = 0
    x = x0
    while x <= x1 + 1e-6:
        if gap and gap[0] < x < gap[1]:
            x += 1.5
            continue
        kit.box(f"fp{x0}_{n}", (0.14, 0.14, 1.1), (x, y, 0.55), white, bevel=0.02)
        if crows is not None and rng and rng.random() < crows:
            crow(kit, f"fc{x0}_{n}", x, y, 1.1, yaw=rng.choice([0, 90, 180, 270]), sc=2.1)
        n += 1
        x += 1.5
    xa, xb = x0, x1
    if gap:
        segs = [(x0, gap[0]), (gap[1], x1)] if x0 < gap[0] < x1 else [(x0, x1)]
    else:
        segs = [(xa, xb)]
    for i, (a, b) in enumerate(segs):
        if b - a < 0.2:
            continue
        for z in (0.45, 0.85):
            kit.box(f"fr{x0}_{i}_{z}", (b - a, 0.06, 0.1), ((a + b) / 2, y, z), white)


def build_field(kit, name, cx, cy, w, d, rng, mats, crows=0, soil=None):
    kit.plane(f"{name}.soil", (w, d), (cx, cy, 0.02), soil)
    n = 0
    rows = int(d // 1.7)
    cols = int(w // 1.7)
    for r in range(rows):
        for c in range(cols):
            x = cx - w / 2 + 0.9 + c * 1.7 + rng.uniform(-0.25, 0.25)
            y = cy - d / 2 + 0.9 + r * 1.7 + rng.uniform(-0.25, 0.25)
            if abs(x - PX) < 0.5 and abs(y - PY) < 0.5:
                continue
            pumpkin(kit, f"{name}.pk{n}", x, y, rng.uniform(0.26, 0.4), mats, rng)
            if crows and rng.random() < crows:
                crow(kit, f"{name}.cr{n}", x + 0.05, y, rng.uniform(0.5, 0.7), yaw=rng.uniform(0, 360), sc=2.1)
            n += 1
    vine = kit.plastic("#3fae4a", 0.8, spec=0.05)
    for r in range(rows):
        y = cy - d / 2 + 0.9 + r * 1.7
        kit.box(f"{name}.vine{r}", (w - 0.6, 0.07, 0.04), (cx, y + 0.35, 0.06), vine)


def build_jeep(kit):
    """The mail truck: a closed white van with a blue and a red stripe, a cab with open side windows (its driver waves
    from one), a windscreen, no lettering. Faces +x."""
    root = kit.empty("jeep", (-100, -15.0, 0))
    W["jeep"] = root
    white = kit.plastic("#f4f4f0", 0.5, spec=0.3)
    blue = kit.plastic("#2f6fd6", 0.5, spec=0.3)
    red = kit.plastic("#d63a3a", 0.5, spec=0.3)
    dark = kit.plastic("#2a2a30", 0.7)
    glass = kit.plastic("#27324a", 0.2, spec=0.6)
    kit.box("jeep.chassis", (4.0, 1.6, 0.5), (0.1, 0, 0.62), white, root, bevel=0.05)
    kit.box("jeep.hood", (0.7, 1.55, 0.45), (2.05, 0, 0.95), white, root, bevel=0.06)
    kit.box("jeep.cargo", (2.3, 1.7, 1.5), (-0.7, 0, 1.6), white, root, bevel=0.06)
    kit.box("jeep.stripeB", (2.32, 1.72, 0.13), (-0.7, 0, 1.45), blue, root, bevel=0.02)
    kit.box("jeep.stripeR", (2.32, 1.72, 0.1), (-0.7, 0, 1.28), red, root, bevel=0.02)
    kit.box("jeep.slide", (0.04, 1.0, 0.9), (-0.7, 0.87, 1.7), kit.plastic("#e4e4de", 0.5), root)
    kit.box("jeep.stripeC", (1.3, 1.62, 0.12), (1.0, 0, 1.0), blue, root, bevel=0.02)
    kit.box("jeep.roof", (1.45, 1.74, 0.09), (1.0, 0, 2.08), white, root, bevel=0.03)
    for sy in (-1, 1):          # the cab's door panels and posts (the windows stay open)
        kit.box(f"jeep.door{sy}", (1.3, 0.06, 0.42), (1.0, sy * 0.8, 1.02), white, root)
        kit.box(f"jeep.cpostF{sy}", (0.1, 0.1, 0.9), (1.68, sy * 0.78, 1.6), white, root)
        kit.box(f"jeep.cpostB{sy}", (0.1, 0.1, 0.9), (0.38, sy * 0.78, 1.6), white, root)
    kit.box("jeep.wind", (0.05, 1.45, 0.7), (1.7, 0, 1.6), glass, root, rot=(0, -0.25, 0))
    kit.box("jeep.cabback", (0.05, 1.5, 0.9), (0.36, 0, 1.6), white, root)
    kit.box("jeep.seat", (0.4, 1.0, 0.2), (0.85, 0, 0.98), dark, root)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"jeep.wheel{sx}{sy}", 0.4, 0.22, (sx * 1.35 + 0.2, sy * 0.78, 0.4), dark, root, rot=(math.pi / 2, 0, 0), n=14)
    # the driver (blocks, not a cast member): torso, head, cap, a waving arm out of the window
    kit.box("jeep.dtorso", (0.38, 0.5, 0.6), (1.0, 0.0, 1.35), blue, root, bevel=0.04)
    kit.box("jeep.dhead", (0.3, 0.3, 0.3), (1.0, 0.0, 1.82), kit.plastic("#e8b88c", 0.5), root, bevel=0.05)
    kit.box("jeep.dcap", (0.34, 0.34, 0.1), (1.0, 0.0, 2.0), blue, root, bevel=0.03)
    kit.box("jeep.dcapb", (0.14, 0.24, 0.04), (1.15, 0.0, 1.96), blue, root)
    piv = kit.empty("jeep.darm", (1.0, 0.3, 1.55), root)
    kit.box("jeep.darmb", (0.14, 0.14, 0.55), (0, 0, 0.27), blue, piv, bevel=0.03)
    kit.box("jeep.dhand", (0.16, 0.16, 0.14), (0, 0, 0.6), kit.plastic("#e8b88c", 0.5), piv, bevel=0.03)
    W["darm"] = piv
    W["jeep_y"] = -15.0


def build_house(kit):
    hx, hy = G.HOUSE
    white = kit.plastic("#f7f3ea", 0.8, spec=0.05)
    red = kit.plastic("#b5472f", 0.7, spec=0.05)
    wood = kit.plastic("#b98550", 0.8, spec=0.05)
    glass = kit.plastic("#7fc4e8", 0.2, spec=0.8)
    kit.box("house.body", (11.0, 8.0, 5.0), (hx, hy, 2.5), white, bevel=0.03)
    for sgn, rx in ((1, -33), (-1, 33)):
        kit.box(f"house.roof{sgn}", (11.8, 5.5, 0.3), (hx, hy + sgn * 2.15, 6.35), red, rot=(rx * D2R, 0, 0), bevel=0.03)
    # porch on the south (front) wall
    kit.box("porch.floor", (8.0, 3.0, 0.3), (hx - 0.5, hy - 5.5, 0.15), wood)
    for i, px in enumerate((-4.3, -0.5, 3.3)):
        kit.box(f"porch.post{i}", (0.2, 0.2, 3.0), (hx + px, hy - 6.9, 1.8), white)
    kit.box("porch.roof", (8.6, 3.5, 0.2), (hx - 0.5, hy - 5.5, 3.4), red)
    for i, wx in enumerate((-3.5, 2.5)):
        kit.box(f"house.win{i}", (1.5, 0.1, 1.5), (hx + wx, hy - 4.02, 2.4), glass, bevel=0.02)
        kit.box(f"house.winf{i}", (1.8, 0.08, 1.8), (hx + wx, hy - 4.0, 2.4), white)
    kit.box("house.door", (1.1, 0.1, 2.2), (hx - 0.5, hy - 4.03, 1.4), kit.plastic("#3f8f6a", 0.6, spec=0.2))
    # the rocker
    rx, ry = G.ROCKER
    seat = kit.plastic("#d8704a", 0.7, spec=0.1)
    kit.box("rocker.seat", (0.7, 0.6, 0.08), (rx, ry, 0.5), seat, bevel=0.02)
    kit.box("rocker.back", (0.7, 0.08, 0.8), (rx, ry + 0.3, 0.9), seat, rot=(-0.15, 0, 0), bevel=0.02)
    for sx in (-1, 1):
        kit.box(f"rocker.arm{sx}", (0.07, 0.6, 0.08), (rx + sx * 0.36, ry, 0.72), seat)
        kit.box(f"rocker.run{sx}", (0.07, 0.9, 0.06), (rx + sx * 0.3, ry, 0.12), wood, rot=(0, 0, 0))
        kit.box(f"rocker.leg{sx}", (0.07, 0.07, 0.4), (rx + sx * 0.3, ry, 0.3), wood)
    # the back door on the west wall, three straw-gold strokes on its frame at knee height
    dx, dy = G.DOOR
    frame = kit.plastic("#fffaf0", 0.8, spec=0.05)
    kit.box("bdoor.leaf", (0.08, 1.0, 2.1), (dx - 0.04, dy, 1.05), kit.plastic("#3f8f6a", 0.6, spec=0.2))
    kit.box("bdoor.casL", (0.1, 0.26, 2.2), (dx - 0.05, dy - 0.64, 1.1), frame)
    kit.box("bdoor.casR", (0.1, 0.26, 2.2), (dx - 0.05, dy + 0.64, 1.1), frame)
    kit.box("bdoor.lintel", (0.1, 1.5, 0.2), (dx - 0.05, dy, 2.2), frame)
    gold = kit.emit("#f2b81c", 0.9, "stroke")
    for k in range(3):
        b = kit.box(f"bdoor.stroke{k}", (0.03, 0.03, 0.26), (dx - 0.115, dy - 0.64 - 0.07 + k * 0.07, 0.5), gold)
        noshadow(b)
    kit.box("bdoor.mat", (1.1, 1.3, 0.05), (dx - 0.8, dy, 0.03), kit.plastic("#c8372d", 0.9))
    kit.box("bdoor.step", (0.7, 1.4, 0.18), (dx - 0.35, dy, 0.09), kit.plastic("#b0aca4", 0.9))
    # Rufus asleep on the mat: a brown hound, long ears
    fur = kit.plastic("#9a5a2a", 0.85, spec=0.05)
    ear = kit.plastic("#6a3a18", 0.85, spec=0.05)
    kit.box("rufus.body", (0.9, 0.34, 0.3), (dx - 0.8, dy + 0.05, 0.25), fur, bevel=0.05)
    kit.box("rufus.head", (0.3, 0.3, 0.26), (dx - 1.3, dy - 0.05, 0.25), fur, bevel=0.05)
    kit.box("rufus.muzzle", (0.18, 0.2, 0.16), (dx - 1.5, dy - 0.05, 0.2), fur, bevel=0.04)
    kit.box("rufus.nose", (0.06, 0.08, 0.06), (dx - 1.6, dy - 0.05, 0.24), kit.plastic("#1c1c20", 0.6))
    for sy in (-1, 1):
        kit.box(f"rufus.ear{sy}", (0.1, 0.1, 0.3), (dx - 1.28, dy - 0.05 + sy * 0.17, 0.2), ear, bevel=0.03)
        kit.box(f"rufus.leg{sy}", (0.3, 0.1, 0.1), (dx - 1.05, dy - 0.05 + sy * 0.12, 0.1), fur)
    kit.box("rufus.tail", (0.4, 0.08, 0.08), (dx - 0.25, dy + 0.35, 0.12), fur, rot=(0, 0, 0.5))


def build_barn(kit):
    bx, by = -17.0, 18.0
    red = kit.plastic("#c8372d", 0.7, spec=0.05)
    white = kit.plastic("#fffaf0", 0.7)
    kit.box("barn.body", (9.0, 11.0, 5.5), (bx, by, 2.75), red, bevel=0.03)
    for sgn, ry in ((1, 28), (-1, -28)):
        kit.box(f"barn.roof{sgn}", (5.4, 12.0, 0.3), (bx + sgn * 2.4, by, 6.7), kit.plastic("#7a3a2a", 0.8), rot=(0, ry * D2R, 0), bevel=0.03)
    kit.box("barn.door", (3.0, 0.1, 3.6), (bx, by - 5.55, 1.8), white)
    for sgn in (-1, 1):
        kit.box(f"barn.x{sgn}", (0.15, 0.08, 4.2), (bx, by - 5.62, 1.8), red, rot=(0, sgn * 40 * D2R, 0))
    kit.cyl("silo", 1.8, 9.0, (bx + 8.0, by + 2, 4.5), kit.plastic("#d8d4cc", 0.6), n=16)
    kit.sphere("silo.top", 1.8, (bx + 8.0, by + 2, 9.0), kit.plastic("#8a8a92", 0.5), seg=12)


def build_kitchen(kit):
    kx, ky = G.KIT
    wall = kit.plastic("#ffd96a", 0.85, spec=0.05)
    trim = kit.plastic("#fffaf0", 0.8)
    kit.plane("k.floor", (14, 13), (kx, ky, 0.02), kit.planks("#d9a468", "#c48a50", 1.0))
    kit.box("k.back", (14, 0.3, 3.2), (kx, ky + 6.2, 1.6), wall)
    kit.box("k.front", (14, 0.3, 3.2), (kx, ky - 6.4, 1.6), wall)
    for sx in (-1, 1):
        kit.box(f"k.side{sx}", (0.3, 13, 3.2), (kx + sx * 7.0, ky, 1.6), wall)
    kit.box("k.ceil", (14.4, 13.4, 0.2), (kx, ky, 3.3), trim)
    # window on the back wall, bright
    kit.box("k.win", (2.2, 0.06, 1.5), (kx - 2.5, ky + 6.0, 1.9), kit.emit("#e8f6ff", 2.2, "kwin"))
    kit.box("k.winf", (2.5, 0.05, 1.8), (kx - 2.5, ky + 6.03, 1.9), trim)
    # counter run along the east wall
    cab = kit.plastic("#4fb3a8", 0.6, spec=0.1)
    kit.box("k.counter", (0.7, 5.0, 0.9), (kx + 6.5, ky + 3.2, 0.45), cab, bevel=0.02)
    kit.box("k.ctop", (0.8, 5.1, 0.06), (kx + 6.5, ky + 3.2, 0.93), trim)
    for nm, (px, py, hh) in {"kitchen_fridge": (6.5, 0.2, 1.9), "kitchen_sink": (6.5, 3.2, 0.96)}.items():
        try:
            kit.prop(nm, (kx + px, ky + py, 0.0 if nm == "kitchen_fridge" else 0.93), rot=90, height=hh)
        except Exception:
            pass
    try:
        kit.prop("houseplant_1", (kx - 6.2, ky + 5.2, 0.0), height=0.8)
        kit.prop("light_floor1", (kx - 6.3, ky - 1.5, 0.0), height=1.7)
    except Exception:
        pass
    # the long table runs north-south at x = kx
    wood = kit.plastic("#b98550", 0.7, spec=0.1)
    kit.box("k.table", (1.5, 5.2, 0.1), (kx, ky + 1.6, 0.8), wood, bevel=0.02)
    cloth = kit.plastic("#d6453a", 0.8)
    kit.box("k.cloth", (1.1, 4.6, 0.02), (kx, ky + 1.6, 0.86), cloth)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"k.tleg{sx}{sy}", (0.1, 0.1, 0.75), (kx + sx * 0.65, ky + 1.6 + sy * 2.4, 0.4), wood)
    # two chairs at the heads of the table
    cwood = kit.plastic("#8a5a34", 0.8, spec=0.05)
    for nm, cy, face in (("grandpa", ky - 1.5, +1), ("grandma", ky + 4.9, -1)):
        kit.box(f"k.{nm}.seat", (0.5, 0.5, 0.06), (kx, cy, 0.46), cwood, bevel=0.02)
        kit.box(f"k.{nm}.back", (0.5, 0.06, 0.6), (kx, cy - face * 0.26, 0.8), cwood, bevel=0.02)
        for sx in (-1, 1):
            for sy in (-1, 1):
                kit.box(f"k.{nm}.leg{sx}{sy}", (0.05, 0.05, 0.44), (kx + sx * 0.22, cy + sy * 0.22, 0.22), cwood)
    # dinner: plates, a pie, forks, glasses
    plate = kit.plastic("#fffaf0", 0.4, spec=0.3)
    kit.cyl("k.plateA", 0.2, 0.025, (kx, ky - 0.55, 0.89), plate, n=16)
    kit.cyl("k.plateB", 0.2, 0.025, (kx, ky + 3.75, 0.89), plate, n=16)
    kit.cyl("k.pie", 0.22, 0.09, (kx, ky + 1.6, 0.92), kit.plastic("#ff8c1a", 0.7), n=16)
    kit.cyl("k.piecrust", 0.25, 0.04, (kx, ky + 1.6, 0.89), kit.plastic("#e8b060", 0.7), n=16)
    metal = kit.metal("#c8ccd0", 0.3)
    kit.box("k.forkA", (0.03, 0.2, 0.01), (kx - 0.3, ky - 0.7, 0.875), metal)
    kit.box("k.forkAt", (0.07, 0.07, 0.01), (kx - 0.3, ky - 0.57, 0.875), metal)
    kit.box("k.forkB", (0.03, 0.2, 0.01), (kx + 0.34, ky + 3.75, 0.875), metal)
    kit.box("k.glassA", (0.07, 0.07, 0.12), (kx + 0.4, ky - 0.2, 0.93), kit.glass("#cfe6f0"))
    # the living room: couch against the south wall, the TV to the north
    lx, ly = G.LIV
    lwall = kit.plastic("#ffb98a", 0.85, spec=0.05)
    kit.plane("l.floor", (14, 12), (lx, ly, 0.02), kit.planks("#d9a468", "#c48a50", 1.0))
    kit.plane("l.rug", (4.4, 3.2), (lx, ly + 2.0, 0.035), kit.plastic("#4f9fd6", 0.9))
    kit.box("l.back", (14, 0.3, 3.2), (lx, ly + 5.8, 1.6), lwall)
    kit.box("l.front", (14, 0.3, 3.2), (lx, ly - 6.0, 1.6), lwall)
    for sx in (-1, 1):
        kit.box(f"l.side{sx}", (0.3, 12, 3.2), (lx + sx * 7.0, ly, 1.6), lwall)
    kit.box("l.ceil", (14.4, 12.4, 0.2), (lx, ly, 3.3), trim)
    sofa = kit.plastic("#d8704a", 0.85, spec=0.05)
    sofa2 = kit.plastic("#e88a60", 0.85, spec=0.05)
    kit.box("l.couch.base", (2.8, 1.0, 0.4), (lx, ly - 0.1, 0.22), sofa, bevel=0.06)
    kit.box("l.couch.back", (2.8, 0.3, 0.8), (lx, ly - 0.65, 0.78), sofa, bevel=0.06)
    for sx in (-1, 1):
        kit.box(f"l.couch.arm{sx}", (0.3, 1.0, 0.65), (lx + sx * 1.4, ly - 0.1, 0.5), sofa, bevel=0.06)
    for sx in (-1, 1):
        kit.box(f"l.couch.cush{sx}", (1.2, 0.8, 0.12), (lx + sx * 0.64, ly + 0.02, 0.48), sofa2, bevel=0.04)
    kit.box("l.tv", (1.8, 0.12, 1.0), (lx, ly + 5.5, 1.1), kit.plastic("#1c1c24", 0.3, spec=0.5), bevel=0.02)
    kit.box("l.tvscreen", (1.6, 0.04, 0.84), (lx, ly + 5.43, 1.1), kit.emit("#6a8aa8", 0.5, "tvscr"))
    kit.box("l.tvstand", (2.4, 0.5, 0.5), (lx, ly + 5.4, 0.25), wood)
    try:
        kit.prop("light_floor1", (lx + 3.0, ly - 0.2, 0.0), height=1.7)
        kit.prop("houseplant_1", (lx - 3.2, ly + 4.6, 0.0), height=0.8)
    except Exception:
        pass
    kit.box("l.win", (1.8, 0.06, 1.3), (lx - 3.5, ly + 5.6, 1.9), kit.emit("#e8f6ff", 2.0, "lwin"))
    # the remote (placed under Grandma's hand in animate)
    W["remote"] = kit.box("remote", (0.07, 0.2, 0.025), (lx, ly, 0.5), kit.plastic("#2a2a30", 0.5), bevel=0.01)
    for k in range(3):
        kit.box(f"remote.b{k}", (0.025, 0.025, 0.012), (0, 0, 0), kit.plastic("#ff8c1a", 0.5), W["remote"])
        W["remote"].children[-1].location = (0, -0.05 + 0.05 * k, 0.016)


def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    rng = random.Random(108)
    plastic = kit.plastic
    grass = kit.grime("#79c850", 0.86, 1.4, "grass", 0.95)
    soil = kit.grime("#a6793f", 0.8, 2.0, "soil", 0.95)
    soil2 = kit.grime("#6e5a3a", 0.8, 2.0, "soil2", 0.95)
    road = kit.grime("#8a8a92", 0.85, 1.5, "road", 0.9)
    orange = [plastic(c, 0.55, spec=0.15) for c in ("#ff8c1a", "#ff9a2a", "#f27a10")]
    white = plastic("#fffaf0", 0.75, spec=0.05)

    # ---------------------------------------------------------------- lights (gains set in animate)
    sun = kit.light("sun", "SUN", (0, -30, 40), 1.0, "#fff0d8", size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#e8f0ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    kx, ky = G.KIT
    lx, ly = G.LIV
    kit.light("kl1", "POINT", (kx, ky + 0.8, 2.9), 420.0, "#fff0d0", size=0.6, shadow=False)
    kit.light("kl2", "POINT", (kx, ky + 4.6, 2.7), 300.0, "#fff0d0", size=0.5, shadow=False)
    kit.light("kl3", "POINT", (kx + 0.6, ky - 3.6, 2.4), 260.0, "#fff4dc", size=0.5, shadow=False)
    kit.light("ll1", "POINT", (lx, ly - 0.2, 2.8), 400.0, "#ffe8c4", size=0.6, shadow=False)
    kit.light("ll3", "POINT", (lx - 1.0, ly + 1.8, 1.5), 170.0, "#fff0d8", size=0.5, shadow=False)
    kit.light("ll2", "POINT", (lx, ly - 3.6, 2.4), 320.0, "#ffe8c4", size=0.5, shadow=False)
    fl = kit.light("flash", "SPOT", (1.0, -1.6, 1.2), 900.0, "#fff4d8", spot=26, blend=0.5, size=0.05)
    kit.aim(fl, (PX, PY, 1.5))

    # ---------------------------------------------------------------- the ground, the road, the sky band
    kit.plane("ground", (500, 500), (0, 0, 0), grass)
    kit.plane("roadbed", (320, 7.0), (20, G.ROAD_Y, 0.03), road)
    kit.plane("roadline", (320, 0.15), (20, G.ROAD_Y, 0.04), plastic("#ffd23f", 0.7))
    bandm = kit.emit("#ff6a1a", 1.3, "bandm")
    W["band"] = kit.box("band", (240, 0.5, 10.0), (0, 32, 7.5), bandm)
    W["band2"] = [kit.box("bandE", (0.5, 160, 10.0), (62, 0, 7.5), bandm), kit.box("bandW", (0.5, 160, 10.0), (-62, 0, 7.5), bandm)]
    for ob in [W["band"]] + W["band2"]:
        noshadow(ob)
    # ---------------------------------------------------------------- Grandpa's patch
    build_field(kit, "ours", 0, 1.5, 13.0, 13.0, rng, orange, crows=0.0, soil=soil)
    # the scarecrow's post, crossbar and step (Grandpa stands on it: set in the cast)
    wood = plastic("#8a5a34", 0.8, spec=0.05)
    kit.box("post.pole", (0.12, 0.12, 2.5), (PX, PY + 0.55, 1.25), wood)
    kit.box("post.bar", (2.9, 0.08, 0.1), (PX, PY + 0.5, BAR_Z), wood)
    kit.box("post.step", (0.9, 0.55, STEP), (PX, PY, STEP / 2), plastic("#b98550", 0.8))
    # the crossword resting on the crossbar by his glove, a pencil tucked in the fold
    paper = plastic("#fffdf4", 0.8)
    inkm = plastic("#26262e", 0.7)
    cw = kit.empty("crossword", (PX + 1.0, PY + 0.36, BAR_Z + 0.05), rot=(-0.28, 0, 0))
    W["crossword"] = cw
    kit.box("cw.paper", (0.56, 0.025, 0.66), (0, 0, 0.33), paper, cw)
    kit.box("cw.fold", (0.012, 0.03, 0.66), (0, 0, 0.33), plastic("#d8d4c4", 0.8), cw)
    for r in range(5):
        for c in range(5):
            if (r * 2 + c) % 3 == 0:
                kit.box(f"cw.cell{r}{c}", (0.075, 0.004, 0.075), (-0.2 + c * 0.1, -0.015, 0.1 + r * 0.1), inkm, cw)
    for r in range(6):
        kit.box(f"cw.hl{r}", (0.5, 0.003, 0.008), (0, -0.0135, 0.06 + r * 0.1), plastic("#6a6a74", 0.8), cw)
        kit.box(f"cw.vl{r}", (0.008, 0.003, 0.5), (-0.25 + r * 0.1, -0.0135, 0.31), plastic("#6a6a74", 0.8), cw)
    kit.box("cw.pencil", (0.4, 0.03, 0.035), (0.0, -0.03, 0.04), plastic("#ffd23f", 0.6), cw, rot=(0, 0.12, 0))
    kit.box("cw.tip", (0.06, 0.03, 0.03), (0.22, -0.03, 0.045), plastic("#26262e", 0.6), cw, rot=(0, 0.12, 0))
    # the lawn chair and thermos in the corn clearing
    cx, cy = G.CHAIR
    frame = kit.metal("#9aa0a8", 0.4)
    canv = plastic("#e8453c", 0.8)
    canv2 = plastic("#fffaf0", 0.8)
    kit.box("chair.seat", (0.55, 0.5, 0.05), (cx, cy, 0.4), canv, bevel=0.01)
    kit.box("chair.back", (0.55, 0.05, 0.6), (cx, cy + 0.27, 0.72), canv2, rot=(-0.2, 0, 0), bevel=0.01)
    for sx in (-1, 1):
        kit.box(f"chair.leg{sx}", (0.04, 0.5, 0.04), (cx + sx * 0.27, cy, 0.2), frame, rot=(0.0, 0, 0))
        kit.box(f"chair.legf{sx}", (0.04, 0.04, 0.42), (cx + sx * 0.27, cy - 0.22, 0.2), frame)
        kit.box(f"chair.legb{sx}", (0.04, 0.04, 0.42), (cx + sx * 0.27, cy + 0.22, 0.2), frame)
    kit.cyl("thermos", 0.09, 0.34, (cx + 0.7, cy - 0.1, 0.17), plastic("#3fae4a", 0.4, spec=0.4), n=12)
    kit.cyl("thermos.cap", 0.08, 0.07, (cx + 0.7, cy - 0.1, 0.37), plastic("#fffaf0", 0.5), n=12)
    # the white fence in front of the three patches (a gap at the gate)
    fence(kit, -26, -9, G.FENCE_Y, white, crows=0.8, rng=rng)
    fence(kit, 9, 26, G.FENCE_Y, white, crows=0.8, rng=rng)
    fence(kit, -9, 9, G.FENCE_Y, white, gap=(-1.6, 1.6))
    # ---------------------------------------------------------------- the neighbors' fields: black with crows
    build_field(kit, "lneigh", -15.0, 1.5, 15.0, 13.0, rng, orange, crows=0.7, soil=soil2)
    build_field(kit, "rneigh", 15.0, 1.5, 15.0, 13.0, rng, orange, crows=0.7, soil=soil2)
    lx_, ly_ = G.LNEIGH
    scarecrow_plain(kit, "lsc", lx_, ly_, hatcrow=True)
    scarecrow_plain(kit, "rsc", 15.0, 2.0)
    # crows on the road side too (the fence posts) and in the air-free sky
    for i in range(14):
        crow(kit, f"road.cr{i}", rng.choice([-1, 1]) * rng.uniform(10, 24), rng.uniform(-6, -4), 0.1, yaw=rng.uniform(0, 360))
    # the flapping crow of S15 on the left neighbor's fence post
    W["flyer"] = crow(kit, "flyer", -8.6, G.FENCE_Y + 0.2, 1.1, yaw=-45, wings=True)
    # ---------------------------------------------------------------- corn, barn, house, trees
    corn(kit, rng, -9.5, 9.5, 10.0, 13.5)
    corn(kit, rng, -9.5, -2.0, 8.0, 10.0)
    corn(kit, rng, 2.0, 9.5, 8.0, 10.0)
    corn(kit, rng, -26, -10, 10.0, 12.0)
    corn(kit, rng, 10, 26, 10.0, 12.0)
    build_barn(kit)
    build_house(kit)
    for k, (x, y, h) in enumerate([(-30, 6, 7.0), (28, 10, 7.5), (46, 6, 8.0), (-34, 20, 8.0), (10, 24, 7.0)]):
        try:
            kit.prop("commontree_1", (x, y, 0), height=h, tint="#cfe8c0")
        except Exception:
            kit.cyl(f"tree{k}.t", 0.35, 3.0, (x, y, 1.5), plastic("#7a5230", 0.8), n=8)
            kit.sphere(f"tree{k}.c", 2.2, (x, y, 4.2), plastic("#5fae4a", 0.8), seg=10)
    build_jeep(kit)
    build_kitchen(kit)
    # ---------------------------------------------------------------- the flashlight (in my hand, set in animate)
    W["torch"] = kit.empty("torch", (0, 0, -50))
    kit.box("torch.body", (0.06, 0.06, 0.2), (0, 0, 0), plastic("#e8453c", 0.5, spec=0.3), W["torch"], bevel=0.01)
    tip = kit.box("torch.tip", (0.075, 0.075, 0.03), (0, 0, -0.115), kit.emit("#fff4d0", 3.0, "torchtip"), W["torch"])
    noshadow(tip)
    bm = kit._new("beam mat")
    nt = bm.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr, em, mx = (nt.nodes.new(n) for n in ("ShaderNodeBsdfTransparent", "ShaderNodeEmission", "ShaderNodeMixShader"))
    em.inputs["Color"].default_value = kit.col("#ffe9b0")
    em.inputs["Strength"].default_value = 1.0
    mx.inputs["Fac"].default_value = 0.09
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    kit._fogged(bm, mx.outputs[0])
    W["beam"] = kit.empty("beam", (0, 0, -50))
    bc = kit.cyl("beam.cone", 0.15, 1.0, (0, 0, -0.5), bm, W["beam"], n=16, r2=0.015)
    noshadow(W["beam"])
    build_tag(kit)
    return {}


def build_tag(kit):
    """The rule meter: a cream tag top-left on the camera: a crow glyph, the crow count 0, a wave glyph that lights."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    cream = kit.emit("#fff1cc", 0.9, "tagcream")
    edge = kit.emit("#3a2210", 0.5, "tagedge")
    ink = kit.emit("#2a2a40", 0.6, "tagink")
    beak = kit.emit("#ff9d1a", 0.8, "tagbeak")
    eye = kit.emit("#fff1cc", 0.9, "tageye")
    numm = kit.emit("#3a2210", 0.6, "tagnum")
    lit = kit.emit("#ff7a10", 2.2, "taglit")
    dim = kit.emit("#cdbd92", 0.5, "tagdim")

    def b(name, size, loc, mat, rot=0.0):
        ob = kit.box(name, (size[0], size[1], 0.004), (loc[0], loc[1], loc[2]), mat, root, rot=(0, 0, rot * D2R))
        noshadow(ob)
        return ob

    b("tag.edge", (1.06, 0.66), (0, 0, 0.0), edge)
    b("tag.plate", (1.0, 0.6), (0, 0, 0.004), cream)
    # crow glyph, facing right
    b("tag.cbody", (0.27, 0.16), (-0.31, -0.04, 0.008), ink)
    b("tag.chead", (0.13, 0.13), (-0.15, 0.07, 0.008), ink)
    b("tag.cbeak", (0.075, 0.04), (-0.07, 0.06, 0.008), beak)
    b("tag.ceye", (0.035, 0.035), (-0.155, 0.095, 0.012), eye)
    b("tag.ctail", (0.14, 0.05), (-0.46, -0.08, 0.008), ink, rot=20)
    b("tag.cwing", (0.15, 0.07), (-0.32, -0.03, 0.012), kit.emit("#4a4a70", 0.6, "tagwing"), rot=-15)
    b("tag.cleg1", (0.025, 0.08), (-0.34, -0.15, 0.008), beak)
    b("tag.cleg2", (0.025, 0.08), (-0.27, -0.15, 0.008), beak)
    # the count: a big 0
    b("tag.z1", (0.2, 0.06), (0.03, 0.17, 0.008), numm)
    b("tag.z2", (0.2, 0.06), (0.03, -0.17, 0.008), numm)
    b("tag.z3", (0.06, 0.4), (-0.04, 0.0, 0.008), numm)
    b("tag.z4", (0.06, 0.4), (0.1, 0.0, 0.008), numm)
    # the wave glyph: a raised hand, lit orange or dim
    W["wave_lit"], W["wave_dim"] = [], []
    for mat, store in ((lit, W["wave_lit"]), (dim, W["wave_dim"])):
        zz = 0.016 if store is W["wave_lit"] else 0.012
        tag = "l" if store is W["wave_lit"] else "d"
        store.append(b(f"tag.palm{tag}", (0.16, 0.14), (0.36, -0.1, zz), mat))
        for i, (fx, fh) in enumerate(((-0.06, 0.15), (-0.02, 0.19), (0.02, 0.19), (0.06, 0.15))):
            store.append(b(f"tag.fing{tag}{i}", (0.032, fh), (0.36 + fx, -0.03 + fh / 2, zz), mat))
        store.append(b(f"tag.thumb{tag}", (0.09, 0.034), (0.28, -0.08, zz), mat, rot=-25))
    for sg in (-1, 1):
        b(f"tag.mark{sg}", (0.025, 0.1), (0.36 + sg * 0.15, 0.12, 0.016), lit, rot=-sg * 25)


def animate(kit, story, tl, t, ctx):
    look = look_at(tl, t)
    gains = {}
    az, el = look["az"] * D2R, look["el"] * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    so = kit.LIGHTS["sun"]["obj"]
    so.location = d * 60
    kit.aim(so, (0, 0, 0))
    kit.LIGHTS["sun"]["light"].color = look["sun_col"]
    kit.LIGHTS["fill"]["light"].color = look["fill_col"]
    gains["sun"], gains["fill"] = look["sun"], look["fill"]
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*look["sky"], 1.0)
    bg.inputs["Strength"].default_value = look["sky_str"]
    for ob in [W["band"]] + W["band2"]:
        ob.hide_render = look["band"] < 0.5
    # which room is lit: all interior lights are always on (they are 100 m away), the sun can't reach them
    bpy.context.view_layer.update()
    # the flashlight: in my hand, aimed at the post's chest, eased on over 0.4 s
    fl = sample("flash", tl, t, {"on": 0.0, "bob": 0.0, "show": 0.0, "pow": 1.0, "beam": 0.0})
    me = bpy.data.objects.get("me.arm1")
    torch, L = W["torch"], kit.LIGHTS["flash"]["obj"]
    if me is not None and fl["show"] > 0.5 and not bpy.data.objects["me"].hide_render:
        tipw = me.matrix_world @ Vector((0, -0.45, -2.2))
        torch.location = tipw
        aimp = Vector((PX + 0.0, PY + 0.05, 1.6))
        if fl["bob"] > 0:
            aimp += Vector((0.5 * math.sin(t * 5.0), 0.0, 0.18 * math.sin(t * 7.3))) * fl["bob"]
        L.location = tipw
        kit.aim(L, aimp)
        torch.rotation_euler = L.rotation_euler
        _hide(torch, False)
        gains["flash"] = fl["on"] * fl["pow"]
        bm_ = W["beam"]
        dist = (aimp - tipw).length
        bm_.location = tipw
        bm_.rotation_euler = L.rotation_euler
        bm_.scale = (dist * 1.45, dist * 1.45, dist * 1.8)
        _hide(bm_, fl["on"] < 0.5 or fl["beam"] < 0.5)
    else:
        _hide(torch, True)
        _hide(W["beam"], True)
        gains["flash"] = 0.0
    # the mail jeep and its waving driver
    jx = -100.0
    for c in tl["cues"]:
        if c["name"] == "jeepgo" and c["t"] <= t:
            u = min(1.0, (t - c["t"]) / c["dur"])
            jx = c["x0"] + (c["x1"] - c["x0"]) * u
    W["jeep"].location = (jx, -15.0, 0.0)
    wv = sample("jwave", tl, t, {"on": 0.0})
    W["darm"].rotation_euler = (-(150 + 22 * math.sin(t * 11.0)) * D2R * wv["on"], 0, 0)
    # the crow that flaps away
    cf = sample("crowfly", tl, t, {"u": 0.0})
    fy = W["flyer"]
    u = cf["u"]
    base = Vector((-8.6, G.FENCE_Y + 0.2, 1.1))
    if u > 0.001:
        p = base + Vector((-3.0 * u, -2.0 * u, 5.0 * u * (1.2 - 0.5 * u)))
        fy.location = p
        fy.rotation_euler = (0, 0, (-45 - 20 * math.sin(u * 3)) * D2R)
        for piv, sx in W["wings"]:
            piv.rotation_euler = (0, sx * (0.6 * math.sin(t * 28.0)) , 0)
    else:
        fy.location = base
        fy.rotation_euler = (0, 0, -45 * D2R)
        for piv, sx in W["wings"]:
            piv.rotation_euler = (0, sx * 1.35, 0)      # wings folded
    # the crossword and the neighbor's crow in the hat
    cw = sample("crossword", tl, t, {"on": 0.0})
    _hide(W["crossword"], cw["on"] < 0.5)
    # the wave glyph and the tag
    wv2 = sample("wave", tl, t, {"on": 0.0})
    for ob in W["wave_lit"]:
        ob.hide_render = wv2["on"] < 0.5
    mk_ = sample("mask", tl, t, {"on": 1.0})
    if W.get("mask"):
        u_ = mk_["on"]          # 1: worn over the face; 0: pushed up on the hat brim (reading glasses show)
        mk = W["mask"]
        mk.location = (0.0, 0.14 * (1 - u_), MASK_UP * (1 - u_))
        mk.rotation_euler = (MASK_TILT * (1 - u_), 0.0, 0.0)
    tg = sample("tagbig", tl, t, {"k": 0.0})
    lens = 40.0
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next((s for s in story["shots"] if s["id"] == shot["id"]), None)
    if spec:
        keys = spec["cam"]
        u2 = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
        lens = keys[0][3]
        if len(keys) > 1:
            for a, b in zip(keys, keys[1:]):
                if u2 <= b[0]:
                    lens = a[3] + (b[3] - a[3]) * ss((u2 - a[0]) / max(1e-6, b[0] - a[0]))
                    break
            else:
                lens = keys[-1][3]
    dist = 0.4
    h2 = dist * 12.0 / lens
    w2 = h2 * 9.0 / 16.0
    k = ss(tg["k"])
    tag = W["tag"]
    s = 0.74 * w2 * (1 + 0.85 * k)
    tag.scale = (s, s, s)
    tag.location = (-0.54 * w2 * (1 - k), (0.78 * (1 - k) + 0.35 * k) * h2, -dist)
    # who sits: legs straight out forward, hips on the seat
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
    # the remote: on the cushion under Grandma's right hand
    gm = bpy.data.objects.get("grandma.arm-1")
    rem = W["remote"]
    if gm is not None and not bpy.data.objects["grandma"].hide_render:
        bpy.context.view_layer.update()
        hp = gm.matrix_world @ Vector((0, -0.3, -2.0))
        rem.location = (hp.x, hp.y + 0.02, max(0.5, hp.z - 0.03))
        _hide(rem, False)
    else:
        rem.hide_render = True
        for ch in rem.children:
            ch.hide_render = True
    return gains


def first_frame(kit, story):
    gp = bpy.data.objects.get("grandpa.headg")
    if gp is not None:
        m = kit.plastic("#f2f2f2", 0.8)
        for sx in (-1, 1):   # a walrus droop on each side of the nose, never one flat bar (it read as teeth)
            kit.box(f"grandpa.stache{sx}", (0.3, 0.07, 0.11), (sx * 0.17, -0.64, -0.1), m, gp, rot=(0, sx * 0.35, 0), bevel=0.03)
        for sx in (-1, 1):
            kit.box(f"grandpa.brow{sx}", (0.36, 0.06, 0.07), (sx * 0.24, -0.63, 0.17), m, gp)
    sk = kit.plastic("#d8b878", 0.9, spec=0.05)
    ink = kit.plastic("#2a2218", 0.8)
    W["mask"] = []

    def make_mask(who):
        hh = bpy.data.objects.get(f"{who}.headg")
        if hh is None:
            return None
        mk = kit.empty(f"{who}.mask", (0, 0, 0), hh)
        kit.box(f"{who}.mask.sack", (1.3, 0.06, 1.28), (0, -0.70, -0.02), sk, mk, bevel=0.05)
        for sx in (-1, 1):
            kit.box(f"{who}.mask.eye{sx}", (0.2, 0.03, 0.2), (sx * 0.29, -0.745, 0.12), ink, mk)
            kit.box(f"{who}.mask.brow{sx}", (0.3, 0.03, 0.05), (sx * 0.29, -0.745, 0.33), ink, mk)
        kit.box(f"{who}.mask.mouth", (0.56, 0.03, 0.06), (0, -0.745, -0.32), ink, mk)
        for k in range(5):
            kit.box(f"{who}.mask.st{k}", (0.05, 0.03, 0.2), (-0.28 + k * 0.14, -0.745, -0.32), ink, mk)
        return mk
    W["mask"] = make_mask("grandpa")
    make_mask("straw")           # the straw one wears the same stitched sack face, always
    # straw at Grandpa's collar and cuffs, a sack glove on each hand; the straw one the same
    straw = kit.plastic("#f0c850", 0.9, spec=0.05)
    sack = kit.plastic("#d8b878", 0.9, spec=0.05)
    for who in ("grandpa", "straw"):
        for sx in (-1, 1):
            arm = bpy.data.objects.get(f"{who}.arm{sx}")
            if arm is None:
                continue
            kit.box(f"{who}.cuff{sx}", (1.12, 1.12, 0.3), (0, 0, -1.7), straw, arm, bevel=0.04)
            for i in range(5):
                ob = kit.box(f"{who}.cs{sx}{i}", (0.1, 0.1, 0.6), (-0.4 + i * 0.2, 0.0, -1.95), straw, arm)
                ob.rotation_euler = ((i % 2 - 0.5) * 0.4, (i - 2) * 0.12, 0)
            kit.box(f"{who}.glove{sx}", (1.0, 1.02, 0.3), (0, 0, -2.0), sack, arm, bevel=0.06)
        if who == "straw":
            hg = bpy.data.objects.get("straw.headg")
            if hg is not None:
                for sx in (-1, 1):
                    for i in range(4):
                        ob = kit.box(f"straw.wisp{sx}{i}", (0.08, 0.08, 0.45), (sx * 0.58, -0.1 + i * 0.1, 0.0 - i * 0.12), straw, hg)
                        ob.rotation_euler = (0, sx * (0.5 + 0.1 * i), 0)
        up = bpy.data.objects.get(f"{who}.torso")
        if up is not None:
            for i in range(7):
                ob = kit.box(f"{who}.col{i}", (0.12, 0.12, 0.55), (-0.7 + i * 0.23, -0.2, 2.1), straw, up)
                ob.rotation_euler = ((i % 3 - 1) * 0.3, (i - 3) * 0.1, 0)


_orig_animate = animate


def animate(kit, story, tl, t, ctx):   # noqa: F811
    if not W.get("inited"):
        W["inited"] = True
        first_frame(kit, story)
    return _orig_animate(kit, story, tl, t, ctx)
