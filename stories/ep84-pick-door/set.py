"""ep84-pick-door: one bright white room, three painted exits with big numerals, and a way home behind you.

Metres, z up, the exits in the far wall (y = 7.2 n + 3) and the camera looking +y. Room n is a full room; rooms 1 and 2
are copies of room 0 stacked behind its exits, so an open exit looks into "the same room with you in it". Room 0 also
has the open way in (door four) in its back wall and the warm hall beyond it.

Built by hand from kit.py's parts. No text: the numerals are blocky seven-segment shapes made of boxes.
Cues (story.json "cues"): ring (the countdown ring glued to the camera), open (an exit swinging open).
"""

from __future__ import annotations

import math
import random

import bpy

from blocky import bl_story, rig

PERIOD = 7.2
DX = {1: -1.25, 2: 0.0, 3: 1.25}
COL = {1: "#8cff3a", 2: "#2fd1c4", 3: "#ff8a2b"}
INK = "#1a2238"
SEG = {1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc"}
_n = [0]


def nm(p):
    _n[0] += 1
    return f"{p}.{_n[0]}"


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


class K:
    kit = None


def P(hexc, rough=0.45, spec=0.4):
    return K.kit.plastic(hexc, rough, spec=spec)


def B(parent, size, loc, mat, name="b", bevel=0.006, rot=(0, 0, 0)):
    return K.kit.box(nm(name), size, loc, mat, parent, rot, bevel)


def E(parent, loc=(0, 0, 0), name="e", rot=(0, 0, 0)):
    return K.kit.empty(nm(name), loc, parent, rot)


def no_shadow(ob):
    try:
        ob.visible_shadow = False
    except Exception:
        pass


def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


def digit(parent, n, h, w, t, mat, depth, plane="xz", name="dg"):
    """A seven-segment numeral of boxes, centred, in the xz plane (depth along y) or the xy plane (depth along z)."""
    root = E(parent, (0, 0, 0), name)
    dx = -(w / 2 - t / 2) if n == 1 else 0.0
    cells = {"a": (0, h / 2 - t / 2, w, t), "d": (0, -h / 2 + t / 2, w, t), "g": (0, 0, w, t),
             "b": (w / 2 - t / 2, h / 4, t, h / 2), "c": (w / 2 - t / 2, -h / 4, t, h / 2),
             "e": (-(w / 2 - t / 2), -h / 4, t, h / 2), "f": (-(w / 2 - t / 2), h / 4, t, h / 2)}
    for s in SEG[n]:
        u, v, su, sv = cells[s]
        if plane == "xz":
            B(root, (su, depth, sv), (u + dx, 0, v), mat, "seg", 0.008)
        else:
            B(root, (su, sv, depth), (u + dx, v, 0), mat, "seg", 0.0)
    return root


# ------------------------------------------------------------------------------------------------ the room
def build_room(kit, n, ctx):
    oy = PERIOD * n
    wall, floor_m, ceil_m = P("#f1f1ec", 0.85, 0.1), P("#d4d8dc", 0.55, 0.3), kit.emit("#e8e6df", 0.8, name="ceil")
    B(None, (6.8, 7.2, 0.1), (0, oy - 0.4, -0.05), floor_m, "floor", 0.0)
    for sx in (-1, 1):
        B(None, (0.2, 7.2, 4.0), (sx * 3.3, oy - 0.4, 2.0), wall, "sidew", 0.0)
    B(None, (6.8, 7.2, 0.2), (0, oy - 0.4, 4.1), ceil_m, "ceil", 0.0)
    # baseboard strip along each side wall so the room has a scale
    for sx in (-1, 1):
        B(None, (0.03, 7.0, 0.14), (sx * 3.185, oy - 0.4, 0.07), P("#bfc6cc", 0.6), "skirt", 0.0)
    yw = oy + 3.1
    for x0, x1 in ((-3.4, -1.775), (-0.725, -0.525), (0.525, 0.725), (1.775, 3.4)):
        B(None, (x1 - x0, 0.2, 4.0), ((x0 + x1) / 2, yw, 2.0), wall, "dwall", 0.0)
    for k in (1, 2, 3):
        B(None, (1.05, 0.2, 1.2), (DX[k], yw, 3.4), wall, "header", 0.0)
    # the exits: leaf on a hinge, a brass knob, a white badge and a dark numeral
    brass = P("#c9a24c", 0.25, 0.9)
    white = P("#ffffff", 0.4, 0.2)
    ink = P(INK, 0.5, 0.2)
    doors = {}
    for k in (1, 2, 3):
        right = k == 3
        hx = DX[k] + (0.5 if right else -0.5)
        hinge = E(None, (hx, yw, 0.02), f"hinge{n}{k}")
        s = -1 if right else 1
        leaf = B(hinge, (1.0, 0.06, 2.76), (s * 0.5, 0, 1.38), P(COL[k], 0.35, 0.5), f"leaf{n}{k}", 0.012)
        B(hinge, (0.8, 0.012, 0.9), (s * 0.5, -0.036, 0.62), P(COL[k], 0.3, 0.6), "panel", 0.004)
        B(hinge, (0.06, 0.04, 0.06), (s * 0.84, -0.045, 1.15), brass, "knobbase", 0.01)
        kn = kit.sphere(nm("knob"), 0.065, (s * 0.84, -0.095, 1.15), brass, hinge, seg=16)
        if k == 2:
            kit.cyl(nm("kd"), 0.034, 0.006, (s * 0.84, -0.158, 1.15), P(INK, 0.4, 0.3), hinge, rot=(math.pi / 2, 0, 0), n=20)
            g4 = digit(hinge, 4, 0.05, 0.034, 0.011, P("#ffffff", 0.3, 0.2), 0.012, "xz", f"kn4{n}")
            g4.location = (s * 0.84, -0.166, 1.15)
        bd = kit.cyl(nm("badge"), 0.36, 0.05, (s * 0.5, -0.055, 1.95), white, hinge, rot=(math.pi / 2, 0, 0), n=32)
        dg = digit(hinge, k, 0.5, 0.3, 0.09, ink, 0.03, "xz", f"num{n}{k}")
        dg.location = (s * 0.5, -0.1, 1.95)
        doors[k] = hinge
    ctx["doors"][n] = doors
    # the worn sisal mat, with scuffs all pointing in (toward the exits)
    B(None, (2.7, 1.1, 0.025), (0, oy + 1.7, 0.0125), P("#a9844f", 0.95, 0.05), "matedge", 0.004)
    B(None, (2.56, 0.96, 0.03), (0, oy + 1.7, 0.0165), P("#c8a874", 0.95, 0.05), "mat", 0.004)
    if n < 2:
        rnd = random.Random(84 + n)
        pm = P("#6e4f27", 0.95, 0.05)
        for i in range(16):
            x = rnd.uniform(-1.1, 1.1)
            y = oy + 1.7 + rnd.uniform(-0.3, 0.25)
            yaw = rnd.uniform(-18, 18)
            pr = E(None, (x, y, 0.046), "print", rot=(0, 0, math.radians(yaw)))
            # a sole (broad toe, narrower waist) and a heel, both fat enough to read as a shoe from above
            B(pr, (0.15, 0.17, 0.012), (0, 0.075, 0), pm, "sole", 0.004)
            B(pr, (0.11, 0.08, 0.012), (0, -0.03, 0), pm, "waist", 0.003)
            B(pr, (0.12, 0.09, 0.012), (0, -0.12, 0), pm, "heel", 0.004)
    # the warm wedge from the open way in behind the camera: a doorway-shaped patch on the floor, carried over the mat
    def hw(y, a, b):
        return a + (b - a) * (y + 3.9) / 5.0

    segs = ((-3.9, 1.15, 0.0), (1.15, 2.25, 0.0195), (2.25, 2.95, 0.0))
    for i, (c, hw0, hw1) in enumerate((("#fbe6c6", 0.62, 1.15), ("#fcdba8", 0.46, 0.85), ("#ffd08a", 0.3, 0.55))):
        for ya, yb, up in segs:
            z = 0.012 + 0.004 * i + up
            vs = [(-hw(ya, hw0, hw1), oy + ya, z), (hw(ya, hw0, hw1), oy + ya, z), (hw(yb, hw0, hw1), oy + yb, z),
                  (-hw(yb, hw0, hw1), oy + yb, z)]
            if up:
                cc = {0: "#f0cf9a", 1: "#f0c07c", 2: "#f2ae55"}[i]
            else:
                cc = c
            w = kit.mesh_obj(nm("wedge"), vs, [(0, 1, 2, 3)], kit.emit(cc, 1.05, name=f"wedge{i}{'m' if up else ''}"))
            no_shadow(w)
    # light
    ln = kit.light(f"ceil{n}", "AREA", (0, oy - 0.2, 3.85), 170, "#fffaf0", size=4.0)
    ln.data.size_y = 5.0
    return oy


def build_hall(kit):
    cream = P("#ffe9c4", 0.85, 0.05)
    # back wall of room 0 with the open way in
    wall = P("#f1f1ec", 0.85, 0.1)
    B(None, (2.85, 0.2, 4.0), (-1.975, -4.1, 2.0), wall, "bwall", 0.0)
    B(None, (2.85, 0.2, 4.0), (1.975, -4.1, 2.0), wall, "bwall", 0.0)
    B(None, (1.1, 0.2, 1.2), (0, -4.1, 3.4), wall, "bheader", 0.0)
    # the 4 on a plate above the way in
    B(None, (1.0, 0.03, 1.0), (0, -3.985, 3.3), P(INK, 0.5, 0.2), "plate4", 0.01)
    digit(None, 4, 0.74, 0.5, 0.14, P("#ffffff", 0.4, 0.2), 0.03, "xz", "num4").location = (0, -3.955, 3.3)
    # the leaf, swung back into the hall
    hinge = E(None, (-0.5, -4.1, 0.02), "hinge4")
    B(hinge, (1.0, 0.06, 2.76), (0.5, 0, 1.38), P("#f4f4ee", 0.4, 0.3), "leaf4", 0.01)
    bg = E(hinge, (0.5, 0.0, 1.95), "badge4", rot=(0, 0, math.pi))
    K.kit.cyl(nm("badge4"), 0.36, 0.05, (0, -0.055, 0), P("#ffffff", 0.4, 0.2), bg, rot=(math.pi / 2, 0, 0), n=32)
    digit(bg, 4, 0.56, 0.38, 0.11, P(INK, 0.5, 0.2), 0.03, "xz", "num4b").location = (0, -0.1, 0)
    hinge.rotation_euler = (0, 0, math.radians(-68))
    # the lime tally on the inside edge of the frame
    B(None, (0.012, 0.14, 0.6), (0.544, -4.1, 1.3), P("#8cff3a", 0.5, 0.2), "tally", 0.002)
    # the hall: floor, walls, runner, lamp, coat hook
    B(None, (3.6, 5.2, 0.1), (0, -6.8, -0.05), P("#f0d5ad", 0.7, 0.2), "hfloor", 0.0)
    B(None, (0.9, 4.8, 0.02), (0, -6.7, 0.011), P("#fff1d6", 0.9, 0.05), "runner", 0.003)
    for sx in (-1, 1):
        B(None, (0.06, 4.8, 0.021), (sx * 0.4, -6.7, 0.0115), P("#e5a92a", 0.8, 0.05), "runstripe", 0.0)
        B(None, (0.1, 5.2, 3.2), (sx * 1.8, -6.8, 1.6), cream, "hwall", 0.0)
    B(None, (3.7, 0.1, 3.2), (0, -9.45, 1.6), cream, "hend", 0.0)
    B(None, (3.7, 5.2, 0.1), (0, -6.8, 3.25), P("#fff5e0", 0.9, 0.05), "hceil", 0.0)
    B(None, (0.46, 0.36, 0.7), (0.3, -6.2, 0.35), P("#c98d4d", 0.6, 0.2), "table", 0.01)
    K.kit.cyl(nm("lampbase"), 0.09, 0.28, (0.3, -6.2, 0.84), P("#ffffff", 0.4, 0.3), None, n=20)
    ctx_shade = K.kit.cyl(nm("shade"), 0.2, 0.32, (0.3, -6.2, 1.14), K.kit.emit("#ffcf6b", 3.2, name="shade"), None, n=24, r2=0.13)
    B(None, (0.04, 0.5, 0.1), (-1.72, -7.5, 1.7), P("#c98d4d", 0.6), "hookboard", 0.01)
    for dy in (-0.15, 0.15):
        B(None, (0.1, 0.04, 0.04), (-1.64, -7.5 + dy, 1.7), P("#c9a24c", 0.3, 0.8), "hook", 0.01)
    B(None, (0.14, 0.42, 0.95), (-1.62, -7.35, 1.2), P("#2f86d8", 0.6), "coat", 0.03)
    # dressing so the far end is not an empty box: art blocks, a coat on the end wall, a rug stripe, a plant
    for x, z, w, h, c in ((-0.55, 1.9, 0.5, 0.65, "#e5a92a"), (0.1, 1.95, 0.5, 0.5, "#2fd1c4"), (0.7, 1.85, 0.4, 0.75, "#ff8a2b")):
        B(None, (w, 0.03, h), (x, -9.38, z), P(c, 0.6, 0.2), "art", 0.006)
    B(None, (0.5, 0.03, 0.12), (-1.2, -9.38, 1.7), P("#c98d4d", 0.6), "hookboard2", 0.01)
    for dx in (-1.35, -1.05):
        B(None, (0.05, 0.08, 0.04), (dx, -9.33, 1.7), P("#c9a24c", 0.3, 0.8), "hook2", 0.01)
    B(None, (0.3, 0.1, 0.8), (-1.35, -9.28, 1.25), P("#2f86d8", 0.6), "coat2", 0.03)
    B(None, (0.26, 0.26, 0.4), (-1.3, -8.6, 0.2), P("#7a4a2a", 0.7), "pot", 0.01)
    B(None, (0.3, 0.3, 0.5), (-1.3, -8.6, 0.65), P("#4fa860", 0.7), "leaves", 0.04)
    # lights: the lamp, and a warm spot through the way in that throws the wedge on the floor
    K.kit.light("lamp", "POINT", (0.15, -6.0, 1.3), 150, "#ffcf6b", size=0.15)
    K.kit.light("hallfill", "POINT", (0, -6.5, 2.7), 220, "#ffe9c4", size=0.5, shadow=False)
    sp = K.kit.light("wedge", "SPOT", (0, -6.6, 2.0), 600, "#ffd89a", size=0.3, spot=75, blend=0.35)
    K.kit.aim(sp, (0, 0.5, 0.0))


# ------------------------------------------------------------------------------------------------ the ring
def build_ring(kit, ctx):
    cam = kit.OBJ["cam"]
    root = E(cam, (0, 0, -0.15), "ringroot")
    ctx["ring_root"] = root
    bg = kit.cyl(nm("ringbg"), 1.1, 0.02, (0, 0, 0), kit.emit("#0d2b34", 0.9, name="ringbg"), root, n=48)
    rim = kit.cyl(nm("ringrim"), 1.2, 0.02, (0, 0, -0.04), kit.emit("#ffffff", 0.9, name="ringrim"), root, n=48)
    lit_m, dim_m = kit.emit("#8cff3a", 1.1, name="ringlit"), kit.emit("#2c5a60", 0.8, name="ringdim")
    ctx["ring_lit"], ctx["ring_dim"] = [], []
    for i in range(24):
        a = 2 * math.pi * i / 24
        loc = (0.82 * math.sin(a), 0.82 * math.cos(a), 0.06)
        d = K.kit.box(nm("rdim"), (0.2, 0.2, 0.02), loc, dim_m, root, (0, 0, -a), 0.0)
        l = K.kit.box(nm("rlit"), (0.215, 0.2, 0.03), (loc[0], loc[1], 0.09), lit_m, root, (0, 0, -a), 0.0)
        ctx["ring_dim"].append(d)
        ctx["ring_lit"].append(l)
    ctx["ring_dg"] = {}
    wm = kit.emit("#ffffff", 1.3, name="ringdg")
    for n in (1, 2, 3, 4):
        g = digit(root, n, 0.9, 0.5, 0.17, wm, 0.04, "xy", f"rdg{n}")
        g.location = (0, 0, 0.14)
        ctx["ring_dg"][n] = g
    for o in [bg, rim] + ctx["ring_dim"] + ctx["ring_lit"]:
        no_shadow(o)
    for g in ctx["ring_dg"].values():
        for c in g.children:
            no_shadow(c)


def cues_of(tl, name):
    return sorted((c for c in tl.get("cues", []) if c["name"] == name), key=lambda c: c["t"])


def place_ring(kit, ctx, tl, t, lens):
    R = cues_of(tl, "ring")
    idx = max([i for i, c in enumerate(R) if c["t"] <= t + 1e-9] or [0])
    c = R[idx]
    pv = R[idx - 1] if idx > 0 else c
    nx = R[idx + 1] if idx + 1 < len(R) else None
    v = ss((t - c["t"]) / 0.35)
    big = lerp(pv.get("big", 1.0), c.get("big", 1.0), v)
    cx = lerp(pv.get("cx", 0.0), c.get("cx", 0.0), v)
    cy = lerp(pv.get("cy", 0.0), c.get("cy", 0.0), v)
    pop = 1.0 + (0.22 * max(0.0, 1.0 - (t - c["t"]) / 0.26) if c.get("pop") else 0.0)
    f = c["f0"]
    if nx is not None and c["f1"] != c["f0"]:
        f = lerp(c["f0"], c["f1"], min(1.0, (t - c["t"]) / max(1e-6, nx["t"] - c["t"])))
    elif c["f1"] != c["f0"]:
        f = c["f1"]
    k = int(round(f * 24))
    lit = [i < k for i in range(24)]
    if c.get("spin"):
        pos = (t * c["spin"] * 24) % 24
        lit = [((i - pos) % 24) < 4 for i in range(24)]
    for i in range(24):
        ctx["ring_lit"][i].hide_render = not lit[i]
    for n, g in ctx["ring_dg"].items():
        on = c["num"] == n
        hide(g, not on)
        if on and n == 4:
            s = max(0.02, ss((t - c["t"]) / 0.3))
            g.scale = (s, s, 1)
        else:
            g.scale = (1, 1, 1)
    d = 0.15
    unit = d / lens
    r_m = 0.20 * 6.75 * unit * big * pop
    x = (-0.63 + cx) * 6.75 * unit
    y = (0.71 + cy) * 12.0 * unit
    root = ctx["ring_root"]
    root.location = (x, y, -d)
    root.scale = (r_m, r_m, r_m)


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    K.kit = kit
    ctx = {"story": story, "doors": {}}
    ctx["shots"] = {s["id"]: s for s in story["shots"]}
    for n in (0, 1, 2):
        build_room(kit, n, ctx)
    build_hall(kit)
    ctx["fill"] = kit.light("camfill", "POINT", (0, 0, 2), 15, "#fff4e6", size=0.6, shadow=False)
    build_ring(kit, ctx)
    # the warm glow under exit one
    B(None, (0.95, 0.14, 0.012), (DX[1], 2.92, 0.008), kit.emit("#ffb347", 3.0, name="glow1"), "glow", 0.0)
    return ctx


def animate(kit, story, tl, t, ctx):
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    sd = ctx["shots"][shot["id"]]
    cl, _, lens, _ = bl_story.cam_at(sd, shot, t, {}, tl)
    ctx["fill"].location = (cl[0], cl[1] - 0.2, cl[2])
    # exits swinging open
    opened = {}
    for c in cues_of(tl, "open"):
        opened[(c["room"], c["door"])] = c["t"]
    for n, doors in ctx["doors"].items():
        for k, hinge in doors.items():
            t0 = opened.get((n, k))
            a = 105.0 * ss((t - t0) / 0.45) if t0 is not None and t >= t0 else 0.0
            if shot["id"] == "S04" and n == 0 and k == 2:
                a += 0.9 * math.sin(t * 70.0)
            hinge.rotation_euler = (0, 0, math.radians(-a if k == 3 else a))
    place_ring(kit, ctx, tl, t, lens)
    return {}
