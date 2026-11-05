"""Writes ../story.json for ep113 "moon lake" (script.md, 2026-11-04). Run: python stories/ep113-moon-lake/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90. Time references use the script's chunk numbers (captions are split to two or three words and the
references are remapped). The moon is never built whole: a rising cap, a patch of the lake bed, glows and reflections.
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
# the 0.7 s music drop before L21
idx = next(i for i, l in enumerate(lines) if l["id"] == "L21")
lines.insert(idx, {"id": "P01", "pause": 0.7, "chunks": [["", ""]]})


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
WZ, DECK = G.WZ, G.DECK
MX, MY = G.MID
UX, UY = G.U
UT = G.UTOP


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
    "me": person("#dca97c", "#f08a2a", "#2f5fc4", "#dca97c", hair="mop", hair_c="#6b4a2e", sleeves="none", brow_w=1.7),
    "grandma": person("#f0c8a0", "#f5f2ec", "#1f2f6a", "#f5f2ec", hair="mop", hair_c="#f4f4f6", eyes="lashes",
                      sleeves="long", brow_w=1.4, width=0.96, face={"eyes": "lashes", "brows": True, "ink": "#1c120c",
                                                                     "cheeks": "#f2a0a0"}),
    "nb1": person("#e6b48c", "#ffb84a", "#f6f0e6", "#e6b48c", hair="long", hair_c="#7a4a2c", eyes="lashes", sleeves="none",
                  brow_w=1.7),
    "nb2": person("#d3a07a", "#3f7a5a", "#7a6a50", "#4a3626", hair="buzz", hair_c="#e8e8ea", hat="bucket",
                  hat_c="#8a9a5a", extras=["glasses"], extra_c="#3a3a3e", sleeves="short"),
    "s1": person("#b98456", "#e8493a", "#2f5fc4", "#b98456", hair="buzz", hair_c="#1a1410", sleeves="none"),
    "s2": person("#f0c8a0", "#2fa8a0", "#ffd23f", "#f0c8a0", hair="long", hair_c="#c89a5a", eyes="lashes", sleeves="none"),
    "s3": person("#8a5a3a", "#ffd23f", "#e8493a", "#8a5a3a", hair="spiky", hair_c="#150f0c", sleeves="none"),
    "s4": person("#e8b890", "#8a5ab0", "#2fa8a0", "#e8b890", hair="swoop", hair_c="#a05a2a", sleeves="none"),
}
DEF = {"lean": 0.0, "arms": [0, 0], "side": [0, 0], "head": [0, 0], "yaw": 0, "expr": "neutral"}
# every attribute starts at its default: the engine holds the FIRST key's value before a key that sets it, so a later
# "lean": 165 would otherwise turn the character upside down from frame 0
acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0], **DEF}] for n in cast}
last = {n: [0, 0, 0] for n in cast}
visible = set()
cues = []
SH = []


def put(who, at, pos, yaw=None, **kw):
    p = list(pos)
    if len(p) == 2:
        p.append(0.0)
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False, "lean": 0.0, "arms": [0, 0], "side": [0, 0], "head": [0, 0]}
    if yaw is not None:
        k["yaw"] = yaw
    k.update(kw)
    acting[who].append(k)
    last[who] = p
    visible.add(who)


def go(who, at, pos, **kw):
    p = list(pos)
    if len(p) == 2:
        p.append(0.0)
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


def shot(at, camera, name=None, hand=None, follow=None, step=2):
    SH.append((at, camera, step, hand, follow, name))


def sit(who, at, on=True, z=0.3):
    cue(at, "sit", who=who, on=on, z=z)


def look(at, id_, dur=0.0):
    cue(at, "look", id=id_, dur=dur)


def dial(at, v, lit=None, dur=0.0):
    kw = {"v": v}
    if lit is not None:
        kw["lit"] = lit
    cue(at, "dial", dur=dur, **kw)


def zoom(at, z, oy=0.0):
    cue(at, "tagzoom", z=z, oy=oy)


def glow(at, g=None, z=None, e=None, disc=None, dur=0.0):
    kw = {}
    if g is not None:
        kw["g"] = g
    if z is not None:
        kw["z"] = z
    if e is not None:
        kw["e"] = e
    if disc is not None:
        kw["disc"] = disc
    cue(at, "glow", dur=dur, **kw)


def boatc(at, x=None, y=None, z=None, dur=0.0, rock=None, yaw=None):
    kw = {}
    for k, v in (("x", x), ("y", y), ("z", z), ("rock", rock), ("yaw", yaw)):
        if v is not None:
            kw[k] = v
    cue(at, "boat", dur=dur, **kw)


def moonc(at, top, dur=0.0):
    cue(at, "moon", top=top, dur=dur)


def oarc(at, a=None, b=None, dur=0.0):
    kw = {}
    if a is not None:
        kw["a"] = a
    if b is not None:
        kw["b"] = b
    cue(at, "oar", dur=dur, **kw)


def ugc(at, e=None, x=None, roll=None, z=None, dur=0.0):
    kw = {}
    for k, v in (("e", e), ("x", x), ("roll", roll), ("z", z)):
        if v is not None:
            kw[k] = v
    cue(at, "ug", dur=dur, **kw)


def F(pos, yaw, d, hz, lens, tzoff=1.45, off=14.0, push=0.1, base=DECK, tz1=None, hz1=None, dx=0.0, lens1=None):
    """A camera in front of a character: `d` metres out along where they face (turned `off` degrees), at height
    base+hz, looking at their face height. A slow push of `push`."""
    a = (yaw + off) * D2R
    sx, sy = math.sin(a), -math.cos(a)
    px, py = pos[0], pos[1]
    p0 = [px + dx + sx * d, py + sy * d, base + hz]
    d1 = d * (1 - push)
    p1 = [px + dx + sx * d1, py + sy * d1, base + (hz1 if hz1 is not None else hz)]
    t0 = [px, py, base + tzoff]
    t1 = [px, py, base + (tz1 if tz1 is not None else tzoff)]
    return mv(p0, t0, lens, p1, t1, lens1 or lens)


def FL(off0, tgt0, lens, off1=None, tgt1=None, lens1=None):
    """A camera that follows a character: offsets from their root (use with shot(..., follow=who))."""
    return mv(off0, tgt0, lens, off1 or off0, tgt1 or tgt0, lens1 or lens)


# who is where in the boat: the boat's centre (bx, by, bz); the bench is at +0.25 along y
def inboat(bx, by, bz):
    return [bx, by + 0.25, bz + 0.18]


GRAN_BENCH_Z = 0.30


# ---------------------------------------------------------------------------------------------- the film
cue(0, "look", id="day", dur=0)
cue(0, "dial", v=0.56, lit=0.0)
cue(0, "glow", g=0.6, z=-1.0, e=0.0, disc=1.0)
cue(0, "moon", top=-3.0)
cue(0, "boat", x=G.BOAT_HOME[0], y=G.BOAT_HOME[1], z=WZ, rock=0.0, yaw=0.0)
cue(0, "oar", a=80.0, b=0.0)
cue(0, "feet", on=0.0)
cue(0, "refl", v=0.0)
cue(0, "pour", p=0.0)
cue(0, "tagzoom", z=0.0, oy=0.0)
cue(0, "steam", lake=0.0, mug=0.0)
cue(0, "gdock", on=0.0)
cue(0, "fish", on=0.0)
cue(0, "bubbles", on=0.0)
cue(0, "ug", e=60.0, x=0.0, roll=0.0, z=3.0)

# ===== 01 the rule and the moon (L01 to L03)
cue(0, "feet", on=1.0)
cue(0, "gdock", on=1.0)
shot(0, mv([1.9, -26.6, 0.45], [0.45, -29.5, 0.3], 30, [1.7, -26.8, 0.45], [0.45, -29.5, 0.3], 30), "feet")
cue("L01.2", "feet", on=0.0)
look("L01.2", "day")
put("me", "L01.2", [0.3, -32.2, DECK], 180, expr="squeeze", head=[0, 6])
shot("L01.2", F([0.3, -32.2], 180, 3.7, 1.7, 36, tzoff=1.55, push=0.12), "hotface")
shot("L01.3", mv([-2.5, -26.5, 1.2], [1.5, -18.0, 0.1], 30, [-1.3, -24.5, 1.4], [1.5, -18.0, 0.1], 30), "glow1")
glow("L01.3", g=1.0, dur=1.2)
cue("L01.3", "gdock", on=0.0)
only("L02", [])
cue("L02", "feet", on=1.0)
cue("L02", "gdock", on=1.0)
shot("L02", mv([0.45, -26.2, 0.5], [0.45, -29.6, 0.25], 30, [0.45, -26.8, 0.5], [0.45, -29.6, 0.3], 30), "steam")
shot("L02.2", mv([-3.4, -30.5, 1.1], [1.5, -18.0, 0.1], 30, [-2.4, -29.5, 1.2], [1.5, -18.0, 0.1], 30), "glow2")
glow("L02.2", g=1.1, dur=1.2)
cue("L03", "feet", on=0.0)
cue("L03", "gdock", on=0.0)
put("grandma", "L03", [0.4, -33.0, DECK], 180, expr="neutral", head=[0, 0])
beat("grandma", "L03.0+0.5", head=[0, 14])
shot("L03", F([0.4, -33.0], 180, 4.4, 1.8, 36, tzoff=1.5, push=0.1), "grannod")
shot("L03.2", mv([1.5, -22.5, 14.0], [1.5, -18.0, 0.0], 22, [1.5, -20.0, 8.0], [1.5, -18.0, 0.0], 22), "pushdown")

# ===== 02 the rule at work (L04 to L08)
only("L04", ["s1", "s2", "s3"])
dial("L04", 0.22, dur=0.01)
glow("L04", g=0.7)
put("s1", "L04", [-5.4, -27.0, -0.7], 150, expr="grin", arms=[0, 0])
put("s2", "L04", [3.6, -27.5, -0.7], 200, expr="smile")
put("s3", "L04", [-2.2, -23.0, -0.7], 170, expr="grin")
go("s1", "L04.2", [-4.6, -26.2, -0.7], yaw=150, keep_yaw=True)
shot("L04", mv([0.5, -21.0, 1.3], [-3.5, -26.0, 0.8], 30, [0.2, -21.4, 1.3], [-3.5, -26.0, 0.8], 30), "widelake")
# L05: the watch at 11:59, then the swimmers climbing out in a line
only("L05", [])
dial("L05", 0.5, dur=0.01)
shot("L05", mv([200.0, -105.0, 3.4], [200.0, -100.0, 1.7], 38, [200.0, -103.5, 3.2], [200.0, -100.0, 1.7], 38), "watch")
bx0, by0 = G.BEACH
only("L05.1", ["s1", "s2", "s3", "s4"])
for i, who in enumerate(["s1", "s2", "s3", "s4"]):
    st = [bx0 + 7.0 - i * 1.4, by0 + 5.2 - i * 1.0, -0.9]
    put(who, "L05.1", st, -54, expr=["grin", "smile", "grin", "smile"][i])
    go(who, "L05.1+0.9", [bx0 + 2.4 - i * 1.4, by0 + 1.7 - i * 1.0, 0.1], yaw=-54)
    go(who, "L05>", [bx0 - 1.0 - i * 1.4, by0 - 0.7 - i * 1.0, 0.1], yaw=-54)
shot("L05.1", mv([bx0 - 6.5, by0 - 5.5, 1.9], [bx0 + 2.0, by0 + 1.6, 1.4], 30, [bx0 - 5.2, by0 - 4.8, 1.8], [bx0 + 1.0, by0 + 0.9, 1.4], 30), "swimmers")
# L06: the fish swim to the middle (under water)
only("L06", [])
look("L06", "under")
glow("L06", g=0.0)
cue("L06", "fish", on=1.0)
ugc("L06", e=90.0, z=1.5, x=1.0)
shot("L06", mv([UX - 6.0, UY - 10.0, G.UFLOOR + 7.0], [UX - 6.0, UY - 3.0, G.UFLOOR + 7.2], 26, [UX - 4.0, UY - 10.0, G.UFLOOR + 7.0], [UX - 4.0, UY - 3.0, G.UFLOOR + 7.2], 26), "fish1")
shot("L06.2", mv([UX - 3.0, UY + 9.5, G.UFLOOR + 7.2], [UX - 3.0, UY + 2.0, G.UFLOOR + 7.4], 26, [UX - 1.0, UY + 9.5, G.UFLOOR + 7.2], [UX - 1.0, UY + 2.0, G.UFLOOR + 7.4], 26), "fish2")
# L07: coffee from the lake
look("L07", "day")
glow("L07", g=0.6)
cue("L07", "fish", on=0.0)
x1, y1 = G.NDOCK1
only("L07", ["nb1"])
put("nb1", "L07", [x1 + 0.2, y1 - 0.2, DECK], 180, expr="smile", arms=[40, 40], lean=24)
beat("nb1", "L07.0+0.7", lean=34, arms=[55, 55])
shot("L07", F([x1 + 0.2, y1 - 0.2], 180, 5.4, 1.6, 32, tzoff=1.2, off=26, push=0.1), "pot")
cue("L07.2", "steam", mug=1.0)
only("L07.2", [])
shot("L07.2", mv([x1 - 2.5, y1 - 4.6, DECK + 1.6], [x1 - 0.9, y1 - 3.0, DECK + 1.45], 38, [x1 - 2.1, y1 - 4.3, DECK + 1.65], [x1 - 0.9, y1 - 3.0, DECK + 1.55], 38), "mug")
# L08: the moon comes up over the dock every night
cue("L08", "steam", mug=0.0)
look("L08", "night", dur=0.01)
glow("L08", g=0.0)
cue("L08", "refl", v=0.8)
dial("L08", 0.97, lit=1.0)
shot("L08", mv([0.4, -20.5, 6.5], [0.3, -27.8, 0.2], 24, [0.4, -21.5, 6.0], [0.3, -27.6, 0.2], 24), "reflect")
shot("L08.2", mv([0.0, -34.5, 3.4], [0.3, -27.0, 0.1], 28, [0.1, -33.5, 3.0], [0.3, -27.0, 0.1], 28), "boards")

# ===== 03 Grandma Nell and what I notice (L09 to L14)
cue("L09", "refl", v=0.0)
look("L09", "day", dur=0.01)
dial("L09", 0.2, lit=0.0)
glow("L09", g=0.6)
only("L09", ["me", "grandma"])
put("grandma", "L09", [0.3, -45.0, DECK], 0, expr="smile", arms=[0, 150])
put("me", "L09", [-1.8, -57.0, 0.0], 160, expr="smile")
go("me", "L09.1+0.6", [-1.0, -50.5, 0.0], yaw=160)
beat("grandma", "L09.1", arms=[0, 120])
shot("L09", F([0.3, -45.0], 0, 3.8, 1.75, 34, tzoff=1.55, off=14, push=0.1), "waveme")
shot("L09.1", FL([1.0, 3.3, 1.75], [0.0, 0.0, 1.5], 34, [0.8, 2.9, 1.7]), "comes", follow="me")
# L10: tying on her visor, then rowing out at dusk
only("L10", ["grandma"])
put("grandma", "L10", [0.4, -31.5, DECK], 180, expr="smile", arms=[150, 150], head=[0, 0])
beat("grandma", "L10.0+0.9", arms=[0, 0])
shot("L10", F([0.4, -31.5], 180, 3.9, 1.8, 36, tzoff=1.6, push=0.1), "visor")
look("L10.1", "dusk", dur=0.01)
dial("L10.1", 0.93, lit=0.0)
glow("L10.1", g=0.9)
only("L10.1", ["grandma"])
bxh, byh = G.BOAT_HOME
boatc("L10.1", x=bxh, y=byh, z=WZ)
sit("grandma", "L10.1", True, GRAN_BENCH_Z)
put("grandma", "L10.1", inboat(bxh, byh, WZ), 0, expr="neutral", keep_yaw=True)
for k_, (tt, ang) in enumerate([("L10.1", 0), ("L10.1+0.8", 25), ("L10.1+1.6", -20)]):
    oarc(tt, a=70.0, b=ang, dur=0.7)
boatc("L10.1+0.2", x=MX + 1.0, y=MY - 5.0, dur=3.4)
go("grandma", "L10>", inboat(MX + 1.0, MY - 5.0, WZ), yaw=0, keep_yaw=True)

shot("L10.1", FL([1.9, -5.2, 1.0], [0.0, 0.0, 1.0], 34, [1.5, -4.6, 1.0]), "rowout", follow="grandma")
# L11: the oar, scuffed silver all down one side
sit("grandma", "L11", False)
only("L11", [])
boatc("L11", x=bxh, y=byh, z=WZ)
look("L11", "day", dur=0.01)
dial("L11", 0.2, lit=0.0)
oarc("L11", a=172.0, b=0.0)
shot("L11", mv([bxh + 0.9, byh - 3.3, 1.9], [bxh + 0.75, byh + 0.25, 1.9], 24, [bxh + 1.0, byh - 2.8, 2.0], [bxh + 0.75, byh + 0.25, 2.0], 24), "oar")
# L12: checking her fishing lines
only("L12", ["grandma"])
put("grandma", "L12", [0.4, -33.0, DECK], 180, expr="neutral", arms=[0, 90], head=[0, 10])
beat("grandma", "L12.0+0.8", arms=[0, 20], head=[0, 0], expr="polite")
shot("L12", F([0.4, -33.0], 180, 4.2, 1.8, 36, tzoff=1.5, off=-18, push=0.16), "fishing")
# L13: her arms shake at breakfast, L14: it's just the coffee
hx_, hy_ = G.HOUSE
tx, ty = hx_ + 3.2, G.PORCH_Y + 0.2
only("L13", ["grandma"])
sit("grandma", "L13", True, 0.42)
put("grandma", "L13", [tx - 0.1, ty - 0.9, 0.25], 180, expr="sad-smile", arms=[60, 60])
for k_ in range(14):
    acting["grandma"].append({"at": f"L13+{0.15 + k_ * 0.14:.2f}", "pos": list(last["grandma"]), "arms": [60 + (6 if k_ % 2 else -6), 60 + (-6 if k_ % 2 else 6)], "blend": 0.05})
shot("L13", mv([tx + 0.5, ty + 3.4, 1.55], [tx - 0.05, ty - 0.55, 1.1], 40, [tx + 0.4, ty + 2.8, 1.5], [tx - 0.1, ty - 0.55, 1.1], 40), "tremble")
beat("grandma", "L14", arms=[100, 100], expr="sad-smile", head=[0, 6])
beat("grandma", "L14+0.8", arms=[100, 100], head=[0, 0])
shot("L14", mv([tx + 0.9, ty + 3.6, 1.7], [tx - 0.1, ty - 0.9, 1.35], 40, [tx + 0.6, ty + 3.0, 1.65], [tx - 0.1, ty - 0.9, 1.4], 40), "lift")

# ===== 04 the hot afternoon (L15 to L22)
sit("grandma", "L15", False)
only("L15", [])
dial("L15", 0.68, lit=0.0, dur=0.01)
zoom("L15", 1.0)
shot("L15", mv([-3.0, -50.0, 1.5], [0.0, -36.0, 1.4], 32, [-1.0, -47.0, 1.6], [0.0, -36.0, 1.4], 32), "shimmer")
zoom("L15.1", 0.0)
only("L16", ["grandma"])
sit("grandma", "L16", True, 0.35)
put("grandma", "L16", [hx_ - 3.6, G.PORCH_Y + 0.5, 0.25], 180, expr="asleep")
shot("L16", F([hx_ - 3.6, G.PORCH_Y + 0.5], 180, 4.0, 1.6, 36, tzoff=1.0, base=0.25, off=-18, push=0.1), "nap")
only("L16.1", [])
sit("grandma", "L16.1", False)
glow("L16.1", g=0.8)
shot("L16.1", mv([-4.0, -34.0, 1.4], [1.5, -18.0, 0.1], 30, [-2.6, -33.0, 1.5], [1.5, -18.0, 0.1], 30), "flatlake")
# L17: three o'clock on the dial, then the run and the jump
dial("L17", 0.78, dur=0.3)
zoom("L17", 1.0)
zoom("L17.1", 0.0)
only("L17", ["me"])
put("me", "L17", [0.3, -38.5, DECK], 180, expr="grin", run=True)
go("me", "L17.1+0.8", [0.3, -31.0, DECK], run=True)
go("me", "L17.1+1.15", [0.4, -28.4, DECK + 1.1])
go("me", "L17>", [0.5, -26.6, -1.3])
shot("L17", mv([-1.9, -25.2, 1.8], [0.3, -34.0, 1.4], 36, [-1.8, -25.0, 1.7], [0.4, -29.0, 0.9], 36), "jump")
# L18: warm as a bath
put("me", "L18", [0.9, -27.0, -0.6], 180, expr="squeeze")
beat("me", "L18.1", expr="wide")
shot("L18", F([0.9, -27.0], 180, 3.8, 1.5, 36, tzoff=1.5, base=-0.6, push=0.1, off=-12), "bath")
# L19: I dove down (the lake bed)
look("L19", "under")
dial("L19", 0.78)
glow("L19", g=0.0)
ugc("L19", e=70.0, z=3.0, x=0.0)
only("L19", ["me"])
put("me", "L19", [UX - 0.6, UY - 2.0, UT + 9.0], 0, expr="wide", lean=165, arms=[160, 160])
go("me", "L19>", [UX - 0.2, UY - 1.0, UT + 2.3])
shot("L19", FL([2.2, 4.8, 0.0], [0.0, 0.0, -0.55], 28, [1.9, 4.2, 0.0]), "dive", follow="me")
# L20: under my hands the glow got brighter
put("me", "L20", [UX, UY - 0.2, UT + 0.95], 0, expr="wide", lean=84, arms=[96, 96])
ugc("L20", e=60.0)
ugc("L20+0.6", e=360.0, dur=1.2)
shot("L20", mv([UX + 1.2, UY - 4.6, UT + 4.4], [UX, UY - 0.9, UT + 0.3], 30, [UX + 0.9, UY - 4.1, UT + 4.0], [UX, UY - 0.9, UT + 0.3], 30), "hands")
# the drop: my face under water, eyes wide
only("P01", ["me"])
put("me", "P01", [UX, UY - 0.3, UT + 3.0], 0, expr="terrified", lean=8, arms=[0, 0])
cue("P01", "bubbles", on=1.0, x=1.6, y=-0.3, z=UT + 2.4)
ugc("P01", e=300.0)
shot("P01", F([UX, UY - 0.3], 0, 3.0, 1.5, 36, tzoff=1.5, push=0.12, base=UT + 3.0, off=0), "eyeswide")
# L21: something huge rolled over beneath me
cue("L21", "bubbles", on=0.0)
put("me", "L21", [UX - 1.0, UY - 0.5, UT + 4.4], 20, expr="scared", lean=40)
ugc("L21", e=40.0)
ugc("L21+0.2", roll=0.0, x=-2.0, dur=0.01)
ugc("L21+0.3", roll=40.0, x=3.0, dur=3.0)
shot("L21", FL([3.8, -3.4, -0.2], [0.0, 0.0, -1.0], 30, [3.4, -3.0, -0.2]), "rolls", follow="me")
# L22: one pale curve wider than Grandma's house
put("me", "L22", [UX + 0.5, UY + 0.5, UT + 4.8], 180, expr="wide", lean=5, arms=[0, 0])
ugc("L22", e=200.0, x=0.0, z=4.0)
shot("L22", mv([UX - 24.0, UY - 14.0, G.UFLOOR + 1.8], [UX, UY, UT + 1.6], 28, [UX - 22.0, UY - 13.0, G.UFLOOR + 2.2], [UX, UY, UT + 1.8], 28), "curve")

# ===== 05 the sky goes dark (L23 to L29)
only("L23", [])
look("L23", "dim", dur=3.0)
dial("L23", 0.8)
glow("L23", g=0.9)
shot("L23", mv([-3.0, -31.5, 1.2], [1.0, -12.0, 2.5], 26, [-2.4, -30.5, 1.3], [1.0, -12.0, 3.4], 26), "skydim")
dial("L23.2", 0.8, lit=1.0, dur=1.0)
zoom("L23.2", 1.0)
shot("L23.2", mv([4.0, -33.0, 3.0], [-4.0, -14.0, 4.0], 24, [3.3, -32.0, 3.2], [-4.0, -14.0, 4.0], 24), "dialdark")
zoom("L24", 0.0)
only("L24", ["nb2"])
x2, y2 = G.NDOCK2
put("nb2", "L24", [x2, y2, DECK], 180, expr="worried", head=[0, 0], arms=[0, 0])
beat("nb2", "L24+0.5", head=[0, -22], expr="wide")
shot("L24", F([x2, y2], 180, 4.6, 1.6, 34, tzoff=1.5, off=-14, push=0.1), "nbrlook")
# L25: swimming hard for the dock
only("L25", ["me"])
put("me", "L25", [1.0, -19.0, -0.7], 0, expr="scared")
for k_ in range(9):
    acting["me"].append({"at": f"L25+{0.1 + k_ * 0.28:.2f}", "pos": [1.0 - 0.1 * k_ * 0.2, -19.0 - 1.15 * (k_ + 1), -0.7], "arms": [150 if k_ % 2 else 20, 20 if k_ % 2 else 150], "blend": 0.12, "yaw": 0})
last["me"] = [0.8, -29.4, -0.7]
shot("L25", mv([0.0, -30.7, 1.3], [1.0, -23.0, 0.6], 40, [0.0, -30.4, 1.25], [0.95, -27.5, 0.6], 40), "swimhard")
# L26: Grandma on the dock in her robe
only("L26", ["grandma"])
put("grandma", "L26", [0.4, -31.2, DECK], 180, expr="worried", arms=[0, 0])
shot("L26", F([0.4, -31.2], 180, 4.3, 1.8, 36, tzoff=1.55, off=-12, push=0.1), "robe")
# L27: the glow sank down and went dim
only("L27", [])
glow("L27", g=0.1, dur=2.4)
shot("L27", mv([0.0, -30.7, 1.5], [1.5, -18.0, 0.1], 28, [0.2, -30.2, 1.45], [1.5, -18.0, 0.1], 28), "sank")
# L28: the sun came back
look("L28", "day", dur=2.6)
dial("L28", 0.8, lit=0.0, dur=1.2)
zoom("L28", 1.0)
shot("L28", mv([1.5, -31.0, 1.4], [1.5, -10.0, 3.0], 24, [1.5, -30.0, 1.5], [1.5, -10.0, 4.4], 24), "sunback")
zoom("L28.1", 0.0)
glow("L28.1", g=0.5)
# L29: "Not YET."
only("L29", ["grandma"])
put("grandma", "L29", [0.4, -33.0, DECK], 180, expr="neutral", head=[0, 4])
beat("grandma", "L29.2", expr="polite")
shot("L29", F([0.4, -33.0], 180, 3.6, 1.7, 40, tzoff=1.55, off=-10, push=0.12), "stern")
shot("L29.2", F([0.4, -33.0], 180, 2.9, 1.65, 42, tzoff=1.58, off=8, push=0.1), "notyet")

# ===== 06 that night: the rise (L30 to L39)
look("L30", "dusk", dur=0.01)
dial("L30", 0.93, lit=0.0)
glow("L30", g=1.0, e=0.0)
only("L30", ["me"])
sit("me", "L30", True, 0.32)
put("me", "L30", [-11.0, -47.6, 0.0], 90, expr="worried", head=[0, 0])
shot("L30", F([-11.0, -47.6], 90, 5.4, 1.0, 36, tzoff=0.85, off=-14, base=0.0, push=0.1), "crouch")
sit("me", "L30.1", False)
only("L30.1", ["grandma"])
put("grandma", "L30.1", [0.4, -42.0, DECK], 180, expr="neutral", arms=[0, 0])
go("grandma", "L30>", [0.4, -31.0, DECK])
shot("L30.1", mv([0.6, -26.5, 1.9], [0.4, -39.0, 1.6], 34, [0.6, -27.5, 1.9], [0.4, -34.0, 1.6], 34), "walkdock")
# L31: she rows out to the middle where the glow is brightest
only("L31", ["grandma"])
sit("grandma", "L31", True, GRAN_BENCH_Z)
boatc("L31", x=bxh, y=byh, z=WZ)
put("grandma", "L31", inboat(bxh, byh, WZ), 0, expr="neutral", keep_yaw=True)
for tt, ang in [("L31", 0), ("L31+0.9", 25), ("L31+1.8", -20), ("L31+2.7", 25)]:
    oarc(tt, a=70.0, b=ang, dur=0.8)
boatc("L31+0.2", x=MX, y=MY, dur=3.4)
go("grandma", "L31.1+0.6", inboat(MX, MY, WZ), yaw=0, keep_yaw=True)
glow("L31", g=1.0, e=120.0, dur=0.5)
shot("L31", FL([1.8, -5.2, 1.0], [0.0, 0.0, 1.0], 34, [1.3, -4.6, 1.0]), "midboat", follow="grandma")
# L32: she leans the oar down into the water
oarc("L32", a=80.0, b=0.0)
oarc("L32+0.2", a=28.0, b=10.0, dur=1.4)
shot("L32", mv([MX + 0.4, MY - 4.4, 1.55], [MX, MY + 0.3, 1.25], 36, [MX + 0.2, MY - 3.9, 1.5], [MX, MY + 0.3, 1.3], 36), "lean")
# L33: and she pushed (lit from below, steady)
glow("L33", e=420.0, dur=0.8)
shot("L33", F([MX, MY + 0.25], 0, 3.6, 1.0, 36, tzoff=1.25, base=WZ + 0.18, off=8, push=0.08), "pushface")
# L34: the whole lake started to rise
moonc("L34", 0.8, dur=2.2)
cue("L34", "pour", p=1.0)
boatc("L34", z=0.8 + 0.0, dur=2.2, rock=0.5)
shot("L34", mv([MX + 2.4, MY - 4.4, 1.2], [MX, MY, 1.5], 34, [MX + 2.0, MY - 3.9, 1.1], [MX, MY, 1.8], 34), "swell")
# L35: and the moon came up out from under her boat
moonc("L35", 3.0, dur=2.6)
boatc("L35", z=3.0, dur=2.6, rock=1.0)
glow("L35", e=700.0, dur=1.2)
go("grandma", "L35", inboat(MX, MY, 0.8), yaw=0, keep_yaw=True)
go("grandma", "L35+2.6", inboat(MX, MY, 3.0), yaw=0, keep_yaw=True)
shot("L35", mv([MX + 4.6, MY - 7.8, 1.1], [MX, MY, 2.4], 44, [MX + 4.0, MY - 7.2, 1.4], [MX, MY, 3.3], 44), "heave")
# L36: water pouring off its craters, the lake lit up white
moonc("L36", 4.2, dur=2.0)
boatc("L36", z=4.2, dur=2.0, rock=0.6)
go("grandma", "L36", inboat(MX, MY, 3.0), yaw=0, keep_yaw=True)
go("grandma", "L36+2.0", inboat(MX, MY, 4.2), yaw=0, keep_yaw=True)
glow("L36", g=1.4, e=1100.0, dur=1.2)
shot("L36", mv([MX - 1.5, MY - 8.8, 1.2], [MX, MY, 3.9], 34, [MX - 1.2, MY - 8.4, 1.4], [MX, MY, 4.3], 34), "pour")
# L37: it lifted off the end of her oar and floated up into the sky (boat slides off, light climbs)
sit("grandma", "L37", True, GRAN_BENCH_Z)
boatc("L37", x=MX + 8.4, y=MY + 2.2, z=WZ, yaw=14.0, rock=0.4)
put("grandma", "L37", inboat(MX + 8.4, MY + 2.2, WZ), 0, expr="awe" if False else "wide", keep_yaw=True)
oarc("L37", a=40.0, b=6.0)
moonc("L37", 6.0)
moonc("L37+0.1", 30.0, dur=4.4)
glow("L37", z=-1.0)
glow("L37+0.2", z=22.0, e=700.0, dur=3.2)
shot("L37", mv([MX + 9.0, MY - 4.2, 0.9], [MX + 8.4, MY + 2.2, 1.3], 34, [MX + 9.0, MY - 3.4, 1.2], [MX + 8.4, MY + 2.2, 1.9], 34), "revealshot")
shot("L37.2", mv([MX + 11.2, MY - 2.8, 1.3], [MX + 8.4, MY + 2.2, 1.4], 36, [MX + 10.8, MY - 2.4, 1.5], [MX + 8.4, MY + 2.2, 2.1], 36), "lightup")
# L38: right over the dock
cue("L38", "pour", p=0.0)
look("L38", "night", dur=1.0)
glow("L38", g=0.0, e=0.0, dur=1.0)
cue("L38", "refl", v=0.8, dur=1.0)
dial("L38", 0.97, lit=1.0, dur=1.0)
only("L38", [])
shot("L38", mv([0.0, -34.5, 3.4], [0.3, -27.0, 0.1], 28, [0.1, -33.5, 3.0], [0.3, -27.0, 0.1], 28), "boards2")
# L39: Grandma rowing back, lit by moonlight
only("L39", ["grandma"])
boatc("L39", x=MX + 1.0, y=MY - 4.0, z=WZ, yaw=0.0, rock=0.0)
put("grandma", "L39", inboat(MX + 1.0, MY - 4.0, WZ), 0, expr="sad-smile", keep_yaw=True)
boatc("L39+0.2", x=bxh, y=byh - 0.5, dur=4.0)
go("grandma", "L39.2", inboat(bxh, byh - 0.5, WZ), yaw=0, keep_yaw=True)
for tt, ang in [("L39", 0), ("L39+0.9", 25), ("L39+1.8", -20), ("L39+2.7", 25)]:
    oarc(tt, a=70.0, b=ang, dur=0.8)
shot("L39", FL([1.8, -5.2, 1.0], [0.0, 0.0, 1.0], 34, [1.5, -4.6, 1.0]), "rowback", follow="grandma")
shot("L39.2", mv([bxh + 0.5, byh - 3.8, 1.4], [bxh, byh - 0.5, 1.1], 40, [bxh + 0.3, byh - 3.0, 1.35], [bxh, byh - 0.5, 1.1], 40), "rowback2")

# ===== 07 the rest of the rule (L40 to L44)
sit("grandma", "L40", False)
only("L40", ["me", "grandma"])
put("me", "L40", [0.0, -32.4, DECK], 90, expr="smile")
put("grandma", "L40", [bxh, byh + 0.25, WZ + 0.18], 0, expr="sad-smile", keep_yaw=True)
sit("grandma", "L40", True, GRAN_BENCH_Z)
shot("L40", F([0.0, -32.4], 90, 3.6, 1.7, 36, tzoff=1.55, off=-14, push=0.1), "metie")
sit("grandma", "L41", False)
only("L41", ["grandma", "me"])
put("grandma", "L41", [0.3, -33.4, DECK], 0, expr="neutral")
put("me", "L41", [-0.4, -36.4, DECK], 180, expr="worried")
beat("grandma", "L41.0+1.2", expr="sad-smile")
shot("L41", mv([2.9, -35.3, DECK + 1.7], [0.3, -33.4, DECK + 1.5], 36, [2.5, -35.1, DECK + 1.7], [0.3, -33.4, DECK + 1.5], 36), "tellsme")
shot("L41.1", F([-0.4, -36.4], 180, 3.4, 1.7, 38, tzoff=1.55, off=-40, push=0.1), "listens")
dial("L42", 0.6, lit=1.0)
zoom("L42", 1.0)
shot("L42", F([0.3, -33.4], 0, 4.6, 1.6, 34, tzoff=1.4, off=36, push=0.1), "diallit")
zoom("L43", 0.0)
only("L43", ["grandma", "me"])
sit("grandma", "L43", True, 0.15)
sit("me", "L43", True, 0.15)
put("grandma", "L43", [0.55, -30.15, DECK], 180, expr="neutral")
put("me", "L43", [-0.55, -30.15, DECK], 180, expr="worried")
shot("L43", F([0.0, -30.15], 180, 4.9, 1.2, 34, tzoff=0.95, off=0, push=0.1), "sitdock")
beat("grandma", "L44", expr="sad-smile", head=[0, -20], arms=[70, 70])
for k_ in range(8):
    acting["grandma"].append({"at": f"L44+{0.2 + k_ * 0.2:.2f}", "pos": list(last["grandma"]), "arms": [80 if k_ % 2 else 55, 55 if k_ % 2 else 80], "blend": 0.12})
shot("L44", F([0.55, -30.15], 180, 3.2, 1.15, 40, tzoff=0.95, off=-8, push=0.1), "rubarms")

# ===== 08 the week after: it doesn't move (L45 to L51)
sit("grandma", "L45", False)
sit("me", "L45", False)
look("L45", "dusk", dur=0.01)
dial("L45", 0.93, lit=0.0)
glow("L45", g=1.0, e=120.0, z=-1.0)
moonc("L45", -3.0)
cue("L45", "refl", v=0.0)
only("L45", ["me", "grandma"])
put("me", "L45", [-0.5, -30.9, DECK], 180, expr="worried")
sit("grandma", "L45", True, GRAN_BENCH_Z)
boatc("L45", x=bxh, y=byh, z=WZ, rock=0.0, yaw=0.0)
put("grandma", "L45", inboat(bxh, byh, WZ), 0, expr="neutral", keep_yaw=True)
for tt, ang in [("L45", 0), ("L45+0.8", 25), ("L45+1.6", -20)]:
    oarc(tt, a=70.0, b=ang, dur=0.7)
boatc("L45+0.2", x=MX + 1.0, y=MY - 5.0, dur=3.0)
go("grandma", "L45>", inboat(MX + 1.0, MY - 5.0, WZ), yaw=0, keep_yaw=True)
shot("L45", mv([-0.3, -26.6, 1.8], [-0.5, -30.9, 1.7], 32, [-0.3, -26.9, 1.8], [-0.5, -30.9, 1.72], 32), "weekafter")
shot("L45.2", FL([1.8, -5.2, 1.0], [0.0, 0.0, 1.0], 34, [1.5, -4.6, 1.0]), "rowsout", follow="grandma")
# L46 oar in, L47 it didn't move
boatc("L46", x=MX, y=MY, z=WZ, dur=0.01)
go("grandma", "L46", inboat(MX, MY, WZ), yaw=0, keep_yaw=True)
oarc("L46", a=80.0, b=0.0)
oarc("L46+0.2", a=28.0, b=10.0, dur=1.2)
shot("L46", mv([MX + 0.4, MY - 4.4, 1.55], [MX, MY + 0.3, 1.25], 36, [MX + 0.2, MY - 3.9, 1.5], [MX, MY + 0.3, 1.3], 36), "oarin")
shot("L47", mv([MX + 4.5, MY - 10.0, 1.6], [MX, MY, 0.8], 30, [MX + 3.8, MY - 9.0, 1.5], [MX, MY, 0.8], 30), "stillglow")
dial("L47", 0.93, lit=0.0)
zoom("L47", 0.7)
zoom("L47.0+1.0", 0.0)
beat("grandma", "L48", expr="worried", arms=[70, 70])
for k_ in range(10):
    acting["grandma"].append({"at": f"L48+{0.1 + k_ * 0.16:.2f}", "pos": list(last["grandma"]), "arms": [78 if k_ % 2 else 62, 62 if k_ % 2 else 78], "blend": 0.06})
shot("L48", F([MX, MY + 0.25], 0, 3.6, 1.0, 36, tzoff=1.25, base=WZ + 0.18, off=-8, push=0.08), "againface")
only("L49", [])
shot("L49", mv([0.0, -42.0, 1.3], [0.2, -28.0, 3.4], 26, [0.1, -40.0, 1.3], [0.2, -28.0, 4.6], 26), "darkskydock")
only("L50", ["grandma", "me"])
put("grandma", "L50", inboat(MX, MY, WZ), 0, expr="worried", head=[0, 0], arms=[70, 70], keep_yaw=True)
beat("grandma", "L50.1", head=[0, 0], expr="worried")
put("me", "L50", [-0.5, -30.9, DECK], 180, expr="worried")
shot("L50", F([MX, MY + 0.25], 0, 5.3, 0.9, 38, tzoff=1.0, base=WZ + 0.18, off=-6, push=0.1), "lookback")
only("L51", ["me"])
put("me", "L51", [-0.3, -31.2, DECK], 180, expr="squeeze", head=[0, 6])
beat("me", "L51.1", expr="neutral", head=[0, 0])
shot("L51", F([-0.3, -31.2], 180, 3.6, 1.7, 40, tzoff=1.55, off=-12, push=0.12), "think")

# ===== 09 the climax: I swim (L52 to L64)
dial("L52", 0.93, lit=0.0)
put("me", "L52", [0.0, -31.6, DECK], 180, expr="grin", run=True)
go("me", "L52+0.5", [0.1, -29.8, DECK + 0.9])
go("me", "L52>", [0.2, -27.4, -1.4])
shot("L52", mv([0.1, -24.0, 1.6], [0.0, -31.2, 2.4], 36, [0.1, -24.0, 1.5], [0.1, -29.0, 1.6], 36), "dive2")
# L53: straight down into the glow
look("L53", "under")
glow("L53", g=0.0, e=0.0)
moonc("L53", -3.0)
only("L53", ["me"])
ugc("L53", e=80.0, z=3.0, x=0.0)
put("me", "L53", [UX, UY, UT + 11.0], 0, expr="determined" if False else "squeeze", lean=165, arms=[165, 165])
go("me", "L53>", [UX, UY, UT + 2.0])
shot("L53", FL([2.2, 4.8, 0.0], [0.0, 0.0, -0.9], 28, [1.9, 4.2, 0.0]), "downglow", follow="me")
# L54: both hands flat on the moon
put("me", "L54", [UX, UY - 0.25, UT + 0.6], 0, expr="wide", lean=84, arms=[96, 96])
ugc("L54", e=260.0)
shot("L54", mv([UX + 1.2, UY - 5.6, UT + 0.45], [UX, UY - 0.9, UT + 0.75], 28, [UX + 0.9, UY - 5.0, UT + 0.45], [UX, UY - 0.9, UT + 0.75], 28), "handsmoon")
# L55: warm, breathing
ugc("L55", e=200.0, dur=1.0)
ugc("L55+1.0", e=330.0, dur=1.2)
ugc("L55+2.2", e=210.0, dur=1.2)
beat("me", "L55", expr="soft")
shot("L55", mv([UX - 3.8, UY - 4.6, UT + 1.3], [UX, UY - 1.0, UT + 0.6], 28, [UX - 3.4, UY - 4.2, UT + 1.2], [UX, UY - 1.0, UT + 0.6], 28), "breathing")
# L56: kicking hard
put("me", "L56", [UX, UY + 0.2, UT + 1.2], 0, expr="squeeze", lean=30, arms=[150, 150], run=True)
go("me", "L56>", [UX, UY - 3.4, UT + 2.8], run=True)
cue("L56", "bubbles", on=1.0, x=2.0, y=-2.0, z=UT + 1.0)
ugc("L56", e=300.0)
shot("L56", FL([1.0, -5.0, 0.8], [-0.7, 0.0, 0.7], 32, [0.8, -4.4, 0.8]), "kick", follow="me")
# L57: it woke
cue("L57", "bubbles", on=0.0)
put("me", "L57", [UX, UY - 0.8, UT + 1.0], 0, expr="wide", lean=6, arms=[100, 100])
ugc("L57", e=220.0)
ugc("L57+0.2", e=720.0, roll=18.0, dur=1.3)
shot("L57", mv([UX + 0.8, UY - 6.0, UT + 0.4], [UX, UY - 0.8, UT + 2.0], 30, [UX + 0.6, UY - 5.4, UT + 0.5], [UX, UY - 0.8, UT + 2.2], 30), "woke")
# L58: the whole lake came up with it
look("L58", "night", dur=0.4)
dial("L58", 0.97, lit=1.0, dur=1.0)
only("L58", ["grandma"])
sit("grandma", "L58", True, GRAN_BENCH_Z)
boatc("L58", x=MX, y=MY, z=WZ, rock=0.5, yaw=0.0)
put("grandma", "L58", inboat(MX, MY, WZ), 0, expr="wide", keep_yaw=True)
boatc("L58+0.1", z=3.4, dur=1.2, rock=0.5)
go("grandma", "L58+0.1", inboat(MX, MY, WZ), yaw=0, keep_yaw=True)
go("grandma", "L58+1.3", inboat(MX, MY, 3.4), yaw=0, keep_yaw=True)
glow("L58", g=1.2, e=500.0, z=-1.0)
moonc("L58", -3.0)
moonc("L58+0.1", 3.4, dur=1.2)
cue("L58", "pour", p=1.0)
shot("L58", mv([MX + 1.0, MY - 9.0, 1.3], [MX, MY, 2.0], 40, [MX + 0.8, MY - 8.6, 1.4], [MX, MY, 3.2], 40), "bulge")
# L59: I came up beside Grandma's boat
look("L59", "dusk", dur=0.01)
moonc("L59", -3.0)
cue("L59", "pour", p=0.0)
boatc("L59", x=MX, y=MY, z=WZ, rock=0.3)
glow("L59", g=1.0, e=260.0)
only("L59", ["grandma", "me"])
put("grandma", "L59", inboat(MX, MY, WZ), 0, expr="wide", keep_yaw=True)
put("me", "L59", [MX + 1.5, MY - 1.4, -0.7], 20, expr="grin")
shot("L59", mv([MX + 2.4, MY - 4.8, 1.5], [MX + 1.5, MY - 1.4, 0.8], 36, [MX + 2.2, MY - 4.4, 1.5], [MX + 1.4, MY - 1.3, 0.85], 36), "surface")
# L60: I climbed in beside her (the oarlock plant, then both of us in the boat)
shot("L60", mv([MX + 2.2, MY - 1.4, 1.5], [MX + 0.8, MY + 0.1, 0.74], 42, [MX + 1.8, MY - 1.1, 1.2], [MX + 0.8, MY + 0.1, 0.74], 46), "oarlock")
oarc("L60", a=75.0, b=0.0)
sit("me", "L60.1", True, GRAN_BENCH_Z)
put("grandma", "L60.1", [MX - 0.42, MY + 0.25, WZ + 0.18], 0, expr="smile", keep_yaw=True)
put("me", "L60.1", [MX + 0.42, MY + 0.25, WZ + 0.18], 0, expr="grin", keep_yaw=True)
glow("L60.1", e=420.0, dur=1.0)
shot("L60.1", F([MX, MY + 0.25], 0, 4.2, 0.9, 36, tzoff=1.1, base=WZ + 0.18, off=-10, push=0.1), "bothin")
# L61: the moon lifted our whole boat
look("L61", "night", dur=0.4)
moonc("L61", 4.4, dur=0.01)
cue("L61", "pour", p=1.0)
boatc("L61", z=4.4, rock=0.8)
put("grandma", "L61", [MX - 0.42, MY + 0.25, 4.58], 0, expr="wide")
put("me", "L61", [MX + 0.42, MY + 0.25, 4.58], 0, expr="wide")
glow("L61", g=1.2, e=1000.0)
shot("L61", mv([MX + 1.5, MY - 9.4, 1.0], [MX, MY, 4.9], 34, [MX + 1.2, MY - 8.8, 1.2], [MX, MY, 5.2], 34), "lifted")
# L62: for one second we sat on top of it
shot("L62", F([MX, MY + 0.25], 0, 3.6, 0.5, 38, tzoff=1.15, base=4.58, off=-8, push=0.1), "twofaces")
beat("grandma", "L62", expr="smile")
beat("me", "L62", expr="grin")
beat("grandma", "L63")
beat("me", "L63")
# L63: it slid out from under us and we splashed down
moonc("L63", 4.4)
moonc("L63+0.4", -3.0, dur=1.0)
boatc("L63", z=4.4)
boatc("L63+0.5", z=WZ, dur=0.6, rock=1.0)
beat("grandma", "L63+0.5")
beat("me", "L63+0.5")
go("grandma", "L63+1.1", [MX - 0.42, MY + 0.25, WZ + 0.18], yaw=0, keep_yaw=True)
go("me", "L63+1.1", [MX + 0.42, MY + 0.25, WZ + 0.18], yaw=0, keep_yaw=True)
for who in ("grandma", "me"):
    acting[who][-1]["blend"] = 0.5
shot("L63", mv([MX + 2.2, MY - 7.6, 1.3], [MX, MY, 3.6], 32, [MX + 2.0, MY - 7.0, 1.2], [MX, MY, 2.6], 32), "slid")
shot("L63.2", F([MX, MY + 0.25], 0, 4.4, 0.9, 32, tzoff=1.1, base=WZ + 0.18, off=-8, push=0.1), "splash")
# L64: and it went up, right over the dock
cue("L64", "pour", p=0.0)
moonc("L64", 40.0)
glow("L64", e=0.0, g=0.0, dur=1.4)
cue("L64", "refl", v=0.8, dur=0.5)
dial("L64", 0.97, lit=1.0)
sit("grandma", "L64", False)
sit("me", "L64", False)
only("L64", [])
shot("L64", mv([0.4, -20.5, 6.5], [0.3, -27.8, 0.2], 24, [0.4, -21.5, 6.0], [0.3, -27.6, 0.2], 24), "settle")
shot("L64.1", mv([0.0, -35.0, 1.5], [0.3, -27.8, 0.3], 30, [0.1, -33.6, 1.3], [0.3, -27.8, 0.35], 30), "overdock")

# ===== 10 the warm turn: together, and the loop (L65 to L70)
cue("L65", "refl", v=0.0)
look("L65", "dusk", dur=0.01)
dial("L65", 0.93, lit=0.0)
glow("L65", g=1.0, e=150.0)
moonc("L65", -3.0)
only("L65", ["grandma", "me"])
boatc("L65", x=bxh, y=byh, z=WZ, rock=0.0)
sit("grandma", "L65", True, GRAN_BENCH_Z)
sit("me", "L65", True, GRAN_BENCH_Z)
put("grandma", "L65", [bxh - 0.42, byh + 0.25, WZ + 0.18], 0, expr="smile", keep_yaw=True)
put("me", "L65", [bxh + 0.42, byh + 0.25, WZ + 0.18], 0, expr="grin", keep_yaw=True)
for tt, ang in [("L65", 0), ("L65+0.8", 25), ("L65+1.6", -20)]:
    oarc(tt, a=70.0, b=ang, dur=0.7)
boatc("L65+0.1", x=MX + 1.0, y=MY - 8.4, dur=1.1)
go("grandma", "L65+1.2", [MX + 0.58, MY - 8.15, WZ + 0.18], yaw=0, keep_yaw=True)
go("me", "L65+1.2", [MX + 1.42, MY - 8.15, WZ + 0.18], yaw=0, keep_yaw=True)
shot("L65", FL([2.5, -5.4, 1.0], [0.42, 0.0, 1.0], 32, [2.1, -4.8, 1.0]), "together", follow="grandma")
# L66: she rows, I swim
only("L66", ["grandma", "me"])
boatc("L66", x=MX + 1.0, y=MY - 3.0, z=WZ)
put("grandma", "L66", [MX + 0.7, MY - 2.75, WZ + 0.18], 0, expr="smile", keep_yaw=True)
sit("me", "L66.1", False)
oarc("L66", a=70.0, b=0.0)
oarc("L66+0.7", a=70.0, b=25.0, dur=0.7)
oarc("L66+1.5", a=70.0, b=-20.0, dur=0.7)
shot("L66", mv([MX + 1.6, MY - 7.6, 1.3], [MX + 1.5, MY - 3.0, 1.2], 26, [MX + 1.5, MY - 7.0, 1.3], [MX + 1.5, MY - 3.0, 1.2], 26), "sheRows")
put("me", "L66.1", [MX + 2.4, MY - 3.0, -0.7], 0, expr="grin")
for k_ in range(6):
    acting["me"].append({"at": f"L66.1+{0.1 + k_ * 0.22:.2f}", "pos": [MX + 2.4 - 0.1 * k_, MY - 3.0 + 0.0, -0.7], "arms": [150 if k_ % 2 else 20, 20 if k_ % 2 else 150], "blend": 0.1, "yaw": 0})
# L67: the noon tick, close
only("L67", [])
look("L67", "day", dur=0.01)
dial("L67", 0.5, lit=0.0)
zoom("L67", 1.5, oy=-0.1)
glow("L67", g=0.6)
shot("L67", mv([-2.0, -33.0, 1.6], [1.5, -18.0, 0.8], 26, [-1.2, -32.0, 1.6], [1.5, -18.0, 0.8], 26), "tick")
# L68: no swimming after noon (the 11:59 swimmers again)
zoom("L68", 0.0)
only("L68", ["s1", "s2", "s3", "s4"])
for i, who in enumerate(["s1", "s2", "s3", "s4"]):
    st = [bx0 + 7.0 - i * 1.4, by0 + 5.2 - i * 1.0, -0.9]
    put(who, "L68", st, -54, expr=["smile", "grin", "smile", "grin"][i])
    go(who, "L68+0.9", [bx0 + 2.4 - i * 1.4, by0 + 1.7 - i * 1.0, 0.1], yaw=-54)
    go(who, "L68>", [bx0 - 1.0 - i * 1.4, by0 - 0.7 - i * 1.0, 0.1], yaw=-54)
shot("L68", mv([bx0 - 6.5, by0 - 5.5, 1.9], [bx0 + 2.0, by0 + 1.6, 1.4], 30, [bx0 - 5.2, by0 - 4.8, 1.8], [bx0 + 1.0, by0 + 0.9, 1.4], 30), "swimmers2")
# L69: unless it's your turn (me grinning up at Grandma in the boat)
look("L69", "dusk", dur=0.01)
dial("L69", 0.93, lit=0.0)
glow("L69", g=1.0, e=150.0)
only("L69", ["grandma", "me"])
boatc("L69", x=MX, y=MY, z=WZ, yaw=0.0)
sit("grandma", "L69", True, GRAN_BENCH_Z)
put("grandma", "L69", inboat(MX, MY, WZ), 150, expr="smile", keep_yaw=True)
put("me", "L69", [MX + 1.6, MY + 0.2, -0.7], -150, expr="grin")
oarc("L69", a=172.0, b=0.0)
shot("L69", mv([MX + 0.9, MY + 4.8, 1.5], [MX + 0.8, MY + 0.2, 1.1], 24, [MX + 0.8, MY + 4.3, 1.4], [MX + 0.8, MY + 0.2, 1.1], 24), "grinup")
# L70: so come on in, any morning (the loop: the opening frame)
sit("grandma", "L70", False)
look("L70", "day", dur=0.01)
dial("L70", 0.56, lit=0.0)
glow("L70", g=0.6)
only("L70", ["me"])
put("me", "L70", [0.3, -33.4, DECK], 180, expr="grin", arms=[0, 150])
beat("me", "L70.1", arms=[0, 120])
shot("L70", F([0.3, -33.4], 180, 4.0, 1.8, 36, tzoff=1.55, off=-12, push=0.1), "waveyouin")
only("L70.2", [])
cue("L70.2", "feet", on=1.0)
glow("L70.2", g=0.6)
cue("L70.2", "gdock", on=1.0)
shot("L70.2", mv([-1.0, -26.6, 0.45], [0.45, -29.5, 0.3], 30, [-0.8, -26.8, 0.45], [0.45, -29.5, 0.3], 30), "feet2")

# ---------------------------------------------------------------------------------------------- finish
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
    {"at": "L01.2", "kind": "bell", "db": -14},
    {"at": "L17.1+0.9", "kind": "thud", "db": -22},
    {"at": "L21", "kind": "thud", "db": -12},
    {"at": "L36", "kind": "whoosh", "db": -20},
    {"at": "L58", "kind": "whoosh", "db": -20},
    {"at": "L63.2", "kind": "thud", "db": -20},
]
music = {
    "root": 52, "mode": "major", "bpm": 92, "seed": 113,
    "sections": [
        {"at": 0, "voices": ["musicbox", "pad"], "energy": 0.4, "root": 52, "mode": "major"},
        {"at": "L15", "voices": ["pulse", "drone"], "energy": 0.35, "root": 52, "mode": "minor"},
        {"at": "L22", "voices": ["drone", "pulse"], "energy": 0.5, "root": 40, "mode": "minor"},
        {"at": "L29", "voices": ["drone"], "energy": 0.12, "root": 40, "mode": "minor"},
        {"at": "L30", "voices": ["pad", "drone"], "energy": 0.45, "root": 52, "mode": "minor"},
        {"at": "L37", "voices": ["pad", "choir"], "energy": 0.55, "root": 52, "mode": "major"},
        {"at": "L40", "voices": ["drone", "pad"], "energy": 0.2, "root": 52, "mode": "minor"},
        {"at": "L45", "voices": ["drone"], "energy": 0.4, "root": 40, "mode": "minor"},
        {"at": "L52", "voices": ["pulse", "drone"], "energy": 0.55, "root": 40, "mode": "minor"},
        {"at": "L58", "voices": ["pad", "choir", "piano"], "energy": 0.7, "root": 52, "mode": "major"},
        {"at": "L65", "voices": ["musicbox", "piano", "pad"], "energy": 0.45, "root": 52, "mode": "major"},
    ],
}
sound = {
    "floor": "wood", "steps_db": -26,
    "ambience": [{"kind": "water", "from": 0, "to": "end", "lufs": -46}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L35.2")], "twist": remap("L39"),
          "emph": [remap(x) for x in ["L01.2", "L05.0", "L20.0", "L21.0", "L35.1", "L37.0", "L57"]],
          "quiet": [[remap("L62"), remap("L63")]], "sway": [names["lean"], names["pushface"], names["againface"]],
          "hold": [names["dialdark"], names["tick"], names["diallit"]]}
story = {
    "slug": "ep113-moon-lake",
    "title": "Grandma's Lake Glows After NOON \U0001F319",
    "made_for_kids": False,
    "premise": ("At Grandma's lake, swimming is free all morning and banned after noon, because the moon sleeps on the "
                "lake bed all day and swimmers wake it, and a moon that wakes goes up. I help Grandma at the lake every "
                "weekend. One hot afternoon I swim anyway, and the sky starts going dark. That night I follow her "
                "rowboat out, and watch her push the moon up with her oar."),
    "twist": ("Grandma has pushed the moon up into the sky with her oar every night for fifty years, and the rule is "
              "there because swimmers wake it. When her arms are too tired one night, I swim down and wake it on "
              "purpose, and now we lift it together."),
    "world": ("A bright summer lake ringed with pines: a gray wooden dock, a red rowboat, a white lake house with a "
              "green screen porch, and a pale glow under the water where the moon sleeps."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#9fd2ff",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#bcd8ee", "fog_density": 0.004, "fog_start": 40.0, "sky": "#5ab8ff",
             "sky_strength": 1.0, "exposure": 0.2, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.25, "grain": 0.008},
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
    "asr_forgive": ["oar is", "oar", "order", "rowed", "rode", "rows", "rose"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
print(json.dumps(names))
