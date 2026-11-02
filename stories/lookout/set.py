"""Lookout (redo 2): a fire lookout tower over an autumn forest, a valley whose town runs on hourglass time. Built from
kit.py's parts (nothing here is shared with another story's set).

Coordinates: the ground at the tower's foot is z = 0 and the tower stands on (0, 0). Its four braced steel legs rise
to the cab: a 4 x 4 m wooden cab (x, y in -CAB .. CAB) whose floor's top is CAB_Z = 19.6, glass on all four sides, under
a metal pyramid roof. The plank catwalk runs WALK = 1 m round it, with a waist-high rail on its outer edge. A
character facing -y has yaw 0. The valley falls away south: the town's night lights lie on its floor (z = -150), its
hillside and the far ridge, where the ranger's hut stands.

THE TOWN (the montage, day): its own slab at TOWN = (1200, 0), far east of the ridge. A street runs along x, the road
at z = -PL and the pavement on a stone plinth at z = 0, so a cellar and an office basement open onto the road under
the pavement. Houses stand behind the pavement (y > 0). No text or signs anywhere.

THE MARKER: a glass hourglass floats above every head, pale brass caps, pale-gold sand. Its stream is driven by one
value per character, `sand` (0.05 gush-free trickle to 1.0 gush): the cue {"name": "sand", "who", "v"}. The grains
are small, steady and never blink.

Cues read here (all optional):
- look: {"id": ...} the whole light from here (LOOKS)
- night: {"n": 1|2|3} the pines' growth and which town lights are on
- ollie: {"where": "win"|"win2"|"hut"|"none", "dur": s} Ollie's own light, fading up over dur
- sand: {"who": name, "v": 0.05..1.0}
- lamp: {"pos": [x, y, z]} set down, or {"hand": "me.arm-1", "offset": [x, y, z]} its bail from a hand
- lamp2: {"hand": "ollie_old.arm-1", "offset": ...} or {"pos": ...} the second lantern (ollie_old's)
- mover: {"pos": [x, y, z], "r": metres, "dur": s, "on": bool} the lamp crossing the valley, eased from the last key
- door / gate: {"open": 0..1, "dur": s}
- radio: {"on": bool}; binos / radio: {"hand": ...}
- parcel: {"on": true} drops onto the pavement hatch
- padlock: {"open": bool}
"""

from __future__ import annotations

import math

import bpy
import numpy as np
from mathutils import Matrix
from mathutils import Vector as V
from mathutils import noise as mnoise

# ------------------------------------------------------------------------------------------------ the tower
CAB_Z = 19.6                  # the cab floor's (and the catwalk's) top
CAB = 2.0                     # half the cab's width
WALK = 1.0                    # the catwalk's depth
WALK_OUT = CAB + WALK         # the catwalk's outer edge (the rail's line)
RAIL_H = 1.0                  # the rail's top above the deck
TOE_BOARD = 0.28              # the plank toe board along the catwalk's edge
SILL = 0.5                    # the glass starts this high above the cab floor ...
HEADER = 2.9                  # ... and stops here
EAVE = 3.1                    # the roof's eave line above the floor
ROOF_OUT = 3.15               # the roof's overhang (past the catwalk's edge)
ROOF_RISE = 1.5
PANES = 1                     # panes per side (one wide pane: no mullion across a face at the glass)
BASE = 3.8                    # half the legs' spread at the ground
LAMP_COT = (1.45, 1.35, CAB_Z + 0.48)    # the lamp set down on the cot's north end
LAMP_DECK = (-2.25, -2.5, CAB_Z)         # in the scare: set down on the catwalk at my right side, by the rail

# ------------------------------------------------------------------------------------------------ the world
# The tower stands on a summit plateau (z = 0 within about 20 m). The ground falls away south along the fire road,
# which runs from the gate at the tower's foot down to a rocky shelf about 50 m lower, and past the shelf it drops to
# the valley floor (VALLEY_Z) with the river winding through it. A higher ridge lies to the north, with the line of
# snapped pines on it. A grey smudge of the controlled burn sits far off east.
ROAD = ((0.0, -6.2), (0.0, -16.0), (3.0, -32.0), (-2.0, -52.0), (6.0, -80.0), (18.0, -120.0), (30.0, -170.0),
        (38.0, -220.0), (42.0, -258.0))
ROAD_W = 3.6
SHELF = (44.0, -266.0)          # the rocky shelf at the road's end, over the valley
VALLEY_Z = -150.0
RIVER_Y = -880.0                # the river winds across the valley floor this far south: far enough that the cab sees
#                                 it over the shelf's edge (the grazing line from the cab through the edge clears the
#                                 floor about 650 m out), and the shelf sees it below
GATE_X, GATE_Y = (-3.1, -1.4), -2.05   # the plank gate at the stairs' foot (its two posts), inside the legs: off
#                                 the last flight I turn south through it, toward the fire road
FENCE = 6.2                     # the forest keeps this far (plus 3 m) off the tower's foot
DOOR_W, DOOR_H = 1.6, 2.1      # the plank door onto the catwalk in the west wall (wide enough for my arms)
STAIR_A = 1.45                  # the stairs: a square switchback round the tower's middle, this far out
STAIR_W = 0.6
STEPS = 112                     # 8 flights of 14 at 0.175 m: the 19.6 m cab floor (L03)
RADIO_SHELF = (0.3, CAB - 0.22, CAB_Z + 0.99)    # the radio on its shelf at the north wall
BINO_SILL = (-1.6, -CAB + 0.16, CAB_Z + SILL + 0.09)
HATCH = (-1.45, -1.45)          # where the stairs come up through the cab floor: the top flight's landing
SNAPPED = ((-140.0, 380.0), (-100.0, 330.0), (-62.0, 282.0), (-40.0, 240.0), (-24.0, 200.0), (-12.0, 160.0))


def terrain_z(x, y):
    """The ground's height: the summit plateau, the long fall south, the drop to the valley floor (VALLEY_Z), the
    valley's two sides and the far ridge, and the higher ridge to the north."""
    z = -0.3 * max(0.0, -y - 20.0) - 0.05 * max(0.0, abs(x) - 24.0)
    z += 0.16 * max(0.0, y - 110.0) - 0.0006 * max(0.0, y - 260.0) ** 2
    if y < -272.0:
        z = max(VALLEY_Z, z - 1.6 * (-272.0 - y))
        z += 0.9 * min(max(0.0, -y - 760.0), 180.0)                  # the far ridge, where the hut stands
        z += 0.7 * max(0.0, abs(x) - 350.0) * min(1.0, (-y - 272.0) / 100.0)   # the valley's two sides
    k = min(1.0, max(0.0, (math.hypot(x, y) - 18.0) / 20.0), max(0.0, (road_dist(x, y) - 6.0) / 10.0))
    z += 0.9 * mnoise.noise(V((x * 0.02, y * 0.02, 0.5))) * k
    return z


def road_pos(u):
    """A point on the road, u in 0..1 along it, and the road's direction there."""
    pts = ROAD
    segs = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    d = u * sum(segs)
    for (a, b), L in zip(zip(pts, pts[1:]), segs):
        if d <= L or (a, b) == (pts[-2], pts[-1]):
            k = min(1.0, d / L)
            x, y = a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k
            return (x, y, terrain_z(x, y)), ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
        d -= L


def road_dist(x, y):
    best = 1e9
    for a, b in zip(ROAD, ROAD[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        k = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy)))
        best = min(best, math.hypot(x - a[0] - dx * k, y - a[1] - dy * k))
    return best


def _cues(tl, name):
    return sorted((c for c in tl.get("cues", []) if c["name"] == name), key=lambda c: c["t"])


def _switch(cs, attr, t, default):
    v = default
    for c in cs:
        if attr in c and c["t"] <= t + 1e-9:
            v = c[attr]
    return v


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _sock(node, ident):
    """A node socket by identifier (the Mix node has three inputs called "A")."""
    return next(s for s in node.inputs if s.identifier == ident)


def _out(node, ident):
    return next(s for s in node.outputs if s.identifier == ident)


def _mix(N, L, a, b, fac):
    """Colour mix: a and b are sockets or RGBA tuples, fac a socket or a number. Returns the output socket."""
    m = N.new("ShaderNodeMix")
    m.data_type = "RGBA"
    for ident, v in (("A_Color", a), ("B_Color", b)):
        if isinstance(v, tuple):
            _sock(m, ident).default_value = v
        else:
            L.new(v, _sock(m, ident))
    if isinstance(fac, (int, float)):
        _sock(m, "Factor_Float").default_value = fac
    else:
        L.new(fac, _sock(m, "Factor_Float"))
    return _out(m, "Result_Color")


def _math(N, L, op, a, b=None, clamp=False):
    m = N.new("ShaderNodeMath")
    m.operation = op
    m.use_clamp = clamp
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            m.inputs[i].default_value = v
        else:
            L.new(v, m.inputs[i])
    return m.outputs[0]


def _range(N, L, v, a, b, lo=0.0, hi=1.0):
    r = N.new("ShaderNodeMapRange")
    r.clamp = True
    L.new(v, r.inputs["Value"])
    r.inputs["From Min"].default_value = a
    r.inputs["From Max"].default_value = b
    r.inputs["To Min"].default_value = lo
    r.inputs["To Max"].default_value = hi
    return r.outputs["Result"]


def _noise(N, L, vec, scale, detail=4.0, rough=0.55):
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = detail
    nz.inputs["Roughness"].default_value = rough
    if vec is not None:
        L.new(vec, nz.inputs["Vector"])
    return nz.outputs["Fac"]


def _scaled(N, L, kind, scale):
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale
    L.new(tc.outputs[kind], mp.inputs["Vector"])
    return mp.outputs["Vector"]


def _dark(c, k):
    return (c[0] * k, c[1] * k, c[2] * k, 1.0)


# ------------------------------------------------------------------------------------------------ materials


def _moss(kit, N, L, base_col, rough_sock, b, lo=0.62, hi=0.84, amount=1.0, extra=None):
    """Moss on whatever faces up: the world normal's z (plus a patchy noise) decides where it grows. `extra` is a
    mask socket added to it (moss spilling over a rim)."""
    geo = N.new("ShaderNodeNewGeometry")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(geo.outputs["Normal"], sep.inputs[0])
    patch = _noise(N, L, _scaled(N, L, "Object", (0.9, 0.9, 0.9)), 1.0, 5.0)
    nz = _math(N, L, "ADD", sep.outputs["Z"], _math(N, L, "MULTIPLY", _math(N, L, "SUBTRACT", patch, 0.5), 0.55))
    mask = _math(N, L, "MULTIPLY", _range(N, L, nz, lo, hi), amount)
    if extra is not None:
        mask = _math(N, L, "MAXIMUM", mask, extra)
    mot = _noise(N, L, _scaled(N, L, "Object", (1, 1, 1)), 5.0, 6.0, 0.65)
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = kit.col("#3b4f1e")
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = kit.col("#5f7a2e")
    L.new(mot, ramp.inputs["Fac"])
    col = _mix(N, L, base_col, _mix(N, L, ramp.outputs["Color"], (0.0, 0.0, 0.0, 1.0), 0.3), mask)
    L.new(col, b.inputs["Base Color"])
    rough = N.new("ShaderNodeMapRange")
    L.new(mask, rough.inputs["Value"])
    rough.inputs["To Min"].default_value = rough_sock
    rough.inputs["To Max"].default_value = 0.97
    L.new(rough.outputs["Result"], b.inputs["Roughness"])
    return mask


def bark_mat(kit, name, hexc="#3b2a1e", moss=True, rough=0.9, stretch=(1.0, 1.0, 0.3), cell=2.4, bump=0.7,
             spill=None):
    """Bark: irregular plates split by deep cracks (Voronoi, stretched along the object's own z, so every log's
    bark runs along it), each plate a little lighter or darker, fine grain, big soft dirt patches, and moss on the
    faces that look up. spill = (z, band): moss also creeps down from object height z over `band` metres."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    c = kit.col(hexc)
    v = _scaled(N, L, "Object", stretch)
    wn = N.new("ShaderNodeTexNoise")
    wn.inputs["Scale"].default_value = 1.4
    wn.inputs["Detail"].default_value = 3.0
    L.new(v, wn.inputs["Vector"])
    off = N.new("ShaderNodeVectorMath")
    off.operation = "MULTIPLY_ADD"
    L.new(wn.outputs["Color"], off.inputs[0])
    off.inputs[1].default_value = (0.45, 0.45, 0.45)
    L.new(v, off.inputs[2])
    vv = off.outputs["Vector"]
    ve = N.new("ShaderNodeTexVoronoi")
    ve.feature = "DISTANCE_TO_EDGE"
    ve.inputs["Scale"].default_value = cell
    L.new(vv, ve.inputs["Vector"])
    vc = N.new("ShaderNodeTexVoronoi")
    vc.inputs["Scale"].default_value = cell
    L.new(vv, vc.inputs["Vector"])
    sep = N.new("ShaderNodeSeparateColor")
    L.new(vc.outputs["Color"], sep.inputs["Color"])
    plate = _range(N, L, ve.outputs["Distance"], 0.0, 0.09)            # 0 in a crack, 1 on a plate
    fine = _noise(N, L, vv, 14.0, 6.0, 0.7)
    pc = _mix(N, L, _dark(c, 0.6), (min(1, c[0] * 1.35), min(1, c[1] * 1.25), min(1, c[2] * 1.15), 1.0),
              sep.outputs["Red"])
    pc = _mix(N, L, _dark(c, 0.7), pc, _range(N, L, fine, 0.3, 0.7, 0.25, 1.0))
    col = _mix(N, L, _dark(c, 0.08), pc, plate)
    dirt = _range(N, L, _noise(N, L, _scaled(N, L, "Object", (1, 1, 1)), 0.35, 3.0), 0.3, 0.7, 0.6, 1.0)
    cc = N.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        L.new(dirt, cc.inputs[k])
    mm = N.new("ShaderNodeMix")
    mm.data_type = "RGBA"
    mm.blend_type = "MULTIPLY"
    _sock(mm, "Factor_Float").default_value = 1.0
    L.new(col, _sock(mm, "A_Color"))
    L.new(cc.outputs["Color"], _sock(mm, "B_Color"))
    base = _out(mm, "Result_Color")
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = 0.22
            break
    extra = None
    if spill:
        tc = N.new("ShaderNodeTexCoord")
        sz = N.new("ShaderNodeSeparateXYZ")
        L.new(tc.outputs["Object"], sz.inputs[0])
        wob = _math(N, L, "MULTIPLY", _math(N, L, "SUBTRACT", _noise(N, L, _scaled(N, L, "Object", (1, 1, 1)), 1.3,
                                                                     4.0), 0.5), spill[1] * 1.6)
        extra = _range(N, L, _math(N, L, "ADD", sz.outputs["Z"], wob), spill[0] - spill[1], spill[0] - spill[1] * 0.35)
        holes = _range(N, L, _noise(N, L, _scaled(N, L, "Object", (1, 1, 1)), 2.2, 4.0), 0.42, 0.58)
        extra = _math(N, L, "MULTIPLY", extra, holes)
    if moss:
        _moss(kit, N, L, base, rough, b, extra=extra)
    else:
        L.new(base, b.inputs["Base Color"])
        b.inputs["Roughness"].default_value = rough
    h = _math(N, L, "ADD", _math(N, L, "MULTIPLY", plate, 0.75), _math(N, L, "MULTIPLY", fine, 0.25))
    bp = N.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    bp.inputs["Distance"].default_value = 0.03
    L.new(h, bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    kit._fogged(m, b.outputs[0])
    return m


def logend_mat(kit, name="log end", hexc="#6e5a44"):
    """End grain: grey-brown growth rings round the log's own axis, a dark bark ring at the edge, moss if it faces up."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    wv = N.new("ShaderNodeTexWave")
    wv.wave_type = "RINGS"
    wv.rings_direction = "Z"
    wv.inputs["Scale"].default_value = 2.2
    wv.inputs["Distortion"].default_value = 2.5
    wv.inputs["Detail"].default_value = 2.0
    tc = N.new("ShaderNodeTexCoord")
    L.new(tc.outputs["Object"], wv.inputs["Vector"])
    c = kit.col(hexc)
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = _dark(c, 0.5)
    ramp.color_ramp.elements[1].color = _dark(c, 0.72)
    L.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    dirt = _noise(N, L, _scaled(N, L, "Object", (1, 1, 1)), 1.6, 4.0)
    col = _mix(N, L, ramp.outputs["Color"], _dark(c, 0.3), _range(N, L, dirt, 0.35, 0.7, 0.2, 0.85))
    _moss(kit, N, L, col, 0.9, b, 0.7, 0.9)
    kit._fogged(m, b.outputs[0])
    return m


def stone_mat(kit, name="stone", hexc="#7e8378"):
    """Weathered granite: dark mottling and lichen, a soft bump, and a moss cap on everything that faces up."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    c = kit.col(hexc)
    v = _scaled(N, L, "Object", (1, 1, 1))
    nz = _noise(N, L, v, 0.9, 6.0, 0.6)
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = _dark(c, 0.45)
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = c
    L.new(nz, ramp.inputs["Fac"])
    _moss(kit, N, L, ramp.outputs["Color"], 0.8, b, 0.42, 0.7)
    fine = _noise(N, L, v, 6.0, 8.0, 0.7)
    bp = N.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.5
    bp.inputs["Distance"].default_value = 0.08
    L.new(fine, bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    kit._fogged(m, b.outputs[0])
    return m


def matte(kit, name, hexc, rough=0.95, noise=None):
    """A plain rough surface (the hollow's walls, needles, cloth), optionally mottled (scale, dark factor)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Roughness"].default_value = rough
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = 0.2
            break
    if noise:
        nz = _noise(N, L, _scaled(N, L, "Object", (1, 1, 1)), noise[0], 6.0)
        L.new(_mix(N, L, _dark(kit.col(hexc), noise[1]), kit.col(hexc), _range(N, L, nz, 0.35, 0.65)),
              b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m


def ember_mat(kit, name, core="#ffcf94", edge="#ff8a2c", strength=0.8):
    """The giant's lights: a hot core fading to amber at the rim, so each reads as a glow, never a painted disc."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    lw = N.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    face = _math(N, L, "SUBTRACT", 1.0, lw.outputs["Facing"])                 # 1 at the middle, 0 at the rim
    em = N.new("ShaderNodeEmission")
    L.new(_mix(N, L, kit.col(edge), kit.col(core), _math(N, L, "POWER", face, 4.0)), em.inputs["Color"])
    L.new(_math(N, L, "MULTIPLY", _math(N, L, "POWER", face, 2.2), strength), em.inputs["Strength"])
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader")
    L.new(_range(N, L, face, 0.0, 0.6), mx.inputs[0])
    L.new(tr.outputs[0], mx.inputs[1])
    L.new(em.outputs[0], mx.inputs[2])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    L.new(mx.outputs[0], out.inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    return m


def hollow_mat(kit, name="hollow", hexc="#22170e"):
    """The hollow's walls: rotten heartwood, nearly black, and kept out of the distance fog so the hollow stays the
    darkest thing in a close (its own two lights faintly warm it)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.97
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = 0.1
            break
    nz = _noise(N, L, _scaled(N, L, "Object", (1.0, 1.0, 0.4)), 3.0, 6.0)
    L.new(_mix(N, L, _dark(kit.col(hexc), 0.4), kit.col(hexc), _range(N, L, nz, 0.35, 0.65)), b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])      # (a far hollow fades like the rest: unfogged it was a flat black egg, S01)
    return m


def night_glass(kit, name="cab glass"):
    """The cab's panes: see-through with a faint dust film, and no reflection (the brief: at night the glass never
    mirrors the lit cab or me)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    tr = N.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = kit.col("#eef2ee")
    dust = N.new("ShaderNodeBsdfDiffuse")
    dust.inputs["Color"].default_value = kit.col("#8c8a80")
    mask = _range(N, L, _noise(N, L, _scaled(N, L, "Object", (1, 1, 1)), 2.2, 5.0), 0.45, 0.85, 0.0, 0.09)
    mx = N.new("ShaderNodeMixShader")
    L.new(mask, mx.inputs[0])
    L.new(tr.outputs[0], mx.inputs[1])
    L.new(dust.outputs[0], mx.inputs[2])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    L.new(mx.outputs[0], out.inputs["Surface"])
    return m


def fog_card_mat(kit, name, hexc, alpha=0.7, scale=(0.22, 0.22, 0.55), top=2.0, fog=None):
    """A fog bank as a flat card (brief: "a few noise cards with a visible top, not a volume"): soft noise, fading
    in over `top` metres below its upper edge (object z = 0 is the card's top), mixed into the distance fog."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs[0])
    edge = _range(N, L, sep.outputs["Z"], 0.0, -top)                 # 0 at the top, 1 deeper in
    wisps = _noise(N, L, _scaled(N, L, "Object", scale), 1.0, 5.0, 0.6)
    lump = _range(N, L, wisps, 0.3, 0.7)
    a = _math(N, L, "MULTIPLY", _math(N, L, "MULTIPLY", edge, lump), alpha)
    # the card's own colour, faded into the fog colour with distance like every other surface
    fc, fd, fs = (kit.col(fog[0])[:3], fog[1], fog[2]) if fog else (kit.FOG["color"], kit.FOG["density"], kit.FOG["start"])
    cam = N.new("ShaderNodeCameraData")
    d = _math(N, L, "MAXIMUM", _math(N, L, "SUBTRACT", cam.outputs["View Distance"], fs), 0.0)
    ff = _math(N, L, "SUBTRACT", 1.0, _math(N, L, "EXPONENT", _math(N, L, "MULTIPLY", d, -fd)))
    em = N.new("ShaderNodeEmission")
    L.new(_mix(N, L, kit.col(hexc), (*fc, 1.0), ff), em.inputs["Color"])
    em.inputs["Strength"].default_value = 1.0
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader")
    L.new(a, mx.inputs[0])
    L.new(tr.outputs[0], mx.inputs[1])
    L.new(em.outputs[0], mx.inputs[2])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    L.new(mx.outputs[0], out.inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    return m


def block_bark_mat(kit, name, hexc="#3b2a1e", moss=True, streak=(5.0, 5.0, 0.5), bump=0.25, rough=0.9):
    """Block-world bark (pass 2, note 21): one flat colour broken by long darker streaks along the object's own z
    and big soft dirt patches, a light bump, and moss on every face that looks up. As simple as kit's own
    materials, so a timber reads as a game part made of wood, not a sculpted nature asset."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    c = kit.col(hexc)
    st = _noise(N, L, _scaled(N, L, "Object", streak), 1.6, 3.0, 0.5)
    col = _mix(N, L, _dark(c, 0.6), (min(1, c[0] * 1.18), min(1, c[1] * 1.12), min(1, c[2] * 1.06), 1.0),
               _range(N, L, st, 0.38, 0.62))
    dirt = _range(N, L, _noise(N, L, _scaled(N, L, "Object", (1, 1, 1)), 0.3, 2.0), 0.3, 0.7, 0.72, 1.0)
    cc = N.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        L.new(dirt, cc.inputs[k])
    mm = N.new("ShaderNodeMix")
    mm.data_type = "RGBA"
    mm.blend_type = "MULTIPLY"
    _sock(mm, "Factor_Float").default_value = 1.0
    L.new(col, _sock(mm, "A_Color"))
    L.new(cc.outputs["Color"], _sock(mm, "B_Color"))
    base = _out(mm, "Result_Color")
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = 0.2
            break
    if moss:
        _moss(kit, N, L, base, rough, b, 0.72, 0.9)
    else:
        L.new(base, b.inputs["Base Color"])
        b.inputs["Roughness"].default_value = rough
    bp = N.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    bp.inputs["Distance"].default_value = 0.02
    L.new(st, bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    kit._fogged(m, b.outputs[0])
    return m


def block_end_mat(kit, name="block end", hexc="#6e5a44"):
    """A timber's cut end: flat grey-brown at 55 to 70% of the brief's #6e5a44 with dirt (never pale, so a row of
    ends never reads as eyes), moss if it faces up."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    c = kit.col(hexc)
    nz = _noise(N, L, _scaled(N, L, "Object", (1, 1, 1)), 2.0, 3.0)
    col = _mix(N, L, _dark(c, 0.45), _dark(c, 0.68), _range(N, L, nz, 0.35, 0.65))
    _moss(kit, N, L, col, 0.92, b, 0.72, 0.9)
    kit._fogged(m, b.outputs[0])
    return m


def block_stone_mat(kit, name="block stone", hexc="#7e8378"):
    """A faceted boulder: one flat grey-green colour with mild mottling and no sculpted bump, moss on the facets
    that look up."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    c = kit.col(hexc)
    nz = _noise(N, L, _scaled(N, L, "Object", (1, 1, 1)), 0.8, 3.0)
    col = _mix(N, L, _dark(c, 0.7), c, _range(N, L, nz, 0.35, 0.65))
    _moss(kit, N, L, col, 0.85, b, 0.5, 0.75)
    kit._fogged(m, b.outputs[0])
    return m


def glow_mat(kit, name, hexc, strength):
    """A plain emission that no fog hides: a light seen through the valley's fog."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = strength
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    return m


def materials(kit):
    return {
        "needles": matte(kit, "needles", "#1e2a22", 0.9, (4.0, 0.6)),
        "trunk": bark_mat(kit, "pine trunk", "#2b2019", moss=False, cell=6.0),
        "ground": ground_mat(kit),
        "smoke": smoke_mat(kit, "valley fog"),
        "stair": kit.planks("#5a4b3b", "#3d3328", 1.0, "X", "stair planks"),
        "fence": matte(kit, "fence wood", "#4a3c2e", 0.9, (2.0, 0.7)),
        "radio": kit.plastic("#121214", 0.55, "radio body"),
        "led": kit.emit("#3cff7a", 3.0, "radio light"),
        "logsheet": ruled_mat(kit),
        "larch": matte(kit, "larch needles", "#c8962e", 0.9, (4.0, 0.7)),
        "bino": bino_mat(kit),
        "planks": kit.planks("#6a5a48", "#45392d", 1.0, "X", "deck planks"),
        "wall": kit.planks("#5e4f3f", "#3f342a", 1.0, "Z", "cab boards"),
        "toeboard": kit.planks("#3a3028", "#2a221b", 1.0, "X", "toe boards"),
        "rail": kit.metal("#3a3e42", 0.6, "rail metal"),
        "steel": kit.metal("#4a4e52", 0.55, "tower steel"),
        "roof": kit.metal("#2c3034", 0.78, "roof metal"),
        "frame": matte(kit, "window frame", "#3a2f25", 0.8),
        "glass": night_glass(kit),
        "lamp_body": kit.metal("#2a2a28", 0.75, "lamp body"),
        "lamp_glow": kit.emit("#ffc884", 0.12, "lamp glow"),
        "cot": matte(kit, "cot", "#4d5244", 0.95, (2.0, 0.7)),
        "iron": kit.metal("#2e2c2a", 0.5, "iron key"),
        "fog_near": fog_card_mat(kit, "fog near", "#3a4550", 0.75),
        "fog_far": fog_card_mat(kit, "fog far", "#46525c", 0.85, (0.08, 0.08, 0.3), 5.0),
        "fog_neck": fog_card_mat(kit, "fog neck", "#3c4852", 0.92, (0.18, 0.18, 0.45), 4.0),
        "fog_day": fog_card_mat(kit, "fog day", "#cdd0cc", 0.8, (0.05, 0.05, 0.35), 4.0, ("#b8bcb8", 0.0045, 20.0)),
        "fog_dayback": fog_card_mat(kit, "fog dayback", "#c3c7c3", 0.97, (0.02, 0.02, 0.05), 60.0,
                                    ("#b8bcb8", 0.0045, 20.0)),
        # the marker
        "brass": kit.metal("#d8c690", 0.3, "hourglass brass"),
        "hgglass": kit.glass("#e8f2f4", "hourglass glass"),
        "sand": glow_mat(kit, "sand glow", "#ffd98a", 1.6),
        # the town (day)
        "t_road": matte(kit, "t road", "#5b5e63", 0.95),
        "t_pave": matte(kit, "t pave", "#d2ccbd", 0.9),
        "t_grass": matte(kit, "t grass", "#6aa84f", 0.95),
        "t_brick": matte(kit, "t brick", "#b04a36", 0.9, (6.0, 0.8)),
        "t_roof": matte(kit, "t roof", "#3f4654", 0.8),
        "t_roofred": matte(kit, "t roofred", "#8e3a2c", 0.8),
        "t_cream": matte(kit, "t cream", "#eadfbf", 0.9),
        "t_blue": matte(kit, "t blue", "#6f93c4", 0.9),
        "t_stone": matte(kit, "t stone", "#a9a49a", 0.9),
        "t_win": matte(kit, "t window", "#27384c", 0.4),
        "t_door": matte(kit, "t door", "#7a4a2a", 0.8),
        "t_lemon": matte(kit, "t lemon", "#f1d24a", 0.85),
        "t_wood": matte(kit, "t wood", "#a0764a", 0.85),
        "t_dark": matte(kit, "t dark", "#2a2d33", 0.9),
        "t_parcel": matte(kit, "t parcel", "#8a6240", 0.9),
        "t_string": matte(kit, "t string", "#d9c9a0", 0.9),
        "t_hill": matte(kit, "t hill", "#5f9a4a", 0.95),
        "t_flower": matte(kit, "t flower", "#e0527a", 0.9),
        # night lights (never fogged)
        "town_glow": glow_mat(kit, "town glow", "#ffc27a", 8.0),
        "ollie_glow": glow_mat(kit, "ollie glow", "#ffb45a", 14.0),
        "mover_glow": glow_mat(kit, "mover glow", "#ffcf8a", 8.0),
        "hut": matte(kit, "hut wood", "#3a2d22", 0.9),
        "hutroof": matte(kit, "hut roof", "#232526", 0.9),
        "badge": kit.metal("#c9a24a", 0.35, "brass badge"),
    }


# ---- meshes
def pine_data(kit, name, M, h=1.0, tiers=4, sides=7, seed=0):
    """A blocky pine (faceted cone tiers on a trunk), height h. One mesh, shared by every tree of that kind:
    the forest, the saplings on the giant's stones and the spring trees are all this."""
    verts, faces, mats = [], [], []

    def cone(r0, z0, z1, rr=0.0, n=sides, twist=0.0, mat=0):
        b0 = len(verts)
        for j in range(n):
            a = 2 * math.pi * j / n + twist
            verts.append((r0 * math.cos(a), r0 * math.sin(a), z0))
        if rr > 0:
            for j in range(n):
                a = 2 * math.pi * j / n + twist
                verts.append((rr * math.cos(a), rr * math.sin(a), z1))
            for j in range(n):
                j2 = (j + 1) % n
                faces.append((b0 + j, b0 + j2, b0 + n + j2, b0 + n + j))
                mats.append(mat)
            faces.append(tuple(range(b0 + n, b0 + 2 * n)))
            mats.append(mat)
        else:
            verts.append((0, 0, z1))
            for j in range(n):
                faces.append((b0 + j, b0 + (j + 1) % n, b0 + n))
                mats.append(mat)
        faces.append(tuple(reversed(range(b0, b0 + n))))
        mats.append(mat)

    cone(0.035 * h, 0.0, 0.42 * h, 0.022 * h, 6, 0.0, 1)
    for k in range(tiers):
        u = k / tiers
        z0 = h * (0.2 + 0.62 * u)
        z1 = z0 + h * (0.36 - 0.12 * u) if k < tiers - 1 else h
        cone(h * (0.27 - 0.17 * u), z0, z1, 0.0, sides, 0.4 * k, 0)
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    me.materials.append(M["needles"])
    me.materials.append(M["trunk"])
    for p, mi in zip(me.polygons, mats):
        p.material_index = mi
    return me


def place_pine(kit, me, name, loc, scale, yaw=0.0, parent=None, lean=(0.0, 0.0)):
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = (lean[0], lean[1], yaw)
    ob.scale = (scale, scale, scale)
    return kit.link(ob, parent)


# ------------------------------------------------------------------------------------------------ the tower


def _wbox(kit, name, lo, hi, mat, parent=None):
    """A box from its world corners, its object space the world's (so the boards line up)."""
    c = tuple((a + b) / 2 for a, b in zip(lo, hi))
    sz = tuple(b - a for a, b in zip(lo, hi))
    return kit.mesh_obj(name, kit.box_verts(*sz, c), kit.BOX_FACES, mat, parent)


def _beam(kit, name, a, b, w, mat):
    """A square steel member from point a to point b."""
    a, b = V(a), V(b)
    d = b - a
    ob = kit.box(name, (w, w, d.length), tuple((a + b) / 2), mat)
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return ob


def build_tower(kit, ctx, M):
    z = CAB_Z
    # the deck: the cab's floor and the catwalk round it, one plank floor with the stairs' hatch at the cab's
    # north-west corner (the top flight comes up through it)
    hx, hy = HATCH
    w = STAIR_W
    _wbox(kit, "deck", (-WALK_OUT, -WALK_OUT, z - 0.14), (WALK_OUT, hy - w / 2, z), M["planks"])
    _wbox(kit, "deck.n", (-WALK_OUT, hy + w / 2, z - 0.14), (WALK_OUT, WALK_OUT, z), M["planks"])
    _wbox(kit, "deck.w", (-WALK_OUT, hy - w / 2, z - 0.14), (hx - w / 2, hy + w / 2, z), M["planks"])
    _wbox(kit, "deck.e", (hx + w / 2, hy - w / 2, z - 0.14), (WALK_OUT, hy + w / 2, z), M["planks"])
    for k, y in enumerate((-WALK_OUT + 0.15, WALK_OUT - 0.15)):     # under the catwalk's edges (clear of the stairs)
        _wbox(kit, f"joist{k}", (-WALK_OUT, y - 0.08, z - 0.44), (WALK_OUT, y + 0.08, z - 0.14), M["steel"])
    # the rail: posts every 1.5 m, a top rail and a mid rail, all round the catwalk's edge
    e = WALK_OUT - 0.04
    for side in range(4):
        for k in range(5):
            u = -WALK_OUT + 1.5 * k
            x, y = [(u, -e), (e, u), (u, e), (-e, u)][side]
            kit.box(f"post{side}{k}", (0.07, 0.07, RAIL_H), (x, y, z + RAIL_H / 2), M["rail"])
    # a plank toe board along the catwalk's outer edge (it also keeps my lamp's light off anything low out there)
    tb = TOE_BOARD
    for nm, lo, hi in (("s", (-WALK_OUT, -WALK_OUT, z), (WALK_OUT, -WALK_OUT + 0.04, z + tb)),
                       ("n", (-WALK_OUT, WALK_OUT - 0.04, z), (WALK_OUT, WALK_OUT, z + tb)),
                       ("e", (WALK_OUT - 0.04, -WALK_OUT, z), (WALK_OUT, WALK_OUT, z + tb)),
                       ("w", (-WALK_OUT, -WALK_OUT, z), (-WALK_OUT + 0.04, WALK_OUT, z + tb))):
        _wbox(kit, f"toeboard_{nm}", lo, hi, M["toeboard"])
    for nm, hz in (("top", RAIL_H), ("mid", RAIL_H / 2)):
        kit.box(f"rail_{nm}_s", (2 * WALK_OUT, 0.06, 0.06), (0, -e, z + hz), M["rail"])
        kit.box(f"rail_{nm}_n", (2 * WALK_OUT, 0.06, 0.06), (0, e, z + hz), M["rail"])
        kit.box(f"rail_{nm}_e", (0.06, 2 * WALK_OUT, 0.06), (e, 0, z + hz), M["rail"])
        kit.box(f"rail_{nm}_w", (0.06, 2 * WALK_OUT, 0.06), (-e, 0, z + hz), M["rail"])
    # the cab: board walls to the sill, glass to the header, corner posts and mullions, the roof
    t = 0.08
    d = DOOR_W / 2
    for nm, lo, hi in (("s", (-CAB, -CAB, z), (CAB, -CAB + t, z + SILL)), ("n", (-CAB, CAB - t, z), (CAB, CAB, z + SILL)),
                       ("e", (CAB - t, -CAB, z), (CAB, CAB, z + SILL)), ("w", (-CAB, -CAB, z), (-CAB + t, CAB, z + SILL))):
        _wbox(kit, f"header_{nm}", (lo[0], lo[1], z + HEADER), (hi[0], hi[1], z + EAVE), M["wall"])
        # the west wall has the door in it (y -d .. d), so its board wall and sill come in two pieces
        parts = [("", lo[1], hi[1])] if nm != "w" else [("_s", lo[1], -d - 0.04), ("_n", d + 0.04, hi[1])]
        for sfx, y0, y1 in parts:
            _wbox(kit, f"wall_{nm}{sfx}", (lo[0], y0, lo[2]), (hi[0], y1, hi[2]), M["wall"])
            _wbox(kit, f"sill_{nm}{sfx}", (lo[0] - 0.02, y0 - (0.02 if y0 == lo[1] else 0), z + SILL - 0.02),
                  (hi[0] + 0.02, y1 + (0.02 if y1 == hi[1] else 0), z + SILL + 0.05), M["frame"])
    # the door's frame: two jambs and a lintel, glass above the lintel to the header
    for k, y in enumerate((-d - 0.02, d + 0.02)):
        _wbox(kit, f"jamb{k}", (-CAB - 0.01, y - 0.04, z), (-CAB + t + 0.01, y + 0.04, z + DOOR_H), M["frame"])
    _wbox(kit, "lintel", (-CAB - 0.01, -d - 0.06, z + DOOR_H), (-CAB + t + 0.01, d + 0.06, z + DOOR_H + 0.08), M["frame"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"corner{sx}{sy}", (0.14, 0.14, EAVE), (sx * (CAB - 0.07), sy * (CAB - 0.07), z + EAVE / 2), M["frame"])
    glass = []
    gh = HEADER - SILL
    for k in range(1, PANES):
        u = -CAB + 2 * CAB * k / PANES
        for nm, loc, size in (("s", (u, -CAB + t / 2, 0), (0.07, 0.1, gh)), ("n", (u, CAB - t / 2, 0), (0.07, 0.1, gh)),
                              ("e", (CAB - t / 2, u, 0), (0.1, 0.07, gh)), ("w", (-CAB + t / 2, u, 0), (0.1, 0.07, gh))):
            kit.box(f"mullion_{nm}{k}", size, (loc[0], loc[1], z + SILL + gh / 2), M["frame"])
    wl = CAB - d - 0.06                     # the west panes either side of the door
    th = HEADER - DOOR_H - 0.08              # and the transom over it
    for nm, loc, size, rot in (
            ("s", (0, -CAB + t / 2, z + SILL + gh / 2), (2 * CAB, gh), (math.pi / 2, 0, 0)),
            ("n", (0, CAB - t / 2, z + SILL + gh / 2), (2 * CAB, gh), (math.pi / 2, 0, 0)),
            ("e", (CAB - t / 2, 0, z + SILL + gh / 2), (2 * CAB, gh), (math.pi / 2, 0, math.pi / 2)),
            ("w_s", (-CAB + t / 2, -CAB + wl / 2, z + SILL + gh / 2), (wl, gh), (math.pi / 2, 0, math.pi / 2)),
            ("w_n", (-CAB + t / 2, CAB - wl / 2, z + SILL + gh / 2), (wl, gh), (math.pi / 2, 0, math.pi / 2)),
            ("w_t", (-CAB + t / 2, 0, z + DOOR_H + 0.08 + th / 2), (2 * d + 0.12, th), (math.pi / 2, 0, math.pi / 2))):
        p = kit.plane(f"glass_{nm}", size, loc, M["glass"], rot=rot)
        p.visible_shadow = False
        glass.append(p)
    ctx["glass"] = glass
    # the roof: a low metal pyramid, its eave out over the catwalk
    ez, az = z + EAVE, z + EAVE + ROOF_RISE
    o = ROOF_OUT
    verts = [(-o, -o, ez), (o, -o, ez), (o, o, ez), (-o, o, ez), (0, 0, az)]
    roof = kit.mesh_obj("roof", verts, [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (3, 2, 1, 0)], M["roof"])
    sol = roof.modifiers.new("thick", "SOLIDIFY")
    sol.thickness = 0.06
    _wbox(kit, "ceiling", (-CAB, -CAB, ez - 0.04), (CAB, CAB, ez), M["wall"])
    # the legs: four braced steel legs splayed to the ground
    tops = [(sx * (CAB - 0.2), sy * (CAB - 0.2), z - 0.44) for sx in (-1, 1) for sy in (-1, 1)]
    foots = [(sx * BASE, sy * BASE, 0.0) for sx in (-1, 1) for sy in (-1, 1)]
    for k, (a, b) in enumerate(zip(tops, foots)):
        _beam(kit, f"leg{k}", a, b, 0.26, M["steel"])
    order = [0, 1, 3, 2]
    for lev in range(4):
        u0, u1 = lev / 4, (lev + 1) / 4
        for i in range(4):
            a, b = order[i], order[(i + 1) % 4]
            pa0 = V(foots[a]).lerp(V(tops[a]), u0)
            pb1 = V(foots[b]).lerp(V(tops[b]), u1)
            pb0 = V(foots[b]).lerp(V(tops[b]), u0)
            pa1 = V(foots[a]).lerp(V(tops[a]), u1)
            _beam(kit, f"brace{lev}{i}a", pa0, pb1, 0.1, M["steel"])
            _beam(kit, f"brace{lev}{i}b", pb0, pa1, 0.1, M["steel"])
            _beam(kit, f"girt{lev}{i}", pa1, V(foots[b]).lerp(V(tops[b]), u1), 0.12, M["steel"])
    # inside: the cot along the east wall and the lamp on the floor
    _wbox(kit, "cot", (CAB - 0.85, -0.9, z + 0.3), (CAB - 0.1, 1.7, z + 0.48), M["cot"])
    for k, y in enumerate((-0.85, 1.65)):
        _wbox(kit, f"cotleg{k}", (CAB - 0.85, y, z), (CAB - 0.1, y + 0.05, z + 0.3), M["rail"])
    ctx["lamp"] = build_lamp(kit, ctx, M)


def build_lamp(kit, ctx, M):
    """The box lantern, 0.3 x 0.3 x 0.4 m: a dark metal frame round a warm glow, a wire bail on top. It never flickers."""
    root = kit.empty("lamp", (0, 0, 0))
    kit.box("lamp.base", (0.3, 0.3, 0.05), (0, 0, 0.025), M["lamp_body"], root, bevel=0.01)
    cap = kit.box("lamp.cap", (0.3, 0.3, 0.06), (0, 0, 0.37), M["lamp_body"], root, bevel=0.01)
    top = kit.box("lamp.top", (0.16, 0.16, 0.04), (0, 0, 0.42), M["lamp_body"], root, bevel=0.01)
    for ob in (cap, top):        # a vented top: the flame lights my face when I hold it below my chin
        ob.visible_shadow = False
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"lamp.post{sx}{sy}", (0.025, 0.025, 0.3), (sx * 0.135, sy * 0.135, 0.2), M["lamp_body"], root)
    glow = kit.box("lamp.glow", (0.24, 0.24, 0.29), (0, 0, 0.195), M["lamp_glow"], root)
    glow.visible_shadow = False
    bail = kit.cyl("lamp.bail", 0.012, 0.2, (0, 0, 0.52), M["lamp_body"], root, rot=(0, math.pi / 2, 0), n=8)
    for sx in (-1, 1):
        kit.box(f"lamp.bailside{sx}", (0.015, 0.015, 0.1), (sx * 0.1, 0, 0.47), M["lamp_body"], root)
    kit.light("lamp", "POINT", (0, 0, 0.2), 95.0, "#ffd9a0", size=0.2, parent=root)
    bail.visible_shadow = True
    return root



def link_lights(kit, coll, light_names, objs, state="INCLUDE"):
    """Light linking: these lights light only `objs` (INCLUDE) or everything but them (EXCLUDE)."""
    col = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = state
    for nm in light_names:
        kit.LIGHTS[nm]["obj"].light_linking.receiver_collection = col



# ------------------------------------------------------------------------------------------------ the land
LOOK_NODES = {"spring": [], "river": [], "smoke": []}   # value nodes a look sets (see apply_look)


def _value(N, v, key):
    n = N.new("ShaderNodeValue")
    n.outputs[0].default_value = v
    LOOK_NODES[key].append(n)
    return n.outputs[0]


def ground_mat(kit, name="ground"):
    """The forest floor: dark needles and mud, gold larch leaves near the tower, and a spring mix to young green."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    v = _scaled(N, L, "Object", (1, 1, 1))
    nz = _noise(N, L, v, 0.25, 4.0)
    autumn = _mix(N, L, kit.col("#1b1712"), kit.col("#2f281c"), _range(N, L, nz, 0.35, 0.65))
    leaves = _range(N, L, _noise(N, L, v, 2.6, 2.0), 0.62, 0.7)
    autumn = _mix(N, L, autumn, kit.col("#7d5f24"), _math(N, L, "MULTIPLY", leaves, 0.7))
    green = _mix(N, L, kit.col("#24361a"), kit.col("#3e5a26"), _range(N, L, nz, 0.35, 0.65))
    L.new(_mix(N, L, autumn, green, _value(N, 0.0, "spring")), b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 1.0
    kit._fogged(m, b.outputs[0])
    return m



def smoke_mat(kit, name="smoke layer", hexc="#8a8178"):
    """Smoke lying in the valley like milk: a flat noise sheet whose thickness each look sets (thinning at first
    light, gone in spring). Never orange, never near me (brief: distant smoke only)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    nz = _noise(N, L, _scaled(N, L, "Object", (0.012, 0.012, 0.012)), 1.0, 5.0)
    holes = _range(N, L, nz, 0.25, 0.6)
    a = _math(N, L, "MULTIPLY", holes, _value(N, 0.0, "smoke"))
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col(hexc)
    em.inputs["Strength"].default_value = 1.0
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader")
    L.new(a, mx.inputs[0])
    L.new(tr.outputs[0], mx.inputs[1])
    L.new(em.outputs[0], mx.inputs[2])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    L.new(mx.outputs[0], out.inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    return m


def ruled_mat(kit, name="log sheet"):
    """The log sheet: pale paper with ruled lines only (no text anywhere in the set)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    wv = N.new("ShaderNodeTexWave")
    wv.bands_direction = "Y"
    wv.inputs["Scale"].default_value = 9.0
    wv.inputs["Distortion"].default_value = 0.0
    tc = N.new("ShaderNodeTexCoord")
    L.new(tc.outputs["Object"], wv.inputs["Vector"])
    L.new(_mix(N, L, kit.col("#7f8a99"), kit.col("#d8d2c2"), _range(N, L, wv.outputs["Fac"], 0.05, 0.25)),
          b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.9
    kit._fogged(m, b.outputs[0])
    return m



# ------------------------------------------------------------------------------------------------ the forest and land
PINE_SCALE = {1: 1.0, 2: 1.12, 3: 1.28, 4: 1.28}     # the pines grow a night at a time (L18, L21)
SCRAPE_BASE = (-2.5, -11.0)
SCRAPE_LEAN = -19.8                                   # degrees about x: its top leans in toward the catwalk rail
SCRAPE_H = 17.0


def build_forest(kit, ctx, M, rng, n=380, r0=10.0, r1=240.0):
    """Pines on the ground, 14 to 17 m (grown by night in animate), gold larch in patches, clear of the tower's foot
    (the fence line plus 3 m) and of the scraping pine's patch."""
    pine, larch = ctx["pine"], ctx["larch"]
    trees = []
    k = 0
    while len(trees) < n and k < n * 40:
        k += 1
        a = rng.uniform(0, 2 * math.pi)
        d = math.sqrt(rng.uniform(r0 ** 2, r1 ** 2))
        x, y = d * math.cos(a), d * math.sin(a)
        if abs(x) < FENCE + 3 and abs(y) < FENCE + 3:
            continue
        if math.hypot(x - SCRAPE_BASE[0], y - SCRAPE_BASE[1]) < 7.0 or y < -28:
            continue
        if any(math.hypot(x - tx, y - ty) < 4.6 for tx, ty in trees):
            continue
        trees.append((x, y))
        gold = mnoise.noise(V((x * 0.03, y * 0.03, 7.0))) > 0.32
        s = rng.uniform(14, 17)
        ob = place_pine(kit, larch if gold else pine, f"pine{len(trees)}", (x, y, terrain_z(x, y) - 0.2), s,
                        rng.uniform(0, 6.3))
        ob["s0"] = s
        ctx.setdefault("tree_objs", []).append(ob)
    # the one that scrapes the catwalk on the third night: it leans in at the tower
    sx, sy = SCRAPE_BASE
    ob = place_pine(kit, pine, "pine.scrape", (sx, sy, 0.0), SCRAPE_H, 0.0, lean=(math.radians(SCRAPE_LEAN), 0.0))
    ob["s0"] = SCRAPE_H
    ctx["tree_objs"].append(ob)
    ctx["trees"] = trees
    return trees


FOG_CARDS = {
    "fog.near": ("fog_near", (6.0, 16.0, 8.5, 60.0, 9.0, 20.0)),
    "fog.tower": ("fog_near", (0.0, -1.0, 10.5, 50.0, 11.0, 20.0)),
    "fog.neck": ("fog_neck", (-4.2, -3.9, CAB_Z - 2.7, 16.0, 9.0, 48.0)),
    "fog.behind": ("fog_near", (0.0, -15.0, 13.0, 80.0, 14.0, 20.0)),
    "fog.far": ("fog_far", (0.0, -45.0, 60.0, 220.0, 70.0, 20.0)),
    "fog.day1": ("fog_day", (0.0, -95.0, 9.0, 320.0, 9.0, 0.0)),
    "fog.day2": ("fog_day", (0.0, -55.0, 10.0, 300.0, 10.0, 0.0)),
    "fog.day3": ("fog_day", (0.0, -24.0, 11.0, 260.0, 11.0, 0.0)),
    "fog.day4": ("fog_day", (0.0, 14.0, 11.5, 260.0, 11.5, 0.0)),
    "fog.day5": ("fog_day", (0.0, 48.0, 12.5, 300.0, 12.5, 0.0)),
    "fog.dayback": ("fog_dayback", (0.0, 170.0, 140.0, 700.0, 150.0, 0.0)),
}


def build_fog(kit, ctx, M):
    cards = []
    for nm, (mat, (x, y, top, w, h, yaw)) in FOG_CARDS.items():
        verts = [(-w / 2, 0, -h), (w / 2, 0, -h), (w / 2, 0, 0), (-w / 2, 0, 0)]
        ob = kit.mesh_obj(nm, verts, [(0, 1, 2, 3)], M[mat], loc=(x, y, top), rot=(0, 0, math.radians(yaw)))
        ob.visible_shadow = False
        ob.visible_diffuse = False
        ob.visible_glossy = False
        cards.append(ob)
    ctx["fog"] = cards
    return cards


def build_land(kit, ctx, M):
    """The terrain (10 m grid near the tower, 20 m out over the valley and the far ridge), the tower's flat pad, and
    the valley's fog sheet."""
    xs = np.concatenate([np.arange(-760.0, -320.0, 20.0), np.arange(-320.0, 321.0, 10.0), np.arange(340.0, 761.0, 20.0)])
    ys = np.concatenate([np.arange(-1100.0, -720.0, 20.0), np.arange(-720.0, 441.0, 10.0)])
    verts, faces = [], []
    for y in ys:
        for x in xs:
            verts.append((float(x), float(y), terrain_z(x, y) - 0.05))
    nx = len(xs)
    for j in range(len(ys) - 1):
        for i in range(nx - 1):
            faces.append((j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i))
    ground = kit.mesh_obj("ground", verts, faces, M["ground"])
    for p in ground.data.polygons:
        p.use_smooth = True
    _wbox(kit, "plateau", (-24, -24, -0.6), (24, 24, 0.0), M["ground"])
    fog = kit.plane("valley fog", (1500, 900), (0, -640, VALLEY_Z + 36), M["smoke"])
    for k in ("visible_shadow", "visible_diffuse", "visible_glossy"):
        setattr(fog, k, False)


# ------------------------------------------------------------------------------------------------ the valley at night
def build_valley(kit, ctx, M):
    """The town's night lights on the valley floor, its hillside and the far ridge (never fogged, never blinking),
    Ollie's three places, the ranger's hut, and the lamp that crosses the valley."""
    rng = np.random.default_rng(16)
    pts = []          # (level, x, y)

    def spread(level, count, cx, cy, rx, ry):
        for _ in range(count):
            for _try in range(30):
                x, y = rng.normal(cx, rx), rng.normal(cy, ry)
                if -880.0 < y < -400.0 and abs(x) < 640.0 and all(math.hypot(x - a, y - b) > 14.0 for _l, a, b in pts):
                    pts.append((level, x, y))
                    break

    spread(1, 34, 10.0, -560.0, 55.0, 40.0)
    spread(2, 40, 0.0, -580.0, 120.0, 60.0)
    spread(3, 90, 0.0, -600.0, 260.0, 90.0)
    lights = []
    for k, (lv, x, y) in enumerate(pts):
        s = rng.uniform(5.5, 8.0)
        ob = kit.box(f"town{k}", (s, s, s), (x, y, terrain_z(x, y) + s / 2), M["town_glow"])
        ob.visible_shadow = False
        ob["level"] = lv
        lights.append(ob)
    ctx["town_lights"] = lights
    # Ollie's light: the warmest point in frame, always steady (win: valley floor, win2: the hillside, hut: the ridge)
    ctx["ollie_at"] = {}
    for nm, (x, y), s in (("win", (30.0, -560.0), 11.0), ("win2", (-410.0, -640.0), 11.0)):
        ob = kit.box(f"ollie_{nm}", (s, s, s), (x, y, terrain_z(x, y) + s / 2), M["ollie_glow"])
        ob.visible_shadow = False
        ctx["ollie_at"][nm] = ob
    # the ranger's hut on the far ridge: a small timber hut, one window facing the tower
    hx, hy = -120.0, -900.0
    hz = terrain_z(hx, hy)
    _wbox(kit, "hut.walls", (hx - 11, hy - 8, hz - 1), (hx + 11, hy + 8, hz + 8), M["hut"])
    rv = [(hx - 13, hy - 10, hz + 8), (hx + 13, hy - 10, hz + 8), (hx + 13, hy + 10, hz + 8), (hx - 13, hy + 10, hz + 8),
          (hx - 13, hy, hz + 14), (hx + 13, hy, hz + 14)]
    kit.mesh_obj("hut.roof", rv, [(0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5), (3, 2, 1, 0)], M["hutroof"])
    w = kit.box("ollie_hut", (9.0, 1.0, 6.0), (hx + 2.0, hy + 8.6, hz + 4.2), M["ollie_glow"])
    w.visible_shadow = False
    ctx["ollie_at"]["hut"] = w
    # the lamp that crosses the valley (and climbs the stairs): a glow whose size and place a cue sets
    mv = kit.sphere("mover", 1.0, (0, 0, -80), M["mover_glow"], seg=10)
    mv.visible_shadow = False
    ctx["mover"] = mv
    kit.light("walklamp", "POINT", (0, 0, -80), 60.0, "#ffcf8a", size=0.2)


# ------------------------------------------------------------------------------------------------ the marker
HG_H = 0.62            # the hourglass's height in metres (a head is 0.41 wide)
GRAINS = 14


def build_hourglass(kit, ctx, M, who):
    """A glass hourglass with pale brass caps and glowing pale-gold sand falling top to bottom, built once per
    character and floated above the head in animate()."""
    root = kit.empty(f"hg.{who}", (0, 0, -100))
    h = HG_H
    cap_w = 0.30
    for z, nm in ((h / 2, "top"), (-h / 2, "bot")):
        kit.box(f"hg.{who}.cap{nm}", (cap_w, cap_w, 0.05), (0, 0, z), M["brass"], root, bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"hg.{who}.post{sx}{sy}", 0.012, h, (sx * cap_w * 0.44, sy * cap_w * 0.44, 0), M["brass"], root, n=6)
    bulb = (h - 0.1) / 2
    r = cap_w * 0.40
    kit.cyl(f"hg.{who}.glass_t", 0.012, bulb, (0, 0, bulb / 2), M["hgglass"], root, n=14, r2=r).visible_shadow = False
    kit.cyl(f"hg.{who}.glass_b", r, bulb, (0, 0, -bulb / 2), M["hgglass"], root, n=14, r2=0.012).visible_shadow = False
    # the sand: a heap in the top bulb, a heap in the bottom one, and the falling grains between
    kit.cyl(f"hg.{who}.heap_t", 0.012, 0.09, (0, 0, 0.07), M["sand"], root, n=10, r2=r * 0.6).visible_shadow = False
    kit.cyl(f"hg.{who}.heap_b", r * 0.75, 0.10, (0, 0, -bulb + 0.05), M["sand"], root, n=10, r2=0.012).visible_shadow = False
    grains = []
    for k in range(GRAINS):
        g = kit.sphere(f"hg.{who}.grain{k}", 0.014, (0, 0, 0), M["sand"], root, seg=6)
        g.visible_shadow = False
        grains.append(g)
    ctx.setdefault("hg", {})[who] = (root, grains)


SAND0 = {"me": 0.3, "ollie": 0.95, "ollie_old": 0.06, "balcony": 0.1, "walker": 0.95, "grandad": 0.1, "son": 0.8,
         "cellarman": 1.0, "office1": 0.9, "office2": 0.9, "office3": 0.9}


def sand_of(tl, t, who):
    v = SAND0.get(who, 0.3)
    for c in _cues(tl, "sand"):
        if c.get("who") == who and c["t"] <= t + 1e-9:
            v = c["v"]
    return v


def place_hourglass(ctx, tl, t, who, state):
    root, grains = ctx["hg"][who]
    head = bpy.data.objects.get(f"{who}.headg")
    hidden = head is None or state["hidden"]
    if ctx.setdefault("hg_hidden", {}).get(who) != hidden:
        ctx["hg_hidden"][who] = hidden
        for ob in root.children_recursive:
            ob.hide_render = hidden
    if hidden:
        root.location = (0, 0, -100)
        return
    wp = head.matrix_world.translation
    hs = ctx["story"]["cast"][who].get("height", 1.0)
    root.location = (wp.x, wp.y, wp.z + (0.20 + 0.14) * hs + HG_H / 2 + 0.12)
    sand = sand_of(tl, t, who)
    n = 2 + int(round((GRAINS - 2) * min(1.0, max(0.0, (sand - 0.05) / 0.95))))
    speed = 0.3 + 2.4 * sand
    top, bot = 0.0, -(HG_H - 0.1) / 2 + 0.10
    for k, g in enumerate(grains):
        g.hide_render = k >= n
        u = (k / n + t * speed + (sum(map(ord, who)) % 7) * 0.13) % 1.0
        spread = 0.012 + 0.03 * sand * u
        a = k * 2.399
        g.location = (spread * math.cos(a), spread * math.sin(a), top - u * (top - bot))
        g.scale = (1.0 + 0.5 * sand,) * 3


def build_stairs(kit, ctx, M):
    """The 112 stairs: eight flights of 14 (0.175 m rise) round a square switchback inside the legs, with a landing at
    each corner and a pipe handrail on the outside, coming up through the hatch in the cab floor."""
    a = STAIR_A
    corners = [(-a, -a), (a, -a), (a, a), (-a, a)]
    rise = CAB_Z / STEPS
    path = [(corners[0][0], corners[0][1], 0.0)]
    for f in range(8):
        c0, c1 = corners[f % 4], corners[(f + 1) % 4]
        dx, dy = (c1[0] - c0[0]) / (2 * a), (c1[1] - c0[1]) / (2 * a)
        z0 = f * 14 * rise
        run = 2 * a - STAIR_W
        for k in range(14):
            u = (k + 0.5) / 14
            cx = c0[0] + dx * (STAIR_W / 2 + run * u)
            cy = c0[1] + dy * (STAIR_W / 2 + run * u)
            size = (run / 14 + 0.02, STAIR_W, 0.05) if dx else (STAIR_W, run / 14 + 0.02, 0.05)
            kit.box(f"stair{f}.{k}", size, (cx, cy, z0 + (k + 1) * rise - 0.025), M["stair"])
        # the landing at the far corner, the handrail along the flight's outer side
        ztop = z0 + 14 * rise
        kit.box(f"landing{f}", (STAIR_W, STAIR_W, 0.06), (c1[0], c1[1], ztop - 0.03), M["stair"])
        ox, oy = (-dy * (STAIR_W / 2) * (1 if f % 4 in (0, 2) else 1)), (dx * (STAIR_W / 2))
        out = V((c0[0] + c1[0], c0[1] + c1[1], 0)) * 0.5
        sgn = V((out.x, out.y, 0)).normalized() if out.length > 0 else V((0, 0, 0))
        # (0.8 m up: my arms, 1.36 m across, pass over it and my legs pass inside it)
        p0 = V((c0[0], c0[1], z0 + 0.8)) + sgn * (STAIR_W / 2)
        p1 = V((c1[0], c1[1], ztop + 0.8)) + sgn * (STAIR_W / 2)
        _beam(kit, f"handrail{f}", p0, p1, 0.04, M["rail"])
        path.append((c1[0], c1[1], ztop))
    ctx["stair_path"] = path


def build_gate(kit, ctx, M):
    """The plank gate at the foot of the stairs, inside the legs: two posts and a gate that swings out (south) toward
    the fire road. There's no fence round the tower's foot, so nothing stands where it waits under the cab (its toes
    reach the legs' line) or where it follows me out onto the road."""
    wood = M["fence"]
    (x0, x1), y = GATE_X, GATE_Y
    for k, x in enumerate((x0, x1)):
        kit.box(f"gate.post{k}", (0.12, 0.12, 1.35), (x, y, 0.675), wood, bevel=0.02)
    hinge = kit.empty("gate", (x0 + 0.08, y, 0.0))
    span = x1 - x0 - 0.18
    n = 7
    for k in range(n):
        kit.box(f"gate.plank{k}", (0.19, 0.05, 1.05), (0.12 + (span - 0.24) * k / (n - 1), 0, 0.68), wood, hinge,
                bevel=0.01)
    for k, h in enumerate((0.32, 1.04)):
        kit.box(f"gate.bar{k}", (span, 0.06, 0.1), (span / 2, -0.05, h), wood, hinge)
    ang = math.atan2(0.72, span - 0.2)
    kit.box("gate.brace", (math.hypot(span - 0.2, 0.72), 0.05, 0.1), (span / 2, -0.09, 0.68), wood, hinge,
            rot=(0, -ang, 0))
    ctx["gate"] = hinge


def build_cab_props(kit, ctx, M):
    """In the cab: the radio (a plain black box with one green light), binoculars on the sill, the log sheet with
    ruled lines, and the plank door onto the catwalk in the west wall. No text anywhere."""
    z = CAB_Z
    _wbox(kit, "shelf", (-0.4, CAB - 0.34, z + 0.95), (0.9, CAB - 0.08, z + 0.99), M["frame"])
    rs = kit.empty("radioset", RADIO_SHELF)
    kit.box("radio", (0.3, 0.16, 0.14), (0, 0, 0.07), M["radio"], rs, bevel=0.015)
    kit.box("radio.knob", (0.04, 0.03, 0.04), (0.08, -0.09, 0.09), M["rail"], rs)
    led = kit.sphere("radio.light", 0.014, (-0.1, -0.085, 0.1), M["led"], rs, seg=8)
    led.visible_shadow = False
    kit.light("radioglow", "POINT", (-0.1, -0.16, 0.1), 0.25, "#3cff7a", size=0.02, parent=rs)
    ctx["led"], ctx["radioset"] = led, rs
    bn = kit.empty("binoculars", BINO_SILL)
    for sx in (-1, 1):
        kit.cyl(f"binoculars{sx}", 0.035, 0.16, (sx * 0.05, 0, 0), M["lamp_body"], bn, rot=(math.pi / 2, 0, 0), n=10)
    kit.box("binoculars.bridge", (0.06, 0.04, 0.03), (0, 0, 0), M["lamp_body"], bn)
    ctx["binoculars"] = bn
    _wbox(kit, "table", (-1.0, CAB - 0.8, z + 0.72), (0.2, CAB - 0.12, z + 0.76), M["frame"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"tableleg{sx}{sy}", (0.04, 0.04, 0.72), (-0.4 + sx * 0.55, CAB - 0.46 + sy * 0.3, z + 0.36), M["frame"])
    kit.box("logsheet", (0.22, 0.3, 0.006), (-0.5, CAB - 0.45, z + 0.765), M["logsheet"])
    hinge = kit.empty("door", (-CAB + 0.04, -DOOR_W / 2, z))
    kit.box("door.slab", (0.05, DOOR_W - 0.04, DOOR_H - 0.02), (0.0, DOOR_W / 2, DOOR_H / 2), M["wall"], hinge, bevel=0.01)
    ctx["door"] = hinge



def build_binocular_mask(kit, ctx, M):
    """The binocular view (L08, L09, L11): a black card with two soft round holes, carried by the camera."""
    cam = bpy.context.scene.camera
    ob = kit.plane("binocular mask", (0.3, 0.3), (0, 0, -0.06), M["bino"], cam)
    for k in ("visible_shadow", "visible_diffuse", "visible_glossy"):
        setattr(ob, k, False)
    ob.hide_render = True
    ctx["bino"] = ob


def bino_mat(kit, name="binocular mask"):
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs[0])
    holes = None
    for cx in (-0.0135, 0.0135):
        dx = _math(N, L, "SUBTRACT", sep.outputs["X"], cx)
        r = _math(N, L, "SQRT", _math(N, L, "ADD", _math(N, L, "MULTIPLY", dx, dx),
                                      _math(N, L, "MULTIPLY", sep.outputs["Y"], sep.outputs["Y"])))
        hole = _range(N, L, r, 0.0165, 0.0195)       # 0 inside a hole, 1 outside
        holes = hole if holes is None else _math(N, L, "MINIMUM", holes, hole)
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0)
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader")
    L.new(holes, mx.inputs[0])
    L.new(tr.outputs[0], mx.inputs[1])
    L.new(em.outputs[0], mx.inputs[2])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    L.new(mx.outputs[0], out.inputs["Surface"])
    return m



# ------------------------------------------------------------------------------------------------ the town (day)
TOWN = (1200.0, 0.0)
PL = 3.2                       # the pavement's height over the road


def tb(kit, name, lo, hi, mat):
    """A box from local town corners (x east along the street, y north, away from the road)."""
    return _wbox(kit, name, (TOWN[0] + lo[0], TOWN[1] + lo[1], lo[2]), (TOWN[0] + hi[0], TOWN[1] + hi[1], hi[2]), mat)


def gable(kit, name, x0, x1, y0, y1, z0, zr, mat):
    """A gable roof with its ridge along x."""
    X0, X1, Y0, Y1, Ym = TOWN[0] + x0, TOWN[0] + x1, TOWN[1] + y0, TOWN[1] + y1, TOWN[1] + (y0 + y1) / 2
    v = [(X0, Y0, z0), (X1, Y0, z0), (X1, Y1, z0), (X0, Y1, z0), (X0, Ym, zr), (X1, Ym, zr)]
    return kit.mesh_obj(name, v, [(0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5), (3, 2, 1, 0)], mat)


def window(kit, name, x0, x1, y, z0, z1, M, frame="t_cream"):
    tb(kit, name + ".f", (x0 - 0.15, y - 0.05, z0 - 0.15), (x1 + 0.15, y + 0.04, z1 + 0.15), M[frame])
    tb(kit, name, (x0, y - 0.1, z0), (x1, y + 0.03, z1), M["t_win"])


def house(kit, name, x0, x1, y0, y1, h, wall, roofm, M, doors=(), wins=()):
    tb(kit, name, (x0, y0, 0.0), (x1, y1, h), M[wall])
    gable(kit, name + ".roof", x0 - 0.5, x1 + 0.5, y0 - 0.6, y1 + 0.6, h, h + (y1 - y0) * 0.4, M[roofm])
    for i, (a, b, z0, z1) in enumerate(wins):
        window(kit, f"{name}.w{i}", a, b, y0, z0, z1, M)
    for i, a in enumerate(doors):
        tb(kit, f"{name}.d{i}", (a - 0.6, y0 - 0.08, 0.0), (a + 0.6, y0 + 0.02, 2.3), M["t_door"])


def build_town(kit, ctx, M):
    """The montage's street: balcony house (L01), cottage with a dormer and a garden (L03), a cellar with a stool and a
    pavement hatch (L04), an office with a basement window row (L05). No text, signs or numbers."""
    tb(kit, "t.base", (-90, -45, -PL - 0.6), (170, 50, -PL), M["t_road"])
    # the plinth the pavement stands on, broken by the two bays that open onto the road
    for k, (a, b) in enumerate(((-90, 55), (65, 76), (104, 170))):
        tb(kit, f"t.pave{k}", (a, -4.0, -PL), (b, 0.0, 0.0), M["t_pave"])
    tb(kit, "t.lawn", (-90, 0.0, -PL), (170, 50, 0.0), M["t_grass"])
    tb(kit, "t.hill", (-90, 48, -PL), (170, 90, 14), M["t_hill"])
    # the bays: a floor of boards, a back wall, a ceiling slab under the pavement
    for k, (a, b) in enumerate(((55, 65), (76, 104))):
        tb(kit, f"t.bayfloor{k}", (a, -4.0, -PL), (b, 0.0, -PL + 0.04), M["t_wood"])
        tb(kit, f"t.bayback{k}", (a, -0.3, -PL), (b, 0.0, 0.0), M["t_cream"])
        tb(kit, f"t.bayroof{k}", (a, -4.0, -0.6), (b, 0.0, 0.0), M["t_pave"])
        tb(kit, f"t.baysidel{k}", (a - 0.02, -4.0, -PL), (a + 0.3, 0.0, -0.6), M["t_stone"])
        tb(kit, f"t.bayside{k}", (b - 0.3, -4.0, -PL), (b + 0.02, 0.0, -0.6), M["t_stone"])
    # the road's kerb and a pale centre line
    for k, (a, b) in enumerate(((-90, 55), (65, 76), (104, 170))):
        tb(kit, f"t.kerb{k}", (a, -4.2, -PL), (b, -4.0, 0.0), M["t_stone"])
    # 1: the balcony house, bricks and lemon shutters; the balcony stands over the pavement
    house(kit, "h1", -9, 9, 0.0, 10.0, 9.0, "t_brick", "t_roof", M, doors=(0.0,),
          wins=((4.2, 6.2, 5.0, 7.0), (-7.4, -5.4, 5.0, 7.0), (-7.6, -5.8, 0.7, 1.9), (5.6, 7.4, 0.7, 1.9)))
    for i, xx in enumerate((-8.2, -4.6, 3.3, 6.9)):
        tb(kit, f"h1.shut{i}", (xx - 0.35, -0.12, 4.9), (xx + 0.35, 0.0, 7.1), M["t_lemon"])
    tb(kit, "h1.bdoor", (-1.0, -0.1, 2.4), (1.0, 0.0, 4.7), M["t_win"])
    tb(kit, "h1.bdoorf", (-1.2, -0.12, 2.4), (1.2, -0.05, 4.9), M["t_cream"])
    tb(kit, "h1.slab", (-3.6, -2.2, 2.1), (3.6, 0.0, 2.4), M["t_wood"])
    tb(kit, "h1.railtop", (-3.6, -2.2, 3.38), (3.6, -2.1, 3.44), M["t_cream"])
    tb(kit, "h1.railmid", (-3.6, -2.2, 2.85), (3.6, -2.14, 2.9), M["t_cream"])
    for i in range(7):
        xx = -3.55 + i * 1.18
        tb(kit, f"h1.post{i}", (xx - 0.05, -2.2, 2.4), (xx + 0.05, -2.1, 3.4), M["t_cream"])
    # 2: the cottage, set back behind a garden; a dormer window in its front slope
    tb(kit, "h2", (24, 4.0, 0.0), (38, 11.0, 3.4), M["t_cream"])
    gable(kit, "h2.roof", 23.4, 38.6, 3.4, 11.6, 3.4, 6.4, M["t_roofred"])
    tb(kit, "h2.chimney", (35.4, 7.0, 3.0), (36.8, 8.2, 7.4), M["t_brick"])
    tb(kit, "h2.door", (26.4, 3.92, 0.0), (27.8, 4.02, 2.2), M["t_door"])
    window(kit, "h2.w0", 30, 32.6, 3.98, 0.9, 2.3, M)
    window(kit, "h2.w1", 33.6, 36, 3.98, 0.9, 2.3, M)
    # the dormer (front face y = 4.9): sill, lintel, posts, a dark back, a little roof
    tb(kit, "dorm.sill", (28.9, 4.7, 3.95), (33.1, 5.0, 4.75), M["t_cream"])
    tb(kit, "dorm.lint", (28.9, 4.7, 5.75), (33.1, 5.0, 6.15), M["t_cream"])
    tb(kit, "dorm.pl", (28.9, 4.7, 4.75), (29.3, 5.0, 5.75), M["t_cream"])
    tb(kit, "dorm.pr", (32.7, 4.7, 4.75), (33.1, 5.0, 5.75), M["t_cream"])
    tb(kit, "dorm.back", (28.9, 6.5, 4.0), (33.1, 6.7, 6.2), M["t_dark"])
    tb(kit, "dorm.sidel", (28.9, 4.7, 4.0), (29.1, 6.7, 6.2), M["t_cream"])
    tb(kit, "dorm.sider", (32.9, 4.7, 4.0), (33.1, 6.7, 6.2), M["t_cream"])
    gable(kit, "dorm.roof", 28.6, 33.4, 4.6, 6.9, 6.15, 6.9, M["t_roofred"])
    # the front garden: a low hedge, flower beds, a fence along the pavement
    tb(kit, "gar.hedge", (22, 3.3, 0.0), (40, 3.8, 0.8), M["t_hill"])
    for i in range(14):
        xx = 22.3 + i * 1.3
        tb(kit, f"gar.pale{i}", (xx, 0.2, 0.0), (xx + 0.14, 0.34, 0.9), M["t_cream"])
    tb(kit, "gar.rail", (22, 0.2, 0.62), (40, 0.34, 0.74), M["t_cream"])
    for i in range(6):
        tb(kit, f"gar.flower{i}", (24 + i * 2.6, 2.4, 0.0), (24.5 + i * 2.6, 2.9, 0.5), M["t_flower"])
    # neighbours, to fill the street
    house(kit, "h3", -32, -12, 0.0, 9.0, 7.0, "t_blue", "t_roof", M, doors=(-22.0,),
          wins=((-29, -27, 3.5, 5.0), (-17, -15, 3.5, 5.0), (-29, -27, 1.0, 2.4)))
    house(kit, "h4", 12, 20, 0.0, 9.0, 6.0, "t_cream", "t_roofred", M, doors=(16.0,), wins=((13, 14.6, 3.2, 4.6),))
    house(kit, "h5", 42, 54, 0.0, 9.0, 7.5, "t_brick", "t_roof", M, doors=(48.0,), wins=((43.4, 45.2, 3.6, 5.2), (50.6, 52.4, 3.6, 5.2)))
    # 3: the cellar's house, its hatch in the pavement, a stool in the bay
    house(kit, "h6", 54.5, 65.5, 0.0, 9.0, 7.0, "t_blue", "t_roof", M, wins=((56, 58, 3.4, 5.0), (61.4, 63.4, 3.4, 5.0)))
    tb(kit, "hatch", (59.0, -3.1, 0.0), (61.0, -1.2, 0.06), M["t_dark"])
    tb(kit, "hatch.f", (58.9, -3.2, 0.0), (61.1, -1.1, 0.03), M["t_stone"])
    tb(kit, "stool", (59.75, -3.35, -PL), (60.25, -2.85, -PL + 0.6), M["t_wood"])
    # 4: the office front, its basement window row on the road
    tb(kit, "h7", (74, 0.0, 0.0), (106, 10.0, 10.0), M["t_stone"])
    for i in range(8):
        window(kit, f"h7.w{i}", 76.5 + i * 3.6, 78.5 + i * 3.6, 0.0, 3.2, 5.0, M)
        window(kit, f"h7.v{i}", 76.5 + i * 3.6, 78.5 + i * 3.6, 0.0, 6.4, 8.2, M)
    gable(kit, "h7.roof", 73.5, 106.5, -0.6, 10.6, 10.0, 11.5, M["t_roof"])
    for i, xx in enumerate((76.0, 82.0, 88.0, 94.0, 100.0, 104.0)):
        tb(kit, f"h7.mull{i}", (xx - 0.15, -4.0, -PL), (xx + 0.15, -3.7, -0.6), M["t_stone"])
    tb(kit, "h7.sillrow", (76, -4.0, -PL), (104, -3.7, -PL + 0.7), M["t_stone"])
    for i, xx in enumerate((79.0, 91.0, 97.0)):
        tb(kit, f"desk{i}", (xx - 1.0, -3.4, -PL), (xx + 1.0, -2.6, -PL + 0.82), M["t_wood"])
        tb(kit, f"desk{i}.top", (xx - 1.05, -3.45, -PL + 0.8), (xx + 1.05, -2.55, -PL + 0.86), M["t_cream"])
    # a few round trees on the hill behind
    rng = np.random.default_rng(3)
    for k in range(14):
        x, y = rng.uniform(-70, 150), rng.uniform(30, 70)
        r = rng.uniform(2.5, 4.0)
        kit.cyl(f"t.trunk{k}", 0.35, 3.0, (TOWN[0] + x, TOWN[1] + y, 1.5), M["t_door"])
        kit.sphere(f"t.crown{k}", r, (TOWN[0] + x, TOWN[1] + y, 3.0 + r * 0.8), M["t_hill"], seg=8)
    # a warm fill in the bays, where the plinth's shade keeps the sun out
    kit.light("bayfill", "POINT", (TOWN[0] + 70.0, TOWN[1] - 3.0, -1.0), 4500.0, "#fff1d8", size=2.0, shadow=False)
    kit.light("bayfill2", "POINT", (TOWN[0] + 90.0, TOWN[1] - 3.0, -1.0), 9000.0, "#fff1d8", size=2.0, shadow=False)
    kit.light("bayfill3", "POINT", (TOWN[0] + 60.0, TOWN[1] - 3.0, -0.8), 2500.0, "#fff1d8", size=2.0, shadow=False)
    # the parcel that drops onto the hatch (hidden until its cue)
    p = kit.empty("parcel", (TOWN[0] + 60.0, TOWN[1] - 2.2, 50.0))
    kit.box("parcel.box", (0.8, 0.6, 0.45), (0, 0, 0.225), M["t_parcel"], p, bevel=0.02)
    kit.box("parcel.s1", (0.06, 0.62, 0.47), (0, 0, 0.225), M["t_string"], p)
    kit.box("parcel.s2", (0.82, 0.06, 0.48), (0, 0, 0.225), M["t_string"], p)
    ctx["parcel"] = p


def open_hood(kit, who="me"):
    """rig.py's hood is a closed box whose front face sits 1 cm in front of the drawn face, so a hooded character
    has no face (pass 1's narrator read as a dark cube). This story's hood is rebuilt here once, open at the front
    and at the neck, with real thickness, so the face shows inside it. Only this story's cast is touched; no other
    story uses a hood, and rig.py is unchanged."""
    ob = bpy.data.objects.get(f"{who}.hood")
    if ob is None or ob.get("opened"):
        return
    from blocky import faces
    R, H = faces.HEAD_R, faces.HEAD_H
    sx, sy, sz = 2 * R + 0.34, 2 * R + 0.3, H + 0.3
    verts = kit.box_verts(sx, sy, sz)
    keep = [f for f in kit.BOX_FACES if f not in ((0, 1, 5, 4), (0, 3, 2, 1))]   # no front (-y), no bottom
    me = bpy.data.meshes.new(f"{who}.hood.open")
    me.from_pydata(verts, [], keep)
    me.update()
    for m in ob.data.materials:
        me.materials.append(m)
    ob.data = me
    ob.modifiers.clear()
    so = ob.modifiers.new("thick", "SOLIDIFY")
    so.thickness = 0.12
    so.offset = -1.0
    bv = ob.modifiers.new("bevel", "BEVEL")
    bv.width = 0.08
    bv.segments = 2
    bv.limit_method = "NONE"
    for p in me.polygons:
        p.use_smooth = True
    try:
        ob.modifiers.new("wn", "WEIGHTED_NORMAL").keep_sharp = True
    except Exception:
        pass
    ob["opened"] = True


def place_lamp(ctx, tl, t):
    """The lantern: a `lamp` cue's "pos" (set down), or "hand" (an arm's name, e.g. "me.arm-1") with an "offset"
    from that hand's end (its bail hanging from my block hand)."""
    # the latest cue decides: a "pos" cue sets it down (and lets go), a "hand" cue picks it up
    c = _last([c for c in _cues(tl, "lamp") if "pos" in c or "hand" in c], t) or {}
    lamp = ctx["lamp"]
    if c.get("hand"):
        arm = bpy.data.objects.get(c["hand"])
        if arm is not None:
            end = arm.matrix_world @ V((0.0, 0.0, -1.75))
            off = c.get("offset", [0.0, 0.0, -0.55])
            lamp.location = (end.x + off[0], end.y + off[1], end.z + off[2])
            return
    lamp.location = tuple(c.get("pos", LAMP_DECK))


def _last(cs, t):
    """The latest cue at or before t (cues are in time order)."""
    out = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            out = c
    return out


def _ease_to(cs, t, key, default):
    """A value that eases from the previous cue's to this cue's over its "dur" (seconds)."""
    prev, cur = default, None
    for c in cs:
        if key in c and c["t"] <= t + 1e-9:
            prev, cur = (cur[key] if cur else prev), c
    if cur is None:
        return default
    u = _ss((t - cur["t"]) / max(1e-6, cur.get("dur", 0.0))) if cur.get("dur") else 1.0
    return prev + (cur[key] - prev) * u



def carry(ctx, tl, t, cue, key, home, off, both=False):
    """A prop in my hand (a cue's "hand", an arm's name; "both" holds it between both hands) or back home."""
    ob = ctx[key]
    hand = _switch(_cues(tl, cue), "hand", t, None)
    if not hand:
        ob.location = home
        ob.rotation_euler = (0, 0, 0)
        return
    arms = [bpy.data.objects.get(hand)]
    if both:
        arms.append(bpy.data.objects.get(hand.replace("arm-1", "arm1")))
    ends = [a.matrix_world @ V((0.0, 0.0, -1.75)) for a in arms if a is not None]
    if not ends:
        return
    e = sum(ends, V((0, 0, 0))) / len(ends)
    rot = arms[0].matrix_world.to_euler()
    ob.location = (e.x + off[0], e.y + off[1], e.z + off[2])
    ob.rotation_euler = (0, 0, rot.z)


# ------------------------------------------------------------------------------------------------ small props
def build_lamp2(kit, ctx, M):
    """Ollie's own lantern (the same design as mine): carried by a hand cue, otherwise put away under the ground."""
    root = kit.empty("lamp2", (0, 0, -60))
    kit.box("lamp2.base", (0.3, 0.3, 0.05), (0, 0, 0.025), M["lamp_body"], root, bevel=0.01)
    kit.box("lamp2.cap", (0.3, 0.3, 0.06), (0, 0, 0.37), M["lamp_body"], root, bevel=0.01).visible_shadow = False
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"lamp2.post{sx}{sy}", (0.025, 0.025, 0.3), (sx * 0.135, sy * 0.135, 0.2), M["lamp_body"], root)
    kit.box("lamp2.glow", (0.24, 0.24, 0.29), (0, 0, 0.195), M["lamp_glow"], root).visible_shadow = False
    kit.cyl("lamp2.bail", 0.012, 0.2, (0, 0, 0.52), M["lamp_body"], root, rot=(0, math.pi / 2, 0), n=8)
    for sx in (-1, 1):
        kit.box(f"lamp2.bailside{sx}", (0.015, 0.015, 0.1), (sx * 0.1, 0, 0.47), M["lamp_body"], root)
    kit.light("lamp2light", "POINT", (0, 0, 0.2), 160.0, "#ffd0a0", size=0.2, parent=root)
    ctx["lamp2"] = root


def build_key_and_lock(kit, ctx, M):
    """The plain iron key on its nail by the cab door, and the padlock on the gate."""
    z = CAB_Z + 1.55
    x, y = -CAB + 0.04, 1.0                      # on the west wall, north of the door
    kit.cyl("nail", 0.012, 0.08, (x + 0.04, y, z + 0.1), M["iron"], rot=(0, math.pi / 2, 0), n=6)
    key = kit.empty("key.cab", (x + 0.1, y, z))
    kit.cyl("key.ring", 0.035, 0.012, (0, 0, 0.06), M["iron"], key, rot=(0, math.pi / 2, 0), n=14)
    kit.box("key.stem", (0.012, 0.012, 0.16), (0, 0, -0.06), M["iron"], key)
    kit.box("key.bit", (0.012, 0.04, 0.03), (0, 0.016, -0.12), M["iron"], key)
    # the padlock: a body and a shackle, hung on the gate's hasp (closed) or swung open and hanging (open)
    lock = kit.empty("padlock", (GATE_X[1] - 0.2, GATE_Y - 0.12, 0.85))
    kit.box("padlock.body", (0.11, 0.05, 0.1), (0, 0, 0), M["iron"], lock, bevel=0.008)
    kit.cyl("padlock.shackle", 0.035, 0.012, (0, 0, 0.07), M["iron"], lock, rot=(math.pi / 2, 0, 0), n=10)
    ctx["padlock"] = lock


def build_mask(kit, ctx, M):
    build_binocular_mask(kit, ctx, M)


# ------------------------------------------------------------------------------------------------ lights
def build_lights(kit, ctx):
    lp = ctx["lamp"].location
    face = kit.light("facekey", "POINT", (0, 0, 0), 12.0, "#ffd9a0", size=0.15, shadow=False)
    face.visible_glossy = False
    fill = kit.light("fill", "SUN", (0, 0, 60), 1.5, "#8ea6c4", rot=(math.radians(66), 0, math.radians(70)))
    fill.data.angle = math.radians(25)
    sun = kit.light("sun", "SUN", (0, 0, 60), 0.0, "#efeadc", rot=SUN_NORTH)
    sun.data.angle = math.radians(30)
    for nm in ("fill", "lamp", "sun"):
        kit.LIGHTS[nm]["obj"].visible_glossy = nm not in ("lamp",)
    ctx["need_me_links"] = True
    lamp_parts = [o for o in ctx["lamp"].children if o.type == "MESH"]
    link_lights(kit, "not the lantern", ["lamp"], lamp_parts, "EXCLUDE")


# ------------------------------------------------------------------------------------------------ looks
NIGHT_GAINS = {"sun": 0.0, "bayfill": 0.0, "bayfill2": 0.0, "bayfill3": 0.0}
DAY_GAINS = {"fill": 0.0, "lamp": 0.35, "facekey": 0.0, "bayfill": 0.0, "bayfill2": 0.0, "bayfill3": 0.0}
SUN_NORTH = (math.radians(42), 0, math.radians(12))     # the sun in the south, shining north, on faces that look south
LOOKS = {
    # noon in the town: bright, a hard sun from the south, the bays lit by their own fill
    "town": {"fog": "#d6e6f2", "density": 0.0012, "start": 60.0, "sky": "#9fcdf2", "sky_strength": 1.15, "exposure": 0.0,
             "cards": {}, "gains": {"fill": 0.0, "lamp": 0.0, "facekey": 0.0, "bayfill": 1.0, "bayfill2": 1.0, "bayfill3": 1.0},
             "sun": 4.0, "sun_rot": SUN_NORTH},
    # a clear cool morning at the tower: pearl light, the sun low in the south on the faces at the gate
    "clear": {"fog": "#c4ccd2", "density": 0.0022, "start": 40.0, "sky": "#cdd8e0", "sky_strength": 0.9,
              "exposure": 0.8, "cards": {}, "gains": DAY_GAINS, "sun": 5.0, "sun_rot": SUN_NORTH},
    # night round the cab: blue-grey fog, one steady amber lamp
    "night": {"fog": "#2a3238", "density": 0.034, "start": 3.0, "sky": "#2c353c", "sky_strength": 1.0,
              "exposure": 1.6, "cards": ["fog.near", "fog.tower", "fog.neck", "fog.behind", "fog.far"],
              "gains": NIGHT_GAINS},
    # the cab seen from outside and below, the fog top just under the catwalk
    "nighthigh": {"fog": "#2a3238", "density": 0.04, "start": 3.0, "sky": "#2c353c", "sky_strength": 1.0,
                  "exposure": 1.6, "gains": NIGHT_GAINS,
                  "cards": {"fog.tower": (0.0, -12.0, CAB_Z - 1.2, 0.0), "fog.behind": (0.0, 14.0, CAB_Z - 1.0, 0.0),
                            "fog.near": (16.0, 0.0, CAB_Z - 1.4, 90.0), "fog.far": (0.0, -45.0, 60.0, 20.0)}},
    # the valley from the cab at night: thin air over the town's lights, fog lying on the floor
    "nightvalley": {"fog": "#2a3238", "density": 0.0016, "start": 20.0, "sky": "#2a3238", "sky_strength": 1.0,
                    "exposure": 1.5, "cards": {}, "gains": NIGHT_GAINS, "smoke": 0.8, "smoke_col": "#566168"},
    # the same through the binoculars (the mask is a card on the camera)
    "nightbino": {"fog": "#2a3238", "density": 0.0016, "start": 20.0, "sky": "#2a3238", "sky_strength": 1.0,
                  "exposure": 1.5, "cards": {}, "gains": NIGHT_GAINS, "smoke": 0.8, "smoke_col": "#566168", "bino": True},
}


def _kit_fog_nodes():
    out = []
    for m in bpy.data.materials:
        if not m.use_nodes or m.name.startswith("fog "):
            continue
        for cam in [n for n in m.node_tree.nodes if n.type == "CAMERA"]:
            try:
                sub = cam.outputs["View Distance"].links[0].to_node
                mx = sub.outputs[0].links[0].to_node
                mul = mx.outputs[0].links[0].to_node
                ex = mul.outputs[0].links[0].to_node
                inv = ex.outputs[0].links[0].to_node
                mix = inv.outputs[0].links[0].to_node
                em = mix.inputs[2].links[0].from_node if mix.inputs[2].links else None
                out.append((sub, mul, em))
            except (IndexError, KeyError, AttributeError):
                continue
    return out


def apply_look(kit, ctx, name):
    if ctx.get("look") == name:
        return
    lk = LOOKS[name]
    c = kit.col(lk["fog"])
    for sub, mul, em in ctx.setdefault("fog_nodes", _kit_fog_nodes()):
        sub.inputs[1].default_value = lk["start"]
        mul.inputs[1].default_value = -lk["density"]
        if em is not None:
            em.inputs["Color"].default_value = c
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = kit.col(lk["sky"])
    bg.inputs["Strength"].default_value = lk["sky_strength"]
    bpy.context.scene.view_settings.exposure = lk["exposure"]
    cards = lk["cards"]
    for ob in ctx["fog"]:
        ob.hide_render = ob.name not in cards
        if isinstance(cards, dict) and ob.name in cards:
            x, y, top, yaw = cards[ob.name]
            ob.location = (x, y, top)
            ob.rotation_euler = (0, 0, math.radians(yaw))
        elif ob.name in FOG_CARDS:
            x, y, top, w, h, yaw = FOG_CARDS[ob.name][1]
            ob.location = (x, y, top)
            ob.rotation_euler = (0, 0, math.radians(yaw))
    kit.LIGHTS["sun"]["base"] = lk.get("sun", 0.0)
    kit.LIGHTS["sun"]["obj"].rotation_euler = lk.get("sun_rot", SUN_NORTH)
    for n in LOOK_NODES["smoke"]:
        n.outputs[0].default_value = lk.get("smoke", 0.0)
    sm = kit.MATS.get("valley fog")
    if sm is not None:
        em = next(nd for nd in sm.node_tree.nodes if nd.type == "EMISSION")
        em.inputs["Color"].default_value = kit.col(lk.get("smoke_col", "#566168"))
    if ctx.get("bino"):
        ctx["bino"].hide_render = not lk.get("bino", False)
    ctx["look"] = name


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    ctx = {"story": story}
    bpy.context.scene.cycles.transparent_max_bounces = 8
    M = materials(kit)
    ctx["M"] = M
    ctx["pine"] = pine_data(kit, "pine", M)
    lm = pine_data(kit, "larch", M)
    lm.materials[0] = M["larch"]
    ctx["larch"] = lm
    rng = np.random.default_rng(14)
    build_tower(kit, ctx, M)
    build_stairs(kit, ctx, M)
    build_cab_props(kit, ctx, M)
    build_key_and_lock(kit, ctx, M)
    build_gate(kit, ctx, M)
    build_land(kit, ctx, M)
    build_forest(kit, ctx, M, rng)
    build_valley(kit, ctx, M)
    build_town(kit, ctx, M)
    build_fog(kit, ctx, M)
    build_binocular_mask(kit, ctx, M)
    ctx["lamp"].location = LAMP_DECK
    build_lamp2(kit, ctx, M)
    build_lights(kit, ctx)
    for who in story.get("cast", {}):
        build_hourglass(kit, ctx, M, who)
    return ctx


# ------------------------------------------------------------------------------------------------ animate
def _cone_box(kit, name, size, loc, mat, parent, rot=(0, 0, 0)):
    return kit.box(name, size, loc, mat, parent, rot=rot, bevel=0.0)


def decor(kit, ctx):
    """Once the cast exists: Ollie's chevron and beanie band, and the older Ollie's beard, badge, belt key and beanie
    band. Everything stands 1 cm or more proud of what it sits on."""
    from blocky import faces
    if ctx.get("decor") or bpy.data.objects.get("ollie.torso") is None:
        return
    ctx["decor"] = True
    M = ctx["M"]
    cream = kit.plastic("#efe6c8", 0.7, "cream")
    grey = kit.plastic("#7d838c", 0.8, "shirt grey")
    R, H = faces.HEAD_R, faces.HEAD_H
    top = H / 2
    # the teen: a grey shirt showing down the open front with a cream chevron, and a cream band on the beanie
    t = bpy.data.objects["ollie.torso"]
    kit.box("ollie.shirtpanel", (0.74, 0.04, 1.86), (0, -0.52, 1.0), grey, t, bevel=0.01)
    for sx in (-1, 1):
        kit.box(f"ollie.chev{sx}", (0.42, 0.03, 0.11), (sx * 0.16, -0.555, 1.3 - 0.0), cream, t,
                rot=(0, -sx * 0.62, 0), bevel=0.01)
    hg = bpy.data.objects["ollie.headg"]
    kit.box("ollie.band", (2 * R + 0.22, 2 * R + 0.22, 0.17), (0, 0.0, top - 0.15), cream, hg, bevel=0.05)
    # the older Ollie
    hg2 = bpy.data.objects["ollie_old.headg"]
    t2 = bpy.data.objects["ollie_old.torso"]
    fade = kit.plastic("#e3d2ae", 0.8, "faded cream")
    kit.box("ollie_old.band", (2 * R + 0.22, 2 * R + 0.22, 0.17), (0, 0.0, top - 0.15), fade, hg2, bevel=0.05)
    brown = kit.plastic("#3a2415", 0.85, "beard brown")
    ash = kit.plastic("#8c8884", 0.85, "beard grey")
    kit.box("ollie_old.chin", (0.84, 0.26, 0.2), (0, -R + 0.06, -top + 0.12), brown, hg2, bevel=0.06)
    kit.box("ollie_old.jaw", (1.0, 0.34, 0.1), (0, -R + 0.16, -top + 0.03), brown, hg2, bevel=0.04)
    for sx in (-1, 1):
        kit.box(f"ollie_old.side{sx}", (0.17, 0.62, 0.62), (sx * (R - 0.03), -0.12, -0.22), ash, hg2, bevel=0.06)
    brass = M["badge"]
    kit.cyl("ollie_old.badge", 0.16, 0.025, (0.5, -0.52, 1.5), brass, t2, rot=(math.pi / 2, 0, 0), n=18)
    kit.box("ollie_old.badgebar", (0.34, 0.03, 0.07), (0.5, -0.525, 1.18), brass, t2, bevel=0.01)
    ring = kit.cyl("ollie_old.ring", 0.12, 0.03, (-0.78, -0.56, 0.42), M["iron"], t2, rot=(math.pi / 2, 0, 0), n=14)
    kit.box("ollie_old.key", (0.07, 0.04, 0.62), (-0.78, -0.58, 0.04), M["iron"], t2, bevel=0.01)
    kit.box("ollie_old.keybit", (0.2, 0.04, 0.1), (-0.7, -0.58, -0.2), M["iron"], t2)
    # the cold fill keeps off me, my face key lights only me
    me = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("me.")]
    link_lights(kit, "not me", ["fill"], me, "EXCLUDE")
    link_lights(kit, "me only", ["facekey"], me, "INCLUDE")


def mover_state(tl, t):
    """The crossing lamp: eased from key to key (a cue's pos, radius and dur), None when the last cue turned it off."""
    ks = _cues(tl, "mover")
    cur, prev = None, None
    for c in ks:
        if c["t"] <= t + 1e-9:
            prev, cur = cur, c
    if cur is None or not cur.get("on", True):
        return None
    p0 = prev["pos"] if prev and prev.get("on", True) else cur["pos"]
    r0 = prev["r"] if prev and prev.get("on", True) else cur["r"]
    d = cur.get("dur", 0.0)
    u = min(1.0, max(0.0, (t - cur["t"]) / d)) if d > 0 else 1.0
    return ([a + (b - a) * u for a, b in zip(p0, cur["pos"])], r0 + (cur["r"] - r0) * u)


def animate(kit, story, tl, t, ctx):
    from blocky import acting
    over = {}
    open_hood(kit)
    decor(kit, ctx)
    look = _switch(_cues(tl, "look"), "id", t, "night")
    apply_look(kit, ctx, look)
    lk = LOOKS[look]
    over.update(lk.get("gains", {}))
    bpy.data.cameras["cam"].clip_end = 2600.0
    # the pines grow a night at a time; the town's lights (and Ollie's) with them
    night = _switch(_cues(tl, "night"), "n", t, 1)
    if ctx.get("night") != night:
        ctx["night"] = night
        for ob in ctx["tree_objs"]:
            s = ob["s0"] * PINE_SCALE[night]
            ob.scale = (s, s, s)
        for ob in ctx["town_lights"]:
            ob.hide_render = ob["level"] > min(night, 3)
    where = _switch(_cues(tl, "ollie"), "where", t, "none")
    cue = [c for c in _cues(tl, "ollie") if c["t"] <= t + 1e-9]
    k = _ss((t - cue[-1]["t"]) / max(1e-6, cue[-1].get("dur", 1.2))) if cue else 0.0
    for nm, ob in ctx["ollie_at"].items():
        ob.hide_render = nm != where or k <= 0.001
    kit.MATS["ollie glow"].node_tree.nodes["Emission"].inputs["Strength"].default_value = 14.0 * k
    # the crossing lamp
    ms = mover_state(tl, t)
    mv = ctx["mover"]
    if ms is None:
        mv.location = (0, 0, -80)
        kit.LIGHTS["walklamp"]["obj"].location = (0, 0, -80)
        over["walklamp"] = 0.0
    else:
        pos, r = ms
        mv.location = tuple(pos)
        mv.scale = (r, r, r)
        kit.LIGHTS["walklamp"]["obj"].location = (pos[0], pos[1], pos[2] + 0.1)
        over["walklamp"] = 1.0 if r < 1.0 else 0.0
    # the door, the gate, the padlock, the radio
    ctx["door"].rotation_euler = (0, 0, -math.radians(100) * _ease_to(_cues(tl, "door"), t, "open", 0.0))
    ctx["gate"].rotation_euler = (0, 0, -math.radians(95) * _ease_to(_cues(tl, "gate"), t, "open", 0.0))
    lock_open = _switch(_cues(tl, "padlock"), "open", t, False)
    pl = ctx["padlock"]
    pl.location = (GATE_X[1] - 0.2, GATE_Y - 0.12, 0.85 - (0.12 if lock_open else 0.0))
    pl.rotation_euler = (0, 0.5 if lock_open else 0.0, 0)
    radio = _switch(_cues(tl, "radio"), "on", t, False)
    over["radioglow"] = 1.0 if radio else 0.0
    ctx["led"].hide_render = not radio
    # the parcel drops onto the hatch
    pc = _cues(tl, "parcel")
    if pc and pc[0]["t"] <= t:
        d = 1.0 - _ss((t - pc[0]["t"]) / 0.22)
        ctx["parcel"].location = (TOWN[0] + 60.0, TOWN[1] - 2.2, 0.06 + 3.0 * d * d)
    else:
        ctx["parcel"].location = (TOWN[0] + 60.0, TOWN[1] - 2.2, 50.0)
    # sitting (an acting key "sit": true), short steps on the steep stairs
    for who in story.get("cast", {}):
        sit = _switch(tl["acting"].get(who, []), "sit", t, False)
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg is not None and sit:
                leg.rotation_euler = (-math.pi / 2, 0, 0)
        root = bpy.data.objects.get(who)
        if root is not None:
            p = root.location
            if max(abs(p.x), abs(p.y)) < STAIR_A + STAIR_W and 0.3 < p.z < CAB_Z - 0.3:
                for sx in (-1, 1):
                    leg = bpy.data.objects.get(f"{who}.leg{sx}")
                    if leg is not None:
                        r = leg.rotation_euler
                        leg.rotation_euler = (r.x / 3.0, r.y, r.z)
    bpy.context.view_layer.update()
    place_lamp(ctx, tl, t)
    carry(ctx, tl, t, "lamp2", "lamp2", (0.0, 0.0, -60.0), (0.0, 0.0, -0.55))
    carry(ctx, tl, t, "radio", "radioset", RADIO_SHELF, (0.0, -0.06, 0.02))
    carry(ctx, tl, t, "binos", "binoculars", BINO_SILL, (0.0, -0.08, 0.05), both=True)
    k2 = 1.0 if _switch(_cues(tl, "lamp2"), "hand", t, None) else 0.0
    over["lamp2light"] = k2
    k = _switch(_cues(tl, "lampglow"), "k", t, 1.0)
    for nd in kit.MATS["lamp glow"].node_tree.nodes:
        if nd.type == "EMISSION":
            nd.inputs["Strength"].default_value = 0.12 * k
    ctx["lamp"].rotation_euler = (0, 0, 0)
    ctx["lamp2"].rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    # my face key rides my head
    hg = bpy.data.objects.get("me.headg")
    if hg is not None:
        m = hg.matrix_world
        fd = (m.to_3x3() @ V((0, -1, 0))).normalized()
        c = m.translation
        kit.LIGHTS["facekey"]["obj"].location = (c.x + fd.x * 0.6, c.y + fd.y * 0.6, c.z - 0.45)
    over["facekey"] = over.get("facekey", 1.0) * _switch(_cues(tl, "facekey"), "gain", t, 1.0)
    # the marker over every head
    for who in story.get("cast", {}):
        place_hourglass(ctx, tl, t, who, acting.state(tl, who, t))
    return over
