"""Writes ../story.json for ep109 "said your name" (script.md, 2026-11-04). Run: python stories/ep109-said-your-name/generator/make_story.py

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
# the 0.6 s music drop before L17
idx = next(i for i, l in enumerate(lines) if l["id"] == "L17")
lines.insert(idx, {"id": "P01", "pause": 0.6, "chunks": [["", ""]]})


def remap(ref):
    if not isinstance(ref, str):
        return ref
    mm = re.match(r"^(L\d+)\.(\d+)(.*)$", ref)
    if mm and mm.group(1) in CHUNKMAP:
        return f"{mm.group(1)}.{CHUNKMAP[mm.group(1)][int(mm.group(2))]}{mm.group(3)}"
    return ref


def remap_all(items):
    for it in items:
        for key in ("at", "from", "to"):
            if key in it:
                it[key] = remap(it[key])


D2R = math.pi / 180


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return [[0, list(p0), list(t0), l0]]
    return [[0, list(p0), list(t0), l0], [1, list(p1), list(t1 if t1 is not None else t0), l1 or l0]]


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


cast = {
    "me": person("#dca97c", "#ffd23a", "#4f78b8", "#ffffff", hair="cap", hair_c="#2a1a14", sleeves="long", brow_w=1.9,
                 extras=["coat"], zip_c="#e0a020"),
    "dev": person("#e8b890", "#2aa6a0", "#c9b27c", "#6a4a32", hair="swoop", hair_c="#14110e", extras=["glasses"],
                  extra_c="#1c1c24", brow_w=1.4),
    "odell": person("#f0c8a0", "#ffb3c7", "#8f7cc8", "#d8c8e8", hair="bun", hair_c="#f4f4f6", pattern="knit",
                    pattern_c="#ff9ab8", eyes="lashes", extras=["glasses"], extra_c="#8a8a9a", height=0.93, width=0.95),
    "baker": person("#e6b48c", "#fffaf0", "#7a6a8a", "#5a4a3a", hair="cap", hair_c="#6a4a2a", extras=["apron"], extra_c="#fffaf0",
                    hat="bucket", hat_c="#fffaf0"),
    "coatman": person("#c58c5a", "#a0724a", "#4a4036", "#2a2a2a", hair="buzz", hair_c="#c8c8cc", extras=["coat"], zip_c="#6a4a2a"),
    "greenw": person("#f0c8a0", "#7fd9a0", "#7fd9a0", "#e8e0d0", hair="long", hair_c="#7a4a2c", eyes="lashes", sleeves="short"),
    "hoodie": person("#d3a07a", "#ff6a5a", "#3a4a6a", "#f4f4f2", hair="spiky", hair_c="#2a2a2a", extras=["hooddown"]),
    "driver": person("#b98456", "#6cc4ff", "#3a4a6a", "#2a2a2a", hair="buzz", hair_c="#1a1410", hat="ballcap", hat_c="#4f78b8"),
    "neighbor": person("#e2b088", "#b8a0ff", "#6b5a48", "#4a3626", hair="cap", hair_c="#b4b4ba", extras=["glasses"], extra_c="#3a3a3e"),
    "seller": person("#d3a07a", "#ff9a1f", "#4a4036", "#2a2a2a", hair="cap", hair_c="#2a1d15", extras=["apron"], extra_c="#fffaf0"),
}
_SKIN = ["#dca97c", "#e8b890", "#b98456", "#f0c8a0", "#8a5a3a", "#d3a07a", "#e2b088", "#f0c8a0", "#c58c5a", "#e6b48c", "#a8744a", "#f0c8a0"]
_SHIRT = ["#ff9ab0", "#9be0ff", "#ffe27a", "#b8a0ff", "#8fe0b0", "#ffb06a", "#ff8a8a", "#7fd0d0", "#d8b0ff", "#a8e87a", "#ffc4e0", "#8fb4ff"]
_PANTS = ["#4f78b8", "#6a5a8a", "#4a4036", "#3a4a5a", "#7a6a5a", "#5a7a6a", "#8a6a7a", "#3a3a4a", "#6a8aa0", "#5a4a3a", "#4a6a7a", "#7a7a9a"]
_HAIR = ["cap", "long", "spiky", "swoop", "bun", "buzz", "cap", "long", "swoop", "spiky", "bun", "cap"]
_HC = ["#2a1d15", "#6a3a22", "#c8a050", "#14110e", "#8a8a96", "#3a2a22", "#a05a2a", "#2a2a2a", "#d8d0c0", "#4a2a1a", "#7a4a2c", "#1a1410"]
for i in range(12):
    f = _HAIR[i] in ("long", "bun")
    cast[f"c{i + 1}"] = person(_SKIN[i], _SHIRT[i], _PANTS[i], "#4a3a3a" if i % 2 else "#f4f4f2", hair=_HAIR[i], hair_c=_HC[i],
                               eyes="lashes" if f else "round", sleeves="short" if i % 3 == 0 else "long",
                               hat="ballcap" if i in (4, 9) else "none", hat_c="#ff7a7a")

acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0]}] for n in cast}
last = {n: [0, 0] for n in cast}
visible = set()
cues = []
SH = []


def put(who, at, pos, yaw=None, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False}
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


def vis(at, obj, on=True):
    cue(at, "vis", obj=obj, on=on)


def clock(at, h, m):
    cue(at, "clock", m=float(h * 60 + m))


def shot(at, camera, name):
    SH.append((at, camera, 2, name))


def fwd(yaw):
    r = yaw * D2R
    return math.sin(r), -math.cos(r)


def fc(pos, yaw, d, lens, h=1.55, tz=1.5, off=0.0, push=0.14, side=0.0, tpos=None):
    """A camera d metres in front of someone facing yaw, looking back at them; off moves the subject toward the right of
    the frame (the rule marker is top-left); push drifts closer over the shot."""
    fx, fy = fwd(yaw)
    px, py = -fy, fx
    tp = tpos or pos

    def key(dd, sd):
        cx, cy = pos[0] + dd * fx + sd * px, pos[1] + dd * fy + sd * py
        lx, ly = tp[0] - cx, tp[1] - cy
        n = math.hypot(lx, ly) or 1.0
        rx, ry = ly / n, -lx / n
        return [cx, cy, h], [tp[0] - rx * off, tp[1] - ry * off, tz]
    a, b = key(d, side), key(d * (1 - push), side * 0.6)
    return mv(a[0], a[1], lens, b[0], b[1], lens)


def yaw_to(a, b):
    return G.yaw_to(a, b)


def mid(a, b):
    return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]


# ---------------------------------------------------------------------------------------------- places
KX, KY = G.K
ME_K = G.ME_K
RAD = (KX - 1.2, 2.2)
NB = G.NB_X
WINS = [x for cx in G.SHOP_X for x in G.win_xs(cx)]          # the north row's upper windows
BX, BY = G.BENCH
SPOT = G.SPOT
TX, TY = G.TABLE
OD = G.OD
BREAD = G.BAKERY
SHX = G.SHELTER[0]

cue(0, "clock", m=7 * 60 + 2.0)
cue(0, "pair", n=1.0)
cue(0, "curtain", u=0.0)
cue(0, "bus", x=-30.0)
vis(0, "cup", True)

# ===== 01 the rule (L01 to L04), our kitchen
put("me", 0, [ME_K[0], ME_K[1]], 0, expr="smile", arms=[0, 100], head=[0, 8])
beat("me", "L02", expr="wide", arms=[0, 100], head=[0, 0])
beat("me", "L03", expr="worried", arms=[0, 112], head=[0, 14])
beat("me", "L03.2", expr="worried", arms=[0, 112], head=[0, 14])
shot(0, mv([KX - 0.2, -0.9, 1.95], [KX - 1.3, 2.7, 1.5], 36, [KX - 0.55, -0.2, 1.9], [KX - 1.3, 2.7, 1.5], 36), "face")
shot("L01.2", mv([KX - 0.9, 0.45, 1.5], [KX - 0.97, 1.9, 1.38], 38, [KX - 0.9, 0.9, 1.5], [KX - 0.97, 1.9, 1.38], 38), "dial")
shot("L02", fc(ME_K, 0, 2.7, 40, h=1.7, tz=1.62, off=0.1, push=0.2), "stunned")
shot("L03", mv([KX - 2.9, 0.5, 1.45], [KX - 1.45, 2.3, 1.42], 40, [KX - 2.6, 0.7, 1.45], [KX - 1.4, 2.3, 1.42], 40), "hand")
shot("L03.2", mv([KX - 1.9, 0.7, 1.15], [KX - 0.97, 2.0, 1.2], 36, [KX - 1.5, 0.9, 1.2], [KX - 0.97, 2.0, 1.25], 36), "hand2")
vis("L03", "cup", False)
# L04 the neighbor, across the street, closing his curtains
only("L04", ["neighbor"])
put("neighbor", "L04", [NB - 0.1, KY, 0], 90, expr="neutral")
beat("neighbor", "L04.1", expr="worried", head=[-14, 0])
cue("L04.1", "curtain", u=1.0, dur=0.8)
shot("L04", mv([KX - 3.0, 0.4, 1.7], [NB, KY, 1.9], 52, [KX - 3.4, 0.2, 1.75], [NB, KY, 1.95], 62), "curtains")

# ===== 02 the montage (L05 to L08): today's town
clock("L05", 7, 40)
only("L05", ["baker"])
put("baker", "L05", [BREAD, 8.3], 0, expr="smile")
beat("baker", "L05.1", expr="smile", head=[10, 0], arms=[0, 40])
shot("L05", mv([BREAD + 0.3, 3.2, 1.75], [BREAD, 8.0, 1.35], 36, [BREAD + 0.1, 3.8, 1.7], [BREAD, 8.0, 1.3], 36), "baker")
shot("L05.2", mv([BREAD - 1.4, 3.6, 1.15], [BREAD + 0.3, 8.2, 1.3], 34, [BREAD - 1.0, 4.2, 1.2], [BREAD + 0.3, 8.2, 1.35], 34), "shelves")
beat("baker", "L05.2", expr="worried", head=[-12, 0], arms=[0, 0])
only("L06", ["coatman"])
put("coatman", "L06", [SHX, -4.75], 180, expr="neutral")
beat("coatman", "L06.2", expr="worried", head=[22, 0])
shot("L06", fc([SHX, -4.75], 180, 4.2, 38, h=1.5, tz=1.5, off=0.12, push=0.2), "coatman")
cue("L06.2-2.6", "bus", x=26.0)
cue("L06.2-2.55", "bus", x=62.0, dur=5.0)
shot("L06.2", mv([SHX + 1.6, 0.9, 1.3], [SHX - 2.0, -3.0, 1.5], 36, [SHX + 1.0, 0.9, 1.3], [SHX - 3.0, -3.0, 1.5], 36), "buspass")
only("L07", ["greenw"])
put("greenw", "L07", [BX - 0.85, BY + 0.0], 180, expr="smile")
vis("L07", "bag2", False)
beat("greenw", "L07.1", expr="worried", head=[0, 12])
shot("L07", fc([BX - 0.85, BY], 180, 4.4, 38, h=2.3, tz=0.9, off=0.12, push=0.2), "woman")
shot("L07.2", mv([BX + 1.5, BY + 4.5, 2.4], [BX + 0.9, BY, 0.8], 40, [BX + 1.2, BY + 4.2, 2.3], [BX + 0.9, BY, 0.8], 40), "emptybench")
only("L08", ["hoodie"])
put("hoodie", "L08", [92.0, 3.3], 0, expr="smile", arms=[0, 100])
vis("L08", "phone", True)
beat("hoodie", "L08.1", expr="worried", head=[0, 18])
shot("L08", fc([92.0, 3.3], 0, 3.4, 38, h=1.5, tz=1.45, off=0.1, push=0.2), "phoneman")
shot("L08.2", mv([91.45, 1.9, 1.55], [91.75, 3.3, 1.1], 70, [91.5, 2.2, 1.5], [91.75, 3.3, 1.1], 70), "phone")
vis("L09", "phone", False)

# ===== 03 my named day (L09 to L16)
clock("L09", 9, 0)
only("L09", ["me"])
put("me", "L09", [-78.5, 2.4], 0, expr="worried", arms=[0, 0], head=[8, 0])
beat("me", "L09.1", expr="worried", head=[-8, 6])
shot("L09", fc([-78.5, 2.4], 0, 3.0, 40, h=1.6, tz=1.55, off=0.12, push=0.18), "fridgeme")
vis("L10", "bag", True)
put("me", "L10", [40.5, 2.6], 90, expr="smile", arms=[0, 0])
go("me", "L11", [43.6, 2.6], expr="smile")
go("me", "L12", [46.2, 2.7], expr="worried")
go("me", "L13", [50.0, 2.8], expr="worried")
go("me", "L14", [53.0, 2.9], expr="worried")
go("me", "L15", [54.6, 3.0], expr="worried")
go("me", "L16", [SPOT[0] - 0.8, 3.0], expr="wide")
go("me", "L16+0.7", [SPOT[0], 3.0], expr="wide")
only("L10", ["me"])
shot("L10", mv([46.0, -0.2, 1.7], [41.8, 2.6, 1.5], 38, [45.0, -0.2, 1.7], [42.6, 2.6, 1.5], 38), "step")
shot("L10.2", mv([46.4, 2.2, 1.0], [42.8, 2.7, 1.4], 36, [46.0, 2.1, 1.0], [43.0, 2.7, 1.4], 36), "walk")
# L11 the bakery line steps back, all at once
LINE = [(54.2, 4.0), (53.1, 4.0), (52.0, 4.0), (50.9, 4.0), (49.8, 4.0), (48.7, 4.0)]
for i, (lx, ly) in enumerate(LINE):
    put(f"c{i + 1}", "L11", [lx, ly], 90, expr="smile")
    beat(f"c{i + 1}", "L11.1-0.05", expr="smile")
    go(f"c{i + 1}", "L11.1+0.1", [lx + 0.1, 4.4], yaw=-60, expr="worried", blend=0.2)
    beat(f"c{i + 1}", "L11.2", expr="worried", head=[-20, 0])
shot("L11", mv([57.5, 2.6, 1.55], [51.0, 4.0, 1.5], 34, [57.0, 2.4, 1.55], [50.5, 4.0, 1.5], 34), "line")
shot("L11.2", mv([41.0, 1.8, 1.6], [44.8, 2.6, 1.5], 38, [41.6, 1.9, 1.6], [45.0, 2.6, 1.5], 38), "meback")
# L12 the ring: top-down on the street, everyone pushed to the edge of an empty circle
HOMES = [(44.0, 3.4), (46.0, 4.2), (48.5, 3.6), (50.5, 4.0), (47.0, 0.4), (50.0, -0.4), (44.5, -1.2), (52.0, -1.0), (46.5, -3.9),
         (49.5, -4.4), (53.0, -3.8), (51.5, 2.0)]
mepath = [(0.0, (46.2, 2.7)), (0.7, (47.4, 2.74)), (1.5, (49.0, 2.76)), (2.2, (50.0, 2.8))]
R_RING = 3.4
for i in range(12):
    nm = f"c{i + 1}"
    hx, hy = HOMES[i]
    if i < 6:
        pass
    for dt, (mx, my) in mepath:
        dx, dy = hx - mx, hy - my
        d = math.hypot(dx, dy) or 1.0
        k = max(d, R_RING) / d
        px, py = mx + dx * k, my + dy * k
        py = min(4.62, max(-5.0, py))
        if dt == 0.0:
            put(nm, "L12", [px, py], yaw_to((px, py), (mx, my)), expr="worried")
        else:
            go(nm, f"L12+{dt}", [px, py], expr="worried")
only("L12", [f"c{i + 1}" for i in range(12)] + ["me"])
shot("L12", mv([47.2, 1.5, 13.0], [47.2, 2.74, 0.0], 20, [48.4, 1.7, 12.0], [48.2, 2.74, 0.0], 20), "ring")
shot("L12.2", mv([48.6, -6.0, 9.5], [48.6, 1.4, 0.0], 36, [49.6, -4.2, 8.6], [49.6, 1.4, 0.0], 36), "ring2")
# L13 the bus slows down, sees me, and keeps going
only("L13", ["me", "driver", "coatman"])
cue("L07", "bus", x=-30.0)
cue("L11", "bus", x=12.0)
cue("L11+0.01", "bus", x=47.0, dur=5.3)
cue("L13.2+0.2", "bus", x=95.0, dur=4.0)
put("driver", "L13", [0, 0, 0], 90, expr="neutral", head=[0, 0])
cue("L13", "sit", who="driver", on=True)
put("coatman", "L13", [SHX + 3.6, -4.75], 180, expr="worried")
beat("driver", "L13.1+0.1", expr="wide", head=[-70, 0])
beat("driver", "L13.2+0.3", expr="neutral", head=[0, 0])
shot("L13", mv([SHX - 7.0, -6.6, 1.9], [SHX - 0.5, -2.6, 1.8], 34, [SHX - 5.0, -6.2, 1.9], [SHX + 1.0, -2.6, 1.8], 34), "busslow")
shot("L13.1", mv([SHX + 0.5, 1.4, 1.65], [SHX + 2.8, -1.9, 1.7], 44, [SHX + 0.9, 1.2, 1.65], [SHX + 2.9, -1.9, 1.7], 44), "driver")
# L14 a face in every window
FACES = [f"c{i + 1}" for i in range(12)]
WIN14 = [WINS[k] for k in (6, 7, 8, 9, 10, 11, 12, 13)]            # shops 3..6
only("L14", FACES[:8])
for nm, wx in zip(FACES[:8], WIN14):
    put(nm, "L14", [wx, 5.35, G.FACE_Z], 0, expr="worried", head=[0, 0])
cue("L14", "clock", m=9 * 60 + 40.0)
shot("L14", mv([WIN14[0] - 1.4, -3.4, 4.9], [WIN14[0] - 0.4, 5.3, 5.0], 38, [WIN14[3] + 0.8, -3.4, 4.9], [WIN14[3] + 1.6, 5.3, 5.0], 38), "windows")
# L15 one face at a curtain
only("L15", ["c9"])
put("c9", "L15", [70.0, 5.35, G.FACE_Z], 0, expr="worried", head=[-12, 0])
beat("c9", "L15.0", expr="worried")
shot("L15", mv([69.4, 1.0, 5.3], [70.0, 5.3, 5.15], 70, [69.7, 1.6, 5.25], [70.0, 5.3, 5.15], 70), "curtainface")
# L16 the bag tears
only("L16", ["me"])
cue("L16+0.5", "tear")
shot("L16", mv([SPOT[0] + 1.3, 1.6, 0.9], [SPOT[0] + 0.45, 3.0, 0.45], 40, [SPOT[0] + 1.0, 1.7, 0.8], [SPOT[0] + 0.45, 3.0, 0.4], 40), "bag")

# ===== 04 the oranges (L17 to L26)
only("P01", ["me"])
beat("me", "P01", expr="wide", head=[0, 25])
shot("P01", mv([SPOT[0] + 2.0, 0.6, 0.7], [SPOT[0] + 0.4, 3.0, 0.35], 40, [SPOT[0] + 1.8, 0.7, 0.55], [SPOT[0] + 0.4, 3.0, 0.3], 40), "firstorange")
shot("L17", mv([SPOT[0] - 3.2, 0.0, 1.0], [SPOT[0] + 1.5, 3.0, 0.2], 32, [SPOT[0] + 1.6, -0.6, 0.9], [SPOT[0] + 0.2, 3.0, 0.2], 32), "rolling")
beat("me", "L17", expr="scared", head=[0, 20])
RING_ANG = [15, 40, 75, 110, 140, 170, 200, 230, 255, 285, 315, 325]
RING_R = [4.6, 4.1, 3.8, 4.4, 4.0, 3.9, 4.5, 4.2, 3.8, 4.3, 4.0, 4.6]
RING = []
for a, r in zip(RING_ANG, RING_R):
    x, y = SPOT[0] + r * math.cos(a * D2R), SPOT[1] + r * math.sin(a * D2R)
    RING.append((x, min(4.55, max(-5.0, y))))
only("L18", [f"c{i + 1}" for i in range(12)] + ["me"])
for i, (x, y) in enumerate(RING):
    put(f"c{i + 1}", "L18", [x, y], yaw_to((x, y), SPOT), expr="worried")
    beat(f"c{i + 1}", "L18.1", expr="wide", head=[0, 6])
shot("L18", mv([SPOT[0] - 3.0, -3.3, 1.7], [SPOT[0] + 1.0, 3.0, 1.3], 30, [SPOT[0] - 2.4, -3.2, 1.7], [SPOT[0] + 1.4, 3.0, 1.3], 30), "dozen")
shot("L19", fc([SPOT[0], 3.0], 0, 3.2, 40, h=1.5, tz=1.5, off=0.14, push=0.2), "alone")
beat("me", "L19", expr="scared", head=[0, 12])
shot("L20.1", mv([SPOT[0] + 0.8, 3.0, 1.55], [SPOT[0] + 14.0, 4.0, 2.0], 40, [SPOT[0] + 0.5, 3.0, 1.55], [SPOT[0] + 16.0, 4.0, 2.2], 40), "towardcafe")
beat("me", "L20.1", expr="worried", head=[-40, 0], yaw=-90)
# L21 back home: our photo, the dial
only("L21", ["me"])
put("me", "L21", [-78.0, 1.0], 0, expr="worried")
cue("L21", "clock", m=9 * 60 + 41.0)
shot("L21", mv([KX + 3.3, 0.9, 1.5], [KX + 3.6, 3.3, 1.5], 50, [KX + 3.55, 1.5, 1.5], [KX + 3.6, 3.3, 1.5], 50), "photo")
shot("L21.1", mv([KX - 1.4, 0.3, 1.38], [KX - 0.97, 1.9, 1.34], 40, [KX - 1.2, 0.8, 1.38], [KX - 0.97, 1.9, 1.34], 40), "dial2")
shot("L22", mv([KX + 0.4, 1.2, 1.55], [KX - 0.8, 2.2, 1.28], 40, [KX + 0.6, 1.5, 1.5], [KX - 0.9, 2.2, 1.28], 40), "dial3")
only("L23", ["me"])
put("me", "L23", [NB + 10.6, KY], -90, expr="worried", head=[0, 14])
shot("L23", mv([NB + 7.4, KY - 0.3, 1.6], [NB + 10.6, KY, 1.5], 38, [NB + 7.6, KY - 0.2, 1.6], [NB + 10.4, KY, 1.5], 38), "windowme")
only("L23.1", ["neighbor", "me"])
put("neighbor", "L23.1", [NB - 0.1, KY, 0], 90, expr="neutral")
cue("L23.1", "curtain", u=0.0)
cue("L23.1+0.3", "curtain", u=1.0, dur=0.7)
shot("L23.1", mv([KX - 3.0, 0.4, 1.7], [NB, KY, 1.9], 52, [KX - 3.4, 0.2, 1.75], [NB, KY, 1.95], 62), "curtains2")
# L24 the cafe, from outside, today
only("L24", [])
vis("L24", "stub", True)
cue("L24", "clock", m=9 * 60 + 42.0)
shot("L24", mv([TX + 1.3, 2.2, 1.45], [TX, 6.6, 1.0], 36, [TX + 0.9, 2.8, 1.4], [TX, 6.6, 1.0], 36), "cafewindow")
shot("L24.2", mv([TX + 0.6, 4.2, 1.5], [TX, 6.6, 0.9], 42, [TX + 0.3, 4.6, 1.3], [TX, 6.6, 0.88], 42), "stubclose")
vis("L25", "plates", True)
shot("L25", mv([TX - 0.5, 5.1, 1.4], [TX, 6.6, 0.88], 50, [TX - 0.2, 5.4, 1.1], [TX, 6.6, 0.88], 50), "plates")
only("L26", ["me", "dev"])
vis("L26", "stub", False)
vis("L26", "plates", False)
put("me", "L26", [SPOT[0], 3.0], 0, expr="worried", head=[0, 16])
shot("L26", fc([SPOT[0], 3.0], 20, 3.4, 40, h=1.4, tz=1.4, off=0.14, push=0.2), "since")
# L27 somebody kneels next to an orange: Dev
OX, OY, _oz = G.orange_final(0)
DEVK = (OX + 0.75, OY - 0.1)
only("L27", ["me", "dev"])
put("dev", "L26", [OX + 4.0, OY + 0.2], -90, expr="neutral", arms=[0, 0])
go("dev", "L27.1-0.1", [DEVK[0], DEVK[1]], yaw=-90, arms=[0, 60])
cue("L27.1", "kneel", who="dev", on=True)
shot("L27", mv([OX + 3.0, OY - 2.2, 0.8], [OX + 1.2, OY, 0.7], 34, [OX + 2.2, OY - 1.9, 0.6], [OX + 0.9, OY, 0.55], 34), "kneel")
shot("L27.2", mv([DEVK[0] + 0.5, OY - 1.25, 0.55], [OX + 0.2, OY, 0.35], 44, [DEVK[0] + 0.3, OY - 1.1, 0.5], [OX + 0.1, OY, 0.3], 44), "sleeve")
cue("L28-0.1", "pick")
cue("L28", "pair", n=2.0, dur=0.5)
put("dev", "L28", [DEVK[0], DEVK[1]], -60, expr="warm", arms=[0, 70])
shot("L28", fc(DEVK, -60, 2.9, 40, h=1.0, tz=0.85, off=0.1, push=0.2), "devknee")
# L29 the whole street gasps
only("L29", FACES[:8])
for nm, wx in zip(FACES[:8], WIN14):
    put(nm, "L29", [wx, 5.35, G.FACE_Z], 0, expr="wide", head=[0, 0])
    acting[nm].append({"from": "L29", "to": "L29>", "mouth": [0.55, 0.55]})
shot("L29", mv([WIN14[4] + 1.0, -3.4, 4.9], [WIN14[4] + 0.3, 5.3, 5.05], 38, [WIN14[7] + 0.6, -3.4, 4.9], [WIN14[7] + 0.4, 5.3, 5.05], 38), "gasp")
# L30 and L31
only("L30", ["me", "dev"])
put("me", "L30", [SPOT[0], 3.0], 20, expr="scared", head=[0, 0])
put("dev", "L30", [DEVK[0], DEVK[1]], -90, expr="warm", arms=[0, 70])
cue("L30", "kneel", who="dev", on=True)
beat("me", "L30.1", expr="scared", head=[-15, 6])
shot("L30", fc([SPOT[0], 3.0], 70, 2.6, 40, h=1.55, tz=1.5, off=0.14, push=0.2), "tellhim")
beat("dev", "L31", expr="smirk", yaw=-70, arms=[0, 70])
shot("L31", fc(DEVK, -70, 2.0, 40, h=0.95, tz=0.8, off=0.1, push=0.2), "wry")
shot("L31.2", mv([DEVK[0] - 1.6, OY - 1.3, 0.9], [DEVK[0], DEVK[1], 0.75], 42, [DEVK[0] - 1.3, OY - 1.1, 0.85], [DEVK[0], DEVK[1], 0.75], 42), "wry2")
# L32 and L33 Dev's words: he stands
only("L32", ["me", "dev"])
cue("L32", "kneel", who="dev", on=False)
put("dev", "L32", [SPOT[0] + 1.2, 3.0], -90, expr="warm")
put("me", "L32", [SPOT[0], 3.0], 90, expr="worried")
beat("dev", "L32.2", expr="neutral", head=[0, 4])
shot("L32", fc([SPOT[0] + 1.2, 3.0], -50, 1.9, 44, h=1.65, tz=1.6, off=0.12, push=0.2), "devface")
shot("L32.2", fc([SPOT[0] + 1.2, 3.0], -110, 1.9, 44, h=1.65, tz=1.6, off=0.12, push=0.2), "devface2")
beat("dev", "L33", expr="smirk", head=[0, -4], side=[0, 0], arms=[0, 0])
shot("L33", fc([SPOT[0] + 1.2, 3.0], -80, 1.6, 50, h=1.65, tz=1.62, off=0.1, push=0.22), "shrug")
# L34 side by side on the sidewalk, the clock runs
only("L34", ["me", "dev"])
put("me", "L34", [57.4, 2.9], 180, expr="smile")
put("dev", "L34", [58.6, 2.9], 180, expr="smile")
clock("L34", 10, 0)
clock("L34.1", 12, 0)
clock("L34.1+0.5", 2, 0)
shot("L34", mv([58.0, 6.2, 1.7], [58.0, 2.9, 1.5], 36, [58.0, 5.6, 1.7], [58.0, 2.9, 1.5], 36), "sidebyside")
# L35 coffee, the bag, the bench
only("L35", ["me", "dev"])
vis("L35", "cups", True)
put("me", "L35", [G.SEAT_ME[0], G.SEAT_ME[1]], 90, expr="smile")
put("dev", "L35", [G.SEAT_DEV[0], G.SEAT_DEV[1]], -90, expr="warm")
cue("L35", "sit", who="me", on=True, z=0.55)
cue("L35", "sit", who="dev", on=True, z=0.55)
shot("L35", mv([TX - 0.2, 4.4, 1.15], [TX, 6.6, 0.95], 44, [TX + 0.1, 4.8, 1.1], [TX, 6.6, 0.95], 44), "coffees")
only("L35.1", ["dev"])
vis("L35.1", "cups", False)
vis("L35.1", "bag2", True)
put("dev", "L35.1", [BX - 1.2, BY + 0.9], 135, expr="smile", arms=[0, 80])
shot("L35.1", mv([BX - 2.6, BY + 2.6, 1.0], [BX - 1.0, BY, 0.75], 40, [BX - 2.3, BY + 2.3, 0.95], [BX - 1.0, BY, 0.75], 40), "tapebag")
only("L35.2", ["me", "dev"])
put("me", "L35.2", [BX - 0.45, BY], 180, expr="smile")
put("dev", "L35.2", [BX + 0.55, BY], 180, expr="warm")
cue("L35.2", "sit", who="me", on=True, z=0.62)
cue("L35.2", "sit", who="dev", on=True, z=0.62)
shot("L35.2", fc([BX + 0.05, BY], 180, 4.6, 36, h=1.35, tz=1.0, off=0.12, push=0.2), "bench")
# L36 walking down the bright street
clock("L36", 3, 0)
only("L36", ["me", "dev"])
cue("L36", "sit", who="me", on=False)
cue("L36", "sit", who="dev", on=False)
vis("L36", "bag2", False)
put("me", "L36", [74.0, 2.6], 90, expr="smile")
put("dev", "L36", [75.2, 2.6], 90, expr="smile")
go("me", "L36>", [78.0, 2.6])
go("dev", "L36>", [79.2, 2.6])
shot("L36", mv([82.0, -0.8, 1.6], [77.0, 2.6, 1.5], 34, [81.4, -0.6, 1.6], [77.8, 2.6, 1.5], 34), "walking")
# L37 the reveal: Dev and me on the bench in a perfect empty ring, a face at every window
only("L37", ["me", "dev"] + FACES[:8])
put("me", "L37", [BX - 0.45, BY], 180, expr="smile")
put("dev", "L37", [BX + 0.55, BY], 180, expr="warm")
cue("L37", "sit", who="me", on=True, z=0.62)
cue("L37", "sit", who="dev", on=True, z=0.62)
WIN37 = [WINS[k] for k in (11, 12, 13, 14, 15, 16, 17, 18)]
for nm, wx in zip(FACES[:8], WIN37):
    put(nm, "L37", [wx, 5.35, G.FACE_Z], 0, expr="worried", head=[0, 0])
shot("L37", mv([BX - 6.0, -27.0, 15.0], [BX + 0.2, -1.5, 3.0], 30, [BX - 4.0, -26.0, 14.0], [BX + 0.2, -1.5, 3.0], 30), "reveal")
shot("L37.2", mv([BX + 7.0, -17.0, 4.5], [BX - 0.5, -2.0, 3.2], 30, [BX + 5.5, -16.0, 4.2], [BX - 0.5, -2.0, 3.2], 30), "reveal2")
only("L38", ["me"])
put("me", "L38", [BX - 0.45, BY], 180, expr="wide")
cue("L38", "sit", who="me", on=True, z=0.62)
shot("L38", fc([BX - 0.45, BY], 180, 2.4, 44, h=1.45, tz=1.35, off=0.12, push=0.2), "getit")
# L39 to L43 the cafe, the plate, the radio
clock("L39", 5, 0)
only("L39", ["me", "dev"])
cue("L39", "sit", who="me", on=True, z=0.55)
cue("L39", "sit", who="dev", on=True, z=0.55)
put("me", "L39", [G.SEAT_ME[0], G.SEAT_ME[1]], 90, expr="sad-smile", head=[0, 10])
put("dev", "L39", [G.SEAT_DEV[0], G.SEAT_DEV[1]], -90, expr="warm")
shot("L39", mv([TX - 1.1, 8.9, 1.45], [G.SEAT_ME[0], 6.6, 1.3], 36, [TX - 1.0, 8.5, 1.45], [G.SEAT_ME[0] + 0.1, 6.6, 1.3], 36), "sorry")
shot("L39.2", fc([G.SEAT_ME[0], 6.6], 20, 2.4, 44, h=1.4, tz=1.25, off=0.14, push=0.2), "sorry2")
beat("dev", "L40", expr="smile", head=[0, 0])
shot("L40", mv([TX + 1.1, 8.9, 1.45], [G.SEAT_DEV[0], 6.6, 1.3], 36, [TX + 1.0, 8.5, 1.45], [G.SEAT_DEV[0] - 0.1, 6.6, 1.3], 36), "devsmile")
shot("L40.2", mv([TX + 1.4, 8.6, 1.5], [TX + 1.2, 3.0, 1.5], 42, [TX + 1.3, 8.2, 1.5], [TX + 1.3, 3.0, 1.5], 42), "window")
vis("L41", "plates", True)
vis("L41", "cake", True)
cue("L41", "plate", u=0.0)
cue("L41+0.2", "plate", u=1.0, dur=0.8)
shot("L41", mv([TX - 0.1, 6.6, 1.9], [TX, 6.6, 0.85], 38, [TX + 0.05, 6.55, 1.7], [TX, 6.6, 0.85], 38), "cake")
only("L42", [])
clock("L42", 8, 0)
shot("L42", mv([KX - 1.25, 0.5, 1.34], [KX - 0.97, 1.9, 1.34], 44, [KX - 1.1, 0.9, 1.34], [KX - 0.97, 1.9, 1.34], 44), "dial4")
shot("L42.2", mv([KX + 1.4, -0.6, 1.9], [KX - 1.0, 2.4, 1.1], 34, [KX + 0.9, -0.2, 1.8], [KX - 1.0, 2.4, 1.1], 34), "radiowide")
clock("L43", 11, 59)
only("L43", ["me", "dev"])
vis("L43", "plates", True)
put("me", "L43", [G.SEAT_ME[0], G.SEAT_ME[1]], 90, expr="laugh")
put("dev", "L43", [G.SEAT_DEV[0], G.SEAT_DEV[1]], -90, expr="laugh")
cue("L43", "sit", who="me", on=True, z=0.55)
cue("L43", "sit", who="dev", on=True, z=0.55)
shot("L43", mv([TX - 0.6, 9.2, 1.5], [TX, 6.6, 1.25], 38, [TX - 0.4, 8.8, 1.5], [TX, 6.6, 1.25], 38), "laugh")
# L44 the next morning, the radio's back
clock("L44", 7, 0)
cue("L44", "pair", n=1.0)
only("L44", ["me"])
put("me", "L44", [-81.2, 1.0], 180, expr="worried", head=[0, 14])
shot("L44", mv([KX - 1.9, 3.5, 1.55], [KX - 1.1, 2.2, 1.0], 36, [KX - 1.4, 3.7, 1.5], [KX - 1.1, 2.2, 1.0], 36), "radioback")
shot("L44.1", mv([KX - 1.2, 3.9, 1.42], [KX - 1.2, 1.0, 1.3], 34, [KX - 1.1, 3.4, 1.4], [KX - 1.2, 1.0, 1.3], 34), "radioback2")
only("L45", ["odell"])
put("odell", "L45", [OD, 5.6, 0.3], 0, expr="wide")
beat("odell", "L45.1", expr="smile")
shot("L45", mv([OD + 0.4, 1.0, 1.35], [OD, 5.6, 1.35], 36, [OD + 0.3, 1.6, 1.35], [OD, 5.6, 1.35], 36), "odell")
only("L46", ["me", "dev", "odell"])
cue("L46", "pair", n=2.0, dur=0.5)
vis("L46", "cups2", False)
put("dev", "L46", [OD + 1.6, 3.6, 0.3], 0, expr="warm")
put("me", "L46", [OD + 3.2, 3.6, 0.3], 0, expr="smile")
put("odell", "L46", [OD, 5.6, 0.3], 0, expr="smile")
vis("L46.2", "cups2", True)
shot("L46", mv([OD + 2.4, -0.8, 1.6], [OD + 2.4, 3.6, 1.45], 36, [OD + 2.4, -0.4, 1.6], [OD + 2.4, 3.6, 1.45], 36), "porch")
shot("L46.2", mv([OD + 2.4, 1.6, 1.3], [OD + 2.4, 3.6, 0.95], 44, [OD + 2.4, 1.9, 1.2], [OD + 2.4, 3.6, 0.95], 44), "coffees2")
HOUSES = [x for i in range(6) for x in G.win_xs(OD - 20 + i * 8.0)]
only("L47", FACES[:8] + ["me", "dev"])
for nm, wx in zip(FACES[:8], HOUSES[1:9]):
    put(nm, "L47", [wx, -9.35, G.FACE_Z], 180, expr="worried", head=[0, 0])
shot("L47", mv([OD - 2.0, 3.0, 5.0], [OD - 3.0, -9.3, 4.9], 38, [OD + 4.0, 3.0, 5.0], [OD + 3.0, -9.3, 4.9], 38), "streetwindows")
shot("L47.2", mv([OD + 2.0, 1.6, 4.8], [HOUSES[5], -9.3, 5.0], 60, [OD + 2.0, 1.8, 4.9], [HOUSES[6], -9.3, 5.0], 60), "streetface")
only("L48", ["odell"])
put("odell", "L48", [OD, 5.6, 0.3], 0, expr="smile")
shot("L48", mv([OD + 0.3, 1.2, 1.45], [OD, 5.6, 1.4], 38, [OD + 0.1, 1.7, 1.45], [OD, 5.6, 1.4], 38), "odellsmile")
only("L48.1", ["me"])
clock("L48.1", 7, 2)
cue("L48.1", "pair", n=1.0)
put("me", "L48.1", [ME_K[0], ME_K[1]], 0, expr="smile", arms=[0, 100], head=[0, 8])
vis("L48.1", "cup", True)
shot("L48.1", mv([KX - 0.55, -0.2, 1.9], [KX - 1.3, 2.7, 1.5], 36, [KX - 0.2, -0.9, 1.95], [KX - 1.3, 2.7, 1.5], 36), "loopface")

# ---------------------------------------------------------------------------------------------- finish
for k_ in acting.values():
    remap_all(k_)
remap_all(cues)
shots, names = [], {}
for i, (at, camera, step, nm) in enumerate(SH):
    s = {"id": f"S{i + 1:02d}", "cam": camera, "step": step}
    if i:
        s["at"] = remap(at)
    shots.append(s)
    names[nm] = s["id"]

sfx = [
    {"at": "L01.3", "kind": "glitch", "db": -23, "dur": 0.45},
    {"at": "L01.3", "kind": "thud", "db": -9},
    {"at": "L11.1", "kind": "thud", "db": -23},
    {"at": "L13.1", "kind": "whoosh", "db": -20, "dur": 0.9},
    {"at": "L16+0.5", "kind": "creak", "db": -16, "dur": 0.5, "tone": "cardboard"},
    {"at": "L17", "kind": "thud", "db": -20},
    {"at": "L17.2", "kind": "thud", "db": -24},
    {"at": "L29", "kind": "whoosh", "db": -22, "dur": 0.8},
    {"at": "L46.2", "kind": "click", "db": -20},
]
music = {
    "root": 57, "mode": "major", "bpm": 116, "seed": 109,
    "sections": [
        {"at": 0, "voices": ["piano", "pad"], "energy": 0.35, "mode": "major"},
        {"at": "L03", "voices": ["piano", "pulse"], "energy": 0.42, "mode": "major"},
        {"at": "L09", "voices": ["piano", "pulse"], "energy": 0.4, "mode": "minor"},
        {"at": "L17", "voices": ["drone"], "energy": 0.35, "mode": "minor", "root": 45},
        {"at": "L27.2", "voices": ["choir"], "energy": 0.3, "mode": "minor", "root": 57},
        {"at": "L30", "voices": ["pad", "piano"], "energy": 0.45, "mode": "major", "root": 57},
        {"at": "L38", "voices": ["drone"], "energy": 0.3, "mode": "minor", "root": 45},
        {"at": "L39", "voices": ["pad"], "energy": 0.3, "mode": "major", "root": 57},
        {"at": "L44", "voices": ["piano", "pulse"], "energy": 0.4, "mode": "major", "root": 57},
    ],
}
sound = {
    "floor": "concrete", "steps_db": -26,
    "ambience": [{"kind": "traffic", "from": "L09", "to": "L26", "lufs": -44}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}, {"from": "L38", "to": "L38.1"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L38"), remap("L28")],
          "emph": [remap(x) for x in ["L01.3", "L02", "L11.1", "L12.2", "L13.2", "L16", "L19", "L28", "L33", "L38"]],
          "twist": remap("L37"),
          "hold": [names["ring"], names["reveal"], names["photo"], names["cafewindow"]],
          "sway": [names["ring"], names["ring2"], names["windows"], names["gasp"]]}
story = {
    "slug": "ep109-said-your-name",
    "title": "The Radio Said My NAME 📻",
    "made_for_kids": False,
    "premise": ("In a sunny town where the morning radio reads out one name and nobody may go near that person all day, "
                "the radio says mine, and a whole street steps away from me while my oranges roll."),
    "twist": ("The worst day of your life was never bad luck, only a whole town staying away, so the day my best friend "
              "Dev stays with me, nothing goes wrong, and the next morning we go to the next person named."),
    "world": ("A pastel main street on a Saturday with a bakery, a cafe with a striped awning, a bus shelter and a park "
              "bench, a kitchen with an old stone radio, and a white porch."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#8f7cff",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#d6eeff", "fog_density": 0.003, "fog_start": 40.0, "sky": "#6cc4ff",
             "sky_strength": 1.0, "exposure": 0.0, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.12, "contrast": 1.05,
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
    "set_moves": [],
    "clip_ok": [],
    "asr_forgive": [],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
print({k: v for k, v in names.items()})
