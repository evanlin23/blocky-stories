"""ep102 "aunt peaches": a green peach valley under a blue sky.

Rule meter: a cream odometer plate in the top-left corner of every frame (a peach glyph that is grey until I eat one, a
road glyph, and three big digits of miles to Aunt Clem's gate). It is a child of the camera.
Cues (story.json) drive: look (day / morn / dusk / noon), odo (the digits), gold (the peach glyph), mv (move anything
named: peaches, cars, the gate leaf), sill (how many peaches on the sill), rock (the porch swing), gone (the ridge road
behind the car), lane (the lane behind the car at the gate), sit (who is seated).
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


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def _L(**kw):
    base = dict(sun=3.6, sun_col="#fff0d8", el=48.0, az=205.0, fill=0.9, fill_col="#fff0e0", sky="#7ec8ff",
                sky_str=1.0, front=0.6)
    base.update(kw)
    return base


LOOKS = {
    "day": _L(),
    "noon": _L(sun=4.0, el=78.0, az=200.0, front=0.5),
    "morn": _L(sun=3.0, sun_col="#ffe0b0", el=24.0, az=215.0, fill=1.0, fill_col="#ffe6d0", sky="#a8d8ff", front=0.9),
    "dusk": _L(sun=2.3, sun_col="#ffb070", el=11.0, az=200.0, fill=1.6, fill_col="#c0d4ff", sky="#ffb27a", sky_str=0.85,
               front=1.6),
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


def reg(name, ob):
    W["obj"][name] = ob
    W["init"][name] = (ob.location.x, ob.location.y, ob.location.z, ob.rotation_euler.z)
    return ob


# ---------------------------------------------------------------------------------------------- parts
def tree(kit, name, x, y, h=5.0, tint="#d4f0b8", fruit=0, rng=0):
    try:
        kit.prop("commontree_1", (x, y, 0), height=h, tint=tint)
    except Exception:
        kit.cyl(f"{name}.trunk", 0.3, h * 0.45, (x, y, h * 0.22), kit.plastic("#7a5230", 0.8), n=8)
        kit.sphere(f"{name}.crown", h * 0.28, (x, y, h * 0.68), kit.plastic("#5fae4a", 0.8), seg=10)
    if fruit:
        pm = kit.plastic("#ff9a5a", 0.5, spec=0.3)
        for k in range(fruit):
            a = (k * 2.4 + rng) % 6.28
            r = 0.9 + 0.25 * (k % 3)
            kit.sphere(f"{name}.pe{k}", 0.11, (x + math.cos(a) * r, y - abs(math.sin(a)) * r - 0.2, h * 0.55 + 0.2 * (k % 4)), pm, seg=6)


def hill(kit, name, x, y, r, sy, col, sz=0.32):
    ob = kit.sphere(name, r, (x, y, -r * (1 - sz) + 0.0), kit.plastic(col, 0.9, spec=0.02), seg=14)
    ob.scale = (1.0, sy, sz)
    noshadow(ob)
    return ob


def house(kit, name, x, y, w, d, h, col, face=-1, roof="#b8604a", glow=True):
    wall = kit.plastic(col, 0.85, spec=0.05)
    kit.box(f"{name}.body", (w, d, h), (x, y, h / 2), wall)
    kit.box(f"{name}.roof", (w + 0.7, d + 0.7, 0.55), (x, y, h + 0.27), kit.plastic(roof, 0.7, spec=0.1))
    kit.box(f"{name}.roof2", (w * 0.8, d * 0.8, 0.5), (x, y, h + 0.7), kit.plastic(roof, 0.7, spec=0.1))
    fy = y + face * (d / 2)
    wm = kit.emit("#ffd98a", 2.2) if glow else kit.plastic("#7fa8c8", 0.2, spec=0.8)
    n = max(1, int(w // 2.6))
    for i in range(n):
        wx = x - w / 2 + (i + 0.5) * w / n
        kit.box(f"{name}.win{i}", (1.0, 0.1, 1.2), (wx, fy + face * 0.04, 1.8), wm)
        kit.box(f"{name}.fr{i}", (1.3, 0.08, 1.5), (wx, fy + face * 0.02, 1.8), kit.plastic("#fff8e8", 0.7))


def peach(kit, name, loc=(0, 0, -50), r=0.12):
    root = kit.empty(name, loc)
    pm = kit.plastic("#ff9355", 0.35, spec=0.5)
    s = kit.sphere(f"{name}.fruit", r, (0, 0, 0), pm, root, seg=14)
    s.scale = (1.0, 1.0, 0.94)
    kit.sphere(f"{name}.blush", r * 0.75, (r * 0.35, -r * 0.45, r * 0.25), kit.plastic("#ff6a4a", 0.4, spec=0.4), root, seg=8)
    kit.box(f"{name}.leaf", (r * 0.9, r * 0.35, 0.02), (r * 0.3, 0, r * 1.0), kit.plastic("#4fae4a", 0.6), root, rot=(0, 0.3, 0.5))
    kit.box(f"{name}.stem", (0.02, 0.02, r * 0.3), (0, 0, r * 0.98), kit.plastic("#6b4326", 0.8), root)
    return reg(name, root)


def car(kit, name, col, loc, openc=True, yaw=0.0):
    """Faces -y (yaw 0). Seats: driver at local (+0.45, +0.3)."""
    root = kit.empty(name, loc)
    body = kit.plastic(col, 0.35, spec=0.5)
    dark = kit.plastic("#2a2d33", 0.7)
    kit.box(f"{name}.base", (1.86, 4.1, 0.5), (0, 0, 0.5), body, root, bevel=0.06)
    kit.box(f"{name}.hood", (1.8, 1.3, 0.14), (0, -1.35, 0.82), body, root, bevel=0.05)
    kit.box(f"{name}.trunk", (1.8, 0.9, 0.14), (0, 1.55, 0.82), body, root, bevel=0.05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"{name}.wh{sx}{sy}", 0.36, 0.26, (sx * 0.96, sy * 1.3, 0.36), dark, root, rot=(0, math.pi / 2, 0), n=14)
        kit.box(f"{name}.head{sx}", (0.32, 0.06, 0.18), (sx * 0.6, -2.07, 0.62), kit.emit("#fff4c8", 2.0), root)
        kit.box(f"{name}.tail{sx}", (0.3, 0.06, 0.16), (sx * 0.65, 2.07, 0.62), kit.emit("#ff4a3a", 1.5), root)
    glass = kit.plastic("#9fc8e8", 0.15, spec=0.9)
    if openc:
        kit.box(f"{name}.dash", (1.76, 0.5, 0.42), (0, -0.78, 0.88), body, root, bevel=0.05)
        kit.box(f"{name}.wframe", (1.7, 0.06, 0.06), (0, -0.98, 1.1), body, root)
        for sx in (-1, 1):
            kit.box(f"{name}.seat{sx}", (0.64, 0.7, 0.14), (sx * 0.45, 0.45, 0.62), dark, root, bevel=0.04)
            kit.box(f"{name}.sback{sx}", (0.64, 0.12, 0.6), (sx * 0.45, 0.85, 0.95), dark, root, bevel=0.04)
        kit.cyl(f"{name}.wheel", 0.2, 0.05, (0.45, -0.52, 1.12), dark, root, rot=(1.1, 0, 0), n=14)
    else:
        kit.box(f"{name}.cabin", (1.72, 2.3, 0.62), (0, 0.3, 1.1), glass, root, bevel=0.06)
        kit.box(f"{name}.roof", (1.8, 2.4, 0.1), (0, 0.3, 1.46), body, root, bevel=0.05)
    return reg(name, root)


def mirror(kit, root):
    """The rear-view mirror: a road strip on both faces so it reads from the front too."""
    kit.box("mirror.stem", (0.05, 0.05, 0.4), (0, -0.9, 1.3), kit.plastic("#2a2d33", 0.6), root)
    m = kit.empty("mirror", (0, -0.9, 1.55), root)
    kit.box("mirror.frame", (0.62, 0.07, 0.24), (0, 0, 0), kit.plastic("#2a2d33", 0.6), m, bevel=0.02)
    W["mroad"] = []
    for s, yy in (("a", 0.045), ("b", -0.045)):
        kit.box(f"mirror.sky{s}", (0.54, 0.02, 0.17), (0, yy, 0), kit.emit("#9fd8ff", 1.2), m)
        kit.box(f"mirror.grass{s}", (0.54, 0.02, 0.07), (0, yy * 1.2, -0.05), kit.emit("#5fae4a", 0.9), m)
        W["mroad"].append(kit.box(f"mirror.road{s}", (0.22, 0.02, 0.09), (0, yy * 1.4, -0.03), kit.emit("#6b6f78", 0.9), m))
    W["mirror"] = m
    return m


# ---------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    P = kit.plastic
    grass = kit.grime("#6fc058", 0.8, 1.6, "grass", 0.95)
    grass2 = kit.grime("#86d06a", 0.8, 1.6, "grass2", 0.95)
    dirt = P("#d9b27a", 0.95, spec=0.02)
    asphalt = P("#6d7178", 0.85, spec=0.05)
    white = P("#f8f5ee", 0.8, spec=0.05)
    wood = P("#b57e4c", 0.75, spec=0.08)
    woodd = P("#8a5a34", 0.8, spec=0.05)
    iron = kit.metal("#3a3d42", 0.5)

    # lights (gains set in animate)
    sun = kit.light("sun", "SUN", (0, -30, 40), 1.0, "#fff0d8", size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#cfe6ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    front = kit.light("front", "SUN", (-10, -30, 20), 1.0, "#ffd2ae", shadow=False)
    front.data.angle = 0.4
    kit.aim(front, (0, 0, 0))
    for nm, c, z in (("room", G.ROOM, 2.6), ("kit", G.KIT, 2.8), ("bus", G.BUS, 2.6)):
        kit.light(nm, "POINT", (c[0], c[1] - 2.0, z), 220.0, "#ffe6c0", size=0.5, shadow=False)

    # world ground
    kit.plane("ground", (1500, 500), (100, 0, -0.02), grass)

    # ================================================================== Aunt Clem's farm
    # the lane runs from the gate away along -y
    W["lane"] = []
    for i in range(16):
        W["lane"].append(kit.box(f"lane{i}", (4.4, 6.0, 0.06), (0, -11.0 - i * 6.0, 0.02), dirt))
    for i in range(6):
        kit.box(f"path{i}", (2.2, 1.6, 0.05), (0, -7.0 + i * 1.7, 0.03), dirt)
    # fence along y = -8 with the gate gap
    for sx in (-1, 1):
        for k in range(1, 9):
            x = sx * (2.0 + k * 3.0)
            kit.box(f"fpost{sx}{k}", (0.2, 0.2, 1.2), (x, -8.0, 0.6), wood)
        L = 24.0
        for z in (0.55, 1.0):
            kit.box(f"frail{sx}{z}", (L, 0.1, 0.12), (sx * (2.0 + L / 2), -8.0, z), wood)
    for sx in (-1, 1):
        kit.box(f"gpost{sx}", (0.34, 0.34, 1.9), (sx * 1.9, -8.0, 0.95), woodd, bevel=0.03)
        kit.box(f"gcap{sx}", (0.46, 0.46, 0.1), (sx * 1.9, -8.0, 1.95), woodd)
    gl = kit.empty("gateleaf", (-1.72, -8.0, 0))              # hinged at the -x post, closed along +x
    for z in (0.35, 0.75, 1.15, 1.55):
        kit.box(f"gl.rail{z}", (3.4, 0.1, 0.13), (1.7, 0, z), wood, gl)
    for k in range(5):
        kit.box(f"gl.up{k}", (0.12, 0.1, 1.4), (0.2 + k * 0.7, 0, 0.9), wood, gl)
    kit.box("gl.diag", (3.6, 0.09, 0.1), (1.7, 0.02, 0.95), wood, gl, rot=(0, 0.42, 0))
    kit.box("gl.latch", (0.35, 0.12, 0.1), (3.3, 0.05, 1.15), iron, gl)
    kit.box("gl.latchdrop", (0.06, 0.12, 0.3), (3.4, 0.05, 1.0), iron, gl)
    reg("gateleaf", gl)
    W["lgrass"] = []
    for k in range(70):
        x = ((k * 37) % 13 - 6.0) * 0.5
        y = -12.0 - (k * 7) % 60
        try:
            W["lgrass"].append(kit.prop("grass", (x, y, 0), height=0.8 + 0.3 * (k % 3), tint="#bfe58a"))
        except Exception:
            W["lgrass"].append(kit.box(f"lg{k}", (0.1, 0.1, 0.8), (x, y, 0.4), P("#7fc860", 0.8)))
    # house, deck, rail
    kit.plane("yard", (60, 14), (0, 0, 0.01), kit.grime("#8bd070", 0.8, 1.6, "yard", 0.95))
    kit.box("deck", (16.4, 4.6, 0.45), (0, 3.8, 0.225), P("#c99a66", 0.75, spec=0.08))
    for i in range(3):
        kit.box(f"pstep{i}", (3.0, 0.5, 0.15 * (i + 1)), (0, 1.25 - i * 0.55 + 0.55, 0.075 * (i + 1) * 0.0 + 0.075 * (3 - i)), wood)
    kit.box("fhouse", (16.0, 6.0, 5.2), (0, 9.0, 2.6), white)
    kit.box("froof", (17.4, 7.4, 0.6), (0, 9.0, 5.45), P("#8a6a5a", 0.7, spec=0.1))
    kit.box("froof2", (14.0, 5.0, 0.8), (0, 9.0, 6.0), P("#8a6a5a", 0.7, spec=0.1))
    kit.box("fdoor", (1.5, 0.12, 2.5), (0.0, 5.94, 1.7), P("#d96a4a", 0.5, spec=0.3))
    wglass = P("#7fb2d8", 0.2, spec=0.8)
    for x in (-5.0, -2.8, 3.2, 5.4):
        kit.box(f"fwin{x}", (1.3, 0.1, 1.6), (x, 5.94, 2.0), wglass)
        kit.box(f"fwf{x}", (1.7, 0.08, 2.0), (x, 5.96, 2.0), P("#fff8e8", 0.7))
    for x in (2.0, 3.6, 5.2, 6.8, 8.0):
        kit.box(f"rpost{x}", (0.18, 0.18, 1.0), (x, 1.6, 0.95), white)
    kit.box("rtop", (6.4, 0.22, 0.1), (5.0, 1.6, 1.45), white)
    kit.box("rmid", (6.4, 0.1, 0.1), (5.0, 1.6, 0.9), white)
    # the porch swing: a frame, two chains, a seat; two strokes on the iron plate where a chain meets the beam
    sx0, sy0 = -5.0, 3.2
    for sx in (-1, 1):
        kit.box(f"swpost{sx}", (0.22, 0.22, 3.0), (sx0 + sx * 1.9, sy0, 0.45 + 1.5), wood)
    kit.box("swbeam", (4.2, 0.26, 0.26), (sx0, sy0, 3.45), wood)
    sw = kit.empty("swing", (sx0, sy0, 3.3))
    for sx in (-1, 1):
        kit.box(f"chain{sx}", (0.05, 0.05, 2.3), (sx * 1.3, 0, -1.15), iron, sw)
    kit.box("swseat", (2.9, 0.8, 0.12), (0, 0, -2.3), P("#e8d4a0", 0.7, spec=0.1), sw, bevel=0.03)
    kit.box("swback", (2.9, 0.1, 0.8), (0, 0.38, -1.9), P("#e8d4a0", 0.7, spec=0.1), sw, bevel=0.03)
    kit.box("swarm", (0.14, 0.7, 0.1), (-1.45, -0.0, -2.0), wood, sw)
    kit.box("swarm2", (0.14, 0.7, 0.1), (1.45, -0.0, -2.0), wood, sw)
    kit.box("swplate", (0.34, 0.06, 0.34), (1.3, -0.17, 0.02), iron, sw)         # on the beam, in the chain's top
    for k in range(2):
        kit.box(f"swstroke{k}", (0.04, 0.02, 0.2), (1.24 + k * 0.12, -0.21, 0.02), P("#ff9a5a", 0.5), sw, rot=(0, 0, 0.35))
    reg("swing", sw)
    # items on the rail: keys
    ky_ = kit.empty("keys", (5.4, 1.56, 1.52))
    kmat = P("#ffd23f", 0.35, spec=0.5)
    rmat = P("#e8ecf2", 0.3, spec=0.5)
    for nm_, sz_, lc_ in (("t", (0.26, 0.04, 0.04), (0, 0, 0.42)), ("b", (0.26, 0.04, 0.04), (0, 0, 0.24)),
                          ("l", (0.04, 0.04, 0.22), (-0.11, 0, 0.33)), ("r", (0.04, 0.04, 0.22), (0.11, 0, 0.33))):
        kit.box(f"keys.ring{nm_}", sz_, lc_, rmat, ky_)
    for i_, x_ in enumerate((-0.06, 0.06)):
        kit.box(f"keys.blade{i_}", (0.07, 0.03, 0.24), (x_, -0.01, 0.12), kmat, ky_)
        kit.box(f"keys.tooth{i_}", (0.05, 0.03, 0.04), (x_ + (0.05 if i_ else -0.05), -0.01, 0.06 + 0.06 * i_), kmat, ky_)
    kit.box("keys.fob", (0.12, 0.04, 0.16), (0.0, -0.03, 0.3), P("#ff5a4a", 0.5), ky_)
    ky_.scale = (0.7, 0.7, 0.7)
    reg("keys", ky_)
    # orchard: peach trees in rows both sides and behind
    k = 0
    for row in range(5):
        for col in range(-6, 7):
            x = col * 5.0 + (2.5 if row % 2 else 0)
            y = -4.0 + row * 7.0 + 20.0
            if abs(x) < 6.0 and y < 30:
                continue
            tree(kit, f"or{k}", x, y, 4.6 + 0.4 * (k % 3), "#d4f0b8" if k % 2 else "#c8e8a8", fruit=3 if k % 4 == 0 else 0, rng=k)
            k += 1
    for j, (x, y) in enumerate([(-14, 8), (-18, 2), (-12, -2), (14, 8), (18, 3), (12, -3), (-26, 6), (26, 6)]):
        tree(kit, f"nt{j}", x, y, 5.2 + 0.4 * (j % 3), "#d4f0b8", fruit=5, rng=j)
    # the valley below the gate (camera looks -y from the porch): hills and warm farmhouses
    for j, (x, y, r, c) in enumerate([(-70, -110, 60, "#7cc464"), (60, -120, 70, "#6fb85a"), (0, -150, 90, "#8acc72"),
                                      (-90, 60, 70, "#7cc464"), (90, 70, 70, "#6fb85a"), (0, 110, 100, "#86c870")]):
        hill(kit, f"vh{j}", x, y, r, 1.0, c)
    for j, (x, y) in enumerate([(-30, -48), (-12, -62), (22, -52), (42, -70), (-46, -78), (6, -88), (30, -100)]):
        house(kit, f"vf{j}", x, y, 7.0 + (j % 2) * 2, 5.0, 3.6, "#f8f5ee", face=+1, roof="#b8604a")

    # ================================================================== mailbox row
    mx, my = G.MAIL
    kit.plane("mlane", (80, 4.4), (mx, my, 0.02), dirt)
    cols = ["#ee5a4a", "#4a8ad8", "#ffd23f", "#4fae4a", "#f6f0e6", "#a05ad8", "#ff9a5a", "#4ac8c0"]
    for i in range(8):
        x = mx - 14 + i * 4.0
        kit.box(f"mbpost{i}", (0.14, 0.14, 1.1), (x, my + 3.6, 0.55), woodd)
        kit.box(f"mbox{i}", (0.5, 0.85, 0.42), (x, my + 3.6, 1.3), P(cols[i], 0.5, spec=0.3), bevel=0.05)
        kit.box(f"mbflag{i}", (0.05, 0.05, 0.3), (x + 0.3, my + 3.4, 1.45), P("#ee3a3a", 0.5))
    for j in range(14):
        tree(kit, f"mt{j}", mx - 36 + j * 5.5, my + 12 + (j % 3) * 3.5, 5.0 + 0.4 * (j % 3), "#d4f0b8", fruit=2 if j % 3 == 0 else 0, rng=j)
    for j, (x, y, r, c) in enumerate([(-30, 70, 60, "#7cc464"), (40, 75, 70, "#6fb85a")]):
        hill(kit, f"mh{j}", mx + x, my + y, r, 1.0, c)
    house(kit, "mfar", mx + 16, my + 24, 8.0, 5.0, 3.6, "#f8f5ee")

    # ================================================================== gas station and picnic table
    gx, gy = G.GAS
    kit.plane("gpad", (34, 16), (gx, gy - 1.0, 0.025), P("#7d8088", 0.9, spec=0.03))
    kit.box("gsbody", (11.0, 5.0, 3.5), (gx, gy + 8.0, 1.75), white)
    kit.box("gsroof", (11.6, 5.6, 0.3), (gx, gy + 8.0, 3.65), P("#c04a3a", 0.7))
    kit.box("gspar", (11.6, 0.3, 0.5), (gx, gy + 5.4, 3.95), P("#c04a3a", 0.7))
    kit.box("gsdoor", (1.6, 0.1, 2.4), (gx - 2.0, gy + 5.46, 1.2), P("#4ac8c0", 0.5, spec=0.3))
    kit.box("gswin", (3.4, 0.1, 1.5), (gx + 2.2, gy + 5.46, 1.7), kit.emit("#ffe2a0", 2.0))
    for i in range(16):
        kit.box(f"gsawn{i}", (0.8, 3.4, 0.1), (gx - 6.0 + i * 0.8, gy + 0.3, 3.4), P("#e8493a" if i % 2 else "#fffaf0", 0.6),
                rot=(0.0, 0, 0))
    for sx in (-1, 1):
        kit.box(f"gspole{sx}", (0.22, 0.22, 3.3), (gx + sx * 5.6, gy - 1.2, 1.65), white)
    kit.box("pump", (0.8, 0.6, 1.5), (gx + 1.0, gy, 0.75), P("#e8493a", 0.4, spec=0.3), bevel=0.05)
    kit.box("pumpface", (0.5, 0.06, 0.5), (gx + 1.0, gy - 0.32, 1.15), P("#fff8e8", 0.6))
    kit.box("pumpisl", (1.8, 1.4, 0.2), (gx + 1.0, gy, 0.1), P("#c9c9cf", 0.8))
    kit.cyl("hose", 0.04, 0.9, (gx + 1.45, gy - 0.32, 0.9), iron, n=6)
    kit.box("gsroofrail", (11.6, 0.1, 0.1), (gx, gy + 5.5, 4.35), P("#c04a3a", 0.7))
    # picnic table and the pie
    tx, ty = gx - 11.0, gy - 1.0
    kit.box("pt.top", (1.1, 2.4, 0.1), (tx, ty, 0.82), wood)
    for sx in (-1, 1):
        kit.box(f"pt.bench{sx}", (0.4, 2.4, 0.1), (tx + sx * 0.95, ty, 0.5), wood)
        kit.box(f"pt.leg{sx}", (0.1, 2.2, 0.8), (tx + sx * 0.4, ty, 0.4), woodd)
    kit.cyl("pie.tin", 0.34, 0.06, (tx, ty, 0.91), kit.metal("#c0c4cc", 0.4), n=20)
    kit.cyl("pie.fill", 0.3, 0.1, (tx, ty, 0.97), P("#d99a4a", 0.7, spec=0.1), n=20)
    kit.box("pie.gap", (0.34, 0.26, 0.14), (tx + 0.17, ty - 0.14, 0.98), P("#8a5a34", 0.8), rot=(0, 0, 0.5))
    for sx in (-1, 1):
        kit.box(f"pie.fork{sx}", (0.2, 0.04, 0.02), (tx + sx * 0.45, ty, 0.88), kit.metal("#d0d4dc", 0.3))
    for j, (x, y, r, c) in enumerate([(-30, 70, 60, "#7cc464"), (40, 75, 70, "#6fb85a")]):
        hill(kit, f"gh{j}", gx + x, gy + y, r, 1.0, c)
    for j in range(10):
        tree(kit, f"gt{j}", gx - 30 + j * 7, gy + 18 + (j % 2) * 4, 5.2, "#d4f0b8", fruit=2 if j % 3 == 0 else 0, rng=j)

    # ================================================================== the guest room
    rx, ry = G.ROOM
    rw = P("#f6e2c0", 0.85, spec=0.05)
    kit.plane("rfloor", (9, 8), (rx, ry, 0.03), kit.planks("#c9976a", "#b78456", 1.0))
    kit.box("rback", (9, 0.3, 3.4), (rx, ry + 3.6, 1.7), rw)
    for sx in (-1, 1):
        kit.box(f"rside{sx}", (0.3, 8, 3.4), (rx + sx * 4.5, ry, 1.7), rw)
    kit.box("rwinframe", (2.0, 0.1, 1.9), (rx + 0.6, ry + 3.42, 1.9), P("#fff8e8", 0.7))
    kit.box("rwinglass", (1.7, 0.06, 1.6), (rx + 0.6, ry + 3.38, 1.9), kit.emit("#a8dcff", 1.1))
    kit.box("rsill", (2.4, 0.5, 0.1), (rx + 0.6, ry + 3.2, 0.95), P("#fff8e8", 0.7))
    kit.box("rbedb", (2.2, 3.2, 0.5), (rx - 2.3, ry + 1.6, 0.25), wood)
    kit.box("rbedm", (2.0, 3.0, 0.3), (rx - 2.3, ry + 1.6, 0.65), P("#fff8e8", 0.8))
    kit.box("rquilt", (2.1, 2.0, 0.12), (rx - 2.3, ry + 1.2, 0.86), kit.checker("#ffd34d", "#fff0b8", 4.0)
            if hasattr(kit, "checker") else P("#ffd34d", 0.8))
    kit.box("rpillow", (1.2, 0.7, 0.2), (rx - 2.3, ry + 2.7, 0.9), P("#ffffff", 0.9))
    kit.box("rduffel", (1.2, 0.6, 0.5), (rx - 2.2, ry + 0.2, 1.1), P("#4a6a8a", 0.8), rot=(0, 0, 0.2))
    kit.box("rdoorframe", (1.7, 0.16, 2.7), (rx + 3.1, ry + 3.42, 1.35), P("#fff8e8", 0.7))
    kit.box("rdoorhall", (1.4, 0.08, 2.5), (rx + 3.1, ry + 3.5, 1.25), kit.emit("#ffe6b0", 1.0))
    # the old photo (no text): two sisters under a peach tree
    px, py, pz = rx - 3.4, ry + 3.42, 2.0
    pl = lambda c: P(c, 0.9)
    kit.box("photo.frame", (2.0, 0.08, 1.6), (px, py, pz), pl("#5a3b24"))
    kit.box("photo.bg", (1.8, 0.05, 1.4), (px, py - 0.06, pz), pl("#f4e6c0"))
    kit.box("photo.sky", (1.8, 0.02, 0.6), (px, py - 0.075, pz + 0.4), pl("#bfe4ff"))
    kit.box("photo.trunk", (0.12, 0.03, 0.7), (px, py - 0.09, pz - 0.05), pl("#7a5230"))
    kit.sphere("photo.crown", 0.4, (px, py - 0.13, pz + 0.38), pl("#6fb85a"), seg=8).scale = (1.3, 0.1, 0.9)
    for i, (dx, c, hc) in enumerate([(-0.5, "#2fa8a0", "#18120e"), (0.5, "#ffd34d", "#8a5a34")]):
        kit.box(f"photo.b{i}", (0.3, 0.03, 0.5), (px + dx, py - 0.1, pz - 0.38), pl(c))
        kit.box(f"photo.h{i}", (0.28, 0.03, 0.28), (px + dx, py - 0.11, pz - 0.0), pl("#f0c8a0"))
        kit.box(f"photo.hr{i}", (0.3, 0.03, 0.1), (px + dx, py - 0.12, pz + 0.12), pl(hc))
        for sx in (-1, 1):
            kit.box(f"photo.e{i}{sx}", (0.04, 0.03, 0.04), (px + dx + sx * 0.07, py - 0.125, pz + 0.02), pl("#1c120c"))
        kit.box(f"photo.s{i}", (0.12, 0.03, 0.025), (px + dx, py - 0.125, pz - 0.07), pl("#7a3a30"))
    kit.box("photo.glasses", (0.22, 0.03, 0.04), (px - 0.5, py - 0.13, pz + 0.02), pl("#2a2a2a"))
    kit.box("photo.braid", (0.07, 0.03, 0.3), (px + 0.66, py - 0.125, pz - 0.2), pl("#8a5a34"))
    # the sill peaches: a row
    W["sill"] = []
    for i in range(12):
        W["sill"].append(peach(kit, f"sillp{i}", (rx + 0.6 - 1.05 + i * 0.19, ry + 3.2, 1.07 + (0.0 if i < 8 else 0.0)), 0.09))

    # ================================================================== our city kitchen
    kx, ky = G.KIT
    kw = P("#e8f0f6", 0.85, spec=0.05)
    kit.plane("kfloor", (9, 8), (kx, ky, 0.03), P("#d8c8b0", 0.7, spec=0.1))
    kit.box("kback", (9, 0.3, 3.4), (kx, ky + 3.6, 1.7), kw)
    for sx in (-1, 1):
        kit.box(f"kside{sx}", (0.3, 8, 3.4), (kx + sx * 4.5, ky, 1.7), kw)
    kit.box("kwinglass", (2.4, 0.06, 1.7), (kx + 0.8, ky + 3.42, 2.0), kit.emit("#a8dcff", 1.1))
    for dx in (-1.25, 1.25):
        kit.box(f"kwf{dx}", (0.12, 0.1, 1.9), (kx + 0.8 + dx, ky + 3.4, 2.0), P("#ffffff", 0.7))
    for j, (x, y, w, h, c) in enumerate([(-6, 14, 5, 6, "#7f9ab8"), (-1, 18, 6, 9, "#9ab0c8"), (5, 15, 5, 7, "#8aa2b8"), (10, 20, 6, 11, "#a8bcd0")]):
        kit.box(f"kcity{j}", (w, 4.0, h), (kx + x, ky + y, h / 2), P(c, 0.9))
    kit.box("kcounter", (3.2, 0.9, 0.95), (kx - 2.6, ky + 3.0, 0.475), P("#ffd34d", 0.5, spec=0.2))
    kit.box("kctop", (3.3, 1.0, 0.08), (kx - 2.6, ky + 3.0, 0.97), P("#f6f2ea", 0.5, spec=0.3))
    kit.box("ksink", (0.9, 0.6, 0.06), (kx - 2.6, ky + 3.0, 1.02), kit.metal("#9aa0a8", 0.3))
    kit.cyl("kfaucet", 0.04, 0.4, (kx - 2.6, ky + 3.3, 1.2), kit.metal("#c0c4cc", 0.3), n=8)
    kit.box("kfaucet2", (0.04, 0.25, 0.04), (kx - 2.6, ky + 3.18, 1.4), kit.metal("#c0c4cc", 0.3))
    kit.box("ktable", (2.0, 1.2, 0.1), (kx + 2.4, ky + 1.6, 0.9), wood)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"ktl{sx}{sy}", (0.1, 0.1, 0.85), (kx + 2.4 + sx * 0.9, ky + 1.6 + sy * 0.5, 0.43), woodd)
    kit.box("kcloth", (1.7, 0.9, 0.03), (kx + 2.4, ky + 1.6, 0.97), kit.checker("#ee5a4a", "#fffaf0", 5.0) if hasattr(kit, "checker") else P("#ee5a4a", 0.7))

    # ================================================================== our street
    cx, cy = G.CITY
    kit.plane("cstreet", (90, 8), (cx, cy - 2.5, 0.03), asphalt)
    kit.plane("cwalk", (90, 4), (cx, cy + 3.5, 0.05), P("#cfcfd4", 0.9, spec=0.03))
    bcols = ["#c8826a", "#9ab0c8", "#d9b88a", "#a8b8a0", "#b89ac0"]
    for i in range(7):
        x = cx - 33 + i * 11
        h = 12.0 + (i % 3) * 3
        kit.box(f"cb{i}", (10.0, 8.0, h), (x, cy + 12.0, h / 2), P(bcols[i % 5], 0.85, spec=0.05))
        for r in range(int(h // 3)):
            for c in range(3):
                kit.box(f"cb{i}w{r}{c}", (1.3, 0.1, 1.5), (x - 3.0 + c * 3.0, cy + 7.97, 2.4 + r * 3.0), kit.emit("#bfe0f8", 0.9))
    kit.box("cdoor", (1.8, 0.14, 2.6), (cx, cy + 7.95, 1.3), P("#4a6a8a", 0.5, spec=0.3))
    kit.box("cstep", (3.0, 1.0, 0.2), (cx, cy + 7.2, 0.1), P("#cfcfd4", 0.8))
    kit.box("cdoorframe", (2.4, 0.1, 3.0), (cx, cy + 7.93, 1.5), P("#fff8e8", 0.7))
    for sx in (-1, 1):
        tree(kit, f"ctree{sx}", cx + sx * 8, cy + 4.0, 4.5)

    # ================================================================== a bus
    bx, by = G.BUS
    kit.plane("bfloor", (9, 4), (bx, by + 0.5, 0.05), P("#8a8f98", 0.7))
    kit.box("bback", (9, 0.3, 3.2), (bx, by + 2.5, 1.6), P("#e8e8f0", 0.8))
    for i in range(3):
        kit.box(f"bwin{i}", (2.2, 0.1, 1.2), (bx - 3.0 + i * 3.0, by + 2.32, 1.9), kit.emit("#a8dcff", 1.2))
    kit.box("bbench", (3.2, 0.9, 0.12), (bx, by + 1.5, 0.58), P("#d9573a", 0.6, spec=0.2), bevel=0.04)
    kit.box("bbenchb", (3.2, 0.12, 0.8), (bx, by + 1.98, 0.98), P("#d9573a", 0.6, spec=0.2), bevel=0.04)
    kit.box("bbenchl", (3.0, 0.8, 0.5), (bx, by + 1.5, 0.3), P("#5a5f68", 0.7))
    kit.cyl("bpole", 0.05, 3.0, (bx + 2.3, by + 0.6, 1.5), kit.metal("#c0c4cc", 0.3), n=8)
    kit.box("bside", (0.3, 4, 3.2), (bx - 4.5, by + 0.5, 1.6), P("#e8e8f0", 0.8))
    kit.box("bside2", (0.3, 4, 3.2), (bx + 4.5, by + 0.5, 1.6), P("#e8e8f0", 0.8))

    # ================================================================== the ridge road
    qx, qy = G.ROAD
    kit.plane("rshoulder", (30, 300), (qx, qy + 20, 0.0), grass2)
    W["road"] = []
    for i in range(36):
        y = -70.0 + i * 6.0
        seg = kit.empty(f"rseg{i}", (qx, y, 0.0))
        kit.box(f"rseg{i}.a", (6.6, 6.0, 0.08), (0, 0, 0.04), asphalt, seg)
        kit.box(f"rseg{i}.d", (0.16, 2.6, 0.02), (0, 0, 0.1), P("#ffd34d", 0.6), seg)
        kit.box(f"rseg{i}.e1", (0.12, 6.0, 0.02), (-3.1, 0, 0.1), P("#f8f5ee", 0.6), seg)
        kit.box(f"rseg{i}.e2", (0.12, 6.0, 0.02), (3.1, 0, 0.1), P("#f8f5ee", 0.6), seg)
        W["road"].append((y, seg))
    # tall grass where the road was
    W["rgrass"] = []
    for k in range(110):
        x = qx + ((k * 37) % 13 - 6.0) * 0.5
        y = 10.0 + (k * 13) % 44
        try:
            W["rgrass"].append(kit.prop("grass", (x, y, 0), height=0.9 + 0.3 * (k % 3), tint="#bfe58a"))
        except Exception:
            W["rgrass"].append(kit.box(f"tg{k}", (0.1, 0.1, 0.8), (x, y, 0.4), P("#7fc860", 0.8)))
    # the fence post at the turn and the dirt track
    kit.box("fpost", (0.3, 0.3, 1.5), (qx - 4.4, G.POST_Y, 0.75), woodd, bevel=0.03)
    kit.box("fpostcap", (0.4, 0.4, 0.1), (qx - 4.4, G.POST_Y, 1.55), woodd)
    kit.box("fpostrail", (0.1, 4.0, 0.12), (qx - 4.4, G.POST_Y + 2.2, 1.1), woodd)
    kit.box("track", (28, 4.0, 0.05), (qx - 18, G.POST_Y, 0.03), dirt)
    for j in range(6):
        tree(kit, f"rt{j}", qx - 12 - j * 5.0, G.POST_Y + 8 + (j % 2) * 3, 5.0, "#d4f0b8", fruit=3, rng=j)
    for j in range(8):
        tree(kit, f"ra{j}", qx - 9 - (j % 2) * 5, -40 + j * 16, 5.0, "#d4f0b8", fruit=2, rng=j)
        tree(kit, f"rb{j}", qx + 9 + (j % 2) * 5, -36 + j * 16, 5.0, "#c8e8a8", fruit=2, rng=j)
    for j, (x, y, r, c) in enumerate([(-60, 10, 40, "#7cc464"), (60, 30, 50, "#6fb85a"), (-30, 70, 45, "#86c870"),
                                      (30, 100, 50, "#9ad07e"), (-10, 135, 55, "#a8d88c"), (0, -90, 70, "#7cc464"),
                                      (-70, 70, 55, "#86c870")]):
        hill(kit, f"rh{j}", qx + x, y, r, 1.0, c)

    # ================================================================== props that move
    W["cars"] = {}
    me_car = car(kit, "mecar", "#e8493a", (qx, 0, 0.0), openc=True)
    mirror(kit, me_car)
    mapc = kit.empty("map", (-0.05, -0.2, 1.13), me_car)
    kit.box("map.sheet", (0.5, 0.7, 0.02), (0, 0, 0), P("#f6ecd0", 0.8), mapc)
    kit.box("map.road", (0.05, 0.4, 0.02), (0, 0.0, 0.012), P("#e8493a", 0.6), mapc)
    kit.box("map.city", (0.18, 0.12, 0.02), (0, -0.25, 0.014), P("#6a707a", 0.8), mapc)
    pg_ = kit.sphere("map.peach", 0.085, (0, 0.24, 0.05), P("#ff8a4a", 0.4), mapc, seg=10)
    kit.box("map.leaf", (0.07, 0.04, 0.02), (0.05, 0.3, 0.1), P("#3f9e3a", 0.6), mapc)
    car(kit, "momcar", "#2fa8a0", (qx, 90, 0.0), openc=False)
    car(kit, "brocar", "#ffb03a", (gx - 20, gy - 4, 0.0), openc=False)
    car(kit, "city1", "#4a8ad8", (cx + 40, cy - 4.0, 0.0), openc=False)
    car(kit, "city2", "#d9573a", (cx - 40, cy - 1.5, 0.0), openc=False)
    for k in range(1, 9):
        peach(kit, f"pc{k}", (0, 0, -60), 0.14)
    ph = kit.empty("phone", (0, 0, -60))
    kit.box("phone.b", (0.09, 0.03, 0.2), (0, 0, 0), kit.plastic("#222428", 0.4, spec=0.5), ph)
    reg("phone", ph)
    for k, c in enumerate(["#ee5a4a", "#4a8ad8"]):
        g = kit.empty(f"gift{k}", (0, 0, -60))
        kit.box(f"gift{k}.b", (0.42, 0.42, 0.34), (0, 0, 0), P(c, 0.5, spec=0.3), g, bevel=0.03)
        kit.box(f"gift{k}.r1", (0.44, 0.08, 0.36), (0, 0, 0), P("#ffd23f", 0.5), g)
        kit.box(f"gift{k}.r2", (0.08, 0.44, 0.36), (0, 0, 0), P("#ffd23f", 0.5), g)
        reg(f"gift{k}", g)
    bowl = kit.empty("bowl", (0, 0, -60))
    kit.cyl("bowl.b", 0.3, 0.16, (0, 0, 0), P("#fff8e8", 0.5, spec=0.3), bowl, n=16, r2=0.2)
    reg("bowl", bowl)
    mc2 = car(kit, "momopen", "#2fa8a0", (qx - 1.7, 31.0, 0.0), openc=True)
    for k in range(3):
        kit.box(f"wrap{k}", (0.22, 0.18, 0.04), (-0.45 + 0.05 * k, 0.4 + 0.15 * k, 0.72 + 0.02 * k), P(["#f8f5ee", "#ffd23f", "#f8f5ee"][k], 0.8), me_car, rot=(0, 0, 0.5 * k))

    build_tag(kit)
    return {}


def build_tag(kit):
    """The rule meter: a cream plate, a round peach glyph (grey then gold) and 3 tight seven-segment digits."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    plate = kit.emit("#fff1cf", 1.0, "tagplate")
    edge = kit.emit("#2a1a0e", 0.5, "tagedge")
    ink = kit.emit("#2a1a0e", 0.5, "tagink")
    grey = kit.emit("#8e8e94", 0.8, "taggrey")
    gold = kit.emit("#ffb21e", 1.4, "taggold")
    leaf = kit.emit("#4fae4a", 0.8, "tagleaf")

    def b(name, size, loc, mat):
        ob = kit.box(name, size, loc, mat, root)
        noshadow(ob)
        return ob
    b("tag.edge", (1.0, 0.5, 0.004), (0, 0, 0.0), edge)
    b("tag.plate", (0.95, 0.45, 0.004), (0, 0, 0.004), plate)
    for nm, mat, zz in (("pgrey", grey, 0.008), ("pgold", gold, 0.01)):
        sp = kit.sphere(f"tag.{nm}", 0.13, (-0.33, -0.02, zz), mat, root, seg=12)
        sp.scale = (1.0, 1.0, 0.02)
        noshadow(sp)
        W["pg" if nm == "pgrey" else "pgold"] = sp
    b("tag.pleaf", (0.12, 0.06, 0.004), (-0.27, 0.15, 0.014), leaf)
    W["seg"] = []
    layout = [("a", 0.0, 0.17, 0.15, 0.05), ("b", 0.075, 0.085, 0.05, 0.17), ("c", 0.075, -0.085, 0.05, 0.17),
              ("d", 0.0, -0.17, 0.15, 0.05), ("e", -0.075, -0.085, 0.05, 0.17), ("f", -0.075, 0.085, 0.05, 0.17),
              ("g", 0.0, 0.0, 0.15, 0.05)]
    for d in range(3):
        row = []
        for nm, x, z, w_, h_ in layout:
            ob = b(f"tag.d{d}{nm}", (w_, h_, 0.004), (x, z, 0.012), ink)
            ob["bx"] = x
            row.append(ob)
        W["seg"].append(row)


DIG = {0: "abcdef", 1: "bc", 2: "abdeg", 3: "abcdg", 4: "bcfg", 5: "acdfg", 6: "acdefg", 7: "abc", 8: "abcdefg", 9: "abcdfg"}
SEGN = "abcdefg"


def _first_frame(kit, story):
    h = bpy.data.objects.get("carrier.headg")
    W["acc"] = True
    for nm, mc in (("carrier", "#f4f4f4"), ("carrier0", "#3a2418")):
        hg = bpy.data.objects.get(f"{nm}.headg")
        if hg is not None:
            m = kit.plastic(mc, 0.8)
            kit.box(f"{nm}.stache", (0.7, 0.08, 0.14), (0, -0.62 - 0.02, -0.2), m, hg, bevel=0.03)
            kit.box(f"{nm}.stacheL", (0.12, 0.08, 0.26), (-0.36, -0.62 - 0.02, -0.28), m, hg, bevel=0.03)
            kit.box(f"{nm}.stacheR", (0.12, 0.08, 0.26), (0.36, -0.62 - 0.02, -0.28), m, hg, bevel=0.03)
        up = bpy.data.objects.get(f"{nm}.upper") or bpy.data.objects.get(f"{nm}.torso")
        if up is not None:
            sat = kit.plastic("#7a5230", 0.7)
            kit.box(f"{nm}.satchel", (1.7, 0.5, 1.1), (1.0, -0.62, 0.75), sat, up, bevel=0.06, rot=(0, 0, 0.0))
            kit.box(f"{nm}.strap", (0.22, 1.06, 2.2), (-0.1, 0.0, 1.0), sat, up, rot=(0, 0.0, 0.0))
    # Aunt Clem's braid
    ch = bpy.data.objects.get("clem.headg")
    if ch is not None:
        gm = kit.plastic("#b8b8c0", 0.7)
        kit.box("clem.braid", (0.3, 0.3, 1.5), (0, 0.78, -0.55), gm, ch, bevel=0.1)
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
        prev = dict(cur)
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
    # the sill row
    sl = sample("sill", tl, t, {"n": 0.0})
    for i, ob in enumerate(W["sill"]):
        _hide(ob, i + 0.5 > sl["n"])
    # the swing
    rk = sample("rock", tl, t, {"a": 0.0})
    sw = W["obj"]["swing"]
    sw.rotation_euler = (rk["a"] * D2R * math.sin(2 * math.pi * t / 2.8), 0, 0)
    # the road behind the car
    gn = sample("gone", tl, t, {"v": 0.0})
    ycut = 150.0 - gn["v"] * (150.0 - 7.0)
    for y, seg in W["road"]:
        _hide(seg, y > ycut)
    for ob in W["rgrass"]:
        _hide(ob, gn["v"] < 0.6)
    for ob in W["mroad"]:
        ob.hide_render = gn["v"] > 0.85
    ln = sample("lane", tl, t, {"v": 0.0})
    for ob in W["lane"]:
        ob.hide_render = ln["v"] > 0.5
    for ob in W["lgrass"]:
        _hide(ob, ln["v"] <= 0.5)
    # the map in the car
    mp = sample("map", tl, t, {"v": 0.0})
    _hide(bpy.data.objects["map"], mp["v"] < 0.5)
    # the odometer digits and the peach glyph
    od = sample("odo", tl, t, {"n": 412.0})
    n = max(0, min(999, int(round(od["n"]))))
    digs = [n // 100, (n // 10) % 10, n % 10]
    cells = []
    for di, dg in enumerate(digs):
        lead = (di == 0 and n < 100) or (di == 1 and n < 10)
        cells.append(0.0 if lead else (0.09 if dg == 1 else 0.2))
    tot = sum(cells) + 0.04 * (sum(1 for c_ in cells if c_) - 1)
    cur = 0.15 - tot / 2
    for di, dg in enumerate(digs):
        lead = cells[di] == 0.0
        on = "" if lead else DIG[dg]
        cc = cur + cells[di] / 2
        for si, nm in enumerate(SEGN):
            ob = W["seg"][di][si]
            ob.hide_render = nm not in on
            ob.location.x = cc + ob["bx"] - (0.075 if dg == 1 else 0.0)
        if not lead:
            cur += cells[di] + 0.04
    gd = sample("gold", tl, t, {"v": 0.0})
    W["pgold"].hide_render = gd["v"] < 0.5
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
    h2 = 12.0 / lens
    w2 = h2 * 9.0 / 16.0
    tag = W["tag"]
    s = 0.8 * w2
    tag.scale = (s, s, s)
    tag.location = (-0.5 * w2 + 0.4 * w2 + 0.06 * w2, 0.76 * h2, -1.0)
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
    # riders on the porch swing turn with it about the beam
    th = rk["a"] * D2R * math.sin(2 * math.pi * t / 2.8)
    rides = {}
    for c in tl["cues"]:
        if c["name"] == "ride" and c["t"] <= t:
            rides[c["who"]] = c
    py_, pz_ = 3.2, 3.3
    for who, c in rides.items():
        root = bpy.data.objects.get(who)
        if c.get("on") and root is not None:
            dy, dz = root.location.y - py_, root.location.z - pz_
            root.location.y = py_ + dy * math.cos(th) - dz * math.sin(th)
            root.location.z = pz_ + dy * math.sin(th) + dz * math.cos(th)
            root.rotation_euler.x += th
    return gains
