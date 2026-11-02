"""Lookout: a fire lookout tower over an autumn forest in fog, and the giant. Built from kit.py's parts (batch 2,
story 3, ep14; nothing here is shared with another story's set).

Coordinates: the ground at the tower's foot is z = 0 and the tower stands on (0, 0). Its four braced steel legs
rise to the cab: a 4 x 4 m wooden cab (x, y in -CAB .. CAB) whose floor's top is CAB_Z = 19.6, glass on all four
sides from the sill to the header, under a metal pyramid roof. The plank catwalk runs WALK = 1 m round it at the
same height, with a waist-high metal rail along its outer edge (+-WALK_OUT). A character facing -y has yaw 0.

THE GIANT (brief, "The creature"; built once by build_giant(), posed only by pose_giant()): our own R6 body plan
at 13.5 times my 1.75 m, built from the forest out of the same kind of game parts as the narrator (pass 2, note 21):
square bevelled timbers, flat colours and solid moss tops. 23.6 m tall, 18.4 m across the arms. Legs and arms
4.6 x 4.6 x 9.2 m, each a bundle of four square posts; the torso a log-cabin wall of 0.92 m timbers, 9.2 wide, 9.2
tall and 4.6 deep with crossed ends at its corners; bark #3b2a1e, timber ends grey-brown (55 to 70% of #6e5a44,
never pale), moss on every face that looks up. Two faceted block boulders (3.9 and 3.6 m, #7e8378, moss on their
upper facets) sit on its shoulders and rise to the middle of its head, three saplings on its left stone and one on
its right. The head is a 14-faceted hollow stump 5 m across and tall with a broken, mossy rim; its front opens into
a dark almond-shaped split 2.5 x 3.3 m (the brief's "about 2.8 x 3": a round opening read as a face, an arch as a
lit doorway), 3.8 m deep. Two warm lights (0.35 m, 1.2 m apart) hang 1.5 m inside it, in its upper part, and
faintly light its walls. No mouth, nose, carving or smile. Its feet are flat with four root toes at the front. Its
front is local -y (like the rig), its origin the ground under its middle. productions/ep14-lookout/designer-notes.md
("Creature test still") has the numbers and the lighting.

Cues read here (all optional):
- giant: {"pos": [x, y, z], "yaw": deg, "head": deg (turn, 60 at most), "pitch": deg (a hunch from the hip),
  "stride": deg (each leg's swing from the hip), "hidden": bool} where the giant is and how it holds itself
- look: {"id": "night" | "day"} the whole light from here (LOOKS: fog, sky, exposure, suns, gains, fog cards)
- lamp: {"pos": [x, y, z]} set down, or {"hand": "me.arm-1", "offset": [x, y, z]} its bail hanging from a hand
- shot: {"look": {...} or null} one shot's own lights (shot_look below)
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
    """The ground's height: the summit plateau, the long fall south along the road, the drop past the shelf to the
    valley, and the higher ridge to the north."""
    z = -0.2 * max(0.0, -y - 20.0) - 0.05 * max(0.0, abs(x) - 24.0)
    z += 0.16 * max(0.0, y - 110.0) - 0.0006 * max(0.0, y - 260.0) ** 2
    if y < -272.0:
        z = max(VALLEY_Z, z - 1.6 * (-272.0 - y))
        z += 0.3 * max(0.0, -y - 1080.0)          # the valley's far side rises into low hills
    # small bumps, smoothed to nothing on the plateau, along the road and on the shelf, so the generator (no
    # Blender) can place me on the ground there with terrain_smooth()
    k = min(1.0, max(0.0, (math.hypot(x, y) - 18.0) / 20.0), max(0.0, (road_dist(x, y) - 6.0) / 10.0),
            max(0.0, (math.hypot(x - SHELF[0], y - SHELF[1]) - 14.0) / 10.0))
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


# ------------------------------------------------------------------------------------------------ the giant
G_SCALE = 13.5                # times my height
LEG = (4.6, 4.6, 9.2)
TORSO = (9.2, 4.6, 9.2)
HIP_Z = 9.2
NECK_Z = 18.4                 # the torso's top
ARM_X = 6.9                   # the arms' centres, out from the middle
ARM_PIVOT = 8.05              # the shoulder pivot above the torso's base (its top is 1.15 above it)
HEAD_R = 2.5                  # the stump: 5 m across
HEAD_H = 5.0                  # ... and 5 m tall to its rim (the rim is broken, +-0.25)
HOLLOW_W, HOLLOW_H = 2.5, 3.3           # the brief's "about 2.8 x 3", as an almond: it reads as a split in the
                                         # wood, never a round face or a lit doorway
HOLLOW_Z = 2.5                # the hollow's middle above the head's base: the lights at 20.9 m standing
LIGHT_SEP = 1.2
LIGHT_IN = 1.5                # how far inside the hollow's mouth the lights hang
LIGHT_R = 0.175               # 0.35 m each (the ember shader fades its rim, so it reads as a glow, not a disc)
LIGHT_Z = HOLLOW_Z + 0.6      # pass 2: in the hollow's upper third, so they peer down out of it (21.5 m standing)
STUMP_FACETS = 14             # pass 2 (note 21): the stump is a faceted block part, not a sculpted trunk
LOG_D = 0.92                  # the torso's logs
HERO_PINES = ((16.5, -10.0, 15.5), (9.5, -24.0, 16.2),      # (the second clear of its walk down the road)
             
              # round its walk-up spot in 03 (the scale wide): their tops reach its chest
              (-44.5, -10.0, 15.8), (-43.0, 4.0, 16.6), (-14.0, -20.5, 15.2), (-30.5, -25.5, 16.2),
              (-46.0, -21.0, 14.8), (-39.0, -26.5, 15.6))
# (x, y, radius): no forest pine where the giant stands. 13.5 m clears its arms (9.2 m out) plus a pine's lowest
# branches (about 4 m), so nothing passes through it (contact probe, pass 2)
CLEAR = ((2.45, -8.0, 13.5), (-28.0, -8.0, 15.5), (-19.0, -1.0, 13.0), (-36.0, -14.0, 13.0),   # the walk up
         (8.0, -9.0, 12.0))                                                                     # the lean
RIM_AT = (3.0, -30.0, 21.0)   # the night rim, low behind the giant's scare spot: it grazes edges, not tops


def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


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


def materials(kit):
    return {
        "bark": bark_mat(kit, "bark", cell=3.2),
        "bark_limb": bark_mat(kit, "bark limb", stretch=(0.7, 0.7, 0.22), cell=2.6),
        "logend": logend_mat(kit),
        "stump": bark_mat(kit, "stump bark", "#3b2a1e", stretch=(0.75, 0.75, 0.14), cell=3.6, bump=0.8,
                          spill=(HEAD_H - 0.05, 0.35)),
        "hollow": hollow_mat(kit),
        "lip": bark_mat(kit, "hollow lip", "#24180f", moss=False, stretch=(1.2, 1.2, 1.2), cell=3.0),
        "stone": stone_mat(kit),
        "needles": matte(kit, "needles", "#1e2a22", 0.9, (4.0, 0.6)),
        "trunk": bark_mat(kit, "pine trunk", "#2b2019", moss=False, cell=6.0),
        "eyes": ember_mat(kit, "giant lights"),
        "tbark": block_bark_mat(kit, "timber bark"),
        "tbark_limb": block_bark_mat(kit, "limb bark", streak=(2.4, 2.4, 0.3)),
        "tend": block_end_mat(kit),
        "sbark": block_bark_mat(kit, "stump block bark", streak=(3.0, 3.0, 0.35), bump=0.3),
        "bstone": block_stone_mat(kit),
        "gstone": block_stone_mat(kit, "giant stone", "#4a5445"),
        "sprout": matte(kit, "spring needles", "#4f8f36", 0.9, (4.0, 0.6)),
        "core": matte(kit, "giant core", "#120c08", 1.0),
        "ground": ground_mat(kit),
        "road": road_mat(kit),
        "river": river_mat(kit),
        "smoke": smoke_mat(kit),
        "smudge": smoke_mat(kit, "burn smudge", "#7a6e62"),
        "stair": kit.planks("#5a4b3b", "#3d3328", 1.0, "X", "stair planks"),
        "fence": matte(kit, "fence wood", "#4a3c2e", 0.9, (2.0, 0.7)),
        "radio": kit.plastic("#121214", 0.55, "radio body"),
        "led": kit.emit("#3cff7a", 3.0, "radio light"),
        "logsheet": ruled_mat(kit),
        "water": matte(kit, "print water", "#0c0f10", 0.55),
        "mud": matte(kit, "mud", "#2a2219", 0.95, (1.5, 0.6)),
        "moss": matte(kit, "moss patch", "#3b4f1e", 0.95, (4.0, 0.6)),
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
        "fog_near": fog_card_mat(kit, "fog near", "#3a4550", 0.75),
        "fog_far": fog_card_mat(kit, "fog far", "#46525c", 0.85, (0.08, 0.08, 0.3), 5.0),
        "fog_neck": fog_card_mat(kit, "fog neck", "#3c4852", 0.92, (0.18, 0.18, 0.45), 4.0),
        "fog_day": fog_card_mat(kit, "fog day", "#cdd0cc", 0.8, (0.05, 0.05, 0.35), 4.0, ("#b8bcb8", 0.0045, 20.0)),
        "fog_dayback": fog_card_mat(kit, "fog dayback", "#c3c7c3", 0.97, (0.02, 0.02, 0.05), 60.0,
                                    ("#b8bcb8", 0.0045, 20.0)),
    }


# ------------------------------------------------------------------------------------------------ meshes


def _set_mats(ob, mats, index_of):
    for m in mats[1:]:
        ob.data.materials.append(m)
    for p in ob.data.polygons:
        p.material_index = index_of(p)


def log_mesh(kit, name, r, length, M, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), seed=0, n=14, segs=6,
             taper=0.05, bow=0.02, wobble=0.05, side="bark"):
    """One round log along its own z: a slightly bowed, tapering, lumpy cylinder with cut ends (end grain)."""
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 100, 3)
    verts, faces = [], []
    for k in range(segs + 1):
        u = k / segs
        z = -length / 2 + length * u
        rr = r * (1 + taper / 2 - taper * u)
        ox = bow * length * (1 - (2 * u - 1) ** 2)
        for j in range(n):
            a = 2 * math.pi * j / n
            w = 1 + wobble * mnoise.noise(V((math.cos(a) * 1.4 + ph[0], math.sin(a) * 1.4 + ph[1], z * 0.9 + ph[2])))
            verts.append((ox + rr * w * math.cos(a), rr * w * math.sin(a), z))
    for k in range(segs):
        for j in range(n):
            j2 = (j + 1) % n
            faces.append((k * n + j, k * n + j2, (k + 1) * n + j2, (k + 1) * n + j))
    nside = len(faces)
    faces.append(tuple(reversed(range(n))))
    faces.append(tuple(range(segs * n, segs * n + n)))
    ob = kit.mesh_obj(name, verts, faces, M[side], parent, loc, rot)
    _set_mats(ob, [M[side], M["logend"]], lambda p: 0 if p.index < nside else 1)
    for p in ob.data.polygons:
        p.use_smooth = p.index < nside
    return ob


ALONG_X = (0.0, math.pi / 2, 0.0)
ALONG_Y = (-math.pi / 2, 0.0, 0.0)


def timber(kit, name, w, d, length, M, parent, loc, rot=(0, 0, 0), side="tbark", end="tend", bevel=0.12,
           taper=0.0):
    """One block-world timber along its own z: a square-ish bevelled box (w x d, `length` long), its two cut ends
    in end grain. `taper` narrows the far (+z) end (root toes)."""
    hw, hd, hl, k = w / 2, d / 2, length / 2, 1.0 - taper
    verts = [(-hw, -hd, -hl), (hw, -hd, -hl), (hw, hd, -hl), (-hw, hd, -hl),
             (-hw * k, -hd * k, hl), (hw * k, -hd * k, hl), (hw * k, hd * k, hl), (-hw * k, hd * k, hl)]
    ob = kit.mesh_obj(name, verts, kit.BOX_FACES, M[side], parent, loc, rot)
    _set_mats(ob, [M[side], M[end]], lambda p: 1 if p.index < 2 else 0)
    if bevel > 0:
        md = ob.modifiers.new("bevel", "BEVEL")
        md.width = min(bevel, min(w, d) * k * 0.4)
        md.segments = 2
        md.limit_method = "NONE"
        for p in ob.data.polygons:
            p.use_smooth = True
        try:
            ob.modifiers.new("wn", "WEIGHTED_NORMAL").keep_sharp = True
        except Exception:
            pass
    return ob


def _icosphere(sub=1):
    t = (1 + 5 ** 0.5) / 2
    vs = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
          (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    vs = [V(v).normalized() for v in vs]
    fs = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6),
          (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10),
          (8, 6, 7), (9, 8, 1)]
    for _ in range(sub):
        cache, nf = {}, []

        def mid(i, j):
            key = (min(i, j), max(i, j))
            if key not in cache:
                vs.append((vs[i] + vs[j]).normalized())
                cache[key] = len(vs) - 1
            return cache[key]
        for a, b, c in fs:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            nf += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        fs = nf
    return vs, fs


def block_boulder(kit, name, r, M, parent, loc, seed, squash=0.82):
    """A faceted block boulder (pass 2, note 21): an icosphere subdivided once (80 flat facets), each corner pushed
    in or out a little and the bottom cut flat, flat-shaded so every facet reads as a plane, moss on the facets
    that face up."""
    rng = np.random.default_rng(seed)
    vs, fs = _icosphere(1)
    verts = []
    for v in vs:
        k = rng.uniform(0.86, 1.1)
        p = v * r * k
        verts.append((p.x * 1.05, p.y * 0.95, max(p.z * squash, -r * 0.5)))
    ob = kit.mesh_obj(name, verts, fs, M["bstone"], parent, loc)
    for p in ob.data.polygons:
        p.use_smooth = False
    return ob


def stump_mesh(kit, name, M, parent, seed=5, n=112, rows=18, facets=14):
    """The head: a thick-walled hollow stump (an outer shell with a broken, mossy rim and a sunken top, and a cavity
    inside it), opened at the front by `hollow_cutter`. Local z = 0 is its base, its front is -y."""
    rng = np.random.default_rng(seed)
    ph = float(rng.uniform(0, 50))
    Ri, Hcap = 1.95, HEAD_H - 0.5
    Rc, Zf, Zc = 1.92, 0.45, Hcap - 0.45

    def g(d, w):
        return math.exp(-(d / w) ** 2)

    def ang(a, b):
        return math.atan2(math.sin(a - b), math.cos(a - b))

    def rim(th):
        """A broken top (theta 0 is local +x, its left; the front, -y, is 3 pi / 2): it slopes from high on its
        right-back to low on its left-front, ragged all round, two broad splinters at the back, a deep notch where
        the split from the hollow reaches the rim, and a smaller one on its left."""
        h = 0.5 * math.cos(ang(th, 2.36))
        h += 0.16 * mnoise.noise(V((math.cos(th) * 3.0 + ph, math.sin(th) * 3.0, 0.0)))
        h += 0.1 * max(0.0, mnoise.noise(V((math.cos(th) * 7.0, math.sin(th) * 7.0, ph))) - 0.05)
        for c, w, d in ((2.0, 0.16, 0.32), (2.7, 0.1, 0.18), (4.28, 0.09, -0.8), (0.6, 0.1, -0.3)):
            h += d * g(ang(th, c), w)
        return HEAD_H + h

    def r_out(th, z):
        base = HEAD_R + 0.22 * math.exp(-z / 0.55) + 0.06 - 0.025 * z      # a stump's flare at the base, a taper
        lump = 0.055 * mnoise.noise(V((math.cos(th) * 2.2 + ph, math.sin(th) * 2.2, z * 0.35)))
        lump += 0.03 * mnoise.noise(V((math.cos(th) * 5.0, math.sin(th) * 5.0, z * 0.9 + ph)))
        for c, zc, d in ((1.2, 3.4, 0.16), (3.9, 1.6, 0.14), (5.9, 3.9, 0.12), (0.2, 1.0, 0.1), (2.6, 2.4, 0.12)):
            lump += d * g(ang(th, c), 0.3) * g(z - zc, 0.6)
        if facets:
            # pass 2 (note 21): a faceted stump, flat facets like a game part; every column sits on its facet's
            # straight edge, so the sides are planes and only the rim stays broken
            fa = 2 * math.pi / facets
            fc = (math.floor(th / fa) + 0.5) * fa
            return max(base * math.cos(fa / 2) / math.cos(th - fc), Ri + 0.5)
        return max(base * (1 + lump), Ri + 0.5)        # never inside the rim's inner wall (a fold breaks the cut)

    cols = []
    for j in range(n):
        th = 2 * math.pi * j / n
        H = rim(th)
        prof = []
        for k in range(rows + 1):
            z = (H - 0.12) * k / rows
            prof.append((r_out(th, z), z))
        ro = prof[-1][0]
        prof += [(ro - 0.1, H - 0.02), (ro - 0.25, H + 0.03), ((ro + Ri) / 2, H + 0.02), (Ri + 0.12, H - 0.04),
                 (Ri, H - 0.22), (Ri - 0.02, Hcap + 0.15), (Ri - 0.2, Hcap + 0.02),
                 (Ri * 0.6, Hcap + 0.05 + 0.04 * math.sin(th * 3)), (Ri * 0.25, Hcap + 0.02)]
        cols.append([(r * math.cos(th), r * math.sin(th), z) for r, z in prof])
    m = len(cols[0])
    verts = [v for c in cols for v in c]
    bot, top = len(verts), len(verts) + 1
    verts += [(0, 0, 0), (0, 0, Hcap)]
    faces = []
    for j in range(n):
        j2 = (j + 1) % n
        for i in range(m - 1):
            faces.append((j * m + i, j2 * m + i, j2 * m + i + 1, j * m + i + 1))
        faces.append((bot, j2 * m, j * m))
        faces.append((j * m + m - 1, j2 * m + m - 1, top))
    nshell = len(faces)
    # the cavity, its faces turned inward
    off = len(verts)
    cz = [Zf, Zf + 0.12] + [Zf + 0.12 + (Zc - Zf - 0.24) * k / 8 for k in range(1, 8)] + [Zc - 0.12, Zc]
    cr = []
    for j in range(n):
        th = 2 * math.pi * j / n
        for k, z in enumerate(cz):
            edge = 0.92 if k in (0, len(cz) - 1) else 1.0
            r = Rc * edge * (1 + 0.04 * mnoise.noise(V((math.cos(th) * 2.5, math.sin(th) * 2.5, z * 0.8 + ph))))
            cr.append((r * math.cos(th), r * math.sin(th), z))
    mc = len(cz)
    verts += cr
    cb, ct = len(verts), len(verts) + 1
    verts += [(0, 0, Zf), (0, 0, Zc)]
    for j in range(n):
        j2 = (j + 1) % n
        for i in range(mc - 1):
            faces.append((off + j * mc + i, off + j * mc + i + 1, off + j2 * mc + i + 1, off + j2 * mc + i))
        faces.append((cb, off + j * mc, off + j2 * mc))
        faces.append((off + j2 * mc + mc - 1, off + j * mc + mc - 1, ct))
    ob = kit.mesh_obj(name, verts, faces, M["sbark"], parent)
    _set_mats(ob, [M["sbark"], M["hollow"]], lambda p: 0 if p.index < nshell else 1)
    for p in ob.data.polygons:
        p.use_smooth = p.index >= nshell or not facets
    return ob


def hollow_cutter(kit, name, M, parent, seed=8, n=240):
    """The hollow's mouth, pushed through the stump's front wall: a lopsided, ragged opening about 2.8 x 3 m,
    fuller low on its right (my left as I face it), and a narrow split running up from its top-right to the rim."""
    ph = float(np.random.default_rng(seed).uniform(0, 50))
    a, b = HOLLOW_W / 2, HOLLOW_H / 2

    def g(d, w):
        return math.exp(-(d / w) ** 2)

    def ang(x, y):
        return math.atan2(math.sin(x - y), math.cos(x - y))

    ring = []
    for i in range(n):
        t = 2 * math.pi * i / n
        # an almond, pointed at the top and the bottom (x ~ cos t |cos t|): a split in the wood, not a doorway
        x, z = a * math.cos(t) * abs(math.cos(t)) ** 0.55, b * math.sin(t)
        f = math.atan2(z, x)
        up = max(0.0, math.sin(t))
        k = 1 + 0.08 * mnoise.noise(V((math.cos(t) * 1.6 + ph, math.sin(t) * 1.6, 0.0)))
        k *= 1 + 0.07 * mnoise.noise(V((math.cos(t) * 6.0, math.sin(t) * 6.0, ph))) * (0.4 + 0.6 * up)
        k *= 1 + 0.04 * mnoise.noise(V((math.cos(t) * 13.0, math.sin(t) * 13.0, ph + 3.0)))
        k *= 1 + 0.12 * g(ang(f, math.pi + 0.55), 0.5) - 0.08 * g(ang(f, 0.6), 0.5)   # lopsided
        r = math.hypot(x, z) * k
        # the split runs on up from its top point to the rim: a radial spike, so the outline stays star-shaped round
        # its middle (the fan caps and the exact boolean need that)
        r += 1.6 * g(ang(f, math.pi / 2 + 0.1), 0.045)
        ring.append((r * math.cos(f), r * math.sin(f)))
    y0, y1 = -HEAD_R - 1.0, -0.9
    verts = [(x, y0, HOLLOW_Z + z) for x, z in ring] + [(x, y1, HOLLOW_Z + z) for x, z in ring]
    verts += [(0.0, y0, HOLLOW_Z), (0.0, y1, HOLLOW_Z)]
    c0, c1 = 2 * n, 2 * n + 1
    # every face points out of the prism (the exact boolean needs it closed and consistent); the outline is star-
    # shaped round its middle, so each cap is a fan from the middle
    faces = [(i, n + i, n + (i + 1) % n, (i + 1) % n) for i in range(n)]
    faces += [(c0, i, (i + 1) % n) for i in range(n)]
    faces += [(c1, n + (i + 1) % n, n + i) for i in range(n)]
    ob = kit.mesh_obj(name, verts, faces, M["lip"], parent)
    ob.hide_render = True
    ob.hide_viewport = True
    return ob


def boulder_mesh(kit, name, r, M, parent, loc, seed, squash=0.86):
    rng = np.random.default_rng(seed)
    ph = V(tuple(rng.uniform(0, 50, 3)))
    seg, rings = 36, 20
    verts, faces = [], []
    for i in range(rings + 1):
        th = math.pi * i / rings
        for j in range(seg):
            f = 2 * math.pi * j / seg
            d = V((math.sin(th) * math.cos(f), math.sin(th) * math.sin(f), math.cos(th)))
            k = 1 + 0.13 * mnoise.noise(d * 1.1 + ph) + 0.05 * mnoise.noise(d * 3.2 + ph) + 0.08 * max(0.0, d.z) ** 3
            p = d * r * k
            verts.append((p.x * 1.04, p.y * 0.96, max(p.z * squash, -r * 0.55)))
    for i in range(rings):
        for j in range(seg):
            a, b2 = i * seg + j, i * seg + (j + 1) % seg
            faces.append((a, a + seg, b2 + seg, b2))
    ob = kit.mesh_obj(name, verts, faces, M["stone"], parent, loc, smooth=True)
    return ob


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


# ------------------------------------------------------------------------------------------------ the giant


def build_giant(kit, ctx, M):
    """Built once. pose_giant() only moves these same parts."""
    rng = np.random.default_rng(14)
    root = kit.empty("giant", (0, 0, 0))
    g = {"root": root}
    seed = [100]

    def nxt():
        seed[0] += 1
        return seed[0]

    def limb(parent, name, top, length, flip=1.0):
        """Four upright square timbers, 4.6 x 4.6 m together, hanging from `top` (local z) for `length` metres."""
        for k, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
            w = 2.18 + rng.uniform(-0.1, 0.04)
            dl = rng.uniform(-0.25, 0.25)
            L = length + dl
            timber(kit, f"{name}.log{k}", w, w * rng.uniform(0.96, 1.02), L, M, parent,
                   (sx * 1.16 + rng.uniform(-0.03, 0.03), sy * 1.16 + rng.uniform(-0.03, 0.03), top - L / 2 + dl / 2),
                   (rng.uniform(-0.012, 0.012), rng.uniform(-0.012, 0.012), rng.uniform(-0.03, 0.03)),
                   side="tbark_limb", bevel=0.22)

    # the legs: from the hips (z = HIP_Z) down to the ground, with four root toes at the front of each foot
    g["hips"] = kit.empty("giant.hips", (0, 0, HIP_Z), root)
    for side, sx in (("l", 1), ("r", -1)):
        leg = kit.empty(f"giant.leg_{side}", (sx * LEG[0] / 2, 0, 0), g["hips"])
        limb(leg, f"giant.leg_{side}", 0.0, HIP_Z - 0.05)
        for k, tx in enumerate((-1.7, -0.57, 0.57, 1.7)):
            ln = 1.5 + rng.uniform(-0.15, 0.2)
            timber(kit, f"giant.toe_{side}{k}", 1.0, 1.0, ln + 1.0, M, leg,
                   (tx, -LEG[1] / 2 - ln / 2 + 0.45, -HIP_Z + 0.48),
                   (math.radians(90 - 8 + rng.uniform(-3, 3)), 0, math.radians(rng.uniform(-6, 6))),
                   bevel=0.12, taper=0.38)
        g[f"leg_{side}"] = leg

    # the torso: a log-cabin wall of square timbers, crossed ends at its corners, closed on top by two timbers
    torso = kit.empty("giant.torso", (0, 0, HIP_Z), root)
    g["torso"] = torso
    W, D, H = TORSO
    r = LOG_D / 2
    fy = D / 2 - r - 0.5                     # the front and back walls' timber centres
    sx_ = W / 2 - r - 0.5                    # the side walls' timber centres
    courses = int(round(H / LOG_D))
    for k in range(courses):
        z = r + k * LOG_D
        for side, y in (("f", -fy), ("b", fy)):
            ln = W + rng.uniform(-0.12, 0.05)
            dd = LOG_D * rng.uniform(0.93, 1.0)
            timber(kit, f"giant.t{side}{k}", dd, dd, ln, M, torso,
                   (rng.uniform(-0.08, 0.08), y + rng.uniform(-0.03, 0.03), z), (0, math.pi / 2, rng.uniform(-0.01, 0.01)))
        if k < courses - 1:
            for side, x in (("l", -sx_), ("r", sx_)):
                ln = D + rng.uniform(-0.1, 0.05)
                dd = LOG_D * rng.uniform(0.93, 1.0)
                timber(kit, f"giant.t{side}{k}", dd, dd, ln, M, torso,
                       (x + rng.uniform(-0.03, 0.03), rng.uniform(-0.05, 0.05), z + r), (-math.pi / 2, 0, 0))
    for k, y in enumerate((-0.46, 0.46)):
        timber(kit, f"giant.ttop{k}", LOG_D, LOG_D, W - 1.4, M, torso, (0, y, H - r), (0, math.pi / 2, 0))
    kit.box("giant.core", (2 * sx_, 2 * fy, H - 0.4), (0, 0, H / 2), M["core"], torso)

    # the shoulders: two faceted block boulders on the torso's top corners, up to the middle of the head,
    # saplings on them
    stones = {"l": (3.9, 4.15, 0.25, 1.05), "r": (3.6, -4.2, 0.2, 0.95)}
    pine = ctx["pine"]
    for side, (dia, x, y, dz) in stones.items():
        b = block_boulder(kit, f"giant.stone_{side}", dia / 2, M, torso, (x, y, H + dz), 31 if side == "l" else 47)
        b.data.materials[0] = M["gstone"]
        g[f"stone_{side}"] = b
    # the giant's own left is +x in its local frame (it faces -y, so +x is on its left hand)
    for k, (dx, dy, s, yaw) in enumerate(((-0.3, -0.4, 1.45, 0.3), (0.55, 0.3, 1.1, 1.4), (-0.05, 0.75, 1.25, 2.2))):
        place_pine(kit, pine, f"giant.sapling_l{k}", (4.15 + dx, 0.25 + dy, H + 1.05 + 1.5), s, yaw, torso,
                   (math.radians(dx * 12), math.radians(-dy * 10)))
    place_pine(kit, pine, "giant.sapling_r0", (-4.0, 0.45, H + 0.95 + 1.4), 1.2, 0.8, torso)

    # the arms: hanging at its sides to the hip, never longer
    for side, sx in (("l", 1), ("r", -1)):
        arm = kit.empty(f"giant.arm_{side}", (sx * ARM_X, 0, ARM_PIVOT), torso)
        limb(arm, f"giant.arm_{side}", H - ARM_PIVOT, H - 0.1, flip=-1.0)
        g[f"arm_{side}"] = arm

    # the head: a hollow stump with two warm lights deep in its hollow
    neck = kit.empty("giant.neck", (0, 0, H), torso)
    head = kit.empty("giant.head", (0, 0, 0), neck)
    g["neck"], g["head"] = neck, head
    shell = stump_mesh(kit, "giant.stump", M, head, n=STUMP_FACETS * 6, facets=STUMP_FACETS)
    cut = hollow_cutter(kit, "giant.hollow_cut", M, head)
    mod = shell.modifiers.new("hollow", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cut
    mod.solver = "EXACT"
    try:
        mod.material_mode = "TRANSFER"
    except Exception:
        pass
    g["stump"] = shell
    _check_cut(shell)
    g["lights"] = []
    for k, sx in enumerate((-1, 1)):
        p = (sx * LIGHT_SEP / 2, -HEAD_R + LIGHT_IN, LIGHT_Z)
        e = kit.sphere(f"giant.light{k}", LIGHT_R, p, M["eyes"], head, seg=16)
        e.visible_shadow = False
        g["lights"].append(e)
        kit.light(f"giantglow{k}", "POINT", p, 14.0, "#ffb860", size=0.17, parent=head)
    # a shadow-only curtain just inside the mouth: no light from outside (my lamp) reaches into the hollow, so it
    # stays dark round its own two lights. Nothing sees it but shadow rays.
    cur = kit.plane("giant.curtain", (HOLLOW_W + 0.8, HOLLOW_H + 3.2), (0, -HEAD_R + 0.4, HOLLOW_Z + 1.0), M["hollow"],
                    head, rot=(math.pi / 2, 0, 0))
    for k in ("visible_camera", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
        setattr(cur, k, False)
    g["curtain"] = cur
    ctx["giant"] = g
    return g


def _check_cut(shell):
    """The hollow must open the front wall and leave the rest: warn loudly if the boolean ate the shell."""
    try:
        dg = bpy.context.evaluated_depsgraph_get()
        me = shell.evaluated_get(dg).to_mesh()
        bark = sum(p.area for p in me.polygons if p.material_index == 0)
        lip = sum(p.area for p in me.polygons if p.material_index == 2)
        shell.evaluated_get(dg).to_mesh_clear()
        if bark < 60.0 or lip < 2.0:
            print(f"WARNING lookout set: the hollow's cut looks wrong (bark {bark:.0f} m2, lip {lip:.1f} m2)", flush=True)
    except Exception as e:  # never stop a render over the check
        print("WARNING lookout set: cut check failed:", e, flush=True)


def pose_giant(g, pos, yaw=180.0, head=0.0, pitch=0.0, hidden=False, stride=0.0):
    """stride: degrees each leg swings from the hip (R6-stiff, the arms swing the other way)."""
    st = math.radians(stride)
    g["leg_l"].rotation_euler = (st, 0, 0)
    g["leg_r"].rotation_euler = (-st, 0, 0)
    g["arm_l"].rotation_euler = (-st, 0, 0)        # the arms swing as far as the legs, the other way (R6)
    g["arm_r"].rotation_euler = (st, 0, 0)
    g["root"].location = pos
    g["root"].rotation_euler = (0, 0, math.radians(yaw))
    g["torso"].rotation_euler = (math.radians(pitch), 0, 0)     # + leans it forward (its front is local -y)
    g["head"].rotation_euler = (0, 0, math.radians(max(-60.0, min(60.0, head))))
    for ob in [g["root"]] + list(g["root"].children_recursive):
        if ob.type != "EMPTY" and not ob.name.endswith("hollow_cut"):
            ob.hide_render = hidden


def giant_objects(g):
    return [o for o in [g["root"]] + list(g["root"].children_recursive) if o.type == "MESH"]


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


def build_forest(kit, ctx, M, rng, n=420, r0=10.0, r1=260.0):
    """Pines on the ground, 14 to 17 m, with gold larch in patches: clear of the giant's spots (CLEAR), the road
    (5 m either side), the fence, the shelf and the open fog down the ridge in front of the scale wide's camera. The
    far ones sink in fog."""
    pine, larch = ctx["pine"], ctx["larch"]
    trees = []
    k = 0
    while len(trees) < n and k < n * 40:
        k += 1
        a = rng.uniform(0, 2 * math.pi)
        d = math.sqrt(rng.uniform(r0 ** 2, r1 ** 2))
        x, y = d * math.cos(a), d * math.sin(a)
        if any(math.hypot(x - cx, y - cy) < cr for cx, cy, cr in CLEAR):
            continue
        below_shelf = 25.0 < x < 130.0 and -390.0 < y < -282.0
        if road_dist(x, y) < 7.5 or (abs(x) < FENCE + 3 and abs(y) < FENCE + 3) or (y < -268 and not below_shelf):
            continue
        if math.hypot(x - SHELF[0], y - SHELF[1]) < 16:
            continue
        if any(math.hypot(x - tx, y - ty) < 4.6 for tx, ty in trees):
            continue
        trees.append((x, y))
        gold = mnoise.noise(V((x * 0.03, y * 0.03, 7.0))) > 0.32
        ob = place_pine(kit, larch if gold else pine, f"pine{len(trees)}", (x, y, terrain_z(x, y) - 0.2),
                        rng.uniform(14, 17), rng.uniform(0, 6.3))
        ctx.setdefault("tree_objs", []).append(ob)
    # pines round the giant's spots whose tops reach only its chest (the scale read in the wides); none closer
    # than 4 m to it, so it's never seen between trees at arm's length
    for k, (x, y, h) in enumerate(HERO_PINES):
        ob = place_pine(kit, pine, f"pine.hero{k}", (x, y, terrain_z(x, y) - 0.2), h, 0.7 * k)
        ctx.setdefault("tree_objs", []).append(ob)
        trees.append((x, y))
    # a stand east of the shelf and down the slope below it, so the giant walking off along it is lost among trees (L72)
    walk_to = ((82.0, -258.0), (108.0, -250.0), (134.0, -244.0))
    for k in range(260):
        x, y = rng.uniform(62.0, 210.0), rng.uniform(-300.0, -214.0)
        if (y < -266.0 and x > 150.0) or any(math.hypot(x - tx, y - ty) < 4.8 for tx, ty in trees) \
                or any(math.hypot(x - wx, y - wy) < 8.0 for wx, wy in walk_to):
            continue
        trees.append((x, y))
        ob = place_pine(kit, pine, f"grove{k}", (x, y, terrain_z(x, y) - 0.2), rng.uniform(15, 19), rng.uniform(0, 6.3))
        ctx.setdefault("tree_objs", []).append(ob)
    ctx["trees"] = trees
    return trees


FOG_CARDS = {
    # name: (material, (x, y, top, width, height, yaw degrees)). Night: round the tower and behind the giant's scare
    # spot. Day: banks across the view up the ridge from the south, their tops at 9 to 12 m so the pine tops and the
    # giant's chest stand out of them, and a pale backdrop far behind the tower.
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
    """The fog banks: vertical noise cards with a soft visible top. A look shows six at most (brief)."""
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


def build_lights(kit, ctx):
    """Night: the giant is a silhouette, not a lit object (critic, pass 2). My lamp's throw touches only its stump
    (never its stones), the night fill never reaches it, and a thin cold rim from behind traces its stump and stones
    against the lifted fog. Day: a soft sun from behind it (the side the wide never sees), so it reads dark against
    pearl fog."""
    lp = ctx["lamp"].location
    key = kit.light("lampkey", "POINT", (lp.x, lp.y, lp.z + 0.2), 60.0, "#ffd9a0", size=0.12)
    # my lamp's light on my own face from below and in front (placed from my head each frame): my raised arm sits
    # between the hanging lantern and my face, so this does the lantern's work on me only
    face = kit.light("facekey", "POINT", (0, 0, 0), 12.0, "#ffd9a0", size=0.15, shadow=False)
    face.visible_glossy = False
    ctx["key_obj"] = key
    fill = kit.light("fill", "SUN", (0, 0, 60), 1.5, "#8ea6c4", rot=(math.radians(66), 0, math.radians(70)))
    fill.data.angle = math.radians(25)
    sun = kit.light("sun", "SUN", (0, 0, 60), 0.0, "#efeadc", rot=(math.radians(66), 0, math.radians(195)))
    sun.data.angle = math.radians(30)
    rim = kit.light("rim", "SPOT", RIM_AT, 60000.0, "#9fb4cc", size=1.0, spot=26, blend=0.35)
    ctx["rim_obj"] = rim
    for nm in ("lampkey", "fill", "rim", "lamp", "sun"):
        kit.LIGHTS[nm]["obj"].visible_glossy = nm not in ("lamp", "lampkey")
    g = ctx["giant"]
    gi = giant_objects(g)
    stones = [o for o in gi if ".stone_" in o.name or ".sapling_" in o.name]
    moss = kit.light("moss", "POINT", (0, 0, 30), 1800.0, "#c9cfa4", size=2.5)
    moss.visible_glossy = False
    link_lights(kit, "stones only", ["moss"], stones, "INCLUDE")
    link_lights(kit, "giant only", ["rim"], gi, "INCLUDE")
    link_lights(kit, "stump and limbs only", ["lampkey"], [o for o in gi if o not in stones], "INCLUDE")
    me = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("me.")]
    link_lights(kit, "not the giant", ["fill"], gi, "EXCLUDE")
    # a warm light for the giant's foot only: it lights the toes in my pool and nothing of mine (L65)
    toe = kit.light("toelight", "POINT", (0, 0, 3), 2500.0, "#ffd9a0", size=0.6)
    toe.visible_glossy = False
    link_lights(kit, "toes only", ["toelight"], [o for o in gi if ".toe_" in o.name or ".leg_" in o.name], "INCLUDE")
    ctx["need_me_links"] = True
    # the lantern's own frame isn't lit by the flame inside it (it would blow out at 10 cm), and the lamp never
    # lights the stones (they stay part of the dark mass)
    lamp_parts = [o for o in ctx["lamp"].children if o.type == "MESH"]
    link_lights(kit, "not the lantern or stones", ["lamp"], lamp_parts + stones, "EXCLUDE")


def aim_at(ob, target):
    ob.rotation_euler = (V(target) - ob.location).to_track_quat("-Z", "Y").to_euler()


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


def road_mat(kit, name="fire road"):
    """The rutted track: dry packed dirt, two darker wheel ruts along it (its UV u runs across the road)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    uv = N.new("ShaderNodeUVMap")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(uv.outputs["UV"], sep.inputs[0])
    rut = _math(N, L, "MINIMUM", _math(N, L, "ABSOLUTE", _math(N, L, "SUBTRACT", sep.outputs["X"], 0.3)),
                _math(N, L, "ABSOLUTE", _math(N, L, "SUBTRACT", sep.outputs["X"], 0.7)))
    nz = _noise(N, L, _scaled(N, L, "Object", (1, 1, 1)), 0.6, 4.0)
    dirt = _mix(N, L, kit.col("#3a3026"), kit.col("#55473a"), _range(N, L, nz, 0.3, 0.7))
    L.new(_mix(N, L, kit.col("#211b15"), dirt, _range(N, L, rut, 0.03, 0.09)), b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.95
    kit._fogged(m, b.outputs[0])
    return m


def river_mat(kit, name="river"):
    """The river from far up: a thin silver line (emissive), as bright as each look says (0 under the smoke)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col("#dbe6ee")
    L.new(_math(N, L, "MULTIPLY", _value(N, 0.0, "river"), 2.4), em.inputs["Strength"])
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    L.new(em.outputs[0], out.inputs["Surface"])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
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


def build_land(kit, ctx, M):
    """The terrain (10 m grid), the fire road (a ribbon on it with ruts), the valley's river and smoke, the burn's
    grey smudge far off east, and the rocky shelf at the road's end."""
    # 10 m near the tower and the road, 20 m out over the far valley and its far hills
    xs = np.concatenate([np.arange(-760.0, -320.0, 20.0), np.arange(-320.0, 321.0, 10.0), np.arange(340.0, 761.0, 20.0)])
    ys = np.concatenate([np.arange(-1400.0, -720.0, 20.0), np.arange(-720.0, 441.0, 10.0)])
    verts, faces = [], []
    for y in ys:
        for x in xs:
            # flatten the plateau under the tower and the road a little, so nothing floats or sinks
            verts.append((float(x), float(y), terrain_z(x, y) - 0.05))
    nx = len(xs)
    for j in range(len(ys) - 1):
        for i in range(nx - 1):
            faces.append((j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i))
    ground = kit.mesh_obj("ground", verts, faces, M["ground"])
    for p in ground.data.polygons:
        p.use_smooth = True
    # the plateau under the tower: an exact flat pad, so the legs and the fence stand on z = 0
    _wbox(kit, "plateau", (-24, -24, -0.6), (24, 24, 0.0), M["ground"])
    # the road: a ribbon 3.6 m wide just above the ground
    n = 260
    rv, rf, ruv = [], [], []
    for k in range(n + 1):
        (x, y, zz), (dx, dy) = road_pos(k / n)
        nxp, nyp = -dy, dx
        for side in (-1, 1):
            px, py = x + side * nxp * ROAD_W / 2, y + side * nyp * ROAD_W / 2
            pz = (0.0 if math.hypot(px, py) < 22 else terrain_z(px, py)) + 0.06
            rv.append((px, py, max(pz, terrain_z(px, py) + 0.06)))
            ruv.append((0.0 if side < 0 else 1.0, k / n * 40))
    for k in range(n):
        rf.append((2 * k, 2 * k + 1, 2 * k + 3, 2 * k + 2))
    road = kit.mesh_obj("fire road", rv, rf, M["road"])
    uvl = road.data.uv_layers.new(name="UVMap")
    for poly in road.data.polygons:
        for li in poly.loop_indices:
            uvl.data[li].uv = ruv[road.data.loops[li].vertex_index]
    ctx["road"] = road
    # the shelf: flat rocks at the road's end, faceted like the giant's stones
    sx, sy = SHELF
    sz = terrain_z(sx, sy)
    rng = np.random.default_rng(5)
    # rocks round the shelf's back and sides (none on its open front edge over the valley, none where I stand)
    for k in range(7):
        a = math.radians(-10 + 200 * k / 6)          # from east round the back (north) to west
        r = rng.uniform(6.5, 8.0)
        block_boulder(kit, f"shelf.rock{k}", rng.uniform(0.9, 1.7), M, None,
                      (sx + r * math.cos(a), sy - 2.0 + r * math.sin(a), sz - 0.3), 200 + k, squash=0.5)
    _wbox(kit, "shelf.slab", (sx - 6, sy - 8, sz - 3.0), (sx + 6, sy + 3, sz + 0.05), M["bstone"])
    # the valley: the river winding through it, the smoke sheet over it
    rv, rf = [], []
    pts = [(-740 + 10 * k, RIVER_Y + 70 * math.sin(k * 0.045) + 30 * math.sin(k * 0.13)) for k in range(149)]
    for k, (x, y) in enumerate(pts):
        for side in (-1, 1):
            rv.append((x, y + side * 7.0, VALLEY_Z + 2.2))
    for k in range(len(pts) - 1):
        rf.append((2 * k, 2 * k + 1, 2 * k + 3, 2 * k + 2))
    river = kit.mesh_obj("river", rv, rf, M["river"])
    for k in ("visible_shadow", "visible_diffuse", "visible_glossy"):
        setattr(river, k, False)
    smoke = kit.plane("valley smoke", (1500, 820), (0, RIVER_Y, VALLEY_Z + 30), M["smoke"])
    for k in ("visible_shadow", "visible_diffuse", "visible_glossy"):
        setattr(smoke, k, False)
    smudge = kit.mesh_obj("burn smudge", [(-90, 0, 0), (90, 0, 0), (90, 0, 55), (-90, 0, 55)], [(0, 1, 2, 3)],
                          M["smudge"], loc=(520.0, -60.0, -20.0), rot=(0, 0, math.radians(90)))
    smudge.visible_shadow = False
    ctx["smudge"] = smudge


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


def print_parts(kit, name, M, x, y, heading):
    """One footprint: a 4.6 m square heel and four toe grooves ahead of it, pointing `heading` (radians, 0 = -y,
    downhill), each a mud rim round dark, rough rainwater (it reflects nobody) with moss in the toes. Returns an
    empty with a sapling place in it for spring."""
    # lying on the ground's slope (the road falls about 1 in 5) and a little above the road's ribbon, so its water
    # shows and no edge floats or sinks
    on_top = math.hypot(x, y) <= 22
    root = kit.empty(name, (x, y, (0.0 if on_top else terrain_z(x, y)) + 0.05))
    if on_top:
        root.rotation_euler = (0, 0, heading)
    else:
        gx = (terrain_z(x + 1.0, y) - terrain_z(x - 1.0, y)) / 2.0
        gy = (terrain_z(x, y + 1.0) - terrain_z(x, y - 1.0)) / 2.0
        tilt = V((0.0, 0.0, 1.0)).rotation_difference(V((-gx, -gy, 1.0)).normalized())
        root.rotation_euler = (tilt.to_matrix() @ Matrix.Rotation(heading, 3, "Z")).to_euler()
    kit.box(f"{name}.water", (4.2, 4.2, 0.04), (0, 0, 0.02), M["water"], root)
    for k, (w, d, px, py) in enumerate(((4.6, 0.3, 0, 2.2), (4.6, 0.3, 0, -2.2), (0.3, 4.6, 2.2, 0), (0.3, 4.6, -2.2, 0))):
        kit.box(f"{name}.rim{k}", (w, d, 0.16), (px, py, 0.08), M["mud"], root, bevel=0.06)
    for k, tx in enumerate((-1.7, -0.57, 0.57, 1.7)):
        kit.box(f"{name}.toe{k}", (0.9, 1.4, 0.04), (tx, -2.2 - 0.85, 0.02), M["water"], root)
        kit.box(f"{name}.toemoss{k}", (0.7, 0.5, 0.05), (tx, -3.3, 0.03), M["moss"], root)
    return root


def build_prints(kit, ctx, M):
    """The prints: at the tower's foot heading off downhill (L22 to L26), and on down the fire road (its walk with
    my lamp). Each gets a small pine in spring (L73)."""
    prints = []
    pts = [(2.5, -13.0), (-1.5, -19.5), (3.0, -27.0), (-0.5, -34.0), (4.5, -41.0)]
    for k in range(10, 60):
        (x, y, _z), (dx, dy) = road_pos(k / 60.0)
        side = 0.9 if k % 2 else -0.9
        pts.append((x - dy * side, y + dx * side))
    for k, (x, y) in enumerate(pts):
        # heading downhill along the road
        (rx, ry, _z), (dx, dy) = road_pos(min(1.0, max(0.0, (-y - 6) / 270.0)))
        h = math.atan2(-dx, dy) + math.pi
        root = print_parts(kit, f"print{k}", M, x, y, h)
        tree = place_pine(kit, ctx["sapling"], f"print{k}.sapling", (0.0, 0.0, 0.04), 3.6, 0.7 * k, root)
        prints.append((root, tree))
    ctx["prints"] = prints


def build_snapped(kit, ctx, M):
    """The snapped treetops on the far ridge, all broken at one height: a line that runs straight for the valley,
    then bends toward my tower (L08 to L11)."""
    pts = []
    for a, b in zip(SNAPPED, SNAPPED[1:]):
        for k in range(6):
            u = k / 6
            pts.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
    rng = np.random.default_rng(23)
    for k, (x, y) in enumerate(pts):
        z = terrain_z(x, y)
        h = rng.uniform(14.5, 16.5)
        place_pine(kit, ctx["snapped_pine"], f"snapped{k}", (x + rng.uniform(-2, 2), y, z), h, rng.uniform(0, 6.3))


def snapped_pine_data(kit, M):
    """A pine broken off at two thirds of its height: the lower tiers and a jagged trunk end."""
    verts, faces = [], []
    me = pine_data(kit, "snapped pine", M, tiers=4)
    # cut the top: drop every vertex above 0.62 of the height to 0.62, so the upper tiers collapse into a stub
    for v in me.vertices:
        if v.co.z > 0.62:
            v.co.z = 0.62 + (v.co.z - 0.62) * 0.08
    me.update()
    return me


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


# ------------------------------------------------------------------------------------------------ looks
# A "look" cue switches the whole light: the distance fog's colour and density (every kit-fogged material), the sky,
# the exposure, which fog cards show, the suns and the other lights' gains. The story's own "look" in story.json
# is the night's; materials are built with it and a day look retints them.
# Looks (pass 3, the build). Every daylight look keeps the giant a dark mass against brighter fog (its ambient sky
# is low, the fog cards and distance fog bright), and every night look keeps the fill off it.
NIGHT_GAINS = {"sun": 0.0}
DAY_GAINS = {"fill": 0.0, "rim": 0.0, "lampkey": 0.0, "lamp": 0.35, "facekey": 0.0}
SCALE_VIEW = -40.0              # the scale wide's view bearing as a card yaw (cards face down its line)
LOOKS = {
    # pearl fog by day round the cab; the burn's smudge far off east
    "day": {"fog": "#b8bcb8", "density": 0.012, "start": 6.0, "sky": "#c3c7c3", "sky_strength": 0.5, "exposure": 0.15,
            "cards": {"fog.day3": (0.0, -30.0, 12.0, 0.0), "fog.day4": (0.0, 30.0, 12.0, 0.0),
                      "fog.dayback": (0.0, 190.0, 140.0, 0.0)},
            "gains": DAY_GAINS, "sun": 1.0, "smudge": True},
    # the same, for the first shot: a fog bank in front of the giant's head, so only a faint mass and two points show
    "dayfar": {"fog": "#b8bcb8", "density": 0.012, "start": 6.0, "sky": "#c3c7c3", "sky_strength": 0.5, "exposure": 0.5,
               "cards": {"fog.day3": (0.0, -30.0, 12.0, 0.0), "fog.day4": (0.0, 30.0, 12.0, 0.0),
                         "fog.day5": (0.0, 46.0, 26.5, 0.0), "fog.dayback": (0.0, 190.0, 140.0, 0.0)},
               "gains": {**DAY_GAINS, "lamp": 1.2}, "sun": 1.0, "smudge": True},
    # a clear morning before the smoke spreads: the valley far below, a silver line in it (L06, L07)
    "clear": {"fog": "#c4ccd2", "density": 0.0022, "start": 40.0, "sky": "#c9d3da", "sky_strength": 0.7,
              "exposure": 0.1, "cards": {}, "gains": DAY_GAINS, "sun": 1.6, "river": 2.5, "smudge": True},
    # the binoculars on the far ridge (thinner fog far out)
    "bino": {"fog": "#bcc0bc", "density": 0.0016, "start": 40.0, "sky": "#c3c7c3", "sky_strength": 0.6,
             "exposure": 0.1, "cards": {}, "gains": DAY_GAINS, "sun": 1.2, "bino": True},
    # dusk: the walk up the ridge over the fog top, the scale wide (L27 to L33)
    "dusk": {"fog": "#b3aea6", "density": 0.0045, "start": 20.0, "sky": "#bdb6ab", "sky_strength": 0.45,
             "exposure": 0.05, "gains": DAY_GAINS, "sun": 1.0,
             "cards": {"fog.day1": (-60.0, -72.0, 7.0, SCALE_VIEW), "fog.day2": (-46.0, -52.0, 8.5, SCALE_VIEW),
                       "fog.day3": (-30.0, -30.0, 10.0, SCALE_VIEW), "fog.day4": (-4.0, 6.0, 11.0, SCALE_VIEW),
                       "fog.day5": (20.0, 40.0, 12.0, SCALE_VIEW), "fog.dayback": (90.0, 150.0, 140.0, SCALE_VIEW)}},
    # night round the cab: blue-grey fog, one steady amber lamp
    "night": {"fog": "#2a3238", "density": 0.034, "start": 3.0, "sky": "#2c353c", "sky_strength": 1.0,
              "exposure": 1.6, "cards": ["fog.near", "fog.tower", "fog.neck", "fog.behind", "fog.far"],
              "gains": NIGHT_GAINS},
    # after dark, the fog top just under the catwalk, no trees showing (L34 to L41)
    "nighthigh": {"fog": "#2a3238", "density": 0.04, "start": 3.0, "sky": "#2c353c", "sky_strength": 1.0,
                  "exposure": 1.6, "gains": NIGHT_GAINS,
                  "cards": {"fog.tower": (0.0, -12.0, CAB_Z - 1.2, 0.0), "fog.behind": (0.0, 14.0, CAB_Z - 1.0, 0.0),
                            "fog.near": (16.0, 0.0, CAB_Z - 1.4, 90.0), "fog.far": (0.0, -45.0, 60.0, 20.0)}},
    # the lean, seen from outside (L40): lifted so the legs, the tilt and the cab read against a paler fog
    "nightlean": {"fog": "#33404a", "density": 0.02, "start": 6.0, "sky": "#3b4a55", "sky_strength": 1.6,
                  "exposure": 2.1, "gains": {**NIGHT_GAINS, "rim": 0.6},
                  "cards": {"fog.tower": (0.0, -12.0, CAB_Z - 6.0, 0.0), "fog.far": (0.0, 40.0, 60.0, 20.0)}},
    # the valley from the cab at night: smoke lying in it like milk, no river (L56, L57)
    "nightvalley": {"fog": "#2a3238", "density": 0.0035, "start": 20.0, "sky": "#2a3238", "sky_strength": 1.0,
                    "exposure": 1.6, "cards": {}, "gains": NIGHT_GAINS, "smoke": 0.95, "smoke_col": "#9a9a96"},
    # the fire road at night: fog to its waist (L63 to L67)
    # (the giant's cold rim is off: it made the stump pale; a dim olive light shows the moss on its stones instead)
    "nightroad": {"fog": "#2a3238", "density": 0.03, "start": 4.0, "sky": "#2c353c", "sky_strength": 1.0,
                  "exposure": 1.6, "gains": {**NIGHT_GAINS, "rim": 0.0, "lamp": 14.0, "lampkey": 25.0}, "moss": 1.0, "waist": True,
                  "cards": {"fog.tower": (0.0, -14.0, 9.5, 0.0), "fog.behind": (0.0, -70.0, 8.0, 0.0),
                            "fog.far": (0.0, -140.0, 60.0, 0.0)}},
    # the high wide down the road (L67): a pale bank behind the giant so it stands out, none over the lamp
    "nightroadhi": {"fog": "#2a3238", "density": 0.012, "start": 8.0, "sky": "#2c353c", "sky_strength": 1.0,
                    "exposure": 1.8, "gains": {**NIGHT_GAINS, "rim": 0.0, "lamp": 4.0}, "moss": 1.0, "waist": True,
                    "cards": {"fog.tower": (0.0, -14.0, 9.5, 0.0), "fog.far": (0.0, -40.0, 60.0, 0.0)}},
    # cold first light on the shelf: the smoke lifting, the river shining (L68 to L72)
    "dawn": {"fog": "#a7b4bf", "density": 0.0035, "start": 20.0, "sky": "#b3c0cb", "sky_strength": 0.55,
             "exposure": 0.2, "cards": {}, "gains": {**DAY_GAINS, "lamp": 0.6}, "sun": 1.4, "smoke": 0.5,
             "smoke_col": "#59616a", "river": 3.0},
    # spring: the same road, green and fogless, a small pine in every print (L73)
    "spring": {"fog": "#c8d6de", "density": 0.0012, "start": 30.0, "sky": "#b8cfdf", "sky_strength": 0.9,
               "exposure": 0.0, "cards": {}, "gains": DAY_GAINS, "sun": 2.6, "spring": 1.0, "river": 0.5},
}


def _kit_fog_nodes():
    """Every kit-fogged material's (start, density, fog emission) nodes (kit._fogged's own structure)."""
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
    for n in LOOK_NODES["spring"]:
        n.outputs[0].default_value = lk.get("spring", 0.0)
    for n in LOOK_NODES["river"]:
        n.outputs[0].default_value = lk.get("river", 0.0)
    for n in LOOK_NODES["smoke"]:
        n.outputs[0].default_value = lk.get("smoke", 0.0)
    sm = kit.MATS.get("smoke layer")
    if sm is not None:
        em = next(nd for nd in sm.node_tree.nodes if nd.type == "EMISSION")
        em.inputs["Color"].default_value = kit.col(lk.get("smoke_col", "#8a8178"))
    if ctx.get("smudge"):
        ctx["smudge"].hide_render = not lk.get("smudge", False)
    if ctx.get("bino"):
        ctx["bino"].hide_render = not lk.get("bino", False)
    for root, tree in ctx.get("prints", []):
        tree.hide_render = lk.get("spring", 0.0) < 0.5
    ctx["look"] = name


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    ctx = {"story": story}
    bpy.context.scene.cycles.transparent_max_bounces = 8
    M = materials(kit)
    ctx["M"] = M
    ctx["pine"] = pine_data(kit, "pine", M)
    sp = pine_data(kit, "sapling", M)
    sp.materials[0] = M["sprout"]
    ctx["sapling"] = sp
    lm = pine_data(kit, "larch", M)
    lm.materials[0] = M["larch"]
    ctx["larch"] = lm
    ctx["snapped_pine"] = snapped_pine_data(kit, M)
    rng = np.random.default_rng(14)
    build_giant(kit, ctx, M)
    before = set(bpy.data.objects)
    build_tower(kit, ctx, M)
    build_stairs(kit, ctx, M)
    build_cab_props(kit, ctx, M)
    # the tower is one group, pivoting at its foot, so it can lean a few degrees (L39)
    tower = kit.empty("tower", (0, 0, 0))
    for ob in set(bpy.data.objects) - before:
        if ob.parent is None and ob is not tower and ob.name != "lamp":
            ob.parent = tower
    ctx["tower"] = tower
    build_gate(kit, ctx, M)
    build_land(kit, ctx, M)
    build_forest(kit, ctx, M, rng)
    build_snapped(kit, ctx, M)
    build_prints(kit, ctx, M)
    build_fog(kit, ctx, M)
    build_binocular_mask(kit, ctx, M)
    ctx["lamp"].location = LAMP_DECK
    build_lights(kit, ctx)
    return ctx


# ------------------------------------------------------------------------------------------------ animate


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


def giant_state(tl, t):
    """Where the giant is at t: the latest `giant` cue, walked along its "walk" (from, to, until) with a stiff R6
    stride whose footfalls land on "beat0" + k * "beat" (the score's pulse), standing on the ground."""
    from blocky.timeline import resolver
    c = _last(_cues(tl, "giant"), t)
    if c is None:
        return None
    at = resolver(tl["lines"], tl["duration"])
    pos = list(c.get("pos", [0.0, -9.0, 0.0]))
    yaw = c.get("yaw", 180.0)
    stride = c.get("stride", 0.0)
    w = c.get("walk")
    if w:
        t1 = at(w["until"]) if isinstance(w["until"], str) else w["until"]
        u = min(1.0, max(0.0, (t - c["t"]) / max(1e-6, t1 - c["t"])))
        pos = [w["from"][0] + (w["to"][0] - w["from"][0]) * u, w["from"][1] + (w["to"][1] - w["from"][1]) * u, 0.0]
        dx, dy = w["to"][0] - w["from"][0], w["to"][1] - w["from"][1]
        yaw = math.degrees(math.atan2(dx, -dy)) if w.get("face", True) else yaw    # its front (local -y) leads
        b0 = at(w["beat0"]) if isinstance(w.get("beat0"), str) else w.get("beat0", c["t"])
        beat = w.get("beat", 1.5)
        stride = w.get("stride", 9.0) * math.cos(math.pi * (t - b0) / beat) if t < t1 else 0.0
    ground = terrain_z(pos[0], pos[1]) if math.hypot(pos[0], pos[1]) > 22 else 0.0
    z = ground + (pos[2] if len(pos) > 2 else 0.0)
    r = c.get("rise")
    if r:
        z += r["from"] * (1 - _ss((t - c["t"]) / r["dur"]))
    walking = (bool(w) and t < (at(w["until"]) if isinstance(w["until"], str) else w["until"]) if w else False) \
        or bool(c.get("pines"))
    return {"pos": (pos[0], pos[1], z), "yaw": yaw, "head": c.get("head", 0.0), "pitch": c.get("pitch", 0.0),
            "stride": stride, "walking": walking, "hidden": c.get("hidden", False), "look_lamp": c.get("look_lamp", False),
            "lights": c.get("lights", 1.0), "fade": c.get("fade"), "t0": c["t"]}


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


def part_pines(ctx, gs, t):
    """The pines it passes lean apart and spring back (L28, L67): every pine within 12 m of its middle leans away
    from it, more the closer it is."""
    walking = gs is not None and gs.get("walking")
    gx, gy = (gs["pos"][0], gs["pos"][1]) if gs else (0.0, 0.0)
    for ob in ctx.get("tree_objs", []):
        dx, dy = ob.location.x - gx, ob.location.y - gy
        d = math.hypot(dx, dy)
        if walking and d < 12.0:
            k = math.radians(14.0) * (1.0 - d / 12.0)
            ob.rotation_euler = (-dy / max(d, 1e-3) * k, dx / max(d, 1e-3) * k, ob.rotation_euler.z)
        elif ob.rotation_euler.x or ob.rotation_euler.y:
            ob.rotation_euler = (0.0, 0.0, ob.rotation_euler.z)


def animate(kit, story, tl, t, ctx):
    over = {}
    open_hood(kit)
    apply_look(kit, ctx, _switch(_cues(tl, "look"), "id", t, "night"))
    for k, v in LOOKS[ctx["look"]].get("gains", {}).items():
        over[k] = v
    over["moss"] = LOOKS[ctx["look"]].get("moss", 0.0)
    # the engine's camera stops at 500 m: the river, 600 m out, needs more (only in the two looks that show it)
    bpy.data.cameras["cam"].clip_end = 1500.0 if ctx["look"] in ("clear", "dawn") else 500.0
    g = ctx["giant"]
    gs = giant_state(tl, t)
    if gs is None:
        gs = {"pos": (0, -60, 0), "yaw": 180, "head": 0, "pitch": 0, "stride": 0, "hidden": True, "look_lamp": False,
              "lights": 1.0, "fade": None, "t0": 0}
    pose_giant(g, gs["pos"], gs["yaw"], gs["head"], gs["pitch"], gs["hidden"], gs["stride"])
    # its lights: they fade up (never pop on) when it rises, and swell about 15% on each breath
    lg = gs["lights"]
    if gs["fade"]:
        lg *= _ss((t - gs["t0"]) / gs["fade"])
    br = 1.0
    for c in _cues(tl, "breath"):
        x = t - c["t"]
        if 0 <= x < 5.0:
            br = max(br, 1.0 + 0.15 * math.sin(math.pi * x / 5.0))
    for k, e in enumerate(g["lights"]):
        e.scale = (br, br, br)
        e.hide_render = gs["hidden"] or lg <= 0.001
        over[f"giantglow{k}"] = br * lg * (0.0 if gs["hidden"] else 1.0)
    em = kit.MATS["giant lights"]
    for nd in em.node_tree.nodes:
        if nd.type == "MATH" and nd.operation == "MULTIPLY" and nd.inputs[1].default_value in (0.8, ctx.get("ember_s", -1)):
            ctx["ember_node"] = nd
    if ctx.get("ember_node") is not None:
        ctx["ember_node"].inputs[1].default_value = 0.8 * lg
        ctx["ember_s"] = 0.8 * lg
    # the tower leans a few degrees as it rests its weight on the frame (L39), and settles back
    lean = _ease_to(_cues(tl, "lean"), t, "deg", 0.0)
    ctx["tower"].rotation_euler = (-math.radians(lean), 0, 0)
    if abs(lean) > 1e-6:
        # I ride the lean: the cast is posed in the world, so anyone up on the tower is carried round its foot by
        # the tower's own rotation (the deck tilts under my boots, and the rail stays where my hands are)
        bpy.context.view_layer.update()
        tm = ctx["tower"].matrix_world.copy()
        for who in story.get("cast", {}):
            root = bpy.data.objects.get(who)
            if root is not None and root.matrix_world.translation.z > CAB_Z - 1.0:
                root.matrix_world = tm @ root.matrix_world
    ctx["door"].rotation_euler = (0, 0, -math.radians(100) * _ease_to(_cues(tl, "door"), t, "open", 0.0))
    ctx["gate"].rotation_euler = (0, 0, -math.radians(95) * _ease_to(_cues(tl, "gate"), t, "open", 0.0))
    radio = _switch(_cues(tl, "radio"), "on", t, False)
    over["radioglow"] = 1.0 if radio else 0.0
    ctx["led"].hide_render = not radio
    # sitting (an acting key "sit": true): both legs forward, the root lowered by a leg's length
    for who in story.get("cast", {}):
        sit = _switch(tl["acting"].get(who, []), "sit", t, False)
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg is not None and sit:
                leg.rotation_euler = (-math.pi / 2, 0, 0)
        # on the steep stairs (47 degrees) I take short, careful steps: a third of the walk's swing, so my boots
        # keep off the treads behind and ahead of me
        root = bpy.data.objects.get(who)
        if root is not None:
            p = root.location
            if max(abs(p.x), abs(p.y)) < STAIR_A + STAIR_W and 0.3 < p.z < CAB_Z - 0.3:
                for sx in (-1, 1):
                    leg = bpy.data.objects.get(f"{who}.leg{sx}")
                    if leg is not None:
                        r = leg.rotation_euler
                        leg.rotation_euler = (r.x / 3.0, r.y, r.z)
    # matrix_world is only current after an update (the cast, the giant and the lamp were just moved)
    bpy.context.view_layer.update()
    if gs["look_lamp"]:
        # its head turns as one piece to keep its lights on my lamp (60 degrees at most)
        hd = g["head"].matrix_world.translation
        lp = ctx["lamp"].location
        want = math.degrees(math.atan2(lp.x - hd.x, -(lp.y - hd.y)))
        body = gs["yaw"]                    # its front (local -y) is at world yaw `yaw`, so the head's turn is want - yaw
        turn = (want - body + 180.0) % 360.0 - 180.0
        g["head"].rotation_euler = (0, 0, math.radians(max(-60.0, min(60.0, turn))))
    place_lamp(ctx, tl, t)
    carry(ctx, tl, t, "radio", "radioset", RADIO_SHELF, (0.0, -0.06, 0.02))
    carry(ctx, tl, t, "binos", "binoculars", BINO_SILL, (0.0, -0.08, 0.05), both=True)
    part_pines(ctx, gs, t)
    # a dim olive light over the giant's stones, and fog to its waist that goes with it (L64 to L67)
    gp = g["root"].location
    kit.LIGHTS["moss"]["obj"].location = (gp.x, gp.y - 7.0, gp.z + 24.0)
    lk = LOOKS[ctx["look"]]
    fogt = next((o for o in ctx["fog"] if o.name == "fog.tower"), None)
    if lk.get("waist") and not gs["hidden"] and fogt is not None:
        fogt.location = (gp.x, gp.y - 2.0, gp.z + 9.0)
    # the lantern's glass can glow brighter for the distant wide (a cue "lampglow", k times its usual strength)
    k = _switch(_cues(tl, "lampglow"), "k", t, 1.0)
    for nd in kit.MATS["lamp glow"].node_tree.nodes:
        if nd.type == "EMISSION":
            nd.inputs["Strength"].default_value = 0.12 * k
    sw = _last([c for c in _cues(tl, "lamp") if "swing" in c], t)
    if sw is not None:
        x = t - sw["t"]
        a = math.radians(sw["swing"]) * math.exp(-x / sw.get("decay", 1.2)) * math.sin(2 * math.pi * x / 1.1)
        ctx["lamp"].rotation_euler = (a, 0.3 * a, 0)
    else:
        ctx["lamp"].rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    lp = ctx["lamp"].matrix_world @ V((0, 0, 0.2))
    ctx["key_obj"].location = (lp.x, lp.y, lp.z)
    if ctx.pop("need_me_links", False):
        # the cast is built after set.build: the cold fill keeps off me and the giant (I'm lamp-lit), and my face
        # key lights only me
        me = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("me.")]
        link_lights(kit, "not the giant", ["fill"], me, "EXCLUDE")
        link_lights(kit, "me only", ["facekey"], me, "INCLUDE")
    hg = bpy.data.objects.get("me.headg")
    if hg is not None:
        m = hg.matrix_world
        fd = (m.to_3x3() @ V((0, -1, 0))).normalized()
        c = m.translation
        kit.LIGHTS["facekey"]["obj"].location = (c.x + fd.x * 0.6, c.y + fd.y * 0.6, c.z - 0.45)
    toe_w = g["leg_l"].matrix_world @ V((0.0, -LEG[1] / 2 - 2.6, -HIP_Z + 0.5))
    kit.LIGHTS["toelight"]["obj"].location = (toe_w.x, toe_w.y - 1.0, toe_w.z + 2.2)
    over["toelight"] = _switch(_cues(tl, "footlit"), "gain", t, 0.0)
    over["facekey"] = over.get("facekey", 1.0) * _switch(_cues(tl, "facekey"), "gain", t, 1.0)
    hd = g["head"].matrix_world.translation
    aim_at(ctx["rim_obj"], (hd.x, hd.y, hd.z + 2.0))
    return over
