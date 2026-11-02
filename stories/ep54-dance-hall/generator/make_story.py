"""Writes ../story.json for ep54 "dance hall" (script.md, 2026-11-02).

Run from anywhere: python stories/ep54-dance-hall/generator/make_story.py
The words are in lines.json next to this file (every line of the script, exactly). Everything else is here: the cast,
the shots, who stands where in each (a "tableau", set on the cut so nobody walks on film), the cues set.py reads, the
score and the sound. Shot ids are numbered in order, and every shot starts on a line reference, never a rounded time.

Places (set.py's coordinates): THE HALL is at the origin (floor x -4..4, y -8..8); Ros's partner's spot P is (0, 0.6),
Ros dances at (0, -0.6) facing +y; the record player is on its table at the north wall (0, 7.3). THE STREET is at x = -80
(bus stop -80, the long table -64, the first gate -52, the neighbours' gate -40). THE BUS is at x = -140. THE STAIR is at
x = +40 (the landing at y 8, z 3.4). A character facing -y has yaw 0, facing +x yaw 90, facing -x yaw -90, facing +y 180.
Arms are [right (rig arm -1), left (arm 1)]: the right arm is on the character's -x side when it faces -y.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

SM = "smirk"          # the warm smile (the engine's "grin" is the uncanny wall of teeth)
EYES_SHUT = "shut"

# ---------------------------------------------------------------------------------------------------- the cast
FACE = {"eyes": "round", "brows": True, "ink": "#16100c"}
cast = {
    # me: short dark curly hair, a mustard cardigan over a white shirt with a big pointed collar (set.py), brown trousers
    "me": {"age": "adult", "skin": "#d9a77c", "shirt": "#c9a23a", "pants": "#5a3d28", "shoes": "#6b4226", "sleeves": "long",
           "hair": "cap", "hair_c": "#1d1612", "face": dict(FACE)},
    # Aunt Ros: a silver bob, a teal blouse with a drawn ripple, navy trousers, silver low-heeled dance shoes
    "ros": {"age": "adult", "skin": "#e8b98e", "shirt": "#2f8a8a", "pattern": "knit", "pattern_c": "#1f6666",
            "pants": "#1f2a4a", "shoes": "#c4cad2", "sleeves": "long", "hair": "long", "hair_c": "#c6c9cf",
            "face": {"eyes": "lashes", "brows": True, "ink": "#16100c"}},
    # the class: four couples, each in its own colours (sage, rust, sky, charcoal)
    "a1": {"age": "adult", "skin": "#f1c9a0", "shirt": "#9cb28a", "pants": "#4a4036", "shoes": "#3a2a1c", "sleeves": "long",
           "hair": "cap", "hair_c": "#6b4a2e", "face": dict(FACE)},
    "a2": {"age": "adult", "skin": "#c68a5c", "shirt": "#9cb28a", "pants": "#6a5a44", "shoes": "#3a2a1c", "sleeves": "long",
           "hair": "bun", "hair_c": "#2a1810", "face": {"eyes": "lashes", "brows": True, "ink": "#16100c"}},
    "b1": {"age": "adult", "skin": "#e8b98e", "shirt": "#b5532f", "pants": "#3b3a40", "shoes": "#2a2018", "sleeves": "long",
           "hair": "buzz", "hair_c": "#a8a8a8", "extras": ["glasses"], "face": dict(FACE)},
    "b2": {"age": "adult", "skin": "#8d5a3b", "shirt": "#b5532f", "pants": "#3b3a40", "shoes": "#2a2018", "sleeves": "long",
           "hair": "long", "hair_c": "#14100e", "face": {"eyes": "lashes", "brows": True, "ink": "#16100c"}},
    "c1": {"age": "adult", "skin": "#b5794e", "shirt": "#6fa8d8", "pants": "#2e3a52", "shoes": "#d8d2c4", "sleeves": "long",
           "hair": "swoop", "hair_c": "#7a3b1c", "face": dict(FACE)},
    "c2": {"age": "adult", "skin": "#f1c9a0", "shirt": "#6fa8d8", "pants": "#2e3a52", "shoes": "#d8d2c4", "sleeves": "long",
           "hair": "bun", "hair_c": "#14100e", "face": {"eyes": "lashes", "brows": True, "ink": "#16100c"}},
    "d1": {"age": "adult", "skin": "#d9a77c", "shirt": "#3b3f46", "pants": "#22242a", "shoes": "#141414", "sleeves": "long",
           "hair": "spiky", "hair_c": "#14100e", "face": dict(FACE)},
    "d2": {"age": "adult", "skin": "#e8b98e", "shirt": "#3b3f46", "pants": "#22242a", "shoes": "#141414", "sleeves": "long",
           "hair": "long", "hair_c": "#a9712f", "face": {"eyes": "lashes", "brows": True, "ink": "#16100c"}},
    # the opener's gate: an older man, and his postman (blue cap, satchel, a parcel)
    "gm": {"age": "adult", "skin": "#e8b98e", "shirt": "#7aa86a", "pattern": "stripes", "pattern_c": "#e8e0c0",
           "pants": "#4a4036", "shoes": "#3a2a1c", "sleeves": "long", "hair": "buzz", "hair_c": "#c8c8c8",
           "extras": ["tie"], "extra_c": "#a03a2c", "face": dict(FACE)},
    "pm": {"age": "adult", "skin": "#8d5a3b", "shirt": "#3b6aa8", "pants": "#2a3550", "shoes": "#1c1c20", "sleeves": "long",
           "hat": "ballcap", "hat_c": "#2a5fc4", "hair": "none", "extras": ["backpack"], "extra_c": "#7a5a38",
           "face": dict(FACE)},
}
MEN = ("me", "a1", "b1", "c1", "d1", "gm")
marks = {"me": [0, "R", "arm-1"], "ros": [0, "L", "arm1"],
         "a1": [1, "L", "arm-1"], "a2": [1, "R", "arm1"], "b1": [2, "L", "arm-1"], "b2": [2, "R", "arm1"],
         "c1": [3, "L", "arm-1"], "c2": [3, "R", "arm1"], "d1": [4, "L", "arm-1"], "d2": [4, "R", "arm1"],
         "gm": [5, "L", "arm-1"], "pm": [5, "R", "arm1"]}
pairs = {"ros": [0, "ros", "me"], "a": [1, "a1", "a2"], "b": [2, "b1", "b2"], "c": [3, "c1", "c2"], "d": [4, "d1", "d2"],
         "g": [5, "gm", "pm"]}

# ---------------------------------------------------------------------------------------------------- helpers
ROS_AT = (0.0, -0.6)
P_AT = (0.0, 0.6)
KP = (0.0, 0.5)                           # where the Stilted stands: its legs straddle the spot
HALL_DOOR = (0.0, -7.0)


def cm(p0, t0, lens, p1=None, t1=None, lens1=None, roll=0.0):
    """A camera: one key, or a slow move from the first key to the second over the shot."""
    if p1 is None:
        return [[0, list(p0), list(t0), lens, roll]]
    return [[0, list(p0), list(t0), lens, roll], [1, list(p1), list(t1 if t1 is not None else t0),
                                                   lens1 if lens1 is not None else lens, roll]]


def yaw_to(frm, to):
    """The yaw that faces `to` from `frm` (0 faces -y, 90 faces +x)."""
    return math.degrees(math.atan2(to[0] - frm[0], -(to[1] - frm[1])))


def D(pos, yaw=0.0, expr="neutral", arms=(0, 0), side=(0, 0), head=(0, 0), z=0.0, **kw):
    """One person in a tableau."""
    d = {"pos": [pos[0], pos[1], z], "yaw": yaw, "expr": expr, "arms": list(arms), "side": list(side), "head": list(head)}
    d.update(kw)
    return d


def face(frm, to, **kw):
    return D(frm, yaw_to(frm, to), **kw)


def couple(c, ang, names, expr=SM, closed=False):
    """A couple in hold: the man at c + 0.6 u, the woman at c - 0.6 u (u = angle `ang`), facing each other, the man's right
    hand on the woman's left (the glyph pair's side)."""
    ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    m, w = (c[0] + 0.6 * ux, c[1] + 0.6 * uy), (c[0] - 0.6 * ux, c[1] - 0.6 * uy)
    return {names[0]: face(m, w, expr=expr, arms=(70, 40), side=(0, 10)),
            names[1]: face(w, m, expr=expr, arms=(40, 70), side=(10, 0))}


CLASS = [("a1", "a2"), ("b1", "b2"), ("c1", "c2"), ("d1", "d2")]


def class_circling(expr=SM, rot=0.0):
    out = {}
    for k, nm in enumerate(CLASS):
        a = rot + 90 * k + 30
        c = (2.1 * math.cos(math.radians(a)), 0.6 + 2.1 * math.sin(math.radians(a)))
        out.update(couple(c, a, nm, expr))
    return out


def class_wall(expr="neutral", clap=False, far=False):
    """The class standing in front of the chairs, watching (west: a, b; east: c, d)."""
    out = {}
    ys = (-3.6, -2.4, -1.2, 0.0)
    for i, n in enumerate(("a1", "a2", "b1", "b2")):
        out[n] = D((-3.0, ys[i] + (6 if far else 0)), 90, expr, arms=(70, 70) if clap else (0, 0))
    for i, n in enumerate(("c1", "c2", "d1", "d2")):
        out[n] = D((3.0, ys[i] + (6 if far else 0)), -90, expr, arms=(70, 70) if clap else (0, 0))
    return out


def ros_demo(expr=EYES_SHUT, **kw):
    return D(ROS_AT, 180, expr, arms=(75, 75), **kw)


def me_at_player(pos=(-0.5, 6.5), yaw=0.0, expr="neutral", **kw):
    return D(pos, yaw, expr, **kw)


# the tableaux: who is where in each shot. Anyone not listed is hidden.
SH = []          # (at, camera, people, opts)


def S(at, cam, people, **opt):
    SH.append((at, cam, people, opt))


# ---------------------------------------------------------------------------------------------------- 01 the rule
BS = -80.0       # the bus stop
STRANGERS = {"a1": D((BS - 0.55, 0.3), 62, SM, arms=(85, 0), head=(-30, 0)),
             "a2": D((BS + 0.55, 0.3), -62, SM, arms=(0, 85), head=(30, 0))}
S(0, cm((BS, -2.5, 1.55), (BS, 0.3, 1.45), 20, (BS, -2.2, 1.55), (BS, 0.3, 1.45), 21), STRANGERS, hand=0.004)
S("L01.4", cm((BS, -1.3, 1.5), (BS, 0.3, 1.4), 24, (BS, -1.1, 1.5), (BS, 0.3, 1.4), 26), STRANGERS)
CAFE = -64.0
CAFE_ROW = {"b1": D((CAFE - 1.9, 3.5), 0, SM, arms=(85, 0)), "b2": D((CAFE - 1.2, 3.5), 0, SM, arms=(0, 70)),
            "c2": D((CAFE - 0.25, 3.5), 0, SM, arms=(0, 85)), "c1": D((CAFE + 0.55, 3.5), 0, SM, arms=(85, 0)),
            "d1": D((CAFE + 1.3, 3.5), 0, SM, arms=(60, 0)), "d2": D((CAFE + 2.0, 3.5), 0, SM, arms=(0, 85))}
S("L02", cm((CAFE - 2.6, 0.3, 1.45), (CAFE - 0.3, 3.4, 1.4), 20, (CAFE - 2.0, 0.3, 1.45), (CAFE - 0.3, 3.4, 1.4), 20), CAFE_ROW)
S("L02.1", cm((CAFE + 0.15, 1.3, 1.45), (CAFE + 0.15, 3.5, 1.4), 24), CAFE_ROW)
S("L02.2", cm((CAFE + 3.6, 1.4, 1.4), (CAFE - 0.5, 3.5, 1.4), 22, (CAFE + 3.0, 1.4, 1.4), (CAFE - 0.5, 3.5, 1.4), 22), CAFE_ROW)
GATE = -52.0
GATE_P = {"gm": D((GATE + 0.55, 4.4), 15, SM, arms=(85, 0)), "pm": D((GATE - 0.55, 4.4), -15, SM, arms=(0, 85))}
S("L03", cm((GATE, 1.2, 1.5), (GATE, 4.4, 1.35), 20, (GATE, 1.6, 1.5), (GATE, 4.4, 1.35), 20), GATE_P)
S("L03.2", cm((GATE + 0.3, 2.0, 1.5), (GATE, 4.4, 1.5), 28), GATE_P)
BUSX = -140.0
BUS_PAIR = {"b1": D((BUSX + 0.6, 0.3), -90, SM, arms=(85, 0)), "b2": D((BUSX - 0.6, 0.3), 90, SM, arms=(0, 85))}
BUS_CROWD = {**BUS_PAIR,
             "a1": D((BUSX - 0.5, -1.5), 0, SM, arms=(160, 160)), "a2": D((BUSX + 0.55, -1.8), 0, SM, arms=(160, 160)),
             "c1": D((BUSX - 0.6, -3.0), 0, SM, arms=(160, 160)), "c2": D((BUSX + 0.5, -3.3), 0, SM, arms=(160, 160))}
S("L04", cm((BUSX + 0.1, -1.8, 1.5), (BUSX, 0.4, 1.4), 22), BUS_PAIR)
S("L04.4", cm((BUSX, 4.0, 1.7), (BUSX, -2.0, 1.5), 20, (BUSX, 3.4, 1.7), (BUSX, -2.0, 1.5), 20),
  {**BUS_CROWD, "b1": D((BUSX + 0.6, 0.3), -90, SM, arms=(85, 160)), "b2": D((BUSX - 0.6, 0.3), 90, SM, arms=(160, 85))})
NB = -40.0
NEIGH = {"d1": D((NB - 0.55, 4.4), 70, "smirk", arms=(85, 0)), "d2": D((NB + 0.55, 4.4), -70, "angry", arms=(0, 85))}
S("L05", cm((NB, 1.3, 1.5), (NB, 4.4, 1.4), 20), NEIGH)
S("L05.3", cm((NB, 2.4, 1.55), (NB, 4.4, 1.5), 28), {"d1": D((NB - 0.55, 4.4), 40, SM, arms=(85, 0)),
                                                      "d2": D((NB + 0.55, 4.4), -40, SM, arms=(0, 85))})
BARE_HANDS = D((BS, 0.3), 0, "neutral", arms=(92, 92), side=(14, 14), head=(0, 4))
S("L06", cm((BS, -2.1, 1.75), (BS, 0.3, 1.2), 22, (BS, -1.8, 1.75), (BS, 0.3, 1.2), 22), {"me": BARE_HANDS})
ST = 40.0
S("L07", cm((ST, 5.6, 3.5), (ST, 2.75, 2.85), 24), {"ros": D((ST, 2.75), 180, SM, arms=(0, 85), z=1.46)})
S("L08", cm((0, -7.6, 2.6), (0, 1.0, 1.7), 17, (0, -6.6, 2.6), (0, 1.0, 1.7), 17),
  {"ros": D((0, -2.0), 180, SM),
   "a1": D((-2.5, -3.5), 135, SM), "a2": D((-1.6, -4.4), 150, SM), "b1": D((2.5, -3.0), -110, SM),
   "b2": D((1.7, -4.2), -150, SM), "c1": D((-1.0, -0.5), 100, SM), "c2": D((1.0, 0.8), -100, SM),
   "d1": D((-3.0, 0.5), 90, "neutral"), "d2": D((3.0, -1.0), -90, "neutral")})
S("L09", cm((0.9, 5.4, 1.55), (-0.3, 7.1, 1.1), 28), {"me": D((-0.76, 6.6), 180, "neutral", arms=(70, 0), head=(0, 4))})
S("L09.4", cm((0.0, 4.0, 1.6), (-0.4, 6.6, 1.5), 24), {"me": me_at_player((-0.4, 6.6), 0, "neutral")})

# ---------------------------------------------------------------------------------------------------- 02 the rule at work
S("L10", cm((-3.4, -6.4, 3.4), (0, 0.4, 1.0), 18, (-3.0, -6.0, 3.0), (0, 0.4, 1.0), 18), class_circling())
CLOSE_C = {**couple((1.5, -1.5), 90, ("c1", "c2"), SM)}
S("L11", cm((-0.2, -1.5, 1.3), (1.0, -1.5, 1.1), 30, (-0.1, -1.5, 1.25), (1.0, -1.5, 1.1), 32), CLOSE_C)
S("L12", cm((0.2, 2.9, 1.65), (0, -0.6, 1.3), 21), {"ros": ros_demo(), **class_wall("neutral")})
S("L12.2", cm((-2.0, 3.5, 1.0), (0, -0.6, 1.3), 20, (-1.6, 3.2, 1.0), (0, -0.6, 1.3), 20), {"ros": ros_demo(), **class_wall("neutral")})
S("L13", cm((0, 0.4, 1.7), (0, -0.6, 1.55), 34), {"ros": D(ROS_AT, 170, EYES_SHUT, arms=(75, 75))})
S("L13.2", cm((0.7, 5.9, 1.3), (0.55, 7.2, 0.95), 40), {"me": D((0.04, 6.8), 180, "neutral", arms=(55, 0))})
S("L14", cm((-1.3, -0.5, 1.15), (-0.5, 0.05, 1.0), 40), {"ros": ros_demo()})
S("L15", cm((0.9, 0.3, 0.16), (-0.3, -5.0, 0.1), 24, (0.9, 0.0, 0.16), (-0.3, -5.0, 0.1), 24), {"ros": ros_demo()})
S("L16", cm((-0.5, -3.0, 0.15), (0.4, -7.2, 0.2), 24), {})
S("L17", cm((0.8, 5.2, 1.5), (-0.3, 6.6, 1.45), 24), {"me": me_at_player((-0.4, 6.6), -20, "worried", head=(20, 0))})

# ---------------------------------------------------------------------------------------------------- 03 traces
COLLAR = {"ros": D((0.0, 6.0), 180, SM, arms=(100, 100)), "me": D((0.0, 6.7), 0, "neutral")}
S("L18", cm((2.2, 6.35, 1.5), (0, 6.35, 1.45), 24), COLLAR)
S("L19", cm((1.3, 6.3, 1.55), (0, 6.3, 1.5), 34), COLLAR)
S("L20", cm((0, -3.2, 1.7), (0, -1.5, 1.55), 28), {"ros": D((0.0, -1.5), 180, "neutral", head=(0, -22))})
S("L21", cm((0, -2.8, 0.5), (0, 0, 3.0), 22), {})
S("L22", cm((-2.2, 0.0, 1.6), (3.96, 0.0, 2.4), 20), {})
S("L23", cm((-0.4, 6.6, 1.3), (-0.25, 7.3, 1.04), 40), {})

# ---------------------------------------------------------------------------------------------------- 04 gone
S("L24", cm((0.0, 5.3, 1.55), (0.1, 6.8, 1.4), 24), {"me": D((0.2, 6.4), 150, "neutral", head=(15, 0))})
S("L24.2", cm((0.0, 5.3, 1.55), (0.0, 6.8, 1.4), 24), {"me": D((0.2, 6.4), 20, "worried", head=(0, 0))})
S("L24.3", cm((0.0, 7.0, 1.6), (0.0, -2.0, 1.4), 17, (0.0, 6.4, 1.6), (0.0, -2.0, 1.4), 17), {})
S("P01", cm((0.0, 6.4, 1.6), (0.0, -2.0, 1.4), 17), {})
S("L25", cm((-1.6, -1.2, 0.3), (0, -0.55, 0.05), 24, (-1.0, -0.9, 0.25), (0, -0.55, 0.05), 24), {})
S("L26", cm((0.0, 0.3, 0.2), (0, -0.55, 0.05), 32), {})
S("L27", cm((-0.4, 6.6, 1.3), (-0.25, 7.3, 1.04), 40), {})
S("L28", cm((0.0, -2.8, 1.75), (0, 0.8, 1.3), 18), {"me": D((0.0, 0.8), 0, "scared", head=(0, 0))})
S("L29", cm((0.4, -0.5, 0.9), (0.0, 0.5, 3.2), 22), {})
S("L30", cm((0.0, -0.7, 1.6), (0, 0.8, 1.5), 34), {"me": D((0.0, 0.8), 0, "scared")})
S("L31", cm((-0.5, 1.5, 0.45), (0.0, -1.8, 0.05), 20), {})
S("L32", cm((ST, 9.0, 4.6), (ST, 0.0, 0.8), 22), {})
S("L33", cm((-0.5, 1.5, 0.45), (0.0, -1.8, 0.05), 20), {})
S("L34", cm((ST, 10.6, 4.95), (ST, 8.0, 4.9), 28), {"ros": D((ST, 8.0), 180, "worried", z=3.4)})
S("L35", cm((ST, 10.8, 5.0), (ST, 8.6, 4.75), 20), {"ros": D((ST - 0.45, 8.3), 180, "worried", z=3.4),
                                                       "me": D((ST + 0.45, 8.6), 180, "worried", z=3.4)})
S("L35.4", cm((ST, 10.3, 5.0), (ST - 0.2, 8.3, 4.95), 36), {"ros": D((ST - 0.2, 8.3), 180, "worried", z=3.4)})
S("L36", cm((ST + 0.3, 10.0, 4.95), (ST - 0.2, 8.1, 4.55), 40), {"ros": D((ST - 0.2, 8.3), 180, "worried", arms=(0, 78), z=3.4)})
S("L37", cm((0, -3.0, 1.6), (0, -0.9, 1.35), 26), {"ros": D((0.0, -1.0), 180, "worried", arms=(55, 55))})

# ---------------------------------------------------------------------------------------------------- 05 closer
S("L38", cm((-1.7, -5.3, 0.3), (-1.75, -6.45, 0.02), 30), {})
S("L39", cm((-1.7, -5.2, 2.7), (-1.75, -6.5, 0.0), 22), {"me": D((-1.75, -6.5), 0, "neutral")})
S("L40", cm((-1.8, -5.6, 2.8), (-1.75, -6.45, 0.0), 22), {})
S("L40.1", cm((-1.8, -2.4, 2.8), (-1.55, -3.15, 0.0), 22), {})
S("L40.2", cm((-0.4, 0.0, 2.8), (-0.8, -1.0, 0.0), 22), {})
S("L41", cm((1.4, -1.2, 0.5), (0, 0.2, 0.25), 26), {"ros": ros_demo()})
S("L42", cm((0, -1.2, 0.9), (0, 0.2, 3.0), 24, (0, -1.2, 0.9), (0, 0.2, 2.8), 24), {})
S("L42.4", cm((0.8, 5.2, 1.5), (-0.3, 6.5, 1.5), 26), {"me": me_at_player((-0.4, 6.5), 150, "scared", head=(20, 0))})
S("L43", cm((0, -7.4, 2.7), (0, 1.5, 1.5), 17, (0, -6.6, 2.5), (0, 1.5, 1.5), 17),
  {"ros": ros_demo("neutral", head=(0, 0)),
   **{n: d for n, d in class_wall("neutral").items()}})
S("L44", cm((0.2, 2.4, 1.45), (0, -0.6, 1.35), 22), {"ros": ros_demo()})

# ---------------------------------------------------------------------------------------------------- 06 the Stilted
S("P02", cm((-0.8, 1.9, 1.5), (0, -0.6, 1.35), 24), {"ros": ros_demo()})
S("L45", cm((0.5, 5.4, 1.45), (-0.2, 6.5, 1.6), 24), {"me": me_at_player((-0.4, 6.5), 150, "scared", head=(20, -10))})
S("L46", cm((-2.7, -1.9, 0.35), (0, 0.2, 1.1), 22), {"ros": ros_demo()})
S("L46.2", cm((-1.0, -0.4, 0.4), (0, 0.5, 0.9), 22, (-1.0, -0.4, 0.9), (0, 0.5, 3.0), 22), {"ros": ros_demo()})
S("L47", cm((-1.9, -2.3, 1.0), (0, 0.5, 3.35), 24), {"ros": ros_demo()})
SIDE = cm((3.8, 0.1, 2.0), (0, 0.1, 2.0), 15)
S("L48", SIDE, {"ros": ros_demo()})
S("L48.2", SIDE, {"ros": ros_demo()})
S("L48.3", SIDE, {"ros": ros_demo()})
S("L49", cm((1.2, -0.75, 1.6), (0, -0.1, 1.5), 28), {"ros": ros_demo()})
S("L50", cm((1.8, -1.3, 1.6), (0, 0.1, 1.45), 24), {"ros": ros_demo()})
S("L51", cm((0.3, 5.5, 1.45), (-0.4, 6.6, 1.2), 28), {"me": me_at_player((-0.4, 6.5), 0, "scared", arms=(40, 40), head=(0, -25))})
S("L52", cm((-1.3, -0.5, 1.15), (-0.5, 0.05, 1.0), 40), {"ros": ros_demo()})

# ---------------------------------------------------------------------------------------------------- 07 the other side
S("L53", cm((0.4, 5.5, 1.55), (-0.3, 6.7, 1.5), 24), {"me": me_at_player((-0.3, 6.6), 0, "worried")})
S("L54", cm((0.7, 6.0, 1.3), (0.58, 7.2, 0.95), 45), {"me": D((0.04, 6.8), 180, "neutral", arms=(55, 0))})
S("L55", cm((BS, -2.1, 1.75), (BS, 0.3, 1.2), 22, (BS, -1.8, 1.75), (BS, 0.3, 1.2), 22), {"me": BARE_HANDS})
S("L56", cm((0.5, 6.7, 1.3), (0.55, 7.3, 0.9), 45), {})
S("P03", cm((1.0, 6.85, 1.0), (0.82, 7.1, 0.89), 55), {})
S("L57", cm((-0.3, 4.9, 1.3), (-0.3, 6.4, 1.3), 28), {"me": D((-0.3, 6.4), 0, "neutral", arms=(75, 0), head=(0, -12))})
S("L58", cm((-1.0, 5.0, 1.25), (-0.8, 5.8, 1.15), 40), {"me": D((-0.3, 6.4), 0, "neutral", arms=(75, 0), head=(0, -12))})
S("L59", cm((0.0, 4.6, 0.6), (0, 0.4, 1.55), 20), {"me": D((0.0, 3.8), 0, "worried", extra_walk=True)})
S("L60", cm((-1.2, 0.0, 1.15), (-0.51, 0.0, 1.05), 36),
  {"ros": D(ROS_AT, 180, EYES_SHUT, arms=(70, 70)), "me": D(P_AT, 0, "neutral", arms=(70, 0))})
S("L61", cm((-1.2, 0.0, 1.15), (-0.51, 0.0, 1.05), 36),
  {"ros": D(ROS_AT, 180, EYES_SHUT, arms=(70, 70)), "me": D(P_AT, 0, "neutral", arms=(70, 0))})
S("L62", cm((1.2, -0.7, 1.58), (0, -0.62, 1.5), 40, (1.2, -0.7, 1.58), (0, -0.62, 1.5), 40),
  {"ros": D(ROS_AT, 180, "wide", arms=(70, 70)), "me": D(P_AT, 0, "neutral", arms=(70, 0))})
S("L63", cm((0, -1.4, 0.9), (0, 0.4, 3.2), 22), {})
S("L63.2", cm((-2.7, -3.3, 1.7), (0, 0.0, 1.25), 20), {"ros": D(ROS_AT, 180, SM, arms=(70, 70)),
                                                      "me": D(P_AT, 0, SM, arms=(70, 0))})

# ---------------------------------------------------------------------------------------------------- 08 kin
S("L64", cm((0.6, 2.0, 1.55), (0, -0.6, 1.45), 28), {"ros": D(ROS_AT, 180, SM, arms=(70, 70)), "me": D(P_AT, 0, SM, arms=(70, 0))})
S("L65", cm((-1.6, 0.0, 1.2), (-0.51, 0.0, 1.05), 30), {"ros": D(ROS_AT, 180, SM, arms=(70, 70)), "me": D(P_AT, 0, SM, arms=(70, 0))})
S("L66", cm((-0.2, 6.2, 1.4), (-0.5, 7.3, 1.0), 34), {})
S("L66.3", cm((0.8, 5.5, 1.5), (-0.3, 6.5, 1.5), 28), {"me": me_at_player((-0.4, 6.5), 0, SM)})
KIN = {"ros": D((0.0, -0.35), 180, SM, arms=(36, 36), side=(0, 30)), "me": D((0.0, 0.35), 0, SM, arms=(36, 0), side=(30, 0))}
S("L67", cm((0, -5.2, 2.3), (0, 0.3, 1.4), 18), {**KIN, **class_wall(SM)})
S("L68", cm((0.9, -0.3, 0.3), (0, 0.0, 0.12), 26),
  {"ros": D((0.0, -0.2), 180, "worried", arms=(36, 36)), "me": D((0.0, 0.02), 0, SM, arms=(36, 0), z=0.09)})
S("L69", cm((-0.4, -4.4, 1.6), (-3.0, -1.4, 1.4), 22), class_wall(SM, clap=True))
S("L70", cm((1.5, -0.9, 1.55), (0, 0.0, 1.35), 24),
  {"ros": D((0.0, -0.35), 180, SM, arms=(100, 36)), "me": D((0.0, 0.35), 0, SM, arms=(36, 0))})

# ---------------------------------------------------------------------------------------------------- 09 the loop
S("L71", cm((0.0, -3.4, 4.3), (0, 0.0, 0.9), 17), {"ros": D((0.0, -0.35), 180, SM, arms=(36, 36)),
                                                  "me": D((0.0, 0.35), 0, SM, arms=(36, 0))})
S("L72", cm((-1.15, 0.3, 1.15), (-0.55, 0.25, 0.95), 34),
  {"ros": D((0.0, -0.35), 180, SM, arms=(36, 36)), "me": D((0.0, 0.35), 0, SM, arms=(60, 0))})
S("L73", cm((0.0, 3.6, 0.9), (0, -0.6, 1.35), 20), {"ros": ros_demo()})
S("L73.3", cm((0.5, -0.3, 0.15), (-0.2, -6.5, 0.1), 24), {"ros": ros_demo()})

# ---------------------------------------------------------------------------------------------------- shots and acting
shots = []
acting = {w: [] for w in cast}
last_pos = {}
hidden_now = {w: False for w in cast}   # (the first shot hides everyone it does not list)
for i, (at, cam, people, opt) in enumerate(SH):
    sd = {"id": f"S{i + 1:02d}", "cam": cam, "step": opt.get("step", 2)}
    if i:
        sd["at"] = at
    if "hand" in opt:
        sd["hand"] = opt["hand"]
    shots.append(sd)
    for w in cast:
        keys = acting[w]
        if w in people:
            sp = dict(people[w])
            walk = sp.pop("extra_walk", False)
            k = {"at": at, **sp}
            if w in last_pos and not hidden_now[w]:
                keys.append({"at": at, "pos": last_pos[w]})
            elif w in last_pos:
                keys.append({"at": at, "pos": last_pos[w]})
            k.update({"blend": 0.0, "hidden": False})
            keys.append(k)
            last_pos[w] = sp["pos"]
            hidden_now[w] = False
            if walk:                      # L59: I walk toward the spot between its legs; cut before I get there
                keys.append({"at": "L59+1.2", "pos": [0.0, 2.6, 0.0]})
                last_pos[w] = [0.0, 2.6, 0.0]
        elif not hidden_now[w]:
            keys.append({"at": at, "hidden": True})
            hidden_now[w] = True

# ---------------------------------------------------------------------------------------------------- cues
KEEP_UP = dict(name="keeper", pos=list(KP), yaw=0, bend=0, arms=[0, 0], side=[0, 0], tilt=0)


def keeper(at, **kw):
    return {"at": at, **{**KEEP_UP, **kw}}


cues = [
    # the hall's lights: every change a slow ramp (hard rule 7). Half light for the night Ros goes, full for the Tuesdays
    {"at": "L23", "name": "hall", "chan": 0.5, "lamps": 0.0, "dur": 0.7},
    {"at": "L34", "name": "hall", "chan": 1.0, "lamps": 1.0, "dur": 0.7},
    {"at": "L43", "name": "hall", "chan": 0.5, "lamps": 0.15, "dur": 1.5},
    {"at": "L65", "name": "hall", "chan": 1.0, "lamps": 1.0, "dur": 0.9},
    {"at": "L73", "name": "hall", "chan": 0.33, "lamps": 0.15, "dur": 1.2},
    # Ros's half dims across the story (every change over 0.4 s or more)
    {"at": 0, "name": "ros_mark", "v": 1.0},
    {"at": "L13.2", "name": "ros_mark", "v": 0.7, "dur": 0.5},
    {"at": "L17", "name": "ros_mark", "v": 0.5, "dur": 0.5},
    {"at": "L19", "name": "ros_mark", "v": 0.9, "dur": 0.4},
    {"at": "L19+0.8", "name": "ros_mark", "v": 0.5, "dur": 0.6},
    {"at": "L33", "name": "ros_mark", "v": 0.25, "dur": 0.5},
    {"at": "L51", "name": "ros_mark", "v": 0.1, "dur": 0.6},
    {"at": "L60", "name": "ros_mark", "v": 1.0, "dur": 0.6},
    # my half: a faint gold through the glove for a second at L13, then on my palm from L57
    {"at": 0, "name": "me_mark", "v": 0.0},
    {"at": "L13.2", "name": "me_mark", "v": 0.3, "dur": 0.4},
    {"at": "L13.2+0.8", "name": "me_mark", "v": 0.0, "dur": 0.4},
    {"at": "L58", "name": "me_mark", "v": 1.0, "dur": 0.6},
    # whole glyphs where two halves meet (0.6 s or more)
    {"at": 0, "name": "whole", "pair": "a", "v": 0.0},
    {"at": "L01.4", "name": "whole", "pair": "a", "v": 1.0, "dur": 0.8},
    {"at": "L02", "name": "whole", "pair": "a", "v": 0.0},
    {"at": "L02.1", "name": "whole", "pair": "c", "v": 1.0, "dur": 0.7},
    {"at": "L03", "name": "whole", "pair": "g", "v": 1.0, "dur": 0.7},
    {"at": "L04.4", "name": "whole", "pair": "b", "v": 1.0, "dur": 0.7},
    {"at": "L05", "name": "whole", "pair": "d", "v": 1.0, "dur": 0.7},
    {"at": "L06", "name": "whole", "pair": "d", "v": 0.0, "dur": 0.6},
    {"at": "L10", "name": "whole", "pair": "a", "v": 1.0, "dur": 0.7},
    {"at": "L10", "name": "whole", "pair": "b", "v": 1.0, "dur": 0.7},
    {"at": "L10", "name": "whole", "pair": "c", "v": 0.0},
    {"at": "L10", "name": "whole", "pair": "d", "v": 1.0, "dur": 0.7},
    {"at": "L11", "name": "whole", "pair": "c", "v": 1.0, "dur": 0.7},
    {"at": "L12", "name": "whole", "pair": "a", "v": 0.0},
    {"at": "L12", "name": "whole", "pair": "b", "v": 0.0},
    {"at": "L12", "name": "whole", "pair": "c", "v": 0.0},
    {"at": "L12", "name": "whole", "pair": "d", "v": 0.0},
    {"at": "L61", "name": "whole", "pair": "ros", "v": 1.0, "dur": 0.8},
    {"at": "L66.3", "name": "whole", "pair": "ros", "v": 0.0, "dur": 0.6},
    {"at": "L67", "name": "whole", "pair": "ros", "v": 1.0, "dur": 0.7},
    {"at": "L69", "name": "whole", "pair": "ros", "v": 0.0, "dur": 0.6},
    {"at": "L70", "name": "whole", "pair": "ros", "v": 1.0, "dur": 0.8},
    {"at": "L73", "name": "whole", "pair": "ros", "v": 0.0, "dur": 0.6},
    # gloves on in the hall (L09 on, off at L56 across a cut; on the lid after it)
    {"at": 0, "name": "gloves", "on": False},
    {"at": "L08", "name": "gloves", "on": True},
    {"at": "L55", "name": "gloves", "on": False},
    {"at": "L56", "name": "glovelid", "on": True},
    {"at": "L67", "name": "glovelid", "on": False},
    # the plum coat and brown boots for the night she goes to the station
    {"at": "L34", "name": "coat", "on": True}, {"at": "L38", "name": "coat", "on": False},
    # the chandelier: it sways from L21 (slowly, period 3 s) until the Stilted comes to stand in it
    {"at": "L20.1", "name": "sway", "amp": 1.0, "dur": 1.0},
    {"at": "L44", "name": "sway", "amp": 0.0, "dur": 1.0},
    {"at": "L29", "name": "sway", "amp": 0.45, "dur": 0.6},
    {"at": "L29.2", "name": "sway", "amp": 1.0, "dur": 0.8},
    # the record: skips back at L23; turning throughout
    {"at": "L23.1", "name": "skip"},
    # props
    {"at": "L25", "name": "shoes", "on": True}, {"at": "L37", "name": "shoes", "on": False},
    {"at": "L31", "name": "ladder", "on": True}, {"at": "L33", "name": "ladder", "on": False},
    {"at": "L38", "name": "scuffs", "sets": ["a"]},
    {"at": "L40", "name": "scuffs", "sets": ["a"]},
    {"at": "L40.1", "name": "scuffs", "sets": ["a", "b"]},
    {"at": "L40.2", "name": "scuffs", "sets": ["a", "b", "c"]},
    {"at": "L41", "name": "scuffs", "sets": ["d"]},
    {"at": "L42", "name": "scuffs", "sets": []},
    {"at": "P03", "name": "tally", "on": True}, {"at": "L57", "name": "tally", "on": False},
    # the chandelier's drops are pushed apart from L42 until the Stilted is gone
    {"at": "L42", "name": "parted", "v": 1.0, "dur": 0.8},
    {"at": "L63", "name": "parted", "v": 0.0},
    # the Stilted: shown from L46 and not before. Every change of pose is across a cut
    {"at": 0, "name": "keeper", "hidden": True},
    keeper("L46", bend=0),
    keeper("L47", bend=0),
    keeper("L48", bend=0),
    keeper("L48.2", bend=80, tilt=0),
    keeper("L48.3", bend=150, tilt=-4),
    keeper("L49", bend=150, tilt=-4),
    keeper("L50", bend=150, tilt=-4, arms=[70, 70], side=[0, 0]),
    keeper("L51", bend=150, tilt=-4, arms=[70, 70]),
    keeper("L52", bend=150, tilt=-4, arms=[70, 70]),
    keeper("L53", bend=150, tilt=-4, arms=[70, 70]),
    {"at": "L54", "name": "keeper", "hidden": True},
    keeper("L59", bend=150, tilt=-4, arms=[70, 70]),
    keeper("L60", bend=150, tilt=-4, arms=[70, 70]),
    {"at": "L63", "name": "keeper", "hidden": True},
]

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    # the street opener: a bus hiss under the bus line, a swell of cheering
    {"at": "L04.4", "kind": "whoosh", "db": -20, "dur": 1.4},
    {"at": "L01.4", "kind": "bell", "db": -26, "dur": 1.2},
    {"at": "L11", "kind": "bell", "db": -24, "dur": 1.2},
    # the creaks: a long low groan, lower each time it nears Ros
    {"at": "L15.1", "kind": "creak", "db": -12, "dur": 1.6},
    {"at": "L16", "kind": "creak", "db": -12, "dur": 1.6},
    {"at": "L16.1", "kind": "creak", "db": -10, "dur": 1.8},
    {"at": "L21.1", "kind": "bell", "db": -24, "dur": 1.0},
    {"at": "L23.1", "kind": "glitch", "db": -14, "dur": 0.5},
    {"at": "P01+0.45", "kind": "thud", "db": -6, "keep": True},
    {"at": "L29", "kind": "bell", "db": -20, "dur": 1.6},
    {"at": "L29.2", "kind": "bell", "db": -20, "dur": 1.6},
    {"at": "L32+0.25", "kind": "door", "db": -18, "dur": 0.8},
    {"at": "L38.2", "kind": "whoosh", "db": -30, "dur": 0.4},
    {"at": "L39.1", "kind": "whoosh", "db": -30, "dur": 0.4},
    {"at": "L42.1", "kind": "bell", "db": -20, "dur": 1.6},
    {"at": "P02+0.3", "kind": "creak", "db": -8, "dur": 1.8, "keep": True},
    {"at": "L46+0.2", "kind": "creak", "db": -14, "dur": 1.2},
    {"at": "L48", "kind": "creak", "db": -15, "dur": 1.2},
    {"at": "L48.2", "kind": "creak", "db": -15, "dur": 1.2},
    {"at": "L48.3", "kind": "creak", "db": -14, "dur": 1.6},
    {"at": "L49", "kind": "breath", "db": -18, "dur": 2.0},
    {"at": "L56", "kind": "click", "db": -16},
    {"at": "L61", "kind": "bell", "db": -18, "dur": 2.0},
    {"at": "L70+0.3", "kind": "bell", "db": -18, "dur": 2.0},
    {"at": "L69", "kind": "knock", "db": -22, "pattern": [0, 0.28, 0.55, 0.85, 1.1, 1.4], "tone": "hand"},
    {"at": "L73.1", "kind": "creak", "db": -18, "dur": 1.2},
    {"at": "L73.3", "kind": "creak", "db": -14, "dur": 1.2},
]
story = {
    "slug": "ep54-dance-hall",
    "title": "In this town, you're born with half a mark",
    "made_for_kids": False,
    "premise": "In a town where everyone is born with half a glowing glyph on one hand and a match out there with the rest, I play the records for Aunt Ros's Tuesday ballroom class in white gloves and never dance. Her half is fading, she dances every demonstration with her arms round nobody, and the floor starts to creak behind her in a stride far too long.",
    "twist": "The rule never says which side of the hand. Mine is on my palm, hidden under my record gloves, and Ros's match has been carrying her records for forty years: a match was never only for love, it is whoever you fit with.",
    "world": "An old upstairs dance hall above a row of shops on Tuesday nights in autumn: a honey maple floor worn pale in a ring, primrose plaster, three tall arched windows of indigo night, bentwood chairs and one low brass chandelier of glass drops, with a sunny bus stop street for the opener.",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffcf66",
    "gap": 0.12,
    "tail": 0.25,
    "look": {"fog": "#c9d8e4", "fog_density": 0.012, "fog_start": 14.0, "sky": "#8fc6ea", "exposure": 0.0, "flash_safe": True},
    "grade": {"shadows": [-0.01, 0.0, 0.03], "highlights": [0.04, 0.02, -0.03], "saturation": 1.0,
              "contrast": 1.05, "vignette": 0.3, "bloom": 0.45, "grain": 0.01},
    "phonemes": {},
    "cast": cast,
    "marks": marks,
    "pairs": pairs,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    # E aeolian, a slow waltz at 84. Thin at first (a soft low pluck and a breathy pad); a heavy low drone enters at the first
    # taking (L24) and holds to the end; E major for the warm turn (L64 to L70), back to minor for the cold close
    "music": {"root": 40, "mode": "minor", "bpm": 84, "seed": 54,
              "sections": [
                  {"at": 0, "voices": ["pad", "piano"], "energy": 0.3},
                  {"at": "L10", "voices": ["pad", "piano"], "energy": 0.4},
                  {"at": "L24", "voices": ["drone", "pad", "piano"], "energy": 0.45},
                  {"at": "L45", "voices": ["drone", "pad"], "energy": 0.5},
                  {"at": "L53", "voices": ["drone", "pad", "piano"], "energy": 0.5},
                  {"at": "L64", "mode": "major", "voices": ["drone", "pad", "piano", "pulse"], "energy": 0.6},
                  {"at": "L71", "mode": "minor", "voices": ["drone"], "energy": 0.3},
              ]},
    "sound": {"floor": "wood", "steps_db": -24,
              "floor_spans": [{"from": "L01", "to": "L08", "floor": "grass"}],
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "L08", "lufs": -40},
                  {"kind": "hum", "from": 0, "to": "L08", "lufs": -44},
                  {"kind": "room", "from": "L08", "to": "L24", "lufs": -40},
                  {"kind": "drone", "from": "L24", "to": "end", "lufs": -34},
                  {"kind": "room", "from": "L24", "to": "end", "lufs": -42},
                  {"kind": "drips", "from": "L28", "to": "L34", "lufs": -46},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "L25", "keep": ["thud"]},
                              {"from": "P02", "to": "L45", "keep": ["creak"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
