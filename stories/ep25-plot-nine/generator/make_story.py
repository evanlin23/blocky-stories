"""Writes ../story.json for ep25 "Plot nine" (script by the writer, 2026-11-02).

Run from anywhere: python stories/ep25-plot-nine/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (time of day, the Digger, the holes, props), the score and the sound.

Places are set.py's metres. The path runs down the hill along -y from the gate at y = 0; a character with yaw 0 faces
-y, yaw 90 faces +x. Odd plots are on the left (x > 0), even plots on the right (x < 0), five rows of five metres:
row r spans y = -1.5 - 6r .. -6.5 - 6r. Plot nine is row 4 on the left: x 1..6, y -25.5..-30.5. Mr. Carter's shed
is at its path corner (x 1.0..2.4, y -27.6..-25.8), its door on the +x face.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# ------------------------------------------------------------------------------------------------ pauses
PAUSES = {"L19": ("P01", 1.5), "L34": ("P02", 0.9), "L59": ("P03", 2.0)}
# holds (seconds after a line) that bring the film to the 2:15 floor without touching the words
HOLDS = {"L04": 0.5, "L10": 0.5, "L29": 0.5, "L44": 0.5, "L56": 0.6, "L58": 0.4, "L69": 0.4, "L70": 0.0}
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

TEMPO = {"L11": 0.93, "L16": 0.93, "L32": 0.8}   # Whisper heard 'in' as 'and' at full pace
for ln in lines:
    if ln['id'] in TEMPO:
        ln['tempo'] = TEMPO[ln['id']]
# spoken forms Whisper needs (captions never change)
SPOKEN = {}
for ln in lines:
    for k, ch in enumerate(ln.get("chunks", [])):
        if (ln["id"], k) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], k)]

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
DIG = {1: (3.4, -3.6), 4: (-3.6, -10.0), 7: (3.4, -22.0), 9: (3.85, -28.8)}
ME_N = (4.05, -28.3)           # me on plot nine at dawn
ME_F = (3.1, -27.9)            # me between the Digger and the shed door
CAR_F = (2.95, -26.25)          # Mr. Carter outside the shed
DOOR = (2.65, -26.95)           # in the doorway
BUCKET = (3.2, -25.3)
EYE = 1.55

# ------------------------------------------------------------------------------------------------ shots
# (at, what, step, camera). The interiors are set.py's: the shed at x 60 and plot ten's at x 80, the shaft at x 120.
SHOTS = [
    # 01 the smell, L01 to L10
    (0, "me bent over the wet soil, face lit, a drop falls off the leaf beside me", 2,
     c([0, [3.6, -28.7, 0.9], [3.75, -27.3, 0.95], 20], [1, [3.6, -28.5, 0.9], [3.75, -27.3, 0.95], 19])),
    ("L02", "wide from the gate: cracked hill, peach sky", 4, move(([0.25, -0.5, 1.9], [0.0, -14, 0.9]),
                                                                  ([0.25, -1.4, 1.9], [0.0, -14, 0.9]), 19)),
    ("L03", "overhead on a neighbour's cracked bed", 4, still([3.5, -9.9, 2.7], [3.5, -10.05, 0.0], 22)),
    ("L04", "high wide down the path to plot nine, wet prints", 4,
     move(([0.0, 0.6, 4.6], [0.6, -22, 0.3]), ([0.0, -0.4, 4.2], [0.6, -22, 0.3]), 19)),
    ("L05", "day one, the gate: Mr. Carter and me, the key on twine", 2,
     still([0.0, 3.5, 1.3], [0.0, 0.4, 1.2], 22)),
    ("L06", "Mr. Carter from behind, walking out", 2, move(([0.55, -1.5, 1.35], [0, 3.0, 1.15]),
                                                           ([0.55, -1.5, 1.35], [0, 5.0, 1.15]), 24)),
    ("L07", "in the shed, dim: twine, oil can, seed packets", 2,
     move(([60.4, 0.3, 1.2], [60.6, 1.8, 1.0]), ([60.5, 0.5, 1.2], [60.6, 1.8, 1.0]), 28)),
    ("L08", "the tool wall, one bare hook", 2, move(([60.0, 0.3, 1.35], [60.0, 1.9, 1.35]),
                                                    ([60.0, 0.6, 1.35], [60.0, 1.9, 1.35]), 26)),
    ("L09", "the padlock, beaded", 2, move(([0.45, -0.55, 1.12], [0.1, 0.0, 1.05]),
                                           ([0.4, -0.45, 1.1], [0.1, 0.0, 1.05]), 38)),
    ("L10", "me at the gate looking down the valley", 2,
     still([1.5, -3.2, 1.55], [0.2, -0.9, 1.5], 30)),
    # 02 the head, L11 to L29
    ("L11", "over my shoulder: a lump in plot one", 2, still([0.55, 2.2, 1.7], [3.0, -3.8, 0.35], 22)),
    ("L12", "plot one, head and shoulders", 2, still([1.3, -5.3, 0.55], [3.4, -3.7, 0.3], 24)),
    ("L13", "the roots on the head and shoulders", 2, still([2.2, -5.0, 0.55], [3.4, -3.65, 0.28], 30)),
    ("L14", "its face: two green points", 4, still([3.55, -5.7, 0.27], [3.4, -3.6, 0.27], 26)),
    ("L15", "me on the path, a careful distance", 2, still([-1.4, -4.2, 1.55], [0.9, -2.3, 1.3], 24)),
    ("L16", "the wet shoulder", 2, still([2.5, -4.6, 0.4], [3.6, -3.7, 0.12], 34)),
    ("L17", "plot one, a round hole", 4, still([0.7, -6.0, 0.55], [3.4, -3.7, 0.2], 26)),
    ("L18", "overhead on the hole", 4, still([3.4, -3.5, 2.5], [3.4, -3.62, 0.0], 24)),
    ("L19", "beside the hole: a pebble drops in", 1, still([2.1, -4.7, 0.7], [3.4, -3.6, 0.45], 28)),
    ("P01", "the black hole, held", 4, still([3.4, -3.55, 2.0], [3.4, -3.62, 0.0], 24)),
    ("L20", "me at the hole, scared", 2, still([0.9, -6.9, 1.4], [2.8, -4.2, 1.15], 22)),
    ("L21", "wide down the path: the hole and the head in plot four", 4,
     still([-1.0, -7.2, 0.8], [-3.6, -10.0, 0.4], 24)),
    ("L22", "plot nine dripping in the low gold sun", 2, still([3.0, -26.4, 0.75], [3.6, -27.7, 0.62], 36)),
    ("L23", "long lens from the gate: the head in plot seven", 4, still([0.5, -17.0, 0.9], [3.4, -22.0, 0.35], 28)),
    ("L24", "plot seven, higher out of the dirt", 2, still([0.9, -24.6, 0.65], [3.4, -22.0, 0.45], 26)),
    ("L25", "the cane going into plot four's hole", 2, still([-1.8, -8.7, 1.0], [-3.55, -9.95, 0.35], 26)),
    ("L26", "the cane's top end sinking", 2, still([-3.0, -9.3, 0.55], [-3.55, -9.95, 0.3], 40)),
    ("L27", "the gate at an earlier, bluer dawn", 2, still([-1.6, -2.6, 1.5], [0.0, 0.7, 1.25], 22)),
    ("L28", "the padlock running with water", 2, still([0.4, -0.5, 1.0], [0.1, 0.0, 0.95], 40)),
    ("L29", "high wide: plot seven, eight, nine and the shed", 4,
     still([0.6, -19.0, 1.5], [3.2, -23.0, 0.5], 22)),
    # 03 Friday, L30 to L44
    ("L30", "wide over the bottom fence: mist coming up", 4,
     move(([0.0, -33.2, 1.5], [0.0, -10.0, 1.0]), ([0.0, -33.2, 1.5], [0.0, -10.0, 1.0]), 19)),
    ("L31", "drops from the padlock onto green wellies", 2, still([0.95, -1.0, 0.55], [0.12, -0.05, 0.55], 28)),
    ("L32", "me walking the path", 2, still([0.2, 1.6, 1.7], [0.0, -6.0, 0.8], 24)),
    ("L32.2", "the hole in plot one, in fog", 4, still([1.2, -1.2, 1.4], [3.4, -3.6, 0.0], 24)),
    ("L32.3+0.12", "the hole in plot four, in fog", 4, still([-1.2, -7.0, 1.4], [-3.6, -10.0, 0.0], 24)),
    ("L32.5", "the hole in plot seven, in fog", 4, still([1.2, -19.2, 1.4], [3.4, -22.0, 0.0], 24)),
    ("L33", "my walk: the cane wigwams come out of the fog", 2,
     move(([0.1, -27.6, EYE], [3.5, -29.5, 0.9]), ([0.15, -28.5, EYE], [3.5, -29.2, 0.9]), 22)),
    ("L34", "between the beans, a shape with its back to us", 2, still([0.45, -28.2, 1.45], [3.85, -28.8, 0.55], 24)),
    ("P02", "hold", 4, still([0.45, -28.2, 1.45], [3.85, -28.8, 0.55], 24)),
    ("L35", "from behind it: out to the chest", 2, still([1.1, -28.3, 1.15], [3.85, -28.8, 0.55], 22)),
    ("L36", "side-on: the arms go into the soil", 2, still([3.9, -31.2, 0.6], [3.85, -28.8, 0.35], 24)),
    ("L37", "low at the soil line where an arm goes in", 2, still([4.7, -30.2, 0.14], [3.85, -29.3, 0.1], 30)),
    ("L38", "my wellies on the wet path", 2, still([-0.3, -26.5, 0.6], [0.5, -28.2, 0.2], 22)),
    ("L39", "its head turned all the way round", 1, still([0.9, -28.5, 1.0], [3.85, -28.8, 0.62], 24)),
    ("L40", "over its shoulder: me, the shed door behind me", 2, still([5.5, -28.2, 1.4], [3.1, -27.9, 1.35], 28)),
    ("L41", "side-on wide: the Digger, me, the shed in a line", 4, still([-1.0, -30.7, 1.2], [3.0, -27.5, 0.9], 19)),
    ("L42", "my face; the door opens behind me", 2, still([4.5, -26.9, 1.5], [3.0, -27.6, 1.3], 20)),
    ("L43", "Mr. Carter in the doorway with the can", 2, still([3.2, -24.4, 1.45], [2.65, -26.95, 1.25], 26)),
    ("L44", "his soaked trousers", 2, still([3.7, -24.9, 0.5], [2.7, -26.9, 0.4], 26)),
    # 04 the can, L45 to L56
    ("L45", "Mr. Carter sees it", 2, still([3.9, -24.5, 1.5], [2.95, -26.3, 1.4], 24)),
    ("L46", "the gate at night: the key in the padlock", 4, still([0.65, -0.75, 1.1], [0.1, 0.0, 1.05], 32)),
    ("L47", "night wide down the path, the gate open", 4, still([0.5, 3.0, 1.6], [0.0, -14.0, 0.6], 19)),
    ("L48", "plot nine at night: water on the leaves", 2, still([3.0, -26.3, 0.85], [3.6, -28.4, 0.6], 28)),
    ("L49", "Friday: Mr. Carter, the can at his side", 2, still([3.9, -24.6, 1.3], [2.95, -26.3, 1.4], 26)),
    ("L50", "high wide of the path in fog: holes beside the prints", 4,
     still([1.0, -1.0, 4.5], [0.0, -19.0, 0.0], 19)),
    ("L51", "over Mr. Carter's shoulder: its green eyes on him", 2, still([3.2, -25.3, 1.55], [3.85, -28.8, 0.75], 24)),
    ("L52", "the can's rose, dripping", 2, still([3.3, -25.5, 0.85], [2.95, -26.0, 0.72], 38)),
    ("L53", "me, from him to the plot", 2, still([4.4, -29.3, 1.5], [3.1, -27.9, 1.4], 22)),
    ("L54", "two shot by the shed; the fog thins", 2, still([4.0, -24.6, 1.45], [3.1, -27.0, 1.3], 22)),
    ("L55", "Mr. Carter, a small smile", 2, still([3.5, -24.4, 1.3], [2.95, -26.25, 1.42], 24)),
    ("L56", "wide from the path: the soil settles", 2, still([0.5, -30.4, 1.1], [3.85, -28.8, 0.4], 21)),
    # 05 passing it on, L57 to L70
    ("L57", "the same angle as L34, clear morning: nothing", 4, still([0.45, -28.2, 1.45], [3.85, -28.8, 0.55], 24)),
    ("L58", "overhead on the hole", 4, still([3.85, -28.7, 2.3], [3.85, -28.82, 0.0], 24)),
    ("L59", "the torch over the hole", 2, still([3.5, -27.0, 1.3], [3.7, -28.8, 0.6], 24)),
    ("P03", "down the shaft: the pale floor and a hand", 4,
     move(([120.0, 0.0, 1.0], [120.0, 0.02, -5]), ([120.0, 0.0, -2.2], [120.0, 0.02, -8]), 30)),
    ("L60", "I fill it, one spade at a time", 2, still([2.0, -30.0, 1.4], [3.4, -29.0, 0.7], 24)),
    ("L61", "Mr. Carter on his bucket, teaching", 2, still([3.4, -27.6, 1.05], [3.2, -25.3, 0.95], 26)),
    ("L62", "me watering at dusk", 2, still([4.9, -27.7, 1.2], [3.1, -27.3, 1.0], 24)),
    ("L63", "I sniff the soil; Mr. Carter nods behind", 2, still([4.4, -28.2, 1.1], [3.1, -27.0, 0.9], 22)),
    ("L64", "high wide: plot nine full, the others green", 4, still([-2.0, -17.5, 7.0], [3.0, -27.0, 0.4], 22)),
    ("L65", "the newcomer wheels her bike down the path, side-on", 2, move(([2.3, -19.6, 1.3], [-0.4, -19.6, 1.2]), ([2.3, -19.7, 1.3], [-0.4, -19.7, 1.2]), 22)),
    ("L66", "plot ten's shed: an empty hook with its clean outline", 2, move(([80.15, 0.5, 1.45], [80.28, 1.9, 1.42]), ([80.2, 0.8, 1.45], [80.28, 1.9, 1.42]), 34)),
    ("L67", "my sleeve and the can toward her sleeve", 2, still([0.0, -24.0, 1.2], [-0.03, -26.4, 1.15], 30)),
    ("L68", "Mr. Carter nods from his bucket", 2, still([3.3, -27.5, 1.0], [3.2, -25.3, 0.95], 28)),
    ("L69", "me and the newcomer at plot ten's edge", 2, still([-1.4, -23.8, 1.5], [-0.1, -26.2, 1.3], 22)),
    ("L70", "plot nine, wet and gold at sunrise", 4, move(([6.9, -23.4, 2.3], [3.5, -28.2, 0.6]),
                                                         ([6.9, -23.9, 2.3], [3.5, -28.2, 0.6]), 20)),
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


hide("carter", 0)
hide("newcomer", 0)
# me
put("me", 0, [3.95, -27.1], yaw=0, lean=6, head=[0, 4], expr="neutral")
key("me", "L01.1", head=[0, 8], lean=0, blend=0.6)
hide("me", "L02")
put("me", "L05", [0.5, 0.4], yaw=-90)
hide("me", "L06")
put("me", "L10", [0.35, -0.9], yaw=yaw_to([0.35, -0.9], [1.5, -3.2]))
put("me", "L11", [0.15, 0.9], yaw=0)
hide("me", "L11.1")
put("me", "L15", [0.3, -2.2], yaw=yaw_to([0.3, -2.2], DIG[1]), expr="worried")
hide("me", "L16")
put("me", "L20", [2.45, -4.1], yaw=yaw_to([2.45, -4.1], DIG[1]), expr="scared", lean=32, head=[0, 18])
hide("me", "L21")
put("me", "L27", [0.0, 3.2], yaw=180)
walk("me", "L27+1.4", [0.0, 0.9])
hide("me", "L28")
put("me", "L31", [0.12, -0.15], yaw=180)
put("me", "L32", [0.12, -0.8], yaw=0)
walk("me", "L32+2.0", [0.12, -5.8])
hide("me", "L32.2")
put("me", "L38", [0.5, -28.2], yaw=yaw_to([0.5, -28.2], DIG[9]), expr="scared")
hide("me", "L39")
put("me", "L40", ME_F, yaw=yaw_to(ME_F, DIG[9]), expr="scared")
key("me", "L43", expr="worried", blend=0.3)
hide("me", "L44")
put("me", "L45", ME_F, yaw=yaw_to(ME_F, CAR_F), expr="worried")
hide("me", "L46")
put("me", "L49", ME_F, yaw=yaw_to(ME_F, CAR_F), expr="worried")
hide("me", "L50")
put("me", "L53", ME_F, yaw=yaw_to(ME_F, CAR_F))
key("me", "L53.1", yaw=yaw_to(ME_F, DIG[9]), blend=0.6)
put("me", "L54", ME_F, yaw=yaw_to(ME_F, CAR_F))
talk("me", "L54", "L54>")
key("me", "L55", expr="soft", blend=0.4)
hide("me", "L57")
put("me", "L59", [3.0, -28.8], yaw=90, arms=[60, 60], head=[0, 24])
put("me", "L60", [3.0, -29.7], yaw=yaw_to([3.0, -29.7], [3.85, -28.8]), arms=[48, 48], side=[-8, -8], lean=14,
    head=[0, 24])
hide("me", "L61")
put("me", "L62", [3.1, -27.3], yaw=yaw_to([3.1, -27.3], [3.9, -28.2]), arms=[40, 40], head=[0, 14])
put("me", "L63", [3.1, -26.9], yaw=yaw_to([3.1, -26.9], [3.8, -27.8]), lean=36, expr="soft", head=[0, 20])
hide("me", "L64")
put("me", "L67", [0.5, -26.3], yaw=-90, arms=[80, 80])
put("me", "L69", [-0.45, -25.9], yaw=-100)
key("me", "L69.1", expr="soft", blend=0.3)
hide("me", "L70")

# Mr. Carter
put("carter", "L05", [-0.5, 0.4], yaw=90, arms=[0, 70])
talk("carter", "L06.1", "L06.2>")
put("carter", "L06", [0.0, 0.2], yaw=180)
walk("carter", "L06+2.0", [0.0, 5.5])
hide("carter", "L07")
put("carter", "L43", DOOR, yaw=90, expr="smirk", head=[0, 10])
put("carter", "L45", CAR_F, yaw=yaw_to(CAR_F, (3.7, -24.8)), expr="wide")
acting["carter"].append({"from": "L45.4", "to": "L45>", "mouth": [0.0, 0.9]})
hide("carter", "L46")
put("carter", "L49", CAR_F, yaw=yaw_to(CAR_F, (3.7, -24.8)), expr="smirk")
talk("carter", "L49.1", "L49>")
key("carter", "L51", yaw=yaw_to(CAR_F, DIG[9]), expr="wide", blend=0.5)
hide("carter", "L52")
put("carter", "L53", CAR_F, yaw=yaw_to(CAR_F, (3.7, -24.8)), expr="wide")
put("carter", "L54", CAR_F, yaw=yaw_to(CAR_F, ME_F))
key("carter", "L55", expr="soft", yaw=yaw_to(CAR_F, (3.5, -24.4)), blend=0.2)
hide("carter", "L57")
BUCKET_SEAT = [BUCKET[0], BUCKET[1], -0.38]
put("carter", "L61", BUCKET_SEAT, yaw=0, arms=[0, 74], sit=True)
hide("carter", "L62")
put("carter", "L63", BUCKET_SEAT, yaw=-30, expr="soft", sit=True, head=[0, 4])
key("carter", "L63.3", head=[0, 12], blend=0.3)
key("carter", "L63.4", head=[0, 0], blend=0.3)
hide("carter", "L64")
put("carter", "L68", BUCKET_SEAT, yaw=-35, expr="soft", sit=True)
key("carter", "L68.1", head=[0, 14], blend=0.3)
key("carter", "L68.2", head=[0, 0], blend=0.35)
hide("carter", "L69")

# the newcomer
put("newcomer", "L65", [-0.45, -18.8], yaw=0, expr="neutral", arms=[60, 0])
walk("newcomer", "L65+2.4", [-0.45, -20.6], arms=[60, 0])
key("newcomer", "L65", expr="neutral")
hide("newcomer", "L66")
put("newcomer", "L67", [-0.55, -26.3], yaw=90, arms=[80, 80])
put("newcomer", "L69", [-1.0, -26.2], yaw=yaw_to([-1.0, -26.2], [-0.45, -25.9]), expr="neutral")
key("newcomer", "L69.1", expr="soft", blend=0.3)
hide("newcomer", "L70")

# ------------------------------------------------------------------------------------------------ cues
cues = [
    # time of day: set.py TOD. Every change between shots is a cut at a shot start or a slow ramp (dur)
    {"at": 0, "name": "tod", "set": "gold"},
    {"at": "L02", "name": "tod", "set": "dawn"},
    {"at": "L05", "name": "tod", "set": "day"},
    {"at": "L11", "name": "tod", "set": "dawn"},
    {"at": "L22", "name": "tod", "set": "gold"},
    {"at": "L23", "name": "tod", "set": "dawn"},
    {"at": "L27", "name": "tod", "set": "early"},
    {"at": "L28", "name": "tod", "set": "dawn"},
    {"at": "L30+0.2", "name": "tod", "set": "fog", "dur": 4.0},
    {"at": "L45+1.0", "name": "tod", "set": "night", "dur": 1.5},
    {"at": "L48+0.8", "name": "tod", "set": "fog", "dur": 1.0},
    {"at": "L54", "name": "tod", "set": "fogthin", "dur": 3.0},
    {"at": "L57", "name": "tod", "set": "clear"},
    {"at": "L61", "name": "tod", "set": "day"},
    {"at": "L61.2", "name": "tod", "set": "dusk", "dur": 1.5},
    {"at": "L62.1", "name": "tod", "set": "day", "dur": 1.0},
    {"at": "L65", "name": "tod", "set": "sunrise"},
    {"at": "L70", "name": "tod", "set": "goldend", "dur": 3.0},
    # the Digger: found where it already stands, never seen moving. up = how far its shoulders stand above the soil
    {"at": 0, "name": "digger", "hidden": True},
    {"at": "L11", "name": "digger", "plot": 1, "up": -0.3, "yaw": 0},
    {"at": "L12", "name": "digger", "plot": 1, "up": 0.2, "yaw": 0},
    {"at": "L17", "name": "digger", "hidden": True},
    {"at": "L21", "name": "digger", "plot": 4, "up": 0.2, "yaw": 0},
    {"at": "L23", "name": "digger", "plot": 7, "up": 0.2, "yaw": 0},
    {"at": "L24", "name": "digger", "plot": 7, "up": 0.42, "yaw": 0},
    {"at": "L25", "name": "digger", "hidden": True},
    {"at": "L29", "name": "digger", "plot": 7, "up": 0.42, "yaw": 0},
    {"at": "L30", "name": "digger", "hidden": True},
    {"at": "L34", "name": "digger", "plot": 9, "up": 0.5, "yaw": 90, "head": 0},
    {"at": "L39", "name": "digger", "plot": 9, "up": 0.5, "yaw": 90, "head": 180},
    {"at": "L46", "name": "digger", "hidden": True},
    {"at": "L49", "name": "digger", "plot": 9, "up": 0.5, "yaw": 90, "head": 180},
    {"at": "L56", "name": "digger", "plot": 9, "up": 0.2, "yaw": 90, "head": 180},
    {"at": "L57", "name": "digger", "hidden": True},
    # holes: plots listed. 1 from Tuesday, 4 from Wednesday's feeding, 7 from Friday; 9 on Saturday
    {"at": 0, "name": "holes", "plots": []},
    {"at": "L17", "name": "holes", "plots": [1]},
    {"at": "L22", "name": "holes", "plots": [1, 4]},
    {"at": "L25", "name": "holes", "plots": [1, 4]},
    {"at": "L29", "name": "holes", "plots": [1, 4]},
    {"at": "L30", "name": "holes", "plots": [1, 4, 7]},
    {"at": "L57", "name": "holes", "plots": [9]},
    {"at": "L61", "name": "holes", "plots": []},
    {"at": "L60+0.4", "name": "mound", "on": True},
    # props
    {"at": 0, "name": "key", "where": "off"},
    {"at": "L05", "name": "key", "where": "carter"},
    {"at": "L06", "name": "key", "where": "off"},
    {"at": "L46", "name": "key", "where": "padlock"},
    {"at": "L47", "name": "key", "where": "off"},
    {"at": 0, "name": "can", "where": "off"},
    {"at": "L43", "name": "can", "where": "carter"},
    {"at": "L46", "name": "can", "where": "off"},
    {"at": "L49", "name": "can", "where": "carter"},
    {"at": "L52", "name": "can", "where": "world", "pos": [2.95, -26.0, 0.72], "rot": [0.0, 0.0, 70.0]},
    {"at": "L53", "name": "can", "where": "carter"},
    {"at": "L56", "name": "can", "where": "off"},
    {"at": "L62", "name": "can", "where": "me", "water": True},
    {"at": "L63", "name": "can", "where": "off"},
    {"at": "L67", "name": "can", "where": "world", "pos": [-0.03, -25.3, 1.3], "rot": [0.0, 0.0, 0.0], "scale": 1.8},
    {"at": "L68", "name": "can", "where": "off"},
    {"at": 0, "name": "torch", "on": 0.0},
    {"at": "L59", "name": "torch", "on": 1.0, "dur": 0.8},
    {"at": "L60", "name": "torch", "on": 0.0, "dur": 0.8},
    {"at": 0, "name": "spade", "on": False},
    {"at": "L60", "name": "spade", "on": True},
    {"at": "L61", "name": "spade", "on": False},
    {"at": "L19+0.45", "name": "pebble", "on": True},
    {"at": "L25", "name": "cane", "on": True, "sink": "L26"},
    {"at": "L27", "name": "cane", "on": False},
    {"at": 0, "name": "bucket", "on": False},
    {"at": "L61", "name": "bucket", "on": True},
    {"at": 0, "name": "bike", "on": False},
    {"at": "L65", "name": "bike", "on": True},
    {"at": "L67", "name": "bike", "on": True, "pos": [-1.0, -27.0], "yaw": 80},
    {"at": "L70", "name": "bike", "on": False},
    # the padlock: 0 dry, 1 beaded (L09), 2 threads (L28), 3 dripping (L31)
    {"at": 0, "name": "padlock", "wet": 0},
    {"at": "L09", "name": "padlock", "wet": 1},
    {"at": "L10", "name": "padlock", "wet": 1},
    {"at": "L11", "name": "padlock", "wet": 1},
    {"at": "L28", "name": "padlock", "wet": 2},
    {"at": "L29", "name": "padlock", "wet": 2},
    {"at": "L31", "name": "padlock", "wet": 3},
    {"at": "L32", "name": "padlock", "wet": 3},
    # water drops: the leaf at plot nine, and a sprinkle across the leaves
    {"at": 0, "name": "sprinkle", "on": False},
    {"at": "L48", "name": "sprinkle", "on": True},
    {"at": "L49", "name": "sprinkle", "on": False},
    # the gate swings open at night (L47) and shut again
    {"at": 0, "name": "gate", "open": 0.0},
    {"at": "L47", "name": "gate", "open": 1.0},
    {"at": "L48", "name": "gate", "open": 0.0},
    # the shed door opens slowly onto the dark (about 0.8 s)
    {"at": 0, "name": "shed", "open": 0.0},
    {"at": "L42+0.35", "name": "shed", "open": 1.0, "dur": 0.8},
    {"at": "L46", "name": "shed", "open": 1.0},
    # the other plots go green in the spring
    {"at": 0, "name": "greens", "on": False},
    {"at": "L64", "name": "greens", "on": True},
]

sfx = [
    {"at": "L09", "kind": "click", "db": -20},
    {"at": "L09+0.7", "kind": "click", "db": -24},
    {"at": "P01+0.55", "kind": "click", "db": -22},
    {"at": "L21", "kind": "whoosh", "db": -30, "dur": 0.8},
    {"at": "P02+0.3", "kind": "hit", "db": -9},
    {"at": "L39", "kind": "sting", "db": -11},
    {"at": "L42+0.3", "kind": "door", "db": -15, "dur": 1.0},
    {"at": "L56+0.5", "kind": "glide", "db": -17, "dur": 1.6},
    {"at": "L56+0.5", "kind": "thud", "db": -24},
    {"at": "L59", "kind": "click", "db": -15},
    {"at": "L60+0.4", "kind": "thud", "db": -22},
    {"at": "L60+1.2", "kind": "thud", "db": -22},
    {"at": "L60+2.0", "kind": "thud", "db": -22},
    {"at": "L70.2", "kind": "bell", "db": -8, "dur": 2.0},
]

story = {
    "slug": "ep25-plot-nine",
    "title": "In a six-week drought, my allotment plot is wet every single dawn.",
    "made_for_kids": False,
    "premise": "In the driest spring on the hill, I take over old Mr. Carter's allotment plot when he says it's time for somebody new. Every plot cracks in the sun but mine, which is dark and wet at every dawn. A head and shoulders of root-wrapped soil rises out of plot one by the gate, and each dawn it is in a bed further down the path, nearer to my beans, leaving a round hole that no cane can find the bottom of.",
    "twist": "Mr. Carter never stopped coming. Every night since he gave me the key he has let himself in with his old key and his old can to water the plot he couldn't let go of, and the thing in the soil rises along the path he walks, following him in to plot nine. The smell of rain was his can, and six weeks is how long since he gave me the key.",
    "world": "allotment gardens on a gentle hillside at dawn in a dry spring: a five-bar gate and an iron padlock, a dusty path, ten plots of cracked clay, tarred sheds, one dark wet plot of bean canes, and mist filling the valley below",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#9be04a",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#a7a9b0", "fog_density": 0.018, "fog_start": 4.0, "sky": "#e7b896", "sky_strength": 1.0,
             "exposure": 0.0},
    "grade": {"shadows": [-0.02, 0.0, 0.05], "highlights": [0.03, 0.01, -0.03], "saturation": 0.95, "contrast": 1.06,
              "vignette": 0.36, "bloom": 0.26, "grain": 0.012},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 50, "mode": "dorian", "bpm": 68, "seed": 25,
              "sections": [
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L11", "voices": ["drone", "pad", "pulse"], "energy": 0.36},
                  {"at": "L19", "voices": ["drone"], "energy": 0.25},
                  {"at": "L21", "voices": ["drone", "pad", "pulse"], "energy": 0.42},
                  {"at": "L30", "voices": ["drone", "pad", "pulse"], "energy": 0.5},
                  {"at": "L34", "voices": ["drone"], "energy": 0.25},
                  {"at": "L35", "voices": ["drone", "pad", "choir"], "energy": 0.5},
                  {"at": "L43", "voices": ["drone", "pad"], "energy": 0.36},
                  {"at": "L46", "voices": ["pad", "drone"], "energy": 0.3},
                  {"at": "L49", "voices": ["drone", "pad", "pulse"], "energy": 0.42},
                  {"at": "L54", "voices": ["piano", "pad", "drone"], "energy": 0.45, "mode": "major", "root": 50},
                  {"at": "L61", "voices": ["piano", "pad"], "energy": 0.4},
                  {"at": "L67", "voices": ["piano", "pad", "drone"], "energy": 0.45},
              ]},
    "sound": {"floor": "grass", "steps_db": -22,
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "end", "lufs": -36},
                  {"kind": "drips", "from": "L09", "to": "L11", "lufs": -40},
                  {"kind": "drips", "from": "L28", "to": "L29", "lufs": -40},
                  {"kind": "drips", "from": "L31", "to": "L32", "lufs": -40},
                  {"kind": "drips", "from": "L48", "to": "L49", "lufs": -38},
                  {"kind": "drips", "from": "L52", "to": "L53", "lufs": -40},
                  {"kind": "crickets", "from": "L46", "to": "L49", "lufs": -40},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01-0.3", "to": "L20", "keep": ["click"]},
                              {"from": "L34+0.8", "to": "L35", "keep": ["hit"]},
                              {"from": "L38+0.4", "to": "L39+0.35", "keep": ["sting"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
