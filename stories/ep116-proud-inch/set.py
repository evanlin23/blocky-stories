"""ep116 "proud inch": Grandpa Gil's bright little hardware store, plus three montage places far to the east (a cafe
door, a tomato garden, a wedding floor) and the rule meter: a cream ruler tag on the camera, top left, in every frame.

Everything the story moves is driven by cues in story.json (see animate): the look (day or the dark dawn), who sits,
the tag's numerals, the ceiling tile, the dust, the back door, the front door, the hat, the key, the new pencil mark.
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
S = G.S
CEIL = G.CEIL


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


LOOKS = {
    "day": dict(sun=3.0, sun_col="#fff0d8", fill=0.6, fill_col="#fff2e2", front=0.45, front_col="#fff0e0", pts=0.6,
                sky="#9fd8ff", sky_str=1.0, win="#e6f6ff", win_str=3.0, pan=2.0),
    # the dark dawn: no overheads, blue light through the window, a blue front light so every face still reads
    "dark": dict(sun=0.0, sun_col="#8fa6e8", fill=0.38, fill_col="#7f9bf0", front=0.42, front_col="#9db4ff", pts=0.0,
                 sky="#3a5cb0", sky_str=0.6, win="#5b82da", win_str=2.4, pan=0.0),
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
        dur = 0.0 if dur <= 0 else max(0.4, dur)        # house bar: no switch faster than 0.3 s, unless set on a cut
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


def noshadow_ret(ob):
    noshadow(ob)
    return ob


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


# ---------------------------------------------------------------------------------------------- small builders
BIN_COLS = ["#e8493a", "#ffd23f", "#3a8fe0", "#ff9a3a", "#f6f0e0", "#4cc06a", "#a05ad8", "#ff7fb0"]


def shelf_unit(kit, name, x, y, w=1.2, d=0.5, h=2.4, face=-1, seed=0, bins=True):
    """A mint shelf unit with bright bins that carry colour dots (no lettering). face -1: bins face -y."""
    mint = kit.plastic("#7fdcc0", 0.55, spec=0.15)
    mint2 = kit.plastic("#5cc4a6", 0.55, spec=0.15)
    for sx in (-1, 1):
        kit.box(f"{name}.post{sx}", (0.06, d, h), (x + sx * (w / 2 - 0.03), y, h / 2), mint2)
    kit.box(f"{name}.back", (w, 0.03, h), (x, y - face * (d / 2 - 0.015), h / 2), mint2)
    levels = [0.25, 0.95, 1.65, 2.35]
    for i, z in enumerate(levels):
        kit.box(f"{name}.board{i}", (w, d, 0.05), (x, y, z), mint)
        if not bins or i == len(levels) - 1:
            continue
        for k in range(3):
            c = BIN_COLS[(seed + i * 3 + k * 2) % len(BIN_COLS)]
            bx = x + (k - 1) * (w / 3.1)
            bh = 0.34 if i < 2 else 0.3
            kit.box(f"{name}.bin{i}{k}", (w / 3.5, d * 0.8, bh), (bx, y + face * 0.02, z + 0.025 + bh / 2),
                    kit.plastic(c, 0.5, spec=0.2), bevel=0.02)
            kit.sphere(f"{name}.dot{i}{k}", 0.035, (bx, y + face * (d * 0.4 + 0.035), z + 0.025 + bh * 0.6),
                       kit.plastic("#fffaf0", 0.4), seg=8)


def seg_digit(kit, root, name, cx, cy, h, mat, z=0.0):
    """Seven boxes (a b c d e f g) for a numeral in the tag's plane (x right, y up, z toward the viewer)."""
    w, t = 0.6 * h, 0.21 * h
    pos = {"a": (cx, cy + h / 2 - t / 2, w, t), "g": (cx, cy, w, t), "d": (cx, cy - h / 2 + t / 2, w, t),
           "f": (cx - w / 2 + t / 2, cy + h / 4, t, h / 2 - t / 2), "b": (cx + w / 2 - t / 2, cy + h / 4, t, h / 2 - t / 2),
           "e": (cx - w / 2 + t / 2, cy - h / 4, t, h / 2 - t / 2), "c": (cx + w / 2 - t / 2, cy - h / 4, t, h / 2 - t / 2)}
    segs = {}
    for k, (x, y, sw, sh) in pos.items():
        ob = kit.box(f"{name}.{k}", (sw, sh, 0.004), (x, y, z), mat, root)
        noshadow(ob)
        segs[k] = ob
    return segs


DIGITS = {0: "abcdef", 1: "bc", 2: "abdeg", 3: "abcdg", 4: "bcfg", 5: "acdfg", 6: "acdefg", 7: "abc", 8: "abcdefg",
          9: "abcdfg"}


def flat(kit, name, x, z, w, h, mat, y, rot=0.0):
    """A flat pencil shape on the door frame, facing -y, `y` is its centre."""
    return kit.box(name, (w, 0.012, h), (x, y, z), mat, rot=(0, rot * D2R, 0))


def disc(kit, name, x, z, r, mat, y):
    return kit.cyl(name, r, 0.012, (x, y, z), mat, rot=(math.pi / 2, 0, 0), n=14)


def drawing(kit, kind, k, x, z, y):
    """A tiny pencil drawing beside a mark, about 0.17 m: a key, a lamp, a truck, a fish, a roller, a bike, a roof, a
    chair, a kettle, a door. Pictures only."""
    cols = ["#d9443a", "#2f7fd1", "#2f9e4a", "#e0900f", "#8a4fc0"]
    ci = 0 if kind == "roof" else k % len(cols)
    m = kit.emit(cols[ci], 1.2, f"pen{ci}")
    n = f"draw{k}"
    if kind == "key":
        disc(kit, n + "r", x - 0.055, z, 0.04, m, y)
        flat(kit, n + "s", x + 0.03, z, 0.12, 0.022, m, y)
        flat(kit, n + "t1", x + 0.065, z - 0.025, 0.02, 0.03, m, y)
        flat(kit, n + "t2", x + 0.1, z - 0.025, 0.02, 0.03, m, y)
    elif kind == "lamp":
        flat(kit, n + "sh", x, z + 0.04, 0.12, 0.07, m, y)
        flat(kit, n + "p", x, z - 0.02, 0.02, 0.1, m, y)
        flat(kit, n + "b", x, z - 0.075, 0.09, 0.02, m, y)
    elif kind == "truck":
        flat(kit, n + "b", x - 0.03, z, 0.13, 0.06, m, y)
        flat(kit, n + "c", x + 0.06, z - 0.01, 0.06, 0.04, m, y)
        disc(kit, n + "w1", x - 0.05, z - 0.045, 0.025, m, y)
        disc(kit, n + "w2", x + 0.06, z - 0.045, 0.025, m, y)
    elif kind == "fish":
        e = kit.sphere(n + "b", 0.05, (x, y, z), m, seg=10)
        e.scale = (1.5, 0.12, 0.9)
        flat(kit, n + "t", x + 0.09, z, 0.05, 0.05, m, y, rot=45)
    elif kind == "roller":
        flat(kit, n + "r", x, z + 0.04, 0.14, 0.045, m, y)
        flat(kit, n + "h", x + 0.07, z - 0.005, 0.02, 0.06, m, y)
        flat(kit, n + "g", x + 0.07, z - 0.06, 0.02, 0.07, m, y)
    elif kind == "bike":
        disc(kit, n + "w1", x - 0.06, z - 0.02, 0.05, m, y)
        disc(kit, n + "w2", x + 0.07, z - 0.02, 0.05, m, y)
        flat(kit, n + "f", x + 0.005, z + 0.015, 0.1, 0.018, m, y)
        flat(kit, n + "h", x + 0.07, z + 0.045, 0.03, 0.018, m, y)
    elif kind == "roof":
        # a plain house: a square with a triangle roof (a three-sided prism, apex up)
        flat(kit, n + "h", x, z - 0.03, 0.09, 0.07, m, y)
        kit.cyl(n + "tri", 0.062, 0.012, (x, y, z + 0.032), m, rot=(math.pi / 2, -math.pi / 2, 0), n=3)
    elif kind == "chair":
        flat(kit, n + "s", x, z - 0.01, 0.1, 0.02, m, y)
        flat(kit, n + "b", x - 0.045, z + 0.04, 0.02, 0.09, m, y)
        flat(kit, n + "l1", x - 0.04, z - 0.055, 0.02, 0.07, m, y)
        flat(kit, n + "l2", x + 0.04, z - 0.055, 0.02, 0.07, m, y)
    elif kind == "kettle":
        kit.sphere(n + "b", 0.055, (x, y, z), m, seg=10).scale = (1, 0.12, 0.9)
        flat(kit, n + "s", x + 0.075, z + 0.015, 0.05, 0.016, m, y, rot=25)
        flat(kit, n + "h", x, z + 0.06, 0.07, 0.016, m, y)
    elif kind == "door":
        flat(kit, n + "d", x, z, 0.09, 0.15, m, y)
        disc(kit, n + "k", x + 0.025, z - 0.005, 0.012, kit.emit("#fff4d8", 1.5, "penk"), y - 0.008)


DRAWS = {3: "key", 9: "lamp", 15: "truck", 21: "fish", 26: "roller", 31: "bike", 36: "roof", 41: "chair", 46: "kettle"}


def hide(ob, h):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


# ---------------------------------------------------------------------------------------------- the world
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    P = kit.plastic
    cream = P("#9fd6ee", 0.85, spec=0.05)
    cream2 = P("#fff4dc", 0.8, spec=0.05)
    honey = P("#d9a35a", 0.5, spec=0.25)
    honey2 = P("#e8b66a", 0.45, spec=0.3)
    wood = P("#b9803f", 0.6, spec=0.15)
    brass = P("#e3b04b", 0.35, spec=0.6)
    floor_m = kit.planks("#e6c58f", "#d1a96d", 1.0, "X", "floorp", 0.7)
    ceil_m = P("#b3ae9f", 0.85, spec=0.03)
    plenum = P("#2d2f36", 0.9, spec=0.0)

    # ---- lights (gains set in animate)
    sun = kit.light("sun", "SUN", (0, -30, 40), 1.0, "#fff0d8", size=0.06)
    sun.data.angle = 0.08
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#fff2e2", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    front = kit.light("front", "SUN", (-6, -30, 18), 1.0, "#fff0e0", shadow=False)
    front.data.angle = 0.4
    kit.aim(front, (0, 0, 0))
    for nm, loc, e in [("pL1", (0.0, 1.0, 3.0), 380.0), ("pL2", (3.0, 0.4, 2.9), 300.0), ("pL3", (-4.0, 2.2, 3.0), 380.0),
                       ("pL4", (-3.0, -3.0, 2.8), 300.0), ("pL5", (2.4, 3.2, 3.0), 240.0), ("pL6", (1.0, -3.5, 2.6), 260.0)]:
        kit.light(nm, "POINT", loc, e, "#ffe8c4", size=0.5, shadow=False)
    kit.light("dk", "POINT", (-3.6, -1.2, 2.3), 320.0, "#a9c0ff", size=0.5, shadow=False)
    kit.light("stock", "POINT", (2.75, 6.8, 2.4), 150.0, "#fff0d0", size=0.4, shadow=False)

    # ---- the shop shell
    kit.box("floor", (12.4, 11.0, 0.1), (-1.55, -0.75, -0.05), floor_m)
    kit.plane("ground", (700, 700), (0, 0, -0.12), P("#b9dca0", 0.9, spec=0.02))
    y0, y1 = G.FRONT_Y, G.BACK_Y
    xl, xr = -7.5, 4.4
    # back wall with the doorway
    kit.box("bw.l", (G.POST_X0 - xl, 0.3, CEIL), ((xl + G.POST_X0) / 2, y1 + 0.15, CEIL / 2), cream)
    kit.box("bw.r", (xr - G.DOOR_X1, 0.3, CEIL), ((xr + G.DOOR_X1) / 2, y1 + 0.15, CEIL / 2), cream)
    kit.box("bw.top", (G.DOOR_X1 - G.POST_X0, 0.3, CEIL - G.DOOR_TOP), ((G.POST_X0 + G.DOOR_X1) / 2, y1 + 0.15, (CEIL + G.DOOR_TOP) / 2), cream)
    # a dark trim round the doorway so the door top edge reads (1 cm proud of the wall face)
    trim = P("#6b4a2e", 0.7)
    kit.box("dw.lintel", (G.DOOR_X1 - G.DOOR_X0 + 0.12, 0.02, 0.12), ((G.DOOR_X0 + G.DOOR_X1) / 2, y1 - 0.01, G.DOOR_TOP + 0.06), trim)
    kit.box("dw.jl", (0.06, 0.02, G.DOOR_TOP), (G.DOOR_X0 - 0.03 + 0.0, y1 - 0.01, G.DOOR_TOP / 2), trim)
    kit.box("dw.jr", (0.06, 0.02, G.DOOR_TOP), (G.DOOR_X1 + 0.03, y1 - 0.01, G.DOOR_TOP / 2), trim)
    kit.box("bw.mid", (G.DOOR_X1 - G.DOOR_X0, 0.3, 0.02), ((G.DOOR_X0 + G.DOOR_X1) / 2, y1 + 0.15, 0.01), cream)
    # side walls, front wall with window and door
    kit.box("lw", (0.3, y1 - y0, CEIL), (xl - 0.15, (y0 + y1) / 2, CEIL / 2), cream)
    kit.box("rw", (0.3, y1 - y0, CEIL), (xr + 0.15, (y0 + y1) / 2, CEIL / 2), cream)
    kit.box("fw.l1", (-6.15 - xl, 0.3, CEIL), ((xl - 6.15) / 2, y0 - 0.15, CEIL / 2), cream)
    kit.box("fw.l2", (-3.0 + 5.05, 0.3, CEIL), ((-5.05 - 3.0) / 2, y0 - 0.15, CEIL / 2), cream)
    kit.box("fw.r", (xr - 2.5, 0.3, CEIL), ((xr + 2.5) / 2, y0 - 0.15, CEIL / 2), cream)
    kit.box("fw.below", (5.5, 0.3, 0.9), (-0.25, y0 - 0.15, 0.45), cream)
    kit.box("fw.above", (5.5, 0.3, CEIL - 2.6), (-0.25, y0 - 0.15, (CEIL + 2.6) / 2), cream)
    W["win_m"] = kit.emit("#e6f6ff", 3.0, "winlight")
    kit.box("fw.pane", (5.5, 0.04, 1.7), (-0.25, y0 - 0.25, 1.75), W["win_m"])
    for i in range(-2, 3):
        kit.box(f"fw.mull{i}", (0.07, 0.07, 1.74), (-0.25 + i * 1.1, y0 - 0.03, 1.75), cream2)
    kit.box("fw.sill", (5.8, 0.2, 0.06), (-0.25, y0 + 0.05, 0.93), honey)
    # the front door (hinged on the left, swings in) and its opening
    fx = G.FDOOR_X
    kit.box("fd.head", (1.2, 0.3, CEIL - 2.2), (fx, y0 - 0.15, (CEIL + 2.2) / 2), cream)
    hinge = kit.empty("fdoor.hinge", (fx - 0.55, y0 + 0.1, 0.0))
    W["fdoor"] = hinge
    kit.box("fdoor.panel", (1.1, 0.06, 2.2), (0.55, 0, 1.1), P("#e86a5a", 0.55, spec=0.2), hinge)
    kit.box("fdoor.glass", (0.6, 0.07, 0.8), (0.55, 0, 1.6), kit.emit("#bfe2ff", 1.5, "fdglass"), hinge)
    kit.sphere("fdoor.knob", 0.05, (0.95, 0.05, 1.05), brass, hinge, seg=8)
    kit.box("bell.arm", (0.3, 0.04, 0.04), (fx + 0.2, y0 + 0.2, 2.35), P("#6b4a2e", 0.7))
    kit.cyl("bell", 0.07, 0.1, (fx + 0.35, y0 + 0.2, 2.28), brass, n=10, r2=0.04)
    # outside the front: a street, neighbours
    kit.box("street", (60, 14, 0.05), (0, y0 - 8, -0.1), P("#8f9aa8", 0.9, spec=0.05))
    for i, (bx, col_, hh) in enumerate([(-9, "#ffb36b", 5.5), (-1, "#8fd0ff", 7.0), (7, "#ff9fb0", 4.8), (15, "#b6e08a", 6.0)]):
        kit.box(f"nbr{i}", (6.0, 3.0, hh), (bx, y0 - 17, hh / 2), P(col_, 0.8, spec=0.05))
        for wi in range(2):
            kit.box(f"nbr{i}w{wi}", (1.0, 0.1, 1.1), (bx - 1.3 + wi * 2.6, y0 - 15.45, 2.6), P("#fff4d8", 0.5))
    # ceiling: tiles on a 0.8 grid, one of them (over the crate) is the one that lifts
    kit.plane("plenum", (14, 13), (-1.6, -0.75, CEIL + 0.14), plenum)
    kit.box("plenum.void", (0.62, 0.62, 0.06), (G.G_POS[0], G.G_POS[1], CEIL + 0.1), plenum)
    for ix in range(-13, 2):
        for iy in range(-9, 5):
            x, y = G.G_POS[0] + 0.8 * ix, G.G_POS[1] + 0.8 * iy
            if ix == 0 and iy == 0:
                continue
            if x < xl - 0.4 or x > xr + 0.4 or y < y0 - 0.4 or y > y1 + 0.4:
                continue
            kit.box(f"ct{ix}_{iy}", (0.78, 0.78, 0.04), (x, y, CEIL - 0.02), ceil_m)
    W["tile"] = kit.box("tile", (0.78, 0.78, 0.04), (G.G_POS[0], G.G_POS[1], CEIL - 0.02), ceil_m)
    W["tile_base"] = Vector((G.G_POS[0], G.G_POS[1], CEIL - 0.02))
    rim = kit.emit("#fff6dc", 9.0, "tilerim")
    W["rim"] = noshadow_ret(kit.box("tile.rim", (0.78, 0.05, 0.03), (0, -0.39, -0.02), rim, W["tile"]))
    # overhead panels (fixed flat lights, no cords)
    pan = kit.emit("#fffaf0", 2.0, "panel")
    W["pan_m"] = pan
    for px, py in [(-4.0, 1.6), (0.0, 1.6), (-4.0, -2.4), (0.0, -2.4)]:
        noshadow(kit.box(f"panel{px}{py}", (1.5, 0.5, 0.03), (px, py, CEIL - 0.07), pan))

    # ---- shelves, bins
    for i, x in enumerate([-6.8, -5.6, -4.4, -3.2, -2.0, -0.8, 0.4]):
        shelf_unit(kit, f"su{i}", x, y1 - 0.25, seed=i * 3)
    # the hat shelf on the right wall beside Grandpa
    hx, hy = 4.15, G.G_POS[1]
    kit.box("hatshelf", (0.5, 1.5, 0.06), (hx, hy, 2.72), mint_shelf(kit))
    for sy in (-1, 1):
        kit.box(f"hatbrk{sy}", (0.05, 0.06, 0.3), (hx + 0.2, hy + sy * 0.6, 2.58), wood)
    hat = kit.empty("hat", (hx, hy, 2.75))
    W["hat"] = hat
    felt = P("#6b4a2e", 0.85, spec=0.05)
    kit.cyl("hat.crown", 0.17, 0.2, (0, 0, 0.13), felt, hat, n=14)
    kit.cyl("hat.brim", 0.3, 0.035, (0, 0, 0.02), felt, hat, n=18)
    kit.cyl("hat.band", 0.178, 0.05, (0, 0, 0.07), P("#d9443a", 0.6), hat, n=14)
    W["hat_shelf"] = Vector((hx, hy, 2.75))

    # ---- the counter
    kit.box("counter", (6.2, 1.0, 1.0), (-1.9, 0.0, 0.5), honey)
    kit.box("counter.top", (6.4, 1.12, 0.08), (-1.9, 0.0, 1.04), honey2, bevel=0.02)
    for i in range(6):
        kit.box(f"counter.panel{i}", (0.95, 0.03, 0.7), (-4.55 + i * 1.07, -0.515, 0.5), P("#c18742", 0.55, spec=0.2))
    # key machine with a brass vise jaw (lore: two pencil-yellow strokes on the jaw)
    kx = -1.8
    kit.box("keym.base", (0.7, 0.45, 0.3), (kx, 0.0, 1.23), P("#5a6a8a", 0.4, spec=0.4), bevel=0.03)
    kit.box("keym.arm", (0.12, 0.12, 0.3), (kx + 0.28, 0.1, 1.5), P("#d9443a", 0.4), bevel=0.02)
    kit.box("keym.jaw", (0.36, 0.12, 0.2), (kx - 0.08, -0.26, 1.45), brass, bevel=0.015)
    ym = kit.emit("#ffcf3a", 2.0, "stroke")
    for i in range(2):
        kit.box(f"keym.stroke{i}", (0.03, 0.006, 0.15), (kx - 0.14 + i * 0.08, -0.33, 1.45), ym)
    # till with numerals
    kit.box("till", (0.7, 0.55, 0.3), (-3.6, 0.1, 1.23), P("#b8c0cc", 0.4, spec=0.4), bevel=0.03)
    kit.box("till.screen", (0.4, 0.04, 0.16), (-3.6, -0.17, 1.42), kit.emit("#1c2a22", 0.5, "tillscr"))
    dm = kit.emit("#7dff9a", 2.0, "tilldig")
    for i, dv in enumerate([2, 5, 0]):
        d = kit.empty(f"tdig{i}", (-3.72 + i * 0.12, -0.2, 1.42), rot=(math.pi / 2, 0, 0))
        sg = seg_digit(kit, d, f"tdig{i}", 0, 0, 0.1, dm)
        for kseg, ob in sg.items():
            ob.hide_render = kseg not in DIGITS[dv]
    # things on the counter near the end: a bike wheel, a lamp, a hinge
    cx = 0.75
    tire = kit.cyl("wheel.tire", 0.33, 0.07, (cx, 0.25, 1.38), P("#2d3036", 0.8), rot=(math.pi / 2, 0, 0), n=20)
    kit.cyl("wheel.rim", 0.25, 0.08, (cx, 0.25, 1.38), P("#c8ced8", 0.3, spec=0.6), rot=(math.pi / 2, 0, 0), n=20)
    kit.cyl("wheel.hub", 0.05, 0.1, (cx, 0.25, 1.38), brass, rot=(math.pi / 2, 0, 0), n=10)
    lx = 1.0
    kit.cyl("lamp.base", 0.13, 0.04, (lx, 0.2, 1.1), P("#e8493a", 0.5), n=14)
    kit.cyl("lamp.stem", 0.025, 0.4, (lx, 0.2, 1.3), brass, n=8)
    kit.cyl("lamp.shade", 0.18, 0.22, (lx, 0.2, 1.58), kit.emit("#ffe49a", 1.4, "lampshade"), n=14, r2=0.1)
    hg = kit.empty("hinge.obj", (0.95, -0.35, 1.09))
    W["hinge"] = hg
    kit.box("hinge.l1", (0.16, 0.1, 0.012), (-0.08, 0, 0.006), brass, hg)
    kit.box("hinge.l2", (0.16, 0.1, 0.012), (0.08, 0.02, 0.006), brass, hg, rot=(0, 0, 0.5))
    kit.cyl("hinge.pin", 0.012, 0.11, (0, 0, 0.012), P("#8d9096", 0.3), hg, rot=(math.pi / 2, 0, 0), n=8)

    # ---- Grandpa's crate (upturned), cart, cartons
    kit.box("crate", (0.8, 0.7, G.CRATE_H), (G.G_POS[0], G.G_POS[1], G.CRATE_H / 2), P("#d99a4a", 0.65, spec=0.1), bevel=0.02)
    for i in range(6):
        kit.box(f"crate.slatL{i}", (0.03, 0.72, 0.06), (G.G_POS[0] - 0.41, G.G_POS[1], 0.08 + i * 0.13), P("#9c6a2c", 0.7))
        kit.box(f"crate.slat{i}", (0.82, 0.03, 0.06), (G.G_POS[0], G.G_POS[1] - 0.36, 0.08 + i * 0.13), P("#9c6a2c", 0.7))
        kit.box(f"crate.slatR{i}", (0.03, 0.72, 0.06), (G.G_POS[0] + 0.41, G.G_POS[1], 0.08 + i * 0.13), P("#9c6a2c", 0.7))
    kit.box("rug", (2.4, 1.6, 0.012), (3.0, 0.4, 0.006), P("#e8654a", 0.9, spec=0.02))

    # ---- the marked door frame and the stockroom
    fr = cream2
    ybo = y1 - 0.03                       # boards sit 6 cm proud of the wall face (y1)
    kit.box("post.l", (0.5, 0.06, CEIL), ((G.POST_X0 + G.DOOR_X0) / 2, y1 - 0.03, CEIL / 2), fr)
    kit.box("post.r", (0.25, 0.06, G.DOOR_TOP), (G.DOOR_X1 + 0.125, y1 - 0.03, G.DOOR_TOP / 2), fr)
    kit.box("post.hdr", (G.DOOR_X1 - G.POST_X0 + 0.25, 0.06, 0.25), ((G.POST_X0 + G.DOOR_X1 + 0.25) / 2, y1 - 0.03, G.DOOR_TOP + 0.125), fr)
    # stockroom
    sx0, sx1 = G.DOOR_X0 - 0.3, G.DOOR_X1 + 1.2
    kit.box("st.floor", (sx1 - sx0, 4.0, 0.06), ((sx0 + sx1) / 2, y1 + 2.0, -0.03), P("#cfa66f", 0.8))
    kit.box("st.back", (sx1 - sx0, 0.1, 3.0), ((sx0 + sx1) / 2, y1 + 4.0, 1.5), P("#fff0cc", 0.8))
    kit.box("st.side", (0.1, 4.0, 3.0), (sx0 - 0.05, y1 + 2.0, 1.5), P("#fff0cc", 0.8))
    kit.box("st.side2", (0.1, 4.0, 3.0), (sx1 + 0.05, y1 + 2.0, 1.5), P("#fff0cc", 0.8))
    kit.box("st.ceil", (sx1 - sx0, 4.0, 0.06), ((sx0 + sx1) / 2, y1 + 2.0, 3.0), P("#fff0cc", 0.8))
    for i, (bx, by, bz, c) in enumerate([(2.6, 7.4, 0.35, "#c98a4a"), (3.4, 7.5, 0.3, "#d99a4a"), (4.4, 6.5, 0.4, "#7fdcc0")]):
        kit.box(f"st.box{i}", (0.8, 0.7, bz * 2), (bx, by, bz), P(c, 0.6), bevel=0.02)
    # the back door itself (stuck, hinged on the right, swings into the stockroom)
    bh = kit.empty("bdoor.hinge", (G.DOOR_X1, y1 + 0.1, 0.0))
    W["bdoor"] = bh
    kit.box("bdoor.panel", (G.DOOR_X1 - G.DOOR_X0 - 0.02, 0.07, G.DOOR_TOP - 0.02),
            (-(G.DOOR_X1 - G.DOOR_X0) / 2, 0, G.DOOR_TOP / 2), P("#8fc4ff", 0.5, spec=0.2), bh)
    kit.sphere("bdoor.knob", 0.055, (-1.15, -0.06, 1.05), brass, bh, seg=8)
    kit.box("bdoor.panelb", (0.5, 0.075, 0.9), (-0.7, 0, 1.55), P("#6fa8e8", 0.5, spec=0.2), bh)
    # pencil marks climbing the left post, a tiny drawing beside every few
    gm = kit.emit("#3b3b46", 1.2, "mark")
    ym_ = y1 - 0.062
    for k in range(G.MARKS):
        z = G.MARK_Z0 + G.MARK_DZ * k
        long = 0.22 if k % 5 == 0 else 0.15
        kit.box(f"mark{k}", (long, 0.008, 0.012), (G.MARK_X - 0.05 + long / 2 - 0.075, ym_, z), gm)
        if k in DRAWS:
            drawing(kit, DRAWS[k], k, 1.93, z, ym_ - 0.002)
    # the new mark with a tiny door, shown at the end
    z = G.MARK_Z0 + G.MARK_DZ * G.MARKS
    new = kit.empty("newmark", (0, 0, 0))
    new.scale = (1.6, 1.6, 1.6)                  # bigger than the old marks, so it reads from across the room
    new.location = (1.7 * (1 - 1.6), ym_ * (1 - 1.6), z * (1 - 1.6))
    W["newmark"] = new
    kit.box("newmark.line", (0.22, 0.008, 0.016), (G.MARK_X - 0.025, ym_ - 0.002, z), kit.emit("#d9443a", 1.4, "newm"), new)
    drawing(kit, "door", 7, 1.93, z, ym_ - 0.002)
    for ob in [o for o in bpy.data.objects if o.name.startswith("draw7")]:
        ob.parent = new
    # dust for the tile
    W["dust"] = []
    dm_ = P("#a39d92", 0.95, spec=0.0)
    for i in range(36):
        a = i * 2.4
        r_ = 0.35 + 0.65 * ((i * 7) % 11) / 10.0
        W["dust"].append((kit.box(f"dust{i}", (0.045, 0.045, 0.045), (G.G_POS[0], G.G_POS[1], CEIL - 0.1), dm_),
                          (r_ * math.cos(a), r_ * math.sin(a), -0.25 - 0.3 * ((i * 5) % 7) / 6.0)))

    # ---- the montage places
    # a cafe door: a low doorway and an awning, the lintel is below a tall man's head
    cx0, cy0 = G.CAFE
    kit.plane("cafe.ground", (30, 30), (cx0, cy0 - 6, -0.01), P("#e8d6b0", 0.9, spec=0.02))
    for nm, (bx, sz) in {"l": (cx0 - 2.6, 3.4), "r": (cx0 + 2.6, 3.4)}.items():
        kit.box(f"cafe.w{nm}", (sz, 0.4, 3.4), (bx, cy0 + 0.2, 1.7), P("#ff9fb0", 0.8, spec=0.05))
    kit.box("cafe.top", (2.0, 0.4, 1.8), (cx0, cy0 + 0.2, 2.5), P("#ff9fb0", 0.8, spec=0.05))   # a low door: its top edge at 1.6
    kit.box("cafe.in", (2.0, 2.0, 1.6), (cx0, cy0 + 1.3, 0.8), P("#ffcf88", 0.7))
    for i in range(8):
        kit.box(f"cafe.aw{i}", (0.5, 1.0, 0.1), (cx0 - 1.75 + i * 0.5, cy0 - 0.5, 2.75), P("#e8493a" if i % 2 else "#fffaf0", 0.6))
    kit.box("cafe.frame", (2.0, 0.1, 0.1), (cx0, cy0 - 0.02, 1.6), P("#7a4a2a", 0.7))
    kit.light("cafel", "POINT", (cx0, cy0 - 2.0, 2.4), 200.0, "#fff0d8", size=0.5, shadow=False)
    # a tomato garden: a fence, rows of plants at knee height
    gx, gy = G.GARDEN
    kit.plane("gar.ground", (30, 30), (gx, gy, -0.01), P("#9fcf7a", 0.95, spec=0.02))
    kit.plane("gar.soil", (12, 3.5), (gx, gy + 0.6, 0.005), P("#8a5a3a", 0.95, spec=0.02))
    kit.box("gar.fence", (14, 0.1, 1.0), (gx, gy + 5.0, 0.5), P("#fff4e0", 0.8))
    for i in range(14):
        kit.box(f"gar.post{i}", (0.1, 0.12, 1.15), (gx - 6.5 + i, gy + 5.0, 0.55), P("#fff4e0", 0.8))
    for i in range(12):
        px = gx - 5.5 + i * 1.0
        for j, py in enumerate((gy - 0.2, gy + 1.3)):
            kit.cyl(f"tom{i}{j}.st", 0.025, 0.5, (px, py, 0.25), P("#4f8f3a", 0.8), n=6)
            kit.sphere(f"tom{i}{j}.lf", 0.3, (px, py, 0.5), P("#3fae44", 0.8), seg=8).scale = (1.0, 0.9, 0.8)
            kit.box(f"tom{i}{j}.cage", (0.04, 0.04, 0.9), (px - 0.28, py, 0.45), P("#e8e8f0", 0.5))
            for q in range(2):
                kit.sphere(f"tom{i}{j}.fr{q}", 0.08, (px + (0.14 if q else -0.12), py - 0.2, 0.42 + 0.1 * q), P("#e8352a", 0.4, spec=0.4), seg=8)
    # a wedding floor: checker tiles, bunting, a flower arch
    wx, wy = G.WEDDING
    kit.plane("wed.ground", (40, 40), (wx, wy, -0.02), P("#cfe8b0", 0.95, spec=0.02))
    kit.box("wed.floor", (8, 6, 0.04), (wx, wy, 0.0), kit.checker("#fff4d8", "#ffcf8a", 3.0, "wedchk"))
    kit.box("wed.back", (10, 0.2, 3.4), (wx, wy + 3.2, 1.7), P("#ffd9e0", 0.8, spec=0.05))
    for i in range(10):
        kit.box(f"wed.flag{i}", (0.4, 0.04, 0.4), (wx - 4.0 + i * 0.9, wy + 3.0, 2.8 - 0.1 * (i % 2)), P(BIN_COLS[i % 8], 0.5),
                rot=(0, 0.785, 0))
    for sx in (-1, 1):
        kit.cyl(f"wed.arch{sx}", 0.12, 3.0, (wx + sx * 1.6, wy + 2.9, 1.5), P("#fffaf0", 0.7), n=10)
    kit.box("wed.archtop", (3.4, 0.2, 0.25), (wx, wy + 2.9, 3.0), P("#fffaf0", 0.7))
    for i in range(16):
        kit.sphere(f"wed.fl{i}", 0.14, (wx - 1.6 + (i % 8) * 0.45, wy + 2.8, 2.95 + 0.1 * (i // 8)), P(BIN_COLS[(i * 3) % 8], 0.5), seg=8)
    kit.light("wedl", "POINT", (wx, wy - 2.0, 2.6), 200.0, "#fff0d8", size=0.5, shadow=False)
    kit.light("gardl", "POINT", (gx, gy - 2.5, 2.4), 100.0, "#fff0d8", size=0.5, shadow=False)

    build_tag(kit)
    return {}


def mint_shelf(kit):
    return kit.plastic("#7fdcc0", 0.55, spec=0.15)


# ---------------------------------------------------------------------------------------------- the rule meter
def build_tag(kit):
    """A cream tag on the camera, top left: a ruler glyph and Grandpa's height in feet and inches (9'0"), and under it a
    smaller row for me (5'9") with a little red apron glyph. Numerals and glyphs only."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    edge = kit.emit("#4a2f17", 0.7, "tagedge")
    plate = kit.emit("#fff3cf", 0.9, "tagplate")
    ink = kit.emit("#2a1a0c", 0.6, "taginK")
    yel = kit.emit("#ffcf3a", 1.0, "tagruler")
    red = kit.emit("#e8493a", 1.0, "tagred")

    def b(name, size, loc, mat):
        ob = kit.box(name, size, loc, mat, root)
        noshadow(ob)
        return ob
    b("tag.edge", (1.12, 0.96, 0.004), (0, 0, 0.0), edge)
    b("tag.plate", (1.06, 0.9, 0.004), (0, 0, 0.004), plate)
    b("tag.div", (0.96, 0.014, 0.004), (0, 0.0, 0.008), ink)
    # the ruler glyph: a tall yellow bar with ticks (row 1)
    b("tag.ruler", (0.15, 0.34, 0.004), (-0.4, 0.24, 0.008), yel)
    for i in range(5):
        ln = 0.09 if i % 2 == 0 else 0.06
        b(f"tag.tick{i}", (ln, 0.018, 0.004), (-0.475 + ln / 2, 0.13 + i * 0.065, 0.012), ink)
    # my apron glyph (row 2)
    b("tag.apron", (0.16, 0.2, 0.004), (-0.4, -0.25, 0.008), red)
    b("tag.apron2", (0.07, 0.07, 0.004), (-0.4, -0.28, 0.012), plate)
    rows = {}
    # feet, a fat dot, then the inches: "9 . 0" and "5 . 10", big digits and no thin marks
    for name, cy, h in [("g", 0.24, 0.34), ("m", -0.25, 0.34)]:
        slots = {}
        for key, cx in [("feet", -0.2), ("tens", 0.06), ("ones", 0.34)]:
            slots[key] = seg_digit(kit, root, f"tag.{name}.{key}", cx, cy, h, ink, 0.012)
        b(f"tag.{name}.dot", (0.06, 0.06, 0.004), (-0.04, cy - h * 0.4, 0.012), ink)
        rows[name] = slots
    W["rows"] = rows
    W["tag_state"] = None


def set_digit(segs, val):
    lit = DIGITS.get(val, "") if val is not None else ""
    for k, ob in segs.items():
        ob.hide_render = k not in lit


# ---------------------------------------------------------------------------------------------- the cast's extras
def _first_frame(kit, story):
    import blocky.rig as rig
    gh = bpy.data.objects.get("grandpa.headg")
    if gh is not None:
        pass
    # Grandpa's trouser legs: shortened, three strips of different cloth sewn on, his shins showing above the boots
    gspec = story["cast"].get("grandpa", {})
    skin = kit.plastic(gspec.get("skin", "#e2b088"), 0.5)
    navy = kit.plastic("#2f4a8a", 0.7)
    green = kit.plastic("#4a8f4a", 0.7)
    plaid = rig.cloth({"shirt": "#c0402a", "pattern": "plaid", "pattern_c": "#f1dda0"}, "shirt")
    for sx in (-1, 1):
        lg = bpy.data.objects.get(f"grandpa.leg{sx}")
        lm = bpy.data.objects.get(f"grandpa.legm{sx}")
        if lg is None or lm is None:
            continue
        lm.scale = (1.0, 1.0, 1.05 / 1.72)
        lm.location.z = -0.525
        kit.box(f"grandpa.hem1{sx}", (1.03, 1.05, 0.14), (0, 0, -1.12), navy, lg, bevel=0.03)
        kit.box(f"grandpa.hem2{sx}", (1.03, 1.05, 0.14), (0, 0, -1.26), green, lg, bevel=0.03)
        kit.box(f"grandpa.hem3{sx}", (1.03, 1.05, 0.14), (0, 0, -1.40), plaid, lg, bevel=0.03)
        kit.box(f"grandpa.shin{sx}", (0.6, 0.62, 0.3), (0, 0, -1.62), skin, lg, bevel=0.03)
    # the bride's dad on his knees: his thighs stand on the floor (the floor hides the rest of the rig leg), the shins
    # lie folded back along the floor behind him with the shoe soles up (rig units: the floor is at z 1.0 here)
    bd = bpy.data.objects.get("bridedad")
    if bd is not None:
        slacks = kit.plastic("#6a707c", 0.7)
        shoe = kit.plastic("#2a2a2a", 0.6)
        for sx in (-1, 1):
            kit.box(f"bridedad.shin{sx}", (0.98, 1.7, 0.7), (sx * 0.5, 1.0, 1.4), slacks, bd, bevel=0.03)
            kit.box(f"bridedad.sole{sx}", (0.98, 0.6, 0.62), (sx * 0.5, 2.1, 1.4), shoe, bd, bevel=0.03)
    # things held in front of the chest, on flat palms
    def held(owner, name, build, loc):
        root = bpy.data.objects.get(owner)
        if root is None:
            return None
        h = kit.empty(f"{owner}.{name}", loc, root)
        build(h)
        return h
    P = kit.plastic

    def tomato(h):
        kit.sphere(f"{h.name}.t", 0.5, (0, 0, 0.5), P("#e8352a", 0.35, spec=0.5), h, seg=14)
        kit.cyl(f"{h.name}.c", 0.2, 0.08, (0, 0, 1.0), P("#3f9a3a", 0.7), h, n=7)

    def faucet(h):
        m = P("#e0742a", 0.35, spec=0.4)
        kit.cyl(f"{h.name}.b", 0.28, 0.5, (0, 0, 0.25), m, h, n=14)
        kit.cyl(f"{h.name}.n", 0.16, 0.9, (0, 0, 0.95), m, h, n=12)
        kit.box(f"{h.name}.s", (0.18, 0.9, 0.16), (0, -0.4, 1.4), m, h, bevel=0.04)
        kit.box(f"{h.name}.h", (0.7, 0.12, 0.12), (0, 0, 0.8), P("#23318a", 0.4), h)

    def key(h):
        m = P("#f2c14a", 0.3, spec=0.6)
        kit.cyl(f"{h.name}.r", 0.2, 0.06, (0, 0, 0.1), m, h, rot=(math.pi / 2, 0, 0), n=12)
        kit.box(f"{h.name}.s", (0.7, 0.07, 0.08), (0.45, 0, 0.1), m, h)
        kit.box(f"{h.name}.t1", (0.08, 0.07, 0.16), (0.65, 0, 0.0), m, h)
        kit.box(f"{h.name}.t2", (0.08, 0.07, 0.16), (0.5, 0, 0.0), m, h)

    W["tomato"] = held("mail", "tomato", tomato, (1.5, -1.35, 4.26))
    if W["tomato"] is not None:
        W["tomato"].scale = (1.0, 1.0, 1.0)
    W["faucet"] = held("bloom", "faucet", faucet, (-0.55, -1.4, 3.55))
    if W["faucet"] is not None:
        W["faucet"].scale = (0.95, 0.95, 0.95)
        W["faucet"].rotation_euler = (0, math.pi / 2, 0)       # lying across both palms
    W["key"] = held("me", "key", key, (1.3, -1.35, 4.26))
    W["inited"] = True


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    look = look_at(tl, t)
    gains = {}
    sun = kit.LIGHTS["sun"]
    az, el = -25 * D2R, 50 * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    sun["obj"].location = d * 60
    kit.aim(sun["obj"], (0, 0, 0))
    sun["light"].color = look["sun_col"]
    kit.LIGHTS["fill"]["light"].color = look["fill_col"]
    kit.LIGHTS["front"]["light"].color = look["front_col"]
    gains["sun"], gains["fill"], gains["front"] = look["sun"], look["fill"], look["front"]
    for nm in ("pL1", "pL2", "pL3", "pL4", "pL5", "pL6"):
        gains[nm] = look["pts"]
    gains["dk"] = 0.55 * (1.0 - min(1.0, look["pts"] / 0.6))
    W["pan_m"].node_tree.nodes["Emission"].inputs["Strength"].default_value = max(0.02, look["pan"])
    gains["stock"] = max(look["pts"], 0.25)
    gains["cafel"] = gains["wedl"] = gains["gardl"] = 1.0
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*look["sky"], 1.0)
    bg.inputs["Strength"].default_value = look["sky_str"]
    em = W["win_m"].node_tree.nodes["Emission"]
    em.inputs["Color"].default_value = (*look["win"], 1.0)
    em.inputs["Strength"].default_value = look["win_str"]
    # the tag: numerals, with a small pop when they change
    tg = sample("tag", tl, t, {"g": 0.0, "m": 9.0})
    g_in, m_in = int(round(tg["g"])), int(round(tg["m"]))
    state = (g_in, m_in)
    if W.get("tag_state") != state:
        W["tag_state"] = state
        r = W["rows"]
        set_digit(r["g"]["feet"], 9)
        set_digit(r["g"]["tens"], 1 if g_in >= 10 else None)
        set_digit(r["g"]["ones"], g_in % 10)
        set_digit(r["m"]["feet"], 5)
        set_digit(r["m"]["tens"], 1 if m_in >= 10 else None)
        set_digit(r["m"]["ones"], m_in % 10)
    pop = 1.0
    for c in tl["cues"]:
        if c["name"] == "tag" and c["t"] <= t < c["t"] + 0.4:
            pop = 1.0 + 0.1 * math.sin(math.pi * (t - c["t"]) / 0.4)
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
    s = 0.5 * w2 * pop
    tag.scale = (s, s, s)
    tag.location = (-0.37 * w2, 0.6 * h2, -dist)
    # who sits: legs straight out forward, hips on the seat
    sits = {}
    for c in tl["cues"]:
        if c["name"] == "sit" and c["t"] <= t:
            sits[c["who"]] = c
    for who, c in sits.items():
        root = bpy.data.objects.get(who)
        if c.get("on") and root is not None:
            h = story["cast"][who].get("height", 1.0)
            root.location.z += c.get("z", 0.67) - 2 * S * h
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    # the ceiling tile (0 in, 0.15 an inch up, 1 out and gone) and the dust
    tu = sample("tile", tl, t, {"u": 0.0})["u"]
    tile = W["tile"]
    W["rim"].hide_render = not (0.02 < tu < 0.999)
    if tu >= 0.999:
        tile.hide_render = True
    else:
        tile.hide_render = False
        base = W["tile_base"]
        if tu <= 0.15:
            k = tu / 0.15                    # the near edge lifts: a dark gap above it, a rim of window light on the edge
            tile.location = (base.x, base.y, base.z + 0.138 * k)
            tile.rotation_euler = (-0.36 * k, 0, 0)
        else:
            k = (tu - 0.15) / 0.85
            tile.location = (base.x + 0.1 * k, base.y, base.z + 0.09 + k * 0.9)
            tile.rotation_euler = (0.5 * k, 0.3 * k, 0.4 * k)
    for ob, dirv in W["dust"]:
        du = 0.0
        for c in tl["cues"]:
            if c["name"] == "dust" and c["t"] <= t < c["t"] + c.get("dur", 1.0):
                du = (t - c["t"]) / c.get("dur", 1.0)
        if du <= 0.0:
            ob.hide_render = True
        else:
            ob.hide_render = False
            ob.location = (G.G_POS[0] + dirv[0] * 0.9 * du, G.G_POS[1] + dirv[1] * 0.9 * du, CEIL - 0.1 + dirv[2] * du)
            k = max(0.05, math.sin(math.pi * min(1.0, du)) * 1.0)
            ob.scale = (k, k, k)
    # doors: back door (0 shut, 1 open), front door
    bd = sample("bdoor", tl, t, {"u": 0.0})["u"]
    W["bdoor"].rotation_euler = (0, 0, -bd * 100 * D2R)
    fd = sample("fdoor", tl, t, {"u": 0.0})["u"]
    W["fdoor"].rotation_euler = (0, 0, fd * 95 * D2R)
    # the hat: on its shelf, or in Grandpa's hand
    hu = sample("hat", tl, t, {"u": 0.0})["u"]
    sh = W["hat_shelf"]
    tgt = Vector((3.55, 0.55, 1.75 + (G.CRATE_H - 0.4)))
    W["hat"].location = sh.lerp(tgt, ss(hu))
    # held things
    for nm in ("key", "tomato", "faucet", "hinge"):
        v = sample("item", tl, t, {nm: 1.0 if nm in ("tomato", "faucet", "hinge") else 0.0}).get(nm, 0.0)
        ob = W.get(nm)
        if ob is not None:
            hide(ob, v < 0.5)
    # the new pencil mark with its tiny door
    nm_ = sample("newmark", tl, t, {"v": 0.0})["v"]
    hide(W["newmark"], nm_ < 0.5)
    return gains
