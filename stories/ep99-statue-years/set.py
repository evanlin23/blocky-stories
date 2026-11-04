"""ep99 "statue years": a sunny hilltop town, a giant seated sandstone statue, and the rule meter: a carved sandstone
tag in the top-left corner of every frame (a candle glyph and a tally of the statue's wrinkles).

Everything the story moves is driven by cues in story.json (see animate): the look (sun, fill, sky: always eased,
or set on a cut), the statue (wrinkles, beard, head), the tally, the calendar page, the crack sliding off the stone,
Mom's gray hair and smile line, and the rising sun. The tag is a child of the camera.
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
Z0, ZB = G.Z0, G.ZB


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def _L(**kw):
    base = dict(sun=3.4, sun_col="#fff0d8", el=45.0, az=-25.0, fill=0.8, fill_col="#fff0e0", sky="#8fd3ff", sky_str=1.0,
                front=0.0, disc=0.0)
    base.update(kw)
    return base


LOOKS = {
    "day": _L(),
    # pre-dawn: lilac sky, the sun still down behind the statue, a warm front light so every face reads
    "dawn0": _L(sun=1.0, sun_col="#ffb88f", el=3.0, az=170.0, fill=1.1, fill_col="#d9c8ff", sky="#c9b4ff", sky_str=0.75,
                front=1.5),
    # sunrise: peach horizon, the sun up behind the statue
    "dawn1": _L(sun=2.4, sun_col="#ffd2a0", el=15.0, az=170.0, fill=1.1, fill_col="#ffd9c0", sky="#ffc7a1", sky_str=0.9,
                front=1.9, disc=1.0),
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


# ---------------------------------------------------------------------------------------------- build helpers
def house(kit, name, x, y, w, d, h, col, face=-1, roof="#c4624a", win=True, boxes=True):
    """A rose sandstone house; its windows face -y (face=-1) or +y."""
    wall = kit.grime(col, 0.9, 2.0, f"wall{col}", 0.9)
    kit.box(f"{name}.body", (w, d, h), (x, y, h / 2), wall)
    kit.box(f"{name}.roof", (w + 0.6, d + 0.6, 0.5), (x, y, h + 0.25), kit.plastic(roof, 0.7, spec=0.1))
    fy = y + face * (d / 2)
    glass = kit.plastic("#5f8fb8", 0.2, spec=0.8)
    yellow = kit.plastic("#ffd23f", 0.6, spec=0.1)
    leaf = kit.plastic("#5f9e4a", 0.8, spec=0.1)
    if win:
        for i in range(max(1, int(w // 2.6))):
            wx = x - w / 2 + (i + 0.5) * w / max(1, int(w // 2.6))
            for wz in ([1.5, 3.6] if h > 4.6 else [1.9]):
                kit.box(f"{name}.win{i}_{wz}", (1.0, 0.1, 1.2), (wx, fy + face * 0.03, wz), glass)
                kit.box(f"{name}.frame{i}_{wz}", (1.3, 0.08, 1.5), (wx, fy + face * 0.015, wz), kit.plastic("#fff4e0", 0.7))
                if boxes:
                    kit.box(f"{name}.wb{i}_{wz}", (1.3, 0.35, 0.3), (wx, fy + face * 0.22, wz - 0.75), kit.plastic("#8a5a3a", 0.8))
                    for k in range(4):
                        kit.sphere(f"{name}.sf{i}_{wz}_{k}", 0.17, (wx - 0.48 + k * 0.32, fy + face * 0.24, wz - 0.5), yellow, seg=8)
                        kit.box(f"{name}.lf{i}_{wz}_{k}", (0.04, 0.04, 0.2), (wx - 0.48 + k * 0.32, fy + face * 0.24, wz - 0.6), leaf)


def sunflower(kit, name, x, y, z, h=1.5, face=-1):
    stem = kit.plastic("#4f8f3a", 0.8, spec=0.05)
    kit.cyl(f"{name}.st", 0.05, h, (x, y, z + h / 2), stem, n=8)
    kit.cyl(f"{name}.pet", 0.36, 0.06, (x, y + face * 0.05, z + h), kit.plastic("#ffd23f", 0.55, spec=0.1),
            rot=(math.pi / 2, 0, 0), n=14)
    kit.cyl(f"{name}.dsc", 0.17, 0.12, (x, y + face * 0.1, z + h), kit.plastic("#6b4326", 0.8, spec=0.05),
            rot=(math.pi / 2, 0, 0), n=10)


def tree(kit, name, x, y, z, h=6.0, tint="#cfe8c0"):
    try:
        kit.prop("commontree_1", (x, y, z), height=h, tint=tint)
    except Exception:
        kit.cyl(f"{name}.trunk", 0.3, h * 0.45, (x, y, z + h * 0.22), kit.plastic("#7a5230", 0.8), n=8)
        kit.sphere(f"{name}.crown", h * 0.28, (x, y, z + h * 0.68), kit.plastic("#5fae4a", 0.8), seg=10)


def wr_line(kit, name, parent, x, z, w, rot, mat, y=-1.245, t=0.075):
    return kit.box(name, (w, 0.05, t), (x, y, z), mat, parent, rot=(0, rot * D2R, 0))


def statue(kit, sand, sand2, crackm):
    root = kit.empty("statue", (0, 0, 0))
    kit.box("plinth", (10.0, 7.6, 1.0), (0, 0, Z0 + 0.5), kit.grime("#e8a48c", 0.88, 1.5, "plinthm", 0.9), root, bevel=0.05)
    kit.box("plinth2", (8.8, 6.6, 0.3), (0, 0, ZB + 0.15), sand2, root, bevel=0.04)
    zb = ZB + 0.3
    for sx in (-1, 1):
        kit.box(f"thigh{sx}", (1.7, 3.8, 1.3), (sx * 1.05, -0.6, zb + 2.0 + 0.65), sand, root, bevel=0.06)
        kit.box(f"shin{sx}", (1.55, 1.4, 2.0), (sx * 1.05, -2.1, zb + 1.0), sand, root, bevel=0.06)
        kit.box(f"foot{sx}", (1.6, 1.9, 0.7), (sx * 1.05, -2.75, zb + 0.35), sand, root, bevel=0.06)
        for k in range(3):
            kit.box(f"toe{sx}_{k}", (0.42, 0.12, 0.45), (sx * 1.05 + (k - 1) * 0.5, -3.72, zb + 0.4), sand2, root, bevel=0.03)
        kit.box(f"upperarm{sx}", (0.95, 1.1, 2.4), (sx * 2.35, 0.7, zb + 5.1), sand, root, bevel=0.06)
        kit.box(f"forearm{sx}", (0.95, 2.7, 0.9), (sx * 2.2, -0.8, zb + 3.85), sand, root, bevel=0.06)
        kit.box(f"hand{sx}", (1.0, 0.95, 0.9), (sx * 2.2, -2.5, zb + 3.85), sand2, root, bevel=0.06)
    kit.box("hips", (3.7, 2.6, 1.1), (0, 0.8, zb + 3.45), sand, root, bevel=0.06)
    kit.box("torso", (3.7, 2.2, 3.4), (0, 0.9, zb + 4.9), sand, root, bevel=0.07)
    kit.box("neck", (1.3, 1.3, 0.6), (0, 0.9, zb + 6.75), sand, root, bevel=0.04)
    # the head: pivots at the neck so it can bend and turn
    head = kit.empty("statue.head", (0, 0.9, zb + 6.9), root)
    W["head"] = head
    kit.box("head.skull", (2.7, 2.5, 3.0), (0, 0, 1.55), sand, head, bevel=0.1)
    kit.box("head.brow", (2.9, 0.5, 0.42), (0, -1.38, 2.18), sand2, head, bevel=0.05)
    kit.box("head.nose", (0.55, 0.75, 1.1), (0, -1.55, 1.38), sand2, head, bevel=0.06)
    kit.box("head.nosebase", (0.95, 0.5, 0.3), (0, -1.48, 0.95), sand2, head, bevel=0.05)
    kit.box("head.stache", (1.9, 0.5, 0.36), (0, -1.38, 0.62), sand2, head, bevel=0.07)
    kit.box("head.chin", (1.6, 0.5, 0.6), (0, -1.35, 0.1), sand2, head, bevel=0.08)
    for sx in (-1, 1):
        kit.box(f"head.cheek{sx}", (0.75, 0.4, 0.55), (sx * 0.95, -1.34, 1.15), sand2, head, bevel=0.07)
        kit.box(f"head.ear{sx}", (0.3, 0.7, 1.0), (sx * 1.5, 0.1, 1.4), sand2, head, bevel=0.05)
        kit.box(f"head.eye{sx}", (0.78, 0.2, 0.34), (sx * 0.68, -1.26, 1.82), crackm, head, bevel=0.03)
        kit.box(f"head.lid{sx}", (0.9, 0.3, 0.14), (sx * 0.68, -1.3, 2.05), sand2, head, bevel=0.03)
    kit.box("head.mouth", (1.2, 0.08, 0.15), (0, -1.265, 0.88), crackm, head)
    # the wrinkles, in the order they go (first gone first); 12 at the start
    wr = []
    wr.append(wr_line(kit, "wr.bagL", head, -0.62, 1.46, 0.62, 0, crackm))        # 0 gone first (12 -> 11)
    wr.append(wr_line(kit, "wr.crowL2", head, -1.17, 1.62, 0.5, -28, crackm))     # 1 (-> 10)
    wr.append(wr_line(kit, "wr.fore4", head, 0, 2.88, 1.55, 0, crackm))           # 2
    wr.append(wr_line(kit, "wr.fore3", head, 0, 2.7, 1.8, 0, crackm))             # 3
    wr.append(wr_line(kit, "wr.crowR2", head, 1.17, 1.62, 0.5, 28, crackm))       # 4 (-> 7)
    wr.append(wr_line(kit, "wr.bagR", head, 0.62, 1.46, 0.62, 0, crackm))         # 5 (-> 6: the one that slides)
    wr.append(wr_line(kit, "wr.fore2", head, 0, 2.52, 2.0, 0, crackm))            # 6 stays
    wr.append(wr_line(kit, "wr.fore1", head, 0, 2.38, 2.1, 0, crackm))
    wr.append(wr_line(kit, "wr.crowL1", head, -1.17, 1.92, 0.5, 28, crackm))
    wr.append(wr_line(kit, "wr.crowR1", head, 1.17, 1.92, 0.5, -28, crackm))
    wr.append(wr_line(kit, "wr.nasoL", head, -0.78, 1.0, 0.8, -30, crackm, y=-1.43))
    wr.append(wr_line(kit, "wr.nasoR", head, 0.78, 1.0, 0.8, 30, crackm, y=-1.43))
    W["wr"] = wr
    # the beard: three hanging strips scaled about the chin
    beard = kit.empty("statue.beard", (0, -0.55, zb + 6.7), root)
    W["beard"] = beard
    for i, (bx, bw, f) in enumerate([(0, 1.4, 1.0), (-0.95, 0.75, 0.82), (0.95, 0.75, 0.82), (-0.45, 0.5, 0.92), (0.45, 0.5, 0.92)]):
        L = 3.2 * f
        kit.box(f"beard{i}", (bw, 0.8, L), (bx, 0, -L / 2), sand2, beard, bevel=0.08)
    # a few hairline cracks on the body
    for i, (cx, cz, ln, rr) in enumerate([(-1.2, 5.5, 1.1, 20), (1.3, 4.6, 0.9, -30), (-0.9, 3.9, 0.7, 0)]):
        kit.box(f"crack{i}", (0.07, 0.05, ln), (cx, -0.22, zb + cz), crackm, root, rot=(0, rr * D2R, 0))
    return root


def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    plastic = kit.plastic
    sand = kit.grime("#e8aa6a", 0.82, 2.2, "sand", 0.88)
    sand2 = kit.grime("#f0b878", 0.86, 3.0, "sand2", 0.88)
    crackm = plastic("#6e4424", 0.9, spec=0.05)
    lawn = kit.grime("#9cc98a", 0.86, 1.4, "lawn", 0.95)
    ground = kit.grime("#a5d08f", 0.88, 1.2, "ground", 0.95)
    brick = kit.bricks("#c4624a", "#b5573f", "#d8b49a", 1.0)
    path = plastic("#efd2b0", 0.85, spec=0.05)
    brass = plastic("#e3b04b", 0.35, spec=0.6)
    cream = plastic("#f6ecd8", 0.7, spec=0.1)

    # ------------------------------------------------------------------ lights (gains set in animate)
    sun = kit.light("sun", "SUN", (0, -30, 40), 1.0, "#fff0d8", size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#cfe6ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    front = kit.light("front", "SUN", (-10, -30, 20), 1.0, "#ffd2ae", shadow=False)
    front.data.angle = 0.4
    kit.aim(front, (0, 0, 0))
    kit.light("cand", "POINT", (0, G.TRAY_Y - 0.8, Z0 + 1.2), 60.0, "#ffcf6e", size=0.3, shadow=False)
    cx, cy = G.COUNTER
    kit.light("bak", "POINT", (cx, cy - 1.5, 3.0), 260.0, "#ffe6c0", size=0.5, shadow=False)
    hx, hy = G.HOME_IN
    kit.light("home", "POINT", (hx, hy - 1.5, 3.0), 260.0, "#ffe6c0", size=0.5, shadow=False)
    mx, my = G.MIRRORS
    kit.light("mir", "POINT", (mx, my - 3.0, 3.2), 200.0, "#fff0d8", size=0.5, shadow=False)
    ax, ay = G.CAL
    kit.light("cal", "POINT", (ax, ay - 3.0, 3.0), 200.0, "#fff0d8", size=0.5, shadow=False)
    sx_, sy_ = G.SLAB
    kit.light("slab", "POINT", (sx_ - 2.0, sy_ - 2.5, 3.0), 160.0, "#ffe6c0", size=0.5, shadow=False)

    # ------------------------------------------------------------------ the town below and the hill
    kit.plane("ground", (700, 700), (0, 0, 0), ground)
    kit.plane("lawn", (36, 36), (0, 2, Z0 + 0.01), lawn)
    kit.box("hill", (36, 36, Z0), (0, 2, Z0 / 2 - 0.02), brick)
    kit.box("path", (4.2, 11.0, 0.04), (0, -10.5, Z0 + 0.03), path)
    kit.box("path2", (7.0, 3.0, 0.04), (0, -4.2, Z0 + 0.03), path)
    n = 15
    y0, y1 = G.STEPS_Y
    for i in range(n):
        h = Z0 - (Z0 / n) * (i + 1) + 0.0
        dy = (y0 - y1) / n
        kit.box(f"step{i}", (8.0, dy, max(0.12, h)), (0, y0 - dy * (i + 0.5), max(0.12, h) / 2), brick)
    for sx in (-1, 1):
        kit.box(f"stepwall{sx}", (0.5, y0 - y1 + 0.2, 1.0), (sx * 4.25, (y0 + y1) / 2, 0.5 + 0.9), kit.grime("#e8a48c", 0.9, 2, "wallm", 0.9))
    # the statue
    statue(kit, sand, sand2, crackm)
    # the candle tray
    kit.box("tray", (7.0, 2.2, 0.18), (0, G.TRAY_Y, Z0 + 0.09), brass, bevel=0.04)
    flame_m = kit.emit("#ffcf6e", 5.0)
    W["flames"] = []
    for r in range(2):
        for c in range(9):
            x = -3.0 + c * 0.75 + (0.35 if r else 0)
            y = G.TRAY_Y - 0.45 + r * 0.9
            col = ["#f6ecd8", "#ffd9e0", "#d8ecff"][(r + c) % 3]
            kit.cyl(f"candle{r}_{c}", 0.13, 0.6, (x, y, Z0 + 0.18 + 0.3), plastic(col, 0.6), n=10)
            W["flames"].append(kit.sphere(f"flame{r}_{c}", 0.09, (x, y, Z0 + 0.18 + 0.68), flame_m, seg=8))
    # the bench (faces +y), with two sage strokes scratched on its iron arm
    bx, by = G.BENCH
    iron = kit.metal("#4a4d52", 0.5)
    wood = plastic("#a8744a", 0.7, spec=0.1)
    kit.box("bench.seat", (3.4, 1.0, 0.14), (bx, by, Z0 + 0.55), wood)
    kit.box("bench.back", (3.4, 0.14, 0.9), (bx, by - 0.5, Z0 + 1.05), wood)
    for sx in (-1, 1):
        kit.box(f"bench.leg{sx}", (0.14, 0.9, 0.55), (bx + sx * 1.5, by, Z0 + 0.27), iron)
        kit.box(f"bench.arm{sx}", (0.24, 1.0, 0.12), (bx + sx * 1.74, by, Z0 + 0.85), iron)
    for k in range(2):
        kit.box(f"bench.stroke{k}", (0.05, 0.5, 0.025), (bx + 1.74 - 0.05 + k * 0.1, by - 0.0 + 0.0, Z0 + 0.915), plastic("#9cc98a", 0.6))
    # sunflower beds and trees
    for bed_x in (-10.0, 10.0):
        for i in range(5):
            for j in range(4):
                sunflower(kit, f"sf{bed_x}_{i}_{j}", bed_x + (i - 2) * 0.85 + (j % 2) * 0.4, -3.0 + j * 1.3 + (i % 2) * 0.3, Z0,
                          1.4 + 0.25 * ((i * 3 + j) % 3))
    for k, (x, y) in enumerate([(-15, 6), (15, 4), (-14, 14), (14, 15), (0, 17)]):
        tree(kit, f"tree{k}", x, y, Z0, 7.5 + (k % 2))
    # the town below the steps: a street and houses facing the hill
    kit.plane("tstreet", (260, 7.0), (0, -33.0, 0.02), plastic("#d9b8a0", 0.9, spec=0.05))
    cols = ["#e8a48c", "#f2c9a8", "#ee9c86", "#f6d8b8", "#e8b49c"]
    for i, x in enumerate(range(-60, 61, 11)):
        house(kit, f"t{i}", x + (i % 3), -42.0 - (i % 2) * 2, 8.0, 7.0, 5.0 + (i % 3), cols[i % 5], face=+1)
        house(kit, f"u{i}", x + 4 + (i % 2), -60.0, 9.0, 8.0, 5.5 + (i % 2), cols[(i + 2) % 5], face=+1)

    # ------------------------------------------------------------------ main street + bakery
    sx0, sy0 = G.STREET
    kit.plane("street", (90, 6.0), (sx0, sy0 - 0.5, 0.03), plastic("#d9b8a0", 0.9, spec=0.05))
    kit.plane("walk", (90, 3.0), (sx0, sy0 + 1.0, 0.05), plastic("#efd2b0", 0.9, spec=0.05))
    kit.plane("sstreet2", (90, 4.0), (sx0, sy0 - 6.0, 0.02), lawn)
    house(kit, "bk", sx0, 5.0, 8.0, 6.0, 5.0, "#f2c9a8", face=-1, win=False)
    stripe_a, stripe_b = plastic("#ffd23f", 0.6), plastic("#fffaf0", 0.6)
    for i in range(14):
        kit.box(f"awn{i}", (0.57, 1.9, 0.07), (sx0 - 3.7 + i * 0.57, 1.25, 3.25), stripe_a if i % 2 else stripe_b,
                rot=(-22 * D2R, 0, 0))
    kit.box("bk.door", (1.5, 0.12, 2.5), (sx0 + 0.0, 1.95, 1.85), plastic("#ee9c86", 0.5, spec=0.3))
    kit.box("bk.win", (2.2, 0.12, 1.5), (sx0 - 2.6, 1.95, 2.0), plastic("#7fb2cc", 0.2, spec=0.8))
    kit.box("bk.win2", (2.2, 0.12, 1.5), (sx0 + 2.6, 1.95, 2.0), plastic("#7fb2cc", 0.2, spec=0.8))
    for i in range(3):
        kit.box(f"bk.step{i}", (3.4, 0.6, 0.2 * (i + 1)), (sx0, 0.2 + 0.6 * i, 0.1 * (i + 1)), brick)
    for k, (x, c) in enumerate([(-8.5, "#ee9c86"), (8.8, "#f6d8b8"), (-17, "#e8b49c"), (17.5, "#f2c9a8"), (26, "#ee9c86"), (-26, "#f6d8b8")]):
        house(kit, f"nb{k}", sx0 + x, 5.0, 9.0, 6.0, 4.6 + (k % 3), c, face=-1)
    for k in range(10):
        house(kit, f"far{k}", sx0 - 40 + k * 9, 16.0, 8.0, 6.0, 5.5 + (k % 3), cols[k % 5], face=-1)
    tree(kit, "st_tree1", sx0 - 5.2, -0.8, 0, 4.5)
    tree(kit, "st_tree2", sx0 + 5.6, -0.8, 0, 4.5)
    # our front door, dawn
    ox, oy = G.HOME_OUT
    kit.plane("hstreet", (60, 6.0), (ox, oy - 3.5, 0.03), plastic("#d9b8a0", 0.9, spec=0.05))
    kit.plane("hwalk", (40, 3.0), (ox, oy + 0.0, 0.05), plastic("#efd2b0", 0.9, spec=0.05))
    wallm = kit.grime("#e8a48c", 0.9, 2.0, "hwall", 0.9)
    for (dx, w_) in [(-3.0, 4.6), (3.0, 4.6)]:
        kit.box(f"hf{dx}", (w_, 0.4, 4.5), (ox + dx, oy + 2.0, 2.25), wallm)
    kit.box("hlintel", (4.0, 0.4, 1.5), (ox, oy + 2.0, 3.75), wallm)
    kit.box("hback", (14, 0.4, 4.5), (ox, oy + 8.2, 2.25), wallm)
    for sx in (-1, 1):
        kit.box(f"hsidew{sx}", (0.4, 6.4, 4.5), (ox + sx * 7.0, oy + 5.2, 2.25), wallm)
    kit.box("hfloor", (14, 6.4, 0.06), (ox, oy + 5.2, 0.04), plastic("#c9976a", 0.8))
    kit.box("hroof", (14.6, 7.5, 0.5), (ox, oy + 4.8, 4.75), plastic("#c4624a", 0.7))
    door = kit.empty("hdoor", (ox - 1.0, oy + 1.8, 0))
    kit.box("hdoor.leaf", (1.0, 0.1, 2.5), (0.5, 0, 1.25), plastic("#7bbfd8", 0.5, spec=0.3), door)
    door.rotation_euler = (0, 0, 70 * D2R)
    for i in range(2):
        kit.box(f"hstep{i}", (2.6, 0.6, 0.15 * (i + 1)), (ox, oy + 1.0 - i * 0.6, 0.075 * (i + 1)), brick)
    for i in range(8):
        sunflower(kit, f"hsf{i}", ox - 5.5 + i * 0.5, oy + 1.2, 0, 1.3, face=-1)
    for k in range(5):
        house(kit, f"hfar{k}", ox - 30 + k * 14, 14.0, 9.0, 6.0, 5.0 + (k % 3), cols[k % 5], face=-1)

    # ------------------------------------------------------------------ inside the bakery
    cwall = plastic("#f6e2c0", 0.85, spec=0.05)
    kit.plane("bkfloor", (12, 9), (cx, cy, 0.03), kit.planks("#c9976a", "#b78456", 1.0))
    kit.box("bkback", (12, 0.3, 3.4), (cx, cy + 3.5, 1.7), cwall)
    for sx in (-1, 1):
        kit.box(f"bkside{sx}", (0.3, 9, 3.4), (cx + sx * 6, cy, 1.7), cwall)
    kit.box("counter", (5.0, 1.0, 1.1), (cx, cy + 0.45, 0.55), plastic("#ffd23f", 0.5, spec=0.2))
    kit.box("counter.top", (5.2, 1.2, 0.1), (cx, cy + 0.45, 1.15), cream, bevel=0.02)
    for z in (1.5, 2.2):
        kit.box(f"shelf{z}", (5.0, 0.5, 0.1), (cx, cy + 3.15, z), wood)
    for k in range(10):
        for z in (1.5, 2.2):
            kit.box(f"loaf{z}_{k}", (0.5, 0.3, 0.26), (cx - 2.2 + k * 0.5, cy + 3.1, z + 0.18), plastic("#d99a4a", 0.7, spec=0.1), bevel=0.08)
    # the old photo on the back wall, past the shelf: young Mrs. Lark beside the shabby old bakery front (no text)
    px, py = cx + 4.2, cy + 3.3
    pz = 1.9
    pl = lambda c, r=0.9: plastic(c, r)
    kit.box("photo.frame", (2.0, 0.08, 1.6), (px, py, pz), pl("#5a3b24", 0.7))
    kit.box("photo.bg", (1.8, 0.05, 1.4), (px, py - 0.06, pz), pl("#e9d8b4"))
    kit.box("photo.sky", (1.8, 0.02, 0.5), (px, py - 0.075, pz + 0.45), pl("#d6dcc8"))
    kit.box("photo.shop", (1.0, 0.03, 0.85), (px - 0.4, py - 0.09, pz - 0.15), pl("#7c7062"))
    kit.box("photo.roof", (1.1, 0.03, 0.14), (px - 0.4, py - 0.10, pz + 0.33), pl("#4a4036"))
    kit.box("photo.awn", (1.1, 0.03, 0.2), (px - 0.4, py - 0.11, pz + 0.12), pl("#a8a090"))
    for k in range(4):
        kit.box(f"photo.awnstripe{k}", (0.13, 0.03, 0.2), (px - 0.75 + k * 0.3, py - 0.12, pz + 0.12), pl("#6e665a"))
    kit.box("photo.door", (0.3, 0.03, 0.5), (px - 0.4, py - 0.11, pz - 0.35), pl("#3c2e22"))
    kit.box("photo.win", (0.28, 0.03, 0.28), (px - 0.8, py - 0.11, pz - 0.18), pl("#9aa4a0"))
    kit.box("photo.crack", (0.03, 0.03, 0.3), (px - 0.08, py - 0.11, pz - 0.05), pl("#2e261e"))
    kit.box("photo.body", (0.34, 0.03, 0.55), (px + 0.5, py - 0.10, pz - 0.35), pl("#2fa8a0"))
    kit.box("photo.apron", (0.22, 0.03, 0.38), (px + 0.5, py - 0.11, pz - 0.42), pl("#fffaf0"))
    kit.box("photo.head", (0.32, 0.03, 0.32), (px + 0.5, py - 0.11, pz + 0.07), pl("#f0c8a0"))
    kit.box("photo.hair", (0.34, 0.03, 0.1), (px + 0.5, py - 0.12, pz + 0.2), pl("#18120e"))
    kit.sphere("photo.bun", 0.1, (px + 0.5, py - 0.12, pz + 0.3), pl("#18120e"), seg=8)
    for sx in (-1, 1):
        kit.box(f"photo.eye{sx}", (0.05, 0.03, 0.05), (px + 0.5 + sx * 0.08, py - 0.125, pz + 0.1), pl("#1c120c"))
    kit.box("photo.smile", (0.14, 0.03, 0.03), (px + 0.5, py - 0.125, pz - 0.02), pl("#7a3a30"))
    mirr = kit.metal("#fbfbff", 0.03)
    mfr = plastic("#e3b04b", 0.4, spec=0.5)
    kit.box("bkmirror.frame", (1.1, 0.06, 1.6), (cx - 2.8, cy + 3.3, 1.9), mfr)
    kit.box("bkmirror.glass", (0.9, 0.04, 1.4), (cx - 2.8, cy + 3.27, 1.9), mirr)

    # ------------------------------------------------------------------ the town's mirror wall
    kit.plane("mfloor", (24, 12), (mx, my, 0.03), plastic("#efd2b0", 0.9, spec=0.05))
    kit.box("mwall", (16, 0.4, 4.0), (mx, my + 2.5, 2.0), kit.grime("#e8a48c", 0.9, 2.0, "mwallm", 0.9))
    for i, xo in enumerate([-1.95, -0.65, 0.65, 1.95]):
        kit.box(f"mirror{i}.frame", (1.2, 0.08, 2.5), (mx + xo, my + 2.27, 2.0), mfr)
        kit.box(f"mirror{i}.glass", (0.98, 0.04, 2.2), (mx + xo, my + 2.22, 2.0), mirr)

    # ------------------------------------------------------------------ the hall and the kitchen
    hwall = plastic("#f6dcc8", 0.85, spec=0.05)
    kit.plane("hfloor", (12, 9), (hx, hy, 0.03), kit.planks("#c9976a", "#b78456", 1.0))
    kit.box("hwall", (12, 0.3, 3.4), (hx, hy + 3.5, 1.7), hwall)
    for sx in (-1, 1):
        kit.box(f"hside{sx}", (0.3, 9, 3.4), (hx + sx * 6, hy, 1.7), hwall)
    kit.box("hmirror.frame", (1.5, 0.08, 2.3), (hx - 1.5, hy + 3.28, 1.7), mfr)
    kit.box("hmirror.glass", (1.25, 0.04, 2.0), (hx - 1.5, hy + 3.22, 1.7), mirr)
    kit.box("table", (2.6, 1.6, 0.12), (hx + 2.8, hy + 1.2, 0.95), wood)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"tleg{sx}{sy}", (0.12, 0.12, 0.9), (hx + 2.8 + sx * 1.15, hy + 1.2 + sy * 0.65, 0.45), wood)
    kit.box("tcloth", (2.2, 1.2, 0.04), (hx + 2.8, hy + 1.2, 1.03), plastic("#ffd23f", 0.7))
    kit.cyl("cup.base", 0.2, 0.18, (hx + 2.8, hy + 1.1, 1.14), plastic("#f6ecd8", 0.7), n=14, r2=0.17)
    kit.cyl("cup.top", 0.22, 0.14, (hx + 2.8, hy + 1.1, 1.3), plastic("#ffb0c8", 0.5, spec=0.2), n=14, r2=0.12)
    kit.cyl("cup.candle", 0.025, 0.14, (hx + 2.8, hy + 1.1, 1.44), plastic("#ffd23f", 0.6), n=8)
    kit.sphere("cup.flame", 0.035, (hx + 2.8, hy + 1.1, 1.54), flame_m, seg=8)
    for sy in (-1, 1):
        kit.box(f"chair{sy}", (0.5, 0.5, 0.08), (hx + 2.8 + sy * 0.9, hy + 2.2, 0.55), wood)
    kit.box("kwin", (2.2, 0.08, 1.6), (hx + 3.0, hy + 3.3, 1.8), plastic("#8fd3ff", 0.2, spec=0.8))
    for k in range(6):
        sunflower(kit, f"hall_sf{k}", hx - 4.6 + k * 0.2, hy + 2.9, 0.6, 0.9)

    # ------------------------------------------------------------------ the calendar glyph
    kit.box("cal.back", (7, 0.2, 6), (ax, ay + 1.2, 3.0), plastic("#ffd23f", 0.6))
    kit.box("cal.card", (3.2, 0.12, 3.8), (ax, ay, 2.1), plastic("#fffaf0", 0.6))
    kit.box("cal.band", (3.2, 0.14, 0.7), (ax, ay - 0.01, 3.75), plastic("#ee9c86", 0.6))
    for r in range(4):
        for c in range(5):
            kit.box(f"cal.cell{r}{c}", (0.4, 0.04, 0.4), (ax - 1.2 + c * 0.6, ay - 0.08, 3.0 - r * 0.6), plastic("#e6e0d6", 0.8))
    kit.cyl("cal.ring", 0.36, 0.05, (ax + 0.0, ay - 0.1, 2.4), plastic("#e8493a", 0.6), rot=(math.pi / 2, 0, 0), n=20)
    kit.cyl("cal.ringin", 0.27, 0.05, (ax + 0.0, ay - 0.12, 2.4), plastic("#e6e0d6", 0.8), rot=(math.pi / 2, 0, 0), n=20)
    hinge = kit.empty("cal.hinge", (ax, ay - 0.2, 4.0))
    kit.box("cal.page", (3.2, 0.1, 3.8), (0, 0, -1.9), plastic("#fffaf0", 0.6), hinge)
    kit.box("cal.pband", (3.2, 0.12, 0.7), (0, -0.01, -0.35), plastic("#ee9c86", 0.6), hinge)
    for r in range(4):
        for c in range(5):
            kit.box(f"cal.pcell{r}{c}", (0.4, 0.04, 0.4), (-1.2 + c * 0.6, -0.07, -1.0 - r * 0.6), plastic("#e6e0d6", 0.8), hinge)
    W["calhinge"] = hinge

    # ------------------------------------------------------------------ the stone cheek, close, with Mom's hand on it
    sand2s = kit.grime("#f0b878", 0.86, 3.0, "sand2", 0.88)
    dark = plastic("#3a1c0a", 0.9, spec=0.05)
    yc = sy_ - 1.5                       # the face's centre line; Mom's hand is on its +y cheek
    X0 = G.SLAB_X
    kit.box("slab", (1.0, 11.0, 7.0), (X0 + 0.5, yc + 0.5, 3.5), sand)
    kit.box("slab.brow", (0.5, 6.0, 0.5), (X0 - 0.25, yc, 4.2), sand2s, bevel=0.05)
    kit.box("slab.nose", (0.7, 0.9, 2.3), (X0 - 0.35, yc, 2.7), sand2s, bevel=0.06)
    kit.box("slab.nosebase", (0.55, 1.5, 0.35), (X0 - 0.28, yc, 1.6), sand2s, bevel=0.05)
    for sg in (-1, 1):
        kit.box(f"slab.eye{sg}", (0.08, 1.5, 0.4), (X0 - 0.04, yc + sg * 1.5, 3.55), dark)
        kit.box(f"slab.lid{sg}", (0.3, 1.8, 0.22), (X0 - 0.15, yc + sg * 1.5, 3.9), sand2s, bevel=0.03)
        kit.box(f"slab.cheek{sg}", (0.3, 1.5, 1.0), (X0 - 0.15, yc + sg * 1.5, 2.0), sand2s, bevel=0.07)
    kit.box("slab.mouth", (0.08, 3.0, 0.16), (X0 - 0.04, yc, 0.8), dark)
    kit.box("slab.stache", (0.3, 3.4, 0.4), (X0 - 0.15, yc, 1.1), sand2s, bevel=0.06)
    # the forehead wrinkles (the statue's carved lines) and crow's feet by each eye
    for i in range(6):
        kit.box(f"slab.wr{i}", (0.06, 4.6 - 0.2 * i, 0.09), (X0 - 0.03, yc, 4.65 + 0.22 * i), dark)
    for sg in (-1, 1):
        for k in range(2):
            kit.box(f"slab.crow{sg}{k}", (0.06, 0.6, 0.07), (X0 - 0.03, yc + sg * 2.6, 3.45 + 0.3 * k), dark,
                    rot=(sg * (0.4 - 0.8 * k), 0, 0))
    W["crack"] = kit.box("slab.crack", (0.1, 0.9, 0.13), (X0 - 0.34, sy_ - 0.1, 2.0), dark)
    kit.plane("slabfloor", (20, 20), (0, sy_, 0.03), lawn)

    # ------------------------------------------------------------------ the sun coming up behind the statue
    W["disc"] = kit.sphere("sundisc", 9.0, (-4, 190, 6), kit.emit("#fff2c8", 6.0), seg=16)
    noshadow(W["disc"])
    W["disc"].visible_glossy = False

    # ------------------------------------------------------------------ the rule meter: a plate on the camera
    build_tag(kit)
    return {}


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def build_tag(kit):
    """The rule meter: a carved stone FACE on a dark plate. Its forehead carries the statue's wrinkles as 12 horizontal
    carved dashes (two columns of six); each gone wrinkle takes a dash off the forehead."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    stone = kit.emit("#f6d6a6", 0.8, "tagstone")
    edge = kit.emit("#3a2210", 0.5, "tagedge")
    ink = kit.emit("#3a1c0a", 0.5, "tagink")
    beard_m = kit.emit("#b9824f", 0.6, "tagbeard")
    # unit plate: 1 wide, 0.9 tall; layers 0.004 apart toward the camera
    def b(name, size, loc, mat):
        ob = kit.box(name, size, loc, mat, root)
        noshadow(ob)
        return ob
    b("tag.edge", (1.0, 0.92, 0.004), (0, 0, 0.0), edge)
    b("tag.plate", (0.9, 0.82, 0.004), (0, 0, 0.004), stone)
    # beard and eyes
    b("tag.beard", (0.62, 0.24, 0.004), (0, -0.28, 0.008), beard_m)
    b("tag.mouth", (0.24, 0.04, 0.004), (0, -0.2, 0.012), ink)
    for sx in (-1, 1):
        b(f"tag.eye{sx}", (0.15, 0.1, 0.004), (sx * 0.22, -0.02, 0.008), ink)
        b(f"tag.brow{sx}", (0.26, 0.05, 0.004), (sx * 0.22, 0.07, 0.008), ink)
    b("tag.nose", (0.08, 0.17, 0.004), (0, -0.1, 0.008), beard_m)
    W["bars"] = []
    for i in range(12):
        col, row = divmod(i, 6)
        x = -0.2 + col * 0.4
        z0 = 0.33 - row * 0.043
        bar = b(f"tag.bar{i}", (0.34, 0.026, 0.004), (x, z0, 0.008), ink)
        W["bars"].append((bar, z0))


def _first_frame(kit, story):
    names = tuple(story.get("cast", {}))
    hg = bpy.data.objects.get("dad.headg")
    if hg is not None:
        m = kit.plastic("#b9b9bf", 0.8)
        kit.box("dad.stache", (0.56, 0.07, 0.11), (0, -0.62 - 0.02, -0.2), m, hg, bevel=0.03)
        kit.box("dad.brow", (0.8, 0.05, 0.05), (0, -0.62 - 0.02, 0.14), m, hg)
    mh = bpy.data.objects.get("mom.headg")
    W["streak"], W["smile"] = [], []
    if mh is not None:
        sil = kit.plastic("#d8d8e0", 0.5, spec=0.3)
        # silver streaks lying on the top-front of her hair (the chestnut fringe), one at L21, more by L29
        for i, (x, y, z, w_, h_) in enumerate([(-0.28, -0.52, 0.5, 0.12, 0.38), (0.2, -0.52, 0.5, 0.1, 0.34),
                                                (-0.05, -0.5, 0.55, 0.1, 0.3), (0.42, -0.4, 0.5, 0.1, 0.3)]):
            ob = kit.box(f"mom.streak{i}", (w_, 0.2, h_), (x, y, z), sil, mh, bevel=0.03)
            ob.rotation_euler = (0, 0, (-10 + 8 * i) * D2R)
            W["streak"].append(ob)
        W["streak"].append(kit.box("mom.silvtop", (1.36, 1.3, 0.05), (0, 0.0, 0.72), sil, mh, bevel=0.02))
        W["back"] = []
        # uneven silver streaks running down the back of her hair from the crown, a wide band at the top
        for k, (x, h_, w_, rz) in enumerate([(-0.42, 1.45, 0.2, 6), (-0.14, 1.0, 0.11, -5), (0.14, 1.55, 0.22, 4),
                                             (0.4, 1.1, 0.12, -6), (-0.28, 0.6, 0.09, 3), (0.28, 0.7, 0.09, -3)]):
            ob = kit.box(f"mom.back{k}", (w_, 0.06, h_), (x, 0.8, 0.7 - h_ / 2), sil, mh, bevel=0.01)
            ob.rotation_euler = (0, rz * D2R, 0)
            W["back"].append(ob)
        W["back"].append(kit.box("mom.backtop", (1.1, 0.06, 0.45), (0, 0.8, 0.5), sil, mh, bevel=0.01))
        clipm = kit.plastic("#ffd23f", 0.5)
        kit.box("mom.clip", (0.22, 0.1, 0.22), (0.45, -0.55, 0.42), clipm, mh, bevel=0.05)
        kit.sphere("mom.clip2", 0.11, (0.45, -0.6, 0.42), kit.plastic("#6b4326", 0.8), mh, seg=8)
        dark = kit.plastic("#7a4a38", 0.8)
        for sx in (-1, 1):
            ob = kit.box(f"mom.smile{sx}", (0.035, 0.03, 0.2), (sx * 0.42, -0.6, -0.26), dark, mh)
            ob.rotation_euler = (0, 0, sx * 20 * D2R)
            W["smile"].append(ob)
    W["inited"] = True


def _hide(ob, hide):
    ob.hide_render = hide
    for c in ob.children_recursive:
        c.hide_render = hide


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    look = look_at(tl, t)
    gains = {}
    # sun
    az, el = look["az"] * D2R, look["el"] * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    so = kit.LIGHTS["sun"]["obj"]
    so.location = d * 60
    kit.aim(so, (0, 0, 0))
    kit.LIGHTS["sun"]["light"].color = look["sun_col"]
    kit.LIGHTS["fill"]["light"].color = look["fill_col"]
    gains["sun"], gains["fill"], gains["front"] = look["sun"], look["fill"], look["front"]
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*look["sky"], 1.0)
    bg.inputs["Strength"].default_value = look["sky_str"]
    # the sun disc rises behind the statue in the sunrise look
    rise = sample("rise", tl, t, {"z": 4.0})
    disc = W["disc"]
    disc.location = (-5, 190, rise["z"])
    disc.hide_render = look["disc"] < 0.01
    # the statue: wrinkles, beard, head
    st = sample("statue", tl, t, {"wr": 12.0, "beard": 1.0, "pitch": 0.0, "yaw": 0.0})
    n = int(round(st["wr"]))
    for i, ob in enumerate(W["wr"]):
        ob.hide_render = i < 12 - n
    W["beard"].scale = (1.0, 1.0, max(0.05, st["beard"]))
    W["head"].rotation_euler = (st["pitch"] * D2R, 0, st["yaw"] * D2R)
    # the tally on the plate
    ty = sample("tally", tl, t, {"n": 12.0})
    for i, (bar, z0) in enumerate(W["bars"]):
        v = min(1.0, max(0.0, ty["n"] - i))
        bar.scale = (max(0.001, v), max(0.001, v), 1.0)
        bar.hide_render = v < 0.02
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
    s = 0.52 * w2
    tag.scale = (s, s, s)
    tag.location = (-0.38 * w2, 0.585 * h2, -dist)
    # the calendar page
    fl = sample("flip", tl, t, {"v": 0.0})
    W["calhinge"].rotation_euler = (-fl["v"] * 175 * D2R, 0, 0)
    # Mom: silver streaks, smile line
    mo = sample("mom", tl, t, {"streak": 0.0, "smile": 0.0})
    for i, ob in enumerate(W["streak"]):
        ob.hide_render = i >= int(round(mo["streak"]))
    for ob in W["smile"]:
        ob.hide_render = mo["smile"] < 0.5
    for ob in W.get("back", []):
        ob.hide_render = mo["streak"] < 5.5
    # the crack sliding off the stone onto Mom's cheek
    sl = sample("slide", tl, t, {"u": 0.0})
    ck = W["crack"]
    u = sl["u"]
    mh = bpy.data.objects.get("mom.headg")
    start = Vector((G.SLAB_X - 0.34, G.SLAB[1] - 0.1, 2.0))
    if u <= 0.001:
        ck.location = start
        ck.rotation_euler = (0, 0, 0)
        ck.scale = (1, 1, 1)
        ck.hide_render = False
    elif u >= 0.999:
        ck.hide_render = True
    else:
        bpy.context.view_layer.update()
        tgt = mh.matrix_world @ Vector((0.4, -0.66, -0.22)) if mh is not None else Vector((0.7, G.SLAB[1], 1.7))
        p = start.lerp(tgt, ss(u))
        p.x -= 0.12 * math.sin(math.pi * u)          # lifts off the stone as it goes
        ck.location = p
        ck.rotation_euler = (0, 0, 90 * D2R * ss(u))
        k_ = 1.0 - 0.75 * ss(u)
        ck.scale = (k_, k_, k_)
        ck.hide_render = False
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
    return gains
