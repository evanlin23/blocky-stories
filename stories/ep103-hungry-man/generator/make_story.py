"""Writes ../story.json for ep103 "the hungry man" (script.md, 2026-11-04). Run: python stories/ep103-hungry-man/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90. Time references use the script's chunk numbers; captions are split to two or three words and the
references are remapped.
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import layout as G  # noqa: E402

OUT = HERE.parent / "story.json"
REV = 1
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = [], {}
for ln in orig_lines:
    if "pause" in ln:
        lines.append(ln)
        continue
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
idx = next(i for i, l in enumerate(lines) if l["id"] == "L38")
lines.insert(idx, {"id": "P01", "pause": 0.6, "chunks": [["", ""]]})


def remap(ref):
    if not isinstance(ref, str):
        return ref
    mm = re.match(r"^(L\d+)\.(\d+)(.*)$", ref)
    if mm and mm.group(1) in CHUNKMAP:
        mp = CHUNKMAP[mm.group(1)]
        return f"{mm.group(1)}.{mp[min(int(mm.group(2)), len(mp) - 1)]}{mm.group(3)}"
    return ref


def remap_all(items):
    for it in items:
        for key in ("at", "from", "to"):
            if key in it:
                it[key] = remap(it[key])


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, collar=None,
           hat="none", hat_c="#333333", extras=(), eyes="round", sleeves="long", brow_w=1.0, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c,
         "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    if brow_w != 1.0:
        d["face"]["brow_w"] = brow_w
    if pattern_c:
        d["pattern_c"] = pattern_c
    if collar:
        d["collar"] = collar
    if extras:
        d["extras"] = list(extras)
    d.update(kw)
    return d


ME = dict(skin="#dca97c", shirt="#8a8f9c", pants="#4a5a7a", shoes="#f4f4f2", hair="swoop", hair_c="#5a3a22",
          pattern="plaid", pattern_c="#c8504a", sleeves="long", brow_w=1.9)
cast = {
    "me": person(**ME),
    "mecoat": person(**{**ME, "shirt": "#2f4a3a", "pattern": "solid", "pattern_c": None}, extras=["coat"]),
    "grandpa": person("#e8bc98", "#2f4a3a", "#3a3a44", "#2a2a2a", hair="cap", hair_c="#f2f2f2", extras=["coat"],
                      eyes="tired", brow_w=2.6, height=1.1, width=0.94),
    "mom": person("#e6b48c", "#6fcfd8", "#5ab8c4", "#f4f4f2", hair="long", hair_c="#7a4a2c", eyes="lashes", brow_w=1.9,
                  width=0.96),
    "ferro": person("#f0c8a0", "#fff6e4", "#8a6a8a", "#5a3a2a", hair="bun", hair_c="#b8b8c0", eyes="lashes",
                    extras=["apron"], extra_c="#d9413b", width=1.02),
    "abern1": person("#c99a70", "#e0a030", "#4a4036", "#2a2a2a", hair="buzz", hair_c="#2a2a2a", sleeves="short"),
    "abern2": person("#d3a07a", "#c9b3f2", "#5a6a7a", "#6a4a32", hair="long", hair_c="#2a1a12", eyes="lashes"),
    "brisco": person("#f0c8a0", "#fff6e4", "#3a3a4a", "#2a2a2a", hair="spiky", hair_c="#a05a2a", extras=["tie"],
                     extra_c="#d9413b", collar="#ffffff"),
}
acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0]}] for n in cast}
last = {n: [0, 0] for n in cast}
visible = set()
cues = []
SH = []


def put(who, at, pos, yaw=None, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False, "lean": 0, "arms": [0, 0], "head": [0, 0], "side": [0, 0]}
    if yaw is not None:
        k["yaw"] = yaw
    k.update(kw)
    acting[who].append(k)
    last[who] = p
    visible.add(who)


def go(who, at, pos, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def beat(who, at, **kw):
    acting[who].append({"at": at, "pos": list(last[who]), **kw})


def only(at, names):
    for w in list(visible):
        if w not in names:
            acting[w].append({"at": at, "hidden": True})
            visible.discard(w)


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def look(at, id_, dur=0):
    cue(at, "look", id=id_, dur=dur)


def plates(at, **kw):
    cue(at, "plates", **kw)


def count(at, n):
    cue(at, "count", n=float(n))


def sit(who, at, on=True, z=0.62):
    cue(at, "sit", who=who, on=on, z=z)


def yaw_to(a, b):
    return math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1])))


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return [[0, list(p0), list(t0), l0]]
    return [[0, list(p0), list(t0), l0], [1, list(p1), list(t1 if t1 is not None else t0), l1 or l0]]


HMAP = {"reveal": 1.25, "shoes": 1.5, "gpworried": 1.6, "glance": 1.6, "gpporchlight": 1.5, "soft": 1.5, "hedoes": 1.5,
        "meeyes": 1.2, "mestunned": 1.4, "fallsface": 1.1, "melaugh": 1.5, "mesmiles": 1.6, "gpstunned": 1.2,
        "lookplate": 1.5, "straight": 1.3, "nonsense": 1.6, "peek": 1.3, "brisconod": 1.3, "wink": 1.5, "mecoat": 1.5,
        "blanket": 0.9, "revealwide": 3.2, "knocker": 0.9, "knocker2": 0.9, "knockerstill": 0.8, "knockdoor": 1.5}


def S(at, pos, tgt, lens=40, push=0.1, tgt2=None, name=None, drift=(0, 0, 0)):
    d_ = math.dist(pos, tgt)
    if name in HMAP:
        lens = 12.0 * d_ / HMAP[name]
    else:
        lens = max(9.0, lens / 3.0)   # lens is in sensor-12 terms: what I wrote is a 36 mm number
    p2 = [pos[i] + (tgt[i] - pos[i]) * push + drift[i] for i in range(3)]
    SH.append((at, mv(pos, tgt, lens, p2, tgt2 or tgt, lens), name))


Z = G.DECK_Z
OX = 0.0
GP = (0.0, -8.0)
PL = lambda side, k: (k * G.SPACING + G.PLATE_DX, side * 7.85)
kx, ky = G.KITCHEN
gx, gy = G.GROOM

# ====================================================================================== 01 the rule (L01 to L09)
look(0, "gold")
count(0, 42)
plates(0, street=1.0, ours=1.0, gp=0.0)
cue(0, "carry", v=0.0)
cue(0, "car", x=60.0)
cue(0, "blind", v=1.0)
cue(0, "clock", h=11.0, m=0.0)
cue(0, "snow", v=0.0)
cue(0, "knock", v=0.0)
cue(0, "door_open", v=0.0)
# L01: close on the hand setting the plate down
put("me", 0, [1.3, 8.55, Z], 0, expr="neutral", lean=20, arms=[0, 78])
beat("me", "L01.1", lean=8, arms=[0, 20])
put("grandpa", 0, [6.0, 3.4], 90, expr="neutral")
go("grandpa", "L01.2", [6.0, 3.4])
go("grandpa", "L01>", [2.6, 3.4])
S(0, [-0.2, 6.9, 0.9], [1.3, 7.95, 0.5], 40, 0.14, name="hook")
S("L01.1", [-0.2, 6.7, 1.75], [0.0, 9.0, 1.75], 52, 0.12, name="knockdoor")
S("L01.2", [-1.8, 5.9, 0.45], [0.8, 8.3, 0.3], 40, 0.14, drift=(0.5, 0, 0), name="shadow")
# L02
only("L02", ["me"])
put("me", "L02", [0.2, 10.1, Z], 180, expr="worried")
beat("me", "L02.1", expr="wide", head=[0, -6])
S("L02", [1.0, 13.8, 1.45], [0.0, 10.0, 1.2], 38, 0.12, name="meinside")
S("L02.2", [0.6, 11.6, 0.4], [0.0, 9.15, 0.3], 40, 0.12, name="underdoor")
# L03: the street
only("L03", [])
S("L03", [-22.0, 3.6, 2.6], [8.0, 6.5, 1.8], 28, 0.1, name="street")
S("L03.1", [-6.0, 3.8, 1.0], [-1.0, 7.6, 0.8], 34, 0.12, drift=(9.0, 0, 0), name="steps")
# L04: all but one put a plate out
only("L04", ["ferro", "abern1", "abern2"])
put("ferro", "L04", [18.0, -8.2, Z], 180, expr="smile", lean=26, arms=[0, 55])
put("abern1", "L04", [17.4, 8.2, Z], 0, expr="smile", lean=20, arms=[50, 50])
put("abern2", "L04", [18.8, 8.2, Z], 0, expr="smile", lean=20, arms=[50, 50])
S("L04", [14.0, -3.2, 1.7], [18.0, -8.2, 1.0], 36, 0.12, name="doors1")
S("L04.1", [14.5, 3.4, 1.7], [18.0, 8.2, 1.1], 36, 0.12, name="doors2")
only("L04.2", ["brisco"])
put("brisco", "L04.2", [-18.0, -8.0, Z], 180, expr="smile", lean=24, arms=[0, 55])
S("L04.2", [-20.5, -4.4, 1.6], [-18.0, -8.0, 1.0], 34, 0.12, name="doors3")
# L05: Mrs. Ferro
only("L05", ["ferro"])
put("ferro", "L05", [18.0, -8.0, Z], 180, expr="smile")
beat("ferro", "L05.1", expr="delighted", arms=[0, 155], head=[0, -6])
S("L05", [16.4, -4.6, 1.7], [18.0, -8.0, 1.6], 42, 0.12, name="ferro")
S("L05.1", [19.3, -6.5, 0.95], [19.3, -7.85, 0.4], 44, 0.1, name="lasagna")
# L06: the Abernathys
only("L06", ["abern1", "abern2"])
put("abern1", "L06", [17.4, 8.1, Z], 0, expr="grin", arms=[75, 75])
put("abern2", "L06", [18.8, 8.1, Z], 0, expr="grin", arms=[75, 75])
S("L06", [17.8, 4.8, 1.5], [18.1, 8.1, 1.3], 36, 0.12, name="abern")
beat("abern1", "L06.1", arms=[0, 0], expr="smile")
beat("abern2", "L06.1", arms=[0, 0], expr="smile")
S("L06.1", [19.3, 6.4, 0.95], [19.3, 7.85, 0.5], 44, 0.1, name="chicken")
S("L06.2", [16.2, 4.2, 1.5], [18.1, 8.1, 1.4], 40, 0.12, name="abern2s")
# L07: Mr. Brisco's sandwich
only("L07", ["brisco"])
put("brisco", "L07", [-18.0, -8.0, Z], 180, expr="smile", lean=18, arms=[0, 50])
S("L07", [-19.5, -4.6, 1.6], [-18.0, -8.0, 1.2], 38, 0.12, name="brisco")
S("L07.2", [-16.7, -6.4, 0.9], [-16.7, -7.85, 0.45], 46, 0.1, name="sandwich")
beat("brisco", "L07.3", lean=0, arms=[0, 0], expr="grin", head=[0, -8])
S("L07.3", [-19.3, -5.0, 1.75], [-18.0, -8.0, 1.65], 44, 0.12, name="brisconod")
# L08: morning, every plate empty
only("L08", ["ferro"])
look("L08", "morning")
plates("L08", street=2.0, ours=2.0, gp=0.0)
S("L08", [-12.0, 3.4, 2.4], [8.0, -6.0, 1.0], 30, 0.1, name="morning")
put("ferro", "L08.2", [18.0, -7.8, Z], 180, expr="smile", arms=[0, 70])
S("L08.2", [16.8, -4.8, 1.7], [18.0, -7.8, 1.5], 42, 0.12, name="ferrolift")
# L09: stacked in threes
S("L09", [19.3, -6.4, 0.85], [19.3, -7.85, 0.4], 46, 0.1, name="stack1")
S("L09.1", [19.3, 6.4, 0.85], [19.3, 7.85, 0.4], 46, 0.1, name="stack2")
only("L09.2", ["me"])
put("me", "L09.2", [1.3, 8.0, Z], 0, expr="smirk", lean=30, arms=[0, 55])
S("L09.2", [0.0, 5.2, 1.3], [1.3, 8.0, 0.8], 38, 0.12, name="mestack")

# ====================================================================================== 02 the figure (L10 to L22)
look("L10", "gold")
plates("L10", street=1.0, ours=1.0, gp=0.0)
only("L10", ["ferro", "abern1", "brisco"])
put("ferro", "L10", [-1.0, -6.2], 90, expr="worried")
put("abern1", "L10", [0.2, -6.2], 90, expr="worried")
put("brisco", "L10", [1.4, -6.2], 90, expr="worried")
beat("ferro", "L10.1", head=[-30, 0])
beat("abern1", "L10.1", head=[-30, 0])
S("L10", [-3.6, -3.0, 1.6], [0.2, -6.2, 1.5], 36, 0.12, name="sidewalk")
only("L10.2", ["brisco"])
put("brisco", "L10.2", [-20.0, -7.8, Z], 180, expr="worried", head=[-20, 0])
S("L10.2", [-21.0, -4.4, 1.8], [-20.0, -7.8, 1.65], 46, 0.12, name="peek")
# L11: the long coat, night
look("L11", "night")
only("L11", ["grandpa"])
put("grandpa", "L11", [28.0, -7.4, Z], 180, expr="neutral", lean=32, arms=[0, 55])
S("L11", [-2.0, -3.6, 1.7], [27.0, -8.0, 1.3], 62, 0.1, name="faraway")
only("L11.1", ["me"])
cue("L11.1", "blind", v=0.0)
put("me", "L11.1", [-2.3, 10.3, Z], 0, expr="worried", arms=[0, 90])
S("L11.1", [-3.6, 6.0, 1.55], [-2.3, 9.4, 1.55], 46, 0.1, name="mewindow")
only("L11.3", [])
cue("L11.3", "blind", v=1.0)
S("L11.3", [0.6, -4.6, 0.9], [0.0, -8.0, 0.4], 42, 0.12, name="bare1")
# L12: Grandpa's is the one porch
look("L12", "gold")
only("L12", [])
S("L12", [-8.0, -5.0, 1.0], [-3.0, -8.0, 0.5], 36, 0.1, drift=(8.0, 0, 0), name="pushalong")
put("grandpa", "L12.2", [1.0, -8.0, Z], 180, expr="neutral", arms=[55, 0])
S("L12.2", [0.0, -4.6, 1.8], [1.0, -8.0, 1.5], 38, 0.1, name="grandpaporch")
# L13
only("L13", ["grandpa"])
S("L13", [1.0, 6.9, 1.7], [0.0, -9.0, 1.6], 38, 0.12, name="across")
S("L13.1", [0.4, -5.6, 0.95], [0.0, -8.0, 0.4], 40, 0.12, name="bare2")
# L14: never knocked on his door
look("L14", "night")
only("L14", [])
S("L14", [0.8, -4.4, 1.6], [0.0, -9.0, 1.4], 36, 0.12, name="gpdoor")
only("L14.2", ["me"])
put("me", "L14.2", [-2.3, 10.4, Z], 0, expr="worried", head=[0, 0])
S("L14.2", [-0.8, 12.6, 1.6], [-2.3, 9.4, 1.55], 38, 0.12, name="melooks")
S("L14.3", [1.0, -3.6, 1.3], [0.0, -9.0, 1.3], 44, 0.12, name="gpdoor2")
# L15: nonsense
look("L15", "gold")
only("L15", ["grandpa", "brisco"])
put("grandpa", "L15", [0.4, -8.0, Z], 180, expr="angry", side=[0, 40])
put("brisco", "L15", [2.0, -6.4], yaw_to((2.0, -6.4), (0.4, -8.0)), expr="smile", arms=[75, 75])
S("L15", [3.8, -3.8, 1.7], [1.0, -7.6, 1.5], 36, 0.12, name="waveoff")
beat("grandpa", "L15.2", head=[40, 0])
S("L15.2", [-2.4, -5.0, 1.7], [0.4, -8.0, 1.6], 40, 0.12, name="nonsense")
go("grandpa", "L15.3", [0.0, -8.0, Z], yaw=180)
S("L15.3", [1.4, -4.8, 1.7], [0.0, -8.6, 1.6], 38, 0.12, name="goesin")
# L16: winter, Grandma's photo
look("L16", "snow")
only("L16", [])
S("L16", [gx - 2.4, gy + 1.4, 1.8], [gx - 2.4, gy + 3.4, 1.8], 44, 0.1, name="photo")
put("grandpa", "L16.1", [gx - 1.6, gy + 2.9], 180, expr="soft", arms=[0, 150])
S("L16.1", [gx - 0.2, gy + 0.2, 1.8], [gx - 1.9, gy + 3.2, 1.8], 40, 0.12, name="straighten")
only("L16.3", [])
cue("L16.3", "snow", v=1.0)
S("L16.3", [0.4, -4.8, 1.0], [0.0, -8.2, 0.5], 40, 0.12, name="snowporch")
# L17, L18
only("L17", [])
S("L17", [gx + 2.0, gy + 0.8, 1.5], [gx + 2.4, gy + 3.0, 0.95], 46, 0.12, name="coldstove")
only("L18", ["grandpa"])
put("grandpa", "L18", [gx + 0.6, gy - 0.35], 180, expr="blank")
sit("grandpa", "L18")
S("L18", [gx + 0.6, gy + 2.6, 1.5], [gx + 0.6, gy - 0.4, 1.1], 42, 0.12, name="cracker")
S("L18.1", [gx + 3.4, gy + 1.0, 1.5], [gx + 3.4, gy + 3.3, 1.2], 40, 0.12, name="coat")
# L19: casseroles
only("L19", ["ferro", "abern1", "abern2", "brisco"])
sit("grandpa", "L19", on=False)
for w, x_ in (("ferro", -1.4), ("abern1", -0.3), ("abern2", 0.8), ("brisco", 1.9)):
    put(w, "L19", [x_, -7.6, Z], 0, expr="smile", arms=[70, 70])
plates("L19", street=1.0, ours=1.0, gp=1.0)
S("L19", [0.6, -4.2, 1.6], [0.2, -8.0, 1.3], 34, 0.12, name="neighbors")
S("L19.1", [0.3, -6.0, 0.85], [0.0, -7.85, 0.4], 44, 0.1, name="casseroles")
# L20
only("L20", ["grandpa", "ferro"])
plates("L20", street=1.0, ours=1.0, gp=0.0)
cue("L20", "carry", v=2.0)
put("grandpa", "L20", [15.4, -6.4], yaw_to((15.4, -6.4), (17.6, -7.6)), expr="angry")
go("grandpa", "L20.1-0.1", [16.8, -7.3])
S("L20", [16.0, -3.6, 1.6], [16.6, -7.0, 1.4], 38, 0.12, name="sendback")
put("ferro", "L20.1", [18.0, -8.3, Z], 180, expr="worried", arms=[70, 70])
S("L20.1", [17.6, -4.8, 1.7], [17.6, -8.0, 1.5], 40, 0.12, name="ferrotakes")
cue("L21", "carry", v=0.0)
# L21
only("L21", ["grandpa"])
put("grandpa", "L21", [0.2, -8.0, Z], 180, expr="angry", arms=[85, 85], head=[0, -8])
S("L21", [0.8, -4.6, 1.7], [0.2, -8.0, 1.7], 40, 0.12, name="folded")
only("L21.1", ["brisco"])
put("brisco", "L21.1", [0.6, -7.4, Z], 0, expr="grin")
S("L21.1", [1.8, -4.8, 1.7], [0.5, -7.9, 1.6], 40, 0.12, name="doorshut")
# L22: the kitchen
look("L22", "snow")
only("L22", ["mom"])
put("mom", "L22", [kx + 0.2, ky + 1.6], 0, expr="soft", arms=[50, 50])
S("L22", [kx + 0.8, ky - 1.4, 1.65], [kx + 0.2, ky + 1.7, 1.45], 38, 0.12, name="momcoat")
put("mom", "L22.2", [kx - 2.5, ky + 2.0], 180, expr="worried", head=[0, 0])
S("L22.2", [kx - 1.0, ky - 0.2, 1.7], [kx - 2.5, ky + 2.0, 1.55], 38, 0.12, name="momwindow")
put("mom", "L22.4", [kx + 0.2, ky + 1.6], 0, expr="polite")
S("L22.4", [kx + 0.5, ky - 0.4, 1.7], [kx + 0.2, ky + 1.6, 1.6], 50, 0.12, name="straight")

# ====================================================================================== 03 the rule broken (L23 to L26)
look("L23", "gold")
cue("L23", "snow", v=0.0)
only("L23", ["me"])
put("me", "L23", [1.6, 13.3, 0.3], 0, expr="smirk", arms=[0, 0])
sit("me", "L23")
cue("L23", "chips", v=1.0)
S("L23", [1.2, 10.4, 1.45], [1.6, 13.3, 1.0], 36, 0.12, name="couch")
cue("L23.2", "chips", v=0.0)
sit("me", "L23.2", on=False)
put("me", "L23.2", [kx - 1.0, ky + 2.0], 180, expr="smirk", head=[-20, 0])
S("L23.2", [kx - 0.6, ky - 0.6, 1.65], [kx - 1.2, ky + 2.4, 1.3], 40, 0.12, name="eyeroll")
# L24: Mom leaves
only("L24", ["me"])
cue("L24", "car", x=-2.0)
cue("L24+0.35", "car", x=-52.0, dur=1.7)
put("me", "L24.1", [1.0, 8.0, Z], 0, expr="smile", arms=[0, 150])
S("L24", [4.0, 0.8, 1.2], [-6.0, -2.8, 0.9], 34, 0.12, name="carleaves")
S("L24.1", [1.7, 4.4, 0.95], [2.8, 6.5, 0.6], 42, 0.1, name="mailbox")
# L25
only("L25", [])
plates("L25", street=1.0, ours=0.0, gp=0.0)
S("L25", [0.2, 4.4, 1.2], [1.3, 8.0, 0.5], 32, 0.12, name="bare ours")
put("me", "L25.1", [kx + 2.4, ky - 0.4], 180, expr="smirk")
cue("L25.1", "meplate", v=1.0)
S("L25.1", [kx + 1.8, ky - 2.6, 1.55], [kx + 2.4, ky - 0.2, 1.4], 40, 0.12, name="mac")
cue("L26", "meplate", v=0.0)
# L26
only("L26", [])
count("L26", 41)
S("L26", [0.4, 0.4, 2.0], [0.6, 8.4, 1.0], 30, 0.12, name="tworpor")

# ====================================================================================== 04 the night (L27 to L37)
look("L27", "night")
S("L27", [-12.0, 2.4, 2.1], [10.0, 0.0, 1.8], 30, 0.1, name="quiet")
cue("L27.3", "blind", v=1.0)
S("L27.3", [-3.6, 5.4, 1.6], [-2.3, 9.4, 1.6], 42, 0.12, name="blindsdown")
# L28: something on our steps
put("grandpa", "L28", [1.2, 3.6], 180, expr="neutral")
go("grandpa", "L28>", [1.2, 6.4])
S("L28", [0.2, 4.8, 0.45], [0.8, 8.3, 0.25], 36, 0.12, name="shadowsteps")
only("L28.1", ["me", "grandpa"])
put("me", "L28.1", [1.6, 13.3, 0.3], 0, expr="worried", arms=[0, 75])
sit("me", "L28.1")
cue("L28.1", "chips", v=1.0)
S("L28.1", [0.8, 10.5, 1.4], [1.6, 13.3, 1.1], 38, 0.12, name="chipfrozen")
put("grandpa", "L28.2", [0.0, 8.0, Z], 180, expr="neutral")
put("grandpa", "L30", [1.5, 8.0, Z], 180, expr="neutral")
S("L28.2", [0.6, 11.0, 0.42], [0.0, 9.15, 0.28], 40, 0.12, name="lightbreaks")
# L29
S("L29", [0.4, 11.6, 1.55], [0.0, 9.15, 1.5], 40, 0.12, name="doorinside")
beat("me", "L29.1", expr="scared", arms=[0, 0])
cue("L29.1", "chips", v=0.0)
S("L29.1", [1.1, 10.6, 1.35], [1.6, 13.3, 1.15], 44, 0.12, name="holdbreath")
# L30: three slow knocks
cue("L30", "knock", v=1.0)
S("L30", [0.3, 6.8, 1.8], [0.0, 9.0, 1.7], 70, 0.1, name="knocker")
beat("me", "L30.1", lean=-12, expr="terrified")
S("L30.1", [2.2, 10.6, 1.5], [1.6, 13.3, 1.2], 40, 0.12, name="flinch")
cue("L30>", "knock", v=0.0)
# L31
beat("me", "L31", lean=0, expr="wide", arms=[0, 0])
S("L31", [1.5, 11.6, 1.2], [1.6, 13.4, 1.15], 62, 0.1, name="blanket")
# L32: midnight
cue("L32", "clock", h=12.0, m=0.0)
S("L32", [-1.0, 11.2, 2.3], [-3.15, 11.6, 2.4], 46, 0.1, name="clock12")
cue("L32.1", "knock", v=0.6)
S("L32.1", [-0.7, 11.4, 1.9], [0.1, 9.15, 1.7], 40, 0.12, name="doorknock")
cue("L32>", "knock", v=0.0)
# L33
cue("L33", "clock", h=1.0, m=0.0)
S("L33", [-1.0, 11.2, 2.3], [-3.15, 11.6, 2.4], 46, 0.1, name="clock1")
only("L33.2", ["grandpa"])
sit("me", "L33.2", on=False)
put("grandpa", "L33.2", [2.4, 8.0, Z], 180, expr="neutral")
S("L33.2", [0.6, 12.0, 1.6], [3.15, 12.0, 1.8], 40, 0.12, name="sidewindow")
put("me", "L33.3", [2.0, 12.2, 0.3], 90, expr="terrified", lean=-14)
S("L33.3", [0.2, 10.4, 1.5], [2.0, 12.2, 1.4], 40, 0.12, name="backaway")
# L34: the coat and basket
only("L34", ["grandpa"])
put("grandpa", "L34", [-2.0, 8.3, Z], 180, expr="neutral", arms=[0, 0])
cue("L34", "blind", v=0.0)
cue("L34", "carry", v=1.0)
S("L34", [-2.2, 11.2, 1.4], [-2.0, 8.3, 1.3], 50, 0.1, name="slit")
S("L34.2", [-0.8, 6.2, 0.9], [-1.9, 8.3, 0.85], 44, 0.12, name="basket")
# L35
cue("L35", "blind", v=1.0)
put("grandpa", "L35", [0.0, 8.0, Z], 180, expr="worried")
S("L35", [0.2, 10.9, 1.8], [0.0, 9.15, 1.75], 48, 0.12, name="doorfrost")
put("me", "L35.1", [1.6, 13.3, 0.3], 0, expr="scared")
sit("me", "L35.1")
S("L35.1", [0.9, 10.6, 1.4], [1.6, 13.3, 1.3], 40, 0.12, name="upright")
# L36
only("L36", ["me", "grandpa"])
sit("me", "L36", on=False)
put("me", "L36", [1.6, 12.4, Z], 0, expr="scared")
go("me", "L36>", [0.5, 10.1, Z])
S("L36", [3.0, 13.8, 1.7], [0.9, 11.2, 1.3], 36, 0.12, name="walkdoor")
beat("me", "L36.1", arms=[0, 60])
S("L36.1", [1.5, 11.0, 1.25], [0.4, 9.2, 1.15], 52, 0.12, name="handlatch")
# L37: the door opens
S("L37", [0.9, 10.5, 1.2], [0.45, 9.15, 1.15], 70, 0.1, name="latch")
cue("L37.1", "door_open", v=1.0, dur=1.1)
S("L37.1", [1.8, 12.8, 1.5], [0.0, 9.2, 1.4], 34, 0.14, name="swing")
only("P01", ["grandpa", "me"])
put("grandpa", "P01", [0.0, 7.7, 0.15], 180, expr="polite", arms=[0, 0])
put("me", "P01", [1.0, 10.8, Z], 0, expr="stunned" if False else "wide")
S("P01", [1.9, 11.6, 0.9], [0.2, 9.0, 0.3], 40, 0.1, name="hallfloor")
# L38 to L41: the reveal
only("L38", ["grandpa"])
S("L38", [0.0, 11.2, 1.7], [0.0, 7.9, 1.5], 42, 0.1, name="reveal")
S("L39", [0.7, 10.6, 1.45], [0.0, 7.0, 1.25], 30, 0.08, name="revealwide")
S("L39.2", [0.1, 10.4, 1.2], [-0.45, 7.7, 0.85], 48, 0.1, name="basketclose")
beat("grandpa", "L40", head=[0, 22], expr="polite")
S("L40", [0.1, 9.8, 1.6], [0.0, 7.6, 1.45], 56, 0.1, name="shoes")
only("L40.1", ["me"])
put("me", "L40.1", [0.0, 9.9, Z], 0, expr="wide")
S("L40.1", [0.3, 6.4, 1.7], [0.0, 9.6, 1.65], 50, 0.1, name="mestunned")
only("L41", ["grandpa"])
put("grandpa", "L41", [0.0, 7.7, 0.15], 180, expr="worried", arms=[0, 0], head=[0, 0])
S("L41", [0.1, 9.9, 1.7], [0.0, 7.7, 1.5], 60, 0.1, name="gpworried")
beat("grandpa", "L41.2", head=[30, 0], expr="worried")
S("L41.2", [-0.3, 9.8, 1.7], [0.0, 7.7, 1.5], 44, 0.1, name="glance")
only("L41.3", ["me"])
put("me", "L41.3", [0.0, 9.9, Z], 0, expr="worried")
S("L41.3", [0.5, 6.5, 1.7], [0.0, 9.7, 1.65], 62, 0.1, name="fallsface")

# ====================================================================================== 05 the cover story (L42 to L58)
only("L42", [])
S("L42", [0.4, 8.6, 1.7], [10.0, -3.0, 1.0], 28, 0.12, name="streetplates")
put("grandpa", "L42.1", [0.0, 7.7, 0.15], 180, expr="polite")
S("L42.1", [0.4, 10.0, 1.7], [0.0, 7.7, 1.5], 52, 0.1, name="gpporchlight")
# L43: Mom's phone, Mom at Ferro's
look("L43", "snow")
cue("L43", "snow", v=1.0)
only("L43", ["mom"])
put("mom", "L43", [kx - 2.5, ky + 2.0], 180, expr="worried", arms=[0, 150])
S("L43", [kx - 1.0, ky - 0.2, 1.7], [kx - 2.5, ky + 2.0, 1.55], 38, 0.12, name="phone")
put("mom", "L43.1", [17.6, -8.2, Z], 0, expr="polite", arms=[0, 120])
S("L43.1", [16.5, -5.2, 1.6], [17.6, -8.2, 1.55], 40, 0.12, name="momknocks")
# L44
only("L44", ["grandpa"])
cue("L44", "carry", v=2.0)
put("grandpa", "L44", [1.2, -2.2], 180, expr="angry")
go("grandpa", "L44>", [1.2, 2.2])
S("L44", [-3.4, 0.0, 1.6], [1.2, 0.0, 1.4], 38, 0.12, name="acrosssnow")
# L45
cue("L45", "carry", v=0.0)
put("grandpa", "L45", [18.6, -6.4], 0, expr="soft", head=[0, 22])
S("L45", [17.0, -3.8, 1.5], [19.0, -7.0, 1.0], 38, 0.12, name="leftplate")
beat("grandpa", "L45.1", head=[-40, 0], arms=[0, 60])
S("L45.1", [16.8, -4.2, 1.6], [18.6, -6.4, 1.3], 40, 0.12, name="liftfoil")
beat("grandpa", "L45.2", head=[40, 0], expr="worried")
S("L45.2", [20.6, -8.0, 1.6], [18.6, -6.2, 1.5], 40, 0.12, name="lookaround")
# L46
look("L46", "gold")
cue("L46", "snow", v=0.0)
plates("L46", street=1.0, ours=1.0, gp=0.0)
only("L46", [])
S("L46", [-20.0, 3.4, 2.2], [8.0, -2.0, 1.6], 30, 0.1, name="atsix")
only("L46.1", ["ferro", "abern2"])
put("ferro", "L46.1", [-0.8, 6.0], yaw_to((-0.8, 6.0), (0.6, 6.0)), expr="smirk")
put("abern2", "L46.1", [0.6, 6.0], yaw_to((0.6, 6.0), (-0.8, 6.0)), expr="grin")
S("L46.1", [-0.1, 3.4, 1.6], [-0.1, 6.0, 1.5], 40, 0.12, name="wink")
# L47
only("L47", ["brisco"])
put("brisco", "L47", [-18.0, -8.0, Z], 180, expr="angry", lean=18, arms=[0, 50])
S("L47", [-19.4, -4.8, 1.6], [-18.0, -8.0, 1.2], 38, 0.12, name="serious")
# L48: Grandpa's midnight dinner
look("L48", "night")
only("L48", ["grandpa"])
put("grandpa", "L48", [gx + 0.6, gy - 0.35], 180, expr="shut", arms=[40, 40])
sit("grandpa", "L48")
S("L48", [gx + 0.6, gy + 2.4, 1.4], [gx + 0.6, gy - 0.4, 1.2], 40, 0.12, name="eatslasagna")
beat("grandpa", "L48.1", expr="soft", head=[18, 0])
S("L48.1", [gx - 0.6, gy + 1.6, 1.4], [gx + 0.6, gy - 0.4, 1.2], 44, 0.12, name="eatssandwich")
# L49: morning waves
look("L49", "morning")
sit("grandpa", "L49", on=False)
only("L49", ["ferro", "abern1", "grandpa"])
put("ferro", "L49", [-1.4, -6.0], yaw_to((-1.4, -6.0), (1.0, -6.0)), expr="smile", arms=[0, 150])
put("abern1", "L49", [-0.2, -6.0], yaw_to((-0.2, -6.0), (1.0, -6.0)), expr="smile", arms=[0, 150])
put("grandpa", "L49", [1.8, -6.0], -90, expr="angry", head=[10, 0])
S("L49", [-0.6, -3.2, 1.7], [0.2, -6.0, 1.5], 36, 0.12, name="waves")
S("L49.1", [-2.8, -4.2, 1.7], [-1.4, -6.0, 1.6], 44, 0.12, name="ferrowatches")
# L50
only("L50", ["grandpa", "brisco"])
put("grandpa", "L50", [-1.6, -6.0], 90, expr="angry")
go("grandpa", "L50>", [1.6, -6.0])
put("brisco", "L50", [2.4, -4.3], -90, expr="grin")
go("brisco", "L50>", [-1.0, -4.3])
S("L50", [0.0, -2.6, 1.6], [0.0, -6.0, 1.5], 38, 0.14, name="passing")
# L51: night, washing
look("L51", "night")
only("L51", ["grandpa"])
put("grandpa", "L51", [gx + 1.4, gy + 2.3], 180, expr="soft", arms=[55, 55])
S("L51", [gx + 1.4, gy - 0.4, 1.65], [gx + 1.4, gy + 2.6, 1.3], 38, 0.12, name="sink")
S("L51.2", [gx + 2.0, gy + 1.8, 1.5], [gx + 2.0, gy + 3.0, 1.05], 50, 0.1, name="threeplates")
S("L52", [gx - 2.4, gy + 2.0, 1.8], [gx - 2.4, gy + 3.4, 1.8], 52, 0.1, name="photo2")
look("L52.1", "morning")
plates("L52.1", street=2.0, ours=2.0, gp=0.0)
only("L52.1", [])
S("L52.1", [18.0, -5.0, 1.0], [19.3, -7.85, 0.4], 36, 0.12, name="morningstacks")
# L53: missing
look("L53", "night")
plates("L53", street=1.0, ours=0.0, gp=0.0)
S("L53", [1.0, 5.6, 0.9], [1.3, 7.85, 0.35], 44, 0.1, name="barestep")
# L54: he knocks
cue("L54", "knock", v=1.0)
S("L54", [0.3, 6.8, 1.8], [0.0, 9.0, 1.7], 70, 0.1, name="knocker2")
put("grandpa", "L54.1", [0.2, 7.2, 0.15], 140, expr="worried", arms=[0, 0])
S("L54.1", [2.8, 7.6, 1.7], [0.2, 7.4, 1.8], 40, 0.12, name="waiting")
cue("L54>", "knock", v=0.0)
# L55
S("L55", [gx - 0.8, gy + 0.4, 1.7], [gx - 2.4, gy + 3.4, 1.8], 40, 0.12, name="photo3")
only("L55.1", ["grandpa"])
put("grandpa", "L55.1", [0.0, 7.0, 0.15], 0, expr="soft")
S("L55.1", [0.5, 9.0, 1.9], [0.0, -6.0, 2.0], 34, 0.14, name="uptheporches")
# L56
put("grandpa", "L56", [0.0, 7.7, 0.15], 180, expr="soft")
S("L56", [0.0, 11.0, 1.7], [0.0, 7.7, 1.5], 48, 0.1, name="soft")
beat("grandpa", "L56.2", expr="smile")
S("L56.2", [0.6, 10.2, 1.7], [0.0, 7.7, 1.5], 56, 0.1, name="hedoes")
# L57
only("L57", [])
cue("L57", "knock", v=0.0)
S("L57", [0.3, 6.8, 1.8], [0.0, 9.0, 1.7], 80, 0.08, name="knockerstill")
# L58
only("L58", ["me"])
put("me", "L58", [0.0, 9.8, Z], 0, expr="soft")
S("L58", [0.3, 7.0, 1.7], [0.0, 9.5, 1.65], 56, 0.1, name="meeyes")

# ====================================================================================== 06 the turn and the loop (L59 to L71)
look("L59", "night")
only("L59", ["me"])
put("me", "L59", [kx + 0.8, ky + 2.3], 180, expr="smile", arms=[50, 0])
S("L59", [kx + 0.8, ky - 0.6, 1.65], [kx + 0.8, ky + 2.5, 1.3], 38, 0.12, name="stove")
put("grandpa", "L59.1", [kx + 2.4, ky - 0.4], 180, expr="polite", arms=[60, 60])
sit("grandpa", "L59.1")
S("L59.1", [kx + 1.4, ky - 3.0, 1.6], [kx + 2.4, ky - 0.2, 1.4], 40, 0.12, name="gptable")
only("L60", ["grandpa"])
cue("L60", "carry", v=4.0)
beat("grandpa", "L60", arms=[0, 75], expr="angry")
S("L60", [kx + 2.0, ky - 2.0, 1.55], [kx + 2.4, ky - 0.2, 1.4], 56, 0.1, name="toodark")
cue("L61", "carry", v=0.0)
beat("grandpa", "L61", arms=[0, 0], expr="smile")
S("L61", [kx + 2.4, ky - 2.4, 1.5], [kx + 2.4, ky - 0.2, 1.0], 44, 0.12, name="emptyplate")
only("L61.1", ["me", "grandpa"])
put("me", "L61.1", [kx + 2.4, ky + 1.6], 0, expr="laugh")
S("L61.1", [kx + 2.8, ky - 1.2, 1.7], [kx + 2.4, ky + 1.6, 1.6], 44, 0.12, name="melaugh")
look("L61.4", "morning")
plates("L61.4", street=1.0, ours=2.0, gp=0.0)
only("L61.4", [])
sit("grandpa", "L61.4", on=False)
S("L61.4", [0.6, 5.4, 0.9], [1.3, 7.85, 0.4], 44, 0.1, name="ourdawn")
# L62
look("L62", "gold")
plates("L62", street=1.0, ours=1.0, gp=0.0)
S("L62", [-14.0, 3.0, 2.0], [8.0, 5.0, 1.6], 30, 0.1, name="sixagain")
count("L62.2", 43)
S("L62.2", [1.2, 5.2, 1.2], [1.3, 7.85, 0.4], 40, 0.12, name="fullplate")
# L63
put("me", "L63", [0.9, 1.4], 0, expr="smile")
cue("L63", "meplate", v=1.0)
go("me", "L63.1", [0.8, -5.8])
S("L63", [-3.4, 0.4, 1.6], [0.9, -1.0, 1.4], 36, 0.1, drift=(1.0, 0, 0), name="crossing")
go("me", "L63.1+0.7", [0.4, -7.2, Z])
beat("me", "L63.1+0.9", lean=20, arms=[0, 50])
S("L63.1", [-1.0, -5.0, 1.2], [0.4, -7.5, 0.7], 40, 0.12, name="setbare")
cue("L63.1+1.0", "meplate", v=0.0)
plates("L63.1+1.0", street=1.0, ours=1.0, gp=1.0)
# L64
look("L64", "night")
put("me", "L64", [-0.7, -7.2, 0.15], 180, expr="smile", lean=0, arms=[0, 0])
sit("me", "L64")
S("L64", [1.2, -3.6, 1.3], [-0.4, -7.2, 0.8], 38, 0.12, name="sitnext")
# L65
only("L65", ["me", "grandpa"])
put("grandpa", "L65", [3.4, -2.6], yaw_to((3.4, -2.6), (1.0, -6.2)), expr="neutral")
cue("L65", "carry", v=3.0)
go("grandpa", "L65.2", [1.4, -5.6])
S("L65", [4.8, -3.0, 1.6], [2.4, -4.2, 1.4], 36, 0.12, name="upsteps")
S("L65.2", [3.0, -3.4, 1.6], [1.0, -6.2, 1.4], 40, 0.12, name="bottomstep")
# L66
beat("grandpa", "L66", expr="wide")
S("L66", [-2.4, -7.4, 1.0], [-0.2, -7.2, 0.9], 40, 0.1, name="mesmiles")
S("L66+0.55", [0.6, -5.0, 1.8], [1.2, -6.0, 1.8], 52, 0.1, name="gpstunned")
# L67
beat("grandpa", "L67", head=[0, 22], expr="soft")
S("L67", [3.0, -5.6, 1.6], [1.2, -6.0, 1.7], 44, 0.1, name="lookplate")
# L68
cue("L68", "carry", v=0.0)
go("grandpa", "L68", [0.5, -7.2, 0.15], yaw=180)
sit("grandpa", "L68+0.7")
S("L68", [2.2, -4.4, 1.4], [0.5, -7.0, 0.9], 38, 0.12, name="sitsdown")
S("L68.1", [0.3, -4.2, 1.0], [0.0, -7.4, 0.7], 34, 0.1, name="sidebyside")
# L69
plates("L69", street=1.0, ours=1.0, gp=3.0)
S("L69", [0.2, -6.0, 0.7], [0.0, -7.6, 0.25], 46, 0.1, name="twoforks")
beat("grandpa", "L69.1", expr="smile", arms=[40, 0])
S("L69.1", [2.2, -4.8, 0.9], [0.0, -7.4, 0.5], 40, 0.12, name="nudge")
# L70
look("L70", "night")
only("L70", ["grandpa", "mecoat"])
sit("grandpa", "L70", on=False)
sit("me", "L70", on=False)
put("grandpa", "L70", [28.0, -7.4, Z], 180, expr="neutral", lean=30, arms=[0, 55])
put("mecoat", "L70", [25.0, -7.4, Z], 180, expr="neutral", lean=26, arms=[0, 55])
S("L70", [-1.0, -3.6, 1.7], [26.5, -8.0, 1.3], 62, 0.1, name="twoshapes")
put("mecoat", "L70.2", [0.6, 7.5, 0.15], 180, expr="grin")
cue("L70.2", "carry", v=0.0)
S("L70.2", [0.2, 10.2, 1.7], [0.6, 7.5, 1.6], 50, 0.1, name="mecoat")
# L71: both knock, loop
look("L71", "gold")
only("L71", ["grandpa", "mecoat"])
put("grandpa", "L71", [-9.8, 8.2, Z], 0, expr="angry", arms=[0, 100])
put("mecoat", "L71", [-8.4, 8.2, Z], 0, expr="angry", arms=[0, 100])
S("L71", [-9.0, 4.8, 1.7], [-9.1, 8.2, 1.7], 38, 0.12, name="bothknock")
only("L71.1", ["me"])
put("me", "L71.1", [1.3, 8.55, Z], 0, expr="neutral", lean=10, arms=[0, 30])
beat("me", "L71.1+0.6", lean=20, arms=[0, 78])
S("L71.1", [-0.2, 6.9, 0.9], [1.3, 7.95, 0.5], 40, 0.14, name="loop")

# ---------------------------------------------------------------------------------------------- finish
for k_ in acting.values():
    remap_all(k_)
remap_all(cues)
shots, names = [], {}
for i, (at, camera, nm) in enumerate(SH):
    s = {"id": f"S{i + 1:02d}", "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    shots.append(s)
    names[nm] = s["id"]

sfx = [
    {"at": "L01.2", "kind": "knock", "pattern": [0.0, 0.32, 0.64], "tone": "soft", "db": -9},
    {"at": "L30.1", "kind": "knock", "pattern": [0.0, 0.8, 1.6], "tone": "below", "db": -11},
    {"at": "L32.1", "kind": "knock", "pattern": [0.0, 0.7, 1.4], "tone": "below", "db": -14},
    {"at": "L33.2", "kind": "knock", "pattern": [0.0, 0.3], "tone": "glass_soft", "db": -16},
    {"at": "L54", "kind": "knock", "pattern": [0.0, 0.7, 1.4], "tone": "hand", "db": -14},
]
music = {
    "root": 53, "mode": "major", "bpm": 96, "seed": 103,
    "sections": [
        {"at": 0, "voices": ["piano", "pad"], "energy": 0.4, "root": 53, "mode": "major"},
        {"at": "L10", "voices": ["piano", "drone"], "energy": 0.3, "root": 53, "mode": "major"},
        {"at": "L23", "voices": ["pulse", "pad"], "energy": 0.35, "root": 53, "mode": "major"},
        {"at": "L28", "voices": ["drone", "pulse"], "energy": 0.45, "root": 41, "mode": "minor"},
        {"at": "L38", "voices": ["pad", "piano"], "energy": 0.35, "root": 53, "mode": "major"},
        {"at": "L59", "voices": ["piano", "pad", "pulse"], "energy": 0.6, "root": 53, "mode": "major"},
    ],
}
sound = {
    "floor": "wood", "steps_db": -26,
    "ambience": [{"kind": "crickets", "from": "L27", "to": "L37", "lufs": -44},
                 {"kind": "room", "from": "L38", "to": "end", "lufs": -46}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L38")], "emph": [remap(x) for x in ["L01.2", "L12.2", "L26", "L37.1", "L42.1", "L58"]],
          "sway": [names["shadowsteps"], names["knocker"], names["knocker2"], names["slit"]],
          "hold": [names["revealwide"]]}
story = {
    "slug": "ep103-hungry-man",
    "title": "Feed The Hungry Man, Or He KNOCKS 🍽️",
    "made_for_kids": False,
    "premise": ("On a street of 43 pastel porches, every Friday at six each house leaves a plate out for the Hungry Man, "
                "who knocks all night at any door that forgets; one porch never leaves one, and last Friday, with "
                "Mom at work, I skipped ours."),
    "twist": ("There is no Hungry Man: my mom made him up the first winter without Grandma so the street could feed "
              "Grandpa, who refused all help, and the tall man in the long coat who collects the plates and knocks "
              "to check on us is Grandpa himself."),
    "world": ("A long street of small pastel houses with porches and warm porch lights at golden hour and at night, "
              "our cream house with a blue door across from Grandpa's gray-green one, and two small kitchens."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffcf73",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#e8d8c8", "fog_density": 0.004, "fog_start": 30.0, "sky": "#9fd8ff",
             "sky_strength": 1.0, "exposure": 0.2, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.2, "grain": 0.008},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [names["swing"], names["carleaves"]],
    "asr_forgive": ["missus ferro", "mister brisco", "in", "light", "the"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
