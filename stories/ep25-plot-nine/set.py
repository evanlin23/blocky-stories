"""Plot nine (ep25): allotment gardens on a hillside at dawn in a dry spring. Built from kit.py's parts; nothing here is
shared with another story's set. There is no text anywhere in the set: stakes, sheds and seed packets are plain.

Coordinates (metres): the gate is at y = 0, the path runs down the hill along -y (x -0.75 .. 0.75), odd plots on the
left (x > 0), even on the right (x < 0), five rows of 5 m: row r spans y = -1.5 - 6r .. -6.5 - 6r. Plot nine is
x 1..6, y -25.5 .. -30.5, Mr. Carter's shed at its path corner (x 1.0 .. 2.4, y -27.6 .. -25.8), the door on its +x
face. The ground is flat; the hill falls away past the bottom fence (y = -32). Interiors sit off to the side: Mr.
Carter's shed at x = 60, plot ten's shed at x = 80, the shaft under the hole at x = 120.

THE DIGGER (the creature). One model, built once, posed by the "digger" cues: which plot, how far its shoulders stand
above the soil ("up"), the body's yaw and the head's own yaw. It's a blocky person built from our blocks but too
long: the torso and both arms are 4 m boxes that go on down into the ground. Packed soil and pale tan roots wound
round the head and shoulders. No mouth, no nose; two small seed-green points close together set in two dark pits.
It is never seen moving: every change of place or height is across a cut.

Cues read here: tod (time of day / light, with an optional ramp), digger, holes, mound, key, can, torch, spade,
pebble, cane, bucket, bike, padlock, sprinkle, gate, shed, greens.
"""

from __future__ import annotations

import math
import random

import bpy
from mathutils import Matrix
from mathutils import Vector as V

from blocky import faces, rig

RIG_S = 0.34
HOLE_R = 0.68
DIG = {1: (3.4, -3.6), 4: (-3.6, -10.0), 7: (3.4, -22.0), 9: (3.85, -28.8)}
FOGC = "#b3aaa9"
WORLD_UP = V((0, 0, 1))

# time of day: key sun, character-only fill, sky strength, horizon and zenith, fog density and brightness
TOD = {
    "dawn":    dict(sun=7.5, sunc="#ffb184", fill=1.5, fillc="#a5b8e6", sky=1.1, hor="#e8bba4", zen="#87a2c9", fogd=0.016, fogb=0.95),
    "day":     dict(sun=8.5, sunc="#fff0d8", fill=1.4, fillc="#b4c6ea", sky=1.5, hor="#cfd3dc", zen="#8fb0da", fogd=0.014, fogb=1.0),
    "gold":    dict(sun=8.5, sunc="#ffbf70", fill=1.4, fillc="#a5b8e6", sky=1.1, hor="#f0b88a", zen="#8aa4c8", fogd=0.016, fogb=0.95),
    "early":   dict(sun=2.8, sunc="#a8bcff", fill=1.8, fillc="#8fa6e0", sky=0.8, hor="#aeb6d8", zen="#5f78b0", fogd=0.016, fogb=0.7),
    "fog":     dict(sun=2.6, sunc="#ffe2c0", fill=2.2, fillc="#c4cfe6", sky=1.5, hor="#a9a8ad", zen="#98a2b4", fogd=0.075, fogb=0.8),
    "fogthin": dict(sun=5.5, sunc="#ffd9a8", fill=1.8, fillc="#c4cfe6", sky=1.5, hor="#d8c9bd", zen="#9fb2cf", fogd=0.04, fogb=1.0),
    "clear":   dict(sun=8.0, sunc="#ffe0b8", fill=1.5, fillc="#b4c6ea", sky=1.3, hor="#e6cdb8", zen="#8fb0da", fogd=0.014, fogb=1.0),
    "dusk":    dict(sun=7.0, sunc="#ff9a5e", fill=1.3, fillc="#9fb0dc", sky=1.0, hor="#e8a682", zen="#7f93c0", fogd=0.016, fogb=0.9),
    "sunrise": dict(sun=8.0, sunc="#ffc088", fill=1.4, fillc="#a5b8e6", sky=1.2, hor="#ecc0a0", zen="#8aa8d0", fogd=0.014, fogb=1.0),
    "goldend": dict(sun=9.0, sunc="#ffc47c", fill=1.4, fillc="#b0c0e8", sky=1.2, hor="#f2c49a", zen="#92acd2", fogd=0.014, fogb=1.0),
    "night":   dict(sun=3.2, sunc="#8aa2f0", fill=1.4, fillc="#7f96d8", sky=0.9, hor="#3b4a76", zen="#1c2848", fogd=0.014, fogb=0.5),
}
SUN_DIR = V((0.88, 0.3, 0.2)).normalized()
FILL_DIR = V((-0.7, 0.2, 0.55)).normalized()


# ------------------------------------------------------------------------------------------------ helpers
def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def _last(cs, t):
    cs = [c for c in cs if c["t"] <= t + 1e-9]
    return cs[-1] if cs else None


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _eased(cs, key, t, default):
    level = prev = default
    for c in cs:
        if c["t"] > t + 1e-9 or key not in c:
            continue
        prev, level = level, c[key]
        d = float(c.get("dur", 0.0))
        if d > 0 and t < c["t"] + d and isinstance(level, (int, float)) and isinstance(prev, (int, float)):
            level = prev + (level - prev) * _ss((t - c["t"]) / d)
    return level


def _switch(keys, attr, t, default):
    v = default
    for k in keys:
        if attr in k and k["t"] <= t + 1e-9:
            v = k[attr]
    return v


def _show(objs, on):
    for o in objs:
        for oo in [o] + list(o.children_recursive):
            oo.hide_render = not on


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _lin(c):
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def _mixc(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


def rod(kit, name, p0, p1, r, mat, parent=None, n=8):
    a, b = V(p0), V(p1)
    d = b - a
    ob = kit.cyl(name, r, d.length, tuple((a + b) / 2), mat, parent, n=n)
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return ob


def torus(kit, name, R, r, loc, mat, parent=None, rot=(0, 0, 0), n=28, m=6, scale=(1, 1, 1)):
    verts, fcs = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        for j in range(m):
            b = 2 * math.pi * j / m
            rr = R + r * math.cos(b)
            verts.append((rr * math.cos(a), rr * math.sin(a), r * math.sin(b)))
    for i in range(n):
        for j in range(m):
            i2, j2 = (i + 1) % n, (j + 1) % m
            fcs.append((i * m + j, i2 * m + j, i2 * m + j2, i * m + j2))
    ob = kit.mesh_obj(name, verts, fcs, mat, parent, loc, rot, smooth=True)
    ob.scale = scale
    return ob


def pbr(kit, name, hexc, rough=0.6, metal=0.0, spec=0.4, noise=None, bump=0.0, coat=0.0):
    """A Principled material through kit's fog. noise = (scale, dark factor, rough variation)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = spec
            break
    if coat:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.1
    if noise:
        tc = N.new("ShaderNodeTexCoord")
        nz = N.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = noise[0]
        nz.inputs["Detail"].default_value = 6.0
        L.new(tc.outputs["Object"], nz.inputs["Vector"])
        ramp = N.new("ShaderNodeValToRGB")
        c = kit.col(hexc)
        ramp.color_ramp.elements[0].position = 0.3
        ramp.color_ramp.elements[0].color = (c[0] * noise[1], c[1] * noise[1], c[2] * noise[1], 1)
        ramp.color_ramp.elements[1].position = 0.7
        ramp.color_ramp.elements[1].color = c
        L.new(nz.outputs["Fac"], ramp.inputs["Fac"])
        L.new(ramp.outputs["Color"], b.inputs["Base Color"])
        if bump:
            bp = N.new("ShaderNodeBump")
            bp.inputs["Strength"].default_value = bump
            bp.inputs["Distance"].default_value = 0.03
            L.new(nz.outputs["Fac"], bp.inputs["Height"])
            L.new(bp.outputs["Normal"], b.inputs["Normal"])
        if noise[2]:
            rr = N.new("ShaderNodeMapRange")
            rr.inputs["To Min"].default_value = max(0.02, rough - noise[2])
            rr.inputs["To Max"].default_value = min(1.0, rough + noise[2])
            L.new(nz.outputs["Fac"], rr.inputs["Value"])
            L.new(rr.outputs["Result"], b.inputs["Roughness"])
    m.diffuse_color = kit.col(hexc)
    kit._fogged(m, b.outputs[0])
    return m


def cracked(kit, name, base, dark, scale=3.2):
    """Sun-baked clay: a Voronoi edge distance makes the cracks (dark and sunk), noise mottles the crust."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    vor = N.new("ShaderNodeTexVoronoi")
    vor.feature = "DISTANCE_TO_EDGE"
    vor.inputs["Scale"].default_value = scale
    L.new(tc.outputs["Object"], vor.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].position = 0.0
    cr.color_ramp.elements[0].color = kit.col(dark)
    cr.color_ramp.elements[1].position = 0.03
    cr.color_ramp.elements[1].color = (1, 1, 1, 1)
    L.new(vor.outputs["Distance"], cr.inputs["Fac"])
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 5.0
    nz.inputs["Detail"].default_value = 6.0
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    mot = N.new("ShaderNodeValToRGB")
    mot.color_ramp.elements[0].position = 0.35
    mot.color_ramp.elements[0].color = tuple(v * 0.8 for v in kit.col(base)[:3]) + (1,)
    mot.color_ramp.elements[1].position = 0.7
    mot.color_ramp.elements[1].color = kit.col(base)
    L.new(nz.outputs["Fac"], mot.inputs["Fac"])
    mix = N.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 1.0
    L.new(mot.outputs["Color"], mix.inputs["A"])
    L.new(cr.outputs["Color"], mix.inputs["B"])
    L.new(mix.outputs["Result"], b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.3
    bp.inputs["Distance"].default_value = 0.04
    L.new(cr.outputs["Color"], bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.92
    m.diffuse_color = kit.col(base)
    kit._fogged(m, b.outputs[0])
    return m


def materials(kit):
    M = {}
    M["clay"] = cracked(kit, "clay", "#a89878", "#6e5c44", 7.5)
    M["clay2"] = cracked(kit, "clay2", "#b3a384", "#74634a", 6.0)
    M["wet"] = pbr(kit, "wet soil", "#4c3827", 0.38, spec=0.55, noise=(3.0, 0.6, 0.12), bump=0.4)
    M["print"] = pbr(kit, "boot print", "#9c8c68", 0.9)
    M["dust"] = pbr(kit, "dust path", "#cdb88c", 0.95, noise=(2.5, 0.82, 0.0), bump=0.2)
    M["grass"] = pbr(kit, "dry grass", "#8d8458", 0.95, noise=(1.8, 0.7, 0.0))
    M["verge"] = pbr(kit, "verge", "#7a7a4c", 0.95, noise=(3.5, 0.6, 0.0))
    M["board"] = kit.planks("#8a7456", "#5d4c38", 1.2, "X", name="edge boards", rough=0.85)
    M["post"] = pbr(kit, "fence wood", "#6d5d46", 0.9, noise=(4.0, 0.7, 0.0))
    M["tar"] = kit.planks("#52453a", "#372d25", 1.4, "Z", name="tarred boards", rough=0.8)
    M["creosote"] = kit.planks("#6a4630", "#47301f", 1.2, "Z", name="creosote boards", rough=0.78)
    M["roof"] = pbr(kit, "roof felt", "#262626", 0.9)
    M["leaf"] = pbr(kit, "bean leaf", "#4f7a3a", 0.55, spec=0.35, noise=(7.0, 0.62, 0.0))
    M["leaf2"] = pbr(kit, "bean leaf b", "#5c8a40", 0.55, spec=0.35)
    M["wilt"] = pbr(kit, "wilt leaf", "#8a6a3a", 0.8, noise=(6.0, 0.65, 0.0))
    M["cane"] = pbr(kit, "cane", "#c4aa6c", 0.7)
    M["twine"] = pbr(kit, "twine", "#a78f5c", 0.9)
    M["iron"] = pbr(kit, "iron", "#2f3034", 0.38, metal=0.9, spec=0.5)
    M["iron2"] = pbr(kit, "iron light", "#6b6e72", 0.4, metal=0.8, spec=0.5)
    M["water"] = pbr(kit, "water", "#b8d3e6", 0.03, spec=1.0, coat=1.0)
    M["hole"] = pbr(kit, "hole black", "#010101", 1.0, spec=0.0)
    M["black"] = pbr(kit, "plug black", "#030303", 1.0, spec=0.0)
    M["soil"] = pbr(kit, "packed soil", "#4a3526", 0.62, spec=0.35, noise=(9.0, 0.55, 0.18), bump=0.8)
    M["soil2"] = pbr(kit, "packed soil b", "#5b4531", 0.8, noise=(13.0, 0.55, 0.0), bump=0.6)
    M["root"] = pbr(kit, "root", "#a88a62", 0.72, noise=(18.0, 0.62, 0.0), bump=0.5)
    M["pit"] = pbr(kit, "eye pit", "#050403", 1.0, spec=0.0)
    M["eye"] = kit.emit("#7fd02a", 3.2, name="eye seed")
    M["mound"] = pbr(kit, "mound", "#3d2c1f", 0.8, noise=(5.0, 0.6, 0.0), bump=0.5)
    M["green"] = pbr(kit, "can green", "#3f7a46", 0.42, metal=0.35, spec=0.5)
    M["steel"] = pbr(kit, "bucket steel", "#8e9296", 0.45, metal=0.8, spec=0.5)
    M["valley"] = pbr(kit, "valley", "#6f7a62", 1.0, noise=(0.4, 0.8, 0.0))
    M["hill"] = pbr(kit, "far hill", "#66745f", 1.0)
    M["tree"] = pbr(kit, "tree green", "#4f6a3a", 0.9, noise=(3.0, 0.6, 0.0))
    M["trunk"] = pbr(kit, "trunk", "#4d3a2c", 0.9)
    M["hedge"] = pbr(kit, "hedge", "#4e6335", 0.95, noise=(6.0, 0.55, 0.0))
    M["floor"] = pbr(kit, "bench floor", "#6f716f", 0.65, spec=0.3, noise=(0.7, 0.8, 0.0))
    M["hand"] = pbr(kit, "unfinished hand", "#b0a79c", 0.6, noise=(14.0, 0.8, 0.0))
    M["paper"] = pbr(kit, "seed paper", "#d9cfae", 0.9)
    M["oil"] = pbr(kit, "oil can", "#7a3b24", 0.5, metal=0.4)
    M["bikered"] = pbr(kit, "bike red", "#a8402e", 0.5, metal=0.2)
    M["tyre"] = pbr(kit, "tyre", "#141414", 0.9)
    M["wellig"] = pbr(kit, "welly green", "#2d6a38", 0.35, spec=0.6)
    M["wellid"] = pbr(kit, "welly dark", "#1f2c20", 0.4, spec=0.5)
    M["wetpants"] = pbr(kit, "wet trousers", "#2a2926", 0.4, spec=0.5)
    M["capwool"] = pbr(kit, "tweed cap", "#7b6d58", 0.95, noise=(25.0, 0.7, 0.0))
    M["pony"] = pbr(kit, "pony", "#4a2e1c", 0.7)
    M["zipstripe"] = pbr(kit, "zip stripe", "#efe4c4", 0.6)
    M["mous"] = pbr(kit, "moustache", "#9a9a98", 0.9)
    M["greenbed"] = pbr(kit, "green crop bed", "#44693a", 0.9, noise=(8.0, 0.55, 0.0))
    M["glow"] = kit.emit("#ffcf8a", 3.0, name="torch lens")
    M["lampglow"] = kit.emit("#ffd9a0", 4.0, name="lamp")
    return M


# ------------------------------------------------------------------------------------------------ plots
def plot_rect(n):
    row = (n - 1) // 2
    y0 = -1.5 - 6 * row
    left = n % 2 == 1
    return (1.0, 6.0, y0 - 5.0, y0) if left else (-6.0, -1.0, y0 - 5.0, y0)


SHEDS = {2: (-5.1, -2.6, -90), 3: (5.1, -8.4, 90), 4: (-5.2, -8.2, -90), 5: (5.1, -14.5, 90),
         6: (-5.1, -14.6, -90), 7: (5.2, -20.5, 90), 8: (-5.1, -20.4, -90), 10: (-5.2, -27.0, -90)}


def small_shed(kit, M, n, x, y, yaw):
    g = kit.empty(f"shed{n}", (x, y, 0), rot=(0, 0, math.radians(yaw)))
    kit.box(f"shed{n}.body", (1.3, 1.5, 1.8), (0, 0, 0.9), M["tar"], g, bevel=0.02)
    kit.box(f"shed{n}.roof", (1.5, 1.8, 0.07), (0, 0, 1.86), M["roof"], g, rot=(0.08, 0, 0), bevel=0.01)
    kit.box(f"shed{n}.door", (0.5, 0.04, 1.4), (-0.2, -0.77, 0.75), M["creosote"], g, bevel=0.01)
    return g


def build_gate(kit, M, ctx):
    for sx in (-1, 1):
        kit.box(f"gatepost{sx}", (0.17, 0.17, 1.75), (sx * 1.05, 0, 0.875), M["post"], bevel=0.02)
    leaves = {}
    for sx in (-1, 1):
        hinge = kit.empty(f"gateleaf{sx}", (sx * 1.0, 0, 0))
        w = 0.95
        cx = -sx * w / 2
        for k, z in enumerate((0.25, 0.5, 0.75, 1.0, 1.25)):
            kit.box(f"gate{sx}.bar{k}", (w, 0.045, 0.085), (cx, 0, z), M["post"], hinge, bevel=0.01)
        for tag, x in (("a", 0.03 * -sx), ("b", -sx * (w - 0.03))):
            kit.box(f"gate{sx}.stile{tag}", (0.06, 0.05, 1.32), (x, 0, 0.7), M["post"], hinge, bevel=0.01)
        d = kit.box(f"gate{sx}.brace", (math.hypot(w, 1.0), 0.04, 0.07), (cx, 0.01, 0.75), M["post"], hinge, bevel=0.01)
        d.rotation_euler = (0, math.atan2(1.0, w) * sx, 0)
        leaves[sx] = hinge
    ctx["leaves"] = leaves
    # the chain across the meeting stiles and the iron padlock hanging on it
    for k in range(7):
        x = -0.06 + 0.04 * k
        z = 1.08 - 0.05 * math.sin(math.pi * (k + 0.5) / 7)
        torus(kit, f"chain{k}", 0.014, 0.0045, (x, -0.035, z), M["iron2"], rot=(math.radians(90 if k % 2 else 0), 0, 0), n=14,
              m=5)
    pl = kit.empty("padlock", (0.1, -0.035, 0.98))
    kit.box("padlock.body", (0.075, 0.034, 0.06), (0, 0, 0), M["iron"], pl, bevel=0.008)
    torus(kit, "padlock.shackle", 0.022, 0.0065, (0, 0, 0.03), M["iron2"], pl, rot=(math.radians(90), 0, 0), n=18, m=5,
          scale=(1, 1, 1.15))
    kit.box("padlock.key", (0.009, 0.004, 0.02), (0, -0.018, -0.005), M["hole"], pl)
    rng = random.Random(5)
    beads = []
    for k in range(16):
        r = rng.uniform(0.0035, 0.0085)
        b = kit.sphere(f"bead{k}", r, (rng.uniform(-0.032, 0.032), -0.02, rng.uniform(-0.026, 0.025)), M["water"], pl, seg=8)
        beads.append(b)
    ctx["beads"] = beads
    streams = []
    for k, x in enumerate((-0.025, 0.005, 0.03)):
        s = kit.cyl(f"stream{k}", 0.0028, 0.55, (x, -0.02, -0.03 - 0.275), M["water"], pl, n=6)
        streams.append(s)
    ctx["streams"] = streams
    ctx["padlock"] = pl


def build_fence(kit, M):
    for side in (-1, 1):
        for k in range(14):
            y = -1.0 - k * 2.4
            kit.box(f"fp{side}_{k}", (0.12, 0.12, 1.1), (side * 7.4, y, 0.55), M["post"], bevel=0.015)
        for z in (0.45, 0.85):
            kit.box(f"fr{side}_{z}", (0.05, 32.6, 0.07), (side * 7.4, -16.3, z), M["post"])
    for k in range(7):
        x = -7.4 + k * 2.47
        kit.box(f"fb_{k}", (0.12, 0.12, 1.1), (x, -32.2, 0.55), M["post"], bevel=0.015)
    for z in (0.45, 0.85):
        kit.box(f"fbr_{z}", (14.9, 0.05, 0.07), (0, -32.2, z), M["post"])


def build_scenery(kit, M):
    kit.plane("ground", (140, 70), (0, 3, -0.012), M["grass"])
    # the lane up from the gate and the path down the hill
    kit.plane("path", (1.7, 70), (0, -16, 0.0), M["dust"])
    kit.plane("lane", (1.7, 40), (0, 22, 0.0), M["dust"])
    # the hill falls away beyond the bottom fence into a misty valley
    verts = [(-90, -32, 0), (90, -32, 0), (90, -95, -26), (-90, -95, -26), (-90, -420, -30), (90, -420, -30)]
    kit.mesh_obj("slope", verts, [(0, 1, 2, 3), (3, 2, 5, 4)], M["valley"], smooth=True)
    for k, (x, y, r, h) in enumerate(((-90, -190, 60, 55), (30, -230, 80, 70), (130, -170, 55, 45), (-20, -330, 120, 90),
                                       (-160, -280, 90, 60), (200, -300, 100, 65))):
        kit.cyl(f"farhill{k}", r, h, (x, y, h / 2 - 28), M["hill"], n=7, r2=r * 0.3)
    # hedge and trees up beyond the gate
    for side in (-1, 1):
        for k in range(4):
            kit.box(f"hedge{side}{k}", (3.2, 1.0, 1.7), (side * (2.6 + 3.2 * k), 3.2, 0.85), M["hedge"], bevel=0.3)
    rng = random.Random(9)
    for k in range(7):
        x, y = rng.uniform(-18, 18), rng.uniform(8, 30)
        if abs(x) < 3:
            x += 6
        kit.cyl(f"trunk{k}", 0.25, 3.2, (x, y, 1.6), M["trunk"], n=8)
        for j in range(3):
            kit.box(f"tree{k}_{j}", (3.2 - j * 0.8, 3.2 - j * 0.8, 1.6), (x, y, 3.6 + j * 1.1), M["tree"], bevel=0.35)


def build_plots(kit, M, ctx):
    rng = random.Random(21)
    for n in range(1, 11):
        x0, x1, y0, y1 = plot_rect(n)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if n == 9:
            kit.plane("plot9", (5, 5), (cx, cy, 0.001), M["wet"])
        else:
            kit.plane(f"plot{n}", (5, 5), (cx, cy, 0.001), M["clay" if n % 2 else "clay2"])
            for k in range(9):    # wilted leaves in rows
                lx, ly = x0 + 0.7 + (k % 3) * 1.8, y0 + 0.9 + (k // 3) * 1.6
                for j in range(3):
                    kit.box(f"wilt{n}_{k}_{j}", (0.2, 0.12, 0.02),
                            (lx + rng.uniform(-0.2, 0.2), ly + rng.uniform(-0.2, 0.2), 0.05 + 0.04 * j), M["wilt"],
                            rot=(rng.uniform(-0.5, 0.5), rng.uniform(-0.6, 0.6), rng.uniform(0, 3)), bevel=0.004)
        for tag, (bx, by, sx_, sy_) in (("n", (cx, y1, 5.1, 0.12)), ("s", (cx, y0, 5.1, 0.12)),
                                         ("w", (x0, cy, 0.12, 5.1)), ("e", (x1, cy, 0.12, 5.1))):
            kit.box(f"edge{n}{tag}", (sx_, sy_, 0.1), (bx, by, 0.05), M["board"], bevel=0.01)
        px = 0.95 if n % 2 else -0.95
        kit.box(f"stake{n}", (0.07, 0.07, 0.55), (px * 1.12, y1 - 0.2, 0.27), M["post"], bevel=0.01)
        if n in SHEDS:
            small_shed(kit, M, n, *SHEDS[n])
    # green-bed overlays for the spring (L64): shown by the "greens" cue
    ctx["greens"] = []
    for n in (1, 2, 3, 4, 5, 6, 7, 8, 10):
        x0, x1, y0, y1 = plot_rect(n)
        g = kit.empty(f"green{n}", ((x0 + x1) / 2, (y0 + y1) / 2, 0))
        kit.plane(f"green{n}.bed", (4.9, 4.9), (0, 0, 0.012), M["greenbed"], g)
        for k in range(16):
            kit.box(f"green{n}.lf{k}", (0.5, 0.4, 0.38), (-1.8 + (k % 4) * 1.2 + rng.uniform(-.2, .2),
                                                           -1.8 + (k // 4) * 1.2 + rng.uniform(-.2, .2), 0.2),
                    M["leaf2"], g, rot=(0, 0, rng.uniform(0, 3)), bevel=0.12)
        ctx["greens"].append(g)
    # plot nine: raised wet rows with bean wigwams, two rows 1.8 m apart
    x0, x1, y0, y1 = plot_rect(9)
    for rx in (2.9, 4.7):
        kit.box(f"row{rx}", (0.9, 4.6, 0.12), (rx, (y0 + y1) / 2, 0.06), M["wet"], bevel=0.05)
        for k in range(4):
            wy = y1 - 0.9 - k * 1.2
            if rx == 2.9 and k in (0, 2):
                continue
            wig = kit.empty(f"wig{rx}_{k}", (rx, wy, 0))
            for j, (ax, ay) in enumerate(((0.32, 0.32), (-0.32, 0.32), (0.32, -0.32), (-0.32, -0.32))):
                rod(kit, f"cane{rx}_{k}_{j}", (ax, ay, 0.0), (0, 0, 2.05), 0.011, M["cane"], wig, n=5)
            for j in range(15):
                z = rng.uniform(0.3, 1.8)
                u = 1 - z / 2.05
                lx, ly = rng.choice((-1, 1)) * 0.32 * u, rng.choice((-1, 1)) * 0.32 * u
                kit.box(f"lf{rx}_{k}_{j}", (0.2, 0.13, 0.015), (lx, ly, z), M["leaf" if j % 2 else "leaf2"], wig,
                        rot=(rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8), rng.uniform(0, 3)), bevel=0.005)
    # the drip leaf, bigger and bent down, where the first drop falls from
    kit.box("dripleaf", (0.26, 0.16, 0.012), (3.55, -27.5, 0.6), M["leaf"], rot=(0.4, 0, 0.3), bevel=0.004)
    # Mr. Carter's shed at the path corner, a door in its +x face
    sx0, sx1, sy0, sy1 = 1.0, 2.4, -27.6, -25.8
    h = 2.0
    t = 0.06
    kit.box("cs.back", (t, sy1 - sy0, h), (sx0 + t / 2, (sy0 + sy1) / 2, h / 2), M["creosote"])
    kit.box("cs.n", (sx1 - sx0, t, h), ((sx0 + sx1) / 2, sy1 - t / 2, h / 2), M["creosote"])
    kit.box("cs.s", (sx1 - sx0, t, h), ((sx0 + sx1) / 2, sy0 + t / 2, h / 2), M["creosote"])
    kit.box("cs.eN", (t, sy1 - -26.6, h), (sx1 - t / 2, (sy1 + -26.6) / 2, h / 2), M["creosote"])
    kit.box("cs.eS", (t, -27.3 - sy0, h), (sx1 - t / 2, (sy0 + -27.3) / 2, h / 2), M["creosote"])
    kit.box("cs.lintel", (t, 0.7, h - 1.75), (sx1 - t / 2, -26.95, 1.75 + (h - 1.75) / 2), M["creosote"])
    kit.box("cs.roof", (1.7, 2.1, 0.07), ((sx0 + sx1) / 2, (sy0 + sy1) / 2, h + 0.08), M["roof"], rot=(0, 0.07, 0), bevel=0.01)
    kit.box("cs.floor", (sx1 - sx0, sy1 - sy0, 0.04), ((sx0 + sx1) / 2, (sy0 + sy1) / 2, 0.02), M["black"])
    kit.box("cs.plug", (0.05, 0.74, 1.8), (sx1 - 0.14, -26.95, 0.9), M["black"])
    door = kit.empty("cs.hinge", (sx1, -27.3, 0))
    kit.box("cs.door", (0.045, 0.7, 1.75), (0, 0.35, 0.875), M["creosote"], door, bevel=0.008)
    kit.box("cs.handle", (0.03, 0.03, 0.12), (0.045, 0.6, 0.9), M["iron"], door)
    ctx["door"] = door
    # the boot prints: faint wet marks from the gate along the path, turning into plot nine
    pr = random.Random(2)
    k, y = 0, -0.9
    while y > -25.2:
        px_ = (0.14 if k % 2 else -0.12) + pr.uniform(-0.03, 0.03)
        a_ = pr.uniform(-0.12, 0.12)
        kit.box(f"print{k}", (0.1, 0.17, 0.004), (px_, y + 0.07, 0.004), M["print"], rot=(0, 0, a_))
        kit.box(f"printh{k}", (0.08, 0.06, 0.004), (px_, y - 0.1, 0.004), M["print"], rot=(0, 0, a_))
        y -= 0.62
        k += 1
    for j in range(3):
        kit.box(f"printT{j}", (0.12, 0.3, 0.004), (0.35 + 0.28 * j, -25.5 - 0.28 * j, 0.004), M["print"],
                rot=(0, 0, math.radians(35)), bevel=0.0)


# ------------------------------------------------------------------------------------------------ the Digger
def build_digger(kit, M, ctx):
    root = kit.empty("digger", (0, 0, -50))
    body = kit.empty("digger.body", (0, 0, 0), root)
    kit.box("digger.torso", (0.68, 0.34, 4.2), (0, 0, -2.1), M["soil"], body, bevel=0.035)
    for sx in (-1, 1):
        kit.box(f"digger.arm{sx}", (0.34, 0.34, 4.2), (sx * 0.51, 0, -2.1 + 0.0), M["soil"], body, bevel=0.03)
    # roots: a few thick strands wound down the shoulders and chest, never a neat pattern
    rng = random.Random(33)
    strands = [((-0.30, -0.18, -0.02), (-0.12, -0.19, -0.2), (0.12, -0.19, -0.42), (0.3, -0.18, -0.7)),
               ((0.34, -0.18, -0.02), (0.2, -0.19, -0.25), (0.0, -0.19, -0.5), (-0.2, -0.18, -0.85)),
               ((-0.62, -0.13, -0.02), (-0.5, -0.19, -0.2), (-0.6, -0.19, -0.5), (-0.45, -0.19, -0.95)),
               ((0.6, -0.13, -0.02), (0.52, -0.19, -0.3), (0.62, -0.19, -0.55), (0.5, -0.19, -1.0)),
               ((-0.3, 0.18, -0.02), (-0.1, 0.19, -0.25), (0.15, 0.19, -0.45), (0.3, 0.19, -0.8)),
               ((0.3, 0.18, -0.02), (0.1, 0.19, -0.3), (-0.15, 0.19, -0.55), (-0.3, 0.19, -0.9)),
               ((-0.6, 0.13, -0.02), (-0.5, 0.19, -0.35), (-0.6, 0.19, -0.7), (-0.5, 0.19, -1.1))]
    for k, st in enumerate(strands):
        for j in range(len(st) - 1):
            rod(kit, f"digger.root{k}_{j}", st[j], st[j + 1], 0.026 - 0.004 * j, M["root"], body, n=6)
    for sx in (-1, 1):
        kit.box(f"digger.shband{sx}", (0.37, 0.37, 0.045), (sx * 0.51, 0, -0.12), M["root"], body, rot=(0.0, sx * 0.08, 0), bevel=0.012)
    for k in range(46):    # clods
        x = rng.uniform(-0.78, 0.78)
        z = rng.uniform(-0.9, 0.03)
        yy = rng.choice((-1, 1)) * 0.175
        sz = rng.uniform(0.04, 0.12)
        kit.box(f"digger.clod{k}", (sz, sz * 0.7, sz * 0.8), (x, yy, z), M["soil2"], body,
                rot=(rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0, 3)), bevel=0.014)
    neck = kit.empty("digger.neck", (0, 0, 0.0), body)
    hs = kit.empty("digger.hs", (0, 0, 0.0), neck)
    hs.scale = (RIG_S, RIG_S, RIG_S * 1.22)
    hs.rotation_euler = (math.radians(5), 0, 0)
    headg = kit.empty("digger.headg", (0, 0, faces.HEAD_H / 2 + 0.02), hs)
    rig.head_mesh("digger.headm", M["soil"], headg)
    R = faces.HEAD_R
    for k, (z, tx, ty) in enumerate(((-0.4, 0.35, 0.1), (-0.05, -0.4, 0.2), (0.3, 0.3, -0.25))):
        torus(kit, f"digger.hring{k}", R + 0.01, 0.034, (0, 0, z), M["root"], headg, rot=(tx, ty, 0), n=36, m=6)
    for k in range(16):    # clods on the head
        a = rng.uniform(0, 2 * math.pi)
        sz = rng.uniform(0.07, 0.17)
        kit.box(f"digger.hclod{k}", (sz, sz * 0.8, sz * 0.7), (R * 0.97 * math.cos(a), R * 0.97 * math.sin(a),
                                                             rng.uniform(-0.5, 0.55)), M["soil2"], headg,
                rot=(rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0, 3)), bevel=0.02)
    # the face: two dark pits and two small seed-green points close together
    for sx in (-1, 1):
        pit = kit.sphere(f"digger.pit{sx}", 0.1, (sx * 0.15, -R + 0.03, 0.08), M["pit"], headg, seg=10)
        pit.scale = (0.8, 0.5, 1.5)
        eye = kit.sphere(f"digger.eye{sx}", 0.03, (sx * 0.15, -R - 0.012, 0.08), M["eye"], headg, seg=10)
        eye.scale = (0.7, 0.6, 1.8)
    nr = kit.empty("digger.neckroots", (0, 0, 0.02), body)
    for k in range(6):
        a = 2 * math.pi * k / 6
        rod(kit, f"digger.nroot{k}", (0.19 * math.cos(a), 0.12 * math.sin(a), -0.02),
            (0.15 * math.cos(a + 0.9), 0.1 * math.sin(a + 0.9), 0.16), 0.022, M["root"], nr, n=6)
    for sx in (-1, 1):   # a seam between torso and arm
        for yy in (-0.171, 0.171):
            kit.box(f"digger.seam{sx}{yy}", (0.012, 0.012, 1.3), (sx * 0.34, yy, -0.65), M["pit"], body)
    ctx["neckroots"] = nr
    ctx["digger"] = {"root": root, "body": body, "neck": neck}
    # the site: a ring of loosened soil and cracks round the base (travels with the root, flat on the ground)
    site = kit.empty("digger.site", (0, 0, 0), root)
    ring = kit.cyl("digger.ring", 0.92, 0.05, (0, 0, 0.0), M["mound"], site, n=24)
    for k in range(16):
        a = 2 * math.pi * k / 16 + rng.uniform(-0.1, 0.1)
        r = rng.uniform(0.7, 0.95)
        s = rng.uniform(0.12, 0.28)
        kit.box(f"digger.sclod{k}", (s, s * 0.8, s * 0.5), (r * math.cos(a), r * math.sin(a), 0.04), M["soil2"], site,
                rot=(0, 0, rng.uniform(0, 3)), bevel=0.03)
    for k in range(9):
        a = 2 * math.pi * k / 9 + rng.uniform(-0.2, 0.2)
        kit.box(f"digger.crack{k}", (0.03, 0.9, 0.006), (1.35 * math.cos(a), 1.35 * math.sin(a), 0.006), M["hole"], site,
                rot=(0, 0, a + math.pi / 2), bevel=0.0)
    ctx["site"] = site
    # a green glint of light from the eyes on the soil around them
    kit.light("digger eyes", "POINT", (0, -R - 0.18, 0.06), 1.0, "#9be04a", size=0.01, parent=headg)
    ctx["digger_parts"] = [root]


def build_holes(kit, M, ctx):
    ctx["holes"] = {}
    for n, (x, y) in DIG.items():
        g = kit.empty(f"hole{n}", (x, y, 0))
        kit.cyl(f"hole{n}.disc", HOLE_R, 0.006, (0, 0, 0.005), M["hole"], g, n=40)
        torus(kit, f"hole{n}.rim", HOLE_R + 0.03, 0.035, (0, 0, 0.012), M["clay2" if n != 9 else "mound"], g, n=40, m=6,
              scale=(1, 1, 0.6))
        ctx["holes"][n] = g
    # the mound I make filling plot nine's hole
    m = kit.empty("mound", (DIG[9][0], DIG[9][1], 0))
    for k in range(10):
        a = 2 * math.pi * k / 10
        s = 0.55 - 0.05 * (k % 3)
        b = kit.sphere(f"mound{k}", s, (0.35 * math.cos(a), 0.35 * math.sin(a), 0.0), M["mound"], m, seg=10)
        b.scale = (1, 1, 0.35)
    b = kit.sphere("mound.top", 0.7, (0, 0, 0), M["mound"], m, seg=12)
    b.scale = (1, 1, 0.4)
    ctx["mound"] = m
    # the pebble and the long cane
    ctx["pebble"] = kit.sphere("pebble", 0.025, (0, 0, -9), pbr(kit, "pebble", "#77726a", 0.8), seg=8)
    ctx["cane"] = rod(kit, "feedcane", (0, 0, 0), (0, 0, 2.6), 0.013, M["cane"], n=6)
    ctx["cane"].location = (0, 0, -9)


# ------------------------------------------------------------------------------------------------ props
def build_props(kit, M, ctx):
    # key on twine
    key = kit.empty("key", (0, 0, -9))
    kit.cyl("key.twine", 0.004, 0.14, (0, 0, 0.07), M["twine"], key, n=5)
    torus(kit, "key.bow", 0.016, 0.005, (0, 0, -0.016), M["iron2"], key, rot=(math.radians(90), 0, 0), n=14, m=5)
    kit.box("key.shaft", (0.008, 0.008, 0.07), (0, 0, -0.07), M["iron2"], key)
    kit.box("key.teeth", (0.02, 0.008, 0.012), (0.01, 0, -0.1), M["iron2"], key)
    ctx["key"] = key
    # the watering can, the origin at the grip, upright
    can = kit.empty("can", (0, 0, -9))
    kit.cyl("can.body", 0.1, 0.22, (0, 0, -0.18), M["green"], can, n=18)
    kit.box("can.handle", (0.025, 0.025, 0.2), (0, 0.09, -0.07), M["green"], can, bevel=0.006)
    kit.box("can.handle2", (0.025, 0.2, 0.025), (0, 0.0, 0.03), M["green"], can, bevel=0.006)
    rod(kit, "can.spout", (0, -0.08, -0.26), (0, -0.33, -0.05), 0.016, M["green"], can, n=8)
    rose = kit.cyl("can.rose", 0.04, 0.03, (0, -0.35, -0.03), M["green"], can, n=14, r2=0.04)
    rose.rotation_euler = (math.radians(-130), 0, 0)
    ctx["can"] = can
    ctx["can_tip"] = V((0, -0.35, -0.03))
    ctx["stream"] = kit.cyl("can.stream", 0.006, 1.0, (0, 0, -9), M["water"], n=6)
    # the torch
    torch = kit.empty("torch", (0, 0, -9))
    kit.cyl("torch.body", 0.032, 0.2, (0, 0, -0.08), M["iron"], torch, n=12)
    kit.cyl("torch.head", 0.048, 0.06, (0, 0, -0.19), M["iron2"], torch, n=12)
    kit.cyl("torch.lens", 0.04, 0.01, (0, 0, -0.225), M["glow"], torch, n=12)
    ctx["torch"] = torch
    sp = kit.light("torch beam", "SPOT", (0, 0, -9), 1.0, "#ffd9a0", spot=38, blend=0.6, size=0.03)
    ctx["torch_light"] = sp
    # the spade
    spade = kit.empty("spade", (0, 0, -9))
    kit.cyl("spade.shaft", 0.017, 0.95, (0, 0, 0.15), M["post"], spade, n=8)
    kit.box("spade.grip", (0.13, 0.03, 0.03), (0, 0, 0.64), M["post"], spade)
    kit.box("spade.blade", (0.2, 0.012, 0.26), (0, 0, -0.45), M["iron2"], spade, bevel=0.004)
    ctx["spade"] = spade
    # the bucket, upturned
    bk = kit.empty("bucket", (3.2, -25.3, 0))
    kit.cyl("bucket.body", 0.19, 0.3, (0, 0, 0.15), M["steel"], bk, n=20, r2=0.15)
    ctx["bucket"] = bk
    # the bike
    bike = kit.empty("bike", (0, 0, -9))
    for y in (-0.55, 0.55):
        torus(kit, f"bike.tyre{y}", 0.31, 0.025, (0, y, 0.34), M["tyre"], bike, rot=(0, math.radians(90), 0), n=28, m=6)
        kit.cyl(f"bike.hub{y}", 0.03, 0.04, (0, y, 0.34), M["iron2"], bike, rot=(0, math.radians(90), 0), n=8)
    rod(kit, "bike.top", (0, -0.5, 0.78), (0, 0.3, 0.75), 0.015, M["bikered"], bike)
    rod(kit, "bike.down", (0, -0.5, 0.78), (0, 0.05, 0.38), 0.015, M["bikered"], bike)
    rod(kit, "bike.seat", (0, 0.3, 0.75), (0, 0.05, 0.38), 0.015, M["bikered"], bike)
    rod(kit, "bike.fork", (0, -0.55, 0.34), (0, -0.5, 0.95), 0.012, M["bikered"], bike)
    rod(kit, "bike.rear", (0, 0.05, 0.38), (0, 0.55, 0.34), 0.012, M["bikered"], bike)
    kit.box("bike.bars", (0.5, 0.03, 0.03), (0, -0.5, 0.97), M["iron"], bike, bevel=0.008)
    kit.box("bike.saddle", (0.12, 0.26, 0.05), (0, 0.32, 0.8), M["tyre"], bike, bevel=0.015)
    ctx["bike"] = bike
    # drops: one per emitter (see EMITTERS); the sprinkle is a field of them
    ctx["drops"] = {}
    for name, *_ in EMITTERS:
        ctx["drops"][name] = kit.sphere(f"drop.{name}", 0.012, (0, 0, -9), M["water"], seg=8)
    rng = random.Random(14)
    ctx["sprinkle"] = []
    for k in range(18):
        d = kit.sphere(f"spr{k}", 0.011, (0, 0, -9), M["water"], seg=6)
        ctx["sprinkle"].append((d, rng.uniform(2.6, 5.0), rng.uniform(-0.8, 0.8), rng.uniform(-2.0, 2.0), rng.uniform(0, 1.2)))


# name, position, period (s), phase, active-when: padlock wet level / leaf always / can / digger plot
EMITTERS = [("leaf", (3.55, -27.62, 0.57), 1.55, 0.0, "always"),
            ("pad", (0.1, -0.05, 0.935), 0.62, 0.2, "pad3"),
            ("pad2", (0.12, -0.05, 0.935), 0.9, 0.55, "pad2"),
            ("rose", (0, 0, 0), 0.5, 0.0, "can")]


# ------------------------------------------------------------------------------------------------ interiors
def build_interior(kit, M, x0, ctx, plot_ten=False):
    """A small shed from inside: the camera looks +y at the back wall (y = 1.9). The tool wall on the left, a shelf
    on the right. In Mr. Carter's one hook is bare, with a clean can-shaped outline in the dust."""
    wood = M["creosote"]
    kit.box(f"in{x0}.floor", (2.8, 3.0, 0.05), (x0, 0.6, -0.025), M["post"])
    kit.box(f"in{x0}.back", (2.8, 0.06, 2.4), (x0, 1.9, 1.2), wood)
    kit.box(f"in{x0}.front", (2.8, 0.06, 2.4), (x0, -0.9, 1.2), wood)
    for s in (-1, 1):
        kit.box(f"in{x0}.side{s}", (0.06, 2.8, 2.4), (x0 + s * 1.4, 0.5, 1.2), wood)
    kit.box(f"in{x0}.ceil", (2.8, 2.9, 0.06), (x0, 0.5, 2.4), M["roof"])
    # the tool wall: spade, fork, hoe on hooks
    tools = [(-0.8, "spade"), (-0.45, "fork"), (-0.1, "hoe")] if not plot_ten else [(-0.7, "hoe"), (-0.3, "spade")]
    for dx, kind in tools:
        x = x0 + dx - 0.1
        kit.box(f"in{x0}.hook{dx}", (0.03, 0.06, 0.03), (x, 1.84, 1.72), M["iron"])
        kit.cyl(f"in{x0}.shaft{dx}", 0.017, 1.15, (x, 1.8, 1.15), M["post"], n=8)
        if kind == "spade":
            kit.box(f"in{x0}.blade{dx}", (0.2, 0.015, 0.28), (x, 1.8, 0.45), M["iron2"], bevel=0.004)
        elif kind == "fork":
            for t in (-0.07, 0, 0.07):
                kit.box(f"in{x0}.tine{dx}{t}", (0.02, 0.015, 0.26), (x + t, 1.8, 0.45), M["iron2"])
            kit.box(f"in{x0}.tbar{dx}", (0.17, 0.015, 0.03), (x, 1.8, 0.6), M["iron2"])
        else:
            kit.box(f"in{x0}.hoe{dx}", (0.22, 0.015, 0.05), (x, 1.78, 0.57), M["iron2"], rot=(0, 0.2, 0))
    bare = x0 + 0.28
    kit.box(f"in{x0}.hookbare", (0.045, 0.09, 0.045), (bare, 1.82, 1.55), M["iron2"], bevel=0.008)
    if not plot_ten:
        # dust on the boards, and the clean can-shaped patch where the can hung
        kit.box(f"in{x0}.dust", (0.95, 0.004, 0.85), (bare, 1.867, 1.28), pbr(kit, "wall dust", "#6b5a44", 0.95))
        kit.box(f"in{x0}.cleanbody", (0.28, 0.004, 0.24), (bare, 1.864, 1.3), M["creosote"])
        kit.box(f"in{x0}.cleanhandle", (0.04, 0.004, 0.24), (bare, 1.864, 1.45), M["creosote"])
        kit.box(f"in{x0}.cleanspout", (0.2, 0.004, 0.035), (bare - 0.2, 1.864, 1.35), M["creosote"], rot=(0, 0.6, 0))
    # the shelf with twine, an oil can and seed packets
    sx = x0 + 0.95
    kit.box(f"in{x0}.shelf", (0.9, 0.35, 0.04), (sx, 1.72, 1.0), M["post"], bevel=0.005)
    kit.box(f"in{x0}.shelf2", (0.9, 0.35, 0.04), (sx, 1.72, 1.5), M["post"], bevel=0.005)
    kit.sphere(f"in{x0}.twine", 0.08, (sx - 0.25, 1.7, 1.1), M["twine"], seg=12)
    kit.cyl(f"in{x0}.oil", 0.05, 0.16, (sx + 0.05, 1.7, 1.1), M["oil"], n=12)
    rod(kit, f"in{x0}.oilspout", (sx + 0.05, 1.7, 1.18), (sx + 0.17, 1.7, 1.26), 0.009, M["oil"])
    for k in range(4):
        kit.box(f"in{x0}.pack{k}", (0.1, 0.012, 0.14), (sx - 0.3 + 0.12 * k, 1.78, 1.58), M["paper"],
                rot=(0, 0.1 * (k - 1.5), 0), bevel=0.003)
        kit.box(f"in{x0}.pod{k}", (0.05, 0.004, 0.07), (sx - 0.3 + 0.12 * k, 1.769, 1.58), M["leaf2"],
                rot=(0, 0.1 * (k - 1.5), 0))
    kit.light(f"lamp{x0}", "POINT", (x0 + 0.1, 0.3, 2.0), 38.0, "#ffd9a8", size=0.12)
    kit.light(f"lamp{x0}b", "POINT", (x0 + 0.8, 1.2, 1.6), 14.0, "#ffd0a0", size=0.1)
    kit.light(f"lamp{x0}c", "POINT", (x0 + 0.3, 1.1, 1.5), 60.0 if plot_ten else 25.0, "#ffd9a8", size=0.1)


def build_shaft(kit, M, ctx):
    """Under the hole (x = 120): a 5 m shaft that opens onto the Bench, a flat pale floor 11 m below, with one
    unfinished hand lying palm up. The torch beam is the only light."""
    x0 = 120.0
    n_ = 28    # an open tube, no caps: the camera looks down it
    tv = [(HOLE_R * math.cos(2 * math.pi * i / n_), HOLE_R * math.sin(2 * math.pi * i / n_), z) for z in (0.0, -5.0) for i in range(n_)]
    tf = [(i, (i + 1) % n_, n_ + (i + 1) % n_, n_ + i) for i in range(n_)]
    kit.mesh_obj("shaft.wall", tv, tf, M["soil"], None, (x0, 0, 0), smooth=True)
    for k in range(6):
        torus(kit, f"shaft.root{k}", HOLE_R - 0.02, 0.03, (x0, 0, -0.5 - k * 0.8), M["root"], n=28, m=5)
    kit.plane("shaft.floor", (90, 90), (x0, 0, -11.0), M["floor"])
    h0 = V((x0 + 0.5, 0.25, -10.95))
    hand = kit.empty("hand", tuple(h0), rot=(0, 0, math.radians(18)))
    kit.box("hand.palm", (0.62, 0.62, 0.16), (0, 0, 0.08), M["hand"], hand, bevel=0.03)
    for k, (fx, fl) in enumerate(((-0.24, 0.62), (-0.08, 0.72), (0.08, 0.66), (0.24, 0.5))):
        kit.box(f"hand.f{k}", (0.12, fl, 0.11), (fx, 0.31 + fl / 2, 0.06), M["hand"], hand, rot=(0, 0, 0.04 * (k - 1.5)),
                bevel=0.025)
    kit.box("hand.thumb", (0.14, 0.42, 0.11), (-0.4, 0.05, 0.06), M["hand"], hand, rot=(0, 0, 0.7), bevel=0.025)
    kit.box("hand.cut", (0.62, 0.1, 0.16), (0, -0.34, 0.08), pbr(kit, "hand cut", "#6e665c", 0.9), hand, bevel=0.01)
    sp = kit.light("shaft beam", "SPOT", (x0, 0, 0.5), 1.0, "#ffd9a0", spot=40, blend=0.7, size=0.08, rot=(0, 0, 0))
    ctx["shaft_light"] = sp
    kit.aim(sp, (x0 + 0.2, 0.1, -11.0))


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    M = materials(kit)
    ctx = {"M": M}
    # the sky: a vertical gradient (horizon to zenith) whose colours animate with the time of day
    w = bpy.context.scene.world
    nt = w.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.55
    mr.clamp = True
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], nt.nodes["Background"].inputs["Color"])
    ctx["sky"] = (ramp, nt.nodes["Background"])
    build_scenery(kit, M)
    build_fence(kit, M)
    build_gate(kit, M, ctx)
    build_plots(kit, M, ctx)
    build_digger(kit, M, ctx)
    build_holes(kit, M, ctx)
    build_props(kit, M, ctx)
    build_interior(kit, M, 60.0, ctx)
    build_interior(kit, M, 80.0, ctx, plot_ten=True)
    build_shaft(kit, M, ctx)
    # the sun, and a character-only fill from the other side (the Digger never gets it: front lights dead)
    sun = kit.light("sun", "SUN", tuple(SUN_DIR * 40), 1.0, "#ffb184", size=0.02)
    kit.aim(sun, (0, 0, 0))
    ctx["sun"] = sun
    fill = kit.light("char fill", "SUN", tuple(FILL_DIR * 40), 1.0, "#a5b8e6", size=0.02)
    kit.aim(fill, (0, 0, 0))
    ctx["fill"] = fill
    kit.light("night glow", "POINT", (0.1, 0.4, 1.4), 1.0, "#9fb4ff", size=0.2)
    ctx["inited"] = False
    return ctx


# ------------------------------------------------------------------------------------------------ animate
def light_only(kit, coll, light_name, objs):
    col = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = "INCLUDE"
    kit.LIGHTS[light_name]["obj"].light_linking.receiver_collection = col


def no_light(kit, coll, light_name, objs):
    col = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = "EXCLUDE"
    kit.LIGHTS[light_name]["obj"].light_linking.receiver_collection = col


def decorate(kit, story, ctx):
    """After the cast exists: wellies, wet trousers, a moustache, the fog nodes to animate, the fill's link."""
    M = ctx["M"]
    for who, mat, lo in (("me", M["wellig"], 1.0), ("carter", M["wellid"], 0.62), ("newcomer", None, 0)):
        if mat is None:
            continue
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg is None:
                continue
            if who == "carter":
                kit.box(f"{who}.wet{sx}", (1.02, 1.04, 1.1), (0, 0, -1.15), M["wetpants"], leg, bevel=0.06)
            kit.box(f"{who}.welly{sx}", (1.04, 1.06, 0.9 * lo), (0, 0, -1.4 + (1 - lo) * 0.45), mat, leg, bevel=0.08)
    hg = bpy.data.objects.get("carter.headg")
    if hg is not None:
        kit.box("carter.capc", (2 * faces.HEAD_R + 0.16, 2 * faces.HEAD_R + 0.2, 0.17), (0, 0.02, 0.58), M["capwool"], hg, bevel=0.06)
        kit.box("carter.mous", (0.4, 0.09, 0.09), (0, -faces.HEAD_R - 0.01, -0.15), M["mous"], hg, bevel=0.03)
        for sx in (-1, 1):
            kit.box(f"carter.mousend{sx}", (0.1, 0.08, 0.15), (sx * 0.2, -faces.HEAD_R + 0.0, -0.2), M["mous"], hg, bevel=0.03)
    hg2 = bpy.data.objects.get("newcomer.headg")
    if hg2 is not None:
        kit.box("newcomer.tail", (0.42, 0.4, 1.0), (0, faces.HEAD_R + 0.2, -0.05), M["pony"], hg2, bevel=0.1)
        kit.box("newcomer.tailtie", (0.46, 0.44, 0.1), (0, faces.HEAD_R + 0.17, 0.38), M["capwool"], hg2, bevel=0.03)
    tor2 = bpy.data.objects.get("newcomer.torso")
    if tor2 is not None:
        kit.box("newcomer.zip", (0.14, 0.04, 1.9), (0, -0.52, 1.0), M["zipstripe"], tor2, bevel=0.01)
    chars = []
    for who in ("me", "carter", "newcomer"):
        r = bpy.data.objects.get(who)
        if r is not None:
            chars += [o for o in r.children_recursive if o.type == "MESH"]
    if chars:
        light_only(kit, "chars", "char fill", chars)
        light_only(kit, "chars2", "night glow", chars)
    # fog nodes (density multiply and fog emission), found once
    d0 = story["look"]["fog_density"]
    fc = _lin(_hex(FOGC))
    dens, ems = [], []
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        for n in m.node_tree.nodes:
            if n.type == "MATH" and n.operation == "MULTIPLY" and abs(n.inputs[1].default_value + d0) < 1e-6:
                dens.append(n)
            elif n.type == "EMISSION":
                c = n.inputs["Color"].default_value
                if all(abs(c[i] - fc[i]) < 0.02 for i in range(3)) and abs(n.inputs["Strength"].default_value - 1.0) < 1e-6:
                    ems.append(n)
    ctx["fog_dens"], ctx["fog_ems"] = dens, ems
    ctx["inited"] = True


def tod_state(tl, t):
    cs = [c for c in _cues(tl, "tod") if c["t"] <= t + 1e-9]
    cur = cs[-1]["set"] if cs else "dawn"
    prev = cs[-2]["set"] if len(cs) > 1 else cur
    u = 1.0
    if cs and float(cs[-1].get("dur", 0)) > 0:
        u = _ss((t - cs[-1]["t"]) / float(cs[-1]["dur"]))
    a, b = TOD[prev], TOD[cur]
    out = {}
    for k in a:
        if isinstance(a[k], str):
            out[k] = _mixc(_hex(a[k]), _hex(b[k]), u)
        else:
            out[k] = a[k] + (b[k] - a[k]) * u
    return out


def _frame(who, part, local):
    """World point on a character's part (rig units), with the character's yaw only (a prop that stays upright)."""
    root = bpy.data.objects.get(who)
    ob = bpy.data.objects.get(f"{who}.{part}")
    if root is None or ob is None or root.hide_render:
        return None
    p = ob.matrix_world @ V(local)
    q = root.matrix_world.to_quaternion()
    yaw = q.to_euler("XYZ").z
    return p, yaw


def _place(ob, p, yaw, rot=(0, 0, 0)):
    ob.location = p
    ob.rotation_euler = (math.radians(rot[0]), math.radians(rot[1]), yaw + math.radians(rot[2]))


def animate(kit, story, tl, t, ctx):
    bpy.context.view_layer.update()
    if not ctx["inited"]:
        decorate(kit, story, ctx)
    M = ctx["M"]
    # ---------------------------------------------------------------- light
    s = tod_state(tl, t)
    ctx["sun"].data.color = _lin(s["sunc"])
    ctx["fill"].data.color = _lin(s["fillc"])
    ramp, bg = ctx["sky"]
    hor, zen = _lin(s["hor"]), _lin(s["zen"])
    ramp.color_ramp.elements[0].color = (*hor, 1)
    ramp.color_ramp.elements[1].color = (*zen, 1)
    bg.inputs["Strength"].default_value = s["sky"] * 0.55
    for n in ctx["fog_dens"]:
        n.inputs[1].default_value = -s["fogd"]
    for n in ctx["fog_ems"]:
        n.inputs["Strength"].default_value = s["fogb"] * (0.75 + 0.25 * s["sky"] / 1.5)
    night = _last(_cues(tl, "tod"), t)
    is_night = bool(night and night["set"] == "night")
    over = {"sun": s["sun"], "char fill": s["fill"], "night glow": 6.0 if is_night else 0.0}
    # ---------------------------------------------------------------- the Digger
    dg = ctx["digger"]
    c = _last(_cues(tl, "digger"), t) or {"hidden": True}
    hidden = bool(c.get("hidden"))
    _show([dg["root"]], not hidden)
    over["digger eyes"] = 0.0 if hidden else 0.35
    if not hidden:
        px, py = DIG[c["plot"]]
        dg["root"].location = (px, py, 0)
        dg["root"].rotation_euler = (0, 0, math.radians(c.get("yaw", 0)))
        dg["body"].location = (0, 0, c["up"])
        dg["neck"].rotation_euler = (0, 0, math.radians(c.get("head", 0)))
        ctx["neckroots"].rotation_euler = (0, 0, math.radians(c.get("head", 0)) * 0.5)
        # the loosened ring stays at the ground whatever the height
        ctx["site"].location = (0, 0, -c["up"])
    hc = _last(_cues(tl, "holes"), t) or {"plots": []}
    for n, g in ctx["holes"].items():
        _show([g], n in hc["plots"])
    _show([ctx["mound"]], bool((_last(_cues(tl, "mound"), t) or {}).get("on")))
    # ---------------------------------------------------------------- the gate, the shed door
    go = float(_eased(_cues(tl, "gate"), "open", t, 0.0))
    ctx["leaves"][-1].rotation_euler = (0, 0, math.radians(95) * go)
    ctx["leaves"][1].rotation_euler = (0, 0, -math.radians(95) * go)
    so = float(_eased(_cues(tl, "shed"), "open", t, 0.0))
    ctx["door"].rotation_euler = (0, 0, -math.radians(82) * so)
    # ---------------------------------------------------------------- the padlock
    wet = (_last(_cues(tl, "padlock"), t) or {"wet": 0}).get("wet", 0)
    _show(ctx["beads"], wet >= 1)
    _show(ctx["streams"], wet == 2)
    # ---------------------------------------------------------------- props held
    kc = _last(_cues(tl, "key"), t) or {"where": "off"}
    k = ctx["key"]
    if kc["where"] == "carter":
        f = _frame("carter", "arm1", (0, 0, -1.9))
        if f:
            _place(k, f[0] + V((0, 0, -0.1)), f[1])
        else:
            k.location = (0, 0, -9)
    elif kc["where"] == "padlock":
        k.location = (0.12, -0.075, 0.99)
        k.rotation_euler = (0, 0, 0)
    else:
        k.location = (0, 0, -9)
    cc = _last(_cues(tl, "can"), t) or {"where": "off"}
    can, stream = ctx["can"], ctx["stream"]
    can_world = None
    stream.location = (0, 0, -9)
    if cc["where"] in ("carter", "me"):
        f = _frame(cc["where"], cc.get("arm", "arm1"), (0, 0, -1.9))
        if f:
            _place(can, f[0], f[1], (0, 0, 0 if cc["where"] == "carter" else 0))
            if cc.get("water") or cc["where"] == "me" and cc.get("water"):
                can.rotation_euler = (math.radians(-38), 0, f[1])
            can_world = can
    elif cc["where"] == "world":
        _place(can, V(cc["pos"]), 0, cc.get("rot", (0, 0, 0)))
        can.rotation_euler = (math.radians(cc["rot"][0]), math.radians(cc["rot"][1]), math.radians(cc["rot"][2]))
        can_world = can
    else:
        can.location = (0, 0, -9)
    if can_world is not None and cc.get("water"):
        bpy.context.view_layer.update()
        tip = can.matrix_world @ ctx["can_tip"]
        stream.location = (tip.x, tip.y, max(0.03, tip.z / 2))
        stream.scale = (1, 1, max(0.05, tip.z - 0.0))
    tg = float(_eased(_cues(tl, "torch"), "on", t, 0.0))
    tor = ctx["torch"]
    f = _frame("me", "arm1", (0, 0, -1.9)) if tg > 0.001 else None
    if f:
        _place(tor, f[0] + V((0, 0, 0.05)), f[1])
        ctx["torch_light"].location = tor.location + V((0, 0, -0.2))
        kit.aim(ctx["torch_light"], (tor.location.x, tor.location.y, 0.0))
        over["torch beam"] = 650.0 * tg
        ctx["shaft_light"]
    else:
        tor.location = (0, 0, -9)
        over["torch beam"] = 0.0
    over["shaft beam"] = 260.0 * tg
    sp = _last(_cues(tl, "spade"), t) or {"on": False}
    f = _frame("me", "arm1", (0, 0, -1.9)) if sp.get("on") else None
    if f:
        _place(ctx["spade"], f[0] + V((0, 0, 0.1)), f[1], (-12, 0, 0))
    else:
        ctx["spade"].location = (0, 0, -9)
    _show([ctx["bucket"]], bool((_last(_cues(tl, "bucket"), t) or {}).get("on")))
    # the bike: beside the newcomer while she wheels it, parked by a cue
    bc = _last(_cues(tl, "bike"), t) or {"on": False}
    bike = ctx["bike"]
    if bc.get("on"):
        if "pos" in bc:
            bike.location = (bc["pos"][0], bc["pos"][1], 0)
            bike.rotation_euler = (0, 0, math.radians(bc.get("yaw", 0)))
        else:
            nc = bpy.data.objects.get("newcomer")
            if nc is not None and not nc.hide_render:
                p = nc.matrix_world @ V((-1.55, -0.2, 0))
                bike.location = (p.x, p.y, 0)
                bike.rotation_euler = (0, 0, nc.matrix_world.to_euler().z)
            else:
                bike.location = (0, 0, -9)
    else:
        bike.location = (0, 0, -9)
    # ---------------------------------------------------------------- the pebble and the feeding cane
    pc = _last(_cues(tl, "pebble"), t)
    pb = ctx["pebble"]
    if pc:
        u = t - pc["t"]
        z = 1.35 - 4.9 * u * u
        pb.location = (3.2 + (3.4 - 3.2) * min(1, u / 0.5), -3.85 + (-3.6 + 3.85) * min(1, u / 0.5), z) if z > -0.2 else (0, 0, -9)
    else:
        pb.location = (0, 0, -9)
    cn = _last(_cues(tl, "cane"), t)
    cane = ctx["cane"]
    if cn and cn.get("on"):
        sink_t = None
        for c2 in _cues(tl, "cane"):
            pass
        t_sink = tl["lines"]["L26"]["onset"] if "L26" in tl["lines"] else cn["t"] + 2.0
        u = _ss((t - t_sink) / 1.6)
        top = 0.9 * (1 - u) - 0.05 * u
        # the cane leans into plot four's hole; its top end sinks below the ground
        base = V((DIG[4][0] + 0.15, DIG[4][1] + 0.1, 0))
        cane.location = (base.x + 0.1, base.y + 0.1, top - 1.3)
        cane.rotation_euler = (math.radians(-6), math.radians(8), 0)
        cane.scale = (1, 1, 1)
    else:
        cane.location = (0, 0, -9)
    # ---------------------------------------------------------------- the other plots go green
    _show(ctx["greens"], bool((_last(_cues(tl, "greens"), t) or {}).get("on")))
    # ---------------------------------------------------------------- drops
    ems = ctx["drops"]
    for name, pos, period, ph, when in EMITTERS:
        d = ems[name]
        on = False
        p0 = V(pos)
        if when == "always":
            on = True
        elif when == "pad3":
            on = wet >= 3
        elif when == "pad2":
            on = wet >= 3
        elif when == "can":
            on = can_world is not None and bool(cc.get("water") is None and cc["where"] in ("carter", "world"))
            if on:
                bpy.context.view_layer.update()
                p0 = can.matrix_world @ ctx["can_tip"]
        if not on:
            d.location = (0, 0, -9)
            continue
        ph_t = ((t + ph * period) % period) / period
        ground = 0.02 if name != "pad" and name != "pad2" else 0.02
        if ph_t < 0.72:
            r = 0.35 + 0.65 * ph_t / 0.72
            d.scale = (r, r, r * 1.15)
            d.location = (p0.x, p0.y, p0.z)
        else:
            fall = (ph_t - 0.72) / 0.28 * 0.34
            z = p0.z - 4.9 * fall * fall
            d.scale = (1, 1, 1.4)
            d.location = (p0.x, p0.y, z) if z > ground else (0, 0, -9)
    sc = bool((_last(_cues(tl, "sprinkle"), t) or {}).get("on"))
    for d, per, dx, dy, ph in ctx["sprinkle"]:
        if not sc:
            d.location = (0, 0, -9)
            continue
        u = ((t * 0.9 + ph) % 1.0)
        z = 1.7 - u * u * 1.65
        d.location = (3.75 + dx + 0.2 * math.sin(ph * 9 + 1), -28.3 + dy * 0.55 + ph * 0.3, z) if z > 0.03 else (0, 0, -9)
        d.scale = (1, 1, 1.5)
    # the Digger's wet shoulder: a drop on Monday
    return over
