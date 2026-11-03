"""ep88-six-paintings: a bright oxblood gallery hall, six frames A-F, and frame C is really a window.

Built by hand from kit.py's parts. No text anywhere: the plaque letters are block glyphs of boxes, our own markers.
World (m, z up): long wall at y 2.9 (front face), camera side is -y. Grid columns x -1.2, 0, 1.2; top row frame
centre z 4.15, bottom row 1.6; frames are 1.1 x 2.0 outside, canvas 0.9 x 1.8. C (top right) is an opening in the wall
with a white window frame and glass; the garden terrace (top z 2.85) lies behind it and the watcher stands on it.
The rule meter: the brass clock-face countdown top-left (its hand sweeps to a red chime mark), and the gold plaques.
"""
from __future__ import annotations

import math

import bpy
from mathutils import Vector as V

from blocky import kit as _kit  # noqa: F401

GX = (-1.2, 0.0, 1.2)
TOPZ, BOTZ = 4.15, 1.4
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
    canvas(cx, cz, "#f3e4c4")
    paint(cx, cz, -0.1, -0.35, 0.62, 0.9, "#2f6fd3", 2)       # blue dress
    paint(cx, cz, -0.1, 0.14, 0.34, 0.4, "#f0c29c", 3)         # face
    paint(cx, cz, -0.1, 0.4, 0.44, 0.24, "#7a4421", 4)         # hair
    paint(cx, cz, -0.1, 0.0, 0.2, 0.05, "#c4584a", 4)          # mouth
    paint(cx, cz, -0.18, 0.18, 0.05, 0.05, "#1a1a22", 4)
    paint(cx, cz, -0.02, 0.18, 0.05, 0.05, "#1a1a22", 4)
    # the greyhound in side view, lower right, facing right: deep chest, tucked belly, long legs, a long snout
    gr, dk = "#aeb5c0", "#7b8390"
    paint(cx, cz, 0.04, -0.58, 0.46, 0.15, gr, 5)              # back and flank
    paint(cx, cz, 0.18, -0.64, 0.2, 0.24, gr, 5)               # deep chest
    paint(cx, cz, -0.08, -0.65, 0.14, 0.08, dk, 6)             # tucked belly shade
    for dx in (0.2, 0.28):
        paint(cx, cz, dx, -0.84, 0.05, 0.24, gr, 5)            # front legs
    for dx in (-0.1, -0.02):
        paint(cx, cz, dx, -0.84, 0.05, 0.24, dk, 5)            # rear legs
    paint(cx, cz, -0.24, -0.62, 0.2, 0.04, gr, 5, rot=0.5)     # tail
    paint(cx, cz, 0.26, -0.42, 0.09, 0.26, gr, 5, rot=-0.25)   # long neck
    paint(cx, cz, 0.3, -0.27, 0.12, 0.1, gr, 6)                # skull
    paint(cx, cz, 0.39, -0.3, 0.17, 0.05, gr, 6)               # long snout
    paint(cx, cz, 0.465, -0.3, 0.03, 0.03, "#15151c", 7)       # nose
    paint(cx, cz, 0.26, -0.22, 0.05, 0.1, dk, 7, rot=0.4)      # ear
    paint(cx, cz, 0.33, -0.26, 0.03, 0.03, "#101018", 7)       # eye


def subject_D(cx, cz):
    canvas(cx, cz, "#27463f")
    paint(cx, cz, 0, -0.75, 0.9, 0.3, "#7a4a2a", 1)            # table
    for dx, up, c in ((-0.25, -0.06, "#d7e04a"), (0.0, 0.08, "#c8d83a"), (0.25, -0.06, "#e8ec6a")):
        paint(cx, cz, dx, -0.2 + up, 0.3, 0.3, c, 2)            # pear belly
        paint(cx, cz, dx, 0.02 + up, 0.2, 0.2, c, 2)            # pear shoulder
        paint(cx, cz, dx, 0.2 + up, 0.12, 0.2, c, 2)            # pear neck, narrow
        paint(cx, cz, dx + 0.01, 0.34 + up, 0.03, 0.08, "#4a2c14", 3)  # stalk
    paint(cx, cz, 0, -0.42, 0.78, 0.1, "#d4502a", 5)            # bowl rim
    paint(cx, cz, 0, -0.55, 0.58, 0.18, "#b23c20", 5)           # bowl belly
    paint(cx, cz, 0, -0.66, 0.3, 0.06, "#8a2c16", 5)            # foot
    paint(cx, cz, 0.3, 0.55, 0.2, 0.12, "#4a7a5c", 3)          # leaf


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
    m = kit._new(nm("fog"))
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Location"].default_value = (0, 0, 0)
    mp.inputs["Scale"].default_value = (5.0, 5.0, 5.0)
    mp.vector_type = "POINT"
    gr = nt.nodes.new("ShaderNodeTexGradient")
    gr.gradient_type = "QUADRATIC_SPHERE"
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].position = 0.0
    rp.color_ramp.elements[0].color = (0, 0, 0, 1)
    rp.color_ramp.elements[1].position = 1.0
    rp.color_ramp.elements[1].color = (0.6, 0.6, 0.6, 1)
    rp.color_ramp.interpolation = "EASE"
    nt.links.new(tc.outputs["Object"], mp.inputs[0])
    nt.links.new(mp.outputs[0], gr.inputs[0])
    nt.links.new(gr.outputs["Fac"], rp.inputs["Fac"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.95, 0.97, 1.0, 1)
    em.inputs["Strength"].default_value = 1.0
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(rp.outputs["Color"], mx.inputs["Fac"])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    return m


def pane_material(kit):
    m = kit._new(nm("pane"))
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.05
    gl.inputs["Color"].default_value = (0.85, 0.92, 1.0, 1)
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs["Fac"].default_value = 0.03
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    return m


def build_clock(kit):
    cx, cz, y = -1.35, 6.2, WALL_Y - 0.1
    rot = (math.pi / 2, 0, 0)
    kit.cyl(nm("clockrim"), 0.55, 0.1, (cx, y, cz), P("#d9a441", 0.25, 0.9), None, rot, 32)
    kit.cyl(nm("clockface"), 0.46, 0.05, (cx, y - 0.04, cz), P("#fff6dc", 0.5, 0.1), None, rot, 32)
    ink = P("#3a1016", 0.6, 0.1)
    for k in range(12):
        a = k * math.pi / 6
        L = 0.1 if k % 3 == 0 else 0.05
        B((0.035, 0.02, L), (cx + 0.38 * math.sin(a), y - 0.075, cz + 0.38 * math.cos(a)), ink, "tick", 0.0,
          rot=(0, -a, 0))
    # red chime mark at 12 and the hand sweeping toward it (at about 10:30 now)
    B((0.07, 0.02, 0.14), (cx, y - 0.08, cz + 0.36), P("#d02a2a", 0.4, 0.2), "mark", 0.0)
    a = -math.radians(50)
    B((0.045, 0.02, 0.36), (cx + 0.18 * math.sin(a), y - 0.09, cz + 0.18 * math.cos(a)), P("#1a1014", 0.5, 0.2),
      "hand", 0.0, rot=(0, -a, 0))
    # red wedge from the hand to the chime mark: a fan of thin red slivers on the face
    n = 16
    verts = [(0.0, 0.0, 0.0)] + [(0.4 * math.sin(a * (1 - i / n)), 0.4 * math.cos(a * (1 - i / n)), 0.0) for i in range(n + 1)]
    faces = [(0, i + 1, i + 2) for i in range(n)]
    kit.mesh_obj(nm("wedge"), verts, faces, P("#e0302a", 0.9, 0.0), None, (cx, y - 0.075, cz),
                 (math.pi / 2, 0, 0))
    kit.cyl(nm("hub"), 0.05, 0.03, (cx, y - 0.1, cz), P("#d9a441", 0.25, 0.9), None, rot, 12)


def build(kit, story, tl):
    K.kit = kit
    ctx = {}
    oxb = P("#6c1a26", 0.7, 0.1)
    # ---- floor, wall (with the window opening), skirting
    B((16, 14, 0.2), (0, -2.0, -0.1), P("#9a6439", 0.25, 0.5), "floor", 0.0)
    wy, wd = WALL_Y + 0.2, 0.4
    wx0, wx1, wz0, wz1 = 0.65, 1.75, 3.15, 5.15      # window opening in C's frame cell
    H = 8.0
    def seg(x0, x1, z0, z1):
        B((x1 - x0, wd, z1 - z0), ((x0 + x1) / 2, wy, (z0 + z1) / 2), oxb, "wall", 0.0)
    seg(-8, wx0, 0, H)
    seg(wx1, 8, 0, H)
    seg(wx0, wx1, 0, wz0)
    seg(wx0, wx1, wz1, H)
    B((16, 0.02, 0.3), (0, WALL_Y - 0.01, 0.15), P("#d9c9a8", 0.5, 0.2), "skirt", 0.004)
    B((16, 0.04, 0.12), (0, WALL_Y - 0.03, 2.55), P("#5d1520", 0.6, 0.1), "rail", 0.004)
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
    # ---- C: white-painted window frame, sill, glass, fog circle on the far side
    wf = P("#fbfaf4", 0.55, 0.2)
    cx, cz = 1.2, TOPZ
    yf = WALL_Y - 0.05
    for (w, h, dx, dz) in ((1.1, 0.1, 0, 0.95), (1.1, 0.1, 0, -0.95), (0.1, 1.8, -0.5, 0), (0.1, 1.8, 0.5, 0)):
        B((w, 0.2, h), (cx + dx, yf, cz + dz), wf, "wframe", 0.015)
    B((1.3, 0.16, 0.07), (cx, WALL_Y - 0.16, cz - 1.0), wf, "wsill", 0.01)
    B((0.07, 0.04, 0.12), (cx + 0.38, WALL_Y - 0.17, cz - 0.4), P("#d9a441", 0.25, 0.9), "wlatch", 0.005)
    ctx["pane"] = kit.plane(nm("pane"), (0.9, 1.8), (cx, WALL_Y + 0.05, cz), pane_material(kit), None,
                            rot=(math.pi / 2, 0, 0))
    ctx["pane"].visible_shadow = False
    ctx["fog"] = kit.plane(nm("fogdisc"), (0.4, 0.4), (cx + 0.0, WALL_Y + 0.2, cz + 0.42), fog_material(kit), None,
                           rot=(math.pi / 2, 0, 0))
    ctx["fog"].visible_shadow = False
    # ---- the garden behind: terrace, hedge, trees, flowers, sky wall
    B((14, 20, 2.1), (1.2, 13.4, 1.8), P("#8fae80", 0.85, 0.05), "lawn", 0.0)
    B((14, 0.4, 3.2), (1.2, 8.8, 4.4), P("#b9c9ae", 0.9, 0.05), "hedge", 0.05)
    for i in range(7):
        B((0.9, 0.5, 0.5 + 0.12 * (i % 3)), (-3.4 + i * 1.4, 8.6, 5.7 + 0.08 * (i % 2)), P("#a3bb98", 0.9), "hedgetop", 0.12)
    B((0.45, 0.45, 2.4), (3.9, 6.4, 4.05), P("#8a5a35", 0.8), "trunk", 0.04)
    for (dx, dy, dz, s) in ((0, 0, 3.0, 1.9), (0.5, 0.2, 3.5, 1.5), (-0.5, -0.2, 3.1, 1.4), (0.2, 0.4, 3.9, 1.1)):
        B((s, s, s * 0.8), (3.9 + dx, 6.4 + dy, 2.85 + dz + 0.5), P("#7fa56e", 0.9), "leaf", 0.2)
    for i in range(14):
        B((0.14, 0.14, 0.14), (-0.6 + (i * 0.37) % 4.4, 5.0 + (i * 0.53) % 2.2, 2.92),
          P(("#ff6f91", "#ffd23c", "#ffffff")[i % 3], 0.6), "flower", 0.04)
    B((40, 0.5, 20), (1.2, 22, 8), P("#a8dcff", 0.9, 0.0), "skywall", 0.0)
    B((40, 40, 0.3), (1.2, 8, 12), P("#a8dcff", 0.9, 0.0), "skyroof", 0.0)
    # ---- the clock
    build_clock(kit)
    # ---- lights: warm hall wash, camera fill, the daylight on the man (no shadow)
    ctx["wash"] = kit.light("wash", "AREA", (0, -4.0, 8.0), 170, "#fff1d8", size=9.0)
    kit.aim(ctx["wash"], (0, 3.0, 2.5))
    ctx["camfill"] = kit.light("camfill", "POINT", (0, -6, 3), 20, "#ffe9cf", size=0.6, shadow=False)
    # a camera-invisible shield just behind the glass keeps the hall's wash off the man; only the garden sun and sky reach him
    sh = B((1.6, 0.05, 3.2), (1.2, WALL_Y + 0.08, TOPZ), P("#000000"), "shield", 0.0)
    sh.visible_camera = False
    ctx["sun"] = kit.light("manlight", "SUN", (8.0, 5.2, 5.4), 9.0, "#fff2d6", shadow=True)
    kit.aim(ctx["sun"], (1.2, 3.95, 4.7))
    ctx["rim"] = kit.light("rim", "AREA", (2.5, 7.0, 6.5), 30, "#fff3d0", size=2.0, shadow=False)
    kit.aim(ctx["rim"], (1.2, 3.95, 4.3))
    return ctx


def animate(kit, story, tl, t, ctx):
    # the fog circle grows and fades every 2 s
    u = 0.5 - 0.5 * math.cos(math.pi * (t % 2.0))
    s = 0.35 + 0.45 * u
    ctx["fog"].scale = (s, s, s)
    return {}
