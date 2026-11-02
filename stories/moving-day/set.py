"""Moving Day: Mum's room in the new house at 3 a.m., and the Boxes. Built from kit.py's parts (batch 2, story 4,
ep17; nothing here is shared with another story's set). This is the creature-test build: Mum's room and the
Boxes, to the brief (`productions/ep17-moving-day/02-brief.md`). The rest of the house comes after it.

Coordinates: the floor is z = 0 and the ceiling is CEIL (2.35 m, low next to a 1.75 m cast member). Mum's room
runs x = X0 .. X1 (left to right as you look in from her door) and y = 0 (the front wall, with her door) .. Y1
(the far wall). Looking in from the door you face +y. Her low divan has its head against the left wall, so from
the door you see it side-on, and she sleeps on her back with her head toward the wall. The plug-in nightlight is
low on the far wall, beyond the Boxes as seen from the door. Just inside the door is a small
wooden chest of drawers with the dim lamp on it (unlit until L51). The window is on the right wall, curtained.
There are no boxes in this room but the Boxes (continuity item 8). Facing the door from the room is yaw 0 (a
character faces -y).

THE BOXES (note 18, "Uncanny beats tentacles"; the brief's continuity list): one figure of 15 taped brown moving
boxes, built once at full size: the face box (its head), a neck chain of three (N1 to N3), a torso of three
(pelvis, belly, a wide chest), two boxes to each leg and two to each arm. It's R6-shaped and every proportion is
wrong: 2.85 m straight without the neck, so it stoops under any ceiling and the neck chain folds along it; limbs
far too long (hanging, its hands reach its knees). The boxes sag and bulge, corners crushed, handholds cut in the
torso. Every box keeps its own outside packing tape along its flap seam. The joints between its boxes are bare
outside: a dark gap with tape glinting inside it, and nothing else holds them. Each hand is the open end of a
forearm box, its four flaps splayed like fingers. Nothing on it is thinner than a box. Its face is a black marker
drawing on the face box (marker.py, one marker width), a new drawing each time we see it: FACES. The face box is
always the same box: tone FACE_TONE and one crushed top corner, the identifying dent. It's never seen moving.
`build_boxes()` makes it once and `pose_boxes()` only places those same parts (the torso by its joints, the neck
chain along the ceiling toward a point, each arm by reaching for a point), and `set_face()` only swaps the
drawing, so it's the same thing in every shot. A pose can leave out neck boxes ("neck": 0 to 3): morning 1 shows
12 boxes, morning 2 13, morning 3 14, then 15.

Cues read here (all optional):
- boxes: {"pose": a name in POSES or a pose dict, "face": one of marker.FACES, "hidden": bool} the Boxes from here
- nightlight: {"on": bool} Mum's nightlight (on unless a cue says otherwise)
- lamp: {"on": 0..1, "dur": s} the dim lamp on her chest of drawers, eased to its level over dur (off unless
  a cue says otherwise)

Acting keys read here (acting.py ignores them): "lie": [x, y, z] degrees, the character's whole body turned to
lie down (pos z is the feet's height; [-88, 0, 90] is on the back, head toward -x); "hide_parts": rig part names
(e.g. "arm1") left out of the render, for limbs under the quilt; "part_offset": {part: [x, y, z]} metres added
to a rig part's place in its parent (an arm lifted to lie on top of the quilt); "sit": true (R6 sitting, the legs
straight out); "width": the character's width against its height (R6 shoulders are wider than this house's hall:
standing, the cast is drawn at 0.88; Mum lies in bed at 1.0).
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector as V
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_ms = importlib.util.spec_from_file_location("moving_day_marker", HERE / "marker.py")
marker = importlib.util.module_from_spec(_ms)
_ms.loader.exec_module(marker)

# ------------------------------------------------------------------------------------------------ Mum's room
X0, X1, Y1 = -1.7, 1.3, 3.3
CEIL = 2.35                # the height the walls, ceilings and the Boxes' poses are built at
LOW, LADDER = 1.84, 3.3    # the ceiling rests on my hair at the start; ladder height from the third morning
PC = {"h": CEIL}           # the ceiling height the Boxes' pose is solved against (animate sets it per pose)
TOPS = []                  # wall pieces that reach the ceiling: (object, bottom z), restretched every frame
CEILS = []                 # things fixed to the ceiling: (object, built z)
SQUARE_X = (-2.3, -1.7)   # L46: the door's square of light on the hall's south wall and ceiling
SQUARE_Z0 = 1.05
SQUARE_DEPTH = 0.6
WALL_T = 0.12
DOOR_X = (-1.6, -0.85)                    # her door, front wall, near the bed's head: I stand in it
DOOR_H = 1.78
WIN_Y, WIN_Z = (1.0, 2.0), (0.9, 1.7)    # the window, right wall, curtained
BED_X, BED_Y = (X0, X0 + 2.05), (1.25, 2.6)
BASE_Z, MAT_Z = 0.2, 0.42                 # the divan's top, the mattress's top
DRAWERS = (-0.5, 0.25)                    # the chest of drawers just inside the door, with the lamp
NIGHTLIGHT = (0.28, 0.3)                  # x on the far wall (beyond the Boxes from the door), height
RIG_S = 0.34                              # rig.py's metres per rig unit

# ------------------------------------------------------------------------------------------------ the house
# One small single-storey house (the brief), no stairs. Mum's room (above) and my room open off the north side
# of a narrow hall; across it, the front room (the front door, the stack, the photo wall, the deep front sill)
# and the kitchen. The hall cupboard, with its shelf at chest height, is at the hall's east end. Rooms are
# (x0, x1, y0, y1) inside their walls; every wall is WALL_T thick, centred on the line between two rooms.
MUMS = (X0, X1, 0.0, Y1)
MINE = (-4.6, -1.82, 0.0, Y1)
HALL = (-4.6, X1, -1.42, -0.12)
FRONT = (-4.6, -0.6, -5.1, -1.54)
KITCHEN = (-0.48, 2.0, -3.9, -1.54)
CUPBOARD = (X1 + WALL_T, 1.95, -1.2, -0.35)
MY_DOOR = (-2.75, -2.0)              # my door, the hall's north wall
FRONT_DOOR_H = (-3.2, -2.45)         # the front room's doorway, the hall's south wall
KITCHEN_DOOR = (0.1, 0.8)            # the kitchen's doorway, the hall's south wall
STREET_DOOR = (-4.3, -3.45)          # the front door, in the front room's south wall: it opens straight in
MY_WIN = (-3.4, -2.7, 0.85, 1.7)      # my room's back wall
FRONT_WIN = (-4.85, -4.05, 0.8, 1.7)   # the front room's east wall, with its deep sill (the mug)
KIT_WIN = (0.8, 1.5, 0.95, 1.7)       # over the sink
CUP_Y = (-1.2, -0.35)                # the cupboard's door, in the hall's east wall
SHELF_Z = 1.2                        # the cupboard shelf, chest height
SILL = (-0.8, -4.45, 0.8)            # where the mug stands on the front sill
STACK = {"x0": -3.32, "w": 0.37, "d": 0.4, "h": 0.36, "cols": 6, "rows": 4, "y": FRONT[2]}
COUNTER = {"y0": -3.9, "d": 0.6, "z": 0.9, "x0": 0.2, "x1": 2.0}
SINK_X = 1.15
KETTLE = {"right": (SINK_X - 0.44, -3.62), "left": (SINK_X + 0.5, -3.62)}   # as you face the counter (south)
ROLLS_AT = (1.7, -3.62)              # the counter's far (left) end: the tape rolls, then the bare cores
MY_BED = {"x": (-4.6, -3.65), "y": (1.25, Y1), "top": 0.5}
MY_PILLOW = (-4.12, 2.97)

# ------------------------------------------------------------------------------------------------ the Boxes
PX_PER_M = 2048                           # marker drawings: pixels per metre of board (the head front is 983 px)
G = 0.035                                 # the bare gap at every joint
DIM = {"thigh": (0.24, 0.24, 0.60), "shin": (0.22, 0.23, 0.62), "hip_x": 0.15,
       "pelvis": (0.50, 0.36, 0.28), "belly": (0.47, 0.38, 0.34), "chest": (0.70, 0.42, 0.40),
       "neck": (0.36, 0.32, 0.27), "head": (0.48, 0.42, 0.44),
       "upper": (0.19, 0.19, 0.74), "fore": (0.18, 0.18, 0.70), "flap": (0.14, 0.087)}
L_UPPER = DIM["upper"][2] - 0.06 + G / 2  # shoulder pivot to elbow pivot
L_FORE = DIM["fore"][2] + G / 2           # elbow pivot to wrist
L_NECK = DIM["neck"][2] + G               # one neck box, pivot to pivot
HIP_Z = DIM["shin"][2] + DIM["thigh"][2] + 1.5 * G
TONES = ["#a8794c", "#9b6d43", "#b2865a", "#8f6640", "#a57a50", "#b08152", "#9d7349", "#a98055"]
FACE_TONE = "#a87b50"                     # the face box, always
FACES = marker.FACES
GLOSSY = {"stare"}
FACE_K = 22                               # the stack box (top row, fifth column) the face box takes the place of                        # the one wet, glossy face

# Poses: angles in degrees. hip [forward, out], knee bend; waist / spine1 / spine2 [forward, side, twist];
# neck: how many neck boxes show (0 to 3), chain: {"to": [x, y], "drop": deg} the chain runs along the ceiling
#   toward that point, then the face box hangs from its end (or, with no chain, "head": [forward, side, twist]);
# face: {"dir": [x, y, z], "roll": deg} the way the drawn face looks (the box hangs below the chain's end, so a
#   face aimed down hangs upside down);
# hands: {side: [x, y, z]} where each wrist reaches (two-bone IK, the elbow toward pole), else arm
#   [forward, out, elbow]; flaps: {side: [front, back, out, in]} splay degrees, curl: degrees each flap tip folds in;
# wrist_roll: {side: degrees} the hand turned about the forearm (flaps broadside to the camera read as an open
#   box end; edge-on they read as wire);
# press: the legs fold (thighs forward, knees bent twice as far) until the torso is under the ceiling;
# land: [x, y] moves the whole figure so the face box hangs over this point (it doesn't converge reliably);
# flip: the drawing turned 180 degrees on the box, so it reads upright on a face box that hangs upside down.
SOLO_FLOOR = (0.3, -0.79, 0.0)
SOLO_SHELF = (1.66, -0.79, SHELF_Z)
POSES = {
    # morning 1 (L01 to L13), the hall: 12 boxes, no neck, stooped under the ceiling till the face box's top just
    # touches it, the frown down the hall (west) at nothing; its arms hang at its sides
    "hall": {"at": [0.55, -0.74], "yaw": -90, "neck": 0, "press": True, "hip": [[3, 4], [1, 5]], "knee": [3, 2],
             "waist": [18, 0, 0], "spine1": [16, 2, 0], "spine2": [14, -1, 2], "head": [-36, 0, 3],
             "hang": {"out": 0.0, "fwd": 0.05}, "flaps": {"-1": [8, 10, 6, 12], "1": [10, 8, 12, 6]}, "flaps": {"-1": [8, 10, 6, 12], "1": [10, 8, 12, 6]},
             "curl": 25, "key": [0.15, -1.3, 1.05], "body_key": [0.3, -1.35, 0.5]},
    # morning 2 (L17 to L21), the kitchen by the fridge: 13 boxes (N1), the face box folded forward along the
    # ceiling, its wet stare on the back of Mum's head at the counter
    "kitchen": {"at": [-0.1, -2.3], "yaw": 60, "neck": 1, "press": True, "clear_n1": True, "hip": [[2, 10], [0, 12]], "knee": [4, 3],
                "waist": [12, 2, -3], "spine1": [12, -3, 3], "spine2": [15, 4, -2],
                "chain": {"to": [0.72, -2.95], "drop": -3.0}, "face": {"dir": [0.72, 0.12, -0.68], "roll": 0}, "flip": True,
                "hang": {"out": 0.05}, "flaps": {"-1": [8, 10, 6, 12], "1": [10, 8, 12, 6]},
                "curl": 25, "key": [1.3, -2.2, 1.0], "body_key": [1.5, -3.3, 0.6]},
    # morning 3 (L26 to L35), the front room's corner by its doorway: 14 boxes (N1, N2), two along the ceiling,
    # the face box at the end of them looking out into the room, its eyes slid hard toward Mum's door
    "front": {"at": [-1.5, -2.3], "yaw": -100, "neck": 2, "press": True, "clear_n1": True, "hip": [[2, 9], [0, 11]], "knee": [4, 3],
              "waist": [12, 2, -2], "spine1": [12, -2, 2], "spine2": [15, 3, -2],
              "chain": {"to": [-2.62, -1.74], "drop": -3.0},
              "face": {"dir": [0.1, -0.7, -0.7], "ext": [0.0, -1.0, -0.15], "roll": 0}, "flip": True, "mirror": True,
              "hang": {"out": 0.05, "fwd": 0.2}, "flaps": {"-1": [8, 10, 6, 12], "1": [10, 8, 12, 6]},
              "curl": 25, "key": [-1.9, -3.2, 1.0], "body_key": [-1.85, -3.55, 0.55], "body_gain": 1.6},
    # morning 4 (L36 to L40), the corner of my room: 15 boxes, the chain along the ceiling toward my bed and the
    # face box hanging face-down over my pillow, every one of its eyes on me
    "mine": {"at": [-2.6, 2.42], "yaw": -97, "neck": 3, "press": True, "clear_n1": True, "hip": [[2, 12], [0, 14]], "knee": [4, 3],
             "waist": [14, 2, -3], "spine1": [14, -3, 3], "spine2": [18, 4, -2],
             "chain": {"to": [-4.25, 2.72]}, "face": {"dir": [0.15, -0.2, -0.97], "roll": 0}, "flip": True,
             "hang": {"out": 0.05}, "flaps": {"-1": [8, 10, 6, 12], "1": [10, 8, 12, 6]},
             "curl": 25, "key": [-3.75, 2.2, 0.75], "key_gain": 1.0, "body_key": [-2.95, 3.22, 1.6], "body_gain": 1.4},
    # the end (L76 to L78): the face box alone on the hall cupboard's shelf, its smile out at the door
    # the L01 box alone (the Boxes' right shin, its peeled tape, the tape inside the gap at its top): on the hall
    # floor for the L01 close, on the cupboard's shelf for L77 (the same box, the same framing; see make_story.py)
    "solo_floor": {"solo": True, "at": SOLO_FLOOR, "yaw": -90, "body_key": [SOLO_FLOOR[0] - 0.55, SOLO_FLOOR[1] + 0.55, 0.75],
                   "body_aim": [SOLO_FLOOR[0], SOLO_FLOOR[1], 0.32], "body_gain": 1.0},
    "solo_shelf": {"solo": True, "at": SOLO_SHELF, "yaw": -90, "body_key": [SOLO_SHELF[0] - 0.55, SOLO_SHELF[1] + 0.55, SHELF_Z + 0.75],
                   "body_aim": [SOLO_SHELF[0], SOLO_SHELF[1], SHELF_Z + 0.32], "body_gain": 1.0},
    # the face box alone: one box in the stack by the front door (the top row's fifth column), frown out into the room
    # (S01, the opening), and the same box alone on the hall cupboard's shelf at the end, frown out at the door
    "head_stack": {"headonly": True, "at": [-1.655, -4.865, 3 * 0.36 + 0.0], "yaw": 183, "scale": 0.8},
    "head_shelf": {"headonly": True, "at": [1.66, -0.79, SHELF_Z], "yaw": -90, "scale": 1.0},
    # morning 2 (L22 to L25), the kitchen: the body stands in the hall doorway out of frame; three neck boxes run
    # flat along the kitchen ceiling from the doorway to over the counter, the face box hanging at their end, its stare
    # down at the back of Mum's head. The ceiling is a third of the way up (2.2 m)
    "kitchen2": {"ceil": 2.2, "at": [0.45, -0.86], "yaw": 0, "neck": 3, "press": True, "clear_n1": True,
                 "hip": [[2, 10], [0, 12]], "knee": [4, 3], "waist": [12, 2, -3], "spine1": [12, -3, 3],
                 "spine2": [15, 4, -2], "chain": {"to": [0.7, -2.75], "drop": -3.0}, "land": [0.7, -2.75],
                 "face": {"dir": [0.7, -0.25, -0.62], "roll": 0}, "flip": True,
                 "hang": {"out": 0.05}, "flaps": {"-1": [8, 10, 6, 12], "1": [10, 8, 12, 6]},
                 "curl": 25, "key": [1.5, -2.2, 0.9], "body_key": [0.2, -1.4, 1.3], "body_aim": [0.45, -1.2, 1.6]},
    "stand": {"at": [0.0, 0.0], "yaw": 0, "neck": 0, "hip": [[0, 2], [0, 2]], "knee": [0, 0], "waist": [0, 0, 0],
              "spine1": [2, 1, 0], "spine2": [3, -1, 0], "head": [6, 0, 4],
              "arm": {"-1": [4, 3, 6], "1": [3, 3, 8]}, "flaps": {"-1": [8, 10, 6, 12], "1": [10, 8, 12, 6]},
              "curl": 25},
    # 3 a.m., L48 on: behind Mum's bed, folded under the ceiling, the neck chain along the ceiling to over the
    # middle of the bed, the face box hanging from it over her chest, face down and wide open; its arms already
    # down beside the bed, the flap hands resting on the quilt's edge at her shoulder and on the mattress edge
    "over_bed": {"at": [0.36, 2.9], "yaw": -30, "neck": 3, "hip": [[2, 12], [0, 14]], "knee": [4, 3],
                 "press": True, "waist": [12, 2, -3], "spine1": [12, -3, 3], "spine2": [16, 4, -2],
                 "chain": {"to": [-0.82, 1.95]}, "face": {"dir": [-0.1, -0.6, -0.8], "roll": 4}, "flip": True,
                 "hands": {"-1": [-0.12, 2.28, 0.72], "1": [0.2, 2.42, 0.66]},
                 "pole": {"-1": [-0.6, 0.6, 0.3], "1": [0.6, 0.6, 0.2]},
                 "flaps": {"-1": [34, 70, 38, 72], "1": [36, 68, 34, 72]}, "curl": 6,
                 "wrist_roll": {"-1": 42, "1": -45},
                 # a cold side light on the neck chain and the body, so the boxes above the face read as board and
                 # not as a black hair-piece (the critic's round 1)
                 "body_key": [1.1, 0.7, 1.7], "body_aim": [-0.45, 2.4, 2.0], "body_gain": 1.3},
}


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def _last(cs, t):
    cs = [c for c in cs if c["t"] <= t + 1e-9]
    return cs[-1] if cs else None


def _switch(keys, attr, t, default):
    v = default
    for k in keys:
        if attr in k and k["t"] <= t + 1e-9:
            v = k[attr]
    return v


def workdir(tl) -> Path:
    d = ROOT / "out" / "work" / tl.get("name", "moving-day") / "faces"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ------------------------------------------------------------------------------------------ node helpers


def _in(node, ident):
    """A node input by identifier (the Mix node has three sockets named "A")."""
    return next(s for s in node.inputs if s.identifier == ident)


def _out(node, ident):
    return next(s for s in node.outputs if s.identifier == ident)


def _feed(L, sock, v):
    if isinstance(v, (int, float)):
        sock.default_value = v
    elif isinstance(v, tuple):
        sock.default_value = v
    else:
        L.new(v, sock)


def _math(N, L, op, a, b=0.0, clamp=False):
    n = N.new("ShaderNodeMath")
    n.operation = op
    n.use_clamp = clamp
    _feed(L, n.inputs[0], a)
    _feed(L, n.inputs[1], b)
    return n.outputs[0]


def _range(N, L, v, a0, a1, b0=0.0, b1=1.0):
    n = N.new("ShaderNodeMapRange")
    n.clamp = True
    _feed(L, n.inputs["Value"], v)
    n.inputs["From Min"].default_value = a0
    n.inputs["From Max"].default_value = a1
    n.inputs["To Min"].default_value = b0
    n.inputs["To Max"].default_value = b1
    return n.outputs["Result"]


def _mixc(N, L, fac, a, b):
    n = N.new("ShaderNodeMix")
    n.data_type = "RGBA"
    _feed(L, _in(n, "Factor_Float"), fac)
    _feed(L, _in(n, "A_Color"), a)
    _feed(L, _in(n, "B_Color"), b)
    return _out(n, "Result_Color")


def _mixf(N, L, fac, a, b):
    n = N.new("ShaderNodeMix")
    n.data_type = "FLOAT"
    _feed(L, _in(n, "Factor_Float"), fac)
    _feed(L, _in(n, "A_Float"), a)
    _feed(L, _in(n, "B_Float"), b)
    return _out(n, "Result_Float")


def _tint(kit, hexc, k):
    c = kit.col(hexc)
    return (min(1.0, c[0] * k), min(1.0, c[1] * k), min(1.0, c[2] * k), 1.0)


# ------------------------------------------------------------------------------------------------ materials


def board(kit, name, tone, seed=0, half=(0.25, 0.2, 0.2), tape="y", tape_len=0.085, tape_w=0.05, decals=None,
          holes=False, wear=0.0):
    """Brown corrugated board: mottled, a fine fibre tooth, packing tape over the seams (a band over the top and
    bottom, `tape` the way it runs, shinier and a little lighter, the board showing through it), handholds
    cut in the side faces, and marker drawings: decals = {"front"|"left"|"right": image node slot or a bpy image}.
    Everything is in object space, so it follows the box's dents. Returns (material, {slot: image node})."""
    m = kit._new(name)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    hx, hy, hz = half
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs[0])
    nsep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Normal"], nsep.inputs[0])
    mp = N.new("ShaderNodeMapping")
    mp.inputs["Location"].default_value = (seed * 1.37, seed * 2.11, seed * 0.73)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    # the board: big soft patches (old boxes, handled), a fine tooth, a few darker scuffs
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.2
    nz.inputs["Detail"].default_value = 3.0
    L.new(mp.outputs["Vector"], nz.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.32
    ramp.color_ramp.elements[0].color = _tint(kit, tone, 0.78 - wear * 0.15)
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = _tint(kit, tone, 1.06)
    L.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    fine = N.new("ShaderNodeTexNoise")
    fine.inputs["Scale"].default_value = 120.0
    fine.inputs["Detail"].default_value = 4.0
    L.new(mp.outputs["Vector"], fine.inputs["Vector"])
    tooth = _range(N, L, fine.outputs["Fac"], 0.3, 0.7, 0.9, 1.06)
    col = ramp.outputs["Color"]
    mul = N.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    _in(mul, "Factor_Float").default_value = 1.0
    L.new(col, _in(mul, "A_Color"))
    cc = N.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        L.new(tooth, cc.inputs[k])
    L.new(cc.outputs["Color"], _in(mul, "B_Color"))
    col = _out(mul, "Result_Color")
    # packing tape over the seams
    tm = 0.0
    if tape:
        a = sep.outputs["X" if tape == "y" else "Y"]
        band = _range(N, L, _math(N, L, "ABSOLUTE", a), tape_w / 2 - 0.0015, tape_w / 2 + 0.0015, 1.0, 0.0)
        z = sep.outputs["Z"]
        top = _range(N, L, z, hz - tape_len - 0.002, hz - tape_len + 0.002)
        bot = _range(N, L, z, -hz + tape_len - 0.002, -hz + tape_len + 0.002, 1.0, 0.0)
        tm = _math(N, L, "MULTIPLY", band, _math(N, L, "MAXIMUM", top, bot))
        tape_col = _mixc(N, L, 0.5, col, kit.col("#d8b071"))
        col = _mixc(N, L, tm, col, tape_col)
    # handholds: a dark slot high in each side face
    if holes:
        side = _range(N, L, _math(N, L, "ABSOLUTE", nsep.outputs["X"]), 0.55, 0.7)
        ey = _math(N, L, "DIVIDE", sep.outputs["Y"], min(0.065, hy * 0.4))
        ez = _math(N, L, "DIVIDE", _math(N, L, "SUBTRACT", sep.outputs["Z"], hz - 0.085), 0.022)
        r2 = _math(N, L, "ADD", _math(N, L, "MULTIPLY", ey, ey), _math(N, L, "MULTIPLY", ez, ez))
        hole = _math(N, L, "MULTIPLY", side, _range(N, L, r2, 0.85, 1.0, 1.0, 0.0))
        col = _mixc(N, L, hole, col, (0.006, 0.005, 0.005, 1))
    # marker drawings, one image per face
    slots = {}
    ink = 0.0
    for slot, img in (decals or {}).items():
        tex = N.new("ShaderNodeTexImage")
        tex.extension = "CLIP"
        tex.interpolation = "Cubic"
        if isinstance(img, bpy.types.Image):
            tex.image = img
        slots[slot] = tex
        if slot == "front":     # the -y face, looking at it: u = x
            u = _math(N, L, "DIVIDE", _math(N, L, "ADD", sep.outputs["X"], hx), 2 * hx)
            mask = _range(N, L, nsep.outputs["Y"], -0.7, -0.55, 1.0, 0.0)
        elif slot == "left":    # the +x face (the box's own left), looking at it: u = y
            u = _math(N, L, "DIVIDE", _math(N, L, "ADD", sep.outputs["Y"], hy), 2 * hy)
            mask = _range(N, L, nsep.outputs["X"], 0.55, 0.7)
        else:                   # "right": the -x face, looking at it: u = -y
            u = _math(N, L, "DIVIDE", _math(N, L, "SUBTRACT", hy, sep.outputs["Y"]), 2 * hy)
            mask = _range(N, L, nsep.outputs["X"], -0.7, -0.55, 1.0, 0.0)
        v = _math(N, L, "DIVIDE", _math(N, L, "ADD", sep.outputs["Z"], hz), 2 * hz)
        cx = N.new("ShaderNodeCombineXYZ")
        L.new(u, cx.inputs["X"])
        L.new(v, cx.inputs["Y"])
        L.new(cx.outputs[0], tex.inputs["Vector"])
        k = _math(N, L, "MULTIPLY", tex.outputs["Alpha"], mask)
        ink = k if ink == 0.0 else _math(N, L, "MAXIMUM", ink, k)
    if ink != 0.0:
        col = _mixc(N, L, ink, col, kit.col("#060507"))
    L.new(col, b.inputs["Base Color"])
    rough = _mixf(N, L, tm, 0.9, 0.42) if tape else 0.9
    if ink != 0.0:
        ir = N.new("ShaderNodeValue")
        ir.outputs[0].default_value = 0.8
        slots["ink_rough"] = ir
        rough = _mixf(N, L, ink, rough, ir.outputs[0])
    _feed(L, b.inputs["Roughness"], rough)
    spec = _mixf(N, L, tm, 0.3, 0.48) if tape else 0.3
    if ink != 0.0:   # marker on board has no sheen: seen at a grazing angle it must still read black
        spec = _mixf(N, L, ink, spec, 0.02)
    _feed(L, b.inputs["Specular IOR Level"], spec)
    bp = N.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.12
    bp.inputs["Distance"].default_value = 0.002
    L.new(fine.outputs["Fac"], bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    kit._fogged(m, b.outputs[0])
    return m, slots


def tape_mat(kit):
    name = "packing tape"
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col("#b98e55")
    b.inputs["Roughness"].default_value = 0.48   # a sheen, not a mirror: a light grazing it must not clip
    b.inputs["Specular IOR Level"].default_value = 0.3
    # a few creases in the tape catch the light in streaks
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 60.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.25
    bp.inputs["Distance"].default_value = 0.001
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    kit._fogged(m, b.outputs[0])
    return m


def fabric(kit, name, hexc, rough=0.92, sheen=0.3):
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 0.2
    for k in ("Sheen Weight", "Sheen"):
        if k in b.inputs:
            b.inputs[k].default_value = sheen
            break
    kit._fogged(m, b.outputs[0])
    return m


def image_mat(kit, name, img, rough=0.9, sheen=0.3):
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 0.2
    for k in ("Sheen Weight", "Sheen"):
        if k in b.inputs:
            b.inputs[k].default_value = sheen
            break
    kit._fogged(m, b.outputs[0])
    return m


MARKER_KEY = __import__("hashlib").sha1((HERE / "marker.py").read_bytes()).hexdigest()[:8]


def pil_image(name, im: Image.Image, path: Path):
    """A PIL drawing as a Blender image. Drawings are keyed on marker.py's contents, so a changed drawing is
    never read back from an old file."""
    path = path.with_name(f"{path.stem}-{MARKER_KEY}{path.suffix}")
    if not path.exists():
        im.save(path)
    img = bpy.data.images.load(str(path), check_existing=True)
    img.colorspace_settings.name = "sRGB"
    img.alpha_mode = "STRAIGHT"
    return img


def patchwork(w=1100, h=1000, seed=4) -> Image.Image:
    """Mum's old quilt: hand-sewn squares of faded plum, lilac and rose, a few split into triangles."""
    r = np.random.default_rng(seed)
    # faded plum, lilac and rose, in a few strengths
    pal = [(110, 64, 92), (132, 86, 112), (150, 132, 178), (172, 156, 196), (176, 116, 134), (196, 142, 156),
           (124, 100, 140), (186, 166, 176)]
    im = Image.new("RGB", (w, h), pal[4])
    d = ImageDraw.Draw(im)
    n = 10
    sx, sy = w / n, h / (n * h / w)
    rows = int(round(h / sx))
    sy = h / rows
    for j in range(rows):
        for i in range(n):
            x0, y0 = i * sx, j * sy
            c = pal[int(r.integers(len(pal)))]
            d.rectangle([x0, y0, x0 + sx, y0 + sy], fill=c)
            if r.random() < 0.3:
                c2 = pal[int(r.integers(len(pal)))]
                d.polygon([(x0, y0), (x0 + sx, y0), (x0, y0 + sy)], fill=c2)
            elif r.random() < 0.2:   # a small print: dots
                c2 = tuple(min(255, int(v * 1.25)) for v in c)
                for a in range(4):
                    for b_ in range(4):
                        cx, cy = x0 + (a + 0.5) * sx / 4, y0 + (b_ + 0.5) * sy / 4
                        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=c2)
    for i in range(n + 1):   # seams, and a running stitch beside each
        d.line([(i * sx, 0), (i * sx, h)], fill=(66, 48, 62), width=3)
    for j in range(rows + 1):
        d.line([(0, j * sy), (w, j * sy)], fill=(66, 48, 62), width=3)
    for i in range(n + 1):
        for y in range(0, h, 14):
            d.line([(i * sx + 7, y), (i * sx + 7, y + 6)], fill=(215, 205, 180), width=2)
    noise = (r.random((h // 4, w // 4)) * 255).astype(np.uint8)
    nz = Image.fromarray(noise).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))
    a = np.asarray(im, np.float32) * (0.88 + 0.16 * np.asarray(nz, np.float32)[..., None] / 255)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.SMOOTH)


def materials(kit, wd: Path):
    """The brief's palette: off-white walls a little green-grey, pale ceilings, honey floorboards, painted trim,
    near-black nights; the quilt (faded plum, lilac, rose) is the only strong colour."""
    M = {}
    M["wall"] = kit.grime("#c2c5b6", 0.9, 1.6, name="wall paint", rough=0.85)
    M["ceiling"] = kit.plastic("#cacbc3", 0.9, name="ceiling paint")
    _b = M["ceiling"].node_tree.nodes["Principled BSDF"]
    _b.inputs["Emission Color"].default_value = kit.col("#cacbc3")
    _b.inputs["Emission Strength"].default_value = 0.0
    M["_ceil_emit"] = _b.inputs["Emission Strength"]
    M["trim"] = kit.plastic("#d4d2c8", 0.5, name="trim")
    M["floor"] = kit.planks("#a77d4b", "#83603a", 1.0, "Y", name="floorboards", rough=0.55)
    M["wood"] = kit.planks("#6e4d34", "#523823", 2.0, "Z", name="dark wood", rough=0.5)
    M["drawer"] = kit.plastic("#5d412c", 0.55, name="drawer front")
    M["base"] = fabric(kit, "divan", "#3a3b40")
    M["sheet"] = fabric(kit, "sheet", "#8d9096", 0.85, 0.4)
    M["pillow"] = fabric(kit, "pillow", "#d6d3c9", 0.85, 0.4)
    M["curtain"] = fabric(kit, "curtain", "#4b5350", 0.95, 0.5)
    M["shade"] = fabric(kit, "lamp shade", "#d2c7b0", 0.8, 0.3)
    M["tape"] = tape_mat(kit)
    M["cord"] = kit.plastic("#1d1c1c", 0.5, name="cord")
    M["bulb"] = kit.glass("#c9cbc6", name="bulb glass")
    M["metal"] = kit.metal("#9a9da0", 0.35, name="metal")
    M["door"] = kit.plastic("#d3d1c6", 0.6, name="door paint")
    M["shelf"] = kit.plastic("#cfcdc2", 0.7, name="shelf paint")
    M["coat a"] = fabric(kit, "coat a", "#2f3a33", 0.95, 0.4)
    M["coat b"] = fabric(kit, "coat b", "#45474f", 0.95, 0.4)
    M["cabinet"] = kit.plastic("#b7bcae", 0.55, name="cabinets")
    M["worktop"] = kit.plastic("#5a5651", 0.45, name="worktop")
    M["fridge"] = kit.plastic("#dcdcd6", 0.35, name="fridge")
    M["kettle"] = kit.plastic("#e0ded8", 0.35, name="kettle")
    M["core"] = kit.plastic("#a37c54", 0.85, name="tape core", spec=0.2)
    M["coreinside"] = kit.plastic("#6e5136", 0.9, name="tape core inside", spec=0.1)
    M["mug"] = kit.plastic("#2f5a63", 0.4, name="mug")
    M["frame wood"] = kit.plastic("#3a2c22", 0.5, name="frame wood")
    M["duvet"] = fabric(kit, "duvet", "#7d8691", 0.9, 0.4)
    # the outside, seen through every window: one glow, set by the time of day (animate)
    m = kit._new("outside")
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col("#7f8fa8")
    e.inputs["Strength"].default_value = 1.3
    kit._fogged(m, e.outputs[0])
    M["outside"] = m
    M["_outside_glow"] = e
    M["nightglow"] = kit.emit("#d6e4ff", 2.2, name="nightlight glow")
    q = pil_image("quilt", patchwork(), wd / "quilt.png")
    M["quilt"] = image_mat(kit, "quilt", q, 0.95, 0.5)
    # the same quilt folded or draped over a box shape (no UVs): the patchwork projected onto every side
    M["quilt drape"] = image_mat(kit, "quilt drape", q, 0.95, 0.5)
    nt = M["quilt drape"].node_tree
    tex = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
    tex.projection = "BOX"
    tex.projection_blend = 0.2
    tcn = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.9, 0.9, 0.9)
    nt.links.new(tcn.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], tex.inputs["Vector"])
    return M


# ------------------------------------------------------------------------------------------------ geometry


def cbox(kit, name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, parent=None, sub=5, bulge=0.012, sag=0.0,
         crush=(), dents=(), shear=(0.0, 0.0), wrinkle=0.0022, seed=0, bevel=0.005):
    """A cardboard box: a subdivided block whose sides bulge a little, top sags, corners crush in
    (crush = [((sx, sy, sz), metres, reach 0..1)]), with dents ([(axis 0..2, side +-1, u, v, radius, depth)]) and a
    shear (the top pushed over), and a faint crumple so flat faces catch the light like board, not plastic."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=sub, use_grid_fill=True)
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 2 * math.pi, 3)
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    for v in bm.verts:
        qx, qy, qz = (max(-1.0, min(1.0, c * 2)) for c in v.co)
        fx, fy, fz = 1 - qx * qx, 1 - qy * qy, 1 - qz * qz
        d = [bulge * qx * fy * fz, bulge * qy * fx * fz, -sag * fx * fy if qz > 0 else 0.0]
        d[0] += shear[0] * qz
        d[1] += shear[1] * qz
        q = V((qx, qy, qz))
        for corner, amt, reach in crush:
            c = V(corner)
            dist = (q - c).length / 2
            w = max(0.0, 1 - dist / reach) ** 2
            if w > 0:
                push = -c.normalized() * amt * w
                cr = amt * 0.35 * w * math.sin(qx * 9 + qy * 7 + qz * 11 + ph[0])
                d[0] += push.x + cr * c.x * 0.3
                d[1] += push.y + cr * c.y * 0.3
                d[2] += push.z - cr * 0.3
        for axis, side, u, vv, rad, depth in dents:
            qa = (qx, qy, qz)
            if abs(qa[axis] - side) < 1e-3:
                o = [qa[k] for k in range(3) if k != axis]
                g = math.exp(-((o[0] - u) ** 2 + (o[1] - vv) ** 2) / (rad * rad))
                d[axis] -= side * depth * g
        x, y, z = qx * hx, qy * hy, qz * hz
        wr = wrinkle * math.sin(x * 37 + ph[0]) * math.sin(y * 41 + ph[1]) * math.sin(z * 29 + ph[2])
        for k, qq in enumerate((qx, qy, qz)):
            if abs(abs(qq) - 1) < 1e-3:
                d[k] += wr * qq
        v.co = (x + d[0], y + d[1], z + d[2])
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    if mat is not None:
        ob.data.materials.append(mat)
    kit.link(ob, parent)
    if bevel > 0:
        m = ob.modifiers.new("bevel", "BEVEL")
        m.width = bevel
        m.segments = 1
        m.limit_method = "ANGLE"
        m.angle_limit = math.radians(35)
    return ob


def pleats(kit, name, x0, x1, y, z0, z1, mat, period=0.11, amp=0.035, n_per=8):
    """A hanging curtain panel: folds along x, straight down."""
    n = max(2, int((x1 - x0) / period * n_per))
    verts, faces = [], []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        yy = y + amp * math.sin(2 * math.pi * (x - x0) / period)
        verts += [(x, yy, z0), (x, yy, z1)]
    for i in range(n):
        a = 2 * i
        faces.append((a, a + 2, a + 3, a + 1))
    ob = kit.mesh_obj(name, verts, faces, mat, smooth=True)
    sol = ob.modifiers.new("solid", "SOLIDIFY")
    sol.thickness = 0.012
    return ob



def joint_tape(kit, name, parent, w, d, mat, axis="z", at=(0, 0, 0)):
    """The tape inside a bare joint: four short strips spanning the gap, set back from the boxes' faces, so all
    you see from outside is a dark gap with tape glinting in it. Parented to the outer box's joint."""
    g = kit.empty(name, at, parent)
    inset = 0.03
    span = G + 0.07
    # taped by hand, from the inside: the strips sit unevenly (place, angle, length), so the glints in a gap
    # never line up into a pattern (the critic's polish)
    r = np.random.default_rng(sum(map(ord, name)))
    for k, (fx, fy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        x, y = fx * (w / 2 - inset), fy * (d / 2 - inset)
        ln = span * float(r.uniform(0.8, 1.15))
        size = {"z": (0.045, 0.004, ln), "x": (ln, 0.045, 0.004)}[axis]
        u = float(r.uniform(0.3, 0.85))
        loc = {"z": (x * u, y, 0.0), "x": (0.0, y, x * u)}[axis]
        kit.box(f"{name}.{k}", size, loc, mat, g, rot=(0, 0, math.radians(fx * fy * float(r.uniform(8, 30)))))
    return g


# ------------------------------------------------------------------------------------------------ the Boxes


def build_boxes(kit, ctx, M, wd: Path, name="boxes"):
    """The Boxes, built once: 15 boxes on joints. Returns its parts: pivots, boxes, the face's slots."""
    rng = np.random.default_rng(29)
    tone = iter(TONES * 3)
    cr = {"name": name, "pivots": {}, "meshes": [], "images": {}, "neck": []}
    P = cr["pivots"]
    tape = M["tape"]
    root = kit.empty(name, (0, 0, 0))
    P["root"] = root

    def jitter(a=2.5, o=0.012):
        return (tuple(float(x) for x in rng.uniform(-o, o, 3)), tuple(math.radians(float(x)) for x in rng.uniform(-a, a, 3)))

    def part(pname, size, loc, parent, tape_axis="y", holes=False, decals=None, tone_hex=None, **kw):
        k = len(cr["meshes"])
        mat, slots = board(kit, f"{name} {pname}", tone_hex or next(tone), seed=k + 3, half=tuple(s / 2 for s in size),
                           tape=tape_axis, tape_len=kw.pop("tape_len", 0.085), holes=holes, decals=decals,
                           wear=0.4 if k % 3 == 0 else 0.0)
        off, rr = jitter(kw.pop("tilt", 2.5), kw.pop("slide", 0.012))
        ob = cbox(kit, f"{name}.{pname}", size, (loc[0] + off[0], loc[1] + off[1], loc[2] + off[2] * 0.3), rr, mat,
                  parent, seed=k + 11, **kw)
        cr["meshes"].append(ob)
        return ob, slots

    # the torso: three boxes stacked a little out of true, each on its own joint, bare gaps between them
    pw, pd, ph = DIM["pelvis"]
    bw, bd, bh = DIM["belly"]
    cw, cd, ch = DIM["chest"]
    waist = kit.empty(f"{name}.waist", (0, 0, HIP_Z), root)
    part("pelvis", DIM["pelvis"], (0, 0, G / 2 + ph / 2), waist, "x", holes=True, sag=0.01,
         crush=[((1, -1, -1), 0.03, 0.35)])
    s1 = kit.empty(f"{name}.spine1", (0, 0, G + ph), waist)
    part("belly", DIM["belly"], (0.015, 0, G / 2 + bh / 2), s1, "y", holes=True, bulge=0.02, sag=0.015,
         crush=[((-1, -1, 1), 0.04, 0.3)], shear=(0.012, 0.0))
    joint_tape(kit, f"{name}.jt.spine1", s1, bw, bd, tape)
    s2 = kit.empty(f"{name}.spine2", (0, 0, G + bh), s1)
    part("chest", DIM["chest"], (0, 0, G / 2 + ch / 2), s2, "y", bulge=0.018, sag=0.02,
         crush=[((1, -1, 1), 0.05, 0.32), ((-1, 1, 1), 0.035, 0.3)], dents=[(1, -1, 0.35, -0.2, 0.25, 0.018)])
    joint_tape(kit, f"{name}.jt.spine2", s2, bw, bd, tape)
    P.update(waist=waist, spine1=s1, spine2=s2)
    # the neck chain, N1 to N3, then the face box. Each joint's place is set by pose_boxes (in the world), so the
    # chain can fold along any ceiling; unposed, they stack straight up from the chest
    nw, nd, nl = DIM["neck"]
    parent, z0 = s2, G + ch
    for k in range(3):
        pv = kit.empty(f"{name}.n{k + 1}", (0, 0, z0), parent)
        ob, _ = part(f"neck{k + 1}", DIM["neck"], (0, 0, G / 2 + nl / 2), pv, "x", tilt=2.0, slide=0.008,
                     bulge=0.012, sag=0.01, crush=[((1 if k % 2 else -1, 1, 1), 0.03, 0.3)])
        joint_tape(kit, f"{name}.jt.n{k + 1}", pv, nw, nd, tape)
        cr["neck"].append((pv, ob))
        P[f"n{k + 1}"] = pv
        parent, z0 = pv, L_NECK
    # the face box: the same box every time (FACE_TONE, its crushed top corner), the drawing on its front. Its
    # own flap-seam tape runs over the top and down the two side faces, never across the drawing
    hw, hd, hh = DIM["head"]
    hp = kit.empty(f"{name}.headpivot", (0, 0, z0), parent)
    head, slots = part("head", DIM["head"], (0, 0, G / 2 + hh / 2), hp, "x", tilt=1.0, slide=0.004,
                       decals={"front": None, "left": None, "right": None}, tone_hex=FACE_TONE, sag=0.02,
                       crush=[((-1, -1, 1), 0.06, 0.38)], bulge=0.01, wrinkle=0.0004)
    joint_tape(kit, f"{name}.jt.head", hp, hw * 0.8, hd * 0.8, tape)
    # smooth-shaded, edges kept: under its tight light a flat-shaded front shows the mesh's facets
    for pl in head.data.polygons:
        pl.use_smooth = True
    head.modifiers.new("wn", "WEIGHTED_NORMAL").keep_sharp = True
    cr["face_slots"] = slots
    cr["head"] = head
    P["head"] = hp
    # legs: two long boxes each, bare gaps at the hip and the knee
    tw_, td_, th_ = DIM["thigh"]
    sw_, sd_, sh_ = DIM["shin"]
    for sx in (-1, 1):
        hip = kit.empty(f"{name}.hip{sx}", (sx * DIM["hip_x"], 0, HIP_Z), root)
        part(f"thigh{sx}", DIM["thigh"], (0, 0, -G / 2 - th_ / 2), hip, "y", tilt=1.5, bulge=0.008,
             crush=[((sx, -1, -1), 0.025, 0.3)])
        joint_tape(kit, f"{name}.jt.hip{sx}", hip, tw_, td_, tape)
        knee = kit.empty(f"{name}.knee{sx}", (0, 0, -G - th_), hip)
        dec = None
        part(f"shin{sx}", DIM["shin"], (0, 0, -G / 2 - sh_ / 2), knee, "x", tilt=1.2, bulge=0.008, decals=dec,
             crush=[((-sx, 1, -1), 0.03, 0.3)])
        joint_tape(kit, f"{name}.jt.knee{sx}", knee, sw_, sd_, tape)
        P[f"hip{sx}"], P[f"knee{sx}"] = hip, knee
    # arms: an upper and a forearm box each, far too long; the hand is the forearm's open end, four flaps
    uw, ud, ul = DIM["upper"]
    fw, fd, fl = DIM["fore"]
    f1, f2 = DIM["flap"]
    for sx in (-1, 1):
        sh = kit.empty(f"{name}.shoulder{sx}", (sx * (cw / 2 + G + uw / 2), 0, G + ch - 0.06), s2)
        part(f"upper{sx}", DIM["upper"], (0, 0, -ul / 2 + 0.06), sh, "x", tilt=1.5, bulge=0.006,
             crush=[((sx, 1, 1), 0.025, 0.3)])
        joint_tape(kit, f"{name}.jt.sh{sx}", sh, uw, ud, tape, axis="x", at=(-sx * (uw / 2 + G / 2), 0, -0.05))
        el = kit.empty(f"{name}.elbow{sx}", (0, 0, -L_UPPER), sh)
        part(f"fore{sx}", DIM["fore"], (0, 0, -G / 2 - fl / 2), el, None, tilt=1.2, bulge=0.006,
             crush=[((-sx, -1, 1), 0.02, 0.3)])
        joint_tape(kit, f"{name}.jt.el{sx}", el, fw, fd, tape)
        wr = kit.empty(f"{name}.wrist{sx}", (0, 0, -L_FORE), el)
        flaps = []
        fmat = cr["meshes"][-1].active_material
        for k, (n, hinge, width) in enumerate(((V((0, -1, 0)), (0, -fd / 2, 0), fw), (V((0, 1, 0)), (0, fd / 2, 0), fw),
                                               (V((sx, 0, 0)), (sx * fw / 2, 0, 0), fd),
                                               (V((-sx, 0, 0)), (-sx * fw / 2, 0, 0), fd))):
            hg = kit.empty(f"{name}.flap{sx}.{k}", hinge, wr)
            width *= 0.72   # flaps a little narrower than the box's sides, so a hand is four fingers with gaps
            thin = (width, 0.006, f1) if abs(n.y) > 0.5 else (0.006, width, f1)
            kit.box(f"{name}.flapb{sx}.{k}", thin, (0, 0, -f1 / 2), fmat, hg)
            fold = kit.empty(f"{name}.fold{sx}.{k}", (0, 0, -f1), hg)
            thin2 = (width * 0.9, 0.006, f2) if abs(n.y) > 0.5 else (0.006, width * 0.9, f2)
            kit.box(f"{name}.flapt{sx}.{k}", thin2, (0, 0, -f2 / 2), fmat, fold)
            flaps.append((hg, fold, n))
        P[f"shoulder{sx}"], P[f"elbow{sx}"], P[f"wrist{sx}"] = sh, el, wr
        cr[f"flaps{sx}"] = flaps
    ctx[name] = cr
    return cr


def set_face(cr, kind, wd: Path, flip=False, mirror=False):
    """Swap the marker drawing on the face box (the same box, the same marker, a new drawing). flip turns the
    drawing 180 degrees on the box, for a pose where the box hangs upside down: the drawing reads upright to the
    viewer while the box's dent and flap seam give the hang away on a second look. mirror draws it the other
    way round (the sideways eyes slid the other way)."""
    key = (kind, bool(flip), bool(mirror))
    if cr.get("face") == key:
        return
    if kind not in FACES:
        raise ValueError(f"the Boxes' face {kind!r} isn't one of {FACES}")
    hw, hd, hh = DIM["head"]
    fw_, sw_, h_ = int(hw * PX_PER_M), int(hd * PX_PER_M), int(hh * PX_PER_M)
    imgs = cr["images"].setdefault(key, {})
    if not imgs:
        tag = kind + ("-flip" if flip else "") + ("-mirror" if mirror else "")
        turn0 = (lambda im: im.rotate(180)) if flip else (lambda im: im)
        turn = (lambda im: turn0(im).transpose(Image.FLIP_LEFT_RIGHT)) if mirror else turn0
        imgs["front"] = pil_image(f"boxes-{tag}-front", turn(marker.face(kind, fw_, h_)), wd / f"boxes-{tag}-front.png")
        for slot, side in (("left", 1), ("right", -1)):
            imgs[slot] = pil_image(f"boxes-{tag}-{slot}", turn(marker.face_side(kind, sw_, h_, side=side, front_w=fw_)),
                                   wd / f"boxes-{tag}-{slot}.png")
    for slot, node in cr["face_slots"].items():
        if slot in imgs:
            node.image = imgs[slot]
    if "ink_rough" in cr["face_slots"]:
        cr["face_slots"]["ink_rough"].outputs[0].default_value = 0.12 if kind in GLOSSY else 0.8
    cr["face"] = key


def eye_line(cr, flip=False):
    """The world point between the drawn eyes on the face box's front (the eyes sit at about 0.23 of the drawing
    from its top), for aiming the face's light."""
    hw, hd, hh = DIM["head"]
    v_top = 0.23
    z = (v_top if flip else 1 - v_top) * hh - hh / 2
    return cr["head"].matrix_world @ V((0.0, -hd / 2, z))


def _rot(deg3):
    return tuple(math.radians(a) for a in deg3)


def _frame(z_axis, x_ref, origin):
    z = z_axis.normalized()
    x = (x_ref - x_ref.dot(z) * z).normalized()
    y = z.cross(x)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = origin
    return m


def _reach(cr, sx, target, pole):
    """Two-bone IK: the shoulder and elbow turn so the wrist is at target, the elbow bending toward pole."""
    P = cr["pivots"]
    sh, el = P[f"shoulder{sx}"], P[f"elbow{sx}"]
    bpy.context.view_layer.update()
    S = sh.matrix_world.translation.copy()
    T = V(target)
    side = P["root"].matrix_world.to_3x3() @ V((1, 0, 0))
    d = T - S
    dist = min(max(d.length, 0.25), (L_UPPER + L_FORE) * 0.999)
    u = d.normalized()
    ca = (L_UPPER ** 2 + dist ** 2 - L_FORE ** 2) / (2 * L_UPPER * dist)
    a = math.acos(max(-1.0, min(1.0, ca)))
    p = P["root"].matrix_world.to_3x3() @ V(pole)
    p = (p - p.dot(u) * u).normalized()
    E = S + L_UPPER * (math.cos(a) * u + math.sin(a) * p)
    W = S + dist * u
    sh.matrix_world = _frame(-(E - S), side, S)
    bpy.context.view_layer.update()
    el.matrix_world = _frame(-(W - E), side, E)


def _face_frame(face_dir, up_hint, roll_deg, origin):
    """A face box frame: its drawn front (local -y) looks along face_dir; its local z (the top of the drawing,
    and the way the box runs out from its joint) is as near up_hint as it can be, then turned by roll about the
    face's axis."""
    y = -V(face_dir).normalized()
    u = V(up_hint)
    z = (u - u.dot(y) * y)
    if z.length < 1e-6:
        z = V((0, 0, 1)) - V((0, 0, 1)).dot(y) * y
    z.normalize()
    x = y.cross(z)
    m = Matrix((x, y, z)).transposed() @ Matrix.Rotation(math.radians(roll_deg), 3, "Y")
    mw = m.to_4x4()
    mw.translation = origin
    return mw


def _chain(cr, pose):
    """Lay the neck chain along the ceiling toward pose["chain"]["to"]: N1 climbs from the chest to the
    ceiling, the rest lie flat against it, and the face box hangs from the last one's end. With fewer neck
    boxes the chain is shorter; with none the face box sits on the chest (pose["head"])."""
    P = cr["pivots"]
    n = int(pose.get("neck", 0))
    for k, (pv, ob) in enumerate(cr["neck"]):
        for o in [ob] + [c for c in pv.children if c.name.startswith(f"{cr['name']}.jt.n")]:
            o.hide_render = k >= n
            for cc in o.children_recursive:
                cc.hide_render = k >= n
    bpy.context.view_layer.update()
    C = P["n1"].matrix_world.translation.copy()
    side = P["spine2"].matrix_world.to_3x3() @ V((1, 0, 0))
    if n == 0:
        P["head"].matrix_world = P["n1"].matrix_world.copy()
        bpy.context.view_layer.update()
        return
    tx, ty = pose["chain"]["to"]
    a = V((tx - C.x, ty - C.y, 0.0))
    a = a.normalized() if a.length > 1e-6 else V((0, -1, 0))
    zc = PC["h"] - DIM["neck"][1] / 2 - 0.05           # a neck box's centre line, flat under the ceiling (its sag clear)
    P_ = C
    for k in range(n):
        pv = P[f"n{k + 1}"]
        zt = zc
        for _ in range(5 if k == 0 else 1):
            if k == 0:
                e = math.asin(max(-1.0, min(1.0, (zt - C.z) / L_NECK)))
                d = V((a.x * math.cos(e), a.y * math.cos(e), math.sin(e)))
            else:
                d = a.copy()
            # the box's thin side (local y) against the ceiling: local -y points down
            x_ref = d.cross(V((0, 0, 1))) if abs(d.z) < 0.99 else side
            pv.matrix_world = _frame(d, x_ref, P_)
            bpy.context.view_layer.update()
            if k:
                break
            # N1 climbs at a slant, so a corner of it rises above its centre line: lower the climb till it's clear
            ob = cr["neck"][0][1]
            top = max((ob.matrix_world @ v.co).z for v in ob.data.vertices)
            if top <= PC["h"] - 0.002:
                break
            zt -= top - (PC["h"] - 0.002) + 0.002
        P_ = P_ + d * L_NECK
    # the face box hangs from the chain's end: it runs down from the joint (its local z, the top of the drawing,
    # points away from the joint), so a face aimed down hangs upside down
    f = pose.get("face", {"dir": [0, -1, -1], "roll": 0})
    hang = V((0, 0, -1)) - a * float(pose["chain"].get("drop", 0.35))
    if f.get("ext"):   # the way the face box runs out from the chain's end, given (the top of its drawing)
        hang = V(f["ext"])
    P["head"].matrix_world = _face_frame(f["dir"], hang, f.get("roll", 0), P_)
    bpy.context.view_layer.update()
    # a tipped box is taller than it is thick: let it hang just clear of the ceiling (the joint's gap opens a little)
    hm = cr["head"].matrix_world
    over = max((hm @ v.co).z for v in cr["head"].data.vertices) - (PC["h"] - 0.012)
    if over > 0:
        P["head"].matrix_world = Matrix.Translation((0, 0, -over)) @ P["head"].matrix_world
        bpy.context.view_layer.update()


def pose_boxes(cr, pose):
    """Put the Boxes in a pose (POSES): only its joints turn. Its feet are set down on the floor; with "press"
    its legs fold until the torso is under the ceiling; with "land" the whole figure moves so the face box
    hangs over that point."""
    P = cr["pivots"]
    root = P["root"]
    hd = pose.get("head", [0, 0, 0])
    at = list(pose["at"])

    def body(crouch):
        root.location = (at[0], at[1], 0.0)
        root.rotation_euler = (0, 0, math.radians(pose.get("yaw", 0)))
        for k, sx in enumerate((-1, 1)):
            fwd, out = pose.get("hip", [[0, 0], [0, 0]])[k]
            P[f"hip{sx}"].rotation_euler = (math.radians(-fwd - crouch), math.radians(-out * sx), 0)
            P[f"knee{sx}"].rotation_euler = (math.radians(pose.get("knee", [0, 0])[k] + 2 * crouch), 0, 0)
        for j in ("waist", "spine1", "spine2"):
            f, s_, tw = pose.get(j, [0, 0, 0])
            P[j].rotation_euler = _rot((f, s_, tw))
        if pose.get("neck", 0) == 0 and not isinstance(hd, dict):
            P["n1"].rotation_euler = _rot(hd)
        bpy.context.view_layer.update()
        if pose.get("neck", 0) == 0:   # the face box sits on the chest: put it there before measuring
            P["head"].matrix_world = P["n1"].matrix_world.copy()
            bpy.context.view_layer.update()
        lo = min(min((ob.matrix_world @ v.co).z for v in ob.data.vertices) for ob in cr["meshes"] if ".shin" in ob.name)
        root.location.z -= lo
        bpy.context.view_layer.update()
        torso = [ob for ob in cr["meshes"] if any(k in ob.name for k in (".pelvis", ".belly", ".chest"))]
        if pose.get("neck", 0) == 0:
            torso.append(cr["head"])
        top = max(max((ob.matrix_world @ v.co).z for v in ob.data.vertices) for ob in torso)
        if pose.get("clear_n1"):   # room under the ceiling for N1's own thickness where it leaves the chest
            top = max(top, P["n1"].matrix_world.translation.z + DIM["neck"][1] / 2 + 0.03)
        return top

    def whole():
        crouch = 0.0
        if pose.get("press") and body(0.0) > PC["h"] - 0.012:
            a, b = 0.0, 55.0
            for _ in range(14):
                crouch = (a + b) / 2
                if body(crouch) > PC["h"] - 0.012:
                    a = crouch
                else:
                    b = crouch
            crouch = b
        body(crouch)
        cr["crouch"] = crouch
        _chain(cr, pose)

    whole()
    if pose.get("land") and pose.get("neck", 0):
        for _ in range(6):   # move the figure so the face box hangs over the point (the pose is the same)
            hc = cr["head"].matrix_world.translation
            at[0] += pose["land"][0] - hc.x
            at[1] += pose["land"][1] - hc.y
            whole()
    cr["at"] = tuple(at)
    for sx in (-1, 1):
        key = str(sx)
        if key in pose.get("hands", {}):
            _reach(cr, sx, pose["hands"][key], pose.get("pole", {}).get(key, [sx, 0.5, 0.3]))
        elif "hang" in pose:   # hanging straight down at its sides, whatever the stoop: each wrist under its shoulder
            h = pose["hang"]
            bpy.context.view_layer.update()
            S = P[f"shoulder{sx}"].matrix_world.translation.copy()
            off = root.matrix_world.to_3x3() @ V((sx * h.get("out", 0.06), -h.get("fwd", 0.04), 0.0))
            _reach(cr, sx, S + off - V((0, 0, h.get("reach", 0.94) * (L_UPPER + L_FORE))), h.get("pole", [0, 1, 0]))
        else:
            fwd, out, elb = pose.get("arm", {}).get(key, [0, 0, 0])
            P[f"shoulder{sx}"].rotation_euler = (math.radians(-fwd), math.radians(-out * sx), 0)
            P[f"elbow{sx}"].rotation_euler = (math.radians(-elb), 0, 0)
        # the hand turned on its wrist (about the forearm), so its flaps meet the camera broadside, not edge-on
        P[f"wrist{sx}"].rotation_euler = (0, 0, math.radians(pose.get("wrist_roll", {}).get(key, 0)))
        spl = pose.get("flaps", {}).get(key, [10, 10, 10, 10])
        curl = math.radians(pose.get("curl", 20))
        for (hg, fold, n), a in zip(cr[f"flaps{sx}"], spl):
            axis = V((0, 0, -1)).cross(n)
            hg.rotation_euler = Matrix.Rotation(math.radians(a), 3, axis).to_euler()
            fold.rotation_euler = Matrix.Rotation(-(curl + math.radians(a) * 0.6), 3, axis).to_euler()
    bpy.context.view_layer.update()


def boxes_extent(cr):
    """(lowest z, highest z, face box centre, its lowest z) of the posed Boxes, for checking the ceiling and the
    air under the face box."""
    zs = []
    for ob in cr["meshes"]:
        if ob.hide_render:
            continue
        mw = ob.matrix_world
        zs += [(mw @ v.co).z for v in ob.data.vertices]
    hm = cr["head"].matrix_world
    hz = min((hm @ v.co).z for v in cr["head"].data.vertices)
    return min(zs), max(zs), tuple(round(c, 3) for c in hm.translation), hz


def light_only(kit, coll, light_name, objs):
    """Light linking: this light lights only these objects."""
    col = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = "INCLUDE"
    kit.LIGHTS[light_name]["obj"].light_linking.receiver_collection = col


def no_shadow(kit, coll, light_name, objs):
    """Shadow linking: these objects cast no shadow from this light."""
    col = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = "EXCLUDE"
    kit.LIGHTS[light_name]["obj"].light_linking.blocker_collection = col


def light_except(kit, coll, light_name, objs):
    """Light linking: this light lights everything but these objects."""
    col = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = "EXCLUDE"
    kit.LIGHTS[light_name]["obj"].light_linking.receiver_collection = col


# ------------------------------------------------------------------------------------------------ the house

_T = WALL_T
WALLS = [  # name, the axis it runs along, where it stands across that axis, from, to, openings (a, b, z0, z1)
    ("w hall n", "x", -_T / 2, -4.6 - _T, X1 + _T, [(*MY_DOOR, 0, DOOR_H), (*DOOR_X, 0, DOOR_H)]),
    ("w hall s", "x", -1.42 - _T / 2, -4.6 - _T, 2.0 + _T, [(*FRONT_DOOR_H, 0, DOOR_H), (*KITCHEN_DOOR, 0, DOOR_H)]),
    ("w back", "x", Y1 + _T / 2, -4.6 - _T, X1 + _T, [MY_WIN]),
    ("w mid", "y", X0 - _T / 2, -_T, Y1 + _T, []),
    ("w west", "y", -4.6 - _T / 2, -5.1 - _T, Y1 + _T, []),
    ("w mum e", "y", X1 + _T / 2, 0.0, Y1 + _T, [(*WIN_Y, *WIN_Z)]),
    ("w hall e", "y", X1 + _T / 2, -1.42 - _T, 0.0, [(*CUP_Y, 0, DOOR_H)]),
    ("w front s", "x", -5.1 - _T / 2, -4.6 - _T, -0.6 + _T, [(*STREET_DOOR, 0, DOOR_H)]),
    ("w front e", "y", -0.6 + _T / 2, -5.1 - _T, -1.42 - _T, [FRONT_WIN]),
    ("w kit s", "x", -3.9 - _T / 2, -0.6 + _T, 2.0 + _T, [KIT_WIN]),
    ("w kit e", "y", 2.0 + _T / 2, -3.9 - _T, -1.42 - _T, []),
    ("w cup back", "y", CUPBOARD[1] + _T / 2, CUP_Y[0] - _T, CUP_Y[1] + _T, []),
    ("w cup s", "x", CUP_Y[0] - _T / 2, X1 + _T, CUPBOARD[1], []),
    ("w cup n", "x", CUP_Y[1] + _T / 2, X1 + _T, CUPBOARD[1], []),
]
WINDOWS = {  # name: (centre on the wall's inside face, the way into the room, (width, height))
    "mum": ((X1, (WIN_Y[0] + WIN_Y[1]) / 2, (WIN_Z[0] + WIN_Z[1]) / 2), (-1, 0, 0),
            (WIN_Y[1] - WIN_Y[0], WIN_Z[1] - WIN_Z[0])),
    "mine": (((MY_WIN[0] + MY_WIN[1]) / 2, Y1, (MY_WIN[2] + MY_WIN[3]) / 2), (0, -1, 0),
             (MY_WIN[1] - MY_WIN[0], MY_WIN[3] - MY_WIN[2])),
    "front": ((FRONT[1], (FRONT_WIN[0] + FRONT_WIN[1]) / 2, (FRONT_WIN[2] + FRONT_WIN[3]) / 2), (-1, 0, 0),
              (FRONT_WIN[1] - FRONT_WIN[0], FRONT_WIN[3] - FRONT_WIN[2])),
    "kitchen": (((KIT_WIN[0] + KIT_WIN[1]) / 2, KITCHEN[2], (KIT_WIN[2] + KIT_WIN[3]) / 2), (0, 1, 0),
                (KIT_WIN[1] - KIT_WIN[0], KIT_WIN[3] - KIT_WIN[2])),
}
ROOMS = {"mum": MUMS, "mine": MINE, "hall": HALL, "front": FRONT, "kitchen": KITCHEN, "cupboard": CUPBOARD}


def wall(kit, name, axis, c, a, b, holes, mat, trim=None):
    """A wall along x (at y = c) or along y (at x = c) from a to b, floor to ceiling, with openings cut in it, and
    skirting on both faces wherever it meets the floor (never across a doorway)."""
    n = [0]

    def piece(lo, hi, z0, z1):
        if hi - lo < 1e-4 or z1 - z0 < 1e-4:
            return
        n[0] += 1
        if axis == "x":
            ob = kit.box(f"{name}.{n[0]}", (hi - lo, _T, z1 - z0), ((lo + hi) / 2, c, (z0 + z1) / 2), mat)
        else:
            ob = kit.box(f"{name}.{n[0]}", (_T, hi - lo, z1 - z0), (c, (lo + hi) / 2, (z0 + z1) / 2), mat)
        if abs(z1 - CEIL) < 1e-6:
            TOPS.append((ob, z0))
        if trim is not None and z0 == 0.0:
            for side in (-1, 1):
                off = side * (_T / 2 + 0.01)
                if axis == "x":
                    kit.box(f"skirt {name}.{n[0]}{'ab'[side > 0]}", (hi - lo, 0.02, 0.1), ((lo + hi) / 2, c + off, 0.05), trim)
                else:
                    kit.box(f"skirt {name}.{n[0]}{'ab'[side > 0]}", (0.02, hi - lo, 0.1), (c + off, (lo + hi) / 2, 0.05), trim)

    x = a
    for lo, hi, z0, z1 in sorted(holes):
        piece(x, lo, 0.0, CEIL)
        piece(lo, hi, 0.0, z0)
        piece(lo, hi, z1, CEIL)
        x = hi
    piece(x, b, 0.0, CEIL)


def tube(kit, name, r_out, r_in, h, loc=(0, 0, 0), mat=None, parent=None, rot=(0, 0, 0), n=28, inner=None):
    """A ring or a tube (a tape core): open through the middle, so you see through it. inner: a second material
    for the inside face (the core's darker inside)."""
    verts, faces = [], []
    for r, z in ((r_out, -h / 2), (r_out, h / 2), (r_in, h / 2), (r_in, -h / 2)):
        for i in range(n):
            a = 2 * math.pi * i / n
            verts.append((r * math.cos(a), r * math.sin(a), z))
    for ring in range(4):
        r0, r1 = ring * n, ((ring + 1) % 4) * n
        for i in range(n):
            j = (i + 1) % n
            faces.append((r0 + i, r0 + j, r1 + j, r1 + i))
    ob = kit.mesh_obj(name, verts, faces, mat, parent, loc, rot, smooth=True)
    if inner is not None:
        ob.data.materials.append(inner)
        for k, pl in enumerate(ob.data.polygons):
            if 2 * n <= k < 3 * n:
                pl.material_index = 1
    return ob


def door_panel(kit, ctx, M, name, hinge, closed_dir, open_dir, w, h=DOOR_H - 0.01):
    """A plain painted door on its hinge (x, y): shut along closed_dir, swung to open_dir. animate() turns it
    from the "door" cues ({"door": name, "open": 0..1, "dur": s})."""
    g = kit.empty(f"door {name}", (hinge[0], hinge[1], 0.0))
    a0 = math.atan2(closed_dir[1], closed_dir[0])
    a1 = math.atan2(open_dir[1], open_dir[0])
    pw = w - 0.11                     # clear of the jambs' trim and the wall's skirting
    kit.box(f"door {name}.panel", (pw, 0.035, h - 0.08), (0.055 + pw / 2, 0, (h - 0.08) / 2 + 0.012), M["door"], g,
            bevel=0.006)
    for side in (-1, 1):
        kit.sphere(f"door {name}.knob{side}", 0.026, (0.055 + pw - 0.07, side * 0.042, 1.0), M["metal"], g, seg=12)
    ctx.setdefault("doors", {})[name] = (g, a0, a1)
    g.rotation_euler = (0, 0, a0)
    return g


def photo_image(kind, w=360, h=460):
    """A family photo, drawn here: only me, Mum and the old house from outside (no third person, no number on
    its door). Mum laughing in two of them, a silent plant for L06."""
    from blocky import faces as F
    bgs = {"house": (150, 168, 186), "mum": (178, 164, 140), "us": (160, 176, 150), "me": (172, 156, 150),
           "garden": (128, 150, 108), "mum2": (190, 170, 150)}
    im = Image.new("RGB", (w, h), bgs.get(kind, (170, 160, 150)))
    d = ImageDraw.Draw(im)
    if kind == "house":   # the old house, plainly tall, with tall windows and a door with no number
        d.rectangle([w * 0.2, h * 0.14, w * 0.8, h * 0.92], fill=(156, 98, 76))
        d.polygon([(w * 0.13, h * 0.16), (w * 0.5, h * 0.03), (w * 0.87, h * 0.16)], fill=(70, 64, 66))
        for row in range(3):
            for col in range(2):
                x0, y0 = w * (0.28 + col * 0.27), h * (0.2 + row * 0.2)
                d.rectangle([x0, y0, x0 + w * 0.17, y0 + h * 0.16], fill=(226, 232, 236))
                d.line([x0 + w * 0.085, y0, x0 + w * 0.085, y0 + h * 0.16], fill=(120, 110, 100), width=3)
        d.rectangle([w * 0.43, h * 0.78, w * 0.57, h * 0.92], fill=(60, 52, 64))
        d.rectangle([0, h * 0.92, w, h], fill=(96, 112, 84))
        return im.filter(ImageFilter.SMOOTH)
    people = {"mum": ["mum"], "mum2": ["mum"], "me": ["me"], "us": ["mum", "me"], "garden": ["mum"]}[kind]
    skins = {"mum": "#a86a58", "me": "#87503f"}
    shirts = {"mum": (108, 124, 151), "me": (63, 90, 80)}
    hairs = {"mum": (90, 74, 66), "me": (20, 18, 19)}
    n = len(people)
    for k, who in enumerate(people):
        cx = w * (0.5 if n == 1 else 0.3 + 0.4 * k)
        s = w * (0.52 if n == 1 else 0.36)
        d.rectangle([cx - s * 0.62, h * 0.64, cx + s * 0.62, h], fill=shirts[who])
        expr = "grin" if who == "mum" else "soft"
        tex = F.face_image({"eyes": "round", "brows": True}, skins[who], expr)
        crop = tex.crop((F.FX0 - 40, F.FY0, F.FX1 + 40, F.FY1)).resize((int(s), int(s * 0.9)))
        hx, hy = int(cx - s / 2), int(h * 0.64 - s * 0.92)
        d.rectangle([hx - 4, hy - 14, hx + s + 4, hy + s * (0.62 if who == "mum" else 0.22)], fill=hairs[who])
        im.paste(crop, (hx, hy))
    return im.filter(ImageFilter.SMOOTH)


def old_house_image(lit, w=640, h=938):
    """The old house from outside: tall and narrow, high windows, a door with no number. In its top window something
    pale and square-headed is folded under the window's ceiling, with the Boxes' marker frown. lit=False is the
    dim, easy-to-miss version Mum hangs (L08); lit=True is the close one (L41)."""
    from blocky import faces as F
    im = Image.new("RGB", (w, h), (150, 168, 186))
    d = ImageDraw.Draw(im)
    d.rectangle([w * 0.2, h * 0.1, w * 0.8, h * 0.93], fill=(156, 98, 76))
    d.polygon([(w * 0.13, h * 0.12), (w * 0.5, h * 0.015), (w * 0.87, h * 0.12)], fill=(70, 64, 66))
    for row in range(1, 5):
        for col in range(2):
            x0, y0 = w * (0.28 + col * 0.27), h * (0.17 + row * 0.145)
            d.rectangle([x0, y0, x0 + w * 0.17, y0 + h * 0.105], fill=(226, 232, 236))
            d.line([x0 + w * 0.085, y0, x0 + w * 0.085, y0 + h * 0.105], fill=(120, 110, 100), width=4)
    d.rectangle([w * 0.43, h * 0.8, w * 0.57, h * 0.93], fill=(60, 52, 64))
    d.rectangle([0, h * 0.93, w, h], fill=(96, 112, 84))
    # the top window: wider, with something folded in it
    wx0, wy0, wx1, wy1 = w * 0.3, h * 0.14, w * 0.7, h * 0.285
    inner = (232, 236, 238) if lit else (150, 156, 160)
    d.rectangle([wx0 - 6, wy0 - 6, wx1 + 6, wy1 + 6], fill=(120, 110, 100))
    d.rectangle([wx0, wy0, wx1, wy1], fill=inner)
    fig = (214, 210, 200) if lit else (168, 168, 166)
    ink = (22, 18, 20) if lit else (96, 98, 100)
    # folded along the window's ceiling, then the box hanging at its end
    d.rectangle([wx0 + 4, wy0 + 4, wx1 - 70, wy0 + 40], fill=fig)
    d.rectangle([wx1 - 140, wy0 + 4, wx1 - 6, wy1 - 8], fill=fig)
    fx0, fy0, fx1, fy1 = wx1 - 130, wy0 + 40, wx1 - 16, wy1 - 12
    lw = 7 if lit else 5
    d.line([fx0 + 20, fy0 + 24, fx0 + 40, fy0 + 24], fill=ink, width=lw)
    d.line([fx1 - 40, fy0 + 24, fx1 - 20, fy0 + 24], fill=ink, width=lw)
    d.arc([fx0 + 22, fy0 + 40, fx1 - 22, fy1 + 20], 205, 335, fill=ink, width=lw)
    return im.filter(ImageFilter.SMOOTH)


PHOTOS = ["oldhouse", "mum", "us", "me", "garden", "mum2", "us", "garden"]
PHOTO_SIZE = [(0.30, 0.44), (0.26, 0.33), (0.3, 0.24), (0.24, 0.3), (0.3, 0.24), (0.26, 0.33), (0.24, 0.3), (0.3, 0.24)]
# where each frame hangs on the front room's long west wall (x = -4.6): (y, z) at eye height before L22; then up
# the wall to its very top and on across the ceiling, flat on it, where the old house's taller wall would have
# been ("wall", y, z) or ("ceil", x, y). The big one of the old house goes highest, onto the ceiling
PHOTO_LOW = [(-3.0, 1.45), (-3.62, 1.58), (-3.3, 1.2), (-4.05, 1.55), (-2.36, 1.48), (-1.98, 1.57), (-3.9, 1.1),
             (-2.5, 1.12)]
PHOTO_UP = [("wall", -4.05, 2.12), ("wall", -3.55, 2.1), ("wall", -3.05, 2.13), ("wall", -2.55, 2.1),
            ("ceil", -4.32, -3.85), ("ceil", -4.3, -3.2), ("ceil", -4.32, -2.55), ("ceil", -3.82, -3.25)]


def build_house(kit, ctx, M):
    """The rooms: a floor and a ceiling each, the walls with their openings, skirting, the windows (a painted
    frame, a sill, the outside beyond), Mum's curtains, bare bulbs, the doors, the cupboard's shelf, the coat
    hooks. No text anywhere."""
    for tag, (x0, x1, y0, y1) in ROOMS.items():
        size = (x1 - x0 + _T, y1 - y0 + _T)
        c = ((x0 + x1) / 2, (y0 + y1) / 2)
        kit.box(f"floor {tag}", (*size, 0.1), (*c, -0.05), M["floor"])
        CEILS.append((kit.box(f"ceiling {tag}", (*size, 0.12), (*c, CEIL + 0.06), M["ceiling"]), CEIL + 0.06))
    for nm, axis, c, a, b, holes in WALLS:
        wall(kit, nm, axis, c, a, b, holes, M["wall"], None if nm.startswith("w cup") else M["trim"])
    # the windows: a painted frame with one upright, a sill (the front room's is deep), the outside beyond (one
    # plane each, its glow set by the time of day: animate), and Mum's curtains, the only ones in the house
    for nm, (c, n, (ww, wh)) in WINDOWS.items():
        cx, cy, cz = c
        nx, ny, _ = n
        along = (0, 1) if nx else (1, 0)
        deep = 0.3 if nm == "front" else 0.16
        sill_c = (cx + nx * deep / 2, cy + ny * deep / 2, cz - wh / 2 - 0.0175)
        kit.box(f"win {nm} sill", (deep if nx else ww + 0.12, ww + 0.12 if nx else deep, 0.035), sill_c, M["trim"])
        for k, (du, dz, su, sz) in enumerate(((-ww / 2 + 0.025, 0, 0.05, wh), (ww / 2 - 0.025, 0, 0.05, wh),
                                               (0, wh / 2 - 0.025, ww, 0.05), (0, -wh / 2 + 0.025, ww, 0.05),
                                               (0, 0, 0.04, wh))):
            lc = (cx - nx * 0.03 + along[0] * du, cy - ny * 0.03 + along[1] * du, cz + dz)
            size = (0.06, su, sz) if nx else (su, 0.06, sz)
            kit.box(f"win {nm} frame{k}", size, lc, M["trim"])
        # (the front room's is small and close: the kitchen is just beyond that corner)
        far, size = (0.35, (1.6, 1.05)) if nm == "front" else (1.2, (3.0, 3.0))
        out = kit.plane(f"outside {nm}", size, (cx - nx * far, cy - ny * far, cz), M["outside"],
                        rot=(math.radians(90), 0, 0) if ny else (0, math.radians(90), 0))
        for k in ("visible_shadow", "visible_diffuse", "visible_glossy"):
            setattr(out, k, False)
    wa, wb = WIN_Y
    za, zb = WIN_Z
    kit.cyl("rod", 0.012, wb - wa + 0.4, (X1 - 0.1, (wa + wb) / 2, zb + 0.12), M["cord"], rot=(math.radians(90), 0, 0))
    for nm, y0_, y1_ in (("curtain a", wa - 0.2, (wa + wb) / 2 - 0.03), ("curtain b", (wa + wb) / 2 + 0.03, wb + 0.2)):
        ob = pleats(kit, nm, y0_, y1_, 0.0, 0.05, zb + 0.11, M["curtain"], period=0.1, amp=0.03)
        ob.rotation_euler = (0, 0, math.radians(90))
        ob.location = (X1 - 0.1, 0, 0)
    # bare pendant bulbs, not fitted yet (a new house): never lit, never swinging
    for k, (bx, by) in enumerate(((0.6, 0.9), (-3.0, 1.3), (-2.1, -0.77), (-2.6, -3.5), (0.9, -2.6))):
        CEILS.append((kit.cyl(f"rose{k}", 0.05, 0.03, (bx, by, CEIL - 0.015), M["trim"]), CEIL - 0.015))
    # the doors: Mum's (open into her room, against the wall by the bed's head), mine, the front door (shut), the
    # hall cupboard's (shut until L75)
    door_panel(kit, ctx, M, "mum", (DOOR_X[0] + 0.01, -0.02), (1, 0), (0, 1), DOOR_X[1] - DOOR_X[0])
    door_panel(kit, ctx, M, "mine", (MY_DOOR[0] + 0.01, -0.02), (1, 0), (0, 1), MY_DOOR[1] - MY_DOOR[0])
    door_panel(kit, ctx, M, "street", (STREET_DOOR[0] + 0.01, FRONT[2] - 0.03), (1, 0), (1, 0),
               STREET_DOOR[1] - STREET_DOOR[0])
    door_panel(kit, ctx, M, "cupboard", (X1 + 0.02, CUP_Y[1] - 0.01), (0, -1), (-1, 0), CUP_Y[1] - CUP_Y[0] - 0.02)
    for nm, (a, b), y in (("mum", DOOR_X, -_T / 2), ("mine", MY_DOOR, -_T / 2), ("front", FRONT_DOOR_H, -1.42 - _T / 2),
                          ("kitchen", KITCHEN_DOOR, -1.42 - _T / 2), ("street", STREET_DOOR, -5.1 - _T / 2)):
        for k, x in enumerate((a, b)):   # painted door frames
            kit.box(f"jamb {nm}{k}", (0.04, _T + 0.03, DOOR_H), (x + (0.02 if k == 0 else -0.02), y, DOOR_H / 2), M["trim"])
        kit.box(f"head {nm}", (b - a, _T + 0.03, 0.05), ((a + b) / 2, y, DOOR_H - 0.025), M["trim"])
    # the pencil mark at my height on my doorframe's hall side (S09, S19): a short line, a little proud of the jamb
    kit.box("pencil mark", (0.04, 0.004, 0.012), (MY_DOOR[1] - 0.02, -_T / 2 - (_T + 0.03) / 2 - 0.003, 1.72),
            kit.plastic("#35353a", 0.8, name="pencil"))
    kit.box("pencil tick", (0.012, 0.004, 0.06), (MY_DOOR[1] - 0.02, -_T / 2 - (_T + 0.03) / 2 - 0.003, 1.70),
            kit.plastic("#35353a", 0.8, name="pencil"))
    for k, y in enumerate(CUP_Y):
        kit.box(f"jamb cupboard{k}", (_T + 0.03, 0.04, DOOR_H), (X1 + _T / 2, y + (0.02 if k == 0 else -0.02), DOOR_H / 2), M["trim"])
    kit.box("head cupboard", (_T + 0.03, CUP_Y[1] - CUP_Y[0], 0.05), (X1 + _T / 2, sum(CUP_Y) / 2, DOOR_H - 0.025), M["trim"])
    # the cupboard's shelf at chest height, and its own dim inside
    x0, x1, y0, y1 = CUPBOARD
    kit.box("shelf", (x1 - x0 - 0.01, y1 - y0 - 0.01, 0.025), ((x0 + x1) / 2, (y0 + y1) / 2, SHELF_Z - 0.0125), M["shelf"])
    # coat hooks by the front door, and the coats that go on them at L73
    kit.box("hook rail", (0.03, 0.62, 0.07), (FRONT[0] + 0.015, FRONT[2] + 0.62, 1.72), M["wood"])
    for k in range(3):
        kit.cyl(f"hook{k}", 0.008, 0.06, (FRONT[0] + 0.05, FRONT[2] + 0.4 + 0.2 * k, 1.71), M["metal"],
                rot=(0, math.radians(90), 0))
    coats = []
    for k, (dy, c_) in enumerate(((0.42, "coat a"), (0.66, "coat b"))):
        coats.append(kit.box(f"coat{k}", (0.1, 0.34, 0.82), (FRONT[0] + 0.08, FRONT[2] + dy + 0.02, 1.28), M[c_], bevel=0.035))
    ctx["coats"] = coats


def build_kitchen(kit, ctx, M):
    c = COUNTER
    y0, y1 = c["y0"], c["y0"] + c["d"]
    kit.box("cabinets", (c["x1"] - c["x0"], c["d"] - 0.04, c["z"] - 0.04), ((c["x0"] + c["x1"]) / 2, (y0 + y1) / 2 - 0.02,
            (c["z"] - 0.04) / 2), M["cabinet"], bevel=0.006)
    for k in range(4):   # cupboard-door seams
        x = c["x0"] + (k + 1) * (c["x1"] - c["x0"]) / 5
        kit.box(f"cabinet seam{k}", (0.006, 0.004, c["z"] - 0.14), (x, y1 - 0.04, (c["z"] - 0.04) / 2), M["cord"])
    kit.box("worktop", (c["x1"] - c["x0"], c["d"], 0.04), ((c["x0"] + c["x1"]) / 2, (y0 + y1) / 2, c["z"] - 0.02),
            M["worktop"], bevel=0.004)
    kit.box("sink", (0.5, 0.36, 0.012), (SINK_X, y0 + 0.3, c["z"] + 0.001), M["metal"])
    kit.cyl("tap", 0.014, 0.25, (SINK_X, y0 + 0.08, c["z"] + 0.12), M["metal"])
    kit.box("tap spout", (0.028, 0.14, 0.028), (SINK_X, y0 + 0.14, c["z"] + 0.24), M["metal"])
    # the fridge (no logo), in the corner by the door
    kit.box("fridge", (0.62, 0.62, 1.7), (KITCHEN[0] + 0.32, y0 + 0.32, 0.85), M["fridge"], bevel=0.03)
    kit.box("fridge seam", (0.6, 0.006, 0.008), (KITCHEN[0] + 0.32, y0 + 0.633, 1.15), M["cord"])
    kit.box("fridge handle", (0.03, 0.03, 0.4), (KITCHEN[0] + 0.56, y0 + 0.645, 1.3), M["metal"])
    # the kettle, to the sink's right until L73, then on its left (no logo)
    g = kit.empty("kettle", (*KETTLE["right"], c["z"]))
    kit.cyl("kettle.body", 0.085, 0.2, (0, 0, 0.1), M["kettle"], g, r2=0.068)
    kit.cyl("kettle.lid", 0.04, 0.02, (0, 0, 0.205), M["cord"], g)
    kit.box("kettle.handle", (0.03, 0.035, 0.17), (0, 0.095, 0.12), M["cord"], g)
    kit.box("kettle.spout", (0.025, 0.08, 0.03), (0, -0.1, 0.14), M["kettle"], g, rot=(math.radians(-30), 0, 0))
    ctx["kettle"] = g
    # five rolls of packing tape lying flat in a loose heap at the far end (morning 2), then the same five as bare
    # cores standing on their edges in one even row in the same spot (morning 3 and 4), then gone (from L62)
    rolls, cores = [], []
    heap = [(-0.07, 0.03, 0, 6, 0), (0.06, 0.05, 0, -5, 0), (0.0, -0.08, 0, 4, 0), (-0.02, 0.01, 0.05, 14, 1),
            (0.05, -0.04, 0.052, -12, 1)]
    for k, (dx, dy, dz, tilt, lvl) in enumerate(heap):
        gx = kit.empty(f"roll{k}", (ROLLS_AT[0] + dx, ROLLS_AT[1] + dy, c["z"] + 0.024 + dz),
                       rot=(math.radians(tilt), math.radians(tilt * 0.6), math.radians(k * 41)))
        tube(kit, f"roll{k}.tape", 0.062, 0.04, 0.048, (0, 0, 0), M["tape"], gx)
        tube(kit, f"roll{k}.core", 0.0405, 0.036, 0.05, (0, 0, 0), M["core"], gx, inner=M["coreinside"])
        rolls.append(gx)
    for k in range(5):
        cx = kit.empty(f"core{k}", (ROLLS_AT[0] - 0.22 + k * 0.105, ROLLS_AT[1] + 0.06, c["z"] + 0.0405),
                       rot=(math.radians(90), 0, 0))
        tube(kit, f"core{k}.ring", 0.0405, 0.036, 0.05, (0, 0, 0), M["core"], cx, inner=M["coreinside"])
        cores.append(cx)
    ctx["rolls"], ctx["cores"] = rolls, cores


# ------------------------------------------------------------------------------------------------ the montage
# L01 to L04 (S02 to S06): a bright street, a lodger's house, a living room and a dining room, far from the house
# (x 60, 100 and 140), lit by their own lights (the "street" time set: one exposure for all of them, so nothing
# strobes between shots). Nobody here is in peril; they are adults who each have one bit of business with a ceiling.
OS = (60.0, 0.0)       # the street
O5 = (100.0, 0.0)      # the living room (the lowered ceiling)
O6 = (140.0, 0.0)      # the dining room (the dome)
YF = 6.0               # the houses' front wall, as y from the street's origin
HOUSES = [  # name, x, width, height, door_w, door_h, body, roof, rows, door colour
    ("a", -6.8, 3.0, 3.2, 0.95, 1.68, "#ff7a59", "#6b3fa0", 1, "#2d5fd0"),
    ("b", -3.3, 3.2, 4.6, 1.05, 2.22, "#3fb6e8", "#f2c230", 2, "#d83a52"),
    ("c", 0.0, 3.0, 3.8, 0.98, 1.86, "#7ccf5a", "#d4483b", 1, "#7a4cc2"),
    ("d", 3.2, 2.4, 8.5, 1.1, 2.86, "#f4d03f", "#2c6fdb", 5, "#d8501f"),
    ("e", 10.0, 3.4, 4.2, 1.1, 1.95, "#ef6fb0", "#2f9e8f", 1, "#1f1b24"),
    ("f", 16.0, 3.4, 2.1, 0.9, 1.78, "#e6dfca", "#6a6f78", 1, "#59616d"),   # the small new house, no number on its door
]


def _unfogged_emit(kit, name, hexc, strength):
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = strength
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    return m


def build_street(kit, ctx, M):
    ox, oy = OS
    pm = lambda hexc, r=0.55: kit.plastic(hexc, r, name=f"st {hexc} {r}")
    kit.box("st ground", (80, 40, 0.2), (ox, oy + 8, -0.1), pm("#8d96a3", 0.8))
    kit.box("st road", (80, 5.0, 0.02), (ox, oy + 1.0, 0.001), pm("#59616d", 0.85))
    kit.box("st pavement", (80, 2.6, 0.02), (ox, oy + 4.2, 0.01), pm("#d0cbbd", 0.8))
    kit.plane("st sky", (240, 90), (ox, oy + 55, 25), _unfogged_emit(kit, "st sky", "#cfe2f4", 1.3), rot=(math.radians(90), 0, 0))
    for nm, x, w, h, dw, dh, body, roof, rows, dc in HOUSES:
        cx = ox + x
        yf = oy + YF
        depth = 4.0
        mb, mw_ = pm(body), kit.glass("#bfe8ff", name="st glass")
        if nm == "e":   # the lodger's house: the door stands open on a dark hall
            kit.box(f"st {nm} left", ((w - dw) / 2, depth, h), (cx - (w + dw) / 4, yf + depth / 2, h / 2), mb)
            kit.box(f"st {nm} right", ((w - dw) / 2, depth, h), (cx + (w + dw) / 4, yf + depth / 2, h / 2), mb)
            kit.box(f"st {nm} over", (dw, depth, h - dh), (cx, yf + depth / 2, dh + (h - dh) / 2), mb)
            kit.box(f"st {nm} hall", (dw + 0.02, 0.05, dh), (cx, yf + 1.4, dh / 2), pm("#2a2430", 0.9))
            kit.box(f"st {nm} hall floor", (dw, 1.4, 0.02), (cx, yf + 0.7, 0.012), pm("#6d5a62", 0.8))
            kit.box(f"st {nm} door", (0.04, 0.8, dh - 0.05), (cx + dw / 2 - 0.02, yf - 0.4, dh / 2), pm(dc), rot=(0, 0, math.radians(-70)))
        else:
            kit.box(f"st {nm} body", (w, depth, h), (cx, yf + depth / 2, h / 2), mb)
            kit.box(f"st {nm} door", (dw, 0.05, dh), (cx, yf - 0.02, dh / 2), pm(dc))
        kit.box(f"st {nm} frame", (dw + 0.16, 0.04, dh + 0.1), (cx, yf - 0.008, (dh + 0.1) / 2), pm("#f4f1e8"))
        kit.box(f"st {nm} roof", (w + 0.4, depth + 0.4, 0.3), (cx, yf + depth / 2, h + 0.15), pm(roof))
        if nm != "e":
            kit.box(f"st {nm} step", (dw + 0.5, 0.5, 0.08), (cx, yf - 0.3, 0.04), pm("#e5e1d6"))
        for r in range(rows):
            z = dh + 0.55 + r * ((h - dh - 1.0) / max(1, rows)) if rows > 1 else dh + 0.5
            if nm == "f":
                z = 1.1
            elif z + 0.5 > h:
                continue
            for dx in (-1, 1):
                if abs(dx) * w * 0.25 < dw * 0.3 and rows == 1:
                    pass
                kit.box(f"st {nm} win{r}{dx}", (0.5, 0.03, 0.62), (cx + dx * w * 0.27, yf - 0.018, z), mw_)
                kit.box(f"st {nm} win{r}{dx}f", (0.58, 0.02, 0.7), (cx + dx * w * 0.27, yf - 0.008, z), pm("#f4f1e8"))
    # the suitcase the lodger carries (placed by animate)
    ctx["suitcase"] = kit.box("suitcase", (0.5, 0.16, 0.36), (0, 0, -5), pm("#e0942a"), bevel=0.02)
    kit.box("suitcase band", (0.52, 0.17, 0.05), (0, 0, 0), pm("#2b2a33"), ctx["suitcase"])
    # the street's light: a soft overcast sun and a lift from the road
    sun = kit.light("street sun", "SUN", (ox, oy - 8, 14), 3.0, "#f4f6ff", rot=(math.radians(55), 0, math.radians(8)))
    sun.data.angle = math.radians(18)
    # ---- the living room (S05): a lowered ceiling and a pale line where it used to be
    px, py = O5
    pr = lambda hexc, r=0.7: kit.plastic(hexc, r, name=f"rm {hexc} {r}")
    kit.box("lr floor", (4.0, 3.6, 0.1), (px, py + 1.6, -0.05), pr("#b98a5a", 0.5))
    kit.box("lr back", (4.0, 0.1, 2.9), (px, py + 3.45, 1.45), pr("#f0d9a8"))
    kit.box("lr left", (0.1, 3.6, 2.9), (px - 2.0, py + 1.6, 1.45), pr("#f0d9a8"))
    kit.box("lr right", (0.1, 3.6, 2.9), (px + 2.0, py + 1.6, 1.45), pr("#f0d9a8"))
    kit.box("lr ceiling", (4.0, 3.6, 0.1), (px, py + 1.6, 2.17), pr("#f7f2e6"))
    kit.plane("lr line", (3.9, 0.07), (px, py + 3.39, 2.06), pr("#fff9ea"), rot=(math.radians(-90), 0, 0))
    for sgn in (-1, 1):
        kit.plane(f"lr line{sgn}", (3.4, 0.07), (px + sgn * 1.94, py + 1.7, 2.06), pr("#fff9ea"),
                  rot=(math.radians(90), 0, math.radians(90 * sgn)))
    kit.box("sofa seat", (1.8, 0.8, 0.42), (px, py + 2.6, 0.21), pr("#1f9d8a", 0.8), bevel=0.05)
    kit.box("sofa back", (1.8, 0.2, 0.8), (px, py + 3.0, 0.62), pr("#188574", 0.8), bevel=0.05)
    for sx in (-1, 1):
        kit.box(f"sofa arm{sx}", (0.2, 0.8, 0.6), (px + sx * 0.9, py + 2.6, 0.3), pr("#188574", 0.8), bevel=0.05)
    kit.box("lr rug", (2.6, 1.8, 0.015), (px, py + 1.2, 0.008), pr("#e0584a", 0.9))
    up = kit.light("lr up", "AREA", (px, py + 1.4, 0.3), 120.0, "#fff1d6", size=2.4, rot=(math.pi, 0, 0))
    kit.light("lr lamp", "AREA", (px, py + 1.0, 1.95), 220.0, "#fff1d6", size=2.4)
    # ---- the dining room (S06): a ceiling that bulges up over the tall hat
    qx, qy = O6
    pd = lambda hexc, r=0.7: kit.plastic(hexc, r, name=f"dr {hexc} {r}")
    kit.box("dr floor", (4.4, 3.6, 0.1), (qx, qy + 1.6, -0.05), pd("#c8a070", 0.5))
    kit.box("dr back", (4.4, 0.1, 3.4), (qx, qy + 3.45, 1.7), pd("#a8d0f0"))
    kit.box("dr left", (0.1, 3.6, 3.4), (qx - 2.2, qy + 1.6, 1.7), pd("#a8d0f0"))
    kit.box("dr right", (0.1, 3.6, 3.4), (qx + 2.2, qy + 1.6, 1.7), pd("#a8d0f0"))
    nx, ny = 44, 36
    verts, faces = [], []
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = -2.2 + 4.4 * i / nx
            y = -0.05 + 3.5 * j / ny
            bump = 0.62 * math.exp(-(((x - 0.95) / 0.62) ** 2 + ((y - 1.9) / 0.62) ** 2))
            verts.append((qx + x, qy + y, 2.45 + bump))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    kit.mesh_obj("dr ceiling", verts, faces, pd("#fdf6e8"), smooth=True)
    kit.box("dr table", (2.2, 0.95, 0.06), (qx, qy + 1.9, 0.76), pd("#8a4f2b", 0.5), bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"dr leg{sx}{sy}", (0.07, 0.07, 0.73), (qx + sx * 1.0, qy + 1.9 + sy * 0.4, 0.365), pd("#6a3a1e", 0.5))
    for sx in (-1, 1):
        kit.box(f"dr chair{sx}", (0.5, 0.5, 0.05), (qx + sx * 1.0, qy + 1.9, 0.43), pd("#d8503f", 0.6))
        kit.box(f"dr chairback{sx}", (0.05, 0.5, 0.5), (qx + sx * 1.27, qy + 1.9, 0.7), pd("#d8503f", 0.6))
        kit.cyl(f"dr plate{sx}", 0.14, 0.015, (qx + sx * 0.55, qy + 1.9, 0.795), pd("#f4f1e8", 0.3))
    kit.light("dr up", "AREA", (qx, qy + 1.4, 0.3), 150.0, "#fff1d6", size=2.4, rot=(math.pi, 0, 0))
    kit.light("dr lamp", "AREA", (qx, qy + 1.4, 2.3), 260.0, "#fff1d6", size=2.6)


def build_my_room(kit, ctx, M):
    (bx0, bx1), (by0, by1), top = MY_BED["x"], MY_BED["y"], MY_BED["top"]
    kit.box("my bed", (bx1 - bx0, by1 - by0, top - 0.2), ((bx0 + bx1) / 2, (by0 + by1) / 2, (top - 0.2) / 2), M["base"], bevel=0.02)
    kit.box("my mattress", (bx1 - bx0 - 0.03, by1 - by0 - 0.03, 0.2), ((bx0 + bx1) / 2, (by0 + by1) / 2, top - 0.1),
            M["sheet"], bevel=0.04, seg=3)
    kit.box("my pillow", (0.6, 0.42, 0.13), (MY_PILLOW[0], MY_PILLOW[1], top + 0.06), M["pillow"], bevel=0.05, seg=3)
    # a plain duvet, puffed over whoever is under it (the quilt is the only patchwork in the house)
    kit.box("my duvet", (bx1 - bx0 + 0.1, 1.42, 0.34), ((bx0 + bx1) / 2, by0 + 0.66, top + 0.13), M["duvet"], bevel=0.12, seg=3)


def stack_slots():
    s = STACK
    out = []
    for row in range(s["rows"]):
        for col in range(s["cols"]):
            out.append((s["x0"] + (col + 0.5) * s["w"], s["y"] + s["d"] / 2 + 0.035, row * s["h"] + s["h"] / 2 + 0.002, row, col))
    return out


def build_stack(kit, ctx, M, wd):
    """The 24 boxes by the front door (the clock), three loose boxes in the front room and the quilt's box: every
    one with its own outside tape and no marker, and a slot for two dry marker eyes (L27 to L35, aimed at Mum's door). Every box faces into the room."""
    blank = pil_image("mark-none", marker.mark("none", 64, 64), wd / "mark-none.png")
    lw = int(DIM["head"][0] * PX_PER_M * 0.5)          # the images are half the head's pixels per metre
    eyes = pil_image("mark-eyes", marker.mark("eyes", 380, 370, 7, lw), wd / "mark-eyes.png")
    ctx["mark_imgs"] = {"none": blank, "eyes": eyes}
    boxes = []
    for k, (x, y, z, row, col) in enumerate(stack_slots()):
        size = (STACK["w"] - 0.012, STACK["d"] - 0.02, STACK["h"] - 0.008)
        mat, slots = board(kit, f"stack box {k}", TONES[(k * 5 + 2) % len(TONES)], seed=90 + k,
                           half=tuple(v / 2 for v in size), tape="y" if k % 2 else "x", holes=(k % 4 == 1),
                           decals={"front": blank})
        ob = cbox(kit, f"stack.{k}", size, (x, y + (k % 3) * 0.008, z), (0, 0, math.pi + math.radians((k * 37 % 7) - 3)),
                  mat, sub=4, seed=200 + k, bulge=0.01, sag=0.008)
        base = blank
        boxes.append({"ob": ob, "slot": slots["front"], "base": base, "row": row, "col": col})
    ctx["stack"] = boxes
    # the clean square on the wall where the face box stood (top row, fifth column): it sat there all along
    cs_ = kit.plane("clean square", (STACK["w"] - 0.01, STACK["h"] - 0.01),
                    (STACK["x0"] + 4.5 * STACK["w"], STACK["y"] + 0.012, 3 * STACK["h"] + STACK["h"] / 2),
                    kit.plastic("#e4e5d8", 0.9, name="clean wall"), rot=(math.radians(-90), 0, 0))
    ctx["clean"] = cs_
    loose = []
    for k, (x, y, yaw) in enumerate(((-3.95, -3.05, 196), (-3.95, -4.3, 172), (-3.35, -2.3, 205))):
        size = (0.5, 0.42, 0.4)
        mat, slots = board(kit, f"loose box {k}", TONES[(k * 3 + 1) % len(TONES)], seed=130 + k,
                           half=tuple(v / 2 for v in size), tape="y", decals={"front": blank})
        ob = cbox(kit, f"loose.{k}", size, (x, y, 0.2), (0, 0, math.radians(yaw)), mat, sub=4, seed=240 + k, bulge=0.01)
        loose.append({"ob": ob, "slot": slots["front"], "home": tuple(ob.location), "yaw": math.radians(yaw)})
    ctx["loose"] = loose
    # the quilt's box (L09): open with the quilt folded in it, then its flaps folded shut and pushed to the stack
    qb = kit.empty("quiltbox", (-3.0, -3.9, 0.0), rot=(0, 0, math.radians(8)))
    w, d, h = 0.56, 0.44, 0.38
    mat, _ = board(kit, "quilt box", "#a57a50", seed=150, half=(w / 2, d / 2, h / 2), tape=None)
    kit.box("quiltbox.base", (w, d, 0.02), (0, 0, 0.01), mat, qb)
    for k, (sz, lc) in enumerate((((w, 0.012, h), (0, -d / 2, h / 2)), ((w, 0.012, h), (0, d / 2, h / 2)),
                                   ((0.012, d, h), (-w / 2, 0, h / 2)), ((0.012, d, h), (w / 2, 0, h / 2)))):
        kit.box(f"quiltbox.side{k}", sz, lc, mat, qb)
    kit.box("quiltbox.quilt", (w - 0.04, d - 0.04, 0.06), (0, 0, h - 0.05), M["quilt drape"], qb, bevel=0.02)
    flaps = []
    for k, (n, hinge, width, ln) in enumerate(((V((0, -1, 0)), (0, -d / 2, h), w, d / 2), (V((0, 1, 0)), (0, d / 2, h), w, d / 2),
                                                (V((1, 0, 0)), (w / 2, 0, h), d, w / 2 - 0.02), (V((-1, 0, 0)), (-w / 2, 0, h), d, w / 2 - 0.02))):
        hg = kit.empty(f"quiltbox.flap{k}", hinge, qb)
        thin = (width, 0.008, ln) if abs(n.y) > 0.5 else (0.008, width, ln)
        kit.box(f"quiltbox.flapm{k}", thin, (0, 0, ln / 2), mat, hg)
        flaps.append((hg, n, k))
    ctx["quiltbox"] = (qb, flaps)
    # clean squares in the dust where the stack's bottom row stood (only once the floor is bare, L41)
    span = STACK["cols"] * STACK["w"] + 0.12
    dust = Image.new("RGBA", (880, 240), (176, 170, 160, 120))
    dd = ImageDraw.Draw(dust)
    for col in range(STACK["cols"]):
        x0 = 880 * (0.06 / span + col * STACK["w"] / span)
        dd.rectangle([x0 + 4, 240 * 0.1, x0 + 880 * (STACK["w"] - 0.014) / span, 240 * 0.86], fill=(0, 0, 0, 0))
    r = np.random.default_rng(5)
    a = np.asarray(dust).astype(np.float32)
    a[..., 3] *= 0.75 + 0.5 * r.random(a.shape[:2])
    dust = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
    dimg = pil_image("dust", dust, wd / "dust.png")
    dm = kit._new("dust")
    nt = dm.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = dimg
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = 0.95
    kit._fogged(dm, b.outputs[0])
    dust_ob = kit.plane("dust squares", (span, STACK["d"] + 0.06), (STACK["x0"] + span / 2 - 0.06, STACK["y"] + STACK["d"] / 2 + 0.01, 0.002), dm)
    uv = dust_ob.data.uv_layers.new(name="UVMap")
    for poly in dust_ob.data.polygons:
        for li in poly.loop_indices:
            co = dust_ob.data.vertices[dust_ob.data.loops[li].vertex_index].co
            uv.data[li].uv = (co.x / span + 0.5, co.y / (STACK["d"] + 0.06) + 0.5)
    ctx["dust"] = dust_ob
    # the folded boxes at Mum's feet (L75): flattened board in a short pile in the hall by the cupboard
    pile = kit.empty("folded pile", (-0.6, -0.92, 0.0), rot=(0, 0, math.radians(6)))
    for k in range(6):
        mat_k, _ = board(kit, f"folded {k}", TONES[k % len(TONES)], seed=170 + k, half=(0.4, 0.3, 0.006), tape="y")
        kit.box(f"folded.{k}", (0.8, 0.5, 0.012), (0.012 * k, -0.01 * k, 0.006 + k * 0.013), mat_k, pile,
                rot=(0, 0, math.radians(k * 4 - 10)))
    ctx["pile"] = pile
    # a box I carry (L05, L71 and L72), held in front of me: animate() places it
    mat_c, _ = board(kit, "carried box", TONES[2], seed=188, half=(0.24, 0.2, 0.18), tape="y")
    ctx["carry"] = cbox(kit, "carried box", (0.48, 0.4, 0.36), (0, 0, -5), (0, 0, 0), mat_c, sub=4, seed=288, bulge=0.01)


def build_props(kit, ctx, M, wd):
    # the mug (no logo): on the front sill most mornings, in Mum's hand when she lifts it
    mug = kit.empty("mug", SILL)
    kit.cyl("mug.body", 0.043, 0.098, (0, 0, 0.049), M["mug"], mug, n=24)
    tube(kit, "mug.handle", 0.03, 0.019, 0.014, (0.05, 0, 0.052), M["mug"], mug, rot=(math.radians(90), 0, 0), n=16)
    kit.cyl("mug.tea", 0.038, 0.004, (0, 0, 0.088), M["drawer"], mug, n=24)
    ctx["mug"] = mug
    # the photos: drawn here, hung low, then up the wall and across the ceiling
    frames = []
    for k, kind in enumerate(PHOTOS):
        fw_, fh_ = PHOTO_SIZE[k]
        if kind == "oldhouse":
            imgs_oh = [pil_image("oh-" + n, old_house_image(n == "lit"), wd / f"photo-oldhouse-{n}.png") for n in ("dim", "lit")]
            img = imgs_oh[0]
        else:
            im = photo_image(kind, 360, int(360 * fh_ / fw_))
            img = pil_image(f"photo {k}", im, wd / f"photo-{k}-{kind}.png")
        g = kit.empty(f"photo{k}", (0, 0, -5))
        kit.box(f"photo{k}.frame", (fw_ + 0.05, 0.022, fh_ + 0.05), (0, 0, 0), M["frame wood"], g, bevel=0.004)
        pm = image_mat(kit, f"photo {k}", img, 0.4, 0.0)
        if kind == "oldhouse":
            ctx["oh_tex"] = next(n for n in pm.node_tree.nodes if n.type == "TEX_IMAGE")
            ctx["oh_imgs"] = {"dim": imgs_oh[0], "lit": imgs_oh[1]}
        pl = kit.plane(f"photo{k}.pic", (fw_, fh_), (0, -0.0115, 0), pm, g, rot=(math.radians(90), 0, 0))
        uv = pl.data.uv_layers.new(name="UVMap")
        for poly in pl.data.polygons:
            for li in poly.loop_indices:
                co = pl.data.vertices[pl.data.loops[li].vertex_index].co
                uv.data[li].uv = (co.x / fw_ + 0.5, co.y / fh_ + 0.5)
        frames.append(g)
    ctx["photos"] = frames
    # the quilt round Mum's shoulders (L64 on): a loose patchwork drape, open at the front
    cape = kit.empty("quilt cape", (0, 0, -5))
    for k, (sz, lc, rx) in enumerate((((1.2, 0.05, 0.9), (0, 0.21, -0.4), -4),      # down her back
                                       ((0.045, 0.4, 0.78), (0.6, 0.02, -0.33), 0),   # over each arm
                                       ((0.045, 0.4, 0.78), (-0.6, 0.02, -0.33), 0),
                                       ((0.38, 0.44, 0.06), (0.4, 0.02, 0.03), 0),    # over each shoulder, the neck clear
                                       ((0.38, 0.44, 0.06), (-0.4, 0.02, 0.03), 0))):
        kit.box(f"cape.{k}", sz, lc, M["quilt drape"], cape, rot=(math.radians(rx), 0, 0), bevel=0.025)
    ctx["cape"] = cape


def time_lights(kit, ctx):
    """The light by time of day (the brief): a soft cold dawn at every window, near black at night with the
    windows a dim grey, the 3 a.m. set in Mum's room, and the low gold sun through the front window from L64.
    TIME_LIGHTS says which are on when."""
    for nm, (c, n, (ww, wh)) in WINDOWS.items():
        cx, cy, cz = c
        ob = kit.light(f"dawn {nm}", "AREA", (cx + n[0] * 0.1, cy + n[1] * 0.1, cz), 70.0, "#9fb0c8", size=ww)
        ob.data.shape = "RECTANGLE"
        ob.data.size_y = wh
        ob.rotation_euler = _panel_rot(n)
        ob.visible_camera = False
        ob.visible_glossy = False
    # the hall has no window: the dawn reaches it through the kitchen and front-room doorways (from the side)
    for nm, (a, b) in (("kitchen", KITCHEN_DOOR), ("front", FRONT_DOOR_H)):
        ob = kit.light(f"spill {nm}", "AREA", ((a + b) / 2, -1.5, 1.1), 34.0, "#9aa8bc", size=b - a)
        ob.data.shape = "RECTANGLE"
        ob.data.size_y = 1.9
        ob.rotation_euler = _panel_rot((0, 1, 0))
        ob.visible_camera = False
        ob.visible_glossy = False
    ob = kit.light("spill sun", "AREA", ((FRONT_DOOR_H[0] + FRONT_DOOR_H[1]) / 2, -1.5, 1.1), 16.0, "#ffd7a0",
                   size=FRONT_DOOR_H[1] - FRONT_DOOR_H[0])
    ob.data.shape = "RECTANGLE"
    ob.data.size_y = 1.9
    ob.rotation_euler = _panel_rot((0, 1, 0))
    ob.visible_camera = False
    ob.visible_glossy = False
    mf = kit.light("me fill", "AREA", (-3.55, 2.05, 1.7), 9.0, "#9aa6ba", size=0.6)
    kit.aim(mf, (MY_PILLOW[0], MY_PILLOW[1] - 0.1, 0.75))
    mf.visible_camera = False
    mf.visible_glossy = False
    nf = kit.light("night front", "AREA", (FRONT[1] - 0.1, WINDOWS["front"][0][1], WINDOWS["front"][0][2]), 12.0, "#7c8696",
                   size=0.8)
    nf.rotation_euler = _panel_rot((-1, 0, 0))
    nf.visible_camera = False
    nf.visible_glossy = False
    hall = kit.light("hall fill", "AREA", (-1.6, -0.77, CEIL - 0.05), 10.0, "#9aa8bc", size=1.0)
    hall.visible_camera = False
    hall.visible_glossy = False
    night = kit.light("night mine", "AREA", (WINDOWS["mine"][0][0], Y1 - 0.1, WINDOWS["mine"][0][2]), 30.0, "#7c8696",
                      size=0.7)
    night.rotation_euler = _panel_rot((0, -1, 0))
    night.visible_camera = False
    night.visible_glossy = False
    # the sun at L64: low and gold, in through the front window, raking across the photo wall and the ceiling
    sun = kit.light("sun", "SPOT", (FRONT[1] + 1.6, -4.75, 1.3), 1500.0, "#ffcf8a", spot=30, blend=0.3, size=0.05)
    kit.aim(sun, (FRONT[0], -3.0, 2.0))
    sun.visible_camera = False
    up = kit.light("sun ceiling", "AREA", (-3.2, -3.4, 0.4), 40.0, "#ffcf8a", size=1.6)
    up.rotation_euler = (math.pi, 0, 0)
    up.visible_camera = False
    up.visible_glossy = False
    # the glow from Mum's door at 3 a.m.: her nightlight, through her open door, throws the Boxes' shadow up the
    # hall's far wall and over its ceiling. It lights the hall only (build() links it)
    nx_, nz = NIGHTLIGHT
    glow = kit.light("door glow", "SPOT", (nx_ + 0.02, Y1 - 0.1, nz + 0.28), 1500.0, "#d6e4ff", spot=60, blend=0.5, size=0.004)
    kit.aim(glow, ((DOOR_X[0] + DOOR_X[1]) / 2, -0.06, 1.0))
    glow.visible_camera = False
    # the face box's own light in the morning scenes: from below and the side, aimed between its eyes, lighting
    # only the face box (animate places it per pose: POSES "key")
    fk = kit.light("face key", "SPOT", (0, 0, 0.3), 40.0, "#c8d4e6", spot=22, blend=0.5, size=0.05)
    fk.visible_camera = False
    fk.data.use_shadow = False
    ctx["face key"] = fk
    # ...and a soft side light on its body (it lights only the Boxes), from the room's window side or from
    # behind: the boxes and their joints read, the front never lit flat (POSES "body_key")
    bk = kit.light("body key", "SPOT", (0, 0, 0.3), 70.0, "#b8c6da", spot=55, blend=0.6, size=0.3)
    bk.visible_camera = False
    bk.visible_glossy = False
    ctx["body key"] = bk
    # warm daylight for the morning shots: a broad warm area under each room's ceiling
    for tag, (x0, x1, y0, y1) in ROOMS.items():
        if tag in ("cupboard",):
            continue
        f = kit.light(f"day {tag}", "AREA", ((x0 + x1) / 2, (y0 + y1) / 2, CEIL - 0.08), 90.0, "#ffe2b8",
                      size=min(x1 - x0, y1 - y0) * 0.9)
        f.visible_camera = False
        f.visible_glossy = False
    # a soft fill under each room's ceiling by day (the white walls' bounce, lifted)
    for tag, (x0, x1, y0, y1) in ROOMS.items():
        if tag == "cupboard":
            continue
        f = kit.light(f"fill {tag}", "AREA", ((x0 + x1) / 2, (y0 + y1) / 2, CEIL - 0.06), 14.0, "#a7b3c4",
                      size=min(x1 - x0, y1 - y0) * 0.6)
        f.visible_camera = False
        f.visible_glossy = False


TIME_LIGHTS = {   # light: gain, per time of day. Every light not listed is off
    "street": {"street sun": 1.0, "lr lamp": 1.0, "dr lamp": 1.0, "lr up": 1.0, "dr up": 1.0},
    "day": {"dawn mum": 0.8, "dawn mine": 0.8, "dawn front": 0.8, "dawn kitchen": 0.7, "spill kitchen": 1.0,
            "spill front": 1.0, "hall fill": 1.0, "face key": 0.0, "body key": 0.0, "fill mum": 1.0, "fill mine": 1.0,
            "fill hall": 1.0, "fill front": 1.8, "fill kitchen": 1.0, "day front": 1.0, "day kitchen": 1.0,
            "day hall": 1.0, "day mine": 1.0, "day mum": 1.0},
    "dawn": {"dawn mum": 1.0, "dawn mine": 1.0, "dawn front": 1.0, "dawn kitchen": 0.55, "spill kitchen": 1.0,
             "spill front": 1.0, "hall fill": 1.0, "face key": 1.0, "body key": 1.0, "fill mum": 1.0, "fill mine": 1.0,
             "fill hall": 1.0, "fill front": 1.8, "fill kitchen": 1.0},
    "night": {"night mine": 1.0, "night front": 1.0, "face key": 0.45, "body key": 0.5, "me fill": 1.0},
    "night3": {"body key": 1.0, "nightlight": 1.0, "nightlight kick": 1.0, "nightlight rim": 1.0, "window": 1.0, "window ceiling": 1.0,
               "window rake": 1.0, "window edge": 1.0, "mum fill": 1.0, "pillow fill": 1.0, "arm fill": 1.0, "door glow": 1.0, "lamp": 1.0, "night mine": 1.0, "me fill": 1.0,
               "night front": 1.0},
    "sun": {"sun": 1.0, "sun ceiling": 1.0, "face key": 0.9, "body key": 0.6, "dawn front": 0.6, "dawn kitchen": 0.8, "dawn mum": 0.7, "dawn mine": 0.7,
            "spill kitchen": 0.8, "spill front": 0.5, "spill sun": 1.0, "hall fill": 1.2, "fill mum": 0.8, "fill mine": 0.8,
            "fill hall": 1.0, "fill front": 1.8, "fill kitchen": 1.0},
    "end": {"dawn front": 0.9, "dawn kitchen": 0.9, "dawn mum": 0.8, "dawn mine": 0.8, "spill kitchen": 1.0,
            "spill front": 1.0, "hall fill": 1.4, "face key": 1.0, "body key": 1.0, "fill hall": 1.2, "fill front": 1.0,
            "fill kitchen": 1.0, "fill mum": 1.0, "fill mine": 1.0},
}
EXPOSURE = {"dawn": 0.45, "night": 1.0, "night3": 1.0, "sun": 0.5, "end": 0.45, "day": 0.45, "street": 0.45}   # the view's exposure by time
OUTSIDE = {"day": ("#dfe6f0", 2.0), "street": ("#7f8fa8", 1.3), "dawn": ("#7f8fa8", 1.3), "night": ("#1f242c", 0.4), "night3": ("#262b33", 0.7), "sun": ("#ffd9a0", 2.4),
           "end": ("#a9b4c2", 1.5)}


# ------------------------------------------------------------------------------------------------ Mum's room


def build_bed(kit, ctx, M):
    (bx0, bx1), (by0, by1) = BED_X, BED_Y
    kit.box("divan", (bx1 - bx0, by1 - by0, BASE_Z), ((bx0 + bx1) / 2, (by0 + by1) / 2, BASE_Z / 2), M["base"], bevel=0.02)
    kit.box("mattress", (bx1 - bx0 - 0.04, by1 - by0 - 0.04, MAT_Z - BASE_Z), ((bx0 + bx1) / 2, (by0 + by1) / 2,
            (BASE_Z + MAT_Z) / 2), M["sheet"], bevel=0.05, seg=3)
    kit.box("headboard", (0.05, by1 - by0 + 0.06, 0.95), (X0 + 0.03, (by0 + by1) / 2, 0.55), M["wood"], bevel=0.015)
    kit.box("pillow", (0.5, 0.7, 0.14), (bx0 + 0.36, 1.92, MAT_Z + 0.065), M["pillow"], bevel=0.06, seg=3,
            rot=(0, 0, math.radians(3)))
    # a second pillow propped against the headboard behind her crown: a pale ground her head and hair read on
    kit.box("pillow2", (0.15, 0.72, 0.46), (bx0 + 0.13, 1.92, MAT_Z + 0.24), M["pillow"], bevel=0.06, seg=3,
            rot=(0, math.radians(-16), 0))


def build_quilt(kit, ctx, M, body):
    """The old quilt, loose and puffy, from her shoulders to the bed's foot and down both sides, over a body
    lying along x at body["y"] from body["x_top"] (shoulders) to body["x_feet"]. Her near arm (body["arm"]: y, x
    from, x to, the height it lies at) lies out on top of it."""
    (bx0, bx1), (by0, by1) = BED_X, BED_Y
    x0, x1 = body["x_top"], bx1 + 0.12
    y0, y1 = by0 - 0.3, by1 + 0.1   # the far side hangs just over the edge: the Boxes stand close behind the bed
    nx, ny = 70, 48
    rng = np.random.default_rng(7)
    ph = rng.uniform(0, 6.28, 4)
    ay, ax0, ax1, az = body["arm"]
    verts, uvs = [], []
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * i / nx
            y = y0 + (y1 - y0) * j / ny
            dy = abs(y - body["y"])
            along = _ss((x - x0) / 0.1) * (1 - _ss((x - body["x_feet"] - 0.05) / 0.25))
            mound = body["h"] * (1 - _ss((dy - body["w"]) / 0.3 + 0.5)) * along
            z = MAT_Z + 0.03 + mound
            # under her near arm the quilt sits just below it, so the arm lies on top
            if abs(y - ay) < 0.2 and ax0 - 0.05 < x < ax1 + 0.05:
                z = min(z, az) if y < body["y"] else z
            out_y = max(by0 - y, y - by1, 0.0)
            out_x = max(x - bx1, 0.0)
            out = math.hypot(out_y, out_x)
            if out > 0:
                z = MAT_Z + 0.03 - out * 2.6 - out * out * 4
            # puffy at the top edge, a loose roll at her shoulders
            z += 0.035 * (1 - _ss((x - x0) / 0.16)) * (1 if out == 0 else 0)
            z += 0.012 * math.sin(x * 7 + ph[0]) * math.sin(y * 5 + ph[1]) + 0.008 * math.sin(x * 13 + y * 11 + ph[2])
            verts.append((x, y, max(0.02, z)))
            uvs.append(((x - x0) / (x1 - x0), (y - y0) / (y1 - y0)))
    faces = []
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    ob = kit.mesh_obj("quilt", verts, faces, M["quilt"], smooth=True)
    uv = ob.data.uv_layers.new(name="UVMap")
    for poly in ob.data.polygons:
        for li in poly.loop_indices:
            uv.data[li].uv = uvs[ob.data.loops[li].vertex_index]
    sol = ob.modifiers.new("solid", "SOLIDIFY")
    sol.thickness = 0.045
    sol.offset = 1.0
    ctx["quilt"] = ob
    return ob


def build_dressing(kit, ctx, M):
    """The chest of drawers inside the door with the dim lamp on it, and the plug-in nightlight on the far wall.
    No logos, no text."""
    x, y = DRAWERS
    w, d, h = 0.62, 0.4, 0.78
    kit.box("drawers", (w, d, h), (x, y + d / 2, h / 2), M["wood"], bevel=0.01)
    for k in range(3):
        z = 0.14 + k * 0.23
        kit.box(f"drawer{k}", (w - 0.06, 0.012, 0.2), (x, y - 0.004, z), M["drawer"], bevel=0.004)
        kit.cyl(f"knob{k}", 0.014, 0.02, (x, y - 0.018, z), M["cord"], rot=(math.radians(90), 0, 0))
    kit.cyl("lamp base", 0.06, 0.04, (x - 0.12, y + 0.2, h + 0.02), M["trim"])
    kit.cyl("lamp stem", 0.012, 0.26, (x - 0.12, y + 0.2, h + 0.17), M["trim"])
    shade = kit.cyl("lamp shade", 0.13, 0.17, (x - 0.12, y + 0.2, h + 0.33), M["shade"], r2=0.09)
    ctx["shade"] = shade
    nx_, nz = NIGHTLIGHT
    kit.box("nightlight", (0.07, 0.035, 0.09), (nx_, Y1 - 0.018, nz), M["trim"], bevel=0.008)
    kit.sphere("nightlight.dome", 0.03, (nx_, Y1 - 0.04, nz), M["nightglow"])
    # L46: the door's square of nightlight on the hall's south wall, running up it and bending over the ceiling:
    # two hard-edged panels (a thin light wash over the wall, not a lit surface), shown only while the cue is on
    sq = kit._new("sqlight")
    nt = sq.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.02, 0.02, 0.025, 1.0)   # a SHADOW: unlit near-black, no sheen
    em.inputs["Strength"].default_value = 1.0
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs["Fac"].default_value = 0.93
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    kit._fogged(sq, mx.outputs[0])
    sx0, sx1 = SQUARE_X
    sqw = kit.box("sqlight.wall", (sx1 - sx0, 0.003, 2.35 - SQUARE_Z0), ((sx0 + sx1) / 2, HALL[2] + 0.002, (SQUARE_Z0 + 2.35) / 2), sq)
    sqc = kit.box("sqlight.ceil", (sx1 - sx0, SQUARE_DEPTH, 0.003), ((sx0 + sx1) / 2, HALL[2] + SQUARE_DEPTH / 2, 2.35 - 0.002), sq)
    ctx["sqlight"] = [sqw, sqc]


def build_lights(kit, ctx):
    nx_, nz = NIGHTLIGHT
    # Mum's nightlight: the only light at 3 a.m., low on the far wall beyond the Boxes. Cold, from below and
    # behind: it rims the Boxes and lights the underside of everything over the bed
    nl = kit.light("nightlight", "POINT", (nx_, Y1 - 0.22, nz + 0.02), 1.2, "#d6e4ff", size=0.04)
    nl.visible_camera = False
    # ...and the same light carried to the face box only (from the nightlight's own place): a tight pool on the
    # eye line, so the bare board inside the eyes is the brightest thing on the Boxes and the box's edges and the
    # foot of the mouth fall away to black. animate() keeps it aimed between the eyes
    kick = kit.light("nightlight kick", "SPOT", (nx_, Y1 - 0.08, nz + 0.03), 230.0, "#d6e4ff", spot=19, blend=0.45,
                     size=0.05)
    kick.visible_camera = False
    kick.data.use_shadow = False   # it stands in for the glow reaching the face past its own body
    ctx["kick"] = kick
    # the window: a dim grey wash through the curtains, from the side. It reaches the room, never the Boxes
    # (build() links it), and the Boxes cast no shadow in it, so the ceiling behind the neck chain stays lit and
    # the chain stands out against it; only the nightlight throws the Boxes' shadow
    win = kit.light("window", "AREA", (X1 - 0.2, WIN_Y[0] + 0.2, 1.9), 22.0, "#8a96aa", size=0.9)
    kit.aim(win, (-0.2, 1.55, 0.5))   # raking the quilt toward the bed's foot; her shoulders stay darker
    win.visible_camera = False
    win.visible_glossy = False
    # the window's light off the far wall, behind and above the Boxes (it lights only the Boxes): a rim, a cold line
    # down every box's far edges, so the body reads as a dozen boxes, not one black suit, and the tape inside
    # the joints glints. From behind, never the front
    edge = kit.light("window edge", "AREA", (0.95, Y1 - 0.08, CEIL - 0.1), 60.0, "#8a96aa", size=0.5)
    kit.aim(edge, (-0.4, 1.4, 1.3))
    edge.visible_camera = False
    # the window's light up on the ceiling over the bed, so the neck chain stands out dark against it (never on
    # the Boxes, and they don't shadow it: build() links it)
    wc = kit.light("window ceiling", "AREA", (X1 - 0.2, 1.5, 1.7), 30.0, "#8a96aa", size=0.6)
    kit.aim(wc, (-0.7, 2.4, CEIL))
    wc.visible_camera = False
    wc.visible_glossy = False
    # the window's light low across the near side of the bed and the floor, from the front right: the quilt's
    # drape toward the foot reads cold and low in colour below the caption (never on the Boxes: build() links it)
    rake = kit.light("window rake", "AREA", (X1 - 0.15, 0.55, 0.95), 26.0, "#8a96aa", size=0.6)
    kit.aim(rake, (-0.9, 1.3, 0.3))
    rake.visible_camera = False
    rake.visible_glossy = False
    # the nightlight's own glow on the Boxes, from its place low behind them (it lights only the Boxes): the
    # undersides we see from the door, the box edges and the tape inside the joints catch it, hard-edged
    nrim = kit.light("nightlight rim", "POINT", (nx_, Y1 - 0.2, nz + 0.05), 13.0, "#d6e4ff", size=0.03)
    nrim.visible_camera = False
    nrim.data.use_shadow = False   # its own legs would shadow every underside we see from the door
    # Mum's own fill, motivated by the window: her face and her near hand only
    fill = kit.light("mum fill", "AREA", (-0.85, 1.25, 2.15), 26.0, "#9aa6ba", size=0.8)
    kit.aim(fill, (-1.35, 1.95, 0.6))
    fill.visible_camera = False
    fill.visible_glossy = False
    for nm, e in (("pillow fill", 26.0 * 0.8), ("arm fill", 13.0)):
        f2 = kit.light(nm, "AREA", (-0.85, 1.25, 2.15), e, "#9aa6ba", size=0.8)
        kit.aim(f2, (-1.35, 1.95, 0.6))
        f2.visible_camera = False
        f2.visible_glossy = False
    # one movable soft light for the shots that need lifting (the "xfill" cues: place, aim, gain), lighting everything
    xf = kit.light("xfill", "AREA", (0, 0, 1.5), 60.0, "#aab6c8", size=0.9)
    xf.visible_camera = False
    xf.visible_glossy = False
    ctx["xfill"] = xf
    # the lamp on the chest of drawers (off until L51)
    lamp = kit.light("lamp", "POINT", (DRAWERS[0] - 0.12, DRAWERS[1] + 0.2, 1.08), 28.0, "#ffc890", size=0.06)
    ctx["lamp"] = lamp


def build(kit, story, tl):
    ctx = {"story": story}
    wd = workdir(tl)
    M = materials(kit, wd)
    ctx["M"], ctx["wd"], ctx["outside"] = M, wd, M["_outside_glow"]
    build_house(kit, ctx, M)
    build_kitchen(kit, ctx, M)
    build_my_room(kit, ctx, M)
    build_street(kit, ctx, M)
    build_stack(kit, ctx, M, wd)
    build_props(kit, ctx, M, wd)
    build_bed(kit, ctx, M)
    body = {"y": 1.92, "x_top": -1.04, "x_feet": 0.27, "h": 0.36, "w": 0.24, "arm": (1.39, -1.02, -0.3, 0.48)}
    build_quilt(kit, ctx, M, body)
    build_dressing(kit, ctx, M)
    cr = build_boxes(kit, ctx, M, wd)
    build_peel(kit, ctx, M, cr)
    build_lights(kit, ctx)
    time_lights(kit, ctx)
    # Mum's own fills light nothing until she lies down and dress_mum() links them to her (a placeholder far off)
    dummy = kit.box("fill placeholder", (0.01, 0.01, 0.01), (0, 0, -20), M["trim"])
    dummy.hide_render = True
    for nm in ("mum fill", "arm fill"):
        light_only(kit, f"{nm} none", nm, [dummy])
    light_only(kit, "mum pillows", "pillow fill", [bpy.data.objects["pillow"], bpy.data.objects["pillow2"]])
    light_only(kit, "boxes face", "nightlight kick", [cr["head"]])
    light_only(kit, "boxes face", "face key", [cr["head"]])
    # 3 a.m. in Mum's room: the window lights the room and none of the Boxes, and the Boxes don't shadow it; the
    # hands and the quilt's edge stay in shadow until the lamp (the brief, item 5). The edge lights light only
    # the Boxes
    allb = [ob for ob in cr["pivots"]["root"].children_recursive if ob.type == "MESH"]
    light_except(kit, "boxes all", "window", allb)
    light_except(kit, "boxes all", "window rake", allb)
    light_except(kit, "boxes all", "window ceiling", allb)
    no_shadow(kit, "boxes cast none", "window", allb)
    no_shadow(kit, "boxes cast none", "window ceiling", allb)
    light_only(kit, "boxes edge", "window edge", allb)
    light_only(kit, "boxes edge", "nightlight rim", allb)
    light_only(kit, "boxes edge", "body key", allb)
    # the glow from her door lights the hall only (its walls, floor, ceiling and whoever stands in it)
    # (never her room's own front wall: lit from inside, it would bounce the glow back round her room)
    hall = [o for o in bpy.data.objects if o.type == "MESH" and (o.name.split(".")[0] in ("w hall s", "w west", "w hall e")
            or o.name.startswith(("floor hall", "ceiling hall", "skirt w hall s", "skirt w hall e", "jamb front", "head front", "jamb kitchen",
                                   "head kitchen", "door mine", "door cupboard", "jamb cupboard", "head cupboard")))]
    light_only(kit, "hall glow", "door glow", hall)
    if __import__("os").environ.get("MOVING_DAY_FLAT"):   # look-dev only: flat light to check the geometry
        kit.world("#8a8f99", 1.0)
        for ob in bpy.data.objects:
            if ob.name.startswith("ceiling") or ob.name.split(".")[0] in __import__("os").environ["MOVING_DAY_FLAT"].split(","):
                ob.hide_render = True
    return ctx


def dress_mum(kit, story, ctx):
    """Once Mum is posed lying down: her hair fanned out on the pillow (her R6 hair block sinks into it, and a
    head with no hair reads as a box), and her own fill light linked to her face and her near hand only."""
    bpy.context.view_layer.update()
    head = bpy.data.objects["mum.headm"]
    vs = [head.matrix_world @ v.co for v in head.data.vertices]
    hx = sum(v.x for v in vs) / len(vs)
    hy = sum(v.y for v in vs) / len(vs)
    zp = MAT_Z + 0.065 + 0.07                      # the pillow's top
    hair = kit.plastic(story["cast"]["mum"].get("hair_c", "#4a3a32"), 0.7, name="mum fan")
    fan = []
    # round her crown (-x) and out behind her head (+y), never over the face side
    for k, (dx, dy, sx, sy, rz) in enumerate(((-0.25, 0.05, 0.24, 0.5, 0), (-0.04, 0.3, 0.38, 0.2, 18),
                                               (-0.3, -0.15, 0.15, 0.2, 30), (-0.16, 0.24, 0.2, 0.16, -20))):
        fan.append(kit.box(f"mum.fan{k}", (sx, sy, 0.022), (hx + dx, hy + dy, zp + 0.006 + 0.004 * k), hair,
                           rot=(0, 0, math.radians(rz)), bevel=0.01))
    # and up the propped pillow behind her crown, so her head has hair round it from the door
    pw = bpy.data.objects.get("pillow2")
    if pw is not None:
        for k, (dy, dz, sy, sz, rx) in enumerate(((0.0, 0.0, 0.46, 0.24, 0), (-0.2, -0.06, 0.16, 0.18, 24),
                                                 (0.21, -0.05, 0.15, 0.2, -20))):
            fan.append(kit.box(f"mum.fanup{k}", (0.02, sy, sz), (0, dy, dz), hair, rot=(math.radians(rx), 0, 0),
                               bevel=0.008, parent=pw))
            fan[-1].location.x = 0.085 + 0.003 * k   # on the pillow's face toward her (its local +x)
            fan[-1].location.z = (zp + 0.2 - pw.location.z) + dz
    # her face and hair at the full fill; the pillows a fifth less and her near arm a stop under her face (the
    # critic's polish), from the same place
    light_only(kit, "mum lit", "mum fill", [head] + fan)
    light_only(kit, "mum arm", "arm fill", [o for o in (bpy.data.objects.get(n) for n in ("mum.skinarm-1",)) if o])
    ctx["mum_dressed"] = True
    ctx["fan"] = fan


def probe(ctx):
    """Contact probe (README: before every final render): BVH overlaps between the posed Boxes and everything
    else, the air under the face box, and how near each flap hand comes to Mum. Printed into the Blender log
    when MOVING_DAY_PROBE is set; returns the overlapping (box, other) names."""
    from mathutils.bvhtree import BVHTree

    dg = bpy.context.evaluated_depsgraph_get()

    def tree(ob):
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        t = BVHTree.FromPolygons([ob.matrix_world @ v.co for v in me.vertices], [tuple(pl.vertices) for pl in me.polygons])
        ev.to_mesh_clear()
        return t

    cr = ctx["boxes"]
    mine = [o for o in cr["pivots"]["root"].children_recursive if o.type == "MESH" and not o.hide_render]
    others = [o for o in bpy.data.objects if o.type == "MESH" and o not in mine and not o.hide_render
              and not o.name.startswith(("outside", "floor", "dust", "folded"))]
    trees = {o.name: tree(o) for o in mine}
    hits = [(n, o.name) for o in others for n, t in trees.items() if t.overlap(tree(o))]
    mum = [o for o in bpy.data.objects if o.name.startswith("mum.") and o.type == "MESH" and not o.hide_render]
    top = max([(o.matrix_world @ v.co).z for o in mum for v in o.data.vertices] +
              [(ctx["quilt"].matrix_world @ v.co).z for v in ctx["quilt"].data.vertices])
    lo, hi, fc, fz = boxes_extent(cr)
    print(f"PROBE {len(hits)} contacts {hits[:20]}; top {hi:.3f} m (ceiling {CEIL}); air under the face box "
          f"{fz - top:.2f} m", flush=True)
    mv = [o.matrix_world @ v.co for o in mum for v in list(o.data.vertices)[::3]]
    for sx in (-1, 1):
        tips = [o.matrix_world @ v.co for o in mine if f".flapb{sx}." in o.name or f".flapt{sx}." in o.name
                for v in o.data.vertices]
        if tips and mv:
            print(f"PROBE hand {sx}: nearest flap to Mum {min((a - b).length for a in tips for b in mv):.3f} m", flush=True)
    return hits


# ------------------------------------------------------------------------------------------------ animate


def build_peel(kit, ctx, M, cr):
    """The L01 box (the Boxes' right shin, the bottom box): the strip of outside tape I peeled, still hanging off
    its front face where it ran up from the flap seam at the floor. It stays peeled in every shot (the brief)."""
    shin = next(o for o in cr["meshes"] if o.name.endswith(".shin1"))
    sw, sd, sh = DIM["shin"]
    n, wdt, length = 16, 0.048, 0.24
    verts, faces = [], []
    p = V((0.04, -sd / 2 - 0.0015, -sh / 2))      # it runs up the face from the bottom edge
    th = 0.0
    pts = []
    for i in range(n + 1):
        pts.append(p.copy())
        s = i / n
        th = 0.0 if s < 0.3 else math.radians(170) * ((s - 0.3) / 0.7) ** 1.4   # stuck flat, then curling off
        p = p + V((0.0, -math.sin(th), math.cos(th))) * (length / n)
    for k, q in enumerate(pts):
        tw = 0.004 * math.sin(k * 0.9)
        verts += [(q.x - wdt / 2, q.y + tw, q.z), (q.x + wdt / 2, q.y - tw, q.z)]
    for i in range(n):
        faces.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    ob = kit.mesh_obj("boxes.peel", verts, faces, M["tape"], shin, smooth=True)
    cr["meshes"].append(ob)
    ctx["peel"] = ob


def _panel_rot(n):
    """A rectangle light's rotation so it shines along n (into a room) with its height (size_y) upright."""
    z = -V(n).normalized()
    y = V((0, 0, 1))
    x = y.cross(z)
    return Matrix((x, y, z)).transposed().to_euler()


def _eased(cs, key, t, default):
    """A cue's value at t: each cue's `key`, eased in over its "dur" from the value before it."""
    level = prev = default
    for c in cs:
        if c["t"] > t + 1e-9 or key not in c:
            continue
        prev, level = level, c[key]
        d = float(c.get("dur", 0.0))
        if d > 0 and t < c["t"] + d and isinstance(level, (int, float)) and isinstance(prev, (int, float)):
            level = prev + (level - prev) * _ss((t - c["t"]) / d)
    return level


def _time_state(kit, tl, t):
    """The lights' gains and the outside's glow at t from the "time" cues ({"set": a TIME_LIGHTS key, "dur": s
    to blend in from the set before})."""
    cs = [c for c in _cues(tl, "time") if c["t"] <= t + 1e-9]
    cur = cs[-1]["set"] if cs else "dawn"
    prev = cs[-2]["set"] if len(cs) > 1 else cur
    u = 1.0
    if cs and float(cs[-1].get("dur", 0)) > 0:
        u = _ss((t - cs[-1]["t"]) / float(cs[-1]["dur"]))
    ga, gb = TIME_LIGHTS[prev], TIME_LIGHTS[cur]
    gains = {k: ga.get(k, 0.0) * (1 - u) + gb.get(k, 0.0) * u for k in set(ga) | set(gb)}
    (ca, sa), (cb, sb) = OUTSIDE[prev], OUTSIDE[cur]
    a, b = kit.col(ca), kit.col(cb)
    colour = tuple(a[i] + (b[i] - a[i]) * u for i in range(3)) + (1.0,)
    return gains, colour, sa + (sb - sa) * u


def _rig_point(who, part, local):
    """A point on a rig part in the world (rig units, under the character's scaled root)."""
    ob = bpy.data.objects.get(f"{who}.{part}")
    return None if ob is None else ob.matrix_world @ V(local)


def _rig_frame(who, local=(0, 0, 0), part=None):
    """A frame at a point on the character, turned with the character but never scaled: for a prop it holds."""
    root = bpy.data.objects.get(who)
    if root is None:
        return None
    ob = bpy.data.objects.get(f"{who}.{part}") if part else root
    p = ob.matrix_world @ V(local)
    rot = root.matrix_world.to_quaternion().to_matrix().to_4x4()
    return Matrix.Translation(p) @ rot


def _show(objs, on):
    for o in objs:
        for oo in [o] + list(o.children_recursive):
            oo.hide_render = not on


def pose_shelf(cr, pose):
    """The face box alone on the hall cupboard's shelf, made up and taped, its smile out at the cupboard door:
    the same box (its dent, its tone), nothing else of the figure."""
    P = cr["pivots"]
    x, y, z = pose["at"]
    m = Matrix.Translation((x, y, z - G / 2 + 0.004)) @ Matrix.Rotation(math.radians(pose.get("yaw", -90)), 4, "Z")
    P["head"].matrix_world = m
    bpy.context.view_layer.update()


def pose_head(cr, pose):
    """The face box alone, set on its bottom at `at`, its drawn front turned `yaw` degrees (0 faces -y), scaled."""
    P = cr["pivots"]
    x, y, z = pose["at"]
    sc = pose.get("scale", 1.0)
    m = (Matrix.Translation((x, y, z + 0.004)) @ Matrix.Rotation(math.radians(pose.get("yaw", 0)), 4, "Z")
         @ Matrix.Scale(sc, 4))
    P["head"].matrix_world = m
    bpy.context.view_layer.update()


def pose_solo(cr, pose):
    """The right shin alone: it stands on its bottom edge at `at`, its front (the peeled tape) toward -x."""
    P = cr["pivots"]
    cr.setdefault("knee1_basis", P["knee1"].matrix_basis.copy())
    x, y, z = pose["at"]
    sh = DIM["shin"][2]
    m = Matrix.Translation((x, y, z + G / 2 + sh + 0.004)) @ Matrix.Rotation(math.radians(pose.get("yaw", -90)), 4, "Z")
    P["knee1"].matrix_world = m
    bpy.context.view_layer.update()


def _boxes_visibility(cr, hidden, pose):
    root = cr["pivots"]["root"]
    for ob in [root] + list(root.children_recursive):
        ob.hide_render = hidden
    if hidden:
        return
    if pose.get("headonly"):
        keep = {cr["head"]} | {o for o in cr["pivots"]["head"].children_recursive if o.name.startswith(f"{cr['name']}.jt.head")}
        for ob in root.children_recursive:
            if ob.type == "MESH":
                ob.hide_render = ob not in keep
        return
    if pose.get("solo"):
        shin = next(o for o in cr["meshes"] if o.name.endswith(".shin1"))
        keep = {shin, next(o for o in cr["meshes"] if o.name == "boxes.peel")}
        keep |= {o for o in cr["pivots"]["knee1"].children_recursive if o.name.startswith("boxes.jt.knee1")}
        for ob in root.children_recursive:
            if ob.type == "MESH":
                ob.hide_render = ob not in keep
        return
    n = int(pose.get("neck", 0))
    for k, (pv, ob) in enumerate(cr["neck"]):
        for o in [ob] + [c for c in pv.children if c.name.startswith(f"{cr['name']}.jt.n")]:
            for oo in [o] + list(o.children_recursive):
                oo.hide_render = k >= n


def animate_boxes(kit, story, tl, t, ctx, over):
    cr = ctx.get("boxes")
    c = _last(_cues(tl, "boxes"), t)
    hidden = c is None or c.get("hidden", False)
    pose_name = c.get("pose", "stand") if c else "stand"
    pose = POSES[pose_name] if isinstance(pose_name, str) else pose_name
    _boxes_visibility(cr, hidden, pose)
    over["face key"] = over["body key"] = 0.0
    if hidden:
        return
    key = (str(pose_name), c.get("face", "frown"))
    PC["h"] = pose.get("ceil", CEIL)
    if ctx.get("posed") != key:
        if not pose.get("solo") and "knee1_basis" in cr:
            cr["pivots"]["knee1"].matrix_basis = cr.pop("knee1_basis")
            bpy.context.view_layer.update()
        if pose.get("solo"):
            pose_solo(cr, pose)
        elif pose.get("headonly"):
            pose_head(cr, pose)
        else:
            pose_boxes(cr, pose)
        if not pose.get("solo"):
            set_face(cr, c.get("face", "frown"), ctx["wd"], bool(pose.get("flip", False)), bool(pose.get("mirror", False)))
        ctx["posed"] = key
        if __import__("os").environ.get("MD_SHIN") and not pose.get("shelf"):
            sh_ = next(o for o in cr["meshes"] if o.name.endswith(".shin1"))
            print("SHIN", pose_name, [[round(x, 4) for x in r] for r in sh_.matrix_world], flush=True)
        lo, hi, face, fz = boxes_extent(cr)
        print(f"boxes {pose_name}: feet {lo:.3f} m, top {hi:.3f} m (ceiling {CEIL}), face box at {face}, its lowest "
              f"point {fz:.3f} m, legs folded {cr.get('crouch', 0):.1f} deg, stands at {cr.get('at')}", flush=True)
        if __import__("os").environ.get("MOVING_DAY_PROBE"):
            probe(ctx)
    eye = eye_line(cr, bool(pose.get("flip", False)))
    kit.aim(ctx["kick"], eye)
    if pose.get("headonly"):
        over["body key"] = 0.0
        over["face key"] = float(pose.get("key_gain", 0.0))
        return
    if pose.get("key"):
        fk = ctx["face key"]
        fk.location = pose["key"]
        kit.aim(fk, eye)
        over["face key"] = float(pose.get("key_gain", 1.0))
    over["body key"] = 0.0
    if pose.get("body_key"):
        bk = ctx["body key"]
        bk.location = pose["body_key"]
        kit.aim(bk, V(pose["body_aim"]) if pose.get("body_aim") else cr["pivots"]["spine1"].matrix_world.translation)
        over["body key"] = float(pose.get("body_gain", 1.0))


def animate_props(kit, story, tl, t, ctx):
    sc = ctx.get("suitcase")
    if sc is not None:
        lod = bpy.data.objects.get("lod")
        on = lod is not None and not lod.hide_render
        sc.hide_render = not on
        for o in sc.children:
            o.hide_render = not on
        if on:
            sc.matrix_world = _rig_frame("lod", (0.0, 0.0, -2.35), "arm1")
    sqc = _last(_cues(tl, "sqlight"), t)
    for ob in ctx.get("sqlight", []):
        ob.hide_render = not (sqc and sqc.get("on", False))
    # the stack by the door: how many are left (the clock), the eyes on them (L27 to L35), the clean squares in
    # the dust (only once the floor is bare)
    c = _last(_cues(tl, "stack"), t) or {}
    hide = set(c.get("hide", [])) | {FACE_K}
    for k, b in enumerate(ctx["stack"]):
        b["ob"].hide_render = k in hide
        if b["slot"].image != b["base"]:
            b["slot"].image = b["base"]
    ctx["clean"].hide_render = not c.get("clean", False)
    ctx["dust"].hide_render = not c.get("dust", False)
    # the loose boxes in the front room, the same eyes on them; one is Mum's seat at L68
    c = _last(_cues(tl, "loose"), t) or {"on": True}
    for k, b in enumerate(ctx["loose"]):
        on = c.get("on", True)
        b["ob"].hide_render = not (k in on if isinstance(on, list) else on)
        img = ctx["mark_imgs"]["eyes" if c.get("eyes") else "none"]
        if b["slot"].image != img:
            b["slot"].image = img
        if k == 0 and c.get("seat"):
            b["ob"].location = tuple(c["seat"][:2]) + (0.2,)
            b["ob"].rotation_euler = (0, 0, math.radians(c["seat"][2] if len(c["seat"]) > 2 else 0))
        else:
            b["ob"].location = b["home"]
            b["ob"].rotation_euler = (0, 0, b["yaw"])
    # the quilt's box: its flaps folded shut over the quilt (open 1 -> 0), then pushed toward the stack
    cs = _cues(tl, "quiltbox")
    qb, flaps = ctx["quiltbox"]
    last = _last(cs, t) or {}
    _show([qb], not last.get("hidden", False))
    op = float(_eased(cs, "open", t, 1.0))
    push = float(_eased(cs, "push", t, 0.0))
    qb.location = (-3.0, -3.9 - 0.45 * push, 0.0)
    for hg, nrm, k in flaps:
        axis = nrm.cross(V((0, 0, 1)))
        shut = 90.0 if k >= 2 else 87.5          # the short flaps fold first, the long ones over them
        stagger = 0.0 if k >= 2 else 0.25        # ...and a moment later
        u = min(1.0, max(0.0, (1.0 - op - stagger) / (1.0 - stagger))) if k < 2 else min(1.0, (1.0 - op) / 0.75)
        ang = -25.0 + (shut + 25.0) * u
        hg.rotation_euler = Matrix.Rotation(math.radians(ang), 3, axis).to_euler()
    # the photos ride up the front room's west wall with the ceiling (their stretch is the ceiling's over LOW); the
    # old house's frame (0) is in Mum's hands in the kitchen (L05), then hangs on the wall (L08 on)
    f = ctx["ceil_h"] / LOW
    oh = _last(_cues(tl, "oldhouse"), t) or {"where": "wall", "look": "dim"}
    img = ctx["oh_imgs"][oh.get("look", "dim")]
    if ctx["oh_tex"].image != img:
        ctx["oh_tex"].image = img
    for k, g in enumerate(ctx["photos"]):
        y, z = PHOTO_LOW[k]
        g.scale = (1 + 0.3 * (f - 1),) * 3
        g.location, g.rotation_euler = (FRONT[0] + 0.012 + 0.0 * k, y, z * f), (0, 0, math.radians(90))
        if k == 0:
            where = oh.get("where", "wall")
            g.hide_render = where == "none"
            for o in g.children_recursive:
                o.hide_render = where == "none"
            if where == "hand":
                fr = _rig_frame("mum", (0, -1.45, 3.1))
                if fr is not None:
                    g.scale = (1, 1, 1)
                    g.matrix_world = fr
    # the mug: on the sill, in a hand, on the counter, or nowhere
    c = _last(_cues(tl, "mug"), t) or {"where": "sill"}
    mug = ctx["mug"]
    where = c.get("where", "sill")
    _show([mug], where != "none")
    if where == "sill":
        mug.matrix_world = Matrix.Translation(SILL) @ Matrix.Rotation(math.radians(110), 4, "Z")   # the handle toward the room
    elif where == "counter":
        mug.matrix_world = Matrix.Translation(tuple(c.get("pos", (0.95, -3.55))) + (COUNTER["z"],)) @ Matrix.Rotation(math.radians(110), 4, "Z")
    elif where == "hand":
        f = _rig_frame(c.get("who", "mum"), (0.0, -0.2, -1.85), c.get("arm", "arm-1"))
        if f is not None:
            mug.matrix_world = f @ Matrix.Translation((0, 0, -0.03))
    # the tape: five full rolls in a heap (morning 2), the same five as bare cores in a row (from L34c), then gone
    c = _last(_cues(tl, "tape"), t) or {"state": "heap"}
    _show(ctx["rolls"], c.get("state") == "heap")
    _show(ctx["cores"], c.get("state") == "row")
    # the kettle, to the sink's right until L73, then on its left
    c = _last(_cues(tl, "kettle"), t) or {"side": "right"}
    ctx["kettle"].location = (*KETTLE[c.get("side", "right")], COUNTER["z"])
    # the coats on their hooks (L73), the folded boxes in the hall (L75)
    _show(ctx["coats"], (_last(_cues(tl, "coats"), t) or {}).get("on", False))
    _show([ctx["pile"]], (_last(_cues(tl, "pile"), t) or {}).get("on", False))
    # the quilt on Mum's bed (L48 to L62), then round her shoulders (L64 on)
    _show([ctx["quilt"]], (_last(_cues(tl, "bedquilt"), t) or {}).get("on", False))
    cape_on = (_last(_cues(tl, "cape"), t) or {}).get("on", False)
    mum_up = bpy.data.objects.get("mum") is not None and not bpy.data.objects["mum"].hide_render
    _show([ctx["cape"]], cape_on and mum_up)
    if cape_on and mum_up:
        f = _rig_frame("mum", (0, 0, 2.0), "torso")
        ctx["cape"].matrix_world = f
    # a box I carry: held in front of my chest
    c = _last(_cues(tl, "carry"), t) or {}
    who = c.get("who", "me")
    on = bool(c.get("on", False)) and bpy.data.objects.get(who) is not None and not bpy.data.objects[who].hide_render
    ctx["carry"].hide_render = not on
    if on:
        ctx["carry"].matrix_world = _rig_frame(who, (0, -1.35, 3.05))
    # the doors, each eased over its cue's "dur"
    for name, (g, a0, a1) in ctx["doors"].items():
        cs = [c_ for c_ in _cues(tl, "door") if c_.get("door") == name]
        lvl = float(_eased(cs, "open", t, 1.0 if name in ("mum", "mine") else 0.0))
        d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        g.rotation_euler = (0, 0, a0 + d * lvl)


def animate_people(kit, story, tl, t, ctx):
    """Acting keys acting.py doesn't know: lying down, sitting, limbs hidden under a quilt or duvet, a part moved
    in its parent. Each holds until a later key sets it again (null clears it)."""
    base = ctx.setdefault("part_base", {})
    for who, keys in tl.get("acting", {}).items():
        root = bpy.data.objects.get(who)
        if root is None:
            continue
        lie = _switch(keys, "lie", t, None)
        if lie:
            root.rotation_euler = _rot(lie)
        w = _switch(keys, "width", t, None)
        if w:
            root.scale.x = root.scale.y * float(w)
        offs = _switch(keys, "part_offset", t, None) or {}
        for name in [n for n in base if n.startswith(f"{who}.")]:
            if name[len(who) + 1:] not in offs:
                bpy.data.objects[name].location = base[name]
        for part, off in offs.items():
            ob = bpy.data.objects.get(f"{who}.{part}")
            if ob is not None:   # from the part's built place; rig parts sit in rig units under a scaled root
                b0 = base.setdefault(ob.name, tuple(ob.location))
                ob.location = (b0[0] + off[0] / RIG_S, b0[1] + off[1] / RIG_S, b0[2] + off[2] / RIG_S)
        for part in _switch(keys, "hide_parts", t, None) or []:
            ob = bpy.data.objects.get(f"{who}.{part}")
            if ob is not None:
                for o in [ob] + list(ob.children_recursive):
                    o.hide_render = True
        if _switch(keys, "sit", t, False):   # R6 sitting: both legs straight out in front
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (math.radians(-90), 0, 0)
    # her hair fanned on the pillow, and her own fill, only while she lies in bed (dressed the first time she does)
    mum = bpy.data.objects.get("mum")
    lying = mum is not None and not mum.hide_render and bool(_switch(tl["acting"].get("mum", []), "lie", t, None))
    if lying and not ctx.get("mum_dressed"):
        dress_mum(kit, story, ctx)
    if ctx.get("fan"):
        _show(ctx["fan"], lying)
    if not ctx.get("me_lit") and bpy.data.objects.get("me.headm") is not None:
        light_only(kit, "me lit", "me fill", [bpy.data.objects["me.headm"]])
        ctx["me_lit"] = True
    if not ctx.get("glow_linked") and bpy.data.objects.get("me") is not None:
        # me in the hall at 3 a.m.: the glow from her door reaches me too
        col = bpy.data.collections.get("hall glow")
        for ob in bpy.data.objects["me"].children_recursive:
            if ob.type == "MESH" and ob.name not in col.objects:
                col.objects.link(ob)
        for co in col.collection_objects:
            co.light_linking.link_state = "INCLUDE"
        ctx["glow_linked"] = True


CEIL_LIGHTS = ("hall fill", "window edge", "fill mum", "fill mine", "fill hall", "fill front", "fill kitchen",
               "day mum", "day mine", "day hall", "day front", "day kitchen")


def animate_ceiling(kit, ctx, h):
    """The ceiling at h: the wall pieces under it are stretched to meet it, the ceiling slabs and roses ride on it, and
    the lights fixed to it go with it. (The walls were built at CEIL.)"""
    for ob, z0 in TOPS:
        hn = h - z0
        ob.hide_render = hn < 0.02
        if hn >= 0.02:
            ob.scale.z = hn / (CEIL - z0)
            ob.location.z = z0 + hn / 2
    for ob, z in CEILS:
        ob.location.z = z + (h - CEIL)
    lz = ctx.setdefault("lz", {})
    for nm in CEIL_LIGHTS:
        L = kit.LIGHTS.get(nm)
        if L is not None:
            lz.setdefault(nm, L["obj"].location.z)
            L["obj"].location.z = lz[nm] + (h - CEIL)


def animate(kit, story, tl, t, ctx):
    over = {}
    dbg = __import__("os").environ.get("MOVING_DAY_CAM")   # look-dev only: "x,y,z,tx,ty,tz,lens" replaces the shot
    if dbg:
        v = [float(x) for x in dbg.split(",")]
        for s in story["shots"]:
            s["cam"] = [[0, v[0:3], v[3:6], v[6]]]
    ctx["ceil_h"] = h = float(_eased(_cues(tl, "ceil"), "h", t, LOW))
    animate_ceiling(kit, ctx, h)
    animate_people(kit, story, tl, t, ctx)
    bpy.context.view_layer.update()   # the cast was just posed: their parts' places, for the props they hold
    animate_props(kit, story, tl, t, ctx)
    animate_boxes(kit, story, tl, t, ctx, over)
    # the light: the time of day, then the practicals' switches on top
    gains, colour, strength = _time_state(kit, tl, t)
    cs = [c for c in _cues(tl, "time") if c["t"] <= t + 1e-9]
    bpy.context.scene.view_settings.exposure = (cs[-1].get("exposure", EXPOSURE[cs[-1]["set"]]) if cs
                                                 else EXPOSURE["dawn"])
    ctx["M"]["_ceil_emit"].default_value = {"day": 0.35, "sun": 0.35, "end": 0.35, "dawn": 0.3}.get(cs[-1]["set"] if cs else "day", 0.0)
    ctx["outside"].inputs["Color"].default_value = colour
    ctx["outside"].inputs["Strength"].default_value = strength
    nc = _last(_cues(tl, "nightlight"), t)
    night_on = 1.0 if (nc.get("on", True) if nc else True) else 0.0
    lamp = float(_eased(_cues(tl, "lamp"), "on", t, 0.0))
    xc = _last(_cues(tl, "xfill"), t)
    if xc and xc.get("gain", 0.0) > 0:
        xf = ctx["xfill"]
        xf.location = xc["pos"]
        kit.aim(xf, xc["aim"])
        xf.data.size = xc.get("size", 0.9)
        gains = {**gains, "xfill": float(xc["gain"])}
    for name in kit.LIGHTS:
        g = gains.get(name, 0.0)
        if name in ("nightlight", "nightlight kick", "nightlight rim", "door glow"):
            g *= night_on
        if name == "lamp":
            g *= lamp
        if name in ("face key", "body key"):
            g *= over.get(name, 0.0)
        over[name] = g
    # the lampshade glows a little once the lamp is on
    return over
