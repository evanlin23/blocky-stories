"""Chairlift: a two-seat lift on a still lake, from the timber station at the water's edge up a pine slope to a bare
ridge, and the Four-Face. Built from kit.py's parts (ep33; nothing here is shared with another story's set).

Coordinates (geometry.py is the one source of truth, shared with make_story.py): the line runs up +y from the bottom
bull wheel at the origin to the top wheel at y = 128. The up rope is at x = +1.8, the down rope at x = -1.8. The deck
top is z = 0, the lake at z = -0.45. A chair's origin is the middle of its seat top, its front is -y at yaw 0, and the
rope is 1.9 m over it. No text, number or sign anywhere.

THE FOUR-FACE: an ordinary R6 body in a faded orange cagoule (rig.Character, built from the cast spec "creature"),
but the head is a hard-edged cube a little bigger than ours with the same face drawn on all four sides: two round
black eyes with a white glint, a long straight black mouth, putty skin. It is built once; the rig's own head is hidden
and the cube is parented to it, so it is one model in every shot. It is only ever seen moving nearer, never moving.

Acting keys read here (acting.py ignores them): "sit": true seats a rider on the chair under them (the chair is the
one whose centre is `seat` (+1 / -1 along the rider's x) away), legs forward and down, hands on the lap.

Cues read here:
- light: {"look": name, "ramp": s, plus any LOOKS key} the sky, fog, sun and fill ease to this look over `ramp`
- lift: {"state": "stop" | "go"} the cable stops or starts (a 1.5 s ease), when nobody rides
- sway: {"amp": degrees, "bias": degrees roll, "dur": s} how far the riders' chairs rock, easing over dur
- card: {"me": bool, "mr": bool} the pink pass card on its cord at my neck or Mr Halvor's
- cup: {"on": bool} the coffee on the deck rail
- ckey: {"gain": x} the creature's side key and rim (default 1)
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector as V

sys.path.insert(0, str(Path(__file__).resolve().parent / "generator"))
import geometry as G  # noqa: E402

from blocky import faces, rig  # noqa: E402

WATER = -0.45
BASE_FOG = 0.010

# looks: the sky (world colour and strength), fog colour and density, the sun's lamp and disc, the follow-camera fill
LOOKS = {
    "pre": dict(sky="#3d5170", sky_s=2.3, fog="#47597a", fogd=0.010, sun_e=0.0, sun_c="#ffb48a", sun_el=7.0, disc=0.0,
                cam=1.0, cam_c="#9cb4e4"),
    "pink": dict(sky="#b7899f", sky_s=2.0, fog="#c997aa", fogd=0.011, sun_e=1.6, sun_c="#ffb898", sun_el=20.0, disc=2.4,
                 cam=0.8, cam_c="#ffd2cc"),
    "gold": dict(sky="#d6aa84", sky_s=2.1, fog="#e0b98e", fogd=0.011, sun_e=3.2, sun_c="#ffd391", sun_el=24.0, disc=3.0,
                 cam=0.7, cam_c="#ffe2b8"),
    # the warm turn (L64 on): brighter than the rides' dawn, so every face reads
    "warm1": dict(sky="#d9a0b4", sky_s=3.6, fog="#d9a9b8", fogd=0.011, sun_e=3.0, sun_c="#ffb898", sun_el=16.0, disc=2.4,
                  cam=1.5, cam_c="#ffe0d8"),
    "warm2": dict(sky="#e3b98f", sky_s=3.6, fog="#e8c295", fogd=0.011, sun_e=4.0, sun_c="#ffd391", sun_el=22.0, disc=3.0,
                  cam=1.3, cam_c="#fff0d0"),
    "fog": dict(sky="#8e959f", sky_s=1.0, fog="#9aa1ab", fogd=0.075, sun_e=0.0, sun_c="#e6e8ee", sun_el=20.0, disc=0.0,
                cam=0.3, cam_c="#e6eaf2"),
    "thin": dict(sky="#a8adb6", sky_s=0.38, fog="#b4b8c0", fogd=0.03, sun_e=0.0, sun_c="#ffd8c0", sun_el=20.0, disc=0.5,
                 cam=0.06, cam_c="#f1e6e6"),
}

CREATURE_ORANGE, PUTTY = "#c97c4a", "#8f8269"
GLINT = 7.0
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


def _hexl(kit, h):
    return kit.col(h)[:3]


# ------------------------------------------------------------------------------------------------ materials


def materials(kit):
    M = {}
    M["water"] = kit.plastic("#10171d", 0.05, name="lake", spec=0.9)
    M["pine_ground"] = kit.grime("#22382c", 0.45, 0.12, name="pine ground", rough=0.95)
    M["rock"] = kit.grime("#6f6f72", 0.45, 0.25, name="ridge rock", rough=0.95)
    M["pine"] = kit.plastic("#1b3226", 0.9, name="pine", spec=0.1)
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
    M["tally"] = kit.plastic(CREATURE_ORANGE, 0.75, name="tally orange", spec=0.1)
    M["concrete"] = kit.concrete("#7d7c78", 1.0, 0.4, name="pier concrete")
    M["lamp"] = kit.emit("#ffcf8a", 6.0, name="hut lamp")
    M["gaterope"] = kit.plastic("#a08c66", 0.9, name="gate rope")
    M["cup"] = kit.plastic("#e9e4da", 0.6, name="paper cup")
    M["steam"] = kit.emit("#dcdfe4", 0.5, name="steam")
    M["card"] = kit.plastic("#f4a7b9", 0.5, name="pass card")
    M["cord"] = kit.plastic("#e58aa2", 0.7, name="pass cord")
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
    # the cup (cue)
    cup = kit.empty("cup", (0.6, 3.45, 1.11))
    kit.cyl("cup.body", 0.075, 0.13, (0, 0, 0.065), M["cup"], cup, n=14, r2=0.06)
    for k in range(3):
        kit.box(f"cup.steam{k}", (0.018, 0.018, 0.2 + 0.05 * k), (0.03 * (k - 1), 0.0, 0.26 + 0.05 * k), M["steam"], cup)
    ctx["cup"] = cup
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
    kit.light("ckey", "SPOT", (0, 0, 5), 0.0, "#d9e4ff", size=0.15, spot=38, blend=0.5)
    kit.light("crim", "SPOT", (0, 0, 5), 0.0, "#ffb7c4", size=0.15, spot=38, blend=0.5)
    kit.light("hutfill", "POINT", (-3.0, -6.0, 2.6), 40.0, "#ffc890", size=0.4, shadow=False)


# ------------------------------------------------------------------------------------------------ the creature's head


def face_png():
    from PIL import Image, ImageDraw

    W = 512
    im = Image.new("RGB", (W, W), faces.hexrgb(PUTTY))
    d = ImageDraw.Draw(im)
    ink = (14, 12, 12)
    for sx in (-1, 1):
        cx, cy, r = W * (0.5 + sx * 0.235), W * 0.40, W * 0.14
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ink)
        g = W * 0.05
        gx, gy = cx + r * 0.32, cy - r * 0.34
        d.ellipse([gx - g, gy - g, gx + g, gy + g], fill=(255, 251, 238))
    th = W * 0.045
    x0, x1, y = W * 0.12, W * 0.88, W * 0.77
    d.line([(x0, y), (x1, y)], fill=ink, width=int(th))
    for x in (x0, x1):
        d.ellipse([x - th / 2, y - th / 2, x + th / 2, y + th / 2], fill=ink)
    return im


def make_cube_head(kit, ctx):
    """The cube, parented to the creature's head pivot, replacing the rig's rounded head."""
    root = bpy.data.objects.get("creature")
    hg = bpy.data.objects.get("creature.headg")
    if root is None or hg is None:
        return False
    ctx["creature_head_rig"] = bpy.data.objects.get("creature.headm")
    side = 1.75
    skin = kit.plastic(PUTTY, 0.45, name="putty")
    kit.box("creature.cube", (side, side, side), (0, 0, 0), skin, hg, bevel=0.012)
    pil = face_png()
    img = bpy.data.images.new("fourface", pil.width, pil.height)
    a = np.asarray(pil.convert("RGBA")).astype(np.float32)[::-1] / 255
    img.pixels.foreach_set(a.ravel())
    img.pack()
    img.colorspace_settings.name = "sRGB"
    m = kit._new("fourface")
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.4
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = img
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(tx.outputs["Color"], bw.inputs["Color"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.80
    ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp.color_ramp.elements[1].position = 0.88
    ramp.color_ramp.elements[1].color = (1.0, 0.96, 0.88, 1)
    nt.links.new(bw.outputs["Val"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = GLINT
    kit._fogged(m, b.outputs[0])
    h = side / 2 + 0.004
    for k in range(4):
        verts = [(-side / 2, -h, -side / 2), (side / 2, -h, -side / 2), (side / 2, -h, side / 2), (-side / 2, -h, side / 2)]
        pl = kit.mesh_obj(f"creature.face{k}", verts, [(0, 1, 2, 3)], m, hg, rot=(0, 0, k * math.pi / 2))
        uv = pl.data.uv_layers.new(name="UVMap")
        for li, uvv in zip(pl.data.polygons[0].loop_indices, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            uv.data[li].uv = uvv
    for ob in root.children_recursive:
        ob.hide_render = root.hide_render   # built mid-run: take the creature's hidden state at once
    ctx["cube_ready"] = True
    return True


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
    ctx["card_ready"] = False
    # opt-in camera aim: a shot's "aim": {"who", "off"} points its camera at that cast member's feet-root + off
    import __main__
    from blocky import acting as _a

    if hasattr(__main__, "cam_at") and not getattr(__main__, "_aim_patched", False):
        orig = __main__.cam_at

        def cam_at2(spec, shot, t, chars, tl_):
            loc, tgt, lens, roll = orig(spec, shot, t, chars, tl_)
            aim = spec.get("aim")
            if aim:
                st = _a.state(tl_, aim["who"], t)
                o = aim.get("off", [0.0, 0.0, 0.0])
                tgt = (st["x"] + o[0], st["y"] + o[1], st["z"] + o[2])
            return loc, tgt, lens, roll

        __main__.cam_at = cam_at2
        __main__._aim_patched = True
    return ctx


# ------------------------------------------------------------------------------------------------ per frame


def clock(ctx, t):
    dt, C = ctx["clock"]
    k = min(len(C) - 2, int(t / dt))
    u = t / dt - k
    return C[k] + (C[k + 1] - C[k]) * u


def look_state(tl, t):
    cs = _cues(tl, "light")
    prev = dict(LOOKS["pre"])
    cur = dict(prev)
    for c in cs:
        if c["t"] > t:
            break
        tgt = {**LOOKS[c.get("look", "pre")], **{k: v for k, v in c.items() if k in LOOKS["pre"]}}
        u = _ss((t - c["t"]) / max(0.01, c.get("ramp", 3.0)))
        cur = {}
        for k, v in tgt.items():
            pv = prev[k]
            if isinstance(v, str):
                a, b = _rgb(pv), _rgb(v)
                cur[k] = tuple(a[i] + (b[i] - a[i]) * u for i in range(3))
            else:
                cur[k] = pv + (v - pv) * u
        if u >= 1:
            prev = {k: (v if not isinstance(v, tuple) else v) for k, v in cur.items()}
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
    w.inputs["Strength"].default_value = L["sky_s"]
    for nd in ctx["fog_nodes"]:
        nd.inputs[1].default_value = -L["fogd"]
    for nd in ctx["fog_cols"]:
        nd.inputs["Color"].default_value = (*_lin(L["fog"]), 1)
    el = math.radians(L["sun_el"])
    az = math.radians(8.0)
    s = V((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    sun = K.LIGHTS["sun"]
    sun["obj"].rotation_euler = (-s).to_track_quat("-Z", "Y").to_euler()
    sun["light"].color = _lin(L["sun_c"])
    K.LIGHTS["sun"]["base"] = max(L["sun_e"], 0.0001)
    ctx["disc"].location = tuple(s * 450.0)
    ctx["disc_e"].inputs["Strength"].default_value = L["disc"]
    ctx["disc_e"].inputs["Color"].default_value = (*_lin(L["sun_c"]), 1)
    # ---- the camera of this frame (the follow-camera fill and the creature's key)
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
    cf["base"] = 7.0 * min(dist, 12.0) ** 2 * L["cam"]
    # ---- the lift clock and the chairs
    P = clock(ctx, t)
    riders = []
    for who, keys in tl["acting"].items():
        if _ac._switch(keys, "sit", t, False):
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
    me_riding = next((r for r in riders if r[0] == "me"), None)
    if me_riding is not None:
        ycur = me_riding[1]["y"]
        P = ycur if me_riding[1]["yaw"] > 1.5 else (G.LL + G.ARC + (G.LL - ycur))
    # opt-in "phase" cue: put cable chair 0 at loop position `u` `when` seconds after the cue (so a chair is in the
    # shot), kept until the next phase cue (one with "off" puts it back)
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
    # cable chairs: skip any that overlap a special chair
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
    # ---- seated riders: legs forward and down, hands on the lap
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
            if arm is not None:
                arm.rotation_euler = (-math.radians(12), 0, 0)
    # sway: a chair and its riders rock about the grip
    for k, c in enumerate(cents[:3]):
        ob = ctx["special"][k]
        pivot = V((c[0], c[1], c[2] + HANG))
        a = math.radians(amp) * math.sin(2 * math.pi * 0.33 * t + k)
        roll = math.radians(bias) * 1.0 + a * 0.6
        pitch = a * 0.5
        # the chair's roll is about its travel axis: world x for an up/down chair
        ob.rotation_euler = (0, 0, c[3])
        _rot_about(ob, pivot, pitch, roll)
        for who in c[4]:
            r = bpy.data.objects[who]
            _rot_about(r, pivot, pitch, roll)
    # ---- the wheels
    ctx["wheel_b"].rotation_euler = (0, 0, P / G.R)
    ctx["wheel_t"].rotation_euler = (0, 0, P / G.R)
    # ---- the cup, the pass card
    ctx["cup"].hide_render = not _switch(_cues(tl, "cup"), "on", t, False)
    for ob in ctx["cup"].children:
        ob.hide_render = ctx["cup"].hide_render
    if not ctx["card_ready"]:
        ctx["card_ready"] = True
        ctx["cards"] = {}
        for key, who in (("me", "me"), ("mr", "mr_halvor")):
            tor = bpy.data.objects.get(f"{who}.torso")
            if tor is None:
                continue
            objs = []
            objs.append(K.box(f"card.{key}", (0.78, 0.05, 1.0), (0, -0.55, 1.15), ctx["M"]["card"], tor, bevel=0.03))
            for sx in (-1, 1):
                b = K.box(f"cord.{key}{sx}", (0.07, 0.04, 1.2), (sx * 0.42, -0.53, 1.45), ctx["M"]["cord"], tor)
                b.rotation_euler = (0, sx * 0.55, 0)
                objs.append(b)
            ctx["cards"][key] = objs
    for key, objs in ctx.get("cards", {}).items():
        on = _switch(_cues(tl, "card"), key, t, key == "me")
        who = "me" if key == "me" else "mr_halvor"
        root = bpy.data.objects.get(who)
        hidden = root is None or root.hide_render
        for ob in objs:
            ob.hide_render = (not on) or hidden
    # ---- props on people: the Halvors' laced boots, Mr Halvor's beard
    if not ctx.get("props_ready"):
        ctx["props_ready"] = True
        for who, bc in (("mr_halvor", "#7a3b2a"), ("mrs_halvor", "#2c4a35")):
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
        hg = bpy.data.objects.get("mr_halvor.headg")
        if hg is not None:
            K.box("mr_halvor.beard", (0.98, 0.2, 0.42), (0, -0.55, -0.4), K.plastic("#f1f0ec", 0.9, name="beard"), hg, bevel=0.07)
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
            sc = root.scale
            k = dv.length / (1.75 * sc.z)
            M2 = Matrix((tuple(xx), tuple(z.cross(xx)), tuple(z))).transposed().to_4x4() @ Matrix.Diagonal((sc.x, sc.y, sc.z * k, 1))
            M2.translation = sh
            ob.matrix_world = M2
    # ---- the creature
    if not ctx.get("cube_ready"):
        make_cube_head(kit, ctx)
    cr = bpy.data.objects.get("creature")
    on_screen = cr is not None and not cr.hide_render
    if ctx.get("creature_head_rig") is not None:
        ctx["creature_head_rig"].hide_render = True
    ck = _switch(_cues(tl, "ckey"), "gain", t, 1.0)
    for nm in ("ckey", "crim"):
        over[nm] = 0.0
    if on_screen:
        head = V(cr.matrix_world.translation) + V((0, 0, 1.62))
        bpy.context.view_layer.update()
        head = cr.matrix_world @ V((0, 0, 4.6))
        to_cam = (cam - head)
        to_cam.z = 0
        if to_cam.length < 1e-3:
            to_cam = V((0, -1, 0))
        to_cam.normalize()
        side = to_cam.cross(V((0, 0, 1)))
        kd = max(1.5, min(dist, 6.0))
        key = K.LIGHTS["ckey"]
        key["obj"].location = head + side * 1.7 + to_cam * 0.1 + V((0, 0, -0.45))
        K.aim(key["obj"], tuple(head))
        key["base"] = 380.0 * ck * (key["obj"].location - head).length ** 2 / 2.2 * min(1.0, max(0.3, (cam - head).length / 3.9) ** 1.4)
        key["light"].color = _lin(L.get("cam_c", "#d9e4ff")) if False else (0.7, 0.8, 1.0)
        over["ckey"] = 1.0
        rim = K.LIGHTS["crim"]
        rim["obj"].location = head - to_cam * 1.5 + V((0, 0, 0.8)) - side * 1.0
        K.aim(rim["obj"], tuple(head))
        rim["base"] = 520.0 * ck * (rim["obj"].location - head).length ** 2 / 2.5
        over["crim"] = 1.0
    return over
