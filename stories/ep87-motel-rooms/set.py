"""ep87-motel-rooms: the motel office (creature test build). Cream stucco, turquoise counter, coral trim, a corkboard of
star-glyph cards, a warm desk lamp below Hal's face and a steady pink neon rim through the glass door."""
from __future__ import annotations

import math

import bpy

from blocky import bl_story, faces, rig


def build(kit, story, tl):
    P = lambda c, r=0.5, s=0.4: kit.plastic(c, r, spec=s)
    B = lambda size, loc, mat, name="b", bevel=0.01, rot=(0, 0, 0), parent=None: kit.box(name, size, loc, mat, parent, rot, bevel)
    sc = bpy.context.scene
    nt = sc.world.node_tree
    bg = nt.nodes["Background"]
    bg.inputs["Color"].default_value = (0.20, 0.13, 0.42, 1)
    bg.inputs["Strength"].default_value = 0.9
    cream, turq, coral = P("#fff1d6", 0.8, 0.1), P("#2cc7c9", 0.4), P("#ff7f66", 0.45)
    # room shell: x -3..3, y -2..3.4, ceiling 2.55
    B((6.2, 0.2, 2.5), (0, 3.5, 1.25), P("#d9c7a8", 0.8, 0.05), "back", 0.0)
    B((0.2, 6, 2.5), (-3.1, 1.0, 1.25), cream, "left", 0.0)
    B((0.2, 6, 2.5), (3.1, 1.0, 1.25), cream, "right", 0.0)
    B((6.4, 6.4, 0.1), (0, 0.9, 2.3), P("#f3e3c8", 0.8, 0.05), "ceiling", 0.0)
    B((6.4, 6, 0.1), (0, 1.0, -0.05), P("#c9b8a0", 0.7, 0.1), "floor", 0.0)
    B((6.2, 0.04, 0.12), (0, 3.38, 0.9), coral, "stripe", 0.01)          # coral trim stripe
    B((6.2, 0.04, 0.10), (0, 3.38, 0.05), turq, "skirt", 0.01)
    # corkboard of cards behind Hal (single star glyph = small yellow square + scribble)
    B((3.4, 0.05, 1.5), (0, 3.36, 1.55), P("#b98a5a", 0.9, 0.05), "cork", 0.01)
    k = 0
    for i in range(8):
        for j in range(4):
            tint = ("#ffffff", "#fff6c8", "#ffe0e8")[(i + j) % 3]
            x, z = -1.45 + i * 0.41, 0.98 + j * 0.37
            B((0.3, 0.012, 0.22), (x, 3.32, z), P(tint, 0.9, 0.05), "card", 0.002, rot=(0, math.radians(((i * 5 + j * 3) % 7) - 3), 0))
            B((0.07, 0.012, 0.07), (x - 0.08, 3.31, z + 0.05), P("#ffb800", 0.6), "star", 0.002)
            B((0.16, 0.012, 0.012), (x + 0.03, 3.31, z - 0.04), P("#8a7a6a", 0.9), "scr", 0.002)
    # the desk (turquoise counter) with a bell and a lamp
    B((3.0, 0.7, 1.0), (0, 0.9, 0.5), turq, "desk", 0.02)
    B((3.1, 0.8, 0.06), (0, 0.9, 1.03), P("#f4e6c4", 0.5), "top", 0.01)
    B((3.0, 0.02, 0.1), (0, 0.54, 0.8), coral, "desktrim", 0.004)
    B((0.18, 0.18, 0.06), (-0.7, 0.8, 1.09), P("#d4a017", 0.3, 0.8), "bell", 0.02)
    B((0.1, 0.1, 0.4), (0.9, 1.0, 1.26), P("#2b2b33", 0.4), "lamppole", 0.01)
    B((0.34, 0.26, 0.2), (0.9, 0.9, 1.5), P("#ff7f66", 0.4), "lampshade", 0.03)
    # glass door side window with neon-pink glow strip (stars as plain pink blocks, no letters)
    B((0.06, 1.8, 2.1), (-3.0, 0.3, 1.05), P("#ff4fb8", 0.3, 0.2), "neonpane", 0.01)
    # scale props: a big key rack with hanging keys and a tall bell, at normal-height scale
    B((0.5, 0.04, 0.7), (-1.5, 3.33, 1.1), P("#7a4a2a", 0.6), "keyrack", 0.01)
    for i in range(4):
        B((0.06, 0.03, 0.14), (-1.65 + i * 0.1, 3.3, 0.95), P("#d4a017", 0.3, 0.8), "key", 0.004)
    B((0.3, 0.3, 0.12), (0.35, 0.1, 1.12), P("#d4a017", 0.3, 0.8), "bell2", 0.03)
    B((0.06, 0.06, 0.08), (0.35, 0.1, 1.22), P("#c0c0c8", 0.3, 0.8), "bellbtn", 0.01)
    # Hal's long fingers stretched along the desktop toward the camera
    for sx in (-0.75, 0.55):
        for f in range(5):
            B((0.05, 0.7, 0.04), (sx + f * 0.075, 0.5, 1.09), P("#e8b98f", 0.5), "finger", 0.012)
    # lights
    kit.light("lampkey", "POINT", (0.3, 1.0, 1.15), 70, "#ffd89a", size=0.2)
    neon = kit.light("neon", "SPOT", (-2.9, 0.9, 1.9), 900, "#ff4fb8", size=0.4, spot=80, blend=0.6)
    kit.aim(neon, (0.3, 2.2, 2.0))
    kit.light("fillroom", "POINT", (0.0, -0.8, 2.2), 40, "#fff1d6", size=0.8, shadow=False)
    rimb = kit.light("rimback", "SPOT", (1.2, 3.0, 2.4), 90, "#ffd89a", size=0.3, spot=70, blend=0.7)
    kit.aim(rimb, (0.0, 1.9, 2.0))
    return {}


def animate(kit, story, tl, t, ctx):
    return {}
