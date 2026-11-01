"""The shared Blender kit for blocky stories: materials, blocks, lights and game-engine fog. Runs in Blender's
Python (the bpy venv). Every story's own `stories/<name>/set.py` builds its world from these parts, and
`rig.py` builds the characters from them.

Fog is done the way game engines do it, in the surface shader: every material mixes toward the fog colour
with distance from the camera (1 - exp(-density * (d - start))), and the world is the fog colour. It costs
nothing next to a volume, and it gives the hazy, fading-out game-world look the reference shorts have.
"""

from __future__ import annotations

import math

import bpy
from mathutils import Vector

COL = {"c": None}
MATS: dict = {}
OBJ: dict = {}           # named things the animation moves
FOG = {"color": (0.02, 0.022, 0.03), "density": 0.0, "start": 0.0}
LIGHTS: dict = {}        # name -> {"light": data, "base": strength, "flicker": {...}}


def srgb(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def col(h: str, a: float = 1.0) -> tuple:
    h = h.lstrip("#")
    return (srgb(int(h[0:2], 16) / 255), srgb(int(h[2:4], 16) / 255), srgb(int(h[4:6], 16) / 255), a)


def link(ob, parent=None):
    (COL["c"] or bpy.context.scene.collection).objects.link(ob)
    if parent is not None:
        ob.parent = parent
    return ob


def empty(name, loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    ob = bpy.data.objects.new(name, None)
    ob.location = loc
    ob.rotation_euler = rot
    return link(ob, parent)


def mesh_obj(name, verts, faces, mat=None, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    if mat is not None:
        ob.data.materials.append(mat)
    return link(ob, parent)


def box_verts(sx, sy, sz, c=(0, 0, 0)):
    x, y, z = sx / 2, sy / 2, sz / 2
    v = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z), (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    return [(a + c[0], b + c[1], d + c[2]) for a, b, d in v]


BOX_FACES = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]


def box(name, size, loc=(0, 0, 0), mat=None, parent=None, rot=(0, 0, 0), bevel=0.0, seg=2):
    """A box centred on loc. A bevel gives the soft plastic edge every part in these games has."""
    ob = mesh_obj(name, box_verts(*size), BOX_FACES, mat, parent, loc, rot)
    if bevel > 0:
        m = ob.modifiers.new("bevel", "BEVEL")
        m.width = min(bevel, min(size) * 0.45)
        m.segments = seg
        m.limit_method = "NONE"
        for p in ob.data.polygons:
            p.use_smooth = True
        ob.data.shade_smooth() if hasattr(ob.data, "shade_smooth") else None
        try:
            ob.modifiers.new("wn", "WEIGHTED_NORMAL").keep_sharp = True
        except Exception:
            pass
    return ob


def cyl(name, r, h, loc=(0, 0, 0), mat=None, parent=None, rot=(0, 0, 0), n=20, r2=None):
    r2 = r if r2 is None else r2
    verts, faces = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        verts.append((r * math.cos(a), r * math.sin(a), -h / 2))
    for i in range(n):
        a = 2 * math.pi * i / n
        verts.append((r2 * math.cos(a), r2 * math.sin(a), h / 2))
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    faces.append(tuple(reversed(range(n))))
    faces.append(tuple(range(n, 2 * n)))
    ob = mesh_obj(name, verts, faces, mat, parent, loc, rot)
    for p in ob.data.polygons[:n]:
        p.use_smooth = True
    return ob


def sphere(name, r, loc=(0, 0, 0), mat=None, parent=None, seg=16):
    verts, faces = [], []
    rings = seg // 2
    for i in range(rings + 1):
        th = math.pi * i / rings
        for j in range(seg):
            ph = 2 * math.pi * j / seg
            verts.append((r * math.sin(th) * math.cos(ph), r * math.sin(th) * math.sin(ph), r * math.cos(th)))
    for i in range(rings):
        for j in range(seg):
            a, b = i * seg + j, i * seg + (j + 1) % seg
            faces.append((a, b, b + seg, a + seg))
    return mesh_obj(name, verts, faces, mat, parent, loc, smooth=True)


def plane(name, size, loc=(0, 0, 0), mat=None, parent=None, rot=(0, 0, 0)):
    x, y = size[0] / 2, size[1] / 2
    return mesh_obj(name, [(-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0)], [(0, 1, 2, 3)], mat, parent, loc, rot)


# ------------------------------------------------------------------------------------------ materials


def _new(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    MATS[name] = m
    return m


def _fogged(m, shader_socket):
    """Route a material's shader through the distance fog."""
    nt = m.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    if FOG["density"] <= 0:
        nt.links.new(shader_socket, out.inputs["Surface"])
        return
    cam = nt.nodes.new("ShaderNodeCameraData")
    sub = nt.nodes.new("ShaderNodeMath")
    sub.operation = "SUBTRACT"
    nt.links.new(cam.outputs["View Distance"], sub.inputs[0])
    sub.inputs[1].default_value = FOG["start"]
    mx = nt.nodes.new("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    nt.links.new(sub.outputs[0], mx.inputs[0])
    mx.inputs[1].default_value = 0.0
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    nt.links.new(mx.outputs[0], mul.inputs[0])
    mul.inputs[1].default_value = -FOG["density"]
    ex = nt.nodes.new("ShaderNodeMath")
    ex.operation = "EXPONENT"
    nt.links.new(mul.outputs[0], ex.inputs[0])
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(ex.outputs[0], inv.inputs[1])
    fog = nt.nodes.new("ShaderNodeEmission")
    fog.inputs["Color"].default_value = (*FOG["color"], 1)
    fog.inputs["Strength"].default_value = 1.0
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(inv.outputs[0], mix.inputs[0])
    nt.links.new(shader_socket, mix.inputs[1])
    nt.links.new(fog.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    try:
        m.emission_sampling = "NONE"  # the fog isn't a light source
    except Exception:
        pass


def plastic(hexc, rough=0.45, name=None, spec=0.4):
    """Smooth game plastic: one flat colour, soft highlights. The material every avatar part is made of."""
    name = name or f"plastic {hexc} {rough}"
    if name in MATS:
        return MATS[name]
    m = _new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = col(hexc)
    b.inputs["Roughness"].default_value = rough
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = spec
            break
    m.diffuse_color = col(hexc)
    _fogged(m, b.outputs[0])
    return m


def emit(hexc, strength, name=None):
    name = name or f"emit {hexc} {strength}"
    if name in MATS:
        return MATS[name]
    m = _new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = col(hexc)
    e.inputs["Strength"].default_value = strength
    _fogged(m, e.outputs[0])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    return m


def checker(c1, c2, scale=1.0, name=None, rough=0.6):
    """Two-tone tiles in object space (floor tiles, a baseplate grid), so tiles stay square on any block."""
    name = name or f"checker {c1} {c2} {scale}"
    if name in MATS:
        return MATS[name]
    m = _new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tc = nt.nodes.new("ShaderNodeTexCoord")
    ck = nt.nodes.new("ShaderNodeTexChecker")
    ck.inputs["Scale"].default_value = scale
    ck.inputs["Color1"].default_value = col(c1)
    ck.inputs["Color2"].default_value = col(c2)
    nt.links.new(tc.outputs["Object"], ck.inputs["Vector"])
    nt.links.new(ck.outputs["Color"], b.inputs["Base Color"])
    _fogged(m, b.outputs[0])
    return m


def grime(hexc, dark=0.55, scale=3.0, name=None, rough=0.7):
    """A flat colour with soft, large dirty patches (noise), for walls and floors that have been left alone."""
    name = name or f"grime {hexc} {dark} {scale}"
    if name in MATS:
        return MATS[name]
    m = _new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 3.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    c = col(hexc)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (c[0] * dark, c[1] * dark, c[2] * dark, 1)
    ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[1].color = c
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    _fogged(m, b.outputs[0])
    return m


def glass(tint="#c8d8e0", name=None):
    name = name or f"glass {tint}"
    if name in MATS:
        return MATS[name]
    m = _new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = col(tint)
    b.inputs["Roughness"].default_value = 0.05
    b.inputs["Transmission Weight" if "Transmission Weight" in b.inputs else "Transmission"].default_value = 1.0
    _fogged(m, b.outputs[0])
    return m


# ---------------------------------------------------------------------------------------------- lights


def light(name, kind, loc, energy, hexc="#ffffff", rot=(0, 0, 0), size=0.2, spot=None, blend=0.3,
          flicker=None, parent=None, shadow=True):
    """A light, remembered by name so the story can flicker or switch it. flicker = {"rate": Hz, "depth": 0..1,
    "seed": n, "dropouts": per-second chance of a near-blackout}."""
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = col(hexc)[:3]
    if hasattr(ld, "use_shadow"):
        ld.use_shadow = shadow
    if kind in ("POINT", "SPOT"):
        ld.shadow_soft_size = size
    if kind == "AREA":
        ld.size = size
    if kind == "SPOT":
        ld.spot_size = math.radians(spot or 45)
        ld.spot_blend = blend
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    ob.rotation_euler = rot
    link(ob, parent)
    LIGHTS[name] = {"obj": ob, "light": ld, "base": energy, "flicker": flicker, "on": True}
    return ob


def aim(ob, target):
    d = Vector(target) - ob.matrix_world.translation if ob.parent else Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def noise1(t, seed, freq):
    """Smooth pseudo-random wobble in -1..1."""
    return (math.sin(t * freq + seed) * 0.5 + math.sin(t * freq * 1.73 + seed * 2.1) * 0.3
            + math.sin(t * freq * 2.91 + seed * 0.7) * 0.2)


def hash01(*xs) -> float:
    h = 0
    for x in xs:
        h = (h * 1000003) ^ int(x * 7919 + 17)
        h &= 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0x5BD1E995) & 0xFFFFFFFF
    h ^= h >> 15
    return (h & 0xFFFF) / 65535


def flicker_gain(t, fl) -> float:
    """A failing bulb: a quick shimmer, plus random dropouts that last a frame or three."""
    if not fl:
        return 1.0
    g = 1.0 - fl.get("depth", 0.2) * (0.5 + 0.5 * noise1(t, fl.get("seed", 1), fl.get("rate", 9.0)))
    drop = fl.get("dropouts", 0.0)
    if drop:
        slot = math.floor(t * 10)
        if hash01(slot, fl.get("seed", 1)) < drop / 10:
            g *= 0.06
    return max(0.0, g)


def update_lights(t, overrides=None):
    """Every frame: each light's flicker, times any switch the story sets (overrides: name -> gain)."""
    overrides = overrides or {}
    for name, L in LIGHTS.items():
        g = flicker_gain(t, L["flicker"]) * overrides.get(name, 1.0)
        L["light"].energy = L["base"] * g


def world(hexc_or_rgb, strength=1.0):
    """The world is the fog colour, so far things fade into it."""
    w = bpy.data.worlds.new("world")
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    c = col(hexc_or_rgb) if isinstance(hexc_or_rgb, str) else (*hexc_or_rgb, 1)
    bg.inputs["Color"].default_value = c
    bg.inputs["Strength"].default_value = strength
    return w


def set_fog(hexc, density, start=0.0):
    """Call before any material is made: materials read it when they're built."""
    c = col(hexc)
    FOG.update(color=c[:3], density=density, start=start)


# ---------------------------------------------------------------------------------------------- easing


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    if isinstance(a, (int, float)):
        return a + (b - a) * u
    return tuple(a[i] + (b[i] - a[i]) * u for i in range(len(a)))


def bump(t, t0, rise=0.08, fall=0.35):
    if t < t0:
        return 0.0
    x = t - t0
    return ss(x / rise) * (1 - ss((x - rise) / fall))


def spring(t, t0, amp=1.0, freq=9.0, decay=7.0):
    if t < t0:
        return 0.0
    x = t - t0
    return amp * math.exp(-decay * x) * math.sin(2 * math.pi * freq * x)


# ------------------------------------------------------------------------------------- set materials
# The reference's sets are realistic around plastic avatars: brick, wood, cobbles, stone. All procedural.


def _mat(name):
    m = _new(name)
    nt = m.node_tree
    return m, nt.nodes, nt.links, nt.nodes["Principled BSDF"]


def _coords(N, L, scale, kind="Object"):
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale if isinstance(scale, (tuple, list)) else (scale,) * 3
    L.new(tc.outputs[kind], mp.inputs["Vector"])
    return mp.outputs["Vector"]


def _bump(N, L, b, height_socket, strength, dist):
    bp = N.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = strength
    bp.inputs["Distance"].default_value = dist
    L.new(height_socket, bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])


def bricks(c1="#7a3b2a", c2="#5e2c22", mortar="#4a4540", scale=1.0, name=None, rough=0.8, row=0.25, width=0.5,
           grime_amt=0.4):
    """Bricks in object space (one brick 0.5 x 0.25 m at scale 1), with soft dirt over them."""
    name = name or f"bricks {c1} {c2} {scale}"
    if name in MATS:
        return MATS[name]
    m, N, L, b = _mat(name)
    v = _coords(N, L, scale)
    br = N.new("ShaderNodeTexBrick")
    br.inputs["Color1"].default_value = col(c1)
    br.inputs["Color2"].default_value = col(c2)
    br.inputs["Mortar"].default_value = col(mortar)
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Mortar Size"].default_value = 0.016
    br.inputs["Brick Width"].default_value = width
    br.inputs["Row Height"].default_value = row
    br.inputs["Bias"].default_value = 0.0
    br.offset = 0.5
    L.new(v, br.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.6
    nz.inputs["Detail"].default_value = 4.0
    L.new(v, nz.inputs["Vector"])
    mix = N.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    L.new(br.outputs["Color"], mix.inputs["A"])
    rr = N.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 1.0
    rr.inputs["To Max"].default_value = 1.0 - grime_amt
    L.new(nz.outputs["Fac"], rr.inputs["Value"])
    cc = N.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        L.new(rr.outputs["Result"], cc.inputs[k])
    L.new(cc.outputs["Color"], mix.inputs["B"])
    mix.inputs["Factor"].default_value = 1.0
    L.new(mix.outputs["Result"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    inv = N.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    L.new(br.outputs["Fac"], inv.inputs[1])
    _bump(N, L, b, inv.outputs["Value"], 0.35, 0.02)
    _fogged(m, b.outputs[0])
    return m


def cobbles(c1="#3b3d44", c2="#6d6a66", gap="#1a1a1d", scale=2.6, wet=0.3, name=None):
    """Rounded stones with dark gaps (Voronoi), glossier when wet."""
    name = name or f"cobbles {c1} {scale} {wet}"
    if name in MATS:
        return MATS[name]
    m, N, L, b = _mat(name)
    v = _coords(N, L, scale)
    vor = N.new("ShaderNodeTexVoronoi")
    vor.feature = "DISTANCE_TO_EDGE"
    L.new(v, vor.inputs["Vector"])
    vor2 = N.new("ShaderNodeTexVoronoi")
    L.new(v, vor2.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = col(c1)
    ramp.color_ramp.elements[1].color = col(c2)
    sep = N.new("ShaderNodeSeparateColor")
    L.new(vor2.outputs["Color"], sep.inputs["Color"])
    L.new(sep.outputs["Red"], ramp.inputs["Fac"])
    edge = N.new("ShaderNodeMapRange")
    edge.inputs["From Max"].default_value = 0.1
    L.new(vor.outputs["Distance"], edge.inputs["Value"])
    mix = N.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = col(gap)
    L.new(ramp.outputs["Color"], mix.inputs["B"])
    L.new(edge.outputs["Result"], mix.inputs["Factor"])
    L.new(mix.outputs["Result"], b.inputs["Base Color"])
    rough = N.new("ShaderNodeMapRange")
    rough.inputs["To Min"].default_value = 0.9 - wet
    rough.inputs["To Max"].default_value = 0.75 - wet * 0.5
    L.new(edge.outputs["Result"], rough.inputs["Value"])
    L.new(rough.outputs["Result"], b.inputs["Roughness"])
    _bump(N, L, b, edge.outputs["Result"], 0.5, 0.04)
    _fogged(m, b.outputs[0])
    return m


def planks(c1="#6b4a2e", c2="#4e3520", scale=1.0, axis="X", name=None, rough=0.75):
    """Wood boards: bands across `axis` (one board about 0.2 m wide at scale 1), grain along it, dark seams."""
    name = name or f"planks {c1} {scale} {axis}"
    if name in MATS:
        return MATS[name]
    m, N, L, b = _mat(name)
    v = _coords(N, L, scale)
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(v, sep.inputs[0])
    across = {"X": "Y", "Y": "X", "Z": "X"}[axis]
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 5.0
    L.new(sep.outputs[across], mul.inputs[0])
    fl = N.new("ShaderNodeMath")
    fl.operation = "FLOOR"
    L.new(mul.outputs[0], fl.inputs[0])
    fr = N.new("ShaderNodeMath")
    fr.operation = "FRACT"
    L.new(mul.outputs[0], fr.inputs[0])
    # per-board shade from the board index
    wn = N.new("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "1D"
    L.new(fl.outputs[0], wn.inputs["W"])
    wave = N.new("ShaderNodeTexWave")
    wave.bands_direction = axis if axis in ("X", "Y", "Z") else "X"
    wave.inputs["Scale"].default_value = 3.0
    wave.inputs["Distortion"].default_value = 6.0
    wave.inputs["Detail"].default_value = 3.0
    L.new(v, wave.inputs["Vector"])
    add = N.new("ShaderNodeMath")
    add.operation = "MULTIPLY_ADD"
    L.new(wave.outputs["Fac"], add.inputs[0])
    add.inputs[1].default_value = 0.35
    L.new(wn.outputs["Value"], add.inputs[2])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = col(c2)
    ramp.color_ramp.elements[1].color = col(c1)
    L.new(add.outputs[0], ramp.inputs["Fac"])
    seam = N.new("ShaderNodeMapRange")
    seam.inputs["From Min"].default_value = 0.0
    seam.inputs["From Max"].default_value = 0.05
    L.new(fr.outputs[0], seam.inputs["Value"])
    mix = N.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (0.01, 0.008, 0.006, 1)
    L.new(ramp.outputs["Color"], mix.inputs["B"])
    L.new(seam.outputs["Result"], mix.inputs["Factor"])
    L.new(mix.outputs["Result"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    _bump(N, L, b, seam.outputs["Result"], 0.3, 0.01)
    _fogged(m, b.outputs[0])
    return m


def concrete(hexc="#7d7c78", scale=1.5, stains=0.45, name=None, rough=0.85):
    return grime(hexc, 1.0 - stains, scale, name, rough)


def metal(hexc="#8a8d90", rough=0.35, name=None):
    name = name or f"metal {hexc} {rough}"
    if name in MATS:
        return MATS[name]
    m, N, L, b = _mat(name)
    b.inputs["Base Color"].default_value = col(hexc)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = rough
    _fogged(m, b.outputs[0])
    return m


# ------------------------------------------------------------------------------------------- render


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    MATS.clear()
    OBJ.clear()
    LIGHTS.clear()


def setup_render(res, samples=8, threads=2, exposure=0.0, look="AgX - Medium High Contrast"):
    """Cycles on the CPU (EEVEE is software-only here), low samples with OIDN, a fixed seed so the denoise holds
    still from frame to frame, and few bounces: these sets are lit like a game, not a photo."""
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.render.threads_mode = "FIXED"
    sc.render.threads = int(threads)
    sc.cycles.samples = int(samples)
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.05
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    sc.cycles.denoising_prefilter = "ACCURATE"
    sc.cycles.seed = 7
    sc.cycles.use_animated_seed = False
    sc.cycles.max_bounces = 4
    sc.cycles.diffuse_bounces = 2
    sc.cycles.glossy_bounces = 1
    sc.cycles.transmission_bounces = 2
    sc.cycles.transparent_max_bounces = 4
    sc.cycles.use_fast_gi = True
    sc.cycles.ao_bounces_render = 1
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 1.0
    sc.cycles.sample_clamp_indirect = 5.0
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.image_settings.color_depth = "8"
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = look
    sc.view_settings.exposure = exposure
    sc.render.use_persistent_data = True
    cam = bpy.data.cameras.new("cam")
    cam.sensor_fit = "VERTICAL"
    cam.sensor_height = 24.0
    cam.clip_start = 0.05
    cam.clip_end = 500
    co = link(bpy.data.objects.new("cam", cam))
    sc.camera = co
    OBJ["cam"] = co
    return co


def place_camera(loc, target, lens, roll=0.0):
    co = OBJ["cam"]
    co.location = loc
    d = Vector(target) - Vector(loc)
    q = d.to_track_quat("-Z", "Y")
    e = q.to_euler()
    if roll:
        from mathutils import Matrix
        e = (q.to_matrix() @ Matrix.Rotation(roll, 3, "Z")).to_euler()
    co.rotation_euler = e
    co.data.lens = lens


def render_to(path):
    sc = bpy.context.scene
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
