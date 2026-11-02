"""Writes ../story.json for ep36 "ice-huts" (script.md in the story folder).

Run from anywhere: python stories/ep36-ice-huts/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (fog ramps, where each flame leans, the door, the lamp, the curtain, breath), the score
and the sound. Every light change is a slow ramp (look.flash_safe is on), and the flames are steady.

Places (set.py's metres): the shore is x = 0, the lake is x > 0, the town street is x = -30. The red hut is at (30, 4).
In hut shots, H(x, y, z) is local to the hut's middle. A character with yaw 0 faces -y, yaw 90 faces +x.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
for ln in lines:                       # the spoken text keeps the names capitalised
    for ch in ln["chunks"]:
        ch[1] = ch[1].replace("grandad", "Grandad")

# the word check: spoken-only respellings (the captions don't change)
SPOKEN = {("L06", 1): "at the curb", ("L61", 1): "round it,"}
TEMPO = {"L10": 0.9, "L61": 0.95}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]
    for k, ch in enumerate(ln["chunks"]):
        if (ln["id"], k) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], k)]

# pause beats (silent, 0.6 to 1.2 s) after these lines, then the loop gap
PAUSES = {"L17": 0.8, "L31": 0.7, "L36": 0.7, "L42": 0.9, "L45": 0.8, "L58": 0.8, "L62": 0.8}
lines2 = []
for ln in lines:
    lines2.append(ln)
    if ln["id"] in PAUSES:
        lines2.append({"id": "P" + ln["id"][1:], "pause": PAUSES[ln["id"]], "chunks": []})
lines = lines2 + [{"id": "P99", "pause": 0.25, "chunks": []}]

RED = (30.0, 4.0)
CAR = (200.0, -150.0)


def H(x, y, z=0.0):
    return [RED[0] + x, RED[1] + y, z]


def C(x, y, z=0.0):
    return [CAR[0] + x, CAR[1] + y, z]


def yaw_to(a, b):
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


def still(loc, tgt, lens):
    return [[0, list(loc), list(tgt), lens]]


def move(a, b, lens_a, lens_b=None):
    return [[0, list(a[0]), list(a[1]), lens_a], [1, list(b[0]), list(b[1]), lens_b or lens_a]]


# ---------------------------------------------------------------------------------------------------- cast
def person(skin, shirt, pants, hair="cap", hair_c="#2a1d15", hat="none", hat_c="#333333", extras=(), height=1.0,
           width=0.88, pattern="solid", pattern_c="#202020", eyes="round", brows=True, shoes="#3a2a20", extra_c=None,
           sleeves="long", age="adult", collar=None):
    d = {"age": age, "skin": skin, "shirt": shirt, "pattern": pattern, "pattern_c": pattern_c, "pants": pants,
         "shoes": shoes, "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c,
         "extras": list(extras), "height": height, "width": width, "face": {"eyes": eyes, "brows": brows, "ink": "#161012"}}
    if extra_c:
        d["extra_c"] = extra_c
    if collar:
        d["collar"] = collar
    return d


cast = {
    "me": person("#d9a77c", "#5b2a55", "#2b2a30", hair="cap", hair_c="#3a2418", hat="beanie", hat_c="#2f3034",
                 extras=["scarf"], extra_c="#8c9094", width=0.78, shoes="#2a2420", collar="#4a2046"),
    "grandad": person("#e2b693", "#e8dfc8", "#4a3f36", hair="buzz", hair_c="#f0f0ee", hat="beanie", hat_c="#c9a03a",
                      extras=["glasses", "coat"], pattern="plaid", pattern_c="#24304a", eyes="classic", height=0.95,
                      width=0.82, shoes="#4a3022", extra_c="#2a2c30"),
    "pell": person("#d8a888", "#b88a58", "#3b3128", hair="cap", hair_c="#5a4a3a", extras=["coat"], width=0.84,
                   shoes="#2a2420"),
    "date_w": person("#c98f6a", "#2f7f7a", "#2a2d33", hair="long", hair_c="#4a2c1c", extras=["coat"], width=0.84),
    "date_m": person("#e0b08a", "#6b4a2e", "#33302c", hair="swoop", hair_c="#2a1d15", pattern="stripes",
                     pattern_c="#5a3d26", width=0.84),
    "newcomer": person("#b98563", "#c0392b", "#2b2e36", hair="bun", hair_c="#1c1512", extras=["coat"], width=0.84),
    "owner": person("#e3b894", "#4c6a3c", "#3a3a40", hair="spiky", hair_c="#7a5a30", extras=["coat"], width=0.84),
    "driver": person("#c4906c", "#8a8e93", "#74787d", hair="buzz", hair_c="#222222", hat="ballcap", hat_c="#4a4d52",
                     width=0.84),
    "fisher1": person("#e0b08a", "#7a4a3a", "#2b2b30", hair="cap", hair_c="#3a2a20", hat="beanie", hat_c="#3d5a6a",
                      extras=["coat"], width=0.84),
    "fisher2": person("#c98f6a", "#3d5a6a", "#2b2b30", hair="long", hair_c="#2a1d15", hat="beanie", hat_c="#b9573a",
                      extras=["coat"], width=0.84),
    "fisher3": person("#e8c19e", "#6a6e4a", "#2b2b30", hair="buzz", hair_c="#7a7a7a", hat="fedora", hat_c="#4a3a2a",
                      extras=["coat"], width=0.84, height=1.08),
    "fisher4": person("#b98563", "#8a5a3a", "#2b2b30", hair="swoop", hair_c="#1a1512", hat="beanie", hat_c="#7a7e50",
                      extras=["coat"], width=0.84),
    "leaner": person("#7a4430", "#8e3b1f", "#16120f", hair="buzz", hair_c="#16120f", extras=["coat"], height=1.06,
                     width=0.62, shoes="#16120f", eyes="dot", brows=False),
}
cast["leaner"]["face"] = {"eyes": "dot", "brows": False, "ink": "#050404", "pupil": "#050404", "glow": "#cfe6ff"}
cast["leaner"]["zip_c"] = "#16120f"

# ---------------------------------------------------------------------------------------------------- shots
# Every shot: (id, at, where, camera, who is in it {name: placement}, flames {name: target}, extras)
# a placement: {"pos": [x, y], "yaw": deg or "to": [x, y] to face, ...acting keys (expr, head, arms, side, lean, z)}
# a flame target: [x, y] a place it leans toward | "shore" | "up" | "spin" | ("swing", at_ref, target)
SH = []
CUES = []
ACT = {k: [] for k in cast}


def shot(sid, at, where, cam, people, flames=None, **kw):
    SH.append(dict(id=sid, at=at, where=where, cam=cam, people=people, flames=flames or {}, **kw))


def P(pos, yaw=None, face=None, **kw):
    d = dict(pos=list(pos), **kw)
    if yaw is not None:
        d["yaw"] = yaw
    if face is not None:
        d["yaw"] = yaw_to(pos, face)
    return d


SIT = 0.25            # a seated body's drop: the hips sit on a stool or a chair
SHORE_PPL = {
    "me": P((1.3, -0.4), 0, expr="soft"),
    "fisher1": P((0.45, 0.35), 0, expr="soft"),
    "fisher2": P((2.25, 0.4), 0, expr="neutral"),
    "fisher3": P((1.35, 1.1), 0, expr="soft"),
}
SHORE_FL = {"me": list(RED), "fisher1": "shore", "fisher2": "shore", "fisher3": "shore"}

# 01 the hook and the montage
shot("S01", 0, "ice", still((2.0, -4.0, 1.62), (1.3, 0.5, 1.68), 26), SHORE_PPL, SHORE_FL)
shot("S02", "L01.2", "ice", still((-0.8, -1.0, 1.6), (14.0, 6.0, 1.5), 24),
     {"me": P((1.3, -0.4), 70, expr="soft"), "fisher1": P((0.45, 0.35), 70, expr="soft"),
      "fisher2": P((2.25, 0.4), 70), "fisher3": P((1.35, 1.1), 70)}, SHORE_FL)
shot("S03", "L02", "town", move(([-31.2, -6.0, 7.0], [-30, 3.0, 0.8]), ([-31.2, -4.0, 6.0], [-30, 5.0, 0.9]), 24),
     {"newcomer": P((-33.2, -1.0), 90), "owner": P((-27.3, 5.0), -90), "driver": P((-32.6, 11.0), 90),
      "date_m": P((-27.4, -1.0), -90), "date_w": P((-33.0, 5.5), 90)},
     {"newcomer": [-26, -1.5], "owner": [-42, 6.5], "driver": [-42, 14], "date_m": [-42, -3], "date_w": [-26, 8.0]})
shot("S04", "L03", "town", still((-31.5, 7.0, 1.5), (-27.0, 11.0, 1.4), 24),
     {"pell": P((-27.0, 9.4), 180, walk=[(1.6, (-27.0, 11.4))], expr="soft")},
     {"pell": [-22, 10.5]}, pell_leaves=False)
shot("S05", "L03.4", "town", still((-21.5, 11.6, 1.45), (-25.4, 11.0, 1.3), 28),
     {"pell": P((-24.5, 11.0), 90, expr="soft")}, {"pell": [-15, 11.0]}, pell_leaves=True, hedge_sway=True)
shot("S06", "L04", "town", still((-29.2, -3.0, 1.4), (-24.5, -3.0, 1.2), 28),
     {"date_w": P((-24.5, -3.75), 225, expr="soft", z=-SIT), "date_m": P((-24.5, -2.25), -45, expr="wide", z=-SIT)},
     {"date_w": [-24.5, 40], "date_m": [-24.5, 40]})
shot("S07", "L05", "town", still((-30.3, -7.2, 1.6), (-33.2, -4.4, 1.6), 28),
     {"newcomer": P((-33.2, -4.3), 20, expr="wide", head=[0, -10])}, {"newcomer": "spin"}, puffs=[0.3])
shot("S08", "L06", "town", still((-33.4, -13.2, 1.5), (-29.4, -9.6, 1.4), 28),
     {"driver": P((-29.8, -9.7), 235, arms=[40, 40], side=[-40, -40], expr="neutral")}, {"driver": [-42, -8]})
shot("S09", "L06.2", "town", still((-30.2, -19.5, 1.6), (-26.9, -16.4, 1.55), 26),
     {"owner": P((-26.9, -16.4), -100, expr="soft"), "driver": P((-28.6, -18.8), 20, head=[0, 12])},
     {"owner": [-45, -16.4], "driver": [-42, -19], "swing": ("owner", "L06.3", [-23, -16.4])})
shot("S10", "L07", "town", still((-30.4, -30.8, 1.6), (-26.9, -27.4, 1.55), 26),
     {"me": P((-26.9, -27.4), -105, expr="worried")}, {"me": [-26.9, -60]})
shot("S11", "L07.2", "town", still((-32.5, 3.0, 2.15), (-33.0, 6.2, 1.5), 20),
     {"me": P((-33.0, 6.2), 9, expr="neutral"), "grandad": P((-37.5, 14.2), 200)},
     {"me": [-37.5, 14.2], "grandad": [-45, 14]}, flame_ang={"me": 55})
shot("S12", "L08.1", "town", still((-21.2, -1.5, 1.7), (-24.0, -2.6, 1.5), 20),
     {"me": P((-24.0, -2.6), 111, expr="neutral"), "grandad": P((-37.0, -1.5), 90, z=-0.2)},
     {"me": [-37.0, -1.5], "grandad": [-45, -1.5]}, flame_ang={"me": 55})
shot("S13", "L09", "town", still((-33.8, -3.6, 1.5), (-36.9, -1.5, 1.3), 28),
     {"me": P((-36.9, -1.5), 120, z=-0.2, expr="worried", head=[0, -18])}, {"me": [-36.9, -30]})
# 02 the hut and the walk out
shot("S14", "L10", "ice", move(([2.0, -1.5, 1.55], [30, 4, 1.2]), ([8.0, 0.5, 1.5], [30, 4, 1.4]), 30, 52),
     {"fisher3": P((28.3, -2.6), 270), "fisher4": P((28.3, -12.4), 270)}, {"fisher3": "shore", "fisher4": "shore"})
shot("S15", "L11", "hut", still(H(1.25, -1.35, 1.35), H(-0.3, 0.4, 1.15), 24),
     {"grandad": P(H(-0.35, 0.4), 60, expr="neutral", z=-0.26, head=[0, 12])}, {"grandad": "shore"})
shot("S16", "L12", "ice", still((10.6, 5.4, 1.55), (7.0, 3.35, 1.4), 28),
     {"me": P((4.5, 3.35), 90, walk=[(1.5, (8.2, 3.35))], expr="soft", arms=[0, 0])}, {"me": list(RED)}, puffs=[0.2])
shot("S17", "L12.2", "ice", still((27.0, 3.55, 1.12), (28.49, 3.73, 0.96), 75), {}, {})
# 03 the fog and the figure
shot("S18", "L13.1", "ice", still((3.0, -3.0, 1.6), (30, 5, 1.7), 24),
     {"fisher3": P((28.3, -2.6), 270), "fisher4": P((28.3, -12.4), 270)}, {"fisher3": [32, -2.6], "fisher4": [32, -12.4]},
     fog=(0.06, 2.2))
shot("S19", "L14", "ice", still((1.0, 0.1, 1.6), (12.0, 0.1, 1.55), 20),
     {"fisher1": P((10.8, -3.2), 270), "fisher2": P((10.8, 3.4), 270), "fisher3": P((27.6, -1.8), 270)},
     {"fisher1": [14, -3.2], "fisher2": [14, 3.4], "fisher3": [31, -1.8]},
     swing_all="shore", swing_at="L14.1")
shot("S20", "L14.3", "ice", still((8.0, -0.2, 1.55), (10.8, -3.2, 1.65), 30),
     {"fisher1": P((10.8, -3.2), -135, expr="wide", head=[0, -14])}, {"fisher1": [14, -3.2]},
     swing={"fisher1": ("L14.4", "shore")})
LEAN_V1 = dict(pos=(150.0, 34.0), lean=8.0, face=RED)
shot("S21", "L15", "ice", still((38.0, 34.0, 1.7), (150.0, 34.0, 1.65), 85), {}, {}, leaner=LEAN_V1, fog=(0.005, 2.0), leaner_cam=True)
shot("S22", "L16", "ice", move(((38.0, 34.0, 1.7), (150.0, 34.0, 1.65)), ((38.0, 34.0, 1.7), (150.0, 34.0, 1.7)), 130, 175), {}, {}, leaner=LEAN_V1)
shot("S23", "L17", "ice", move(((38.0, 34.0, 1.7), (150.0, 34.0, 1.9)), ((38.0, 34.0, 1.7), (150.0, 34.0, 1.9)), 220, 300), {}, {}, leaner=LEAN_V1)
# 04 the first time inside
shot("S24", "L18", "hut", still(H(-1.1, -1.2, 1.2), H(0.6, 0.4, 0.75), 24),
     {"grandad": P(H(-0.35, 0.4), 150, z=-0.26, expr="soft", head=[-40, 5])}, {"grandad": "shore"})
shot("S25", "L19", "hut", still(H(0.4, -1.2, 1.15), H(-2.0, -1.2, 1.25), 24),
     {"me": P(H(-2.15, -1.2), 90, expr="worried", lean=22)}, {"me": list(RED)}, door_state=0.95)
shot("S26", "L20", "ice", still((11.4, 5.4, 1.55), (8.0, 3.35, 1.4), 28),
     {"me": P((5.0, 3.35), 90, walk=[(1.5, (9.0, 3.35))], expr="soft")}, {"me": list(RED)}, puffs=[0.2], fog=(0.06, 0.01))
LEAN_V2 = dict(pos=(64.8, 8.0), lean=25.0, face=RED)
shot("S27", "L21", "ice", still((46.0, 6.5, 1.7), (64.8, 8.0, 1.2), 55), {}, {}, leaner=LEAN_V2, fog=(0.006, 2.4),
     leaner_cam=True)
shot("S28", "L22", "ice", still((62.0, 0.5, 1.2), (64.8, 8.0, 1.0), 40), {}, {}, leaner=LEAN_V2)
shot("S29", "L23", "ice", still((65.9, 8.7, 1.75), (30.0, 4.0, 1.2), 40), {}, {}, leaner=LEAN_V2)
shot("S30", "L24", "hut", still(H(0.9, -0.5, 1.3), H(-0.35, 0.4, 1.2), 26),
     {"grandad": P(H(-0.35, 0.4), 60, z=-0.26, expr="soft", head=[0, -6])}, {"grandad": "shore"})
shot("S31", "L24.2", "hut", still(H(0.4, -0.6, 1.2), H(-2.0, -1.0, 1.3), 24),
     {"me": P(H(-2.0, -1.0), 90, expr="soft", lean=18, arms=[0, 0])}, {"me": list(RED)}, door_state=0.95)
# 05 the drive
shot("S32", "L25", "car", still(C(0.1, 0.35, 1.5), C(0.5, 1.15, 1.05), 26),
     {"grandad": P(C(0.5, 1.1), 70, z=-0.23, expr="asleep", head=[0, 14], blink=False)},
     {"grandad": [CAR[0] + 1.0, CAR[1] + 3.0]})
shot("S33", "L26", "car", still(C(0.05, 1.9, 1.5), C(-0.3, -0.3, 1.3), 24),
     {"me": P(C(-0.42, -0.2), 0, z=-0.23, expr="worried"),
      "grandad": P(C(0.5, 1.1), 70, z=-0.23, expr="asleep", head=[0, 14], blink=False)},
     {"me": C(0.5, 1.1), "grandad": [CAR[0] + 1.0, CAR[1] + 3.0]}, flame_ang={"me": 42})
shot("S34", "L27", "car", still(C(0.45, 0.5, 1.5), C(-0.4, -0.5, 1.2), 26),
     {"me": P(C(-0.42, -0.2), 55, z=-0.23, expr="worried", look=[0.8, 0.8])}, {"me": C(0.5, 1.1)}, flame_ang={"me": 42})
# 06 visits three and four
LEAN_V3 = dict(pos=(27.0, 12.4), lean=45.0, face=(28.5, 3.0))
shot("S35", "L28", "ice", still((18.0, 3.0, 1.6), (27.0, 12.4, 1.1), 40), {}, {}, leaner=LEAN_V3, fog=(0.006, 0.01))
shot("S36", "L29", "ice", still((27.0, 8.6, 0.28), (27.0, 12.4, 1.4), 30), {}, {}, leaner=LEAN_V3)
shot("S37", "L30", "ice", still((26.6, 10.6, 0.16), (27.0, 12.4, 0.1), 34), {}, {}, leaner=LEAN_V3)
shot("S38", "L31", "ice", still((27.6, 2.4, 1.3), (27.0, 12.4, 1.15), 45), {}, {}, leaner=LEAN_V3)
shot("S39", "L32", "hut", still(H(0.6, -0.9, 1.25), H(-2.0, -1.0, 0.8), 24),
     {"me": P(H(-1.75, -1.0), -90, expr="worried", lean=-6)}, {"me": list(RED)}, door_state=0.95)
shot("S40", "L32.3", "hut", still(H(0.95, -1.1, 1.3), H(-0.35, 0.45, 1.25), 26),
     {"grandad": P(H(-0.35, 0.4), 180, z=-0.26, expr="wide", blink=False)}, {"grandad": "shore"})
LEAN_V4 = dict(pos=(RED[0] + 0.25, RED[1] + 3.5), lean=55.0, face=(RED[0] + 0.25, RED[1] + 1.0), look=[0.5, 0.0])
shot("S41", "L33", "hut", still(H(0.2, -0.5, 1.15), H(0.25, 1.8, 1.1), 30),
     {"me": P(H(-0.7, -0.6), 180, expr="scared", z=0.0)}, {"me": list(RED)}, leaner=LEAN_V4, curtain=0.0, leaner_cam=True,
     leaner_key_gain=0.0)
shot("S42", "L34", "ice", still((RED[0] + 3.4, RED[1] + 3.2, 0.95), (RED[0] + 0.3, RED[1] + 2.6, 0.95), 28), {}, {},
     leaner=LEAN_V4, fog=(0.012, 0.01))
shot("S43", "L35", "ice", still(H(-1.2, 2.2, 0.9), H(0.25, 2.3, 0.92), 60), {}, {},
     leaner=LEAN_V4)
shot("S44", "L36", "hut", still(H(0.2, -0.4, 1.2), H(0.25, 1.8, 1.15), 30),
     {"me": P(H(-0.7, -0.6), 180, expr="scared")}, {"me": list(RED)}, leaner=LEAN_V4, curtain=1.0, curtain_dur=0.9)
# 07 the fog night
shot("S45", "L37", "ice", still((4.0, -1.0, 1.7), (30.0, 4.0, 1.2), 30), {}, {}, fog=(0.16, 0.01))
shot("S46", "L38", "ice", still((22.0, 3.4, 1.65), (28.4, 2.2, 1.45), 30),
     {"grandad": P((28.3, 3.0), -95, walk=[(0.9, (26.0, 3.4)), (2.4, (25.2, -4.5))], expr="neutral")},
     {"grandad": "shore"}, door_open=(1.0, 0.5))
shot("S47", "L39", "hut", still(H(1.1, -1.2, 1.35), H(0.2, 0.2, 1.4), 26),
     {"me": P(H(-0.2, -0.6), 60, expr="worried", lean=0)}, {"me": list(RED)}, lamp=(0.15, 2.5), door_close=True)
shot("S48", "L40", "hut", still(H(-1.0, -1.5, 1.5), H(-0.2, -0.6, 1.5), 40),
     {"me": P(H(-0.2, -0.6), -90, expr="wide")}, {"me": list(RED)})
shot("S49", "L41", "hut", still(H(1.2, -0.9, 1.3), H(-1.9, -0.9, 1.1), 30),
     {"me": P(H(-1.25, -0.95), -90, expr="scared", lean=20)}, {"me": list(RED)}, door_open=(1.0, 0.7), door_at="L41.2")
SCARE_L = dict(pos=(RED[0] - 2.8, RED[1] + 0.38), lean=50.0, face=(RED[0] - 1.7, RED[1] - 0.3), look=[0.0, 0.0])
ME_SCARE = P(H(-0.15, -0.2), -90, expr="terrified", lean=42, head=[0, 0], blink=False)
shot("S50", "L42", "ice", still(H(-0.7, -1.25, 0.35), H(-1.5, -0.2, 1.1), 30), {"me": ME_SCARE}, {"me": list(RED)},
     leaner=SCARE_L, leaner_cam=True, door_open=(1.0, 0.01), door_state=1.0, fog=(0.07, 0.01))
shot("S51", "L43", "ice", still(H(-1.6, -3.4, 1.15), H(-1.7, -0.1, 1.1), 36), {"me": ME_SCARE}, {"me": list(RED)}, leaner=SCARE_L)
shot("S52", "L44", "ice", still(H(-2.3, -1.7, 1.1), H(-1.4, -0.2, 1.1), 50), {"me": ME_SCARE}, {"me": list(RED)}, leaner=SCARE_L,
     puffs=[0.2, 0.75])
shot("S53", "L44.2", "ice", still(H(-0.7, -1.25, 0.4), H(-1.8, -0.2, 1.05), 55), {"me": ME_SCARE}, {"me": list(RED)},
     leaner=SCARE_L)
shot("S54", "L45", "ice", still(H(-3.5, -1.4, 1.3), H(0.75, 0.4, 0.6), 32), {"me": ME_SCARE}, {"me": list(RED)}, leaner=SCARE_L)
# 08 the climax: the rule turned
FAR_F = {"fisher1": P((11.2, -5.2), 90), "fisher2": P((11.2, 8.6), 90), "fisher3": P((22.5, -3.5), 90),
         "fisher4": P((20.0, -10.0), 90)}
FAR_FL = {k: "shore" for k in FAR_F}
shot("S55", "L46", "ice", still(H(-1.9, -0.9, 1.3), H(-12.0, -0.2, 1.4), 28), dict(FAR_F), dict(FAR_FL), fog=(0.09, 0.01))
shot("S56", "L47", "ice", still(H(-3.4, -2.6, 1.55), H(-1.4, -0.9, 1.55), 28),
     {"me": P(H(-1.4, -0.9), -100, expr="worried", lean=10)}, {"me": "shore"})
shot("S57", "L48", "ice", still(H(-2.9, -0.5, 0.7), H(-1.4, -0.9, 1.9), 26),
     {"me": P(H(-1.4, -0.9), -100, expr="wide", head=[0, -32])}, {"me": "shore"})
shot("S58", "L49", "ice", still(H(-1.5, -2.2, 0.3), H(-1.6, -0.9, 2.0), 28),
     {"me": P(H(-1.6, -0.9), -100, expr="wide", head=[0, -30])}, {"me": "shore", "swing": ("me", "L49.0", [88.0, -4.0])},
     flame_ang={"me": 52}, leaner=SCARE_L)
shot("S59", "L50", "ice", still(H(-5.0, -2.2, 1.35), H(-2.1, -0.9, 1.1), 28),
     {"me": P(H(-1.2, -1.0), -90, expr="worried", walk=[(1.2, H(-4.4, -1.15)[:2])], lean=10)}, {"me": [88.0, -4.0]},
     leaner=SCARE_L)
shot("S59b", "L50.3", "ice", still(H(-2.6, -2.8, 1.4), H(-6.5, -1.0, 1.3), 28),
     {"me": P(H(-4.6, -1.2), -90, walk=[(1.5, H(-12.0, -1.2)[:2])], expr="worried")}, {"me": [88.0, -4.0]})
GRANDAD_AT = (88.0, -4.0)
shot("S60", "L51", "ice", still((38.5, -5.2, 1.5), (39.0, -2.0, 1.5), 22),
     {"me": P((33.0, -2.0), 90, walk=[(2.0, (44.5, -2.0))], expr="soft")}, {"me": GRANDAD_AT}, fog=(0.06, 0.01), puffs=[0.4])
shot("S61", "L52", "ice", still((78.0, -1.0, 1.0), (88.0, -4.0, 0.95), 38),
     {"grandad": P(GRANDAD_AT, 270, z=-0.3, expr="neutral")}, {"grandad": "shore"})
shot("S62", "L53", "ice", still((83.8, -2.4, 1.3), (88.0, -4.0, 1.05), 32),
     {"grandad": P(GRANDAD_AT, 250, z=-0.3, expr="neutral", arms=[40, 40], side=[-40, -40], head=[0, 8])}, {"grandad": "shore"})
shot("S63", "L54", "ice", still((87.6, -9.4, 1.35), (87.4, -4.6, 1.5), 28),
     {"grandad": P(GRANDAD_AT, 215, z=-0.3, expr="neutral"), "me": P((86.6, -5.6), 40, expr="soft")},
     {"grandad": "shore", "me": GRANDAD_AT})
shot("S64", "L55", "ice", still((85.2, -2.1, 1.1), (88.0, -4.0, 1.0), 40),
     {"grandad": P(GRANDAD_AT, 238, z=-0.3, expr="grin")}, {"grandad": "shore"})
shot("S65", "L56", "ice", still((84.4, -8.0, 2.5), (87.3, -4.8, 1.5), 24),
     {"me": P((86.6, -5.6), 40, expr="soft", head=[0, 10]), "grandad": P(GRANDAD_AT, 215, z=-0.3, expr="neutral")},
     {"me": GRANDAD_AT, "grandad": "shore"})
shot("S66", "L57", "car", still(C(0.05, 1.9, 1.5), C(-0.3, -0.3, 1.3), 24),
     {"me": P(C(-0.42, -0.2), 0, z=-0.23, expr="worried"),
      "grandad": P(C(0.5, 1.1), 70, z=-0.23, expr="asleep", head=[0, 14], blink=False)},
     {"me": C(0.5, 1.1), "grandad": [CAR[0] + 1.0, CAR[1] + 3.0]}, flame_ang={"me": 42})
shot("S67", "L57.3", "town", move(([-32.5, 3.0, 2.15], [-33.0, 6.2, 1.5]), ([-33.6, 6.4, 2.05], [-35.8, 11.0, 1.3]), 20, 26),
     {"me": P((-33.0, 6.2), 9), "grandad": P((-37.5, 14.2), 200)}, {"me": [-37.5, 14.2], "grandad": [-45, 14]},
     flame_ang={"me": 55})
shot("S68", "L58", "town", move(([-21.2, -1.5, 1.7], [-24.0, -2.6, 1.5]), ([-22.6, -1.9, 1.6], [-30.0, -1.6, 1.0]), 20, 28),
     {"me": P((-24.0, -2.6), 111), "grandad": P((-37.0, -1.5), 90, z=-0.2)},
     {"me": [-37.0, -1.5], "grandad": [-45, -1.5]}, flame_ang={"me": 55})
# 09 the warm turn
shot("S69", "L59", "ice", still((15.0, 4.4, 1.55), (29.0, 3.6, 1.55), 30),
     {"me": P((24.0, 2.8), 90, walk=[(2.2, (26.0, 2.8))]), "grandad": P((24.0, 4.9), 90, walk=[(2.2, (26.0, 4.9))])},
     {"me": [24.0, 40.0], "grandad": "shore"}, fog=(0.03, 2.0), puffs=[0.5], leaner_cam=False)
shot("S70", "L60", "ice", still(H(-5.6, 2.4, 1.5), H(-2.0, -0.2, 1.1), 30), {}, {}, leaner=dict(SCARE_L, lean=50.0),
     door_state=0.0, fog=(0.03, 0.01))
shot("S71", "L60.3", "ice", still(H(-5.6, -3.0, 1.45), H(-2.0, -1.0, 1.2), 30),
     {"me": P(H(-3.4, -1.9), 80, walk=[(1.2, H(-1.6, -1.15)[:2])], expr="worried"),
      "grandad": P(H(-3.7, -3.3), 80, walk=[(1.2, H(-1.9, -1.45)[:2])])}, {"me": "shore", "grandad": "shore"},
     leaner=SCARE_L)
shot("S72", "L61.3", "hut", still(H(-0.9, -1.2, 1.2), H(0.75, 0.45, 0.8), 24),
     {"me": P(H(0.75, 0.4), 0, z=-0.26, expr="soft")}, {"me": "shore"}, lamp=(1.0, 1.5), lap=True, door_state=0.0)
shot("S73", "L62", "hut", still(H(-0.9, -0.9, 1.25), H(0.25, 1.8, 1.0), 30),
     {"me": P(H(0.75, 0.4), 150, z=-0.26, expr="soft", head=[-30, 4])}, {"me": "shore"}, lap=True)
shot("S74", "L63", "hut", still(H(1.2, -1.5, 1.35), H(0.2, 0.4, 1.0), 26),
     {"me": P(H(0.75, 0.4), -60, z=-0.26, expr="soft"), "grandad": P(H(-0.35, 0.4), 120, z=-0.26, expr="soft")},
     {"me": "shore", "grandad": "shore"}, lap=True, dusk=(1.0, 3.0))
shot("S75", "L64", "hut", still(H(-0.35, -1.0, 1.6), H(-0.35, 0.4, 1.6), 30),
     {"grandad": P(H(-0.35, 0.4), 5, z=-0.26, expr="soft")}, {"grandad": "spin", "swing": ("grandad", "L64.4", H(0.75, 0.4))},
     lap=True)
shot("S76", "L65", "hut", still(H(0.2, -1.6, 1.3), H(0.2, 0.4, 1.4), 24),
     {"me": P(H(0.75, 0.4), -75, z=-0.26, expr="soft"), "grandad": P(H(-0.35, 0.4), 75, z=-0.26, expr="soft")},
     {"me": H(-0.35, 0.4), "grandad": H(0.75, 0.4)}, lap=True)
shot("S77", "L65.5", "hut", still(H(1.2, -1.4, 1.35), H(0.75, 0.4, 1.35), 45),
     {"me": P(H(0.75, 0.4), 14, z=-0.26, expr="grin")}, {"me": H(-0.35, 0.4)}, lap=True)

WHERE = {s["id"]: s["where"] for s in SH}
LEANER_SHOTS = [s["id"] for s in SH if s.get("leaner")]

# ---------------------------------------------------------------------------------------------------- build acting + cues
shots = []
visible = set()
flame_cur = {}
for i, s in enumerate(SH):
    d = {"id": s["id"], "cam": s["cam"], "hand": 0.0 if s["where"] == "hut" and False else 0.004, "step": 2}
    if i:
        d["at"] = s["at"]
    shots.append(d)
    at = s["at"]
    now = set(s["people"])
    for who in cast:
        if who == "leaner":
            continue
        if who in now:
            p = s["people"][who]
            keys = {k: v for k, v in p.items() if k not in ("pos", "yaw", "walk", "z")}
            z = p.get("z", 0)
            pos3 = [p["pos"][0], p["pos"][1]] + ([z] if z else [])
            prev = next((k["pos"] for k in reversed(ACT[who]) if "pos" in k), None)
            if prev is not None:
                ACT[who].append({"at": at, "pos": prev})
            base = {"at": at, "pos": pos3, "blend": 0, "hidden": False, "arms": [0, 0], "side": [0, 0],
                    "head": [0, 0], "lean": 0, "tremble": 0, "blink": True, "look": [0, 0]}
            if "yaw" in p:
                base["yaw"] = p["yaw"]
            base.update(keys)
            ACT[who].append(base)
            for dt, pos in p.get("walk", []):
                ACT[who].append({"at": f"{at}+{dt}", "pos": list(pos[:2]) + ([z] if z else [])})
            visible.add(who)
        elif who in visible:
            ACT[who].append({"at": at, "hidden": True, "blend": 0})
            visible.discard(who)
    # the Leaner
    L = s.get("leaner")
    if L:
        pos = list(L["pos"])
        key = {"at": at, "pos": pos, "yaw": yaw_to(pos, L["face"]), "lean": L["lean"], "expr": "blank", "blend": 0,
               "hidden": False, "arms": [0, 0], "side": [0, 0], "head": [0, 0], "blink": False, "look": L.get("look", [0, 0])}
        if ACT["leaner"]:
            prev = next((k["pos"] for k in reversed(ACT["leaner"]) if "pos" in k), None)
            if prev is not None:
                ACT["leaner"].append({"at": at, "pos": prev})
        ACT["leaner"].append(key)
        visible.add("leaner")
    elif "leaner" in visible:
        ACT["leaner"].append({"at": at, "hidden": True, "blend": 0})
        visible.discard("leaner")
    # flames: snap to the shot's lean at its start
    for who in s["people"]:
        tgt = s["flames"].get(who, "shore")
        ang = s.get("flame_ang", {}).get(who, 40)
        c = {"at": at, "name": "flame", "who": who, "dur": 0.0, "ang": ang}
        if tgt == "up":
            c["to"] = None
        elif tgt == "spin":
            c["spin"] = 2.0
            c["ang"] = 35
        elif tgt == "shore":
            c["to"] = [-300, 0]
            c["shore"] = True
        else:
            c["to"] = list(tgt[:2])
        CUES.append(c)
    sw = s["flames"].get("swing")
    if sw:
        who, when, tgt = sw
        CUES.append({"at": when, "name": "flame", "who": who, "dur": 1.0, "ang": s.get("flame_ang", {}).get(who, 40),
                     "to": list(tgt[:2])})
    for who, (when, tgt) in s.get("swing", {}).items():
        c = {"at": when, "name": "flame", "who": who, "dur": 1.0, "ang": 40}
        if tgt == "shore":
            c["to"] = [-300, 0]
            c["shore"] = True
        else:
            c["to"] = list(tgt)
        CUES.append(c)
    if s.get("swing_all"):
        for who in s["people"]:
            CUES.append({"at": s["swing_at"], "name": "flame", "who": who, "dur": 1.0, "ang": 40, "to": [-300, 0], "shore": True})
    # fog ramps, the lamp, the door, the curtain, the dusk, breath
    if s.get("fog"):
        dd, dur = s["fog"]
        CUES.append({"at": at, "name": "fog", "d": dd, "dur": dur})
    if s.get("lamp"):
        v, dur = s["lamp"]
        CUES.append({"at": at, "name": "lamp", "on": v, "dur": dur})
    if "door_open" in s and isinstance(s["door_open"], tuple):
        v, dur = s["door_open"]
        CUES.append({"at": s.get("door_at", at), "name": "door", "open": v, "dur": dur})
    if "door_state" in s:
        CUES.append({"at": at, "name": "door", "open": s["door_state"], "dur": 0.0})
    if s.get("door_close"):
        CUES.append({"at": at, "name": "door", "open": 0.0, "dur": 0.0})
    if "curtain" in s:
        CUES.append({"at": at, "name": "curtain", "shut": s["curtain"], "dur": s.get("curtain_dur", 0.0)})
    if s.get("dusk"):
        v, dur = s["dusk"]
        CUES.append({"at": at, "name": "dusk", "v": v, "dur": dur})
    for dt in s.get("puffs", []):
        CUES.append({"at": f"{at}+{dt}", "name": "puff", "who": "me"})
    if s.get("hedge_sway"):
        CUES.append({"at": at, "name": "hedge", "amp": 1.0})

for who in cast:
    ACT[who].insert(0, {"at": 0, "hidden": True, "pos": [0, 0], "blend": 0})
acting = dict(ACT)
# the hedge sways only in S05 (a slow rock), the lamp and door start at their rest values
CUES.insert(0, {"at": 0, "name": "fog", "d": 0.005, "dur": 0.0})

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L02", "kind": "whoosh", "db": -30, "dur": 1.0},
    {"at": "L13.1", "kind": "riser", "db": -26, "dur": 2.0},
    {"at": "L15", "kind": "whoosh", "db": -28, "dur": 1.6},
    {"at": "L33", "kind": "sting", "db": -14},
    {"at": "L36.1", "kind": "whoosh", "db": -22, "dur": 0.6},
    {"at": "L40.1", "kind": "scrape", "db": -17, "dur": 0.22},
    {"at": "L40.1+0.45", "kind": "scrape", "db": -17, "dur": 0.22},
    {"at": "L41.2", "kind": "door", "db": -16},
    {"at": "L42", "kind": "sting", "db": -8},
    {"at": "L61.2", "kind": "click", "db": -22},
    {"at": "L21", "kind": "whoosh", "db": -30, "dur": 1.4},
]
for t_ in ("L15.1", "L24.1", "L30.1", "L47.1"):
    sfx.append({"at": t_, "kind": "click", "db": -30})

story = {
    "slug": "ep36-ice-huts",
    "title": "In this town, the little flame over your head always leans toward home",
    "made_for_kids": False,
    "premise": ("In a lake town, a small amber flame floats over every head and always leans toward home. Mine never leans toward my flat. "
                "Each Saturday I visit Grandad's red fishing hut on the frozen lake, and each time the fog lifts a rust-red person with no "
                "flame stands a little nearer, tipped at a slant no one could hold."),
    "twist": ("My flame was never wandering: it leans toward home, and home is Grandad. It followed him around town, in the car and "
              "across the ice, and the thing on the ice stood where the second stool's empty seat was."),
    "world": ("a frozen lake with painted wooden fishing huts and low gold sun, fog rolling in and lifting, a small town on the shore, "
              "a red hut with two stools over one hole"),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff7a2e",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#c3d1de", "fog_density": 0.005, "fog_start": 6.0, "sky": "#b9cde0", "sky_strength": 1.0,
             "exposure": -0.75, "flash_safe": True},
    "grade": {"shadows": [-0.01, 0.0, 0.05], "highlights": [0.02, 0.0, -0.02], "saturation": 0.95, "contrast": 1.08,
              "vignette": 0.3, "bloom": 0.3, "grain": 0.01, "red_line": 0.79},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": CUES,
    "fx": [],
    "shot_where": WHERE,
    "leaner_shots": LEANER_SHOTS,
    "leaves_shots": ["S05"],
    "door_shots": ["S25", "S31", "S39", "S49", "S50", "S51", "S52", "S53", "S54", "S55", "S56", "S57", "S58", "S59", "S70", "S71"],
    "music": {"root": 47, "mode": "minor", "bpm": 64, "seed": 36,
              "sections": [
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L07", "voices": ["drone", "pad"], "energy": 0.35},
                  {"at": "L13", "voices": ["drone", "pad", "pulse"], "energy": 0.4},
                  {"at": "L15", "voices": ["drone", "pad"], "energy": 0.35},
                  {"at": "L28", "voices": ["drone", "pad", "pulse"], "energy": 0.5},
                  {"at": "L33", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L37", "voices": ["drone", "pad", "choir"], "energy": 0.5},
                  {"at": "L42", "voices": ["drone", "choir"], "energy": 0.45},
                  {"at": "L46", "voices": ["drone", "pad", "choir"], "energy": 0.55},
                  {"at": "L56", "voices": ["pad", "choir"], "energy": 0.4},
                  {"at": "L59", "voices": ["piano", "pad"], "energy": 0.4, "mode": "major", "root": 47},
                  {"at": "L64", "voices": ["piano", "pad"], "energy": 0.35, "mode": "major", "root": 47},
              ]},
    "sound": {"floor": "grass", "steps_db": -20,
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "L25", "lufs": -34},
                  {"kind": "wind", "from": "L28", "to": "L59", "lufs": -33},
                  {"kind": "hum", "from": "L15", "to": "L16", "lufs": -44},
                  {"kind": "room", "from": "L61.3", "to": "end", "lufs": -38},
                  {"kind": "wind", "from": "L59", "to": "L61", "lufs": -40},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "L15-0.6", "to": "L15.1", "keep": ["whoosh"]},
                              {"from": "L33-0.6", "to": "L33.1", "keep": ["sting"]},
                              {"from": "L42-0.8", "to": "L42.2", "keep": ["sting"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
