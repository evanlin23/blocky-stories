"""Writes ../story.json for "Our Cat Brings Home WARM Shoes" (warm-shoes, batch 6 P1).

Run from anywhere: python stories/warm-shoes/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast (me, Dad, the Strider), the shots and
their cameras, the acting, the cues set.py reads (count, pairs, cat, strider, flap, tap, bus, car, props) and the score.

World (metres, z up, the house front faces -y): the porch deck at y -3.2..0 (top z 0.4), the front door at x 0..1, the
mat at (0.62, -0.85), the rail ledge at y -3 (z 1.43) with twelve slots, the slate panel at (1.1, -2.85), the gate at
y -9 between posts at x +-1.2, the road down -y with eight streetlights at y -14 - 10k, the bus shelter at y -96.
My room is x -7.2..-1.7 (window at x -4.4..-2.6), the hall is to its right. Acting yaw: 0 faces -y, 180 faces +y,
90 faces +x, -90 faces -x.
"""
import json
import sys
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
LOOP = 0.25

# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True, "ink": "#24131f"}
cast = {
    "me": {"age": "teen", "skin": "#f1c9a0", "shirt": "#1fb3a8", "pattern": "solid", "pants": "#8a8d96",
           "shoes": "#f4f4f2", "sleeves": "long", "hair": "swoop", "hair_c": "#6a4426", "extras": ["hooddown"],
           "extra_c": "#1fb3a8", "face": dict(FACE)},
    "dad": {"age": "adult", "skin": "#d9a27a", "shirt": "#c0392b", "pattern": "plaid", "pattern_c": "#1c2a5a",
            "pants": "#3b5a8c", "shoes": "#b98a4e", "sleeves": "long", "hair": "none", "hat": "ballcap",
            "hat_c": "#1c2a5a", "width": 1.12, "face": dict(FACE)},
    "strider": {"age": "adult", "skin": "#4b3321", "shirt": "#7a5230", "pattern": "stripes", "pattern_c": "#93663a",
                "pants": "#7d5530", "shoes": "#14110e", "sleeves": "long", "hair": "none", "extras": ["coat"],
                "zip_c": "#7d5530", "height": 1.5, "width": 0.82,
                "face": {"eyes": "hollow", "brows": False, "mouth": "none", "ink": "#24131f", "eye_scale": 0.6}},
}

# ---------------------------------------------------------------------------------------------------- state
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {k: [] for k in cast}
cues = []
shots = []
PS = {}          # the "pairs" cue's whole state
CS = {}          # the "strider" cue's state


def raw(who, at, **kw):
    acting[who].append({"at": at, **kw})


def put(who, at, pos, yaw=0, expr="neutral", **kw):
    """The character is there from this instant (a cut), everything it doesn't set back to neutral."""
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


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def pairs(at, **kw):
    for k, v in kw.items():
        if v is None:
            PS.pop(k, None)
        else:
            PS[k] = v
    cues.append({"at": at, "name": "pairs", **json.loads(json.dumps(PS))})


def pr(pos, yaw=0, steam=False, scale=1.0):
    return {"pos": list(pos), "yaw": yaw, "steam": steam, "scale": scale}


def cat(at, pos=None, **kw):
    if pos is None:
        cues.append({"at": at, "name": "cat", "hidden": True})
    else:
        cues.append({"at": at, "name": "cat", "pos": list(pos), **kw})


def strider(at, **kw):
    CS.update(kw)
    cues.append({"at": at, "name": "strider", **json.loads(json.dumps(CS))})


def count(at, n):
    cue(at, "count", n=n)


# ---------------------------------------------------------------------------------------------------- cameras
def pos_of(tg, d, az, el):
    a, e = math.radians(az), math.radians(el)
    return [round(tg[0] + d * math.sin(a) * math.cos(e), 3), round(tg[1] - d * math.cos(a) * math.cos(e), 3),
            round(tg[2] + d * math.sin(e), 3)]


def C(tgt, d, az=0, el=10, lens=30, d2=None, lens2=None, tgt2=None, az2=None, el2=None):
    """A camera aimed at tgt from distance d, azimuth az (0 = from the -y side looking +y, 180 = from the +y side
    looking -y, 90 = from +x) and elevation el; with d2/tgt2/lens2 it moves there over the shot (a push-in)."""
    k_ = 1.3 if d >= 0.9 else 1.12          # the frame is only ~30 degrees wide: stand back a little from everything
    d = d * k_
    d2 = d2 * k_ if d2 is not None else None
    lens = lens * 0.92
    lens2 = lens2 * 0.92 if lens2 else None
    k0 = [0, pos_of(tgt, d, az, el), list(tgt), lens]
    if d2 is None and tgt2 is None and lens2 is None and az2 is None and el2 is None:
        return [k0]
    t2 = tgt2 or tgt
    return [k0, [1, pos_of(t2, d2 if d2 is not None else d, az if az2 is None else az2, el if el2 is None else el2),
                 list(t2), lens2 or lens]]


def wide(l):
    return round(l * 0.86, 1) if 24 <= l <= 50 else l


def X(loc, tgt, lens, loc2=None, tgt2=None, lens2=None, raw=False):
    if not raw:
        lens, lens2 = wide(lens), (wide(lens2) if lens2 else None)
    ks = [[0, list(loc), list(tgt), lens]]
    if loc2 or tgt2 or lens2:
        ks.append([1, list(loc2 or loc), list(tgt2 or tgt), lens2 or lens])
    return ks


def S(at, cam, look, hand=0.006, dof=None, fill=1.0, sun=1.0, street=1.0, porch=0.0, exp=0.0, step=2, note="", key=0.0, rim=0.0):
    d = {"id": f"S{len(shots) + 1:02d}", "cam": cam, "step": step, "hand": hand, "look": look}
    if len(shots):
        d["at"] = at
    if dof:
        d["dof"] = dof
    for k, v, dflt in (("fill", fill, 1.0), ("sun", sun, 1.0), ("street", street, 1.0), ("porch", porch, 0.0),
                       ("exp", exp, 0.0), ("key", key, 0.0), ("rim", rim, 0.0)):
        if v != dflt:
            d[k] = v
    if note:
        d["note"] = note
    shots.append(d)
    return d


FRAME1 = X((0.72, -0.05, 0.55), (0.80, -2.9, 0.98), 24, (0.68, -0.30, 0.53), None, None, raw=True)


def ST(x=-1.9, tgt=(0, -60, 1.5), lens=16, y=-1.2, z=1.85, lens2=None, tgt2=None):
    """The view from my window / the porch over the rail row: low in the frame, the pairs on the ledge."""
    return X((x, y, z), tgt, lens, None, tgt2, lens2)


# ---------------------------------------------------------------------------------------------------- places
M, A, S_, N, D = "morning", "afternoon", "sundown", "night", "dawn"
MATP = (0.62, -0.85, 0.47)
IMAT = (0.5, 0.85, 0.47)
DECK = 0.4
GATE_R = (1.62, -9.9)


def STR(at, pos, yaw=180, shoes="shiny", lean=0, head=(0, 0), sq=1.0, expr="neutral"):
    """The Strider placed (a cut) at pos, facing yaw, in these shoes; squashed to sq of its height."""
    put("strider", at, pos, yaw, expr, lean=lean, head=list(head), arms=[0, 0], side=[0, 0])
    strider(at, shoes=shoes, sq=sq)


for k in acting:
    acting[k].append({"at": 0, "pos": [0, 20, 0], "hidden": True, "blend": 0, **NEUTRAL})

# =========================================================================================== 01 L01-L05
count(0, 8)
pairs(0, sneaker=pr(MATP, 160, True))
cat(0, (0.1, -0.95, DECK + 0.07), yaw=-90, to=[-1.1, -0.95, DECK + 0.07], dur=0.9, tail="up")
S(0, FRAME1, M, dof=[0.85, 2.4], fill=0.6,
  note="frame 1: the steaming pair on the mat, rail row and chalk 8 soft behind, a tail tip leaving")
S("L01.4", C((0.62, -0.97, 0.6), 0.55, 200, 28, 30, d2=0.38), M, dof=[0.5, 2.0], hand=0.004,
  note="steam rising off the toes on WARM")
pairs("L02", oldsneak=pr((0.32, -0.88, 0.47), 165, False))
S("L02", C((0.47, -0.9, 0.5), 0.8, 20, 80, 30, d2=0.5), M, hand=0.003, note="top-down: the same shoe beside the left warm one")
pairs("L03", work=pr(MATP, 170, True), sneaker=None, oldsneak=None)
S("L03", C((0.62, -0.9, 0.55), 0.8, 25, 14, 30, d2=0.55), M, dof=[0.7, 2.2], note="Monday work boots with sawdust")
pairs("L04", slipper=pr(MATP, 165, True), work=None)
S("L04", C((0.62, -0.9, 0.52), 0.8, -25, 16, 30, d2=0.55), M, dof=[0.7, 2.2], note="Tuesday slippers full of sand")
pairs("L05", tap=pr(MATP, 170, True), slipper=None)
cue("L05.2", "tap")
S("L05", C((0.62, -0.9, 0.52), 0.8, 10, 12, 30, d2=0.55), M, dof=[0.7, 2.2], note="Wednesday one tap shoe, still tapping")

# =========================================================================================== 02 L06-L14
pairs("L06", tap=None, heel=None)
cat("L06", (0.5, -0.3, DECK), yaw=180, pose="stand", face="smug", carry="heel", to=[0.5, 0.42, DECK], dur=1.0, tail="up")
cue("L06", "flapswing", dur=1.2, peak=0.7)
S("L06", X((0.5, 1.55, 0.78), (0.5, 0.1, 0.62), 26, (0.5, 1.2, 0.78), None, 28), M, fill=0.7, note="the flap clacks, Biscuit pushes through with a heel")
cat("L06.2", (0.5, 0.75, DECK), yaw=180, face="smug", carry="heel", tail="up")
pairs("L06.2+0.6", heel=pr((0.5, 0.95, 0.47), 200, True))
cat("L06.2+0.6", (0.5, 0.78, DECK), yaw=180, face="smug", tail="up")
S("L06.2", C((0.5, 0.85, 0.5), 1.1, 175, 18, 28, d2=0.85), M, fill=0.7, note="he drops it on the mat")
# L07: my bed in morning sun, Biscuit asleep on my feet, a warm pair by the door
pairs("L07", heel=None, slipper2=pr((-2.5, 3.0, 0.43), 90, True))
put("me", "L07", (-6.4, 3.95, 0.95), 0, "smirk", lean=-90)
cat("L07", (-6.4, 3.65, 1.12), yaw=0, pose="lie", face="asleep")
S("L07", X((-3.0, 2.0, 1.9), (-6.0, 4.4, 1.0), 24, (-3.3, 2.2, 1.8)), M, fill=0.5, note="my bed in the morning sun, Biscuit asleep on my feet")
gone("me", "L08")
# L08: Dad lines them up on the rail, then the long row
put("dad", "L08", (5.0, -2.3), 0, "angry", arms=[0, 70])
pairs("L08", slipper2=None)
cat("L08")
S("L08", C((5.0, -2.5, 1.5), 1.9, 60, 8, 28, d2=1.5), M, note="Dad sets the slippers at the end of the row")
S("L08.2", X((6.5, -2.0, 1.75), (-3.5, -3.0, 1.45), 26, (6.3, -2.2, 1.7), (-3.5, -3.0, 1.45)), M, note="the long row, toes out")
gone("dad", "L09")
# L09: my hand, the chalk
put("me", "L09", (1.1, -2.0), 0, "neutral", arms=[0, 80])
count("L09.1", 9)
S("L09", C((1.1, -2.85, DECK + 1.62), 1.05, 150, 4, 30, d2=0.8), M, note="my hand rubs out the 8 and chalks a 9")
gone("me", "L10")
# L10: nobody comes
count("L10", 10)
S("L10", ST(-1.9, (0, -60, 1.5), 16), M, street=0.0, note="down the sunny street, nobody coming")
S("L10.2", X((0.2, -3.3, 1.35), (0, -9.0, 0.95), 30, (0.2, -3.9, 1.3)), M, street=0.0, note="the gate, shut, nobody at it")
pairs("L10a", dadboots=pr((-2.2, -3.0, 1.46), 0, False))
cue("L10a", "hide_rail", idx=[])
S("L10a", C((-2.9, -3.0, 1.5), 0.75, 190, 18, 30, d2=0.5), M, dof=[0.7, 2.4], note="a heel of each pair turned up")
cue("L10a.2", "hide_rail", idx=[1])
S("L10a.2", C((-2.2, -3.0, 1.5), 0.7, 200, 20, 30, d2=0.5), M, dof=[0.6, 2.4], note="Dad's boot beside a rail pair, same length")
cue("L11", "hide_rail", idx=[])
pairs("L11", dadboots=None, slipper2=pr((1.35, 0.7, 0.47), 20, True))
S("L11", X((0.9, 1.9, 0.62), (1.7, 0.7, 0.58), 26, (1.0, 1.5, 0.6), (1.7, 0.7, 0.56), 28), M, fill=0.7, note="Biscuit's bowl is full, a warm pair beside it")
# L13: Dad points, the empty carrier
put("dad", "L13", (1.7, -1.6), 155, "angry", arms=[0, 88], head=[0, 0])
cat("L13", (1.0, -2.3, DECK), yaw=60, face="smug", tail="up")
pairs("L13", slipper2=None)
S("L13", X((2.7, -0.3, 1.6), (1.6, -2.0, 1.5), 24, (2.4, -0.5, 1.6)), M, note="Dad points, his face, Biscuit smug on the porch")
cat("L13.2")
gone("dad", "L13.2")
cue("L13.2", "props", carrier={"pos": [1.9, -1.5, DECK + 0.02], "yaw": 160, "scale": 1.3}, bag=None)
S("L13.2", C((1.9, -1.5, 0.75), 1.3, 190, 12, 28, d2=0.95), M, note="an empty cat carrier by the porch door")
# L14: me, determined, Biscuit in my arms, the rail row behind us
put("me", "L14", (0.5, -1.9), 180, "smirk", arms=[60, 60])
cue("L14", "props", carrier=None)
cat("L14", (0.5, -1.62, 0.92), yaw=180, pose="lie", face="neutral", tail="down")
S("L14", X((0.3, -0.3, 1.45), (0.55, -2.5, 1.2), 24, (0.45, -0.7, 1.45)), M, fill=0.7, note="me with Biscuit in my arms")
gone("me", "L15")
cat("L15")

# =========================================================================================== 03 L15-L19 sundown
count("L15", 11)
cue("L15", "bus", on=True, go=True, dur=1.8)
put("dad", "L15", (3.3, -94.0), 0, "neutral")
raw("dad", "L15.2", pos=[3.0, -93.0])
S("L15", X((-1.9, -1.2, 1.9), (3.2, -96, 1.6), 135), S_, hand=0.004, note="the far bus shelter, the bus pulling away, Dad small")
cue("L15.2", "bus", on=False)
gone("dad", "L15.2")
S("L15.2", ST(-1.9, (0.5, -70, 1.4), 16), S_, note="eight streetlights toward our gate, the gold field")
# L16: Dad on the porch step taking his cap off
put("dad", "L16", (0.5, -1.9), 180, "worried", arms=[0, 45], side=[0, 0])
put("me", "L16", (1.5, -1.75), 180, "worried")
S("L16", X((0.8, -0.35, 1.5), (0.7, -2.2, 1.45), 24, (0.9, -0.55, 1.5)), S_, fill=0.9, note="Dad on the step, worried, me beside him")
gone("me", "L16.3")
put("dad", "L16.3", (0.2, -1.5), 0, "worried", head=[0, 0])
S("L16.3", X((0.6, -0.7, 1.9), (-0.6, -30, 1.5), 40, (0.8, -0.8, 1.9)), S_, fill=0.0, note="over his shoulder, one streetlight picked out")
put("dad", "L17", (0.45, -1.7), 180, "worried", arms=[0, 82])
S("L17", X((0.9, -0.3, 1.62), (0.5, -1.7, 1.55), 30, (0.85, -0.5, 1.6)), S_, fill=0.8, note="Dad, a hand up flat: this far")
put("dad", "L18", (0.5, -1.7), 180, "scared")
S("L18", X((0.85, -0.25, 1.6), (0.6, -1.7, 1.6), 28, (0.8, -0.45, 1.58)), S_, fill=0.8, note="Dad, eyes front, the chalk 11 behind")
gone("dad", "L19")
S("L19", X((0.2, -3.3, 1.45), (1.4, -9.0, 1.0), 38), S_, note="the gate and the right gatepost, nobody there")

# =========================================================================================== 04 Thursday L21-L32
put("me", "L21", (-3.5, 0.75), 55, "smirk", side=[0, 70])
S("L21", X((-2.0, 2.2, 1.75), (-3.5, 0.6, 1.8), 32, (-2.2, 1.9, 1.78)), S_, fill=0.8, note="me at my window, curtain held back")
gone("me", "L22")
put("dad", "L22", (0.4, -36.0), 180, "neutral")
raw("dad", "L22+0.9", pos=[0.4, -34.5])
S("L22", ST(-1.9, (0.4, -34, 1.3), 40), S_, note="Dad under the light, small, eyes front")
STR("L23", (0.0, -44.0), 180, "shiny")
put("dad", "L23", (0.4, -34.5), 180, "neutral")
S("L23", ST(-1.9, (0.2, -40, 1.5), 85), S_, hand=0.004, note="one light back, someone")
S("L24", X((-2.0, -1.2, 1.9), (0, -44, 1.45), 135), S_, hand=0.004, note="the Strider under the light, full length")
put("me", "L24.2", (-3.5, 0.75), 55, "scared")
gone("dad", "L24.2")
gone("strider", "L24.2")
S("L24.2", X((-2.1, 1.8, 1.72), (-3.5, 0.6, 1.8), 30, (-2.4, 1.6, 1.75)), S_, fill=0.8, note="me at the window, scared")
gone("me", "L25")
STR("L25", (0.0, -44.0), 180, "shiny")
S("L25", X((1.4, -41.5, 0.3), (0.0, -44.0, 0.12), 36, (1.1, -42.0, 0.25)), S_, hand=0.004, note="shiny black shoes catching the lamp")
gone("strider", "L26")
put("dad", "L26", (0.0, -8.5), 180, "neutral")
raw("dad", "L26.2", pos=[0.0, -5.6])
S("L26", C((0, -7.0, 1.3), 3.2, 180, 8, 32), S_, note="Dad comes in the gate, eyes front")
STR("L26.2", GATE_R, 180, "shiny")
S("L26.2", X((0.6, -4.8, 1.55), (GATE_R[0], GATE_R[1], 1.5), 50, (0.8, -5.0, 1.55)), S_, hand=0.004, note="it stops at our right gatepost")
gone("dad", "L27")
gone("strider", "L27")
cue("L27", "flapswing", dur=1.0, peak=0.7)
cat("L27", (0.5, -0.3, DECK), yaw=180, face="neutral", carry="shiny", to=[0.5, 0.4, DECK], dur=0.6, tail="up")
S("L27", X((0.5, 1.7, 0.8), (0.5, 0.1, 0.62), 26), S_, fill=0.7, note="the cat flap clacks open")
cue("L27+0.45", "flapswing", dur=1.4, peak=0.55)
cat("L27+0.45", (0.5, 0.45, DECK), yaw=180, face="neutral", carry="shiny", to=[0.5, 0.9, DECK], dur=1.0, tail="up")
S("L27+0.45", X((0.95, 1.0, 1.25), (0.5, 0.15, 1.26), 30, (0.85, 0.85, 1.25)), S_, hand=0.002, dof=[1.1, 3.5],
  note="the lore shot: three ginger strokes in the flap's frame")
cat("L28.1", (0.5, 0.7, DECK), yaw=180, face="neutral", carry="shiny", to=[0.5, 0.95, DECK], dur=0.5, tail="up")
S("L28.1", C((0.5, 0.85, 0.5), 1.0, 170, 20, 28, d2=0.75), S_, fill=0.7, note="Biscuit sets the shiny shoes on the mat")
cat("L28.3", (0.5, 0.98, DECK), yaw=170, face="neutral", tail="up")
pairs("L28.3", shiny=pr((0.5, 0.78, 0.47), 175, True))
cat("L29", (0.15, 1.0, DECK), yaw=170, face="neutral", tail="up")
S("L29", C((0.5, 0.78, 0.55), 0.7, 160, 20, 30, d2=0.5), S_, dof=[0.6, 2.2], fill=0.7, note="still warm")
put("me", "L30", (0.5, 1.55), 0, "smirk", lean=42, arms=[70, 70])
cat("L30", (0.5, 0.98, DECK), yaw=180, face="neutral", tail="up")
S("L30", C((0.5, 1.1, 0.8), 1.7, 120, 12, 28, d2=1.4), S_, fill=0.8, note="me crouched by Biscuit, amazed")
cat("L30.3", (0.5, 0.98, DECK), yaw=180, face="slowblink", tail="up")
gone("me", "L30.3")
S("L30.3", C((0.5, 0.98, 0.6), 0.8, 180, 14, 30, d2=0.55), S_, fill=0.8, dof=[0.7, 2.4], note="Biscuit, slow blink")
cat("L31")
pairs("L31", shiny=None)
put("me", "L31", (3.3, 4.0), 0, "smirk", head=[0, 0])
put("dad", "L31", (3.3, 3.0), 180, "neutral")
S("L31", C((3.3, 3.5, 1.5), 1.7, 60, 4, 34, d2=1.4), S_, fill=0.8, note="me smiling, looking up at Dad in the kitchen doorway")
put("me", "L32", (3.3, 4.2), 0, "smirk", arms=[40, 40])
put("dad", "L32", (3.3, 3.0), 180, "angry")
S("L32", C((3.3, 3.6, 1.5), 2.0, 90, 6, 28), S_, fill=0.8, note="I tell Dad, hands up")
gone("me", "L32.1")
put("dad", "L32.1", (2.1, -2.35), 0, "angry", arms=[0, 70])
count("L32.2", 12)
S("L32.1", X((1.55, -1.0, 1.7), (1.9, -2.6, 1.45), 22), S_, fill=0.8, note="Dad puts the shiny shoes on the end of the rail, chalk 12")

# =========================================================================================== 05 Friday L33-L44
gone("dad", "L33")
put("me", "L33", (0.0, -40.0), 180, "neutral")
raw("me", "L33.2", pos=[0.0, -34.5])
S("L33", X((2.0, -26.0, 1.55), (0.0, -37.0, 1.3), 40, (1.8, -26.0, 1.55)), S_, hand=0.01, note="me walking up our road at sundown")
S("L33.2", C((0.0, -35.0, 1.2), 3.8, 150, 6, 36, d2=3.2), S_, hand=0.01, note="closer, the streetlights behind")
gone("me", "L33a")
S("L33a", X((0.3, -27.0, 0.38), (0.0, -37.0, 0.55), 26, (0.3, -27.4, 0.38)), S_, hand=0.003, note="low behind me, one light back, empty")
put("me", "L33a.2", (0.0, -6.0), 180, "worried")
S("L33a.2", C((0.0, -6.0, 1.55), 1.5, 180, 4, 34, d2=1.2), S_, fill=0.9, note="my face, worried, eyes front")
put("me", "L33b", (0.0, -12.0), 180, "scared", run=True)
raw("me", "L33b>", pos=[0.0, -4.4], run=True)
S("L33b", ST(-1.9, (0.0, -9.0, 1.2), 22), S_, note="I run through the gate, the rail row in frame")
gone("me", "L33c")
pairs("L33c", sneaker=pr(MATP, 160, True))
count("L33c", 12)
S("L33c", FRAME1, S_, dof=[0.85, 2.4], fill=0.6, note="the pair on the mat is my size")
put("me", "L34", (0.22, -0.92), 0, "worried")
S("L34", X((1.8, -2.6, 1.6), (0.5, -0.95, 1.15), 24, (1.5, -2.3, 1.55)), S_, fill=0.8, note="me beside the pair, the same shoe")
S("L34.2", C((0.55, -1.0, 0.56), 0.45, 200, 30, 30, d2=0.32), S_, dof=[0.4, 1.8], hand=0.003, note="the matching red laces")
gone("me", "L35")
pairs("L35", sneaker=None)
put("me", "L35", (0.6, -1.9), 180, "smirk")
S("L35", X((0.3, -0.25, 1.5), (0.7, -2.4, 1.35), 24, (0.5, -0.5, 1.5)), S_, fill=0.8, note="I glance at the rail row and the chalk 12")
put("me", "L35.2", (-4.1, 3.4), 0, "smirk")
pairs("L35.2", sneaker=pr((-4.6, 3.9, 0.47), 170, False))
S("L35.2", X((-2.3, 2.4, 1.6), (-4.4, 3.8, 0.6), 26, (-2.9, 2.6, 1.5)), S_, fill=0.8, note="I set the sneakers by my bed")
# 3 AM
put("me", "L36", (-6.4, 4.0, 0.95), 0, "worried", lean=-68)
pairs("L36", sneaker=pr((-4.6, 3.9, 0.47), 170, False))
cue("L36", "props", carrier=None)
S("L36", X((-4.3, 2.0, 1.4), (-6.2, 4.3, 1.4), 26), N, fill=0.0, porch=0.0, street=1.0, note="3 AM, the lamp low, me sitting up")
gone("me", "P01")
S("P01", X((-6.0, 5.0, 1.45), (-3.5, 0.0, 1.9), 30), N, fill=0.0, note="hold on the window, nothing, then a tap")
STR("L37", (-3.5, -1.6), 180, "sneaker", lean=14, head=[0, 0])
S("L37", X((-6.0, 5.0, 1.45), (-3.5, 0.0, 1.9), 30, (-5.8, 4.7, 1.45)), N, fill=0.0, key=1.0, rim=1.0, note="a big dark shape against the violet glass")
STR("L38", (-3.4, -2.0), 180, "sneaker", lean=40, head=[0, 4])
S("L38", X((-4.9, 4.6, 1.5), (-3.5, -1.2, 2.1), 26, (-4.4, 3.6, 1.6)), N, fill=0.0, key=1.0, rim=1.0, note="bent down to the glass, from the side")
STR("L39", (-3.5, -2.15), 180, "sneaker", lean=46, head=[0, -38])
S("L39", X((-3.5, 1.7, 1.85), (-3.5, 0.0, 2.0), 36, (-3.5, 1.3, 1.9)), N, fill=0.0, key=1.0, rim=1.0, note="its face through the glass, lamp-lit, no mouth, two green points")
S("L39.2", X((-3.5, 1.0, 1.9), (-3.5, -0.4, 2.0), 50, (-3.5, 0.7, 1.95)), N, fill=0.0, key=1.0, rim=1.0, hand=0.003, note="closer on the eyes")
STR("L40", (-3.5, -2.15), 180, "sneaker", lean=46, head=[0, -26])
S("L40", X((-3.2, 1.5, 1.8), (-3.5, -0.2, 2.0), 40, (-3.2, 1.3, 1.8)), N, fill=0.0, key=1.0, rim=1.0, note="its head tilts down")
S("L40.2", X((-3.6, 2.1, 1.1), (-4.6, 3.9, 0.55), 30, (-3.8, 2.3, 1.0)), N, fill=0.0, key=1.0, rim=1.0, note="the sneakers by my bed, in its eyeline")
STR("L41", (-3.5, -2.15), 180, "sneaker", lean=46, head=[0, -40])
S("L41", X((-3.5, 1.5, 1.85), (-3.5, 0.0, 2.0), 40, (-3.5, 1.2, 1.9)), N, fill=0.0, key=1.0, rim=1.0, note="then at me, level")
cue("L42+0.1", "blink", dur=0.85)
S("L42", X((-3.5, 1.0, 1.9), (-3.5, -0.3, 2.0), 62, (-3.5, 0.7, 1.95)), N, fill=0.0, key=1.0, rim=1.0, hand=0.002, note="and it blinked, slow")
gone("strider", "L43")
pairs("L43", sneaker=None)
S("L43", X((-2.3, 1.1, 1.8), (-5.0, 4.0, 0.8), 22, (-2.6, 1.4, 1.7)), M, fill=0.5, note="the sneakers are gone, an empty patch of floor")
cat("L44", (-4.6, 3.9, DECK), yaw=20, pose="asleep", face="asleep", tail="up")
S("L44", C((-4.6, 3.9, 0.7), 1.0, 200, 22, 28, d2=0.75), M, fill=0.5, note="Biscuit asleep right where they'd been")

# =========================================================================================== 06 Saturday L46-L49
cat("L46")
gone("strider", "L46")
put("dad", "L46", (1.9, -2.15), 180, "neutral", lean=32, arms=[50, 50])
cue("L46", "props", carrier={"pos": [1.9, -1.2, DECK + 0.02], "yaw": 0, "scale": 1.3})
cat("L46", (1.9, -1.2, DECK + 0.08), yaw=0, face="neutral", pose="lie", tail="up")
S("L46", X((1.7, -5.2, 3.0), (1.9, -1.9, 0.9), 24, (2.0, -4.6, 2.8)), A, note="Dad shuts the carrier door")
gone("dad", "L46.2")
S("L46.2", C((1.9, -1.2, 0.72), 1.0, 0, 6, 28, d2=0.75), A, fill=0.6, note="Biscuit looking out through the grille")
cat("L47")
gone("dad", "L47")
cue("L47", "props", carrier=None)
cue("L47", "car", on=True, go=True, dur=1.7)
S("L47", X((0.3, -5.5, 1.5), (-1.7, -14.0, 1.2), 30, (0.1, -5.5, 1.5)), A, note="Dad's car pulls away, the carrier on the back seat")
cue("L47.2", "car", on=False)
put("me", "L47.2", (0.3, -2.0), 0, "worried")
S("L47.2", C((0.3, -2.0, 1.5), 1.5, 160, 6, 30, d2=1.2), A, note="me on the porch, watching it go")
gone("me", "L48")
put("dad", "L48", (0.1, -2.3), 0, "neutral", lean=22, arms=[50, 50])
count("L48", 7)
count("L48+0.45", 3)
count("L48.2", 0)
cue("L48", "props", bag={"pos": [-1.3, -2.2, DECK + 0.02], "yaw": 20})
pairs("L48", dadboots=None)
cue("L48", "lid", on=False)
S("L48", X((0.1, -0.4, 1.6), (-1.2, -2.5, 1.0), 24, (-0.1, -0.6, 1.5)), A, note="Dad sweeps the pairs into a bag")
gone("dad", "L48.2")
cue("L48.2", "props", bag=None)
cue("L48.2+0.5", "lid", on=True)
S("L48.2", C((-4.4, -22.0, 0.8), 2.4, 20, 18, 28, d2=1.8), A, street=0.0, note="the trash can lid claps shut")
put("me", "L49", (1.1, -2.0), 0, "neutral", arms=[0, 80])
S("L49", C((1.1, -2.85, DECK + 1.62), 1.05, 150, 4, 30, d2=0.8), A, note="my hand rubs out the 12 and chalks 0")

# =========================================================================================== 07 Sundown L51-L57
gone("me", "L51")
put("me", "L51", (-3.5, 0.75), 15, "worried", side=[0, 60])
S("L51", X((-2.6, -1.5, 2.35), (-3.5, 0.75, 1.7), 32, (-2.8, -1.2, 2.3)), S_, fill=0.8, note="me at my window again")
gone("me", "L51.2")
S("L51.2", ST(-1.9, (0, -50, 1.4), 16), S_, note="the empty rail below, the chalk 0")
cue("L52", "bus", on=True, go=True, dur=1.6)
put("dad", "L52", (0.0, -84.0), 0, "neutral")
raw("dad", "L52.2", pos=[0.0, -82.5])
S("L52", X((-1.9, -1.2, 1.9), (1.6, -86.0, 1.5), 120), S_, hand=0.004, note="the bus pulls away, Dad under the first light")
cue("L52.2", "bus", on=False)
S("L52.2", X((-1.9, -1.2, 1.9), (0.0, -88.0, 1.4), 120), S_, hand=0.004, note="the light behind him, empty")
gone("dad", "P02")
S("P02", X((-1.9, -1.2, 1.9), (3.0, -95.0, 1.5), 135), S_, hand=0.003, note="the far end, the shelter, wind")
STR("L54", (0.0, -84.0), 180, "rubber")
S("L54", X((-1.9, -1.2, 1.9), (0.0, -84.0, 1.5), 135, None, (0.6, -84.0, 1.45), 185), S_, hand=0.003, note="under the last light, someone, small")
STR("L55", (0.0, -54.0), 180, "rubber")
put("dad", "L55", (0.2, -24.5), 180, "neutral")
S("L55", X((-1.9, -1.2, 1.9), (0.0, -54.0, 1.4), 110), S_, hand=0.004, note="one light closer")
STR("L55.2", (0.0, -34.0), 180, "rubber")
S("L55.2", X((-1.9, -1.2, 1.9), (0.1, -30.0, 1.4), 70, None, (0.1, -30.0, 1.4), 80), S_, hand=0.004, note="right behind Dad")
gone("dad", "L56")
STR("L56", (0.3, -34.0), 180, "rubber")
S("L56", X((1.9, -37.0, 0.32), (0.3, -34.0, 0.45), 32, (1.7, -36.5, 0.3)), S_, hand=0.004, note="muddy green rubber boots with hay")
gone("strider", "L56.2")
put("me", "L56.2", (-3.5, 0.75), 15, "worried", side=[0, 60])
S("L56.2", X((-2.6, -1.5, 2.35), (-3.5, 0.75, 1.7), 32, (-2.8, -1.2, 2.3)), S_, fill=0.8, note="me, working it out")
put("me", "L57", (-3.5, 0.75), 15, "smirk", side=[0, 60], head=[0, 0])
S("L57", X((-2.6, -1.5, 2.35), (-3.5, 0.75, 1.7), 34, (-2.9, -1.2, 2.3)), S_, fill=0.8, note="boots like that only come from the farm")

# =========================================================================================== 08 The gate L58-L66
gone("me", "L58")
put("dad", "L58", (0.0, -9.5), 180, "neutral", arms=[0, 28])
S("L58", C((0.0, -9.4, 1.4), 1.7, 170, 6, 30, d2=1.4), S_, fill=0.8, note="Dad reaches the gate, a hand on the latch")
put("dad", "L59", (0.0, -8.2), 0, "scared")
S("L59", C((0.0, -8.2, 1.5), 2.3, 20, 6, 30, d2=1.9), S_, fill=0.7, note="Dad turns round, scared")
STR("L59.1", GATE_R, 180, "rubber")
S("L59.1", X((0.6, -6.9, 1.75), (GATE_R[0], GATE_R[1], 1.5), 40, (0.5, -7.0, 1.75)), S_, fill=0.5, hand=0.004, note="over his shoulder, the Strider at the gatepost")
STR("L60", GATE_R, 180, "rubber", head=[0, 24], lean=4)
S("L60", C((GATE_R[0], GATE_R[1], 1.9), 3.4, 150, 4, 34, d2=3.0), S_, fill=0.5, hand=0.004, note="it stopped, its head bowed to Dad")
STR("L61", GATE_R, 180, "rubber", sq=0.5, head=[0, 20])
S("L61", C((GATE_R[0], GATE_R[1], 0.8), 2.6, 150, 8, 34), S_, fill=0.6, note="smaller: crouched, the coat pooled")
gone("strider", "L61+0.38")
pairs("L61+0.38", rubber=pr((GATE_R[0], GATE_R[1], 0.38), 175, True, 2.3))
S("L61+0.38", C((GATE_R[0], GATE_R[1], 0.7), 2.6, 150, 8, 34), S_, fill=0.6, note="nothing there but the boots, steaming")
cat("L62", (1.80, -10.04, 0.4), yaw=-90, pose="stand", face="neutral", pitch=-22, tail="up", mud=True,
    to=[1.80, -10.04, 0.95], dur=1.3)
S("L62", C((1.38, -10.07, 1.2), 0.95, -90, 3, 30, d2=0.8), S_, fill=1.0, note="low side close, Biscuit's muddy head and ears come out of the left boot, facing us")
cat("L63", (GATE_R[0] - 0.9, GATE_R[1] + 0.1, 0.4), yaw=12, face="neutral", tail="up", mud=True)
S("L63", C((GATE_R[0] - 0.9, GATE_R[1] + 0.1, 0.62), 1.0, 10, 8, 30, d2=0.75), S_, fill=0.9, note="muddy to the ears")
put("dad", "L65", (0.0, -8.2), 0, "soft", head=[0, 20])
S("L65", C((0.0, -8.2, 1.4), 1.9, 25, 5, 30, d2=1.6), S_, fill=0.8, note="Dad looking down, soft")
gone("dad", "L66")
cat("L66")
count("L66", 12)
cue("L66", "meter", n=0)
pairs("L66", rubber=None)
S("L66", X((6.5, -2.0, 1.75), (-3.5, -3.0, 1.45), 26, (6.3, -2.2, 1.7), (-3.5, -3.0, 1.45)), M, note="the row of pairs as it was")
count("L66.2", 0)
cue("L66.2", "meter", n=-1)
pairs("L66.2", rubber=pr((GATE_R[0], GATE_R[1], 0.38), 175, True, 2.3))
S("L66.2", C((GATE_R[0], GATE_R[1], 0.6), 2.3, 150, 8, 34), S_, note="the boots on the path, still steaming")
cat("L66a", (GATE_R[0] - 0.22, GATE_R[1], 0.62), yaw=170, pose="stand", face="neutral", pitch=-10, tail="up", mud=True)
S("L66a", C((GATE_R[0] - 0.22, GATE_R[1], 0.7), 1.5, 160, 10, 30, d2=1.2), S_, fill=0.9, note="he needs a pair to stand up in")
pairs("L66b", rubber=None)
cat("L66b", (-4.4, -22.0, 0.5), yaw=90, pose="stand", face="neutral", pitch=-60, tail="up", mud=True)
S("L66b", C((-4.4, -22.0, 0.9), 2.2, 40, 14, 30, d2=1.7), S_, note="a ginger tail goes into a neighbor's trash can")
cat("L66b.2")
count("L66b.2", 12)
cue("L66b.2", "meter", n=0)
S("L66b.2", X((6.5, -2.0, 1.75), (-3.5, -3.0, 1.45), 24, (6.2, -2.3, 1.7), (-3.5, -3.0, 1.45)), S_, note="the rail of mixed old pairs, every one the same size")
count("L66c", 0)
cue("L66c", "meter", n=-1)
pairs("L66c", sneaker=pr(MATP, 160, True))
S("L66c", FRAME1, S_, dof=[0.85, 2.4], fill=0.6, note="my sneakers on the mat")
pairs("L66c.2", sneaker=None)
S("L66c.2", X((0.3, -27.0, 0.38), (0.0, -37.0, 0.55), 26, (0.3, -27.4, 0.38)), S_, hand=0.003, note="the empty asphalt one light behind me")
cat("L66e")
count("L66e", 0)
pairs("L66e", sneaker=pr((-4.6, 3.9, 0.47), 170, False))
S("L66e", X((-2.6, 2.2, 1.5), (-4.6, 3.9, 0.9), 26, (-3.0, 2.4, 1.4)), S_, fill=0.8, note="a pair kept inside, the window dark above")
pairs("L66e.3", sneaker=None)
put("me", "L66e.3", (0.0, -45.0), 180, "neutral", hidden=False)
raw("me", "L66f", pos=[0.0, -41.0])
S("L66e.3", X((-1.9, -1.2, 1.9), (0.0, -46.0, 1.3), 40), S_, note="somebody walks home alone")
gone("me", "L66f")
S("L66f", X((-3.5, 1.2, 1.75), (-3.5, 0.0, 1.55), 30, (-3.5, 0.9, 1.7)), S_, fill=0.8, note="the window glass, empty now, two faint marks on the sill")

# =========================================================================================== 09 Home L68-L71
put("dad", "L68", (0.0, -8.5), 0, "soft", arms=[55, 55])
cat("L68", (0.0, -8.82, 1.12), yaw=0, pose="lie", face="neutral", tail="down", mud=True)
S("L68", C((0.0, -8.6, 1.2), 1.6, 20, 6, 30, d2=1.3), S_, fill=0.9, note="Dad picks Biscuit up, mud and all")
cat("L69")
put("dad", "L69", (0.95, 0.7), 90, "neutral", lean=14, arms=[50, 50])
S("L69", X((1.4, 3.6, 1.3), (1.4, 0.7, 0.85), 15, raw=True), D, fill=1.3, key=0.6, note="dawn, Dad pouring food into the bowl")
put("me", "L69.2", (-0.4, 2.8), 180, "smirk")
put("dad", "L69.2", (1.0, 0.9), 160, "polite")
S("L69.2", X((0.6, 3.3, 1.5), (1.35, 0.8, 1.0), 15, (0.9, 3.1, 1.5), raw=True), D, fill=1.6, note="I caught Dad, sheepish")
gone("me", "L70")
put("dad", "L70", (1.5, 0.9), 180, "polite", arms=[0, 105])
cat("L70", (1.8, 0.68, DECK), yaw=60, pose="stand", face="neutral", pitch=12, tail="up", mud=True)
S("L70", C((1.6, 0.8, 1.4), 1.9, 160, 4, 30, d2=1.5), D, fill=0.8, note="a finger to his lips, Biscuit eating")
cat("L71")
gone("dad", "L71")
put("dad", "L71", (0.9, -8.4), 0, "neutral", arms=[0, 70])
pairs("L71", dadboots=pr((1.2, -9.0, 1.58), 0, False, 0.8), oldsneak=pr((1.2 + 0.3, -9.0, 1.58), 0, False, 0.8))
S("L71", C((1.3, -8.9, 1.5), 1.9, 20, 8, 30, d2=1.5), S_, fill=0.8, note="Dad sets his boots and my sneakers on the gatepost")
gone("dad", "L71.2")
S("L71.2", C((1.3, -9.0, 1.65), 1.0, 160, 10, 30, d2=0.75), S_, fill=0.7, dof=[0.9, 2.4], note="my sneakers and his boots, side by side")
cat("L71.3", (-1.2, -9.0, 1.6), yaw=20, pose="lie", face="neutral", tail="up", mud=True)
S("L71.3", C((-1.2, -9.0, 1.7), 1.7, 30, 8, 28, d2=1.35), S_, fill=0.8, note="Biscuit on the other gatepost")

# =========================================================================================== 10 The loop L72-L76
cat("L72")
pairs("L72", dadboots=None, oldsneak=None)
put("me", "L72", (0.0, -90.0), 180, "neutral")
raw("me", "L72.3", pos=[0.0, -84.0])
S("L72", X((-1.8, -70.0, 1.6), (0.0, -88.0, 1.4), 60, (-1.8, -70.0, 1.6), (0.0, -86.0, 1.4)), S_, hand=0.006, note="me walking up the road from the shelter")
raw("me", "L72.3", pos=[0.0, -60.0])
S("L72.3", X((1.8, -66.0, 1.2), (0.0, -58.0, 1.4), 38, (1.6, -60.0, 1.2)), S_, hand=0.008, note="and walked the long road")
put("me", "L73", (0.0, -40.0), 180, "neutral")
STR("L73", (0.0, -50.0), 180, "sneaker")
S("L73", X((0.6, -44.0, 0.45), (0.0, -50.0, 0.8), 26, (0.5, -44.4, 0.45)), S_, hand=0.004, note="my old sneakers one light behind me, the coat hem above")
S("L73.2", X((0.75, -38.2, 1.6), (0.0, -40.0, 1.55), 36, (0.6, -38.7, 1.58)), S_, fill=0.9, note="my face, eyes front")
put("me", "L74", (0.0, -40.0), 180, "neutral")
S("L74", X((1.3, -37.6, 1.5), (-0.1, -47.5, 1.6), 34, (1.2, -37.9, 1.5)), S_, fill=0.9, hand=0.004, note="over my shoulder, soft, two green points")
gone("strider", "L75")
put("me", "L75", (0.0, -40.0), 180, "smirk")
S("L75", C((0.0, -40.0, 1.55), 1.4, 170, 3, 38, d2=1.15), S_, fill=0.9, note="I didn't look back, a small smile")
gone("me", "L76")
count("L76", 8)
cat("L76", (0.1, -0.95, DECK + 0.07), yaw=-90, to=[-1.1, -0.95, DECK + 0.07], dur=0.9, tail="up")
pairs("L76", oldsneak=pr(MATP, 160, True))
S("L76", FRAME1, M, dof=[0.85, 2.4], fill=0.6, note="my old sneakers on the mat: frame 1 again")

# ---------------------------------------------------------------------------------------------------- story
look = {"fog": "#ffd7b8", "fog_density": 0.004, "fog_start": 30.0, "sky": "#ff9d4d", "exposure": 0.0,
        "flash_safe": True, "style": "closer", "polish": {"emph": ["L01", "L05", "L37", "L39", "L66", "L76"], "reveal": ["L66", "L39"], "quiet": [["L68", "L70"]], "sway": ["S59", "S60", "S61"], "camera": True, "idle": True, "ease": True, "ones": "walk"}}
story = {
    "slug": "warm-shoes",
    "title": "Our Cat Brings Home WARM Shoes \U0001F408",
    "made_for_kids": False,
    "premise": "Every night our ginger cat Biscuit carries a pair of old shoes in through the cat flap, always size eleven, "
               "always still warm, and nobody in town ever comes for them. Dad lines them up on the porch rail and says "
               "the cat goes on Saturday, and all week someone far too tall has walked one streetlight behind him on "
               "his way home from the bus.",
    "twist": "The tall stranger behind Dad is Biscuit himself, standing up in old shoes to walk Dad home, and at our gate "
             "he gets small again and climbs out of the boots. The shoes were never stolen, and a pair kept inside means "
             "somebody walks home alone.",
    "world": "a mint-green house with a white porch rail full of old shoes, a chalk count on a slate post, a picket gate, "
             "one long road of eight streetlights to a bus shelter, and a field of gold grass at sundown",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffb238",
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
    "music": {"root": 43, "mode": "mixolydian", "bpm": 104, "seed": 61,
              "sections": [
                  {"at": 0, "voices": ["bubble", "pulse", "pluck_hi"], "energy": 0.55},
                  {"at": "L16", "voices": ["pad", "bubble"], "energy": 0.4},
                  {"at": "L21", "voices": ["pad", "pulse", "pluck"], "energy": 0.5},
                  {"at": "L36", "voices": ["pad", "drone"], "energy": 0.35, "mode": "minor"},
                  {"at": "L37", "voices": ["drone", "pad"], "energy": 0.55, "mode": "minor"},
                  {"at": "L43", "voices": ["drone", "pad", "pluck"], "energy": 0.4, "mode": "mixolydian"},
                  {"at": "L68", "voices": ["drone", "pad", "pluck_hi"], "energy": 0.5, "mode": "major"},
                  {"at": "L72", "voices": ["drone", "pad"], "energy": 0.3, "mode": "minor"},
              ]},
    "sound": {
        "rev": 1, "floor": "wood", "steps_db": -22,
        "ambience": [{"kind": "crickets", "from": "L15", "to": "L43", "lufs": -40},
                     {"kind": "crickets", "from": "L51", "to": "end", "lufs": -40},
                     {"kind": "wind", "from": "L36", "to": "L43", "lufs": -42}],
        "sfx": [
            {"at": "L01>-0.32", "kind": "thud", "db": -16},
            {"at": "L01>-0.34", "kind": "puff", "db": -20},
            {"at": "L05.2", "kind": "click", "db": -22},
            {"at": "L05.2+0.45", "kind": "click", "db": -22},
            {"at": "L06", "kind": "latch", "db": -16},
            {"at": "L27", "kind": "latch", "db": -16},
            {"at": "L28.1", "kind": "latch", "db": -20},
            {"at": "P01+0.55", "kind": "knock", "db": -18, "pattern": [0], "tone": "glass_soft"},
            {"at": "P02+0.45", "kind": "thud", "db": -26},
            {"at": "L47", "kind": "door", "db": -16},
            {"at": "L48.2+0.5", "kind": "thud", "db": -16},
            {"at": "L62", "kind": "puff", "db": -22},
        ],
        "music_drops": [{"from": "L36>", "to": "P01>"}, {"from": "P02-0.1", "to": "P02>"}],
    },
}
from blocky import timeline

voice = json.loads((HERE.parent / "voice-timings.json").read_text())
_tl0 = timeline.build({"name": "warm-shoes", "lines": lines, "shots": [{"id": "S0"}], "gap": 0.12, "tail": LOOP,
    "min_read": 0.15,
    
                       "cast": cast}, voice)
AT = timeline.resolver(_tl0["lines"], _tl0["duration"])
for k in acting:
    acting[k].sort(key=lambda e: AT(e["at"]))
cues.sort(key=lambda e: AT(e["at"]))
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots, {len(cues)} cues")
