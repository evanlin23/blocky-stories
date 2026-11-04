"""Writes ../story.json for "Everyone Hides When The WHISTLE Blows" (ep98-town-whistle, batch 9b).

Run from anywhere: python stories/ep98-town-whistle/generator/make_story.py
The words are in lines.json (made from script.md by mklines.py). Everything else is here: the cast, the shots and
their cameras, the acting, the cues set.py reads (steps, tag, puff, lamp, under, door, dust, kettle, cut, ladder,
leaf), the score and the sound.

World (metres, z up): the street runs along y, the pole and whistle at (0, 0) (the mouth faces -y), our white house
(-14, 3.5), Grandpa's butter house on stone piers (-14, -6, floor z 0.9, window at y -6), the Dunns' blue house
(14, 6), a cellar bulkhead at (8.2, 3.6). Our kitchen and the stairwell: x 86..100 and the wall x=100 with the
basement door at y=0; steps go +x and down (rise 0.27, run 0.28). The bakery is at x=-200, the cutaway at y=200.
Acting yaw: 0 faces -y, 180 faces +y, 90 faces +x, -90 faces -x.
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
SX, RISE, RUN = 100.0, 0.27, 0.28

# ------------------------------------------------------------------------------------------------ cast
FACE = {"eyes": "round", "brows": True, "ink": "#24131f"}


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", eyes="round", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": shoes,
         "sleeves": "short", "hair": hair, "hair_c": hair_c, "face": {**FACE, "eyes": eyes}}
    d.update(kw)
    return d


cast = {
    "me": person("#e8b88f", "#d83a34", "#d8c38a", "#f4f4f2", hair="cap", hair_c="#15100c", collar="#ffffff"),
    "dad": person("#dba27a", "#4a86d6", "#8a8f98", "#4a3a2a", hair="cap", hair_c="#8d8d90", eyes="tired"),
    "arlo": person("#ecc09a", "#3a9a5a", "#7a5a3a", "#8a5a3a", hair="cap", hair_c="#f4f4f4", pattern="knit",
                   pattern_c="#2f7f49", sleeves="long", height=0.96),
    "dunn": person("#e3a878", "#ff8a58", "#ff8a58", "#c89a70", hair="long", hair_c="#a2a2ae", eyes="lashes"),
    "mr_dunn": person("#dba27a", "#7a9a4a", "#5a5a62", "#3a3a3a", hair="buzz", hair_c="#555555"),
    "baker": person("#e8b88f", "#fafafa", "#5a4a3a", "#3a2a1a", hair="none", hat="beanie", hat_c="#fafafa",
                    extras=["apron"], extra_c="#ffffff", width=1.1),
    "mail": person("#c98f66", "#3a6ad6", "#2a4a8a", "#2a2a2a", hair="bun", hair_c="#3a2216", eyes="lashes",
                   extras=["backpack"], extra_c="#8a5a2a"),
    "t1": person("#e8b88f", "#16b8a8", "#f4f4f2", "#f4f4f2", hat="ballcap", hat_c="#16b8a8"),
    "t2": person("#b98456", "#16b8a8", "#f4f4f2", "#f4f4f2", hat="ballcap", hat_c="#16b8a8", hair="buzz"),
    "t3": person("#f0c8a0", "#16b8a8", "#f4f4f2", "#f4f4f2", hair="long", hair_c="#8a4a22", eyes="lashes"),
    "t4": person("#8a5a3a", "#16b8a8", "#f4f4f2", "#f4f4f2", hat="ballcap", hat_c="#16b8a8"),
    "n1": person("#e8b88f", "#e8a43a", "#4a5a8a", "#8a5a3a", hair="swoop", hair_c="#5a3a22"),
    "n2": person("#c98f66", "#b04a8a", "#3a3a44", "#2a2a2a", hair="bun", hair_c="#1a1210", eyes="lashes"),
    "n3": person("#f0c8a0", "#4a9ad6", "#6a5a4a", "#3a2a1a", hair="spiky", hair_c="#7a5a2a"),
}

# ------------------------------------------------------------------------------------------------ state
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {k: [{"at": 0, "hidden": True, "pos": [0, 0, 0], "blend": 0}] for k in cast}
cues = []
shots = []
NAMES = {}


def raw(who, at, **kw):
    acting[who].append({"at": at, **kw})


def put(who, at, pos, yaw=0, expr="neutral", **kw):
    """There from this instant (a cut); everything not set returns to neutral."""
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": list(pos), "blend": 0, "yaw": yaw, "expr": expr, "hidden": False, **NEUTRAL, **kw})


def walk(who, at0, pos0, at1, pos1, yaw=None, expr="neutral", **kw):
    put(who, at0, pos0, yaw if yaw is not None else 0, expr, **kw)
    raw(who, at1, pos=list(pos1))


def gone(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def steps(at, n, new=0):
    cue(at, "steps", n=n, new=new)


def tag(at, n):
    cue(at, "tag", n=n)


# ------------------------------------------------------------------------------------------------ cameras
def X(loc, tgt, lens, loc2=None, tgt2=None, lens2=None):
    ks = [[0, list(loc), list(tgt), lens]]
    if loc2 or tgt2 or lens2:
        ks.append([1, list(loc2 or loc), list(tgt2 or tgt), lens2 or lens])
    return ks


def PX(loc, tgt, lens, k=0.10, hold_tgt=True):
    """A push: the camera glides k of the way toward the target over the shot."""
    l2 = [loc[i] + (tgt[i] - loc[i]) * k for i in range(3)]
    return [[0, list(loc), list(tgt), lens], [1, l2, list(tgt), lens]]


def S(at, cam, look="day", name=None, **kw):
    sid = f"S{len(shots) + 1:02d}"
    sh = {"id": sid, "cam": cam, "look": look, **kw}
    if shots:
        sh["at"] = at
    shots.append(sh)
    if name:
        NAMES[name] = sid
    return sid


def stair(k):
    """World x, z of the top of step k."""
    return SX + RUN * (k - 0.5), -RISE * k


def ab(x, h, n=28):
    """z of a camera h above the stairs' surface at world x (the stairs start at SX; the landing is at step n)."""
    return max(-RISE * (x - SX) / RUN, -RISE * n) + h


# the whistle's mouth, the pole's foot, anchors
WM = (0.0, -0.5, 6.9)
LX, LZ = SX + RUN * 28, -RISE * 28

# ------------------------------------------------------------------------------------------------ the film
for who in cast:
    pass

# --- 01 the hook, L01 to L02
cue(0, "puff", whistle=1.0)
steps(0, 26)
tag(0, 26)
cue(0, "door", open=0.0)
cue(0, "lamp", pos=[99.9, 0.0, 0.95], off=True)
S(0, PX((0.7, -4.2, 7.0), (0, 0, 6.95), 28, 0.12), "day", name="hook", fill=0.7, hand=0.004)
walk("n1", "L01.2", (4.9, 0.6), "L02-0.3", (7.4, 3.5), expr="scared")
raw("n1", "L02+0.1", pos=[8.2, 3.6])
gone("n1", "L02+0.15")
S("L01.2", PX((3.6, -1.2, 1.5), (8.0, 3.4, 0.7), 20, 0.10), "day", fill=0.9)
S("L02", PX((1.4, -34.0, 0.55), (0, 6.0, 2.2), 22, 0.14), "day", fill=0.6)
cue("L02", "puff", whistle=0.0)

# --- 02 the montage, L03 to L06
for i, (who, y0) in enumerate((("n1", 18.0), ("n2", 15.5), ("n3", 13.0))):
    walk(who, "L03", (-4.4, y0 + 8), "L03.2+0.2", (-9.0, y0 - 2.0 + (1 if i == 0 else 0)), expr="scared")
    gone(who, "L04-0.05")
S("L03", X((-1.0, 9.0, 1.3), (-6.5, 15.0, 1.1), 20, (-1.5, 10.0, 1.3), (-6.5, 14.0, 1.1), 20), "day", fill=0.9)
put("baker", "L04", (-200.0, 0.4), 180, "wide", arms=[40, 40])
walk("baker", "L04", (-200.0, 0.5), "L04.1", (-200.0, 0.5), 180, "wide", arms=[40, 40])
raw("baker", "L04.2", pos=[-198.2, -1.5], expr="scared")
gone("baker", "L05-0.05")
S("L04", PX((-197.4, -2.6, 1.7), (-200.0, 1.6, 1.0), 20, 0.10), "in", fill=0.8, inside=1.4)
for i, who in enumerate(("t1", "t2", "t3", "t4")):
    walk(who, "L05", (-3.0 + 2.0 * i, -62.0 + (i % 2) * 1.2), "L05.2-0.1", (-3.0 + 2.0 * i + 1.0, -52.0 - i * 0.6), expr="scared")
    gone(who, "L05.2")
S("L05", PX((7.0, -46.0, 1.5), (0, -62.0, 0.9), 18, 0.10), "day", fill=0.9)
steps("L05.2", 13)
tag("L05.2", 13)
cue("L05.2", "door", open=1.0)
for i, who in enumerate(("t1", "t2", "t3", "t4")):
    ln = -0.3 + 0.2 * i
    t0 = 0.3 * i
    put(who, f"L05.2+{t0:.2f}", (98.2, ln, 0.0), 90, "scared")
    for j, k in enumerate((1, 3, 6, 9)):
        raw(who, f"L05.2+{t0 + 0.2 * (j + 1):.2f}", pos=[stair(k)[0], ln, stair(k)[1]])
    gone(who, f"L05.2+{t0 + 0.95:.2f}")
S("L05.2", PX((97.6, 0.3, 1.7), (102.4, 0.0, -1.2), 17, 0.08), "in", fill=0.9, stairl=1.5)
walk("mail", "L06", (4.6, -14.0), "L06.2", (9.9, -6.0), expr="scared")
gone("mail", "L06.2+0.25")
S("L06", PX((3.2, -16.0, 1.5), (8.6, -8.0, 1.1), 20, 0.12), "day", fill=0.9)
cue("L05.2", "puff", whistle=0.0)
steps("L06", 26)
tag("L06", 26)

# --- 03 the numbers, L07 to L10
cue("L07", "door", open=1.0)
put("me", "L07", (98.0, 0.9), 150, "worried")
raw("me", "L07.3", pos=[98.2, 0.8])
put("dad", "L07", (99.2, 0.0, 0.0), 90, "worried")
for j, k in enumerate((1, 3, 5)):
    raw("dad", f"L07+{0.45 * (j + 1):.2f}", pos=[stair(k)[0], 0.0, stair(k)[1]])
cue("L07", "lamp", pos=[99.9, 0.0, 0.95], to=[102.4, 0.0, -0.2], dur=1.3)
S("L07", PX((97.0, 3.4, 1.5), (99.0, -0.1, 1.2), 18, 0.10), "in", fill=0.9, stairl=1.4, lamp=1.2)
gone("dad", "L07.3+0.1")
tag("L07.3", 13)
for k, (dt, n) in enumerate(((0.35, 15), (0.5, 17), (0.65, 20), (0.8, 23))):
    tag(f"L07.4+{dt - 0.35:.2f}", n)
tag("L08", 24)
tag("L08.1", 26)
S("L07.3", X((97.0, 0.1, 1.5), (100.0, 0.1, 1.4), 24, (97.8, 0.1, 1.5), (100.0, 0.1, 1.4), 24), "in", fill=0.4, tagbig=3.0, name="tagbig")
put("me", "L08", (99.3, 0.0, 0.0), 90, "worried", arms=[0, 0])
S("L08", PX((107.0, 0.0, ab(107.0, 1.0)), (SX + 0.4, 0.0, 0.4), 14, 0.14), "in", fill=0.8, stairl=1.6, lamp=0.0)
cue("L08", "lamp", pos=[104.0, 0.0, -2.6])
steps("L09", 26, new=26)
S("L09", PX((106.2, -0.45, ab(106.2, 0.75)), (107.2, 0.0, -7.0), 30, 0.10), "in", fill=0.9, lamp=1.4)
steps("L10", 26)
gone("me", "L08+0.05")
put("me", "L10", (stair(9)[0], 0.0, stair(9)[1]), 90, "neutral", arms=[0, 130])
key("me", "L10.1", arms=[0, 130], head=[0, 14])
S("L10", PX((104.8, 0.0, ab(104.8, 1.5)), (stair(9)[0], 0.0, stair(9)[1] + 1.55), 26, 0.10), "in", fill=1.0, stairl=1.5, lamp=0.0)
cue("L10", "lamp", pos=[stair(7)[0] + 0.2, 0.3, stair(7)[1] + 0.2])

# --- 04 Grandpa and the house, L11 to L16
gone("me", "L11-0.05")
put("arlo", "L11", (-9.9, -3.3, 0.9), 90, "neutral")
put("dad", "L11", (-10.0, 1.2, 0.18), 90, "worried")
S("L11", X((-1.2, -0.6, 1.8), (-10.0, -1.0, 1.6), 15, (-2.2, -0.6, 1.8), (-10.0, -1.0, 1.6), 15), "day", fill=0.8, name="neighbors")
gone("dad", "L12-0.05")
gone("arlo", "L12-0.05")
S("L12", PX((-14.0, -19.0, 2.4), (-14.0, -6.0, 1.9), 18, 0.12), "day", fill=0.7)
S("L12.2", X((-14.0, -15.0, 0.35), (-14.0, -3.0, 0.5), 18, (-14.0, -11.0, 0.35), (-14.0, -3.0, 0.5), 18), "day", fill=0.5)
S("L13", PX((-9.6, -8.4, 0.55), (-11.4, -6.0, 0.4), 22, 0.12), "day", fill=0.6)
cue("L14", "kettle", on=True)
put("arlo", "L14", (-13.0, -6.2, 0.9), -90, "soft", arms=[0, 40])
S("L14", PX((-15.6, -7.7, 2.4), (-13.0, -6.2, 2.3), 21, 0.08), "in", fill=0.9, inside=1.3)
cue("L15", "kettle", on=False)
gone("arlo", "L15-0.05")
put("dad", "L15", (-9.9, -4.6, 0.9), 90, "worried", arms=[35, 35])
key("dad", "L15.2", arms=[35, 35], head=[0, -8])
S("L15", PX((-6.4, -4.2, 2.0), (-9.8, -4.8, 1.8), 22, 0.10), "day", fill=0.9)
gone("dad", "L16-0.05")
put("arlo", "L16", (-9.9, -4.6, 0.9), 90, "smirk", arms=[0, 70])
key("arlo", "L16.2", arms=[0, 90])
S("L16", PX((-6.2, -4.6, 1.9), (-9.9, -4.6, 1.7), 22, 0.12), "day", fill=0.9)

# --- 05 the pole, L17 to L23
gone("arlo", "L17-0.05")
S("L17", X((1.8, -1.8, 0.6), (0.0, 0.0, 6.3), 17, (1.2, -1.2, 0.7), (0.0, 0.0, 7.0), 17), "day", fill=0.3)
S("L18", PX((1.5, -3.2, 5.0), (0.9, 0.0, 0.6), 21, 0.10), "day", fill=0.5)
S("L18.3", PX((1.05, -1.4, 0.85), (1.05, 0.0, 0.15), 24, 0.14), "day", fill=0.6)
cue("L19", "dust", who=["n1", "n2", "dad"])
walk("n1", "L19", (8.2, 3.6), "L19.2", (5.2, 1.4), 270, "neutral")
walk("n2", "L19.1", (8.2, 18.0), "L19.3", (5.8, 16.4), 270, "neutral")
S("L19", PX((2.0, -1.2, 1.7), (7.2, 3.0, 1.1), 18, 0.10), "morning", fill=1.0)
gone("n1", "L19.3")
gone("n2", "L19.3+0.1")
put("dad", "L19.3", (-9.4, 2.6, 0.0), 90, "worried")
S("L19.3", PX((-4.6, 1.4, 1.7), (-9.4, 2.6, 1.55), 24, 0.10), "morning", fill=1.0)
cue("L20", "puff", shoulder=[-9.4, 2.1, 1.45])
S("L20", PX((-7.6, 0.2, 1.9), (-9.4, 2.3, 1.5), 34, 0.12), "morning", fill=0.8)
cue("L21", "puff", shoulder=None)
cue("L21", "dust", who=["dad"])
gone("dad", "L21-0.05")
steps("L21", 26)
put("dad", "L21", (stair(26)[0], 0.0, stair(26)[1] - 0.42), 90, "asleep", lean=18, head=[0, 20])
cue("L21", "lamp", pos=[stair(25)[0] - 0.1, 0.55, stair(25)[1] + 0.2])
cue("L21", "puff", shoulder=[stair(26)[0], 0.0, stair(26)[1] + 0.6])
S("L21", PX((stair(21)[0], -0.4, ab(stair(21)[0], 1.1, 26)), (stair(26)[0], 0.0, stair(26)[1] + 0.5), 22, 0.10), "in", fill=0.9, lamp=1.2, stairl=1.2)
gone("dad", "L22-0.05")
cue("L22", "puff", shoulder=None)
cue("L22", "dust", who=[])
put("arlo", "L22", (-9.9, -4.6, 0.9), 90, "smile")
S("L22", PX((-5.6, -5.2, 1.9), (-9.9, -4.6, 1.65), 24, 0.10), "day", fill=0.9)
gone("arlo", "L23-0.05")
put("dad", "L23", (-9.4, 0.1, 0.0), 0, "angry", arms=[85, 0])
key("dad", "L23.2", arms=[95, 0], head=[20, 0])
S("L23", X((-5.0, 0.4, 1.7), (-9.4, 0.0, 1.6), 22, (-5.6, 0.4, 1.7), (-9.4, 0.0, 1.6), 22), "day", fill=0.9, name="dadpoint")
put("arlo", "L23.1", (-9.9, -3.0, 0.9), 90, "smile")
S("L23.1", PX((-6.0, -1.0, 1.9), (-9.6, -1.2, 1.6), 20, 0.10), "day", fill=0.9)

# --- 06 Tuesday at sundown, L24 to L29
gone("dad", "L24-0.05")
gone("arlo", "L24-0.05")
cue("L24", "puff", whistle=1.0)
S("L24", PX((1.2, -3.2, 6.3), (0, 0, 6.95), 26, 0.10), "gold", fill=0.7)
cue("L25", "puff", whistle=0.0)
cue("L25", "door", open=0.0, to=1.0, dur=0.7)
walk("dad", "L25", (95.6, 3.0), "L25+1.0", (99.0, 0.15), 90, "scared")
S("L25", X((97.8, -1.7, 1.5), (99.75, 0.55, 1.4), 20, (98.2, -1.5, 1.5), (99.75, 0.55, 1.4), 20), "in", fill=1.1, name="tally")
gone("dad", "L26-0.05")
walk("me", "L26", (-9.5, 1.5), "L26+0.5", (-9.5, -0.8, 0.9), 180, "scared")
raw("me", "L26+0.95", pos=[-9.5, -2.2, 0.0])
raw("me", "L26.1+0.5", pos=[-9.7, -3.6, 0.9])
S("L26", PX((-5.4, 1.2, 1.6), (-9.5, -0.8, 0.8), 20, 0.12), "gold", fill=0.9)
gone("me", "L27-0.05")
put("arlo", "L27", (-14.0, -6.0, 0.9), 90, "smirk")
put("me", "L27.0", (-15.2, -4.4, 0.9), 70, "scared", arms=[40, 40])
S("L27", PX((-11.5, -3.6, 2.5), (-14.4, -5.4, 2.1), 17, 0.10), "gold", fill=0.8, inside=1.0)
gone("me", "L28-0.05")
gone("arlo", "L28-0.05")
S("L28", X((-12.2, -6.3, 2.1), (0.0, -4.0, 1.5), 19, (-12.0, -6.0, 2.1), (0.0, -4.0, 1.5), 19), "gold", fill=0.5, inside=0.8)
put("arlo", "L29", (-12.4, -5.4, 0.9), 90, "neutral")
put("me", "L29", (-12.4, -6.6, 0.9), 90, "worried")
S("L29", PX((-6.6, -6.0, 2.5), (-12.4, -6.0, 2.45), 30, 0.10), "gold", fill=0.5, inside=0.6)
S("P01", PX((-6.6, -6.0, 2.5), (-12.4, -6.0, 2.45), 30, 0.18), "gold", fill=0.5, inside=0.6)

# --- 07 the street is empty, L30 to L36
gone("me", "L30-0.05")
gone("arlo", "L30-0.05")
S("L30", PX((-12.0, -5.6, 2.3), (10.0, -3.0, 1.2), 22, 0.10), "gold", fill=0.5, inside=0.6)
cue("L31", "leaf", pos=[0.3, -9.0])
S("L31", PX((-2.2, -20.0, 0.42), (0.3, -8.0, 0.2), 20, 0.12), "gold", fill=0.5)
cue("L32", "leaf", off=True)
cue("L32", "puff", wells=1.0)
S("L32", PX((-5.8, -7.0, 0.9), (-10.1, 6.0, 0.35), 17, 0.10), "gold", fill=0.5)
S("L32.2", PX((-5.4, 0.2, 0.8), (-10.1, 2.6, 0.3), 24, 0.10), "gold", fill=0.5)
S("L33", PX((5.4, 12.0, 0.9), (10.1, 7.0, 0.3), 18, 0.10), "gold", fill=0.5)
cue("L34", "puff", whistle=1.0)
S("L34", PX((-1.4, -3.6, 7.9), (0, 0, 7.0), 24, 0.08), "gold", fill=0.5)
cue("L35", "puff", whistle=0.0, wells=0.0)
cue("L35", "leaf", off=True)
cue("L35", "kettle", on=True)
put("arlo", "L35", (-15.9, -6.5, 0.9), -90, "soft", arms=[55, 0])
S("L35", PX((-12.6, -8.6, 2.5), (-16.0, -6.5, 2.3), 17, 0.10), "gold", fill=0.8, inside=1.2)
put("arlo", "L36", (-14.5, -6.4, 0.9), 0, "neutral", arms=[60, 60])
put("me", "L36", (-14.5, -3.9, 0.9), 180, "worried", arms=[45, 45])
S("L36", PX((-11.4, -5.0, 2.4), (-14.5, -5.2, 2.3), 15, 0.10), "gold", fill=0.8, inside=1.2)
cue("L37", "kettle", on=False)

# --- 08 the Dunns, L37 to L42
steps("L37", 27)
tag("L37", 27)
gone("arlo", "L37-0.05")
gone("me", "L37-0.05")
put("mr_dunn", "L37", (6.2, 4.6), 90, "neutral")
put("dunn", "L37", (6.6, 3.0), 90, "neutral")
S("L37", PX((1.4, 0.4, 1.7), (7.2, 3.6, 1.3), 18, 0.12), "morning", fill=0.5)
S("L37.2", X((5.2, 2.2, 1.3), (8.2, 3.6, 0.7), 26, (5.8, 2.6, 1.2), (8.2, 3.6, 0.7), 26), "morning", fill=0.5)
steps("L38", 41)
tag("L38", 27)
S("L38", PX((98.4, 0.0, 0.9), (110.0, 0.0, -8.5), 15, 0.08), "in", fill=1.0, stairl=2.5, lamp=0.0)
steps("L39", 27)
key("dunn", "L39", expr="polite")
gone("mr_dunn", "L39-0.05")
put("dunn", "L39", (6.6, 3.5), 90, "polite")
S("L39", PX((3.6, 2.4, 1.6), (6.6, 3.5, 1.55), 30, 0.10), "morning", fill=0.5)
walk("dunn", "L39.2", (6.6, 3.5), "L39.5+0.2", (7.5, 3.6), 90, "polite")
S("L39.3", PX((3.8, 5.6, 1.4), (7.6, 3.6, 0.9), 20, 0.08), "morning", fill=0.5)
gone("dunn", "L40-0.05")
cue("L40", "dust", who=["dad"])
walk("dad", "L40", (stair(8)[0], 0.0, stair(8)[1]), "L40.2", (99.6, 0.0, 0.0), 270, "blank", lean=6)
S("L40", PX((97.0, 0.0, 1.2), (stair(5)[0], 0.0, stair(5)[1] + 0.8), 20, 0.10), "in", fill=1.0, stairl=1.6, lamp=0.0)
gone("dad", "L41-0.05")
cue("L41", "dust", who=[])
put("dad", "L41", (SX - 7.0 + 1.35 * math.cos(math.radians(200)), 1.35 * math.sin(math.radians(200)), -0.22), 20, "blank")
put("arlo", "L41", (SX - 7.0 + 1.35 * math.cos(math.radians(320)), 1.35 * math.sin(math.radians(320)), -0.22), 130, "neutral")
S("L41", PX((SX - 10.5, 1.8, 1.7), (SX - 7.0, 0.0, 1.0), 19, 0.10), "in", fill=1.0, inside=1.4)
gone("arlo", "L42-0.05")
put("dad", "L42", (SX - 3.0, 0.3, 0.0), 90, "blank")
S("L42", PX((SX - 1.2, 0.0, 1.55), (SX - 3.0, 0.3, 1.5), 32, 0.10), "in", fill=0.9, inside=1.0)

# --- 09 midnight, L43 to L52
gone("dad", "L43-0.05")
cue("L43", "puff", whistle=1.0)
S("L43", PX((3.0, -6.0, 2.2), (0.0, 0.0, 6.8), 20, 0.10), "night", fill=0.2)
cue("L44", "puff", whistle=0.0)
cue("L44", "door", open=1.0)
put("dad", "L44", (99.1, 0.0, 0.0), 90, "worried", arms=[30, 30])
put("me", "L44", (97.8, 0.3, 0.0), 90, "worried")
cue("L44", "lamp", pos=[99.8, 0.55, 0.8])
S("L44", PX((95.6, 1.7, 1.7), (99.9, 0.1, 1.2), 20, 0.10), "night", fill=0.7, inside=0.8, lamp=1.6, stairl=1.0)
gone("dad", "L44.2-0.05")
steps("L44.2", 27)
tag("L44.2", 27)
walk("me", "L44.2", (98.1, 0.3, 0.0), "L45", (stair(8)[0], 0.0, stair(8)[1]), 90, "worried")
raw("me", "L45.1", pos=[stair(15)[0], 0.0, stair(15)[1]])
raw("me", "L46", pos=[stair(19)[0], 0.0, stair(19)[1]])
cue("L44.2", "lamp", pos=[stair(2)[0], 0.55, stair(2)[1] + 0.6], to=[stair(19)[0], 0.55, stair(19)[1] + 0.6], dur=2.8)
S("L44.2", PX((stair(12)[0] + 1.2, 0.2, ab(stair(12)[0] + 1.2, 1.5)), (stair(5)[0], 0.0, stair(5)[1] + 1.2), 16, 0.08), "night", fill=0.8, inside=0.8, lamp=1.0, stairl=1.0)
steps("L45", 27)
tag("L45", 27)
steps("L45.1", 28, new=28)
tag("L45.1", 28)
S("L45", PX((stair(14)[0] + 1.6, 0.15, ab(stair(14)[0] + 1.6, 1.6)), (stair(10)[0], 0.0, stair(10)[1] + 1.3), 16, 0.10), "night", fill=0.8, lamp=1.0, stairl=1.0, inside=0.8)
S("L45.1", PX((stair(22)[0] + 1.6, 0.15, ab(stair(22)[0] + 1.6, 1.6)), (stair(17)[0], 0.0, stair(17)[1] + 1.3), 16, 0.10), "night", fill=0.8, lamp=1.0, stairl=1.0, inside=0.8)
S("L46", PX((99.0, 0.0, 1.5), (stair(26)[0], 0.0, stair(26)[1] + 0.2), 14, 0.10), "night", fill=0.8, lamp=0.6, stairl=2.2, inside=0.8)
gone("me", "L46.3-0.05")
put("me", "L46.3", (stair(20)[0], 0.0, stair(20)[1]), 90, "scared")
key("me", "L46.4", head=[0, 22])
S("L46.3", PX((stair(20)[0] + 2.6, 0.2, ab(stair(20)[0] + 2.6, 1.6)), (stair(20)[0], 0.0, stair(20)[1] + 1.5), 22, 0.10), "night", fill=0.9, lamp=1.0, stairl=1.4, inside=0.8)
gone("me", "L47-0.05")
steps("L47", 28, new=28)
put("dad", "L47", (stair(28)[0], 0.0, stair(28)[1] - 0.42), 90, "asleep", lean=18, head=[0, 20])
cue("L47", "lamp", pos=[stair(27)[0] - 0.1, 0.55, stair(27)[1] + 0.2])
S("L47", PX((LX + 1.6, -0.5, LZ + 1.3), (stair(28)[0], 0.0, LZ + 0.6), 16, 0.10), "night", fill=0.6, lamp=1.4, stairl=1.0, inside=0.8)
S("L48", PX((LX - 0.2, -0.6, LZ + 1.4), (LX + 1.45, 0.0, LZ), 30, 0.12), "night", fill=0.9, lamp=0.8, stairl=0.6, inside=0.8)
cue("L49", "puff", shoulder=[LX + 1.45, 0.0, LZ + 0.1])
S("L49", PX((LX + 0.5, -1.0, LZ + 0.55), (LX + 1.45, 0.0, LZ + 0.25), 28, 0.10), "night", fill=0.9, lamp=1.0, stairl=0.8, inside=0.8)
put("me", "L50", (stair(26)[0], 0.28, stair(26)[1]), 90, "scared")
put("dad", "L50", (stair(28)[0], -0.2, stair(28)[1] - 0.42), 90, "asleep", lean=18, head=[0, 20])
cue("L50", "puff", shoulder=None)
cue("L50", "lamp", pos=[stair(26)[0] + 0.25, 0.6, stair(26)[1] + 0.6])
S("L50", PX((LX + 2.2, 0.1, LZ + 1.5), (stair(26)[0], 0.28, stair(26)[1] + 1.5), 20, 0.10), "night", fill=0.4, lamp=1.6, stairl=0.8, inside=0.8)
cue("L51", "puff", shoulder=[LX + 1.45, 0.0, LZ + 0.1])
S("L51", PX((LX + 0.6, -1.1, LZ + 0.4), (LX + 1.45, 0.0, LZ + 0.08), 28, 0.10), "night", fill=0.8, lamp=0.6, stairl=0.6, inside=0.8)
cue("L52", "puff", shoulder=None)
put("me", "L52", (stair(27)[0], 0.0, stair(27)[1]), 90, "scared", arms=[0, 70])
cue("L52", "lamp", pos=[stair(27)[0] + 0.5, 0.6, stair(27)[1] + 0.6], to=[LX + 1.2, 0.5, LZ + 0.25], dur=1.4)
S("L52", PX((LX + 0.8, -1.5, LZ + 1.2), (stair(27)[0] + 0.6, 0.0, LZ + 0.8), 20, 0.10), "night", fill=0.9, lamp=1.0, stairl=0.6, inside=0.8)
gone("me", "L52+0.9")
gone("dad", "L52+0.9")
cue("L52+0.9", "lamp", pos=[LX + 1.2, 0.0, LZ + 0.25], off=True)
S("P02", PX((LX + 0.45, -0.35, LZ + 0.9), (LX + 1.45, 0.0, LZ - 0.1), 36, 0.14), "night", fill=0.3, lamp=0.0, stairl=0.0, inside=0.6)

# --- 10 the Under, L53 to L55
cue("L53", "under", on=True, light=0.12)
S("L53", PX((LX + 1.45, 0.6, LZ + 1.3), (LX + 1.45, -0.55, LZ - 5.8), 24, 0.10), "night", fill=0.0, lamp=0.0, stairl=0.0, inside=0.5, ufill=1.0, name="eyes")
cue("L53.1", "under", on=True, light=1.0)
S("L53.1", PX((LX + 3.0, -11.5, LZ - 0.9), (LX + 1.45, -2.2, LZ - 5.6), 13, 0.08), "night", fill=0.0, lamp=0.0, stairl=0.0, inside=0.5, ufill=2.4, name="face")
S("L54", PX((LX - 2.2, -8.5, LZ - 1.6), (LX + 1.45, -1.0, LZ - 5.6), 15, 0.08), "night", fill=0.0, lamp=0.0, stairl=0.0, inside=0.5, ufill=2.4, name="face2")
S("L54.2", PX((LX + 1.2, -12.5, LZ - 4.2), (LX + 1.45, -1.5, LZ - 5.6), 12, 0.10), "night", fill=0.0, lamp=0.0, stairl=0.0, inside=0.5, ufill=2.4)
S("L55", PX((LX + 3.2, -3.4, LZ - 3.6), (LX + 1.45, -2.2, LZ - 5.4), 22, 0.10), "night", fill=0.0, lamp=0.0, stairl=0.0, inside=0.5, name="mouth")
S("L55.2", PX((LX - 0.3, -3.2, LZ - 3.2), (LX + 1.45, -2.2, LZ - 5.2), 22, 0.08), "night", fill=0.0, lamp=0.0, stairl=0.0, inside=0.5)
cue("L56", "under", on=False, light=0.0)

# --- 11 the reveal, L56 to L61
S("L56", PX((2.4, -12.0, 1.0), (0.0, 12.0, 2.4), 16, 0.12), "dawn", fill=0.8)
S("L57", PX((0.0, 162.0, -12.0), (0.0, 200.0, -12.0), 15, 0.08), "day", fill=0.0, inside=0.0, exp=0.2, name="cutaway", hold=True)
cue("L57", "cut", ext=0)
cue("L58", "cut", ext=0, pulse=True, dur=1.8)
S("L58", PX((0.0, 172.0, -8.0), (0.0, 200.0, -12.0), 18, 0.10), "day", fill=0.0, exp=0.2)
cue("L58.2", "cut", ext=0)
cue("L59", "cut", ext=1)
cue("L59.2", "cut", ext=2)
cue("L59.4", "cut", ext=3)
S("L58.2", PX((0.0, 174.0, -18.0), (0.0, 200.0, -24.0), 18, 0.10), "day", fill=0.0, exp=0.2)
S("L59", X((10.0, 172.0, -7.0), (10.0, 200.0, -7.0), 18, (6.0, 180.0, -7.0), (10.0, 200.0, -7.0), 18), "day", fill=0.0, exp=0.2)
S("L59.3", X((-10.0, 172.0, -7.0), (-10.0, 200.0, -7.0), 18, (-6.0, 180.0, -7.0), (-10.0, 200.0, -7.0), 18), "day", fill=0.0, exp=0.2)
S("L60", PX((-14.0, 188.0, 1.8), (-14.0, 200.0, 0.6), 20, 0.10), "day", fill=0.0, exp=0.2)
put("arlo", "L61", (-12.4, -6.0, 0.9), 90, "soft")
S("L61", PX((-6.6, -6.0, 2.5), (-12.4, -6.0, 2.45), 28, 0.10), "dawn", fill=0.5, inside=0.8)

# --- 12 the climb and the blow, L62 to L69
gone("arlo", "L62-0.05")
steps("L62", 28)
put("dad", "L62", (stair(14)[0], 0.5, stair(14)[1]), 270, "worried", lean=8)
put("me", "L62", (stair(14)[0] + 0.1, -0.5, stair(14)[1]), 270, "worried", arms=[0, 0])
raw("dad", "L62.1+0.2", pos=[stair(5)[0], 0.5, stair(5)[1]])
raw("me", "L62.1+0.2", pos=[stair(5)[0] + 0.1, -0.5, stair(5)[1]])
cue("L62", "dust", who=["dad"])
cue("L62", "lamp", pos=[stair(2)[0], 0.0, stair(2)[1] + 1.4])
S("L62", PX((stair(4)[0] - 0.0, 0.0, ab(stair(4)[0], 1.6)), (stair(11)[0], 0.0, stair(11)[1] + 0.8), 18, 0.10), "in", fill=1.0, stairl=1.6, lamp=1.0)
gone("dad", "L63-0.05")
gone("me", "L63-0.05")
cue("L63", "dust", who=[])
cue("L63", "ladder", on=True)
put("arlo", "L63", (0.0, -1.3), 180, "neutral", arms=[55, 55])
S("L63", PX((3.4, -5.0, 1.9), (0.0, -0.4, 2.4), 22, 0.10), "dawn", fill=0.9)
put("me", "L64", (0.0, -1.0, 5.15), 180, "focus" if False else "neutral", arms=[70, 70])
key("me", "L64.2", arms=[70, 70], head=[0, -10])
S("L64", PX((3.4, -1.0, 6.2), (0.0, -0.9, 6.3), 24, 0.10), "dawn", fill=0.9)
cue("L64.2", "puff", whistle=-1.0)
S("L64.2", PX((2.0, -2.8, 7.1), (0.0, -0.6, 6.9), 28, 0.10), "dawn", fill=0.7)
gone("me", "L65-0.05")
gone("arlo", "L65-0.05")
cue("L65", "puff", whistle=0.0, collar=-1.0)
S("L65", PX((1.05, -1.9, 1.5), (1.05, 0.0, 0.15), 22, 0.12), "dawn", fill=0.7)
cue("L66", "puff", collar=0.0)
cue("L66", "cut", ext=3, pulse=True, dur=2.0, gaze=0.0)
cue("L66.2", "cut", ext=3, gaze=1.0)
cue("L66.2", "cut", ext=3, gaze=1.0)
S("L66", PX((0.0, 170.0, -10.0), (0.0, 200.0, -16.0), 18, 0.10), "day", fill=0.0, exp=0.2)
S("L66.2", PX((0.0, 176.0, -22.0), (0.0, 200.0, -26.0), 20, 0.12), "day", fill=0.0, exp=0.2)
cue("L67", "puff", wells=-1.0)
S("L67", PX((0.0, 27.0, 1.6), (0.0, -10.0, 0.3), 14, 0.10), "dawn", fill=0.6)
put("arlo", "L67.2", (1.3, -1.7), 270, "neutral", head=[0, 38])
S("L67.2", PX((2.4, -4.0, 1.4), (0.4, -1.3, 1.3), 28, 0.10), "dawn", fill=0.9)
cue("L68", "puff", wells=0.0)
cue("L68", "cut", ext=3, gaze=1.0, gone=True)
gone("arlo", "L68+0.8")
S("L68", PX((0.0, 176.0, -20.0), (0.0, 200.0, -30.0), 18, 0.10), "day", fill=0.0, exp=0.2)
S("L69", PX((0.0, 172.0, -26.0), (0.0, 200.0, -38.0), 20, 0.10), "day", fill=0.0, exp=0.2)

# --- 13 warm, then cold, L70 to L74
steps("L70", 13)
tag("L70", 13)
S("L70", PX((98.4, 0.0, 1.1), (SX + 3.4, 0.0, -1.8), 16, 0.08), "in", fill=1.0, stairl=1.5, lamp=0.0)
cue("L70", "lamp", pos=[SX + 2.0, 0.0, -0.4], off=True)
cue("L70", "door", open=1.0)
cue("L71", "door", open=1.0, to=0.0, dur=0.7)
put("dad", "L71", (SX - 7.0 + 1.35 * math.cos(math.radians(200)), 1.35 * math.sin(math.radians(200)), -0.22), 20, "laugh")
put("arlo", "L71", (SX - 7.0 + 1.35 * math.cos(math.radians(320)), 1.35 * math.sin(math.radians(320)), -0.22), 130, "laugh")
put("me", "L71", (SX - 7.0, 1.4, -0.22), 180, "smile")
S("L71", PX((SX - 10.6, -2.2, 1.9), (SX - 7.0, 0.1, 1.0), 20, 0.10), "in", fill=1.1, inside=1.5)
gone("dad", "L72-0.05")
gone("arlo", "L72-0.05")
gone("me", "L72-0.05")
S("L72", PX((SX - 4.6, 0.4, 0.2), (SX - 7.0, 0.0, 0.0), 26, 0.12), "in", fill=0.5, inside=0.8)
cue("L72.2", "puff", shoulder=[SX - 7.3, 0.2, 0.03])
S("L72.2", PX((SX - 5.4, -0.3, 0.14), (SX - 7.3, 0.2, 0.05), 30, 0.12), "in", fill=0.5, inside=0.7)
tag("L73", 13)
S("L73", X((SX - 6.0, 0.0, 0.6), (SX - 7.3, 0.2, 0.4), 22, (SX - 6.4, 0.0, 0.6), (SX - 7.3, 0.2, 0.4), 22), "in", fill=0.3, inside=0.7, tagbig=2.4)
cue("L73.1", "puff", shoulder=None)
put("dad", "L74", (SX - 12.2, 2.8, -0.2), 90, "blank")
S("L74", PX((SX - 8.6, 3.6, 1.8), (SX - 12.2, 2.8, 1.2), 22, 0.08), "in", fill=0.9, inside=1.0)
walk("dad", "L74.1", (SX - 3.5, 0.7, 0.0), "L74.3", (SX - 1.7, 0.45, 0.0), 90, "blank")
S("L74.1", PX((SX - 0.7, -0.9, 1.5), (SX - 4.0, 0.7, 1.4), 20, 0.10), "in", fill=0.9, inside=1.0)
put("dad", "L74.3", (SX - 1.7, 0.45, 0.0), 90, "blank", arms=[0, 85])
S("L74.3", PX((SX - 1.1, -1.7, 1.15), (SX - 0.1, 0.4, 1.1), 26, 0.12), "in", fill=0.9, inside=1.0)

# ------------------------------------------------------------------------------------------------ sound
whistle = lambda at, db=-12, d=1.6, pitch=220: {"at": at, "kind": "whistle", "db": db, "dur": d, "pitch": pitch}
sfx = [
    whistle("L01.2+0.12", -12, 1.5),
    whistle("L14-0.2", -22, 1.3, 880),
    whistle("L24", -12, 1.6),
    {"at": "L25+0.35", "kind": "door", "db": -15},
    whistle("L34", -13, 1.5),
    whistle("L35", -22, 1.4, 880),
    whistle("L43", -12, 1.8),
    whistle("L50", -17, 1.4),
    {"at": "P02+0.4", "kind": "breath", "db": -16, "dur": 0.6, "keep": True},
    whistle("L64.2", -11, 1.6),
    {"at": "L68", "kind": "thud", "db": -18},
    whistle("L73", -24, 1.5),
]
music = {"root": 50, "mode": "minor", "bpm": 84, "seed": 98,
         "sections": [
             {"at": 0, "voices": ["pluck", "pulse", "pad"], "energy": 0.55},
             {"at": "L23", "voices": ["pluck_hi", "pad"], "energy": 0.4},
             {"at": "L24", "voices": ["pluck", "pulse", "pad"], "energy": 0.55},
             {"at": "L30", "voices": ["drone", "pad"], "energy": 0.6},
             {"at": "L37", "voices": ["drone", "pluck"], "energy": 0.5},
             {"at": "L43", "voices": ["drone", "pad", "pluck"], "energy": 0.6},
             {"at": "L53", "voices": ["drone", "choir"], "energy": 0.8},
             {"at": "L56", "voices": ["drone", "pad", "pluck"], "energy": 0.55},
             {"at": "L62", "voices": ["drone", "pulse", "pluck"], "energy": 0.7},
             {"at": "L70", "voices": ["pad", "pluck_hi"], "energy": 0.4, "mode": "major"},
             {"at": "L72", "voices": ["drone", "pad"], "energy": 0.3, "mode": "minor"},
         ]}
sound = {"rev": 1, "floor": "grass", "steps_db": -22,
         "floor_spans": [{"from": "L05.2", "to": "L06", "floor": "wood"}, {"from": "L07", "to": "L11", "floor": "wood"},
                         {"from": "L21", "to": "L22", "floor": "wood"}, {"from": "L25", "to": "L26", "floor": "wood"},
                         {"from": "L40", "to": "L43", "floor": "wood"}, {"from": "L44", "to": "L53", "floor": "wood"},
                         {"from": "L62", "to": "L63", "floor": "wood"}, {"from": "L74", "to": "end", "floor": "wood"}],
         "ambience": [{"kind": "crickets", "from": "L24", "to": "L36", "lufs": -42},
                      {"kind": "wind", "from": "L43", "to": "L53", "lufs": -44}],
         "sfx": sfx,
         "music_drops": [{"from": "P01", "to": "P01>"}, {"from": "P02", "to": "P02>", "keep": ["breath"]}]}

look = {"fog": "#cfe8ff", "fog_density": 0.003, "fog_start": 45.0, "sky": "#8fd0ff", "exposure": 0.0,
        "flash_safe": True, "style": "closer",
        "polish": {"emph": ["L01", "L18", "L36", "L53", "L54", "L66"], "reveal": ["L54", "L56"], "twist": "L56",
                   "quiet": [["L70", "L71"]],
                   "sway": [NAMES.get(n) for n in ("eyes", "face", "face2", "mouth") if NAMES.get(n)],
                   "hold": [NAMES[n] for n in ("tagbig", "cutaway", "tally") if n in NAMES],
                   "camera": True, "idle": True, "ease": True}}

story = {
    "slug": "ep98-town-whistle",
    "title": "Everyone Hides When The WHISTLE Blows \U0001F4EF",
    "made_for_kids": False,
    "premise": ("When the town whistle blows, at any hour, everyone goes down to their basement until it stops. I'm 24, "
                "back living with Dad, and our basement has gained one step every whistle, from thirteen to twenty-six. "
                "My grandpa next door, in the only house with no basement, makes tea."),
    "twist": ("Nothing walks the streets: the thing lives under the town and blows the whistle itself to call everyone "
              "down, and every time they come it pulls their stairs one step closer. Grandpa built on stone blocks so "
              "it could never call him. I blow the whistle from the top and its own rule sends it deeper down."),
    "world": ("a bright summer street of pastel clapboard houses with a green iron pole and a brass whistle in the "
              "middle of the road, cellar steps going down, a face as wide as a basement far under the street"),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#7be04a",
    "gap": 0.12,
    "tail": LOOP,
    "min_read": 0.15,
    "fade_in": False,
    "fade_out": False,
    "look": look,
    "grade": {"shadows": [-0.01, 0.0, 0.04], "highlights": [0.03, 0.01, -0.02], "saturation": 1.14, "contrast": 1.06,
              "vignette": 0.18, "bloom": 0.22, "grain": 0.008, "red_line": 0.7},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "music": music,
    "sound": sound,
    "set_moves": [],
}
from blocky import timeline

voice = json.loads((HERE.parent / "voice-timings.json").read_text())
_tl0 = timeline.build({"name": "ep98-town-whistle", "lines": lines, "shots": [{"id": "S0"}], "gap": 0.12, "tail": LOOP,
                       "min_read": 0.15, "cast": cast}, voice)
AT = timeline.resolver(_tl0["lines"], _tl0["duration"])
for k in acting:
    acting[k].sort(key=lambda e: AT(e["at"]))
cues.sort(key=lambda e: AT(e["at"]))
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots, {len(cues)} cues")
