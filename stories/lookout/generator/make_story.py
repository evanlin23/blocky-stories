"""Writes ../story.json for ep16 "Lookout" (redo 2, 2026-11-02): in this valley time runs slower the higher up you are.

Run from anywhere: python stories/lookout/generator/make_story.py
The words are in lines.json next to this file (every line of the script, exactly). Everything else is here: the
cast, the shots, the acting, the cues set.py reads, the effects, the score and the sound. Every shot starts on a line
reference, never a rounded time.

Places (set.py's coordinates): the tower stands on (0, 0), the ground at its foot is z = 0, the cab's floor is
CAB_Z = 19.6. The valley falls away south (y < 0); the town's night lights lie on its floor near (0, -560); the
ranger's hut is on the far ridge near (-120, -900). The day town is a separate slab at (1200, 0). A character
facing -y has yaw 0, facing +x yaw 90, facing -x yaw -90, facing +y yaw 180.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

Z = 19.6
A = 1.45
RISE = Z / 112
PL = 3.2
TX = 1200.0


def tw(x, y, z=0.0):
    return [TX + x, y, z]


def mv(p0, t0, l0, p1=None, t1=None, l1=None, roll=0.0):
    if p1 is None:
        return [[0, p0, t0, l0, roll]]
    return [[0, p0, t0, l0, roll], [1, p1, t1 if t1 is not None else t0, l1 if l1 is not None else l0, roll]]


def stair_corner(k):
    order = [(-A, -A), (-A, A), (A, A), (A, -A)]
    x, y = order[k % 4]
    return [x, y, round(Z - k * 14 * RISE, 3)]


# ---------------------------------------------------------------------------------------------------- the cast
FACE = {"eyes": "round", "brows": True, "ink": "#16100c"}
cast = {
    "me": {"age": "adult", "skin": "#b5794e", "shirt": "#2a56c6", "pattern": "plaid", "pattern_c": "#141821",
           "collar": "#101216", "pants": "#2e2924", "shoes": "#a8733a", "sleeves": "long", "hair": "cap",
           "hair_c": "#121214", "hat": "hood", "hat_c": "#4b4e57", "face": dict(FACE)},
    # my brother as a teen: a head shorter, a red knit beanie, a mustard rain jacket over grey, a quick grin
    "ollie": {"age": "teen", "skin": "#b5794e", "shirt": "#d9a21b", "collar": "#8a8f96", "pants": "#262a33",
              "shoes": "#f2efe6", "sleeves": "long", "hair": "cap", "hair_c": "#3a2415", "hat": "beanie",
              "hat_c": "#c0392b", "extras": ["coat"], "height": 0.84, "face": dict(FACE)},
    # the same face twenty years on: taller than me, a beard going grey, a faded beanie, a ranger's green jacket
    "ollie_old": {"age": "adult", "skin": "#b5794e", "shirt": "#2f4a38", "collar": "#1c2a21", "pants": "#2b2b2b",
                  "shoes": "#3a2c20", "sleeves": "long", "hair": "cap", "hair_c": "#3a2415", "hat": "beanie",
                  "hat_c": "#c98a8a", "extras": ["coat"], "height": 1.1, "face": dict(FACE)},
    "balcony": {"age": "adult", "skin": "#d9a074", "shirt": "#f2d94e", "pants": "#6b5b7b", "shoes": "#8a5a3a",
                "sleeves": "long", "hair": "long", "hair_c": "#5a3a22", "face": {"eyes": "lashes", "brows": True, "ink": "#2a1a12"}},
    "walker": {"age": "adult", "skin": "#e3b58a", "shirt": "#2f6fb5", "pants": "#3a3a40", "shoes": "#222222",
               "sleeves": "long", "hair": "spiky", "hair_c": "#222222", "extras": ["coat"], "face": {"eyes": "round", "brows": True, "ink": "#1a1410"}},
    "grandad": {"age": "adult", "skin": "#e8c19c", "shirt": "#8f6b4b", "pattern": "knit", "pattern_c": "#7a5a3d",
                "pants": "#4a4038", "shoes": "#3a2c20", "sleeves": "long", "hair": "cap", "hair_c": "#1a1a1a",
                "face": {"eyes": "round", "brows": True, "ink": "#1a1410"}},
    "son": {"age": "adult", "skin": "#c98e62", "shirt": "#5f7f3f", "pants": "#4c4a3c", "shoes": "#5a4630",
            "sleeves": "long", "hair": "cap", "hair_c": "#b4b4b0", "face": {"eyes": "round", "brows": True, "ink": "#1a1410"}},
    "cellarman": {"age": "adult", "skin": "#a8693f", "shirt": "#6a6f7a", "pants": "#3a3a3a", "shoes": "#222222",
                  "sleeves": "long", "hair": "buzz", "hair_c": "#3a2c20", "face": {"eyes": "round", "brows": True, "ink": "#1a1410"}},
    "office1": {"age": "adult", "skin": "#e8c19c", "shirt": "#f0f0f0", "pants": "#2c3550", "shoes": "#222222",
                "sleeves": "long", "hair": "swoop", "hair_c": "#6a3b1c", "extras": ["tie"], "extra_c": "#a02c2c",
                "face": {"eyes": "round", "brows": True, "ink": "#1a1410"}},
    "office2": {"age": "adult", "skin": "#8c5a38", "shirt": "#b7c9e8", "pants": "#2c3550", "shoes": "#222222",
                "sleeves": "long", "hair": "buzz", "hair_c": "#1a1a1a", "extras": ["glasses", "tie"], "extra_c": "#20242c",
                "face": {"eyes": "round", "brows": True, "ink": "#1a1410"}},
    "office3": {"age": "adult", "skin": "#d9a074", "shirt": "#c9b3e0", "pants": "#3a3a40", "shoes": "#222222",
                "sleeves": "long", "hair": "bun", "hair_c": "#2a1d15", "face": {"eyes": "lashes", "brows": True, "ink": "#2a1a12"}},
}

# ---------------------------------------------------------------------------------------------------- places
def at_floor(p, z=Z):
    return [p[0], p[1], z]


GLASS_S = at_floor([0.4, -1.55])
GLASS_E = at_floor([1.45, -1.25])
GLASS_N = at_floor([-0.8, 1.0])
RADIO_AT = at_floor([0.8, 1.0])
COT_ME = [1.52, 0.95, Z - 0.03]          # sitting on the cot, my thighs on its top
COT_OLD = [1.52, -0.35, Z - 0.03]
COT1 = [1.52, 0.3, Z - 0.03]
CORNER_NW = at_floor([-1.35, 0.4])
FAR_GLASS = at_floor([-1.45, 0.2])
DOOR_OUT = [-2.5, 0.0, Z]
LAMP_TABLE = [-0.5, 1.5, Z + 0.76]
LAMP_COT = [1.5, -0.55, Z + 0.48]
LAMP_HAND = {"hand": "me.arm-1", "offset": [0.0, 0.0, -0.56]}
HOLD = dict(arms=[20, 0])
HIGH = dict(arms=[155, 0])
RAILS = dict(arms=[82, 82])
BINO = dict(arms=[102, 102])
GATE_Y = -2.05

# ---------------------------------------------------------------------------------------------------- the shots
# Each shot: id-less dict. "at" a line ref, "cam", "look" (set.py LOOKS), "night" (1..3), "who" {name: state}, "lamp"
# ("table" | "cot" | "hand" | [x, y, z]), "binos" (me holds the binoculars), "cues" (extras)
S = []


def shot(at, cam, look, who=None, lamp="table", **kw):
    S.append(dict(at=at, cam=cam, look=look, who=who or {}, lamp=lamp, **kw))


def st(pos, yaw=0, expr="neutral", **kw):
    return dict(pos=pos, yaw=yaw, expr=expr, **kw)


BAL = st([TX + 0.0, -1.45, 2.4], 0, "smile", **RAILS, head=[0, 0])
WALK = st(tw(-1.3, -3.3), 10, "wide", arms=[0, 0], head=[0, 14])
# ---- 01 the rule: a noon street (0 to about 20 s)
shot(0, mv(tw(0.2, -11.8, 1.6), tw(-0.2, -2.4, 3.0), 28, tw(0.1, -10.8, 1.7), tw(-0.2, -2.4, 3.1), 28), "town",
     {"balcony": BAL, "walker": WALK}, sand=[("balcony", 0.1), ("walker", 0.95)], hand=0.003)
shot("L01.2", mv(tw(-0.3, -8.0, 2.8), tw(-0.6, -2.4, 3.8), 30, tw(-0.3, -7.4, 2.9), tw(-0.6, -2.4, 3.9), 30), "town",
     {"balcony": BAL, "walker": WALK})
shot("L02", mv(tw(-24, -9, 1.7), tw(-12, -1.5, 1.8), 22, tw(14, -9, 1.7), tw(24, -1.5, 2.0), 22), "town",
     {"balcony": BAL, "walker": WALK,
      "grandad": st(tw(31, 5.2, 4.05), 0, "grin", arms=[0, 150]),
      "son": st(tw(33, 2.0), 0, "smirk")})
shot("L03", mv(tw(31, -0.5, 3.0), tw(31.0, 5.0, 5.1), 40, tw(31, -0.2, 3.1), tw(31.0, 5.0, 5.2), 40), "town",
     {"grandad": st(tw(31, 5.2, 4.05), 0, "grin", arms=[0, 150])})
shot("L03.2", mv(tw(34.2, -1.8, 1.5), tw(33.0, 2.0, 1.5), 30, tw(34.0, -1.5, 1.5), tw(33.0, 2.0, 1.6), 30), "town",
     {"son": st(tw(33, 2.0), 0, "smirk", arms=[40, 40], head=[0, -8]),
      "grandad": st(tw(31, 5.2, 4.05), 0, "grin", arms=[0, 150])}, sand=[("son", 0.8)])
shot("L04", mv(tw(60, -10.0, -1.9), tw(60, -2.5, -1.8), 24, tw(60, -9.0, -1.9), tw(60, -2.5, -1.7), 24), "town",
     {"cellarman": st(tw(60, -3.0, -PL + 0.1), 0, "worried", sit=True, arms=[30, 0])})
shot("L04.2", mv(tw(60, -6.5, 1.7), tw(60, -2.2, 0.3), 30, tw(60, -6.0, 1.6), tw(60, -2.2, 0.3), 30), "town",
     {}, parcel=True)
shot("L05", mv(tw(86, -11.0, -1.9), tw(88, -2.5, -1.8), 22, tw(92, -11.0, -1.9), tw(92, -2.5, -1.8), 22), "town",
     {"office1": st(tw(79, -2.0, -PL), 0, "grin"), "office2": st(tw(91, -2.0, -PL), 0, "grin"),
      "office3": st(tw(97, -2.0, -PL), 0, "grin")})
shot("L05.2", mv(tw(93, -7.5, -1.9), tw(94, -2.4, -1.8), 28), "town",
     {"office2": st(tw(91, -2.0, -PL), 0, "grin"), "office3": st(tw(97, -2.0, -PL), 0, "laugh")})
# ---- the lookout (L06 to L12)
shot("L06", mv([26, -75, 12], [0, 0, 13], 34, [22, -70, 12.5], [0, 0, 13.5], 36), "clear", {})
shot("L06.1", mv([-1.4, -7.2, 1.45], [-2.1, -2.2, 1.3], 26), "clear",
     {"me": st([-2.1, -3.2, 0.0], 0, "smile", arms=[0, 0])}, sand=[("me", 0.3)])
shot("L07", mv([3.0, -6.0, 1.0], [0.0, 0.0, 11.0], 20, [3.0, -6.0, 1.0], [0.0, -1.0, 19.0], 20), "clear", {})
shot("L07.3", mv([3.0, 3.4, 9.5], [-0.4, -0.2, 17.0], 24, [3.0, 3.4, 12.5], [-0.4, -0.2, 20.2], 24), "clear", {})
shot("L08", mv([-2.2, -8.4, 1.4], [-2.2, -2.2, 1.7], 30), "clear",
     {"me": st([-1.7, -3.3, 0.0], 0, "smile"), "ollie": st([-2.85, -3.3, 0.0], 0, "grin")},
     sand=[("me", 0.3)])
shot("L09", mv([-2.7, -6.6, 1.5], [-2.85, -3.3, 1.9], 36), "clear",
     {"ollie": st([-2.85, -3.3, 0.0], 0, "smile")}, flap=("ollie", "L09", "L09>"))
shot("L10", mv([-1.6, -8.0, 1.5], [-2.6, -3.4, 1.7], 30), "clear",
     {"ollie": st([-2.85, -3.4, 0.0], 0, "smile", side=[0, 95]), "me": st([-1.7, -3.2, 0.0], 0, "smile")},
     flap=("ollie", "L10", "L10>"))
shot("L10.2", mv([-3.4, -3.0, 1.7], [-1.0, -90.0, -20.0], 30), "clear", {"ollie": st([-2.9, -3.5, 0.0], 0, "grin", arms=[0, 100])},
     flap=("ollie", "L10.2", "L10>"))
shot("L11", mv([-2.3, -9.0, 1.4], [-2.4, -2.2, 1.1], 26), "clear",
     {"me": st([-2.2, -1.2, 0.0], 0, "smile"), "ollie": st([-3.9, -4.6, 0.0], 0, "grin", arms=[0, 160])},
     gate=("L11", 0.0, 0.6))
shot("L11.2", mv([-1.1, -3.3, 1.0], [-1.55, -2.1, 0.88], 60), "clear", {}, padlock=False)
shot("L12", mv([-0.9, 1.5, 21.6], [-1.95, 1.0, 21.25], 26), "clear", {})
# ---- 02 the nights (L13 to L21)
shot("L13", mv([14.0, -14.0, 22.0], [0.0, 0.0, 21.0], 28, [12.5, -12.5, 22.0], [0.0, 0.0, 21.0], 30), "nighthigh", {},
     lamp="cot")
shot("L13.2", mv([0.9, -4.7, 21.4], [0.45, -1.5, 21.15], 30), "night",
     {"me": st(GLASS_S, 0, "neutral", **HIGH)}, lamp="hand", sand=[("me", 0.06)])
shot("L14", mv([0.4, -1.5, 21.15], [30.0, -560.0, -148.0], 80), "nightbino", {}, night=1,
     ollie=("win", 0.2, 1.2))
shot("L14.3", mv([0.9, -4.7, 21.4], [0.45, -1.5, 21.15], 30), "night",
     {"me": st(GLASS_S, 0, "smile", **HOLD)}, lamp="hand", night=1)
shot("L15", mv([0.5, 0.2, 21.0], [0.4, 1.6, 20.8], 30), "night", {}, radio_on=("L15", "L15.3"))
shot("L16", mv([0.4, -1.5, 21.15], [30.0, -560.0, -148.0], 80), "nightbino", {}, night=1)
shot("L16.2", mv([-1.3, -1.2, 21.1], [1.4, 0.3, 20.6], 26), "night",
     {"me": st(COT1, -90, "puzzled", sit=True, arms=[0, 0])}, lamp="cot", sand=[("me", 0.06)])
shot("L17", mv([0.4, -1.5, 21.15], [-410.0, -640.0, -125.0], 70), "nightbino", {}, night=2, ollie=("win2", 0.0, 1.0))
shot("L17.3", mv([0.9, -4.7, 21.4], [0.0, -1.5, 21.15], 30), "night",
     {"me": st(GLASS_S, 0, "worried", arms=[0, 0])}, night=2)
shot("L18", mv([-2.6, -2.2, 22.2], [-2.6, -9.0, 14.0], 40), "night", {}, night=2)
shot("L19", mv([0.5, -2.7, 21.9], [10.0, -560.0, -120.0], 22), "nightvalley", {}, night=3)
shot("L20", mv([0.4, -1.5, 21.15], [-120.0, -891.0, -20.0], 100), "nightbino", {}, night=3, ollie=("hut", 0.0, 1.0))
shot("L20.4", mv([0.9, -4.7, 21.4], [0.4, -1.5, 21.15], 30), "night",
     {"me": st(GLASS_S, 0, "worried", **BINO)}, night=3, binos="me.arm-1")
shot("L21", mv([-3.4, -2.2, 20.9], [-1.6, -4.9, 20.4], 24), "night", {}, night=3, scrape=True)
shot("L21.2", mv([1.3, 0.4, 21.2], [0.0, -1.8, 20.6], 30), "night",
     {"me": st(GLASS_S, 0, "scared", arms=[0, 0], head=[0, -10])}, night=3)
# ---- 03 the fourth night (L22 to L33)
shot("L22", mv([-0.9, 1.0, 21.2], [0.55, 1.8, 20.9], 30), "night", {}, night=4, radio_on=("L22", "L24>+0.3"))
shot("L23", mv([-0.6, -1.2, 21.1], [0.5, 0.9, 20.5], 26), "night",
     {"me": st(GLASS_N, 180, "worried", **HOLD)}, lamp="hand", night=4)
shot("L24", mv([0.7, 0.3, 21.0], [0.45, 1.8, 20.9], 40), "night", {}, night=4)
shot("L25", mv([-0.8, -0.1, 21.3], [0.4, 1.0, 20.9], 30), "night",
     {"me": st(GLASS_N, 180, "terrified", **HOLD)}, lamp="hand", night=4)
shot("P01", mv([0.5, -1.0, 21.2], [-120.0, -891.0, -20.0], 60), "nightvalley", {}, night=4, ollie=("hut", 0.0, 0.01))
shot("L26", mv([0.4, -1.5, 21.15], [-120.0, -891.0, -20.0], 100), "nightbino", {}, night=4, mover="L26")
shot("L27", mv([0.5, -2.7, 21.9], [-40.0, -450.0, -120.0], 22), "nightvalley", {}, night=4)
shot("L27.3", mv([0.5, -2.7, 21.5], [-2.0, -90.0, -10.0], 24, [0.5, -2.7, 21.5], [-2.3, -50.0, -6.0], 24), "nightvalley", {},
     night=4)
shot("L28", mv([-3.4, -6.2, 0.8], [-2.25, -2.1, 0.7], 30), "night", {}, night=4, padlock=True, gate=("L28.2", 1.0, 0.5))
shot("L29", mv([-1.2, -0.9, 20.4], [-1.45, -1.45, 17.5], 26), "night", {}, night=4)
shot("L30", mv([1.1, 0.7, 21.1], [-1.4, -1.3, 20.2], 22), "night",
     {"me": st(at_floor([1.2, 0.9]), 0, "terrified", arms=[20, 85])}, lamp="hand", night=4)
shot("L30.3", mv([0.3, 0.4, 21.0], [-2.0, 0.0, 20.2], 24), "night", {}, night=4, mover="door")
shot("P02", mv([0.1, 0.0, 21.0], [-2.0, 0.0, 20.6], 30), "night",
     {"me": st(at_floor([1.2, 0.9]), 180, "terrified", **HOLD)}, lamp="hand", night=4, door=("P02", 1.0, 0.5))
shot("L31", mv([0.2, 0.3, 20.95], [-2.4, 0.0, 20.75], 26), "night",
     {"ollie_old": st([-2.5, 0.0, Z], 90, "neutral", arms=[25, 0], head=[0, -4]),
      "me": st(at_floor([1.2, 0.9]), 180, "terrified", **HOLD)}, lamp="hand", night=4, lamp2=True)
shot("L32", mv([-1.55, 0.05, 22.0], [-2.5, 0.0, 22.0], 36), "night",
     {"ollie_old": st([-2.5, 0.0, Z], 90, "neutral", arms=[25, 0], head=[0, -4])}, night=4, lamp2=True)
shot("L33", mv([-0.9, 0.0, 20.9], [-2.5, 0.0, 20.95], 30), "night",
     {"ollie_old": st([-2.5, 0.0, Z], 90, "neutral", arms=[125, 0], head=[0, 0])}, night=4, lamp2=True)
shot("P03", mv([-0.7, 0.0, 21.15], [-2.5, 0.0, 21.15], 36), "night",
     {"ollie_old": st([-2.5, 0.0, Z], 90, "neutral", arms=[125, 0], head=[0, 0])}, night=4, lamp2=True)
# ---- 04 the reveal (L34 to the end)
shot("L34", mv([-0.5, 0.0, 21.2], [-2.5, 0.0, 21.2], 34), "night",
     {"ollie_old": st([-2.5, 0.0, Z], 90, "soft", arms=[125, 0])}, night=4, lamp2=True)
shot("L35", mv([-0.3, -2.0, 21.2], [-1.0, 0.0, 21.0], 22), "night",
     {"ollie_old": st([-1.55, 0.0, Z], 90, "soft", arms=[25, 0]), "me": st(at_floor([-0.3, 0.9]), -90, "wide", **HOLD)},
     lamp="hand", night=4, lamp2=True, door=("L35", 1.0, 0.1))
shot("L36", mv([0.5, -0.5, 21.4], [0.0, -560.0, -120.0], 24), "nightvalley", {}, night=3)
shot("L36.3", mv([-0.8, -1.4, 21.15], [-0.3, 0.5, 21.15], 34), "night",
     {"me": st(at_floor([-0.3, 0.9]), 0, "wide", **HOLD)}, lamp="hand", night=3)
shot("L37", mv([0.4, -1.5, 21.15], [30.0, -560.0, -148.0], 80), "nightbino", {}, night=1, ollie=("win", 0.0, 0.3))
shot("L38", mv([-1.7, -0.3, 21.2], [-2.5, 0.0, 21.1], 32), "night",
     {"ollie_old": st([-1.55, 0.0, Z], 90, "soft", arms=[25, 0], head=[0, -4])}, night=4, lamp2=True)
shot("L38.3", mv([0.5, -1.5, 21.15], [20.0, -560.0, -148.0], 60), "nightvalley", {}, night=1)
shot("L39", mv([-0.4, -2.3, 21.6], [-120.0, -560.0, -80.0], 20, [0.0, -2.3, 21.6], [-60.0, -600.0, -90.0], 20), "nightvalley", {}, night=3, ollie=("hut", 0.0, 0.01))
shot("L39.3", mv([0.4, -1.5, 21.15], [-120.0, -891.0, -20.0], 100), "nightbino", {}, night=3, ollie=("hut", 0.0, 0.01))
shot("L40", mv([-0.2, -1.8, 21.9], [0.9, 0.5, 21.9], 22), "night",
     {"ollie_old": st([-0.4, 0.2, Z], 90, "soft", arms=[0, 0]), "me": st(at_floor([0.6, 0.2]), -90, "soft", arms=[0, 0])},
     night=3, lamp="table")
shot("L41", mv([-1.6, -1.2, 20.35], [-1.4, 0.1, 19.95], 40), "night",
     {"ollie_old": st([-1.2, 0.5, Z], 90, "soft", arms=[0, 0])}, night=3, lamp2=True)
shot("L41.3", mv([-1.2, 0.1, 21.5], [-1.97, 1.0, 21.15], 40), "night", {}, night=3)
shot("L42", mv([-0.6, 0.45, 21.2], [1.55, 0.3, 20.7], 24), "night",
     {"ollie_old": st(COT_OLD, -90, "smile", sit=True), "me": st(COT_ME, -90, "soft", sit=True)},
     lamp=[1.2, 0.3, Z + 0.48], night=3)
shot("L43", mv([-0.1, 0.3, 21.4], [1.55, 0.3, 21.9], 30), "night",
     {"ollie_old": st(COT_OLD, -90, "smile", sit=True), "me": st(COT_ME, -90, "soft", sit=True)},
     lamp=[1.2, 0.3, Z + 0.48], night=3, sand=[("me", 0.06), ("ollie_old", 0.06)])
shot("P04", mv([-1.2, 0.3, 21.15], [1.55, 0.3, 20.7], 26, [-0.9, 0.3, 21.15], [1.55, 0.3, 20.75], 26), "night",
     {"ollie_old": st(COT_OLD, -90, "smile", sit=True), "me": st(COT_ME, -90, "soft", sit=True)},
     lamp=[1.2, 0.3, Z + 0.48], night=3)
shot("L44", mv([14.0, -14.0, 22.0], [0.0, 0.0, 21.0], 28, [12.5, -12.5, 22.0], [0.0, 0.0, 21.0], 30), "nighthigh",
     {}, lamp="cot", night=3)
shot("L44.3", mv([8.0, -8.0, 21.8], [0.0, 0.0, 21.0], 30, [6.5, -6.6, 21.6], [0.0, 0.0, 21.0], 32), "nighthigh",
     {}, lamp="cot", night=3)
shot("L45", mv([0.5, -2.7, 21.9], [10.0, -560.0, -120.0], 22), "nightvalley", {}, night=3, shift=True)
shot("L46", mv([0.4, -2.2, 21.3], [0.4, -1.5, 21.15], 30), "night",
     {"me": st(GLASS_S, 0, "soft", arms=[0, 0])}, night=3)

# ---------------------------------------------------------------------------------------------------- build
shots = []
acting = {k: [] for k in cast}
cues = []
fx = []
vis = {k: False for k in cast}
last = {}


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


for k in cast:
    key(k, 0, pos=[0, 0, -60], hidden=True, yaw=0, expr="neutral")
    last[k] = [0, 0, -60]

lamp_cue = None
for i, s in enumerate(S):
    sid = f"S{i + 1:02d}"
    at = s["at"]
    d = {"id": sid, "cam": s["cam"], "step": 2}
    if i:
        d["at"] = at
    if s.get("hand") is not None:
        d["hand"] = s["hand"]
    shots.append(d)
    t_at = at if i else 0
    for who in cast:
        st_ = s["who"].get(who)
        if st_ is None:
            if vis[who]:
                key(who, t_at, pos=last[who], hidden=True)
                vis[who] = False
            continue
        extra = {k2: v for k2, v in st_.items() if k2 not in ("pos", "yaw", "expr")}
        base = {"pos": st_["pos"], "yaw": st_["yaw"], "expr": st_["expr"], "blend": 0.0}
        if "sit" not in extra:
            extra["sit"] = False
        extra.setdefault("arms", [0, 0])
        extra.setdefault("head", [0, 0])
        if i:
            key(who, t_at, pos=last[who] if vis[who] else st_["pos"])
        key(who, t_at, **base, hidden=False, **extra)
        last[who] = st_["pos"]
        vis[who] = True
    # cues: look, night, lamp, sand
    cues.append({"at": t_at, "name": "look", "id": s["look"]})
    cues.append({"at": t_at, "name": "night", "n": s.get("night", 1)})
    lp = s["lamp"]
    if lp == "hand":
        cues.append({"at": t_at, "name": "lamp", **LAMP_HAND})
    elif lp == "table":
        cues.append({"at": t_at, "name": "lamp", "pos": LAMP_TABLE})
    elif lp == "cot":
        cues.append({"at": t_at, "name": "lamp", "pos": LAMP_COT})
    else:
        cues.append({"at": t_at, "name": "lamp", "pos": lp})
    cues.append({"at": t_at, "name": "binos", "hand": s.get("binos")})
    cues.append({"at": t_at, "name": "lamp2", "hand": "ollie_old.arm-1", "offset": [0.0, 0.0, -0.55]} if s.get("lamp2")
                else {"at": t_at, "name": "lamp2", "hand": None})
    cues[-1]["at"] = t_at
    for who, v in s.get("sand", []):
        cues.append({"at": t_at, "name": "sand", "who": who, "v": v})
    if s.get("parcel"):
        cues.append({"at": t_at + 0 if isinstance(t_at, (int, float)) else t_at, "name": "parcel", "on": True})
    if s.get("ollie"):
        w, _x, dur = s["ollie"]
        cues.append({"at": t_at, "name": "ollie", "where": w, "dur": dur})
    if s.get("padlock") is not None:
        cues.append({"at": t_at, "name": "padlock", "open": bool(s["padlock"])})
    if s.get("gate"):
        ref, op, dur = s["gate"]
        cues.append({"at": ref, "name": "gate", "open": op, "dur": dur})
    if s.get("door"):
        ref, op, dur = s["door"]
        cues.append({"at": ref, "name": "door", "open": op, "dur": dur})
    if s.get("flap"):
        who, a, b = s["flap"]
        acting[who].append({"from": a, "to": b, "mouth": [0.7, 0.7], "flap": True})
    if s.get("radio_on"):
        a, b = s["radio_on"]
        cues.append({"at": a, "name": "radio", "on": True})
        cues.append({"at": b, "name": "radio", "on": False})

# the gate is shut and the lock hangs shut until the shots that open them
cues.insert(0, {"at": 0, "name": "gate", "open": 1.0, "dur": 0.0})
cues.insert(0, {"at": 0, "name": "door", "open": 0.0, "dur": 0.0})
cues.insert(0, {"at": 0, "name": "padlock", "open": False})
cues.insert(0, {"at": 0, "name": "parcel_reset"})

# the lamp that crosses the valley, then climbs the stairs (L26 to L30)
hut_win = [-118.0, -891.4, -19.8]
path = [("L26", hut_win, 3.2, 0.0), ("L26.2", [-90.0, -700.0, -135.0], 3.2, 1.3), ("L27", [-30.0, -450.0, -146.0], 3.0, 1.4),
        ("L27.1", [-4.0, -200.0, -34.0], 2.0, 1.3), ("L27.3", [-2.4, -60.0, -8.0], 0.7, 0.9),
        ("L28", [-2.4, -9.0, 1.2], 0.14, 0.9), ("L28.2", [-2.25, -3.4, 1.0], 0.12, 0.4), ("L28.2+0.45", [-2.25, -1.4, 1.1], 0.12, 0.5)]
for ref, pos, r, dur in path:
    cues.append({"at": ref, "name": "mover", "pos": pos, "r": r, "dur": dur, "on": True})
# up the stairs, flight by flight (the glow rises as the steps do), 8 flights over L29 to L30>
for f in range(8):
    a, b = stair_corner(f), stair_corner(f + 1)
    cues.append({"at": f"L29+{f * 0.45:.2f}", "name": "mover", "pos": [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2 + 1.1],
                 "r": 0.12, "dur": 0.45, "on": True})
cues.append({"at": "L30.3", "name": "mover", "pos": [-2.5, 0.0, Z + 1.0], "r": 0.12, "dur": 0.4, "on": True})
cues.append({"at": "P02", "name": "mover", "pos": [-2.5, 0.0, -80.0], "r": 0.12, "dur": 0.0, "on": False})
# the hut's own window goes dark as the lamp leaves it
cues.append({"at": "L26", "name": "ollie", "where": "none", "dur": 0.4})
cues = [c for c in cues if c["name"] != "parcel_reset"]
# the parcel only drops once
seen = False
out_cues = []
for c in cues:
    if c["name"] == "parcel":
        if seen:
            continue
        seen = True
    if c["name"] == "binos" and c.get("hand") is None:
        c = {"at": c["at"], "name": "binos", "hand": None}
    out_cues.append(c)
cues = out_cues
cues.sort(key=lambda c: 0 if c["at"] == 0 else 1)

# me, once: the mouth of Ollie and his hands are acted above. Sand for the town stays at its default values.
cues += [{"at": "L08", "name": "sand", "who": "me", "v": 0.3}, {"at": "L12", "name": "sand", "who": "me", "v": 0.06},
         {"at": "L08", "name": "sand", "who": "ollie", "v": 0.95}]

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L15", "kind": "radio", "db": -15}, {"at": "L15.3", "kind": "click", "db": -13},
    {"at": "L22", "kind": "radio", "db": -15}, {"at": "L24>+0.2", "kind": "click", "db": -13},
    {"at": "L21+0.1", "kind": "whoosh", "db": -20, "dur": 0.8}, {"at": "L21+0.6", "kind": "whoosh", "db": -20, "dur": 0.8},
    {"at": "L28.2", "kind": "hit", "db": -14}, {"at": "L28.2+0.05", "kind": "creak", "db": -16, "dur": 0.7},
    {"at": "P02", "kind": "door", "db": -12, "keep": True},
    {"at": "P02+0.35", "kind": "hit", "db": -9, "keep": True},
    {"at": "P03", "kind": "sting", "db": -11, "dur": 1.6, "keep": True},
]
for k in range(9):          # heavy, slow wood steps up the 112 stairs, L29 to the door
    sfx.append({"at": f"L29+{k * 0.42:.2f}", "kind": "thud", "db": -9 if k % 2 == 0 else -11})
    sfx.append({"at": f"L29+{k * 0.42:.2f}", "kind": "creak", "db": -20, "dur": 0.4})
story = {
    "slug": "ep16-lookout",
    "title": "In This Valley Time Runs SLOWER the Higher You Are",
    "made_for_kids": False,
    "premise": "In a valley where time runs slower the higher up you are, I take a one-week shift alone in the fire lookout on the highest ridge. My brother Ollie, still a teenager, walks me to the gate and makes me promise to flash my lamp at ten every night so he can flash back. His window light answers, then never goes dark, and each night it's somewhere higher up the valley.",
    "twist": "The tall stranger who climbs my 112 stairs on the fourth night is Ollie, older than me now: four nights for me were twenty years for him. His window never went dark because he flashed it every night, seven thousand times, and from up here it blurred into one light. Every year he moved a little higher to slow his own sand, so he would never get too far ahead of me, and he became the ranger to get the other key.",
    "world": "A valley town of blocky houses in noon sun with an hourglass of falling sand over every head, and above it, on the highest ridge, a fire lookout: a glass cab on steel legs 112 stairs up, a catwalk, a lamp, a radio, autumn pines that grow taller each night, and the town's lights spreading below in the fog.",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffb22e",
    "gap": 0.12,
    "tail": 0.25,
    "look": {"fog": "#2a3238", "fog_density": 0.034, "fog_start": 3.0, "sky": "#2a3238", "exposure": 1.6,
             "flash_safe": True},
    "grade": {"shadows": [-0.02, 0.01, 0.02], "highlights": [0.04, 0.015, -0.03], "saturation": 0.95,
              "contrast": 1.06, "vignette": 0.3, "bloom": 0.4, "grain": 0.012, "red_line": 0.79},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    "music": {"root": 40, "mode": "dorian", "bpm": 72, "seed": 16,
              "sections": [
                  {"at": 0, "voices": ["pad", "piano"], "energy": 0.4},
                  {"at": "L13", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L24", "voices": ["drone", "pad"], "energy": 0.75},
                  {"at": "L28", "voices": ["drone", "pad", "pulse"], "energy": 0.8},
                  {"at": "L31", "voices": ["drone", "pad"], "energy": 0.6},
                  {"at": "L42", "voices": ["drone", "pad", "piano"], "energy": 0.45},
                  {"at": "L45", "voices": ["drone"], "energy": 0.5},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "L13", "lufs": -38},
                  {"kind": "wind", "from": "L13", "to": "end", "lufs": -37},
                  {"kind": "static", "from": "P01", "to": "L26", "lufs": -42},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P02", "to": "L31", "keep": ["door", "hit"]},
                              {"from": "P03", "to": "L34", "keep": ["sting"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
