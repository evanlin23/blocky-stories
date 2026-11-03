"""Writes ../story.json for ep85-early-alarm ("Don't Get Up Before The ALARM", script.md, 2026-11-03).

Run from anywhere: python stories/ep85-early-alarm/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots, the acting and the cues
set.py reads, the score and the sound. Shot ids follow the script (S01 ... S71).

Places (set.py's coordinates, metres, z up). Acting yaw: 0 faces -y, 180 faces +y, 90 faces +x.
  yard: house back wall y = -1, back step (0, -1.5), the Sun asleep at (0, 7, 2.1), the shed door at (-5, 10.8)
  bed (100, 0): bed head toward +y at x = -1.5, nightstand and clock at (-0.55, 4), doorway on the +x wall (y 1.2..2.1)
  kit (140, 0): table (0.4, 2.6), Dad's chair (0.4, 3.35), counter x = -2.15; pkit (170, 0): fridge (1.7, 4.2)
  liv (200, 0): couch (0.3, 4.1); hall (230, 0): corridor x -1..1, y 0..6; shed (260, 0): winch at (0, 2.6)
  street (320, 0): houses at x = -16, -8, 0 (ours), 8 (Mr. Pruitt's), 16; fronts at y = 0, porches at y = -0.75
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
ids = [l["id"] for l in lines]
lines.insert(ids.index("L38"), {"id": "P01", "pause": 0.6, "chunks": []})     # the drop before the shed door
ids = [l["id"] for l in lines]
lines.insert(ids.index("L64a"), {"id": "P02", "pause": 0.5, "chunks": []})    # the held beat: two alarms

BED, KIT, PKIT, LIV, HALL, SHED, STR = 100, 140, 170, 200, 230, 260, 320


def at(ox):
    return lambda x, y, z=0.0: [round(ox + x, 3), round(y, 3), round(z, 3)]


B, K, PK, L, H, SH, T = at(BED), at(KIT), at(PKIT), at(LIV), at(HALL), at(SHED), at(STR)
SHA = lambda x, y, z=0.0: SH(x, y + 1.0, z)      # the winch stands 1 m deeper (set.py: the shed is 5 m deep)
Y = at(0)

# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True, "ink": "#24131f"}


def person(**kw):
    d = {"age": "adult", "skin": "#f1c9a0", "shirt": "#1f2f6a", "pattern": "solid", "pants": "#3a4a6a", "shoes": "#f4f4f2",
         "sleeves": "long", "hair": "cap", "hair_c": "#5a3a22", "face": dict(FACE)}
    d.update(kw)
    return d


cast = {
    "me": person(age="teen", shirt="#1f2f6a", pants="#8a8fd0", hair="spiky", extras=["hooddown"], extra_c="#1f2f6a",
                 height=0.97),
    "dad": person(skin="#eba283", shirt="#d9503a", pattern="plaid", pattern_c="#7a1f14", pants="#3a4a6a", hair="cap",
                  hair_c="#9a9aa2", height=1.07, collar="#fff1e2", face={**FACE, "cheeks": "#e0402f"}),
    "dadr": person(skin="#eba283", shirt="#3f6fd0", pants="#3a4a6a", hair="cap", hair_c="#9a9aa2", height=1.07,
                   extras=["coat"], extra_c="#3f6fd0", face={**FACE, "cheeks": "#e0402f"}),
    "dady": person(skin="#e8a888", shirt="#3f6fd0", pants="#3a4a6a", hair="cap", hair_c="#6a4026", height=1.07,
                   extras=["coat"], extra_c="#3f6fd0", face={**FACE, "cheeks": "#e0402f"}),
    "pruitt": person(skin="#f0c7a6", shirt="#3fae5a", pants="#6a5a4a", hair="buzz", hair_c="#f2f2f2", height=1.0,
                     extras=["glasses"]),
    "n1": person(skin="#c78f68", shirt="#ff8fb0", pants="#ff8fb0", hair="bun", hair_c="#2a1a14", extras=["coat"],
                 extra_c="#ff8fb0"),
    "n2": person(shirt="#7a5fd0", pants="#7a5fd0", hair="cap", hair_c="#2a1a14", extras=["coat"], extra_c="#7a5fd0",
                 height=1.05),
    "n3": person(skin="#e0b08a", shirt="#3fb8a8", pants="#3fb8a8", hair="swoop", hair_c="#8a4a22", extras=["coat"],
                 extra_c="#3fb8a8"),
    "mail": person(skin="#d9a679", shirt="#5aa0ff", pants="#4a5a7a", hair="cap", hair_c="#2a1a14", hat="ballcap",
                   hat_c="#3a78d8"),
}
FAR = [0, -200, 0]
keys = {k: [{"at": 0, "pos": FAR, "yaw": 0, "hidden": True, "expr": "neutral"}] for k in cast}
last = {k: FAR for k in cast}


def put(who, t, pos, yaw=None, **kw):
    keys[who].append({"at": t, "pos": last[who]})
    k = {"at": t, "pos": pos, "blend": 0.0, "hidden": False, "arms": [0, 0], "side": [0, 0], "lean": 0, "head": [0, 0], **kw}
    if yaw is not None:
        k["yaw"] = yaw
    keys[who].append(k)
    last[who] = pos


def walk(who, t, pos, **kw):
    keys[who].append({"at": t, "pos": pos, **kw})
    last[who] = pos


def hide(who, t):
    keys[who].append({"at": t, "hidden": True})


def st(who, t, **kw):
    keys[who].append({"at": t, **kw})


LIE = dict(lean=-90)
# ---- me: asleep-awake in bed (head toward +y), then the kitchen, the hall, the yard, the shed
ME_BED = B(-1.5, 2.3, 0.74)
put("me", 0, ME_BED, 0, expr="blank", **LIE)
hide("me", "L10-0.01")
put("me", "L10", K(2.9, 0.9), 270, expr="blank")
walk("me", "L10+0.5", K(1.5, 1.0), yaw=270)
st("me", "L11", expr="blank")
hide("me", "L13")
put("me", "L16-0.01", ME_BED, 0, expr="angry", **LIE)
st("me", "L17.1+0.4", expr="angry")
put("me", "L20", ME_BED, 0, expr="blank", **LIE)
st("me", "L21", expr="wide")
put("me", "L24", ME_BED, 0, expr="wide", **LIE)
put("me", "L35-0.01", H(-0.55, 2.9), 90, expr="angry")
put("me", "L36", ME_BED, 0, expr="wide", **LIE)
put("me", "L37", B(-0.45, 3.15), 0, expr="worried", arms=[0, 0])
hide("me", "P01")
put("me", "L44+0.6", Y(-0.72, 3.3), 45, expr="scared")
st("me", "L46", expr="scared")
put("me", "L47", Y(-2.8, 2.3), 180, expr="awed" if False else "wide", head=[0, -28])
st("me", "L47.2", head=[0, 0], expr="worried", blend=0.6)
put("me", "L48", Y(-1.0, 1.0), 180, expr="worried")
st("me", "L50", expr="worried")
put("me", "L51-0.01", Y(-0.9, 0.2), 180, expr="worried")
hide("me", "L51.2")
put("me", "L55.2", Y(-0.7, 3.0), 45, expr="worried")
hide("me", "L55a")
put("me", "L55a.3", Y(-0.8, 2.5), 180, expr="worried")
hide("me", "L56")
put("me", "L60", SHA(1.35, 2.6), 270, expr="angry", arms=[69, 69], lean=-12)
put("me", "L61", SHA(1.5, 2.6), 270, expr="neutral", head=[-40, 0])
st("me", "L61+0.6", head=[40, 0], blend=0.4)
st("me", "L63.1", expr="worried", head=[0, 0])
put("me", "L64", SHA(1.5, 2.6), 270, expr="smile", head=[-55, 0], arms=[46, 46])
st("me", "L64b", expr="smile")
put("me", "L65.2", SHA(1.35, 2.6), 270, expr="angry", arms=[69, 69])
st("me", "L66", expr="angry", lean=-16)
put("me", "L67-0.01", Y(-4.5, 8.0), 180, expr="awed" if False else "smile")
put("me", "L68", Y(-4.1, 10.5), 0, expr="smile")
hide("me", "L70")
put("me", "L71-0.01", B(-1.5, 2.45, 0.74), 0, expr="blank", **LIE)
hide("me", "L71.4+0.3")

# ---- Dad: kitchen table, window, bedside, couch, doorway, yard and shed (robe from the couch on)
put("dad", 0, K(0.4, 3.35, -0.25), 0, expr="delighted")
hide("dad", "L09-0.01")
put("dad", "L09", K(0.4, 3.35, -0.25), 0, expr="delighted")
st("dad", "L11", expr="smile")
hide("dad", "L12")
put("dad", "L15-0.01", K(0.0, 3.9), 180, expr="worried", head=[22, 0], lean=0)
st("dad", "L15.1", head=[-22, 0], blend=0.5)
hide("dad", "L16")
put("dad", "L16.1-0.01", B(0.0, 3.5), 90, expr="delighted", side=[75, 75])
hide("dad", "L17-0.01")
put("dad", "L17", B(-0.55, 2.6), 270, expr="delighted", arms=[74, 74])
st("dad", "L17.1", yaw=300)
hide("dad", "L18-0.01")
put("dad", "L18", L(0.3, 4.0, -0.25), 0, expr="squeeze", arms=[-57, -57])
put("dad", "L19", L(1.3, 3.9, 0.78), 90, expr="squeeze", **LIE)
hide("dad", "L20")
put("dad", "L29a", L(1.3, 3.9, 0.78), 90, expr="squeeze", **LIE)
st("dad", "L29a.2", head=[0, 0])
hide("dad", "L30")
put("dadr", "L33", L(1.3, 3.9, 0.78), 90, expr="angry", head=[-70, 0], **LIE)
hide("dadr", "L34-0.01")
put("dadr", "L34", B(2.1, 1.65), 270, expr="angry", arms=[0, 0], side=[0, 0], lean=0)
st("dadr", "L35-0.02", hidden=True)
put("dadr", "L35-0.01", H(0.55, 2.9), 270, expr="angry")
hide("dadr", "L36")
put("dadr", "L48", Y(0.0, -0.5, 0.25), 180, expr="soft", arms=[-52, -52])
st("dadr", "L49", expr="soft")
put("dadr", "L50", Y(0.55, -0.3), 180, expr="soft")
hide("dadr", "L51")
put("dadr", "L52", SHA(1.7, 2.6), 270, expr="squeeze", arms=[72, 72])
hide("dadr", "L53-0.01")
put("dady", "L53", SHA(1.7, 2.6), 270, expr="soft", arms=[72, 72])
hide("dady", "L53a")
hide("dadr", "L53a-0.01")
put("dadr", "L53a", Y(0.0, -0.6), 0, expr="squeeze", arms=[-52, -52])
walk("dadr", "L53a+0.9", Y(-4.8, 3.0), yaw=0)
walk("dadr", "L53a>", Y(-4.6, 9.8), yaw=0)
hide("dadr", "L53b")
put("dadr", "L53b-0.01", SHA(1.7, 2.6), 270, expr="squeeze", arms=[72, 72])
hide("dadr", "L53b.3")
put("dadr", "L54-0.01", L(1.3, 3.9, 0.78), 90, expr="squeeze", **LIE)
hide("dadr", "L56+1.9")
put("dadr", "L57-0.01", Y(-1.5, 2.4), 270, expr="soft", head=[0, 25])
hide("dadr", "L57+1.2")
put("dadr", "L58-0.01", SHA(-0.85, 1.9), 90, expr="smile", arms=[0, 54], head=[25, 0])
st("dadr", "L58.2", arms=[0, 40])
put("dadr", "L59", SHA(1.7, 2.6), 270, expr="squeeze", arms=[72, 72], lean=14)
st("dadr", "L59.2", lean=18)
put("dadr", "L60", SHA(-1.5, 2.2), 90, expr="squeeze", arms=[0, 0], side=[0, 0])
st("dadr", "L61", expr="squeeze")
put("dadr", "L63", SHA(-1.5, 2.2), 90, expr="soft", head=[0, 0])
put("dadr", "L64", SHA(-1.5, 2.2), 90, expr="smile", head=[0, 0])
put("dadr", "L65", SHA(-1.35, 2.5), 90, expr="soft", arms=[57, 57])
put("dadr", "L67-0.01", Y(-5.4, 10.5), 0, expr="soft")
st("dadr", "L69", expr="soft")
hide("dadr", "L70")
put("dadr", "L71-0.01", B(2.1, 1.65), 270, expr="soft", arms=[0, 0])
hide("dadr", "L71.4+0.3")

# ---- the neighbors
put("pruitt", "L04-0.01", PK(0.8, 3.2), 90, expr="neutral", arms=[63, 63])
hide("pruitt", "L05>")
put("pruitt", "L26-0.01", T(-9.1, -0.8, 0.25), 0, expr="worried", head=[0, -30])
put("n1", "L26-0.01", T(-7.9, -0.8, 0.25), 0, expr="worried", head=[0, -30])
put("n2", "L26-0.01", T(-6.7, -0.8, 0.25), 0, expr="worried", head=[0, -30])
put("n3", "L26-0.01", T(-8.5, -1.7, 0.25), 0, expr="worried", head=[0, -30])
for w in ("pruitt", "n1", "n2", "n3"):
    hide(w, "L27")
put("pruitt", "L32", T(6.3, -2.9), 180, expr="neutral", arms=[52, 52])
walk("pruitt", "L32>", T(9.6, -2.9), yaw=180)
hide("pruitt", "L33")
put("pruitt", "L55a.1-0.01", Y(7.9, 8.0), 270, expr="worried")
hide("pruitt", "L55a.2")
put("mail", "L55a.2-0.01", Y(7.7, 12.0), 270, expr="worried", arms=[0, 0])
hide("mail", "L55a.3")

acting = keys

# ---------------------------------------------------------------------------------------------------- shots
SHOTS = []


def cam(loc, tgt, lens, loc2=None, tgt2=None, lens2=None):
    if loc2 is None and tgt2 is None and lens2 is None:
        return [[0, loc, tgt, lens]]
    return [[0, loc, tgt, lens], [1, loc2 or loc, tgt2 or tgt, lens2 or lens]]


def S(sid, t, stage, sky, c, hand=0.003, **kw):
    if stage == "shed":      # the shed's winch is 1 m deeper than the camera marks were written for
        for k in c:
            k[2] = [k[2][0], k[2][1] + 1.0, k[2][2]]
    SHOTS.append({"id": sid, "at": t, "stage": stage, "sky": sky, "cam": c, "hand": hand, "step": 2, **kw})


WIN = [3.5, -0.7, 4.4]          # my upstairs window, looking over the yard
CLK = B(-0.55, 4.0, 0.76)
# -- the hook and the rule
S("S01", 0, "bed", "dark", cam(B(-0.55, 2.8, 0.8), CLK, 38, B(-0.55, 3.0, 0.78), CLK, 38), 0.001)
S("S02a", "L02", "bed", "dark", cam(B(0.9, 1.1, 1.5), B(-1.5, 3.4, 0.7), 30, B(0.7, 1.4, 1.5), B(-1.5, 3.5, 0.7), 32), 0.002)
S("S02b", "L02.1", "bed", "dark", cam(B(-1.5, 3.5, 1.9), B(-1.5, 4.0, 0.75), 34, B(-1.5, 3.6, 1.7), B(-1.5, 4.0, 0.75), 38), 0.001)
S("S03", "L03", "street", "dawn", cam(T(0, -18, 4.4), T(0, 0, 2.4), 20, T(0.6, -17, 4.4), T(0, 0, 2.4), 22))
S("S04", "L04", "pkit", "dawn", cam(PK(1.2, 0.2, 1.4), PK(1.0, 4.0, 1.3), 26, PK(1.2, 0.5, 1.4), PK(1.0, 4.0, 1.3), 28))
S("S05", "L05", "pkit", "dawn", cam(PK(1.6, 1.6, 1.3), PK(1.5, 4.0, 1.2), 32, PK(1.6, 2.0, 1.3), PK(1.5, 4.0, 1.2), 34))
S("S06", "L06", "pkit", "dawn", cam(PK(0.3, 0.4, 0.5), PK(1.2, 1.2, 0.33), 24, PK(0.5, 0.5, 0.45), PK(1.2, 1.2, 0.33), 28))
S("S07", "L07", "street", "dawn", cam(T(-4, -9, 3.5), T(-4, 0, 3.4), 24, T(-3.4, -9, 3.5), T(-4, 0, 3.4), 26))
S("S08", "L08", "street", "dawn", cam(T(-3.0, -8, 1.8), T(-1.9, 0, 1.5), 26, T(-2.6, -7, 1.7), T(-1.9, 0, 1.5), 30))
S("S09", "L09", "kit", "dawn", cam(K(0.1, 0.6, 1.3), K(0.4, 3.3, 1.1), 30, K(0.3, 1.0, 1.3), K(0.4, 3.3, 1.15), 32))
S("S10", "L10", "kit", "dawn", cam(K(-1.5, 2.0, 1.4), K(1.7, 1.0, 1.2), 24, K(-1.0, 1.9, 1.4), K(1.5, 1.0, 1.25), 26))
S("S11", "L11", "kit", "dawn", cam(K(0.4, 1.1, 1.55), K(0.4, 3.35, 1.55), 36, K(0.4, 1.4, 1.55), K(0.4, 3.35, 1.55), 40))
S("S12", "L12", "kit", "dawn", cam(K(-2.15, 1.6, 2.2), K(-2.15, 2.3, 0.95), 30, K(-2.15, 1.9, 1.9), K(-2.15, 2.3, 0.95), 30), 0.001)
S("S13", "L13", "yard", "dawn", cam(WIN, [-1.0, 11.0, 0.3], 17, [3.2, -0.7, 4.4], [-1.0, 11.0, 0.3], 18))
S("S14", "L14", "yard", "dawn", cam(WIN, [-5.0, 12.5, 7.0], 28, [3.2, -0.7, 4.6], [-5.0, 12.5, 8.0], 28))
S("S15", "L15", "kit", "dawn", cam(K(-1.7, 2.6, 1.75), K(0.0, 3.9, 1.75), 30, K(-1.4, 2.8, 1.75), K(0.0, 3.9, 1.75), 32))
S("S16a", "L16", "bed", "dawn", cam(B(0.3, 2.2, 1.3), B(-1.5, 3.9, 0.8), 34, B(0.2, 2.6, 1.2), B(-1.5, 3.9, 0.8), 38))
S("S16b", "L16.1", "bed", "peach", cam(B(1.8, 3.0, 1.6), B(-0.3, 3.9, 1.5), 30, B(1.4, 3.0, 1.6), B(-0.3, 3.9, 1.5), 32))
S("S17a", "L17", "bed", "peach", cam(B(0.9, 1.7, 1.2), B(-1.1, 2.8, 0.8), 30, B(0.7, 1.9, 1.2), B(-1.1, 2.8, 0.8), 32))
S("S17b", "L17.1", "bed", "peach", cam(B(0.3, 2.9, 1.2), B(-1.5, 4.0, 0.8), 32, B(0.2, 3.1, 1.2), B(-1.5, 4.0, 0.8), 34))
S("S18", "L18", "liv", "dawn", cam(L(0.3, 1.5, 1.5), L(0.3, 4.0, 1.4), 28, L(0.3, 1.9, 1.5), L(0.3, 4.0, 1.4), 30))
S("S19", "L19", "liv", "dawn", cam(L(0.2, 3.0, 2.7), L(0.2, 4.15, 0.6), 22, L(0.2, 3.4, 2.6), L(0.2, 4.15, 0.6), 24))
# -- the dark mornings
S("S20", "L20", "bed", "dark", cam(B(-0.55, 2.8, 0.8), CLK, 36, B(-0.45, 3.0, 0.8), CLK, 36), 0.002)
S("S21", "L21", "bed", "dark", cam(B(-0.7, 3.2, 1.35), B(-1.5, 4.0, 0.78), 42, B(-0.8, 3.4, 1.3), B(-1.5, 4.0, 0.78), 46), 0.001)
S("S22", "L22", "bed", "dark", cam(B(1.4, 0.6, 1.6), B(-1.5, 3.2, 0.65), 28, B(1.2, 1.0, 1.5), B(-1.5, 3.2, 0.65), 30))
S("S23", "L23", "bed", "dark", cam(B(-1.5, 3.3, 2.0), B(-1.5, 3.9, 0.7), 26, B(-1.5, 3.5, 1.9), B(-1.5, 3.9, 0.7), 28), 0.001)
S("S24", "L24", "bed", "dark", cam(B(0.6, 1.4, 1.6), B(-0.3, 4.3, 1.7), 26, B(0.4, 1.8, 1.6), B(-0.3, 4.3, 1.7), 28))
S("S25", "L25", "bed", "dark", cam(B(-0.5, 1.8, 1.7), B(-0.3, 4.3, 1.7), 30, B(-0.3, 2.2, 1.7), B(-0.3, 4.3, 1.7), 32))
S("S26", "L26", "street", "dark", cam(T(-8.0, -6.5, 1.6), T(-8.0, 0, 2.0), 20, T(-8.0, -5.6, 1.6), T(-8.0, 0, 2.3), 22))
S("S27", "L27", "yard", "dawn", cam(WIN, [-5.0, 12.5, 6.5], 28, [3.2, -0.7, 4.5], [-5.0, 12.5, 7.0], 28))
S("S28", "L28", "street", "dawn", cam(T(-1, -12.5, 1.7), T(0, -7, 1.0), 24, T(1, -12.5, 1.7), T(0, -7, 1.0), 24))
S("S29", "L29", "street", "dawn", cam(T(8, -2.2, 5.4), T(8, 2.0, 4.9), 34, T(8, -1.6, 5.4), T(8, 2.0, 4.9), 38))
S("S29a", "L29a", "liv", "dawn", cam(L(-1.4, 2.4, 1.4), L(-0.3, 4.15, 0.85), 28, L(-1.2, 2.6, 1.4), L(-0.3, 4.15, 0.85), 30))
S("S29b", "L29a.2", "liv", "dawn", cam(L(-0.5, 3.3, 1.6), L(-0.4, 4.15, 0.85), 40, L(-0.5, 3.5, 1.5), L(-0.4, 4.15, 0.85), 44))
S("S30", "L30", "bed", "dark", cam(B(-0.1, 3.0, 0.95), CLK, 34, B(-0.35, 3.1, 0.85), CLK, 34), 0.002)
S("S31", "L31", "yard", "dark", cam(WIN, [-1.0, 9.0, 0.2], 26, [3.2, -0.7, 4.2], [-1.0, 9.0, 0.2], 28))
S("S32", "L32", "street", "dark", cam(T(8, -8, 1.6), T(7.8, -2.0, 0.9), 26, T(8.4, -7.5, 1.6), T(8.0, -2.0, 0.9), 28))
S("S33", "L33", "liv", "dawn", cam(L(-1.5, 2.4, 1.5), L(-0.4, 4.15, 0.85), 30, L(-1.3, 2.6, 1.5), L(-0.4, 4.15, 0.85), 32))
S("S34", "L34", "bed", "dark", cam(B(-1.0, 1.4, 1.5), B(2.1, 1.65, 1.35), 26, B(-0.8, 1.45, 1.5), B(2.1, 1.65, 1.35), 28))
S("S35", "L35", "hall", "dark", cam(H(0.0, 0.3, 1.5), H(0.0, 3.0, 1.3), 26, H(0.0, 0.7, 1.5), H(0.0, 3.0, 1.3), 28))
S("S36", "L36", "bed", "dark", cam(B(-0.55, 3.2, 0.8), CLK, 34, B(-0.5, 2.8, 0.8), CLK, 34), 0.002)
S("S37", "L37", "bed", "dark", cam(B(0.9, 1.2, 1.6), B(-0.45, 3.15, 1.3), 26, B(0.7, 1.5, 1.6), B(-0.45, 3.15, 1.3), 28))
S("P01", "P01", "yard", "night", cam(Y(0.0, 3.2, 1.5), Y(0.0, -0.9, 1.2), 28, Y(0.0, 2.8, 1.5), Y(0.0, -0.9, 1.2), 28), 0.002)
# -- the yard at night
S("S38", "L38", "yard", "night", cam(Y(-6.8, 2.0, 1.4), Y(-5.0, 10.9, 1.4), 26, Y(-6.4, 3.6, 1.4), Y(-5.0, 10.9, 1.4), 26), 0.004, key=0.5)
S("S39", "L39", "yard", "night", cam(Y(-1.2, 3.2, 0.35), Y(-4.4, 10.0, 0.3), 22, Y(-1.6, 4.4, 0.4), Y(-4.4, 10.0, 0.3), 22), 0.004, key=0.5)
S("S40", "L40", "yard", "night", cam(Y(-8.0, 9.5, 0.7), Y(-1.0, 6.0, 2.4), 20, Y(-7.0, 8.4, 0.8), Y(-0.6, 6.0, 2.4), 20), 0.004, key=0.4)
S("S41", "L41", "yard", "night", cam(Y(7.5, -1.0, 2.0), Y(0.0, 7.0, 2.4), 18, Y(6.5, -0.4, 2.0), Y(0.0, 7.0, 2.4), 18), 0.004, key=0.3)
S("S42", "L42", "yard", "night", cam(Y(-4.5, 1.0, 1.7), Y(-0.8, 5.0, 2.0), 34, Y(-4.0, 1.4, 1.8), Y(-0.6, 5.0, 2.1), 36), 0.004, key=0.3)
S("S43", "L43", "yard", "night", cam(Y(5.5, 1.5, 1.5), Y(0.0, 7.0, 2.4), 24, Y(5.0, 2.0, 1.6), Y(0.0, 7.0, 2.4), 24), 0.004, key=0.3)
S("S44", "L44", "yard", "night", cam(Y(0.1, 2.3, 1.8), Y(0.05, 6.2, 1.8), 24, Y(0.05, 2.7, 1.8), Y(0.05, 6.2, 1.8), 24), 0.002, key=0.3)
S("S45", "L45", "yard", "night", cam(Y(0.0, 1.5, 1.8), Y(0.0, 4.4, 1.6), 19, Y(-1.0, 1.9, 1.5), Y(-0.05, 4.4, 1.55), 19), 0.0, key=0.3)
S("S46", "L46", "yard", "night", cam(Y(0.0, 2.5, 1.9), Y(0.0, 6.2, 1.9), 24, Y(0.0, -1.5, 2.6), Y(0.0, 6.5, 2.2), 26), 0.002, key=0.3)
S("S47", "L47", "yard", "night", cam(Y(-2.8, 5.2, 1.3), Y(-2.8, 2.3, 1.6), 30, Y(-2.8, 5.0, 1.3), Y(-2.8, 2.3, 1.7), 30), 0.003, key=0.5)
S("S48", "L48", "yard", "night", cam(Y(0.3, 3.2, 1.7), Y(0.0, -0.5, 1.9), 26, Y(0.2, 2.8, 1.7), Y(0.0, -0.5, 1.9), 28), 0.003, key=0.4)
S("S49", "L49", "yard", "night", cam(Y(0.0, 1.6, 1.9), Y(0.0, -0.5, 1.95), 34, Y(0.0, 1.9, 1.9), Y(0.0, -0.5, 1.95), 36), 0.002, key=0.4)
S("S50", "L50", "yard", "night", cam(Y(0.0, 3.4, 1.5), Y(0.0, -0.5, 1.4), 24, Y(0.0, 3.0, 1.5), Y(0.0, -0.5, 1.4), 24), 0.003, key=0.5)
S("S51", "L51", "yard", "peach", cam(Y(0.0, 3.0, 1.5), Y(-5.0, 11.0, 5.0), 24, Y(0.0, 3.0, 1.5), Y(-3.0, 9.0, 3.5), 22), 0.003)
S("S52a", "L52", "shed", "dawn", cam(SH(0.2, 0.4, 1.5), SH(1.2, 2.6, 1.2), 28, SH(0.5, 0.5, 1.5), SH(1.2, 2.6, 1.2), 30))
S("S52b", "L52.1", "shed", "dawn", cam(SH(0.8, 1.4, 2.2), SH(0.0, 2.6, 2.4), 30, SH(0.6, 1.6, 2.3), SH(0.0, 2.6, 2.5), 32))
S("S53", "L53", "shed", "dawn", cam(SH(-0.5, 0.5, 1.4), SH(1.3, 2.6, 1.4), 24, SH(-0.3, 0.7, 1.4), SH(1.3, 2.6, 1.4), 26), 0.003, key=1.6)
S("S53a", "L53a", "yard", "night", cam(WIN, [-3.0, 5.0, 0.4], 20, [3.2, -0.7, 4.3], [-3.0, 5.0, 0.4], 22))
S("S53b", "L53b", "shed", "dark", cam(SH(0.2, 0.4, 1.5), SH(1.1, 2.6, 1.3), 30, SH(0.5, 0.6, 1.5), SH(1.1, 2.6, 1.3), 32))
S("S53c", "L53b.3", "yard", "dawn", cam(WIN, [-5.0, 12.5, 6.5], 28, [3.2, -0.7, 4.5], [-5.0, 12.5, 7.0], 28))
S("S54", "L54", "bed", "dark", cam(B(1.6, 0.8, 1.5), B(-1.2, 3.2, 0.6), 28, B(1.3, 1.1, 1.4), B(-1.2, 3.2, 0.6), 30))
S("S55a", "L55", "yard", "night", cam(Y(0.0, 2.6, 1.9), Y(0.05, 6.2, 1.8), 26, Y(0.05, 2.9, 1.9), Y(0.05, 6.2, 1.8), 28), 0.003, key=0.3)
S("S55b", "L55.2", "yard", "night", cam(Y(0.6, 0.4, 1.7), Y(-0.7, 3.0, 1.55), 30, Y(0.4, 0.9, 1.7), Y(-0.7, 3.0, 1.55), 32), 0.003, key=0.4)
S("S55c", "L55a", "yard", "night", cam(Y(5.5, 1.2, 0.6), Y(0.0, 7.0, 2.0), 20, Y(5.0, 1.6, 0.8), Y(0.0, 7.0, 2.0), 20), 0.003, key=0.4)
S("S55d", "L55a.1", "yard", "night", cam(Y(4.0, 5.0, 1.5), Y(7.9, 8.0, 1.5), 28, Y(4.5, 5.5, 1.5), Y(7.9, 8.0, 1.5), 28), 0.003, key=0.5)
S("S55e", "L55a.2", "yard", "night", cam(Y(3.5, 9.5, 1.5), Y(7.7, 12.0, 1.4), 28, Y(4.0, 10.0, 1.5), Y(7.7, 12.0, 1.4), 28), 0.003, key=0.5)
S("S55f", "L55a.3", "yard", "night", cam(Y(-0.8, 0.3, 1.5), Y(0.0, 7.0, 1.9), 24, Y(-0.8, 2.2, 1.5), Y(0.0, 7.0, 1.9), 24), 0.001, key=0.4)
S("S56a", "L56", "liv", "dark", cam(L(-1.2, 1.2, 1.3), L(-0.2, 4.2, 0.9), 26, L(-0.8, 1.6, 1.3), L(-0.2, 4.2, 0.9), 28))
S("S56b", "L56.4", "bed", "dark", cam(B(-0.1, 2.4, 0.9), CLK, 36, B(-0.3, 2.6, 0.85), CLK, 36), 0.002)
S("S56c", "L56.6", "hall", "dark", cam(H(0.0, 0.8, 1.4), H(0.0, 5.9, 1.2), 30, H(0.0, 2.0, 1.4), H(0.0, 5.9, 1.2), 30))
S("S57", "L57", "yard", "night", cam(Y(-3.0, 2.4, 1.6), Y(-1.5, 2.4, 1.55), 40, Y(-2.8, 2.4, 1.6), Y(-1.5, 2.4, 1.55), 44), 0.002, key=0.6)
S("S58", "L58", "shed", "dawn", cam(SH(0.2, 0.3, 1.1), SH(-0.2, 2.2, 0.85), 30, SH(0.1, 0.9, 1.0), SH(-0.2, 2.2, 0.85), 34), 0.001)
S("S59a", "L59", "shed", "dawn", cam(SH(0.3, 0.4, 1.4), SH(1.0, 2.6, 1.2), 24, SH(0.5, 0.8, 1.4), SH(1.0, 2.6, 1.2), 26))
S("S59b", "L59.2", "shed", "dawn", cam(SH(0.3, 0.6, 1.7), SH(1.45, 2.6, 1.6), 32, SH(0.4, 0.9, 1.7), SH(1.45, 2.6, 1.6), 34), 0.002)
S("S60", "L60", "shed", "dawn", cam(SH(0.3, 0.4, 1.6), SH(1.4, 2.6, 1.3), 26, SH(0.5, 0.7, 1.6), SH(1.4, 2.6, 1.3), 28))
S("S61", "L61", "shed", "dawn", cam(SH(0.2, 1.1, 1.5), SH(1.5, 2.6, 1.5), 40, SH(0.5, 1.2, 1.5), SH(1.5, 2.6, 1.5), 44), 0.002)
S("S62", "L62", "yard", "night", cam(Y(0.0, 2.6, 1.9), Y(0.05, 6.2, 1.8), 28, Y(0.05, 2.9, 1.9), Y(0.05, 6.2, 1.8), 30), 0.002, key=0.3)
S("S63a", "L63", "shed", "dawn", cam(SH(-0.4, 1.0, 1.7), SH(-1.5, 2.2, 1.65), 44, SH(-0.5, 1.1, 1.7), SH(-1.5, 2.2, 1.65), 48), 0.002)
S("S63b", "L63.1", "shed", "dawn", cam(SH(0.7, 1.4, 1.5), SH(1.5, 2.6, 1.5), 44, SH(0.8, 1.5, 1.5), SH(1.5, 2.6, 1.5), 48), 0.002)
S("S64", "L64", "shed", "dawn", cam(SH(0.7, 1.6, 1.55), SH(1.5, 2.6, 1.5), 38, SH(0.8, 1.7, 1.55), SH(1.5, 2.6, 1.5), 42), 0.002)
S("S64a", "P02", "shed", "dawn", cam(SH(0.0, 0.0, 1.5), SH(0.0, 2.6, 1.3), 24), 0.0)
S("S64b", "L64a", "shed", "dawn", cam(SH(0.0, 0.5, 1.5), SH(0.0, 2.6, 1.3), 22, SH(0.0, 0.9, 1.5), SH(0.0, 2.6, 1.3), 24))
S("S64c", "L64b", "shed", "dawn", cam(SH(-0.3, 0.4, 2.1), SH(0.1, 2.6, 1.1), 22, SH(-0.1, 0.8, 2.0), SH(0.1, 2.6, 1.1), 24))
S("S65a", "L65", "shed", "dawn", cam(SH(-1.0, 1.1, 1.3), SH(-0.7, 2.4, 1.05), 30, SH(-0.9, 1.3, 1.3), SH(-0.7, 2.4, 1.05), 32), 0.002)
S("S65b", "L65.2", "shed", "dawn", cam(SH(2.1, 1.0, 1.4), SH(1.2, 2.6, 1.2), 26, SH(1.9, 1.5, 1.4), SH(1.2, 2.6, 1.2), 28), 0.002)
S("S66", "L66", "yard", "peach", cam(Y(6.5, -0.5, 1.6), Y(0.0, 7.0, 3.2), 20, Y(6.0, 0.0, 1.6), Y(0.0, 7.0, 4.2), 20), 0.002)
S("S67", "L67", "yard", "peach", cam(Y(2.5, 0.3, 1.4), Y(-4.0, 12.0, 8.0), 20, Y(2.5, 0.3, 1.4), Y(-5.0, 12.0, 9.5), 20), 0.002)
S("S68", "L68", "yard", "peach", cam(Y(-4.7, 6.8, 1.45), Y(-4.7, 10.5, 1.4), 26, Y(-4.7, 7.4, 1.45), Y(-4.7, 10.5, 1.4), 28), 0.002, key=1.4)
S("S68b", "L68.2", "yard", "peach", cam(Y(-4.7, 8.2, 1.6), Y(-7.6, 13.4, 4.0), 26, Y(-4.7, 8.6, 1.6), Y(-7.6, 13.4, 4.4), 26), 0.002)
S("S69", "L69", "yard", "peach", cam(Y(-4.7, 8.4, 1.55), Y(-4.75, 10.5, 1.45), 44, Y(-4.7, 8.8, 1.55), Y(-4.75, 10.5, 1.45), 48), 0.002, key=1.4)
S("S69b", "L69.2", "yard", "peach", cam(Y(-3.2, 8.6, 1.5), Y(-4.5, 10.5, 1.3), 30, Y(-3.4, 8.9, 1.5), Y(-4.5, 10.5, 1.3), 34), 0.002, key=1.4)
S("S70", "L70", "bed", "dawn", cam(B(1.45, 2.6, 1.55), B(1.45, 4.3, 1.55), 28, B(1.45, 3.0, 1.55), B(1.45, 4.3, 1.55), 30), 0.001)
S("S71", "L71", "bed", "dark", cam(B(-1.0, 1.4, 1.5), B(2.1, 1.65, 1.4), 26, B(-0.8, 1.45, 1.5), B(2.1, 1.65, 1.4), 28))
S("S71b", "L71.4", "bed", "dark", cam(B(-0.55, 2.8, 0.8), CLK, 38, B(-0.55, 3.0, 0.78), CLK, 38), 0.001)

shots = []
for i, s in enumerate(SHOTS):
    d = dict(s)
    if i == 0:
        d.pop("at")
    shots.append(d)

# ---------------------------------------------------------------------------------------------------- cues
cues = []


def cue(t, name, **kw):
    cues.append({"at": t, "name": name, **kw})


state = {"s": "5:00", "up": 0, "ring": 0, "two": 0, "big": 0}


def clock(t, dur=0.3, **kw):
    state.update(kw)
    cue(t, "clock", dur=dur, **dict(state))


clock(0, 0, ring=1)
clock("L03", ring=0)
clock("L10", 0.6, s="7:00", up=1)
clock("L20", 0.3, s="5:00", up=0, ring=1)
clock("L22", ring=0)
clock("L24", 0, s="6:00")
clock("L25", 0, s="7:00")
clock("L26", 0, s="8:00")
clock("L27", 0.6, s="9:00", up=1)
clock("L30", 0.3, s="5:00", up=0, ring=1)
clock("L31", 0.6, s="11:00", up=1, ring=0)
clock("L36", 0.3, s="5:00", up=0, ring=1)
clock("L38", ring=0)
clock("L54", ring=1)
clock("L55", ring=0)
clock("L56", ring=1)
clock("L57", ring=0)
clock("L58", 0, s="5:30")
clock("P02", 0.2, two=1, big=1)
clock("L64b", 0.3, two=0, big=0)
clock("L67", 1.0, s="5:58", up=1)
clock("L71.4+0.5", 0.0, s="5:00", up=0, ring=1)

# the Sun: below the horizon in the montage, rising over the shed from my window (L14), crooked (L27), asleep on the lawn
SKYFAR = [-27.9, 48.0, 20.0]
cue(0, "sunpos", p=[-27.9, 48.0, -14.0], s=1.0, face=0, dur=0)
cue("L14-0.3", "sunpos", p=SKYFAR, s=1.0, face=0, dur=1.7)
cue("L16", "sunpos", p=SKYFAR, s=1.0, face=0, dur=0)
cue("L26", "sunpos", p=[-27.9, 48.0, -14.0], s=1.0, face=0, dur=0)
cue("L27", "sunpos", p=[-22.0, 48.0, 12.0], s=1.0, face=0, dur=2.0)
cue("L29", "sunpos", p=[-22.0, 48.0, 12.0], s=1.0, face=0, dur=0)
cue("L30", "sunpos", p=[-27.9, 48.0, -14.0], s=1.0, face=0, dur=0)
cue("L31+0.6", "sunpos", p=[-18.0, 48.0, -4.0], s=1.0, face=0, dur=1.8)
cue("L32", "sunpos", p=[-27.9, 48.0, -14.0], s=1.0, face=0, dur=0)
cue("L36", "sunpos", p=[0.0, 7.0, 2.1], s=1.0, face=1, dur=0)
cue("L43", "sunpos", p=[0.0, 7.0, 2.1], s=1.05, face=1, dur=0.7)
cue("L43+0.8", "sunpos", p=[0.0, 7.0, 2.1], s=1.0, face=1, dur=0.7)
cue("L51-0.02", "sunpos", p=[-24.6, 48.0, 17.0], s=1.0, face=0, dur=0)
cue("L51", "sunpos", p=[-24.6, 48.0, 17.0], s=1.0, face=0, dur=0)
cue("L51+0.4", "sunpos", p=[0.0, 7.0, 2.1], s=1.0, face=1, dur=3.2)
cue("L53b.1", "sunpos", p=[0.0, 7.0, 2.1], s=1.0, face=1, dur=0)
cue("L53b.3", "sunpos", p=[-22.0, 48.0, 8.0], s=1.0, face=0, dur=0)
cue("L53b.3+0.1", "sunpos", p=[-22.0, 48.0, 12.0], s=1.0, face=0, dur=1.2)
cue("L54", "sunpos", p=[0.0, 7.0, 2.1], s=1.0, face=1, dur=0)
cue("L66", "sunpos", p=[0.0, 7.0, 5.0], s=1.0, face=1, dur=1.0)
cue("L67", "sunpos", p=[-26.7, 48.0, 24.0], s=1.0, face=0, dur=3.4)
cue("L70", "sunpos", p=[-26.7, 48.0, 24.0], s=1.0, face=0, dur=0)
# the lid, and the Sun's own glow (a 1.5 s ramp, never a flicker)
cue(0, "eye", v=0, dur=0)
cue("L44", "eye", v=1.0, dur=1.3)
cue("L46+0.3", "eye", v=0.55, dur=0.45)
cue("L46+0.9", "eye", v=1.0, dur=0.45)
cue("L55-0.01", "eye", v=0.75, dur=0.0)
cue("L51", "eye", v=0.0, dur=0.0)
cue("L51+3.4", "eye", v=0.0, dur=0.0)
cue("L53b.1", "eye", v=1.0, dur=0.0)
cue("L55", "eye", v=0.8, dur=0.0)
cue(0, "glow", v=1.0, dur=0)
cue("L44", "glow", v=1.7, dur=1.5)
cue("L51", "glow", v=1.5, dur=0)
# rope
cue(0, "rope", mode="slack")
cue("L14", "rope", mode="taut")
cue("L26", "rope", mode="slack")
cue("L27", "rope", mode="taut")
cue("L30", "rope", mode="slack")
cue("L53b.3", "rope", mode="taut")
cue("L54", "rope", mode="slack")
cue("L66-0.2", "rope", mode="taut")
cue("L70+1", "rope", mode="taut")
cue(0, "tight", v=0, dur=0)
cue("L52.1", "tight", v=0, dur=0)
cue("L52.3", "tight", v=1, dur=0.6)
cue("L53b", "tight", v=0, dur=0)
cue("L65", "tight", v=0, dur=0)
cue("L66", "tight", v=1, dur=0.8)
# fridge, crank, curtains, bed, street, car
cue(0, "fridge", v=0, dur=0)
cue("L04+0.2", "fridge", v=1, dur=0.5)
cue("L05", "fridge", v=0, dur=0.7)
cue(0, "crank", v=0, dur=0)
cue("L53b", "crank", v=0.6, dur=2.4)
cue("L59.2", "crank", v=0.6, dur=0)
cue("L65.2", "crank", v=1.8, dur=2.0)
cue(0, "curtain", v=0, dur=0)
cue("L16.1", "curtain", v=1, dur=0.5)
cue("L18", "curtain", v=1, dur=0)
cue("L20", "curtain", v=0, dur=0)
cue(0, "blanket", v=0, dur=0)
cue("L17", "blanket", v=1, dur=0.6)
cue("L18", "blanket", v=0, dur=0)
cue(0, "pillow", v=0, dur=0)
cue("L17.1", "pillow", v=1, dur=0.4)
cue("L18", "pillow", v=0, dur=0)
cue(0, "street", lit="ours")
cue("L26", "street", lit="all")
cue("L28", "street", lit="ours")
cue("L32", "street", lit="all")
cue(0, "car", x=-20, dur=0)
cue("L28-0.05", "car", x=-9, dur=0)
cue("L28", "car", x=9, dur=1.9)
cue("L29", "car", x=-20, dur=0)

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L01.3+0.55", "kind": "bell", "db": -14, "dur": 0.3},                     # the alarm's chirp, cut short, on "up"
    {"at": "L01.3+0.55", "kind": "hit", "db": -9, "dur": 0.7},                       # and the sub swell under it
    {"at": "L05+0.55", "kind": "latch", "db": -16, "dur": 0.2},                      # the fridge closes
    {"at": "L20", "kind": "bell", "db": -24, "dur": 0.4},                            # muffled through a pillow
    {"at": "L30", "kind": "bell", "db": -24, "dur": 0.4},
    {"at": "L38", "kind": "creak", "db": -14, "dur": 1.0},                           # the shed door
    {"at": "L43", "kind": "hit", "db": -22, "dur": 0.9},                             # one slow warm breath
    {"at": "L44+0.2", "kind": "hit", "db": -14, "dur": 1.2},                         # the eye opens
    {"at": "L65.2", "kind": "click", "db": -20, "dur": 0.1},                         # the winch ratchet, wooden and low
    {"at": "L65.2+0.7", "kind": "click", "db": -20, "dur": 0.1},
    {"at": "L66+0.1", "kind": "click", "db": -20, "dur": 0.1},
    {"at": "L67", "kind": "riser", "db": -16, "dur": 1.6},
]

story = {
    "slug": "ep85-early-alarm",
    "title": "Don't Get Up Before The ALARM",
    "made_for_kids": False,
    "premise": "In our town, if your alarm rings an hour early you lie still until it is light; my dad is always up first, and when his back goes out my alarm rings at five and the sun does not come up until nine.",
    "twist": "The sun does not rise: every night it comes down to sleep in our backyard, and every morning someone who has seen it has to wake it and winch it back up. For thirty years that was my dad, and now it takes two of us.",
    "world": "a peach and lavender suburban dawn: a backyard with a round bare patch, a barn-red shed with a pulley on its roof and a winch inside, a rope across the lawn to a garage-sized glowing sleeping sun",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffb000",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "look": {"style": "closer", "fog": "#cdb8e8", "fog_density": 0.0, "fog_start": 8.0, "sky": "#f4c7d6",
             "sky_strength": 1.4, "exposure": 0.0, "flash_safe": True,
             "polish": {"reveal": ["L46"], "twist": "L46", "quiet": [["L68", "L69"]],
                        "sway": ["S38", "S39", "S40", "S42", "S43", "S44", "S46"], "hold": ["S64a"]}},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.01, -0.02], "saturation": 1.12, "contrast": 1.05,
              "vignette": 0.22, "bloom": 0.25, "grain": 0.009},
    "clip_ok": ["S17b/bed.pillow"],
    "asr_forgive": ["it's", "in", "pruitt", "five fifty eight"],
    "phonemes": {"Pruitt": "pɹˈuːɪt"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 46, "mode": "major", "bpm": 84, "seed": 85,
              "sections": [
                  {"at": 0, "voices": ["pad", "pulse"], "energy": 0.35},
                  {"at": "L20", "voices": ["drone", "pulse"], "energy": 0.3},
                  {"at": "L38", "voices": ["drone"], "energy": 0.55},
                  {"at": "L59", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L64b", "voices": ["pad", "choir"], "energy": 0.65},
                  {"at": "L68", "voices": ["pad"], "energy": 0.35},
              ]},
    "sound": {"floor": "wood", "steps_db": -22, "rev": 1,
              "ambience": [{"kind": "room", "from": 0, "to": "end", "lufs": -38},
                           {"kind": "crickets", "from": "L36", "to": "L51", "lufs": -34}],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "P01>", "keep": ["creak"]}, {"from": "P02", "to": "P02>"}]},
}
story["rev"] = 5
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
