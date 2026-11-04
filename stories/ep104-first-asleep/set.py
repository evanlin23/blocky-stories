"""ep104-first-asleep: the dream. Phase 1: the creature test still (the dream giant at a porch, moonlit driveway)."""

from __future__ import annotations

import math

import bpy

K = {}


def P(h, rough=0.5, spec=0.3):
    return K["kit"].plastic(h, rough, spec=spec)


def B(parent, size, loc, mat, rot=(0, 0, 0), bevel=0.01, name="b"):
    return K["kit"].box(name, size, loc, mat, parent, rot, bevel)


def E(parent, loc=(0, 0, 0), rot=(0, 0, 0), name="e"):
    return K["kit"].empty(name, loc, parent, rot)


def build_giant(kit, at, yaw=0.0):
    """A stooped man, arms past his knees, a long neck, a light-blue cap. Built from boxes. Faces -y (the camera)."""
    root = E(None, at, (0, 0, yaw), "giant")
    cloth = P("#141a33", 0.7, 0.4)           # a dark navy shirt
    pants = P("#101428", 0.7, 0.4)
    skin = P("#3a3040", 0.7, 0.3)
    capm = P("#2c3f5e", 0.8, 0.5)
    strap = P("#8a5a2b", 0.6, 0.3)
    shoe = P("#0b0b10", 0.5, 0.2)
    # legs, hip at z 1.45; narrow, long
    for sx in (-1, 1):
        B(root, (0.20, 0.24, 1.5), (sx * 0.16, 0, 0.75 + 0.05), pants, name="leg")
        B(root, (0.22, 0.42, 0.12), (sx * 0.16, -0.08, 0.06), shoe, name="foot")
    # torso, leaning toward the camera
    tor = E(root, (0, 0.0, 1.55), (0.7, 0.0, 0.12), "torso")
    B(tor, (0.52, 0.28, 0.95), (0, 0, 0.47), cloth, name="chest")
    B(tor, (0.52, 0.30, 0.14), (0, 0, 0.0), pants, name="hips")
    # mailbag strap across the chest, bag at the hip
    B(tor, (0.09, 0.30, 1.0), (0.0, -0.01, 0.5), strap, rot=(0, 0.62, 0), bevel=0.01, name="strap")
    bag = B(tor, (0.5, 0.2, 0.42), (-0.38, -0.02, -0.18), strap, rot=(0, 0.1, 0), bevel=0.03, name="bag")
    paper = P("#e9e4d8", 0.9, 0.05)
    for i in range(4):
        B(tor, (0.14, 0.02, 0.18), (-0.5 + 0.08 * i, -0.13, -0.0 - 0.02 * i), paper, rot=(0, 0, 0.2 * i - 0.3), bevel=0.003, name="paper")
    # arms: long, hands below the knees
    for sx in (-1, 1):
        sh = E(tor, (sx * 0.34, 0.0, 0.88 - (0.14 if sx < 0 else 0)), (-0.25 + 0.05 * sx, 0, sx * 0.07 + (0.12 if sx < 0 else -0.05)), "shoulder")
        B(sh, (0.12, 0.13, 0.95), (0, 0, -0.47), cloth, name="uarm")
        el = E(sh, (0, 0, -0.95), (0.18 if sx < 0 else 0.5, 0, 0), "elbow")
        B(el, (0.11, 0.12, 0.85), (0, 0, -0.42), cloth, name="farm")
        B(el, (0.13, 0.08, 0.2), (0, 0, -0.95), skin, name="hand")
        for f in range(3):
            B(el, (0.025, 0.04, 0.22), (-0.04 + 0.04 * f, 0, -1.12), skin, name="fing")
    # long neck, then the head bent forward and down
    neck = E(tor, (0, 0, 0.92), (0.45, 0.0, 0.1), "neck")
    B(neck, (0.24, 0.22, 0.6), (0, 0, 0.32), skin, name="neckb")
    head = E(neck, (0, 0, 0.6), (-0.1, 0.12, 0.08), "chead")
    B(head, (0.32, 0.30, 0.52), (0, 0, 0.26), P("#4a3a54", 0.7, 0.2), name="skull")     # long narrow head
    B(head, (0.36, 0.34, 0.14), (0, 0.0, 0.5), capm, bevel=0.03, name="cap")   # cap crown over the head
    B(head, (0.35, 0.18, 0.03), (0, -0.22, 0.46), capm, rot=(0.12, 0, 0), bevel=0.008, name="brim")
    glow = kit.emit("#dfeaff", 6.0, name="glint")
    for sx in (-1, 1):
        kit.sphere("glint", 0.014, (sx * 0.05, -0.15, 0.34), glow, head, seg=8)
    return root


def build(kit, story, tl):
    K["kit"] = kit
    sc = bpy.context.scene
    w = sc.world
    nt = w.node_tree
    bg = nt.nodes["Background"]
    bg.inputs["Color"].default_value = (0.05, 0.04, 0.12, 1)
    bg.inputs["Strength"].default_value = 1.0
    # ground: dark grass and a driveway
    B(None, (80, 80, 0.4), (0, 10, -0.2), P("#1d2a3a", 0.9, 0.05), name="lawn", bevel=0)
    B(None, (3.4, 40, 0.06), (0, 6, 0.0), P("#46466e", 0.6, 0.2), name="drive", bevel=0)
    # house wall and porch, 6 m back
    wall = P("#9ee6c4", 0.7, 0.1)
    B(None, (14, 0.3, 5.0), (0, 6.6, 2.5), kit.emit("#4a3f86", 0.7, name="wallglow"), name="housewall", bevel=0)
    B(None, (5.6, 3.6, 0.25), (0, 4.8, 0.12), P("#6e5a7a", 0.8, 0.1), name="porchfloor", bevel=0.01)
    for sx in (-1, 1):
        B(None, (0.16, 0.16, 2.9), (sx * 2.7, 3.2, 1.5), P("#cfc7e6", 0.6, 0.2), name="post", bevel=0.01)
    B(None, (6.0, 3.8, 0.18), (0, 5.0, 3.0), P("#07061a", 0.9, 0.0), name="porchroof", bevel=0.01)
    B(None, (6.2, 0.2, 0.30), (0, 3.1, 2.95), P("#e6defa", 0.5, 0.2), name="fascia", bevel=0.01)
    B(None, (1.1, 0.12, 2.0), (-1.4, 6.4, 1.2), P("#5a3c6e", 0.6, 0.1), name="door", bevel=0.01)
    B(None, (1.2, 0.1, 1.0), (2.0, 6.4, 1.6), kit.emit("#ffcf7a", 3.0, name="win"), name="window", bevel=0)
    # mailbox on a post: the scale reference, at the giant's knee
    B(None, (0.14, 0.14, 1.05), (-0.55, 3.4, 0.55), P("#8a6a4a", 0.7, 0.05), name="mpost", bevel=0.01)
    B(None, (0.4, 0.75, 0.36), (-0.55, 3.4, 1.22), P("#d7263d", 0.4, 0.3), name="mailbox", bevel=0.05)
    # a streetlight behind and to the side of the giant
    B(None, (0.14, 0.14, 5.0), (2.4, 8.0, 2.5), P("#2b2f3b", 0.5, 0.3), name="pole", bevel=0.02)
    B(None, (0.9, 0.12, 0.12), (1.95, 8.0, 5.0), P("#2b2f3b", 0.5, 0.3), name="arm", bevel=0.02)
    B(None, (0.4, 0.3, 0.12), (1.5, 8.0, 4.95), kit.emit("#dfe8ff", 25.0, name="bulb"), name="lamp", bevel=0.01)
    # the giant, at the porch's edge, under the roof (roof edge 2.45), head pressed to it
    build_giant(kit, (0.15, 4.2, 0.15), 0.12)
    B(None, (1.2, 0.1, 2.6), (0.75, 6.45, 2.0), kit.emit("#cfdcff", 1.6, name="glowpanel"), name="glowpanel", bevel=0)
    # lights: hard rim from behind, a cold lavender bounce from below, a faint moon
    L = kit.light("street", "SPOT", (1.5, 8.0, 4.6), 5000, "#d8e6ff", size=0.2, spot=55, blend=0.3)
    kit.aim(L, (0.1, 3.9, 2.0))
    L2 = kit.light("rimcap", "SPOT", (-1.0, 6.5, 3.4), 2500, "#bfe0ff", size=0.15, spot=40, blend=0.4)
    kit.aim(L2, (0.1, 3.9, 2.6))
    L3 = kit.light("under", "SPOT", (0.0, -0.5, 0.05), 0, "#b79cff", size=0.3, spot=60, blend=0.6)
    kit.aim(L3, (0.1, 3.9, 1.4))
    L4 = kit.light("capkey", "SPOT", (1.2, -1.5, 3.8), 0, "#cfe8ff", size=0.1, spot=9, blend=0.5)
    kit.aim(L4, (0.1, 3.7, 2.7))
    L5 = kit.light("rimL", "SPOT", (-2.4, 5.2, 3.0), 9000, "#b79cff", size=0.2, spot=50, blend=0.4)
    kit.aim(L5, (0.1, 4.2, 1.8))
    L6 = kit.light("rimR", "SPOT", (2.6, 5.2, 3.0), 9000, "#c9d8ff", size=0.2, spot=50, blend=0.4)
    kit.aim(L6, (0.1, 4.2, 1.8))
    kit.light("moon", "SUN", (0, 0, 20), 0.15, "#8f8cff", rot=(math.radians(50), 0, math.radians(200)), size=0.1)
    return {}


def animate(kit, story, tl, t, ctx):
    return None
