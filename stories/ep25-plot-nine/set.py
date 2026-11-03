"""Plot nine (ep25, redo round 2): allotment gardens on a hillside at dawn, and the roots that grow where you belong.
Built from kit.py's parts; nothing here is shared with another story's set. There is no text anywhere in the set.

Coordinates (metres): the gate is at y = 0, the path runs down the hill along -y (x -0.75 .. 0.75), odd plots on the
left (x > 0), even on the right (x < 0), five rows of 5 m: row r spans y = -1.5 - 6r .. -6.5 - 6r. Plot nine is
x 1..6, y -25.5 .. -30.5, Mum's shed at its path corner (x 1.0 .. 2.4, y -27.6 .. -25.8), the door on its +x
face. Plot ten (mine) is across the path: x -6..-1, same rows. The ground is flat; the hill falls away past the
bottom fence (y = -32). Mum's shed interior sits off to the side at x = 60.

ROOTS. Everyone who belongs here has dark, tapering roots fanned over the ground from their boots (tube(), root_fan()):
Mr Pell's bed and his run to the gate, Mum's run up the path (pieces, so a cue can shorten it to the plot the Digger is
in), her fan at her boots, the umbrellas' fans, the Digger's run to her boots. Never pale, never jointed.

THE DIGGER (the creature). One model, built once, posed by the "digger" cues: which plot, how far its shoulders stand
above the soil ("up"), the body's yaw (always 180, facing the gate) and the head's own turn. It's a blocky person built
from our blocks but too long: narrow shoulders, a long neck, and a torso and both arms that are 4 m boxes going on down
into the ground, wound with dark root cable. No mouth, no nose; two small seed-green points set in two dark pits.
It is never seen moving: every change of place or height is across a cut.

Cues read here: tod (time of day / light, with an optional ramp), digger, holes, dent, pebble, bucket, flask, bike, pot,
gate, mumrun, mumfan, digrun.
"""

from __future__ import annotations

import math
import random

import bpy
from mathutils import Matrix
from mathutils import Vector as V

from blocky import faces, rig

RIG_S = 0.34
DIG_S = 1.25
HOLE_R = 0.68
DIG = {1: (3.4, -3.6), 4: (-3.6, -10.0), 7: (3.4, -22.0), 9: (4.3, -26.0)}
PELL = (3.4, -9.8)
PELL_AZ = math.degrees(math.atan2(1.6 - PELL[0], -(-8.0 - PELL[1])))    # the way old Mr Pell faces
POT = (0.0, -1.9)
MUMP = (3.8, -27.7)
FOGC = "#b3aaa9"
WORLD_UP = V((0, 0, 1))

# time of day: key sun, character-only fill, sky strength, horizon and zenith, fog density and brightness
TOD = {
    "bright":  dict(sun=8.5, sunc="#ffd2a0", fill=1.5, fillc="#b4c6ea", sky=1.5, hor="#f0cdb0", zen="#8fb0da", fogd=0.010, fogb=1.0),
    "dawn":    dict(sun=7.5, sunc="#ffb184", fill=1.5, fillc="#a5b8e6", sky=1.1, hor="#e8bba4", zen="#87a2c9", fogd=0.016, fogb=0.95),
    "tue":     dict(sun=6.5, sunc="#ffbf98", fill=1.6, fillc="#a8bae6", sky=1.1, hor="#dcc0b0", zen="#8aa2c4", fogd=0.020, fogb=0.95),
    "wed":     dict(sun=5.5, sunc="#f4c8a8", fill=1.7, fillc="#a8bce6", sky=1.2, hor="#cfc0b8", zen="#8ea4c2", fogd=0.026, fogb=0.95),
    "fog":     dict(sun=2.6, sunc="#ffe2c0", fill=2.2, fillc="#c4cfe6", sky=1.5, hor="#a9a8ad", zen="#98a2b4", fogd=0.075, fogb=0.8),
    "fogthin": dict(sun=5.5, sunc="#ffd9a8", fill=1.8, fillc="#c4cfe6", sky=1.5, hor="#d8c9bd", zen="#9fb2cf", fogd=0.04, fogb=1.0),
    "dusk":    dict(sun=7.0, sunc="#ff9a5e", fill=1.3, fillc="#9fb0dc", sky=1.0, hor="#e8a682", zen="#7f93c0", fogd=0.016, fogb=0.9),
    "grey":    dict(sun=4.0, sunc="#d8d8e6", fill=2.0, fillc="#b4c0e0", sky=1.3, hor="#b4b8c4", zen="#8a98b8", fogd=0.030, fogb=0.9),
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
    M["inwood"] = kit.planks("#5d5144", "#40372e", 1.2, "Z", name="shed inside boards", rough=0.8)
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
    M["root"] = pbr(kit, "root", "#33251a", 0.8, spec=0.22, noise=(16.0, 0.7, 0.1), bump=0.6)
    M["terra"] = pbr(kit, "terracotta", "#b5643c", 0.7, noise=(6.0, 0.8, 0.0), bump=0.2)
    M["bsoil"] = pbr(kit, "bucket soil", "#2c2018", 0.9, noise=(14.0, 0.6, 0.0), bump=0.6)
    M["umbnavy"] = pbr(kit, "umbrella navy", "#27324a", 0.6)
    M["umbred"] = pbr(kit, "umbrella maroon", "#6a2430", 0.6)
    M["umbgreen"] = pbr(kit, "umbrella green", "#2f5a3e", 0.6)
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
    M["pony"] = pbr(kit, "pony", "#6b4226", 0.7)
    M["zipstripe"] = pbr(kit, "zip stripe", "#efe4c4", 0.6)
    M["mous"] = pbr(kit, "moustache", "#9a9a98", 0.9)
    M["greenbed"] = pbr(kit, "green crop bed", "#44693a", 0.9, noise=(8.0, 0.55, 0.0))
    M["glow"] = kit.emit("#ffcf8a", 3.0, name="torch lens")
    M["lampglow"] = kit.emit("#ffd9a0", 4.0, name="lamp")
    M["lettuce"] = pbr(kit, "lettuce", "#8bb750", 0.6, spec=0.3, noise=(7.0, 0.72, 0.0))
    M["lettuce2"] = pbr(kit, "lettuce b", "#6f9f42", 0.6, spec=0.3, noise=(7.0, 0.72, 0.0))
    M["raked"] = pbr(kit, "raked soil", "#5b4332", 0.88, noise=(4.0, 0.75, 0.0), bump=0.4)
    M["ridge"] = pbr(kit, "rake ridge", "#6e5440", 0.9)
    M["sage"] = pbr(kit, "sage scarf", "#7fa36a", 0.9, noise=(30.0, 0.85, 0.0))
    M["brass"] = pbr(kit, "brass", "#b8963c", 0.35, metal=0.8, spec=0.5)
    M["mugred"] = pbr(kit, "enamel mug", "#b84a3a", 0.35, spec=0.6)
    M["glove"] = pbr(kit, "work glove", "#c47a34", 0.85, noise=(20.0, 0.8, 0.0))
    M["umb"] = pbr(kit, "umbrella handle", "#4a2f1c", 0.45, spec=0.5)
    M["frame"] = pbr(kit, "glasses frame", "#2a2622", 0.4, metal=0.3)
    M["stalk"] = pbr(kit, "green stalk", "#5f9440", 0.55, spec=0.35, noise=(9.0, 0.7, 0.0))
    M["flaskcap"] = pbr(kit, "flask cap", "#2c3a44", 0.5, metal=0.3)
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
    # the chain across the meeting stiles and the iron padlock hanging on it (seen, never mentioned)
    for k in range(7):
        x = -0.06 + 0.04 * k
        z = 1.08 - 0.05 * math.sin(math.pi * (k + 0.5) / 7)
        torus(kit, f"chain{k}", 0.014, 0.0045, (x, -0.035, z), M["iron2"], rot=(math.radians(90 if k % 2 else 0), 0, 0), n=14,
              m=5)
    pl = kit.empty("padlock", (0.1, -0.035, 0.98))
    kit.box("padlock.body", (0.075, 0.034, 0.06), (0, 0, 0), M["iron"], pl, bevel=0.008)
    torus(kit, "padlock.shackle", 0.022, 0.0065, (0, 0, 0.03), M["iron2"], pl, rot=(math.radians(90), 0, 0), n=18, m=5,
          scale=(1, 1, 1.15))
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


def lettuce_bed(kit, M, n):
    x0, x1, y0, y1 = plot_rect(n)
    rng = random.Random(40 + n)
    for i in range(10):
        for j in range(9):
            x = x0 + 0.5 + i * 0.44 + rng.uniform(-0.05, 0.05)
            y = y0 + 0.5 + j * 0.5 + rng.uniform(-0.05, 0.05)
            m = M["lettuce" if (i + j) % 2 else "lettuce2"]
            kit.box(f"let{n}_{i}_{j}", (0.27, 0.27, 0.15), (x, y, 0.08), m, rot=(0, 0, rng.uniform(0, 3)), bevel=0.07)
            kit.box(f"let{n}_{i}_{j}b", (0.17, 0.17, 0.12), (x, y, 0.17), m, rot=(0, 0, rng.uniform(0, 3)), bevel=0.05)


def raked_bed(kit, M, n):
    x0, x1, y0, y1 = plot_rect(n)
    cx = (x0 + x1) / 2
    for k in range(24):
        x = x0 + 0.35 + k * 0.2
        kit.box(f"ridge{n}_{k}", (0.07, 4.5, 0.03), (x, (y0 + y1) / 2, 0.015), M["ridge"], bevel=0.012)


def build_plots(kit, M, ctx):
    rng = random.Random(21)
    for n in range(1, 11):
        x0, x1, y0, y1 = plot_rect(n)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if n == 9:
            kit.plane("plot9", (5, 5), (cx, cy, 0.001), M["wet"])
        elif n == 10:
            kit.plane("plot10", (5, 5), (cx, cy, 0.001), M["raked"])
            raked_bed(kit, M, n)
        else:
            kit.plane(f"plot{n}", (5, 5), (cx, cy, 0.001), M["clay" if n % 2 else "clay2"])
            for k in range(9):    # wilted leaves in rows
                if n == 6:
                    break
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
    lettuce_bed(kit, M, 6)
    # plot nine: raised wet rows with bean wigwams, two rows 1.8 m apart
    x0, x1, y0, y1 = plot_rect(9)
    for rx in (2.9, 4.7):
        kit.box(f"row{rx}", (0.9, 4.6, 0.12), (rx, (y0 + y1) / 2, 0.06), M["wet"], bevel=0.05)
        for k in range(4):
            wy = y1 - 0.9 - k * 1.2
            if (rx, k) not in ((2.9, 0), (2.9, 3)):
                continue
            wig = kit.empty(f"wig{rx}_{k}", (rx, wy, 0))
            for j, (ax, ay) in enumerate(((0.32, 0.32), (-0.32, 0.32), (0.32, -0.32), (-0.32, -0.32))):
                rod(kit, f"cane{rx}_{k}_{j}", (ax, ay, 0.0), (0, 0, 2.05), 0.011, M["cane"], wig, n=5)
            for j in range(15):
                z = rng.uniform(0.3, 1.8)
                u = 1 - z / 2.05
                lx, ly = rng.choice((-1, 1)) * 0.32 * u, rng.choice((-1, 1)) * 0.32 * u
                kit.box(f"lf{rx}_{k}_{j}", (0.14, 0.09, 0.015), (lx, ly, z), M["leaf" if j % 2 else "leaf2"], wig,
                        rot=(rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8), rng.uniform(0, 3)), bevel=0.005)
    # Mum's shed at the path corner, a door in its +x face
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


def catmull(pts, k=4):
    """Points along a smooth curve through pts (Catmull-Rom), k steps per span."""
    P = [V(p) for p in pts]
    ext = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for j in range(k):
            t = j / k
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-1])
    return out


def tube(kit, name, pts, r0, r1, mat, parent=None, m=6, k=4):
    """One smooth root: a tapering tube along pts, thick at the first point and fine at the last. No joints."""
    path = catmull(pts, k) if len(pts) > 2 else [V(p) for p in pts]
    n = len(path)
    verts = []
    for i, p in enumerate(path):
        t = (path[min(i + 1, n - 1)] - path[max(i - 1, 0)]).normalized()
        a = t.cross(WORLD_UP)
        if a.length < 1e-4:
            a = t.cross(V((1, 0, 0)))
        a.normalize()
        b = t.cross(a)
        r = r0 + (r1 - r0) * ((i / (n - 1)) ** 0.8)
        for j in range(m):
            th = 2 * math.pi * j / m
            verts.append(tuple(p + r * (math.cos(th) * a + math.sin(th) * b)))
    fcs = [(i * m + j, i * m + (j + 1) % m, (i + 1) * m + (j + 1) % m, (i + 1) * m + j) for i in range(n - 1) for j in range(m)]
    fcs.append(tuple(reversed(range(m))))
    fcs.append(tuple((n - 1) * m + j for j in range(m)))
    return kit.mesh_obj(name, verts, fcs, mat, parent, smooth=True)


def ribbon(kit, name, pts, w, z, mat):
    """A flat strip along pts (the groove a root leaves in the dust)."""
    path = catmull(pts, 3) if len(pts) > 2 else [V(p) for p in pts]
    verts = []
    for i, p in enumerate(path):
        t = (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)])
        t.z = 0
        t.normalize()
        s = V((-t.y, t.x, 0)) * (w / 2)
        verts += [(p.x - s.x, p.y - s.y, z), (p.x + s.x, p.y + s.y, z)]
    fcs = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(path) - 1)]
    return kit.mesh_obj(name, verts, fcs, mat, None, smooth=False)


def root_fan(kit, M, name, n, L, spread, seed, r0=0.04, parent=None, loc=(0, 0, 0), yaw=0.0, boots=0.12):
    """Dark tapering roots fanned over the ground from a pair of boots (or an object's base). The fan opens
    towards `yaw` (the way a character facing yaw looks); L is the longest root, scaled per pose by the cue."""
    g = kit.empty(name, loc, parent, rot=(0, 0, math.radians(yaw + 180)))
    rng = random.Random(seed)
    for i in range(n):
        a = math.radians(-spread + 2 * spread * (i + rng.uniform(-0.3, 0.3)) / max(1, n - 1))
        ln = L * rng.uniform(0.55, 1.0) * (1.0 - 0.3 * abs(math.sin(a)))
        side = rng.choice((-1, 1)) * boots
        dx, dy = math.sin(a), math.cos(a)
        ph = rng.uniform(0, 6)
        pts = []
        for s in (0.0, 0.12, 0.3, 0.55, 0.8, 1.0):
            wob = 0.12 * ln * math.sin(s * 4.0 + ph) * s
            x = side * (1 - min(1.0, s * 3)) + dx * ln * s - dy * wob
            y = dy * ln * s + dx * wob
            pts.append((x, y, 0.035 + 0.12 * max(0.0, 1 - s * 4)))
        tube(kit, f"{name}.r{i}", pts, r0 * rng.uniform(0.8, 1.15), 0.008, M["root"], g, m=6, k=3)
    return g


def build_digger(kit, M, ctx):
    root = kit.empty("digger", (0, 0, -50))
    root.scale = (DIG_S, DIG_S, DIG_S)    # taller than the cast
    body = kit.empty("digger.body", (0, 0, 0), root)
    kit.box("digger.torso", (0.58, 0.34, 4.2), (0, 0, -2.1), M["soil"], body, bevel=0.035)
    for sx in (-1, 1):
        kit.box(f"digger.arm{sx}", (0.3, 0.34, 4.2), (sx * 0.44, 0, -2.1), M["soil"], body, bevel=0.03)
    # the long neck: a column of packed soil, one block taller than before, under the head
    kit.box("digger.neckcol", (0.26, 0.24, 0.5), (0, 0, 0.18), M["soil"], body, bevel=0.04)
    for sx in (-1, 1):    # the shoulders slope up to the neck
        kit.box(f"digger.slope{sx}", (0.42, 0.34, 0.16), (sx * 0.3, 0, 0.0), M["soil"], body, rot=(0, sx * 0.42, 0), bevel=0.04)
    # roots: dark cable, thick at the shoulders and tapering to a fine point, wound down the chest and arms and on
    # into the soil at the waist. Never pale, never jointed.
    rng = random.Random(33)
    strands = [((-0.26, -0.18, -0.02), (-0.1, -0.19, -0.3), (0.12, -0.19, -0.6), (0.26, -0.18, -1.0), (0.1, -0.18, -1.7), (-0.1, -0.18, -2.5)),
               ((0.28, -0.18, -0.02), (0.16, -0.19, -0.3), (0.0, -0.19, -0.7), (-0.2, -0.18, -1.2), (-0.1, -0.18, -2.0), (0.1, -0.18, -2.6)),
               ((-0.58, -0.14, -0.04), (-0.46, -0.19, -0.3), (-0.58, -0.19, -0.8), (-0.42, -0.19, -1.4), (-0.5, -0.19, -2.4)),
               ((0.58, -0.14, -0.04), (0.5, -0.19, -0.35), (0.6, -0.19, -0.9), (0.44, -0.19, -1.5), (0.5, -0.19, -2.5)),
               ((-0.26, 0.18, -0.02), (-0.1, 0.19, -0.3), (0.14, 0.19, -0.55), (0.26, 0.19, -1.0), (0.1, 0.19, -1.9), (0.0, 0.19, -2.6)),
               ((0.26, 0.18, -0.02), (0.1, 0.19, -0.35), (-0.14, 0.19, -0.65), (-0.26, 0.19, -1.1), (-0.1, 0.19, -2.0)),
               ((-0.56, 0.14, -0.04), (-0.46, 0.19, -0.4), (-0.58, 0.19, -0.9), (-0.44, 0.19, -1.8)),
               ((0.1, -0.18, -0.02), (0.22, -0.19, -0.2), (0.4, -0.19, -0.5), (0.5, -0.19, -1.3), (0.44, -0.19, -2.3))]
    for k, st in enumerate(strands):
        tube(kit, f"digger.root{k}", st, 0.042, 0.01, M["root"], body, m=6, k=3)
    for sx in (-1, 1):     # a cable round each shoulder
        tube(kit, f"digger.shcable{sx}", [(sx * 0.58, -0.19, -0.12), (sx * 0.44, -0.2, -0.16), (sx * 0.3, -0.19, -0.1),
                                          (sx * 0.38, 0.0, -0.1), (sx * 0.5, 0.19, -0.14), (sx * 0.58, 0.14, -0.2)],
             0.04, 0.016, M["root"], body, m=6, k=3)
    for k in range(40):    # clods
        x = rng.uniform(-0.62, 0.62)
        z = rng.uniform(-0.9, 0.03)
        yy = rng.choice((-1, 1)) * 0.175
        sz = rng.uniform(0.04, 0.12)
        kit.box(f"digger.clod{k}", (sz, sz * 0.7, sz * 0.8), (x, yy, z), M["soil2"], body,
                rot=(rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0, 3)), bevel=0.014)
    neck = kit.empty("digger.neck", (0, 0, 0.4), body)
    hs = kit.empty("digger.hs", (0, 0, 0.0), neck)
    hs.scale = (RIG_S * 0.86, RIG_S * 0.9, RIG_S * 1.3)    # a long oval head on the long neck
    hs.rotation_euler = (math.radians(13), 0, 0)    # stooping towards whoever looks
    headg = kit.empty("digger.headg", (0, 0, faces.HEAD_H / 2 + 0.02), hs)
    rig.head_mesh("digger.headm", M["soil"], headg)
    R = faces.HEAD_R
    for k in range(14):    # clods on the head, clear of the face
        a = rng.uniform(0, 2 * math.pi)
        if abs(a - math.pi * 1.5) < 0.9:
            a += 1.8
        sz = rng.uniform(0.07, 0.17)
        kit.box(f"digger.hclod{k}", (sz, sz * 0.8, sz * 0.7), (R * 0.97 * math.cos(a), R * 0.97 * math.sin(a),
                                                             rng.uniform(-0.2, 0.55)), M["soil2"], headg,
                rot=(rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0, 3)), bevel=0.02)
    # two dark roots cross the crown from the back, clear of the face (no knot, no tails)
    for k, pts in enumerate((((-0.58, 0.2, 0.18), (-0.4, 0.12, 0.5), (-0.05, 0.1, 0.64), (0.35, 0.02, 0.58), (0.58, 0.25, 0.3)),
                             ((0.5, 0.3, 0.22), (0.3, 0.3, 0.56), (-0.1, 0.25, 0.64), (-0.4, 0.3, 0.52), (-0.6, 0.0, 0.15)))):
        tube(kit, f"digger.crown{k}", pts, 0.07, 0.025, M["root"], headg, m=6, k=3)
    # the face: two dark pits and two small seed-green points close together
    for sx in (-1, 1):
        pit = kit.sphere(f"digger.pit{sx}", 0.1, (sx * 0.15, -R + 0.03, 0.08), M["pit"], headg, seg=10)
        pit.scale = (0.8, 0.5, 1.5)
        eye = kit.sphere(f"digger.eye{sx}", 0.03, (sx * 0.15, -R - 0.012, 0.08), M["eye"], headg, seg=10)
        eye.scale = (0.7, 0.6, 1.8)
    # dark roots twisted up the long neck (they turn with the head, half as far, so the neck reads as wrung)
    nr = kit.empty("digger.neckroots", (0, 0, 0.0), body)
    for k in range(5):
        a0 = 2 * math.pi * k / 5
        pts = [(0.15 * math.cos(a0 + 1.4 * u), 0.14 * math.sin(a0 + 1.4 * u), 0.0 + 0.42 * u) for u in (0, 0.25, 0.5, 0.75, 1.0)]
        tube(kit, f"digger.nroot{k}", pts, 0.04, 0.014, M["root"], nr, m=6, k=3)
    ctx["neckroots"] = nr
    ctx["digger"] = {"root": root, "body": body, "neck": neck}
    # the site: a ring of loosened soil and cracks round the base (travels with the root, flat on the ground)
    site = kit.empty("digger.site", (0, 0, 0), root)
    kit.cyl("digger.ring", 0.92, 0.05, (0, 0, 0.0), M["mound"], site, n=24)
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
    # a green glint of light from the eyes, and a warm rim from behind and the side so the dark roots separate from the soil
    kit.light("digger eyes", "POINT", (0, -R - 0.18, 0.06), 1.0, "#9be04a", size=0.01, parent=headg)
    kit.light("digger rim", "POINT", (1.3, 1.1, 0.5), 1.0, "#ffb878", size=0.3, parent=body)
    kit.light("digger rim2", "POINT", (-1.2, -1.2, 0.6), 1.0, "#9fb6e8", size=0.3, parent=body)
    ctx["digger_parts"] = [root]


def build_roots(kit, M, ctx):
    """Every root in the story. Mr Pell's bed and run to the gate, Mum's run up the path in pieces (so a cue can
    shorten it), her fan, the Digger's run to her boots, and small ambient fans round the hill."""
    # --- Mr Pell: a tree's fan round his wellies in plot three, and his longest root out and along the path to the gate
    root_fan(kit, M, "pellfan", 12, 1.5, 175, 5, r0=0.05, loc=(PELL[0], PELL[1], 0), yaw=PELL_AZ)
    run = [(PELL[0] - 0.3, PELL[1], 0.04), (2.6, -9.7, 0.04), (1.7, -9.5, 0.04), (1.0, -9.2, 0.1), (0.55, -8.7, 0.045),
           (0.4, -6.5, 0.04), (0.35, -3.5, 0.04), (0.5, -1.0, 0.04), (0.9, -0.3, 0.04)]
    curl = [(0.9, -0.3, 0.04)] + [(1.05 + 0.15 * math.cos(a), 0.15 * math.sin(a), 0.04 + 0.01 * k)
                                  for k, a in enumerate((-2.6, -3.5, -4.5, -5.5, -6.5, -7.4))]
    tube(kit, "pellrun", run, 0.05, 0.03, M["root"], m=6, k=4)
    tube(kit, "pellcurl", curl, 0.03, 0.012, M["root"], m=6, k=3)
    # --- Mum's run: pieces from plot nine up the path, the branches into plots seven, four and one
    pieces = [  # (name, points, r0, r1, ymax)
        ("m0", [(MUMP[0] - 0.2, MUMP[1] - 0.2, 0.04), (3.2, -28.3, 0.04), (2.4, -28.6, 0.15), (1.6, -28.4, 0.04), (1.0, -28.0, 0.1),
                (0.45, -27.4, 0.04), (0.2, -26.0, 0.04)], 0.075, 0.06, -26.0),
        ("m1", [(0.2, -26.0, 0.04), (-0.15, -24.0, 0.04), (-0.3, -21.0, 0.04)], 0.06, 0.055, -21.0),
        ("m2", [(-0.3, -21.0, 0.04), (-0.1, -18.0, 0.04), (-0.1, -15.0, 0.04)], 0.055, 0.05, -15.0),
        ("m3", [(-0.1, -15.0, 0.04), (-0.4, -12.0, 0.04), (-0.35, -9.5, 0.04)], 0.05, 0.045, -9.5),
        ("m4", [(-0.35, -9.5, 0.04), (-0.1, -6.0, 0.04), (-0.25, -3.0, 0.04), (-0.1, -1.4, 0.04)], 0.045, 0.02, -1.4),
        ("b7", [(-0.3, -22.0, 0.04), (0.3, -22.0, 0.04), (1.0, -22.0, 0.1), (1.7, -21.9, 0.04), (2.3, -22.0, 0.04)], 0.045, 0.02, -21.5),
        ("b4", [(-0.35, -10.3, 0.04), (-1.0, -10.2, 0.1), (-1.7, -10.1, 0.04), (-2.4, -10.0, 0.04)], 0.04, 0.02, -9.8),
        ("b1", [(-0.25, -3.7, 0.04), (0.4, -3.6, 0.04), (1.0, -3.6, 0.1), (1.7, -3.6, 0.04), (2.25, -3.6, 0.04)], 0.04, 0.02, -3.4),
    ]
    groove = pbr(kit, "groove", "#8b7852", 0.97)
    ctx["mumpieces"] = []
    for nm, pts, r0, r1, ymax in pieces:
        ob = tube(kit, f"mumrun.{nm}", pts, r0, r1, M["root"], m=6, k=4)
        gr = ribbon(kit, f"mumgroove.{nm}", pts, 0.15, 0.004 if nm.startswith("m") else 0.0035, groove)
        ctx["mumpieces"].append((ob, gr, ymax))
    # --- Mum's fan at her boots, pose-scaled by a cue, and the curl of her roots over the bucket rim
    mf = kit.empty("mumfan", (MUMP[0], MUMP[1], 0))
    sc = kit.empty("mumfan.scale", (0, 0, 0), mf)
    root_fan(kit, M, "mumfan.fan", 11, 1.35, 150, 11, r0=0.05, parent=sc, yaw=0.0)
    cu = kit.empty("mumfan.curl", (0, 0, 0), mf, rot=(0, 0, math.pi))
    curlp = [(0.0, 0.1, 0.035), (0.0, 0.6, 0.04), (0.0, 1.0, 0.05), (0.0, 1.18, 0.2), (0.0, 1.24, 0.34), (0.0, 1.4, 0.33), (0.0, 1.6, 0.29)]
    tube(kit, "mumfan.curltube", curlp, 0.042, 0.012, M["root"], cu, m=6, k=4)
    ctx["mumfan"] = (mf, sc, cu)
    # --- the Digger's own root: from its waist across the bed into the fan at her boots
    dr = [(DIG[9][0] - 0.05, DIG[9][1] - 0.25, 0.12), (4.05, -26.7, 0.06), (3.95, -27.15, 0.06), (MUMP[0] + 0.05, MUMP[1] + 0.25, 0.05)]
    ctx["digrun"] = tube(kit, "digrun", dr, 0.07, 0.03, M["root"], m=7, k=5)
    # --- small ambient fans, so the other beds show roots too
    for k, (x, y, yw) in enumerate(((-3.4, -22.0, 70), (-3.3, -16.0, 250), (3.4, -16.0, 120), (-3.4, -4.4, 200), (-3.5, -9.5, 20))):
        root_fan(kit, M, f"amb{k}", 8, 1.0, 170, 40 + k, r0=0.035, loc=(x, y, 0), yaw=yw)


def build_holes(kit, M, ctx):
    ctx["holes"] = {}
    for n in (1, 4, 7):
        x, y = DIG[n]
        g = kit.empty(f"hole{n}", (x, y, 0))
        kit.cyl(f"hole{n}.disc", HOLE_R, 0.006, (0, 0, 0.005), M["hole"], g, n=40)
        torus(kit, f"hole{n}.rim", HOLE_R + 0.03, 0.035, (0, 0, 0.012), M["clay2"], g, n=40, m=6, scale=(1, 1, 0.6))
        ctx["holes"][n] = g
    # the round dent left in plot nine's soil when it settles (flat, soft, no hole)
    d = kit.empty("dent", (DIG[9][0], DIG[9][1], 0))
    dd = kit.sphere("dent.disc", 0.78, (0, 0, 0.0), M["mound"], d, seg=14)
    dd.scale = (1, 1, 0.025)
    torus(kit, "dent.rim", 0.82, 0.04, (0, 0, 0.012), M["mound"], d, n=36, m=6, scale=(1, 1, 0.6))
    ctx["dent"] = d
    ctx["pebble"] = kit.sphere("pebble", 0.025, (0, 0, -9), pbr(kit, "pebble", "#77726a", 0.8), seg=8)


def hook_arc(kit, M, name, parent, r, z0):
    """A crook: a half circle on top of the shaft."""
    band(kit, name, [(r - r * math.cos(math.pi * i / 12), 0, z0 + r * math.sin(math.pi * i / 12)) for i in range(13)],
         0.011, M["umb"], parent)


def band(kit, name, pts, r, mat, parent):
    for j in range(len(pts) - 1):
        rod(kit, f"{name}_{j}", pts[j], pts[j + 1], r, mat, parent, n=6)


def umbrella(kit, M, name, loc, canopy, yaw, lean, seed):
    g = kit.empty(name, (loc[0], loc[1], 0), rot=(math.radians(lean[0]), math.radians(lean[1]), math.radians(yaw)))
    kit.cyl(f"{name}.ferrule", 0.009, 0.1, (0, 0, 0.03), M["iron2"], g, n=8)
    kit.cyl(f"{name}.canopy", 0.014, 0.58, (0, 0, 0.38), canopy, g, n=10, r2=0.05)
    kit.cyl(f"{name}.tie", 0.054, 0.04, (0, 0, 0.62), M["iron"], g, n=10, r2=0.052)
    rod(kit, f"{name}.shaft", (0, 0, 0.64), (0, 0, 0.88), 0.011, M["umb"], g, n=7)
    hook_arc(kit, M, f"{name}.hook", g, 0.055, 0.88)
    root_fan(kit, M, f"{name}.fan", 6, 0.4, 175, seed, r0=0.016, parent=g, boots=0.0, yaw=yaw * 0)
    return g


def make_bucket(kit, M, name, loc, parent=None, full=False, bean=False):
    """A steel pail, upright: wider at the top, a bail handle folded down on one side. Optionally full of dark soil,
    optionally with one young bean plant. Returns the group and the toggles."""
    bk = kit.empty(name, loc, parent)
    kit.cyl(f"{name}.body", 0.15, 0.3, (0, 0, 0.15), M["steel"], bk, n=20, r2=0.19)
    torus(kit, f"{name}.rim", 0.19, 0.009, (0, 0, 0.3), M["steel"], bk, n=24, m=5)
    inner = kit.cyl(f"{name}.in", 0.185, 0.004, (0, 0, 0.285), M["black"], bk, n=20)
    soil = kit.cyl(f"{name}.soil", 0.185, 0.04, (0, 0, 0.285), M["bsoil"], bk, n=20)
    tube(kit, f"{name}.bail", [(0.19, 0, 0.29), (0.26, 0, 0.27), (0.3, 0, 0.2), (0.29, 0, 0.12)], 0.008, 0.006, M["steel"], bk, m=5, k=3)
    plant = kit.empty(f"{name}.bean", (0, 0, 0.3), bk)
    tube(kit, f"{name}.stem", [(0, 0, 0), (0.015, 0, 0.18), (0.0, 0.01, 0.34), (0.02, 0, 0.5)], 0.011, 0.005, M["leaf"], plant, m=5, k=3)
    rng = random.Random(7)
    for k in range(7):
        z = 0.1 + 0.07 * k
        a = rng.uniform(0, 6.28)
        kit.box(f"{name}.lf{k}", (0.1, 0.07, 0.008), (0.05 * math.cos(a), 0.05 * math.sin(a), z), M["leaf" if k % 2 else "leaf2"],
                plant, rot=(rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), a), bevel=0.003)
    rod(kit, f"{name}.cane", (-0.04, 0, 0), (-0.04, 0, 0.62), 0.006, M["cane"], plant, n=5)
    return bk, inner, soil, plant


def build_props(kit, M, ctx):
    tog = {}
    # --- the gate: three closed umbrellas stood tip-down in the verge, each with a small fan of dark roots at its tip
    for k, (x, y, col, lean) in enumerate(((1.5, -0.7, M["umbnavy"], (4, 3)), (1.95, -0.52, M["umbred"], (-3, 5)),
                                           (2.4, -0.74, M["umbgreen"], (2, -4)))):
        umbrella(kit, M, f"umb{k}", (x, y), col, 40 * k, lean, 70 + k)
    # --- Mr Pell's giant pot on its barrow (shown by a cue)
    pg = kit.empty("potbarrow", (POT[0], POT[1], 0))
    kit.box("barrow.tray", (1.0, 1.5, 0.1), (0, 0, 0.38), M["post"], pg, bevel=0.015)
    for sx in (-1, 1):
        kit.box(f"barrow.side{sx}", (0.05, 1.5, 0.22), (sx * 0.5, 0, 0.5), M["post"], pg, bevel=0.01)
        rod(kit, f"barrow.handle{sx}", (sx * 0.4, -0.55, 0.42), (sx * 0.46, -1.55, 0.78), 0.03, M["post"], pg, n=8)
        kit.box(f"barrow.leg{sx}", (0.06, 0.06, 0.34), (sx * 0.42, -0.55, 0.17), M["post"], pg, bevel=0.01)
    torus(kit, "barrow.wheel", 0.27, 0.05, (0, 0.95, 0.3), M["tyre"], pg, rot=(0, math.radians(90), 0), n=22, m=6)
    kit.cyl("barrow.hub", 0.05, 0.12, (0, 0.95, 0.3), M["iron2"], pg, rot=(0, math.radians(90), 0), n=10)
    kit.box("barrow.fork", (0.6, 0.05, 0.06), (0, 0.95, 0.3), M["post"], pg)
    kit.cyl("pot.body", 0.5, 0.66, (0, 0, 0.75), M["terra"], pg, n=28, r2=0.62)
    torus(kit, "pot.rim", 0.62, 0.05, (0, 0, 1.08), M["terra"], pg, n=28, m=6)
    kit.cyl("pot.soil", 0.6, 0.02, (0, 0, 1.03), M["bsoil"], pg, n=28)
    tog["pot"] = ([pg], False)
    # --- the bucket, the flask
    bk, binner, bsoil, bplant = make_bucket(kit, M, "bucket", (-20, -20, 0))
    ctx["bucket"] = (bk, binner, bsoil, bplant)
    fk = kit.empty("flask", (-20, -20, 0))
    kit.cyl("flask.body", 0.05, 0.19, (0, 0, 0.095), M["steel"], fk, n=14)
    kit.cyl("flask.neck", 0.026, 0.04, (0, 0, 0.21), M["steel"], fk, n=10)
    kit.cyl("flask.cap", 0.03, 0.03, (0, 0, 0.245), M["flaskcap"], fk, n=10)
    ctx["flask"] = fk
    # --- the bike, with the bucket hung on its handlebars and her roots trailing from it
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
    make_bucket(kit, M, "bikebucket", (0, -0.8, 0.66), bike, full=True, bean=True)
    ctx["bikebucket_on"] = True
    for nm in ("bikebucket.in",):
        bpy.data.objects[nm].hide_render = True
    rod(kit, "bike.bucketstrap", (0, -0.62, 0.95), (0.0, -0.8, 0.96), 0.008, M["iron"], bike, n=5)
    tube(kit, "bike.trail", [(0.12, -0.8, 0.66), (0.22, -0.75, 0.4), (0.3, -0.35, 0.08), (0.3, 0.5, 0.035), (0.2, 1.4, 0.03), (0.0, 2.1, 0.03)],
         0.026, 0.008, M["root"], bike, m=6, k=4)
    ctx["bike"] = bike
    ctx["tog"] = tog


def build_interior(kit, M, x0, ctx):
    """Mum's shed from inside: the camera looks +y at the back wall (y = 1.9). The tool wall on the left is bare,
    every hook empty, and a shelf on the right is half cleared."""
    wood = M["inwood"]
    kit.box(f"in{x0}.floor", (2.8, 3.0, 0.05), (x0, 0.6, -0.025), M["post"])
    kit.box(f"in{x0}.back", (2.8, 0.06, 2.4), (x0, 1.9, 1.2), wood)
    kit.box(f"in{x0}.front", (2.8, 0.06, 2.4), (x0, -0.9, 1.2), wood)
    for s in (-1, 1):
        kit.box(f"in{x0}.side{s}", (0.06, 2.8, 2.4), (x0 + s * 1.4, 0.5, 1.2), wood)
    kit.box(f"in{x0}.ceil", (2.8, 2.9, 0.06), (x0, 0.5, 2.4), M["roof"])
    for dx in (-1.0, -0.7, -0.4, -0.1, 0.2, 0.5):     # bare hooks
        kit.box(f"in{x0}.hook{dx}", (0.04, 0.08, 0.04), (x0 + dx, 1.84, 1.65), M["iron2"], bevel=0.008)
        kit.box(f"in{x0}.hookb{dx}", (0.04, 0.08, 0.04), (x0 + dx, 1.84, 1.2), M["iron2"], bevel=0.008)
    sx_ = x0 + 0.95
    kit.box(f"in{x0}.shelf", (0.9, 0.35, 0.04), (sx_, 1.72, 1.0), M["post"], bevel=0.005)
    kit.box(f"in{x0}.shelf2", (0.9, 0.35, 0.04), (sx_, 1.72, 1.5), M["post"], bevel=0.005)
    kit.sphere(f"in{x0}.twine", 0.08, (sx_ - 0.25, 1.7, 1.1), M["twine"], seg=12)
    kit.box(f"in{x0}.pack0", (0.1, 0.012, 0.14), (sx_ - 0.1, 1.78, 1.58), M["paper"], bevel=0.003)
    kit.light(f"lamp{x0}", "POINT", (x0 + 0.1, 0.3, 2.0), 12.0, "#ffeedd", size=0.12)
    kit.light(f"lamp{x0}b", "POINT", (x0 + 0.8, 1.2, 1.6), 4.0, "#ffeedd", size=0.1)
    kit.light(f"lamp{x0}c", "POINT", (x0 + 0.3, 1.1, 1.5), 8.0, "#ffeedd", size=0.1)


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
    build_roots(kit, M, ctx)
    build_holes(kit, M, ctx)
    build_props(kit, M, ctx)
    build_interior(kit, M, 60.0, ctx)
    # the sun, and a character-only fill from the other side (the Digger never gets it: front lights dead)
    sun = kit.light("sun", "SUN", tuple(SUN_DIR * 40), 1.0, "#ffb184", size=0.02)
    kit.aim(sun, (0, 0, 0))
    ctx["sun"] = sun
    fill = kit.light("char fill", "SUN", tuple(FILL_DIR * 40), 1.0, "#a5b8e6", size=0.02)
    kit.aim(fill, (0, 0, 0))
    ctx["fill"] = fill
    ctx["inited"] = False
    return ctx


# ------------------------------------------------------------------------------------------------ animate
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
    for who, mat, lo in (("me", M["wellig"], 1.0), ("carter", M["wellid"], 0.62), ("newcomer", M["wellid"], 0.8)):
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg is None:
                continue
            kit.box(f"{who}.welly{sx}", (1.04, 1.06, 0.9 * lo), (0, 0, -1.4 + (1 - lo) * 0.45), mat, leg, bevel=0.08)
    hg = bpy.data.objects.get("carter.headg")
    if hg is not None:
        ctx["grandcap"] = kit.box("carter.capc", (2 * faces.HEAD_R + 0.16, 2 * faces.HEAD_R + 0.2, 0.17), (0, 0.02, 0.58), M["capwool"], hg, bevel=0.06)
        kit.box("carter.mous", (0.4, 0.09, 0.09), (0, -faces.HEAD_R - 0.01, -0.15), M["mous"], hg, bevel=0.03)
        for sx in (-1, 1):
            kit.box(f"carter.mousend{sx}", (0.1, 0.08, 0.15), (sx * 0.2, -faces.HEAD_R + 0.0, -0.2), M["mous"], hg, bevel=0.03)
    hg2 = bpy.data.objects.get("newcomer.headg")
    if hg2 is not None:
        kit.box("newcomer.tail", (0.46, 0.44, 1.5), (0, faces.HEAD_R + 0.22, -0.3), M["pony"], hg2, bevel=0.1)
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
    over = {"sun": s["sun"], "char fill": s["fill"]}
    # ---------------------------------------------------------------- the Digger
    dg = ctx["digger"]
    c = _last(_cues(tl, "digger"), t) or {"hidden": True}
    hidden = bool(c.get("hidden"))
    _show([dg["root"]], not hidden)
    over["digger eyes"] = 0.0 if hidden else 0.35
    over["digger rim"] = 0.0 if hidden else 55.0
    over["digger rim2"] = 0.0 if hidden else 22.0
    if not hidden:
        px, py = DIG[c["plot"]]
        dg["root"].location = (px, py, 0)
        dg["root"].rotation_euler = (0, 0, math.radians(c.get("yaw", 0)))
        dg["body"].location = (0, 0, c["up"])
        dg["neck"].rotation_euler = (0, 0, math.radians(c.get("head", 0)))
        ctx["neckroots"].rotation_euler = (0, 0, math.radians(c.get("head", 0)) * 0.5)
        # the loosened ring stays at the ground whatever the height
        ctx["site"].location = (0, 0, 0)
        _show([ctx["site"]], not c.get("nosite"))
    hc = _last(_cues(tl, "holes"), t) or {"plots": []}
    for n, g in ctx["holes"].items():
        _show([g], n in hc["plots"])
    _show([ctx["dent"]], bool((_last(_cues(tl, "dent"), t) or {}).get("on")))
    # ---------------------------------------------------------------- the gate, the shed door
    go = float(_eased(_cues(tl, "gate"), "open", t, 0.0))
    ctx["leaves"][-1].rotation_euler = (0, 0, math.radians(95) * go)
    ctx["leaves"][1].rotation_euler = (0, 0, -math.radians(95) * go)
    so = float(_eased(_cues(tl, "shed"), "open", t, 0.0))
    ctx["door"].rotation_euler = (0, 0, -math.radians(82) * so)
    # ---------------------------------------------------------------- props that switch on and off
    for nm, (objs, default) in ctx["tog"].items():
        on = (_last(_cues(tl, nm), t) or {"on": default}).get("on", default)
        _show(objs, bool(on))
    # the bucket (upright, empty or full of soil, with or without its bean) and the flask
    bc_ = _last(_cues(tl, "bucket"), t) or {"pos": [-20, -20]}
    bk, binner, bsoil, bplant = ctx["bucket"]
    bk.location = (bc_["pos"][0], bc_["pos"][1], 0)
    _show([bk], True)
    _show([binner], not bc_.get("full"))
    _show([bsoil], bool(bc_.get("full")))
    _show([bplant], bool(bc_.get("bean")))
    fc_ = _last(_cues(tl, "flask"), t) or {"pos": [-20, -20]}
    ctx["flask"].location = (fc_["pos"][0], fc_["pos"][1], 0)
    # ---------------------------------------------------------------- roots
    mr = _last(_cues(tl, "mumrun"), t) or {"to": 0.0, "groove": False}
    for ob, gr, ymax in ctx["mumpieces"]:
        shown = ymax <= mr["to"] + 0.4
        _show([ob], shown)
        _show([gr], (not shown) and bool(mr.get("groove")))
    mf, sc, cu = ctx["mumfan"]
    fcue = _last(_cues(tl, "mumfan"), t) or {"off": True}
    if fcue.get("off"):
        _show([mf], False)
    else:
        _show([mf], True)
        mf.location = (fcue["pos"][0], fcue["pos"][1], 0)
        mf.rotation_euler = (0, 0, math.radians(fcue["yaw"]))
        sc.scale = (fcue["scale"], fcue["scale"], 1.0)
        _show([cu], bool(fcue.get("bucket")))
    _show([ctx["digrun"]], bool((_last(_cues(tl, "digrun"), t) or {}).get("on")))
    # the bike: beside the newcomer while she wheels it
    bc = _last(_cues(tl, "bike"), t) or {"on": False}
    bike = ctx["bike"]
    if bc.get("on"):
        nc = bpy.data.objects.get("newcomer")
        if nc is not None and not nc.hide_render:
            p = nc.matrix_world @ V((-1.55, -0.2, 0))
            bike.location = (p.x, p.y, 0)
            bike.rotation_euler = (0, 0, nc.matrix_world.to_euler().z)
        else:
            bike.location = (0, 0, -9)
    else:
        bike.location = (0, 0, -9)
    # ---------------------------------------------------------------- the pebble into plot one's hole
    pc = _last(_cues(tl, "pebble"), t)
    pb = ctx["pebble"]
    if pc:
        u = t - pc["t"]
        z = 1.35 - 4.9 * u * u
        f0, f1 = pc["from"], pc["to"]
        pb.location = (f0[0] + (f1[0] - f0[0]) * min(1, u / 0.5), f0[1] + (f1[1] - f0[1]) * min(1, u / 0.5), z) if z > -0.2 else (0, 0, -9)
    else:
        pb.location = (0, 0, -9)
    return over
