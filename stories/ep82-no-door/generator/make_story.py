"""Writes ../story.json for "Pizza For The House With No DOOR" (ep82-no-door, batch 7).

Run from anywhere: python stories/ep82-no-door/generator/make_story.py
The words are in lines.json beside this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (ch channels, badge, obj, puff) and the score.

World (metres, z up): the street runs along x. The sidewalk is y -6.2..-3.8, the road y -14..-6.4 (cars heading +x in
the lane at y -12), the doorless house's front wall is at y 0 (x -3..3, body y 0..5), the neighbours' porches are at
y -1.8..0 at x -8.6, -18.6, -28.6, the pizza place at x -40 (window onto a counter), the far lemon house at (150, 60).
Acting yaw: 0 faces -y (toward the street), 180 faces +y, 90 faces +x, -90 faces -x.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True, "ink": "#24131f"}
cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#ff4d2e", "pattern": "solid", "collar": "#fff3dc",
           "pants": "#cdb48a", "shoes": "#ffffff", "sleeves": "short", "hair": "mop", "hair_c": "#1c1418",
           "hat": "ballcap", "hat_c": "#ff4d2e", "face": dict(FACE)},
    "marisol": {"age": "adult", "skin": "#e8b890", "shirt": "#e9b83a", "pattern": "solid", "pants": "#3b5a8c",
                "shoes": "#ffffff", "sleeves": "long", "hair": "bun", "hair_c": "#2a1a1a", "extras": ["apron"],
                "extra_c": "#ffffff", "face": {"eyes": "lashes", "brows": True, "ink": "#24131f"}},
    "n1": {"age": "adult", "skin": "#d9a27a", "shirt": "#c9a8ff", "pattern": "knit", "pants": "#5b6270",
           "shoes": "#3b3b44", "sleeves": "long", "hair": "buzz", "hair_c": "#4a3a30", "face": dict(FACE)},
    "n2": {"age": "adult", "skin": "#c98f66", "shirt": "#ffd21f", "pattern": "solid", "pants": "#6a4a8a",
           "shoes": "#ffffff", "sleeves": "short", "hair": "long", "hair_c": "#6b3a22",
           "face": {"eyes": "lashes", "brows": True, "ink": "#24131f"}},
    "n3": {"age": "adult", "skin": "#e8c4a0", "shirt": "#8de3c4", "pattern": "solid", "pants": "#8a8d96",
           "shoes": "#5a4a3a", "sleeves": "short", "hair": "buzz", "hair_c": "#d6d6d6", "extras": ["glasses"],
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
    """The character is there from this instant (a cut); anything it doesn't set goes back to neutral."""
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": list(pos), "blend": 0, "yaw": yaw, "expr": expr, "hidden": False, **NEUTRAL, **kw})


def go(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": list(pos), **kw})


def gone(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def ch(at, k, v, dur=0.0):
    cues.append({"at": at, "name": "ch", "k": k, "v": v, "dur": dur})


def badge(at, txt, mode="norm"):
    cue(at, "badge", txt=txt, mode=mode)


def obj(at, k, pos=None, on=True, **kw):
    d = {"at": at, "name": "obj", "k": k, "on": on}
    if pos is not None:
        d["pos"] = list(pos)
    d.update(kw)
    cues.append(d)


# ---------------------------------------------------------------------------------------------------- cameras
def V(loc, tgt, lens, loc2=None, tgt2=None, lens2=None):
    ks = [[0, list(loc), list(tgt), lens]]
    if loc2 or tgt2 or lens2:
        ks.append([1, list(loc2 or loc), list(tgt2 or tgt), lens2 or lens])
    return ks


def S(at, cam, note="", hand=0.006, step=2, fill=1.0, exp=0.0, follow=None):
    d = {"id": f"S{len(shots) + 1:02d}", "cam": cam, "step": step, "hand": hand}
    if shots:
        d["at"] = at
    if follow:
        d["follow"] = follow
    if fill != 1.0:
        d["fill"] = fill
    if exp:
        d["exp"] = exp
    if note:
        d["note"] = note
    shots.append(d)
    return d


for k in acting:
    acting[k].append({"at": 0, "pos": [0, 40, 0], "hidden": True, "blend": 0, **NEUTRAL})

SLOT = (-1.5, 0, 0.5)         # the low brass slot, knee height
FRAME1 = V((-1.5, -1.55, 0.78), (-1.5, 0, 0.5), 24, (-1.5, -1.15, 0.7))
PORCH = {"n1": (-8.6, -0.9), "n2": (-18.6, -0.9), "n3": (-28.6, -0.9)}

# the neighbours stand on their porches all film (they stay behind their porch lights)
put("n1", 0.01, PORCH["n1"], 0, "worried")
put("n2", 0.01, PORCH["n2"], 0, "worried")
put("n3", 0.01, PORCH["n3"], 0, "neutral")

# the chimney: a soft puff every four seconds, none in the drop and while it stands
for i in range(8):
    cue(1.5 + 4.0 * i, "puff")
for tt in (61.5, 65.5, 69.5):
    cue(tt, "puff")

# =========================================================================================== 01 the hook, L01-L02
badge(0, "+0:02", "late")
obj(0, "box", (-1.5, -0.04, 0.5))
ch(0, "glow", 0.5)
S(0, FRAME1, "frame 1: the brass slot centred, a pizza box half through, no door anywhere; push in")
put("me", "L02", (-2.2, -2.0), 0, "worried", head=[0, 6])
S("L02", V((-2.2, -4.3, 1.5), (-2.2, -2.0, 1.5), 34, (-2.2, -3.7, 1.5)), "my face beside the late badge")
gone("me", "L03")

# =========================================================================================== 02 the montage L03-L10
obj("L03", "box", on=False)
badge("L03", "5:58")
badge("L03.1", "5:59")
badge("L03.2", "6:00")
put("marisol", "L03", (-40.6, 1.9), 0, "smile", arms=[55, 55], head=[0, 22])
obj("L03", "box", (-40.5, 0.8, 1.07))
S("L03", V((-39.3, -1.8, 1.45), (-40.5, 0.9, 1.15), 28, (-39.6, -1.3, 1.4)), "the counter: Marisol boxes one plain pizza")
gone("marisol", "L04")
obj("L04", "box", on=False)
S("L04", V((7.5, -13.5, 2.4), (0, 0, 2.8), 28, (6.2, -12.0, 2.4)), "the doorless house, wide-ish")
S("L04.1", V((2.5, -4.6, 0.5), (0, 0, 1.0), 26, (2.0, -3.6, 0.55)), "no path, lawn to the wall")
S("L04.2", V((-3.2, -2.4, 0.4), (-1.5, 0, 0.5), 26, (-2.6, -1.5, 0.45)), "just a brass slot")
put("me", "L04.3", (-0.6, -0.9), 180, "neutral")
S("L04.3", V((-3.0, -2.0, 0.55), (-1.3, -0.2, 0.55), 28, (-2.6, -1.6, 0.55)), "at knee height: the slot beside my knee")
gone("me", "L05")
obj("L05", "box", (-1.5, -1.0, 0.5), to=[-1.5, 0.25, 0.5], dur=0.9)
ch("L05+0.2", "flap", 1.0, 0.25)
ch("L05+1.0", "flap", 0.0, 0.3)
obj("L05+1.1", "box", on=False)
S("L05", V((-2.2, -1.6, 0.7), (-1.5, 0, 0.5), 26, (-1.9, -1.2, 0.6)), "you slide the box in")
ch("L05.1", "glow", 1.0, 0.4)
S("L05.1", V((-1.5, -0.9, 0.62), (-1.5, 0, 0.5), 30, (-1.5, -0.6, 0.55)), "the slot is warm")
ch("L05.2", "flap", 0.6, 0.3)
ch("L05.2+0.5", "flap", 0.0, 0.4)
S("L05.2", V((0.0, -3.6, 0.9), (-1.5, 0, 0.5), 32, (-0.8, -2.8, 0.8)), "like breath: the flap lifts a little")
ch("L06", "glow", 0.15, 0.6)
ch("L06", "flap", 1.0, 0.2)
obj("L06", "bill", (-1.5, -0.08, 0.5), to=[-1.5, -0.2, 0.238], dur=0.8)
ch("L06+0.9", "flap", 0.0, 0.3)
S("L06", V((-1.9, -1.3, 0.62), (-1.5, -0.1, 0.4), 30, (-1.7, -0.9, 0.5)), "the flap lifts: a green twenty slides out")
S("L06.1", V((-1.5, -0.9, 0.6), (-1.5, -0.15, 0.25), 32, (-1.5, -0.55, 0.45)), "the money slides back out")
obj("L07", "bill", (-1.5, -0.2, 0.238))
S("L07", V((-1.5, -0.5, 0.8), (-1.5, -0.15, 0.23), 30, (-1.5, -0.4, 0.6)), "a twenty on the tray")
obj("L07.1", "bill", on=False)
obj("L07.1", "tiny", (-1.5, -0.15, 0.23))
S("L07.1", V((-2.0, -0.9, 0.45), (-1.5, -0.15, 0.27), 36, (-1.8, -0.65, 0.38)), "folded into")
S("L07.2", V((-2.1, -1.1, 0.3), (-1.5, -0.15, 0.3), 40, (-2.0, -0.9, 0.32)), "a tiny HOUSE: the quotable line")
obj("L08", "tiny", on=False)
S("L08", V((3.0, -7.0, 1.5), (2.0, 3.0, 7.0), 24, (3.0, -5.5, 2.0)), "its chimney puffs against the pink sky")
S("L08.1", V((-5, -9, 3.0), (1.5, 2, 6.5), 30, (-4, -8, 3.5)), "every four seconds")
S("L08.2", V((10, -15, 2.5), (1, 0, 4.5), 30, (9, -14, 2.5)), "like clockwork: the whole house, a puff over it")
S("L09", V((-3.0, -13.0, 1.6), (-21, 0, 2.2), 20, (-5, -13.0, 1.6), (-20, 0, 2.2)), "three porches in a row, lights on")
S("L09.1", V((-9.4, -4.2, 2.2), (-8.6, -0.6, 2.6), 30, (-9.0, -3.2, 2.3)), "the porch light, a neighbor behind it")
S("L09.2", V((-17.0, -4.5, 1.7), (-18.6, -0.9, 1.8), 30, (-17.6, -3.6, 1.7)), "till it's delivered: a neighbor watching")
put("n2", "L10", (4.8, -4.9), 0, "neutral")
go("n2", "L10.1", (5.3, -8.5))
go("n2", "L11", (5.8, -15.0))
obj("L10", "dog", (4.8, -6.0), to=[5.3, -9.5], dur=0.8, yaw=0)
obj("L10.1", "dog", (5.3, -9.5), to=[5.8, -16.0], dur=0.7, yaw=0)
S("L10", V((-1, -3.6, 1.4), (5.5, -8.5, 0.9), 24, (0, -3.6, 1.4), (6, -9.5, 0.9)), "nobody walks a dog past it: a woman and dog hurry by")
S("L10.1", V((-2, -11.5, 1.3), (5.5, -13, 1.0), 28, (-1, -11.5, 1.3)), "across the road, far sidewalk")
put("n2", "L11", PORCH["n2"], 0, "worried")
obj("L11", "dog", on=False)

# =========================================================================================== 03 the sister L11-L14
put("marisol", "L11", (-39.8, 1.9), 0, "smile")
put("me", "L11", (-41.2, 1.9), 0, "smile")
S("L11", V((-40.4, -2.8, 1.55), (-40.4, 1.6, 1.45), 26, (-40.4, -2.4, 1.5)), "the pizza place: Marisol and me, both smile")
S("L11.1", V((-33, -8, 1.8), (-40, 0, 1.8), 24, (-34, -7, 1.8)), "the pizza place from the street")
S("L11.2", V((-26, -8, 2.2), (-38, 0, 1.8), 22, (-27, -8, 2.0)), "on the corner, the red door and its warm light")
put("marisol", "L12", (-39.6, 1.9), -90, "smile", arms=[0, 70])
put("me", "L12", (-41.2, 1.9), 90, "smile", arms=[0, 0])
obj("L12", "bag", (-40.4, 1.5, 1.35))
S("L12", V((-40.4, -2.4, 1.6), (-40.4, 1.5, 1.4), 26, (-40.4, -1.9, 1.5)), "Marisol hands me the red bag")
put("marisol", "L12.1", (-39.6, 1.9), 0, "smile")
S("L12.1", V((-39.6, -1.2, 1.7), (-39.6, 1.9, 1.62), 38, (-39.6, -0.8, 1.65)), "Marisol, warm: ten years")
obj("L13", "bag", on=False)
gone("marisol", "L13")
gone("me", "L13")
put("me", "L13", (-36.3, -11.55, -0.2), 90, "smile")
go("me", "L14", (-27.3, -11.55, -0.2))
obj("L13", "car", (-36.0, -12.0), to=[-27.0, -12.0], dur=1.25, yaw=90)
S("L13", V((-33, -5.75, 1.4), (-35, -12, 1.1), 26, (-31, -5.75, 1.4), (-30, -12, 1.1)), "the red car pulls out of the lot")
S("L13.1", V((0, 0, 0), (0, 0, 0), 30), "", follow="me")
shots[-1]["cam"] = V((2.4, 1.8, 1.65), (0, 0, 1.55), 30, (1.9, 1.3, 1.6))
shots[-1]["note"] = "she gave it to ME: my smile from the car"
gone("me", "L14")

# =========================================================================================== 04 tonight, the run L14-L18
badge("L14", "5:58")
obj("L14", "car", (-18.0, -12.0), yaw=90, flat=True)
put("me", "L14", (-18.0, -9.5), 0, "worried", arms=[0, 0])
S("L14", V((-14, -6.8, 1.3), (-18, -10.5, 1.0), 28, (-15, -7.2, 1.3)), "tonight: the car stopped, me beside it")
S("L14.1", V((-16.0, -8.4, 0.8), (-16.7, -11.0, 0.3), 30, (-16.2, -9.2, 0.6)), "my tire went flat")
S("L14.2", V((-1.5, -5.0, 1.6), (-19, -11, 0.9), 20, (-3, -5.0, 1.6)), "two blocks away")
badge("L15", "5:59")
obj("L15", "car", on=False)
put("me", "L15", (-14.0, -5.2), 90, "scared", run=True)
go("me", "L18", (-3.2, -4.6))
obj("L15", "bag", follow="me", off=(0.32, -0.05, 0.85), pos=[0, 0, 0])
S("L15", V((2.6, -2.4, 1.1), (0, 0, 1.2), 28, (2.2, -2.0, 1.1)), "so I ran it", hand=0.012, follow="me")
badge("L16", "+0:01", "late")
S("L16", V((1.7, -1.3, 1.6), (0, 0, 1.55), 34, (1.5, -1.1, 1.6)), "six-oh-one", hand=0.012, follow="me")
ch("L17+0.05", "plight0", 0.0, 0.6)
ch("L17+0.30", "plight3", 0.0, 0.6)
ch("L17+0.70", "plight1", 0.0, 0.6)
ch("L17+1.20", "plight2", 0.0, 0.6)
S("L17", V((-1.5, -5.75, 1.6), (-24, 0, 2.4), 22, (-2.5, -5.75, 1.6)), "up and down the street the porch lights go out")
S("L17.1", V((-17.6, -3.2, 2.3), (-18.6, -0.45, 2.7), 30, (-17.9, -2.6, 2.5)), "the porch light, dimming")
S("L17.2", V((-2, -5.8, 1.7), (-26, -0.5, 2.3), 20, (-4, -5.8, 1.7)), "dark porches, the sky still pink")
badge("L18", "+0:02", "late")
obj("L18", "bag", on=False)
put("me", "L18", (-2.2, -3.0), 10, "worried", tremble=3, head=[0, 5])
S("L18", V((-2.0, -6.8, 1.5), (-2.4, -3.2, 1.5), 32, (-2.1, -6.0, 1.5)), "six-oh-two: me, out of breath")

# =========================================================================================== 05 the blink L19-L20
put("me", "L19", (-2.2, -3.0), 180, "scared", head=[0, -8])
S("L19", V((-3.6, -6.5, 1.6), (0, 0, 3.8), 30, (-3.0, -6.0, 1.9)), "the two top windows")
ch("L19.1", "eyes", 0.0, 0.4)
S("L19.1", V((0, -8.5, 3.9), (0, 0, 3.9), 34, (0, -6.5, 3.9)), "went dark")
ch("L19.2", "eyes", 1.0, 0.4)
S("L19.2", V((1.8, -5, 3.9), (1.7, 0, 3.9), 34, (1.7, -4.0, 3.9)), "and lit again")
S("L20", V((0, -6, 3.6), (0, 0, 4.0), 28, (0, -4.6, 3.9)), "like it blinked")
gone("me", "P01")
S("P01", V((4, -16, 2.8), (0, 0, 4.5), 28, (3, -14, 2.8)), "the drop: the house, still")

# =========================================================================================== 06 it stands L21-L27
badge("L21", "+0:03", "late")
put("me", "L21", (-1.2, -3.0), 0, "scared", head=[0, -22], arms=[0, 0])
S("L21", V((-1.0, -9, 1.4), (-1.2, -3.0, 2.6), 30, (-1.0, -7.6, 1.5)), "six-oh-three: me looking up")
ch("L22", "crack", 1.0, 0.8)
S("L22", V((0.5, -4.8, 0.25), (0, -1.0, 0.2), 28, (0.3, -3.5, 0.3)), "the lawn splits")
ch("L23-0.1", "rise", 1.0, 1.5)
S("L23", V((6, -13, 0.45), (0, 0, 3.8), 24, (5, -12, 0.45), (0, 0, 4.5)), "the house rises, the sky pink behind it")
S("L23.1", V((-7, -9.5, 0.5), (0, 0, 5.0), 22, (-6, -9.0, 0.5), (0, 0, 6.0)), "stood up")
gone("me", "L24")
S("L24", V((0, -23, 3.2), (0, 0, 5.0), 30, (0, -21, 3.6)), "the whole house, standing, roof on")
S("L24.1", V((7.0, -13, 1.2), (0, 0, 6.0), 26, (6, -12, 1.4)), "somebody made of the house")
put("me", "L25", (-0.9, -1.2), 180, "scared", head=[0, -18])
S("L25", V((0, -20, 0.8), (0, 0, 6.2), 34, (0, -18.5, 0.9), (0, 0, 6.6)), "the cover frame: me tiny at its feet")
S("L25.1", V((2, -17, 7.5), (0, 0, 9.0), 30, (1.5, -14, 8.0)), "with a roof on")
gone("me", "L26")
S("L26", V((4.5, -7, 1.2), (0.5, 1.2, 2.3), 26, (3.5, -6, 1.5)), "its knees came up")
S("L26.1", V((-1, -5.5, 0.35), (-1.6, 1, 0.8), 26, (-1, -4.5, 0.4)), "out of the lawn")
ch("L27+0.2", "mflap", 1.0, 0.4)
ch("L27+1.0", "mflap", 0.0, 0.4)
S("L27", V((0, -7.5, 6.6), (0, 0, 6.6), 28, (0, -4.4, 6.6)), "the slot was its mouth; the tally on the flap")

# =========================================================================================== 07 it turns L28-L29
S("L28", V((-5, -8, 3.0), (-22, 0, 2.2), 22, (-7, -8, 3.0)), "every porch light was out")
ch("L28.1", "turn", -40.0, 0.01)
S("L28.1", V((8, -17, 3.5), (0, 0, 6.0), 26, (7, -15, 3.8)), "so it turned")
S("L28.2", V((-14, -9, 2.0), (-37, 0, 2.3), 22, (-17, -9, 2.0)), "toward the one door still lit")
put("marisol", "L29", (-39.8, 1.9), 0, "worried", arms=[60, 60])
S("L29", V((-35, -5, 1.6), (-37.5, 0, 2.0), 30, (-35.5, -3.5, 1.7)), "Marisol's door")
S("L29.1", V((-40.0, -3.0, 1.6), (-40.0, 1.8, 1.6), 32, (-40.0, -2.2, 1.6)), "Marisol in the window, worried")
gone("marisol", "L30")

# =========================================================================================== 08 the order L30-L38
put("me", "L30", (-4.5, -5.2), 0, "worried")
obj("L30", "box", follow="me", off=(0, -0.45, 1.0), pos=[0, 0, 0])
obj("L30", "slip", follow="me", off=(0, -0.45, 1.045), pos=[0, 0, 0])
S("L30", V((-4.5, -6.3, 1.9), (-4.5, -5.755, 1.02), 32, (-4.5, -6.1, 1.7)), "the order slip on the lid: a doorless house glyph")
S("L30.1", V((-4.5, -5.9, 1.5), (-4.5, -5.755, 1.03), 44, (-4.5, -5.85, 1.3)), "always says the same thing")
obj("L31", "slip", on=False)
S("L31", V((-4.5, -7.3, 1.6), (-4.5, -5.2, 1.55), 34, (-4.5, -6.6, 1.6)), "the house with no door: my face")
ch("L32", "shift", 1.0, 0.0)
ch("L32", "turn", -40.0, 0.0)
put("me", "L32", (-3.0, -7.0), 90, "scared", run=True)
go("me", "L32.1", (0.0, -0.8))
go("me", "L33", (0.0, 1.4))
S("L32", V((-2.4, -2.2, 0.8), (0, 0.5, 0.9), 26, (-2.0, -1.8, 0.8)), "so I carried the pizza", hand=0.012, follow="me")
S("L32.1", V((6, -9, 1.0), (0, 1, 1.2), 26, (5, -8, 1.0)), "to where the house")
S("L32.2", V((0, -7, 2.0), (0, 2.5, 0.1), 28, (0, -5, 1.6)), "used to be: bare dirt")
put("me", "L33", (0.0, 1.3), 180, "worried", lean=32, arms=[60, 60])
obj("L33", "box", follow="me", off=(0, -0.55, 0.9), pos=[0, 0, 0])
obj("L33+0.5", "box", (0.0, 1.85, 0.9), to=[0.0, 1.85, 0.04], dur=0.5)
S("L33", V((2.5, -1.0, 1.0), (0, 1.8, 0.7), 30, (2.0, -0.2, 1.0)), "I set it down")
obj("L33.1", "box", (0.0, 2.3, 0.04))
gone("me", "L33.1")
S("L33.1", V((0, 1.2, 3.0), (0, 2.0, 0.05), 24, (0, 1.2, 2.6)), "top-down: the box on the bare dirt")
S("L33.2", V((4.0, -2.4, 1.4), (0, 2.5, 0.2), 26, (3.4, -1.9, 1.2)), "right in the middle")
S("L33.3", V((-6, -9, 3.0), (2, 2, 2.5), 24, (-5, -8, 3.0)), "of the lot, the standing house beside it")
S("L34", V((8, -4.5, 0.6), (8, 2.5, 1.2), 26, (8, -3.8, 0.6)), "it stopped: its feet, still")
ch("L35", "turn", -95.0, 0.8)
ch("L35", "bow", 16.0, 0.8)
S("L35", V((0.5, 0.5, 1.2), (8, 2.5, 8.0), 22, (0.5, 0.5, 1.0)), "its window-eyes lowered toward the box")
S("L35.1", V((-3.0, -1.5, 0.7), (1.5, 2.5, 2.5), 24, (-2.5, -1.2, 0.7)), "looked back at the box")
ch("L36", "shift", 0.0, 0.0)
ch("L36", "turn", 0.0, 0.0)
ch("L36", "bow", 0.0, 0.0)
ch("L36", "rise", 0.5, 0.0)
S("L36", V((0, -20, 3.0), (0, 0, 4.5), 28, (0, -18, 3.2)), "across a cut: it's back over its lot")
ch("L36.1", "rise", 0.2, 0.5)
obj("L36.1", "box", on=False)
S("L36.1", V((6, -14, 1.0), (0, 0, 3.5), 26, (5, -13, 1.0)), "and sat down")
S("L36.2", V((-5, -9, 0.6), (0, 1.0, 1.0), 26, (-4, -8, 0.6)), "right on top of it")
badge("L37", "OK", "ok")
ch("L37", "rise", 0.0, 1.2)
ch("L37", "crack", 0.0, 1.2)
S("L37", V((3.5, -5, 0.8), (1.6, 1, 1.0), 26, (3, -4, 0.8)), "its knees sink back under the lawn")
S("L37.1", V((0, -9, 3.8), (0, 0, 3.9), 32, (0, -7.0, 3.9)), "the windows lit")
for tt, i in (("L38+0.05", 0), ("L38+0.35", 3), ("L38+0.65", 1), ("L38+0.95", 2)):
    ch(tt, f"plight{i}", 1.0, 0.6)
S("L38", V((9, -16, 2.4), (0, 0, 3.2), 26, (8, -15, 2.4)), "just a house at sundown")
S("L38.1", V((-3, -6, 1.7), (-20, 0, 2.5), 22, (-5, -6, 1.7)), "porch lights ramp back on")

# =========================================================================================== 09 warm turn L39-L42
ch("L39", "flap", 1.0, 0.2)
ch("L39+0.9", "flap", 0.0, 0.3)
obj("L39", "bill", (-1.5, -0.08, 0.5), to=[-1.5, -0.2, 0.238], dur=0.7)
S("L39", V((-2.0, -1.3, 0.6), (-1.5, -0.1, 0.45), 30, (-1.8, -0.9, 0.55)), "the slot pushes out a twenty")
obj("L39.1", "bill", on=False)
obj("L39.1", "tiny", (-1.5, -0.15, 0.23))
S("L39.1", V((-1.9, -0.8, 0.42), (-1.5, -0.15, 0.27), 36, (-1.75, -0.6, 0.36)), "folded into a tiny house")
obj("L40", "tiny", on=False)
put("marisol", "L40", (-8.0, -5.2), 90, "laugh", run=True)
go("marisol", "L41", (0.6, -5.2))
obj("L40", "box", follow="marisol", off=(0, -0.45, 0.95), pos=[0, 0, 0])
S("L40", V((2.4, -2.2, 1.0), (0, 0, 1.2), 28, (2.0, -1.8, 1.0)), "Marisol comes running", hand=0.012, follow="marisol")
S("L40.1", V((1.1, -1.5, 1.3), (0, -0.1, 1.15), 34, (0.9, -1.2, 1.3)), "with a second pizza", hand=0.012, follow="marisol")
obj("L41", "box", on=False)
obj("L41", "box2", (0.5, -5.55, 0.48))
put("me", "L41", (-0.4, -5.75, -0.23), 0, "laugh", tremble=2)
put("marisol", "L41", (1.4, -5.75, -0.23), 0, "laugh", tremble=2)
S("L41", V((0.5, -9.0, 1.2), (0.5, -5.75, 0.95), 28, (0.5, -8.0, 1.2)), "we split it on the curb")
S("L41.1", V((0.5, -12, 1.6), (0.5, -3, 1.8), 26, (0.5, -11, 1.6)), "on the curb, the lemon house behind")
S("L41.2", V((0.5, -7.5, 1.3), (0.5, -5.75, 1.25), 38, (0.5, -7.0, 1.3)), "laughing so hard")
S("L41.3", V((0.5, -8.0, 1.2), (0.5, -5.75, 1.15), 34, (0.5, -7.2, 1.2)), "we shook")
put("marisol", "L42", (1.4, -5.75, -0.23), -75, "soft", arms=[0, 95])
put("me", "L42", (-0.4, -5.75, -0.23), 20, "smile")
S("L42", V((0.5, -8, 1.35), (0.5, -5.75, 1.3), 34, (0.5, -7.2, 1.35)), "she says")
S("L42.1", V((1.4, -7.2, 1.5), (0.5, -5.75, 1.45), 40, (1.2, -6.7, 1.5)), "the route is mine: she taps my cap brim")
gone("me", "L43")
gone("marisol", "L43")
obj("L42.1", "box2", on=False)

# =========================================================================================== 10 the sting + loop L43-L44
badge("L43", "6:00")
obj("L43", "slip", (-40.9, 0.7, 1.01))
obj("L43", "slip2", (-40.4, 0.7, 1.01))
S("L43", V((-40.2, -1.3, 1.7), (-40.6, 0.7, 1.05), 34, (-40.4, -0.9, 1.5)), "last night: a second slip beside the first")
S("L43.1", V((-40.6, 0.2, 1.9), (-40.6, 0.75, 1.02), 36, (-40.6, 0.3, 1.5)), "a second order came in")
S("L43.2", V((147, 28, 2.0), (150, 60, 4.0), 26, (148, 31, 2.0)), "from another house: a second lemon house, puffing")
ch("L43.3+0.1", "flap", 1.0, 0.2)
ch("L43.3+0.4", "flap", 0.0, 0.2)
ch("L43.3+0.7", "flap", 1.0, 0.2)
ch("L43.3+1.0", "flap", 0.0, 0.3)
obj("L43.3", "slip", on=False)
obj("L43.3", "slip2", on=False)
S("L43.3", V((-1.5, -1.6, 0.78), (-1.5, 0, 0.5), 24, (-1.5, -1.2, 0.72)), "with no door: the slot's flap lifts twice")
badge("L44", "+0:02", "late")
obj("L44", "box", (-1.5, -0.04, 0.5))
S("L44", V((-1.5, -2.2, 1.0), (-1.5, 0, 0.55), 24, (-1.5, -1.55, 0.78), (-1.5, 0, 0.5)), "push in to frame 1: the loop")

# ---------------------------------------------------------------------------------------------------- story
look = {"fog": "#ffd0b0", "fog_density": 0.002, "fog_start": 40.0, "sky": "#ff8a4a", "exposure": 0.0, "flash_safe": True,
        "style": "closer",
        "polish": {"emph": ["L01", "L24", "L27", "L36"], "reveal": ["L24", "L27"], "twist": "L24",
                   "quiet": [["L40", "L42"]], "camera": True, "idle": True, "ease": True}}
story = {
    "slug": "ep82-no-door",
    "title": "Pizza For The House With No DOOR \U0001F355",
    "made_for_kids": False,
    "premise": "Every night at six I bring one large plain pizza to a lemon house with no door and no path, and slide it "
               "through a brass slot at knee height. A twenty slides back out, folded into a tiny house. My big sister "
               "gave me her route this month, and tonight my tire went flat two blocks away.",
    "twist": "The house is somebody enormous sitting very still with a roof on. The slot is its mouth, the top windows "
             "its eyes, and one plain pizza a night is what keeps it sitting. Late, it stands and turns toward the "
             "nearest lit door; the order only ever says the house with no door, so I deliver it to the bare dirt.",
    "world": "a short sundown street of painted houses with porch lights, one doorless lemon-brick house with a brass "
             "slot at knee height, and a red-and-white pizza place on the corner",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff4d2e",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "look": look,
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.04, 0.01, -0.03], "saturation": 1.12, "contrast": 1.05,
              "vignette": 0.15, "bloom": 0.2, "grain": 0.008, "red_line": 0.78},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "music": {"root": 40, "mode": "mixolydian", "bpm": 124, "seed": 82,
              "sections": [
                  {"at": 0, "voices": ["pulse", "pluck_hi", "bubble"], "energy": 0.7},
                  {"at": "L14", "voices": ["pulse", "pluck_hi", "bubble"], "energy": 0.95},
                  {"at": "L16", "voices": ["pulse", "tick"], "energy": 0.6},
                  {"at": "L21", "voices": ["drone", "pulse"], "energy": 0.55},
                  {"at": "L36", "voices": ["pulse", "pluck", "pad"], "energy": 0.55},
                  {"at": "L43", "voices": ["drone"], "energy": 0.3},
              ]},
    "sound": {
        "rev": 1, "floor": "concrete", "steps_db": -22,
        "ambience": [{"kind": "traffic", "from": 0, "to": "end", "lufs": -44}],
        "sfx": [
            {"at": "L01>-0.3", "kind": "knock", "pattern": [0], "tone": "soft", "db": -10},
            {"at": "L05+0.2", "kind": "latch", "db": -20},
            {"at": "L14.1", "kind": "puff", "db": -20},
            {"at": "L22", "kind": "thud", "db": -14},
            {"at": "L23", "kind": "creak", "dur": 1.6, "db": -12},
            {"at": "L24.1", "kind": "sting_mid", "db": -14},
            {"at": "L36.1+0.1", "kind": "thud", "db": -9},
            {"at": "L43.3", "kind": "thud", "db": -14},
        ],
        "music_drops": [{"from": "P01", "to": "P01>"}],
    },
}
from blocky import timeline

voice = json.loads((HERE.parent / "voice-timings.json").read_text())
_tl0 = timeline.build({"name": "ep82-no-door", "lines": lines, "shots": [{"id": "S0"}], "gap": 0.12, "tail": 0.25,
                       "cast": cast}, voice)
AT = timeline.resolver(_tl0["lines"], _tl0["duration"])
for k in acting:
    acting[k].sort(key=lambda e: AT(e["at"]))
cues.sort(key=lambda e: AT(e["at"]))
story["rev"] = 1
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots, {len(cues)} cues")
