"""Writes ../story.json for ep35 "Fire ring" (script.md, 2026-11-02).

Run from anywhere: python stories/ep35-fire-ring/generator/make_story.py
The words are in lines.json next to this file (every line of the script, plus the spare L07b). Everything else is
here: the cast, the shots, the acting, the cues set.py reads, the score and the sound.

Places (set.py's coordinates, metres): the ring's middle is (0, 0), ground z = 0 there. Seats: Grandad's south
(0, -1.9), mine north (0, 1.9), the empty slab west (-1.9, 0). The tent is 3 m west (x = -4.6), its door facing south.
Three stepping stones run east: (4, 0), (6, 0.5), (8, 0.2). The hill falls away south to the wall (y = -40) and its
gate (x = -1.4). Grandad's front door is far east at (300, 0). A character facing -y has yaw 0, facing +x yaw 90,
facing -x yaw -90, facing +y yaw 180.
"""
import ast
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# ---------------------------------------------------------------------------------------------- the ground
# set.py's ground() and constants, read from the file (it imports bpy, so it can't be imported here)
_src = (HERE.parent / "set.py").read_text()
_ns = {"math": math}
for node in ast.parse(_src).body:
    if isinstance(node, ast.FunctionDef) and node.name in ("ground", "_ss"):
        exec(compile(ast.Module([node], []), "set.py", "exec"), _ns)
    elif isinstance(node, ast.Assign):
        names = [n.id for t in node.targets for n in ast.walk(t) if isinstance(n, ast.Name)]
        if any(n in ("SEAT_TOP", "SLAB_TOP", "WALL_Y", "GATE_X", "TENT_X", "TENT_Y", "TENT_W", "TENT_L", "TENT_H", "HEARTH_TOP")
               for n in names):
            exec(compile(ast.Module([node], []), "set.py", "exec"), _ns)
ground = _ns["ground"]
SEAT_TOP, SLAB_TOP, WALL_Y, GATE_X = _ns["SEAT_TOP"], _ns["SLAB_TOP"], _ns["WALL_Y"], _ns["GATE_X"]
TENT_X, TENT_Y = _ns["TENT_X"], _ns["TENT_Y"]
HEARTH_TOP = _ns["HEARTH_TOP"]
GZ = ground(0.0, WALL_Y)                  # the ground at the wall
POST_H = 1.35
POST_TOP = GZ + POST_H
HOME = (300.0, 0.0)


def P(x, y, dz=0.0):
    return [round(x, 3), round(y, 3), round(ground(x, y) + dz, 3)]


def W(x, y, h):
    """A camera or target point h metres over the ground."""
    return [round(x, 3), round(y, 3), round(ground(x, y) + h, 3)]


SIT_Z = round(SEAT_TOP - 0.51, 3)         # a seated root over a seat stone: thighs on its top


def sit_g(x=0.0):
    return [x, -2.02, SIT_Z]


def sit_m(x=0.0):
    return [x, 2.02, SIT_Z]


# ---------------------------------------------------------------------------------------------- cameras
def c(*keys):
    return [list(k) for k in keys]


def C(loc, tgt, lens, loc2=None, tgt2=None, lens2=None):
    """A camera: one key, or a move to a second over the shot."""
    if loc2 is None:
        return c([0, loc, tgt, lens])
    return c([0, loc, tgt, lens], [1, loc2, tgt2 if tgt2 is not None else tgt, lens2 if lens2 is not None else lens])


# ---------------------------------------------------------------------------------------------- the cast
cast = {
    # me: a young adult. Dark block hair, a moss-green fleece with a cream band at the neck, a knitted beanie
    "me": {"age": "adult", "skin": "#c68a60", "shirt": "#4f6a3a", "pattern": "solid", "collar": "#e8dcc0",
           "pants": "#343a48", "shoes": "#4a3a2a", "sleeves": "long", "hair": "cap", "hair_c": "#1e1612",
           "hat": "beanie", "hat_c": "#d9a23a", "face": {"eyes": "round", "brows": True, "ink": "#1a1210"}},
    # Dad: grey at the sides, a stiff brand-new orange waterproof, grey walking trousers
    "dad": {"age": "adult", "skin": "#d9a47c", "shirt": "#f06a1c", "pattern": "solid", "collar": "#c9540f",
            "pants": "#6a6d72", "shoes": "#3a2e24", "sleeves": "long", "hair": "cap", "hair_c": "#8a8884",
            "extras": ["coat", "hooddown"], "zip_c": "#2a2a2e",
            "face": {"eyes": "round", "brows": True, "ink": "#1a1210"}},
    # Grandad: white hair, a flat cap, a brown tweed-check jumper, glasses
    "grandad": {"age": "adult", "skin": "#e0b690", "shirt": "#7a5a3a", "pattern": "plaid", "pattern_c": "#3e2e1e",
                "pants": "#4a4a42", "shoes": "#2e241c", "sleeves": "long", "hair": "cap", "hair_c": "#ecebe6",
                "hat": "ballcap", "hat_c": "#6a5a42", "extras": ["glasses"],
                "face": {"eyes": "round", "brows": True, "ink": "#1a1210", "cheeks": "#d9907a"}},
    # Big Hands: ordinary height, a heather-purple knit jumper, peat-brown trousers and boots, a muted heath-tan head
    # with a small calm half-lidded face set low (set.py adds the tall head, the mitten hands, the catch points)
    "bighands": {"age": "adult", "skin": "#b8a27c", "shirt": "#6c4a9a", "pattern": "knit", "pattern_c": "#4a3426",
                 "pants": "#4a3426", "shoes": "#3a281c", "sleeves": "long", "hair": "none",
                 "face": {"eyes": "tired", "brows": False, "ink": "#2a1e14", "glow": "#ff8a3d", "pupil": "#1c130c"}},
}

# ---------------------------------------------------------------------------------------------- shots
GRAND = C  # (alias for readability)
SH = [
    # ---- 01 the taste
    (0, C([0.62, -0.25, 0.92], [0.02, 2.0, 0.98], 34), {}),                                   # S01 the mug in the firelight
    ("L01.1", C([0.62, 0.2, 0.3], [0.14, 1.02, 0.13], 40), {}),                           # S02 me chewing over it
    ("L02", C([0.55, 1.35, 1.2], [0.0, -2.0, 1.0], 38), {}),                                # S03 Dad across the fire
    ("L03", C([3.4, -22.0, 1.2], [-2.3, -12.6, 1.25], 30, [3.4, -20.0, 1.2], [-2.3, -9.0, 1.3], 30), {"hand": 0.004}),   # S04
    ("L03.3", C([-1.2, -5.2, 0.8], [0.0, 0.0, 0.6], 30, [-1.2, -4.0, 0.8], [0.0, 0.0, 0.6], 34), {}),                   # S05
    ("L04", C([7.4, -6.6, 6.2], [0.0, 0.2, 0.4], 30), {}),                                  # S06 high wide of the three seats
    ("L05", C([-0.55, 0.6, 0.98], [-1.9, 0.05, 0.78], 42), {}),                             # S07 the phone on the empty seat
    ("L05.3", C([-1.25, 0.05, 1.18], [0.0, -2.0, 1.0], 38), {}),                            # S08 Grandad laughing
    ("L06", C([1.5, -0.45, 1.0], [-0.55, -0.4, 0.78], 26), {}),                             # S09 Grandad pouring
    ("L06.2", C([0.25, -0.5, 0.8], [-0.3, 0.0, 0.3], 42), {}),                              # S10 the stew, the flask
    ("L07", C([HOME[0], -5.3, 1.5], [HOME[0], -0.5, 1.3], 34), {}),                         # S11 Grandad at his door
    ("L07b", C([HOME[0] + 0.7, -4.2, 1.3], [HOME[0], -0.5, 1.35], 42, [HOME[0] + 0.3, -3.0, 1.3], [HOME[0], -0.5, 1.4], 44), {}),   # S12
    # ---- 02 night one
    ("L08", C([-4.8, -12.6, 1.1], [-6.4, -8.4, 1.2], 26, [-2.2, -12.4, 1.1], [-3.6, -8.1, 1.2], 26), {}),                              # S13 Dad on the path
    ("L09", C([2.8, -4.9, 1.3], [-3.8, -0.8, 0.9], 30), {}),                                # S14 the tent up
    ("L10-0.45", C([2.5, 0.7, 1.1], [0.0, -2.0, 0.8], 34), {}),                                  # S15 Dad sits on Grandad's seat
    ("L10.1", C([0.9, -0.5, 1.05], [0.0, 2.0, 1.0], 34), {}),                               # S16 me angry
    ("L10.1+0.8", C([2.3, -2.7, 1.35], [0.45, -1.4, 0.62], 30), {}),                           # S17 Dad's back, the pack, the flask
    ("L12", C([-0.5, -0.55, 0.9], [-0.5, 0.15, 0.08], 28), {}),                             # S18 THE LORE PLANT (set at "L11>-0.35")
    ("L13", C([1.3, 0.35, 0.98], [-0.1, 2.0, 1.02], 32), {}),                               # S19 my face over the mug
    ("L14", C([0.2, -1.0, 1.4], [-2.6, -12.5, -0.3], 30), {}),                              # S20 Dad down the hill
    ("L15", C([-0.7, -0.6, 0.92], [0.0, 2.0, 1.0], 34), {}),                                # S21 me looking east
    ("L16", C([1.8, 0.15, 0.3], [8.5, 0.35, 0.25], 26, [2.6, 0.15, 0.3], [8.5, 0.35, 0.25], 26), {}),   # S22 low along the stones
    ("L17", C([0.0, 1.7, 1.12], [8.0, 0.2, 1.2], 32), {}),                                 # S23 my POV: small on the farthest stone
    ("L18", C([4.8, 1.55, 1.25], [8.0, 0.2, 1.25], 36), {}),                                # S24 medium
    ("L19", C([5.0, 0.2, 1.05], [7.2, 0.2, 1.1], 18), {}),                                # S25 the hands fill the frame
    ("L19.2", C([-4.6, -4.5, 0.75], [-4.6, -1.3, 0.66], 30), {}),                          # S26 the tent door for scale
    ("P01", C([0.4, -0.5, 1.05], [0.0, 2.0, 1.02], 36), {}),                                # S27 my face, scared
    ("L20", C([2.0, -3.3, 1.2], [-1.8, -1.2, 1.0], 32), {}),                                # S28 Dad into the firelight
    ("L20.1", C([0.0, 1.7, 1.12], [8.0, 0.2, 1.1], 32), {}),                               # S29 the empty farthest stone
    ("L21", C([-0.2, 1.0, 1.15], [1.5, -1.3, 0.85], 34), {}),                                 # S30 Dad banking the fire
    ("L21>-0.3", C([0.6, -0.45, 1.0], [0.0, 2.2, 1.05], 30), {}),                                 # S31 me
    ("L22.1", C([-0.5, 0.95, 1.0], [0.0, -2.0, 0.98], 34), {}),                             # S32 Dad
    # ---- 03 night two
    ("L23", C([0.2, -1.0, 1.4], [-2.6, -12.5, -0.3], 30), {}),                              # S33
    ("L24", C([0.0, 1.7, 1.12], [6.0, 0.5, 1.2], 32), {}),                                 # S34 middle stone
    ("L25", C([1.0, 1.5, 1.2], [6.0, 0.5, 1.3], 40, [3.5, 1.1, 1.35], [6.0, 0.5, 1.45], 48), {}),     # S35 the push
    ("L26", C([4.5, 1.1, 1.58], [6.0, 0.5, 1.58], 46), {}),                                 # S36 its face
    ("L27", C([7.6, 2.6, 1.6], [0.0, 0.1, 0.7], 30), {}),                                  # S37 over its shoulder
    ("L27.1", C([1.0, 1.2, 0.9], [-1.9, 0.0, 0.55], 32), {}),                              # S38 the empty seat
    ("L28", C([-1.9, -4.2, 1.25], [-4.2, -2.2, 0.95], 32), {}),                              # S39 Dad turns the tent door
    ("L29", C([-4.6, -0.5, 1.15], [-4.6, 0.95, 0.3], 26), {}),                              # S40 inside, me awake
    ("L30", C([-4.6, 0.45, 1.0], [-4.6, 1.0, 0.3], 40), {}),                             # S41 my eyes
    # ---- 04 night three, the scare
    ("L31", C([-0.9, -0.9, 0.42], [4.0, 0.0, 1.2], 32), {}),                               # S42 THE REVEAL
    ("L32", C([0.1, 1.35, 0.42], [2.75, 0.68, 1.15], 38), {}),                                # S43 the fingertips
    ("L33", C([-4.6, 0.3, 0.75], [-4.6, -1.3, 0.62], 36), {}),                              # S44 frost on the door
    ("L33.2", C([-4.6, -0.9, 1.7], [-4.6, -0.15, 1.1], 22), {}),                          # S45 me sitting up
    ("L34", C([1.1, -1.25, 0.6], [0.3, 0.0, 0.12], 34), {}),                                # S46 the embers
    ("L35", C([-4.0, 0.3, 0.5], [-5.4, 0.45, 0.95], 24, [-4.1, 0.3, 0.5], [-5.4, 0.45, 1.0], 24), {}),   # S47 the wall, dark then glowing
    ("L37", C([-4.35, 0.2, 1.0], [-5.5, 0.2, 0.62], 12), {}),                                # S48 the two hands
    ("L38", C([-4.2, 0.2, 0.8], [-5.4, 0.95, 0.7], 20), {}),                             # S49 over Dad
    ("L39", C([-4.6, -0.9, 1.7], [-4.6, -0.15, 1.1], 22), {}),                              # S50 my face, orange on it
    ("L40", C([1.0, -3.4, 0.6], [-2.3, 0.1, 1.05], 38), {}),                               # S51 the exterior
    ("L41", C([-4.6, -0.85, 1.7], [-4.6, -0.15, 1.2], 30), {}),                              # S52 my eyes shut and open
    ("L42", C([-4.2, 0.2, 0.8], [-5.4, 0.95, 0.3], 20), {}),                              # S53 the finger on the bag (tilted down, clear of the caption band)
    ("L43", C([-5.05, 0.35, 0.78], [-5.3, 0.95, 0.35], 40), {}),                              # S54 Dad's face
    ("L44", C([-4.6, 0.4, 0.95], [-4.6, 1.0, 0.3], 36), {}),                               # S55 me, eyes squeezed shut
    ("L45", C([-4.0, 0.3, 0.5], [-5.4, 0.45, 0.95], 24), {}),                                # S56 the wall goes dark
    ("L46", C([4.4, -3.1, 1.5], [0.0, 0.0, 0.25], 30), {}),                                 # S57 frost
    ("L47", C([1.8, -1.5, 1.0], [-1.9, 0.0, 0.45], 32, [-0.4, -0.9, 0.8], [-1.9, 0.0, 0.5], 32), {}),  # S58 push to the empty seat
    ("L48", C([-1.62, -0.15, 1.95], [-1.9, 0.0, 0.62], 30), {}),                            # S59 top shot: the dry shape
    # ---- 05 the call
    ("L49", C([0.9, -1.2, 1.5], [-1.4, -10.0, 0.5], 30), {}),                               # S60 Dad off again, me following
    ("L50", C(W(2.8, -43.8, 1.6), W(0.9, -39.2, 1.5), 30), {}),                             # S61 me behind the wall
    ("L51", C(W(1.6, -46.0, 1.6), W(-0.45, -40.6, 1.4), 28), {}),                           # S62 the phone on the gatepost
    ("L52", C([2.6, -44.2, POST_TOP + 0.2], [-0.45, -40.0, POST_TOP + 0.05], 50), {}),           # S63 the phone, close
    ("L52.2", C(W(2.5, -43.0, 1.62), W(0.9, -39.2, 1.52), 34), {}),                         # S64 my face
    ("L53", C(W(-2.0, -38.4, 1.45), W(-0.45, -41.3, 1.45), 32), {}),                          # S65 Dad leaning on the post
    ("L54", C(W(-1.2, -38.9, 1.4), W(-0.45, -41.3, 1.5), 44), {}),                           # S66 his face
    ("L55", C(W(-3.0, -39.0, 1.55), W(-0.45, -41.3, 1.45), 38), {}),                        # S67 looking up the hill
    ("L56", C([2.6, -44.2, POST_TOP + 0.2], [-0.45, -40.0, POST_TOP + 0.05], 50), {}),           # S68 the phone
    ("L56>-0.3", C([-0.2, 1.0, 1.15], [1.5, -1.3, 0.85], 34), {}),                                 # S69 the banking, again
    ("L57.1", C([-1.9, -4.2, 1.25], [-4.2, -2.2, 0.95], 32), {}),                            # S70 the tent door, again
    ("L57.2", C([2.4, -43.6, POST_TOP + 0.2], [-0.45, -40.0, POST_TOP + 0.05], 50), {}),          # S71 the glow
    ("L58", C(W(2.2, -42.2, 1.6), W(0.9, -39.2, 1.5), 36), {}),                             # S72 my face behind the wall
    # ---- 06 the fire
    ("L59", C(W(1.2, -44.5, 1.6), W(-0.3, -40.8, 1.1), 28), {}),                            # S73 stepping out
    ("L60", C(W(-0.45, -45.5, 1.4), W(-0.45, -41.5, 1.35), 30), {}),                        # S74 two-shot
    ("L61", C(W(0.4, -44.6, 1.55), W(-1.2, -41.4, 1.5), 34), {}),                           # S75 me
    ("L62", C(W(0.9, -45.5, 1.4), W(0.3, -41.6, 1.2), 32), {}),                             # S76 Dad's boots
    ("L62.1+0.5", C(W(-0.6, -45.2, 1.5), W(0.3, -41.6, 1.5), 36), {}),                          # S77 the smile
    ("L63", C([3.2, -15.8, 0.9], [-0.5, -11.5, 1.2], 28), {}),                              # S78 climbing at sunset
    ("L64", C([0.3, 0.45, 0.95], [-1.9, 0.0, 0.72], 38), {}),                               # S79 one bar
    ("L65", C([0.0, -1.8, 1.1], [0.0, 2.0, 0.95], 22), {}),                                 # S80 us on the seat
    ("L65.1", C([-0.75, -0.7, 0.85], [-1.9, 0.05, 0.72], 40), {}),                          # S81 turning him to the fire
    ("L66", C([0.8, 0.4, 0.55], [9.0, 0.4, 0.3], 24), {}),                                  # S82 the stones, empty
    ("L67", C([0.3, 0.45, 0.95], [-1.9, 0.0, 0.72], 38), {}),                               # S83 the phone laughs
    ("L67.1+0.3", C([0.5, -0.6, 1.1], [0.7, 2.0, 0.95], 36), {}),                               # S84 Dad laughing
    ("L68", C([-0.3, -0.6, 1.1], [-0.7, 2.0, 1.0], 36), {}),                              # S85 my face turns
    ("L69", C([0.9, -0.6, 1.1], [0.7, 2.0, 1.0], 36), {}),                                  # S86 Dad goes red
    ("L69.1", C([-1.1, -1.0, 0.7], [-0.45, -0.2, 0.25], 38), {}),                         # S87 the flask lands
    ("L70", C([2.0, -0.7, 1.15], [-1.2, -0.05, 0.5], 34), {}),                                 # S88 the last frame
]
shots = []
for i, (at, cam, opt) in enumerate(SH):
    s = {"id": f"S{i + 1:02d}", "cam": cam, "step": opt.get("step", 2)}
    if i:
        s["at"] = at
    if "hand" in opt:
        s["hand"] = opt["hand"]
    shots.append(s)
# (the lore plant, S18, starts with L12 and holds 1.9 s: L12 is 1.7 s long and the next shot starts at L13)

# ---------------------------------------------------------------------------------------------- acting


def jump(at, frm, to, **kw):
    """A move on a cut: two keys at the same moment, so nobody walks on film."""
    return [{"at": at, "pos": frm}, {"at": at, "pos": to, "blend": 0.0, **kw}]


SEAT_FACE_N = 180
SEAT_FACE_S = 0
TENT_ME = [TENT_X, -0.55, 0.22]           # lying in my bag (head north)
TENT_DAD = [TENT_X - 0.7, -0.55, 0.22]
TENT_ME_SIT = [TENT_X, -0.15, round(0.4 - 0.51, 3)]
HIDE = [0, 0, -30]

me = [
    # 01: at my seat, chewing
    {"at": 0, "pos": sit_m(), "yaw": 0, "expr": "smirk", "sit": True, "arms": [0, 0], "side": [0, 0], "head": [0, 4], "lean": 0},
    {"from": "L01", "to": "L01>", "mouth": [0.35, 0.35], "flap": True},
    {"at": "L02", "pos": sit_m(), "expr": "neutral"},
    *jump("L03", sit_m(), P(-1.55, -15.5), yaw=0, sit=False, expr="neutral", arms=[0, 0], head=[0, 0]),
    {"at": "L03>", "pos": P(-1.55, -10.4)},
    *jump("L04", P(-1.55, -10.4), sit_m(), yaw=0, sit=True, expr="neutral"),
    {"at": "L05", "pos": sit_m(), "expr": "smirk"},
    *jump("L07", sit_m(), HIDE, hidden=True),
    *jump("L10", HIDE, sit_m(), hidden=False, yaw=0, sit=True, expr="angry"),
    {"at": "L11", "pos": sit_m(), "expr": "angry"},
    {"at": "L13", "pos": sit_m(), "expr": "worried"},
    {"at": "L15", "pos": sit_m(), "expr": "neutral", "yaw": 58, "head": [-18, 2]},
    {"at": "L17", "pos": sit_m(), "expr": "scared", "yaw": 62, "head": [-20, 0]},
    *jump("P01", sit_m(), sit_m(), yaw=0, head=[0, 0], expr="scared"),
    {"at": "L20", "pos": sit_m(), "expr": "worried"},
    {"at": "L22", "pos": sit_m(), "expr": "neutral", "head": [0, 6]},
    {"at": "L23", "pos": sit_m(), "expr": "worried"},
    {"at": "L24", "pos": sit_m(), "yaw": 62, "head": [-20, 0], "expr": "scared"},
    {"at": "L28", "pos": sit_m(), "yaw": 0, "head": [0, 0], "expr": "worried"},
    # the tent: lying awake, then sitting up cold, then lying back
    *jump("L29", sit_m(), TENT_ME, sit=False, lean=-90, yaw=0, expr="worried", blink=False, head=[0, 0]),
    {"at": "L30", "pos": TENT_ME, "expr": "scared"},
    *jump("L33", TENT_ME, TENT_ME_SIT, lean=0, yaw=0, sit=True, expr="scared", blink=True, head=[0, 0]),
    {"at": "L39", "pos": TENT_ME_SIT, "expr": "scared"},
    {"at": "L41+0.2", "pos": TENT_ME_SIT, "expr": "shut"},
    {"at": "L41+0.62", "pos": TENT_ME_SIT, "expr": "scared"},
    *jump("L44", TENT_ME_SIT, TENT_ME, lean=-90, sit=False, yaw=0, expr="squeeze"),
    {"at": "L45", "pos": TENT_ME, "expr": "wide"},
    *jump("L46", TENT_ME, HIDE, hidden=True),
    # the call: following Dad, behind the wall, out by the gate
    *jump("L49", HIDE, P(-0.4, -5.0), hidden=True, lean=0, sit=False, yaw=0, expr="neutral", arms=[0, 0], head=[0, 0]),
    {"at": "L49>", "pos": P(-0.8, -7.0)},
    *jump("L50", P(-0.8, -7.0), P(0.9, -39.3), hidden=False, yaw=0, expr="neutral"),
    {"at": "L52.1", "pos": P(0.9, -39.3), "expr": "wide"},
    {"at": "L58", "pos": P(0.9, -39.3), "expr": "soft"},
    {"at": "L59", "pos": P(0.9, -39.3), "expr": "neutral"},
    {"at": "L59+0.5", "pos": P(-0.2, -39.6)},
    {"at": "L59>", "pos": P(-1.2, -41.5), "yaw": 90, "expr": "neutral"},
    {"at": "L61", "pos": P(-1.2, -41.5), "expr": "soft", "yaw": 90},
    # sunset: climbing, then at the ring
    *jump("L63", P(-1.2, -41.5), P(-1.3, -14.0), yaw=0, expr="soft"),
    {"at": "L63>", "pos": P(-1.3, -9.8)},
    *jump("L64", P(-1.3, -9.8), HIDE, hidden=True),
    *jump("L65", HIDE, sit_m(-0.7), hidden=False, yaw=0, sit=True, expr="soft", arms=[0, 0]),
    {"at": "L68", "pos": sit_m(-0.7), "expr": "wide", "head": [-38, 0], "yaw": 0},
    {"at": "L70", "pos": sit_m(-0.7), "expr": "soft", "head": [0, 0]},
]

dad = [
    {"at": 0, "pos": HIDE, "hidden": True, "yaw": 0, "arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "sit": False},
    *jump("L02", HIDE, sit_g(), hidden=False, yaw=180, sit=True, expr="grin", arms=[0, 0], lean=0),
    *jump("L03", sit_g(), HIDE, hidden=True),
    *jump("L08", HIDE, P(-7.8, -8.6), hidden=False, sit=False, yaw=90, expr="neutral", arms=[0, 0]),
    {"at": "L08>", "pos": P(-3.0, -8.0)},
    *jump("L09", P(-3.0, -8.0), P(-2.6, -3.0), yaw=-125, expr="neutral"),
    *jump("L10", P(-2.6, -3.0), sit_g(), yaw=180, sit=True, expr="grin"),
    {"at": "L10.1", "pos": sit_g(), "expr": "grin"},
    *jump("L11", sit_g(), [-0.3, -1.2, 0.0], sit=False, yaw=180, lean=24, arms=[48, 48], expr="neutral"),
    *jump("L13", [-0.3, -1.2, 0.0], sit_g(), sit=True, yaw=180, lean=0, arms=[0, 0], expr="smirk"),
    *jump("L14", sit_g(), P(-1.2, -5.0), sit=False, yaw=180, expr="neutral", arms=[0, 50]),
    {"at": "L14>", "pos": P(-2.0, -10.5)},
    *jump("L15", P(-2.0, -10.5), HIDE, hidden=True),
    *jump("L20", HIDE, [-3.3, -1.5, 0.0], hidden=False, yaw=90, expr="neutral", arms=[0, 0]),
    {"at": "L20>", "pos": [-1.4, -1.2, 0.0]},
    *jump("L21", [-1.4, -1.2, 0.0], [1.5, -1.3, 0.0], yaw=-131, lean=22, expr="neutral", arms=[28, 28]),
    *jump("L22", [1.5, -1.3, 0.0], sit_g(), sit=True, yaw=180, lean=0, arms=[0, 0], expr="neutral"),
    *jump("L23", sit_g(), P(-1.2, -5.0), sit=False, yaw=180, expr="neutral", arms=[0, 50]),
    {"at": "L23>", "pos": P(-2.0, -10.5)},
    *jump("L24", P(-2.0, -10.5), HIDE, hidden=True),
    *jump("L28", HIDE, [-4.2, -2.2, 0.0], hidden=False, yaw=140, expr="neutral", arms=[0, 0]),
    {"at": "L28>", "pos": [-4.2, -2.2, 0.0], "arms": [0, 30]},
    *jump("L29", [-4.2, -2.2, 0.0], TENT_DAD, lean=-90, yaw=0, expr="asleep", blink=False, arms=[0, 0]),
    *jump("L46", TENT_DAD, HIDE, hidden=True),
    *jump("L49", HIDE, P(-1.2, -5.5), hidden=False, lean=0, yaw=180, expr="neutral", arms=[0, 50]),
    {"at": "L49>", "pos": P(-1.7, -8.8)},
    *jump("L50", P(-1.7, -8.8), P(-0.45, -41.3), yaw=180, arms=[62, 62], lean=18, expr="worried"),
    {"at": "L53", "pos": P(-0.45, -41.3), "head": [0, 14], "expr": "worried"},
    {"at": "L55", "pos": P(-0.45, -41.3), "head": [0, -8]},
    # the replays (L57): banking the fire, the tent door, then the post again
    *jump("L56>-0.3", P(-0.45, -41.3), [1.5, -1.3, 0.0], yaw=-131, lean=22, expr="neutral", arms=[28, 28], head=[0, 0]),
    *jump("L57.1", [1.5, -1.3, 0.0], [-4.2, -2.2, 0.0], yaw=140, lean=0, arms=[0, 30]),
    *jump("L57.2", [-4.2, -2.2, 0.0], P(-0.45, -41.3), yaw=180, arms=[62, 62], lean=18, expr="worried", head=[0, 14]),
    {"at": "L59", "pos": P(-0.45, -41.3), "expr": "wide", "head": [0, 0], "lean": 0, "arms": [0, 0]},
    {"at": "L59+0.5", "pos": P(0.3, -41.6), "yaw": -90},
    {"at": "L60", "pos": P(0.3, -41.6), "yaw": -90, "expr": "neutral"},
    {"at": "L62", "pos": P(0.3, -41.6), "head": [0, 30], "expr": "worried"},
    {"at": "L62.1", "pos": P(0.3, -41.6), "head": [0, 0], "expr": "soft"},
    *jump("L63", P(0.3, -41.6), P(0.1, -14.0), yaw=0, expr="soft", head=[0, 0]),
    {"at": "L63>", "pos": P(0.1, -9.8)},
    *jump("L64", P(0.1, -9.8), HIDE, hidden=True),
    *jump("L65", HIDE, sit_m(0.7), hidden=False, yaw=0, sit=True, expr="soft", arms=[0, 0], lean=0),
    {"at": "L67.1", "pos": sit_m(0.7), "expr": "soft"},
    {"at": "L69", "pos": sit_m(0.7), "expr": "squeeze"},
    *jump("L69.1", sit_m(0.7), [-0.35, -1.0, 0.0], sit=False, yaw=180, lean=20, arms=[0, 78], expr="squeeze"),
    *jump("L70", [-0.35, -1.0, 0.0], sit_m(0.7), sit=True, yaw=0, lean=0, arms=[0, 0], expr="soft"),
]

grandad = [
    {"at": 0, "pos": HIDE, "hidden": True, "yaw": 0, "arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "sit": False},
    *jump("L03", HIDE, P(-3.1, -15.5), hidden=False, yaw=0, expr="neutral", arms=[0, 0], sit=False, lean=0),
    {"at": "L03>", "pos": P(-3.1, -10.4)},
    *jump("L04", P(-3.1, -10.4), sit_g(), yaw=180, sit=True, expr="grin"),
    *jump("L05", sit_g(), sit_g(), yaw=-132, lean=10, expr="smirk", head=[0, 0]),
    *jump("L06", sit_g(), [-0.82, -0.8, 0.0], sit=False, yaw=146, lean=0, arms=[0, 42], expr="smirk"),
    *jump("L07", [-0.82, -0.8, 0.0], [HOME[0], -0.55, 0.18], yaw=0, expr="grin", arms=[0, 150]),
    *jump("L08", [HOME[0], -0.55, 0.18], HIDE, hidden=True),
]

# Big Hands: not there until L17; on the farthest, middle and nearest stones; at the ring at L40
STAND = dict(yaw=-90, arms=[30, 30], side=[16, 16], expr="neutral", sit=False, lean=0, head=[0, 0])
bighands = [
    {"at": 0, "pos": HIDE, "hidden": True, "yaw": 0, "arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "sit": False},
    *jump("L17", HIDE, [8.0, 0.2, 0.05], hidden=False, **STAND),
    *jump("L20", [8.0, 0.2, 0.05], HIDE, hidden=True),
    *jump("L24", HIDE, [6.0, 0.5, 0.05], hidden=False, **STAND),
    {"at": "L27", "pos": [6.0, 0.5, 0.05], "look": [-0.2, 0.0]},
    *jump("L28", [6.0, 0.5, 0.05], HIDE, hidden=True),
    *jump("L31", HIDE, [4.0, 0.0, 0.05], hidden=False, **STAND),
    *jump("L33", [4.0, 0.0, 0.05], HIDE, hidden=True),
    *jump("L40", HIDE, [-2.5, 0.12, 0.0], hidden=False, yaw=90, arms=[40, 40], side=[35, 35], expr="neutral", sit=False, lean=0, head=[0, 8]),
    *jump("L41", [-2.5, 0.12, 0.0], HIDE, hidden=True),
]

acting = {"me": me, "dad": dad, "grandad": grandad, "bighands": bighands}

# ---------------------------------------------------------------------------------------------- cues
PHONE_SEAT = [-1.9, 0.05, SLAB_TOP]
cues = [
    # the light
    {"at": 0, "name": "look", "id": "dusk"},
    {"at": "L03", "name": "look", "id": "memory"},
    {"at": "L07", "name": "look", "id": "home"},
    {"at": "L08", "name": "look", "id": "dusk"},
    {"at": "L23", "name": "look", "id": "dusk2"},
    {"at": "L31", "name": "look", "id": "frostdusk"},
    {"at": "L33", "name": "look", "id": "night"},
    {"at": "L46", "name": "look", "id": "dawn"},
    {"at": "L49", "name": "look", "id": "morning"},
    {"at": "L56>-0.3", "name": "look", "id": "morning"},
    {"at": "L57.2", "name": "look", "id": "morning"},
    {"at": "L63", "name": "look", "id": "sunset"},
    # the fire: out in the morning, embers at night three, lit again for the phone
    {"at": 0, "name": "fire", "level": 1.0},
    {"at": "L34", "name": "fire", "level": 0.2},
    {"at": "L46", "name": "fire", "level": 0.0},
    {"at": "L56>-0.3", "name": "fire", "level": 1.0},
    {"at": "L57.2", "name": "fire", "level": 0.0},
    {"at": "L64", "name": "fire", "level": 1.0},
    # the tent canvas: warm low firelight (L29), cold and dark (L33), the glow (L36), cold moon blue (L45)
    {"at": 0, "name": "glow", "v": 0.0, "mix": 0.0},
    {"at": "L29", "name": "glow", "v": 0.12, "mix": 0.0},
    {"at": "L33", "name": "glow", "v": 0.2, "mix": 1.0},
    {"at": "L36", "name": "glow", "v": 0.32, "mix": 0.0, "dur": 0.6},
    {"at": "L45", "name": "glow", "v": 0.26, "mix": 1.0, "dur": 1.5},
    {"at": "L46", "name": "glow", "v": 0.0, "mix": 1.0},
    {"at": 0, "name": "tentlight", "v": 0.0, "fill": 0.0},
    {"at": "L29", "name": "tentlight", "v": 0.5, "fill": 0.3},
    {"at": "L33", "name": "tentlight", "v": 0.0, "fill": 2.2},
    {"at": "L36", "name": "tentlight", "v": 1.0, "fill": 0.4, "dur": 0.6},
    {"at": "L45", "name": "tentlight", "v": 0.0, "fill": 1.2, "dur": 1.5},
    {"at": "L46", "name": "tentlight", "v": 0.0, "fill": 0.0},
    {"at": "L57.1", "name": "tentlight", "v": 0.0, "fill": 0.0},
    {"at": "L37", "name": "shadow", "mode": "hands"},
    {"at": "L42", "name": "shadow", "mode": "finger"},
    {"at": "L44", "name": "shadow", "mode": "none"},
    {"at": 0, "name": "shadow", "mode": "none"},
    {"at": "L33", "name": "doorfrost", "on": True},
    {"at": "L33.1", "name": "doorfrost", "on": False},
    {"at": "L46", "name": "dry", "on": True},
    {"at": "L49", "name": "dry", "on": False},
    {"at": 0, "name": "gate", "deg": 0.0},
    {"at": "L50", "name": "gate", "deg": 92.0},
    {"at": "L63", "name": "gate", "deg": 92.0},
    {"at": "L21", "name": "turves", "on": True},
    {"at": "L33", "name": "turves", "on": True},
    {"at": 0, "name": "flare", "v": 2.2},
    {"at": "L02", "name": "flare", "v": 0.0},
    {"at": 0, "name": "hkey", "v": 1.0},
    {"at": "L40", "name": "hkey", "v": 0.12},
    # L40: an ember-orange low light under the hands, so the creature is lit from below (round 1)
    {"at": "L40", "name": "flare", "v": 0.35, "pos": [-1.3, 0.1, 0.18]},
    {"at": "L41", "name": "flare", "v": 0.0},
    # L19.2: the tent door is lifted out of black so the size comparison reads (round 1)
    {"at": "L40", "name": "exposure", "v": 0.45},
    {"at": "L41", "name": "exposure", "v": -0.2},
    {"at": "L42", "name": "exposure", "v": 0.0},
    {"at": "L63", "name": "exposure", "v": 0.4},
    {"at": "L69", "name": "exposure", "v": 0.7},
    {"at": "L19.2", "name": "doorlit", "v": 3.5},
    {"at": "P01", "name": "doorlit", "v": 0.0},
    {"at": "L41", "name": "hkey", "v": 1.0},
    # Big Hands' palms: tipped at the fire, flat over the embers at L40
    {"at": 0, "name": "handtilt", "deg": -150.0},
    {"at": "L40", "name": "handtilt", "deg": -60.0},
    # props. The mug on a ring stone's side; the phone; the dented flask; the pack; Grandad's stick
    {"at": 0, "name": "mug", "pos": [0.18, 1.06, 0.0]},
    {"at": "L02", "name": "mug", "hidden": True},
    {"at": "L12", "name": "mug", "pos": [0.55, 1.2, 0.0]},
    {"at": 0, "name": "phone", "hidden": True},
    {"at": "L05", "name": "phone", "pos": PHONE_SEAT, "yaw": 58, "tilt": -18},
    {"at": "L06", "name": "phone", "hidden": True},
    {"at": "L14", "name": "phone", "hand": "dad.arm1", "offset": [0.0, 0.0, 0.0], "tilt": -80, "yaw": 90},
    {"at": "L15", "name": "phone", "hidden": True},
    {"at": "L23", "name": "phone", "hand": "dad.arm1", "offset": [0.0, 0.0, 0.0], "tilt": -80, "yaw": 90},
    {"at": "L24", "name": "phone", "hidden": True},
    {"at": "L49", "name": "phone", "hand": "dad.arm1", "offset": [0.0, 0.0, 0.0], "tilt": -80, "yaw": 90, "glow": 7.0, "scale": 3.5, "halo": True},
    {"at": "L50", "name": "phone", "pos": [-0.45, -40.0, POST_TOP], "yaw": 0, "tilt": -12},
    {"at": "L56>-0.3", "name": "phone", "hidden": True},
    {"at": "L57.2", "name": "phone", "pos": [-0.45, -40.0, POST_TOP], "yaw": 0, "tilt": -12},
    {"at": "L63", "name": "phone", "hand": "dad.arm1", "offset": [0.0, 0.0, 0.0], "tilt": -60, "yaw": 0},
    {"at": "L64", "name": "phone", "pos": PHONE_SEAT, "yaw": 78, "tilt": -18},
    {"at": "L65.1", "name": "phone", "pos": PHONE_SEAT, "yaw": 90, "tilt": -18},
    {"at": 0, "name": "flask", "hidden": True},
    {"at": "L06", "name": "flask", "hand": "grandad.arm1", "offset": [0.25, -0.25, 0.0], "tilt": 60, "yaw": 270},
    {"at": "L07", "name": "flask", "hidden": True},
    {"at": "L09", "name": "flask", "pos": [0.78, -1.42, 0.5], "yaw": 0, "tilt": 0},
    {"at": "L13", "name": "flask", "pos": [0.78, -1.42, 0.5], "yaw": 0, "tilt": 0},
    {"at": "L14", "name": "flask", "hidden": True},
    {"at": "L69", "name": "flask", "hand": "dad.arm1", "offset": [0.0, 0.0, 0.0], "tilt": 0},
    {"at": "L69.1", "name": "flask", "pos": [-0.5, -0.28, HEARTH_TOP], "yaw": -90, "tilt": 0},
    {"at": 0, "name": "pack", "hidden": True},
    {"at": "L08", "name": "pack", "worn": True},
    {"at": "L09", "name": "pack", "pos": [0.78, -1.42, 0.0], "yaw": 25},
    {"at": "L14", "name": "pack", "pos": [0.78, -1.42, 0.0], "yaw": 25},
    {"at": 0, "name": "stick", "hidden": True},
    {"at": "L03", "name": "stick", "hand": "grandad.arm-1", "offset": [0.0, 0.0, 0.0], "tilt": 0},
    {"at": "L04", "name": "stick", "pos": [-0.55, -2.35, 0.0], "yaw": 0, "tilt": 14},
    {"at": "L06", "name": "stick", "pos": [-0.55, -2.35, 0.0], "yaw": 0, "tilt": 14},
    {"at": "L07", "name": "stick", "pos": [HOME[0] + 0.55, -0.7, 0.18], "yaw": 0, "tilt": 6},
    {"at": "L08", "name": "stick", "hidden": True},
]
# the stick is carried by the left arm at L03 and leans on the stone after; the rig only holds things at an arm's end

fx = []

# ---------------------------------------------------------------------------------------------- sound
sfx = [
    # the jacket creaks (L08), the curlew calls at dusk (L14) and at sunset (L63)
    {"at": "L08+0.4", "kind": "creak", "db": -24, "dur": 0.5},
    {"at": "L08+1.4", "kind": "creak", "db": -25, "dur": 0.5},
    {"at": "L08+2.6", "kind": "creak", "db": -25, "dur": 0.5},
    {"at": "L14+0.5", "kind": "curlew", "db": -24, "dur": 1.7},
    {"at": "L63+0.3", "kind": "curlew", "db": -26, "dur": 1.7},
    # Big Hands: a low breath of air, never a footstep
    {"at": "L19", "kind": "breath", "db": -22, "dur": 2.0},
    {"at": "L26", "kind": "breath", "db": -23, "dur": 2.0},
    # the phone: static crackle each time Grandad's words are reported
    *[{"at": a, "kind": "radio", "db": -17, "dur": 0.7} for a in ("L52", "L56", "L67", "L68")],
    {"at": "P03", "kind": "radio", "db": -24, "dur": 0.5},
    # night two in the tent: the palms rubbing, loud and near
    {"at": "L30", "kind": "rasp", "db": -9, "dur": 2.6},
    {"at": "L33+0.3", "kind": "click", "db": -26},
    {"at": "L34+0.3", "kind": "click", "db": -27},
    {"at": "P02+0.2", "kind": "click", "db": -28},
    # the hits on HANDS and ON
    {"at": "L37.2", "kind": "hit", "db": -8},
    {"at": "L42.1>-0.22", "kind": "hit", "db": -9},
    {"at": "L41+0.2", "kind": "click", "db": -22},
    {"at": "L41+0.62", "kind": "click", "db": -22},
    # the morning: a gate latch
    {"at": "L59", "kind": "click", "db": -18},
    # the close: the final chord falls, a log settles in the fire with a crackle of sparks, and it carries into the loop
    {"at": "L70.3", "kind": "glide", "db": -14, "dur": 0.9},
    {"at": "L70>-0.2", "kind": "logsettle", "db": -8, "dur": 1.2},
]
STEPS = {"floor": "grass", "steps_db": -22}

story = {
    "slug": "ep35-fire-ring",
    "title": "Dad has never camped. So why does his stew taste exactly like Grandad's?",
    "made_for_kids": False,
    "premise": "On a high moor beside an old stone fire ring with three seats, Dad takes Grandad's place for the autumn camp and "
               "knows far too much for a man who has never camped, while someone in heather purple with hands as big as the "
               "tent door stands one stepping stone nearer the fire each night.",
    "twist": "Dad has been ringing Grandad every evening from the bottom of the hill to be talked through the camp, and the stew "
             "is Grandad's recipe from the dented flask, so the thing that seemed like a replacement was a call for help.",
    "world": "A high autumn moor in heather and peat with black bog pools, a ring of old grey stones, a moss-green ridge tent, "
             "a drystone wall and a field gate down the hill.",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff8a3d",
    "gap": 0.12,
    "tail": 0.25,
    "fade_out": False,
    "look": {"fog": "#2a3550", "fog_density": 0.02, "fog_start": 6.0, "sky": "#101830", "exposure": 0.55},
    "grade": {"shadows": [-0.01, 0.0, 0.04], "highlights": [0.04, 0.015, -0.025], "saturation": 0.95,
              "contrast": 1.05, "vignette": 0.3, "bloom": 0.3, "grain": 0.012, "red_line": 0.76},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    # D Dorian, 74 bpm: a low drone, a plucked figure, a breathy pad. From L59 it turns to D major, warm and low
    "music": {"root": 50, "mode": "dorian", "bpm": 74, "seed": 35,
              "sections": [
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L08", "voices": ["drone", "pad", "piano"], "energy": 0.35},
                  {"at": "L17", "voices": ["drone", "pad", "piano"], "energy": 0.45},
                  {"at": "L21", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L24", "voices": ["drone", "pad", "piano"], "energy": 0.5},
                  {"at": "L29", "voices": ["drone", "pad"], "energy": 0.35},
                  {"at": "L31", "voices": ["drone", "pad", "piano"], "energy": 0.55},
                  {"at": "L33", "voices": ["drone", "pad"], "energy": 0.45},
                  {"at": "L37.2", "voices": ["drone", "pad", "piano"], "energy": 0.6},
                  {"at": "L45", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L46", "voices": ["pad", "piano"], "energy": 0.3},
                  {"at": "L49", "voices": ["drone", "pad", "piano"], "energy": 0.35},
                  {"at": "L59", "mode": "major", "voices": ["pad", "piano"], "energy": 0.45},
                  {"at": "L64", "mode": "major", "voices": ["drone", "pad", "piano"], "energy": 0.55},
                  {"at": "L70", "mode": "major", "voices": ["pad", "piano"], "energy": 0.4},
              ]},
    "sound": {"floor": "grass", "steps_db": -22,
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "end", "lufs": -35},
                  {"kind": "fire", "from": 0, "to": "L33", "lufs": -38},
                  {"kind": "drips", "from": "L14", "to": "L33", "lufs": -44},
                  {"kind": "fire", "from": "L34", "to": "L46", "lufs": -46},
                  {"kind": "wind", "from": "L46", "to": "L63", "lufs": -38},
                  {"kind": "fire", "from": "L63", "to": "end", "lufs": -34},
              ],
              "sfx": sfx,
              # the music out for 0.7 s before L37 (the hit lands on HANDS) and for 0.6 s before L42 (the hit lands on ON)
              "music_drops": [{"from": "L36>-0.6", "to": "L37.2", "keep": ["hit"]},
                              {"from": "L41>-0.5", "to": "L42.1>-0.22", "keep": ["hit"]}]},
}
# The shots, cues and sounds below name chunks by their place in the script (L19.2 = the script's third part of L19).
# lines.json splits any part over three words into captions of two or three, so each reference is moved to the first
# caption of the part it means.
import re

ORIG = {l["id"]: l.get("orig", []) for l in lines if "chunks" in l}
REF = re.compile(r"^(L\d+b?)\.(\d+)(.*)$")


def remap(ref):
    m = REF.match(ref)
    if not m or m.group(1) not in ORIG or not ORIG[m.group(1)]:
        return ref
    o = ORIG[m.group(1)]
    k = int(m.group(2))
    return f"{m.group(1)}.{o.index(k) if k in o else k}{m.group(3)}"


def walk(x):
    if isinstance(x, dict):
        return {k: (remap(v) if k in ("at", "from", "to", "until") and isinstance(v, str) else walk(v)) for k, v in x.items()}
    if isinstance(x, list):
        return [walk(v) for v in x]
    return x


story = walk(story)
story["lines"] = [{k: v for k, v in l.items() if k != "orig"} for l in lines]
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
