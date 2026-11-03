"""Writes ../story.json for ep43 "Days Since You Last LAUGHED" (script.md, reworked 2026-11-03).

Run from anywhere: python stories/ep43-reading-room/generator/make_story.py
The words are in lines.json next to this file (script.md's 44 lines, [caption, spoken] chunks). Everything else is here:
the cast, the shots, the staging, the cues set.py reads, the score and the sound.

Places: every scene is built in its own patch of the Blender world (SCN gives each patch's origin), so a shot's camera
and a character's place are written in the scene's own metres and `W()` moves them. A character facing -y has yaw 0,
facing +x yaw 90, facing +y 180, facing -x -90. The reading room is round (radius 8.6, centre 0,0): the arched window is
in its west wall, the stacks along the east wall. Tam and I sit on the south side of the window table (facing +y), the
Negative's chair is across from Tam. Only 0, 1, 2 and 4 ever show as digits.
"""
import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

SCN = {"room": (0, 0), "door": (500, 0), "street": (700, 0)}
PARK = [3000.0, 3000.0, 0.0]


def W(scene, p):
    o = SCN[scene]
    return [round(p[0] + o[0], 3), round(p[1] + o[1], 3), round(p[2], 3) if len(p) > 2 else 0.0]


# ---------------------------------------------------------------------------------------------------- the cast
def person(shirt, pants, skin, hair="cap", hair_c="#2a1d15", shoes="#2a2420", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": shoes,
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "face": {"eyes": "round", "brows": True, "ink": "#1c1416"}}
    d.update(kw)
    return d


cast = {
    "me": person("#7a1f2e", "#2b3550", "#e6b18c", "cap", "#121216", "#1c1c24", pattern="knit", pattern_c="#661825"),
    "tam": person("#b9a98a", "#3a3f4c", "#efc9a5", "spiky", "#3a2616", "#d8d4cc", extras=["glasses", "hooddown"],
                  extra_c="#141414", face={"eyes": "tired", "brows": True, "ink": "#1c1416", "bags": True}),
    # the Negative: skin near-black, white strokes; its mouth is a story-local decal (set.py), so the face has none
    "neg": person("#36755f", "#d4caaf", "#15181c", "cap", "#7c8088", "#f2f2f2", pattern="knit", pattern_c="#2c6551",
                  face={"eyes": "none", "brows": False, "ink": "#f2f2f2", "mouth": "none"}),
    "woman": person("#2a8a8a", "#2a2f3a", "#d9a47e", "bun", "#4a2a1a", extras=["coat"], zip_c="#1d6666"),
    "man": person("#6b4a2e", "#33302c", "#c89270", "none", hat="ballcap", hat_c="#5a4a38", extras=["coat"],
                  zip_c="#4a3220"),
    "postman": person("#1d2c52", "#2a2f44", "#e2b490", "none", hat="ballcap", hat_c="#1d2c52", extras=["backpack"],
                      extra_c="#7a5a3a", face={"eyes": "round", "brows": True, "ink": "#1c1416"}),
    "e1": person("#3d6ea6", "#2f3340", "#f1c9a0", "swoop", "#6a3a1e"),
    "e2": person("#8a3b3b", "#2b2b30", "#c58f68", "buzz", "#1c1410"),
    "e3": person("#4b8a5a", "#3a3426", "#f2d0ac", "long", "#d8b060"),
    "e4": person("#c9a23c", "#2a3550", "#9a6a4a", "cap", "#14100c"),
    "e5": person("#7a4a8a", "#2a2a38", "#e2b08a", "bun", "#2a1a12"),
    "e6": person("#d97b4a", "#34404a", "#d8a47c", "spiky", "#5a2a14"),
    "e7": person("#48768a", "#2f2b2b", "#f0c8a2", "swoop", "#1a1410"),
    "e8": person("#a0905c", "#303a34", "#b98262", "cap", "#16110d"),
}
READER_IDS = [f"e{i}" for i in range(1, 9)]
NUM_SLOTS = {"me": 1, "tam": 2, "woman": 1, "man": 1, "postman": 1, **{w: 1 for w in READER_IDS}}

# ---------------------------------------------------------------------------------------------------- the room
SEAT_Z = -0.13
TAM_AT = (-7.0, -0.95)
ME_AT = (-5.6, -0.95)
ACROSS = (-6.7, 0.95)          # the chair across from Tam (a little toward me, so a camera behind Tam sees past him)
MAN_AT = (-3.2, -1.5)
B_NEG = (-3.1, -0.6)
C_NEG = (2.75, -0.5)
D_NEG = (6.35, 0.4)            # east side of table D, facing -x
D_BACK = (4.45, 0.4)           # west side of table D, facing +x (the new one in the sting is seen from behind)
READERS = {   # who: (x, y, yaw)
    "e1": (-1.5, -5.55, 180), "e2": (0.8, -5.55, 180), "e3": (-1.5, -3.65, 0), "e4": (0.8, -3.65, 0),
    "e5": (-1.2, 3.25, 180), "e6": (1.5, 3.25, 180), "e7": (-1.2, 5.15, 0), "e8": (1.5, 5.15, 0),
}
READER_NUM = {"e1": 0, "e2": 1, "e3": 0, "e4": 0, "e5": 1, "e6": 0, "e7": 0, "e8": 1}
TABLES = [   # id, centre, size (x, y), lamps (x, y)
    {"id": "W", "c": [-6.3, 0.0], "size": [2.4, 1.0], "lamps": [[-6.3, -0.25]]},
    {"id": "M", "c": [-3.2, -2.3], "size": [1.2, 0.9], "lamps": [[-3.2, -2.3]]},
    {"id": "B", "c": [-3.9, -0.6], "size": [1.0, 1.0], "lamps": [[-4.2, -0.35]]},
    {"id": "C", "c": [1.8, 0.0], "size": [1.0, 3.2], "lamps": [[1.8, 0.0]]},
    {"id": "D", "c": [5.4, 0.0], "size": [1.0, 3.2], "lamps": [[5.4, 0.4]]},
    {"id": "N", "c": [0.5, -4.6], "size": [6.4, 1.0], "lamps": [[-0.5, -4.6], [2.3, -4.6]]},
    {"id": "P", "c": [0.5, 4.2], "size": [6.0, 1.0], "lamps": [[-0.4, 4.2], [1.6, 4.2]]},
]
CHAIRS = ([[x, y, yaw] for x, y, yaw in READERS.values()] +
          [[*TAM_AT, 180], [*ME_AT, 180], [*ACROSS, -12], [*MAN_AT, 0], [*B_NEG, -90], [*C_NEG, -90], [*D_NEG, -90],
           [*D_BACK, 90]])

READ = dict(sit=True, bend=22, arms=[62, 62], head=[0, 26], expr="neutral")


def seat(x, y, yaw, **kw):
    return {"p": [x, y, SEAT_Z], "yaw": yaw, **{**READ, **kw}}


ROOM_DEF = {w: {**seat(x, y, yaw), "num": READER_NUM[w]} for w, (x, y, yaw) in READERS.items()}
ROOM_DEF["tam"] = {**seat(*TAM_AT, 180, bend=30, head=[0, 22], arms=[58, 50], expr="worried"), "num": 40}
ROOM_DEF["me"] = {**seat(*ME_AT, 180, bend=12, head=[0, 22], expr="grin"), "num": 0}
ROOM_DEF["man"] = {**seat(*MAN_AT, 0, bend=16, head=[0, 24]), "num": 1}
NEG_SIT = dict(sit=True, bend=0, arms=[62, 62], head=[0, 0], expr="blank", blink=False)
ROOM_DEF["neg"] = {"p": [*D_NEG, SEAT_Z], "yaw": -90, **NEG_SIT}
DEFAULTS = {"room": ROOM_DEF}

TAM_WRITE = dict(bend=30, head=[0, 22], arms=[58, 50], expr="worried")
LEAN = dict(bend=40, arms=[84, 84], head=[0, -40], expr="blank")        # the Negative leaning across the table
MESEAT = dict(p=[*ME_AT, SEAT_Z], yaw=180)
STAND = dict(p=[ME_AT[0], -1.55, 0.0], yaw=180, sit=False, bend=0, arms=[0, 0], head=[0, 0])

# ---------------------------------------------------------------------------------------------------- the shots
# Each shot: (ref, scene, cam, stage, options). cam = (loc, target, lens).
SH = []


def S(ref, scene, cam, stage=None, **opt):
    SH.append({"ref": ref, "scene": scene, "cam": cam, "stage": stage or {}, **opt})


WIDE = ([6.0, -5.0, 3.4], [-1.5, 1.0, 2.2], 17)
LOCK = ([-5.4, -0.9, 1.55], [3.0, -0.4, 1.3], 24)              # my eyeline: the man near, the Negative far
GRIN_CAM = ([-5.8, -3.0, 2.4], [-7.45, 0.9, 1.3], 25)       # the Negative's face across from Tam, over Tam's shoulder
D_FRONT = ([4.9, 0.0, 1.45], [6.35, 0.4, 1.3], 60)            # the far table, its face

# 01 the hook: Tam's 40, then the rule in two street spots
S(0, "room", ([-7.0, 1.9, 1.85], [-7.0, -1.0, 1.85], 50),
  {}, stack=False)
S("L02", "room", ([-7.0, 1.6, 2.0], [-7.0, -1.0, 2.1], 70), {})
S("L03", "street", ([0.3, -3.2, 1.7], [0.0, 0.0, 1.8], 30),
  {"woman": {"p": [0.0, 0.0, 0.0], "yaw": 0, "expr": "grin", "num": 1, "head": [0, 6]}}, phone=([0.0, -0.4, 1.25], 0))
S("L03.2", "street", ([0.2, -1.7, 1.95], [0.0, 0.0, 2.0], 50),
  {"woman": {"expr": "laugh", "roll": [("L03.2+0.2", 0)]}}, phone=([0.0, -0.4, 1.25], 0))
S("L04", "door", ([0.1, -4.4, 1.9], [0.0, 0.2, 2.1], 28),
  {"postman": {"p": [0.0, 0.2, 0.2], "yaw": 0, "expr": "angry", "num": 2}}, phone=None)
S("L04.2", "door", ([0.7, -2.7, 0.5], [0.0, 0.2, 2.3], 24), {})
S("L05", "room", ([-7.0, 1.9, 1.9], [-7.0, -0.9, 1.7], 38), {}, stack=True)
S("L05.2", "room", ([-7.0, 1.2, 1.95], [-7.0, -0.5, 1.75], 60), {"tam": {"head": [0, 14], "expr": "worried"}})
S("L06", "room", WIDE, {}, stack=False)
S("L06.2", "room", ([-5.0, -0.1, 1.5], [-6.9, -0.7, 1.15], 38), {})
S("L07", "room", ([-6.2, -1.9, 1.2], [-6.5, 0.0, 6.0], 24), {})
S("L07.2", "room", ([-1.5, -2.3, 1.4], [-1.4, -4.3, 0.95], 40), {}, page=True)
S("L08", "room", ([-6.3, 2.0, 1.7], [-6.3, -1.0, 1.65], 36), {"me": {"expr": "grin"}})
S("L08.2", "room", ([-5.6, 0.9, 1.6], [-5.6, -1.0, 1.55], 45), {"me": {"expr": "smirk", "head": [0, 6]}})
S("L09.1", "room", ([-6.0, 0.6, 1.05], [-6.0, -0.5, 1.05], 85), {}, phone=([-6.0, -0.5, 1.05], 180))
S("L09.2", "room", ([-6.3, 1.5, 1.55], [-6.3, -1.0, 1.5], 40),
  {"tam": {"expr": "blank", "head": [0, 14]}, "me": {"expr": "squeeze", "head": [0, 10]}}, phone=None)
# the drop (P01), then I see it
S("L10", "room", ([-5.6, 0.5, 1.55], [-5.6, -1.0, 1.55], 55), {"me": {"expr": "wide", "head": [0, -2]}})
S("L10.1", "room", ([-5.4, -1.0, 1.55], [6.35, 0.4, 1.2], 40), {})
S("L11", "room", ([3.2, -0.9, 1.6], [6.35, 0.4, 1.3], 40), {})
S("L11.2", "room", ([4.2, -0.2, 1.5], [6.35, 0.4, 1.3], 50), {})
S("L12.2", "room", D_FRONT, {}, hold=True, grin=True)
S("L13", "room", ([7.3, 0.9, 1.7], [-7.0, -0.95, 1.6], 65), {"neg": {"head": [-18, 0]}})
S("L13.2", "room", ([-6.6, 1.4, 1.8], [-7.0, -1.0, 1.7], 45), {"tam": {"head": [0, 24]}, "me": {"expr": "neutral"}})
S("L14", "room", ([-3.2, -3.6, 1.7], [-3.2, -1.5, 1.55], 45),
  {"man": {"expr": "smirk", "tremble": 7}})
S("L15", "room", ([-3.2, -3.2, 1.6], [-3.2, -1.5, 1.55], 55),
  {"man": {"expr": "squeeze", "arms": [150, 150], "head": [0, 6], "tremble": 0}})
S("L16", "room", LOCK, {"neg": {"p": [*D_NEG, SEAT_Z]}, "man": {"expr": "squeeze", "arms": [150, 150]}}, hold=True, lock=True)
S("L16.1", "room", LOCK, {"neg": {"p": [*C_NEG, SEAT_Z]}, "man": {"expr": "neutral", "arms": [62, 62], "head": [0, 24]}},
  hold=True, lock=True, scale=1.1)
S("L16.3", "room", ([-0.6, -0.9, 1.55], [2.75, -0.5, 1.4], 40), {})
S("L17", "room", ([-7.0, 0.7, 1.55], [-7.0, -0.95, 1.45], 55), {}, pencil="L17+0.3")
S("L17.3", "room", ([-7.0, 1.5, 1.9], [-7.0, -1.0, 1.9], 50), {"tam": {"blink": False, "expr": "blank"}})
S("L18", "room", ([-5.6, 1.3, 1.6], [-5.6, -1.0, 1.6], 45),
  {"me": {"expr": "squeeze", "tremble": 4, "head": [0, 12]}})
S("L18.3", "room", ([-5.6, 0.5, 1.6], [-5.6, -1.0, 1.6], 80), {"me": {"expr": "shut", "tremble": 3}})
S("L18.5", "room", LOCK, {"me": {"tremble": 0}}, hold=True, lock=True)
S("L19", "room", LOCK, {"neg": {"p": [*B_NEG, SEAT_Z]}}, hold=True, lock=True, scale=1.2)
S("L19.1", "room", ([-0.6, 0.6, 1.6], [-3.1, -0.6, 1.5], 40), {})
# the closing timer
S("L20", "room", ([-3.0, 3.6, 2.6], [-3.0, 8.0, 2.55], 40), {}, lamps_down="L20", dead_all=True)
S("L20.1", "room", WIDE, {})
S("L21", "room", ([3.0, -0.2, 2.2], [-7.0, 0.0, 2.0], 36), {})
S("L21.2", "room", ([-5.6, -0.4, 1.7], [-7.0, 0.2, 1.6], 30),
  {"neg": {"p": [*ACROSS, SEAT_Z], "yaw": -12, **NEG_SIT}}, scale=1.2)
S("L22", "room", ([-5.6, 0.7, 1.6], [-5.6, -1.0, 1.6], 50), {}, lamps_up="L22")
# the drop (P02), then the reveal
S("L23", "room", ([-3.4, 0.1, 1.55], [-7.0, 0.0, 1.5], 24), {})
S("L24", "room", ([-5.3, -2.3, 1.25], [-6.85, 0.1, 2.0], 30), {"neg": {**LEAN, "yaw": 18}, "tam": {"yaw": 140}}, hold=True, test=True)
S("L24.2", "room", ([-6.1, 1.9, 1.75], [-7.0, -1.0, 1.45], 40), {})
S("L25", "room", ([-5.6, 0.9, 1.6], [-5.6, -1.0, 1.55], 45), {"me": {"expr": "wide", "head": [8, 0]}})
S("L25.1", "room", ([-6.4, -0.1, 1.15], [-7.0, 0.75, 0.95], 45), {})
S("L26", "room", WIDE, {w: {"arms": [140, 140], "expr": "squeeze", "head": [0, 20]} for w in READER_IDS})
S("L26.2", "room", GRIN_CAM, {w: {"arms": list(READ["arms"]), "expr": "neutral", "head": [0, 26]} for w in READER_IDS},
  hold=True, payoff=True)
S("L27", "room", ([-6.8, -2.4, 2.3], [-7.0, 0.9, 1.9], 40), {})
S("L27.2", "room", ([-5.2, -1.6, 1.6], [-7.0, 0.9, 1.5], 50), {})
S("L28", "room", ([-5.0, -0.5, 1.5], [-7.0, -0.8, 1.4], 55), {})
S("L28.2", "room", ([-5.6, 0.4, 2.2], [-7.0, 0.2, 2.0], 30), {})
S("L29", "room", ([-6.9, -2.6, 2.3], [-7.0, -0.95, 2.07], 55), {})
S("L30", "room", ([-5.5, 0.1, 1.2], [-7.0, 0.0, 0.85], 45), {"neg": {"arms": [90, 90], "bend": 44}})
S("L31", "room", ([-5.6, -0.2, 0.95], [-5.6, -0.95, 1.7], 40), {"me": {"expr": "neutral", "head": [0, 0]}})
S("L32", "room", ([2.0, -5.0, 3.2], [-5.0, -0.5, 1.6], 20), {"me": STAND})
S("L32.2", "room", ([-3.0, -6.3, 1.8], [-1.5, -4.0, 1.5], 35),
  {"e3": {"head": [0, -4]}, "e4": {"head": [0, -4]}, "e1": {"head": [0, -4]}, "e2": {"head": [0, -4]}})
S("L33", "room", ([-5.6, 1.2, 1.7], [-5.6, -1.55, 1.75], 40), {"me": {"head": [0, -8], "expr": "wide"}})
# the drop (P03), then the joke
S("L34", "room", ([-5.6, 0.9, 1.75], [-5.6, -1.55, 1.8], 55),
  {"me": {"arms": [0, 170], "head": [0, -22], "expr": "grin", "mouth": [("L34", "L35>", [0.5, 0.5], True)]}})
S("L35", "room", ([-7.0, 1.4, 1.7], [-7.0, -1.0, 1.55], 55),
  {"tam": {"head": [0, -2], "bend": 8, "expr": "smirk", "tremble": 3}, "me": {"arms": [0, 0], "head": [0, 0]}})
S("L35.2", "room", GRIN_CAM, {}, hold=True)
S("L36", "room", ([-7.0, 1.6, 2.9], [-7.0, -1.0, 1.9], 40), {"tam": {"expr": "laugh", "tremble": 5, "bend": 14}})
S("L37", "room", ([-7.0, 1.6, 2.9], [-7.0, -1.0, 1.9], 34), {"tam": {"roll": [("L37", 0)]}}, )
S("L38", "room", ([-3.2, -3.6, 1.7], [-3.2, -1.5, 1.55], 45),
  {"man": {"expr": "laugh", "tremble": 5, "head": [0, -6], "roll": [("L38+0.3", 0)]}})
S("L38.1", "room", WIDE, {w: {"expr": "laugh", "head": [0, -6], "bend": 4, "tremble": 3, "arms": [100, 100]} for w in READER_IDS})
S("L39", "room", ([3.0, -0.2, 2.2], [-7.0, 0.0, 2.0], 36),
  {"e2": {"roll": [("L39", 0)]}, "e5": {"roll": [("L39+0.5", 0)]}, "e8": {"roll": [("L39+1.0", 0)]}})
S("L40", "room", ([-5.4, 1.0, 1.7], [-7.0, 0.95, 1.4], 36), {}, apart=True)
S("L41", "room", ([-5.0, -1.0, 0.6], [-7.0, 0.95, 6.0], 24), {})
S("L41.2", "room", ([-6.3, 1.7, 1.7], [-6.3, -1.0, 1.7], 34),
  {"tam": {"expr": "laugh", "tremble": 4}, "me": {"expr": "laugh", "tremble": 4, "head": [0, 4]}})
S("L42", "room", ([-7.0, 1.2, 1.7], [-7.0, -1.0, 1.6], 55),
  {"tam": {"expr": "laugh", "bend": 6, "head": [10, 8], "tremble": 6, "arms": [150, 58]}})
S("L42.2", "room", ([-5.6, 1.2, 1.7], [-5.6, -1.0, 1.6], 55), {"me": {"expr": "grin", "tremble": 0}})
# next morning
S("L43", "room", ([-6.3, 1.9, 2.0], [-6.3, -1.0, 1.8], 30),
  {"tam": {"expr": "soft", "tremble": 0, "bend": 24, "head": [0, 20], "arms": [58, 50]},
   "me": {"expr": "soft", "tremble": 0}, "neg": {"p": PARK}}, morning=True)
S("L44", "room", ([-1.5, 0.4, 1.5], [4.45, 0.4, 1.35], 40),
  {"neg": {"p": [*D_BACK, SEAT_Z], "yaw": 90, **NEG_SIT}}, scale=1.0, apart_off=True)
S("L44.3", "room", ([1.5, 0.4, 1.8], [4.45, 0.4, 2.3], 45), {})

# ---------------------------------------------------------------------------------------------------- build the shots
# lens: the camera's sensor is 24 mm tall, so a frame at distance d is 24 d / lens high and 13.5 d / lens wide
LENS = {0: 32, "L02": 38, "L04": 30, "L05": 32, "L05.2": 40, "L06.2": 22, "L07": 20, "L07.2": 28, "L08": 17, "L08.2": 38,
        "L09.1": 55, "L09.2": 20, "L10": 30, "L10.1": 40, "L11": 40, "L11.2": 38, "L12.2": 26, "L13": 64, "L13.2": 32,
        "L14": 26, "L15": 30, "L16": 20, "L16.1": 20, "L16.3": 40, "L17": 40, "L17.3": 36, "L18": 32, "L18.3": 40,
        "L18.5": 20, "L19": 20, "L19.1": 34, "L21": 30, "L21.2": 20, "L22": 30, "L23": 22, "L24": 30, "L24.2": 34,
        "L25": 30, "L25.1": 22, "L27": 28, "L27.2": 30, "L28": 36, "L28.2": 24, "L29": 34, "L30": 28, "L31": 28,
        "L32.2": 28, "L33": 28, "L34": 36, "L35": 34, "L35.2": 25, "L36": 24, "L37": 24, "L38": 26, "L39": 30,
        "L40": 24, "L41.2": 20, "L42": 34, "L42.2": 34, "L43": 22, "L44": 32, "L44.3": 30, "L26.2": 25}
for s_ in SH:
    if s_["ref"] in LENS:
        c_ = s_["cam"]
        s_["cam"] = (c_[0], c_[1], LENS[s_["ref"]])
for i, s in enumerate(SH):
    sid = f"S{i + 1:02d}"
    s["id"] = sid
    s["ref_"] = s["ref"] if i else 0

lines2 = []
for ln in lines:
    lines2.append(ln)
    if ln["id"] == "L09":
        lines2.append({"id": "P01", "pause": 0.6, "chunks": []})
    if ln["id"] == "L22":
        lines2.append({"id": "P02", "pause": 0.6, "chunks": []})
    if ln["id"] == "L33":
        lines2.append({"id": "P03", "pause": 0.6, "chunks": []})
lines = lines2
# shots that start after a drop begin on the line after it (P01>, P02>, P03> are the same instant as that line's start)

shots, scene_of = [], {}
for i, s in enumerate(SH):
    cam = s["cam"]
    sc = s["scene"]
    shot = {"id": s["id"], "cam": [[0, W(sc, cam[0]), W(sc, cam[1]), cam[2]]], "step": 2, "hand": 0.004}
    if i:
        shot["at"] = s["ref"]
    shots.append(shot)
    scene_of[s["id"]] = sc

# ---- the staging -> acting and number cues
acting = {w: [] for w in cast}
cues = []
KEYF = {"yaw": 0, "sit": False, "bend": 0, "arms": [0, 0], "head": [0, 0], "expr": "neutral", "look": [0, 0],
        "blink": True, "tremble": 0, "side": [0, 0]}
cur, last_key, last_pos, last_num = {}, {}, {w: PARK for w in cast}, {}
prev_scene = None


def spec_key(sc, sp):
    k = {f: copy.deepcopy(sp.get(f, d)) for f, d in KEYF.items()}
    p = sp.get("p")
    k["pos"] = PARK if (p is None or p[0] > 2000) else W(sc, p)
    return k


for i, s in enumerate(SH):
    sc, ref = s["scene"], s["ref_"]
    if sc != prev_scene:
        cur = {w: copy.deepcopy(DEFAULTS.get(sc, {}).get(w, {"p": None})) for w in cast}
        prev_scene = sc
    for who, sp in s["stage"].items():
        sp = dict(sp)
        base = cur[who] if cur[who].get("p") is not None or "p" in sp else {"p": None}
        if "p" in sp and sp["p"] is not None and sp["p"][0] > 2000:
            base = {"p": None}
        cur[who] = {**base, **sp}
    for who in cast:
        sp = cur[who]
        k = spec_key(sc, sp)
        sig = json.dumps(k, sort_keys=True)
        if sig != last_key.get(who) or sp.get("mouth"):
            frm = last_pos[who]
            if ref != 0:   # at t=0 a PARK pre-key would hide everyone on frame 0
                acting[who].append({"at": ref, "pos": frm})
            acting[who].append({"at": ref, **k, "blend": 0.0})
            last_key[who] = sig
            last_pos[who] = k["pos"]
            for a, b, mm, flap in sp.get("mouth", []):
                acting[who].append({"from": a, "to": b, "mouth": mm, **({"flap": True} if flap else {})})
            cur[who].pop("mouth", None)
        if who in NUM_SLOTS and sp.get("num") is not None and last_num.get(who) != sp["num"]:
            cues.append({"at": ref, "name": "num", "who": who, "v": sp["num"], "snap": True})
            last_num[who] = sp["num"]
        for rf, v in sp.get("roll", []):
            cues.append({"at": rf, "name": "num", "who": who, "v": v})
            last_num[who] = v
            sp["num"] = v
        sp.pop("roll", None)

# ---- per-shot cues
for i, s in enumerate(SH):
    ref = s["ref_"]
    if "stack" in s:
        cues.append({"at": ref, "name": "stack", "on": s["stack"]})
    if "phone" in s:
        ph = s["phone"]
        if ph is None:
            cues.append({"at": ref, "name": "phone", "pos": None})
        else:
            sc = s["scene"]
            cues.append({"at": ref, "name": "phone", "pos": W(sc, ph[0]), "yaw": ph[1]})
    if s.get("page"):
        cues.append({"at": ref, "name": "page", "dur": 0.8})
    if s.get("pencil"):
        cues.append({"at": s["pencil"], "name": "pencil"})
    if s.get("scale"):
        cues.append({"at": ref, "name": "negscale", "v": s["scale"]})
    if s.get("apart_off"):
        cues.append({"at": ref, "name": "apart", "off": True})
    if s.get("apart"):
        cues.append({"at": ref, "name": "apart"})
    if s.get("lamps_down"):
        cues.append({"at": s["lamps_down"], "name": "lamps", "to": 0.15, "dur": 1.5})
        cues.append({"at": s["lamps_down"], "name": "dome", "to": 0.4, "dur": 1.5})     # dusk amber: a dimming, never a blackout
    if s.get("lamps_up"):
        cues.append({"at": s["lamps_up"], "name": "lamps", "to": 1.0, "dur": 1.5})
        cues.append({"at": s["lamps_up"], "name": "dome", "to": 0.35, "dur": 1.5})
    if s.get("morning"):
        cues.append({"at": "L42+0.3", "name": "dome", "to": 1.0, "dur": 2.0})
cues += [{"at": 0, "name": "negscale", "v": 1.0}, {"at": 0, "name": "lamps", "to": 1.0, "dur": 0.1},
         {"at": 0, "name": "dome", "to": 1.0, "dur": 0.1}, {"at": 0, "name": "dead", "tables": ["D"]},
         {"at": "L16.1", "name": "dead", "tables": ["D", "C"]},
         {"at": "L19", "name": "dead", "tables": ["D", "C", "B"]},
         {"at": "L43", "name": "dead", "tables": []},
         {"at": "L44", "name": "dead", "tables": ["D"]}]

# ---- sound (2 to 4 events per 10 s in all; the polish pack adds its own hits and risers)
rolls = [c for c in cues if c["name"] == "num" and not c.get("snap")]
sfx = [{"at": c["at"], "kind": "click", "db": -27} for c in rolls]
sfx += [
    {"at": "L16.1", "kind": "thud", "db": -20, "dur": 0.4, "keep": True},     # the jump cuts: the same low thump twice
    {"at": "L19", "kind": "thud", "db": -20, "dur": 0.4, "keep": True},
    {"at": "L17+0.3", "kind": "click", "db": -22},                           # the pencil on the wood
    {"at": "L15+0.2", "kind": "click", "db": -30},                           # the gulp
    {"at": "L20", "kind": "glide", "db": -16, "dur": 1.5},
    {"at": "L22", "kind": "riser", "db": -22, "dur": 1.5},
    {"at": "L44.3", "kind": "sting", "db": -10, "dur": 2.0, "keep": True},
]

hold_ids = [s["id"] for s in SH if s.get("hold")]
test_id = next(s["id"] for s in SH if s.get("test"))

story = {
    "slug": "ep43-reading-room",
    "title": "Days Since You Last LAUGHED \U0001F92B",
    "made_for_kids": False,
    "premise": "In a town where a number over every head counts the days since you last laughed, my stressed little brother "
               "has crammed for finals in a silent domed reading room until his number says forty, and a person printed "
               "in reverse, with an upside-down grin and no number at all, moves a table nearer each time someone "
               "swallows a laugh.",
    "twist": "The thing is made of every laugh swallowed under the dome, so the silence feeds it and it goes to whoever "
             "holds in the most; one laugh rolls a number back to zero, so I break the room's rule and tell our dumbest "
             "old joke out loud, my brother cracks, the whole room laughs, and it comes apart.",
    "world": "A sunny round public reading room under a glass dome of square panes, with oak tables, green-and-brass lamps "
             "on one closing timer, tall stacks of plain books and a window in the west wall, plus a bright street and a "
             "front doorstep.",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff9ec4",
    "gap": 0.15,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "look": {"fog": "#f3e6c8", "fog_density": 0.004, "fog_start": 16.0, "sky": "#a9c4d8", "exposure": 0.2,
             "flash_safe": True,
             "polish": {"hold": hold_ids, "reveal": ["L23", "L40"], "twist": ["L36"], "sway": []}},
    "grade": {"shadows": [-0.01, 0.0, 0.03], "highlights": [0.03, 0.01, -0.02], "saturation": 1.0, "contrast": 1.06,
              "vignette": 0.3, "bloom": 0.4, "grain": 0.012},
    "phonemes": {"Tam": "tˈæm"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "scene_of": scene_of,
    "scenes": {k: list(v) for k, v in SCN.items()},
    "numbers": NUM_SLOTS,
    "room": {"tables": TABLES, "chairs": CHAIRS, "readers": READER_IDS},
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 50, "mode": "dorian", "bpm": 96, "seed": 43,
              "sections": [
                  {"at": 0, "voices": ["piano", "pad"], "energy": 0.45},
                  {"at": "L10", "voices": ["piano", "pad"], "energy": 0.3},
                  {"at": "L23", "mode": "minor", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L36", "mode": "major", "voices": ["pad", "piano"], "energy": 0.7},
                  {"at": "L43", "mode": "dorian", "voices": ["pad"], "energy": 0.25},
                  {"at": "L44", "voices": ["drone"], "energy": 0.2},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "end", "lufs": -44},
                  {"kind": "hum", "from": "L06", "to": "L43", "lufs": -46},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "P01>", "keep": ["hit"]},
                              {"from": "P02", "to": "P02>", "keep": ["hit"]},
                              {"from": "P03", "to": "P03>", "keep": []}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues); test shot {test_id}")
