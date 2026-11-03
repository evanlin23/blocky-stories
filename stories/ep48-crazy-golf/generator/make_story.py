"""Writes ../story.json for ep48 "crazy golf" (script.md, 2026-11-02). Run: python stories/ep48-crazy-golf/generator/make_story.py

The words are in lines.json (every line of the script). Places are in ../golf_layout.py (shared with set.py).
Coordinates: x east, y away from the gate (0, 0), z up. A character facing -y has yaw 0, +x 90, -x -90, +y 180.
Shot ids are numbered in order, and every shot starts on a line reference.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import golf_layout as G  # noqa: E402

OUT = HERE.parent / "story.json"
import re
orig_lines = json.loads((HERE / "lines.json").read_text())
# captions are two or three words at a time: longer script chunks are split, and chunk references are remapped
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


# ---------------------------------------------------------------------------------------------- cameras
def cam(tx, ty, tz, az, d, h, lens=35, push=None, roll=0.0):
    """Camera d metres from the target toward azimuth az (0 = on the -y side looking +y, 90 = on the +x side),
    h high. push: dolly in by that fraction over the shot."""
    def at(dd):
        return [round(tx + dd * math.sin(az * D2R), 3), round(ty - dd * math.cos(az * D2R), 3), h]
    tgt = [tx, ty, tz]
    if push is None:
        return [[0, at(d), tgt, lens, roll]]
    return [[0, at(d), tgt, lens, roll], [1, at(d * (1 - push)), tgt, lens, roll]]


def mv(p0, t0, l0, p1=None, t1=None, l1=None, roll=0.0):
    if p1 is None:
        return [[0, list(p0), list(t0), l0, roll]]
    return [[0, list(p0), list(t0), l0, roll], [1, list(p1), list(t1 if t1 is not None else t0), l1 or l0, roll]]


# ---------------------------------------------------------------------------------------------- the cast
def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, collar=None,
           hat="none", hat_c="#333333", extras=(), eyes="round", ink="#16100c", sleeves="long", zip_c=None, brow_w=1.0, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c,
         "face": {"eyes": eyes, "brows": True, "ink": ink}}
    if brow_w != 1.0:
        d["face"]["brow_w"] = brow_w
    if pattern_c:
        d["pattern_c"] = pattern_c
    if collar:
        d["collar"] = collar
    if extras:
        d["extras"] = list(extras)
    if zip_c:
        d["zip_c"] = zip_c
    d.update(kw)
    return d


cast = {
    "me": person("#d9a577", "#b5532f", "#262c42", "#f0f0ee", hair="mop", hair_c="#3a2618", collar="#efe2c4", brow_w=1.9,
                 extras=["coat"], zip_c="#efe2c4"),
    "dad": person("#e8b890", "#243a5e", "#b99a6a", "#5a3b22", hair="none", collar="#f0dc6a", eyes="tired",
                  ink="#55555c"),
    "gordon": person("#e6b48c", "#3f7a4a", "#3a3a44", "#4a3a2a", hair="swoop", hair_c="#5a3a22", pattern="plaid",
                     pattern_c="#2a5236"),
    "gordon_wife": person("#c98f66", "#6a2f55", "#2a2a30", "#2a2a30", hair="long", hair_c="#8a3a1f",
                          extras=["coat"], zip_c="#3a1a30"),
    "footballer": person("#e8c4a0", "#b8433c", "#b8433c", "#efefef", hair="swoop", hair_c="#eeeeee",
                         pattern="stripes", pattern_c="#f3efe8"),
    "builder_a": person("#d6a07a", "#e6e02a", "#3a3d44", "#5a4a32", hair="cap", hair_c="#1c1a18", hat="beanie",
                        hat_c="#9a9ea4", sleeves="short"),
    "builder_b": person("#b98456", "#e6e02a", "#4a4a52", "#5a4a32", hair="buzz", hair_c="#1c1a18", hat="beanie",
                        hat_c="#9a9ea4", sleeves="short"),
    "c1": person("#e8b890", "#2f7fb0", "#2b2f3a", "#d8d8d8", hair="spiky", hair_c="#5a3a22", pattern="stripes",
                 pattern_c="#e8f0f4"),
    "c2": person("#a9714a", "#d0883a", "#3a2f2a", "#2a2a2a", hair="long", hair_c="#1a1210"),
    "c3": person("#f0c8a0", "#7a4f9a", "#3a4a5a", "#c8b898", hair="swoop", hair_c="#a05a2a", sleeves="short"),
    "c4": person("#d3a07a", "#3a8a6a", "#5a4a3a", "#2a3a2a", hair="buzz", hair_c="#2a2a2a", extras=["scarf"],
                 extra_c="#d0c040"),
    "c5": person("#b98456", "#c8a43a", "#2f3548", "#f2f2f0", hair="cap", hair_c="#2a1a12", hat="ballcap",
                 hat_c="#a03a32"),
    "c6": person("#e8b890", "#d8d0c0", "#6a8a9a", "#5a4632", hair="none", hair_c="#000000", sleeves="short",
                 extras=["glasses"]),
    "c7": person("#8a5a3a", "#b04a5a", "#2a2a38", "#d8d0c8", hair="bun", hair_c="#150f0c"),
    "c8": person("#f0c8a0", "#4a6a3a", "#4a4036", "#3a2a1a", hair="cap", hair_c="#8a6a3a", hat="bucket",
                 hat_c="#c8b070"),
}
CAST_ORDER = list(cast)

# ---------------------------------------------------------------------------------------------- acting helpers
acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0]}] for n in cast}
last = {n: [0, 0] for n in cast}


def put(who, at, pos, yaw=None, **kw):
    """Appear (or jump) to pos on `at` (no walking across the cut)."""
    p = list(pos)
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False}
    if yaw is not None:
        k["yaw"] = yaw
    k.update(kw)
    acting[who].append(k)
    last[who] = p


def walk(who, at, pos, **kw):
    p = list(pos)
    k = {"at": at, "pos": p}
    k.update(kw)
    acting[who].append(k)
    last[who] = p


def hold(who, at, **kw):
    acting[who].append({"at": at, "pos": list(last[who]), **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True})


# ---------------------------------------------------------------------------------------------- cues
cues = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def look(at, id_, dur=0.6):
    """dur 0 is a hard set on a cut (the shot opens already in this light)."""
    cue(at, "look", id=id_, dur=dur)


def obj(id_, at, pos=None, yaw=0.0, dur=0.0, hide=False, rot=None):
    c = {"at": at, "name": "obj", "id": id_}
    if pos is not None:
        c["pos"] = list(pos)
        c["yaw"] = yaw
        c["rot"] = list(rot or [0, 0, 0])
    if dur:
        c["dur"] = dur
    if hide:
        c["hide"] = True
    cues.append(c)


def sit(who, at, on=True, z=0.46):
    cue(at, "sit", who=who, on=on, z=z)


def wring(at, w, pos=G.TEE_R, yaw=180.0, lean=(0.0, 0.0), head_extra=0.0, dur=0.0, hide_=False):
    c = {"at": at, "name": "wring", "pos": list(pos), "yaw": yaw, "wring": w, "lean": list(lean),
         "head_extra": head_extra}
    if dur:
        c["dur"] = dur
    if hide_:
        c["hide"] = True
    cues.append(c)


# figures: id -> [pose, mop]
figs = {}
for i, pose in enumerate(["sit", "lie", "stand", "lie", "sit", "stand", "wave", "lie", "sit", "stand", "lie", "sit"]):
    figs[f"l{i + 1}"] = [pose, False]
figs.update({"str": ["lie", False], "gd": ["sit", False], "ft": ["stand", False], "ft1": ["wave1", False],
             "ft2": ["wave", False],
             "mop": ["hug", True]})
for i in range(1, 7):
    figs[f"v{i}"] = ["sit" if i % 2 else "lie", False]
GZ = 0.0
LAWN_FIGS = {"l1": (-1.3, -28.6, 20), "l2": (1.4, -29.6, -40), "l3": (0.4, -34.0, 200), "l4": (-9.5, -31.0, 70),
             "l5": (8.5, -33.0, 150), "l6": (-13.0, -26.0, 10), "l7": (12.5, -24.0, -70), "l8": (-2.0, -38.5, 100),
             "l9": (6.0, -22.0, 170), "l10": (-6.0, -35.5, 30), "l11": (3.0, -40.0, 80), "l12": (-11.0, -36.0, 250)}
for k, (x, y, yw) in LAWN_FIGS.items():
    obj(f"fig_{k}", 0, [x, y, GZ], yw)
    obj(f"fig_{k}", "L09", hide=True)

MOP_AT = [G.SHADOW_SIT[0], G.SHADOW_SIT[1], 0.085]
TEE_FACING = -17.0

# ---------------------------------------------------------------------------------------------- the story, scene by scene
SH = []


def shot(at, camera, step=2, hand=None, follow=None):
    SH.append((at, camera, step, hand, follow))


ax, ay = G.ROOM_A
bx, by = G.ROOM_B
cx, cy = G.ROOM_C
hx0, hy0 = G.HOUSE
HB = G.BENCH_HOUSE

# ===== 01 the rule (L01 to L08): lawns, bright late sun
look(0, "day")
cue(0, "sails", rate=8.0)
cue(0, "fenced", n=0)
cue(0, "gate", open=0.0)
cue(0, "door", open=0.0)
# L01
put("me", 0, [0.0, -26.2], 180, expr="neutral", head=[0, 3])
walk("me", "L01.2>", [0.0, -24.4])
put("c1", 0, [-2.8, -31.0], 180)
walk("c1", "L02", [-2.8, -28.3])
put("c2", 0, [2.6, -32.0], 180)
walk("c2", "L02", [2.6, -29.2])
put("c3", 0, [-12.0, -23.0], 90)
walk("c3", "L02", [2.0, -23.0])
put("c4", 0, [13.0, -26.0], -90)
walk("c4", "L02", [-1.0, -26.0])
shot(0, mv([0.2, -20.6, 1.5], [0.0, -26.2, 0.95], 34), hand=0.006)
shot("L01.2", mv([-5.0, -17.5, 0.6], [1.0, -28.0, 0.3], 30, [-4.4, -17.8, 0.6], [1.0, -28.0, 0.3], 30))
# L02: the shoes on the path, the bench's long shadow; then high over the lawn
hide("me", "L02")
hide("c1", "L02+0.1")
hide("c2", "L02+0.1")
put("c5", "L02", [-6.0, -25.0], 180)
shot("L02", mv([-6.0, -22.9, 0.2], [-6.0, -25.0, 0.2], 30))
put("c3", "L02.2", [-3.0, -20.0], 90)
walk("c3", "L03", [3.0, -20.0])
shot("L02.2", mv([0.0, -9.0, 12.0], [0.0, -28.0, 0.0], 28, [0.0, -10.0, 11.5], [0.0, -28.0, 0.0], 28))
# L03: a man cools off in a stranger's shadow
hide("c3", "L03")
hide("c4", "L03")
hide("c5", "L03")
put("c6", "L03", [-7.9, -21.0], 180, expr="soft", arms=[0, 100])
sit("c6", "L03", True, 0.06)
obj("fig_str", 0, [-7.0, -21.0, 0.0], 90)
shot("L03", mv([-7.7, -17.9, 1.0], [-7.9, -21.0, 0.75], 34))
# L04
hide("c6", "L04")
sit("c6", "L04", False)
obj("fig_gd", 0, [G.EX_DOOR[0], G.EX_DOOR[1] - 0.55, 0.19], 0)
put("gordon", "L04.2", [-22.7, -2.1], 180, expr="smirk")
put("gordon_wife", "L04.2", [-21.4, -2.1], 180, expr="neutral", arms=[75, 75])
shot("L04", mv([-22.0, -3.0, 1.0], [-22.0, 0.7, 0.45], 32))
shot("L04.2", mv([-18.6, -2.3, 1.45], [-22.1, -2.0, 1.35], 30))
# L05, L06
hide("gordon", "L05")
hide("gordon_wife", "L05")
put("footballer", "L05", [34.0, -18.7], 0, expr="soft", arms=[0, 150])
obj("fig_ft", 0, [34.0, -25.6, 0.04], 0)
obj("fig_ft", "L06+0.15", hide=True)
obj("fig_ft1", "L06+0.15", [34.0, -25.6, 0.04], 0)
obj("fig_ft1", "L06+0.55", hide=True)
obj("fig_ft2", "L06+0.55", [34.0, -25.6, 0.04], 0)
shot("L05", mv([33.0, -22.2, 1.5], [34.0, -18.7, 1.5], 34))
shot("L05.2", mv([36.4, -31.6, 2.9], [34.0, -25.4, 0.3], 30))
shot("L06", mv([34.4, -29.2, 3.3], [34.2, -25.3, 0.05], 36))
hide("footballer", "L07")
# L07: low behind me, the sun in front of me
look("L07", "front", 0)
put("me", "L07", [0.0, -24.6], 180, expr="neutral")
walk("me", "L07>", [0.0, -22.4])
shot("L07", mv([0.4, -30.6, 1.3], [0.0, -26.2, 0.0], 28), hand=0.004)
look("L08", "day", 0)
put("me", "L08", [-6.0, -24.0], 180, expr="neutral", head=[0, 12])
shot("L08", mv([-6.0, -20.4, 1.7], [-6.0, -24.0, 1.3], 34))

# ===== 02 the last week (L09 to L22): the course in warm sun
hide("me", "L09")
put("dad", "L09", [2.9, 1.7], -90, expr="smile")
shot("L09", mv([-0.4, 0.6, 1.65], [3.0, 1.75, 1.55], 32))
put("builder_a", "L09.1", [-7.6, 1.9], 90, expr="neutral", arms=[40, 40])
obj("survey", "L09.1", [-6.9, 1.9, 0.0])
shot("L09.1", mv([-5.2, -1.6, 1.4], [-7.3, 1.9, 0.9], 35))
obj("survey", "L11", hide=True)
hide("builder_a", "L11")
put("me", "L11", [0.0, -0.8], 180, expr="soft")
hold("dad", "L11", arms=[0, 150], expr="soft")
shot("L11", mv([-3.0, -3.6, 1.6], [1.3, 0.8, 1.4], 26))
# L12: builders lift a mesh panel; high wide with three holes fenced
hide("me", "L12")
put("builder_a", "L12", [-9.2, 1.9], 180, arms=[100, 100], expr="neutral")
put("builder_b", "L12", [-10.8, 1.9], 180, arms=[100, 100], expr="neutral")
hold("dad", "L12", arms=[0, 0], expr="soft")
obj("panel_a", "L12", [-10.0, 2.45, 0.0], 0)
cue("L12", "fenced", n=1)
shot("L12", mv([-7.4, -0.6, 1.6], [-10.0, 2.2, 1.2], 28))
hide("builder_a", "L12.2")
hide("builder_b", "L12.2")
obj("panel_a", "L12.2", hide=True)
cue("L12.2", "fenced", n=3)
shot("L12.2", mv([0.0, -6.0, 13.0], [0.0, 14.0, 0.0], 28))
# L13: visitors' shadows slide out under the gate
cue("L13", "fenced", n=5)
obj("fig_v1", 0, [-6.4, 5.8, 0.08], 40)
obj("fig_v1", "L13", [-6.4, 5.8, 0.08], 40)
obj("fig_v1", "L13+0.1", [-1.2, 1.9, 0.03], 40, dur=1.5)
obj("fig_v1", "L13.2", [-0.5, 0.6, 0.03], 5)
obj("fig_v1", "L13.2+0.1", [-0.5, -1.6, 0.01], 5, dur=1.0)
obj("fig_v2", "L13.2", [0.5, 1.5, 0.03], 175)
obj("fig_v2", "L13.2+0.1", [0.9, -1.9, 0.01], 175, dur=1.2)
shot("L13", mv([-1.8, 0.5, 0.25], [-4.8, 5.0, 0.1], 28))
shot("L13.2", mv([1.2, -3.0, 0.5], [0.0, 0.0, 0.3], 28))
# L14: they sit on the pavement against the railings
SIT_X = [-6.0, -4.0, -2.2, 2.4, 4.2, 6.0]
for i, x in enumerate(SIT_X, 1):
    obj(f"fig_v{i}", "L14", [x, -0.5, 0.01], 180)
cue("L14", "fenced", n=8)
shot("L14", mv([-7.5, -4.6, 1.1], [0.0, -0.7, 0.1], 26, [-6.5, -4.4, 1.0], [0.0, -0.7, 0.1], 26))
# L15: seventeen fenced, one shadow left on the last green
cue("L15", "fenced", n=17)
look("L15", "eve", 0)
obj("fig_mop", "L15", MOP_AT, TEE_FACING)
shot("L15", mv([0.0, -4.0, 15.0], [0.0, 22.0, 0.0], 28))
shot("L15.2", mv([2.6, 29.0, 1.5], [2.6, 25.0, 0.1], 32))
# L16: Dad putts
put("dad", "L16", [G.TEE_L[0], 19.95], 180, expr="neutral", arms=[40, 40])
obj("putter1", "L16", [-0.9, 20.62, 0.0], 0, rot=[19, 0, 0])
obj("ball1", "L16", [G.BALL_L[0], 20.85, 0.125])
shot("L16", mv([-3.4, 18.3, 1.4], [-0.9, 20.4, 1.0], 35))
# L17: he sits by the shadow with two putters
put("dad", "L17", [4.4, 24.35], -90, expr="neutral", arms=[0, 0])
sit("dad", "L17", True, 0.5)
obj("putter1", "L17", [4.22, 23.22, 0.66], 0, rot=[0, -14, 0])
obj("putter2", "L17", [4.34, 23.22, 0.66], 0, rot=[0, -9, 0])
obj("ball1", "L17", hide=True)
shot("L17", mv([1.5, 22.3, 1.25], [4.3, 24.0, 0.85], 30))
put("me", "L18", [5.7, 25.6], -50, expr="neutral")
shot("L18", mv([3.0, 21.4, 1.55], [5.5, 25.3, 1.45], 30))
shot("L19+0.3", mv([2.5, 21.8, 2.4], [2.6, 24.9, 0.05], 36))
hold("me", "L19.1", expr="soft")
shot("L19.1", mv([4.4, 21.9, 1.4], [4.4, 24.3, 1.4], 45))
# L20: the sails turn backwards
hide("me", "L20")
hide("dad", "L20")
sit("dad", "L20", False)
cue("L20", "sails", rate=-24.0)
shot("L20", mv([-2.0, 17.0, 1.6], [-8.8, 24.0, 3.2], 32))
# L21: every flag wound round its pole
cue("L21", "flag", which="all", wound=1)
shot("L21", mv([-4.0, 13.7, 1.1], [-4.0, 15.4, 1.08], 45))
shot("L21.1", mv([-10.5, 14.2, 0.8], [4.0, 15.4, 1.0], 30))
# L22: a second ball in the last cup
obj("ball1", "L22", [-0.05, 29.62, 0.1])
obj("ball2", "L22", [0.05, 29.58, 0.1])
shot("L22", mv([0.0, 29.79, 1.2], [0.0, 29.8, 0.0], 55))
put("dad", "L22.1", [0.6, 28.4], 160, expr="worried", head=[0, 22])
obj("putter1", "L22.1", [1.2, 28.4, 0.0], 0, rot=[0, 0, 0])
obj("putter2", "L22.1", [4.34, 23.22, 0.66], 0, rot=[0, -9, 0])
shot("L22.1", mv([2.3, 31.2, 1.6], [0.6, 28.5, 1.35], 32))

# ===== 03 Thursday (L23 to L36)
look("L23", "bedroom", 0)
hide("dad", "L23")
put("me", "L23", [ax + 0.2, ay + 0.9], 90, expr="neutral", arms=[40, 40], head=[0, 0])
shot("L23", mv([ax - 1.8, ay - 1.5, 1.5], [ax + 0.3, ay + 0.9, 1.1], 22))
look("L24", "dadroom", 0)
put("me", "L24", [bx, by - 2.1], 180, expr="worried", arms=[0, 0])
shot("L24", mv([bx - 1.5, by + 1.2, 1.5], [bx, by - 2.1, 1.3], 24))
hide("me", "P01")
look("P01", "midnight", 0)
cue("P01", "sails", rate=0.0)
shot("P01", mv([0.0, -7.0, 1.5], [0.0, 3.0, 1.2], 28))
shot("L25", mv([2.2, 21.6, 1.1], [4.4, 24.2, 0.7], 32))
obj("putter1", "L26", [0.2, 22.6, 0.11], 0, rot=[90, 0, 0])
obj("putter2", "L26", hide=True)
shot("L26", mv([0.0, 20.4, 0.2], [0.2, 22.3, 0.1], 32))
obj("flask", "L27", [4.45, 23.75, 0.48], 0)
obj("flask_lid", "L27", [4.2, 23.95, 0.48], 0)
put("me", "L27.1", [3.4, 24.8], -30, expr="scared", head=[-20, 0])
shot("L27", mv([3.5, 22.7, 0.85], [4.4, 23.8, 0.55], 40))
shot("L27.1", mv([1.7, 22.0, 1.6], [3.4, 24.8, 1.4], 30))
hide("me", "L28")
cue("L28", "flag", which="all", wound=2)
shot("L28", mv([0.0, -2.0, 12.0], [0.0, 16.0, 0.0], 26))
shot("L29", mv([-0.6, 27.3, 1.0], [2.6, 24.4, 0.15], 34))
put("me", "L30", [-11.0, 1.6], 90, expr="scared")
walk("me", "L30>", [-5.5, 1.6])
shot("L30", mv([2.3, -1.4, 1.5], [0.0, 0.0, 1.4], 30), follow="me", hand=0.01)
hide("me", "L31")
shot("L31", mv([-3.0, 16.8, 1.3], [-8.8, 25.0, 2.2], 34))
put("me", "L31.2", [-2.0, 17.6], 180, expr="scared")
shot("L31.2", mv([-2.0, 19.9, 1.55], [-2.0, 17.6, 1.5], 38))
# L32: the kitchen
look("L32", "kitchen", 0)
put("me", "L32", [cx - 1.0, cy + 0.2], 90, expr="worried")
sit("me", "L32", True, 0.46)
shot("L32", mv([cx - 1.6, cy - 1.5, 1.4], [cx - 0.9, cy + 0.3, 1.0], 22))
# L33: the front door opens onto dawn
hide("me", "L33")
sit("me", "L33", False)
look("L33", "dawn", 0)
cue("L33", "door", open=1.0, dur=0.9)
shot("L33", mv([hx0 - 0.8, hy0 + 3.2, 1.5], [hx0 - 0.8, hy0 - 3.0, 1.1], 26))
look("L34", "dawn2", 2.5)
put("dad", "L34", [HB[0], HB[1]], 0, expr="worried", arms=[20, 20])
sit("dad", "L34", True, 0.5)
shot("L34", mv([HB[0], HB[1] - 3.8, 1.45], [HB[0], HB[1], 1.2], 32))
hold("dad", "L35", expr="smirk", head=[0, -14])
shot("L35", mv([HB[0] + 0.4, HB[1] - 2.2, 1.35], [HB[0], HB[1], 1.4], 40))
shot("L36", mv([HB[0], HB[1] - 1.6, 1.0], [HB[0], HB[1], 1.1], 60))

# ===== 04 the second tee (L37 to L55)
look("L37", "dusk", 0)
cue("L37", "door", open=0.0)
hide("dad", "L37")
sit("dad", "L37", False)
cue("L37", "lastfence", on=True)
put("builder_a", "L37", [0.0, 17.5], 180, arms=[100, 100], expr="neutral")
put("builder_b", "L37", [1.6, 17.5], 180, arms=[100, 100], expr="neutral")
obj("putter1", "L37", hide=True)
obj("flask", "L37", hide=True)
obj("flask_lid", "L37", hide=True)
obj("ball1", "L37", hide=True)
obj("ball2", "L37", hide=True)
cue("L37", "sails", rate=6.0)
shot("L37", mv([-3.2, 15.8, 1.4], [0.8, 18.4, 1.2], 30))
hide("builder_a", "L38")
hide("builder_b", "L38")
put("dad", "L38", [-0.9, 16.8], 180, expr="neutral")
walk("dad", "L38>", [-0.9, 19.5])
obj("putter1", "L38", [-1.45, 16.8, 0.0])
obj("putter1", "L38+0.05", [-1.45, 19.5, 0.0], dur=1.6)
obj("putter2", "L38", [-0.35, 16.8, 0.0])
obj("putter2", "L38+0.05", [-0.35, 19.5, 0.0], dur=1.6)
shot("L38", mv([-0.4, 15.4, 1.3], [-0.9, 18.2, 1.1], 30))
put("dad", "L39.1", [G.TEE_L[0], 19.9], 180, expr="neutral", arms=[0, 0])
obj("putter1", "L39", hide=True)
obj("putter2", "L39", hide=True)
look("L39", "dusk_tee", 0.3)
shot("L39", mv([0.0, 15.0, 5.5], [0.0, 21.6, 0.0], 30))
shot("L39.1", mv([0.0, 17.2, 1.1], [0.0, 19.9, 0.7], 28))
obj("print1", "L40", [0.72, 19.9, 0.1], 0)
obj("print2", "L40", [1.08, 19.9, 0.1], 0)
put("me", "L40.1", [2.2, 16.9], 20, expr="worried")
shot("L40", mv([0.9, 18.6, 0.55], [0.9, 19.9, 0.1], 36))
shot("L40.1", mv([0.3, 14.6, 1.5], [2.2, 16.9, 1.4], 30))
hide("me", "L41")
put("dad", "L41", [G.TEE_L[0], 19.95], 180, expr="neutral", arms=[40, 40])
obj("putter1", "L41", [-0.9, 20.62, 0.0], 0, rot=[19, 0, 0])
obj("ball1", "L41", [G.BALL_L[0], 20.85, 0.125])
obj("ball1", "L41+0.4", [G.BALL_L[0], 24.5, 0.125], dur=2.0)
shot("L41", mv([-2.6, 18.6, 1.1], [-0.9, 20.2, 0.7], 30))
cue("L41.1", "flag", which="near", wound=2)
shot("L41.1", mv([2.9, 18.3, 1.1], [1.9, 19.2, 1.1], 45))
# L42: Saturday, the low sun under the windmill
look("L42", "dusk2", 1.0)
obj("ball1", "L42", hide=True)
obj("putter1", "L42", hide=True)
hold("dad", "L42", arms=[0, 0])
shot("L42", mv([-13.5, 24.0, 1.4], [0.0, 24.0, 0.8], 30))
shot("L42.2", mv([-3.4, 22.6, 1.6], [-0.9, 19.95, 1.55], 38))
# P02 and the reveal
wring("P02", 180.0)
shot("P02", mv([0.0, 17.9, 0.7], [0.62, 19.9, 0.75], 40))
shot("L43", mv([0.2, 16.9, 1.3], [0.9, 19.9, 1.4], 18))
shot("L44", mv([0.0, 16.3, 1.1], [0.0, 19.9, 1.0], 20))
shot("L45", mv([0.5, 16.9, 0.5], [0.9, 19.9, 0.8], 18, [0.5, 16.9, 1.0], [0.9, 19.9, 1.8], 18))
shot("L46", mv([-0.5, 17.1, 0.5], [0.9, 19.9, 1.2], 18, [-0.2, 17.1, 0.6], [0.9, 19.9, 1.2], 18))
shot("L47", mv([3.6, 19.9, 1.3], [0.9, 19.9, 1.3], 18))
shot("L47.2", mv([1.9, 19.2, 1.9], [0.9, 19.9, 1.9], 55))
shot("L48", mv([0.8, 16.9, 2.0], [0.9, 19.9, 2.3], 30))
shot("L49", mv([3.0, 8.0, 4.6], [-3.0, 21.0, 1.8], 22))
shot("L50", mv([3.5, 23.5, 0.5], [0.9, 19.9, 0.9], 24))
# L51: the string lights fade on
look("L51", "dusk_str", 1.5)
hold("dad", "L51", arms=[40, 40])
obj("putter1", "L51", [-0.9, 20.62, 0.0], 0, rot=[19, 0, 0])
obj("ball1", "L51", [G.BALL_L[0], 20.85, 0.125])
shot("L51", mv([-2.8, 18.4, 1.25], [-0.9, 20.1, 1.2], 32))
wring("L52", 240.0)
wring("L52.2", 300.0)
shot("L52", mv([0.9, 23.6, 1.4], [0.9, 19.9, 1.3], 28))
shot("L52.2", mv([0.9, 23.6, 1.4], [0.9, 19.9, 1.3], 28))
wring("L53", 360.0, head_extra=90.0)
shot("L53", mv([0.3, 22.6, 1.7], [0.2, 19.9, 1.7], 22))
wring("L54", 360.0, head_extra=90.0, lean=(0.0, 0.0))
wring("L54+0.2", 360.0, head_extra=90.0, lean=(0.0, 22.0), dur=1.4)
shot("L54", mv([3.6, 19.9, 1.4], [0.9, 19.9, 1.4], 22))
shot("L55", mv([-1.5, 22.5, 1.5], [-0.9, 19.95, 1.45], 36))

# ===== 05 the second reading (L56 to L69)
put("me", "L56", [0.1, 17.1], 180, expr="scared")
walk("me", "L56.1", [0.2, 18.9])
shot("L56", mv([-2.6, 17.4, 1.4], [0.1, 17.9, 1.3], 30))
put("me", "L57", [1.8, 23.5], 90, expr="worried")
shot("L57", mv([-1.5, 21.6, 3.2], [2.4, 24.0, 0.3], 28))
put("me", "L58", [1.7, 24.9], 0, expr="worried")
sit("me", "L58", True, 0.09)
shot("L58", mv([1.9, 22.0, 2.8], [2.2, 24.9, 0.2], 28))
sit("me", "L58.1", False)
put("me", "L58.1", [1.5, 23.8], 0, expr="worried", arms=[0, 0])
walk("me", "L58.1>", [1.5, 23.8], arms=[150, 0])
shot("L58.1", mv([1.5, 21.9, 1.6], [1.5, 23.8, 1.6], 40))
put("me", "L59", [1.0, 24.0], 0, expr="worried", head=[0, 32], arms=[0, 0])
shot("L59", mv([1.0, 21.8, 1.5], [1.0, 24.0, 1.3], 34))
put("me", "L60", [-1.2, 23.8], 0, expr="worried", head=[0, 32])
shot("L60", mv([-0.3, 27.6, 3.0], [-0.3, 23.8, 0.0], 24))
look("L61", "dusk_str2", 1.0)
shot("L61", mv([3.6, 22.4, 0.8], [2.6, 25.0, 0.1], 34))
put("dad", "L61.2", [2.9, 25.7], 0, expr="neutral")
obj("putter2", "L61.2", [4.34, 23.22, 0.66], 0, rot=[0, -9, 0])
put("me", "L61.2", [-1.0, 26.0], 90, expr="worried")
shot("L61.2", mv([2.9, 22.2, 1.4], [2.9, 25.6, 1.3], 34, [2.9, 23.3, 1.4], [2.9, 25.6, 1.3], 34))
put("dad", "L62", [0.9, 25.6], -90, expr="neutral")
shot("L62", mv([-0.1, 22.4, 1.2], [-0.1, 25.8, 0.8], 30))
hold("me", "L63", expr="soft", yaw=50)
shot("L63", mv([0.8, 23.2, 1.55], [-1.0, 26.0, 1.5], 34))
# L64: Thursday night under my window, then the pavement shadows
hide("me", "L64")
hide("dad", "L64")
look("L64", "win_lit", 0)
look("L64+0.4", "win_dark", 1.2)
put("dad", "L64", [HB[0], HB[1]], 0, expr="worried", head=[0, -22])
sit("dad", "L64", True, 0.5)
shot("L64", mv([HB[0], HB[1] - 4.0, 1.7], [HB[0], HB[1], 1.9], 28))
look("L64.3", "dusk_str", 0)
hide("dad", "L64.3")
sit("dad", "L64.3", False)
shot("L64.3", mv([-7.5, -4.6, 1.1], [0.0, -0.7, 0.1], 26, [-6.5, -4.4, 1.0], [0.0, -0.7, 0.1], 26))
# L65: the second putter
obj("putter1", "L65", hide=True)
obj("putter2", "L65", [4.34, 23.22, 0.66], 0, rot=[0, -9, 0])
shot("L65", mv([2.6, 22.6, 1.0], [4.3, 23.3, 0.5], 35))
put("me", "L65.1", [3.4, 24.0], -90, expr="worried", arms=[0, 35])
obj("putter2", "L65.1", [3.0, 23.5, 0.0], 0, rot=[0, 0, 0])
shot("L65.1", mv([3.4, 21.6, 1.4], [3.4, 24.0, 1.1], 32))
# L66, L67: onto the second tee, face to face
put("me", "L66", [0.9, 18.6], 180, expr="scared", arms=[0, 35])
walk("me", "L66>", [0.9, 19.15], arms=[0, 35])
obj("putter2", "L66", [0.39, 18.9, 0.0], 0, rot=[0, 0, 0])
obj("putter2", "L66+0.05", [0.39, 19.45, 0.0], dur=1.0)
shot("L66", mv([-0.5, 18.2, 0.2], [0.9, 19.3, 0.15], 30))
wring("L67", 180.0, lean=(-28.0, 0.0), head_extra=70.0)
obj("putter2", "L67", [0.39, 19.45, 0.0])
hold("me", "L67", yaw=75, expr="scared")
shot("L67", mv([2.9, 18.3, 2.6], [0.9, 19.45, 1.9], 20))
# L68: I putt; the tee is just me
hide("me", "L68")
put("me", "L68", [0.9, 19.55], 180, expr="neutral", arms=[0, 35])
wring("L68", 180.0, hide_=True)
obj("putter2", "L68", [0.39, 19.95, 0.0])
obj("ball2", "L68", [0.9, 20.7, 0.125])
obj("ball2", "L68+0.35", [0.9, 23.4, 0.125], dur=1.4)
shot("L68", mv([-1.4, 18.4, 1.0], [0.9, 20.0, 0.5], 30))
put("dad", "L68.1", [G.TEE_L[0], 19.95], 120, expr="soft")
shot("L68.1", mv([0.0, 17.9, 1.4], [0.0, 19.9, 1.35], 24))
# L69: the last hole together
put("dad", "L69", [-0.8, 23.0], 180, expr="soft")
walk("dad", "L69.2", [-0.6, 25.8])
put("me", "L69", [0.8, 23.0], 180, expr="soft", arms=[0, 0])
walk("me", "L69.2", [0.6, 25.8])
obj("putter2", "L69", hide=True)
obj("ball1", "L69", [-0.9, 24.5, 0.125])
obj("ball1", "L69+0.05", [-0.05, 29.58, 0.1], dur=1.1)
obj("ball2", "L69", [0.9, 23.4, 0.125])
obj("ball2", "L69+0.05", [0.05, 29.58, 0.1], dur=1.0)
shot("L69", mv([0.0, 20.8, 2.0], [0.0, 27.0, 0.6], 26))
shot("L69.2", mv([0.0, 29.15, 0.85], [0.0, 29.45, 0.1], 50))

# ===== 06 the last round (L70 to L76)
look("L70", "sunday", 0)
hide("me", "L70")
hide("dad", "L70")
cue("L70", "lastfence", on=False)
cue("L70", "fenced", n=0)
cue("L70", "gate", open=1.0, dur=1.0)
cue("L70", "sails", rate=10.0)
for i, who in enumerate(["c1", "c2", "c3", "c4", "c5", "c6"]):
    put(who, "L70", [-3.5 + i * 1.4, -2.6 - (i % 2) * 0.8], 180, expr="soft" if i % 2 else "neutral")
put("dad", "L70", [1.9, 0.9], 0, expr="soft")
for i in range(1, 7):
    obj(f"fig_v{i}", "L70", [SIT_X[i - 1], -0.5, 0.01], 180)
shot("L70", mv([-1.0, -7.0, 1.6], [0.0, 0.8, 1.3], 24))
# L71: the whole town plays
spots = {"c1": (-9.6, 5.0), "c2": (-5.6, 10.4), "c3": (6.4, 4.6), "c4": (9.8, 10.2), "c5": (-3.6, 15.0),
         "c6": (0.2, 14.8), "c7": (4.0, 14.6), "c8": (8.2, 14.2)}
for who, (x, y) in spots.items():
    put(who, "L71", [x, y], 180 if who in ("c1", "c3", "c5", "c7") else 20, expr="soft")
put("gordon", "L71", [-2.5, 4.8], 90, expr="soft")
put("gordon_wife", "L71", [-1.6, 4.9], 90, expr="soft")
put("footballer", "L71", [-7.0, 23.5], 90, expr="soft")
put("dad", "L71", [1.9, 0.9], 0, expr="soft")
shot("L71", mv([0.0, -5.0, 12.0], [0.0, 16.0, 0.0], 26))
# L72: the shadows slide back in
for who in ("c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "gordon", "gordon_wife", "footballer"):
    hide(who, "L72")
INSIDE = {1: (-6.5, 6.4), 2: (-3.0, 11.0), 3: (3.0, 6.0), 4: (7.0, 11.2), 5: (-2.0, 16.0), 6: (5.5, 16.2)}
for i in range(1, 7):
    obj(f"fig_v{i}", "L72+0.05", [INSIDE[i][0], INSIDE[i][1], 0.03], 180, dur=1.6)
shot("L72", mv([0.6, -3.2, 0.7], [0.0, 0.0, 0.3], 28))
put("c1", "L72.2", [INSIDE[1][0] - 1.0, INSIDE[1][1] - 0.4], 90, expr="soft")
put("c3", "L72.2", [INSIDE[3][0] + 1.0, INSIDE[3][1] - 0.4], -90, expr="soft")
put("c2", "L72.2", [INSIDE[2][0] + 1.1, INSIDE[2][1]], -90, expr="soft")
shot("L72.2", mv([-4.0, 8.5, 0.6], [-1.0, 8.2, 0.3], 28))
# L73: Dad's shadow runs from my feet to his
look("L73", "gold", 0)
for who in ("c1", "c2", "c3", "dad"):
    hide(who, "L73")
for i in range(1, 7):
    obj(f"fig_v{i}", "L73", hide=True)
put("dad", "L73", [0.9, 25.6], -90, expr="soft")
put("me", "L73", [-1.0, 26.0], 90, expr="soft")
shot("L73", mv([-0.1, 21.0, 3.3], [-0.05, 25.8, 0.0], 26))
shot("L73.2", mv([0.0, 22.0, 4.6], [0.0, 26.0, 0.0], 26))
# L74 to L76: late gold, the mop shadow alone, then the cold line
hide("dad", "L74")
hide("me", "L74")
shot("L74", mv([2.0, 22.0, 3.9], [2.7, 25.1, 0.0], 24, [2.3, 22.8, 3.5], [2.7, 25.1, 0.0], 24))
put("me", "L75", [-0.4, 1.0], 0, expr="neutral")
shot("L75", mv([-1.0, -4.4, 2.4], [0.4, 1.0, 0.1], 26))
hide("me", "L76")
look("L76", "gold2", 2.0)
obj("survey", "L76", [3.3, 25.2, 0.085])
shot("L76", mv([1.4, 22.2, 3.6], [2.8, 25.0, 0.0], 24, [1.8, 22.8, 3.3], [2.8, 25.0, 0.0], 24))

# ---------------------------------------------------------------------------------------------- finish the lists
# the creature starts hidden; the "x" placeholder cue is dropped
cue(0, "wring", pos=[0, 0], yaw=180, wring=180, lean=[0, 0], head_extra=0, hide=True)

for k_ in acting.values():
    remap_all(k_)
remap_all(cues)
shots = []
for i, (at, camera, step, hand, follow) in enumerate(SH):
    s = {"id": f"S{i + 1:03d}", "cam": camera, "step": step}
    if i:
        s["at"] = remap(at)
    if hand is not None:
        s["hand"] = hand
    if follow:
        s["follow"] = follow
    shots.append(s)

# ---------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L16", "kind": "click", "db": -13}, {"at": "L16+0.3", "kind": "whoosh", "db": -26},
    {"at": "L22", "kind": "click", "db": -15},
    {"at": "L12", "kind": "thud", "db": -12}, {"at": "L12.2", "kind": "click", "db": -14},
    {"at": "L37", "kind": "thud", "db": -11}, {"at": "L37+0.25", "kind": "click", "db": -13},
    {"at": "L31", "kind": "creak", "db": -12, "dur": 1.5}, {"at": "L41.1-0.3", "kind": "creak", "db": -14, "dur": 1.2},
    {"at": "L41+0.1", "kind": "click", "db": -13}, {"at": "L41+0.4", "kind": "whoosh", "db": -24},
    {"at": "L52", "kind": "creak", "db": -13, "dur": 1.0}, {"at": "L52.2", "kind": "creak", "db": -12, "dur": 1.0},
    {"at": "L54", "kind": "creak", "db": -14, "dur": 1.6},
    {"at": "L33", "kind": "door", "db": -15},
    {"at": "L51+0.5", "kind": "click", "db": -14},
    {"at": "L68", "kind": "click", "db": -12}, {"at": "L68+0.35", "kind": "whoosh", "db": -24},
    {"at": "L69+0.9", "kind": "click", "db": -14}, {"at": "L69+1.05", "kind": "click", "db": -14},
    {"at": "L67", "kind": "creak", "db": -16, "dur": 1.3},
    {"at": "P01", "kind": "breath", "db": -18, "dur": 0.6, "keep": True},
    {"at": "P02", "kind": "breath", "db": -18, "dur": 0.7, "keep": True},
    {"at": "P02+0.62", "kind": "creak", "db": -3, "dur": 1.3, "keep": True},
    {"at": "L76.1", "kind": "glide", "db": -18, "dur": 1.2},
    {"at": "L70", "kind": "door", "db": -18},
]
music = {
    "root": 55, "mode": "lydian", "bpm": 92, "seed": 48,
    "sections": [
        {"at": 0, "voices": ["piano"], "energy": 0.3, "root": 55, "mode": "lydian"},
        {"at": "L15", "voices": ["piano", "pad"], "energy": 0.3, "root": 55, "mode": "lydian"},
        {"at": "L23", "voices": ["piano"], "energy": 0.15, "root": 55, "mode": "lydian"},
        {"at": "L25", "voices": ["drone", "piano"], "energy": 0.8, "root": 43, "mode": "phrygian"},
        {"at": "L37", "voices": ["drone", "piano"], "energy": 0.6, "root": 43, "mode": "phrygian"},
        {"at": "L43", "voices": ["drone"], "energy": 0.9, "root": 43, "mode": "phrygian"},
        {"at": "L56", "voices": ["drone", "piano"], "energy": 0.5, "root": 43, "mode": "phrygian"},
        {"at": "L65", "voices": ["drone", "pad", "piano"], "energy": 0.6, "root": 43, "mode": "major"},
        {"at": "L74", "voices": ["drone"], "energy": 0.9, "root": 43, "mode": "phrygian"},
    ],
}
sound = {
    "floor": "grass", "steps_db": -23,
    "floor_spans": [{"from": "L23", "to": "L25", "floor": "wood"}, {"from": "L32", "to": "L34", "floor": "wood"}],
    "ambience": [
        {"kind": "wind", "from": 0, "to": "L23", "lufs": -37},
        {"kind": "hum", "from": 0, "to": "L23", "lufs": -45},
        {"kind": "drone", "from": "L25", "to": "end", "lufs": -30},
        {"kind": "crickets", "from": "L25", "to": "L33", "lufs": -40},
        {"kind": "wind", "from": "L33", "to": "L70", "lufs": -40},
        {"kind": "room", "from": "L70", "to": "L74", "lufs": -35},
    ],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>", "keep": ["breath"]},
                    {"from": "P02", "to": "P02>", "keep": ["breath", "creak"]}],
}

story = {
    "slug": "ep48-crazy-golf",
    "title": "In this town, your shadow stays where you were happiest",
    "made_for_kids": False,
    "premise": ("In a town where nobody's shadow stays under them and each one sits wherever its owner was happiest, "
                "I come home for the last week of my dad's crazy golf course and watch the old visitors' shadows slip "
                "out under the gate while something wrung like a cloth begins to stand on the last hole's second tee."),
    "twist": ("The shadow on the last green is mine, from the summers he taught me the course, and the round-headed "
              "one at my own feet is his: his happiest place is wherever I am. The second tee was built for a second "
              "player, so I step onto it and play the last hole with him."),
    "world": ("A fenced crazy-golf course in a town park in its closing week: eighteen small greens with painted posts, "
              "a white windmill, a pond bridge, a cream kiosk, builders' mesh fences going up every morning, a "
              "bench and lamp post by the last green, Dad's brick house across the lawns."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffc94a",
    "gap": 0.12,
    "tail": 0.25,
    "look": {"fog": "#8c88a8", "fog_density": 0.012, "fog_start": 14.0, "sky": "#9bb6d8", "sky_strength": 1.0,
             "exposure": 0.35, "flash_safe": True},
    "grade": {"shadows": [-0.02, 0.0, 0.04], "highlights": [0.04, 0.015, -0.03], "saturation": 1.0, "contrast": 1.06,
              "vignette": 0.3, "bloom": 0.3, "grain": 0.012, "red_line": 0.79},
    "phonemes": {},
    "figs": figs,
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["floor_spans"])
remap_all(sound["ambience"])
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
