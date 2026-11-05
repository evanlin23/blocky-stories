"""Writes ../story.json for ep115 "are we there" (script.md, 2026-11-05). Run: python stories/ep115-are-we-there/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90. Shots use the script's chunk numbers (a shot at "L07.2" starts on chunk 2 of line L07); captions are
split to two or three words and the references are remapped.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import layout as G  # noqa: E402

OUT = HERE.parent / "story.json"
REV = 4
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
idx = next(i for i, l in enumerate(lines) if l["id"] == "L20")
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


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return [[0, list(p0), list(t0), l0]]
    return [[0, list(p0), list(t0), l0], [1, list(p1), list(t1 if t1 is not None else t0), l1 or l0]]


def face(xy, d, lens, dx=-0.45, dz=0.05, tx=0.0, tz=0.0, push=0.12, hz=1.57):
    """A camera in front of a head at xy (on the -y side), d metres away, easing in by `push`."""
    x, y = xy
    tgt = [x + tx, y, hz + tz]
    return mv([x + dx, y - d, hz + dz], tgt, lens, [x + dx * 0.8, y - d * (1 - push), hz + dz], tgt, lens)


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, hat="none",
           hat_c="#333333", extras=(), eyes="round", sleeves="long", brow_w=1.0, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c,
         "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    if brow_w != 1.0:
        d["face"]["brow_w"] = brow_w
    if pattern_c:
        d["pattern_c"] = pattern_c
    if extras:
        d["extras"] = list(extras)
    d.update(kw)
    return d


cast = {
    "me": person("#e8b890", "#4f9a5a", "#4a5a78", "#5a4a3a", hair="cap", hair_c="#4a3224", pattern="plaid",
                 pattern_c="#2f6a3a", extras=["coat"], extra_c="#8a909a", brow_w=1.6),
    "jo": person("#dca97c", "#a98be0", "#3a4258", "#f4f4f2", hair="cap", hair_c="#201612", hat="beanie", hat_c="#f4f4f4",
                 eyes="lashes", brow_w=1.6),
    "mom": person("#e6b48c", "#ff8a6b", "#4a4a5a", "#3a2a1a", hair="cap", hair_c="#9a8878", pattern="knit",
                  pattern_c="#e8745a", extras=["glasses"], extra_c="#3a2a2a", eyes="lashes", brow_w=1.6),
    "plowman": person("#d9a47a", "#2a2d33", "#3a4258", "#2a2d33", hair="cap", hair_c="#5a4a3a", hat="ballcap",
                      hat_c="#ff8a1e", brow_w=1.9),
    "trucker": person("#c89870", "#c04a3a", "#3a4258", "#2a2d33", hair="cap", hair_c="#3a2a1a", pattern="plaid",
                      pattern_c="#2a2a2a", hat="ballcap", hat_c="#3a6ea8", brow_w=1.9),
    "pizza": person("#e2b088", "#f4f4f4", "#2a2d33", "#2a2d33", hair="cap", hair_c="#3a2418", hat="ballcap",
                    hat_c="#d9362b", brow_w=1.6),
    "quiet1": person("#e2b088", "#6a7a8a", "#2a2d33", "#2a2d33", hair="cap", hair_c="#3a2a1a", hat="beanie",
                     hat_c="#d9362b", brow_w=1.6),
    "quiet2": person("#c89870", "#8a5a7a", "#2a2d33", "#2a2d33", hair="bun", hair_c="#1a1410", eyes="lashes",
                     brow_w=1.6),
}
def three():
    """The front three-shot from the hood: Mom in front, Jo and me behind, all three heads whole."""
    return mv([-0.02, -3.4, 1.62], [-0.02, 1.0, 1.52], 31, [-0.02, -3.2, 1.62], [-0.02, 1.0, 1.52], 31)


PLOW0 = (G.PLOW[0] + 0.5, 0.4)
RIG0 = (G.TRUCK[0] + 0.5, 0.4)
PIZ0 = (G.DOOR[0], 1.4)
Q1 = (G.SILVER[0] - 0.5, 0.45)
Q2 = (G.SILVER[0] + 0.5, 0.45)
START = {"me": (G.ME, 0.0), "jo": (G.JO, 0.0), "mom": (G.MOM, 0.0), "plowman": (PLOW0, 0.95), "trucker": (RIG0, 0.95),
         "pizza": (PIZ0, 0.15), "quiet1": (Q1, 0.0), "quiet2": (Q2, 0.0)}
acting = {}
last = {}
for n_, (xy_, z_) in START.items():
    acting[n_] = [{"at": 0, "pos": [xy_[0], xy_[1], z_] if z_ else list(xy_), "yaw": 0, "expr": "neutral", "blend": 0.0}]
    last[n_] = [xy_[0], xy_[1], z_] if z_ else list(xy_)
cues = []
SH = []


def beat(who, at, **kw):
    acting[who].append({"at": at, "pos": list(last[who]), **kw})


def put(who, at, pos, yaw=None, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0}
    if yaw is not None:
        k["yaw"] = yaw
    k.update(kw)
    acting[who].append(k)
    last[who] = p


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def shot(at, camera, name, step=2, hand=None, follow=None):
    SH.append((at, camera, step, hand, follow, name))


def move(at, obj, dur=0.0, **kw):
    cue(at, "mv", obj=obj, dur=dur, **kw)


def lap(at, n):
    cue(at, "lap", n=float(n))


def speed(at, v, dur=0.0):
    cue(at, "speed", v=float(v), dur=dur)


def sit(who, at, on=True):
    cue(at, "sit", who=who, on=on)


def look(at, id_, dur=0.0):
    cue(at, "look", id=id_, dur=dur)


def tagbig(at, s=1.0, x=-0.5, y=0.66):
    cue(at, "tagbig", s=s, x=x, y=y)


def post_pass(at, y0, y1, dur, off=0.0):
    move(at, "post", x=G.POST_X, y=y0, z=0.0)
    move(f"{at}+{off + 0.02}" if off == 0 else at, "post", dur=dur, lin=True, y=y1)


def rf(line, off):
    return f"{line}{off:+.2f}"


def falls_come(line, arrive, dur=3.4):
    """The waterfall slides in from ahead beside Mom's window and stops there, as the van slows."""
    move(rf(line, arrive - dur), "falls", x=G.FALLS_X + 1.5, y=-50.0, z=0.0)
    move(rf(line, arrive - dur + 0.02), "falls", dur=dur - 0.02, y=G.FALLS_Y)


def falls_go(line, off, dur=3.0):
    move(rf(line, off), "falls", dur=dur, y=G.FALLS_Y + 70.0)
    move(rf(line, off + dur + 0.1), "falls", z=-60.0)


VAN_X = 0.0
MOMF = G.MOM
for w_ in ("me", "jo", "mom", "quiet1", "quiet2"):
    sit(w_, 0)
cue(0, "lap", n=37.0)
cue(0, "speed", v=9.0)
cue(0, "look", id="day", dur=0.0)
cue(0, "flakes", v=0.0)
cue(0, "tagbig", s=1.0, x=-0.5, y=0.66)
move(0, "falls", x=G.FALLS_X + 1.5, y=-50.0, z=-60.0)
move(0, "post", x=G.POST_X, y=-60.0)
move(0, "hatch", z=0.0)
move(0, "phone", x=G.JO[0] - 0.02, y=0.7, z=-60.0)

# ===================================================================== 01 the hook (L01 to L02)
# me, lips shut, the mile post sliding past the window behind me
beat("me", 0, expr="shut")
move(0, "post", x=G.POST_X, y=1.5)
move(0.02, "post", dur=1.4, lin=True, y=14.0)
shot(0, face(G.ME, 1.9, 31, dx=0.7, tx=-0.12, push=0.1), "mehook")
move("L01.1", "post", x=G.POST_X, y=-2.0)
move("L01.1+0.02", "post", dur=1.5, lin=True, y=5.0)
shot("L01.1", mv([-7.2, 0.9, 1.35], [-3.4, 0.9, 1.25], 26, [-6.6, 0.9, 1.35], [-3.4, 0.9, 1.25], 26), "postclose")
shot("L01.3", face(G.ME, 1.6, 36, dx=0.55, tx=-0.1, push=0.12), "meovr")
# L02: back to mile one
move("L01.3", "post", x=G.POST_X, y=-60.0)
shot("L02", three(), "three1")
beat("mom", "L02", expr="smile")
beat("jo", "L02", expr="neutral")
beat("me", "L02", expr="neutral")

# ===================================================================== 02 the rule at work (L03 to L06)
tagbig("L03", s=1.5, x=0.0, y=0.3)
shot("L03", mv([-1.0, -12.0, 1.8], [0.0, 0.0, 1.5], 34, [-0.6, -10.5, 1.8], [0.0, 0.0, 1.5], 34), "tag37")
tagbig("L03.2")
beat("jo", "L03.2", expr="neutral", head=[-18, 0])
beat("me", "L03.2", expr="neutral", head=[18, 0])
beat("jo", "L03.2+0.5", head=[18, 0])
beat("me", "L03.2+0.5", head=[-18, 0])
beat("jo", "L03.2+0.9", head=[-18, 0])
beat("me", "L03.2+0.9", head=[18, 0])
shot("L03.2", mv([-0.3, -1.35, 1.62], [-0.3, 1.45, 1.57], 22, [-0.3, -1.1, 1.62], [-0.3, 1.45, 1.57], 22), "shake1")
beat("trucker", "L04", expr="shut")
shot("L04", mv([RIG0[0] - 0.3, -5.2, 2.6], [RIG0[0], 0.4, 2.52], 36, [RIG0[0] - 0.25, -4.7, 2.6], [RIG0[0], 0.4, 2.52], 36), "trucker")
beat("pizza", "L05", expr="polite", arms=[90, 90])
shot("L05", mv([G.DOOR[0] - 0.3, -2.4, 1.78], [G.DOOR[0], 1.4, 1.62], 30, [G.DOOR[0] - 0.25, -1.9, 1.78], [G.DOOR[0], 1.4, 1.62], 30), "pizza")
beat("pizza", "L05.2", expr="sad-smile")
shot("L05.2", mv([G.DOOR[0] - 0.15, -1.4, 1.75], [G.DOOR[0], 1.4, 1.5], 30, [G.DOOR[0] - 0.1, -1.1, 1.75], [G.DOOR[0], 1.4, 1.5], 30), "stubble")
beat("quiet1", "L06", expr="wide")
beat("quiet2", "L06", expr="wide")
shot("L06", mv([G.SILVER[0] - 0.1, -3.7, 1.7], [G.SILVER[0], 0.45, 1.55], 32, [G.SILVER[0] - 0.1, -3.4, 1.7], [G.SILVER[0], 0.45, 1.55], 32), "silent")

# ===================================================================== 03 who we are (L07 to L11)
beat("mom", "L07", expr="smile")
shot("L07", face(G.MOM, 1.7, 26, dx=-0.5, tx=0.12), "mom07")
beat("jo", "L07.2", expr="smile")
beat("me", "L07.2", expr="smile", head=[0, 0])
shot("L07.2", mv([-0.3, -1.35, 1.62], [-0.3, 1.45, 1.57], 22, [-0.3, -1.1, 1.62], [-0.3, 1.45, 1.57], 22), "duo07")
move("L07.3", "cabin", x=-6.5, y=-60.0, z=-0.45)
move("L08", "cabin", x=-6.0, y=-112.0, z=8.4)
shot("L07.3", mv([-0.3, 0.8, 1.62], [-5.6, -60.0, 2.4], 52, [-0.3, 0.8, 1.62], [-5.6, -60.0, 2.4], 58), "cabinfar")
shot("L08", mv([-0.3, -1.45, 1.62], [-0.3, 1.45, 1.57], 22, [-0.3, -1.2, 1.62], [-0.3, 1.45, 1.57], 23), "duo08")
beat("jo", "L08", expr="neutral", head=[0, 0])
beat("me", "L08", expr="neutral")
shot("L09", mv([9.0, 14.0, 7.0], [0.0, -20.0, 2.5], 22, [8.0, 12.0, 6.6], [0.0, -20.0, 2.5], 22), "highwide")
beat("mom", "L10", expr="warm")
shot("L10", face(G.MOM, 1.65, 28, dx=-0.45, tx=0.12), "mom10")
move("L10", "falls", x=G.FALLS_X + 1.5, y=-50.0, z=-60.0)
move("L10.2", "cooler", x=-0.45, y=-0.1, z=0.5)
move("L11", "cooler", x=G.COOLER[0], y=G.COOLER[1], z=0.5)
shot("L10.2", mv([-0.45, -0.16, 1.95], [-0.45, -0.1, 0.5], 24, [-0.45, -0.16, 1.7], [-0.45, -0.1, 0.5], 24), "cooler1")

# L11: the three landmarks
shot("L11", mv([G.PINE[0], -14.0, 3.0], [G.PINE[0], 0.0, 4.8], 26, [G.PINE[0], -13.0, 3.4], [G.PINE[0], 0.0, 4.8], 26), "pine1")
shot("L11.1", mv([G.PLOW[0] - 0.4, -7.8, 2.2], [G.PLOW[0], 0.0, 2.0], 30, [G.PLOW[0] - 0.3, -7.2, 2.3], [G.PLOW[0], 0.0, 2.0], 30), "plow1")
shot("L11.2", mv([G.FALLS[0], -11.0, 3.4], [G.FALLS[0], 4.0, 4.6], 24, [G.FALLS[0], -10.0, 3.6], [G.FALLS[0], 4.0, 4.6], 24), "falls1")

# ===================================================================== 04 the loop shows (L12 to L19)
lap("L12", 38)
move("L12", "post", x=G.POST_X, y=-1.8)
move("L12+0.02", "post", dur=1.1, lin=True, y=0.6)
shot("L12", mv([-8.0, -1.4, 1.2], [-3.7, -1.5, 1.2], 28, [-7.6, -1.2, 1.2], [-3.7, -0.6, 1.2], 28), "post2")
tagbig("L12.1", s=1.6, x=0.0, y=0.3)
shot("L12.1", mv([0.0, 0.7, 1.62], [0.0, -30.0, 1.7], 26, [0.0, 0.7, 1.62], [0.0, -30.0, 1.7], 27), "tag38")
tagbig("L13")
move("L13", "post", x=G.POST_X, y=-60.0)
beat("jo", "L13", expr="worried", head=[-30, 0])
beat("me", "L13.1", expr="worried", head=[30, 0])
shot("L13", face(G.JO, 1.9, 29, dx=-0.4, tx=0.0), "jo13")
shot("L13.1", face(G.ME, 1.9, 29, dx=0.5, tx=0.0), "me13")
beat("jo", "L14", head=[-20, 0], expr="worried")
beat("me", "L14", head=[20, 0], expr="worried")
beat("jo", "L14.1", head=[20, 0])
beat("me", "L14.1", head=[-20, 0])
beat("jo", "L14.1+0.5", head=[-20, 0])
beat("me", "L14.1+0.5", head=[20, 0])
shot("L14", mv([-0.3, -1.45, 1.62], [-0.3, 1.45, 1.57], 22, [-0.3, -1.2, 1.62], [-0.3, 1.45, 1.57], 23), "duo14")
beat("jo", "L15", head=[0, 0], expr="neutral")
beat("me", "L15", head=[0, 0], expr="neutral")
beat("mom", "L15", expr="smile")
beat("mom", "L15.2", expr="warm")
shot("L15", face(G.MOM, 1.7, 26, dx=-0.5, tx=0.12), "mom15")
lap("L16", 39)
shot("L16", mv([G.PINE[0] + 2.0, -13.0, 3.2], [G.PINE[0], 0.0, 4.8], 26, [G.PINE[0] + 1.5, -12.0, 3.5], [G.PINE[0], 0.0, 4.8], 26), "pine2")
beat("plowman", "L16.1", arms=[0, 150], expr="grin")
beat("plowman", "L16.1+0.25", arms=[0, 120])
beat("plowman", "L16.1+0.5", arms=[0, 155])
shot("L16.1", mv([G.PLOW[0] + 0.6, -5.4, 2.55], [G.PLOW[0] + 0.5, 0.4, 2.45], 36, [G.PLOW[0] + 0.5, -5.0, 2.55], [G.PLOW[0] + 0.5, 0.4, 2.45], 36), "plowwave1")
# L17: Mom slows at the waterfall
speed("L17+0.8", 1.2, 1.4)
falls_come("L17", 1.6)
shot("L17", face(G.MOM, 1.65, 24, dx=-0.55, tx=0.28), "mom17")
shot("L17.2", mv([G.FALLS[0] - 3.0, -9.5, 2.8], [G.FALLS[0], 4.0, 4.2], 26, [G.FALLS[0] - 2.5, -8.5, 3.0], [G.FALLS[0], 4.0, 4.2], 26), "falls2")
falls_go("L18", -0.2, 3.0)
speed("L18-0.1", 9.0, 1.0)
beat("mom", "L18", hidden=True)
shot("L18", mv([-0.45, 0.3, 1.3], [0.5, -1.1, 0.98], 40, [-0.3, 0.1, 1.25], [0.5, -1.1, 0.98], 40), "gauge")
beat("jo", "L19", expr="worried")
move("L19", "phone", x=G.JO[0], y=0.62, z=1.2)
cue("L19", "sit", who="jo", on=True)
beat("jo", "L19", arms=[75, 75])
shot("L19", face(G.JO, 1.7, 30, dx=-0.6, tz=-0.05), "jo19")
move("L19.1", "phone", x=-0.1, y=-0.2, z=1.3)
shot("L19.1", mv([-0.1, -0.66, 1.3], [-0.1, -0.2, 1.33], 30, [-0.1, -0.6, 1.3], [-0.1, -0.2, 1.33], 30), "phone")

# ===================================================================== 05 the squall (L20 to L26)
shot("P01", mv([4.0, -34.0, 7.0], [0.0, 0.0, 1.5], 36, [3.6, -30.0, 6.4], [0.0, 0.0, 1.5], 36), "dropwide")
look("P01", "squall", 0.6)
speed("P01", 6.0, 0.6)
move("P01>", "phone", z=-60.0)
beat("jo", "P01>", arms=[0, 0])
beat("mom", "P01", hidden=False)
cue("P01>", "flakes", v=1.0)
lap("L20", 40)
tagbig("L20", s=1.5, x=0.0, y=0.3)
shot("L20", mv([-2.0, -9.0, 1.6], [0.0, 0.0, 1.3], 34, [-1.6, -8.4, 1.6], [0.0, 0.0, 1.3], 34), "tag40")
tagbig("L20.1")
shot("L20.1", mv([2.6, -6.4, 0.6], [-0.1, -2.9, 0.5], 34, [2.3, -5.6, 0.6], [-0.1, -2.9, 0.5], 34), "lights")
beat("plowman", "L21", arms=[0, 150], expr="grin")
beat("plowman", "L21+0.3", arms=[0, 120])
beat("plowman", "L21+0.6", arms=[0, 155])
shot("L21", mv([G.PLOW[0] + 0.7, -5.4, 2.55], [G.PLOW[0] + 0.5, 0.4, 2.45], 36, [G.PLOW[0] + 0.5, -5.0, 2.55], [G.PLOW[0] + 0.5, 0.4, 2.45], 36), "plowwave2")
beat("me", "L21.1", expr="worried", head=[-8, 0])
shot("L21.1", face(G.ME, 1.8, 30, dx=0.5), "me21")
beat("jo", "L22", expr="neutral", arms=[40, 0])
shot("L22", mv([-0.2, 0.2, 1.62], [-0.05, 1.35, 1.0], 28, [-0.15, 0.3, 1.58], [-0.05, 1.35, 1.0], 28), "cooler2")
beat("me", "L23", expr="neutral", head=[35, 0])
shot("L23", face(G.ME, 1.8, 30, dx=0.6, tx=0.1, push=0.1), "me23")
beat("mom", "L24", expr="neutral")
speed("L24", 1.0, 1.0)
falls_come("L24", 0.5, 2.6)
shot("L24", face(G.MOM, 1.65, 24, dx=-0.55, tx=0.28), "mom24")
beat("mom", "L25.1", expr="neutral")
cues.append({"at": "L25.1", "name": "noop"})
acting["mom"].append({"from": "L25.1", "to": "L26>", "mouth": [0.0, 0.35], "flap": True})
shot("L25", face(G.MOM, 1.5, 30, dx=-0.5, tx=0.22), "mom25")
shot("L26", face(G.MOM, 1.6, 30, dx=-0.55, tx=0.28, tz=-0.22, push=0.08), "reveal")

# ===================================================================== 06 the twist (L27 to L31)
falls_go("L27", 0.5, 3.0)
speed("L27", 6.0, 1.2)
beat("mom", "L27", expr="sad-smile")
shot("L27", face(G.MOM, 1.6, 28, dx=-0.5, tx=0.12), "mom27")
beat("me", "L27.1", expr="wide", head=[0, 0])
beat("mom", "L28", expr="warm")
beat("jo", "L28", head=[0, 0], expr="neutral", arms=[0, 0])
beat("me", "L28", expr="neutral")
shot("L28", three(), "three2")
look("L28.2", "day", 1.0)
cue("L28.2", "flakes", v=0.0)
speed("L28.2", 9.0, 1.0)
# L29: the sliding door handle, then Jo at the open hatch
shot("L28.3", mv([-3.0, 1.3, 0.85], [-1.36, 1.7, 0.7], 42, [-2.6, 1.4, 0.8], [-1.36, 1.7, 0.7], 42), "handle")
sit("jo", "L29.1", False)
put("jo", "L29.2", [-0.6, 3.6], 180, expr="smile", arms=[0, 0], head=[0, 0])
move("L29.1", "hatch", z=2.6)
shot("L29.2", mv([-0.5, 6.3, 1.65], [-0.45, 3.2, 1.5], 30, [-0.45, 5.8, 1.65], [-0.45, 3.2, 1.5], 30), "hatchjo")
move("L30+0.3", "hatch", z=0.0)
beat("mom", "L30", expr="sad-smile")
shot("L30", face(G.MOM, 1.65, 28, dx=-0.5, tx=0.12), "mom30")
beat("mom", "L30+0.7", expr="smile")
put("jo", "L31", [G.JO[0], G.JO[1]], 0, expr="laugh", arms=[0, 0], head=[0, 0])
sit("jo", "L31", True)
beat("jo", "L31", expr="laugh")
beat("jo", "L31.2", arms=[0, 0], expr="laugh")
shot("L31", face(G.JO, 1.8, 30, dx=-0.35), "jo31")

# ===================================================================== 07 the turn (L32 to L37)
beat("me", "L32", expr="smile")
shot("L32", face(G.ME, 1.8, 28, dx=0.5, tx=0.0), "me32")
beat("jo", "L32.2", expr="smile", head=[-14, 0])
beat("mom", "L32.2", expr="warm")
shot("L32.2", three(), "three3")
lap("L33", 41)
beat("mom", "L33", expr="smile")
beat("jo", "L33", head=[0, 0], expr="smile")
speed("L33", 9.0)
shot("L33", face(G.MOM, 1.7, 26, dx=-0.5, tx=0.12), "mom33")
speed("L34", 1.2, 1.2)
falls_come("L34", 0.4, 2.6)
beat("mom", "L34", expr="warm")
shot("L34", face(G.MOM, 1.65, 24, dx=-0.55, tx=0.28), "mom34")
falls_go("L34.1", 0.8, 3.0)
move("L34.1-0.02", "cabin", x=0.2, y=-80.0, z=-0.45)
move("L34.1", "cabin", dur=2.4, y=-22.0)
speed("L34.1", 5.0, 1.0)
shot("L34.1+0.4", mv([-0.3, 0.8, 1.62], [0.2, -60.0, 3.0], 28, [-0.3, 0.8, 1.62], [0.2, -30.0, 2.6], 28), "cabinup")
beat("jo", "L35.1", expr="smile")
beat("me", "L35.1", expr="smile")
shot("L35.1", mv([-0.3, -1.45, 1.62], [-0.3, 1.45, 1.57], 22, [-0.3, -1.2, 1.62], [-0.3, 1.45, 1.57], 23), "duo35")
beat("jo", "L36", head=[-30, 0], expr="smile")
shot("L36", face(G.JO, 1.9, 29, dx=-0.4), "jo36")
beat("me", "L36.1", head=[30, 0], expr="smile")
shot("L36.1", face(G.ME, 1.9, 29, dx=0.5), "me36")
beat("jo", "L37", head=[0, 0], expr="grin")
beat("me", "L37", head=[0, 0], expr="grin")
for w_ in ("jo", "me"):
    acting[w_].append({"from": "L37.1-0.1", "to": "L37>", "mouth": [0.0, 0.55], "flap": True})
shot("L37", mv([-0.3, -1.45, 1.62], [-0.3, 1.45, 1.57], 22, [-0.3, -1.2, 1.62], [-0.3, 1.45, 1.57], 23), "duo37")
beat("mom", "L37.1", expr="smile")
move("L37.1", "post", x=G.POST_X, y=-3.0)
move("L37.1+0.02", "post", dur=1.4, lin=True, y=14.0)
shot("L37.1", face(G.ME, 1.9, 31, dx=0.7, tx=-0.12, push=0.1), "loopme")

# ---------------------------------------------------------------------------------------------- finish
for k_ in acting.values():
    remap_all(k_)
remap_all(cues)
cues[:] = [c for c in cues if c["name"] != "noop"]
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

sfx = []


def honk(at):
    sfx.append({"at": at, "kind": "ding", "pitch": 290, "lp": 1500, "dur": 0.45, "db": -13})
    sfx.append({"at": f"{at}+0.22", "kind": "ding", "pitch": 365, "lp": 1500, "dur": 0.55, "db": -13})


honk("L11.1")
honk("L16.1")
honk("L21")
for ref in ("L12", "L16", "L20", "L33"):
    sfx.append({"at": ref, "kind": "click", "db": -22})
music = {
    "root": 50, "mode": "major", "bpm": 112, "seed": 115,
    "sections": [
        {"at": 0, "voices": ["musicbox", "pulse", "pad"], "energy": 0.55, "root": 50, "mode": "major"},
        {"at": "L12", "voices": ["musicbox", "pulse", "pad"], "energy": 0.6, "root": 50, "mode": "major"},
        {"at": "L20", "voices": ["drone", "pad"], "energy": 0.3, "root": 50, "mode": "minor"},
        {"at": "L27", "voices": ["drone", "pad"], "energy": 0.25, "root": 50, "mode": "major"},
        {"at": "L31.1", "voices": ["musicbox", "pad"], "energy": 0.4, "root": 50, "mode": "major"},
        {"at": "L32", "voices": ["musicbox", "pulse", "pad"], "energy": 0.62, "root": 50, "mode": "major"},
    ],
}
sound = {
    "floor": "snow", "steps_db": -26,
    "ambience": [{"kind": "wind", "from": "L20", "to": "L27", "lufs": -40}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
hold = [names[n_] for n_ in ("reveal", "handle", "gauge", "phone", "highwide", "tag37", "tag38", "tag40", "cabinfar", "three1", "three2", "three3")]
sway = [names[n_] for n_ in ("plowwave2", "me21", "cooler2", "me23", "mom24", "mom25", "reveal")]
polish = {"reveal": [remap("L26"), remap("L30")], "twist": remap("L27"),
          "quiet": [[remap("L33"), remap("L34.1")]], "hold": hold, "sway": sway}
story = {
    "slug": "ep115-are-we-there",
    "title": "The Drive That Starts OVER 🚗",
    "made_for_kids": False,
    "premise": ("On our mountain road, asking are we there yet sends the car back to mile one. My family has driven "
                "the same winter road to our rented cabin thirty-seven times, and neither my sister nor I ever asked."),
    "twist": ("It was our mom: she whispers the question at the frozen waterfall every lap, with snacks packed for "
              "fifty laps, because the drive is the only time she gets both her grown kids in one car. We make her a "
              "deal, a drive a month, and then ask it ourselves, together, for one more lap."),
    "world": ("A bright blue-sky winter mountain road through snowy pines in a teal minivan: a huge snowy pine, a "
              "honking orange snowplow, a frozen waterfall on a rock face, a white mile post and a little log cabin."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff9a2e",
    "gap": 0.15,
    "tail": 0.0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#e4f1fb", "fog_density": 0.003, "fog_start": 45.0, "sky": "#7cc6ff",
             "sky_strength": 1.0, "exposure": 0.15, "flash_safe": True, "polish": polish},
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
    "set_moves": [],
    "clip_ok": [],
    "framing_ok": [names[n_] for n_ in ("pine1", "falls1", "pine2", "jo31", "me23")],
    "asr_forgive": [],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
if __import__("os").environ.get("NAMES"):
    print({v: k for k, v in names.items()})
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
