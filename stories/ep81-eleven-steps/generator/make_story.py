"""Writes ../story.json for "Our Stairs Grow One Step At NIGHT" (ep81-eleven-steps, batch 7).

Run from anywhere: python stories/ep81-eleven-steps/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast (me, Dad, Luis), the shots and their
cameras, the acting, the cues set.py reads (count, box, climber, dip, mydoor, ddoor, torch, props, car) and the score.

World (metres, z up): the stairs climb +y, nine treads (tread k at y 0.28(k-1)..0.28k, top z 0.19k), x -0.8..0.8; the
landing (step ten) is z 1.9 from y 2.52 to 4.9, my door at y 4.9 (x 0), my room beyond it. The hall runs -y from the
foot of the stairs to the front door at y -5, Dad's door on its left wall at y -1.8, the kitchen opens off its right
side (x 0.9..5.9). Acting yaw: 0 faces -y, 180 faces +y, 90 faces +x, -90 faces -x.
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
LZ = 1.9                      # the landing and my room's floor

# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True, "ink": "#24131f"}
cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#8e3f8f", "pattern": "stripes", "pattern_c": "#f6ead2",
           "pants": "#8a8d96", "shoes": "#ffffff", "sleeves": "long", "hair": "cap", "hair_c": "#6a4426", "face": dict(FACE)},
    "dad": {"age": "adult", "skin": "#e2b48c", "shirt": "#22306a", "pattern": "solid", "pants": "#7f9ccf",
            "pants_pattern": "plaid", "pants_pattern_c": "#2c3e7a", "shoes": "#7a5230", "sleeves": "long",
            "extras": ["coat"], "zip_c": "#f6ead2", "hair": "cap", "hair_c": "#8c8c94", "width": 1.1, "face": dict(FACE)},
    "luis": {"age": "adult", "skin": "#c98e5f", "shirt": "#3f9a4a", "pattern": "solid", "pants": "#2c3e55",
             "shoes": "#f4f4f2", "sleeves": "long", "hair": "cap", "hair_c": "#1c1410", "hat": "ballcap", "hat_c": "#d7263d",
             "face": dict(FACE)},
}

# ---------------------------------------------------------------------------------------------------- state
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {k: [] for k in cast}
cues = []
shots = []


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


CN = {"n": 11, "ticks": None}


def count(at, n, ticks=None):
    cue(at, "count", n=n, **({"ticks": ticks} if ticks is not None else {}))


def box(at, pos=None, **kw):
    if pos is None:
        cue(at, "box", on=False)
    else:
        cue(at, "box", on=True, pos=list(pos), **kw)


BOT = (0.0, -0.25, 0.06)                       # the box at the foot of the stairs, snug against the first step
ROOMBOX = (-0.55, 6.5, LZ + 0.06)              # beside my bed
DOORBOX = (0.0, 4.45, LZ + 0.06)               # shoved out onto the landing in front of my door


def clm(at, pos=None, **kw):
    if pos is None:
        cue(at, "climber", on=False)
    else:
        cue(at, "climber", on=True, pos=list(pos), **kw)


PS = {}


def props(at, **kw):
    """The props cue restates its whole state: merge, None removes."""
    for k, v in kw.items():
        if v is None or v is False:
            PS.pop(k, None)
        else:
            PS[k] = v
    cues.append({"at": at, "name": "props", **json.loads(json.dumps(PS))})


def dip(at, k, dur=0.5):
    cue(at, "dip", k=k, dur=dur)


def ST(k, dx=0.0):
    """On tread k (0 = the hall floor at the foot, 10 = the landing): where feet stand."""
    if k <= 0:
        return [dx, -0.45, 0.0]
    if k >= 10:
        return [dx, 3.2, LZ]
    return [dx, 0.28 * (k - 1) + 0.14, 0.19 * k]


# ---------------------------------------------------------------------------------------------------- cameras
def X(loc, tgt, lens, loc2=None, tgt2=None, lens2=None, push=0.10):
    """A camera, always with a small push toward the target unless a second key is given."""
    if loc2 is None and tgt2 is None and lens2 is None:
        loc2 = [loc[i] + (tgt[i] - loc[i]) * push for i in range(3)]
    ks = [[0, list(loc), list(tgt), lens]]
    ks.append([1, list(loc2 or loc), list(tgt2 or tgt), lens2 or lens])
    return ks


def S(at, cam, look, hand=0.004, fill=1.0, exp=0.0, step=2, note="", **kw):
    d = {"id": f"S{len(shots) + 1:02d}", "cam": cam, "step": step, "hand": hand, "look": look}
    if len(shots):
        d["at"] = at
    if fill != 1.0:
        d["fill"] = fill
    if exp:
        d["exp"] = exp
    d.update(kw)
    if note:
        d["note"] = note
    shots.append(d)
    return d


for k in acting:
    acting[k].append({"at": 0, "pos": [0, 20, 0], "hidden": True, "blend": 0, **NEUTRAL})

# camera stand-points
KSIDE = (3.0, 1.0, 1.55)                       # in the kitchen, looking across the stairs from their open side
TOP = (0.0, 3.0, 3.5)                          # on the landing, high, looking down the stairs
HALLCAM = (0.0, -0.2, 1.5)

# =========================================================================================== 01 L01-L08 the hook
count(0, 11)
box(0, BOT)
S(0, X((0.05, -1.15, 0.3), (0.0, 1.7, 1.05), 12.5, (0.05, -0.8, 0.32), None, 12.5), "night", hand=0.003,
  note="frame 1: low up the stairs from the foot, eleven plum steps, the box a shade brighter, tag 11")
# L02: the nightlight, then the top-down with each tread dipping in turn
S("L02", X((0.9, 3.4, 2.5), (1.65, 4.8, 2.3), 16), "night", note="the amber nightlight on the landing")
S("L02.1", X((0.05, 3.2, 3.9), (0.0, 0.9, 0.9), 11.5), "night", note="top-down: each tread dips in turn, nobody on them")
for i in range(9):
    dip(f"L02.1+{0.04 + 0.17 * i:.2f}", i + 1, 0.4)
# L03: by day, me counting up the stairs, tag 10
count("L03", 10)
box("L03")
put("me", "L03", ST(0), 180, "neutral", arms=[0, 70])
raw("me", "L03>", pos=ST(9), arms=[0, 70])
S("L03", X((3.1, 0.4, 1.7), (0.0, 1.0, 1.15), 11.5, (3.0, 0.7, 1.7), None, 11.5), "day", note="day: me walking up, a pointed finger, tag 10")
# L04: the same walk at night, tag 11; then two treads side by side
count("L04", 11)
box("L04", BOT)
put("me", "L04", ST(0), 180, "worried", arms=[0, 70])
raw("me", "L04.1", pos=ST(5), arms=[0, 70])
S("L04", X((3.1, 0.4, 1.7), (0.0, 1.0, 1.15), 11.5, (3.0, 0.7, 1.7), None, 11.5), "night", note="night: the same walk, tag 11")
gone("me", "L04.2")
S("L04.2", X((1.3, 0.2, 0.7), (0.0, 0.7, 0.45), 13), "night", hand=0.002, note="two treads side by side, identical")
# L05, L06: Luis counting on his fingers, then he leaves past the front door glass
put("luis", "L05", (0.15, -0.75), 180, "worried", arms=[60, 60])
props("L05", bowl={"pos": [0.62, -2.75, 0.74]})
S("L05", X((0.45, -3.3, 1.5), (0.1, -0.8, 1.4), 15), "night", note="Luis at the foot of the stairs, counting on his fingers")
walk("luis", "L06", (0.15, -1.0), "L06.1", (0.0, -4.0), 0, "worried")
S("L06", X((0.0, -0.9, 1.5), (0.0, -4.6, 1.25), 14), "night", note="Luis walks to the front door")
gone("luis", "L06.1")
cue("L06.1", "car", on=True, go=True, dur=1.8)
S("L06.1", X((0.0, -3.4, 1.35), (0.0, -5.0, 1.2), 17), "night", note="tail lights pulling away through the door glass")
cue("L06>", "car", on=False)
# L07: 2 a.m., the stairs empty, three treads dip
props("L07", bowl=None)
S("L07", X((0.0, -2.5, 1.15), (0.0, 1.6, 1.3), 12), "night", note="wide from the hall, 2 a.m., empty stairs")
for i, k in enumerate((2, 4, 6)):
    dip(f"L07.1+{0.15 + 0.35 * i:.2f}", k, 0.5)
# L08: morning, my hand flat on the cold step just below the landing
count("L08", 10)
box("L08")
put("me", "L08", [0.0, 2.0, 0.19 * 8], 180, "neutral", lean=48, arms=[10, 70])
S("L08", X((0.8, 1.2, 2.5), (0.0, 2.3, 1.7), 13, (0.55, 1.5, 2.35), None, 13), "day", note="morning: my hand on the step below the landing, cold")
gone("me", "L08>")

# =========================================================================================== 02 L09-L16 Dad's rule
put("dad", "L09", (0.15, -0.9), 180, "stern")
props("L09", hold_mug=True)
S("L09", X((0.0, 1.0, 1.75), (0.0, -0.9, 1.45), 14), "day", note="Dad at the foot of the stairs with his mug, stern")
S("L10", X((-0.2, -2.6, 1.65), (-0.78, -3.4, 1.7), 19), "day", note="the hall clock at ten")
put("dad", "L10.1", (0.15, -0.9), 180, "stern", arms=[0, 100])
props("L10.1", hold_mug=False)
S("L10.1", X((2.4, -0.3, 1.5), (0.1, -0.9, 1.45), 14), "day", note="Dad pointing up the stairs")
put("me", "L11", ST(10), 180, "neutral", arms=[0, 40])
props("L11", hold_glass=True)
S("L11", X((3.0, 0.2, 1.7), (0.0, 1.6, 2.0), 11.5), "day", note="me at the top with an empty glass, Dad below shaking his head")
put("dad", "L11", (0.15, -0.9), 180, "stern", head=[25, 0])
raw("dad", "L11.1", head=[-25, 0], blend=0.3)
gone("me", "L12")
props("L12", hold_glass=False)
walk("dad", "L12", ST(0), "L12>", ST(2), 180, "tired")
S("L12", X((0.0, -2.0, 1.2), (0.0, 0.3, 0.9), 13), "evening", note="Dad's slippers on the bottom steps from behind, me already upstairs")
put("dad", "L13", (2.2, -1.2), 90, "tired")
S("L13", X((3.4, -0.4, 0.8), (2.2, -1.2, 0.5), 15), "day", hand=0.003, note="morning kitchen doorway: carpet fluff on Dad's pajama knees")
gone("dad", "L14")
put("me", "L14", (4.6, 1.55), 90, "smirk", arms=[0, 40])
S("L14", X((3.0, 0.6, 1.6), (4.6, 1.6, 1.4), 14), "day", note="me at the fridge, smirking")
gone("me", "L15")
# L15, L16: night, me at the top with a flashlight, tag 10 (the box isn't out yet)
count("L15", 10)
box("L15")
put("me", "L15", [0.2, 3.0, LZ - 0.62], 180, "neutral", arms=[40, 40])
props("L15", hold_flash=True)
cue("L15", "torch", on=True, pos=[0.2, 2.9, LZ + 0.7], target=[0.0, 0.5, 0.9])
S("L15", X((0.2, 4.2, LZ + 1.1), (0.0, 2.6, LZ + 0.5), 12), "evening", note="me at the top step with a flashlight, tag 10")
S("L16", X((0.0, 3.6, 3.4), (0.0, 0.9, 1.0), 11.5), "evening", note="the flashlight down the empty stairs")

# =========================================================================================== 03 L17-L21 Dad and the box
cue("L17", "torch", on=False)
props("L17", hold_flash=False)
gone("me", "L17")
cue("L17", "ddoor", open=0, to=88, dur=1.0)
S("L17", X((0.0, 2.9, 2.9), (-0.9, -1.8, 1.0), 12.5), "evening", note="down the stairs: Dad's door opening in the hall below")
put("dad", "L18", (-0.1, -1.6), 0, "stern", arms=[50, 50])
cue("L18", "ddoor", open=88)
walk("dad", "L18", (-0.45, -1.9), "L18>", (0.0, -1.1), 0, "stern", arms=[50, 50])
box("L18", (-0.45, -2.2, 0.95), pitch=8, to=[0.0, -1.5, 0.95], dur=1.9)
S("L18", X((0.9, -0.1, 1.5), (-0.25, -1.4, 1.1), 13), "evening", note="Dad carrying the carpeted box out of his room")
put("dad", "L19", (0.0, -1.0), 180, "stern", lean=18, arms=[55, 55])
box("L19", (0.0, -1.55, 1.0), pitch=75, roll=0)
S("L19", X((0.35, -0.55, 1.35), (0.0, -1.5, 1.05), 14, (0.25, -0.75, 1.3), None, 14), "evening", hand=0.002,
  note="close: the box's plum carpet, its brass rod; tilted, two plum strokes on the underside")
put("dad", "L20", (0.0, -0.95), 180, "stern", lean=38, arms=[60, 60])
count("L20", 11)
box("L20", BOT)
S("L20", X((1.1, -1.7, 0.75), (0.0, -0.3, 0.3), 13), "evening", note="Dad sets it snug against the first step")
walk("dad", "L21", (0.0, -0.9), "L21>", (-0.5, -1.8), 0, "tired")
cue("L21+0.3", "ddoor", open=88, to=0, dur=0.8)
S("L21", X((0.0, 0.9, 1.7), (-0.3, -1.6, 1.3), 14), "evening", note="Dad walking back to his room without looking up")
gone("dad", "L21>")

# =========================================================================================== 04 L22-L28 the box, the fight
S("L22", X((0.0, 3.8, 4.2), (0.0, 0.2, 0.35), 10.5), "evening", note="top-down: eleven steps, the box the bottom one")
put("me", "L23", [0.0, 3.1, LZ], 0, "angry", arms=[0, 0])
S("L23", X((0.1, 0.9, 2.2), (0.0, 3.1, 3.4), 15), "evening", note="me, angry, at the top")
put("me", "L24", [0.0, 3.1, LZ], 0, "angry", side=[-35, -35], arms=[50, 50])
S("L24", X((0.3, 1.2, 2.4), (0.0, 3.1, 3.3), 15, (0.1, 1.5, 2.45), None, 15), "evening", note="me at the top, arms folded")
walk("me", "L25", ST(3), "L25>", ST(4), 0, "smirk")
S("L25", X((0.65, 0.2, 0.75), (0.0, 0.45, 0.65), 15, (0.6, 0.35, 0.78), None, 15), "evening", hand=0.002, note="a past-tense if: socks tiptoeing down a tread")
gone("me", "L25>")
count("L26", 10)
box("L26")
put("dad", "L26", (3.9, -1.2), -90, "neutral", arms=[0, 60])
props("L26", hold_mug=True)
S("L26", X((3.0, -3.4, 1.55), (3.9, -1.2, 1.4), 14), "day", note="breakfast: Dad shrugs over his mug")
put("dad", "L27", (3.7, -1.2), -90, "angry", arms=[40, 40])
put("me", "L27", (2.4, -1.2), 90, "angry", arms=[40, 40])
S("L27", X((3.0, -3.2, 1.5), (3.0, -1.2, 1.4), 12.5), "day", note="the two of us arguing across the table, both angry")
gone("dad", "L28")
gone("me", "L28")
props("L28", hold_mug=False)
# L28: Saturday night, me carries the box up the stairs and hides it by my bed
count("L28", 10)
walk("me", "L28", ST(0), "L28.1", ST(10), 180, "neutral", arms=[55, 55])
box("L28", (0.0, -0.85, 1.0), pitch=6, to=[0.0, 3.1, LZ + 1.0], dur=1.7)
S("L28", X((3.0, 0.2, 1.7), (0.0, 1.4, 1.5), 11.5), "night", note="night: me carrying the box up the stairs")
gone("me", "L28.1")
box("L28.1", ROOMBOX)
S("L28.1", X((1.5, 5.6, LZ + 1.5), (-0.5, 6.6, LZ + 0.3), 12), "roomdim", note="the box beside my bed, tag back to 10")

# =========================================================================================== 05 L29-L35 the count
put("me", "L29", [-1.7, 8.0, LZ + 0.55], 0, "worried", lean=-90, arms=[0, 0])
S("L29", X((0.0, 5.8, LZ + 0.9), (-1.2, 8.0, LZ + 0.6), 11.5), "roomdim", fill=0.6,
  note="my room in the dark, me in bed with my eyes open, the gap under the door glowing amber")
for i, (ref, k) in enumerate((("L30", 1), ("L30.1", 2), ("L30.2", 3))):
    count(ref, 10, i + 1)
    dip(ref, k, 0.55)
    S(ref, X((0.9, -0.2 + 0.28 * i, 0.55 + 0.19 * i), (0.0, 0.1 + 0.28 * i, 0.3 + 0.19 * i), 15, push=0.12), "dim", hand=0.002,
      note=f"tread {k} dips, nobody on it")
put("me", "L31", [-1.7, 8.0, LZ + 0.55], 0, "scared", lean=-90, arms=[70, 0])
count("L31", 10, 3)
S("L31", X((-1.0, 7.0, LZ + 2.2), (-1.7, 8.0, LZ + 0.7), 13), "roomdim", fill=0.7, note="me counting on my fingers in bed")
gone("me", "L31>")
for i, (ref, k) in enumerate((("L32", 7), ("L32.1", 8), ("L32.2", 9))):
    count(ref, 10, k)
    dip(ref, k, 0.55)
    S(ref, X((0.9, 0.28 * (k - 1) - 0.1, 0.19 * k + 0.35), (0.0, 0.28 * (k - 1) + 0.14, 0.19 * k), 15, push=0.12), "dim", hand=0.002,
      note=f"tread {k} dips, nobody on it")
count("P01", 10, 9)
S("P01", X((0.0, 6.1, LZ + 0.05), (0.0, 4.95, LZ + 0.04), 13), "roomdim", fill=0.0, note="the gap under my door, still, glowing")
count("L33", 10, 10)
dip("L33", 9, 0.7)
S("L33", X((0.8, 2.0, 2.2), (0.0, 2.4, 1.75), 15), "dim", hand=0.002, note="the top tread at the landing dips")
S("L34", X((0.0, 2.7, 2.7), (0.0, 4.8, LZ + 0.2), 12), "dim", note="ten is the landing: the nightlight, my door at the end")
S("L35", X((0.0, 6.6, LZ + 1.3), (0.0, 4.95, LZ + 1.2), 13), "roomdim", fill=0.4, note="ten is my door, from inside")

# =========================================================================================== 06 L36-L42 the Climber
# L36: the door bows, a long flat hand under it. L37-L40: the face at the gap. L41-L42: the whole shape.
count("L36", 10)
cue("L36", "mydoor", open=0, bow=0.0, to=0, bow_to=1.0, dur=0.9)
clm("L36", None)
props("L36", chand={"pos": [0.0, 4.72, LZ + 0.045], "yaw": 0})
cue("L36", "torch", on=False)
S("L36", X((0.0, 5.9, LZ + 0.5), (0.0, 4.9, LZ + 0.35), 13, (0.0, 5.6, LZ + 0.3), None, 13), "roomdim", fill=0.5, note="my door bows in its frame; a long flat hand just past the gap")
put("me", "L37", [0.15, 5.9, LZ + 0.17], 180, "scared", lean=-86, arms=[80, 0])
props("L37", chand=None)
cue("L37", "mydoor", open=0, bow=1.0)
cue("L37", "torch", on=True, pos=[0.4, 5.75, LZ + 0.08], target=[0.0, 4.7, LZ + 0.05])
clm("L37", [0.0, 3.22, LZ], yaw=180, fold=1.5, roll=0, reach=8, hp=0, hoff=0.05, kx=0.0, ky=1.0, kz=0.2, ax=0.0, az=1.3)
S("L37", X((0.15, 6.4, LZ + 0.2), (0.0, 4.9, LZ + 0.3), 13), "roomdim", fill=0.4, note="me flat on the floor with the flashlight, looking at the gap")
put("me", "L37>", [0.15, 5.9, LZ + 0.17], 180, "scared", lean=-86, arms=[80, 0], hidden=True)
S("L38", X((0.0, 5.65, LZ + 0.065), (0.0, 4.7, LZ + 0.065), 12, (0.0, 5.45, LZ + 0.065), None, 12), "roomdim", fill=0.0, hand=0.002,
  note="the gap: two big black eyes in a cream face, looking back")
S("L39", X((0.0, 5.4, LZ + 0.065), (0.0, 4.7, LZ + 0.065), 12, (0.0, 5.2, LZ + 0.065), None, 12), "roomdim", fill=0.0, hand=0.002,
  note="sideways, way too big")
S("L40", X((-0.12, 5.5, LZ + 0.06), (-0.2, 4.7, LZ + 0.075), 20, (-0.12, 5.25, LZ + 0.06), None, 20), "roomdim", fill=0.0, hand=0.002,
  note="the cover frame: one eye at the gap, an inch from mine")
cue("L41", "mydoor", open=0, bow=0.0)
clm("L41", [0.15, 3.0, LZ], yaw=180, fold=0.62, roll=-75, reach=8, hp=5, hy=-80, hoff=0.42, kx=1.6, ky=0.2, kz=0.2)
cue("L41", "torch", on=False)
S("L41", X((2.3, 1.7, 3.4), (0.3, 3.6, 2.7), 10, (2.25, 1.9, 3.3), None, 10), "dim", hand=0.003, note="from the stairs side, lit: it has to fold under our ceiling")
S("L41.1", X((1.8, 3.4, 2.3), (0.2, 3.7, 3.0), 13, (1.6, 3.5, 2.4), None, 13), "dim", hand=0.003, note="its head bent flat on its shoulder, its eye on me")

# =========================================================================================== 07 L43-L51 the rule's logic
count("L43", 10)
clm("L43", None)
S("L43", X((0.0, 3.4, 3.2), (0.0, 0.2, 0.7), 11.5), "dim", note="down the stairs past where it stood: ten treads, the bottom one bare")
S("L44", X((0.0, 1.2, 1.8), (0.0, 3.0, 1.9), 40, (0.0, 1.2, 1.8), None, 55), "dim", hand=0.002, note="the tag, ten")
box("L45", ROOMBOX)
S("L45", X((1.5, 5.6, LZ + 1.5), (-0.55, 6.6, LZ + 0.3), 12), "roomdim", note="the box beside my bed")
# L46-L47: the diagram-like top-down: the box at the bottom, the Climber one tread below the landing
count("L46", 11)
box("L46", BOT)
S("L46", X((0.0, 3.9, 4.4), (0.0, 0.2, 0.4), 10.5), "evening", note="top-down: with eleven steps (the box the bottom one)")
clm("L46.1", [0.0, 2.38, 0.19 * 9], yaw=180, fold=0.62, roll=-75, reach=8, hp=5, hy=-80, hoff=0.42, kx=0.0, ky=-1.4, kz=0.3, az=1.2)
count("L46.1", 11)
S("L46.1", X((0.0, 3.9, 4.3), (0.0, 1.9, 1.8), 12), "evening", note="ten leaves it one tread below the landing")
S("L47", X((1.1, 4.1, 3.0), (0.0, 2.4, 1.9), 13), "evening", note="one step below the landing, one step from me")
clm("L48", None)
S("L48", X((1.3, -1.7, 0.9), (0.0, -0.4, 0.4), 13), "dawn", note="dawn: Dad lifts the box away so I'd never know")
put("dad", "L48", (0.0, -0.95), 180, "tired", lean=30, arms=[60, 60])
box("L48", (0.0, -0.62, 0.9), pitch=6)
count("L48", 10)
box("L48>")
gone("dad", "L48>")
count("L49", 10)
box("L49", ROOMBOX)
S("L49", X((1.6, 5.7, LZ + 1.6), (-0.55, 6.5, LZ + 0.25), 12), "roomdim", note="the box by my bed")
put("me", "L50", [0.3, 6.2, LZ], 90, "worried", head=[-40, 0])
S("L50", X((1.3, 7.6, LZ + 1.7), (0.3, 6.2, LZ + 1.5), 12), "roomdim", fill=0.8, note="me, worried, looking from the box to the door")
put("me", "L51", [0.3, 6.2, LZ], 180, "neutral", head=[0, 0])
raw("me", "L51.1", expr="angry")
S("L51", X((0.4, 7.8, LZ + 1.6), (0.3, 6.2, LZ + 1.6), 14), "roomdim", fill=0.9, note="me, eyes widening, then determined")

# =========================================================================================== 08 L52-L58 the box on the landing
cue("L52", "mydoor", open=0, to=26, dur=0.6)
put("me", "L52", [0.3, 6.0, LZ], 180, "angry", arms=[50, 50], lean=20)
S("L52", X((1.0, 7.6, LZ + 1.5), (0.1, 5.3, LZ + 0.5), 12), "roomdim", fill=0.7, note="my door open a crack, the box slides out onto the landing")
box("L52+0.2", ROOMBOX, to=list(DOORBOX), dur=0.8)
gone("me", "L52.1")
count("L52.1", 11)
cue("L52.1", "mydoor", open=26)
clm("L53", [0.15, 2.7, LZ], yaw=180, fold=0.62, roll=-75, reach=8, hp=-10, hy=-80, hoff=0.42, kx=1.2, ky=0.0, kz=0.3, az=1.0)
box("L53", DOORBOX)
S("L53", X((0.0, 1.3, LZ + 0.35), (0.0, 4.5, LZ + 0.4), 12), "dim", hand=0.003, note="floor level: the box between its flat hands and my door")
cue("L53", "mydoor", open=0)
S("L54", X((1.7, 3.0, LZ + 0.9), (0.1, 3.6, LZ + 0.9), 12, (1.4, 3.1, LZ + 0.9), None, 12), "dim", hand=0.003,
  note="it looks down at the box, a long time")
S("L55", X((0.3, 4.3, LZ + 1.1), (0.15, 2.9, LZ + 1.4), 15), "dim", hand=0.003, note="it doesn't climb it")
S("L56", X((0.9, 2.2, 2.8), (0.2, 3.8, 3.3), 11.5, (0.9, 2.3, 2.9), None, 11.5), "dawn", hand=0.003, note="dawn comes up in the round window, it stands one step short")
S("L57", X((0.0, 6.6, LZ + 1.0), (0.0, 5.1, LZ + 0.8), 13), "dawn", fill=0.9, note="me with my back to the door, listening")
put("me", "L57", [0.0, 5.45, LZ - 0.62], 180, "scared", arms=[40, 40])
raw("me", "L57.1", expr="tired")
cue("L57", "torch", on=False)

# =========================================================================================== 09 L58-L66 the warm turn
clm("L58", None)
box("L58", DOORBOX)
count("L58", 10)
put("me", "L58", [0.35, 4.35, LZ - 0.62], 180, "asleep", lean=0)
S("L58", X((0.0, 2.0, 3.0), (0.2, 4.4, LZ + 0.6), 12), "dawn", fill=1.0, note="morning: the landing empty but for the box; me asleep against my door")
put("dad", "L58", [0.0, 2.6, LZ], 0, "soft")
walk("dad", "L58.1", [0.0, 2.6, LZ], "L59", [0.0, 3.0, LZ], 180, "soft")
S("L59", X((0.0, 4.3, LZ + 1.4), (0.0, 2.6, LZ + 1.5), 14), "dawn", fill=0.9, note="Dad's face at the top of the stairs, soft")
put("dad", "L60", [-0.35, 4.0, LZ - 0.62], 180, "soft")
S("L60", X((2.0, 3.0, LZ + 1.5), (-0.1, 4.2, LZ + 1.0), 13), "dawn", fill=0.9, note="Dad sits down beside me on the landing")
S("L61", X((1.0, 3.0, LZ + 0.7), (0.0, 4.4, LZ + 0.4), 13), "dawn", fill=0.8, note="the box between us")
put("dad", "L62", [-0.35, 4.0, LZ - 0.62], 180, "soft", head=[40, 0])
S("L62", X((0.0, 3.2, LZ + 1.2), (-0.35, 4.0, LZ + 1.0), 20), "dawn", fill=0.9, note="Dad, close, soft")
put("me", "L63", [0.35, 4.35, LZ - 0.62], 180, "soft")
S("L63", X((0.5, 3.2, LZ + 1.2), (0.35, 4.35, LZ + 1.0), 20), "dawn", fill=0.9, note="me, close, awake")
put("me", "L64", [0.35, 4.35, LZ - 0.62], 180, "smile")
put("dad", "L64", [-0.35, 4.0, LZ - 0.62], 180, "smile")
S("L64", X((0.2, 0.4, 3.3), (0.0, 4.0, 2.2), 11.5), "day", fill=0.9, note="wide down the stairs in daylight, both of us on the landing, smiling")
# L65, L66: taking turns
gone("dad", "L65")
count("L65", 11)
box("L65", BOT)
put("me", "L65", [0.0, -1.0, 0.0], 180, "neutral", lean=26, arms=[55, 55])
S("L65", X((1.2, -1.8, 0.8), (0.0, -0.3, 0.3), 13), "night", note="night: me setting the box at the bottom, tag 11")
gone("me", "L65>")
count("L66", 10)
box("L66", (0.0, -0.62, 0.9), pitch=6)
put("dad", "L66", [0.0, -0.95, 0.0], 180, "tired", lean=30, arms=[60, 60])
S("L66", X((1.2, -1.7, 0.9), (0.0, -0.5, 0.4), 13), "dawn", note="dawn: Dad lifting it, tag 10")
box("L66>")
gone("dad", "L66>")

# =========================================================================================== 10 L67-L71 the sting and the loop
count("L67", 11)
box("L67", BOT)
S("L67", X((0.0, -1.5, 0.35), (0.0, 1.7, 1.1), 12.5, (0.0, -1.15, 0.37), None, 12.5), "night", hand=0.003, note="the stairs at two a.m. from the bottom, one tread dips")
dip("L67.1", 5, 0.6)
S("L68", X((0.8, 1.6, 2.6), (0.0, 2.3, 1.75), 14), "night", hand=0.003, note="the cold step just below the landing")
clm("L69", [0.0, 2.38, 0.19 * 9 - 0.35], yaw=180, fold=0.55, roll=-75, reach=8, hp=-5, hy=-80, hoff=0.42, kx=0.0, ky=-1.5, kz=0.4, az=1.0)
S("L69", X((0.0, 0.2, 2.2), (0.0, 2.4, 2.3), 13), "night", hand=0.003, note="on the step just below the landing, it has sat down")
S("L70", X((0.9, 1.0, 2.5), (0.0, 2.35, 2.2), 12, (0.8, 1.2, 2.45), None, 12), "night", hand=0.003, note="head on its shoulder, facing up, waiting")
clm("L71", None)
count("L71", 11)
S("L71", X((0.05, -1.5, 0.3), (0.0, 1.7, 1.05), 12.5, (0.05, -1.15, 0.31), None, 12.5), "night", hand=0.003, note="push in to the bottom step: frame 1 again")

# ---------------------------------------------------------------------------------------------------- story
look = {"style": "closer", "flash_safe": True,
        "polish": {"emph": ["L01", "L22", "L33", "L38", "L44", "L52", "L70"], "reveal": ["L38", "L44", "L70"], "twist": "L43",
                   "quiet": [["L59", "L63"]], "camera": True, "idle": True, "ease": True}}
story = {
    "slug": "ep81-eleven-steps",
    "title": "Our Stairs Grow One Step At NIGHT \U0001FA9C",
    "made_for_kids": False,
    "premise": "Our stairs have ten steps by day and eleven at night, and at two in the morning they creak ten times with "
               "nobody on them. Dad's one house rule is that everyone is upstairs by ten and nobody is on the stairs "
               "after, so one night I sit at the top with a flashlight to catch the new step.",
    "twist": "The eleventh step is a carpeted box Dad has set at the bottom of the stairs every night for eleven years, "
             "because something very tall climbs exactly ten steps each night and stops one short of my door. With the "
             "box in my room it reaches the landing, and shoved out in front of my door it stands one step short until "
             "dawn. Now we take turns setting it, and last night it sat down to wait.",
    "world": "a two-storey house's one straight staircase of honey oak and plum carpet with a landing, a round window "
             "and an amber nightlight, a hall with a mustard lamp, and a kitchen beside it",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#c77dff",
    "gap": 0.12,
    "tail": LOOP,
    "min_read": 0.15,
    "fade_in": False,
    "fade_out": False,
    "look": look,
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.01, -0.02], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.2, "grain": 0.008, "red_line": 0.7},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "music": {"root": 45, "mode": "minor", "bpm": 76, "seed": 81,
              "sections": [
                  {"at": 0, "voices": ["tick", "pluck", "pulse"], "energy": 0.45},
                  {"at": "L17", "voices": ["tick", "pluck", "pad"], "energy": 0.4},
                  {"at": "L29", "voices": ["tick", "pulse"], "energy": 0.22},
                  {"at": "L33", "voices": ["drone", "tick"], "energy": 0.5},
                  {"at": "L58", "voices": ["pad", "drone"], "energy": 0.4, "mode": "major"},
                  {"at": "L67", "voices": ["drone", "tick"], "energy": 0.35},
              ]},
    "sound": {
        "rev": 1, "floor": "wood", "steps_db": -24,
        "ambience": [{"kind": "room", "from": 0, "to": "end", "lufs": -44}],
        "sfx": [
            {"at": "L01.2", "kind": "creak", "db": -14, "dur": 0.9},
            {"at": "L02.1+0.04", "kind": "creak", "db": -20, "dur": 0.35},
            {"at": "L02.1+0.38", "kind": "creak", "db": -20, "dur": 0.35},
            {"at": "L02.1+0.72", "kind": "creak", "db": -20, "dur": 0.35},
            {"at": "L02.1+1.06", "kind": "creak", "db": -20, "dur": 0.35},
            {"at": "L17+0.1", "kind": "latch", "db": -18},
            {"at": "L30", "kind": "creak", "db": -16, "dur": 0.5},
            {"at": "L30.1", "kind": "creak", "db": -16, "dur": 0.5},
            {"at": "L30.2", "kind": "creak", "db": -16, "dur": 0.5},
            {"at": "L32", "kind": "creak", "db": -16, "dur": 0.5},
            {"at": "L32.1", "kind": "creak", "db": -16, "dur": 0.5},
            {"at": "L32.2", "kind": "creak", "db": -16, "dur": 0.5},
            {"at": "L33", "kind": "creak", "db": -14, "dur": 0.7},
            {"at": "L36+0.2", "kind": "creak", "db": -16, "dur": 1.4},
            {"at": "L52+0.2", "kind": "whoosh", "db": -22},
            {"at": "L67.1", "kind": "creak", "db": -20, "dur": 0.5},
        ],
        "music_drops": [{"from": "L32>", "to": "P01>"}],
    },
}
from blocky import timeline

voice = json.loads((HERE.parent / "voice-timings.json").read_text())
_tl0 = timeline.build({"name": "ep81-eleven-steps", "lines": lines, "shots": [{"id": "S0"}], "gap": 0.12, "tail": LOOP,
                       "min_read": 0.15, "cast": cast}, voice)
AT = timeline.resolver(_tl0["lines"], _tl0["duration"])
for k in acting:
    acting[k].sort(key=lambda e: AT(e["at"]))
cues.sort(key=lambda e: AT(e["at"]))
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots, {len(cues)} cues")
