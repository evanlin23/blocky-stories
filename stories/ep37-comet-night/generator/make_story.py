"""Writes ../story.json for ep37 "In this town, every promise ties a knot over your head" (script.md).

Run from anywhere: python stories/ep37-comet-night/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (keeper, knots, cloud, dome lights), the score and the sound.

Places (set.py's metres, z up). The square is at the origin (the civic steps at y 8.4 .. 11, facing south, the cafe
on the east, the old friends' bench on the west). The hill is at x = 200 (my house at y 0 facing north up the
slope, Mum's 16 m east, the dome 58 m up the slope). The dome's inside is at x = -300, drawn here as D(x, y, z):
the pier at (-0.45, 0.3), two chairs side by side at y -0.55 (Dad's at x -0.45, the second at 0.75), the arched
door in the south wall (y -4.4), the dusty stool at (2.9, 2.6), the chart table on the west wall.
A character with yaw 0 faces -y; yaw 180 faces +y; yaw 90 faces +x.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
nchunks = {ln["id"]: len(ln["chunks"]) for ln in lines}

HX, CX, Y0, TH, DOME_YL, SEAT = 200.0, -300.0, 12.0, math.radians(10), 58.0, 0.46
SITZ = SEAT - 0.68        # the feet's height for a sitter whose hips are on the seat


def hill(x, yl, zl=0.0):
    return [HX + x, Y0 + yl * math.cos(TH) - zl * math.sin(TH), yl * math.sin(TH) + zl * math.cos(TH)]


def D(x, y, z=0.0):
    return [CX + x, y, z]


# ---------------------------------------------------------------------------------------------------- lines
# pause beats (0.5 s) after L28, L31, L42, L44, L50, L62, and 0.3 s after L68 before the loop cut
PAUSES = {"L28": "P1", "L31": "P2", "L42": "P3", "L44": "P4", "L50": "P5", "L62": "P6"}
HOLDS = {"L61": 0.5, "L66": 0.5}                    # a line's gap, if the voice lands short
out_lines = []
for ln in lines:
    out_lines.append(ln)
    if ln["id"] in PAUSES:
        out_lines.append({"id": PAUSES[ln["id"]], "pause": 0.5, "chunks": []})
out_lines.append({"id": "P7", "pause": 0.3, "chunks": []})
for ln in out_lines:
    if ln["id"] in HOLDS:
        ln["gap"] = HOLDS[ln["id"]]
# the word check: slower reads where Whisper hears them wrong (filled in after the first asr run)
TEMPO = {"L12": 0.92, "L28": 0.92, "L59": 0.92, "L14": 0.95, "L16": 0.85}
SPOKEN = {("L12", 1): "it was one,", ("L28", 0): "And through it...", ("L14", 1): "Mum, said it", ("L16", 1): "week. He'd, be", ("L59", 1): "seat is not kept"}
for ln in out_lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]
    for k, ch in enumerate(ln.get("chunks", [])):
        if (ln["id"], k) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], k)]

# ---------------------------------------------------------------------------------------------------- cast
def person(skin, shirt, pants, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, collar=None, shoes="#2a2a2e",
           extras=None, extra_c=None, face=None, cord=None, hat="none", hat_c=None, sleeves="long", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "face": face or {"eyes": "round", "brows": True}}
    if pattern_c:
        d["pattern_c"] = pattern_c
    if collar:
        d["collar"] = collar
    if extras:
        d["extras"] = extras
    if extra_c:
        d["extra_c"] = extra_c
    if hat_c:
        d["hat_c"] = hat_c
    if cord:
        d["cord"] = cord
    d.update(kw)
    return d


DULL = [0.3, 0.3, 0.3]
cast = {
    "me": person("#f1c9a0", "#b5532c", "#232a3a", hair="cap", hair_c="#171414", collar="#e8dcc0", extras=["glasses"],
                 extra_c="#161616", face={"eyes": "round", "brows": True, "ink": "#1c1214"},
                 cord={"knots": [2.2], "late": True, "len": 0.3}),
    "dad": person("#e2b894", "#cdbf9e", "#6a6a6e", hair="cap", hair_c="#8a8a86", pattern="knit", pattern_c="#b8a888",
                  collar="#2f5a44", face={"eyes": "tired", "brows": True, "ink": "#201618", "bags": True},
                  cord={"grey": True, "knots": [0.0], "loose": True, "len": 0.34}),
    "mum": person("#d8a888", "#2f7f7a", "#3a3a44", hair="cap", hair_c="#2a2224", pattern="knit", pattern_c="#256862",
                  face={"eyes": "round", "brows": True, "ink": "#1c1214"}, cord={"knots": [1.4, 1.4], "len": 0.34}),
    "bride": person("#f2d2b4", "#f3ecd8", "#f3ecd8", hair="long", hair_c="#6a3b20", collar="#e6ddc4", shoes="#e8e0d0",
                    face={"eyes": "lashes", "brows": True, "ink": "#2a1818"}, cord={"knots": [2.4]}),
    "groom": person("#c89870", "#34363c", "#34363c", hair="cap", hair_c="#241810", extras=["tie"], extra_c="#a34a5a",
                    collar="#f3ecd8", face={"eyes": "round", "brows": True}, cord={"knots": [2.4]}),
    "callman": person("#e6bd96", "#3d5f8a", "#2b2f3a", hair="cap", hair_c="#5a3a20", face={"eyes": "tired", "brows": True},
                      cord={"knots": [0.3], "len": 0.34}),
    "friend1": person("#e8c3a0", "#b7a6d9", "#555a66", hair="cap", hair_c="#dadada", pattern="knit", pattern_c="#a090c8",
                      face={"eyes": "round", "brows": True}),
    "friend2": person("#c99a78", "#d3a53a", "#4c5260", hair="bun", hair_c="#d4d4d4", pattern="knit", pattern_c="#b98f2c",
                      face={"eyes": "lashes", "brows": True}),
    "mayor": person("#e3b890", "#6e1f35", "#2a2224", hair="buzz", hair_c="#555555", extras=["tie"], extra_c="#d6c27a",
                    collar="#f0e8d8", face={"eyes": "round", "brows": True}, cord={"knots": [1.8]}),
    "neighbour": person("#d9ac86", "#2f6a4a", "#2f3138", hair="cap", hair_c="#2c2c2c", face={"eyes": "round", "brows": True},
                        cord={"knots": [0.5]}),
    "lender": person("#b57e5c", "#e8c640", "#3a4a66", hair="bun", hair_c="#2c1a12", face={"eyes": "lashes", "brows": True},
                     cord={"knots": [1.9]}),
}
crowd_specs = [
    ("c1", "#e6bf9a", "#8a9a4a", "#3a3a44", "cap", "#3a2418", [0.35, 0.35, 0.35]),
    ("c2", "#b98a64", "#c4604a", "#2c3140", "spiky", "#1a1410", [0.3, 0.3]),
    ("c3", "#f0cfae", "#4a7aa8", "#30323a", "swoop", "#7a4a22", [0.3, 0.3, 0.3, 0.3]),
    ("c4", "#d1a27e", "#b090c0", "#3d3a44", "long", "#2a1a14", [0.35, 0.35]),
    ("c5", "#e4bb96", "#58806a", "#2d2f36", "cap", "#4a3220", [0.4, 2.0]),
    ("c6", "#a87656", "#d49a4a", "#3a3a48", "bun", "#1c1410", [0.35, 0.35, 0.35]),
    ("c7", "#efcba8", "#7a5a8a", "#30323a", "cap", "#9a6a30", [0.3]),
    ("c8", "#c89870", "#3f7f9a", "#2c2f38", "spiky", "#2a2018", [0.3, 0.3]),
]
for nm, skin, shirt, pants, hair, hair_c, kn in crowd_specs:
    cast[nm] = person(skin, shirt, pants, hair=hair, hair_c=hair_c, face={"eyes": "round", "brows": True},
                      cord={"knots": kn, "len": 0.34})


# ---------------------------------------------------------------------------------------------------- helpers
def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return c([0, loc, tgt, lens])


def move(a, b, lens_a, lens_b=None):
    return c([0, a[0], a[1], lens_a], [1, b[0], b[1], lens_b or lens_a])


def ref(lid, half=False, k=None):
    if k is not None:
        return f"{lid}.{k}"
    if half:
        return f"{lid}.{max(1, nchunks[lid] // 2)}"
    return lid


# ---------------------------------------------------------------------------------------------------- shots
# (id, at, scene, camera, step). scene: day, memory, dusk, night, dome
DOORSTEP = [HX, 1.3, 0.12]
SQ = "day"
SHOTS = [
    ("S01", None, SQ, still([0, 6.5, 2.3], [0.0, 9.9, 1.75], 19), 4),
    ("S02", ref("L01", True), SQ, move(([-3, -9, 8.5], [0, 3, 1]), ([3, -9, 9.2], [0, 3, 1]), 24), 4),
    ("S03", "L02", SQ, still([0.6, 7.0, 2.35], [0.15, 9.9, 2.2], 26), 4),
    ("S04", ref("L02", True), SQ, still([0, 5.3, 1.8], [0, 10.3, 1.55], 17), 4),
    ("S05", "L03", SQ, still([11.0, -2.6, 1.55], [9.3, -1.0, 1.35], 24), 4),
    ("S06", "L04", SQ, still([-5.7, -1.1, 1.5], [-8.5, -1.1, 1.35], 17), 4),
    ("S07", "L05", SQ, still([3.7, -0.2, 1.55], [3.5, 2.5, 1.45], 26), 4),
    ("S08", "L06", SQ, still([-2.9, -4.4, 1.6], [-2.7, -1.6, 1.45], 22), 4),
    ("S09", "L07", SQ, move(([-2, -10, 3.0], [0, 0, 1.5]), ([2, -10, 3.2], [0, 0, 1.5]), 22), 4),
    ("S10", "L08", SQ, still([0.7, -7.2, 1.9], [0, -2.2, 1.65], 22), 4),
    ("S11", "L09", SQ, still([0.1, -4.9, 1.7], [0, -2.2, 1.62], 32), 4),
    ("S12", "L10", "dome", still(D(-1.5, 0.5, 1.55), D(-0.45, -0.4, 1.5), 17), 4),
    ("S13", "L11", "dome", still(D(-1.2, 0.3, 1.9), D(-0.45, -0.4, 1.8), 25), 4),
    ("S14", "L12", "dusk", still([HX - 1.9, 3.6, 1.75], [HX, 1.3, 1.65], 24), 4),
    ("S15", "L13", "memory", still([HX + 0.5, 3.6, 1.8], [HX, 0.4, 1.7], 24), 4),
    ("S16", "L14", "dome", still(D(-1.15, 0.2, 1.75), D(-0.45, -0.4, 1.7), 21), 4),
    ("S17", "L15", "dusk", still([HX + 14.9, 4.4, 1.75], [HX + 16, 1.6, 1.65], 26), 4),
    ("S18", ref("L15", True), "dusk", still([HX + 3, 4, 2.0], hill(0, DOME_YL, 4.5), 55), 4),
    ("S19", "L16", "night", move(([HX + 14, -8, 4.5], [HX, 38, 6]), ([HX + 10, -8, 5.5], [HX, 38, 6]), 24), 4),
    ("S20", "L17", "night", c([0, [-1.7, 2.7, 1.45], [0, 0, 1.4], 28]), 2),
    ("S21", "L18", "dome", still(D(0.4, -2.3, 1.55), D(-0.45, -0.5, 1.5), 26), 4),
    ("S22", "L19", "dome", still(D(-0.1, -1.8, 1.5), D(-0.3, 1.4, 4.3), 22), 4),
    ("S23", "L20", "dome", still(D(2.0, 1.9, 1.4), D(0.15, -0.55, 0.7), 24), 4),
    ("S24", ref("L20", True), "dome", still(D(1.9, -1.7, 1.0), D(0.4, -0.5, 0.5), 30), 4),
    ("S25", "L21", "dome", still(D(1.1, 0.8, 1.5), D(2.9, 2.6, 1.15), 28), 4),
    ("S26", "L22", "dome", still(D(-1.3, 0.3, 1.85), D(-0.45, -0.4, 1.75), 24), 4),
    ("S27", "L23", "dome", still(D(-1.0, 0.5, 1.9), D(-0.45, -0.4, 1.8), 28), 4),
    ("S28", "L24", "dome", still(D(-1.3, 0.3, 1.6), D(-0.45, -0.4, 1.5), 18), 4),
    ("S29", "L25", "dome", still(D(-0.1, -0.95, 1.55), D(0, -3.85, 1.05), 30), 4),
    ("S30", "L26", "dome", still(D(-1.8, -0.9, 1.15), D(0, -3.85, 0.95), 30), 4),
    ("S31", "L27", "dome", still(D(-0.7, -2.3, 1.35), D(0, -3.85, 1.2), 38), 4),
    ("S32", "L28", "dome", move([D(-0.3, -2.5, 1.3), D(0, -3.85, 1.16)], [D(-0.1, -3.0, 1.25), D(0, -3.85, 1.16)], 50, 62), 4),
    ("S33", "L29", "dome", still(D(-2.1, -2.5, 1.25), D(0, -3.85, 1.15), 38), 4),
    ("S34", "L30", "dome", still(D(-0.4, -2.4, 1.6), D(0, -3.85, 1.85), 28), 4),
    ("S35", "L31", "dome", still(D(-1.2, -0.8, 1.4), D(0, -3.85, 1.0), 30), 4),
    ("S36", "L32", "dome", still(D(-1.3, 0.2, 1.75), D(-0.45, -0.4, 1.7), 20), 4),
    ("S37", "L33", "dome", still(D(1.4, 1.6, 1.4), D(-3.3, -0.5, 1.2), 30), 4),
    ("S38", "L34", "dome", still(D(-4.0, -0.5, 1.6), D(-0.45, -0.4, 1.4), 28), 4),
    ("S39", "L35", "dome", still(D(-1.1, 0.3, 1.5), D(-0.45, -0.45, 1.45), 24), 4),
    ("S40", "L36", "dome", still(D(-1.5, 0.2, 1.75), D(-0.45, -0.4, 1.75), 18), 4),
    ("S41", "L37", "dome", still(D(-1.8, -1.3, 1.25), D(-0.45, -0.55, 1.2), 26), 4),
    ("S42", "L38", "dome", still(D(1.7, 1.0, 1.4), D(0.75, -1.55, 1.1), 26), 4),
    ("S43", ref("L38", True), "dome", still(D(1.4, 0.9, 1.5), D(2.9, 2.6, 1.15), 20), 4),
    ("S44", "L39", "dome", still(D(1.5, -0.1, 1.5), D(0.75, -1.55, 1.7), 40), 4),
    ("S45", "L40", "dome", still(D(3.0, 3.0, 2.3), D(-0.2, -0.5, 1.2), 20), 4),
    ("S46", ref("L40", True), "dome", still(D(1.5, 1.0, 0.6), D(-0.2, 0.1, 0.55), 24), 4),
    ("S47", "L41", "dome", still(D(1.7, 1.4, 1.5), D(2.9, 2.6, 1.2), 20), 4),
    ("S48", "L42", "dome", still(D(2.7, 2.4, 1.25), D(-0.45, -1.5, 1.15), 45), 1),
    ("S49", "L43", "dome", still(D(2.3, -1.4, 1.4), D(-0.45, -1.2, 1.4), 40), 1),
    ("S50", "L44", "dome", still(D(-1.7, -0.3, 0.45), D(-0.45, -1.45, 1.25), 36), 1),
    ("S51", ref("L44", True), "dome", still(D(0.7, 0.0, 1.0), D(-0.45, -1.45, 1.2), 55), 1),
    ("S52", "L45", "dome", still(D(1.7, 1.4, 1.5), D(2.9, 2.6, 1.2), 20), 1),
    ("S53", "L46", "dome", still(D(2.7, 2.4, 1.25), D(-0.45, -1.5, 1.15), 36), 2),
    ("S54", ref("L46", True), "dome", still(D(-1.3, 0.3, 1.85), D(-0.45, -0.4, 1.75), 24), 4),
    ("S55", "L47", "dome", still(D(0.5, 2.0, 1.5), D(2.9, 2.6, 1.15), 20), 4),
    ("S56", "L48", "dome", still(D(-0.8, -1.3, 1.0), D(-0.2, 0.9, 5.0), 20), 4),
    ("S57", "L49", "dome", still(D(-0.6, 0.0, 0.6), D(-0.2, 0.3, 6.5), 22), 4),
    ("S58", "L50", "dome", still(D(-1.4, 0.4, 1.55), D(-0.45, -0.45, 1.45), 18), 4),
    ("S59", "L51", "dome", still(D(-1.3, -1.3, 1.9), D(-0.45, -0.45, 1.75), 18), 4),
    ("S60", ref("L51", True), "dome", still(D(1.6, 1.3, 1.5), D(2.9, 2.6, 1.15), 20), 4),
    ("S61", "L52", "dome", still(D(-1.6, -1.6, 1.4), D(-0.45, -0.5, 1.3), 20), 4),
    ("S62", "L53", "dome", still(D(2.6, 2.0, 1.4), D(0.75, -0.7, 1.0), 32), 1),
    ("S63", "L54", "dome", still(D(1.9, 1.0, 1.2), D(0.75, -0.65, 0.95), 34), 1),
    ("S64", "L55", "dome", still(D(1.3, 0.9, 1.5), D(2.9, 2.6, 1.15), 20), 4),
    ("S65", "L56", "memory", still([HX + 0.5, 3.6, 1.8], [HX, 0.4, 1.7], 24), 4),
    ("S66", "L57", "dome", still(D(1.9, -1.7, 1.0), D(0.4, -0.5, 0.5), 30), 4),
    ("S67", "L58", "dome", still(D(-2.0, -0.4, 1.5), D(-0.45, -0.45, 1.5), 20), 4),
    ("S68", "L59", "dome", still(D(1.3, 1.1, 1.5), D(2.9, 2.6, 1.15), 20), 4),
    ("S69", "L60", "dome", still(D(2.3, 1.7, 1.35), D(0.75, -0.55, 1.25), 28), 1),
    ("S70", "L61", "dome", still(D(3.0, 3.0, 2.3), D(-0.2, -0.5, 1.2), 20), 4),
    ("S71", "L62", "dome", still(D(-2.2, 1.6, 1.9), D(-0.2, -0.4, 1.1), 22), 4),
    ("S72", "L63", "dome", still(D(0.2, 2.6, 0.7), D(0.15, -0.55, 1.6), 20), 4),
    ("S73", "L64", "dome", still(D(1.4, 0.7, 1.5), D(0.75, -0.55, 1.45), 30), 4),
    ("S74", ref("L64", k=2), "dome", still(D(1.4, 1.0, 1.3), D(0.3, 0.0, 0.75), 28), 4),
    ("S75", ref("L65", k=1), "dome", still(D(0.7, 0.65, 1.9), D(-0.27, 0.654, 1.87), 28), 4),
    ("S76", "L66", "dome", still(D(0.15, 1.6, 1.45), D(0.15, -0.55, 1.45), 16), 4),
    ("S77", "L67", "dome", still(D(1.4, 0.6, 1.45), D(0.75, -0.55, 1.4), 28), 4),
    ("S78", "L68", "dome", still(D(0.15, 1.9, 1.5), D(0.15, -0.55, 1.5), 17), 4),
]
shots = []
for sid, at, scene, cam, step in SHOTS:
    s = {"id": sid, "cam": cam, "hand": 0.0 if step == 1 else 0.004, "step": step, "scene": scene}
    if at:
        s["at"] = at
    shots.append(s)
# S20: the camera follows me up the path (offsets from my feet)
for s in shots:
    if s["id"] == "S20":
        s["follow"] = "me"

# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "sit": False, "blink": True}
acting = {k: [] for k in cast}


def put(who, at, pos, yaw=0, expr="neutral", **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, "hidden": False, **NEUTRAL, "yaw": yaw, "expr": expr, **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": pos, **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


# the square, all standing from the start (hidden: me, until S10)
put("bride", 0, [-0.62, 9.9, 0.54], 0, "grin")
put("groom", 0, [0.62, 9.9, 0.54], 0, "grin")
put("c1", 0, [-2.6, 9.9, 0.54], 0, "neutral")
put("c2", 0, [-1.5, 10.5, 0.72], 0, "smirk")
put("c3", 0, [1.5, 10.5, 0.72], 0, "grin")
put("c4", 0, [2.6, 9.9, 0.54], 0, "neutral")
put("callman", 0, [9.3, -1.0, SEAT - 0.68], 90, "worried", sit=True, head=[0, 10])
put("friend1", 0, [-8.5, -1.7, SEAT - 0.68], 90, "grin", sit=True, head=[-15, 0])
put("friend2", 0, [-8.5, -0.5, SEAT - 0.68], 90, "grin", sit=True, head=[15, 0])
put("mayor", 0, [3.5, 2.5, 0], 0, "grin")
put("neighbour", 0, [-3.4, -1.6, 0], 90, "smirk", arms=[80, 80])
put("lender", 0, [-2.0, -1.6, 0], -90, "grin", arms=[80, 80])
put("c5", 0, [-1.6, -1.2, 0], 0, "neutral")
put("c6", 0, [1.9, -1.6, 0], 0, "smirk")
put("c7", 0, [-0.9, -3.8, 0], 0, "neutral")
put("c8", 0, [4.6, -2.0, 0], 0, "grin")
put("mum", 0, [HX + 16, 1.6, 0], 180, "worried", head=[0, -8])
put("dad", 0, D(-0.45, -0.58, SITZ), 180, "tired", sit=True, lean=10)
put("me", 0, [0, -2.2, 0], 0, "neutral", hidden=True)

# claps (S04 on L02, S09 on L07): hands apart, never touching
for who in ("c1", "c2", "c3", "c4"):
    key(who, ref("L02", True), arms=[82, 82], side=[-14, -14], blend=0.1)
    key(who, "L03", arms=[0, 0], side=[0, 0], blend=0.2)
for who in ("c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "bride", "groom", "mayor"):
    key(who, "L07", arms=[82, 82], side=[-14, -14], blend=0.1)
    key(who, "L08", arms=[0, 0], side=[0, 0], blend=0.3)
# the umbrella handover: the lender's knot lets go
key("lender", "L06", expr="grin")
# me in the square
put("me", "L08", [0, -2.2, 0], 0, "neutral", hidden=False)
key("me", "L09", expr="smirk", side=[38, 38], head=[0, 6], blend=0.25)
# me on my doorstep at dusk, looking up the hill
put("me", "L12", DOORSTEP, 180, "worried", head=[0, -10])
# Dad in my doorway ten years ago (S15), then back to the chair
put("dad", "L13", [HX, 0.45, 0], 180, "worried")
put("dad", "L14", D(-0.45, -0.58, SITZ), 180, "shut", sit=True, lean=10)
put("mum", "L15", [HX + 16, 1.6, 0], 180, "worried", head=[0, -10])
# me climbing the path (S20)
put("me", "L17", hill(0.4, 0.5), 180, "worried", head=[0, -6])
walk("me", "L18", hill(0.4, 3.4), yaw=180)
# the dome: Dad turns to the door, then back
put("dad", "L18", D(-0.45, -0.58, SITZ), 180, "wide", sit=True, lean=4)
key("dad", "L18", yaw=25, blend=0.35)
key("dad", "L19", yaw=180, expr="neutral", lean=10, blend=0.5)
put("me", "L21", D(2.9, 2.6, SITZ), -47, "neutral", sit=True, arms=[55, 55], side=[-35, -35])
key("dad", "L24", arms=[125, 125], expr="squeeze", head=[0, 14], lean=6, blend=0.4)
key("dad", "L25", arms=[0, 0], expr="tired", head=[0, 0], lean=10, blend=0.4)
key("me", "L25", expr="scared", arms=[0, 0], side=[0, 0])
key("me", "L31", expr="worried", head=[-40, 0])
key("dad", "L35", expr="blank")
key("me", "L33", expr="scared")
key("dad", "L36", expr="tired")
key("dad", "L37", expr="asleep", head=[0, 32], lean=15, blend=0.6)
key("me", "L38", expr="terrified", head=[0, 0])
key("dad", "L47", expr="asleep")
key("me", "L40", expr="worried")
key("me", "L42", expr="scared")
key("me", "L46", expr="terrified")
key("dad", "L48", expr="tired", head=[0, 0], lean=10, blend=0.8)
key("dad", "L50", head=[0, -22], expr="worried", lean=4, blend=0.9)
key("dad", "L51", head=[0, -32], expr="wide", lean=0, blend=0.5)
key("dad", "L52", head=[0, 6], expr="worried", lean=6, blend=0.7)
key("me", "L52", expr="worried")
key("me", "L53", expr="terrified")
key("me", "L55", expr="worried")
# the memory again (S65), then the dome
put("dad", "L56", [HX, 0.45, 0], 180, "soft")
put("dad", "L57", D(-0.45, -0.58, SITZ), 180, "soft", sit=True, lean=6, head=[-5, 0])
key("dad", "L58", head=[-62, 0], blend=0.6)
put("me", "L59", D(2.9, 2.6, 0), -47, "worried")
put("me", "L60", D(0.75, -0.58, SITZ), 180, "soft", sit=True, lean=4)
key("dad", "L61", expr="soft", head=[-45, 0], lean=2, blend=0.8)
key("me", "L62", expr="soft", head=[30, 0])
key("me", "L64", head=[35, 0], expr="soft")
key("dad", "L64", head=[-50, 0], expr="soft")
key("dad", "L66", expr="grin", head=[-40, 0], blend=0.2)
key("me", "L66", expr="grin", head=[30, 0], blend=0.2)
key("me", "L67", expr="soft", head=[0, 0], blend=0.5)
key("dad", "L67", head=[-30, 0])
key("me", "L68", expr="soft")
key("dad", "L68", expr="soft")
# the narrator's mouth is the narrator's: mine moves a little on "Hi, Dad" (flap) and the laugh (flap)
acting["me"].append({"from": ref("L64", k=2), "to": "L64>", "mouth": [0.6, 0.6], "flap": True})
acting["dad"].append({"from": "L66", "to": "L66>", "mouth": [0.55, 0.55], "flap": True})
acting["me"].append({"from": "L66", "to": "L66>", "mouth": [0.45, 0.45], "flap": True})
# the dad of the memory has darker hair ("hair" cue); everyone else is as built

# ---------------------------------------------------------------------------------------------------- cues
cues = []


def cue(name, at, **kw):
    cues.append({"at": at, "name": name, **kw})


# Dad's hair steps paler each night; the memory has dark hair
cue("hair", 0, who="dad", color="#8a8a86")
cue("hair", "L13", who="dad", color="#2e2a28")
cue("hair", "L14", who="dad", color="#8a8a86")
cue("hair", "L32", who="dad", color="#a2a29e")
cue("hair", "L36", who="dad", color="#b4b4b0")
cue("hair", "L40", who="dad", color="#c4c4c0")
cue("hair", "L56", who="dad", color="#2e2a28")
cue("hair", "L57", who="dad", color="#c4c4c0")
# Dad's knot: smaller and harder each night, a faint glow when new (the memory), loosening at L62
cue("knot", 0, who="dad", i=0, scale=1.0, glow=0.0)
cue("knot", "L11", who="dad", i=0, scale=0.93, dur=0.7)
cue("knot", "L13", who="dad", i=0, scale=1.3, glow=1.3, dur=0.0)
cue("knot", "L14", who="dad", i=0, scale=0.93, glow=0.0, dur=0.0)
cue("knot", "L14.1", who="dad", i=0, scale=0.88, dur=0.6)
cue("knot", "L23", who="dad", i=0, scale=0.82, dur=0.6)
cue("knot", "L32", who="dad", i=0, scale=0.76, dur=0.6)
cue("knot", "L36", who="dad", i=0, scale=0.7, dur=0.6)
cue("knot", "L46.1", who="dad", i=0, scale=0.62, dur=0.6)
cue("knot", "L51", who="dad", i=0, scale=0.56, dur=0.5)
cue("knot", "L56", who="dad", i=0, scale=0.0, glow=1.1, dur=0.0)
cue("knot", "L56+0.25", who="dad", i=0, scale=1.3, glow=1.1, dur=0.9)
cue("knot", "L57", who="dad", i=0, scale=0.56, glow=0.0, dur=0.0)
cue("knot", "L62", who="dad", i=0, scale=0.0, dur=1.2)
cue("cordset", 0, who="dad", len=0.34, stand=0.0)
cue("cordset", "L32", who="dad", len=0.31, stand=0.0, dur=0.5)
cue("cordset", "L36", who="dad", len=0.3, stand=1.0, dur=0.9)
cue("cordset", "L56", who="dad", len=0.34, stand=0.0, dur=0.0)
cue("cordset", "L57", who="dad", len=0.3, stand=1.0, dur=0.0)
cue("cordset", "L62", who="dad", len=0.34, stand=0.0, dur=1.2)
# the lender's kept promise (S08), my own new knot (S77)
cue("knot", ref("L06", k=1), who="lender", i=0, scale=0.0, dur=1.2)
cue("puff", ref("L06", k=1), who="lender", dur=1.2)
cue("puff", "L62", who="dad", dur=1.2)
cue("knot", "L67", who="me", i=0, scale=1.0, dur=1.0)
cue("cap", ref("L64", k=2))
# the sky through the slit: cloud over 3 s at L48, pink dawn over 8 s from L66
cue("cloud", 0, amount=0.0, pink=0.0)
cue("cloud", "L48", amount=1.0, dur=3.0)
cue("cloud", "L66", pink=1.0, dur=8.0)
# the dome's bulbs fade over 2 s, never a switch
cue("dome", 0, bulbs=1.0)
cue("dome", "L40", bulbs=0.0, dur=2.0)
cue("dome", "L46", bulbs=1.0, dur=2.0)
cue("dome", "L53", bulbs=0.0, dur=2.0)
cue("dome", "L61", bulbs=1.0, dur=2.0)
# the man with the hole
cue("keeper", 0, hidden=True)
cue("keeper", "L25", hidden=False, pos=[0, -3.85], yaw=180)
cue("keeper", ref("L31", k=2), hidden=True)
cue("keeper", "L33", hidden=False, pos=[-3.3, -0.5], yaw=90)
cue("keeper", "L36", hidden=True)
cue("keeper", "L38", hidden=False, pos=[0.75, -1.55], yaw=180, head=[0, 36])
cue("keeper", "L40", hidden=True)
cue("keeper", "L42", hidden=False, pos=[-0.45, -1.55], yaw=180, bend=26, head=[0, 10])
cue("keeper", "L46", hidden=True)
cue("keeper", "L53+1.5", hidden=False, pos=[0.75, -0.62], yaw=180, sit=0.55, head=[0, 8])
cue("keeper", "L60", hidden=True)
cue("streak", ref("L44", True), dur=1.5)

# ---------------------------------------------------------------------------------------------------- fx and sound
fx = []
sfx = [
    {"at": "L07", "kind": "bubbles", "db": -20, "dur": 1.6},                  # the clap swell
    {"at": ref("L06", k=1), "kind": "whoosh", "db": -24, "dur": 1.0},         # the puff
    {"at": "L11", "kind": "creak", "db": -18, "dur": 1.2},                    # the knot creak
    {"at": "L14.1", "kind": "creak", "db": -18, "dur": 1.2},
    {"at": "L22", "kind": "creak", "db": -16, "dur": 1.6},
    {"at": "L32", "kind": "creak", "db": -17, "dur": 1.4},
    {"at": "L36", "kind": "creak", "db": -16, "dur": 1.6},
    {"at": "L46.1", "kind": "creak", "db": -16, "dur": 1.4},
    {"at": "L51", "kind": "creak", "db": -12, "dur": 2.0},
    {"at": "L25", "kind": "sting", "db": -14},
    {"at": "L42", "kind": "sting", "db": -10},
    {"at": "L53+0.3", "kind": "sting", "db": -14},
    {"at": ref("L44", True), "kind": "whoosh", "db": -14, "dur": 1.2},        # the streak in the hole
    {"at": "L40", "kind": "riser", "db": -26, "dur": 2.0},
    {"at": "L62", "kind": "whoosh", "db": -22, "dur": 1.2},
    {"at": ref("L64", k=2), "kind": "click", "db": -16},                      # the cap's tick on wood
    {"at": "L12", "kind": "whoosh", "db": -34, "dur": 1.0},
]
music = {"root": 45, "mode": "minor", "bpm": 80, "seed": 37, "sections": [
    {"at": 0, "voices": ["pulse", "pad", "drone"], "energy": 0.5},
    {"at": "L10", "voices": ["drone", "pad", "pulse"], "energy": 0.38},
    {"at": "L17", "voices": ["drone", "pad"], "energy": 0.3},
    {"at": "L25", "voices": ["drone", "pad", "choir"], "energy": 0.4},
    {"at": "L40", "voices": ["drone", "choir"], "energy": 0.45},
    {"at": "L46", "voices": ["drone", "pad"], "energy": 0.3},
    {"at": "L53", "voices": ["drone", "choir"], "energy": 0.5},
    {"at": "L61", "voices": ["piano", "pad", "pulse"], "energy": 0.45, "mode": "major"},
]}
sound = {
    "floor": "wood", "steps_db": -22,
    "ambience": [
        {"kind": "room", "from": 0, "to": "L10", "lufs": -40},
        {"kind": "crickets", "from": "L12", "to": "L21", "lufs": -34},
        {"kind": "wind", "from": "L16", "to": "L21", "lufs": -36},
        {"kind": "hum", "from": "L21", "to": "end", "lufs": -40},
        {"kind": "room", "from": "L21", "to": "end", "lufs": -38},
    ],
    "sfx": sfx,
    "music_drops": [{"from": "L25-0.6", "to": "L25.1", "keep": ["sting"]},
                    {"from": "L42-0.6", "to": "L42.1", "keep": ["sting"]},
                    {"from": "L53-0.6", "to": "L53.1", "keep": ["sting"]}],
}

story = {
    "slug": "ep37-comet-night",
    "title": "In this town, every promise ties a knot over your head",
    "made_for_kids": False,
    "premise": "In my town every promise you make ties a small glowing knot onto a cord over your head until you keep it. I have no knots because I make no promises. My dad has the oldest knot in town, grey and hard, and in shooting-star week I go up to his hilltop observatory, where a man with a square hole through his chest stands a little nearer the empty second chair each night.",
    "twist": "The grey knot was never a broken promise: it was the one Dad kept every August, a saved seat that only counts as kept once I sit in it. The first line opens as a weight and turns into the longest-kept promise in town, and the narrator with no knots makes one.",
    "world": "a sunny cream-stone hill-town square with knotted cords bobbing over every head, a dry-grass hill, and a round stone observatory with a verdigris copper dome, its slit open to a made-up starfield",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff7aa8",
    "caption": {"ink": "#0a0b12", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#0d1528", "fog_density": 0.02, "fog_start": 14.0, "sky": "#8ec9f0", "sky_strength": 1.2,
             "exposure": 0.0, "flash_safe": True},
    "grade": {"shadows": [-0.015, 0.0, 0.035], "highlights": [0.02, 0.008, -0.01], "saturation": 0.88, "contrast": 1.06,
              "vignette": 0.34, "bloom": 0.3, "grain": 0.012},
    "phonemes": {"Mum": "mˈʌm"},
    "cast": cast,
    "lines": out_lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    "music": music,
    "sound": sound,
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
