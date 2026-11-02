"""Writes ../story.json for ep15 "Only one of us walked out of the mirror maze" (script.md, brief.md, 2026-10-31).

Run from anywhere: python stories/mirror-maze/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting (me, Tasha, the maze guy and the copy), the cues set.py reads, the shot looks, the score and the sound.

THE COPY. It is never a second spec: set.py builds it from Tasha's. Its keys are in the rig's own local terms, so on a
mirrored rig my own keys verbatim make it my reflection, LAG later, with `pos` and `yaw` reflected across the glass
plane. `m()` writes my key and, while a plane is set (MIR), the copy's lagged reflection of it. `put()` is a cut: it
teleports without a walk. Keys are sorted by their resolved time at the end (a lagged key can land after the next
scene's cut).

Places (metres, the field is z = 0): the maze's front faces -y at y = 12 with its arch at x = 3, steps and a deck
in front; the duckboards run from it down to the fry van at (1, -16). The worklight is at (2, 3.5) and the bumper
cars' rink and its tarp are east of it. The truck is at (-4, 7). The maze's inside is built at x = 60 and is cut
to on the action: a corridor 1.5 m wide along +y, its panes clear, with the copies' ghosts in the cells beside it.
"""
import json
import math
from pathlib import Path

from blocky import timeline

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
LAG = 0.395
LOOP = 0.25

# ---------------------------------------------------------------------------------------------------- the words
# Word-check pins and the script's own holds are all in lines.json (gap) and here (pauses)
TEMPO = {"L16": 0.95, "L77": 0.92, "L81": 0.92}
SPOKEN = {("L77", 1): "back also", ("L16", 1): "Tasha's"}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]
    for k, ch in enumerate(ln.get("chunks", [])):
        if (ln["id"], k) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], k)]

# ---------------------------------------------------------------------------------------------------- cast
cast = {
    "me": {"age": "adult", "skin": "#d9a27a", "shirt": "#b8697a", "pattern": "solid", "collar": "#8f4a5c",
           "pants": "#151518", "shoes": "#0c0c0e", "sleeves": "long", "hair": "cap", "hair_c": "#3a2a20",
           "hat": "bucket", "hat_c": "#6f9a2e", "face": {"eyes": "round", "brows": True, "ink": "#24131f"}},
    "tasha": {"age": "adult", "skin": "#b07850", "shirt": "#f0c419", "pattern": "solid", "collar": "#d8aa12",
              "pants": "#151518", "shoes": "#0c0c0e", "sleeves": "long", "hair": "swoop", "hair_c": "#5a2a48",
              "fringe": "hard", "hat": "none", "extras": ["coat", "hooddown"], "zip_c": "#3b3224",
              "face": {"eyes": "round", "brows": True, "ink": "#24131f"}},
    "guy": {"age": "adult", "skin": "#6e4a33", "shirt": "#3b3e4c", "pattern": "solid", "pants": "#3a3d42",
            "shoes": "#0c0c0e", "sleeves": "long", "hair": "none", "hat": "hood", "hat_c": "#3b3e4c", "width": 1.15,
            "face": {"eyes": "round", "brows": True, "ink": "#1a0f0a"}},
}

# ---------------------------------------------------------------------------------------------------- time
voice = json.loads((HERE.parent / "voice-timings.json").read_text())
# the pauses' lengths are set below; they don't move any line's own timing before them, so use a first pass
PAUSE = {"P01": 1.8, "P02": 0.5, "P03": 1.8}
for ln in lines:
    if ln["id"] in PAUSE:
        ln["pause"] = PAUSE[ln["id"]]
_tl0 = timeline.build({"name": "mirror-maze", "lines": lines, "shots": [{"id": "S0"}], "gap": 0.12, "tail": LOOP,
                       "cast": cast}, voice)
AT = timeline.resolver(_tl0["lines"], _tl0["duration"])


def sec(ref):
    return round(AT(ref), 3)


import re

_REF = re.compile(r"^(?P<b>[^+-]+)(?P<o>[+-]\d+(?:\.\d+)?)?$")


def fmt(a):
    """A time as a story.json ref: a ref (or seconds) with one combined offset."""
    ref, off = a if isinstance(a, tuple) else (a, 0.0)
    if isinstance(ref, (int, float)):
        return round(ref + off, 3)
    m_ = _REF.match(ref)
    base, o = (m_.group("b"), float(m_.group("o") or 0)) if m_ else (ref, 0.0)
    off = round(off + o, 3)
    return base if abs(off) < 1e-9 else f"{base}{off:+.3f}"


def lag(a, extra=0.0):
    ref, off = a if isinstance(a, tuple) else (a, 0.0)
    return (ref, off + LAG + extra)


# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True, "stride": 0,
           "bow": 0}
acting = {"me": [], "tasha": [], "guy": [], "copy": []}
MIR = None          # the glass plane x = MIR: while set, m() and put() also drive the copy
DY = 0.0


def refl(pos, plane):
    return [round(2 * plane - pos[0], 3), pos[1]] + list(pos[2:])


def raw(who, at, **kw):
    acting[who].append({"at": fmt(at), **kw})


def put(who, at, pos, **kw):
    """A cut: the character is there from this instant, with everything it doesn't set back to neutral."""
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": fmt(at), "pos": prev})
    base = {**NEUTRAL, "hidden": False, "expr": "neutral" if who != "me" else "worried"}
    keys.append({"at": fmt(at), "pos": pos, "blend": 0, **base, **kw})


def hide(who, at):
    acting[who].append({"at": fmt(at), "hidden": True, "blend": 0})


def m(at, pos=None, **kw):
    """One of my keys (a walk, a pose), and its lagged reflection for the copy while MIR is set."""
    k = dict(kw)
    if pos is not None:
        k["pos"] = pos
    raw("me", at, **k)
    if MIR is not None:
        c = dict(kw)
        if pos is not None:
            c["pos"] = refl(pos, MIR)
        if "yaw" in c:
            c["yaw"] = -c["yaw"]
        raw("copy", lag(at), **c)


def mput(at, pos, yaw=0, **kw):
    """A cut for both of us: I'm there, and so is my reflection across MIR (no lag on a cut)."""
    put("me", at, pos, yaw=yaw, **kw)
    if MIR is not None:
        ck = {k: v for k, v in kw.items() if k != "expr"}
        put("copy", at, refl(pos, MIR), yaw=-yaw, expr=kw.get("expr", "worried"), **ck)


def mouth(who, a, b, lo=0.0, hi=0.8, flap=True):
    acting[who].append({"from": fmt(a), "to": fmt(b), "mouth": [lo, hi], "flap": flap})


def cmouth(a, b, hi=0.8):
    """The copy's mouth makes my words, late, silent."""
    acting["copy"].append({"from": fmt(lag(a)), "to": fmt(lag(b)), "mouth": [0.0, hi], "flap": True})


def hide_all(at, *who):
    for w in who:
        hide(w, at)


# ---------------------------------------------------------------------------------------------------- shots
shots = []      # (at, step, cam spec dict, looks dict or None, dof or None, note)
RAIN_OFF = set()


def S(at, cam, step=2, look=None, dof=None, follow=None, hand=None, note="", rain=True):
    d = {"at": at, "cam": cam, "step": step, "look": look, "dof": dof, "follow": follow, "hand": hand, "note": note,
         "rain": rain}
    shots.append(d)
    return d


def one(loc, tgt, lens, roll=0):
    return [[0, list(loc), list(tgt), lens] + ([roll] if roll else [])]


def mv(a, b, lens_a, lens_b=None):
    return [[0, list(a[0]), list(a[1]), lens_a], [1, list(b[0]), list(b[1]), lens_b or lens_a]]


# =========================================================================================== 01 the joke, L01 to L11
TASHA_A, ME_A = [2.4, 8.4], [3.6, 8.4]     # the open: facing each other under the maze's glow, side-on to the lens
CAM_OPEN = ((3.0, 3.6, 1.38), (3.0, 8.4, 1.5), 34)
put("tasha", 0, TASHA_A, yaw=90, expr="smirk", head=[-45, 0], arms=[0, 82])
put("me", 0, ME_A, yaw=-90, expr="neutral", head=[40, 0])
hide("copy", 0)
hide("guy", 0)
S(0, one(*CAM_OPEN), 2, note="the open: side-on two-shot, Tasha points at my green hat")
mouth("tasha", "L01.3", "L01>", 0.1, 0.8)
S("L02", one((3.2, 4.0, 1.45), (3.5, 8.4, 1.6), 60), 2, note="my face, resigned")
mouth("me", "L02.1", "L02.1>", 0.1, 0.7)
raw("tasha", "L03", arms=[0, 0], blend=0.3)
S("L03", one((0.3, 4.2, 1.3), (3.0, 8.4, 1.45), 30), 2, note="two-shot, the rule")
put("tasha", "L04", TASHA_A, yaw=0, expr="grin", head=[0, 0], arms=[85, 85])
put("me", "L04", ME_A, yaw=-60, expr="worried", head=[0, 0])
S("L04", one((2.4, 4.6, 1.5), (2.4, 8.4, 1.55), 46), 2, note="her FRIES yell, a mouth flap, both arms up")
mouth("tasha", "L04.1", "L04.1>", 0.2, 0.9)
put("tasha", "L05", [2.4, 8.4], yaw=0, expr="grin", head=[0, 0], arms=[0, 0])
S("L05", one((2.1, 4.8, 1.5), (2.4, 8.4, 1.56), 56), 2, note="her grin, the shine bright")
# L06 a wide from behind: the two of us walking up to the maze
put("tasha", "L06", [0.4, 3.0], yaw=180, expr="smirk")
put("me", "L06", [1.3, 3.0], yaw=180, expr="neutral")
raw("tasha", "L06>", pos=[0.6, 6.0])
raw("me", "L06>", pos=[1.5, 6.0])
S("L06", mv(((0.9, 0.3, 1.45), (1.0, 6.5, 1.4)), ((0.9, 1.6, 1.45), (1.0, 7.5, 1.4)), 30), 2,
  note="a wide from behind, the two of us walking up to the maze")
# L07 the fair packing up
put("tasha", "L07", [0.4, 6.6], yaw=180)
hide("tasha", "L07")
hide("me", "L07")
S("L07", mv(((-1.8, -2.8, 1.7), (-6.5, 8.0, 1.9)), ((-1.8, -2.8, 1.7), (-5.5, 8.0, 1.9)), 20), 2,
  note="the fair packing up: rides under tarps, the flatbed, the dark big wheel far back")
S("L08", one((1.0, 0.0, 0.4), (0.7, 6.0, 0.5), 26), 2, note="pouring: the puddle across the boards")
S("L08.2", one((-5.5, 1.0, 1.4), (-9.5, 5.0, 1.8), 22), 2, note="half the rides under tarps")
S("L09", one((3.0, 3.8, 1.3), (3.0, 12.0, 3.6), 22), 4, note="the maze front, its bulbs burning steady")
S("L09.3", one((5.0, 10.4, 1.5), (1.0, -16.0, 1.4), 28), 4, look={"van": [[0.7, -14.6, 2.0], [0.7, -13.5, 1.0], 40]},
  note="looking back down the field: the fry van's warm square far off")
GUY_RIM = {"rim": [[8.5, 6.5, 8.0], [3.6, 13.2, 6.3], 3000, 22], "rim2": [[-2.0, 7.0, 8.0], [3.6, 13.2, 6.3], 1500, 22]}
# L10 the maze guy up at the roofline
put("guy", "L10", [3.6, 13.2, 5.45], yaw=180, expr="neutral", arms=[40, 40])
raw("guy", "L10+0.5", arms=[10, 10], blend=0.5)
raw("guy", "L10+1.0", arms=[45, 45], blend=0.5)
raw("guy", "L10+1.6", arms=[10, 10], blend=0.5)
raw("guy", "L10+2.2", arms=[45, 45], blend=0.5)
S("L10", one((6.0, 5.4, 1.2), (3.6, 13.0, 6.9), 24), 2, look=GUY_RIM, note="the maze guy at the roofline, his back to us")
S("L11", one((2.0, 7.2, 1.2), (3.6, 13.0, 6.9), 32), 2, look=GUY_RIM, note="his back")
raw("guy", "L11>", arms=[0, 0])

# =========================================================================================== 02 the maze, L12 to L23
# L12 up the steps under the bulbs (outside), then in
put("tasha", "L12", [2.7, 7.4, 0.05], yaw=180, expr="smirk")
put("me", "L12", [3.4, 7.2, 0.05], yaw=180, expr="neutral")
hide("guy", "L12")
raw("tasha", "L12.2", pos=[2.8, 10.0, 1.1])
raw("me", "L12.2", pos=[3.3, 9.9, 1.1])
raw("tasha", "L12>", pos=[2.8, 11.5, 1.1])
raw("me", "L12>", pos=[3.3, 11.4, 1.1])
S("L12", mv(((3.0, 5.2, 1.5), (3.0, 9.0, 1.9)), ((3.0, 6.6, 1.5), (3.0, 11.5, 1.9)), 24), 2,
  note="up the steps under the bulbs")
# inside (x = 60). The corridor runs +y, 1.5 m wide. Tasha and I walk it; the cells beside it hold our reflections
cues = []
cues += [{"at": 0, "name": "props", "roll": True, "trip": 1, "coins": 0, "end1": True, "carry": False}]
cues += [{"at": "L13", "name": "ghosts", "me": "on", "ta": "tasha"}]
IN = 60.0
put("tasha", "L13", [IN + 0.35, 2.6], yaw=180, expr="neutral", arms=[0, 0])
put("me", "L13", [IN - 0.35, 2.2], yaw=180, expr="worried")
raw("tasha", "L13>", pos=[IN + 0.35, 4.2])
raw("me", "L13>", pos=[IN - 0.35, 3.9])
LOOK_IN = {"camfill": 0.3, "maze": 0, "inside": 0, "wash": 0, "amb": 0.35, "room": 1.0, "roomb": 1.0}
S("L13", mv(((IN, -1.6, 1.35), (IN, 8.0, 1.45)), ((IN, -1.0, 1.35), (IN, 8.5, 1.45)), 24), 2, look=LOOK_IN,
  note="the glass grid with both of us repeated down every pane", rain=False)
put("tasha", "L14", [IN + 0.3, 4.2], yaw=180, expr="smirk", head=[0, 0])
put("me", "L14", [IN - 0.4, 3.6], yaw=180, expr="neutral")
raw("tasha", "L14.1", yaw=180, pos=[IN + 0.3, 5.6], blend=0.4)
mouth("tasha", "L14.1", "L14>", 0.1, 0.8)
S("L14", one((IN - 0.55, 2.4, 1.5), (IN + 0.3, 4.2, 1.55), 30), 2, look=LOOK_IN,
  note="her smirk side-on, already turning away down a corridor", rain=False)
raw("tasha", "L15", pos=[IN + 0.3, 6.6])
raw("tasha", "L15>", pos=[IN + 0.3, 8.4])
S("L15", one((IN - 0.1, 0.5, 1.4), (IN + 0.2, 9.0, 1.45), 26), 2, look=LOOK_IN, note="we split up", rain=False)
# she's at the back, standing still (the plant): her spot for the whole film
SPOT = [IN, 13.5]
put("tasha", "L16", SPOT, yaw=0, expr="neutral", arms=[0, 0])
put("me", "L16", [IN, 2.0], yaw=180, expr="neutral")
raw("me", "L16+0.2", pos=[IN, 3.6])
raw("me", "L17", pos=[IN, 4.8], arms=[0, 40], head=[30, 0])
raw("me", "L17.2", head=[-30, 0], arms=[40, 0], blend=0.4)
raw("me", "L18", pos=[IN, 4.8], head=[0, 0], arms=[0, 0])
cues += [{"at": "L16", "name": "ghosts", "me": "on", "ta": "copy", "dy": 6.0}]
S("L16", mv(((IN + 0.3, 0.2, 1.4), (IN, 9.0, 1.45)), ((IN + 0.3, 1.2, 1.4), (IN, 9.5, 1.45)), 26), 2,
  look=LOOK_IN, note="a slow track past the panes: Tasha after Tasha, all moving", rain=False)
S("L17", one((IN - 0.3, 0.8, 1.5), (IN + 0.3, 9.0, 1.45), 30), 2, look=LOOK_IN, note="every one of them moving", rain=False)
S("L18", one((IN - 0.1, 5.0, 1.45), (IN, 13.5, 1.4), 55), 2, look=LOOK_IN,
  note="far down the glass one Tasha stands still while the rest move", rain=False)
cues.append({"at": "L19", "name": "ghosts", "me": "off", "ta": "copy", "dy": 6.0})
S("L19", one((IN + 0.5, 2.3, 1.55), (IN, 4.8, 1.6), 40), 2, look=LOOK_IN, note="me, I figured it was the angles",
  rain=False)
# L20 out of the exit into the rain, alone for a beat
hide_all("L20", "tasha")
cues += [{"at": "L20", "name": "ghosts", "me": "off", "ta": "off"}]
put("me", "L20", [3.0, 12.6, 1.05], yaw=0, expr="smirk")
raw("me", "L20+0.9", pos=[3.6, 10.9, 1.05])
S("L20", one((5.2, 6.2, 1.25), (3.2, 11.4, 1.5), 22), 2, note="me out of the exit into the rain, alone")
# L21 the copy steps out. From here until L78 every Tasha outside the glass is the copy
put("copy", "L21", [3.0, 12.7, 1.05], yaw=0, expr="neutral")
raw("copy", "L21+0.1", pos=[3.0, 11.1, 1.05])
put("me", "L21", [3.8, 10.9, 1.05], yaw=-30, expr="smirk", head=[0, 0])
S("L21", one((5.2, 6.2, 1.25), (3.2, 11.4, 1.5), 22), 2, note="then Tasha came out")
# L22: the same angle as the open, mirrored across the arch's centre line: the fringe the other way
put("copy", "L22", [6.0 - TASHA_A[0], TASHA_A[1]], yaw=-90, expr="smirk", head=[-45, 0], arms=[0, 82])
put("me", "L22", [6.0 - ME_A[0], ME_A[1]], yaw=90, expr="neutral", head=[40, 0])
S("L22", one(*CAM_OPEN), 2, note="the exit framing: the same angle as L01, her fringe swept the other way")
put("me", "L23", [4.2, 9.6], yaw=-20, expr="worried", head=[0, -25])
put("copy", "L23", [5.6, 9.2], yaw=60, expr="neutral")
S("L23", one((2.6, 8.0, 1.5), (4.2, 9.6, 1.65), 55), 2, note="I figured it was the wind")

# =========================================================================================== 03 walking out, L24 to L35
# I walk the boards at x = 0.2; the copy is my reflection across the plane x = 1.0 (1.8 m from me), half a beat late
MIR = 1.0
X0 = 0.2
cues += [{"at": "L24", "name": "props", "roll": False, "trip": 1, "coins": 0, "end1": True, "carry": False}]
hide("guy", "L24")
mput("L24", [X0, 5.0], yaw=0, expr="worried")
m("L28-0.1", [X0, -3.0])
m("L28", [X0, -3.0], yaw=0)
m("L28.1", yaw=90, head=[0, 0], blend=0.2)       # I turn to her (face +x)
m("L30", yaw=90)
m("L31.2", arms=[0, 150], expr="smirk", blend=0.3)     # I point at my hat (right arm, up)
m("L32", arms=[0, 0], blend=0.4)
mouth("me", "L31.3", "L31>", 0.1, 0.8)
cmouth("L31.3", "L31>")
acting["copy"].append({"from": fmt("L33.1"), "to": fmt("L33>"), "mouth": [0.0, 0.8], "flap": True})
m("L35", pos=[X0, -3.0], yaw=0, arms=[0, 0], blend=0.4)
m("L35>-0.5", pos=[X0, -4.0])
FOL = "me"
S("L24", one((3.0, 4.4, 1.4), (0.9, -0.5, 1.1), 26), 2, follow="me", note="side-on walk across the duckboards, the van far off")
S("L25", one((2.6, 3.8, 0.6), (0.9, -0.5, 0.8), 20), 2, follow="me", note="two-shot wide, our legs out of step")
S("L26", one((3.0, 3.6, 1.3), (0.9, -0.5, 1.1), 24), 2, follow="me", note="always on the side with the puddles")
S("L27", one((1.5, -1.6, 0.22), (0.7, 0.0, 0.12), 24), 2, follow="me", note="low along a puddle: my boot splashes, hers makes no sound")
S("L28", one((0.8, -4.2, 1.4), (0.8, 0.0, 1.4), 26), 2, follow="me", note="I stop and turn to her")
S("L29", one((-2.2, -1.8, 1.5), (1.8, 0.0, 1.5), 24), 2, follow="me", note="mid shot, side-lit: she stops and turns to me, late")
S("L30", one((0.8, -4.2, 1.4), (0.8, 0.0, 1.4), 26), 2, follow="me", note="so I tried her own trick on her")
S("L31", one((0.0, -3.0, 1.5), (0.1, 0.0, 1.55), 22), 2, follow="me", note="me pointing at my hat")
S("L32", one((1.6, -3.0, 1.5), (1.6, 0.0, 1.55), 22), 2, follow="me", note="she points at her own head, mirror-handed, late")
S("L33", one((1.7, 2.5, 1.55), (1.6, 0.0, 1.55), 30), 2, follow="me", note="her mouth makes the words, no sound")
S("L34", one((0.8, -4.2, 1.4), (0.8, 0.0, 1.4), 26), 2, follow="me", note="normally she'd laugh at me")
S("L35", one((3.0, 4.4, 1.4), (0.9, -0.5, 1.1), 26), 2, follow="me", note="I kept walking")

# =========================================================================================== 04 the truck, L36 to L43
# Walking +y by the cab; at "ducked" I step round behind it. The copy walks on the boards and freezes mid-step
MIR = None
put("me", "L36", [X0, 6.2], yaw=180, expr="worried")
raw("me", "L36.2", pos=[X0, 8.4])
raw("me", "L36.2+0.9", pos=[-1.5, 9.5], bow=0)
raw("me", "L36.3", bow=38, blend=0.35)
put("copy", "L36", [1.8, 6.2], yaw=180, expr="worried")
raw("copy", lag("L36.2"), pos=[1.8, 7.7])
raw("copy", ("L36.2", 1.0), pos=[1.8, 7.9], stride=24, blend=0.1)
raw("copy", "L37.1", stride=24)
S("L36", one((3.6, 3.4, 1.4), (-0.6, 7.2, 1.2), 24), 2, note="a gust: I duck behind the truck")
put("me", "L37", [-1.5, 9.5], yaw=160, expr="scared", bow=38, head=[0, 0])
raw("me", "L37", bow=38)
raw("me", "L37+0.7", bow=0, blend=0.5)
S("L37", one((-1.4, 9.2, 1.55), (1.8, 7.9, 1.15), 30), 2, note="when I stood up she was frozen")
S("L38", one((3.6, 6.0, 0.7), (1.8, 7.9, 0.8), 30), 2, note="mid-step, one foot in the air")
S("L39", one((3.6, 9.2, 1.4), (1.8, 7.9, 1.35), 36), 2, note="rain running off her coat")
raw("copy", "L40", stride=0, blend=0.15)
S("L40", one((0.3, 5.9, 1.3), (1.8, 7.9, 1.0), 34), 2, note="her foot comes down fast; the dip itself is never shown")
S("L40.1", one((0.6, 7.6, 1.5), (-1.5, 9.5, 1.55), 26), 2, note="my face: the narrator seeing it")
put("me", "L42", [X0, 2.4], yaw=0, expr="worried")
MIR = 1.0
put("copy", "L42", refl([X0, 2.4], MIR), yaw=0, expr="worried")
m("L42>", pos=[X0, 0.6])
S("L42", one((3.0, 4.4, 1.4), (0.9, -0.5, 1.1), 26), 2, follow="me", note="side-on walk again, the lag back")
S("L43", one((0.2, -2.6, 1.55), (0.2, 0.0, 1.6), 28), 2, follow="me", note="I didn't say a word")

# =========================================================================================== 05 the bumper cars, L44 to L59
MIR = None
COPY_AT = [1.0, 4.3]
HIDE_AT = [5.2, 3.6]
ME_FACE = [1.29, 2.83]
FROZEN = {"arms": [100, 6], "side": [-6, 0], "head": [0, 0], "expr": "blank", "blink": False}
put("me", "L44", [3.0, 3.4], yaw=90, expr="worried")
raw("me", "L44.2", pos=HIDE_AT, arms=[0, 70], yaw=90, blend=0.3)
raw("me", "L44>", arms=[0, 0])
put("copy", "L44", COPY_AT, yaw=33, **{"arms": [0, 0], "expr": "blank", "head": [0, 0], "blink": True})
raw("copy", lag("L44.2"), arms=[100, 6], blend=0.4)
raw("copy", lag("L44.2", 0.5), blink=False)
S("L44", one((3.0, 1.0, 1.4), (4.2, 3.6, 1.4), 30), 2, note="I push the tarp up with the back of one hand and slip behind")
put("me", "L45", HIDE_AT, yaw=0, expr="scared", tremble=6, head=[0, 0])
S("L45", one((7.4, 1.6, 1.4), (5.2, 3.6, 1.5), 26), 2, note="behind the tarp, shaking")
put("me", "L46", HIDE_AT, yaw=0, expr="scared", arms=[118, 118], tremble=3)
for i, ref in enumerate(("L46.3", "L46.3+0.5", "L46.3+1.0")):
    raw("me", ref, lean=6, blend=0.35)
    raw("me", (ref, 0.35), lean=-1, blend=0.35)
S("L46", one((5.2, 0.6, 1.6), (5.2, 3.6, 1.62), 28), 2, note="my hands over my face, three breaths (close, the hands at the sleeve ends)")
S("L47", one((-0.9, 1.4, 1.15), (1.0, 4.3, 1.1), 30), 2,
  look="SCARE_WIDE", note="her out on the open ground, frozen with one hand half up, lit from below by the worklight")
put("copy", "L47", COPY_AT, yaw=33, **FROZEN)
put("me", "L48", HIDE_AT, yaw=-90, expr="scared", arms=[62, 6])
raw("me", "L48>", pos=[4.4, 1.6])
raw("me", "L49>", pos=[2.4, 1.6])
raw("me", "L50>", pos=ME_FACE, yaw=150)
S("L48", one((6.3, 1.6, 1.4), (4.6, 2.8, 1.4), 32), 2, note="then I stepped out")
S("L49", one((2.8, 1.2, 1.45), (1.0, 4.3, 1.2), 34), 2, look="SCARE_WIDE", note="she was right where I'd left her")
S("L50", one((-1.8, 2.4, 1.3), (1.0, 4.3, 1.35), 34), 2, look="SCARE_WIDE", note="in the rain, one hand half up")
# P01: the replay, the brief's fallback: frozen, the hand comes down, one short step along the glass, the head comes round
put("me", "L51", ME_FACE, yaw=150, expr="wide", arms=[62, 6], side=[-6, 0], head=[0, 0])
CAM_P01 = ((-2.19, 2.23, 1.4), (1.0, 4.3, 1.1), 24)
S("L51", one(*CAM_P01), 2, look="SCARE_WIDE", note="then she saw me")
STEP_TO = [1.2, 4.34]
raw("copy", "P01", blink=False)
raw("copy", "P01+0.4", arms=[62, 6], blend=0.65)
raw("copy", "P01+1.05", pos=COPY_AT, keep_yaw=True)
raw("copy", "P01+1.35", pos=STEP_TO)
raw("copy", "P01+1.35", head=[75, 8], blend=0.45)
S("P01", one(*CAM_P01), 1, look="SCARE_WIDE", note="the replay, silent: the hand comes down, one short step, the head comes round")
S("P02", one((-0.34, 2.81, 1.45), (1.0, 4.3, 1.41), 40), 1, look="SCARE_FACE", dof=[2.0, 1.0],
  note="the stop: her face, lit from below, 72% of the frame width")
put("copy", "L52", [1.2, 4.34], yaw=33, **{"arms": [62, 6], "side": [-6, 0], "head": [75, 8], "expr": "blank", "blink": False})
S("L52", one((-0.34, 2.81, 1.45), (1.0, 4.3, 1.41), 40), 1, look="SCARE_FACE", dof=[2.0, 1.0], note="her face, still")
put("me", "L52.3", ME_FACE, yaw=150, expr="wide", arms=[62, 6], side=[-6, 0])
S("L52.3", one((2.15, 4.15, 1.55), (1.29, 2.83, 1.55), 46), 2, look="SCARE_ME", note="my wide face")
S("L53", one((-2.0, 2.0, 1.4), (1.1, 4.3, 1.2), 26), 2, look="SCARE_WIDE", note="and she stopped, facing me, in my pose")
S("L54", mv(((-0.34, 2.81, 1.45), (1.0, 4.3, 1.41)), ((-0.1, 3.0, 1.45), (1.0, 4.3, 1.41)), 40, 44), 1,
  look="SCARE_FACE", dof=[2.0, 1.0], note="her eyes were black, like a window at night")
S("L55", mv(((-0.1, 3.0, 1.45), (1.0, 4.3, 1.41)), ((0.1, 3.2, 1.45), (1.0, 4.3, 1.41)), 44, 48), 1,
  look="SCARE_FACE", dof=[1.9, 1.0], note="no shine at all")
S("L56", one((2.15, 4.15, 1.55), (1.29, 2.83, 1.55), 50), 2, look="SCARE_ME", note="that's what a reflection does")
S("L57", mv(((-1.4, 1.9, 1.5), (1.0, 4.3, 1.35)), ((-0.9, 2.4, 1.5), (1.0, 4.3, 1.35)), 30, 36), 2, look="SCARE_WIDE",
  note="it can't move if it can't see you")
S("L58", mv(((-0.34, 2.81, 1.45), (1.0, 4.3, 1.41)), ((-0.1, 3.0, 1.45), (1.0, 4.3, 1.41)), 40, 46), 1, look="SCARE_FACE",
  dof=[2.0, 1.0], note="it came out of the glass")
S("L59", one((2.15, 4.15, 1.55), (1.29, 2.83, 1.55), 56), 2, look="SCARE_ME", note="Tasha was still in there")

# =========================================================================================== 06 back in, L60 to L82
# L60 and L61 running back across the field with it at my glass side, half a beat behind
MIR = 1.0
mput("L60", [X0, -3.0], yaw=0, expr="scared")
m("L61", pos=[X0, 7.4])
m("L61>-0.5", pos=[X0, 9.4])
S("L60", one((0.9, -6.0, 1.5), (0.4, 2.0, 1.4), 28), 2, follow="me", note="running back across the field, the maze lit ahead")
S("L61", one((3.6, -4.6, 1.4), (0.9, 0.6, 1.2), 26), 2, follow="me", note="it ran with me, half a beat behind")
# inside again, the roof off, half the panes out, rain through the open grid
MIR = None
hide("copy", "L62")
cues += [{"at": "L62", "name": "props", "roll": False, "trip": 2, "coins": 0, "end1": True, "carry": False},
         {"at": "L62", "name": "ghosts", "me": "off", "ta": "off"}]
put("me", "L62", [IN, 2.4], yaw=180, expr="scared")
hide("tasha", "L62")
LOOK_IN2 = {"camfill": 0.3, "maze": 0, "inside": 0, "wash": 0, "amb": 0.5, "room": 1.1, "roomb": 1.1}
S("L62", mv(((IN, 1.0, 1.0), (IN, 3.5, 3.4)), ((IN, 1.4, 1.0), (IN, 4.5, 3.9)), 20), 2, look=LOOK_IN2,
  note="the roof off, rain coming straight in through the open grid")
cues += [{"at": "L63", "name": "ghosts", "me": "off", "ta": "copy", "dy": 4.0}]
raw("me", "L63", head=[40, 0], arms=[0, 40])
raw("me", "L63.2", head=[-40, 0], arms=[40, 0], blend=0.4)
raw("me", "L63>-0.3", head=[0, 0], arms=[0, 0], blend=0.4)
S("L63", one((IN - 0.2, -1.5, 1.4), (IN + 0.1, 9.5, 1.45), 24), 2, look=LOOK_IN2,
  note="a wide of panes, every one her, each copying me half a beat late")
S("L64", one((IN + 0.5, -0.3, 1.5), (IN - 0.3, 2.4, 1.55), 26), 2, look=LOOK_IN2, note="none of them showed me")
# L65 I hide behind the stacked frame; every Tasha stops
put("me", "L65", [IN + 0.5, 5.2], yaw=180, expr="scared")
raw("me", "L65.2", pos=[IN + 0.45, 6.9])
cues += [{"at": "L63", "name": "ghosts", "me": "off", "ta": "copy", "dy": 4.0, "hide": "L65.2+0.2", "until": "L69-0.395"}]
S("L65", one((IN - 0.35, 1.6, 1.5), (IN + 0.2, 6.3, 1.4), 26), 2, look=LOOK_IN2, note="behind a stacked steel frame, where nothing could see me")
raw("me", "L66", pos=[IN + 0.45, 6.5], yaw=180)
S("L66", one((IN - 0.35, 2.8, 1.5), (IN, 10.0, 1.45), 26), 2, look=LOOK_IN2, note="the frozen gallery")
S("L67", one((IN - 0.3, 2.6, 1.5), (IN, 11.0, 1.45), 24), 2, look=LOOK_IN2, note="for half a beat nothing moved")
# L68 the real Tasha far down the glass, waving both arms
put("tasha", "L68.2", SPOT, yaw=0, expr="worried", arms=[0, 0])
for i, r in enumerate(("L68.2+0.3", "L68.2+0.9", "L68.2+1.5")):
    raw("tasha", r, arms=[150, 150] if i % 2 == 0 else [110, 110], blend=0.25)
S("L68", one((IN - 0.35, 3.0, 1.5), (IN, 11.0, 1.45), 24), 2, look=LOOK_IN2, note="every Tasha frozen")
S("L68.2", one((IN - 0.2, 7.0, 1.6), (IN, 13.5, 1.4), 46), 2, look=LOOK_IN2,
  note="the real Tasha far down the glass, waving both arms, everything else still")
raw("tasha", "L69", arms=[0, 0], blend=0.4)
S("L69", one((IN - 0.2, 7.0, 1.6), (IN, 13.5, 1.4), 46), 2, look=LOOK_IN2, note="in the same spot as before")
# L70 I've run down the glass to her pane; it stands between us
cues += [{"at": "L70", "name": "ghosts", "me": "off", "ta": "off"}]
put("me", "L70", [IN + 0.35, 10.4], yaw=180, expr="wide")
put("copy", "L70", [IN - 0.4, 12.0], yaw=0, expr="neutral", **{"head": [0, 0], "arms": [0, 0], "blink": True})
put("tasha", "L70", SPOT, yaw=0, expr="wide", arms=[0, 0])
raw("tasha", "L70.2", arms=[0, 82], expr="grin", blend=0.2)
mouth("tasha", "L70.3", "L70>", 0.1, 0.8)
S("L70", one((IN + 0.9, 7.6, 1.5), (IN + 0.1, 13.5, 1.55), 22), 2, look=LOOK_IN2, note="her face goes wide, then she points at my hat")
S("L71", one((IN + 0.7, 10.6, 1.5), (IN, 13.5, 1.55), 36), 2, look=LOOK_IN2, note="a reflection can't go first")
raw("me", "L72", arms=[0, 150], expr="smirk", blend=0.3)
mouth("me", "L72.1", "L72.1>", 0.1, 0.8)
raw("me", "L72.2", arms=[0, 0], blend=0.4)
S("L72", one((IN + 0.9, 11.8, 1.6), (IN + 0.35, 10.4, 1.62), 34), 2, look=LOOK_IN2, note="PICKLE, on purpose")
raw("tasha", "L73", arms=[85, 85], expr="grin", blend=0.2)
mouth("tasha", "L73.1" if False else "L73", "L73>", 0.2, 0.9)
S("L73", one((IN + 0.6, 10.8, 1.5), (IN, 13.5, 1.55), 36), 2, look=LOOK_IN2, note="her FRIES yell through the glass, a mouth flap, her grin")
raw("tasha", "L74", arms=[0, 0], expr="grin", blend=0.3)
S("L74", one((IN + 0.55, 10.8, 1.5), (IN, 13.5, 1.55), 36), 2, look=LOOK_IN2, note="she's still Tasha, and she's still winning")
S("L75", one((IN + 0.5, 6.4, 1.6), (IN - 0.1, 12.4, 1.45), 30), 2, look=LOOK_IN2,
  note="a wide where the plane between us is easy to read: me, then it facing me, then her pane right behind")
raw("me", "L75>", pos=[IN + 0.35, 10.4], keep_yaw=True)
raw("copy", "L75>", pos=[IN - 0.4, 12.0], keep_yaw=True)
raw("me", "L76+0.5", pos=[IN + 0.45, 9.3])
raw("copy", lag("L76+0.5"), pos=[IN - 0.4, 12.9])
S("L76", one((IN + 0.5, 6.4, 1.6), (IN - 0.1, 12.4, 1.45), 30), 2, look=LOOK_IN2, note="so I stepped back")
S("L77", one((IN + 0.5, 6.4, 1.6), (IN - 0.1, 12.4, 1.45), 30), 2, look=LOOK_IN2, note="it stepped back too, half a beat late")
cues += [{"at": "L78", "name": "props", "roll": False, "trip": 2, "coins": 0, "end1": False, "carry": False, "wet": True}]
put("tasha", "L78", SPOT, yaw=0, expr="grin", arms=[0, 0])
raw("tasha", "L78>", pos=[IN - 0.05, 11.0])
hide("copy", "L78")
S("L78", mv(((IN - 0.45, 7.4, 1.5), (IN, 12.5, 1.4)), ((IN - 0.45, 7.8, 1.5), (IN, 12.2, 1.4)), 30), 2, look=LOOK_IN2,
  note="Tasha stepping out of that same pane, soaked and grinning")
S("L79", one((IN + 0.5, 9.9, 1.62), (IN - 0.05, 11.0, 1.6), 30), 2, look=LOOK_IN2, note="the eye close-up: her shine is back")
put("me", "L80", [IN + 0.35, 10.2], yaw=0, expr="grin")
put("tasha", "L80", [IN - 0.8, 10.9], yaw=0, expr="grin")
raw("tasha", "L80+0.7", pos=[IN - 0.3, 10.3])
put("copy", "L80", [IN, 14.5], yaw=0, expr="blank", **{"blink": False})
S("L80", one((IN + 0.6, 6.6, 1.5), (IN - 0.1, 11.6, 1.45), 30), 2, look=LOOK_IN2,
  note="the one touch: she bumps my shoulder; in the pane behind her the copy stands in my pose, late")
# L81 and L82: the maze guy carries that pane to the truck, his back to us
cues += [{"at": "L81", "name": "props", "roll": False, "trip": 1, "coins": 0, "end1": True, "carry": True,
          "off": [1.0, 0.6], "yaw": 90},
         {"at": "L82", "name": "copyattach", "on": True, "off": [0.0, -0.45], "yaw": 0}]
hide_all("L81", "me", "tasha")
put("guy", "L81", [2.0, 9.6], yaw=-90, expr="neutral")
raw("guy", "L82>", pos=[-2.0, 9.7])
raw("guy", "P03>", pos=[-3.6, 9.7])
put("copy", "L82", [0.0, 0.0], yaw=0, expr="blank", **{"head": [0, 0], "arms": [0, 0], "blink": False})
raw("copy", "L82+0.6", head=[40, 0], blend=0.5)
raw("copy", "L82.3", head=[0, 0], blend=0.5)
S("L81", one((7.8, 8.3, 1.4), (1.5, 9.6, 1.25), 30), 2, note="the maze guy carries that pane to the truck, his back to us")
S("L82", one((4.2, 8.7, 1.4), (-0.5, 9.7, 1.3), 34), 2, note="in the glass it watched us go, late, like always")
cues += [{"at": "P03", "name": "fade", "dur": 1.6}]
hide("copy", "P03+0.7")
S("P03", one((3.0, 2.0, 1.4), (3.0, 12.0, 3.2), 22), 4, note="the maze's bulbs go off in one slow fade")

# =========================================================================================== 07 the fry van, L83 to L88
cues += [{"at": "L83", "name": "props", "roll": False, "trip": 1, "coins": 4, "end1": True, "carry": False},
         {"at": "L83", "name": "fade", "dur": 0.01, "reset": True}]
hide_all("L83", "guy", "copy")
VANX = 0.7
put("me", "L83", [1.0, -12.9], yaw=0, expr="smirk", head=[0, 0])
put("tasha", "L83", [2.0, -12.9], yaw=0, expr="smirk", head=[0, 0], arms=[0, 0])
LOOK_VAN = {"van": [(VANX, -14.1, 2.2), (VANX + 0.4, -13.2, 1.0), 110, 1.8, "#ffb060"], "camfill": 0.4, "amb": 0.5, "wash": 0, "maze": 0,
            "inside": 0}
S("L83", one((-0.9, -14.2, 1.55), (1.5, -12.6, 1.4), 30), 2, look=LOOK_VAN, note="the warm turn: a side-by-side two-shot under the amber strip, coins already on the counter")
S("L84", one((-0.6, -14.0, 1.55), (1.5, -12.6, 1.45), 34), 2, look=LOOK_VAN, note="before she even pointed")
raw("me", "L85", head=[0, -38], blend=0.5)
raw("tasha", "L85", head=[0, -38], blend=0.5)
raw("me", "L86.3", head=[0, 0], blend=0.5)
raw("tasha", "L86.3", head=[0, 0], blend=0.5)
S("L85", one((0.9, -14.35, 1.3), (1.5, -12.6, 1.8), 30), 2, look=LOOK_VAN, note="we both looked up at the rain")
S("L86", one((4.6, -11.8, 1.35), (2.4, -14.9, 1.35), 24), 2, look=LOOK_VAN,
  note="the van's polished steel side: our two reflections look up at the rain with us, on time")
raw("tasha", "L87", expr="grin")
raw("me", "L87", expr="grin")
S("L87", one((1.2, -14.3, 1.5), (1.5, -12.6, 1.55), 24), 2, look=LOOK_VAN, note="and nobody was late")
# L88: the last shot is L01's framing: she points at my hat, and the film cuts back to it
put("tasha", "L88", [0.4, -13.2], yaw=90, expr="smirk", head=[-45, 0], arms=[0, 0])
put("me", "L88", [1.6, -13.2], yaw=-90, expr="neutral", head=[40, 0])
raw("tasha", "L88.3", arms=[0, 82], blend=0.45)
S("L88", one((1.0, -9.7, 1.38), (1.0, -13.2, 1.5), 34), 2, look=LOOK_VAN, note="at the fry van she pointed at my hat: L01's framing, so the loop is the joke starting again")

# ---------------------------------------------------------------------------------------------------- looks
# The scare's lights, from the creature test (designer-notes: p2i), in each shot's own terms. A light a shot doesn't name
# is off. face and hair are shadowless and reach only the heads.
SCARE_FACE = {"exposure": 0.0, "camfill": 0.0, "face": [[0.819, 4.099, 1.22], [1.0, 4.3, 1.45], 3.6, 0.3], "hair": [[0.656, 3.843, 0.9], [1.0, 4.3, 1.45], 4.5],
              "rim": [[2.977, 4.673, 2.0], [1.0, 4.3, 1.6], 1700, 9], "rim2": [[1.469, 6.3, 2.1], [1.0, 4.3, 1.6], 900, 16],
              "bounce": [[0.481, 4.337, 0.07], [1.0, 4.3, 1.0], 6], "work": [[2.05, 3.45, 0.77], [1.3, 4.05, 1.0], 300, 45],
              "wash": 0.5, "inside": 0.6, "bulbs": 0.06, "amb": 0.0}
SCARE_WIDE = {"exposure": 0.0, "camfill": 0.0, "face": [[0.82, 4.1, 1.2], [1.0, 4.3, 1.4], 3.6, 0.3], "hair": [[0.656, 3.843, 0.9], [1.0, 4.3, 1.45], 4.5],
              "rim": [[2.977, 4.673, 2.0], [1.0, 4.3, 1.6], 1700, 9], "rim2": [[1.469, 6.3, 2.1], [1.0, 4.3, 1.6], 900, 16],
              "bounce": [[0.481, 4.337, 0.07], [1.0, 4.3, 1.0], 20], "work": [[2.05, 3.45, 0.77], [1.3, 4.05, 1.0], 300, 45],
              "kick": [[2.6, 2.2, 1.9], [1.29, 2.83, 1.2], 300, 25],
              "wash": 0.5, "inside": 0.6, "bulbs": 0.1, "amb": 0.15}
SCARE_ME = {"exposure": 0.0, "camfill": 0.0, "face": [[1.55, 3.5, 1.2], [1.29, 2.83, 1.55], 1.1, 0.3], "hair": [[1.5, 3.4, 1.1], [1.29, 2.83, 1.6], 4.0],
            "kick": [[2.8, 2.2, 1.9], [1.29, 2.83, 1.4], 420, 25], "rim": [[0.3, 1.2, 2.1], [1.29, 2.83, 1.6], 900, 14],
            "work": [[2.05, 3.45, 0.77], [1.3, 3.2, 1.0], 300, 45], "wash": 0.4, "inside": 0.4, "bulbs": 0.06, "amb": 0.1}
NAMED = {"SCARE_FACE": SCARE_FACE, "SCARE_WIDE": SCARE_WIDE, "SCARE_ME": SCARE_ME}

# ---------------------------------------------------------------------------------------------------- assemble
# the shot list, each shot's id numbered in order; sort the acting by resolved time (a lagged key can land after
# the next scene's cut), keeping the order of keys at the same instant
out_shots, looks, dofs, rain_shots = [], {}, {}, []
for i, d in enumerate(shots):
    sid = f"S{i + 1:02d}"
    sh = {"id": sid, "cam": d["cam"], "step": d["step"], "hand": 0.0 if d["step"] == 4 else (0.006 if d["step"] == 1 else 0.01),
          "note": d["note"]}
    if i:
        sh["at"] = d["at"]
    if d["follow"]:
        sh["follow"] = d["follow"]
    out_shots.append(sh)
    lk = d["look"]
    if isinstance(lk, str):
        lk = NAMED[lk]
    if lk:
        looks[sid] = lk
    if d["dof"]:
        dofs[sid] = d["dof"]
    if d["rain"]:
        rain_shots.append(sid)


def key_t(k):
    return AT(k["from"]) if "from" in k else AT(k["at"])


for who in acting:
    ks = acting[who]
    order = sorted(range(len(ks)), key=lambda j: (round(key_t(ks[j]), 3), j))
    acting[who] = [ks[j] for j in order]
acting = {w: ks for w, ks in acting.items() if ks}

cues.sort(key=lambda c: AT(c["at"]))
# set.py reads the ghosts' freeze window as refs it resolves itself; cue extras are kept as given

story = {
    "slug": "ep15-mirror-maze",
    "title": "Only one of us walked out of the mirror maze",
    "made_for_kids": False,
    "premise": "On the last rainy weekend of a travelling fair, my best friend Tasha and I go into the mirror maze before it comes down, and the friend who walks out half a beat behind me is not the one who walked in.",
    "twist": "The Tasha who came out is only a reflection: it can't move unless it can see me, so it freezes when I hide and copies me late. The real Tasha is still in the glass, and I only find her in the half beat when nothing in the maze can see me.",
    "world": "a travelling fair packing up in the rain at night: duckboards over mud, rides under black tarps, a lilac-bulbed mirror maze trailer, a flatbed truck, bumper cars, a warm fry van far across the field",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffd23a",
    "gap": 0.12,
    "tail": LOOP,
    "look": {"fog": "#1c1826", "fog_density": 0.055, "fog_start": 3.5, "sky": "#120f18", "exposure": 0.7},
    "grade": {"shadows": [0.03, -0.02, 0.07], "highlights": [-0.02, 0.0, 0.03], "saturation": 0.9, "contrast": 1.1,
              "vignette": 0.5, "bloom": 0.35, "grain": 0.012, "red_line": 0.78},
    "rain_shots": rain_shots,
    "rain_gain": 1.2,
    "phonemes": {"Tasha's": "tˈɑʃəz"},
    "cast": cast,
    "lines": lines,
    "shots": out_shots,
    "acting": acting,
    "cues": cues,
    "looks": looks,
    "dof": dofs,
    "light_only": {"face": ["copy.headm", "tasha.headm", "me.headm"], "hair": ["copy.hair*", "tasha.hair*", "me.hair*"]},
    "fx": [],
    "music": {"root": 40, "mode": "dorian", "bpm": 76, "seed": 15,
              "sections": [
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L12", "voices": ["drone", "pad", "piano"], "energy": 0.38},
                  {"at": "L24", "voices": ["drone", "pad", "piano", "pulse"], "energy": 0.5},
                  {"at": "L36", "voices": ["drone", "pad", "piano", "pulse"], "energy": 0.6},
                  {"at": "L44", "voices": ["drone", "pad", "pulse"], "energy": 0.55},
                  {"at": "L51", "voices": ["drone"], "energy": 0.2},
                  {"at": "L56", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L60", "voices": ["drone", "pad", "piano", "pulse"], "energy": 0.7},
                  {"at": "L78", "voices": ["piano", "pad"], "energy": 0.3},
                  {"at": "P03", "voices": ["drone"], "energy": 0.2},
                  {"at": "L83", "voices": ["piano", "pad", "drone"], "energy": 0.5, "mode": "major", "root": 40},
              ]},
    "sound": {"floor": "wood", "steps_db": -20,
              "ambience": [
                  {"kind": "rain", "from": 0, "to": "end", "lufs": -34},
                  {"kind": "wind", "from": "L07", "to": "L12", "lufs": -40},
                  {"kind": "hum", "from": "L12", "to": "L20", "lufs": -42},
                  {"kind": "wind", "from": "L36", "to": "L38", "lufs": -34},
                  {"kind": "drips", "from": "L62", "to": "L82", "lufs": -40},
              ],
              "sfx": [
                  {"at": "L36", "kind": "whoosh", "db": -20},
                  {"at": "P02", "kind": "hit", "db": -6},
                  {"at": "P02", "kind": "sting", "db": -9},
                  {"at": "L59", "kind": "riser", "db": -20, "dur": 1.6},
                  {"at": "L77.2>", "kind": "whoosh", "db": -16},
                  {"at": "L83", "kind": "click", "db": -14},
                  {"at": "P03", "kind": "hum_sweep", "db": -16, "dur": 2.4},
              ],
              "music_drops": [{"from": "L51", "to": "P02>", "keep": ["hit", "sting"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(out_shots)} shots)")
