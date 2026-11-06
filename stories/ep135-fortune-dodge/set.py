"""ep135-fortune-dodge: a county fair midway, Ray's hot dog cart, the fortune machine that is never wrong.

One bright, plastic world (the "closer" look), three stages far apart on the ground plane:
  MID   (0, 0)     the midway: sawdust, a striped tent wall, a stopped big wheel, Ray's red and white cart, the tall
                   teal fortune machine, a pie stand and poster, a dunk tank, a lemonade stand, string lights.
  ROOM  (60, 0)    our house: a kitchen corner (table, lamp, clock with no numerals), the couch, the front door.
  PORCH (120, 0)   the front porch: deck, rail, steps and the door behind.

NOTHING BLINKS, PULSES, FLICKERS OR MOVES. The machine has no lights. The string lights are on at the same strength in
every dusk frame and off in the others. The only slow light change is the dawn at L46 (1.5 s); the other looks swap
over the last 0.4 s of the shot before a cut. Nothing in the set is animated: cues only show or hide a still object.

No text anywhere: the cards carry a painted star, the poster a blocky face and a painted pie, the clock has no numerals.

Every extra on a character (Ray's moustache, the second apron on me) is MADE in build(), unparented and out of the way;
animate() only attaches it to the rig's part and mirrors the rig's hide flag each frame, so it is the same in every
process (lesson 44).

Cues (story.json "cues"): look {id, dur}, card {on} (my card face down on the cart's counter), card2 {on} (the new card),
mcard {on} (a card in the machine's hand slot), apron2 {where: hook|counter|porch|none}, spatula {on}, splash {on},
grillhot {on}, meapron {on}, patch {i}.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector as V

sys.path.insert(0, str(Path(__file__).resolve().parent))

W = {}
_n = [0]

MID = (0.0, 0.0)
ROOM = (60.0, 0.0)
PORCH = (120.0, 0.0)
MACH = (4.0, 4.0)
CART = (-2.5, 4.0)
PIE = (-9.5, 6.0)
POSTER = (-13.5, 6.0)
DUNK = (-18.5, 6.0)
LEMON = (11.5, 5.5)

RED, CREAM = "#e2463a", "#f6ecd6"
TEAL, GOLD = "#1fa3a0", "#ffc93a"
CORAL = "#ff7a5c"


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


def lin(h):
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(v / 255) for v in hexrgb(h))


def P(hexc, rough=0.5, spec=0.35):
    return W["kit"].plastic(hexc, rough, spec=spec)


def B(parent, size, loc, mat, name="b", bevel=0.0, rot=(0, 0, 0)):
    return W["kit"].box(nm(name), size, loc, mat, parent, rot, bevel)


def E(parent, loc=(0, 0, 0), name="e", rot=(0, 0, 0)):
    return W["kit"].empty(nm(name), loc, parent, rot)


def C(parent, r, h, loc, mat, name="c", rot=(0, 0, 0), n=20, r2=None):
    return W["kit"].cyl(nm(name), r, h, loc, mat, parent, rot, n, r2)


def S(r, loc, mat, name="s", seg=12):
    return W["kit"].sphere(nm(name), r, loc, mat, None, seg=seg)


def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


def noshadow(ob):
    try:
        ob.visible_shadow = False
    except Exception:
        pass


def star(cx, cy, cz, r_out, r_in, mat, plane="xz", thick=0.03, name="star"):
    """A flat five-point star, painted on. plane xz faces -y (a front); xy faces +z (a card's top)."""
    kit = W["kit"]
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        r = r_out if i % 2 == 0 else r_in
        pts.append((r * math.cos(a), r * math.sin(a)))
    verts, faces = [], []
    n = len(pts)
    for (u, v) in pts:
        verts.append((u, v))
    verts2 = []
    for side in (-0.5, 0.5):
        for (u, v) in pts:
            if plane == "xz":
                verts2.append((u, side * thick, v))
            else:
                verts2.append((u, v, side * thick))
    cA = len(verts2)
    verts2.append((0, -0.5 * thick, 0) if plane == "xz" else (0, 0, -0.5 * thick))
    verts2.append((0, 0.5 * thick, 0) if plane == "xz" else (0, 0, 0.5 * thick))
    for i in range(n):
        j = (i + 1) % n
        faces.append((cA, i, j))
        faces.append((cA + 1, n + j, n + i))
        faces.append((i, n + i, n + j, j))
    return kit.mesh_obj(nm(name), verts2, faces, mat, None, (cx, cy, cz))


# ------------------------------------------------------------------------------------------------------------- looks
LOOKS = {
    "day": dict(sky="#8fd6ff", world=0.9, sun=0.8, suncol="#fff1d8", fill=0.25, exp=-0.05, bulbs=0.0, lamp=0.0,
                win="#cfeeff", wins=2.5),
    "late": dict(sky="#ffc890", world=0.8, sun=0.55, suncol="#ffc080", fill=0.35, exp=0.05, bulbs=0.0, lamp=0.0,
                 win="#ffb070", wins=2.5),
    "dusk": dict(sky="#ff9f7a", world=0.75, sun=0.45, suncol="#ffb070", fill=0.4, exp=0.12, bulbs=1.0, lamp=0.0,
                 win="#ff9f7a", wins=2.0),
    "eve": dict(sky="#26386a", world=0.4, sun=0.0, suncol="#9fc4ff", fill=0.55, exp=0.3, bulbs=0.0, lamp=1.0,
                win="#2a4a7c", wins=1.2),
    "dawn": dict(sky="#ffb8a6", world=0.85, sun=0.55, suncol="#ffd0a0", fill=0.4, exp=0.1, bulbs=0.0, lamp=0.0,
                 win="#ffc8a8", wins=2.5),
}


def mixed(a, b, u):
    out = {}
    for k in a:
        if isinstance(a[k], str):
            ca, cb = lin(a[k]), lin(b[k])
            out[k] = tuple(ca[i] + (cb[i] - ca[i]) * u for i in range(3))
        else:
            out[k] = lerp(a[k], b[k], u)
    return out


def look_at(tl, t):
    cues = sorted((c for c in tl["cues"] if c["name"] == "look"), key=lambda c: c["t"])
    cur = LOOKS[cues[0]["id"]] if cues else LOOKS["day"]
    prev = cur
    for c in cues:
        if c["t"] > t:
            break
        prev, cur = cur, LOOKS[c["id"]]
        dur = c.get("dur", 0.0)
        dur = 0.0 if dur <= 0 else max(0.3, dur)      # house bar: no light change faster than 0.3 s
        if t < c["t"] + dur:
            return mixed(prev, cur, ss((t - c["t"]) / dur))
    return mixed(cur, cur, 0.0)


def cue_at(tl, name, t):
    out = {}
    for c in sorted(tl["cues"], key=lambda c: c["t"]):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c
    return out


# ------------------------------------------------------------------------------------------------------------- midway
def stripes(x0, y, z, n, w, h, d, c1, c2, name="stripe", rot=(0, 0, 0), axis="x"):
    """A row of n alternating coloured boxes along x (a tent wall, an awning)."""
    out = []
    for i in range(n):
        out.append(B(None, (w, d, h), (x0 + (i + 0.5) * w, y, z), P(c1 if i % 2 == 0 else c2, 0.7, 0.1), name, rot=rot))
    return out


def build_ground(kit):
    B(None, (200, 120, 0.4), (0, 40, -0.2), kit.texture("concrete", 0.5, tint="#e8c48a"), "sawdust")
    # the tent wall at the back and its scalloped valance
    stripes(-30, 13, 1.7, 40, 1.5, 3.4, 0.3, RED, CREAM, "tentwall")
    for i in range(40):
        B(None, (1.5, 0.36, 0.5), (-30 + (i + 0.5) * 1.5, 12.8, 3.55), P(CREAM if i % 2 == 0 else RED, 0.7, 0.1), "valance", 0.1)
    # two more tents either side, in front of the wall's ends, to break the line
    for (tx, col1, col2) in ((-24.0, "#3a7fd0", CREAM), (22.0, "#e8c040", CREAM)):
        stripes(tx - 3, 10.5, 1.5, 6, 1.0, 3.0, 0.3, col1, col2, "tent")
        C(None, 4.6, 1.8, (tx, 10.5, 3.9), P(col1, 0.7), "tentroof", n=4, r2=0.2, rot=(0, 0, math.pi / 4))
    for i, (x, y, h) in enumerate(((-26, 20, 9.0), (-8, 24, 10.0), (12, 22, 9.5), (28, 18, 8.5))):
        try:
            kit.prop("commontree_1" if i % 2 == 0 else "birchtree_1", (x, y, 0), rot=37 * i, height=h, tint="#8fd860")
        except Exception:
            pass
    # bunting along the wall, painted shapes only
    for i in range(30):
        x = -22 + i * 1.5
        z = 3.2 - 0.3 * math.sin(math.pi * (i % 6) / 5.0)
        col = ("#ffc93a", "#e2463a", "#3a7fd0", "#4fae5a")[i % 4]
        B(None, (0.5, 0.04, 0.5), (x, 11.6, z), P(col, 0.7), "pennant", rot=(0, math.pi / 4, 0))


def build_wheel(kit):
    """A stopped big wheel far behind the tents. Static."""
    cx, cy, cz, R = 4.0, 38.0, 11.5, 9.5
    rim = P("#f6f3ea", 0.5)
    axle = P("#c8ced8", 0.4, 0.6)
    N = 32
    for i in range(N):
        a = 2 * math.pi * i / N
        B(None, (2 * math.pi * R / N * 1.08, 0.5, 0.45), (cx + R * math.cos(a), cy, cz + R * math.sin(a)), rim, "wheelrim",
          rot=(0, -(a + math.pi / 2), 0))
    for i in range(12):
        a = 2 * math.pi * i / 12
        B(None, (R, 0.3, 0.25), (cx + R / 2 * math.cos(a), cy, cz + R / 2 * math.sin(a)), axle, "wheelspoke", rot=(0, -a, 0))
    C(None, 0.9, 0.9, (cx, cy, cz), P(GOLD, 0.4), "wheelhub", rot=(math.pi / 2, 0, 0), n=16)
    cols = ["#e2463a", "#3a7fd0", "#ffc93a", "#4fae5a", "#ff7a5c", "#8a4a8a"]
    for i in range(12):
        a = 2 * math.pi * i / 12 + math.pi / 12
        B(None, (1.5, 1.1, 1.2), (cx + R * math.cos(a), cy - 0.2, cz + R * math.sin(a) - 1.0), P(cols[i % 6], 0.5), "gondola", 0.1)
    for sx in (-1, 1):
        ln = math.hypot(6.0, cz)
        ang = math.atan2(cz, 6.0 * sx)
        B(None, (ln, 0.6, 0.6), (cx + 3.0 * sx, cy, cz / 2), axle, "wheelleg", rot=(0, -ang, 0))


def build_lights(kit):
    """String lights across the midway: on at one steady strength in dusk looks, off otherwise."""
    pole = P("#5a3a22", 0.7)
    for sx in (-1, 1):
        C(None, 0.1, 4.6, (sx * 21, 9.0, 2.3), pole, "lightpole", n=8)
    W["bulbs"] = []
    cols = ["#ffd86b", "#ff9a5c", "#fff2c0", "#ffb3c8"]
    W["bulbmats"] = []
    for c in cols:
        W["bulbmats"].append(kit.emit(c, 0.0, name="bulb" + c[1:]))
    for i in range(43):
        x = -21 + i
        z = 4.4 - 0.9 * (1 - (x / 21.0) ** 2)
        b = B(None, (0.2, 0.2, 0.2), (x, 9.0, z), W["bulbmats"][i % 4], "bulb", 0.04)
        noshadow(b)
        B(None, (1.0, 0.03, 0.03), (x, 9.0, z + 0.14), P("#2a2a2e", 0.6), "wire")


def build_machine(kit):
    mx, my = MACH
    stone = P("#d8d2c4", 0.8, 0.05)
    teal = P(TEAL, 0.45, 0.35)
    teal2 = P("#0f7f7d", 0.45, 0.3)
    gold = P(GOLD, 0.35, 0.6)
    dark = P("#10222a", 0.6, 0.1)
    B(None, (1.6, 1.2, 0.45), (mx, my, 0.225), stone, "machine.base", 0.03)
    B(None, (1.3, 0.9, 2.15), (mx, my, 1.525), teal, "machine.body", 0.05)
    B(None, (1.55, 1.05, 0.2), (mx, my, 2.7), teal2, "machine.crown", 0.04)
    B(None, (1.0, 0.7, 0.28), (mx, my, 2.94), teal, "machine.cap", 0.05)
    S(0.13, (mx, my, 3.18), gold, "machine.ball")
    fy = my - 0.45
    # the upper painted panel and the big gold star
    B(None, (1.08, 0.03, 0.98), (mx, fy - 0.015, 2.2), teal2, "machine.panel", 0.02)
    B(None, (1.16, 0.03, 0.06), (mx, fy - 0.03, 2.72), gold, "machine.trim")
    B(None, (1.16, 0.03, 0.06), (mx, fy - 0.03, 1.68), gold, "machine.trim")
    star(mx, fy - 0.05, 2.2, 0.4, 0.17, gold, "xz", 0.03, "machine.star")
    # the lower panel with the open-hand slot (palm and four fingers and a thumb, dark)
    B(None, (1.08, 0.03, 0.78), (mx, fy - 0.015, 1.15), teal2, "machine.panel2", 0.02)
    B(None, (0.34, 0.03, 0.3), (mx, fy - 0.04, 0.98), dark, "machine.palm", 0.03)
    for i, (dx, h) in enumerate(((-0.13, 0.2), (-0.045, 0.26), (0.045, 0.28), (0.13, 0.22))):
        B(None, (0.065, 0.03, h), (mx + dx, fy - 0.04, 1.13 + h / 2), dark, "machine.finger", 0.02)
    B(None, (0.2, 0.03, 0.065), (mx + 0.24, fy - 0.04, 1.02), dark, "machine.thumb", 0.02, rot=(0, 0.5, 0))
    for sx in (-1, 1):
        B(None, (0.06, 0.03, 1.9), (mx + sx * 0.58, fy - 0.025, 1.5), gold, "machine.edge")
    # a card poking out of the slot (cue mcard), cream with a painted star on top
    W["mcard"] = [B(None, (0.26, 0.34, 0.014), (mx, fy - 0.16, 0.9), P("#fff6dc", 0.6, 0.1), "mcard.body", 0.004),
                  star(mx, fy - 0.2, 0.9 + 0.012, 0.075, 0.032, gold, "xy", 0.006, "mcard.star")]


def build_cart(kit):
    cx, cy = CART
    red, white = P("#d8302a", 0.5, 0.35), P("#fbfaf6", 0.5, 0.3)
    B(None, (2.6, 1.2, 0.76), (cx, cy, 0.64), red, "cart.body", 0.05)
    B(None, (2.8, 1.3, 0.07), (cx, cy, 1.035), white, "cart.counter", 0.02)
    B(None, (2.62, 0.03, 0.16), (cx, cy - 0.61, 0.5), white, "cart.stripe")
    B(None, (2.62, 0.03, 0.16), (cx, cy - 0.61, 0.82), white, "cart.stripe")
    tire, hub = P("#26262c", 0.8), P(GOLD, 0.4, 0.5)
    for (wx, tilt) in ((cx - 1.15, 0.12), (cx + 1.15, 0.0)):
        C(None, 0.32, 0.12, (wx, cy - 0.38, 0.32), tire, "cart.wheel", rot=(0, math.pi / 2, tilt), n=20)
        C(None, 0.12, 0.14, (wx, cy - 0.38, 0.32), hub, "cart.hub", rot=(0, math.pi / 2, tilt), n=12)
    # the grill, and its hot glow (cue grillhot)
    B(None, (0.95, 0.6, 0.1), (cx - 0.75, cy - 0.05, 1.125), P("#2a2a30", 0.5, 0.4), "cart.grill", 0.02)
    W["grillglow"] = B(None, (0.8, 0.46, 0.02), (cx - 0.75, cy - 0.05, 1.19), kit.emit("#ff7a2a", 1.6, name="grillglow"), "grillglow")
    noshadow(W["grillglow"])
    # back frame: two posts, a teal backboard with two hooks, a striped umbrella
    wood = P("#fbfaf6", 0.5)
    for sx in (-1, 1):
        B(None, (0.08, 0.08, 1.8), (cx + sx * 1.38, cy + 0.6, 1.95), wood, "cart.post")
    B(None, (2.8, 0.06, 1.0), (cx, cy + 1.6, 2.0), P("#2f78b8", 0.5, 0.2), "cart.backboard")
    for hx in (cx - 1.0, cx + 1.0):
        B(None, (0.06, 0.1, 0.06), (hx, cy + 1.54, 2.35), P("#c8ced8", 0.3, 0.8), "cart.hook")
    # the old white apron on the left hook, always
    B(None, (0.5, 0.04, 0.78), (cx - 1.0, cy + 1.5, 1.92), white, "cart.apronold")
    B(None, (0.3, 0.045, 0.2), (cx - 1.0, cy + 1.48, 1.78), P("#e8e4dc", 0.6), "cart.apronoldpocket")
    # the second apron (coral, a cream pocket): hung, folded on the counter, or on the porch rail
    cor, pk = P(CORAL, 0.6, 0.15), P("#fff6dc", 0.6, 0.1)
    W["apron_hook"] = [B(None, (0.5, 0.04, 0.78), (cx + 1.0, cy + 1.5, 1.92), cor, "apron.hook"),
                       B(None, (0.3, 0.045, 0.2), (cx + 1.0, cy + 1.46, 1.78), pk, "apron.hookpocket")]
    W["apron_counter"] = [B(None, (0.46, 0.34, 0.07), (cx + 0.05, cy + 0.12, 1.105), cor, "apron.counter", 0.02),
                          B(None, (0.26, 0.2, 0.012), (cx + 0.05, cy + 0.12, 1.07), pk, "apron.counterpocket")]
    # the umbrella: eight stripes round a pole
    ux, uy = cx + 1.4, cy + 0.6
    C(None, 0.04, 2.9, (ux, uy, 2.2), P("#c8ced8", 0.4, 0.6), "cart.umbpole", n=8)
    rim_r, rz, ap = 2.9, 2.72, 3.4
    for i in range(8):
        a0, a1 = 2 * math.pi * i / 8, 2 * math.pi * (i + 1) / 8
        verts = [(0, 0, ap), (rim_r * math.cos(a0), rim_r * math.sin(a0), rz), (rim_r * math.cos(a1), rim_r * math.sin(a1), rz)]
        kit.mesh_obj(nm("cart.umb"), verts, [(0, 1, 2)], P(RED if i % 2 == 0 else CREAM, 0.7, 0.1), None, (ux, uy, 0))
    # the face-down card on the counter, and the new one (cues card, card2); stars up
    cardm = P("#fff6dc", 0.6, 0.1)
    W["card"] = [B(None, (0.3, 0.2, 0.012), (cx + 0.62, cy - 0.12, 1.077), cardm, "card.body", 0.003, rot=(0, 0, 0.2)),
                 star(cx + 0.62, cy - 0.12, 1.087, 0.065, 0.028, P(GOLD, 0.35, 0.6), "xy", 0.006, "card.star")]
    W["card2"] = [B(None, (0.3, 0.2, 0.012), (cx - 0.1, cy - 0.22, 1.077), cardm, "card2.body", 0.003, rot=(0, 0, -0.25)),
                  star(cx - 0.1, cy - 0.22, 1.087, 0.065, 0.028, P(GOLD, 0.35, 0.6), "xy", 0.006, "card2.star")]
    # the spatula, on the counter between us (cue spatula)
    W["spatula"] = [B(None, (0.34, 0.035, 0.022), (cx + 0.2, cy - 0.34, 1.085), P("#7a5230", 0.6), "spat.handle", 0.006),
                    B(None, (0.14, 0.11, 0.014), (cx + 0.43, cy - 0.34, 1.085), P("#c8ced8", 0.3, 0.8), "spat.head", 0.004)]
    # the wrench on the ground by the wobbly wheel
    B(None, (0.5, 0.06, 0.04), (cx - 1.6, cy - 0.9, 0.03), P("#8a8d96", 0.35, 0.8), "wrench.arm", 0.01, rot=(0, 0, 0.5))
    B(None, (0.14, 0.12, 0.04), (cx - 1.4, cy - 0.78, 0.03), P("#8a8d96", 0.35, 0.8), "wrench.head", 0.01)


def build_stalls(kit):
    # ---- the pie stand
    px, py = PIE
    B(None, (2.2, 0.9, 1.0), (px, py, 0.5), P("#ff9bb5", 0.6, 0.2), "pie.counter", 0.03)
    B(None, (2.4, 1.0, 0.07), (px, py, 1.035), P(CREAM, 0.6), "pie.top", 0.02)
    for sx in (-1, 1):
        B(None, (0.1, 0.1, 2.5), (px + sx * 1.1, py + 0.5, 1.25), P("#fbfaf6", 0.5), "pie.post")
    stripes(px - 1.3, py + 0.2, 2.5, 6, 0.433, 0.08, 1.6, "#ff9bb5", CREAM, "pie.awn", rot=(0.18, 0, 0))
    B(None, (2.6, 0.06, 0.9), (px, py + 1.5, 1.9), P("#8fd6ff", 0.5), "pie.back")
    C(None, 0.17, 0.02, (px + 0.3, py - 0.08, 1.08), P("#fbfaf6", 0.4, 0.5), "pie.plate", n=20)
    C(None, 0.13, 0.05, (px + 0.3, py - 0.08, 1.12), P("#d9a05b", 0.6), "pie.slice", n=3)
    C(None, 0.08, 0.052, (px + 0.3, py - 0.08, 1.125), P("#c22a3a", 0.5), "pie.fill", n=3)
    C(None, 0.3, 0.07, (px - 0.6, py + 0.05, 1.12), P("#d9a05b", 0.6), "pie.whole", n=24)
    C(None, 0.2, 0.075, (px - 0.6, py + 0.05, 1.12), P("#c22a3a", 0.5), "pie.wholefill", n=24)
    # ---- the poster: a big blocky face and a painted pie, no lettering
    qx, qy = POSTER
    for sx in (-1, 1):
        B(None, (0.1, 0.1, 2.6), (qx + sx * 1.05, qy + 0.1, 1.3), P("#8a5a32", 0.7), "poster.leg")
    B(None, (2.3, 0.08, 2.1), (qx, qy, 2.0), P(CREAM, 0.7, 0.05), "poster.board", 0.03)
    B(None, (2.4, 0.06, 0.1), (qx, qy - 0.02, 3.0), P(RED, 0.6), "poster.frame")
    B(None, (2.4, 0.06, 0.1), (qx, qy - 0.02, 1.0), P(RED, 0.6), "poster.frame")
    skin = P("#b07a50", 0.6, 0.15)
    fx, fz = qx - 0.55, 2.1
    B(None, (0.9, 0.05, 0.9), (fx, qy - 0.06, fz), skin, "poster.face", 0.05)
    B(None, (0.98, 0.06, 0.25), (fx, qy - 0.07, fz + 0.5), P("#2a1d15", 0.7), "poster.hair", 0.05)
    for sx in (-1, 1):
        B(None, (0.1, 0.05, 0.14), (fx + sx * 0.2, qy - 0.1, fz + 0.1), P("#14101a", 0.5), "poster.eye")
    for i, u in enumerate((-0.27, -0.14, 0.0, 0.14, 0.27)):
        B(None, (0.14, 0.05, 0.07), (fx + u, qy - 0.1, fz - 0.22 - 0.09 * (1 - (u / 0.27) ** 2) * -1), P("#14101a", 0.5), "poster.smile")
    C(None, 0.4, 0.05, (qx + 0.6, qy - 0.08, 2.1), P("#d9a05b", 0.6), "poster.pie", rot=(math.pi / 2, 0, 0), n=28)
    C(None, 0.28, 0.06, (qx + 0.6, qy - 0.11, 2.1), P("#c22a3a", 0.5), "poster.piefill", rot=(math.pi / 2, 0, 0), n=28)
    for k in range(3):
        B(None, (0.62, 0.06, 0.04), (qx + 0.6, qy - 0.14, 2.1 + (k - 1) * 0.16), P("#d9a05b", 0.6), "poster.lattice")
    # ---- the dunk tank
    dx, dy = DUNK
    B(None, (2.2, 1.6, 1.5), (dx, dy, 0.75), P("#3a9be0", 0.2, 0.7), "dunk.tank", 0.04)
    B(None, (2.2, 1.6, 0.04), (dx, dy, 1.52), P("#8fd6ff", 0.1, 0.8), "dunk.water")
    B(None, (2.6, 0.12, 3.8), (dx, dy + 1.0, 1.9), P(RED, 0.6), "dunk.back", 0.03)
    for sx in (-1, 1):
        B(None, (0.12, 0.12, 2.35), (dx + sx * 0.62, dy + 0.55, 1.175), P("#fbfaf6", 0.5), "dunk.post")
    B(None, (1.3, 0.8, 0.1), (dx, dy + 0.2, 2.3), P(CREAM, 0.6), "dunk.seat")
    C(None, 0.4, 0.05, (dx + 1.45, dy - 0.2, 1.8), P(RED, 0.5), "dunk.target", rot=(math.pi / 2, 0, 0), n=24)
    C(None, 0.26, 0.055, (dx + 1.45, dy - 0.22, 1.8), P(CREAM, 0.5), "dunk.target2", rot=(math.pi / 2, 0, 0), n=24)
    C(None, 0.12, 0.06, (dx + 1.45, dy - 0.24, 1.8), P(RED, 0.5), "dunk.target3", rot=(math.pi / 2, 0, 0), n=24)
    # spray (cue splash): white blocks round the tank's top
    spr = P("#ffffff", 0.2, 0.6)
    W["splash"] = []
    for i in range(14):
        a = 2 * math.pi * i / 14
        side = 1 if i % 2 == 0 else -1
        xo = side * (0.7 + 0.2 * (i % 4))
        W["splash"].append(B(None, (0.2 + 0.05 * (i % 3), 0.2, 0.26), (dx + xo, dy - 0.55 - 0.15 * (i % 3),
                                                                        1.7 + 0.35 * (i % 4)), spr, "splash", 0.07))
    # ---- the lemonade stand (fat awning posts at the front corners)
    lx, ly = LEMON
    yel = P("#ffe066", 0.5, 0.25)
    B(None, (3.0, 1.0, 1.0), (lx, ly, 0.5), yel, "lemon.counter", 0.03)
    B(None, (3.2, 1.1, 0.07), (lx, ly, 1.035), P(CREAM, 0.6), "lemon.top", 0.02)
    for sx in (-1, 1):
        B(None, (0.34, 0.34, 2.5), (lx + sx * 1.6, ly - 2.3, 1.25), P("#fbfaf6", 0.5), "lemon.post", 0.04)
        B(None, (0.12, 0.12, 2.5), (lx + sx * 1.5, ly + 0.5, 1.25), P("#fbfaf6", 0.5), "lemon.rearpost")
    stripes(lx - 1.8, ly - 0.9, 2.55, 8, 0.45, 0.07, 3.4, "#ffe066", CREAM, "lemon.awn", rot=(0.16, 0, 0))
    B(None, (3.4, 0.06, 1.2), (lx, ly + 0.55, 1.9), P("#ff9bb5", 0.5), "lemon.back")
    for k in range(3):
        S(0.16, (lx - 1.1 + k * 0.3, ly + 0.1, 1.2), P("#ffe066", 0.4, 0.4), "lemon.fruit")
    C(None, 0.08, 0.2, (lx + 0.5, ly - 0.15, 1.17), P("#fbfaf6", 0.3, 0.5), "lemon.cup", n=14, r2=0.06)


def build_midway(kit):
    build_ground(kit)
    build_wheel(kit)
    build_lights(kit)
    build_machine(kit)
    build_cart(kit)
    build_stalls(kit)


# ------------------------------------------------------------------------------------------------------------- house
def build_room(kit):
    rx, ry = ROOM
    floor = kit.texture("wood", 0.7, tint="#f1d8b0")
    B(None, (26, 14, 0.1), (rx + 3, ry + 2, -0.05), floor, "rfloor")
    wy = ry + 4.7
    walls = ((-9.0, -0.5, "#f8e4b0", "kitchen"), (-0.5, 7.0, "#bfe3d6", "living"), (7.0, 15.0, "#f7c9c0", "hall"))
    for (x0, x1, c, n) in walls:
        B(None, (x1 - x0, 0.2, 3.2), ((x0 + x1) / 2 + rx, wy, 1.6), P(c, 0.85, 0.05), "wall." + n)
    for sx, xx in ((-1, -9.0), (1, 15.0)):
        B(None, (0.2, 12.0, 3.2), (rx + xx, ry - 1.3, 1.6), P("#f1dcc0", 0.85, 0.05), "wall.side")
    base = P("#ffffff", 0.5)
    B(None, (24, 0.06, 0.14), (rx + 3, wy - 0.13, 0.07), base, "skirt")
    # ---- the kitchen: round table, two chairs, mugs, the lamp, a window, the clock with no numerals
    tx, ty = rx - 4.5, ry + 1.9
    tab = P("#c98f55", 0.55, 0.15)
    C(None, 0.78, 0.06, (tx, ty, 0.76), tab, "kitchentable", n=32)
    C(None, 0.08, 0.74, (tx, ty, 0.38), P("#8a5a32", 0.6), "tableleg", n=10)
    C(None, 0.34, 0.05, (tx, ty, 0.03), P("#8a5a32", 0.6), "tablefoot", n=16)
    C(None, 0.84, 0.014, (tx, ty, 0.8), P("#f2d8d0", 0.8, 0.05), "tablecloth", n=32)
    for (cxx, cyy) in ((tx + 0.35, ty - 0.2), (tx - 0.5, ty - 0.1)):
        C(None, 0.08, 0.1, (cxx, cyy, 0.865), P("#e8604a", 0.4, 0.4), "mug", n=14)
    for (cxx, cyy, ry_) in ((tx - 1.1, ty + 0.95, 0.0), (tx + 1.2, ty + 0.8, 0.0)):
        B(None, (0.5, 0.5, 0.06), (cxx, cyy, 0.45), P("#e0aa62", 0.6), "chairseat", 0.01)
        B(None, (0.5, 0.06, 0.55), (cxx, cyy + 0.25, 0.75), P("#e0aa62", 0.6), "chairback", 0.01)
        for lx_ in (-1, 1):
            for ly_ in (-1, 1):
                B(None, (0.05, 0.05, 0.42), (cxx + lx_ * 0.2, cyy + ly_ * 0.2, 0.21), P("#c08a48", 0.6), "chairleg")
    # a small lamp on the table, left of the middle
    lpx, lpy = tx - 0.42, ty + 0.12
    C(None, 0.17, 0.26, (lpx, lpy, 1.05), P("#ffe9a8", 0.6, 0.1), "lampshade", n=16, r2=0.11)
    C(None, 0.025, 0.2, (lpx, lpy, 0.9), P("#5a3a22", 0.5), "lampstem", n=8)
    C(None, 0.1, 0.03, (lpx, lpy, 0.84), P("#5a3a22", 0.5), "lampfoot", n=12)
    W["lampglow"] = B(None, (0.26, 0.26, 0.3), (lpx, lpy, 1.05), kit.emit("#ffd9a0", 2.2, name="lampglow"), "lampglow", 0.08)
    noshadow(W["lampglow"])
    W["tablelight"] = kit.light("tablelight", "POINT", (lpx - 0.6, lpy - 1.1, 1.7), 220, "#ffd9a8", size=0.6, shadow=False)
    # window in the kitchen wall
    wx = rx - 7.0
    B(None, (1.7, 0.1, 1.5), (wx, wy - 0.14, 1.75), base, "kwindowframe")
    W["kglass"] = kit.emit("#cfeeff", 2.5, name="kwindowglass")
    B(None, (1.5, 0.04, 1.3), (wx, wy - 0.2, 1.75), W["kglass"], "kwindowglass")
    B(None, (0.05, 0.06, 1.3), (wx, wy - 0.22, 1.75), base, "kwindowmullion")
    B(None, (1.5, 0.06, 0.05), (wx, wy - 0.22, 1.75), base, "kwindowtransom")
    # the clock: a round white face, a red rim, two hands, four plain ticks, no numerals
    kx = rx - 2.6
    C(None, 0.36, 0.05, (kx, wy - 0.15, 2.25), P("#e2463a", 0.4, 0.3), "clock.rim", rot=(math.pi / 2, 0, 0), n=32)
    C(None, 0.31, 0.06, (kx, wy - 0.17, 2.25), P("#fbfaf6", 0.4, 0.2), "clock.face", rot=(math.pi / 2, 0, 0), n=32)
    B(None, (0.03, 0.03, 0.22), (kx + 0.04, wy - 0.22, 2.32), P("#14101a", 0.5), "clock.long", rot=(0, 0.35, 0))
    B(None, (0.03, 0.03, 0.16), (kx - 0.07, wy - 0.22, 2.29), P("#14101a", 0.5), "clock.short", rot=(0, -1.1, 0))
    for (ux, uz) in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        B(None, (0.03, 0.03, 0.06), (kx + ux * 0.25, wy - 0.22, 2.25 + uz * 0.25), P("#14101a", 0.5), "clock.tick")
    # ---- the couch and its window, and the patch of sun on the wall (cue patch)
    cx = rx + 3.0
    coral = P("#ff7a6a", 0.6, 0.15)
    B(None, (2.6, 1.0, 0.45), (cx, ry + 3.6, 0.225), coral, "couch.seat", 0.06)
    B(None, (2.6, 0.32, 1.0), (cx, ry + 4.2, 0.5), coral, "couch.back", 0.08)
    for sx in (-1, 1):
        B(None, (0.34, 1.0, 0.75), (cx + sx * 1.3, ry + 3.6, 0.375), P("#e8604a", 0.6, 0.15), "couch.arm", 0.07)
    B(None, (0.6, 0.18, 0.5), (cx - 0.9, ry + 3.95, 0.7), P("#ffe066", 0.7), "couch.pillow", 0.07)
    B(None, (1.9, 0.1, 1.5), (cx, wy - 0.14, 2.05), base, "cwindowframe")
    W["cglass"] = kit.emit("#cfeeff", 2.5, name="cwindowglass")
    B(None, (1.7, 0.04, 1.3), (cx, wy - 0.2, 2.05), W["cglass"], "cwindowglass")
    B(None, (0.05, 0.06, 1.3), (cx, wy - 0.22, 2.05), base, "cwindowmullion")
    B(None, (1.7, 0.06, 0.05), (cx, wy - 0.22, 2.05), base, "cwindowtransom")
    W["patches"] = []
    for (px_, pz_, w_, h_) in ((cx + 2.9, 1.7, 1.3, 1.6), (cx + 2.6, 1.0, 1.5, 0.9), (cx + 2.2, 0.6, 1.7, 0.5)):
        W["patches"].append(B(None, (w_, 0.02, h_), (px_, wy - 0.115, pz_), P("#fff0b8", 0.9, 0.0), "sunpatch"))
    # ---- the front door in the hall
    dx = rx + 10.5
    B(None, (1.3, 0.12, 2.3), (dx, wy - 0.12, 1.15), base, "doorframe")
    B(None, (1.0, 0.1, 2.1), (dx, wy - 0.2, 1.05), P("#1f8a8a", 0.4, 0.3), "frontdoor", 0.01)
    S(0.06, (dx + 0.35, wy - 0.3, 1.0), P("#d8a93b", 0.3, 0.9), "doorknob")
    B(None, (0.34, 0.2, 0.012), (dx, wy - 0.7, 0.01), P("#2fb5a8", 0.9), "doormat")
    B(None, (1.0, 2.4, 0.02), (dx, ry + 3.4, 0.011), P("#ffe066", 0.9), "hallrunner")
    B(None, (0.5, 0.5, 0.9), (dx + 2.7, ry + 4.2, 0.45), P("#a9754a", 0.6), "hallcabinet")
    B(None, (0.5, 0.06, 1.4), (dx - 2.8, wy - 0.12, 1.7), P("#7a5230", 0.6), "coatboard")
    for i, c in enumerate(("#c0504a", "#4a6a9a", "#d9a441")):
        if i == 0:
            B(None, (0.14, 0.5, 0.95), (dx - 2.8, wy - 0.3, 1.2), P(c, 0.9, 0.05), "coat", 0.04)
    W["roomlight"] = kit.light("roomlight", "POINT", (rx + 3, ry + 1.0, 3.0), 90, "#ffe9c8", size=0.8, shadow=False)
    # the fixed daylight is the sun and sky; the room light only lifts the interior
    for nmx in ("roomlight", "tablelight"):
        kit.LIGHTS[nmx]["obj"].visible_camera = False


def build_porch(kit):
    px, py = PORCH
    wy = py + 7.0
    B(None, (24, 0.3, 4.4), (px, wy, 2.2), P("#ffe9a8", 0.8, 0.05), "porch.wall", 0.02)
    B(None, (24, 8, 0.1), (px, py + 3, -0.05), kit.texture("concrete", 0.5, tint="#cfe6c8"), "porch.yard")
    wood = P("#c98f55", 0.6, 0.15)
    B(None, (11.0, 3.6, 0.45), (px, py + 5.2, 0.225), wood, "porch.deck", 0.02)
    for k, (y0, z) in enumerate(((3.05, 0.3), (2.35, 0.15))):
        B(None, (2.4, 0.7, z), (px, py + y0, z / 2), P("#b98a5a", 0.6), "porch.step", 0.02)
    # the door and its frame
    B(None, (1.4, 0.12, 2.4), (px, wy - 0.22, 0.45 + 1.2), P("#ffffff", 0.5), "porch.doorframe")
    B(None, (1.1, 0.1, 2.2), (px, wy - 0.3, 0.45 + 1.1), P("#1f8a8a", 0.4, 0.3), "porch.door", 0.01)
    S(0.06, (px + 0.4, wy - 0.4, 0.45 + 1.05), P("#d8a93b", 0.3, 0.9), "porch.knob")
    # windows either side
    for sx in (-1, 1):
        B(None, (1.4, 0.1, 1.5), (px + sx * 4.2, wy - 0.2, 2.2), P("#ffffff", 0.5), "porch.wframe")
        B(None, (1.2, 0.04, 1.3), (px + sx * 4.2, wy - 0.26, 2.2), P("#bfe3f5", 0.1, 0.5), "porch.wglass")
    # rail: posts every 1.4 m with a gap for the steps
    white = P("#fbfaf6", 0.5)
    for xx in (-5.0, -3.6, -2.2, -1.2, 1.2, 2.2, 3.6, 5.0):
        B(None, (0.14, 0.14, 1.1), (px + xx, py + 3.5, 0.45 + 0.55), white, "porch.railpost", 0.02)
    for (x0, x1) in ((-5.0, -1.2), (1.2, 5.0)):
        B(None, (x1 - x0, 0.14, 0.1), (px + (x0 + x1) / 2, py + 3.5, 0.45 + 1.1), white, "porch.rail", 0.02)
        B(None, (x1 - x0, 0.06, 0.06), (px + (x0 + x1) / 2, py + 3.5, 0.45 + 0.4), white, "porch.railbar")
    # the plate of two egg sandwiches on the rail at Ray's side (left of the steps)
    sx0, sy0, sz0 = px - 2.3, py + 3.5, 0.45 + 1.15
    C(None, 0.22, 0.02, (sx0, sy0, sz0 + 0.01), P("#fbfaf6", 0.4, 0.5), "plate", n=24)
    for k in range(2):
        xo = (k - 0.5) * 0.24
        B(None, (0.2, 0.2, 0.025), (sx0 + xo, sy0, sz0 + 0.04), P("#e8c48a", 0.7), "sandwich.bread", 0.01)
        B(None, (0.2, 0.2, 0.025), (sx0 + xo, sy0, sz0 + 0.1), P("#e8c48a", 0.7), "sandwich.bread", 0.01)
        B(None, (0.17, 0.17, 0.035), (sx0 + xo, sy0, sz0 + 0.07), P("#ffe066", 0.5), "sandwich.egg", 0.01)
    # the second apron on the porch rail (cue apron2 where=porch), folded on the rail
    cor, pk = P(CORAL, 0.6, 0.15), P("#fff6dc", 0.6, 0.1)
    W["apron_porch"] = [B(None, (0.4, 0.3, 0.07), (px - 1.75, py + 3.5, 0.45 + 1.15), cor, "apron.porch", 0.02),
                        B(None, (0.22, 0.18, 0.012), (px - 1.75, py + 3.5, 0.45 + 1.115), pk, "apron.porchpocket")]
    # plate on the step between us at S52: a second plate, always there, on the second step
    stx, sty, stz = px, py + 2.35, 0.15
    C(None, 0.22, 0.02, (stx, sty, stz + 0.01), P("#fbfaf6", 0.4, 0.5), "stepplate", n=24)
    for k in range(2):
        B(None, (0.2, 0.2, 0.05), (stx + (k - 0.5) * 0.24, sty, stz + 0.05), P("#e8c48a", 0.7), "stepsandwich", 0.01)
    B(None, (0.2, 0.3, 0.012), (px + 1.0, py + 1.5, 0.006), P("#ffe066", 0.9), "porch.mat")
    W["porchlight"] = kit.light("porchlight", "POINT", (px, py + 2.0, 3.0), 90, "#ffe9c8", size=0.8, shadow=False)
    kit.LIGHTS["porchlight"]["obj"].visible_camera = False


# ------------------------------------------------------------------------------------------------------------- extras
def build_extras(kit):
    """Made now, unparented, hidden from nobody: animate() attaches each to its rig part and mirrors that part's hide flag."""
    W["extras"] = []          # (object, parent name, cue name or None)
    wm = P("#f4f4f2", 0.8)
    mu = [B(None, (0.64, 0.12, 0.14), (0, -0.63, -0.2), wm, "ray.moustache", 0.04),
          B(None, (0.14, 0.12, 0.18), (-0.33, -0.6, -0.24), wm, "ray.moustache", 0.04),
          B(None, (0.14, 0.12, 0.18), (0.33, -0.6, -0.24), wm, "ray.moustache", 0.04)]
    for o in mu:
        W["extras"].append((o, "ray.headg", None))
    cor, pk = P(CORAL, 0.6, 0.15), P("#fff6dc", 0.6, 0.1)
    ap = [B(None, (1.6, 0.06, 2.4), (0, -0.55, 0.8), cor, "me.apron2", 0.03),
          B(None, (0.8, 0.05, 0.55), (0, -0.6, 0.2), pk, "me.apron2pocket", 0.02),
          B(None, (2.06, 1.06, 0.14), (0, 0, -0.1), cor, "me.apron2tie", 0.03)]
    for o in ap:
        W["extras"].append((o, "me.torso", "meapron"))


def attach_extras(tl, t):
    for (o, pname, cuen) in W["extras"]:
        p = bpy.data.objects.get(pname)
        if p is None:
            continue
        if o.parent is None:
            o.parent = p
            o.matrix_parent_inverse = Matrix.Identity(4)
        h = bool(p.hide_render)
        if cuen is not None:
            h = h or not cue_at(tl, cuen, t).get("on")
        o.hide_render = h


# ------------------------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    W.clear()
    W.update(kit=kit, story=story)
    W["shots"] = {s["id"]: s for s in story["shots"]}
    try:
        W["bg"] = bpy.context.scene.world.node_tree.nodes["Background"]
    except Exception:
        W["bg"] = None
    W["sun"] = kit.light("sun", "SUN", (0, 0, 50), 4.5, "#fff1d8", size=0.1)
    W["sun"].data.angle = 0.06
    W["sun"].rotation_euler = (math.radians(50), math.radians(8), math.radians(-30))
    W["camkey"] = kit.light("camkey", "POINT", (0, 0, 5), 60, "#ffd9a8", size=0.5, shadow=False)
    W["camfill"] = kit.light("camfill", "POINT", (0, 0, 5), 40, "#fff0dc", size=0.8, shadow=False)
    for nmx in ("sun", "camkey", "camfill"):
        kit.LIGHTS[nmx]["obj"].visible_camera = False
    build_midway(kit)
    build_room(kit)
    build_porch(kit)
    build_extras(kit)
    try:
        from blocky import polish
        W["camspecs"] = polish.cam_specs(story, tl, polish.spec(story))
    except Exception:
        W["camspecs"] = None
    return {}


def animate(kit, story, tl, t, ctx):
    attach_extras(tl, t)
    L = look_at(tl, t)
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    sd = W["shots"].get(shot["id"], {})
    try:
        from blocky import bl_story
        cl, ct, lens, _ = bl_story.cam_at(W["camspecs"][shot["id"]], shot, t, {}, tl)
    except Exception:
        k0 = sd.get("cam", [[0, [0, -3, 1.5], [0, 0, 1.5], 36]])[0]
        cl, ct, lens = k0[1], k0[2], k0[3]
    sc = bpy.context.scene
    if W["bg"] is not None:
        W["bg"].inputs["Color"].default_value = (*L["sky"], 1.0)
        W["bg"].inputs["Strength"].default_value = L["world"]
    sc.view_settings.exposure = L["exp"] + sd.get("exp", 0.0)
    W["sun"].data.color = L["suncol"]
    for m in W["bulbmats"]:
        for nd in m.node_tree.nodes:
            if nd.type == "EMISSION":
                nd.inputs["Strength"].default_value = 5.0 * L["bulbs"]
    for key in ("kglass", "cglass"):
        for nd in W[key].node_tree.nodes:
            if nd.type == "EMISSION":
                nd.inputs["Color"].default_value = (*L["win"], 1.0)
                nd.inputs["Strength"].default_value = L["wins"]
    hide(W["lampglow"], L["lamp"] < 0.5)
    # the camera's own soft warm key and fill on faces, scaled by distance so a close-up is not blown out
    f = V(ct) - V(cl)
    dist = max(0.3, f.length)
    f.normalize()
    r = f.cross(V((0, 0, 1)))
    r = r.normalized() if r.length > 1e-6 else V((1, 0, 0))
    kpos = V(cl) - r * 0.7 + V((0, 0, 0.6))
    W["camkey"].location = (kpos.x, kpos.y, kpos.z)
    fpos = V(cl) + r * 0.9 + V((0, 0, 0.1))
    W["camfill"].location = (fpos.x, fpos.y, fpos.z)
    fg = min(2.2, max(0.05, (dist / 3.0) ** 2))
    face = 1.0 if sd.get("face", True) else 0.0
    indoors = cl[0] > 30
    gains = {"sun": L["sun"],
             "camkey": face * sd.get("key", 1.0) * fg * (0.55 if L["sun"] > 0.3 else 1.0),
             "camfill": L["fill"] * sd.get("fill", 1.0) * fg * (1.0 if face else 0.4),
             "tablelight": L["lamp"] if indoors else 0.0,
             "roomlight": (0.35 + 0.65 * (1.0 - L["sun"])) if indoors else 0.0,
             "porchlight": (0.35 + 0.65 * (1.0 - L["sun"])) if cl[0] > 100 else 0.0}
    # cues: still objects shown or hidden
    for o in W["card"]:
        hide(o, not cue_at(tl, "card", t).get("on"))
    for o in W["card2"]:
        hide(o, not cue_at(tl, "card2", t).get("on"))
    for o in W["mcard"]:
        hide(o, not cue_at(tl, "mcard", t).get("on"))
    for o in W["spatula"]:
        hide(o, not cue_at(tl, "spatula", t).get("on"))
    sp = bool(cue_at(tl, "splash", t).get("on"))
    for o in W["splash"]:
        hide(o, not sp)
    hide(W["grillglow"], not cue_at(tl, "grillhot", t).get("on"))
    where = cue_at(tl, "apron2", t).get("where", "none")
    for key, w in (("apron_hook", "hook"), ("apron_counter", "counter"), ("apron_porch", "porch")):
        for o in W[key]:
            hide(o, where != w)
    pi = cue_at(tl, "patch", t).get("i", -1)
    for k, o in enumerate(W["patches"]):
        hide(o, k != pi)
    return gains
