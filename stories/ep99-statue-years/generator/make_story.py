"""Writes ../story.json for ep99 "statue years" (script.md, 2026-11-03). Run: python stories/ep99-statue-years/generator/make_story.py

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
# the 0.6 s music drop before L25
idx = next(i for i, l in enumerate(lines) if l["id"] == "L25")
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
Z0, ZB = G.Z0, G.ZB


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
    "me": person("#dca97c", "#ffd23f", "#6a707c", "#f4f4f2", hair="swoop", hair_c="#c89a5a", sleeves="short", brow_w=1.9),
    "mom": person("#e6b48c", "#9cc98a", "#f6f0e6", "#d8c8a8", hair="long", hair_c="#7a4a2c", pattern="knit",
                  pattern_c="#7fb070", eyes="lashes", brow_w=1.9, extras=["coat"], width=0.96),
    "dad": person("#e2b088", "#c0543a", "#6b5a48", "#4a3626", hair="cap", hair_c="#b4b4ba",
                  collar="#f0e2c4", extras=["glasses"], width=1.06, extra_c="#3a3a3e"),
    "lark": person("#f0c8a0", "#2fa8a0", "#2c3a4a", "#7a4a2a", hair="bun", hair_c="#18120e", eyes="lashes",
                   extras=["apron"], extra_c="#fffaf0"),
    "c1": person("#b98456", "#4a8a5a", "#4a4036", "#2a2a2a", hair="buzz", hair_c="#1a1410", sleeves="short"),
    "c2": person("#f0c8a0", "#d8c8a8", "#5a6a7a", "#6a4a32", hair="cap", hair_c="#6a4a2a", hat="ballcap", hat_c="#c0543a"),
    "c3": person("#8a5a3a", "#8a5ab0", "#2a2a38", "#d8d0c8", hair="long", hair_c="#150f0c", eyes="lashes"),
    "c4": person("#e8b890", "#e8845a", "#3a4a5a", "#3a2a1a", hair="spiky", hair_c="#a05a2a", sleeves="short"),
    "c5": person("#d3a07a", "#3a8aaa", "#5a4a3a", "#2a3a2a", hair="swoop", hair_c="#2a2a2a"),
}
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


def shot(at, camera, step=2, hand=None, follow=None, name=None):
    SH.append((at, camera, step, hand, follow, name))


def statue(at, **kw):
    cue(at, "statue", **kw)


def tally(at, n, dur=0.45):
    cue(at, "tally", n=float(n), dur=dur)


def sit(who, at, on=True, z=0.62):
    cue(at, "sit", who=who, on=on, z=z)


# ---------------------------------------------------------------------------------------------- positions
SX, SY = G.STREET
CX, CY = G.COUNTER
HX, HY = G.HOME_IN
OX, OY = G.HOME_OUT
MX, MY = G.MIRRORS
CAX, CAY = G.CAL
SLX, SLY = G.SLAB
FACE_Y, FACE_Z = -0.4, ZB + 0.3 + 6.9 + 1.55       # the statue's face
cue(0, "look", id="day", dur=0)
cue(0, "statue", wr=12.0, beard=1.0, pitch=0.0, yaw=0.0)
cue(0, "tally", n=12.0)

# ===== 01 the rule (L01 to L12)
shot(0, mv([0.0, -13.6, FACE_Z - 0.4], [0.0, FACE_Y, FACE_Z + 0.05], 50, [0.0, -11.6, FACE_Z - 0.2], [0.0, FACE_Y, FACE_Z + 0.05], 50), name="face1")
shot("L01.1", mv([0.6, -13.0, FACE_Z - 0.5], [0.0, FACE_Y, FACE_Z + 0.25], 80, [0.2, -11.5, FACE_Z - 0.3], [0.0, FACE_Y, FACE_Z + 0.25], 80), name="eyes")
# L02: the tray of candles
shot("L02", mv([0.0, -9.6, Z0 + 0.9], [0.0, G.TRAY_Y, Z0 + 0.5], 32, [0.0, -8.2, Z0 + 1.0], [0.0, G.TRAY_Y, Z0 + 0.6], 32), name="tray")
shot("L02.2", mv([2.4, -8.2, Z0 + 0.8], [-0.5, G.TRAY_Y, Z0 + 0.8], 55, [1.4, -8.0, Z0 + 0.9], [-0.7, G.TRAY_Y, Z0 + 0.8], 55), name="flames")
# L03: a man lights a candle, then touches the toe
put("c1", "L03", [1.8, G.TRAY_Y - 1.4, Z0], 180, expr="soft", arms=[0, 55], lean=12)
beat("c1", "L03.1-0.1", arms=[0, 20], lean=0)
shot("L03", mv([4.2, -9.6, Z0 + 1.5], [1.5, G.TRAY_Y, Z0 + 1.0], 40, [3.6, -9.4, Z0 + 1.4], [1.7, G.TRAY_Y, Z0 + 1.0], 40), name="light")
put("c1", "L03.1", [-1.05, -4.55, Z0], 180, expr="soft", arms=[105, 0])
beat("c1", "L03.2", arms=[115, 0], head=[0, -8])
shot("L03.1", mv([2.6, -5.4, Z0 + 1.9], [-1.05, -4.1, Z0 + 1.5], 40, [2.2, -5.0, Z0 + 1.8], [-1.05, -4.1, Z0 + 1.6], 40), name="toe")
# L04: Mrs. Lark
only("L04", ["lark"])
put("lark", "L04", [CX, CY + 1.4], 0, expr="smile")
beat("lark", "L04.1", expr="grin", head=[10, 0])
shot("L04", mv([CX, CY - 3.0, 1.55], [CX, CY + 1.4, 1.5], 36, [CX, CY - 2.5, 1.55], [CX, CY + 1.4, 1.5], 36), name="lark")
shot("L04.1", mv([CX + 1.0, CY + 0.2, 1.95], [CX + 2.0, CY + 3.2, 1.95], 45, [CX + 1.4, CY + 1.2, 1.95], [CX + 2.0, CY + 3.2, 1.95], 45), name="photo")
shot("L04.2", mv([CX, CY - 1.0, 1.65], [CX, CY + 1.4, 1.6], 55, [CX, CY - 0.6, 1.65], [CX, CY + 1.4, 1.6], 55), name="lark2")
# L05: Mom and me on the main street
only("L05", ["mom", "me"])
put("mom", "L05", [SX - 0.75, SY - 1.0], 0, expr="grin")
put("me", "L05", [SX + 0.75, SY - 1.0], 0, expr="grin")
beat("me", "L05.1", head=[-12, 0], expr="smile")
shot("L05", mv([SX - 0.2, SY - 5.4, 1.4], [SX, SY - 1.0, 1.5], 38, [SX - 0.1, SY - 4.4, 1.45], [SX, SY - 1.0, 1.5], 38), name="momme")
shot("L05.1", mv([SX + 0.4, SY - 3.4, 1.6], [SX, SY - 1.0, 1.65], 52, [SX + 0.2, SY - 3.0, 1.62], [SX, SY - 1.0, 1.65], 52), name="momme2")
# L06: the beard
only("L06", [])
shot("L06", mv([0.0, -9.0, ZB + 8.2], [0.0, -0.6, ZB + 8.2], 36, [0.0, -9.0, ZB + 3.6], [0.0, -0.6, ZB + 3.8], 36), name="beard")
shot("L06.1", mv([4.2, -8.0, ZB + 2.4], [0.0, -1.8, ZB + 3.4], 40, [3.4, -7.6, ZB + 2.6], [0.0, -1.8, ZB + 3.5], 40), name="knees")
# L07: the cheek, the bench arm
shot("L07", mv([3.4, -5.6, 12.1], [0.9, -0.5, 12.4], 60, [2.8, -5.0, 12.3], [0.9, -0.5, 12.4], 60), name="cheek")
bx, by = G.BENCH
shot("L07+0.9", mv([bx + 1.7, by - 1.1, Z0 + 1.45], [bx + 1.74, by, Z0 + 0.9], 48, [bx + 1.7, by - 0.7, Z0 + 1.3], [bx + 1.74, by, Z0 + 0.9], 48), name="bencharm")
# L08: Dad on the bakery steps
only("L08", ["dad", "mom"])
put("dad", "L08", [SX - 0.7, SY + 0.8, 0.4], 0, expr="smile", arms=[0, 40])
put("mom", "L08", [SX + 0.7, SY + 0.8, 0.4], 0, expr="smile", arms=[40, 0])
beat("dad", "L08.1", head=[10, 0], expr="soft")
shot("L08", mv([SX - 0.3, SY - 3.4, 1.5], [SX, SY + 0.8, 1.7], 36, [SX - 0.1, SY - 2.8, 1.55], [SX, SY + 0.8, 1.7], 36), name="dad")
shot("L08.1", mv([SX + 0.5, SY - 2.0, 1.75], [SX, SY + 0.8, 2.0], 55, [SX + 0.3, SY - 1.6, 1.8], [SX, SY + 0.8, 2.0], 55), name="dad2")
# L09: a crowd of young faces, Dad's gray head in the middle
only("L09", ["dad", "c4", "c5"])
for who, x, y, e in [("c4", -1.4, -0.9, "grin"), ("dad", 0.0, -0.2, "smile"), ("c5", 1.4, -0.9, "smile")]:
    put(who, "L09", [SX + x, SY + y], 0, expr=e, arms=[0, 0])
beat("c4", "L09.1", head=[15, 0])
beat("dad", "L09.1", expr="soft")
shot("L09", mv([SX - 1.2, SY - 8.2, 1.5], [SX - 0.2, SY - 0.6, 1.6], 32, [SX + 1.2, SY - 7.4, 1.5], [SX + 0.2, SY - 0.6, 1.6], 32), name="crowd")
# L10: Dad laughs, pats his hair
only("L10", ["dad"])
put("dad", "L10", [SX, SY - 0.5], 0, expr="smile")
beat("dad", "L10.1", expr="laugh", arms=[0, 155], head=[0, 6])
shot("L10", mv([SX - 0.5, SY - 3.4, 1.7], [SX, SY - 0.5, 1.7], 44, [SX - 0.3, SY - 2.8, 1.72], [SX, SY - 0.5, 1.7], 44), name="dadlaugh")
# L11: a stranger at the counter looks from Dad to Mom
only("L11", ["dad", "mom", "c2"])
put("c2", "L11", [CX + 1.6, CY - 0.9], 0, expr="polite", head=[0, 0])
put("dad", "L11", [CX + 0.3, CY - 0.9], 0, expr="smile")
put("mom", "L11", [CX - 1.0, CY - 0.9], 0, expr="polite", side=[0, 125])
beat("c2", "L11+0.5", head=[-35, 0])
beat("c2", "L11+1.0", head=[35, 0])
shot("L11", mv([CX + 0.6, CY + 2.9, 1.85], [CX + 0.2, CY - 0.9, 1.6], 34, [CX + 0.3, CY + 2.4, 1.8], [CX + 0.2, CY - 0.9, 1.6], 34), name="stranger")
shot("L11.1", mv([CX - 0.2, CY + 1.4, 1.95], [CX - 0.3, CY - 0.9, 1.75], 55, [CX - 0.1, CY + 1.2, 1.95], [CX - 0.3, CY - 0.9, 1.75], 55), name="momhand")
# L12: the calendar, then me at the top of the steps
only("L12", [])
cue("L12", "flip", v=0.0)
cue("L12+0.1", "flip", v=1.0, dur=0.7)
shot("L12", mv([CAX, CAY - 5.4, 2.6], [CAX, CAY, 2.6], 38, [CAX, CAY - 4.6, 2.6], [CAX, CAY, 2.6], 38), name="calflip")
shot("L12+1.1", mv([CAX + 0.2, CAY - 3.2, 2.5], [CAX, CAY, 2.4], 50, [CAX, CAY - 2.6, 2.45], [CAX, CAY, 2.4], 50), name="calring")
put("me", "L12+1.9", [0.0, -15.2, Z0], 180, expr="smile")
shot("L12+1.9", mv([-0.6, -19.0, Z0 + 1.6], [0.0, -2.0, Z0 + 5.5], 28, [-0.2, -18.2, Z0 + 1.7], [0.0, -2.0, Z0 + 5.6], 28), name="mebehind")
put("me", "L12+2.6", [-1.8, -13.5, Z0], 172, expr="smile")
beat("me", "L12+3.0", expr="grin", head=[-12, 0])
shot("L12+2.6", mv([-3.6, -9.6, Z0 + 1.55], [-1.8, -13.5, Z0 + 1.5], 48, [-3.2, -9.9, Z0 + 1.55], [-1.8, -13.5, Z0 + 1.5], 48), name="meface")

# ===== 02 the statue gets younger (L13 to L24)
only("L13", [])
shot("L13", mv([0.0, -12.8, FACE_Z - 0.6], [0.0, FACE_Y, FACE_Z], 50, [0.0, -10.8, FACE_Z - 0.3], [0.0, FACE_Y, FACE_Z], 50), name="face2")
shot("L13.1", mv([-3.6, -11.0, FACE_Z - 0.4], [0.0, FACE_Y, FACE_Z], 55, [-3.0, -10.4, FACE_Z - 0.3], [0.0, FACE_Y, FACE_Z], 55), name="face3")
statue("L14", wr=11.0)
tally("L14+0.25", 11)
shot("L14", mv([-2.2, -6.8, FACE_Z - 0.2], [-0.7, FACE_Y, FACE_Z - 0.3], 70, [-1.8, -6.2, FACE_Z - 0.2], [-0.7, FACE_Y, FACE_Z - 0.3], 70), name="cheek1")
statue("L15", wr=10.0)
tally("L15+0.25", 10)
shot("L15", mv([-2.6, -6.4, FACE_Z + 0.1], [-1.2, FACE_Y, FACE_Z + 0.1], 80, [-2.2, -6.0, FACE_Z + 0.1], [-1.2, FACE_Y, FACE_Z + 0.1], 80), name="cheek2")
statue("L16", wr=7.0, beard=0.45)
tally("L16+0.2", 7, 0.6)
shot("L16", mv([7.0, -25.0, Z0 + 5.0], [0.0, 0.0, ZB + 5.5], 30, [5.5, -23.0, Z0 + 5.5], [0.0, 0.0, ZB + 5.5], 30), name="beardchest")
shot("L16.1", mv([-3.8, -8.6, ZB + 3.6], [0.0, -1.0, ZB + 5.6], 36, [-3.2, -8.4, ZB + 4.4], [0.0, -1.0, ZB + 5.8], 36), name="beardchest2")
# L17: the town at its mirrors
only("L17", ["c3", "c4", "c5"])
for who, xo, e in [("c3", -1.3, "worried"), ("c4", 0.0, "worried"), ("c5", 1.3, "wide")]:
    put(who, "L17", [MX + xo, MY + 0.9], 180, expr=e)
beat("c4", "L17+0.5", head=[0, 10], expr="wide")
shot("L17", mv([MX - 0.8, MY - 4.0, 1.7], [MX, MY + 1.5, 1.8], 26, [MX + 0.6, MY - 3.6, 1.7], [MX, MY + 1.5, 1.8], 26), name="mirrors")
only("L17.1", ["lark"])
put("lark", "L17.1", [CX - 2.8, CY + 2.3], 180, expr="worried")
beat("lark", "L17.1+0.6", head=[0, 10], expr="wide")
shot("L17.1", mv([CX - 2.2, CY + 0.3, 1.8], [CX - 2.8, CY + 3.2, 1.8], 38, [CX - 2.4, CY + 0.9, 1.8], [CX - 2.8, CY + 3.2, 1.8], 38), name="larkmirror")
# L18: me on the bench, worried
only("L18", ["me"])
put("me", "L18", [bx, by], 180, expr="worried", head=[0, 5])
sit("me", "L18", True, 0.62)
beat("me", "L18.1", head=[0, 14], expr="worried")
shot("L18", mv([bx + 2.4, by + 4.2, Z0 + 1.45], [bx, by, Z0 + 1.2], 38, [bx + 2.0, by + 3.8, Z0 + 1.45], [bx, by, Z0 + 1.2], 38), name="mebench")
shot("L18.1", mv([bx, by + 0.2, Z0 + 1.3], [0.0, -0.4, 12.3], 34, [bx + 0.3, by + 0.2, Z0 + 1.35], [0.0, -0.4, 12.0], 34), name="povface")
shot("L18.2", mv([bx + 1.2, by + 1.8, Z0 + 1.5], [bx, by, Z0 + 1.35], 58, [bx + 0.9, by + 1.6, Z0 + 1.5], [bx, by, Z0 + 1.35], 58), name="mebench2")
# L19: three young heads, no gray
only("L19", ["c3"])
sit("me", "L19", False)
put("c3", "L19", [SX - 3.0, SY - 1.0], 0, expr="smile")
shot("L19", mv([SX - 3.2, SY - 3.4, 1.7], [SX - 3.0, SY - 1.0, 1.7], 55), name="young1")
only("L19+0.5", ["c4"])
put("c4", "L19+0.5", [SX + 3.0, SY - 1.0], 0, expr="grin")
shot("L19+0.5", mv([SX + 3.3, SY - 3.4, 1.7], [SX + 3.0, SY - 1.0, 1.7], 55), name="young2")
only("L19+1.0", ["c5"])
put("c5", "L19+1.0", [SX, SY - 1.0], 0, expr="smile")
shot("L19+1.0", mv([SX - 0.2, SY - 3.4, 1.7], [SX, SY - 1.0, 1.7], 55), name="young3")
# L20 to L22: Mom at the hall mirror, one silver streak
only("L20", ["mom"])
put("mom", "L20", [HX - 1.5, HY + 2.0], 180, expr="soft")
shot("L20", mv([HX + 1.8, HY - 1.6, 1.75], [HX - 1.5, HY + 3.0, 1.7], 30, [HX + 1.4, HY - 1.4, 1.75], [HX - 1.5, HY + 3.0, 1.7], 30), name="hallmirror")
cue("L21", "mom", streak=1.0)
put("mom", "L21", [HX + 0.5, HY + 0.6], 0, expr="soft")
shot("L21", mv([HX + 0.3, HY - 1.0, 2.1], [HX + 0.5, HY + 0.6, 1.9], 70, [HX + 0.4, HY - 0.8, 2.1], [HX + 0.5, HY + 0.6, 1.9], 70), name="streak")
beat("mom", "L22", arms=[0, 150], expr="soft", head=[0, 4])
shot("L22", mv([HX + 1.2, HY - 0.9, 1.95], [HX + 0.5, HY + 0.6, 1.8], 50, [HX + 1.0, HY - 0.9, 1.95], [HX + 0.5, HY + 0.6, 1.8], 50), name="handstreak")
beat("mom", "L22.1", arms=[0, 0], expr="smile", head=[0, 0])
shot("L22.1", mv([HX + 0.5, HY - 1.8, 1.7], [HX + 0.5, HY + 0.6, 1.65], 50, [HX + 0.5, HY - 1.4, 1.7], [HX + 0.5, HY + 0.6, 1.65], 50), name="momsmile")

# ===== 03 dawn (L23 to L31)
only("L23", ["mom"])
cue("L23", "look", id="dawn0", dur=0)
put("mom", "L23", [OX, OY + 3.3], 0, expr="soft")
go("mom", "L23+0.2", [OX, OY + 3.3])
go("mom", "L23.1-0.1", [OX, OY - 2.6])
acting["mom"][-3]["sfx"] = "door"
shot("L23", mv([OX + 3.4, OY - 5.8, 1.3], [OX, OY + 1.0, 1.4], 34, [OX + 2.6, OY - 5.4, 1.3], [OX, OY + 0.4, 1.4], 34), name="doorway")
put("mom", "L23.1", [OX + 0.5, OY - 3.0], -90, expr="soft")
go("mom", "L23>", [OX - 3.5, OY - 3.0])
shot("L23.1", mv([OX - 1.0, OY - 8.6, 1.5], [OX - 1.5, OY - 3.0, 1.4], 26, [OX - 1.6, OY - 8.2, 1.5], [OX - 1.7, OY - 3.0, 1.4], 26), name="momwalk")
only("L24", ["me"])
put("me", "L24", [0.4, -25.6, 0.25], 180, expr="worried")
go("me", "L24+0.9", [0.4, -17.2, Z0 - 0.15])
go("me", "L24>", [0.4, -15.4, Z0])
shot("L24", mv([2.6, -31.0, 1.4], [0.4, -21.0, 1.6], 30, [2.2, -27.0, 1.4], [0.4, -19.0, 1.9], 30), name="follow")
shot("L24.1", mv([0.2, -13.4, Z0 + 1.55], [0.4, -19.0, 1.8], 45, [0.2, -13.2, Z0 + 1.5], [0.4, -18.0, 1.9], 45), name="mefront")
# the drop: the dawn park, the statue's outline
only("P01", [])
shot("P01", mv([-2.0, -30.0, 1.5], [0.0, 0.0, 9.5], 24, [0.0, -26.0, 1.9], [0.0, 0.0, 9.8], 24), name="outline")
statue("L25", pitch=38.0)
put("me", "L25", [-0.9, -14.0, Z0], 180, expr="wide")
put("mom", "L25", [0.4, -4.4, Z0], 180, expr="soft")
shot("L25", mv([0.4, -17.0, Z0 + 1.7], [0.0, -3.0, Z0 + 5.0], 26, [0.3, -16.4, Z0 + 1.7], [0.0, -2.0, Z0 + 5.6], 26), name="behindme")
shot("L25.2", mv([2.0, -10.0, ZB + 1.5], [0.0, -0.8, 12.0], 30, [1.6, -9.0, ZB + 2.5], [0.0, -0.8, 11.6], 30), name="bentface")
beat("mom", "L25.3", head=[0, -6])
shot("L25.3", mv([2.4, -10.0, Z0 + 1.5], [0.4, -4.4, Z0 + 1.5], 42, [1.6, -9.0, Z0 + 1.6], [0.4, -4.4, Z0 + 1.6], 42), name="feet")
# L26: it was Mom
put("mom", "L26", [0.4, -4.4, Z0], 0, expr="soft")
shot("L26", mv([0.2, -9.0, Z0 + 1.6], [0.4, -4.4, Z0 + 1.6], 42, [0.3, -7.8, Z0 + 1.6], [0.4, -4.4, Z0 + 1.6], 42), name="itwasmom")
# L27: her hand on the stone, a line slides onto her face
only("L27", ["mom"])
statue("L27", wr=6.0)
put("mom", "L27", [0.8, SLY, 0], 45, expr="soft", arms=[90, 90])
cue("L27.2", "slide", u=0.0)
cue("L27.2+0.1", "slide", u=1.0, dur=1.3)
cue("L27.2+1.4", "mom", smile=1.0)
tally("L27.2", 6, 0.5)
shot("L27", mv([-0.8, SLY - 4.4, 1.6], [0.9, SLY, 1.5], 30, [-0.4, SLY - 4.0, 1.6], [0.9, SLY, 1.5], 30), name="handcheek")
shot("L27.2", mv([0.2, SLY - 3.0, 1.65], [1.0, SLY, 1.55], 42, [0.5, SLY - 2.7, 1.65], [1.0, SLY, 1.55], 42), name="slide")
shot("L27.3", mv([-0.6, SLY - 3.2, 1.7], [1.0, SLY, 1.5], 38, [-0.2, SLY - 2.9, 1.7], [1.0, SLY, 1.5], 38), name="slide2")
only("L28", ["mom"])
put("mom", "L28", [0.4, -4.4, Z0], 0, expr="smile")
shot("L28", mv([0.4, -7.4, Z0 + 1.65], [0.4, -4.4, Z0 + 1.58], 55, [0.4, -6.6, Z0 + 1.65], [0.4, -4.4, Z0 + 1.58], 55), name="smileline")
# L29: me, then the sun comes up
put("me", "L29", [-8.0, -5.4, Z0], 0, expr="wide")
put("mom", "L29", [3.9, -3.2, ZB + 0.3], 0, expr="soft")
cue("L29", "look", id="dawn1", dur=1.6)
cue("L29", "rise", z=4.0)
cue("L29", "rise", z=16.0, dur=4.0)
cue("L29", "mom", streak=4.0)
shot("L29", mv([-5.2, -9.4, Z0 + 1.5], [-8.0, -5.4, Z0 + 1.5], 42, [-5.6, -9.0, Z0 + 1.5], [-8.0, -5.4, Z0 + 1.5], 42), name="meamazed")
beat("me", "L29.1", expr="amazed" if False else "wide", head=[20, -8])
shot("L29.1", mv([0.0, -17.0, Z0 + 0.9], [0.0, 0.0, 10.5], 26, [0.0, -15.5, Z0 + 1.1], [0.0, 0.0, 10.5], 26), name="sunrise")
# L30: Mom on the plinth looks down the hill
only("L30", ["mom"])
shot("L30", mv([7.6, -9.0, ZB + 1.9], [3.9, -3.2, ZB + 1.6], 36, [6.8, -8.4, ZB + 1.9], [3.9, -3.2, ZB + 1.6], 36), name="plinth")
beat("mom", "L30.1", head=[-14, 5], expr="soft")
shot("L30.1", mv([4.4, -6.6, ZB + 1.7], [3.9, -3.2, ZB + 1.6], 55, [4.2, -6.0, ZB + 1.7], [3.9, -3.2, ZB + 1.6], 55), name="plinth2")
# L31: she sees me
put("me", "L31", [2.2, -10.8, Z0], 180, expr="neutral")
beat("mom", "L31", expr="polite", head=[18, 0])
beat("mom", "L31.1", expr="laugh", head=[8, 0])
shot("L31", mv([2.6, -12.4, Z0 + 1.7], [3.9, -3.2, ZB + 1.7], 70, [3.0, -12.0, Z0 + 1.7], [3.9, -3.2, ZB + 1.7], 70), name="seesme")

# ===== 04 the warm turn (L32 to L40)
statue("L32", pitch=0.0)
cue("L32", "look", id="day", dur=0)
only("L32", ["mom", "dad"])
put("dad", "L32", [SX - 0.7, SY + 1.4], 0, expr="smile", arms=[0, 40])
put("mom", "L32", [SX + 0.7, SY + 1.4], 0, expr="laugh", arms=[40, 0])
go("dad", "L32+0.4", [SX - 0.7, SY - 3.4])
go("mom", "L32+0.4", [SX + 0.7, SY - 3.4])
shot("L32", mv([SX, SY - 9.0, 1.5], [SX, SY - 0.4, 1.6], 34, [SX, SY - 8.4, 1.5], [SX, SY - 0.8, 1.6], 34), name="armarm")
put("dad", "L32.1", [SX - 0.7, SY + 0.0], 0, expr="smile", arms=[0, 40])
put("mom", "L32.1", [SX + 0.7, SY + 0.0], 0, expr="smile", arms=[40, 0])
go("dad", "L32>", [SX - 0.7, SY - 2.2])
go("mom", "L32>", [SX + 0.7, SY - 2.2])
shot("L32.1", mv([SX, SY - 5.6, 1.7], [SX, SY - 0.6, 1.75], 50, [SX, SY - 5.6, 1.7], [SX, SY - 1.2, 1.75], 50), name="armarm2")
put("dad", "L33", [SX - 0.7, SY - 1.0], 180, expr="smile", arms=[0, 40])
put("mom", "L33", [SX + 0.7, SY - 1.0], 180, expr="smile", arms=[40, 0])
cue("L33", "mom", streak=6.0)
go("dad", "L33>", [SX - 0.7, SY + 0.7, 0.4])
go("mom", "L33>", [SX + 0.7, SY + 0.7, 0.4])
shot("L33", mv([SX, SY - 4.4, 1.9], [SX, SY + 0.8, 1.8], 42, [SX, SY - 3.8, 1.9], [SX, SY + 0.8, 1.8], 42), name="twoheads")
only("L34", ["lark", "dad", "mom"])
put("lark", "L34", [CX, CY + 1.4], 0, expr="smile")
put("dad", "L34", [CX - 0.8, CY - 1.0], 180, expr="smile", arms=[0, 40])
put("mom", "L34", [CX + 0.8, CY - 1.0], 180, expr="smile", arms=[40, 0])
only("L34.1", ["lark"])
beat("lark", "L34.1", expr="grin", head=[0, 5])
shot("L34", mv([CX, CY - 4.4, 1.6], [CX, CY + 0.2, 1.55], 36, [CX, CY - 3.6, 1.6], [CX, CY + 0.2, 1.55], 36), name="larksmile")
shot("L34.1", mv([CX + 0.4, CY - 2.8, 1.7], [CX, CY + 1.4, 1.6], 50, [CX + 0.3, CY - 2.4, 1.7], [CX, CY + 1.4, 1.6], 50), name="larksmile2")
# L35: the kitchen, my birthday
only("L35", ["me"])
put("me", "L35", [HX + 2.8, HY + 2.3], 0, expr="smile")
beat("me", "L35.1", expr="grin")
shot("L35", mv([HX + 2.8, HY - 1.1, 1.75], [HX + 2.8, HY + 1.0, 1.35], 40, [HX + 2.8, HY - 0.5, 1.7], [HX + 2.8, HY + 1.0, 1.35], 40), name="cupcake")
cue("L35.1", "flip", v=1.0)
only("L35.1", [])
shot("L35.1", mv([CAX + 0.1, CAY - 4.4, 2.5], [CAX, CAY, 2.4], 38, [CAX, CAY - 3.4, 2.45], [CAX, CAY, 2.4], 38), name="calcircle")
# L36: I walk past the statue
put("me", "L36", [-3.2, -8.4, Z0], 90, expr="smile")
go("me", "L36+0.85", [3.4, -8.4, Z0])
shot("L36", mv([0.6, -12.6, Z0 + 1.0], [0.0, -8.4, Z0 + 1.6], 34, [-0.4, -12.4, Z0 + 1.0], [0.4, -8.4, Z0 + 1.6], 34), name="walkpast")
put("me", "L36+0.9", [-2.4, -9.6, Z0], 90, expr="smile")
go("me", "L36>", [2.6, -9.6, Z0])
shot("L36+0.9", mv([-1.0, -5.2, Z0 + 0.5], [0.0, -9.6, Z0 + 1.0], 40, [1.0, -5.0, Z0 + 0.5], [0.4, -9.6, Z0 + 1.0], 40), name="walkpast2")
put("me", "L37", [0.0, -16.3, Z0], 0, expr="grin")
shot("L37", mv([0.0, -22.0, 1.8], [0.0, -16.3, Z0 + 1.5], 40, [0.0, -21.0, 2.0], [0.0, -16.3, Z0 + 1.55], 40), name="topstep")
# L38: the statue turns its head to watch me go
put("me", "L38", [2.4, -16.8, Z0], 0, expr="smile")
go("me", "L38+1.4", [2.4, -24.0, 0.3])
beat("me", "L38+1.4", expr="smile")
shot("L38", mv([2.0, -12.4, Z0 + 2.4], [2.4, -21.0, 1.7], 30, [2.2, -12.0, Z0 + 2.5], [2.4, -22.0, 1.4], 30), name="godown")
statue("L38.1", yaw=26.0)
cue("L38.1", "look", id="day", dur=0)
shot("L38.1", mv([2.4, -30.0, 0.6], [0.4, 0.0, 10.8], 28, [2.4, -28.0, 0.8], [0.4, 0.0, 11.4], 28), name="turned")
shot("L38.2", mv([3.4, -17.4, Z0 + 0.6], [0.4, -0.2, FACE_Z], 36, [2.8, -15.0, Z0 + 0.8], [0.4, -0.2, FACE_Z], 36), name="turned2")
shot("L39", mv([5.6, -12.6, FACE_Z - 0.5], [0.3, FACE_Y + 0.4, FACE_Z], 50, [4.8, -10.8, FACE_Z - 0.3], [0.3, FACE_Y + 0.4, FACE_Z], 50), name="turnedface")
shot("L39.1", mv([4.2, -9.0, FACE_Z - 1.0], [0.3, FACE_Y + 0.4, FACE_Z], 60, [3.6, -8.0, FACE_Z - 0.8], [0.3, FACE_Y + 0.4, FACE_Z], 60), name="turnedface2")
statue("L40", yaw=0.0)
only("L40", [])
shot("L40", mv([0.0, -13.6, FACE_Z - 0.4], [0.0, FACE_Y, FACE_Z + 0.05], 50, [0.0, -12.2, FACE_Z - 0.3], [0.0, FACE_Y, FACE_Z + 0.05], 50), name="loop")

def front(tx, ty, tz, d, lens, dx=0.0, push=0.14):
    return mv([tx + dx, ty - d, tz], [tx, ty, tz], lens, [tx + dx * 0.7, ty - d * (1 - push), tz], [tx, ty, tz], lens)


OVR = {
    "momme": front(SX, SY - 1, 1.4, 6.6, 36, -0.4), "momme2": front(SX, SY - 1, 1.5, 5.8, 34, 0.4),
    "dad": front(SX, SY + 0.8, 1.7, 6.6, 36, -0.3), "dad2": front(SX, SY + 0.8, 1.95, 5.6, 34, 0.3),
    "dadlaugh": front(SX, SY - 0.5, 1.55, 4.2, 46, -0.3),
    "stranger": front(CX + 0.2, CY - 0.9, 1.55, 7.2, 32, 0.5), "momhand": front(CX - 0.3, CY - 0.9, 1.6, 5.6, 40, 0.3),
    "lark": front(CX, CY + 1.4, 1.5, 4.6, 36), "photo": front(CX + 2.0, CY + 3.3, 1.95, 4.2, 40, -0.3),
    "lark2": front(CX, CY + 1.4, 1.6, 3.6, 55, 0.3),
    "armarm2": front(SX, SY - 0.6, 1.75, 5.6, 36),
    "twoheads": mv([SX, SY - 5.6, 1.9], [SX, SY + 0.8, 1.8], 32, [SX, SY - 4.8, 1.9], [SX, SY + 0.8, 1.8], 32),
    "larksmile": front(CX, CY + 0.2, 1.55, 5.8, 26), "larksmile2": front(CX, CY + 1.4, 1.6, 4.4, 45, 0.3),
}
SH[:] = [(a, OVR.get(nm, c), st, h, f, nm) for (a, c, st, h, f, nm) in SH]
# ---------------------------------------------------------------------------------------------- finish
cue(0, "rise", z=4.0)
cue(0, "mom", streak=0.0, smile=0.0)
cue(0, "flip", v=0.0)
cue(0, "slide", u=0.0)
for k_ in acting.values():
    remap_all(k_)
remap_all(cues)
shots, names = [], {}
for i, (at, camera, step, hand, follow, nm) in enumerate(SH):
    s = {"id": f"S{i + 1:02d}", "cam": camera, "step": step}
    if i:
        s["at"] = remap(at)
    if hand is not None:
        s["hand"] = hand
    if follow:
        s["follow"] = follow
    shots.append(s)
    names[nm] = s["id"]

sfx = [
    {"at": "L01.2", "kind": "thud", "db": -8},
    {"at": "L14", "kind": "thud", "db": -19},
    {"at": "L16", "kind": "thud", "db": -19},
    {"at": "L27.2+0.1", "kind": "whoosh", "db": -22},
    {"at": "L38.1", "kind": "creak", "db": -15, "dur": 1.5},
]
music = {
    "root": 55, "mode": "major", "bpm": 96, "seed": 99,
    "sections": [
        {"at": 0, "voices": ["piano", "pad"], "energy": 0.35, "root": 55, "mode": "major"},
        {"at": "L13", "voices": ["piano", "drone"], "energy": 0.3, "root": 55, "mode": "minor"},
        {"at": "L25", "voices": ["drone", "piano"], "energy": 0.4, "root": 43, "mode": "minor"},
        {"at": "L29", "voices": ["piano", "pad"], "energy": 0.45, "root": 55, "mode": "major"},
        {"at": "L32", "voices": ["piano", "pad", "pulse"], "energy": 0.6, "root": 55, "mode": "major"},
        {"at": "L38", "voices": ["drone"], "energy": 0.3, "root": 43, "mode": "minor"},
    ],
}
sound = {
    "floor": "stone", "steps_db": -26,
    "ambience": [{"kind": "wind", "from": 0, "to": "end", "lufs": -42},
                 {"kind": "crickets", "from": "L23", "to": "L28", "lufs": -44}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L26")], "emph": [remap(x) for x in ["L01.2", "L05.1", "L07.1", "L20", "L26", "L33", "L37"]],
          "quiet": [[remap("L32"), remap("L34")]], "sway": [names["slide"], names["slide2"]],
          "hold": [names["photo"]]}
story = {
    "slug": "ep99-statue-years",
    "title": "Nobody Here Ages But The STATUE",
    "made_for_kids": False,
    "premise": ("In a sunny hilltop town where you give a giant stone statue your year on every birthday so nobody "
                "ages, I watch the statue get younger one wrinkle a day while my mom grows her first gray hair and "
                "slips out before sunrise."),
    "twist": ("Mom is taking her own years back from the statue, one every morning, so she can grow old beside my "
              "dad, the only man in town who never gave one away. On my birthday I keep mine."),
    "world": ("A hilltop park above a small town of rose sandstone houses and sunflower window boxes: a long flight of "
              "brick steps, sunflower beds, a giant seated sandstone statue with a stone beard, a brass tray of "
              "birthday candles, a bakery with a striped awning."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#46d2ff",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#cfe6f5", "fog_density": 0.004, "fog_start": 30.0, "sky": "#8fd3ff",
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
    "set_moves": [names["calflip"], names["slide"], names["slide2"], names["sunrise"], names["handcheek"]],
    "clip_ok": ["crack", "S54/slab.crack", "S55/slab.crack"],
    "asr_forgive": ["statue's", "turn twenty one", "two", "toward", "twenty first", "watched"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
print({k: v for k, v in names.items()})
