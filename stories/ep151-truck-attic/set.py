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
SLEEVE = "#34343c"
HAND = "#6b5a63"
BRASS = "#d8a83a"
PATH = [(2.5, 1.2, 3.62), (2.5, -0.55, 3.56), (2.46, -0.95, 3.0), (2.28, -1.65, 2.5), (2.1, -2.55, 2.02),
        (2.02, -3.6, 1.78)]


def build_arm(kit):
    wool = kit.plastic(SLEEVE, 0.92, spec=0.05)
    skin = kit.plastic(HAND, 0.7, spec=0.1)
    brass = kit.plastic(BRASS, 0.3, spec=0.8)
    t = 0.34
    for a, b in zip(PATH, PATH[1:]):
        seg(a, b, t, wool, "sleeve", 0.04, ext=t * 0.5)
    w = V(PATH[-1])
    # the wide cuff: a fatter, shorter box on the sleeve's end, hanging a little past the wrist
    seg(w + V((0.0, 0.1, 0.0)), w + V((-0.05, -0.28, -0.06)), 0.44, wool, "cuff", 0.05, thick2=0.44)
    # the one big brass button, on the cuff's camera side, 1 cm proud
    bt = kit.cyl(nm("button"), 0.075, 0.05, (w.x - 0.235, w.y - 0.1, w.z - 0.02), brass, None, (0, math.radians(90), 0), n=18)
    # the long flat hand, palm up, resting out toward the camera side: palm then four long flat fingers
    px, py, pz = w.x - 0.1, w.y - 0.45, w.z - 0.2
    B(None, (0.32, 0.5, 0.09), (px, py, pz), skin, "palm", 0.02)
    for i in range(4):
        fx = px - 0.12 + i * 0.08
        B(None, (0.065, 0.62, 0.07), (fx, py - 0.5, pz - 0.005 - 0.004 * (i % 2)), skin, "finger", 0.015)
    B(None, (0.1, 0.4, 0.075), (px + 0.2, py - 0.2, pz - 0.0), skin, "thumb", 0.015, rot=(0, 0, math.radians(-25)))


# ------------------------------------------------------------------------------------------------ the house
def build_house(kit):
    blue, blue2 = P("#9cc8ec", 0.7, 0.1), P("#86b6de", 0.7, 0.1)
    white = P("#d6d1c4", 0.6, 0.1)
    roof = P("#5b5560", 0.8, 0.05)
    dark = P("#120f14", 1.0, 0.0)
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
    kit.cyl(nm("cord"), 0.01, 0.5, (2.5, 2.2, 3.85), dark, None, n=6)
    B(None, (0.1, 0.1, 0.14), (2.5, 2.2, 3.58), kit.emit("#ffe27a", 9.0, name="bulb"), "bulb")
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
    cuff = V(PATH[-1])
    spot = kit.light("cuffsun", "SPOT", (-3.0, -8.0, 6.5), 4200, "#fff0d0", size=0.3, spot=9, blend=0.5)
    kit.aim(spot, (cuff.x - 0.05, cuff.y - 0.1, cuff.z - 0.05))
    kit.light("truckin", "POINT", (3.9, -3.7, 2.7), 90, "#fff2dc", size=0.3, shadow=False)
    # the bulb's glow on the arm root inside the window
    kit.light("bulbglow", "POINT", (2.5, 1.9, 3.7), 12, "#ffd86a", size=0.1)
    # sky fill so the shaded house front stays bright
    fill = kit.light("skyfill", "AREA", (-6.0, -14.0, 8.0), 900, "#dff0ff", size=12.0, shadow=False)
    kit.aim(fill, (2.5, 0.0, 2.5))
    fill.data.size_y = 10
    return {}
