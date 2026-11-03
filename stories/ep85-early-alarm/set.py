"""ep85-early-alarm: a small backyard at five in the morning, and the Sun asleep on the lawn.
WIP: the creature test still. Built from kit.py's parts. No text anywhere.

The Sun: a 3 x 3 x 3 lattice of soft rounded blocks (the eight corner blocks left out, so it reads round), each block a
marigold shell, with a hot core showing through the seams between them. One huge gold eye on the front, under a heavy
lid and a dark amber brow. Steady light, never a flicker; it only swells a little as it breathes.
"""
from __future__ import annotations

import math

import bpy
from mathutils import Vector as V

SUN = (0.0, 7.0, 2.1)     # the Sun's centre
PITCH = 1.65              # block pitch; blocks are 1.55 so the seams are 0.1 wide
FRONT = SUN[1] - PITCH * 1.5 + 0.05   # the front blocks' face (y)
EYE = (0.05, FRONT - 0.02, 1.8)       # the eye's centre on that face
SHED = (-7.5, 12.5)


def rot_x90():
    return (math.radians(90), 0, 0)


def disc(kit, name, r, y, x, z, mat, parent, sx=1.0, sz=1.0, h=0.02):
    ob = kit.cyl(name, r, h, (x, y, z), mat, parent, rot=rot_x90(), n=40)
    ob.scale = (sx, 1.0, sz)   # the cylinder's axis runs along y, so x and z are its width and height... via local axes
    return ob


def build(kit, story, tl):
    ctx = {}
    gold = kit.emit("#ffb000", 2.6, "sun shell")
    core = kit.emit("#ffd25e", 9.0, "sun core")
    sclera = kit.emit("#fff0b0", 5.0, "eye sclera")
    iris = kit.emit("#ffa800", 3.2, "eye iris")
    ring = kit.emit("#e07a00", 2.0, "eye ring")
    pupil = kit.emit("#4a1c00", 0.12, "eye pupil")
    glint = kit.emit("#ffffff", 6.0, "eye glint")
    lid = kit.emit("#a85500", 0.9, "sun lid")
    brow = kit.emit("#7a3a00", 0.5, "sun brow")

    # --- the ground: a dark lawn, a bare warm patch the size of a garage, and a back fence
    lawn = kit.plastic("#16423f", 0.95, "lawn")
    bare = kit.plastic("#7a4a2c", 0.95, "bare patch")
    kit.plane("lawn", (90, 90), (0, 10, 0), lawn)
    p = kit.cyl("bare", 4.6, 0.02, (0, 7.0, 0.012), bare, n=48)
    wood = kit.plastic("#3b2a22", 0.8, "fence")
    for i in range(-9, 10):
        kit.box(f"fence{i}", (0.9, 0.08, 1.7), (i * 1.0 + 2, 19.0, 0.85), wood, bevel=0.02)

    # --- the Sun
    root = kit.empty("sun", (SUN[0], SUN[1], SUN[2]))
    kit.sphere("sun.core", 2.35, (0, 0, 0), core, root, seg=24)
    k = 0
    for ix in (-1, 0, 1):
        for iy in (-1, 0, 1):
            for iz in (-1, 0, 1):
                if abs(ix) + abs(iy) + abs(iz) == 3:
                    continue   # no corner blocks: a worn-smooth die
                kit.box(f"sun.blk{k}", (1.55, 1.55, 1.55), (ix * PITCH, iy * PITCH, iz * PITCH), gold, root, bevel=0.42, seg=4)
                k += 1
    # the eye, in the root so it breathes with the body
    ex, ey, ez = EYE[0] - SUN[0], EYE[1] - SUN[1], EYE[2] - SUN[2]
    ctx["root"] = root
    ctx["eye_y"] = ey
    kit.box("sun.socket", (1.9, 0.12, 1.45), (ex, ey - 0.0, ez), kit.emit("#7a3a00", 0.7, "socket"), root, bevel=0.05)
    sc = disc(kit, "sun.sclera", 0.62, ey - 0.10, ex, ez, sclera, root, sx=1.0, sz=0.82, h=0.04)
    disc(kit, "sun.ring", 0.42, ey - 0.13, ex, ez - 0.02, ring, root, h=0.03)
    disc(kit, "sun.iris", 0.37, ey - 0.15, ex, ez - 0.02, iris, root, h=0.03)
    disc(kit, "sun.pupil", 0.2, ey - 0.17, ex, ez - 0.02, pupil, root, sx=0.5, sz=1.0, h=0.03)
    kit.sphere("sun.glint", 0.055, (ex + 0.13, ey - 0.20, ez + 0.1), glint, root, seg=10)
    # lids: the upper one half down (heavy, menacing), a thinner lower one; the brow ridge over both
    ctx["lid"] = disc(kit, "sun.lid", 0.7, ey - 0.20, ex, ez + 0.55, lid, root, sx=1.0, sz=0.55, h=0.04)
    disc(kit, "sun.lidlow", 0.7, ey - 0.20, ex, ez - 0.78, lid, root, sx=1.0, sz=0.4, h=0.04)
    kit.box("sun.brow", (1.9, 0.28, 0.34), (ex, ey - 0.12, ez + 0.88), brow, root, bevel=0.1, seg=3)
    # --- the shed, barn red, with its door ajar and warm light spilling
    red = kit.plastic("#c4473a", 0.7, "barn red")
    dark = kit.plastic("#5a2620", 0.8, "shed roof")
    sx, sy = SHED
    kit.box("shed", (4.2, 3.4, 3.6), (sx, sy, 1.8), red, bevel=0.04)
    kit.box("shed.roof", (4.6, 3.8, 0.25), (sx, sy, 3.75), dark, bevel=0.03)
    kit.box("shed.mast", (0.15, 0.15, 0.8), (sx, sy, 4.3), wood)
    kit.cyl("shed.pulley", 0.32, 0.12, (sx, sy - 0.25, 4.7), kit.metal("#8a8d90", 0.4), rot=rot_x90(), n=20)
    kit.box("shed.door", (1.3, 0.08, 2.4), (sx + 2.15, sy - 1.9, 1.3), kit.emit("#ffd18a", 2.0, "shed light"), rot=(0, 0, math.radians(-70)))
    # --- the rope: shed door across the grass to the harness
    rope = kit.plastic("#b79868", 0.9, "rope")
    a, b = V((sx + 1.8, sy - 2.6, 0.04)), V((-1.0, SUN[1] - 2.6, 0.04))
    n = 26
    for i in range(n):
        p0, p1 = a.lerp(b, i / n), a.lerp(b, (i + 1) / n)
        m = (p0 + p1) / 2
        seg = kit.cyl(f"rope{i}", 0.05, (p1 - p0).length * 1.05, tuple(m), rope, n=8)
        seg.rotation_euler = (p1 - p0).to_track_quat("Z", "Y").to_euler()
    for j, zz in enumerate((1.0, 3.2)):   # the harness: loops round the body
        kit.box(f"sun.harn{j}", (5.15, 5.15, 0.14), (0, 0, zz - SUN[2]), rope, root, bevel=0.05)
    # --- lights: the Sun's own warm light on the lawn and on whoever stands near, a cool rim from the dark sky
    kit.light("sunlit", "POINT", (0.0, FRONT - 1.2, 1.9), 900.0, "#ffb347", size=0.9)
    kit.light("sunfill", "AREA", (0.0, FRONT - 3.5, 3.5), 380.0, "#ffc060", rot=(math.radians(-15), 0, 0), size=6.0)
    kit.light("shedlamp", "POINT", (sx + 2.0, sy - 2.4, 1.6), 250.0, "#ffd18a", size=0.5)
    kit.light("rim", "SPOT", (-5.0, 0.5, 5.0), 700.0, "#9fb8ff", size=0.5, spot=60, blend=0.6)
    kit.aim(kit.LIGHTS["rim"]["obj"], (-0.5, 5.5, 1.6))
    for nm, L in kit.LIGHTS.items():
        L["obj"].visible_camera = False
    return ctx


def animate(kit, story, tl, t, ctx):
    breathe = 1.0 + 0.012 * math.sin(2 * math.pi * t / 4.0)
    ctx["root"].scale = (breathe, breathe, breathe)
    # eye opening: the lid's cover slides up with the cue (this still holds it half-open)
    ctx["lid"].location.z = 0.0 + (1.8 - 2.1) + 0.55 + 0.0
    return {}
