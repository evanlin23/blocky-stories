"""Closing Page (ep90): a bright supermarket at 9:59 and its endless back room, where the Tallyman keeps the tabs.

Coordinates: metres, z up, front of a character is -y at yaw 0. The back room runs along +y; the Tallyman stands at
(0, 0) facing -y (toward the camera / me), shelves and crates recede behind him.
(Creature test: only the back room and the Tallyman are built so far.)
"""
from __future__ import annotations

import math
import random

import bpy  # noqa: F401
from mathutils import Vector as V

ORANGE, WHITE, YELLOW, CREAM = "#ff9a1f", "#fff6e6", "#ffd93b", "#ffe9bd"
APRON, WOOD, LAMP, BLUE, RED = "#2f9e5b", "#b98a52", "#ffcf80", "#5ec8ff", "#ff3b3b"
CH = {}


def stickers(kit, name, size, centre, rng, n, parent, skip=(), base_c="#a85a14"):
    """Cover a box part (size, centre) with n layered curling price stickers, plus an orange core."""
    kit.box(f"{name}.core", size, centre, kit.plastic(base_c, 0.5), parent, bevel=0.03)
    mats = [kit.plastic(c, 0.6) for c in ("#8a4a12", "#7c4310", "#a8681c", "#6f6a60", "#8a4a12", "#6e3a0e", "#5f5a52")]
    ink = kit.plastic("#3a2410", 0.6)
    sx, sy, sz = size
    c = V(centre)
    faces = [f for f in ("+x", "-x", "+y", "-y", "+z", "-z") if f not in skip]
    for i in range(n):
        f = rng.choice(faces)
        ax = "xyz".index(f[1])
        sgn = 1 if f[0] == "+" else -1
        dims = [sx, sy, sz]
        others = [k for k in range(3) if k != ax]
        w = rng.uniform(0.11, 0.24)
        h = rng.uniform(0.08, 0.17)
        off = V((0, 0, 0))
        for k in others:
            off[k] = rng.uniform(-0.5, 0.5) * dims[k] * 0.98
        off[ax] = sgn * (dims[ax] / 2 + 0.012 + (i % 9) * 0.0035 + rng.uniform(0, 0.002))
        pd = [0.0, 0.0, 0.0]
        pd[ax] = 0.008
        pd[others[0]] = w
        pd[others[1]] = h
        rot = [0.0, 0.0, 0.0]
        rot[ax] = rng.uniform(-0.5, 0.5)                       # twist about the face normal
        rot[others[0]] += rng.uniform(-0.45, 0.45) * (1 if i % 3 == 0 else 0.5)       # curling edge
        rot[others[1]] += rng.uniform(-0.45, 0.45) * (1 if i % 3 == 1 else 0.5)
        p = kit.box(f"{name}.st{i}", pd, tuple(c + off), rng.choice(mats), parent, rot=tuple(rot), bevel=0.004)
        if i % 5 == 0:         # a price numeral bar on some
            pd2 = list(pd)
            pd2[ax] = 0.004
            pd2[others[0]] = w * 0.6
            pd2[others[1]] = h * 0.18
            o2 = off.copy()
            o2[ax] += sgn * 0.007
            kit.box(f"{name}.bar{i}", pd2, tuple(c + o2), ink, parent, rot=tuple(rot), bevel=0.0)


def tallyman(kit, pos=(0.0, 0.0), yaw=0.0, scale=1.0):
    rng = random.Random(90)
    root = kit.empty("tallyman", (pos[0], pos[1], 0.0), rot=(0, 0, yaw))
    root.scale = (scale, scale, scale)
    # a long-limbed clerk, taller than the cast (about 2.45 m)
    legs = [(-0.2, 0), (0.2, 0)]
    for k, (lx, _) in enumerate(legs):
        stickers(kit, f"leg{k}", (0.3, 0.32, 1.1), (lx, 0, 0.55), rng, 120, root, skip=("-z",))
        kit.box(f"shoe{k}", (0.34, 0.5, 0.14), (lx, -0.07, 0.07), kit.plastic("#2a2420", 0.6), root, bevel=0.03)
    stickers(kit, "torso", (0.86, 0.5, 0.95), (0, 0, 1.58), rng, 330, root, skip=("-z",))
    for k, ax in enumerate((-1, 1)):
        stickers(kit, f"arm{k}", (0.24, 0.24, 1.7), (ax * 0.58, -0.08, 1.25), rng, 170, root)
        kit.box(f"hand{k}", (0.26, 0.2, 0.26), (ax * 0.58, -0.1, 0.3), kit.plastic("#c9c2b4", 0.6), root, bevel=0.05)
    # the head: a taller sticker block, the neck stickers under it
    neck = 2.1
    hd = kit.empty("headpivot", (0, 0, neck), root, rot=(0.38, 0.22, 0.0))
    stickers(kit, "head", (0.56, 0.5, 0.56), (0, 0, 2.36 - neck), rng, 220, hd, skip=("-z", "-y"))
    kit.box("face", (0.52, 0.04, 0.52), (0, -0.265, 2.36 - neck), kit.plastic("#a85a14", 0.6), hd, bevel=0.01)
    kit.box("visor", (0.54, 0.03, 0.2), (0, -0.295, 2.41 - neck), kit.plastic("#0a0404", 0.4), hd, bevel=0.008)
    kit.box("scan", (0.5, 0.02, 0.05), (0, -0.315, 2.41 - neck), kit.emit("#ff0000", 5), hd, bevel=0.005)
    kit.box("scanglow", (0.56, 0.015, 0.012), (0, -0.318, 2.41 - neck), kit.emit("#ff0000", 5), hd)
    # the green apron over the torso front, with a pocket and a chest read-out (glyph bars only)
    ap = kit.plastic(APRON, 0.5)
    kit.box("apron", (0.74, 0.07, 0.85), (0, -0.30, 1.52), ap, root, bevel=0.025)
    kit.box("apronbib", (0.52, 0.07, 0.3), (0, -0.30, 2.0), ap, root, bevel=0.025)
    kit.box("strapL", (0.07, 0.06, 0.35), (-0.3, -0.24, 2.1), ap, root)
    kit.box("strapR", (0.07, 0.06, 0.35), (0.3, -0.24, 2.1), ap, root)
    kit.box("pocket", (0.5, 0.05, 0.22), (0, -0.36, 1.25), kit.plastic("#26844c", 0.5), root, bevel=0.02)
    kit.box("hem", (0.2, 0.03, 0.1), (0.16, -0.405, 1.12), kit.plastic("#d9d2c0", 0.5), root, bevel=0.005)
    for i, hh in enumerate((0.05, 0.06, 0.04, 0.06)):
        kit.box(f"num{i}", (0.03, 0.01, hh), (0.09 + i * 0.045, -0.425, 1.12), kit.plastic("#201408", 0.6), root)
    CH["root"] = root
    return root


def room(kit):
    floor = kit.plastic("#d8cfc0", 0.5)
    kit.box("floor", (30, 60, 0.2), (0, 14, -0.1), floor)
    kit.box("ceil", (30, 60, 0.2), (0, 14, 5.1), kit.plastic("#8f8f86", 0.9))
    kit.box("wallL", (0.3, 60, 5.2), (-9, 14, 2.5), kit.plastic("#cbbfa6", 0.8))
    kit.box("wallR", (0.3, 60, 5.2), (9, 14, 2.5), kit.plastic("#cbbfa6", 0.8))
    kit.box("wallB", (30, 0.3, 5.2), (0, 42, 2.5), kit.plastic("#cbbfa6", 0.8))
    kit.box("wallF", (30, 0.3, 5.2), (0, -9, 2.5), kit.plastic("#cbbfa6", 0.8))
    steel = kit.plastic("#7d8f9c", 0.4)
    wood = kit.plastic(WOOD, 0.7)
    dark = kit.plastic("#8a6338", 0.7)
    mark = kit.plastic("#8a4fd1", 0.5)
    rng = random.Random(5)
    # long rows of tall shelves going back, crates on them, each crate a name glyph
    for sx in (-5.2, -2.6, 2.6, 5.2):
        for y0 in range(2, 40, 1):
            pass
        for lvl, z in enumerate((0.1, 1.35, 2.6, 3.85)):
            kit.box(f"shelf{sx}.{lvl}", (1.1, 38, 0.1), (sx, 21, z), steel)
            y = 3.0
            while y < 40:
                w = rng.choice((0.9, 1.1, 1.3))
                kit.box(f"cr{sx}.{lvl}.{int(y)}", (0.95, w, 0.95), (sx + rng.uniform(-0.04, 0.04), y, z + 0.52),
                        wood if rng.random() < 0.6 else dark, bevel=0.025)
                kit.box(f"gl{sx}.{lvl}.{int(y)}", (0.01, 0.28, 0.28), (sx + (0.482 if sx < 0 else -0.482), y, z + 0.62), mark) \
                    if False else None
                side = 1 if sx < 0 else -1
                gy = y
                kit.box(f"gl{sx}.{lvl}.{int(y)}", (0.012, 0.24, 0.24), (sx + side * 0.485, gy, z + 0.62),
                        kit.plastic(rng.choice(("#8a4fd1", "#ff9a1f", "#6fd34a", "#5ec8ff")), 0.5))
                y += w + 0.08
        for z in (0, 4.0):
            for y in (2.5, 20, 39.5):
                kit.box(f"post{sx}{z}{y}", (0.12, 0.12, 5), (sx - 0.5, y, 2.5), steel)
    # warm work lights in rows overhead
    lamp = kit.emit(LAMP, 5)
    for ly in range(17, 40, 4):
        for lx in (-3.9, 0.0, 3.9):
            kit.box(f"lamp{lx}.{ly}", (0.35, 2.4, 0.08), (lx, ly, 4.98), lamp)
    for ly, e in ((24, 500),):
        kit.light(f"work{ly}", "AREA", (0, ly, 4.7), e, LAMP, size=5)
        kit.aim(kit.LIGHTS[f"work{ly}"]["obj"], (0, ly, 0))
    # a doorway of clear plastic strips at the front is behind the camera; not built here


def build(kit, story, tl):
    room(kit)
    tallyman(kit, (0.0, 5.0), 0.0, 1.3)
    # key from below-front (warm), blue freezer rim from behind-left, a little fill
    kit.light("under", "AREA", (0.0, 1.5, 0.2), 700, "#ffb860", size=2.5)
    kit.light("underL", "AREA", (-1.8, 3.0, 0.2), 350, "#ffb860", size=1.5)
    kit.aim(kit.LIGHTS["underL"]["obj"], (0, 5, 2.0))
    kit.aim(kit.LIGHTS["under"]["obj"], (0, 5, 2.4))
    kit.light("rimB", "AREA", (-2.2, 8.5, 3.2), 1100, BLUE, size=2.0)
    kit.aim(kit.LIGHTS["rimB"]["obj"], (0, 5, 1.9))
    kit.light("rimC", "AREA", (2.4, 8.5, 3.2), 500, BLUE, size=2.0)
    kit.aim(kit.LIGHTS["rimC"]["obj"], (0, 5, 1.9))
    kit.light("fill", "AREA", (0.0, -1.5, 3.0), 60, "#fff1dd", size=4.0)
    kit.aim(kit.LIGHTS["fill"]["obj"], (0, 5, 1.9))
    kit.light("scanlight", "POINT", (0.0, 4.2, 2.9), 25, "#ff0000", size=0.1)
    return {}


def animate(kit, story, tl, t, ctx):
    return {}
