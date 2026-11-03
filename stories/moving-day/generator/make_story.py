"""Writes ../story.json for ep17 "In This Town Every House Grows To Fit The TALLEST" (the rule-first redo, script.md).

Run from anywhere: python stories/moving-day/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the 57 shots and their cameras, the
acting, the cues set.py reads (the time of day, the ceiling's height, the Boxes' pose and face, the stack, the old
house photo, the props, the doors, the practicals), the effects, the score and the sound. Shot ids are numbered in
order (S01 ... S57) and match script.md. The places are set.py's: see the note above the cameras.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

LOOP = 0.12          # the last word ends 0.25 s before the hard cut (the voice's own tail is 0.13 s of it), into L01
# the word check: these lines a touch slower so a swallowed "it", "and" or "me" comes through
TEMPO = {"L21": 0.94, "L11": 1.1, "L16": 0.95, "L17": 0.96}
GAPS = {"L28": 0.72, "L13": 0.05}   # a 0.6 s music drop between L28 and L29
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]
    if ln["id"] in GAPS:
        ln["gap"] = GAPS[ln["id"]]
lines = lines + [{"id": "P03", "pause": LOOP, "chunks": []}]

# ---------------------------------------------------------------------------------------------------- cast
# Skins sit off the cardboard ramp (hue 29 to 30 degrees): Mum #a86a58, me #87503f. Nobody wears cardboard brown or
# the quilt's plum, lilac or rose. The extras (the montage, one shot each) are adults in bright plastic colours.
cast = {
    "me": {"age": "adult", "skin": "#87503f", "shirt": "#3f5a50", "pattern": "solid", "collar": "#354d44",
           "pants": "#2f3033", "shoes": "#8a8c8f", "sleeves": "long", "hair": "cap", "hair_c": "#141213",
           "hat": "none", "width": 0.88, "face": {"eyes": "round", "brows": True, "ink": "#161012"}},
    "mum": {"age": "adult", "skin": "#a86a58", "shirt": "#6c7c97", "pattern": "solid", "collar": "#5f6e88",
            "pants": "#2b2e36", "shoes": "#2b2e36", "sleeves": "long", "hair": "long", "hair_c": "#5a4a42",
            "hat": "none", "height": 0.95, "width": 0.88, "face": {"eyes": "round", "brows": True, "ink": "#1a1214", "bags": True}},
}


def extra(skin, shirt, pants, hair, height, hat="none", hat_c=None, sleeves="short", pattern="solid", hair_c="#2a1a10"):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": "#262626",
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "height": height, "width": 0.88,
         "face": {"eyes": "round", "brows": True}}
    if hat_c:
        d["hat_c"] = hat_c
    return d


cast.update({
    "a": extra("#c68642", "#f2b01e", "#2d3a8c", "buzz", 0.9),
    "b": extra("#8d5524", "#e8453c", "#1e6e5a", "cap", 1.2, hair_c="#1a1a1a"),
    "p3": extra("#e0ac69", "#2fa4e0", "#5a3a8a", "swoop", 1.0, hair_c="#6a3a1a"),
    "c": extra("#a96b44", "#7a4cc2", "#2b2e36", "buzz", 1.55, sleeves="long"),
    "lod": extra("#d4a373", "#ff7a2f", "#2b2f55", "cap", 1.0, sleeves="long", hair_c="#3a2a1a"),
    "w1": extra("#b57a52", "#2fa86a", "#3a3f58", "bun", 0.95, hair_c="#2a1a10"),
    "w2": extra("#e0b080", "#e8c040", "#3a3f58", "spiky", 1.05, hair_c="#7a3a1a"),
    "host": extra("#c98d62", "#d83a52", "#2b2e36", "buzz", 1.0, sleeves="long"),
    "guest": extra("#8d5524", "#3fa0e8", "#2b2e36", "cap", 1.05, hat="tophat", hat_c="#8a3ac2", sleeves="long",
                   hair_c="#1a1a1a"),
})


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return c([0, loc, tgt, lens])


def yaw_to(a, b):
    """The yaw that faces from a toward b (yaw 0 faces -y, 90 faces +x)."""
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


def move(a, b, lens_a, lens_b=None):
    """A slow camera move: (loc, target) at the shot's start to (loc, target) at its end."""
    return c([0, a[0], a[1], lens_a], [1, b[0], b[1], lens_b or lens_a])


# ---------------------------------------------------------------------------------------------------- cameras
# Places (set.py's metres; the floor is z = 0). The hall runs west to east (x -4.6 .. 1.3) between y -1.42 and
# -0.12. North of it: my room (x -4.6 .. -1.82) and Mum's room (x -1.7 .. 1.3, her door at x -1.6 .. -0.85). South of
# it: the front room (x -4.6 .. -0.6, y -5.1 .. -1.54; the front door and the stack on its south wall, the photo wall
# on the west) and the kitchen (x -0.48 .. 2.0; the counter along the south wall). The hall cupboard is at the hall's
# east end. The street, the living room and the dining room of the montage are far to the east (x 60, 100, 140).
# A character with yaw 0 faces -y; yaw 90 faces +x.
OS, O5, O6 = (60.0, 0.0), (100.0, 0.0), (140.0, 0.0)
CLOCK = still([-2.8, -1.75, 1.6], [-2.72, -5.1, 0.8], 13)   # the same locked-off wide every time
# Mum's room at 3 a.m.
WIDE = still([-1.3, -0.25, 1.43], [-0.76, 2.5, 0.95], 18)
FACE_BELOW = c([0, [-0.95, 1.0, 0.75], [-0.6, 2.2, 1.95], 24], [1, [-0.92, 1.12, 0.74], [-0.6, 2.2, 1.95], 25])
ARMS_SIDE = still([0.95, 1.15, 1.05], [-0.45, 2.45, 0.95], 28)
LAMP = still([-0.15, 1.15, 1.45], [-0.55, 0.38, 0.95], 26)
HAND_NEAR = still([-0.75, 1.15, 1.2], [-0.1, 2.3, 0.72], 28)
MUM_SLEEP = still([-1.35, 0.6, 1.0], [-1.3, 1.92, 0.75], 40)
HIGH_QUILT = still([0.75, 0.45, 1.95], [-0.5, 1.95, 0.45], 20)

# (at, what, step, camera). step: 1 on ones (the scare), 4 on fours (locked wides), 2 on twos.
SHOTS = [
    # 1 the rule, L01 to L04 (0 to 10 s): a lit hall opening, then the street of mixed-height houses
    (0, "S01 the front room, warm and even: me under the low ceiling, the face box in the stack beside me, frowning", 2,
     still([-1.0, -2.2, 1.0], [-2.3, -4.5, 1.55], 17)),
    ("L01.4", "S02 the street: four houses of different heights, the tallest one at each door, head at the lintel", 2,
     move(([OS[0] - 4.2, -2.5, 1.3], [OS[0] - 4.2, 6.0, 2.2]), ([OS[0] - 0.6, -2.5, 1.3], [OS[0] - 0.6, 6.0, 2.2]), 13)),
    ("L02+0.57", "S03 the tower house: a tall man at its door, waving", 2,
     still([OS[0] + 4.9, 1.2, 1.0], [OS[0] + 3.2, 6.0, 3.0], 17)),
    ("L03", "S04 a lodger walks out of a front door with a suitcase", 2,
     still([OS[0] + 8.6, -1.5, 1.35], [OS[0] + 10.0, 5.0, 1.2], 17)),
    ("L03+1.35", "S05 a couple on a sofa look up: the ceiling sits lower, a pale line where it was", 2,
     still([O5[0] + 0.1, -1.2, 1.3], [O5[0], 2.6, 1.55], 22)),
    ("L04", "S06 a dinner: a guest in a tall hat, the ceiling bulged up over it, the host glaring", 2,
     still([O6[0] + 0.55, -3.0, 1.6], [O6[0] + 0.55, 1.9, 1.75], 18)),
    # 2 our house, L05 to L13 (10 to 24 s)
    ("L05", "S07 close in the kitchen: the old house photo in Mum's hands", 2,
     still([0.85, -3.42, 1.35], [0.85, -2.4, 1.1], 22)),
    ("L06", "S08 the small house from outside, morning, no number on the door", 2,
     still([OS[0] + 16.0, -2.2, 1.4], [OS[0] + 16.0, 6.0, 1.2], 22)),
    ("L06.2", "S09 me in my doorway, hair on the ceiling, a pencil mark on the frame at my height", 2,
     still([-2.4, -1.36, 1.3], [-2.38, 0.0, 1.25], 14)),
    ("L07", "S10 Mum in the kitchen doorway, flat-faced and tired", 2,
     still([0.45, -0.45, 1.4], [0.45, -1.75, 1.3], 30)),
    ("L08", "S11 Mum hangs the old house frame at her eye height; its top window is dim", 2,
     still([-3.0, -2.45, 1.52], [-4.59, -3.0, 1.5], 30)),
    ("L09", "S12 Mum steps back, no smile, mouth moving under the quote", 2,
     still([-2.15, -4.5, 1.4], [-3.3, -3.1, 1.5], 32)),
    ("L10", "S13 Mum crosses the room head down with her mug, past the stack and the frown", 2,
     move(([-0.9, -2.3, 1.35], [-1.9, -4.5, 1.25]), ([-1.5, -2.3, 1.35], [-2.5, -4.5, 1.25]), 15)),
    ("L11", "S14 the stack by the door (the locked-off wide)", 4, CLOCK),
    ("L11.1", "S15 me on the floor at the face-out box, frowning at it", 2,
     still([-0.85, -3.5, 0.95], [-1.7, -4.5, 0.95], 26)),
    ("L12", "S16 close on the box's top corner: tape shining through the gap from inside", 4,
     move(([-1.35, -3.9, 1.75], [-1.62, -4.75, 1.4]), ([-1.45, -4.1, 1.62], [-1.62, -4.75, 1.4]), 40)),
    ("L13", "S17 low beside the face box: its frown toward the hall and Mum's door", 2,
     still([-0.95, -3.3, 0.55], [-1.75, -4.8, 1.2], 24)),
    # 3 the house grows, L14 to L26 (24 to 46 s)
    ("L14", "S18 me in bed in the dark, eyes open", 2, still([-3.25, 1.6, 1.35], [-4.1, 2.75, 0.72], 26)),
    ("L15", "S19 my doorway again: a hand of air over my head", 2, still([-2.4, -1.36, 1.3], [-2.38, 0.0, 1.35], 14)),
    ("L16", "S20 low up the hall, the ceiling higher", 2, still([-4.35, -0.77, 0.55], [1.0, -0.77, 1.95], 20)),
    ("L17", "S21 my face, scared, looking up into the gap", 2, still([-1.75, -0.77, 1.5], [-3.0, -0.77, 1.65], 32)),
    ("L18", "S22 the stack: six boxes gone", 4, CLOCK),
    ("L19", "S23 the front room, the walls taller", 2, still([-0.8, -1.95, 1.4], [-4.0, -3.5, 1.7], 14)),
    ("L20", "S24 the frames high on the wall, the old house among them", 2, still([-2.7, -3.5, 1.1], [-4.5, -3.1, 1.9], 22)),
    ("L21", "S25 from below, the frames as if hung from above", 2, still([-3.95, -3.0, 0.5], [-4.5, -3.1, 2.05], 16)),
    ("L22", "S26 the kitchen ceiling: a long run of boxes folded along it from the doorway", 2,
     still([1.85, -3.5, 1.05], [0.5, -1.9, 2.0], 17)),
    ("L23", "S27 the face box at the end of the run, hanging, staring down", 2, still([1.9, -1.7, 1.5], [0.7, -2.75, 1.85], 20)),
    ("L23.3", "S28 Mum's back, small; the face above her at the top of the frame", 2, still([1.9, -1.55, 1.6], [0.85, -3.0, 1.6], 17)),
    ("L24", "S29 Mum pouring tea, head down, profile", 2, still([1.95, -3.0, 1.35], [1.1, -3.0, 1.2], 17)),
    ("L25", "S30 close on Mum's lowered face, calm", 2, still([1.3, -3.55, 1.45], [1.1, -3.0, 1.45], 22)),
    ("L26", "S31 the stack, shorter again, a clean square where the face box stood", 4, CLOCK),
    # 4 three a.m., L27 to L34 (46 to 61 s)
    ("L27", "S32 the hall in the nightlight's glow, the ceiling creaking upward", 2,
     still([-4.5, -0.55, 0.9], [-1.0, -0.6, 1.9], 16)),
    ("L28", "S33 Mum's door, open, darker inside", 2, still([-0.75, -1.1, 1.65], [-1.15, 1.2, 1.3], 22)),
    ("L29", "S34 side-on from the doorway: the Boxes bent over her bed, the face box hanging over her", 1, WIDE),
    ("L30", "S35 the face box from below, wide open", 1, FACE_BELOW),
    ("L31", "S36 side-on, the arms already down toward the quilt", 1, ARMS_SIDE),
    ("L32", "S37 the lamp comes up", 1, LAMP),
    ("L33", "S38 the box ends resting flat on the patterned quilt", 1, HAND_NEAR),
    ("L33.3", "S39 high and wide: the quilt laid square and flat, Mum's face calm", 1, HIGH_QUILT),
    ("L34", "S40 Mum asleep in the warm light", 1, MUM_SLEEP),
    # 5 ladder height, L35 to L39 (61 to 71 s)
    ("L35", "S41 Mum's room in morning light, the corner empty, the ceiling high", 2, WIDE),
    ("L35.2", "S42 the stack, whole again, the face box not among them", 4, CLOCK),
    ("L36", "S43 Mum in the front room with her mug, her head tilting up", 2, still([-1.0, -2.35, 1.5], [-1.9, -3.6, 1.45], 30)),
    ("L36.1+0.37", "S44 her eyeline: the frames at the top of a tall wall", 2, move(([-2.6, -3.4, 1.3], [-4.5, -3.1, 2.4]), ([-2.6, -3.4, 1.3], [-4.5, -3.1, 3.0]), 17)),
    ("L37", "S45 Mum still looking up, mouthing the words", 2, still([-1.0, -2.35, 1.5], [-1.9, -3.6, 1.55], 32)),
    ("P02", "S46 the laugh, held, in low gold sun", 2, still([-1.1, -3.3, 1.52], [-1.6, -4.1, 1.47], 22)),
    ("L38", "S47 Mum sits on a box, still laughing", 2, still([-2.5, -2.8, 1.3], [-1.6, -4.2, 0.95], 17)),
    ("L39", "S48 a two-shot: me laughing too, the room tall around us", 2, still([-0.8, -2.5, 1.45], [-1.95, -4.0, 1.1], 15)),
    # 6 the old house, L40 to L48 (71 to 88 s)
    ("L40", "S49 from below, the old house frame at the top of the wall", 2, still([-3.3, -3.05, 0.55], [-4.5, -3.0, 2.55], 20)),
    ("L41", "S50 close on the photo, a slow push to the top window", 2,
     move(([-3.85, -3.0, 2.55], [-4.55, -3.0, 2.7]), ([-4.05, -3.0, 2.68], [-4.55, -3.0, 2.76]), 38, 46)),
    ("L42", "S51 Mum below, laughing quietly, the old photo above her", 2, still([-2.6, -2.6, 0.7], [-4.0, -3.1, 2.1], 19)),
    ("L43", "S52 low and wide: Mum and me small at the foot of a tall wall", 2, still([-0.85, -1.85, 0.4], [-3.6, -3.7, 2.0], 13)),
    ("L44", "S53 my face, looking up", 2, still([-2.0, -2.5, 1.5], [-3.0, -3.3, 1.8], 32)),
    ("L45", "S54 the stack, whole, a clean square where the face box stood", 4, CLOCK),
    ("L45b", "S54b Mum below the old photo, head tipped back to it, eyes wet", 2,
     still([-2.5, -2.7, 1.55], [-3.9, -3.1, 1.8], 20)),
    ("L46", "S55 the hall: Mum opens the cupboard, head down", 2, still([-0.6, -1.25, 1.5], [1.45, -0.75, 1.15], 20)),
    ("L47", "S56 inside the cupboard: the face box alone on the shelf, frown out", 4,
     move(([0.35, -0.95, 1.5], [1.66, -0.79, 1.42]), ([0.5, -0.9, 1.48], [1.66, -0.79, 1.42]), 22)),
    ("L48", "S57 Mum swings the door shut, head still down", 2, still([-0.6, -1.25, 1.5], [1.5, -0.75, 1.3], 24)),
]

shots = []
for i, (at, what, step, cam) in enumerate(SHOTS):
    s = {"id": f"S{i + 1:02d}", "cam": cam, "hand": 0.006 if step == 1 else 0.004, "step": step, "what": what}
    if step == 4 or cam is CLOCK:
        s["hand"] = 0.0          # locked off
    if i:
        s["at"] = at
    shots.append(s)

# ---------------------------------------------------------------------------------------------------- acting
# Every place change happens on a cut: put() writes a zero-length step (no walk, no footsteps) and a key with blend 0,
# so nothing starts moving in the shot before. A put() resets every number it doesn't set. walk() is a move inside a
# shot (footsteps on the boards).
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "lie": None, "sit": False,
           "hide_parts": [], "part_offset": {}, "blink": True, "width": 0.88}   # R6 shoulders are wider than the hall
acting = {k: [] for k in cast}


def put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, "hidden": False, **NEUTRAL,
                 "expr": "worried" if who == "me" else "neutral", **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": pos, **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def talk(who, a, b):   # a mouth moving under the narrator's reporting of it
    acting[who].append({"from": a, "to": b, "mouth": [0.55, 0.55], "flap": True})


MUM_BED = [0.27, 1.92, 0.59]
ME_BED = [-4.12, 1.28, 0.75]
IN_BED = {"lie": [-88, 0, 90], "head": [-55, 0], "side": [24, 0], "expr": "asleep", "blink": False, "width": 1.0,
          "part_offset": {"neck": [0, -0.04, 0], "arm-1": [0.0, -0.03, 0]},
          "hide_parts": ["arm1", "leg-1", "leg1", "torsom", "collar"]}
ME_IN_BED = {"lie": [-88, 0, 0], "hide_parts": ["arm1", "arm-1", "leg-1", "leg1", "torsom", "collar"]}
for who in cast:
    if who != "me":
        hide(who, 0)

# ---- the montage
SX, SY = OS
YD = SY + 5.68       # a doorway person's y: on the step
for who, x in (("a", SX - 6.8), ("b", SX - 3.3), ("p3", SX + 0.0), ("c", SX + 3.2)):
    put(who, "L01.4", [x, YD, 0.08], yaw=0, expr="grin" if who != "c" else "smirk")
    hide(who, "L03")
for who in ("a", "b", "p3"):
    hide(who, "L02+0.57")
for k in range(6):                                           # the tall man waves
    key("c", f"L02+{0.8 + 0.4 * k:.2f}", side=[0, 28 if k % 2 == 0 else 8], arms=[0, 150], blend=0.3)
put("lod", "L03", [SX + 10.0, SY + 6.4, 0.0], yaw=0, expr="neutral", side=[0, 4])
walk("lod", "L03+0.1", [SX + 10.0, SY + 6.4, 0.0], side=[0, 4])
walk("lod", "L03+1.3", [SX + 10.0, SY + 2.6, 0.0], side=[0, 4])
hide("lod", "L03+1.35")
put("w1", "L03+1.35", [O5[0] - 0.45, O5[1] + 2.55, -0.09], yaw=0, sit=True, head=[0, -28], expr="worried")
put("w2", "L03+1.35", [O5[0] + 0.45, O5[1] + 2.55, -0.09], yaw=0, sit=True, head=[0, -28], expr="worried")
hide("w1", "L04")
hide("w2", "L04")
put("host", "L04", [O6[0] - 1.38, O6[1] + 1.9, -0.055], yaw=40, sit=True, expr="angry")
put("guest", "L04", [O6[0] + 1.38, O6[1] + 1.9, -0.055], yaw=-30, sit=True, expr="smirk")
hide("host", "L05")
hide("guest", "L05")

# ---- me
put("me", 0, [-2.45, -4.0], yaw=180, expr="worried")                                  # S01: under the low ceiling
hide("me", "L01.4")
put("me", "L06.2", [-2.38, 0.2], yaw=0, expr="worried")                              # S09: in my doorway
hide("me", "L07")
put("me", "L11.1", [-1.72, -4.1, -0.51], yaw=0, sit=True, head=[0, 18], expr="worried")   # on the floor at the box
hide("me", "L12")
put("me", "L14", ME_BED, **ME_IN_BED)                                                # awake in bed in the dark
hide("me", "L15")
put("me", "L15", [-2.38, 0.2], yaw=0, expr="worried")                                # S19: my doorway again
hide("me", "L16")
put("me", "L17", [-3.0, -0.8], yaw=90, head=[0, -32], expr="scared")                 # S21: looking up
hide("me", "L18")
put("me", "L32", [-1.15, 0.62], yaw=90, arms=[40, 0], side=[-6, 0], expr="wide")     # my hand at the lamp's switch
key("me", "L32+0.3", arms=[38, 0], side=[-6, 0], blend=0.2)
hide("me", "L33")
put("me", "L39", [-2.3, -3.7], yaw=yaw_to([-2.3, -3.7], [-1.6, -4.3]), expr="laugh", tremble=1.2)
put("me", "L43", [-3.0, -3.3], yaw=yaw_to([-3.0, -3.3], [-0.9, -1.9]), head=[0, -24], expr="soft")
put("me", "L44", [-2.9, -3.3], yaw=yaw_to([-2.9, -3.3], [-2.0, -2.5]), head=[0, -30], expr="soft")
hide("me", "L45")

# ---- Mum
put("mum", "L05", [0.85, -2.45], yaw=0, arms=[58, 58], head=[0, 14])                # S07: the photo in her hands
hide("mum", "L06")
put("mum", "L07", [0.45, -1.72], yaw=180, head=[0, 12])                               # S10: the kitchen doorway
hide("mum", "L08")
put("mum", "L08", [-4.0, -3.62], yaw=-90, arms=[75, 75], side=[-10, -10], head=[0, -4])   # S11: hanging the frame
key("mum", "L08+0.7", arms=[60, 60], blend=0.4)
put("mum", "L09", [-3.3, -3.1], yaw=yaw_to([-3.3, -3.1], [-2.15, -4.5]), arms=[20, 20], side=[-12, -12], head=[0, 12])
talk("mum", "L09", "L09>")
put("mum", "L10", [-1.0, -4.0], yaw=-90, arms=[70, 0], head=[0, 22])                  # S13: crossing, mug in hand
key("mum", "L10+0.25", arms=[84, 0], blend=0.35)
walk("mum", "L10+0.3", [-1.0, -4.0], arms=[84, 0], head=[0, 22])
walk("mum", "L10>", [-3.4, -4.0], arms=[84, 0], head=[0, 22])
hide("mum", "L11")
put("mum", "L23", [1.15, -3.0], yaw=0, arms=[78, 74], head=[0, 22])                   # S26 on: at the counter
key("mum", "L24", arms=[80, 78], blend=0.4)
hide("mum", "L26")
put("mum", "L28", MUM_BED, yaw=0, **IN_BED)                                           # asleep under the quilt
put("mum", "L36", [-1.9, -3.6], yaw=yaw_to([-1.9, -3.6], [-1.0, -2.35]), arms=[84, 0], side=[-12, -12], head=[0, 14])
key("mum", "L36.1", yaw=yaw_to([-1.9, -3.6], [-1.0, -2.35]) + 5, head=[0, -34], blend=0.5)     # she looks up
put("mum", "L37", [-1.9, -3.6], yaw=yaw_to([-1.9, -3.6], [-1.0, -2.35]) + 5, arms=[70, 22], side=[-12, -12], head=[0, -34])
talk("mum", "L37", "L37>")
put("mum", "P02", [-1.6, -4.1], yaw=150, arms=[60, 30], side=[-12, -12], head=[0, 6], expr="laugh", tremble=2.4)
put("mum", "L38", [-1.6, -4.3, -0.085], yaw=180, arms=[50, 25], side=[-10, -10], expr="laugh", tremble=2.0, sit=True)
put("mum", "L39", [-1.6, -4.3, -0.085], yaw=165, arms=[50, 25], side=[-10, -10], expr="laugh", tremble=1.6, sit=True)
hide("mum", "L40")
put("mum", "L42", [-3.7, -3.0], yaw=-90, head=[0, -32], expr="laugh", tremble=1.0)
put("mum", "L43", [-3.4, -3.5], yaw=yaw_to([-3.4, -3.5], [-0.9, -1.9]), head=[0, -24], expr="laugh", tremble=0.8)
hide("mum", "L44")
put("mum", "L45b", [-3.6, -3.0], yaw=135, head=[0, -16], expr="crying")
put("mum", "L46", [0.2, -0.74], yaw=90, arms=[0, 0], head=[0, 5])                     # the hall cupboard
key("mum", "L46.1", arms=[0, 18], blend=0.2)
key("mum", "L46.1+0.7", arms=[0, 4], blend=0.5)
hide("mum", "L47")
put("mum", "L48", [0.2, -0.74], yaw=90, arms=[0, 18], head=[0, 5])                    # she swings it shut
key("mum", "L48.2", arms=[0, 6], blend=0.6)

# ---------------------------------------------------------------------------------------------------- cues
cues = [
    # the time of day (set.py TIME_LIGHTS): warm even day, the street's bright overcast, near-black night, 3 a.m.,
    # the gold morning
    {"at": 0, "name": "time", "set": "day"},
    {"at": 0, "name": "ceil", "h": 1.72},
    {"at": "L01.4", "name": "time", "set": "street"},
    {"at": "L05", "name": "time", "set": "day"},
    {"at": "L06", "name": "time", "set": "street"},
    {"at": "L06.2", "name": "time", "set": "day"},
    {"at": "L14", "name": "time", "set": "night"},
    {"at": "L15", "name": "time", "set": "day"},
    {"at": "L27", "name": "time", "set": "night3", "exposure": 1.5},      # the dark hall: only the glow from her door
    {"at": "L28", "name": "time", "set": "night3"},
    {"at": "L35", "name": "time", "set": "sun"},
    {"at": "L46", "name": "time", "set": "end"},
    # the ceiling: on my hair, a hand above it (morning 1), a third of the way up (morning 2), creaking up at three
    # a.m. (S32), ladder height from the third morning
    {"at": "L15", "name": "ceil", "h": 1.98},
    {"at": "L19", "name": "ceil", "h": 2.2},
    {"at": "L27", "name": "ceil", "h": 2.35, "dur": 2.4},
    {"at": "L35", "name": "ceil", "h": 3.3},
    # the Boxes (one model): the face box in the stack, in the kitchen (morning 2), over Mum's bed, then alone on the shelf
    {"at": 0, "name": "boxes", "pose": "head_stack", "face": "frown"},
    {"at": "L22", "name": "boxes", "pose": "kitchen2", "face": "stare"},
    {"at": "L26", "name": "boxes", "hidden": True},
    {"at": "L29", "name": "boxes", "pose": "over_bed", "face": "wide"},
    {"at": "L35", "name": "boxes", "hidden": True},
    {"at": "L46", "name": "boxes", "pose": "head_shelf", "face": "frown"},
    # the stack: six gone (L18), shorter again with the face box's clean square (L26), whole again (L35)
    {"at": 0, "name": "stack", "hide": []},
    {"at": "L18", "name": "stack", "hide": [12, 13, 14, 18, 19, 20]},
    {"at": "L26", "name": "stack", "hide": [12, 13, 14, 18, 19, 20, 21, 23], "clean": True},
    {"at": "L35", "name": "stack", "hide": [], "clean": True},   # whole but the face box's one clean square (S54)
    {"at": 0, "name": "loose", "on": False},
    {"at": "L38", "name": "loose", "on": [0], "seat": [-1.6, -4.3, 0]},
    {"at": "L40", "name": "loose", "on": False},
    {"at": 0, "name": "quiltbox", "hidden": True},
    # the old house photo: in Mum's hands (L05), then on the wall, dim; lit for the reveal at L41
    {"at": 0, "name": "oldhouse", "where": "none", "look": "dim"},
    {"at": "L05", "name": "oldhouse", "where": "hand", "look": "dim"},
    {"at": "L06", "name": "oldhouse", "where": "none", "look": "dim"},
    {"at": "L08+0.8", "name": "oldhouse", "where": "wall", "look": "dim"},
    {"at": "L41", "name": "oldhouse", "where": "wall", "look": "lit"},
    {"at": "L42", "name": "oldhouse", "where": "wall", "look": "dim"},
    {"at": "L45b", "name": "oldhouse", "where": "wall", "look": "lit"},
    {"at": "L46", "name": "oldhouse", "where": "wall", "look": "dim"},
    # the mug: on the sill, in Mum's hand (S13, S43), on the counter for her tea
    {"at": 0, "name": "mug", "where": "sill"},
    {"at": "L10", "name": "mug", "where": "hand", "who": "mum", "arm": "arm-1"},
    {"at": "L11", "name": "mug", "where": "sill"},
    {"at": "L24", "name": "mug", "where": "counter", "pos": [0.55, -3.55]},
    {"at": "L26", "name": "mug", "where": "sill"},
    {"at": "L36", "name": "mug", "where": "hand", "who": "mum", "arm": "arm-1"},
    {"at": "L38", "name": "mug", "where": "sill"},
    {"at": 0, "name": "tape", "state": "none"},
    {"at": 0, "name": "kettle", "side": "right"},
    {"at": 0, "name": "coats", "on": False},
    {"at": 0, "name": "pile", "on": False},
    {"at": 0, "name": "bedquilt", "on": False},
    {"at": "L28", "name": "bedquilt", "on": True},
    {"at": "L36", "name": "bedquilt", "on": False},
    {"at": 0, "name": "cape", "on": False},
    {"at": 0, "name": "carry", "on": False},
    # the doors: Mum's shut, then found open at 3 a.m.; the hall cupboard opened at L46 and swung shut on "UP"
    {"at": 0, "name": "door", "door": "mum", "open": 0.0},
    {"at": "L28", "name": "door", "door": "mum", "open": 1.0},
    {"at": "L36", "name": "door", "door": "mum", "open": 0.0},
    {"at": "L46.1", "name": "door", "door": "cupboard", "open": 1.0, "dur": 0.9},
    {"at": "L48.2", "name": "door", "door": "cupboard", "open": 0.0, "dur": 0.75},
    # Mum's nightlight and the dim lamp on her chest of drawers (it comes up over 1.2 s, never a snap)
    {"at": 0, "name": "nightlight", "on": False},
    {"at": "L27", "name": "nightlight", "on": True},
    {"at": "L35", "name": "nightlight", "on": False},
    {"at": 0, "name": "lamp", "on": 0.0},
    {"at": "L32", "name": "lamp", "on": 1.0, "dur": 1.2},
    {"at": "L35", "name": "lamp", "on": 0.0},
    # the relights ("xfill": one soft light, placed and aimed per beat, off between)
    {"at": 0, "name": "xfill", "pos": [-1.6, -3.0, 1.7], "aim": [-2.2, -4.3, 1.3], "gain": 1.2},
    {"at": "L01.4", "name": "xfill", "gain": 0},
    {"at": "L07", "name": "xfill", "pos": [0.2, -0.5, 1.5], "aim": [0.45, -1.72, 1.4], "gain": 1.1},
    {"at": "L08", "name": "xfill", "gain": 0},
    {"at": "L11.1", "name": "xfill", "pos": [-0.8, -3.2, 1.3], "aim": [-1.7, -4.5, 1.0], "gain": 1.2},
    {"at": "L13", "name": "xfill", "pos": [-0.9, -3.4, 0.7], "aim": [-1.7, -4.8, 1.2], "gain": 1.0},
    {"at": "L14", "name": "xfill", "gain": 0},
    {"at": "L35", "name": "xfill", "pos": [0.4, 0.4, 2.6], "aim": [-0.6, 2.0, 0.8], "gain": 4.0},
    {"at": "L35.2", "name": "xfill", "gain": 0},
    {"at": "L40", "name": "xfill", "pos": [-3.0, -3.0, 1.5], "aim": [-4.5, -3.0, 2.5], "gain": 0.8},
    {"at": "L41", "name": "xfill", "pos": [-3.5, -2.7, 2.9], "aim": [-4.55, -3.0, 2.7], "gain": 1.5},
    {"at": "L42", "name": "xfill", "gain": 0},
    {"at": "L45b", "name": "xfill", "pos": [-2.3, -2.3, 1.7], "aim": [-3.6, -3.0, 1.5], "gain": 3.0},
    {"at": "L46", "name": "xfill", "gain": 0},
    {"at": "L27", "name": "xfill", "pos": [-3.6, -0.8, 1.7], "aim": [-1.6, -0.8, 1.1], "gain": 0.22},
    {"at": "L28", "name": "xfill", "gain": 0},
    {"at": "L47", "name": "xfill", "pos": [0.3, -1.4, 1.9], "aim": [1.66, -0.79, 1.3], "gain": 1.6},
    {"at": "L48", "name": "xfill", "gain": 0},
]

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L14.1", "kind": "scrape", "db": -14, "dur": 2.0, "distant": True},           # cardboard down the hall
    {"at": "L27", "kind": "creak", "db": -12, "dur": 2.4},                                # the house rising
    {"at": "P01+0.2", "kind": "creak", "tone": "cardboard", "db": -20, "dur": 1.0},      # one low cardboard creak
    {"at": "L32", "kind": "click", "db": -12},                                            # the lamp switch, audible
    {"at": "L46.1", "kind": "door", "db": -18},                                           # the cupboard, soft
    {"at": "L48>-0.2", "kind": "thud", "db": -12, "dur": 0.8},                           # it shuts on "UP"
]

story = {
    "slug": "ep17-moving-day",
    "title": "In This Town Every House Grows To Fit The TALLEST",
    "made_for_kids": False,
    "premise": "In this town a house grows or sinks to fit the tallest one living in it, a hand a night. Our old house was always a ladder taller than Mum or me. It sold, Mum hasn't laughed since, and the small new house fits me exactly, until each morning there's more room over my head, the walls have stretched with Mum's photos on them, and the stack of moving boxes by the door is shorter.",
    "twist": "The old house never broke the rule: something tall always lived in it with us, folded under its high ceilings while Mum never looked up. When we moved it taped itself into one of our boxes from the inside and came along, and the new house grew to fit it, back to ladder height.",
    "world": "a small single-storey house half moved into: off-white walls, honey boards, a stack of taped moving boxes by the front door, a hall cupboard, ceilings that start right on my hair and rise to ladder height over four mornings, and a bright street of houses of very different heights for the opening montage",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#b98aff",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#0d1015", "fog_density": 0.01, "fog_start": 2.5, "sky": "#0b0d11", "sky_strength": 1.0,
             "exposure": 1.0, "flash_safe": True},
    "grade": {"shadows": [-0.02, 0.0, 0.04], "highlights": [0.0, 0.005, 0.01], "saturation": 0.92, "contrast": 1.08,
              "vignette": 0.35, "bloom": 0.2, "grain": 0.012, "red_line": 0.79},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    # minor at 72 bpm: thin and light under the montage, one held low note from L11, the heavy drone from L27, a
    # drop before L29, the major at P02 (the laugh), a single low note from L40, one soft note under L48
    "music": {"root": 43, "mode": "minor", "bpm": 72, "seed": 17,
              "sections": [
                  {"at": 0, "voices": ["pad", "pulse"], "energy": 0.25},
                  {"at": "L05", "voices": ["pad"], "energy": 0.25},
                  {"at": "L11", "voices": ["drone"], "energy": 0.3},
                  {"at": "L14", "voices": ["drone", "pad"], "energy": 0.32},
                  {"at": "L19", "voices": ["drone", "pad", "pulse"], "energy": 0.4},
                  {"at": "L27", "voices": ["drone", "pad", "choir"], "energy": 0.6},
                  {"at": "L32", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L35", "voices": ["pad"], "energy": 0.25},
                  {"at": "P02", "voices": ["piano", "pad", "drone"], "energy": 0.5, "mode": "major", "root": 41},
                  {"at": "L40", "voices": ["drone"], "energy": 0.25, "mode": "minor", "root": 43},
                  {"at": "L48", "voices": ["drone"], "energy": 0.3},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "L27", "lufs": -34},
                  {"kind": "room", "from": "L27", "to": "L35", "lufs": -38},
                  {"kind": "room", "from": "L35", "to": "end", "lufs": -34},
                  {"kind": "wind", "from": 0, "to": "L05", "lufs": -42},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "L28>", "to": "L29"},
                              {"from": "L31.1", "to": "L32", "db": -45.0, "keep": ["creak", "click"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
