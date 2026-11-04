"""Writes ../story.json for `ep94-today-again` (batch 9a, script.md 2026-11-03).

Run from anywhere: python stories/ep94-today-again/generator/make_story.py
The words are in lines.json next to this file. The cast, the shots and their cameras, the acting, the cues set.py
reads, the score and the sound are all here.

Places (metres; z = 0 is the floor everywhere; a character facing -y has yaw 0, +x 90, +y 180, -x -90):
  THE BAKERY   x -4..4, y 0..7. Front wall at y 0 (to -0.3): door at x = -2.6, wall clock at x = -0.7, window x 0.5..3.5.
               Counter along y 4.3 (x -3.6..2.6), me behind it at (1.0, 5.3). Back door at x = 3.0, y = 7. Alley beyond.
  THE STREET   sidewalk y -3..-0.3, road y -3..-9, houses opposite.
  THE YARD     x 6..22, y 0..13 behind the hedge at x 5.6; cake table at (13, 6); Okafor's ladder at x 4.3, y 0.1.
  GARDEN (60,0)   KITCHEN (100,0)   BEDROOM (140,0)   PRINT NOOK (180,0)
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
LOOP = 0.25
GAP = 0.12
_RR = re.compile(r"^(?P<id>[LP]\d\d)\.(?P<c>\d)(?P<rest>.*)$")


def R(ref):
    return ref


# ---------------------------------------------------------------------------------------------------- cast
def person(skin, shirt, pants, hair="cap", hair_c="#2a1d15", shoes="#2a2a30", eyes="round", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": shoes,
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "face": {"eyes": eyes, "brows": True, "ink": "#24131f"}}
    d.update(kw)
    return d


cast = {
    # me: the baker at the counter: curly black block hair, a pistachio apron over a white T-shirt, jeans
    "me": person("#e7b48c", "#fbfbf6", "#3d5a8a", "mop", "#1a1512", shoes="#f4f0e8", sleeves="short",
                 extras=["apron"], extra_c="#a8e07a"),
    # Mom: a curly gray bun, a coral cardigan, a big watch (set.py adds it)
    "mom": person("#f0c6a4", "#ff8a73", "#5d6f9c", "bun", "#b9bcc6", shoes="#8a5a3c", eyes="lashes", collar="#fff3dc"),
    "pearl": person("#8a5a3c", "#4a86e8", "#2f5ba8", "long", "#1d140f", shoes="#f4f0e8", eyes="lashes",
                    hat="ballcap", hat_c="#2f6fd6"),
    "oka": person("#a8704a", "#58b368", "#6a5a48", "buzz", "#ececec", shoes="#3a2a20", pattern="knit", pattern_c="#4a9c5a"),
    "lund": person("#e0b48c", "#f2b84b", "#4a5a7a", "swoop", "#6a4a2a", shoes="#3a3a44"),
    "dunn": person("#f1c9a0", "#b69be0", "#7a6a9a", "bun", "#d9d9e2", shoes="#8a7a9a", eyes="lashes", extras=["apron", "glasses"], extra_c="#fff3dc"),
}
NEIGH = [
    ("#d9a27a", "#ff8fc7", "#3a5aa6", "spiky", "#2a1d15", "round"), ("#f1c9a0", "#7cc6ff", "#2a2d3a", "long", "#8a4a22", "lashes"),
    ("#8a5a3c", "#ffd95a", "#3a3d4a", "cap", "#1a1410", "round"), ("#e0b48c", "#3fb6a8", "#d9d2c0", "bun", "#c0c0c8", "lashes"),
    ("#a8704a", "#ff9e6b", "#2a3a5a", "swoop", "#3a2418", "round"), ("#f1c9a0", "#b69be0", "#3a3d44", "cap", "#d9b86a", "lashes"),
]
for i, (sk, sh, pa, ha, hc, ey) in enumerate(NEIGH):
    cast[f"n{i}"] = person(sk, sh, pa, ha, hc, eyes=ey)

# ---------------------------------------------------------------------------------------------------- helpers
LINE_NO = {ln["id"]: i + 1 for i, ln in enumerate(lines)}
_REF = re.compile(r"^(?P<id>[LP]\d\d)(?:\.(?P<c>\d))?(?P<tail>>)?(?P<o>[+-]\d+(?:\.\d+)?)?$")


def tkey(ref):
    if isinstance(ref, (int, float)):
        return float(ref)
    m = _REF.match(ref)
    base = LINE_NO[m.group("id")]
    return base * 100 + int(m.group("c") or 0) * 12 + (99 if m.group("tail") else 0) + float(m.group("o") or 0)


def fmt(a):
    return round(a, 3) if isinstance(a, (int, float)) else a


acting = {w: [] for w in cast}
cues = []
shown = {w: True for w in cast}
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}


def raw(who, at, **kw):
    acting[who].append({"at": fmt(at), **kw})


def put(who, at, pos, yaw=0, expr="neutral", **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": fmt(at), "pos": prev})
    keys.append({"at": fmt(at), "pos": list(pos), "blend": 0, **NEUTRAL, "hidden": False, "yaw": yaw, "expr": expr, **kw})
    shown[who] = True


def hide(who, at):
    if shown[who]:
        acting[who].append({"at": fmt(at), "hidden": True, "blend": 0})
        shown[who] = False


def walk(who, at, pos, **kw):
    raw(who, at, pos=list(pos), **kw)


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


shots = []


def S(at, cam, who=None, tod=None, note="", step=2, hand=0.006, follow=None):
    """A shot. cam = (loc, tgt, lens) or (loc, tgt, lens, loc2, tgt2, lens2) for a move. who = {name: (pos, yaw, expr, kw)}."""
    who = who or {}
    for name in cast:
        if name in who:
            spec = who[name]
            pos, yaw = spec[0], spec[1]
            expr = spec[2] if len(spec) > 2 else "neutral"
            kw = spec[3] if len(spec) > 3 else {}
            put(name, at, pos, yaw, expr, **kw)
        else:
            hide(name, at)
    wl = lambda L: round(L * 0.78, 1) if L >= 40 else L   # close-ups a touch wider: a face at about a third of the frame
    if len(cam) == 3:
        keys = [[0, list(cam[0]), list(cam[1]), wl(cam[2])]]
    else:
        keys = [[0, list(cam[0]), list(cam[1]), wl(cam[2])], [1, list(cam[3]), list(cam[4]), wl(cam[5])]]
    shots.append({"at": at, "cam": keys, "step": step, "hand": hand, "note": note, "follow": follow})
    return len(shots)


def X(x, y, z=0.0):
    return [x, y, z]


# ---- stage constants
ME = (1.0, 5.3)
TBL = (13.0, 6.0)                # the yard's cake table
BADGE = [("L01", 5), ("L13", 1), ("L14", 2), ("L15", 3), ("L17", 1), ("L18", 3), ("L20", 4), ("L25.2", 5)]
for _a, _n in BADGE:
    cue(_a, "badge", n=_n)
cue(0, "clock", v=[9, 2])
cue(0, "rain", on=False)
cue("L25", "rain", on=False)

# =========================================================================================== 01 the hook, L01
S(0, ((-0.8, 3.7, 2.2), (-0.8, 0, 2.05), 40, (-0.8, 2.9, 2.2), (-0.8, 0, 2.05), 40),
  note="close on the wall clock at 9:02, the calendar inset x5 top-left; push in")
cue("L01.1-0.1", "rain", on=True)
S("L01.1-0.1", ((1.5, 1.7, 1.75), (2.0, 0, 1.95), 32, (1.7, 1.4, 1.8), (2.0, 0, 1.95), 32),
  note="the window close: thin rain streaks on the glass, the street bright and dry behind")
S("L01.2-0.2", ((0.4, 3.0, 1.6), (1.0, 5.3, 1.55), 50, (0.55, 3.2, 1.6), (1.0, 5.3, 1.55), 50),
  who={"me": (ME, 0, "worried", {"head": [20, 0], "arms": [30, 30]})},
  note="my face by 1.4 s, uneasy, looking at the window")
S("L01.3-0.1", ((1.4, 1.5, 1.7), (2.1, 0, 1.9), 34, (1.6, 1.2, 1.75), (2.1, 0, 1.9), 34),
  note="close on the streaming glass, the sunny street behind. Hit on BETTER")

# =========================================================================================== 02 the rule, L02 to L03
S("L02", ((1.5, 3.0, 1.6), (1.0, 5.3, 1.5), 34, (1.35, 3.2, 1.6), (1.0, 5.3, 1.5), 36),
  who={"me": (ME, 0, "worried", {"head": [25, 0], "arms": [30, 30]})},
  note="me behind the counter in my apron, uneasy, looking at the rain")
S("L02.2", ((1.0, 2.3, 1.2), (2.3, 0, 2.2), 26, (1.4, 2.0, 1.1), (2.3, 0, 2.3), 26), note="rain running down the glass, low")
S("L02.4", ((0.5, 2.9, 1.6), (1.0, 5.3, 1.55), 46), who={"me": (ME, 0, "worried", {"head": [0, 0], "arms": [40, 0]})},
  note="me, on AGAIN")
S("L03", ((0.1, 3.2, 1.6), (1.0, 5.3, 1.55), 52, (0.5, 3.4, 1.6), (1.0, 5.3, 1.55), 52),
  who={"me": (ME, 0, "wide", {"arms": [0, 0]})}, note="close on my face: only YOU remember")

# =========================================================================================== 03 the montage, L04 to L06
G0 = 60.0
LUND = (G0, 3.0)
GUESTS = {f"n{i}": (X(G0 - 3.2 + i * 1.1 + (i % 2) * 0.4, 6.2 + (i % 3) * 0.7), 150 + i * 14, "polite", {"arms": [70, 0]}) for i in range(5)}
S("L04", ((G0 + 1.2, -2.2, 1.7), (G0 - 0.5, 4.2, 1.3), 26, (G0 + 0.6, -1.6, 1.7), (G0 - 0.3, 4.2, 1.3), 26),
  who={"lund": (X(G0 - 0.5, 3.2), 0, "grin", {"arms": [70, 70]}), **GUESTS},
  note="a garden party: Mr. Lund carrying a tall white wedding cake")
cue("L04", "wcake", mode="hand")
cue("L04", "wtilt", v=[0])
S("L04.2", ((G0 - 0.4, 0.6, 1.5), (G0 - 0.5, 3.1, 1.5), 34, (G0 - 0.4, 0.9, 1.5), (G0 - 0.5, 3.1, 1.5), 34),
  who={"lund": (X(G0 - 0.5, 3.0), 0, "scared", {"arms": [72, 72]})}, note="close: the cake tipping, cut before it lands")
cue("L04.2", "wtilt", v=[0])
cue("L04.2+0.55", "wtilt", v=[34])
cue("L04.3-0.02", "wtilt", v=[34])
S("L04.3", ((G0 + 2.8, -0.2, 1.5), (G0 - 0.3, 3.4, 1.4), 28, (G0 + 2.4, 0.1, 1.5), (G0 - 0.3, 3.4, 1.4), 28),
  who={"lund": (X(G0 - 0.5, 3.6), 0, "neutral", {"arms": [72, 72]}), **GUESTS},
  note="Saturday again: Mr. Lund carrying it very slowly, the guests none the wiser")
cue("L04.3", "wtilt", v=[0])
cue("L05", "wcake", mode="hide")
walk("lund", "L04.3", X(G0 - 0.5, 3.6))
walk("lund", "L05-0.1", X(G0 - 0.5, 2.1))
K0 = 100.0
S("L05", ((K0 + 0.5, 0.5, 1.5), (K0, 2.7, 1.2), 34, (K0 + 0.2, 0.9, 1.4), (K0, 2.7, 1.1), 34),
  who={"dunn": (X(K0, 3.7), 0, "worried", {"arms": [60, 60]})},
  note="Mrs. Dunn's toaster puffing a soft grey cloud")
cue("L05", "toast", n="burnt")
cue("L05+0.1", "puff", on=True)
raw("dunn", "L05.1", arms=[100, 30], expr="scared", blend=0.2)
raw("dunn", "L05.1+0.35", arms=[60, 100], blend=0.2)
cue("L05.2-0.1", "puff", on=False)
cue("L05.2-0.1", "toast", n="gold")
S("L05.2", ((K0 + 0.9, 0.7, 1.45), (K0 - 0.1, 2.8, 1.2), 34, (K0 + 0.5, 1.1, 1.4), (K0 - 0.1, 2.8, 1.2), 34),
  who={"dunn": (X(K0, 3.7), 0, "smirk", {"arms": [50, 50]})}, note="perfect golden toast, Mrs. Dunn smug")
S("L06", ((-1.0, -9.5, 1.5), (0.5, -1.0, 1.6), 22, (0.0, -8.0, 1.4), (0.5, -1.0, 1.6), 22),
  who={"n0": (X(-5.5, -1.7), 90, "neutral", {}), "n1": (X(-3.8, -1.9), 90, "neutral", {}), "n2": (X(5.5, -2.0), -90, "neutral", {}),
       "n3": (X(2.2, -1.6), -90, "neutral", {})},
  note="a sunny street, neighbors strolling, oblivious")
walk("n0", "L06", X(-5.5, -1.7))
walk("n0", "L06.1+0.2", X(-1.5, -1.7))
walk("n1", "L06", X(-3.8, -1.9))
walk("n1", "L06.1+0.2", X(0.0, -1.9))
walk("n2", "L06", X(5.5, -2.0))
walk("n2", "L06.1+0.2", X(1.5, -2.0))
walk("n3", "L06", X(2.2, -1.6))
walk("n3", "L06.1+0.2", X(-1.8, -1.6))
S("L06.1+0.2", ((-1.2, -5.0, 1.3), (-0.2, -1.8, 1.5), 34, (-0.2, -4.6, 1.3), (-1.2, -1.8, 1.5), 34),
  who={"n0": (X(-3.6, -1.7), 90, "neutral", {}), "n1": (X(-2.0, -1.9), 90, "neutral", {}), "n2": (X(3.0, -2.0), -90, "neutral", {})},
  note="close on a pair strolling past, not noticing")
walk("n0", "L06.1+0.2", X(-3.6, -1.7))
walk("n0", "L06>", X(-0.4, -1.7))
walk("n1", "L06.1+0.2", X(-2.0, -1.9))
walk("n1", "L06>", X(1.0, -1.9))
walk("n2", "L06.1+0.2", X(3.0, -2.0))
walk("n2", "L06>", X(0.4, -2.0))

# =========================================================================================== 04 me and the birthday, L07 to L09
S("L07", ((2.3, 2.6, 1.55), (0.3, 5.3, 1.3), 30, (1.9, 2.8, 1.55), (0.5, 5.3, 1.3), 30),
  who={"me": ((1.0, 5.3), 0, "neutral", {"arms": [50, 50], "head": [15, -8]})},
  note="inside the bakery: pink walls, the case of cakes, me boxing a muffin")
raw("me", "L07+0.2", arms=[75, 75], blend=0.3)
raw("me", "L07.1", arms=[45, 45], blend=0.3)
S("L07.1+0.2", ((-3.3, 2.4, 1.0), (-1.9, 4.3, 1.1), 30, (-3.0, 2.5, 1.0), (-1.9, 4.3, 1.1), 30),
  note="the glass case of cakes and muffins")
S("L07.3", ((-1.1, 1.9, 1.5), (-2.6, 0.2, 2.5), 28, (-1.4, 1.8, 1.55), (-2.6, 0.2, 2.5), 28),
  who={"n0": (X(-2.6, -0.9), 180, "neutral", {})}, note="the bell over the door jingles, a customer coming in")
cue("L07.3", "bell")
walk("n0", "L07.3", X(-2.6, -0.9))
walk("n0", "L07.3+0.5", X(-2.6, 1.5))
S("L08", ((0.0, 2.9, 1.55), (1.0, 5.3, 1.45), 46), who={"me": (ME, 0, "hopeful", {"arms": [60, 0], "head": [-10, -8]})},
  note="me by the register, hopeful, a candle in my hand")
cue("L08", "candle", on=True)
S("L08.2", ((2.3, 2.3, 1.45), (2.1, 3.7, 1.05), 30, (2.15, 2.6, 1.4), (2.1, 3.7, 1.05), 30),
  who={"me": (ME, 0, "hopeful", {"arms": [70, 0]})}, note="the candle muffin; two pink tally strokes on the brass counter edge (lore, held)")
S("L09+0.4", ((2.3, 3.2, 1.5), (1.4, 5.3, 1.5), 48, (2.0, 3.3, 1.5), (1.4, 5.3, 1.5), 48),
  who={"me": ((1.4, 5.3), 0, "sad-smile", {"arms": [55, 0], "head": [-30, 4]})},
  note="me, deflated, then blowing out my own candle")
raw("me", "L09.1-0.05", head=[0, 10], blend=0.3)
cue("L09.1+0.3", "candle", on=False)
raw("me", "L09.1+0.3", expr="shut", blend=0.1)

# =========================================================================================== 05 the rain, L10 to L11
S("L10", ((-0.8, 2.6, 2.6), (-0.8, 0, 2.55), 36, (-0.8, 1.9, 2.5), (-0.8, 0, 2.5), 36), note="the clock at 9:02, its second hand")
cue("L10.2-0.02", "rain", on=False)
S("L10.2", ((1.2, 1.6, 1.4), (1.8, 0, 1.7), 40, (1.4, 1.3, 1.5), (1.8, 0, 1.8), 40), note="rain starting on the window, close")
cue("L10.2+0.1", "rain", on=True)
S("L11", ((-4.8, -3.4, 1.35), (2.6, -0.6, 1.9), 22, (-3.4, -3.1, 1.4), (2.6, -0.6, 1.9), 22),
  who={"n2": (X(2.6, -1.6), -90, "neutral", {})},
  note="from the sidewalk: the whole street sunny and dry, rain only down the bakery window (plant)")
walk("n2", "L11", X(2.6, -1.6))
walk("n2", "L11>", X(-3.2, -1.6))
S("L11.1+0.2", ((0.2, -3.6, 1.4), (2.0, 0, 1.9), 28, (1.0, -3.0, 1.6), (2.0, 0, 2.0), 28),
  note="close on the streaming window, dry pavement under it")

# =========================================================================================== 06 Pearl, L12 to L15
DOOR = -2.6
S("L12", ((-1.0, 2.6, 1.6), (-0.4, 0, 2.5), 26), note="the clock reads 9:15")
cue("L12", "clock", v=[9, 15])
S("L12.1", ((-1.2, 2.2, 1.5), (DOOR, -1.4, 1.45), 30, (-1.6, 1.8, 1.5), (DOOR, -1.4, 1.45), 30),
  who={"pearl": (X(DOOR, -2.2), 180, "grin", {"arms": [20, 20]})},
  note="Pearl at the door with her mail bag, cheery")
walk("pearl", "L12.1+0.1", X(DOOR, -2.2))
walk("pearl", "L12.3", X(DOOR, -0.9))
cue("L12.1", "fdoor", v=[85], dur=0.0)
S("L12.3", ((0.2, 2.6, 1.45), (DOOR, 0.3, 1.3), 30, (-0.2, 2.5, 1.45), (DOOR, 0.5, 1.3), 30),
  who={"pearl": (X(DOOR, -0.9), 180, "grin", {})}, note="she comes in, the bell jingles")
walk("pearl", "L12.3", X(DOOR, -0.9))
walk("pearl", "L12>", X(DOOR + 0.3, 1.6))
cue("L12.3", "bell")
# the first today: she trips
cue("L13", "glit", n=1)
S("L13", ((-0.4, 2.7, 1.3), (DOOR, 0.5, 1.0), 28, (-0.7, 2.4, 1.3), (DOOR, 0.5, 1.0), 28),
  who={"pearl": (X(DOOR, -0.9), 180, "grin", {"arms": [10, 10]})},
  note="Pearl catching her toe on the mat and grabbing the door frame, letters fanning out")
walk("pearl", "L13", X(DOOR, -0.9))
walk("pearl", "L13.1-0.2", X(DOOR, 0.7))
raw("pearl", "L13.1-0.2", lean=0, arms=[10, 10])
raw("pearl", "L13.1+0.1", lean=28, arms=[100, 60], expr="scared", blend=0.18)
raw("pearl", "L13.1+0.5", lean=6, arms=[40, 30], expr="worried", blend=0.4)
cue("L13.1+0.1", "letters")
# the second: she steps over it
cue("L14", "glit", n=2)
S("L14", ((-0.1, 3.5, 1.55), (-2.4, 0.3, 1.1), 22, (-0.4, 3.3, 1.55), (-2.4, 0.5, 1.1), 22),
  who={"pearl": (X(DOOR, -1.0), 180, "grin", {"arms": [8, 8]})},
  note="the second today: Pearl approaching the door")
cue("L14", "letters_off")
cue("L14", "clock", v=[9, 15])
walk("pearl", "L14", X(DOOR, -1.0))
walk("pearl", "L14.1", X(DOOR, 0.1))
S("L14.1+0.15", ((0.5, 2.7, 1.5), (-2.5, 0.5, 1.15), 20, (0.2, 2.6, 1.5), (-2.5, 0.5, 1.15), 20),
  who={"pearl": (X(DOOR, 0.1), 180, "smile", {"arms": [8, 8]})},
  note="Pearl stepping neatly over the mat, her hands with more glitter")
walk("pearl", "L14.1+0.15", X(DOOR, 0.1))
walk("pearl", "L14.1+0.7", X(DOOR + 0.1, 1.5))
raw("pearl", "L14.1+0.15", arms=[16, 16])
# the third: she holds the door
cue("L15", "glit", n=3)
S("L15", ((0.6, 3.4, 1.5), (-2.4, 0.5, 1.2), 20, (0.3, 3.2, 1.5), (-2.4, 0.5, 1.2), 20),
  who={"pearl": (X(-2.0, 0.9), 150, "smile", {"arms": [10, 85]})},
  note="the third today: Pearl holding the door, her hands sparkling")
S("L15.2", ((0.6, 3.2, 1.5), (-2.5, 0.2, 1.25), 20, (0.3, 3.0, 1.5), (-2.5, 0.2, 1.25), 20),
  who={"pearl": (X(-2.0, 0.9), 150, "grin", {"arms": [10, 85]}), "lund": (X(DOOR - 0.1, -1.3), 180, "grin", {})},
  note="Mr. Lund coming in, both smiling")
cue("L15.2", "bell")
walk("lund", "L15.2", X(DOOR - 0.1, -1.3))
walk("lund", "L15>", X(DOOR - 0.3, 0.2))

# =========================================================================================== 07 Mom, L16 to L19
MOMC = (-0.4, 3.3)
cue("L16", "clock", v=[9, 30])
S("L16", ((1.0, 5.6, 1.7), (-1.3, 1.0, 1.5), 28, (0.7, 5.4, 1.7), (-1.0, 1.8, 1.5), 28),
  who={"mom": (X(-2.4, 0.2), 150, "smile", {"arms": [10, 10]})},
  note="the bell jingles; my mom comes in, face to camera")
cue("L16", "bell")
walk("mom", "L16", X(-2.4, 0.2))
walk("mom", "L16.1-0.1", X(*MOMC))
raw("mom", "L16.1-0.1", yaw=180, blend=0.3)
S("L16.1", ((-1.9, 6.4, 1.7), (-0.4, 3.3, 1.55), 36, (-1.7, 6.2, 1.7), (-0.4, 3.3, 1.55), 36),
  who={"mom": (X(*MOMC), 180, "smile", {"arms": [70, 10]}), "me": ((1.6, 5.4), 0, "hopeful", {})},
  note="Mom at the counter (curly bun, coral cardigan), pointing at a muffin, breezy")
cue("L16.1", "muff", v=[-0.6, 4.3, 1.07])
S("L16.3", ((-0.5, 4.0, 1.9), (-0.5, 4.4, 1.07), 40, (-0.4, 3.8, 1.8), (-0.5, 4.4, 1.07), 40),
  who={"mom": (X(*MOMC), 180, "smile", {"arms": [30, 10]})},
  note="the muffin going into a pink bag")
cue("L16.3", "muff", v=[-0.6, 4.3, 1.07])
cue("L16.3+0.35", "muff", v=[-0.5, 4.4, 1.4])
cue("L16.3+0.8", "muff", v=[-0.5, 4.4, 1.12])
cue("L16>", "muff", v=[-0.5, 4.4, 1.12])
# x1: she knocks her coffee over
S("L17", ((0.9, 5.8, 1.75), (MOMC[0], 3.3, 1.6), 30, (0.6, 5.6, 1.75), (MOMC[0], 3.3, 1.6), 30),
  who={"mom": (X(*MOMC), 180, "smile", {"arms": [70, 40]})},
  note="the first today: Mom at the counter with her coffee")
cue("L17", "cup", mode="hand", tilt=0)
cue("L17", "coffee_off")
cue("L17", "clock", v=[9, 30])
S("L17.1+0.1", ((0.9, 5.7, 1.9), (-0.3, 3.7, 1.3), 28, (0.6, 5.4, 1.85), (-0.3, 3.7, 1.3), 28),
  who={"mom": (X(*MOMC), 180, "scared", {"arms": [100, 30]})},
  note="her elbow tipping the cup, a brown splash on the counter")
cue("L17.1+0.1", "cup", mode="hand", tilt=0)
cue("L17.1+0.3", "cup", mode="hand", tilt=70)
cue("L17.1+0.32", "spill")
raw("mom", "L17.1+0.1", arms=[100, 30], blend=0.1)
S("L17.3", ((0.5, 5.2, 1.9), (-0.3, 3.9, 1.2), 30, (0.2, 5.0, 1.85), (-0.3, 3.9, 1.2), 30),
  who={"mom": (X(*MOMC), 180, "worried", {"arms": [100, 30]})}, note="the brown puddle on the counter")
cue("L18-0.02", "spill_off")
S("L18", ((1.0, 6.2, 1.5), (-0.4, 3.5, 1.4), 34, (0.7, 6.0, 1.5), (-0.4, 3.5, 1.4), 34),
  who={"mom": (X(*MOMC), 180, "grin", {"arms": [70, 40]})},
  note="the third today: the cup caught, upright in her hand")
cue("L18", "cup", mode="hand", tilt=60)
cue("L18+0.15", "cup", mode="hand", tilt=0)
raw("mom", "L18.1+0.1", expr="delighted", blend=0.2)
S("L19", ((2.5, 5.9, 1.4), (-0.3, 3.3, 1.5), 34, (2.0, 5.9, 1.4), (-0.3, 3.3, 1.5), 34),
  who={"mom": (X(*MOMC), 180, "smile", {"arms": [60, 20]})}, note="Mom paying, breezy")
cue("L19", "cup", mode="hide")
S("L19.2", ((0.0, 3.0, 1.55), (1.2, 5.3, 1.4), 46), who={"me": ((1.2, 5.3), 0, "sad-smile", {"head": [-20, -8]})},
  note="me sad behind the till")

# =========================================================================================== 08 I say it out loud, L20 to L21
S("L20", ((0.9, 3.0, 1.55), (1.0, 5.3, 1.45), 44, (1.0, 2.8, 1.5), (1.0, 5.3, 1.45), 44),
  who={"me": (ME, 0, "angry", {"lean": 14, "arms": [65, 65]})}, note="me leaning over the counter, fed up")
S("L20.2", ((1.9, 3.0, 1.6), (1.0, 5.3, 1.55), 48), who={"me": (ME, 0, "scared", {"lean": 6, "arms": [120, 120]})},
  note="me, close, shouting it out loud")
S("L20.3+0.35", ((0.6, 5.6, 1.6), (0.0, 2.2, 1.5), 28, (0.8, 5.5, 1.6), (0.0, 2.2, 1.5), 28),
  who={"n0": (X(-1.0, 1.8), 0, "worried", {"arms": [80, 0]}), "n1": (X(0.4, 2.2), 0, "worried", {"head": [0, 0]}),
       "n2": (X(1.5, 1.7), 0, "worried", {}), "mom": (X(*MOMC), 180, "worried", {"arms": [0, 20]})},
  note="the customers glancing up")
raw("n0", "L20.3+0.4", head=[-30, 0], blend=0.3)
raw("n1", "L20.3+0.55", head=[25, 0], blend=0.3)
raw("n2", "L20.3+0.35", head=[-20, 0], blend=0.3)
S("L21.1", ((0.3, 3.0, 1.6), (1.0, 5.3, 1.55), 50, (0.5, 3.3, 1.6), (1.0, 5.3, 1.55), 50),
  who={"me": (ME, 0, "worried", {"arms": [30, 30]})}, note="me, close, to the whole room")

# =========================================================================================== 09 the room freezes, P01 and L22 to L25
# each customer stands behind a stand-up table, facing the counter (and the camera behind it), mid-bite or mid-sip
FROZEN = {
    "n0": (X(-1.9, 0.9), 188, "neutral", {"arms": [100, 0]}), "n1": (X(-0.7, 1.7), 172, "neutral", {"arms": [85, 85]}),
    "n2": (X(0.5, 1.0), 184, "neutral", {"arms": [100, 0]}), "n3": (X(2.4, 1.1), 168, "neutral", {"arms": [80, 80]}),
    "n4": (X(1.1, 2.5), 192, "neutral", {"arms": [100, 0]}), "n5": (X(-2.1, 2.5), 176, "neutral", {"arms": [85, 85]}),
}
MOMF = (X(1.7, 0.35), 180, "neutral", {"arms": [80, 0]})
S("P01", ((0.4, 6.8, 1.8), (0.4, 1.4, 0.95), 12, (0.4, 6.4, 1.8), (0.4, 1.4, 0.95), 12),
  who={**FROZEN, "mom": MOMF},
  note="the drop: the whole bakery frozen mid-bite, a coffee pour hanging in the air")
cue("P01", "pour", on=True)
S("L22", ((0.4, 6.8, 1.85), (0.4, 1.4, 0.95), 12, (0.4, 6.3, 1.8), (0.4, 1.4, 0.95), 12),
  who={**FROZEN, "mom": MOMF},
  note="six customers frozen mid-bite and mid-sip, Mom serious at the back")
cue("L22", "pour", on=True)
S("L22.1", ((-2.0, 4.6, 1.7), (-0.7, 1.7, 1.5), 36, (-1.8, 4.3, 1.7), (-0.7, 1.7, 1.5), 36),
  who={**FROZEN}, note="a frozen bite, close")
cue("L22.1+0.45", "pour", on=False)
S("L22.1+0.5", ((0.4, 6.7, 1.8), (0.4, 1.4, 0.95), 12, (0.4, 6.2, 1.8), (0.4, 1.4, 0.95), 12),
  who={**FROZEN, "mom": MOMF},
  note="every head turning together")
for _n, _y in (("n0", 81), ("n1", 60), ("n2", 61), ("n3", 302), ("n4", 41), ("n5", 54)):
    raw(_n, "L22.1+0.7", head=[0, 0], yaw=_y, blend=0.35)
S("L23.1", ((-0.3, 3.3, 1.5), (1.3, 0.8, 1.45), 40, (-0.1, 3.0, 1.5), (1.3, 0.8, 1.45), 40),
  who={"mom": (X(1.3, 0.8), 180, "neutral", {"arms": [80, 0]})}, note="Mom at the window table, serious")
S("L24", ((0.1, 2.6, 1.65), (1.3, 0.8, 1.55), 52, (0.9, 2.1, 1.5), (1.65, 0.9, 1.4), 72),
  who={"mom": (X(1.3, 0.8), 180, "neutral", {"arms": [75, 0]})},
  note="Mom, close, serious, glancing at her watch (cover frame)")
raw("mom", "L24+0.15", expr="neutral", arms=[100, 0], head=[0, 14], blend=0.3)
cue("L24.1", "tick")
S("L24.2", ((0.5, 6.7, 1.8), (0.4, 1.4, 0.95), 12, (0.4, 6.2, 1.8), (0.4, 1.4, 0.95), 12),
  who={**{k: (v[0], 180, "neutral", {"arms": [30, 30]}) for k, v in FROZEN.items()}},
  note="every customer nodding and quietly putting their cups down")
for _n in ("n0", "n1", "n2", "n3", "n4", "n5"):
    raw(_n, "L24.2+0.1", head=[0, 14], arms=[30, 30], blend=0.35)
    raw(_n, "L24.2+0.6", head=[0, -2], blend=0.35)
S("L24.3", ((0.1, 2.5, 1.65), (1.3, 0.8, 1.6), 46), who={"mom": (X(1.3, 0.8), 180, "angry", {"arms": [30, 0]})},
  note="Mom, determined: from the top")
# L25: next morning
BR = 140.0
cue("L25", "alarm", v=[7, 0])
S("L25", ((BR + 2.0, 1.2, 1.1), (BR + 3.2, 4.3, 0.95), 36, (BR + 2.4, 1.5, 1.1), (BR + 3.2, 4.3, 0.95), 36),
  note="my alarm clock at 7:00")
S("L25.2", ((BR + 2.5, 1.0, 1.4), (BR + 3.0, 4.3, 1.1), 36), note="the calendar inset: 12, and the badge clicks to x5")
cue("L25.2-0.3", "tagbig", v=1, dur=0.4)
cue("L25.2+1.0", "tagbig", v=0, dur=0.4)

# =========================================================================================== 10 today five, L26 to L29
cue("L26", "clock", v=[9, 1])
cue("L26", "ladder1", on=True)
cue("L26", "pour", on=False)
S("L26", ((3.2, 1.5, 1.5), (1.4, 5.3, 1.45), 30, (2.8, 1.8, 1.5), (1.2, 5.3, 1.45), 30),
  who={"me": ((1.4, 5.3), 0, "worried", {"head": [-25, 0], "arms": [25, 25]})}, note="me looking around, then slipping off")
walk("me", "L26+0.3", (1.4, 5.3))
walk("me", "L26.2", (2.2, 5.9))
S("L26.2", ((-0.8, 2.8, 2.6), (-0.8, 0, 2.5), 36, (-0.8, 2.1, 2.5), (-0.8, 0, 2.5), 36), note="the wall clock at 9:01, the inset x5")
S("L26.3", ((1.2, 3.4, 1.5), (3.0, 7.2, 1.2), 26, (1.5, 3.8, 1.5), (3.0, 7.2, 1.2), 26),
  who={"me": ((2.2, 5.9), 180, "worried", {})}, note="me slipping out the back door into a bright alley")
walk("me", "L26.3", (2.2, 5.9))
walk("me", "L26.3+0.25", (3.0, 6.0))
walk("me", "L26.3+0.5", (3.0, 7.8))
walk("me", "L26>", (3.0, 9.2))
cue("L26.3", "bdoor", v=[0], dur=0)
cue("L26.3+0.3", "bdoor", v=[95], dur=0.5)
S("L27", ((2.0, -4.2, 1.6), (3.85, -0.9, 3.9), 32, (2.3, -3.8, 1.8), (3.85, -0.9, 3.95), 32),
  who={"oka": (X(3.85, -0.95, 2.9), -28, "grin", {"arms": [15, 25], "side": [0, 75], "head": [12, 0]})},
  note="low angle up the bakery wall: Mr. Okafor on a tall ladder, focused")
S("L27.3", ((6.6, -3.0, 1.0), (4.0, -0.9, 0.5), 28, (5.8, -2.8, 1.0), (4.0, -0.9, 0.5), 28),
  note="the ladder's feet in a flower bed")
S("L27.4", ((2.2, -4.0, 1.9), (3.9, -0.7, 3.9), 30, (2.6, -3.6, 2.2), (3.9, -0.7, 3.95), 30),
  who={"oka": (X(3.85, -0.95, 2.9), -28, "grin", {"arms": [15, 25], "side": [0, 75], "head": [12, 0]})}, note="up by our roof")
cue("L28-0.2", "hose", on=True)
cue("L28-0.2", "rain", on=True)
S("L28", ((1.2, -3.6, 3.0), (3.0, -0.4, 3.3), 30, (1.7, -3.4, 2.9), (3.0, -0.4, 3.2), 30),
  who={"oka": (X(3.85, -0.95, 2.9), -28, "grin", {"arms": [15, 25], "side": [0, 75], "head": [12, 0]})},
  note="the hose spraying down over the window's top edge, a little rainbow in the spray")
cue("L28", "rainbow", on=True)
S("L28.2", ((-0.5, -5.0, 1.5), (2.0, -0.3, 2.2), 22, (0.3, -4.6, 1.6), (2.0, -0.3, 2.2), 22),
  who={"oka": (X(3.85, -0.95, 2.9), -28, "grin", {"arms": [15, 25], "side": [0, 75], "head": [12, 0]})},
  note="the spray streaming down the window")
cue("L28.2+0.6", "rainbow", on=False)
cue("L29-0.1", "wet", on=True)
cue("L29>", "hose", on=False)
cue("L30", "wet", on=False)
S("L29", ((2.0, -3.3, 1.55), (2.6, -0.8, 1.6), 46, (2.2, -3.1, 1.6), (2.6, -0.8, 1.6), 46),
  who={"me": (X(2.6, -0.8), 0, "wide", {"head": [0, 16], "arms": [20, 20]})}, note="me, stunned, wet hair")

# =========================================================================================== 11 behind the hedge, L30 to L32
CROUCH = {"lean": 22}
RING = [(-3.0, 0.0), (-2.2, -2.3), (0.0, -3.2), (2.2, -2.3), (3.0, 0.0), (2.2, 2.4), (0.0, 3.3), (-2.2, 2.4)]
NAMES9 = ["n0", "n1", "n2", "n3", "n4", "n5", "lund", "dunn", "pearl"]


def crowd(pose=None, z=0.0, yaw=-90, expr="grin"):
    d = {}
    for i, nm in enumerate(NAMES9[:8]):
        rx, ry = RING[i]
        d[nm] = (X(TBL[0] + rx * 1.15, TBL[1] + ry * 1.15, z), yaw, expr, dict(pose or {}))
    d["pearl"] = (X(TBL[0] + 1.2, TBL[1] + 3.9, z), 180, expr, dict(pose or {}))
    return d


CROWD_C = crowd({"lean": 22}, z=-0.55, expr="neutral")
S("L30", ((4.9, 4.2, 1.55), (12.0, 6.2, 1.0), 30, (4.9, 5.0, 1.55), (12.0, 6.2, 1.0), 30),
  who={**CROWD_C, "me": (X(4.8, 5.9), -90, "worried", {})},
  note="peeking past a hedge: a crowd of neighbors crouched in a yard")
S("L30.2", ((5.0, 8.4, 1.6), (13.0, 5.0, 0.9), 22, (5.0, 7.6, 1.6), (13.0, 5.0, 0.9), 22),
  who={**CROWD_C}, note="the whole block, crouched")
cue("L30", "balloons", on=True)
S("L31-0.1", ((8.3, 6.0, 2.2), (13.0, 6.0, 3.0), 28, (9.4, 6.0, 2.0), (13.0, 6.0, 3.1), 28),
  who={**CROWD_C}, note="balloons bobbing over the table")
S("L31.1", ((10.1, 4.6, 1.5), (13.0, 6.0, 1.3), 40, (10.6, 4.9, 1.5), (13.0, 6.0, 1.3), 40),
  who={**CROWD_C}, note="the big three-layer cake")
S("L32", ((14.3, 8.6, 1.9), (13.0, 9.9, 1.5), 36, (14.0, 8.2, 1.8), (13.0, 9.9, 1.5), 36),
  who={"pearl": (X(13.0, 10.4), 0, "grin", {"arms": [100, 40]})}, note="Pearl shaking a glitter jar over the cake")
cue("L32", "jar", on=True)
S("L32.2", ((13.1, 8.6, 1.7), (13.0, 9.9, 1.1), 36, (12.8, 8.9, 1.5), (13.0, 9.9, 1.05), 36),
  who={"pearl": (X(13.0, 10.4), 0, "grin", {"arms": [100, 40]})}, note="glitter falling on the cake")
S("L32.4", ((12.6, 8.5, 1.45), (13.0, 9.9, 1.25), 62, (12.9, 8.9, 1.4), (13.0, 9.9, 1.25), 62),
  who={"pearl": (X(13.0, 10.4), 0, "smile", {"arms": [85, 60]})}, note="close on her hands, sparkling")
cue("L32.4", "jar", on=False)
cue("L32.4", "glit", n=4)

# =========================================================================================== 12 it isn't a do-over, L33 to L37
S("L33", ((6.4, 5.4, 1.5), (5.0, 6.0, 1.45), 40), who={"me": (X(4.8, 6.0), 90, "worried", {"head": [0, 0]})},
  note="me behind the hedge, thinking")
S("L33.1+0.28", ((-0.4, 2.7, 1.3), (DOOR, 0.5, 1.0), 28, (-0.7, 2.4, 1.3), (DOOR, 0.5, 1.0), 28),
  who={"pearl": (X(DOOR, -0.9), 180, "grin", {"arms": [10, 10]})},
  note="a callback to the first today: Pearl tripping on the mat")
cue("L33.1+0.28", "glit", n=1)
walk("pearl", "L33.1+0.28", X(DOOR, -0.9))
walk("pearl", "L33.2-0.1", X(DOOR, 0.7))
raw("pearl", "L33.2-0.1", lean=0, arms=[10, 10])
raw("pearl", "L33.2+0.2", lean=28, arms=[100, 60], expr="scared", blend=0.18)
cue("L33.2+0.2", "letters")
S("L33.3", ((G0 + 2.8, -0.2, 1.5), (G0 - 0.3, 3.4, 1.4), 28, (G0 + 2.4, 0.1, 1.5), (G0 - 0.3, 3.4, 1.4), 28),
  who={"lund": (X(G0 - 0.5, 3.6), 0, "neutral", {"arms": [72, 72]}), **GUESTS},
  note="a callback to Mr. Lund's second Saturday: the guests none the wiser")
cue("L33.3", "wcake", mode="hand")
S("L33.5", ((2.0, 6.0, 1.7), (-0.4, 3.4, 1.5), 28, (1.6, 5.8, 1.7), (-0.4, 3.4, 1.5), 28),
  who={"mom": (X(*MOMC), 180, "smile", {"arms": [70, 40]}), "pearl": (X(-1.9, 1.4), 180, "smile", {}), "lund": (X(0.9, 1.7), 180, "smile", {}),
       "n0": (X(-2.8, 2.0), 0, "smile", {})},
  note="everyone else does the day the same: the bakery, again")
cue("L33.5", "wcake", mode="hide")
cue("L33.5", "cup", mode="hand", tilt=0)
S("L34", ((1.6, 2.0, 1.4), (-0.4, 3.6, 1.2), 32, (1.4, 2.2, 1.4), (-0.4, 3.6, 1.2), 32),
  who={"mom": (X(*MOMC), 180, "scared", {"arms": [100, 30]})},
  note="a callback to the first coffee: the cup tipping")
cue("L34", "cup", mode="hand", tilt=0)
cue("L34+0.2", "cup", mode="hand", tilt=70)
S("L35", ((1.0, 6.2, 1.5), (-0.4, 3.5, 1.4), 34, (0.7, 6.0, 1.5), (-0.4, 3.5, 1.4), 34),
  who={"mom": (X(*MOMC), 180, "grin", {"arms": [70, 40]})}, note="a callback to the third: the cup caught")
cue("L35", "cup", mode="hand", tilt=60)
cue("L35+0.12", "cup", mode="hand", tilt=0)
S("L36", ((6.6, 5.3, 1.5), (5.0, 6.0, 1.5), 48), who={"me": (X(4.8, 6.0), 90, "wide", {})},
  note="me behind the hedge, realizing")
cue("L36", "cup", mode="hide")
cue("L36", "clip", mode="hide")
cue("L36.1+0.15", "clip", mode="chest")
cue("L36.1+0.15", "clipscale", v=[2.2])
cue("L36.1+0.2", "ladder2", on=True)
S("L36.1+0.2", ((17.8, 13.0, 4.6), (11.2, 6.8, 1.6), 22, (17.2, 12.4, 4.2), (11.2, 6.8, 1.6), 22),
  who={**crowd({"arms": [20, 20]}, expr="grin"), "mom": (X(11.7, 8.3), 137, "neutral", {"arms": [70, 70]}),
       "oka": (X(7.4, 5.4, 2.45), 90, "grin", {"arms": [150, 150]})},
  note="the reveal picture, overhead: the whole block on tape marks around the cake, Mom in the middle with a clipboard, Okafor on his ladder")
S37 = len(shots)

# =========================================================================================== 13 the reveal said, L38 to L43
cue("L38", "tape", on=True)
cue("L38", "ladder2", on=False)
cue("L38", "clipscale", v=[1.5])
S("L38", ((7.0, 6.0, 1.6), (13.0, 6.0, 1.5), 20, (7.6, 6.0, 1.6), (13.0, 6.0, 1.5), 22),
  who={**crowd({"arms": [150, 150], "head": [0, 8]}, expr="wide")},
  note="neighbors practicing their surprised faces, arms up")
raw("n0", "L38+0.3", arms=[170, 170], blend=0.2)
raw("n1", "L38+0.5", arms=[160, 160], blend=0.2)
S("L38.2", ((G0 + 1.3, 1.2, 1.55), (G0 + 0.3, 3.0, 1.4), 40),
  who={"lund": (X(G0 + 0.3, 3.0), 0, "focused" if False else "neutral", {"arms": [80, 20]})},
  note="Mr. Lund with a stopwatch")
cue("L38.2", "stopw", on=True)
S("L38.4", ((6.4, 5.3, 1.6), (5.0, 6.0, 1.5), 46, (6.2, 5.6, 1.6), (5.0, 6.0, 1.5), 46),
  who={"me": (X(4.8, 6.0), 90, "worried", {"head": [0, 0]})}, note="me, taking it in")
cue("L38.4", "stopw", on=False)
CLIP_AT = (TBL[0] - 1.2, TBL[1] + 1.8)
MF = (-0.866, -0.5)


def MC(d, side=0.3, h=1.55):
    """A camera spot d metres in front of Mom (she faces yaw -60), side metres to her left."""
    return (CLIP_AT[0] + d * MF[0] + side * 0.5, CLIP_AT[1] + d * MF[1] - side * 0.866, h)


MOMP = (X(*CLIP_AT), -60)
cue("L39", "clip", mode="hand")
S("L39", (MC(1.9, 0.25, 1.45), (CLIP_AT[0] + 0.8 * MF[0], CLIP_AT[1] + 0.8 * MF[1], 1.2), 30,
          MC(1.6, 0.15, 1.4), (CLIP_AT[0] + 0.8 * MF[0], CLIP_AT[1] + 0.8 * MF[1], 1.2), 30),
  who={"mom": (*MOMP, "neutral", {"arms": [75, 75]})},
  note="close on the clipboard: three rows of glyph ticks and a doodle of my face")
S("L39.3", (MC(2.7, 0.4, 1.6), (CLIP_AT[0], CLIP_AT[1], 1.55), 46, MC(2.4, 0.2, 1.6), (CLIP_AT[0], CLIP_AT[1], 1.55), 46),
  who={"mom": (*MOMP, "sad-smile", {"arms": [85, 85]})}, note="Mom hugging the clipboard to her chest, guilty")
cue("L39.3", "clip", mode="chest")
S("L40", (MC(2.7, 0.5, 1.6), (CLIP_AT[0], CLIP_AT[1], 1.58), 50, MC(2.3, 0.3, 1.6), (CLIP_AT[0], CLIP_AT[1], 1.58), 50),
  who={"mom": (*MOMP, "angry", {"arms": [75, 75], "head": [0, -6]})}, note="Mom, determined, chewing her pen")
cue("L40", "pen", on=True)
S("L40.2", ((6.4, 5.0, 1.5), (14.0, 6.6, 1.0), 26), who={**crowd({"arms": [40, 40]}, expr="grin")},
  note="the whole block practicing, seen past the hedge")
S("L40.3", (MC(2.5, -0.5, 1.6), (CLIP_AT[0], CLIP_AT[1], 1.58), 46, MC(2.2, -0.3, 1.6), (CLIP_AT[0], CLIP_AT[1], 1.58), 46),
  who={"mom": (*MOMP, "angry", {"arms": [75, 75]})}, note="Mom, never one that worked")
cue("L40.3", "pen", on=False)
S("L41", ((6.4, 5.4, 1.5), (5.0, 6.0, 1.5), 52), who={"me": (X(4.8, 6.0), 90, "sad-smile", {"head": [0, 6]})},
  note="me, sheepish")
cue("L42", "kclock", v=[9, 30])
S("L42", ((K0 - 3.3, 3.9, 2.0), (K0, 4.5, 2.2), 24, (K0 - 3.0, 3.7, 2.0), (K0, 4.5, 2.2), 24),
  who={"n3": (X(K0, 4.3, 0.45), 270, "neutral", {"arms": [20, 120], "head": [-20, 0]})},
  note="a neighbor on a step stool turning a kitchen clock's hands back")
cue("L42.1", "kclock", v=[9, 0], dur=0.9)
cue("L42.3-0.01", "clock", v=[9, 30])
S("L42.3", ((-0.8, 2.6, 2.5), (-0.8, 0, 2.45), 36, (-0.8, 2.0, 2.4), (-0.8, 0, 2.4), 36),
  note="the bakery wall clock, its hands slid back to 9:00")
cue("L42.3+0.15", "clock", v=[9, 0], dur=0.9)
cue("L43", "alarm", v=[7, 0])
S("L43", ((BR + 0.3, 0.6, 1.5), (BR + 2.6, 3.4, 1.0), 30, (BR + 0.8, 1.6, 1.5), (BR + 2.9, 4.2, 1.0), 40),
  who={"mom": (X(BR + 0.9, 1.0), -20, "neutral", {"arms": [10, 10]})}, note="Mom tiptoeing past my bed to my alarm clock, turning it back")
walk("mom", "L43", X(BR + 0.9, 1.0))
walk("mom", "L43.1", X(BR + 2.3, 3.4))
cue("L43.1+0.2", "alarm", v=[7, 0])
cue("L43.1+0.3", "alarm", v=[6, 0], dur=0.7)
NN = 180.0
S("L43.3", ((NN - 0.9, 0.8, 1.7), (NN, 2.9, 0.95), 34, (NN - 0.6, 1.0, 1.55), (NN, 2.9, 0.95), 34),
  note="a stack of the same newspaper, still warm from a home printer")

# =========================================================================================== 14 the loop, L44 to L48
cue("L44", "clock", v=[9, 0])
S("L44", ((3.0, 5.0, 1.55), (3.0, 9.5, 1.3), 26, (3.0, 5.4, 1.55), (3.0, 9.0, 1.3), 26),
  who={"me": (X(3.0, 10.8), 0, "worried", {"head": [-30, 0]})},
  note="the bright alley: me tiptoeing back in through the back door")
cue("L44-0.5", "bdoor", v=[0])
cue("L44-0.45", "bdoor", v=[95], dur=0.2)
walk("me", "L44", X(3.0, 10.8))
walk("me", "L44.1", X(3.0, 7.6))
S("L44.3", ((1.2, 3.4, 1.5), (3.0, 6.4, 1.3), 30, (1.6, 3.6, 1.5), (3.0, 6.4, 1.3), 30),
  who={"me": (X(3.0, 7.6), 0, "worried", {"head": [25, 0], "arms": [20, 20]})}, note="in through the back door, tiptoe")
walk("me", "L44.3", X(3.0, 7.6))
walk("me", "L44>", X(1.0, 5.3))
cue("L44.3+0.5", "bdoor", v=[0], dur=0.5)
cue("L45", "clock", v=[9, 30], dur=0.6)
S("L45", ((-0.8, 2.7, 2.5), (-0.8, 0, 2.45), 36, (-0.8, 2.1, 2.4), (-0.8, 0, 2.4), 36), note="the wall clock at 9:30")
cue("L46", "ghost", on=True)
cue("L47", "ghost", on=False)
S("L46", ((-0.8, 1.4, 1.55), (-2.1, 3.86, 1.5), 28, (-1.0, 1.6, 1.55), (-2.1, 3.86, 1.5), 28),
  who={"me": ((-3.0, 2.8), 180, "wide", {"arms": [30, 30], "head": [0, 6]})},
  note="me practicing a huge surprised face in the cake case glass")
raw("me", "L46.1", expr="delighted", arms=[60, 60], blend=0.15)
cue("L47", "rain", on=True)
cue("L47-0.1", "tagbig", v=1, dur=0.4)
S("L47", ((1.0, 4.2, 1.5), (1.0, 6.0, 1.5), 40), note="the calendar inset, close: 12")
cue("L47>", "tagbig", v=0, dur=0.4)
cue("L47+0.1", "badge", n=5)
cue("L48-0.05", "rain", on=False)
cue("L48", "clock", v=[9, 2])
S("L48", ((-0.8, 3.7, 2.2), (-0.8, 0, 2.05), 40, (-0.8, 2.9, 2.2), (-0.8, 0, 2.05), 40),
  note="the clock at 9:02 and the rain starting on the window (S01's framing). Loop")
cue("L48.1", "rain", on=True)

# ---------------------------------------------------------------------------------------------------- assemble
out_shots = []
for i, d in enumerate(shots):
    sh = {"id": f"S{i + 1:02d}", "cam": d["cam"], "step": d["step"], "hand": d["hand"], "note": d["note"]}
    if i:
        sh["at"] = d["at"]
    if d["follow"]:
        sh["follow"] = d["follow"]
    out_shots.append(sh)


def key_t(k):
    return tkey(k["from"]) if "from" in k else tkey(k["at"])


for who in acting:
    ks = acting[who]
    order = sorted(range(len(ks)), key=lambda j: (key_t(ks[j]), j))
    acting[who] = [ks[j] for j in order]
acting = {w: ks for w, ks in acting.items() if ks}
cues.sort(key=lambda c: tkey(c["at"]))

story = {
    "slug": "ep94-today-again",
    "title": "Everyone's Getting BETTER At Today 🎂",
    "made_for_kids": False,
    "premise": "In my town, when your day goes wrong you get it again and only you remember. I work the morning counter at the corner bakery, today is my birthday and nobody has said so, and today has now happened five times. Each time, everybody does it a little better.",
    "twist": "It was never a do-over. A real do-over would leave everyone else repeating the day the same, but my whole block, led by Mom, is rehearsing my surprise party on me: they set every clock back overnight, print the same newspaper, and make the rain with a garden hose. I sneak back in and plan to act surprised.",
    "world": "a frosting-pink corner bakery with a pistachio counter, a sunny street outside, and a green backyard behind the hedge with a rehearsal party on tape marks",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff8fc7",
    "gap": GAP,
    "tail": LOOP,
    "fade_in": False,
    "fade_out": False,
    "rev": 6,
    "look": {"style": "closer", "fog": "#d8ecf8", "fog_density": 0.004, "fog_start": 16.0, "sky": "#8fd3ff", "sky_strength": 1.0,
             "exposure": 0.15, "hdri": "kloppenheim_06_puresky", "hdri_strength": 0.5, "hdri_rotation": 40, "flash_safe": True,
             "polish": {"emph": ["L01", "L03", "L11", "L21", "L24", "L36", "L37"], "reveal": ["L37"], "twist": "L37",
                        "hold": [f"S{S37:02d}"], "sway": [], "ones": "moving"}},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.01, -0.02], "saturation": 1.1, "contrast": 1.04,
              "vignette": 0.2, "bloom": 0.2, "grain": 0.008},
    "phonemes": {"Okafor": "Okˈɑfɔɹ"},
    "asr_forgive": ["oh two", "oh one", "nine oh two", "nine fifteen", "nine thirty", "nine oh one", "mister okafor", "work", "nobody's"],
    "cast": cast,
    "lines": lines,
    "shots": out_shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "set_moves": [],
    "music": {"root": 46, "mode": "major", "bpm": 118, "seed": 94, "sections": [
        {"at": 0, "voices": ["piano", "pulse"], "energy": 0.42},
        {"at": "L22", "voices": ["drone", "pad"], "energy": 0.4},
        {"at": "L25", "voices": ["piano", "pulse", "pad"], "energy": 0.4},
        {"at": "L26", "voices": ["pulse", "piano"], "energy": 0.34},
        {"at": "L36", "voices": ["drone"], "energy": 0.3},
        {"at": "L37", "voices": ["piano", "pulse", "pad"], "energy": 0.6},
        {"at": "L45", "voices": ["piano", "pulse"], "energy": 0.46}]},
    "sound": {
        "floor": "wood", "steps_db": -26, "rev": 6,
        "ambience": [{"kind": "rain", "from": "L10", "to": "L11>", "lufs": -38},
                     {"kind": "water", "from": "L28", "to": "L29", "lufs": -40},
                     {"kind": "rain", "from": "L47", "to": "end", "lufs": -38}],
        "sfx": [{"at": "L01.3+0.05", "kind": "ding", "pitch": 700, "fall": 0.55, "dur": 0.4, "lp": 3800, "db": -12},
                {"at": "L01.3+0.42", "kind": "ding", "pitch": 1568, "dur": 1.0, "lp": 4000, "db": -12},
                {"at": "L12.3", "kind": "ding", "pitch": 1568, "dur": 0.8, "lp": 4000, "db": -16},
                {"at": "L16", "kind": "ding", "pitch": 1568, "dur": 0.8, "lp": 4000, "db": -16},
                {"at": "L24.1", "kind": "thud", "db": -14, "dur": 0.2},
                {"at": "L13.1+0.1", "kind": "thud", "db": -16},
                {"at": "L25.2", "kind": "click", "db": -10}],
        "music_drops": [{"from": "P01", "to": "P01>"}],
    },
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False))
print(f"wrote {OUT}: {len(out_shots)} shots, {len(cues)} cues")
