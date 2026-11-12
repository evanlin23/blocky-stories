"""ep144 "lap behind": one outdoor town pool at sunrise (layout.py).

Water is an opaque turquoise slab, so a swimmer is only what shows above it (head, shoulders, arms) and nothing is ever
shot from below. The follower is never a body: it is foam (clusters f0..f3), driven from cues in story.json:
  f0   the follower. {"mode": "off|pin|chase", "x", "y", "v", "D"}: pinned at x, y, or chasing "me" D metres behind
       along the lap (reflected off the walls), v 0..1 scales it (0 = flat water).
  f1 / f2 / f3  pinned foam: {"x", "y", "v", "s"} (my kick's big and small splash, Grandpa's ripple).
  bn   the lap board's numbers {"a", "b"}; b2 {"v2"} fades the second row (0.4 s). The board and the camera-parented
       tag (the rule meter) show the same two rows.
  sun  none: the sun climbs slowly from 20 to 55 degrees over the film (6:00 to 6:40).
Nothing flickers: foam moves on sines under 2 Hz, the sun is steady, digits swap with no flash.
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: F401
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {}
_M = {}

WATER_A, WATER_B = "#0fb0d6", "#0aa2cc"
DECK_A, DECK_B = "#f3ede0", "#e9dfca"
CREAM = "#f6e7c8"
TERRA = "#c8603a"
RED, BLUE = "#e8433a", "#2f5bea"
NAVY = "#1b2a6b"
SEG = {"0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg", "5": "acdfg", "6": "acdefg", "7": "abc",
       "8": "abcdefg", "9": "abcdfg"}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def mat(kit, hexc, rough=0.6, spec=0.15):
    k = (hexc, rough, spec)
    if k not in _M:
        _M[k] = kit.plastic(hexc, rough, spec=spec)
    return _M[k]


def sample(name, tl, t, defaults):
    cur, prev = dict(defaults), dict(defaults)
    for c in sorted((c for c in tl["cues"] if c["name"] == name), key=lambda c: c["t"]):
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


# ------------------------------------------------------------------------------------------ seven segments
def seg_digit(kit, name, parent, plane, cu, cv, w, h, t, layer, m):
    hh = h / 2
    defs = {"a": (0, hh - t / 2, w, t), "g": (0, 0, w, t), "d": (0, -hh + t / 2, w, t),
            "f": (-w / 2 + t / 2, hh / 2, t, hh), "b": (w / 2 - t / 2, hh / 2, t, hh),
            "e": (-w / 2 + t / 2, -hh / 2, t, hh), "c": (w / 2 - t / 2, -hh / 2, t, hh)}
    out = {}
    for k, (du, dv, sw, sh) in defs.items():
        if plane == "xz":     # a board facing +y: layer is how far the digit stands proud of the plate (+y)
            ob = kit.box(f"{name}.{k}", (sw, 0.012, sh), (-(cu + du), layer, cv + dv), m, parent)
        else:                 # a tag on the camera: layer toward the camera (+z)
            ob = kit.box(f"{name}.{k}", (sw, sh, 0.002), (cu + du, cv + dv, layer), m, parent)
        out[k] = ob
    return out


def panel(kit, tag, parent, plane, layer, cfg, ink, ink2, ghost):
    """Two rows (mine, the follower's) of a swimmer glyph and two seven-segment digits."""
    rows = []
    for r, (v, m) in enumerate(((cfg["v1"], ink), (cfg["v2"], ink2))):
        digs = [seg_digit(kit, f"{tag}.r{r}d{i}", parent, plane, x, v, cfg["dw"], cfg["dh"], cfg["t"], layer, m)
                for i, x in enumerate(cfg["xd"])]
        # glyph: a head and a long body (swimmer), same for both rows
        gx = cfg["xg"]
        gl = []
        if plane == "xz":
            gl.append(kit.cyl(f"{tag}.r{r}gh", 0.07, 0.012, (-(gx + 0.12), layer, v + 0.03), m, parent, rot=(math.pi / 2, 0, 0), n=14))
            gl.append(kit.box(f"{tag}.r{r}gb", (0.24, 0.012, 0.07), (-(gx - 0.06), layer, v - 0.02), m, parent))
        else:
            gl.append(kit.cyl(f"{tag}.r{r}gh", 0.05, 0.002, (gx + 0.08, v + 0.025, layer), m, parent, n=14))
            gl.append(kit.box(f"{tag}.r{r}gb", (0.17, 0.05, 0.002), (gx - 0.04, v - 0.015, layer), m, parent))
        rows.append((digs, gl))
    return rows


def show_digit(segs, ch):
    on = SEG.get(ch, "")
    for k, ob in segs.items():
        ob.hide_render = k not in on


def set_row(row, val, visible):
    digs, gl = row
    s = str(int(val))
    slots = [" ", s] if len(s) < 2 else list(s[-2:])
    for segs, ch in zip(digs, slots):
        if not visible or ch == " ":
            for ob in segs.values():
                ob.hide_render = True
        else:
            show_digit(segs, ch)
    for ob in gl:
        ob.hide_render = not visible


def set_board(a, b, v2):
    for key in ("board", "tag"):
        r1, r2 = W[key]
        set_row(r1, a, True)
        set_row(r2, max(b, 0), v2 > 0.03)
        for nd in W[key + "_m2"].node_tree.nodes:
            if nd.type == "EMISSION":
                nd.inputs["Strength"].default_value = W[key + "_s2"] * min(1.0, v2)


def emitmat(kit, hexc, strength, name):
    m = kit.emit(hexc, strength, name)
    return m


# ------------------------------------------------------------------------------------------------ foam
def build_foam(kit, nm, n=11, r0=0.22, seed=0):
    root = kit.empty(nm, (0, 0, -5))
    wm = kit.emit("#eefaff", 1.0, "foamwhite")
    kids = []
    for i in range(n):
        a = 2 * math.pi * (i + 0.37 * seed) / n
        rad = 0.0 if i == 0 else r0 * (0.9 + 0.35 * ((i * 7 + seed * 3) % 5) / 4)
        sz = (0.30 if i == 0 else 0.16 + 0.05 * ((i * 3 + seed) % 4)) * (r0 / 0.22)
        o = kit.sphere(f"{nm}.b{i}", sz, (rad * math.cos(a), rad * math.sin(a), 0.0), wm, root, seg=10)
        o.scale = (1.0, 1.0, 0.35)
        noshadow(o)
        kids.append((o, rad * math.cos(a), rad * math.sin(a), sz, i))
    drops = []
    for i in range(4):
        a = 2 * math.pi * (i + 0.2 * seed) / 4
        o = kit.sphere(f"{nm}.d{i}", 0.03 * (r0 / 0.22), (0, 0, 0.3), wm, root, seg=8)
        noshadow(o)
        drops.append((o, 0.14 * math.cos(a) * (r0 / 0.22), 0.14 * math.sin(a) * (r0 / 0.22), i))
    W.setdefault("foam", {})[nm] = (root, kids, drops, seed)


def foam_pose(nm, x, y, v, s, t):
    root, kids, drops, seed = W["foam"][nm]
    if v <= 0.01:
        root.location = (x, y, -5.0)
        root.scale = (0.001, 0.001, 0.001)
        return
    root.location = (x, y, 0.0)
    k = v * s
    root.scale = (k, k, k)
    for o, bx, by, sz, i in kids:
        ph = i * 0.9 + seed
        o.location = (bx + 0.05 * math.sin(2 * math.pi * 0.9 * t + ph), by + 0.05 * math.cos(2 * math.pi * 0.7 * t + ph),
                      0.03 + 0.04 * math.sin(2 * math.pi * 1.3 * t + ph))
        sc = 1.0 + 0.18 * math.sin(2 * math.pi * 1.1 * t + ph)
        o.scale = (sc, sc, 0.35 * sc)
    for o, bx, by, i in drops:
        u = (t * 1.2 + i / 4.0 + seed * 0.13) % 1.0
        o.location = (bx * (0.6 + u), by * (0.6 + u), 0.05 + 0.3 * 4 * u * (1 - u))


# ------------------------------------------------------------------------------------------------ world
def deck_box(kit, name, x0, x1, y0, y1, m):
    return kit.box(name, (x1 - x0, y1 - y0, 0.54), ((x0 + x1) / 2, (y0 + y1) / 2, G.DECK - 0.27), m)


def tree(kit, i, x, y, h=6.0, lean=0.0):
    trunk = mat(kit, "#9a6a3c", 0.8, 0.05)
    leaf = mat(kit, "#3fae52", 0.7, 0.08)
    leaf2 = mat(kit, "#2f9a48", 0.7, 0.08)
    kit.cyl(f"tree{i}.t", 0.2, h, (x, y, h / 2), trunk, n=10, r2=0.14)
    top = kit.empty(f"tree{i}.top", (x + lean, y, h))
    for j in range(6):
        a = j * 60 + 17 * i
        f = kit.box(f"tree{i}.f{j}", (2.6, 0.55, 0.1), (math.cos(a * D2R) * 1.2, math.sin(a * D2R) * 1.2, -0.25),
                    leaf if j % 2 else leaf2, top, rot=(0.35 * math.sin(a * D2R), -0.35 * math.cos(a * D2R), a * D2R), bevel=0.03)
    kit.sphere(f"tree{i}.c", 0.45, (x + lean, y, h - 0.1), leaf2, seg=10)


def build(kit, story, tl):
    _M.clear()
    W.clear()
    # lights: a low warm sun from the east (+x, a touch south of east so faces toward +y get light), steady fill
    sun = kit.light("sun", "SUN", (30, -10, 20), 3.0, "#fff2e0", size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -30, 30), 2.2, "#fff0e0", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    W["sun"] = sun

    # water: an opaque slab with two close tones so a big stretch of it is never one flat colour
    kit.box("water", (14.4, G.Y, 0.6), (0, G.Y / 2, -0.3), kit.checker(WATER_A, WATER_B, 1.1, rough=0.35))
    deck = kit.checker(DECK_A, DECK_B, 0.9, rough=0.8)
    deck_box(kit, "deck.s", -16, 16, -9, 0, deck)
    deck_box(kit, "deck.n", -16, 16, G.Y, G.Y + 8, deck)
    deck_box(kit, "deck.w", -16, -7.2, 0, G.Y, deck)
    deck_box(kit, "deck.e", 7.2, 16, 0, G.Y, deck)
    edge = mat(kit, "#bfe8ef", 0.6, 0.1)
    for nm, size, loc in (("edge.s", (14.4, 0.04, 0.14), (0, -0.0, 0.07)), ("edge.n", (14.4, 0.04, 0.14), (0, G.Y, 0.07)),
                          ("edge.w", (0.04, G.Y, 0.14), (-7.2, G.Y / 2, 0.07)), ("edge.e", (0.04, G.Y, 0.14), (7.2, G.Y / 2, 0.07))):
        kit.box(nm, size, loc, edge)
    kit.box("lawn", (160, 160, 0.1), (0, 0, -0.45), mat(kit, "#6cc063", 0.9, 0.02))
    # lane ropes with red and blue floats
    rope, fr, fb = mat(kit, "#ffffff", 0.7, 0.05), mat(kit, RED, 0.6), mat(kit, BLUE, 0.6)
    for k in range(1, 8):
        x = -7.2 + k * G.LW
        kit.box(f"rope{k}", (0.035, G.Y - 0.7, 0.035), (x, G.Y / 2, 0.03), rope)
        n = int((G.Y - 1.0) / 0.55)
        for j in range(n):
            kit.box(f"rope{k}.f{j}", (0.11, 0.24, 0.1), (x, 0.7 + j * 0.55, 0.05), fr if j % 2 else fb, bevel=0.02)
    # starting blocks, one in front of every lane
    bl = mat(kit, "#dbe3ea", 0.5, 0.15)
    for k in range(1, 9):
        bx = G.lane_x(k)
        kit.box(f"block{k}", (0.7, 0.6, G.BLOCK_H), (bx, -0.55, G.DECK + G.BLOCK_H / 2), bl, bevel=0.03)
        kit.box(f"block{k}.top", (0.7, 0.6, 0.03), (bx, -0.7, G.DECK + G.BLOCK_H + 0.015), mat(kit, "#9fb4c4", 0.5), rot=(0.12, 0, 0))
    # lane four's block: the tally of two strokes (lore), blue, on the pool-facing side
    bx, by = G.BLOCK
    st = mat(kit, "#2f7fe0", 0.5)
    for dx in (-0.08, 0.08):
        kit.box(f"block4.tally{dx}", (0.04, 0.012, 0.22), (bx + dx, by + 0.306, G.DECK + 0.3), st)
    # the ladder at lane four's corner
    steel = mat(kit, "#c9d3da", 0.3, 0.5)
    for lx in (-0.5, -0.1):
        kit.box(f"ladder.r{lx}", (0.045, 0.045, 2.0), (lx, 0.15, -0.1), steel)
        kit.box(f"ladder.t{lx}", (0.045, 0.5, 0.045), (lx, -0.1, 0.88), steel)
    for j in range(3):
        kit.box(f"ladder.s{j}", (0.4, 0.04, 0.04), (-0.3, 0.15, -0.5 + j * 0.4), steel)

    # the changing house: low, cream, a tiled (terracotta) roof overhanging
    hx, hy = G.HOUSE
    kit.box("house", (9.0, 4.2, 3.0), (hx, hy, 1.5), mat(kit, CREAM, 0.8, 0.05))
    kit.box("house.roof", (9.8, 5.0, 0.3), (hx, hy, 3.15), mat(kit, TERRA, 0.7, 0.08), bevel=0.04)
    kit.box("house.ridge", (8.6, 2.2, 0.6), (hx, hy, 3.6), mat(kit, "#b4532f", 0.7, 0.08), bevel=0.05)
    kit.box("house.door", (1.1, 0.06, 2.1), (hx + 2.0, hy + 2.13, 1.05), mat(kit, "#2f8fa8", 0.5, 0.1))
    for i, wx in enumerate((-2.6, -0.4, -1.5)):
        if i == 2:
            continue
        kit.box(f"house.win{i}", (1.2, 0.06, 1.0), (hx + wx, hy + 2.13, 1.7), mat(kit, "#9fd6ec", 0.2, 0.4))
        kit.box(f"house.winf{i}", (1.36, 0.05, 1.16), (hx + wx, hy + 2.11, 1.7), mat(kit, "#ffffff", 0.5))
    kit.box("house.bench", (3.0, 0.5, 0.45), (hx - 3.0, hy + 2.6, 0.4), mat(kit, "#b98a52", 0.8))
    # trees and hedges round the pool: tall, so the far end of every shot has something in it
    for i, (tx, ty, th, tl_) in enumerate(((-9.5, 20.5, 6.5, 0.3), (-4.0, 22.5, 7.5, -0.2), (2.5, 21.5, 6.0, 0.4), (8.5, 22.5, 7.0, -0.3),
                                           (12.5, 12.0, 6.5, 0.2), (-12.5, 10.0, 7.0, -0.3), (13.0, 2.5, 6.0, 0.2),
                                           (-13.0, 1.0, 6.5, 0.3), (11.0, -6.0, 7.0, -0.2), (6.0, -12.5, 6.0, 0.3), (-10.5, -9.0, 6.5, 0.0))):
        tree(kit, i, tx, ty, th, tl_)
    hedge = mat(kit, "#3a9a4a", 0.85, 0.03)
    kit.box("hedge.n", (34, 1.0, 1.6), (0, G.Y + 6.5, 0.8), hedge, bevel=0.1)
    kit.box("hedge.w", (1.0, 24, 1.6), (-14.5, 4, 0.8), hedge, bevel=0.1)
    kit.box("hedge.e", (1.0, 24, 1.6), (14.5, 4, 0.8), hedge, bevel=0.1)
    kit.box("hedge.s", (34, 1.0, 1.6), (0, -9.2, 0.8), hedge, bevel=0.1)
    # clouds, lit peach and gold
    for i, (cx, cy, cz, sx) in enumerate(((-18, 60, 24, 34), (22, 64, 30, 40), (-30, -60, 26, 30), (20, -62, 22, 36), (50, 10, 28, 30), (-52, 14, 25, 30))):
        kit.box(f"cloud{i}", (sx, 5, 3.2), (cx, cy, cz), kit.emit("#ffe3c8" if i % 2 else "#fff0c8", 1.0), bevel=0.8)

    # the pool sign: a white board on a post, a lane with two swimmers in it (no words)
    sx, sy = G.SIGN
    kit.box("sign.post", (0.12, 0.12, 1.5), (sx, sy, 0.75), mat(kit, "#8a8f99", 0.4, 0.3))
    kit.box("sign.panel", (1.1, 0.06, 1.3), (sx, sy, 1.75), mat(kit, "#fbfbf6", 0.5, 0.1), bevel=0.02)
    yf = sy + 0.06
    kit.box("sign.rim", (1.1, 0.012, 0.06), (sx, yf, 2.37), mat(kit, RED, 0.5))
    kit.box("sign.rim2", (1.1, 0.012, 0.06), (sx, yf, 1.13), mat(kit, RED, 0.5))
    kit.box("sign.lane", (0.94, 0.012, 0.74), (sx, yf, 1.75), mat(kit, "#3aa8f0", 0.4, 0.2))
    for j, zz in enumerate((1.42, 2.08)):
        kit.box(f"sign.rope{j}", (0.94, 0.014, 0.05), (sx, yf + 0.008, zz), mat(kit, "#ffffff", 0.5))
    navy = mat(kit, NAVY, 0.4, 0.15)
    for j, zz in enumerate((1.62, 1.88)):
        kit.sphere(f"sign.h{j}", 0.075, (sx + 0.25, yf + 0.03, zz), navy, seg=10)
        kit.box(f"sign.b{j}", (0.42, 0.02, 0.1), (sx - 0.06, yf + 0.03, zz - 0.02), navy, bevel=0.03)
        kit.box(f"sign.a{j}", (0.2, 0.02, 0.05), (sx + 0.14, yf + 0.03, zz + 0.08), navy, rot=(0, 0.4, 0), bevel=0.02)
    # (the sign's glyph is the rule's picture: two swimmers, one lane)
    W["sign_pos"] = (sx, sy)

    # the lap board
    bx, by = G.BOARD
    root = kit.empty("board", (bx, by, 1.75))
    kit.box("board.legL", (0.1, 0.1, 1.2), (bx - 0.7, by, 0.6), mat(kit, "#4a4f58", 0.5, 0.2))
    kit.box("board.legR", (0.1, 0.1, 1.2), (bx + 0.7, by, 0.6), mat(kit, "#4a4f58", 0.5, 0.2))
    kit.box("board.frame", (1.84, 0.1, 1.36), (0, 0, 0), mat(kit, "#f4f4ee", 0.5, 0.1), root, bevel=0.03)
    kit.box("board.plate", (1.7, 0.1, 1.22), (0, 0.012, 0), mat(kit, "#0d0f14", 0.7, 0.05), root)
    ink = kit.emit("#ffffff", 1.1, "boardink1")
    ink2 = kit.emit("#ffffff", 1.1, "boardink2")
    W["board_m2"], W["board_s2"] = ink2, 1.1
    cfgb = dict(v1=0.27, v2=-0.27, dw=0.3, dh=0.46, t=0.075, xd=(0.1, 0.5), xg=-0.45)
    W["board"] = panel(kit, "board", root, "xz", 0.085, cfgb, ink, ink2, None)
    for rr in W["board"]:
        for dg in rr[0]:
            for ob in dg.values():
                noshadow(ob)
    # the rule tag, a copy of the board on the camera (top corner), same two rows
    cam = kit.OBJ["cam"]
    tag = kit.empty("tag", (0, 0, 0), cam)
    kit.box("tag.edge", (1.04, 0.84, 0.004), (0, 0, 0), kit.emit("#ffffff", 0.9, "tagedge"), tag)
    kit.box("tag.plate", (0.98, 0.78, 0.004), (0, 0, 0.004), kit.emit("#0d0f14", 0.35, "tagplate"), tag)
    tink = kit.emit("#ffffff", 1.0, "taginkA")
    tink2 = kit.emit("#ffffff", 1.0, "taginkB")
    W["tag_m2"], W["tag_s2"] = tink2, 1.0
    cfgt = dict(v1=0.2, v2=-0.2, dw=0.28, dh=0.34, t=0.07, xd=(-0.02, 0.32), xg=-0.38)
    W["tag"] = panel(kit, "tag", tag, "xy", 0.012, cfgt, tink, tink2, None)
    for ob in tag.children_recursive:
        noshadow(ob)
    W["tag_root"] = tag

    # lifeguard's tower on the east deck: a solid seat, so a seated guard's legs are inside it
    cx, cy = G.CHAIR
    kit.box("tower", (1.1, 1.1, 1.0), (cx, cy, 1.05), mat(kit, "#f2f2ea", 0.6, 0.1), bevel=0.03)
    kit.box("tower.base", (1.4, 1.4, 0.55), (cx, cy, 0.27), mat(kit, RED, 0.6), bevel=0.03)
    kit.box("tower.back", (1.1, 0.12, 0.7), (cx, cy - 0.5, 1.9), mat(kit, "#f2f2ea", 0.6, 0.1))

    # the duck towel on lane four's block: yellow, an orange beak mark, soaked (darker, hanging over the edge, dripping)
    bx, by = G.BLOCK
    top = G.DECK + G.BLOCK_H + 0.03
    yel = mat(kit, "#ffd23f", 0.5, 0.2)
    W["towel"] = kit.empty("towel", (bx, by, 0))
    kit.box("towel.a", (0.52, 0.4, 0.13), (0, -0.04, top + 0.065), yel, W["towel"], bevel=0.03)
    kit.box("towel.f", (0.52, 0.03, 0.22), (0, 0.205, top - 0.04), mat(kit, "#e8b222", 0.4, 0.3), W["towel"], bevel=0.01)
    kit.box("towel.beak", (0.18, 0.11, 0.014), (0.0, -0.0, top + 0.137), mat(kit, "#ff8a1f", 0.5), W["towel"], bevel=0.01)
    kit.box("towel.eye", (0.045, 0.045, 0.014), (-0.11, -0.1, top + 0.137), mat(kit, "#3a2a1a", 0.5), W["towel"])
    kit.box("puddle", (0.9, 0.55, 0.012), (bx, by + 0.62, G.DECK + 0.008), mat(kit, "#7fdcee", 0.2, 0.4))
    W["drip"] = kit.sphere("drip", 0.03, (bx + 0.1, by + 0.24, top - 0.1), mat(kit, "#6fd8ec", 0.2, 0.4), seg=8)
    W["dripx"] = (bx + 0.1, by + 0.26, top - 0.14)
    W["towel_objs"] = [o for o in bpy.data.objects if o.name.startswith(("towel.", "puddle"))]
    for i in range(4):
        build_foam(kit, f"f{i}", n=8, r0=(0.42 if i == 0 else 0.32 if i == 1 else 0.2 if i == 2 else 0.22), seed=i)
    _install_extras()
    return {}


# ---------------------------------------------------------------------------------------------- the cast's extras
def _extras(self, hg, spec, kit, faces):
    n = self.name
    R, H = faces.HEAD_R, faces.HEAD_H
    top = H / 2
    if spec.get("moustache"):   # Grandpa: a big white block moustache just under the nose, clear of the mouth
        mc = kit.plastic(spec["moustache"], 0.9, spec=0.02)
        kit.box(f"{n}.must", (0.84, 0.16, 0.2), (0, -0.54, -0.15), mc, hg, bevel=0.05)
        for sx in (-1, 1):
            kit.box(f"{n}.mustt{sx}", (0.2, 0.15, 0.26), (sx * 0.4, -0.52, -0.22), mc, hg, bevel=0.06)
    if spec.get("goggles"):   # blue goggles pushed up on the cap: two lenses and a strap
        gc = kit.plastic(spec["goggles"], 0.35, spec=0.4)
        kit.box(f"{n}.gstrap", (2 * R + 0.2, 2 * R + 0.2, 0.09), (0, 0.0, top - 0.08), gc, hg, bevel=0.03)
        for sx in (-1, 1):
            kit.box(f"{n}.glens{sx}", (0.42, 0.2, 0.3), (sx * 0.28, -R - 0.02, top - 0.08), gc, hg, bevel=0.08)


def _install_extras():
    try:
        from blocky import faces, kit as kit_mod, rig
    except Exception:   # the framing lint runs this file without Blender
        return
    if getattr(rig.Character, "_ep144", False):
        return
    orig = rig.Character._accessories

    def accessories(self, hg, spec):
        orig(self, hg, spec)
        _extras(self, hg, spec, kit_mod, faces)

    rig.Character._accessories = accessories
    rig.Character._ep144 = True


# ---------------------------------------------------------------------------------------------- animate
def reflect(y):
    p = y % (2 * G.Y)
    return p if p <= G.Y else 2 * G.Y - p


def animate(kit, story, tl, t, ctx):
    # the sun climbs: 20 degrees at 6:00 to 55 at 6:40 (the whole film), azimuth fixed
    el = (20 + 35 * min(1.0, t / 40.0)) * D2R
    d = Vector((0.97 * math.cos(el), 0.25 * math.cos(el), math.sin(el)))
    sun = W["sun"]
    sun.location = d.normalized() * 60
    kit.aim(sun, (0, 0, 0))
    # board and tag
    bn = sample("bn", tl, t, {"a": 0.0, "b": 0.0})
    b2 = sample("b2", tl, t, {"v2": 0.0})
    set_board(round(bn["a"]), round(bn["b"]), b2["v2"])
    # foam
    me = bpy.data.objects.get("me")
    f0 = sample("f0", tl, t, {"mode": "off", "x": 0.0, "y": 0.0, "v": 0.0, "D": 7.0})
    x, y, v = f0["x"], f0["y"], f0["v"]
    if f0["mode"] == "chase" and me is not None:
        yaw = me.rotation_euler.z
        dir_y = -math.cos(yaw)
        y = reflect(me.location.y - dir_y * f0["D"])
        x = me.location.x
    elif f0["mode"] == "off":
        v = 0.0
    foam_pose("f0", x, y, v, 1.0, t)
    for nm in ("f1", "f2", "f3"):
        c = sample(nm, tl, t, {"x": 0.0, "y": 0.0, "v": 0.0, "s": 1.0, "w": 0.0})
        cx_, cy_ = c["x"], c["y"]
        if c["w"] > 0.5:     # ripple riding beside Grandpa
            lou = bpy.data.objects.get("lou")
            if lou is not None:
                cx_, cy_ = lou.location.x + c["x"], lou.location.y + c["y"]
        foam_pose(nm, cx_, cy_, c["v"], c["s"], t)
    # the duck towel, its puddle and its drip exist from the cue "tw" (it is lost until L23)
    tw = sample("tw", tl, t, {"v": 0.0})["v"] > 0.5
    for ob in W["towel_objs"]:
        ob.hide_render = not tw
    # the duck towel's drip, a slow fall on the block's pool side
    dx, dy, dz = W["dripx"]
    u = (t * 0.9) % 1.0
    W["drip"].location = (dx, dy, dz - 0.55 * u * u) if (u < 0.85 and tw) else (dx, dy, -5.0)
    return {}
