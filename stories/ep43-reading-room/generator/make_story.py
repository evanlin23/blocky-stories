"""Writes ../story.json for ep43 "reading room" (script.md, batch 4).

Run from anywhere: python stories/ep43-reading-room/generator/make_story.py
The words are in lines.json next to this file (script.md's 71 lines plus three silent drop beats). Everything else is
here: the cast, the shots, the staging, the cues set.py reads, the score and the sound.

Places: every scene is built in its own patch of the Blender world (SCN gives each patch's origin), so a shot's camera
and a character's place are written in the scene's own metres and `W()` moves them. Characters and sets that aren't in
the shot's scene are hidden by set.py. A character facing -y has yaw 0, facing +x yaw 90, facing +y 180, facing -x -90.
The reading room is round (radius 8.6, centre 0,0). The arched window is in its west wall (x = -8.5) and the stacks
stand along the east wall.
"""
import copy
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

SCN = {"room": (0, 0), "steps": (200, 0), "party": (300, 0), "station": (400, 0), "door": (500, 0),
       "kitchen": (600, 0), "street": (700, 0), "flat": (800, 0)}
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
    "neg": person("#36755f", "#d4caaf", "#15181c", "cap", "#ececec", "#f2f2f2", pattern="knit", pattern_c="#2c6551",
                  face={"eyes": "negative", "brows": True, "ink": "#f2f2f2", "pupil": "#ffffff", "mouth": "line"}),
    "baker": person("#e8c030", "#4a3f36", "#f0c8a0", "none", hat="beanie", hat_c="#f6f3ea", extras=["apron"],
                    extra_c="#f6f3ea"),
    "woman": person("#2a8a8a", "#2a2f3a", "#d9a47e", "bun", "#4a2a1a", extras=["coat"], zip_c="#1d6666"),
    "man": person("#6b4a2e", "#33302c", "#c89270", "none", hat="ballcap", hat_c="#5a4a38", extras=["coat"],
                  zip_c="#4a3220"),
    "postman": person("#1d2c52", "#2a2f44", "#e2b490", "none", hat="ballcap", hat_c="#1d2c52", extras=["backpack"],
                      extra_c="#7a5a3a"),
    "ossie": person("#d0a030", "#4d4638", "#e8bc98", "none", pattern="knit", pattern_c="#b08a22"),
    "e1": person("#3d6ea6", "#2f3340", "#f1c9a0", "swoop", "#6a3a1e"),
    "e2": person("#8a3b3b", "#2b2b30", "#c58f68", "buzz", "#1c1410"),
    "e3": person("#4b8a5a", "#3a3426", "#f2d0ac", "long", "#d8b060"),
    "e4": person("#c9a23c", "#2a3550", "#9a6a4a", "cap", "#14100c"),
    "e5": person("#7a4a8a", "#2a2a38", "#e2b08a", "bun", "#2a1a12"),
    "e6": person("#d97b4a", "#34404a", "#d8a47c", "spiky", "#5a2a14"),
    "e7": person("#48768a", "#2f2b2b", "#f0c8a2", "swoop", "#1a1410"),
    "e8": person("#a0905c", "#303a34", "#b98262", "cap", "#16110d"),
    "e9": person("#9a4a5e", "#2c3040", "#ecc29c", "long", "#2a1810"),
    "e10": person("#5a6c9a", "#3a3830", "#d4a07a", "buzz", "#322018"),
    "e11": person("#6a8a4a", "#2a2a2e", "#f0cba5", "cap", "#8a5a30"),
    "e12": person("#b0602e", "#30343c", "#c9946c", "swoop", "#201610"),
}
ORDER = list(cast)
NUM_SLOTS = {"me": 2, "tam": 2, "baker": 3, "woman": 1, "man": 2, "postman": 5, "ossie": 1,
             **{f"e{i}": 3 for i in range(1, 13)}}

# ---------------------------------------------------------------------------------------------------- the room
SEAT_Z = -0.13                       # hips on a 0.38 m seat
SOFA_Z = -0.06                       # hips on a 0.45 m sofa
TAM_AT = (-7.0, -0.95)
OLD_AT = (-7.0, 0.95)
B_NEG = (-5.3, -0.95)
C_NEG = (2.75, -0.5)
D_NEG = (6.35, 0.4)
ME_AT = (4.15, -4.6)
STAND_AT = (4.2, -3.65)
READERS = {   # who: (x, y, yaw)
    "e1": (-1.5, -5.55, 180), "e2": (0.8, -5.55, 180), "e3": (-1.5, -3.65, 0), "e4": (0.8, -3.65, 0),
    "e5": (-1.2, 3.25, 180), "e6": (1.5, 3.25, 180), "e7": (-1.2, 5.15, 0), "e8": (1.5, 5.15, 0),
    "e9": (0.85, -0.9, 90), "e10": (0.85, 0.9, 90), "e11": (4.45, -1.4, 90), "e12": (4.45, 1.2, 90),
}
READER_NUM = dict(zip(READERS, [61, 204, 12, 88, 340, 25, 77, 150, 43, 19, 96, 8]))
TABLES = [   # id, centre, size (x, y), lamps (x, y)
    {"id": "W", "c": [-7.0, 0.0], "size": [1.0, 1.0], "lamps": [[-7.0, -0.25]]},
    {"id": "B", "c": [-5.3, 0.0], "size": [1.0, 1.0], "lamps": [[-5.3, 0.2]]},
    {"id": "C", "c": [1.8, 0.0], "size": [1.0, 3.2], "lamps": [[1.8, 0.0]]},
    {"id": "D", "c": [5.4, 0.0], "size": [1.0, 3.2], "lamps": [[5.4, 0.4]]},
    {"id": "N", "c": [0.5, -4.6], "size": [6.4, 1.0], "lamps": [[-0.5, -4.6], [2.3, -4.6]]},
    {"id": "P", "c": [0.5, 4.2], "size": [6.0, 1.0], "lamps": [[-0.4, 4.2], [1.6, 4.2]]},
]
CHAIRS = [[x, y, yaw] for x, y, yaw in READERS.values()] + [[*TAM_AT, 180], [*ME_AT, -90], [*C_NEG, -90],
                                                          [*D_NEG, -90], [*B_NEG, 180], [-5.3, 0.95, 0]]
OLD_CHAIR = [*OLD_AT, 0]

READ = dict(sit=True, bend=22, arms=[62, 62], head=[0, 26], expr="neutral")
LOOK_UP = dict(sit=True, bend=0, arms=[62, 62], head=[0, -4], expr="wide")


def seat(x, y, yaw, **kw):
    return {"p": [x, y, SEAT_Z], "yaw": yaw, **{**READ, **kw}}


ROOM_DEF = {w: {**seat(x, y, yaw), "num": READER_NUM[w]} for w, (x, y, yaw) in READERS.items()}
ROOM_DEF["tam"] = seat(*TAM_AT, 180, bend=30, head=[0, 22], arms=[58, 50], expr="worried")
ROOM_DEF["me"] = seat(*ME_AT, -90, bend=12, head=[0, 22])
NEG_SIT = dict(sit=True, bend=0, arms=[62, 62], head=[0, 0], expr="blank", blink=False)
DEFAULTS = {"room": ROOM_DEF}

# ---------------------------------------------------------------------------------------------------- the shots
# Each shot: (ref, scene, cam, stage, options). cam = (loc, target, lens) or (loc, target, lens, loc2, target2, lens2).
SH = []


def S(ref, scene, cam, stage=None, **opt):
    SH.append({"ref": ref, "scene": scene, "cam": cam, "stage": stage or {}, **opt})


def stp(i, dx=0.0):
    """A standing place on the library steps (step i, dx across)."""
    return [dx, round(1.0 - 0.55 * i - 0.275, 3), round(0.16 * (6 - i), 3)]


STEP_PEOPLE = {   # who: (step, dx, number)
    "e1": (3, -0.72, 41), "e2": (2, 0.0, 212), "e3": (3, 0.72, 18),
    "e4": (1, -2.4, 133), "e5": (2, -1.6, 7), "e6": (2, 1.7, 56), "e7": (1, 2.5, 320), "e8": (4, -2.2, 24),
    "e9": (5, 2.0, 91), "e10": (5, -0.9, 15),
}

# 01 the rule, shown (steps, party, station, door, kitchen)
S(0, "steps", ([0.0, -5.4, 1.85], [0.0, -1.0, 1.85], 31, [0.0, -5.1, 1.85], [0.0, -1.0, 1.85], 31),
  {w: {"p": stp(i, dx), "yaw": 0, "num": n, "numz": (0.4 if w == "e2" else 0.0)} for w, (i, dx, n) in list(STEP_PEOPLE.items())[:3]})
S("L01.2", "steps", ([1.2, -9.5, 3.4], [0.0, 0.0, 1.5], 24, [0.4, -9.0, 3.3], [0.0, 0.0, 1.5], 24),
  {w: {"p": stp(i, dx), "yaw": 0, "num": n} for w, (i, dx, n) in list(STEP_PEOPLE.items())[3:]})
S("L02", "steps", ([1.6, -7.6, 1.5], [0.2, -3.3, 2.0], 32),
  {"baker": {"p": [0.4, -3.3, 0.0], "yaw": 0, "expr": "soft", "num": 900},
   **{w: {"p": PARK} for w in ("e1", "e2", "e3", "e4", "e5", "e7", "e9", "e10")}})
S("L03", "party", ([0.0, -4.0, 1.75], [0.0, 0.0, 2.0], 19),
  {"e1": {"p": [-1.2, 0.3, 0.0], "yaw": 25, "expr": "soft", "num": 14, "roll": [("L03+0.15", 15)]},
   "e4": {"p": [-0.4, -0.2, 0.0], "yaw": 8, "expr": "neutral", "num": 120, "roll": [("L03+0.65", 121)]},
   "e5": {"p": [0.4, 0.3, 0.0], "yaw": -8, "expr": "soft", "num": 87},
   "e6": {"p": [1.2, -0.2, 0.0], "yaw": -25, "expr": "neutral", "num": 63, "roll": [("L03+1.15", 64)]}})
S("L03.2", "party", ([0.4, -1.9, 1.78], [0.4, 0.3, 2.05], 34),
  {"e5": {"expr": "smirk", "roll": [("L03.2+0.35", 88)],
          "mouth": [("L03.2", "L03.2+0.9", [0.5, 0.5], True)]}})
S("L04", "station", ([0.0, -3.4, 1.6], [0.2, 0.9, 1.9], 28),
  {"woman": {"p": [0.2, 2.0, 0.45], "yaw": 0, "num": 0, "walk": ([0.2, 0.2, 0.0], "L05")}})
S("L05", "station", ([0.2, -3.8, 1.7], [-0.4, -0.2, 1.95], 30),
  {"woman": {"p": [0.3, 0.2, 0.0], "yaw": -70},
   "man": {"p": [-1.3, -0.5, 0.0], "yaw": 70, "num": 63, "then": [("L05+0.5", {"head": [0, 18]}, 0.2),
                                                                  ("L05+1.0", {"head": [0, -2]}, 0.3)]}})
S("L05.2", "station", ([0.45, -1.9, 1.75], [0.3, 0.2, 2.0], 36),
  {"woman": {"num": 0, "expr": "neutral", "roll": [("L05.4", 1)], "mouth": [("L05.2", "L05.4", [0.5, 0.5], True)]}})
S("L06", "door", ([0.1, -4.4, 1.9], [0.0, 0.2, 2.1], 28),
  {"postman": {"p": [0.0, 0.2, 0.2], "yaw": 0, "expr": "soft", "num": 48113}})
S("L06.2", "door", ([0.7, -2.7, 0.3], [0.0, 0.2, 2.3], 22), {})
S("L07", "kitchen", ([0.2, -2.9, 1.7], [0.0, 0.5, 1.9], 30),
  {"ossie": {"p": [0.0, 0.9, 0.0], "yaw": 0, "expr": "soft", "arms": [150, 150], "num": 5}})
S("L07.2", "kitchen", ([0.15, -0.95, 0.98], [0.0, 0.55, 1.45], 38), {})
# 02 the exception
S("L08", "street", ([0.4, -2.4, 1.7], [0.0, 0.0, 1.9], 34),
  {"me": {"p": [0.0, 0.0, 0.0], "yaw": 0, "num": 1, "expr": "neutral", "head": [0, 0]}}, phones="head")
S("L08.1", "street", ([-0.5, -6.0, 1.8], [0.2, 0.0, 1.8], 26, [-0.2, -6.0, 1.8], [0.9, 0.0, 1.8], 26),
  {"me": {"p": [-2.6, 0.0, 0.0], "walk": ([2.6, 0.0, 0.0], "L09")}})
S("L09", "street", ([0.3, -1.7, 1.6], [0.0, 0.0, 1.62], 40),
  {"me": {"p": [0.0, 0.0, 0.0], "yaw": 0, "head": [0, 32], "expr": "neutral"}})
S("L10", "street", ([0.45, -1.9, 2.0], [0.0, 0.3, 1.6], 32),
  {"me": {"p": [0.0, 0.0, 0.0], "yaw": 180, "head": [0, 34]}})
S("L11", "flat", ([1.5, 0.6, 1.7], [1.2, -2.0, 1.5], 30),
  {"tam": {"p": [1.2, -1.9, SOFA_Z], "yaw": 180, "sit": True, "bend": 6, "arms": [30, 30], "head": [0, 6],
           "expr": "neutral", "num": 12}})
S("L11.3", "flat", ([1.2, -0.1, 1.5], [1.2, -1.9, 1.5], 42), {})
S("L12", "flat", ([1.2, -0.2, 2.2], [1.2, -1.9, 2.15], 32),
  {"tam": {"roll": [("L12.1", 9)]}})
# 03 the reading room, afternoon one
S("L13", "room", ([7.2, -5.5, 3.4], [-1.5, 1.0, 2.2], 17), {}, rain=True)
S("L13.2", "room", ([-5.3, 1.9, 1.55], [-7.0, -0.3, 1.2], 28), {})
S("L14", "room", ([-7.0, -1.15, 1.35], [-7.0, 0.95, 0.75], 30), {"tam": {"p": [3000, 3000, 0]}})
S("L15", "room", ([1.6, -4.4, 1.5], [4.15, -4.6, 1.35], 36),
  {"tam": {"p": [-7.0, -0.95, SEAT_Z]}}, phones="head")
S("L15.2", "room", ([4.0, -4.55, 1.5], [-7.0, 0.0, 1.3], 70), {})
S("L16", "room", ([0.0, 0.0, 2.0], [-1.0, 1.0, 8.0], 24), {}, rain=True)
S("L17", "room", ([-7.0, 1.7, 2.0], [-7.0, -1.0, 2.2], 34), {"tam": {"roll": [("L17+0.1", 6)]}})
S("L17.2", "room", ([3.5, -1.9, 1.3], [0.8, 0.9, 1.3], 28), {})
S("L18", "room", ([1.25, -0.4, 1.4], [1.6, -0.9, 0.8], 40), {}, page=True)
S("L18.1", "room", ([-6.0, 0.4, 1.6], [-7.0, -0.95, 1.3], 40), {})
S("L19", "room", ([-7.0, 2.0, 2.25], [-7.0, -1.0, 2.0], 30, [-7.0, 1.3, 2.2], [-7.0, -1.0, 2.0], 30), {})
# 04 the thing at the far table
S("P01", "room", ([2.6, -4.6, 1.45], [4.15, -4.6, 1.4], 50),
  {"me": {"then": [("P01+0.1", {"head": [0, 2], "expr": "worried"}, 0.45)]}})
S("L20.2", "room", ([4.15, -4.6, 1.45], [6.3, 0.4, 1.3], 40),
  {"neg": {"p": [*D_NEG, SEAT_Z], "yaw": -90, **NEG_SIT}, "e11": {"p": PARK}, "e12": {"p": PARK}})
S("L21", "room", ([3.7, -0.9, 1.35], [6.35, 0.45, 1.35], 36), {})
S("L22", "room", ([3.1, 0.4, 1.45], [6.35, 0.4, 1.45], 40), {})
S("L23", "room", ([3.2, -1.3, 1.7], [6.35, 0.4, 1.5], 42), {})
S("L24", "room", ([4.75, -4.5, 1.2], [4.9, 0.4, 1.4], 60), {})
S("L25", "room", ([5.0, -0.8, 0.7], [6.35, 0.4, 2.1], 36),
  {"e11": {"p": [4.45, -1.4, SEAT_Z]}, "e12": {"p": [4.45, 1.2, SEAT_Z]}})
S("L26", "room", ([6.3, -2.3, 1.5], [-5.0, 0.0, 1.3], 50),
  {"neg": {"head": [-32, 4]}})
# 05 the first strange night, the flat
S("L27", "flat", ([2.7, 0.8, 1.65], [1.1, -1.9, 1.3], 26),
  {"tam": {"p": [1.2, -1.9, SOFA_Z], "yaw": 180, "sit": True, "bend": 12, "arms": [20, 20], "head": [10, 18],
           "expr": "asleep", "num": 6},
   "me": {"p": PARK}}, night=True)
S("L28", "flat", ([0.9, 2.4, 1.6], [1.4, -0.5, 1.5], 30),
  {"me": {"p": [2.1, 1.0, 0.0], "yaw": 90, "num": 1, "head": [0, 0], "expr": "neutral",
          },
   "tam": {"expr": "asleep", "mouth": [("L28+0.55", "L28+0.95", [0.1, 0.55], False)]}}, night=True, warm="L28+0.6")
S("L28.3", "flat", ([1.9, 1.75, 1.15], [2.8, 1.0, 1.0], 40), {}, night=True, steam=True)
# 06 afternoon two
S("L29", "room", ([6.2, -4.0, 4.0], [0.4, 0.3, 1.0], 20),
  {"neg": {"p": [*C_NEG, SEAT_Z], "yaw": -90, "head": [-12, 4], **{k: v for k, v in NEG_SIT.items() if k != "head"}},
   "tam": {"p": [-7.0, -0.95, SEAT_Z], "num": 6, "bend": 30, "head": [0, 22], "yaw": 180, "sit": True,
           "arms": [58, 50], "expr": "worried"},
   "me": {"p": [*ME_AT, SEAT_Z], "yaw": -90, "num": 1, "expr": "neutral", "sit": True, "bend": 12, "head": [0, 22],
          "arms": [62, 62]},
   "e11": {"p": [4.45, -1.4, SEAT_Z]}, "e12": {"p": [4.45, 1.2, SEAT_Z]}, **{
       w: {"p": [x, y, SEAT_Z], "yaw": yaw, "num": READER_NUM[w], **READ} for w, (x, y, yaw) in READERS.items()
       if w not in ("e11", "e12")}}, phones="head")
S("L30", "room", ([3.4, -4.5, 1.5], [4.15, -4.6, 1.4], 36),
  {"me": {"expr": "wide", "head": [0, 0], "look": [0, 0]}})
S("L30.2", "room", ([1.0, 1.4, 1.5], [2.75, -0.5, 1.2], 44), {})
S("L31", "room", ([-5.4, 0.5, 2.1], [-7.0, -0.95, 2.1], 30), {"tam": {"roll": [("L31+0.1", 4)]}})
S("L32", "room", ([3.2, -4.0, 1.55], [4.15, -4.6, 1.45], 44),
  {"me": {"head": [28, 2], "expr": "worried"}}, phones="half")
S("L32.3", "room", ([-7.0, -0.55, 0.98], [-7.0, 0.25, 0.8], 36), {}, tally=True)
# 07 afternoon three
S("L33", "room", ([0.0, 3.0, 3.0], [-5.4, -0.5, 1.2], 22),
  {"neg": {"p": [*B_NEG, SEAT_Z], "yaw": 180, "head": [90, 4]}, "e12": {"p": [4.45, 1.2, SEAT_Z]}})
S("L34", "room", ([-4.9, -1.5, 1.7], [-7.0, -0.3, 0.9], 36), {})
S("L35", "room", ([-7.5, -2.6, 1.7], [-5.3, -0.95, 1.4], 30), {"e5": {"numz": 0.8}})
S("L36", "room", ([-7.0, 1.7, 2.0], [-7.0, -1.0, 2.1], 34), {"tam": {"roll": [("L36+0.25", 2)]}, "e5": {"numz": 0.0}})
# 08 the closing timer
S("L37", "room", ([-3.0, 3.6, 2.6], [-3.0, 8.0, 2.55], 40), {}, lamps_down="L37+0.8", dome_dim=True)
S("L38", "room", ([6.8, -4.5, 3.4], [-2.0, 1.0, 1.6], 18), {})
S("L39", "room", ([3.0, -0.2, 2.2], [-7.0, 0.0, 2.0], 36), {})
S("L40", "room", ([-5.4, -1.8, 1.8], [-7.0, 0.1, 1.9], 30),
  {"neg": {"p": [*OLD_AT, SEAT_Z], "yaw": 0, "head": [0, 0]}}, oldseat=True)
S("L41", "room", ([2.6, -4.6, 1.45], [4.15, -4.6, 1.4], 50),
  {"me": {"expr": "worried", "head": [0, 0]}}, lamps_up="L41-0.1")
S("P02", "room", ([-3.3, 0.0, 2.0], [-7.0, 0.0, 1.6], 20),
  {"neg": {"bend": 45, "arms": [26, 26], "head": [52, -38]},
   "tam": {"bend": 12, "head": [-24, -4], "num": 2}}, reveal=True)
S("L42.3", "room", ([-4.4, 0.0, 2.0], [-7.0, 0.0, 1.4], 30), {})
S("L43", "room", ([-7.0, 1.9, 2.1], [-7.0, -1.0, 2.0], 32), {"tam": {"roll": [("L43", 1)]}})
S("L44", "room", ([-6.4, 0.2, 2.15], [-7.0, -1.0, 2.1], 40), {})
S("L45", "room", ([4.0, -4.3, 1.55], [-7.0, 0.1, 1.35], 60), {})
S("L46", "room", ([4.15, -4.6, 1.35], [-7.0, 0.95, 1.2], 90), {})
S("L47", "room", ([4.15, -4.6, 0.9], [4.15, -4.6, 2.4], 30),
  {"me": {"head": [0, -34]}})
S("P03", "room", ([4.15, -4.15, 0.6], [4.15, -4.6, 2.2], 30), {})
S("L49", "station", ([0.0, -3.4, 1.6], [0.2, 0.2, 1.9], 28),
  {"woman": {"p": [0.2, 0.2, 0.0], "yaw": 0, "num": 0, "expr": "neutral"}, "me": {"p": PARK}})
S("L50", "station", ([0.2, -3.8, 1.7], [-0.4, -0.2, 1.95], 30),
  {"woman": {"p": [0.3, 0.2, 0.0], "yaw": -70}, "man": {"p": [-1.3, -0.5, 0.0], "yaw": 70, "num": 63}})
S("L51", "room", ([4.15, -4.15, 1.35], [4.15, -4.6, 1.5], 40),
  {"neg": {"p": [*OLD_AT, SEAT_Z], "yaw": 0, **NEG_SIT},
   "tam": {"p": [-7.0, -0.95, SEAT_Z], "yaw": 180, "sit": True, "bend": 30, "arms": [58, 50], "head": [0, 22],
           "expr": "worried"},
   "me": {"p": [*ME_AT, SEAT_Z], "yaw": -90, "sit": True, "bend": 12, "head": [0, -6], "expr": "wide",
          "arms": [62, 62]}})
S("L52", "room", ([4.15, -4.15, 0.6], [4.15, -4.6, 2.2], 30), {})
S("L53", "flat", ([2.7, 0.8, 1.65], [1.1, -1.9, 1.3], 26),
  {"tam": {"p": [1.2, -1.9, SOFA_Z], "yaw": 180, "sit": True, "bend": 12, "arms": [20, 20], "head": [10, 18],
           "expr": "asleep", "num": 6, "mouth": [("L53+0.2", "L53+0.6", [0.1, 0.55], False)]},
   "me": {"p": [2.1, 1.0, 0.0], "yaw": 90, "num": 1}}, night=True)
S("L54", "room", ([-7.0, 1.7, 2.0], [-7.0, -1.0, 2.1], 34),
  {"tam": {"p": [-7.0, -0.95, SEAT_Z], "yaw": 180, "sit": True, "bend": 30, "arms": [58, 50], "head": [0, 22],
           "expr": "worried", "num": 1}, "me": {"p": [*ME_AT, SEAT_Z], "yaw": -90, "sit": True, "bend": 12,
                                                  "head": [0, -6], "expr": "wide", "arms": [62, 62], "num": 1},
   "neg": {"p": [*OLD_AT, SEAT_Z], "yaw": 0, **NEG_SIT}})
S("L55", "room", ([4.15, -4.6, 1.4], [-7.0, 0.95, 1.2], 90), {})
S("L56", "station", ([0.45, -1.9, 1.75], [0.3, 0.2, 2.0], 36),
  {"woman": {"p": [0.3, 0.2, 0.0], "yaw": -70, "num": 0, "roll": [("L56+0.6", 1)]},
   "man": {"p": [-1.3, -0.5, 0.0], "yaw": 70, "num": 63}})
# 09 the loophole
S("L57", "room", ([6.9, -2.5, 3.0], [1.0, -2.0, 1.2], 22),
  {"me": {"p": [*STAND_AT, 0.0], "yaw": -90, "sit": False, "bend": 0, "head": [0, 0], "arms": [0, 0], "expr": "neutral"},
   "tam": {"p": [-7.0, -0.95, SEAT_Z], "yaw": 180, "sit": True, "bend": 30, "arms": [58, 50], "head": [0, 22],
           "expr": "worried", "num": 1}}, phones="head", oldseat=True)
S("L58", "room", ([2.9, -3.6, 1.7], [4.2, -3.65, 1.6], 44),
  {"me": {"head": [0, 0], "expr": "neutral"}}, phones="neck")
S("L59", "room", ([2.7, -3.5, 1.7], [4.2, -3.65, 1.65], 52),
  {"me": {"expr": "wide", "mouth": [("L59", "L59>", [0.7, 0.7], True)]}})
S("L60", "room", ([6.9, -2.5, 3.0], [1.0, -2.0, 1.2], 22),
  {w: {**LOOK_UP} for w in READERS} | {"tam": {"bend": 0, "head": [0, -4], "expr": "wide"},
                                        "me": {"expr": "neutral"}})
S("L61", "room", ([-7.0, 1.6, 2.1], [-7.0, -1.0, 2.2], 32, [-7.0, 1.2, 2.1], [-7.0, -1.0, 2.2], 32),
  {"tam": {"roll": [("L61.2", 2), ("L61.3", 10), ("L61.4", 20)]}, "neg": {"p": PARK}})
S("L62", "room", ([3.2, -3.6, 2.1], [4.2, -3.65, 1.95], 36),
  {"me": {"roll": [("L62.1", 20)]}})
S("L63", "room", ([-3.4, -0.4, 1.6], [-2.0, -2.6, 1.5], 30, [-5.6, 0.2, 1.6], [-4.4, -1.5, 1.5], 30),
  {"me": {"p": [-2.0, -2.6, 0.0], "yaw": -120, "sit": False, "bend": 0, "arms": [0, 0], "head": [0, 0],
          "expr": "neutral", "walk": ([-4.4, -1.5, 0.0], "L64")}})
S("L64", "room", ([-5.2, 0.1, 1.45], [-7.0, 0.95, 0.6], 36),
  {"me": {"p": PARK}, "e7": {"p": PARK}}, oldchair=True, dead_off=True)
S("L65", "room", ([-6.5, 1.55, 0.95], [-7.0, 0.95, 0.5], 40), {})
S("L66", "room", ([-5.3, 1.8, 1.7], [-7.0, 0.3, 1.3], 28),
  {"me": {"p": [-7.0, 1.2, SEAT_Z], "yaw": 0, "sit": True, "bend": 4, "arms": [50, 50], "head": [0, 8],
          "expr": "soft"},
   "tam": {"p": [-7.0, -0.95, SEAT_Z], "yaw": 180, "sit": True, "bend": 10, "arms": [58, 50], "head": [0, 4],
           "expr": "neutral"}})
S("L67", "room", ([-3.7, -0.6, 1.6], [-5.5, 0.2, 1.4], 34),
  {"e7": {"p": [-5.3, 0.95, SEAT_Z], "yaw": 0, **READ, "arms": [150, 62], "head": [0, -2], "expr": "soft"},
   "tam": {"arms": [58, 150], "head": [18, -2], "expr": "soft"}})
S("L68", "room", ([-3.0, 0.7, 1.6], [-6.0, 0.0, 1.0], 30),
  {"e8": {"p": [-6.0, 0.0, SEAT_Z], "yaw": -90, **READ, "bend": 12, "head": [0, 6]},
   "e9": {"p": [-6.9, -2.1, 0.0], "yaw": 0, "head": [0, 0], "sit": False, "bend": 0, "arms": [0, 0],
          "expr": "soft"},
   "e10": {"p": [-8.0, 1.5, 0.0], "yaw": -20, "sit": False, "bend": 0, "arms": [0, 0], "expr": "soft",
           "head": [0, 0]}}, chairs=True)
S("L69", "room", ([-7.0, 1.5, 1.55], [-7.0, -0.95, 1.4], 40),
  {"tam": {"expr": "wide", "head": [0, -4], "arms": [58, 50], "bend": 0,
           "then": [("L69.3", {"expr": "grin"}, 0.3)]}} | {w: {"num_off": True} for w in ("e7", "e8", "e9", "e10")})
S("L70", "room", ([-4.2, 3.4, 4.3], [-7.0, 0.0, 1.5], 26),
  {"tam": {"roll": [("L70+0.4", 21)]}, "me": {"num": 1}})
S("L71", "room", ([-7.0, 1.4, 2.0], [-7.0, 0.95, 2.35], 32, [-7.0, 1.4, 2.0], [-7.0, -0.3, 2.0], 32),
  {"tam": {"expr": "grin"}, "me": {"roll": [("L71+0.9", 21)]}, "e8": {"p": PARK}, "e9": {"p": PARK}, "e10": {"p": PARK}})

# ---------------------------------------------------------------------------------------------------- build
# camera pass (after the stills sheet): cameras that sat inside a head, a table or a wall, and the framings the sheet asked for
CAM_FIX = {
    "L02": ([1.2, -7.0, 1.7], [0.4, -3.3, 1.65], 30),
    "L05.2": ([0.45, -2.3, 1.85], [0.3, 0.2, 2.15], 34),
    "L28": ([1.9, 2.7, 1.65], [1.6, -1.0, 1.4], 24),
    "L28.3": ([2.55, 1.8, 1.35], [2.65, 1.0, 1.1], 36),
    "L03.2": ([0.4, -2.5, 1.8], [0.4, 0.3, 2.0], 34),
    "L05": ([0.0, -4.4, 1.7], [-0.4, -0.2, 1.8], 26),
    "L08.1": ([-0.6, -3.7, 1.75], [0.3, 0.0, 1.7], 22, [-0.1, -3.7, 1.75], [0.9, 0.0, 1.7], 22),
    "L13": ([6.0, -5.0, 3.4], [-1.5, 1.0, 2.2], 17),
    "L14": ([-6.4, -1.0, 1.5], [-7.0, 1.0, 0.6], 30),
    "L15.2": ([4.7, -4.25, 1.75], [-7.0, 0.0, 1.3], 70),
    "L18.1": ([-7.9, 0.6, 1.7], [-7.0, -0.45, 1.3], 28),
    "P01": ([1.95, -4.7, 1.45], [3.95, -4.6, 1.4], 24),
    "L20.2": ([4.6, -4.3, 1.65], [6.3, 0.4, 1.3], 40),
    "L24": ([4.55, -4.1, 1.2], [6.3, 0.4, 1.2], 28),
    "L25": ([3.6, -0.2, 0.95], [6.2, 0.4, 1.75], 32),
    "L26": ([7.3, 0.9, 1.7], [-7.0, 0.0, 1.3], 55),
    "L30": ([2.2, -4.0, 1.5], [3.95, -4.6, 1.4], 26),
    "L30.2": ([0.2, -2.4, 1.6], [2.75, -0.5, 1.2], 40),
    "L32": ([2.4, -3.9, 1.6], [3.95, -4.6, 1.45], 28),
    "L32.3": ([-7.0, 0.3, 0.95], [-7.0, -0.13, 0.82], 36),
    "L34": ([-5.0, -1.9, 2.1], [-7.0, -0.35, 0.85], 28),
    "L41": ([2.0, -4.5, 1.5], [3.95, -4.6, 1.4], 28),
    "L22": ([-0.8, 0.4, 1.6], [6.35, 0.4, 1.4], 40),
    "L23": ([0.0, -2.0, 1.9], [6.35, 0.4, 1.5], 34),
    "P02": ([-2.6, 0.0, 1.8], [-7.0, 0.0, 1.5], 22),
    "L42.3": ([-2.4, 0.0, 1.8], [-7.0, 0.0, 1.5], 22),
    "L45": ([-5.0, -0.2, 1.5], [4.15, -4.6, 1.3], 70),
    "L46": ([4.6, -4.3, 1.75], [-7.0, 0.95, 1.2], 85),
    "L47": ([3.1, -4.6, 1.0], [3.95, -4.6, 1.65], 28),
    "P03": ([4.3, -3.6, 0.8], [4.0, -4.6, 2.0], 28),
    "L51": ([2.3, -4.0, 1.5], [3.95, -4.6, 1.45], 28),
    "L52": ([4.3, -3.6, 0.8], [4.0, -4.6, 2.0], 28),
    "L55": ([4.6, -4.3, 1.75], [-7.0, 0.95, 1.2], 85),
    "L57": ([5.8, -3.0, 1.95], [-1.0, -4.3, 1.3], 24),
    "L58": ([2.7, -3.6, 1.7], [4.2, -3.65, 1.6], 36),
    "L60": ([5.4, -2.0, 3.1], [-3.0, 0.0, 1.2], 17),
    "L62": ([2.0, -3.65, 2.0], [4.2, -3.65, 1.95], 28),
    "L64": ([-5.9, 1.9, 1.2], [-7.0, 1.1, 0.55], 34),
    "L65": ([-6.3, 1.5, 0.9], [-7.0, 1.0, 0.5], 40),
    "L67": ([-6.0, -3.2, 1.6], [-6.2, 0.4, 1.3], 26),
    "L69": ([-7.6, 1.9, 1.55], [-7.05, -0.95, 1.45], 34),
    "L71": ([-4.6, 2.3, 2.0], [-7.0, 1.0, 2.0], 36, [-4.9, -2.0, 2.0], [-7.0, -0.95, 1.7], 32),
}
for s in SH:
    if s["ref"] in CAM_FIX:
        s["cam"] = CAM_FIX[s["ref"]]
SH[10]["stage"] = SH[10]["stage"]
S_SEAT = {"at": "L64", "name": "seat", "to": 1.0, "dur": 0.6}

# lines and chunk refs
lines2 = []
for ln in lines:
    lines2.append(ln)
    if ln["id"] == "L19":
        lines2.append({"id": "P01", "pause": 0.6, "chunks": []})
    if ln["id"] == "L41":
        lines2.append({"id": "P02", "pause": 0.6, "chunks": []})
    if ln["id"] == "L47":
        lines2.append({"id": "P03", "pause": 0.6, "chunks": []})
lines = lines2

shots, scene_of = [], {}
for i, s in enumerate(SH):
    sid = f"S{i + 1:02d}"
    cam = s["cam"]
    sc = s["scene"]
    keys = [[0, W(sc, cam[0]), W(sc, cam[1]), cam[2]]]
    if len(cam) > 3:
        keys.append([1, W(sc, cam[3]), W(sc, cam[4]), cam[5]])
    shot = {"id": sid, "cam": keys, "step": 2, "hand": s.get("hand", 0.004)}
    if i:
        shot["at"] = s["ref"]
    shots.append(shot)
    scene_of[sid] = sc
    s["id"] = sid
    s["ref_"] = s["ref"] if i else 0

# ---- the staging -> acting and number cues
acting = {w: [] for w in cast}
cues = []
KEYF = {"yaw": 0, "sit": False, "bend": 0, "arms": [0, 0], "head": [0, 0], "expr": "neutral", "look": [0, 0],
        "blink": True, "tremble": 0, "side": [0, 0]}
cur, last_key, last_pos, last_num = {}, {}, {w: PARK for w in cast}, {}
last_numz = {}
prev_scene = None
nxt_ref = [s["ref"] for s in SH[1:]] + ["end"]


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
        extra = []
        if sp.get("walk"):
            to, until = sp["walk"]
            extra.append(({"pos": W(sc, to)}, until, 0.0))
        for rf, fields, bl in sp.get("then", []):
            extra.append((fields, rf, bl))
        sig = json.dumps(k, sort_keys=True)
        if sig != last_key.get(who) or extra or sp.get("mouth"):
            frm = last_pos[who]
            if ref != 0:   # at t=0 a PARK pre-key would hide everyone on frame 0
                acting[who].append({"at": ref, "pos": frm})
            acting[who].append({"at": ref, **k, "blend": 0.0})
            last_key[who] = sig
            last_pos[who] = k["pos"]
            for fields, rf, bl in extra:
                kk = {**k, **{f: v for f, v in fields.items() if f != "pos"}}
                if "pos" in fields:
                    kk["pos"] = fields["pos"]
                    last_pos[who] = kk["pos"]
                    kk["keep_yaw"] = False
                acting[who].append({"at": rf, **kk, "blend": bl if bl else 0.25})
                # the later shots start from the new pose
                cur[who] = {**cur[who], **{f: v for f, v in fields.items() if f != "pos"}}
                if "pos" in fields:
                    cur[who]["p"] = [fields["pos"][0] - SCN[sc][0], fields["pos"][1] - SCN[sc][1], fields["pos"][2]]
                last_key[who] = None
            for m in sp.get("mouth", []):
                a, b, mm, flap = m
                acting[who].append({"from": a, "to": b, "mouth": mm, **({"flap": True} if flap else {})})
            cur[who].pop("mouth", None)
            cur[who].pop("walk", None)
            cur[who].pop("then", None)
        # numbers
        if sp.pop("num_off", False):
            cues.append({"at": ref, "name": "num", "who": who, "v": None, "snap": True})
            last_num[who] = None
            sp["num"] = None
        nz = sp.get("numz", 0.0)
        if who in NUM_SLOTS and last_numz.get(who, 0.0) != nz:
            cues.append({"at": ref, "name": "numz", "who": who, "v": nz})
            last_numz[who] = nz
        if who in NUM_SLOTS and sp.get("num") is not None:
            if last_num.get(who) != sp["num"]:
                cues.append({"at": ref, "name": "num", "who": who, "v": sp["num"], "snap": True})
                last_num[who] = sp["num"]
        for rf, v in sp.get("roll", []):
            cues.append({"at": rf, "name": "num", "who": who, "v": v})
            last_num[who] = v
            sp["num"] = v
        sp.pop("roll", None)

# ---- per-shot cues
phones_state = None
for i, s in enumerate(SH):
    ref = s["ref_"]
    if s.get("phones"):
        cues.append({"at": ref, "name": "phones", "mode": s["phones"]})
    if s.get("lamps_down"):
        cues.append({"at": s["lamps_down"], "name": "lamps", "to": 0.15, "dur": 1.5})
        cues.append({"at": s["lamps_down"], "name": "dome", "to": 0.12, "dur": 1.5})   # the room goes to about 15%: numbers and a rim light
    if s.get("lamps_up"):
        cues.append({"at": s["lamps_up"], "name": "lamps", "to": 1.0, "dur": 1.5})
        cues.append({"at": s["lamps_up"], "name": "dome", "to": 0.5, "dur": 1.5})
    if s.get("dome_dim"):
        cues.append({"at": "L33", "name": "dome", "to": 1.0, "dur": 0.1})
        cues.append({"at": "L34", "name": "dome", "to": 0.5, "dur": 4.5})
    if s.get("warm"):
        cues.append({"at": s["warm"], "name": "warm", "who": "me"})
    if s.get("oldchair"):
        cues.append({"at": ref, "name": "oldchair", "d": 0.25})
        cues.append(S_SEAT)
        cues.append({"at": ref, "name": "dome", "to": 1.0, "dur": 1.2})
    if s.get("dead_off"):
        cues.append({"at": ref, "name": "dead", "tables": []})
    if s.get("page"):
        cues.append({"at": ref, "name": "page", "dur": 0.8})
    if s.get("steam"):
        cues.append({"at": ref, "name": "steam", "on": True})
    if s.get("chairs"):
        cues.append({"at": ref, "name": "extra_chairs", "on": True})
# the dead lamps: a lamp goes out at the table the Negative sits at, from the line it's first there
cues += [{"at": 0, "name": "dead", "tables": []},
         {"at": "L20.2", "name": "dead", "tables": ["D"]},
         {"at": "L29", "name": "dead", "tables": ["D", "C"]},
         {"at": "L33", "name": "dead", "tables": ["D", "C", "B"]}]
cues += [{"at": 0, "name": "lamps", "to": 1.0, "dur": 0.1}, {"at": 0, "name": "dome", "to": 1.0, "dur": 0.1},
         {"at": 0, "name": "phones", "mode": "head"}, {"at": "L58", "name": "phones", "mode": "neck"},
         {"at": 0, "name": "extra_chairs", "on": False}]
# the open dome's dusk comes slowly, well before the timer (flash plan: a dimming, never a blackout)
cues = [c for c in cues if not (c["name"] == "dome" and c.get("dur") == 0.1 and c["at"] == "L33")]

# ---- sound
rolls = [c for c in cues if c["name"] == "num" and not c.get("snap")]
sfx = [{"at": c["at"], "kind": "click", "db": -27} for c in rolls]
sfx += [
    {"at": "L18+0.15", "kind": "whoosh", "db": -26, "dur": 0.3},
    {"at": "P01>", "kind": "hit", "db": -17, "keep": True},
    {"at": "L28.3", "kind": "riser", "db": -24, "dur": 2.0},
    {"at": "L32.3", "kind": "riser", "db": -23, "dur": 1.9},
    {"at": "L37+0.8", "kind": "glide", "db": -15, "dur": 1.7},
    {"at": "L41-0.1", "kind": "riser", "db": -22, "dur": 1.4},
    {"at": "P02", "kind": "sting", "db": -9, "dur": 2.2, "keep": True},
    {"at": "P03>", "kind": "hit", "db": -17, "keep": True},
    {"at": "L68", "kind": "scrape", "db": -26, "dur": 1.0},
    {"at": "L67+0.2", "kind": "whoosh", "db": -28, "dur": 0.3},
]
sfx += [{"at": f"L37+{0.0 + 0.6 * k:.1f}", "kind": "click", "db": -23} for k in range(2)]
sfx += [{"at": f"L16+{0.0 + 0.55 * k:.2f}", "kind": "click", "db": -30} for k in range(3)]

story = {
    "slug": "ep43-reading-room",
    "title": "In this town, the number over your head is how many people know your name",
    "made_for_kids": False,
    "premise": "In a town where a glowing number over every head counts the people who know your name, my number has said "
               "1 for years, and my brother's has been falling since he began studying alone in the domed reading room "
               "where we used to sit together, while a person printed in reverse, with no number at all, takes a table "
               "nearer to him every afternoon.",
    "twist": "You don't count yourself. My 1 was never me, it was my brother, the only person in town who knew my name, "
             "and his last 1 was me, so I was never out of his count: I say both our names once, aloud, in the silent room.",
    "world": "A round public reading room under a rain-streaked glass dome with green plaster walls, oak tables and "
             "brass-and-green lamps on one closing timer, plus library steps in the sun, a party, a station platform, a "
             "wet street and a small flat.",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff9ec4",
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#8a9aa6", "fog_density": 0.006, "fog_start": 14.0, "sky": "#9fb3c2", "exposure": 0.2,
             "flash_safe": True},
    "grade": {"shadows": [-0.01, 0.0, 0.03], "highlights": [0.03, 0.01, -0.02], "saturation": 0.96, "contrast": 1.06,
              "vignette": 0.32, "bloom": 0.42, "grain": 0.012},
    "rain_shots": sorted({s["id"] for s in SH if s.get("rain") or s["scene"] == "street"}),
    "rain_gain": 0.7,
    "phonemes": {"Ossie": "ˈɔzi", "Tam": "tˈæm", "Luke": "lˈuːk"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "scene_of": scene_of,
    "night_shots": [s["id"] for s in SH if s.get("night")],
    "steam_shots": [s["id"] for s in SH if s.get("steam")],
    "scenes": {k: list(v) for k, v in SCN.items()},
    "numbers": NUM_SLOTS,
    "room": {"tables": TABLES, "chairs": CHAIRS, "old_chair": OLD_CHAIR, "readers": list(READERS)},
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 45, "mode": "dorian", "bpm": 80, "seed": 43,
              "sections": [
                  {"at": 0, "voices": ["pad", "piano"], "energy": 0.4},
                  {"at": "L08", "voices": ["pad", "piano"], "energy": 0.3},
                  {"at": "L13", "voices": ["drone", "pad", "piano"], "energy": 0.3},
                  {"at": "P01", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L27", "voices": ["drone", "pad", "piano"], "energy": 0.3},
                  {"at": "L33", "voices": ["drone", "pad"], "energy": 0.35},
                  {"at": "L37", "voices": ["drone", "pad"], "energy": 0.25},
                  {"at": "P02", "voices": ["drone", "pad"], "energy": 0.5},
                  {"at": "L48", "voices": ["pad"], "energy": 0.3},
                  {"at": "L57", "mode": "major", "voices": ["pad", "piano"], "energy": 0.65},
                  {"at": "L63", "mode": "major", "voices": ["pad", "piano"], "energy": 0.75},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "L08", "lufs": -44},
                  {"kind": "rain", "from": "L08", "to": "end", "lufs": -35},
                  {"kind": "hum", "from": "L13", "to": "L66", "lufs": -45},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "P01>", "keep": ["hit"]},
                              {"from": "P02", "to": "P02>", "keep": ["sting"]},
                              {"from": "P03", "to": "P03>", "keep": ["hit"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
