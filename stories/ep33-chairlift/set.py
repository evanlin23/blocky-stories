"""Chairlift: a two-seat lift on a still lake in spring, from the timber station at the water's edge up a pine slope to
a bare ridge with a long bench facing the sunrise. Built from kit.py's parts (ep33 redo; nothing here is shared with
another story's set).

Coordinates (geometry.py is the one source of truth, shared with make_story.py): the line runs up +y from the bottom
bull wheel at the origin to the top wheel at y = 128. The up rope is at x = +1.8, the down rope at x = -1.8. The deck
top is z = 0, the lake at z = -0.45, the ridge top z = 39.5. The sun is beyond the ridge (+y). A chair's origin is the
middle of its seat top, its front is -y at yaw 0, and the rope is 1.9 m over it. No text, number or sign anywhere.

Acting keys read here (acting.py ignores them): "sit": true seats a rider on the chair under them (the chair is the
one whose centre is `seat` (+1 / -1 along the rider's x) away), legs forward and down, hands on the lap. "perch":
true seats a character on the ridge bench (legs straight forward).

Cues read here:
- light: {"look": name, "ramp": s, plus any LOOKS key} the sky, fog, sun and fill ease to this look over `ramp`
- sunsweep: {"az0", "az1", "dur"} the sun swings round in azimuth (the shadows sweep), level never changes
- clouds: {"on": bool, "speed": m/s} the racing cloud cards (a smooth time-lapse sky)
- mist: {"on": bool, "speed": m/s} the low fog cards drifting off the lake (L23)
- sway: {"amp": degrees, "bias": degrees roll, "dur": s} how far the riders' chairs rock, easing over dur
- blanket: {"on": bool, "who": name | null, "local": [x, y, z] from that character's feet-root, "pos": [x, y, z]
  (when no `who`), "size": [x, y, z], "yaw": degrees} Gran's blanket
- gull: {"mode": "off" | "hat" | "fly", "dur": s, "to": [dx, dy, dz]} the gull on Gran's hat, or lifting off
- summer: {} the land turns a richer green on the cut
- arm_to, phase, upchairs: as in the earlier build (a hand held out, a chair put in the shot, chairs on the up line)
- open: {"from": f, "dur": s} sky, sun and fill start at f of their level and ease up over dur (a soft opening)
A shot's "scope": true puts the viewer's round soft-edged mask over it.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector as V

sys.path.insert(0, str(Path(__file__).resolve().parent / "generator"))
import geometry as G  # noqa: E402

from blocky import faces, rig  # noqa: E402,F401

WATER = -0.45
BASE_FOG = 0.010

# looks: the sky (world colour and strength), fog colour and density, the sun's lamp and disc, the follow-camera fill.
# Spring dawn, clear: "base" is the clear gold dawn the film opens on.
LOOKS = {
    "base": dict(sky="#9ec1d6", sky_s=1.3, fog="#d9c2a8", fogd=0.004, sun_e=3.0, sun_c="#ffd391", sun_el=22.0, disc=2.6,
                 cam=0.9, cam_c="#ffe2b8"),
    "pink": dict(sky="#c99fb4", sky_s=1.3, fog="#d9a9b8", fogd=0.005, sun_e=2.4, sun_c="#ffb898", sun_el=17.0, disc=2.4,
                 cam=1.0, cam_c="#ffd2cc"),
    "gold": dict(sky="#a9c4d2", sky_s=1.3, fog="#e0b98e", fogd=0.004, sun_e=3.2, sun_c="#ffd391", sun_el=24.0, disc=3.0,
                 cam=0.9, cam_c="#ffe2b8"),
    # flat cool daylight, the viewer's close on Gran asleep: her face clearly lit, never dark
    "flat": dict(sky="#b9c8d4", sky_s=1.6, fog="#c9cdd2", fogd=0.004, sun_e=1.4, sun_c="#e8eef6", sun_el=40.0, disc=0.0,
                 cam=1.8, cam_c="#e6eef8"),
    "fog": dict(sky="#b4bcc4", sky_s=1.2, fog="#c9cdd2", fogd=0.020, sun_e=1.2, sun_c="#ffe6cc", sun_el=22.0, disc=0.8,
                cam=1.1, cam_c="#e6eaf2"),
}
LOOKS["pre"] = LOOKS["base"]

STROKE_ORANGE = "#d98a4c"
Z0 = 39.5   # the ridge top
BENCH_Y, BENCH_Z = 137.0, 0.46
HANG = G.HANG
SPACING = 22.0


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl["cues"] if c["name"] == name]


def _switch(cs, attr, t, default):
    v = default
    for c in cs:
        if attr in c and c["t"] <= t + 1e-9:
            v = c[attr]
    return v


def _open(tl, t):
    """The `open` cue's brightness factor at t: `from` at the cue, easing to 1 over `dur` s."""
    f = 1.0
    for c in _cues(tl, "open"):
        if c["t"] <= t:
            f = c.get("from", 0.6) + (1.0 - c.get("from", 0.6)) * _ss((t - c["t"]) / max(0.01, c.get("dur", 0.5)))
    return f


def _hexl(kit, h):
    return kit.col(h)[:3]


# ------------------------------------------------------------------------------------------------ materials


def materials(kit):
    M = {}
    M["water"] = kit.plastic("#13232a", 0.05, name="lake", spec=0.9)
    M["pine_ground"] = kit.grime("#37663c", 0.5, 0.12, name="pine ground", rough=0.95)
    M["rock"] = kit.grime("#8c8a82", 0.5, 0.25, name="ridge rock", rough=0.95)
    M["pine"] = kit.plastic("#22382c", 0.9, name="pine", spec=0.1)
    M["deck"] = kit.planks("#6b5a48", "#40342a", 1.3, "X", name="deck planks")
    M["timber"] = kit.planks("#5a4636", "#3a2d22", 1.0, "Z", name="timber wall")
    M["post"] = kit.plastic("#4b3a2d", 0.85, name="post")
    M["roof"] = kit.plastic("#364239", 0.6, name="roof")
    M["steel"] = kit.plastic("#8a9097", 0.5, name="tower steel")
    M["dark"] = kit.plastic("#2a2e33", 0.55, name="dark steel")
    M["rope"] = kit.plastic("#26292d", 0.7, name="haul rope")
    M["rubber"] = kit.plastic("#1b1b1d", 0.8, name="footrest rubber", spec=0.15)
    M["slat"] = kit.plastic("#7d7468", 0.7, name="seat slat")
    M["frame"] = kit.plastic("#7d858c", 0.5, name="chair frame")
    M["tally"] = kit.plastic(STROKE_ORANGE, 0.75, name="tally orange", spec=0.1)
    M["concrete"] = kit.concrete("#7d7c78", 1.0, 0.4, name="pier concrete")
    M["lamp"] = kit.emit("#ffcf8a", 6.0, name="hut lamp")
    M["gaterope"] = kit.plastic("#a08c66", 0.9, name="gate rope")
    M["cup"] = kit.plastic("#e9e4da", 0.6, name="paper cup")
    M["steam"] = kit.emit("#dcdfe4", 0.5, name="steam")
    M["blanket"] = kit.checker("#3f6b4a", "#7aa36b", 7.0, name="blanket check", rough=0.95)
    M["blanket_edge"] = kit.plastic("#3f6b4a", 0.95, name="blanket edge")
    M["gull"] = kit.plastic("#f1f1ee", 0.7, name="gull white")
    M["gull_wing"] = kit.plastic("#9aa0a6", 0.7, name="gull grey")
    M["beak"] = kit.plastic("#e8a23a", 0.6, name="beak")
    M["suitcase"] = kit.plastic("#7a4a2c", 0.6, name="suitcase leather")
    M["brass"] = kit.metal("#b89a55", 0.35, name="brass")
    M["plate"] = kit.plastic("#eee9dd", 0.35, name="plate")
    M["table"] = kit.planks("#8a6a48", "#5e4630", 1.2, "X", name="table planks")
    M["house_a"] = kit.plastic("#c9b99a", 0.8, name="house cream")
    M["house_b"] = kit.plastic("#a96f55", 0.8, name="house clay")
    M["house_c"] = kit.plastic("#8aa1a8", 0.8, name="house sage")
    M["house_roof"] = kit.plastic("#4a4040", 0.7, name="house roof")
    M["my_door"] = kit.plastic("#c23b3b", 0.6, name="my door")
    M["viewer"] = kit.plastic("#3a4a44", 0.35, name="viewer green", spec=0.5)
    M["lens"] = kit.plastic("#1c2a30", 0.1, name="viewer glass", spec=0.9)
    M["bench"] = kit.plastic("#7a5f45", 0.8, name="bench")
    M["window"] = kit.emit("#ffc479", 3.0, name="hut window")
    return M


# ------------------------------------------------------------------------------------------------ the land


def build_land(kit, ctx, M):
    nx, ny = 41, 61
    xs = [-90 + 4.5 * i for i in range(nx)]
    ys = [-60 + 5.0 * j for j in range(ny)]
    verts, faces_, mats = [], [], []
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            h = G.ground(x, y)
            if h > 1.0:
                h += 0.7 * math.sin(x * 0.37 + y * 0.21) * math.sin(y * 0.13 - x * 0.19) + kit.hash01(i, j) * 0.5
            verts.append((x, y, h))
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            faces_.append((a, a + 1, a + nx + 1, a + nx))
            zc = sum(verts[k][2] for k in (a, a + 1, a + nx, a + nx + 1)) / 4
            mats.append(1 if zc > 31.0 else 0)
    ob = kit.mesh_obj("land", verts, faces_, M["pine_ground"], smooth=True)
    ob.data.materials.append(M["rock"])
    for p, m_ in zip(ob.data.polygons, mats):
        p.material_index = m_
    kit.plane("lake", (900, 900), (0, 150, WATER), M["water"])
    # pines: one mesh of stacked cones
    tv, tf = [], []
    n = 7
    for gx in range(-60, 61, 7):
        for gy in range(-58, 121, 7):
            x = gx + (kit.hash01(gx, gy, 1) - 0.5) * 5
            y = gy + (kit.hash01(gx, gy, 2) - 0.5) * 5
            if abs(x) < 4.3 and -14 < y < 130 or (y > 118) or (y < -13 and abs(x) < 14):
                continue
            g = G.ground(x, y)
            if g < 0.8:
                continue
            hgt = 5.5 + 4.5 * kit.hash01(gx, gy, 3)
            for k, (z0, r, hh) in enumerate([(0.0, 1.9, 0.62), (0.4, 1.45, 0.62), (0.75, 0.95, 0.5)]):
                base = len(tv)
                zb = g + hgt * z0
                for q in range(n):
                    a = 2 * math.pi * q / n
                    tv.append((x + r * math.cos(a) * hgt / 7.5, y + r * math.sin(a) * hgt / 7.5, zb))
                tv.append((x, y, zb + hh * hgt))
                for q in range(n):
                    tf.append((base + q, base + n, base + (q + 1) % n))
            # a trunk
    ob2 = kit.mesh_obj("pines", tv, tf, M["pine"], smooth=False)
    ctx["land"] = ob


# ------------------------------------------------------------------------------------------------ the stations


def beam(kit, name, p0, p1, w, mat, parent=None):
    """A square rod between two points."""
    a, b = V(p0), V(p1)
    d = b - a
    ob = kit.box(name, (w, w, d.length), tuple((a + b) / 2), mat, parent, bevel=0.0)
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return ob


def tube(kit, name, p0, p1, r, mat, parent=None, n=8):
    a, b = V(p0), V(p1)
    d = b - a
    ob = kit.cyl(name, r, d.length, tuple((a + b) / 2), mat, parent, n=n)
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return ob


def bull_wheel(kit, name, cx, cy, z, M):
    root = kit.empty(name, (cx, cy, z))
    kit.cyl(f"{name}.drum", 1.86, 0.3, (0, 0, 0), M["steel"], root, n=40)
    kit.cyl(f"{name}.rim", 1.9, 0.07, (0, 0, 0.17), M["dark"], root, n=40)
    kit.cyl(f"{name}.inner", 1.55, 0.34, (0, 0, 0), M["dark"], root, n=32)
    kit.cyl(f"{name}.hub", 0.35, 0.5, (0, 0, 0.02), M["steel"], root, n=16)
    for k in range(6):
        a = math.pi * k / 6
        b = kit.box(f"{name}.spoke{k}", (3.5, 0.12, 0.12), (0, 0, 0.19), M["steel"], root, bevel=0.0)
        b.rotation_euler = (0, 0, a)
    kit.cyl(f"{name}.shaft", 0.12, z - 0.0 + 0.5, (0, 0, -(z + 0.5) / 2 + 0.0), M["dark"], root, n=10)
    return root


def build_bottom(kit, ctx, M):
    # the deck on piles over the water
    kit.box("deck", (19.0, 16.5, 0.35), (-0.5, -4.75, -0.175), M["deck"])
    for ix in range(-4, 5):
        for iy in range(-2, 3):
            kit.cyl(f"pile{ix}_{iy}", 0.22, 3.0, (ix * 2.2 - 0.5, iy * 3.4 - 5.5, -1.7), M["post"], n=8)
    # the roof over the wheel, on four posts, pitched along y
    for sx in (-1, 1):
        for y in (-3.6, 2.4):
            kit.box(f"rpost{sx}{y}", (0.3, 0.3, 4.4), (sx * 4.6, y, 2.2), M["post"], bevel=0.02)
    for sx in (-1, 1):
        r = kit.box(f"roof{sx}", (3.3, 6.9, 0.14), (sx * 2.2, -0.6, 4.95), M["roof"], bevel=0.02)
        r.rotation_euler = (0, -sx * 0.30, 0)
        kit.box(f"rbeam{sx}", (0.22, 6.3, 0.24), (sx * 4.6, -0.6, 4.35), M["post"], bevel=0.02)
    kit.box("ridge", (0.3, 7.0, 0.2), (0, -0.6, 5.55), M["post"], bevel=0.02)
    # the wheel and its sheave frame
    ctx["wheel_b"] = bull_wheel(kit, "wheelB", 0, 0, 2.3, M)
    kit.box("wframe", (0.5, 0.5, 2.2), (0, 0, 1.0), M["dark"], bevel=0.02)
    # the hut, to the left (-x): timber walls, a door, one lit window
    kit.box("hut", (4.6, 6.2, 3.1), (-8.2, -1.5, 1.55), M["timber"], bevel=0.02)
    r = kit.box("hutroofL", (2.7, 6.8, 0.14), (-9.1, -1.5, 3.55), M["roof"], bevel=0.02)
    r.rotation_euler = (0, 0.28, 0)
    r = kit.box("hutroofR", (2.7, 6.8, 0.14), (-7.3, -1.5, 3.55), M["roof"], bevel=0.02)
    r.rotation_euler = (0, -0.28, 0)
    kit.box("hutdoor", (0.9, 0.08, 2.0), (-7.2, -4.62, 1.0), M["post"], bevel=0.01)
    kit.box("hutwin", (1.3, 0.06, 0.9), (-9.3, -4.62, 1.7), M["window"])
    kit.box("hutwinF", (1.5, 0.05, 1.1), (-9.3, -4.64, 1.7), M["post"])
    kit.light("hutlamp", "POINT", (-6.4, -5.0, 2.4), 90.0, "#ffc27a", size=0.3, shadow=False)
    # the gate: two posts and a sagging rope
    for x in (-3.4, -0.7):
        kit.box(f"gpost{x}", (0.16, 0.16, 1.15), (x, -3.2, 0.575), M["post"], bevel=0.02)
        kit.cyl(f"gcap{x}", 0.11, 0.08, (x, -3.2, 1.19), M["dark"], n=8)
    pts = [(-3.4 + 2.7 * k / 6, -3.2, 1.05 - 0.14 * math.sin(math.pi * k / 6)) for k in range(7)]
    for k in range(6):
        tube(kit, f"grope{k}", pts[k], pts[k + 1], 0.022, M["gaterope"])
    # a bench against the hut, and the rail along the lake edge
    kit.box("bench", (1.8, 0.45, 0.07), (-5.6, -4.3, 0.46), M["bench"], bevel=0.02)
    for x in (-6.3, -4.9):
        kit.box(f"benchleg{x}", (0.07, 0.4, 0.46), (x, -4.3, 0.23), M["post"])
    for x in [-9.5 + 1.6 * k for k in range(12)]:
        kit.box(f"rail_post{x}", (0.1, 0.1, 1.05), (x, 3.45, 0.52), M["post"], bevel=0.01)
    kit.box("rail_top", (19.0, 0.1, 0.08), (-0.5, 3.45, 1.07), M["post"], bevel=0.01)
    kit.box("rail_mid", (19.0, 0.06, 0.06), (-0.5, 3.45, 0.55), M["post"], bevel=0.01)
    # the lake-edge lamp posts for the dawn
    ctx["bottom_wheel_angle"] = 0.0


def build_top(kit, ctx, M):
    y0, zr = G.LL, G.rope_z(G.LL)
    g = 39.5
    kit.box("top_slab", (20.0, 24.0, 0.8), (0, y0 + 3.0, g - 0.4), M["rock"], bevel=0.05)
    for sx in (-1, 1):
        for y in (y0 - 3.6, y0 + 3.2):
            kit.box(f"tpost{sx}{y}", (0.3, 0.3, 5.0), (sx * 4.6, y, g + 2.5), M["post"], bevel=0.02)
    for sx in (-1, 1):
        r = kit.box(f"troof{sx}", (3.3, 7.8, 0.14), (sx * 2.2, y0 - 0.2, g + 5.5), M["roof"], bevel=0.02)
        r.rotation_euler = (0, -sx * 0.30, 0)
    kit.box("tridge", (0.3, 7.9, 0.2), (0, y0 - 0.2, g + 6.1), M["post"], bevel=0.02)
    ctx["wheel_t"] = bull_wheel(kit, "wheelT", 0, y0, zr - 0.15, M)
    kit.box("twframe", (0.5, 0.5, 2.4), (0, y0, zr - 1.4), M["dark"], bevel=0.02)
    kit.box("thut", (4.0, 4.5, 2.7), (8.0, y0 + 2.5, g + 1.35), M["timber"], bevel=0.02)
    kit.box("tdeckrail", (0.1, 8.0, 0.08), (4.2, y0 - 1.0, g + 1.05), M["post"])


def build_line(kit, ctx, M):
    ys = [y for y, _ in G.ROPE if -1 <= y <= G.LL + 3]
    for x in (G.XU, G.XD):
        for k in range(len(ys) - 1):
            tube(kit, f"rope{x}{k}", (x, ys[k], G.rope_z(ys[k])), (x, ys[k + 1], G.rope_z(ys[k + 1])), 0.03, M["rope"])
    for k, y in enumerate(G.TOWERS):
        zt = G.rope_z(y) + 0.9
        gz = max(G.ground(0, y), -1.2)
        if G.ground(0, y) < 0:
            kit.cyl(f"pier{k}", 0.9, 2.2, (0, y, WATER - 0.2), M["concrete"], n=10)
            gz = WATER + 0.9
        kit.box(f"tcol{k}", (0.5, 0.5, zt - gz), (0, y, (zt + gz) / 2), M["steel"], bevel=0.02)
        kit.box(f"tarm{k}", (5.4, 0.45, 0.35), (0, y, zt - 0.2), M["steel"], bevel=0.03)
        for sx in (-1, 1):
            kit.box(f"tshe{k}{sx}", (0.5, 1.1, 0.4), (sx * 1.8, y, G.rope_z(y) - 0.2), M["dark"], bevel=0.04)
            beam(kit, f"tbrace{k}{sx}", (0, y, zt - 2.4), (sx * 2.5, y, zt - 0.3), 0.14, M["steel"])


# ------------------------------------------------------------------------------------------------ chairs


def build_chair(kit, M, name, tally=False):
    root = kit.empty(name, (0, 0, -50))
    W = 2.9
    for i in range(5):
        kit.box(f"{name}.slat{i}", (W, 0.085, 0.05), (0, -0.24 + 0.12 * i, -0.025), M["slat"], root, bevel=0.01)
    for sx in (-1, 1):
        kit.box(f"{name}.rail{sx}", (0.06, 0.66, 0.07), (sx * 1.45, 0.02, -0.07), M["frame"], root, bevel=0.01)
        kit.box(f"{name}.bpost{sx}", (0.05, 0.05, 0.66), (sx * 1.45, 0.32, 0.28), M["frame"], root, bevel=0.01)
        kit.box(f"{name}.arm{sx}", (0.05, 1.0, 0.05), (sx * 1.45, -0.13, 0.64), M["frame"], root, bevel=0.01)
        kit.box(f"{name}.fstrut{sx}", (0.05, 0.05, 0.42), (sx * 1.45, -0.46, -0.13), M["frame"], root, bevel=0.01)
        kit.box(f"{name}.strutd{sx}", (0.05, 0.4, 0.05), (sx * 1.45, -0.3, -0.04), M["frame"], root, bevel=0.01)
    for z in (0.22, 0.48):
        kit.box(f"{name}.back{z}", (W, 0.04, 0.05), (0, 0.33, z), M["frame"], root, bevel=0.01)
    bar = kit.cyl(f"{name}.lapbar", 0.026, W, (0, -0.62, 0.64), M["frame"], root, n=8)
    bar.rotation_euler = (0, math.pi / 2, 0)
    kit.box(f"{name}.foot", (W, 0.36, 0.07), (0, -0.55, -0.34), M["rubber"], root, bevel=0.012)
    if tally:   # two short upright strokes pressed into the rubber, one per seat, in the Four-Face's colour
        for x in (-0.2, 0.2):
            kit.box(f"{name}.tally{x}", (0.06, 0.26, 0.012), (x, -0.55, -0.298), M["tally"], root)
    kit.cyl(f"{name}.hanger", 0.03, HANG - 0.05, (0, 0.34, 0.05 + (HANG - 0.05) / 2), M["frame"], root, n=8)
    kit.box(f"{name}.grip", (0.26, 0.42, 0.2), (0, 0.34, HANG), M["dark"], root, bevel=0.03)
    return root


def build_chairs(kit, ctx, M):
    n_cable = int(G.TOT // SPACING)
    ctx["spacing"] = G.TOT / n_cable
    ctx["cable"] = [build_chair(kit, M, f"cchair{k}") for k in range(n_cable)]
    ctx["special"] = [build_chair(kit, M, f"schair{k}", tally=(k == 0)) for k in range(3)]


# ------------------------------------------------------------------------------------------------ the sun and lights


def build_sky(kit, ctx, M):
    m = kit._new("sun disc")
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col("#ffd18c")
    e.inputs["Strength"].default_value = 0.0
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    ctx["disc_e"] = e
    ctx["disc"] = kit.sphere("sundisc", 18.0, (60, 450, 60), m, seg=24)
    kit.light("sun", "SUN", (0, 0, 50), 1.0, "#ffb48a", rot=(0.5, 0, 0))
    kit.light("camfill", "AREA", (0, 0, 5), 10.0, "#9cb4e4", size=1.5, shadow=False)
    kit.light("hutfill", "POINT", (-3.0, -6.0, 2.6), 40.0, "#ffc890", size=0.4, shadow=False)


# ------------------------------------------------------------------------------------------------ props and the town


def soft_card_mat(kit, name, color, strength, alpha, power=0.8):
    """A flat emissive card whose edges fade to nothing (a cloud or a drift of mist). Not fogged: it is the sky."""
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sub = nt.nodes.new("ShaderNodeVectorMath")
    sub.operation = "SUBTRACT"
    sub.inputs[1].default_value = (0.5, 0.5, 0.0)
    nt.links.new(tc.outputs["Generated"], sub.inputs[0])
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    nt.links.new(sub.outputs[0], ln.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.5
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 0.0
    nt.links.new(ln.outputs["Value"], mr.inputs["Value"])
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 1.0 / power
    nt.links.new(mr.outputs["Result"], pw.inputs[0])
    am = nt.nodes.new("ShaderNodeMath")
    am.operation = "MULTIPLY"
    am.inputs[1].default_value = alpha
    nt.links.new(pw.outputs[0], am.inputs[0])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col(color)
    em.inputs["Strength"].default_value = strength
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(am.outputs[0], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    return m


def scope_mat(kit):
    """The viewer's round soft-edged mask: black outside a circle, clear inside, fading over the rim."""
    m = kit._new("viewer scope")
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sub = nt.nodes.new("ShaderNodeVectorMath")
    sub.operation = "LENGTH"
    nt.links.new(tc.outputs["Object"], sub.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 4.3
    mr.inputs["From Max"].default_value = 5.5
    mr.inputs["To Min"].default_value = 0.0
    mr.inputs["To Max"].default_value = 1.0
    nt.links.new(sub.outputs["Value"], mr.inputs["Value"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.01, 0.012, 0.012, 1)
    em.inputs["Strength"].default_value = 1.0
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mr.outputs["Result"], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return m


def house(kit, name, x, y, w, d, h, wall, roof, door=None):
    z = G.ground(x, y)
    kit.box(f"{name}.w", (w, d, h), (x, y, z + h / 2), wall, bevel=0.03)
    for sx in (-1, 1):
        r = kit.box(f"{name}.r{sx}", (w * 0.62, d + 0.5, 0.18), (x + sx * w * 0.24, y, z + h + w * 0.1), roof, bevel=0.02)
        r.rotation_euler = (0, -sx * 0.42, 0)
    if door is not None:
        kit.box(f"{name}.d", (0.9, 0.06, 1.7), (x, y + d / 2 + 0.02, z + 0.85), door, bevel=0.0)


def build_town(kit, ctx, M):
    """The town on the flat ground behind the deck: a scatter of small houses, one with a red door (mine)."""
    spots = [(-20, -24, 6, 5, 3.6, "house_a"), (-12, -30, 5, 5, 3.4, "house_b"), (-4, -22, 6, 5, 3.8, "house_c"),
             (6, -26, 5, 5, 3.4, "house_a"), (14, -23, 6, 5, 3.6, "house_b"), (-26, -36, 6, 5, 3.6, "house_c"),
             (-8, -40, 6, 5, 3.8, "house_b"), (2, -36, 5, 5, 3.4, "house_a"), (12, -39, 6, 5, 3.6, "house_c"),
             (21, -33, 5, 5, 3.4, "house_b"), (-16, -46, 6, 5, 3.6, "house_a"), (8, -48, 6, 5, 3.6, "house_c"),
             (-16, 96, 5, 4, 3.2, "house_a"), (-13, 74, 5, 4, 3.2, "house_c"), (13, 90, 5, 4, 3.2, "house_b"),
             (15, 68, 5, 4, 3.2, "house_a"), (-17, 60, 5, 4, 3.2, "house_b"), (17, 55, 5, 4, 3.2, "house_c")]
    for k, (x, y, w, d, h, c) in enumerate(spots):
        house(kit, f"town{k}", x, y, w, d, h, M[c], M["house_roof"], M["my_door"] if k in (2, 13) else None)


def build_props(kit, ctx, M):
    # the viewer: a fixed sightseeing telescope on a steel post at the deck rail, no text, no coin slot
    vx, vy = -5.5, 3.05
    kit.box("viewer.post", (0.2, 0.2, 1.3), (vx, vy, 0.65), M["dark"], bevel=0.03)
    kit.box("viewer.base", (0.5, 0.5, 0.1), (vx, vy, 0.05), M["dark"], bevel=0.03)
    kit.box("viewer.yoke", (0.4, 0.2, 0.16), (vx, vy, 1.34), M["viewer"], bevel=0.03)
    tube(kit, "viewer.tube", (vx, vy - 0.55, 1.42), (vx, vy + 0.75, 1.78), 0.1, M["viewer"], n=14)
    tube(kit, "viewer.eye", (vx, vy - 0.62, 1.40), (vx, vy - 0.45, 1.45), 0.07, M["dark"], n=14)
    tube(kit, "viewer.front", (vx, vy + 0.68, 1.76), (vx, vy + 0.9, 1.82), 0.13, M["dark"], n=14)
    kit.cyl("viewer.glass", 0.09, 0.02, (vx, vy + 0.91, 1.825), M["lens"], rot=(math.radians(-72), 0, 0), n=14)
    # the picnic table with two plates
    tx, ty = -3.3, -8.0
    kit.box("table.top", (2.2, 0.95, 0.08), (tx, ty, 0.76), M["table"], bevel=0.015)
    for sx in (-1, 1):
        kit.box(f"table.leg{sx}", (0.1, 0.8, 0.72), (tx + sx * 0.9, ty, 0.36), M["post"])
        for sy in (-1, 1):
            kit.box(f"table.bench{sx}{sy}", (2.2, 0.32, 0.06), (tx, ty + sy * 0.78, 0.44), M["table"], bevel=0.01)
    for sy in (-1, 1):
        kit.box(f"table.bleg{sy}", (1.9, 0.08, 0.44), (tx, ty + sy * 0.78, 0.22), M["post"])
    for sx, sy in ((-0.55, -0.22), (0.55, 0.22)):
        kit.cyl(f"plate{sx}", 0.19, 0.03, (tx + sx, ty + sy, 0.815), M["plate"], n=20)
    # an old-fashioned suitcase by the gate rope: brown, brass corners and a handle, no mark on it
    sx_, sy_ = -3.7, -3.95
    kit.box("case.body", (0.75, 0.24, 0.5), (sx_, sy_, 0.25), M["suitcase"], bevel=0.03)
    for dx in (-1, 1):
        for dz in (0.03, 0.47):
            kit.box(f"case.c{dx}{dz}", (0.08, 0.26, 0.08), (sx_ + dx * 0.36, sy_, dz), M["brass"], bevel=0.01)
    kit.box("case.h", (0.2, 0.05, 0.05), (sx_, sy_, 0.55), M["brass"])
    for dx in (-1, 1):
        kit.box(f"case.hs{dx}", (0.03, 0.05, 0.07), (sx_ + dx * 0.1, sy_, 0.52), M["brass"])
    # the long bench on the ridge, facing the sunrise (+y). The backrest stops short of the left end, where two
    # people sit looking the other way
    zs = Z0 + BENCH_Z
    kit.box("bench.seat", (11.4, 0.52, 0.07), (0, BENCH_Y, zs - 0.035), M["bench"], bevel=0.015)
    for x in (-5.3, -2.6, 0.0, 2.6, 5.3):
        kit.box(f"bench.leg{x}", (0.1, 0.4, BENCH_Z - 0.07), (x, BENCH_Y, Z0 + (BENCH_Z - 0.07) / 2), M["post"])
    kit.box("bench.back", (7.5, 0.05, 0.4), (1.9 + 0.0, BENCH_Y - 0.25, zs + 0.3), M["bench"], bevel=0.01)
    for x in (-1.7, 5.4):
        kit.box(f"bench.bp{x}", (0.07, 0.07, 0.5), (x, BENCH_Y - 0.25, zs + 0.2), M["post"])
    # gull
    g = kit.empty("gull", (0, 0, -60))
    kit.box("gull.body", (0.22, 0.4, 0.17), (0, 0, 0), M["gull"], g, bevel=0.06)
    kit.box("gull.tail", (0.14, 0.14, 0.04), (0, 0.24, 0.02), M["gull_wing"], g, bevel=0.01)
    kit.box("gull.head", (0.13, 0.14, 0.13), (0, -0.23, 0.09), M["gull"], g, bevel=0.04)
    kit.box("gull.beak", (0.04, 0.1, 0.03), (0, -0.33, 0.085), M["beak"], g)
    for sx in (-1, 1):
        kit.box(f"gull.wing{sx}", (0.04, 0.34, 0.12), (sx * 0.12, 0.02, 0.03), M["gull_wing"], g, bevel=0.015)
    ctx["gull"] = g
    # Gran's blanket: one slab, sized and placed by the blanket cue
    ctx["blanket"] = kit.box("blanket", (1.0, 1.0, 1.0), (0, 0, -60), M["blanket"], bevel=0.0)
    # the viewer's mask, parented to the camera
    sc = kit.mesh_obj("scope", [(-4.5, -8, 0), (4.5, -8, 0), (4.5, 8, 0), (-4.5, 8, 0)], [(0, 1, 2, 3)], scope_mat(kit))
    sc.parent = kit.OBJ["cam"]
    sc.location = (0, 0, -0.4)
    sc.hide_render = True
    ctx["scope"] = sc
    # racing cloud cards on a ring round the valley, and drifting mist cards over the lake
    cm = soft_card_mat(kit, "cloud card", "#fff1e2", 0.85, 0.78)
    ctx["clouds"] = []
    n = 16
    for k in range(n):
        c = kit.plane(f"cloud{k}", (100.0 + 40 * kit.hash01(k, 1), 26.0 + 14 * kit.hash01(k, 2)), (0, 0, 90), cm)
        c.rotation_euler = (math.pi / 2, 0, 0)
        c.hide_render = True
        ctx["clouds"].append((c, 360.0 * k / n + 11 * kit.hash01(k, 3), 52 + 22 * kit.hash01(k, 4)))
    mm = soft_card_mat(kit, "mist card", "#d3d6da", 0.8, 0.3)
    ctx["mist"] = []
    for k in range(14):
        c = kit.plane(f"mist{k}", (34.0, 26.0), (0, 0, 0), mm)
        c.hide_render = True
        ctx["mist"].append((c, -50 + 100 * kit.hash01(k, 5), 4 + 78 * kit.hash01(k, 6), 0.4 + 5.0 * kit.hash01(k, 7)))


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    ctx = {}
    M = materials(kit)
    ctx["M"] = M
    build_land(kit, ctx, M)
    build_bottom(kit, ctx, M)
    build_top(kit, ctx, M)
    build_line(kit, ctx, M)
    build_chairs(kit, ctx, M)
    build_sky(kit, ctx, M)
    build_town(kit, ctx, M)
    build_props(kit, ctx, M)
    # the lift clock: how far the cable has moved by time t (it can stop and start)
    stops = sorted([(c["t"], c["state"]) for c in _cues(tl, "lift")])
    dt, C, c_, v_ = 0.05, [0.0], 0.0, 1.0
    t = 0.0
    while t < tl["duration"] + 1:
        want = 1.0
        for ts, st in stops:
            if ts <= t:
                want = 0.0 if st == "stop" else 1.0
        v_ += (want - v_) * min(1.0, dt / 0.7)
        c_ += 2.4 * v_ * dt
        C.append(c_)
        t += dt
    ctx["clock"] = (dt, C)
    return ctx


# ------------------------------------------------------------------------------------------------ per frame


def clock(ctx, t):
    dt, C = ctx["clock"]
    k = min(len(C) - 2, int(t / dt))
    u = t / dt - k
    return C[k] + (C[k + 1] - C[k]) * u


def look_state(tl, t):
    cs = _cues(tl, "light")
    prev = dict(LOOKS["base"])
    cur = dict(prev)
    for c in cs:
        if c["t"] > t:
            break
        tgt = {**LOOKS[c.get("look", "base")], **{k: v for k, v in c.items() if k in LOOKS["base"]}}
        u = _ss((t - c["t"]) / max(0.01, c.get("ramp", 3.0)))
        cur = {}
        for k, v in tgt.items():
            pv = prev[k]
            if isinstance(v, str) or isinstance(pv, tuple):
                a, b = _rgb(pv), _rgb(v)
                cur[k] = tuple(a[i] + (b[i] - a[i]) * u for i in range(3))
            else:
                cur[k] = pv + (v - pv) * u
        if u >= 1:
            prev = dict(cur)
    return cur


def _rgb(v):
    if isinstance(v, tuple):
        return v
    h = v.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _lin(c):
    return tuple(((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in _rgb(c))


def _fog_nodes(ctx):
    if "fog_nodes" not in ctx:
        from blocky import kit as _k

        d = _k.FOG["density"]
        ctx["fog_nodes"] = [nd for m in bpy.data.materials if m.node_tree for nd in m.node_tree.nodes
                            if nd.type == "MATH" and nd.operation == "MULTIPLY" and d > 0
                            and abs(nd.inputs[1].default_value + d) < 1e-6]
        fc = tuple(_k.FOG["color"])
        ctx["fog_cols"] = [nd for m in bpy.data.materials if m.node_tree for nd in m.node_tree.nodes
                           if nd.type == "EMISSION" and all(abs(a - b) < 1e-6 for a, b in
                                                             zip(nd.inputs["Color"].default_value[:3], fc))]
    return ctx["fog_nodes"]


def sway_now(tl, t):
    cs = _cues(tl, "sway")
    amp, bias = 1.4, 0.0
    pa, pb = amp, bias
    for c in cs:
        if c["t"] > t:
            break
        u = _ss((t - c["t"]) / max(0.01, c.get("dur", 1.0)))
        amp = pa + (c.get("amp", 1.4) - pa) * u
        bias = pb + (c.get("bias", 0.0) - pb) * u
        if u >= 1:
            pa, pb = amp, bias
    return amp, bias


def _rot_about(ob, pivot, rx, ry):
    """Rotate an object (placed in world space) about a world pivot: rx about world x, then ry about world y."""
    M_ = Matrix.Translation(pivot) @ Matrix.Rotation(ry, 4, "Y") @ Matrix.Rotation(rx, 4, "X") @ Matrix.Translation(-V(pivot))
    ob.matrix_world = M_ @ ob.matrix_basis   # these objects have no parent, and matrix_world isn't updated yet


def _local(st, loc):
    """A point in a character's own frame (x right, y forward as -y at yaw 0) from its feet-root, in world space."""
    c, sn = math.cos(st["yaw"]), math.sin(st["yaw"])
    return V((st["x"] + loc[0] * c - loc[1] * sn, st["y"] + loc[0] * sn + loc[1] * c, st["z"] + loc[2]))


def _sweep(tl, t):
    """The sun's azimuth: 8 degrees (just off the ridge line) unless a sunsweep cue is swinging it round."""
    az = 8.0
    for c in sorted(_cues(tl, "sunsweep"), key=lambda c_: c_["t"]):
        if c["t"] <= t:
            u = _ss((t - c["t"]) / max(0.01, c.get("dur", 3.0)))
            az = c["az0"] + (c["az1"] - c["az0"]) * u
    return az


def animate(kit, story, tl, t, ctx):
    import __main__
    from blocky import acting as _ac
    from blocky import kit as K

    over = {}
    _fog_nodes(ctx)
    # ---- the look
    L = look_state(tl, t)
    w = bpy.context.scene.world.node_tree.nodes["Background"]
    w.inputs["Color"].default_value = (*_lin(L["sky"]), 1)
    for nd in ctx["fog_nodes"]:
        nd.inputs[1].default_value = -L["fogd"]
    for nd in ctx["fog_cols"]:
        nd.inputs["Color"].default_value = (*_lin(L["fog"]), 1)
    el = math.radians(L["sun_el"])
    az = math.radians(_sweep(tl, t))
    s = V((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    sun = K.LIGHTS["sun"]
    sun["obj"].rotation_euler = (-s).to_track_quat("-Z", "Y").to_euler()
    sun["light"].color = _lin(L["sun_c"])
    opn = _open(tl, t)
    K.LIGHTS["sun"]["base"] = max(L["sun_e"] * opn, 0.0001)
    ctx["disc"].location = tuple(s * 450.0)
    ctx["disc_e"].inputs["Strength"].default_value = L["disc"]
    ctx["disc_e"].inputs["Color"].default_value = (*_lin(L["sun_c"]), 1)
    # ---- the camera of this frame (the follow-camera fill, the viewer's mask)
    shot = next((x for x in tl["shots"] if x["start"] <= t < x["end"]), tl["shots"][-1])
    spec = next(x for x in story["shots"] if x["id"] == shot["id"])
    loc, tgt, lens, _ = __main__.cam_at(spec, shot, t, None, tl)
    cam, tg = V(loc), V(tgt)
    fwd = (tg - cam)
    dist = max(0.8, fwd.length)
    cf = K.LIGHTS["camfill"]
    cf["obj"].location = cam + V((0.0, 0.0, 0.15))
    cf["obj"].rotation_euler = fwd.to_track_quat("-Z", "Y").to_euler()
    cf["light"].color = _lin(L["cam_c"])
    cf["light"].size = 1.5
    w.inputs["Strength"].default_value = L["sky_s"] * opn
    cf["base"] = 7.0 * min(dist, 12.0) ** 2 * L["cam"] * spec.get("cfill", 1.0) * opn
    sc = ctx["scope"]
    sc.hide_render = not spec.get("scope", False)
    sc.scale = (1.5 * 0.4 / lens,) * 3
    # ---- racing clouds and drifting mist (smooth, one direction, the light level never cycles)
    cl = [c for c in _cues(tl, "clouds") if c["t"] <= t]
    cl_on = bool(cl and cl[-1].get("on", True))
    for ob, a0, hz in ctx["clouds"]:
        ob.hide_render = not cl_on
        if cl_on:
            sp = cl[-1].get("speed", 40.0)
            a = math.radians(a0) + (sp / 140.0) * (t - cl[-1]["t"])
            ob.location = (140.0 * math.cos(a), 100.0 + 140.0 * math.sin(a), hz)
            ob.rotation_euler = (math.pi / 2, 0, a + math.pi / 2 + math.pi)
    ms = [c for c in _cues(tl, "mist") if c["t"] <= t]
    ms_on = bool(ms and ms[-1].get("on", True))
    for ob, x0, y0, z0 in ctx["mist"]:
        ob.hide_render = not ms_on
        if ms_on:
            tt = t - ms[-1]["t"]
            ob.location = (-60 + (x0 + 60 + ms[-1].get("speed", 6.0) * tt) % 120, y0, z0 + 0.35 * tt)
    # ---- the lift clock and the chairs
    P = clock(ctx, t)
    riders = []
    for who, keys in tl["acting"].items():
        if _ac._switch(keys, "sit", t, False) and not _ac._switch(keys, "hidden", t, False):
            s_ = _ac.state(tl, who, t)
            riders.append((who, s_, _ac._switch(keys, "seat", t, 1.0)))
    amp, bias = sway_now(tl, t)
    cents = []
    for who, s_, seat in riders:
        yaw = s_["yaw"]
        c_, sn = math.cos(yaw), math.sin(yaw)
        lx, ly = seat * G.SIDE, G.HIP_Y
        cx = s_["x"] - (lx * c_ - ly * sn)
        cy = s_["y"] - (lx * sn + ly * c_)
        cz = s_["z"] - G.ROOT_DZ
        for c in cents:
            if abs(c[0] - cx) < 0.05 and abs(c[1] - cy) < 0.05:
                c[4].append(who)
                break
        else:
            cents.append([cx, cy, cz, yaw, [who]])
    cents.sort(key=lambda c: 0 if "me" in c[4] else 1)   # my chair is the one with the footrest strokes
    me_riding = next((r for r in riders if r[0] == "me"), None)
    if me_riding is not None:
        ycur = me_riding[1]["y"]
        P = ycur if me_riding[1]["yaw"] > 1.5 else (G.LL + G.ARC + (G.LL - ycur))
    shift = 0.0
    for c in sorted(_cues(tl, "phase"), key=lambda c_: c_["t"]):
        if c["t"] <= t:
            shift = 0.0 if c.get("off") else (c["u"] - clock(ctx, c["t"] + c.get("when", 0.0))) % ctx["spacing"]
    ph = P + shift
    for ob in ctx["special"]:
        ob.location = (0, 0, -60)
    for k, c in enumerate(cents[:3]):
        ob = ctx["special"][k]
        ob.location = (c[0], c[1], c[2])
        ob.rotation_euler = (0, 0, c[3])
    up_on = _switch(_cues(tl, "upchairs"), "on", t, False)
    for k, ob in enumerate(ctx["cable"]):
        u = (ph + k * ctx["spacing"]) % G.TOT
        x, y, zr, yaw = G.path(u)
        if not up_on and (u < G.LL or u >= G.BOTTOM_ARC):   # only the returning chairs are empty on the lift
            ob.location = (x, y, -60)
            continue
        ob.location = (x, y, zr - HANG)
        ob.rotation_euler = (0, 0, yaw)
        for c in cents:
            if math.hypot(c[0] - x, c[1] - y) < 5.5:
                ob.location = (x, y, -60)
    # ---- seated riders: legs forward and down, hands on the lap (unless the acting raises an arm)
    for who, s_, seat in riders:
        r = bpy.data.objects.get(who)
        if r is None:
            continue
        r.location.z = s_["z"]
        r.rotation_euler.x = math.radians(_ac._held(tl["acting"][who], "lean", t, 0.0))
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            arm = bpy.data.objects.get(f"{who}.arm{sx}")
            if leg is not None:
                leg.rotation_euler = (-math.radians(55), 0, 0)
            if arm is not None and not any(abs(a) > 0.05 for a in s_["arms"]):
                arm.rotation_euler = (-math.radians(12), 0, 0)
    # ---- the bench: legs straight forward, hands in the lap
    for who, keys in tl["acting"].items():
        if _ac._switch(keys, "perch", t, False):
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                arm = bpy.data.objects.get(f"{who}.arm{sx}")
                if leg is not None:
                    leg.rotation_euler = (-math.radians(84), 0, 0)
                if arm is not None and not any(abs(a) > 0.05 for a in _ac.state(tl, who, t)["arms"]):
                    arm.rotation_euler = (-math.radians(34), 0, 0)
    # sway: a chair and its riders rock about the grip
    for k, c in enumerate(cents[:3]):
        ob = ctx["special"][k]
        pivot = V((c[0], c[1], c[2] + HANG))
        a = math.radians(amp) * math.sin(2 * math.pi * 0.33 * t + k)
        roll = math.radians(bias) * 1.0 + a * 0.6
        pitch = a * 0.5
        ob.rotation_euler = (0, 0, c[3])
        _rot_about(ob, pivot, pitch, roll)
        for who in c[4]:
            r = bpy.data.objects[who]
            _rot_about(r, pivot, pitch, roll)
    # ---- the wheels
    ctx["wheel_b"].rotation_euler = (0, 0, P / G.R)
    ctx["wheel_t"].rotation_euler = (0, 0, P / G.R)
    # ---- props on people: boots, Mr Pell's beard, Gran's knit hat
    if not ctx.get("props_ready"):
        ctx["props_ready"] = True
        for who, bc in (("mr_pell", "#7a3b2a"), ("gran", "#2c4a35")):
            boot = K.plastic(bc, 0.7, name=f"boot {who}")
            lace = K.plastic("#e4dcc6", 0.8, name="laces")
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is None:
                    continue
                K.box(f"{who}.boot{sx}", (1.05, 1.07, 0.92), (0, 0, -1.56), boot, leg, bevel=0.07)
                for k in range(4):
                    K.box(f"{who}.lace{sx}{k}", (0.62, 0.05, 0.07), (0, -0.56, -1.2 - 0.18 * k), lace, leg)
                K.box(f"{who}.lacev{sx}", (0.07, 0.05, 0.72), (0, -0.57, -1.52), lace, leg)
        hg = bpy.data.objects.get("mr_pell.headg")
        if hg is not None:
            K.box("mr_pell.beard", (0.98, 0.2, 0.42), (0, -0.55, -0.4), K.plastic("#f1f0ec", 0.9, name="beard"), hg, bevel=0.07)
        # two faded-orange strokes pressed in the footrest are built into the first special chair (the lore plant)
    # ---- an arm stretched to a point (close-ups of a hand only)
    cs = [c for c in _cues(tl, "arm_to") if c["t"] <= t]
    if cs and cs[-1].get("to"):
        c = cs[-1]
        ob = bpy.data.objects.get(f"{c['who']}.arm{c.get('arm', 1)}")
        root = bpy.data.objects.get(c["who"])
        if ob is not None and root is not None:
            bpy.context.view_layer.update()
            sh = ob.matrix_world.translation.copy()
            dv = V(c["to"]) - sh
            z = -dv.normalized()
            xx = V((1, 0, 0)) - z.x * z
            xx.normalize()
            sc_ = root.scale
            k = dv.length / (1.75 * sc_.z)
            M2 = Matrix((tuple(xx), tuple(z.cross(xx)), tuple(z))).transposed().to_4x4() @ Matrix.Diagonal((sc_.x, sc_.y, sc_.z * k, 1))
            M2.translation = sh
            ob.matrix_world = M2
    # ---- the blanket
    bl = [c for c in _cues(tl, "blanket") if c["t"] <= t]
    bo = ctx["blanket"]
    if bl and bl[-1].get("on", True):
        c = bl[-1]
        yaw = math.radians(c.get("yaw", 0.0))
        if c.get("who"):
            st = _ac.state(tl, c["who"], t)
            bo.location = tuple(_local(st, c["local"]))
            yaw += st["yaw"]
        else:
            bo.location = tuple(c["pos"])
        bo.scale = tuple(c["size"])
        bo.rotation_euler = (0, 0, yaw)
        bo.hide_render = False
    else:
        bo.hide_render = True
    # ---- the gull
    gc = [c for c in _cues(tl, "gull") if c["t"] <= t]
    gull = ctx["gull"]
    mode = gc[-1].get("mode", "off") if gc else "off"
    if mode == "off":
        gull.location = (0, 0, -60)
    else:
        hg = bpy.data.objects.get("gran.headg")
        bpy.context.view_layer.update()
        hat = hg.matrix_world.translation + V((0, 0, 0.25)) if hg is not None else V((0, 0, -60))
        if mode == "hat":
            gull.location = tuple(hat)
            gull.rotation_euler = (0, 0, math.radians(180))
        else:
            u = _ss((t - gc[-1]["t"]) / max(0.01, gc[-1].get("dur", 1.2)))
            d = V(gc[-1].get("to", [2.0, 3.0, 2.5]))
            gull.location = tuple(hat + d * u + V((0, 0, 0.35 * math.sin(math.pi * u))))
            gull.rotation_euler = (math.radians(-18 * u), 0, math.radians(180))
            for sx in (-1, 1):
                wob = bpy.data.objects.get(f"gull.wing{sx}")
                if wob is not None:
                    wob.rotation_euler = (0, sx * math.radians(50) * math.sin(t * 22.0), 0)
    # ---- summer (the last shot): a richer green
    if _cues(tl, "summer") and _cues(tl, "summer")[0]["t"] <= t:
        ctx["land"].data.materials[0].node_tree.nodes  # the same material, recoloured once
        if not ctx.get("summered"):
            ctx["summered"] = True
            for nd in ctx["land"].data.materials[0].node_tree.nodes:
                if nd.type == "VALTORGB":
                    for e in nd.color_ramp.elements:
                        e.color = (e.color[0] * 0.8, min(1.0, e.color[1] * 1.3), e.color[2] * 0.7, 1)
    return over
