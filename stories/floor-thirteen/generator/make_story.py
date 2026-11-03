"""Writes ../story.json for ep14 "In This Building Everything You FORGET Goes To Floor 13" (the redo, r4: script.md,
2026-11-02: everything you forget turns up on thirteen, and the thing forgotten is me).

Run from anywhere: python stories/floor-thirteen/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (lights, doors, indicator, panel, the Attendant's pose and lit buttons, the finger,
the hour on the balcony, props, the cake), the score and the sound.

Places (set.py's metres). The lift car: x -1.05 .. 1.05, y -0.95 (the doors) .. 0.95, floor z = 0, facing the doors
is yaw 0 (-y). The floor panel is on the front wall at x = -0.75 (slot 11 is the 12 button, 12 the 13 button, 21
close); "left" as you face the doors is +x. Past the doors (y < -1.27) one of two places shows: 13's long hall (12 m,
shelves both sides, the armchair at y -6.3, my shelf on the left at y -8.3) or the 12 landing (3.9 m long, our two
doors on the end wall at y = -5.17: mine at x +0.55, Grandad's at x -0.55). The balconies are 30 m east: the divider
wall at x = 30, mine on the west (x < 30), his pots on the east, the outer rail at y = 0; the two-shots are filmed
from the street side (y < 0). The stairwell is 40 m west: steps going down toward -y.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

BX = 30.0
STX = -40.0
DOOR_W = 1.1
LOOP = 0.3            # the last word ends 0.3 s before the cut back to the DING
HOLDS = {"L07": 0.15, "L24": 0.25, "L27": 0.3, "L31": 0.55, "L35": 0.15, "L41": 1.0, "L46": 0.5, "L47": 0.35,
         "L44": 0.1, "L12": 0.2}
for ln in lines:
    if ln["id"] in HOLDS and "pause" not in ln:
        ln["gap"] = HOLDS[ln["id"]]

# ------------------------------------------------------------------------------------------------------ cast
cast = {
    "me": {"age": "adult", "skin": "#c68e66", "shirt": "#6a5c94", "pattern": "solid", "collar": "#6a5c94",
           "pants": "#8f8566", "shoes": "#e0782a", "sleeves": "long", "hair": "swoop", "hair_c": "#141213",
           "hat": "hoodopen", "hat_c": "#6a5c94",
           "face": {"eyes": "round", "brows": True, "ink": "#161012"}},
    # Grandad: grey hair, a knitted cardigan, tired eyes; his glasses are pushed up on his head (set.py)
    "okafor": {"age": "adult", "skin": "#b57e58", "shirt": "#7d6a52", "pattern": "knit", "pattern_c": "#65563f",
               "collar": "#d9d2bd", "pants": "#4a4a50", "shoes": "#2a1c14", "sleeves": "long", "hair": "cap",
               "hair_c": "#b9b9bd", "hat": "none",
               "face": {"eyes": "tired", "brows": True, "ink": "#161012", "bags": True}},
    "abel": {"age": "adult", "skin": "#e2b48c", "shirt": "#3f6a9a", "pattern": "plaid", "pattern_c": "#2f5580",
             "collar": "#3f6a9a", "pants": "#4a4036", "shoes": "#2a2420", "sleeves": "long", "hair": "swoop",
             "hair_c": "#3a2a1c", "hat": "none", "face": {"eyes": "round", "brows": True, "ink": "#161012"}},
    "abel_wife": {"age": "adult", "skin": "#d9a67e", "shirt": "#6f8f7a", "pattern": "solid", "collar": "#6f8f7a",
                  "pants": "#3a3a48", "shoes": "#2a2420", "sleeves": "long", "hair": "long", "hair_c": "#2b1d18",
                  "hat": "none", "face": {"eyes": "lashes", "brows": True, "ink": "#161012"}},
    "ruiz": {"age": "adult", "skin": "#8a5a3c", "shirt": "#7a5a9a", "pattern": "knit", "pattern_c": "#5f4580",
             "collar": "#c9bfa8", "pants": "#4a4a50", "shoes": "#2a1c14", "sleeves": "long", "hair": "bun",
             "hair_c": "#c9c9cc", "hat": "none", "face": {"eyes": "lashes", "brows": True, "ink": "#161012"}},
    "crossword": {"age": "adult", "skin": "#e8c4a0", "shirt": "#5d7a8a", "pattern": "stripes", "pattern_c": "#b8c9d2",
                  "collar": "#5d7a8a", "pants": "#6b5d45", "shoes": "#2a2420", "sleeves": "long", "hair": "buzz",
                  "hair_c": "#4a4038", "hat": "none", "extras": ["glasses"],
                  "face": {"eyes": "round", "brows": True, "ink": "#161012"}},
}


def C(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return C([0, loc, tgt, lens])


def move(a, b, lens_a, lens_b=None):
    return C([0, a[0], a[1], lens_a], [1, b[0], b[1], lens_b or lens_a])


# ----------------------------------------------------------------------------------------------------- cameras
BACK_WIDE = still([0.0, 1.4, 1.45], [0.0, -1.9, 1.5], 22)
BACK_WIDE_B = still([-0.1, 1.05, 1.5], [0.0, -1.9, 1.5], 22)
FIRST = still([0.12, 1.1, 1.6], [0.0, -1.9, 1.55], 22)           # over my shoulder, the doors parting on bright 13
PANEL_LOW = still([-0.74, -0.33, 0.95], [-0.745, -0.94, 0.95], 40)
PANEL_MID = still([-0.70, -0.62, 1.265], [-0.75, -0.94, 1.262], 50)   # the 12 (z 1.226) and the 13 (z 1.292), digits on both
INDICATOR = still([0.0, 0.0, 2.2], [0.0, -0.94, 2.3], 30)
FACE_ME = still([0.32, -0.86, 1.52], [-0.1, 0.6, 1.5], 24)
HELD = still([0.05, 0.95, 1.1], [0.0, -1.9, 1.8], 18)             # the bump frame, locked off
FACE_FEAR = still([0.3, -0.86, 1.2], [-0.35, 0.15, 1.55], 26)
BAL = still([BX, -2.6, 1.6], [BX, 0.75, 1.5], 22)                 # the balconies from the street side

# ------------------------------------------------------------------------------------------------------ shots
SH = []
FK = None


def shot(at, label, cam, step=2, hand=0.01, key=None, tl=None):
    SH.append({"at": at, "label": label, "cam": cam, "step": step, "hand": hand, "key": key, "tl": tl})


def _lamp_placeholder():
    pass


def lamp(cam, aim, w=1.0, up=0.45, c="#e8e4dc", size=0.7, side=0.0):
    """A face key by the camera: where the (first) camera key is, a little up and to the side, aimed at `aim`."""
    x, y, z = cam[0][1]
    return {"at": [round(x + side, 3), round(y, 3), round(z + up, 3)], "aim": list(aim), "w": round(w * 0.55, 3), "c": c,
            "size": size}


# 01 floor thirteen, bright
# the opening (recipe v1, 2026-11-03): the warning over the 13 button lit on its own, pushing in; my face on OUT
PANEL_PUSH = move(([-0.60, -0.15, 1.30], [-0.7075, -0.94, 1.292]), ([-0.65, -0.42, 1.295], [-0.7075, -0.94, 1.292]), 33, 46)
shot(0, "first frame: the floor panel close, the 13 button lit cold on its own, my finger hovering by the 12; pushing in",
     PANEL_PUSH, 1, 0.004)
shot("L01.3-0.2", "my face in the car, looking at the panel: the DING and the hit land on OUT; the walnut wall behind, the cold panel glow on my face", FACE_ME, 2, 0.006,
     {"at": [-0.55, -0.8, 1.55], "aim": [-0.1, 0.6, 1.5], "w": 0.8, "c": "#a9c8ff", "size": 0.6})
shot("L02", "bright 13: the board of keys, a tag on every ring; Mr. Abel lifts his set off it",
     still([-0.8, -3.0, 1.55], [1.2, -3.0, 1.55], 22))
shot("L02b", "the doors part on bright 13: shelves, Mr. Abel turning with his keys, 13 lit above", FIRST, 1, 0.006)
shot("L02b.2", "closer on a shelf: kettle, hat, books, each with a brass tag", still([-0.2, -2.0, 1.4], [-1.4, -4.0, 1.3], 24))
shot("L03", "Mr. Abel with a big iced cake on a stand, guilty", still([0.1, -2.6, 1.4], [0.1, -4.5, 1.15], 18))
shot("L03.3", "the cake close, its brass tag", still([0.1, -3.0, 1.15], [0.1, -4.0, 1.1], 14))
SHOT_LAND = still([0.8, -2.7, 1.6], [-0.4, -5.0, 1.45], 16)
shot("L04", "the Abels' front door: his wife, arms folded", SHOT_LAND)
shot("L04.2", "her face softening at the cake", still([-0.1, -4.0, 1.6], [-0.65, -5.3, 1.55], 20))
shot("L05", "Mrs. Ruiz in the lift, a shrug", FACE_ME, 2, 0.01, lamp(FACE_ME, [-0.1, 0.6, 1.5], 0.9, up=0.3))
shot("L06", "bright 13: a man in an armchair doing the crossword, a tag on the chair arm; he waves",
     still([0.5, -4.4, 1.35], [-0.35, -6.2, 1.15], 20))
# 02 Grandad
shot("L07", "me in the lift, arms folded, pleased with myself", FACE_ME, 2, 0.01, lamp(FACE_ME, [-0.1, 0.6, 1.5], 0.9, up=0.3))
SHOT_HIS_DOOR = still([0.5, -3.5, 1.6], [-0.55, -5.1, 1.5], 18)
shot("L08", "the twelve landing: his door opens, him smiling at me", SHOT_HIS_DOOR)
shot("L09", "morning sun on the balconies: a tomato on his open palm over the low wall", BAL, 2, 0.01,
     lamp(BAL, [BX, 0.75, 1.5], 0.6, up=0.25, c="#ffe3b8", size=1.5))
L10C = still([BX + 0.9, -1.5, 1.6], [BX + 0.4, 0.75, 1.4], 24)
shot("L10", "him patting his pockets", L10C, 2, 0.01, lamp(L10C, [BX + 0.4, 0.75, 1.4], 1.0, up=0.2, c="#ffe3b8", size=1.0))
shot("L11", "the lift: Grandad, the indicator reading 13, his glasses pushed up on his head",
     still([0.3, 0.75, 1.6], [0.0, -0.6, 1.85], 20), 2, 0.01, {"at": [0.9, 0.3, 2.1], "aim": [0.0, -0.3, 1.7], "w": 0.6, "c": "#e8e4dc", "size": 0.7})
shot("L12", "close on his face, glasses on his forehead, puzzled", still([0.3, -0.86, 1.55], [-0.05, 0.45, 1.5], 24), 2, 0.01, {"at": [0.3, -0.86, 1.9], "aim": [-0.05, 0.45, 1.5], "w": 0.5, "c": "#e8e4dc", "size": 0.7})
# 03 Tuesday
shot("L13", "insert: my finger on the 12 button", PANEL_MID)
shot("L14", "insert: the indicator ticking from 12 to 13", INDICATOR)
shot("L14.1+0.35", "my face", FACE_ME, 2, 0.01, lamp(FACE_ME, [-0.1, 0.6, 1.5], 0.9, up=0.3))
shot("P02", "the doors part on thirteen with the sconces off", BACK_WIDE, 1)
shot("L15", "wide from the car through the gap: the shelves in shadow, fog", still([0.0, 0.8, 1.5], [0.0, -8.0, 1.3], 24))
shot("L16", "the dark shelves, the brass tags catching a little light", still([0.0, -0.5, 1.45], [-1.3, -2.9, 1.35], 24))
shot("L17", "the long hall: one small cold light and a dark shape at the far end", still([0.0, 0.5, 1.7], [0.2, -12.0, 1.8], 26))
shot("L17.4", "pointed at me: a slow push on the far light", move(([0.0, 0.5, 1.7], [0.2, -12.0, 1.8]), ([0.0, 0.5, 1.7], [0.2, -12.0, 1.85]), 26, 60))
shot("L18", "the doors close on their own, the light still on me", BACK_WIDE_B, 2, 0.003)
shot("L19", "the twelve landing: Grandad at his door, a tomato on his palm", SHOT_HIS_DOOR)
# 04 Wednesday
shot("L20", "insert: the indicator, 12 to 13", INDICATOR)
shot("P03", "the doors part on dark thirteen", BACK_WIDE, 1)
shot("L21", "through the gap: the shape halfway up the hall, chest up, side-lit", still([0.0, 0.5, 1.6], [0.25, -7.2, 1.7], 34))
shot("L22", "closer: the black jacket, brass buttons and piping, the peaked cap", still([0.0, 0.4, 1.6], [0.25, -7.2, 2.0], 55))
shot("L23", "close on its head: the 3x3 panel", still([0.0, 0.4, 1.7], [0.25, -7.2, 2.1], 95))
shot("L23.3", "the panel: one button lit toward me", still([0.0, 0.4, 1.7], [0.25, -7.2, 2.1], 120))
shot("L24.1", "my face", FACE_ME, 2, 0.01, lamp(FACE_ME, [-0.1, 0.6, 1.5], 0.9, up=0.3))
shot("L25", "the balconies at blue hour: Grandad talking over the wall, me pausing", BAL, 2, 0.01,
     lamp(BAL, [BX, 0.75, 1.5], 1.0, up=0.2, c="#bcd0ff", size=1.6))
L26C = still([BX - 0.9, -1.8, 1.6], [BX - 0.35, 0.75, 1.5], 24)
shot("L26", "me smiling, a little too long", L26C, 2, 0.01, lamp(L26C, [BX - 0.35, 0.75, 1.5], 1.0, up=0.2, c="#bcd0ff", size=1.0))
# 05 Thursday
shot("L27", "insert: the indicator, 12 to 13, no press", INDICATOR)
shot("P04", "the doors part", BACK_WIDE, 1)
shot("L28", "wide from the car: straight in front of the gap, a step from the sill", BACK_WIDE_B)
shot("L29", "a low shot: the sleeves running far down", still([0.25, 0.9, 0.5], [0.0, -1.7, 0.75], 30))
shot("L29.3", "the folded gloves hang below its knees", still([0.05, 0.95, 0.85], [0.0, -1.7, 1.0], 30))
TAGL = {"at": [0.5, -1.0, 0.2], "aim": [0.0, -1.5, 0.3], "w": 0.3, "c": "#bcd0ff", "size": 0.3}
shot("L30", "low close: the brass tag hanging from the gloves", still([0.2, 0.4, 0.5], [0.0, -1.5, 0.3], 90), tl=TAGL)
shot("L31", "insert: the tag, 12 and the one cold stroke, held", still([0.1, 0.3, 0.42], [0.0, -1.48, 0.3], 130), tl=TAGL)
shot("L32", "a fast run of presses on close", PANEL_LOW)
shot("P05", "THE BUMP: the held centre-line frame, locked off: the leaves hit its shoulders", HELD, 1, 0)
shot("L34", "my face lit cold from below by its buttons", FACE_FEAR, 1, 0.004,
     lamp(FACE_FEAR, [-0.35, 0.15, 1.55], 0.5, up=0.1, c="#bcd0ff", side=0.2))
shot("L35", "the doorway is empty across the cut, the doors closing with nothing in the way", BACK_WIDE, 1, 0.003)
SD_CAM = still([-1.0, -1.5, 1.5], [1.2, -3.5, 1.2], 18)
shot("L36", "the twelve landing: the stairwell door swings open and I come through", SD_CAM)
# 06 Grandad's door
shot("L37", "the twelve landing, his door opening, his face", SHOT_HIS_DOOR)
L38C = still([0.0, -4.1, 1.6], [-0.55, -5.1, 1.55], 22)
shot("L38", "close on his face: polite, kind, nothing in it for me", L38C, 2, 0.006, lamp(L38C, [-0.55, -5.1, 1.55], 0.7, up=0.2))
shot("L39", "his mouth moving under the quote", L38C, 2, 0.006, lamp(L38C, [-0.55, -5.1, 1.55], 0.7, up=0.2))
L392 = still([0.2, -4.9, 1.55], [-0.1, -3.6, 1.5], 22)
P06C = still([0.2, -4.9, 1.6], [0.0, -2.0, 1.9], 20)
shot("L39.2", "then my face; near silence: hold, the indicator over the lift doors still lit 13", P06C, 2, 0.003,
     lamp(P06C, [0.0, -3.6, 1.5], 0.7, up=0.2))
shot("L40", "insert: the indicator over the lift doors, reading 13, cold", still([0.0, -3.2, 2.15], [0.0, -1.34, 2.3], 44))
shot("L41", "wide: him in his doorway, me a step back, the space between us", still([0.0, -1.6, 1.5], [0.0, -5.0, 1.35], 20), 2, 0.003)
# 07 Fetching
shot("L42", "the lift doors part on dark thirteen: me stepping out for the first time", still([0.0, 1.2, 1.55], [0.0, -4.0, 1.35], 22), 1)
shot("L43", "side mid-shot: I walk past the Attendant, its one lit button follows me", still([1.0, -3.4, 1.5], [-0.3, -5.8, 1.5], 18))
shot("L43.3", "a shelf with a brass 12 tag", still([-0.1, -7.3, 1.5], [-1.2, -8.3, 1.3], 24))
shot("L44", "the red scarf on the shelf, cold-lit, a brass tag", still([-0.2, -7.6, 1.45], [-1.2, -8.34, 1.2], 26))
shot("L44.3", "my hands lifting it off, on my open palms", still([0.6, -7.3, 1.65], [-0.5, -8.3, 1.3], 18))
shot("L45", "the twelve landing: the scarf lying across his open palms", still([-0.1, -4.0, 1.5], [-0.55, -5.0, 1.25], 20), 2, 0.004)
L46C = still([-0.25, -4.2, 1.6], [-0.55, -5.1, 1.5], 24)
shot("L46", "his face, looking down at it", L46C, 2, 0.004, lamp(L46C, [-0.55, -5.1, 1.5], 0.7, up=0.2, c="#ffe3b8"))
L47C = still([0.55, -4.0, 1.6], [-0.55, -4.75, 1.5], 18)
shot("L47", "his face comes up to mine, knowing me; his hand on my shoulder", L47C, 2, 0.004, lamp(L47C, [-0.55, -4.75, 1.5], 0.7, up=0.2, c="#ffe3b8"))
shot("L48", "the balconies next morning: a tomato on the wall top between us, him puzzled at me again", BAL, 2, 0.01,
     lamp(BAL, [BX, 0.75, 1.5], 0.6, up=0.25, c="#ffe3b8", size=1.5))
shot("L49", "me in the lift, the scarf round my neck", FACE_ME, 2, 0.01, lamp(FACE_ME, [-0.1, 0.6, 1.5], 0.9, up=0.3))
shot("L49.1+0.3", "the indicator ticking from 12 to 13, over my shoulder", still([0.25, 0.9, 1.65], [0.0, -0.9, 1.9], 22), 2, 0.004)
shot("L50", "the doors part on dark thirteen: the Attendant facing the car, my tag hanging from its gloves",
     move(([0.0, 0.6, 1.5], [0.0, -2.6, 1.15]), ([0.0, 0.3, 1.05], [0.0, -2.6, 0.8]), 24, 38), 1, 0.002,
     tl={"at": [0.5, -1.0, 0.5], "aim": [0.0, -2.2, 0.55], "w": 0.9, "c": "#bcd0ff", "size": 0.3})

shots = []
def drift(cam, k, amt=0.06):
    """No shot is static: a single-key camera gets a slow push (every other one also drifts sideways)."""
    if len(cam) != 1:
        return cam
    t, loc, tgt, lens = cam[0]
    loc2 = [loc[i] + amt * (tgt[i] - loc[i]) for i in range(3)]
    if k % 2:
        loc2[0] += 0.06
    return [cam[0], [1, [round(v, 3) for v in loc2], tgt, lens]]


NO_DRIFT = {"P05"}
for k, s in enumerate(SH):
    if s["at"] not in NO_DRIFT:
        s["cam"] = drift(s["cam"], k)
    d = {"id": f"S{k + 1:02d}", "cam": s["cam"], "step": s["step"], "hand": s["hand"]}
    if s.get("key"):
        d["key"] = s["key"]
    if s.get("tl"):
        d["tl"] = s["tl"]
    if k:
        d["at"] = s["at"]
    shots.append(d)

# ------------------------------------------------------------------------------------------------------ acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
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


def talk(who, a, b, amount=0.6):
    acting[who].append({"from": a, "to": b, "mouth": [amount, amount], "flap": True})


for who in cast:
    hide(who, 0)
ME_BACK = [-0.1, 0.6]
BAL_HIM = [BX + 0.5, 0.75]
BAL_ME = [BX - 0.5, 0.75]
HIS_DOOR = [-0.55, -5.1]

# --- 01: bright thirteen
put("me", 0, ME_BACK, yaw=0, expr="worried")
hide("me", "L02")
put("abel", "L02", [0.8, -3.0], yaw=-90, arms=[0, 30], expr="grin")
key("abel", "L02.1", arms=[0, 105], blend=0.35)
put("abel", "L02b", [0.1, -2.0], yaw=180, arms=[0, 100], expr="grin")
put("abel", "L03", [0.1, -4.6], yaw=180, arms=[70, 70], expr="worried")
put("abel", "L04", [0.2, -4.3], yaw=0, arms=[70, 70], expr="worried")
hide("abel", "L04.2")
put("abel_wife", "L04", [-0.65, -5.3], yaw=180, arms=[58, 58], expr="angry")
key("abel_wife", "L04.2", expr="soft", arms=[18, 18], blend=0.6)
hide("abel_wife", "L05")
put("ruiz", "L05", ME_BACK, yaw=0, expr="neutral")
key("ruiz", "L05.2", side=[38, 38], blend=0.15)
key("ruiz", "L05.2+0.55", side=[0, 0], blend=0.3)
hide("ruiz", "L06")
put("crossword", "L06", [-0.35, -6.2, -0.22], yaw=180, arms=[60, 60], expr="smile")
key("crossword", "L06.2+0.2", arms=[60, 155], blend=0.2)
key("crossword", "L06.2+0.5", arms=[60, 120], blend=0.2)
key("crossword", "L06.2+0.8", arms=[60, 155], blend=0.2)
key("crossword", "L06.2+1.1", arms=[60, 60], blend=0.3)
hide("crossword", "L07")
# --- 02: Grandad
put("me", "L07", ME_BACK, yaw=0, arms=[55, 55], expr="smirk")
hide("me", "L08")
put("okafor", "L08", HIS_DOOR, yaw=180, expr="smile")
put("okafor", "L09", BAL_HIM, yaw=-90, arms=[0, 100], head=[70, 0], expr="smile")
put("me", "L09", BAL_ME, yaw=90, head=[-70, 0], expr="smile")
put("okafor", "L10", [BX + 0.45, 0.75], yaw=0, expr="worried")
hide("me", "L10")
for k in range(8):   # patting his pockets
    key("okafor", f"L10+{0.25 * k:.2f}", arms=[14, 0] if k % 2 == 0 else [0, 14], blend=0.1)
put("okafor", "L11", [0.0, -0.3], yaw=0, head=[0, 0], expr="neutral")
put("okafor", "L12", [-0.05, 0.45], yaw=0, expr="worried")
hide("okafor", "L13")
# --- 03: Tuesday (me, small and in the car only for the faces)
put("me", "L14.1", ME_BACK, yaw=0, expr="worried")
hide("me", "P02")
put("okafor", "L19", [-0.55, -5.0], yaw=180, arms=[0, 100], expr="grin")
for k in range(4):   # a wave of the tomato
    key("okafor", f"L19.3+{0.25 * k:.2f}", arms=[0, 90 if k % 2 == 0 else 115], blend=0.12)
hide("okafor", "L20")
# --- 04: Wednesday
put("me", "L24.1", ME_BACK, yaw=0, expr="worried")
hide("me", "L25")
put("okafor", "L25", BAL_HIM, yaw=-90, head=[70, 0], expr="neutral")
talk("okafor", "L25.1", "L25>")
put("me", "L25", BAL_ME, yaw=90, head=[-70, 0], expr="worried")
put("me", "L26", BAL_ME, yaw=90, head=[-70, 0], expr="grin")
hide("okafor", "L27")
hide("me", "L27")
# --- 05: Thursday. The bump: me alone against the right wall
ME_HELD = dict(pos=[-0.58, 0.12], yaw=80, head=[65, 0])
put("me", "P05", ME_HELD["pos"], yaw=ME_HELD["yaw"], head=ME_HELD["head"], expr="terrified")
put("me", "L34", [-0.35, 0.2], yaw=0, head=[0, -6], expr="terrified")
hide("me", "L35")
# the stairs: I run down toward -y; z follows the nosings (rise .13 per .2 run)
put("me", "L36", [2.0, -3.5], yaw=90, expr="worried")
walk("me", "L36+0.1", [1.3, -3.5], keep_yaw=False)
walk("me", "L36+0.6", [0.9, -3.5], keep_yaw=False)
walk("me", "L36>", [0.3, -3.3])
hide("me", "L37")
# --- 06: Grandad's door
put("okafor", "L37", HIS_DOOR, yaw=180, expr="neutral")
key("okafor", "L38", expr="smile")
talk("okafor", "L39.1", "L39>")
put("me", "L39.2", [-0.1, -3.6], yaw=0, head=[0, 0], expr="worried")
put("me", "P06", [0.0, -3.6], yaw=0, head=[0, 0], expr="worried")
put("me", "L41", [0.2, -4.2], yaw=0, expr="worried")
put("okafor", "L41", [-0.55, -5.15], yaw=180, expr="smile")
# --- 07: fetching
hide("okafor", "L42")
put("me", "L42", [0.0, 0.35], yaw=0, expr="worried")
walk("me", "L42>", [0.0, -3.7])
put("me", "L43", [0.1, -3.0], yaw=0, expr="worried")
walk("me", "L43.3", [0.1, -7.2])
hide("me", "L43.3")
put("me", "L44.3", [-0.5, -8.3], yaw=-90, arms=[80, 80], expr="soft")
hide("me", "L45")
put("okafor", "L45", HIS_DOOR, yaw=180, arms=[80, 80], expr="neutral")
key("okafor", "L46", head=[0, 38], expr="soft", blend=0.5)
put("me", "L47", [-0.55, -4.3], yaw=0, expr="soft")
put("okafor", "L47", HIS_DOOR, yaw=180, arms=[0, 78], head=[0, 0], expr="smile")
talk("okafor", "L47.1", "L47>")
put("okafor", "L48", BAL_HIM, yaw=-90, head=[70, 0], expr="worried")
put("me", "L48", BAL_ME, yaw=90, head=[-70, 0], expr="worried")
hide("okafor", "L49")
put("me", "L49", ME_BACK, yaw=0, expr="smile")
put("me", "L49.1", [0.0, -0.1], yaw=0, expr="smile")
hide("me", "L50")

# -------------------------------------------------------------------------------------------------------- cues
cues = []


def cue(at, name, **kw):
    if name in ("lights", "attendant"):
        kw["dur"] = max(kw.get("dur", 0.3), 0.3)   # flash-safe: every light switch ramps over at least 0.3 s
    cues.append({"at": at, "name": name, **kw})


def thirteen(at, dur=1.2, **kw):
    cue(at, "lights", state="thirteen", cast_dark=True, cast_rim=kw.pop("rim", 0.7), fill=kw.pop("fill", 0.0), dur=dur, **kw)


# the lights: bright thirteen is the car's light plus the warm lamps; dark thirteen the dimmed car and the cold lamp
cue(0, "lights", state="on")
cue("L01.3-0.6", "lights", state="bright", dur=0.5)
cue("L04", "lights", state="land", dur=0.3)
cue("L05", "lights", state="on", dur=0.3)
cue("L06", "lights", state="bright", dur=0.3)
cue("L07", "lights", state="on", dur=0.5)
cue("L08", "lights", state="land", dur=0.4)
cue("L09", "lights", state="balc_gold", dur=0.4)
cue("L11", "lights", state="on", dur=0.4)
thirteen("P02", 1.4, fill=1.0)
cue("L19", "lights", state="land", dur=0.5)
cue("L20", "lights", state="on", dur=0.4)
thirteen("P03", 1.4, fill=1.0)
cue("L25", "lights", state="balc_blue", dur=0.4)
cue("L27", "lights", state="on", dur=0.4)
thirteen("P04", 1.4, fill=0.8)
thirteen("P05", 0.5, rim=0.7, fill=0.0)
thirteen("L34", 0.4, rim=0.5, fill=1.1)
cue("L36", "lights", state="land", dur=0.3)
cue(0, "stair_door", open=0.0)
cue("L36-0.1", "stair_door", open=1.0, dur=0.3)
cue("L37", "stair_door", open=0.0, dur=0.1)
cue("L37", "lights", state="land", dur=0.9)
thirteen("L42", 1.0, rim=0.6, fill=1.0, shelf=0.0)
thirteen("L43.3", 0.5, rim=0.6, fill=1.0, shelf=1.0)
cue("L45", "lights", state="land", dur=0.5)
cue("L48", "lights", state="balc_gold", dur=0.5)
cue("L49", "lights", state="on", dur=0.5)
thirteen("L50", 1.0, rim=0.0, fill=0.0)

# the doors: gap in metres between the leaves (1.1 open). The hall's own doors stay open.
cue(0, "doors", gap=0.0, hall=1.0)
cue("L02b", "doors", gap=0.14, hall=1.0)
cue("L02b+0.04", "doors", gap=DOOR_W, hall=1.0, dur=0.55)
cue("L07", "doors", gap=0.0, hall=1.0, dur=0.5)
cue("P02", "doors", gap=DOOR_W, hall=1.0, dur=0.6)
cue("L18.1", "doors", gap=0.0, hall=1.0, dur=1.5)
cue("P03", "doors", gap=DOOR_W, hall=1.0, dur=0.6)
cue("L26", "doors", gap=0.0, hall=1.0, dur=0.3)
cue("P04", "doors", gap=DOOR_W, hall=1.0, dur=0.6)
cue("L32+0.2", "doors", gap=0.8, hall=1.0, dur=1.0)       # the leaves run in over the press inserts
cue("P05", "doors", gap=0.8, hall=1.0, recoil=0.05)         # and stop dead on its shoulders as the THUMP does
cue("L33.3", "doors", gap=0.8, hall=1.0, recoil=0.06)       # BOUNCED
cue("L33.3+0.5", "doors", gap=DOOR_W, hall=1.0, dur=0.7)   # the leaves roll back
cue("L35", "doors", gap=DOOR_W, hall=1.0)
cue("L35+0.2", "doors", gap=0.0, hall=1.0, dur=1.4)
cue("L42", "doors", gap=DOOR_W, hall=1.0, dur=0.7)
cue("L45", "doors", gap=0.0, hall=1.0, dur=0.3)
cue("L50", "doors", gap=DOOR_W, hall=1.0, dur=0.7)

# the landing's two front doors
cue(0, "land_doors", me=0.0, him=0.0)
cue("L04", "land_doors", me=0.0, him=1.0, dur=0.1)
cue("L05", "land_doors", me=0.0, him=0.0, dur=0.1)
cue("L08", "land_doors", me=0.0, him=0.0, dur=0.1)
cue("L08.1", "land_doors", me=0.0, him=1.0, dur=0.7)
cue("L19", "land_doors", me=0.0, him=1.0, dur=0.1)
cue("L20", "land_doors", me=0.0, him=0.0, dur=0.1)
cue("L37", "land_doors", me=0.0, him=0.0, dur=0.1)
cue("L37.1", "land_doors", me=0.0, him=1.0, dur=0.6)
cue("L45", "land_doors", me=0.0, him=1.0, dur=0.1)

# the floor indicator
cue(0, "indicator", floor="12", arrow="up")
cue("L01.1", "indicator", floor="13", arrow=None)
cue("L07", "indicator", floor="12", arrow=None)
cue("L11", "indicator", floor="13", arrow=None)
cue("L13", "indicator", floor="12", arrow=None)
cue("L14", "indicator", floor="12", arrow="up")
cue("L14+0.55", "indicator", floor="13", arrow=None)
cue("L20", "indicator", floor="12", arrow="up")
cue("L20+0.55", "indicator", floor="13", arrow=None)
cue("L27", "indicator", floor="12", arrow="up")
cue("L27+0.45", "indicator", floor="13", arrow=None)
cue("L49", "indicator", floor="12", arrow=None)
cue("L49.1+0.3", "indicator", floor="12", arrow="up")
cue("L49.1+0.75", "indicator", floor="13", arrow=None)

# the floor panel's lit buttons (11 is the 12, 12 the 13, 21 close)
cue(0, "panel", lit=[12])                       # the 13 button, lit on its own: the opening's warned-of thing
cue("L02", "panel", lit=[])
cue("L13+0.25", "panel", lit=[11])
cue("L13+0.7", "panel", lit=[11, 12])           # Tuesday: the 13 lights up by itself as my finger lifts (the plant)
cue("L14-0.25", "panel", lit=[])
for k in range(9):
    cue(f"L32+{0.05 + 0.18 * k:.2f}", "panel", lit=[21])
    cue(f"L32+{0.12 + 0.18 * k:.2f}", "panel", lit=[])

# my finger (press goes 0 to 1 and back)
cue(0, "finger", on=True, button=11, press=0.0)   # hovering by the 12: I didn't press the 13
cue("L01.3", "finger", on=False)
cue("L13", "finger", on=True, button=11, press=0.0)
cue("L13+0.25", "finger", on=True, button=11, press=1.0, dur=0.1)
cue("L13+0.7", "finger", on=True, button=11, press=0.0, dur=0.1)
cue("L14", "finger", on=False)
cue("L32", "finger", on=True, button=21, press=0.0)
for k in range(9):
    cue(f"L32+{0.05 + 0.18 * k:.2f}", "finger", on=True, button=21, press=1.0, dur=0.05)
    cue(f"L32+{0.12 + 0.18 * k:.2f}", "finger", on=True, button=21, press=0.0, dur=0.05)
cue("P05", "finger", on=False)

# the Attendant: where it stands (found there when a shot starts, never seen moving), which buttons are lit
cue(0, "attendant", hidden=True)
cue("P02", "attendant", pose="far", lit=[4], glow=1.6, eye=1.4, side=1.0, rim=1.0, wash=0.0, key=0.0)
cue("L19", "attendant", hidden=True)
cue("P03", "attendant", pose="half", lit=[4], glow=1.6, eye=1.4, side=1.0, rim=1.0, wash=0.0, key=0.0)
cue("L25", "attendant", hidden=True)
cue("P04", "attendant", pose="centre", lit=[4], glow=1.5, eye=1.3, key=0.3)
BUMP = dict(pose="bump", bend=44, head=[-16, 0, 0], glow=0.75, eye=1.9, peak=0.0, key=0.3, wash=0.55)
cue("P05", "attendant", lit="all", dur=0.5, **BUMP)
cue("L35", "attendant", hidden=True)
cue("L43", "attendant", pose="shelf", lit=[5], glow=1.6, eye=1.4, side=1.0, rim=1.0, wash=0.0, key=0.0)
cue("L43.1+0.3", "attendant", pose="shelf", lit=[4], glow=1.6, eye=1.4, side=1.0, rim=1.0, wash=0.0, key=0.0, dur=0.3)
cue("L43.2", "attendant", pose="shelf", lit=[3], glow=1.6, eye=1.4, side=1.0, rim=1.0, wash=0.0, key=0.0, dur=0.3)
cue("L45", "attendant", hidden=True)
cue("L50", "attendant", pose="last", lit=[4], glow=1.5, eye=1.3, side=0.15, rim=0.5, sleeve=0.25, wash=0.7, key=0.4)

# balconies: the hour, the tomatoes on the wall, the props
cue(0, "sky", hour=None)
cue("L09", "sky", hour="gold")
cue("L11", "sky", hour=None)
cue("L25", "sky", hour="blue")
cue("L27", "sky", hour=None)
cue("L48", "sky", hour="gold")
cue("L49", "sky", hour=None)
cue(0, "tomatoes", n=0)
cue("L48", "tomatoes", n=1)
cue("L49", "tomatoes", n=0)
cue(0, "props", keys=True)
cue("L03", "props", keys=False)
cue("L09", "props", tomato=True, keys=False)
cue("L10", "props", tomato=False)
cue("L19", "props", tomato=True)
cue("L20", "props", tomato=False)
cue("L44.3", "props", scarf_me=True, shelf_scarf=False)
cue("L45", "props", scarf_him=True, shelf_scarf=False)
cue("L47", "props", shelf_scarf=False)
cue("L49", "props", scarf_neck=True, shelf_scarf=False)
cue("L50", "props", shelf_scarf=True)
cue(0, "cake", on=False)
cue("L03", "cake", on=True, pos=[0.1, -4.0, 0.98], yaw=0)
cue("L04", "cake", on=True, pos=[0.2, -4.85, 0.98], yaw=0)
cue("L04.2", "cake", on=True, pos=[-0.2, -4.75, 0.98], yaw=0)
cue("L05", "cake", on=False)

# ---------------------------------------------------------------------------------------------------- sound
sfx = []


def sf(at, kind, db, **kw):
    sfx.append({"at": at, "kind": kind, "db": db, **kw})


sf("L01.3>-0.22", "bell", -15)                   # the sound hit on the warning's last word, OUT
sf("L01.3>-0.22", "hit", -9, keep=True)
for at in ("P02", "P03", "P04"):
    sf(at, "bell", -15)
sf("L13+0.25", "click", -12)
for k in range(9):
    sf(f"L32+{0.05 + 0.18 * k:.2f}", "click", -15)
sf("P05", "hit", -6, keep=True)
sf("P05", "thud", -9, keep=True)
sf("L33.3", "thud", -16)
sf("L32+0.2", "whoosh", -26, dur=1.0, keep=True)
sf("L33.3+0.5", "whoosh", -28, dur=0.6)
sf("L18.1", "whoosh", -26, dur=1.4)
sf("L35+0.2", "whoosh", -26, dur=1.2)
sf("L42", "whoosh", -28, dur=0.7)
sf("L50", "whoosh", -28, dur=0.7)
sf("L08.1", "door", -30, dur=0.6)
sf("L37.1", "door", -30, dur=0.6)
sf("L36", "door", -24, dur=0.6)
sf("L31", "sting", -24)
# post sfx (2026-11-03 lift): the doors, the bump and the beats land with recorded effects
sf("L02b", "bell", -20)
sf("L02b", "whoosh", -22, dur=0.8)
sf("L02", "whoosh", -28, dur=0.5)
sf("L03", "thud", -24)
sf("L09", "whoosh", -30, dur=0.6)
sf("P02", "door", -22, dur=1.0)
sf("P03", "door", -22, dur=1.0)
sf("P04", "door", -20, dur=1.0)
sf("L17.4", "whoosh", -28, dur=1.0)
sf("L23.3", "thud", -20)
sf("L28", "thud", -22, keep=True)
sf("L34", "thud", -18)
sf("L41", "thud", -20)
sf("L42", "door", -22, dur=1.0)
sf("L47", "whoosh", -30, dur=0.6)
sf("L50", "door", -20, dur=1.0)

story = {
    "slug": "ep14-floor-thirteen",
    "title": "My 13 Button Lit Up By ITSELF 🔘",
    "made_for_kids": False,
    "fade_in": False,
    "premise": "In an older apartment tower, everything anyone forgets turns up on the thirteenth floor, where residents ride up to fetch it: keys, a forgotten anniversary as a cake, even a first boyfriend doing the crossword. I've never forgotten anything and never been up there. Then the elevator starts going past my floor to a dark thirteen, where something in a black-and-brass elevator attendant's uniform with a panel of elevator buttons for a face is nearer each morning, a brass tag with my apartment number hanging from its folded gloves.",
    "twist": "I was the thing that turned up on thirteen, because Grandad next door had forgotten me. Nothing on thirteen is gone, though, and what you fetch back you remember: I fetch the red scarf he knits me every winter from my shelf up there, put it in his hands, and he says my name. He forgets me most mornings now, so most mornings I go up and fetch myself back.",
    "world": "an older apartment tower in an unnamed city: a walnut-and-brass elevator car, the thirteenth floor as a long umber hall of open shelves of forgotten things with brass tags (warm and busy when people fetch, dark with one cold light when the elevator brings me), a beige twelfth-floor landing with two doors, and two side-by-side concrete balconies with a low wall and Grandad's crowd of terracotta pots.",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffbf3f",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": LOOP,
    "look": {"fog": "#0d1015", "fog_density": 0.02, "fog_start": 1.5, "sky": "#0b0d11", "sky_strength": 1.0,
             "exposure": 1.0, "flash_safe": True,
             "polish": {"quiet": [["L45", "L47"]]}},
    "grade": {"shadows": [-0.02, 0.0, 0.04], "highlights": [0.0, 0.005, 0.01], "saturation": 0.88, "contrast": 1.1,
              "vignette": 0.4, "bloom": 0.22, "grain": 0.014, "red_line": 0.79},
    "phonemes": {"Abel": "ˈAbəl", "Ruiz": "ɹuˈis", "pressed": "pɹˈɛst", "forgotten": "fɚɡˈɑtᵊn"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    # A minor at 100 bpm. The montage is thin and plucky; at the first dark DING the pluck stops and a low drone on A,
    # Phrygian, holds to the end; a warm Dorian pad over it while he holds the scarf, then the drone alone
    "music": {"root": 45, "mode": "minor", "bpm": 100, "seed": 14,
              "sections": [
                  {"at": 0, "voices": ["pulse", "piano"], "energy": 0.32},
                  {"at": "L09", "voices": ["pulse", "piano"], "energy": 0.36},
                  {"at": "P02", "voices": ["drone"], "energy": 0.4, "mode": "phrygian"},
                  {"at": "P04", "voices": ["drone", "pad"], "energy": 0.5, "mode": "phrygian"},
                  {"at": "L36", "voices": ["drone"], "energy": 0.4, "mode": "phrygian"},
                  {"at": "L45", "voices": ["drone", "pad"], "energy": 0.4, "mode": "dorian"},
                  {"at": "L48", "voices": ["drone"], "energy": 0.4, "mode": "phrygian"},
              ]},
    "sound": {"rev": 3, "floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "hum", "from": 0, "to": "L08", "lufs": -40},
                  {"kind": "room", "from": "L08", "to": "L09", "lufs": -40},
                  {"kind": "wind", "from": "L09", "to": "L11", "lufs": -40},
                  {"kind": "hum", "from": "L11", "to": "P02", "lufs": -38},
                  {"kind": "drone", "from": "P02", "to": "L19", "lufs": -38},
                  {"kind": "room", "from": "L19", "to": "L20", "lufs": -40},
                  {"kind": "drone", "from": "L20", "to": "L25", "lufs": -38},
                  {"kind": "wind", "from": "L25", "to": "L27", "lufs": -40},
                  {"kind": "drone", "from": "L27", "to": "L36", "lufs": -38},
                  {"kind": "room", "from": "L36", "to": "L42", "lufs": -40},
                  {"kind": "drone", "from": "L42", "to": "L45", "lufs": -38},
                  {"kind": "room", "from": "L45", "to": "L48", "lufs": -40},
                  {"kind": "wind", "from": "L48", "to": "L49", "lufs": -40},
                  {"kind": "drone", "from": "L49", "to": "end", "lufs": -38},
              ],
              "sfx": sfx,
              # the voice and the hit only for 0.6 s before the bump, then near silence under the stranger's smile
              "music_drops": [{"from": "L32+0.9", "to": "P05", "db": -45.0, "keep": ["hit", "thud", "whoosh"]},
                              {"from": "L39>", "to": "P06>", "db": -45.0}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
