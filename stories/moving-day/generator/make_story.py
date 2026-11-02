"""Writes ../story.json for ep17 "The box was taped shut from the inside" (script 02b, brief 02, 2026-10-31).

Run from anywhere: python stories/moving-day/generator/make_story.py
The words are in lines.json next to this file (the scriptwriter's). Everything else is here: the cast, the shots
and their cameras, the acting, the cues set.py reads (the time of day, the Boxes' pose and face, the stack clock,
the props, the doors, the practicals), the effects, the score and the sound. Shot ids are numbered in order (S01,
...). The places are set.py's: see the note above the cameras.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# ---------------------------------------------------------------------------------------------------- holds
# If the voice lands short of the owner's 2:15 floor, holds are added in the brief's order, never words:
# P02 up to 2.4 s, the photos after L66 +0.3 s, the smile after L77 +0.2 s, L61's gap up to 0.7 s, P01 up to 1.4 s.
HOLDS = {"P02": 2.4, "L66": 0.42, "L77": 0.65, "L61": 0.7, "P01": 1.4}
LOOP = 0.25          # the brief: a hard cut 0.25 s after the last word, into L01 (no fade at either end)

for ln in lines:
    lid = ln["id"]
    if lid in HOLDS:
        if "pause" in ln:
            ln["pause"] = HOLDS[lid]
        else:
            ln["gap"] = HOLDS[lid]
lines = lines + [{"id": "P03", "pause": LOOP, "chunks": []}]

# the word check (asr): lines a touch slower, so a swallowed word comes through ("had" in L23 was heard as "it";
# "flaps still" in L02 ran together), and a pause in L53's spoken text only (README: "its... slits."), so "tucked
# round" isn't heard as "tucked around"; L64 gets a breath after "wrapped", as Whisper heard "in a quilt"
# at either tempo and with "thee". The captions don't change
TEMPO = {"L02": 0.95, "L23": 0.92, "L53": 0.94}
SPOKEN = {("L53", 0): "Tucked, round", ("L64", 1): "wrapped,"}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]
    for k, ch in enumerate(ln.get("chunks", [])):
        if (ln["id"], k) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], k)]

# ---------------------------------------------------------------------------------------------------- cast
# One voice for everyone (note 18): voice A reads every line; Mum's words are reported. Skins sit off the cardboard
# ramp (the boards are hue 29 to 30 degrees, lightness 41 to 53%), producer's ruling 2026-10-31: Mum #a86a58 (hue
# 14), me #87503f (hue 14, deeper: in cold daylight the lighter #9c5e4c read pink). Nobody wears cardboard brown or the quilt's
# plum, lilac or rose; nothing from the brief's ban list. My top is a dark green-grey, not olive: olive went
# mustard in the gold sun.
cast = {
    "me": {"age": "adult", "skin": "#87503f", "shirt": "#3f5a50", "pattern": "solid", "collar": "#354d44",
           "pants": "#2f3033", "shoes": "#8a8c8f", "sleeves": "long", "hair": "cap", "hair_c": "#141213",
           "hat": "none", "width": 0.88, "face": {"eyes": "round", "brows": True, "ink": "#161012"}},
    "mum": {"age": "adult", "skin": "#a86a58", "shirt": "#6c7c97", "pattern": "solid", "collar": "#5f6e88",
            "pants": "#2b2e36", "shoes": "#2b2e36", "sleeves": "long", "hair": "long", "hair_c": "#5a4a42",
            "hat": "none", "height": 0.95, "width": 0.88, "face": {"eyes": "round", "brows": True, "ink": "#1a1214", "bags": True}},
}


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
# Places (set.py's metres; the floor is z = 0, the ceiling 2.35 m). The hall runs west to east (x -4.6 .. 1.3)
# between y -1.42 and -0.12. North of it: my room (x -4.6 .. -1.82, my bed's head against the back wall at
# y 3.3) and Mum's room (x -1.7 .. 1.3, her door at x -1.6 .. -0.85). South of it: the front room (x -4.6 ..
# -0.6, y -5.1 .. -1.54; the front door and the stack on its south wall, the photo wall on the west, the deep
# sill on the east) and the kitchen (x -0.48 .. 2.0; the counter along the south wall, the fridge by the door).
# The hall cupboard is at the hall's east end. A character with yaw 0 faces -y; yaw 90 faces +x.
CLOCK = still([-2.8, -1.75, 1.6], [-2.72, -5.1, 0.8], 13)   # the same locked-off wide every time
# Mum's room at 3 a.m. (the creature test still and its inserts)
WIDE = still([-1.3, -0.25, 1.43], [-0.76, 2.5, 0.95], 18)
FACE_BELOW = c([0, [-0.95, 1.0, 0.75], [-0.6, 2.2, 1.95], 24], [1, [-0.92, 1.12, 0.74], [-0.6, 2.2, 1.95], 25])
ARMS_SIDE = still([0.95, 1.15, 1.05], [-0.45, 2.45, 0.95], 28)
LAMP = still([-0.15, 1.15, 1.45], [-0.55, 0.38, 0.95], 26)
HAND_NEAR = still([-0.6, 1.3, 1.25], [-0.86, 2.38, 0.8], 32)
MUM_FACE = still([-0.9, 0.9, 1.3], [-1.3, 1.85, 0.75], 32)
QUILT = still([0.12, 0.72, 1.3], [-0.6, 1.62, 0.55], 26)
MUM_SLEEP = still([-1.35, 0.6, 1.0], [-1.3, 1.92, 0.75], 40)
SHOULDERS = still([-0.9, 1.0, 1.2], [-1.05, 1.9, 0.7], 35)
JOINTS = c([0, [-0.35, 1.4, 1.45], [-0.75, 2.45, 1.45], 28], [1, [-0.38, 1.52, 1.45], [-0.75, 2.45, 1.45], 30])
FROWN = still([-1.25, -0.82, 1.55], [-0.13, -0.75, 2.02], 26)
STARE = still([1.75, -2.55, 1.45], [0.62, -2.94, 1.95], 26)
SIDEWAYS = still([-2.38, -2.87, 1.16], [-2.5, -2.03, 1.97], 26)
MANY = still([-3.98, 2.66, 1.15], [-3.86, 2.8, 2.06], 18)
SHELF = still([0.75, -0.62, 1.55], [1.69, -0.79, 1.42], 26)
SMILE = still([0.86, -0.77, 1.45], [1.69, -0.79, 1.42], 18)

# (at, room, what, step, camera). step: 1 on ones (the scare), 4 on fours (the clock wides, the face and night
# inserts, L29b's door, L34c's cores, the shelf), 2 on twos. Rooms: hall, front, kitchen, mine, mum
SHOTS = [
    # 01 the box, L01 to L12 (morning 1, cold dawn; the Boxes in the hall, 12 boxes, the frown)
    (0, "hall", "close on the bottom box: its peeled strip, my hand at it, tape glinting in the knee's gap", 2,
     move(([-0.3, -1.22, 0.2], [0.32, -0.95, 0.16]), ([-0.22, -1.18, 0.19], [0.32, -0.95, 0.16]), 24, 26)),
    ("L02", "hall", "my flat hands on its shins", 2, still([-1.2, -0.35, 1.9], [0.05, -0.8, 0.7], 22)),
    ("L03", "hall", "a slow tilt up the Boxes to the frown at the ceiling, me beside it for scale", 2,
     move(([-1.65, -0.42, 0.4], [0.2, -0.72, 0.55]), ([-1.65, -0.42, 0.75], [-0.1, -0.76, 2.05]), 18)),
    ("L04.3", "hall", "the frown, close", 4, FROWN),
    ("L05", "front", "the low ceiling: me carrying a box under the bare bulb, the ceiling just over my head", 2,
     still([-1.1, -2.3, 1.2], [-2.6, -3.3, 1.55], 18)),
    ("L06", "kitchen", "Mum tired just inside the kitchen door, head down, the Boxes' legs in the hall behind her", 2,
     still([0.85, -3.25, 1.4], [0.45, -1.8, 1.3], 24)),
    ("L07", "front", "Mum hanging the old house's photo at eye height, her mouth going", 2,
     still([-2.5, -1.75, 1.7], [-4.4, -2.7, 1.3], 20)),
    ("L08", "front", "my face to a box I'm carrying, eyes shut", 2, still([-1.5, -2.6, 1.55], [-2.4, -3.6, 1.35], 24)),
    ("L09", "front", "Mum folds the flaps shut over the quilt and pushes the box to the stack", 2,
     still([-2.15, -3.8, 1.2], [-3.0, -4.0, 0.4], 26)),
    ("L10", "front", "the mug on the sill", 2,
     move(([-1.36, -4.1, 1.05], [-0.78, -4.45, 0.87]), ([-1.26, -4.15, 1.02], [-0.78, -4.45, 0.87]), 35)),
    ("L11", "front", "Mum lifting it, head down (to L12)", 2, still([-0.7, -2.85, 1.55], [-1.15, -4.25, 1.05], 22)),
    # 02 the stack, L13 to L25
    ("L13", "hall", "Mum carrying the mug past the Boxes, under its face", 2,
     still([-3.4, -0.8, 1.45], [-0.4, -0.85, 1.35], 22)),
    ("L14", "front", "the clock wide: 24", 4, CLOCK),
    ("L15", "front", "the clock wide: 18, a row lower, no dust squares", 4, CLOCK),
    ("L16", "mine", "me in bed in the dark, awake", 2, still([-3.25, 1.6, 1.35], [-4.1, 2.75, 0.72], 26)),
    ("L17", "kitchen", "morning 2: the kitchen, the Boxes by the fridge, Mum at the counter", 2,
     still([1.88, -3.22, 1.55], [0.1, -2.3, 1.55], 16)),
    ("L18", "kitchen", "low on the face box folded along the ceiling", 2, still([1.4, -2.2, 0.9], [0.6, -2.85, 2.1], 20)),
    ("L19", "kitchen", "over its shoulder to Mum at the counter, the five tape rolls heaped at its far end", 2,
     still([1.9, -1.7, 1.2], [0.4, -2.75, 1.75], 16)),
    ("L20", "kitchen", "the wet stare over the back of Mum's head, locked", 4, STARE),
    ("L21", "kitchen", "Mum making tea right under it, the rolls still in frame", 2,
     still([1.9, -1.8, 1.55], [0.8, -3.2, 1.45], 20)),
    ("L22", "front", "a tilt up the photo wall onto the ceiling", 2,
     move(([-2.7, -3.0, 1.25], [-4.6, -3.1, 1.45]), ([-2.7, -3.0, 1.25], [-4.35, -3.2, 2.4]), 20)),
    ("L23", "front", "the frames from below", 2, still([-3.75, -3.2, 0.45], [-4.25, -3.1, 2.35], 16)),
    ("L24", "front", "Mum crossing under them, head down", 2, still([-2.2, -3.7, 0.9], [-4.1, -2.9, 1.65], 18)),
    ("L25", "front", "the clock wide: 12", 4, CLOCK),
    # 03 the seams, L26 to L35 (morning 3; the front-room corner, 14 boxes, the sideways face)
    ("L26", "front", "the Boxes in the front-room corner by the doorway", 2, still([-4.2, -4.55, 1.5], [-1.9, -2.2, 1.5], 18)),
    ("L27", "front", "a slow pan across the eyed boxes", 2,
     move(([-2.75, -2.25, 1.3], [-3.6, -2.7, 0.35]), ([-2.75, -2.25, 1.3], [-2.0, -4.6, 0.3]), 24)),
    ("L28.3", "front", "the reverse, through the doorway and across the hall to Mum's shut door", 2,
     still([-4.3, -2.75, 1.45], [-1.22, -0.06, 1.05], 18)),
    ("L29", "front", "the sideways face", 4, SIDEWAYS),
    ("L29b", "front", "Mum's shut door, quiet in grey light, the sideways face at the frame's edge, closer", 4,
     still([-4.2, -3.4, 1.45], [-1.22, -0.06, 1.0], 28)),
    ("L30", "front", "my hands flat on a joint, leaning back", 2, still([-0.75, -3.65, 1.45], [-1.45, -2.65, 1.2], 22)),
    ("L31", "front", "my arms trembling", 2, still([-0.85, -3.35, 1.4], [-1.4, -2.6, 1.15], 28)),
    ("L32", "front", "a bare joint, no tape", 2, still([-1.65, -3.05, 1.45], [-1.6, -2.3, 1.42], 35)),
    ("L33", "front", "a slow push into the joint, tape glinting inside", 2,
     move(([-1.6, -3.0, 1.45], [-1.6, -2.3, 1.42]), ([-1.6, -2.82, 1.44], [-1.6, -2.3, 1.42]), 40)),
    ("L34", "front", "me stepping back, the Boxes unmarked", 2, still([-3.9, -3.7, 1.45], [-2.0, -2.25, 1.45], 18)),
    ("L34b", "kitchen", "the kitchen: me at the counter looking down at the cores, over my shoulder", 2,
     still([0.55, -2.6, 1.7], [1.72, -3.56, 0.94], 26)),
    ("L34c", "kitchen", "close and low along the five bare cores standing in a row, locked", 4,
     still([1.18, -3.2, 0.97], [1.7, -3.58, 0.94], 30)),
    ("L35", "front", "the clock wide: 4, each with two marker eyes at Mum's door", 4, CLOCK),
    # 04 my room, L36 to L43 (night; 15 boxes, far too many eyes)
    ("L36", "mine", "from my pillow, the Boxes in the corner", 2, still([-4.1, 2.75, 0.8], [-2.6, 2.35, 1.55], 18)),
    ("L37", "mine", "looking up at the face box above me", 2, still([-4.12, 2.6, 0.84], [-3.86, 2.8, 2.08], 18)),
    ("L38", "mine", "the many eyes", 4, MANY),
    ("L39", "mine", "my terrified face", 2, still([-3.95, 2.2, 1.5], [-4.12, 2.86, 0.8], 30)),
    ("L40", "mine", "the window greying toward dawn behind it", 2, still([-4.25, 1.45, 1.05], [-3.05, 3.3, 1.4], 22)),
    ("L41", "front", "the empty clock wide: bare floor, clean squares in the dust (to L42)", 4, CLOCK),
    ("L43", "kitchen", "breakfast, me wrecked, the row of cores in the background", 2,
     still([0.15, -1.85, 1.55], [1.5, -3.45, 1.05], 18)),
    # 05 three a.m., L44 to L55 (from L48 on ones)
    ("L44", "mine", "my eyes open in the dark", 2, still([-4.0, 1.95, 1.2], [-4.12, 2.88, 0.78], 22)),
    ("L45", "hall", "the dark hall, a cold glow at Mum's door", 2, still([-3.5, -0.95, 1.45], [-1.3, -0.35, 1.05], 20)),
    ("L46", "hall", "the square shadow up the hall wall and over the ceiling", 2,
     still([-1.2, -0.15, 1.25], [-1.85, -1.42, 1.75], 16)),
    ("L47.2", "hall", "her open door, over my shoulder", 2, still([-0.75, -1.1, 1.75], [-1.15, 1.2, 1.3], 22)),
    ("L48", "mum", "the side-on wide: the Boxes bent over the bed, the chain along the ceiling", 1, WIDE),
    ("L49", "mum", "the wide-open face from below", 1, FACE_BELOW),
    ("L50", "mum", "the arms already down, side-on", 1, ARMS_SIDE),
    ("P01", "mum", "the hold", 1, WIDE),
    ("L51", "mum", "my hand at the lamp, the lamp coming up", 1, LAMP),
    ("L52", "mum", "the flap hands on the quilt's edge", 1, HAND_NEAR),
    ("L53", "mum", "Mum's calm face, one arm out on top of the quilt", 1, MUM_FACE),
    ("L54", "mum", "the quilt in lamp light, her arm and hand on it", 1, QUILT),
    ("L55", "mum", "Mum sleeping", 1, MUM_SLEEP),
    # 06 where it lived, L56 to L61
    ("L56", "mum", "me in the doorway, the Boxes over the bed in lamp light", 2,
     still([1.1, 3.15, 1.75], [-0.9, 0.6, 1.25], 16)),
    ("L57", "mum", "the quilt at her shoulders", 2, SHOULDERS),
    ("L58", "front", "the mug on the dark sill, at night", 4, still([-1.3, -4.2, 1.0], [-0.8, -4.45, 0.86], 35)),
    ("L59", "front", "the frames on the dark ceiling, at night", 4, still([-3.55, -3.0, 0.75], [-4.3, -3.2, 2.35], 18)),
    ("L60", "mum", "the joints in lamp light", 2, JOINTS),
    ("L61", "mum", "back to the still side-on wide, the face unchanged", 2, WIDE),
    # 07 ladder height, L62 to L74
    ("L62", "mum", "Mum's room in the morning, the corner empty, Mum asleep", 2, WIDE),
    ("L63", "front", "the clock wide: 24 again, outside tape, no marker", 4, CLOCK),
    ("L64", "hall", "Mum in the hall in the quilt, the first sun from the front room", 2,
     still([-3.9, -0.95, 1.5], [-1.6, -0.6, 1.25], 22)),
    ("L65", "front", "to the sill, the mug", 2, still([-3.8, -3.3, 1.5], [-1.2, -4.0, 1.1], 20)),
    ("L66", "front", "her head tilting up, then her eyeline to the frames on the ceiling", 2,
     c([0, [-2.25, -3.45, 1.3], [-1.3, -3.96, 1.5], 30], [0.5, [-2.25, -3.45, 1.3], [-1.3, -3.96, 1.5], 30],
       [1, [-2.25, -3.45, 1.3], [-4.25, -3.2, 2.3], 22])),
    ("L67", "front", "\"That's LADDER HEIGHT\"", 2, still([-2.3, -3.35, 1.45], [-1.35, -3.95, 1.45], 30)),
    ("P02", "front", "the two-shot in gold sun, the laugh", 2, still([-1.0, -2.0, 1.5], [-2.0, -3.95, 1.25], 15)),
    ("L68", "front", "Mum sitting on a box (to L69)", 2, still([-2.5, -2.8, 1.3], [-1.6, -4.2, 0.95], 17)),
    ("L70", "front", "both of us laughing", 2, still([-0.8, -2.5, 1.45], [-1.95, -4.0, 1.1], 15)),
    ("L71", "front", "unpacking the stack the old way: a two-shot", 2, still([-0.85, -2.3, 1.5], [-2.2, -4.1, 1.1], 15)),
    ("L72", "front", "she points, I put it there", 2, still([-1.2, -4.5, 1.5], [-3.3, -3.4, 1.3], 20)),
    ("L73", "front", "coats on the hooks by the door", 2, still([-2.6, -3.4, 1.6], [-4.4, -4.5, 1.35], 20)),
    ("L73.2", "kitchen", "the kettle moved left, that end of the counter bare", 2,
     still([1.95, -2.1, 1.6], [1.5, -3.6, 0.95], 22)),
    ("L74", "front", "the photos left up, in the sun", 2, still([-2.85, -2.6, 1.15], [-4.3, -3.3, 2.3], 18)),
    # 08 the last box, L75 to L78
    ("L75", "hall", "the folded boxes at Mum's feet, the cupboard opening", 2, still([-0.6, -1.25, 2.15], [1.45, -0.75, 1.15], 20)),
    ("L76", "hall", "the box on the shelf, its dent", 4, SHELF),
    ("L77", "hall", "the smile", 4, SMILE),
    ("L78", "hall", "Mum swings the cupboard door shut; the smile in view till the gap closes on \"it\", then the door",
     2, still([-0.6, -1.25, 2.15], [1.45, -0.75, 1.3], 24)),
]

shots = []
for i, (at, room, what, step, cam) in enumerate(SHOTS):
    s = {"id": f"S{i + 1:02d}", "cam": cam, "hand": 0.006 if step == 1 else 0.004, "step": step,
         "room": room, "what": what}
    if step == 4 or cam in (CLOCK,):
        s["hand"] = 0.0          # locked off
    if i:
        s["at"] = at
    shots.append(s)

# ---------------------------------------------------------------------------------------------------- acting
# Every place change happens on a cut: put() writes a zero-length step (no walk, no footsteps) and a key with
# blend 0, so nothing starts moving in the shot before. A put() resets every number it doesn't set. walk() is a
# move inside a shot (footsteps on the boards).
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "lie": None, "sit": False,
           "hide_parts": [], "part_offset": {}, "blink": True, "width": 0.88}   # R6 shoulders are wider than the hall
acting = {"me": [], "mum": []}


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


def tremble_arms(who, a, n, lo, hi, step=0.09):   # arms shaking: small fast steps
    for k in range(n):
        v = lo if k % 2 else hi
        acting[who].append({"at": f"{a}+{k * step:.2f}", "arms": [v, v + 2], "blend": step * 0.8})


MUM_BED = [0.27, 1.92, 0.59]
ME_BED = [-4.12, 1.28, 0.75]
IN_BED = {"lie": [-88, 0, 90], "head": [-55, 0], "side": [24, 0], "expr": "asleep", "blink": False, "width": 1.0,
          "part_offset": {"neck": [0, -0.04, 0], "arm-1": [0.0, -0.03, 0]},
          "hide_parts": ["arm1", "leg-1", "leg1", "torsom", "collar"]}
ME_IN_BED = {"lie": [-88, 0, 0], "hide_parts": ["arm1", "arm-1", "leg-1", "leg1", "torsom", "collar"]}

# me
put("me", 0, [-0.8, -0.76], yaw=90, arms=[48, 0], side=[-25, 0], lean=6)        # my hand at the bottom box
put("me", "L02", [-0.75, -0.76], yaw=90, arms=[55, 55], side=[-22, -22], lean=6)
hide("me", "L03")
put("me", "L05", [-2.1, -2.45], yaw=-150, arms=[78, 78], side=[-10, -10], head=[0, 8])   # carrying a box
walk("me", "L06-0.05", [-2.6, -3.2], arms=[78, 78], side=[-10, -10])
hide("me", "L06")
put("me", "L08", [-2.4, -3.6], yaw=yaw_to([-2.4, -3.6], [-1.5, -2.6]), arms=[78, 78], side=[-10, -10], head=[0, 26],
    expr="asleep", blink=False)                                                   # my face to a box
hide("me", "L09")
put("me", "L16", ME_BED, **ME_IN_BED)                                            # awake in bed in the dark
hide("me", "L17")
put("me", "L30", [-1.22, -3.1], yaw=180, lean=-10, arms=[78, 78], side=[-8, -14])  # pulling at a joint
key("me", "L31", arms=[78, 80], blend=0.05)
tremble_arms("me", "L31", 13, 75, 81)
hide("me", "L32")                                                                 # the joint inserts
put("me", "L34", [-1.3, -3.15], yaw=180, arms=[30, 30])                            # stepping back
walk("me", "L34+0.9", [-1.3, -3.6], arms=[10, 10], keep_yaw=True)
put("me", "L34b", [1.25, -2.92], yaw=0, head=[0, 32])                              # at the counter, looking down
hide("me", "L34c")
hide("me", "L36")                                                                 # my eyes: the camera
put("me", "L39", ME_BED, **ME_IN_BED, expr="terrified", blink=False)              # awake under it
key("me", "L40", expr="worried", blend=0.3)
put("me", "L43", [1.45, -2.1], yaw=-130, head=[0, 22])                            # breakfast, wrecked
put("me", "L44", ME_BED, **ME_IN_BED, expr="wide", blink=False)                   # 3 a.m.: eyes open
put("me", "L45", [-2.75, -0.78], yaw=90, expr="wide")                            # out in the hall
walk("me", "L46-0.1", [-2.1, -0.78], expr="wide")
hide("me", "L46")
put("me", "L47.2", [-1.22, -0.5], yaw=180, expr="wide")
hide("me", "L48")                                                                 # I'm the camera in the wides
put("me", "L51", [-1.15, 0.62], yaw=90, arms=[40, 0], side=[-6, 0], expr="wide")  # my hand at the lamp's switch
key("me", "L51+0.3", arms=[38, 0], side=[-6, 0], blend=0.2)
hide("me", "L52")
put("me", "L56", [-1.22, -0.35], yaw=180, expr="wide")
hide("me", "L57")
put("me", "P02", [-2.4, -3.75], yaw=yaw_to([-2.4, -3.75], [-1.6, -4.1]), expr="grin")
hide("me", "L68")
put("me", "L70", [-2.3, -3.7], yaw=yaw_to([-2.3, -3.7], [-1.6, -4.3]), expr="grin", tremble=1.2)
put("me", "L71", [-2.8, -3.94], yaw=0, arms=[78, 78], side=[-10, -10], expr="grin")
put("me", "L72", [-2.9, -4.0], yaw=-60, arms=[78, 78], side=[-10, -10], expr="soft")
walk("me", "L72+1.0", [-3.6, -3.6], arms=[78, 78], side=[-10, -10])
put("me", "L73", [-3.85, -4.15], yaw=-90, arms=[0, 92], expr="soft")             # a coat on its hook
hide("me", "L73.2")

# Mum
hide("mum", 0)
put("mum", "L06", [0.45, -1.95], yaw=0, head=[0, 22])                             # tired in the kitchen doorway
put("mum", "L07", [-3.85, -2.6], yaw=-90, arms=[75, 75], side=[-25, -25], head=[0, -6])   # hanging a frame
talk("mum", "L07", "L07>")
hide("mum", "L08")
put("mum", "L09", [-3.0, -3.25], yaw=0, lean=10, arms=[22, 22], side=[-14, -14], head=[0, 24])
walk("mum", "L09+1.15", [-3.0, -3.25], lean=10, arms=[22, 22], side=[-14, -14])
walk("mum", "L09+2.0", [-3.0, -3.8], lean=10)                                    # pushing the box to the stack
hide("mum", "L10")
put("mum", "L11", [-1.3, -3.96], yaw=90, arms=[70, 0], head=[0, 22])              # her mug, head down
key("mum", "L11.2", arms=[84, 0], blend=0.35)
talk("mum", "L11", "L11>")
put("mum", "L13", [-2.55, -0.8], yaw=90, arms=[40, 0], head=[0, 22])               # carrying it toward the Boxes
walk("mum", "L13+1.2", [-1.6, -0.77], arms=[40, 0], head=[0, 22])
walk("mum", "L14-0.03", [-1.25, -0.77], arms=[40, 0], head=[0, 22])               # ...to her own door
hide("mum", "L14")
put("mum", "L17", [1.0, -2.89], yaw=0, arms=[78, 74], head=[0, 22])                # at the counter, back to it
key("mum", "L21", arms=[80, 78], blend=0.4)
hide("mum", "L22")
put("mum", "L24", [-3.9, -1.95], yaw=0, head=[0, 25])                             # crossing under the photos
walk("mum", "L25-0.03", [-3.9, -3.8], head=[0, 25])
hide("mum", "L25")
put("mum", "L43", [0.75, -2.89], yaw=0, arms=[78, 74], head=[0, 12])              # breakfast
talk("mum", "L43.1", "L43>")
hide("mum", "L44")
put("mum", "L48", MUM_BED, yaw=0, **IN_BED)                                       # asleep under the quilt
put("mum", "L64", [-1.3, -0.77], yaw=-90, arms=[22, 22], side=[-12, -12], head=[0, 14])   # in the quilt
walk("mum", "L65-0.03", [-2.5, -0.77], arms=[22, 22], side=[-12, -12], head=[0, 14])
put("mum", "L65", [-2.7, -2.35], yaw=130, arms=[22, 22], side=[-12, -12], head=[0, 14])
walk("mum", "L65+1.1", [-1.3, -3.9], arms=[22, 22], side=[-12, -12])
key("mum", "L65+1.1", yaw=90, arms=[70, 22], blend=0.3)
put("mum", "L66", [-1.3, -3.85], yaw=90, arms=[70, 22], side=[-12, -12], head=[0, 10])
key("mum", "L66.1", yaw=-105, head=[0, -34], blend=0.5)                           # for once, she looks up
put("mum", "L67", [-1.3, -3.85], yaw=-105, arms=[70, 22], side=[-12, -12], head=[0, -30], expr="grin")
talk("mum", "L67.1", "L67>")
put("mum", "P02", [-1.6, -4.1], yaw=150, arms=[60, 30], side=[-12, -12], head=[0, 6], expr="squeeze", tremble=2.4)
put("mum", "L68", [-1.6, -4.3, -0.085], yaw=180, arms=[50, 25], side=[-10, -10], expr="squeeze", tremble=2.0, sit=True)
put("mum", "L70", [-1.6, -4.3, -0.085], yaw=165, arms=[50, 25], side=[-10, -10], expr="grin", tremble=1.6, sit=True)
put("mum", "L71", [-1.6, -4.1], yaw=0, arms=[45, 45], side=[-10, -10], expr="soft")
put("mum", "L72", [-2.1, -2.6], yaw=-90, arms=[0, 95], expr="soft")               # she points
put("mum", "L73", [-3.15, -3.55], yaw=-90, arms=[20, 20], expr="soft")
put("mum", "L73.2", [0.95, -2.89], yaw=0, arms=[78, 78], head=[0, 15], expr="soft")   # the kettle to the left
put("mum", "L75", [0.2, -0.74], yaw=90, arms=[0, 0], head=[0, 5])                  # the hall cupboard
key("mum", "L75.2", arms=[0, 18], blend=0.2)
key("mum", "L75.2+0.7", arms=[0, 4], blend=0.5)
put("mum", "L78", [0.2, -0.74], yaw=90, arms=[0, 18], head=[0, 5])                 # she swings it shut
key("mum", "L78.2", arms=[0, 6], blend=0.6)

# ---------------------------------------------------------------------------------------------------- cues
cues = [
    # the time of day (set.py TIME_LIGHTS): cold dawn, near-black nights, 3 a.m., the first sun, the cupboard
    {"at": 0, "name": "time", "set": "dawn"},
    {"at": "L16", "name": "time", "set": "night"},
    {"at": "L17", "name": "time", "set": "dawn"},
    {"at": "L36", "name": "time", "set": "night"},
    {"at": "L40", "name": "time", "set": "dawn", "dur": 1.2},      # my window greys slowly toward dawn
    {"at": "L44", "name": "time", "set": "night3"},
    {"at": "L45", "name": "time", "set": "night3", "exposure": 1.5},   # the dark hall: only the glow from her door
    {"at": "L48", "name": "time", "set": "night3"},
    {"at": "L62", "name": "time", "set": "dawn"},
    {"at": "L64", "name": "time", "set": "sun"},
    {"at": "L75", "name": "time", "set": "end"},
    # the Boxes: found where it already stands when a scene starts, never seen moving
    {"at": 0, "name": "boxes", "pose": "hall", "face": "frown"},
    {"at": "L14", "name": "boxes", "hidden": True},
    {"at": "L17", "name": "boxes", "pose": "kitchen", "face": "stare"},
    {"at": "L26", "name": "boxes", "pose": "front", "face": "sideways"},
    {"at": "L36", "name": "boxes", "pose": "mine", "face": "many_eyes"},
    {"at": "L41", "name": "boxes", "hidden": True},
    {"at": "L44", "name": "boxes", "pose": "over_bed", "face": "wide"},
    {"at": "L62", "name": "boxes", "hidden": True},
    {"at": "L75", "name": "boxes", "pose": "shelf", "face": "smile"},
    # the stack by the door (the clock): 24, 18, 12, 4 with eyes, 0 with clean squares in the dust, 24 again
    {"at": 0, "name": "stack", "count": 24},
    {"at": "L15", "name": "stack", "count": 18},
    {"at": "L17", "name": "stack", "count": 12},
    {"at": "L26", "name": "stack", "count": 4, "eyes": True},
    {"at": "L36", "name": "stack", "count": 0, "dust": True},
    {"at": "L63", "name": "stack", "count": 24},
    {"at": "L71", "name": "stack", "count": 18},
    {"at": "L72", "name": "stack", "count": 12},
    {"at": "L75", "name": "stack", "count": 0},
    # the loose front-room boxes: eyes on morning 3, gone with the stack (no loose box from L41 to L63)
    {"at": 0, "name": "loose", "on": True},
    {"at": "L26", "name": "loose", "on": True, "eyes": True},
    {"at": "L36", "name": "loose", "on": False},
    {"at": "L68", "name": "loose", "on": [0], "seat": [-1.6, -4.3, 0]},
    {"at": "L71", "name": "loose", "on": [0, 2]},
    # the quilt's box (L09): its flaps folded shut over the quilt, then pushed to the stack; then it's in the stack
    {"at": 0, "name": "quiltbox", "open": 1.0},
    {"at": "L09+0.1", "name": "quiltbox", "open": 0.0, "dur": 1.0},
    {"at": "L09+1.2", "name": "quiltbox", "push": 1.0, "dur": 0.8},
    {"at": "L10", "name": "quiltbox", "hidden": True},
    # the photos at eye height, then up the wall and across the ceiling from morning 2 on
    {"at": 0, "name": "photos", "where": "low"},
    {"at": "L17", "name": "photos", "where": "up"},
    # the mug: on the sill every morning, in Mum's hand, back on the sill where it lived
    {"at": 0, "name": "mug", "where": "sill"},
    {"at": "L11.2", "name": "mug", "where": "hand", "who": "mum", "arm": "arm-1"},
    {"at": "L14", "name": "mug", "where": "sill"},
    {"at": "L43", "name": "mug", "where": "counter", "pos": [0.45, -3.55]},
    {"at": "L44", "name": "mug", "where": "sill"},
    {"at": "L65+1.15", "name": "mug", "where": "hand", "who": "mum", "arm": "arm-1"},
    {"at": "L71", "name": "mug", "where": "sill"},
    # the tape: five full rolls heaped on the counter (morning 2), the same five as bare cores in a row
    # (mornings 3 and 4), gone after 3 a.m. (the Boxes' traces go; what it put where it lived stays)
    {"at": 0, "name": "tape", "state": "heap"},
    {"at": "L26", "name": "tape", "state": "row"},
    {"at": "L62", "name": "tape", "state": "none"},
    {"at": 0, "name": "kettle", "side": "right"},
    {"at": "L73.2+0.35", "name": "kettle", "side": "left"},
    {"at": 0, "name": "coats", "on": False},
    {"at": "L73", "name": "coats", "on": True},
    {"at": 0, "name": "pile", "on": False},
    {"at": "L75", "name": "pile", "on": True},
    {"at": 0, "name": "bedquilt", "on": False},
    {"at": "L44", "name": "bedquilt", "on": True},
    {"at": "L64", "name": "bedquilt", "on": False},
    {"at": 0, "name": "cape", "on": False},
    {"at": "L64", "name": "cape", "on": True},
    {"at": "L70", "name": "cape", "on": False},         # off once she's laughing: we unpack
    {"at": 0, "name": "carry", "on": False},
    {"at": "L05", "name": "carry", "who": "me", "on": True},
    {"at": "L06", "name": "carry", "on": False},
    {"at": "L08", "name": "carry", "who": "me", "on": True},
    {"at": "L09", "name": "carry", "on": False},
    {"at": "L71", "name": "carry", "who": "me", "on": True},
    {"at": "L73", "name": "carry", "on": False},
    # the doors: Mum's shut on morning 3 and found open at 3 a.m.; the hall cupboard opened at L75 and swung shut
    # so the gap closes on "it"
    {"at": "L26", "name": "door", "door": "mum", "open": 0.0},
    {"at": "L44", "name": "door", "door": "mum", "open": 1.0},
    {"at": "L75.2", "name": "door", "door": "cupboard", "open": 1.0, "dur": 0.9},
    {"at": "L78.2-0.85", "name": "door", "door": "cupboard", "open": 0.0, "dur": 1.1},
    # Mum's room at 3 a.m.
    {"at": 0, "name": "nightlight", "on": False},
    {"at": "L44", "name": "nightlight", "on": True},
    {"at": "L62", "name": "nightlight", "on": False},
    {"at": 0, "name": "lamp", "on": 0.0},
    {"at": "L51.1", "name": "lamp", "on": 1.0, "dur": 0.8},   # it comes up slowly, the first warm light
    {"at": "L62", "name": "lamp", "on": 0.0},
]

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L02", "kind": "tape", "db": -14},                                # the peel, under "PEELED" (not frame 0)
    {"at": "L04.3", "kind": "thud", "db": -18},                              # soft, on "a FROWN."
    {"at": "L16.1", "kind": "scrape", "db": -20, "dur": 2.2, "distant": True},   # through a wall
    {"at": "L43>", "kind": "scrape", "db": -20, "dur": 3.0, "distant": True},    # cut dead by H2 on "STOPPED"
    {"at": "L36", "kind": "sting", "db": -10},
    {"at": "L45.1", "kind": "riser", "db": -20, "dur": 1.4},
    {"at": "P01+0.2", "kind": "creak", "tone": "cardboard", "db": -20, "dur": 1.0},   # one slow papery flex
    {"at": "L51.1", "kind": "click", "db": -12},                             # the lamp switch, audible
    {"at": "L75.3", "kind": "door", "db": -18},                              # the cupboard, soft
]

story = {
    "slug": "ep17-moving-day",
    "title": "The box was taped shut from the inside",
    "made_for_kids": False,
    "premise": "I've moved with Mum into a smaller house with low ceilings after the old one was sold. Mum hasn't laughed since. Something built from our own moving boxes stands in a different room each morning, taller each time, with a new marker face, while the stack by the door shrinks and Mum's things turn up in odd places.",
    "twist": "It puts everything where it lived in the old house: the mug on the old kitchen windowsill, the photos at the old wall's height, and at 3 a.m. its hands were tucking the old quilt round Mum, because in the old house her room was the cold one.",
    "world": "a small single-storey house half moved into: low ceilings, off-white walls, honey boards, a stack of taped moving boxes by the front door, Mum's room lit by one cold nightlight",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#b98aff",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#0d1015", "fog_density": 0.02, "fog_start": 1.5, "sky": "#0b0d11", "sky_strength": 1.0,
             "exposure": 1.0},
    "grade": {"shadows": [-0.02, 0.0, 0.04], "highlights": [0.0, 0.005, 0.01], "saturation": 0.85, "contrast": 1.1,
              "vignette": 0.42, "bloom": 0.22, "grain": 0.014, "red_line": 0.79},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    # dorian on G2 at 74, no melody until home comes back: the piano enters at P02 ("the piano is the old house")
    "music": {"root": 43, "mode": "dorian", "bpm": 74, "seed": 17,
              "sections": [
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L14", "voices": ["drone", "pad", "pulse"], "energy": 0.35},
                  {"at": "L16", "voices": ["drone"], "energy": 0.3},
                  {"at": "L17", "voices": ["drone", "pad", "pulse"], "energy": 0.42},
                  {"at": "L25", "voices": ["drone", "pad", "pulse"], "energy": 0.5},
                  {"at": "L30", "voices": ["drone", "pad", "pulse"], "energy": 0.6},
                  {"at": "L36", "voices": ["drone", "choir"], "energy": 0.35},
                  {"at": "L41", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L44", "voices": ["drone"], "energy": 0.25},
                  {"at": "L45", "voices": ["drone", "pad", "choir"], "energy": 0.4},
                  {"at": "L47", "voices": ["drone", "pad", "choir"], "energy": 0.55},
                  {"at": "L51.1", "voices": ["pad"], "energy": 0.22},
                  {"at": "L56", "voices": ["drone", "pad", "choir"], "energy": 0.4},
                  {"at": "L62", "voices": ["pad"], "energy": 0.25},
                  {"at": "P02", "voices": ["piano", "pad", "drone"], "energy": 0.5, "mode": "major", "root": 41},
                  {"at": "L75", "voices": ["piano", "pad"], "energy": 0.3},
                  {"at": "L78", "voices": ["drone"], "energy": 0.3},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "L44", "lufs": -34},
                  {"kind": "room", "from": "L44", "to": "L62", "lufs": -38},
                  {"kind": "room", "from": "L62", "to": "end", "lufs": -34},
                  {"kind": "hum", "from": "L17", "to": "L22", "lufs": -40},
                  {"kind": "hum", "from": "L34b", "to": "L35", "lufs": -40},
                  {"kind": "hum", "from": "L43", "to": "L44", "lufs": -40},
                  {"kind": "hum", "from": "L73.2", "to": "L74", "lufs": -42},
              ],
              "sfx": sfx,
              # three holes: the music, ambience and footsteps fall and the voice plays on
              "music_drops": [{"from": "L36-0.6", "to": "L36.2", "keep": ["sting"]},
                              {"from": "L44.2", "to": "L45"},
                              {"from": "L49-0.6", "to": "L51.1", "db": -45.0, "keep": ["creak", "click"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
