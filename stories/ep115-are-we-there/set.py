"""ep115 "are we there": Mom's teal minivan on a bright winter mountain road.

Rule meter: a cream tag near the top-left of every frame (a white mile post with a black 1, a loop arrow, and the lap
count in two big digits). It is a child of the camera. Cues (story.json) drive:
  look   (day / squall)             the light and the sky
  lap    (n)                        the two digits
  speed  (v)                        how fast the road scrolls past the windows (m/s), eased over dur
  mv     (obj, x, y, z, yaw, dur)   move anything named: the post, the cabin, the waterfall, the hatch
  sit    (who, on)                  a character sits (legs turned forward)
  tagbig (s, x, y)                  a bigger tag at the top centre for a close look at the count
  flakes (v)                        snow flakes in front of the lens (0 or 1)
The van is at the origin (layout.py), the landmarks stand on stages far to the east.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {"obj": {}, "init": {}, "scroll": []}
PERIOD = 24.0


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def _L(**kw):
    base = dict(sun=3.4, sun_col="#fff4e2", el=52.0, az=200.0, fill=1.1, fill_col="#e8f2ff", sky="#7cc6ff",
                sky_str=1.0)
    base.update(kw)
    return base


LOOKS = {
    "day": _L(),
    "squall": _L(sun=1.2, sun_col="#e4ecf4", el=60.0, fill=1.7, fill_col="#f2f6fa", sky="#c9d3dc", sky_str=1.25),
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


def sample(name, tl, t, defaults):
    cur, prev = dict(defaults), dict(defaults)
    for c in tl["cues"]:
        if c["name"] != name:
            continue
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


# ------------------------------------------------------------------------------------------------ scenery
SNOW = "#f4f8fb"


def pine(kit, x, y, h=6.0, parent=None, tint="#f4fbff"):
    try:
        return kit.prop("pinetree_snow_1", (x, y, G.ROAD_Z), height=h, tint=tint, parent=parent)
    except Exception:
        P = kit.plastic
        root = kit.empty("pinefb", (x, y, G.ROAD_Z), parent)
        kit.cyl("pinefb.t", 0.25, h * 0.4, (0, 0, h * 0.2), P("#6a4a2a", 0.8), root, n=8)
        kit.cyl("pinefb.c", h * 0.28, h * 0.8, (0, 0, h * 0.62), P("#2f7a4f", 0.8), root, n=8, r2=0.1)
        return root


def hill(kit, name, x, y, r, sy, col, sz=0.45, z0=0.0):
    ob = kit.sphere(name, r, (x, y, z0), kit.plastic(col, 0.9, spec=0.02), seg=14)
    ob.scale = (1.0, sy, sz)
    noshadow(ob)
    return ob


def backdrop(kit, x0, y0, n=9, span=40.0, tall=7.0):
    """A snowy treeline and soft white hills behind a stage."""
    for i in range(n):
        x = x0 - span / 2 + i * span / (n - 1) + (i % 3) * 0.7
        pine(kit, x, y0 + (i % 2) * 3.0, tall + (i % 4) * 0.8)
    hill(kit, f"bd{x0}.a", x0 - 20, y0 + 40, 30, 1.0, "#e7f1f9")
    hill(kit, f"bd{x0}.b", x0 + 25, y0 + 55, 36, 1.0, "#dbe8f3")


def falls_rock(kit, name, loc, yaw=0.0, w=14.0, h=9.0):
    """The frozen waterfall: a dark grey rock face with a snow cap, a sheet of ice-blue ice and uneven drips of ice
    hanging down it. Its viewing side is local -y."""
    P = kit.plastic
    root = kit.empty(name, loc)
    root.rotation_euler = (0, 0, yaw)
    rock = P("#5f6d80", 0.9, spec=0.05)
    rock2 = P("#4c5a6d", 0.9, spec=0.05)
    rock3 = P("#7a8798", 0.9, spec=0.05)
    kit.box(f"{name}.wall", (w, 3.0, h), (0, 0, h / 2 + G.ROAD_Z), rock, root)
    for i, (dx, dz, ww, hh) in enumerate([(-4.8, 3.0, 3.6, 1.0), (4.2, 5.4, 4.2, 1.2), (-5.5, 6.6, 2.6, 1.3),
                                          (5.8, 2.0, 2.4, 1.4), (-3.0, 1.0, 2.2, 0.8)]):
        kit.box(f"{name}.ledge{i}", (ww, 0.7, hh), (dx, -1.75, dz + G.ROAD_Z), rock2 if i % 2 else rock3, root, bevel=0.1)
    kit.box(f"{name}.cap", (w + 0.4, 3.2, 0.9), (0, 0, h + G.ROAD_Z + 0.2), P(SNOW, 0.9, spec=0.05), root, bevel=0.2)
    ice = [P("#7cc8ee", 0.2, spec=0.9), P("#9ad9f6", 0.2, spec=0.9), P("#b6e6fb", 0.25, spec=0.8)]
    # a sheet of blue ice down the middle, then drips of every length
    top = h + G.ROAD_Z
    kit.box(f"{name}.sheet", (2.6, 0.35, 4.6), (1.0, -1.65, top - 2.3), ice[1], root, bevel=0.12)
    drips = [(-3.6, 0.5, 2.4), (-2.6, 0.4, 3.6), (-1.7, 0.6, 1.8), (-0.5, 0.45, 3.1), (2.6, 0.7, 6.0), (3.4, 0.4, 3.0),
             (4.2, 0.5, 4.1), (5.0, 0.35, 2.0)]
    for i, (dx, ww, ln) in enumerate(drips):
        m = ice[i % 3]
        kit.box(f"{name}.ice{i}", (ww, 0.55, ln), (dx, -1.95, top - ln / 2), m, root, bevel=0.14)
        kit.box(f"{name}.tip{i}", (ww * 0.55, 0.5, ln * 0.18), (dx, -1.95, top - ln - ln * 0.07), m, root, bevel=0.1)
    s = kit.sphere(f"{name}.pool", 2.6, (0.4, -2.4, G.ROAD_Z + 0.1), ice[2], root, seg=12)
    s.scale = (1.5, 0.8, 0.3)
    return root


def cabin(kit, name, loc):
    """The little log cabin: brown logs, a snowy roof, a chimney with smoke, a blank sign. Front is -y."""
    P = kit.plastic
    root = kit.empty(name, loc)
    log = P("#b07a48", 0.85, spec=0.05)
    log2 = P("#9a6636", 0.85, spec=0.05)
    kit.box(f"{name}.body", (6.2, 4.6, 3.0), (0, 0, 1.5), log, root)
    for i in range(6):
        kit.cyl(f"{name}.log{i}", 0.2, 6.5, (0, -2.35, 0.3 + i * 0.5), log2 if i % 2 else log, root, rot=(0, math.pi / 2, 0), n=10)
    snow = P(SNOW, 0.9, spec=0.05)
    for sx in (-1, 1):
        kit.box(f"{name}.roof{sx}", (3.9, 5.2, 0.35), (sx * 1.7, 0, 3.55), P("#5a3a26", 0.8), root, rot=(0, sx * 0.45, 0))
        kit.box(f"{name}.rsnow{sx}", (3.9, 5.3, 0.3), (sx * 1.7, 0, 3.8), snow, root, rot=(0, sx * 0.45, 0), bevel=0.1)
    kit.box(f"{name}.chim", (0.7, 0.7, 1.8), (1.9, 0.5, 4.3), P("#7a6a5e", 0.9), root)
    kit.box(f"{name}.door", (1.2, 0.14, 2.2), (-0.8, -2.34, 1.1), P("#5a3a22", 0.7), root)
    kit.box(f"{name}.win", (1.2, 0.12, 1.0), (1.6, -2.34, 1.7), kit.emit("#ffd98a", 1.6), root)
    kit.box(f"{name}.winf", (1.5, 0.1, 1.3), (1.6, -2.32, 1.7), P("#fff8e8", 0.7), root)
    kit.box(f"{name}.step", (2.0, 0.9, 0.2), (-0.8, -2.8, 0.1), snow, root)
    kit.box(f"{name}.post", (0.15, 0.15, 1.6), (-4.0, -3.4, 0.8), log2, root)
    kit.box(f"{name}.sign", (1.5, 0.1, 0.8), (-4.0, -3.45, 1.5), P("#c89a62", 0.8), root)
    W["smoke"] = []
    for i in range(5):
        sp = kit.sphere(f"{name}.smoke{i}", 0.35, (1.9, 0.5, 5.4), P("#ffffff", 0.9, spec=0.0), root, seg=8)
        noshadow(sp)
        W["smoke"].append(sp)
    return root


def truck_cab(kit, name, x0, body, trim, blade=False):
    """A tall blocky cab with an open windshield, facing -y. The driver stands inside on a floor at z = 0.95 so his
    head (centre 2.52) shows in the window (z 1.9 to 3.15)."""
    P = kit.plastic
    b = P(body, 0.4, spec=0.5)
    t = P(trim, 0.5, spec=0.3)
    dk = P("#2a2d33", 0.7)
    fl = P("#4a4f58", 0.8)
    kit.box(f"{name}.floor", (2.5, 2.3, 0.2), (x0, 0.35, 0.85), fl)
    kit.box(f"{name}.back", (2.6, 0.15, 2.5), (x0, 1.45, 2.05), b)
    for sx in (-1, 1):
        kit.box(f"{name}.side{sx}", (0.15, 2.3, 2.5), (x0 + sx * 1.3, 0.35, 2.05), b)
        kit.box(f"{name}.pill{sx}", (0.35, 0.18, 1.45), (x0 + sx * 1.12, -0.8, 2.52), b)
    kit.box(f"{name}.roof", (2.8, 2.5, 0.18), (x0, 0.3, 3.35), b, bevel=0.05)
    kit.box(f"{name}.rooftrim", (2.84, 0.2, 0.1), (x0, -0.95, 3.2), t)
    kit.box(f"{name}.cowl", (2.6, 0.2, 1.1), (x0, -0.8, 1.45), b)
    kit.box(f"{name}.dash", (2.2, 0.55, 0.12), (x0, -0.55, 1.95), dk)
    kit.box(f"{name}.hood", (2.4, 1.7, 0.95), (x0, -1.75, 1.1), b, bevel=0.07)
    kit.box(f"{name}.grille", (1.7, 0.12, 0.6), (x0, -2.62, 1.0), dk)
    kit.box(f"{name}.bumper", (2.7, 0.35, 0.3), (x0, -2.7, 0.55), t, bevel=0.05)
    for sx in (-1, 1):
        kit.box(f"{name}.lamp{sx}", (0.4, 0.1, 0.3), (x0 + sx * 0.95, -2.65, 1.3), kit.emit("#fff2c8", 2.0))
        for sy in (-1.5, 0.7):
            kit.cyl(f"{name}.wh{sx}{sy}", 0.62, 0.45, (x0 + sx * 1.3, sy, 0.62), dk, rot=(0, math.pi / 2, 0), n=16)
    if blade:
        kit.box(f"{name}.blade", (3.5, 0.4, 1.15), (x0, -3.4, 0.85), P("#ffb42a", 0.4, spec=0.5), rot=(0, 0, 0.18), bevel=0.06)
        for sx in (-1, 1):
            kit.box(f"{name}.arm{sx}", (0.18, 1.0, 0.2), (x0 + sx * 0.8, -3.0, 0.75), dk)
        kit.sphere(f"{name}.beacon", 0.22, (x0, 0.2, 3.62), kit.emit("#ffb02a", 2.2), seg=8)
    else:
        for sx in (-1, 1):
            kit.cyl(f"{name}.stack{sx}", 0.1, 2.0, (x0 + sx * 1.5, 1.2, 2.4), P("#c8ccd2", 0.3, spec=0.8), n=10)
        kit.box(f"{name}.stripe", (2.42, 0.1, 0.2), (x0, -2.1, 1.35), t)


def silver_car(kit, x0):
    P = kit.plastic
    b = P("#c9d1da", 0.3, spec=0.7)
    dk = P("#2a2d33", 0.7)
    kit.box("sc.floor", (2.0, 2.4, 0.1), (x0, 0.3, 0.1), P("#4a4f58", 0.8))
    kit.box("sc.body", (2.0, 4.6, 0.7), (x0, -0.2, 0.45), b, bevel=0.08)
    kit.box("sc.hood", (1.9, 1.7, 0.4), (x0, -1.95, 0.9), b, bevel=0.08)
    kit.box("sc.dash", (1.8, 0.5, 0.35), (x0, -0.55, 0.95), P("#8b929c", 0.8))
    kit.box("sc.back", (1.9, 0.12, 1.5), (x0, 1.55, 1.5), b)
    for sx in (-1, 1):
        kit.box(f"sc.side{sx}", (0.12, 2.4, 0.9), (x0 + sx * 1.0, 0.35, 1.2), b)
        kit.box(f"sc.pill{sx}", (0.22, 0.16, 1.2), (x0 + sx * 0.92, -0.9, 1.6), b, rot=(0.0, 0, 0))
        kit.box(f"sc.seat{sx}", (0.75, 0.7, 0.18), (x0 + sx * 0.55, 0.45, 0.4), P("#2f3540", 0.8))
        kit.box(f"sc.sb{sx}", (0.75, 0.14, 0.9), (x0 + sx * 0.55, 0.9, 0.85), P("#2f3540", 0.8))
        kit.cyl(f"sc.wh{sx}", 0.4, 0.3, (x0 + sx * 1.0, -1.8, 0.4), dk, rot=(0, math.pi / 2, 0), n=14)
        kit.box(f"sc.lamp{sx}", (0.4, 0.08, 0.2), (x0 + sx * 0.7, -2.82, 0.9), kit.emit("#fff2c8", 2.0))
    kit.box("sc.roof", (2.1, 2.5, 0.14), (x0, 0.35, 2.3), b, bevel=0.05)
    kit.box("sc.bumper", (2.0, 0.2, 0.2), (x0, -2.85, 0.45), dk)


def cabin_door_stage(kit, x0):
    P = kit.plastic
    log = P("#8a5a36", 0.85, spec=0.05)
    log2 = P("#7a4c2c", 0.85, spec=0.05)
    kit.box("dr.wall", (7.0, 0.5, 3.4), (x0, 3.0, 1.7), log)
    for i in range(7):
        kit.cyl(f"dr.log{i}", 0.22, 7.2, (x0, 2.7, 0.3 + i * 0.5), log2 if i % 2 else log, rot=(0, math.pi / 2, 0), n=10)
    kit.box("dr.door", (1.4, 0.14, 2.4), (x0, 2.65, 1.3), P("#5a3a22", 0.7))
    kit.box("dr.doorf", (1.7, 0.1, 2.7), (x0, 2.68, 1.4), P("#fff8e8", 0.7))
    kit.box("dr.knob", (0.14, 0.14, 0.14), (x0 + 0.5, 2.55, 1.2), P("#d8c070", 0.3, spec=0.8))
    kit.box("dr.porch", (7.0, 3.6, 0.6), (x0, 1.0, -0.15), P("#b98a5a", 0.8))
    kit.box("dr.snow", (7.0, 1.4, 0.6), (x0, -1.0, -0.15), P(SNOW, 0.9, spec=0.05), bevel=0.06)
    kit.box("dr.win", (1.3, 0.1, 1.1), (x0 - 2.4, 2.6, 1.8), kit.emit("#ffd98a", 1.6))
    kit.box("dr.winf", (1.6, 0.08, 1.4), (x0 - 2.4, 2.64, 1.8), P("#fff8e8", 0.7))
    kit.box("dr.roof", (7.4, 2.4, 0.3), (x0, 2.0, 3.6), P("#5a3a26", 0.8))
    kit.box("dr.rsnow", (7.4, 2.5, 0.3), (x0, 2.0, 3.85), P(SNOW, 0.9, spec=0.05), bevel=0.1)
    for sx in (-1, 1):
        kit.box(f"dr.post{sx}", (0.25, 0.25, 3.4), (x0 + sx * 3.4, -0.1, 1.7), log2)
    box = kit.empty("pizzabox", (x0, 0.75, 1.1))
    kit.box("pizza.b", (0.56, 0.56, 0.07), (0, 0, 0), P("#f1e2c0", 0.7), box, bevel=0.01)
    kit.box("pizza.lid", (0.56, 0.56, 0.02), (0, 0, 0.04), P("#e8d4a8", 0.7), box)
    kit.box("pizza.stripe", (0.3, 0.3, 0.01), (0, 0, 0.055), P("#e8493a", 0.6), box)


def packet(kit, name, loc, col, parent, flat=False, rot=0.0, sz=1.0):
    """A pillow snack packet with crimped ends and no writing. Upright it faces +y (the hatch camera); flat it faces up."""
    P = kit.plastic
    root = kit.empty(name, loc, parent)
    root.rotation_euler = (math.pi / 2, 0, rot) if flat else (0, rot * 3.0, 0)
    k = sz
    body = P(col, 0.45, spec=0.35)
    crimp = P("#fff6e0", 0.5, spec=0.2)
    kit.box(f"{name}.b", (0.34 * k, 0.1 * k, 0.24 * k), (0, 0, 0), body, root, bevel=0.035 * k)
    for sx in (-1, 1):
        kit.box(f"{name}.c{sx}", (0.07 * k, 0.045 * k, 0.28 * k), (sx * 0.19 * k, 0, 0), crimp, root)
    kit.box(f"{name}.s", (0.2 * k, 0.104 * k, 0.04 * k), (0, 0, 0.0), crimp, root)
    return root


# ---------------------------------------------------------------------------------------------- the van
def van(kit):
    P = kit.plastic
    teal = P("#2fb7a8", 0.4, spec=0.5)
    cream = P("#f1e8d6", 0.85, spec=0.05)
    tan = P("#d8c39a", 0.85, spec=0.05)
    dark = P("#2a2d33", 0.7)
    dash = P("#b9c4cd", 0.7)
    chrome = kit.metal("#d4d8de", 0.25)
    y0, y1 = -1.6, 2.7
    yc, ln = (y0 + y1) / 2, y1 - y0
    kit.box("vfloor", (2.6, ln, 0.12), (0, yc, -0.06), P("#cfc6b4", 0.9, spec=0.05))
    kit.box("vunder", (2.4, ln, 0.3), (0, yc, -0.27), dark)
    for sx in (-1, 1):
        kit.box(f"vwall_in{sx}", (0.08, ln, 1.2), (sx * 1.2, yc, 0.3), cream)
        kit.box(f"vwall_out{sx}", (0.08, ln, 1.2), (sx * 1.285, yc, 0.3), teal)
        kit.box(f"vsill{sx}", (0.2, ln, 0.1), (sx * 1.24, yc, 0.95), teal, bevel=0.03)
        for k, py in enumerate((-1.52, 0.9, 2.64)):
            kit.box(f"vpil{sx}{k}", (0.2, 0.16, 1.2), (sx * 1.24, py, 1.55), teal)
        kit.box(f"vrail{sx}", (0.2, ln, 0.14), (sx * 1.24, yc, 2.1), teal)
        for sy in (-0.85, 1.6):
            kit.cyl(f"vwh{sx}{sy}", 0.38, 0.28, (sx * 1.2, sy, -0.07), dark, rot=(0, math.pi / 2, 0), n=18)
            kit.cyl(f"vhub{sx}{sy}", 0.17, 0.3, (sx * 1.21, sy, -0.07), kit.metal("#b4bac2", 0.3), rot=(0, math.pi / 2, 0), n=12)
        kit.box(f"vlamp{sx}", (0.42, 0.1, 0.22), (sx * 0.8, -2.97, 0.3), kit.emit("#fff6d8", 2.6))
    kit.box("vceil", (2.5, ln, 0.1), (0, yc, 2.12), cream)
    kit.box("vroof", (2.62, ln, 0.1), (0, yc, 2.23), teal, bevel=0.04)
    # the cowl, the hood and the dash
    kit.box("vdash", (2.4, 0.55, 0.5), (0, -1.25, 0.72), dash, bevel=0.05)
    kit.box("vhood", (2.5, 1.4, 0.5), (0, -2.15, 0.1), teal, bevel=0.06)
    kit.box("vgrille", (1.9, 0.1, 0.36), (0, -2.86, 0.08), dark)
    kit.box("vbump", (2.55, 0.3, 0.2), (0, -2.9, -0.2), P("#e8ecf0", 0.5, spec=0.4), bevel=0.05)
    # seats
    for sx, sy, wd in ((G.MOM[0], G.MOM[1], 0.8),):
        kit.box("seatM", (wd, 0.72, 0.5), (sx, sy, 0.25), tan, bevel=0.05)
        kit.box("seatMb", (wd, 0.14, 0.75), (sx, sy + 0.4, 0.88), tan, bevel=0.05)
        kit.box("seatMh", (0.4, 0.12, 0.28), (sx, sy + 0.4, 1.4), tan, bevel=0.04)
    kit.box("bench", (2.3, 0.72, 0.5), (0, G.JO[1] + 0.0, 0.25), tan, bevel=0.05)
    kit.box("benchb", (2.3, 0.14, 0.75), (0, G.JO[1] + 0.4, 0.88), tan, bevel=0.05)
    for x_ in (G.ME[0], G.JO[0]):
        kit.box(f"benchh{x_}", (0.4, 0.12, 0.28), (x_, G.JO[1] + 0.4, 1.4), tan, bevel=0.04)
    # the cooler between the back seats, lid up, packed to the top with pillow packets
    cx, cy = G.COOLER
    cr = kit.empty("cooler", (cx, cy, 0.5))
    cr.scale = (1.25, 1.25, 1.25)
    kit.box("cool.body", (0.3, 0.4, 0.36), (0, 0, 0.18), P("#59b4f2", 0.5, spec=0.3), cr, bevel=0.03)
    kit.box("cool.rim", (0.34, 0.44, 0.04), (0, 0, 0.37), P("#f4f8fb", 0.5), cr, bevel=0.01)
    lid = kit.empty("cool.lid", (0, 0.2, 0.38), cr)
    kit.box("cool.lidb", (0.34, 0.44, 0.05), (0, -0.22, 0.0), P("#f4f8fb", 0.5), lid, bevel=0.02)
    lid.rotation_euler = (-1.9, 0, 0)
    cols = ["#ff5a4a", "#ffd23f", "#4fd06a", "#ff9a2e", "#c07ae8", "#46c8e8", "#ff7aa8"]
    n = 0
    for lay in range(2):
        for r in range(4):
            for c in range(3):
                packet(kit, f"cool.pk{n}", (-0.1 + c * 0.1 + 0.02 * lay, -0.14 + r * 0.095, 0.4 + lay * 0.035), cols[(n * 3) % 7], cr,
                       flat=True, rot=0.35 * (((n * 5) % 7) - 3) / 3, sz=0.28)
                n += 1
    reg("cooler", cr)
    kit.light("coolerlight", "POINT", (-0.45, -0.45, 1.3), 16.0, "#fffaf0", size=0.3, shadow=False)
    # the cargo: pillow snack packets stacked high behind the back seat
    n = 0
    for r in range(7):
        for c in range(5):
            for d in range(2):
                packet(kit, f"cargo{n}", (-0.85 + c * 0.44 + (0.2 if r % 2 else 0.0) + d * 0.1, 2.2 + d * 0.17, 0.12 + r * 0.19),
                       cols[(r + c * 2 + d) % 7], None, flat=False, rot=0.06 * ((c + d + r) % 3 - 1), sz=1.0)
                n += 1
    # the hatch (lifts away on a cue); a window in it
    ht = kit.empty("hatch", (0, 2.78, 0.0))
    kit.box("hatch.low", (2.4, 0.1, 1.2), (0, 0, 0.3), teal, ht)
    kit.box("hatch.top", (2.4, 0.1, 0.25), (0, 0, 2.0), teal, ht)
    for sx in (-1, 1):
        kit.box(f"hatch.p{sx}", (0.35, 0.1, 1.2), (sx * 1.0, 0, 1.4), teal, ht)
    reg("hatch", ht)
    # the sliding door handle on the passenger side, with three orange strokes scratched into the chrome
    kit.box("vhandle", (0.06, 0.34, 0.07), (-1.35, 1.7, 0.7), chrome, bevel=0.02)
    kit.box("vhandle_p", (0.08, 0.05, 0.07), (-1.345, 1.55, 0.7), chrome)
    kit.box("vhandle_q", (0.08, 0.05, 0.07), (-1.345, 1.85, 0.7), chrome)
    for k in range(3):
        kit.box(f"vstroke{k}", (0.04, 0.014, 0.1), (-1.385, 1.6 + k * 0.1, 0.7), P("#ff8a1e", 0.5), rot=(0, 0, 0.0))
    kit.box("vdoorline", (0.02, 0.02, 1.2), (-1.33, 0.35, 0.3), dark)
    # the dash gauge: the fuel dial with a pump glyph and a needle that never moves
    gx, gy, gz = 0.58, -1.08, 0.97
    gr = kit.empty("gauge", (gx, gy, gz))
    gr.rotation_euler = (math.pi / 2 - 0.5, 0, math.pi)
    kit.cyl("gauge.bez", 0.19, 0.04, (0, 0, 0), dark, gr, n=24, )
    kit.cyl("gauge.face", 0.16, 0.05, (0, 0, 0.005), P("#fbf6e6", 0.5), gr, n=24)
    kit.box("gauge.needle", (0.014, 0.12, 0.012), (0.04, 0.05, 0.034), P("#e8392a", 0.4), gr, rot=(0, 0, -0.9))
    for k in range(5):
        a = -1.1 + k * 0.55
        kit.box(f"gauge.tick{k}", (0.012, 0.035, 0.01), (math.sin(a) * 0.125, math.cos(a) * 0.125, 0.032), dark, gr, rot=(0, 0, -a))
    kit.box("gauge.pump", (0.045, 0.04, 0.012), (0.0, -0.075, 0.032), P("#2a2d33", 0.5), gr)
    kit.box("gauge.hose", (0.014, 0.05, 0.012), (0.03, -0.07, 0.032), P("#2a2d33", 0.5), gr)
    kit.box("gauge.pump2", (0.05, 0.014, 0.012), (0.0, -0.1, 0.032), P("#2a2d33", 0.5), gr)
    # the phone
    ph = kit.empty("phone", (0, 0, -60))
    kit.box("phone.b", (0.1, 0.014, 0.2), (0, 0, 0), P("#1a1c20", 0.4, spec=0.5), ph, bevel=0.012)
    kit.box("phone.s", (0.088, 0.004, 0.18), (0, -0.009, 0), kit.emit("#e8f6ff", 1.5), ph)
    pm = kit.emit("#101418", 0.0)
    segs = {"a": (0, 1, 1), "b": (1, 0.5, 0), "c": (1, -0.5, 0), "d": (0, -1, 1), "e": (-1, -0.5, 0), "f": (-1, 0.5, 0), "g": (0, 0, 1)}
    dig = {"4": "fgbc", "1": "bc", "2": "abged"}
    for di, (ch, cx_) in enumerate((("4", -0.036), ("1", -0.001), ("2", 0.03))):
        for k in dig[ch]:
            sx_, sz_, across = segs[k]
            size = (0.022, 0.003, 0.007) if across else (0.007, 0.003, 0.026)
            kit.box(f"phone.d{di}{k}", size, (cx_ + sx_ * 0.0105, -0.0135, sz_ * 0.024), pm, ph)
    for zz in (-0.012, 0.012):
        kit.box(f"phone.col{zz}", (0.005, 0.003, 0.005), (-0.0185, -0.0135, zz), pm, ph)
    reg("phone", ph)
    kit.light("phonelight", "POINT", (0.38, 0.6, 1.2), 1.0, "#dff2ff", size=0.2, shadow=False)
    # light inside the van, from the camera's side, so every face is lit
    kit.light("dome", "POINT", (0.0, 0.2, 1.95), 80.0, "#fff4e2", size=0.6, shadow=False)
    kit.light("dome2", "POINT", (0.0, 1.9, 1.95), 70.0, "#fff4e2", size=0.6, shadow=False)
    kit.light("hatchlight", "POINT", (-0.2, 5.0, 2.4), 260.0, "#fff0d8", size=0.6, shadow=False)
    kit.light("vkey", "POINT", (-0.2, -2.1, 1.9), 150.0, "#fffaf0", size=0.6, shadow=False)


def world(kit):
    P = kit.plastic
    snow = P(SNOW, 0.9, spec=0.04)
    kit.plane("ground", (3000, 2000), (0, 0, G.ROAD_Z - 0.02), snow)
    asph = P("#b9c2cc", 0.75, spec=0.05)
    kit.box("road", (8.6, 230, 0.08), (0.2, -50, G.ROAD_Z - 0.04), asph)
    # the scrolling strip: pines, snowbanks and dashes, all repeating every PERIOD metres
    sc = kit.empty("scroll", (0, 0, 0))
    W["scroll"].append(sc)
    ys = [-110.0 + k * PERIOD for k in range(0, 7)]     # base y of each repeat: -110 .. 34
    rows_l = [(-10.0, 6.0), (-13.0, 7.2), (-17.0, 8.0), (-22.0, 7.0)]
    rows_r = [(11.5, 6.5), (15.0, 7.5), (20.0, 7.0)]
    rows_rn = [(8.2, 5.0)]     # the near right row, hidden while the waterfall stands there
    nearr = kit.empty("scroll_nearr", (0, 0, 0), sc)
    W["nearr"] = nearr
    for yb in ys:
        for i, (x, h) in enumerate(rows_l):
            for j in range(2):
                pine(kit, x + ((j * 3 + i) % 3) * 0.6, yb + j * 12 + i * 3.7, h + (j * 0.9), sc)
        for i, (x, h) in enumerate(rows_r):
            for j in range(2):
                pine(kit, x + (j % 2) * 0.8, yb + j * 12 + i * 4.3 + 2.0, h + j * 0.7, sc)
        for i, (x, h) in enumerate(rows_rn):
            for j in range(2):
                pine(kit, x + j * 0.9, yb + j * 12 + 5.0, h + j * 0.6, nearr)
        # banks along both road edges, dashes in the middle and on the lanes
        for sx, bx in ((-1, -4.9), (1, 5.3)):
            for j in range(2):
                bk = kit.box(f"bank{sx}{yb}{j}", (1.6, 9.5, 0.75), (bx, yb + j * 12 + 4, G.ROAD_Z + 0.2), P(SNOW, 0.9, spec=0.05), sc, bevel=0.3)
        for j in range(3):
            kit.box(f"dash{yb}{j}", (0.16, 3.0, 0.03), (1.9, yb + j * 8 + 2, G.ROAD_Z + 0.02), P("#f6d36a", 0.6), sc)
            kit.box(f"edgel{yb}{j}", (0.12, 6.0, 0.03), (-3.3, yb + j * 8 + 2, G.ROAD_Z + 0.02), P("#f4f8fb", 0.6), sc)
    # far mountains
    for x, y, r, c in ((-70, -150, 60, "#e3edf6"), (60, -170, 70, "#d3e1ee"), (0, -230, 100, "#dce8f3"),
                       (-110, 20, 60, "#e3edf6"), (90, 40, 60, "#d3e1ee")):
        hill(kit, f"mtn{x}", x, y, r, 1.0, c, sz=0.7)
    # the cabin hill and the cabin; the mile post; the waterfall beside the road
    hill(kit, "cabhill", -6, -112, 28, 1.0, "#eef5fb", sz=0.5, z0=-8.0)
    cb = cabin(kit, "cabin", (-6, -112, 8.4))
    reg("cabin", cb)
    mp = kit.empty("post", (G.POST_X, -40, 0))
    kit.box("post.b", (0.34, 0.34, 2.2), (0, 0, G.ROAD_Z + 1.1), P("#fbfbf6", 0.5, spec=0.2), mp, bevel=0.04)
    kit.box("post.cap", (0.4, 0.4, 0.14), (0, 0, G.ROAD_Z + 2.25), P("#2a2d33", 0.6), mp, bevel=0.02)
    kit.box("post.band", (0.36, 0.36, 0.16), (0, 0, G.ROAD_Z + 1.9), P("#e8493a", 0.5), mp)
    ink = P("#111114", 0.6)
    for sx in (-1, 1):    # the black 1 on the two faces the road looks at (the sides toward and away from it)
        xf = sx * 0.19
        kit.box(f"post.one{sx}", (0.03, 0.06, 0.8), (xf, 0.0, G.ROAD_Z + 1.25), ink, mp)
        kit.box(f"post.oneflag{sx}", (0.03, 0.14, 0.07), (xf, -sx * 0.05, G.ROAD_Z + 1.6), ink, mp, rot=(0.6 * sx, 0, 0))
        kit.box(f"post.onebase{sx}", (0.03, 0.22, 0.07), (xf, 0.0, G.ROAD_Z + 0.85), ink, mp)
    reg("post", mp)
    fv = falls_rock(kit, "fallsv", (G.FALLS_X + 1.5, G.FALLS_Y, -60.0), yaw=-math.pi / 2)
    reg("falls", fv)


def stages(kit):
    P = kit.plastic
    # the pine on the bend
    x0, y0 = G.PINE
    kit.box("pn.road", (30, 5.0, 0.08), (x0, -4.0, G.ROAD_Z - 0.03), P("#b9c2cc", 0.75, spec=0.05))
    pine(kit, x0, y0, 11.0)
    pine(kit, x0 - 7, y0 + 4, 7.5)
    pine(kit, x0 + 8, y0 + 5, 7.0)
    pine(kit, x0 - 15, y0 + 8, 8.0)
    pine(kit, x0 + 16, y0 + 9, 8.5)
    kit.box("pn.bank", (28, 2.0, 0.7), (x0, -1.0, G.ROAD_Z + 0.2), P(SNOW, 0.9, spec=0.05), bevel=0.3)
    hill(kit, "pn.h1", x0 - 20, y0 + 50, 40, 1.0, "#e3edf6", sz=0.7)
    hill(kit, "pn.h2", x0 + 30, y0 + 60, 50, 1.0, "#d3e1ee", sz=0.7)
    # the plow in its pull-off
    x0, y0 = G.PLOW
    kit.box("pl.pad", (16, 12, 0.5), (x0, 0, -0.25), P("#b9c2cc", 0.75, spec=0.05))
    truck_cab(kit, "plow", x0, "#ff8a1e", "#ffe0b0", blade=True)
    backdrop(kit, x0, 8.0, n=9, span=34, tall=7.5)
    kit.box("pl.bank", (22, 2.0, 0.8), (x0, 5.0, G.ROAD_Z + 0.2), P(SNOW, 0.9, spec=0.05), bevel=0.3)
    # the trucker's cab
    x0, y0 = G.TRUCK
    kit.box("tr.pad", (16, 12, 0.5), (x0, 0, -0.25), P("#b9c2cc", 0.75, spec=0.05))
    truck_cab(kit, "rig", x0, "#3a6ea8", "#f4f8fb", blade=False)
    backdrop(kit, x0, 8.0, n=9, span=34, tall=7.5)
    kit.box("tr.bank", (22, 2.0, 0.8), (x0, 5.0, G.ROAD_Z + 0.2), P(SNOW, 0.9, spec=0.05), bevel=0.3)
    # the pizza man at the cabin door
    cabin_door_stage(kit, G.DOOR[0])
    backdrop(kit, G.DOOR[0], 10.0, n=9, span=34, tall=7.5)
    # the silver car
    x0 = G.SILVER[0]
    kit.box("sv.pad", (16, 12, 0.5), (x0, 0, -0.25), P("#b9c2cc", 0.75, spec=0.05))
    silver_car(kit, x0)
    backdrop(kit, x0, 8.0, n=9, span=34, tall=7.5)
    kit.box("sv.bank", (22, 2.0, 0.8), (x0, 5.0, G.ROAD_Z + 0.2), P(SNOW, 0.9, spec=0.05), bevel=0.3)
    # the waterfall seen straight on
    x0 = G.FALLS[0]
    falls_rock(kit, "fallsA", (x0, 6.0, 0.0))
    kit.box("fa.road", (30, 6.0, 0.08), (x0, -5.0, G.ROAD_Z - 0.03), P("#b9c2cc", 0.75, spec=0.05))
    for i in range(7):
        pine(kit, x0 - 24 + i * 8, 3.0 + (i % 2) * 2, 7.5)
    hill(kit, "fa.h", x0 + 10, 70, 45, 1.0, "#e3edf6", sz=0.7)
    # lights for the stages (a soft key from the camera side)
    for nm, (sx, sy) in (("pine", G.PINE), ("plow", G.PLOW), ("truck", G.TRUCK), ("door", G.DOOR), ("silver", G.SILVER)):
        kit.light(f"key_{nm}", "POINT", (sx, -4.5, 3.4), 520.0 if nm != "pine" else 0.0, "#fffaf0", size=0.8, shadow=False)
    kit.light("key_falls", "POINT", (G.FALLS[0], -6.0, 4.5), 0.0, "#fffaf0", size=0.8, shadow=False)


# ---------------------------------------------------------------------------------------------- the tag
DIG = {0: "abcdef", 1: "bc", 2: "abdeg", 3: "abcdg", 4: "bcfg", 5: "acdfg", 6: "acdefg", 7: "abc", 8: "abcdefg", 9: "abcdfg"}
SEGN = "abcdefg"


def build_tag(kit):
    """The rule meter: a cream plate with a white mile post carrying a black 1, a loop arrow, and two big digits."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    plate = kit.emit("#fff1cf", 1.0, "tagplate")
    edge = kit.emit("#2a1a0e", 0.5, "tagedge")
    ink = kit.emit("#14100c", 0.5, "tagink")
    white = kit.emit("#ffffff", 1.2, "tagwhite")
    red = kit.emit("#e8493a", 0.9, "tagred")

    def b(name, size, loc, mat, rot=(0, 0, 0)):
        ob = kit.box(name, size, loc, mat, root, rot=rot)
        noshadow(ob)
        return ob
    b("tag.edge", (1.04, 0.5, 0.004), (0, 0, 0.0), edge)
    b("tag.plate", (0.98, 0.44, 0.004), (0, 0, 0.004), plate)
    # the mile post: a tall white post with a dark outline, a red band, a black 1
    b("tag.pedge", (0.2, 0.4, 0.004), (-0.38, 0, 0.008), edge)
    b("tag.ppost", (0.16, 0.36, 0.004), (-0.38, 0, 0.012), white)
    b("tag.pband", (0.16, 0.06, 0.004), (-0.38, 0.14, 0.016), red)
    b("tag.p1", (0.04, 0.2, 0.004), (-0.375, -0.02, 0.02), ink)
    b("tag.p1f", (0.07, 0.035, 0.004), (-0.405, 0.055, 0.02), ink, rot=(0, 0, 0.5))
    b("tag.p1b", (0.1, 0.035, 0.004), (-0.375, -0.12, 0.02), ink)
    # the loop arrow: a dark ring with a gap and a head
    rg = kit.cyl("tag.ring", 0.115, 0.004, (-0.12, 0, 0.008), ink, root, n=28)
    rg2 = kit.cyl("tag.ring2", 0.072, 0.004, (-0.12, 0, 0.012), plate, root, n=28)
    gap = b("tag.gap", (0.13, 0.07, 0.004), (-0.07, 0.07, 0.016), plate, rot=(0, 0, -0.78))
    for o in (rg, rg2):
        noshadow(o)
    ah = kit.mesh_obj("tag.head", [(0, 0.0, 0), (0.07, 0.0, 0), (0.035, 0.07, 0), (0, 0.0, 0.004), (0.07, 0.0, 0.004), (0.035, 0.07, 0.004)],
                      [(2, 1, 0), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)], ink, root, (-0.055, 0.07, 0.016), (0, 0, 0))
    noshadow(ah)
    W["seg"] = []
    W["one"] = []
    layout = [("a", 0.0, 0.15, 0.1, 0.05), ("b", 0.055, 0.075, 0.05, 0.1), ("c", 0.055, -0.075, 0.05, 0.1),
              ("d", 0.0, -0.15, 0.1, 0.05), ("e", -0.055, -0.075, 0.05, 0.1), ("f", -0.055, 0.075, 0.05, 0.1),
              ("g", 0.0, 0.0, 0.1, 0.05)]
    for d, cx in enumerate((0.15, 0.34)):
        row = []
        for nm, x, z, w_, h_ in layout:
            ob = b(f"tag.d{d}{nm}", (w_, h_, 0.004), (cx + x * 1.0, z, 0.012), ink)
            row.append(ob)
        W["seg"].append(row)
        # a "1" carries a flag and a base, so it reads as a one and never as an exclamation mark
        flag = b(f"tag.d{d}flag", (0.07, 0.036, 0.004), (cx + 0.012, 0.112, 0.012), ink, rot=(0, 0, -0.55))
        base = b(f"tag.d{d}base", (0.13, 0.04, 0.004), (cx + 0.035, -0.15, 0.012), ink)
        W["one"].append((flag, base))
    rt = kit.empty("tagroot", (0, 0, 0), cam)
    # a stand-in used for placement only
    return root


# -------------------------------------------------------------------------------------------- the build
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    sun = kit.light("sun", "SUN", (0, -30, 40), 1.0, "#fff4e2", size=0.06)
    sun.data.angle = 0.08
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#e8f2ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    world(kit)
    van(kit)
    stages(kit)
    # snow flakes: small bright cubes in front of the lens, only in the squall
    cam = kit.OBJ["cam"]
    W["flakes"] = []
    fm = kit.emit("#f6fbff", 1.1, "flake")
    for i in range(70):
        u = ((i * 37) % 97) / 97.0
        v = ((i * 53) % 89) / 89.0
        d = 1.0 + 5.0 * (((i * 29) % 83) / 83.0)
        ob = kit.box(f"flake{i}", (0.03, 0.03, 0.03), (0, 0, -d), fm, cam, rot=(0.3 * i, 0.5 * i, 0.2 * i))
        noshadow(ob)
        ob["d"], ob["u"], ob["v"] = d, u, v
        W["flakes"].append(ob)
    build_tag(kit)
    return {}


def _first_frame(kit, story):
    W["inited"] = True
    try:
        hg = bpy.data.objects.get("me.headg")
        if hg is not None:
            m = kit.plastic("#3a2418", 0.9)
            kit.box("me.chin", (0.62, 0.1, 0.16), (0, -0.6, -0.5), m, hg, bevel=0.04)
            for sx in (-1, 1):
                kit.box(f"me.cheek{sx}", (0.1, 0.1, 0.34), (sx * 0.5, -0.5, -0.3), m, hg, bevel=0.03)
        jh = bpy.data.objects.get("jo.headg")
        if jh is not None:
            m = kit.plastic("#201612", 0.9)
            kit.box("jo.tail", (0.28, 0.28, 1.1), (0, 0.66, 0.35), m, jh, bevel=0.1)
        ph_ = bpy.data.objects.get("pizza.headg")
        if ph_ is not None:
            m = kit.plastic("#7a6252", 0.95)     # stubble: a shaded band across the whole jaw, no moustache
            kit.box("pizza.chin", (0.98, 0.06, 0.3), (0, -0.64, -0.42), m, ph_, bevel=0.03)
            for sx in (-1, 1):
                kit.box(f"pizza.cheek{sx}", (0.14, 0.06, 0.5), (sx * 0.5, -0.55, -0.2), m, ph_, bevel=0.03)
        for who, light, sleeve in (("quiet1", "#f6d6b4", "#6a7a8a"), ("quiet2", "#ecc096", "#8a5a7a")):
            qh = bpy.data.objects.get(f"{who}.headg")
            if qh is not None:     # a flat palm over the mouth, with the wrist and sleeve rising to it
                ed = kit.plastic("#6a4630", 0.6)
                pc = kit.plastic(light, 0.6)
                kit.box(f"{who}.pedge", (0.84, 0.1, 0.5), (0, -0.7, -0.3), ed, qh, bevel=0.04)
                kit.box(f"{who}.palm", (0.76, 0.12, 0.42), (0, -0.76, -0.3), pc, qh, bevel=0.04)
                for fx in (-0.19, 0.0, 0.19):
                    kit.box(f"{who}.fgap{fx}", (0.02, 0.04, 0.12), (fx, -0.83, -0.05), ed, qh)
                kit.box(f"{who}.thumb", (0.14, 0.1, 0.3), (0.42, -0.74, -0.52), pc, qh, bevel=0.03)
                kit.box(f"{who}.wrist", (0.34, 0.18, 0.5), (0.0, -0.76, -0.75), pc, qh, bevel=0.04)
                kit.box(f"{who}.sleeve", (0.5, 0.26, 0.6), (0.0, -0.78, -1.2), kit.plastic(sleeve, 0.8), qh, bevel=0.05)
        if mh0 := bpy.data.objects.get("mom.headg"):
            # clear lenses with a thin dark frame all round, so her eyes read
            for sx in (-1, 1):
                gl = bpy.data.objects.get(f"mom.gl{sx}")
                if gl is not None:
                    gl.hide_render = True
                    gl.hide_viewport = True
                    gl.scale = (0.0001, 0.0001, 0.0001)
                    gl.location = (0.0, 0.0, -50.0)
                fr = kit.plastic("#2a1a16", 0.4)
                x0 = sx * 0.24
                kit.box(f"mom.flo{sx}", (0.46, 0.04, 0.035), (x0, -0.67, -0.19), fr, mh0)
                for ex in (-1, 1):
                    kit.box(f"mom.fl{sx}{ex}", (0.035, 0.04, 0.34), (x0 + ex * 0.22, -0.67, -0.02), fr, mh0)
        mh = bpy.data.objects.get("mom.headg")
        if mh is not None:
            m = kit.plastic("#9a8878", 0.9)
            for k, (x, z) in enumerate(((-0.45, 0.05), (0.45, 0.05), (-0.3, 0.45), (0.3, 0.45), (0.0, 0.6))):
                kit.sphere(f"mom.curl{k}", 0.2, (x, -0.1, z), m, mh, seg=8)
    except Exception:
        pass


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
    gains["sun"], gains["fill"] = look["sun"], look["fill"]
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
                u = (t - c["t"]) / dur
                u = u if c.get("lin") else ss(u)
                out = {k: prev[k] + (tgt[k] - prev[k]) * u for k in tgt}
            else:
                out = tgt
        ob.location = (out["x"], out["y"], out["z"])
        ob.rotation_euler = (ob.rotation_euler.x, ob.rotation_euler.y, out["yaw"] * D2R)
    # the waterfall beside the road replaces the near pines on that side
    fz = W["obj"]["falls"].location.z
    _hide(W["nearr"], fz > -30.0)
    # the road scrolling past: integrate the speed cues
    sp = sorted([c for c in tl["cues"] if c["name"] == "speed"], key=lambda c: c["t"])

    def speed_at(tau):
        cur = 9.0
        for c in sp:
            if c["t"] > tau:
                break
            dur = c.get("dur", 0.0)
            if dur > 0 and tau < c["t"] + dur:
                return cur + (c["v"] - cur) * ss((tau - c["t"]) / dur)
            cur = c["v"]
        return cur

    pos, tt = 0.0, 0.0
    while tt < t:
        step = min(0.05, t - tt)
        pos += speed_at(tt + step / 2) * step
        tt += step
    for sc in W["scroll"]:
        sc.location.y = pos % PERIOD
    # the cabin's smoke
    for i, sp_ in enumerate(W.get("smoke", [])):
        ph = ((t * 0.45 + i / 5.0) % 1.0)
        sp_.location = (1.9 + 0.5 * ph, 0.5, 5.2 + ph * 3.0)
        s = 0.5 + ph * 1.4
        sp_.scale = (s, s, s)
    # the lap digits
    lp = sample("lap", tl, t, {"n": 37.0})
    n = max(0, min(99, int(round(lp["n"]))))
    for di, dg in enumerate((n // 10, n % 10)):
        on = DIG[dg]
        if dg == 1:
            on = "bc"
        W["one"][di][0].hide_render = dg != 1
        W["one"][di][1].hide_render = dg != 1
        for si, nm in enumerate(SEGN):
            W["seg"][di][si].hide_render = nm not in on
    gains["phonelight"] = 7.0 if W["obj"]["phone"].location.z > -10 else 0.0
    # the tag sits in the top-left corner at a fixed angular size, whatever the lens
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
    tb = sample("tagbig", tl, t, {"s": 1.0, "x": -0.5, "y": 0.66})
    s = 0.8 * w2 * tb["s"]
    tag.scale = (s, s, s)
    tag.location = (tb["x"] * w2, tb["y"] * h2, -1.0)
    # who sits: legs straight out forward
    sits = {}
    for c in tl["cues"]:
        if c["name"] == "sit" and c["t"] <= t:
            sits[c["who"]] = c
    for who, c in sits.items():
        root = bpy.data.objects.get(who)
        if c.get("on") and root is not None:
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    # the squall's flakes ride on the camera, but never inside the van or a cab: those are culled by world position
    fl = sample("flakes", tl, t, {"v": 0.0})
    on = fl["v"] > 0.5
    cam_m = None
    if on and spec and isinstance(bpy.app.version, tuple):
        try:
            from mathutils import Matrix
            keys = spec["cam"]
            u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
            loc_, tgt_ = keys[0][1], keys[0][2]
            if len(keys) > 1 and u > keys[0][0]:
                loc_, tgt_ = keys[-1][1], keys[-1][2]
                for a, b in zip(keys, keys[1:]):
                    if u <= b[0]:
                        v = ss((u - a[0]) / max(1e-6, b[0] - a[0]))
                        loc_ = [a[1][i] + (b[1][i] - a[1][i]) * v for i in range(3)]
                        tgt_ = [a[2][i] + (b[2][i] - a[2][i]) * v for i in range(3)]
                        break
            q = (Vector(tgt_) - Vector(loc_)).to_track_quat("-Z", "Y")
            cam_m = Matrix.Translation(loc_) @ q.to_matrix().to_4x4()
        except Exception:
            cam_m = None
    boxes = [(-1.7, 1.7, -3.4, 3.2, -0.8, 2.8), (G.PLOW[0] - 2.6, G.PLOW[0] + 3.6, -7.0, 2.4, -0.8, 4.4)]
    for ob in W["flakes"]:
        ob.hide_render = not on
        if not on:
            continue
        dd = ob["d"]
        xr = dd * 0.34
        yr = dd * 0.6
        x = ((ob["u"] * 2 - 1) * xr + 1.6 * t * (0.7 + 0.5 * ob["v"]) + xr) % (2 * xr) - xr
        y = ((ob["v"] * 2 - 1) * yr - 0.5 * t * (0.5 + ob["u"]) + yr) % (2 * yr) - yr
        sc_ = 0.5 + 0.6 * (dd / 6.0)
        ob.location = (x, y, -dd)
        ob.scale = (sc_, sc_, sc_)
        if cam_m is not None:
            wp = cam_m @ Vector((x, y, -dd))
            if any(b[0] < wp.x < b[1] and b[2] < wp.y < b[3] and b[4] < wp.z < b[5] for b in boxes):
                ob.hide_render = True
    return gains
