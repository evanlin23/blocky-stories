"""Writes ../story.json for "My Fortune Cookie Was BLANK" (ep121-blank-fortune, batch 12).

Run from anywhere: python stories/ep121-blank-fortune/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (day, cookie, cookie2, slip_*, phone, soda, wallet, pen, drawer, bills, geese, car, snow)
and the score.

World (metres, z up, cameras look +y, characters face -y at yaw 0): the station at the origin (pumps at x -2.0 and 0.4,
y 3, the pickup at x 3.4..7.8), the shop at x 40, the tire at x 80, the lot at x 120, my kitchen at x 160, my bedroom at
x 200, Grandpa's house at x 240, Grandpa's kitchen at x 280 (the doorway to Grandma's chair at y 4.2), the dashboard at x 320.
Hands: the arms are raised 90 degrees and a prop rests on the palm (arms[0] is the screen-left arm, at x - 0.51).
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
XS, XT, XL, XK, XB, XH, XG, XD = 40, 80, 120, 160, 200, 240, 280, 320

# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True, "ink": "#24131f"}
cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#d9a521", "pattern": "plaid", "pattern_c": "#8a5a14",
           "pants": "#3b5a8c", "shoes": "#f4f4f2", "sleeves": "long", "hair": "cap", "hair_c": "#6a4426",
           "hat": "ballcap", "hat_c": "#1c2a5a", "face": dict(FACE)},
    "grandpa": {"age": "adult", "skin": "#e8bf98", "shirt": "#4a76a8", "pattern": "solid", "pants": "#3b5a8c",
                "shoes": "#6a4a2a", "sleeves": "long", "hair": "cap", "hair_c": "#f2f2f2", "hat": "ballcap",
                "hat_c": "#c8372d", "face": dict(FACE)},
    "grandma": {"age": "adult", "skin": "#efc6a0", "shirt": "#b49ae0", "pattern": "solid", "pants": "#5a5a7a",
                "shoes": "#4a3a3a", "sleeves": "long", "hair": "bun", "hair_c": "#d8d8e4", "extras": ["glasses"],
                "extra_c": "#8a6aa8", "face": {"eyes": "lashes", "brows": True, "ink": "#24131f"}},
    "clerk": {"age": "adult", "skin": "#c98f66", "shirt": "#ffffff", "pattern": "solid", "pants": "#3a3f4a",
              "shoes": "#2a2d3a", "sleeves": "short", "hair": "cap", "hair_c": "#5a3a22", "vest": "#3fa860",
              "face": dict(FACE)},
    "tireman": {"age": "adult", "skin": "#d9a27a", "shirt": "#e07a2f", "pattern": "solid", "pants": "#4a4f5c",
                "shoes": "#2a2d3a", "sleeves": "long", "hair": "buzz", "hair_c": "#2a1d15", "face": dict(FACE)},
    "cust": {"age": "adult", "skin": "#b98458", "shirt": "#3f86c8", "pattern": "solid", "pants": "#3a3f4a",
             "shoes": "#f4f4f2", "sleeves": "long", "hair": "buzz", "hair_c": "#1c1410", "face": dict(FACE)},
    "lady": {"age": "adult", "skin": "#e8b894", "shirt": "#e24a6a", "pattern": "solid", "pants": "#5a5a7a",
             "shoes": "#f4f4f2", "sleeves": "long", "hair": "long", "hair_c": "#8a4a2a",
             "face": {"eyes": "lashes", "brows": True, "ink": "#24131f"}},
}

# ---------------------------------------------------------------------------------------------------- state
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {k: [] for k in cast}
cues = []
shots = []
VIS = set()


def put(who, at, pos, yaw=0, expr="neutral", **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": list(pos), "blend": 0, "yaw": yaw, "expr": expr, "hidden": False, **NEUTRAL, **kw})


def raw(who, at, **kw):
    acting[who].append({"at": at, **kw})


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


for k in acting:
    acting[k].append({"at": 0, "pos": [0, 40, 0], "hidden": True, "blend": 0, **NEUTRAL})


# ---------------------------------------------------------------------------------------------------- cameras
def pos_of(tg, d, az, el):
    a, e = math.radians(az), math.radians(el)
    return [round(tg[0] + d * math.sin(a) * math.cos(e), 3), round(tg[1] - d * math.cos(a) * math.cos(e), 3),
            round(tg[2] + d * math.sin(e), 3)]


def C(tgt, d, az=0, el=4, lens=30, d2=None, lens2=None, tgt2=None, az2=None, el2=None):
    """A camera aimed at tgt from distance d, azimuth az (0 = from the -y side looking +y) and elevation el;
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


def S(at, cam, look="day", hand=0.006, fill=1.0, step=2, note="", exp=0.0):
    d = {"id": f"S{len(shots) + 1:02d}", "cam": cam, "step": step, "hand": hand}
    if len(shots):
        d["at"] = at
    if look != "day":
        d["look"] = look
    if fill != 1.0:
        d["fill"] = fill
    if exp:
        d["exp"] = exp
    if note:
        d["note"] = note
    shots.append(d)
    return d


def palm(x, y, side=0, z=1.5):
    return [round(x + (-0.51 if side == 0 else 0.51), 3), round(y - 0.5, 3), z]


def head(x, y, z=1.55):
    return (x, y, z)


ARMS_L, ARMS_R, ARMS_B = [90, 0], [0, 90], [90, 90]
TILT = [35, 0, 0]          # a prop on a palm tipped toward the camera so it reads

# =========================================================================================== 01 L01-L07 the rule at work
ME_P = (1.0, 2.0)
GP_P = (2.4, 2.0)
cue(0, "day", v=0.0)
scene(0, me=dict(pos=ME_P, yaw=0, expr="neutral", arms=ARMS_L))
pc = palm(*ME_P, 0)
cue(0, "cookie", on=True, pos=pc, rot=TILT, s=1.6)
S(0, C((0.75, 1.7, 1.5), 1.25, 0, 12, 30, d2=1.05), hand=0.004,
  note="frame 1: close on the cracked cookie on my flat palm, my face behind it, the tag at Wednesday")
cue("L01.3", "sfx_mark")  # placeholder for readers; the sound itself is in sound.sfx
S("L01.2", C((0.3, 1.5, 1.5), 0.95, 0, 14, 40, d2=0.62), hand=0.003, note="push in on the slip; FRIDAY lands here")
scene("L02", me=dict(pos=ME_P, yaw=0, expr="smile", arms=ARMS_L))
cue("L02", "cookie", on=False, pos=pc)
S("L02", C(head(*ME_P), 2.2, 6, 3, 34, d2=1.8), note="my face at the pump, smiling")
S("L02.2", C((0.2, 3.2, 1.7), 4.6, 12, 6, 30, d2=4.0), note="the canopy and the two pumps, short and close enough")
scene("L03", cust=dict(pos=(XS - 0.3, 1.4), yaw=180, expr="neutral", arms=ARMS_B),
     clerk=dict(pos=(XS + 0.1, 3.95), yaw=0, expr="neutral", arms=[0, 80]))
pc3 = palm(XS - 0.3, 1.4, 0, 1.5)
pc3 = [XS - 0.3 + 0.51, 1.4 + 0.5, 1.5]
cue("L03", "cookie", on=True, pos=[pc3[0], pc3[1], 2.3], pos2=pc3, rot=[0, 0, 0], rot2=[0, 0, 20], dur=0.7, s=1.5)
S("L03", C((XS + 0.15, 2.9, 1.55), 1.6, 8, 8, 32, d2=1.35), note="a cookie drops into a customer's flat palm, the clerk's face behind")
cue("L03.1", "day", v=0.0)
scene("L03.1", cust=dict(pos=(XS - 0.3, 1.4), yaw=180, arms=ARMS_B), clerk=dict(pos=(XS + 0.1, 3.95), yaw=0, expr="neutral", arms=[0, 80]))
S("L03.1", C((XS + 0.1, 2.0, 1.5), 1.3, 14, 14, 38, d2=1.05), note="closer on the cookie in the palm")
# L04: the man with the tire
cue("L04", "cookie", on=False, pos=pc3)
scene("L04", tireman=dict(pos=(XT + 1.5, 2.6), yaw=0, expr="neutral"))
S("L04", C((XT + 1.5, 2.6, 1.5), 2.2, 0, 6, 30, d2=1.9), note="a man at his tire, face to camera")
cue("L04.2", "bills", on=True)
scene("L04.2", tireman=dict(pos=(XT + 1.5, 2.6), yaw=0, expr="wide", arms=[40, 0]))
S("L04.2", C((XT + 1.5, 2.6, 1.5), 1.9, -5, 4, 34, d2=1.5), note="he stares: stunned")
S("L04.3", C((XT + 0.2, 4.0, 1.15), 1.2, 0, 8, 34, d2=0.85), note="close: forty dollars poking out of the tread")
# L05: the woman and the geese
LADY_V = 1.3  # walking speed, split between x and y below
scene("L05", lady=dict(pos=(XL - 3.0, 3.6), yaw=35, expr="worried"))
S("L05", C((XL - 3.0, 3.6, 1.45), 2.0, 0, 5, 30, tgt2=(XL - 2.55, 3.1, 1.45), d2=1.9), note="a woman crossing the lot toward us, face three-quarters to camera")
S("L05.3", C((XL - 2.4, 3.9, 0.6), 2.6, 0, 4, 28, d2=2.4, tgt2=(XL - 1.8, 3.9, 0.6)), note="a line of geese waddling after her, close")
scene("L06", me=dict(pos=(0.9, 2.0), yaw=0, expr="smile"), grandpa=dict(pos=(2.3, 2.0), yaw=0, expr="smile"))
S("L06", C((1.7, 2.3, 1.3), 2.4, 0, 4, 30, d2=2.1), note="Grandpa and me at the pump beside the teal truck; the pump's holster with two gold strokes at the edge")
S("L06.2", C((1.7, 2.1, 1.2), 2.6, -8, 5, 30, d2=2.2), note="a low look at the pump and the holster tally")
scene("L06.3", me=dict(pos=(0.9, 2.0), yaw=0, expr="smile"), grandpa=dict(pos=(2.3, 2.0), yaw=0, expr="smile", arms=[0, 0]))
S("L06.3", C(head(2.3, 2.0, 1.45), 2.4, -12, 4, 32, d2=2.0), note="Grandpa filling up his truck")
scene("L07", grandpa=dict(pos=(2.3, 2.0), yaw=0, expr="warm", arms=ARMS_L))
cue("L07", "cookie2", on=True, pos=palm(2.3, 2.0, 0), rot=TILT, s=1.6)
cue("L07", "slip_ck", on=False)
S("L07", C(head(2.3, 2.0, 1.5), 2.3, 8, 5, 34, d2=1.8), note="Grandpa, reading out loud, warm")
scene("L07.2", me=dict(pos=(0.9, 2.0), yaw=0, expr="neutral", arms=ARMS_R), grandpa=dict(pos=(2.3, 2.0), yaw=0, expr="warm", arms=ARMS_L))
cue("L07.2", "cookie", on=True, pos=palm(0.9, 2.0, 1), rot=TILT, s=1.6)
S("L07.2", C(head(1.2, 2.0, 1.5), 2.3, -6, 5, 34, d2=1.8), note="my face, reading mine; his cookie at the edge")
# =========================================================================================== 02 L08-L15 the blank
HS = [60, 0, 5]            # the blank slip held up toward the camera on my palm
HS2 = [240, 0, 5]          # ... and flipped over
scene("L08", me=dict(pos=(1.4, 2.0), yaw=0, expr="stunned", arms=ARMS_R))
cue("L08", "cookie2", on=False, pos=palm(2.3, 2.0, 0))
cue("L08", "cookie", on=False, pos=palm(0.9, 2.0, 1))
cue("L08", "slip_mine", on=True, pos=[1.4 + 0.51, 1.5, 1.52], rot=HS, s=1.6, prog=0.0)
S("L08", C(head(1.4, 2.0, 1.5), 2.1, 0, 4, 34, d2=1.7), note="my face, stunned, the blank slip on my flat palm")
S("L08.1", C((1.91, 1.6, 1.52), 1.3, 0, 14, 34, d2=1.0), note="the slip, whole, held up")
S("L09", C((1.91, 1.5, 1.52), 0.85, 0, 20, 34, d2=0.75), hand=0.002, note="close: the blank slip, one side")
cue("L09.1", "slip_mine", on=True, pos=[1.91, 1.5, 1.52], rot=HS, rot2=HS2, dur=0.45, s=1.6, prog=0.0)
S("L09.1", C((1.91, 1.5, 1.52), 0.85, 0, 20, 34, d2=0.75), hand=0.002, note="flipped: the other side, blank")
scene("L10", clerk=dict(pos=(XS + 0.1, 3.95), yaw=0, expr="stunned"))
cue("L10", "slip_mine", on=False)
cue("L10", "drawer")
S("L10", C(head(XS + 0.1, 3.95, 1.55), 2.0, 0, 3, 34, d2=1.6), exp=-0.25, note="the clerk, stunned, going pale")
S("L10.1", C(head(XS + 0.1, 3.95, 1.55), 1.5, 8, 3, 36, d2=1.2), exp=-0.25, note="closer on the clerk")
S("L11", C(head(XS + 0.1, 3.95, 1.55), 1.8, -10, 4, 34, d2=1.4), exp=-0.25, note="the clerk, close, telling me")
scene("L11.2", clerk=dict(pos=(XS + 0.1, 3.95), yaw=0, expr="neutral"))
S("L11.2", C(head(XS + 0.1, 3.95, 1.55), 2.0, 6, 3, 30, d2=1.7), exp=-0.25, note="the clerk again, a little back")
scene("L12", grandpa=dict(pos=(XS - 0.3, 3.0), yaw=0, expr="neutral"))
S("L12", C(head(XS - 0.3, 3.0, 1.5), 2.1, 0, 3, 34, d2=1.7), exp=-0.25, note="Grandpa, neutral, looking at the slip")
scene("L13", grandpa=dict(pos=(XS - 0.3, 3.0), yaw=0, expr="smile"))
S("L13", C(head(XS - 0.3, 3.0, 1.5), 1.7, 0, 3, 38, d2=1.4), exp=-0.25, note="Grandpa just smiled")
scene("L14", me=dict(pos=(XS - 0.5, 2.6), yaw=0, expr="worried"),
      grandpa=dict(pos=(XS + 0.7, 2.6), yaw=0, expr="smile"))
S("L14", C((XS + 0.1, 2.6, 1.5), 2.2, 0, 3, 30, d2=2.0), exp=-0.25, note="two-shot: me asking, Grandpa shaking his head")
scene("L15", clerk=dict(pos=(XS + 0.1, 3.95), yaw=0, expr="worried", arms=[0, 80]), me=dict(pos=(XS - 1.0, 2.0), yaw=0, expr="worried"))
cue("L15.2", "soda", on=True, pos=[XS + 0.1 + 0.51, 3.45, 1.55], pos2=[XS + 0.1 + 0.51, 2.7, 1.12], dur=0.6, s=1.8)
S("L15", C(head(XS + 0.1, 3.95, 1.55), 2.0, 0, 3, 34, d2=1.6), exp=-0.25, note="the clerk, uneasy, a soda on his palm")
scene("L15.2", clerk=dict(pos=(XS + 0.1, 3.95), yaw=0, expr="worried", arms=[0, 80]), me=dict(pos=(XS - 0.55, 2.4), yaw=0, expr="worried"))
S("L15.2", C((XS + 0.03, 2.8, 1.35), 2.2, 0, 8, 34, d2=2.0), exp=-0.25, note="the soda slides across; my face beside it")
# =========================================================================================== 03 L16-L19 nothing happens
cue("L16", "soda", on=False, pos=[0, 0, 0])
scene("L16", me=dict(pos=(XK, 1.6), yaw=0, expr="neutral"))
cue("L16", "day", v=0.0, v2=1.0, dur=1.6)
S("L16", C(head(XK, 1.6, 1.55), 2.4, 0, 3, 32, d2=2.0), note="my face at my kitchen window; the needle moves toward Thursday")
scene("L16.2", me=dict(pos=(XK - 0.9, 1.6), yaw=0, expr="neutral"))
S("L16.2", C((XK - 0.5, 2.0, 1.55), 2.2, 0, 2, 26, d2=1.9), note="me at the window, the street through it")
scene("L17")
S("L17", C((XK, 5.0, 1.5), 3.5, 0, 0, 26, d2=3.0), note="my quiet street from my window: nothing happening")
scene("L18", me=dict(pos=(XK, 1.6), yaw=0, expr="worried"))
S("L18", C(head(XK, 1.6, 1.55), 2.0, 5, 2, 36, d2=1.6), note="my face, uneasy")
scene("L19", me=dict(pos=(XB, 3.3, -0.5), yaw=0, expr="worried", blink=False))
cue("L19", "slip_mine", on=True, pos=[XB + 1.15, 3.4, 0.62], rot=[0, 0, 0], s=1.6, prog=0.0)
S("L19", C((XB + 0.5, 3.3, 1.0), 3.0, 0, 6, 28, d2=2.5), look="night", fill=0.7,
  note="me in bed, eyes open; the blank slip on the nightstand")
S("L19.1", C((XB + 1.15, 3.45, 0.62), 0.95, 0, 58, 34, d2=0.8), look="night", fill=0.7, exp=-0.2, note="the slip on the nightstand")
scene("P01")
S("P01", C((XB + 1.15, 3.45, 0.62), 0.85, 0, 55, 34, d2=0.7), look="night", fill=0.7, exp=-0.2, note="the drop: the slip, still")
# =========================================================================================== 04 L20-L24 Grandpa's house
GP = dict(pos=(XG, 3.0, -0.28), yaw=0)
GM = dict(pos=(XG + 0.2, 4.95, -0.25), yaw=0)
TOP = dict(look="night", fill=0.7, exp=-0.15)
cue("L20", "slip_mine", on=False)
cue("L20", "car", x0=XH - 3.6, x1=XH - 1.6, dur=1.0)
scene("L20")
S("L20", C((XH - 1.0, 6.0, 1.5), 8.5, 4, 4, 28, d2=7.8), look="night", note="my car pulling up at Grandpa's house at night, the kitchen window lit")
scene("L21", grandma=dict(GM, expr="asleep", blink=False))
S("L21", C(head(XG + 0.2, 4.95, 1.3), 2.0, 0, 3, 34, d2=1.6), look="night", fill=0.6, note="Grandma asleep in her green armchair")
scene("L22", grandpa=dict(GP, expr="neutral"), grandma=dict(GM, expr="asleep"))
cue("L22", "wallet", on=True)
S("L22", C(head(XG, 3.0, 1.3), 2.3, 0, 8, 32, d2=1.9), look="night", fill=0.6, note="Grandpa at the yellow kitchen table")
S("L22.3", C((XG + 0.1, 2.3, 1.0), 1.5, 0, 18, 34, d2=1.2), look="night", fill=0.6, note="his old wallet on the table, Grandpa's face behind it")
scene("L23")
cue("L23", "slip_gp", on=True, pos=[XG, 1.75, 0.775], rot=[0, 0, 0], s=1.6, prog=0.0)
S("L23", C((XG, 1.58, 0.78), 0.85, 0, 80, 32), **TOP, note="close: a yellowed slip lying open on the table")
scene("L23.2", grandpa=dict(GP, expr="warm"), grandma=dict(GM, expr="asleep"))
S("L23.2", C((XG, 2.4, 0.7), 2.1, 0, 14, 34, d2=1.8), look="night", fill=0.6, note="Grandpa's face behind it, warm")
scene("L24", grandpa=dict(pos=(XG - 0.4, 3.0, -0.28), yaw=0, expr="warm"), grandma=dict(GM, expr="asleep"))
cue("L24", "slip_gp", on=True, pos=[XG, 1.75, 0.775], rot=[0, 0, 0], s=1.6, prog=1.0)
S("L24", C((XG + 0.05, 3.2, 0.95), 2.0, 0, 8, 34, d2=1.8), look="night", fill=0.6,
  note="the reveal picture: Grandpa, the yellow slip covered in blue scribble, Grandma asleep through the doorway")
S("L24.1", C((XG, 1.58, 0.78), 0.9, 0, 78, 32, d2=0.8), **TOP, note="close: the scribble covering the old slip")
# =========================================================================================== 05 L25-L34 the turn
scene("L25")
cue("L25", "slip_mine", on=True, pos=[XG, 1.5, 0.775], rot=[0, 0, 0], s=1.6, prog=0.0)
cue("L25", "slip_gp", on=True, pos=[XG, 2.0, 0.775], rot=[0, 0, 0], s=1.6, prog=1.0)
S("L25", C((XG, 1.6, 0.78), 1.15, 0, 80, 32, d2=1.0), **TOP, note="close: my blank slip beside his")
scene("L25.3", me=dict(pos=(XG - 0.2, 0.6), yaw=0, expr="stunned"), grandpa=dict(GP, expr="warm"),
      grandma=dict(GM, expr="asleep"))
S("L25.3", C(head(XG - 0.2, 0.6, 1.5), 1.8, 0, 3, 36, d2=1.4), look="night", fill=0.9, note="my face, close, stunned")
scene("L26", grandpa=dict(GP, expr="smile"),
      grandma=dict(GM, expr="asleep"))
S("L26", C(head(XG, 3.0, 1.3), 1.9, 0, 4, 36, d2=1.5), look="night", fill=0.6, note="Grandpa, smiling, a nod")
# the two-shot of Grandpa and Grandma: Grandpa left, low; Grandma through the doorway, higher in frame
TS = dict(look="night", fill=0.65)
scene("L27", grandpa=dict(pos=(XG - 0.35, 3.0, -0.28), yaw=0, expr="warm", head=[-25, 0]), grandma=dict(GM, expr="asleep"))
S("L27", C((XG - 0.05, 4.0, 1.35), 4.3, 0, 8, 80, d2=3.9), **TS, note="Grandma asleep, Grandpa's face in the foreground looking at her")
scene("L28", grandpa=dict(GP, expr="warm"), grandma=dict(GM, expr="asleep"))
S("L28", C(head(XG, 3.0, 1.3), 1.8, 0, 4, 36, d2=1.4), look="night", fill=0.6, note="Grandpa, close, warm")
scene("L29", grandma=dict(GM, expr="smile", blink=False))
S("L29", C(head(XG + 0.2, 4.95, 1.3), 1.9, 0, 3, 34, d2=1.6), look="night", fill=0.6, note="Grandma, asleep, smiling in her sleep")
scene("L30", grandpa=dict(GP, expr="smile"))
S("L30", C(head(XG, 3.0, 1.3), 2.0, 0, 4, 36, d2=1.6), look="night", fill=0.6, note="Grandpa, a little proud")
cue("L31", "snow", on=True)
scene("L31", grandpa=dict(pos=(XG - 1.4, 3.4), yaw=0, expr="warm"))
S("L31", C((XG - 1.8, 3.4, 1.5), 2.6, 0, 3, 34, d2=2.2), look="night", fill=0.8, note="Grandpa, close, warm, the snowy kitchen window beside him")
cue("L32", "snow", on=False)
scene("L32", grandpa=dict(pos=(XG + 0.2, 2.95, -0.28), yaw=0, expr="neutral", arms=[0, 75]))
cue("L32", "slip_mine", on=False)
cue("L32", "slip_gp", on=True, pos=[XG + 0.7, 2.25, 0.775], rot=[0, 0, 10], s=1.6, prog=1.0)
S("L32", C((XG + 0.45, 2.6, 1.0), 1.9, 0, 18, 36, d2=1.7), look="night", fill=0.6, note="Grandpa, neutral, tapping the old slip with a finger")
scene("L33", grandpa=dict(pos=(XG - 0.35, 3.0, -0.28), yaw=0, expr="smile", head=[-25, 0]), grandma=dict(GM, expr="asleep"))
cue("L33", "slip_gp", on=False)
S("L33", C((XG - 0.05, 4.0, 1.35), 4.3, 0, 8, 80, d2=3.9), **TS, note="Grandpa, a glance at Grandma in the next room")
scene("L34", grandpa=dict(pos=(XG - 0.35, 3.0, -0.28), yaw=0, expr="smile"), grandma=dict(pos=(XG + 0.25, 4.95, -0.25), yaw=0, expr="smile"))
S("L34", C((XG - 0.05, 4.0, 1.35), 4.2, 0, 8, 80, d2=3.8), **TS, note="Grandma asleep, smiling, Grandpa's face in front, smiling")
# =========================================================================================== 06 L35-L38 I write mine
scene("L35")
cue("L35", "pen", on=True)
cue("L35", "slip_mine", on=True, pos=[XG, 1.9, 0.775], rot=[0, 0, 0], s=1.6, prog=0.0)
S("L35", C((XG, 1.5, 0.78), 0.95, 0, 80, 32, d2=0.85), **TOP, note="close: a long dark pen beside my blank slip on the table")
scene("L36", me=dict(pos=(XG, 3.0, -0.28), yaw=0, expr="smile"))
cue("L36", "slip_mine", on=True, pos=[XG, 1.75, 0.775], rot=[0, 0, 0], s=1.6, prog=0.0, prog2=1.0, dur=1.6)
S("L36", C((XG, 2.4, 0.95), 1.6, 0, 16, 34, d2=1.4), look="night", fill=0.7, note="my face over the slip, smiling; blue scribble appears line by line")
scene("L37")
cue("L37", "slip_mine", on=True, pos=[XG, 1.55, 0.775], pos2=[XG, 2.1, 0.775], rot=[0, 0, 0], s=1.6, prog=1.0, dur=1.0)
S("L37", C((XG, 1.65, 0.78), 1.1, 0, 80, 32, d2=0.95), **TOP, note="close: my slip, covered in scribble, slid across to Grandpa")
scene("L38", grandpa=dict(pos=(XG - 0.3, 3.0, -0.28), yaw=0, expr="laugh"), grandma=dict(pos=(XG + 0.25, 4.95, -0.25), yaw=0, expr="laugh"))
S("L38", C((XG - 0.05, 4.0, 1.35), 4.2, 0, 8, 80, d2=3.8), **TS, note="Grandpa laughing, Grandma waking in her chair behind him")
# =========================================================================================== 07 L39-L44 Friday and the loop
MP = (1.3, 2.0)
PH = [palm(*MP, 0)[0], palm(*MP, 0)[1], 1.52]
scene("L39", me=dict(pos=MP, yaw=0, expr="neutral", arms=ARMS_L))
cue("L38>", "pen", on=False)
cue("L39", "slip_mine", on=False)
cue("L39", "phone", on=True, mode="ring", pos=PH, rot=[40, 0, 0], s=2.4)
cue("L39", "day", v=1.0, v2=2.0, dur=0.8)
S("L39", C((0.95, 1.8, 1.5), 1.6, 0, 14, 32, d2=1.3), hand=0.004, note="Friday morning: my phone ringing on my flat palm, my face behind it, the needle at Friday. Cover frame")
cue("L39.1", "phone", on=True, mode="ring", pos=PH, rot=[40, 0, 0], s=2.4)
S("L39.1", C((PH[0] - 0.1, 1.5, 1.52), 0.95, 0, 12, 40, d2=0.8), hand=0.003, note="close on the ringing phone")
scene("L40", me=dict(pos=MP, yaw=0, expr="neutral", arms=ARMS_L))
cue("L40", "phone", on=True, mode="call", pos=PH, rot=[40, 0, 0], s=3.2)
S("L40", C((0.62, 1.5, 1.4), 1.25, 0, 8, 36, d2=1.05), hand=0.004, note="Grandpa on a video call, his face (red cap, white mustache) on the screen; the pump's gauge at zero behind")
scene("L40.1", me=dict(pos=(1.0, 2.0), yaw=0, expr="neutral", arms=ARMS_L), grandpa=dict(pos=(2.3, 2.0), yaw=0, expr="smile"))
S("L40.1", C((1.65, 2.2, 1.3), 2.3, 0, 4, 30, d2=2.0), note="Grandpa at the pump by his empty truck, the gauge at zero")
cue("L41", "phone", on=False, pos=[0, 0, 0])
scene("L41", me=dict(pos=(1.0, 2.0), yaw=0, expr="laugh"))
S("L41", C(head(1.0, 2.0, 1.55), 2.0, 0, 3, 36, d2=1.6), note="my face, laughing")
cue("L41.1", "day", v=2.0, v2=0.0, dur=0.8)
scene("L41.1", me=dict(pos=(1.0, 2.0), yaw=0, expr="smile"), grandpa=dict(pos=(2.3, 2.0), yaw=0, expr="smile"))
S("L41.1", C((1.65, 2.3, 1.3), 2.3, 0, 4, 30, d2=2.0), note="me and Grandpa at the pump, the tag resetting to Wednesday")
scene("L42", grandpa=dict(pos=(XD, 1.4), yaw=0, expr="warm"))
cue("L42", "slip_tape", on=True, pos=[XD, 0.18, 0.99], rot=[90, 0, 0], s=1.3, prog=1.0)
S("L42", C((XD, 0.6, 1.0), 2.4, 0, 4, 34, d2=1.9), note="my slip taped to his dashboard, Grandpa's face beyond it")
cue("L43", "slip_tape", on=False)
scene("L43", me=dict(pos=(1.0, 2.0), yaw=0, expr="smile", arms=ARMS_R), grandpa=dict(pos=(2.5, 2.0), yaw=0, expr="smile", arms=ARMS_L))
cue("L43", "cookie", on=True, pos=palm(1.0, 2.0, 1), rot=TILT, s=2.0)
cue("L43", "cookie2", on=True, pos=palm(2.5, 2.0, 0), rot=TILT, s=2.0)
S("L43", C((1.75, 1.9, 1.45), 2.6, 0, 8, 32, d2=2.3), note="two cookies on our two flat palms, both our faces behind them")
scene("L44", grandpa=dict(pos=(2.4, 2.0), yaw=0, expr="warm", arms=[0, 90]), me=dict(pos=(1.0, 2.0), yaw=0, expr="smile", arms=ARMS_L))
S("L44", C(head(2.4, 2.0, 1.5), 2.2, 0, 6, 34, d2=1.8), note="Grandpa reads his out loud")
scene("L44.1", me=dict(pos=ME_P, yaw=0, expr="neutral", arms=ARMS_L))
cue("L44.1", "cookie2", on=False, pos=palm(2.4, 2.0, 1))
cue("L44.1", "cookie", on=True, pos=pc, rot=TILT, s=1.6)
S("L44.1", C((0.75, 1.7, 1.5), 1.55, 0, 12, 30, d2=1.25), hand=0.004, note="push in on my cookie on my flat palm to S01's first framing. Loop")

# ---------------------------------------------------------------------------------------------------- story
look = {"fog": "#cfeeff", "fog_density": 0.0, "fog_start": 30.0, "sky": "#cfeeff", "exposure": 0.0, "flash_safe": True,
        "style": "closer",
        "polish": {"emph": ["L01.3", "L08.1", "L12.1", "L25.3", "L40.2"], "reveal": ["L24"], "twist": "L25",
                   "quiet": [["L29", "L30"], ["L33", "L34"]], "hold": [], "camera": True, "idle": True, "ease": True}}
story = {
    "slug": "ep121-blank-fortune",
    "title": "My Fortune Cookie Was BLANK \U0001F960",
    "made_for_kids": False,
    "premise": "At the gas station on our highway every fortune cookie comes true by Friday, word for word. A man finds forty "
               "dollars in his tire, geese follow a woman for a week. Every Wednesday my grandpa Ike and I fill up his truck "
               "and read our fortunes out loud. Last Wednesday mine was blank, and the clerk had only seen one blank before.",
    "twist": "A blank is the one fortune you get to write, and it comes true for whoever you hand it to. The other blank "
             "was Grandpa's, fifty years ago: he wrote it for Grandma, 'You will never eat dinner alone', and he has never "
             "missed one. I write mine for him, 'You will never fill up your truck alone', and now I fill his tank every week.",
    "world": "a bright highway gas station with two red pumps under a white canopy and a teal pickup, a shop with a jar of "
             "wrapped cookies, and Grandpa's small yellow kitchen with Grandma's green armchair through the doorway",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffb52e",
    "gap": 0.12,
    "tail": LOOP,
    "min_read": 0.15,
    "fade_in": False,
    "fade_out": False,
    "look": look,
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.015, -0.02], "saturation": 1.25, "contrast": 1.05,
              "vignette": 0.15, "bloom": 0.3, "grain": 0.008, "red_line": 0.7},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "set_moves": [],
    "clip_ok": [],
    "framing_ok": ["S11", "S44", "S69"],
    "music": {"root": 55, "mode": "major", "bpm": 116, "seed": 121,
              "sections": [
                  {"at": 0, "voices": ["pluck_hi", "pulse", "bubble"], "energy": 0.6},
                  {"at": "L16", "voices": ["tick", "pluck", "pad"], "energy": 0.35},
                  {"at": "L20", "voices": ["drone", "pad"], "energy": 0.35},
                  {"at": "L25", "voices": ["pad", "pluck", "musicbox"], "energy": 0.45},
                  {"at": "L35", "voices": ["pluck_hi", "pulse", "bubble", "pad"], "energy": 0.6},
              ]},
    "sound": {
        "rev": 1, "floor": "concrete", "steps_db": -24,
        "ambience": [{"kind": "traffic", "from": 0, "to": "L16", "lufs": -42},
                     {"kind": "room", "from": "L16", "to": "end", "lufs": -42}],
        "sfx": [
            {"at": "L01.3", "kind": "click", "db": -12},
            {"at": "L01.3", "kind": "thud", "db": -16},
            {"at": "L10", "kind": "click", "db": -20},
            {"at": "L23", "kind": "creak", "db": -22, "dur": 0.6},
            {"at": "L05.3", "kind": "squeak", "db": -24},
            {"at": "L14", "kind": "click", "db": -22},
            {"at": "L27", "kind": "click", "db": -22},
            {"at": "L36", "kind": "click", "db": -22},
            {"at": "L38.2", "kind": "ding", "db": -22},
            {"at": "L39", "kind": "chime", "db": -22},
            {"at": "L42.1", "kind": "thud", "db": -20},
        ],
        "music_drops": [{"from": "L19>", "to": "P01>"}],
    },
}

vt = HERE.parent / "voice-timings.json"
if vt.exists():
    from blocky import timeline
    voice = json.loads(vt.read_text())
    _tl0 = timeline.build({"name": "ep121-blank-fortune", "lines": lines, "shots": [{"id": "S0"}], "gap": 0.12, "tail": LOOP,
                           "min_read": 0.15, "cast": cast}, voice)
    AT = timeline.resolver(_tl0["lines"], _tl0["duration"])
    # the lady walks at a steady pace; the geese join her at L05.3
    t0, t1, t2 = AT("L05"), AT("L05.3"), AT("L06")
    # she walks diagonally toward the camera and to the right, so her face is three-quarters on
    vx, vy = LADY_V * 0.5, -LADY_V * 0.48
    p1 = [XL - 3.0 + vx * (t1 - t0), 3.6 + vy * (t1 - t0)]
    p2 = [XL - 3.0 + vx * (t2 - t0), 3.6 + vy * (t2 - t0)]
    acting["lady"].append({"at": "L05.3", "pos": p1, "hidden": True})
    acting["lady"].append({"at": "L06", "pos": p2, "hidden": True})
    cues.append({"at": "L05.3", "name": "geese", "on": True, "x0": p1[0] + 0.5, "x1": p2[0] + 0.7, "y": 3.9, "dur": t2 - t1})
    for k in acting:
        acting[k].sort(key=lambda e: AT(e["at"]))
    cues.sort(key=lambda e: AT(e["at"]))
cues[:] = [c for c in cues if c["name"] != "sfx_mark"]
story["rev"] = 8
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots, {len(cues)} cues")
