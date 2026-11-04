"""Writes ../story.json for "Three Burnt Bridges To A STRANGER" (ep100-window-bridges).

Run from anywhere: python stories/ep100-window-bridges/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the acting
and the cues set.py reads (count, bridge, burnt, sea, pip, show, tray) and the score.

World (metres, z up): the lane runs along y (sea at +y); my wall is x = -1.6, Eli's x = +1.6. Third-floor rooms: floor
z 6.0, sill 6.9. I stand at (-2.25, -0.5, 6.0) facing +x (yaw 90); Eli at (2.25, -0.5, 6.0) facing -x (yaw -90). Our bridge
is at y -0.5, z 6.93. Burnt bridges (y): old +0.55, mid -1.6, far +1.75. Acting yaw: 0 faces -y, 90 faces +x.
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
MIN_SHOT = 0.58
MIN_PRIMARY = 0.48

FACE = {"eyes": "round", "brows": True, "ink": "#24131f"}
LASH = {"eyes": "lashes", "brows": True, "ink": "#24131f"}
cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#ff6f61", "pattern": "solid", "pants": "#7a8a4a", "shoes": "#f4f4f2",
           "sleeves": "long", "hair": "swoop", "hair_c": "#3a2418", "extras": ["hooddown"], "extra_c": "#ff6f61", "face": dict(FACE)},
    "eli": {"age": "adult", "skin": "#eaa98a", "shirt": "#1f3a68", "pattern": "knit", "pattern_c": "#2f5596", "pants": "#2b2f3a",
            "shoes": "#3a2a1c", "sleeves": "short", "hair": "cap", "hair_c": "#e8c66a", "face": dict(FACE)},
    "mom": {"age": "adult", "skin": "#d9a27a", "shirt": "#7b3f8c", "pattern": "solid", "pants": "#7b3f8c", "shoes": "#3a2a2a",
            "sleeves": "short", "hair": "bun", "hair_c": "#4a4448", "extras": ["apron"], "extra_c": "#1fa39a", "face": dict(LASH)},
    "vega": {"age": "adult", "skin": "#e8c4a0", "shirt": "#d7263d", "pattern": "solid", "pants": "#5a3a3a", "shoes": "#3a2a2a",
             "sleeves": "long", "hair": "long", "hair_c": "#f4f1ec", "extras": ["scarf"], "extra_c": "#d7263d", "face": dict(LASH)},
    "nb1": {"age": "adult", "skin": "#c98e68", "shirt": "#3a7ca5", "pattern": "solid", "pants": "#3a3a4a", "shoes": "#2a2a2a",
            "sleeves": "long", "hair": "spiky", "hair_c": "#2a1d15", "face": dict(FACE)},
    "nb2": {"age": "adult", "skin": "#f1c9a0", "shirt": "#e0a030", "pattern": "stripes", "pattern_c": "#ffffff", "pants": "#3a3a4a",
            "shoes": "#2a2a2a", "sleeves": "long", "hair": "long", "hair_c": "#7a4a22", "face": dict(LASH)},
    "stone_a": {"age": "adult", "skin": "#e0b898", "shirt": "#8a8f98", "pattern": "knit", "pattern_c": "#a4a9b2", "pants": "#4a4a52",
                "shoes": "#2a2a2a", "sleeves": "long", "hair": "none", "hat": "ballcap", "hat_c": "#5a5f68", "face": dict(FACE)},
    "stone_b": {"age": "adult", "skin": "#d9a27a", "shirt": "#7a5230", "pattern": "knit", "pattern_c": "#946a40", "pants": "#4a4a52",
                "shoes": "#2a2a2a", "sleeves": "long", "hair": "none", "hat": "ballcap", "hat_c": "#5a3d22", "face": dict(FACE)},
}

NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {k: [] for k in cast}
cues = []
shots = []


def raw(who, at, **kw):
    acting[who].append({"at": at, **kw})


def put(who, at, pos, yaw=0, expr="neutral", **kw):
    """The character is there from this instant (a cut); everything it doesn't set goes back to neutral."""
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": list(pos), "blend": 0, "yaw": yaw, "expr": expr, "hidden": False, **NEUTRAL, **kw})


def pose(who, at, blend=0.3, **kw):
    """Change a standing character's pose from this instant (eased), position held."""
    keys = acting[who]
    prev = next(k["pos"] for k in reversed(keys) if "pos" in k)
    keys.append({"at": at, "pos": prev, "blend": blend, **kw})


def walk(who, at0, p0, at1, p1, yaw=None, expr="neutral", **kw):
    put(who, at0, p0, yaw if yaw is not None else 0, expr, **kw)
    raw(who, at1, pos=list(p1))


def gone(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def count(at, n, to=None, dur=1.0):
    d = {"n": n}
    if to is not None:
        d.update({"n_to": to, "dur": dur})
    cue(at, "count", **d)


def bridge(at, vis, to=None, dur=1.0):
    d = {"vis": vis}
    if to is not None:
        d.update({"vis_to": to, "dur": dur})
    cue(at, "bridge", **d)


def burnt(at, h, to=None, dur=1.0, sway=0.0, tilt=None):
    d = {"h": h, "sway": sway, "tilt": tilt or [0.0, 0.0, 0.0]}
    if to is not None:
        d.update({"h_to": to, "dur": dur})
    cue(at, "burnt", **d)


def show(at, *names):
    cue(at, "show", on=list(names))


# ---------------------------------------------------------------------------------------------------- cameras
def pos_of(tg, d, az, el):
    a, e = math.radians(az), math.radians(el)
    return [round(tg[0] + d * math.sin(a) * math.cos(e), 3), round(tg[1] - d * math.cos(a) * math.cos(e), 3),
            round(tg[2] + d * math.sin(e), 3)]


def C(tgt, d, az=0, el=8, lens=30, d2=None, lens2=None, tgt2=None, az2=None, el2=None):
    """A camera aimed at tgt from distance d, azimuth az (0 = from -y looking +y, 90 = from +x looking -x), elevation el;
    with d2 / tgt2 / lens2 / az2 it moves there over the shot."""
    k0 = [0, pos_of(tgt, d, az, el), list(tgt), lens]
    if d2 is None and tgt2 is None and lens2 is None and az2 is None and el2 is None:
        return [k0]
    t2 = tgt2 or tgt
    return [k0, [1, pos_of(t2, d2 if d2 is not None else d, az if az2 is None else az2, el if el2 is None else el2),
                 list(t2), lens2 or lens]]


def X(loc, tgt, lens, loc2=None, tgt2=None, lens2=None):
    ks = [[0, list(loc), list(tgt), lens]]
    if loc2 or tgt2 or lens2:
        ks.append([1, list(loc2 or loc), list(tgt2 or tgt), lens2 or lens])
    return ks


HOLD, SWAY = [], []
KEEP_AT = {"L02.2", "L06.1", "L07.1", "L24.1", "L35.2", "L49.2", "L36.2", "L12.1", "L12.2", "L56", "L64"}


def S(at, cam, look="day", fill=1.0, hand=0.004, dof=None, exp=0.0, torch=None, note="", step=2, hold=False, sway=False):
    d = {"id": f"S{len(shots) + 1:02d}", "cam": cam, "step": step, "hand": hand, "look": look}
    if len(shots):
        d["at"] = at
    if fill != 1.0:
        d["fill"] = fill
    if dof:
        d["dof"] = dof
    if exp:
        d["exp"] = exp
    if torch:
        d["torch"] = torch
    if note:
        d["note"] = note
    d["_opt"] = isinstance(at, str) and at not in KEEP_AT and ("." in at or "+" in at)
    shots.append(d)
    if hold:
        HOLD.append(d["id"])
    if sway or look in ("night", "autumn"):
        SWAY.append(d["id"])
    return d


ME = (-2.25, -0.5, 6.0)
EL = (2.25, -0.5, 6.0)


def at_me(d=2.6, lens=30, dy=0.25, z=7.55, dz=0.5, z2=None, d2=None, lens2=None, dy2=None, tz=7.45):
    """Camera across the lane, looking at me at my window (az -90 means standing at -x; we stand at +x, az 90)."""
    c0 = [0, [ME[0] + d, ME[1] + dy, tz + dz], [ME[0], ME[1], tz], lens]
    if d2 is None and lens2 is None and dy2 is None and z2 is None:
        return [c0]
    return [c0, [1, [ME[0] + (d2 or d), ME[1] + (dy if dy2 is None else dy2), tz + (dz if z2 is None else z2)], [ME[0], ME[1], tz],
                 lens2 or lens]]


def at_eli(d=2.6, lens=30, dy=-0.25, dz=0.5, d2=None, lens2=None, dy2=None, z2=None, tz=7.45):
    c0 = [0, [EL[0] - d, EL[1] + dy, tz + dz], [EL[0], EL[1], tz], lens]
    if d2 is None and lens2 is None and dy2 is None and z2 is None:
        return [c0]
    return [c0, [1, [EL[0] - (d2 or d), EL[1] + (dy if dy2 is None else dy2), tz + (dz if z2 is None else z2)], [EL[0], EL[1], tz],
                 lens2 or lens]]


for k in acting:
    acting[k].append({"at": 0, "pos": [0, 20, 0], "hidden": True, "blend": 0, **NEUTRAL})


def me_w(at, expr="neutral", **kw):
    put("me", at, ME, 90, expr, **kw)


def eli_w(at, expr="neutral", **kw):
    put("eli", at, EL, -90, expr, **kw)


DOWN = [0, 22]          # head [yaw, pitch]: looking down
ON = {"torch": None}

# ===================================================================================================== 01 the hook L01-L08
count(0, 208)
bridge(0, 22)
burnt(0, [0.0, 0.0, 0.0])
SH = ["matches"]
show(0, *SH)
# S01: close, straight down from my sill: our new planks in the foreground, the three charred bridges on the cobbles, the
# teal shutters opposite at the top of the frame
S(0, X((-1.25, -1.9, 7.6), (0.9, 0.2, 1.2), 22, (-1.0, -1.6, 7.0), (0.9, 0.2, 1.0), 25), "day", fill=1.0, hand=0.003,
  note="frame 1: our newest planks at my sill, the three burnt bridges below, shutters opposite")
me_w("L02", "worried", head=DOWN)
S("L02", at_me(2.3, 30, 0.3, dz=0.55, z2=0.7, d2=1.9, lens2=33), "day", note="me at my window, worried, looking down")
S("L02.2", X((-1.0, -2.6, 0.9), (1.0, -1.6, 0.25), 26, (-0.7, -2.5, 0.7), (1.2, -1.6, 0.2), 28), "day", hand=0.003,
  note="low on the cobbles along a burnt bridge to the opposite wall")
gone("me", "L03")
S("L03", X((0.0, -8.0, 3.0), (0.0, 6.0, 7.0), 17, (0.0, -7.2, 3.6), (0.0, 7.0, 7.2), 19), "day", fill=0.8,
  note="up the alley: dozens of little bridges between windows, sun through them")
S("L03.1", X((0.3, 12.0, 4.4), (0.0, -6.0, 7.2), 18, (0.1, 11.0, 4.8), (0.0, -6.0, 7.4), 19), "day", fill=0.8, note="bridges at every height, down the lane")
bridge("L04", 19, 22, 1.0)
S("L04", X((0.5, -1.7, 7.9), (1.2, -0.5, 6.95), 34, (0.7, -1.5, 7.8), (1.3, -0.5, 6.95), 38), "day", fill=0.8, hand=0.002,
  note="tight: a new pale plank settling on a bridge")
put("vega", "L05", (-2.25, 3.0, 6.0), 90, "smile", side=[0, 30])
S("L05", X((0.4, 3.0, 7.9), (-2.25, 3.0, 7.45), 32, (0.2, 3.0, 7.8), (-2.25, 3.0, 7.45), 36), "day", note="Mrs. Vega at her window, smiling")
S("L05.1", X((1.0, -3.5, 6.4), (-1.0, 3.0, 7.4), 20, (1.0, -3.0, 6.6), (-1.0, 3.2, 7.4), 22), "day", fill=0.9,
  note="sixty bridges fan out from her window like a web")
gone("vega", "L06")
put("stone_a", "L06", (-2.25, 21.0, 6.0), 90, "neutral")
put("stone_b", "L06", (2.25, 21.0, 6.0), -90, "neutral")
S("L06", X((0.1, 20.2, 8.0), (-2.25, 21.0, 7.45), 30, (0.1, 20.4, 7.9), (-2.25, 21.0, 7.45), 34), "day", note="an old guy in a flat cap at his window")
S("L06.1", X((-0.1, 21.8, 8.0), (2.25, 21.0, 7.45), 30, (-0.1, 21.6, 7.9), (2.25, 21.0, 7.45), 34), "day", note="and the other, facing him")
S("L06.2", X((-1.2, 17.0, 8.3), (0.0, 21.0, 6.9), 24, (-1.0, 17.6, 8.1), (0.0, 21.0, 6.9), 27), "day", note="their bridge, smooth grey stone")
gone("stone_a", "L07")
gone("stone_b", "L07")
put("nb1", "L07", (-2.25, -6.0, 6.0), 90, "angry", arms=[0, 0])
put("nb2", "L07", (2.25, -6.0, 6.0), -90, "angry")
S("L07", X((0.1, -6.8, 8.0), (-2.25, -6.0, 7.45), 30, (0.1, -6.6, 7.9), (-2.25, -6.0, 7.45), 34), "day", note="a neighbor glaring across his bridge")
S("L07+0.4", X((-0.1, -5.2, 8.0), (2.25, -6.0, 7.45), 30, (-0.1, -5.4, 7.9), (2.25, -6.0, 7.45), 34), "day", note="and the other glaring back")
gone("nb1", "L07.1")
gone("nb2", "L07.1")
walk("nb1", "L07.1", (-0.9, -6.0, 0.0), "L07.2", (0.8, -6.0, 0.0), 90, "neutral")
walk("nb2", "L07.1", (0.9, -4.8, 0.0), "L07.2", (-0.8, -4.8, 0.0), -90, "neutral")
burnt("L07.1", [0.0, 0.0, 0.0])
S("L07.1", X((0.0, -9.0, 1.6), (0.0, -1.0, 1.0), 26, (0.0, -8.4, 1.6), (0.0, -1.0, 1.0), 28), "day",
  note="the same two pass each other on the cobbles, strangers, a charred bridge behind")
S("L07.2", C((0.0, -5.4, 1.1), 3.2, 20, 6, 28, d2=2.6), "day", note="they don't look at each other")
gone("nb1", "L08")
gone("nb2", "L08")
put("vega", "L08", (-2.25, -3.0, 6.0), 90, "blank", side=[0, 0])
S("L08", C((-2.25, -3.0, 7.4), 2.8, 90, 6, 30, d2=2.1), "day", note="an old woman at a window, lips pressed shut")
S("L08.1", X((-0.3, -2.4, 8.4), (-1.0, -3.0, 0.4), 26, (-0.3, -2.6, 8.2), (-1.0, -3.0, 0.4), 30), "day", note="looking down at the empty cobbles")

# ===================================================================================================== 02 Eli L09-L13
gone("vega", "L09")
count("L09", 3)
bridge("L09", 3)
put("eli", "L09", EL, -90, "smile", side=[0, 0], arms=[0, 100])
pose("eli", "L09+0.6", 0.25, arms=[0, 80], head=[10, 0])
pose("eli", "L09+1.2", 0.25, arms=[0, 110], head=[-8, 0])
S("L09", at_eli(2.6, 30, -0.3, z2=0.6, d2=2.0, lens2=33), "april", note="April sun: Eli at his window, sunburned forearms, waving")
S("L09.2", X((-1.3, -1.4, 7.9), (2.0, -0.3, 7.2), 24, (-1.0, -1.2, 7.8), (2.1, -0.3, 7.3), 26), "april", note="the guy across the alley, ELI")
me_w("L10", "laugh")
eli_w("L10", "laugh")
pose("me", "L10+0.5", 0.2, head=[0, 8], side=[0, 20])
pose("eli", "L10+0.5", 0.2, head=[0, -6])
S("L10", X((0.0, -1.4, 8.3), (0.0, -0.5, 7.2), 20, (0.0, -1.0, 8.1), (0.0, -0.5, 7.2), 22), "april",
  note="Eli and me laughing at our two windows, the bridge three planks long")
S("L10.1", at_me(2.4, 30, 0.2, z2=0.6, d2=1.9, lens2=34), "april", note="me, laughing")
gone("me", "L11")
gone("eli", "L11")
put("me", "L11", (-0.55, -4.5, 0.0), 0, "laugh", head=[0, 0])
put("eli", "L11", (0.55, -4.5, 0.0), 0, "laugh")
pose("eli", "L11+0.2", 0.3, side=[0, 85], head=[10, 0])
pose("me", "L11+0.4", 0.25, head=[-10, 4], lean=-6)
S("L11", C((0.0, -4.5, 1.35), 3.2, 0, 4, 30, d2=2.5), "april", note="Eli claps me on the shoulder, both laughing (cut before it lands)")
S("L11.1", C((-0.2, -4.5, 1.4), 2.4, 20, 5, 32, d2=1.9), "april", note="closer, both laughing")
gone("me", "L12")
gone("eli", "L12")
count("L12", 4, 30, 2.4)
bridge("L12", 4, 22, 2.4)
S("L12", X((-0.5, -1.7, 7.7), (-1.2, -0.5, 6.95), 28, (-0.4, -1.5, 7.55), (-1.25, -0.5, 6.95), 32), "april", hand=0.002, dof=[1.5, 3.5],
  note="LORE: the first plank at my sill, two teal strokes, the counter ticking")
S("L12.1", X((-1.3, -1.4, 7.8), (0.8, -0.5, 6.95), 24, (-1.0, -1.3, 7.7), (1.0, -0.5, 6.95), 26), "april", note="planks growing across")
S("L12.2", X((0.0, -4.0, 5.2), (0.0, -0.5, 7.0), 28, (0.0, -3.3, 5.6), (0.0, -0.5, 7.0), 30), "april", note="the whole bridge, thirty planks, from below")
S("L13", X((-1.2, 17.5, 8.2), (0.0, 21.0, 6.9), 24, (-1.0, 18.0, 8.0), (0.0, 21.0, 6.9), 27), "day", note="bridges take years: the old stone bridge for scale")
count("L13", 30)
bridge("L13", 22)

# ===================================================================================================== 03 life together L14-L21
me_w("L14", "smile")
eli_w("L14", "smile")
cue("L14", "tray", x=-1.4, x_to=1.4, dur=1.3)
S("L14", X((0.0, -1.7, 7.9), (0.0, -0.5, 7.1), 28, (0.0, -1.4, 7.7), (0.0, -0.5, 7.1), 32), "april", hand=0.003,
  note="two mugs, one sliding across the bridge on a little tray")
S("L14.1", X((-0.7, -1.2, 7.5), (0.2, -0.5, 7.1), 36, (0.5, -1.0, 7.4), (0.6, -0.5, 7.1), 36), "april", hand=0.002, note="the tray slides")
cue("L15", "tray", off=True)
SH.append("cards")
show("L15", *SH)
pose("eli", "L15", 0.2, expr="sly", head=[0, -8], side=[0, 40])
pose("me", "L15", 0.2, expr="smirk", head=[0, 18])
S("L15", X((0.0, -1.4, 8.1), (0.0, -0.5, 7.0), 26, (0.0, -1.1, 7.9), (0.0, -0.5, 7.0), 30), "april", hand=0.003,
  note="cards on the bridge between our windows, Eli sly, a card up his sleeve")
S("L15.1", at_eli(2.3, 30, -0.3, z2=0.6, d2=1.8, lens2=34), "april", note="Eli, sly")
pose("eli", "L16", 0.3, expr="smile", arms=[0, 80], side=[0, 20])
pose("me", "L16", 0.3, expr="worried", head=[0, 0])
SH.remove("cards")
show("L16", *SH)
S("L16", X((0.0, -1.3, 8.0), (0.0, -0.5, 7.2), 24, (0.0, -1.0, 7.8), (0.0, -0.5, 7.2), 27), "april", note="Eli hands me a mug made exactly how I like it (cut before hands meet)")
S("L16.1", at_me(2.2, 30, 0.2, z2=0.6, d2=1.8, lens2=34), "april", note="me, worried")
# L17: our hall, Pip leaps at Eli
gone("me", "L17")
gone("eli", "L17")
put("eli", "L17", (39.1, -1.6, 0.0), 180, "laugh")
pose("eli", "L17+0.5", 0.25, lean=10, arms=[40, 40])
cue("L17", "pip", pos=[40.6, -0.3, 0.0], yaw=-52, pos_to=[39.4, -1.3, 0.0], dur=0.9, hop=0.8)
S("L17", X((41.6, 0.4, 1.5), (39.2, -1.4, 0.9), 22, (41.2, 0.2, 1.5), (39.2, -1.4, 0.9), 24), "home", note="Pip the terrier leaps at Eli in our hall, tail going")
S("L17.1", X((40.4, -0.1, 1.0), (39.4, -1.3, 0.8), 26, (40.1, -0.3, 1.0), (39.4, -1.3, 0.8), 30), "home", note="Pip jumping up, close")
gone("eli", "L18")
put("mom", "L18", (38.5, -1.9, 0.0), 150, "smile")
pose("mom", "L18+0.4", 0.2, side=[0, 25])
put("me", "L18", (40.0, -0.9, 0.0), 150, "worried")
pose("me", "L18+0.7", 0.3, head=[-30, 0], expr="worried")
cue("L18", "pip", hidden=True)
S("L18", X((39.9, 0.5, 1.6), (38.5, -1.9, 1.5), 28, (39.6, 0.3, 1.6), (38.5, -1.9, 1.5), 32), "home", note="Mom at our door, smiling, saying his name")
S("L18.1", X((41.4, -2.0, 1.6), (40.0, -0.9, 1.5), 30, (41.2, -1.9, 1.6), (40.0, -0.9, 1.5), 34), "home", note="me turning, puzzled")
gone("mom", "L19")
gone("me", "L19")
put("eli", "L19", (41.9, 0.4, 0.0), -90, "smile")
put("mom", "L19", (40.8, 1.6, 0.0), 0, "smile", arms=[40, 40])
SH.append("plate3")
show("L19", *SH)
S("L19", X((38.6, -1.8, 2.0), (40.8, 0.5, 0.9), 22, (38.9, -1.6, 1.9), (40.8, 0.5, 0.9), 24), "home", fill=0.9, note="our dinner table, a third plate already set")
S("L19.1", X((40.0, -0.8, 1.7), (41.9, 0.4, 1.5), 30, (40.2, -0.7, 1.7), (41.9, 0.4, 1.5), 34), "home", note="Eli at the table")
S("L20", X((40.8, -0.7, 1.5), (40.8, 1.6, 1.1), 26, (40.8, -0.5, 1.5), (40.8, 1.6, 1.15), 30), "home", note="close on Mom setting it down, at ease")
gone("eli", "L21")
pose("mom", "L21", 0.3, expr="sad-smile", head=[0, 22], arms=[0, 0])
S("L21", X((40.8, -0.6, 1.6), (40.8, 1.7, 1.5), 34, (40.8, -0.2, 1.6), (40.8, 1.7, 1.5), 38), "home", note="Mom, very quiet, looking down at the table")

# ===================================================================================================== 04 the matches L22-L24
gone("mom", "L22")
S("L22", X((0.3, 1.0, 7.7), (1.42, 0.45, 6.98), 36, (0.6, 0.9, 7.6), (1.42, 0.45, 6.98), 42), "day", hand=0.002, dof=[1.2, 4.0], note="Eli's windowsill: a small box of matches by a potted plant")
S("L22.1", X((0.2, 1.0, 7.7), (1.5, 0.35, 7.0), 30, (0.6, 0.8, 7.5), (1.5, 0.35, 7.0), 34), "day", hand=0.002, note="the box and loose matches")
S("L23", X((-0.5, -0.6, 7.7), (3.0, -0.5, 7.3), 22, (0.1, -0.6, 7.6), (3.2, -0.5, 7.3), 24), "day", hand=0.003,
  note="Eli's room through the window: no candles anywhere")
S("L23+0.7", X((0.2, 0.9, 7.8), (3.5, -0.8, 6.8), 22, (0.8, 0.8, 7.7), (3.6, -0.8, 6.8), 24), "day", hand=0.003, note="the room, a bed, a sea bag")
burnt("L24", [0.0, 0.0, 0.0])
count("L24", 64)
S("L24", X((-1.2, -2.1, 7.4), (0.8, 0.0, 1.0), 22, (-0.9, -1.8, 6.8), (0.8, 0.1, 0.8), 24), "day", hand=0.003,
  note="over the lane: the three burnt bridges lie exactly under ours")
eli_w("L24.1", "neutral", lean=14, arms=[0, 0])
pose("eli", "L24.1+0.3", 0.4, lean=26, head=[0, 10])
S("L24.1", X((-1.2, -1.0, 3.0), (1.6, -0.5, 7.0), 22, (-1.0, -0.8, 3.6), (1.6, -0.5, 7.2), 24), "day", note="their far ends, right under Eli's window, Eli leaning out above")
S("L24.2", at_eli(2.4, 30, -0.4, dz=0.9, z2=0.4, d2=1.8, lens2=34), "day", note="Eli leaning out at his sill")

# ===================================================================================================== 05 the nights L25-L33
gone("eli", "L25")
me_w("L25", "worried", head=[0, 6], side=[0, 0], lean=6)
S("L25", at_me(2.2, 30, 0.3, dz=0.4, z2=0.6, d2=1.8, lens2=33), "autumn", note="autumn night, string lights on, my breath at the window")
S("L25.1", X((0.0, -1.2, 9.2), (-0.8, 0.3, 9.4), 28, (-0.3, -1.0, 9.2), (-0.8, 0.3, 9.4), 30), "autumn", hand=0.004, note="string lights across the bridges")
gone("me", "L26")
burnt("L26", [0.18, 0.12, 0.1], sway=0.3)
S("L26", X((0.2, -3.6, 0.35), (0.0, -0.4, 0.3), 30, (0.2, -3.2, 0.3), (0.0, -0.4, 0.3), 32), "night", fill=1.2, hand=0.003,
  note="low on the cobbles: the burnt bridges a hand's width up off the ground")
S("L26.1", X((1.0, -3.0, 0.22), (-0.5, 0.5, 0.25), 26, (0.7, -2.7, 0.2), (-0.5, 0.5, 0.25), 28), "night", fill=1.3, hand=0.003, note="light under the planks")
burnt("L27", [1.0, 0.8, 0.7], sway=0.5)
S("L27", X((0.0, -6.5, 1.6), (0.0, 0.4, 1.3), 24, (0.0, -6.0, 1.7), (0.0, 0.4, 1.3), 26), "night", fill=1.2, note="wider: lifted to waist height, swaying")
S("L27.1", X((1.1, -2.8, 1.3), (-0.8, 0.5, 1.1), 26, (0.9, -2.4, 1.4), (-0.8, 0.5, 1.1), 28), "night", fill=1.2, note="swaying planks, close")
burnt("L28", [3.7, 3.2, 2.9], sway=0.8, tilt=[0.1, 0.05, 0.05])
S("L28", X((0.8, -5.0, 1.6), (0.0, 0.5, 3.8), 18, (0.8, -4.2, 1.8), (0.0, 0.5, 4.0), 18), "night", fill=1.0, note="from below: the burnt bridges a floor up, black and cracked")
S("L28.1", X((-1.3, -3.0, 2.0), (0.5, 0.5, 4.4), 20, (-1.1, -2.6, 2.2), (0.5, 0.5, 4.6), 22), "night", fill=1.0, note="rising toward us")
S("L28.2", X((-2.6, -0.2, 7.7), (0.6, 0.6, 3.8), 22, (-2.5, -0.2, 7.6), (0.6, 0.6, 3.9), 24), "night", fill=1.0, note="from my window: swaying UP")
burnt("L29", [5.6, 4.6, 4.2], sway=0.8)
S("L29", X((0.8, -5.0, 1.6), (0.0, 0.5, 5.4), 18, (0.8, -4.4, 1.9), (0.0, 0.5, 5.6), 18), "night", fill=1.0, note="the next night: higher")
S("L29.1", X((-2.6, -0.2, 7.7), (0.4, 0.6, 5.2), 22, (-2.5, -0.2, 7.6), (0.4, 0.6, 5.4), 24), "night", fill=1.0, note="from my window, higher")
burnt("L30", [5.6, 4.6, 4.2], sway=0.8)
gone("me", "L30")
S("L30", X((0.0, 9.5, 2.0), (0.0, 16.0, 0.6), 24, (0.0, 9.0, 2.0), (0.0, 16.0, 0.6), 26), "night", fill=1.3, hand=0.004,
  note="down the lane: someone else's old burnt bridge, flat on the cobbles")
S("L30.1", X((-1.2, 10.8, 0.9), (0.0, 13.0, 0.25), 28, (-1.0, 11.4, 0.7), (0.0, 13.0, 0.25), 32), "night", fill=1.4, hand=0.003, note="the other burnt bridge, flat, still")
walk("vega", "L31", (1.15, -4.6, 0.0), "L31>", (-1.15, -4.6, 0.0), -90, "worried")
S("L31", X((0.0, -9.0, 1.6), (0.0, -1.0, 1.4), 26, (0.0, -8.6, 1.6), (0.0, 0.0, 1.4), 28), "night", fill=1.2, note="Mrs. Vega crosses the lane so she won't walk under them")
S("L31.1", X((-1.0, -7.0, 1.6), (1.0, -1.5, 1.4), 26, (-0.8, -6.2, 1.6), (1.0, 0.0, 1.4), 28), "night", fill=1.3, note="her scarlet shawl, hurrying along the wall")
gone("vega", "L32")
put("me", "L32", (-4.45, 0.5, 6.75), 0, "worried", lean=-90)
pose("me", "L32+0.8", 0.4, head=[0, 0], expr="scared")
S("L32", X((-2.4, -1.5, 8.3), (-4.4, 1.0, 6.6), 26, (-2.9, -1.3, 8.0), (-4.4, 1.0, 6.6), 28), "night", fill=0.7, exp=-0.05,
  note="me waking in bed, the clock glyph at three")
S("L32.1", X((-3.4, 1.9, 7.6), (-5.4, 1.9, 7.6), 30, (-3.6, 1.9, 7.6), (-5.4, 1.9, 7.6), 34), "night", fill=0.9, hand=0.002, note="the clock glyph at three")
S("P01", X((-1.0, -0.6, 7.9), (-2.5, -0.5, 7.4), 24, (-1.3, -0.6, 7.8), (-2.5, -0.5, 7.4), 26), "night", fill=0.5, hand=0.002, exp=-0.15,
  note="drop: my dark window, still")
burnt("L33", [6.1, 5.3, 5.0], tilt=[0.5, 0.3, 0.25], sway=0.2)
gone("me", "L33")
S("L33", X((-3.2, 0.2, 7.7), (-1.4, 0.55, 7.0), 30, (-3.0, 0.3, 7.6), (-1.4, 0.55, 7.0), 34), "night", fill=0.9, hand=0.002, note="the oldest burnt bridge's end resting on my windowsill")
S("L33.1", X((-0.2, -0.6, 8.0), (-1.5, 0.55, 7.0), 28, (-0.4, -0.4, 7.9), (-1.5, 0.55, 7.0), 32), "night", fill=1.0, note="charred wood on my sill, from outside")
S("L33.2", X((0.5, -4.0, 5.0), (-0.5, 0.6, 6.0), 20, (0.4, -3.6, 5.3), (-0.5, 0.6, 6.2), 22), "night", fill=1.1, note="the other two just below")

# ===================================================================================================== 06 the alley at 3 a.m. L34-L43
LOW = [1.2, 0.8, 0.6]
burnt("L34", LOW, sway=0.15)
put("me", "L34", (-0.9, -2.3, 0.0), 180, "worried", head=[0, 12])
raw("me", "L34>", pos=[-0.7, -1.2, 0.0])
S("L34", X((-1.4, -5.0, 1.7), (-0.7, -1.3, 1.3), 28, (-1.3, -4.2, 1.6), (-0.6, -0.8, 1.3), 30), "night", fill=1.1, torch=[0.0, 0.55, 1.3, 0.0, 0.4],
  note="me on the cobbles in my hoodie, phone torch on")
S("L34.1", C((-0.7, -1.2, 1.4), 1.8, 30, 4, 30, d2=1.4), "night", fill=1.2, torch=[0.0, 0.55, 1.3, 0.0, 0.4], note="my face in the torch light")
S("L35", X((-1.45, 0.55, 1.6), (0.6, 0.55, 1.2), 22, (-1.0, 0.55, 1.5), (0.7, 0.55, 1.2), 24), "night", fill=1.2, torch=[0.0, 0.55, 1.3, 0.0, 0.4], hand=0.003,
  note="along the lowest burnt bridge to its middle")
S("L35.2", X((-0.55, 0.55, 2.4), (0.0, 0.55, 1.28), 30, (-0.3, 0.55, 2.0), (0.0, 0.55, 1.28), 34), "night", fill=1.2, torch=[0.0, 0.55, 1.3, 0.0, 0.4], hand=0.002,
  note="the one unburnt plank, pale in the soot")
S("L36", X((-0.5, 0.55, 2.7), (0.0, 0.55, 1.3), 20, (-0.35, 0.55, 2.4), (0.0, 0.55, 1.3), 22), "night", fill=1.0, torch=[0.0, 0.55, 1.3, 0.0, 0.4], hand=0.0015, hold=True, note="two soot handprints, side by side, on the plank")
S("L36.2", X((-0.35, 0.55, 2.3), (0.0, 0.55, 1.3), 22, (-0.25, 0.55, 2.1), (0.0, 0.55, 1.3), 24), "night", fill=1.0, torch=[0.0, 0.55, 1.3, 0.0, 0.4], hand=0.0015, hold=True, note="close: side by side")
pose("me", "L37", 0.4, arms=[0, 0], side=[0, 0], head=[0, 22])
put("me", "L37", (0.55, -0.1, 0.0), 180, "soft", head=[0, 24])
pose("me", "L37+0.4", 0.35, arms=[0, 70])
S("L37", X((-0.9, -0.9, 1.9), (0.1, 0.3, 1.3), 28, (-0.7, -0.6, 1.8), (0.1, 0.4, 1.3), 31), "night", fill=1.3, torch=[0.0, 0.55, 1.3, 0.0, -0.3],
  note="my hand held over one print, matching it")
gone("me", "L37.1")
S("L37.1", X((-0.9, -1.2, 5.4), (1.7, -0.5, 7.4), 22, (-0.6, -1.1, 5.7), (1.7, -0.5, 7.4), 24), "night", fill=1.0, note="across the alley, Eli's window dark")
burnt("L38", LOW, sway=0.15)
S("L38", X((-0.55, -1.6, 2.45), (0.0, -1.6, 0.9), 34, (-0.35, -1.6, 2.0), (0.0, -1.6, 0.9), 38), "night", fill=1.3, torch=[0.0, -1.6, 0.9, 0.0, -0.6], hand=0.002,
  hold=True, note="the second burnt bridge's middle plank, the same notches")
S("L38.1", X((-0.55, 1.75, 2.45), (0.0, 1.75, 0.7), 34, (-0.35, 1.75, 2.0), (0.0, 1.75, 0.7), 38), "night", fill=1.3, torch=[0.0, 1.75, 0.7, 0.0, 0.8], hand=0.002,
  hold=True, note="the third, the same prints")
S("L39", X((0.55, 0.55, 1.9), (0.22, 0.55, 1.28), 38, (0.38, 0.55, 1.6), (0.2, 0.55, 1.28), 44), "night", fill=1.3, torch=[0.0, 0.55, 1.3, 0.0, 0.4], hand=0.0015,
  hold=True, note="tight: the date notches, a nine, the month glyph")
put("me", "L40", (-0.4, -1.0, 0.0), 90, "scared", head=[0, -26], lean=-6)
S("L40", X((1.1, -1.0, 1.7), (-0.4, -1.0, 1.5), 30, (0.9, -1.0, 1.7), (-0.4, -1.0, 1.5), 34), "night", fill=1.2, note="I look up at Eli's window, scared")
S("L40.1", X((-0.4, -1.2, 1.0), (1.55, -0.5, 7.2), 24, (-0.2, -1.0, 1.4), (1.55, -0.5, 7.6), 26), "night", fill=1.0, note="up the wall to the dark window")
gone("me", "L41")
S("L41", X((-2.7, -0.5, 8.0), (3.3, -1.1, 6.8), 22, (-2.6, -0.5, 8.0), (3.3, -1.1, 6.8), 26), "night", fill=1.0, hand=0.003, note="through his window: a packed sea bag by his bed")
S("L41.1", X((-2.7, 0.2, 8.0), (5.3, 0.7, 7.55), 24, (-2.6, 0.2, 8.0), (5.3, 0.7, 7.55), 30), "night", fill=1.0, hand=0.003, note="a coil of rope on a hook")
show("L42", "ticket", *SH)
S("L42", X((0.5, -0.2, 7.5), (1.3, 0.85, 6.93), 38, (0.8, 0.1, 7.4), (1.3, 0.85, 6.93), 44), "night", fill=1.1, hand=0.002, dof=[1.4, 2.8],
  note="a plain card on his sill with a boat glyph and a ten")
S("L42.1", X((0.7, 0.5, 7.3), (1.3, 0.85, 6.93), 44, (0.95, 0.65, 7.2), (1.3, 0.85, 6.93), 52), "night", fill=1.1, hand=0.002, note="the ten")
S("L42.2", X((-0.3, 1.1, 7.9), (2.0, 0.4, 7.0), 26, (0.1, 1.0, 7.7), (2.0, 0.4, 7.0), 28), "night", fill=1.1, note="the sill: card, matches, plant")
SH.append("ticket")
show("L43", *[x for x in SH if x != "ticket"])
put("mom", "L43", (40.8, 1.6, 0.0), 0, "sad-smile", head=[0, 18])
pose("mom", "L43+1.2", 0.5, expr="smile", head=[0, -6])
S("L43", X((41.2, -0.5, 1.6), (40.8, 1.7, 1.5), 32, (41.0, -0.2, 1.6), (40.8, 1.7, 1.5), 36), "home", note="morning: Mom at our table, quiet")
S("L43.1", X((40.0, -0.5, 1.6), (40.8, 1.7, 1.5), 34, (40.2, -0.2, 1.6), (40.8, 1.7, 1.5), 38), "home", note="then nodding")
S("L43.2", X((38.6, -1.8, 2.0), (40.8, 0.5, 0.9), 22, (38.9, -1.6, 1.9), (40.8, 0.5, 0.9), 24), "home", fill=0.9, note="the table, set for three")
gone("mom", "L44")

# ===================================================================================================== 07 the reveal L44-L48
burnt("L44", [0.0, 0.0, 0.0], sway=0.0)
count("L44", 64)
S("L44", X((-0.5, 0.55, 2.1), (0.0, 0.55, 0.1), 30, (-0.3, 0.55, 1.5), (0.0, 0.55, 0.1), 36), "day", fill=1.0, hand=0.002, hold=True,
  note="the handprints again, close, daylight: we never fought")
S("L44+0.7", X((-0.45, 0.55, 1.7), (0.0, 0.55, 0.08), 38, (-0.3, 0.55, 1.3), (0.0, 0.55, 0.08), 48), "day", hand=0.0015, hold=True, note="the two hands, close")
put("me", "L45", (-0.37, -0.5, 6.96), 90, "soft", head=[0, 0])
put("eli", "L45", (0.37, -0.5, 6.96), -90, "soft")
pose("me", "L45+0.8", 0.5, head=[0, 5])
pose("eli", "L45+0.8", 0.5, head=[0, 4])
S("L45", X((0.0, -3.6, 8.2), (0.0, -0.5, 8.0), 26, (0.0, -3.0, 8.2), (0.0, -0.5, 8.0), 28), "autumn", fill=1.1, exp=0.1, note="a memory, last November: Eli and me in the middle of our bridge at night, string lights on, soft")
S("L45.1", X((0.0, -2.4, 8.3), (0.0, -0.5, 8.1), 30, (0.0, -2.0, 8.3), (0.0, -0.5, 8.1), 34), "autumn", fill=1.1, exp=0.1, note="closer, both soft")
show("L46", "matchpair", *[x for x in SH if x != "matches"])
pose("me", "L46", 0.4, arms=[0, 80], expr="soft")
pose("eli", "L46", 0.4, arms=[0, 80], expr="soft")
S("L46", X((-1.2, -2.8, 8.6), (0.0, -0.5, 7.9), 22, (-1.0, -2.6, 8.5), (0.0, -0.5, 7.9), 24), "autumn", fill=1.0, exp=0.1, note="wide: both of us in the middle, two matches held out in the dark (never lit)")
S("L46.1", X((0.0, -1.6, 8.2), (0.0, -0.5, 8.0), 40, (0.0, -1.3, 8.2), (0.0, -0.5, 8.0), 46), "autumn", fill=1.1, hand=0.002, exp=0.1, note="two matches held out")
pose("me", "L47", 0.3, expr="shut", arms=[0, 0], head=[0, 0])
pose("eli", "L47", 0.3, expr="shut", arms=[0, 0], head=[0, 0])
S("L47", X((0.0, -2.0, 8.3), (0.0, -0.5, 8.1), 36, (0.0, -1.7, 8.3), (0.0, -0.5, 8.1), 40), "autumn", fill=1.1, exp=0.1, hand=0.002, note="my face and Eli's, side by side, eyes shut")
S("L47.1", X((0.3, -1.7, 8.3), (0.0, -0.5, 8.1), 34, (0.2, -1.5, 8.3), (0.0, -0.5, 8.1), 38), "autumn", fill=1.1, hand=0.002, exp=0.1, note="eyes shut")
gone("me", "L48")
gone("eli", "L48")
show("L48", *[x for x in SH if x != "matchpair"])
count("L48", 3)
bridge("L48", 3)
put("eli", "L48", EL, -90, "smile", arms=[0, 100])
pose("eli", "L48+0.7", 0.25, arms=[0, 80], head=[10, 0])
pose("eli", "L48+1.3", 0.25, arms=[0, 110], head=[-8, 0])
S("L48", at_eli(2.6, 30, -0.3, z2=0.6, d2=2.0, lens2=33), "april", note="spring: Eli at his window waving for the first time")
put("me", "L48.2", ME, 90, "blank", head=[0, 0])
S("L48.2", at_me(2.4, 30, 0.25, z2=0.6, d2=1.9, lens2=34), "april", note="me watching him, a stranger again")
S("L48.3", X((-1.3, -1.4, 7.9), (2.0, -0.3, 7.2), 24, (-1.0, -1.2, 7.8), (2.1, -0.3, 7.3), 26), "april", note="the first time")
gone("me", "L49")
gone("eli", "L49")
burnt("L49", [4.2, 3.5, 3.2], sway=0.6, tilt=[0.12, 0.06, 0.06])
count("L49", 64)
bridge("L49", 22)
S("L49", X((0.0, -4.0, 2.6), (0.0, 0.5, 6.2), 22, (0.0, -3.4, 3.2), (0.0, 0.5, 6.4), 24), "night", fill=1.2,
  note="the three burnt bridges at night from below, raised toward our windows, string lights over them")
S("L49.1", X((-2.6, -0.2, 7.7), (0.4, 0.6, 5.0), 22, (-2.5, -0.2, 7.6), (0.4, 0.6, 5.2), 24), "night", fill=1.0, note="rising when it gets cold")
S("L49.2", X((-0.45, 0.55, 5.8), (0.0, 0.55, 4.35), 22, (-0.3, 0.55, 5.5), (0.0, 0.55, 4.35), 24), "night", fill=1.2, torch=[0.0, 0.55, 4.3, 0.0, -0.4], hand=0.002, hold=True, note="a burnt bridge remembers: the handprint plank")
S("L49.3", X((0.45, 0.55, 5.6), (0.0, 0.55, 4.35), 24, (0.3, 0.55, 5.3), (0.0, 0.55, 4.35), 26), "night", fill=1.2, hand=0.002, hold=True, note="what the two of you forgot")
burnt("L49.4", [6.1, 5.3, 5.0], sway=0.5, tilt=[0.5, 0.3, 0.25])
S("L49.4", X((-2.6, -0.2, 7.7), (0.0, 0.6, 5.4), 22, (-2.5, -0.1, 7.6), (-0.4, 0.6, 6.0), 24), "night", fill=1.0, note="and reaches back")
S("L49.5", X((-3.2, 0.2, 7.7), (-1.4, 0.55, 7.0), 30, (-3.0, 0.3, 7.6), (-1.4, 0.55, 7.0), 34), "night", fill=1.0, hand=0.003, note="on the night it burned")

# ===================================================================================================== 08 the turn L50-L53
burnt("L50", [0.0, 0.0, 0.0])
put("me", "L50", ME, 90, "worried", arms=[0, 0], side=[0, 60], head=[0, 14])
S("L50", at_me(2.4, 30, 0.2, z2=0.7, d2=1.9, lens2=34), "winter", note="me at my window pointing down at the handprints")
S("L50.1", X((0.0, -1.0, 9.0), (0.0, 0.55, 0.0), 26, (0.0, -0.7, 8.4), (0.0, 0.55, 0.0), 30), "winter", note="down at the handprints")
put("eli", "L50.2", EL, -90, "blank", head=[0, 22])
S("L50.2", at_eli(2.4, 30, -0.3, z2=0.6, d2=1.9, lens2=34), "winter", note="Eli staring at the matches, blank, like a stranger")
S("L50.3", X((0.5, 0.0, 7.7), (1.42, 0.5, 6.98), 36, (0.8, 0.2, 7.5), (1.42, 0.5, 6.98), 44), "winter", hand=0.002, dof=[1.1, 2.8], note="the matches on his sill")
S("L50.4", at_eli(1.9, 34, -0.2, dz=0.3, z2=0.4, d2=1.6, lens2=40), "winter", note="like he'd never seen them before")
SH.remove("matches")
pose("eli", "L51", 0.3, arms=[0, 60], side=[0, 10], expr="blank", head=[0, 20])
pose("eli", "L51+0.6", 0.25, arms=[0, 0], side=[0, 0], expr="soft", head=[0, 8])
show("L51+0.35", *SH)
S("L51", X((0.5, -1.0, 7.4), (2.0, -0.7, 7.0), 40, (0.8, -0.9, 7.3), (1.9, -0.7, 7.0), 46), "winter", hand=0.002, note="his hand at the end of his sleeve sweeps the box into his pocket")
S("L51.1", at_eli(2.0, 34, -0.3, z2=0.4, d2=1.6, lens2=40), "winter", note="the matches in his pocket")
pose("eli", "L52", 0.3, expr="smile", head=[0, 0], arms=[0, 0])
S("L52", at_eli(2.3, 30, -0.2, z2=0.55, d2=1.8, lens2=34), "winter", note="Eli grins across the bridge: so I'd have to miss you?")
S("L52.1", X((0.0, -1.2, 8.0), (1.3, -0.5, 7.5), 28, (0.3, -1.0, 7.9), (1.5, -0.5, 7.5), 32), "winter", note="across the bridge, toward him")
pose("me", "L53", 0.25, expr="laugh", head=[0, 0], side=[0, 0])
S("L53", at_me(2.2, 30, 0.2, z2=0.6, d2=1.7, lens2=34), "winter", note="me, laughing: good")
S("L53.1", X((0.0, -1.6, 8.2), (0.0, -0.5, 7.2), 26, (0.0, -1.2, 8.0), (0.0, -0.5, 7.2), 29), "winter", note="both of us, laughing across the bridge")

# ===================================================================================================== 09 the loophole L54-L61
pose("eli", "L54", 0.3, expr="laugh")
S("L54", X((0.0, -6.0, 13.5), (0.0, -0.3, 3.0), 22, (0.0, -5.2, 12.5), (0.0, -0.3, 3.5), 24), "winter", hand=0.003,
  note="the alley from above: our bridge whole, the burnt three flat and still")
S("L54.1", X((-0.6, -2.4, 9.6), (0.2, 0.2, 2.0), 24, (-0.4, -1.8, 9.2), (0.2, 0.2, 2.0), 26), "winter", note="the burnt three, still")
gone("me", "L55")
S("L55", X((-1.3, -0.5, 7.5), (3.2, -0.5, 7.6), 20, (1.4, -0.5, 7.5), (6.5, -0.5, 8.4), 22), "winter", hand=0.003,
  note="along our bridge to Eli's window, and past it, to the open sky")
S("L55.1", X((1.0, -1.1, 7.7), (7.0, -0.5, 9.5), 22, (3.5, -1.0, 7.8), (9.0, -0.3, 11.0), 24), "winter", hand=0.003, note="past the window, to the sky")
gone("eli", "L56")
cast["eli_sea"] = dict(cast["eli"], extras=["backpack"], extra_c="#e0573f")
acting["eli_sea"] = []
walk("eli_sea", "L56", (0.3, 24.0, 0.0), "L56>", (0.1, 33.0, 0.0), 180, "smile")
pose("eli_sea", "L56+1.1", 0.4, arms=[0, 0], side=[0, 100])
S("L56", X((-0.4, 14.0, 1.4), (0.2, 28.0, 1.5), 22, (-0.3, 17.0, 1.5), (0.2, 32.0, 1.5), 24), "dawn", fill=1.1,
  note="the end of the lane at dawn: Eli with his sea bag, walking toward the sea")
S("L56+0.6", C((0.1, 31.0, 1.5), 3.2, 20, 4, 26, d2=2.6), "dawn", fill=1.1, note="Eli turns and waves back")
gone("eli_sea", "L57")
count("L57", 65)
put("me", "L57", ME, 90, "soft", head=[0, 8])
cue("L57", "frost", on=True)
S("L57", at_me(2.3, 30, 0.25, z2=0.6, d2=1.8, lens2=34), "winter", note="winter: me at my window, frost on the glass, soft")
S("L57.1", X((-0.7, -1.0, 8.1), (-2.3, -0.5, 7.3), 28, (-1.0, -0.9, 7.9), (-2.3, -0.5, 7.3), 32), "winter", note="frost on my window")
cue("L58", "frost", on=False)
gone("me", "L58")
count("L58", 66, 100, 2.0)
cue("L58", "sea", n=0, n_to=8, dur=2.0)
S("L58", X((-2.6, -0.5, 7.9), (2.4, -0.5, 6.95), 22, (-2.5, -0.5, 7.8), (2.6, -0.5, 6.95), 24), "night", fill=1.2, hand=0.003, note="night: a new plank appears past Eli's window, the counter ticks")
S("L58.1", X((-0.3, -2.4, 8.4), (1.9, -0.5, 6.95), 30, (0.0, -2.2, 8.3), (2.2, -0.5, 6.95), 34), "night", fill=1.2, hand=0.002, note="the new plank")
count("L59", 100, 150, 2.4)
cue("L59", "sea", n=8, n_to=150, dur=2.6)
S("L59", X((-8.0, -9.0, 15.0), (7.0, 4.0, 12.0), 20, (-6.0, -7.0, 14.5), (8.0, 8.0, 13.0), 22), "dusk", fill=0.8, hand=0.004,
  note="wide: the bridge stretches up from Eli's window over the terracotta roofs")
S("L59.1", X((3.0, -8.0, 12.0), (10.0, 4.0, 11.5), 22, (4.0, -6.0, 13.0), (11.0, 8.0, 13.0), 24), "dusk", fill=0.8, note="over the roofs")
count("L60", 150, 190, 1.8)
cue("L60", "sea", n=150, n_to=380, dur=2.0)
S("L60", X((22.0, 10.0, 30.0), (4.0, 70.0, 6.0), 20, (20.0, 20.0, 30.0), (3.0, 90.0, 6.0), 22), "dusk", fill=0.7, hand=0.006,
  note="from high above the town: the bridge going out over the sea, a thin line of planks in the coral dusk")
count("L61", 190, 208, 1.6)
cue("L61", "sea", n=380, n_to=520, dur=1.8)
S("L61", X((14.0, 96.0, 10.0), (-4.0, 144.0, 3.6), 24, (10.0, 106.0, 9.0), (-4.0, 148.0, 3.8), 28), "dusk", fill=0.8, hand=0.004,
  note="far out on the water: the bridge's end, and beyond it a small boat's light")
S("L61.1", X((0.0, 132.0, 6.0), (-5.0, 152.0, 4.0), 30, (-1.0, 138.0, 5.0), (-5.5, 152.0, 4.0), 36), "dusk", fill=0.8, hand=0.004, note="the boat's light")

# ===================================================================================================== 10 the loop L62-L64
count("L62", 208)
cue("L62", "sea", n=520)
put("eli", "L62", (0.4, 12.0, 0.0), 180, "smile")
gone("eli", "L62")
S("L62", X((0.0, -8.2, 2.2), (0.0, 5.0, 6.4), 22, (0.0, -7.4, 2.8), (0.0, 5.0, 6.6), 24), "april", fill=0.9,
  note="spring: the alley, window boxes in bloom, Eli's shutters open")
S("L62.1", at_eli(2.8, 28, -0.4, dz=0.7, z2=0.4, d2=2.3, lens2=30), "april", note="Eli's open window, nobody yet")
S("L62.2", X((1.0, -4.6, 3.0), (1.2, 0.0, 7.0), 24, (1.0, -3.8, 3.4), (1.2, 0.0, 7.0), 26), "april", note="April light on the shutters")
walk("me", "L63", (-0.45, -8.2, 0.0), "L63>", (-0.45, -4.4, 0.0), 180, "smile")
walk("eli", "L63", (0.45, -8.2, 0.0), "L63>", (0.45, -4.4, 0.0), 180, "smile")
S("L63", X((0.0, -8.7, 1.7), (0.0, -3.0, 1.2), 20, (0.0, -8.4, 1.7), (0.0, -3.0, 1.2), 22), "april", fill=1.0, note="me and Eli walking down the cobbles toward the three burnt bridges")
S("L63.1", X((-0.9, -6.0, 1.3), (0.0, -3.0, 1.0), 30, (-0.6, -5.4, 1.3), (0.0, -3.0, 1.0), 32), "april", fill=1.0, note="side by side")
pose("me", "L64", 0.5, yaw=150, expr="smile", head=[20, 0])
pose("eli", "L64", 0.5, yaw=210, expr="smile", head=[-20, 0])
S("L64", C((0.0, -4.4, 1.5), 2.6, 160, 6, 28, d2=2.0), "april", fill=1.0, note="me turning to Eli, both smiling")
S("L64.1", X((0.0, -1.2, 1.8), (0.0, -4.4, 1.4), 26, (-1.25, -1.9, 7.6), (0.9, 0.2, 1.2), 22), "april", fill=1.0, note="then tilt down to the three burnt bridges (the loop)")

# ---------------------------------------------------------------------------------------------------- story
look = {"fog": "#ffe6cf", "fog_density": 0.0015, "fog_start": 40.0, "sky": "#9edcff", "exposure": 0.0, "flash_safe": True,
        "style": "closer",
        "polish": {"emph": ["L01", "L26", "L33", "L36", "L44", "L48", "L52", "L53"], "reveal": ["L36", "L44", "L48"],
                   "twist": "L44", "sway": SWAY, "hold": HOLD, "camera": True, "idle": True, "ease": True}}
story = {
    "slug": "ep100-window-bridges",
    "title": "Three Burnt Bridges To A STRANGER \U0001F309",
    "made_for_kids": False,
    "premise": "In our seaside town every friendship builds a little plank bridge between two windows, and burning one makes "
               "both friends forget the other ever lived. Three burnt bridges lie in the alley under my window, all running "
               "to the window of a man I have never met, and when the nights get cold they start to rise toward us.",
    "twist": "The stranger is Eli, my best friend. Every year the night before his boat ships out we stand in the middle of "
             "our bridge and burn it together so neither of us has to miss the other, and every spring we meet for the first "
             "time. This year we keep the bridge, it grows past his window out over the sea, and I tell him how it started.",
    "world": "a bright cobbled alley between tall terracotta and ochre houses with teal shutters, dozens of plank bridges "
             "strung between facing windows, and the sea glittering at the end of the lane",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff6f61",
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
    "set_moves": [],
    "clip_ok": [],
    "music": {"root": 45, "mode": "major", "bpm": 104, "seed": 100,
              "sections": [
                  {"at": 0, "voices": ["pluck", "pulse", "pad"], "energy": 0.5},
                  {"at": "L25", "voices": ["pluck", "pad"], "energy": 0.4, "mode": "minor"},
                  {"at": "L26", "voices": ["drone", "pad", "pluck"], "energy": 0.5, "mode": "minor"},
                  {"at": "L44", "voices": ["drone", "pluck"], "energy": 0.32, "mode": "minor"},
                  {"at": "L49", "voices": ["pad", "pluck"], "energy": 0.4, "mode": "major"},
                  {"at": "L54", "voices": ["pad", "pluck", "pulse", "pluck_hi"], "energy": 0.6, "mode": "major"},
                  {"at": "L62", "voices": ["pad", "pluck"], "energy": 0.3, "mode": "major"},
              ]},
    "sound": {
        "rev": 1, "floor": "stone", "steps_db": -22,
        "ambience": [{"kind": "gulls", "from": 0, "to": "L25", "lufs": -46},
                     {"kind": "water", "from": 0, "to": "L25", "lufs": -44},
                     {"kind": "crickets", "from": "L25", "to": "L43", "lufs": -42},
                     {"kind": "water", "from": "L54", "to": "end", "lufs": -44}],
        "sfx": [
            {"at": "L01.2+0.05", "kind": "hit", "db": -12},
            {"at": "L01.2+0.05", "kind": "creak", "db": -16, "dur": 1.0},
            {"at": "L04", "kind": "knock", "db": -22, "pattern": [0], "tone": "soft"},
            {"at": "L12.1", "kind": "knock", "db": -22, "pattern": [0], "tone": "soft"},
            {"at": "L26.1", "kind": "creak", "db": -22, "dur": 1.4},
            {"at": "L29", "kind": "creak", "db": -22, "dur": 1.4},
            {"at": "L33+0.9", "kind": "knock", "db": -16, "pattern": [0], "tone": "soft"},
            {"at": "L58", "kind": "knock", "db": -22, "pattern": [0], "tone": "soft"},
        ],
        "music_drops": [{"from": "P01", "to": "P01>"}],
    },
}
try:
    from blocky import timeline

    voice = json.loads((HERE.parent / "voice-timings.json").read_text())
    _tl0 = timeline.build({"name": "ep100-window-bridges", "lines": lines, "shots": [{"id": "S0"}], "gap": 0.12, "tail": LOOP,
                           "min_read": 0.15, "cast": cast}, voice)
    AT = timeline.resolver(_tl0["lines"], _tl0["duration"])
    for k in acting:
        acting[k].sort(key=lambda e: AT(e["at"]))
    cues.sort(key=lambda e: AT(e["at"]))
except FileNotFoundError:
    print("no voice-timings yet: acting and cues left unsorted")
try:
    if shots:
        dur_end = _tl0["duration"]
        def _drop():
            for i, sh in enumerate(shots[1:], 1):
                nxt = AT(shots[i + 1]["at"]) if i + 1 < len(shots) else dur_end
                if sh["_opt"] and nxt - AT(sh["at"]) < MIN_SHOT:
                    return shots.pop(i)
            return None
        while _drop():
            pass

        def _merge():
            for i, sh in enumerate(shots[1:], 1):
                nxt = AT(shots[i + 1]["at"]) if i + 1 < len(shots) else dur_end
                if nxt - AT(sh["at"]) < MIN_PRIMARY:
                    if i + 1 < len(shots) and shots[i + 1]["_opt"]:
                        shots.pop(i + 1)          # this shot runs on over the next, optional one
                    elif i + 1 < len(shots):
                        shots[i + 1]["at"] = sh["at"]   # the next one starts where this one did
                        shots.pop(i)
                    else:
                        shots.pop(i)
                    return True
            return False
        while _merge():
            pass
except NameError:
    pass
for sh in shots:
    sh.pop("_opt", None)
live = {sh["id"] for sh in shots}
HOLD[:] = [x for x in HOLD if x in live]
SWAY[:] = [x for x in SWAY if x in live]
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots, {len(cues)} cues")
