"""Writes ../story.json for ep95-corn-maze (script.md, 2026-11-03). Run: python stories/ep95-corn-maze/generator/make_story.py

Words are in lines.json (51 lines). Places are in ../geo.py (shared with set.py). Every scene has its own origin (geo.ORG):
cameras and acting are written in the scene's local metres (x east, y away from the gate, z up) and converted here.
A character facing -y has yaw 0, +x 90, -x -90, +y 180. The camera lens is 34 everywhere so the lantern marker fits.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import geo as G  # noqa: E402

OUT = HERE.parent / "story.json"
import re
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = [], {}
for ln in orig_lines:   # captions are two or three words at a time: longer chunks are split, and chunk refs are remapped
    out, mp = [], []
    for cap, spoken in ln["chunks"]:
        cw, sw = cap.split(), spoken.split()
        n = len(cw)
        k = 1 if n <= 3 else (2 if n <= 6 else 3)
        sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
        mp.append(len(out))
        i = 0
        for sz in sizes:
            out.append([" ".join(cw[i:i + sz]), " ".join(sw[i:i + sz])])
            i += sz
    CHUNKMAP[ln["id"]] = mp
    lines.append({**ln, "chunks": out})
REF = re.compile(r"^(L\d+b?)\.(\d+)(.*)$")


def remap(x):
    if isinstance(x, str):
        m = REF.match(x)
        if m and m.group(1) in CHUNKMAP:
            return f"{m.group(1)}.{CHUNKMAP[m.group(1)][int(m.group(2))]}{m.group(3)}"
        return x
    if isinstance(x, list):
        return [remap(v) for v in x]
    if isinstance(x, dict):
        return {k: (v if k == "lines" else remap(v)) for k, v in x.items()}
    return x


REV = 10


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, hat="none", hat_c="#333333",
           extras=(), eyes="round", sleeves="long", ink="#24131f"):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes, "sleeves": sleeves,
         "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c, "face": {"eyes": eyes, "brows": True, "ink": ink}}
    if pattern_c:
        d["pattern_c"] = pattern_c
    if extras:
        d["extras"] = list(extras)
    return d


cast = {
    "june": {"age": "adult", "skin": "#e0b48c", "shirt": "#d8443a", "pattern": "plaid", "pants": "#3d5a80", "shoes": "#3a2a20",
             "sleeves": "long", "hair": "long", "hair_c": "#a8a8a8", "hat": "bucket", "hat_c": "#d8c070",
             "face": {"eyes": "round", "brows": True, "ink": "#24131f"}},
    "lost": person("#d9a577", "#2f6fb0", "#6a5a44", "#3a2a20", hair="swoop", hair_c="#3a2618", pattern="stripes", pattern_c="#e8f0f4"),
    "dad": person("#e8b890", "#4a7a4a", "#5a5040", "#4a3a2a", hair="cap", hair_c="#c8c8c8", pattern="plaid", pattern_c="#2a5236", extras=["glasses"]),
    "son": person("#c98f66", "#e07a30", "#2f3548", "#d8d8d8", hair="spiky", hair_c="#1a1210", sleeves="short"),
    "woman": person("#f0c8a0", "#2f8f8f", "#2a2a30", "#2a2a30", hair="long", hair_c="#6a2a1a", eyes="lashes"),
    "guy": person("#8a5a3a", "#c8402f", "#3a3a44", "#e8e8e8", hair="buzz", hair_c="#1c1a18", hat="beanie", hat_c="#e8d8a0"),
}

acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0]}] for n in cast}
last = {n: [0.0, 0.0] for n in cast}


def pw(sc, x, y):
    w = G.W(sc, x, y)
    return [w[0], w[1]]


def put(who, at, sc, x, y, yaw=None, z=None, **kw):
    """Appear at (x, y) on `at` (a jump, no walking across the cut). z lifts her onto a roof."""
    p = pw(sc, x, y) + ([z] if z is not None else [])
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False}
    if yaw is not None:
        k["yaw"] = yaw
    k.update(kw)
    acting[who].append(k)
    last[who] = p


def go(who, at, sc, x, y, z=None, **kw):
    p = pw(sc, x, y) + ([z] if z is not None else [])
    k = {"at": at, "pos": p}
    k.update(kw)
    acting[who].append(k)
    last[who] = p


def st(who, at, **kw):
    k = {"at": at, "pos": list(last[who])}
    k.update(kw)
    acting[who].append(k)


def hide(who, at):
    acting[who].append({"at": at, "pos": list(last[who]), "hidden": True, "blend": 0.0})


# ---------------------------------------------------------------------------------------------- shots and cameras
SHOTS = []      # (id, at, scene, layout, look, cam keys)


def C(sc, p, t, p2=None, t2=None, lens=34):
    a = [0, G.W(sc, *p), G.W(sc, *t), lens]
    if p2 is None and t2 is None:
        return [a]
    return [a, [1, G.W(sc, *(p2 or p)), G.W(sc, *(t2 or t)), lens]]


def shot(sid, at, sc, layout, look, cam, **kw):
    SHOTS.append(dict(id=sid, at=at, scene=sc, layout=layout, look=look, cam=cam, **kw))


def end_of(sid):
    ids = [s["id"] for s in SHOTS]
    i = ids.index(sid)
    return SHOTS[i + 1]["at"] if i + 1 < len(ids) else "end"


# the order matters: shots and acting are added together, in time order.
# ------------------------------------------------------------------ S01 to S03: the hook
shot("S01a", 0, "entrance", "entrance", "dusk", C("entrance", (0.3, -2.6, 1.8), (0.3, 0, 1.92), (0.3, -2.0, 1.85), (0.3, 0, 1.92)))
shot("S01b", "L01.1", "entrance", "entrance", "dusk", C("entrance", (0.55, -2.4, 1.9), (0.3, 0, 1.9), (0.4, -2.0, 1.88), (0.3, 0, 1.88)))
shot("S01c", "L01.2", "entrance", "entrance", "dusk", C("entrance", (0.3, -1.6, 1.78), (0.3, 0, 1.82), (0.3, -1.3, 1.78), (0.3, 0, 1.82)))
shot("S02", "L02", "entrance", "entrance", "dusk", C("entrance", (0.2, -16, 0.45), (1.5, 2, 1.0), (0.2, -11.5, 0.5), (1.5, 2, 1.0)))
put("woman", "L03", "day", -2.6, -30.6, 45)
go("woman", "L03.1", "day", -0.6, -28.2)
put("guy", "L03", "day", 2.6, -31.2, -40)
go("guy", "L03.1", "day", 0.7, -28.3)
shot("S03a", "L03", "day", "day", "dusk", C("day", (-5.5, -35.5, 1.6), (-0.5, -28.5, 1.4), (-4.6, -35.0, 1.6), (-0.4, -28.5, 1.4)))
put("dad", "L03.1", "day", -4.0, -31.8, 70, expr="neutral")
go("dad", "L04", "day", -1.2, -31.0)
put("son", "L03.1", "day", -5.2, -31.6, 70)
go("son", "L04", "day", -2.7, -31.0)
hide("woman", "L03.1")
hide("guy", "L03.1")
shot("S03b", "L03.1", "day", "day", "dusk", C("day", (-1.0, -34.2, 1.5), (-2.4, -29.0, 1.55), (-1.6, -33.6, 1.5), (-2.4, -29.0, 1.55)))
hide("dad", "L04")
hide("son", "L04")
# ------------------------------------------------------------------ S04 to S10: the montage
put("lost", "L04", "day", 0.0, 4.5, 0, expr="worried")
st("lost", "L04+0.4", yaw=-110, blend=0.4, side=[40, 40])
st("lost", "L05-0.2", yaw=-250, blend=0.5, side=[50, 20])
shot("S04", "L04", "day", "day", "dusk", C("day", (0.0, -2.0, 1.5), (0.0, 4.5, 1.3), (1.0, -0.4, 1.5), (0.0, 4.5, 1.3)))
put("lost", "L05", "day", 0.0, 4.5, 20, expr="worried", head=[0, 0])
shot("S05a", "L05", "day", "day", "dusk", C("day", (0.5, 2.0, 0.9), (-0.6, 4.4, 1.3), (0.5, 2.6, 1.0), (-0.7, 4.5, 1.4)))
st("lost", "L05.2", expr="wide", head=[28, 6], yaw=10, blend=0.3)
shot("S05b", "L05.2", "day", "day", "dusk", C("day", (1.0, 0.2, 1.6), (0.0, 4.5, 1.45), (0.6, 0.6, 1.6), (0.0, 4.5, 1.45)))
hide("lost", "L06")
shot("S06", "L06", "day", "day", "dusk", C("day", (0.8, 3.0, 1.6), (-0.3, 8.5, 1.7), (0.3, 4.2, 1.65), (-0.5, 8.5, 1.75)))
put("lost", "L07", "day", 8.55, 3.9, 180, expr="worried")
go("lost", "L08-0.15", "day", 8.55, 0.4)
shot("S07", "L07", "day", "day", "dusk", C("day", (8.7, 7.1, 2.0), (8.4, -1.0, 0.8), (8.7, 7.1, 2.1), (8.4, -2.0, 0.8)))
hide("lost", "L08")
put("dad", "L08", "day", -0.6, -31.0, 180, expr="angry", side=[0, 75])
put("son", "L08", "day", 0.6, -31.0, 180, expr="angry", side=[75, 0])
go("dad", "L08.2", "day", -0.6, -28.6)
go("son", "L08.2", "day", 0.6, -28.6)
shot("S08a", "L08", "day", "day", "dusk", C("day", (0.5, -36.0, 1.6), (0.0, -29.5, 1.5), (0.2, -35.0, 1.55), (0.0, -29.5, 1.5)))
put("dad", "L08.2", "day", 7.6, -24.3, 0, expr="laugh", side=[35, 0])
put("son", "L08.2", "day", 8.55, -24.3, 0, expr="laugh", side=[0, 0])
go("dad", "L09-0.1", "day", 7.6, -27.0)
go("son", "L09-0.1", "day", 8.55, -27.0)
shot("S08b", "L08.2", "day", "day", "dusk", C("day", (8.0, -33.0, 1.5), (8.0, -26.0, 1.4), (8.0, -32.0, 1.5), (8.0, -26.2, 1.4)))
hide("dad", "L09")
hide("son", "L09")
shot("S09a", "L09", "day", "day", "dusk", C("day", (-17.0, 19.4, 0.38), (-17.0, 21.0, 0.03), (-17.0, 19.9, 0.28), (-17.0, 21.0, 0.03)))
shot("S09b", "L09.1", "day", "day", "dusk", C("day", (9.3, -30.9, 1.35), (10.4, -28.4, 0.95), (9.7, -30.4, 1.25), (10.4, -28.4, 0.98)))
put("woman", "L09.3", "day", 8.4, -31.4, 20, expr="wide")
go("woman", "L09.3+0.6", "day", 9.65, -29.9, arms=[0, 0])
st("woman", "L10-0.15", arms=[70, 70], yaw=40)
shot("S09c", "L09.3", "day", "day", "dusk", C("day", (7.2, -34.5, 1.4), (9.6, -29.3, 1.2), (7.8, -34.0, 1.4), (9.8, -29.4, 1.2)))
hide("woman", "L10")
put("guy", "L10", "day", 15.0, 1.6, 0, expr="grin", arms=[0, 165], head=[-25, 0])
st("guy", "L10.2", head=[-25, 0])
shot("S10a", "L10", "day", "day", "dusk", C("day", (15.0, -3.8, 1.5), (15.0, 2.0, 1.4), (15.0, -2.6, 1.5), (15.0, 2.0, 1.4)))
shot("S10b", "L10.2", "day", "day", "dusk", C("day", (15.6, -0.3, 1.55), (15.0, 2.0, 1.5), (15.4, 0.3, 1.55), (15.0, 2.0, 1.5)))
st("guy", "L10.2+0.1", expr="laugh")
hide("guy", "L11")
shot("S11", "L11", "day", "day", "dusk", C("day", (0.1, -10.5, 0.7), (0.0, 0.0, 1.2), (0.1, -6.2, 0.78), (0.0, 6.0, 1.35)))
# S12: four groups in four paths at the same moment
put("lost", "L12", "day", 0.0, -16.0, 180, expr="neutral")
go("lost", "L13-0.05", "day", 0.0, -13.4)
put("dad", "L12", "day", 7.7, -8.0, 0, expr="laugh")
put("son", "L12", "day", 8.6, -8.0, 0, expr="laugh")
go("dad", "L13-0.05", "day", 7.7, -10.4)
go("son", "L13-0.05", "day", 8.6, -10.4)
put("woman", "L12", "day", -9.0, 15.0, 180, expr="neutral")
go("woman", "L13-0.05", "day", -9.0, 17.3)
put("guy", "L12", "day", -12.0, -9.0, 180, expr="grin")
go("guy", "L13-0.05", "day", -12.0, -6.7)
shot("S12", "L12", "day", "day", "dusk", C("day", (0.0, -63.0, 42.0), (0.0, -2.0, 0.0), (0.0, -58.0, 38.0), (0.0, -2.0, 0.0)))
for w in ("lost", "dad", "son", "woman", "guy"):
    hide(w, "L13")
# ------------------------------------------------------------------ S13 to S19: June's summers
put("june", "L13", "summer", -6.6, -29.8, 90, expr="smile", arms=[60, 60])
go("june", "L14-0.05", "summer", -4.4, -29.6)
shot("S13", "L13", "summer", "summer", "summer", C("summer", (-1.5, -36.0, 1.5), (-5.0, -29.6, 1.1), (-2.5, -35.5, 1.5), (-5.0, -29.4, 1.1)), mower=True)
put("june", "L14", "summer", -4.0, -24.2, 180, expr="smile", arms=[60, 60])
go("june", "L14.2-0.05", "summer", -4.0, -22.5)
shot("S14a", "L14", "summer", "summer", "summer", C("summer", (-4.2, -18.8, 1.7), (-4.0, -23.2, 1.3), (-4.2, -19.4, 1.7), (-4.0, -22.6, 1.3)), mower=True)
put("june", "L14.2", "summer", -4.0, -22.5, 180, expr="smile", arms=[60, 60])
go("june", "L15-0.05", "summer", -4.0, -21.2)
shot("S14b", "L14.2", "summer", "summer", "summer", C("summer", (-6.2, -27.5, 2.5), (-0.5, -10.0, 0.8), (-5.0, -27.0, 2.4), (-0.5, -10.0, 0.8)), mower=True)
put("june", "L15", "summer", 0.15, -12.2, -90, expr="laugh", arms=[0, 0], blend=0.0)
acting["june"].append({"at": "L15", "from": "L15", "to": "L15>", "mouth": [0.6, 0.6], "flap": True})
st("june", "L15+0.3", arms=[50, 10], side=[0, 25], blend=0.2)
st("june", "L15+0.65", arms=[10, 60], side=[25, 0], blend=0.2)
st("june", "L15+1.0", arms=[40, 40], side=[10, 10], blend=0.2)
shot("S15", "L15", "summer", "summer", "summer", C("summer", (4.2, -9.6, 2.1), (0.1, -12.3, 1.3), (4.0, -10.4, 2.1), (0.1, -12.3, 1.3)))
put("june", "L16", "summer", 2.55, -4.2, -90, expr="soft", arms=[0, 65], lean=-5)
st("june", "L16+0.5", lean=-3, arms=[0, 75])
shot("S16", "L16", "summer", "summer", "summer", C("summer", (0.9, -8.0, 1.7), (2.5, -4.3, 1.25), (1.3, -7.6, 1.7), (2.5, -4.3, 1.25)))
hide("june", "L17")
shot("S17", "L17", "partial", "partial", "summer", C("partial", (4.0, -45.0, 15.0), (-3.0, -9.0, 0.0), (4.0, -45.0, 15.0), (0.0, -9.0, 0.0)))
put("june", "L18", "summer", -8.0, 14.0, 0, expr="soft", side=[75, 0], arms=[0, 0])
st("june", "L18+0.3", side=[60, 0])
st("june", "L18.1", side=[78, 0])
st("june", "L18.1+0.35", side=[62, 0])
shot("S18a", "L18", "summer", "summer", "summer", C("summer", (-7.0, 9.2, 1.8), (-8.3, 14.0, 1.3), (-7.2, 9.8, 1.75), (-8.4, 14.0, 1.3)))
st("june", "L18+0.8", expr="soft", head=[0, 0])
shot("S18b", "L18+0.8", "summer", "summer", "summer", C("summer", (-8.1, 10.3, 1.7), (-8.0, 14.0, 1.55), (-8.1, 11.0, 1.65), (-8.0, 14.0, 1.55)))
hide("june", "L19")
# S19: daylight, June strides through the open maze with her mug and takes the turn without looking (a), then stops at a fork
# where the stalks are perfectly still and tilts her head to listen, as the lost man did (b)
put("june", "L19", "day", 0.0, 4.4, 180, expr="content", arms=[0, 0], head=[0, -22])
go("june", "L19+0.8", "day", 0.0, 6.0)
go("june", "L19.1-0.1", "day", -2.6, 6.0)
shot("S19a", "L19", "day", "day", "dusk", C("day", (4.2, 6.0, 1.5), (-0.4, 5.2, 1.4), (3.6, 6.1, 1.5), (-0.8, 5.4, 1.4)))
put("june", "L19.1", "day", 0.0, 4.5, 20, expr="curious", arms=[0, 0], head=[28, 6])
st("june", "L19.1+0.5", head=[32, 8])
shot("S19b", "L19.1", "day", "day", "dusk", C("day", (0.5, 0.2, 1.6), (0.0, 4.5, 1.45), (0.3, 0.7, 1.6), (0.0, 4.5, 1.45)))
# ------------------------------------------------------------------ S20 to S27: the last night
put("june", "L20", "day", -3.4, -30.2, 121, expr="neutral", arms=[70, 70])
go("june", "L20.1+0.2", "day", -1.2, -28.9)
go("june", "L21", "day", -0.3, -28.3)
shot("S20", "L20", "day", "day", "lantern", C("day", (0.4, -24.0, 1.5), (-1.4, -29.0, 1.4), (0.2, -26.0, 1.45), (-1.5, -29.4, 1.4)))
go("june", "L22-0.1", "day", 0.0, -24.3)
shot("S21", "L21", "day", "day", "lantern", C("day", (0.2, -21.4, 1.5), (0.0, -26.0, 1.2), (0.1, -22.4, 1.5), (0.0, -26.0, 1.2)))
put("june", "L22", "day", 0.0, -19.4, 180, expr="neutral", arms=[70, 70])
go("june", "L23-0.05", "day", 0.0, -16.2)
shot("S22", "L22", "day", "day", "lantern", C("day", (-0.1, -11.6, 1.5), (0.0, -20.5, 1.7), (0.0, -12.4, 1.5), (0.0, -21.5, 1.7)))
put("june", "L23", "day", 0.0, 5.4, -120, expr="neutral", arms=[70, 70], look=[0.8, 0])
shot("S23a", "L23", "day", "day", "lantern", C("day", (-4.4, 5.6, 1.5), (1.0, 6.0, 1.45), (-3.6, 5.8, 1.5), (0.6, 6.2, 1.45)))
shot("S23b", "L23.2", "day", "day", "lantern", C("day", (8.0, 4.6, 1.5), (8.0, -14.0, 1.9), (8.0, 2.4, 1.5), (8.0, -14.0, 1.9)))
put("june", "L24", "day", 0.2, 5.7, -150, expr="neutral", arms=[70, 70])
st("june", "L24+0.15", yaw=100, look=[0, 0], blend=0.2)
go("june", "L25-0.05", "day", -1.4, 6.0)
shot("S24", "L24", "day", "day", "lantern", C("day", (-6.5, 6.0, 1.5), (0.0, 6.0, 1.4), (-6.0, 6.2, 1.5), (-0.5, 6.0, 1.4)))
shot("S25a", "L25", "day", "day", "lantern", C("day", (-4.6, 5.6, 1.15), (-0.6, 7.2, 1.4), (-4.2, 5.8, 1.15), (-0.9, 7.0, 1.4)))
shot("S25b", "L25.1", "day", "day", "lantern", C("day", (-3.3, 6.1, 1.25), (-1.2, 6.8, 1.4), (-2.6, 6.2, 1.3), (-1.3, 6.9, 1.4)))
put("june", "L26", "day", -7.6, 6.0, -90, expr="neutral", arms=[40, 70])
go("june", "L26+0.45", "day", -9.0, 6.3)
go("june", "L27-0.05", "day", -9.0, 7.9)
shot("S26", "L26", "day", "day", "lantern", C("day", (-9.0, 11.8, 1.5), (-8.2, 6.4, 1.4), (-9.0, 11.0, 1.5), (-9.0, 7.4, 1.4)))
hide("june", "L27")
shot("S27a", "L27", "day", "day", "lantern", C("day", (7.7, -22.0, 2.6), (7.05, -26.2, 2.95), (7.6, -23.2, 2.7), (7.05, -26.2, 2.95)))
put("june", "L27.2", "day", -9.0, 11.0, 180, expr="neutral", arms=[40, 70])
go("june", "L28-0.05", "day", -9.0, 11.6)
shot("S27b", "L27.2", "day", "day", "lantern", C("day", (-9.4, 15.4, 0.9), (-9.0, 11.3, 1.3), (-9.2, 15.0, 0.95), (-9.0, 11.4, 1.3)))
# ------------------------------------------------------------------ S28 to S33: lights out
put("june", "L28", "day", -9.0, 11.2, 180, expr="neutral", arms=[40, 70])
go("june", "L28.1", "day", -9.0, 12.6)
shot("S28a", "L28", "day", "day", "moon", C("day", (-9.0, 18.6, 1.9), (-9.0, 11.2, 1.2), (-9.0, 17.8, 1.9), (-9.0, 11.2, 1.2)))
go("june", "L29-0.05", "day", -9.0, 14.0)
shot("S28b", "L28.1", "closed", "closed", "moon", C("closed", (-9.0, 17.6, 0.7), (-9.0, 11.0, 1.8), (-9.0, 17.0, 0.8), (-9.0, 11.0, 1.8)))
put("june", "L29", "closed", -9.0, 14.0, 180, expr="worried", arms=[40, 70])
go("june", "L29.2", "closed", -9.0, 15.4)
shot("S29a", "L29", "closed", "closed", "moon", C("closed", (-9.0, 18.8, 1.4), (-9.0, 13.0, 1.4), (-9.0, 18.2, 1.4), (-9.0, 13.0, 1.4)))
hide("june", "L29.2")
shot("S29b", "L29.2", "closed", "closed", "moon", C("closed", (-9.0, 12.4, 0.8), (-9.0, 9.2, 1.4), (-9.0, 11.8, 0.85), (-9.0, 9.2, 1.45)))
# S29c to S29e (L29b): the next path closes too, then the pocket she's left in, corn on every side
put("june", "L29b", "closed", -9.0, 14.0, -70, expr="worried", arms=[40, 70])
shot("S29c", "L29b", "closed", "closed", "moon", C("closed", (-9.0, 10.0, 1.45), (-10.6, 14.0, 1.3), (-9.0, 10.4, 1.45), (-10.3, 14.0, 1.3)))
shot("S29d", "L29b+0.3", "nosid", "nosid", "moon", C("nosid", (-9.0, 10.0, 1.45), (-10.6, 14.0, 1.3), (-9.0, 10.4, 1.45), (-10.3, 14.0, 1.3)))
put("june", "L29b.1", "sealed", -9.0, 14.0, 0, expr="worried", arms=[40, 70], blend=0.0)
st("june", "L29b.1+0.1", yaw=0)
st("june", "L29b.1+0.3", yaw=130, blend=0.3)
st("june", "L29b.1+0.6", yaw=250, blend=0.3)
st("june", "L29b.1+0.9", yaw=360, blend=0.3)
shot("S29e", "L29b.1", "sealed", "sealed", "moon", C("sealed", (-9.0, 11.0, 0.8), (-9.0, 14.0, 1.35), (-9.0, 11.4, 0.8), (-9.0, 14.0, 1.4)))
put("june", "L30", "closed", -9.0, 29.3, 0, expr="neutral", arms=[0, 0])
go("june", "L30.1+0.1", "closed", -9.0, 27.35)
st("june", "L30.1+0.25", yaw=0, blend=0.3)
st("june", "L30.2", sit=True, expr="soft", arms=[55, 55])
shot("S30a", "L30", "closed", "closed", "moon", C("closed", (-8.2, 24.1, 1.4), (-9.0, 26.8, 1.0), (-8.3, 24.5, 1.35), (-9.0, 26.9, 0.85)))
shot("S30b", "L30.2", "closed", "closed", "moon", C("closed", (-9.0, 23.8, 0.8), (-9.0, 27.0, 0.55), (-8.8, 24.2, 0.75), (-9.0, 27.0, 0.55)))
st("june", "L30.2+0.7", arms=[30, 60])
shot("S30c", "L30.2+0.7", "closed", "closed", "moon", C("closed", (-9.3, 24.4, 0.55), (-9.0, 25.65, 0.2), (-9.2, 24.6, 0.5), (-9.0, 25.65, 0.22)))
st("june", "L31", expr="smile", arms=[0, 0], head=[0, 0])
shot("S31", "L31", "closed", "closed", "moon", C("closed", (-9.0, 24.8, 1.0), (-9.0, 27.2, 0.72), (-9.0, 24.5, 0.95), (-9.0, 27.2, 0.75)))
shot("S32", "L32", "closed", "closed", "moon", C("closed", (-8.2, 25.2, 0.95), (-10.6, 29.8, 1.4), (-8.6, 25.6, 0.95), (-10.6, 29.8, 1.5)))
hide("june", "L33")
# S33: low on the empty straw where feet would be, tilted down, then straight up out of the corn
shot("S33", "L33", "closed", "closed", "moon", [[0, G.W("closed", -9.0, 12.8, 1.2), G.W("closed", -9.0, 12.2, 0.15), 34],
                                              [0.45, G.W("closed", -9.0, 12.8, 2.2), G.W("closed", -9.0, 12.4, 0.0), 34],
                                              [1, G.W("closed", -9.0, 13.0, 24.0), G.W("closed", -9.0, 13.2, 0.0), 34]])
shot("S34", "L34", "face", "face", "moonhi", [[0, G.W("face", 0.0, -5.0, 152.0), G.W("face", 0.0, -4.7, 0.0), 34],
                                           [1, G.W("face", 0.0, -5.0, 144.0), G.W("face", 0.0, -4.7, 0.0), 34]])
# ------------------------------------------------------------------ S35 to S41: the reveal explained
put("june", "L35.1", "summer", -4.0, -22.6, 180, expr="laugh", arms=[60, 60])
go("june", "L35.2-0.05", "summer", -4.0, -21.3)
shot("S35a", "L35.1", "summer", "summer", "summer", C("summer", (-4.2, -18.8, 1.7), (-4.0, -23.2, 1.3), (-4.2, -19.4, 1.7), (-4.0, -22.6, 1.3)), mower=True)
put("june", "L35.2", "summer", -8.0, 14.0, 0, expr="smile", side=[80, 0], arms=[0, 0])
acting["june"].append({"at": "L35.2", "from": "L35.2", "to": "L36", "mouth": [0.5, 0.5], "flap": True})
st("june", "L35.2+0.4", side=[70, 0])
shot("S35b", "L35.2", "summer", "summer", "summer", C("summer", (-6.8, 12.4, 1.45), (-9.1, 14.2, 1.35), (-7.2, 12.8, 1.45), (-9.1, 14.2, 1.35)))
hide("june", "L36")
shot("S36", "L36", "day", "day", "dusk", C("day", (0.1, -9.0, 0.6), (0.0, 0.0, 1.2), (0.1, -5.0, 0.65), (0.0, 4.0, 1.3)))
put("june", "L37", "closed", -9.0, 27.35, 0, expr="smile", sit=True, snap=True, arms=[0, 0], blend=0.0)
shot("S37", "L37", "closed", "closed", "moon", C("closed", (-6.7, 24.8, 1.1), (-9.0, 27.4, 0.85), (-6.8, 25.2, 1.1), (-9.0, 27.4, 0.85)))
hide("june", "L38")
put("lost", "L38", "day", 0.0, 4.5, 20, expr="wide", head=[28, 6])
shot("S38a", "L38", "day", "day", "dusk", C("day", (1.0, 0.2, 1.6), (0.0, 4.5, 1.45), (0.6, 0.6, 1.6), (0.0, 4.5, 1.45)))
shot("S38b", "L38.2", "day", "day", "dusk", C("day", (0.5, 2.0, 0.9), (-0.6, 4.4, 1.3), (0.5, 2.6, 1.0), (-0.7, 4.5, 1.4)))
hide("lost", "L39")
put("june", "L39", "closed", -9.0, 27.35, 0, expr="soft", sit=True, snap=True, arms=[0, 0], blend=0.0)
shot("S39", "L39", "closed", "closed", "moon", C("closed", (-7.4, 24.4, 1.05), (-9.0, 27.2, 0.8), (-7.6, 24.6, 1.0), (-9.0, 27.2, 0.8)))
shot("S40", "L40", "closed", "closed", "moon", C("closed", (-9.7, 24.4, 0.6), (-9.0, 25.65, 0.2), (-9.5, 24.6, 0.55), (-9.0, 25.65, 0.24)))
st("june", "L40.1", expr="smile")
put("june", "L41", "closed", -9.0, 26.8, 90, expr="neutral", arms=[0, 70], sit=False, blend=0.0)
shot("S41a", "L41", "closed", "closed", "moon", C("closed", (-11.7, 24.7, 1.3), (-7.2, 26.4, 1.3), (-11.4, 25.1, 1.3), (-7.0, 26.4, 1.3)))
put("june", "L41+0.8", "open", -8.2, 26.4, 90, expr="hopeful", arms=[0, 70], sit=False)
go("june", "L42-0.05", "open", -6.2, 26.4)
shot("S41b", "L41+0.8", "open", "open", "moon", C("open", (-11.3, 26.2, 1.4), (-5.0, 26.4, 1.4), (-11.3, 26.4, 1.4), (-4.4, 26.4, 1.4)))
hide("june", "L42")
# ------------------------------------------------------------------ S42 to S45: every path she ever cut
shot("S42", "L42", "star", "star", "moonhi", C("star", (0.0, -0.3, 132.0), (0.0, 1.0, 0.0), (0.0, -0.2, 124.0), (0.0, 1.0, 0.0)))
shot("S43", "L43", "tractor", "tractor", "moonhi", C("tractor", (0.0, -0.3, 132.0), (0.0, 1.0, 0.0), (0.0, -0.2, 124.0), (0.0, 1.0, 0.0)))
shot("S44a", "L44", "pig", "pig", "moonhi", C("pig", (0.0, -0.3, 132.0), (0.0, 1.0, 0.0), (0.0, -0.2, 124.0), (0.0, 1.0, 0.0)))
put("june", "L44.1+0.4", "open", -1.5, 24.6, 0, expr="laugh", arms=[0, 0], sit=False)
shot("S44b", "L44.1+0.4", "open", "open", "moon", C("open", (-1.5, 20.4, 1.5), (-1.5, 24.6, 1.4), (-1.5, 20.9, 1.5), (-1.5, 24.6, 1.4)))
put("june", "L45", "open", -1.5, 23.4, 0, expr="smile", arms=[0, 0], side=[0, 68])
go("june", "L45.2-0.05", "open", -1.5, 21.6)
shot("S45a", "L45", "open", "open", "moon", C("open", (-1.1, 18.6, 0.95), (-1.5, 22.2, 1.3), (-1.3, 19.2, 1.0), (-1.5, 22.0, 1.3)))
put("june", "L45.2", "open", -1.5, 21.4, 180, expr="smile", arms=[0, 0], side=[68, 0])
go("june", "L46-0.05", "open", -1.5, 19.6)
shot("S45b", "L45.2", "open", "open", "moon", C("open", (-1.5, 25.2, 1.55), (-1.5, 19.5, 1.3), (-1.5, 24.6, 1.55), (-1.5, 19.5, 1.3)))
hide("june", "L46")
# ------------------------------------------------------------------ S46 to S51: the long night, dawn, her face, and the loop
put("june", "L46", "summer", -4.0, -22.5, 180, expr="smile", arms=[60, 60])
go("june", "L46.1-0.05", "summer", -4.0, -21.2)
shot("S46a", "L46", "summer", "summer", "summer", C("summer", (-6.2, -27.5, 2.5), (-0.5, -10.0, 0.8), (-5.0, -27.0, 2.4), (-0.5, -10.0, 0.8)), mower=True)
hide("june", "L46.1")
put("june", "L46.1", "closed", -9.0, 27.35, 0, expr="asleep", sit=True, snap=True, arms=[0, 0], blend=0.0)
shot("S46b", "L46.1", "closed", "closed", "predawn", C("closed", (-7.4, 24.2, 1.0), (-9.0, 27.2, 0.8), (-7.2, 24.6, 1.0), (-9.0, 27.2, 0.85)))
hide("june", "L47")
shot("S47a", "L47", "dawn", "dawn", "predawn", C("dawn", (0.0, -14.0, 0.6), (0.0, -6.0, 1.2), (0.0, -6.0, 0.65), (0.0, 2.0, 1.25)))
shot("S47b", "L47.1", "curve", "curve", "predawn", C("curve", (-10.4, -6.4, 0.7), (-1.9, -10.8, 1.2), (-8.6, -8.0, 0.75), (1.2, -10.9, 1.2)))
put("june", "L48", "dawn", -0.4, -40.4, 200, expr="curious", arms=[0, 0], z=3.4)
shot("S48a", "L48", "herface", "herface", "dawn", C("herface", (-2.4, -37.6, 4.8), (-0.3, -40.4, 4.95), (-2.1, -37.9, 4.8), (-0.3, -40.4, 4.95)))
shot("S48b", "L48.1", "herface", "herface", "dawn", C("herface", (0.9, -41.8, 5.0), (-0.2, -30.0, 1.5), (0.8, -41.9, 5.05), (-0.2, -30.0, 1.5)))
shot("S49a", "L49", "herface", "herface", "dawn", C("herface", (0.0, -5.0, 152.0), (0.0, -4.7, 0.0), (0.0, -5.0, 146.0), (0.0, -4.7, 0.0)))
st("june", "L49.1", expr="laugh", arms=[0, 140])
shot("S49b", "L49.1", "herface", "herface", "dawn", C("herface", (-1.2, -38.4, 4.95), (-0.4, -40.4, 5.0), (-1.0, -38.6, 4.95), (-0.4, -40.4, 5.0)))
st("june", "L50", expr="smile", arms=[0, 165], side=[0, 8])
st("june", "L50+0.35", side=[0, 40], blend=0.3)
st("june", "L50+0.7", side=[0, 8], blend=0.3)
st("june", "L50+1.05", side=[0, 40], blend=0.3)
shot("S50a", "L50", "herface", "herface", "dawn", C("herface", (2.2, -37.4, 4.6), (-0.4, -40.4, 5.0), (1.9, -37.8, 4.6), (-0.4, -40.4, 5.0)))
shot("S50b", "L50.1", "herface", "herface", "dawn", C("herface", (0.0, -40.0, 17.0), (0.0, -8.0, 0.0), (0.0, -43.0, 22.0), (0.0, -6.0, 0.0)))
hide("june", "L51")
put("june", "L51", "day", 3.2, -30.6, -60, expr="smile", arms=[0, 0])
put("woman", "L51", "day", -2.4, -32.4, 140, expr="neutral")
go("woman", "L51+1.2", "day", -0.5, -28.4)
put("dad", "L51", "day", 1.6, -32.8, 160, expr="neutral")
go("dad", "L51+1.2", "day", 0.7, -28.8)
shot("S51a", "L51", "day", "day", "dusk2", C("day", (-3.4, -34.6, 1.5), (0.6, -28.2, 1.9), (-2.8, -34.2, 1.5), (0.8, -27.6, 2.0)))
hide("woman", "L51.2")
hide("dad", "L51.2")
shot("S51b", "L51.2", "entrance", "entrance", "dusk", C("entrance", (0.3, -2.6, 1.8), (0.3, 0, 1.92), (0.3, -2.0, 1.85), (0.3, 0, 1.92)))

# ---------------------------------------------------------------------------------------------- assemble
shots_json = []
for i, s in enumerate(SHOTS):
    d = {"id": s["id"], "cam": s["cam"], "step": 2}
    if s["at"] != 0:
        d["at"] = s["at"]
    shots_json.append(d)
shot_layout = {s["id"]: s["layout"] for s in SHOTS if s["layout"]}
shot_look = {s["id"]: s["look"] for s in SHOTS}
ids = [s["id"] for s in SHOTS]
rng = lambda a, b: ids[ids.index(a):ids.index(b) + 1]
mower_shots = [s["id"] for s in SHOTS if s.get("mower")]
props = {
    "phone_a": ["S09a"], "phone_b": ["S09b", "S09c"],
    "held_q": rng("S20", "S30a"), "held_th": rng("S20", "S30a") + ["S16", "S19a", "S19b", "S51a"],
    "flash": ["S26", "S27b", "S28a", "S28b", "S29a", "S29b", "S29c", "S29d", "S29e", "S30a", "S41a", "S41b", "S44b", "S45a", "S45b"],
    "ground_set": ["S30a", "S30b", "S30c", "S31", "S32", "S37", "S39", "S40", "S41a", "S41b", "S46b"],
    "steam": ["S30b", "S30c", "S31", "S37", "S39", "S40", "S46b"],
    "eye": ["S34"], "dot": ["S42", "S43", "S44a"], "cup_s": ["S16"],
}
rustle = {"S01a": 0.6, "S02": 1.0, "S05a": 1.2, "S10a": 1.0, "S10b": 2.0, "S11": 1.0, "S23a": 1.5, "S28a": 2.0,
          "S28b": 2.5, "S29a": 1.0, "S32": 0.3, "S36": 2.0, "S37": 2.5, "S38b": 2.5, "S41a": 2.5, "S45a": 1.0, "S45b": 0.8, "S20": 0.5,
          "S22": 0.5, "S24": 0.6, "S26": 0.6, "S13": 0.6, "S14a": 0.6, "S15": 0.8, "S25a": 2.5, "S25b": 2.5, "S29c": 1.5,
          "S29d": 1.0, "S29e": 1.5, "S46b": 2.0, "S47a": 2.0, "S47b": 1.2}
dot_path = {"S42": {"pts": [[x, y] for x, y in G.STAR_PATH]},
            "S43": {"pts": [[0.0, -3.0], [0.0, -4.2], [0.0, -3.2]]},
            "S44a": {"pts": [[-12.0, 0.0], [-3.0, -6.0], [8.0, -5.0], [12.5, 0.0]]}}

OUTS = {0: "L22+0.2", 1: "L22+0.4", 2: "L22+0.6", 3: "L22+0.8", 4: "L22+1.0", 5: "L22+1.2", 6: "L23+0.5", 7: "L23+1.2",
        8: "L24+0.0", 9: "L25+0.05", 10: "L26+0.4", 11: "L27+0.1"}
cues = [{"at": v, "name": f"out{k}"} for k, v in OUTS.items()]
cues += [{"at": "L27+0.45", "name": "moon"}, {"at": "L51+0.1", "name": "icon_up"}, {"at": "L01.2", "name": "stay"}]

# keep each character's keys in time order (the resolver below checks it)
story = {
    "slug": "ep95-corn-maze",
    "title": "Lights Out Means You STAY All Night 🌽",
    "made_for_kids": False,
    "premise": "At our corn maze, if the lanterns go out while you're still inside, you stay the night, and nobody has, because a voice in the corn tells lost people where to turn.",
    "twist": "The voice is the maze itself; its paths are a huge face, and the farmer June walked in to stay all night, so by dawn it had cut her own face for her.",
    "world": "a farm's corn maze at lights out: gold corn, iron lanterns, a navy sky with a big silver moon, gold dawn",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff7a1f",
    "gap": 0.15,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "look": {"style": "closer", "flash_safe": True, "fog": "#0a1233", "fog_density": 0.0, "fog_start": 500.0, "sky": "#0a1233",
             "exposure": 0.3,
             "polish": {"hold": ["S34"], "twist": "L33", "reveal": ["L33", "L34"],
                        "emph": ["L01.2", "L10.2", "L24", "L25.1", "L27.2", "L33", "L34", "L38.2", "L40.1", "L49.1", "L51.2"],
                        "sway": ["S22", "S23a", "S24", "S25a", "S25b", "S26", "S28a", "S28b", "S29a", "S29b", "S29c", "S29d", "S29e"]}},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.0, 0.0, 0.0], "saturation": 1.05, "contrast": 1.05,
              "vignette": 0.25, "bloom": 0.3, "grain": 0.009},
    "layouts": ["face", "partial", "star", "tractor", "pig", "entrance", "day", "closed", "open", "nosid", "sealed", "summer", "dawn", "curve", "herface"],
    "shot_layout": shot_layout,
    "shot_look": shot_look,
    "props_by_shot": props,
    "mower_shots": mower_shots,
    "flash_on": props["flash"],
    "eye_shots": ["S34"],
    "ripple_shots": ["S50b"],
    "shot_rustle": rustle,
    "dot_path": dot_path,
    "cast": cast,
    "lines": lines,
    "shots": shots_json,
    "acting": acting,
    "cues": cues,
    "set_moves": [i for i in ids if i in rustle or i in dot_path or i in rng("S20", "S27b") or i in ("S01a", "S01b", "S01c", "S30b", "S30c", "S40", "S50b", "S51a", "S51b", "S31", "S39", "S37", "S29e", "S33")],
    "clip_ok": [],
    "music": {"root": 43, "mode": "mixolydian", "bpm": 70, "seed": 95,
              "sections": [{"at": 0, "voices": ["piano", "pad"], "energy": 0.35},
                           {"at": "L20", "voices": ["piano", "pad", "drone"], "energy": 0.45},
                           {"at": "L22", "voices": ["drone", "pad"], "energy": 0.5},
                           {"at": "L28", "voices": ["drone"], "energy": 0.35},
                           {"at": "L33", "voices": ["pad", "choir"], "energy": 0.4},
                           {"at": "L35", "voices": ["piano", "pad"], "energy": 0.55},
                           {"at": "L46", "voices": ["pad"], "energy": 0.3},
                           {"at": "L48", "voices": ["pad", "choir", "piano"], "energy": 0.5},
                           {"at": "L51", "voices": ["piano"], "energy": 0.3}]},
    "sound": {"floor": "grass", "steps_db": -20, "rev": 2,
              "ambience": [{"kind": "wind", "from": 0, "to": "end", "lufs": -38},
                           {"kind": "crickets", "from": "L20", "to": "L48-0.2", "lufs": -38}],
              "sfx": [],
              "music_drops": [["L27.2+0.15", "L28"], ["L32>-0.1", "L33"]]},
    "rev": REV,
}
story = remap(story)
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False))
print("wrote", OUT, len(shots_json), "shots")
