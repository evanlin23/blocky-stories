"""ep114 "band green": a town green with a white bandstand, string lights, painted shops and a bench.

The rule meter is a cream tag on the camera (top-left): a music-note glyph, the song counter (1 to 47) in seven
segment digits, and a row of seven footprint glyphs that light when people dance (mine, the last, stays dark until
L37). Everything the story moves is driven by cues in story.json (see animate): the look, the song counter, the
footprints, how hard the town dances and how tired it is, which way it faces, the band's walk, pose, brim and eyes,
the clock, the truck and the phone's screen. The dancers' moves are drawn in animate on top of their acting keys.
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


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def _L(**kw):
    base = dict(sun=4.0, sun_col="#ffc58a", sd=(-0.62, -0.62, 0.5), fill=1.1, fill_col="#ffe6cc", sky="#ffc89a",
                sky_str=1.0, bulbs=0.0, stage=0.0, rim=0.0, disc=0.0)
    base.update(kw)
    return base


LOOKS = {
    # the bright summer evening: low warm sun from the south-west, the bandstand roof keeps the players in shade
    "dusk": _L(),
    # three in the morning: the string lights and the lit bandstand are the light
    "night": _L(sun=0.0, sd=(-0.3, -0.5, 0.8), fill=0.9, fill_col="#8fa8ff", sky="#243466", sky_str=0.9,
                bulbs=520.0, stage=380.0, rim=600.0),
    # sunrise over the green, gold
    "dawn": _L(sun=3.6, sun_col="#ffd9a0", sd=(0.3, 0.8, 0.32), fill=1.5, fill_col="#ffe9c8", sky="#ffd8a6",
               sky_str=1.0, bulbs=60.0, disc=1.0),
}


def look_at(tl, t):
    cues = [c for c in tl["cues"] if c["name"] == "look"]
    cur = LOOKS[cues[0]["id"]] if cues else LOOKS["dusk"]
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
                elif isinstance(a, tuple):
                    out[k] = tuple(x + (y - x) * u for x, y in zip(a, b))
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


def seg(kit, name, p0, p1, w, mat, parent=None):
    """A thin box from p0 to p1."""
    d = Vector(p1) - Vector(p0)
    L = d.length
    mid = (Vector(p0) + Vector(p1)) / 2
    horiz = math.hypot(d.x, d.y)
    return kit.box(name, (L, w, w), tuple(mid), mat, parent, rot=(0, -math.atan2(d.z, horiz), math.atan2(d.y, d.x)))


# ---------------------------------------------------------------------------------------------- the town
def shop(kit, name, x, y, face, w, d, h, color, glyph, roof="#d9684a"):
    """A painted shop whose front faces `face` ('S' faces -y ... ). Local frame: width along x, front at -y."""
    ang = {"S": 0, "E": 90, "N": 180, "W": -90}[face] * D2R
    root = kit.empty(f"shop.{name}", (x, y, 0), rot=(0, 0, ang))
    plastic = kit.plastic
    wall = kit.grime(color, 0.9, 2.0, f"wall{color}", 0.9)
    kit.box(f"{name}.body", (w, d, h), (0, 0, h / 2), wall, root)
    kit.box(f"{name}.roof", (w + 0.7, d + 0.7, 0.45), (0, 0, h + 0.22), plastic(roof, 0.7, spec=0.1), root)
    fy = -d / 2
    glass = plastic("#8fc9e8", 0.15, spec=0.8)
    frame = plastic("#fff7e6", 0.7)
    n = max(1, int(w // 3.4))
    for i in range(n):
        wx = -w / 2 + (i + 0.5) * w / n
        if i == n // 2:
            kit.box(f"{name}.door", (1.5, 0.12, 2.5), (wx, fy - 0.07, 1.25), plastic("#5a8fd9", 0.5, spec=0.3), root)
            continue
        kit.box(f"{name}.frame{i}", (1.9, 0.1, 1.7), (wx, fy - 0.06, 1.7), frame, root)
        kit.box(f"{name}.win{i}", (1.6, 0.1, 1.4), (wx, fy - 0.12, 1.7), glass, root)
    # a striped awning and a glyph board above the door
    ax = -w / 2 + (n // 2 + 0.5) * w / n
    for k in range(6):
        kit.box(f"{name}.awn{k}", (0.42, 1.0, 0.07), (ax - 1.05 + k * 0.42, fy - 0.55, 2.85),
                plastic("#fff7e6" if k % 2 else color, 0.6), root, rot=(-15 * D2R, 0, 0))
    bz = h - 0.9
    kit.box(f"{name}.board", (2.6, 0.14, 1.2), (ax, fy - 0.1, bz), plastic("#2d3a5c", 0.6, spec=0.1), root)
    gm = plastic("#ffd36b", 0.4, spec=0.3)
    gw = plastic("#fff7e6", 0.5)
    gy = fy - 0.2
    if glyph == "coin":      # bank
        kit.cyl(f"{name}.coin", 0.45, 0.06, (ax, gy, bz), gm, root, rot=(math.pi / 2, 0, 0), n=20)
        kit.cyl(f"{name}.coin2", 0.28, 0.06, (ax, gy - 0.03, bz), plastic("#e6b640", 0.4, spec=0.3), root,
                rot=(math.pi / 2, 0, 0), n=20)
    elif glyph == "loaf":    # bakery
        kit.box(f"{name}.loaf", (1.3, 0.1, 0.6), (ax, gy, bz - 0.05), plastic("#e0a050", 0.6), root, bevel=0.2)
        for k in range(3):
            kit.box(f"{name}.cut{k}", (0.08, 0.04, 0.3), (ax - 0.35 + k * 0.35, gy - 0.06, bz - 0.02), plastic("#b87a38", 0.7), root,
                    rot=(0, 0.5, 0))
    elif glyph == "mail":    # post office: an envelope
        kit.box(f"{name}.env", (1.4, 0.08, 0.9), (ax, gy, bz), gw, root)
        seg(kit, f"{name}.f1", (ax - 0.7, gy - 0.05, bz + 0.45), (ax, gy - 0.05, bz - 0.05), 0.06, gm, root)
        seg(kit, f"{name}.f2", (ax + 0.7, gy - 0.05, bz + 0.45), (ax, gy - 0.05, bz - 0.05), 0.06, gm, root)
    elif glyph == "cup":
        kit.cyl(f"{name}.cup", 0.3, 0.6, (ax, gy, bz), gw, root, rot=(math.pi / 2, 0, 0), n=14)
        kit.box(f"{name}.cuph", (0.2, 0.06, 0.3), (ax + 0.4, gy, bz), gw, root)
    elif glyph == "key":
        kit.cyl(f"{name}.key", 0.28, 0.06, (ax - 0.4, gy, bz), gm, root, rot=(math.pi / 2, 0, 0), n=14)
        kit.box(f"{name}.keyb", (0.9, 0.06, 0.12), (ax + 0.2, gy, bz), gm, root)
    return root


def tree(kit, name, x, y, h=6.0, tint="#d4f0c4"):
    try:
        kit.prop("commontree_1", (x, y, 0), height=h, tint=tint)
    except Exception:
        kit.cyl(f"{name}.trunk", 0.3, h * 0.45, (x, y, h * 0.22), kit.plastic("#7a5230", 0.8), n=8)
        kit.sphere(f"{name}.crown", h * 0.28, (x, y, h * 0.68), kit.plastic("#5fae4a", 0.8), seg=10)


def bandstand(kit):
    plastic = kit.plastic
    white = plastic("#f2f0e8", 0.55, spec=0.15)
    trim = plastic("#d9d5c8", 0.6)
    zf = G.STAGE_Z
    cx, cy = 0.0, G.STAGE[1] + 2.05           # the stage floor runs 3 m either side of cy
    front, back = cy - 3.0, cy + 3.0
    kit.box("stage.floor", (10.4, 6.0, zf), (cx, cy, zf / 2), kit.planks("#c9b896", "#b8a584", 1.2), bevel=0.04)
    kit.box("stage.skirt", (10.5, 0.15, zf), (cx, front - 0.07, zf / 2), white)
    for i in range(3):
        kit.box(f"stage.step{i}", (3.0, 0.5, 0.3 * (3 - i)), (0, front - 0.25 - i * 0.5, 0.15 * (3 - i)), trim)
        kit.box(f"stage.bstep{i}", (3.0, 0.5, 0.3 * (3 - i)), (0, back + 0.25 + i * 0.5, 0.15 * (3 - i)), trim)
    for sx in (-1, 1):
        for yy in (cy - 2.7, cy + 2.7):
            kit.cyl(f"post{sx}_{yy}", 0.14, 2.6, (sx * 4.8, yy, zf + 1.3), white, n=12)
    # the roof: two slabs meeting at a ridge, low enough that the players' hat crowns touch the eave
    ey = 2.95
    rise = 1.1
    ang = math.atan2(rise, ey)
    L = math.hypot(ey, rise) + 0.3
    roofm = plastic("#c8c4b8", 0.7, spec=0.1)
    zt = zf + 2.45
    for s in (-1, 1):
        kit.box(f"roof{s}", (10.8, L, 0.14), (0, cy + s * ey / 2, zt + rise / 2 + 0.07), roofm, rot=(-s * ang, 0, 0))
        kit.box(f"trim{s}", (10.8, 0.1, 0.14), (0, cy + s * (ey + 0.1), zt + 0.0), white)
    for sx in (-1, 1):   # the gable ends: a triangle of wall
        verts = [(sx * 5.4, cy - ey, zt), (sx * 5.4, cy + ey, zt), (sx * 5.4, cy, zt + rise)]
        kit.mesh_obj(f"gable{sx}", verts, [(0, 1, 2)] if sx > 0 else [(0, 2, 1)], white)
    kit.box("ridge", (10.9, 0.3, 0.2), (0, cy, zt + rise + 0.1), white)
    # a string of bulbs along each eave
    W["eave_bulbs"] = []
    bm = kit.emit("#ffd36b", 7.0)
    for s in (-1, 1):
        for i in range(15):
            x = -4.6 + i * 0.657
            W["eave_bulbs"].append(kit.sphere(f"eave{s}_{i}", 0.085, (x, cy + s * (ey + 0.05), zt - 0.1 + 0.04 * math.sin(i * 0.9)), bm, seg=8))
    ink = plastic("#2b2b30", 0.5)
    for x in G.BAND_X:   # blank music stands
        kit.cyl(f"stand{x}", 0.02, 1.0, (x, G.STAGE[1] - 0.8, zf + 0.5), ink, n=6)
        kit.box(f"standtop{x}", (0.5, 0.03, 0.34), (x, G.STAGE[1] - 0.8, zf + 1.0), ink, rot=(-0.3, 0, 0))


def string_lights(kit):
    """Strands criss-crossing the green on poles, z about 3.4, sagging in the middle."""
    pole = kit.plastic("#5a4636", 0.7)
    wire = kit.plastic("#2a2a2e", 0.6)
    bm = kit.emit("#ffd36b", 7.0)
    W["bulbs"] = []
    strands = []
    for y in (-9.0, -3.5, 2.0, 6.5):
        strands.append(((-11.0, y), (11.0, y)))
    posts = set()
    for a, b in strands:
        posts.add(a)
        posts.add(b)
    for k, (x, y) in enumerate(sorted(posts)):
        kit.cyl(f"pole{k}", 0.09, 3.8, (x, y, 1.9), pole, n=8)
    for si, (a, b) in enumerate(strands):
        n = 13
        pts = []
        for i in range(n + 1):
            u = i / n
            x = a[0] + (b[0] - a[0]) * u
            y = a[1] + (b[1] - a[1]) * u
            z = 3.65 - 0.5 * math.sin(math.pi * u)
            pts.append((x, y, z))
        for i in range(n):
            seg(kit, f"wire{si}_{i}", pts[i], pts[i + 1], 0.025, wire)
        for i in range(1, n):
            W["bulbs"].append(kit.sphere(f"bulb{si}_{i}", 0.1, (pts[i][0], pts[i][1], pts[i][2] - 0.12), bm, seg=8))


def build_clock(kit, x, y):
    """A clock tower facing -x (west). Built in a local frame whose front is -y, then turned."""
    plastic = kit.plastic
    root = kit.empty("clocktower", (x, y, 0), rot=(0, 0, -90 * D2R))
    kit.box("tower", (3.4, 3.4, 9.5), (0, 0, 4.75), kit.grime("#f0e4cc", 0.9, 2.0, "towerm", 0.9), root)
    kit.box("towercap", (4.2, 4.2, 0.5), (0, 0, 9.75), plastic("#a84b3a", 0.7), root)
    kit.box("towerpeak", (2.6, 2.6, 1.6), (0, 0, 10.8), plastic("#a84b3a", 0.7), root)
    fy = -1.7
    kit.cyl("clock.rim", 1.45, 0.12, (0, fy - 0.04, 7.2), plastic("#2d3a5c", 0.5), root, rot=(math.pi / 2, 0, 0), n=32)
    kit.cyl("clock.face", 1.32, 0.12, (0, fy - 0.1, 7.2), plastic("#fff7e6", 0.5), root, rot=(math.pi / 2, 0, 0), n=32)
    ink = plastic("#2d3a5c", 0.5)
    for i in range(12):
        a = i * 30 * D2R
        big = i % 3 == 0
        r = 1.1
        kit.box(f"clock.tick{i}", (0.1 if not big else 0.18, 0.05, 0.2 if not big else 0.34),
                (r * math.sin(a), fy - 0.18, 7.2 + r * math.cos(a)), ink, root, rot=(0, a, 0))
    hh = kit.empty("clock.hour", (0, fy - 0.24, 7.2), root)
    kit.box("clock.hourb", (0.16, 0.05, 0.75), (0, 0, 0.3), ink, hh)
    mh = kit.empty("clock.min", (0, fy - 0.3, 7.2), root)
    kit.box("clock.minb", (0.1, 0.05, 1.05), (0, 0, 0.42), ink, mh)
    W["hour"], W["min"] = hh, mh


def build_bench(kit, name, x, y, face):
    """A bench for two: face = +1 faces +x, -1 faces -x. Seat 3.0 along y."""
    plastic = kit.plastic
    iron = kit.metal("#3c4048", 0.5)
    wood = plastic("#b07c4a", 0.65, spec=0.1)
    root = kit.empty(f"{name}", (x, y, 0), rot=(0, 0, 0 if face > 0 else math.pi))
    # local: faces +x. seat along y
    kit.box(f"{name}.seat", (0.9, 3.0, 0.1), (0, 0, 0.5), wood, root, bevel=0.02)
    kit.box(f"{name}.back", (0.1, 3.0, 0.8), (-0.45, 0, 0.95), wood, root, bevel=0.02)
    for sy in (-1, 1):
        kit.box(f"{name}.leg{sy}", (0.8, 0.1, 0.5), (0, sy * 1.4, 0.25), iron, root)
        kit.box(f"{name}.arm{sy}", (0.85, 0.12, 0.1), (0.0, sy * 1.52, 0.82), iron, root)
        kit.box(f"{name}.armpost{sy}", (0.1, 0.1, 0.32), (0.36, sy * 1.52, 0.66), iron, root)
    return root


def build_band(kit):
    plastic = kit.plastic
    jacket = plastic("#e6e3d6", 0.6, spec=0.2)
    trou = plastic("#16161a", 0.6)
    hatm = plastic("#17171c", 0.6)
    skin = plastic("#171413", 0.8, spec=0.05)
    glove = plastic("#ece9de", 0.6)
    brass = plastic("#d9a62e", 0.28, spec=0.9)
    brass2 = plastic("#e8c050", 0.28, spec=0.9)
    eye = kit.emit("#ffe9a0", 90.0, "bandeye")
    W["pl"] = []
    for i, x in enumerate(G.BAND_X):
        n = f"pl{i}"
        root = kit.empty(n, (x, G.STAGE[1], G.STAGE_Z))
        P = {"root": root}
        for sx in (-1, 1):
            leg = kit.empty(f"{n}.leg{sx}", (sx * 0.16, 0, 1.05), root)
            kit.box(f"{n}.legm{sx}", (0.22, 0.26, 1.05), (0, 0, -0.52), trou, leg, bevel=0.03)
            kit.box(f"{n}.shoe{sx}", (0.24, 0.36, 0.12), (0, -0.05, -1.0), plastic("#0c0c0e", 0.5), leg)
            P[f"leg{sx}"] = leg
        body = kit.empty(f"{n}.body", (0, 0, 1.05), root)
        kit.box(f"{n}.torso", (0.62, 0.34, 0.98), (0, 0, 0.49), jacket, body, bevel=0.04)
        kit.box(f"{n}.belt", (0.64, 0.36, 0.08), (0, 0, 0.04), plastic("#1c1c20", 0.5), body)
        for k in range(3):
            kit.cyl(f"{n}.btn{k}", 0.025, 0.03, (0, -0.18, 0.3 + k * 0.2), brass2, body, rot=(math.pi / 2, 0, 0), n=8)
        for sx in (-1, 1):
            arm = kit.empty(f"{n}.arm{sx}", (sx * 0.4, 0, 0.88), body)
            kit.box(f"{n}.upper{sx}", (0.15, 0.15, 0.72), (0, 0, -0.36), jacket, arm, bevel=0.03)
            fore = kit.empty(f"{n}.fore{sx}", (0, 0, -0.72), arm)
            kit.box(f"{n}.forem{sx}", (0.14, 0.14, 0.52), (0, 0, -0.26), jacket, fore, bevel=0.03)
            kit.box(f"{n}.glove{sx}", (0.17, 0.17, 0.2), (0, 0, -0.6), glove, fore, bevel=0.04)
            P[f"arm{sx}"] = arm
            P[f"fore{sx}"] = fore
        neck = kit.empty(f"{n}.neck", (0, 0, 0.98), body)
        kit.box(f"{n}.neckm", (0.13, 0.13, 0.24), (0, 0, 0.1), skin, neck)
        head = kit.empty(f"{n}.head", (0, 0, 0.2), neck)
        kit.box(f"{n}.headm", (0.3, 0.28, 0.34), (0, 0, 0.17), skin, head, bevel=0.03)
        kit.box(f"{n}.hat", (0.36, 0.34, 0.2), (0, 0.01, 0.4), hatm, head, bevel=0.03)
        brimh = kit.empty(f"{n}.brimh", (0, -0.17, 0.32), head)
        kit.box(f"{n}.brim", (0.42, 0.3, 0.035), (0, -0.14, 0), hatm, brimh, bevel=0.012)
        P["brimh"] = brimh
        e = []
        for sx in (-1, 1):
            e.append(kit.sphere(f"{n}.eye{sx}", 0.045, (sx * 0.075, -0.158, 0.2), eye, head, seg=8))
            e[-1].hide_render = True
        W[f"{n}.eyes"] = e
        P["neck"], P["head"], P["body"] = neck, head, body
        # the horn, hung from the body so it rocks with it
        horn = kit.empty(f"{n}.horn", (0, -0.5, 1.12), body)
        kind = ["trumpet", "trumpet", "cornet", "trombone", "tuba"][i]
        if kind == "tuba":
            kit.cyl(f"{n}.tube", 0.045, 0.7, (0, 0, 0), brass, horn, rot=(math.pi / 2, 0, 0), n=10)
            kit.cyl(f"{n}.bell", 0.05, 0.5, (0, -0.55, 0.32), brass, horn, n=14, r2=0.3)
            kit.cyl(f"{n}.loop", 0.3, 0.07, (0, -0.25, -0.05), brass2, horn, rot=(math.pi / 2, 0, 0), n=18)
        else:
            ln = 0.75 if kind == "trombone" else 0.55
            kit.cyl(f"{n}.tube", 0.03, ln, (0, 0, 0), brass, horn, rot=(math.pi / 2, 0, 0), n=10)
            kit.cyl(f"{n}.bell", 0.04, 0.24, (0, -ln / 2 - 0.1, 0), brass2, horn, rot=(math.pi / 2, 0, 0), n=14, r2=0.15)
            kit.cyl(f"{n}.valve", 0.04, 0.16, (0, 0.02, 0.07), brass, horn, n=8)
        P["horn"] = horn
        W["pl"].append(P)


# ---------------------------------------------------------------------------------------------- the rule meter
DIGIT_SEGS = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd", 6: "afgedc", 7: "abc",
              8: "abcdefg", 9: "abcdfg"}


def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    edge = kit.emit("#2b2118", 0.6, "tagedge")
    plate = kit.emit("#f2e6c8", 0.85, "tagplate")
    ink = kit.emit("#2b2118", 0.6, "tagink")
    gold = kit.emit("#ff9f1c", 1.6, "taggold")
    off = kit.emit("#74675a", 0.7, "tagoff")
    green = kit.emit("#2f9d45", 0.9, "taggreen")

    def b(name, size, loc, mat):
        ob = kit.box(name, size, loc, mat, root)
        noshadow(ob)
        return ob

    def disc(name, r, loc, mat, sc=(1, 1)):
        ob = kit.cyl(name, r, 0.006, loc, mat, root, n=14)
        ob.scale = (sc[0], sc[1], 1)
        noshadow(ob)
        return ob

    b("tag.edge", (1.06, 0.7, 0.006), (0, 0, 0), edge)
    b("tag.plate", (1.0, 0.64, 0.006), (0, 0, 0.007), plate)
    # a double music note (two heads, two stems, a beam) in green
    z = 0.016
    disc("tag.n1", 0.07, (-0.38, 0.0, z), green, (1.25, 0.9))
    disc("tag.n2", 0.07, (-0.14, -0.04, z), green, (1.25, 0.9))
    b("tag.s1", (0.035, 0.34, 0.006), (-0.325, 0.17, z), green)
    b("tag.s2", (0.035, 0.34, 0.006), (-0.085, 0.13, z), green)
    ob = b("tag.beam", (0.3, 0.075, 0.006), (-0.205, 0.335, z), green)
    ob.rotation_euler = (0, 0, -0.1)
    # two seven-segment digits
    W["digits"] = []
    for di, cx in enumerate((0.2, 0.4)):
        dw, dh, t = 0.15, 0.34, 0.045
        cy = 0.1
        pos = {"a": (0, dh / 2 - t / 2, dw, t), "g": (0, 0, dw, t), "d": (0, -dh / 2 + t / 2, dw, t),
               "f": (-dw / 2 + t / 2, dh / 4, t, dh / 2), "b": (dw / 2 - t / 2, dh / 4, t, dh / 2),
               "e": (-dw / 2 + t / 2, -dh / 4, t, dh / 2), "c": (dw / 2 - t / 2, -dh / 4, t, dh / 2)}
        d = {}
        for k, (px, py, sw, sh) in pos.items():
            d[k] = b(f"tag.d{di}{k}", (sw, sh, 0.006), (cx + px, cy + py, z), ink)
        W["digits"].append(d)
    # seven footprints, the last one mine
    W["feet"] = []
    for i in range(7):
        x = -0.42 + i * 0.14
        y = -0.215
        on = [disc(f"tag.f{i}a", 0.036, (x, y + 0.045, z), gold, (0.9, 1.15)),
              disc(f"tag.f{i}b", 0.028, (x, y - 0.04, z), gold, (0.85, 1.0))]
        offs = [disc(f"tag.o{i}a", 0.036, (x, y + 0.045, z + 0.002), off, (0.9, 1.15)),
                disc(f"tag.o{i}b", 0.028, (x, y - 0.04, z + 0.002), off, (0.85, 1.0))]
        W["feet"].append((on, offs))


# ---------------------------------------------------------------------------------------------- the phone
def build_phone(kit):
    """The phone: faces -y in its own frame. Screen shows a photo (v=0) or a video call (v=1)."""
    plastic = kit.plastic
    root = kit.empty("phone", (0, 0, -50))
    W["phone"] = root
    kit.box("phone.body", (0.24, 0.03, 0.48), (0, 0, 0), plastic("#26262c", 0.4, spec=0.6), root, bevel=0.012)
    kit.box("phone.screen", (0.21, 0.01, 0.43), (0, -0.017, 0), kit.emit("#dff3ff", 0.6, "phonescr"), root)

    def px(name, size, loc, mat):
        return kit.box(name, size, (loc[0], -0.026 - loc[1], loc[2]), mat, root)

    em = lambda c, s=0.8: kit.emit(c, s)
    photo, call = [], []
    # photo: a green park behind two heads, me (dark twists, mustard) and Benny (red curls, green shirt)
    photo.append(px("ph.sky", (0.21, 0.004, 0.43), (0, 0, 0), em("#8fd3ff")))
    photo.append(px("ph.grass", (0.21, 0.004, 0.14), (0, 0.003, -0.145), em("#4fc45a")))
    for who, ox, skin, hair, shirt in (("me", -0.052, "#8a5a3a", "#15110f", "#e0a32a"), ("ben", 0.052, "#f0c8a0", "#d9501c", "#3e9e5a")):
        photo.append(px(f"ph.{who}.body", (0.085, 0.004, 0.09), (ox, 0.006, -0.08), em(shirt)))
        photo.append(px(f"ph.{who}.head", (0.075, 0.004, 0.07), (ox, 0.009, -0.002), em(skin)))
        photo.append(px(f"ph.{who}.hair", (0.085, 0.004, 0.032), (ox, 0.012, 0.04), em(hair)))
        for sx in (-1, 1):
            photo.append(px(f"ph.{who}.eye{sx}", (0.009, 0.004, 0.013), (ox + sx * 0.02, 0.012, 0.004), em("#1c120c")))
        photo.append(px(f"ph.{who}.mouth", (0.034, 0.004, 0.02), (ox, 0.012, -0.027), em("#5a1f1a")))
        photo.append(px(f"ph.{who}.teeth", (0.028, 0.004, 0.007), (ox, 0.014, -0.02), em("#fffdf4")))
    # call: Benny big, laughing, on a warm room wall
    call.append(px("cl.bg", (0.21, 0.004, 0.43), (0, 0, 0), em("#f6d8a0")))
    call.append(px("cl.body", (0.17, 0.004, 0.14), (0, 0.004, -0.17), em("#3e9e5a")))
    call.append(px("cl.head", (0.13, 0.004, 0.14), (0, 0.008, -0.01), em("#f0c8a0")))
    call.append(px("cl.hair", (0.145, 0.004, 0.06), (0, 0.012, 0.075), em("#d9501c")))
    for sx in (-1, 1):
        call.append(px(f"cl.curl{sx}", (0.035, 0.004, 0.07), (sx * 0.07, 0.012, 0.03), em("#d9501c")))
        call.append(px(f"cl.eye{sx}", (0.03, 0.004, 0.01), (sx * 0.035, 0.014, 0.012), em("#1c120c")))
        for k in range(3):
            call.append(px(f"cl.fr{sx}{k}", (0.008, 0.004, 0.008), (sx * (0.03 + 0.012 * k), 0.014, -0.012 - 0.004 * (k % 2)), em("#a8663c")))
    call.append(px("cl.mouth", (0.07, 0.004, 0.045), (0, 0.014, -0.05), em("#5a1f1a")))
    call.append(px("cl.teeth", (0.062, 0.004, 0.012), (0, 0.016, -0.034), em("#fffdf4")))
    call.append(px("cl.tongue", (0.034, 0.004, 0.014), (0, 0.016, -0.067), em("#e8707a")))
    W["photo"], W["call"] = photo, call
    return root


def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    plastic = kit.plastic
    lawn = kit.grime("#4fc45a", 0.8, 2.2, "lawn", 0.95)
    lawn2 = kit.grime("#5fd06a", 0.85, 1.2, "lawn2", 0.95)
    # ------------------------------------------------------------------ lights (gains set in animate)
    sun = kit.light("sun", "SUN", (-30, -30, 30), 1.0, "#ffc58a", size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -10, 30), 1.0, "#ffe6cc", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    for k, (x, y) in enumerate([(-6, -5), (6, -5), (0, 0), (-6, 3), (6, 3), (0, 6)]):
        kit.light(f"bulb{k}", "POINT", (x, y, 3.2), 1.0, "#ffd890", size=0.4, shadow=False)
    kit.light("stage", "POINT", (0, G.STAGE[1] + 1.4, 3.1), 1.0, "#ffe2a8", size=0.03, shadow=False)
    rim = kit.light("rim", "SPOT", (0, G.STAGE[1] + 3.2, 3.3), 1.0, "#fff0cc", spot=100, blend=0.5, shadow=False, size=0.03)
    kit.aim(rim, (0, G.STAGE[1] - 2.5, 1.2))
    # a second rim from behind and above the leader, for the band close-ups (gain 0 elsewhere)
    rim2 = kit.light("rim2", "SPOT", (0.9, G.STAGE[1] + 2.6, 4.6), 1.0, "#cfe0ff", spot=60, blend=0.4, shadow=False, size=0.03)
    kit.aim(rim2, (0, G.STAGE[1] - 0.2, 3.3))
    for k_, sx_ in enumerate((-1, 1)):
        r3 = kit.light(f"edge{k_}", "SPOT", (sx_ * 2.4, G.STAGE[1] + 1.9, 3.2), 1.0, "#d8e6ff", spot=70, blend=0.5, shadow=False, size=0.03)
        kit.aim(r3, (sx_ * 0.15, G.STAGE[1] - 0.3, 2.9))
    for nm in ["sun", "fill", "stage", "rim", "rim2", "edge0", "edge1"] + [f"bulb{k}" for k in range(6)]:
        kit.LIGHTS[nm]["obj"].visible_camera = False
    # ------------------------------------------------------------------ ground and roads
    kit.plane("ground", (400, 400), (0, 0, -0.02), lawn2)
    kit.plane("lawn", (20, 24.5), (0, 2.2, 0.0), lawn)
    road = plastic("#6d7078", 0.9, spec=0.05)
    for sx in (-1, 1):
        kit.plane(f"road{sx}", (3.0, 70), (sx * 12.3, 0, 0.012), road)
        kit.plane(f"line{sx}", (0.15, 70), (sx * 12.3, 0, 0.02), plastic("#ffd36b", 0.8, spec=0.05))
    kit.plane("sroad", (50, 3.0), (0, -12.3, 0.014), road)
    kit.plane("path", (2.4, 6.0), (0, 4.8, 0.012), plastic("#e8dcc4", 0.9, spec=0.05))
    kit.plane("lane", (14, 14), (0, 21.0, 0.012), plastic("#d9cdb4", 0.9, spec=0.05))
    # ------------------------------------------------------------------ the shops round the green
    cols = ["#f2a98c", "#8fc9e8", "#f6d27a", "#a8d98f", "#e89ac0", "#c4b2f0"]
    shop(kit, "bank", -12.0, 19.0, "S", 8.0, 6.0, 5.6, "#f6d27a", "coin")
    shop(kit, "bake", 12.0, 19.0, "S", 8.0, 6.0, 5.0, "#f2a98c", "loaf")
    shop(kit, "post", -17.2, 7.0, "E", 8.0, 6.0, 5.0, "#8fc9e8", "mail")
    shop(kit, "cafe", -17.2, -6.0, "E", 8.0, 6.0, 4.8, "#a8d98f", "cup")
    shop(kit, "key", 17.2, -6.0, "W", 8.0, 6.0, 4.8, "#e89ac0", "key")
    shop(kit, "bake2", 17.2, 8.0, "W", 8.0, 6.0, 5.2, "#c4b2f0", "loaf")
    shop(kit, "s1", -6.0, -19.0, "N", 8.0, 6.0, 5.0, "#f6d27a", "cup")
    shop(kit, "s2", 6.0, -19.0, "N", 8.0, 6.0, 5.4, "#8fc9e8", "mail")
    build_clock(kit, 15.7, 1.0)
    for k, (x, y) in enumerate([(-10.6, 12), (10.6, 13), (-10.8, -9), (10.8, -9.5), (-10.8, 2.5), (-7.0, 15.5), (7.0, 15.5)]):
        tree(kit, f"tree{k}", x, y, 6.5 + (k % 3) * 0.6)
    # ------------------------------------------------------------------ the bandstand, the lights, the benches
    bandstand(kit)
    string_lights(kit)
    build_bench(kit, "bench1", G.BENCH1[0], G.BENCH1[1], +1)
    build_bench(kit, "bench2", G.BENCH2[0], G.BENCH2[1], -1)
    # two bench-green strokes scratched into the iron arm beside the empty half (1.5 cm proud)
    sm = plastic("#a8f0b4", 0.5)
    for k in range(2):
        kit.box(f"scratch{k}", (0.025, 0.09, 0.025), (G.BENCH1[0] - 0.12 + k * 0.1, G.BENCH1[1] + 1.52, 0.9), sm)
    # the mail carrier's bag
    kit.box("bag", (0.9, 0.55, 0.36), (G.DANCE["mail"][0], G.DANCE["mail"][1], 0.18), plastic("#7a4a2a", 0.7), bevel=0.08)
    kit.box("bag.flap", (0.92, 0.57, 0.1), (G.DANCE["mail"][0], G.DANCE["mail"][1], 0.36), plastic("#2f5fa8", 0.6), bevel=0.04)
    # ------------------------------------------------------------------ the moving truck
    tr = kit.empty("truck", (12.3, -60, 0))
    W["truck"] = tr
    kit.box("truck.cargo", (2.3, 4.6, 2.6), (0, 0, 1.75), plastic("#f2f0e8", 0.6, spec=0.2), tr, bevel=0.06)
    kit.box("truck.cab", (2.2, 1.6, 1.9), (0, 3.1, 1.3), plastic("#d9684a", 0.5, spec=0.3), tr, bevel=0.06)
    kit.box("truck.win", (1.8, 0.1, 0.7), (0, 3.92, 1.7), plastic("#8fc9e8", 0.15, spec=0.8), tr)
    kit.box("truck.stripe", (2.34, 3.0, 0.3), (0, -0.4, 1.1), plastic("#2d3a5c", 0.6), tr)
    kit.box("truck.doorL", (0.04, 0.04, 2.3), (0, -2.32, 1.75), plastic("#b8b4a6", 0.6), tr)
    for sx in (-1, 1):
        for yy in (-1.5, 3.2):
            kit.cyl(f"truck.w{sx}{yy}", 0.42, 0.3, (sx * 1.1, yy, 0.42), plastic("#1c1c20", 0.8), tr, rot=(0, math.pi / 2, 0), n=14)
    # ------------------------------------------------------------------ the band, the phone, the rule meter, the sun
    build_band(kit)
    build_phone(kit)
    W["disc"] = kit.sphere("sundisc", 10.0, (-14, 170, 9), kit.emit("#fff2c8", 6.0), seg=16)
    noshadow(W["disc"])
    W["disc"].visible_glossy = False
    build_tag(kit)
    return {}


# ---------------------------------------------------------------------------------------------- the cast's extras
def _first_frame(kit, story):
    gh = bpy.data.objects.get("grandpa.headg")
    if gh is not None:
        wm = kit.plastic("#f4f4f2", 0.8)
        kit.box("grandpa.beard", (0.82, 0.1, 0.3), (0, -0.585, -0.4), wm, gh, bevel=0.04)
        kit.box("grandpa.stache", (0.5, 0.08, 0.1), (0, -0.62, -0.2), wm, gh, bevel=0.03)
    gt = bpy.data.objects.get("grandpa.torso")
    if gt is not None:
        red = kit.plastic("#d9483a", 0.6)
        for sx in (-1, 1):
            kit.box(f"grandpa.susp{sx}", (0.16, 0.04, 1.9), (sx * 0.55, -0.525, 1.0), red, gt)
    # the sandwich in his raised hand
    sa = bpy.data.objects.get("sand.arm1")
    if sa is not None:
        sw = kit.empty("sand.sandwich", (0, -0.1, -2.0), sa)
        sw.scale = (1.0, 1.0, 1.0)
        kit.box("sandwich.b1", (0.9, 0.62, 0.2), (0, 0, 0.0), kit.plastic("#e0a860", 0.7), sw, bevel=0.07)
        kit.box("sandwich.l", (0.96, 0.66, 0.08), (0, 0, 0.12), kit.plastic("#4fc45a", 0.7), sw, bevel=0.03)
        kit.box("sandwich.h", (0.92, 0.64, 0.08), (0, 0, 0.2), kit.plastic("#f08a9a", 0.7), sw, bevel=0.03)
        kit.box("sandwich.b2", (0.9, 0.62, 0.2), (0, 0, 0.32), kit.plastic("#e0a860", 0.7), sw, bevel=0.07)
        W["sandwich"] = sw
    ma = bpy.data.objects.get("me.arm1")
    if ma is not None:
        W["me_hand"] = ma
    W["inited"] = True


def _digit(d, n):
    segs = DIGIT_SEGS.get(n, "")
    for k, ob in d.items():
        ob.hide_render = k not in segs


# ---------------------------------------------------------------------------------------------- the dance
BENCH_TARGET = G.BENCH1
LOWKEY = {"S41", "S42", "S43", "S44", "S45", "S46", "S66"}
TAGMACRO = {"S59"}
EDGE = {"S41": 900.0, "S44": 1500.0, "S45": 2000.0, "S66": 1800.0}
DIM = {"S67": (0.0, 0.04, 0.35, 0.1)}
HIDEHORN = {"S43", "S44", "S45", "S46"}
DANCERS = ["grandpa", "bank", "mail", "sand", "t1", "t2", "t3", "t4", "t5", "t6", "t7"]


def _wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def dance_one(who, t, amp, tired, fm, ftarget, W_):
    root = bpy.data.objects.get(who)
    if root is None or amp < 0.01 and tired < 0.01:
        return
    bx, by, byaw = G.DANCE[who]
    ph = (sum(map(ord, who)) % 17) * 0.37
    beat = 2 * math.pi / G.BEAT
    w2 = beat / 2                      # a two-beat cycle
    P = lambda n: bpy.data.objects.get(f"{who}.{n}")
    arm_l, arm_r, leg_l, leg_r, neck = P("arm-1"), P("arm1"), P("leg-1"), P("leg1"), P("neck")
    style = W_["style"].get(who, "bounce")
    s1 = math.sin(w2 * t + ph)
    s2 = math.sin(w2 * t + ph + math.pi)
    bounce = abs(math.sin(beat / 2 * t + ph))
    lean0 = root.rotation_euler.x
    yaw = byaw * D2R
    z_add = 0.0
    aL = aR = 0.0
    sL = sR = 0.2
    lL = lR = 0.0
    hy = hp = 0.0
    if style == "robot":
        q = lambda s: 1.0 if s > 0 else 0.0
        step = math.floor(t / (G.BEAT * 1.0) + ph) % 4
        aL = 1.57 * (1 if step in (0, 1) else 0) * amp
        aR = 1.57 * (1 if step in (1, 2) else 0) * amp
        sL = sR = 0.1
        hy = 0.5 * (1 if step in (0, 3) else -1) * amp
        lL = 0.3 * q(s1) * amp
        lR = 0.3 * q(s2) * amp
        yaw += 0.15 * q(s1) * amp
        z_add = 0.02 * bounce * amp
    elif style == "spin":     # the mail carrier, seated on her bag, spinning
        yaw += (t * 5.4 + ph) * min(1.0, amp * 1.5) if amp > 0.01 else 0
        aL = aR = 0.3 * amp
        sL = sR = 1.25 * amp
        lL = lR = -1.4
        z_add = -0.21
        lean0 = -0.15 * amp
    elif style == "knees":    # grandpa: the knees go on the beat
        pump = (0.5 * math.sin(beat / 2 * t * 2 + ph) * amp)
        lL = pump + 0.1 * s1 * amp
        lR = pump - 0.1 * s1 * amp
        z_add = -0.04 * (1 + math.sin(beat * t + ph)) * amp
        aL = (0.5 + 0.5 * s1) * amp
        aR = (0.5 + 0.5 * s2) * amp
        sL = sR = 0.4 * amp
        yaw += 0.3 * s1 * amp
    elif style == "sandwich":
        aL = (1.0 + 0.8 * s1) * amp
        aR = 1.25
        sL = 0.3
        sR = 0.0
        lL = 0.45 * s1 * amp
        lR = -0.45 * s1 * amp
        z_add = 0.07 * bounce * amp
        hp = 0.14 * math.sin(beat * 0.5 * t) * amp
        yaw += 0.35 * s1 * amp
    elif style == "chair":    # me: stiff as a folding chair, arms straight out
        step = math.floor(t / (G.BEAT * 0.5)) % 2
        aL = aR = 0.15
        sL = sR = 1.5
        lL = lR = 0.0
        z_add = 0.07 * (1 if step else 0) * amp
        yaw += (0.25 if step else -0.25) * amp
        hp = 0.1
        lean0 = -0.04
    else:                     # a plain bounce, arms swinging
        aL = (1.1 + 0.9 * s1) * amp
        aR = (1.1 + 0.9 * s2) * amp
        sL = sR = (0.3 + 0.25 * s2) * amp
        lL = 0.5 * s1 * amp
        lR = -0.5 * s1 * amp
        z_add = 0.07 * bounce * amp
        yaw += 0.5 * s1 * amp + (t * 2.4 + ph * 3) * (1.0 if ph > 3.0 else 0.0) * amp
        hy = 0.3 * math.sin(w2 * t * 0.5 + ph) * amp
    # tired: lower, lean forward, drag the feet
    ta = 1 - 0.6 * tired
    aL, aR = aL * ta, aR * ta
    lean = lean0 + tired * 0.24
    hp += tired * 0.5
    z_add -= tired * 0.03
    yaw_dance = yaw
    if fm > 0.001 and style not in ("spin",):
        tgt = math.atan2(ftarget[0] - root.location.x, -(ftarget[1] - root.location.y))
        yaw = yaw_dance + _wrap(tgt - yaw_dance) * fm
    root.rotation_euler = (lean, 0, yaw)
    root.location.z += z_add
    if arm_l:
        arm_l.rotation_euler = (-aL, sL, 0)
    if arm_r:
        arm_r.rotation_euler = (-aR, -sR, 0)
    if leg_l:
        leg_l.rotation_euler = (lL, 0, 0)
    if leg_r:
        leg_r.rotation_euler = (lR, 0, 0)
    if neck:
        neck.rotation_euler = (neck.rotation_euler.x + hp, 0, neck.rotation_euler.z + hy)


STYLE = {"grandpa": "knees", "bank": "robot", "mail": "spin", "sand": "sandwich"}


def band_pose(t, tl):
    b = sample("band", tl, t, {"u": 0.0, "play": 0.0, "brim": 0.0, "eyes": 0.0, "turn": 0.0, "hush": 0.0})
    u, play = b["u"], b["play"]
    moving = 0.002 < u < 0.998
    beat = 2 * math.pi / G.BEAT
    for i, P in enumerate(W["pl"]):
        root = P["root"]
        y = G.STAGE[1] + (G.BAND_OFF_Y - G.STAGE[1]) * (1 - u)
        root.location = (G.BAND_X[i], y, G.STAGE_Z * ss((15.4 - y) / 1.4))
        root.rotation_euler = (0, 0, math.pi * b["turn"])
        sw = 0.55 * math.sin(2 * math.pi * 0.85 * t + i * 0.7) if moving else 0.0
        P["leg-1"].rotation_euler = (sw, 0, 0)
        P["leg1"].rotation_euler = (-sw, 0, 0)
        ph = i * 0.9
        p = play
        s_ = 0.05 + 0.85 * p
        tt = 0.05 + 3.5 * p
        for sx in (-1, 1):
            arm, fore = P[f"arm{sx}"], P[f"fore{sx}"]
            swing = 0.0 if p > 0.5 else (-sw * sx * 0.6 if moving else 0.0)
            arm.rotation_euler = (-(s_) + swing, 0, -sx * 0.5 * p)
            fore.rotation_euler = (-(tt - s_), 0, 0)
        # the horn: at the mouth while playing, hanging by the hand when lowered
        h = P["horn"]
        h.location = (0.0 + (1 - p) * 0.46, -0.5 * p - 0.1 * (1 - p), 1.12 * p + 0.2 * (1 - p))
        h.rotation_euler = (-(1 - p) * 1.4, 0, 0)
        if i == 2 and W.get("sid") in HIDEHORN:   # the bell would sit in front of the face the close-up is about
            h.location = (0.0, -0.1, -0.9)
        rock = 0.03 * math.sin(beat * t / 2 + ph) * p
        P["body"].rotation_euler = (0.06 + rock, 0, 0.04 * math.sin(beat * t / 4 + ph) * p)
        P["neck"].rotation_euler = (0.5 - (0.34 * b["brim"] if i == 2 else 0.0) + 0.04 * math.sin(beat * t + ph) * p, 0, 0)
        brim = 0.5 - (0.42 * b["brim"] if i == 2 else 0.0)
        P["brimh"].rotation_euler = (brim, 0, 0)
        if i == 2:
            for e in W["pl2.eyes"]:
                e.hide_render = b["eyes"] < 0.5


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
        W["style"] = dict(STYLE)
        W["style"]["me"] = "chair"
    look = look_at(tl, t)
    gains = {}
    # the sun and fill
    sd = Vector(look["sd"]).normalized()
    so = kit.LIGHTS["sun"]["obj"]
    so.location = sd * 60
    kit.aim(so, (0, 0, 0))
    kit.LIGHTS["sun"]["light"].color = look["sun_col"]
    kit.LIGHTS["fill"]["light"].color = look["fill_col"]
    gains["sun"], gains["fill"] = look["sun"], look["fill"]
    for k in range(6):
        gains[f"bulb{k}"] = look["bulbs"]
    gains["stage"], gains["rim"] = look["stage"], look["rim"]
    shot0 = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    sid = shot0["id"]
    # the band close-ups: no key light, only the rim, and none of the bulbs behind the hat
    lowkey = sid in LOWKEY
    gains["rim2"] = 0.0
    gains["edge0"] = gains["edge1"] = 0.0
    W["sid"] = sid
    if sid in DIM:     # the white-lit bandstand held down so the cuts to and from navy don't flash
        gains["stage"] *= DIM[sid][0]
        gains["rim"] *= DIM[sid][1]
        gains["fill"] *= DIM[sid][2]
        for k in range(6):
            gains[f"bulb{k}"] *= DIM[sid][3]
    if lowkey:
        for k in range(6):
            gains[f"bulb{k}"] = 0.0
        gains["stage"] = 0.0
        gains["sun"] = 0.0
        gains["fill"] = look["fill"] * 0.5
        gains["rim"] = 600.0
        gains["rim2"] = 2200.0
        if sid == "S41":
            gains["rim"], gains["rim2"] = 0.0, 500.0
        if sid in EDGE:
            gains["edge0"] = gains["edge1"] = EDGE[sid]
    for ob in W["eave_bulbs"] + W["bulbs"]:
        ob.hide_render = lowkey
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*look["sky"], 1.0)
    bg.inputs["Strength"].default_value = look["sky_str"]
    W["disc"].hide_render = look["disc"] < 0.01
    W["disc"].location = (-14, 170, 9) if look["disc"] >= 0.01 else (-14, 170, -400)
    # the clock and the truck
    ck = sample("clock", tl, t, {"h": 12.0})
    W["hour"].rotation_euler = (0, (ck["h"] % 12) * 30 * D2R, 0)
    W["min"].rotation_euler = (0, ((ck["h"] * 60) % 60) * 6 * D2R, 0)
    tk = sample("truck", tl, t, {"y": -60.0})
    W["truck"].location = (12.3, tk["y"], 0)
    # the tag
    sg = sample("song", tl, t, {"n": 1.0})
    n = int(round(sg["n"]))
    _digit(W["digits"][0], (n // 10) if n >= 10 else -1)
    _digit(W["digits"][1], n % 10)
    ft = sample("feet", tl, t, {"n": 6.0})
    for i, (on, offs) in enumerate(W["feet"]):
        lit = ft["n"] > i + 0.5
        for ob in on:
            ob.hide_render = not lit
        for ob in offs:
            ob.hide_render = lit
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
    s = 0.58 * w2
    tag.scale = (s, s, s)
    tag.location = (-0.45 * w2, 0.60 * h2, -dist)
    if sid in TAGMACRO:   # the footprint row, close: the tag blown up so the seven glyphs fill the width
        tag.scale = (s * 3.1, s * 3.1, s * 3.1)
        tag.location = (0.0, 0.38 * h2, -dist)
    # the phone: on my hand (photo) or on my chest (call)
    pv = sample("phone", tl, t, {"where": 0.0, "screen": 0.0, "x": 0.0, "y": 0.0, "z": 0.0, "rot": 0.0, "lie": 0.0, "tilt": 0.0})
    ph = W["phone"]
    if pv["where"] < 0.5:
        ph.location = (0, 0, -50)
    else:
        ph.location = (pv["x"], pv["y"], pv["z"])
        ph.rotation_euler = ((-math.pi / 2) if pv["lie"] > 0.5 else pv["tilt"] * D2R, 0, pv["rot"] * D2R)
    for ob in W["photo"]:
        ob.hide_render = pv["screen"] > 0.5
    for ob in W["call"]:
        ob.hide_render = pv["screen"] < 0.5
    # the town: how hard it dances, how tired, which way it faces
    dn = sample("dance", tl, t, {"amp": 1.0, "tired": 0.0})
    fc = sample("face", tl, t, {"m": 0.0, "tx": G.BENCH1[0], "ty": G.BENCH1[1]})
    s6 = sample("sit6", tl, t, {"s": 0.0})["s"]
    for who in DANCERS + ["me"]:
        r_ = bpy.data.objects.get(who)
        if r_ is not None:   # lying on the back: lift the body half its thickness off the grass
            r_.location.z += 0.27 * min(1.0, max(0.0, -r_.rotation_euler.x / 1.4))
    lay = sample("lying", tl, t, {"k": 0.0})["k"]
    for who in DANCERS:
        if lay > 0.5 and who != "t6":
            _laugh(who, t)
            continue
        if who == "t6" and s6 > 0.01:
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"t6.leg{sx}")
                if leg:
                    leg.rotation_euler = (leg.rotation_euler.x * (1 - s6) + (-math.pi / 2 * 0.97) * s6, 0, 0)
            if s6 > 0.5:
                continue
        dance_one(who, t, dn["amp"], dn["tired"], fc["m"], (fc["tx"], fc["ty"]), W)
    # me: sitting, then up and dancing
    me = bpy.data.objects.get("me")
    sit = sample("sit", tl, t, {"s": 1.0})["s"]
    md = sample("medance", tl, t, {"amp": 0.0})["amp"]
    if me is not None:
        if lay > 0.5:
            _laugh("me", t)
        elif md > 0.01:
            _dance_me(t, md)
        if sit > 0.001:
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"me.leg{sx}")
                if leg:
                    cur = leg.rotation_euler.x
                    leg.rotation_euler = (cur * (1 - sit) + (-math.pi / 2 * 0.97) * sit, 0, 0)
    # lying down: the feet are the root, so a lean of -90 puts the back on the grass (set by the acting keys)
    band_pose(t, tl)
    return gains


def _laugh(who, t):
    """On the back, laughing: arms waving in the air, legs kicking, the chest shaking, the head up toward the camera."""
    root = bpy.data.objects.get(who)
    ph = (sum(map(ord, who)) % 17) * 0.9
    s1 = math.sin(7.0 * t + ph)
    s2 = math.sin(6.0 * t + ph + 1.7)
    P = lambda n: bpy.data.objects.get(f"{who}.{n}")
    if P("arm-1"):
        P("arm-1").rotation_euler = (-(1.5 + 0.6 * s1), 0.5, 0)
    if P("arm1"):
        P("arm1").rotation_euler = (-(1.5 + 0.6 * s2), -0.5, 0)
    if P("leg-1"):
        P("leg-1").rotation_euler = (0.5 * s2, 0, 0)
    if P("leg1"):
        P("leg1").rotation_euler = (-0.5 * s1, 0, 0)
    if P("neck"):
        P("neck").rotation_euler = (P("neck").rotation_euler.x + 0.95, 0, 0.25 * s1)
    root.rotation_euler = (root.rotation_euler.x + 0.05 * s1, 0, root.rotation_euler.z)


def _dance_me(t, amp):
    root = bpy.data.objects.get("me")
    beat = 2 * math.pi / G.BEAT
    sn = math.sin(2 * math.pi * t / G.BEAT)      # smooth, so a big close figure doesn't flash on a pose snap
    root.location.z += 0.04 * (1 + sn) * amp
    root.rotation_euler = (root.rotation_euler.x, 0, root.rotation_euler.z + 0.28 * sn * amp)
    al, ar = bpy.data.objects.get("me.arm-1"), bpy.data.objects.get("me.arm1")
    if al:
        al.rotation_euler = (-0.15, 1.5 * amp, 0)
    if ar:
        ar.rotation_euler = (-0.15, -1.5 * amp, 0)
    for sx in (-1, 1):
        leg = bpy.data.objects.get(f"me.leg{sx}")
        if leg:
            leg.rotation_euler = (0.0, 0, 0)
    neck = bpy.data.objects.get("me.neck")
    if neck:
        neck.rotation_euler = (neck.rotation_euler.x + 0.1 * amp, 0, neck.rotation_euler.z + 0.2 * math.sin(beat * t / 2) * amp)
