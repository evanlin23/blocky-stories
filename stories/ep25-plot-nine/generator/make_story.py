"""Writes ../story.json for ep25 "Plot nine" (redo round 2, 2026-11-03: the root-thing is Mum, who is leaving).

Run from anywhere: python stories/ep25-plot-nine/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (time of day, the Digger, the holes, roots, props), the score and the sound.

Places are set.py's metres. The path runs down the hill along -y from the gate at y = 0; a character with yaw 0 faces
-y, yaw 90 faces +x, yaw 180 faces the gate. Odd plots are on the left (x > 0), even plots on the right (x < 0), five
rows of five metres: row r spans y = -1.5 - 6r .. -6.5 - 6r. Plot nine is row 4 on the left: x 1..6, y -25.5..-30.5;
Mum's shed is at its path corner (x 1.0..2.4, y -27.6..-25.8), its door on the +x face. Plot ten (mine) is across the path.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# ------------------------------------------------------------------------------------------------ pauses
PAUSES = {"L19": ("P01", 1.0), "L26": ("P02", 0.7)}
full = []
for ln in lines:
    full.append(ln)
    if ln["id"] in PAUSES:
        pid, dur = PAUSES[ln["id"]]
        full.append({"id": pid, "pause": dur, "chunks": []})
LOOP = 0.25
full.append({"id": "P04", "pause": LOOP, "chunks": []})
lines = full

TEMPO = {"L17": 0.93, "L36": 0.93, "L31": 0.93}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]

cast = {
    "me": {"age": "adult", "skin": "#d9a07c", "shirt": "#5d7d3c", "pattern": "knit", "pattern_c": "#46632d",
           "collar": "#4a6a30", "pants": "#6b4a2e", "shoes": "#2d6a38", "sleeves": "long", "hair": "cap",
           "hair_c": "#1c1612", "hat": "none", "face": {"eyes": "round", "brows": True, "ink": "#161012"}},
    "carter": {"age": "adult", "skin": "#dcb08f", "shirt": "#6e4c32", "pattern": "knit", "pattern_c": "#58391f",
               "collar": "#b9b29a", "pants": "#4a463e", "shoes": "#2a2a22", "sleeves": "long", "hair": "cap",
               "hair_c": "#7b6d58", "hat": "none", "height": 0.97,
               "face": {"eyes": "tired", "brows": True, "ink": "#1c1613", "bags": True}},
    # Mum: skin matched to mine, dark hair going grey, the mustard windbreaker and ponytail kept
    "newcomer": {"age": "adult", "skin": "#d9a07c", "shirt": "#c4872c", "pattern": "solid", "collar": "#a8721f",
                 "pants": "#cfc4ab", "shoes": "#33353a", "sleeves": "long", "hair": "cap", "hair_c": "#5e5550",
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


def around(p, d, az, z):
    """A camera spot d metres from p, in the compass direction az (the same yaw convention: 0 is -y, 90 is +x)."""
    a = math.radians(az)
    return [round(p[0] + d * math.sin(a), 2), round(p[1] - d * math.cos(a), 2), z]


def portrait(p, yaw, d, off, z, lens, tz=1.5):
    """In front of a character at p facing yaw, off degrees round to one side, aimed at the head."""
    return still(around(p, d, yaw + off, z), [p[0], p[1], tz], lens)


# places
DIG = {1: (3.4, -3.6), 4: (-3.6, -10.0), 7: (3.4, -22.0), 9: (4.3, -26.0)}
UP = {"lump": -0.5, "shoulders": 0.3, "arms": 0.55, "chest": 0.8, "waist": 1.05}
PELL = (3.4, -9.8)              # old Mr Pell's bed, plot three
PELL_AZ = yaw_to(PELL, (1.6, -8.0))   # the way he faces and the camera stands
POT = (0.0, -1.9)               # the giant pot on its barrow, by the gate
MUMP = (3.8, -27.7)             # Mum at plot nine
MUM_DOOR = (2.95, -26.95)       # Mum in her shed doorway
ME10 = (-3.2, -27.4)            # me in my bare plot
BUCKET9 = (3.8, -29.1)
BUCKET10 = (-1.55, -27.3)
FLASK10 = (-1.55, -26.8)
GATE_M = (0.15, -0.9)           # Mum at the gate
HEAD_TO_MUM = round(yaw_to(DIG[9], MUMP) - 180)   # the head's own turn, from facing the gate round to Mum

# ------------------------------------------------------------------------------------------------ shots
# (at, what, step, camera)
SHOTS = [
    # 01 the rule, L01 to L12
    (0, "S01 Mr Pell in his bed, roots fanned from his wellies", 2,
     still(around(PELL, 3.8, PELL_AZ, 0.95), [PELL[0], PELL[1], 0.85], 30)),
    ("L02", "S02 high wide: his root runs out and up the path to the gate", 4,
     move(([2.4, -8.0, 4.2], [0.3, -5.0, 0.0]), ([2.1, -7.4, 4.0], [0.3, -4.8, 0.0]), 26)),
    ("L02.3", "S03 the root's tip curled round the gate post", 4, still([0.2, -1.2, 0.4], [1.05, 0.0, 0.12], 40)),
    ("L03", "S04 Mr Pell in a giant pot on a barrow", 2, still([0.7, -5.9, 1.0], [POT[0], POT[1], 1.2], 32)),
    ("L04", "S05 three umbrellas, root fans at their tips", 4,
     move(([3.3, -2.5, 0.55], [1.9, -0.6, 0.35]), ([3.1, -2.3, 0.55], [1.9, -0.6, 0.35]), 26)),
    ("L05", "S06 my wellies on the raked soil", 4, still([-0.9, -24.8, 0.45], [ME10[0], ME10[1], 0.2], 36)),
    ("L05.2", "S07 me looking down at them", 2, still([-1.7, -25.2, 1.35], [ME10[0], ME10[1], 1.1], 34)),
    ("L06", "S08 me alone on my bare plot", 2, still([-6.0, -21.5, 1.6], [-2.6, -27.0, 0.7], 26)),
    ("L07", "S09 Mum at plot nine, a wave; me in the foreground", 2, still([-0.3, -31.2, 1.5], [MUMP[0], MUMP[1], 1.4], 55)),
    ("L07.2", "S10 her wellies, a thick fan of roots", 4, still([5.1, -26.6, 0.5], [MUMP[0], MUMP[1], 0.12], 34)),
    ("L08.1", "S11 high wide up the path: her root run", 4,
     move(([0.0, -27.5, 6.5], [0.3, -12.0, 0.0]), ([0.0, -26.5, 6.5], [0.3, -11.0, 0.0]), 24)),
    ("L09", "S12 the run under plot seven's board", 4, still([-0.6, -20.4, 0.28], [1.0, -22.0, 0.05], 34)),
    ("L09.2", "S13 the same at plot four", 4, still([0.6, -9.2, 0.28], [-1.0, -10.2, 0.05], 34)),
    ("L10", "S14 across the path, side-on", 2, still([0.0, -23.6, 1.5], [0.0, -27.5, 1.35], 24)),
    ("L11", "S15 the bucket set down at my plot's edge", 4, still([-0.3, -25.2, 0.7], [BUCKET10[0], BUCKET10[1], 0.15], 40)),
    ("L11.3", "S16 the flask beside it", 4, still([-0.5, -26.0, 0.6], [FLASK10[0], FLASK10[1], 0.13], 44)),
    ("L11.3>", "S17 Mum's shed, the tool wall bare", 4,
     move(([60.4, 0.1, 1.42], [60.45, 1.8, 1.38]), ([60.4, 0.3, 1.42], [60.45, 1.8, 1.38]), 30)),
    ("L12.1", "S18 Mum in her shed doorway, a little too bright", 2,
     still(around(MUM_DOOR, 2.6, 90 - 22, 1.5), [MUM_DOOR[0], MUM_DOOR[1], 1.5], 48)),
    # 02 the head, L13 to L24
    ("L13", "S19 over my shoulder: a lump in plot one", 2, still([-0.6, 3.4, 1.9], [3.4, -3.6, 0.3], 26)),
    ("L14", "S20 plot one: the head and shoulders, roots, the ring", 4, still([1.9, -6.8, 0.8], [3.4, -3.6, 0.85], 30)),
    ("L15", "S21 its face: two green points", 4, still([3.45, -1.5, 1.1], [3.4, -3.6, 1.3], 32)),
    ("L16", "S22 from behind and lower: the back of its head, the gate", 4, still([3.2, -5.8, 0.4], [3.4, -3.6, 1.2], 28)),
    ("L17", "S23 Mum looking up the path", 2, portrait(MUMP, 180, 4.3, 3, 1.5, 68)),
    ("L18", "S24 plot one, a neat round hole", 4, still([1.0, -3.7, 0.65], [3.4, -3.6, 0.1], 30)),
    ("L19", "S25 a pebble drops into the black", 4, still([2.4, -4.8, 0.9], [3.4, -3.6, 0.1], 28)),
    ("P01", "S26 the black hole, held", 4, still([3.4, -3.55, 2.0], [3.4, -3.62, 0.0], 24)),
    ("L20", "S27 me crouched by the hole, listening", 2, portrait((2.45, -4.1), yaw_to((2.45, -4.1), DIG[1]), 2.8, 30, 1.4, 34, 1.1)),
    ("L21", "S28 wide: the hole, and the head in plot four", 4, still([4.0, -1.6, 0.55], [-2.0, -9.6, 0.6], 22)),
    ("L22", "S29 the groove in the path above plot four", 4, still([0.0, -4.0, 3.4], [-0.2, -8.6, 0.0], 30)),
    ("L22.1", "S30 Mum's wellies, the fan thinner", 4, still([5.1, -26.4, 0.45], [MUMP[0], MUMP[1], 0.12], 34)),
    ("L23", "S31 long lens from the gate: the head in plot seven", 4, still([0.5, -1.0, 1.0], [3.4, -22.0, 0.5], 70)),
    ("L23.2", "S32 plot seven: out to the chest", 2, still([0.0, -22.0, 1.0], [3.4, -22.0, 1.2], 28)),
    ("L24", "S33 Mum at the gate looking out, the head far behind her", 2,
     portrait(GATE_M, 180, 3.4, 25, 1.5, 38, 1.35)),
    # 03 Friday, L25 to L36
    ("L25", "S34 wide over the bottom fence: mist coming up", 4,
     move(([0.0, -33.2, 1.5], [0.0, -10.0, 1.0]), ([0.0, -33.2, 1.5], [0.0, -10.0, 1.0]), 19)),
    ("L26", "S35 between the beans, a shape with its back to us", 2, still([-0.2, -31.2, 1.2], [DIG[9][0], DIG[9][1], 1.45], 30)),
    ("P02", "S36 hold", 4, still([-0.2, -31.2, 1.2], [DIG[9][0], DIG[9][1], 1.45], 30)),
    ("L27", "S37 its head turned all the way round", 1,
     still(around(DIG[9], 3.4, yaw_to(DIG[9], MUMP) - 30, 1.3), [DIG[9][0], DIG[9][1], 2.0], 38)),
    ("L27.3", "S38 over its shoulder: Mum by her shed", 2,
     still(around(DIG[9], 1.9, yaw_to(MUMP, DIG[9]) + 40, 1.7), [MUMP[0], MUMP[1], 1.5], 55)),
    ("L28", "S39 Mum close, calm, eyes on it", 2, portrait(MUMP, yaw_to(MUMP, DIG[9]), 2.4, 38, 1.5, 58)),
    ("L29", "S40 low along the soil: a root leaving its waist", 4, still([5.0, -27.6, 0.5], [4.0, -26.8, 0.1], 28)),
    ("L30", "S41 the picture: the root from its waist to her boots", 4,
     still([6.8, -30.0, 0.9], [4.0, -27.0, 0.6], 20)),
    ("L30.2", "S42 her wellies, the run joining her fan", 4, still([5.0, -28.6, 0.5], [3.9, -27.5, 0.1], 34)),
    ("L31", "S43 side-on wide: Mum and the Digger across the bean row", 4,
     still([7.0, -29.0, 1.6], [4.0, -26.85, 1.3], 30)),
    ("L32", "S44 high wide down the path: the holes in a line", 4, still([0.4, -3.0, 6.0], [0.3, -24.0, 0.0], 24)),
    ("L33", "S45 overhead on plot seven's hole", 4, still([3.4, -21.9, 2.6], [3.4, -22.0, 0.0], 24)),
    ("L34", "S46 Mum, worried, eyes down", 2, portrait(MUMP, yaw_to(MUMP, DIG[9]), 2.5, -30, 1.45, 58)),
    ("L35", "S47 me, scared, looking from the Digger to Mum", 2, portrait((2.2, -29.7), yaw_to((2.2, -29.7), MUMP), 2.0, 40, 1.5, 50)),
    ("L36", "S48 wide from behind me at plot ten", 2, still([-5.4, -28.6, 1.4], [0.5, -28.0, 1.1], 28)),
    # 04 the bucket, L37 to L43
    ("L37", "S49 me, resolved, turning to Mum", 2, portrait((2.2, -29.7), yaw_to((2.2, -29.7), MUMP), 2.4, 25, 1.5, 55)),
    ("L37.3", "S50 callback: Mr Pell in his pot", 2, still([0.7, -5.9, 1.0], [POT[0], POT[1], 1.2], 32)),
    ("L38", "S51 the bucket full of plot nine's soil", 4, still([2.4, -27.0, 0.9], [BUCKET9[0], BUCKET9[1], 0.2], 36)),
    ("L39", "S52 one bean in the soil", 4, still([3.0, -27.9, 0.65], [BUCKET9[0], BUCKET9[1], 0.3], 44)),
    ("L40", "S53 Mum beside the bucket, her roots curl in", 2,
     still([5.4, -30.3, 1.3], [MUMP[0], MUMP[1] - 0.8, 1.0], 32)),
    ("L41", "S54 the Digger settling to the shoulders", 4, still([0.7, -30.2, 1.1], [DIG[9][0], DIG[9][1], 0.6], 22)),
    ("L41.3", "S55 flat dark soil with a round dent", 4, still([3.6, -23.3, 1.3], [DIG[9][0], DIG[9][1], 0.0], 26)),
    ("L42", "S56 Mum wheels her bike up the path, the bucket on the bars", 2,
     move(([1.8, -16.6, 1.1], [-0.2, -13.2, 0.8]), ([1.8, -16.2, 1.1], [-0.2, -12.8, 0.8]), 32)),
    ("L43", "S57 Mum at the gate turns round and looks right back", 2,
     still(around(GATE_M, 2.5, -20, 1.5), [GATE_M[0], GATE_M[1], 1.45], 52)),
    ("L43.2", "S58 me, a small wave", 2, portrait((-0.4, -23.0), 180, 2.8, 25, 1.5, 44)),
    # 05 the sting, L44 to L46
    ("L44", "S59 high wide, a grey dawn, the holes", 4, still([0.0, 3.0, 6.5], [0.2, -18.0, 0.0], 20)),
    ("L45", "S60 a pebble drops into plot one's hole", 4, still([2.4, -4.8, 0.9], [3.4, -3.6, 0.1], 28)),
    ("L46", "S61 me crouched by the hole, hearing it", 2, portrait((2.45, -4.1), yaw_to((2.45, -4.1), DIG[1]), 2.8, 30, 1.4, 34, 1.1)),
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


# old Mr Pell: his bed (L01), the pot by the gate (L03), the callback (L37.2)
put("carter", 0, [PELL[0], PELL[1]], yaw=PELL_AZ, expr="smile", head=[0, 0])
hide("carter", "L02")
put("carter", "L03", [POT[0], POT[1], 0.6], yaw=0, expr="smirk", head=[0, 6])
hide("carter", "L04")
put("carter", "L37.3", [POT[0], POT[1], 0.6], yaw=0, expr="smirk", head=[0, 6])
hide("carter", "L38")

# me
hide("me", 0)
put("me", "L05", ME10, yaw=yaw_to(ME10, (-2.2, -25.9)), expr="neutral")
put("me", "L05.2", ME10, yaw=yaw_to(ME10, (-1.7, -25.2)), expr="neutral", head=[0, -22])
put("me", "L06", ME10, yaw=270, expr="neutral", head=[0, 0])
put("me", "L07", [1.3, -30.9], yaw=yaw_to([1.3, -30.9], MUMP), expr="neutral", head=[0, 0])
put("me", "L10", [-1.15, -27.6], yaw=90, expr="worried", head=[0, 0])
hide("me", "L11")
put("me", "L13", [-0.3, 1.5], yaw=0, head=[0, 4])
hide("me", "L14")
put("me", "L20", [2.45, -4.1], yaw=yaw_to([2.45, -4.1], DIG[1]), expr="scared", lean=32, head=[0, 18])
hide("me", "L21")
put("me", "L31", [4.7, -27.4], yaw=yaw_to([4.7, -27.4], DIG[9]), expr="scared", head=[0, 0])
key("me", "L31>", head=[0, 18], blend=0.4)
put("me", "L35", [2.2, -29.7], yaw=yaw_to([2.2, -29.7], MUMP), expr="scared", head=[0, 0])
put("me", "L36", ME10, yaw=270, expr="worried")
put("me", "L37", [2.2, -29.7], yaw=yaw_to([2.2, -29.7], MUMP), expr="neutral")
key("me", "L37.3", expr="neutral", yaw=yaw_to([2.2, -29.7], MUMP), blend=0.4)
hide("me", "L37.3")
hide("me", "L38")
put("me", "L43.2", [-0.4, -23.0], yaw=180, expr="smile", arms=[0, 70])
key("me", "L43.2+0.4", arms=[0, 40], blend=0.3)
key("me", "L43.2+0.8", arms=[0, 75], blend=0.3)
hide("me", "L44")
put("me", "L46", [2.45, -4.1], yaw=yaw_to([2.45, -4.1], DIG[1]), expr="worried", lean=32, head=[0, 18])

# Mum
hide("newcomer", 0)
put("newcomer", "L07", MUMP, yaw=yaw_to(MUMP, (-0.3, -31.2)), expr="smile", arms=[0, 70])
key("newcomer", "L07+0.5", arms=[0, 40], blend=0.3)
key("newcomer", "L07+0.9", arms=[0, 75], blend=0.3)
put("newcomer", "L08", MUMP, yaw=0, expr="neutral")
put("newcomer", "L10", [1.15, -27.6], yaw=0, expr="neutral", head=[0, 0])
hide("newcomer", "L11")
put("newcomer", "L12.1", MUM_DOOR, yaw=90, expr="smile", head=[0, 0])
hide("newcomer", "L13")
put("newcomer", "L17", MUMP, yaw=180, expr="neutral", head=[0, 0])
hide("newcomer", "L18")
put("newcomer", "L22.1", MUMP, yaw=180, expr="neutral")
hide("newcomer", "L23")
put("newcomer", "L24", GATE_M, yaw=180, expr="worried", head=[0, 0])
hide("newcomer", "L25")
put("newcomer", "L27.3", MUMP, yaw=yaw_to(MUMP, DIG[9]), expr="neutral", blink=False)
put("newcomer", "L28", MUMP, yaw=yaw_to(MUMP, DIG[9]), expr="neutral", blink=False)
put("newcomer", "L34", MUMP, yaw=yaw_to(MUMP, DIG[9]), expr="worried", head=[0, 14])
put("newcomer", "L36", MUMP, yaw=yaw_to(MUMP, DIG[9]), expr="worried")
hide("newcomer", "L37")
put("newcomer", "L40", MUMP, yaw=yaw_to(MUMP, (5.4, -30.3)), expr="smile", head=[0, 0])
hide("newcomer", "L41")
put("newcomer", "L42", [-0.3, -15.0], yaw=180, expr="smile", arms=[0, 60])
walk("newcomer", "L42>", [-0.3, -11.5], arms=[0, 60])
hide("newcomer", "L43")
put("newcomer", "L43", GATE_M, yaw=0, expr="smile", arms=[0, 60])
hide("newcomer", "L44")

# ------------------------------------------------------------------------------------------------ cues
def tod(at, name, dur=0.3):
    return {"at": at, "name": "tod", "set": name, "dur": dur}


cues = [
    {"at": 0, "name": "tod", "set": "bright"},
    tod("L13", "dawn", 0.6),
    tod("L18", "tue", 0.6),
    tod("L23", "wed", 0.6),
    {"at": "L25", "name": "tod", "set": "fog", "dur": 3.0},
    {"at": "L41", "name": "tod", "set": "fogthin", "dur": 2.5},
    {"at": "L42", "name": "tod", "set": "bright", "dur": 1.2},
    {"at": "L44", "name": "tod", "set": "grey", "dur": 0.8},
    # the Digger: found where it already stands, never seen moving. Every pose faces the gate (yaw 180).
    {"at": 0, "name": "digger", "hidden": True},
    {"at": "L13", "name": "digger", "plot": 1, "up": UP["lump"], "yaw": 180},
    {"at": "L14", "name": "digger", "plot": 1, "up": UP["shoulders"], "yaw": 180},
    {"at": "L18", "name": "digger", "hidden": True},
    {"at": "L21", "name": "digger", "plot": 4, "up": UP["arms"], "yaw": 180},
    {"at": "L23", "name": "digger", "plot": 7, "up": UP["chest"], "yaw": 180},
    {"at": "L25", "name": "digger", "hidden": True},
    {"at": "L26", "name": "digger", "plot": 9, "up": UP["waist"], "yaw": 180, "head": 0},
    {"at": "L27", "name": "digger", "plot": 9, "up": UP["waist"], "yaw": 180, "head": HEAD_TO_MUM},
    {"at": "L41", "name": "digger", "plot": 9, "up": UP["shoulders"], "yaw": 180, "head": HEAD_TO_MUM},
    {"at": "L41.3", "name": "digger", "hidden": True},
    # the holes stay open to the end (the sting drops a pebble down plot one)
    {"at": 0, "name": "holes", "plots": []},
    {"at": "L18", "name": "holes", "plots": [1]},
    {"at": "L23", "name": "holes", "plots": [1, 4]},
    {"at": "L25", "name": "holes", "plots": [1, 4, 7]},
    {"at": 0, "name": "dent", "on": False},
    {"at": "L41.3", "name": "dent", "on": True},
    # roots: Mum's run up the path (to = the highest y it still reaches), her fan, the Digger's run to her boots
    {"at": 0, "name": "mumrun", "to": 0.0, "groove": False},
    {"at": "L18", "name": "mumrun", "to": -9.0, "groove": True},
    {"at": "L23", "name": "mumrun", "to": -19.0, "groove": True},
    {"at": "L25", "name": "mumrun", "to": -100.0, "groove": False},
    {"at": 0, "name": "mumfan", "pos": MUMP, "yaw": 180, "scale": 1.0},
    {"at": "L18", "name": "mumfan", "pos": MUMP, "yaw": 180, "scale": 0.62},
    {"at": "L23", "name": "mumfan", "pos": MUMP, "yaw": 180, "scale": 0.4},
    {"at": "L24", "name": "mumfan", "off": True},
    {"at": "L27.3", "name": "mumfan", "pos": MUMP, "yaw": yaw_to(MUMP, DIG[9]), "scale": 0.4},
    {"at": "L40", "name": "mumfan", "pos": MUMP, "yaw": yaw_to(MUMP, BUCKET9), "scale": 0.4, "bucket": True},
    {"at": "L41", "name": "mumfan", "off": True},
    {"at": "L42", "name": "mumfan", "off": True},
    {"at": "L43", "name": "mumfan", "pos": GATE_M, "yaw": 0, "scale": 0.5},
    {"at": "L44", "name": "mumfan", "off": True},
    {"at": 0, "name": "digrun", "on": False},
    {"at": "L29", "name": "digrun", "on": True},
    {"at": "L40", "name": "digrun", "on": False},
    # props: the bucket (upright, then full of soil), the flask, the bean, the bike
    {"at": 0, "name": "bucket", "pos": [-20.0, -20.0], "full": False, "bean": False},
    {"at": "L11", "name": "bucket", "pos": list(BUCKET10), "full": False, "bean": False},
    {"at": "L12", "name": "bucket", "pos": [-20.0, -20.0], "full": False, "bean": False},
    {"at": "L38", "name": "bucket", "pos": list(BUCKET9), "full": True, "bean": False},
    {"at": "L39", "name": "bucket", "pos": list(BUCKET9), "full": True, "bean": True},
    {"at": "L41", "name": "bucket", "pos": [-20.0, -20.0], "full": True, "bean": True},
    {"at": 0, "name": "flask", "pos": [-20.0, -20.0]},
    {"at": "L11.3", "name": "flask", "pos": list(FLASK10)},
    {"at": "L12", "name": "flask", "pos": [-20.0, -20.0]},
    {"at": "L03", "name": "pot", "on": True},
    {"at": "L04", "name": "pot", "on": False},
    {"at": "L37.3", "name": "pot", "on": True},
    {"at": "L38", "name": "pot", "on": False},
    {"at": 0, "name": "bike", "on": False},
    {"at": "L42", "name": "bike", "on": True},
    {"at": "L44", "name": "bike", "on": False},
    {"at": "L42", "name": "gate", "open": 1.0, "dur": 2.0},
    {"at": "L44", "name": "gate", "open": 0.0, "dur": 0.5},
    {"at": "L19+0.35", "name": "pebble", "on": True, "from": [3.2, -3.85], "to": [3.4, -3.6]},
    {"at": "L45+0.35", "name": "pebble", "on": True, "from": [3.2, -3.85], "to": [3.4, -3.6]},
]

sfx = [
    {"at": "P01+0.55", "kind": "tock", "db": -26, "dur": 0.3},
    {"at": "P02+0.3", "kind": "hit", "db": -10, "lowpass": 3000},
    {"at": "L29+0.1", "kind": "rootcreak", "db": -21, "dur": 3.2},
    {"at": "L41+0.3", "kind": "glide", "db": -18, "dur": 1.6, "lowpass": 3000},
    {"at": "L41+0.3", "kind": "thud", "db": -24},
    {"at": "L46>-0.3", "kind": "tock", "db": -17, "dur": 0.5},
]

story = {
    "slug": "ep25-plot-nine",
    "title": "On This Hill You Grow ROOTS Where You Belong",
    "made_for_kids": False,
    "premise": "On an allotment hill where everyone grows roots into the ground where they belong, I'm the only gardener whose boots come up clean. Mum has plot nine across the path from mine, and her roots are the longest on the hill, running up the path under every plot she's ever had. This week she gives me her bucket and her flask. Then a head and shoulders of soil and roots with no face comes up in plot one by the gate, facing the gate, and every dawn it's a plot nearer to hers while her roots get shorter.",
    "twist": "The faceless thing is Mum: every root she ever put down on this hill, coming up in her shape, because she is leaving and couldn't tell me. Nobody up here moves house, they get repotted, so I fill her bucket with plot nine and one bean, her roots climb in, and she wheels it out through the gate. The pebble that never landed lands, because nothing of her is left in the hole.",
    "world": "allotment gardens on a hillside at dawn in a dry spring: a five-bar gate with a chain and padlock, a dusty path, ten plots of pale cracked clay with dark roots fanned across them, creosote sheds, one dark worked plot of bean canes, a bare raked bed, and mist filling the valley below",
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
    "phonemes": {"in": "ˈɪn"},
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
                  {"at": "L19>", "voices": ["drone"], "energy": 0.25},
                  {"at": "L20", "voices": ["drone", "pad", "pulse"], "energy": 0.42},
                  {"at": "L26>", "voices": ["drone"], "energy": 0.25},
                  {"at": "L27", "voices": ["drone", "pad", "pulse"], "energy": 0.5},
                  {"at": "L38", "voices": ["piano", "pad", "drone"], "energy": 0.45, "mode": "major", "root": 50},
                  {"at": "L44", "voices": ["drone"], "energy": 0.28, "mode": "dorian", "root": 50},
              ]},
    "sound": {"floor": "grass", "steps_db": -22,
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "end", "lufs": -36, "lowpass": 3000},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01-0.2", "to": "L20", "keep": ["tock"]},
                              {"from": "P02", "to": "L27+0.5", "keep": ["hit"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
