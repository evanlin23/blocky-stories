"""The drive-in: a lot of big old blocky cars facing one huge screen, a projector beam with soft dust, and five small
rooms far off for the montage (a bar table, a harbour rail, a cafe table, a sofa, a late office).

Coordinates (metres, z up): the lot's rows run along y (row 1 at y = 0, row 4 at y = -21, the booth at y = -56), the
screen stands at y = +48, the aisle with the beam is x = 0, and every car faces +y. Seated people face +y (yaw 180).
The rooms stand at x = 300 (bar), 400 (harbour), 500 (cafe), 600 (sofa) and 700 (office).

THE MARKER over every head is a flat gold oval ring with a black cut-out silhouette inside it (our own shapes, made of
polygons). It floats a hand above the head and always turns to face the camera. Theo's cut-out fades by beat.

THE CREATURE (the Unlit) is an ordinary R6 person, a whole head too tall, every surface a matte black no light lands
on. A thin cool rim comes from a fresnel glow in its own materials and two small glints sit on its face; it throws no
shadow and carries no marker. It is posed only by the acting (hidden, standing, seated), so it is never seen moving.

Every light change is a slow fade (look.flash_safe): the beam, the screen, the reel running out, the ring filling in.
Cues read here: env (the lighting preset), beam (v, dur), ring (v, dur), shadow (who, on, rise / turn), door (car,
side, open, dur), roll, tub (slide), cap (on), turn (who, deg).
"""

from __future__ import annotations

import math
from mathutils import Euler
import random
import sys

import bpy
from mathutils import Vector

from blocky import acting as acting_mod

SCREEN_Y = 48.0
SCREEN_W, SCREEN_H, SCREEN_Z0 = 26.0, 14.6, 1.4
BOOTH = (0.0, -56.0)
GOLD = "#ffcf5a"
MARK_M = 0.62            # a marker's unit, in metres
CHAR_TOP = 1.775         # the head top of a standing 1.0 person
V = Vector

# ---- lighting presets, applied per shot (a cut): sun gain/colour/direction, the world's top and horizon colours
# and strength, the screen's brightness, the screen light, a fill light, the car dash glows
ENV = {
    "gold": dict(sun=(1.0, "#ffb26b", (40, 12, 14)), zen="#4a3866", hor="#f2a65a", wstr=1.0, screen=0.9,
                 scl=0.0, fill=0.25, dash=0.0),
    "bar": dict(sun=(0.0, "#ffb26b", (40, -30, 16)), zen="#2a1c1a", hor="#3a2a22", wstr=0.35, screen=0.0, scl=0.0,
                fill=0.0, dash=0.0),
    "harbour": dict(sun=(0.55, "#ff9a60", (-30, -40, 6)), zen="#3a2a55", hor="#e08a5a", wstr=0.9, screen=0.0,
                    scl=0.0, fill=0.1, dash=0.0),
    "cafe": dict(sun=(0.0, "#ffb26b", (40, -30, 16)), zen="#40302a", hor="#6a4a38", wstr=0.5, screen=0.0, scl=0.0,
                 fill=0.05, dash=0.0),
    "sofa": dict(sun=(0.0, "#ffb26b", (40, -30, 16)), zen="#2a2a3a", hor="#3a3040", wstr=0.35, screen=0.0, scl=0.0,
                 fill=0.0, dash=0.0),
    "office": dict(sun=(0.0, "#ffb26b", (40, -30, 16)), zen="#10141f", hor="#1a2030", wstr=0.35, screen=0.0, scl=0.0,
                   fill=0.0, dash=0.0),
    "office_five": dict(sun=(0.0, "#ffb26b", (40, -30, 16)), zen="#6a5a7a", hor="#e8a068", wstr=0.9, screen=0.0,
                        scl=0.0, fill=0.05, dash=0.0),
    "night1": dict(sun=(0.0, "#9bb0ff", (40, -30, 16)), zen="#0a1a4a", hor="#2c5cb4", wstr=0.30, screen=1.0, scl=0.20,
                   fill=0.0, dash=1.0, bsp=0.16, gnd="#26385e", lamp=0.5),
    "night2": dict(sun=(0.0, "#9bb0ff", (40, -30, 16)), zen="#08143a", hor="#244c98", wstr=0.24, screen=1.0, scl=0.16,
                   fill=0.0, dash=1.0, bsp=0.13, gnd="#1d2d4e", lamp=0.5),
    "night3": dict(sun=(0.0, "#9bb0ff", (40, -30, 16)), zen="#060f30", hor="#1c3c7c", wstr=0.19, screen=1.0, scl=0.12,
                   fill=0.0, dash=1.0, bsp=0.10, gnd="#16233f", lamp=0.5),
    "night4": dict(sun=(0.0, "#9bb0ff", (40, -30, 16)), zen="#050c26", hor="#16306a", wstr=0.15, screen=1.0, scl=0.09,
                   fill=0.0, dash=1.0, bsp=0.08, gnd="#111c34", lamp=0.5),
    "warm": dict(sun=(0.0, "#9bb0ff", (40, -30, 16)), zen="#060f30", hor="#0c2250", wstr=0.20, screen=1.0, scl=0.14,
                 fill=0.0, dash=1.6, bsp=0.12, gnd="#16233f", lamp=0.6),
}
PAINT = {"C": "#e8dcc0", "T": "#3b7d7a", "B": "#9a4a3a"}
# (x, y, paint). Theo's cream car is row 1 at x = 3.4, mine the teal one in row 4. Columns 3.4 in rows 2, 3 and 5
# to 7 stay empty so my view of Theo's car (and the back of the lot) is clear.
CARS = [(-3.4, 0.0, "B"), (13.4, 0.0, "T"), (-8.4, 0.0, "C"),
        (-3.4, -7.0, "C"), (-8.4, -7.0, "B"),
        (-8.4, -14.0, "T"), (-3.4, -14.0, "C"),
        (-13.4, -21.0, "B"), (8.4, -21.0, "C"),
        (-3.4, -28.0, "C"), (8.4, -28.0, "T"), (-8.4, -28.0, "B"), (13.4, -28.0, "C"),
        (-3.4, -35.0, "T"), (8.4, -35.0, "C"), (-8.4, -35.0, "C"),
        (-3.4, -42.0, "B"), (8.4, -42.0, "C"), (-8.4, -42.0, "T")]
NAMED = {"theo": (3.4, 0.0, "C"), "me": (3.4, -21.0, "T")}


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return sorted((c for c in tl["cues"] if c["name"] == name), key=lambda c: c["t"])


def _shot(tl, t):
    return next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])


def _ramp(cues, t, key, default, dur_key="dur"):
    """A value that eases from its last value to a cue's value over the cue's dur (a slow fade, never a snap)."""
    v = default
    for c in cues:
        if c["t"] <= t + 1e-9:
            d = c.get(dur_key, 0.0)
            tgt = c[key]
            v = tgt if d <= 0 else v + (tgt - v) * _ss((t - c["t"]) / d)
        else:
            break
    return v


# ======================================================================================================= materials
def alpha_mat(kit, name, hexc, alpha, rough=0.3):
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Alpha"].default_value = alpha
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = 0.0
            break
    kit._fogged(m, b.outputs[0])
    return m


def flat_emit(kit, name, hexc, strength):
    """Plain emission, no fog (markers, the screen)."""
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = strength
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    return m, e


def fade_emit(kit, name, hexc):
    """Emission mixed with transparency by a factor the story sets (a cut-out, a shadow, the beam)."""
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = 1.0
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs[0].default_value = 1.0
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(e.outputs[0], mx.inputs[2])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return m, e, mx


def poly(kit, name, pts, mat, parent, y=0.0):
    verts = [(x, y, z) for x, z in pts]
    return kit.mesh_obj(name, verts, [tuple(range(len(pts)))], mat, parent)


def circle(cx, cz, r, n=24, sx=1.0):
    return [(cx + sx * r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def ellipse_band(cx, cz, rx, rz, w, n=40):
    """The ring: quads between an outer and an inner ellipse."""
    return [([(cx + rx * math.cos(a0), cz + rz * math.sin(a0)), (cx + rx * math.cos(a1), cz + rz * math.sin(a1)),
              (cx + (rx - w) * math.cos(a1), cz + (rz - w) * math.sin(a1)),
              (cx + (rx - w) * math.cos(a0), cz + (rz - w) * math.sin(a0))])
            for a0, a1 in ((2 * math.pi * i / n, 2 * math.pi * (i + 1) / n) for i in range(n))]


SHOULDERS = [(-0.85, -0.95), (0.85, -0.95), (0.8, -0.5), (0.5, -0.22), (0.17, -0.08), (0.17, 0.12), (-0.17, 0.12),
             (-0.17, -0.08), (-0.5, -0.22), (-0.8, -0.5)]
HEAD = circle(0, 0.38, 0.36)
CROWN = [(0.42 * math.cos(math.pi * i / 12), 0.5 + 0.36 * math.sin(math.pi * i / 12)) for i in range(13)]


def sil_shapes(kind):
    """The cut-out as polygons in the x-z plane, roughly -1..1: head and shoulders, plus what marks the person."""
    base = [SHOULDERS, HEAD]
    if kind in ("cap", "cap_tuft"):
        base += [CROWN, [(-0.40, 0.58), (-0.93, 0.52), (-0.93, 0.44), (-0.4, 0.44)]]
        if kind == "cap_tuft":      # the tuft pokes out under the back of the cap
            base += [[(0.2, 0.7), (0.4, 1.22), (0.5, 0.66), (0.4, 0.5)]]   # up and back, like Theo's tuft in S12
    elif kind == "bride":
        base = [[(0.0, 1.0), (0.3, 0.85), (0.78, -0.3), (0.92, -0.95), (-0.92, -0.95), (-0.78, -0.3), (-0.3, 0.85)],
                HEAD, [(-0.3, 0.7), (-0.15, 0.98), (0.0, 0.8), (0.15, 0.98), (0.3, 0.7)]]
    elif kind == "dog":
        base = [[(-0.75, -0.25), (0.45, -0.25), (0.45, 0.2), (-0.75, 0.2)],                 # body
                [(0.35, 0.05), (0.62, 0.05), (0.62, 0.5), (0.35, 0.5)], [(0.6, 0.05), (0.95, 0.05), (0.95, 0.28), (0.6, 0.28)],
                [(0.38, 0.45), (0.5, 0.45), (0.46, 0.78), (0.36, 0.78)],                    # ear
                [(-0.75, -0.25), (-0.55, -0.25), (-0.55, -0.85), (-0.75, -0.85)], [(0.25, -0.25), (0.45, -0.25), (0.45, -0.85), (0.25, -0.85)],
                [(-0.8, 0.0), (-0.95, 0.5), (-0.82, 0.55), (-0.65, 0.1)]]                   # tail
    elif kind == "quiff":
        base += [[(-0.36, 0.62), (-0.18, 1.02), (0.32, 1.1), (0.58, 0.86), (0.3, 0.68)]]
    elif kind == "long":
        base += [[(0.52 * math.cos(math.pi * i / 12), 0.42 + 0.5 * math.sin(math.pi * i / 12)) for i in range(13)]
                 + [(-0.56, -0.55), (0.56, -0.55)]]
    elif kind == "bob":
        base += [[(0.5 * math.cos(math.pi * i / 12), 0.42 + 0.46 * math.sin(math.pi * i / 12)) for i in range(13)]
                 + [(-0.5, 0.0), (0.5, 0.0)]]
    elif kind == "spiky":
        base += [[(0.44 * math.cos(math.pi * i / 10), 0.42 + 0.44 * math.sin(math.pi * i / 10) + (0.1 if i % 2 else 0.0))
                  for i in range(11)]]
    elif kind == "short":
        base += [[(-0.38, 0.5), (-0.3, 0.8), (0.3, 0.8), (0.38, 0.5)]]
    return base


MARK_KIND = {"me": "cap_tuft", "theo": "cap", "dev": "bride", "mate1": "long", "mate2": "spiky", "sailor": "dog",
             "cafe_woman": "quiff", "cafe_date": "long", "sofa_woman": "short", "bg1": "spiky", "bg2": "long",
             "bg3": "quiff", "bg4": "bob", "bg5": "long", "bg6": "spiky"}


# ======================================================================================================= the lot
def box(kit, name, size, loc, mat, parent, bevel=0.0, rot=(0, 0, 0)):
    return kit.box(name, size, loc, mat, parent, rot=rot, bevel=bevel)


def build_car(kit, name, x, y, paint, near, ctx):
    """An old wide blocky car: a bench seat for two big riders (interior 3.4 m), open windows, doors that swing."""
    bev = 0.05 if near else 0.0
    root = kit.empty(f"car.{name}", (x, y, 0))
    body = kit.plastic(PAINT[paint], 0.5)
    dark = kit.plastic("#26262b", 0.7)
    trim = kit.metal("#9a9da0", 0.4)
    seatm = kit.plastic("#6a3a2c", 0.8)
    glass = alpha_mat(kit, "windscreen", "#aabbc0", 0.12)
    box(kit, f"{name}.floor", (3.5, 5.8, 0.12), (0, 0, 0.26), dark, root)
    box(kit, f"{name}.hood", (3.7, 1.8, 0.8), (0, 2.0, 0.7), body, root, bev)
    box(kit, f"{name}.hoodtop", (3.5, 1.7, 0.08), (0, 2.0, 1.12), body, root, bev)
    box(kit, f"{name}.trunk", (3.7, 1.4, 0.8), (0, -2.2, 0.7), body, root, bev)
    box(kit, f"{name}.trunktop", (3.5, 1.3, 0.08), (0, -2.2, 1.12), body, root, bev)
    box(kit, f"{name}.dash", (3.4, 0.4, 0.75), (0, 1.0, 0.68), dark, root)
    box(kit, f"{name}.shelf", (3.4, 0.5, 0.78), (0, -1.4, 0.69), body, root)
    box(kit, f"{name}.bumpf", (3.8, 0.22, 0.2), (0, 3.0, 0.45), trim, root, bev)
    box(kit, f"{name}.bumpb", (3.8, 0.22, 0.2), (0, -3.0, 0.45), trim, root, bev)
    for sx in (-1, 1):
        box(kit, f"{name}.lamp{sx}", (0.45, 0.1, 0.4), (sx * 1.25, 2.93, 0.78), kit.plastic("#8a8a80", 0.4), root, bev)
        for sy in (-1, 1):
            w = kit.cyl(f"{name}.wheel{sx}{sy}", 0.5, 0.3, (sx * 1.75, sy * 1.75, 0.5), dark, root, rot=(0, math.pi / 2, 0))
        box(kit, f"{name}.Apil{sx}", (0.14, 0.2, 1.0), (sx * 1.78, 1.28, 1.6), body, root, bev)
        box(kit, f"{name}.Cpil{sx}", (0.16, 0.5, 1.0), (sx * 1.76, -1.55, 1.6), body, root, bev)
    box(kit, f"{name}.roof", (3.7, 3.4, 0.1), (0, -0.15, 2.1), body, root, bev)
    roof = bpy.data.objects[f"{name}.roof"]
    # glass: a faint windscreen and rear window
    # the bench: a seat and a back, brown vinyl
    box(kit, f"{name}.cushion", (3.2, 0.95, 0.22), (0, -0.05, 0.44), seatm, root, 0.04)
    box(kit, f"{name}.back", (3.2, 0.2, 0.95), (0, -0.62, 0.98), seatm, root, 0.04)
    doors = {}
    for sx in (-1, 1):
        hinge = kit.empty(f"{name}.hinge{sx}", (sx * 1.85, 1.2, 0), root)
        box(kit, f"{name}.dpanel{sx}", (0.14, 2.7, 0.8), (0, -1.35, 0.7), body, hinge, bev)
        box(kit, f"{name}.dtop{sx}", (0.14, 2.7, 0.1), (0, -1.35, 2.05), body, hinge, bev)
        box(kit, f"{name}.dfront{sx}", (0.14, 0.12, 0.95), (0, -0.06, 1.55), body, hinge)
        box(kit, f"{name}.drear{sx}", (0.14, 0.12, 0.95), (0, -2.64, 1.55), body, hinge)
        doors[sx] = hinge
    sp = None
    if near:
        # the old speaker box hooked over the driver window's edge, with a grille
        hinge = doors[-1]
        sm = kit.plastic("#b4b8bc", 0.5)
        box(kit, f"{name}.spk", (0.34, 0.5, 0.52), (-0.02, -1.0, 1.15), sm, hinge, 0.03)
        box(kit, f"{name}.spkgrille", (0.04, 0.38, 0.14), (-0.2, -1.0, 1.28), kit.plastic("#2a2c2e", 0.7), hinge)
        box(kit, f"{name}.spkhook", (0.2, 0.06, 0.06), (0.0, -1.0, 1.43), sm, hinge)
        if name == "theo":      # the lore plant: two short soot-black tally strokes pressed into the metal face
            sootm = kit.plastic("#050505", 0.9)
            for dy in (-0.07, 0.07):
                box(kit, f"{name}.tally{dy}", (0.03, 0.05, 0.2), (-0.2, -1.0 + dy, 1.05), sootm, hinge)
    ctx["cars"][name] = {"root": root, "doors": doors, "roof": roof, "x": x, "y": y}
    return root


def build_lot(kit, ctx):
    ground = kit.grime("#6a6460", 0.6, 1.6)
    kit.plane("ground", (2400, 500), (400, -100, 0), ground)
    ctx["gnd"] = [n for n in ground.node_tree.nodes if n.type == "VALTORGB"]
    # screen: a frame, posts, an emissive face whose colour drifts
    dark = kit.plastic("#1d1c22", 0.8)
    kit.box("screen.frame", (SCREEN_W + 1.2, 0.5, SCREEN_H + 1.2), (0, SCREEN_Y + 0.35, SCREEN_Z0 + SCREEN_H / 2), dark)
    for sx in (-8, 0, 8):
        kit.box(f"screen.post{sx}", (0.8, 0.8, SCREEN_Z0 + 0.5), (sx, SCREEN_Y + 0.5, (SCREEN_Z0) / 2), dark)
    m = kit._new("screen face")
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.22
    nz.inputs["Detail"].default_value = 1.0
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = kit.col("#8aa4d8")
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = kit.col("#f0b070")
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    face = kit.plane("screen.face", (SCREEN_W, SCREEN_H), (0, SCREEN_Y, SCREEN_Z0 + SCREEN_H / 2), m, rot=(math.pi / 2, 0, 0))
    ctx["screen"] = {"em": em, "map": mp, "obj": face}
    # the booth, with a lit lamp behind the back of the lot
    bm = kit.plastic("#3a3a40", 0.8)
    kit.box("booth", (5.0, 4.0, 3.4), (BOOTH[0], BOOTH[1] - 2.5, 1.7), bm)
    kit.box("booth.roof", (5.6, 4.6, 0.2), (BOOTH[0], BOOTH[1] - 2.5, 3.5), kit.plastic("#2a2a30", 0.8))
    kit.box("booth.port", (0.8, 0.1, 0.5), (BOOTH[0], BOOTH[1] - 0.45, 1.2), kit.emit("#dfe6f2", 2.0), None)
    for sx in (-1, 1):
        kit.cyl(f"lamp.pole{sx}", 0.07, 5.0, (sx * 8.0, -52.0, 2.5), dark)
        lm = kit.emit("#ffc890", 6.0)
        kit.box(f"lamp.head{sx}", (0.5, 0.5, 0.2), (sx * 8.0, -52.0, 5.0), lm)
    kit.light("lampA", "POINT", (8.0, -52.0, 4.8), 1200.0, "#ffbb77", size=0.4)
    kit.light("lampB", "POINT", (-8.0, -52.0, 4.8), 600.0, "#ffbb77", size=0.4)
    # a low snack bar and a fence and dark trees round the lot
    kit.box("snack", (10.0, 6.0, 3.6), (-30.0, -14.0, 1.8), kit.plastic("#5b4f45", 0.8))
    kit.box("snack.roof", (11.0, 7.0, 0.3), (-30.0, -14.0, 3.7), kit.plastic("#3a332e", 0.8))
    kit.box("snack.win", (6.0, 0.1, 1.0), (-30.0, -10.95, 2.0), kit.emit("#ffcf8a", 2.0))
    rnd = random.Random(38)
    tm = kit.plastic("#0e1a14", 0.9)
    for i in range(46):
        side = -1 if i % 2 else 1
        tx = side * rnd.uniform(24, 60)
        ty = rnd.uniform(-60, 52)
        h = rnd.uniform(5, 11)
        kit.box(f"tree{i}", (rnd.uniform(3, 5), rnd.uniform(3, 5), h), (tx, ty, h / 2), tm)
    fm = kit.plastic("#2b2b30", 0.8)
    for sx in (-1, 1):
        kit.box(f"fence{sx}", (0.2, 140.0, 2.2), (sx * 22.0, -4.0, 1.1), fm)
    kit.box("fence.back", (44.0, 0.2, 2.2), (0, -58.5, 1.1), fm)
    # speaker poles between the cars
    pm = kit.metal("#7b7e80", 0.5)
    for ry in (0.0, -7.0, -14.0, -21.0, -28.0, -35.0, -42.0):
        for px in (-11.0, -5.9, 5.9, 10.9):
            kit.cyl(f"pole{px}{ry}", 0.06, 1.3, (px, ry + 0.3, 0.65), pm)
            kit.box(f"pbox{px}{ry}", (0.3, 0.14, 0.34), (px, ry + 0.3, 1.2), kit.plastic("#4a4d50", 0.6))
    # cars
    ctx["cars"] = {}
    for n, (cx, cy, p) in NAMED.items():
        build_car(kit, n, cx, cy, p, True, ctx)
    for i, (cx, cy, p) in enumerate(CARS):
        build_car(kit, f"c{i}", cx, cy, p, False, ctx)
    # the projector beam: a long four-sided frustum of faint silver light, plus a little dust inside it
    bmat, be, bmix = fade_emit(kit, "beam", "#dfe6f2")
    be.inputs["Strength"].default_value = 1.0
    nt = bmat.node_tree
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 0.0
    nt.links.new(lw.outputs["Facing"], mul.inputs[0])
    nt.links.new(mul.outputs[0], bmix.inputs[0])
    ay, az, hw = BOOTH[1] + 0.5, 1.2, 0.3
    ey = SCREEN_Y - 0.4
    A = [(-hw, ay, az - 0.2), (hw, ay, az - 0.2), (hw, ay, az + 0.2), (-hw, ay, az + 0.2)]
    B = [(-SCREEN_W / 2, ey, SCREEN_Z0 + 0.05), (SCREEN_W / 2, ey, SCREEN_Z0 + 0.05),
         (SCREEN_W / 2, ey, SCREEN_Z0 + SCREEN_H), (-SCREEN_W / 2, ey, SCREEN_Z0 + SCREEN_H)]
    faces = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    ctx["beam"] = {"obj": kit.mesh_obj("beam", A + B, faces, bmat), "mul": mul, "str": be}
    ctx["beam"]["obj"].visible_shadow = False
    dm, de = flat_emit(kit, "dust", "#cfd8e8", 1.0)
    verts, fcs = [], []
    for i in range(160):
        yy = rnd.uniform(-52, 18)
        u = (yy - ay) / (ey - ay)
        xx = rnd.uniform(-1, 1) * (0.3 + u * 12.7)
        zz = az + (rnd.uniform(0, 1) * (SCREEN_H + 0.05) * u) + 0.25 * (1 - u) * rnd.uniform(-1, 1)
        s = rnd.uniform(0.006, 0.014) * (1.0 + 0.012 * abs(yy + 60))
        b0 = len(verts)
        verts += [(xx - s, yy, zz - s), (xx + s, yy, zz - s), (xx + s, yy, zz + s), (xx - s, yy, zz + s)]
        fcs.append((b0, b0 + 1, b0 + 2, b0 + 3))
    ctx["dust"] = {"obj": kit.mesh_obj("dust", verts, fcs, dm), "em": de}
    ctx["dust"]["obj"].visible_shadow = False
    # lights: sun, a fill, the screen's light, the projector's spot
    ctx["sun"] = kit.light("sun", "SUN", (40, -30, 16), 5.0, "#ffb26b", size=0.3)
    kit.light("fill", "AREA", (0, -14, 30), 40000.0, "#9aa8d0", size=70.0)
    ctx["fill"] = kit.LIGHTS["fill"]["obj"]
    ctx["fill"].rotation_euler = (0, 0, 0)
    sl = kit.light("screenlight", "AREA", (0, SCREEN_Y - 1.2, SCREEN_Z0 + SCREEN_H * 0.5), 45000.0, "#b8c8e6", size=18.0)
    sl.rotation_euler = (-math.pi / 2, 0, 0)    # an area light shines down its -z; turned to shine toward -y
    sl.data.shape = "RECTANGLE"
    sl.data.size, sl.data.size_y = 22.0, 12.0
    sp = kit.light("beamspot", "SPOT", (BOOTH[0], BOOTH[1] + 0.3, 1.3), 120000.0, "#dfe6f2", size=0.4, spot=15, blend=0.6)
    kit.aim(sp, (0, 0, 6.0))
    # a faint dash glow in each of the two cars that matter
    for n in ("theo", "me"):
        c = ctx["cars"][n]
        kit.light(f"dash.{n}", "POINT", (c["x"], c["y"] + 0.7, 1.0), 14.0, "#ffb070", size=0.2)
    kit.light("spk.glow", "POINT", (0.7, -20.3, 1.5), 8.0, "#ffe0b0", size=0.2)
    kit.light("unlit.back", "POINT", (0, 0, 3), 1.0, "#7f9ae0", size=0.5)
    kit.light("cabin", "POINT", (3.4, 0.1, 1.8), 1.0, "#9fb4ff", size=0.3)


# ======================================================================================================= rooms
def build_rooms(kit, ctx):
    wall = kit.plastic("#5a4a40", 0.9)
    wood = kit.plastic("#4a3c32", 0.7)
    # ---- 1 the bar (x = 300)
    kit.box("bar.floor", (12, 10, 0.2), (300, 2, -0.1), kit.plastic("#2a2624", 0.7))
    kit.box("bar.wall", (12, 0.3, 5), (300, 3.2, 2.5), kit.plastic("#3b3a3c", 0.9))
    kit.box("bar.shelf", (6, 0.4, 0.1), (300, 2.9, 2.4), wood)
    kit.box("bar.shelf2", (6, 0.4, 0.1), (300, 2.9, 3.2), wood)
    for i, c in enumerate(("#6a8a4a", "#a0642a", "#3a5a8a", "#8a3a3a", "#c0a050", "#4a7a6a", "#7a5a9a")):
        kit.cyl(f"bottle{i}", 0.1, 0.5, (298 + 0.65 * i, 2.85, 2.7), kit.plastic(c, 0.2), rot=(0, 0, 0))
        kit.cyl(f"bottle{i}b", 0.1, 0.5, (298.3 + 0.65 * i, 2.85, 3.5), kit.plastic(c, 0.2))
    for i, bx in enumerate((297.2, 299.0, 301.0, 302.8)):
        kit.sphere(f"barbulb{i}", 0.12, (bx, 2.2, 4.2), kit.emit("#ffcf8a", 6.0))
    kit.cyl("bar.table", 1.5, 0.08, (300, -0.9, 0.95), wood, n=28)
    kit.cyl("bar.tablepost", 0.12, 0.95, (300, -0.9, 0.47), wood)
    for i, mx in enumerate((299.1, 300.0, 300.9)):
        kit.cyl(f"mug{i}", 0.1, 0.22, (mx, -1.2, 1.1), kit.plastic("#d8b85a", 0.3))
    for sx in (298.85, 300.0, 301.15):
        kit.cyl(f"stool{int(sx)}", 0.28, 0.08, (sx, 0.2, 0.58), wood)
        kit.cyl(f"stoolp{sx}", 0.06, 0.58, (sx, 0.2, 0.29), wood)
    kit.light("bar.key", "POINT", (300, -1.4, 3.2), 260.0, "#ffe0b8", size=0.5)
    kit.light("bar.back", "POINT", (300, 1.6, 3.0), 160.0, "#ffe0b8", size=0.5)
    # ---- 2 the harbour (x = 400)
    kit.box("harb.quay", (14, 8, 0.3), (400, -1, -0.15), kit.concrete("#7a7670", 1.2))
    sea = kit.plane("harb.sea", (80, 60), (400, 38, -0.9), kit.plastic("#27414f", 0.12))
    for i in range(5):
        kit.cyl(f"harb.post{i}", 0.08, 1.0, (396.5 + i * 1.8, 0.9, 0.5), kit.metal("#5f6466", 0.5))
    kit.box("harb.rail", (9.0, 0.08, 0.08), (400, 0.9, 1.0), kit.metal("#6a6e70", 0.4))
    kit.box("harb.rail2", (9.0, 0.08, 0.08), (400, 0.9, 0.65), kit.metal("#6a6e70", 0.4))
    kit.cyl("harb.bollard", 0.22, 0.6, (402.8, -0.9, 0.3), kit.plastic("#2b2b30", 0.6))
    kit.box("harb.boat", (6, 2.2, 1.0), (394.0, 12.0, 0.1), kit.plastic("#3a2a2a", 0.7))
    kit.box("harb.boatcab", (2.0, 1.6, 1.2), (393.0, 12.0, 1.1), kit.plastic("#cfc6b0", 0.7))
    kit.box("harb.bag", (0.5, 0.35, 0.7), (398.7, -0.6, 0.35), kit.plastic("#5e5a3c", 0.9), bevel=0.08)
    dg = kit.plastic("#8a6a44", 0.8)     # the dog, a plain blocky dog
    kit.box("dog.body", (0.28, 0.7, 0.3), (401.1, -0.6, 0.45), dg, bevel=0.05)
    kit.box("dog.head", (0.24, 0.26, 0.24), (401.1, -0.98, 0.7), dg, bevel=0.05)
    kit.box("dog.snout", (0.14, 0.14, 0.12), (401.1, -1.14, 0.66), kit.plastic("#5a4630", 0.8), bevel=0.03)
    for sx in (-1, 1):
        kit.box(f"dog.ear{sx}", (0.06, 0.1, 0.16), (401.1 + sx * 0.1, -0.94, 0.86), kit.plastic("#5a4630", 0.8))
        for sy in (-0.8, -0.4):
            kit.box(f"dog.leg{sx}{sy}", (0.08, 0.08, 0.22), (401.1 + sx * 0.09, sy, 0.17), dg)
    kit.box("dog.tail", (0.06, 0.28, 0.06), (401.1, -0.2, 0.62), dg, rot=(0.5, 0, 0))
    # ---- 3 the cafe (x = 500)
    kit.box("cafe.floor", (10, 10, 0.2), (500, 2, -0.1), kit.plastic("#5c4a3a", 0.6))
    kit.box("cafe.wall", (10, 0.3, 4.4), (500, 3.0, 2.2), kit.plastic("#7a5e4a", 0.9))
    kit.box("cafe.window", (4.0, 0.1, 2.2), (500, 2.8, 2.0), kit.emit("#ffd9a0", 3.0))
    kit.box("cafe.wframe", (4.3, 0.16, 0.12), (500, 2.76, 3.15), wood)
    kit.box("cafe.wframe2", (0.12, 0.16, 2.3), (500, 2.76, 2.0), wood)
    kit.cyl("cafe.table", 0.55, 0.06, (500, 0.1, 0.78), wood, n=24)
    kit.cyl("cafe.tpost", 0.07, 0.78, (500, 0.1, 0.39), wood)
    for i, cx in enumerate((499.8, 500.2)):
        kit.cyl(f"cafe.cup{i}", 0.07, 0.1, (cx, 0.0, 0.86), kit.plastic("#f2efe6", 0.3))
    for sx, sy in ((499.2, 0.1), (500.8, 0.1)):
        kit.box(f"cafe.chair{sx}", (0.56, 0.56, 0.08), (sx, sy, 0.55), wood)
    kit.cyl("cafe.plant", 0.22, 0.4, (502.0, 2.2, 0.2), kit.plastic("#8a4a30", 0.7))
    kit.sphere("cafe.leaf", 0.45, (502.0, 2.2, 0.85), kit.plastic("#3a6a3a", 0.8))
    kit.light("cafe.key", "POINT", (500, -1.2, 2.8), 150.0, "#ffd0a0", size=0.5)
    kit.light("cafe.win", "AREA", (500, 2.2, 2.0), 500.0, "#ffd9a0", size=3.0).rotation_euler = (-math.pi / 2, 0, 0)
    # ---- 4 the sofa (x = 600)
    kit.box("sofa.floor", (10, 10, 0.2), (600, 2, -0.1), kit.plastic("#3a3640", 0.8))
    kit.box("sofa.wall", (10, 0.3, 4.4), (600, 2.8, 2.2), kit.plastic("#43455a", 0.9))
    sm = kit.plastic("#7b4a58", 0.85)
    kit.box("sofa.seat", (3.2, 1.1, 0.5), (600, 0.65, 0.3), sm, bevel=0.1)
    kit.box("sofa.back", (3.2, 0.4, 1.0), (600, 1.2, 0.95), sm, bevel=0.1)
    for sx in (-1, 1):
        kit.box(f"sofa.arm{sx}", (0.35, 1.1, 0.8), (600 + sx * 1.6, 0.65, 0.5), sm, bevel=0.1)
    kit.box("sofa.cushion", (0.8, 0.28, 0.6), (599.5, -0.4, 0.78), kit.plastic("#d8b070", 0.9), bevel=0.1, rot=(-0.35, 0, 0))
    pm = kit.plastic("#18181c", 0.4)
    kit.box("sofa.phone", (0.34, 0.04, 0.62), (599.5, -0.58, 1.02), pm, rot=(-0.35, 0, 0), bevel=0.01)
    kit.sphere("sofa.lamp", 0.2, (602.4, 2.2, 1.7), kit.emit("#ffcf8a", 5.0))
    kit.light("sofa.lamp", "POINT", (602.2, 1.8, 1.8), 120.0, "#ffbb77", size=0.4)
    kit.light("sofa.key", "POINT", (600.5, -2.0, 2.6), 320.0, "#c8d0ff", size=0.5)
    # ---- 5 the office (x = 700)
    kit.box("off.floor", (10, 10, 0.2), (700, 2, -0.1), kit.plastic("#2f3036", 0.8))
    kit.box("off.wall", (10, 0.3, 4.4), (700, 2.9, 2.2), kit.plastic("#8a8478", 0.9))
    kit.box("off.wallR", (0.3, 8, 4.4), (703.2, 0, 2.2), kit.plastic("#1b2234", 0.9))
    wm = kit.emit("#e8b070", 2.0)
    for i in range(9):
        kit.box(f"off.city{i}", (0.06, 0.18 + (i % 3) * 0.12, 0.16), (703.0, -1.6 + i * 0.4, 2.0 + (i % 4) * 0.35), wm)
    kit.box("off.desk", (2.8, 1.2, 0.08), (700, 0.0, 0.95), kit.plastic("#6a5a48", 0.6))
    kit.box("off.deskbase", (2.6, 1.0, 0.9), (700, 0.0, 0.45), kit.plastic("#4a4a52", 0.7))
    kit.box("off.chair", (0.7, 0.7, 0.1), (700.6, 0.55, 0.5), kit.plastic("#2a2a32", 0.7))
    kit.box("off.chairb", (0.7, 0.12, 0.9), (700.6, 0.95, 0.95), kit.plastic("#2a2a32", 0.7))
    kit.box("off.hook", (1.4, 0.1, 0.12), (698.8, 2.7, 2.1), kit.metal("#5d6063", 0.5))
    kit.box("off.coat", (0.9, 0.2, 1.6), (698.4, 2.6, 1.4), kit.plastic("#3b4a66", 0.9), bevel=0.06)
    kit.box("off.lamparm", (0.06, 0.06, 0.6), (699.3, 0.0, 1.25), kit.metal("#2a2a2e", 0.4))
    kit.box("off.lamphead", (0.4, 0.2, 0.14), (699.3, -0.2, 1.55), kit.plastic("#2a2a2e", 0.5))
    kit.sphere("off.bulb", 0.08, (699.3, -0.26, 1.46), kit.emit("#ffdca0", 8.0))
    kit.light("off.lamp", "POINT", (699.3, -0.35, 1.45), 90.0, "#ffd9a0", size=0.2)
    kit.light("off.cold", "POINT", (702.0, 0.5, 2.6), 60.0, "#8aa0ff", size=0.6)
    kit.light("off.day", "AREA", (703.0, 0.0, 2.2), 0.0, "#ffc890", size=5.0).rotation_euler = (0, math.pi / 2, 0)


# ======================================================================================================= props
def build_props(kit, ctx):
    # my loose cap (on the hook in the office, on the seat beside me), the popcorn tub, Theo's tuft
    capm = kit.plastic("#a6402f", 0.6)
    cap = kit.empty("loosecap", (0, 0, 0))
    kit.box("loosecap.c", (0.42, 0.42, 0.2), (0, 0, 0.1), capm, cap, bevel=0.06)
    kit.box("loosecap.b", (0.34, 0.26, 0.04), (0, -0.3, 0.04), capm, cap, bevel=0.02)
    ctx["loosecap"] = cap
    tub = kit.empty("tub", (0, 0, 0))
    kit.cyl("tub.cup", 0.2, 0.32, (0, 0, 0.16), kit.plastic("#d9d4c8", 0.5), tub, r2=0.24)
    pm = kit.plastic("#d8b85a", 0.4)
    kit.sphere("tub.pop", 0.24, (0, 0, 0.36), pm, tub, seg=10)
    kit.cyl("tub.stripe", 0.225, 0.08, (0, 0, 0.12), kit.plastic("#c0392b", 0.5), tub)
    tub.scale = (1.9, 1.9, 1.9)
    ctx["tub"] = tub
    # the phone's screen in the sofa vignette: a man holding up his phone, drawn
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (200, 360), (50, 64, 104))
    d = ImageDraw.Draw(im)
    d.rectangle([60, 215, 140, 360], fill=(96, 140, 190))
    d.rectangle([76, 140, 124, 218], fill=(214, 168, 130))
    d.rectangle([70, 118, 130, 150], fill=(60, 44, 30))
    d.ellipse([36, 14, 164, 128], outline=(255, 207, 90), width=7)
    d.ellipse([88, 168, 98, 180], fill=(30, 24, 20)); d.ellipse([102, 168, 112, 180], fill=(30, 24, 20)); d.rectangle([90, 196, 110, 202], fill=(120, 60, 50))
    d.polygon([(100, 36), (118, 50), (118, 70), (130, 96), (70, 96), (82, 70), (82, 50)], fill=(10, 10, 14))
    d.ellipse([84, 38, 116, 74], fill=(10, 10, 14))
    d.rectangle([72, 60, 128, 76], fill=(10, 10, 14))
    img = bpy.data.images.new("phonescreen", 200, 360)
    px = []
    for y in range(360 - 1, -1, -1):
        for x in range(200):
            r, g, b = im.getpixel((x, y))
            px += [(r / 255) ** 2.2, (g / 255) ** 2.2, (b / 255) ** 2.2, 1.0]
    img.pixels = px
    m = kit._new("phonescreen")
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tcg = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tcg.outputs["Generated"], tex.inputs["Vector"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 3.0
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    scr = kit.plane("phone.screen", (0.3, 0.54), (599.5, -0.605, 1.02), m, rot=(math.pi / 2 - 0.35, 0, 0))
    scr.scale = (1.3, 1.3, 1.3)
    # world gradient for the sky
    w = bpy.context.scene.world
    nt = w.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.35
    mr.inputs["From Max"].default_value = 0.9
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(mr.outputs["Result"], mix.inputs[0])
    nt.links.new(mix.outputs["Result"], bg.inputs["Color"])
    ctx["sky"] = {"hor": mix.inputs[6], "zen": mix.inputs[7], "bg": bg}


# ======================================================================================================= markers
def build_markers(kit, ctx, story):
    ctx["markers"] = {}
    ringm, _ = flat_emit(kit, "ring gold", GOLD, 2.6)
    for who in story["cast"]:
        if who not in MARK_KIND:
            continue
        root = kit.empty(f"mark.{who}", (0, 0, 0))
        root.scale = (MARK_M, MARK_M, MARK_M)
        for i, quad in enumerate(ellipse_band(0, 0, 0.62, 0.8, 0.075)):
            poly(kit, f"mark.{who}.r{i}", quad, ringm, root, y=0.01)
        sg = kit.empty(f"mark.{who}.sil", (0, 0, -0.03), root)
        sg.scale = (0.56, 1.0, 0.56)
        m, em, mx = fade_emit(kit, f"sil.{who}", "#0b0b0e")
        for i, pts in enumerate(sil_shapes(MARK_KIND[who])):
            poly(kit, f"mark.{who}.s{i}", pts, m, sg)
        ctx["markers"][who] = {"root": root, "sil": sg, "em": em, "mix": mx, "kind": MARK_KIND[who]}
    # the giant ones on the screen: two shadows (mine, then Theo's) with a giant ring and the other's outline
    ctx["giants"] = {}
    gring, _ = flat_emit(kit, "giant ring", GOLD, 2.2)
    gdisc, _ = flat_emit(kit, "giant disc", "#d9c9a0", 1.0)
    for who, other, kind, x in (("me", "theo", "cap_tuft", -3.2), ("theo", "me", "cap", 3.2)):
        root = kit.empty(f"giant.{who}", (x, SCREEN_Y - 0.55, SCREEN_Z0 + 0.4))
        sm, _, smx = fade_emit(kit, f"shadow.{who}", "#06060a")
        smx.inputs[0].default_value = 0.94
        front = kit.empty(f"giant.{who}.front", (0, 0, 0), root)
        prof = kit.empty(f"giant.{who}.prof", (0, 0, 0), root)
        cap = (who in ("me", "theo"))
        # front-on: head, torso, arms, legs, a cap
        for i, pts in enumerate([circle(0, 4.95, 0.52), [(-0.72, 2.0), (0.72, 2.0), (0.72, 4.3), (-0.72, 4.3)],
                                 [(-1.18, 2.1), (-0.76, 2.1), (-0.76, 4.2), (-1.18, 4.2)], [(0.76, 2.1), (1.18, 2.1), (1.18, 4.2), (0.76, 4.2)],
                                 [(-0.66, 0.0), (-0.05, 0.0), (-0.05, 2.0), (-0.66, 2.0)], [(0.05, 0.0), (0.66, 0.0), (0.66, 2.0), (0.05, 2.0)],
                                 [(-0.2, 4.2), (0.2, 4.2), (0.2, 4.5), (-0.2, 4.5)],
                                 [(0.55 * math.cos(math.pi * k / 12), 5.1 + 0.42 * math.sin(math.pi * k / 12)) for k in range(13)],
                                 [(-0.5, 5.2), (-1.15, 5.12), (-1.15, 5.02), (-0.5, 5.02)]]):
            poly(kit, f"giant.{who}.f{i}", pts, sm, front)
        d = 1.0 if who == "me" else -1.0         # the way the peak points when it turns toward the other
        for i, pts in enumerate([circle(0, 4.95, 0.52), [(-0.4, 2.0), (0.4, 2.0), (0.4, 4.3), (-0.4, 4.3)],
                                 [(-0.15, 2.1), (0.15, 2.1), (0.2 * d, 3.6), (-0.2 * d, 3.6)],
                                 [(-0.4, 0.0), (0.4, 0.0), (0.4, 2.0), (-0.4, 2.0)],
                                 [(0.55 * math.cos(math.pi * k / 12), 5.1 + 0.42 * math.sin(math.pi * k / 12)) for k in range(13)],
                                 [(d * 0.5, 5.2), (d * 1.15, 5.12), (d * 1.15, 5.02), (d * 0.5, 5.02)]]):
            poly(kit, f"giant.{who}.p{i}", pts, sm, prof)
        # tuft on Theo's shadow? No: Theo's shadow is plain; his tuft is on the cap in my ring (the outline of Theo)
        ring = kit.empty(f"giant.{who}.ring", (0, 0, 6.55), root)
        ring.scale = (1.26, 1.0, 1.1)       # 1.5 x the shadow's head width
        for i, quad in enumerate(ellipse_band(0, 0, 0.62, 0.8, 0.085)):
            poly(kit, f"giant.{who}.r{i}", quad, gring, ring, y=-0.02)
        # a pale lit disc inside the ring so the black outline reads against it (the sky behind is dark)
        poly(kit, f"giant.{who}.disc", circle(0, 0, 0.6, n=40, sx=1.0) if False else [(0.62 * math.cos(2 * math.pi * k / 48), 0.8 * math.sin(2 * math.pi * k / 48)) for k in range(48)],
             gdisc, ring, y=-0.01)
        gs = kit.empty(f"giant.{who}.sil", (0, 0.0, 0.0), ring)
        gs.scale = (0.62 / 1.26, 1.0, 0.62 / 1.1)
        gm, _, _ = fade_emit(kit, f"giantsil.{who}", "#050507")
        for i, pts in enumerate(sil_shapes("cap_tuft" if who == "me" else "cap")):
            poly(kit, f"giant.{who}.s{i}", pts, gm, gs, y=-0.04)
        ctx["giants"][who] = {"root": root, "front": front, "prof": prof, "x": x, "ring": ring}


def build(kit, story, tl):
    ctx = {"turn": {}, "ready": False}
    build_props(kit, ctx)
    build_lot(kit, ctx)
    build_rooms(kit, ctx)
    build_markers(kit, ctx, story)
    return ctx


# ======================================================================================================= the Unlit
def ready_unlit(kit, ctx):
    """First frame: once the cast exists, make the Unlit black with a rim, give it two glints, cast no shadow."""
    if ctx["ready"]:
        return
    ctx["ready"] = True
    root = bpy.data.objects.get("unlit")
    if root is None:
        return
    mats = set()
    for ob in root.children_recursive:
        ob.visible_shadow = False
        for ms in getattr(ob.data, "materials", []) if ob.data is not None and hasattr(ob.data, "materials") else []:
            if ms is not None:
                mats.add(ms)
    for m in mats:
        nt = m.node_tree
        b = nt.nodes.get("Principled BSDF")
        if b is None:
            continue
        for k in ("Specular IOR Level", "Specular"):
            if k in b.inputs:
                b.inputs[k].default_value = 0.0
                break
        b.inputs["Roughness"].default_value = 1.0
        for lk in list(b.inputs["Base Color"].links):      # no light lands on it: a black surface, rim and glints only
            nt.links.remove(lk)
        b.inputs["Base Color"].default_value = kit.col("#050506")
        gm_ = nt.nodes.new("ShaderNodeNewGeometry")
        bv = nt.nodes.new("ShaderNodeBevel")
        bv.inputs["Radius"].default_value = 0.03
        bv.samples = 6
        ctx.setdefault("bevels", []).append(bv)

        def _adot(nrm):
            dt = nt.nodes.new("ShaderNodeVectorMath")
            dt.operation = "DOT_PRODUCT"
            nt.links.new(nrm, dt.inputs[0])
            nt.links.new(gm_.outputs["Incoming"], dt.inputs[1])
            ab = nt.nodes.new("ShaderNodeMath")
            ab.operation = "ABSOLUTE"
            nt.links.new(dt.outputs["Value"], ab.inputs[0])
            return ab

        def _math(op, a=None, b_=None, va=None, vb=None, clamp=False):
            n = nt.nodes.new("ShaderNodeMath")
            n.operation = op
            n.use_clamp = clamp
            if a is not None:
                nt.links.new(a, n.inputs[0])
            elif va is not None:
                n.inputs[0].default_value = va
            if b_ is not None:
                nt.links.new(b_, n.inputs[1])
            elif vb is not None:
                n.inputs[1].default_value = vb
            return n

        ag = _adot(gm_.outputs["Normal"])
        abv = _adot(bv.outputs["Normal"])
        edge = _math("SUBTRACT", ag.outputs[0], abv.outputs[0], clamp=True)         # only where the bevel tilts the normal away
        edge = _math("MULTIPLY", edge.outputs[0], vb=5.0)
        graz = _math("SUBTRACT", None, abv.outputs[0], va=1.0)
        graz = _math("POWER", graz.outputs[0], vb=16.0)
        tot = _math("ADD", edge.outputs[0], graz.outputs[0])
        pm = _math("MULTIPLY", tot.outputs[0], vb=3.0)
        ctx.setdefault("rimnodes", []).append(pm)
        nt.links.new(pm.outputs[0], b.inputs["Emission Strength"])
        b.inputs["Emission Color"].default_value = kit.col("#7f9ed6")
    # the head's two glints, the brightest thing on it
    build_halo(kit, ctx)
    hg = bpy.data.objects["unlit.headg"]
    gm, ge = flat_emit(kit, "glint", "#cfdfff", 3.5)
    ctx["glintem"] = ge
    ctx["glints"] = []
    for sx in (-1, 1):       # narrow slits, slanted a little: glints, not dots
        g = kit.box(f"unlit.glint{sx}", (0.15, 0.02, 0.03), (sx * 0.2, -0.61, 0.1), gm, hg, rot=(0, sx * 0.35, 0))
        g.visible_shadow = False
        ctx["glints"].append(g)


def build_halo(kit, ctx):
    m = kit._new("halo")
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col("#4f78c8")
    e.inputs["Strength"].default_value = 1.8
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vm = nt.nodes.new("ShaderNodeMapping")
    vm.inputs["Scale"].default_value = (1 / 2.1, 1 / 2.7, 0.0)
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 1.0
    mr.inputs["To Min"].default_value = 0.5
    mr.inputs["To Max"].default_value = 0.0
    nt.links.new(tc.outputs["Object"], vm.inputs["Vector"])
    nt.links.new(vm.outputs["Vector"], ln.inputs[0])
    nt.links.new(ln.outputs["Value"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(e.outputs[0], mx.inputs[2])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    h = kit.plane("unlit.halo", (4.2, 5.4), (0, 0, 0), m)
    h.visible_shadow = False
    ctx["halo"] = h


def ready_cast(kit, ctx):
    """Theo's tuft at the back of his head; my cap parts to toggle."""
    if "tuft" in ctx:
        return
    hg = bpy.data.objects.get("theo.headg")
    if hg is not None:
        hair = kit.plastic("#b58a56", 0.65)
        kit.box("theo.tuft", (0.26, 0.28, 0.55), (0.0, 0.5, 0.78), hair, hg, bevel=0.06, rot=(0.25, 0, 0.0))
        kit.box("theo.tuft2", (0.2, 0.22, 0.4), (0.12, 0.52, 0.72), hair, hg, bevel=0.05, rot=(0.3, 0, 0.3))
    ctx["tuft"] = True
    ctx["mecap"] = [bpy.data.objects[n] for n in ("me.capc", "me.capb") if n in bpy.data.objects]


# ======================================================================================================= animate
def _cam(tl, story, t, shot):
    """The camera of this frame (bl_story places it after animate runs), by the same rule bl_story uses."""
    main = sys.modules.get("__main__")
    fn = getattr(main, "cam_at", None)
    if fn is None:
        return None
    spec = next(s for s in story["shots"] if s["id"] == shot["id"])
    try:
        return V(fn(spec, shot, t, {}, tl)[0])
    except Exception:
        return None


def hexv(kit, h):
    return kit.col(h)[:3]


def animate(kit, story, tl, t, ctx):
    ready_unlit(kit, ctx)
    ready_cast(kit, ctx)
    shot = _shot(tl, t)
    sid = shot["id"]
    over = {}
    cam_early = _cam(tl, story, t, shot)
    # ---- the lighting preset of this shot
    env = None
    for c in _cues(tl, "env"):
        if c["t"] <= t + 1e-9:
            env = c["preset"]
    E = ENV[env or "gold"]
    sg, sc, (ax, ay, az) = E["sun"]
    ctx["sun"].data.color = hexv(kit, sc)
    ctx["sun"].location = (ax, ay, az)
    kit.aim(ctx["sun"], (0, 0, 0))
    over["sun"] = sg
    over["fill"] = E["fill"]
    beam = _ramp(_cues(tl, "beam"), t, "v", 0.0)
    over["beamspot"] = beam * (E.get("bsp", 1.0) if E["screen"] > 0.95 else 0.0)
    over["screenlight"] = E["scl"] * (0.04 + 0.96 * beam) if E["scl"] > 0 else 0.0
    for n in ("theo", "me"):
        over[f"dash.{n}"] = E["dash"]
    over["spk.glow"] = 1.0 if sid == "S38" else 0.0
    over["lampA"] = over["lampB"] = E.get("lamp", 1.0) if E["screen"] > 0.95 else 0.0
    ctx["gnd"][0].color_ramp.elements[1].color = kit.col(E.get("gnd", "#6a6460"))
    gc = kit.col(E.get("gnd", "#6a6460"))
    ctx["gnd"][0].color_ramp.elements[0].color = (gc[0] * 0.55, gc[1] * 0.55, gc[2] * 0.55, 1)
    day = env in ("office_five",)
    over["off.lamp"] = 0.0 if env == "office_five" else 1.0
    over["off.cold"] = 0.0 if env == "office_five" else 1.0
    over["off.day"] = 1.0 if env == "office_five" else 0.0
    kit.LIGHTS["off.day"]["base"] = 900.0
    over["fill"] = E["fill"]
    # the world: horizon and top colours
    sk = ctx["sky"]
    sk["hor"].default_value = kit.col(E["hor"])
    sk["zen"].default_value = kit.col(E["zen"])
    sk["bg"].inputs["Strength"].default_value = E["wstr"]
    # a small light that rides with the shots that sit in or beside a cabin (steady, so no flash)
    CAB = {"S41": ((3.4, 0.4, 1.45), 14, "#9fb4ff"), "S42": ((3.9, 0.5, 1.5), 14, "#9fb4ff"),
           "S60": ((-3.4, 1.0, 2.5), 260, "#ffd9a8"), "S61": ((0.4, -2.4, 2.0), 420, "#ffd9a8"),
           "S67": ((4.9, 0.6, 2.2), 330, "#ffd9a8"), "S68": ((3.9, 0.4, 2.3), 120, "#ffd9a8"),
           "S69": ((3.4, 0.9, 2.1), 160, "#ffd9a8"), "S70": ((0.6, -0.2, 1.65), 60, "#ffe0b8"),
           "S08": ((599.9, -1.6, 1.7), 90, "#cfd8ff"), "S14": ((699.9, 1.0, 2.5), 90, "#ffd0a0"),
           "S11": ((2.0, 2.0, 3.0), 160, "#ffd9a8")}
    cb = CAB.get(sid)
    cl = kit.LIGHTS["cabin"]
    if cb:
        cl["obj"].location = cb[0]
        cl["light"].color = hexv(kit, cb[2])[:3]
        over["cabin"] = cb[1]
    else:
        over["cabin"] = 0.0
    # ---- the screen: a slow drift of colour; its brightness follows the beam (a fade of 1.5 s or more)
    scr = ctx["screen"]
    scr["map"].inputs["Location"].default_value = (0.0, t * 0.05, t * 0.035)
    if E["screen"] > 0.95:
        scr["em"].inputs["Strength"].default_value = E["screen"] * (0.04 + 0.96 * beam)
    else:
        scr["em"].inputs["Strength"].default_value = E["screen"]
    ctx["beam"]["mul"].inputs[1].default_value = 0.07 * beam
    ctx["dust"]["em"].inputs["Strength"].default_value = 0.9 * beam
    vis_beam = beam > 0.001
    ctx["beam"]["obj"].hide_render = not vis_beam
    ctx["dust"]["obj"].hide_render = not vis_beam
    # ---- cars: roofs on except in the shots that sit inside a cabin, my car rolling in, doors
    ROOF_OFF = {"S13", "S16", "S17", "S19", "S22", "S25", "S27", "S35", "S45", "S46", "S47", "S63", "S68", "S69",
                "S70", "S72", "S73", "S11", "S12"}
    for n, c in ctx["cars"].items():
        c["roof"].hide_render = ((n in ("theo", "me")) and sid in ROOF_OFF) or (n == "c0" and sid == "S60")
    roll = _cues(tl, "roll")
    me = ctx["cars"]["me"]
    off = 0.0
    if roll:
        r0 = roll[0]["t"]
        end = next(s["start"] for s in tl["shots"] if s["id"] == "S19")
        if r0 <= t < end:
            off = -7.0 * (1 - _ss((t - r0) / roll[0]["dur"]))
    me["root"].location = (me["x"], me["y"] + off, 0)
    for n, car in (("me", me), ("theo", ctx["cars"]["theo"])):
        for side in (-1, 1):
            op, prev = 0.0, 0.0
            for c in _cues(tl, "door"):
                if c["car"] == n and c["side"] == side and c["t"] <= t + 1e-9:
                    d = c.get("dur", 0.45)
                    op = c["open"] if d <= 0 else prev + (c["open"] - prev) * _ss((t - c["t"]) / d)
                    prev = c["open"]
            car["doors"][side].rotation_euler = (0, 0, side * math.radians(62) * op)
    # ---- the cap: on my head or off (and the loose one on the hook, on the seat)
    capon = True
    for c in _cues(tl, "cap"):
        if c["t"] <= t + 1e-9:
            capon = c["on"]
    me_state = acting_mod.state(tl, "me", t)
    for ob in ctx["mecap"]:
        ob.hide_render = (not capon) or me_state["hidden"]
    lc = ctx["loosecap"]
    lc.hide_render = capon
    for ob in lc.children:
        ob.hide_render = capon
    if sid == "S14":
        lc.location, lc.rotation_euler = (699.35, 2.3, 1.75), (0, 0, 0)
        lc.scale = (1.7, 1.7, 1.7)
    else:
        lc.location, lc.rotation_euler = (4.35, -21.3, 0.62), (0, 0, 0.4)
        lc.scale = (1.0, 1.0, 1.0)
    # ---- the popcorn tub: on the bench in S13, sliding to me at L62, gone otherwise
    tub = ctx["tub"]
    show = sid == "S13" or sid == "S69"
    for ob in [tub] + list(tub.children):
        ob.hide_render = not show
    if sid == "S13":
        tub.location = (3.4, -0.05, 0.55)
    elif sid == "S69":
        t0 = next((c["t"] for c in _cues(tl, "tub")), shot["start"])
        tub.location = (2.7 + 1.2 * _ss((t - t0) / 0.9), -0.05, 0.55)
    # ---- the rooms' own people: sitting people bend their legs
    for who, keys in tl["acting"].items():
        ob = bpy.data.objects.get(who)
        if ob is None:
            continue
        sitting = acting_mod._switch(keys, "sit", t, False)
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg is not None:
                leg.rotation_euler = (-math.pi / 2, 0, 0) if sitting else leg.rotation_euler
    root = bpy.data.objects.get("unlit")
    ub = kit.LIGHTS["unlit.back"]
    seated_u = sid in ("S40", "S41", "S42", "S43", "S44", "S45")
    if root is not None and not root.hide_render and not seated_u:
        loc_u = root.matrix_world.translation
        ub["obj"].location = (loc_u.x, loc_u.y + 2.6, 2.6)
        over["unlit.back"] = 0.0
    else:
        over["unlit.back"] = 0.0
    # seated in the car: the head bends FORWARD (top toward the windscreen) against the roof lining, face turned back to me
    neck = bpy.data.objects.get("unlit.neck")
    if neck is not None and seated_u:
        ust = acting_mod.state(tl, "unlit", t)
        neck.rotation_mode = "QUATERNION"
        qz = Euler((0, 0, ust["head_yaw"])).to_quaternion()
        qx = Euler((ust["head_pitch"] * 0.8, 0, 0)).to_quaternion()
        neck.rotation_quaternion = qx @ qz
    elif neck is not None:
        neck.rotation_mode = "XYZ"
    # ---- the Unlit's glints follow its hidden state; its rim and glints grow with the distance from the camera
    root = bpy.data.objects.get("unlit")
    if cam_early is not None and root is not None:
        dd = (cam_early - root.matrix_world.translation).length
        for pmn in ctx.get("rimnodes", []):
            pmn.inputs[1].default_value = (0.5 if seated_u else 1.0) * 2.0 * (1.0 + dd / 4.0)
        for bv in ctx.get("bevels", []):
            bv.inputs["Radius"].default_value = 0.015 if seated_u else 0.03
        ctx["glintem"].inputs["Strength"].default_value = 3.5 * (1.0 + dd / 15.0)
    gsc = 1.0 + (min(1.6, dd / 8.0) if cam_early is not None and root is not None else 0.0)
    for g in ctx.get("glints", []):
        g.hide_render = root.hide_render
        g.scale = (gsc, 1.0, gsc)
    # a soft pale-blue mist card behind the standing Unlit, so its black reads against something
    halo = ctx.get("halo")
    if halo is not None:
        on = root is not None and not root.hide_render and not seated_u and cam_early is not None
        halo.hide_render = not on
        if on:
            lu = root.matrix_world.translation
            ang = math.atan2(cam_early.x - lu.x, -(cam_early.y - lu.y))
            dirv = V((lu.x - cam_early.x, lu.y - cam_early.y, 0)).normalized()
            halo.location = (lu.x + dirv.x * 1.6, lu.y + dirv.y * 1.6, 1.9)
            halo.rotation_euler = (math.pi / 2, 0, ang)
            hs = 1.0 + dd / 9.0
            halo.scale = (hs, hs, hs)
    # ---- markers
    cam = _cam(tl, story, t, shot)
    ring_v = _ramp(_cues(tl, "ring"), t, "v", 1.0)
    turns = {"me": 0.0, "theo": 0.0}
    for c in _cues(tl, "turn"):
        if c["t"] <= t + 1e-9:
            turns[c["who"]] = c["deg"]
    for who, mk in ctx["markers"].items():
        s = acting_mod.state(tl, who, t)
        hid = s["hidden"]
        scale = bpy.data.objects[who].scale.z / 0.34 if who in bpy.data.objects else 1.0
        top = s["z"] + CHAR_TOP * scale
        mk["root"].location = (s["x"], s["y"], top + 0.27 + 0.8 * MARK_M)
        for ob in [mk["root"]] + list(mk["root"].children_recursive):
            ob.hide_render = hid
        if cam is not None:
            a = math.atan2(cam.x - s["x"], -(cam.y - s["y"]))
            mk["root"].rotation_euler = (0, 0, a)
        mk["sil"].rotation_euler = (0, 0, math.radians(turns.get(who, 0.0)))
        f = ring_v if who == "theo" else 1.0
        grey = 0.04 + 0.78 * (1 - f) ** 0.8
        gv = int(min(255, grey * 255 * 1.05))
        mk["em"].inputs["Color"].default_value = kit.col("#%02x%02x%02x" % (gv, gv, gv))
        mk["mix"].inputs[0].default_value = max(0.0, min(1.0, f * 1.8))
    # ---- the giant shadows on the screen
    sh = {c["t"]: c for c in _cues(tl, "shadow")}
    turn_t = next((c["t"] for c in _cues(tl, "shadow") if "turn" in c), None)
    for who, g in ctx["giants"].items():
        on, t0, rise = False, 0.0, 1.0
        for c in _cues(tl, "shadow"):
            if c.get("who") == who and c["t"] <= t + 1e-9:
                on = c["on"]
                t0, rise = c["t"], c.get("rise", 1.0)
        for ob in [g["root"]] + list(g["root"].children_recursive):
            ob.hide_render = not on
        k = 0.5 + 0.5 * _ss((t - t0) / max(0.01, rise))
        turned = turn_t is not None and t >= turn_t
        g["root"].scale = (2.4 * k, 1.0, 2.4 * k)
        x0 = (g["x"] if not turned else 2.6) if who == "theo" else (-3.2 if not turned else -2.6)
        # my shadow starts centred, then Theo's joins on the right
        g["root"].location = (x0 if sid not in ("S52", "S53", "S54", "S55", "S56", "S57", "S58") else (-0.0 if who == "me" else x0),
                              SCREEN_Y - 0.55, SCREEN_Z0 + 0.4)
        g["front"].hide_render = turned
        for ob in g["front"].children_recursive:
            ob.hide_render = turned or not on
        for ob in g["prof"].children_recursive:
            ob.hide_render = (not turned) or not on
    return over
