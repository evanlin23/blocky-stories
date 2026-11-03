"""ep88-six-paintings: a bright oxblood gallery hall, six frames A-F, and frame C is really a window.

Built by hand from kit.py's parts. No text anywhere: the plaque letters are block glyphs of boxes, our own markers.
World (m, z up): long wall at y 2.9 (front face), camera side is -y. Grid columns x -1.2, 0, 1.2; top row frame
centre z 4.15, bottom row 1.6; frames are 1.1 x 2.0 outside, canvas 0.9 x 1.8. C (top right) is an opening in the wall
with a white window frame and glass; the garden terrace (top z 2.85) lies behind it and the watcher stands on it.
The rule meter: a brass clock-face countdown parented to the camera, top-left in every shot (its hand sweeps to a red
chime mark), and the gold plaques.
"""
from __future__ import annotations

import math

import bpy
from mathutils import Vector as V

from blocky import kit as _kit  # noqa: F401

GX = (-1.2, 0.0, 1.2)
TOPZ, BOTZ = 4.15, 0.85
WALL_Y = 2.9
GLYPH = {  # 3 x 5 block letters, row 0 on top
    "A": ["010", "101", "111", "101", "101"],
    "B": ["110", "101", "110", "101", "110"],
    "C": ["011", "100", "100", "100", "011"],
    "D": ["110", "101", "101", "101", "110"],
    "E": ["111", "100", "110", "100", "111"],
    "F": ["111", "100", "110", "100", "100"],
}
_n = [0]


def nm(p):
    _n[0] += 1
    return f"{p}.{_n[0]}"


class K:
    kit = None


def P(h, rough=0.45, spec=0.4):
    return K.kit.plastic(h, rough, spec=spec)


def B(size, loc, mat, name="b", bevel=0.004, rot=(0, 0, 0), parent=None):
    return K.kit.box(nm(name), size, loc, mat, parent, rot, bevel)


def paint(cx, cz, dx, dz, w, h, color, layer=1, rough=0.8, rot=0.0):
    """A flat blob on a canvas centred (cx, cz): offset (dx, dz), size w x h, `layer` steps proud of the canvas."""
    y = WALL_Y - 0.02 - layer * 0.012
    return B((w, 0.012, h), (cx + dx, y, cz + dz), P(color, rough, 0.1), "paint", 0.0, rot=(0, rot, 0))


def plaque(cx, letter):
    z = 0.35 if cx is not None else 0
    return z


def build_plaque(x, z, letter):
    y = WALL_Y - 0.03
    B((0.72, 0.05, 0.4), (x, y, z), P("#e2b23c", 0.3, 0.8), "plaque", 0.01)
    B((0.76, 0.04, 0.44), (x, y + 0.012, z), P("#9a6b1e", 0.4, 0.5), "plaquerim", 0.01)
    px = 0.062
    for r, row in enumerate(GLYPH[letter]):
        for c, ch in enumerate(row):
            if ch == "1":
                B((px, 0.02, px), (x + (c - 1) * px, y - 0.03, z + (2 - r) * px), P("#24060b", 0.6, 0.1), "glyph", 0.0)


def gilt_frame(cx, cz):
    g = P("#e2b23c", 0.3, 0.85)
    d = P("#a87820", 0.4, 0.6)
    y = WALL_Y - 0.06
    for (w, h, dx, dz) in ((1.1, 0.1, 0, 0.95), (1.1, 0.1, 0, -0.95), (0.1, 1.8, -0.5, 0), (0.1, 1.8, 0.5, 0)):
        B((w, 0.12, h), (cx + dx, y, cz + dz), g, "gilt", 0.02)
    for (w, h, dx, dz) in ((0.92, 0.04, 0, 0.88), (0.92, 0.04, 0, -0.88), (0.04, 1.76, -0.44, 0), (0.04, 1.76, 0.44, 0)):
        B((w, 0.05, h), (cx + dx, y - 0.04, cz + dz), d, "lip", 0.005)
    # brass picture light above
    B((0.5, 0.06, 0.05), (cx, y - 0.1, cz + 1.12), P("#d9a441", 0.25, 0.9), "plight", 0.01)
    B((0.04, 0.12, 0.04), (cx, y - 0.04, cz + 1.07), P("#d9a441", 0.25, 0.9), "plarm", 0.005)


def canvas(cx, cz, color):
    B((0.9, 0.02, 1.8), (cx, WALL_Y - 0.01, cz), P(color, 0.85, 0.05), "canvas", 0.0)


def subject_A(cx, cz):
    canvas(cx, cz, "#5b95c4")
    paint(cx, cz, 0, -0.2, 0.9, 0.6, "#2c6f9a", 1)             # sea band
    paint(cx, cz, 0, -0.62, 0.8, 0.62, "#14285a", 2)           # navy coat
    paint(cx, cz, 0, -0.38, 0.22, 0.34, "#f4f1ea", 3)          # shirt
    paint(cx, cz, 0, 0.12, 0.46, 0.5, "#e8b48a", 3)           # face
    paint(cx, cz, 0, -0.14, 0.4, 0.26, "#f6f6f4", 4)           # white beard
    paint(cx, cz, 0, 0.16, 0.2, 0.05, "#2a1a14", 4)            # brows
    paint(cx, cz, -0.1, 0.1, 0.07, 0.07, "#1a1a22", 5)
    paint(cx, cz, 0.1, 0.1, 0.07, 0.07, "#1a1a22", 5)
    paint(cx, cz, 0, 0.5, 0.56, 0.2, "#fafafa", 4)             # hat crown
    paint(cx, cz, 0, 0.36, 0.64, 0.07, "#111116", 5)           # peak
    paint(cx, cz, 0, 0.52, 0.1, 0.1, "#e2b23c", 5)             # badge
    for dx in (-0.2, 0.2):
        paint(cx, cz, dx, -0.7, 0.07, 0.07, "#e2b23c", 4)
        paint(cx, cz, dx, -0.52, 0.07, 0.07, "#e2b23c", 4)


def subject_B(cx, cz):
    canvas(cx, cz, "#cfe3ef")
    paint(cx, cz, 0, -0.62, 0.9, 0.52, "#7fa86a", 1)           # grass
    gr, dk = "#aeb5c0", "#7b8390"
    k, ox, oz = 0.85, -0.09, -0.02

    def d(dx, dz, w, h, c, layer, rot=0.0):
        paint(cx, cz, dx * k + ox, dz * k + oz, w * k, h * k, c, layer, rot=rot)
    # the greyhound ALONE, side view facing right: deep chest, tucked belly, long legs, a long snout
    d(0.0, 0.12, 0.52, 0.15, gr, 5)                            # back and flank
    d(-0.2, 0.08, 0.2, 0.26, gr, 6)                            # haunch
    d(0.2, 0.02, 0.22, 0.32, gr, 6)                            # deep chest
    d(-0.02, -0.04, 0.24, 0.08, dk, 8)                         # tucked belly shade
    for x in (0.22, 0.3):
        d(x, -0.3, 0.055, 0.42, gr, 7)                         # front legs
    for x in (-0.24, -0.14):
        d(x, -0.3, 0.055, 0.42, dk, 7)                         # rear legs
    d(-0.38, 0.06, 0.24, 0.045, gr, 5, rot=0.6)                # tail
    d(0.3, 0.3, 0.12, 0.3, gr, 7, rot=-0.3)                    # long neck
    d(0.37, 0.48, 0.15, 0.12, gr, 8)                           # skull
    d(0.5, 0.45, 0.22, 0.06, gr, 9)                            # long snout
    d(0.62, 0.455, 0.04, 0.045, "#15151c", 10)                 # nose
    d(0.31, 0.5, 0.06, 0.11, dk, 10, rot=0.4)                  # ear
    d(0.4, 0.5, 0.035, 0.035, "#101018", 10)                   # eye


def subject_D(cx, cz):
    canvas(cx, cz, "#27463f")
    paint(cx, cz, 0, -0.78, 0.9, 0.26, "#7a4a2a", 1)           # table
    for dx, up, c, sh in ((-0.2, 0.0, "#d7e04a", "#a9b52c"), (0.22, 0.08, "#e8ec6a", "#b8be3e")):
        paint(cx, cz, dx, -0.3 + up, 0.36, 0.3, c, 2)           # pear belly, fat bottom
        paint(cx, cz, dx + 0.12, -0.3 + up, 0.1, 0.28, sh, 4)   # shaded side
        paint(cx, cz, dx, -0.08 + up, 0.26, 0.2, c, 3)          # shoulder
        paint(cx, cz, dx, 0.13 + up, 0.14, 0.24, c, 4)          # narrow neck
        paint(cx, cz, dx + 0.01, 0.34 + up, 0.035, 0.1, "#4a2c14", 5)   # stem
    paint(cx, cz, 0.0, -0.5, 0.8, 0.1, "#d4502a", 5)            # bowl rim
    paint(cx, cz, 0, -0.62, 0.6, 0.16, "#b23c20", 5)            # bowl belly
    paint(cx, cz, 0, -0.72, 0.3, 0.05, "#8a2c16", 5)            # foot
    paint(cx, cz, 0.3, 0.6, 0.2, 0.12, "#4a7a5c", 3)            # leaf


def subject_E(cx, cz):
    canvas(cx, cz, "#8d96a3")                                   # a grey sky
    paint(cx, cz, -0.2, 0.62, 0.5, 0.26, "#6b7482", 2)         # storm clouds
    paint(cx, cz, 0.2, 0.42, 0.46, 0.2, "#5d6674", 2)
    paint(cx, cz, 0.0, -0.45, 0.9, 0.9, "#1d4558", 1)          # sea, horizon at the middle
    for dx, dz, w in ((-0.3, -0.12, 0.3), (0.25, -0.22, 0.34), (-0.15, -0.5, 0.4), (0.28, -0.62, 0.32), (-0.3, -0.78, 0.3)):
        paint(cx, cz, dx, dz, w, 0.07, "#f4f8fb", 2)           # whitecaps
        paint(cx, cz, dx + 0.06, dz + 0.07, w * 0.5, 0.06, "#f4f8fb", 3)
    paint(cx, cz, 0.0, -0.05, 0.4, 0.1, "#7a3a1c", 3, rot=0.35)     # a tilted ship: hull
    paint(cx, cz, -0.05, 0.1, 0.04, 0.4, "#e8e0cc", 4, rot=0.35)    # mast
    paint(cx, cz, -0.03, 0.14, 0.2, 0.26, "#f4efe0", 4, rot=0.35)   # sail


def subject_F(cx, cz):
    canvas(cx, cz, "#d9c7a0")
    wd = "#8a5330"
    paint(cx, cz, 0, -0.78, 0.9, 0.24, "#a8946a", 1)           # floor
    paint(cx, cz, 0, -0.84, 0.5, 0.05, "#7e6a44", 2)           # shadow
    for dx in (-0.22, 0.22):
        paint(cx, cz, dx, -0.5, 0.08, 0.5, wd, 2)              # legs
    paint(cx, cz, 0, -0.2, 0.6, 0.1, wd, 3)                    # seat
    paint(cx, cz, 0, -0.12, 0.5, 0.07, "#c0392b", 4)           # red cushion
    for dx in (-0.25, 0.25):
        paint(cx, cz, dx, 0.35, 0.08, 1.0, wd, 2)              # back posts
    paint(cx, cz, 0, 0.5, 0.42, 0.55, "#b8743c", 3)            # back panel
    paint(cx, cz, 0, 0.88, 0.58, 0.08, wd, 3)                  # top rail


def fog_material(kit):
    """A matte grey breath on the glass: a soft round patch, diffuse (no emission), its strength driven per frame."""
    m = kit._new(nm("fog"))
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (4.0, 4.0, 4.0)
    mp.vector_type = "POINT"
    gr = nt.nodes.new("ShaderNodeTexGradient")
    gr.gradient_type = "QUADRATIC_SPHERE"
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].position = 0.0
    rp.color_ramp.elements[0].color = (0, 0, 0, 1)
    rp.color_ramp.elements[1].position = 0.9
    rp.color_ramp.elements[1].color = (0.78, 0.78, 0.78, 1)
    rp.color_ramp.interpolation = "EASE"
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 1.0
    nt.links.new(tc.outputs["Object"], mp.inputs[0])
    nt.links.new(mp.outputs[0], gr.inputs[0])
    nt.links.new(gr.outputs["Fac"], rp.inputs["Fac"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    df = nt.nodes.new("ShaderNodeBsdfDiffuse")
    df.inputs["Color"].default_value = _kit.col("#a6a39e")
    df.inputs["Roughness"].default_value = 1.0
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(rp.outputs["Color"], mx.inputs["Fac"])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(df.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    return m, rp.color_ramp.elements[1]


def pane_material(kit):
    """Clear glass whose reflection grows toward grazing angles (a sheen when you see it from the side)."""
    m = kit._new(nm("pane"))
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.04
    gl.inputs["Color"].default_value = (0.85, 0.92, 1.0, 1)
    fr = nt.nodes.new("ShaderNodeFresnel")
    fr.inputs["IOR"].default_value = 1.45
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(fr.outputs[0], mx.inputs["Fac"])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    return m


def sheen_material(kit, fac):
    """A faint pale reflection streak: transparent mixed with a soft white."""
    m = kit._new(nm("sheen"))
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.9, 0.95, 1.0, 1)
    em.inputs["Strength"].default_value = 0.6
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs["Fac"].default_value = fac
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    return m


# ------------------------------------------------------------------------------------------ the countdown clock (HUD)
HUD_POS = (-0.1, 0.215, -0.8)     # camera-local: top-left at lens 33 to 40
HUD_R = 0.026
CHIME_A = 120.0                    # the hand starts here (degrees clockwise from 12) and sweeps to 360


def build_hud(kit, ctx):
    cam = kit.OBJ["cam"]
    root = kit.empty("hudroot", HUD_POS, cam)
    ctx["hud"] = root
    r = HUD_R
    brass = kit.emit("#d9a441", 0.85)
    face = kit.emit("#fff1d0", 0.62)
    ink = kit.emit("#2a0c12", 1.0)
    red = kit.emit("#d8342c", 0.8)
    parts = [kit.cyl(nm("hudrim"), r * 1.12, 0.002, (0, 0, -0.002), brass, root, n=40),
             kit.cyl(nm("hudface"), r, 0.002, (0, 0, 0), face, root, n=40)]
    ctx["wedges"] = []
    n = 24
    span = 360.0 - CHIME_A
    for k in range(n):
        a0 = math.radians(CHIME_A + span * k / n)
        a1 = math.radians(CHIME_A + span * (k + 1) / n)
        verts = [(0, 0, 0), (0.92 * r * math.sin(a0), 0.92 * r * math.cos(a0), 0),
                 (0.92 * r * math.sin(a1), 0.92 * r * math.cos(a1), 0)]
        w = kit.mesh_obj(nm("hudwedge"), verts, [(0, 2, 1)], red, root, (0, 0, 0.0015))
        ctx["wedges"].append((w, CHIME_A + span * (k + 0.5) / n))
    for k in range(12):
        a = k * math.pi / 6
        L = 0.17 * r if k % 3 == 0 else 0.09 * r
        kit.box(nm("hudtick"), (0.07 * r, L, 0.001), (0.8 * r * math.sin(a), 0.8 * r * math.cos(a), 0.0022), ink, root,
                (0, 0, -a))
    kit.box(nm("hudmark"), (0.16 * r, 0.26 * r, 0.001), (0, 0.84 * r, 0.0026), red, root)
    piv = kit.empty("hudhand", (0, 0, 0.003), root)
    kit.box(nm("hudhandbar"), (0.09 * r, 0.82 * r, 0.001), (0, 0.4 * r, 0), ink, piv)
    kit.cyl(nm("hudhub"), 0.09 * r, 0.002, (0, 0, 0.0012), brass, piv, n=16)
    ctx["hand"] = piv
    for ob in [root] + list(root.children_recursive) + list(piv.children):
        if ob.type == "MESH":
            ob.visible_shadow = False


# ------------------------------------------------------------------------------------------ build
def figure(kit, name, x, y0, s, mat):
    """A flat person-shaped shadow lying on the floor, feet at (x, y0), head toward +y."""
    root = kit.empty(name, (x, y0, FLOOR_TOP + 0.016))
    h = 0.012
    B((0.14, 0.8 * s, h), (-0.12, 0.4 * s, 0), mat, "shl", 0.0, parent=root)
    B((0.14, 0.8 * s, h), (0.12, 0.4 * s, 0), mat, "shr", 0.0, parent=root)
    B((0.5, 0.7 * s, h), (0, 1.15 * s, 0), mat, "sht", 0.0, parent=root)
    B((0.11, 0.7 * s, h), (-0.33, 1.15 * s, 0), mat, "sha", 0.0, parent=root)
    B((0.11, 0.7 * s, h), (0.33, 1.15 * s, 0), mat, "shb", 0.0, parent=root)
    K.kit.cyl(nm("shh"), 0.16, h, (0, 1.72 * s, 0), mat, root, n=20)
    for ob in root.children:
        ob.visible_shadow = False
    return root


FLOOR_TOP = -0.62
DOOR_X = -4.6


def build(kit, story, tl):
    K.kit = kit
    ctx = {}
    oxb = P("#6c1a26", 0.7, 0.1)
    # ---- floor, back wall, wall (with the window opening), skirting
    B((18, 18.3, 0.2), (0, -5.85, FLOOR_TOP - 0.1), P("#9a6439", 0.25, 0.5), "floor", 0.0)
    B((18, 0.4, 9), (0, -15.2, 3.9), oxb, "backwall", 0.0)
    wy, wd = WALL_Y + 0.2, 0.4
    wx0, wx1, wz0, wz1 = 0.65, 1.75, 3.15, 5.15      # window opening in C's frame cell
    H = 8.0

    def seg(x0, x1, z0, z1):
        o = B((x1 - x0, wd, z1 - z0), ((x0 + x1) / 2, wy, (z0 + z1) / 2), oxb, "wall", 0.0)
        if z0 == wz1:
            o.visible_shadow = False   # the wall above the opening doesn't stop the man's key
    seg(-8, wx0, 0, H)
    seg(wx1, 8, 0, H)
    seg(wx0, wx1, 0, wz0)
    seg(wx0, wx1, wz1, H)
    B((16, 0.02, 0.08), (0, WALL_Y - 0.01, -0.58), P("#d9c9a8", 0.5, 0.2), "skirt", 0.004)
    # ---- the five gilt frames
    subs = {(0, 0): subject_A, (1, 0): subject_B, (0, 1): subject_D, (1, 1): subject_E, (2, 1): subject_F}
    for (ci, ri), fn in subs.items():
        cz = TOPZ if ri == 0 else BOTZ
        gilt_frame(GX[ci], cz)
        fn(GX[ci], cz)
    for i, L in enumerate("ABC"):
        build_plaque(GX[i], TOPZ - 1.25, L)
    for i, L in enumerate("DEF"):
        build_plaque(GX[i], BOTZ - 1.2, L)
    # ---- C: white-painted window frame, a deep white reveal, glass at the back of the reveal, breath on its far face
    wf = P("#fbfaf4", 0.55, 0.2)
    cx, cz = 1.2, TOPZ
    for (w, h, dx, dz) in ((1.1, 0.1, 0, 0.95), (1.1, 0.1, 0, -0.95), (0.1, 1.8, -0.5, 0), (0.1, 1.8, 0.5, 0)):
        B((w, 0.12, h), (cx + dx, WALL_Y - 0.06, cz + dz), wf, "wframe", 0.02).visible_shadow = False
    B((1.3, 0.12, 0.06), (cx, WALL_Y - 0.1, cz - 1.0), wf, "wsill", 0.01)
    # white reveal liner: four slabs 2 cm inside the cut, 2 cm short of both wall faces
    for (sx, sy, sz, lx, lz) in ((0.02, 0.36, 2.0, wx0 + 0.01, 4.15), (0.02, 0.36, 2.0, wx1 - 0.01, 4.15),
                                 (1.06, 0.36, 0.02, 1.2, wz0 + 0.01), (1.06, 0.36, 0.02, 1.2, wz1 - 0.01)):
        B((sx, sy, sz), (lx, 3.1, lz), wf, "liner", 0.0).visible_shadow = False
    # a brass window latch on the right bar: a plate and a turn-lever, proud of the white wood
    brass = P("#d9a441", 0.25, 0.9)
    B((0.07, 0.03, 0.18), (cx + 0.5, WALL_Y - 0.135, cz), brass, "latchplate", 0.008)
    B((0.2, 0.035, 0.045), (cx + 0.46, WALL_Y - 0.165, cz + 0.02), brass, "latchlever", 0.01, rot=(0, math.radians(-12), 0))
    B((0.05, 0.045, 0.05), (cx + 0.5, WALL_Y - 0.165, cz + 0.02), brass, "latchnub", 0.01)
    GLASS_Y = 3.2
    ctx["pane"] = kit.plane(nm("pane"), (1.06, 1.96), (cx, GLASS_Y, cz), pane_material(kit), None, rot=(math.pi / 2, 0, 0))
    ctx["pane"].visible_shadow = False
    fogm, ctx["fog_str"] = fog_material(kit)
    ctx["fog"] = kit.plane(nm("fogdisc"), (0.4, 0.4), (cx + 0.08, GLASS_Y + 0.012, cz + 0.4), fogm, None,
                           rot=(math.pi / 2, 0, 0))
    ctx["fog"].visible_shadow = False
    ctx["fog_base"] = (cx + 0.08, cz + 0.4)
    sheen = kit.plane(nm("sheen"), (0.07, 1.5), (cx - 0.28, GLASS_Y - 0.03, cz + 0.05), sheen_material(kit, 0.1), None,
                      rot=(math.pi / 2, math.radians(-16), 0))
    sheen.visible_shadow = False
    # ---- the garden behind: terrace, hedge, trees, flowers, sky wall
    B((14, 20, 2.1), (1.2, 13.4, 1.8), P("#8fae80", 0.85, 0.05), "lawn", 0.0)
    B((14, 0.4, 3.2), (1.2, 8.8, 4.4), P("#b9c9ae", 0.9, 0.05), "hedge", 0.05)
    ctx["sway"] = []
    for i in range(7):
        o = B((0.9, 0.5, 0.5 + 0.12 * (i % 3)), (-3.4 + i * 1.4, 8.6, 5.7 + 0.08 * (i % 2)), P("#a3bb98", 0.9), "hedgetop", 0.12)
        ctx["sway"].append((o, o.location.copy(), i * 0.9, 0.5))
    B((0.45, 0.45, 2.4), (3.9, 6.4, 4.05), P("#8a5a35", 0.8), "trunk", 0.04)
    for (dx, dy, dz, s) in ((0, 0, 3.0, 1.9), (0.5, 0.2, 3.5, 1.5), (-0.5, -0.2, 3.1, 1.4), (0.2, 0.4, 3.9, 1.1)):
        B((s, s, s * 0.8), (3.9 + dx, 6.4 + dy, 2.85 + dz + 0.5), P("#7fa56e", 0.9), "leaf", 0.2)
    for i in range(14):
        B((0.14, 0.14, 0.14), (-0.6 + (i * 0.37) % 4.4, 5.0 + (i * 0.53) % 2.2, 2.92),
          P(("#ff6f91", "#ffd23c", "#ffffff")[i % 3], 0.6), "flower", 0.04)
    # leafy sprigs right behind the man: the only thing in any frame that moves by itself
    for i, (lx, lz, ls, col) in enumerate(((0.78, 4.85, 0.3, "#6fa55c"), (0.95, 4.2, 0.26, "#5f9a58"), (1.62, 4.7, 0.32, "#79ad62"),
                                           (1.5, 4.05, 0.26, "#66a05a"), (0.72, 3.8, 0.24, "#7db36a"), (1.68, 5.0, 0.26, "#5f9a58"))):
        o = B((ls, ls * 0.6, ls * 0.9), (lx, 5.2, lz), P(col, 0.9), "sprig", 0.08)
        ctx["sway"].append((o, o.location.copy(), 1.7 * i, 1.0))
    B((40, 0.5, 20), (1.2, 22, 8), P("#a8dcff", 0.9, 0.0), "skywall", 0.0)
    B((40, 40, 0.3), (1.2, 8, 12), P("#a8dcff", 0.9, 0.0), "skyroof", 0.0)
    # ---- the garden door at the hall's end: white frame, sage glass, a brass lever that dips at the click
    dwx = DOOR_X
    for (sx, sz, lx, lz) in ((0.1, 3.3, dwx - 0.7, 1.05), (0.1, 3.3, dwx + 0.7, 1.05)):
        B((sx, 0.12, sz), (lx, WALL_Y - 0.06, lz), wf, "dpost", 0.02)
    for lz in (2.65, -0.55):
        B((1.5, 0.12, 0.1), (dwx, WALL_Y - 0.06, lz), wf, "dbar", 0.02)
    B((1.3, 0.12, 0.08), (dwx, WALL_Y - 0.06, 1.3), wf, "dmid", 0.02)
    B((0.07, 0.12, 3.0), (dwx - 0.02, WALL_Y - 0.06, 1.05), wf, "dstile", 0.02)
    sage = P("#b9dcae", 0.2, 0.6)
    for lx in (dwx - 0.38, dwx + 0.36):
        for (zc, hh) in ((0.38, 1.7), (2.0, 1.1)):
            B((0.4, 0.02, hh), (lx, WALL_Y - 0.035, zc), sage, "dglass", 0.0)
    B((0.1, 0.03, 0.26), (dwx + 0.55, WALL_Y - 0.14, 1.0), P("#d9a441", 0.25, 0.9), "rose", 0.01)
    ctx["lever"] = kit.empty("leverpivot", (dwx + 0.55, WALL_Y - 0.17, 1.06))
    B((0.36, 0.04, 0.05), (-0.14, 0, 0), P("#e8b84a", 0.2, 0.95), "lever", 0.012, parent=ctx["lever"])
    B((0.05, 0.04, 0.05), (0.05, 0, 0), P("#e8b84a", 0.2, 0.95), "levernub", 0.012, parent=ctx["lever"])
    # ---- the two floor shadows (yours, then the second one)
    shm = P("#4e2a1a", 0.9, 0.0)
    ctx["shadow1"] = figure(kit, "shadow1", -0.45, -4.9, 1.0, shm)
    ctx["shadow2"] = figure(kit, "shadow2", 1.7, -4.9, 1.14, shm)
    # ---- the countdown clock
    build_hud(kit, ctx)
    # ---- lights: warm hall wash, camera fill, the daylight on the man
    ctx["wash"] = kit.light("wash", "AREA", (0, -4.0, 8.0), 170, "#fff1d8", size=9.0)
    kit.aim(ctx["wash"], (0, 3.0, 2.5))
    ctx["camfill"] = kit.light("camfill", "POINT", (0, -6, 3), 20, "#ffe9cf", size=0.6, shadow=False)
    # a camera-invisible shield just behind the glass keeps the hall's wash off the man; only the garden sun and sky reach him
    sh = B((1.6, 0.05, 3.2), (1.2, WALL_Y + 0.08, TOPZ), P("#000000"), "shield", 0.0)
    sh.visible_camera = False
    ctx["sun"] = kit.light("manlight", "SPOT", (2.2, -2.0, 7.9), 2400.0, "#fff0d0", size=0.05, spot=12, blend=0.35, shadow=True)
    kit.aim(ctx["sun"], (1.2, 3.65, 4.9))
    brow = B((0.5, 0.8, 0.05), (1.2, 3.25, 5.03), P("#000000"), "browshelf", 0.0)
    brow.visible_camera = False
    ctx["rim"] = kit.light("rim", "AREA", (2.5, 7.0, 6.5), 30, "#fff3d0", size=2.0, shadow=False)
    kit.aim(ctx["rim"], (1.2, 3.95, 4.3))
    # a soft low fill in front of him, linked to him only: just enough to open the shadow on the far eye
    ctx["manfill"] = kit.light("manfill", "POINT", (0.4, 1.6, 4.2), 22, "#e8f0ff", size=1.2, shadow=False)
    ctx["fogfill"] = kit.light("fogfill", "POINT", (1.5, 2.0, 4.9), 110, "#fff6ec", size=1.0, shadow=False)
    for l in ("rim", "camfill", "wash", "manfill", "fogfill"):
        ctx[l].visible_camera = False
    # a low hedge of flowers hides his hands and hips: only head and shoulders show, like a portrait
    hb = P("#9cc488", 0.9)
    B((1.1, 0.5, 0.15), (1.2, 3.35, 3.88), hb, "bed", 0.05)
    for i in range(7):
        B((0.1, 0.1, 0.1), (0.78 + i * 0.07, 3.2, 3.99 + 0.02 * (i % 2)), P(("#ff6f91", "#ffd23c", "#ffffff")[i % 3], 0.6), "bedflower", 0.03)
    return ctx


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def fog_level(t, t_fogs):
    """0..1 breath on the glass: a quick bloom, a slow clear, every 2 s, the cycle starting at L13's 'It FOGS'."""
    p = ((t - t_fogs) % 2.0) / 2.0
    if p < 0.25:
        return smooth(p / 0.25)
    return 1.0 - smooth((p - 0.25) / 0.75)


def animate(kit, story, tl, t, ctx):
    from blocky import timeline
    cue = lambda n, d=0.0: timeline.cue(tl, n, d)
    t_sweep, t_chime, t_snap = cue("sweep"), cue("chime"), cue("snap")
    t_gone, t_latch, t_second = cue("gone"), cue("latch"), cue("second")
    # ---- the breath on the glass (matte grey, on the garden side), gone when he is
    u = fog_level(t, cue("fogs", 16.4)) if t < t_gone else 0.0
    early = 0.7 if t < t_chime else 1.0
    s = (0.55 + 0.45 * u) * (0.78 if t < t_chime else 1.0)
    fx, fz = ctx["fog_base"]
    ctx["fog"].scale = (s, s, s)
    ctx["fog"].location = (fx + 0.05 * u, ctx["fog"].location[1], fz)
    k_ = 0.0 if t >= t_gone else min(0.85, u * 0.85 * early + 0.01)
    ctx["fog_str"].color = (k_, k_, k_, 1.0)
    ctx["fog"].hide_render = t >= t_gone or u < 0.01
    # ---- the man's light: flat and dim behind the glass until the chime, then up over 0.6 s
    g = 0.3 + 0.7 * smooth((t - t_chime) / 0.6)
    if not ctx.get("flinked"):   # a soft light that lights only the breath
        col2 = bpy.data.collections.new("fog only")
        col2.objects.link(ctx["fog"])
        ctx["fogfill"].light_linking.receiver_collection = col2
        for co in col2.collection_objects:
            co.light_linking.link_state = "INCLUDE"
        ctx["flinked"] = True
    over = {"manlight": g, "rim": 0.55 + 0.45 * smooth((t - t_chime) / 0.6), "manfill": g}
    if not ctx.get("linked"):   # his lights light only him: no spill circle on the wall
        man = bpy.data.objects.get("watcher")
        if man is not None:
            objs = [man] + list(man.children_recursive)
            col = bpy.data.collections.new("man only")
            for ob in objs:
                if ob.type == "MESH":
                    col.objects.link(ob)
            for nm_ in ("sun", "manfill"):
                ctx[nm_].light_linking.receiver_collection = col
                for co in col.collection_objects:
                    co.light_linking.link_state = "INCLUDE"
            ctx["linked"] = True
    # ---- the countdown hand sweeps from L02 to the chime, then rings
    hud = ctx["hud"]
    f = max(0.0, min(1.0, (t - t_sweep) / max(0.1, t_chime - t_sweep)))
    if t >= t_second + 0.5:
        f = 0.0   # the loop: the countdown starts over
    ang = CHIME_A + (360.0 - CHIME_A) * f
    ctx["hand"].rotation_euler = (0, 0, -math.radians(ang))
    for w, a in ctx["wedges"]:
        w.hide_render = a < ang
    big = smooth((t - t_chime) / 0.25) * (1.0 - smooth((t - (t_snap - 0.05)) / 0.05))
    hud.scale = (1 + 0.9 * big,) * 3
    hud.location = (HUD_POS[0] + 0.078 * big, HUD_POS[1] - 0.06 * big, HUD_POS[2])
    ring = max(0.0, 1.0 - (t - t_chime) / 0.5) if t >= t_chime else 0.0
    hud.rotation_euler = (0, 0, math.radians(7) * ring * math.sin(46 * (t - t_chime)))
    # ---- the garden: sprigs and hedge tops sway a little
    for o, base, ph, k in ctx["sway"]:
        o.location = (base[0] + 0.03 * k * math.sin(1.7 * t + ph), base[1], base[2] + 0.015 * k * math.sin(2.3 * t + ph))
        o.rotation_euler = (0, 0.07 * k * math.sin(1.9 * t + ph), 0.05 * k * math.sin(1.3 * t + 2 * ph))
    # ---- the lever dips at the click and comes back
    dip = smooth((t - t_latch) / 0.08) * (1.0 - smooth((t - t_latch - 0.55) / 0.25)) if t >= t_latch else 0.0
    ctx["lever"].rotation_euler = (0, math.radians(-26) * dip, 0)
    # ---- the second shadow slides in beside yours
    k = smooth((t - t_second) / 0.4)
    ctx["shadow2"].location = (1.7 + (0.55 - 1.7) * k, -4.9, FLOOR_TOP + 0.016)
    for ob in ctx["shadow2"].children:
        ob.hide_render = t < t_second - 0.05
    for ob in ctx["shadow1"].children:
        ob.hide_render = t < cue("floor", 31.0)
    return over
