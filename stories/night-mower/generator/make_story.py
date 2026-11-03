"""Writes ../story.json for night-mower "He Mows With His Eyes SHUT" (batch 6, slot P3; script.md).

Run from anywhere: python stories/night-mower/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the 58 shots with their cameras and
who stands where in each, the tracks set.py animates (the lid, the eye, the meter, the hall pictures, the blinds ...),
the score and the sound. Shot ids match script.md (S01 ... S58, with S01b and S49b as extra cuts).

Places (metres, the ground is z = 0; yaw 0 faces -y, 90 faces +x, 180 faces +y, -90 faces -x):
  the street: y -4 .. 4, running along x. Our side (north) has the sidewalk y 4 .. 5.2 and the yards y 5.2 .. 12.
  our yard x -15 .. -0.2 (the bald circle at (-2.6, 8.4)), the low fence at x = 0, Mr. Odell's lawn x 0.2 .. 15
  (the hump and the Head's lid at (7.2, 8.6)), his mint house behind it (y 12 and up), our butter-yellow house
  x -14 .. -4 (the bedroom upstairs at z 2.8, its window at x = -6, the porch at (-8.2, 10.8)).
  across the street: the south houses (front wall y = -9), the coral one at x = -6 leans toward his lawn.
  the hall is built at x = 100 (z 0), the bedside clock at x = 130.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

LOOP = 0.25
GAP = 0.12
# word-check pins: the voice's own spelling for lines the word check mishears (captions stay as written)
TEMPO = {}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]

# ---------------------------------------------------------------------------------------------------- cast
cast = {
    "me": {"age": "adult", "skin": "#e0ac84", "shirt": "#1fb5a8", "pattern": "solid", "collar": "#188f85",
           "pants": "#8a8d93", "shoes": "#f4f4f4", "sleeves": "long", "hair": "cap", "hair_c": "#3b2416",
           "hat": "none", "extras": ["hooddown"], "extra_c": "#1fb5a8", "face": {"eyes": "round", "brows": True, "ink": "#2a1810"}},
    "dad": {"age": "adult", "skin": "#e8b48a", "shirt": "#d93a3a", "pattern": "plaid", "pattern_c": "#ffffff",
            "collar": "#b32d2d", "pants": "#c9b27a", "shoes": "#f4f4f4", "sleeves": "short", "hair": "cap",
            "hair_c": "#c99a52", "hat": "bucket", "hat_c": "#3fa65a", "width": 1.05,
            "face": {"eyes": "round", "brows": True, "ink": "#2a1810"}},
    "dadn": {"age": "adult", "skin": "#e8b48a", "shirt": "#d93a3a", "pattern": "plaid", "pattern_c": "#ffffff",
             "collar": "#b32d2d", "pants": "#c9b27a", "shoes": "#f4f4f4", "sleeves": "long", "hair": "cap",
             "hair_c": "#c99a52", "hat": "none", "extras": ["coat"], "extra_c": "#1f2f66", "width": 1.05,
             "face": {"eyes": "round", "brows": True, "ink": "#2a1810"}},
    "odell": {"age": "adult", "skin": "#e8bf9a", "shirt": "#2f6b3a", "pattern": "solid", "collar": "#25552d",
              "pants": "#6b4a2e", "shoes": "#5a3a22", "sleeves": "long", "hair": "cap", "hair_c": "#f2f2ee",
              "hat": "none", "height": 0.97, "width": 1.0,
              "face": {"eyes": "round", "brows": True, "ink": "#2a1810", "brow_w": 1.7}},
}

# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {w: [] for w in cast}


def _put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, **NEUTRAL, "hidden": False, "expr": "neutral", **kw})


def stage(at, **ents):
    """Who stands where from `at`: who=(pos, yaw, expr, extras dict). Anyone not named is hidden."""
    for who in cast:
        if who in ents:
            pos, yaw, expr, *rest = ents[who]
            kw = dict(rest[0]) if rest else {}
            if who == "odell" and expr == "shut" and "arms" not in kw:
                kw["arms"] = [62, 62]          # his hands on the mower's handle bar
            _put(who, at, pos, yaw=yaw, expr=expr, **kw)
        else:
            acting[who].append({"at": at, "hidden": True, "blend": 0})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": pos, **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


# ---------------------------------------------------------------------------------------------------- cameras
def C(loc, tgt, lens, loc2=None, tgt2=None, lens2=None):
    ks = [[0, list(loc), list(tgt), lens]]
    if loc2 or tgt2 or lens2:
        ks.append([1, list(loc2 or loc), list(tgt2 or tgt), lens2 or lens])
    return ks


shots = []
looks = {}


def shot(sid, at, cam, note, day=0, step=2, hand=0.008, follow=None, **look):
    d = {"id": sid, "cam": cam, "step": step, "hand": hand, "note": note}
    if at is not None and sid != "S01":
        d["at"] = at
    if follow:
        d["follow"] = follow
    shots.append(d)
    looks[sid] = {"day": day, **look}


Z2 = 2.8   # the bedroom floor
# ---------------------------------------------------------------------------------------------------- 01 the rule
shot("S01", 0, C((9.0, 5.2, 1.2), (9.0, 9.4, 1.45), 36, (9.0, 6.2, 1.2), (9.0, 9.4, 1.5), 40),
     "frame 1: low, floodlit, Mr. Odell pushing the red mower straight at us, eyes shut, pushing in")
stage(0, odell=((9.0, 10.9, 0), 0, "shut", {"arms": [0, 0]}))
walk("odell", "L01.2", (9.0, 9.6, 0))
shot("S01b", "L01.2", C((9.7, 7.4, 0.95), (9.0, 9.5, 1.55), 42, (9.4, 8.0, 1.0), (9.0, 9.4, 1.56), 48),
     "closer: his shut-eyed face over the deck, the hit on RUNNING")
stage("L01.2", odell=((9.0, 9.6, 0), 0, "shut"))
walk("odell", "L02", (9.0, 9.0, 0))
shot("S02", "L02", C((-6.0, 13.6, 4.35), (-6.0, 12.3, 4.35), 32, (-6.0, 13.1, 4.35), (-6.0, 12.3, 4.35), 34),
     "inside the dark room, close on the blinds: one slat dips and a green stripe cuts across")
stage("L02")
shot("S03", "L03", C((-2.6, -1.8, 3.1), (-6.4, -9.0, 3.9), 38, (-3.2, -2.6, 3.2), (-6.6, -9.0, 3.9), 40),
     "night: the coral house across the street, one blind slat in its upstairs window bent down")
stage("L03")
shot("S04", "L04", C((-6.0, 6.0, 2.4), (-6.0, -9.0, 2.6), 20, (-6.0, 5.2, 2.4), (-6.0, -9.0, 2.6), 21),
     "the coral house straight on, level: it leans toward his lawn, its porch light at the slant")
stage("L04")
shot("S05", "L05", C((6.0, 0.4, 4.0), (6.0, -9.0, 3.9), 20, (6.0, -0.4, 4.0), (6.0, -9.0, 3.9), 21),
     "three upstairs windows, blinds dropping shut left to right")
stage("L05")
shot("S06", "L06", C((7.8, 8.1, 1.45), (9.0, 9.6, 1.6), 52, (8.3, 8.5, 1.5), (9.0, 9.6, 1.6), 58),
     "tight on Mr. Odell's face, eyes shut, the floodlights behind his white hair, handle in the bottom of frame")
stage("L06", odell=((9.0, 9.7, 0), 0, "shut"))
walk("odell", "L07", (9.0, 9.0, 0))

# ---------------------------------------------------------------------------------------------------- 02 Dad (day)
shot("S07", "L07", C((-3.4, 5.6, 1.7), (-1.1, 8.2, 1.65), 36, (-3.1, 5.9, 1.7), (-1.1, 8.2, 1.65), 40),
     "day: Dad at the low fence in his garden cap, angry, glaring over at the green lawn", day=1)
stage("L07", dad=((-1.1, 8.1, 0), 90, "angry"))
shot("S08", "L08", C((-5.0, 5.6, 1.5), (-2.6, 8.3, 0.7), 30, (-4.6, 5.9, 1.4), (-2.6, 8.3, 0.7), 32),
     "our yard: Dad bent over the bald circle, a seed bag beside him, worried", day=1)
stage("L08", dad=((-3.9, 8.5, 0), 90, "worried", {"lean": 38}))
shot("S09", "L09", C((-2.6, 8.4, 9.0), (-2.6, 8.4, 0), 34, (-2.6, 8.4, 7.8), (-2.6, 8.4, 0), 34),
     "top-down on the bald circle: clean edge, grass all round (plant 1)", day=1, hand=0.0)
stage("L09")
shot("S10", "L10", C((-5.4, 6.0, 2.0), (-2.9, 8.3, 0.9), 30, (-5.0, 6.2, 1.9), (-2.9, 8.3, 0.9), 32),
     "seed scattering on the circle", day=1)
stage("L10", dad=((-4.0, 7.3, 0), 45, "neutral", {"lean": 28, "arms": [40, 40]}))
shot("S11", "L10.1", C((-4.4, 5.8, 3.0), (-2.6, 8.4, 0), 28, (-4.0, 6.0, 2.8), (-2.6, 8.4, 0), 30),
     "a sod roll laid on it, yellowing at the edges", day=1)
stage("L10.1", dad=((-4.0, 7.3, 0), 45, "neutral", {"lean": 20}))
shot("S12", "L11", C((-2.6, 5.4, 1.1), (-2.6, 8.4, 0.1), 26, (-2.9, 5.5, 1.0), (-2.6, 8.4, 0.1), 28),
     "the circle bare again, a sprinkler ticking over it", day=1)
stage("L11")
shot("S13", "L12", C((-5.2, 4.2, 1.9), (3.2, 12.0, 2.2), 20, (-4.6, 4.4, 1.9), (3.2, 12.0, 2.3), 20),
     "first wide: the two houses and the fence, Mr. Odell waving on his porch, Dad in the foreground", day=1)
stage("L12", dad=((-1.6, 6.4, 0), 90, "angry"), odell=((9.0, 11.4, 0), 0, "smile", {"side": [0, 140]}))
key("odell", "L12.2", side=[0, 105], blend=0.3)
key("odell", "L12.2+0.5", side=[0, 140], blend=0.3)
shot("S14", "L13", C((-1.2, 5.4, 1.66), (-1.2, 7.6, 1.66), 42, (-1.2, 5.8, 1.66), (-1.2, 7.6, 1.66), 46),
     "Dad's face, angry, a comic squint", day=1)
stage("L13", dad=((-1.2, 7.7, 0), 0, "angry"))
shot("S15", "L13.1", C((3.0, 5.4, 0.4), (8.4, 9.4, 0.2), 28, (3.6, 5.5, 0.4), (8.4, 9.4, 0.2), 30),
     "his lawn, every blade even, the stripes curving", day=1)
stage("L13.1")
shot("S16", "L14", C((129.2, -1.5, 1.05), (130.0, 0.0, 0.95), 40, (129.45, -1.2, 1.02), (130.0, 0.0, 0.95), 42),
     "night: the bedside clock reads 3:00 in red digits")
stage("L14")
shot("S17", "L14.1", C((-7.6, 14.6, Z2 + 1.4), (-9.5, 18.0, Z2 + 1.5), 26, (-7.9, 14.9, Z2 + 1.4), (-9.5, 18.0, Z2 + 1.5), 28),
     "Dad in his robe in my doorway, pointing at the window")
stage("L14.1", dadn=((-9.5, 18.1, Z2), 0, "neutral", {"arms": [0, 85]}))

# ---------------------------------------------------------------------------------------------------- 03 night one
shot("S18", "L15", C((-5.8, 13.0, Z2 + 1.55), (4.0, 9.2, 1.2), 62, (-5.8, 12.9, Z2 + 1.55), (4.6, 9.0, 1.2), 70),
     "through the blinds' gaps: the floodlit lawn, the red mower starting its line")
stage("L15", odell=((4.4, 10.9, 0), 0, "shut"))
walk("odell", "L16", (4.4, 9.4, 0))
shot("S19", "L16", C((-6.0, 10.2, 4.3), (-6.0, 12.1, 4.35), 34, (-6.0, 10.9, 4.35), (-6.0, 12.1, 4.35), 38),
     "outside the window, close on the blinds: one slat bends, Dad's eye in the gap, green on his face")
stage("L16", dadn=((-6.0, 13.0, Z2), 0, "neutral", {"lean": 6}))
shot("S19b", "L16.1", C((-6.6, 16.2, Z2 + 1.7), (-7.6, 14.2, Z2 + 1.6), 32, (-6.8, 15.8, Z2 + 1.7), (-7.6, 14.2, Z2 + 1.6), 34),
     "me behind him, worried")
stage("L16.1", dadn=((-6.0, 13.0, Z2), 0, "neutral"), me=((-7.6, 14.2, Z2), 180, "worried"))
shot("S20", "L17", C((-1.6, 9.8, 7.0), (7.2, 8.4, 0.0), 19, (-0.8, 9.6, 7.0), (7.2, 8.4, 0.0), 19),
     "high angle from our window onto his lawn: every stripe bowing round the hump (plant 2), held", hand=0.0)
stage("L17", odell=((12.0, 10.6, 0), 90, "shut"))
shot("S21", "L18", C((-9.8, 17.8, Z2 + 1.8), (-6.8, 13.4, Z2 + 0.9), 22, (-9.4, 17.4, Z2 + 1.8), (-6.8, 13.4, Z2 + 0.9), 22),
     "my room, the desk lamp swaying a little; the meter's bubble slides a tick", step=1)
stage("L18", dadn=((-6.0, 13.6, Z2), 0, "worried"), me=((-8.2, 14.6, Z2), 0, "scared"))
shot("S22", "L19", C((100.7, -0.9, 1.45), (103.0, 0.0, 1.5), 32, (101.0, -0.9, 1.45), (103.2, 0.0, 1.5), 32),
     "the hall: three pictures easing to a tilt", step=1)
stage("L19")
shot("S23", "L20", C((101.0, -0.95, 1.35), (106.0, -0.4, 1.5), 24, (101.6, -0.95, 1.35), (106.0, -0.4, 1.5), 24),
     "all three tilted the same way, the window at the hall's end glowing green")
stage("L20")
shot("S24", "L21", C((-6.8, 16.6, Z2 + 1.65), (-6.8, 13.0, Z2 + 1.55), 28, (-6.8, 16.2, Z2 + 1.65), (-6.8, 13.0, Z2 + 1.55), 30),
     "Dad at the window, shrugging, me beside him, worried")
stage("L21", dadn=((-6.0, 13.0, Z2), 180, "neutral", {"side": [55, 55]}), me=((-7.7, 13.2, Z2), 180, "worried"))
shot("S25", "L22", C((-5.3, 13.3, Z2 + 1.12), (-5.4, 12.45, Z2 + 0.94), 46, (-5.3, 13.1, Z2 + 1.1), (-5.4, 12.45, Z2 + 0.94), 50),
     "close on Dad's yellow spirit level on the sill, its bubble off-centre toward the lawn")
stage("L22")

# ---------------------------------------------------------------------------------------------------- 04 night two
shot("S26", "L23", C((-4.6, 8.2, 1.6), (-8.2, 10.8, 1.6), 38, (-4.9, 8.6, 1.6), (-8.2, 10.8, 1.6), 40),
     "our porch: Dad in his robe, binoculars raised, angry")
stage("L23", dadn=((-8.2, 10.8, 0.2), 90, "angry", {"arms": [80, 80]}))
shot("S27", "L23.2", C((-9.4, 10.2, 1.75), (7.0, 9.2, 1.2), 82, (-9.4, 10.2, 1.75), (6.4, 9.2, 1.2), 90),
     "over his shoulder: the floodlit lawn, Mr. Odell mowing, eyes shut", hand=0.004)
stage("L23.2", dadn=((-8.2, 10.8, 0.2), 90, "angry", {"arms": [80, 80]}), odell=((5.0, 10.6, 0), 0, "shut"))
walk("odell", "L24", (5.0, 9.3, 0))
shot("S28", "L24", C((-4.8, 16.6, Z2 + 1.5), (-7.6, 13.5, Z2 + 0.9), 24, (-5.0, 16.2, Z2 + 1.5), (-7.6, 13.5, Z2 + 0.9), 24),
     "me at the desk, scared, the empty chair rolls across to the window", step=1)
stage("L24", me=((-8.6, 13.3, Z2), 90, "scared"))
shot("S29", "L25", C((10.4, 6.6, 0.45), (7.2, 8.6, 0.65), 32, (9.8, 6.6, 0.5), (7.2, 8.6, 0.7), 34),
     "low on the lawn: the mower rolling over the top of the hump", step=1)
stage("L25", odell=((7.0, 11.0, 0.0), 0, "shut"))
walk("odell", "L25.2", (7.0, 8.7, 0.3))
walk("odell", "L26", (7.0, 7.0, 0.1))

# ---------------------------------------------------------------------------------------------------- 05 the eye
shot("S30", "L26", C((4.0, 5.2, 0.22), (6.3, 6.7, 0.12), 40, (4.4, 5.3, 0.22), (6.3, 6.7, 0.12), 42),
     "close on the lawn by the hump: a long line along the stripes rises a hand", step=1)
stage("L26", odell=((10.6, 6.0, 0), 90, "shut"))
shot("S31", "L27", C((7.2, 3.2, 1.4), (7.2, 8.0, 0.3), 26, (7.2, 3.4, 1.3), (7.2, 8.0, 0.3), 28),
     "mid: the lens-shaped flap of turf lifting along the hump, warm underside showing", step=1)
stage("L27", odell=((10.6, 6.0, 0), 90, "shut"))
shot("S32", "L27.1", C((7.0, 5.0, 0.35), (7.2, 8.6, 0.55), 30, (7.1, 5.4, 0.4), (7.2, 8.6, 0.55), 32),
     "lower: the dark gap widening", step=1)
stage("L27.1", odell=((10.6, 6.0, 0), 90, "shut"))
shot("S33", "L28", C((7.2, 0.6, 4.4), (7.2, 8.5, -0.1), 20, (7.2, 1.1, 4.2), (7.2, 8.5, -0.1), 20),
     "the test still: looking down into the open lid, the eye looking up, the mower at the edge, Mr. Odell eyes shut", step=1, hand=0.004, flood=0.55)
stage("L28", odell=((10.0, 6.6, 0), 90, "shut"))
shot("S34", "L28.2", C((4.6, 4.2, 1.7), (7.0, 8.6, -0.1), 30, (5.0, 4.8, 1.5), (7.0, 8.6, -0.1), 34),
     "closer, low from the west: the pupil, the highlight, the lid's edge", step=1, hand=0.004, flood=0.55)
stage("L28.2", odell=((10.0, 6.6, 0), 90, "shut"))
shot("S35", "L29", C((-4.6, 8.2, 1.6), (-8.2, 10.8, 1.6), 38, (-5.0, 8.6, 1.62), (-8.2, 10.8, 1.62), 44),
     "reverse: Dad on our porch, binoculars lowered a little, scared, lit green", step=1)
stage("L29", dadn=((-8.2, 10.8, 0.2), 90, "scared", {"arms": [45, 45], "tremble": 1.5}))
shot("S36", "L30", C((7.6, 1.4, 5.3), (7.2, 8.5, -0.2), 20, (7.4, 2.4, 4.8), (7.2, 8.5, -0.2), 22),
     "the eye, the highlight now aimed toward our porch", step=1, hand=0.004, flood=0.55)
stage("L30", odell=((10.0, 6.6, 0), 90, "shut"))
shot("S37", "L31", C((-15.0, 3.2, 0.95), (2.0, 5.0, 0.8), 28, (-12.0, 3.2, 0.95), (2.0, 5.0, 0.8), 28),
     "the street at night: a row of plain mailboxes leaning toward our house", step=1)
stage("L31")
shot("S38", "L31.1", C((-9.6, 10.0, 2.0), (-7.3, 11.9, 2.1), 34, (-9.2, 10.2, 2.0), (-7.3, 11.9, 2.1), 36),
     "our porch light swaying toward the lawn", step=1)
stage("L31.1")

# ---------------------------------------------------------------------------------------------------- 06 said plainly
shot("S39", "L32", C((3.4, 5.6, 0.9), (6.2, 8.2, 1.3), 30, (3.8, 5.8, 0.95), (6.2, 8.2, 1.3), 32),
     "the mower halting on the lawn, the open eye beyond it, the hum stops dead", step=1)
stage("L32", odell=((5.0, 8.3, 0), 0, "shut"))
shot("S40", "L33", C((5.4, 6.2, 0.65), (4.8, 8.2, 1.6), 38, (5.2, 6.5, 0.7), (4.8, 8.2, 1.62), 42),
     "Mr. Odell's face, eyes shut, tilted up toward my window")
stage("L33", odell=((4.8, 8.3, 0), 0, "shut", {"head": [0, -22]}))
shot("S41", "L33.2", C((-6.8, 16.6, Z2 + 1.65), (-6.8, 13.0, Z2 + 1.55), 30, (-6.8, 16.3, Z2 + 1.65), (-6.8, 13.0, Z2 + 1.55), 32),
     "me at the window, scared, nodding")
stage("L33.2", me=((-6.4, 13.0, Z2), 180, "scared", {"head": [0, 12]}))
key("me", "L33.2+0.5", head=[0, -8], blend=0.2)
key("me", "L33.2+0.9", head=[0, 12], blend=0.2)
shot("S42", "L34", C((7.2, 4.6, 1.5), (7.2, 9.0, 0.5), 30, (7.2, 4.8, 1.4), (7.2, 9.0, 0.5), 30),
     "low across the lawn: the open eye in the middle ground, his mint house behind", step=1)
stage("L34", odell=((10.6, 6.0, 0), 90, "shut"))
shot("S43", "L35", C((3.2, 8.5, 20.0), (3.2, 8.5, 0.0), 18, (3.2, 8.5, 17.0), (3.2, 8.5, 0.0), 18),
     "high above our roof: the open eye, the brow stripes, the low fence and our round bald circle in one frame", step=1, hand=0.0)
stage("L35")
shot("S44", "L36", C((7.2, 2.4, 5.4), (7.2, 8.6, 0.0), 24, (7.2, 3.0, 5.0), (7.2, 8.6, 0.0), 24),
     "the striped lawn over the eye, the stripes bowing over it", step=1)
stage("L36")
shot("S45", "L37", C((-2.6, 8.4, 9.0), (-2.6, 8.4, 0), 34, (-2.6, 8.4, 7.8), (-2.6, 8.4, 0), 34),
     "top-down on our bald circle again, in moonlight", hand=0.0)
stage("L37")
shot("S46", "L38", C((7.0, 4.0, 2.6), (7.2, 8.7, -0.15), 30, (7.1, 4.6, 2.2), (7.2, 8.7, -0.15), 36),
     "the eye, highlight on Dad", step=1, hand=0.004)
stage("L38", odell=((10.6, 6.0, 0), 90, "shut"))
shot("S47", "L38.2", C((-6.0, 5.4, 2.4), (-6.0, -9.0, 2.6), 21, (-6.0, 4.6, 2.4), (-6.0, -9.0, 2.6), 22),
     "the leaning coral house across the street, now read as turned toward the lawn")
stage("L38.2")

# ---------------------------------------------------------------------------------------------------- 07 neighbors
shot("S48", "L39", C((-4.6, 8.2, 1.6), (-8.2, 10.8, 1.6), 38, (-5.0, 8.6, 1.62), (-8.2, 10.8, 1.62), 40),
     "Dad on the porch lowering the binoculars, worried", step=1)
stage("L39", dadn=((-8.2, 10.8, 0.2), 90, "worried", {"arms": [45, 45]}))
shot("S49", "L40", C((-6.4, 9.2, 1.68), (-8.2, 10.8, 1.66), 46, (-6.8, 9.6, 1.68), (-8.2, 10.8, 1.66), 50),
     "Dad's face, eyes shut", step=1)
stage("L40", dadn=((-8.2, 10.8, 0.2), 90, "shut"))
shot("S49b", "L40.1", C((7.2, 0.6, 4.4), (7.2, 8.5, -0.1), 20, (7.2, 1.1, 4.2), (7.2, 8.5, -0.1), 20),
     "the lid sinks shut", step=1)
stage("L40.1", odell=((10.0, 6.6, 0), 90, "shut"))
shot("S50", "L40.2", C((100.7, -0.9, 1.45), (103.0, 0.0, 1.5), 32, (101.0, -0.9, 1.45), (103.2, 0.0, 1.5), 32),
     "the hall pictures easing back level over a second", step=1)
stage("L40.2")
shot("S51", "L41", C((-0.8, 4.6, 1.2), (0.2, 7.6, 1.0), 30, (-0.2, 4.8, 1.2), (0.4, 7.6, 1.0), 32),
     "Dad stepping over the low white fence onto the green lawn, eyes shut, cap off", step=1)
stage("L41", dadn=((-1.6, 7.6, 0), 90, "shut"))
walk("dadn", "L41+0.5", (-0.5, 7.6, 0))
walk("dadn", "L41+0.85", (0.0, 7.6, 0.42))
walk("dadn", "L41+1.2", (0.6, 7.6, 0))
walk("dadn", "L42", (2.0, 7.6, 0))
shot("S52", "L42", C((1.0, 5.8, 1.5), (3.0, 8.0, 1.5), 36, (1.3, 6.0, 1.5), (3.0, 8.0, 1.5), 40),
     "Mr. Odell, eyes shut, smiling, turning his face toward Dad's steps")
stage("L42", odell=((3.3, 8.0, 0), -90, "shut", {"head": [-25, 0], "arms": [0, 0]}), dadn=((2.0, 7.4, 0), 90, "shut"))
shot("S53", "L43", C((5.6, 4.8, 1.3), (5.2, 8.6, 1.15), 30, (5.5, 5.4, 1.25), (5.2, 8.6, 1.15), 32),
     "the two of them on the lawn: Dad with the cord, Mr. Odell steering, both eyes shut, the hum back")
stage("L43", odell=((5.6, 10.6, 0), 0, "shut"), dadn=((4.3, 10.7, 0), 0, "shut", {"arms": [60, 60]}))
walk("odell", "L43.1-0.15", (5.6, 9.7, 0))
walk("dadn", "L43.1-0.15", (4.3, 9.8, 0))
shot("S54", "L43.1-0.15", C((0.95, -1.2, 1.2), (0.28, -0.35, 0.98), 52, (0.8, -1.05, 1.15), (0.28, -0.35, 0.98), 56),
     "the lore shot: close on the handle bar, two lime strokes by the left grip", follow="odell", hand=0.003)
stage("L43.1-0.15", odell=((5.6, 9.7, 0), 0, "shut"), dadn=((4.3, 9.8, 0), 0, "shut", {"arms": [60, 60]}))
walk("odell", "L44", (5.6, 9.2, 0))
walk("dadn", "L44", (4.3, 9.3, 0))
shot("S55", "L44", C((-3.8, 11.4, 5.6), (6.0, 8.6, 0.4), 22, (-3.4, 11.2, 5.6), (6.0, 8.6, 0.4), 22),
     "the pair from my window, mowing a perfect curved stripe", hand=0.0)
stage("L44", odell=((7.4, 10.6, 0), 0, "shut"), dadn=((6.1, 10.7, 0), 0, "shut", {"arms": [60, 60]}))
walk("odell", "L45", (7.4, 8.6, 0))
walk("dadn", "L45", (6.1, 8.7, 0))
shot("S56", "L45", C((-4.8, 5.8, 1.5), (-2.8, 8.4, 0.9), 30, (-4.4, 6.0, 1.5), (-2.8, 8.4, 0.9), 32),
     "dawn-blue morning: Dad with the hose watering the bald circle, smiling", day=0.55)
stage("L45", dad=((-3.9, 8.5, 0), 90, "smile", {"arms": [50, 50]}))
shot("S57", "L45.2", C((-2.2, 6.4, 1.6), (0.9, 8.2, 1.6), 34, (-1.9, 6.6, 1.6), (0.9, 8.2, 1.6), 38),
     "Mr. Odell waving over the fence, eyes open, smiling", day=0.55)
stage("L45.2", odell=((1.0, 8.2, 0), -90, "smile", {"side": [0, 140]}))
key("odell", "L45.2+0.5", side=[0, 105], blend=0.3)
key("odell", "L45.2+1.0", side=[0, 140], blend=0.3)
shot("S58", "L46", C((7.2, 5.0, 0.5), (7.2, 8.6, 0.15), 28, (7.2, 5.1, 0.42), (7.2, 8.6, 0.12), 30),
     "back to 3 AM: low on the floodlit lawn, empty; the seam opens a crack and the eye looks into the lens", step=1, hand=0.002)
stage("L46")

# ---------------------------------------------------------------------------------------------------- tracks
tracks = {
    "lid": [[0, 0], ["L26", 0], ["L26+0.6", 0.03], ["L27", 0.03], ["L27+1.6", 0.7], ["L28.1", 1.0], ["L40.1", 1.0],
            ["L40.1+0.9", 0], ["L46+0.15", 0], ["L46+0.8", 0.1]],
    "eye": [[0, 0], ["L29", 1], ["L40", 1], ["L46", 2]],                      # stepped: 0 up, 1 at Dad, 2 at the lens
    "meter": [[0, 0], ["L18", 0], ["L18+1", 0.33], ["L24", 0.33], ["L24+1", 0.66], ["L31", 0.66], ["L31+0.8", 1.0],
              ["L40", 1.0], ["L40+1", 0], ["L46+0.1", 0], ["L46+0.7", 0.12]],
    "pic": [[0, 0], ["L19.1", 0], ["L19.1+0.8", 1], ["L40.2", 1], ["L40.2+1.0", 0]],
    "mail": [[0, 0], ["L31", 0], ["L31+0.8", 1], ["L40.2", 1], ["L40.2+1.0", 0]],
    "chair": [[0, 0], ["L24+0.3", 0], ["L24+2.0", 1]],
    "slat": [[0, 0], ["L02+0.1", 0], ["L02+0.5", 1], ["L02>", 1], ["L03", 0], ["L16", 0], ["L16+0.4", 1]],
    "sway": [[0, 0], ["L18", 0], ["L18+0.5", 1], ["L19", 0.5], ["L20", 0], ["L31.1", 0], ["L31.1+0.5", 1], ["L32", 0.4]],
    "binos": [[0, 0], ["L23", 1], ["L29", 0.5], ["L39", 0.5], ["L39+0.5", 0]],
    "sod": [[0, 0], ["L10.1", 1], ["L11", 0]],
    "sprink": [[0, 0], ["L11", 1], ["L12", 0]],
    "hose": [[0, 0], ["L45", 1], ["L46", 0]],
    "bw0": [[0, 0], ["L05.1+0.1", 0], ["L05.1+0.4", 1]],
    "bw1": [[0, 0], ["L05.1+0.6", 0], ["L05.1+0.9", 1]],
    "bw2": [[0, 0], ["L05.2", 0], ["L05.2+0.3", 1]],
}

premise = ("Our neighbor Mr. Odell has the greenest lawn on the street and his mower only runs at 3 AM. Everyone on our "
           "street obeys one rule: never look at his lawn while the mower is running. My dad has lost a lawn war to "
           "him for ten years, because ours has one perfectly round bald spot, and he sets an alarm to catch him cheating.")
twist = ("The street is built on a giant sleeping head. Mr. Odell's lawn is its eyebrow, our bald spot is where its "
         "hairline is going, and when he trims the brow the eye under the turf wakes and turns toward whoever is watching, "
         "tipping every house on it. Mr. Odell mows with his eyes shut so it never turns to him. Dad shuts his, the street "
         "settles, and the two rivals become a crew of two.")
world = ("a bright suburban cul-de-sac at three in the morning: a floodlit stripe-mown lawn with a low oval hump, a butter "
         "yellow house with a blinded upstairs window, a leaning coral house across the street, a low white fence, "
         "plain mailboxes and a red push mower on an orange cord")

story = {
    "slug": "night-mower",
    "title": "He Mows With His Eyes SHUT",
    "made_for_kids": False,
    "premise": premise,
    "twist": twist,
    "world": world,
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#b6ff3b",
    "gap": GAP,
    "tail": LOOP,
    "fade_in": False,
    "fade_out": False,
    "look": {"style": "closer", "fog": "#6f86c8", "fog_density": 0.012, "fog_start": 14.0, "sky": "#1b2a6b",
             "exposure": 0.0, "flash_safe": True, "hdri": "moonless_golf", "hdri_strength": 0.6, "hdri_visible": False},
    "grade": {"shadows": [0.0, 0.0, 0.05], "highlights": [0.02, 0.01, -0.02], "saturation": 1.12, "contrast": 1.06,
              "vignette": 0.3, "bloom": 0.3, "grain": 0.01, "red_line": 0.78},
    "caption": {"shadow": 0.6},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": {w: ks for w, ks in acting.items() if ks},
    "tracks": tracks,
    "looks": looks,
    "meter": tracks["meter"],
    "fx": [],
    "music": {"root": 50, "mode": "mixolydian", "bpm": 100, "seed": 6,
              "sections": [
                  {"at": 0, "voices": ["pulse", "piano"], "energy": 0.5},
                  {"at": "L07", "voices": ["pulse", "piano"], "energy": 0.55},
                  {"at": "L15", "voices": ["pulse", "pad"], "energy": 0.45},
                  {"at": "L24", "voices": ["pulse", "pad", "piano"], "energy": 0.55},
                  {"at": "L27", "voices": ["drone", "pad"], "energy": 0.6},
                  {"at": "L32", "voices": ["drone"], "energy": 0.5},
                  {"at": "L39", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L43", "voices": ["piano", "pad"], "energy": 0.5, "mode": "major", "root": 50},
                  {"at": "L46", "voices": ["drone"], "energy": 0.3},
              ]},
    "sound": {"floor": "grass", "steps_db": -22, "rev": 1,
              "ambience": [
                  {"kind": "crickets", "from": 0, "to": "L07", "lufs": -36},
                  {"kind": "wind", "from": "L07", "to": "L14", "lufs": -40},
                  {"kind": "crickets", "from": "L14", "to": "end", "lufs": -36},
                  {"kind": "hum", "from": "L01.3", "to": "L07", "lufs": -40},
                  {"kind": "hum", "from": "L15", "to": "L32", "lufs": -38},
                  {"kind": "hum", "from": "L43", "to": "L46", "lufs": -42},
                  {"kind": "drone", "from": "L27", "to": "end", "lufs": -34},
              ],
              "sfx": [
                  {"at": "L01.3", "kind": "thud", "db": -5},
                  {"at": "L05.1+0.1", "kind": "latch", "db": -16},
                  {"at": "L05.1+0.6", "kind": "latch", "db": -16},
                  {"at": "L05.2", "kind": "latch", "db": -14},
                  {"at": "L18.1", "kind": "creak", "db": -10, "dur": 1.2},
                  {"at": "L24.1", "kind": "whoosh", "db": -26},
                  {"at": "L26+0.1", "kind": "creak", "db": -9, "dur": 1.3},
                  {"at": "L31.1", "kind": "creak", "db": -10, "dur": 1.4},
                  {"at": "L35.1", "kind": "thud", "db": -4},
              ],
              "music_drops": [{"from": "L25.2", "to": "L26.1", "keep": ["creak"]},
                              {"from": "L34.1", "to": "L35.1", "keep": ["thud"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
