"""Writes ../story.json for "Free Fries, One RULE" (ep83-free-fries, batch 7).

Run from anywhere: python stories/ep83-free-fries/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (hatch, bell, sign, tb, dollar, stove, smell, mgloves, mbA, mbB, dish, cal, hbask, srbox)
and the score.

World (metres, z up, cameras look +y): the diner at the origin (hatch wall at y 3.9, hatch x -0.65..0.65, kitchen door
at x 1.4, our booth bench at y 3.45 with me at x 4.4 and Omar at 5.8, the counter at x -7.4..-2, Mr. Haskins at -4.0),
Mom's kitchen at x 60, our kitchen at x 100, the stockroom at x 140. Acting yaw: 0 faces -y, 180 faces +y, 90 faces +x.
"""
import json
import sys
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
LOOP = 0.25
KM, HM, SR = 60.0, 100.0, 140.0

# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True, "ink": "#24131f"}
cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#8de3c4", "pattern": "stripes", "pattern_c": "#ffffff",
           "pants": "#4a6fa5", "shoes": "#f4f4f2", "sleeves": "long", "hair": "cap", "hair_c": "#c8a15a",
           "face": dict(FACE)},
    "omar": {"age": "adult", "skin": "#a8714a", "shirt": "#e8b923", "pattern": "solid", "pants": "#7d828c",
             "shoes": "#f4f4f2", "sleeves": "long", "hair": "cap", "hair_c": "#14110e", "extras": ["hooddown"],
             "extra_c": "#e8b923", "face": dict(FACE)},
    "mom": {"age": "adult", "skin": "#e0b08a", "shirt": "#c9a8ff", "pattern": "solid", "pants": "#5a5a7a",
            "shoes": "#2a2d3a", "sleeves": "long", "hair": "long", "hair_c": "#4a2e1f", "extras": ["glasses"],
            "extra_c": "#2a2d3a", "face": {"eyes": "lashes", "brows": True, "ink": "#24131f"}},
    "haskins": {"age": "adult", "skin": "#f1c9a0", "shirt": "#f5e8c8", "pattern": "solid", "pants": "#7d828c",
                "shoes": "#2a2d3a", "sleeves": "long", "hair": "cap", "hair_c": "#f2f2f2", "extras": ["tie"],
                "extra_c": "#e23a3a", "face": dict(FACE)},
}

# ---------------------------------------------------------------------------------------------------- state
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {k: [] for k in cast}
cues = []
shots = []
VIS = set()


def raw(who, at, **kw):
    acting[who].append({"at": at, **kw})


def put(who, at, pos, yaw=0, expr="neutral", **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": list(pos), "blend": 0, "yaw": yaw, "expr": expr, "hidden": False, **NEUTRAL, **kw})


def gone(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def scene(at, **chars):
    """Exactly these characters are on stage from `at`; anyone else is hidden. Each value: dict(pos=, yaw=, expr=, ...)."""
    for who in cast:
        if who in chars:
            c = dict(chars[who])
            put(who, at, c.pop("pos"), c.pop("yaw", 0), c.pop("expr", "neutral"), **c)
            VIS.add(who)
        elif who in VIS:
            gone(who, at)
            VIS.discard(who)


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


# ---------------------------------------------------------------------------------------------------- cameras
def pos_of(tg, d, az, el):
    a, e = math.radians(az), math.radians(el)
    return [round(tg[0] + d * math.sin(a) * math.cos(e), 3), round(tg[1] - d * math.cos(a) * math.cos(e), 3),
            round(tg[2] + d * math.sin(e), 3)]


def C(tgt, d, az=0, el=10, lens=30, d2=None, lens2=None, tgt2=None, az2=None, el2=None):
    """A camera aimed at tgt from distance d, azimuth az (0 = from the -y side looking +y, 90 = from +x) and elevation el;
    with d2/tgt2/lens2 it moves there over the shot."""
    k_ = 1.3 if d >= 0.9 else 1.12
    d = d * k_
    d2 = d2 * k_ if d2 is not None else None
    lens = lens * 0.6
    lens2 = lens2 * 0.6 if lens2 else None
    k0 = [0, pos_of(tgt, d, az, el), list(tgt), lens]
    if d2 is None and tgt2 is None and lens2 is None and az2 is None and el2 is None:
        return [k0]
    t2 = tgt2 or tgt
    return [k0, [1, pos_of(t2, d2 if d2 is not None else d, az if az2 is None else az2, el if el2 is None else el2),
                 list(t2), lens2 or lens]]


def S(at, cam, look="day", hand=0.006, dof=None, ring=False, exp=0.0, fill=1.0, step=2, note=""):
    d = {"id": f"S{len(shots) + 1:02d}", "cam": cam, "step": step, "hand": hand}
    if len(shots):
        d["at"] = at
    if look != "day":
        d["look"] = look
    if dof:
        d["dof"] = dof
    if ring:
        d["ring"] = True
    if exp:
        d["exp"] = exp
    if fill != 1.0:
        d["fill"] = fill
    if note:
        d["note"] = note
    shots.append(d)
    return d


# ---------------------------------------------------------------------------------------------------- places
HATCH = (0.0, 3.9, 1.45)
WIN = (1.4, 3.8, 1.58)
ME_SEAT = (4.4, 3.45, -0.23)
OM_SEAT = (5.8, 3.45, -0.23)
MOM_TABLE = (KM - 2.4, 2.25, -0.23)
MOM_COUCH = (KM + 0.4, 2.85, -0.23)
HK_SEATS = {"omar": (HM - 3.15, 2.25, -0.23), "mom": (HM - 2.4, 2.25, -0.23), "me": (HM - 1.65, 2.25, -0.23)}
FIRST_OUT = {"sfx": None}

for k in acting:
    acting[k].append({"at": 0, "pos": [0, 20, 0], "hidden": True, "blend": 0, **NEUTRAL})
cue(0, "sign", tint="pink")


def hatch(at, kind="yellow", s0=0.0, s1=1.0, dur=1.2, basket=True, wig=0.0, second=False):
    cue(at, "hatch", kind=kind, s0=s0, s1=s1, dur=dur, basket=basket, wig=wig, second=second)


# =========================================================================================== 01 L01-L08 the rule at work
hatch(0, dur=1.6)
S(0, C((0.45, 3.9, 1.95), 2.5, 0, 4, 30, d2=2.0), hand=0.004,
  note="frame 1: close on the hatch, yellow gloves sliding a gold basket, the sign above, the dark round window beside")
S("L02", C((1.4, 3.9, 1.6), 1.2, 15, 3, 40, d2=0.9), note="close on the round window, dark, the pink glow on its glass")
hatch("L03", s0=1.0, s1=1.0, wig=0.0, basket=False)
scene("L03", me=dict(pos=(2.6, 0.6, 0), yaw=40, expr="smile"))
raw("me", "L03.1-0.3", pos=[4.4, 2.8, 0])
raw("me", "L03.1", pos=list(ME_SEAT))
S("L03", C((3.7, 2.1, 0.9), 3.0, 0, 4, 30, d2=2.6), note="a customer slides into the booth")
cue("L03.1", "bell")
scene("L03.1")
S("L03.1", C((0.78, 3.7, 1.08), 0.8, 10, 12, 40, d2=0.6), note="the little brass bell dings by itself")
hatch("L04", dur=1.2)
S("L04", C((0, 3.7, 1.08), 1.5, -10, 8, 34, d2=1.1), note="a basket slides out of the hatch")
hatch("L05", s0=1.0, s1=1.0, wig=1.0)
S("L05", C((0, 3.95, 1.2), 0.9, 0, 6, 40, d2=0.7), hand=0.003, note="tighter on the yellow gloves, the dark beyond")
hatch("L06", kind="pink", dur=0.8)
S("L06", C((0, 3.7, 1.1), 1.4, 20, 8, 34, d2=1.1), note="pink gloves")
hatch("L06.1", kind="green", dur=0.8)
S("L06.1", C((0, 3.7, 1.1), 1.4, -20, 8, 34, d2=1.1), note="green gardening gloves")
hatch("L06.2", kind="mitt", dur=0.8)
S("L06.2", C((0, 3.7, 1.1), 1.3, 5, 14, 34, d2=1.0), note="oven mitts with hearts")
hatch("L07", s0=1.0, s1=1.0, basket=False)
scene("L07", haskins=dict(pos=(-4.0, 2.4, 0), yaw=0, expr="smile"))
S("L07", C((-3.8, 2.4, 1.45), 2.2, 0, 3, 38, d2=1.8), note="Mr. Haskins at the counter, a basket beside him")
S("L07.3", C((-4.0, 2.4, 1.55), 1.2, 0, 3, 42, d2=0.95), note="his smile, forty years of it")
scene("L08")
hatch("L08", s0=1.0, s1=1.0, wig=1.0, basket=False)
S("L08", C((0, 3.9, 1.25), 1.5, 0, -14, 28, d2=1.2), note="the hatch from a customer's low angle: gloves only")

# =========================================================================================== 02 L09-L19 the want, the clue, the dare
scene("L09", me=dict(pos=ME_SEAT, yaw=0, expr="laugh"), omar=dict(pos=OM_SEAT, yaw=0, expr="laugh"))
S("L09", C((5.1, 3.45, 1.3), 2.5, 0, 4, 32, d2=2.1), note="our booth: Omar and me laughing")
scene("L09.4", me=dict(pos=ME_SEAT, yaw=0, expr="worried", side=[0.9, 0.9]),
      omar=dict(pos=OM_SEAT, yaw=0, expr="worried", side=[0.9, 0.9]))
S("L09.4", C((5.1, 3.45, 1.3), 2.2, 0, 4, 34, d2=1.8), note="BROKE: pockets out")
scene("L10")
S("L10", C((-2.4, 3.8, 2.6), 1.4, 0, 0, 32, d2=1.0), note="the round wall clock at four")
cue("L11", "tb", on=True)
scene("L11", me=dict(pos=ME_SEAT, yaw=0, expr="smile"), omar=dict(pos=OM_SEAT, yaw=0, expr="grin"))
S("L11", C((5.1, 2.1, 0.8), 1.5, 0, 78, 32, d2=1.15), note="top-down: two baskets, the two gold strokes on the edge")
scene("L12", me=dict(pos=ME_SEAT, yaw=0, expr="soft"))
S("L12", C((4.4, 3.45, 1.35), 1.4, 0, 3, 40, d2=1.0), note="me tasting a fry, eyes closed")
cue("L13", "smell", on=True)
scene("L13")
S("L13", C((KM, 1.1, 1.25), 2.6, 0, 8, 30, d2=2.1), look="eve",
  note="Mom's kitchen across town, evening: the stove cold, the smell of fries a gold shimmer")
cue("L14", "smell", on=False)
S("L14", C((KM - 0.2, 1.15, 1.1), 0.8, 10, 40, 36, d2=0.6), look="eve", note="the cold empty pot")
scene("L15", mom=dict(pos=MOM_TABLE, yaw=0, expr="squeeze", arms=[0, 2.0]))
S("L15", C((KM - 2.4, 2.25, 1.3), 1.9, 0, 4, 36, d2=1.5), look="eve", note="Mom at the table rubbing her eyes")
scene("L16", mom=dict(pos=MOM_COUCH, yaw=0, expr="asleep", head=[0, 0.25]))
S("L16", C((KM + 0.4, 2.85, 1.15), 2.3, 12, 8, 32, d2=1.9), look="eve",
  note="Mom asleep on the couch, glasses on her nose")
scene("L17", me=dict(pos=ME_SEAT, yaw=0, expr="neutral"), omar=dict(pos=OM_SEAT, yaw=-40, expr="grin"))
S("L17", C((5.1, 3.45, 1.3), 2.0, 0, 4, 34, d2=1.6), note="Omar nodding at the kitchen door")
scene("L18", me=dict(pos=ME_SEAT, yaw=0, expr="worried"), omar=dict(pos=OM_SEAT, yaw=0, expr="grin", arms=[1.2, 1.2]))
cue("L18.1", "dollar", on=True)
S("L18", C((5.1, 2.35, 0.8), 1.1, 0, 60, 34, d2=0.9), note="Omar's single green dollar slapped on the table")
scene("L19", me=dict(pos=(1.4, 2.9, 0), yaw=180, expr="worried"))
cue("L19", "dollar", on=False)
S("L19", C((1.4, 3.3, 1.55), 1.8, -28, 3, 38, d2=1.5), note="me at the kitchen door, the round window at eye level")
S("P01", C((1.4, 3.9, 1.58), 1.0, 0, 2, 40, d2=0.8), note="the drop: the round window, still")

# =========================================================================================== 03 L20-L27 the look
scene("L20", me=dict(pos=(1.4, 3.3, 0), yaw=180, expr="worried", lean=0.25))
S("L20", C((1.4, 3.45, 1.55), 1.1, 58, 3, 40, d2=0.85), note="I lean to the glass")
cue("L21", "stove", on=True)
scene("L21")
S("L21", C((KM, 1.95, 1.5), 1.2, 0, 3, 40), look="eve", dof=[0.3, 0.7], ring=True,
  note="through the window: no diner kitchen, a blur of butter yellow")
S("L22", C((KM + 1.3, 3.1, 1.5), 3.0, 0, 3, 26, d2=2.6), dof=[2.9, 6.0], ring=True,
  note="it sharpens: Mom's kitchen, the sink window, the hook")
cue("L23", "mgloves", on=True)
scene("L23", mom=dict(pos=(KM - 0.2, 1.95, 0), yaw=0, expr="asleep", arms=[0.2, 0.2]))
S("L23", C((KM - 0.2, 1.95, 1.5), 2.2, 0, 3, 40, d2=1.7), ring=True, note="Mom at her stove, eyes shut, calm. Cover frame")
cue("L24", "mbA", on=True, dur=1.4, z0=1.35, z1=1.13, y0=1.4)
scene("L24", mom=dict(pos=(KM - 0.2, 1.95, 0), yaw=0, expr="asleep", arms=[1.1, 1.1]))
S("L24", C((KM - 0.2, 1.4, 1.1), 1.3, 0, 12, 36, d2=1.0), ring=True,
  note="her hands at the ends of her sleeves lowering the basket into the oil")
scene("L25", mom=dict(pos=(KM - 0.2, 1.95, 0), yaw=0, expr="blank", arms=[1.1, 1.1]))
S("L25", C((KM - 0.2, 1.95, 1.58), 1.3, 0, 2, 52, d2=1.0), ring=True, note="close: her eyes open")
S("L26", C((KM - 0.2, 1.95, 1.58), 1.0, 0, 0, 52, d2=0.8), ring=True, note="her face straight to camera through the glass")
scene("L27", me=dict(pos=(1.4, 2.5, 0), yaw=0, expr="scared"))
S("L27", C((1.4, 2.5, 1.58), 1.1, 0, 2, 44, d2=0.85), note="my face on my side of the glass, the sign's glow on my cheek")

# =========================================================================================== 04 L28-L32 the twist
cue("L28", "sign", tint="gold", dur=0.5)
scene("L28")
S("L28", C((0, 3.8, 2.5), 1.6, 0, 0, 36, d2=1.15), note="the 0.00 sign, its digits ramping from pink to gold")
cue("L29", "sign", tint="pink")
hatch("L29", s0=1.0, s1=1.0, wig=1.0)
S("L29", C((0, 3.9, 1.25), 1.0, 0, 6, 40, d2=0.75), note="the hatch gloves")
scene("L29.3", mom=dict(pos=(KM - 0.2, 1.95, 0), yaw=0, expr="asleep", arms=[1.1, 1.1]))
S("L29.3", C((KM - 0.2, 1.7, 1.25), 1.6, 0, 6, 36, d2=1.2), note="Mom's kitchen, her hands in the same yellow gloves")
cue("L29.5", "mgloves", on=True)
S("L29.5", C((KM - 0.2, 1.4, 1.0), 0.8, 0, 14, 40, d2=0.6), ring=False, note="in their OWN gloves")
cue("L30", "mgloves", on=False)
scene("L30", mom=dict(pos=MOM_COUCH, yaw=0, expr="asleep", head=[0, 0.25]))
S("L30", C((KM + 0.4, 2.85, 1.15), 2.3, 12, 8, 32, d2=1.9), look="eve", note="Mom asleep on the couch")
scene("L31", mom=dict(pos=MOM_TABLE, yaw=0, expr="worried"))
S("L31", C((KM - 2.4, 2.25, 1.35), 1.9, 0, 4, 36, d2=1.5), look="eve", note="Mom at the table, tired")
cue("L32", "stove", on=True)
scene("L32")
S("L32", C((KM, 1.0, 1.3), 3.0, 0, 18, 28, d2=2.4), look="eve", note="Mom's kitchen from the doorway, a pot on, warm light")

# =========================================================================================== 05 L33-L40 the turn
cue("L33", "hatch", kind="yellow", s0=0.0, s1=1.0, dur=1.2, basket=True, wig=0.0, second=True)
S("L33", C((0.15, 3.7, 1.1), 1.4, 10, 6, 36, d2=1.1), note="a second basket sliding out, toward Omar")
cue("L34", "mbA", on=True, dur=0.01, z0=1.13, z1=1.13)
cue("L34", "mbB", on=True, dur=1.4, z0=1.35, z1=1.13, y0=1.4)
cue("L34", "mgloves", on=True)
scene("L34", mom=dict(pos=(KM + 0.25, 1.95, 0), yaw=0, expr="asleep", arms=[1.1, 1.1]))
S("L34", C((KM + 0.1, 1.95, 1.4), 2.0, 0, 3, 40, d2=1.6), ring=True, note="through the window: Mom setting a second basket in the oil")
cue("L35", "mgloves", on=False)
scene("L35", mom=dict(pos=HK_SEATS["mom"], yaw=0, expr="smile"), omar=dict(pos=HK_SEATS["omar"], yaw=0, expr="grin"),
      me=dict(pos=HK_SEATS["me"], yaw=0, expr="smile"))
S("L35", C((HM - 2.4, 2.25, 1.25), 3.1, 0, 5, 30, d2=2.6), note="our kitchen table: Mom, me and Omar at dinner, Omar's plate full")
scene("L36", omar=dict(pos=(HM - 0.45, 1.95, 0), yaw=0, expr="grin", arms=[1.0, 1.0]),
      me=dict(pos=(HM + 0.35, 1.95, 0), yaw=0, expr="smile", arms=[1.0, 1.0]),
      mom=dict(pos=HK_SEATS["mom"], yaw=0, expr="laugh"))
S("L36", C((HM - 1.2, 2.0, 1.25), 4.0, 0, 6, 28, d2=3.4), note="Omar and me at the stove, Mom laughing at the table")
cue("L37", "dish", which="pan")
scene("L37")
S("L37", C((HM - 0.2, 0.95, 1.0), 0.9, 15, 40, 36, d2=0.65), note="a pan of noodles")
cue("L38", "dish", which="tray")
S("L38", C((HM + 0.3, 0.95, 1.0), 0.9, -15, 40, 36, d2=0.65), note="a tray of something baked")
cue("L38+0.65", "dish", which=None)
cue("L38+0.65", "cal", dur=0.8)
S("L38+0.65", C((HM + 1.2, 3.38, 1.55), 1.0, 0, 0, 36, d2=0.8), note="a calendar page flipping")
cue("L39", "cal", dur=0.01)
hatch("L39", kind="ours", dur=1.1)
scene("L39", mom=dict(pos=(-1.1, 3.0, 0), yaw=0, expr="smile"))
S("L39", C((-0.5, 3.2, 1.35), 3.2, 0, 4, 30, d2=2.7), note="the diner at noon: Mom waits, a basket slides out in a mustard sleeve and a denim cuff")
scene("L40", mom=dict(pos=(0.2, 2.2, 0), yaw=0, expr="soft", arms=[3.0, 3.0]))
hatch("L40", s0=0.0, s1=0.0, basket=False)
S("L40", C((0.2, 2.2, 1.45), 2.4, 0, 4, 32, d2=1.9), note="Mom stretching, rested")

# =========================================================================================== 06 L41-L43 the sting and the loop
scene("L41", mom=dict(pos=(-1.0, 3.0, 0), yaw=120, expr="smile", arms=[1.5, 0]))
S("L41", C((-1.0, 3.0, 1.45), 2.2, 55, 3, 36, d2=1.8), note="Mom at the diner counter, pointing at the hatch")
cue("L41.2", "srbox", x0=SR - 1.0, x1=SR + 0.2, y0=1.3, y1=1.3, dur=1.4)
scene("L41.2", me=dict(pos=(SR - 1.2, 0.9, 0), yaw=90, expr="neutral", arms=[0.9, 0.9]),
      omar=dict(pos=(SR - 0.6, 1.7, 0), yaw=90, expr="neutral", arms=[0.9, 0.9]))
raw("me", "L41.2+1.4", pos=[SR + 0.2, 0.9, 0])
raw("omar", "L41.2+1.4", pos=[SR + 0.8, 1.7, 0])
S("L41.2", C((SR, 1.3, 1.2), 3.4, 0, 5, 30, d2=3.0), note="Omar and me at work in a stockroom, mid-step, carrying a box")
cue("L42", "srbox", x0=SR, x1=SR, y0=1.3, y1=1.3, dur=0.1)
scene("L42", me=dict(pos=(SR - 0.45, 1.5, 0), yaw=0, expr="shut"), omar=dict(pos=(SR + 0.45, 1.5, 0), yaw=0, expr="shut"))
S("L42", C((SR, 1.5, 1.55), 1.9, 0, 3, 36, d2=1.5), note="we blink")
cue("L42.2", "hbask", on=True)
cue("L42.2", "stove", on=True)
scene("L42.2", omar=dict(pos=(HM - 0.45, 1.95, 0), yaw=0, expr="wide", arms=[1.0, 1.0]),
      me=dict(pos=(HM + 0.35, 1.95, 0), yaw=0, expr="wide", arms=[1.1, 1.1]))
S("L42.2", C((HM, 1.95, 1.35), 2.7, 0, 5, 30, d2=2.3), note="at our apartment stove side by side, a fry basket in my hands")
S("L42.3", C((HM + 0.35, 1.3, 1.1), 1.0, 0, 14, 38, d2=0.75), note="holding a fry basket")
cue("L43", "hbask", on=False)
cue("L43", "stove", on=False)
scene("L43")
hatch("L43", dur=1.6)
S("L43", C((0.45, 3.9, 1.95), 2.6, 0, 4, 30, d2=2.5), hand=0.004, note="the hatch again, back to S01's framing. Loop")

# ---------------------------------------------------------------------------------------------------- story
look = {"fog": "#cfeeff", "fog_density": 0.0, "fog_start": 30.0, "sky": "#cfeeff", "exposure": 0.0, "flash_safe": True,
        "style": "closer",
        "polish": {"emph": ["L01", "L12", "L20", "L26", "L28"], "reveal": ["L28"], "twist": "L28",
                   "quiet": [["L36", "L38"]], "sway": ["S22", "S23"], "camera": True, "idle": True, "ease": True}}
story = {
    "slug": "ep83-free-fries",
    "title": "Free Fries, One RULE \U0001F35F",
    "made_for_kids": False,
    "premise": "At this diner the fries are free, forever. Two yellow gloves slide every basket out of the order hatch, "
               "nobody has seen the cook, and the one rule is never look in the kitchen. My best friend Omar and I are "
               "broke, so we sit in the same booth every day at four. My fries taste just like my mom's, her kitchen "
               "across town smells of fries though nobody's cooked, and she's asleep on the couch by five. Omar bets me "
               "his last dollar I won't look.",
    "twist": "Through the kitchen door's round window is my mom's kitchen: she fries my basket in her own yellow gloves, "
             "eyes shut, every afternoon, never knowing. Whoever cooks for you most makes your fries, so Omar and I start "
             "cooking dinner for her every night until we are the ones who cook for her most. Now the second she orders, "
             "we blink and we're at our stove holding a fry basket.",
    "world": "a small bright retro diner in afternoon sun with a mint booth, a chrome order hatch under a round glowing "
             "0.00 sign and a kitchen door with one round window, and a yellow home kitchen across town",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffc21a",
    "gap": 0.12,
    "tail": LOOP,
    "min_read": 0.15,
    "fade_in": False,
    "fade_out": False,
    "look": look,
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.015, -0.02], "saturation": 1.12, "contrast": 1.05,
              "vignette": 0.15, "bloom": 0.3, "grain": 0.008, "red_line": 0.7},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "set_moves": [],
    "music": {"root": 53, "mode": "major", "bpm": 132, "seed": 83,
              "sections": [
                  {"at": 0, "voices": ["bubble", "pulse", "pluck_hi"], "energy": 0.6},
                  {"at": "L12", "voices": ["bubble", "pulse", "pluck", "pad"], "energy": 0.55},
                  {"at": "L20", "voices": ["drone", "pad", "pluck"], "energy": 0.4, "mode": "minor"},
                  {"at": "L28", "voices": ["drone", "pad"], "energy": 0.5, "mode": "minor"},
                  {"at": "L33", "voices": ["pad", "pluck", "bubble"], "energy": 0.45, "mode": "major"},
                  {"at": "L36", "voices": ["pad", "pluck_hi", "bubble", "pulse"], "energy": 0.5, "mode": "major"},
                  {"at": "L41", "voices": ["drone"], "energy": 0.3, "mode": "minor"},
              ]},
    "sound": {
        "rev": 1, "floor": "wood", "steps_db": -22,
        "ambience": [{"kind": "room", "from": 0, "to": "end", "lufs": -40}],
        "sfx": [
            {"at": "L01.3", "kind": "bell", "db": -12},
            {"at": "L03.1", "kind": "ding", "db": -16},
            {"at": "L18.1", "kind": "thud", "db": -16},
            {"at": "L20", "kind": "creak", "db": -20, "dur": 0.9},
            {"at": "L25", "kind": "hit", "db": -26},
            {"at": "L42.2", "kind": "burner", "db": -28, "dur": 1.2},
        ],
        "music_drops": [{"from": "L19>", "to": "P01>"}],
    },
}

vt = HERE.parent / "voice-timings.json"
if vt.exists():
    from blocky import timeline
    voice = json.loads(vt.read_text())
    _tl0 = timeline.build({"name": "ep83-free-fries", "lines": lines, "shots": [{"id": "S0"}], "gap": 0.12, "tail": LOOP,
                           "min_read": 0.15, "cast": cast}, voice)
    AT = timeline.resolver(_tl0["lines"], _tl0["duration"])
    for k in acting:
        acting[k].sort(key=lambda e: AT(e["at"]))
    cues.sort(key=lambda e: AT(e["at"]))
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots, {len(cues)} cues")
