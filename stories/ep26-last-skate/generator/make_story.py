"""Writes ../story.json for ep26 "last-skate" (script.md, writer 2026-11-02).

Run from anywhere: python stories/ep26-last-skate/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (the room's dim, the spotlight's path, the Skater, the skates, the door), the score
and the sound. Places are set.py's (see its docstring): the rink floor is x +-7, y +-4.4; the south rail is y -4.15
with a gap between its posts at x -1.2 and 1.2; the snack bar is west on the concourse, the hire counter east.
A character with yaw 0 faces -y; yaw 90 faces +x; yaw 180 faces +y (north, the floor from the concourse).
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# The lore shot (S12) must hold 1.5 s or more: L10 gets a longer gap after it. The loop cut is 0.25 s after the last
# word (P03, no fade at either end).
# the word check (asr): a few lines a touch slower so a swallowed word comes through ("speakers" heard "speaker",
# "her skates" heard "escapes", "round them" heard "around him"), and a breath after "My Nan" so it isn't heard as
# "Nan's" with the next line's first word
TEMPO = {"L01": 0.94, "L45": 0.94, "L54": 0.94, "L72": 0.94, "L03": 1.0, "L07": 0.95, "L10": 0.92, "L18": 0.94,
         "L20": 0.94, "L30": 0.9, "L56": 0.95, "L64": 0.92}
# and a comma in the spoken text only (the captions don't change) where a word was swallowed
SPOKEN = {}
for ln in lines:
    for k, ch in enumerate(ln.get("chunks", [])):
        if (ln["id"], k) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], k)]
for ln in lines:
    if ln["id"] == "L10":
        ln["gap"] = 0.5
    if ln["id"] == "L03":
        ln["gap"] = 0.6
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]
lines = lines + [{"id": "P03", "pause": 0.25, "chunks": []}]

# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True, "ink": "#16100f"}
cast = {
    "me": {"age": "adult", "skin": "#c98e66", "shirt": "#2a8d88", "pattern": "solid", "collar": "#237873",
           "pants": "#33384f", "shoes": "#d8d3c6", "sleeves": "short", "hair": "cap", "hair_c": "#1a1412",
           "hat": "none", "face": dict(FACE)},
    "nan": {"age": "adult", "skin": "#ecc29c", "shirt": "#a58bd0", "pattern": "solid", "collar": "#bba5de",
            "pants": "#d6d1e2", "shoes": "#f1efe9", "sleeves": "short", "hair": "bun", "hair_c": "#cfd2d8",
            "hat": "none", "height": 0.9, "width": 0.88,
            "face": {"eyes": "lashes", "brows": True, "ink": "#1b1214", "bags": True}},
    "pop": {"age": "adult", "skin": "#e4ae88", "shirt": "#3f6d52", "pattern": "plaid", "pattern_c": "#e3d9bf",
            "collar": "#35604a", "pants": "#e6dcc0", "shoes": "#5e4128", "sleeves": "short", "hair": "none",
            "hair_c": "#ecebe8", "hat": "none", "width": 1.12,
            "face": {"eyes": "round", "brows": True, "ink": "#1a1210", "bags": True}},
    "lenny": {"age": "adult", "skin": "#d49a74", "shirt": "#b0293b", "pattern": "solid", "collar": "#b0293b",
              "pants": "#2c2b33", "shoes": "#222222", "sleeves": "short", "hair": "buzz", "hair_c": "#2a1d17",
              "hat": "none", "extras": ["scarf"], "extra_c": "#26262c", "face": dict(FACE)},
    "c1a": {"age": "adult", "skin": "#e0a67e", "shirt": "#3a5f9a", "pattern": "solid", "pants": "#2e3045",
            "shoes": "#e8dcc2", "sleeves": "short", "hair": "swoop", "hair_c": "#3a2a1c", "hat": "none",
            "face": dict(FACE)},
    "c1b": {"age": "adult", "skin": "#8d5a3f", "shirt": "#d0a43a", "pattern": "solid", "pants": "#4a3b33",
            "shoes": "#e8dcc2", "sleeves": "short", "hair": "long", "hair_c": "#18110e", "hat": "none",
            "face": {"eyes": "lashes", "brows": True, "ink": "#18100e"}},
    "c2a": {"age": "adult", "skin": "#f0c8a4", "shirt": "#5a8a56", "pattern": "stripes", "pattern_c": "#dfe4d2",
            "pants": "#3d4150", "shoes": "#e8dcc2", "sleeves": "short", "hair": "spiky", "hair_c": "#7a4a2a",
            "hat": "none", "face": dict(FACE)},
    "c2b": {"age": "adult", "skin": "#b87850", "shirt": "#7d4f8e", "pattern": "solid", "pants": "#2c3040",
            "shoes": "#e8dcc2", "sleeves": "short", "hair": "bun", "hair_c": "#241812", "hat": "none",
            "face": {"eyes": "round", "brows": True, "ink": "#1c1210", "bags": False}},
}


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens, roll=0):
    return c([0, loc, tgt, lens, roll])


def move(a, b, lens_a, lens_b=None):
    return c([0, a[0], a[1], lens_a], [1, b[0], b[1], lens_b or lens_a])


def yaw_to(a, b):
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


# ---------------------------------------------------------------------------------------------------- places
NAN = (3.0, -3.75)         # Nan at the south rail
SKR = (1.65, -3.75)        # the Skater's post at the rail (and where Pop stands at the end)
FAR = (-2.5, 3.7)          # the far (north) rail
MID = (0.5, 0.2)           # the middle of the floor
SEAT_Y = -6.7
ME_X, POP_X = -5.0, -3.8
SEAT_Z = 0.19

# ---------------------------------------------------------------------------------------------------- cameras
def C(loc, tgt, h, roll=0):
    """A still camera: h is the height in metres the frame shows at the target (portrait, sensor height 24 mm)."""
    d = math.dist(loc, tgt)
    return still(loc, tgt, round(24.0 * d / h, 1), roll)


# the view from the snack bar over the floor, the high wide, the far-rail long lens, the rail 3/4 from the concourse
FLOOR = still([-2.4, -5.6, 2.1], [1.0, 0.5, 0.9], 22)
HIGH = still([-5.8, -7.9, 3.9], [1.0, 0.5, 0.6], 20)
FARCAM = still([-3.0, -5.6, 1.5], [FAR[0], FAR[1], 1.35], 55)
RAIL34 = still([4.4, -6.2, 1.4], [2.3, -3.75, 1.2], 24)
BOOTH = C([-1.3, 0.2, 2.9], [0.0, 5.4, 3.0], 2.4)
POPSEAT = [POP_X, SEAT_Y, 1.25]
MESEAT = [ME_X, SEAT_Y, 1.25]

SHOTS = [
    # 01 the dedication (dim; the spotlight slides along the rail)
    (0, "dark: the pool slides slowly onto Nan, alone at the rail, her face in frame", 2, C([3.0, -6.3, 1.3], [3.0, -3.75, 1.25], 2.3)),
    ("L01.2", "the booth lamp, Lenny at the mic, his face in frame", 2, C([-0.9, 0.6, 3.0], [0.0, 5.4, 2.95], 2.3)),
    ("L02", "the pool settles on Nan, from behind (over the rail from the concourse)", 2,
     C([3.0, -7.2, 1.5], [3.0, -3.8, 1.0], 2.7)),
    ("L03", "Nan's face in the soft pool, looking off toward the snack bar", 2, C([3.0, -1.4, 1.3], [3.0, -3.75, 1.25], 1.5)),
    ("L04", "the same rail in full warm light, crowded", 2, still([6.2, -1.8, 1.55], [1.5, -4.1, 1.0], 24)),
    # 02 the last night
    ("L05", "the rink from outside at dusk", 2, move(([-15.0, -5.6, 1.2], [-8.0, -7.0, 0.7]), ([-13.4, -6.2, 1.2], [-8.0, -7.0, 0.7]), 25)),
    ("L06", "wide inside: floor, couples, stripes", 2, still([-6.6, -2.4, 1.9], [2.0, 0.8, 1.0], 20)),
    ("L07", "the three of us coming in through the doors", 2, C([-1.6, -4.7, 1.6], [-7.4, -7.0, 1.2], 5.2)),
    ("L08", "under the ceiling fans, then down to the shine of the floor", 2,
     move(([-1.0, -5.3, 1.0], [0.0, 2.7, 4.4]), ([-1.0, -5.3, 1.0], [0.5, 0.5, 0.0]), 24)),
    ("L09", "the painted stripes, locked off", 4, still([5.6, 0.2, 1.4], [8.0, 0.8, 1.5], 30)),
    ("L10", "Nan at the hire counter, the cubby wall behind", 2, C([3.6, -4.9, 1.7], [4.5, -8.4, 1.8], 3.6)),
    ("L10.2", "the lore shot: the bottom-row end cubby, the far-too-long cherry skates, the tally on the near heel", 2,
     C([6.5, -6.0, 1.15], [6.5, -8.05, 1.12], 0.9)),
    ("L11", "Pop beside her, shaking his head, smiling", 2, C([4.5, -4.8, 1.5], [5.0, -6.9, 1.2], 2.6)),
    ("L12", "Pop settling on the stool under the amber lamp", 2, C([-1.5, -4.4, 1.6], [POP_X, SEAT_Y, 1.0], 2.8)),
    ("L13", "close on his knees and the tape", 2, C([-2.0, -6.4, 0.85], [POP_X, -6.4, 0.8], 1.4)),
    ("L14", "Pop to Nan: 'You skate for both of us'", 2, C([-2.0, -3.3, 1.7], [-3.2, -6.4, 1.3], 3.0)),
    ("L15", "Nan from behind, gliding to the rail", 2, still([-1.2, -7.6, 1.3], [0.2, -4.4, 0.9], 28)),
    # 03 slow song one
    ("L16", "the room dims for a slow song, seen from the snack bar", 2, FLOOR),
    ("L17", "couples gliding past, seen at the elbows", 2, still([-6.4, -3.6, 1.3], [-1.0, 0.0, 1.0], 24)),
    ("L18", "high wide: the pool travelling round the floor", 2, HIGH),
    ("L19", "Nan alone at the rail, the couples beyond", 2, C([3.8, -6.6, 1.4], [3.0, -3.5, 1.2], 2.8)),
    ("L20", "me and Pop at the snack bar, the tub between us", 2, C([-1.7, -3.7, 1.55], [-4.4, -6.4, 1.2], 3.0)),
    ("L21", "the pool sliding along the far rail, then onto a tall striped shape", 2, FARCAM),
    ("L22", "medium on the Skater at the far rail, face toward the floor", 2,
     C([-3.0, -5.4, 1.3], [FAR[0], FAR[1], 1.25], 3.4)),
    ("L23", "side view of its legs: two bends, a hard shadow under each", 2, C([-6.4, 3.6, 0.9], [FAR[0], FAR[1] - 0.2, 1.2], 3.2)),
    ("L24", "the pool slides away, the room passes, the pool returns: nothing there", 2, FARCAM),
    # 04 Lenny
    ("L25", "Pop waving up at the booth", 2, C([-1.8, -4.2, 1.6], [POP_X, SEAT_Y, 1.4], 2.6)),
    ("L25.3", "Lenny waves back", 2, BOOTH),
    ("L26", "my face, puzzled", 2, C([-2.6, -4.3, 1.55], [ME_X, SEAT_Y, 1.4], 2.5)),
    ("L27", "Pop shrugging: it's on his shirt", 2, C([-1.8, -4.2, 1.6], [POP_X, SEAT_Y, 1.4], 2.6)),
    ("L27.5", "Lenny in the booth: a plain cherry shirt, nothing on it", 2, C([-0.8, 0.6, 3.0], [0.0, 5.4, 3.0], 1.6)),
    # 05 slow song two
    ("L28", "the dim, the pool sliding in from the frame's edge", 2, FLOOR),
    ("L29", "high wide: the pool on the Skater, dead centre", 2, HIGH),
    ("L30", "medium on its folded arms", 2, C([-1.6, -3.5, 1.55], [MID[0], MID[1], 1.4], 2.9)),
    ("L31", "its cream oval face, painted smile, eyes toward the rail", 2, still([-0.1, -1.5, 1.2], [MID[0], MID[1], 1.95], 38)),
    ("L31.2", "reverse: Nan at the rail, unaware", 2, C([3.0, -6.6, 1.5], [3.0, -3.75, 1.3], 2.8)),
    ("L32", "me pointing, Pop eating a chip", 2, C([-1.7, -3.6, 1.6], [-4.2, -6.5, 1.3], 3.0)),
    ("L33", "close on Pop's wrist and the plain watch", 2, C([-3.0, -5.3, 1.9], [-3.23, -6.1, 1.5], 0.9)),
    # 06 slow song three
    ("L34", "the chip tub untouched, my face worried", 2, C([-2.8, -4.6, 1.6], [-4.6, -6.4, 1.3], 2.3)),
    ("L35", "low on the floor boards as the pool edges across them", 2, move(([-4.0, -3.7, 0.18], [1.2, -3.2, 0.0]), ([-4.0, -3.7, 0.18], [1.8, -3.5, 0.0]), 34)),
    ("L36", "along the rail: Nan, a cream post, the Skater folded and facing her", 2, RAIL34),
    ("L37", "up close, its stripes faded almost to pink", 2, C([3.0, -5.0, 1.55], [2.0, -3.75, 1.4], 1.4)),
    ("L38", "its face, the eye highlights the brightest thing, key from below", 2, still([2.9, -4.7, 1.1], [1.75, -3.75, 2.0], 36)),
    ("L39", "Nan's face, looking past camera toward us", 2, C([3.4, -5.3, 1.4], [3.0, -3.75, 1.3], 1.7)),
    ("L40", "the pool slides off it, and back again", 2, RAIL34),
    ("P01+0.55", "THE REVEAL: its head turned all the way round, over its back, looking at me", 1,
     still([3.7, -5.7, 1.0], [1.7, -3.75, 1.8], 30)),
    ("L42", "my face, terrified", 2, C([-2.8, -4.4, 1.6], [ME_X, SEAT_Y, 1.4], 2.5)),
    ("L43", "the chrome stool beside me, empty, the amber lamp over it", 2, C([-1.5, -4.4, 1.5], [POP_X, SEAT_Y, 0.9], 3.0)),
    ("L44", "close on the tub, steam faint and slow", 2, C([-3.6, -4.9, 1.6], [-4.4, -5.98, 1.3], 0.9)),
    # 07 the last skate
    ("L45", "the booth lamp, Lenny at the mic", 2, BOOTH),
    ("L46", "the slow 2 s dim on the wide", 2, HIGH),
    ("L47", "couples gliding off through the gap, the floor left bare", 2, still([0.8, 3.2, 1.55], [0.0, -4.3, 0.95], 24)),
    ("L48", "the pool settling on Nan", 2, C([1.4, -0.6, 1.5], [3.0, -3.75, 1.0], 3.0)),
    ("L49", "the pool widens and the Skater is in it, at her shoulder, a head taller", 1, RAIL34),
    ("L50", "THE TEST STILL: its arm held out to her, folded twice, the hand at the end of the sleeve", 1,
     still([2.3, -6.9, 1.0], [2.3, -3.75, 1.45], 21)),
    ("L51", "Nan looks at the hand", 2, C([2.5, -5.4, 1.45], [3.0, -3.75, 1.35], 1.7)),
    ("L52", "Nan's hand rising, a hand's width from its hand", 2, C([2.6, -6.4, 1.3], [2.6, -3.75, 1.3], 2.4)),
    ("L53", "me standing, terrified, the waltz swelling", 2, C([-2.9, -4.3, 1.6], [ME_X, -6.4, 1.4], 2.8)),
    ("L54", "the booth: Lenny at the mic, smiling", 2, BOOTH),
    # 08 Pop
    ("L55", "the door by the hire counter swings open", 2, still([0.3, -2.4, 1.4], [0.0, -9.0, 1.2], 26)),
    ("L56", "out rolled Pop", 2, C([0.3, -2.4, 1.4], [0.0, -8.4, 1.1], 3.4)),
    ("L57", "close on his skates on the honey boards", 2, C([2.3, -1.0, 0.9], [0.2, -4.4, 0.5], 2.7)),
    ("L58", "Pop coming across the floor, wobbling, the tape on his knees", 2, C([-2.4, -0.8, 1.3], [0.5, -2.2, 1.0], 3.0)),
    ("L59", "Nan's face, wide, then softening", 2, C([2.4, -5.4, 1.45], [3.0, -3.75, 1.35], 1.8)),
    ("L60", "my face, wide, putting it together", 2, C([-2.9, -4.3, 1.6], [ME_X, -6.4, 1.4], 2.6)),
    ("L61", "Lenny leaning out of the booth, a raised sleeve", 2, C([-0.8, 0.4, 3.0], [0.0, 5.3, 3.0], 2.3)),
    ("L62", "Pop wobbling, steady for one second, proud", 2, C([-0.6, -0.6, 1.4], [2.0, -2.8, 1.1], 2.9)),
    ("L63", "Pop at the rail, his hand out (cut away before the hands meet)", 2, C([4.3, -6.3, 1.45], [2.3, -3.75, 1.3], 3.0)),
    ("L64", "the pool sliding round them", 2, HIGH),
    ("L65", "an empty, lit rail post, no bodies", 2, C([2.4, -5.6, 1.1], [2.4, -4.15, 0.95], 1.6)),
    ("L66", "wider: Pop standing in exactly that place, Nan beside him", 2, C([5.2, -6.4, 1.7], [2.3, -3.6, 1.2], 3.8)),
    # 09 two of them
    ("L67", "Nan laughing, Pop laughing with her", 2, C([2.3, -5.6, 1.5], [2.3, -3.75, 1.3], 2.7)),
    ("L68", "low tracking: the two of them gliding", 2, c([0, [-2.2, -2.6, 0.75], [0.0, 0.0, 1.0], 30])),
    ("L69", "Pop tips a little, Nan's arm at his elbow", 2, c([0, [-1.8, -1.9, 1.35], [0.0, 0.0, 1.2], 36])),
    ("L70", "the pair coming past the snack bar, laughing", 2, still([-6.2, -4.9, 1.4], [-2.6, -2.8, 1.2], 26)),
    ("L71", "me on the chrome stool, chin on my hand", 2, C([-2.0, -4.2, 1.5], [POP_X, SEAT_Y, 1.35], 2.6)),
    ("L72", "crane up to the overhead wide", 2,
     c([0, [-3.4, -4.6, 1.5], [-3.0, -1.0, 1.0], 26, 0], [0.85, [-2.0, -7.4, 7.4], [-2.4, 0.6, 0.8], 38, 0],
       [1, [-2.0, -7.4, 7.4], [-2.4, 0.6, 0.8], 38, 0])),
    ("L73", "hold the overhead wide, the fans at the frame's edge", 2, still([-2.0, -7.4, 7.4], [-2.4, 0.6, 0.8], 38, 0)),
]

# per-shot light level (set.py scales every light by it) so that cuts between shots land at similar brightness: the
# flash pre-check found 2 to 3 flashes a second where dim and bright shots alternated. Measured at the final's steps.
EXPO = {"S15": 1.9, "S16": 0.8, "S17": 0.7, "S09": 0.55, "S01": 1.0, "S02": 1.1, "S19": 1.4, "S20": 1.18, "S21": 1.03, "S22": 1.53, "S23": 1.09, "S24": 0.77, "S25": 0.87, "S26": 1.49, "S31": 0.55, "S32": 0.77, "S33": 1.18, "S34": 0.81, "S35": 0.77, "S36": 1.08, "S37": 1.51, "S38": 1.04, "S39": 1.17, "S40": 0.92, "S41": 1.13, "S42": 1.42, "S43": 2.5, "S44": 0.99, "S45": 1.19, "S46": 1.5, "S47": 1.7, "S48": 0.93, "S49": 0.96, "S50": 0.72, "S51": 1.34, "S52": 2.49, "S53": 2.13, "S54": 1.26, "S55": 1.21, "S56": 0.79, "S57": 1.13, "S58": 2.1, "S59": 0.89, "S60": 1.28, "S61": 1.05, "S62": 0.75, "S63": 0.8, "S64": 0.84, "S65": 1.86, "S66": 1.47, "S67": 1.04, "S68": 0.99, "S69": 1.32, "S70": 0.89, "S71": 0.95, "S72": 0.8, "S73": 0.87, "S74": 0.7, "S75": 1.33, "S76": 1.49, "S77": 0.7, "S78": 0.76}

shots = []
for i, (at, what, step, cam) in enumerate(SHOTS):
    s = {"id": f"S{i + 1:02d}", "cam": cam, "hand": 0.0 if step == 1 else 0.004, "step": step, "what": what}
    if f"S{i + 1:02d}" in EXPO:
        s["expo"] = EXPO[f"S{i + 1:02d}"]
    if i:
        s["at"] = at
    shots.append(s)
# the two gliding shots are locked off (a following camera slides the plank grain across the whole frame)
for sh in shots:
    if sh["what"].startswith("low tracking"):
        sh["cam"] = still([0.8, 0.8, 1.1], [0.8, -3.0, 1.0], 18)
    if sh["what"].startswith("Pop tips"):
        sh["cam"] = still([-1.6, 0.5, 1.3], [-1.6, -2.8, 1.1], 20)
overhead = [s["id"] for s in shots if s["what"].startswith(("crane up", "hold the overhead"))]

# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True, "sit": False,
           "skate": False, "wobble": 0, "hidden": False}
acting = {w: [] for w in cast}


def put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, **NEUTRAL, "expr": "neutral", **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": pos, **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def talk(who, a, b):
    acting[who].append({"from": a, "to": b, "mouth": [0.5, 0.5], "flap": True})


def seat(who, at, x, **kw):
    put(who, at, [x, SEAT_Y, SEAT_Z], yaw=180, sit=True, arms=[66, 66], **kw)


# ---- me
hide("me", 0)
put("me", "L07", [-9.5, -7.5], yaw=90, expr="neutral")
walk("me", "L07>", [-6.1, -7.4])
hide("me", "L08")
seat("me", "L16", ME_X, expr="worried")
key("me", "L20", arms=[66, 66], expr="neutral")
key("me", "L26", expr="worried")
key("me", "L32", arms=[66, 100], expr="wide", blend=0.3)
key("me", "L34", arms=[66, 66], expr="worried", blend=0.3)
key("me", "L42", expr="terrified", blend=0.1)
put("me", "L53", [ME_X, -6.35], yaw=180, arms=[100, 100], side=[10, 10], expr="terrified", blink=False)
put("me", "L60", [ME_X, -6.35], yaw=180, arms=[70, 70], expr="wide", blink=False)
seat("me", "L71", POP_X, expr="soft")
key("me", "L71", arms=[78, 78])

# ---- Pop
hide("pop", 0)
put("pop", "L07", [-9.8, -7.0], yaw=90, expr="neutral", arms=[100, 0])
walk("pop", "L07>", [-6.3, -7.0], arms=[100, 0])
hide("pop", "L08")
put("pop", "L11", [5.6, -6.8], yaw=0, expr="smirk")
key("pop", "L11", head=[25, 0])
seat("pop", "L12", POP_X, expr="smirk")
key("pop", "L25", arms=[66, 160], blend=0.3)
key("pop", "L25.3", arms=[66, 66], blend=0.4)
key("pop", "L27.2", arms=[66, 66], side=[0, 25], expr="smirk", blend=0.3)
key("pop", "L32", arms=[66, 90], side=[0, 0], expr="smirk", blend=0.3)
key("pop", "L33", arms=[85, 66], blend=0.4)
hide("pop", "L43")
put("pop", "L56", [0.0, -8.6], yaw=180, skate=True, wobble=0, side=[75, 75], expr="smirk")
key("pop", "L57", wobble=1.2)
key("pop", "L58", expr="grin")
walk("pop", "L56>", [0.0, -6.3], side=[75, 75])
walk("pop", "L57>", [0.2, -4.1], side=[75, 75])
walk("pop", "L58+1.0", [0.0, -2.6], side=[75, 75])
walk("pop", "L58>", [1.0, -1.7], side=[75, 75])
walk("pop", "L59>", [1.9, -2.0], side=[75, 75])
walk("pop", "L61>", [2.5, -2.5], side=[75, 75])
walk("pop", "L62>", [2.1, -3.0], side=[70, 70], wobble=2)
walk("pop", "L63+1.3", [SKR[0], SKR[1]], side=[40, 0], arms=[0, 72], wobble=3)
key("pop", "L63+1.3", yaw=90, blend=0.3)
hide("pop", "L65")
put("pop", "L66", [SKR[0], SKR[1]], yaw=90, wobble=1, expr="grin", arms=[0, 72])
# skating off with Nan from L68: waypoints of the lap (seconds after L68) and the two partners' lateral offsets
LAP = [(0.0, (2.0, -3.7)), (2.0, (-0.6, -2.7)), (4.0, (-3.2, -2.8)), (6.0, (-4.8, 0.4)), (8.0, (-3.6, 2.2)),
       (10.0, (-2.8, 1.5)), (12.0, (-2.2, 0.2)), (14.0, (-1.7, -1.0)), (16.0, (-1.0, -2.0))]


def lap_pos(i, who):
    """The pair side by side: Pop on the lap's path, Nan a step to the left of the way they're going."""
    t, (x, y) = LAP[i]
    a = LAP[max(i - 1, 0)][1]
    b = LAP[min(i + 1, len(LAP) - 1)][1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    nx, ny = -dy / n, dx / n          # left of travel
    k = 0.62 if who == "nan" else -0.62
    return t, [round(x + nx * k, 3), round(y + ny * k, 3)]


for i in range(len(LAP)):
    t, p = lap_pos(i, "pop")
    if i == 0:
        key("pop", "L67", yaw=90)
        walk("pop", f"L68+{t:.1f}", p, side=[0, 0], arms=[0, 40], wobble=4)
    else:
        joined = i >= 5
        walk("pop", f"L68+{t:.1f}", p, side=[0, 70] if joined else [0, 0], arms=[0, 0] if joined else [0, 40],
             wobble=1.5 if joined else (4 if i % 2 else 2))

# ---- Nan
put("nan", 0, list(NAN), yaw=0, expr="soft")
key("nan", "L02", yaw=180, blend=0)
key("nan", "L03", head=[62, 0], blend=0.3)
key("nan", "L04", head=[0, 0], expr="grin", blend=0.3)
put("nan", "L07", [-9.0, -6.5], yaw=90, expr="grin")
walk("nan", "L07>", [-6.0, -6.6])
hide("nan", "L08")
put("nan", "L10", [4.4, -6.8], yaw=0, expr="neutral")
put("nan", "L14", [-2.7, -6.2], yaw=-90, expr="soft")
walk("nan", "L14.4", [-2.7, -6.2], skate=True)
walk("nan", "L15+0.4", [-0.3, -4.6], skate=True)
walk("nan", "L15>", [NAN[0], NAN[1]], skate=True)
put("nan", "L16", list(NAN), yaw=180, expr="soft", skate=False)
put("nan", "L34", list(NAN), yaw=0, head=[-30, 0], expr="soft")
key("nan", "L39", head=[-45, 0], blend=0.3)
put("nan", "L48", list(NAN), yaw=0, head=[-30, 0], expr="soft")
put("nan", "L51", list(NAN), yaw=-55, expr="soft", head=[0, 18])
key("nan", "L52", arms=[0, 62], blend=0.4)
put("nan", "L55", list(NAN), yaw=-60, expr="wide")
key("nan", "L59+0.5", expr="soft")
key("nan", "L63", arms=[0, 62], blend=0.4)
key("nan", "L64", yaw=-90, arms=[0, 40], expr="soft")
hide("nan", "L65")
put("nan", "L66", list(NAN), yaw=-90, arms=[0, 40], expr="soft")
key("nan", "L67", expr="grin", head=[0, 0])
for i in range(len(LAP)):
    t, p = lap_pos(i, "nan")
    if i == 0:
        key("nan", "L67+1.5", arms=[0, 40])
        put("nan", "L68", [NAN[0] - 0.8, NAN[1] + 0.0], yaw=-90, skate=True, arms=[0, 40], expr="grin")
    jn = i >= 5
    walk("nan", f"L68+{max(t, 0.9):.1f}" if i == 0 else f"L68+{t:.1f}", p, skate=True, arms=[0, 0] if jn else [0, 40],
         side=[70, 0] if jn else [0, 0], expr="grin")

# ---- Lenny at the booth
put("lenny", 0, [0.0, 5.5, 1.74], yaw=0, expr="neutral")
key("lenny", "L25.3", arms=[0, 150], expr="grin", blend=0.3)
key("lenny", "L25>", arms=[0, 0], blend=0.5)
key("lenny", "L54", expr="grin", head=[10, 0])
key("lenny", "L61", expr="grin", lean=14, arms=[0, 165], head=[0, 0], blend=0.4)
key("lenny", "L61>", lean=0, arms=[0, 0], blend=0.5)

# ---- the couples: elliptical orbits of the floor (a = 5.2, b = 2.4), side by side
A_, B_ = 5.2, 2.4
OMEGA = 0.4          # rad/s, about 1.7 m/s


def ell(theta, off):
    x, y = A_ * math.cos(theta), B_ * math.sin(theta)
    nx, ny = math.cos(theta) * B_, math.sin(theta) * A_       # outward normal of the ellipse (unnormalised)
    n = math.hypot(nx, ny)
    return [round(x + off * nx / n, 3), round(y + off * ny / n, 3)]


def orbit(anchor, secs, th0, a, b, off=0.45, hide_at=None):
    for who, o in ((a, -off), (b, off)):
        put(who, anchor, ell(th0, o), yaw=0, skate=True, expr="grin", arms=[18, 18], side=[8, 8])
        n = int(secs / 0.5)
        for k in range(1, n + 1):
            walk(who, f"{anchor}+{k * 0.5:.1f}", ell(th0 + OMEGA * k * 0.5, o), skate=True, arms=[18, 18], side=[8, 8])
        hide(who, f"{anchor}+{secs + 0.1:.1f}")


for w in ("c1a", "c1b", "c2a", "c2b"):
    hide(w, 0)
orbit("L04", 3.4, 3.9, "c1a", "c1b")
orbit("L04", 3.4, 0.8, "c2a", "c2b")
orbit("L06", 5.0, 3.0, "c1a", "c1b")
orbit("L06", 5.0, 5.4, "c2a", "c2b")
orbit("L16", 23.0, 2.0, "c1a", "c1b")
orbit("L16", 23.0, 5.3, "c2a", "c2b")
orbit("L28", 11.4, 3.4, "c1a", "c1b")
orbit("L28", 11.4, 0.4, "c2a", "c2b")
orbit("L35", 18.0, 5.6, "c1a", "c1b")
orbit("L35", 18.0, 2.6, "c2a", "c2b")
orbit("L45", 2.9, 2.5, "c1a", "c1b")
orbit("L45", 2.9, 5.5, "c2a", "c2b")
# L47: they roll off through the gap in the south rail, one couple after the other
for who, dx, p0, lag in (("c1a", -0.4, (-0.8, 0.0), 0.0), ("c1b", 0.4, (-0.8, 0.0), 0.0),
                         ("c2a", -0.4, (-3.4, -0.9), 1.4), ("c2b", 0.4, (-3.4, -0.9), 1.4)):
    put(who, "L47", [p0[0] + dx, p0[1]], yaw=180, skate=True, expr="grin", arms=[18, 18])
    walk(who, f"L47+{1.0 + lag:.1f}", [p0[0] + dx + 0.6, p0[1] - 1.2], skate=True, arms=[18, 18])
    walk(who, f"L47+{2.2 + lag:.1f}", [dx * 0.8, -3.7], skate=True, arms=[18, 18])
    walk(who, f"L47+{3.3 + lag:.1f}", [dx * 0.8 - 0.3, -5.0], skate=True, arms=[18, 18])
    walk(who, f"L47+{4.6 + lag:.1f}", [dx * 0.8 - 3.2, -5.0], skate=True, arms=[18, 18])
    hide(who, f"L47+{4.8 + lag:.1f}")

# ---------------------------------------------------------------------------------------------------- cues
cues = [{"at": 0, "name": "skates", "who": w, "on": True} for w in ("c1a", "c1b", "c2a", "c2b")]
cues += [
    {"at": "L11", "name": "skates", "who": "nan", "on": True},
    {"at": "L56", "name": "skates", "who": "pop", "on": True},
    # the room's level: dim (0.2) for the dedication, full for the fast songs, 0.3 for a slow song, lower for the last
    # skate, then warm and a little up for Pop. Every change is a slow ramp.
    {"at": "L04", "name": "dim", "level": 1.0, "dur": 1.4},
    {"at": "L16", "name": "dim", "level": 0.3, "dur": 1.2},
    {"at": "L25", "name": "dim", "level": 1.0, "dur": 1.5},
    {"at": "L28", "name": "dim", "level": 0.3, "dur": 1.2},
    {"at": "L33>", "name": "dim", "level": 0.8, "dur": 1.5},
    {"at": "L34", "name": "dim", "level": 0.3, "dur": 1.5},
    {"at": "L46", "name": "dim", "level": 0.07, "dur": 2.0},
    {"at": "L55", "name": "dim", "level": 0.34, "dur": 3.0},
    {"at": "L64", "name": "dim", "level": 0.4, "dur": 3.0},
    # the spotlight: where it is, how bright, how wide a cone. It's never on in a fast song and never pops.
    {"at": 0, "name": "spot", "to": [NAN[0], NAN[1]], "dur": 3.4, "size": 30},
    {"at": "L04", "name": "spot", "gain": 0.0, "dur": 1.6},
    {"at": "L16", "name": "spot", "to": [7.2, -2.6], "size": 42, "dur": 0.02},
    {"at": "L16+1.0", "name": "spot", "gain": 1.0, "dur": 1.4},
    {"at": "L18", "name": "spot", "to": [6.2, 2.8], "dur": 2.4},
    {"at": "L19", "name": "spot", "to": [3.2, 3.5], "dur": 2.0},
    {"at": "L20", "name": "spot", "to": [0.4, 3.6], "dur": 2.0},
    {"at": "L21", "name": "spot", "to": [FAR[0], FAR[1]], "dur": 2.6},
    {"at": "L24", "name": "spot", "to": [-6.8, 1.8], "dur": 1.0},
    {"at": "L24.2", "name": "spot", "to": [FAR[0], FAR[1]], "dur": 1.8},
    {"at": "L25", "name": "spot", "gain": 0.0, "dur": 1.5},
    {"at": "L28", "name": "spot", "to": [8.0, -0.6], "dur": 0.02},
    {"at": "L28+0.4", "name": "spot", "gain": 1.0, "dur": 1.0},
    {"at": "L28.1", "name": "spot", "to": [MID[0], MID[1]], "dur": 3.0},
    {"at": "L33", "name": "spot", "gain": 0.0, "dur": 1.5},
    {"at": "L34", "name": "spot", "to": [-3.8, -1.6], "dur": 0.02},
    {"at": "L34+0.8", "name": "spot", "gain": 1.0, "dur": 1.2},
    {"at": "L35", "name": "spot", "to": [SKR[0], SKR[1] + 0.2], "dur": 3.4},
    {"at": "L40", "name": "spot", "to": [-1.6, -1.6], "dur": 1.0},
    {"at": "L40.2", "name": "spot", "to": [SKR[0], SKR[1] + 0.2], "dur": 1.4},
    {"at": "L43", "name": "spot", "gain": 0.0, "dur": 1.2},
    {"at": "L47", "name": "spot", "to": [-3.5, -0.5], "size": 28, "dur": 0.02},
    {"at": "L47+0.8", "name": "spot", "gain": 1.0, "dur": 1.2},
    {"at": "L48", "name": "spot", "to": [NAN[0] - 0.2, NAN[1] + 0.2], "dur": 2.4},
    {"at": "L49", "name": "spot", "size": 44, "dur": 1.4},
    {"at": "L72", "name": "spot", "gain": 0.55, "dur": 2.0},
    {"at": "L64", "name": "spot", "to": [4.8, -2.4], "dur": 1.6},
    {"at": "L64+1.2", "name": "spot", "to": [2.4, -3.6], "dur": 1.6},
]
for i in range(1, len(LAP)):
    px, py = lap_pos(i, "pop")[1]
    cues.append({"at": f"L68+{LAP[i - 1][0]:.1f}", "name": "spot", "to": [round(px - 0.2, 3), py], "dur": 2.0, "size": 46})
# the Skater: placed where it already stands when a beat starts, never seen moving
HEAD_DOWN = [0, 24]
cues += [
    {"at": "L21", "name": "skater", "pos": list(FAR), "yaw": 0, "pose": "rest", "head": HEAD_DOWN, "hidden": False},
    {"at": "L24.2", "name": "skater", "hidden": True},
    {"at": "L28", "name": "skater", "pos": list(MID), "yaw": yaw_to(MID, NAN), "pose": "rest", "head": [0, 0], "hidden": False},
    {"at": "L33>", "name": "skater", "hidden": True},
    {"at": "L35", "name": "skater", "pos": list(SKR), "yaw": 90, "pose": "rest", "head": [0, 0], "hidden": False},
    {"at": "P01+0.55", "name": "skater", "head": [180, 0]},
    {"at": "L43", "name": "skater", "hidden": True},
    {"at": "L49", "name": "skater", "pos": list(SKR), "yaw": 90, "pose": "reach", "head": [-40, 0], "hidden": False, "reach_side": -1},
    {"at": "L54", "name": "skater", "hidden": True},
    {"at": "L55", "name": "door", "open": 1.0, "dur": 2.2},
    {"at": "L58", "name": "door", "open": 0.0, "dur": 1.5},
    {"at": "L44", "name": "steam", "on": True},
    {"at": "L45", "name": "steam", "on": False},
]

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": 0, "kind": "click", "db": -16},
    {"at": "L01.2", "kind": "whoosh", "db": -26, "dur": 1.5},
    {"at": "L10.2", "kind": "castors", "db": -30, "dur": 1.4},
    {"at": "L15", "kind": "castors", "db": -26, "dur": 3.0},
    {"at": "L21", "kind": "riser", "db": -28, "dur": 2.4},
    {"at": "L31", "kind": "sting", "db": -22},
    {"at": "L36", "kind": "riser", "db": -26, "dur": 2.0},
    {"at": "P01+0.55", "kind": "hit", "db": -4},
    {"at": "P01+0.55", "kind": "sting", "db": -10},
    {"at": "L47", "kind": "castors", "db": -26, "dur": 3.5},
    {"at": "L49", "kind": "sting", "db": -14},
    {"at": "P02+0.45", "kind": "hit", "db": -5},
    {"at": "L55", "kind": "door", "db": -14},
    {"at": "L56", "kind": "castors", "db": -24, "dur": 3.0},
    {"at": "L68", "kind": "castors", "db": -26, "dur": 4.0},
    {"at": "L70", "kind": "castors", "db": -26, "dur": 3.0},
    {"at": "L73>-0.7", "kind": "bell", "db": -12, "dur": 2.0},
]

story = {
    "slug": "ep26-last-skate",
    "title": "Every slow song, something at the roller rink stood a little closer to my nan",
    "made_for_kids": False,
    "premise": "On the last night before an old roller rink shuts, I take Nan and Pop back to where they met. Pop says his knees are done and sits at the snack bar, so Nan waits at the rail alone through every slow song. Each time the slow spotlight comes round, a Skater in faded cherry-and-cream stripes, with legs and arms that bend twice like a folding chair, stands nearer to her.",
    "twist": "The dedication was Pop's. He asked for their song and spent six months of Tuesdays relearning to skate in secret. On the last skate he rolls out and holds out his hand, and the Skater is gone: it had been standing right where he should have been. The couple by the rail had two people in it after all.",
    "world": "an old roller rink on its last night: a honey maple floor, a cherry padded rail with cream posts, cherry-and-cream stripes on every wall, three slow ceiling fans, a snack bar with an amber lamp, a hire counter with a wall of cubbies, a raised booth, and one soft spotlight that creeps round the floor on slow songs",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff5f7e",
    "caption": {"ink": "#0a0809", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#1a1519", "fog_density": 0.012, "fog_start": 6.0, "sky": "#1c4a52", "sky_strength": 0.35,
             "exposure": 0.4},
    "grade": {"shadows": [0.0, 0.0, 0.012], "highlights": [0.025, 0.01, -0.02], "saturation": 0.88, "red_line": 0.78, "contrast": 1.06,
              "vignette": 0.38, "bloom": 0.3, "grain": 0.013},
    "phonemes": {"Nan": "nˈæn"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "overhead_shots": overhead,
    "acting": acting,
    "cues": cues,
    "fx": [],
    # the fast songs: a bright organ-ish pulse in D major (pad, piano and pulse); the slow songs: F lydian, soft pad and
    # piano; the last skate and "their song": the same, warmer, with the drone held low under it
    "music": {"root": 50, "mode": "major", "bpm": 72, "seed": 26,
              "sections": [
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.25, "mode": "lydian", "root": 53},
                  {"at": "L04", "voices": ["pad", "pulse", "piano"], "energy": 0.6, "mode": "major", "root": 50},
                  {"at": "L16", "voices": ["pad", "piano"], "energy": 0.3, "mode": "lydian", "root": 53},
                  {"at": "L25", "voices": ["pad", "pulse", "piano"], "energy": 0.55, "mode": "major", "root": 50},
                  {"at": "L28", "voices": ["pad", "piano"], "energy": 0.3, "mode": "lydian", "root": 53},
                  {"at": "L33>", "voices": ["pad", "pulse"], "energy": 0.4, "mode": "major", "root": 50},
                  {"at": "L34", "voices": ["pad", "piano", "drone"], "energy": 0.3, "mode": "lydian", "root": 53},
                  {"at": "L45", "voices": ["pad", "drone"], "energy": 0.25, "mode": "lydian", "root": 53},
                  {"at": "L53", "voices": ["pad", "piano", "drone", "choir"], "energy": 0.55, "mode": "lydian", "root": 53},
                  {"at": "L55", "voices": ["pad", "piano", "drone"], "energy": 0.45, "mode": "lydian", "root": 53},
                  {"at": "L67", "voices": ["pad", "piano", "drone"], "energy": 0.4, "mode": "lydian", "root": 53},
              ]},
    "sound": {"floor": "wood", "steps_db": -26,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "end", "lufs": -34},
                  {"kind": "hum", "from": 0, "to": "end", "lufs": -40},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01-0.1", "to": "L41", "keep": ["hit", "sting"]},
                              {"from": "P02-0.1", "to": "L51", "keep": ["hit"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
