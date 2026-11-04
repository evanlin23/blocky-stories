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
    DX, DH, BY = 0.85, 1.95, 4.6
    kit.box(nm("backL"), (W - DX, 0.2, 2.6), (-(W + DX) / 2, BY, 1.3), wall)
    kit.box(nm("backR"), (W - DX, 0.2, 2.6), ((W + DX) / 2, BY, 1.3), wall)
    kit.box(nm("backT"), (2 * DX, 0.2, 2.6 - DH), (0, BY, DH + (2.6 - DH) / 2), wall)
    for sx in (-1, 1):   # door frame, proud of the wall
        kit.box(nm("jamb"), (0.12, 0.3, DH), (sx * (DX + 0.06), BY - 0.02, DH / 2), trim, bevel=0.01)
    kit.box(nm("head"), (2 * DX + 0.24, 0.3, 0.12), (0, BY - 0.02, DH + 0.06), trim, bevel=0.01)
    # the bright room behind: floor, walls, a glowing back wall
    kit.box(nm("back_floor"), (2 * W, 4.0, 0.1), (0, 6.8, -0.05), P("#c8a47c", 0.6))
    kit.box(nm("glow"), (6.4, 0.1, 2.6), (0, 8.6, 1.3), kit.emit("#ffd9a8", 1.1))
    for sx in (-1, 1):
        kit.box(nm("bside"), (0.1, 4.0, 2.6), (sx * W, 6.8, 1.3), P("#e8d8c0", 0.8))
    # window wall in the foreground (we look through it from outside): frame bars
    FY = -0.1
    for sx in (-1, 1):
        kit.box(nm("fr"), (1.6, 0.14, 3.0), (sx * (1.15 + 0.8), FY, 1.5), P("#355c86", 0.6), bevel=0.01)
    kit.box(nm("sill"), (3.0, 0.2, 0.9), (0, FY, 0.45), P("#355c86", 0.6), bevel=0.01)
    kit.box(nm("lintel"), (3.0, 0.14, 1.0), (0, FY, 2.55), P("#355c86", 0.6), bevel=0.01)
    # kitchen dressing: oven beside the door, a counter, a table edge
    kit.prop("kitchen_oven", (-1.75, 4.2, 0), rot=0, height=1.0)
    kit.box(nm("oven_glow"), (0.5, 0.04, 0.3), (-1.75, 3.72, 0.45), kit.emit("#ff9a3c", 4.0))
    kit.prop("kitchen_cabinet1", (1.9, 4.2, 0), rot=0, height=1.0)
    # lights: dusk outside, the back room glowing behind her, the oven low in front of her
    kit.world("#1c2438", 0.35)
    ctx["back"] = kit.light("backrim", "AREA", (0.0, 5.6, 1.5), 450, "#fff0d6", size=2.0, rot=(math.radians(-90), 0, 0))
    ctx["back"].data.size, ctx["back"].data.size_y = 1.6, 1.8
    ctx["back"].rotation_euler = (math.radians(90), 0, 0)   # faces -y, toward the camera
    ctx["oven"] = kit.light("ovenlow", "POINT", (-0.5, 3.0, 0.1), 38, "#ffa458", size=0.3)
    ctx["room"] = kit.light("roomdim", "POINT", (0, 1.8, 2.3), 110, "#8fa8c8", size=0.6, shadow=False)
    return ctx


def animate(kit, story, tl, t, ctx):
    g = rig.CHARS.get("grandma")
    if g is not None and not ctx["late"]:
        ctx["late"] = True
        for k in ("arm-1", "arm1"):
            g.P[k].scale = (1.0, 1.0, 1.35)       # hands down past the hips
        P = lambda h, r=0.5: kit.plastic(h, r)
        hg = g.head.children[0]
        clip = kit.sphere(nm("pearl"), 0.075, (0.0, 0.5, 0.82), P("#fdf6ec", 0.2), hg, seg=12)   # on the bun, behind
        clip.location = (0.2, -0.05, 0.78)
        # a thin gold shawl pin: none. cardigan front edge: a darker seam down the middle
        kit.box(nm("cardi"), (0.06, 0.04, 1.9), (0, -0.505, 1.0), P("#7d62a8", 0.6), g.upper)
    return {}
