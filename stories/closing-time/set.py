"""Closing Time: the night hall of a city aquarium, its big tank behind a wall of thick acrylic, the service
corridor, and the Regular. Built from kit.py's parts (story 3, ep13; nothing here is shared with another story's
set).

Coordinates: the hall's floor is z = 0. The acrylic wall's inside face is the plane y = 0, and the hall runs back
from it, y = 0 .. 6, x = -7 .. 7, under a 5 m concrete ceiling. The tank is the other side, y < 0: the acrylic is
ACRYLIC_T thick, the tank floor (sand) is TANK_Z below the hall's floor, and the blue goes on until it's black.
Facing the glass from the hall is yaw 0 (a character faces -y). The service corridor leaves the hall's back wall
at x = 5 and runs back (+y) to a steel door with a round porthole.

The hall is a box built into the tank's rock wall: its front (y = 0 .. BOX_D) sticks out of the rock into the water,
so from the water side its roof shows, with a square steel hatch on top (the keepers' hatch: from inside it's a
plain steel square with no handle on our side). In front of it, on the tank floor, are a rail and two benches facing
it, the same bench model as the two in the hall.

THE REGULAR (note 18, "uncanny beats tentacles"; the brief's continuity list): a broad, limbless diamond 6 m from
wingtip to wingtip and 4 m from the top of its rim to the root of its short thick tail, about 0.5 m thick at the
centre and thinning to a soft rounded rim. Wet near-black navy back, milk-white front with a faint blue cast. Two
rows of heavy shut lids down its front; behind each is a modelled, realistic human eye (wet white, brown iris, black
pupil), the only realistic eyes in the film, about as wide as a cast member's head. One long closed mouth line below
them. Nothing on it is thinner than a forearm. `build_regular()` makes it once and `pose_regular()` only moves those
same parts (where it is, its tilt, the ripple running round its rim, each lid and where every eye looks), so it's the
same thing in every shot. The pup is the same build at a quarter of the size.

Cues read here (all optional):
- regular / pup: {"pos": [x, y, z] its centre, "yaw": deg, "roll": deg, "press": 0..1, "glide": true, "ripple": amp,
  "hidden": bool} where it is; a cue with "glide" moves it smoothly from the cue before (it's always seen moving)
- eyes / pup_eyes: {"state": "shut" | "open" | "crack" | "blinkwave", "order": [eye indices] or "rows", "every": s, "look": "me" |
  "dev" | "rosa" | "cam" | [x, y, z], "blink": true} lids open (or close) one after another from the cue's time;
  "crack" lifts the lids of "which" a little for "dur" seconds
- shot: {"look": {...} or null} one shot's own lights (shot_look below)
- lights: {"state": "rest" | "stuck" | "fade" | "dark", "dur": s} the hall's display lights
- fogbloom: {"on": bool, "dur": s} the breath fog on the acrylic where it presses
- bubbles: {"kind": "applause" | "tiny", "dur": s, "x0", "x1"} a stream of bubbles rolling along the glass
- mop / bucket: {"who", "pos"} props
- door: {"open": 0..1, "dur": s} the corridor's steel door
- tank_fog: {"density": d} thins the blue (the reveal)

Acting keys read here (acting.py ignores them): "bow": degrees the torso bends forward at the hips; "mop": true puts
a mop in the right hand; "wave": [left, right] waving amplitude (the arm's raised by `arms`, this swings it);
"wipe": true makes the right hand wipe along the rail.
"""

from __future__ import annotations

import math

import bpy
import numpy as np
from mathutils import Matrix, Vector as V

from blocky import rig

# ------------------------------------------------------------------------------------------------ the hall
HX0, HX1 = -7.0, 7.0          # the hall's inside, side to side
HY1 = 6.0                     # the back wall (the glass is y = 0)
CEIL = 5.0
GLASS_X0, GLASS_X1 = -6.0, 6.0
GLASS_Z0, GLASS_Z1 = 0.25, 4.75
ACRYLIC_T = 0.3               # the acrylic's thickness: its tank face is y = -ACRYLIC_T
GLASS_FACE = -ACRYLIC_T
RAIL_Y, RAIL_Z = 0.45, 1.0    # the brushed steel handrail along the glass
TANK_Z = -1.2                 # the sand floor on the water side
BOX_D = 2.4                   # how far the hall's front sticks out of the rock (its roof shows from the water)
ROOF_Z = CEIL + 0.45
HATCH = (-2.2, 1.2)           # the ceiling hatch's centre (x, y): inside the part of the box that's in the water
HATCH_W = 1.0
PILLARS = [(-3.6, 3.6), (3.6, 3.6)]
COR_X = 5.0                   # the service corridor's centre line; it leaves the back wall (y = HY1) and runs +y
COR_W, COR_L, COR_H = 1.7, 9.0, 2.7
BENCHES_HALL = [(-3.0, 3.0), (2.6, 3.0)]
BENCHES_TANK = [(-2.0, -5.6), (2.4, -6.2)]

# ------------------------------------------------------------------------------------------------ the Regular
REG_A = 3.0                   # half its width (wingtip to wingtip is 6 m)
REG_BT, REG_BB = 1.7, 2.3     # its centre to the top of the rim, and to the tail root (4 m in all)
REG_TF, REG_TB = 0.3, 0.2     # the front bulge and the back, at the centre (0.5 m thick)
REG_P = 1.6                   # the outline: a superellipse between a diamond (1) and an oval (2), soft-cornered
EYE_R = 0.2                   # an eyeball's radius: 0.4 m across, a cast member's head is 0.42
LID_R = EYE_R + 0.036          # the top of a lid sheet over the eyeball (it touches the glass when pressed)
SINK = 0.06                   # each eye's centre sits this far under the skin, so the lids make heavy mounds
MOUND = LID_R - SINK
ROW_X = 0.55                  # the two rows, either side of the middle
ROW_Z = [0.88, 0.41, -0.06, -0.53, -1.0]    # five lids a row, top to bottom (about 2.1 m with the lids)
MOUTH_Z, MOUTH_W = -1.72, 1.5
LID_OPEN_U, LID_OPEN_L = 27.0, -24.0        # degrees: a heavy-lidded, level stare
LID_SHUT_U, LID_SHUT_L = -6.0, 3.0
EYE_MAX = math.radians(42.0)                # how far an eyeball turns in its lids


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def _switch(cs, attr, t, default):
    v = default
    for c in cs:
        if attr in c and c["t"] <= t + 1e-9:
            v = c[attr]
    return v


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


# ------------------------------------------------------------------------------------------------ materials
# Two fogs: the hall is clear (no fog unless a shot is looking at it from the water), and everything in the tank
# fades into the blue with distance from the camera. Each material's fog node is kept in a group so animate()
# can set it per shot.
FOGS = {"hall": [], "tank": [], "reg": [], "eyes": []}
TANK_FOG = {"color": "#114a5e", "density": 0.14, "start": 3.5}


def _fog(kit, m, sock, group):
    """Route a shader through a distance fog of our own (kit's fog is global and the hall must stay clear)."""
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    cam = N.new("ShaderNodeCameraData")
    sub = N.new("ShaderNodeMath")
    sub.operation = "SUBTRACT"
    L.new(cam.outputs["View Distance"], sub.inputs[0])
    sub.inputs[1].default_value = TANK_FOG["start"]
    mx = N.new("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    L.new(sub.outputs[0], mx.inputs[0])
    mx.inputs[1].default_value = 0.0
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(mx.outputs[0], mul.inputs[0])
    mul.inputs[1].default_value = -TANK_FOG["density"] if group in ("tank", "reg", "eyes") else 0.0
    ex = N.new("ShaderNodeMath")
    ex.operation = "EXPONENT"
    L.new(mul.outputs[0], ex.inputs[0])
    inv = N.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    L.new(ex.outputs[0], inv.inputs[1])
    fog = N.new("ShaderNodeEmission")
    fog.inputs["Color"].default_value = kit.col(TANK_FOG["color"])
    fog.inputs["Strength"].default_value = 1.0
    mix = N.new("ShaderNodeMixShader")
    L.new(inv.outputs[0], mix.inputs[0])
    L.new(sock, mix.inputs[1])
    L.new(fog.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs["Surface"])
    FOGS[group].append((mul, sub, fog))
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass


def pbr(kit, name, hexc, rough=0.5, group="hall", metal=0.0, coat=0.0, sss=0.0, sss_r=(0.4, 0.5, 0.7),
        noise=None, bump=None, spec=0.5):
    """A Principled material, fogged by its group. noise = (scale, dark factor, detail) mottles the colour; bump =
    (scale, strength, distance) roughens the surface."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
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
        b.inputs["Coat Roughness"].default_value = 0.06
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = sss_r
        b.inputs["Subsurface Scale"].default_value = 0.05
    tc = None
    if noise:
        tc = N.new("ShaderNodeTexCoord")
        nz = N.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = noise[0]
        nz.inputs["Detail"].default_value = noise[2] if len(noise) > 2 else 4.0
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
        tc = tc or N.new("ShaderNodeTexCoord")
        nz2 = N.new("ShaderNodeTexNoise")
        nz2.inputs["Scale"].default_value = bump[0]
        nz2.inputs["Detail"].default_value = 8.0
        L.new(tc.outputs["Object"], nz2.inputs["Vector"])
        bp = N.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump[1]
        bp.inputs["Distance"].default_value = bump[2]
        L.new(nz2.outputs["Fac"], bp.inputs["Height"])
        L.new(bp.outputs["Normal"], b.inputs["Normal"])
    m.diffuse_color = kit.col(hexc)
    _fog(kit, m, b.outputs[0], group)
    return m


def emitter(kit, name, hexc, strength, group="hall"):
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = strength
    _fog(kit, m, e.outputs[0], group)
    return m


def acrylic(kit, name="acrylic", tint="#f6fbfb", gloss=0.03):
    """Thick clear acrylic, cheaply: a see-through layer tinted faint blue-green, with a Fresnel reflection on top
    (IOR 1.49). No refraction, so the tank and the Regular sit exactly where they are and every frame stays cheap."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    N.remove(N["Principled BSDF"])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    tr = N.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = kit.col(tint)
    gl = N.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = gloss
    gl.inputs["Color"].default_value = (1, 1, 1, 1)
    fr = N.new("ShaderNodeFresnel")
    fr.name = "fresnel"
    fr.inputs["IOR"].default_value = 1.49
    mix = N.new("ShaderNodeMixShader")
    L.new(fr.outputs[0], mix.inputs[0])
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(gl.outputs[0], mix.inputs[2])
    # light passing through it (shadow rays) sees only the clear tint, so the caustics and the hall's lamps cross
    lp = N.new("ShaderNodeLightPath")
    tr2 = N.new("ShaderNodeBsdfTransparent")
    tr2.inputs["Color"].default_value = kit.col(tint)
    mix2 = N.new("ShaderNodeMixShader")
    L.new(lp.outputs["Is Shadow Ray"], mix2.inputs[0])
    L.new(mix.outputs[0], mix2.inputs[1])
    L.new(tr2.outputs[0], mix2.inputs[2])
    L.new(mix2.outputs[0], out.inputs["Surface"])
    return m


def refog(kit, m, group):
    """A kit material (made with no fog) routed through one of our fogs instead."""
    nt = m.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    lk = out.inputs["Surface"].links[0]
    sock = lk.from_socket
    nt.links.remove(lk)
    _fog(kit, m, sock, group)
    return m


def tiles(kit, name, c1, c2, grout, size=0.15, rough=0.12, group="hall"):
    """Square glazed tiles in a stack bond (kit's bricks with no offset), glossy, a little uneven."""
    m = kit.bricks(c1, c2, grout, 1.0 / size * 0.25, name=name, rough=rough, row=0.25, width=0.25, grime_amt=0.12)
    for n in m.node_tree.nodes:
        if n.bl_idname == "ShaderNodeTexBrick":
            n.offset = 0.0
            n.inputs["Mortar Size"].default_value = 0.012
    return refog(kit, m, group)


def materials(kit):
    M = {}
    R = "reg"
    # the Regular: wet navy back with darker mottling, a milk-white front with a faint blue cast, see-through at
    # the rim (subsurface), the skin round each eye greyer (sunk in), a blue-black upper lid margin, a wet lower one
    M["reg_back"] = pbr(kit, "reg back", "#141c2b", 0.32, R, coat=0.6, noise=(1.6, 0.55, 5.0), bump=(9.0, 0.12, 0.02))
    # round 2 (P1): the front is a cool blue-white, never neutral grey (#a4b3c4, in the decision's #9aa8b3 ..
    # #aebccb), so it stays "PALE" against the navy back without clipping; the lids are the same skin in their own
    # fog group ("eyes"), so a wide can sink the outline into the blue and keep the rows
    FRONT = "#a4b3c4"
    M["reg_front"] = pbr(kit, "reg front", FRONT, 0.36, R, coat=0.45, sss=0.25, sss_r=(0.5, 0.65, 0.9),
                         noise=(3.0, 0.9, 4.0), bump=(14.0, 0.08, 0.01))
    E = "eyes"
    M["reg_lid"] = pbr(kit, "reg lid", FRONT, 0.36, E, coat=0.45, sss=0.25, sss_r=(0.5, 0.65, 0.9),
                       noise=(3.0, 0.9, 4.0), bump=(14.0, 0.08, 0.01))
    M["reg_socket"] = pbr(kit, "reg socket", "#5c6a7a", 0.3, E, coat=0.5, sss=0.2, sss_r=(0.5, 0.65, 0.9))
    M["reg_lower"] = pbr(kit, "reg lower", "#788595", 0.12, E, coat=1.0)
    # the upper lash line a touch darker and less glossy (the shut lids read as lips at S24)
    M["reg_margin"] = pbr(kit, "reg margin", "#030407", 0.35, E, coat=0.4)
    M["reg_mouth"] = pbr(kit, "reg mouth", "#0b1018", 0.3, R, coat=0.5)
    M["acrylic"] = acrylic(kit)
    M["steel_dark"] = pbr(kit, "steel dark", "#24282c", 0.45, metal=1.0)
    M["silicone"] = pbr(kit, "silicone", "#08090b", 0.6)
    # the hall: polished concrete, white square tile to 1.2 m, raw concrete above, brushed steel
    M["floor"] = pbr(kit, "polished concrete", "#565b60", 0.16, noise=(0.9, 0.72, 6.0), bump=(40.0, 0.02, 0.002))
    M["tile"] = tiles(kit, "hall tile", "#e4e9e6", "#d9dfdc", "#8c938f")
    M["concrete"] = refog(kit, kit.concrete("#6c6e6c", 1.2, 0.5, name="hall concrete", rough=0.9), "hall")
    M["ceiling"] = refog(kit, kit.concrete("#4b4e50", 0.8, 0.45, name="hall ceiling", rough=0.92), "hall")
    M["steel"] = pbr(kit, "brushed steel", "#a9adb0", 0.28, metal=1.0, bump=(200.0, 0.04, 0.001))
    M["steel_hatch"] = pbr(kit, "hatch steel", "#8a8f93", 0.5, metal=0.35, noise=(2.0, 0.8))
    M["rubber"] = pbr(kit, "rubber", "#141516", 0.7)
    M["yellow"] = pbr(kit, "bucket yellow", "#e3b21c", 0.35, coat=0.3)
    M["wood"] = refog(kit, kit.planks("#7a5536", "#5d3f27", 1.0, "X", name="bench wood", rough=0.6), "hall")
    M["mop"] = pbr(kit, "mop strands", "#c9c2b0", 0.9, noise=(30.0, 0.7))
    M["panel_rest"] = emitter(kit, "display panel", "#e9f2f6", 6.0)
    M["switch"] = pbr(kit, "switch plate", "#d8d8d2", 0.4)
    M["tabard"] = pbr(kit, "tabard", "#34373d", 0.85, noise=(18.0, 0.85))
    M["fogbloom"] = bloom_mat(kit)
    # the corridor: cream tile, pipes, a steel mop sink, the caged light
    M["ctile"] = tiles(kit, "corridor tile", "#e2d8bf", "#d6cdb5", "#8f8875", size=0.12)
    M["pipe"] = pbr(kit, "pipe", "#5f6a6c", 0.45, metal=0.6)
    M["cage"] = pbr(kit, "cage", "#202224", 0.5, metal=1.0)
    M["bulb"] = emitter(kit, "caged bulb", "#e9f1ff", 25.0)
    M["porthole"] = acrylic(kit, "porthole", "#f4f8f8")
    M["door"] = pbr(kit, "steel door", "#6f767b", 0.42, metal=0.85, noise=(1.5, 0.8))
    # the tank: sand, blocky rock, the box's outside, kelp, the crowd, the benches out there, bubbles
    T = "tank"
    M["sand"] = pbr(kit, "sand", "#7f8a7c", 0.95, T, noise=(0.7, 0.7, 6.0), bump=(6.0, 0.25, 0.04))
    M["rock"] = pbr(kit, "rock", "#3a4648", 0.9, T, noise=(1.1, 0.55, 6.0), bump=(3.0, 0.4, 0.05))
    M["rock2"] = pbr(kit, "rock dark", "#262f33", 0.9, T, noise=(1.4, 0.6, 6.0), bump=(3.5, 0.4, 0.05))
    M["box_out"] = pbr(kit, "box outside", "#4f5a5b", 0.85, T, noise=(0.8, 0.6, 6.0))
    M["kelp"] = pbr(kit, "kelp", "#1d2a1e", 0.6, T, noise=(4.0, 0.6))
    M["crowd"] = crowd_mat(kit)
    M["wood_t"] = refog(kit, kit.planks("#6e5a45", "#4f4232", 1.0, "X", name="tank bench wood", rough=0.8), T)
    M["steel_t"] = pbr(kit, "tank rail", "#7c8487", 0.4, T, metal=0.9)
    M["hatch_out"] = pbr(kit, "hatch outside", "#6b7375", 0.5, T, metal=0.8, noise=(2.0, 0.7))
    M["ray"] = ray_mat(kit)
    M["bubble"] = bubble_mat(kit)
    M["hallglow"] = emitter(kit, "hall seen from the water", "#cfe6ee", 1.0, T)
    return M


def crowd_mat(kit):
    """The crowd's skin: a dark blue-black body with a faint fog-blue rim where it turns away (a Fresnel glow), so
    each one reads as a leaf-shaped fish in the water, not a hole in the picture (round 2, P3)."""
    name = "crowd"
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col("#15293a")
    b.inputs["Roughness"].default_value = 0.55
    lw = N.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    ramp = N.new("ShaderNodeMath")
    ramp.operation = "POWER"
    L.new(lw.outputs["Facing"], ramp.inputs[0])
    ramp.inputs[1].default_value = 2.2
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col("#4f9fb4")
    gain = N.new("ShaderNodeMath")
    gain.name = "rim"
    gain.operation = "MULTIPLY"
    L.new(ramp.outputs[0], gain.inputs[0])
    gain.inputs[1].default_value = 0.6
    L.new(gain.outputs[0], em.inputs["Strength"])
    add = N.new("ShaderNodeAddShader")
    L.new(b.outputs[0], add.inputs[0])
    L.new(em.outputs[0], add.inputs[1])
    _fog(kit, m, add.outputs[0], "tank")
    return m


def leaf_mesh(kit, name, mat):
    """One crowd fish: a lens-shaped body (pointed at both ends) with a small forked tail, 2 x 0.9 units, thin, its
    broad side to the hall."""
    n = 18
    top, bot = [], []
    for i in range(n + 1):
        x = -1.0 + 2.0 * i / n
        h = 0.45 * (1 - x * x) ** 0.85 * (1 + 0.12 * x)
        top.append((x, h))
        bot.append((x, -h * 0.92))
    outline = top + [(1.0, 0.0), (1.32, 0.3), (1.22, 0.0), (1.32, -0.3)] + bot[::-1][:-1]
    verts, faces = [], []
    for y in (0.5, -0.5):
        verts += [(x, y, z) for x, z in outline]
    k = len(outline)
    cf, cb = len(verts), len(verts) + 1
    verts += [(0.0, 0.62, 0.0), (0.0, -0.62, 0.0)]
    for i in range(k):
        j = (i + 1) % k
        faces.append((i, j, cf))
        faces.append((k + j, k + i, cb))
        faces.append((i, k + i, k + j, j))
    return kit.mesh_obj(name, verts, faces, mat, None, smooth=True)


def bloom_mat(kit):
    """The breath fog on the acrylic: a soft pale haze, round, thickest in the middle (its alpha is driven)."""
    m = kit._new("fog bloom")
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    N.remove(N["Principled BSDF"])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    tc = N.new("ShaderNodeTexCoord")
    gr = N.new("ShaderNodeTexGradient")
    gr.gradient_type = "SPHERICAL"
    mp = N.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    L.new(mp.outputs["Vector"], gr.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(gr.outputs["Fac"], mul.inputs[0])
    L.new(nz.outputs["Fac"], mul.inputs[1])
    amt = N.new("ShaderNodeMath")
    amt.operation = "MULTIPLY"
    amt.name = "amount"
    amt.inputs[1].default_value = 0.0
    L.new(mul.outputs[0], amt.inputs[0])
    tr = N.new("ShaderNodeBsdfTransparent")
    df = N.new("ShaderNodeEmission")      # breath haze: added on top, faint and pale, it never dims what's behind
    df.inputs["Color"].default_value = kit.col("#cfe2ea")
    L.new(amt.outputs[0], df.inputs["Strength"])
    add = N.new("ShaderNodeAddShader")
    L.new(tr.outputs[0], add.inputs[0])
    L.new(df.outputs[0], add.inputs[1])
    L.new(add.outputs[0], out.inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    kit.MATS["fog bloom"] = m
    return m


def ray_mat(kit):
    """God rays from the surface: faint additive light, fading at both ends (transparent elsewhere)."""
    m = kit._new("god ray")
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    N.remove(N["Principled BSDF"])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Generated"], sep.inputs[0])
    fade = N.new("ShaderNodeFloatCurve") if False else N.new("ShaderNodeMath")
    fade.operation = "PINGPONG"
    fade.inputs[1].default_value = 0.5
    L.new(sep.outputs["Z"], fade.inputs[0])
    side = N.new("ShaderNodeMath")
    side.operation = "PINGPONG"
    side.inputs[1].default_value = 0.5
    L.new(sep.outputs["X"], side.inputs[0])
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(fade.outputs[0], mul.inputs[0])
    L.new(side.outputs[0], mul.inputs[1])
    g = N.new("ShaderNodeMath")
    g.operation = "MULTIPLY"
    g.name = "gain"
    g.inputs[1].default_value = 0.12
    L.new(mul.outputs[0], g.inputs[0])
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col("#7fd4e6")
    L.new(g.outputs[0], em.inputs["Strength"])
    tr = N.new("ShaderNodeBsdfTransparent")
    add = N.new("ShaderNodeAddShader")
    L.new(em.outputs[0], add.inputs[0])
    L.new(tr.outputs[0], add.inputs[1])
    L.new(add.outputs[0], out.inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    kit.MATS["god ray"] = m
    return m


def bubble_mat(kit):
    """A bubble: see-through in the middle, a bright silver rim (Fresnel), faintly fogged with the tank."""
    m = kit._new("bubble")
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    N.remove(N["Principled BSDF"])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    lw = N.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col("#e8fbff")
    em.inputs["Strength"].default_value = 2.2
    tr = N.new("ShaderNodeBsdfTransparent")
    mix = N.new("ShaderNodeMixShader")
    L.new(lw.outputs["Facing"], mix.inputs[0])
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(em.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    kit.MATS["bubble"] = m
    return m


# ------------------------------------------------------------------------------------------------ the eyes


def eye_texture(seed=0, size=768):
    """The front of a human eyeball as a flat texture (planar along the gaze, -1..1 across the ball): a wet white,
    a brown iris with radial fibres, a darker ring at its edge, a darker collarette round a black pupil. No veins,
    no red. Made here from noise, per eye a little different."""
    from PIL import Image

    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[-1:1:size * 1j, -1:1:size * 1j]
    rho = np.hypot(xx, yy)
    th = np.arctan2(yy, xx)
    IRIS, PUP = 0.43, 0.15 + 0.012 * rng.standard_normal()
    # sclera: an off-white, a touch cooler and darker toward the edges of the ball
    scl = np.stack([0.93 - 0.06 * rho ** 3, 0.92 - 0.06 * rho ** 3, 0.89 - 0.05 * rho ** 3], -1)
    # iris fibres: many thin radial streaks (noise in angle), plus coarse crypts
    f = np.zeros_like(rho)
    for k, (n, a) in enumerate(((180, 0.35), (60, 0.35), (23, 0.3))):
        ph = rng.uniform(0, 2 * np.pi, 8)
        f += a * np.sin(n * th + 2.5 * np.sin(3 * th + ph[0]) + 6 * rho + ph[1])
    f = 0.5 + 0.5 * np.tanh(f)
    base = np.array([0.36, 0.2, 0.09]) * (0.9 + 0.2 * rng.random())
    light = np.array([0.62, 0.42, 0.2])
    dark = np.array([0.12, 0.06, 0.03])
    u = (rho - PUP) / (IRIS - PUP)                   # 0 at the pupil, 1 at the iris edge
    col = base[None, None] * (0.75 + 0.5 * f[..., None])
    col = col + (light - base)[None, None] * (np.clip(1 - np.abs(u - 0.45) / 0.25, 0, 1) * f * 0.5)[..., None]
    coll = np.exp(-((u - 0.12) / 0.09) ** 2)[..., None]       # the collarette round the pupil
    col = col * (1 - 0.45 * coll)
    limb = np.clip((u - 0.8) / 0.2, 0, 1) ** 1.5             # the dark limbal ring
    col = col * (1 - limb[..., None]) + dark * limb[..., None]
    img = np.where((rho < IRIS)[..., None], col, scl)
    # a soft blend from the limbal ring into the white
    edge = np.clip((rho - IRIS) / 0.04, 0, 1)[..., None]
    img = np.where((rho >= IRIS)[..., None], dark * (1 - edge) + scl * edge, img)
    img = np.where((rho < PUP)[..., None], np.array([0.012, 0.01, 0.01]), img)
    pe = np.clip((rho - PUP) / 0.012, 0, 1)[..., None]
    img = np.where((rho < PUP + 0.012)[..., None], np.array([0.012, 0.01, 0.01]) * (1 - pe) + img * pe, img)
    return Image.fromarray(np.clip(img * 255, 0, 255).astype(np.uint8))


def eye_material(kit, idx, group="reg"):
    name = f"eye {idx % 4}"
    if name in kit.MATS:
        return kit.MATS[name]
    pil = eye_texture(seed=idx % 4 + 11)
    img = bpy.data.images.new(name, pil.width, pil.height)
    a = np.asarray(pil.convert("RGBA")).astype(np.float32)[::-1] / 255
    img.pixels.foreach_set(a.ravel())
    img.pack()
    m = kit._new(name)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    tx = N.new("ShaderNodeTexImage")
    tx.image = img
    tx.interpolation = "Cubic"
    uv = N.new("ShaderNodeUVMap")
    L.new(uv.outputs["UV"], tx.inputs["Vector"])
    L.new(tx.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.25
    b.inputs["Coat Weight"].default_value = 1.0      # the wet cornea: a sharp, bright highlight
    b.inputs["Coat Roughness"].default_value = 0.02
    b.inputs["Subsurface Weight"].default_value = 0.08
    b.inputs["Subsurface Radius"].default_value = (0.6, 0.5, 0.45)
    b.inputs["Subsurface Scale"].default_value = 0.01
    _fog(kit, m, b.outputs[0], group)
    return m


def uv_ball(kit, name, r, mat, parent, seg=40, rings=24):
    """A sphere looking along +y, with a planar UV along +y (so the eye texture sits on its front)."""
    verts, faces, uvs = [], [], []
    for i in range(rings + 1):
        th = math.pi * i / rings          # 0 at the front (+y)
        for j in range(seg):
            ph = 2 * math.pi * j / seg
            x, z, y = r * math.sin(th) * math.cos(ph), r * math.sin(th) * math.sin(ph), r * math.cos(th)
            verts.append((x, y, z))
            uvs.append((0.5 + x / (2 * r), 0.5 + z / (2 * r)) if y > 0 else (0.98, 0.5))
    for i in range(rings):
        for j in range(seg):
            a, b = i * seg + j, i * seg + (j + 1) % seg
            faces.append((a, a + seg, b + seg, b))
    ob = kit.mesh_obj(name, verts, faces, mat, parent, smooth=True)
    uv = ob.data.uv_layers.new(name="UVMap")
    for poly in ob.data.polygons:
        for li in poly.loop_indices:
            uv.data[li].uv = uvs[ob.data.loops[li].vertex_index]
    return ob


LID_ANG, LID_RINGS = 72, 16
LID_OUT = 0.46                 # the lid sheet's outer edge, tucked under the body's skin
APER_W = 0.186                 # half the almond's width (the corners sit on the eyeball)
APER_OPEN = (0.074, 0.06)      # the almond's upper and lower half-heights, open: a human 3 to 1, the lids over the top and bottom of the iris
APER_SHUT_Z = -0.022           # where the lids meet when shut, a little below the middle


def _smax(a, b, k=0.03):
    h = np.clip(0.5 + 0.5 * (a - b) / k, 0, 1)
    return a * h + b * (1 - h) + k * h * (1 - h)


def lid_coords(open_, gz=0.0, wide=1.0):
    """The lid sheet round one eye (local, gaze +y, the eye's centre at 0): ring 0 lies on the eyeball along the
    almond's edge (the wet inner margin), ring 1 is the lid's rim just outside it, and the rest wrap the eyeball
    and swell into the skin with a soft puffy roll, out to LID_OUT. open_ 0 (shut) .. 1 (open). gz is the gaze's
    vertical turn (sine): the lids follow it, so a downward stare is hooded, not wide-eyed. wide scales the
    opening (each eye a little different)."""
    o = _ss(open_)
    hu = (APER_OPEN[0] * wide - max(0.0, -gz) * 0.03 + max(0.0, gz) * 0.03) * o + 0.003
    hl = (APER_OPEN[1] * wide - max(0.0, gz) * 0.025 + max(0.0, -gz) * 0.015) * o + 0.003
    z0 = APER_SHUT_Z * (1 - o) + gz * 0.11 * o
    al = np.linspace(0, 2 * np.pi, LID_ANG, endpoint=False)
    c, s_ = np.cos(al), np.sin(al)
    ax = APER_W * np.sign(c) * np.abs(c) ** 0.85
    az = z0 + np.where(s_ > 0, hu, hl) * s_ * (1.0 - 0.18 * np.abs(c))
    ox, oz = LID_OUT * c, LID_OUT * s_
    rings = []
    for k in range(LID_RINGS + 1):
        if k == 0:
            f = 0.0
        else:
            f = 0.015 + 0.985 * ((k - 1) / (LID_RINGS - 1)) ** 1.5
        x = ax + (ox - ax) * f
        z = az + (oz - az) * f
        r2 = x * x + z * z
        if k == 0:
            y = np.sqrt(np.clip(EYE_R ** 2 - r2, 0, None)) + 0.004
        else:
            rr = np.sqrt(r2)
            ball = np.sqrt(np.clip((EYE_R + 0.032) ** 2 - r2, 0, None))
            skin = SINK + 0.002 + 0.042 * np.exp(-((rr - 0.25) / 0.07) ** 2) + 0.012 * np.exp(-((rr - 0.34) / 0.06) ** 2)
            y = _smax(ball, skin, 0.05)
            d = f * np.hypot(ox - ax, oz - az)                  # distance out from the almond's edge
            y = y - np.where(s_ > 0, 0.016 * np.exp(-((d - 0.07) / 0.016) ** 2) * (0.4 + 0.6 * s_),
                             0.008 * np.exp(-((d - 0.09) / 0.03) ** 2) * (-s_))
            if k == LID_RINGS:
                y = np.full_like(y, SINK - 0.02)
        rings.append(np.stack([x, y, z], -1))
    return np.concatenate(rings)


def lid_mesh(kit, name, mat, margin_mat, socket_mat, lower_mat, parent):
    """One eye's lid sheet (vertices from lid_coords; set_lids moves them)."""
    v = lid_coords(0.0)
    faces, mats = [], []
    for k in range(LID_RINGS):
        for j in range(LID_ANG):
            j2 = (j + 1) % LID_ANG
            a, b = k * LID_ANG + j, k * LID_ANG + j2
            faces.append((a, b, b + LID_ANG, a + LID_ANG))
            upper = math.sin(2 * math.pi * (j + 0.5) / LID_ANG) > 0
            mats.append((1 if upper else 3) if k == 0 else 2 if k <= 2 else 0)
    ob = kit.mesh_obj(name, [tuple(p) for p in v], faces, mat, parent, smooth=True)
    ob.data.materials.append(margin_mat)
    ob.data.materials.append(socket_mat)
    ob.data.materials.append(lower_mat)
    for p, mi in zip(ob.data.polygons, mats):
        p.material_index = mi
    return ob


# ------------------------------------------------------------------------------------------------ the body


def _outline(theta):
    """A point on the Regular's outline (x, z) at angle theta: a soft-cornered diamond, deeper below."""
    c, s = math.cos(theta), math.sin(theta)
    x = REG_A * math.copysign(abs(c) ** (2 / REG_P), c)
    b = REG_BT if s > 0 else REG_BB
    z = b * math.copysign(abs(s) ** (2 / REG_P), s)
    return x, z


def _norm_r(x, z):
    b = REG_BT if z > 0 else REG_BB
    return (abs(x / REG_A) ** REG_P + abs(z / b) ** REG_P) ** (1 / REG_P)


def _thick(r, t0):
    r = min(1.0, r)
    return t0 * max(0.0, 1 - r ** 2.4) ** 0.5


def build_body(kit, name, M, parent, n_ang=120, n_ring=26):
    """The body's mesh: front (+y) and back surfaces meeting at a rounded rim, from a polar grid that's denser at
    the rim. Returns the object and the rest positions (with each vertex's r and angle) for the ripple."""
    verts, faces, mats, info = [], [], [], []
    rings = [math.sin(0.5 * math.pi * i / n_ring) for i in range(1, n_ring + 1)]
    for side, t0 in ((1, REG_TF), (-1, REG_TB)):
        base = len(verts)
        verts.append((0.0, side * t0, 0.0))
        info.append((0.0, 0.0, side))
        for r in rings:
            for j in range(n_ang):
                th = 2 * math.pi * j / n_ang
                bx, bz = _outline(th)
                verts.append((bx * r, side * _thick(r, t0), bz * r))
                info.append((r, th, side))
        for j in range(n_ang):
            j2 = (j + 1) % n_ang
            f = (base, base + 1 + j, base + 1 + j2)
            faces.append(f if side < 0 else tuple(reversed(f)))
            mats.append(0 if side > 0 else 1)
        for i in range(n_ring - 1):
            for j in range(n_ang):
                j2 = (j + 1) % n_ang
                a, b = base + 1 + i * n_ang + j, base + 1 + i * n_ang + j2
                c_, d = a + n_ang, b + n_ang
                f = (a, c_, d, b)
                faces.append(f if side < 0 else tuple(reversed(f)))
                mats.append(0 if side > 0 else 1)
    # stitch the two rims (the last ring of each side) with one thin band, so there's no crack
    n_side = 1 + n_ring * n_ang
    for j in range(n_ang):
        j2 = (j + 1) % n_ang
        a, b = 1 + (n_ring - 1) * n_ang + j, 1 + (n_ring - 1) * n_ang + j2
        faces.append((a, b, n_side + b, n_side + a) if True else None)
        mats.append(1)
    ob = kit.mesh_obj(name, verts, faces, None, parent, smooth=True)
    ob.data.materials.append(M["reg_front"])
    ob.data.materials.append(M["reg_back"])
    for p, mi in zip(ob.data.polygons, mats):
        p.material_index = mi
    rest = np.array(verts, dtype=np.float64)
    return ob, rest, np.array(info, dtype=np.float64)


def front_y(x, z):
    """The front surface's height (local y) at (x, z), at rest."""
    return _thick(_norm_r(x, z), REG_TF)


def eye_slots():
    """(x, z) of every lid, row by row: the left row top to bottom, then the right."""
    return [(sx * ROW_X, z) for sx in (-1, 1) for z in ROW_Z]


def build_regular(kit, ctx, M, name="regular", scale=1.0):
    """The Regular (or, at scale 0.25, its pup): one body, a tail stub, the closed mouth line, and the lids and
    real eyes in two rows. Built once; pose_regular() only moves these parts."""
    root = kit.empty(name, (0, -6, 2.4))
    root.scale = (scale,) * 3
    body, rest, info = build_body(kit, f"{name}.body", M, root)
    # the tail stub: short, thick as a leg, rounded, from the bottom tip of the back, curving away from the glass
    tail = kit.empty(f"{name}.tailp", (0, -0.12, -REG_BB + 0.34), root, rot=(math.radians(-88), 0, 0))
    kit.cyl(f"{name}.tail", 0.19, 1.0, (0, 0, -0.5), M["reg_back"], tail, n=20, r2=0.11)
    kit.sphere(f"{name}.tailtip", 0.11, (0, 0, -1.0), M["reg_back"], tail, seg=16)
    kit.sphere(f"{name}.tailroot", 0.2, (0, 0, -0.05), M["reg_back"], tail, seg=16).scale = (1.0, 0.7, 1.1)
    # the mouth: one long straight closed line, two soft swollen lips of the same skin pressed together over a thin
    # dark seam, sunk into the front so they read as flesh, not a slot
    mz = MOUTH_Z
    my = front_y(0, mz)
    mouth = kit.box(f"{name}.mouth", (MOUTH_W - 0.1, 0.05, 0.022), (0, my - 0.02, mz), M["reg_mouth"], root, bevel=0.01)
    for k, dz in enumerate((0.034, -0.034)):
        lip = kit.empty(f"{name}.lip{k}", (0, my - 0.035, mz + dz), root)
        lip.scale = (1.0, 0.55, 0.8 if k == 0 else 0.95)
        kit.cyl(f"{name}.lipc{k}", 0.05, MOUTH_W - 0.1, (0, 0, 0), M["reg_front"], lip, rot=(0, math.pi / 2, 0), n=16)
        for sx in (-1, 1):
            kit.sphere(f"{name}.lipe{k}{sx}", 0.05, (sx * (MOUTH_W - 0.1) / 2, 0, 0), M["reg_front"], lip, seg=12)
    eyes = []
    jit = np.random.default_rng(23)
    for i, (x, z) in enumerate(eye_slots()):
        # grown, not stamped: each lid a little off the grid, a little bigger or smaller, a little tilted
        x += float(jit.uniform(-0.03, 0.03))
        z += float(jit.uniform(-0.035, 0.035))
        e = kit.empty(f"{name}.eye{i}", (x, front_y(x, z) - SINK, z), root)
        e.scale = (float(jit.uniform(0.93, 1.08)),) * 3
        e.rotation_euler = (0, float(jit.uniform(-0.09, 0.09)), 0)
        ball = uv_ball(kit, f"{name}.ball{i}", EYE_R, eye_material(kit, i, "eyes"), e)
        lid = lid_mesh(kit, f"{name}.lid{i}", M["reg_lid"], M["reg_margin"], M["reg_socket"], M["reg_lower"], e)
        eyes.append({"e": e, "ball": ball, "lid": lid, "x": x, "z": z, "open": -1.0, "gz": 0.0,
                     "wide": float(jit.uniform(0.92, 1.05))})
    reg = {"root": root, "body": body, "rest": rest, "info": info, "eyes": eyes, "scale": scale, "mouth": mouth,
           "tail": tail}
    set_lids(reg, [0.0] * len(eyes))
    ctx[name] = reg
    return reg


def set_lids(reg, opens):
    """Each eye's lids, 0 (shut) to 1 (open): the lid sheet takes its almond for that opening and gaze."""
    for k, e in enumerate(reg["eyes"]):
        o = max(0.0, min(1.0, opens[k]))
        key = (round(o, 4), round(e["gz"], 3))
        if e.get("key") == key:
            continue
        e["key"], e["open"] = key, o
        me = e["lid"].data
        me.vertices.foreach_set("co", lid_coords(o, e["gz"], e["wide"]).astype(np.float32).ravel())
        me.update()


def aim_eyes(reg, target):
    """Every open eye turns to the same point (world), within how far an eyeball turns in its lids."""
    bpy.context.view_layer.update()
    for e in reg["eyes"]:
        mw = e["e"].matrix_world
        loc = mw.inverted() @ V(target)
        d = loc.normalized()
        ang = d.angle(V((0, 1, 0)))
        if ang > EYE_MAX:
            axis = V((0, 1, 0)).cross(d).normalized()
            d = (Matrix.Rotation(EYE_MAX, 3, axis) @ V((0, 1, 0))).normalized()
        e["ball"].rotation_euler = d.to_track_quat("Y", "Z").to_euler()
        e["gz"] = float(d.z)


def pose_regular(reg, at, yaw=0.0, roll=0.0, pitch=0.0, press=0.0, t=0.0, ripple=0.12, hidden=False):
    """Put the Regular (or the pup) at `at`, tilted like a kite (yaw, roll, pitch in degrees), its rim rippling in
    one wave that travels round it, and with press > 0 its front flattened against the acrylic (only on the tank
    side: it never crosses the glass)."""
    root = reg["root"]
    for ob in [root] + list(root.children_recursive):
        ob.hide_render = hidden
    if hidden:
        return
    sc = reg["scale"]
    root.location = at
    root.rotation_euler = (math.radians(pitch), math.radians(roll), math.radians(yaw))
    rest, info = reg["rest"], reg["info"]
    r, th, side = info[:, 0], info[:, 1], info[:, 2]
    w = np.clip((r - 0.62) / 0.38, 0, 1) ** 1.6
    wave = ripple * w * np.sin(2 * th - 2.1 * t) + 0.35 * ripple * w * np.sin(5 * th + 3.3 * t + 1.0)
    v = rest.copy()
    v[:, 1] += wave
    if press > 0:
        bpy.context.view_layer.update()
        Mw = np.array(root.matrix_world)
        lim = GLASS_FACE - 0.004 - MOUND * sc
        hom = np.c_[v, np.ones(len(v))]
        wv = hom @ Mw.T
        over = wv[:, 1] > lim
        wv[over, 1] = lim + (wv[over, 1] - lim) * 0.03
        v = (wv @ np.linalg.inv(Mw).T)[:, :3]
    me = reg["body"].data
    me.vertices.foreach_set("co", v.astype(np.float32).ravel())
    me.update()
    # the eyes ride the front: each lid's centre sits SINK under the skin there (flattened where it presses)
    bpy.context.view_layer.update()
    Mw = root.matrix_world
    inv = Mw.inverted()
    for e in reg["eyes"]:
        p = V((e["x"], front_y(e["x"], e["z"]) - SINK, e["z"]))
        if press > 0:
            wp = Mw @ p
            lim = GLASS_FACE - 0.004 - (LID_R * e["e"].scale[0] + 0.01) * sc
            if wp.y > lim:
                wp.y = lim
            p = inv @ wp
        e["e"].location = p


def no_glints(kit, light_names, objs):
    """Light linking: these lights still light everything and glint off skin and eyes, but the acrylic doesn't
    receive them, so a hall lamp never shows as a bright patch in the glass."""
    col = bpy.data.collections.get("no glints") or bpy.data.collections.new("no glints")
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = "EXCLUDE"
    for nm in light_names:
        L = kit.LIGHTS[nm]["obj"]
        L.light_linking.receiver_collection = col
        L.visible_glossy = True


def link_lights(kit, coll, light_names, objs, state, glossy=True):
    """Light linking: these lights light only `objs` (INCLUDE) or everything but them (EXCLUDE)."""
    col = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = state
    for nm in light_names:
        L = kit.LIGHTS[nm]["obj"]
        L.light_linking.receiver_collection = col
        L.visible_glossy = glossy


# ------------------------------------------------------------------------------------------------ test build


def build_glass(kit, ctx, M):
    """The acrylic wall: one thick slab in a dark steel frame with black silicone seams."""
    w, h = GLASS_X1 - GLASS_X0, GLASS_Z1 - GLASS_Z0
    cx, cz = (GLASS_X0 + GLASS_X1) / 2, (GLASS_Z0 + GLASS_Z1) / 2
    ctx["glass"] = kit.box("acrylic", (w, ACRYLIC_T, h), (cx, -ACRYLIC_T / 2, cz), M["acrylic"])
    fr = 0.22
    for nm, size, loc in (("frame top", (w + 2 * fr, ACRYLIC_T + 0.1, fr), (cx, -ACRYLIC_T / 2, GLASS_Z1 + fr / 2)),
                          ("frame bot", (w + 2 * fr, ACRYLIC_T + 0.1, fr), (cx, -ACRYLIC_T / 2, GLASS_Z0 - fr / 2)),
                          ("frame l", (fr, ACRYLIC_T + 0.1, h), (GLASS_X0 - fr / 2, -ACRYLIC_T / 2, cz)),
                          ("frame r", (fr, ACRYLIC_T + 0.1, h), (GLASS_X1 + fr / 2, -ACRYLIC_T / 2, cz))):
        kit.box(nm, size, loc, M["steel_dark"], bevel=0.02)
    for nm, size, loc in (("seam top", (w, 0.02, 0.025), (cx, 0.006, GLASS_Z1 - 0.012)),
                          ("seam bot", (w, 0.02, 0.025), (cx, 0.006, GLASS_Z0 + 0.012))):
        kit.box(nm, size, loc, M["silicone"])


def _wbox(kit, name, lo, hi, mat, parent=None, bevel=0.0):
    """A box from its world corners, its object space the world's (so tiles and boards line up)."""
    c = tuple((a + b) / 2 for a, b in zip(lo, hi))
    sz = tuple(b - a for a, b in zip(lo, hi))
    ob = kit.mesh_obj(name, kit.box_verts(*sz, c), kit.BOX_FACES, mat, parent)
    if bevel:
        m = ob.modifiers.new("bevel", "BEVEL")
        m.width = bevel
        m.segments = 2
    return ob


def build_hall(kit, ctx, M):
    """The hall: the floor, the tiled and concrete walls round the acrylic, the ceiling with its display lights
    and the hatch, two pillars, the handrail, the door to the corridor."""
    T = 0.25                                                    # wall thickness
    _wbox(kit, "hall floor", (HX0 - T, -ACRYLIC_T, -0.3), (HX1 + T, HY1 + T, 0.0), M["floor"])
    _wbox(kit, "hall ceiling", (HX0 - T, -ACRYLIC_T, CEIL), (HX1 + T, HY1 + T, ROOF_Z), M["ceiling"])
    # the glass wall's surround (y = -ACRYLIC_T .. 0): concrete either side, above and below the acrylic
    fx0, fx1 = GLASS_X0 - 0.22, GLASS_X1 + 0.22
    _wbox(kit, "glass wall l", (HX0, -ACRYLIC_T - 0.05, 0), (fx0, 0.0, CEIL), M["concrete"])
    _wbox(kit, "glass wall r", (fx1, -ACRYLIC_T - 0.05, 0), (HX1, 0.0, CEIL), M["concrete"])
    _wbox(kit, "glass wall top", (fx0, -ACRYLIC_T - 0.05, GLASS_Z1 + 0.22), (fx1, 0.0, CEIL), M["concrete"])
    _wbox(kit, "glass plinth", (fx0, -ACRYLIC_T - 0.05, 0), (fx1, 0.0, GLASS_Z0 - 0.22), M["tile"])
    # the back and side walls: tile to 1.2 m, concrete above, with the corridor's door in the back wall
    dx0, dx1, dh = COR_X - 0.6, COR_X + 0.6, 2.3
    for nm, lo, hi in (("back l", (HX0, HY1, 0), (dx0, HY1 + T, CEIL)), ("back r", (dx1, HY1, 0), (HX1, HY1 + T, CEIL)),
                       ("back top", (dx0, HY1, dh), (dx1, HY1 + T, CEIL)),
                       ("side l", (HX0 - T, -ACRYLIC_T, 0), (HX0, HY1 + T, CEIL)),
                       ("side r", (HX1, -ACRYLIC_T, 0), (HX1 + T, HY1 + T, CEIL))):
        _wbox(kit, "wall " + nm, lo, hi, M["concrete"])
    TH = 1.2
    for nm, lo, hi in (("back l", (HX0, HY1 - 0.02, 0), (dx0, HY1, TH)), ("back r", (dx1, HY1 - 0.02, 0), (HX1, HY1, TH)),
                       ("side l", (HX0, -0.0, 0), (HX0 + 0.02, HY1, TH)), ("side r", (HX1 - 0.02, 0.0, 0), (HX1, HY1, TH))):
        _wbox(kit, "tile " + nm, lo, hi, M["tile"])
    for k, (px, py) in enumerate(PILLARS):
        _wbox(kit, f"pillar{k}", (px - 0.3, py - 0.3, 0), (px + 0.3, py + 0.3, CEIL), M["concrete"])
        _wbox(kit, f"pillar tile{k}", (px - 0.31, py - 0.31, 0), (px + 0.31, py + 0.31, TH), M["tile"])
    # the handrail: one brushed tube on posts, waist high along the glass
    kit.cyl("rail", 0.03, GLASS_X1 - GLASS_X0 - 0.4, (0, RAIL_Y, RAIL_Z), M["steel"], rot=(0, math.pi / 2, 0), n=14)
    for k in range(7):
        x = GLASS_X0 + 0.2 + k * (GLASS_X1 - GLASS_X0 - 0.4) / 6
        kit.cyl(f"rail post{k}", 0.025, RAIL_Z, (x, RAIL_Y, RAIL_Z / 2), M["steel"], n=10)
    # the display lights: one row of recessed square panels over the hall, pale and cool
    ctx["panels"] = []
    for k in range(8):
        x = -6.1 + k * (12.2 / 7)
        kit.box(f"panel trim{k}", (0.72, 0.72, 0.04), (x, 1.9, CEIL - 0.015), M["steel_dark"])
        ctx["panels"].append(kit.plane(f"panel{k}", (0.6, 0.6), (x, 1.9, CEIL - 0.04), M["panel_rest"],
                                       rot=(math.pi, 0, 0)))
    # the hatch: a square steel plate set in the ceiling, its hinge line on one side, no handle on our side
    hx, hy = HATCH
    kit.box("hatch frame", (HATCH_W + 0.14, HATCH_W + 0.14, 0.05), (hx, hy, CEIL - 0.02), M["steel_dark"])
    kit.box("hatch", (HATCH_W, HATCH_W, 0.05), (hx, hy, CEIL - 0.035), M["steel_hatch"], bevel=0.01)
    kit.cyl("hatch hinge", 0.02, HATCH_W - 0.1, (hx, hy + HATCH_W / 2 - 0.03, CEIL - 0.065), M["steel_dark"],
            rot=(0, math.pi / 2, 0), n=10)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"hatch bolt{sx}{sy}", 0.018, 0.02, (hx + sx * 0.42, hy + sy * 0.42, CEIL - 0.065), M["steel_dark"], n=8)
    # the light switch by the corridor door (a plain plate, two rockers, no text)
    kit.box("switch plate", (0.16, 0.02, 0.26), (dx0 - 0.35, HY1 - 0.01, 1.35), M["switch"], bevel=0.01)
    for k in range(2):
        kit.box(f"switch{k}", (0.05, 0.03, 0.09), (dx0 - 0.38 + k * 0.06, HY1 - 0.03, 1.35), M["switch"], bevel=0.008)
    # a floor drain
    kit.cyl("drain", 0.14, 0.01, (0.6, 3.2, 0.003), M["steel_dark"], n=24)


def bench(kit, name, x, y, z, yaw, wood, metal):
    """A plain wooden bench (three slats on two steel frames), facing -y at yaw 0."""
    root = kit.empty(name, (x, y, z), rot=(0, 0, math.radians(yaw)))
    for k in range(3):
        kit.box(f"{name} slat{k}", (1.9, 0.12, 0.05), (0, -0.14 + k * 0.14, 0.45), wood, root, bevel=0.012)
    for k in range(2):     # the backrest, so a bench plainly faces one way
        kit.box(f"{name} back{k}", (1.9, 0.04, 0.12), (0, 0.24, 0.62 + k * 0.17), wood, root, bevel=0.012)
    for sx in (-1, 1):
        kit.box(f"{name} leg{sx}", (0.05, 0.4, 0.42), (sx * 0.8, 0, 0.21), metal, root, bevel=0.01)
        kit.box(f"{name} upright{sx}", (0.05, 0.04, 0.48), (sx * 0.8, 0.25, 0.66), metal, root, bevel=0.01)
    return root


def build_props(kit, ctx, M):
    for k, (bx, by) in enumerate(BENCHES_HALL):
        bench(kit, f"hall bench{k}", bx, by, 0.0, 0, M["wood"], M["steel_dark"])
    # the mop bucket on castors with its wringer: the one warm colour in the hall
    b = kit.empty("bucket", (3.3, 1.6, 0.0))
    kit.box("bucket body", (0.55, 0.4, 0.36), (0, 0, 0.26), M["yellow"], b, bevel=0.05)
    kit.box("bucket wringer", (0.24, 0.36, 0.2), (0.14, 0, 0.52), M["yellow"], b, bevel=0.03)
    kit.box("bucket water", (0.36, 0.34, 0.02), (-0.08, 0, 0.42), kit.glass("#7f9a9a"), b)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"castor{sx}{sy}", 0.035, 0.03, (sx * 0.22, sy * 0.15, 0.04), M["rubber"], b, rot=(0, math.pi / 2, 0), n=12)
    kit.cyl("bucket handle", 0.012, 0.9, (0.14, 0, 0.95), M["steel"], b, n=8)
    ctx["bucket"] = b
    # a plain yellow wet-floor cone (no text)
    kit.cyl("cone", 0.16, 0.6, (-4.6, 1.5, 0.3), M["yellow"], n=4, r2=0.03)
    kit.box("cone base", (0.34, 0.34, 0.03), (-4.6, 1.5, 0.015), M["yellow"])
    # a spare mop leaning on a pillar
    mop(kit, "spare mop", M, None, (3.25, 3.28, 1.0), rot=(math.radians(-10), math.radians(6), 0))


def mop(kit, name, M, parent, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0):
    """A mop: a 1.4 m steel handle and a grey strand head. Its origin is where a hand grips it, 0.45 m from the
    top; the head is down its -z."""
    root = kit.empty(name, loc, parent, rot=rot)
    root.scale = (scale,) * 3
    kit.cyl(f"{name} handle", 0.016, 1.4, (0, 0, -0.25), M["steel"], root, n=10)
    kit.box(f"{name} head", (0.36, 0.1, 0.12), (0, 0, -0.95), M["mop"], root, bevel=0.04)
    return root


def build_corridor(kit, ctx, M):
    """The service corridor: cream tile, pipes on the ceiling, a deep steel mop sink, three tabards on hooks, one
    caged light, the steel door into the hall (with a round clear porthole) and a plain one at the far end."""
    x0, x1 = COR_X - COR_W / 2, COR_X + COR_W / 2
    y0, y1 = HY1 + 0.25, HY1 + 0.25 + COR_L
    _wbox(kit, "cor floor", (x0, y0, -0.3), (x1, y1, 0.0), M["floor"])
    _wbox(kit, "cor ceiling", (x0, y0, COR_H), (x1, y1, COR_H + 0.25), M["ceiling"])
    _wbox(kit, "cor wall l", (x0 - 0.2, y0, 0), (x0, y1, COR_H), M["ctile"])
    _wbox(kit, "cor wall r", (x1, y0, 0), (x1 + 0.2, y1, COR_H), M["ctile"])
    _wbox(kit, "cor end", (x0, y1, 0), (x1, y1 + 0.2, COR_H), M["ctile"])
    kit.box("cor end door", (0.95, 0.06, 2.1), (COR_X, y1 - 0.03, 1.05), M["door"], bevel=0.01)
    for k, (dx, dz, r) in enumerate(((0.45, COR_H - 0.12, 0.05), (0.25, COR_H - 0.1, 0.035), (-0.5, COR_H - 0.14, 0.06))):
        kit.cyl(f"pipe{k}", r, COR_L, (COR_X + dx, (y0 + y1) / 2, dz), M["pipe"], rot=(math.pi / 2, 0, 0), n=12)
    # the mop sink (left wall) and the hooks with our three tabards (right wall)
    sk = kit.empty("sink", (x0 + 0.3, y0 + 3.2, 0))
    kit.box("sink basin", (0.55, 0.7, 0.35), (0, 0, 0.62), M["steel"], sk, bevel=0.02)
    kit.box("sink stand", (0.5, 0.6, 0.45), (0, 0, 0.22), M["steel_dark"], sk)
    kit.cyl("tap", 0.02, 0.3, (-0.18, 0, 1.0), M["steel"], sk, n=8)
    for k in range(3):
        hy = y0 + 1.6 + k * 0.45
        kit.cyl(f"hook{k}", 0.012, 0.1, (x1 - 0.05, hy, 1.75), M["steel"], rot=(0, math.pi / 2, 0), n=6)
        kit.box(f"hung tabard{k}", (0.04, 0.42, 0.75), (x1 - 0.06, hy, 1.35), M["tabard"], bevel=0.02)
    # the one light: a bulb in a wire cage, steady and cold
    lc = (COR_X, y0 + 4.5, COR_H - 0.18)
    kit.sphere("cor bulb", 0.05, lc, M["bulb"], seg=12)
    for k in range(4):
        kit.box(f"cage{k}", (0.008, 0.008, 0.16), (lc[0] + 0.07 * math.cos(k * math.pi / 2), lc[1] + 0.07 * math.sin(k * math.pi / 2), lc[2]),
                M["cage"])
    kit.light("corridor", "POINT", (lc[0], lc[1], lc[2] - 0.08), 70.0, "#dfe8ff", size=0.05)
    # the door into the hall, hinged on its left edge, with a round clear porthole
    hinge = kit.empty("hall door", (COR_X - 0.58, HY1 + 0.1, 0.0))
    leaf = kit.box("hall door leaf", (1.14, 0.06, 2.25), (0.57, 0, 1.125), M["door"], hinge, bevel=0.01)
    kit.cyl("porthole rim", 0.19, 0.08, (0.57, 0, 1.55), M["steel_dark"], hinge, rot=(math.pi / 2, 0, 0), n=28)
    kit.cyl("porthole", 0.16, 0.085, (0.57, 0, 1.55), M["porthole"], hinge, rot=(math.pi / 2, 0, 0), n=28)
    kit.box("door push plate", (0.12, 0.08, 0.3), (1.0, -0.04, 1.05), M["steel"], hinge, bevel=0.01)
    ctx["door"] = hinge


def build_tank(kit, ctx, M, rng):
    """The water side: sand, the rock wall round the hall's box, the box's outside and roof with the keepers' hatch,
    the rail and two benches facing it, kelp, god rays."""
    _wbox(kit, "sand", (-40, -45, TANK_Z - 0.3), (40, -ACRYLIC_T - 0.05, TANK_Z), M["sand"])
    # sand mounds, so the floor isn't a table top
    for k in range(14):
        x, y = float(rng.uniform(-14, 14)), float(rng.uniform(-30, -3))
        s_ = kit.sphere(f"dune{k}", 1.0, (x, y, TANK_Z - 0.75), M["sand"], seg=16)
        s_.scale = (float(rng.uniform(2, 4)), float(rng.uniform(1.5, 3)), 0.9)
    # the box's front below the glass and its sides and roof where it sticks out of the rock (y 0 .. BOX_D)
    _wbox(kit, "box plinth", (HX0 - 0.25, -ACRYLIC_T - 0.06, TANK_Z - 0.1), (HX1 + 0.25, -ACRYLIC_T - 0.05, 0.02),
          M["box_out"])
    _wbox(kit, "box front l", (HX0 - 0.25, -ACRYLIC_T - 0.07, 0), (GLASS_X0 - 0.22, -ACRYLIC_T - 0.05, ROOF_Z), M["box_out"])
    _wbox(kit, "box front r", (GLASS_X1 + 0.22, -ACRYLIC_T - 0.07, 0), (HX1 + 0.25, -ACRYLIC_T - 0.05, ROOF_Z), M["box_out"])
    _wbox(kit, "box front top", (GLASS_X0 - 0.22, -ACRYLIC_T - 0.07, GLASS_Z1 + 0.22), (GLASS_X1 + 0.22, -ACRYLIC_T - 0.05, ROOF_Z),
          M["box_out"])
    _wbox(kit, "box roof", (HX0 - 0.25, -ACRYLIC_T - 0.07, ROOF_Z), (HX1 + 0.25, BOX_D, ROOF_Z + 0.04), M["box_out"])
    _wbox(kit, "box side l", (HX0 - 0.3, -ACRYLIC_T - 0.07, TANK_Z), (HX0 - 0.25, BOX_D, ROOF_Z), M["box_out"])
    _wbox(kit, "box side r", (HX1 + 0.25, -ACRYLIC_T - 0.07, TANK_Z), (HX1 + 0.3, BOX_D, ROOF_Z), M["box_out"])
    # the keepers' hatch on the roof: the same square, seen from its own side, with a hinge and a wheel to open it
    hx, hy = HATCH
    kit.box("hatch top", (HATCH_W + 0.1, HATCH_W + 0.1, 0.08), (hx, hy, ROOF_Z + 0.08), M["hatch_out"], bevel=0.02)
    kit.cyl("hatch wheel", 0.22, 0.04, (hx, hy, ROOF_Z + 0.2), M["hatch_out"], n=20)
    kit.cyl("hatch wheel hub", 0.05, 0.1, (hx, hy, ROOF_Z + 0.16), M["hatch_out"], n=10)
    kit.cyl("hatch hinge top", 0.05, HATCH_W, (hx, hy + HATCH_W / 2 + 0.03, ROOF_Z + 0.1), M["hatch_out"],
            rot=(0, math.pi / 2, 0), n=12)
    # the rock wall the box is set into: big blocky stones, a face at y = BOX_D, round the box and over it
    k = 0
    for gx in np.arange(-22, 22.1, 1.6):
        for gz in np.arange(TANK_Z, 16, 1.5):
            inside = abs(gx) < HX1 + 0.6 and gz < ROOF_Z + 0.2
            if inside:
                continue
            sx, sz = float(rng.uniform(1.4, 2.4)), float(rng.uniform(1.2, 2.2))
            yy = BOX_D + float(rng.uniform(-0.6, 0.5)) + 0.4 * max(0.0, (abs(gx) - 12) / 6)
            kit.box(f"rock{k}", (sx, float(rng.uniform(1.2, 2.5)), sz), (float(gx + rng.uniform(-0.3, 0.3)), yy,
                    float(gz + rng.uniform(-0.3, 0.3))), M["rock"] if k % 3 else M["rock2"],
                    rot=tuple(float(v) for v in rng.uniform(-0.25, 0.25, 3)), bevel=0.12)
            k += 1
    # the rock frame: heavier stones round the box's front edges, so from the water it's a lit box framed in rock
    for j in range(16):
        u = j / 15
        for x, z in ((HX0 - 0.9, TANK_Z + u * (ROOF_Z - TANK_Z + 0.6)), (HX1 + 0.9, TANK_Z + u * (ROOF_Z - TANK_Z + 0.6)),
                     (HX0 - 0.6 + u * (HX1 - HX0 + 1.2), ROOF_Z + 0.75)):
            top = z > ROOF_Z    # the top row sits along the back of the roof, so the roof and its hatch show
            kit.box(f"frame rock{j}-{x:.0f}-{z:.0f}", tuple(float(v) for v in rng.uniform(0.9, 1.6, 3)),
                    (x + float(rng.uniform(-0.2, 0.2)), float(rng.uniform(BOX_D - 0.2, BOX_D + 0.6)) if top
                     else float(rng.uniform(-0.2, 1.6)), z),
                    M["rock2"], rot=tuple(float(v) for v in rng.uniform(-0.3, 0.3, 3)), bevel=0.1)
    # boulders on the sand in front, and the audience's rail and benches facing the box
    for j in range(10):
        x = float(rng.choice([-1, 1])) * float(rng.uniform(7.5, 13))
        kit.box(f"boulder{j}", tuple(float(v) for v in rng.uniform(0.8, 2.2, 3)), (x, float(rng.uniform(-12, -2)), TANK_Z + 0.3),
                M["rock"], rot=tuple(float(v) for v in rng.uniform(-0.4, 0.4, 3)), bevel=0.15)
    ry = -3.4
    kit.cyl("tank rail", 0.035, 12.0, (0, ry, TANK_Z + 0.95), M["steel_t"], rot=(0, math.pi / 2, 0), n=12)
    for j in range(7):
        kit.cyl(f"tank rail post{j}", 0.03, 0.95, (-6 + j * 2, ry, TANK_Z + 0.475), M["steel_t"], n=8)
    for j, (bx, by) in enumerate(BENCHES_TANK):
        bench(kit, f"tank bench{j}", bx, by, TANK_Z, 180, M["wood_t"], M["steel_t"])
    # kelp: tall dark strands of stacked boxes, swaying (animate)
    ctx["kelp"] = []
    for j, (x, y) in enumerate(((-9.5, -6), (-8.2, -9), (9.0, -7.5), (10.5, -11), (-12, -16), (7, -19), (-5, -24),
                                (13, -21))):
        root = kit.empty(f"kelp{j}", (x, y, TANK_Z))
        segs = []
        parent = root
        for q in range(9):
            seg = kit.empty(f"kelp{j}.{q}", (0, 0, 0.0 if q == 0 else 0.75), parent)
            kit.box(f"kelp{j}.blade{q}", (0.22, 0.06, 0.8), (0, 0, 0.38), M["kelp"], seg, bevel=0.02)
            segs.append(seg)
            parent = seg
        ctx["kelp"].append((segs, j))
    # god rays: faint light falling from the surface
    ctx["rays"] = []
    for j in range(7):
        x = float(rng.uniform(-10, 10))
        y = float(rng.uniform(-22, -3))
        r = kit.plane(f"ray{j}", (1.4, 18.0), (x, y, 7.0), M["ray"], rot=(math.radians(90), 0, math.radians(float(rng.uniform(-30, 30)))))
        r.rotation_euler.rotate_axis("X", math.radians(-14))
        r.visible_shadow = False
        ctx["rays"].append(r)


def build_crowd(kit, ctx, M, rng, n=260):
    """The crowd: one simple flat leaf-shaped silhouette (no eyes, no fins, no colour), instanced, hanging still,
    all facing the hall. They come in order: a cue's "n" says how many are there."""
    me = None
    pts = []
    for k in range(n):
        if k < 70:          # the first ones: scattered far back
            p = (rng.uniform(-11, 11), rng.uniform(-26, -7), rng.uniform(TANK_Z + 0.8, 6.0))
        elif k < 150:       # more each morning, closer
            p = (rng.uniform(-9, 9), rng.uniform(-14, -3), rng.uniform(TANK_Z + 0.6, 5.6))
        else:               # the packed night: right up against the glass, edge to edge
            p = (rng.uniform(-6.5, 6.5), rng.uniform(-3.2, -0.75), rng.uniform(TANK_Z + 0.5, 5.2))
        pts.append(tuple(float(v) for v in p))
    objs = []
    for k, p in enumerate(pts):
        if me is None:
            ob = leaf_mesh(kit, "crowd0", M["crowd"])
            ob.location = p
            me = ob.data
        else:
            ob = bpy.data.objects.new(f"crowd{k}", me)
            kit.link(ob)
            ob.location = p
        L = float(rng.uniform(0.28, 0.5))
        ob.scale = (L, 0.06, L * float(rng.uniform(0.8, 1.15)))
        ob.rotation_euler = (0, float(rng.uniform(-0.25, 0.25)), float(rng.uniform(-0.15, 0.15)))
        objs.append({"ob": ob, "p": p, "ph": float(rng.uniform(0, 6.3))})
    ctx["crowd"] = objs


def build_bubbles(kit, ctx, M, n=170):
    """Bubbles for the applause: one small sphere, instanced, on the water side of the acrylic (animate rolls them)."""
    base = kit.sphere("bubble0", 1.0, (0, -50, -50), M["bubble"], seg=10)
    base.visible_shadow = False
    obs = [base]
    for k in range(1, n):
        ob = bpy.data.objects.new(f"bubble{k}", base.data)
        kit.link(ob)
        ob.location = (0, -50, -50)
        ob.visible_shadow = False
        obs.append(ob)
    ctx["bubbles"] = obs


CAUSTIC_SPOT = (0.0, -6.0, 10.0)


def caustic_light(kit, ctx):
    """The caustics: a spot high over the tank shining down through the acrylic into the hall, through a hidden
    sheet a metre under it whose see-through colour is the bright web of light through moving water (a 4D Voronoi
    edge pattern, two scales; its W moves with time). The sheet's shadow is the crawling caustic on the floor, the
    tile and the cast. Nobody sees the sheet itself."""
    ob = kit.light("caustic", "SPOT", CAUSTIC_SPOT, 9000.0, "#b5f3ec", size=0.0005, spot=70, blend=0.5)
    kit.aim(ob, (0.0, 3.0, 0.0))
    m = kit._new("caustic cookie")
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    N.remove(N["Principled BSDF"])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    tc = N.new("ShaderNodeTexCoord")
    ws = []
    mins = []
    nz = N.new("ShaderNodeTexNoise")          # warp the cells so the web is water, not tiles
    nz.inputs["Scale"].default_value = 9.0
    nz.inputs["Detail"].default_value = 2.0
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    wp = N.new("ShaderNodeVectorMath")
    wp.operation = "MULTIPLY_ADD"
    L.new(nz.outputs["Color"], wp.inputs[0])
    wp.inputs[1].default_value = (0.025, 0.025, 0.025)
    L.new(tc.outputs["Object"], wp.inputs[2])
    for sc in (48.0, 75.0):        # cells a couple of cm on the sheet: about 0.2 m by the time they reach the floor
        vo = N.new("ShaderNodeTexVoronoi")
        vo.voronoi_dimensions = "4D"
        vo.feature = "DISTANCE_TO_EDGE"
        vo.inputs["Scale"].default_value = sc
        L.new(wp.outputs["Vector"], vo.inputs["Vector"])
        ws.append(vo.inputs["W"])
        mins.append(vo)
    mn = N.new("ShaderNodeMath")
    mn.operation = "MINIMUM"
    L.new(mins[0].outputs["Distance"], mn.inputs[0])
    L.new(mins[1].outputs["Distance"], mn.inputs[1])
    rp = N.new("ShaderNodeMapRange")
    rp.inputs["From Min"].default_value = 0.0
    rp.inputs["From Max"].default_value = 0.1
    rp.inputs["To Min"].default_value = 1.0
    rp.inputs["To Max"].default_value = 0.45
    L.new(mn.outputs[0], rp.inputs["Value"])
    cc = N.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        L.new(rp.outputs["Result"], cc.inputs[k])
    tr = N.new("ShaderNodeBsdfTransparent")
    L.new(cc.outputs["Color"], tr.inputs["Color"])
    L.new(tr.outputs[0], out.inputs["Surface"])
    sheet = kit.plane("caustic sheet", (3.2, 3.2), (CAUSTIC_SPOT[0], CAUSTIC_SPOT[1] + 0.35, CAUSTIC_SPOT[2] - 1.0), m)
    sheet.visible_camera = False
    sheet.visible_glossy = False
    ctx["caustic_w"] = ws


def build_lights(kit, ctx):
    # the display lights' real light: four area lights along the panel row
    for k in range(4):
        x = -5.25 + k * 3.5
        kit.light(f"disp{k}", "AREA", (x, 1.9, CEIL - 0.06), 70.0, "#e6f0f5", size=3.2)
        kit.LIGHTS[f"disp{k}"]["obj"].rotation_euler = (0, 0, 0)
        kit.LIGHTS[f"disp{k}"]["light"].shape = "RECTANGLE"
        kit.LIGHTS[f"disp{k}"]["light"].size_y = 0.8
    kit.light("hallfill", "AREA", (0.0, 4.6, CEIL - 0.1), 40.0, "#9fb8c8", size=8.0)
    # the tank's own light from the surface, and a faint blue bounce in the hall from the glass
    kit.light("tanktop", "AREA", (0.0, -10.0, 13.0), 5200.0, "#7cccdf", size=24.0)
    kit.light("glassglow", "AREA", (0.0, 0.25, 2.4), 18.0, "#9cc6d4", size=10.0)
    kit.LIGHTS["glassglow"]["obj"].rotation_euler = (math.radians(90), 0, 0)
    kit.LIGHTS["glassglow"]["light"].shape = "RECTANGLE"
    kit.LIGHTS["glassglow"]["light"].size_y = 4.0
    caustic_light(kit, ctx)
    # the stage: a soft spot from the hall's ceiling onto whatever's pressed to the glass (peak), and the eyes'
    # catch light (an emitter off to the side, seen in the eyes, never in the flat acrylic)
    kit.light("stage", "SPOT", (-1.0, 2.0, 4.85), 0.0, "#f2f6f8", size=0.25, spot=80, blend=0.6)
    kit.aim(kit.LIGHTS["stage"]["obj"], (-1.6, -0.5, 2.6))
    for nm in ("key", "key2"):
        kit.light(nm, "SPOT", (0, 0, 1), 0.0, "#dce8f0", size=0.1, spot=40, blend=0.6)
    # round 2 (P1): the Regular's own key, from below. A long soft strip at the foot of the glass, tilted up into the
    # tank, lighting only the Regular and the pup (light linking), so the hall's ceiling lights never flatten its
    # front and its sockets and rim fall into shadow. A shot can scale it ("underkey" in its look)
    kit.light("underkey", "AREA", (0.0, 0.3, 0.06), 120.0, "#c7dcf0", size=12.0)
    kit.LIGHTS["underkey"]["light"].shape = "RECTANGLE"
    kit.LIGHTS["underkey"]["light"].size_y = 0.25
    kit.aim(kit.LIGHTS["underkey"]["obj"], (0.0, -1.4, 3.0))
    for nm, L in kit.LIGHTS.items():
        L["obj"].visible_glossy = False


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    ctx = {"story": story}
    # light through the acrylic (two faces), a bubble or the breath fog, and back out: more see-through surfaces
    # than kit's 4 on one path, so give it room or the far side goes unlit
    bpy.context.scene.cycles.transparent_max_bounces = 10
    for g in FOGS.values():
        g.clear()
    rng = np.random.default_rng(13)
    M = materials(kit)
    ctx["M"] = M
    build_glass(kit, ctx, M)
    build_hall(kit, ctx, M)
    build_props(kit, ctx, M)
    build_corridor(kit, ctx, M)
    build_tank(kit, ctx, M, rng)
    build_crowd(kit, ctx, M, rng)
    build_bubbles(kit, ctx, M)
    build_regular(kit, ctx, M, "regular", 1.0)
    build_regular(kit, ctx, M, "pup", 0.25)
    bl = kit.plane("fogbloom", (3.0, 2.4), (-1.6, 0.004, 2.5), M["fogbloom"], rot=(math.radians(90), 0, 0))
    bl.visible_shadow = False
    ctx["fogbloom"] = bl
    # the eyes' catch light (round 2, P1): a soft panel high behind the hall cameras, seen only as the wet glint in
    # the corneas, so the speculars are the brightest thing on the Regular
    catch = kit.plane("catch", (1.0, 1.6), (4.6, 2.6, 3.0), emitter(kit, "eye catch", "#eef4f8", 14.0))
    kit.aim(catch, (-1.6, -0.5, 2.8))
    catch.rotation_euler.rotate_axis("X", math.pi)
    catch.visible_camera = False
    catch.visible_shadow = False
    ctx["catch"] = catch
    # round 2 (P1): a small glint-only panel at the hall cameras' height, so the wet corneas carry the brightest
    # point on the Regular without lighting its skin
    glint = kit.plane("glint", (0.3, 0.22), (-0.4, 3.6, 2.2), emitter(kit, "eye glint", "#f4f8fa", 220.0))
    kit.aim(glint, (-1.6, -0.5, 2.8))
    glint.rotation_euler.rotate_axis("X", math.pi)
    for k in ("visible_camera", "visible_shadow", "visible_diffuse", "visible_transmission", "visible_volume_scatter"):
        setattr(glint, k, False)
    ctx["glint"] = glint
    build_lights(kit, ctx)
    # the hall's lamps glint off skin and eyes but never show in the acrylic
    no_glints(kit, ["key", "key2"], [ctx["glass"], bpy.data.objects["porthole"]])
    # round 2 (P1): the hall's ceiling lights (the stage spot, the display lights and the fill) don't reach the
    # Regular or the pup: it's lit from below (underkey) and by each shot's own key
    creature = [o for nm in ("regular", "pup") for o in [ctx[nm]["root"]] + list(ctx[nm]["root"].children_recursive)
                if o.type == "MESH"]
    link_lights(kit, "no fill", ["stage", "disp0", "disp1", "disp2", "disp3", "hallfill", "tanktop"],
                [ctx["glass"], bpy.data.objects["porthole"]] + creature, "EXCLUDE", glossy=True)
    link_lights(kit, "creature only", ["underkey"], creature, "INCLUDE", glossy=False)
    eyes = [e["ball"] for nm in ("regular", "pup") for e in ctx[nm]["eyes"]]
    col = bpy.data.collections.new("eyes only")
    for ob in eyes:
        col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = "INCLUDE"
    ctx["glint"].light_linking.receiver_collection = col
    # each creature carries its own soft key from below and in front (it lights only itself), so wherever it hangs
    # in the tank its front is keyed from below, never flat from above; a shot scales it ("regularkey", "pupkey")
    for nm, base in (("regular", 45.0), ("pup", 6.0)):
        root = ctx[nm]["root"]
        ob = kit.light(f"{nm}key", "AREA", (0.0, 2.4, -2.4), base, "#c9ddf0", size=2.5, parent=root)
        ob.rotation_euler = (V((0.0, 0.0, 0.4)) - V((0.0, 2.4, -2.4))).to_track_quat("-Z", "Y").to_euler()
        ob.visible_glossy = False
        ob.visible_camera = False
        own = [o for o in [root] + list(root.children_recursive) if o.type == "MESH"]
        link_lights(kit, f"{nm} only", [f"{nm}key"], own, "INCLUDE", glossy=False)
    kit.LIGHTS["underkey"]["obj"].visible_camera = False
    # the ceiling's glowing panels are mesh lights: they mustn't light or glare on the Regular either
    nofill = bpy.data.collections["no fill"]
    for ob in ctx["panels"]:
        ob.light_linking.receiver_collection = nofill
    ctx["extras_done"] = False
    return ctx


# ------------------------------------------------------------------------------------------------ animate


def _ease_cue(cs, attr, t, default, dur_key="dur"):
    """A value that eases from the cue before to each cue's value over the cue's dur."""
    v = default
    for c in cs:
        if attr not in c or c["t"] > t + 1e-9:
            continue
        d = c.get(dur_key, 0.0)
        u = 1.0 if d <= 0 else _ss((t - c["t"]) / d)
        v = v + (c[attr] - v) * u
    return v


def _glide(cs, t):
    """The Regular's (or pup's) state at t: the last cue's, gliding smoothly from it to the next if that one says
    "glide" (eased at both ends: it's an animal, never a jump)."""
    if not cs:
        return None
    cur = None
    for i, c in enumerate(cs):
        if c["t"] <= t + 1e-9:
            cur = i
    if cur is None:
        return None
    a = cs[cur]
    st = {k: a.get(k) for k in ("pos", "yaw", "roll", "pitch", "press", "ripple", "hidden")}
    nxt = cs[cur + 1] if cur + 1 < len(cs) else None
    if nxt is not None and nxt.get("glide") and not nxt.get("hidden") and not a.get("hidden"):
        u = (t - a["t"]) / max(1e-6, nxt["t"] - a["t"])
        u = u * u * (3 - 2 * u)
        for k in ("yaw", "roll", "pitch", "press"):
            st[k] = (a.get(k) or 0.0) + ((nxt.get(k) or 0.0) - (a.get(k) or 0.0)) * u
        st["pos"] = [a["pos"][i] + (nxt["pos"][i] - a["pos"][i]) * u for i in range(3)]
        st["moving"] = math.hypot(nxt["pos"][0] - a["pos"][0], nxt["pos"][1] - a["pos"][1]) > 0.05
    return st


def person_head(tl, who, t, story=None):
    from blocky import acting

    s = acting.state(tl, who, t)
    keys = tl["acting"].get(who, [])
    bow = math.radians(acting._held(keys, "bow", t, 0.0))
    h = 1.55 * ((story or {}).get("cast", {}).get(who, {}).get("height", 1.0))
    return V((s["x"] + math.sin(s["yaw"]) * math.sin(bow) * 0.9, s["y"] - math.cos(s["yaw"]) * math.sin(bow) * 0.9,
              s["z"] + h * (0.45 + 0.55 * math.cos(bow))))


def cam_now(story, tl, t):
    import __main__

    shot = _shot(tl, t)
    spec = next(s for s in story["shots"] if s["id"] == shot["id"])
    if hasattr(__main__, "cam_at"):
        return V(__main__.cam_at(spec, shot, t, None, tl)[0])
    return V(spec["cam"][0][1])


def _look_point(story, tl, t, look):
    if isinstance(look, (list, tuple)):
        return V(look)
    if isinstance(look, str) and look.startswith("hand:"):     # someone's right hand (the waving one)
        ob = bpy.data.objects.get(f"{look[5:]}.arm1")
        if ob is not None:
            bpy.context.view_layer.update()
            return ob.matrix_world @ V((0.0, 0.0, -1.75))
        look = look[5:]
    if look == "cam":
        return cam_now(story, tl, t)
    return person_head(tl, look, t, story)


BLINK_SLOT = 0.45
BLINK_ORDER = [3, 8, 0, 6, 2, 9, 5, 1, 7, 4]


def eye_opens(tl, name, t, n, kit=None):
    """Every lid's opening at t from the "eyes" cues: shut, opening one after another (order, every), open with a
    slow ripple of single blinks (never two together), closing one after another, or two cracked open briefly."""
    cs = _cues(tl, name)
    opens = [0.0] * n
    look = "me"
    for c in cs:
        if c["t"] > t + 1e-9:
            break
        look = c.get("look", look)
        order = c.get("order", list(range(n)))
        if order == "rows":       # top to bottom down both rows: left and right together, row by row (a little apart)
            order = [k for r in range(5) for k in (r, 5 + r)]
        every = c.get("every", 0.22)
        dur = c.get("open_dur", 0.28)
        st = c.get("state", "open")
        for j, k in enumerate(order):
            if k >= n:
                continue
            t0 = c["t"] + j * every
            u = _ss((t - t0) / dur)
            if st == "open":
                opens[k] = max(opens[k], u) if t >= t0 else opens[k]
            elif st == "shut":
                opens[k] = opens[k] * (1 - u) if t >= t0 else opens[k]
            elif st == "blinkwave":     # one blink each, one eye after another
                x = t - t0
                if 0 <= x <= 0.3:
                    opens[k] *= 1 - max(0.0, math.sin(math.pi * x / 0.3)) ** 0.7
            elif st == "crack":
                d = c.get("hold", 0.9)
                x = t - t0
                if 0 <= x <= d + 0.25:
                    a = _ss(x / 0.12) * (1 - _ss((x - d) / 0.22))
                    opens[k] = max(opens[k], c.get("amount", 0.55) * a)
    # blinks: each open eye blinks on its own slow clock, offset so they ripple across the front, never together
    blink_on = _switch(cs, "blink", t, True)
    if blink_on:
        # one blink slot every BLINK_SLOT s, handed to the next eye in a shuffled order (some slots skipped), and a
        # blink lasts less than a slot: so they ripple across the front and two never close at once
        slot = int(math.floor(t / BLINK_SLOT))
        ph = max(0.0, t - slot * BLINK_SLOT)
        if ph < 0.3 and kit.hash01(slot, 7) < 0.7:
            k = BLINK_ORDER[slot % len(BLINK_ORDER)] % n
            if opens[k] >= 0.5:
                opens[k] *= 1 - max(0.0, math.sin(math.pi * ph / 0.3)) ** 0.7
    return opens, look


def place_creature(kit, story, tl, t, ctx, name):
    reg = ctx[name]
    st = _glide(_cues(tl, name), t)
    if st is None or st.get("hidden"):
        pose_regular(reg, (0, -60, 0), hidden=True)
        return None
    rip = st.get("ripple")
    if rip is None:
        rip = 0.16 if st.get("moving") else 0.07
    pose_regular(reg, st["pos"], st.get("yaw") or 0.0, st.get("roll") or 0.0, st.get("pitch") or 0.0,
                 st.get("press") or 0.0, t, rip)
    opens, look = eye_opens(tl, f"{name}_eyes" if name != "regular" else "eyes", t, len(reg["eyes"]), kit)
    aim_eyes(reg, _look_point(story, tl, t, look))
    set_lids(reg, opens)
    return st


def _extras(kit, story, tl, ctx):
    """The cast's extras, added once (the cast is built after the set): each tabard's back panel, Rosa's keys,
    and a mop for anyone whose acting says "mop"."""
    M = ctx["M"]
    for who in story.get("cast", {}):
        tor = bpy.data.objects.get(f"{who}.torso")
        if tor is None:
            continue
        kit.box(f"{who}.tabard back", (1.6, 0.06, 2.3), (0, 0.53, 0.85), M["tabard"], tor, bevel=0.03)
        for sx in (-1, 1):
            kit.box(f"{who}.tabard strap{sx}", (0.3, 1.08, 0.08), (sx * 0.55, 0, 1.97), M["tabard"], tor, bevel=0.02)
        arm = bpy.data.objects.get(f"{who}.arm1")
        if arm is not None:
            sc = story["cast"][who].get("height", 1.0) * rig.S
            m = mop(kit, f"{who}.mop", M, arm, (0, -0.15, -1.7), rot=(math.radians(-60), 0, 0), scale=1 / sc)
            ctx.setdefault("mops", {})[who] = m
    tor = bpy.data.objects.get("rosa.torso")
    if tor is not None:
        ring = kit.empty("rosa.keys", (-1.05, -0.45, 0.25), tor)
        for k in range(5):
            kit.box(f"rosa.key{k}", (0.09, 0.05, 0.32), (0.08 * (k - 2), 0, -0.12 - 0.03 * abs(k - 2)), M["steel"], ring,
                    rot=(0, 0.25 * (k - 2), 0), bevel=0.01)
        kit.cyl("rosa.keyring", 0.12, 0.03, (0, 0, 0.05), M["steel"], ring, rot=(math.pi / 2, 0, 0), n=14)
    ctx["extras_done"] = True


LIGHT_STATES = {"rest": (0.5, 1.0, 0.0), "stuck": (1.5, 0.55, 1.0), "dark": (0.06, 0.6, 0.0)}


def animate(kit, story, tl, t, ctx):
    from blocky import acting as _ac
    from blocky import kit as K

    if not ctx.get("extras_done"):
        _extras(kit, story, tl, ctx)
    over = {}
    shot = _shot(tl, t)["id"]
    # ---- the hall's display lights: dim at rest, stuck bright, fading down like a stage
    cs = _cues(tl, "lights")
    st0 = "rest"
    gain, caus, stage = LIGHT_STATES["rest"]
    for c in cs:
        if c["t"] > t + 1e-9:
            break
        tgt = LIGHT_STATES[c["state"]]
        d = c.get("dur", 0.0)
        u = 1.0 if d <= 0 else _ss((t - c["t"]) / d)
        gain = gain + (tgt[0] - gain) * u
        caus = caus + (tgt[1] - caus) * u
        stage = stage + (tgt[2] - stage) * u
        st0 = c["state"]
    for k in range(4):
        over[f"disp{k}"] = gain
    over["hallfill"] = 0.5 + 0.5 * gain
    M = ctx["M"]
    pe = next(n for n in M["panel_rest"].node_tree.nodes if n.bl_idname == "ShaderNodeEmission")
    pe.inputs["Strength"].default_value = 6.0 * max(0.05, gain)
    over["caustic"] = caus
    over["stage"] = stage
    K.LIGHTS["stage"]["base"] = 340.0
    for k, w in enumerate(ctx["caustic_w"]):
        w.default_value = t * (0.16 + 0.07 * k)
    # ---- the tank's blue: thinner for the reveal and the far looks (a story key per shot)
    dens = story.get("tank_fog", {}).get(shot, TANK_FOG["density"])
    rdens = story.get("reg_fog", {}).get(shot, dens)
    for mul, sub, fog in FOGS["tank"]:
        mul.inputs[1].default_value = -dens
    for mul, sub, fog in FOGS["reg"]:
        mul.inputs[1].default_value = -rdens
    edens = story.get("eye_fog", {}).get(shot, rdens)     # the rows can stay out of the blue the outline sinks into
    for mul, sub, fog in FOGS["eyes"]:
        mul.inputs[1].default_value = -edens
    hf = story.get("hall_fog", {}).get(shot, 0.0)     # the hall seen from out in the water takes the blue too
    for mul, sub, fog in FOGS["hall"]:
        mul.inputs[1].default_value = -hf
    # ---- the crowd: how many are there, a slow drift in depth only
    n = int(_switch(_cues(tl, "crowd"), "n", t, 60))
    n = int(story.get("crowd_n", {}).get(shot, n))
    clear = float(story.get("crowd_clear", {}).get(shot, 0.0))
    camp = cam_now(story, tl, t) if clear else None
    for k, c in enumerate(ctx["crowd"]):
        ob = c["ob"]
        vis = k < n and (camp is None or (V(c["p"]) - camp).length > clear)
        ob.hide_render = not vis
        if vis:
            x, y, z = c["p"]
            ob.location = (x, y + 0.12 * math.sin(0.23 * t + c["ph"]), z + 0.03 * math.sin(0.4 * t + c["ph"]))
    # ---- kelp sways, god rays shimmer
    for segs, j in ctx["kelp"]:
        for q, seg in enumerate(segs):
            seg.rotation_euler = (0.05 * math.sin(0.7 * t + j + q * 0.5), 0.07 * math.sin(0.5 * t + j * 1.3 + q * 0.4), 0)
    g = next(n for n in M["ray"].node_tree.nodes if n.name == "gain")
    g.inputs[1].default_value = 0.1 + 0.03 * math.sin(0.8 * t)
    # ---- the corridor door
    op = _ease_cue(_cues(tl, "door"), "open", t, 0.0)
    ctx["door"].rotation_euler = (0, 0, math.radians(-95.0) * op)
    # ---- the fog bloom where it presses
    fb = _ease_cue(_cues(tl, "fogbloom"), "amount", t, 0.0)
    a = next(n for n in M["fogbloom"].node_tree.nodes if n.name == "amount")
    a.inputs[1].default_value = fb
    ctx["fogbloom"].hide_render = fb < 0.01
    # ---- bubbles rolling along the glass (applause), or the pup's tiny stream
    bubbles(tl, t, ctx)
    # ---- the Regular and its pup
    info = place_creature(kit, story, tl, t, ctx, "regular")
    place_creature(kit, story, tl, t, ctx, "pup")
    # ---- people: bowing, waving, mops, wiping the rail
    for who, keys in tl["acting"].items():
        tor = bpy.data.objects.get(f"{who}.torso")
        if tor is None:
            continue
        bow = _ac._held(keys, "bow", t, 0.0)
        tor.rotation_euler = (math.radians(bow), 0, 0)
        wv = _ac._held(keys, "wave", t, [0.0, 0.0])
        for sx_, amp in ((-1, wv[0]), (1, wv[1])):
            arm = bpy.data.objects.get(f"{who}.arm{sx_}")
            if arm is not None and amp:
                hz = _ac._held(keys, "wave_hz", t, 1.9)
                arm.rotation_euler.y += math.radians(amp) * math.sin(2 * math.pi * hz * t + (0 if sx_ > 0 else 1.3))
        wipe = _ac._held(keys, "wipe", t, 0.0)
        if wipe:
            arm = bpy.data.objects.get(f"{who}.arm1")
            if arm is not None:
                arm.rotation_euler.y += math.radians(18 * wipe) * math.sin(2 * math.pi * 0.9 * t)
        m = ctx.get("mops", {}).get(who)
        if m is not None:
            on = bool(_switch(keys, "mop", t, False))
            for ob in [m] + list(m.children_recursive):
                ob.hide_render = not on
    shot_look(kit, tl, t, ctx, over, info)
    # ---- the acrylic's reflection: a shot looking through it at a steep angle can thin it ("glass_ior": {shot: ior}),
    # or the glass turns into a mirror of the hall and hides what's behind it
    ior = float(story.get("glass_ior", {}).get(shot, story.get("glass_ior_default", 1.49)))
    M["acrylic"].node_tree.nodes["fresnel"].inputs["IOR"].default_value = ior
    # ---- depth of field for the few shots that ask for it: story "dof": {shot: [focus metres, f-stop]}
    cam = bpy.context.scene.camera
    if cam is not None:
        d = story.get("dof", {}).get(shot)
        cam.data.dof.use_dof = bool(d)
        if d:
            cam.data.dof.focus_distance = float(d[0])
            cam.data.dof.aperture_fstop = float(d[1])
    return over


def bubbles(tl, t, ctx):
    obs = ctx["bubbles"]
    live = []
    for c in _cues(tl, "bubbles"):
        x = t - c["t"]
        d = c.get("dur", 2.0)
        if 0 <= x <= d + 2.0:
            live.append((c, x, d))
    k = 0
    rng = np.random.default_rng(5)
    for c, x, d in live:
        kind = c.get("kind", "applause")
        n = 150 if kind == "applause" else 16
        x0, x1 = c.get("x0", GLASS_X0 + 0.3), c.get("x1", GLASS_X1 - 0.3)
        z0, z1 = c.get("z0", 0.4), c.get("z1", 4.6)
        front = x0 + (x1 - x0) * min(1.0, x / d)          # the wave's leading edge rolls from x0 to x1
        for j in range(n):
            if k >= len(obs):
                break
            ob = obs[k]
            k += 1
            u = rng.random()
            bx = x0 + (x1 - x0) * u
            born = (bx - x0) / max(1e-6, x1 - x0) * d     # each bubble starts when the front reaches it
            age = x - born - rng.random() * 0.25
            if age < 0 or age > 1.8:
                ob.location = (0, -50, -50)
                continue
            r = (0.035 if kind == "applause" else 0.018) * (0.5 + rng.random())
            zb = z0 + (z1 - z0) * rng.random()
            ob.location = (bx + 0.12 * math.sin(age * 6 + j), GLASS_FACE - 0.03 - rng.random() * 0.12,
                           zb + age * (0.5 + 0.6 * rng.random()))
            ob.scale = (r, r, r * 0.9)
    for ob in obs[k:]:
        ob.location = (0, -50, -50)


def shot_look(kit, tl, t, ctx, over, info):
    """One shot's own lights, from a "shot" cue's `look` (on from the shot's first frame, off with {"look": null}
    at its last). Keys: disp / caustic / hallfill / tanktop / glassglow / corridor / stage: gains on those lights;
    key, key2: [pos, aim, watts, cone degrees?, colour?] a spot put exactly there."""
    from blocky import kit as K

    look = _switch(_cues(tl, "shot"), "look", t, None)
    for nm in ("key", "key2"):
        over[nm] = 0.0
    if not look:
        return
    for nm in ("caustic", "hallfill", "tanktop", "glassglow", "corridor", "stage", "underkey", "regularkey", "pupkey"):
        if nm in look:
            over[nm] = over.get(nm, 1.0) * look[nm]
    if "disp" in look:
        for k in range(4):
            over[f"disp{k}"] = over.get(f"disp{k}", 1.0) * look["disp"]
    for nm in ("key", "key2"):
        if nm not in look:
            continue
        pos, aim, watts = look[nm][:3]
        ob = K.LIGHTS[nm]["obj"]
        ob.location = pos
        ob.rotation_euler = (V(aim) - V(pos)).to_track_quat("-Z", "Y").to_euler()
        K.LIGHTS[nm]["base"] = watts
        if len(look[nm]) > 3:
            K.LIGHTS[nm]["light"].spot_size = math.radians(look[nm][3])
        K.LIGHTS[nm]["light"].color = K.col(look[nm][4] if len(look[nm]) > 4 else "#dce8f0")[:3]
        over[nm] = 1.0
