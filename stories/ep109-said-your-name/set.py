"""ep109 "said your name": a bright Saturday. Four places a long way apart: our kitchen with the old radio, a pastel
main street (bakery, fruit stand, cafe, bus shelter, park bench, faces at the upper windows), the cafe's window table,
and Mrs. Odell's porch.

The rule marker is a cream tag on the camera, top-left in every frame: a radio-dial glyph lit red, a day clock in
seven-segment numerals, and a ring with a person glyph inside it (a second glyph joins when Dev kneels).

Everything the story moves is a cue in story.json (see animate): the clock, the ring's second person, the bus, the
neighbor's curtains, the oranges, who is kneeling or sitting, what is shown (cup, phone, bag, plates, candle stub).
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


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


# ------------------------------------------------------------------------------------------ build helpers
def flowers(kit, nm, x, y, z, dirn, wide=1.6):
    box = kit.plastic("#ff9ab0", 0.7, spec=0.1)
    kit.box(f"{nm}.fb", (wide, 0.32, 0.3), (x, y + dirn * 0.2, z), kit.plastic("#8fd9a8", 0.7, spec=0.1))
    cols = ["#ff7a9a", "#fff1d6", "#ffd23a", "#ffffff", "#ff9a1f"]
    n = int(wide / 0.28)
    for k in range(n):
        kit.sphere(f"{nm}.fl{k}", 0.1, (x - wide / 2 + 0.2 + k * 0.27, y + dirn * 0.2, z + 0.2),
                   kit.plastic(cols[k % 5], 0.6, spec=0.1), seg=8)
    return box


def storey(kit, nm, cx, w, fy, inn, col, roofc, ground=True, wide_curtain=None):
    """A shop front 8 wide: wall slab 0.4 thick, a ground storey, and an upper storey with two real window holes.
    inn is +1 when the building lies toward +y (the face looks -y), -1 for a south row. A character at z = FACE_Z
    stands in the hole, so its face is at the window."""
    wall = kit.grime(col, 0.93, 2.0, f"wall{col}", 0.9)
    yc = fy + inn * 0.2
    x0, x1 = cx - w / 2, cx + w / 2
    z0, z1 = G.WIN_Z
    if ground:
        kit.box(f"{nm}.g", (w, 0.4, G.SW), (cx, yc, G.SW / 2), wall)
    kit.box(f"{nm}.ub", (w, 0.4, z0 - G.SW), (cx, yc, (G.SW + z0) / 2), wall)
    kit.box(f"{nm}.ut", (w, 0.4, G.UP - z1), (cx, yc, (z1 + G.UP) / 2), wall)
    xs = G.win_xs(cx)
    hw = 0.75
    edges = [x0] + sum([[x - hw, x + hw] for x in xs], []) + [x1]
    for k in range(0, len(edges), 2):
        a, b = edges[k], edges[k + 1]
        kit.box(f"{nm}.p{k}", (b - a, 0.4, z1 - z0), ((a + b) / 2, yc, (z0 + z1) / 2), wall)
    kit.box(f"{nm}.roof", (w + 0.5, 6.2, 0.4), (cx, fy + inn * 3.0, G.UP + 0.2), kit.plastic(roofc, 0.7, spec=0.1))
    inside = kit.plastic("#fff0d0", 0.9, spec=0.02)
    cream = kit.plastic("#fff4e0", 0.7, spec=0.1)
    for j, x in enumerate(xs):
        kit.box(f"{nm}.back{j}", (1.9, 0.1, 2.0), (x, fy + inn * 0.78, (z0 + z1) / 2), inside)
        for sgn in (-1, 1):
            kit.box(f"{nm}.fr{j}{sgn}", (0.1, 0.12, z1 - z0 + 0.2), (x + sgn * (hw + 0.05), fy - inn * 0.02, (z0 + z1) / 2), cream)
        kit.box(f"{nm}.frt{j}", (1.7, 0.12, 0.1), (x, fy - inn * 0.02, z1 + 0.05), cream)
        kit.box(f"{nm}.frb{j}", (1.7, 0.12, 0.1), (x, fy - inn * 0.02, z0 - 0.05), cream)
        flowers(kit, f"{nm}.w{j}", x, fy, z0 - 0.12, -inn)
        cw = 0.17
        for sgn in (-1, 1):
            w_ = cw
            if wide_curtain is not None and abs(x - wide_curtain) < 0.1 and sgn == -1:
                w_ = 0.8
            cc = "#c9b8ff" if (j + (1 if sgn > 0 else 0)) % 2 else "#ffb3d1"
            kit.box(f"{nm}.cur{j}{sgn}", (w_, 0.05, z1 - z0 - 0.05),
                    (x + sgn * (hw - w_ / 2), fy + inn * 0.09, (z0 + z1) / 2), kit.plastic(cc, 0.9, spec=0.02))


def awning(kit, nm, cx, ca, cb, n=14, wd=0.57, y=4.25, z=3.2, rx=-22):
    sa, sb = kit.plastic(ca, 0.6), kit.plastic(cb, 0.6)
    for i in range(n):
        kit.box(f"{nm}.s{i}", (wd, 1.9, 0.07), (cx - n * wd / 2 + wd / 2 + i * wd, y, z), sa if i % 2 else sb,
                rot=(rx * D2R, 0, 0))


def room(kit, nm, x0, x1, y0, y1, h, floor, wallc):
    kit.plane(f"{nm}.floor", (x1 - x0, y1 - y0), ((x0 + x1) / 2, (y0 + y1) / 2, 0.03), floor)
    wm = kit.plastic(wallc, 0.9, spec=0.02)
    kit.box(f"{nm}.back", (x1 - x0, 0.2, h), ((x0 + x1) / 2, y1, h / 2), wm)
    for sx, x in ((0, x0), (1, x1)):
        kit.box(f"{nm}.side{sx}", (0.2, y1 - y0, h), (x, (y0 + y1) / 2, h / 2), wm)
    kit.box(f"{nm}.ceil", (x1 - x0, y1 - y0, 0.2), ((x0 + x1) / 2, (y0 + y1) / 2, h + 0.1), kit.plastic("#fff6e6", 0.9, spec=0.02))


def lamp(kit, nm, x, y):
    kit.cyl(f"{nm}.pole", 0.06, 3.6, (x, y, 1.8), kit.plastic("#5a4a7a", 0.5), n=8)
    kit.sphere(f"{nm}.bulb", 0.2, (x, y, 3.7), kit.plastic("#fff6d0", 0.4, spec=0.6), seg=10)


def tree(kit, nm, x, y, h=6.0, tint="#c6f0b8"):
    try:
        kit.prop("commontree_1", (x, y, 0), height=h, tint=tint)
    except Exception:
        kit.cyl(f"{nm}.trunk", 0.3, h * 0.45, (x, y, h * 0.22), kit.plastic("#8a5a3a", 0.8), n=8)
        kit.sphere(f"{nm}.crown", h * 0.28, (x, y, h * 0.68), kit.plastic("#6fd06a", 0.8), seg=10)


def glyph_board(kit, nm, x, y, z, kind, col):
    """A shop board with a glyph and no letters."""
    kit.box(f"{nm}.bd", (2.4, 0.12, 0.8), (x, y, z), kit.plastic("#fff1d6", 0.6))
    m = kit.plastic(col, 0.5)
    if kind == "bun":
        kit.sphere(f"{nm}.g", 0.28, (x, y - 0.1, z), m, seg=12)
    elif kind == "cup":
        kit.cyl(f"{nm}.g", 0.2, 0.34, (x - 0.05, y - 0.1, z), m, rot=(math.pi / 2, 0, 0), n=12)
        kit.box(f"{nm}.h", (0.16, 0.06, 0.2), (x + 0.22, y - 0.1, z), m)
    elif kind == "orange":
        kit.sphere(f"{nm}.g", 0.26, (x, y - 0.1, z), m, seg=12)
    else:
        kit.box(f"{nm}.g", (0.5, 0.06, 0.5), (x, y - 0.1, z), m, rot=(0, 45 * D2R, 0))


def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    P = kit.plastic
    # ------------------------------------------------------------------ lights
    az, el = 165 * D2R, 50 * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    sun = kit.light("sun", "SUN", tuple(d * 60), 1.0, "#fff2dc", size=0.06)
    sun.data.angle = 0.06
    kit.aim(sun, (0, 0, 0))
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#d8ecff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    front = kit.light("front", "SUN", (-10, -30, 20), 1.0, "#fff0e0", shadow=False)
    front.data.angle = 0.4
    kit.aim(front, (0, 0, 0))
    kx, ky = G.K
    kit.light("kit", "POINT", (kx - 1.0, ky - 1.0, 3.0), 320.0, "#fff0d8", size=0.6, shadow=False)
    kit.light("kit2", "POINT", (kx - 1.5, ky + 3.6, 2.4), 160.0, "#fff0d8", size=0.5, shadow=False)
    kit.light("bak", "POINT", (G.BAKERY, 7.0, 3.0), 300.0, "#fff0d0", size=0.6, shadow=False)
    kit.light("caf", "POINT", (G.CAFE, 8.0, 3.0), 340.0, "#fff0d0", size=0.6, shadow=False)
    kit.light("caf2", "POINT", (G.TABLE[0], G.TABLE[1] + 1.4, 2.2), 160.0, "#fff4e0", size=0.4, shadow=False)
    kit.light("odl", "POINT", (G.OD, 7.5, 2.4), 200.0, "#fff0d0", size=0.5, shadow=False)
    kit.light("odwin", "POINT", (G.OD, -3.2, 6.2), 1500.0, "#fff2dc", size=1.0, shadow=False)
    kit.light("nbl", "POINT", (G.NB_X + 4.0, G.K[1], 2.6), 420.0, "#fff2dc", size=0.6, shadow=False)
    W["drvl"] = kit.light("drvl", "POINT", (0, 0, 3), 260.0, "#fff4e0", size=0.5, shadow=False)
    kit.light("benchkey", "POINT", (G.BENCH[0] - 0.4, -4.6, 2.8), 520.0, "#fff0d8", size=0.6, shadow=False)
    kit.light("woman", "POINT", (G.BENCH[0] - 0.9, -4.2, 2.6), 300.0, "#fff0d8", size=0.6, shadow=False)

    ground = kit.grime("#a8ec9c", 0.92, 1.2, "ground", 0.95)
    lawn = kit.grime("#9be58f", 0.9, 1.4, "lawn", 0.95)
    road = P("#a9a6d4", 0.9, spec=0.05)
    walk = P("#fbe6cc", 0.85, spec=0.05)
    cream = P("#fff1d6", 0.7, spec=0.1)
    wood = P("#c78a58", 0.7, spec=0.1)

    kit.plane("ground", (900, 600), (60, 0, 0.0), ground)

    # ------------------------------------------------------------------ the main street
    kit.plane("road", (150, 6.0), (68, -1.2, 0.02), road)
    kit.plane("walkN", (150, 3.2), (68, 3.4, 0.03), walk)
    kit.plane("walkS", (150, 2.6), (68, -5.5, 0.03), walk)
    kit.plane("lawnS", (150, 8.0), (68, -10.8, 0.02), lawn)
    for i in range(36):
        kit.box(f"dash{i}", (1.6, 0.14, 0.012), (22 + i * 3.0, -1.2, 0.035), P("#ffd23a", 0.6))
    cols = ["#bdf0d8", "#ffd6b8", "#ffe7a6", "#d8c9ff", "#ffc9d8", "#c4ecff"]
    roofs = ["#ff8a70", "#8f7cff", "#ffb347", "#4fc4b8", "#ff7aa8", "#6cc4ff"]
    for i, cx in enumerate(G.SHOP_X):
        ground_floor = cx not in (G.BAKERY, G.CAFE)
        storey(kit, f"n{i}", cx, 8.0, G.NY, +1, cols[i % 6], roofs[i % 6], ground=ground_floor,
               wide_curtain=None)
        if ground_floor and cx != 60.0 or cx == 60.0:
            if ground_floor:
                gl = P("#8fd3ff", 0.2, spec=0.8)
                kit.box(f"n{i}.door", (1.1, 0.1, 2.4), (cx + 2.4, 4.93, 1.2), P(roofs[(i + 2) % 6], 0.5, spec=0.3))
                kit.box(f"n{i}.win", (3.0, 0.1, 1.5), (cx - 1.4, 4.93, 1.6), gl)
                kit.box(f"n{i}.wf", (3.3, 0.08, 1.8), (cx - 1.4, 4.96, 1.6), cream)
                glyph_board(kit, f"n{i}.bd", cx - 1.0, 4.9, 2.95, ["star", "orange", "cup", "bun"][i % 4], roofs[(i + 3) % 6])
    # the bakery front: window to the counter, a door, a striped awning
    bx = G.BAKERY
    wallb = kit.grime("#ffd6b8", 0.93, 2.0, "wall#ffd6b8", 0.9)
    kit.box("bk.pl", (1.5, 0.4, G.SW), (bx - 3.25, 5.2, G.SW / 2), wallb)
    kit.box("bk.sill", (4.7, 0.4, 0.9), (bx - 0.15, 5.2, 0.45), wallb)
    kit.box("bk.lint", (4.7, 0.4, 0.5), (bx - 0.15, 5.2, G.SW - 0.25), wallb)
    kit.box("bk.pr", (1.8, 0.4, G.SW), (bx + 3.1, 5.2, G.SW / 2), wallb)
    kit.box("bk.door", (1.0, 0.1, 2.4), (bx + 3.1, 4.95, 1.2), P("#ff8a70", 0.5, spec=0.3))
    room(kit, "bk", bx - 4.0, bx + 4.0, 5.0, 11.0, G.SW, P("#e8b27a", 0.8, spec=0.1), "#fff0d8")
    awning(kit, "bkaw", bx, "#4fc4b8", "#fff1d6", n=14)
    glyph_board(kit, "bkbd", bx, 4.88, 3.3, "bun", "#ff9a1f")
    kit.box("bk.counter", (6.4, 0.9, 1.0), (bx, 7.3, 0.5), P("#ff8a70", 0.5, spec=0.2))
    kit.box("bk.ctop", (6.6, 1.1, 0.08), (bx, 7.3, 1.04), cream, bevel=0.02)
    bun = P("#e0a05a", 0.6, spec=0.15)
    for r in range(2):
        kit.box(f"bk.tray{r}", (5.6, 0.34, 0.03), (bx, 7.0 + r * 0.45, 1.1), P("#fffaf0", 0.6))
        for k in range(14):
            kit.sphere(f"bk.bun{r}_{k}", 0.13, (bx - 2.6 + k * 0.4, 7.0 + r * 0.45, 1.24), bun, seg=8)
    for z in (1.5, 2.2, 2.9):
        kit.box(f"bk.shelf{z}", (7.0, 0.5, 0.08), (bx, 10.6, z), wood)
        for k in range(12):
            kit.box(f"bk.loaf{z}_{k}", (0.45, 0.28, 0.26), (bx - 3.0 + k * 0.55, 10.55, z + 0.17), bun, bevel=0.08)
    # the cafe front: a big window onto the window table, a door, a striped awning
    cx = G.CAFE
    wallc = kit.grime("#ffc9d8", 0.93, 2.0, "wall#ffc9d8", 0.9)
    kit.box("cf.pl", (0.9, 0.4, G.SW), (cx - 3.55, 5.2, G.SW / 2), wallc)
    kit.box("cf.sill", (4.8, 0.4, 0.9), (cx - 1.1, 5.2, 0.45), wallc)
    kit.box("cf.lint", (4.8, 0.4, 0.5), (cx - 1.1, 5.2, G.SW - 0.25), wallc)
    kit.box("cf.pr", (2.3, 0.4, G.SW), (cx + 2.85, 5.2, G.SW / 2), wallc)
    kit.box("cf.door", (1.1, 0.1, 2.4), (cx + 2.9, 4.95, 1.2), P("#8f7cff", 0.5, spec=0.3))
    for sg in (-1, 1):
        kit.box(f"cf.fr{sg}", (0.08, 0.12, 2.6), (cx - 1.1 + sg * 2.45, 4.97, 2.2), cream)
    kit.box("cf.frt", (4.9, 0.12, 0.08), (cx - 1.1, 4.97, 3.0), cream)
    kit.box("cf.frb", (4.9, 0.12, 0.08), (cx - 1.1, 4.97, 0.9), cream)
    room(kit, "cf", cx - 4.0, cx + 4.0, 5.0, 11.0, G.SW, P("#ffe7c4", 0.8, spec=0.1), "#e9fff4")
    awning(kit, "cfaw", cx, "#ff7a7a", "#fff1d6", n=14)
    glyph_board(kit, "cfbd", cx, 4.88, 3.3, "cup", "#ff7a7a")
    tx, ty = G.TABLE
    kit.cyl("cf.tbl", 0.5, 0.06, (tx, ty, 0.82), P("#fff1d6", 0.5, spec=0.2), n=20)
    kit.cyl("cf.tleg", 0.07, 0.8, (tx, ty, 0.4), P("#5a4a7a", 0.5), n=10)
    kit.cyl("cf.tbase", 0.3, 0.04, (tx, ty, 0.04), P("#5a4a7a", 0.5), n=14)
    for nm_, (sx_, sy_) in (("cA", G.SEAT_ME), ("cB", G.SEAT_DEV)):
        kit.box(f"cf.{nm_}.seat", (0.5, 0.5, 0.06), (sx_, sy_, 0.52), P("#8f7cff", 0.6))
        kit.box(f"cf.{nm_}.leg", (0.08, 0.08, 0.5), (sx_, sy_, 0.25), P("#5a4a7a", 0.5))
    for k in range(3):
        kit.box(f"cf.tab{k}", (0.8, 0.8, 0.05), (cx + 1.4 + (k % 2) * 0.1, 8.6 + k * 1.0, 0.75), cream)
        kit.cyl(f"cf.tleg{k}", 0.06, 0.74, (cx + 1.4 + (k % 2) * 0.1, 8.6 + k * 1.0, 0.37), P("#5a4a7a", 0.5), n=8)
    kit.box("cf.bar", (4.2, 0.9, 1.1), (cx - 1.5, 10.2, 0.55), P("#ff7a7a", 0.5, spec=0.2))
    # things that appear and disappear at the cafe table
    W["stub"] = kit.cyl("cf.stub", 0.03, 0.05, (tx + 0.1, ty - 0.05, 0.88), P("#ffd23a", 0.6), n=8)
    W["stub2"] = kit.sphere("cf.stubflame", 0.022, (tx + 0.1, ty - 0.05, 0.925), kit.emit("#ffcf6e", 4.0), seg=6)
    W["cups"] = []
    for k, (ox_, oy_) in enumerate(((-0.2, 0.0), (0.2, 0.0))):
        W["cups"].append(kit.cyl(f"cf.cup{k}", 0.07, 0.09, (tx + ox_, ty + oy_, 0.89), P("#ffffff", 0.4, spec=0.3), n=12))
        W["cups"].append(kit.cyl(f"cf.coffee{k}", 0.055, 0.01, (tx + ox_, ty + oy_, 0.935), P("#6b3a22", 0.4), n=12))
    W["plates"] = []
    W["plates"].append(kit.cyl("cf.plateA", 0.17, 0.02, (tx - 0.2, ty, 0.865), P("#ffffff", 0.3, spec=0.5), n=16))
    pdev = kit.cyl("cf.plateB", 0.17, 0.02, (tx + 0.2, ty, 0.865), P("#ffffff", 0.3, spec=0.5), n=16)
    kit.box("cf.cake", (0.17, 0.12, 0.1), (0, 0, 0.06), P("#7a3b24", 0.6), pdev, bevel=0.02)
    kit.box("cf.icing", (0.17, 0.12, 0.025), (0, 0, 0.12), P("#e8507f", 0.6), pdev, bevel=0.01)
    W["plates"].append(pdev)
    W["plateB"] = pdev
    # fruit stand
    sx0, sy0 = G.STALL
    kit.box("fs.table", (3.0, 1.0, 0.9), (sx0, sy0, 0.45), P("#8fd9a8", 0.6, spec=0.1))
    for k in range(4):
        kit.cyl(f"fs.pole{k}", 0.04, 2.4, (sx0 + (-1.5 if k % 2 else 1.5), sy0 + (-0.55 if k < 2 else 0.55), 1.2), cream, n=8)
    awning(kit, "fsaw", sx0, "#ff9a1f", "#fff1d6", n=6, wd=0.5, y=sy0 - 0.1, z=2.4, rx=-8)
    om = P("#ff9a1f", 0.45, spec=0.3)
    for r in range(3):
        for c in range(7 - r):
            for rr in range(2):
                kit.sphere(f"fs.o{r}_{c}_{rr}", 0.11, (sx0 - 1.2 + c * 0.25 + r * 0.12, sy0 - 0.2 + rr * 0.35, 0.99 + r * 0.17), om, seg=8)
    glyph_board(kit, "fsbd", sx0, sy0 + 0.6, 2.0, "orange", "#ff9a1f")
    # lamps, trees and the south side
    for x in (34, 58, 82, 106):
        lamp(kit, f"lp{x}", x, 1.9)
    for x in (42, 70, 98):
        tree(kit, f"st{x}", x, -6.6, 4.8)
    for x, hgt in ((44, 6.5), (62, 7.5), (104, 6.5)):
        tree(kit, f"pk{x}", x, -12.5, hgt)
    for i in range(12):
        hx = 14 + i * 9.5
        kit.box(f"so{i}", (8.0, 6.0, 5.5 + (i % 3)), (hx, -22.0, 3.0), kit.grime(cols[i % 6], 0.93, 2.0, f"sw{i % 6}", 0.9))
        kit.box(f"so{i}.r", (8.5, 6.5, 0.4), (hx, -22.0, 6.0 + (i % 3)), P(roofs[i % 6], 0.7, spec=0.1))
    # the bus shelter
    shx, shy = G.SHELTER
    gl = P("#bfe6ff", 0.15, spec=0.9)
    W["shroof"] = kit.box("sh.roof", (3.4, 1.8, 0.12), (shx, shy, 2.5), P("#ff8a70", 0.6))
    kit.box("sh.back", (3.2, 0.06, 2.2), (shx, shy - 0.8, 1.35), gl)
    for sg in (-1, 1):
        kit.box(f"sh.post{sg}", (0.1, 0.1, 2.5), (shx + sg * 1.6, shy + 0.8, 1.25), P("#5a4a7a", 0.5))
        kit.box(f"sh.side{sg}", (0.06, 1.4, 1.6), (shx + sg * 1.6, shy - 0.1, 1.5), gl)
    kit.box("sh.bench", (2.0, 0.45, 0.1), (shx, shy - 0.45, 0.5), wood)
    kit.box("sh.bleg", (1.8, 0.35, 0.45), (shx, shy - 0.45, 0.25), P("#5a4a7a", 0.5))
    kit.cyl("sh.signpole", 0.05, 2.8, (shx - 2.4, shy + 0.8, 1.4), P("#5a4a7a", 0.5), n=8)
    kit.cyl("sh.sign", 0.3, 0.06, (shx - 2.4, shy + 0.72, 2.9), P("#6cc4ff", 0.4), rot=(math.pi / 2, 0, 0), n=16)
    kit.box("sh.glyph", (0.32, 0.04, 0.2), (shx - 2.4, shy + 0.68, 2.9), P("#ffffff", 0.4))
    # the park bench, facing the street, with a tree behind it
    bx_, by_ = G.BENCH
    kit.box("bench.seat", (3.4, 1.0, 0.14), (bx_, by_, 0.55), wood)
    kit.box("bench.back", (3.4, 0.14, 0.9), (bx_, by_ - 0.5, 1.05), wood)
    for sg in (-1, 1):
        kit.box(f"bench.leg{sg}", (0.14, 0.9, 0.55), (bx_ + sg * 1.5, by_, 0.27), P("#5a4a7a", 0.5))
        kit.box(f"bench.arm{sg}", (0.24, 1.0, 0.12), (bx_ + sg * 1.74, by_, 0.85), P("#5a4a7a", 0.5))
    for k in range(10):
        kit.sphere(f"shrub{k}", 0.5 + 0.1 * (k % 3), (bx_ - 5 + k * 1.1, by_ - 3.0, 0.4), P(["#6fd06a", "#8be07a", "#58c466"][k % 3], 0.8), seg=8)
    W["bag2"] = []
    bg = kit.empty("bag2", (bx_ - 1.0, by_, 0.62))
    kit.box("bag2.body", (0.34, 0.24, 0.42), (0, 0, 0.21), P("#d9a36a", 0.9, spec=0.02), bg, bevel=0.02)
    kit.box("bag2.tape", (0.2, 0.26, 0.05), (0, 0, 0.06), P("#fff2a8", 0.5), bg)
    W["bag2obj"] = bg

    # ------------------------------------------------------------------ the bus (front toward +x)
    bus = kit.empty("bus", (0, G.BUS_Y, 0))
    W["bus"] = bus
    bc = P("#ff8a70", 0.5, spec=0.3)
    kit.box("bus.low", (9.0, 2.6, 1.3), (0, 0, 1.15), bc, bus, bevel=0.1)
    kit.box("bus.stripe", (9.02, 2.62, 0.2), (0, 0, 1.55), cream, bus)
    kit.box("bus.roof", (9.0, 2.6, 0.2), (0, 0, 3.0), bc, bus, bevel=0.08)
    kit.box("bus.floor", (8.8, 2.4, 0.1), (0, 0, 1.18), P("#e8d2b0", 0.8), bus)
    for sg in (-1, 1):
        for k in range(7):
            kit.box(f"bus.post{sg}{k}", (0.12, 0.12, 1.2), (-4.2 + k * 1.4, sg * 1.25, 2.3), bc, bus)
        kit.box(f"bus.fpost{sg}", (0.14, 0.14, 1.2), (4.4, sg * 1.2, 2.3), bc, bus)
    for k in range(3):
        for sg in (-1, 1):
            kit.box(f"bus.seat{k}{sg}", (0.6, 0.8, 0.5), (-3.2 + k * 1.6, sg * 0.8, 1.5), P("#8f7cff", 0.7), bus)
    kit.box("bus.seatd", (0.5, 0.5, 0.4), (3.0, 0.7, 1.45), P("#8f7cff", 0.7), bus)
    kit.box("bus.dash", (0.4, 2.2, 0.5), (4.2, 0, 1.5), P("#5a4a7a", 0.6), bus)
    kit.cyl("bus.wheel", 0.2, 0.05, (3.95, 0.65, 1.95), P("#5a4a7a", 0.5), bus, rot=(0, 0.6, 0), n=12)
    for sx_ in (-2.8, 2.8):
        for sg in (-1, 1):
            kit.cyl(f"bus.tire{sx_}{sg}", 0.55, 0.35, (sx_, sg * 1.2, 0.55), P("#3a3350", 0.8, spec=0.1), bus,
                    rot=(math.pi / 2, 0, 0), n=16)
            kit.cyl(f"bus.hub{sx_}{sg}", 0.28, 0.37, (sx_, sg * 1.2, 0.55), P("#fff1d6", 0.5), bus, rot=(math.pi / 2, 0, 0), n=12)
    for sg in (-1, 1):
        kit.box(f"bus.lamp{sg}", (0.06, 0.4, 0.3), (4.52, sg * 0.9, 1.0), kit.emit("#fff2b0", 2.0), bus)

    # ------------------------------------------------------------------ our kitchen
    wallk = P("#ffd6b8", 0.9, spec=0.02)
    wallm = P("#bdf0d8", 0.9, spec=0.02)
    flo = kit.planks("#e6b98a", "#d9a674", 1.2)
    kit.plane("k.floor", (12, 9), (kx, ky, 0.03), flo)
    kit.box("k.back", (12, 0.3, 3.4), (kx, ky + 4.65, 1.7), wallk)
    kit.box("k.right", (0.3, 9.6, 3.4), (kx + 6.15, ky, 1.7), wallm)
    # the left wall, with the window
    lx = kx - 6.0
    kit.box("k.l_lo", (0.3, 9.6, 1.0), (lx, ky, 0.5), wallm)
    kit.box("k.l_hi", (0.3, 9.6, 0.9), (lx, ky, 2.95), wallm)
    kit.box("k.l_a", (0.3, 3.8, 1.5), (lx, ky - 2.9 - 0.0, 1.75), wallm)
    kit.box("k.l_b", (0.3, 3.8, 1.5), (lx, ky + 2.9 + 0.0, 1.75), wallm)
    for yy in (-1.0, 1.0):
        kit.box(f"k.wf{yy}", (0.34, 0.1, 1.6), (lx, ky + yy, 1.75), cream)
    kit.box("k.wft", (0.34, 2.1, 0.1), (lx, ky, 2.5), cream)
    kit.box("k.wfb", (0.4, 2.2, 0.1), (lx + 0.05, ky, 1.0), cream)
    # the island and the radio
    ix, iy = kx - 1.2, 2.2
    kit.box("k.island", (5.4, 1.0, 0.9), (ix, iy, 0.45), P("#ffd23a", 0.5, spec=0.2), bevel=0.03)
    kit.box("k.itop", (5.6, 1.2, 0.06), (ix, iy, 0.93), cream, bevel=0.02)
    for k in range(5):
        kit.box(f"k.idoor{k}", (0.9, 0.03, 0.7), (ix - 2.1 + k * 1.05, iy - 0.51, 0.45), P("#ffe27a", 0.5))
    rz = G.COUNTER_Z + 0.03
    stone = kit.grime("#e8dfce", 0.88, 5.0, "oldstone", 0.95)
    rx_, ry_ = G.RAD
    rx_ = ix
    kit.box("radio.base", (1.14, 0.62, 0.07), (rx_, ry_, rz + 0.035), stone, bevel=0.02)
    kit.box("radio.body", (1.0, 0.54, 0.44), (rx_, ry_, rz + 0.07 + 0.22), stone, bevel=0.05)
    fy_ = ry_ - 0.27 - 0.012
    zc_ = rz + 0.29
    kit.box("radio.panel", (0.94, 0.03, 0.38), (rx_, fy_, zc_), P("#ffb866", 0.6, spec=0.1), bevel=0.01)
    kit.box("radio.grille", (0.5, 0.03, 0.3), (rx_ - 0.2, fy_ - 0.02, zc_), P("#ffe9bf", 0.9, spec=0.02))
    for k in range(9):
        kit.box(f"radio.rib{k}", (0.015, 0.03, 0.28), (rx_ - 0.4 + k * 0.05, fy_ - 0.04, zc_), P("#c9894a", 0.9, spec=0.02))
    kit.cyl("radio.ring", 0.17, 0.03, (rx_ + 0.27, fy_ - 0.02, zc_), cream, rot=(math.pi / 2, 0, 0), n=24)
    W["dialm"] = kit.emit("#c80030", 0.65, "dialred")
    kit.cyl("radio.dial", 0.14, 0.03, (rx_ + 0.27, fy_ - 0.04, zc_), W["dialm"], rot=(math.pi / 2, 0, 0), n=24)
    for k in range(12):
        a = k * 30 * D2R
        kit.box(f"radio.tick{k}", (0.012, 0.03, 0.03), (rx_ + 0.27 + 0.155 * math.sin(a), fy_ - 0.05, zc_ + 0.155 * math.cos(a)),
                P("#3a2a4a", 0.6), rot=(0, -a, 0))
    kit.box("radio.needle", (0.014, 0.03, 0.12), (rx_ + 0.29, fy_ - 0.055, zc_ + 0.04), cream, rot=(0, -0.5, 0))
    # the fruit bowl, the clock, shelves
    kit.cyl("k.bowl", 0.3, 0.14, (ix + 2.1, iy, G.COUNTER_Z + 0.1), P("#8f7cff", 0.5, spec=0.3), n=16, r2=0.22)
    for k in range(4):
        kit.sphere(f"k.bo{k}", 0.1, (ix + 2.0 + 0.1 * (k % 2) * 1.5, iy - 0.08 + 0.12 * (k // 2), G.COUNTER_Z + 0.22), P("#ff9a1f", 0.45, spec=0.3), seg=8)
    for k in range(3):
        kit.box(f"k.up{k}", (1.6, 0.6, 1.0), (kx - 4.5 + k * 1.7, ky + 4.2, 2.4), P("#ffe27a", 0.5))
    kit.box("k.cnt", (5.0, 0.9, 0.9), (kx - 3.2, ky + 4.0, 0.45), P("#ffd23a", 0.5, spec=0.2))
    kit.box("k.cnttop", (5.2, 1.0, 0.05), (kx - 3.2, ky + 4.0, 0.93), cream)
    # the fridge with the photos on it
    fx, fy = G.FRIDGE
    kit.box("fr.body", (1.3, 1.1, 2.3), (fx, fy + 0.55, 1.15), P("#e4fff4", 0.4, spec=0.4), bevel=0.04)
    kit.box("fr.seam", (1.28, 0.02, 0.03), (fx, fy - 0.005, 1.55), P("#9ad0b8", 0.6))
    kit.box("fr.handle", (0.05, 0.06, 0.5), (fx + 0.5, fy - 0.05, 1.9), P("#5a4a7a", 0.4))
    cards = [(-0.38, 1.95, 0.22, 0.3, "#ffd23a"), (0.22, 2.0, 0.26, 0.2, "#ff9ab0"), (-0.4, 0.95, 0.3, 0.22, "#8f7cff"),
             (0.3, 1.0, 0.2, 0.28, "#6cc4ff")]
    for k, (cx_, cz_, w_, h_, c_) in enumerate(cards):
        kit.box(f"fr.card{k}", (w_, 0.015, h_), (fx + cx_, fy - 0.013, cz_), P(c_, 0.7))
    px_, pz_ = fx - 0.05, 1.5          # our photo: Dev and me laughing
    py_ = fy - 0.016
    kit.box("ph.card", (0.62, 0.015, 0.48), (px_, py_, pz_), P("#ffffff", 0.7))
    kit.box("ph.bg", (0.54, 0.015, 0.4), (px_, py_ - 0.008, pz_), P("#8fd3ff", 0.8))
    for who, ox_, skin, hair, body, glasses in (("me", -0.12, "#dca97c", "#2a1a14", "#ffd23a", False),
                                                  ("dev", 0.13, "#e8b890", "#14110e", "#2aa6a0", True)):
        kit.box(f"ph.{who}.body", (0.2, 0.015, 0.14), (px_ + ox_, py_ - 0.018, pz_ - 0.15), P(body, 0.6))
        kit.box(f"ph.{who}.head", (0.17, 0.015, 0.17), (px_ + ox_, py_ - 0.026, pz_ - 0.02), P(skin, 0.6))
        kit.box(f"ph.{who}.hair", (0.18, 0.015, 0.06), (px_ + ox_, py_ - 0.034, pz_ + 0.075), P(hair, 0.6))
        for sg in (-1, 1):
            kit.box(f"ph.{who}.eye{sg}", (0.025, 0.015, 0.025), (px_ + ox_ + sg * 0.04, py_ - 0.04, pz_ - 0.005), P("#1c120c", 0.6))
        kit.box(f"ph.{who}.mouth", (0.09, 0.015, 0.045), (px_ + ox_, py_ - 0.04, pz_ - 0.065), P("#7a2a30", 0.6))
        if glasses:
            kit.box(f"ph.{who}.gl", (0.15, 0.015, 0.012), (px_ + ox_, py_ - 0.045, pz_ + 0.0), P("#1c120c", 0.6))
    # the neighbor's house across the street, its window and curtains
    nx = G.NB_X
    kit.plane("k.road", (10, 40), (kx - 9.5, ky, 0.02), road)
    wn = kit.grime("#c4ecff", 0.93, 2.0, "wall#c4ecff", 0.9)
    kit.box("nb.lo", (0.4, 16, 1.3), (nx, ky, 0.65), wn)
    kit.box("nb.hi", (0.4, 16, 2.4), (nx, ky, 3.7), wn)
    kit.box("nb.a", (0.4, 7.2, 1.4), (nx, ky - 4.4, 2.0), wn)
    kit.box("nb.b", (0.4, 7.2, 1.4), (nx, ky + 4.4, 2.0), wn)
    kit.box("nb.back", (0.1, 2.0, 1.6), (nx - 0.55, ky, 2.0), P("#fff0d0", 0.9, spec=0.02))
    kit.box("nb.roof", (6.0, 16.5, 0.4), (nx - 2.6, ky, 4.7), P("#8f7cff", 0.7))
    W["curt"] = []
    for sg in (-1, 1):
        o = kit.box(f"nb.cur{sg}", (0.05, 1.0, 1.1), (nx + 0.23, ky + sg * 0.5, 1.9), P("#ffb3d1", 0.9, spec=0.02))
        W["curt"].append((o, sg))
    for sg in (-1, 1):
        kit.box(f"nb.fr{sg}", (0.12, 0.1, 1.6), (nx + 0.22, ky + sg * 0.85, 2.0), cream)
    for sz in (1.25, 2.55):
        kit.box(f"nb.fh{sz}", (0.12, 1.8, 0.1), (nx + 0.22, ky, sz), cream)
    kit.plane("k.grassL", (80, 80), (kx - 50, ky, 0.0), ground)

    # ------------------------------------------------------------------ Mrs. Odell's porch
    ox = G.OD
    kit.plane("odroad", (60, 6.0), (ox, -1.2, 0.02), road)
    kit.plane("odwalk", (60, 3.2), (ox, 3.4, 0.03), walk)
    wo = kit.grime("#fff4e8", 0.95, 2.0, "wall#fff4e8", 0.9)
    kit.box("od.pl", (5.0, 0.4, 3.6), (ox - 4.1, 5.2, 1.8), wo)
    kit.box("od.pr", (5.0, 0.4, 3.6), (ox + 4.1, 5.2, 1.8), wo)
    kit.box("od.lint", (3.2, 0.4, 1.2), (ox, 5.2, 3.0), wo)
    kit.box("od.wall2", (13.2, 0.4, 3.4), (ox, 5.2, 5.3), wo)
    kit.box("od.roof", (14.0, 7.0, 0.4), (ox, 8.0, 7.2), P("#ff8aa8", 0.7))
    room(kit, "od", ox - 6.6, ox + 6.6, 5.0, 11.0, 3.6, P("#f2c9a0", 0.8, spec=0.1), "#fff0d8")
    kit.box("od.deck", (12.0, 3.4, 0.3), (ox, 3.3, 0.15), P("#fffaf0", 0.6, spec=0.1), bevel=0.02)
    for i in range(3):
        kit.box(f"od.step{i}", (3.0, 0.5, 0.1 * (i + 1)), (ox, 1.35 - i * 0.0 - 0.0, 0.05 * (i + 1)), P("#fffaf0", 0.6))
    for k in range(5):
        px = ox - 5.6 + k * 1.4 if k < 3 else ox + 1.8 + (k - 3) * 3.3
        kit.box(f"od.post{k}", (0.2, 0.2, 3.1), (px, 1.8, 1.85), P("#fffaf0", 0.6))
    kit.box("od.beam", (12.2, 0.3, 0.25), (ox, 1.8, 3.5), P("#fffaf0", 0.6))
    for k in range(16):
        if -1.7 < (ox - 5.6 + k * 0.72) - ox < 4.8:
            continue
        kit.box(f"od.rail{k}", (0.07, 0.07, 0.7), (ox - 5.6 + k * 0.72, 1.8, 0.7), P("#fffaf0", 0.6))
    kit.box("od.railtop", (4.3, 0.1, 0.07), (ox - 3.55, 1.8, 1.08), P("#fffaf0", 0.6))
    kit.box("od.railtop2", (4.3, 0.1, 0.07), (ox + 3.55, 1.8, 1.08), P("#fffaf0", 0.6))
    # rocker and little table
    kit.box("od.rock.seat", (0.7, 0.7, 0.08), (ox - 3.6, 4.0, 0.7), P("#ffb3d1", 0.7))
    kit.box("od.rock.back", (0.7, 0.08, 0.8), (ox - 3.6, 4.35, 1.1), P("#ffb3d1", 0.7))
    kit.box("od.rock.base", (0.74, 0.8, 0.05), (ox - 3.6, 4.0, 0.36), wood)
    kit.cyl("od.tbl", 0.38, 0.05, (ox + 2.4, 3.6, 0.85), cream, n=18)
    kit.cyl("od.tleg", 0.05, 0.55, (ox + 2.4, 3.6, 0.57), P("#5a4a7a", 0.5), n=8)
    W["cups2"] = []
    for k, ddx in enumerate((-0.12, 0.12)):
        W["cups2"].append(kit.cyl(f"od.cup{k}", 0.065, 0.09, (ox + 2.4 + ddx, 3.6, 0.93), P("#ffffff", 0.4, spec=0.3), n=12))
        W["cups2"].append(kit.cyl(f"od.cof{k}", 0.05, 0.01, (ox + 2.4 + ddx, 3.6, 0.975), P("#6b3a22", 0.4), n=12))
    for k in range(6):
        kit.sphere(f"od.pot{k}", 0.3, (ox - 6.3 + k * 0.0, 2.2 + k * 0.3, 0.55), P(["#ff7aa8", "#ffd23a"][k % 2], 0.6), seg=8)
    # the houses across from the porch, with faces at their upper windows
    for i, hx in enumerate([ox - 20 + i2 * 8.0 for i2 in range(6)]):
        storey(kit, f"od{i}", hx, 8.0, -9.0, -1, cols[(i + 2) % 6], roofs[(i + 4) % 6], ground=True)
    W["odwin"] = [x for i in range(6) for x in G.win_xs(ox - 20 + i * 8.0)]

    build_tag(kit)
    return {}


# ------------------------------------------------------------------------------------------ the rule marker
SEGS = {"a": (0, 1, 1, 0), "b": (1, 0.5, 0, 1), "c": (1, -0.5, 0, 1), "d": (0, -1, 1, 0), "e": (-1, -0.5, 0, 1),
        "f": (-1, 0.5, 0, 1), "g": (0, 0, 1, 0)}
DIGITS = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd", 6: "afgedc", 7: "abc", 8: "abcdefg", 9: "abcdfg"}


def build_tag(kit):
    """A cream tag, 1.5 x 0.9 units, on the camera: the dial glyph (lit red) on the left, the day clock top right, and
    the ring with a person inside it bottom right."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    plate = kit.emit("#fff1d6", 0.6, "tagplate")
    edge = kit.emit("#6b3a22", 0.6, "tagedge")
    redm = kit.emit("#c00030", 0.6, "tagred")
    ink = kit.emit("#2a2250", 0.8, "taginkk")
    teal = kit.emit("#1f9a94", 0.9, "tagteal")
    p1m = kit.emit("#5a3ca0", 0.9, "tagp1")
    p2m = kit.emit("#e8741a", 0.95, "tagp2")

    def b(name, size, loc, mat):
        ob = kit.box(name, size, loc, mat, root)
        noshadow(ob)
        return ob

    def c(name, r, loc, mat, n=28):
        ob = kit.cyl(name, r, 0.004, loc, mat, root, n=n)
        noshadow(ob)
        return ob

    b("tag.edge", (1.56, 0.96, 0.004), (0, 0, 0.0), edge)
    b("tag.plate", (1.5, 0.9, 0.004), (0, 0, 0.004), plate)
    # the dial glyph
    dx = -0.47
    c("tag.dial.rim", 0.36, (dx, 0, 0.008), ink)
    c("tag.dial.face", 0.325, (dx, 0, 0.012), plate)
    c("tag.dial.red", 0.265, (dx, 0, 0.016), redm)
    for k in range(10):
        a = (-120 + k * 26.7) * D2R
        b(f"tag.dial.tick{k}", (0.03, 0.07, 0.004), (dx + 0.3 * math.sin(a), 0.3 * math.cos(a), 0.02), ink).rotation_euler = (0, 0, -a)
    nd = b("tag.dial.needle", (0.04, 0.3, 0.004), (dx + 0.07, 0.06, 0.024), plate)
    nd.rotation_euler = (0, 0, -0.5)
    c("tag.dial.hub", 0.05, (dx, 0, 0.028), ink, 14)
    # the clock: four seven-segment digits and a colon
    W["digits"] = []
    zc = 0.22
    dxs = [0.03, 0.20, 0.47, 0.64]
    for di, X in enumerate(dxs):
        segs = {}
        for k, (sx, sz, hz, vt) in SEGS.items():
            wdt, hgt = (0.10, 0.05) if hz else (0.05, 0.13)
            segs[k] = b(f"tag.d{di}{k}", (wdt, hgt, 0.004), (X + sx * 0.05, zc + sz * 0.17, 0.008), ink)
        W["digits"].append(segs)
    for sgn in (-1, 1):
        c(f"tag.colon{sgn}", 0.026, (0.335, zc + sgn * 0.08, 0.008), ink, 10)
    # the ring with the person glyph(s)
    rx, rz = 0.36, -0.2
    c("tag.ring.out", 0.215, (rx, rz, 0.008), teal)
    c("tag.ring.in", 0.16, (rx, rz, 0.012), plate)
    W["p1"] = kit.empty("tag.p1", (rx, rz, 0.016), root)
    kit.sphere("tag.p1.head", 0.05, (0, 0.055, 0.0), p1m, W["p1"], seg=10).scale = (1, 1, 0.1)
    b2 = kit.box("tag.p1.body", (0.12, 0.1, 0.004), (0, -0.045, 0.0), p1m, W["p1"])
    W["p2"] = kit.empty("tag.p2", (rx, rz, 0.02), root)
    kit.sphere("tag.p2.head", 0.05, (0, 0.055, 0.0), p2m, W["p2"], seg=10).scale = (1, 1, 0.1)
    kit.box("tag.p2.body", (0.12, 0.1, 0.004), (0, -0.045, 0.0), p2m, W["p2"])
    for ob in list(W["p1"].children) + list(W["p2"].children):
        noshadow(ob)


def _first_frame(kit, story):
    W["inited"] = True


def set_clock(m):
    h = int(m // 60) % 12 or 12
    mi = int(m % 60)
    vals = [1 if h >= 10 else None, h % 10, mi // 10, mi % 10]
    for di, v in enumerate(vals):
        for k, ob in W["digits"][di].items():
            ob.hide_render = (v is None) or (k not in DIGITS[v])


def vis(tl, t, name, default=False):
    on = default
    for c in tl["cues"]:
        if c["name"] != "vis" or c.get("obj") != name:
            continue
        if c["t"] > t:
            break
        on = bool(c.get("on", True))
    return on


def show(ob, on):
    ob.hide_render = not on
    for c in ob.children_recursive:
        c.hide_render = not on


def hand_world(who, sx, off=(0.0, 0.0, -1.6)):
    arm = bpy.data.objects.get(f"{who}.arm{sx}")
    if arm is None:
        return None
    return arm.matrix_world @ Vector(off)


def _get_prop(kit, name, maker):
    ob = W.get(name)
    if ob is None:
        ob = W[name] = maker()
    return ob


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    P = kit.plastic
    gains = {"sun": 3.3, "fill": 0.9, "front": 0.8}
    # the clock
    m = 7 * 60 + 2
    for c in tl["cues"]:
        if c["name"] == "clock" and c["t"] <= t:
            m = c["m"]
    set_clock(m)
    # the ring's second person
    pr = sample("pair", tl, t, {"n": 1.0})
    n2 = max(0.0, min(1.0, pr["n"] - 1.0))
    W["p1"].location.x = 0.36 - 0.06 * n2
    W["p2"].location.x = 0.36 + 0.06 * n2
    s2 = max(0.001, n2)
    W["p2"].scale = (s2, s2, s2)
    W["p2"].hide_render = n2 < 0.02
    for ch in W["p2"].children:
        ch.hide_render = n2 < 0.02
    s1 = 1.0 - 0.15 * n2
    W["p1"].scale = (s1, s1, s1)
    # the radio dial breathes slowly
    W["dialm"].node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.6 + 0.1 * math.sin(t * 2.2)
    # the bus
    bs = sample("bus", tl, t, {"x": -30.0})
    W["bus"].location = (bs["x"], G.BUS_Y, 0.0)
    W["drvl"].location = (bs["x"] + 3.0, G.BUS_Y + 3.0, 2.6)
    drv = bpy.data.objects.get("driver")
    if drv is not None:
        drv.location = (bs["x"] + 3.0, G.BUS_Y + 0.7, 1.18 + 0.45 - 0.68)
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"driver.leg{sx}")
            if leg:
                leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    # the neighbor's curtains
    cu = sample("curtain", tl, t, {"u": 0.0})
    for ob, sg in W["curt"]:
        wdt = 0.4 + 0.5 * cu["u"]
        ob.scale = (1, wdt, 1)
        ob.location = (G.NB_X + 0.23, G.K[1] + sg * (0.9 - wdt / 2), 1.9)
    # who sits and who kneels
    sits, kneels = {}, {}
    for c in tl["cues"]:
        if c["t"] > t:
            break
        if c["name"] == "sit":
            sits[c["who"]] = c
        elif c["name"] == "kneel":
            kneels[c["who"]] = c
    for who, c in sits.items():
        root = bpy.data.objects.get(who)
        if c.get("on") and root is not None and who != "driver":
            root.location.z += c.get("z", 0.5) - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    for who, c in kneels.items():
        root = bpy.data.objects.get(who)
        if c.get("on") and root is not None:
            root.location.z += 0.2 - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (math.pi / 2 * 0.95, 0, 0)
    bpy.context.view_layer.update()
    show(W["shroof"], not vis(tl, t, "shroof_off"))
    # table things
    show(W["stub"], vis(tl, t, "stub"))
    show(W["stub2"], vis(tl, t, "stub"))
    for ob in W["cups"]:
        show(ob, vis(tl, t, "cups"))
    on = vis(tl, t, "plates")
    for ob in W["plates"]:
        show(ob, on)
    cake_on = on and vis(tl, t, "cake")
    for ch in W["plateB"].children:
        ch.hide_render = not cake_on
    pl = sample("plate", tl, t, {"u": 0.0})
    tx, ty = G.TABLE
    W["plateB"].location = (tx + 0.2 - 0.4 * pl["u"], ty, 0.865)
    for ob in W["cups2"]:
        show(ob, vis(tl, t, "cups2"))
    show(W["bag2obj"], vis(tl, t, "bag2"))
    # things held in a hand
    cup = _get_prop(kit, "cup", lambda: _mk_cup(kit))
    on = vis(tl, t, "cup")
    show(cup, on)
    if on:
        p = hand_world("me", 1, (0.0, -0.05, -1.5))
        if p is not None:
            cup.location = (p.x, p.y, p.z + 0.17 + 0.07)
    cake = _get_prop(kit, "cupcake", lambda: _mk_cupcake(kit))
    on = vis(tl, t, "cupcake")
    show(cake, on)
    if on:
        p = hand_world("greenw", 1, (0.0, -0.05, -1.5))
        if p is not None:
            cake.location = (p.x, p.y, p.z + 0.17 + 0.05)
    phone = _get_prop(kit, "phone", lambda: _mk_phone(kit))
    on = vis(tl, t, "phone")
    show(phone, on)
    if on:
        p = hand_world("hoodie", 1, (0.0, -0.05, -1.5))
        if p is not None:
            phone.location = (p.x, p.y, p.z + 0.17 + 0.012)
    # the paper bag and the oranges
    bag = _get_prop(kit, "bag", lambda: _mk_bag(kit))
    oranges = _get_prop(kit, "oranges", lambda: _mk_oranges(kit))
    tear = [c["t"] for c in tl["cues"] if c["name"] == "tear"]
    T0 = tear[0] if tear else 1e9
    bag_on = vis(tl, t, "bag")
    show(bag, bag_on)
    if bag_on:
        if t < T0 + 0.25:
            p = hand_world("me", 1, (0.0, 0.0, -1.7))
            if p is not None:
                bag.location = (p.x + 0.1, p.y, p.z - 0.4)
                bag.rotation_euler = (0, 0, 0)
                bag.scale = (1, 1, 1)
        else:
            u = ss((t - T0 - 0.25) / 0.35)
            sx0, sy0 = G.SPOT[0] + 0.4, G.SPOT[1] - 0.05
            bag.location = (sx0 + 0.15 * u, sy0, 0.45 * (1 - u) + 0.14 * u)
            bag.rotation_euler = (0, 80 * D2R * u, 0)
            bag.scale = (1, 1, 1 - 0.35 * u)
    for ob in bag.children:
        if ob.name.startswith("bag.tear"):
            ob.hide_render = not (bag_on and t >= T0 + 0.15)
    for i, o in enumerate(oranges):
        if i < 3 and t < T0 + G.orange_release(i) and vis(tl, t, "bag") and t >= 0:
            p = hand_world("me", 1, (0.0, 0.0, -1.7))
            if p is not None and bag_on:
                o.location = (p.x + 0.1 + 0.07 * (i - 1), p.y + 0.02 * i, p.z - 0.4 + 0.46)
                show(o, True)
            else:
                show(o, False)
        elif t >= T0 + G.orange_release(i):
            x, y, z = G.orange_at(i, t - T0 - G.orange_release(i))
            held = [c for c in tl["cues"] if c["name"] == "pick" and c["t"] <= t]
            held = held if held and held[-1].get("on", True) else []
            if i == 0 and held:
                p = hand_world("dev", 1, (0.0, -0.05, -1.5))
                if p is not None:
                    x, y, z = p.x, p.y, p.z + 0.17 + G.ORANGE_R
            o.location = (x, y, z)
            show(o, True)
        else:
            show(o, False)
    # the rule marker sits top-left at a fixed angular size, whatever the lens
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
    h2 = 12.0 / lens
    w2 = h2 * 9.0 / 16.0
    s = 0.62 * w2
    tag = W["tag"]
    tag.scale = (s, s, s)
    tag.location = (-0.9 * w2 + 0.75 * s, 0.88 * h2 - 0.45 * s, -1.0)
    return gains


def _mk_cup(kit):
    P = kit.plastic
    r = kit.empty("cup", (0, 0, -9))
    kit.cyl("cup.body", 0.07, 0.12, (0, 0, 0), P("#ffffff", 0.35, spec=0.4), r, n=14)
    kit.cyl("cup.coffee", 0.058, 0.01, (0, 0, 0.062), P("#6b3a22", 0.4), r, n=14)
    kit.box("cup.handle", (0.05, 0.02, 0.06), (0.09, 0, 0.0), P("#ffffff", 0.35), r)
    return r


def _mk_cupcake(kit):
    P = kit.plastic
    r = kit.empty("cupcake", (0, 0, -9))
    kit.cyl("cupcake.cup", 0.055, 0.07, (0, 0, 0), P("#ffd23a", 0.5, spec=0.2), r, n=12, r2=0.04)
    kit.sphere("cupcake.icing", 0.06, (0, 0, 0.06), P("#ff9ab0", 0.5, spec=0.3), r, seg=10)
    kit.sphere("cupcake.cherry", 0.022, (0, 0, 0.12), P("#e8281a", 0.4, spec=0.5), r, seg=8)
    return r


def _mk_phone(kit):
    P = kit.plastic
    r = kit.empty("phone", (0, 0, -9))
    kit.box("phone.body", (0.09, 0.17, 0.012), (0, 0, 0), P("#2a2250", 0.3, spec=0.5), r, bevel=0.004)
    kit.box("phone.screen", (0.078, 0.15, 0.004), (0, 0, 0.007), P("#14102a", 0.2, spec=0.7), r)
    return r


def _mk_bag(kit):
    P = kit.plastic
    r = kit.empty("bag", (0, 0, -9))
    kit.box("bag.body", (0.34, 0.24, 0.42), (0, 0, 0.0), P("#d9a36a", 0.9, spec=0.02), r, bevel=0.02)
    kit.box("bag.fold", (0.34, 0.03, 0.1), (0, -0.125, 0.19), P("#c68a52", 0.9, spec=0.02), r)
    dark = P("#4a2a14", 0.9, spec=0.02)
    kit.box("bag.tear0", (0.2, 0.012, 0.07), (0, -0.126, -0.15), dark, r)
    kit.box("bag.tear1", (0.12, 0.012, 0.06), (-0.06, -0.126, -0.09), dark, r, rot=(0, 0.5, 0))
    kit.box("bag.tear2", (0.1, 0.012, 0.05), (0.07, -0.126, -0.1), dark, r, rot=(0, -0.6, 0))
    return r


def _mk_oranges(kit):
    om = kit.plastic("#ff9a1f", 0.45, spec=0.3)
    out = []
    for i in range(G.N_ORANGES):
        o = kit.sphere(f"orange{i}", G.ORANGE_R, (0, 0, -9), om, seg=12)
        o.hide_render = True
        out.append(o)
    return out
