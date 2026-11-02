"""Writes ../story.json for ep29 "My new workmates call me the Spare" (script 2026-11-02).

Run from anywhere: python stories/ep29-ten-pin/generator/make_story.py
The words are in lines.json next to this file (the scriptwriter's). Everything else is here: the cast, the shots
and their cameras, the acting, the cues set.py reads (the creature, the pins, the sweep, the ball, the props, the
lane lights, the score screen), the score and the sound.

Places (set.py's metres): lane i runs down +y at x = -1.6 i (ours is lane 0 against the right wall), the foul line is
y = 0 and the pin deck's head pin y = 14.4. The approach is y = -4.6 .. 0, then the carpet and the five seats at
y = -5.6, the score screen over the approach at y = -3.4 facing -y. A character with yaw 0 faces -y; yaw 180 faces
down the lanes (+y); yaw 90 faces +x.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
LOOP = 0.25
# captions show two or three words: a longer chunk of the script is split (the spoken words split with it), and
# every "Lxx.n" reference below is moved to the new chunk numbering
CHUNK_MAP = {}


def _split(cap, sp):
    cw, sw = cap.split(" "), sp.split(" ")
    n = len(cw)
    if n <= 3 or len(sw) != n:
        return [(cap, sp)]
    k = -(-n // 3)
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    out, i = [], 0
    for z in sizes:
        out.append((" ".join(cw[i:i + z]), " ".join(sw[i:i + z])))
        i += z
    return out


for ln in lines:
    new = []
    for old, (cap, sp) in enumerate(ln.get("chunks", [])):
        CHUNK_MAP[(ln["id"], old)] = len(new)
        new += [list(x) for x in _split(cap, sp)]
    if "chunks" in ln:
        ln["chunks"] = new
TEMPO = {"L16": 0.93, "L19": 0.93, "L38": 0.93, "L45": 0.9, "L76": 0.9}   # the word check: a swallowed word comes through
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]
lines = lines + [{"id": "P99", "pause": LOOP, "chunks": []}]


def _fixref(v):
    import re
    m = re.match(r"^(L\d+)\.(\d+)(.*)$", v) if isinstance(v, str) else None
    if not m:
        return v
    return f"{m.group(1)}.{CHUNK_MAP.get((m.group(1), int(m.group(2))), int(m.group(2)))}{m.group(3)}"


def _walk(o):
    if isinstance(o, dict):
        return {k: (_fixref(v) if k in ("at", "from", "to") else _walk(v)) for k, v in o.items()}
    if isinstance(o, list):
        return [_walk(x) for x in o]
    return o



TEAL, CREAM = "#1f8f86", "#efe6d2"
# ---------------------------------------------------------------------------------------------------- cast
cast = {
    "me": {"age": "adult", "skin": "#e0b48c", "shirt": "#6d7076", "pattern": "solid", "collar": "#5b5e63",
           "pants": "#2b3550", "shoes": "#585b61", "sleeves": "long", "hair": "cap", "hair_c": "#4a2f1d", "hat": "none",
           "extras": ["hooddown"], "width": 0.8, "face": {"eyes": "round", "brows": True}},
    "dev": {"age": "adult", "skin": "#8d5a3c", "shirt": TEAL, "pattern": "solid", "pants": "#2d3140", "shoes": "#1a1a1e",
            "sleeves": "long", "hair": "buzz", "hair_c": "#1c1614", "hat": "none", "extras": ["glasses"],
            "extra_c": "#16181d", "height": 1.06, "width": 0.8, "face": {"eyes": "round", "brows": True}},
    "rosie": {"age": "adult", "skin": "#f1c9a0", "shirt": TEAL, "pattern": "solid", "pants": "#3a3340", "shoes": "#d8d2c6",
              "sleeves": "long", "hair": "spiky", "hair_c": "#b5451f", "hat": "none", "width": 0.8,
              "face": {"eyes": "lashes", "brows": True, "cheeks": "#e8907a"}},
    "mags": {"age": "adult", "skin": "#e8c3a0", "shirt": TEAL, "pattern": "solid", "pants": "#4a4850", "shoes": "#3a2f2a",
             "sleeves": "long", "hair": "bun", "hair_c": "#aeaeb4", "hat": "none", "height": 0.95, "width": 0.8,
             "face": {"eyes": "round", "brows": True, "bags": True}},
    "tomasz": {"age": "adult", "skin": "#c68a62", "shirt": TEAL, "pattern": "solid", "pants": "#2a2d36", "shoes": "#202226",
               "sleeves": "long", "hair": "cap", "hair_c": "#1c1614", "hat": "beanie", "hat_c": "#1e3264", "width": 0.8,
               "face": {"eyes": "round", "brows": True}},
}
WHO = list(cast)


def c(*keys):
    return [list(k) for k in keys]


def cam(fr, tgt, lens, v=0.0):
    """A locked camera. v lowers the target by that fraction of the frame's height, so a face sits higher in the
    frame (above the caption band)."""
    d = math.dist(fr, tgt)
    h = 24.0 * d / lens
    return c([0, list(fr), [tgt[0], tgt[1], tgt[2] - v * h], lens])


def mv(fr0, tgt0, fr1, tgt1, lens0, lens1=None, v=0.0):
    lens1 = lens1 or lens0
    out = []
    for u, fr, tgt, ln in ((0, fr0, tgt0, lens0), (1, fr1, tgt1, lens1)):
        h = 24.0 * math.dist(fr, tgt) / ln
        out.append([u, list(fr), [tgt[0], tgt[1], tgt[2] - v * h], ln])
    return out


# ---------------------------------------------------------------------------------------------------- places
SEAT_X = {"dev": 0.15, "tomasz": -0.85, "mags": -1.85, "rosie": -2.85, "me": -3.9}
SEAT_Y = -5.62
STAND_X = {"dev": 0.2, "tomasz": -0.8, "mags": -1.8, "rosie": -2.8, "me": -3.8}
SCR_X = -1.35
SEAT_Z = -0.05
LANE_Y = 15.9


def seat(who, **kw):
    return ([SEAT_X[who], SEAT_Y, SEAT_Z], 180, {"sit": True, **kw})


def stand(who, y=-4.5, yaw=180, **kw):
    return ([STAND_X[who], y], yaw, kw)


def yaw_to(a, b):
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


def face_cam(pos, yaw, d, lens, h=1.5, side=0.0, v=0.14):
    """A camera d metres in front of a character at pos facing yaw, looking at their face."""
    fx, fy = math.sin(math.radians(yaw)), -math.cos(math.radians(yaw))
    rx, ry = -fy, fx
    fr = [pos[0] + fx * d + rx * side, pos[1] + fy * d + ry * side, h]
    return cam(fr, [pos[0], pos[1], h], lens, v)


# ---------------------------------------------------------------------------------------------------- shots
# (at, scene, camera, extra) -- scene: who -> (pos, yaw, opts); anyone not named is hidden. extra: step, hand.
SHOTS = []


def shot(at, scene, camera, step=2, hand=0.004, note=""):
    SHOTS.append({"at": at, "scene": scene, "cam": camera, "step": step, "hand": hand, "note": note})


SEATED_ALL = {w: seat(w) for w in WHO}

# 01 night one ---------------------------------------------------------------------------------------------
shot(0, {"me": ([-0.3, -1.5], 0, {"expr": "smirk"})},
     mv([-0.3, -4.8, 1.5], [-0.3, -1.5, 1.45], [-0.3, -4.2, 1.5], [-0.3, -1.5, 1.45], 26, 30, v=0.1), note="S1")
shot("L02", {"me": ([-0.3, -1.5], 0, {"expr": "smirk"})},
     mv([1.0, -6.9, 0.8], [-0.7, 2.0, 1.55], [0.6, -6.9, 0.8], [-0.7, 2.0, 1.55], 20, 21), note="S2 wide, screen glowing")
shot("L03", {w: ([x, -10.6], 180, {"expr": "neutral"}) for w, x in
             (("dev", -0.4), ("rosie", -0.9), ("mags", -0.5), ("tomasz", -0.9))} | {"me": ([-0.7, -11.6], 180, {})},
     cam([0.4, -5.0, 1.3], [-0.7, -9.2, 1.3], 21, 0.0), note="S3 front doors, in")
shot("L04", {"dev": seat("dev", expr="neutral")}, face_cam([SEAT_X["dev"], SEAT_Y], 180, 2.7, 24), note="S4 Dev")
shot("L04.1", {"rosie": seat("rosie", expr="soft")}, face_cam([SEAT_X["rosie"], SEAT_Y], 180, 2.7, 24), note="S4 Rosie")
shot("L04.2", {"mags": seat("mags", expr="neutral")}, face_cam([SEAT_X["mags"], SEAT_Y], 180, 2.7, 24), note="S4 Mags")
shot("L04.3", {"tomasz": seat("tomasz", expr="smirk")}, face_cam([SEAT_X["tomasz"], SEAT_Y], 180, 2.7, 24), note="S4 Tomasz")
shot("L04.4", {w: seat(w) for w in ("dev", "tomasz", "mags", "rosie")},
     cam([-1.0, -2.6, 1.55], [-1.0, -5.6, 1.4], 14, 0.1), note="S4 the four, all teal")
shot("L05", {"me": seat("me", expr="worried"), "rosie": seat("rosie")},
     cam([-2.9, -3.3, 1.45], [-3.7, -5.6, 1.4], 24, 0.12), note="S5 me on the end seat, a little apart")
shot("L06", {}, mv([-1.0, -5.2, 0.4], [0.0, -1.4, 3.0], [-0.6, -5.2, 0.4], [0.0, -1.4, 3.1], 22), note="S6 lamp housing")
shot("L07", {"mags": ([-1.0, -3.7], 0, {"arms": [0, 84], "side": [0, 34], "expr": "soft", "talk": ("L07", "L07>")})},
     cam([-1.0, -6.0, 1.5], [-1.0, -3.7, 1.3], 24, 0.1), note="S7 Mags holds out the shoes (plant 2)")
shot("L08", {"me": ([-1.0, -3.2], 0, {"expr": "worried"})},
     mv([-1.0, -5.4, 0.7], [-1.0, -3.2, 0.15], [-1.0, -5.0, 0.6], [-1.0, -3.2, 0.15], 30, 34), note="S8 warm shoes")
shot("L09", {w: seat(w) for w in WHO},
     cam([SCR_X, -7.2, 1.25], [SCR_X, -3.4, 2.1], 30, 0.0), note="S9 the screen, six rows (plant 1)")
shot("L10", {}, cam([SCR_X, -5.6, 2.3], [SCR_X - 0.2, -3.4, 2.5], 26, 0.0), note="S10 rows one to four")
shot("L11", {}, cam([SCR_X, -5.4, 1.5], [SCR_X - 0.45, -3.4, 1.95], 27, 0.0), note="S11 the sixth row")
shot("L12", {}, cam([SCR_X - 0.4, -5.2, 1.9], [SCR_X - 0.45, -3.4, 2.1], 25, 0.0), hand=0, note="S12 the fifth row, held")
shot("L13", {"dev": ([SEAT_X["dev"], SEAT_Y, SEAT_Z], -95, {"sit": True, "arms": [0, 170], "expr": "neutral",
                                                              "talk": ("L13", "L14>")})},
     cam([0.5, -3.7, 1.55], [0.15, -5.6, 1.55], 24, 0.1), note="S13 Dev, one finger up")
shot("L14", {w: seat(w) for w in WHO}, cam([SCR_X, -7.0, 1.3], [SCR_X, -3.4, 2.05], 30, 0.0), note="S14 the fifth row lights up")
shot("L15", {w: stand(w) for w in WHO}, cam([SCR_X, -7.9, 1.25], [SCR_X, -3.4, 1.9], 24, 0.0), note="S15 standing back")
shot("L16", {"dev": ([-1.2, -3.0], 0, {"arms": [86, 0], "expr": "smirk", "talk": ("L16.2", "L16>")}),
             "rosie": ([-0.2, -3.0], 0, {"expr": "soft"}), "mags": ([-2.2, -3.0], 0, {"expr": "soft"}),
             "tomasz": ([0.7, -3.3], 0, {"expr": "smirk"})},
     cam([-1.2, -5.4, 1.4], [-1.2, -3.0, 1.45], 22, 0.1), note="S16 Dev points at me")
shot("L17", {"me": ([-1.2, -2.2], 0, {"expr": "smirk", "head": [0, 4]})},
     face_cam([-1.2, -2.2], 0, 1.8, 24), note="S17 flat unsure smile")
shot("L18", {}, cam([0.15, -0.9, 0.3], [0.0, 6.5, 0.12], 26, 0.0), hand=0.002, note="S18 the gutter ball")
shot("L19", {}, cam([-0.8, -3.6, 0.92], [-0.8, -2.05, 0.55], 28, 0.0), hand=0, note="S19 LORE PLANT")
shot("L20", {"me": ([-1.2, -2.6], -135, {"expr": "wide", "head": [0, -6]})},
     face_cam([-1.2, -2.6], -135, 2.0, 24), note="S20 I saw it")

# 02 week one ---------------------------------------------------------------------------------------------
LONG = [-0.4, -1.5, 1.15]
shot("L21", {}, cam(LONG, [-4.8, 15.0, 1.6], 85, 0.0), hand=0, note="S21 three lanes down")
shot("L22", {}, cam(LONG, [-4.8, 15.4, 1.45], 135, 0.0), hand=0, note="S22 somebody standing")
shot("L23", {}, cam(LONG, [-4.8, 15.9, 0.95], 140, 0.0), hand=0, note="S23 body, chest to shoes")
shot("L24", {}, mv(LONG, [-4.8, 15.9, 0.8], LONG, [-4.8, 15.9, 1.85], 110, 110, 0.0), hand=0, note="S24 tilt up to two heads")
shot("L25", {}, cam(LONG, [-4.8, 15.9, 1.57], 210, 0.0), hand=0, note="S25 bottom face")
shot("L26", {}, cam(LONG, [-4.8, 15.9, 1.99], 210, 0.0), hand=0, note="S26 top face shut")
shot("L27", {"me": seat("me", expr="worried", head=[-40, 0]), "rosie": seat("rosie", expr="neutral")},
     cam([-3.4, -3.6, 1.5], [-3.4, -5.6, 1.42], 18, 0.1), note="S27 nudging Rosie")
shot("L28", {"rosie": ([SEAT_X["rosie"], SEAT_Y, SEAT_Z], 180, {"sit": True, "head": [-20, 0], "expr": "neutral"})},
     cam([-1.9, -6.9, 1.95], [-4.8, 15.9, 1.55], 55, 0.0), hand=0.003, note="S28 over Rosie's shoulder")
shot("L28.2", {"rosie": seat("rosie", expr="worried", talk=("L28.2", "L28>"))},
     face_cam([SEAT_X["rosie"], SEAT_Y], 180, 2.4, 22), note="S28 her puzzled face")
shot("L29", {"tomasz": seat("tomasz", expr="smirk", head=[0, -26])},
     face_cam([SEAT_X["tomasz"], SEAT_Y], 180, 2.4, 22), note="S29 Tomasz looks up")
shot("L29.1", {"tomasz": seat("tomasz", expr="smirk", head=[0, -26])},
     cam([-0.6, -7.2, 1.2], [SCR_X - 0.2, -3.4, 2.15], 26, 0.0), note="S29 the cross (plant 3)")
shot("L29.3", {"tomasz": seat("tomasz", expr="smirk", head=[0, -26], talk=("L29.3", "L29>"))},
     face_cam([SEAT_X["tomasz"], SEAT_Y], 195, 2.3, 22), note="S29 Tomasz, pleased")
shot("L30", {}, cam([SCR_X - 0.2, -5.3, 1.6], [SCR_X - 0.3, -3.4, 1.95], 26, 0.0), note="S30 my row, short bars")
shot("L30.1", {"me": seat("me", expr="worried")}, face_cam([SEAT_X["me"], SEAT_Y], 180, 2.2, 22), note="S30 my face")

# 03 week two ---------------------------------------------------------------------------------------------
shot("L31", {}, cam([-1.0, -5.0, 1.1], [-2.7, 15.0, 1.5], 40, 0.0), hand=0.003, note="S31 two lanes down")
shot("L32", {}, cam([-1.2, -1.0, 0.3], [-3.2, 15.9, 0.18], 110, 0.0), hand=0, note="S32 its shoes")
shot("L32.2", {"me": ([-1.5, -4.0], 0, {"expr": "worried"})},
     cam([-1.5, -6.0, 0.7], [-1.5, -4.0, 0.2], 28, 0.0), note="S32 my matching shoes")
shot("L33", {}, cam([-1.0, -0.5, 1.2], [-3.1, 15.9, 1.99], 200, 0.0), hand=0, note="S33 top head, a slit")
shot("L34", {}, cam([SCR_X, -5.4, 1.9], [SCR_X - 0.45, -3.4, 2.1], 22, 0.0), hand=0, note="S34 the fifth row lights up")
shot("L34.2", {w: stand(w) for w in WHO}, cam([-2.6, -8.0, 1.3], [SCR_X, -3.4, 1.8], 22, 0.0), note="S34 we all stand back")
shot("L35", {}, cam([0.9, -4.4, 1.0], [-0.4, 0.0, 0.5], 22, 0.0), note="S35 nobody bowls")
shot("L36", {}, cam([0.2, -0.6, 0.35], [0.0, 14.6, 0.3], 80, 0.0), hand=0.002, note="S36 the pins go down")
shot("L37", {"dev": ([-1.7, -4.95], 0, {"head": [0, 38], "expr": "neutral"}),
             "tomasz": ([-2.7, -4.95], 0, {"head": [0, 40], "expr": "neutral"})},
     cam([-2.2, -2.7, 1.5], [-2.2, -4.95, 1.2], 18, 0.1), note="S37 nachos")
shot("L37.2", {"mags": ([-1.7, -4.95], 0, {"head": [0, 38], "expr": "neutral"}),
               "rosie": ([-2.7, -4.95], 0, {"head": [0, 40], "expr": "neutral"})},
     cam([-2.2, -2.7, 1.5], [-2.2, -4.95, 1.2], 18, 0.1), note="S37 nachos 2")

# 04 week three -------------------------------------------------------------------------------------------
shot("L38", {}, cam([0.3, -0.5, 1.2], [-1.55, 15.9, 1.75], 115, 0.0), hand=0, note="S38 next to ours")
shot("L39", {}, cam([0.3, -0.5, 1.2], [-1.55, 15.9, 1.99], 220, 0.0), hand=0, note="S39 half open")
shot("L40", {}, cam([0.3, -0.5, 1.2], [-1.55, 15.9, 1.5], 100, 0.0), hand=0, note="S40 both heads turned")
shot("L41", {}, cam([0.3, -0.5, 1.2], [-1.55, 15.9, 1.6], 105, 0.0), hand=0, note="S41a first dip")
shot("L41+0.65", {}, cam([0.3, -0.5, 1.2], [-1.55, 15.9, 1.6], 105, 0.0), hand=0, note="S41b")
shot("L41+2.05", {}, cam([0.3, -0.5, 1.2], [-1.55, 15.9, 1.6], 105, 0.0), hand=0, note="S41c")
shot("L42", {"me": ([0.0, -2.8], 180, {"expr": "worried", "head": [0, 24]})},
     cam([0.35, -1.9, 0.3], [0.0, -0.6, 0.12], 24, 0.0), note="S42 my shoes up to the line")

# 05 week four --------------------------------------------------------------------------------------------
shot("L43", {}, mv([0.3, -0.5, 1.1], [-1.6, 15.9, 1.0], [0.3, -0.5, 1.1], [-8.0, 15.9, 1.0], 70, 70, 0.0), hand=0,
     note="S43 all the decks empty")
shot("L44", {}, cam([SCR_X, -5.4, 1.9], [SCR_X - 0.45, -3.4, 2.1], 22, 0.0), hand=0, note="S44 the fifth row lights up")
shot("L44.2", {w: stand(w) for w in WHO}, cam([-4.6, -7.4, 0.95], [SCR_X, -3.4, 1.8], 22, 0.0), note="S44 everyone stands back")
shot("L45", {"mags": ([SCR_X, -4.9], 0, {"expr": "neutral", "talk": ("L45.3", "L45>")})},
     cam([-1.2, -6.9, 1.45], [-1.35, -3.9, 1.85], 22, 0.0), hand=0.003, note="S45 your go, Spare (plant 4)")
shot("L46", {"dev": ([-0.6, -4.9], 180 + 0, {"expr": "neutral"}), "rosie": ([-1.55, -4.9], 180, {"expr": "worried"}),
             "tomasz": ([-2.5, -4.9], 180, {"expr": "neutral"})},
     mv([-0.6, -2.6, 1.5], [-0.6, -4.9, 1.45], [-2.5, -2.6, 1.5], [-2.5, -4.9, 1.45], 24, 24, 0.1), note="S46 nobody stops me")
shot("L47", {"me": ([0.0, -1.5], 180, {"arms": [62, 62], "side": [-8, -8], "expr": "worried"})},
     cam([2.1, -1.0, 1.3], [0.0, -0.9, 1.1], 17, 0.0), note="S47 I step on, ball at my chest")
shot("L48", {}, cam([0.0, -0.6, 0.5], [0.0, 14.6, 0.55], 95, 0.0), hand=0.002, note="S48 a fresh rack")
shot("L49", {}, cam([0.0, -0.6, 0.5], [0.0, 14.6, 0.9], 75, 0.0), hand=0.002, note="S49 the sweep lifts")
shot("L50", {}, cam([0.0, -0.6, 0.45], [0.0, 15.2, 1.35], 95, 0.0), hand=0, step=1, note="S50 THE REVEAL")
shot("L51", {}, cam([0.0, -0.6, 0.6], [0.0, 15.2, 1.75], 160, 0.0), hand=0, step=1, note="S51 both faces")
shot("L52", {}, cam([0.0, -0.6, 0.6], [0.0, 15.2, 2.0], 230, 0.0), hand=0, step=1, note="S52 wide eyes")
shot("L53", {}, mv([0.35, -3.2, 1.0], [0.0, -1.4, 2.8], [0.3, -3.1, 1.0], [0.0, -1.4, 2.85], 24, 24), step=1,
     note="S53 the light dips")
shot("L53.1", {}, cam([0.0, -0.6, 0.9], [0.0, 7.5, 1.5], 40, 0.0), hand=0, step=1, note="S54 halfway up")
shot("L55", {"me": ([0.0, -0.9], 180, {"expr": "scared"}),
             "dev": ([-0.4, -4.4], 180, {"expr": "neutral"}), "rosie": ([-1.4, -4.4], 180, {"expr": "neutral"}),
             "mags": ([-2.4, -4.4], 180, {"expr": "neutral"}), "tomasz": ([-3.4, -4.4], 180, {"expr": "neutral"})},
     cam([1.6, -1.6, 1.5], [-1.2, -4.3, 1.4], 20, 0.0), note="S55 behind me, still")
shot("L56", {"me": ([0.0, -0.9], 180, {"arms": [10, 10], "expr": "scared"})},
     cam([0.45, -3.4, 0.55], [0.0, 8.0, 0.25], 26, 0.0), step=1, hand=0.002, note="S56 I bowled")
shot("L57", {}, cam([1.0, 5.5, 0.35], [0.0, 7.6, 0.45], 30, 0.0), step=1, hand=0.002, note="S57 through where it stood")
shot("L58", {}, mv([0.4, 10.6, 0.5], [0.0, 15.0, 0.4], [0.2, 10.8, 0.5], [0.0, 15.0, 0.45], 45, 45), step=1,
     note="S58 all ten down")
shot("L59", {"me": ([0.0, -0.8], 0, {"expr": "soft", "arms": [20, 20]}), "dev": ([-1.0, -4.2], 180, {})},
     face_cam([0.0, -0.8], 0, 2.0, 22, v=0.16), step=1, note="S59 my first strike")

# 06 the twist (bright) -----------------------------------------------------------------------------------
shot("L60", {w: seat(w) for w in ("dev", "tomasz", "mags", "rosie")},
     cam([SCR_X, -6.6, 1.3], [SCR_X - 0.2, -3.4, 2.05], 28, 0.0), hand=0.002, note="S60 my picture slides up")
shot("L61", {w: seat(w) for w in ("dev", "tomasz", "mags", "rosie")},
     cam([SCR_X, -7.2, 1.3], [SCR_X, -3.4, 2.1], 30, 0.0), hand=0.002, note="S61 five rows")
shot("L62", {"me": seat("me", expr="soft"), "rosie": seat("rosie", expr="soft", talk=("L62", "L62>"))},
     cam([-3.2, -3.5, 1.45], [-3.4, -5.6, 1.42], 18, 0.1), note="S62 Rosie and Juno")
shot("L63", {w: seat(w, expr="soft") for w in ("dev", "tomasz", "mags", "rosie")},
     cam([-2.0, -2.5, 1.35], [-2.0, -5.6, 1.1], 13, 0.0), note="S63 four and an empty seat")
shot("L64", {}, cam([SCR_X, -5.4, 1.9], [SCR_X - 0.2, -3.4, 2.1], 24, 0.0), hand=0, note="S64 it bowls itself")
shot("L65", {"tomasz": seat("tomasz", expr="smirk", side=[28, 28], head=[0, 8]), "dev": seat("dev", expr="soft")},
     cam([-0.2, -3.4, 1.5], [-0.35, -5.6, 1.45], 17, 0.1), note="S65 shrugs")
shot("L66", {"mags": seat("mags", expr="soft", talk=("L66", "L66.2"))},
     face_cam([SEAT_X["mags"], SEAT_Y], 180, 2.2, 22), note="S66 Mags with the bag")
shot("L66.3", {"me": ([-1.5, -4.0], 0, {"expr": "soft"})},
     cam([-1.5, -6.0, 0.7], [-1.5, -4.0, 0.2], 28, 0.0), note="S66 my shoes")
shot("L67", {"dev": ([SEAT_X["dev"], SEAT_Y, SEAT_Z], -140, {"sit": True, "expr": "soft", "talk": ("L67.1", "L67>")})},
     cam([-1.3, -3.7, 1.55], [0.15, -5.6, 1.5], 24, 0.1), note="S67 Dev, take its place")
shot("L68", {"me": seat("me", expr="soft", head=[0, -4])}, face_cam([SEAT_X["me"], SEAT_Y], 180, 2.0, 22), note="S68 my grin")
shot("L69", {"mags": ([-1.0, -3.9], 0, {"arms": [0, 84], "side": [0, 34], "expr": "soft"})},
     cam([-1.0, -6.2, 1.5], [-1.0, -3.9, 1.3], 24, 0.1), note="S69 the fifth teal shirt")
shot("L69.2", {"me": ([-1.0, -3.9], 0, {"expr": "soft"})}, face_cam([-1.0, -3.9], 0, 2.0, 24), note="S69 me in it")

# 07 the warm turn and the freeze (bright) ----------------------------------------------------------------
shot("L70", {"tomasz": ([-0.85, -3.9], 0, {"arms": [168, 168], "expr": "wide", "talk": ("L70.1", "L70>")})},
     face_cam([-0.85, -3.9], 0, 2.4, 22, v=0.1), note="S70 forklift!")
ROW = {"dev": 0.2, "tomasz": -0.9, "mags": -2.0, "rosie": -3.1}
shot("L71", {w: ([x, -3.9], 0, {"arms": [88, 88], "expr": "soft", "keep_yaw": True}) for w, x in ROW.items()},
     cam([2.0, -0.4, 1.4], [-1.4, -3.4, 1.15], 22, 0.0), hand=0.002, note="S71 the team reverses")
shot("L72", {"me": ([-1.0, -3.9], 0, {"expr": "soft", "laugh": True})}, face_cam([-1.0, -3.9], 0, 1.9, 22, v=0.16),
     note="S72 I'm laughing")
shot("L73", {**{w: ([x, -3.9], 0, {"arms": [88, 88], "expr": "soft"}) for w, x in ROW.items()},
             "me": ([-4.2, -3.9], 0, {"arms": [88, 88], "expr": "soft"})},
     cam([-1.7, -0.9, 1.4], [-2.1, -3.9, 1.25], 14, 0.0), note="S73 I join the row")
shot("L74", {**{w: ([x - 0.2, -2.2], 0, {"arms": [88, 88], "expr": "soft"}) for w, x in
                (("dev", 0.8), ("tomasz", -0.3), ("mags", -1.4), ("rosie", -2.5))},
             "me": ([-3.6, -2.2], 0, {"arms": [88, 88], "expr": "soft"})},
     cam([-1.4, 5.5, 1.4], [-1.4, -2.2, 1.3], 24, 0.0), hand=0.003, note="S74 five grown-ups")
FIVE = {"dev": 0.6, "tomasz": -0.5, "mags": -1.6, "rosie": -2.7, "me": -3.8}
shot("L75", {w: ([x, -1.2], 0, {"arms": [88, 88], "expr": "soft", "freeze": True}) for w, x in FIVE.items()},
     cam([-1.7, -6.8, 3.25], [-1.7, 3.0, 0.1], 24, 0.0), hand=0, note="S75 FREEZE: five shadows")

shots = []
for i, s in enumerate(SHOTS):
    d = {"id": f"S{i + 1:02d}", "cam": s["cam"], "hand": s["hand"], "step": s["step"], "note": s["note"]}
    if i:
        d["at"] = s["at"]
    shots.append(d)

# ---------------------------------------------------------------------------------------------------- acting
# Every key carries "_o" = (shot index, order), so the lists end in time order whatever order they were written.
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "sit": False, "blink": True}
acting = {w: [] for w in WHO}
SHOT_AT = {}
for _i, _s in enumerate(SHOTS):
    SHOT_AT[_s["at"] if _i else 0] = _i
_seq = [0]


def _add(who, k, shot):
    _seq[0] += 1
    acting[who].append({**k, "_o": (shot, _seq[0])})


def put(who, shot, at, pos, yaw=0, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in sorted(keys, key=lambda k: k["_o"], reverse=True) if "pos" in k), None)
    if prev is not None:
        _add(who, {"at": at, "pos": prev}, shot)
    _add(who, {"at": at, "pos": pos, "yaw": yaw, "blend": 0, "hidden": False, "keep_yaw": True, **NEUTRAL,
               "expr": "neutral", **kw}, shot)


def hide(who, shot, at):
    _add(who, {"at": at, "hidden": True, "blend": 0}, shot)


def talk(who, shot, a, b):
    _add(who, {"from": a, "to": b, "mouth": [0.55, 0.55], "flap": True}, shot)


WALKS = {}


def walk(who, shot_at, at, pos, yaw):
    """A move inside the shot that starts at shot_at (footsteps on the boards)."""
    WALKS.setdefault(shot_at, []).append((who, at, pos, yaw))


for w, x in (("dev", -0.4), ("rosie", -0.9), ("mags", -0.5), ("tomasz", -0.9)):   # the entrance
    walk(w, "L03", "L03+0.05", [x, -6.6], 180)
walk("me", "L03", "L03+0.05", [-0.7, -7.7], 180)
walk("me", "L03", "L03+1.5", [-0.7, -6.9], 180)
walk("me", "L42", "L42+0.1", [0.0, -0.6], 180)                  # up to the line
walk("me", "L47", "L47+0.1", [0.0, -0.75], 180)                 # onto the approach
for w, x in ROW.items():                                         # the row reverses, facing the camera's side
    walk(w, "L71", "L71+0.3", [x, -3.9], 0)
    walk(w, "L71", "L71+2.9", [x, -2.4], 0)
walk("me", "L73", "L73+0.05", [-4.2, -3.9], 0)
walk("me", "L73", "L73+0.9", [-4.2, -3.2], 0)

for i, s in enumerate(SHOTS):
    at = s["at"] if i else 0
    for w in WHO:
        if w in s["scene"]:
            pos, yaw, opts = s["scene"][w]
            opts = dict(opts)
            tk = opts.pop("talk", None)
            laugh = opts.pop("laugh", False)
            opts.pop("freeze", None)
            opts.pop("keep_yaw", None)
            put(w, i, at, pos, yaw, **opts)
            if tk:
                talk(w, i, *tk)
            if laugh:
                _add(w, {"from": at, "to": "L73", "mouth": [0.6, 0.6], "flap": True}, i)
        else:
            hide(w, i, at)
    for (w, wat, wpos, wyaw) in WALKS.get(at, []):
        _add(w, {"at": wat, "pos": wpos, "yaw": wyaw, "keep_yaw": True}, i)


for w in WHO:
    acting[w].sort(key=lambda k: k["_o"])
    for k in acting[w]:
        del k["_o"]

# ---------------------------------------------------------------------------------------------------- cues
cues = [
    {"at": 0, "name": "spare", "hidden": True},
    {"at": "L22", "name": "spare", "lane": 3, "eyes": "shut", "key": 0.18, "rim": 0.6},
    {"at": "L23", "name": "spare", "lane": 3, "eyes": "shut", "key": 0.8, "rim": 1.0},
    {"at": "L31", "name": "spare", "lane": 2, "eyes": "slit", "bot": 0, "top": 0},
    {"at": "L33", "name": "spare", "lane": 2, "eyes": "slit", "bot": 18, "top": 0},
    {"at": "L38", "name": "spare", "lane": 1, "eyes": "half", "bot": 0, "top": 0},
    {"at": "L40", "name": "spare", "lane": 1, "eyes": "half", "bot": 55, "top": 50},
    {"at": "L41+0.65", "name": "spare", "lane": 1, "eyes": "half", "bot": 35, "top": 28},
    {"at": "L41+2.05", "name": "spare", "lane": 1, "eyes": "half", "bot": 12, "top": 8},
    {"at": "L43", "name": "spare", "hidden": True},
    {"at": "L50", "name": "spare", "lane": 0, "pos": [0.0, 15.2], "eyes": "wide", "gap": True, "bot": 0, "top": 0},
    {"at": "L53.1", "name": "spare", "lane": 0, "pos": [0.0, 7.5], "eyes": "wide", "bot": 0, "top": 0},
    {"at": "L57", "name": "spare", "hidden": True},
    # our pins
    {"at": 0, "name": "pins", "act": "up"},
    {"at": "L36.1", "name": "pins", "act": "fall"},
    {"at": "L37.2", "name": "pins", "act": "hide"},
    {"at": "L48", "name": "pins", "act": "drop"},
    {"at": "L58+0.05", "name": "pins", "act": "fall"},
    {"at": "L48", "name": "sweep", "act": "down"},
    {"at": "L49", "name": "sweep", "act": "up"},
    # the ball
    {"at": 0, "name": "ball", "hide": True},
    {"at": "L18", "name": "ball", "path": [[0, [0.05, -0.3, 0.11]], [0.5, [0.0, 2.0, 0.11]], [1.0, [-0.3, 5.0, 0.11]],
                                           [1.7, [-0.64, 10.5, 0.02]]]},
    {"at": "L19", "name": "ball", "path": [[0.2, [-0.8, -1.7, 0.23]], [1.3, [-0.8, -2.55, 0.23]]]},
    {"at": "L20", "name": "ball", "hide": True},
    {"at": "L56+0.1", "name": "ball", "path": [[0, [0.0, -0.2, 0.109]], [3.15, [0.0, 14.2, 0.109]]]},
    {"at": "L59", "name": "ball", "hide": True},
    # the lane lights: two slow dips in week three, one in week four, the house lights come up at the strike
    {"at": "L41", "name": "dip", "down": 0.5, "hold": 0.25, "up": 0.6, "depth": 0.55},
    {"at": "L41+1.45", "name": "dip", "down": 0.5, "hold": 0.25, "up": 0.6, "depth": 0.55},
    {"at": "L53", "name": "dip", "down": 0.6, "hold": 0.3, "up": 0.8, "depth": 0.55},
    {"at": "L58", "name": "house", "rise": 1.5},
    {"at": "L75-1.0", "name": "shadowlight", "on": 1.0},
    {"at": "L75-0.1", "name": "show", "what": "noscreen", "on": True},
    # props
    {"at": "L07", "name": "show", "what": "shoes", "on": True},
    {"at": "L08", "name": "show", "what": "shoes", "on": False},
    {"at": "L08", "name": "show", "what": "myshoes", "on": True},
    {"at": "L37", "name": "show", "what": "nachos", "on": True},
    {"at": "L38", "name": "show", "what": "nachos", "on": False},
    {"at": "L47", "name": "show", "what": "myball", "on": True},
    {"at": "L56", "name": "show", "what": "myball", "on": False},
    {"at": "L66", "name": "show", "what": "bag", "on": True},
    {"at": "L66.3", "name": "show", "what": "bag", "on": False},
    {"at": "L66.2", "name": "show", "what": "shoes", "on": True},
    {"at": "L66.3", "name": "show", "what": "shoes", "on": False},
    {"at": "L69", "name": "show", "what": "shirt", "on": True},
    {"at": "L69.2", "name": "show", "what": "shirt", "on": False},
    {"at": "L69.2", "name": "show", "what": "myshirt", "on": True},
    {"at": "L03", "name": "door", "open": 1.0},
    {"at": "L04", "name": "door", "open": 0.0},
    # the score screen: the fifth row scores on its own from the first night
    {"at": 0, "name": "screen", "lit5": 0, "dim": 0, "slide": 0, "sixth": 1, "n5": 1},
    {"at": "L10", "name": "screen", "n5": 2},
    {"at": "L12", "name": "screen", "n5": 3},
    {"at": "L12.1", "name": "screen", "n5": 4},
    {"at": "L12.2", "name": "screen", "n5": 5},
    {"at": "L14.1", "name": "screen", "lit5": 1, "dim": 1, "dur": 0.5},
    {"at": "L15.2", "name": "screen", "n5": 6, "sym5": ["", "", "", "", "", "/"]},
    {"at": "L17", "name": "screen", "lit5": 0, "dim": 0, "dur": 0.5},
    {"at": "L29.1", "name": "screen", "n5": 6, "sym5": ["", "", "", "", "/", "x"]},
    {"at": "L34.1", "name": "screen", "lit5": 1, "dim": 1, "dur": 0.5},
    {"at": "L36", "name": "screen", "lit5": 0, "dim": 0, "dur": 0.5},
    {"at": "L44.1", "name": "screen", "lit5": 1, "dim": 1, "dur": 0.5},
    {"at": "L60", "name": "screen", "dim": 0, "dur": 0.6},
    {"at": "L60.1", "name": "screen", "slide": 1, "sixth": 0, "dur": 1.0},
    {"at": "L60.2", "name": "screen", "n5": 6, "sym5": ["", "", "", "", "", "x"]},
    {"at": "L63", "name": "screen", "n5": 3, "sym5": []},
    {"at": "L64", "name": "screen", "n5": 4, "sym5": []},
    {"at": "L64.1", "name": "screen", "n5": 5, "sym5": ["", "", "", "", "x"]},
    {"at": "L64.2", "name": "screen", "n5": 6, "sym5": ["", "", "", "", "x", "x"]},
]

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L06", "kind": "alley_buzz", "db": -24, "dur": 1.6},
    {"at": "L18+0.05", "kind": "alley_roll", "db": -18, "dur": 1.7},
    {"at": "L18+1.5", "kind": "thud", "db": -26},
    {"at": "L19", "kind": "alley_roll", "db": -22, "dur": 1.3},
    {"at": "L19.2+0.3", "kind": "alley_thunk", "db": -14},
    {"at": "L36.1", "kind": "alley_clatter", "db": -12, "dur": 1.5},
    {"at": "L41", "kind": "alley_buzz", "db": -22, "dur": 1.5},
    {"at": "L41+1.45", "kind": "alley_buzz", "db": -21, "dur": 1.5},
    {"at": "L48", "kind": "alley_clunk", "db": -12},
    {"at": "L49", "kind": "alley_whirr", "db": -16, "dur": 1.1},
    {"at": "L50+0.02", "kind": "hit", "db": -8},
    {"at": "L53", "kind": "alley_buzz", "db": -15, "dur": 1.6},
    {"at": "L56+0.1", "kind": "alley_roll", "db": -16, "dur": 3.3},
    {"at": "L58+0.05", "kind": "alley_clatter", "db": -8, "dur": 1.5},
    {"at": "L60.2", "kind": "bell", "db": -26},
    {"at": "L71.2", "kind": "alley_beep", "db": -21, "pattern": [0, 0.53, 1.06, 1.58]},
    {"at": "L76-0.2", "kind": "alley_roll", "db": -22, "dur": 0.9},
    {"at": "L76.2+0.2", "kind": "alley_thunk", "db": -9},
]
story = {
    "slug": "ep29-ten-pin",
    "title": "My new workmates call me the Spare",
    "made_for_kids": False,
    "premise": "I'm new at the warehouse and my workmates take me to their Thursday bowling league at a tired old alley, where I'm called the Spare. Their score screen has a fifth row with no picture that scores on its own, and a bowler in our team shirt with a second head stacked on its own stands one lane nearer ours every week.",
    "twist": "The team was five until their friend Juno moved away. Every Thursday since, the fifth row bowled itself, and they called whatever bowled it the Spare. They gave me the name on purpose, to take its place, and when I bowl in the fifth row's turn my picture slides up into the fifth row and the thing is gone.",
    "world": "a tired eight-lane bowling alley on league nights: honey maple lanes, burgundy squiggle carpet, mustard seats, warm tungsten approaches, cold strip lights over the pin decks",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#3ad6c0",
    "gap": 0.12,
    "min_read": 0.12,
    "tail": 0,
    "look": {"fog": "#15131c", "fog_density": 0.03, "fog_start": 8.0, "sky": "#0c0b10", "exposure": 0.6},
    "grade": {"shadows": [-0.02, 0.0, 0.04], "highlights": [0.03, 0.01, -0.02], "saturation": 1.0, "contrast": 1.05,
              "vignette": 0.3, "bloom": 0.25, "grain": 0.012},
    "phonemes": {"nachos": "nˈɑtʃOz"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 50, "mode": "dorian", "bpm": 100, "seed": 29,
              "sections": [
                  {"at": 0, "voices": ["pad", "pulse"], "energy": 0.4},
                  {"at": "L20", "voices": ["pad"], "energy": 0.3},
                  {"at": "L21", "voices": ["drone", "pad"], "energy": 0.35},
                  {"at": "L31", "voices": ["drone", "pad", "pulse"], "energy": 0.4},
                  {"at": "L38", "voices": ["drone", "pad", "choir"], "energy": 0.35},
                  {"at": "L43", "voices": ["drone"], "energy": 0.25},
                  {"at": "L47", "voices": ["drone", "choir"], "energy": 0.4},
                  {"at": "L58", "voices": ["pad", "drone"], "energy": 0.3},
                  {"at": "L60", "voices": ["piano", "pad"], "energy": 0.4, "mode": "major"},
                  {"at": "L70", "voices": ["piano", "pad", "pulse"], "energy": 0.65, "mode": "major"},
                  {"at": "L75", "voices": ["pad", "piano"], "energy": 0.35, "mode": "major"},
              ]},
    "sound": {"floor": "wood", "steps_db": -20,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "end", "lufs": -34},
                  {"kind": "hum", "from": 0, "to": "L58", "lufs": -40},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "L49>", "to": "L50+0.7", "keep": ["hit"]}]},
}
story = _walk(story)
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
