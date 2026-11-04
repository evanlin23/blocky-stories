"""Writes ../story.json for ep105 "backward neighbor" (script.md, 2026-11-04). Run: python stories/ep105-backward-neighbor/generator/make_story.py

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
REV = 9
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
# the 0.6 s music drop before L44
idx = next(i for i, l in enumerate(lines) if l["id"] == "L44")
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


def C(tx, ty, tz, d, lens, ang=0.0, push=0.14, dz=0.0, dx=0.0, tz2=None):
    """Camera d metres from the target at angle ang (degrees round the target, 0 = from -y), pushing in by `push`."""
    a = ang * D2R
    sx, sy = math.sin(a), -math.cos(a)
    p0 = [tx + sx * d + dx, ty + sy * d, tz + dz]
    d2 = d * (1 - push)
    p1 = [tx + sx * d2 + dx * 0.7, ty + sy * d2, tz + dz]
    return mv(p0, [tx, ty, tz], lens, p1, [tx, ty, tz if tz2 is None else tz2], lens)


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


VS = "#e8bd98"       # Vern's skin, the same at every age
CARD = "#8a5a3c"     # Vern's brown cardigan
cast = {
    "me": person("#f0c4a0", "#4fc060", "#3a4a6a", "#f4f4f2", hair="cap", hair_c="#1c1410", brow_w=1.9),
    "me2": person("#f0c4a0", "#4fc060", "#3a4a6a", "#f4f4f2", hair="cap", hair_c="#8a8a92", brow_w=1.9),
    "me3": person("#f0c4a0", "#6a9a8a", "#4a4a5a", "#6a5a4a", hair="cap", hair_c="#74747e", pattern="knit",
                  pattern_c="#587a6c", extras=["glasses"], extra_c="#d8452f", glasses_c="#d8452f", brow_w=1.9),
    "vern0": person(VS, CARD, "#6b5a48", "#4a3626", hair="cap", hair_c="#d2d4dc", pattern="knit", pattern_c="#6e4630",
                    extras=["glasses"], extra_c="#3a3a3e", brow_w=1.6),
    "vern0s": person(VS, "#34406a", "#34406a", "#2a2a32", hair="cap", hair_c="#d2d4dc", collar="#f4f4f4",
                     extras=["glasses", "tie"], extra_c="#e8553f", brow_w=1.6),
    "vern1": person(VS, CARD, "#6b5a48", "#4a3626", hair="cap", hair_c="#b0b0b8", pattern="knit", pattern_c="#6e4630",
                    brow_w=1.6),
    "vern2": person(VS, CARD, "#6b5a48", "#4a3626", hair="cap", hair_c="#7a5a44", pattern="knit", pattern_c="#6e4630",
                    brow_w=1.6),
    "vern3": person(VS, CARD, "#6b5a48", "#4a3626", hair="spiky", hair_c="#6a4228", pattern="knit", pattern_c="#6e4630",
                    brow_w=1.6),
    "vern4": person(VS, "#5a8ad0", "#3a4a6a", "#f4f4f2", hair="spiky", hair_c="#6a4228", collar="#f4f4f4", brow_w=1.6,
                    extras=["coat"], zip_c="#3a5a90"),
    "nora": person("#f0c8a0", "#ffd23f", "#ffd23f", "#f4f4f2", hair="mop", hair_c="#e8553f", eyes="lashes", brow_w=1.9,
                   width=0.96),
    "nora2": person("#f0c8a0", "#e8a060", "#6a5a6a", "#6a5a4a", hair="bun", hair_c="#bfa6a8", eyes="lashes", brow_w=1.9,
                    width=0.96, pattern="knit", pattern_c="#d08a50"),
    "m1": person("#b98456", "#ff9a30", "#3a3a48", "#2a2a2a", hair="buzz", hair_c="#1a1410", sleeves="short"),
    "m2": person("#f0c8a0", "#3aa0a0", "#3a3a48", "#2a2a2a", hair="cap", hair_c="#6a4a2a", hat="ballcap", hat_c="#2f6fb0",
                 sleeves="short"),
    "mail": person("#8a5a3a", "#4a7ac0", "#3a4a6a", "#2a2a32", hair="bun", hair_c="#150f0c", eyes="lashes", hat="ballcap",
                   hat_c="#4a7ac0", extras=["backpack"], extra_c="#e8553f"),
    "g1": person("#d3a07a", "#b070e0", "#b070e0", "#f4f4f2", hair="long", hair_c="#2a2a2a", eyes="lashes"),
    "g2": person("#e8b890", "#d8c8a8", "#5a6a7a", "#6a4a32", hair="spiky", hair_c="#a05a2a"),
    "g3": person("#8a5a3a", "#ff6a8a", "#ff6a8a", "#f4f4f2", hair="bun", hair_c="#150f0c", eyes="lashes"),
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


def shot(at, camera, name=None):
    SH.append((at, camera, name))


def look(at, id_, dur=0):
    cue(at, "look", id=id_, dur=dur)


def season(at, id_):
    cue(at, "season", id=id_)


def count(at, n):
    cue(at, "count", n=float(n))


def show(at, obj, on=True):
    cue(at, "vis", obj=obj, on=on)


def sit(who, at, chair="chairA", z=0.56, on=True, rock=False):
    cue(at, "sit", who=who, on=on, z=z, chair=chair)
    if rock:
        cue(at, "rock", who=who, on=True)


def off(at, dt):
    """A time reference moved by dt seconds (a ref may carry one offset only)."""
    m = re.match(r"^(.*?)([+-][0-9.]+)?$", at)
    base, o = m.group(1), float(m.group(2) or 0)
    return f"{base}{o + dt:+.2f}"


def flip(at, n=None):
    """The porch calendar page flips: down over the old number, up on the new one."""
    cue(at, "flip", v=0.0, dur=0.25)
    if n is not None:
        cue(off(at, 0.28), "count", n=float(n))
    cue(off(at, 0.3), "flip", v=1.0, dur=0.3)


# ---------------------------------------------------------------------------------------------- places
VX, VY = G.VERN_DOOR
HUGM, HUGV = (-5.5, -1.8), (-4.2, -1.8)
CALX, CALY = G.CAL
AX, AY = G.CHAIR_A
BX, BY = G.CHAIR_B
RX, RY = G.ROOM
WX, WY = G.WED
BBX, BBY = G.BARB
GX, GY = G.GAR
DX, DY = G.DRIVE
MEET_V = (DX - 2.1, -4.5)       # young Vern, on his new lawn beside the truck
FACE = 1.55


def cu(pos, yaw, d=3.4, lens=50, side=0.0, z=FACE, **kw):
    return C(pos[0], pos[1], z, d, lens, ang=yaw + side, **kw)


def cal_close(d=3.4, lens=28, z=2.0, **kw):
    return C(CALX + 0.1, CALY - 0.2, z, d, lens, **kw)


# ===== 01 the hook (L01 to L04)
look(0, "day")
count(0, 10950)
show(0, "movebox")
show(0, "cane_vern0")
show(0, "cal", False)
put("vern0", 0, HUGV, -45, expr="crying", arms=[75, 75])
put("me", 0, HUGM, 55, expr="worried", arms=[50, 50])
shot(0, cu(HUGV, -45, 3.7, 50, tz2=FACE, dx=0.0), "hook")
shot("L01.1", cu(HUGM, 55, 4.6, 46), "mehug")
shot("L01.2", C(-4.9, -2.8, 0.7, 5.0, 36, ang=-10, dz=0.5), "boxfeet")
shot("L01.3", C(-4.9, -1.8, 1.5, 6.2, 36, ang=-8), "hugwide")
# L02: Vern steps back and wipes his glasses; the movers freeze with a couch
beat("vern0", "L02-0.05", arms=[75, 75])
go("vern0", "L02+0.4", [-3.7, -1.8])
beat("vern0", "L02+0.45", arms=[0, 110], expr="crying", yaw=-35)
beat("me", "L02", arms=[0, 0], expr="polite", yaw=45)
show("L02", "carry_me")
shot("L02.1", cu(HUGM, 50, 3.6, 46, side=10), "mebox")
put("m1", "L02.2", [-9.2, -0.6], 0, expr="wide", arms=[40, 40])
put("m2", "L02.2", [-7.4, -0.6], 0, expr="wide", arms=[40, 40])
show("L02.2", "couch")
shot("L02.2", C(-8.3, -0.6, 1.2, 6.6, 34, ang=5), "movers")
beat("vern0", "L02.3", arms=[0, 0], expr="crying")
shot("L02.3", cu((-3.7, -1.8), -35, 3.3, 52, side=10), "cried")
# L03
only("L03", ["vern0", "me"])
show("L03", "couch", False)
beat("vern0", "L03", expr="sad-smile", yaw=-30)
shot("L03", cu((-3.7, -1.8), -30, 3.3, 52, side=-5), "thank")
beat("me", "L03.2", expr="wide", yaw=40)
shot("L03.2", cu(HUGM, 45, 3.3, 52), "stunned")
# L04: a minute, a watch, a pat, his mailbox, the walk home
beat("me", "L04", expr="worried", arms=[100, 0], head=[0, 0])
shot("L04", cu(HUGM, 40, 4.0, 46, side=-10), "watch")
beat("me", "L04.1", arms=[0, 0], yaw=55)
beat("vern0", "L04.1", arms=[0, 70], yaw=-70)
go("vern0", "L04.1+0.5", [-1.0, -1.8], arms=[0, 0])
shot("L04.2", C(G.MBOX_VERN[0], G.MBOX_VERN[1], 1.25, 2.6, 46, ang=-20), "mailbox")
go("vern0", "L04.3", [VX - 2.0, 3.6])
shot("L04.3", C(0.5, -1.0, 1.4, 9.0, 28, ang=-5, push=0.18), "walkhome")
# ===== 02 the rule at work (L05 to L12)
only("L05", ["vern0", "me"])
show("L05", "cane_vern0", False)
show("L05", "cal")
show("L05", "carry_me", False)
shot("L05", cal_close(3.6, 28), "calendar")
put("vern0", "L05.1", [AX, AY - 0.15], 0, expr="smile")
sit("vern0", "L05.1", "chairA", rock=True)
put("me", "L05.1", [-4.4, -2.4], 0, expr="soft", arms=[40, 40])
shot("L05.1", C(AX, AY, 1.3, 5.2, 40, ang=-12), "rocker")
# L06: dusk and dawn at his door
look("L06", "dusk")
only("L06", ["vern0"])
sit("vern0", "L06", on=False)
put("vern0", "L06", [VX - 0.9, 4.4], 0, expr="soft")
shot("L06", C(VX - 0.9, 4.4, 1.5, 4.6, 38, ang=0), "dusk")
look("L06.1", "morning")
shot("L06.1", C(VX - 0.9, 4.4, 1.5, 4.0, 38, ang=0), "dawn")
# L07: he taps his temple
look("L07", "day")
only("L07", ["vern0", "me"])
put("vern0", "L07", [0.9, -1.2], -80, expr="smirk", arms=[0, 150])
put("me", "L07", [-0.9, -1.2], 80, expr="worried")
shot("L07", cu((0.9, -1.2), -50, 3.3, 50), "tap")
shot("L07.1", C(0, -1.2, 1.4, 6.5, 34, ang=0), "fence2")
# L08: flag up before the mail
only("L08", [])
cue("L08", "flag", v=0.0)
cue("L08.1", "flag", v=1.0, dur=0.6)
shot("L08", C(G.MBOX_VERN[0], G.MBOX_VERN[1], 1.3, 2.8, 42, ang=-15), "flag")
put("mail", "L08.2", [9.0, -6.4], -90, expr="smile")
go("mail", "L08.2+0.9", [4.6, -6.0])
shot("L08.2", C(5.4, -5.8, 1.4, 6.0, 36, ang=15), "mail")
# L09: he waves before I open the door
only("L09", ["vern0"])
put("vern0", "L09", [VX - 1.2, 4.4], 0, expr="grin", arms=[0, 150])
shot("L09", C(VX - 1.2, 4.4, 1.5, 5.0, 40, ang=-3), "wave1")
only("L09.1", ["vern0", "me"])
cue("L09.1", "mydoor", a=0.0)
cue("L09.1+0.2", "mydoor", a=100.0, dur=0.5)
put("me", "L09.1", [-5.6, 4.9], 0, expr="neutral")
go("me", "L09.1+0.7", [-5.6, 4.1])
acting["me"][-1]["sfx"] = "door"
shot("L09.1", C(-6.0, 5.2, 1.3, 5.2, 36, ang=0), "opendoor")
go("me", "L09.2", [-6.0, 3.2])
beat("me", "L09.2", yaw=60, arms=[0, 120], expr="smile")
beat("me", "L09.3", yaw=0, arms=[0, 0], expr="worried")
shot("L09.3", cu((-6.0, 3.2), 0, 3.4, 50), "confused")
# L10: the calendar flips backward every morning
only("L10", [])
cue("L10", "mydoor", a=0.0)
flip("L10", 10950)
shot("L10", cal_close(3.9, 28), "flip")
shot("L10.1", cal_close(2.4, 28, 1.95), "flipclose")
shot("L10.2", C(CALX + 1.5, CALY - 3.0, 1.8, 3.6, 34, ang=35), "flipside")
# L11: ten thousand nine hundred and fifty
put("me", "L11", [CALX, 3.9], 180, expr="wide")
shot("L11", C(CALX, 3.9, 1.6, 4.2, 34, ang=150), "reading")
shot("L11.2", cal_close(2.3, 28, 1.95), "number")
# L12: counting down
only("L12", [])
flip("L12", 10949)
shot("L12", cal_close(3.0, 28), "tick")
# ===== 03 the first night and morning (L13 to L15)
look("L13", "night")
count("L13", 10948)
put("vern0", "L13", [VX, 4.1], 0, expr="soft", arms=[40, 40])
put("m1", "L13", [VX + 1.2, 3.3], 0, expr="neutral", arms=[40, 40])
show("L13", "carry_vern0")
show("L13", "carry_m1")
cue("L13", "truck", y=0.0, vis=1.0)
cue("L13", "truckdoor", a=100.0)
go("vern0", "L13+1.6", [DX - 0.9, 5.3])
go("m1", "L13+1.9", [DX + 0.6, 6.2])
shot("L13", mv([-3.0, 1.8, 1.8], [8.5, 4.6, 1.2], 30, [-2.2, 1.9, 1.8], [8.6, 4.6, 1.2], 30), "nightwin")
only("L13.1", ["vern0", "m1"])
put("me", "L13.1", [-9.4, 7.3], 0, expr="worried")
show("L13.1", "tb_me")
shot("L13.1", C(-9.4, 7.3, 1.55, 4.2, 50, ang=0, push=0.1), "toothbrush")
show("L13.2", "tb_me", False)
only("L13.2", ["m2", "vern0"])
put("m2", "L13.2", [VX + 2.6, 4.2], 90, expr="neutral", arms=[40, 40])
show("L13.2", "carry_m2")
put("vern0", "L13.2", [VX + 3.4, 5.0], 90, expr="soft", arms=[40, 40])
go("vern0", "L13.2+0.9", [DX - 1.8, 5.3])
go("m2", "L13.2+0.9", [DX - 2.4, 5.4])
shot("L13.2", C(VX + 4.4, 4.0, 1.4, 5.0, 38, ang=-20), "carrying")
cue("L13.3", "truckdoor", a=100.0)
cue("L13.3+0.2", "truckdoor", a=0.0, dur=0.8)
shot("L13.3", C(DX, 5.4, 1.3, 6.6, 34, ang=-35), "truckdoors")
# L14: morning, every box back inside
look("L14", "day")
only("L14", [])
cue("L14", "truck", y=0.0, vis=0.0)
count("L14", 10947)
show("L14", "carry_vern0", False)
show("L14", "carry_m1", False)
show("L14", "carry_m2", False)
shot("L14", mv([RX, RY - 9.5, 1.6], [RX, RY, 1.7], 32, [RX, RY - 8.0, 1.6], [RX, RY, 1.7], 32), "livingwin")
shot("L14.1", mv([RX - 0.8, RY - 4.8, 2.0], [RX - 1.15, RY + 3.3, 2.35], 52, [RX - 0.7, RY - 4.4, 2.0], [RX - 1.15, RY + 3.3, 2.35], 52), "framewin")
put("vern0", "L14.2", [VX - 1.2, 4.4], 0, expr="smile", arms=[0, 150])
shot("L14.2", C(VX - 1.2, 4.4, 1.5, 4.6, 40, ang=-3), "coffeewave")
put("me", "L14.3", [-9.4, 6.4], 0, expr="wide")
shot("L14.3", C(-9.4, 6.4, 1.6, 3.4, 54, ang=0), "faceglass")
# L15: the truck is gone
only("L15", ["me"])
put("me", "L15", [-4.8, -1.2], 90, expr="wide")
shot("L15", cu((-4.8, -1.2), 60, 3.6, 46), "staring")
# ===== 04 the fence, Nora, the years (L16 to L24)
count("L16", 10940)
only("L16", ["me"])
put("me", "L16", [-0.8, 0.4], 130, expr="worried")
shot("L16", mv([0.7, -5.2, 1.0], [0.0, 3.0, 0.6], 30, [0.4, -4.4, 1.0], [0.0, 3.0, 0.6], 30), "pickets")
show("L16.2", "lemon")
put("vern0", "L16.2", [0.95, -1.6], -70, expr="grin", arms=[0, 70])
shot("L16.2", C(0, -1.6, 1.25, 2.4, 46, ang=-15), "lemonade")
only("L17", [])
shot("L17", C(0, 1.5, 0.8, 3.4, 34, ang=-50), "fine2")
# L18: a storm knocks it flat, I stand it up again
show("L18.1", "lemon", False)
look("L18.1", "storm")
cue("L18.1", "maple", s=1.0, bend=0.0)
cue("L18.2", "fence", v=0.0)
cue("L18.2+0.1", "fence", v=1.0, dur=0.7)
shot("L18.1", C(0, -1.0, 1.4, 8.0, 28, ang=-12), "storm")
look("L18.3", "day")
show("L18.3", "hammer")
put("me", "L18.3", [-1.3, -1.4], 70, expr="smile", arms=[60, 60])
cue("L18.3", "fence", v=1.0)
cue("L18.3+0.1", "fence", v=0.0, dur=1.1)
shot("L18.3", cu((-1.3, -1.4), 55, 4.2, 40, side=15), "fixing")
show("L19", "hammer", False)
show("L20", "porchbox", False)
# L19: Nora?
count("L19", 10930)
only("L19", ["vern0", "me"])
put("vern0", "L19", [0.95, -1.2], -75, expr="smirk", arms=[0, 0])
put("me", "L19", [-0.95, -1.2], 75, expr="worried")
shot("L19", cu((0.95, -1.2), -45, 3.3, 52), "asknora")
shot("L19.2", cu((-0.95, -1.2), 45, 3.4, 50), "shrug")
beat("me", "L19.2", arms=[0, 0], expr="wide")
only("L19.4", ["me"])
show("L19.4", "porchbox")
put("me", "L19.4", [-6.0, 4.6], 0, expr="soft")
shot("L19.4", C(-6.0, 4.6, 1.3, 5.8, 32, ang=0), "alone")
# L20: the wedding
only("L20", ["nora", "me"])
season("L20", "summer")
count("L20", 10220)
show("L20", "movebox", False)
put("nora", "L20", [WX + 0.55, WY + 0.9], 0, expr="laugh", arms=[15, 15])
put("me", "L20", [WX - 0.55, WY + 0.9], 0, expr="laugh", arms=[15, 15])
shot("L20", C(WX, WY + 0.9, 1.5, 6.4, 38, ang=0), "wedding")
only("L20.1", ["nora", "me", "g1", "g2", "g3"])
put("g1", "L20.1", [WX - 2.4, WY - 1.0], 0, expr="laugh", arms=[110, 110])
put("g2", "L20.1", [WX + 2.4, WY - 1.0], 0, expr="laugh", arms=[100, 100])
put("g3", "L20.1", [WX + 3.4, WY - 2.2], 0, expr="grin", arms=[80, 80])
beat("nora", "L20.1", arms=[60, 60], expr="laugh")
shot("L20.1", C(WX, WY + 0.9, 1.6, 6.2, 40, ang=-6), "bouquet")
only("L20.2", ["nora"])
beat("nora", "L20.2", arms=[0, 0], expr="laugh")
shot("L20.2", cu((WX + 0.55, WY + 0.9), 0, 3.3, 52), "noracu")
# L21: Vern cries through the vows
only("L21", ["vern0s"])
put("vern0s", "L21", [WX - 1.8, WY - 0.6], 20, expr="crying")
shot("L21", cu((WX - 1.8, WY - 0.6), 20, 3.4, 50), "vernsob")
only("L21.2", ["me", "vern0s"])
put("me", "L21.2", [WX, WY + 0.9], 160, expr="soft", head=[-30, 0])
put("vern0s", "L21.2", [WX - 1.8, WY - 0.6], 0, expr="crying")
shot("L21.2", C(WX - 0.8, WY + 0.2, 1.5, 4.8, 40, ang=-20), "mouthing")
# L22: every year he got younger, I got older
season("L22", "autumn")
look("L22", "day")
count("L22", 9125)
only("L22", ["vern0"])
put("vern0", "L22", [3.0, -1.6], 0, expr="smile", arms=[60, 60], lean=10)
beat("vern0", "L22+0.5", lean=-6, arms=[80, 40])
shot("L22", cu((3.0, -1.6), 0, 4.4, 40), "rake")
season("L22.1", "winter")
look("L22.1", "snow")
only("L22.1", ["vern1"])
put("vern1", "L22.1", [3.0, -1.6], 0, expr="smile", arms=[60, 60], lean=10)
shot("L22.1", cu((3.0, -1.6), 0, 4.4, 40), "shovel")
season("L22.2", "spring")
look("L22.2", "day")
only("L22.2", ["vern2"])
put("vern2", "L22.2", [1.0, -2.6], 90, expr="grin")
go("vern2", "L22+2.2", [-2.4, -2.6])
shot("L22.2", C(0, -2.6, 1.5, 5.6, 38, ang=-20), "jog")
cue("L22.3", "maple", s=1.05, bend=0.0)
only("L22.3", ["me2"])
put("me2", "L22.3", [-0.9, -1.2], 70, expr="soft")
shot("L22.3", cu((-0.9, -1.2), 55, 3.4, 50), "gray")
season("L22.3+0.65", "summer")
cue("L22.3+0.65", "maple", s=1.35, bend=0.0)
shot("L22.3+0.65", mv([-2.0, -4.0, 0.8], [0.2, 4.6, 5.4], 26, [-1.4, -3.4, 0.9], [0.2, 4.6, 5.8], 26), "maple")
# L23: white to gray to brown
count("L23", 7300)
only("L23", ["vern0"])
put("vern0", "L23", [BBX, BBY + 0.9], 0, expr="smile", arms=[0, 60])
sit("vern0", "L23", z=0.62, chair="chairA")
shot("L23", C(BBX, BBY + 1.0, 1.55, 3.6, 46, ang=0), "barber")
sit("vern0", "L23.2", on=False)
only("L23.2", ["vern1"])
put("vern1", "L23.2", [BBX, BBY + 0.9], 0, expr="smile", arms=[0, 60])
sit("vern1", "L23.2", z=0.62, chair="chairA")
only("L23.3", ["vern2", "me2"])
sit("vern1", "L23.3", on=False)
put("vern2", "L23.3", [4.0, -2.2], -40, expr="laugh")
put("me2", "L23.3", [2.6, -2.2], 40, expr="laugh")
show("L23.3", "bbq")
shot("L23.3", C(3.4, -2.2, 1.5, 4.2, 44, ang=-10), "bbqlaugh")
# L24: the cane in the garage
only("L24", [])
show("L24", "bbq", False)
count("L24", 6200)
shot("L24", C(GX - 0.5, GY + 2.1, 0.95, 5.0, 40, ang=0, push=0.1), "cane")
only("L24.2", ["me2", "vern2"])
put("me2", "L24.2", [GX - 0.2, GY + 0.8], 0, expr="worried", arms=[70, 0])
put("vern2", "L24.2", [GX + 1.2, GY + 0.2], 0, expr="laugh", arms=[150, 150])
shot("L24.2", C(GX + 0.6, GY + 0.5, 1.5, 4.6, 42, ang=0), "puzzled")
# ===== 05 never yesterday, only tomorrow (L25 to L31)
count("L25", 5475)
only("L25", ["me2", "vern2"])
put("me2", "L25", [-0.9, -1.2], 70, expr="laugh", arms=[60, 0])
put("vern2", "L25", [0.9, -1.2], -70, expr="blank")
shot("L25", cu((-0.9, -1.2), 55, 3.6, 50), "plate")
shot("L25.1", cu((0.9, -1.2), -55, 3.4, 52), "polite")
shot("L25.2", C(0, -1.2, 1.5, 5.4, 36, ang=0), "polite2")
beat("vern2", "L26", expr="grin", arms=[90, 0], yaw=-110)
shot("L26", mv([1.4, -3.0, 1.5], [-3.0, 0.8, 0.7], 34, [0.8, -2.6, 1.4], [-3.0, 0.8, 0.7], 34), "tomatoes")
count("L27", 4200)
only("L27", ["vern2"])
put("vern2", "L27", [AX, AY - 0.15], 0, expr="smile")
sit("vern2", "L27", "chairA", rock=True)
shot("L27", C(AX, AY, 1.3, 5.0, 40, ang=-10), "watchplant")
sit("vern2", "L27.1", on=False)
put("vern2", "L27.1", [VX - 1.2, 4.4], 0, expr="smile", arms=[0, 150])
shot("L27.1", C(VX - 1.2, 4.4, 1.5, 4.8, 40, ang=-3), "wavefirst")
put("vern2", "L28", [AX, AY - 0.15], 0, expr="smile", arms=[0, 0])
sit("vern2", "L28", "chairA", rock=True)
shot("L28", C(AX, AY, 1.3, 4.6, 42, ang=-8), "humming")
shot("L28.2", cal_close(3.3, 28), "cal2")
only("L29", ["vern3"])
sit("vern2", "L29", on=False)
count("L29", 3650)
put("vern3", "L29", [VX - 1.2, 4.4], 0, expr="smile")
shot("L29", cu((VX - 1.2, 4.4), 0, 3.2, 52), "youngish")
cue("L29", "flip", v=0.0, dur=0.2)
cue("L29+0.25", "flip", v=1.0, dur=0.3)
# L30: running out
only("L30", ["vern3", "me2"])
count("L30", 1825)
put("vern3", "L30", [CALX + 1.4, 3.7], 0, expr="soft")
put("me2", "L30", [CALX - 0.2, 3.7], 0, expr="soft")
shot("L30", C(CALX + 0.6, 3.7, 1.4, 4.8, 36, ang=0), "steps")
shot("L30.2", cal_close(1.9, 28, 1.95), "tag")
# L31: faster
only("L31", [])
flip("L31", 1500)
shot("L31", cal_close(3.2, 28), "flip3")
flip("L31+0.9", 1300)
only("L31.2", ["me2"])
sit("vern3", "L31.2", on=False)
put("me2", "L31.2", [-6.0, 4.6], 0, expr="worried")
shot("L31.2", C(-6.0, 4.6, 1.4, 5.0, 38, ang=0), "watchme")
# ===== 06 zero (L32 to L34)
look("L32", "dusk")
count("L32", 900)
show("L32", "tallylamp")
show("L34", "tallylamp", False)
only("L32", ["vern3", "me2"])
show("L32", "chairs")
put("vern3", "L32", [AX, AY - 0.15], 0, expr="soft")
sit("vern3", "L32", "chairA", rock=True)
put("me2", "L32", [BX, BY - 0.15], 0, expr="worried", head=[-25, 0], lean=14)
sit("me2", "L32", "chairB", z=0.56)
shot("L32", C(AX + 0.8, AY, 1.2, 7.4, 34, ang=-10, push=0.06), "twochairs")
shot("L32.2", mv([AX - 0.8, AY - 1.6, 1.15], [AX - 0.46, AY, 0.83], 46, [AX - 0.6, AY - 1.3, 1.1], [AX - 0.46, AY, 0.83], 46), "tally")
shot("L32.3", cal_close(3.6, 28), "darkcal")
look("L33", "dusk")
beat("vern3", "L33", expr="smile", head=[18, 0])
shot("L33", cu((AX, AY), 8, 3.4, 52), "shake")
shot("L33.1", C(AX, AY, 1.3, 4.4, 40, ang=-15), "rocks")
look("L34", "day")
sit("me2", "L34", on=False)
sit("vern3", "L34", on=False)
only("L34", ["vern3"])
put("vern3", "L34", [VX - 1.2, 4.4], 0, expr="warm")
shot("L34", cu((VX - 1.2, 4.4), 0, 3.3, 52), "youllknow")
shot("L34.3", mv([G.CHAIR_B[0] + 0.5, 2.6, 2.4], [G.CHAIR_B[0] + 0.5, 4.6, 2.3], 55, [G.CHAIR_B[0] + 0.4, 2.9, 2.35], [G.CHAIR_B[0] + 0.5, 4.6, 2.3], 55), "chime")
# ===== 07 the photos come down (L35 to L43)
look("L35", "bluedusk")
count("L35", 600)
only("L35", [])
cue("L35", "photos", n=9.0)
shot("L35", mv([RX, RY - 9.0, 1.9], [RX, RY + 3.3, 1.9], 28, [RX, RY - 7.6, 1.9], [RX, RY + 3.3, 1.9], 28), "fullwall")
shot("L35.1", mv([RX + 1.4, RY - 5.0, 1.5], [RX + 1.15, RY + 3.3, 1.2], 48, [RX + 1.3, RY - 4.4, 1.5], [RX + 1.15, RY + 3.3, 1.2], 48), "fencephoto")
count("L36", 450)
shot("L36", C(RX + 2.3, RY + 3.3, 1.1, 3.3, 46, ang=0, dz=0.1), "bbqphoto")
cue("L36.1", "photos", n=8.0)
shot("L36.1", C(RX + 2.3, RY + 3.3, 1.1, 3.2, 46, ang=0, dz=0.1), "paleSquare")
put("vern3", "L36.2", [RX + 1.0, RY + 2.4], 180, expr="blank", arms=[150, 150])
shot("L36.2", C(RX + 1.0, RY + 2.4, 1.6, 3.8, 42, ang=170), "lifting")
cue("L37", "photos", n=8.0)
cue("L37+0.3", "photos", n=7.0)
count("L37", 300)
only("L37", [])
shot("L37", C(RX + 1.15, RY + 3.3, 1.3, 4.6, 40, ang=0), "fencegone")
cue("L37.1", "photos", n=6.0)
shot("L37.1", C(RX - 1.15, RY + 3.3, 2.35, 3.2, 46, ang=0), "weddinggone")
cue("L37.1+0.4", "photos", n=3.0)
cue("L37.1+0.4", "rboxes", n=4.0)
cue("L38", "photos", n=1.0)
cue("L38", "rboxes", n=6.0)
count("L38", 90)
shot("L38", mv([RX, RY - 1.5, 1.9], [RX, RY + 3.3, 1.9], 32, [RX, RY - 0.5, 1.9], [RX, RY + 3.3, 1.9], 32), "oneleft")
put("me2", "L38.2", [RX + 0.6, RY - 4.5], 180, expr="worried")
shot("L38.2", mv([RX, RY - 1.2, 1.6], [RX + 0.6, RY - 4.5, 1.5], 44, [RX + 0.1, RY - 1.8, 1.6], [RX + 0.6, RY - 4.5, 1.5], 44), "atwindow")
only("L39", [])
count("L39", 30)
shot("L39", C(RX + 0.1, RY + 3.3, 1.85, 6.2, 40, ang=0), "lastframe")
shot("L39.1", C(RX + 0.15, RY + 3.3, 1.95, 2.7, 40, ang=0, push=0.08), "youngears")
shot("L40", C(RX + 0.3, RY + 3.3, 1.97, 2.4, 40, ang=0, push=0.08), "oldman")
look("L40.1", "dayroom", 0.4)
show("L40.1", "rglass", False)
show("L41", "rglass")
only("L40.1", ["me3"])
put("me3", "L40.1", [RX + 0.6, RY - 4.5], 180, expr="scared")
shot("L40.1", mv([RX + 0.2, RY - 2.0, 1.6], [RX + 0.6, RY - 4.5, 1.5], 50, [RX + 0.3, RY - 2.4, 1.6], [RX + 0.6, RY - 4.5, 1.5], 50), "scaredwin")
# L41: last week he waved at me like a stranger
look("L41", "day")
count("L41", 7)
cue("L41", "photos", n=1.0)
only("L41", ["vern3"])
put("vern3", "L41", [VX - 1.2, 4.4], 0, expr="blank", arms=[0, 120])
shot("L41", cu((VX - 1.2, 4.4), 0, 4.8, 42, dx=0.0), "strangerwave")
beat("vern3", "L41.2", expr="polite", arms=[0, 0])
go("vern3", "L41.2+0.5", [VX, 6.3])
shot("L41.2", C(VX - 0.5, 4.4, 1.5, 5.0, 38, ang=-4), "turnsaway")
only("L41.4", ["vern3"])
put("vern3", "L41.4", [VX - 1.2, 4.4], 0, expr="polite", arms=[0, 60])
shot("L41.4", cu((VX - 1.2, 4.4), 0, 3.4, 50), "newneighbor")
# L42: trying to remember my name
count("L42", 3)
beat("vern3", "L42", expr="worried", head=[0, 0])
shot("L42", cu((VX - 1.2, 4.4), 0, 3.0, 52), "squint2")
put("vern3", "L42.2", [G.MBOX_VERN[0] + 0.7, -5.0], -80, expr="polite")
shot("L42.2", C(G.MBOX_VERN[0], G.MBOX_VERN[1], 1.4, 2.8, 46, ang=-20), "checkname")
only("L42.3", ["me3"])
put("me3", "L42.3", [-3.4, -5.0], 90, expr="worried")
shot("L42.3", cu((-3.4, -5.0), 55, 3.2, 52), "fall")
count("L43", 1)
only("L43", [])
shot("L43", cal_close(2.6, 28), "calone")
shot("L43.1", mv([RX, RY - 2.0, 1.8], [RX, RY + 3.3, 1.8], 32, [RX, RY - 1.2, 1.8], [RX, RY + 3.3, 1.8], 32), "barewall")
cue("L43.1", "photos", n=1.0)
cue("L44", "photos", n=0.0)
# the drop: the porch calendar, last page at 1
shot("P01", cal_close(2.8, 28), "dropcal")
# ===== 08 the twist (L44 to L53)
look("L44", "morning")
count("L44", 1)
cue("L44", "truck", y=-8.0, vis=1.0)
cue("L44", "truckdoor", a=0.0)
cue("L44", "truck", y=0.0, vis=1.0, dur=1.4)
shot("L44", mv([DX - 7.5, -11.0, 1.5], [DX, -4.0, 1.4], 32, [DX - 6.5, -10.0, 1.5], [DX, -2.5, 1.4], 32), "backing")
cue("L44.2", "truckdoor", a=110.0, dur=0.8)
shot("L44.2", C(DX, 3.0, 1.6, 14.0, 28, ang=-55), "dooropen")
# L45: a young guy jumps down with a box
only("L45", ["vern4"])
put("vern4", "L45", [DX - 1.6, -1.0, 0.6], 20, expr="smile")
show("L45", "carry_vern4")
shot("L45", cu((DX - 1.7, -1.0), 20, 3.0, 46, z=1.8), "hopprep")
put("m1", "L45.2", [DX + 0.4, 5.9], 0, expr="neutral", arms=[40, 40])
put("m2", "L45.2", [DX - 0.8, 5.9], 0, expr="neutral", arms=[40, 40])
show("L45.2", "carry_m1")
shot("L45.2", C(DX, 5.6, 1.3, 6.0, 36, ang=-20), "moversup")
only("L45.3", ["vern4"])
put("vern4", "L45.3", [DX - 1.6, -1.0, 0.6], 20, expr="smile")
go("vern4", "L45.3+0.3", [DX - 1.9, -1.2, 0.0])
beat("vern4", "L45.4", yaw=180, expr="smile")
shot("L45.3", C(DX - 1.7, -1.1, 1.0, 5.4, 40, ang=-10), "hop")
# L46: Vern's ears, Vern's laugh
only("L46", ["vern4", "m1"])
put("vern4", "L46", [MEET_V[0], MEET_V[1]], 0, expr="laugh")
put("m1", "L46", [MEET_V[0] + 1.4, MEET_V[1] + 0.6], -80, expr="grin")
show("L46", "carry_vern4", False)
shot("L46", cu(MEET_V, 0, 3.4, 50), "younglaugh")
only("L46.1", ["vern0"])
show("L46.1", "carry_m1", False)
put("vern0", "L46.1", [-4.2, -1.8], -45, expr="laugh")
shot("L46.1", cu((-4.2, -1.8), -45, 3.3, 52), "oldlaugh")
only("L46.2", ["vern4"])
put("vern4", "L46.2", MEET_V, 0, expr="warm")
shot("L46.2", cu(MEET_V, 0, 3.0, 54), "baregface")
# L47: he walks over; L48: the reveal (stuck out his hand, hi I'm Vern), held about 1.6 s
only("L47", ["vern4"])
put("vern4", "L47", [DX - 5.5, MEET_V[1]], -90, expr="smile", arms=[0, 0])
go("vern4", "L47+0.45", [MEET_V[0], MEET_V[1]], arms=[0, 0])
shot("L47", C(DX - 6.0, MEET_V[1], 1.4, 6.0, 36, ang=10), "walkover")
only("L47.1", ["vern4", "me3"])
put("vern4", "L47.1", [MEET_V[0], MEET_V[1]], -50, expr="smile", arms=[80, 80])
put("me3", "L47.1", [MEET_V[0] - 1.3, MEET_V[1]], 50, expr="soft")
shot("L47.1", C(MEET_V[0] - 0.65, MEET_V[1], 1.6, 7.6, 36, ang=0, push=0.04), "reveal")
shot("L48.2", cu(MEET_V, -20, 3.0, 54), "justmoved")
# L49
only("L49", ["vern4"])
beat("vern4", "L49", arms=[0, 0], expr="delighted", yaw=0)
shot("L49", cu(MEET_V, 15, 3.2, 52), "delighted")
shot("L49.1", cal_close(2.6, 28), "calzero")
shot("L49.2", C(0, -4.0, 1.6, 12.0, 26, ang=0), "street")
# L50: he doesn't know me yet
only("L50", ["me3"])
put("me3", "L50", [MEET_V[0] - 1.6, MEET_V[1]], 80, expr="crying")
shot("L50", cu((MEET_V[0] - 1.6, MEET_V[1]), 60, 3.3, 52), "teary")
only("L50.2", ["vern4"])
put("vern4", "L50.2", [MEET_V[0] - 0.4, MEET_V[1]], -80, expr="polite", head=[0, 12])
shot("L50.2", cu((MEET_V[0] - 0.4, MEET_V[1]), -45, 3.2, 52), "waitname")
# L51: thirty years ahead of him (the callback run, forward)
count("L51", 10950)
only("L51", [])
season("L51", "summer")
shot("L51", C(0, -1.5, 1.2, 7.0, 32, ang=-30), "cbfence")
put("nora", "L51+0.3", [WX + 0.7, WY + 0.9], 0, expr="laugh")
put("me", "L51+0.3", [WX - 0.7, WY + 0.9], 0, expr="laugh")
shot("L51+0.3", C(WX, WY + 0.9, 1.5, 5.0, 40, ang=0), "cbwedding")
only("L51+0.6", [])
shot("L51+0.6", C(AX + 0.8, AY, 0.9, 4.0, 36, ang=-20), "cbchairs")
only("L51.1", ["vern4"])
put("vern4", "L51.1", [MEET_V[0] - 0.4, MEET_V[1]], -80, expr="grin")
shot("L51.1", cu((MEET_V[0] - 0.4, MEET_V[1]), -40, 3.1, 52), "grinahead")
# L52: all the ones I already had: the bare nail
count("L52", 1)
show("L52", "cal", False)
only("L52", [])
shot("L52", C(CALX, CALY - 0.2, 2.2, 3.2, 40), "barenail")
# L53
only("L53", ["me3"])
put("me3", "L53", [MEET_V[0] - 1.6, MEET_V[1]], 80, expr="soft")
shot("L53", cu((MEET_V[0] - 1.6, MEET_V[1]), 60, 3.2, 52), "eyesfull")
only("L53.2", [])
shot("L53.2", C(0, -1.5, 1.1, 6.0, 34, ang=40), "fence3")
show("L53.3", "chairs")
shot("L53.3", C(AX + 0.8, AY, 0.9, 3.4, 40, ang=-15), "chairs2")
# L54: I tried to just shake his hand
only("L54", ["me3", "vern4"])
put("me3", "L54", [MEET_V[0] - 1.4, MEET_V[1]], 80, expr="worried", arms=[0, 90])
put("vern4", "L54", [MEET_V[0] - 0.4, MEET_V[1]], -80, expr="smile", arms=[0, 90])
show("L54", "cal")
shot("L54", C(MEET_V[0] - 0.9, MEET_V[1], 1.3, 2.4, 46, ang=-70), "reach")
# L55
only("L55", ["me3"])
beat("me3", "L55", arms=[0, 0], expr="crying")
shot("L55", cu((MEET_V[0] - 1.4, MEET_V[1]), 60, 3.0, 54), "crumple")
# L56: I hugged him
only("L56", ["me3", "vern4"])
put("me3", "L56", [MEET_V[0] - 0.7, MEET_V[1]], 80, expr="crying", arms=[75, 75])
put("vern4", "L56", [MEET_V[0] + 0.3, MEET_V[1]], -80, expr="wide", arms=[40, 40])
show("L56", "carry_vern4")
shot("L56", C(MEET_V[0] - 0.2, MEET_V[1], 1.5, 5.4, 42, ang=-5, push=0.06), "hug")
shot("L56.2", cu((MEET_V[0] - 0.7, MEET_V[1]), 55, 3.2, 50), "cried")
# L57
beat("me3", "L57", expr="sad-smile")
shot("L57", cu((MEET_V[0] - 0.7, MEET_V[1]), 60, 3.2, 52), "wetsmile")
beat("vern4", "L57.2", expr="wide")
shot("L57.2", cu((MEET_V[0] + 0.3, MEET_V[1]), -60, 3.2, 52), "stunned2")
# L58: the picture
show("L58", "carry_vern4", False)
show("L58", "cam_nora")
only("L58", ["nora2"])
put("nora2", "L58", [-6.0, 4.5], 0, expr="smile", arms=[100, 100])
shot("L58", C(-6.0, 4.5, 1.6, 3.8, 40, ang=0), "noracam")
show("L58.1", "cam_nora", False)
only("L58.1", ["me3", "vern4"])
put("me3", "L58.1", [MEET_V[0] - 0.5, MEET_V[1]], 70, expr="crying", arms=[75, 75])
put("vern4", "L58.1", [MEET_V[0] + 0.5, MEET_V[1]], -70, expr="wide", arms=[60, 60])
shot("L58.1", C(MEET_V[0], MEET_V[1], 1.4, 5.6, 36, ang=0, push=0.08), "photoframe")
# L59
only("L59", ["vern4", "me3"])
beat("vern4", "L59", arms=[0, 0], expr="worried")
go("vern4", "L59+0.5", [MEET_V[0] + 1.0, MEET_V[1]], arms=[0, 0])
shot("L59", cu((MEET_V[0] + 1.0, MEET_V[1]), -30, 3.3, 52), "crazy")
only("L59.1", ["m1", "m2"])
put("m1", "L59.1", [DX - 4.6, 1.5], 0, expr="wide")
put("m2", "L59.1", [DX - 3.4, 1.5], 0, expr="wide")
shot("L59.1", C(DX - 4.0, 1.5, 1.5, 4.4, 42, ang=0), "moversglance")
# L60
only("L60", ["vern4"])
put("vern4", "L60", [MEET_V[0] + 1.0, MEET_V[1]], 0, expr="laugh")
shot("L60", cu((MEET_V[0] + 1.0, MEET_V[1]), 0, 3.4, 52), "laughs")
put("vern4", "L60.2", [MEET_V[0] + 1.0, MEET_V[1]], -90, expr="smile")
show("L60.2", "carry_vern4")
go("vern4", "L60.4", [VX - 1.2, 4.4])
shot("L60.2", C(DX - 3.0, MEET_V[1] + 1.0, 1.4, 6.0, 36, ang=-20), "porchwalk")
show("L60.4", "cal")
count("L60.4", 0)
put("vern4", "L60.4", [CALX + 1.0, 4.2], 180, expr="smile")
show("L60.4", "carry_vern4", False)
shot("L60.4", C(CALX + 0.4, 4.2, 1.8, 3.4, 40, ang=165, dz=0.0), "newcal")
# ===== 09 empty house, the loop (L61 to L62)
only("L61", [])
show("L61", "cal", False)
show("L61", "chairs", False)
cue("L61", "truck", y=0.0, vis=0.0)
shot("L61", C(VX, 4.0, 1.5, 9.0, 30, ang=-8), "emptyporch")
shot("L61.2", C(DX - 1.0, 0.0, 0.6, 8.5, 30, ang=-30, dz=0.8), "emptydrive2")
only("L61.4", ["me3"])
put("me3", "L61.4", [-0.7, -1.3], 80, expr="soft", arms=[50, 0])
shot("L61.4", cu((-0.7, -1.3), 55, 3.4, 50), "picket")
only("L61.5", ["me3", "nora2"])
put("me3", "L61.5", [-4.6, -2.0], 35, expr="soft")
put("nora2", "L61.5", [-3.4, -2.0], -35, expr="soft", arms=[80, 80])
shot("L61.5", C(-4.0, -2.0, 1.5, 5.0, 38, ang=0), "nora_me")
only("L62.1", ["vern0", "me"])
count("L62.1", 10950)
look("L62.1", "day")
show("L62.1", "movebox")
show("L62.1", "cane_vern0")
put("vern0", "L62.1", HUGV, -45, expr="crying", arms=[75, 75])
put("me", "L62.1", HUGM, 55, expr="worried", arms=[50, 50])
shot("L62.1", cu(HUGV, -45, 4.9, 46, push=0.15), "loop")

# ---------------------------------------------------------------------------------------------- finish
cue(0, "flip", v=1.0)
cue(0, "flag", v=0.0)
cue(0, "maple", s=0.8, bend=0.0)
cue(0, "truck", y=0.0, vis=0.0)
cue(0, "photos", n=9.0)
cue(0, "rboxes", n=0.0)
cue(0, "mydoor", a=0.0)
season(0, "summer")
for k_ in acting.values():
    vi = next((i for i, a in enumerate(k_) if a.get("at") == 0 and a.get("hidden") is False), None)
    if vi is not None:
        k_[:vi] = []
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
    {"at": "L01.3>-0.25", "kind": "bell", "db": -10},
    {"at": "L10", "kind": "click", "db": -22},
    {"at": "L18.2+0.45", "kind": "thud", "db": -14},
    {"at": "L44.1", "kind": "creak", "db": -22, "dur": 1.2},
    {"at": "L56", "kind": "thud", "db": -20},
]
music = {
    "root": 57, "mode": "minor", "bpm": 92, "seed": 105,
    "sections": [
        {"at": 0, "voices": ["piano", "pad"], "energy": 0.35, "root": 57, "mode": "minor"},
        {"at": "L16", "voices": ["piano", "pad", "pulse"], "energy": 0.45, "root": 57, "mode": "major"},
        {"at": "L32", "voices": ["drone", "pad"], "energy": 0.3, "root": 45, "mode": "minor"},
        {"at": "L44", "voices": ["piano", "pad"], "energy": 0.35, "root": 57, "mode": "minor"},
        {"at": "L54", "voices": ["piano", "pad", "pulse", "choir"], "energy": 0.55, "root": 57, "mode": "major"},
    ],
}
sound = {
    "floor": "grass", "steps_db": -26,
    "ambience": [{"kind": "wind", "from": 0, "to": "end", "lufs": -44},
                 {"kind": "crickets", "from": "L13", "to": "L14", "lufs": -44},
                 {"kind": "crickets", "from": "L32", "to": "L34", "lufs": -44}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L48"), remap("L49")], "emph": [remap(x) for x in ["L01.1", "L06.1", "L12", "L20.2", "L26", "L34.3",
                                                                          "L40", "L48.1", "L55", "L62.1"]],
          "quiet": [[remap("L57"), remap("L58")]], "sway": [names["strangerwave"], names["squint2"]], "hold": [names["reveal"]]}
story = {
    "slug": "ep105-backward-neighbor",
    "title": "He Said Goodbye The Day We MET 📦",
    "made_for_kids": False,
    "premise": ("On a sunny cul-de-sac, my new neighbor Vern, about 85, hugs me on my lawn the day I move in, cries, and "
                "thanks me for thirty years, because Vern lives his days in reverse: he gets younger every year I age, never "
                "remembers yesterday, only tomorrow, and his porch calendar counts down from 10,950."),
    "twist": ("His last day on our street was my first, so thirty years later, on his first day, a young Vern moves in "
              "next door knowing nothing, and now I am the one who knows it all, cries, hugs him and thanks him for "
              "thirty years."),
    "world": ("Two small houses side by side on a bright cul-de-sac: mine pale blue, Vern's butter yellow with a deep porch, "
              "a white picket fence between the yards, a maple that grows through the seasons, and a flip calendar on a "
              "nail by Vern's door."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff8c3a",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#d8ecf8", "fog_density": 0.003, "fog_start": 40.0, "sky": "#8fd3ff",
             "sky_strength": 1.0, "exposure": 0.2, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.12, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.2, "grain": 0.008},
    "phonemes": {},
    "homophones": {"zero": "thousand", "when": "a"},   # Whisper writes "11,000" and hears "a Nora" as "when Nora"
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [names["flip"], names["flipclose"], names["tick"], names["flip3"], names["storm"], names["fixing"],
                  names["backing"], names["dooropen"], names["truckdoors"]],
    "clip_ok": [],
    "asr_forgive": ["thousand nine hundred and fifty", "the way you wave", "wave at a new neighbor"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
