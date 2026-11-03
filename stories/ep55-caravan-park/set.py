"""Caravan Park: a static caravan park on a grassy headland in autumn, the town below it (bus shelter, shop bench,
station), the path up to the old bench, and the Kneeler. Built from kit.py's parts (ep55; nothing here is shared with
another story's set).

Coordinates (metres, z up, front is -y): our gate is at (0, 0) between two granite posts, and the two folding chairs
sit just inside it at y = -1.6 (mine at x = -0.7, Jory's at x = +0.7), facing +y, out to the path. Our caravan stands
behind them (y = -6.9 .. -4.5, door at x = 0, step unit in front of it). The headland path runs +y to the old bench
at (3.6, 20.5), set well back from the edge (the turf ends at y = 42, the sea far below). The row of neighbours is
along -x and +x. The town is far off along +x (bus shelter x = 80, shop x = 120, station x = 160), and a small
interior set (kettle, table and phone, coat hook) sits at x = 300.

THE KNEELER: a person built from the same blocks, far too tall. It only ever kneels (shins flat behind it, hands at
its sides), as tall as the 2.1 m gatepost. Caravan cream from head to chest, a broad lichen band across the middle,
cream again below, two small black eyes with a warm highlight each. No moss anywhere on it. One model, posed by
lean and head pitch/yaw, and only ever changing across a cut except the slow head bend.

Cues read here (all optional; every ramp is a "dur" in seconds):
- env: {"set": name, "dur"} the light (sun, sky, fog) ramps to a preset
- lamp: {"v": 0..1, "dur"} the porch lamp; window: {"v", "dur"} the lit kitchen window
- moss: {"who", "v": level, "dur"} how much moss a character wears; shower: {"who"} the moss bursts off
- kneeler: {"show": bool, "lean": degrees, "pitch": degrees, "yaw": degrees, "dur"}
- hollows: {"which": "step"|"chair", "v": 0..1.2, "dur"}; water: {"which", "v"}; mat: {"v": 0..1} (step mat pushed);
- cap: {"v": 0|1} the cap on the right gatepost; seatmoss: {"v": 0|1} Jory's chair seat green
- gulls: {"v": 0|1, "x0", "y0", "z0", "dx", "dy"} gulls in the air; sitgull: {"v"} a gull on the post
- phone: {"v"} the phone on the table shudders; train: {"v"} the train at the platform
Acting keys read here (acting.py ignores them): "sit": true bends both legs forward.
"""

from __future__ import annotations

import math

import bpy
import numpy as np
from mathutils import Vector as V

from blocky import acting as AC
from blocky import faces, rig

# ------------------------------------------------------------------------------------------------ places
GATE_X = 0.75                       # the gateposts at x = +-0.75, y = 0
CHAIR_Y = -1.6
CHAIR_ME = (-0.7, CHAIR_Y)
CHAIR_JO = (0.7, CHAIR_Y)
KNEEL = (-1.7, -2.3)             # the Kneeler by my chair
KNEEL_STEP = (-1.0, -3.2)           # its hollows by the step
CARAVAN = dict(x0=-3.3, x1=3.3, y0=-6.9, y1=-4.5, h=2.5)
DOOR_X = 0.0
BENCH = (3.6, 20.5)
PATH_END = 42.0
INT = (300.0, -90.0)                  # the interior set
TOWN_BUS, TOWN_SHOP, TOWN_STN = 80.0, 120.0, 160.0
KS = rig.S

PRESETS = {   # sun strength, sun colour, elevation, azimuth, sky colour, sky strength, fog colour, fog multiplier, window glow
    "day": (4.6, "#fff1da", 40, 205, "#bfd3df", 1.15, "#c9d7dc", 1.0, 0.0),
    "gold": (4.2, "#ffc77f", 17, 215, "#ecc79c", 0.95, "#e4cba8", 1.4, 0.15),
    "dusk": (2.4, "#ff9d5e", 6, 220, "#f2b17c", 0.85, "#dcab8c", 2.0, 0.55),
    "morn": (2.6, "#ffe9d2", 13, 140, "#cfd9dd", 1.1, "#cbd5d8", 3.0, 0.0),
    "fog": (1.5, "#f0e8dc", 22, 205, "#a3adb3", 0.95, "#a3adb3", 14.0, 0.0),
    "fogdusk": (0.7, "#f0d8c0", 12, 205, "#848e96", 0.5, "#8a949c", 14.0, 0.9),
    "foglift": (3.2, "#fff0dc", 26, 205, "#c0cacd", 1.1, "#c0cacd", 2.5, 0.0),
    "grey": (1.3, "#e6e8ea", 28, 205, "#aab3b8", 1.0, "#aab3b8", 3.0, 0.0),
    "gold2": (4.0, "#ffc27a", 15, 215, "#ecc49a", 0.95, "#e6c9a6", 1.6, 0.2),
    "dusk2": (2.2, "#ff9f62", 6, 220, "#f0b07a", 0.9, "#dcab8c", 2.2, 0.6),
    "cold": (0.9, "#c2c8d6", 7, 220, "#9ba5b4", 0.75, "#9aa3b0", 4.5, 0.7),
}


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _hash(*xs):
    h = 0
    for x in xs:
        h = (h * 1000003) ^ int(x * 7919 + 17)
        h &= 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0x5BD1E995) & 0xFFFFFFFF
    h ^= h >> 15
    return (h & 0xFFFF) / 65535


def _cues(tl, name, who=None):
    key = ("cc", name, who)
    C = tl.setdefault("_cc", {})
    if key not in C:
        C[key] = sorted([c for c in tl["cues"] if c["name"] == name and (who is None or c.get("who") == who)],
                        key=lambda c: c["t"])
    return C[key]


def _ramped(cs, t, key, default, get=lambda x: x, mix=None):
    """A value that eases from one cue's setting to the next over the newer cue's `dur`."""
    cs = [c for c in cs if key in c]
    mix = mix or (lambda a, b, u: a + (b - a) * u)
    idx = -1
    for i, c in enumerate(cs):
        if c["t"] <= t + 1e-9:
            idx = i
    if idx < 0:
        return default

    def val(i, tt):
        c = cs[i]
        prev = default if i == 0 else val(i - 1, c["t"])
        d = c.get("dur", 0.0)
        u = 1.0 if d <= 0 else _ss((tt - c["t"]) / d)
        return mix(prev, get(c[key]), u)
    return val(idx, t)


def _hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _vec_mix(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


def _pvec(name):
    p = PRESETS[name]
    return (p[0], *_hexrgb(p[1]), p[2], p[3], *_hexrgb(p[4]), p[5], *_hexrgb(p[6]), p[7], p[8])


# ------------------------------------------------------------------------------------------------ materials


def _mixed(kit, name, base, other, amount, scale=6.0, rough=0.9, dark=None, detail=6.0):
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = detail
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.62 - amount * 0.5
    ramp.color_ramp.elements[0].color = kit.col(base)
    ramp.color_ramp.elements[1].position = 0.78 - amount * 0.4
    ramp.color_ramp.elements[1].color = kit.col(other)
    if dark:
        e = ramp.color_ramp.elements.new(0.2)
        e.color = kit.col(dark)
    L.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    L.new(ramp.outputs["Color"], b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m


def _image_mat(kit, name, pil, rough=0.5, emit=0.0):
    img = bpy.data.images.new(name, pil.width, pil.height, alpha=False)
    a = np.asarray(pil.convert("RGBA")).astype(np.float32)[::-1] / 255
    img.pixels.foreach_set(a.ravel())
    img.pack()
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = img
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    if emit:
        nt.links.new(tx.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    kit._fogged(m, b.outputs[0])
    return m, img


def materials(kit):
    M = {}
    M["turf"] = _mixed(kit, "turf", "#7f9a4e", "#b8874a", 0.55, 2.2, 0.95, dark="#62793c")
    M["turf_wet"] = _mixed(kit, "turf wet", "#6d8645", "#8d7a45", 0.4, 2.2, 0.35, dark="#4f6733")
    M["path"] = _mixed(kit, "path", "#b9a273", "#8c7a52", 0.5, 3.0, 0.95)
    M["sea"] = kit.plastic("#5d7480", 0.25, name="sea")
    M["cream"] = kit.plastic("#e6dcc0", 0.55, name="caravan cream")
    M["roof"] = kit.plastic("#d4cdb8", 0.6, name="caravan roof")
    M["lichen"] = kit.plastic("#7d9a5a", 0.55, name="lichen stripe")
    M["blue"] = kit.plastic("#5c7fa3", 0.55, name="stripe blue")
    M["rust"] = kit.plastic("#b0603a", 0.55, name="stripe rust")
    M["mustard"] = kit.plastic("#d3a73c", 0.55, name="stripe mustard")
    M["glass"] = kit.plastic("#2b3640", 0.12, name="van glass")
    M["frame"] = kit.plastic("#cfc6aa", 0.6, name="van frame")
    M["door"] = kit.plastic("#d8cfb4", 0.55, name="van door")
    M["metal"] = kit.metal("#9ba0a3", 0.4, name="step metal")
    M["coir"] = _mixed(kit, "coir", "#8a6a3d", "#5f4527", 0.5, 18.0, 0.95)
    M["granite"] = _mixed(kit, "granite", "#8c8a84", "#6c6a66", 0.5, 7.0, 0.85)
    M["white"] = kit.plastic("#f1efe6", 0.6, name="picket white")
    M["canvas"] = kit.plastic("#c8b58a", 0.9, name="canvas")
    M["canvas2"] = kit.plastic("#8a5f4a", 0.9, name="canvas rust")
    M["chairframe"] = kit.plastic("#5b4a38", 0.6, name="chair frame")
    M["wood"] = _mixed(kit, "weathered wood", "#7b6a58", "#5a4d3f", 0.4, 6.0, 0.9)
    M["gorse"] = _mixed(kit, "gorse", "#3e4a2c", "#566236", 0.4, 4.0, 0.9)
    M["gorse_f"] = kit.plastic("#e3c53a", 0.6, name="gorse flower")
    M["bracken"] = _mixed(kit, "bracken", "#b8874a", "#8b6234", 0.5, 4.0, 0.9)
    M["moss"] = _mixed(kit, "moss", "#6f8f3e", "#9fb860", 0.6, 14.0, 0.95, detail=3.0)
    M["flower"] = kit.plastic("#f4f2e6", 0.5, name="moss flower")
    M["rustcap"] = kit.plastic("#c2602a", 0.9, name="rust cap")
    M["lampglass"] = kit.emit("#f2c47c", 9.0, name="porch lamp glass")
    M["water"] = kit.plastic("#43525b", 0.04, name="hollow water")
    M["shop"] = kit.plastic("#b9906a", 0.7, name="shop wall")
    M["shopred"] = kit.plastic("#8d4a3a", 0.7, name="shop roof")
    M["kettle"] = kit.plastic("#c8483a", 0.35, name="painted kettle")
    M["platform"] = _mixed(kit, "platform", "#8a8780", "#6e6c66", 0.5, 5.0, 0.9)
    M["train"] = kit.plastic("#4f6a78", 0.5, name="train")
    M["dark"] = kit.plastic("#262a30", 0.6, name="dark")
    M["coatgrey"] = kit.plastic("#56626c", 0.8, name="coat grey")
    M["ink"] = kit.plastic("#2a2420", 0.7, name="ink")
    M["floor"] = kit.plastic("#8b7a5f", 0.8, name="in floor")
    M["wall"] = kit.plastic("#d9d0b6", 0.9, name="in wall")
    M["screen"] = kit.emit("#bfe6ff", 1.6, name="phone glow")
    M["steam"] = kit.plastic("#b9bcbf", 0.3, name="steel")
    M["gull"] = kit.plastic("#eceae4", 0.6, name="gull")
    M["gullwing"] = kit.plastic("#8f969c", 0.6, name="gull wing")
    M["bill"] = kit.plastic("#d9a441", 0.6, name="gull bill")
    M["flake"] = kit.plastic("#7da043", 0.9, name="moss flake")
    M["petal"] = kit.plastic("#f6f4ea", 0.7, name="petal")
    M["bushglow"] = kit.emit("#f6e8b0", 1.0, name="window glow")
    return M


def wbox(kit, name, lo, hi, mat, parent=None, bevel=0.0):
    """A box from two world corners (object space = world space, so patterns line up)."""
    lo, hi = tuple(min(a, b) for a, b in zip(lo, hi)), tuple(max(a, b) for a, b in zip(lo, hi))
    c = tuple((a + b) / 2 for a, b in zip(lo, hi))
    s = tuple(b - a for a, b in zip(lo, hi))
    if bevel:
        return kit.box(name, s, c, mat, parent, bevel=bevel)
    return kit.mesh_obj(name, kit.box_verts(*s, c), kit.BOX_FACES, mat, parent)


# ------------------------------------------------------------------------------------------------ the ground


GRID = dict(x0=-6.0, x1=6.0, y0=-8.0, y1=2.0, step=0.1)      # the finely cut yard, where the hollows go
HOLLOWS = {
    # (x, y, rx, ry, depth): knees; shin grooves are long shallow ovals behind them (toward -y)
    "step": [(KNEEL_STEP[0] - 0.26, KNEEL_STEP[1], 0.24, 0.24, 0.2), (KNEEL_STEP[0] + 0.26, KNEEL_STEP[1], 0.24, 0.24, 0.2),
             (KNEEL_STEP[0] - 0.26, KNEEL_STEP[1] - 0.55, 0.17, 0.6, 0.045),
             (KNEEL_STEP[0] + 0.26, KNEEL_STEP[1] - 0.55, 0.17, 0.6, 0.045)],
    "chair": [(KNEEL[0] - 0.26, KNEEL[1], 0.24, 0.24, 0.2), (KNEEL[0] + 0.26, KNEEL[1], 0.24, 0.24, 0.2),
              (KNEEL[0] - 0.26, KNEEL[1] - 0.55, 0.17, 0.6, 0.05), (KNEEL[0] + 0.26, KNEEL[1] - 0.55, 0.17, 0.6, 0.05)],
}


def build_ground(kit, ctx, M):
    # the far turf, in four pieces round the finely cut yard (so no piece overlaps it)
    g = GRID
    big = 400.0
    wbox(kit, "turf n", (-big, g["y1"], -0.5), (big + 120, PATH_END, 0.0), M["turf"])
    wbox(kit, "turf s", (-big, -60.0, -0.5), (big + 120, g["y0"], 0.0), M["turf"])
    wbox(kit, "turf w", (-big, g["y0"], -0.5), (g["x0"], g["y1"], 0.0), M["turf"])
    wbox(kit, "turf e", (g["x1"], g["y0"], -0.5), (big + 120, g["y1"], 0.0), M["turf"])
    wbox(kit, "sea", (-900, PATH_END, -12.5), (900, 900, -12.0), M["sea"])
    wbox(kit, "cliff", (-big, PATH_END, -12.0), (big + 120, PATH_END + 0.4, 0.0), M["granite"])
    nx = int(round((g["x1"] - g["x0"]) / g["step"]))
    ny = int(round((g["y1"] - g["y0"]) / g["step"]))
    xs = np.linspace(g["x0"], g["x1"], nx + 1)
    ys = np.linspace(g["y0"], g["y1"], ny + 1)
    X, Y = np.meshgrid(xs, ys)
    verts = [(float(x), float(y), 0.0) for x, y in zip(X.ravel(), Y.ravel())]
    fcs = []
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            fcs.append((a, a + 1, a + nx + 2, a + nx + 1))
    ob = kit.mesh_obj("yard", verts, fcs, M["turf_wet"], smooth=True)
    ctx["yard"] = ob
    ctx["yard_xy"] = (X.ravel(), Y.ravel())
    ctx["yard_z"] = None
    # the worn path, up the headland in two bends
    pts = [(0.0, 0.0), (0.0, 6.0), (1.0, 11.0), (2.4, 16.0), (3.4, 20.5)]
    for k, ((ax, ay), (bx, by)) in enumerate(zip(pts, pts[1:])):
        n = 6
        for q in range(n):
            u0, u1 = q / n, (q + 1) / n
            x0, y0 = ax + (bx - ax) * u0, ay + (by - ay) * u0
            x1, y1 = ax + (bx - ax) * u1, ay + (by - ay) * u1
            ang = math.atan2(y1 - y0, x1 - x0)
            wd = 0.46 + 0.1 * math.sin(k + q)
            seg = kit.plane(f"path{k}.{q}", (math.hypot(x1 - x0, y1 - y0) + 0.2, wd * 2), ((x0 + x1) / 2, (y0 + y1) / 2, 0.012),
                            M["path"], rot=(0, 0, ang))
    # the beaten patch by the gate and the step
    kit.plane("path gate", (2.4, 2.4), (0.0, -0.6, 0.011), M["path"])
    kit.plane("path step", (1.3, 2.2), (0.75, -3.4, 0.011), M["path"])   # clear of the hollows at x -1.5 to -0.5
    for tag, (px, py) in (("a", (-2.0, 8.0)), ("b", (2.5, 12.0))):
        pass
    # gorse and bracken along the path and on the headland
    n = 0
    for i in range(130):
        r1, r2, r3, r4 = (_hash(i, k) for k in range(4))
        y = 3.0 + r1 * 36.0
        side = -1 if r2 < 0.5 else 1
        px = np.interp(y, [p[1] for p in pts] + [60], [p[0] for p in pts] + [4.0])
        x = px + side * (1.6 + r3 * 16.0 * (0.5 + y / 60))
        if abs(x - px) < 1.5:
            continue
        if y > 17 and abs(x - BENCH[0]) < 2.6 and abs(y - BENCH[1]) < 2.2:
            continue
        s = 0.5 + r4 * 0.8
        if r2 < 0.2 or r2 > 0.8:
            gorse(kit, M, f"gorse{n}", x, y, s, i)
        else:
            bracken(kit, M, f"bracken{n}", x, y, s, i)
        n += 1
    # a few clumps near the caravans
    for i in range(24):
        x = -14 + _hash(i, 50) * 28
        y = 3 + _hash(i, 51) * 3.5 + (0 if abs(x) > 3 else 2)
        if abs(x) < 3 and y < 5:
            continue
        gorse(kit, M, f"gorsef{i}", x, y, 0.4 + _hash(i, 52) * 0.4, 100 + i)


def gorse(kit, M, name, x, y, s, seed):
    for k in range(3):
        dx, dy = (_hash(seed, k, 1) - 0.5) * s * 1.2, (_hash(seed, k, 2) - 0.5) * s * 1.2
        r = s * (0.45 + _hash(seed, k, 3) * 0.3)
        b = kit.sphere(f"{name}.{k}", 1.0, (x + dx, y + dy, r * 0.45), M["gorse"], seg=8)
        b.scale = (r, r, r * 0.8)
    for k in range(4):
        a = _hash(seed, k, 4) * 6.28
        kit.sphere(f"{name}.f{k}", 0.07, (x + math.cos(a) * s * 0.4, y + math.sin(a) * s * 0.4, s * (0.5 + 0.2 * _hash(seed, k, 5))),
                   M["gorse_f"], seg=6)


def bracken(kit, M, name, x, y, s, seed):
    for k in range(4):
        a = _hash(seed, k, 6) * 6.28
        r = s * (0.3 + _hash(seed, k, 7) * 0.5)
        kit.cyl(f"{name}.{k}", s * 0.35, s * 0.9, (x + math.cos(a) * r * 0.6, y + math.sin(a) * r * 0.6, s * 0.4),
                M["bracken"], rot=((_hash(seed, k, 8) - 0.5) * 0.4, (_hash(seed, k, 9) - 0.5) * 0.4, 0), n=7, r2=s * 0.05)


# ------------------------------------------------------------------------------------------------ the park


def caravan(kit, ctx, M, name, cx, y0, stripe, ours=False, lit=False, door_x=0.0):
    """A static caravan, long side to the gate (+y). Returns the parts the story animates."""
    w, d, h = 6.6, 2.4, 2.5
    x0, x1, y1 = cx - w / 2, cx + w / 2, y0 + d
    out = {}
    wbox(kit, f"{name}.body", (x0, y0, 0.45), (x1, y1, h), M["cream"], bevel=0.12)
    wbox(kit, f"{name}.plinth", (x0 + 0.1, y0 + 0.1, 0.0), (x1 - 0.1, y1 - 0.1, 0.5), M["steam"])
    wbox(kit, f"{name}.roof", (x0 + 0.1, y0 + 0.1, h - 0.02), (x1 - 0.1, y1 - 0.1, h + 0.14), M["roof"], bevel=0.05)
    wbox(kit, f"{name}.stripe", (x0 - 0.01, y1 - 0.02, 1.25), (x1 + 0.01, y1 + 0.02, 1.55), M[stripe], bevel=0.01)
    for sx in (-1, 1):
        wbox(kit, f"{name}.endstripe{sx}", (cx + sx * w / 2 - 0.02 + (0.02 if sx > 0 else 0), y0, 1.25),
             (cx + sx * w / 2 + 0.02 + (0.02 if sx > 0 else 0), y1, 1.55), M[stripe])
    # the door (a recess in the middle) and windows
    wbox(kit, f"{name}.doorframe", (cx + door_x - 0.52, y1 - 0.01, 0.62), (cx + door_x + 0.52, y1 + 0.05, 2.12), M["frame"], bevel=0.02)
    wbox(kit, f"{name}.door", (cx + door_x - 0.44, y1 + 0.05, 0.68), (cx + door_x + 0.44, y1 + 0.09, 2.06), M["door"], bevel=0.015)
    wbox(kit, f"{name}.doorwin", (cx + door_x - 0.27, y1 + 0.09, 1.38), (cx + door_x + 0.27, y1 + 0.11, 1.93), M["glass"])
    wbox(kit, f"{name}.handle", (cx + door_x + 0.30, y1 + 0.09, 1.12), (cx + door_x + 0.38, y1 + 0.14, 1.2), M["steam"])
    wins = []
    for sx in (-1, 1):
        wx = cx + sx * 2.0
        wbox(kit, f"{name}.winframe{sx}", (wx - 0.62, y1 - 0.01, 1.58), (wx + 0.62, y1 + 0.04, 2.3), M["frame"], bevel=0.02)
        pane = wbox(kit, f"{name}.pane{sx}", (wx - 0.54, y1 + 0.04, 1.65), (wx + 0.54, y1 + 0.055, 2.23), M["glass"])
        wins.append((pane, wx))
    out["wins"] = wins
    # the three-step metal step unit with a coir mat on the bottom step
    sx0 = cx + door_x
    for k in range(3):
        wbox(kit, f"{name}.step{k}", (sx0 - 0.55, y1 + 0.78 - 0.3 * k - 0.0, 0.0), (sx0 + 0.55, y1 + 1.08 - 0.3 * k, 0.17 * (k + 1) * 1.4),
             M["metal"], bevel=0.015)
    for sx in (-1, 1):
        wbox(kit, f"{name}.stepside{sx}", (sx0 + sx * 0.56 - 0.025, y1 + 0.2, 0.0), (sx0 + sx * 0.56 + 0.025, y1 + 1.08, 0.48), M["metal"])
    if ours:
        out["step_y"] = y1 + 0.93
        out["step_x"] = sx0
        # the bottom step's plate (y1+0.78..1.08, top at 0.24) is where the two lichen tally strokes go
        for k, dx in enumerate((-0.14, 0.14)):
            wbox(kit, f"{name}.tally{k}", (sx0 + dx - 0.035, y1 + 0.84, 0.236 + 0.008), (sx0 + dx + 0.035, y1 + 1.04, 0.236 + 0.03),
                 M["lichen"])
        mat = wbox(kit, f"{name}.mat", (sx0 - 0.46, y1 + 0.82, 0.236), (sx0 + 0.46, y1 + 1.04, 0.28), M["coir"], bevel=0.01)
        out["mat"] = mat
        out["mat_base"] = tuple(mat.location)
        out["mat0"] = (sx0, y1 + 0.93)
        # the porch lamp, to the right of the door
        lamp = kit.sphere(f"{name}.lamp", 0.1, (sx0 + 0.86, y1 + 0.14, 2.0), M["lampglass"], seg=10)
        kit.cyl(f"{name}.lampbase", 0.06, 0.05, (sx0 + 0.86, y1 + 0.06, 2.0), M["dark"], rot=(math.pi / 2, 0, 0), n=10)
        out["lamp"] = lamp
        L = kit.light("lamp", "POINT", (sx0 + 0.86, y1 + 0.4, 2.0), 50.0, "#f2c47c", size=0.12)
        # the kitchen window's light (left window), spilling out
        kit.light("window", "AREA", (cx - 2.0, y1 + 0.5, 1.9), 60.0, "#ffc98a", size=1.1)
        kit.aim(kit.LIGHTS["window"]["obj"], (cx - 2.0, y1 + 5.0, 0.6))
        # glowing pane
        glow = wbox(kit, f"{name}.glow", (cx - 2.0 - 0.54, y1 + 0.06, 1.65), (cx - 2.0 + 0.54, y1 + 0.07, 2.23), M["bushglow"])
        out["glow"] = glow
    return out


def build_park(kit, ctx, M):
    ours = caravan(kit, ctx, M, "van", 0.0, CARAVAN["y0"], "lichen", ours=True)
    ctx["van"] = ours
    for i, (cx, st) in enumerate(((-9.4, "mustard"), (-18.8, "blue"), (9.4, "rust"), (18.8, "mustard"))):
        caravan(kit, ctx, M, f"nvan{i}", cx, CARAVAN["y0"], st)
        # a little porch lamp and step on each (no numbers)
    # the gate, the posts, the pickets
    for sx in (-1, 1):
        wbox(kit, f"post{sx}", (sx * GATE_X - 0.19, -0.19, 0.0), (sx * GATE_X + 0.19, 0.19, 2.1), M["granite"], bevel=0.03)
        wbox(kit, f"postcap{sx}", (sx * GATE_X - 0.23, -0.23, 2.1), (sx * GATE_X + 0.23, 0.23, 2.18), M["granite"], bevel=0.02)
    for sx in (-1, 1):  # picket fence runs out from each post
        for k in range(1, 22):
            x = sx * (GATE_X + 0.45 * k)
            wbox(kit, f"pk{sx}.{k}", (x - 0.04, -0.03, 0.0), (x + 0.04, 0.03, 1.0 - 0.02 * (k % 2)), M["white"])
        wbox(kit, f"rail{sx}a", (min(sx * GATE_X, sx * 10.3), -0.04, 0.65), (max(sx * GATE_X, sx * 10.3), 0.04, 0.72), M["white"])
        wbox(kit, f"rail{sx}b", (min(sx * GATE_X, sx * 10.3), -0.04, 0.25), (max(sx * GATE_X, sx * 10.3), 0.04, 0.32), M["white"])
    # the gate leaf, open a little, hinged on the left post
    for k in range(8):
        x = -GATE_X + 0.16 + 0.17 * k
        wbox(kit, f"gk{k}", (x - 0.04, 0.55, 0.0), (x + 0.04, 0.6, 0.95), M["white"])
    wbox(kit, "gate rail a", (-GATE_X + 0.1, 0.54, 0.62), (-GATE_X + 1.4, 0.61, 0.69), M["white"])
    wbox(kit, "gate rail b", (-GATE_X + 0.1, 0.54, 0.24), (-GATE_X + 1.4, 0.61, 0.31), M["white"])
    # the two folding canvas chairs
    for nm, (cx, cy), mat in (("me", CHAIR_ME, "canvas"), ("jo", CHAIR_JO, "canvas2")):
        chair(kit, ctx, M, nm, cx, cy, M[mat])
    # Jory's chair seat is moss when the cue says so
    seat = kit.box("seatmoss", (0.5, 0.46, 0.07), (CHAIR_JO[0], CHAIR_JO[1], 0.43), M["moss"], bevel=0.03)
    ctx["seatmoss"] = [seat]
    for k in range(10):
        f = kit.cyl(f"seatflower{k}", 0.034, 0.012, (CHAIR_JO[0] + (_hash(k, 70) - 0.5) * 0.4, CHAIR_JO[1] + (_hash(k, 71) - 0.5) * 0.36, 0.48),
                    M["flower"], n=7)
        ctx["seatmoss"].append(f)
    # the rust cap on the right gatepost (furry with moss)
    cap = kit.empty("gatecap", (GATE_X, 0.0, 2.18))
    kit.cyl("gatecap.crown", 0.19, 0.2, (0, 0, 0.1), M["rustcap"], cap, n=14, r2=0.15)
    kit.box("gatecap.rib", (0.38, 0.38, 0.1), (0, 0, 0.02), M["rustcap"], cap, bevel=0.04)
    for k in range(7):
        s = kit.sphere(f"gatecap.m{k}", 1.0, (math.cos(k * 1.1) * 0.12, math.sin(k * 1.1) * 0.12, 0.17 + 0.03 * (k % 2)), M["moss"], cap, seg=8)
        s.scale = (0.1, 0.1, 0.06)
        kit.cyl(f"gatecap.f{k}", 0.03, 0.012, (math.cos(k * 1.7) * 0.11, math.sin(k * 1.7) * 0.11, 0.235), M["flower"], cap, n=7)
    ctx["cap"] = [cap] + list(cap.children_recursive)
    # the bench at the top
    bx, by = BENCH
    wbox(kit, "bench seat", (bx - 1.05, by - 0.22, 0.42), (bx + 1.05, by + 0.22, 0.48), M["wood"], bevel=0.015)
    wbox(kit, "bench back", (bx - 1.05, by + 0.2, 0.62), (bx + 1.05, by + 0.26, 0.98), M["wood"], bevel=0.015)
    for sx in (-1, 1):
        wbox(kit, f"bench leg{sx}", (bx + sx * 0.95 - 0.04, by - 0.2, 0.0), (bx + sx * 0.95 + 0.04, by + 0.24, 0.42), M["wood"])
        wbox(kit, f"bench post{sx}", (bx + sx * 0.95 - 0.04, by + 0.2, 0.42), (bx + sx * 0.95 + 0.04, by + 0.26, 0.98), M["wood"])
    # a gull post
    wbox(kit, "gull post", (-3.4, 7.0, 0.0), (-3.22, 7.18, 1.1), M["wood"])
    ctx["sitgull"] = gull(kit, M, "sitgull", (-3.31, 7.09, 1.18))
    # a few things by the caravan: a water butt
    kit.cyl("butt", 0.3, 0.9, (3.9, -4.1, 0.45), M["blue"], n=14)


def chair(kit, ctx, M, nm, cx, cy, canvas):
    """A folding canvas chair facing +y (open side toward the path)."""
    fr = M["chairframe"]
    for sx in (-1, 1):
        kit.box(f"ch{nm}.legf{sx}", (0.04, 0.04, 0.42), (cx + sx * 0.27, cy + 0.2, 0.21), fr, bevel=0.008)
        kit.box(f"ch{nm}.legb{sx}", (0.04, 0.04, 0.42), (cx + sx * 0.27, cy - 0.2, 0.21), fr, bevel=0.008)
        kit.box(f"ch{nm}.arm{sx}", (0.05, 0.5, 0.04), (cx + sx * 0.27, cy, 0.62), fr, bevel=0.01)
        kit.box(f"ch{nm}.post{sx}", (0.04, 0.04, 0.22), (cx + sx * 0.27, cy + 0.2, 0.52), fr, bevel=0.008)
        kit.box(f"ch{nm}.bpost{sx}", (0.04, 0.05, 0.62), (cx + sx * 0.27, cy - 0.21, 0.72), fr, bevel=0.008, rot=(-0.12, 0, 0))
    kit.box(f"ch{nm}.seat", (0.5, 0.46, 0.03), (cx, cy, 0.4), canvas, bevel=0.01)
    kit.box(f"ch{nm}.back", (0.5, 0.03, 0.46), (cx, cy - 0.23, 0.74), canvas, bevel=0.01, rot=(-0.12, 0, 0))


def gull(kit, M, name, loc, scale=1.0):
    root = kit.empty(name, loc)
    kit.box(f"{name}.body", (0.34 * scale, 0.14 * scale, 0.11 * scale), (0, 0, 0), M["gull"], root, bevel=0.03)
    kit.box(f"{name}.head", (0.1 * scale, 0.09 * scale, 0.09 * scale), (0.2 * scale, 0, 0.06 * scale), M["gull"], root, bevel=0.025)
    kit.box(f"{name}.bill", (0.07 * scale, 0.03 * scale, 0.025 * scale), (0.27 * scale, 0, 0.05 * scale), M["bill"], root)
    kit.box(f"{name}.tail", (0.12 * scale, 0.1 * scale, 0.03 * scale), (-0.22 * scale, 0, 0.0), M["gull"], root, bevel=0.01)
    wings = []
    for sx in (-1, 1):
        piv = kit.empty(f"{name}.wp{sx}", (0, sx * 0.06 * scale, 0.04 * scale), root)
        kit.box(f"{name}.wing{sx}", (0.22 * scale, 0.42 * scale, 0.025 * scale), (-0.02 * scale, sx * 0.21 * scale, 0), M["gullwing"], piv, bevel=0.008)
        wings.append((piv, sx))
    root["wings"] = [w[0].name for w in wings]
    return root


# ------------------------------------------------------------------------------------------------ the town


def build_town(kit, ctx, M):
    """The town faces +y (the sun and the camera are on that side); every y here is mirrored from the park's."""
    # bus shelter with its glyph disc (a curl over a bar)
    bx = TOWN_BUS
    for sx in (-1, 1):
        wbox(kit, f"bus post{sx}", (bx + sx * 1.3 - 0.05, -0.05, 0.0), (bx + sx * 1.3 + 0.05, 0.05, 2.3), M["steam"])
        wbox(kit, f"bus post b{sx}", (bx + sx * 1.3 - 0.05, -1.05, 0.0), (bx + sx * 1.3 + 0.05, -0.95, 2.3), M["steam"])
    wbox(kit, "bus roof", (bx - 1.5, -1.2, 2.3), (bx + 1.5, 0.2, 2.42), M["shopred"], bevel=0.03)
    wbox(kit, "bus back", (bx - 1.3, -1.06, 0.3), (bx + 1.3, -1.0, 2.3), M["glass"])
    wbox(kit, "bus seat", (bx - 1.0, -0.95, 0.42), (bx + 1.0, -0.6, 0.47), M["wood"])
    wbox(kit, "bus pole", (bx + 2.2, -0.04, 0.0), (bx + 2.28, 0.04, 2.6), M["steam"])
    kit.cyl("bus disc", 0.36, 0.04, (bx + 2.24, 0.07, 2.6), M["cream"], rot=(math.pi / 2, 0, 0), n=24)
    glyph(kit, M, "busglyph", (bx + 2.24, 0.1, 2.6), 0.2)
    # the shop and its bench, with a painted kettle sign
    sx0 = TOWN_SHOP
    wbox(kit, "shop wall", (sx0 - 2.6, -4.0, 0.0), (sx0 + 2.6, -1.0, 3.0), M["shop"], bevel=0.06)
    wbox(kit, "shop roof", (sx0 - 2.8, -4.2, 3.0), (sx0 + 2.8, -0.8, 3.25), M["shopred"], bevel=0.05)
    wbox(kit, "shop window", (sx0 - 2.0, -1.0, 0.8), (sx0 - 0.3, -0.97, 2.3), M["glass"])
    wbox(kit, "shop door", (sx0 + 0.6, -1.02, 0.0), (sx0 + 1.5, -0.97, 2.1), M["door"])
    kit.sphere("kettle body", 0.34, (sx0 + 1.7, -0.7, 2.7), M["kettle"], seg=14).scale = (1.0, 0.35, 0.85)
    kit.cyl("kettle spout", 0.05, 0.4, (sx0 + 1.3, -0.62, 2.8), M["kettle"], rot=(0, 0.9, 0), n=8, r2=0.03)
    kit.box("kettle handle", (0.5, 0.05, 0.05), (sx0 + 1.7, -0.62, 3.13), M["kettle"], bevel=0.02)
    wbox(kit, "sign arm", (sx0 + 1.25, -1.0, 3.0), (sx0 + 2.2, -0.9, 3.06), M["dark"])
    wbox(kit, "shop bench seat", (sx0 - 1.3, -0.55, 0.42), (sx0 + 0.3, -0.1, 0.48), M["wood"], bevel=0.015)
    wbox(kit, "shop bench back", (sx0 - 1.3, -0.56, 0.62), (sx0 + 0.3, -0.5, 1.0), M["wood"], bevel=0.015)
    for sx in (-1, 1):
        wbox(kit, f"shop bench leg{sx}", (sx0 - 0.5 + sx * 0.7 - 0.04, -0.54, 0.0), (sx0 - 0.5 + sx * 0.7 + 0.04, -0.12, 0.42), M["wood"])
    # the station: a platform, a lamp, a glyph board, a carriage
    px = TOWN_STN
    wbox(kit, "platform", (px - 12.0, -4.6, 0.0), (px + 12.0, -1.5, 0.45), M["platform"], bevel=0.02)
    wbox(kit, "platform line", (px - 12.0, -1.62, 0.45), (px + 12.0, -1.5, 0.46), M["cream"])
    wbox(kit, "track bed", (px - 40, -1.5, -0.15), (px + 40, 1.9, 0.0), M["dark"])
    for k in range(-50, 50):
        wbox(kit, f"sleeper{k}", (px + k * 0.8 - 0.1, -1.2, 0.0), (px + k * 0.8 + 0.1, 1.5, 0.05), M["wood"])
    for yy in (-0.4, 0.9):
        wbox(kit, f"rail{yy}", (px - 40, yy - 0.04, 0.05), (px + 40, yy + 0.04, 0.15), M["steam"])
    wbox(kit, "stn lamp pole", (px - 3.1, -3.98, 0.45), (px - 3.02, -3.9, 3.1), M["dark"])
    kit.sphere("stn lamp", 0.16, (px - 3.06, -3.94, 3.2), M["lampglass"], seg=10)
    wbox(kit, "stn board post a", (px + 4.0, -4.3, 0.45), (px + 4.06, -4.25, 1.9), M["dark"])
    wbox(kit, "stn board post b", (px + 5.34, -4.3, 0.45), (px + 5.4, -4.25, 1.9), M["dark"])
    wbox(kit, "glyph board", (px + 4.0, -4.25, 1.0), (px + 5.4, -4.2, 1.9), M["dark"])
    glyph(kit, M, "stnglyph", (px + 4.7, -4.17, 1.45), 0.25)
    # the carriage, its door side to the platform
    ctx["train"] = []
    t0 = kit.empty("train", (px, 0.2, 0.0))
    for name, lo, hi, mat in (("body", (-7, -1.3, 0.5), (7, 1.3, 3.2), "train"), ("under", (-6.8, -1.0, 0.15), (6.8, 1.0, 0.5), "dark"),
                              ("stripe", (-7.01, -1.31, 1.7), (7.01, 1.31, 1.95), "cream")):
        ctx["train"].append(wbox(kit, f"train.{name}", lo, hi, M[mat], t0, bevel=0.04))
    for sx in range(-5, 6, 2):
        if abs(sx) == 1:
            continue
        ctx["train"].append(wbox(kit, f"train.win{sx}", (sx - 0.6, -1.32, 2.0), (sx + 0.6, -1.29, 2.8), M["glass"], t0))
    ctx["train"].append(wbox(kit, "train.door", (-0.5, -1.33, 0.5), (0.5, -1.29, 2.8), M["dark"], t0))
    ctx["train_obs"] = [t0] + list(t0.children_recursive)


def glyph(kit, M, name, loc, r):
    """Our own glyph: a curl over a bar (made of blocks, no letters)."""
    x, y, z = loc
    s = 1
    kit.box(f"{name}.bar", (r * 1.6, 0.03, r * 0.28), (x, y + s * 0.015, z - r * 0.55), M["ink"], bevel=0.01)
    for k in range(9):
        a = math.pi * 1.5 * k / 8 + 0.4
        kit.box(f"{name}.c{k}", (r * 0.3, 0.03, r * 0.3), (x + math.cos(a) * r * 0.55, y + s * 0.015, z + r * 0.15 + math.sin(a) * r * 0.5),
                M["ink"], bevel=0.01, rot=(0, -a, 0))


# ------------------------------------------------------------------------------------------------ the interior


def build_interior(kit, ctx, M):
    ix, iy = INT
    # a closed box room: floor, walls, ceiling
    wbox(kit, "in floor", (ix - 2.2, iy - 2.0, -0.1), (ix + 2.2, iy + 2.0, 0.0), M["floor"])
    wbox(kit, "in ceil", (ix - 2.3, iy - 2.1, 2.3), (ix + 2.3, iy + 2.1, 2.4), M["wall"])
    wbox(kit, "in wall n", (ix - 2.3, iy + 2.0, 0.0), (ix + 2.3, iy + 2.1, 2.4), M["wall"])
    wbox(kit, "in wall s", (ix - 2.3, iy - 2.1, 0.0), (ix + 2.3, iy - 2.0, 2.4), M["wall"])
    wbox(kit, "in wall w", (ix - 2.3, iy - 2.1, 0.0), (ix - 2.2, iy + 2.1, 2.4), M["wall"])
    wbox(kit, "in wall e", (ix + 2.2, iy - 2.1, 0.0), (ix + 2.3, iy + 2.1, 2.4), M["wall"])
    # the hob and kettle (against the north wall)
    wbox(kit, "hob unit", (ix - 1.8, iy + 1.35, 0.0), (ix - 0.6, iy + 2.0, 0.9), M["frame"], bevel=0.02)
    wbox(kit, "hob top", (ix - 1.8, iy + 1.35, 0.9), (ix - 0.6, iy + 2.0, 0.94), M["dark"])
    kit.cyl("ring a", 0.15, 0.015, (ix - 1.4, iy + 1.7, 0.95), M["kettle"], n=16)
    kt = kit.empty("kettle", (ix - 1.4, iy + 1.7, 0.94))
    kit.cyl("kettle.body", 0.17, 0.2, (0, 0, 0.12), M["steam"], kt, n=16, r2=0.14)
    kit.cyl("kettle.lid", 0.08, 0.04, (0, 0, 0.24), M["steam"], kt, n=12)
    kit.box("kettle.handle", (0.26, 0.03, 0.03), (0, 0, 0.28), M["dark"], kt, bevel=0.01)
    kit.cyl("kettle.spout", 0.025, 0.14, (0.18, 0, 0.18), M["steam"], kt, rot=(0, 1.0, 0), n=8)
    # a lit window on the north wall
    wbox(kit, "in window", (ix + 0.2, iy + 1.99, 1.1), (ix + 1.4, iy + 2.0, 1.9), M["bushglow"])
    # the table and the phone
    wbox(kit, "table top", (ix + 0.2, iy - 0.9, 0.72), (ix + 1.5, iy - 0.2, 0.77), M["wood"], bevel=0.01)
    for sx in (0.3, 1.4):
        for sy in (-0.85, -0.25):
            wbox(kit, f"table leg{sx}{sy}", (ix + sx - 0.025, iy + sy - 0.025, 0.0), (ix + sx + 0.025, iy + sy + 0.025, 0.72), M["wood"])
    ph = kit.empty("phone", (ix + 0.85, iy - 0.55, 0.77))
    kit.box("phone.body", (0.075, 0.15, 0.012), (0, 0, 0.006), M["dark"], ph, bevel=0.005)
    kit.box("phone.screen", (0.065, 0.14, 0.003), (0, 0, 0.0135), M["screen"], ph)
    ctx["phone"] = ph
    ctx["phone_home"] = tuple(ph.location)
    # the coat hook and the boot mat by the door (west wall = the door side)
    wbox(kit, "hook board", (ix - 2.19, iy - 0.2, 1.5), (ix - 2.15, iy + 0.7, 1.58), M["wood"])
    for k in range(3):
        kit.cyl(f"hook{k}", 0.012, 0.1, (ix - 2.1, iy + k * 0.3 - 0.05, 1.55), M["steam"], rot=(0, math.pi / 2, 0), n=6)
    coat = kit.empty("coat", (ix - 2.08, iy + 0.25, 1.55))
    kit.box("coat.body", (0.14, 0.5, 0.95), (0, 0, -0.5), M["coatgrey"], coat, bevel=0.04)
    kit.box("coat.collar", (0.17, 0.52, 0.1), (0, 0, -0.04), M["dark"], coat, bevel=0.03)
    wbox(kit, "boot mat", (ix - 2.0, iy - 0.2, 0.0), (ix - 1.2, iy + 0.7, 0.02), M["coir"])
    for k, yy in enumerate((0.0, 0.4)):
        wbox(kit, f"boot patch{k}", (ix - 1.8, iy + yy - 0.05, 0.021), (ix - 1.45, iy + yy + 0.2, 0.024), M["floor"])
    for nm, (lx, ly, lz), e in (("in key", (ix, iy - 0.3, 2.1), 90.0), ("in fill", (ix - 1.0, iy + 0.8, 2.0), 40.0)):
        kit.light(nm, "POINT", (lx, ly, lz), e, "#ffd9a8", size=0.3)


# ------------------------------------------------------------------------------------------------ moss


def moss_pad(kit, ctx, M, who, parent, name, loc, size, thr, flowers=0, seed=0):
    ob = kit.sphere(name, 1.0, loc, M["moss"], parent, seg=8)
    ob.scale = size
    ob.hide_render = True
    ctx["moss"].setdefault(who, []).append((ob, thr, tuple(size), loc))
    for k in range(flowers):
        fx = loc[0] + (_hash(seed, k, 1) - 0.5) * size[0] * 1.2
        fy = loc[1] + (_hash(seed, k, 2) - 0.5) * size[1] * 1.2
        fz = loc[2] + size[2] * 0.82
        f = kit.cyl(f"{name}.f{k}", 0.085, 0.045, (fx, fy, fz), M["flower"], parent, n=7)
        f.hide_render = True
        ctx["moss"][who].append((f, thr + 0.03, (1, 1, 1), (fx, fy, fz)))


# zones: (parent part, centre, spread, count, thr0, thr1, size, flowers per pad)
def moss_zones(kit, ctx, M, who, zones, seed):
    n = 0
    for (part, c, sp, cnt, t0, t1, size, fl) in zones:
        parent = bpy.data.objects.get(f"{who}.{part}")
        for k in range(cnt):
            r = [(_hash(seed, n, q) - 0.5) for q in range(4)]
            loc = (c[0] + r[0] * 2 * sp[0], c[1] + r[1] * 2 * sp[1], c[2] + r[2] * 2 * sp[2])
            thr = t0 + (t1 - t0) * (k / max(1, cnt - 1))
            sz = tuple(s * (0.85 + 0.4 * (r[3] + 0.5)) for s in size)
            moss_pad(kit, ctx, M, who, parent, f"{who}.moss{n}", loc, sz, thr, fl, seed + n)
            n += 1


def shoulder(side, cnt=3, t0=0.0, t1=0.5, big=1.0, fl=1):
    return [("torso", (side * 1.45, 0.0, 2.02), (0.35, 0.25, 0.04), cnt, t0, t1, (0.5 * big, 0.45 * big, 0.26 * big), fl),
            ("arm" + str(side), (0.0, 0.0, 0.1), (0.2, 0.2, 0.05), 1, t0, t0, (0.5 * big, 0.5 * big, 0.2 * big), 1)]


def build_moss(kit, ctx, M, cast):
    ctx["moss"] = {}
    hat_pad = lambda t0, t1, cnt, big=1.0: ("headg", (0.0, 0.0, 0.68), (0.3, 0.3, 0.02), cnt, t0, t1, (0.34 * big, 0.34 * big, 0.14 * big), 1)
    spec = {
        "neighbour": shoulder(-1, 3, 0, 0.1) + shoulder(1, 3, 0, 0.1) + [("headg", (0.0, 0.0, 0.62), (0.4, 0.4, 0.02), 4, 0, 0.1, (0.24, 0.24, 0.12), 2)],
        "busman": (shoulder(-1, 3, 0, 0.2, 1.1) + shoulder(1, 3, 0, 0.2, 1.1)
                   + [("torso", (0.0, -0.58, 1.0), (0.8, 0.0, 0.85), 10, 0.0, 0.3, (0.5, 0.3, 0.4), 1),
                      ("torso", (0.0, 0.55, 1.0), (0.8, 0.0, 0.8), 6, 0.0, 0.3, (0.5, 0.3, 0.4), 1),
                      ("leg-1", (0.0, -0.5, -1.0), (0.2, 0.0, 0.6), 4, 0.0, 0.3, (0.5, 0.3, 0.4), 1),
                      ("leg1", (0.0, -0.5, -1.0), (0.2, 0.0, 0.6), 4, 0.0, 0.3, (0.5, 0.3, 0.4), 1),
                      ("arm-1", (0.0, 0.0, -0.8), (0.1, 0.0, 0.6), 4, 0.0, 0.3, (0.55, 0.55, 0.4), 1),
                      ("arm1", (0.0, 0.0, -0.8), (0.1, 0.0, 0.6), 4, 0.0, 0.3, (0.55, 0.55, 0.4), 1),
                      hat_pad(0.0, 0.2, 5)]),
        "parcelman": shoulder(-1, 2, 0, 0.1, 0.8) + shoulder(1, 2, 0, 0.1, 0.8),
        "meeter1": shoulder(-1, 3, 0, 0.1, 1.1) + shoulder(1, 3, 0, 0.1, 1.1) + [hat_pad(0, 0.1, 3), ("arm1", (0, 0, -0.7), (0.1, 0, 0.5), 3, 0, 0.1, (0.5, 0.5, 0.35), 1)],
        "meeter2": shoulder(-1, 3, 0, 0.1, 1.2) + shoulder(1, 3, 0, 0.1, 1.2) + [hat_pad(0, 0.1, 3), ("torso", (0.0, 0.55, 1.0), (0.8, 0.0, 0.7), 5, 0, 0.1, (0.5, 0.3, 0.4), 1)],
        "meeter3": shoulder(-1, 3, 0, 0.1, 1.1) + shoulder(1, 3, 0, 0.1, 1.2) + [hat_pad(0, 0.1, 3), ("arm-1", (0, 0, -0.7), (0.1, 0, 0.5), 3, 0, 0.1, (0.5, 0.5, 0.35), 1)],
        "benchman": (shoulder(-1, 3, 0, 0.1, 1.1) + shoulder(1, 3, 0, 0.1, 1.1)
                     + [("arm-1", (0.0, 0.0, -0.45), (0.1, 0.0, 0.5), 5, 0, 0.1, (0.55, 0.55, 0.4), 1),
                        ("arm1", (0.0, 0.0, -0.45), (0.1, 0.0, 0.5), 5, 0, 0.1, (0.55, 0.55, 0.4), 1)]),
        # Jory: his left shoulder is local +x. Thickest there, first. Then right, head, brows. Above 1.0: head to foot.
        "jory": (shoulder(1, 5, 0.05, 0.62, 1.05, 2)
                 + shoulder(-1, 4, 0.34, 0.88, 0.8, 1)
                 + [("headg", (0.0, 0.0, 0.7), (0.3, 0.3, 0.02), 4, 0.5, 0.9, (0.34, 0.34, 0.14), 2)]
                 + [("torso", (0.0, -0.58, 1.0), (0.8, 0.0, 0.85), 8, 1.0, 1.1, (0.5, 0.3, 0.4), 1),
                    ("torso", (0.0, 0.55, 1.0), (0.8, 0.0, 0.8), 6, 1.0, 1.1, (0.5, 0.3, 0.4), 1),
                    ("leg-1", (0.0, -0.5, -1.0), (0.2, 0.0, 0.7), 5, 1.02, 1.12, (0.5, 0.3, 0.4), 1),
                    ("leg1", (0.0, -0.5, -1.0), (0.2, 0.0, 0.7), 5, 1.02, 1.12, (0.5, 0.3, 0.4), 1),
                    ("arm-1", (0.0, 0.0, -0.8), (0.1, 0.0, 0.6), 4, 1.0, 1.1, (0.55, 0.55, 0.4), 1),
                    ("arm1", (0.0, 0.0, -0.8), (0.1, 0.0, 0.6), 4, 1.0, 1.1, (0.55, 0.55, 0.4), 1),
                    ("headg", (0.0, 0.0, 0.52), (0.4, 0.45, 0.02), 5, 1.03, 1.13, (0.26, 0.26, 0.14), 2)]),
        # me: one small pad on my right shoulder (local -x), a second flower as it thickens
        "me": [("torso", (-1.45, 0.0, 2.02), (0.1, 0.1, 0.0), 1, 0.15, 0.15, (0.5, 0.45, 0.22), 1),
               ("torso", (-1.5, 0.05, 2.0), (0.1, 0.1, 0.0), 1, 0.45, 0.45, (0.42, 0.4, 0.22), 1)],
    }
    for who, zones in spec.items():
        if who in cast:
            moss_zones(kit, ctx, M, who, zones, seed=sum(map(ord, who)))
    # Maggie (cast id jory): a low white bun under the cap, a long plum skirt, and flowers in her hair
    R, H = faces.HEAD_R, faces.HEAD_H
    top = H / 2
    if "jory" in cast:
        hg = bpy.data.objects["jory.headg"]
        white = kit.plastic("#f2f2ee", 0.8, name="white hair")
        for sx in (-1, 1):   # long white locks fall in front of her shoulders so she reads as a woman from the front
            kit.box(f"jory.lock{sx}", (0.34, 0.5, H * 0.95), (sx * (R - 0.02), -0.1, top - H * 0.5), white, hg, bevel=0.1)
        plum = kit.plastic("#6e4f6e", 0.8, name="heather plum")
        kit.box("jory.skirt", (2.12, 1.5, 1.7), (0, 0, 1.2), plum, bpy.data.objects["jory"], bevel=0.1)
        kit.box("jory.skirt2", (2.3, 1.6, 0.2), (0, 0, 0.45), plum, bpy.data.objects["jory"], bevel=0.05)
        for k, (fx, fy, fz) in enumerate([(-0.6, -0.29, 0.13), (-0.52, -0.31, 0.27), (-0.68, -0.22, 0.3),
                                           (0.6, -0.29, 0.13), (0.52, -0.31, 0.27), (0.68, -0.22, 0.3)]):
            f = kit.cyl(f"jory.hairf{k}", 0.12, 0.05, (fx, fy, fz), M["flower"], hg, rot=(math.pi / 2, 0, 0), n=7)
            f.hide_render = True
            ctx["moss"]["jory"].append((f, 0.7 + 0.03 * (k % 3), (1, 1, 1), tuple(f.location)))
            c = kit.cyl(f"jory.hairfc{k}", 0.04, 0.03, (fx, fy - 0.03, fz), kit.plastic("#e8b830", 0.6, name="flower eye"), hg, rot=(math.pi / 2, 0, 0), n=6)
            c.hide_render = True
            ctx["moss"]["jory"].append((c, 0.7 + 0.03 * (k % 3), (1, 1, 1), tuple(c.location)))
    # the narrator: short grey block hair at the back and sides, and a short grey block beard
    if "me" in cast:
        hg = bpy.data.objects["me.headg"]
        grey = kit.plastic("#a9a9ab", 0.85, name="grey hair")
        kit.box("me.hback2", (2 * R + 0.08, 0.3, H * 0.4), (0, R - 0.08, top - H * 0.28), grey, hg, bevel=0.1)
        for sx in (-1, 1):
            kit.box(f"me.hside2{sx}", (0.2, 0.8, 0.45), (sx * (R - 0.02), 0.2, top - 0.3), grey, hg, bevel=0.08)
        kit.box("me.beard", (1.0, 0.3, 0.3), (0, -R + 0.02, -H / 2 + 0.2), grey, hg, bevel=0.1)
        for sx in (-1, 1):
            kit.box(f"me.beardS{sx}", (0.2, 0.7, 0.5), (sx * (R - 0.02), -0.1, -0.25), grey, hg, bevel=0.07)
    if "parcelman" in cast:
        hg = bpy.data.objects["parcelman.headg"]
        kit.cyl("parcel.flower", 0.1, 0.05, (0.0, -0.64, -0.05), M["flower"], hg, rot=(math.pi / 2, 0, 0), n=8)
        kit.cyl("parcel.flower2", 0.04, 0.06, (0.0, -0.67, -0.05), kit.plastic("#e8c040", 0.6, name="pollen"), hg, rot=(math.pi / 2, 0, 0), n=6)
    # the moss flakes and petals for a shower (hidden until a cue)
    ctx["flakes"] = []
    for i in range(52):
        petal = i % 3 == 0
        s = 0.05 if petal else 0.06
        ob = kit.box(f"flake{i}", (s * 1.4, s * 1.1, s * 0.35) if petal else (s, s, s * 0.5), (0, 0, -50), M["petal"] if petal else M["flake"], bevel=0.008)
        ob.hide_render = True
        ctx["flakes"].append(ob)


# ------------------------------------------------------------------------------------------------ the Kneeler

K_THIGH_W, K_THIGH_H = 0.34, 0.74
K_HIP = 0.9
K_TORSO = 0.8
HEAD_SC = 0.42


def kneeler_face():
    from PIL import Image, ImageDraw, ImageFilter

    cream = (214, 202, 172)
    im = Image.new("RGB", (faces.TEX_W, faces.TEX_H), cream)
    d = ImageDraw.Draw(im)
    s = faces.FX1 - faces.FX0
    ink = (6, 5, 5)
    # two small round eyes set close and level, each with a pinprick, and a short straight drawn mouth
    for cxn in (0.5 - 0.085, 0.5 + 0.085):
        cx, cy = faces._fx(cxn), faces._fy(0.42)
        rr = 0.038
        faces._ellipse(d, cx, cy, rr * s, rr * s * 1.35, fill=ink)
        faces._ellipse(d, cx + rr * s * 0.2, cy - rr * s * 0.35, rr * s * 0.2, rr * s * 0.2, fill=(255, 250, 235))
    mx0, mx1, my = faces._fx(0.5 - 0.13), faces._fx(0.5 + 0.13), faces._fy(0.68)
    d.rounded_rectangle([mx0, my - 0.012 * s, mx1, my + 0.012 * s], radius=0.012 * s, fill=ink)
    return im.filter(ImageFilter.SMOOTH)


def build_kneeler(kit, ctx, M):
    cream = _mixed(kit, "kn cream", "#e2d8ba", "#c4b99a", 0.3, 3.0, 0.7)
    lich = _mixed(kit, "kn lichen", "#7d9a5a", "#678550", 0.3, 3.0, 0.7)
    root = kit.empty("kneeler", (KNEEL[0], KNEEL[1], 0.0))
    root.rotation_euler = (0, 0, math.pi)      # forward (-y local) becomes +y, out to the path
    ctx["kn_root"] = root
    tx = K_THIGH_W / 2 + 0.085
    for sx in (-1, 1):
        # the shin lies flat behind the knee, the thigh rises from the knee, the foot at the end of the shin
        kit.box(f"kn.shin{sx}", (0.32, 1.05, 0.22), (sx * tx, 0.45, 0.11), cream, root, bevel=0.05)
        kit.box(f"kn.foot{sx}", (0.3, 0.3, 0.17), (sx * tx, 1.1, 0.085), lich, root, bevel=0.04)
        kit.box(f"kn.thigh{sx}", (K_THIGH_W, 0.42, K_THIGH_H), (sx * tx, 0.0, 0.12 + K_THIGH_H / 2), cream, root, bevel=0.06)
        kit.box(f"kn.thighband{sx}", (K_THIGH_W + 0.012, 0.432, 0.18), (sx * tx, 0.0, 0.48), lich, root, bevel=0.05)
    hip = kit.empty("kn.hip", (0.0, 0.05, K_HIP), root)
    ctx["kn_hip"] = hip
    # the torso: cream belly, a broad lichen band, cream chest, narrow and long
    kit.box("kn.belly", (0.66, 0.36, 0.14), (0, 0, 0.07), cream, hip, bevel=0.05)
    kit.box("kn.band", (0.67, 0.37, 0.36), (0, 0, 0.32), lich, hip, bevel=0.05)
    kit.box("kn.chest", (0.66, 0.36, 0.30), (0, 0, 0.65), cream, hip, bevel=0.07)
    kit.box("kn.shoulders", (1.04, 0.3, 0.14), (0, 0, 0.72), cream, hip, bevel=0.06)
    ctx["kn_arms"] = []
    for sx in (-1, 1):
        sh = kit.empty(f"kn.sh{sx}", (sx * 0.5, 0.0, 0.72), hip)
        kit.box(f"kn.arm_u{sx}", (0.17, 0.22, 0.4), (0, 0, -0.14), cream, sh, bevel=0.045)
        kit.box(f"kn.arm_b{sx}", (0.175, 0.225, 0.34), (0, 0, -0.51), lich, sh, bevel=0.045)
        kit.box(f"kn.arm_l{sx}", (0.17, 0.22, 0.34), (0, 0, -0.85), cream, sh, bevel=0.045)
        kit.box(f"kn.hand{sx}", (0.19, 0.26, 0.2), (0, -0.01, -1.08), cream, sh, bevel=0.05)
        ctx["kn_arms"].append((sh, sx))
    neck = kit.empty("kn.neck", (0.0, 0.0, K_TORSO), hip)
    kit.box("kn.neckm", (0.14, 0.14, 0.12), (0, 0, 0.0), cream, neck, bevel=0.03)
    ctx["kn_neck"] = neck
    head = kit.empty("kn.head", (0, 0, 0.06 + 0.25), neck)
    hs = kit.empty("kn.heads", (0, 0, 0), head)
    hs.scale = (HEAD_SC, HEAD_SC, HEAD_SC * 1.3)
    hm, tex = rig.head_material("kneeler", "#e2d6b8")
    hm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
    pil = kneeler_face()
    img = bpy.data.images.new("kneeler face", pil.width, pil.height)
    a = np.asarray(pil.convert("RGBA")).astype(np.float32)[::-1] / 255
    img.pixels.foreach_set(a.ravel())
    img.pack()
    img.colorspace_settings.name = "sRGB"
    tex.image = img
    nt = hm.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    sep = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(tex.outputs["Color"], sep.inputs["Color"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.9
    ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp.color_ramp.elements[1].position = 0.97
    ramp.color_ramp.elements[1].color = (1.0, 0.82, 0.55, 1)
    nt.links.new(sep.outputs["Val"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 3.0
    rig.head_mesh("kn.headm", hm, hs)
    ctx["kn_head"] = head
    head.rotation_euler = (math.radians(-6), math.radians(11), 0)
    ctx["kn_parts"] = [root] + list(root.children_recursive)


def place_kneeler(kit, tl, t, ctx):
    cs = _cues(tl, "kneeler")
    show = False
    for c in cs:
        if c["t"] <= t + 1e-9 and "show" in c:
            show = c["show"]
    for ob in ctx["kn_parts"]:
        ob.hide_render = not show
    if not show:
        return
    lean = _ramped(cs, t, "lean", 0.0)
    pitch = _ramped(cs, t, "pitch", 0.0)
    yaw = _ramped(cs, t, "yaw", 0.0)
    ctx["kn_hip"].rotation_euler = (math.radians(lean), 0, 0)
    for sh, sx in ctx["kn_arms"]:
        sh.rotation_euler = (math.radians(-lean * 0.85), 0, 0)
    ctx["kn_neck"].rotation_euler = (math.radians(-lean * 0.95 + pitch), 0, math.radians(yaw))


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    ctx = {"story": story}
    M = materials(kit)
    ctx["M"] = M
    build_ground(kit, ctx, M)
    build_park(kit, ctx, M)
    build_town(kit, ctx, M)
    build_interior(kit, ctx, M)
    build_kneeler(kit, ctx, M)
    # hollows' water discs
    ctx["water"] = {}
    for which, hs in HOLLOWS.items():
        ctx["water"][which] = []
        for k, (x, y, rx, ry, dp) in enumerate(hs[:2]):
            w = kit.cyl(f"water.{which}{k}", rx * 0.8, 0.01, (x, y, -dp * 0.6), M["water"], n=18)
            w.hide_render = True
            ctx["water"][which].append(w)
    # gulls in the air
    ctx["gulls"] = [gull(kit, M, f"gull{i}", (0, 0, -50), 1.4) for i in range(4)]
    # lights: the sun (animated by the env cue), a sky fill, the Kneeler's key and rim
    kit.light("sun", "SUN", (0, 0, 40), 4.0, "#fff1da", rot=(math.radians(50), 0, math.radians(200)), size=0.02)
    kit.light("kkey", "SPOT", (0, 0, 4), 0.0, "#ffbf80", size=0.35, spot=62, blend=0.7)
    kit.light("krim", "SPOT", (0, 0, 4), 0.0, "#9fb8d8", size=0.3, spot=70, blend=0.6)
    kit.light("kfill", "AREA", (0, 0, 4), 0.0, "#d8e0f0", size=3.0)
    kit.light("face", "AREA", (0, 0, 4), 0.0, "#fff0e0", size=1.4)
    ctx["story_cast"] = story.get("cast", {})
    return ctx


def after_cast(kit, story, ctx):
    pass


def _fog_nodes(ctx):
    if "fog_nodes" not in ctx:
        from blocky import kit as _k
        d = _k.FOG["density"]
        ctx["fog_d"] = d
        ctx["fog_nodes"] = [nd for m in bpy.data.materials if m.node_tree for nd in m.node_tree.nodes
                            if nd.type == "MATH" and nd.operation == "MULTIPLY" and d > 0
                            and abs(nd.inputs[1].default_value + d) < 1e-6]
        fc = tuple(_k.FOG["color"])
        ctx["fog_cols"] = [nd for m in bpy.data.materials if m.node_tree for nd in m.node_tree.nodes
                           if nd.type == "EMISSION" and all(abs(a - b) < 1e-6 for a, b in zip(nd.inputs["Color"].default_value[:3], fc))]
    return ctx["fog_nodes"]


def _yard_z(ctx, amt):
    """The yard's heights for the current hollow amounts (a dict which -> 0..1.2)."""
    X, Y = ctx["yard_xy"]
    z = np.zeros_like(X)
    for which, hs in HOLLOWS.items():
        a = amt.get(which, 0.0)
        if a <= 0.001:
            continue
        for (x, y, rx, ry, dp) in hs:
            r2 = ((X - x) / rx) ** 2 + ((Y - y) / ry) ** 2
            prof = np.where(r2 < 1.0, (1.0 - r2) ** 1.5, 0.0)
            z -= dp * a * prof
    return z


def animate(kit, story, tl, t, ctx):
    from blocky import kit as K

    over = {}
    if "moss" not in ctx:
        build_moss(kit, ctx, ctx["M"], story.get("cast", {}))
        K.LIGHTS["sun"]["light"].angle = math.radians(3.0)
    # ---- the light, the sky and the fog
    cs = _cues(tl, "env")
    P = _ramped([dict(c, v=_pvec(c["set"])) for c in cs], t, "v", _pvec("day"), mix=_vec_mix) if cs else _pvec("day")
    sun_e, sc_r, sc_g, sc_b, elev, az, wr, wg, wb, ws, fr, fg, fb, fm, win = P
    sun = K.LIGHTS["sun"]
    sun["base"] = sun_e
    sun["light"].color = (K.srgb(sc_r), K.srgb(sc_g), K.srgb(sc_b))
    sun["obj"].rotation_euler = (math.radians(90 - elev), 0, math.radians(az))
    w = bpy.context.scene.world.node_tree.nodes["Background"]
    w.inputs["Color"].default_value = (K.srgb(wr), K.srgb(wg), K.srgb(wb), 1)
    w.inputs["Strength"].default_value = ws
    nodes = _fog_nodes(ctx)
    for nd in nodes:
        nd.inputs[1].default_value = -ctx["fog_d"] * fm
    fcol = (K.srgb(fr), K.srgb(fg), K.srgb(fb), 1)
    for nd in ctx["fog_cols"]:
        nd.inputs["Color"].default_value = fcol
    # ---- lamp, kitchen window
    lamp = _ramped(_cues(tl, "lamp"), t, "v", 1.0)
    over["lamp"] = lamp
    ctx["M"]["lampglass"].node_tree.nodes["Emission"].inputs["Strength"].default_value = 9.0 * lamp
    wl = _ramped(_cues(tl, "window"), t, "v", 1.0)
    K.LIGHTS["window"]["base"] = 60.0 * (0.2 + 0.8 * min(1.0, win * 1.6))
    over["window"] = 0.5 + 0.5 * wl
    ctx["M"]["bushglow"].node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.4 + 2.2 * min(1.0, win * 1.5)
    # ---- the shot's own light (the Kneeler's key and rim, a face light), from "shot" cues
    shot_look(kit, tl, t, ctx, over)
    # ---- the yard's hollows
    amt = {}
    for which in HOLLOWS:
        amt[which] = _ramped([c for c in _cues(tl, "hollows") if c.get("which") == which], t, "v", 0.0)
    key = tuple(round(v, 3) for v in amt.values())
    if ctx.get("yard_key") != key:
        ctx["yard_key"] = key
        z = _yard_z(ctx, amt)
        X, Y = ctx["yard_xy"]
        co = np.stack([X, Y, z], axis=1).astype(np.float32)
        ctx["yard"].data.vertices.foreach_set("co", co.ravel())
        ctx["yard"].data.update()
    for which, ws_ in ctx["water"].items():
        wv = _ramped([c for c in _cues(tl, "water") if c.get("which") == which], t, "v", 0.0)
        for ob, (x, y, rx, ry, dp) in zip(ws_, HOLLOWS[which][:2]):
            ob.hide_render = True   # the dents stay plain grass (the dark discs read as lumps)
            ob.location = (x, y, -dp * amt[which] * (1.0 - 0.55 * wv) + 0.004)
            ob.scale = (1, 1, 1)
    # ---- things
    mat = ctx["van"]["mat"]
    mv = _ramped(_cues(tl, "mat"), t, "v", 0.0)
    mx, my = ctx["van"]["mat0"]
    mat.location = (mv * 0.7, mv * 0.1, 0.0)
    capv = _ramped(_cues(tl, "cap"), t, "v", 0.0)
    for ob in ctx["cap"]:
        ob.hide_render = capv < 0.5
    sm = _ramped(_cues(tl, "seatmoss"), t, "v", 0.0)
    for ob in ctx["seatmoss"]:
        ob.hide_render = sm < 0.5
    ph = ctx["phone"]
    pv = _ramped(_cues(tl, "phone"), t, "v", 0.0)
    ph.location = (ctx["phone_home"][0] + pv * 0.004 * math.sin(t * 90), ctx["phone_home"][1] + pv * 0.003 * math.sin(t * 83 + 1), ctx["phone_home"][2])
    tr = _ramped(_cues(tl, "train"), t, "v", 1.0)
    for ob in ctx["train_obs"]:
        ob.hide_render = tr < 0.5
    sg = _ramped(_cues(tl, "sitgull"), t, "v", 0.0)
    ctx["sitgull"].hide_render = sg < 0.5
    for ob in ctx["sitgull"].children_recursive:
        ob.hide_render = sg < 0.5
    # gulls drifting past
    gc = _cues(tl, "gulls")
    gv = _ramped(gc, t, "v", 0.0)
    last = [c for c in gc if c["t"] <= t and c.get("v", 0) >= 0.5]
    for i, g in enumerate(ctx["gulls"]):
        on = gv >= 0.5 and last
        g.hide_render = not on
        for ob in g.children_recursive:
            ob.hide_render = not on
        if on:
            c = last[-1]
            u = t - c["t"]
            sp = 1.2 + 0.18 * i
            g.location = (c["x0"] + c["dx"] * u * sp + 0.9 * i, c["y0"] + c["dy"] * u * sp + 0.6 * i, c["z0"] + 0.25 * math.sin(u * 1.3 + i) + 0.5 * i)
            g.rotation_euler = (0, 0, math.atan2(c["dy"], c["dx"]))
            fl = math.sin(u * 5.5 + i * 1.7) * 0.5
            for pivn in g["wings"]:
                p = bpy.data.objects[pivn]
                p.rotation_euler = (fl * (-1 if p.name.endswith("-1") else 1), 0, 0)
    # ---- the people
    for who, keys in tl["acting"].items():
        for sx_ in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx_}")
            if leg is not None and AC._switch(keys, "sit", t, False):
                leg.rotation_euler = (-math.pi / 2, 0, 0)
    # ---- moss
    for who, pads in ctx["moss"].items():
        lv = _ramped(_cues(tl, "moss", who), t, "v", 0.0)
        gone = bpy.data.objects[who].hide_render
        for ob, thr, size, loc in pads:
            if lv > thr and not gone:
                grow = 0.45 + 0.55 * _ss((lv - thr) / 0.18)
                ob.hide_render = False
                if size != (1, 1, 1):
                    ob.scale = tuple(s * grow for s in size)
            else:
                ob.hide_render = True
    # ---- showers
    showers = _cues(tl, "shower")
    sh = [c for c in showers if 0 <= t - c["t"] < 1.2]
    for ob in ctx["flakes"]:
        ob.hide_render = True
    if sh:
        c = sh[-1]
        u = t - c["t"]
        s0 = AC.state(tl, c["who"], c["t"])
        chk = c.get("h", 1.5)
        for i, ob in enumerate(ctx["flakes"]):
            a = _hash(i, 3) * 6.28
            rr = 0.2 + _hash(i, 4) * 0.5
            x0 = s0["x"] + math.cos(a) * rr * 0.6
            y0 = s0["y"] + math.sin(a) * rr * 0.6
            z0 = s0["z"] + chk - _hash(i, 5) * chk * 0.8
            vx, vy = math.cos(a) * (0.3 + _hash(i, 6) * 0.9), math.sin(a) * (0.3 + _hash(i, 6) * 0.9)
            vz = 0.9 + _hash(i, 7) * 1.4 - (0.5 if z0 < 1.0 else 0.0)
            g = 2.6
            x, y = x0 + vx * u, y0 + vy * u
            z = z0 + vz * u - 0.5 * g * u * u * (1 + 0.5 * _hash(i, 8))
            fl = max(z, s0["z"] + 0.02)
            ob.location = (x, y, fl)
            ob.rotation_euler = (u * (3 + 5 * _hash(i, 9)), u * (2 + 4 * _hash(i, 10)), u * 4)
            ob.hide_render = u > 1.0
            k = 1.0 - _ss((u - 0.6) / 0.4)
            ob.scale = (k, k, k)
    place_kneeler(kit, tl, t, ctx)
    return over


def shot_look(kit, tl, t, ctx, over):
    """A shot's own light from a "shot" cue's `look`: {"kkey": [pos, aim, watts, cone, colour], "krim": [...],
    "kfill": [pos, aim, watts], "face": [pos, aim, watts]}; on from that cue, off with {"look": null}."""
    from blocky import kit as K

    look = None
    for c in _cues(tl, "shot"):
        if c["t"] <= t + 1e-9:
            look = c.get("look")
    for nm in ("kkey", "krim", "kfill", "face"):
        over[nm] = 0.0
    if not look:
        return
    for nm in ("kkey", "krim", "kfill", "face"):
        if nm not in look:
            continue
        spec = look[nm]
        pos, aim, watts = spec[:3]
        ob = K.LIGHTS[nm]["obj"]
        ob.location = pos
        ob.rotation_euler = (V(aim) - V(pos)).to_track_quat("-Z", "Y").to_euler()
        K.LIGHTS[nm]["base"] = watts
        if len(spec) > 3 and K.LIGHTS[nm]["light"].type == "SPOT":
            K.LIGHTS[nm]["light"].spot_size = math.radians(spec[3])
        if len(spec) > 4:
            K.LIGHTS[nm]["light"].color = K.col(spec[4])[:3]
        over[nm] = 1.0
