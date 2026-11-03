"""Writes ../story.json for ep25 "Plot nine" (script by the writer, redo 2026-11-02).

Run from anywhere: python stories/ep25-plot-nine/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (time of day, the Digger, the holes, props), the score and the sound.

Places are set.py's metres. The path runs down the hill along -y from the gate at y = 0; a character with yaw 0 faces
-y, yaw 90 faces +x. Odd plots are on the left (x > 0), even plots on the right (x < 0), five rows of five metres:
row r spans y = -1.5 - 6r .. -6.5 - 6r. Plot nine is row 4 on the left: x 1..6, y -25.5..-30.5; Grandad's shed is at
its path corner (x 1.0..2.4, y -27.6..-25.8), its door on the +x face. Plot ten (mine) is across the path.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# ------------------------------------------------------------------------------------------------ pauses
PAUSES = {"L18": ("P01", 1.0), "L26": ("P02", 0.7)}
HOLDS = {}
full = []
for ln in lines:
    if ln["id"] in HOLDS:
        ln["gap"] = HOLDS[ln["id"]]
    full.append(ln)
    if ln["id"] in PAUSES:
        pid, dur = PAUSES[ln["id"]]
        full.append({"id": pid, "pause": dur, "chunks": []})
LOOP = 0.25
full.append({"id": "P04", "pause": LOOP, "chunks": []})
lines = full

TEMPO = {"L17": 0.93, "L36": 0.93}
for ln in lines:
    if ln['id'] in TEMPO:
        ln['tempo'] = TEMPO[ln['id']]

cast = {
    "me": {"age": "adult", "skin": "#d9a07c", "shirt": "#5d7d3c", "pattern": "knit", "pattern_c": "#46632d",
           "collar": "#4a6a30", "pants": "#6b4a2e", "shoes": "#2d6a38", "sleeves": "long", "hair": "cap",
           "hair_c": "#1c1612", "hat": "none", "face": {"eyes": "round", "brows": True, "ink": "#161012"}},
    "carter": {"age": "adult", "skin": "#dcb08f", "shirt": "#6e4c32", "pattern": "knit", "pattern_c": "#58391f",
               "collar": "#b9b29a", "pants": "#4a463e", "shoes": "#2a2a22", "sleeves": "long", "hair": "cap",
               "hair_c": "#7b6d58", "hat": "none", "height": 0.97,
               "face": {"eyes": "tired", "brows": True, "ink": "#1c1613", "bags": True}},
    "newcomer": {"age": "adult", "skin": "#8c5c40", "shirt": "#c4872c", "pattern": "solid", "collar": "#a8721f",
                 "pants": "#cfc4ab", "shoes": "#33353a", "sleeves": "long", "hair": "cap", "hair_c": "#4a2e1c",
                 "hat": "none", "height": 0.96, "face": {"eyes": "lashes", "brows": True, "ink": "#161012"}},
}


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return c([0, loc, tgt, lens])


def move(a, b, lens_a, lens_b=None):
    return c([0, a[0], a[1], lens_a], [1, b[0], b[1], lens_b or lens_a])


def yaw_to(a, b):
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


# places
DIG = {1: (3.4, -3.6), 4: (-3.6, -10.0), 7: (3.4, -22.0), 9: (3.85, -28.8), 10: (-3.5, -28.0)}
UP = {"lump": 0.0, "shoulders": 0.2, "arms": 0.38, "chest": 0.5, "waist": 0.66, "crown": -0.3, "eyes": -0.17}
CAR_F = (2.95, -26.25)          # Grandad outside the shed
BUCKET = (3.2, -25.3)
BUCKET_SEAT = [BUCKET[0], BUCKET[1], -0.38]
GRAN_FACE = (2.55, -28.8)       # Grandad face to face with the Digger across the bean row
EYE = 1.55

# ------------------------------------------------------------------------------------------------ shots
# (at, what, step, camera). The interior is set.py's: Grandad's shed at x 60.
SHOTS = [
    # 01 the rule, L01 to L12
    (0, "plot six: keys on a stalk, the woman behind", 2,
     c([0, [-1.3, -14.1, 0.62], [-3.0, -15.9, 1.0], 31], [1, [-1.35, -14.15, 0.62], [-3.0, -15.9, 1.0], 30])),
    ("L02", "close on the keys on the stalk, dew", 4, still([-1.5, -14.6, 0.78], [-2.75, -15.6, 0.74], 36)),
    ("L03", "three umbrella handles by the gate", 2,
     move(([3.3, -2.5, 0.55], [1.9, -0.6, 0.35]), ([3.1, -2.3, 0.55], [1.9, -0.6, 0.35]), 26)),
    ("L04", "plot two's flask bush", 2, move(([-0.4, -6.4, 0.95], [-3.1, -4.1, 0.65]), ([-0.5, -6.2, 0.95], [-3.1, -4.1, 0.65]), 26)),
    ("L05", "the woman wheels her bike up the path, keys on the bars", 2,
     move(([3.6, -13.4, 1.05], [-0.2, -11.6, 0.8]), ([3.6, -13.3, 1.05], [-0.2, -11.3, 0.8]), 30)),
    ("L06", "plot ten from above: bare raked soil, my wellies", 4, still([-0.9, -25.0, 3.0], [-2.0, -26.9, 0.0], 24)),
    ("L07", "me at plot ten, pleased with myself", 2, still([0.9, -26.2, 1.55], [-2.3, -27.0, 1.4], 28)),
    ("L08", "across the path: Grandad on his bucket, a small wave", 2, still([0.4, -23.4, 1.45], [3.2, -25.3, 1.15], 50)),
    ("L09", "walking down the path at dawn, the two of us", 2,
     move(([0.1, 1.8, 1.55], [0.1, -4.0, 1.0]), ([0.1, 0.8, 1.55], [0.1, -4.0, 1.0]), 26)),
    ("L09.4-0.25", "Grandad tips his cap to the stake at plot one", 2, still([1.9, -0.9, 1.35], [0.3, -1.8, 1.35], 36)),
    ("L09.4+0.2", "...at plot four", 2, still([-1.9, -6.8, 1.35], [-0.3, -7.6, 1.35], 36)),
    ("L09.4+0.65", "...at plot seven", 2, still([1.9, -18.9, 1.35], [0.3, -19.6, 1.35], 36)),
    ("L10", "the tool wall: the green scarf on its hook", 4,
     move(([60.4, 0.1, 1.42], [60.45, 1.8, 1.38]), ([60.4, 0.3, 1.42], [60.45, 1.8, 1.38]), 30)),
    ("L11", "glasses on a stalk in the beans", 2, still([2.9, -24.6, 0.85], [3.8, -26.85, 0.6], 34)),
    ("L11.2", "Grandad, peering at them", 2, still([4.7, -22.9, 1.35], [3.2, -25.3, 1.1], 32)),
    ("L12", "his cap on a stalk", 2, still([3.3, -24.6, 0.85], [3.85, -27.45, 0.6], 34)),
    ("L12.1", "Grandad bareheaded, laughing", 2, still([4.2, -22.6, 1.4], [3.2, -25.3, 1.2], 32)),
    # 02 the head, L13 to L24
    ("L13", "over my shoulder: a lump in plot one", 2, still([-0.6, 3.4, 1.9], [3.4, -3.6, 0.3], 26)),
    ("L14", "plot one: the head and shoulders in profile, the knot", 4, still([1.1, -3.7, 0.5], [3.4, -3.6, 0.38], 30)),
    ("L15", "its face: two green points", 4, still([3.5, -5.5, 0.4], [3.4, -3.6, 0.38], 28)),
    ("L16", "Grandad at the gate, still", 2, still([1.75, -2.5, 1.45], [0.45, -0.9, 1.4], 36)),
    ("L17", "plot one, a round hole", 4, still([1.1, -3.7, 0.5], [3.4, -3.6, 0.0], 28)),
    ("L18", "over the hole: a pebble drops in", 4, still([2.4, -4.8, 0.9], [3.4, -3.6, 0.1], 28)),
    ("P01", "the black hole, held", 4, still([3.4, -3.55, 2.0], [3.4, -3.62, 0.0], 24)),
    ("L19", "me crouched by the hole, scared", 2, still([0.9, -6.9, 1.4], [2.6, -4.3, 1.0], 24)),
    ("L20", "wide: the hole, and the head in plot four", 4, still([4.0, -1.6, 0.55], [-2.0, -9.6, 0.6], 22)),
    ("L21", "long lens from the gate: the head in plot seven", 4, still([0.5, -1.0, 1.0], [3.4, -22.0, 0.5], 70)),
    ("L21.2", "plot seven: out to the chest, knot in profile", 2, still([0.8, -22.0, 0.85], [3.4, -22.0, 0.75], 34)),
    ("L22", "Grandad on his bucket, chatting to the beans", 2, still([3.7, -27.4, 1.25], [3.2, -25.3, 1.05], 38)),
    ("L23", "Grandad, worried, mid-sentence", 2, still([2.1, -22.9, 1.25], [3.2, -25.3, 1.1], 40)),
    ("L24", "me, worried; far up the path the head in plot seven", 4,
     still([-0.8, -28.4, 1.6], [0.0, -26.3, 1.5], 32)),
    # 03 Friday, L25 to L33
    ("L25", "wide over the bottom fence: mist coming up", 4,
     move(([0.0, -33.2, 1.5], [0.0, -10.0, 1.0]), ([0.0, -33.2, 1.5], [0.0, -10.0, 1.0]), 19)),
    ("L26", "between the beans, a shape with its back to us", 2, still([0.45, -28.2, 1.45], [3.85, -28.8, 0.7], 24)),
    ("P02", "hold", 4, still([0.45, -28.2, 1.45], [3.85, -28.8, 0.7], 24)),
    ("L27", "its head turned all the way round", 1, still([0.9, -28.5, 1.1], [3.85, -28.8, 0.88], 24)),
    ("L27.3", "over its shoulder: Grandad by his shed door", 2, still([4.7, -29.5, 1.4], [2.95, -26.25, 1.45], 65)),
    ("L28", "Grandad looks right back", 2, still([3.9, -27.6, 1.5], [2.95, -26.25, 1.45], 36)),
    ("L29.1", "close on the root knot under its chin", 4, still([2.75, -28.8, 0.92], [3.85, -28.8, 0.78], 34)),
    ("L29.4", "the scarf's knot on the hook, same framing", 4, still([60.0, 0.2, 1.5], [60.28, 1.8, 1.32], 34)),
    ("L30", "side-on wide: Grandad and the head across the bean row", 4,
     still([3.2, -32.0, 1.6], [3.2, -28.8, 1.1], 22)),
    ("L31", "high wide down the path: holes in a line, the head in nine", 4,
     still([0.4, -3.0, 6.0], [0.3, -24.0, 0.0], 24)),
    ("L32", "overhead on plot seven's hole", 4, still([3.4, -21.9, 2.6], [3.4, -22.0, 0.0], 24)),
    ("L32.2", "where its waist meets the soil", 4, still([2.8, -29.9, 0.55], [3.85, -28.8, 0.5], 30)),
    ("L33", "me, from the head to Grandad", 2, still([1.3, -31.3, 1.5], [3.0, -30.3, 1.5], 34)),
    # 04 the walk, L34 to L40
    ("L34", "me, resolved, turning to Grandad", 2, still([2.3, -27.8, 1.55], [3.2, -30.1, 1.5], 34)),
    ("L35", "from behind: the two of us walking up the path", 4,
     move(([0.0, -24.8, 1.5], [0.0, -14.0, 1.0]), ([0.0, -23.0, 1.5], [0.0, -13.0, 1.0]), 26)),
    ("L36", "at plot one's hole, me telling him", 2, still([4.0, -6.8, 1.5], [1.8, -4.6, 1.4], 36)),
    ("L36.2", "plot four's hole: his face starts to change", 2, still([-0.3, -8.0, 1.55], [-2.4, -8.8, 1.45], 38)),
    ("L37", "plot seven: Grandad nods", 2, still([0.4, -20.2, 1.5], [2.2, -21.6, 1.4], 34)),
    ("L37.1", "his shed down the hill in the fog", 4, still([0.6, -21.0, 1.3], [1.7, -26.7, 1.0], 28)),
    ("L38", "face to face across the bean row, the fog thinning", 4,
     still([3.2, -31.0, 1.45], [3.2, -28.8, 1.3], 28)),
    ("L39", "the head sinks to the shoulders", 4, still([0.5, -30.4, 1.1], [3.5, -28.8, 0.5], 21)),
    ("L39.2", "flat dark soil, a round dent", 4, still([3.5, -26.9, 1.2], [3.85, -28.8, 0.0], 26)),
    ("L40", "the shed wall: his cap by her scarf", 4,
     move(([60.35, 0.3, 1.45], [60.45, 1.8, 1.4]), ([60.4, 0.2, 1.45], [60.45, 1.8, 1.4]), 32)),
    # 05 the sting, L41 to L43
    ("L41", "high wide down the hill, grey dawn", 4, still([0.0, 3.0, 6.5], [0.2, -18.0, 0.0], 20)),
    ("L42", "plot ten: a crown just breaks the soil", 2, still([-0.4, -29.4, 0.75], [-3.5, -28.0, 0.25], 30)),
    ("L43", "the crown, low and close", 4, still([-2.4, -28.0, 0.2], [-3.5, -28.0, 0.28], 40)),
]

shots = []
for i, (at, what, step, cam) in enumerate(SHOTS):
    s = {"id": f"S{i + 1:02d}", "cam": cam, "hand": 0.004 if step == 4 else 0.006, "step": step, "what": what}
    if i:
        s["at"] = at
    shots.append(s)

# ------------------------------------------------------------------------------------------------ acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True, "sit": False}
acting = {"me": [], "carter": [], "newcomer": []}


def put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, "hidden": False, **NEUTRAL, "expr": "neutral", **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": pos, **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def talk(who, a, b):
    acting[who].append({"from": a, "to": b, "mouth": [0.55, 0.55], "flap": True})


# the newcomer: plot six (L01), wheeling her bike (L05), and nowhere else
put("newcomer", 0, [-3.4, -16.3], yaw=yaw_to([-3.4, -16.3], [-1.5, -14.4]), expr="neutral", head=[0, 6])
key("newcomer", "L01.2", expr="smile", blend=0.5)
hide("newcomer", "L02")
put("newcomer", "L05", [-0.45, -12.6], yaw=180, arms=[0, 60])
walk("newcomer", "L05>", [-0.45, -10.6], arms=[0, 60])
key("newcomer", "L05", expr="smile")
hide("newcomer", "L06")

# me
hide("me", 0)
put("me", "L07", [-2.2, -27.0], yaw=90, expr="smile", head=[0, 4])
put("me", "L08", [-0.2, -24.2], yaw=90, head=[0, -4])
put("me", "L09", [-0.38, -0.2], yaw=0)
walk("me", "L09.4-0.55", [-0.38, -3.0])
hide("me", "L09.4-0.25")
put("me", "L13", [-0.3, 1.3], yaw=0, head=[0, 4])
hide("me", "L14")
put("me", "L19", [2.45, -4.1], yaw=yaw_to([2.45, -4.1], DIG[1]), expr="scared", lean=32, head=[0, 18])
hide("me", "L20")
put("me", "L24", [-0.05, -26.4], yaw=yaw_to([-0.05, -26.4], [-0.8, -28.4]), expr="worried", head=[0, -6])
hide("me", "L25")
put("me", "L30", [4.9, -30.0], yaw=180, expr="worried")
put("me", "L33", [3.0, -30.3], yaw=yaw_to([3.0, -30.3], DIG[9]), expr="scared", head=[0, 12])
key("me", "L33.1", yaw=yaw_to([3.0, -30.3], GRAN_FACE), head=[0, 0], blend=0.7)
put("me", "L34", [3.2, -30.1], yaw=yaw_to([3.2, -30.1], GRAN_FACE), expr="neutral")
key("me", "L34.1", expr="neutral", yaw=yaw_to([3.2, -30.1], GRAN_FACE), blend=0.4)
put("me", "L35", [-0.4, -22.0], yaw=180)
walk("me", "L35>", [-0.4, -19.2])
put("me", "L36", [1.2, -4.0], yaw=yaw_to([1.2, -4.0], [2.2, -5.0]))
talk("me", "L36", "L36.2")
put("me", "L36.2", [-2.2, -10.0], yaw=yaw_to([-2.2, -10.0], [-2.4, -8.7]))
put("me", "L37", [2.3, -22.9], yaw=yaw_to([2.3, -22.9], [2.2, -21.6]))
hide("me", "L37.1")
hide("me", "L38")
hide("me", "L39.2")
hide("me", "L42")
hide("me", "L43")

# Grandad
hide("carter", 0)
put("carter", "L08", BUCKET_SEAT, yaw=-90, expr="smile", sit=True, arms=[0, 40])
key("carter", "L08.1", arms=[0, 40], blend=0.2)
key("carter", "L08.2", arms=[0, 0], blend=0.4)
put("carter", "L09", [0.38, -0.2], yaw=0)
walk("carter", "L09.4-0.55", [0.38, -3.0])
put("carter", "L09.4-0.25", [0.25, -1.8], yaw=90, arms=[0, 100], head=[0, 14], expr="smile")
put("carter", "L09.4+0.2", [-0.25, -7.6], yaw=-90, arms=[0, 100], head=[0, 14], expr="smile")
put("carter", "L09.4+0.65", [0.25, -19.6], yaw=90, arms=[0, 100], head=[0, 14], expr="smile")
hide("carter", "L10")
put("carter", "L11.2", BUCKET_SEAT, yaw=yaw_to(BUCKET, [3.0, -24.0]), expr="smirk", sit=True, head=[0, 16])
hide("carter", "L12")
put("carter", "L12.1", BUCKET_SEAT, yaw=yaw_to(BUCKET, [2.4, -23.9]), expr="laugh", sit=True, head=[0, -8])
hide("carter", "L13")
put("carter", "L16", [0.45, -0.9], yaw=yaw_to([0.45, -0.9], DIG[1]), expr="neutral", head=[0, 0])
hide("carter", "L17")
put("carter", "L22", BUCKET_SEAT, yaw=0, expr="smile", sit=True, head=[0, 6])
talk("carter", "L22", "L22>")
put("carter", "L23", BUCKET_SEAT, yaw=yaw_to(BUCKET, [2.1, -22.9]), expr="worried", sit=True, head=[0, 4])
acting["carter"].append({"from": "L23", "to": "L23.1", "mouth": [0.0, 0.5]})
hide("carter", "L24")
put("carter", "L27.3", CAR_F, yaw=yaw_to(CAR_F, (4.7, -29.5)), expr="neutral")
put("carter", "L28", CAR_F, yaw=yaw_to(CAR_F, DIG[9]), expr="neutral", blink=False)
hide("carter", "L29.1")
put("carter", "L30", GRAN_FACE, yaw=90, expr="neutral")
put("carter", "L33", GRAN_FACE, yaw=90, expr="worried")
hide("carter", "L34")
put("carter", "L35", [0.4, -22.0], yaw=180)
walk("carter", "L35>", [0.4, -19.2])
put("carter", "L36", [2.2, -5.0], yaw=yaw_to([2.2, -5.0], [1.2, -4.0]), expr="neutral")
put("carter", "L36.2", [-2.4, -8.7], yaw=yaw_to([-2.4, -8.7], [-0.3, -8.0]), expr="neutral")
key("carter", "L36.2+0.8", expr="smile", blend=0.5)
put("carter", "L37", [2.2, -21.6], yaw=yaw_to([2.2, -21.6], [0.4, -20.2]), expr="smile", head=[0, 10])
key("carter", "L37+0.7", head=[0, 0], blend=0.3)
key("carter", "L37+1.2", head=[0, 10], blend=0.3)
hide("carter", "L37.1")
put("carter", "L38", GRAN_FACE, yaw=90, expr="smile")
put("carter", "L39", GRAN_FACE, yaw=90, expr="smile")
hide("carter", "L39.2")
put("carter", "L42", [0.0, -26.0], yaw=0, hidden=True)
hide("carter", "L40")

# ------------------------------------------------------------------------------------------------ cues
def tod(at, name, dur=0.3):
    return {"at": at, "name": "tod", "set": name, "dur": dur}


cues = [
    {"at": 0, "name": "tod", "set": "bright"},
    tod("L13", "dawn"),
    tod("L17", "tue"),
    tod("L21", "wed"),
    {"at": "L25", "name": "tod", "set": "fog", "dur": 3.0},
    tod("L31", "fogthin"),
    tod("L32", "fog"),
    {"at": "L38", "name": "tod", "set": "fogthin", "dur": 2.5},
    tod("L40", "dusk"),
    tod("L41", "grey"),
    # the Digger: found where it already stands, never seen moving. up = how far its neck stands above the soil
    {"at": 0, "name": "digger", "hidden": True},
    {"at": "L13", "name": "digger", "plot": 1, "up": UP["lump"], "yaw": 0},
    {"at": "L14", "name": "digger", "plot": 1, "up": UP["shoulders"], "yaw": 0},
    {"at": "L17", "name": "digger", "hidden": True},
    {"at": "L20", "name": "digger", "plot": 4, "up": UP["arms"], "yaw": 0},
    {"at": "L21", "name": "digger", "plot": 7, "up": UP["chest"], "yaw": 0},
    {"at": "L24", "name": "digger", "plot": 7, "up": UP["chest"], "yaw": yaw_to(DIG[7], (-0.8, -28.4))},
    {"at": "L25", "name": "digger", "hidden": True},
    {"at": "L26", "name": "digger", "plot": 9, "up": UP["waist"], "yaw": 90, "head": 0},
    {"at": "L27", "name": "digger", "plot": 9, "up": UP["waist"], "yaw": 90, "head": 180},
    {"at": "L39", "name": "digger", "plot": 9, "up": UP["shoulders"], "yaw": 90, "head": 180},
    {"at": "L39.2", "name": "digger", "hidden": True},
    {"at": "L42", "name": "digger", "plot": 10, "up": UP["crown"], "yaw": 90, "head": 0, "nosite": True},
    {"at": "L43", "name": "digger", "plot": 10, "up": UP["eyes"], "yaw": 90, "head": 0, "nosite": True},
    # holes: plot one from Tuesday, four from Wednesday, seven from Friday; all settle at L39
    {"at": 0, "name": "holes", "plots": []},
    {"at": "L17", "name": "holes", "plots": [1]},
    {"at": "L21", "name": "holes", "plots": [1, 4]},
    {"at": "L25", "name": "holes", "plots": [1, 4, 7]},
    {"at": "L39", "name": "holes", "plots": []},
    {"at": 0, "name": "dent", "on": False},
    {"at": "L39.2", "name": "dent", "on": True},
    {"at": "L40", "name": "dent", "on": False},
    # props
    {"at": 0, "name": "bucket", "on": True},
    {"at": "L05", "name": "keystalk", "on": False},
    {"at": 0, "name": "bike", "on": False},
    {"at": "L05", "name": "bike", "on": True},
    {"at": "L06", "name": "bike", "on": False},
    {"at": "L11", "name": "glasses", "on": True},
    {"at": "L12", "name": "capstalk", "on": True},
    {"at": "L12.1", "name": "capstalk", "on": False},
    {"at": "L12.1", "name": "grandcap", "on": False},
    {"at": "L13", "name": "grandcap", "on": True},
    {"at": "L40", "name": "intcap", "on": True},
    {"at": "L29.1", "name": "knotlight", "on": True},
    {"at": "L29.4", "name": "knotlight", "on": False},
    {"at": "L18+0.35", "name": "pebble", "on": True},
]

sfx = [
    {"at": "P01+0.55", "kind": "click", "db": -22},
    {"at": "P02+0.3", "kind": "hit", "db": -9},
    {"at": "L39+0.3", "kind": "glide", "db": -17, "dur": 1.6},
    {"at": "L39+0.3", "kind": "thud", "db": -24},
    {"at": "L42.2", "kind": "click", "db": -17},
    {"at": "L42.2+0.1", "kind": "thud", "db": -26},
]

story = {
    "slug": "ep25-plot-nine",
    "title": "On This Hill, Whatever You FORGET Comes Back Up",
    "made_for_kids": False,
    "premise": "On an allotment hill where whatever you forget comes back up out of the ground, where you left it, I'm the one gardener nothing ever comes up for. Grandad has plot nine across the path from mine. This week his glasses and his cap come up in his beans. Then a head and shoulders of soil and roots with no face comes up in plot one by the gate, and every dawn it's in a plot further down the path, higher out of the ground, nearer to his.",
    "twist": "The faceless thing is Gran: Grandad is forgetting her a year at a time, and the hill gives each year back in the plot where they spent it. Its roots are knotted under its chin like her green headscarf, it rises in plots one, four and seven, then nine, and when I walk him to every hole and tell him what he told me, he says her name and the soil settles. Then I find something in my own plot, and I can't remember who it is.",
    "world": "allotment gardens on a hillside at dawn in a dry spring: a five-bar gate with a chain and padlock, a dusty path, ten plots of pale cracked clay, tarred sheds, one dark worked plot of bean canes with a creosote shed, a bare raked bed, and mist filling the valley below",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#9be04a",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#a7a9b0", "fog_density": 0.018, "fog_start": 4.0, "sky": "#e7b896", "sky_strength": 1.0,
             "exposure": 0.0, "flash_safe": True},
    "grade": {"shadows": [-0.02, 0.0, 0.05], "highlights": [0.03, 0.01, -0.03], "saturation": 0.95, "contrast": 1.06,
              "vignette": 0.36, "bloom": 0.26, "grain": 0.012},
    "phonemes": {"Gran": "ɡɹˈæn", "in": "ˈɪn"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 50, "mode": "dorian", "bpm": 68, "seed": 25,
              "sections": [
                  {"at": 0, "voices": ["pluck", "pad"], "energy": 0.3},
                  {"at": "L13", "voices": ["drone", "pad", "pulse"], "energy": 0.36},
                  {"at": "P01", "voices": ["drone"], "energy": 0.25},
                  {"at": "L19", "voices": ["drone", "pad", "pulse"], "energy": 0.42},
                  {"at": "L26>", "voices": ["drone"], "energy": 0.25},
                  {"at": "L27", "voices": ["drone", "pad", "pulse"], "energy": 0.5},
                  {"at": "L38", "voices": ["piano", "pad", "drone"], "energy": 0.45, "mode": "major", "root": 50},
                  {"at": "L41", "voices": ["drone"], "energy": 0.28, "mode": "dorian", "root": 50},
              ]},
    "sound": {"floor": "grass", "steps_db": -22,
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "end", "lufs": -36},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01-0.2", "to": "L19", "keep": ["click"]},
                              {"from": "P02", "to": "L27+0.5", "keep": ["hit"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
