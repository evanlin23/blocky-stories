"""Writes ../story.json for "Our House Leans Toward HIS" (ep118-two-houses, batch 12).

Run from anywhere: python stories/ep118-two-houses/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (lean, tag, sash, marble, frames, squirrel, note, notebig, hold) and the score.

World (metres, z up, the houses face -y): our house (butter yellow) pivots on its inner bottom edge at x -0.8 and
leans toward +x; Mr. Pruitt's (sky blue) pivots at x +0.8 and leans toward -x. `ux` is the distance outward from a
house's inner edge, y the depth from its front face, z the height. Wp() maps those to world metres for a lean of
`deg` degrees, which is how cameras and people are placed on the tilted floors. Acting yaw: 0 faces -y (the street).
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
LOOP = 0.25

# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True, "ink": "#24131f"}
cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#1fb3a8", "pattern": "solid", "pants": "#b59a6a", "shoes": "#f4f4f2",
           "sleeves": "short", "hair": "cap", "hair_c": "#2a1d15", "face": dict(FACE)},
    "dad": {"age": "adult", "skin": "#d9a27a", "shirt": "#8a5a36", "pattern": "knit", "pattern_c": "#a06c42", "pants": "#4a4f5c",
            "shoes": "#3a2a20", "sleeves": "long", "hair": "none", "width": 1.1, "height": 0.96, "face": dict(FACE)},
    "dad_n": {"age": "adult", "skin": "#d9a27a", "shirt": "#8a2f3a", "pattern": "solid", "pants": "#8a2f3a", "shoes": "#3a2a20",
              "sleeves": "long", "hair": "none", "width": 1.1, "height": 0.96, "extras": ["coat"], "zip_c": "#e8c0a0",
              "face": dict(FACE)},
    "pruitt": {"age": "adult", "skin": "#ecc3a0", "shirt": "#3d78d0", "pattern": "knit", "pattern_c": "#5a92e0", "pants": "#3a3f4e",
               "shoes": "#2a2a30", "sleeves": "long", "hair": "swoop", "hair_c": "#f1efe8", "height": 1.08, "width": 0.88,
               "extras": ["glasses"], "extra_c": "#111114", "face": dict(FACE)},
    "pruitt_n": {"age": "adult", "skin": "#ecc3a0", "shirt": "#26365e", "pattern": "solid", "pants": "#26365e", "shoes": "#2a2a30",
                 "sleeves": "long", "hair": "swoop", "hair_c": "#f1efe8", "height": 1.08, "width": 0.88,
                 "extras": ["coat", "glasses"], "extra_c": "#111114", "zip_c": "#9aa6c8", "face": dict(FACE)},
    "baker1": {"age": "adult", "skin": "#d9a27a", "shirt": "#ffffff", "pattern": "solid", "pants": "#4a4f5c", "shoes": "#3a2a20",
               "sleeves": "long", "hair": "none", "hat": "tophat", "hat_c": "#ffffff", "extras": ["apron"], "extra_c": "#fffaf0",
               "face": dict(FACE)},
    "baker2": {"age": "adult", "skin": "#ecc3a0", "shirt": "#ffffff", "pattern": "solid", "pants": "#4a4f5c", "shoes": "#3a2a20",
               "sleeves": "long", "hair": "none", "hat": "tophat", "hat_c": "#ffffff", "extras": ["apron"], "extra_c": "#fffaf0",
               "face": dict(FACE)},
}

NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {k: [] for k in cast}
cues, shots = [], []
visible = set()
DEG = 5.0

# ---------------------------------------------------------------------------------------------------- geometry
HEADH = {"me": 1.62, "dad": 1.55, "dad_n": 1.55, "pruitt": 1.72, "pruitt_n": 1.72, "baker1": 1.6, "baker2": 1.6}
F1, F2 = 0.08, 3.0


def Wp(side, ux, y, z, deg=None):
    """World point of a house-local point (side 'o' ours, 'h' his) at the current lean."""
    d = DEG if deg is None else deg
    s, px = (1, -0.8) if side == "o" else (-1, 0.8)
    a = math.radians(d)
    return [round(px - s * (ux * math.cos(a) - z * math.sin(a)), 3), round(y, 3), round(ux * math.sin(a) + z * math.cos(a), 3)]


def feet(side, ux, y, level):
    return Wp(side, ux, y, level)


def head(side, ux, y, level, who="me"):
    p = feet(side, ux, y, level)
    return [p[0], p[1], round(p[2] + HEADH[who], 3)]


def add(p, d):
    return [round(p[0] + d[0], 3), round(p[1] + d[1], 3), round(p[2] + d[2], 3)]


# ---------------------------------------------------------------------------------------------------- acting
def raw(who, at, **kw):
    acting[who].append({"at": at, **kw})


def put(who, at, pos, yaw=0, expr="neutral", **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": list(pos), "blend": 0, "yaw": yaw, "expr": expr, "hidden": False, **NEUTRAL, **kw})
    visible.add(who)


def gone(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})
    visible.discard(who)


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def lean(at, who, deg, dur):
    cue(at, "lean", who=who, deg=deg, dur=dur)


# ---------------------------------------------------------------------------------------------------- cameras
def cam(loc, tgt, lens, loc2=None, tgt2=None, lens2=None):
    ks = [[0, list(loc), list(tgt), lens]]
    if loc2 or tgt2 or lens2:
        ks.append([1, list(loc2 or loc), list(tgt2 or tgt), lens2 or lens])
    return ks


def S(sid, at, cams, look="day", keep=(), **kw):
    """A shot. `keep`: the characters who stay visible across the cut (everybody else is hidden at it)."""
    d = {"id": sid, "cam": cams, "step": 2, "hand": 0.004, "look": look}
    if len(shots):
        d["at"] = at
    d.update(kw)
    shots.append(d)
    for w in list(visible):
        if w not in keep:
            gone(w, at)
    return d


def show(sid, at, cams, look, people, **kw):
    """people: list of (who, pos, yaw, expr, extra-kw)."""
    S(sid, at, cams, look, **kw)
    for who, pos, yaw, expr, ex in people:
        put(who, at, pos, yaw, expr, **ex)


for k in acting:
    acting[k].append({"at": 0, "pos": [0, 40, 0], "hidden": True, "blend": 0, **NEUTRAL})

ANG, SHEEP, LAUGH, SMILE, WARM = "angry", "smirk", "laugh", "smile", "warm"
YARD_D, YARD_P = (-0.5, -1.6), (0.5, -1.6)
BX = (-0.06, 0.0)

# =========================================================================================== 01 L01-L05  (day, lean 5)
# S01a: Dad at the island in our kitchen, his mug tilted on it (it leans with the house), a crooked frame behind him
dadk = feet("o", 2.55, 3.85, F1)
S("S01a", 0, cam(add(feet("o", 2.55, 1.3, F1), (0, 0, 2.15)), add(dadk, (0, 0, 1.4)), 40, add(feet("o", 2.55, 1.7, F1), (0, 0, 2.1))),
  "day", fill=0.7)
put("dad", 0, dadk, 0, ANG)
cue(0, "tag", v="a")
cue(0, "frames", deg=3.0)
# S01b: Pruitt's face in his window
pw = feet("h", 0.5, 0.5, F2)
pw = add(pw, (0, 0, -0.27))       # head fully inside the window, under the lintel
pwh = add(pw, (0, 0, 1.68))
S("S01b", "L02", cam(add(pwh, (0.0, -2.4, 0.0)), pwh, 34, add(pwh, (0.0, -2.0, 0.0))), "day", fill=0.5)
put("pruitt", "L02", pw, 0, ANG)
# S02: both over the hedge, glaring
show("S02", "L03", cam([0.0, -4.7, 1.7], [0.0, -1.6, 1.55], 22, [0.0, -4.2, 1.7]), "day",
     [("dad", (*YARD_D, 0), 0, ANG, {}), ("pruitt", (*YARD_P, 0), 0, ANG, {})], fill=0.7)
# S03a/b: another street's pair tips together and stands back up
lean("L03.2", "lilac", 8.0, 1.0)
lean("L03.2", "coral", 8.0, 1.0)
lean("L03.4", "lilac", 0.0, 2.6)
lean("L03.4", "coral", 0.0, 2.6)
lean("L04", "lilac", 3.5, 0.5)
lean("L04", "coral", 3.5, 0.5)
S("S03a", "L03.3", cam([-10.4, -13.6, 3.6], [-10.4, 0.0, 3.8], 19, [-10.4, -13.0, 3.6]), "day")
S("S03b", "L03.4", cam([-10.4, -13.4, 3.4], [-10.4, 0.0, 3.8], 19, [-10.4, -12.6, 3.7]), "day")
# S04: two bakeries kiss over the street, a baker at each door
show("S04", "L04", cam([-58.8, -11.0, 3.8], [-58.8, 0.0, 3.8], 20, [-58.8, -10.2, 3.8]), "day",
     [("baker1", (-61.85, -1.0, 0), 0, SMILE, {}), ("baker2", (-55.75, -1.0, 0), 0, SMILE, {})])
# S05: the duplex folded like a book
S("S05", "L05", cam([-79.1, -11.0, 3.8], [-79.1, 0.0, 3.9], 20, [-79.1, -10.0, 4.0]), "day")

# =========================================================================================== 02 L06-L15
show("S06a", "L06", cam([0.0, -4.7, 1.7], [0.0, -1.6, 1.55], 20, [0.0, -4.2, 1.7]), "day",
     [("dad", (*YARD_D, 0), 15, ANG, {}), ("pruitt", (*YARD_P, 0), -15, ANG, {})])
show("S06b", "L06.3", cam([0.15, -4.0, 1.85], [0.55, -1.6, 1.7], 32, [0.15, -3.6, 1.85]), "day",
     [("pruitt", (*YARD_P, 0), -15, ANG, {}), ("dad", (*YARD_D, 0), 15, ANG, {})])
show("S07", "L07", cam([0.0, -12.5, 3.2], [0.0, 0.0, 3.9], 22, [0.0, -11.5, 3.4]), "day", [])
# S08: our table on a stack of books; me behind it
meK = feet("o", 1.0, 2.3, F1)
show("S08", "L08", cam(add(feet("o", 1.7, 0.5, F1), (0, 0, 0.3)), add(feet("o", 0.6, 1.3, F1), (0, 0, 0.12)), 24,
                      add(feet("o", 2.2, 0.5, F1), (0, 0, 1.0)), add(feet("o", 1.0, 1.8, F1), (0, 0, 1.2))), "day",
     [("me", feet("o", 1.0, 2.5, F1), 0, "neutral", {})], fill=0.6)
# S09: the marble, in the hall, rolls to his side
cue("L09.1-0.4", "marble", ux=2.5, y=0.95)
show("S09a", "L09", cam(add(feet("o", 2.9, 0.4, F2), (0, 0, 0.55)), add(feet("o", 2.55, 0.95, F2), (0, 0, 0.3)), 30,
                       add(feet("o", 2.8, 0.6, F2), (0, 0, 0.5))), "day", [], hl=0.7, fill=0.5)
S("S09b", "L09.1", cam(add(feet("o", 2.5, 0.25, F2), (0, 0, 0.3)), add(feet("o", 2.3, 0.95, F2), (0, 0, 0.12)), 15,
                       add(feet("o", 1.7, 0.25, F2), (0, 0, 0.3)), add(feet("o", 1.3, 0.95, F2), (0, 0, 0.12))), "day", hl=0.7, fill=0.5)
# S10: Dad's mug tilted, the coffee level, his face behind it (cover frame)
mugw = feet("o", 2.75, 2.9, F1)
show("S10", "L10", cam(add(feet("o", 2.55, 1.3, F1), (0, 0, 2.15)), add(feet("o", 2.55, 3.4, F1), (0, 0, 1.4)), 40,
                      add(feet("o", 2.55, 1.7, F1), (0, 0, 2.1)), add(feet("o", 2.55, 3.4, F1), (0, 0, 1.42))), "day",
     [("dad", dadk, 0, ANG, {})], fill=0.7)
# S11: at the gate, pointing with flat hands
show("S11", "L11", cam([0.0, -8.0, 1.7], [0.0, -4.5, 1.45], 26, [0.0, -7.2, 1.7]), "day",
     [("dad", (-0.62, -4.5, 0), 40, ANG, {"arms": [0, 80], "head": [-40, 0]}),
      ("pruitt", (0.62, -4.5, 0), -40, ANG, {"arms": [80, 0], "head": [40, 0]})])
# S12: his hedge. who owns the squirrel
show("S12a", "L12", cam([-0.1, -4.2, 1.7], [-0.5, -1.9, 1.55], 32, [-0.1, -3.7, 1.7]), "day",
     [("dad", (-0.5, -1.9, 0), 10, ANG, {})])
cue("L12.1", "squirrel", pos=[0.3, -2.4, 0.76], yaw=-100, scale=1.8)
cue("L13", "squirrel", hidden=True)
show("S12b", "L12.1", cam([0.45, -4.9, 1.2], [0.05, -2.4, 1.2], 24, [0.45, -4.5, 1.2]), "day",
     [("dad", (-0.55, -1.8, 0), 0, ANG, {}), ("pruitt", (0.55, -1.8, 0), 0, ANG, {})])
# S13: the angry note on his door, every morning
note_at = Wp("h", 2.95, 0.035, 1.55, 5.0)
cue("L13+0.6", "note", on=True)
show("S13", "L13", cam([4.9, -3.4, 1.6], [3.5, -0.4, 1.5], 30, [4.5, -2.9, 1.6], [3.5, -0.4, 1.5]), "day",
     [("dad", (3.4, -0.7, 0), 70, ANG, {"side": [0, 106], "head": [-20, 0]})], fill=0.9, dl=0.6)
# S14: the note, then his face reading it
cue("L14", "notebig", on=True, pos=[3.3, -1.45, 1.3], scale=1.0)
show("S14a", "L14", cam([3.3, -2.35, 1.3], [3.3, -1.45, 1.3], 34, [3.3, -2.05, 1.3]), "day",
     [])
show("S14b", "L14.1", cam([3.2, -3.5, 1.7], [3.3, -1.0, 1.55], 32, [3.2, -3.0, 1.7]), "day",
     [("pruitt", (3.3, -1.0, 0), 0, "neutral", {"arms": [70, 70], "look": [0, -0.6]})])
cue("L15", "notebig", on=False, pos=[0, 0, -9])
# S15: two mugs in the sink; me, juice
sinkp = feet("o", 1.95, 2.9, F1)
show("S15a", "L15", cam(add(feet("o", 1.95, 1.9, F1), (0, 0, 1.75)), add(feet("o", 1.95, 2.9, F1), (0, 0, 0.95)), 32,
                       add(feet("o", 1.95, 2.3, F1), (0, 0, 1.6)), add(feet("o", 1.95, 2.9, F1), (0, 0, 0.95))), "day", [], fill=0.7)
show("S15b", "L15.4", cam(add(feet("o", 2.0, 1.6, F1), (0, 0, 1.55)), add(feet("o", 2.0, 3.85, F1), (0, 0, 1.5)), 40,
                         add(feet("o", 2.0, 2.0, F1), (0, 0, 1.55))), "day",
     [("me", feet("o", 2.0, 3.85, F1), 0, "neutral", {})], fill=0.7)

# =========================================================================================== 03 L16-L27  (night, storm)
DEG = 8.5
lean("L16", "main", 8.5, 5.0)
S("S16", "L16", cam([0.0, -12.5, 3.4], [0.0, 0.0, 3.9], 22, [0.0, -11.6, 3.5]), "night", pk=1.0, hl=1.0, pl=1.0, fill=0.2,
  rain=True)
cue("L17", "frames", deg=3.0, to=9.0, dur=3.5)
mehall = feet("o", 2.7, 3.7, F2)
show("S17", "L17", cam(add(feet("o", 1.6, 0.5, F2), (0, 0, 1.5)), add(mehall, (0, 0, 1.45)), 28,
                      add(feet("o", 1.6, 0.9, F2), (0, 0, 1.5)), add(mehall, (0, 0, 1.5))), "night",
     [("me", mehall, 0, "worried", {})], fill=0.5)
S("S18a", "L18", cam([0.0, -6.8, 4.5], [0.0, 0.0, 4.5], 26, [0.0, -6.0, 4.5]), "night", pk=1.0, fill=0.2, rain=True)
S("S18b", "L18.2", cam([0.0, -2.8, 4.5], [0.0, 0.0, 4.5], 34, [0.0, -2.3, 4.5]), "night", pk=1.0, fill=0.2, rain=True)
# the drop: his lamp goes out slowly (the shot before ramps it down over 0.35 s)
S("S19a", "P01", cam([-0.25, -2.3, 4.5], [0.0, 0.0, 4.5], 36, [-0.2, -2.0, 4.5]), "night", pl=0.0, pk=0.5, fill=0.15, rain=True)
# S19: out of his dark window, something reaches
PR_WIN = feet("h", 0.5, 0.45, F2)
PR_DARK = add(feet("h", 0.55, 0.55, F2), (0, 0, -0.9))      # standing back in the dark room, only the arm reaches out
show("S19", "L19", cam([-0.9, -2.0, 4.5], [0.35, 0.0, 4.45], 36, [-0.7, -1.8, 4.5], [0.3, 0.0, 4.45]), "night",
     [], pl=0.0, pk=0.5, fill=0.1, rain=True)
S("S19b", "L19.1", cam([0.9, -3.4, 4.15], [-0.4, -0.5, 4.17], 34, [0.8, -3.1, 4.15], [-0.4, -0.5, 4.18]), "night",
  pl=0.0, pk=0.5, fill=0.3, rain=True, armout=True)
S("S19c", "L19.2", cam([0.7, -2.6, 4.15], [-0.45, -0.7, 4.28], 36, [0.55, -2.0, 4.15], [-0.47, -0.7, 4.3]), "night",
  pl=0.0, pk=0.5, fill=0.3, rain=True, armout=True)
cue("L19", "hold", p=False, d=False)
# S20: A HAND. toward ours -- me, scared, in our window
ME_WIN = feet("o", 0.65, 1.0, F2)
show("S20", "L20", cam([0.1, -2.6, 4.3], [-0.65, -0.7, 4.4], 24, [0.0, -2.3, 4.3], [-0.65, -0.7, 4.4]), "night",
     [("me", ME_WIN, 15, "scared", {})], pl=0.0, pk=0.5, fill=0.3, rain=True, armout=True)
cue("L21+0.15", "sash", dur=0.55)
show("S21", "L21", cam([-0.64, -1.7, 4.45], [-0.64, 0.0, 4.4], 40, [-0.64, -1.35, 4.45]), "night",
     [], pl=0.5, pk=0.6, fill=0.25, rain=True)
DAD_WIN = feet("o", 0.5, 0.4, F2)
show("S22", "L22", cam(add(DAD_WIN, (-0.15, -2.1, 1.4)), add(DAD_WIN, (0, 0, 1.4)), 38, add(DAD_WIN, (-0.1, -1.8, 1.42))), "night",
     [("dad_n", DAD_WIN, 0, "neutral", {"lean": 6})], pl=0.9, pk=0.8, fill=0.35, rain=True)
cue("L23", "hold", p=True, d=False)
show("S23", "L23", cam([0.0, -3.5, 4.55], [0.0, 0.0, 4.5], 21, [0.0, -3.1, 4.55]), "night",
     [("pruitt_n", PR_WIN, -25, "neutral", {"arms": [90, 0], "lean": 10}), ("dad_n", DAD_WIN, 25, "neutral", {"lean": 6})],
     pl=0.9, pk=0.8, fill=0.3, rain=True)
cue("L24", "hold", p=False, d=True)
show("S24", "L24", cam([0.0, -3.5, 4.55], [0.0, 0.0, 4.5], 21, [0.0, -3.1, 4.55]), "night",
     [("pruitt_n", PR_WIN, -25, WARM, {"arms": [60, 0], "lean": 3}),
      ("dad_n", DAD_WIN, 25, WARM, {"arms": [0, 60], "lean": 6})], pl=1.0, pk=0.8, fill=0.35, rain=True)
show("S25", "L25", cam(add(DAD_WIN, (0.1, -2.1, 1.4)), add(DAD_WIN, (0, 0, 1.42)), 38, add(DAD_WIN, (0.1, -1.8, 1.42))), "night",
     [("dad_n", DAD_WIN, 0, LAUGH, {"lean": 6})], pl=1.0, pk=0.8, fill=0.35, rain=True)
cue("L25", "hold", p=False, d=False)
PR_IN, DAD_IN = feet("h", 0.32, 0.45, F2), feet("o", 0.32, 0.4, F2)      # a little nearer the gap so both heads fit a tight frame
BOTH = [("pruitt_n", PR_IN, -25, LAUGH, {"arms": [90, 0], "lean": 6}), ("dad_n", DAD_IN, 25, LAUGH, {"arms": [0, 90], "lean": 6})]
cue("L26", "hold", p=False, d=True)
show("S26a", "L26", cam([0.0, -3.2, 4.6], [0.0, 0.0, 4.6], 22, [0.0, -3.0, 4.6]), "night", BOTH, pl=1.0, pk=0.8, fill=0.4,
     rain=True)
S("S26b", "L26.2", cam([0.0, -2.9, 4.6], [0.0, 0.0, 4.6], 26, [0.0, -2.6, 4.6]), "night", keep=("pruitt_n", "dad_n"),
  pl=1.0, pk=0.8, fill=0.4, rain=True)
cue("L27", "hold", p=False, d=False)
show("S27a", "L27", cam(add(mehall, (0.0, -2.3, 1.55)), add(mehall, (0, 0, 1.5)), 32, add(mehall, (0.0, -1.9, 1.55))), "night",
     [("me", mehall, 0, "wide", {})], fill=0.45, hl=1.0)
show("S27b", "L27.1", cam(add(DAD_WIN, (0.2, -2.0, 1.4)), add(DAD_WIN, (0, 0, 1.42)), 38, add(DAD_WIN, (0.2, -1.7, 1.42))), "night",
     [("dad_n", DAD_WIN, 0, SHEEP, {"lean": 4, "head": [-25, -5], "look": [-0.8, 0]})], pl=1.0, pk=0.8, fill=0.35, rain=True)

# =========================================================================================== 04 L28-L37  (they're friends)
show("S28a", "L28", cam([0.0, -3.5, 4.55], [0.0, 0.0, 4.55], 21, [0.0, -3.1, 4.55]), "night",
     [("pruitt_n", PR_WIN, 0, SMILE, {"lean": 4}), ("dad_n", DAD_WIN, 0, SMILE, {"lean": 4})], pl=1.0, pk=0.8, fill=0.4, rain=True)
S("S28b", "L28.2", cam([0.0, -2.2, 4.55], [0.0, 0.0, 4.55], 32, [0.0, -1.9, 4.55]), "night", keep=("pruitt_n", "dad_n"),
  pl=1.0, pk=0.8, fill=0.4, rain=True)
lean("L29.1", "main", 7.2, 3.2)
S("S29", "L29", cam([0.0, -7.5, 4.0], [0.0, 0.0, 4.4], 24, [0.0, -6.6, 4.1]), "night", keep=("pruitt_n", "dad_n"), pl=1.0, pk=1.0,
  fill=0.2, rain=True)
cue("L30", "hold", p=True, d=True)
show("S30", "L30", cam([0.0, -3.4, 4.5], [0.0, 0.0, 4.55], 22, [0.0, -3.0, 4.55]), "night",
     [("pruitt_n", PR_WIN, -35, WARM, {"arms": [90, 0], "lean": 3}), ("dad_n", DAD_WIN, 35, WARM, {"arms": [0, 90], "lean": 8})],
     pl=1.0, pk=0.8, fill=0.4, rain=True)
cue("L31", "hold", p=False, d=False)
lean("L31", "main", 8.5, 1.6)
show("S31", "L31", cam([0.0, -4.7, 1.7], [0.0, -1.6, 1.55], 22, [0.0, -4.2, 1.7]), "day",
     [("dad", (*YARD_D, 0), 0, ANG, {}), ("pruitt", (*YARD_P, 0), 0, ANG, {})], fill=0.7)
DAD_UP = feet("o", 0.4, 0.4, F2)
show("S32", "L32", cam(add(DAD_UP, (-0.3, -2.6, 1.4)), add(DAD_UP, (0.2, 0, 1.4)), 30, add(DAD_UP, (-0.2, -2.2, 1.45))), "day",
     [("dad", DAD_UP, 0, "neutral", {"lean": 5})], fill=0.5, hl=0.5)
show("S33", "L33", cam([-1.4, -4.2, 1.7], [-2.0, -1.8, 1.6], 34, [-1.5, -3.6, 1.7]), "day",
     [("me", (-2.0, -1.8, 0), 0, "wide", {})], fill=0.7)
raw("me", "L33.1", pos=[-2.0, -1.8, 0], expr="laugh")
cue("L34", "notebig", on=True, pos=[3.3, -1.45, 1.3], scale=1.0)
show("S34a", "L34", cam([3.3, -2.05, 1.3], [3.3, -1.45, 1.3], 34), "day", [], fill=0.9)
show("S34b", "L34.1", cam([3.2, -3.3, 1.75], [3.3, -1.0, 1.65], 32, [3.2, -2.8, 1.75]), "day",
     [("pruitt", (3.3, -1.0, 0), 0, SMILE, {})], fill=0.7)
cue("L34.1", "notebig", on=False, pos=[0, 0, -9])
raw("pruitt", "L34.1+0.35", pos=[3.3, -1.0, 0], expr="soft", blend=0.15)
raw("pruitt", "L34.1+0.75", pos=[3.3, -1.0, 0], expr=SMILE, blend=0.15)
show("S35", "L35", cam([0.0, -9.0, 0.7], [0.0, 0.0, 5.0], 22, [0.0, -8.4, 0.9], [0.0, 0.0, 5.3]), "day", [])
show("S36", "L36", cam([0.55, -4.6, 1.75], [0.0, -1.6, 1.6], 26, [0.45, -4.1, 1.75]), "day",
     [("dad", (*YARD_D, 0), 0, ANG, {}), ("pruitt", (*YARD_P, 0), 0, SMILE, {})], fill=0.7)
show("S37", "L37", cam([0.0, -3.4, 1.7], [-0.55, -1.6, 1.38], 34, [0.0, -3.0, 1.7], [-0.55, -1.6, 1.38]), "day",
     [("dad", (-0.55, -1.6, 0), 0, SHEEP, {"arms": [0, 0], "side": [0, 0]})], fill=0.8)
cue("L37.2", "shush", on=True)
cue("L38", "shush", on=False)

# =========================================================================================== 05 L38-L43
gate_latch = [-0.1, -4.86, 0.5]
show("S38a", "L38", cam([-0.6, -5.5, 0.52], gate_latch, 42, [-0.45, -5.3, 0.52]), "day", [], fill=0.9)
show("S38b", "L38.1", cam([-0.1, -7.4, 1.6], [-0.2, -4.6, 1.6], 30, [-0.1, -7.0, 1.6]), "day",
     [("me", (-0.5, -4.7, 0), 0, SMILE, {"arms": [0, 0]}), ("dad", (-0.55, -1.8, 0), 0, ANG, {}),
      ("pruitt", (0.55, -1.8, 0), 0, ANG, {})], fill=0.7)
show("S39", "L39", cam(add(feet("o", 2.0, 1.6, F1), (0, 0, 1.55)), add(feet("o", 2.0, 3.85, F1), (0, 0, 1.5)), 40,
                      add(feet("o", 2.0, 2.0, F1), (0, 0, 1.55))), "night",
     [("me", feet("o", 2.0, 3.85, F1), 0, SMILE, {})], fill=0.7, kl=1.0, pk=1.0)
WIN_K = feet("o", 1.55, 0.5, F1)
show("S40", "L40", cam(add(WIN_K, (0.1, -1.7, 1.45)), add(WIN_K, (0, 0, 1.52)), 36, add(WIN_K, (0.1, -1.4, 1.5))), "day",
     [("me", WIN_K, 0, "worried", {})], fill=0.6)
lean("L41", "mint", 8.0, 0.8)
cue("L41", "tag", v="b")
S("S41a", "L41", cam([16.0, -13.0, 3.7], [-2.0, -14.5, 3.8], 22, [14.5, -13.2, 3.7], [-2.0, -14.6, 3.8]), "day", fill=0.5)
cue("L41.2", "marble", mode="step", pos=[-3.75, -0.95, 0.19], dir=[0.0, -1.0], acc=1.6)
S("S41b", "L41.2", cam([-3.75, -0.2, 0.95], [-3.75, -1.5, 0.1], 32, [-3.75, -0.5, 0.9], [-3.75, -2.5, 0.1]), "day", fill=0.9)
w_dad = feet("o", 1.12, 1.0, F1)
w_me = feet("o", 1.76, 0.5, F1)
cx = (w_dad[0] + w_me[0]) / 2
show("S42", "L42", cam([cx, -3.2, 1.65], [cx, 0.0, 1.8], 35, [cx, -2.8, 1.65]), "day", [], fill=1.0)
put("dad", "L42", w_dad, 20, "wide")
put("me", "L42", w_me, -20, "wide")
show("S43a", "L43", cam(add(WIN_K, (0.1, -1.9, 1.45)), add(WIN_K, (0, 0, 1.52)), 36, add(WIN_K, (0.1, -1.5, 1.5))), "day",
     [("me", WIN_K, 0, "worried", {})], fill=0.6)
# the loop: back to S01a's picture (Dad, cross, the tilted mug on the island)
S("S43b", "L43+0.55", cam(add(feet("o", 2.55, 1.3, F1), (0, 0, 2.15)), add(dadk, (0, 0, 1.4)), 40, add(feet("o", 2.55, 1.7, F1), (0, 0, 2.1))), "day", fill=0.7)
put("dad", "L43+0.55", dadk, 0, ANG)

# ---------------------------------------------------------------------------------------------------- story
rain_shots = [s["id"] for s in shots if s.pop("rain", False)]
look = {"fog": "#d8f0ff", "fog_density": 0.0015, "fog_start": 40.0, "sky": "#86c8ff", "exposure": 0.0,
        "flash_safe": True, "style": "closer",
        "polish": {"emph": ["L01", "L02.1", "L19", "L26", "L41"], "reveal": ["L26"], "twist": "L28",
                   "quiet": [["L28", "L30"]], "hold": [], "camera": True, "idle": True, "ease": True}}
story = {
    "slug": "ep118-two-houses",
    "title": "Our House Leans Toward HIS \U0001F3E0",
    "made_for_kids": False,
    "premise": "On our street, when neighbors fight, their houses lean toward each other until they make up. Dad and Mr. Pruitt "
               "next door have fought for forty years, and our house leans eleven feet toward his. One stormy night the "
               "upstairs windows end up a foot apart, and at two a.m. I see what really happens there.",
    "twist": "The longest lean in town is fake: Dad and Mr. Pruitt are best friends who make up every night at two a.m., "
             "passing coffee from window to window, and start a new fight every morning so the houses stay close enough "
             "to do it. The rule only counts a fight, never whether you mean it. And now the house across the street is "
             "leaning toward ours.",
    "world": "a bright steep street of narrow painted houses, ours butter yellow and Mr. Pruitt's sky blue, a hedge, a picket "
             "gate between the yards, and a rainy blue night with two lit windows a foot apart",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#4aa3ff",
    "gap": 0.12,
    "tail": LOOP,
    "min_read": 0.15,
    "fade_in": False,
    "fade_out": False,
    "homophones": {"hours": "ours", "watch": "wash"},
    "phonemes": {"pruitt": "pɹˈuɪt", "wash": "wˈɔʃ", "houses": "hˈaʊzᵻz"},
    "look": look,
    "grade": {"shadows": [-0.01, 0.0, 0.04], "highlights": [0.03, 0.01, -0.02], "saturation": 1.12, "contrast": 1.05,
              "vignette": 0.16, "bloom": 0.2, "grain": 0.008, "red_line": 0.7},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "rain_shots": rain_shots,
    "music": {"root": 43, "mode": "mixolydian", "bpm": 104, "seed": 118,
              "sections": [
                  {"at": 0, "voices": ["bubble", "pulse", "pluck_hi"], "energy": 0.55},
                  {"at": "L16", "voices": ["pulse", "pad"], "energy": 0.3},
                  {"at": "L19", "voices": ["drone", "pad"], "energy": 0.35, "mode": "minor"},
                  {"at": "L24", "voices": ["pad", "musicbox"], "energy": 0.35, "mode": "major"},
                  {"at": "L28", "voices": ["bubble", "pad", "pluck"], "energy": 0.4},
                  {"at": "L36", "voices": ["bubble", "pulse", "pluck_hi"], "energy": 0.55},
                  {"at": "L40", "voices": ["drone", "pad"], "energy": 0.3, "mode": "minor"},
                  {"at": "L43", "voices": ["bubble", "pulse", "pluck_hi"], "energy": 0.5, "mode": "mixolydian"},
              ]},
    "sound": {
        "rev": 1, "floor": "wood", "steps_db": -22,
        "ambience": [{"kind": "rain", "from": "L16", "to": "L31", "lufs": -34},
                     {"kind": "wind", "from": "L16", "to": "L19", "lufs": -42}],
        "sfx": [
            {"at": "L02.1", "kind": "creak", "db": -16, "dur": 0.9},
            {"at": "L01>-0.2", "kind": "thud", "db": -14},
            {"at": "L17", "kind": "creak", "db": -18, "dur": 1.2},
            {"at": "L21+0.15", "kind": "creak", "db": -18, "dur": 0.6},
            {"at": "L19+0.2", "kind": "thud", "db": -16},
            {"at": "L38+0.12", "kind": "latch", "db": -16},
            {"at": "L09.1+0.25", "kind": "click", "db": -24},
            {"at": "L30+0.3", "kind": "bell", "db": -26, "dur": 0.4},
            {"at": "L41.2+0.1", "kind": "click", "db": -22},
            {"at": "L40.1", "kind": "creak", "db": -16, "dur": 1.0},
            {"at": "L41+0.1", "kind": "creak", "db": -14, "dur": 0.8},
        ],
        "music_drops": [{"from": "L18>", "to": "L19"}],
    },
}
from blocky import timeline

vt = HERE.parent / "voice-timings.json"
if vt.exists():
    voice = json.loads(vt.read_text())
    _tl0 = timeline.build({"name": "ep118-two-houses", "lines": lines, "shots": [{"id": "S0"}], "gap": 0.12, "tail": LOOP,
                           "min_read": 0.15, "cast": cast}, voice)
    AT = timeline.resolver(_tl0["lines"], _tl0["duration"])
    for k in acting:
        acting[k].sort(key=lambda e: AT(e["at"]))
    cues.sort(key=lambda e: AT(e["at"]))
story["rev"] = 38
story["clip_ok"] = ["sidehair", "sidehair2"]
story["framing_ok"] = ["S13", "S03a", "S03b", "S05", "S07", "S16", "S35", "S41a"]
story["frames_ok"] = ["S01a", "S09a", "S14a", "S43b"]
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots, {len(cues)} cues")
