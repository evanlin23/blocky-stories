"""ep117 "My Parents GLOW In The Dark": a red-and-cream pizza place on a Friday evening, and little side scenes.

Rule meter: a cream tag top-left of every frame: a big lightbulb glyph and a 3-bar glow meter (Mom, Dad, me). It is a
child of the camera. Glow is a steady warm emission on skin (faces and hands, never clothes) plus a soft warm light
that follows the head. It only ever ramps (smoothstep over 0.5 s or more): never a flicker, pulse or strobe.
Cues (story.json): look (room / day / lot / stage), gmom gdad gme goth (glow level; goth follows whichever of the
roommate, planner or woman is on screen), bar (the tag's three fills), shades (sunglasses), spot (stage light), moths,
bglow (the whole booth warms), waiter (the arm with the pizza), pie (the whole pizza vs the last slice), fridgeglow,
mv (move anything registered), sit (who is seated).
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
HALO = 1.4
EM = 0.9          # emission of a glowing face at glow level 1


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def _L(**kw):
    base = dict(sun=2.0, sun_col="#fff0dc", el=50.0, az=205.0, fill=1.1, fill_col="#fff1e2", sky="#ffe9cc",
                sky_str=0.9, front=1.3, front_col="#fff0e0", pend=1.0)
    base.update(kw)
    return base


LOOKS = {
    "room": _L(sun=1.2, fill=0.7, front=0.9, sky_str=0.7),
    "day": _L(sky="#cfe6ff", sky_str=0.8, sun=1.8, fill=0.8, front=1.0),
    "roomdim": _L(sun=0.3, fill=0.3, front=0.35, sky_str=0.4, pend=0.12),
    "gum": _L(sun=0.45, fill=0.3, front=0.45, sky_str=0.3),
    "lot": _L(sun=0.5, sun_col="#9db4ff", el=35.0, az=200.0, fill=1.1, fill_col="#8aa2f0", sky="#33509a", sky_str=0.8,
              front=2.1, front_col="#ffe6d2"),
    "stage": _L(sun=0.0, fill=0.6, fill_col="#c8a8ff", sky="#3a2466", sky_str=0.5, front=1.3, front_col="#e8d8ff"),
}


def look_at(tl, t):
    cues = [c for c in tl["cues"] if c["name"] == "look"]
    cur = LOOKS[cues[0]["id"]] if cues else LOOKS["room"]
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


def sample(name, tl, t, defaults, key=None):
    cues = [c for c in tl["cues"] if c["name"] == name and (key is None or c.get("who") == key)]
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


def reg(name, ob):
    W["obj"][name] = ob
    W["init"][name] = (ob.location.x, ob.location.y, ob.location.z, ob.rotation_euler.z)
    return ob


def _hide(ob, hide):
    ob.hide_render = hide
    for c in ob.children_recursive:
        c.hide_render = hide


# ---------------------------------------------------------------------------------------------- parts
def gum_machine(kit, x, y):
    P = kit.plastic
    kit.box("gm.base", (0.8, 0.7, 0.9), (x, y, 0.45), P("#d8343a", 0.4, spec=0.4), bevel=0.05)
    kit.box("gm.foot", (0.9, 0.8, 0.08), (x, y, 0.04), P("#8f2024", 0.5))
    kit.box("gm.slot", (0.18, 0.04, 0.26), (x, y - 0.37, 0.62), P("#cfd3d8", 0.3, spec=0.8))
    kit.box("gm.chute", (0.3, 0.05, 0.2), (x, y - 0.355, 0.22), P("#2a2a30", 0.5))
    kit.cyl("gm.neck", 0.28, 0.1, (x, y, 0.95), P("#cfd3d8", 0.3, spec=0.8), n=16)
    gl = kit.sphere("gm.globe", 0.4, (x, y, 1.4), kit.glass("#e8f2ff"), seg=18)
    gl.visible_shadow = False
    kit.cyl("gm.cap", 0.3, 0.1, (x, y, 1.84), P("#d8343a", 0.4), n=16)
    cols = ["#ff4b3a", "#ffd23f", "#3fd0ff", "#7be07a", "#ff7ad9", "#ffffff", "#ff9a3a", "#9a6bff"]
    for k in range(34):
        a = k * 2.399
        r = 0.05 + 0.24 * ((k * 0.37) % 1.0) ** 0.6
        h = 1.14 + (k % 5) * 0.09 + (0.0 if r < 0.2 else -0.06)
        kit.sphere(f"gm.ball{k}", 0.075, (x + r * math.cos(a), y + r * math.sin(a), h), P(cols[k % 8], 0.3), seg=8)


def wagon(kit, x, y):
    """The station wagon, nose to the camera (-y): a hood, a windshield, two glowing headlights, wheels down both sides."""
    P = kit.plastic
    body = P("#3fae68", 0.4, spec=0.5)
    kit.box("car.low", (1.9, 4.7, 0.75), (x, y, 0.62), body, bevel=0.08)
    kit.box("car.cab", (1.8, 2.9, 0.7), (x, y + 0.35, 1.32), body, bevel=0.08)
    dark = P("#16213f", 0.2, spec=0.8)
    kit.box("car.wind", (1.5, 0.02, 0.5), (x, y + 0.35 - 1.46, 1.34), dark)
    for s_ in (-1, 1):
        kit.box(f"car.win{s_}", (0.02, 2.5, 0.46), (x + s_ * 0.905, y + 0.35, 1.36), dark)
        for wy in (-1.45, 1.45):
            kit.cyl(f"car.wh{s_}{wy}", 0.34, 0.2, (x + s_ * 0.88, y + wy, 0.34), P("#1a1a1f", 0.7),
                    rot=(0, math.pi / 2, 0), n=16)
        kit.box(f"car.hl{s_}", (0.34, 0.04, 0.2), (x + s_ * 0.6, y - 2.37, 0.78), kit.emit("#fff2c8", 6.0, f"hl{s_}"))
    kit.box("car.grille", (0.7, 0.04, 0.16), (x, y - 2.37, 0.66), P("#2a2a30", 0.4, spec=0.6))
    kit.box("car.bump", (1.9, 0.1, 0.14), (x, y - 2.4, 0.3), P("#cfd3d8", 0.3, spec=0.8))


def tree_ball(kit, name, x, y, z, col):
    kit.sphere(name, 0.28, (x, y, z), kit.plastic(col, 0.4), seg=10)


# ---------------------------------------------------------------------------------------------- build
GX_, GY_ = G.GUM


def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    P = kit.plastic
    cream = P("#f6ecd6", 0.7, spec=0.05)
    red = P("#d8343a", 0.45, spec=0.35)
    # lights: gains set in animate
    sun = kit.light("sun", "SUN", (0, -30, 40), 1.0, "#fff0d8", size=0.06)
    sun.data.angle = 0.1
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#cfe6ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    front = kit.light("front", "SUN", (-10, -30, 20), 1.0, "#ffd2ae", shadow=False)
    front.data.angle = 0.4
    kit.aim(front, (0, 0, 0))
    for i, px in enumerate((-3.0, 0.0, 3.0)):
        kit.light(f"pend{i}", "POINT", (px, 2.2, 2.3), 90.0, "#ffd9a8", size=0.3, shadow=False)
    kit.light("glowmom", "POINT", (0, 0, 2), 26.0, "#ffd98a", size=0.25, shadow=True)
    kit.light("glowdad", "POINT", (0, 0, 2), 26.0, "#ffd98a", size=0.25, shadow=False)
    kit.light("glowme", "POINT", (0, 0, 2), 26.0, "#ffd98a", size=0.25, shadow=False)
    kit.light("glowoth", "POINT", (0, 0, 2), 14.0, "#ffd98a", size=0.25, shadow=False)
    kit.light("bglow", "POINT", (0, 1.4, 2.4), 160.0, "#ffcf70", size=0.6, shadow=False)
    kit.light("fridge", "POINT", (G.FRIDGE[0] - 0.3, 2.7, 1.2), 70.0, "#f0f6ff", size=0.4, shadow=False)
    kit.light("lamp", "POINT", (G.LOT[0] + 4.0, 12.5, 5.5), 1100.0, "#ffd9a0", size=0.4, shadow=False)
    sp = kit.light("spot", "SPOT", (G.STAGE[0] + 0.6, -0.5, 5.0), 1400.0, "#fff4e0", size=0.2, spot=34, blend=0.5,
                   shadow=False)
    kit.aim(sp, (G.STAGE[0], 3.0, 1.45))

    # ============================================================== the pizza place
    floor = kit.checker("#e2463f", "#f6ecd6", 1.6, "floor")
    kit.plane("floor", (30, 14), (0, 0, 0.0), floor)
    kit.box("wall.back", (30, 0.3, 3.6), (0, 4.15, 1.8), cream)
    kit.box("wall.wain", (30, 0.1, 0.95), (0, 3.95, 0.475), red)
    kit.box("wall.wainTop", (30, 0.12, 0.06), (0, 3.94, 0.98), P("#fff8e8", 0.5))
    for s in (-1, 1):
        kit.box(f"wall.side{s}", (0.3, 12, 3.6), (s * 15.0, -2.0, 1.8), cream)
    # the window above the booth: a dusk-blue panel and a cream frame, each a few cm proud of the wall
    kit.box("win.panel", (6.8, 0.02, 1.9), (0, 3.985, 2.25), kit.emit("#3b4f9e", 0.7))
    fr_m = P("#fff8e8", 0.5)
    kit.box("win.top", (7.0, 0.06, 0.1), (0, 3.97, 3.25), fr_m)
    kit.box("win.bot", (7.0, 0.06, 0.1), (0, 3.97, 1.28), fr_m)
    for wx in (-3.45, 3.45, 0.0):
        kit.box(f"win.m{wx}", (0.1, 0.06, 2.0), (wx, 3.97, 2.25), fr_m)
    # the booth
    kit.box("bench.seat", (5.0, 0.9, 0.5), (0, 3.45, 0.25), red, bevel=0.04)
    kit.box("bench.back", (5.0, 0.2, 0.7), (0, 3.85, 0.85), red, bevel=0.04)
    kit.box("bench.trim", (5.02, 0.22, 0.05), (0, 3.85, 1.2), P("#b0282d", 0.5))
    # the table, set high enough to clear sitters' knees
    kit.box("table.top", (4.2, 0.9, 0.06), (0, 2.8, 0.95), P("#dcc9a0", 0.7, spec=0.05), bevel=0.02)
    for tx in (-1.4, 1.4):
        kit.cyl(f"table.leg{tx}", 0.09, 0.9, (tx, 2.8, 0.45), P("#9fa4aa", 0.3, spec=0.7), n=12)
        kit.cyl(f"table.foot{tx}", 0.3, 0.05, (tx, 2.8, 0.03), P("#9fa4aa", 0.3, spec=0.7), n=16)
    # the pizza: a whole pie (anchovy and pineapple) and, for one shot, only the last slice
    pie = kit.empty("pie", (0, 2.8, 0.98))
    kit.cyl("pie.pan", 0.5, 0.02, (0, 0, 0.0), P("#aeb2b8", 0.3, spec=0.7), pie, n=28)
    kit.cyl("pie.crust", 0.44, 0.05, (0, 0, 0.035), P("#e0a65a", 0.6), pie, n=28)
    kit.cyl("pie.cheese", 0.37, 0.05, (0, 0, 0.06), P("#ffcf5a", 0.5), pie, n=28)
    pine = P("#ffe35a", 0.4)
    anch = P("#6b5a4c", 0.5)
    for k in range(16):
        a = k * 2.4 + 0.3
        r = 0.08 + 0.26 * ((k * 0.41) % 1.0)
        kit.box(f"pie.pa{k}", (0.075, 0.075, 0.035), (r * math.cos(a), r * math.sin(a), 0.1), pine, pie, rot=(0, 0, a), bevel=0.01)
    for k in range(13):
        a = k * 2.9 + 1.0
        r = 0.1 + 0.25 * ((k * 0.57) % 1.0)
        kit.box(f"pie.an{k}", (0.16, 0.03, 0.02), (r * math.cos(a), r * math.sin(a), 0.1), anch, pie, rot=(0, 0, a * 1.7))
    reg("pie", pie)
    sl = kit.empty("slice", (0.0, 2.7, 0.99))
    ang = math.radians(42)
    n = 7
    vs = [(0, 0, 0.0), (0, 0, 0.1)]
    for i in range(n + 1):
        a = -ang / 2 + ang * i / n
        vs.append((0.46 * math.cos(a + math.pi / 2), 0.46 * math.sin(a + math.pi / 2) * 1.0 - 0.0, 0.0))
    # a wedge pointing +y: apex at the origin, a round crust edge at 0.44
    verts = [(0.0, 0.0, 0.0), (0.0, 0.0, 0.07)]
    for i in range(n + 1):
        a = math.pi / 2 - ang / 2 + ang * i / n
        verts.append((0.44 * math.cos(a), 0.44 * math.sin(a), 0.0))
        verts.append((0.44 * math.cos(a), 0.44 * math.sin(a), 0.07))
    faces = []
    for i in range(n):
        b0, b1 = 2 + 2 * i, 2 + 2 * (i + 1)
        faces += [(0, b1, b0), (1, b0 + 1, b1 + 1), (b0, b1, b1 + 1, b0 + 1)]
    faces += [(0, 2, 3, 1), (0, 1, 2 + 2 * n + 1, 2 + 2 * n)]
    wedge = kit.mesh_obj("slice.w", verts, faces, P("#ffcf5a", 0.5), sl)
    kit.box("slice.crust", (0.22, 0.05, 0.075), (0, 0.43, 0.037), P("#e0a65a", 0.6), sl, bevel=0.01)
    kit.box("slice.pa", (0.07, 0.07, 0.03), (0.04, 0.25, 0.085), pine, sl)
    kit.box("slice.an", (0.16, 0.03, 0.02), (-0.05, 0.32, 0.08), anch, sl, rot=(0, 0, 0.5))
    kit.cyl("slice.tray", 0.4, 0.02, (0.0, 0.18, 0.012), P("#8f2024", 0.5, spec=0.3), sl, n=24)
    reg("slice", sl)
    # pendant lamps (fixed)
    for i, px in enumerate((-3.0, 0.0, 3.0)):
        kit.cyl(f"pend{i}.cord", 0.02, 2.0, (px, 2.2, 3.4), P("#2a2a2e", 0.5), n=6)
        kit.sphere(f"pend{i}.shade", 0.3, (px, 2.2, 2.3), kit.emit("#fff0cf", 1.0), seg=14)
    # the gumball machine and a small counter
    gum_machine(kit, *G.GUM)
    # coloured gumball shadows on the wall behind the machine (shown only while Mom's light is on it, cue gshadow):
    # each ball projected from a low lamp left of the machine, stretched along the wall, in a dark shade of its colour
    W["gsh"] = []
    Lp = (GX_ - 2.2, 0.8, 1.0)
    dcols_ = ["#b8281c", "#c89400", "#1480b8", "#2f9a2f", "#b83a90", "#8a8a98", "#c05c10", "#6030c0"]
    cols_ = ["#ff4b3a", "#ffd23f", "#3fd0ff", "#7be07a", "#ff7ad9", "#ffffff", "#ff9a3a", "#9a6bff"]
    for k in range(0, 34, 3):
        a = k * 2.399
        r = 0.05 + 0.24 * ((k * 0.37) % 1.0) ** 0.6
        h = 1.14 + (k % 5) * 0.09 + (0.0 if r < 0.2 else -0.06)
        bx, bz = GX_ + r * math.cos(a), h
        by = GY_ + r * math.sin(a)
        sc_ = (3.97 - Lp[1]) / (by - Lp[1])
        wx, wz = Lp[0] + sc_ * (bx - Lp[0]), Lp[2] + sc_ * (bz - Lp[2])
        mt = kit.emit(dcols_[k % 8], 0.9, f"gshm{k}")
        d_ = kit.cyl(f"gsh{k}", 0.1, 0.01, (wx, 3.975, wz), mt, rot=(math.pi / 2, 0, 0), n=16)
        d_.scale = (2.2, 1.0, 1.0)
        W["gsh"].append(d_)
    kit.box("counter", (5.0, 0.8, 1.05), (-9.0, 3.4, 0.525), P("#7a3a2a", 0.6))
    kit.box("counter.top", (5.2, 0.9, 0.06), (-9.0, 3.38, 1.08), cream)
    kit.box("box.pz", (0.7, 0.7, 0.07), (-8.5, 3.38, 1.14), P("#e8d8b8", 0.8))
    # the coat hook at the end of the booth, with three pizza-red strokes (a tally, no words)
    chrome = kit.metal("#cfd3d8", 0.25)
    steel = P("#5d636e", 0.35, spec=0.5)
    kit.box("hook.post", (0.3, 0.2, 1.3), (2.75, 3.45, 0.65), steel)
    kit.box("hook.arm", (0.12, 0.45, 0.12), (2.75, 3.15, 1.22), steel)
    kit.box("hook.tip", (0.12, 0.12, 0.28), (2.75, 2.95, 1.3), steel)
    for k, dx in enumerate((-0.095, 0.0, 0.095)):
        kit.box(f"hook.t{k}", (0.07, 0.02, 0.6), (2.75 + dx, 3.34, 0.62), P("#ff2a20", 0.5))
    # the waiter's arm (a sleeve, a flat hand and a fresh pie), off screen until L32
    wa = kit.empty("wa", (2.6, 1.4, -60.0))
    kit.box("wa.sleeve", (1.3, 0.3, 0.26), (1.15, 0.0, 0.14), P("#f4f4f2", 0.6), wa, bevel=0.04)
    kit.box("wa.hand", (0.3, 0.22, 0.12), (0.5, 0.0, 0.06), P("#cf9d74", 0.5), wa, bevel=0.02)
    kit.cyl("wa.pan", 0.44, 0.02, (0.0, 0.0, 0.0), P("#aeb2b8", 0.3, spec=0.7), wa, n=24)
    kit.cyl("wa.pie", 0.36, 0.06, (0.0, 0.0, 0.04), P("#ffcf5a", 0.5), wa, n=24)
    for k in range(7):
        a = k * 2.4
        kit.box(f"wa.top{k}", (0.07, 0.03, 0.02), (0.22 * math.cos(a) * ((k % 3 + 1) / 3), 0.22 * math.sin(a) * ((k % 3 + 1) / 3), 0.085),
                P("#6b5a4c" if k % 2 else "#ffe35a", 0.5), wa)
    reg("wa", wa)

    # ============================================================== the lot
    LX, LY = G.LOT
    kit.plane("lot.ground", (80, 60), (LX, 20, 0.0), P("#3a4880", 0.9, spec=0.05))
    for k in range(-4, 5):
        kit.box(f"lot.line{k}", (0.12, 4.0, 0.012), (LX + k * 3.0, 7.0, 0.012), P("#a9b6e8", 0.8))
    kit.box("lot.bld", (60, 1.6, 8.0), (LX, 35, 4.0), P("#23356e", 0.8, spec=0.05))
    kit.box("lot.bldtop", (60, 1.8, 0.5), (LX, 35, 8.2), P("#1a2a5c", 0.8))
    wm = kit.emit("#ffd98a", 1.2)
    for k in range(-5, 6):
        kit.box(f"lot.w{k}", (1.6, 0.04, 1.3), (LX + k * 4.6, 34.18, 3.3), wm)
    kit.cyl("lot.pole", 0.12, 7.0, (LX + 9.0, 26.0, 3.5), P("#1a2548", 0.6), n=8)
    kit.sphere("lot.lampbulb", 0.4, (LX + 9.0, 26.0, 7.0), kit.emit("#ffe2a8", 2.0), seg=10)
    wagon(kit, G.CAR[0], G.CAR[1])
    kit.box("lot.curb", (60, 0.4, 0.2), (LX, 2.0, 0.1), P("#6a78b8", 0.8))
    # moths: two pale wings each
    W["moths"] = []
    for k in range(6):
        m = kit.empty(f"moth{k}", (0, 0, -80.0))
        mt = P("#e8d8b0", 0.6)
        kit.box(f"moth{k}.wl", (0.09, 0.07, 0.008), (-0.045, 0, 0), mt, m)
        kit.box(f"moth{k}.wr", (0.09, 0.07, 0.008), (0.045, 0, 0), mt, m)
        kit.box(f"moth{k}.b", (0.02, 0.07, 0.02), (0, 0, 0.0), P("#6a5a48", 0.6), m)
        W["moths"].append(m)

    # ============================================================== the bus stop
    BX, BY = G.BUS
    kit.plane("bus.ground", (30, 14), (BX, 0, 0.0), P("#9aa0aa", 0.9))
    kit.box("bus.wall", (30, 0.3, 4.0), (BX, 5.15, 2.0), P("#4f7fb8", 0.8))
    kit.box("bus.kerb", (30, 0.4, 0.15), (BX, 0.4, 0.075), P("#c8ccd2", 0.8))
    kit.cyl("bus.pole", 0.06, 2.8, (BX + 1.5, 2.8, 1.4), kit.metal("#aab0b8", 0.3), n=8)
    kit.cyl("bus.sign", 0.32, 0.04, (BX + 1.5, 2.74, 2.7), P("#3d74d6", 0.5), rot=(math.pi / 2, 0, 0), n=20)
    kit.cyl("bus.signdot", 0.18, 0.03, (BX + 1.5, 2.715, 2.7), P("#fff8e8", 0.5), rot=(math.pi / 2, 0, 0), n=20)
    kit.box("bus.bench", (1.8, 0.5, 0.1), (BX - 2.0, 3.6, 0.5), P("#7a5230", 0.7))
    kit.box("bus.benchback", (1.8, 0.08, 0.5), (BX - 2.0, 3.85, 0.85), P("#7a5230", 0.7))

    # ============================================================== the planner's door
    PX, PY = G.PLAN
    kit.plane("pl.ground", (30, 14), (PX, 0, 0.0), P("#c9a070", 0.7))
    kit.box("pl.wall", (30, 0.3, 4.0), (PX, 4.15, 2.0), P("#b8467f", 0.8))
    kit.box("pl.base", (30, 0.1, 0.3), (PX, 3.95, 0.15), P("#fff8e8", 0.6))
    door = kit.empty("door", (PX - 0.95, 2.55, 0.0), None, rot=(0, 0, math.radians(-8)))
    kit.box("door.leaf", (1.3, 0.08, 2.2), (0.65, 0, 1.1), P("#5a8ad8", 0.5), door, bevel=0.02)
    kit.sphere("door.knob", 0.05, (1.15, -0.07, 1.05), kit.metal("#e0c070", 0.3), door, seg=8)
    for k, c in enumerate(["#ff4b3a", "#ffd23f", "#3fd0ff"]):
        kit.sphere(f"pl.bal{k}", 0.3, (PX + 1.6 + 0.35 * k, 3.5, 2.3 + 0.2 * (k % 2)), P(c, 0.3), seg=10)

    # ============================================================== the card table
    KX, KY = G.CARD
    kit.plane("cd.ground", (30, 14), (KX, 0, 0.0), P("#8a6a4a", 0.7))
    kit.box("cd.wall", (30, 0.3, 4.0), (KX, 4.15, 2.0), P("#3d7466", 0.8))
    kit.cyl("cd.table", 0.95, 0.06, (KX, 1.9, 0.78), P("#2f7a52", 0.8), n=24)
    kit.cyl("cd.leg", 0.1, 0.75, (KX, 1.9, 0.375), P("#5a3a22", 0.6), n=10)
    kit.cyl("cd.foot", 0.4, 0.05, (KX, 1.9, 0.025), P("#5a3a22", 0.6), n=14)
    for k, (cx, cy, ca) in enumerate([(-0.62, 1.4, 0.4), (0.7, 1.55, 2.1), (-0.15, 2.45, 1.0), (0.4, 2.25, 3.6),
                                       (0.0, 1.2, 5.2), (-0.7, 2.1, 2.7)]):
        kit.box(f"cd.card{k}", (0.16, 0.23, 0.006), (KX + cx, cy + 0.9 - 0.4, 0.816 + 0.002 * k), P("#d8343a" if k % 2 else "#3d74d6", 0.5),
                rot=(0, 0, ca))
    for k, (ccx, ccy, ca) in enumerate([(-1.9, 2.4, 0.6), (1.9, 2.2, -0.5), (-1.2, 3.3, 0.2), (1.4, 3.3, -0.3)]):
        ch = kit.empty(f"cd.chair{k}", (KX + ccx, ccy, 0.0), None, rot=(0, 0, ca))
        kit.box(f"cd.chair{k}.s", (0.5, 0.5, 0.06), (0, 0, 0.45), P("#7a5230", 0.7), ch)
        kit.box(f"cd.chair{k}.b", (0.5, 0.06, 0.5), (0, 0.22, 0.72), P("#7a5230", 0.7), ch)
        for lx_, ly_ in ((-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2)):
            kit.box(f"cd.chair{k}.l{lx_}{ly_}", (0.05, 0.05, 0.45), (lx_, ly_, 0.225), P("#5a3a22", 0.7), ch)

    # ============================================================== the kitchen and the open fridge
    FX, FY = G.FRIDGE
    kit.plane("fr.ground", (30, 14), (FX, 0, 0.0), P("#e8e2d0", 0.5, spec=0.3))
    kit.box("fr.wall", (30, 0.3, 4.0), (FX, 4.15, 2.0), P("#4a7fa0", 0.8))
    kit.box("fr.counter", (2.6, 0.7, 0.95), (FX - 2.2, 3.55, 0.475), P("#8a6a4a", 0.6))
    fw = P("#f4f6f8", 0.35, spec=0.5)
    gx, gy = FX - 0.3, 3.0
    kit.box("fr.back", (1.0, 0.04, 1.85), (gx, gy + 0.46, 0.95), kit.emit("#f0f6ff", 0.9))
    kit.box("fr.l", (0.06, 0.9, 1.9), (gx - 0.53, gy, 0.95), fw)
    kit.box("fr.r", (0.06, 0.9, 1.9), (gx + 0.53, gy, 0.95), fw)
    kit.box("fr.t", (1.12, 0.9, 0.06), (gx, gy, 1.9), fw)
    kit.box("fr.b", (1.12, 0.9, 0.06), (gx, gy, 0.03), fw)
    for k, z in enumerate((0.6, 1.1, 1.5)):
        kit.box(f"fr.sh{k}", (0.98, 0.7, 0.025), (gx, gy - 0.05, z), P("#cfe0f0", 0.2, spec=0.8))
    for k, c in enumerate(["#ff9a3a", "#7be07a", "#ffd23f"]):
        kit.box(f"fr.food{k}", (0.18, 0.18, 0.16), (gx - 0.3 + 0.28 * k, gy - 0.05, 0.7 + 0.5 * (k % 2)), P(c, 0.5))
    dl = kit.empty("fr.door", (gx - 0.53, gy - 0.45, 0.0), None, rot=(0, 0, math.radians(100)))
    kit.box("fr.doorleaf", (1.06, 0.08, 1.9), (0.53, 0, 0.95), fw, dl)
    bx = kit.empty("box", (0, 0, -60))
    kit.box("box.b", (0.36, 0.24, 0.26), (0, 0, 0), P("#fff8e8", 0.6), bx, bevel=0.01)
    kit.box("box.s", (0.37, 0.25, 0.08), (0, 0, 0.02), P("#ff2a20", 0.5), bx)
    reg("box", bx)

    # ============================================================== the stage
    TX, TY = G.STAGE
    kit.plane("st.ground", (30, 14), (TX, 0, 0.0), P("#3a2a5a", 0.5, spec=0.3))
    kit.box("st.wall", (30, 0.3, 4.5), (TX, 4.65, 2.25), P("#6a3a9a", 0.8))
    for k in range(-3, 4):
        kit.box(f"st.cur{k}", (0.9, 0.12, 4.0), (TX + k * 1.4, 4.4, 2.0), P("#b0283a" if k % 2 else "#8a2040", 0.8))

    # a soft gold halo behind each glowing head: a plane whose alpha falls off from the middle
    W["halo"] = {}
    for who in ("mom", "dad", "me", "oth"):
        hm = bpy.data.materials.new(f"halo {who}")
        hm.use_nodes = True
        nt = hm.node_tree
        for n_ in list(nt.nodes):
            nt.nodes.remove(n_)
        outn = nt.nodes.new("ShaderNodeOutputMaterial")
        mixn = nt.nodes.new("ShaderNodeMixShader")
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (1.0, 0.62, 0.15, 1.0)
        em.inputs["Strength"].default_value = 2.6
        tc = nt.nodes.new("ShaderNodeTexCoord")
        gr = nt.nodes.new("ShaderNodeTexGradient")
        gr.gradient_type = "QUADRATIC_SPHERE"
        sq = nt.nodes.new("ShaderNodeMath")
        sq.operation = "MULTIPLY"
        sq.inputs[1].default_value = 0.0
        nt.links.new(tc.outputs["Object"], gr.inputs["Vector"])
        nt.links.new(gr.outputs["Fac"], sq.inputs[0])
        nt.links.new(sq.outputs[0], mixn.inputs[0])
        nt.links.new(tr.outputs[0], mixn.inputs[1])
        nt.links.new(em.outputs[0], mixn.inputs[2])
        nt.links.new(mixn.outputs[0], outn.inputs["Surface"])
        ob = kit.plane(f"halo.{who}", (2.0, 2.0), (0, 0, -90.0), hm, rot=(math.pi / 2, 0, 0))
        noshadow(ob)
        ob.visible_glossy = False
        ob.visible_diffuse = False
        W["halo"][who] = (ob, sq)
    build_tag(kit)
    return {}


def build_tag(kit):
    """The rule meter: a cream plate, a big lightbulb glyph and three glow bars (Mom, Dad, me)."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    plate = kit.emit("#fff1cf", 1.0, "tagplate")
    edge = kit.emit("#2a1a0e", 0.5, "tagedge")
    gold = kit.emit("#ffc21e", 1.6, "taggold")
    dim = kit.emit("#d9cdb2", 0.8, "tagdim")
    ink = kit.emit("#2a1a0e", 0.5, "tagink")
    grey = kit.emit("#8d8a84", 0.7, "taggrey")

    def b(name, size, loc, mat, parent=None):
        ob = kit.box(name, size, loc, mat, parent or root)
        noshadow(ob)
        return ob
    b("tag.edge", (1.0, 0.56, 0.004), (0, 0, 0.0), edge)
    b("tag.plate", (0.95, 0.51, 0.004), (0, 0, 0.004), plate)
    # the bulb: a clear glass globe (pale rim, dark outline) with a glowing gold fill, a filament, a screw base
    glass = kit.emit("#eef6ff", 1.0, "tagglass")
    hot = kit.emit("#ffc21e", 3.0, "taghot")

    def disc(name, r, loc, mat):
        ob = kit.sphere(name, r, loc, mat, root, seg=20)
        ob.scale = (1.0, 1.0, 0.02)
        noshadow(ob)
        return ob
    disc("tag.brim", 0.2, (-0.3, 0.045, 0.006), ink)
    disc("tag.bglass", 0.178, (-0.3, 0.045, 0.010), glass)
    disc("tag.bulb", 0.14, (-0.3, 0.045, 0.014), hot)
    disc("tag.shine", 0.03, (-0.36, 0.11, 0.018), glass)
    b("tag.neckO", (0.17, 0.1, 0.004), (-0.3, -0.115, 0.008), ink)
    b("tag.neck", (0.13, 0.09, 0.004), (-0.3, -0.115, 0.012), glass)
    b("tag.baseO", (0.15, 0.115, 0.004), (-0.3, -0.2, 0.008), ink)
    b("tag.base1", (0.115, 0.035, 0.004), (-0.3, -0.175, 0.012), grey)
    b("tag.base2", (0.115, 0.035, 0.004), (-0.3, -0.225, 0.012), grey)
    # filament: a small V on a stem
    for sx_ in (-1, 1):
        f_ = b(f"tag.fil{sx_}", (0.018, 0.1, 0.004), (-0.3 + sx_ * 0.032, 0.07, 0.022), ink)
        f_.rotation_euler = (0, 0, -sx_ * 0.5)
    b("tag.stem", (0.018, 0.1, 0.004), (-0.3, -0.04, 0.022), ink)
    # three bars: an empty slot, then a gold fill that grows from the bottom
    W["bars"] = []
    for i, (x, dc) in enumerate(zip((0.0, 0.17, 0.34), ("#e0a32a", "#3f8a4e", "#3d74d6"))):
        b(f"tag.slot{i}", (0.12, 0.32, 0.004), (x + 0.02, 0.04, 0.01), ink)
        b(f"tag.dim{i}", (0.1, 0.30, 0.004), (x + 0.02, 0.04, 0.016), dim)
        pivot = kit.empty(f"tag.bar{i}", (x + 0.02, -0.11, 0.022), root)
        fill = kit.box(f"tag.fill{i}", (0.1, 0.30, 0.004), (0, 0.15, 0.0), gold, pivot)
        noshadow(fill)
        W["bars"].append(pivot)
        for nm_, r_, z_, m_ in ((f"tag.doto{i}", 0.062, 0.010, ink), (f"tag.dot{i}", 0.05, 0.014, kit.emit(dc, 1.1, f"tagdot{i}"))):
            disc(nm_, r_, (x + 0.02, -0.19, z_), m_)


# ---------------------------------------------------------------------------------------------- first frame extras
def _first_frame(kit, story):
    from blocky import rig
    W["inited"] = True
    # Dad's grey moustache
    dh = bpy.data.objects.get("dad.headg")
    if dh is not None:
        m = kit.plastic("#a9a9ae", 0.8)
        kit.box("dad.stache", (0.7, 0.08, 0.14), (0, -0.64, -0.2), m, dh, bevel=0.03)
        kit.box("dad.stacheL", (0.12, 0.08, 0.26), (-0.36, -0.64, -0.28), m, dh, bevel=0.03)
        kit.box("dad.stacheR", (0.12, 0.08, 0.26), (0.36, -0.64, -0.28), m, dh, bevel=0.03)
    mh = bpy.data.objects.get("mom.headg")
    if mh is not None:
        g = kit.plastic("#f2c14e", 0.3, spec=0.8)
        for s in (-1, 1):
            kit.sphere(f"mom.ear{s}", 0.11, (s * 0.66, -0.05, -0.3), g, mh, seg=8)
    for who in ("mom", "dad"):
        hg = bpy.data.objects.get(f"{who}.headg")
        if hg is None:
            continue
        sg = kit.plastic("#101014", 0.2, spec=0.8)
        sh = kit.empty(f"{who}.shades", (0, 0, 0), hg)
        kit.box(f"{who}.shades.l", (0.4, 0.05, 0.2), (-0.22, -0.66, 0.1), sg, sh, bevel=0.02)
        kit.box(f"{who}.shades.r", (0.4, 0.05, 0.2), (0.22, -0.66, 0.1), sg, sh, bevel=0.02)
        kit.box(f"{who}.shades.b", (0.12, 0.05, 0.05), (0, -0.66, 0.15), sg, sh)
        W["obj"][f"{who}.shades"] = sh
    # emission on the skin: the head's material takes the face texture as its glow, the arms' skin takes its colour
    W["glowmat"] = {}
    for who in ("mom", "dad", "me", "roommate", "planner", "woman"):
        ch = rig.CHARS.get(who)
        if ch is None:
            continue
        hm = ch.head_mat
        nt = hm.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs[0].default_value = 1.0
        mix.inputs[7].default_value = (1.0, 0.86, 0.5, 1.0)
        tex = ch.face_tex
        nt.links.new(tex.outputs["Color"], mix.inputs[6])
        nt.links.new(mix.outputs[2], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 0.0
        arm = bpy.data.objects.get(f"{who}.skinarm1") or bpy.data.objects.get(f"{who}.skinarm-1")
        am = arm.active_material if arm is not None else None
        if am is not None:
            ab = am.node_tree.nodes["Principled BSDF"]
            c = ab.inputs["Base Color"].default_value
            ab.inputs["Emission Color"].default_value = (min(1.0, c[0] * 1.0), min(1.0, c[1] * 0.86), min(1.0, c[2] * 0.5), 1.0)
            ab.inputs["Emission Strength"].default_value = 0.0
        W["glowmat"][who] = (bsdf, ab if am is not None else None)


def _head_pos(who):
    hg = bpy.data.objects.get(f"{who}.headg")
    return hg.matrix_world.translation.copy() if hg is not None else None


def animate(kit, story, tl, t, ctx):
    bpy.context.view_layer.update()
    if not W.get("inited"):
        _first_frame(kit, story)
    look = look_at(tl, t)
    gains = {}
    az, el = look["az"] * D2R, look["el"] * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    so = kit.LIGHTS["sun"]["obj"]
    so.location = d * 60
    kit.aim(so, (0, 0, 0))
    kit.LIGHTS["sun"]["light"].color = look["sun_col"]
    kit.LIGHTS["fill"]["light"].color = look["fill_col"]
    kit.LIGHTS["front"]["light"].color = look["front_col"]
    gains["sun"], gains["fill"], gains["front"] = look["sun"], look["fill"], look["front"]
    for i_ in range(3):
        gains[f"pend{i_}"] = look["pend"]
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*look["sky"], 1.0)
    bg.inputs["Strength"].default_value = look["sky_str"]

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
        cur = dict(x=x0, y=y0, z=z0, yaw=r0 / D2R)
        prev = dict(cur)
        out = dict(cur)
        for c in cs:
            if c["t"] > t:
                break
            prev = dict(out)
            tgt = dict(prev)
            for k in ("x", "y", "z", "yaw"):
                if k in c:
                    tgt[k] = c[k]
            dur = c.get("dur", 0.0)
            if dur > 0 and t < c["t"] + dur:
                u = ss((t - c["t"]) / dur)
                out = {k: prev[k] + (tgt[k] - prev[k]) * u for k in tgt}
            else:
                out = tgt
        ob.location = (out["x"], out["y"], out["z"])
        ob.rotation_euler = (ob.rotation_euler.x, ob.rotation_euler.y, out["yaw"] * D2R)

    # which pizza: the whole pie, or only the last slice (shot S10b)
    st = sample("pie", tl, t, {"v": 1.0})
    _hide(W["obj"]["pie"], st["v"] < 0.5)
    _hide(W["obj"]["slice"], st["v"] > 0.5)

    gs_ = sample("gshadow", tl, t, {"v": 0.0})["v"]
    for d_ in W.get("gsh", []):
        _hide(d_, gs_ < 0.5)

    # sunglasses
    for who in ("mom", "dad"):
        sh = W["obj"].get(f"{who}.shades")
        if sh is not None:
            v = sample("shades", tl, t, {"v": 0.0}, key=who)
            _hide(sh, v["v"] < 0.5)

    # glow: levels, emission on the skin, the lamp that follows the head
    oth = None
    for who in ("roommate", "planner", "woman"):
        a = bpy.data.objects.get(who)
        if a is not None and not a.hide_render:
            oth = who
    levels = {"mom": sample("gmom", tl, t, {"v": 0.0})["v"], "dad": sample("gdad", tl, t, {"v": 0.0})["v"],
              "me": sample("gme", tl, t, {"v": 0.0})["v"]}
    if oth:
        levels[oth] = sample("goth", tl, t, {"v": 0.0})["v"]
    for who, (bsdf, arms) in W["glowmat"].items():
        v = levels.get(who, 0.0)
        bsdf.inputs["Emission Strength"].default_value = EM * v
        if arms is not None:
            arms.inputs["Emission Strength"].default_value = EM * v
    lname = {"mom": "glowmom", "dad": "glowdad", "me": "glowme"}
    for who, ln in list(lname.items()) + ([(oth, "glowoth")] if oth else []):
        ob = bpy.data.objects.get(who)
        hp = _head_pos(who)
        L = kit.LIGHTS[ln]["obj"]
        vis = ob is not None and not ob.hide_render
        if hp is not None and vis:
            L.location = (hp.x - 0.05, hp.y - 0.45, hp.z + 0.5)
            gains[ln] = levels.get(who, 0.0)
        else:
            gains[ln] = 0.0
    if not oth:
        gains["glowoth"] = 0.0

    # the halos
    for who in ("mom", "dad", "me", "oth"):
        ob, sq = W["halo"][who]
        real = oth if who == "oth" else who
        o_ = bpy.data.objects.get(real) if real else None
        hp = _head_pos(real) if real else None
        v = levels.get(real, 0.0) if real else 0.0
        if hp is None or o_ is None or o_.hide_render or v < 0.01:
            ob.location = (0, 0, -90.0)
            continue
        ob.location = (hp.x, hp.y + 0.45, hp.z - 0.1)
        r = 0.75 + 0.15 * max(0.0, v - 0.8)
        ob.scale = (r, r, r)
        sq.inputs[1].default_value = HALO * min(v, 1.9)
    # the tag's bars
    br = sample("bar", tl, t, {"m": 1.0, "d": 1.0, "s": 0.0})
    for i, k in enumerate(("m", "d", "s")):
        p = W["bars"][i]
        p.scale = (1.0, max(0.001, br[k]), 1.0)
    # the whole booth warms for L31 on
    bg_ = sample("bglow", tl, t, {"v": 0.0})
    gains["bglow"] = bg_["v"]
    fr_ = sample("fridgeglow", tl, t, {"v": 0.0})
    gains["fridge"] = 1.0
    gains["spot"] = sample("spot", tl, t, {"v": 0.0})["v"]
    # the waiter's arm
    wv = sample("waiter", tl, t, {"v": 0.0})
    W["obj"]["wa"].hide_render = wv["v"] < 0.5
    for c in W["obj"]["wa"].children_recursive:
        c.hide_render = wv["v"] < 0.5
    if wv["v"] < 0.5:
        W["obj"]["wa"].location.z = -60.0
    # moths circle the two glowing heads
    mv_ = sample("moths", tl, t, {"v": 0.0})["v"]
    heads = [_head_pos("mom"), _head_pos("dad")]
    for k, m in enumerate(W["moths"]):
        hp = heads[k % 2]
        if mv_ < 0.02 or hp is None:
            m.location = (0, 0, -80)
            continue
        a = t * (0.9 + 0.12 * k) + k * 1.1
        r = 0.6 + 0.12 * (k % 3)
        m.location = (hp.x + r * math.cos(a), hp.y - 0.4 + 0.25 * math.sin(a * 0.7), hp.z + 0.05 + 0.4 * math.sin(a * 1.3 + k))
        m.rotation_euler = (0.3, 0, a)
        m.children[0].rotation_euler = (0, 0.7 * math.sin(t * 22 + k), 0)
        m.children[1].rotation_euler = (0, -0.7 * math.sin(t * 22 + k), 0)
        m.scale = (3.4 * mv_,) * 3

    # the tag sits top-left at a fixed angular size, whatever the lens
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
    tag = W["tag"]
    s = 0.82 * w2
    tag.scale = (s, s, s)
    tag.location = (-w2 + 0.5 * s + 0.05 * w2, 0.98 * h2 - 0.28 * s - 0.06 * w2 - 0.12 * h2, -1.0)

    # who sits: legs straight out forward, hips on the seat
    sits = {}
    for c in tl["cues"]:
        if c["name"] == "sit" and c["t"] <= t:
            sits[c["who"]] = c
    for who, c in sits.items():
        root = bpy.data.objects.get(who)
        if c.get("on") and root is not None:
            root.location.z += c.get("z", 0.67) - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    return gains
