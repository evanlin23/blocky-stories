"""Writes ../story.json for ep107 "returned days" (script.md, 2026-11-04). Run: python stories/ep107-returned-days/generator/make_story.py

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
REV = 2
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
TX, TY = G.TUL
MX, MY = G.MEC
APZ = 3.4
KX, HX, CX, HALLX, RAINX, ODX, LOBX, APX, BACKX = G.KX, G.HX, G.CX, G.HALLX, G.RAINX, G.ODX, G.LOBX, G.APX, G.BACKX
AR, AL = G.AISLE_R, G.AISLE_L
PALM = (0.51, -0.74, 1.30)       # a flat right palm, local to the holder
BOTH = (0.0, -0.78, 1.2)         # two forearms out front
EAR = (0.5, -0.5, 1.66)          # a phone at the ear (right arm raised 125)
DOOR_F = (-3.0, -4.0)


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return [[0, list(p0), list(t0), l0]]
    return [[0, list(p0), list(t0), l0], [1, list(p1), list(t1 if t1 is not None else t0), l1 or l0]]


def cam(tx, ty, tz, w, az=0.0, el=0.0, lens=40.0, push=0.12, sh=(0, 0, 0), dz=0.0):
    """A camera aimed at (tx, ty, tz) with a frame w metres wide at the target, seen from azimuth az (0 = from -y,
    90 = from +x, 180 = from +y, 270 = from -x) and el degrees up; it pushes in by `push` (negative pulls out)."""
    def pos(width, tgt):
        d = width * lens / 13.5
        a, e = az * D2R, el * D2R
        return [tgt[0] + d * math.sin(a) * math.cos(e), tgt[1] - d * math.cos(a) * math.cos(e), tgt[2] + d * math.sin(e) + dz]
    t0 = [tx, ty, tz]
    t1 = [tx + sh[0], ty + sh[1], tz + sh[2]]
    return mv(pos(w, t0), t0, lens, pos(w * (1 - push), t1), t1, lens)


def cm(p0, t0, p1, t1, lens):
    return mv(p0, t0, lens, p1, t1, lens)


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
    "me": person("#e3b088", "#2f4f86", "#4a6fa5", "#f4f4f2", hair="swoop", hair_c="#c0983f", brow_w=1.9),
    "dad": person("#d9a47c", "#c09a6b", "#5b5547", "#3a2a1c", hair="cap", hair_c="#b8b8be", collar="#e8d9b8", width=1.06),
    "tulley": person("#f0c8a0", "#a77f5a", "#6a5a48", "#3a2a1c", hair="buzz", hair_c="#ececec", pattern="knit",
                     pattern_c="#8a6444", extras=["glasses"], extra_c="#3a3a3e", height=0.96),
    "oduya": person("#8a5a3a", "#e0527a", "#2a6f5a", "#3a2a1c", hair="none", hat="beanie", hat_c="#ff9a2e", eyes="lashes",
                    brow_w=1.9),
    "rich": person("#f1c9a0", "#f4f4f4", "#2e3a52", "#f2a0c0", hair="spiky", hair_c="#6a4a2a", extras=["tie"],
                   extra_c="#c0392b"),
    "rich2": person("#f1c9a0", "#f4f4f4", "#2e3a52", "#1c1c20", hair="spiky", hair_c="#6a4a2a", extras=["tie"],
                    extra_c="#c0392b"),
    "intv": person("#c88f66", "#555b6a", "#2a2f3a", "#1c1c20", hair="bun", hair_c="#1a1410", eyes="lashes"),
    "cust": person("#f0c8a0", "#e8845a", "#4a5a7a", "#6a4a32", hair="long", hair_c="#6a3a1a", eyes="lashes"),
    "man": person("#b98456", "#f6f6f2", "#4a4036", "#2a2a2a", hair="buzz", hair_c="#1a1410", sleeves="short"),
    "p1": person("#9a6a48", "#c0507a", "#2a2a38", "#d8d0c8", hair="long", hair_c="#150f0c", eyes="lashes"),
    "p2": person("#e8b890", "#3a8aaa", "#5a4a3a", "#2a3a2a", hair="spiky", hair_c="#a05a2a", sleeves="short"),
    "p3": person("#d3a07a", "#5fae4a", "#3a3a4a", "#6a4a32", hair="cap", hair_c="#2a2a2a"),
}
acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0]}] for n in cast}
last = {n: [0, 0] for n in cast}
visible = set()
cues = []
SH = []
LOOK = [None]


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


def talk(who, a, b, amt=0.55):
    acting[who].append({"from": a, "to": b, "mouth": [amt, amt], "flap": True})


def shot(at, camera, look=None, name=None, step=2):
    SH.append((at, camera, step, None, None, name))
    if look and look != LOOK[0]:
        cue(at, "look", id=look, dur=0)
        LOOK[0] = look


def obj(at, name, **kw):
    cue(at, "obj", obj=name, **kw)


def hold(at, name, who, off, **kw):
    obj(at, name, who=who, off=list(off), **kw)


def world(at, name, p, **kw):
    obj(at, name, p=list(p), **kw)


def unobj(at, name):
    obj(at, name, vis=False)


def sit(who, at, on=True, z=0.62):
    cue(at, "sit", who=who, on=on, z=z)


def lamps(at, a=None, b=None, c=None, dur=0.4):
    kw = {k: v for k, v in (("a", a), ("b", b), ("c", c)) if v is not None}
    cue(at, "lamps", dur=dur, **kw)


def fdoor(at, a, dur=0.4):
    cue(at, "fdoor", a=float(a), dur=dur)


def bdoor(at, a, dur=0.8):
    cue(at, "bdoor", a=float(a), dur=dur)


# ---------------------------------------------------------------------------------------------- 01 the rule (L01 to L18)
cue(0, "look", id="day", dur=0)
LOOK[0] = "day"
# L01: the receipt slides under the bell, the stamp comes down on "ELSE"
only(0, ["tulley"])
put("tulley", 0, [TX, TY], 0, expr="polite", arms=[0, 88])
world(0, "rcp", [-3.4, 3.2, 1.012], rz=-25)
world("L01+0.05", "rcp", [-1.29, 3.72, 1.012], rz=0, dur=1.2)
world(0, "stamp", [-1.29, 3.72, 1.32])
world("L01.4-0.15", "stamp", [-1.29, 3.72, 1.09], dur=0.2)
world("L01.4+0.15", "stamp", [-1.29, 3.72, 1.32], dur=0.3)
cue("L01.4-0.05", "ring", v=1.0)
beat("tulley", "L01.4-0.15", arms=[0, 72], blend=0.15)
beat("tulley", "L01.4+0.15", arms=[0, 88], blend=0.3)
world("L01.3", "gb5", [-4.9, 9.38, 1.99], rz=0)
world("L01.3+0.1", "gb5", [-3.6, 9.38, 1.99], rz=0, dur=0.9)
shot(0, cam(-2.1, 3.75, 1.1, 1.5, az=-8, el=30, lens=40, push=0.1), name="s1a")
shot("L01.2", cam(TX, TY, 1.52, 1.0, lens=45, push=0.1), name="s1b")
shot("L01.3", cam(-3.9, 9.4, 1.8, 1.7, lens=40, push=0.1), name="s1c")
shot("L01.4", cam(-1.29, 3.72, 1.08, 0.9, az=-25, el=25, lens=45, push=0.12), name="s1d")
# L02: the back of the receipt, then me squinting at it
only("L02", ["me"])
shot("L02", cam(BACKX, 0, 1.5, 1.2, push=0.1), name="s2a")
put("me", "L02.1", [MX, MY], 180, expr="neutral", arms=[0, 0])
beat("me", "L02.1+0.5", head=[0, 14], expr="worried")
shot("L02.1", cam(MX, MY, 1.52, 0.95, az=180, lens=50, push=0.1), name="s2b")
# L03: the fan of receipts, then me scared
only("L03", ["me"])
put("me", "L03.1", [APX - 2.2, 4.9, APZ], 0, expr="scared", head=[0, 22], lean=8)
shot("L03", cam(APX - 2.2, 3.5, APZ + 0.84, 1.2, el=60, lens=40, push=0.15), look="day", name="s3a")
shot("L03.1", cam(APX - 2.2, 4.9, APZ + 1.45, 1.1, lens=50, push=0.1), name="s3b")
# L04: Tulley's at night, then me pushing through the door
only("L04", ["me"])
put("me", "L04", [DOOR_F[0], -5.7], 180, expr="neutral", arms=[0, 88])
hold("L04", "rcp", "me", PALM)
shot("L04", cam(DOOR_F[0] - 0.4, -5.7, 1.35, 1.7, az=-22, el=10, lens=40, push=0.08), look="night", name="s4a")
lamps("L04", 1, 1, 1, dur=0.0)
put("me", "L04.1", [DOOR_F[0], -7.0], 180, expr="neutral", arms=[0, 0])
go("me", "L04.1+0.9", [DOOR_F[0], -1.8])
fdoor("L04.1-0.2", 80, dur=0.3)
fdoor("L04.1+1.4", 0, dur=0.6)
cue("L04.1+0.5", "bell")
acting["me"][-1]["sfx"] = "door"
shot("L04.1", cam(DOOR_F[0], -3.6, 1.45, 2.3, az=180, lens=40, push=0.1), name="s4b")
# L05: Mr. Tulley takes the receipt, the day comes off me like a coat
only("L05", ["me", "tulley"])
put("me", "L05", [MX, MY], 180, expr="neutral", arms=[0, 88])
put("tulley", "L05", [TX, TY], 0, expr="polite", arms=[0, 88])
hold("L05", "rcp", "me", PALM)
world("L05+0.5", "rcp", [-1.52, 3.45, 1.012], rz=0, dur=0.4)
hold("L05+0.95", "rcp", "tulley", (0.51, -0.7, 1.27))
unobj("L05+1.4", "rcp")
hold("L05.1", "shim", "me", (0.0, 0.4, 1.1))
hold("L05.2", "shim", "me", (0.0, 1.0, 1.9), dur=0.7)
beat("me", "L05.2", arms=[0, 0], expr="soft")
shot("L05", cam(-1.8, 3.5, 1.35, 2.1, az=55, el=6, lens=40, push=0.06), look="night", name="s5a")
shot("L05.1", cam(MX, MY + 0.1, 1.5, 1.6, az=60, el=8, lens=45, push=0.1), name="s5b")
# L06: the shimmer folds into a little gray box on the counter; I roll my shoulders
world("L06", "shim", [-2.4, 3.5, 1.15], s=0.32, dur=0.75)
unobj("L06+0.8", "shim")
world("L06+0.78", "gb4", [-2.4, 3.5, 1.0], rz=0)
beat("me", "L06+0.2", expr="soft", head=[10, -4])
shot("L06", cam(-2.4, 3.5, 1.15, 1.3, az=-30, el=22, lens=40, push=0.12), name="s6a")
shot("L06+0.8", cam(MX, MY, 1.5, 0.95, az=180, lens=50, push=0.1), name="s6b")
# L07: a street rewinding (the coffee un-spills), then the man walks on
only("L07", ["man"])
put("man", "L07", [3.0, -6.2], 0, expr="worried", arms=[0, 88])
hold("L07", "cup", "man", PALM)
cue("L07", "stain", v=1.0)
cue("L07+0.25", "stain", v=0.0, dur=1.0)
beat("man", "L07+1.2", expr="neutral", arms=[0, 20])
shot("L07", cam(3.0, -6.2, 1.1, 1.7, lens=40, push=0.12), look="day", name="s7a")
beat("man", "L07.1", expr="neutral", arms=[0, 20])
go("man", "L07.1>", [8.0, -6.2], yaw=90)
shot("L07.1", cam(5.0, -6.1, 1.2, 3.2, az=20, lens=40, push=0.1, sh=(1.5, 0, 0)), name="s7b")
# L08: three passersby glance at each other and walk on
only("L08", ["p1", "p2", "p3"])
unobj("L08", "cup")
for who, x, y in (("p1", -2.0, -6.1), ("p2", 0.0, -6.3), ("p3", 2.0, -6.1)):
    put(who, "L08", [x, y], 0, expr="blank")
beat("p1", "L08+0.5", head=[-40, 0])
beat("p2", "L08+0.6", head=[-40, 0])
beat("p3", "L08+0.7", head=[40, 0])
beat("p1", "L08.1", head=[40, 0], expr="worried")
beat("p2", "L08.1+0.2", head=[40, 0])
beat("p3", "L08.1+0.1", head=[-40, 0])
shot("L08", cam(0.0, -6.2, 1.5, 3.8, lens=40, push=0.14), name="s8")
# L09: Mrs. Oduya backs her van over the mailbox
only("L09", ["oduya"])
put("oduya", "L09", [ODX + 4.6, 0.6], 180, expr="neutral", arms=[0, 0])
sit("oduya", "L09", True, 0.9)
go("oduya", "L09.2", [ODX + 4.6, -1.9])
beat("oduya", "L09.2+0.3", expr="scared")
go("oduya", "L09.2+0.7", [ODX + 4.6, -2.35])
cue("L09.2+0.3", "mbx", f=0.0)
cue("L09.2+0.4", "mbx", f=1.0, dur=0.3)
shot("L09", cam(ODX + 4.0, -1.8, 1.2, 7.4, az=90, el=10, lens=40, push=0.08), look="day", name="s9a")
shot("L09.1", cam(ODX + 4.6, 0.6, 1.4, 3.0, az=112, el=6, lens=40, push=0.06), name="s9b")
shot("L09.2", cam(ODX + 4.6, -3.0, 0.9, 3.8, az=120, lens=40, push=0.1), name="s9c")
only("L09.3", ["oduya"])
sit("oduya", "L09.3", False)
put("oduya", "L09.3", [MX, MY], 180, expr="worried", arms=[0, 88])
hold("L09.3", "rcp", "oduya", PALM)
shot("L09.3", cam(MX, MY, 1.4, 1.8, az=70, el=6, lens=40, push=0.1), name="s9d")
# L10: the mailbox is fine; she backs out perfectly and waves
only("L10", ["oduya", "p1"])
unobj("L10", "rcp")
sit("oduya", "L10", True, 0.9)
cue("L10", "mbx", f=0.0)
put("oduya", "L10", [ODX + 3.0, 4.5], 180, expr="smile", arms=[0, 105])
go("oduya", "L10.2", [ODX + 3.0, -2.0])
put("p1", "L10", [ODX + 7.5, -2.8], -90, expr="smile", arms=[0, 150])
beat("p1", "L10.1", arms=[150, 0])
shot("L10", cam(ODX + 4.6, -4.9, 1.1, 1.3, az=30, lens=40, push=0.12), name="s10a")
shot("L10.1", cam(ODX + 3.2, 2.4, 1.5, 3.4, az=112, el=6, lens=40, push=0.0, sh=(0, -2.6, 0)), name="s10b")
# L11: Rich wore slippers to the interview
only("L11", ["rich", "intv"])
sit("oduya", "L11", False)
put("rich", "L11", [LOBX - 0.72, 4.0], 70, expr="polite")
put("intv", "L11", [LOBX + 0.72, 4.0], -70, expr="blank", head=[0, 28])
beat("intv", "L11+0.8", head=[0, 38], expr="wide")
shot("L11", cam(LOBX, 4.0, 1.45, 2.5, az=-12, lens=40, push=-0.04), look="day", name="s11a")
only("L11.1", ["rich"])
put("rich", "L11.1", [MX, MY], 180, expr="polite", arms=[0, 0])
shot("L11.1", cam(MX, MY, 1.05, 2.4, az=70, lens=40, push=0.06), name="s11b")
beat("rich", "L11.3", expr="worried", head=[0, 12])
shot("L11.3", cam(MX, MY, 1.5, 0.95, az=180, lens=50, push=0.1), name="s11c")
# L12: he got the job the second time
only("L12", ["rich2", "intv"])
put("rich2", "L12", [LOBX - 0.72, 4.0], 90, expr="grin", arms=[0, 88])
put("intv", "L12", [LOBX + 0.73, 4.0], -90, expr="smile", arms=[88, 0])
beat("rich2", "L12+0.5", arms=[0, 70])
beat("intv", "L12+0.5", arms=[70, 0])
shot("L12", cam(LOBX, 4.3, 1.35, 3.0, az=-12, lens=40, push=0.12), name="s12a")
only("L12.1", ["rich2"])
put("rich2", "L12.1", [LOBX + 5.2, 11.4], 0, expr="grin", arms=[0, 0])
for k in range(6):
    t_ = 0.1 + 0.3 * k
    beat("rich2", f"L12.1+{t_:.2f}", arms=[165, 20] if k % 2 == 0 else [20, 165], yaw=(-22 if k % 2 == 0 else 22), blend=0.12)
shot("L12.1", cam(LOBX + 5.2, 11.2, 1.25, 2.3, lens=40, push=0.1), name="s12b")
# L13: the fine print on every receipt (magnifier), me leaning in
only("L13", ["me"])
cue("L13", "mag", u=0.0)
cue("L13", "mag", u=1.0, dur=1.6)
shot("L13", cam(BACKX, 0, 1.45, 1.1, push=0.1), name="s13a")
put("me", "L13.1", [APX - 2.2, 4.9, APZ], 0, expr="worried", head=[0, 25], lean=10)
beat("me", "L13.1+0.8", lean=18)
shot("L13.1", cam(APX - 2.2, 4.9, APZ + 1.4, 1.3, lens=50, push=0.12), name="s13b")
# L14: returned days are restocked: Mr. Tulley carries an armful through the door
only("L14", ["tulley"])
bdoor("L14-0.1", -100, dur=0.5)
put("tulley", "L14", [AR, 6.4], 180, expr="polite", arms=[88, 88])
go("tulley", "L14+0.9", [AR, 9.4])
go("tulley", "L14.1+0.35", [AR, 12.4])
hold("L14", "gb3", "tulley", (0.0, -0.78, 1.2))
hold("L14", "gb4", "tulley", (0.0, -0.78, 1.46))
hold("L14", "gb5", "tulley", (0.0, -0.78, 1.72))
shot("L14", cm([-4.2, 8.7, 1.5], [AR, 8.7, 1.3], [-4.0, 8.7, 1.5], [AR, 8.7, 1.3], 36), name="s14a")
bdoor("L14.1+0.3", 0, dur=0.6)
unobj("L14.1+0.6", "gb3")
unobj("L14.1+0.6", "gb4")
unobj("L14.1+0.6", "gb5")
only("L14.1+0.8", [])
shot("L14.1", cam(AR, 10.0, 1.3, 2.4, lens=40, push=0.1), name="s14b")
# L15: in the back room they sit on a shelf in little gray boxes
bdoor("L15-0.1", -22, dur=0.5)
shot("L15", cm([2.1, 8.6, 1.5], [AR, 15.0, 1.7], [2.35, 9.2, 1.5], [AR, 15.0, 1.7], 45), look="dim", name="s15a")
shot("L15.2", cam(0.85, 16.0, 1.9, 0.9, az=90, lens=50, push=0.12), name="s15b")
# L16: somebody can buy them, four dollars each
bdoor("L16", 0, dur=0.6)
only("L16", ["cust", "tulley"])
put("cust", "L16", [MX, MY], 180, expr="polite", arms=[0, 0])
put("tulley", "L16", [TX, TY], 0, expr="knowing", arms=[88, 88])
hold("L16", "gb1", "tulley", BOTH)
world("L16.1", "gb1", [MX, 3.45, 1.0], rz=0, dur=0.4)
world("L16.2", "coins2", [MX + 0.25, 3.1, 1.004], rz=15, dur=0.0)
shot("L16", cam(MX, 3.5, 1.35, 2.5, az=90, el=6, lens=40, push=0.1), look="day", name="s16a")
shot("L16.2", cam(MX + 0.2, 3.1, 1.02, 0.9, az=0, el=38, lens=45, push=0.12), name="s16b")
# L17: whoever buys a day gets to remember it
only("L17", ["cust"])
unobj("L17", "coins2")
beat("cust", "L17", arms=[88, 88], expr="delighted")
hold("L17", "gb1", "cust", (0.0, -0.8, 0.95))
cue("L17", "lid", a=0.0)
cue("L17+0.2", "lid", a=100.0, dur=0.6)
cue("L17", "glow", x=MX, y=MY + 0.8, z=1.55, g=0.0)
cue("L17+0.2", "glow", x=MX, y=MY + 0.8, z=1.55, g=1.0, dur=0.6)
shot("L17", cam(MX, MY, 1.3, 1.5, az=150, el=18, lens=45, push=0.1), name="s17")
# L18: the whole thing, the way it happened; a day nobody remembers goes sour on the shelf
beat("cust", "L18", expr="laugh")
shot("L18", cam(MX, MY, 1.5, 0.85, az=180, lens=50, push=0.1), name="s18a")
cue("L18.1", "lid", a=0.0, dur=0.5)
cue("L18.1+0.2", "glow", x=MX, y=MY + 0.8, z=1.55, g=0.0, dur=0.5)
shot("L18.1", cam(MX, 3.0, 1.2, 1.5, az=90, lens=40, push=0.1), name="s18b")
only("L18.2", ["tulley"])
unobj("L18.2", "gb1")
put("tulley", "L18.2", [TX, TY], 0, expr="knowing", arms=[0, 0])
talk("tulley", "L18.2", "L18.3")
shot("L18.2", cam(TX, TY, 1.52, 1.0, lens=45, push=0.1), name="s18c")
shot("L18.4", cam(-3.2, 9.6, 1.7, 1.5, lens=40, push=0.1), name="s18d")

# ---------------------------------------------------------------------------------------------- 02 forty-seven days (L19 to L28)
only("L19", ["me"])
put("me", "L19", [MX, MY], 180, expr="worried", arms=[0, 0])
shot("L19", cam(MX, MY, 1.5, 0.95, az=180, lens=50, push=0.1), name="s19a")
only("L19.1", ["tulley"])
put("tulley", "L19.1", [TX, TY], 0, expr="knowing", arms=[0, 88])
world("L19.1", "rcp", [-1.29, 3.72, 1.012])
cue("L19.1", "ring", v=0.0)
world("L19.1", "stamp", [-1.29, 3.72, 1.32])
world("L19.1+0.5", "stamp", [-1.29, 3.72, 1.09], dur=0.2)
cue("L19.1+0.6", "ring", v=1.0)
world("L19.1+0.85", "stamp", [-1.29, 3.72, 1.32], dur=0.3)
beat("tulley", "L19.1+0.5", arms=[0, 72], blend=0.15)
beat("tulley", "L19.1+0.85", arms=[0, 88], blend=0.3)
shot("L19.1", cam(TX + 0.4, TY - 0.3, 1.3, 1.5, az=-20, lens=40, push=0.12), name="s19b")
# L20: a fast stack of my receipts lands on the counter
unobj("L20", "stamp")
unobj("L20", "rcp")
only("L20", [])
world("L20", "rcp", [-1.4, 3.3, 1.9], rz=10)
world("L20+0.2", "rcp", [-1.4, 3.3, 1.014], rz=10, dur=0.25, hop=0.0)
world("L20+0.5", "rcp", [-1.35, 3.35, 1.022], rz=-12, dur=0.01)
shot("L20", cam(-1.4, 3.35, 1.02, 1.1, el=40, lens=40, push=0.12), name="s20")
# L21: my car breaking down; the day I got laid off
only("L21", ["me"])
unobj("L21", "rcp")
shot("L21", cam(CX + 0.5, -4.5, 1.1, 5.2, az=160, lens=40, push=0.1, dz=0.4), look="day", name="s21a")
put("me", "L21.1", [HALLX, 4.2], 0, expr="worried", arms=[88, 88], head=[0, 14])
hold("L21.1", "cbox", "me", (0.0, -0.95, 1.05))
shot("L21.1", cam(HALLX, 5.5, 1.35, 2.3, lens=40, push=0.1), name="s21b")
# L22: locked out in the rain
only("L22", ["me"])
unobj("L22", "cbox")
put("me", "L22", [RAINX, 4.8], 0, expr="worried", arms=[0, 0], head=[0, 8])
for k in range(5):
    beat("me", f"L22+{0.2 + 0.4 * k:.2f}", arms=[40, 0] if k % 2 == 0 else [0, 40], blend=0.1)
shot("L22", cam(RAINX, 4.8, 1.3, 1.9, lens=40, push=0.12), look="rain", name="s22")
# L23: I don't remember any of them
put("me", "L23", [APX - 1.0, 4.6, APZ], 0, expr="worried", arms=[0, 88], head=[0, 22])
hold("L23", "rcp", "me", PALM)
shot("L23", cam(APX - 1.0, 4.6, APZ + 1.35, 1.2, lens=50, push=0.12), look="day", name="s23")
# L24: I only know from the receipts
unobj("L24", "rcp")
only("L24", [])
cue("L24", "flick", u=0.0)
cue("L24.1", "flick", u=1.0, dur=1.0)
shot("L24", cam(APX + 3.8, 6.9, APZ + 0.95, 1.2, el=48, lens=40, push=0.12), name="s24a")
shot("L24.1", cam(APX + 3.7, 6.9, APZ + 0.95, 0.8, el=55, lens=40, push=0.12), name="s24b")
# L25: the same stamp on the back of every one
shot("L25", cm([BACKX + 3.2, -1.5, 1.1], [BACKX + 3.2, 0, 1.0], [BACKX + 9.0, -1.5, 1.1], [BACKX + 9.0, 0, 1.0], 55), name="s25")
# L26: SOLD
cue("L26", "pulse", p=0.0)
cue("L26", "pulse", p=1.0, dur=0.15)
cue("L26+0.2", "pulse", p=0.0, dur=0.3)
shot("L26", cam(BACKX + 14.0, 0, 1.2, 1.6, lens=40, push=0.2), name="s26")
# L27: somebody in this town is living my worst days
put("me", "L27", [APX, 7.0, APZ], 180, expr="scared", arms=[0, 0])
shot("L27", cam(APX, 6.9, APZ + 1.5, 1.4, az=180, lens=45, push=0.08), name="s27a")
only("L27.1", ["p1", "p2", "p3"])
put("p1", "L27.1", [APX - 2.0, 11.6, 0], 90, expr="neutral")
go("p1", "L27.1>", [APX + 3.0, 11.6, 0])
put("p2", "L27.1", [APX + 3.0, 12.3, 0], -90, expr="neutral")
go("p2", "L27.1>", [APX - 2.5, 12.3, 0])
put("p3", "L27.1", [APX + 0.0, 11.8, 0], 90, expr="neutral")
go("p3", "L27.1>", [APX + 4.0, 11.8, 0])
shot("L27.1", cm([APX, 7.4, APZ + 1.5], [APX + 0.5, 12.0, 0.8], [APX + 0.4, 7.4, APZ + 1.5], [APX + 0.8, 12.0, 0.8], 50), name="s27b")
# L28: forty-seven times
only("L28", ["me"])
put("me", "L28", [APX - 1.0, 4.6, APZ], 0, expr="worried", arms=[0, 0], head=[0, 10])
cue("L28", "pulse", p=1.0, dur=0.2)
cue("L28+0.5", "pulse", p=0.0, dur=0.3)
shot("L28", cam(APX - 1.0, 4.6, APZ + 1.5, 0.9, lens=50, push=0.15), name="s28")

# ---------------------------------------------------------------------------------------------- 03 after closing (L29 to L43)
# L29: closing time
cue("L29", "look", id="eve", dur=0)
LOOK[0] = "eve"
only("L29", ["me", "tulley"])
put("me", "L29", [-5.0, 6.2], 90, expr="neutral", arms=[0, 0])
beat("me", "L29.2", head=[-30, 0], expr="worried")
put("tulley", "L29", [-0.5, 7.2], 270, expr="polite", arms=[0, 0])
shot("L29", cam(-4.6, 6.4, 1.2, 3.0, az=-35, lens=40, push=0.1), name="s29a")
unobj("L29.2", "stamp")
put("tulley", "L29.2", [-3.0, -2.4], 0, expr="polite", arms=[0, 88])
beat("tulley", "L29.2+0.4", arms=[0, 88])
world("L29.2", "gb5", [-3.0, -3.93, 1.62], rz=0)
only("L29.2", ["tulley"])
shot("L29.2", cm([-1.4, 1.2, 1.5], [-3.0, -3.6, 1.55], [-1.9, 0.6, 1.5], [-3.0, -3.7, 1.55], 45), name="s29b")
# L30: Mr. Tulley turns off the lights and goes upstairs
cue("L30.1", "look", id="night", dur=1.4)
LOOK[0] = "night"
lamps("L30.1", 0, None, None, dur=0.4)
lamps("L30.1+0.5", 0, 0, None, dur=0.4)
lamps("L30.1+1.0", 0, 0, 0, dur=0.4)
unobj("L30", "gb5")
put("tulley", "L30", [-0.5, 3.0], 0, expr="polite", arms=[0, 0])
only("L30", ["tulley"])
shot("L30", cam(-0.5, 3.0, 1.5, 1.8, az=20, lens=40, push=0.1), name="s30a")
go("tulley", "L30.2", [5.0, 4.4], yaw=90)
go("tulley", "L30.2+0.9", [6.0, 5.0], yaw=180)
go("tulley", "L30>", [6.0, 8.6, 2.6])
shot("L30.2", cm([-3.6, 7.0, 1.5], [6.0, 6.6, 1.3], [-3.0, 7.0, 1.5], [6.0, 7.2, 1.5], 36), name="s30b")
only("L30>", [])
# L31: I open the back-room door
put("me", "L31", [2.58, 9.3], 180, expr="neutral", arms=[0, 90])
shot("L31", cam(2.2, 9.7, 1.3, 1.7, az=-30, el=8, lens=40, push=0.08), look="dim", name="s31a")
bdoor("L31.1", -100, dur=1.3)
acting["me"][-1]["sfx"] = "creak"
beat("me", "L31.1", arms=[0, 0])
go("me", "L31.1+0.8", [1.0, 8.8], yaw=180)
shot("L31.1", cm([3.2, 6.8, 1.55], [AR, 17.0, 1.8], [2.8, 7.2, 1.55], [AR, 17.0, 1.8], 45), name="s31b")
# L32: shelves up to the ceiling
only("L32", [])
put("me", "L32.1", [AR, 15.2], -90, expr="wide", arms=[0, 0], head=[0, -25])
shot("L32", cm([2.9, 12.4, 0.35], [0.9, 19.0, 3.3], [2.7, 12.8, 0.4], [0.9, 19.0, 3.6], 26), name="s32a")
shot("L32.1", cm([AR + 1.0, 11.4, 0.9], [AR - 0.4, 15.2, 2.0], [AR + 0.8, 11.8, 0.9], [AR - 0.4, 15.2, 2.2], 28), name="s32b")
# L33: thousands of gray boxes, each one somebody's bad day
only("L33", [])
cue("L33", "bulb", a=0.06)
cue("L33.2", "bulb", a=0.14, dur=0.6)
shot("L33", cm([2.5, 13.0, 1.9], [0.85, 15.0, 1.9], [2.5, 20.0, 1.9], [0.85, 22.0, 1.9], 45), name="s33a")
shot("L33.2", cm([AR, 19.0, 0.9], [AR, 24.6, 3.0], [AR, 19.6, 1.0], [AR, 24.6, 3.2], 36), name="s33b")
# L34: you can hear them if you get close
put("me", "L34", [1.7, 16.0], -90, expr="shut", arms=[0, 0], head=[70, 0], lean=18)
shot("L34", cam(1.3, 16.0, 1.45, 1.4, az=0, lens=45, push=0.12), name="s34a")
put("me", "L34.1", [1.8, 16.0], 0, expr="wide", arms=[0, 0], head=[-55, 0], lean=0)
shot("L34.1", cam(1.8, 16.0, 1.55, 0.95, az=0, lens=50, push=0.1), name="s34b")
# L35: a birthday party in one, rain in another
only("L35", [])
shot("L35", cam(-4.3, 17.6, 2.35, 0.9, az=90, lens=45, push=0.12), name="s35a")
shot("L35.2", cam(-4.3, 19.4, 1.9, 0.9, az=90, lens=45, push=0.12), name="s35b")
# L36: mine are on the bottom shelf
put("me", "L36", [3.45, 17.0], 172, expr="curious", arms=[0, 0], head=[0, 0])
sit("me", "L36", True, 0.17)
shot("L36", cm([2.9, 20.4, 1.1], [3.45, 17.0, 0.7], [3.0, 20.0, 1.05], [3.45, 17.0, 0.7], 30), name="s36a")
only("L36.1", [])
shot("L36.1", cm([3.2, 12.0, 0.45], [4.3, 20.0, 0.3], [3.3, 13.0, 0.45], [4.3, 21.0, 0.3], 35), name="s36b")
put("me", "L36.2", [3.3, 17.0], 90, expr="soft", arms=[0, 55])
shot("L36.2", cam(4.0, 17.0, 0.5, 1.2, az=-70, el=10, lens=40, push=0.12), name="s36c")
# L37: forty-seven boxes, one hold slip
only("L37", [])
shot("L37", cam(4.28, 12.6, 0.4, 1.6, az=292, el=10, lens=22, push=0.1), name="s37a")
put("me", "L37.1", [3.4, 13.4], 90, expr="neutral", arms=[0, 0], head=[0, 14])
sit("me", "L37.1", False)
shot("L37.1", cam(3.4, 13.4, 1.0, 1.0, az=-30, lens=50, push=0.12), name="s37b")
# L38: the front bell rings
cue("L38", "look", id="night", dur=0)
LOOK[0] = "night"
only("L38", ["me"])
fdoor("L38-0.1", 65, dur=0.4)
cue("L38+0.3", "bell")
shot("L38", cam(-3.0, -3.7, 2.6, 1.2, az=180, lens=45, push=0.12), look="night", name="s38a")
put("me", "L38.1", [3.4, 17.0], 180, expr="scared", arms=[0, 0])
sit("me", "L38.1", True, 0.17)
shot("L38.1", cam(3.4, 17.0, 0.9, 1.3, az=0, lens=45, push=0.12), look="dim", name="s38b")
# L39: somebody was coming in after closing (a shape in the door, through the bead curtain)
only("L39", ["dad"])
sit("me", "L39", False)
put("dad", "L39", [DOOR_F[0], -3.4], 180, expr="neutral", arms=[0, 0])
shot("L39", cm([-1.6, 6.4, 1.4], [DOOR_F[0], -3.6, 1.25], [-1.7, 6.2, 1.4], [DOOR_F[0], -3.6, 1.25], 75), look="night", name="s39")
# L40: I hid behind the shelf and held my breath
only("L40", ["me"])
fdoor("L40", 0, dur=0.6)
put("me", "L40", [-1.9, 26.6], 0, expr="scared", arms=[0, 0], head=[0, 0])
shot("L40", cam(-1.9, 26.6, 1.5, 1.4, lens=45, push=0.12), look="dim", name="s40a")
shot("L40.1", cm([AR, 14.0, 0.9], [AR, 24.6, 3.0], [AR, 14.8, 1.0], [AR, 24.6, 3.2], 36), name="s40b")
# L41: slow footsteps, straight to my boxes
only("L41", ["dad"])
put("dad", "L41", [AR, 19.8], 180, expr="neutral", arms=[0, 0])
go("dad", "L41.1", [AR, 22.8])
shot("L41", cm([AR + 0.25, 25.4, 0.06], [AR, 20.5, 0.12], [AR + 0.2, 25.2, 0.06], [AR, 21.9, 0.12], 60), name="s41a")
put("dad", "L41.1", [3.3, 24.0], 180, expr="neutral")
go("dad", "L41>", [3.3, 25.7], yaw=90)
shot("L41.1", cm([2.2, 22.0, 0.35], [3.65, 25.2, 0.3], [2.4, 22.6, 0.4], [3.65, 25.5, 0.3], 36), name="s41b")
# L42: a hand took the newest one
world("L42-0.5", "gb2", [4.55, 26.2, 0.1], rz=90)
beat("dad", "L42", yaw=90, arms=[0, 88], expr="neutral")
hold("L42+0.3", "gb2", "dad", PALM, dur=0.6, hop=0.0)
shot("L42", cm([3.85, 23.0, 1.05], [4.0, 26.2, 1.0], [3.85, 23.4, 1.15], [4.0, 26.2, 1.2], 35), name="s42a")
only("L42.1", ["dad"])
shot("L42.1", cm([-1.6, 25.75, 1.95], [3.4, 25.8, 1.4], [-1.4, 25.75, 1.95], [3.4, 25.8, 1.35], 55), name="s42b")
# L43: then he whistled
beat("dad", "L43", yaw=90, head=[0, 0])
shot("L43", cm([-2.3, 25.7, 1.85], [3.5, 25.8, 1.4], [-2.0, 25.7, 1.85], [3.5, 25.8, 1.4], 70), name="s43a")
put("me", "L43.2", [-2.4, 25.75], 90, expr="wide", arms=[0, 0])
only("L43.2", ["me", "dad"])
shot("L43.2", cam(-2.4, 25.75, 1.5, 0.95, az=90, lens=50, push=0.1, dz=0.0), name="s43b")
# the music drop (P01): the bulb and the shelf in its light
shot("P01", cm([AR, 20.0, 0.9], [AR, 24.4, 3.1], [AR, 20.6, 1.0], [AR, 24.4, 3.3], 34), name="drop")
cue("P01", "bulb", a=0.1)

# ---------------------------------------------------------------------------------------------- 04 it was my dad (L44 to L60)
# L44: it was my Dad
only("L44", ["dad"])
put("dad", "L44", [3.0, 25.3], 90, expr="neutral", arms=[0, 88])
hold("L44", "gb2", "dad", PALM)
beat("dad", "L44+0.2", yaw=0, expr="neutral", blend=0.5)
cue("L44", "bulb", a=0.05)
shot("L44", cam(3.0, 25.3, 1.55, 1.1, lens=50, push=0.1, dz=0.0), name="s44")
# L45: he paid four dollars for my worst day (the reveal picture)
cue("L45.1", "coins", v=1.0)
only("L45", ["dad"])
shot("L45", cm([AR, 17.5, 1.5], [3.4, 25.5, 1.2], [AR + 0.1, 18.4, 1.5], [3.4, 25.5, 1.2], 50), name="s45a")
shot("L45.1", cm([3.4, 25.3, 0.55], [4.45, 26.4, 0.12], [3.5, 25.5, 0.5], [4.45, 26.4, 0.12], 45), name="s45b")
# L46: the one where I lost my job
shot("L46", cam(3.5, 24.5, 1.3, 0.6, lens=45, az=-10, push=0.12, dz=0.0), name="s46a")
only("L46.1", ["me"])
put("me", "L46.1", [HALLX, 4.2], 0, expr="worried", arms=[88, 88], head=[0, 14])
hold("L46.1", "cbox", "me", (0.0, -0.95, 1.05))
shot("L46.1", cam(HALLX, 4.2, 1.35, 2.0, lens=40, push=0.1), look="day", name="s46b")
# L47: I stepped out from behind the shelf
unobj("L47", "cbox")
only("L47", ["me"])
put("me", "L47", [-1.9, 27.4], 270, expr="neutral", arms=[0, 0])
go("me", "L47.1", [0.0, 28.0], yaw=90)
go("me", "L47.1+1.0", [1.6, 27.3], yaw=90)
go("me", "L47.2", [2.3, 26.6], yaw=60)
shot("L47", cm([4.6, 27.9, 1.5], [0.2, 27.8, 1.4], [4.6, 27.8, 1.5], [1.2, 27.6, 1.4], 34), look="dim", name="s47a")
only("L47.2", ["me", "dad"])
put("dad", "L47.2", [3.0, 25.3], 0, expr="startled", arms=[0, 88])
hold("L47.2", "gb2", "dad", PALM)
beat("dad", "L47.2+0.4", expr="startled")
shot("L47.2", cam(3.0, 25.3, 1.5, 1.3, lens=45, push=0.1), name="s47b")
# L48: he nearly dropped it
cue("L48", "bulb", a=0.05)
beat("dad", "L48", arms=[88, 88], expr="startled")
hold("L48", "gb2", "dad", BOTH)
hold("L48+0.3", "gb2", "dad", (0.0, -0.78, 1.0), swing=0.04, dur=0.3)
beat("dad", "L48.1", arms=[88, 88], expr="sad-smile")
hold("L48.1", "gb2", "dad", (0.0, -0.5, 1.0), dur=0.4)
shot("L48", cam(3.0, 25.1, 1.2, 1.3, az=-20, lens=40, push=0.1), name="s48a")
shot("L48.1", cam(3.0, 25.3, 1.52, 0.95, lens=50, push=0.1), name="s48b")
# L49: I asked him why
put("me", "L49", [2.3, 26.6], 60, expr="wide", arms=[0, 0], head=[0, 0])
only("L49", ["me"])
shot("L49", cam(2.3, 26.6, 1.52, 0.95, az=-60, lens=50, push=0.1), name="s49")
# L50: why would anyone buy these?
only("L50", ["me", "dad"])
beat("me", "L50", arms=[0, 150], expr="worried")
shot("L50", cam(2.4, 26.2, 1.3, 2.0, az=-45, lens=40, push=0.1), name="s50a")
beat("dad", "L50.1", head=[0, 28], expr="sad-smile")
shot("L50.1", cam(3.0, 25.3, 1.5, 1.0, lens=50, push=0.1), name="s50b")
# L51: because you called me
only("L51", ["dad"])
beat("dad", "L51", head=[0, 0], expr="sad-smile")
talk("dad", "L51", "L51>", 0.35)
shot("L51", cam(3.0, 25.3, 1.52, 0.95, lens=50, push=0.1), name="s51a")
only("L51.1", ["me"])
beat("me", "L51.1", arms=[0, 0], expr="worried")
shot("L51.1", cam(2.3, 26.6, 1.52, 0.95, az=-60, lens=50, push=0.1), name="s51b")
# L52: on every one of these days you called me (Dad touches my row, one by one)
only("L52", ["dad"])
unobj("L52", "gb2")
put("dad", "L52", [3.45, 20.4], 135, expr="sad-smile", arms=[0, 60])
sit("dad", "L52", True, 0.17)
go("dad", "L52.1+0.2", [3.45, 21.6])
go("dad", "L52.2", [3.45, 22.8])
shot("L52", cm([2.2, 23.4, 0.95], [3.45, 20.6, 0.7], [2.3, 24.8, 0.95], [3.45, 22.2, 0.7], 40), name="s52a")
shot("L52.2", cm([3.0, 17.0, 0.55], [4.3, 22.5, 0.3], [3.2, 17.8, 0.55], [4.3, 23.5, 0.3], 36), name="s52b")
# L53: car broke down, you called; locked out, you called
only("L53", ["me"])
sit("dad", "L53", False)
put("me", "L53", [CX - 2.8, -2.9], 0, expr="worried", arms=[0, 125])
hold("L53", "phone", "me", EAR)
talk("me", "L53", "L53.1", 0.6)
shot("L53", cam(CX - 2.8, -2.9, 1.4, 1.7, lens=40, push=0.12), look="day", name="s53a")
put("me", "L53.2", [RAINX, 4.8], 0, expr="laugh", arms=[0, 125])
talk("me", "L53.2", "L53.3", 0.6)
shot("L53.2", cam(RAINX, 4.8, 1.4, 1.7, lens=40, push=0.12), look="rain", name="s53b")
only("L53.3", ["dad"])
unobj("L53.3", "phone")
put("dad", "L53.3", [KX + 2.4, 7.6], 180, expr="soft", arms=[0, 125])
hold("L53.3", "handset", "dad", EAR)
shot("L53.3", cam(KX + 2.4, 7.6, 1.45, 1.8, az=180, lens=40, push=0.12), look="day", name="s53c")
# L54: the bad days are the only days you ever call
only("L54", ["dad"])
unobj("L54", "handset")
put("dad", "L54", [3.0, 25.3], 0, expr="sad-smile", arms=[0, 0])
shot("L54", cam(3.0, 25.3, 1.52, 0.95, lens=50, push=0.1), look="dim", name="s54a")
only("L54.1", ["me"])
put("me", "L54.1", [2.3, 26.6], 60, expr="worried", arms=[0, 0], head=[0, 10])
shot("L54.1", cam(2.3, 26.6, 1.52, 0.95, az=-60, lens=50, push=0.1), name="s54b")
# L55: every time you returned one, the call went with it
only("L55", ["me", "tulley"])
put("me", "L55", [MX, MY], 180, expr="soft", arms=[0, 0])
put("tulley", "L55", [TX, TY], 0, expr="polite", arms=[0, 0])
hold("L55", "shim", "me", (0.0, 0.4, 1.1))
hold("L55.1", "shim", "me", (0.0, 1.0, 1.9), dur=0.7)
unobj("L55.2", "shim")
shot("L55", cam(-1.5, 3.4, 1.35, 2.4, az=90, el=6, lens=40, push=0.1), look="night", name="s55a")
only("L55.2", [])
world("L55.2", "handset", [KX + 2.4, 8.7, 0.95], swing=0.13)
shot("L55.2", cam(KX + 2.4, 8.6, 1.1, 1.2, lens=45, push=0.12), look="day", name="s55b")
# L56: so he bought them back
unobj("L56", "handset")
only("L56", ["dad", "tulley"])
put("dad", "L56", [MX, MY], 180, expr="sad-smile", arms=[0, 0])
put("tulley", "L56", [TX, TY], 0, expr="knowing", arms=[0, 0])
world("L56", "coins2", [MX + 0.1, 3.0, 1.004], rz=10)
world("L56+0.4", "coins2", [-1.5, 3.5, 1.004], rz=10, dur=0.5)
shot("L56", cam(MX, 3.1, 1.3, 1.9, az=90, lens=40, push=0.1), look="night", name="s56a")
unobj("L56.1", "coins2")
beat("tulley", "L56.1", arms=[88, 88], expr="knowing")
hold("L56.1", "gb3", "tulley", BOTH)
world("L56.1+0.8", "gb3", [-1.8, 3.45, 1.0], dur=0.4)
shot("L56.1", cam(TX, TY, 1.52, 1.0, lens=45, push=0.1), name="s56b")
only("L56.2", ["dad"])
unobj("L56.2", "gb3")
put("dad", "L56.2", [-2.0, -6.2], 90, expr="soft", arms=[0, 40])
hold("L56.2", "gb3", "dad", (0.5, -0.35, 1.0))
go("dad", "L56>", [3.0, -6.2], yaw=90)
shot("L56.2", cam(0.5, -6.2, 1.2, 3.4, az=15, lens=40, push=0.1, sh=(1.5, 0, 0)), name="s56c")
# L57: forty-seven phone calls, about flat tires, about the rain
only("L57", [])
unobj("L57", "gb3")
shot("L57", cam(KX + 4.7, 8.8, 1.7, 3.0, lens=40, push=0.12), look="day", name="s57a")
shot("L57.1", cam(KX + 2.4, 8.8, 1.7, 0.9, lens=50, push=0.12), name="s57b")
put("dad", "L57.2", [KX - 1.0, 6.0], 0, expr="soft", arms=[0, 0])
shot("L57.2", cam(KX - 1.0, 4.8, 1.2, 3.2, lens=40, push=0.12), name="s57c")
# L58: two years of me on a shelf (Dad opens a box at his table)
only("L58", ["dad"])
put("dad", "L58", [KX - 1.0, 6.0], 0, expr="smile", arms=[0, 0])
sit("dad", "L58", True, 0.52)
world("L58", "gb3", [KX - 1.0, 4.8, 0.86], rz=0)
cue("L58", "lid", b=0.0)
cue("L58+0.2", "lid", b=100.0, dur=0.6)
cue("L58", "glow", x=KX - 1.0, y=4.9, z=1.3, g=0.0)
cue("L58+0.2", "glow", x=KX - 1.0, y=4.9, z=1.3, g=1.0, dur=0.6)
shot("L58", cam(KX - 1.0, 5.5, 1.15, 1.7, lens=40, push=0.1, el=6), name="s58a")
shot("L58.1", cam(KX - 1.0, 6.0, 1.35, 0.95, lens=50, push=0.1), name="s58b")
# L59: I thought we'd just stopped talking
only("L59", ["me"])
unobj("L59", "gb3")
cue("L59", "glow", x=0, y=0, z=-50, g=0.0)
sit("dad", "L59", False)
put("me", "L59", [2.3, 26.6], 60, expr="sad-smile", arms=[0, 0], head=[0, 10])
shot("L59", cam(2.3, 26.6, 1.52, 0.95, az=-60, lens=50, push=0.1), look="dim", name="s59a")
only("L59.1", [])
world("L59.1", "phone", [APX + 3.8, 7.5, APZ + 1.06], rx=90, rz=0)
shot("L59.1", cam(APX + 3.8, 7.5, APZ + 1.06, 0.9, el=50, lens=40, push=0.12), look="day", name="s59b")
# L60: we hadn't, I just kept giving it back
unobj("L60", "phone")
only("L60", ["me"])
put("me", "L60", [3.4, 20.0], 90, expr="sad-smile", arms=[0, 0], head=[0, 14])
shot("L60", cm([2.2, 18.0, 1.2], [4.3, 21.0, 0.5], [2.4, 18.8, 1.2], [4.3, 21.0, 0.5], 40), look="dim", name="s60a")
only("L60.1", ["dad"])
put("dad", "L60.1", [3.0, 25.3], 0, expr="sad-smile", arms=[88, 88])
hold("L60.1", "gb2", "dad", BOTH)
hold("L60.1+0.8", "gb2", "dad", (0.0, -1.1, 1.2), dur=0.7)
shot("L60.1", cam(3.0, 25.0, 1.3, 1.5, lens=45, push=0.12), name="s60b")

# ---------------------------------------------------------------------------------------------- 05 I kept it (L61 to L71)
# L61: today was a bad day too
only("L61", ["me"])
unobj("L61", "gb2")
put("me", "L61", [2.3, 26.6], 60, expr="soft", arms=[0, 0], head=[0, 10])
beat("me", "L61+0.2", arms=[0, 140], head=[0, 14])
shot("L61", cam(2.3, 26.6, 1.52, 0.9, az=-60, lens=50, push=0.12), name="s61")
# L62: I found out I don't call my Dad on the good ones
only("L62", ["me", "dad"])
bdoor("L62-0.3", -165, dur=0.3)
put("me", "L62", [2.1, 11.2], 0, expr="soft", arms=[0, 0])
put("dad", "L62", [3.03, 11.2], 0, expr="soft", arms=[0, 0])
shot("L62", cm([2.4, 6.6, 1.7], [2.57, 11.2, 1.55], [2.5, 6.9, 1.7], [2.57, 11.2, 1.55], 32), look="dim", name="s62a")
only("L62.2", ["me"])
beat("me", "L62.2", arms=[88, 88], expr="soft")
hold("L62.2", "phone", "me", (0.0, -0.45, 1.5))
shot("L62.2", cam(2.1, 11.2, 1.5, 0.95, az=0, lens=50, push=0.1), name="s62b")
bdoor("L63", 0, dur=0.5)
# L63: but I didn't return it
only("L63", ["me"])
unobj("L63", "phone")
put("me", "L63", [-4.2, 1.8], 0, expr="soft", arms=[0, 88])
hold("L63", "rcp", "me", PALM)
shot("L63", cam(-4.0, 1.4, 1.3, 1.1, lens=45, az=15, push=0.12), look="day", name="s63a")
world("L63.1", "rcp", [-5.4, 1.6, 1.3], dur=0.5, hop=0.25)
unobj("L63.1+0.55", "rcp")
shot("L63.1", cm([-2.4, -0.2, 1.7], [-5.0, 1.6, 1.0], [-2.8, 0.0, 1.7], [-5.0, 1.6, 0.9], 40), name="s63b")
# L64: I kept it (the key line grows into the tag)
beat("me", "L64", arms=[0, 0], expr="smile", head=[0, 0])
cue("L64", "kept", k=0.0)
cue("L64+0.05", "kept", k=1.0, dur=0.3)
shot("L64", cam(-4.2, 1.8, 1.5, 0.95, lens=50, push=0.14), name="s64")
# L65: I drove him home
only("L65", ["dad"])
shot("L65", cam(HX - 1.0, -3.0, 0.9, 5.0, az=-30, lens=40, push=0.1), look="night", name="s65a")
put("dad", "L65+0.3", [HX - 2.3, -2.6], 90, expr="soft", arms=[0, 40])
hold("L65+0.3", "gb2", "dad", (0.5, -0.35, 1.0))
go("dad", "L65>", [HX + 1.0, 3.6], yaw=0)
shot("L65+0.3", cam(HX - 0.2, -0.6, 1.3, 4.6, az=-10, lens=40, push=0.1), name="s65b")
# L66: and we talked till two in the morning
only("L66", ["dad", "me"])
unobj("L66", "gb2")
put("dad", "L66", [KX - 1.0, 5.7], 0, expr="laugh", arms=[0, 0])
put("me", "L66", [KX - 1.0, 3.9], 180, expr="laugh", arms=[0, 0])
sit("dad", "L66", True, 0.52)
sit("me", "L66", True, 0.52)
beat("dad", "L66.1", expr="smile")
beat("me", "L66.1+0.3", expr="laugh", head=[0, 6])
shot("L66", cam(KX - 1.0, 4.8, 1.3, 2.7, lens=28, push=0.05, az=85), look="day", name="s66a")
only("L66.1", [])
shot("L66.1", cam(KX + 2.4, 8.86, 1.78, 0.7, lens=50, push=0.08, sh=(0, 0, -0.04)), name="s66b")
shot("L66.1+0.9", cam(KX + 0.9, 8.95, 2.35, 1.2, lens=45, push=0.1), name="s66c")
# L67: the first one he didn't have to buy
only("L67", ["dad"])
sit("dad", "L67", True, 0.52)
put("dad", "L67", [KX - 1.0, 6.0], 0, expr="laugh", arms=[0, 140])
shot("L67", cam(KX - 1.0, 6.0, 1.45, 0.95, lens=50, push=0.1), name="s67a")
only("L67.1", ["me"])
sit("dad", "L67.1", False)
put("me", "L67.1", [KX - 1.0, 3.6], 180, expr="soft", arms=[0, 0])
sit("me", "L67.1", True, 0.52)
shot("L67.1", cam(KX - 1.0, 3.6, 1.42, 0.95, az=180, lens=50, push=0.1), name="s67b")
# L68: tomorrow is a good day
only("L68", ["me"])
sit("me", "L68", False)
put("me", "L68", [APX, 5.0, APZ], 0, expr="smile", arms=[170, 170])
beat("me", "L68.1", arms=[10, 10], expr="grin")
shot("L68", cam(APX, 5.0, APZ + 1.4, 2.2, lens=40, push=0.12), look="day", name="s68")
# L69: I'm calling him anyway
put("me", "L69", [APX - 1.0, 4.6, APZ], 0, expr="grin", arms=[0, 125])
hold("L69", "phone", "me", EAR)
talk("me", "L69", "L69>", 0.6)
shot("L69", cam(APX - 1.0, 4.6, APZ + 1.45, 1.2, lens=45, push=0.12), name="s69a")
only("L69.0+0.9", ["dad"])
unobj("L69.0+0.9", "phone")
put("dad", "L69.0+0.9", [KX + 2.4, 7.6], 180, expr="startled", arms=[0, 125])
hold("L69.0+0.9", "handset", "dad", EAR)
beat("dad", "L69.0+0.95", expr="grin")
shot("L69.0+0.9", cam(KX + 2.4, 7.6, 1.45, 1.5, az=180, lens=45, push=0.12), name="s69b")
# L70: when we walk past Tulley's now
only("L70", ["dad", "me"])
unobj("L70", "handset")
put("dad", "L70", [-4.3, -6.1], 90, expr="smile", arms=[0, 0])
put("me", "L70", [-3.3, -6.1], 90, expr="smile", arms=[0, 0])
go("dad", "L70.1+0.9", [-2.2, -6.1])
go("me", "L70.1+0.9", [-0.9, -6.1])
shot("L70", cam(-3.8, -6.1, 1.4, 2.8, az=-10, lens=40, push=0.0, sh=(0.5, 0, 0)), name="s70a")
put("tulley", "L70.1", [1.9, -2.6], 0, expr="knowing", arms=[0, 150])
visible.add("tulley")
beat("tulley", "L70.1+0.5", arms=[0, 135])
shot("L70.1", cam(1.9, -3.4, 1.5, 1.5, az=0, lens=40, push=0.1), name="s70b")
# L71: Dad taps the window and reads me the fine print (and the loop back to the counter)
only("L71", ["dad", "tulley"])
put("dad", "L71", [2.0, -5.0], 180, expr="laugh", arms=[0, 100])
beat("dad", "L71.1+0.2", arms=[0, 88])
beat("dad", "L71.1+0.5", arms=[0, 100])
beat("dad", "L71.1+0.8", arms=[0, 88])
shot("L71", cam(2.0, -4.9, 1.5, 1.5, az=180, lens=45, push=0.1), name="s71a")
only("L71.2", [])
world("L71.2", "rcp", [-3.4, 3.2, 1.012], rz=-25)
cue("L71.2", "ring", v=0.0)
world("L71.3", "rcp", [-3.1, 3.3, 1.012], rz=-25, dur=0.6)
shot("L71.2", cam(-2.3, 3.6, 1.12, 1.9, az=15, el=22, push=0.1), name="s71b")

# ---------------------------------------------------------------------------------------------- finish
cue(0, "lamps", a=1.0, b=1.0, c=1.0)
cue(0, "kept", k=0.0)
cue(0, "ring", v=0.0)
cue(0, "coins", v=0.0)
cue(0, "stain", v=1.0)
cue(0, "mbx", f=0.0)
cue(0, "lid", a=0.0, b=0.0, c=0.0)
cue(0, "glow", x=0.0, y=0.0, z=-50.0, g=0.0)
cue(0, "flick", u=0.0)
cue(0, "mag", u=0.0)
cue(0, "pulse", p=0.0)
cue(0, "bulb", a=0.06)
cue(0, "fdoor", a=0.0)
cue(0, "bdoor", a=0.0)
# gb2 stands in its shelf slot until it is lifted
world(0, "gb2", [4.55, 26.2, 0.1], rz=90)
for k_ in acting.values():
    remap_all(k_)
remap_all(cues)
shots, names = [], {}
for i, (at, camera, step, hand, follow, nm) in enumerate(SH):
    s = {"id": f"S{i + 1:02d}", "cam": camera, "step": step}
    if i:
        s["at"] = remap(at)
    shots.append(s)
    names[nm] = s["id"]

sfx = [
    {"at": "L01.4-0.1", "kind": "thud", "db": -9},
    {"at": "L19.1+0.5", "kind": "thud", "db": -19},
    {"at": "L31.1", "kind": "creak", "db": -16, "dur": 1.3},
    {"at": "L38+0.3", "kind": "ding", "db": -17, "pitch": 1320, "dur": 1.2, "lp": 3200},
    {"at": "L43", "kind": "whistle", "db": -20, "dur": 1.5, "pitch": 760, "name": True},
    {"at": "L14.1+0.5", "kind": "door", "db": -20},
    {"at": "L63.1+0.5", "kind": "thud", "db": -24},
]
music = {
    "root": 48, "mode": "major", "bpm": 104, "seed": 107,
    "sections": [
        {"at": 0, "voices": ["pulse", "pad"], "energy": 0.5, "root": 48, "mode": "major"},
        {"at": "L19", "voices": ["pad", "drone"], "energy": 0.38, "root": 48, "mode": "minor"},
        {"at": "L29", "voices": ["drone", "pulse"], "energy": 0.32, "root": 43, "mode": "minor"},
        {"at": "L44", "voices": ["piano", "pad"], "energy": 0.36, "root": 48, "mode": "major"},
        {"at": "L61", "voices": ["pulse", "pad", "piano"], "energy": 0.5, "root": 48, "mode": "major"},
        {"at": "L65", "voices": ["piano", "pad", "pulse", "choir"], "energy": 0.68, "root": 48, "mode": "major"},
    ],
}
sound = {
    "floor": "wood", "steps_db": -24,
    "ambience": [{"kind": "traffic", "from": 0, "to": "L29", "lufs": -46},
                 {"kind": "room", "from": "L29", "to": "L60", "lufs": -40},
                 {"kind": "traffic", "from": "L65", "to": "end", "lufs": -46}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L44")], "twist": remap("L44"),
          "emph": [remap(x) for x in ["L03.2", "L08", "L12", "L19.1", "L26", "L33.2", "L38.1", "L44", "L45.1", "L54.2", "L64"]],
          "quiet": [[remap("L66"), remap("L67")]],
          "sway": [names[n] for n in ("s39", "s40a", "s41a", "s41b", "s42b", "s43a")],
          "hold": [names["s45a"], names["s62a"], names["s66b"]]}
story = {
    "slug": "ep107-returned-days",
    "title": "Someone Buys My Bad DAYS \U0001f9fe",
    "made_for_kids": False,
    "premise": ("At a returns shop in a sunny town you can hand back a bad day before midnight and it never happened, "
                "but the fine print says returned days are restocked and sold, and I find that somebody has bought "
                "every one of the 47 I returned."),
    "twist": ("My dad has been buying my returned bad days for four dollars each, because the bad days were the only "
              "days I ever called him, and every return took the call away; I keep today and drive him home."),
    "world": ("A mint-and-cream returns shop with a long counter, a brass bell and a stamp, a dim back room of tall "
              "shelves of little gray boxes you can hear, and a small yellow kitchen with an old wall phone."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#e2463c",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#cfe6f5", "fog_density": 0.002, "fog_start": 40.0, "sky": "#8fd3ff",
             "sky_strength": 1.0, "exposure": 0.0, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.2, "grain": 0.008},
    "phonemes": {"Oduya": "ˌOdˈujə"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "rain_shots": [names["s22"], names["s53b"]],
    "set_moves": [],
    "clip_ok": ["mbx", "van", "S09", "S10", "bk"],
    "asr_forgive": ["mister tulley", "tulley's", "tulley", "mister", "missus", "returned", "dollars", "i've", "we'd", "every", "one", "unhappens"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
print({k: v for k, v in names.items()})
