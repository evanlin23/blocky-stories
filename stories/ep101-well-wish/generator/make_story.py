"""Writes ../story.json for ep101 "well wish" (script.md, 2026-11-04). Run: python stories/ep101-well-wish/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0,
+x 90, +y 180, -x -90. Time references use the script's chunk numbers; captions are split to two or three words and
the references are remapped.
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
REV = 3
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = [], {}
for ln in orig_lines:
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
idx = next(i for i, l in enumerate(lines) if l["id"] == "L33")
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


def A(tgt, yaw, d, off=0.0, dz=0.0, lens=36, push=0.14, swing=7.0, tz=None):
    """A camera d metres from tgt along the direction yaw (+ off) degrees, pushing in; looks at tgt."""
    tx, ty, z = tgt
    if d <= 3.8:                 # a close-up: stand back a little so the hair clears the tag and the head stays whole
        d = d * 1.2
    z2 = z if tz is None else tz
    a0, a1 = (yaw + off) * D2R, (yaw + off + swing) * D2R
    d1 = d * (1 - push)
    return mv([tx + d * math.sin(a0), ty - d * math.cos(a0), z + dz], [tx, ty, z2], lens,
              [tx + d1 * math.sin(a1), ty - d1 * math.cos(a1), z + dz], [tx, ty, z2], lens)


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
    "me": person("#dca97c", "#e3a72f", "#3d5a8a", "#f4f4f2", hair="spiky", hair_c="#4a3020", extras=["hooddown"], brow_w=1.9),
    "wes": person("#e2b088", "#3f7d4e", "#4a5368", "#5a3b24", hair="cap", hair_c="#c9a46a", pattern="plaid",
                  pattern_c="#2b5a37", height=1.07, width=1.04, brow_w=1.6),
    "mom": person("#e6b48c", "#d9a0a8", "#6a5a6a", "#d8c8a8", hair="mop", hair_c="#b4b4ba", pattern="knit",
                  pattern_c="#c28890", eyes="lashes", brow_w=1.9, width=0.96),
    "kemp": person("#e8b48c", "#ff7a8a", "#e8b48c", "#fffaf0", hair="long", hair_c="#e4e4e8", hat="bucket", hat_c="#ffe38a",
                   eyes="lashes", brow_w=1.9, width=0.96, sleeves="short"),
    "hobb": person("#d9a47c", "#8a96a8", "#5a5048", "#3a2a1a", hair="buzz", hair_c="#c0c0c8", hat="ballcap", hat_c="#7a6a58",
                   collar="#f0e8d8", width=1.04),
    "wom": person("#c68a5e", "#2fa8a0", "#3a4a5a", "#f4f4f2", hair="bun", hair_c="#1a1410", eyes="lashes", brow_w=1.9),
    "driver": person("#e8b48c", "#5a7ab0", "#3a4258", "#25272c", hair="cap", hair_c="#6a4a2a", hat="ballcap", hat_c="#2f4a7a",
                     width=1.08),
    "n1": person("#b98456", "#4a8aff", "#3a3a48", "#2a2a2a", hair="buzz", hair_c="#1a1410", hat="beanie", hat_c="#e8402f",
                 extras=["coat", "scarf"], extra_c="#ff9a4a"),
    "p1": person("#f0c8a0", "#8a5ab0", "#4a4036", "#2a2a2a", hair="swoop", hair_c="#6a4a2a"),
    "p2": person("#d3a07a", "#ee9c4a", "#3a3a48", "#2a2a2a", hair="long", hair_c="#150f0c", eyes="lashes"),
    "p3": person("#8a5a3a", "#3a8aaa", "#2a2a38", "#d8d0c8", hair="buzz", hair_c="#150f0c"),
}
acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0]}] for n in cast}
last = {n: [0, 0] for n in cast}
visible = set()
cues = []
SH = []


def put(who, at, pos, yaw=None, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False, "head": [0, 0], "lean": 0, "arms": [0, 0]}
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


def sit(who, at, on=True, z=0.62):
    cue(at, "sit", who=who, on=on, z=z)


def meter(at, bar=None, red=None, digits=None, num=None, dur=0.0):
    k = {}
    for key, v in (("bar", bar), ("red", red), ("digits", digits), ("num", num)):
        if v is not None:
            k[key] = float(v)
    if dur:
        k["dur"] = dur
    cue(at, "meter", **k)


def plink(at, glow=0):
    cue(at, "plink", glow=glow)


def coin(at, x=None, y=None, z=None, spin=None, att=None, who=None, dur=0.0):
    k = {}
    for key, v in (("x", x), ("y", y), ("z", z), ("spin", spin), ("att", att)):
        if v is not None:
            k[key] = float(v)
    if who is not None:
        k["who"] = who
    if dur:
        k["dur"] = dur
    cue(at, "coin", **k)


def look(at, id_, dur=0.0):
    cue(at, "look", id=id_, dur=dur)


# ------------------------------------------------------------------------------------------------ places
SQX, SQY = G.SQ
STX, STY = G.ST
HBX, HBY = G.HB
KPX, KPY = G.KP
LRX, LRY = G.LR
WRX, WRY = G.WR
HLX, HLY = G.HL
KTX, KTY = G.KT
BIX, BIY = G.BI
HWX, HWY = G.HW
MTX, MTY = G.MT
LPX, LPY = G.LP
WELL = (SQX, SQY, 0.6)
ME_W = (-2.5, 0.0)            # where I stand at the well (facing +x)
OT_W = (2.5, 0.0)             # where the other person stands (facing -x)
LANE = G.LANE_X
CURB_CAR = (LANE - 0.4, 3.0)
STOP_CAR = (LANE, -11.7)      # the car at the stop sign
PORCH = (STX - 8.6, 0.0)      # the porch deck (z 0.6)
STEP = (STX - 6.9, 0.0)       # the upper step (top at 0.4)
CORNER = (STX - 4.6, STY - 14.3)  # the sidewalk beside the stop sign


CARZ = 0.26                   # Wes's seat height in the car: head under the roof


def ride(at, v=1.0):
    cue(at, "ride", v=v)


def wes_seat_drive(at):
    sit("wes", at, True, CARZ)


# ============================================================================================ L01 to L07
cue(0, "look", id="day", dur=0)
cue(0, "meter", bar=0.3, red=0.0, digits=0.0, num=0.0)
# L01 -- the hook: a coin hits the well, then me, then Wes at the corner
coin(0, x=0.05, y=0.0, z=2.3, spin=0)
coin(0.01, z=0.64, spin=900, dur=0.62)
plink(0.66)
coin(0.72, z=-50.0)
COINCAM = mv([1.5, -1.9, 2.5], [0.0, 0.0, 1.4], 36, [1.2, -1.5, 2.4], [0.0, 0.0, 1.0], 36)
shot(0, COINCAM, name="coin1")
put("me", "L01.1-0.05", [ME_W[0], ME_W[1], 0], 90, expr="worried", head=[0, -12])
beat("me", "L01.2", head=[0, 0], expr="worried")
shot("L01.1", A((ME_W[0], ME_W[1], 1.5), 90, 3.0, off=-48, lens=40, push=0.16), name="mewell")
only("L01.2", ["wes"])
put("wes", "L01.2", [CORNER[0], CORNER[1], 0], 180, expr="sad-smile", arms=[0, 0])
cue("L01.2", "duffel", v=0)
shot("L01.2", A((CORNER[0], CORNER[1], 1.2), 180, 5.0, off=15, dz=0.0, lens=32, push=0.1), name="wescorner")
meter("L01.3", bar=1.0, red=1.0, dur=0.3)
beat("wes", "L01.3", head=[0, 5])
shot("L01.3", A((CORNER[0], CORNER[1], 1.6), 180, 2.9, off=-18, lens=40, push=0.16), name="wesface")
meter("L02", bar=0.3, red=0.0, dur=0.5)

# L02 -- the well grants every wish, word for word: a woman flips a coin over it
only("L02", ["wom"])
put("wom", "L02", [OT_W[0], OT_W[1], 0], -90, expr="hopeful", arms=[0, 70])
cue("L02", "look", id="day", dur=0)
coin("L02.1+0.05", x=1.7, y=0.0, z=1.4, spin=0)
coin("L02.1+0.07", x=0.0, y=0.0, z=0.64, spin=1080, dur=0.7)
plink("L02.1+0.8")
coin("L02.1+0.85", z=-50.0)
beat("wom", "L02.1", arms=[0, 0], expr="smile")
shot("L02", A((OT_W[0], OT_W[1], 1.5), -90, 3.6, off=30, lens=34, push=0.1), name="woman")
shot("L02.1+0.1", mv([-1.2, -1.7, 2.3], [0.9, 0.0, 1.0], 34, [-0.9, -1.4, 2.2], [0.5, 0.0, 0.8], 34), name="coindown")
shot("L02.2", mv([4.2, -6.0, 1.6], [0.0, 0.0, 1.3], 30, [3.4, -5.0, 1.6], [0.0, 0.0, 1.3], 30), name="wellsun")

# L03 -- not what you MEANT, what you SAID
only("L03", ["me"])
put("me", "L03", [ME_W[0], ME_W[1], 0], 90, expr="neutral", head=[-30, 0])
beat("me", "L03.1", expr="neutral", head=[0, 0])
shot("L03", A((ME_W[0], ME_W[1], 1.5), 90, 2.8, off=-42, lens=38, push=0.12), name="meserious")
shot("L03.1", mv([0.4, -1.3, 1.4], [0.0, 0.0, 0.58], 42, [0.15, -0.8, 1.2], [0.0, 0.0, 0.58], 42), name="tiltwater")

# L04, L05 -- Mrs. Kemp
only("L04", ["kemp"])
put("kemp", "L04", [ME_W[0], ME_W[1], 0], 90, expr="shut", arms=[40, 0])
cue("L04", "puff", v=0)
shot("L04", A((ME_W[0], ME_W[1], 1.5), 90, 3.2, off=-40, lens=38, push=0.12), name="kemp1")
beat("kemp", "L04.1+0.3", expr="smile", arms=[0, 0], head=[0, 8])
shot("L04.1+0.3", A((ME_W[0], ME_W[1], 1.55), 90, 2.5, off=-22, lens=40, push=0.18), name="kemp2")
only("L05", ["kemp", "n1"])
look("L05", "snow")
put("kemp", "L05", [KPX - 9.2, KPY + 14.0, 0], 90, expr="grin", arms=[0, 0])
sit("kemp", "L05", True, 0.5)
put("n1", "L05", [KPX - 4.8, KPY + 24.0, 0], 180, expr="scared")
go("n1", "L05.1-0.02", [KPX - 4.8, KPY + 21.0, 0], tremble=7)
shot("L05", mv([KPX + 1.0, KPY + 5.0, 3.0], [KPX - 9.2, KPY + 12.6, 0.8], 22, [KPX + 0.7, KPY + 5.6, 2.8], [KPX - 9.2, KPY + 12.6, 0.8], 22),
     name="snowstreet")
go("n1", "L05.2", [KPX - 4.8, KPY + 17.0, 0], tremble=7)
beat("kemp", "L05.2", arms=[0, 165], expr="laugh")
shot("L05.1", A((KPX - 9.2, KPY + 14.0, 1.1), 90, 6.0, off=-35, lens=30, push=0.12), name="chair")
shot("L05.2+0.2", mv([KPX - 5.4, KPY + 10.4, 1.5], [KPX - 9.2, KPY + 13.8, 1.15], 30, [KPX - 5.9, KPY + 11.0, 1.45], [KPX - 9.2, KPY + 13.9, 1.15], 30), name="parka")

# L06, L07 -- Mr. Hobb
only("L06", ["hobb"])
look("L06", "day")
put("hobb", "L06", [HBX - 4.8, HBY + 12.0, 0], 0, expr="neutral", arms=[70, 70])
go("hobb", "L06.1+0.15", [HBX - 4.8, HBY + 9.0, 0])
shot("L06", A((HBX - 4.8, HBY + 10.5, 1.3), 90, 6.5, off=20, lens=34, push=0.1), name="hobb1")
beat("hobb", "L06.1+0.2", arms=[0, 55], expr="worried")
shot("L06.1+0.2", A((HBX - 4.8, HBY + 9.0, 1.15), 90, 4.6, off=-30, lens=30, push=0.1), name="watch")
only("L07-0.02", [])
cue("L07-0.02", "bus", x=HBX - 1.5, y=HBY + 6.0, yaw=0.0)
shot("L07", A((HBX - 1.5, HBY + 6.0, 1.7), 90, 11.0, off=-30, lens=34, push=0.1), name="bus1")
only("L07.1-0.1", ["p1", "p2", "p3"])
for who, x, y in (("p1", BIX - 1.3, BIY + 0.4), ("p2", BIX + 1.3, BIY + 1.8), ("p3", BIX - 1.3, BIY + 3.2)):
    put(who, "L07.1-0.1", [x, y, 0], 0, expr="worried", arms=[0, 0])
    sit(who, "L07.1-0.1", True, 0.64)
    beat(who, "L07.1", arms=[0, 100], expr="worried")
shot("L07.1", mv([BIX + 0.2, BIY - 2.6, 1.7], [BIX, BIY + 1.8, 1.2], 38, [BIX + 0.1, BIY - 2.0, 1.65], [BIX, BIY + 1.8, 1.2], 38), name="watchers")
only("L07.2+0.1", ["hobb"])
put("hobb", "L07.2+0.1", [HBX - 5.0, HBY + 6.2, 0], 0, expr="smile", arms=[0, 0])
go("hobb", "L07.2+0.9", [HBX - 3.7, HBY + 2.9, 0])
beat("hobb", "L07.2+1.0", arms=[0, 150], expr="grin")
shot("L07.2+0.2", mv([HBX - 8.7, HBY + 4.6, 1.5], [HBX - 5.0, HBY + 6.0, 1.1], 26, [HBX - 8.3, HBY + 1.8, 1.5], [HBX - 3.9, HBY + 3.2, 1.1], 26), name="hobbboard")

# ============================================================================================ L08 to L12 (three years ago)
only("L08", ["wes", "me"])
look("L08", "day")
cue("L08", "wbox", v=1.0)
cue("L08", "duffel", v=2.0)
put("wes", "L08", [STX - 9.5, STY - 0.3, 0.6], 90, expr="grin", arms=[75, 75])
go("wes", "L08.1+0.6", [STX - 6.6, STY - 0.3, 0.3])
put("me", "L08", [STX - 9.1, STY + 1.6, 0.6], 90, expr="worried", arms=[0, 0])
shot("L08", A((STX - 8.4, STY - 0.3, 1.5), 90, 5.6, off=-32, lens=34, push=0.12), name="wesbox")
shot("L08.1", mv([STX - 3.2, STY + 3.6, 1.8], [STX - 7.0, STY - 0.3, 1.6], 32, [STX - 3.0, STY + 3.4, 1.8], [STX - 6.7, STY - 0.3, 1.6], 32), name="weswho")
beat("wes", "L08.2", arms=[75, 75], expr="grin")
shot("L08.2", A((STX - 8.8, STY + 1.6, 2.0), 90, 4.4, off=-25, lens=34, push=0.12), name="medoor")
cue("L09", "wbox", v=0.0)
only("L09", ["me"])
put("me", "L09", [LRX - 0.5, LRY - 0.8, 0], 90, expr="sad-smile", head=[0, 6])
shot("L09", mv([LRX - 3.4, LRY - 3.0, 1.6], [LRX + 0.8, LRY - 0.9, 1.0], 32, [LRX - 2.8, LRY - 2.7, 1.6], [LRX + 1.3, LRY - 0.9, 1.0], 32), name="empty")
beat("me", "L09.2", head=[0, 0], expr="worried")
shot("L09.2", A((LRX - 0.5, LRY - 0.8, 1.5), 90, 3.6, off=-30, lens=36, push=0.12), name="mealone")
put("me", "L09.4-0.05", [LRX + 0.2, LRY + 0.3, 0], 180, expr="sad-smile")
shot("L09.4", mv([LRX - 2.4, LRY - 1.2, 1.6], [LRX + 0.8, LRY + 2.3, 1.0], 32, [LRX - 1.8, LRY - 1.0, 1.6], [LRX + 1.2, LRY + 2.4, 1.2], 32), name="stairs")

# L10, L11 -- I make the wish, at dusk
only("L10", ["me"])
look("L10", "dusk", 0.5)
put("me", "L10", [ME_W[0], ME_W[1], 0], 90, expr="worried", arms=[0, 70])
coin("L10", att=1, who="me")
shot("L10", A((ME_W[0], ME_W[1], 1.35), 90, 2.7, off=-38, lens=36, push=0.12), name="coinhand")
coin("L10.2", att=0, x=-2.0, y=0.0, z=1.2, spin=0)
coin("L10.2+0.02", z=2.5, spin=540, dur=0.42)
coin("L10.2+0.5", z=1.35, spin=1080, dur=0.4)
shot("L10.2", mv([-1.1, -3.9, 1.5], [-2.4, 0.0, 1.7], 30, [-1.5, -3.5, 1.6], [-2.4, 0.0, 1.8], 30), name="coinflip")
beat("me", "L10.2+0.5", arms=[0, 80])
coin("L11", att=1, who="me")
beat("me", "L11", expr="shut", arms=[0, 70])
shot("L11", A((ME_W[0], ME_W[1], 1.55), 90, 2.5, off=-35, lens=40, push=0.14), name="mewish")
coin("L11.1+0.36", att=0, x=-0.8, y=0.0, z=1.2, spin=0)
coin("L11.1+0.38", x=0.0, z=0.64, spin=480, dur=0.33)
plink("L11.1+0.75", 1)
coin("L11.1+0.8", z=-50.0)
shot("L11.1+0.36", mv([0.9, -1.3, 1.3], [0.0, 0.0, 0.6], 40, [0.6, -0.8, 1.1], [0.0, 0.0, 0.6], 40), name="goldrings")

# L12 -- he drives off
only("L12", ["wes"])
look("L12", "day")
cue("L12", "duffel", v=0)
put("wes", "L12", [CURB_CAR[0] + 0.45, CURB_CAR[1] + 0.35, 0], 0, expr="grin")
sit("wes", "L12", True, CARZ)
ride("L12")
cue("L12", "car", x=LANE, y=-4.0, yaw=0.0, dur=0.9)
cue("L12+0.9", "car", x=LANE, y=STOP_CAR[1], dur=1.35)
meter("L12+0.8", bar=1.0, dur=1.3)
shot("L12", A((CURB_CAR[0], CURB_CAR[1] - 2.0, 0.9), 90, 8.0, off=-35, lens=32, push=0.12), name="pullaway")
beat("wes", "L12.1", expr="grin", arms=[0, 150])
shot("L12.1", A((LANE + 0.45, -6.0, 1.3), 90, 3.8, off=-30, lens=34, push=0.1, dz=0.05), name="waving")
shot("L12.2", A((LANE, -9.0, 1.0), 270, 6.5, off=25, lens=32, push=0.1), name="notchrise")

# ============================================================================================ L13 to L20 (the leash)
meter("L13", bar=1.0, red=1.0)
shot("L13", A((LANE, STOP_CAR[1] + 1.5, 0.8), 0, 5.0, off=165, lens=30, push=0.1, dz=0.5), name="halt")
beat("wes", "L13.1", expr="angry", arms=[0, 0])
shot("L13.1", A((LANE + 0.45, STOP_CAR[1] + 0.4, 1.4), 0, 3.0, off=-8, lens=36, push=0.12), name="keyturn")
cue("L14", "car", x=LANE, y=-4.0, dur=1.2)
cue("L14.1", "car", x=CURB_CAR[0] - 0.0, y=CURB_CAR[1], dur=1.1)
meter("L14", bar=0.2, red=0.0, dur=1.0)
beat("wes", "L14", arms=[75, 75], expr="wide", head=[0, -10])
shot("L14", mv([LANE + 4.6, -12.8, 1.4], [LANE, -11.9, 1.25], 24, [LANE + 4.6, -9.8, 1.4], [LANE, -9.0, 1.25], 24), name="rollback")
shot("L14.1", A((CURB_CAR[0], CURB_CAR[1], 0.9), 90, 7.5, off=-40, lens=32, push=0.12), name="parked")
only("L14.2", ["wes", "me"])
ride("L14.2", 0.0)
put("me", "L14.2", [PORCH[0], PORCH[1] + 1.0, 0.6], 90, expr="scared")
put("wes", "L14.2", [CURB_CAR[0] + 0.45, CURB_CAR[1] + 0.35, 0], 0, expr="angry")
sit("wes", "L14.2", True, CARZ)
ride("L14.2", 1.0)
shot("L14.2", A((PORCH[0], PORCH[1] + 1.0, 2.0), 90, 4.2, off=-30, lens=34, push=0.1), name="porchscared")
# L15 -- the bus
ride("L15-0.02", 0.0)
only("L15", ["wes"])
cue("L15", "duffel", v=1.0)
put("wes", "L15", [BIX + 1.3, BIY + 0.4, 0], 0, expr="sad-smile")
sit("wes", "L15", True, 0.64)
shot("L15", A((BIX + 1.3, BIY + 0.4, 1.3), 0, 4.0, off=180 + 20, lens=34, push=0.12), name="wesbus")
cue("L15.1", "bus", x=HBX - 1.5, y=HBY + 6.0, yaw=0.0)
cue("L15.1+0.05", "bus", x=HBX - 0.6, y=HBY + 5.4, yaw=80.0, dur=0.45)
cue("L15.1+0.5", "bus", x=HBX - 1.2, y=HBY + 6.4, yaw=180.0, dur=0.45)
only("L15.1", [])
shot("L15.1", A((HBX - 1.0, HBY + 6.0, 1.6), 90, 12.0, off=-25, lens=34, push=0.1), name="uturn")
# L16 -- walking
only("L16", ["wes"])
cue("L16", "duffel", v=0)
sit("wes", "L16", False)
meter("L16", bar=0.4, red=0.0)
put("wes", "L16", [STX - 4.6, STY - 3.0, 0], 0, expr="neutral")
go("wes", "L16+1.0", [CORNER[0], CORNER[1], 0])
meter("L16+0.9", bar=1.0, red=1.0, dur=0.3)
shot("L16", A((STX - 4.6, STY - 7.0, 1.2), 90, 7.5, off=-60, lens=32, push=0.1), name="stride")
go("wes", "L16.1+0.05", [CORNER[0], CORNER[1] + 4.0, 0], keep_yaw=True, yaw=0)
beat("wes", "L16.1+0.05", yaw=0, expr="angry")
shot("L16.1", mv([CORNER[0] + 3.6, CORNER[1] + 3.0, 1.3], [CORNER[0], CORNER[1] + 0.5, 0.9], 22,
                 [CORNER[0] + 3.4, CORNER[1] + 3.1, 1.3], [CORNER[0], CORNER[1] + 0.7, 0.9], 22), name="feet")
go("wes", "L16.2+0.95", [STX - 7.5, STY - 0.4, 0.4], keep_yaw=True, yaw=0)
shot("L16.2+0.35", A((STX - 6.5, STY - 1.0, 1.2), 90, 6.0, off=-40, lens=34, push=0.1), name="backwalk")
# L17 -- one block, never one inch more
meter("L17", bar=1.0, red=1.0)
shot("L17", A((MTX, MTY, 3.0), 0, 5.2, off=0, lens=32, push=0.1), name="bigmeter")
put("wes", "L17.1+0.22", [CORNER[0], CORNER[1], 0], 180, expr="blank", head=[0, 25])
shot("L17.1+0.27", A((CORNER[0], CORNER[1], 1.4), 180, 4.6, off=-22, lens=30, push=0.1, dz=0.0), name="crack")
# L18 -- he never asked me why
meter("L18", bar=0.3, red=0.0, dur=0.6)
only("L18", ["wes", "me"])
put("me", "L18", [STEP[0], STEP[1] - 0.5, 0.4], 90, expr="worried", head=[0, 0])
put("wes", "L18", [STEP[0], STEP[1] + 0.5, 0.4], 90, expr="sad-smile")
sit("me", "L18", True, 0.47)
sit("wes", "L18", True, 0.47)
shot("L18", A((STEP[0] + 0.3, STEP[1], 1.3), 90, 5.0, off=-8, lens=32, push=0.1), name="porchpair")
beat("me", "L18+0.55", head=[-40, 0], expr="worried")
shot("L18+0.55", A((STEP[0] + 0.3, STEP[1], 1.3), 90, 5.0, off=-24, lens=32, push=0.1), name="sneak")
# L19 -- back into his old room
sit("me", "L19-0.02", False)
sit("wes", "L19-0.02", False)
only("L19", ["wes", "mom"])
cue("L19", "wbox", v=1.0)
put("mom", "L19", [LRX + 1.2, LRY + 1.0, 0], 90, expr="soft")
put("wes", "L19", [LRX - 2.2, LRY + 3.0, 0], 90, expr="sad-smile", arms=[75, 75])
go("wes", "L19+0.9", [LRX + 3.6, LRY + 3.0, 2.4])
shot("L19", mv([LRX + 0.8, LRY - 1.8, 1.8], [LRX + 0.8, LRY + 3.0, 1.2], 30, [LRX + 1.2, LRY - 1.6, 1.8], [LRX + 1.4, LRY + 3.0, 1.5], 30), name="upstairs")
only("L19.1", ["wes"])
cue("L19.1", "wbox", v=0.0)
cue("L19.1", "posters", n=0.0)
cue("L19.1", "season", v=0)
put("wes", "L19.1", [WRX + 1.2, WRY + 3.0, 0], 180, expr="sad-smile", arms=[0, 100])
cue("L19.1+0.5", "posters", n=1.0)
cue("L19.1+0.9", "posters", n=3.0)
shot("L19.1", mv([WRX - 0.6, WRY - 1.6, 1.8], [WRX + 0.8, WRY + 3.3, 1.8], 34, [WRX - 0.2, WRY - 1.4, 1.8], [WRX + 0.8, WRY + 3.3, 1.9], 34), name="posters")
# L20 -- three years: summer, autumn, snow
put("wes", "L20", [WRX + 2.0, WRY - 0.6, 0], 20, expr="neutral", arms=[0, 0])
sit("wes", "L20", True, 0.6)
cue("L20", "season", v=0)
cue("L20+0.4", "season", v=1)
cue("L20+0.8", "season", v=2)
shot("L20", mv([WRX - 0.8, WRY - 3.0, 1.5], [WRX + 2.7, WRY - 0.1, 1.25], 28, [WRX - 0.2, WRY - 2.9, 1.5], [WRX + 2.8, WRY - 0.1, 1.25], 28), name="summer")

# ============================================================================================ L21 to L24 (the job)
sit("wes", "L21-0.02", False)
only("L21", ["wes"])
cue("L21", "season", v=0)
put("wes", "L21", [KTX, KTY + 1.0, 0], 0, expr="wide")
sit("wes", "L21", True, 0.6)
cue("L21", "wphone", v=1.0, lit=1.0)
beat("wes", "L21", arms=[0, 70])
shot("L21", A((KTX, KTY + 1.0, 1.3), 0, 3.6, off=0, lens=36, push=0.12), name="job")
beat("wes", "L21.1+0.38", arms=[170, 170], expr="grin")
sit("wes", "L21.1+0.38", False)
cue("L21.1+0.38", "wphone", v=0.0)
shot("L21.1+0.38", A((KTX, KTY + 1.0, 1.4), 0, 4.2, off=-18, lens=34, push=0.1), name="punchair")
beat("wes", "L21.1+0.9", arms=[0, 0], expr="neutral")
only("L22", [])
shot("L22", A((LPX, LPY, 2.5), 0, 5.4, off=0, lens=34, push=0.1), name="map")
# L23, L24 -- at 2 a.m. I hear him turn it down
look("L23", "night", 0.5)
only("L23", ["me"])
put("me", "L23", [HLX + 2.9, HLY + 1.1, 0], 90, expr="worried", lean=0)
cue("L23", "wdoor", a=0.0)
shot("L23", mv([HLX + 0.3, HLY - 2.0, 1.1], [HLX + 3.0, HLY + 1.0, 1.0], 24, [HLX + 0.8, HLY - 1.9, 1.1], [HLX + 3.0, HLY + 1.0, 1.0], 24), name="lightline")
beat("me", "L23.1+0.2", head=[0, 10], lean=8, expr="worried")
shot("L23.1+0.2", A((HLX + 2.9, HLY + 1.1, 1.3), 90, 3.0, off=-55, lens=26, push=0.12), name="ear")
only("L24", ["me", "wes"])
cue("L24-0.6", "wdoor", a=-75.0, dur=0.5)
put("wes", "L24", [WRX - 2.4, WRY + 0.1, 0], -90, expr="warm", arms=[0, 165])
sit("wes", "L24", True, 0.62)
cue("L24", "wphone", v=1.0, lit=1.0)
shot("L24", mv([HLX + 1.8, HLY - 0.4, 1.3], [WRX - 2.4, WRY + 0.1, 1.5], 34, [HLX + 2.3, HLY - 0.3, 1.3], [WRX - 2.4, WRY + 0.1, 1.5], 34), name="gap")
beat("wes", "L24.1", arms=[0, 0], expr="blank", head=[0, -25])
cue("L24.1", "wphone", v=0.0)
shot("L24.1", mv([HLX + 2.0, HLY - 0.4, 1.2], [WRX - 2.4, WRY + 0.1, 1.2], 34, [HLX + 2.4, HLY - 0.3, 1.2], [WRX - 2.4, WRY + 0.1, 1.3], 34), name="ceiling")
sit("wes", "L24.2", False)
only("L24.3", ["me"])
put("me", "L24.3", [HLX + 0.8, HLY + 0.2, 0], 90, expr="worried", arms=[0, 115])
shot("L24.3", A((HLX + 0.8, HLY + 0.2, 1.3), 90, 3.0, off=-30, lens=26, push=0.12), name="handmouth")

# ============================================================================================ L25 to L30 (the well at night)
look("L25", "night")
only("L25", ["me"])
put("me", "L25", [-1.0, -12.0, 0], 0, expr="worried")
go("me", "L25.1+0.3", [-1.9, -2.0, 0])
shot("L25", mv([-7.0, -9.0, 2.2], [0.0, 0.0, 1.5], 30, [-6.0, -8.0, 2.0], [0.0, 0.0, 1.4], 30), name="nightwell")
shot("L25.1+0.25", mv([-7.2, -6.8, 1.3], [-0.9, -2.6, 0.9], 26, [-6.4, -5.9, 1.3], [-1.0, -1.6, 0.8], 26), name="basestone")
# L26 -- I can't take it back
put("me", "L26+0.2", [-3.0, 0.0, 0], 90, expr="sad-smile", lean=22)
shot("L26+0.2", A((-2.6, 0.0, 1.4), 90, 3.0, off=-40, lens=38, push=0.12), name="plead")
put("me", "L26.2", [0.0, -2.3, 0], 0, expr="blank", head=[0, -8])
sit("me", "L26.2", True, 0.2)
shot("L26.2", A((0.0, -2.3, 0.9), 0, 4.0, off=0, lens=36, push=0.12, dz=0.2), name="sitwell")
cue("L26.2", "clock", h=10.0, dur=0)
cue("L26.2+0.4", "clock", h=11.0, dur=0.4)
shot("L26.2+0.6", mv([SQX + 0.5, SQY - 1.0, 4.0], [SQX, SQY + 11.8, 5.6], 30, [SQX + 0.5, SQY + 0.0, 4.4], [SQX, SQY + 11.8, 5.6], 30), name="clock")
# L27 -- the coin comes back
sit("me", "L27-0.02", False)
put("me", "L27", [-2.2, 0.0, 0], 90, expr="wide", arms=[0, 0])
coin("L27.1-0.05", att=0, x=0.0, y=0.0, z=0.6, spin=0)
plink("L27.1-0.05", 0)
coin("L27.1-0.03", z=2.1, spin=720, dur=0.45)
shot("L27", mv([1.8, -2.4, 1.8], [0.0, 0.0, 1.3], 30, [1.5, -2.0, 1.8], [0.0, 0.0, 1.4], 30), name="spit")
coin("L27.1+0.4", att=1, who="me")
beat("me", "L27.1+0.4", arms=[0, 85], expr="wide")
shot("L27.1+0.4", A((-2.2, 0.0, 1.2), 90, 2.8, off=-35, lens=36, push=0.12), name="palm")
# L28, L29, L30 -- the words
only("L28", ["me"])
coin("L28", att=0, z=-50.0)
put("me", "L28", [-2.2, 0.0, 0], 90, expr="neutral", arms=[0, 0])
shot("L28", A((-2.2, 0.0, 1.55), 90, 2.4, off=-30, lens=42, push=0.14), name="moonface")
shot("L28.1+0.25", A((-2.2, 0.0, 1.45), 0, 4.0, off=14, lens=30, push=0.1), name="stillwater")
plink("L29.0+0.4", 1)
shot("L29", mv([0.8, -1.2, 1.2], [0.0, 0.0, 0.6], 40, [0.5, -0.8, 1.0], [0.0, 0.0, 0.6], 40), name="ringsback")
put("me", "L30", [-2.2, 0.0, 0], 90, expr="neutral")
coin("L30", att=1, who="me")
beat("me", "L30", arms=[0, 70])
shot("L30", A((-2.2, 0.0, 1.4), 90, 4.2, off=-35, lens=34, push=0.1), name="standup")
go("me", "L30.1", [-3.5, -4.0, 0], run=True)
go("me", "L30.2+0.6", [-3.5, -16.0, 0], run=True)
shot("L30.1", mv([-3.3, -10.5, 1.5], [-3.5, -4.0, 1.2], 28, [-3.3, -10.5, 1.5], [-3.5, -6.0, 1.2], 28), name="runout")
shot("L30.1+0.75", A((-3.5, -9.0, 1.3), 0, 7.0, off=165, lens=32, push=0.1), name="runout2")

# ============================================================================================ L31 to L35 (letting go)
look("L31", "dawn")
only("L31", ["me", "wes"])
cue("L31", "mbox", v=1.0)
coin("L31", att=0, z=-50.0)
put("me", "L31", [STX - 9.4, STY + 1.6, 0.6], 90, expr="neutral", arms=[75, 75])
go("me", "L31+0.9", [STX - 7.2, STY + 1.6, 0.2])
put("wes", "L31", [STX - 9.4, STY - 1.4, 0.6], 90, expr="wide")
shot("L31", A((STX - 8.4, STY + 1.6, 1.6), 90, 5.4, off=-25, lens=32, push=0.1), name="dawnbox")
shot("L31.1+0.3", A((LANE + 1.2, CURB_CAR[1], 1.0), 90, 5.5, off=36, lens=34, push=0.12), name="loadcar")
cue("L31.1+0.3", "mbox", v=0.0)
only("L32", ["wes", "me"])
put("wes", "L32", [STX - 6.6, STY + 0.0, 0.2], 90, expr="smirk", arms=[0, 0])
put("me", "L32", [STX - 4.8, STY + 3.4, 0], 270, expr="soft", arms=[0, 0])
shot("L32", A((STX - 6.6, STY + 0.0, 1.5), 90, 3.8, off=-26, lens=36, push=0.12), name="itwontlet")
shot("L32.1+0.25", A((STX - 6.6, STY + 0.0, 1.7), 90, 4.4, off=-8, lens=34, push=0.1), name="shut")
# the drop
only("P01", [])
shot("P01", mv([0.8, -1.5, 1.7], [0.0, 0.0, 0.58], 36, [0.55, -1.0, 1.5], [0.0, 0.0, 0.58], 36), name="dropwater")
plink("P01+0.05", 0)
look("P01", "day")
meter("L32", bar=1.0, red=1.0, dur=0.3)
# L33 -- I'm letting you go
only("L33", ["me", "wes"])
meter("L33", bar=1.0, red=1.0)
put("me", "L33", [STX - 5.5, STY + 1.0, 0], 90, expr="soft", arms=[0, 0])
put("wes", "L33", [STX - 4.2, STY + 1.0, 0], 270, expr="wide", arms=[0, 0])
shot("L33", A((STX - 5.5, STY + 1.0, 1.4), 90, 3.2, off=55, lens=34, push=0.12), name="letgo1")
beat("wes", "L33.1+0.25", expr="smirk")
shot("L33.1+0.25", A((STX - 4.2, STY + 1.0, 1.4), 270, 3.2, off=-55, lens=34, push=0.12), name="wesface2")
beat("me", "L33.2", arms=[0, 80], expr="soft")
cue("L33.2", "keys", v=1.0)
cue("L33.2+0.8", "keys", v=0.0)
shot("L33.2", A((STX - 4.85, STY + 1.0, 1.3), 90, 5.0, off=60, lens=30, push=0.1), name="keys")
# L34 -- the car does not stop
only("L34", ["wes"])
cue("L34", "car", x=LANE, y=CURB_CAR[1], yaw=0.0)
put("wes", "L34", [CURB_CAR[0] + 0.45, CURB_CAR[1] + 0.35, 0], 0, expr="grin")
sit("wes", "L34", True, CARZ)
ride("L34")
cue("L33.2+0.9", "car", x=LANE, y=-5.0, dur=0.6)
cue("L34", "car", x=LANE, y=-16.0, dur=0.65)
cue("L34.0+0.6", "car", x=LANE, y=-28.0, dur=0.5)
shot("L34", A((LANE, -2.0, 0.9), 0, 8.0, off=170, lens=32, push=0.1), name="toward")
meter("L34+0.5", bar=1.0, red=1.0)
shot("L34.0+0.6", A((LANE, STOP_CAR[1] - 3.0, 0.9), 0, 4.5, off=170, lens=34, push=0.1, dz=0.3), name="pastsign")
meter("L34.2", bar=1.25, red=0.0, dur=0.7)
shot("L34.2", A((MTX, MTY, 3.0), 0, 5.0, off=0, lens=34, push=0.1), name="meterpast")
# L35 -- two blocks, then past the town line
cue("L35", "car", x=LANE, y=-60.0, dur=0.8)
cue("L35.1", "car", x=LANE, y=-130.0, dur=1.1)
meter("L35", bar=1.25, red=0.0)
meter("L35.2+0.2", digits=1.0, num=3.0)
meter("L35.2+0.45", num=9.0, dur=0.25)
meter("L35.2+0.7", num=14.0, dur=0.25)
shot("L35", mv([G.ST[0] - 6.0, G.LINE_Y + 12.0, 2.0], [G.ST[0] - 3.5, G.LINE_Y, 2.0], 36, [G.ST[0] - 5.5, G.LINE_Y + 6.0, 2.0], [G.ST[0] - 3.5, G.LINE_Y, 2.0], 36), name="townline")
ride("L35.2", 0.0)
only("L35.2", ["me"])
put("me", "L35.2", [STX - 4.6, STY - 1.0, 0], 180, expr="wide")
shot("L35.2", A((STX - 4.6, STY - 1.0, 1.4), 180, 4.0, off=-28, lens=36, push=0.12), name="watching")

# ============================================================================================ L36 to L42 (the warm turn)
meter("L36", num=60.0, dur=1.0)
cue("L36", "mphone", v=1.0, lit=0.0)
beat("me", "L36", arms=[0, 65])
cue("L36+0.5", "mphone", v=1.0, lit=1.0)
shot("L36", mv([STX - 1.8, STY + 1.6, 1.6], [STX - 4.85, STY - 0.75, 1.2], 30, [STX - 2.1, STY + 1.2, 1.6], [STX - 4.85, STY - 0.75, 1.2], 30), name="phone")
look("L37", "sunrise")
meter("L37", num=120.0, dur=2.0)
shot("L37", mv([HWX - 0.3, HWY + 3.3, 1.45], [HWX - 0.3, HWY - 30, 1.4], 34, [HWX - 0.3, HWY + 3.3, 1.45], [HWX - 0.3, HWY - 30, 1.6], 38), name="highway")
look("L37.1", "day")
only("L37.1", ["me"])
beat("me", "L37.1", arms=[0, 0], expr="laugh")
cue("L37.1", "mphone", v=0.0)
shot("L37.1", A((STX - 4.6, STY - 1.0, 1.55), 180, 3.2, off=-28, lens=38, push=0.14), name="laughing")
# L38 -- the flash back: he was watching me wish
look("L38", "dusk")
only("L38", ["wes"])
put("wes", "L38", [SQX - 1.5, SQY + 10.6, 0], 15, expr="soft", arms=[0, 0], head=[-20, 0])
shot("L38", mv([SQX + 0.9, SQY + 5.6, 1.1], [SQX - 1.5, SQY + 10.6, 1.6], 36, [SQX + 0.4, SQY + 6.4, 1.2], [SQX - 1.5, SQY + 10.6, 1.6], 36), name="awning")
look("L38.2", "day")
only("L38.2", ["wes"])
sit("wes", "L38.2", True, CARZ)
put("wes", "L38.2", [LANE + 0.45, -20.0 + 0.35, 0], 0, expr="smirk")
cue("L38.2", "car", x=LANE, y=-20.0, yaw=0.0)
ride("L38.2")
shot("L38.2", A((LANE + 0.45, -19.7, 1.3), 0, 3.4, off=8, lens=34, push=0.1), name="mirror")
ride("L38.3", 0.0)
sit("wes", "L38.3", False)
only("L38.3", ["me"])
put("me", "L38.3", [STX - 4.6, STY - 1.0, 0], 180, expr="wide", arms=[0, 40])
shot("L38.3", A((STX - 4.6, STY - 1.0, 1.55), 180, 3.0, off=30, lens=38, push=0.12), name="mestunned")
# L39
only("L39", ["wes", "me"])
put("wes", "L39", [STEP[0], STEP[1] + 0.5, 0.4], 90, expr="sad-smile")
sit("wes", "L39", True, 0.47)
put("me", "L39", [STEP[0], STEP[1] - 0.5, 0.4], 90, expr="soft")
sit("me", "L39", True, 0.47)
shot("L39", A((STEP[0] + 0.3, STEP[1], 1.3), 90, 5.0, off=-8, lens=32, push=0.1), name="porchpair2")
sit("wes", "L39.1-0.02", False)
sit("me", "L39.1-0.02", False)
only("L39.1", ["me"])
put("me", "L39.1", [CURB_CAR[0] - 0.4, CURB_CAR[1] - 0.2, 0.0], 90, expr="soft")
sit("me", "L39.1", True, 0.2)
shot("L39.1", A((CURB_CAR[0] - 0.4, CURB_CAR[1] - 0.2, 0.9), 90, 4.4, off=-30, lens=34, push=0.12), name="curb")
# L40, L41, L42
sit("me", "L40-0.02", False)
only("L40", ["wes", "mom"])
put("wes", "L40", [STX - 7.4, STY + 0.2, 0.4], 90, expr="grin", arms=[75, 75], keep_yaw=True)
cue("L40", "wbox", v=1.0)
put("mom", "L40", [STX - 9.5, STY + 0.2, 0.6], 90, expr="soft", arms=[0, 0])
shot("L40", A((STX - 7.4, STY + 0.2, 1.75), 90, 4.4, off=-48, lens=36, push=0.1, tz=2.1), name="sunday")
beat("mom", "L40.1", arms=[75, 75])
beat("wes", "L40.1", arms=[75, 75], expr="grin")
go("wes", "L40.1+0.1", [STX - 8.4, STY + 0.2, 0.6])
cue("L40.1", "wbox", v=0.0)
beat("wes", "L40.1+0.7", arms=[75, 75], expr="grin")
shot("L40.1", A((STX - 8.9, STY + 0.2, 1.95), 90, 5.2, off=-50, lens=30, push=0.1), name="hug")
meter("L40.1+0.2", num=600.0, dur=0.6)
shot("L41", A((MTX, MTY, 3.0), 0, 4.8, off=0, lens=34, push=0.1), name="miles")
only("L41.1", ["wes", "me"])
put("me", "L41.1", [STEP[0], STEP[1] - 0.5, 0.4], 90, expr="laugh")
put("wes", "L41.1", [STEP[0], STEP[1] + 0.5, 0.4], 90, expr="laugh")
sit("me", "L41.1", True, 0.47)
sit("wes", "L41.1", True, 0.47)
beat("wes", "L41.1+0.6", arms=[0, 40])
shot("L41.1", A((STEP[0] + 0.3, STEP[1], 1.35), 90, 5.0, off=-12, lens=32, push=0.1), name="shoving")
# L42 -- the impression, then the coin back into the well (and around again)
look("L42", "day")
sit("me", "L42-0.02", False)
sit("wes", "L42-0.02", False)
only("L42", ["wes", "me"])
put("wes", "L42", [STX - 5.4, STY - 1.0, 0], 90, expr="shut", head=[0, 0])
put("me", "L42", [STX - 5.4, STY + 1.6, 0], 270, expr="laugh", arms=[0, 100])
shot("L42", A((STX - 5.4, STY - 1.0, 1.55), 90, 3.0, off=-30, lens=38, push=0.12), name="impression")
put("wes", "L42.1", [STX - 5.4, STY - 0.65, 0], 180, expr="shut", head=[0, 0])
put("me", "L42.1", [STX - 5.4, STY + 0.75, 0], 0, expr="laugh", arms=[0, 100])
shot("L42.1", A((STX - 5.4, STY + 0.05, 1.3), 90, 5.0, off=0, lens=32, push=0.1), name="laughhands")
only("L42.2", [])
coin("L42.2", att=0, x=0.05, y=0.0, z=2.3, spin=0)
coin("L42.2+0.01", z=0.64, spin=900, dur=0.62)
plink("L42.2+0.66")
coin("L42.2+0.72", z=-50.0)
shot("L42.2", COINCAM, name="loopcoin")

# ------------------------------------------------------------------------------------------------ finish
cue(0, "season", v=0)
cue(0, "posters", n=3.0)
cue(0, "clock", h=10.0)
cue(0, "wdoor", a=0.0)
cue(0, "car", x=CURB_CAR[0], y=CURB_CAR[1], yaw=0.0)
cue(0, "bus", x=HBX - 40.0, y=HBY, yaw=180.0)
cue(0, "ride", v=0.0)
cue(0, "wbox", v=0.0)
cue(0, "keys", v=0.0)
cue(0, "mbox", v=0.0)
cue(0, "duffel", v=0)
cue(0, "wphone", v=0.0, lit=1.0)
cue(0, "mphone", v=0.0, lit=1.0)
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
    {"at": "L01.3", "kind": "thud", "db": -6},
    {"at": "L14.1", "kind": "creak", "db": -20, "dur": 0.8},
    {"at": "L27.1+0.5", "kind": "click", "db": -14},
    {"at": "L36+0.5", "kind": "click", "db": -12},
    {"at": "L35.2+0.2", "kind": "hit", "db": -8},
]
music = {
    "root": 50, "mode": "major", "bpm": 104, "seed": 101,
    "sections": [
        {"at": 0, "voices": ["piano", "pad"], "energy": 0.4, "root": 50, "mode": "major"},
        {"at": "L08", "voices": ["piano", "pulse", "pad"], "energy": 0.45, "root": 50, "mode": "minor"},
        {"at": "L18", "voices": ["piano", "pad"], "energy": 0.3, "root": 50, "mode": "minor"},
        {"at": "L25", "voices": ["drone", "pad"], "energy": 0.35, "root": 43, "mode": "minor"},
        {"at": "L31", "voices": ["piano", "pad"], "energy": 0.4, "root": 50, "mode": "major"},
        {"at": "L33", "voices": ["pulse", "pad", "piano"], "energy": 0.65, "root": 50, "mode": "major"},
        {"at": "L37", "voices": ["piano", "pad", "pulse"], "energy": 0.6, "root": 50, "mode": "major"},
    ],
}
sound = {
    "floor": "stone", "steps_db": -26,
    "ambience": [{"kind": "wind", "from": 0, "to": "end", "lufs": -44},
                 {"kind": "crickets", "from": "L25", "to": "L31", "lufs": -44}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L30.1")], "twist": remap("L30"),
          "emph": [remap(x) for x in ["L01.3", "L03.0", "L10.2", "L11.1", "L14.0", "L24.0", "L30.1", "L33.2", "L38.3"]],
          "sway": [names[n] for n in ("halt", "keyturn", "rollback", "porchscared", "stride", "feet")],
          "hold": [names[n] for n in ("bigmeter", "meterpast", "miles")]}
story = {
    "slug": "ep101-well-wish",
    "title": "The Well Heard EVERY Word 🪣",
    "made_for_kids": False,
    "premise": ("Our town's wishing well grants every wish word for word. Three years ago I wished I'd never lose my "
                "big brother Wes, and now he cannot get one block away from me, even as he lands his dream job across "
                "the country."),
    "twist": ("You only lose what you don't mean to let go of: I let Wes go on purpose, the leash lets him pass the "
              "town line, and he reveals he heard my wish three years ago and stayed so I wouldn't feel bad."),
    "world": ("A sunny brick town square with a round pale stone well, a hilly street of painted houses with a "
              "brick-red corner house, a green town-line post and a rule meter tag that fills toward a red notch."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffcf4a",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#cfe6f5", "fog_density": 0.003, "fog_start": 40.0, "sky": "#8fd3ff",
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
    "set_moves": [names[n] for n in ("coin1", "coindown", "coinflip", "goldrings", "pullaway", "waving", "rollback",
                                      "parked", "halt", "uturn", "toward", "pastsign", "clock",
                                      "spit", "palm", "loopcoin", "dropwater", "stillwater", "ringsback", "lightline",
                                      "gap", "summer", "posters", "meterpast", "townline")
                  if n in names],
    "clip_ok": [],
    "asr_forgive": ["kemp", "hobb", "wes", "it's", "missus", "mister"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
print({k: v for k, v in names.items()})
