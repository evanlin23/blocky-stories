"""Writes ../story.json for "Our Town Photo Is Missing ONE Face" (ep140-town-photo, batch 15, eerie lane).

Run from anywhere: python stories/ep140-town-photo/generator/make_story.py
The words are in lines.json (captions in 2 to 3 word chunks; L01.3 means chunk 3, 0-based). Everything else is here.

World (metres, z up, characters at yaw 0 face -y, toward the shot cameras): the bleachers' front row at y = 3.0, five rows
0.9 m deep and 0.45 m up, seats 0.8 m apart (x = 0.8 k, +0.4 on odd rows); me row 2 k 0, Mom row 2 k -1, Grandma row 0
k -1, Mr. Okafor's seat row 0 k 0. The box camera stands at (0.1, -5.0), the photographer behind it at y = -6.1 facing +y
(yaw 180). The headcount board is at (-4.6, 1.0). The hallway is at x = 70, the kite stall at x = -60.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

HALLX, BEACHX = 70.0, -60.0
BOARDX, BOARDY = -4.6, 1.0

# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True, "ink": "#24131f"}
LASH = {"eyes": "lashes", "brows": True, "ink": "#24131f"}
cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#f2b53a", "pattern": "solid", "pants": "#3a4a6a",
           "shoes": "#5a3b22", "sleeves": "long", "hair": "swoop", "hair_c": "#6b4226", "extras": ["coat"], "zip_c": "#8a6414",
           "body_width": 0.6, "face": {**FACE, "freckles": True}},
    "mom": {"age": "adult", "skin": "#f1c9a0", "shirt": "#2bb3a3", "pattern": "solid", "pants": "#4a4258",
            "shoes": "#6a4a2a", "sleeves": "long", "hair": "bun", "hair_c": "#2a1c14", "height": 0.95, "body_width": 0.6,
            "face": dict(LASH)},
    "okafor": {"age": "adult", "skin": "#e9c3a0", "shirt": "#3c3f46", "pattern": "solid", "collar": "#f4f4f0",
               "pants": "#2f3238", "shoes": "#1c1a1c", "sleeves": "long", "hair": "none", "height": 0.97, "body_width": 0.6, "face": {**FACE, "bags": True}},
    "grandma": {"age": "adult", "skin": "#f6d5b5", "shirt": "#b9a0e0", "pattern": "solid", "pants": "#7a6a98",
                "shoes": "#5a4a6a", "sleeves": "long", "hair": "bun", "hair_c": "#f2f2f2", "height": 0.9,
                "body_width": 0.6, "face": {**LASH, "bags": True}},
    "benny": {"age": "adult", "skin": "#d9a678", "shirt": "#ff6f61", "pattern": "stripes", "pattern_c": "#ffd23f",
              "pants": "#f2e2b8", "shoes": "#6a4a2a", "sleeves": "short", "hair": "spiky", "hair_c": "#3a2616",
              "height": 1.02, "face": dict(FACE)},
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


def gone(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def talk(who, frm, to, amt=0.6):
    acting[who].append({"from": frm, "to": to, "mouth": [amt, amt], "flap": True})


for k in acting:
    acting[k].append({"at": 0, "pos": [0, 30, 0], "hidden": True, "blend": 0, **NEUTRAL})


# ---------------------------------------------------------------------------------------------------- places
def seat(r, k, h=1.0):
    x = 0.8 * k + (0.4 if r % 2 else 0.0)
    return [round(x, 3), 3.0 + 0.9 * r, round(0.45 * (r + 1) + 0.06 - 0.68 * h, 3)]


ME_S = seat(2, 0)
MOM_S = seat(2, -1, 0.95)
GM_S = seat(0, -1, 0.9)
OK_S = seat(0, 0, 0.97)
OK_C = [-0.5, -5.5, 0.0]
ME_C = [-0.5, -5.5, 0.0]
LOOK_Z = {"me": 1.57, "mom": 1.49, "okafor": 1.52, "grandma": 1.41}


# ---------------------------------------------------------------------------------------------------- cameras
def pos_of(tg, d, az, el):
    a, e = math.radians(az), math.radians(el)
    return [round(tg[0] + d * math.sin(a) * math.cos(e), 3), round(tg[1] - d * math.cos(a) * math.cos(e), 3),
            round(tg[2] + d * math.sin(e), 3)]


def C(tgt, w, az=0, el=3, lens=45, w2=None, tgt2=None, az2=None):
    """A camera aimed at tgt, standing so the frame shows w metres across at the target (lens 45: 2 m at 6.7 m).
    With w2 / tgt2 / az2 it moves there over the shot."""
    k0 = [0, pos_of(tgt, w * lens / 13.5, az, el), list(tgt), lens]
    if w2 is None and tgt2 is None and az2 is None:
        return [k0]
    t2 = tgt2 or tgt
    return [k0, [1, pos_of(t2, (w2 or w) * lens / 13.5, az if az2 is None else az2, el), list(t2), lens]]


def X(loc, tgt, lens, loc2=None, tgt2=None, lens2=None):
    ks = [[0, list(loc), list(tgt), lens]]
    if loc2 or tgt2 or lens2:
        ks.append([1, list(loc2 or loc), list(tgt2 or tgt), lens2 or lens])
    return ks


def S(at, sid, cam, hand=0.004, dof=None, fill=1.0, step=2, note="", **kw):
    d = {"id": sid, "cam": cam, "step": step, "hand": hand}
    if shots:
        d["at"] = at
    if dof:
        d["dof"] = dof
    if fill != 1.0:
        d["fill"] = fill
    d.update(kw)
    if note:
        d["note"] = note
    shots.append(d)
    return d


def sit(who, at, spot, expr="neutral", rise=0.28, **kw):
    """Cut in standing a little high, then sink onto the seat over 0.5 s (the legs hang inside the tier)."""
    put(who, at, [spot[0], spot[1], spot[2] + rise], 0, expr, **kw)
    raw(who, f"{at}+0.5" if isinstance(at, str) else at + 0.5, pos=list(spot), blend=0.5)


# ================================================================================================ the cast on the stands, from frame 1
put("me", 0, ME_S, 0, "worried")
put("mom", 0, MOM_S, 0, "worried")
put("grandma", 0, GM_S, 0, "neutral")
gone("grandma", "L02")      # cheated out of the stands for the close shots on Mom and me (she sits in front of Mom)
# Mom holds the proof print from L02 to L08
HOLD = [[0, 0], [0, 0]]

cue(0, "board", g="a")
cue(0, "tag", g="a")
cue(0, "cheer", on=False)

# ================================================================================================ L01 to L03 the count, the rule
S(0, "S01a", C((BOARDX, 1.0, 1.15), 1.3, az=0, el=1, lens=40, w2=1.15, tgt2=(BOARDX, 1.0, 1.1)),
  note="S01a frame 1: the headcount board close, 212 on top, the 212/211 tile in the corner")
S("L01.3", "S01b", C((BOARDX, 1.0, 1.15), 1.4, az=0, el=1, lens=40, w2=1.2, tgt2=(BOARDX, 1.0, 1.05)),
  note="S01b tilt down to 211, push on ELEVEN")
# S02: Mom holds the proof up in front of her; me beside, soft behind it
raw("mom", "L02", arms=[62, 62], side=[-22, -22], blend=0.3, expr="worried")
cue("L02", "pr_proof", on=True, pos=[-0.62, 4.1, 1.6], rot=[0, 0], s=1.55)
S("L02", "S02a", C((-0.42, 4.5, 1.6), 1.45, az=0, el=8, lens=70, w2=1.35), clear=True, note="S02a the proof in Mom's hands, the green-ringed gap; my face soft behind")
S("L02.2", "S02b", C((-0.7, 4.4, 1.7), 1.3, az=0, el=8, lens=70, w2=1.15), clear=True, note="S02b punch in on the gap on HERE")
S("L03", "S03", C((-0.12, 4.8, 2.22), 1.2, az=0, el=18, lens=70, w2=1.05), clear=True, note="S03 my face, scared, the print's edge low left")
raw("me", "L03", expr="scared", blend=0.2)
raw("me", "L03+1.6", expr="worried", blend=0.2)

# ================================================================================================ L04, L05 the example
cue("L04", "pr_last", on=True, pos=[BOARDX + 0.62, 0.82, 1.4], rot=[0, -7], s=2.0)
S("L04", "S04", C((BOARDX + 0.7, 0.9, 1.4), 1.3, az=-3, el=3, w2=1.15), note="S04 last year's print on the board's ledge, a gap in row two, ringed")
put("benny", "L05", [BEACHX, 0.2, 0.0], 0, "laugh", arms=[40, 40])
cue("L05", "pr_last", on=False)
S("L05", "S05", C((BEACHX, 0.0, 1.35), 1.9, az=0, el=3, w2=1.75), note="S05 Uncle Benny at his kite stall, laughing, a big plain diamond kite at chest height")

# ================================================================================================ L08, L09 Mom counts, holds on
gone("benny", "L08")
raw("mom", "L08", arms=[62, 62], side=[-22, -22], expr="worried", blend=0.0)
raw("mom", "L08+0.8", arms=[62, 62], side=[-22, -22], head=[0, 14], blend=0.4)
raw("mom", "L08+1.6", arms=[62, 62], side=[-22, -22], head=[0, 0], blend=0.4)
raw("me", "L08", expr="worried", blend=0.2)
S("L08", "S08", C((-0.5, 4.6, 1.7), 1.6, az=0, el=6, lens=60, w2=1.45), clear=True, note="S08 two-shot: Mom (worried) counts the proof, me beside her (uneasy)")
cue("L09", "pr_proof", on=False)
raw("mom", "L09", arms=[0, 72], side=[0, 16], head=[0, 0], blend=0.4, expr="worried")
raw("me", "L09", arms=[72, 0], side=[16, 0], blend=0.4, expr="worried")
S("L09", "S09a", C((-0.4, 4.6, 1.9), 1.6, az=0, el=14, lens=70, w2=1.4), clear=True, note="S09a Mom's hand closing round mine on the bench, her face above")
S("L09.2", "S09b", C((-0.42, 4.7, 2.0), 1.7, az=0, el=14, lens=70, w2=1.55), clear=True, note="S09b Mom's face, worried")

# ================================================================================================ L10 to L13 Saturday, pickles
cue("L10", "board", g="a900")
S("L10", "S10", C((BOARDX + 0.1, 1.0, 1.05), 1.75, az=0, el=2, w2=1.6), note="S10 the board with a chalk clock at 9:00")
put("okafor", "L11", OK_C, 180, "neutral")
cue("L11", "board", g="a")
S("L11", "S11", C((-0.5, -5.5, 1.5), 1.45, az=-150, el=3, w2=1.3), back=True, note="S11 Mr. Okafor at the box camera, very straight")
raw("okafor", "L12.2", expr="laugh", arms=[0, 170], blend=0.35)
talk("okafor", "L12.2", "L12>", 0.8)
raw("okafor", "L12", head=[-10, 0], blend=0.3)
S("L12", "S12", C((-0.5, -5.5, 1.55), 1.15, az=-165, el=3, w2=1.0), back=True, note="S12 cap raised, mouth wide on PICKLES")
gone("okafor", "L13")
put("grandma", "L13", GM_S, 0, "laugh", arms=[165, 165])
gone("grandma", "L13.2")
cue("L13", "cheer", on=True)
raw("me", "L13", expr="laugh", arms=[165, 165], side=[0, 28], blend=0.4)
raw("mom", "L13", expr="laugh", arms=[165, 165], side=[0, 0], blend=0.4)
S("L13", "S13a", X((2.3, -9.5, 1.3), (-0.5, 5.0, 2.6), 70, (2.1, -9.0, 1.3), (-0.5, 5.0, 2.6), 70),
  note="S13a wide of the bleachers from the camera: everyone laughing, arms up")
S("L13.2", "S13b", C((-0.4, 4.8, 2.25), 1.8, az=0, el=18, lens=70, w2=1.55), clear=True, note="S13b punch in on Mom and me laughing")

# ================================================================================================ L16, L17 the test shot
cue("L16", "cheer", on=False)
sit("me", "L16", ME_S, "worried", rise=0.32, arms=[60, 0], side=[18, 0])
raw("mom", "L16", expr="worried", arms=[0, 60], side=[0, 18], blend=0.3)
S("L16", "S16", C((-0.4, 4.6, 1.95), 1.7, az=0, el=8, lens=70, w2=1.5), clear=True, note="S16 I sit beside Mom, our hands joined between us")
cue("L17", "pr_test", on=True, pos=[-0.62, 4.22, 1.9], rot=[0, 0], s=1.35)
raw("mom", "L17", arms=[62, 62], side=[-22, -22], expr="worried", blend=0.35)
S("L17", "S17a", C((-0.62, 4.5, 2.0), 1.5, az=0, el=18, lens=70, w2=1.35), clear=True, note="S17a the new print: Mom's hand holds nothing; Mom's face above it")
raw("mom", "L17.2", expr="wide", blend=0.2)
cue("L17.2", "pr_test", on=False)
S("L17.2", "S17b", C((-0.8, 4.8, 2.2), 1.05, az=0, el=18, lens=70, w2=0.95), clear=True, note="S17b Mom's face, stunned")

# ================================================================================================ L18 to L20 the hallway
gone("me", "L18")
gone("mom", "L18")
put("me", "L18", [HALLX - 2.8, 0.9, 0.0], 90, "neutral")
raw("me", "L18+2.4", pos=[HALLX + 0.7, 0.9, 0.0], blend=0.3)
S("L18", "S18", X((HALLX + 4.8, -2.0, 1.35), (HALLX - 1.2, 0.9, 1.95), 28, (HALLX + 4.4, -2.0, 1.35), (HALLX + 0.2, 0.9, 1.95), 28),
  note="S18 the hallway of framed photos; I walk past, side tracking")
S("L19", "S19a", X((HALLX + 0.6, -2.5, 1.6), (HALLX + 0.6, 2.9, 1.75), 16, (HALLX + 0.6, -2.3, 1.6), (HALLX + 0.6, 2.9, 1.75), 16),
  note="S19a three framed photos side by side, nobody at a camera")
gone("me", "L19")
put("me", "L19.2", [HALLX + 0.8, 0.9, 0.0], 0, "worried")
S("L19.2", "S19b", C((HALLX + 0.8, 0.9, 1.52), 1.4, az=0, el=2, lens=28, w2=1.25), note="S19b my face, uneasy")
put("me", "L20", [HALLX + 0.25, 1.55, 0.0], 0, "smile")
S("L20", "S20", C((HALLX + 0.1, 2.2, 1.65), 1.7, az=-6, el=2, lens=24, w2=1.4), note="S20 one old photo, grass at the bottom edge and nobody; I smile beside it")

# ================================================================================================ L21 to L23 8:59, his hands
gone("me", "L21")
cue("L21", "board", g="a859")
S("L21", "S21", C((-3.9, 2.0, 1.5), 3.6, az=-8, el=2, lens=36, w2=3.3), note="S21 the board's clock at 8:59; the full bleachers behind")
OK_H = [-0.5, -5.5, 0.0]
put("okafor", "L22", OK_H, 180, "worried", arms=[58, 58], side=[-26, -26])
cue("L22", "bulb", on=True, pos=[-0.5, -4.95, 1.2], shake=0.012, big=2.2)
for i, dt in enumerate((0.3, 0.55, 0.8, 1.05, 1.3, 1.55, 1.8)):
    raw("okafor", f"L22+{dt}", arms=[58 + (3 if i % 2 else -3), 58 - (3 if i % 2 else -3)], side=[-26, -26], blend=0.2, tremble=1.2)
S("L22", "S22a", C((-0.5, -4.95, 1.3), 1.25, az=-140, el=4, w2=1.1), back=True, note="S22a his hands on the shutter bulb, shaking")
raw("okafor", "L22.2", head=[0, 0], blend=0.2)
S("L22.2", "S22b", C((-0.5, -5.5, 1.5), 1.1, az=-160, el=3, w2=1.0), back=True, note="S22b his face, worried")
raw("okafor", "L23", head=[-34, 0], expr="neutral", arms=[58, 58], side=[-26, -26], blend=0.5)
S("L23", "S23a", C((-0.5, -5.3, 1.35), 1.15, az=-165, el=3, w2=1.05), fill=1.6, back=True, note="S23a Mr. Okafor turns to look straight at me")
cue("L23.2", "bulb", on=True, pos=[-0.5, -4.95, 1.3], to=[-0.9, -4.3, 1.2], dur=0.6, big=2.4)
raw("okafor", "L23.2", arms=[75, 95], side=[-26, -50], blend=0.4)
S("L23.2", "S23b", C((-0.65, -4.9, 1.35), 1.1, az=-165, el=3, w2=1.0), fill=1.6, back=True, note="S23b his hand holds the shutter bulb out to the camera")

# ================================================================================================ L24 to L26 the swap, the count
cue("L24", "bulb", on=False)
gone("me", "L24")
gone("okafor", "L24")
sit("okafor", "L24", OK_S, "smile", rise=0.4)
put("grandma", "L24", GM_S, 0, "smile")
put("mom", "L24", MOM_S, 0, "smile")
cue("L24", "cheer", on=False)
S("L24", "S24", C((-0.4, 3.0, 1.5), 1.75, az=0, el=2, w2=1.55), note="S24 Mr. Okafor sits in the front row beside Grandma, smiling")
put("me", "L25", ME_C, 180, "neutral", arms=[0, 0], head=[0, 0])
S("L25", "S25", C((-0.3, -5.4, 1.5), 1.5, az=-150, el=3, w2=1.35), back=True, note="S25 me behind the camera, my eye at the viewfinder")
cue("L26", "vf", on=True)
S("L26", "S26a", X((0.1, -3.9, 1.6), (-0.3, 4.6, 1.5), 40, (0.1, -3.6, 1.6), (-0.3, 4.6, 1.5), 40), fill=0.2,
  note="S26a through the viewfinder: a thin frame line over the bleachers, every face filled")
cue("L26.2", "vf", on=False)
raw("mom", "L26.2", expr="smile", arms=[0, 0], side=[0, 0], blend=0.4)
raw("grandma", "L26.2", expr="smile", blend=0.4)
S("L26.2", "S26b", C((-0.7, 4.8, 1.85), 1.35, az=0, el=12, lens=70, w2=1.2), clear=True, note="S26b Mom smiling, the empty seat beside her")
cue("L26.2+0.45", "board", g="smudge")
cue("L26.2+0.66", "board", g="b859")
cue("L26.2+0.66", "tag", g="b")
S("L26.2+0.45", "S26c", C((BOARDX + 0.1, 1.0, 1.05), 1.75, az=0, el=2, w2=1.6), note="S26c the 211 is wiped and 212 written")

# ================================================================================================ L28, L29 pickles, click
raw("me", "L28", expr="wide", blend=0.2, head=[0, 4])
talk("me", "L28.2", "L28>", 0.8)
raw("me", "L28.2", expr="laugh", blend=0.2)
S("L28", "S28a", C((-0.5, -5.5, 1.55), 1.0, az=-150, el=3, w2=0.9), back=True, note="S28a my face at the camera, stunned, then PICKLES")
cue("L28.2", "cheer", on=True)
S("L28.2", "S28b", X((0.1, -12.5, 3.2), (0.0, 4.8, 2.3), 26, (0.1, -11.8, 3.2), (0.0, 4.8, 2.3), 26), note="S28b the bleachers, everyone laughing, arms up")
raw("me", "L29", expr="smile", arms=[60, 60], side=[-24, -24], head=[0, 0], blend=0.3)
cue("L29", "bulb", on=True, pos=[-0.5, -4.9, 1.1], squeeze=0.3, big=2.6)
S("L29", "S29", C((-0.5, -4.95, 1.3), 0.95, az=-140, el=4, w2=0.85), back=True, note="S29 my hand squeezes the shutter bulb: Click.")

# ================================================================================================ the drop, L31 to L35
cue("P1", "bulb", on=False)
cue("P1", "pr_final", on=True, pos=[-0.24, -5.1, 1.45], to=[-0.5, -4.85, 1.5], dur=0.55, rot=[180, 0], s=1.5)
S("P1", "S30", C((-0.4, -4.95, 1.2), 1.0, az=-150, el=4, w2=0.9), back=True, note="the drop: the print slides out of the camera's slot into my hands")
cue("L31", "pr_final", on=True, pos=[-0.5, -4.85, 1.5], rot=[180, 0], s=1.5)
cue("L31", "cheer", on=False)
S("L31", "S31a", C((-0.5, -4.85, 1.2), 1.0, az=-150, el=4, w2=0.9), back=True, note="S31a the print: Mr. Okafor in the front row, smiling")
S("L32", "S31o", C((0.0, 3.0, 1.18), 0.9, az=0, el=2, w2=0.8), note="S31o Mr. Okafor himself in the front row, smiling (the print's face, seen for real)")
S("L32.1", "S31b", C((-0.5, -4.85, 1.31), 0.42, az=-150, el=3, w2=0.34), back=True, note="S31b punch in on his face in the print")
cue("L33", "pr_final", on=False)
S("L33", "S32", C((-1.0, 3.0, 1.45), 1.3, az=0, el=2, w2=1.15), note="S32 Grandma, stunned, then smiling")
raw("grandma", "L33", expr="wide", blend=0.3)
raw("grandma", "L33.3", expr="smile", blend=0.4)
put("okafor", "L34", [-1.1, -5.5, 0.0], 180, "smile", side=[0, 0])
raw("okafor", "L34+0.9", side=[70, 0], blend=0.5)
put("me", "L34", ME_C, 180, "smile")
S("L34", "S33", C((-0.8, -5.5, 1.45), 1.6, az=-160, el=3, w2=1.4), fill=1.6, back=True, note="S33 Mr. Okafor beside me at the camera, one step in to pat my shoulder")
raw("okafor", "L35", expr="smile", blend=0.3)
talk("okafor", "L35", "L35>", 0.5)
S("L35", "S34", C((-1.1, -5.5, 1.5), 1.1, az=-170, el=3, w2=1.0), back=True, note="S34 his face, smiling, eyes on me")

# ================================================================================================ L37 the loop
gone("okafor", "L37")
put("me", "L37", [BOARDX + 1.2, 0.0, 0.0], 0, "worried")
cue("L37", "board", g="b900")
S("L37", "S36", C((BOARDX + 0.85, 0.0, 1.5), 3.0, az=10, el=3, w2=2.7), note="S36 my face, uneasy, the 212 / 212 board behind my shoulder")

# ---------------------------------------------------------------------------------------------------- story
look = {"fog": "#d8ecff", "fog_density": 0.002, "fog_start": 30.0, "sky": "#a8d8ff", "exposure": 0.0,
        "flash_safe": True, "style": "closer",
        "polish": {"hold": ["S19a", "S26a"], "emph": ["L03.1", "L13.2", "L28.2", "L35.1"], "reveal": ["L32"], "twist": "L32"}}
story = {
    "slug": "ep140-town-photo",
    "title": "Our Town Photo Is Missing ONE Face \U0001F4F7",
    "made_for_kids": False,
    "premise": "Every year our whole town poses on the bleachers, and the photo only shows people who'll still be here next "
               "year. Two hundred twelve of us posed and two hundred eleven faces came out, with a pale gap where I sit.",
    "twist": "The photo was right. The photographer is never in it, and today the old man who has held the camera for eighty "
             "years, and who has never aged, hands it to me. I am the one behind it now, so the count comes out whole and he "
             "finally sits in the picture.",
    "world": "a bright town square on a sunny Saturday: white wooden bleachers in five rows, a red-brick town hall with "
             "bunting behind, a green chalkboard headcount, a big wooden box camera on a tripod, and the hall's long hallway "
             "of framed photos",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "phonemes": {"Okafor": "Okˈɑfɔɹ"},
    "key_color": "#7ed957",
    "gap": 0.15,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "look": look,
    "grade": {"shadows": [-0.01, 0.0, 0.03], "highlights": [0.03, 0.01, -0.02], "saturation": 1.08, "contrast": 1.05,
              "vignette": 0.12, "bloom": 0.15, "grain": 0.008, "red_line": 0.7, "red_lift_blue": 0.42},
    "asr_forgive": ["two hundred twelve", "two hundred eleven", "ay em", "mister okafor", "eight fifty nine"],
    "hud": {"object": "tag", "at": [-0.6, 0.76], "size": 0.5},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "set_moves": [],
    "frames_ok": [],
    "framing_ok": [],
    "framing_props": {"photo": [-4.6, 1.0, 1.5], "twelve": [-4.6, 1.0, 1.5], "eight": [-4.6, 1.0, 1.5], "fifty": [-4.6, 1.0, 1.5],
                      "nine": [-4.6, 1.0, 1.5], "it": [-0.5, -4.85, 1.4]},
    "staging_ok": ["S33/me+okafor close on purpose: he steps in and pats my shoulder, no overlap",
                   "S34/me+okafor close on purpose: his face over my shoulder after the pat, no overlap"],
    "music": {"root": 41, "mode": "major", "bpm": 104, "seed": 140,
              "sections": [
                  {"at": 0, "voices": ["pulse", "pluck_hi"], "energy": 0.45},
                  {"at": "L10", "voices": ["pad", "pluck_hi", "pulse"], "energy": 0.5},
                  {"at": "L17", "voices": ["drone", "pad", "pluck"], "energy": 0.4},
                  {"at": "L31", "voices": ["drone", "pad", "pluck"], "energy": 0.3},
              ]},
    "sound": {
        "rev": 1, "floor": "wood", "steps_db": -22,
        "ambience": [{"kind": "wind", "from": 0, "to": "end", "lufs": -46}],
        "sfx": [{"at": "L29+0.02", "kind": "click", "db": -10},
                {"at": "P1+0.05", "kind": "whoosh", "db": -22}],
        "music_drops": [["P1", "P1>"]],
    },
}
from blocky import timeline

vf = HERE.parent / "voice-timings.json"


def key(e):
    return e.get("at", e.get("from"))


if vf.exists():
    voice = json.loads(vf.read_text())
    _tl0 = timeline.build({"name": "ep140-town-photo", "lines": lines, "shots": [{"id": "S0"}], "gap": 0.15, "tail": 0.25,
                           "cast": cast}, voice)
    AT = timeline.resolver(_tl0["lines"], _tl0["duration"])
    for k in acting:
        acting[k].sort(key=lambda e: AT(key(e)))
    cues.sort(key=lambda e: AT(e["at"]))
story["rev"] = 2
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots, {len(cues)} cues")
