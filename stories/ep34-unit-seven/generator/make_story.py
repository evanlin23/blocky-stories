"""Writes ../story.json for ep34 "unit seven" (script.md, writer 2026-11-02).

Run from anywhere: python stories/ep34-unit-seven/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (see its docstring), the effects, the score and the sound.

Places (set.py's metres): the corridor runs along +y (x -1.1 .. 0.9) from the yard door (y -1.2) to the end wall
(y 16). Units 7 to 12 are on the +x side, centres y 3.0, 5.3, 7.6, 9.9, 12.2, 14.5. A character with yaw 0 faces -y,
yaw 90 faces +x, yaw -90 faces -x (out of a unit into the corridor).
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

TEMPO = {"L49": 0.8, "L67": 0.88, "L64": 0.9, "L73": 0.95, "L54": 0.7, "L57": 0.95, "L19": 0.95}
GAPS = {"L12": 0.35, "L37": 0.4, "L54": 0.7, "L69": 0.7, "L60": 0.55, "L67": 0.35, "L68": 0.4, "L58": 0.2}
LOOP = 0.45          # seconds after the last word: the door's thud lands in it
for ln in lines:
    if ln["id"] == "L42":
        ln["gap"] = 0.7                       # the hole before the reveal
    if ln["id"] == "L33":
        ln["gap"] = 0.5                       # the scrape plays alone
    if ln["id"] == "P01":
        ln["pause"] = 0.9
    # slower, softer reads where the script asks (tempo), and a breath after a few lines (gap)
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]
    if ln["id"] in GAPS:
        ln["gap"] = GAPS[ln["id"]]

YC = {7: 3.0, 8: 5.3, 9: 7.6, 10: 9.9, 11: 12.2, 12: 14.5}
KX, KY = 60.0, 0.0     # the kitchen

cast = {
    "me": {"age": "adult", "skin": "#d9a67a", "shirt": "#2f5a3c", "pattern": "solid", "collar": "#294d34",
           "pants": "#33363b", "shoes": "#5b3d27", "sleeves": "long", "hair": "swoop", "hair_c": "#3a2a20",
           "hat": "none", "width": 0.9, "face": {"eyes": "round", "brows": True, "ink": "#1c1214"}},
    "jo": {"age": "adult", "skin": "#e6bd96", "shirt": "#a8603f", "pattern": "solid", "collar": "#92522f",
           "pants": "#232a3a", "shoes": "#ececec", "sleeves": "long", "hair": "long", "hair_c": "#141214",
           "hat": "none", "width": 0.9, "face": {"eyes": "lashes", "brows": True, "ink": "#1c1214"}},
    "deep": {"age": "adult", "skin": "#b9b4a2", "shirt": "#355f96", "pattern": "solid", "collar": "#355f96",
             "pants": "#355f96", "shoes": "#8a6f52", "sleeves": "long", "hair": "none", "hair_c": "#8a6f52",
             "hat": "ballcap", "hat_c": "#54432f", "width": 0.7,
             "face": {"eyes": "hollow", "brows": False, "ink": "#0b0b0d", "pupil": "#08080a", "mouth": "line",
                      "glow": "#eaf1ff"}},
}


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return c([0, loc, tgt, lens])


def move(a, b, lens_a, lens_b=None):
    return c([0, a[0], a[1], lens_a], [1, b[0], b[1], lens_b or lens_a])


def yaw_to(a, b):
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


# ---------------------------------------------------------------------------------------------------- cameras
LONG_LENS = lambda y, x=0.3: still([-0.3, -0.8, 1.5], [x, y, 1.25], 55)
AISLE_CAM = still([-1.0, 3.0, 1.45], [2.5, 3.0, 1.3], 24)          # straight down unit seven's aisle from the corridor
FACE_SIDE = lambda k: still([-0.7, YC[k] - 0.1, 1.55], [1.2, YC[k], 1.5], 36)
SIT = (2.3, 2.25)
SIT_Z = 0.46
KEYCAM = still([1.62, 2.14, 1.6], [1.62, 2.18, 1.2], 28)

SHOTS = [
    (0, "L01 low in the corridor: me walking toward the lamp-lit open door seven, round-scribbled boxes inside it",
     move(([-0.95, 1.0, 1.4], [0.6, 3.6, 1.1]), ([-0.95, 1.2, 1.4], [0.6, 3.6, 1.1]), 18, 18)),
    ("L02", "outside at dusk: the low block, the yard, the sodium lamp",
     move(([-8.5, -17.0, 1.7], [0.2, -1.5, 1.4]), ([-7.5, -16.2, 1.7], [0.2, -1.5, 1.4]), 22)),
    ("L03", "memory: unit seven half full, me at the door, Jo smiling", still([3.95, 2.95, 1.3], [1.0, 3.0, 1.15], 22)),
    ("L04", "Jo at the back of the aisle with a box, me at the front", AISLE_CAM),
    ("L05", "the yard by day: Jo walking to her car, me at the yard door", still([-4.2, -8.0, 1.5], [0.8, -4.5, 1.0], 24)),
    ("L06", "the corridor at night, me at door seven", still([-0.45, -1.0, 1.5], [0.6, 3.0, 1.3], 26)),
    ("L07", "inside seven: the stacks and the aisle, the lamp on the floor", still([0.95, 3.0, 1.15], [3.0, 3.0, 0.85], 22)),
    ("L08", "the two box faces, round on the right, zigzag on the left", still([-1.0, 3.0, 0.85], [1.45, 3.0, -0.25], 14)),
    ("L09", "me on the round stack looking at the jagged one", still([0.95, 3.45, 1.65], [2.3, 2.4, 1.3], 18)),
    ("L10", "knee height on the frame: the two strokes, the padlock", still([1.0, 3.05, 0.5], [1.0, 2.04, 0.5], 48)),
    ("L11+0.3", "top-down on the box top: the ring and two keys", KEYCAM),
    ("L12", "my face in the lamp's light", still([1.3, 3.35, 2.0], [2.3, 2.25, 2.02], 26)),
    ("L13", "the round button, its green ring", still([0.3, 1.25, 1.3], [-1.1, 0.55, 0.98], 35)),
    ("L14", "the corridor from the entrance, lit, empty", still([-0.1, -0.9, 1.5], [-0.1, 10.0, 1.2], 24)),
    ("L15", "the lights click off: my phone's glow, the green ring ahead",
     move(([-0.15, 7.4, 1.5], [-0.4, 0.5, 1.25]), ([-0.15, 6.6, 1.5], [-0.4, 0.5, 1.25]), 24)),
    ("L16", "long lens: unit eleven's door is up, a dark opening near centre", still([-0.8, 6.0, 1.4], [0.9, 12.2, 1.15], 38)),
    ("L17", "closer: the Deep One front-on in unit eleven's doorway", FACE_SIDE(11)),
    ("L18", "mid shot of its front, the face plain", still([-0.5, 12.15, 1.5], [1.2, 12.2, 1.4], 44)),
    ("L19", "me at my door, a small nod", still([-0.1, 6.3, 1.5], [0.0, 3.3, 1.35], 42)),
    ("L19.2", "reverse: it hasn't changed", still([-0.2, 3.7, 1.5], [0.7, 12.2, 1.4], 70)),
    ("L20", "over its shoulder: me small at door seven, locking up",
     still([0.55, 13.2, 1.45], [-0.1, 3.0, 1.15], 40)),
    ("L21", "long lens: unit ten's door is up", LONG_LENS(10.0)),
    ("L22", "front-on, unit ten", FACE_SIDE(10)),
    ("L23", "me walking down the corridor with the torch", still([-0.1, -0.9, 1.5], [-0.2, 7.0, 1.2], 30)),
    ("L24", "from two metres off: its face and the start of its flank", still([0.2, 7.95, 1.5], [1.2, 9.9, 1.3], 30)),
    ("L25", "low side angle: the flank runs back the whole depth in a cold rim",
     move(([0.55, 9.2, 0.4], [3.6, 9.55, 1.05]), ([0.6, 9.18, 0.36], [3.6, 9.5, 1.05]), 18)),
    ("L26", "close on the ribbed flank and the grime", still([2.2, 10.84, 0.78], [2.0, 10.38, 0.78], 17)),
    ("L27", "front-on again, from beside it: the face to the corridor", still([-0.3, 9.55, 1.55], [1.1, 9.9, 1.55], 42)),
    ("L28", "long lens: unit nine's door is up", LONG_LENS(7.6)),
    ("L29", "closer: the body side-on, the head turned square round to me, both eyes on the camera", still([-0.9, 3.6, 1.55], [1.2, 7.9, 1.55], 70)),
    ("L30", "the hasp, door seven already down", still([-0.1, 3.5, 0.45], [0.9, 3.0, 0.15], 30)),
    ("L31", "the corridor, lit, door eight next to mine", still([-0.35, 0.8, 1.5], [0.9, 5.0, 1.25], 28)),
    ("L32", "door eight's foot, no lock", still([-0.1, 5.7, 0.5], [0.9, 5.3, 0.22], 32)),
    ("L33", "inside seven: me on the round stack, worried", still([1.05, 3.05, 1.75], [2.3, 2.35, 2.0], 26)),
    ("L34", "the shared wall, lamp-lit", still([2.0, 3.1, 1.25], [3.0, 3.98, 1.2], 28)),
    ("L35", "a slow pan along the wall, front to back",
     move(([1.2, 3.1, 1.3], [1.7, 3.98, 1.25]), ([3.4, 3.1, 1.3], [3.9, 3.98, 1.25]), 28)),
    ("L36", "my face, scared, eyes following", still([2.3, 3.35, 2.0], [2.3, 2.25, 2.02], 30)),
    ("L37", "door seven shut from the corridor", still([-0.35, 1.2, 1.5], [0.9, 3.6, 1.25], 26)),
    ("L38", "the whole corridor, every door down", still([-0.1, -0.9, 1.4], [-0.1, 12.0, 1.3], 20)),
    ("L39", "me on the round stack, the lamp on the floor", still([1.0, 3.4, 1.05], [2.2, 2.3, 1.2], 24)),
    ("L40", "the lights beyond my door ramp down", still([3.3, 3.1, 1.6], [0.9, 2.9, 1.3], 26)),
    ("L41", "me walking up the low-lit corridor to the button, my back to seven",
     still([0.0, 3.9, 1.55], [-0.6, 0.6, 1.2], 26)),
    ("L42", "me at the button, looking back over my shoulder, worried", still([-0.2, 1.95, 1.58], [-0.6, 0.62, 1.52], 40)),
    ("L43", "the hit: it is in my unit, its face lit from below", still([-0.95, 0.1, 1.2], [1.15, 3.0, 1.45], 62)),
    ("L44", "its face right at my open door", still([-0.3, 3.45, 1.58], [1.0, 3.0, 1.58], 44)),
    ("L45", "low from the doorway's edge: the cold-rimmed flank running back to the wall",
     still([0.45, 2.22, 0.42], [3.4, 2.7, 1.05], 18)),
    ("L46", "the lamp beside its boot", still([0.6, 2.05, 0.5], [1.2, 2.6, 0.2], 28)),
    ("L47", "my face, terrified, then my eyes drop", still([0.45, 2.55, 1.58], [-0.2, 1.4, 1.52], 34)),
    ("L48", "down the aisle line: its head in profile, one eye, facing the left stack", still([-0.1, 3.0, 1.5], [2.5, 3.0, 1.5], 30)),
    ("L49", "hard cut, same framing: the head in profile facing the right stack", still([-0.1, 3.0, 1.5], [2.5, 3.0, 1.5], 30)),
    ("L50", "the jagged boxes beside its flank", still([0.1, 3.4, 1.1], [1.5, 3.8, 0.85], 30)),
    ("L51", "the round boxes beside its flank, the lamp at the foot", still([0.1, 2.6, 1.1], [1.5, 2.3, 0.8], 30)),
    ("L52", "memory: a round scribble on a fresh box, the kitchen table",
     still([KX + 2.0, -2.0, 1.55], [KX - 0.2, 0.1, 1.15], 30)),
    ("L53", "my face, sad", still([0.45, 2.55, 1.58], [-0.2, 1.4, 1.52], 34)),
    ("L54", "close on the round stack and my lamp, its flank at the left edge, head still turned to the stack",
     still([0.15, 2.85, 1.0], [1.5, 2.3, 0.8], 30)),
    ("L55", "that night: the ring with one key, the second beside it",
     still([KX - 0.25, 0.12, 1.42], [KX - 0.22, 0.22, 0.775], 40)),
    ("L56", "me with my phone to my ear by the bright window", still([KX + 0.45, -0.1, 1.62], [KX + 1.0, 2.0, 1.5], 40)),
    ("L57", "a hold on my face, a small breath out", still([KX + 0.75, 0.55, 1.62], [KX + 1.0, 2.0, 1.55], 46)),
    ("L58", "the yard in evening sun: Jo's car pulling in", still([-3.0, -10.5, 1.3], [1.0, -4.5, 1.2], 22)),
    ("L59", "Jo and me side by side as the door rises", still([-0.6, 0.0, 1.5], [0.3, 3.0, 1.35], 32)),
    ("L60", "straight down the aisle in daylight: the stacks and an empty aisle", AISLE_CAM),
    ("L61", "Jo and me carrying her half out, walking toward the sun", still([-0.3, -0.9, 1.45], [0.0, 4.0, 1.2], 28)),
    ("L62", "Jo in the aisle with a round one, eyebrows up", still([0.6, 3.0, 1.55], [2.0, 3.0, 1.5], 34)),
    ("L63", "Jo: \"That one's yours, obviously\"", still([0.6, 3.0, 1.55], [2.0, 3.0, 1.5], 34)),
    ("L63.3", "and me, a small laugh", still([3.7, 3.0, 1.55], [1.4, 3.0, 1.5], 36)),
    ("L64", "the key-return slot, sunlight across it", still([0.1, -0.95, 1.45], [-1.1, -0.1, 1.25], 34)),
    ("P01", "close on the slot", still([0.2, -0.3, 1.32], [-1.1, -0.3, 1.28], 45)),
    ("L65", "her car going out of the gate in the low sun, me watching", still([-4.0, -4.5, 1.4], [5.5, -8.5, 1.0], 26)),
    ("L66", "me carrying round-scribbled boxes out into the sunny yard", still([-0.1, -7.0, 1.4], [-0.1, 0.0, 1.25], 30)),
    ("L67", "one small box on the bare floor of seven, sun across it", still([1.0, 3.6, 0.9], [2.0, 3.0, 0.15], 28)),
    ("L68", "straight down the bare unit to the back wall", AISLE_CAM),
    ("L69", "the same view, a little wider: a bar of sun on the floor outside",
     still([-1.0, 2.4, 1.5], [2.5, 3.1, 0.9], 20)),
    ("L70", "me in the doorway with the small box", still([-0.9, 3.0, 1.55], [1.2, 3.0, 1.45], 38)),
    ("L71", "the blue door rolling down, me beside it with the box", still([-0.9, 1.3, 1.5], [0.6, 3.4, 1.15], 26)),
    ("L71+0.7", "low on the door coming down over the empty floor", still([-0.5, 2.1, 0.22], [0.9, 3.0, 0.3], 20)),
    ("L73", "the corridor from the entrance, sunny: me walking toward the camera, the door landing behind",
     still([-0.3, -1.0, 1.45], [0.25, 5.0, 1.15], 21)),
]

shots = []
for i, (at, what, cam) in enumerate(SHOTS):
    s = {"id": f"S{i + 1:02d}", "cam": cam, "hand": 0.006, "step": 1 if at in ("L15", "L40", "L41", "L42", "L43") else 2,
         "what": what}
    if i:
        s["at"] = at
    shots.append(s)

# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "sit": False}
acting = {"me": [], "jo": [], "deep": []}


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


CARRY = {"arms": [80, 80], "side": [-6, -6]}
SITTING = {"sit": True, "arms": [10, 10], "side": [-8, -8]}

# me
put("me", 0, [-0.5, 2.4], yaw=-15, expr="neutral")
walk("me", "L01>", [-0.55, 1.9])
hide("me", "L02")
put("me", "L03", [1.2, 2.5], yaw=90, expr="soft")
put("me", "L04", [1.7, 3.3], yaw=90, expr="neutral", arms=[20, 20])
put("me", "L05", [-0.45, -1.75], yaw=0, expr="neutral")
put("me", "L06", [0.45, 2.7], yaw=90, expr="worried")
hide("me", "L07")
put("me", "L09", [SIT[0], SIT[1], SIT_Z], yaw=180, expr="worried", **SITTING)
put("me", "L12", [SIT[0], SIT[1], SIT_Z], yaw=180, expr="worried", **SITTING)
hide("me", "L13")
put("me", "L15", [0.15, 3.3], yaw=180, expr="neutral")
walk("me", "L15.2", [-0.1, 2.0])
walk("me", "L15.3+0.1", [-0.5, 0.85])
hide("me", "L16")
put("me", "L19", [-0.1, 3.4], yaw=180, expr="neutral")
key("me", "L19.1", head=[0, 10], blend=0.15)
key("me", "L19.1+0.35", head=[0, -2], blend=0.2)
put("me", "L19.2", [-0.1, 3.5], yaw=180)
put("me", "L20", [0.45, 3.05], yaw=90, expr="neutral")
walk("me", "L20.2+0.2", [0.0, 2.2], yaw=0, keep_yaw=False)
walk("me", "L20.3+0.3", [-0.1, 0.2])
hide("me", "L21")
put("me", "L23", [-0.1, 2.0], yaw=180)
walk("me", "L23+1.9", [-0.3, 6.4])
put("me", "L24", [-0.45, 7.2], yaw=yaw_to([-0.45, 7.2], [1.2, 9.9]), expr="worried")
put("me", "L25", [0.4, 8.7], yaw=yaw_to([0.4, 8.7], [3.9, 9.4]), expr="worried")
put("me", "L26", [0.5, 10.75], yaw=yaw_to([0.5, 10.75], [2.3, 10.4]), expr="worried")
put("me", "L27", [-0.6, 8.4], yaw=yaw_to([-0.6, 8.4], [1.1, 9.9]), expr="worried")
hide("me", "L28")
put("me", "L33", [SIT[0], SIT[1], SIT_Z], yaw=180, expr="worried", **SITTING)
key("me", "L36", expr="scared", look=[0.9, 0.0], blend=0.1)
hide("me", "L37")
put("me", "L39", [SIT[0], SIT[1], SIT_Z], yaw=180, expr="neutral", **SITTING)
put("me", "L41", [0.5, 3.0], yaw=180)
walk("me", "L41+0.2", [0.5, 2.5], yaw=180)
walk("me", "L41.2+0.5", [-0.6, 0.85])
put("me", "L42", [-0.6, 0.62], yaw=180, expr="worried")
hide("me", "L43")
put("me", "L47", [-0.2, 1.4], yaw=yaw_to([-0.2, 1.4], [1.0, 3.0]), expr="terrified")
key("me", "L47.3", expr="worried", head=[0, 18], blend=0.3)
hide("me", "L48")
put("me", "L52", [KX - 0.2, -0.25], yaw=180, expr="grin", arms=[55, 0], side=[-10, 0])
put("me", "L53", [-0.2, 1.4], yaw=yaw_to([-0.2, 1.4], [1.0, 3.0]), expr="worried", head=[0, 10])
hide("me", "L54")
put("me", "L56", [KX + 1.0, 2.0], yaw=0, expr="neutral", arms=[165, 0], side=[0, 0], head=[0, 4])
put("me", "L57", [KX + 1.0, 2.0], yaw=0, expr="worried", arms=[165, 0], head=[0, 4])
key("me", "L57.4", expr="soft", blend=0.3)
hide("me", "L58")
put("me", "L59", [0.3, 3.45], yaw=50, expr="soft")
hide("me", "L60")
put("me", "L61", [0.5, 4.0], yaw=0, expr="soft", **CARRY)
walk("me", "L61+0.6", [0.1, 1.8], **CARRY)
walk("me", "L62-0.05", [0.0, 2.2], **CARRY)
hide("me", "L62")
put("me", "L63.3", [1.5, 3.0], yaw=90, expr="soft")
hide("me", "L64")
put("me", "L65", [-0.1, -1.55], yaw=0, expr="soft", head=[0, 0])
put("me", "L66", [-0.1, 0.2], yaw=0, expr="soft", **CARRY)
walk("me", "L66+1.9", [-0.1, -4.2], **CARRY)
hide("me", "L67")
put("me", "L70", [1.25, 3.0], yaw=-90, expr="soft", **CARRY)
put("me", "L71", [0.3, 3.75], yaw=90, expr="soft", **CARRY)
put("me", "L73", [0.25, 3.4], yaw=180, expr="soft", **CARRY)
walk("me", "L73+0.1", [0.0, 0.2], yaw=0)

# Jo
hide("jo", 0)
put("jo", "L03", [1.95, 3.2], yaw=90, expr="soft")
put("jo", "L04", [3.45, 2.75], yaw=-90, expr="soft", **CARRY)
put("jo", "L05", [0.5, -2.0], yaw=0, expr="neutral")
walk("jo", "L05+0.1", [0.5, -2.0], yaw=0)
walk("jo", "L05>", [1.9, -5.0])
hide("jo", "L06")
put("jo", "L59", [0.3, 2.6], yaw=50, expr="soft")
hide("jo", "L60")
put("jo", "L61", [0.5, 2.4], yaw=0, expr="soft", **CARRY)
walk("jo", "L61+0.1", [-0.1, 1.5], **CARRY)
hide("jo", "L61.4")
put("jo", "L62", [2.5, 3.0], yaw=-90, expr="wide", **CARRY)
key("jo", "L63", expr="soft", blend=0.2)
hide("jo", "L63.3")
put("jo", "L64", [-0.55, 0.1], yaw=-54, expr="soft", arms=[78, 0])
hide("jo", "P01")

# the Deep One: found where it stands, never seen moving
hide("deep", 0)
for at, unit, extra in (("L17", 11, {}), ("L22", 10, {}), ("L29", 9, {"head": [99, 0]})):
    # unit nine: the body is turned a little away from the corridor and the head a long way round, so the neck reads
    put("deep", at, [1.2, YC[unit] + (0.3 if unit == 9 else 0.0)], yaw=-115 if unit == 9 else -90, expr="neutral", **extra)
    hide("deep", {"L17": "L21", "L22": "L28", "L29": "L31"}[at])
put("deep", "L43", [1.2, 3.0], yaw=-90, expr="neutral")
key("deep", "L48", head=[-90, 0], blend=0)
key("deep", "L49", head=[90, 0], blend=0)
hide("deep", "L52")
put("deep", "L53", [1.2, 3.0], yaw=-90, head=[90, 0])
hide("deep", "L55")

# ---------------------------------------------------------------------------------------------------- cues
cues = [
    {"at": 0, "name": "time", "set": "open"},
    {"at": "L02", "name": "time", "set": "dusk", "dur": 0.01},
    {"at": "L03", "name": "time", "set": "mem", "dur": 0.01},
    {"at": "L05", "name": "time", "set": "day", "dur": 0.01},
    {"at": "L06", "name": "time", "set": "dusk", "dur": 0.01},
    {"at": "L58", "name": "time", "set": "sun", "dur": 0.01},
    # the corridor timer: slow ramps only (1.2 s down to 12%, 1.0 s up)
    {"at": "L15.1", "name": "corr", "level": 0.12, "dur": 1.2},
    {"at": "L15.3+0.4", "name": "corr", "level": 1.0, "dur": 1.0},
    {"at": "L40.2", "name": "corr", "level": 0.12, "dur": 1.2},
    {"at": "L42+0.3", "name": "corr", "level": 0.22, "dur": 1.0},
    {"at": "L43+0.3", "name": "corr", "level": 0.09, "dur": 2.4},
    {"at": "L55", "name": "corr", "level": 1.0, "dur": 0.01},
    # doors
    {"at": 0, "name": "door", "unit": 7, "open": 1.0},
    {"at": "L16", "name": "door", "unit": 11, "open": 1.0},
    {"at": "L20.2", "name": "door", "unit": 7, "open": 0.0, "dur": 1.4},
    {"at": "L21", "name": "door", "unit": 11, "open": 0.0},
    {"at": "L21", "name": "door", "unit": 10, "open": 1.0},
    {"at": "L28", "name": "door", "unit": 10, "open": 0.0},
    {"at": "L28", "name": "door", "unit": 9, "open": 1.0},
    {"at": "L31", "name": "door", "unit": 9, "open": 0.0},
    {"at": "L33", "name": "door", "unit": 7, "open": 1.0},
    {"at": "L37", "name": "door", "unit": 7, "open": 0.0},
    {"at": "L39", "name": "door", "unit": 7, "open": 1.0},
    {"at": "L55", "name": "door", "unit": 7, "open": 0.0},
    {"at": "L59.3", "name": "door", "unit": 7, "open": 1.0, "dur": 1.4},
    {"at": "L71+0.2", "name": "door", "unit": 7, "open": 0.5, "dur": 2.4},
    {"at": "L73>-2.2", "name": "door", "unit": 7, "open": 0.0, "dur": 2.4},
    # unit seven's stacks (18 each when full)
    {"at": 0, "name": "stacks", "left": 18, "right": 18},
    {"at": "L03", "name": "stacks", "left": 9, "right": 9},
    {"at": "L06", "name": "stacks", "left": 18, "right": 18},
    {"at": "L61", "name": "stacks", "left": 12, "right": 18},
    {"at": "L61.4", "name": "stacks", "left": 6, "right": 18},
    {"at": "L62", "name": "stacks", "left": 3, "right": 18},
    {"at": "L63.3", "name": "stacks", "left": 0, "right": 18},
    {"at": "L66", "name": "stacks", "left": 0, "right": 9},
    {"at": "L67", "name": "stacks", "left": 0, "right": 0},
    # the lamp
    {"at": "L03", "name": "lamp", "on": 0.0},
    {"at": "L06", "name": "lamp", "on": 1.0},
    {"at": "L55", "name": "lamp", "on": 0.0},
    {"at": "L67", "name": "lamp", "on": 1.0},
    # my phone's glow and torch
    {"at": "L15", "name": "phone", "on": 1.0},
    {"at": "L16", "name": "phone", "on": 0.0},
    {"at": "L23", "name": "phone", "on": 1.0},
    {"at": "L23", "name": "torch", "on": 1.0},
    {"at": "L24", "name": "torch", "on": 0.08},
    {"at": "L26", "name": "torch", "on": 0.3},
    {"at": "L27", "name": "torch", "on": 0.4},
    {"at": "L28", "name": "phone", "on": 0.0},
    {"at": "L28", "name": "torch", "on": 0.0},
    {"at": "L41", "name": "phone", "on": 1.0},
    {"at": "L43", "name": "phone", "on": 0.0},
    # boxes in arms
    {"at": "L04", "name": "carry", "who": "jo", "style": "jagged", "on": True},
    {"at": "L05", "name": "carry", "who": "jo", "style": "jagged", "on": False},
    {"at": "L61", "name": "carry", "who": "jo", "style": "jagged", "on": True},
    {"at": "L61", "name": "carry", "who": "me", "style": "jagged", "on": True},
    {"at": "L61.4", "name": "carry", "who": "jo", "style": "jagged", "on": False},
    {"at": "L62", "name": "carry", "who": "me", "style": "jagged", "on": False},
    {"at": "L62", "name": "carry", "who": "jo", "style": "round", "on": True},
    {"at": "L63.3", "name": "carry", "who": "jo", "style": "round", "on": False},
    {"at": "L66", "name": "carry", "who": "me", "style": "round", "on": True},
    {"at": "L67", "name": "carry", "who": "me", "style": "round", "on": False},
    {"at": "L70", "name": "carry", "who": "me", "style": "small", "on": True},
    # the small box on a surface
    {"at": "L52", "name": "small", "on": True, "pos": [KX - 0.2, 0.3, 0.775]},
    {"at": "L53", "name": "small", "on": False},
    {"at": "L67", "name": "small", "on": True, "pos": [2.0, 3.0, 0.0]},
    {"at": "L68", "name": "small", "on": False},
    # the keys
    {"at": "L11", "name": "keys", "mode": "ring2"},
    {"at": "L13", "name": "keys", "mode": "none"},
    {"at": "L55", "name": "keys", "mode": "table"},
    {"at": "L56", "name": "keys", "mode": "none"},
    # the light on the strokes and the padlock
    {"at": "L10", "name": "plant", "on": 1.0},
    {"at": "L11+0.5", "name": "plant", "on": 0.0},
    # my kitchen
    {"at": 0, "name": "kitchen", "set": "night"},
    {"at": "L52", "name": "kitchen", "set": "day"},
    {"at": "L55", "name": "kitchen", "set": "night"},
    {"at": "L56", "name": "kitchen", "set": "day"},
    {"at": "L56", "name": "call", "on": True},
    {"at": "L58", "name": "call", "on": False},
    # Jo's car
    {"at": "L05", "name": "car", "pos": [3.4, -8.6], "yaw": 90},
    {"at": "L06", "name": "car", "pos": [3.4, -8.6], "yaw": 90, "hide": True},
    {"at": "L58", "name": "car", "pos": [10.0, -8.6], "yaw": 90},
    {"at": "L58+0.3", "name": "car", "pos": [3.4, -8.6], "yaw": 90, "dur": 2.2},
    {"at": "L65+0.2", "name": "car", "pos": [20.0, -8.6], "yaw": 90, "dur": 3.5},
    # the scare's light and the head tube
    {"at": "L43", "name": "facelight", "on": 1.0},
    {"at": "L55", "name": "facelight", "on": 0.0},
    {"at": "L29", "name": "headtube", "on": False},
    {"at": "L38", "name": "headtube", "on": True},
    {"at": "L48", "name": "headtube", "on": False},
    {"at": "L24", "name": "rim", "on": 1.0, "pos": [3.9, 9.05, 1.3], "aim": [1.2, 9.4, 1.15]},
    {"at": "L28", "name": "rim", "on": 0.0},
    {"at": "L45", "name": "rim", "on": 1.0, "pos": [2.3, 1.95, 1.4], "aim": [1.2, 2.5, 1.2]},
    {"at": "L46", "name": "rim", "on": 0.0},
    {"at": "L48", "name": "profile", "on": True},
    {"at": "L55", "name": "profile", "on": False},
    {"at": "L45", "name": "stacks", "left": 18, "right": 9},
    {"at": "L46", "name": "stacks", "left": 18, "right": 18},
    {"at": "L64", "name": "slotlight", "on": 1.0},
    {"at": "L65", "name": "slotlight", "on": 0.0},
]

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L15.1", "kind": "click", "db": -14},
    {"at": "L15.3", "kind": "click", "db": -16},
    {"at": "L40.2", "kind": "click", "db": -14},
    {"at": "L41.2", "kind": "click", "db": -16},
    {"at": "L34.1", "kind": "creak", "db": -12, "dur": 2.2},
    {"at": "L43", "kind": "hit", "db": -7},
    {"at": "P01+0.2", "kind": "bell", "db": -16, "dur": 1.5},
    {"at": "L71+0.2", "kind": "rattle", "db": -16, "dur": 1.6},
    {"at": "L73>-2.2", "kind": "rattle", "db": -12, "dur": 2.4},
    {"at": "L73>+0.12", "kind": "thud", "db": -9},
]

story = {
    "slug": "ep34-unit-seven",
    "title": "Every Tuesday at seven, I visit a room",
    "made_for_kids": False,
    "premise": "Every Tuesday at seven, after work, I let myself into a rented storage unit on the edge of town and sit for an hour among boxes I tell myself belong to my ex, Jo. The corridor lights run on a one-minute timer. One Tuesday someone stands in the open doorway of unit eleven. From the front they look ordinary. From the side they run back the whole depth of the unit. Each Tuesday they are one door nearer mine.",
    "twist": "Half the boxes are mine, and I hold both keys. The Deep One in my unit looks from the jagged stack to the round one as if counting, and the count makes me read my own scribbles: every week I have been visiting my own things and calling them hers. When Jo takes her half and I give mine away, the room ends empty.", "twist_old": "Half the boxes are mine. The thing that has come to stand in the aisle is standing exactly where Jo stood the night we packed, because a unit rented by two is counted for two and I have been keeping her place empty. When Jo takes her half and I give mine away, the room is finally empty of anyone's things.",
    "world": "a low self-storage block at the edge of a made-up town: one lit indoor corridor of twelve blue roller doors on a one-minute light timer, a yard door onto asphalt and one sodium lamp",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#6cc3ff",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": LOOP,
    "look": {"fog": "#2a3140", "fog_density": 0.012, "fog_start": 6.0, "sky": "#161d2e", "sky_strength": 0.5,
             "exposure": 0.0},
    "grade": {"shadows": [-0.02, 0.0, 0.05], "highlights": [0.02, 0.01, -0.02], "saturation": 0.95, "contrast": 1.06,
              "vignette": 0.32, "bloom": 0.2, "grain": 0.012},
    "phonemes": {"Jo": "ʤˈO", "Jo's": "ʤˈOz"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 41, "mode": "locrian", "bpm": 62, "seed": 34,
              "sections": [
                  {"at": 0, "voices": ["drone"], "energy": 0.3},
                  {"at": "L13", "voices": ["drone", "pulse"], "energy": 0.32},
                  {"at": "L21", "voices": ["drone", "pad", "pulse"], "energy": 0.42},
                  {"at": "L28", "voices": ["drone", "pad", "pulse"], "energy": 0.52},
                  {"at": "L33", "voices": ["drone", "pad", "pulse"], "energy": 0.6},
                  {"at": "L39", "voices": ["drone", "pad", "pulse"], "energy": 0.7},
                  {"at": "L43", "voices": ["drone", "pad"], "energy": 0.55},
                  {"at": "L55", "voices": ["drone", "pad"], "energy": 0.35},
                  {"at": "L58", "voices": ["pad", "piano"], "energy": 0.35, "mode": "major", "root": 42},
              ]},
    "sound": {"floor": "stone", "steps_db": -22,
              "ambience": [
                  {"kind": "hum", "from": 0, "to": "L15.1", "lufs": -34},
                  {"kind": "hum", "from": "L15.1", "to": "L15.3+0.4", "lufs": -44},
                  {"kind": "hum", "from": "L15.3+0.4", "to": "L40.2", "lufs": -34},
                  {"kind": "hum", "from": "L40.2", "to": "L42+0.3", "lufs": -44},
                  {"kind": "hum", "from": "L42+0.3", "to": "L58", "lufs": -34},
                  {"kind": "hum", "from": "L58", "to": "end", "lufs": -38},
                  {"kind": "wind", "from": "L58", "to": "end", "lufs": -38},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "L42>", "to": "L43", "keep": ["hit"]},
                              {"from": "L33>", "to": "L34", "keep": ["creak"]}]},
}
story.pop("twist_old", None)
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
