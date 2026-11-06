"""ep130-rival-clock: everyone's sleeve counts down to their best friend; mine hit zero eleven years ago.

One bright, sunny, steady world (the "closer" look). The greenhouse: a long hall of white frames with tables of seedlings,
stations along x (bench, hoses, tomatoes, radio, koi tank, Gus's round table), a hedge and the sky beyond. Four small
stages far off in y: a bus, a yard sale, a sidewalk and a bedroom.

NOTHING BLINKS, PULSES OR FLICKERS. The sun, the sky and every light are the same strength in every frame of the film.
Only the camera's own key and fill follow the shot (they change at cuts). The cuffs are cream/coloured cloth bands with
big blocky numerals (boxes, 1 cm proud of the cloth); a numeral changes only at a cut (cue "gus").

Cuffs on bodies are made in late() (the cast exists only after build()), once, and every animate call sets their
visibility from t and from their owner's hidden flag, so a render process that starts mid-film sees the same scene.

Cues (story.json "cues"): gus {sleeve: buttoned|rolled, n: null|1|0}, cups {on}, radio2 {on}, tap {on}, wide {on}.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector as V

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

W = {}
_n = [0]
INK = "#15161a"


def nm(p):
    _n[0] += 1
    return f"{p}.{_n[0]}"


def P(hexc, rough=0.5, spec=0.35):
    return W["kit"].plastic(hexc, rough, spec=spec)


def B(parent, size, loc, mat, name="b", bevel=0.0, rot=(0, 0, 0)):
    return W["kit"].box(nm(name), size, loc, mat, parent, rot, bevel)


def E(parent, loc=(0, 0, 0), name="e", rot=(0, 0, 0)):
    return W["kit"].empty(nm(name), loc, parent, rot)


def C(parent, r, h, loc, mat, name="c", rot=(0, 0, 0), n=20, r2=None):
    return W["kit"].cyl(nm(name), r, h, loc, mat, parent, rot, n, r2)


def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


def noshadow(ob):
    for o in [ob] + list(ob.children_recursive):
        try:
            o.visible_shadow = False
        except Exception:
            pass


def cue_at(tl, name, t):
    out = {}
    for c in sorted(tl["cues"], key=lambda c: c["t"]):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c
    return out


# ---------------------------------------------------------------------------------------------------- numerals
SEGS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc",
        "8": "abcdefg", "9": "abcdfg"}


def make_digits(parent, text, cx, cv, level, w, h, t, depth, plane):
    """Blocky seven-segment numerals made of boxes, `depth` thick and standing on the cloth. plane 'top': glyphs lie in
    x/y (up is +y), centred at (cx, cv), on a surface at height `level`; 'front': glyphs lie in x/z facing -y, centred
    at (cx, cv=z), on a surface at y = `level`."""
    mat = P(INK, 0.6, 0.1)
    gap = w * 0.28
    total = len(text) * w + (len(text) - 1) * gap
    out = []
    for i, ch in enumerate(text):
        gx = cx - total / 2 + w / 2 + i * (w + gap)
        pos = {"a": (0, h / 2 - t / 2, w, t), "g": (0, 0, w, t), "d": (0, -h / 2 + t / 2, w, t),
               "f": (-w / 2 + t / 2, h / 4, t, h / 2), "b": (w / 2 - t / 2, h / 4, t, h / 2),
               "e": (-w / 2 + t / 2, -h / 4, t, h / 2), "c": (w / 2 - t / 2, -h / 4, t, h / 2)}
        items = [(k,) + pos[k] for k in SEGS[ch]]
        if ch == "1":   # a centred stem, a flag at the top left and a base: a one, not a stick
            items = [("S", 0, 0, t * 1.15, h), ("A", -w / 4 + t * 0.2, h / 2 - t / 2, w / 2, t),
                     ("D", 0, -h / 2 + t / 2, w, t)]
        for k, px, pv, sw, sh in items:
            if plane == "top":
                out.append(B(parent, (sw, sh, depth), (gx + px, cv + pv, level + depth / 2 - 0.002), mat, "dig"))
            else:
                out.append(B(parent, (sw, depth, sh), (gx + px, level - depth / 2 + 0.002, cv + pv), mat, "dig"))
    return out


# ---------------------------------------------------------------------------------------------------- forearm props
CUFFS = {"me": "#f2e7c9", "gus": "#e3b32e"}


def arm_prop(name, loc, cuff, texts, yaw=0.0, sleeve="#8c93a0", skin="#a8744f", along=0.0, flannel=None, scale=1.0, pitch=0.0):
    """A forearm lying flat (origin on the surface it lies on), elbow toward -x, hand toward +x, a broad cuff of the
    person's colour on its top, blocky numerals 1 cm proud of it. texts: a string, or a dict of state -> string
    (only one state shows at a time, set by animate). Returns the group (hide with `hide`) and a dict of state groups."""
    p = math.radians(pitch)       # the far end tipped up toward the camera so the numerals face it; the front edge stays on the surface
    loc = (loc[0], loc[1], loc[2] + 0.165 * scale * math.sin(p))
    g = E(None, loc, name, (p, 0, math.radians(yaw)))
    g.scale = (scale, scale, scale)
    kit = W["kit"]
    arm = P(skin, 0.5)
    B(g, (0.92, 0.33, 0.33), (0.1, 0, 0.165), arm, "forearm", 0.03)
    B(g, (0.26, 0.3, 0.2), (0.69, 0, 0.12), arm, "hand", 0.04)
    B(g, (0.34, 0.36, 0.35), (-0.5, 0, 0.175), P(sleeve, 0.8, 0.05), "tsleeve", 0.04)
    B(g, (0.56, 0.35, 0.35), (0.05, 0, 0.175), P(cuff, 0.7, 0.05), "cuff", 0.03)
    states = {}
    items = texts if isinstance(texts, dict) else {"": texts}
    for k, txt in items.items():
        sg = E(g, (0, 0, 0), "state")
        if txt:
            n = len(txt)
            w = min(0.22, 0.5 / (n + 0.28 * (n - 1)))
            make_digits(sg, txt, 0.05, 0.0, 0.35, w, 0.28, 0.06, 0.012, "top")
        states[k] = sg
    fl = {}
    if flannel is not None:
        # a buttoned flannel sleeve over the whole cuff: plaid, with a cuff-strap and a button
        fm = flannel
        fl["buttoned"] = E(g, (0, 0, 0), "buttoned")
        B(fl["buttoned"], (0.7, 0.41, 0.41), (0.0, 0, 0.205), fm, "flannelsleeve", 0.04)
        B(fl["buttoned"], (0.1, 0.43, 0.43), (0.3, 0, 0.215), P("#8f2a24", 0.7), "flannelstrap", 0.02)
        kit.sphere(nm("button"), 0.035, (0.3, 0, 0.44), P("#efe8d6", 0.4), fl["buttoned"], seg=10)
        fl["rolled"] = E(g, (0, 0, 0), "rolled")
        B(fl["rolled"], (0.26, 0.42, 0.42), (-0.36, 0, 0.21), fm, "rollband", 0.06)
    return g, states, fl


# ---------------------------------------------------------------------------------------------------- the greenhouse
GREENS = ["#5cc85a", "#4fb84e", "#6ad266", "#47ab4f"]


def seedling_tray(x, y, z, k):
    kit = W["kit"]
    B(None, (0.88, 0.9, 0.1), (x, y, z + 0.05), P("#3a3f46", 0.7, 0.1), "tray")
    for i in range(6):
        for j in range(3):
            h = 0.12 + 0.05 * ((i * 3 + j + k) % 3)
            B(None, (0.1, 0.1, h), (x - 0.34 + 0.136 * i, y - 0.3 + 0.3 * j, z + 0.1 + h / 2), P(GREENS[(i + j + k) % 4], 0.8, 0.05),
              "seedling", 0.02)


def build_hall(kit):
    x0, x1 = G.HALL
    xm, lx = (x0 + x1) / 2, x1 - x0
    floor = kit.texture("concrete", 0.5, tint="#e9efe6")
    B(None, (lx + 6, 18, 0.2), (xm, 1.0, -0.1), floor, "hallfloor")
    # an aisle strip of light stone down the middle (y -1.5..1.5)
    B(None, (lx, 3.4, 0.01), (xm, 0.2, 0.005), P("#f1ede0", 0.9, 0.05), "aisle")
    # the lawn and hedge beyond the back wall
    B(None, (lx + 80, 60, 0.3), (xm, 44, -0.2), kit.texture("grass", 0.6, tint="#7ed25a"), "lawn")
    for i in range(int(lx / 2.2) + 2):
        hx = x0 - 2 + i * 2.2
        B(None, (2.3, 1.4, 1.6 + 0.35 * ((i * 5) % 4)), (hx, 12.5, 0.8 + 0.17 * ((i * 5) % 4)), P(GREENS[i % 4], 0.8, 0.05),
          "hedge", 0.15)
    # the frame: posts every 2 m along the back, a rail, and end posts
    white = P("#ffffff", 0.45, 0.2)
    for i in range(int(lx / 2.0) + 1):
        px = x0 + i * 2.0
        B(None, (0.12, 0.12, 4.2), (px, 9.0, 2.1), white, "post")
        B(None, (0.1, 0.1, 2.0), (px - 1.0, 9.0, 3.9), white, "mull")
    for z in (0.9, 2.2, 3.5, 4.2):
        B(None, (lx, 0.1, 0.1), (xm, 9.0, z), white, "rail")
    for sx in (x0, x1):
        for y in (-6.5, -3.0, 0.5, 4.0, 8.5):
            B(None, (0.12, 0.12, 4.2), (sx, y, 2.1), white, "endpost")
        for z in (2.2, 4.2):
            B(None, (0.1, 15.6, 0.1), (sx, 1.0, z), white, "endrail")
    # rafters behind the people only (y 4..9), so the front stays open to the sunny sky
    for i in range(int(lx / 3.0) + 1):
        rx = x0 + i * 3.0
        B(None, (0.1, 5.2, 0.1), (rx, 6.5, 4.5), white, "rafter", rot=(math.radians(-8), 0, 0))
    B(None, (lx, 0.12, 0.12), (xm, 9.0, 4.6), white, "ridge")
    # tables of seedlings, two rows
    wood = P("#c9a46a", 0.6, 0.1)
    for row, ry in enumerate((3.4, 5.6)):
        B(None, (lx - 1, 0.95, 0.07), (xm, ry, 0.82), P("#f4f6f4", 0.5, 0.2), "tabletop")
        for i in range(int((lx - 1) / 3.0) + 1):
            for sy in (-0.4, 0.4):
                B(None, (0.07, 0.07, 0.8), (x0 + 0.5 + i * 3.0, ry + sy, 0.4), wood, "tableleg")
        for i in range(int((lx - 2) / 0.95)):
            if row == 0 and abs((x0 + 1 + i * 0.95) - G.SX["tom"]) < 3.2:
                continue
            seedling_tray(x0 + 1 + i * 0.95, ry, 0.855, i + row)


def build_bench(kit):
    bx = G.SX["bench"]
    top = G.BENCH_TOP
    wood = P("#c08a52", 0.55, 0.15)
    B(None, (2.4, 0.8, 0.06), (bx, 0.35, top - 0.03), P("#e2b678", 0.55, 0.15), "benchtop", 0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            B(None, (0.08, 0.08, top - 0.06), (bx + sx * 1.1, 0.35 + sy * 0.32, (top - 0.06) / 2), wood, "benchleg")
    B(None, (2.2, 0.7, 0.04), (bx, 0.35, 0.3), wood, "benchshelf")
    for i in range(3):
        B(None, (0.5, 0.4, 0.2), (bx - 0.8 + 0.8 * i, 0.35, 0.42), P(["#e9d9b8", "#d9c7a0", "#cfe0cf"][i], 0.8, 0.05), "crate")
    # trays and pots on the far end of the bench (the near end stays clear for my arm)
    seedling_tray(bx - 0.75, 0.5, top, 1)
    # the birthday cactus with its bow, on the bench
    cx, cy = bx - 0.3, 0.52
    C(None, 0.1, 0.16, (cx, cy, top + 0.08), P("#c4623a", 0.7, 0.1), "cactuspot", n=16, r2=0.12)
    gcol = P("#3e9a4e", 0.7, 0.1)
    C(None, 0.065, 0.3, (cx, cy, top + 0.3), gcol, "cactus", n=14)
    kit.sphere(nm("cactustop"), 0.065, (cx, cy, top + 0.45), gcol, None, seg=12)
    C(None, 0.04, 0.14, (cx + 0.1, cy, top + 0.28), gcol, "cactusarm", rot=(0, math.radians(90), 0), n=10)
    C(None, 0.04, 0.14, (cx + 0.16, cy, top + 0.34), gcol, "cactusarm2", n=10)
    kit.sphere(nm("cactusarmtop"), 0.04, (cx + 0.16, cy, top + 0.41), gcol, None, seg=10)
    pink = P("#ff5fa2", 0.45, 0.3)
    for s in (-1, 1):
        B(None, (0.1, 0.03, 0.06), (cx + s * 0.06, cy - 0.07, top + 0.2), pink, "bow", 0.015, rot=(0, math.radians(s * 25), 0))
    B(None, (0.035, 0.035, 0.035), (cx, cy - 0.075, top + 0.2), pink, "bowknot", 0.01)
    W["bench_arm"], W["bench_states"], _ = arm_prop("armbench", G.BENCH_ARM, CUFFS["me"], "0", scale=1.35, pitch=30)
    # my other hand, resting near the cuff (cue tap)
    W["tap"] = E(None, (G.BENCH_ARM[0] - 0.12, G.BENCH_ARM[1] - 0.34, top), "taphand")
    B(W["tap"], (0.2, 0.2, 0.1), (0, 0, 0.05), P("#a8744f", 0.5), "taphand", 0.04)
    B(W["tap"], (0.3, 0.26, 0.12), (-0.25, -0.04, 0.06), P("#8c93a0", 0.8, 0.05), "tapsleeve", 0.04)


def build_hoses(kit):
    hx = G.SX["hose"]
    green = P("#2fb85a", 0.45, 0.4)
    dark = P("#1d7a3c", 0.5, 0.3)
    for sx, rr, hy in ((-2.4, 0.55, 2.3), (2.6, 0.5, 2.3), (-2.55, 0.55, 1.15)):
        C(None, rr, 0.5, (hx + sx, hy, 0.25), green, "hosecoil", n=28)
        C(None, rr * 0.55, 0.52, (hx + sx, hy, 0.26), dark, "hosehub", n=20)
        C(None, rr * 0.9, 0.06, (hx + sx, hy, 0.53), P("#27a350", 0.45, 0.4), "hosetop", n=28)
    # a wall tap and a reel post at the back
    B(None, (0.12, 0.12, 1.0), (hx - 1.0, 2.6, 0.5), P("#8a8f98", 0.4, 0.7), "tappipe")
    B(None, (0.3, 0.12, 0.12), (hx - 0.9, 2.55, 1.0), P("#d9a441", 0.35, 0.8), "tapbody")
    # the tangled hose on the floor in front: a zigzag of green blocks
    pts = [(-1.5, -0.55), (-0.9, -0.2), (-0.3, -0.7), (0.4, -0.25), (1.0, -0.7), (1.6, -0.3)]
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        L = math.hypot(bx - ax, by - ay)
        B(None, (L + 0.1, 0.1, 0.1), (hx + (ax + bx) / 2, (ay + by) / 2, 0.06), green, "hosetangle", 0.04,
          rot=(0, 0, math.atan2(by - ay, bx - ax)))
        kit.sphere(nm("hosebend"), 0.06, (hx + bx, by, 0.06), green, None, seg=10)


def build_tomatoes(kit):
    tx = G.SX["tom"]
    terr = P("#c4623a", 0.7, 0.1)
    red = P("#e2463a", 0.4, 0.3)
    for i in range(7):
        x = tx - 2.6 + i * 0.86
        C(None, 0.19, 0.3, (x, 3.2, 0.97), terr, "tpot", n=16, r2=0.23)
        B(None, (0.5, 0.4, 0.55), (x, 3.2, 1.35), P(GREENS[i % 4], 0.8, 0.05), "tomleaf", 0.12)
        for k in range(5):
            a = k * 1.9 + i
            kit.sphere(nm("tomato"), 0.075, (x + 0.2 * math.cos(a), 3.2 - 0.17 + 0.05 * math.sin(a), 1.2 + 0.1 * (k % 3)), red, None,
                       seg=10)
        B(None, (0.03, 0.03, 1.1), (x + 0.28, 3.2, 1.3), P("#b8a27a", 0.7), "stake")


def build_radio(kit, x, y, z, name, big=True):
    """A little old radio (cream body, teal trim, a dark speaker grille, one big brass dial) whose base is at (x, y, z).
    Two mustard strokes are scratched in the brass rim of the dial. Returns the group."""
    g = E(None, (x, y, z), name)
    body = P("#f2e2b8", 0.5, 0.3)
    B(g, (0.5, 0.26, 0.3), (0, 0, 0.15), body, "radiobody", 0.04)
    B(g, (0.52, 0.28, 0.05), (0, 0, 0.3), P("#2b9a96", 0.45, 0.3), "radiotop", 0.02)
    for i in range(5):
        B(g, (0.2, 0.012, 0.03), (-0.1, -0.135, 0.06 + 0.045 * i), P("#3b3432", 0.6), "grille")
    # the big dial
    C(g, 0.1, 0.03, (0.13, -0.14, 0.17), P("#d8a93b", 0.3, 0.9), "dialrim", rot=(math.pi / 2, 0, 0), n=28)
    dial = E(g, (0.13, -0.16, 0.17), "dial")
    C(dial, 0.07, 0.03, (0, 0, 0), P("#fbf6ea", 0.4, 0.3), "dialface", rot=(math.pi / 2, 0, 0), n=28)
    B(dial, (0.02, 0.025, 0.06), (0, -0.01, 0.03), P("#c8352c", 0.4, 0.3), "dialneedle", 0.004)
    # two mustard tally strokes on the rim (lore), steady
    for s in (-1, 1):
        B(g, (0.012, 0.012, 0.045), (0.13 + s * 0.02, -0.158, 0.265), P("#e3b32e", 0.4, 0.4), "tally")
    return g


def build_radio_station(kit):
    rx = G.SX["radio"]
    crate = P("#b98a52", 0.65, 0.1)
    B(None, (0.75, 0.5, 0.62), (rx, 0.0, 0.31), crate, "crate", 0.02)
    for z in (0.15, 0.31, 0.47):
        B(None, (0.77, 0.52, 0.04), (rx, 0.0, z), P("#8f6334", 0.7), "cratestrip", 0.01)
    W["radio1"] = build_radio(kit, rx, 0.0, 0.62, "radio1")


def build_tank(kit):
    kx = G.SX["tank"]
    slate, slate2 = P("#5a6a78", 0.6, 0.2), P("#6f808f", 0.55, 0.2)
    B(None, (2.9, 1.25, 1.0), (kx, -0.35, 0.5), slate, "tankbody", 0.02)
    # coping: front broad (y -0.95..-0.5), back thin (0.15..0.27), ends 0.3 wide
    B(None, (3.0, 0.5, 0.12), (kx, -0.72, 1.06), slate2, "copefront", 0.015)
    B(None, (3.0, 0.14, 0.12), (kx, 0.2, 1.06), slate2, "copeback", 0.015)
    for s in (-1, 1):
        B(None, (0.34, 1.3, 0.12), (kx + s * 1.28, -0.38, 1.06), slate2, "copeend", 0.015)
    water = P("#4fb8c8", 0.1, 0.8)
    B(None, (2.2, 0.62, 0.04), (kx, -0.22, 0.98), water, "water", 0.0)
    orange = P("#ff8a2a", 0.5, 0.1)
    for i, (dx, dy, r) in enumerate(((-0.7, -0.3, 0.16), (-0.1, -0.1, 0.12), (0.5, -0.35, 0.15), (0.8, -0.05, 0.1), (-0.4, 0.0, 0.09))):
        C(None, r, 0.006, (kx + dx, dy - 0.0, 1.002), orange, "koi", n=16)
    # a clear green plant bunch on the left end for colour
    for i in range(3):
        B(None, (0.3, 0.3, 0.4), (kx - 1.75 + 0.1 * i, 0.5 - 0.2 * i, 0.2), P(GREENS[i], 0.8, 0.05), "tankplant", 0.1)
    W["rim_arm"], W["rim_states"], W["rim_fl"] = arm_prop("armrim", G.RIM_ARM, CUFFS["gus"], {"": "", "1": "1", "0": "0"},
                                                          flannel=W["flannel_prop"], pitch=35)


def build_table(kit):
    tx = G.SX["table"]
    cloth = P("#fff1c2", 0.85, 0.05)
    C(None, 0.58, 0.72, (tx, 0.0, 0.37), cloth, "tableskirt", n=36, r2=0.5)
    C(None, 0.58, 0.04, (tx, 0.0, 0.73), P("#ffd86b", 0.8, 0.05), "tabletop", n=36)
    # a folding chair behind it (back slats)
    wood = P("#8a5a32", 0.6)
    B(None, (0.5, 0.5, 0.05), (tx, 1.0, 0.43), wood, "chairseat", 0.01)
    B(None, (0.5, 0.05, 0.5), (tx, 1.27, 0.7), wood, "chairback", 0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            B(None, (0.04, 0.04, 0.42), (tx + sx * 0.22, 1.0 + sy * 0.22, 0.21), wood, "chairleg")
    # the far door: white frame, glass left clear, behind the table
    white = P("#ffffff", 0.45, 0.2)
    for sx in (-1, 1):
        B(None, (0.1, 0.12, 2.3), (tx + sx * 0.6, 8.9, 1.15), white, "doorjamb")
    B(None, (1.3, 0.12, 0.1), (tx, 8.9, 2.3), white, "doortop")
    # cups (two paper cups), steam as two pale blocks each, and the second radio, shown by cue
    W["cups"] = E(None, (tx, 0.0, G.TABLE_Z), "cups")
    for sx in (-1, 1):
        C(W["cups"], 0.07, 0.05, (sx * 0.38, 0.2, 0.19), P("#f4efe6", 0.6, 0.1), "cuplid", n=16)
        C(W["cups"], 0.065, 0.2, (sx * 0.38, 0.2, 0.1), P("#f4efe6", 0.6, 0.1), "cup", n=16, r2=0.05)
        C(W["cups"], 0.07, 0.07, (sx * 0.38, 0.2, 0.11), P("#c9783a", 0.7, 0.1), "cupsleeve", n=16, r2=0.06)
        B(W["cups"], (0.07, 0.07, 0.08), (sx * 0.38, 0.2, 0.31), P("#ffffff", 0.9, 0.0), "steam", 0.03)
        B(W["cups"], (0.05, 0.05, 0.07), (sx * 0.385, 0.2, 0.4), P("#ffffff", 0.9, 0.0), "steam", 0.025)
    W["radio2"] = build_radio(kit, tx, 0.2, G.TABLE_Z, "radio2")
    W["table_arm"], W["table_states"], W["table_fl"] = arm_prop("armtable", G.TABLE_ARM, CUFFS["gus"], {"": "", "1": "1", "0": "0"},
                                                               flannel=W["flannel_prop"], scale=1.25, pitch=35)
    W["rev_arm"], W["rev_states"], W["rev_fl"] = arm_prop("armrev", (tx - 0.02, -0.02, G.TABLE_Z), CUFFS["gus"], {"": "", "1": "1", "0": "0"},
                                                          flannel=W["flannel_prop"], scale=1.2, pitch=20)
    # my hand on top of the radio beside the dial (cue dialhand); the sleeve runs off to the right, off the dial's face
    W["dialhand"] = E(None, (tx + 0.2, 0.2 - 0.05, G.TABLE_Z + 0.36), "dialhand")
    B(W["dialhand"], (0.14, 0.12, 0.07), (0, 0, 0.0), P("#a8744f", 0.5), "dialhandbox", 0.025)
    B(W["dialhand"], (0.3, 0.14, 0.1), (0.2, 0.02, 0.02), P("#8c93a0", 0.8, 0.05), "dialsleeve", 0.03)


# ---------------------------------------------------------------------------------------------------- the other places
def room(kit, cx, cy, w, d, h, wall, floor, ceil, lightc, name):
    B(None, (w, d, 0.2), (cx, cy, -0.1), P(floor, 0.7, 0.1), f"{name}floor")
    B(None, (w, 0.2, h), (cx, cy + d / 2, h / 2), P(wall, 0.8, 0.05), f"{name}back")
    for s in (-1, 1):
        B(None, (0.2, d, h), (cx + s * w / 2, cy, h / 2), P(wall, 0.8, 0.05), f"{name}side")
    B(None, (w + 0.4, d + 4.0, 0.2), (cx, cy - 1.8, h + 0.1), P(ceil, 0.9, 0.05), f"{name}ceil")
    W["rlights"].append(kit.light(f"{name}light", "POINT", (cx, cy - 0.5, h - 0.35), 260, lightc, size=0.6, shadow=False))


def build_bus(kit):
    cx, cy = G.BUS
    room(kit, cx, cy, 7.0, 4.4, 2.7, "#dff1ff", "#8d99a8", "#f4f9ff", "#fff4e0", "bus")
    skyp = kit.emit("#bfe6ff", 2.6, name="buswin")
    for i in range(3):
        B(None, (1.7, 0.05, 0.95), (cx - 2.2 + 2.2 * i, cy + 2.15, 1.5), skyp, "buswindow")
        B(None, (1.82, 0.07, 0.07), (cx - 2.2 + 2.2 * i, cy + 2.13, 2.0), P("#ffffff", 0.5), "buswinframe")
        B(None, (1.82, 0.07, 0.07), (cx - 2.2 + 2.2 * i, cy + 2.13, 1.0), P("#ffffff", 0.5), "buswinframe")
    # their seat: a solid bench block (cushion at z 0.45) and a back rest behind it
    B(None, (2.6, 1.0, 0.45), (cx, cy + 1.2, 0.225), P("#2f7fd8", 0.75, 0.05), "busseat", 0.03)
    B(None, (2.6, 0.2, 1.0), (cx, cy + 1.75, 0.95), P("#2f7fd8", 0.75, 0.05), "busseatback", 0.03)
    # the seat in front: its back is a rail with a padded top at z 1.0 (the arms lie on it)
    B(None, (2.8, 0.45, 0.55), (cx, cy - 0.15, 0.275), P("#e8782a", 0.75, 0.05), "busrail", 0.03)
    B(None, (2.8, 0.5, 0.08), (cx, cy - 0.15, 0.59), P("#f29a4a", 0.7, 0.05), "busrailpad", 0.03)
    W["bus_arms"] = [arm_prop(f"busarm{i}", (cx + x, cy - 0.15 + dy, 0.63), c, t, yaw=yw, scale=1.1, pitch=60)[0]
                     for i, (x, dy, c, t, yw) in enumerate(((-0.75, 0.0, "#ff8a7a", "0", 0), (0.3, 0.0, "#7ab8ff", "0", 0)))]
    # three more for the montage (S03): a wide padded shelf with three forearms stacked front to back
    B(None, (1.9, 2.3, 0.08), (cx + 2.4, cy - 0.15, 0.59), P("#f29a4a", 0.7, 0.05), "busrailpad")
    B(None, (1.9, 2.3, 0.55), (cx + 2.4, cy - 0.15, 0.275), P("#e8782a", 0.75, 0.05), "busrail", 0.03)
    W["bus3"] = [arm_prop(f"busthree{i}", (cx + 2.4, cy - 0.15 + (i - 1) * 0.78, 0.63), c, t, scale=1.25, pitch=40)[0]
                 for i, (c, t) in enumerate((("#ff8a7a", "3"), ("#7ab8ff", "58"), ("#9be07a", "900")))]


def build_yard(kit):
    cx, cy = G.YARD
    B(None, (40, 30, 0.3), (cx, cy + 6, -0.15), kit.texture("grass", 0.6, tint="#7ed25a"), "yardlawn")
    for i in range(14):
        B(None, (2.2, 1.2, 1.6 + 0.3 * (i % 3)), (cx - 14 + 2.2 * i, cy + 6.5, 0.9), P(GREENS[i % 4], 0.8, 0.05), "yardhedge", 0.15)
    B(None, (30, 0.12, 1.1), (cx, cy + 5.2, 0.55), P("#fff6e8", 0.6), "yardfence")
    # a yard-sale couch: a solid base, a back and arms
    cc = P("#d96a5a", 0.8, 0.05)
    B(None, (2.3, 0.95, 0.45), (cx, cy + 1.2, 0.225), cc, "couchbase", 0.04)
    B(None, (2.3, 0.22, 0.95), (cx, cy + 1.7, 0.85), cc, "couchback", 0.05)
    for s in (-1, 1):
        B(None, (0.22, 0.95, 0.7), (cx + s * 1.2, cy + 1.2, 0.5), cc, "couucharm", 0.05)
    # a yard-sale table of odds in front of them (the lap board), with a bright quilt
    B(None, (2.4, 0.7, 0.55), (cx, cy - 0.1, 0.275), P("#8a5a32", 0.7), "saletable", 0.02)
    B(None, (2.5, 0.8, 0.07), (cx, cy - 0.1, 0.59), P("#ffd86b", 0.8, 0.05), "salecloth", 0.02)
    for i, (x, c) in enumerate(((-1.0, "#7ab8ff"), (1.05, "#9be07a"))):
        B(None, (0.3, 0.3, 0.3), (cx + x, cy - 0.15, 0.78), P(c, 0.6, 0.1), "salebox", 0.03)
    W["yard_arms"] = [arm_prop(f"yardarm{i}", (cx + x, cy - 0.12, 0.625), c, "0", scale=1.1, pitch=60)[0]
                      for i, (x, c) in enumerate(((-0.75, "#c9a0ff"), (0.3, "#7fe0b0")))]


def build_walk(kit):
    cx, cy = G.WALK
    B(None, (40, 40, 0.3), (cx, cy + 12, -0.15), kit.texture("grass", 0.6, tint="#7ed25a"), "walklawn")
    B(None, (40, 16.0, 0.1), (cx, cy - 4.5, -0.05), kit.texture("concrete", 0.5, tint="#e6dcc8"), "sidewalk")
    B(None, (40, 0.5, 0.7), (cx, cy + 3.4, 0.35), P("#f3e6cf", 0.8, 0.05), "walkwall", 0.03)
    B(None, (40, 0.55, 0.06), (cx, cy + 3.4, 0.72), P("#d9c7a0", 0.7), "walkwalltop")
    for i in range(10):
        B(None, (2.6, 1.8, 1.8 + 0.4 * (i % 3)), (cx - 12 + 2.7 * i, cy + 5.2, 1.0 + 0.2 * (i % 3)), P(GREENS[i % 4], 0.8, 0.05),
          "walkhedge", 0.2)
    for tx_ in (-5.0, 4.0, 11.0):
        B(None, (0.4, 0.4, 3.0), (cx + tx_, cy + 7.0, 1.5), P("#8a5a32", 0.8), "trunk")
        kit.sphere(nm("crown"), 1.5, (cx + tx_, cy + 7.0, 3.6), P("#52c05a", 0.8, 0.05), None, seg=12)
    W["walk_arm"], _, _ = arm_prop("walkarm", (cx + 0.2, cy + 3.4, 0.75), "#ff9a3a", "347", skin="#d9a86a", sleeve="#2b6fd8")


def build_bed(kit):
    cx, cy = G.BED
    room(kit, cx, cy, 5.2, 4.6, 2.8, "#a9c4f0", "#7a8fb8", "#d9e4ff", "#cfe0ff", "bed")
    glass = kit.emit("#8fb0ff", 2.2, name="bedwin")
    B(None, (1.3, 0.05, 1.2), (cx - 1.2, cy + 2.25, 1.6), glass, "bedwindow")
    for dx, dz, sx_, sz_ in ((0, 0, 1.42, 0.07), (0, 0.6, 1.42, 0.07), (0, -0.6, 1.42, 0.07)):
        B(None, (sx_, 0.07, sz_), (cx - 1.2 + dx, cy + 2.22, 1.6 + dz), P("#ffffff", 0.5), "bedwinframe")
    B(None, (0.07, 0.07, 1.3), (cx - 1.2, cy + 2.22, 1.6), P("#ffffff", 0.5), "bedwinframe")
    # a pale moon box in the window
    B(None, (0.22, 0.04, 0.22), (cx - 1.0, cy + 2.2, 1.95), P("#fff7d8", 0.5), "moon")
    # the bed: frame, mattress, headboard at +y, pillow
    B(None, (1.5, 2.3, 0.35), (cx, cy + 0.9, 0.2), P("#9a6a3c", 0.6), "bedframe", 0.03)
    B(None, (1.4, 2.2, 0.22), (cx, cy + 0.9, 0.46), P("#f6f1ea", 0.8, 0.05), "mattress", 0.05)
    B(None, (1.6, 0.14, 1.1), (cx, cy + 2.05, 0.7), P("#9a6a3c", 0.6), "headboard", 0.03)
    B(None, (0.7, 0.45, 0.06), (cx, cy + 1.65, 0.60), P("#ffffff", 0.8, 0.05), "pillow", 0.02)
    # the quilt over my body (narrower than my shoulders so my arms lie outside it)
    B(None, (0.62, 1.2, 0.12), (cx, cy + 0.55, 1.08), P("#ff9a7a", 0.85, 0.05), "quilt", 0.06)
    B(None, (0.64, 0.16, 0.15), (cx, cy + 0.2, 1.085), P("#ffd86b", 0.85, 0.05), "quiltstripe", 0.04)
    B(None, (0.64, 0.16, 0.15), (cx, cy + 0.75, 1.085), P("#ffd86b", 0.85, 0.05), "quiltstripe", 0.04)
    # the lamp on the night stand, off (dark shade, no light)
    B(None, (0.5, 0.5, 0.5), (cx + 1.5, cy + 1.9, 0.25), P("#9a6a3c", 0.6), "nightstand")
    C(None, 0.16, 0.26, (cx + 1.5, cy + 1.9, 0.65), P("#e9dcc0", 0.8, 0.05), "lampshade", n=16, r2=0.1)
    W["bed_arm"], _, _ = arm_prop("armbed", (cx, cy + 0.15, 1.14), CUFFS["me"], "0")


# ---------------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    W.clear()
    W.update(kit=kit, story=story, inited=False)
    W["shots"] = {s["id"]: s for s in story["shots"]}
    W["rlights"] = []
    sc = bpy.context.scene
    try:
        W["bg"] = sc.world.node_tree.nodes["Background"]
    except Exception:
        W["bg"] = None
    W["sun"] = kit.light("sun", "SUN", (0, 0, 50), 4.2, "#fff1d8", size=0.1)
    W["sun"].data.angle = 0.06
    W["sun"].rotation_euler = (math.radians(50), math.radians(8), math.radians(-30))
    W["camkey"] = kit.light("camkey", "POINT", (0, 0, 5), 60, "#fff0d8", size=0.5, shadow=False)
    W["camfill"] = kit.light("camfill", "POINT", (0, 0, 5), 40, "#fff8f0", size=0.8, shadow=False)
    for nmx in ("sun", "camkey", "camfill"):
        kit.LIGHTS[nmx]["obj"].visible_camera = False
    from blocky import rig
    W["flannel_mat"] = rig.cloth(story["cast"]["gus"], "shirt")
    fp = kit._new("cloth prop flannel")      # the same plaid for the forearm props, in the props' own (small) object units
    fp.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = kit.col(story["cast"]["gus"]["shirt"])
    fp.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8
    rig._plaid(fp, story["cast"]["gus"].get("pattern_c", "#202020"), story["cast"]["gus"]["shirt"], 4.0)
    W["flannel_prop"] = fp
    build_hall(kit)
    build_bench(kit)
    build_hoses(kit)
    build_tomatoes(kit)
    build_radio_station(kit)
    build_tank(kit)
    build_table(kit)
    build_bus(kit)
    build_yard(kit)
    build_walk(kit)
    build_bed(kit)
    make_cast(kit, story)
    build_extras(kit, story)
    try:
        from blocky import polish
        W["camspecs"] = polish.cam_specs(story, tl, polish.spec(story))
    except Exception:
        W["camspecs"] = None
    return {}


# ---------------------------------------------------------------------------------------------------- the cuffs on bodies
def make_cast(kit, story):
    """Build every rig here, in build(), so the cuffs and the beard can be made with them (lesson 44). The engine then
    asks rig.Character for the same names: the factory below hands back the rigs made here."""
    import tempfile
    from blocky import rig
    d = Path(bpy.app.tempdir or tempfile.gettempdir()) / "ep130-faces"
    d.mkdir(parents=True, exist_ok=True)
    made = {}
    real = getattr(rig, "_ep130_real", None) or rig.Character
    rig._ep130_real = real
    for name, spec in story.get("cast", {}).items():
        if not spec.get("offscreen"):
            made[name] = real(name, spec, d)

    def factory(name, spec, workdir):
        return made[name] if name in made else real(name, spec, workdir)
    rig.Character = factory


def rig_cuff(kit, name, color, text, arm, states=None):
    """The cloth cuff on a rig's arm1 (rig units): a broad band 1 unit long (about 34 cm) from the wrist up, numerals 0.03
    (about 1 cm) proud of its front. Returns (cuff box, {state: group of numerals})."""
    cuff = kit.box(f"{name}.cuff", (1.02, 1.04, 1.0), (0, 0, -1.2), P(color, 0.7, 0.05), arm, bevel=0.03)
    groups = {}
    items = states if states is not None else {"": text}
    for k, txt in items.items():
        g = kit.empty(f"{name}.cuffdigits.{k or 'x'}", (0, 0, 0), arm)
        if txt:
            n = len(txt)
            w = min(0.5, 0.86 / n - 0.02 * n)
            make_digits(g, txt, 0.0, -1.2, -0.52, w, 0.78, 0.14, 0.03, "front")
        groups[k] = g
    return cuff, groups


def build_extras(kit, story):
    g = bpy.data.objects.get
    W["late"] = []          # (owner name, object, rule) rule: "always" | "buttoned" | "rolled" | ("n", value)
    plain = {"me": ("#f2e7c9", "0"), "me_young": ("#f2e7c9", "0"), "stranger_a": ("#ff8a7a", "0"), "stranger_b": ("#7ab8ff", "0"),
             "mom": ("#c9a0ff", "0"), "rita": ("#7fe0b0", "0"), "walker": ("#ff9a3a", "347")}
    W["cuffs"] = {}
    for who, (col, txt) in plain.items():
        arm = g(f"{who}.arm1")
        if arm is None:
            continue
        cuff, groups = rig_cuff(kit, who, col, txt, arm)
        W["late"].append((who, cuff, "always"))
        for grp in groups.values():
            W["late"].append((who, grp, "always"))
    arm = g("gus.arm1")
    if arm is not None:
        cuff, groups = rig_cuff(kit, "gus", CUFFS["gus"], None, arm, {"1": "1", "0": "0"})
        W["late"].append(("gus", cuff, "rolled"))
        W["late"].append(("gus", groups["1"], ("rolled", "1")))
        W["late"].append(("gus", groups["0"], ("rolled", "0")))
        fm = W["flannel_mat"]
        fa = kit.box("gus.flannelforearm", (1.1, 1.12, 1.27), (0, 0, -1.09), fm, arm, bevel=0.04)
        fb = kit.box("gus.rolledband", (1.1, 1.12, 0.4), (0, 0, -0.6), fm, arm, bevel=0.07)
        W["late"] += [("gus", fa, "buttoned"), ("gus", fb, "rolled")]
        # the other forearm is bare in the flannel too: a sleeve cover on arm-1 (always buttoned)
        arm0 = g("gus.arm-1")
        if arm0 is not None:
            fc = kit.box("gus.flannelforearm0", (1.04, 1.06, 1.27), (0, 0, -1.09), fm, arm0, bevel=0.04)
            W["late"].append(("gus", fc, "always"))
        # the thick gray beard on the head (jaw and chin only; the mouth stays clear)
        hg = g("gus.headg")
        if hg is not None:
            bm = P("#3a3b42", 0.9, 0.05)
            W["late"] += [("gus", kit.box("gus.beardchin", (0.88, 0.5, 0.4), (0, -0.4, -0.45), bm, hg, bevel=0.1), "always"),
                          ("gus", kit.box("gus.beardl", (0.12, 0.7, 0.4), (-0.54, -0.08, -0.45), bm, hg, bevel=0.05), "always"),
                          ("gus", kit.box("gus.beardr", (0.12, 0.7, 0.4), (0.54, -0.08, -0.45), bm, hg, bevel=0.05), "always"),
                          ("gus", kit.box("gus.brow", (0.34, 0.06, 0.07), (-0.24, -0.62, 0.2), bm, hg, bevel=0.02), "always"),
                          ("gus", kit.box("gus.brow2", (0.34, 0.06, 0.07), (0.24, -0.62, 0.2), bm, hg, bevel=0.02), "always")]


def owner_hidden(who):
    ob = bpy.data.objects.get(who)
    return True if ob is None else ob.hide_render


def animate(kit, story, tl, t, ctx):
    gc = cue_at(tl, "gus", t) or {}
    sleeve = gc.get("sleeve", "buttoned")
    n = gc.get("n")
    n = None if n is None else str(n)
    for who, ob, rule in W["late"]:
        oh = owner_hidden(who)
        if rule == "always":
            vis = True
        elif rule == "buttoned":
            vis = sleeve == "buttoned"
        elif rule == "rolled":
            vis = sleeve == "rolled"
        else:
            vis = sleeve == "rolled" and n == rule[1]
        hide(ob, oh or not vis)
    on = set(cue_at(tl, "props", t).get("on", []))
    hide(W["bench_arm"], "barm" not in on)
    hide(W["tap"], "tap" not in on)
    hide(W["rim_arm"], "rarm" not in on)
    hide(W["table_arm"], "tarm" not in on)
    hide(W["bed_arm"], "bedarm" not in on)
    hide(W["rev_arm"], "rev" not in on)
    # props that follow Gus's sleeve and numeral
    for key, flag in (("rim", "rarm"), ("table", "tarm"), ("rev", "rev")):
        off = flag not in on
        for st, grp in W[f"{key}_states"].items():
            hide(grp, off or not (st and sleeve == "rolled" and st == n))
        hide(W[f"{key}_fl"]["buttoned"], off or sleeve != "buttoned")
        hide(W[f"{key}_fl"]["rolled"], off or sleeve != "rolled")
    for st, grp in W["bench_states"].items():
        hide(grp, "barm" not in on)
    hide(W["cups"], not cue_at(tl, "cups", t).get("on"))
    r2 = bool(cue_at(tl, "radio2", t).get("on"))
    hide(W["radio2"], not r2)
    hide(W["dialhand"], not cue_at(tl, "dialhand", t).get("on"))
    # cameras and the two camera lights (same strength everywhere; they follow the shot)
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    sd = W["shots"].get(shot["id"], {})
    try:
        from blocky import bl_story
        cl, ct, lens, _ = bl_story.cam_at(W["camspecs"][shot["id"]], shot, t, {}, tl)
    except Exception:
        k0 = sd.get("cam", [[0, [0, -3, 1.5], [0, 0, 1.5], 36]])[0]
        cl, ct, lens = k0[1], k0[2], k0[3]
    sc = bpy.context.scene
    sc.view_settings.exposure = sd.get("exp", 0.0)
    f = V(ct) - V(cl)
    dist = max(0.3, f.length)
    f.normalize()
    r = f.cross(V((0, 0, 1)))
    r = r.normalized() if r.length > 1e-6 else V((1, 0, 0))
    kpos = V(cl) - r * 0.7 + V((0, 0, 0.6))
    W["camkey"].location = (kpos.x, kpos.y, kpos.z)
    fpos = V(cl) + r * 0.9 + V((0, 0, 0.1))
    W["camfill"].location = (fpos.x, fpos.y, fpos.z)
    fg = min(2.2, max(0.05, (dist / 3.5) ** 2))
    return {"camkey": sd.get("key", 1.0) * fg, "camfill": sd.get("fill", 1.0) * fg}
