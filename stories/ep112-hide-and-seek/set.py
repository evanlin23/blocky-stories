"""ep112 "hide and seek": Grandma's big green back yard on a bright summer afternoon.

Rule meter: a cream tag in the top-left of every frame (a round eye glyph, then a game clock, years : days, 31 : 204).
It is a child of the camera. At L14 the eye flips to a green tick and the clock stops; at L19 it resets to 0 : 0 and the
eye comes back in a new colour. No letters anywhere, only the glyph and numerals.
Cues (story.json) drive: mv (move anything registered: the salad bowl, the fork, the falling mustache, the shed door),
clock (years y, days d), eye (0 teal eye, 1 tick, 2 orange eye), pulse (the tag bumps), photo (the old group photo on
Grandma's palm), gst (Glenn's mustache on his lip), mst (my mustache), sit (who is seated).
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {"obj": {}, "init": {}}
BROWN = "#6b4226"


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def reg(name, ob):
    W["obj"][name] = ob
    W["init"][name] = (ob.location.x, ob.location.y, ob.location.z, ob.rotation_euler.z)
    return ob


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


# ---------------------------------------------------------------------------------------------- parts
def tree(kit, name, x, y, h=6.0, tint="#c8f0a0"):
    try:
        kit.prop("commontree_1", (x, y, 0), height=h, tint=tint)
    except Exception:
        kit.cyl(f"{name}.trunk", 0.3, h * 0.45, (x, y, h * 0.22), kit.plastic("#7a5230", 0.8), n=8)
        kit.sphere(f"{name}.crown", h * 0.28, (x, y, h * 0.68), kit.plastic("#5fae4a", 0.8), seg=10)


def bush(kit, name, x, y, h=0.9, tint="#bfe58a"):
    try:
        kit.prop("bush_1", (x, y, 0), height=h, tint=tint)
    except Exception:
        kit.sphere(name, h * 0.55, (x, y, h * 0.4), kit.plastic("#5fbf4a", 0.8), seg=10)


def table(kit, nm, cx, cy):
    P = kit.plastic
    wood = P("#c28a55", 0.75, spec=0.08)
    woodd = P("#9c6a3e", 0.8, spec=0.05)
    cloth = kit.checker("#e84a4a", "#fff6f0", 4.0, "cloth")
    kit.box(f"{nm}.top", (2.7, 1.05, 0.07), (cx, cy, 0.78), cloth)
    kit.box(f"{nm}.rim", (2.76, 1.1, 0.05), (cx, cy, 0.735), wood)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"{nm}.leg{sx}{sy}", (0.09, 0.09, 0.74), (cx + sx * 1.15, cy + sy * 0.36, 0.37), woodd)
    for sy in (-1, 1):
        by = cy + sy * G.FAR
        kit.box(f"{nm}.seat{sy}", (2.8, 0.3, 0.07), (cx, by, 0.425), wood)
        kit.box(f"{nm}.apron{sy}", (2.8, 0.05, 0.22), (cx, by - 0.125, 0.30), wood)
        for sx in (-1, 1):
            kit.box(f"{nm}.bleg{sx}{sy}", (0.1, 0.28, 0.4), (cx + sx * 1.25, by, 0.2), woodd)


def salad_bowl(kit, name, x, y, z, r):
    P = kit.plastic
    root = kit.empty(name, (x, y, z))
    kit.cyl(f"{name}.body", r, r * 0.62, (0, 0, r * 0.31), P("#fffaf0", 0.35, spec=0.5), root, n=24, r2=r * 0.7)
    kit.cyl(f"{name}.rim", r * 1.04, 0.035, (0, 0, r * 0.62), P("#ffffff", 0.3, spec=0.5), root, n=24)
    m = kit.sphere(f"{name}.mound", r * 0.98, (0, 0, r * 0.52), P("#f8e79a", 0.85, spec=0.05), root, seg=14)
    m.scale = (1.0, 1.0, 0.5)
    cube = P("#fff3b8", 0.8, spec=0.05)
    green = P("#6fbf4a", 0.7)
    orange = P("#ff8a3a", 0.6)
    for k in range(16):
        a = k * 2.4
        rr = r * (0.2 + 0.07 * (k % 9))
        h = r * 0.52 + math.sqrt(max(0.0, (r * 0.98) ** 2 - rr ** 2)) * 0.5 - r * 0.03
        mat = green if k % 5 == 0 else (orange if k % 7 == 0 else cube)
        kit.box(f"{name}.c{k}", (r * 0.16, r * 0.16, r * 0.14), (math.cos(a) * rr, math.sin(a) * rr, h), mat, root,
                rot=(0.3 * k, 0.2, a), bevel=0.01)
    return root


def stache(kit, name, parent, s=1.0, z=0.0, y=0.0, tilt=0.09):
    """The mustache: a fat bar and two curled-down ends. s=1 in rig units (a head is 1.24 wide)."""
    m = kit.plastic(BROWN, 0.8)
    root = kit.empty(name, (0, y, z), parent, rot=(0, tilt, 0))
    kit.box(f"{name}.bar", (1.12 * s, 0.17 * s, 0.26 * s), (0, 0, 0.0), m, root, bevel=0.05)
    for sx in (-1, 1):
        kit.box(f"{name}.dr{sx}", (0.2 * s, 0.17 * s, 0.46 * s), (sx * 0.55 * s, 0, -0.17 * s), m, root, bevel=0.05)
        kit.box(f"{name}.tp{sx}", (0.14 * s, 0.17 * s, 0.22 * s), (sx * 0.62 * s, 0, -0.45 * s), m, root, bevel=0.04)
    return root


def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    P = kit.plastic
    grass = kit.grime("#62cf55", 0.8, 1.6, "grass", 0.95)
    stripe = P("#76dc62", 0.95, spec=0.02)
    white = P("#fbf8f0", 0.8, spec=0.05)
    wood = P("#c28a55", 0.75, spec=0.08)
    woodd = P("#9c6a3e", 0.8, spec=0.05)

    # lights: sun from the camera side, a soft fill and a warm front
    az, el = 205.0 * D2R, 48.0 * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    sun = kit.light("sun", "SUN", tuple(d * 60), 2.5, "#fff0d8", size=0.06)
    sun.data.angle = 0.06
    kit.aim(sun, (0, 0, 0))
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#cfe6ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    front = kit.light("front", "SUN", (-10, -30, 20), 0.7, "#ffe4c8", shadow=False)
    front.data.angle = 0.4
    kit.aim(front, (0, 0, 0))
    front2 = kit.light("front2", "SUN", (10, 30, 20), 0.4, "#fffaf0", shadow=False)
    front2.data.angle = 0.4
    kit.aim(front2, (0, 0, 0))

    # ground and mowing stripes
    kit.plane("ground", (1500, 500), (100, 0, -0.02), grass)
    for i in range(10):
        kit.box(f"stripe{i}", (2.6, 24.0, 0.02), (-14.0 + i * 5.2, 5.0, 0.0), stripe)

    # the white fence to the neighbor's yard
    for k in range(76):
        x = -17.0 + k * 0.3
        kit.box(f"pick{k}", (0.14, 0.06, 1.15), (x, G.FENCE_Y, 0.58), white, bevel=0.015)
    for z in (0.35, 0.85):
        kit.box(f"frail{z}", (23.0, 0.08, 0.1), (-5.6, G.FENCE_Y + 0.07, z), white)
    for k in range(0, 9):
        kit.box(f"fpost{k}", (0.16, 0.16, 1.3), (-17.0 + k * 2.9, G.FENCE_Y + 0.05, 0.65), white)
    kit.box("fraiL", (23.0, 0.2, 0.06), (-5.6, G.FENCE_Y, 1.2), white)

    # the neighbor's yellow house
    nx, ny = G.NH
    yellow = P("#ffd84a", 0.85, spec=0.05)
    kit.box("nh.body", (9.0, 6.0, 4.2), (nx, ny, 2.1), yellow)
    roof = P("#c9604a", 0.7, spec=0.1)
    for sy in (-1, 1):
        kit.box(f"nh.roof{sy}", (10.2, 4.4, 0.3), (nx, ny + sy * 1.85, 4.85), roof, rot=(-sy * 0.5, 0, 0))
    glass = P("#8fc8ee", 0.2, spec=0.8)
    for wx in (-8.0, -1.6):
        kit.box(f"nh.wf{wx}", (1.5, 0.08, 1.7), (wx, ny - 3.03, 2.4), white)
        kit.box(f"nh.wg{wx}", (1.2, 0.08, 1.4), (wx, ny - 3.07, 2.4), glass)
    kit.box("nh.door", (1.2, 0.1, 2.2), (-5.5, ny - 3.05, 1.2), P("#3a86e0", 0.5, spec=0.3))
    kit.box("nh.deck", (4.4, 1.4, 0.3), (-5.5, ny - 3.7, 0.15), wood)
    for px in (-7.5, -3.5):
        kit.box(f"nh.post{px}", (0.14, 0.14, 2.5), (px, ny - 4.3, 1.55), white)
    kit.box("nh.proof", (4.8, 1.8, 0.16), (-5.5, ny - 3.8, 2.85), roof)
    # his mailbox on a post by the fence
    mx, my = G.MAILBOX
    kit.box("mb.post", (0.1, 0.1, 1.1), (mx, my, 0.55), woodd)
    kit.box("mb.box", (0.55, 0.32, 0.3), (mx, my, 1.25), P("#3a86e0", 0.45, spec=0.3))
    kit.box("mb.flag", (0.05, 0.05, 0.28), (mx + 0.3, my, 1.35), P("#e84a4a", 0.5))

    # Grandma's house, the porch, and the dark gap under it
    gx, gy = G.GH
    kit.box("gh.body", (10.0, 6.0, 4.6), (gx, gy, 2.3), P("#fff0d4", 0.85, spec=0.05))
    groof = P("#d65a48", 0.7, spec=0.1)
    for sy in (-1, 1):
        kit.box(f"gh.roof{sy}", (11.2, 4.4, 0.3), (gx, gy + sy * 1.9, 5.2), groof, rot=(-sy * 0.5, 0, 0))
    kit.box("gh.door", (1.4, 0.1, 2.3), (gx, 10.95, 1.8), P("#2fb5a8", 0.5, spec=0.3))
    for wx in (gx - 3.2, gx + 3.2):
        kit.box(f"gh.wf{wx}", (1.5, 0.08, 1.7), (wx, 10.96, 2.5), white)
        kit.box(f"gh.wg{wx}", (1.2, 0.08, 1.4), (wx, 10.92, 2.5), glass)
    px, py = G.PORCH
    kit.box("deck", (8.6, 2.6, 0.2), (px, py, 0.55), wood)
    kit.box("under", (8.4, 2.2, 0.46), (px, py + 0.2, 0.23), P("#4b3829", 0.95, spec=0.02))
    for sx in (-1, 1):
        kit.box(f"pp{sx}", (0.2, 0.2, 2.8), (px + sx * 4.1, py - 1.15, 2.05), white)
    kit.box("proof", (9.0, 3.0, 0.18), (px, py - 0.1, 3.5), groof)
    for i in range(2):
        kit.box(f"pstep{i}", (1.8, 0.5 + 0.0 * i, 0.22 * (i + 1)), (px, 8.1 - i * 0.45, 0.11 * (i + 1)), wood)

    # the old shed, sagging, with a door that can swing
    sx_, sy_ = G.SHED
    gray = P("#b3ab9c", 0.9, spec=0.03)
    kit.box("shed.body", (3.0, 2.4, 2.5), (sx_, sy_, 1.25), gray, rot=(0, 0.02, 0.0))
    kit.box("shed.roof", (3.5, 3.0, 0.16), (sx_, sy_, 2.62), P("#8f877a", 0.8, spec=0.05), rot=(0.1, 0.05, 0.0))
    kit.box("shed.roof2", (3.5, 1.4, 0.16), (sx_ + 0.05, sy_ - 1.5, 2.45), P("#7f776a", 0.8, spec=0.05), rot=(0.35, 0.05, 0.0))
    batten = P("#968e80", 0.9, spec=0.03)
    for k in range(7):
        bx = sx_ - 1.35 + k * 0.38
        if bx > sx_ + 0.3:
            continue
        kit.box(f"shed.b{k}", (0.07, 0.03, 2.4), (bx, 7.4 - 0.012, 1.25), batten)
    kit.box("shed.dark", (0.95, 0.04, 1.9), (sx_ + 1.0, 7.4 - 0.005, 0.97), P("#1b1410", 0.95, spec=0.0))
    leaf = kit.empty("shedd", (sx_ + 1.5, 7.4 - 0.04, 0), None)
    kit.box("shedd.leaf", (0.96, 0.08, 1.9), (-0.48, 0, 0.97), P("#7a7164", 0.85, spec=0.03), leaf)
    kit.box("shedd.cross", (0.96, 0.05, 0.12), (-0.48, -0.06, 1.3), P("#565b61", 0.9), leaf)
    kit.box("shedd.cross2", (0.96, 0.05, 0.12), (-0.48, -0.06, 0.5), P("#565b61", 0.9), leaf)
    reg("shedd", leaf)

    # tables, grill, string lights
    table(kit, "ta", *G.TA)
    table(kit, "tb", *G.TB)
    # the tally: two strokes scratched into the outer face of table A's far bench's left end board, low down
    ex_ = G.TA[0] - 1.44
    kit.box("endboard", (0.04, 0.3, 0.3), (ex_, G.TA[1] + G.FAR, 0.27), P("#c28a55", 0.75, spec=0.08))
    for k, off in enumerate((-0.05, 0.04)):
        kit.box(f"tally{k}", (0.012, 0.035, 0.18), (ex_ - 0.026, G.TA[1] + G.FAR + off, 0.26), P("#ffe27a", 0.7))
    kit.sphere("grill.b", 0.42, (11.5, 2.0, 0.95), P("#d94a3a", 0.35, spec=0.5), seg=14)
    kit.cyl("grill.cap", 0.12, 0.08, (11.5, 2.0, 1.38), P("#2a2d33", 0.5), n=12)
    for k in range(3):
        a = k * 2.094
        kit.cyl(f"grill.l{k}", 0.03, 0.62, (11.5 + math.cos(a) * 0.28, 2.0 + math.sin(a) * 0.28, 0.3), P("#2a2d33", 0.5), n=8)
    cols = ["#ffd23f", "#ff6f5e", "#6fd0ff", "#9be564"]
    for px_ in (-10.0, 3.4):
        kit.cyl(f"pole{px_}", 0.05, 3.5, (px_, 5.6, 1.75), P("#6a4a2e", 0.8), n=8)
    for k in range(15):
        u = k / 14.0
        bx = -10.0 + u * 13.4
        bz = 3.35 - 0.55 * math.sin(math.pi * u)
        kit.sphere(f"bulb{k}", 0.1, (bx, 5.6, bz), kit.emit(cols[k % 4], 3.0), seg=8)
    # trees and bushes
    for i, (x, y, h) in enumerate(((-13.5, 8.0, 6.5), (-12.0, 15.0, 7.0), (-9.0, 28.0, 8.0), (-1.0, 28.0, 8.5), (-9.0, -11.0, 7.0), (-2.0, -12.0, 7.5), (5.0, -11.0, 6.5), (12.0, -9.0, 7.0),
                                   (7.0, 27.0, 8.0), (16.5, 1.5, 6.5), (15.5, 20.0, 7.5), (-15.0, 25.0, 7.5))):
        tree(kit, f"tr{i}", x, y, h)
    for i, x in enumerate(v for v in range(-15, 4, 3) if not -5 <= v <= 1):
        bush(kit, f"bu{i}", x + 0.5, G.FENCE_Y - 0.9, 0.9 if i % 2 else 1.1)
    # Glenn's flashlight on the fence rail (rests, not held)
    kit.cyl("flash.b", 0.035, 0.22, (-1.45, G.FENCE_Y - 0.02, 1.32), P("#2a2d33", 0.4), rot=(math.pi / 2, 0, 0.0), n=10)
    kit.cyl("flash.h", 0.05, 0.07, (-1.45, G.FENCE_Y - 0.14, 1.32), P("#ffe9a0", 0.3), rot=(math.pi / 2, 0, 0.0), n=10)

    # food and things that move
    bw = salad_bowl(kit, "bowl", G.TB[0] + 0.8, G.TB[1], 0.815, 0.34)
    reg("bowl", bw)
    gb = salad_bowl(kit, "gbowl", G.TA[0] - 0.7, G.TA[1] + 0.3, 0.815, 0.27)
    reg("gbowl", gb)
    # a few plates and cups on the cloth
    pcols = ["#ffd23f", "#6fd0ff", "#6fd0ff", "#ffd23f"]
    for i, (x, y) in enumerate(((G.TB[0] - 0.8, G.TB[1] - 0.2), (G.TB[0] + 0.0, G.TB[1] + 0.2), (G.TA[0] + 0.85, G.TA[1] + 0.15),
                                (G.TA[0] + 1.0, G.TA[1] - 0.3))):
        kit.cyl(f"plate{i}", 0.2, 0.02, (x, y, 0.825), P(pcols[i], 0.35, spec=0.5), n=20)
    kit.cyl("cup0", 0.07, 0.14, (G.TA[0] - 0.2, G.TA[1] - 0.3, 0.89), P("#ff6f5e", 0.4), n=12, r2=0.055)
    kit.cyl("cup1", 0.07, 0.14, (G.TB[0] + 0.3, G.TB[1] - 0.25, 0.89), P("#6fd0ff", 0.4), n=12, r2=0.055)
    fk = kit.empty("fork", (0.0, 0.0, -60.0))
    steel = kit.metal("#aab2ba", 0.3)
    kit.box("fork.h", (0.05, 0.34, 0.02), (0, 0.06, 0), P("#e84a4a", 0.4), fk, bevel=0.008)
    for k in (-1, 0, 1):
        kit.box(f"fork.t{k}", (0.018, 0.17, 0.02), (k * 0.034, -0.2, 0), steel, fk)
    kit.box("fork.hd", (0.115, 0.05, 0.02), (0, -0.11, 0), steel, fk)
    reg("fork", fk)
    fs = kit.empty("fst", (0.0, 0.0, -60.0))
    stache(kit, "fst.m", fs, 0.34 * 1.0, 0.0, 0.0)
    reg("fst", fs)
    build_tag(kit)
    return {}


# ---------------------------------------------------------------------------------------------- the rule meter
SEGN = "abcdefg"
DIG = {0: "abcdef", 1: "bc", 2: "abdeg", 3: "abcdg", 4: "bcfg", 5: "acdfg", 6: "acdefg", 7: "abc", 8: "abcdefg", 9: "abcdfg"}
SEGL = [("a", 0.0, 0.185, 0.095, 0.045), ("b", 0.05, 0.095, 0.045, 0.17), ("c", 0.05, -0.095, 0.045, 0.17),
        ("d", 0.0, -0.185, 0.095, 0.045), ("e", -0.05, -0.095, 0.045, 0.17), ("f", -0.05, 0.095, 0.045, 0.17),
        ("g", 0.0, 0.0, 0.095, 0.045)]


def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    plate = kit.emit("#fff1cf", 1.0, "tagplate")
    edge = kit.emit("#2a1a0e", 0.5, "tagedge")
    ink = kit.emit("#2a1a0e", 0.5, "tagink")
    white = kit.emit("#ffffff", 1.0, "tagwhite")
    irisA = kit.emit("#1f86e8", 1.0, "tagirisA")
    irisB = kit.emit("#ff7a1e", 1.2, "tagirisB")
    tick = kit.emit("#14b84a", 1.2, "tagtick")

    def b(name, size, loc, mat, rot=(0, 0, 0)):
        ob = kit.box(name, size, loc, mat, root, rot=rot)
        noshadow(ob)
        return ob

    def ell(name, r, loc, mat, sx, sy):
        sp = kit.sphere(name, r, loc, mat, root, seg=16)
        sp.scale = (sx, sy, 0.02)
        noshadow(sp)
        return sp
    b("tag.edge", (1.56, 0.66, 0.004), (0, 0, 0.0), edge)
    b("tag.plate", (1.5, 0.6, 0.004), (0, 0, 0.004), plate)
    ex = -0.5
    W["eye"] = []
    W["eye"].append(ell("tag.eo", 0.2, (ex, 0, 0.008), edge, 1.0, 0.72))
    W["eye"].append(ell("tag.ew", 0.18, (ex, 0, 0.010), white, 1.0, 0.68))
    W["irisA"] = ell("tag.iA", 0.105, (ex, 0, 0.012), irisA, 1.0, 1.0)
    W["irisB"] = ell("tag.iB", 0.105, (ex, 0, 0.012), irisB, 1.0, 1.0)
    W["eye"].append(ell("tag.ep", 0.052, (ex, 0, 0.014), ink, 1.0, 1.0))
    W["tick"] = [b("tag.k1", (0.14, 0.08, 0.004), (ex - 0.1, -0.04, 0.012), tick, (0, 0, -0.75)),
                 b("tag.k2", (0.34, 0.08, 0.004), (ex + 0.07, 0.02, 0.012), tick, (0, 0, 0.85))]
    W["seg"] = []
    for g, n in (("L", 2), ("R", 3)):
        grp = []
        for d in range(n):
            row = []
            for nm, x, z, w_, h_ in SEGL:
                ob = b(f"tag.{g}{d}{nm}", (w_, h_, 0.004), (x, z, 0.012), ink)
                ob["bx"] = x
                row.append(ob)
            grp.append(row)
        W["seg"].append(grp)
    W["colon"] = [b("tag.col0", (0.05, 0.05, 0.004), (0, 0.075, 0.012), ink), b("tag.col1", (0.05, 0.05, 0.004), (0, -0.075, 0.012), ink)]


def _hide(ob, hide):
    ob.hide_render = hide
    for c in ob.children_recursive:
        c.hide_render = hide


def _first_frame(kit, story):
    W["inited"] = True
    P = kit.plastic
    gl = bpy.data.objects.get("glenn.headg")
    W["gst"] = []
    if gl is not None:
        W["gst"].append(stache(kit, "glenn.st", gl, 1.0, -0.2, -0.74, 0.09))
        sg = P("#1e1f24", 0.3, spec=0.6)
        for sx in (-1, 1):
            W["gst"].append(kit.box(f"glenn.sgl{sx}", (0.46, 0.1, 0.24), (sx * 0.26, -0.55, 0.62), sg, gl, bevel=0.05))
        W["gst"].append(kit.box("glenn.sgb", (0.12, 0.1, 0.05), (0, -0.55, 0.66), sg, gl))
        sgs = W["gst"][1:]
    up = bpy.data.objects.get("glenn.upper") or bpy.data.objects.get("glenn.torso")
    if up is not None:
        cols = ["#ff7aa8", "#ffffff", "#ffd23f", "#ff9a5a"]
        for i, (fx, fz) in enumerate(((-0.62, 0.35), (0.12, 0.7), (0.65, 0.3), (-0.2, 1.1), (0.55, 1.25), (-0.65, 1.62), (0.12, 1.62))):
            kit.cyl(f"glenn.fl{i}", 0.17, 0.05, (fx, -0.53, fz), P(cols[i % 4], 0.5), up, rot=(math.pi / 2, 0, 0), n=10)
            kit.cyl(f"glenn.fc{i}", 0.07, 0.06, (fx, -0.55, fz), P("#ffb020", 0.5), up, rot=(math.pi / 2, 0, 0), n=8)
    me = bpy.data.objects.get("me.headg")
    W["mst"] = []
    if me is not None:
        W["mst"].append(stache(kit, "me.st", me, 1.0, -0.2, -0.74, 0.09))
    # Grandma's glasses: the engine's glass lenses pick up the green grass, so drop them and keep clear rims
    for sx in (-1, 1):
        ob = bpy.data.objects.get(f"grandma.gl{sx}")
        if ob is not None:
            bpy.data.objects.remove(ob, do_unlink=True)
    gh = bpy.data.objects.get("grandma.headg")
    if gh is not None:
        rim = P("#3a2a4a", 0.4)
        for sx in (-1, 1):
            cx = sx * 0.24
            kit.box(f"grandma.rb{sx}", (0.5, 0.04, 0.045), (cx, -0.655, -0.19), rim, gh)
            kit.box(f"grandma.rl{sx}", (0.045, 0.04, 0.36), (cx - 0.23, -0.655, -0.02), rim, gh)
            kit.box(f"grandma.rr{sx}", (0.045, 0.04, 0.36), (cx + 0.23, -0.655, -0.02), rim, gh)
    if gh is not None:
        for sx in (-1, 1):
            kit.sphere(f"grandma.ear{sx}", 0.09, (sx * 0.66, 0.0, -0.3), P("#ff7aa8", 0.35, spec=0.5), gh, seg=8)
    gu = bpy.data.objects.get("grandma.upper") or bpy.data.objects.get("grandma.torso")
    if gu is not None:
        for k in range(9):
            u = k / 8.0
            kit.sphere(f"grandma.pearl{k}", 0.085, (-0.62 + 1.24 * u, -0.545, 1.78 - 0.34 * math.sin(math.pi * u)),
                       P("#fffaf0", 0.25, spec=0.6), gu, seg=6)
    # the old group photo, resting tilted on Grandma's right palm (adults in old clothes, one empty spot in the back row)
    arm = bpy.data.objects.get("grandma.arm1")
    W["photo"] = None
    if arm is not None:
        pr = kit.empty("photo", (0.0, -0.53, -1.5), arm)
        W["photo"] = pr
        kit.box("photo.fr", (1.3, 0.04, 1.5), (0, 0, 0), P("#fffdf6", 0.6), pr)
        kit.box("photo.sky", (1.12, 0.04, 0.5), (0, -0.04, 0.4), P("#a8dcff", 0.9), pr)
        kit.box("photo.bg", (1.12, 0.04, 0.62), (0, -0.04, -0.16), P("#7ccf6a", 0.9), pr)
        kit.box("photo.grill", (0.16, 0.05, 0.2), (-0.5, -0.09, 0.12), P("#7a3a2a", 0.6), pr)
        kit.sphere("photo.gl", 0.1, (-0.5, -0.12, 0.3), P("#d94a3a", 0.5), pr, seg=8)
        shirts = ["#b05a3a", "#d8a62a", "#3a8a8a", "#8a5a9a", "#5a7a3a", "#c0603a", "#3a5a9a", "#9a8a6a"]
        skins = ["#e6b48c", "#c89870", "#f0c8a8", "#8a5a3c", "#dca97c"]
        hairs = ["#2a1a10", "#6a3a1a", "#c8a050", "#1a1410", "#8a8a8a"]
        eye = P("#1c120c", 0.5)
        ppl = []
        for i, xx in enumerate((-0.2, 0.06, 0.32, 0.58)):    # back row, the third slot left empty
            if i == 2:
                continue
            ppl.append((f"b{i}", xx - 0.02, 0.13, i))
        for i, xx in enumerate((-0.4, -0.14, 0.12, 0.38)):
            ppl.append((f"f{i}", xx, -0.3, i + 4))
        for nm, xx, zz, k in ppl:
            kit.box(f"photo.{nm}b", (0.2, 0.05, 0.26), (xx, -0.1, zz - 0.02), P(shirts[k % 8], 0.6), pr, bevel=0.01)
            kit.sphere(f"photo.{nm}h", 0.095, (xx, -0.12, zz + 0.2), P(skins[k % 5], 0.6), pr, seg=8)
            kit.box(f"photo.{nm}r", (0.2, 0.07, 0.07), (xx, -0.135, zz + 0.265), P(hairs[k % 5], 0.7), pr, bevel=0.015)
            for sx in (-1, 1):
                kit.box(f"photo.{nm}e{sx}", (0.03, 0.02, 0.035), (xx + sx * 0.04, -0.215, zz + 0.2), eye, pr)
        noshadow(pr)


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    gains = {"sun": 2.5, "fill": 1.0, "front": 0.5, "front2": 0.4}
    # movers
    movers = {}
    for c in tl["cues"]:
        if c["name"] == "mv":
            movers.setdefault(c["obj"], []).append(c)
    for nm, cs in movers.items():
        ob = W["obj"].get(nm)
        if ob is None:
            continue
        x0, y0, z0, r0 = W["init"][nm]
        cur = dict(x=x0, y=y0, z=z0, yaw=r0 / D2R, vis=1.0)
        out = dict(cur)
        for c in cs:
            if c["t"] > t:
                break
            prev = dict(out)
            tgt = dict(prev)
            for k in ("x", "y", "z", "yaw", "vis"):
                if k in c:
                    tgt[k] = c[k]
            dur = c.get("dur", 0.0)
            if dur > 0 and t < c["t"] + dur:
                u = (t - c["t"]) / dur
                u = u if c.get("lin") else ss(u)
                out = {k: prev[k] + (tgt[k] - prev[k]) * u for k in tgt}
            else:
                out = tgt
        ob.location = (out["x"], out["y"], out["z"])
        ob.rotation_euler = (ob.rotation_euler.x, ob.rotation_euler.y, out["yaw"] * D2R)
        _hide(ob, out["vis"] < 0.5)
    # photo, mustaches (never shown while their owner is hidden: pose() hides a hidden character's own parts)
    def gone(who):
        r = bpy.data.objects.get(who)
        return r is None or r.hide_render
    if W.get("photo") is not None:
        _hide(W["photo"], sample("photo", tl, t, {"v": 0.0})["v"] < 0.5 or gone("grandma"))
    g = sample("gst", tl, t, {"v": 1.0})["v"] < 0.5 or gone("glenn")
    for ob in W.get("gst", []):
        if ob.name.startswith("glenn.st"):
            _hide(ob, g)
    ms = sample("mst", tl, t, {"v": 0.0})["v"] < 0.5 or gone("me")
    for ob in W.get("mst", []):
        _hide(ob, ms)
    # the rule meter: years : days
    ck = sample("clock", tl, t, {"y": 31.0, "d": 204.0})
    ys, ds = str(max(0, int(round(ck["y"])))), str(max(0, min(999, int(round(ck["d"])))))
    groups = []
    for grp, s in zip(W["seg"], (ys, ds)):
        cells = []
        for ch in s:
            cells.append((int(ch), 0.06 if ch == "1" else 0.13))
        groups.append(cells)

    def width(cells):
        return sum(c[1] for c in cells) + 0.035 * (len(cells) - 1)
    wl, wr = width(groups[0]), width(groups[1])
    x0 = 0.18 - (wl + 0.12 + wr) / 2
    starts = [x0, x0 + wl + 0.12]
    for ob in W["colon"]:
        ob.location.x = x0 + wl + 0.06
    for gi, (grp, cells) in enumerate(zip(W["seg"], groups)):
        cur = starts[gi]
        for di, row in enumerate(grp):
            if di >= len(cells):
                for ob in row:
                    ob.hide_render = True
                continue
            dg, cw = cells[di]
            on = DIG[dg]
            cc = cur + cw / 2
            for si, nm in enumerate(SEGN):
                ob = row[si]
                ob.hide_render = nm not in on
                ob.location.x = cc + ob["bx"] - (0.05 if dg == 1 else 0.0)
            cur += cw + 0.035
    ey = sample("eye", tl, t, {"v": 0.0})["v"]
    for ob in W["eye"]:
        ob.hide_render = abs(ey - 1.0) < 0.5
    W["irisA"].hide_render = ey > 0.5
    W["irisB"].hide_render = not (ey > 1.5)
    for ob in W["tick"]:
        ob.hide_render = not (0.5 < ey < 1.5)
    # the plate sits top-left at a fixed share of the frame, whatever the lens
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
    pulse = 1.0
    for c in tl["cues"]:
        if c["name"] == "pulse" and 0.0 <= t - c["t"] < 0.6:
            pulse = 1.0 + 0.22 * math.sin(math.pi * (t - c["t"]) / 0.6)
    s = 0.6 * w2 * pulse
    tag = W["tag"]
    tag.scale = (s, s, s)
    tag.location = (-0.30 * w2, 0.68 * h2, -1.0)
    # who sits: legs straight out forward, hips on the bench
    sits = {}
    for c in tl["cues"]:
        if c["name"] == "sit" and c["t"] <= t:
            sits[c["who"]] = c
    for who, c in sits.items():
        root = bpy.data.objects.get(who)
        if c.get("on") and root is not None:
            root.location.z += c.get("z", G.SEAT) - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    return gains
