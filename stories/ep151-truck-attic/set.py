"""ep151-truck-attic: one bright summer street, our pale-blue house, and the lodger's arm out of the attic window.

Built here from kit.py's parts (no text anywhere). World (metres, z up, the house front faces -y):
- OUR HOUSE: main block x -7..0, the garage wing x 0..5 with a front gable; its attic window is a hole in the gable wall
  at x 2.5, z 3.15..4.05, a dark closed pocket behind it with one steady bare bulb far back (the camera never goes in).
- THE TRUCK: mint and white, boxy, in the driveway nose to the garage (x 2.6..4.8, y -1.2..-6.0), a serving hatch in
  its -x side at y -3.7, an awning over it. The ice cream man (cast) stands inside at the hatch.
- THE ARM: the lodger's charcoal coat sleeve, built from boxes along a path from the window, over the gutter, down to
  the hatch, ending in a wide cuff with a brass button and a long flat palm-up hand. Never a face.
Light: afternoon sun from behind the house (the arm's camera side stays in shade, a hard rim on its top edge), a narrow
spot on the cuff only (the one lit identity cue), sky fill for the bright summer look.
"""
from __future__ import annotations

import math

import bpy
from mathutils import Vector as V

_n = [0]


def nm(p):
    _n[0] += 1
    return f"{p}.{_n[0]}"


class K:
    kit = None


def P(h, rough=0.5, spec=0.3):
    return K.kit.plastic(h, rough, spec=spec)


def B(parent, size, loc, mat, name="b", bevel=0.0, rot=(0, 0, 0)):
    return K.kit.box(nm(name), size, loc, mat, parent, rot, bevel)


def seg(p, q, thick, mat, name="seg", bevel=0.03, ext=0.0, thick2=None):
    """A box from p to q (its long axis along p->q), extended ext at both ends so bends close without gaps."""
    a, b = V(p), V(q)
    d = b - a
    L = d.length
    ob = K.kit.box(nm(name), (thick, thick2 or thick, L + 2 * ext), (a + b) / 2, mat, None, (0, 0, 0), bevel)
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return ob


def wall_with_hole(x0, x1, z0, z1, hx0, hx1, hz0, hz1, y, th, mat, name):
    """A wall slab (x0..x1, z0..z1) at y with a rectangular hole, as four boxes."""
    def part(a0, a1, b0, b1):
        if a1 - a0 < 1e-4 or b1 - b0 < 1e-4:
            return
        B(None, (a1 - a0, th, b1 - b0), ((a0 + a1) / 2, y, (b0 + b1) / 2), mat, name)
    part(x0, hx0, z0, z1)
    part(hx1, x1, z0, z1)
    part(hx0, hx1, z0, hz0)
    part(hx0, hx1, hz1, z1)


# ------------------------------------------------------------------------------------------------ the arm
SLEEVE = "#5d5d6a"
SLEEVE2 = "#4a4a56"
HAND = "#b9a2d4"
BRASS = "#8c7438"
PATH = [(2.5, 1.2, 3.55), (2.5, -0.6, 3.5), (2.47, -1.0, 3.05), (2.3, -1.7, 2.55), (2.12, -2.6, 2.2),
        (2.02, -3.55, 2.02), (2.02, -3.7, 1.8)]


def oct_seg(p, q, t, mat, name, bevel=0.06, ext=0.0):
    """A rounder limb: the same box drawn twice, turned 45 degrees about its axis (an octagon section)."""
    from mathutils import Quaternion
    a, b = V(p), V(q)
    d = b - a
    q0 = d.to_track_quat("Z", "Y")
    for roll in (0.0, math.radians(45)):
        ob = K.kit.box(nm(name), (t, t, d.length + 2 * ext), (a + b) / 2, mat, None, (0, 0, 0), bevel)
        ob.rotation_euler = (q0 @ Quaternion((0, 0, 1), roll)).to_euler()


def finger(base, dirs, lens, th, mat):
    """A finger of several joints: each joint a box along its direction, bending as dirs says."""
    pt = V(base)
    for d, ln in zip(dirs, lens):
        d = V(d).normalized()
        e = pt + d * ln
        seg(pt, e, th, mat, "finger", 0.02, ext=th * 0.4)
        pt = e
        th *= 0.9
    return pt


def build_arm(kit):
    wool = kit.plastic(SLEEVE, 0.95, spec=0.03)
    wool2 = kit.plastic(SLEEVE2, 0.95, spec=0.03)
    band = kit.plastic("#8d8a9c", 0.9, spec=0.03)
    skin = kit.plastic(HAND, 0.6, spec=0.15)
    brass = kit.plastic(BRASS, 0.8, spec=0.1)
    t = 0.3
    for a, b in zip(PATH, PATH[1:]):
        oct_seg(a, b, t, wool, "sleeve", 0.07, ext=t * 0.4)
    # creases: thin, slightly fatter rings across the sleeve, turned about the axis, darker wool
    for i, (a, b) in enumerate(zip(PATH[:-1], PATH[1:])):
        A, Bv = V(a), V(b)
        d = (Bv - A).normalized()
        n = max(2, int((Bv - A).length / 0.5))
        for k in range(1, n):
            c = A + (Bv - A) * (k / n)
            oct_seg(c - d * 0.035, c + d * 0.035, t + 0.03, wool2, "fold", 0.04)
    # the elbow where it bends over the gutter: a fat knuckle of cloth
    e = V(PATH[2])
    oct_seg(e + V((0, 0.12, 0.12)), e + V((0, -0.1, -0.1)), t + 0.1, wool, "elbow", 0.1)
    # the soft turned-back cuff band at the wrist (round-ish, lighter), and the dark sleeve mouth under it
    w = V(PATH[-1])
    oct_seg(w + V((0, 0, 0.1)), w + V((0, 0, -0.05)), 0.4, band, "cuff", 0.09)
    oct_seg(w + V((0, 0, -0.05)), w + V((0, 0, -0.12)), 0.31, wool2, "mouth", 0.05)
    # a small matte button on the cuff's camera side
    kit.cyl(nm("button"), 0.04, 0.03, (w.x - 0.2, w.y - 0.02, w.z + 0.04), brass, None, (0, math.radians(90), 0), n=14)
    # the hand: pale dusky lilac, hanging limp from the wrist, palm toward us, four long separate fingers + thumb
    hx, hy = w.x - 0.02, w.y
    top = w.z - 0.12
    B(None, (0.12, 0.3, 0.3), (hx, hy, top - 0.15), skin, "palm", 0.03)
    for i in range(4):
        fy = hy + 0.115 - i * 0.077
        ln = (0.26, 0.3, 0.28, 0.2)[i]
        finger((hx - 0.01, fy, top - 0.28),
               [(-0.05 * (i - 1.5), -0.1, -1.0), (0.0, -0.45, -0.9), (0.0, -0.85, -0.5)], (ln, 0.2, 0.16), 0.06, skin)
    finger((hx - 0.01, hy + 0.17, top - 0.12), [(0.0, 0.8, -0.35), (0.0, 0.9, -0.4)], (0.17, 0.15), 0.07, skin)


# ------------------------------------------------------------------------------------------------ the house
def build_house(kit):
    blue, blue2 = P("#9cc8ec", 0.7, 0.1), P("#86b6de", 0.7, 0.1)
    white = P("#d6d1c4", 0.6, 0.1)
    roof = P("#5b5560", 0.8, 0.05)
    dark = P("#000000", 1.0, 0.0)
    # main block (two storeys) left of the garage
    B(None, (7.05, 8.0, 5.6), (-3.5, 4.0, 2.8), blue, "main")
    B(None, (7.6, 8.6, 0.35), (-3.5, 4.0, 5.75), roof, "mainroof")
    for x in (-5.3, -2.0):
        for z, h in ((1.7, 1.1), (4.0, 1.1)):
            if x == -2.0 and z == 1.7:
                continue
            B(None, (1.2, 0.06, h), (x, -0.03, z), P("#f2efe6", 0.5), "winfr")
            B(None, (1.0, 0.07, h - 0.2), (x, -0.045, z), kit.glass("#bfe2ff"), "pane")
    B(None, (1.1, 0.07, 2.2), (-2.0, -0.04, 1.1), P("#c0485a", 0.5), "door")     # front door
    B(None, (2.0, 1.0, 0.12), (-2.0, -0.5, 0.06), P("#cfcabd", 0.8), "step")
    # garage wing: wall below the gutter, then the gable wall with the attic window hole
    B(None, (5.0, 0.2, 2.75), (2.5, 0.1, 1.375), white, "garagewall")
    B(None, (4.0, 0.06, 2.3), (2.5, -0.04, 1.2), P("#c4bfb2", 0.6, 0.1), "garagedoor")
    for z in (0.5, 1.1, 1.7):
        B(None, (4.0, 0.075, 0.04), (2.5, -0.045, z), P("#a39e92", 0.6), "doorgroove")
    B(None, (5.5, 0.34, 0.2), (2.5, -0.15, 2.82), white, "gutter")                  # the gutter / fascia the sleeve bends over
    hx0, hx1, hz0, hz1 = 2.0, 3.0, 3.15, 4.05
    wall_with_hole(0.0, 5.0, 2.9, 4.7, hx0, hx1, hz0, hz1, 0.1, 0.2, blue, "gablewall")
    # the gable triangle above, a prism
    v = [(0, 0, 4.7), (5, 0, 4.7), (2.5, 0, 5.95), (0, 0.2, 4.7), (5, 0.2, 4.7), (2.5, 0.2, 5.95)]
    f = [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)]
    kit.mesh_obj(nm("gable"), v, f, blue, None, (0, 0, 0))
    # garage body behind the wall, roof slabs with an overhang
    B(None, (5.0, 8.0, 2.75), (2.5, 4.2, 1.375), white, "garagebody")
    ang = math.atan2(5.95 - 4.7, 2.5)
    L = math.hypot(2.5, 1.25) + 0.45
    for s in (-1, 1):
        B(None, (L, 8.8, 0.14), (2.5 + s * 1.3, 4.1, 5.35), roof, "garroof", 0.0, rot=(0, s * ang, 0))
    B(None, (5.0, 7.6, 1.95), (2.5, 4.6, 3.72), blue2, "garattic")
    # the window frame (proud of the wall) and the dark closed pocket behind
    fr = P("#e6e2d6", 0.5, 0.1)
    for (sx, sy, cx, cz) in ((1.16, 0.08, 2.5, hz1 + 0.04), (1.16, 0.08, 2.5, hz0 - 0.04),
                             (0.08, 0.98, hx0 - 0.04, 3.6), (0.08, 0.98, hx1 + 0.04, 3.6)):
        B(None, (sx, 0.1, sy), (cx, -0.07, cz), fr, "winframe")
    B(None, (1.14, 0.02, 0.06), (2.5, -0.13, hz0 - 0.1), fr, "sill")
    cx, cy, cz = 2.5, 1.5, 3.6
    for size, loc in (((1.0, 0.1, 1.0), (2.5, 2.7, 3.6)), ((0.1, 2.5, 1.0), (1.96, 1.45, 3.6)), ((0.1, 2.5, 1.0), (3.04, 1.45, 3.6)),
                      ((1.2, 2.5, 0.1), (2.5, 1.45, 4.1)), ((1.2, 2.5, 0.1), (2.5, 1.45, 3.1))):
        B(None, size, loc, dark, "pocket")
    # (no bulb: the pocket is pitch black)
    # kit.cyl(nm("cord"), 0.01, 0.5, (2.5, 2.2, 3.85), dark, None, n=6)
    return None


def build_truck(kit):
    mint, white = P("#9fe6c8", 0.35, 0.5), P("#e8e8e0", 0.4, 0.3)
    dark = P("#2a2a30", 0.8, 0.1)
    cream = P("#f2e8d0", 0.7, 0.1)
    x0, x1 = 2.6, 4.8
    xc = (x0 + x1) / 2
    # chassis and wheels
    B(None, (2.0, 4.6, 0.3), (xc, -3.6, 0.4), dark, "chassis")
    for y in (-2.0, -5.2):
        for x in (x0 + 0.05, x1 - 0.05):
            kit.cyl(nm("wheel"), 0.42, 0.28, (x, y, 0.42), dark, None, (0, math.radians(90), 0), n=18)
    # the cab at the nose (y -1.2..-2.4)
    B(None, (2.2, 1.3, 1.5), (xc, -1.85, 1.2), mint, "cab", 0.05)
    B(None, (2.0, 0.06, 0.7), (xc, -1.19, 1.5), kit.glass("#bfe2ff"), "windscreen")
    # the cargo box (y -2.4..-6.0, z 0.55..3.1): floor, roof, back, front, +x side, and the -x side with the hatch hole
    th = 0.1
    B(None, (2.2, 3.6, th), (xc, -4.2, 0.6), cream, "floor")
    B(None, (2.2, 3.6, th), (xc, -4.2, 3.1), white, "boxroof", 0.03)
    B(None, (2.2, th, 2.5), (xc, -6.0, 1.85), mint, "boxback", 0.02)
    B(None, (2.2, th, 2.5), (xc, -2.45, 1.85), cream, "boxfront")
    B(None, (th, 3.6, 2.5), (x1, -4.2, 1.85), mint, "boxside", 0.02)
    return xc


def build_truck_side(kit, x0):
    """The -x side wall of the box with the serving hatch hole (y -4.4..-3.0, z 1.3..2.5), an awning and counter."""
    mint = P("#9fe6c8", 0.35, 0.5)
    th = 0.1

    def part(y0, y1, z0, z1):
        B(None, (th, y1 - y0, z1 - z0), (x0, (y0 + y1) / 2, (z0 + z1) / 2), mint, "boxside", 0.0)
    part(-6.0, -4.4, 0.55, 3.1)
    part(-3.0, -2.4, 0.55, 3.1)
    part(-4.4, -3.0, 0.55, 1.3)
    part(-4.4, -3.0, 2.5, 3.1)
    B(None, (0.5, 1.5, 0.06), (x0 - 0.2, -3.7, 1.3), P("#e8e8e0", 0.4), "counter")
    red, white = P("#e8445a", 0.6), P("#f2f2ee", 0.6)
    for i in range(6):
        y = -4.45 + i * 0.3
        B(None, (0.8, 0.3, 0.05), (x0 - 0.45, y + 0.15, 2.75 - 0.18), red if i % 2 else white, "awn", 0.0,
          rot=(0, math.radians(-25), 0))
    # an ice pop glyph on the box side
    B(None, (0.03, 0.3, 0.6), (x0 - 0.06, -5.3, 1.9), P("#ff9a2a", 0.5), "popglyph")
    B(None, (0.03, 0.08, 0.3), (x0 - 0.06, -5.3, 1.45), P("#e8e8e0", 0.5), "popstick")


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    K.kit = kit
    sc = bpy.context.scene
    # ground
    B(None, (200, 160, 0.4), (0, -50, -0.2), P("#62c45a", 0.9, 0.05), "lawn")
    B(None, (4.0, 8.4, 0.08), (3.5, -4.4, 0.02), P("#a9a49b", 0.85, 0.05), "drive")
    B(None, (40, 7.0, 0.1), (0, -16.0, 0.03), P("#4a4c54", 0.9, 0.05), "road")
    B(None, (40, 2.0, 0.12), (0, -11.5, 0.05), P("#c8c6c0", 0.8), "walk")
    # neighbour (Mrs. Lee's, pale yellow) and a tree or two
    B(None, (7.0, 8.0, 5.0), (11.5, 3.0, 2.5), P("#f4dc8a", 0.7, 0.1), "lee")
    B(None, (7.6, 8.6, 0.3), (11.5, 3.0, 5.15), P("#7a4b46", 0.8), "leeroof")
    for nme, x, y, h in (("commontree_1", -9.0, -7.0, 6.5), ("commontree_2", 9.5, -8.0, 7.0), ("birchtree_1", 15.0, -9.0, 7.5)):
        try:
            kit.prop(nme, (x, y, 0), rot=37 * x, height=h, tint="#8fe05a")
        except Exception:
            pass
    build_house(kit)
    build_truck(kit)
    build_truck_side(kit, 2.6)
    build_arm(kit)
    # light: the sun is behind the house (from +y, a little from -x), high, so fronts are in sky-lit shade
    sun = kit.light("sun", "SUN", (0, 0, 50), 4.2, "#fff1d8", size=0.1)
    sun.data.angle = 0.05
    el, az = math.radians(60), math.radians(-18)
    to_sun = V((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    sun.rotation_euler = (-to_sun).to_track_quat("-Z", "Y").to_euler()
    # the cuff in sun: a narrow warm spot from the front, only on the cuff and button
    cuff = V(PATH[-1]) + V((0, 0, -0.35))
    spot = kit.light("cuffsun", "SPOT", (-3.0, -8.0, 6.5), 4200, "#fff0d0", size=0.3, spot=9, blend=0.5)
    kit.aim(spot, (cuff.x - 0.05, cuff.y - 0.1, cuff.z - 0.05))
    kit.light("truckin", "POINT", (3.9, -3.7, 2.7), 90, "#fff2dc", size=0.3, shadow=False)
    # the bulb's glow on the arm root inside the window
    # sky fill so the shaded house front stays bright
    fill = kit.light("skyfill", "AREA", (-6.0, -14.0, 8.0), 900, "#dff0ff", size=12.0, shadow=False)
    kit.aim(fill, (2.5, 0.0, 2.5))
    fill.data.size_y = 10
    return {}
