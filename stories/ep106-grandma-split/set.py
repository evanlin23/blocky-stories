"""ep106-grandma-split: Grandma is two half-people; the other half stands in Marco's kitchen.

Creature test build (2026-11-04): Marco's little blue house seen from outside through a window at dusk. Inside,
a kitchen with a wide doorway in the back wall; the split Grandma (the rig's 'grandma' with body_width 0.5, so the
torso, legs and arms are half as wide as the cast's while the head keeps its size, and the arms stretched) stands in
the doorway with a bright room behind her (rim) and the warm oven light from below. Marco's normal shoulder sits in
the foreground as the scale proof.
"""

from __future__ import annotations

import math

import bpy

from blocky import rig

_n = [0]


def nm(p):
    _n[0] += 1
    return f"{p}.{_n[0]}"


def build(kit, story, tl):
    P = lambda h, r=0.55: kit.plastic(h, r)
    ctx = {"late": False}
    wall = P("#5f86a6", 0.8)
    trim = P("#ece4d6", 0.5)
    floor = P("#9a6a45", 0.6)
    W = 3.2     # half width of the kitchen
    # floor, ceiling, side walls
    kit.box(nm("floor"), (2 * W, 8.0, 0.1), (0, 3.0, -0.05), floor)
    kit.box(nm("ceil"), (2 * W, 8.0, 0.1), (0, 3.0, 2.55), P("#d8d0c4", 0.9))
    for sx in (-1, 1):
        kit.box(nm("side"), (0.1, 8.0, 2.6), (sx * W, 3.0, 1.3), wall)
    # back wall (y=4.6) with a wide doorway: x in [-0.85, 0.85], height 1.95
    DX, DH, BY = 0.85, 2.1, 4.6
    kit.box(nm("backL"), (W - DX, 0.2, 2.6), (-(W + DX) / 2, BY, 1.3), wall)
    kit.box(nm("backR"), (W - DX, 0.2, 2.6), ((W + DX) / 2, BY, 1.3), wall)
    kit.box(nm("backT"), (2 * DX, 0.2, 2.6 - DH), (0, BY, DH + (2.6 - DH) / 2), wall)
    for sx in (-1, 1):   # door frame, proud of the wall
        kit.box(nm("jamb"), (0.12, 0.3, DH), (sx * (DX + 0.06), BY - 0.02, DH / 2), trim, bevel=0.01)
    kit.box(nm("head"), (2 * DX + 0.24, 0.3, 0.12), (0, BY - 0.02, DH + 0.06), trim, bevel=0.01)
    # the bright room behind: floor, walls, a glowing back wall
    kit.box(nm("back_floor"), (2 * W, 4.0, 0.1), (0, 6.8, -0.05), P("#c8a47c", 0.6))
    kit.box(nm("glow"), (6.4, 0.1, 2.6), (0, 8.6, 1.3), kit.emit("#ff9a50", 0.9))
    for sx in (-1, 1):
        kit.box(nm("bside"), (0.1, 4.0, 2.6), (sx * W, 6.8, 1.3), P("#e8d8c0", 0.8))
    # window wall in the foreground (we look through it from outside): frame bars
    FY = -0.1
    for sx in (-1, 1):
        kit.box(nm("fr"), (1.6, 0.14, 3.0), (sx * (1.15 + 0.8), FY, 1.5), P("#355c86", 0.6), bevel=0.01)
    kit.box(nm("sill"), (3.0, 0.2, 0.3), (0, FY, 0.15), P("#355c86", 0.6), bevel=0.01)
    kit.box(nm("lintel"), (3.0, 0.14, 0.6), (0, FY, 2.75), P("#355c86", 0.6), bevel=0.01)
    DK = P("#06101e", 0.7)
    kit.box(nm("wsill"), (3.0, 0.3, 1.2), (0, 0.45, 0.1), DK, bevel=0.01)
    kit.box(nm("wbar"), (0.5, 0.3, 3.0), (0.42, 0.45, 1.5), DK, bevel=0.01)
    kit.box(nm("wlint"), (3.0, 0.3, 0.8), (0, 0.45, 1.84), DK, bevel=0.01)
    # kitchen dressing: oven beside the door, a counter, a table edge
    kit.prop("kitchen_oven", (-1.75, 4.2, 0), rot=0, height=1.0)
    kit.box(nm("oven_glow"), (0.5, 0.04, 0.3), (-1.75, 3.72, 0.45), kit.emit("#ff9a3c", 4.0))
    kit.prop("kitchen_cabinet1", (1.9, 4.2, 0), rot=0, height=1.0)
    # lights: dusk outside, the back room glowing behind her, the oven low in front of her
    kit.world("#2b4f9a", 0.9)
    kit.box(nm("outwall"), (12, 0.2, 3), (0, FY - 0.15, 4.0), P("#4f7fcf", 0.8))
    for sx in (-1, 1):
        kit.box(nm("outwall3"), (4.5, 0.2, 5), (sx * (2.75 + 2.25), FY - 0.15, 1.5), P("#4f7fcf", 0.8))
    # roast on a board (held low in her hands) with a carving fork stuck in it, no knife
    bx, by, bz = 0.0, 3.62, 0.62
    kit.box(nm("board"), (0.46, 0.34, 0.04), (bx, by, bz), P("#8a5a32", 0.6), bevel=0.01)
    kit.box(nm("roast"), (0.34, 0.26, 0.2), (bx, by, bz + 0.12), P("#a4612f", 0.55), bevel=0.05)
    kit.box(nm("crust"), (0.34, 0.14, 0.05), (bx, by - 0.01, bz + 0.24), P("#7a3f1c", 0.5), bevel=0.02)
    kit.box(nm("forkh"), (0.045, 0.045, 0.2), (bx + 0.15, by - 0.02, bz + 0.27), P("#4a2e1a", 0.5), bevel=0.008)
    kit.box(nm("forkn"), (0.1, 0.012, 0.03), (bx + 0.15, by - 0.02, bz + 0.36), P("#d6d8dc", 0.25), bevel=0.004)
    for dx in (-0.04, 0.0, 0.04):
        kit.box(nm("tine"), (0.012, 0.012, 0.14), (bx + 0.15 + dx, by - 0.02, bz + 0.45), P("#d6d8dc", 0.25))
    ctx["marco"] = kit.light("marcofill", "POINT", (-0.6, 0.0, 1.6), 40, "#ffd9a0", size=0.5, shadow=False)
    ctx["face"] = kit.light("facefill", "POINT", (0.3, 2.6, 0.2), 80, "#ff9a50", size=0.2, shadow=False)
    ctx["cool"] = kit.light("coolfill", "POINT", (-1.0, 0.8, 1.6), 90, "#6f93ff", size=0.5, shadow=False)
    ctx["rimtop"] = kit.light("rimtop", "SPOT", (0.2, 5.3, 2.4), 2400, "#ffb067", size=0.2, spot=1.2)
    kit.aim(ctx["rimtop"], (0.0, 4.0, 1.4))
    ctx["back"] = kit.light("backrim", "AREA", (0.0, 5.6, 1.5), 500, "#ffc890", size=2.0, rot=(math.radians(-90), 0, 0))
    ctx["back"].data.size, ctx["back"].data.size_y = 1.6, 1.8
    ctx["back"].rotation_euler = (math.radians(90), 0, 0)   # faces -y, toward the camera
    ctx["oven"] = kit.light("ovenlow", "POINT", (-0.9, 3.6, 0.7), 120, "#ffa458", size=0.3)
    ctx["room"] = kit.light("roomdim", "POINT", (0, 1.8, 2.3), 25, "#8fa8c8", size=0.6, shadow=False)
    return ctx


def animate(kit, story, tl, t, ctx):
    g = rig.CHARS.get("grandma")
    if g is not None and not ctx["late"]:
        ctx["late"] = True
        for k, sx in (("arm-1", -1), ("arm1", 1)):
            g.P[k].scale = (1.0, 1.0, 1.7)       # hands down past the knees
            g.P[k].location.x = sx * 0.78         # a clear gap between each arm and the narrow torso
        P = lambda h, r=0.5: kit.plastic(h, r)
        hg = g.head.children[0]
        clip = kit.sphere(nm("pearl"), 0.075, (0.0, 0.5, 0.82), P("#fdf6ec", 0.2), hg, seg=12)   # on the bun, behind
        clip.location = (0.2, -0.05, 0.78)
        # a thin gold shawl pin: none. cardigan front edge: a darker seam down the middle
        kit.box(nm("cardi"), (0.06, 0.04, 1.9), (0, -0.505, 1.0), P("#9a78c8", 0.6), g.upper)
    if g is not None:
        g.neck.rotation_euler = (g.neck.rotation_euler[0], 0.04, g.neck.rotation_euler[2])   # a slight head tilt
    return {}
