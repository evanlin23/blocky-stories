"""ep51 "Fossil hall": a town museum's fossil hall on Friday late openings.

Places (metres, floor z = 0, a character with yaw 0 faces -y, yaw 90 faces +x, a seated one has yaw 180 here):
  hall        x -14..14, y -10..8. The big skeleton runs along x at y = 1.5 (head at x -4.4, tail tip at x 7.5). The long bench
              sits at y = -3.4, seat 0.46 high, 3.4 long, facing the skeleton (+y). Abe's end is x +1.0, mine x -1.0.
              The arch at x = -14 opens onto the dark galleries.
  gallery     x -34..-14, y -3.2..3.2, cases down both long walls.
  basement    x 100 (a low concrete store), stairs and the door at x 140.
  montage     living room x 180, doorstep x 220, park bench x 260, restaurant x 300, steps x 340, street x 380, bedroom x 420.

The glow (the rule's marker) is a stack of soft shells behind each body: back faces only, gold emission, so each
character wears an outline of light that never covers the face. Strength 1 is a faint rim, 6 a lamp. It only ever
ramps (cues "glow" with a dur), and it stays below clipping (the shells' emission is capped, see GLOW_UNIT).
The Stooped is one model (build_stooped), posed by the "stooped" cue and never seen moving: a pose changes across a cut.
"""

from __future__ import annotations

import math
import random

import bpy
from mathutils import Vector as V
from PIL import Image, ImageDraw

from blocky import faces, rig

U = 0.34                       # metres per rig unit
GLOW_UNIT = 0.7               # emission strength of the nearest shell at glow strength 1
SHELLS = ((0.035, 1.0), (0.085, 0.5), (0.15, 0.22))   # (grow in rig units, share of the strength)
GOLD = "#ffd98a"
GLOW_GOLD = "#ffb83a"


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
    """A numeric cue value that ramps over the cue's dur."""
    level = prev = default
    for c in cs:
        if c["t"] > t + 1e-9 or key not in c:
            continue
        prev, level = level, c[key]
        d = float(c.get("dur", 0.0))
        if d > 0 and t < c["t"] + d:
            level = prev + (level - prev) * _ss((t - c["t"]) / d)
    return level


def _who(c, who):
    w = c.get("who")
    return w == who or (isinstance(w, list) and who in w)


def _show(objs, on):
    for o in objs:
        for oo in [o] + list(o.children_recursive):
            oo.hide_render = not on


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _lin(c):
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def pbr(kit, name, hexc, rough=0.6, metal=0.0, spec=0.4, noise=None, bump=0.0):
    """A Principled material through kit's fog. noise = (scale, dark factor)."""
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
    if noise:
        tc = N.new("ShaderNodeTexCoord")
        nz = N.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = noise[0]
        nz.inputs["Detail"].default_value = 5.0
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
            bp.inputs["Distance"].default_value = 0.02
            L.new(nz.outputs["Fac"], bp.inputs["Height"])
            L.new(bp.outputs["Normal"], b.inputs["Normal"])
    m.diffuse_color = kit.col(hexc)
    kit._fogged(m, b.outputs[0])
    return m


def film(kit, name, hexc, amount):
    """A see-through film: transparent, with `amount` of a diffuse colour over it (dust on glass)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    d = N.new("ShaderNodeBsdfDiffuse")
    d.inputs["Color"].default_value = kit.col(hexc)
    t = N.new("ShaderNodeBsdfTransparent")
    mix = N.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = amount
    L.new(t.outputs[0], mix.inputs[1])
    L.new(d.outputs[0], mix.inputs[2])
    kit._fogged(m, mix.outputs[0])
    return m


def clear_glass(kit, name="clear glass"):
    """Cheap glass: mostly transparent with a faint glossy sheen, so cases read without the cost of refraction."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    g = N.new("ShaderNodeBsdfGlossy")
    g.inputs["Roughness"].default_value = 0.04
    g.inputs["Color"].default_value = (0.8, 0.9, 0.88, 1)
    t = N.new("ShaderNodeBsdfTransparent")
    mix = N.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = 0.07
    L.new(t.outputs[0], mix.inputs[1])
    L.new(g.outputs[0], mix.inputs[2])
    kit._fogged(m, mix.outputs[0])
    return m


def materials(kit):
    M = {}
    M["marble"] = kit.checker("#e9dfca", "#a39f97", 1 / 0.9, "marble", 0.3)
    M["wall"] = pbr(kit, "wall", "#ece3d0", 0.9, noise=(1.2, 0.92))
    M["ceil"] = pbr(kit, "ceil", "#e2d8c0", 0.9)
    M["beam"] = pbr(kit, "beam", "#5b3f29", 0.7, noise=(6, 0.8))
    M["wood"] = pbr(kit, "wood dark", "#4a3324", 0.6, noise=(8, 0.75), bump=0.2)
    M["bench"] = pbr(kit, "bench wood", "#8a5a34", 0.55, noise=(9, 0.7), bump=0.2)
    M["iron"] = pbr(kit, "iron", "#26262a", 0.5, 0.9, noise=(5, 0.8))
    M["bone"] = pbr(kit, "bone", "#c9a46a", 0.72, noise=(4, 0.85), bump=0.15)
    M["mend"] = pbr(kit, "mended bone", "#d8d4c8", 0.7)
    M["seam"] = pbr(kit, "seam", "#3a3226", 0.9)
    M["felt"] = pbr(kit, "felt", "#2f4a3a", 0.95)
    M["felt2"] = pbr(kit, "felt2", "#5a2f2f", 0.95)
    M["shell"] = pbr(kit, "shell", "#e6dcc6", 0.5)
    M["fern"] = pbr(kit, "fern", "#4f7a3a", 0.8)
    M["tooth"] = pbr(kit, "tooth", "#efe8d6", 0.45)
    M["glass"] = clear_glass(kit)
    M["dust"] = film(kit, "dust film", "#a7aeb0", 0.5)
    M["plinth"] = pbr(kit, "plinth", "#5a4030", 0.7, noise=(7, 0.8))
    M["lamp"] = kit.emit("#fff0d4", 6.0, "lamp face")
    M["window"] = kit.emit("#9fb6e0", 0.9, "window")
    M["concrete"] = kit.concrete("#5d5a55", 1.5, 0.45, "concrete")
    M["crate"] = pbr(kit, "crate", "#7d5d3c", 0.8, noise=(10, 0.7), bump=0.2)
    M["sheet"] = pbr(kit, "dust sheet", "#cfc8b8", 0.95, noise=(3, 0.85))
    M["shelf"] = pbr(kit, "shelf", "#3d3e42", 0.6, 0.8)
    M["bulb"] = pbr(kit, "bulb off", "#8d8a80", 0.3)
    M["torch"] = pbr(kit, "torch body", "#2c5a3a", 0.4)
    M["lens"] = kit.emit("#ffe2a8", 3.0, "torch lens")
    M["gold"] = kit.emit(GOLD, 0.9, "gold glimmer")
    M["coat"] = pbr(kit, "stooped coat", "#4a3c2c", 0.9, noise=(6, 0.82))
    M["brass"] = pbr(kit, "brass", "#b08a3e", 0.35, 0.9)
    M["trou"] = pbr(kit, "stooped trousers", "#54473a", 0.9)
    M["shoe"] = pbr(kit, "stooped shoes", "#4a3626", 0.6)
    M["skin"] = pbr(kit, "stooped skin", "#3a3028", 0.85)
    M["hand"] = pbr(kit, "stooped hands", "#6e5c48", 0.8)
    M["sandstone"] = pbr(kit, "sandstone", "#d9c6a5", 0.85, noise=(2.2, 0.9), bump=0.2)
    M["grass"] = pbr(kit, "grass", "#5f8a3f", 0.95, noise=(9, 0.8))
    M["road"] = pbr(kit, "road", "#4b4b50", 0.9, noise=(5, 0.85))
    M["pave"] = pbr(kit, "pavement", "#a8a39a", 0.85, noise=(3, 0.9))
    M["brick"] = kit.bricks("#8a4a38", "#6e3a2c", "#5a5550", 1.0, "bricks")
    M["floor_wood"] = kit.planks("#8a6a45", "#6a4e30", 1.0, "X", "floorwood")
    M["sofa"] = pbr(kit, "sofa", "#5d6f8a", 0.9, noise=(8, 0.85))
    M["cloth"] = pbr(kit, "tablecloth", "#f0ebe0", 0.9)
    M["bed"] = pbr(kit, "bed", "#8a9ab5", 0.9, noise=(6, 0.85))
    M["pillow"] = pbr(kit, "pillow", "#e9e5da", 0.9)
    M["towel"] = kit.checker("#e8e2d2", "#8a9fb8", 6.0, "towel", 0.95)
    M["leaf"] = pbr(kit, "leaf", "#3f7a37", 0.9, noise=(6, 0.8))
    M["trunk"] = pbr(kit, "trunk", "#5a4330", 0.9, noise=(8, 0.7))
    M["door"] = pbr(kit, "front door", "#2f5a4a", 0.6)
    M["candle"] = pbr(kit, "candle", "#f4ecd8", 0.6)
    M["flame"] = kit.emit("#ffc060", 5.0, "flame")
    M["fern_rel"] = pbr(kit, "fern relief", "#bba784", 0.85)
    M["spark"] = kit.emit(GOLD, 2.0, "spark")
    return M


def B(kit, name, size, loc, mat, parent=None, rot=(0, 0, 0), bevel=0.0):
    return kit.box(name, size, loc, mat, parent, rot, bevel=bevel)


# ------------------------------------------------------------------------------------------------ the hall
def case(kit, M, name, x, y, face, length=1.8, depth=0.8, dusty=False, items=0, parent=None):
    """A glass-fronted case on a dark wood plinth. `face` is the direction its glass front looks: +1 faces +y, -1 faces -y,
    +2 faces +x, -2 faces -x. A dusty case wears a film on the front and top, with a clean stripe at knee height that
    a cue shows or hides (ctx['stripes'])."""
    horiz = abs(face) == 1          # glass front along x
    sx, sy = (length, depth) if horiz else (depth, length)
    g = kit.empty(name, (x, y, 0), parent)
    B(kit, f"{name}.plinth", (sx, sy, 0.32), (0, 0, 0.16), M["plinth"], g, bevel=0.02)
    B(kit, f"{name}.base", (sx - 0.1, sy - 0.1, 0.1), (0, 0, 0.37), M["wood"], g, bevel=0.02)
    B(kit, f"{name}.felt", (sx - 0.2, sy - 0.2, 0.04), (0, 0, 0.44), M["felt"] if items % 2 == 0 else M["felt2"], g)
    top = B(kit, f"{name}.top", (sx, sy, 0.1), (0, 0, 1.62), M["wood"], g, bevel=0.02)
    for cx in (-1, 1):
        for cy in (-1, 1):
            B(kit, f"{name}.post{cx}{cy}", (0.06, 0.06, 1.2), (cx * (sx / 2 - 0.03), cy * (sy / 2 - 0.03), 1.0), M["wood"], g)
    # contents: blocky shells, ferns and teeth on the felt
    rnd = random.Random(sum(map(ord, name)))
    for k in range(3 + items % 3):
        px, py = rnd.uniform(-sx / 2 + 0.25, sx / 2 - 0.25), rnd.uniform(-sy / 2 + 0.2, sy / 2 - 0.2)
        kind = rnd.choice(("shell", "fern", "tooth"))
        if kind == "shell":
            B(kit, f"{name}.sh{k}", (0.24, 0.2, 0.12), (px, py, 0.52), M["shell"], g, rot=(0, 0, rnd.uniform(0, 3)), bevel=0.04)
            B(kit, f"{name}.sh{k}b", (0.15, 0.13, 0.1), (px, py, 0.62), M["shell"], g, rot=(0, 0, rnd.uniform(0, 3)), bevel=0.03)
        elif kind == "fern":
            for j in range(4):
                B(kit, f"{name}.fe{k}{j}", (0.05, 0.3 - 0.05 * j, 0.03), (px + 0.1 * j, py, 0.48 + 0.05 * j), M["fern"], g,
                  rot=(0, 0, 0.3 * j), bevel=0.01)
        else:
            kit.cyl(f"{name}.to{k}", 0.07, 0.3, (px, py, 0.62), M["tooth"], g, n=8, r2=0.01)
    # the glass: the front and the top, in one thin pane each
    n = {1: (0, 1), -1: (0, -1), 2: (1, 0), -2: (-1, 0)}[face]
    off = (sx / 2 if n[0] else 0) * n[0], (sy / 2 if n[1] else 0) * n[1]
    gs = (0.02, sy - 0.08, 1.2) if n[0] else (sx - 0.08, 0.02, 1.2)
    B(kit, f"{name}.pane", gs, (off[0] - n[0] * 0.03, off[1] - n[1] * 0.03, 1.0), M["glass"], g)
    ctx_stripes = []
    if dusty:
        # the film is two pieces with a gap at knee height: below 0.42 and above 0.6 of the pane (z 0.4..1.6)
        for nm, z0, z1 in (("lo", 0.4, 0.46), ("hi", 0.6, 1.6)):
            if n[0]:
                sz = (0.014, sy - 0.04, z1 - z0)
            else:
                sz = (sx - 0.04, 0.014, z1 - z0)
            B(kit, f"{name}.film{nm}", sz, (off[0] + n[0] * 0.012, off[1] + n[1] * 0.012, (z0 + z1) / 2), M["dust"], g)
        # the stripe's gap is filled with film until the cue shows it (z 0.46..0.6)
        if n[0]:
            sz = (0.014, sy - 0.04, 0.14)
        else:
            sz = (sx - 0.04, 0.014, 0.14)
        fill = B(kit, f"{name}.stripefill", sz, (off[0] + n[0] * 0.012, off[1] + n[1] * 0.012, 0.53), M["dust"], g)
        ctx_stripes.append(fill)
        B(kit, f"{name}.dusttop", (sx, sy, 0.012), (0, 0, 1.575), M["dust"], g)
    return g, ctx_stripes


def build_hall(kit, M, ctx):
    kit.plane("hall floor", (28, 18), (0, -1, 0), M["marble"])
    # walls, with an arch at x = -14 onto the galleries (y -1.5..1.5, 3.6 high)
    B(kit, "wall back", (28.8, 0.4, 7.4), (0, 8.2, 3.7), M["wall"])
    B(kit, "wall front", (28.8, 0.4, 7.4), (0, -10.2, 3.7), M["wall"])
    B(kit, "wall +x", (0.4, 18.8, 7.4), (14.2, -1, 3.7), M["wall"])
    B(kit, "wall -x a", (0.4, 8.5, 7.4), (-14.2, -5.75, 3.7), M["wall"])
    B(kit, "wall -x b", (0.4, 6.5, 7.4), (-14.2, 4.75, 3.7), M["wall"])
    B(kit, "wall -x lintel", (0.4, 3.0, 3.8), (-14.2, 0, 5.5), M["wall"])
    B(kit, "ceiling", (28.8, 18.8, 0.3), (0, -1, 7.55), M["ceil"])
    for i in range(-3, 4):
        B(kit, f"beam x{i}", (0.4, 18.8, 0.35), (i * 4.0, -1, 7.3), M["beam"])
    for j in range(-2, 3):
        B(kit, f"beam y{j}", (28.8, 0.4, 0.35), (0, -1 + j * 3.6, 7.3), M["beam"])
    # skirting and pilasters
    for x in range(-12, 13, 4):
        B(kit, f"pil back {x}", (0.6, 0.3, 7.2), (x, 7.9, 3.6), M["wall"], bevel=0.04)
        B(kit, f"pil front {x}", (0.6, 0.3, 7.2), (x, -9.9, 3.6), M["wall"], bevel=0.04)
    B(kit, "skirt back", (28, 0.12, 0.35), (0, 7.98, 0.18), M["beam"])
    B(kit, "skirt front", (28, 0.12, 0.35), (0, -9.98, 0.18), M["beam"])
    # cases along the back and front walls
    ctx["stripes"] = []
    k = 0
    for x in (-11, -8.6, -6.2, 4.4, 6.8, 9.2, 11.6):
        case(kit, M, f"hcase b{k}", x, 7.4, -1, items=k)
        k += 1
    for x in (-11, -8.6, -6.2, -3.8, -1.4, 1.0, 3.4, 5.8, 8.2, 10.6):
        case(kit, M, f"hcase f{k}", x, -9.4, 1, items=k)
        k += 1
    for y in (-6, -3.4, -0.8, 1.8, 4.4):
        case(kit, M, f"hcase e{k}", 13.4, y, -2, length=1.8, items=k)
        k += 1
    # lamps: area lights in the ceiling, and the lamp faces you see looking up
    for i, x in enumerate((-9, -3, 3, 9)):
        kit.light(f"hall{i}", "AREA", (x, -2.0, 6.9), 1500.0, "#ffe8c8", rot=(0, 0, 0), size=3.0)
        for dy in (-2.4, 2.4):
            B(kit, f"lampface {x} {dy}", (1.8, 0.2, 0.06), (x, -2.0 + dy, 7.1), M["lamp"])
    kit.light("stooped rim", "SPOT", (-1.0, -8.2, 3.0), 700.0, "#8fb0ff", size=0.3, spot=34, blend=0.7)
    kit.aim(kit.LIGHTS["stooped rim"]["obj"], (-1.0, -3.9, 1.2))
    kit.light("tail gold", "POINT", (5.6, -0.5, 2.3), 140.0, GOLD, size=0.3)
    kit.light("hall blue", "AREA", (0, -1.5, 6.8), 650.0, "#7f9bd6", rot=(0, 0, 0), size=10.0)
    ctx["lamp_mat"] = M["lamp"]


def build_skeleton(kit, M, ctx):
    root = kit.empty("skel", (0, 1.5, 0))
    for i in range(4):
        B(kit, f"vert{i}", (0.82, 1.1, 1.1), (-1.2 + 0.85 * i, 0, 2.4), M["bone"], root, bevel=0.06)
        if i:
            B(kit, f"vgap{i}", (0.06, 1.0, 1.0), (-1.2 + 0.85 * i - 0.43, 0, 2.4), M["seam"], root)
    # ribs
    for k in range(5):
        for s in (-1, 1):
            B(kit, f"rib{k}{s}", (0.1, 0.1, 1.0), (-1.2 + 0.65 * k + 0.2, s * 0.62, 1.95), M["bone"], root,
              rot=(s * 0.18, 0, 0), bevel=0.03)
    # four legs, each a stack of three blocks
    for lx, ly in ((-1.2, -0.6), (-1.2, 0.6), (1.45, -0.6), (1.45, 0.6)):
        for j in range(3):
            B(kit, f"leg{lx}{ly}{j}", (0.5, 0.5, 0.58), (lx, ly, 0.3 + 0.63 * j), M["bone"], root, bevel=0.05)
        B(kit, f"foot{lx}{ly}", (0.66, 0.74, 0.12), (lx, ly, 0.06), M["bone"], root, bevel=0.04)
    # the neck: a stack of blocks stepping up and out toward -x, parented to a pivot
    neck = kit.empty("skel.neck", (-1.7, 0, 3.0), root)
    n = 7
    for i in range(n):
        u = i / (n - 1)
        sz = 0.64 - 0.28 * u
        B(kit, f"neckblock{i}", (sz, sz * 0.95, sz), (-2.0 * u * 1.1, 0, 2.2 * u + 0.1), M["bone"], neck,
          rot=(0, math.radians(-40 + 25 * u), 0), bevel=0.04)
    headp = kit.empty("skel.head", (-2.4, 0, 2.5), neck)
    B(kit, "skull", (0.95, 0.5, 0.46), (-0.3, 0, 0.0), M["bone"], headp, bevel=0.07)
    B(kit, "snout", (0.5, 0.36, 0.3), (-0.82, 0, -0.04), M["bone"], headp, bevel=0.05)
    B(kit, "jaw", (0.8, 0.4, 0.14), (-0.55, 0, -0.3), M["bone"], headp, bevel=0.04)
    for s in (-1, 1):
        B(kit, f"socket{s}", (0.14, 0.05, 0.14), (-0.28, s * 0.25, 0.08), M["seam"], headp)
    ctx["skel_neck"], ctx["skel_head"] = neck, headp
    # the tail: ten blocks tapering down toward the tip, one pale and mended
    for k in range(10):
        sz = 0.84 - 0.065 * k
        x = 2.3 + 0.56 * k
        z = 2.45 - 0.115 * k
        mat = M["mend"] if k == 7 else M["bone"]
        B(kit, f"tail{k}", (0.52, sz, sz * 0.9), (x, 0, z), mat, root, bevel=0.04)
        if k == 7:
            B(kit, "seam a", (0.02, sz + 0.02, sz * 0.9 + 0.02), (x - 0.265, 0, z), M["seam"], root)
            B(kit, "seam b", (0.02, sz + 0.02, sz * 0.9 + 0.02), (x + 0.265, 0, z), M["seam"], root)
    # iron frame: posts and base plates
    for (px, h) in ((-2.4, 3.9), (4.0, 2.1), (6.0, 1.4)):
        kit.cyl(f"post{px}", 0.035, h, (px, 0, h / 2), M["iron"], root, n=8)
        B(kit, f"plate{px}", (0.5, 0.5, 0.04), (px, 0, 0.02), M["iron"], root)
    B(kit, "frame bar", (3.6, 0.05, 0.05), (0.2, 0, 1.8), M["iron"], root)


def build_bench(kit, M, ctx):
    y = -3.4
    B(kit, "bench seat", (2.8, 0.5, 0.07), (0, y, 0.43), M["bench"], bevel=0.02)
    B(kit, "bench slat", (2.8, 0.5, 0.07), (0, y, 0.43), M["bench"], bevel=0.02)
    B(kit, "bench rail", (2.6, 0.04, 0.1), (0, y - 0.2, 0.3), M["iron"])
    for s in (-1, 1):
        # a slab leg, wider than it is thick
        B(kit, f"bench leg{s}", (0.06, 0.46, 0.43), (s * 1.25, y, 0.215), M["iron"], bevel=0.01)
        B(kit, f"bench foot{s}", (0.24, 0.5, 0.04), (s * 1.25, y, 0.02), M["iron"], bevel=0.01)
    # the lore plant: two short upright dust-brown strokes on the inner face of the leg at my end (x = -1.55 leg, face +x)
    sm = pbr(kit, "tally", "#d8c49a", 0.9)
    for dy in (-0.09, 0.09):
        B(kit, f"tally{dy}", (0.014, 0.04, 0.24), (-1.25 - 0.036, y + dy, 0.2), sm)
    kit.light("tally lamp", "POINT", (-1.75, y, 0.34), 4.0, "#ffe2b0", size=0.1)


def build_gallery(kit, M, ctx):
    x0, x1 = -34.0, -14.0
    cx = (x0 + x1) / 2
    kit.plane("gal floor", (21, 6.6), (cx, 0, 0), M["marble"])
    B(kit, "gal wall n", (21, 0.3, 6.5), (cx, 3.45, 3.25), M["wall"])
    B(kit, "gal wall s", (21, 0.3, 6.5), (cx, -3.45, 3.25), M["wall"])
    B(kit, "gal wall end", (0.3, 7, 6.5), (x0 - 0.15, 0, 3.25), M["wall"])
    B(kit, "gal ceil", (21, 7, 0.3), (cx, 0, 6.5), M["ceil"])
    # windows high up: pale blue panels, the only daylight left
    for i in range(6):
        wx = x0 + 2.5 + i * 3.4
        for sy in (-1, 1):
            B(kit, f"galwin{i}{sy}", (1.2, 0.05, 1.3), (wx, sy * 3.28, 4.7), M["window"])
    for k, x in enumerate(range(-33, -15, 2)):
        cs = case(kit, M, f"gcase n{k}", x + 0.2, 2.5, -1, length=1.7, dusty=True, items=k)
        ctx["stripes"] += cs[1]
        cs = case(kit, M, f"gcase s{k}", x + 0.2, -2.5, 1, length=1.7, dusty=True, items=k + 1)
        ctx["stripes"] += cs[1]
    kit.light("gal moon", "AREA", (-24, 0, 6.2), 650.0, "#6f8fcf", rot=(0, 0, 0), size=8.0)


def build_basement(kit, M, ctx):
    X = 100.0
    kit.plane("base floor", (6, 6), (X, 0, 0), M["concrete"])
    B(kit, "base wall n", (6.4, 0.2, 2.6), (X, 3.1, 1.3), M["concrete"])
    B(kit, "base wall s", (6.4, 0.2, 2.6), (X, -3.1, 1.3), M["concrete"])
    B(kit, "base wall w", (0.2, 6.2, 2.6), (X - 3.1, 0, 1.3), M["concrete"])
    B(kit, "base wall e", (0.2, 6.2, 2.6), (X + 3.1, 0, 1.3), M["concrete"])
    B(kit, "base ceil", (6.4, 6.4, 0.2), (X, 0, 2.7), M["concrete"])
    # shelving along the north wall
    for i in range(4):
        B(kit, f"shelfpost{i}", (0.06, 0.4, 2.2), (X - 2.7 + i * 1.8, 2.7, 1.1), M["shelf"])
    for lv in range(4):
        B(kit, f"shelfboard{lv}", (5.5, 0.4, 0.04), (X, 2.7, 0.3 + lv * 0.6), M["shelf"])
    rnd = random.Random(4)
    for lv in range(4):
        for j in range(5):
            B(kit, f"box{lv}{j}", (0.5, 0.32, 0.3), (X - 2.3 + j * 1.1, 2.7, 0.48 + lv * 0.6), M["crate"], bevel=0.02,
              rot=(0, 0, rnd.uniform(-0.1, 0.1)))
    # crates, and plaster casts under dust sheets
    for (cx, cy, s) in ((X - 2.3, -2.2, 0.9), (X - 1.2, -1.9, 0.55), (X + 2.2, -1.8, 1.0)):
        B(kit, f"crate{cx}", (s, s, s), (cx, cy, s / 2), M["crate"], bevel=0.02, rot=(0, 0, 0.2))
    for (cx, cy, h) in ((X + 2.2, 0.8, 1.3), (X - 2.4, 0.4, 1.0), (X + 0.4, -2.4, 0.8)):
        kit.cyl(f"cast{cx}", 0.4, h, (cx, cy, h / 2), M["sheet"], n=12, r2=0.26)
        kit.sphere(f"casttop{cx}", 0.27, (cx, cy, h), M["sheet"], seg=10)
    # the long crate Abe lies along, and the sheet over him
    B(kit, "long crate", (2.1, 0.9, 0.6), (X, 0.0, 0.3), M["crate"], bevel=0.02)
    kit.sphere("bulb", 0.07, (X, 0, 2.5), M["bulb"], seg=10)
    # a bare dust sheet draped over the long crate's top for Abe to lie under
    ctx["sheet_over"] = B(kit, "abe sheet", (1.55, 0.7, 0.42), (X - 0.2, 0.0, 1.0), kit.emit("#ffd98a", 1.05, "sheet glow"), bevel=0.16)
    ctx["sheet_over"].hide_render = True
    kit.light("base dim", "POINT", (X, 0, 2.3), 6.0, "#7a8aa8", size=0.3)
    kit.light("base lamp", "POINT", (X - 0.4, -1.4, 1.5), 5.0, "#ffd9a0", size=0.3)
    # stairs and the door at x = 140: eight steps going down toward -y
    SX = 140.0
    B(kit, "stair wall w", (0.3, 8, 4.2), (SX - 1.15, -2.0, 1.6), M["concrete"])
    B(kit, "stair wall e", (0.3, 8, 4.2), (SX + 1.15, -2.0, 1.6), M["concrete"])
    B(kit, "stair ceil", (2.6, 9, 0.3), (SX, -2.0, 3.0), M["concrete"])
    for i in range(8):
        h = 1.6 - 0.2 * (i + 1)
        B(kit, f"step{i}", (2.0, 0.5, max(0.05, 1.6 - 0.2 * i)), (SX, 0.4 - i * 0.5, max(0.05, 1.6 - 0.2 * i) / 2), M["concrete"])
    B(kit, "stair back", (2.6, 0.3, 4.2), (SX, -4.35, 1.6), M["concrete"])
    B(kit, "base door", (1.0, 0.06, 2.0), (SX, -4.15, 1.04), M["wood"], bevel=0.01)
    B(kit, "base door frame", (1.2, 0.1, 0.12), (SX, -4.15, 2.08), M["shelf"])
    B(kit, "door gap glow", (0.92, 0.1, 0.04), (SX, -4.1, 0.025), kit.emit(GOLD, 2.2, "door leak"))
    kit.light("stair lamp", "POINT", (SX, -0.5, 2.6), 22.0, "#9fb0d0", size=0.3)
    kit.light("door leak", "POINT", (SX, -3.8, 0.1), 9.0, GOLD, size=0.2)


# ------------------------------------------------------------------------------------------------ the Stooped
def stooped_face(path_face, path_mask):
    """Its own drawn face on the head texture: two small round white eyes a little too far apart in dark hollows, pin
    pupils, no brows, a short straight mouth. The mask marks the eyes (they are the one thing that is lightly self-lit)."""
    W, H = faces.TEX_W, faces.TEX_H
    skin = (46, 40, 36)
    im = Image.new("RGB", (W, H), skin)
    mk = Image.new("L", (W, H), 0)
    d, dm = ImageDraw.Draw(im), ImageDraw.Draw(mk)
    s = faces.FX1 - faces.FX0
    cx, ey = faces._fx(0.5), faces._fy(0.40)
    ink = (20, 14, 12)
    for side in (-1, 1):
        x = cx + side * 0.33 * s
        hx, hy = 0.17 * s, 0.2 * s
        d.ellipse([x - hx, ey - hy * 0.9, x + hx, ey + hy * 1.15], fill=(14, 10, 8))
        r = 0.03 * s
        d.ellipse([x - r, ey - r, x + r, ey + r], fill=(226, 222, 206), outline=ink, width=int(0.012 * s))
        dm.ellipse([x - r, ey - r, x + r, ey + r], fill=255)
        pr = 0.009 * s
        d.ellipse([x - pr, ey - pr, x + pr, ey + pr], fill=(6, 5, 5))
    for side in (-1, 1):
        d.ellipse([cx + side * 0.45 * s - 0.12 * s, faces._fy(0.62) - 0.12 * s, cx + side * 0.45 * s + 0.12 * s, faces._fy(0.62) + 0.12 * s], fill=(38, 32, 28))
    my = faces._fy(0.78)
    rnd = random.Random(7)
    # a wide, tall, dark ragged gape (never a round O): torn edges and a few long uneven teeth
    top = [(cx - 0.42 * s, my - 0.02 * s)]
    bot = [(cx - 0.42 * s, my - 0.02 * s)]
    for k in range(-5, 6):
        top.append((cx + k * 0.075 * s, my - (0.07 + 0.05 * rnd.random()) * s))
        bot.append((cx + k * 0.075 * s, my + (0.1 + 0.08 * rnd.random()) * s))
    top.append((cx + 0.42 * s, my - 0.02 * s))
    bot.append((cx + 0.42 * s, my - 0.02 * s))
    d.polygon(top + bot[::-1], fill=(4, 2, 2))
    for k in range(-4, 5):
        if rnd.random() < 0.7:
            x0 = cx + (k + rnd.uniform(-0.2, 0.2)) * 0.085 * s
            ln = rnd.uniform(0.05, 0.11) * s
            d.polygon([(x0 - 0.016 * s, my - 0.06 * s), (x0 + 0.016 * s, my - 0.06 * s), (x0, my - 0.06 * s + ln)], fill=(150, 140, 118))
        if rnd.random() < 0.5:
            x0 = cx + (k + rnd.uniform(-0.2, 0.2)) * 0.085 * s
            ln = rnd.uniform(0.04, 0.09) * s
            d.polygon([(x0 - 0.016 * s, my + 0.1 * s), (x0 + 0.016 * s, my + 0.1 * s), (x0, my + 0.1 * s - ln)], fill=(140, 130, 110))
    im.save(path_face)
    mk.save(path_mask)


def build_stooped(kit, M, ctx):
    """Tall and folded: very long legs put the hips and the level back at 2.6 to 2.9 m, over the cast's heads; the long
    neck and head hang from the front of the back, the long arms hang with hands. Root = the floor between the feet."""
    root = kit.empty("stooped", (0, 0, -40))
    HZ = 2.74                                   # centre height of the back
    B(kit, "st torso", (0.6, 1.3, 0.34), (0, -0.45, HZ), M["coat"], root, bevel=0.04)
    B(kit, "st yoke", (0.96, 0.34, 0.4), (0, -1.08, HZ - 0.01), M["coat"], root, bevel=0.06)
    B(kit, "st coat tail", (0.54, 0.06, 0.9), (0, 0.22, HZ - 0.5), M["coat"], root, bevel=0.02)
    B(kit, "st collar", (0.3, 0.2, 0.2), (0, -1.17, HZ - 0.08), M["coat"], root, bevel=0.04)
    for s in (-1, 1):
        B(kit, f"st thigh{s}", (0.24, 0.26, 1.4), (s * 0.15, -0.03, 1.95), M["trou"], root, bevel=0.03)
        B(kit, f"st knee{s}", (0.2, 0.2, 0.2), (s * 0.15, 0.0, 1.22), M["trou"], root, bevel=0.03)
        B(kit, f"st shin{s}", (0.2, 0.2, 1.2), (s * 0.15, 0.03, 0.62), M["trou"], root, bevel=0.03)
        B(kit, f"st shoe{s}", (0.28, 0.5, 0.12), (s * 0.15, -0.08, 0.06), M["shoe"], root, bevel=0.04)
        B(kit, f"st sleeve{s}", (0.2, 0.2, 1.05), (s * 0.5, -1.08, HZ - 0.55), M["coat"], root, bevel=0.03)
        B(kit, f"st forearm{s}", (0.14, 0.14, 0.95), (s * 0.5, -1.08, 1.12), M["hand"], root, bevel=0.03)
        B(kit, f"st cuff{s}", (0.22, 0.22, 0.05), (s * 0.5, -1.08, 1.67), M["brass"], root)
        B(kit, f"st hand{s}", (0.17, 0.1, 0.2), (s * 0.5, -1.08, 0.55), M["hand"], root, bevel=0.03)
        for fx in (-0.06, -0.02, 0.02, 0.06):
            B(kit, f"st finger{s}{fx}", (0.026, 0.03, 0.26), (s * 0.5 + fx, -1.08, 0.33), M["hand"], root, bevel=0.01)
    # brass buttons down the hanging front (the underside of the folded body), a brass badge at the collar
    for i in range(4):
        kit.cyl(f"st button{i}", 0.04, 0.03, (0, -0.18 - i * 0.24, HZ - 0.17), M["brass"], root, n=14)
    B(kit, "st pin", (0.08, 0.08, 0.02), (0.13, -0.95, HZ - 0.17), M["brass"], root)
    # the neck hangs from the front of the back and swings; drop is its length; the head hangs from it
    neck = kit.empty("st neck", (0, -1.2, HZ - 0.04), root)
    nb = B(kit, "st neck box", (0.17, 0.17, 1.0), (0, 0, -0.5), M["skin"], neck, bevel=0.03)
    nb.location = (0, 0, 0)
    nb.parent = neck
    headr = kit.empty("st headroll", (0, 0, -1.0), neck)
    path = bpy.app.tempdir or "/tmp/"
    pf, pm = path + "stooped-face.png", path + "stooped-mask.png"
    stooped_face(pf, pm)
    m = kit._new("stooped head")
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.8
    tex = N.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(pf)
    tex.image.colorspace_settings.name = "sRGB"
    mk = N.new("ShaderNodeTexImage")
    mk.image = bpy.data.images.load(pm)
    mk.image.colorspace_settings.name = "Non-Color"
    uvn = N.new("ShaderNodeUVMap")
    L.new(uvn.outputs["UV"], tex.inputs["Vector"])
    L.new(uvn.outputs["UV"], mk.inputs["Vector"])
    L.new(tex.outputs["Color"], b.inputs["Base Color"])
    L.new(tex.outputs["Color"], b.inputs["Emission Color"])
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 0.9
    L.new(mk.outputs["Color"], mul.inputs[0])
    L.new(mul.outputs[0], b.inputs["Emission Strength"])
    kit._fogged(m, b.outputs[0])
    # the head mesh is in rig units (radius 0.62): scale it to metres. headr sits at the head's centre, so a roll turns it in place
    hm = rig.head_mesh("st head", m, headr)
    hm.scale = (U * 0.85, U * 0.8, U * 1.4)      # long and gaunt
    # heavy brow, long nose and a jutting jaw, in the head's own space (front is -y)
    B(kit, "st nose", (0.05, 0.06, 0.12), (0, -0.2, -0.05), M["skin"], headr, bevel=0.015)
    ctx["stooped"] = dict(root=root, neck=neck, headr=headr, nb=nb)


def set_stooped(ctx, c):
    s = ctx["stooped"]
    root = s["root"]
    hidden = c is None or c.get("hidden")
    _show([root], not hidden)
    if hidden:
        return
    px, py = c["pos"]
    root.location = (px, py, 0)
    root.rotation_euler = (0, 0, math.radians(c.get("yaw", 180)))
    drop = c.get("drop", 1.3)                   # neck length: ~1.3 hangs the face at seated face height
    s["nb"].scale = (1, 1, drop)
    s["nb"].location = (0, 0, -drop / 2)
    s["headr"].location = (0, 0, -drop - 0.2)
    s["neck"].rotation_euler = (math.radians(c.get("neck", 0)), 0, math.radians(c.get("lean", 0)))
    # the head: roll 180 is face upside down (hanging); 0 is the right way up. pitch tips the face up toward a face
    s["headr"].rotation_euler = (math.radians(c.get("pitch", 0)), math.radians(c.get("roll", 180)),
                                 math.radians(c.get("hyaw", 0)))


# ------------------------------------------------------------------------------------------------ the glow
def part_specs(who):
    """(object name, size, centre, shape) of each body part to wrap, in the part's own space (rig units)."""
    out = [(f"{who}.torso", (2.0, 1.0, 2.0), (0, 0, 1.0), "box")]
    for sx in (-1, 1):
        out.append((f"{who}.arm{sx}", (0.98, 1.0, 2.0), (0, 0, -0.75), "box"))
        out.append((f"{who}.leg{sx}", (1.0, 1.0, 2.0), (0, 0, -1.0), "box"))
    out.append((f"{who}.headg", (1.24, 1.24, 1.2), (0, 0, 0), "cyl"))
    return out


def glow_material(kit, who, ring, share):
    name = f"glow {who} {ring}"
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    geo = N.new("ShaderNodeNewGeometry")
    on = N.new("ShaderNodeValue")
    on.outputs[0].default_value = 1.0
    f = N.new("ShaderNodeMath")
    f.operation = "MULTIPLY"
    L.new(geo.outputs["Backfacing"], f.inputs[0])
    L.new(on.outputs[0], f.inputs[1])
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col(GLOW_GOLD)
    em.inputs["Strength"].default_value = 0.0
    tr = N.new("ShaderNodeBsdfTransparent")
    mix = N.new("ShaderNodeMixShader")
    L.new(f.outputs[0], mix.inputs[0])
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(em.outputs[0], mix.inputs[2])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    L.new(mix.outputs[0], out.inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    return m, em, on


def make_glow(kit, ctx, who):
    shells = []
    mats = []
    for ring, (grow, share) in enumerate(SHELLS):
        m, em, on = glow_material(kit, who, ring, share)
        mats.append((em, on, share))
        for name, size, centre, shape in part_specs(who):
            par = bpy.data.objects.get(name)
            if par is None:
                continue
            if shape == "cyl":
                ob = kit.cyl(f"{name}.gl{ring}", 0.62 + grow, 1.2 + 2 * grow, centre, m, par, n=24)
            else:
                ob = kit.box(f"{name}.gl{ring}", (size[0] + 2 * grow, size[1] + 2 * grow, size[2] + 2 * grow), centre, m, par,
                             bevel=0.07 + grow * 0.3)
            for attr in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
                if hasattr(ob, attr):
                    setattr(ob, attr, False)
            shells.append(ob)
    ctx["glow"][who] = dict(shells=shells, mats=mats)


COSTUME_DONE = {"v": False}


def decorate(kit, story, ctx):
    """After the cast exists: costume pieces on top of the rig's, the glow shells, the glow lights."""
    M = ctx["M"]
    ab = bpy.data.objects.get("abe.torso")
    if ab is not None:
        B(kit, "abe vest", (2.06, 1.06, 1.7), (0, 0, 0.98), M["vestgreen"], ab, bevel=0.06)
        B(kit, "abe pin", (0.16, 0.04, 0.16), (0.55, -0.55, 1.5), M["brass"], ab)
        hg = bpy.data.objects.get("abe.headg")
        B(kit, "abe moustache", (0.64, 0.08, 0.1), (0, -faces.HEAD_R - 0.02, -0.15), M["white"], hg, bevel=0.03)
        for sx in (-1, 1):
            B(kit, f"abe must{sx}", (0.12, 0.08, 0.22), (sx * 0.3, -faces.HEAD_R - 0.01, -0.22), M["white"], hg, bevel=0.03)
    me = bpy.data.objects.get("me.torso")
    if me is not None:
        B(kit, "me stripes", (0.9, 0.04, 1.5), (0, -0.52, 0.95), M["mestripe"], me)
    cu = bpy.data.objects.get("curator.torso")
    if cu is not None:
        B(kit, "cur blouse", (0.8, 0.04, 1.2), (0, -0.52, 1.15), M["white"], cu)
        B(kit, "cur badge", (0.3, 0.04, 0.3), (0.4, -0.55, 0.8), M["brass"], cu)
        B(kit, "cur lanyard", (0.06, 0.03, 1.2), (0.28, -0.53, 1.35), M["brass"], cu)
    hg = bpy.data.objects.get("curator.headg")
    if hg is not None:
        # a grey bob: the rig's "long" hair is the bob already
        pass
    for who in list(story["cast"]):
        if story.get("glow", {}).get(who, 0) > 0 or who in story.get("glow_later", []):
            make_glow(kit, ctx, who)
    # a point light that follows each bright character
    ctx["inited"] = True


def lens_hide():
    for nm in ("abe.gl-1", "abe.gl1"):   # the rig's glasses lenses render black: keep the frames
        ob = bpy.data.objects.get(nm)
        if ob is not None:
            ob.hide_render = True


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    M = materials(kit)
    M["vestgreen"] = pbr(kit, "vest", "#1f4a38", 0.7, noise=(6, 0.85))
    M["white"] = pbr(kit, "white hair", "#d9d5c8", 0.8)
    M["mestripe"] = rig.cloth({"shirt": "#1d2c4a", "pattern": "stripes", "pattern_c": "#efe8d6"}, "shirt")
    ctx = {"M": M, "glow": {}, "inited": False}
    sc = bpy.context.scene
    sc.cycles.transparent_max_bounces = 40
    build_hall(kit, M, ctx)
    build_skeleton(kit, M, ctx)
    build_bench(kit, M, ctx)
    build_gallery(kit, M, ctx)
    build_basement(kit, M, ctx)
    build_stooped(kit, M, ctx)
    build_props(kit, M, ctx)
    build_montage(kit, M, ctx)
    # lights that move with the story
    sun = kit.light("sun", "SUN", (30, -20, 40), 1.0, "#fff0d8", size=0.02)
    kit.aim(sun, (0, 0, 0))
    ctx["sun"] = sun
    for who in story.get("glow_lights", []):
        kit.light(f"gl {who}", "POINT", (0, 0, -50), 1.0, GOLD, size=0.3)
    ctx["focus"] = bpy.data.objects.new("focus", None)
    kit.link(ctx["focus"])
    return ctx


def build_props(kit, M, ctx):
    # the torch: a short cylinder lying on its side with a lens at one end and a soft spot light along it
    t = kit.empty("torch", (0, 0, -40))
    kit.cyl("torch body", 0.035, 0.22, (0, 0, 0.035), M["torch"], t, rot=(0, math.pi / 2, 0), n=12)
    kit.cyl("torch head", 0.05, 0.07, (0.12, 0, 0.035), M["iron"], t, rot=(0, math.pi / 2, 0), n=12)
    kit.cyl("torch lens", 0.045, 0.012, (0.157, 0, 0.035), M["lens"], t, rot=(0, math.pi / 2, 0), n=12)
    ls = kit.light("torch beam", "SPOT", (0.16, 0, 0.05), 1.0, "#ffd9a0", rot=(0, -math.pi / 2 + 0.07, 0), size=0.04,
                   spot=70, blend=0.9, parent=t)
    ctx["torch"] = t
    # sparks: small soft gold motes that drift up over the crowd and go out
    ctx["sparks"] = []
    for i in range(16):
        sp = kit.sphere(f"spark{i}", 0.11, (0, 0, -50), M["spark"], seg=8)
        sp.visible_shadow = False
        ctx["sparks"].append(sp)
    ctx["spark1"] = kit.sphere("spark one", 0.06, (0, 0, -50), M["spark"], seg=8)


# ------------------------------------------------------------------------------------------------ animate
def animate(kit, story, tl, t, ctx):
    bpy.context.view_layer.update()
    if not ctx["inited"]:
        decorate(kit, story, ctx)
    lens_hide()
    M = ctx["M"]
    over = {}
    # ---- people sitting: both legs forward (acting.py ignores the key)
    for who, keys in tl["acting"].items():
        on = False
        for k in keys:
            if k["t"] <= t + 1e-9 and "sit" in k:
                on = bool(k["sit"])
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg is not None and on:
                leg.rotation_euler = (-math.pi / 2, 0, 0)
    # ---- the hall's lamps: a level that ramps (never a step)
    lv = _eased(_cues(tl, "hall"), "level", t, 1.0)
    for i in range(4):
        over[f"hall{i}"] = lv
    over["hall blue"] = 0.4 + 0.6 * (1.0 - lv)
    over["gal moon"] = _eased(_cues(tl, "gal"), "level", t, 1.0)
    over["tail gold"] = _eased(_cues(tl, "tailgold"), "on", t, 0.0)
    ctx["sheet_over"].hide_render = not bool((_last(_cues(tl, "sheet"), t) or {}).get("on"))
    M["lamp"].node_tree.nodes["Emission"].inputs["Strength"].default_value = 6.0 * max(0.04, lv)
    # ---- the sun, and the sky
    sc = _last(_cues(tl, "sun"), t) or {"set": "off"}
    SUNS = {"off": (0.0, "#fff0d8", (30, -20, 40)), "day": (3.2, "#fff0d8", (20, -25, 38)),
            "dusk": (2.4, "#ff9a5e", (40, -10, 12)), "steps": (3.4, "#fff2dc", (16, -34, 36))}
    en, colr, pos = SUNS[sc["set"]]
    ctx["sun"].data.energy = en
    ctx["sun"].data.color = _lin(_rgb(colr))
    ctx["sun"].location = pos
    kit.aim(ctx["sun"], (0, 0, 0))
    sky = _last(_cues(tl, "sky"), t) or {"color": "#1a1c24", "strength": 0.2}
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*_lin(_rgb(sky["color"])), 1)
    bg.inputs["Strength"].default_value = sky.get("strength", 1.0)
    # ---- stripes (the wiped line): shown means the film's gap is open
    show = bool((_last(_cues(tl, "stripes"), t) or {}).get("on", False))
    for ob in ctx["stripes"]:
        ob.hide_render = show
    # ---- the skeleton's head
    hy = _eased(_cues(tl, "skull"), "yaw", t, 0.0)
    ctx["skel_head"].rotation_euler = (0, 0, math.radians(hy))
    # ---- the Stooped: never seen moving, so a pose is a switch at a cut
    sc_ = _last(_cues(tl, "stooped"), t)
    set_stooped(ctx, sc_)
    over["stooped rim"] = 0.0 if (sc_ is None or sc_.get("hidden")) else 1.0
    rimo = kit.LIGHTS["stooped rim"]["obj"]
    if sc_ is not None and not sc_.get("hidden") and sc_["pos"][0] < -5:
        px_, py_ = sc_["pos"]
        rimo.location = (px_ + 5.0, py_ - 2.5, 3.2)
        kit.aim(rimo, (px_, py_ - 0.4, 1.2))
    else:
        rimo.location = (-1.0, -8.2, 3.0)
        kit.aim(rimo, (-1.0, -3.9, 1.2))
    over["tally lamp"] = _eased(_cues(tl, "tally"), "on", t, 0.0)
    # ---- the torch rolling in slow circles by the skeleton's feet
    tg = _eased(_cues(tl, "torch"), "on", t, 0.0)
    tor = ctx["torch"]
    if tg > 0.001:
        a = t * 2 * math.pi / 3.0
        tor.location = (-0.3 + 0.28 * math.cos(a), -0.2 + 0.28 * math.sin(a), 0)
        tor.rotation_euler = (0, 0, a + math.pi / 2)
        over["torch beam"] = 70.0 * tg
        kit.LIGHTS["torch beam"]["base"] = 1.0
    else:
        tor.location = (0, 0, -40)
        over["torch beam"] = 0.0
    # ---- the glow: shells and lights, per character, always ramped
    gcues = _cues(tl, "glow")
    for who, g in ctx["glow"].items():
        root = bpy.data.objects.get(who)
        vis = root is not None and not root.hide_render
        s = _eased([c for c in gcues if _who(c, who)], "s", t, float(story.get("glow", {}).get(who, 0)))
        on = vis and s > 0.02
        for ob in g["shells"]:
            ob.hide_render = not on
        for em, onn, share in g["mats"]:
            em.inputs["Strength"].default_value = GLOW_UNIT * (min(s, 6.0) ** 0.7) * share
            onn.outputs[0].default_value = 1.0 if on else 0.0
    for who in story.get("glow_lights", []):
        L = kit.LIGHTS[f"gl {who}"]
        torso = bpy.data.objects.get(f"{who}.torso")
        root = bpy.data.objects.get(who)
        s = _eased([c for c in gcues if _who(c, who)], "s", t, float(story.get("glow", {}).get(who, 0)))
        if torso is None or root is None or root.hide_render or s <= 0.02:
            L["obj"].location = (0, 0, -50)
            over[f"gl {who}"] = 0.0
            continue
        p = torso.matrix_world @ V((0, -5.0, 1.6 if who == "abe" else 1.0))
        L["obj"].location = (p.x, p.y, p.z + 0.1)
        L["base"] = story.get("glow_light_w", 90.0)
        over[f"gl {who}"] = s / 3.0 * _eased(_cues(tl, "glk"), "level", t, 1.0)
    # ---- sparks
    sk = _last(_cues(tl, "sparks"), t)
    for i, sp in enumerate(ctx["sparks"]):
        if sk is None or t - sk["t"] > 4.0:
            sp.location = (0, 0, -50)
            continue
        rnd = random.Random(i * 31 + 7)
        d = i * 0.13
        u = (t - sk["t"] - d) / 1.5
        if u < 0 or u > 1:
            sp.location = (0, 0, -50)
            continue
        cx, cy = sk.get("center", [0, -3])
        x, y = cx + rnd.uniform(-3.5, 3.5), cy + rnd.uniform(-1.5, 2.5)
        sp.location = (x + 0.3 * math.sin(u * 5 + i), y, 1.7 + 1.2 * u)
        k = max(0.01, math.sin(math.pi * min(1.0, u)))
        sp.scale = (k, k, k)
    s1 = _last(_cues(tl, "spark1"), t)
    sp1 = ctx["spark1"]
    if s1 and 0 <= t - s1["t"] <= 0.8:
        u = (t - s1["t"]) / 0.8
        a, b = s1["a"], s1["b"]
        sp1.location = (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u + 0.15 * math.sin(math.pi * u))
        k = 0.6 + 0.4 * math.sin(math.pi * u)
        sp1.scale = (k, k, k)
    else:
        sp1.location = (0, 0, -50)
    # ---- a soft depth of field for the glimpses
    cam = bpy.data.objects["cam"].data
    d = _last(_cues(tl, "dof"), t)
    if d and d.get("on"):
        cam.dof.use_dof = True
        ctx["focus"].location = d["focus"]
        cam.dof.focus_object = ctx["focus"]
        cam.dof.aperture_fstop = d.get("f", 1.6)
    else:
        cam.dof.use_dof = False
    return over


# ------------------------------------------------------------------------------------------------ the montage sets
def room(kit, M, name, x, y, w, d, h, wall, floor, ceil=True):
    """A closed room centred on (x, y): floor, four walls (inner faces at +-w/2, +-d/2), ceiling."""
    kit.plane(f"{name} floor", (w, d), (x, y, 0), floor)
    B(kit, f"{name} wall n", (w + 0.4, 0.2, h), (x, y + d / 2 + 0.1, h / 2), wall)
    B(kit, f"{name} wall s", (w + 0.4, 0.2, h), (x, y - d / 2 - 0.1, h / 2), wall)
    B(kit, f"{name} wall e", (0.2, d + 0.4, h), (x + w / 2 + 0.1, y, h / 2), wall)
    B(kit, f"{name} wall w", (0.2, d + 0.4, h), (x - w / 2 - 0.1, y, h / 2), wall)
    if ceil:
        B(kit, f"{name} ceil", (w + 0.4, d + 0.4, 0.2), (x, y, h + 0.1), M["ceil"])


def park_bench(kit, M, name, x, y):
    B(kit, f"{name} seat", (1.9, 0.5, 0.07), (x, y, 0.43), M["bench"], bevel=0.02)
    B(kit, f"{name} back", (1.9, 0.06, 0.42), (x, y + 0.24, 0.75), M["bench"], bevel=0.02)
    for s in (-1, 1):
        B(kit, f"{name} leg{s}", (0.06, 0.46, 0.43), (x + s * 0.85, y, 0.215), M["iron"], bevel=0.01)


def build_montage(kit, M, ctx):
    # 1 living room (x 180): a sofa, a rug, a window, a lamp
    X = 180.0
    room(kit, M, "lv", X, 0, 8, 6, 2.7, M["wall"], M["floor_wood"])
    B(kit, "lv sofa seat", (3.0, 0.9, 0.45), (X, 0.85, 0.225), M["sofa"], bevel=0.06)
    B(kit, "lv sofa back", (3.0, 0.28, 0.95), (X, 1.4, 0.48), M["sofa"], bevel=0.06)
    for s in (-1, 1):
        B(kit, f"lv sofa arm{s}", (0.28, 1.1, 0.7), (X + s * 1.6, 0.9, 0.35), M["sofa"], bevel=0.06)
    B(kit, "lv rug", (3.2, 2.0, 0.02), (X, -1.0, 0.012), M["felt2"])
    B(kit, "lv window", (0.04, 1.8, 1.3), (X + 3.96, 0.0, 1.5), M["window"])
    B(kit, "lv shelf", (1.6, 0.35, 1.4), (X - 3.0, 2.75, 0.7), M["wood"], bevel=0.02)
    kit.light("lv lamp", "POINT", (X - 1.0, -0.5, 2.2), 70.0, "#ffd9a8", size=0.3)
    kit.light("lv fill", "AREA", (X, 0, 2.55), 120.0, "#a8b4d8", size=3.0)
    # 2 doorstep at dusk (x 220): a brick house front, a door, a step, a path
    X = 220.0
    kit.plane("ds ground", (40, 30), (X, -8, 0), M["grass"])
    kit.plane("ds path", (1.6, 7), (X, 0.0, 0.01), M["pave"])
    B(kit, "ds house", (10, 0.4, 3.6), (X, 3.4, 1.8), M["brick"])
    B(kit, "ds door", (1.0, 0.1, 2.1), (X, 3.15, 1.05), M["door"], bevel=0.02)
    B(kit, "ds step", (1.8, 0.9, 0.18), (X, 2.65, 0.09), M["sandstone"], bevel=0.02)
    B(kit, "ds frame", (1.3, 0.12, 0.14), (X, 3.15, 2.15), M["wood"])
    for sx in (-3, 3):
        B(kit, f"ds window{sx}", (1.2, 0.05, 1.1), (X + sx, 3.19, 1.6), kit.emit("#ffcf8a", 1.2, "dusk window"))
    # 3 park bench in the sun (x 260)
    X = 260.0
    kit.plane("pk ground", (60, 40), (X, 0, 0), M["grass"])
    park_bench(kit, M, "pk bench", X, 0)
    for (tx, ty) in ((X + 4.0, 3.5), (X - 4.5, 4.5), (X + 7.0, 7.0)):
        B(kit, f"pk trunk{tx}", (0.5, 0.5, 3.0), (tx, ty, 1.5), M["trunk"], bevel=0.05)
        B(kit, f"pk leaves{tx}", (3.2, 3.2, 2.4), (tx, ty, 4.1), M["leaf"], bevel=0.3)
        B(kit, f"pk leaves2{tx}", (2.2, 2.2, 1.6), (tx + 0.3, ty, 5.5), M["leaf"], bevel=0.25)
    B(kit, "pk path", (2.0, 30, 0.02), (X + 1.0, 8, 0.01), M["pave"])
    # 4 restaurant (x 300)
    X = 300.0
    room(kit, M, "rs", X, 0, 8, 7, 3.0, M["brick"], M["floor_wood"])
    kit.cyl("rs table top", 0.62, 0.05, (X, 0.0, 0.76), M["cloth"], n=24)
    kit.cyl("rs table cloth", 0.6, 0.55, (X, 0.0, 0.5), M["cloth"], n=24, r2=0.66)
    for k, (cxx, cyy) in enumerate(((-0.12, 0.0), (0.12, 0.0))):
        kit.cyl(f"rs candle{k}", 0.025, 0.2, (X + cxx, cyy, 0.88), M["candle"], n=10)
        kit.sphere(f"rs flame{k}", 0.022, (X + cxx, cyy, 1.0), M["flame"], seg=8)
    for s in (-1, 1):
        B(kit, f"rs chair{s}", (0.5, 0.5, 0.06), (X + s * 1.15, 0, 0.44), M["wood"], bevel=0.02)
        B(kit, f"rs chair back{s}", (0.06, 0.5, 0.55), (X + s * 1.4, 0, 0.72), M["wood"], bevel=0.02)
        for dx in (-0.2, 0.2):
            for dy in (-0.2, 0.2):
                B(kit, f"rs cleg{s}{dx}{dy}", (0.05, 0.05, 0.42), (X + s * 1.15 + dx, dy, 0.21), M["wood"])
    for k, tx in enumerate((-2.6, 2.6)):
        kit.cyl(f"rs t2 {k}", 0.5, 0.05, (X + tx, 2.4, 0.76), M["cloth"], n=20)
        kit.cyl(f"rs t2c {k}", 0.45, 0.7, (X + tx, 2.4, 0.4), M["cloth"], n=20, r2=0.52)
    kit.light("rs warm", "POINT", (X, 0.0, 1.7), 90.0, "#ffc890", size=0.3)
    kit.light("rs candles", "POINT", (X, 0.0, 1.05), 8.0, "#ffb060", size=0.08)
    kit.light("rs fill", "AREA", (X, 0, 2.9), 80.0, "#d8c0a0", size=4.0)
    # 5 the museum steps in the sun (x 340)
    X = 340.0
    kit.plane("st ground", (60, 40), (X, -2, 0), M["pave"])
    for k in range(5):
        B(kit, f"st step{k}", (12, 0.55, 0.17 * (k + 1)), (X, 2.9 + 0.55 * k + 0.27, 0.085 * (k + 1)), M["sandstone"], bevel=0.015)
    B(kit, "st facade", (16, 0.8, 7.5), (X, 6.2, 3.75), M["sandstone"], bevel=0.02)
    B(kit, "st door", (2.4, 0.2, 3.4), (X, 5.75, 0.85 + 1.7), M["door"], bevel=0.02)
    for sx in (-4.4, 4.4):
        kit.cyl(f"st col{sx}", 0.5, 5.4, (X + sx, 5.0, 3.4), M["sandstone"], n=20)
        B(kit, f"st capital{sx}", (1.3, 1.3, 0.3), (X + sx, 5.0, 6.15), M["sandstone"], bevel=0.04)
    B(kit, "st lintel", (11, 1.4, 0.8), (X, 5.0, 6.5), M["sandstone"], bevel=0.03)
    # the museum's sign: a carved curling fern, in relief on the lintel
    for k in range(14):
        a = k * 0.55
        r = 0.08 + 0.055 * k
        B(kit, f"st fern{k}", (0.18, 0.05, 0.18), (X + r * math.cos(a) * 1.0, 4.28, 6.5 + r * math.sin(a) * 0.75), M["fern_rel"],
          rot=(0, a, 0), bevel=0.02)
    # 6 the street at dusk (x 380)
    X = 380.0
    kit.plane("sr ground", (60, 40), (X, 0, 0), M["pave"])
    kit.plane("sr road", (60, 5.4), (X, 0, 0.012), M["road"])
    for k, hx in enumerate((-9, -3, 3, 9)):
        for sy in (-1, 1):
            B(kit, f"sr house{k}{sy}", (5.2, 0.6, 5.0 + (k % 2)), (X + hx, sy * 7.6, 2.5), M["brick"])
            B(kit, f"sr door{k}{sy}", (0.9, 0.08, 2.0), (X + hx - 1.2, sy * 7.28, 1.0), M["door"])
            B(kit, f"sr win{k}{sy}", (1.1, 0.06, 1.1), (X + hx + 1.1, sy * 7.28, 1.8), kit.emit("#ffcf8a", 1.2, "dusk window"))
    for hx in (-6, 6):
        kit.cyl(f"sr lamp{hx}", 0.05, 3.6, (X + hx, 3.6, 1.8), M["iron"], n=8)
        kit.sphere(f"sr lamphead{hx}", 0.16, (X + hx, 3.6, 3.7), kit.emit("#ffd9a0", 2.5, "street lamp"), seg=10)
    # 7 the bedroom (x 420): a bed, a window, night
    X = 420.0
    room(kit, M, "bd", X, 0, 4.6, 4.2, 2.6, M["wall"], M["floor_wood"])
    B(kit, "bd bedframe", (1.3, 2.2, 0.32), (X, 0.3, 0.16), M["wood"], bevel=0.02)
    B(kit, "bd mattress", (1.2, 2.1, 0.2), (X, 0.3, 0.42), M["bed"], bevel=0.05)
    B(kit, "bd pillow", (0.7, 0.4, 0.14), (X, -0.55, 0.59), M["pillow"], bevel=0.06)
    B(kit, "bd window", (0.04, 1.2, 1.0), (X + 2.28, 0.0, 1.6), kit.emit("#7f94c8", 0.8, "night window"))
    kit.light("bd moon", "AREA", (X + 1.5, 0, 2.4), 60.0, "#7f94c8", size=2.0)
    B(kit, "bd towel", (0.5, 0.5, 0.05), (X, -0.54, 0.93), M["towel"], bevel=0.01)
