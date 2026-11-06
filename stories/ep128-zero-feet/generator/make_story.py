"""Writes ../story.json for ep128 "zero feet" (script.md, 2026-11-05). Run: python stories/ep128-zero-feet/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90. Time references use the script's own chunk numbers; captions are split by timeline.split_lines and
the references are remapped.

Batch 13: nothing blinks, pulses, flickers or switches, so there are no lights cues at all. Day and night are separate
places (layout.py), cut between. The only cues are who sits and Mom's frozen pose.
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(ROOT))
import layout as G  # noqa: E402
from blocky import timeline  # noqa: E402

OUT = HERE.parent / "story.json"
REV = 2
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = timeline.split_lines(orig_lines)
idx = next(i for i, l in enumerate(lines) if l["id"] == "L24")
lines.insert(idx, {"id": "P01", "pause": 0.6, "chunks": [["", ""]]})     # the 0.6 s music drop before L24


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
LAND = G.LAND_Z
UP = -24.0          # head pitch that looks up (checked on the stills)


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return [[0, list(p0), list(t0), l0]]
    return [[0, list(p0), list(t0), l0], [1, list(p1), list(t1 if t1 is not None else t0), l1 or l0]]


def A(O, x, y, z=0.0):
    return [O[0] + x, O[1] + y, z]


def fc(O, tx, ty, tz, d, lens, dx=0.0, dz=0.0, push=0.12, az=0.0, lens2=None):
    """A camera d metres from the target, on the -y side turned az degrees round it, with a slow push in."""
    a = az * D2R
    tgt = [O[0] + tx, O[1] + ty, tz]
    p0 = [tgt[0] + dx + d * math.sin(a), tgt[1] - d * math.cos(a), tz + dz]
    p1 = [tgt[0] + dx * (1 - push) + d * (1 - push) * math.sin(a), tgt[1] - d * (1 - push) * math.cos(a), tz + dz]
    return mv(p0, tgt, lens, p1, tgt, lens2 or lens)


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
    "me": person("#d9a374", "#4caf50", "#8b9098", "#f4f4f2", hair="mop", hair_c="#5a3a22", extras=["hooddown"],
                 extra_c="#43a047", brow_w=1.7),
    "mom": person("#d9a374", "#7cc4ff", "#c9b8f5", "#ff8fc8", hair="cap", hair_c="#3b2418",
                  eyes="lashes", extras=["coat"], extra_c="#7cc4ff", brow_w=1.6,
                  pants_pattern="stripes", pants_pattern_c="#ffffff"),
    "grandpa": person("#e9c6a0", "#9a7452", "#4a4a52", "#3a2a1a", hair="cap", hair_c="#f4f4f4", pattern="knit",
                      pattern_c="#7a5a3c", extras=["glasses"], extra_c="#3a3a3e", brow_w=1.4),
    "grandma": person("#e9c6a0", "#ee94b0", "#6a5a7a", "#7a5a4a", hair="bun", hair_c="#f2f2f2", pattern="knit",
                      pattern_c="#c76a89", eyes="lashes", extras=["glasses"], extra_c="#c04a7a", brow_w=1.3),
    "trucker": person("#c58c60", "#c94a3a", "#3a4f78", "#3a2a22", hair="cap", hair_c="#2a1d15", pattern="plaid",
                      pattern_c="#2a2a2a", hat="ballcap", hat_c="#e8a33a", brow_w=1.5, width=1.05),
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


def shot(at, camera, name, step=2, hand=None, follow=None):
    SH.append((at, camera, step, hand, follow, name))


def sit(who, at, on=True, z=0.62):
    cue(at, "sit", who=who, on=on, z=z)


def freeze(at, on=True):
    cue(at, "freeze", who="mom", on=on)


# ---------------------------------------------------------------------------------------------- places
AD, AB, AN = G.APT_D, G.APT_B, G.APT_N
SD, SN = G.ST_D, G.ST_N
CX, CY = G.COUCH_X, G.COUCH_Y
STX, STY = 1.4, 2.3                 # my kitchen spot
MOMX, MOMY = -0.55, G.MOM_XY[1]
MZ = LAND                            # the flat's floor


def me_seat(O, at, expr, **kw):
    put("me", at, A(O, CX, CY), 0, expr=expr, **kw)
    sit("me", at)


def me_stand(O, at, x, y, expr, yaw=0, **kw):
    sit("me", at, False)
    put("me", at, A(O, x, y), yaw, expr=expr, **kw)


def mom_stand(at, x, y, expr, yaw=0, **kw):
    kw.setdefault("arms", [35, -25])
    put("mom", at, [SN[0] + x, SN[1] + y, MZ], yaw, expr=expr, **kw)


def hookcam(O, push):
    """Me on the couch, the 0 phone flat on the seat beside me, seen from a little above so the phone reads flat."""
    return fc(O, -1.08, CY, 0.95, 3.3, 36, dx=0.0, dz=0.95, push=push)


def momcam(tz, d, lens, dx=0.0, tx=MOMX, ty=MOMY, **kw):
    return fc(SN, tx, ty, MZ + tz, d, lens, dx=dx, **kw)


# ===== 01 the hook, the rule, the montage (L01 to L06)
only(0, ["me"])
me_seat(AD, 0, "worried", head=[0, UP])
shot(0, hookcam(AD, 0.08), "hook")
beat("me", "L01+0.5", head=[0, UP - 4])
shot("L01+0.5", fc(AD, CX, CY, 1.5, 2.1, 40, dx=0.1, dz=0.05, push=0.1), "hook2")
beat("me", "L02", expr="neutral", head=[0, 0])
shot("L02", fc(AD, CX - 0.1, CY, 1.0, 4.7, 32, dx=0.4, dz=0.2), "alone")
beat("me", "L03.1", expr="neutral", head=[-6, 0])
shot("L03", mv(A(AD, G.PHONE_COUCH[0], 3.35, 1.35), A(AD, G.PHONE_COUCH[0], 4.5, 0.47), 34,
               A(AD, G.PHONE_COUCH[0], 3.6, 1.2), A(AD, G.PHONE_COUCH[0], 4.5, 0.47), 34), "phone1")
shot("L03.1", fc(AD, CX, CY, 1.5, 3.0, 42, dx=0.2, dz=0.0), "face3")
shot("L03.2", fc(AD, CX, CY, 1.5, 3.3, 38, dx=-0.5, dz=0.1, az=14, push=0.2), "face3b")
# L04: Grandpa's den, Grandma in his armchair
only("L04", ["grandpa", "grandma"])
put("grandma", "L04", [G.DEN[0] + 0.6, G.DEN[1] + 4.2], 0, expr="smile")
sit("grandma", "L04")
put("grandpa", "L04", [G.DEN[0] + 1.7, G.DEN[1] + 4.3], 0, expr="smile")
beat("grandpa", "L04.1", expr="delighted")
shot("L04", fc(G.DEN, 1.1, 4.2, 1.4, 2.85, 23, dx=0.0, dz=0.9, push=0.04), "den")
only("L04.2", ["grandma"])
beat("grandma", "L04.2", expr="delighted", head=[8, 0])
shot("L04.2", fc(G.DEN, 0.95, 4.2, 1.2, 3.0, 28, dx=0.0, dz=0.5, push=0.08), "den2")
# L05: the trucker at the diner
only("L05", ["trucker"])
put("trucker", "L05", [G.DINER[0] + 0.0, G.DINER[1] + 4.4], 0, expr="neutral")
sit("trucker", "L05")
shot("L05", fc(G.DINER, 0.3, 4.2, 1.15, 4.2, 34, dx=0.1, push=0.1), "diner")
shot("L05.2", mv(A(G.DINER, 0.75, 2.2, 1.85), A(G.DINER, 0.75, 3.12, 1.0), 30, A(G.DINER, 0.75, 2.4, 1.75), A(G.DINER, 0.75, 3.12, 1.0), 30),
     "phone900")
# L06: my old phone on my childhood desk, the hallway, Mom's door
only("L06", [])
shot("L06", mv(A(G.HALL_D, 0.45, 2.8, 1.3), A(G.HALL_D, -0.7, 2.8, 0.8), 34, A(G.HALL_D, 0.2, 2.8, 1.15), A(G.HALL_D, -0.7, 2.8, 0.8), 34),
     "oldphone")
shot("L06.3", mv(A(G.HALL_D, 0.0, 0.9, 1.5), A(G.HALL_D, 0.0, 7.5, 1.45), 30, A(G.HALL_D, 0.0, 1.7, 1.5), A(G.HALL_D, 0.0, 7.5, 1.45), 30),
     "hallmom")

# ===== 02 the apartment, the zero, the mornings (L07 to L12)
only("L07", ["me"])
put("me", "L07", [G.CAR[0] - 0.45, G.CAR[1] + 0.35], 0, expr="smile")
sit("me", "L07")
shot("L07", fc(G.CAR, -0.45, 0.2, 1.4, 3.6, 38, dz=0.1, push=0.1), "car")
only("L07.2", [])
shot("L07.2", mv(A(AB, 2.2, 0.5, 1.2), A(AB, -0.9, 2.8, 0.6), 30, A(AB, 1.6, 0.9, 1.15), A(AB, -0.9, 2.8, 0.6), 30), "boxes")
shot("L08", mv(A(AB, 2.3, 0.3, 1.55), A(AB, -0.4, 4.4, 1.0), 26, A(AB, 1.8, 0.5, 1.5), A(AB, -0.4, 4.4, 1.0), 26), "oneroom")
shot("L09", mv(A(AD, 1.35, 3.5, 1.75), A(AD, 2.5, 3.5, 0.96), 36, A(AD, 1.55, 3.5, 1.55), A(AD, 2.5, 3.5, 0.96), 36), "phone0")
me_stand(AD, "L10", 1.0, 3.5, "wide", tremble=3.0)
shot("L10", fc(AD, 1.0, 3.5, 1.57, 2.7, 42, dx=-0.1, push=0.1), "shook")
beat("me", "L10.1", expr="wide", tremble=0.0)
shot("L10.1", mv(A(AD, 1.2, 3.1, 1.6), A(AD, 2.5, 3.5, 0.96), 36, A(AD, 1.45, 3.3, 1.45), A(AD, 2.5, 3.5, 0.96), 36), "still0")
only("L11", [])
shot("L11", fc(G.FRIDGE, -0.2, 2.6, 1.05, 4.3, 36, dz=0.1, push=0.1), "fridge")
me_stand(AD, "L11.2", 1.95, 4.0, "worried")
shot("L11.2", fc(AD, 1.95, 4.0, 1.57, 2.7, 42, dx=-0.2, push=0.1), "fridgeface")
only("L12", [])
shot("L12", mv(A(AD, -1.7, 2.0, 1.45), A(AD, -2.3, 3.5, 0.4), 38, A(AD, -1.9, 2.4, 1.15), A(AD, -2.3, 3.5, 0.4), 38), "laundry")
put("me", "L12.2", A(AD, -1.4, 3.0), 0, expr="wide")
shot("L12.2", fc(AD, -1.4, 3.0, 1.57, 2.6, 42, dx=0.2, push=0.1), "foldface")

# ===== 03 the nights (L13 to L19)
only("L13", ["me"])
me_seat(AN, "L13", "neutral")
shot("L13", hookcam(AN, 0.08), "night")
only("L14", [])
sit("me", "L14", False)
shot("L14", mv(A(AN, 0.6, 1.8, 0.45), A(AN, 0.3, 3.0, 2.85), 28, A(AN, 0.5, 2.0, 0.45), A(AN, 0.1, 3.2, 2.85), 28), "ceiling1")
put("me", "L15", A(AN, -0.45, 4.2), 40, expr="neutral")
go("me", "L15+1.1", A(AN, STX, STY), yaw=40)
beat("me", "L15+1.15", yaw=0, expr="neutral")
shot("L15", mv(A(AN, 0.5, -0.7, 1.55), A(AN, 0.45, 3.6, 1.25), 22, A(AN, 0.55, -0.3, 1.55), A(AN, 0.6, 3.3, 1.3), 22), "walk")
only("L15.2", [])
shot("L15.2", mv(A(AN, -0.3, 1.2, 0.4), A(AN, 2.7, 2.4, 2.55), 28, A(AN, -0.2, 1.4, 0.4), A(AN, 2.7, 2.6, 2.65), 28), "ceiling2")
put("me", "L16", A(AN, STX, STY), 0, expr="worried", head=[0, UP])
shot("L16", fc(AN, STX, STY, 1.55, 2.7, 44, dx=-0.2, push=0.1), "stopped")
beat("me", "L17", expr="scared", head=[0, UP - 4])
shot("L17", fc(AN, STX, STY, 1.6, 2.7, 44, dx=0.1, push=0.06), "scared1")
# L18: the stairwell by day, the tally on the newel post
only("L18", [])
shot("L18", mv(A(SD, -0.45, -2.6, 1.6), A(SD, -0.45, 6.4, 2.5), 22, A(SD, -0.4, -2.3, 1.6), A(SD, -0.4, 6.4, 2.55), 22), "stairs")
shot("L18.2", mv(A(SD, 0.3, 1.8, 1.9), A(SD, 0.0, 6.4, 3.6), 30, A(SD, 0.15, 2.4, 2.4), A(SD, 0.0, 6.4, 3.7), 30), "stairs2")
put("me", "L19", A(SD, 0.0, -2.55), 180, expr="worried", head=[0, UP + 6])
sit("me", "L19", False)
shot("L19", mv(A(SD, 0.25, 2.9, 3.1), A(SD, 0.0, -2.55, 1.55), 66, A(SD, 0.2, 2.3, 2.9), A(SD, 0.0, -2.55, 1.6), 66), "atdoor")

# ===== 04 the freeze (L20 to L23, the drop)
me_stand(AN, "L20", 0.0, 2.8, "neutral")
shot("L20", fc(AN, 0.0, 2.8, 1.5, 3.4, 38, dx=0.1, push=0.1), "still1")
shot("L20.2", fc(AN, 0.0, 2.8, 1.52, 2.1, 42, dx=-0.1, push=0.1), "still2")
only("L21", [])
shot("L21", mv(A(AN, 0.9, 4.6, 0.45), A(AN, 0.3, 3.0, 2.85), 28, A(AN, 0.8, 4.4, 0.45), A(AN, 0.4, 2.9, 2.85), 28), "ceiling3")
put("me", "L22", A(AN, 0.3, 2.7), 0, expr="worried")
go("me", "L22.1+0.1", A(AN, -0.3, 2.7))
beat("me", "L22.1>", yaw=0, expr="worried")
shot("L22", mv(A(AN, 0.1, 0.0, 0.45), A(AN, -0.05, 2.7, 0.2), 25, A(AN, 0.05, 0.2, 0.4), A(AN, -0.05, 2.7, 0.2), 25), "feet")
put("me", "L23", A(AN, -0.3, 2.7), 0, expr="scared", head=[0, UP])
shot("L23", fc(AN, -0.3, 2.7, 1.55, 2.4, 46, dx=0.1, push=0.1), "scared2")
only("P01", [])
shot("P01", mv(A(AN, 1.6, 0.7, 0.4), A(AN, -0.5, 3.0, 2.8), 28, A(AN, 1.5, 0.9, 0.4), A(AN, -0.4, 3.0, 2.8), 28), "ceiling4")

# ===== 05 the stairs and the reveal (L24 to L33)
put("me", "L24", A(SN, 0.0, -2.55), 180, expr="scared")
go("me", "L24.1", A(SN, 0.0, -2.55), yaw=180)
go("me", "L24.1+0.9", A(SN, 0.0, 4.0, LAND), yaw=180, run=True)
shot("L24", mv(A(SN, 0.45, 3.4, 3.3), A(SN, 0.0, -2.5, 1.5), 62, A(SN, 0.3, 1.2, 2.0), A(SN, 0.0, 0.2, 1.7), 40), "run")
only("L25", [])
shot("L25", mv(A(SN, 0.1, 3.9, LAND + 1.5), A(SN, 0.0, 9.6, LAND + 1.35), 22, A(SN, 0.05, 4.3, LAND + 1.5), A(SN, 0.0, 9.6, LAND + 1.35), 22),
     "opendoor")
only("L26", ["mom"])
mom_stand("L26", MOMX, MOMY, "sad-smile")
freeze("L26")
sit("me", "L26", False)
shot("L26", momcam(1.05, 2.7, 34, push=0.04, az=32), "frozen")
shot("L26.1", mv([SN[0] + 1.9, SN[1] + MOMY - 1.7, MZ + 0.45], [SN[0] + MOMX - 0.05, SN[1] + MOMY, MZ + 0.25], 24,
                 [SN[0] + 1.8, SN[1] + MOMY - 1.6, MZ + 0.45], [SN[0] + MOMX - 0.05, SN[1] + MOMY, MZ + 0.25], 24), "slippers")
put("me", "L26.2", A(SN, 0.0, 6.55, LAND), 180, expr="scared")
shot("L26.2", mv(A(SN, 0.5, 9.0, LAND + 1.7), A(SN, 0.0, 6.55, LAND + 1.55), 44, A(SN, 0.4, 8.7, LAND + 1.7), A(SN, 0.0, 6.55, LAND + 1.55), 44),
     "mefreeze")
only("L27", ["mom"])
shot("L27", momcam(1.55, 3.3, 52, dx=0.35, push=0.1), "momface")
beat("mom", "L28", expr="sad-smile")
shot("L28", momcam(1.55, 2.8, 52, dx=0.3, push=0.08), "momface2")
beat("mom", "L28+0.5", expr="smile")
only("L29", ["me"])
put("me", "L29", A(SN, 0.0, 6.55, LAND), 180, expr="wide")
shot("L29", mv(A(SN, -0.3, 9.0, LAND + 1.7), A(SN, 0.0, 6.55, LAND + 1.55), 44, A(SN, -0.2, 8.7, LAND + 1.7), A(SN, 0.0, 6.55, LAND + 1.55), 44),
     "mestunned")
only("L30", ["mom"])
shot("L30", momcam(1.55, 2.7, 52, dx=0.35, push=0.1), "momsmile")
mom_stand("L30", MOMX, MOMY, "smile")
# L31: I walk to my kitchen on "Every step I took", Mom walks to hers on "she took it TOO"
freeze("L31", False)
only("L31", ["me"])
put("me", "L31", A(AN, -0.45, 4.2), 40, expr="neutral")
go("me", "L31+0.95", A(AN, STX, STY), yaw=40)
beat("me", "L31+1.0", yaw=0)
shot("L31", mv(A(AN, 0.3, 0.7, 1.5), A(AN, 0.3, 3.4, 1.4), 24, A(AN, 0.95, 0.7, 1.5), A(AN, 1.2, 2.6, 1.4), 24), "mewalk")
only("L31.2", ["mom"])
put("mom", "L31.2", [SN[0] - 0.3, SN[1] + 10.9, MZ], 0, expr="smile", arms=[0, 0])
go("mom", "L31.2+0.15", [SN[0] - 0.3, SN[1] + 10.9, MZ])
go("mom", "L31.3+0.65", [SN[0] + 0.9, SN[1] + 8.5, MZ], yaw=25)
shot("L31.2", mv([SN[0] + 0.5, SN[1] + 7.0, MZ + 1.5], [SN[0] + 0.3, SN[1] + 9.8, MZ + 1.35], 24,
                 [SN[0] + 0.7, SN[1] + 7.0, MZ + 1.5], [SN[0] + 0.7, SN[1] + 9.0, MZ + 1.35], 24), "momwalk")
only("L32", ["mom"])
put("mom", "L32", [SN[0] - 0.2, SN[1] + 9.5, MZ], 0, expr="warm", arms=[0, 0])
shot("L32", momcam(1.55, 2.7, 52, tx=-0.2, ty=9.5, dx=0.3, push=0.1), "momwarm")
only("L33", [])
shot("L33", mv(A(AN, 1.35, 3.5, 1.75), A(AN, 2.5, 3.5, 0.96), 36, A(AN, 1.55, 3.5, 1.55), A(AN, 2.5, 3.5, 0.96), 36), "phone0b")

# ===== 06 the warm turn (L34 to L44)
only("L34", [])
shot("L34", mv(A(G.HALL_N, 0.0, 0.9, 1.5), A(G.HALL_N, 0.0, 7.5, 1.45), 30, A(G.HALL_N, 0.0, 1.8, 1.5), A(G.HALL_N, 0.0, 7.5, 1.45), 30),
     "hallnight")
only("L34.2", ["me"])
me_seat(AN, "L34.2", "warm")
shot("L34.2", fc(AN, CX, CY, 1.5, 2.4, 42, dx=0.15, push=0.1), "warmme")
only("L35", ["mom"])
put("mom", "L35", [SN[0] - 0.2, SN[1] + 9.5, MZ], 0, expr="warm", head=[0, 0], arms=[0, 0])
shot("L35", momcam(1.55, 2.5, 52, tx=-0.2, ty=9.5, dx=-0.25, push=0.08), "momtouched")
beat("mom", "L36", expr="smile", head=[0, 7])
beat("mom", "L36.1", head=[0, -3])
beat("mom", "L36.2", head=[0, 6])
shot("L36", momcam(1.55, 2.6, 52, tx=-0.2, ty=9.5, dx=0.2, push=0.08), "momnod")
only("L37", ["me"])
me_seat(AN, "L37", "sad-smile")
shot("L37", fc(AN, CX, CY, 1.5, 2.8, 42, dx=-0.2, push=0.1, az=12), "sheepme")
only("L38", [])
sit("me", "L38", False)
shot("L38", mv([SN[0] + 0.7, SN[1] + 7.6, MZ + 1.7], [SN[0] + 1.15, SN[1] + 10.4, MZ + 0.8], 28,
               [SN[0] + 0.8, SN[1] + 8.0, MZ + 1.6], [SN[0] + 1.15, SN[1] + 10.4, MZ + 0.8], 28), "tablefortwo")
shot("L39", mv([SN[0] - 0.4, SN[1] + 8.6, MZ + 1.6], [SN[0] - 1.1, SN[1] + 11.1, MZ + 0.8], 34,
               [SN[0] - 0.6, SN[1] + 8.9, MZ + 1.4], [SN[0] - 1.1, SN[1] + 11.1, MZ + 0.8], 34), "herlaundry")
only("L40", ["me"])
me_seat(AD, "L40", "smile")
shot("L40", fc(AD, CX, CY, 1.5, 2.5, 42, dx=0.1, push=0.1, az=-10), "givingup")
me_stand(AN, "L41", -0.45, 4.2, "neutral", yaw=40)
go("me", "L41+0.7", A(AN, STX, STY), yaw=40)
beat("me", "L41+0.75", yaw=0)
shot("L41", mv(A(AN, 0.5, -0.7, 1.55), A(AN, 0.45, 3.6, 1.25), 22, A(AN, 0.55, -0.3, 1.55), A(AN, 0.6, 3.3, 1.3), 22), "nightwalk")
only("L41.2", [])
shot("L41.2", mv(A(AN, -0.5, 0.8, 0.4), A(AN, 2.7, 2.4, 2.6), 28, A(AN, -0.4, 1.0, 0.4), A(AN, 2.7, 2.6, 2.7), 28), "ceiling5")
only("L42", ["me"])
put("me", "L42", A(AN, STX, STY), 0, expr="warm", head=[0, UP + 4])
shot("L42", fc(AN, STX, STY, 1.55, 2.5, 44, dx=0.15, push=0.1), "listening")
only("L43", [])
shot("L43", mv([SN[0] + 1.2, SN[1] + 8.9, MZ + 1.75], [SN[0] + 1.2, SN[1] + 10.42, MZ + 0.82], 36,
               [SN[0] + 1.2, SN[1] + 9.2, MZ + 1.55], [SN[0] + 1.2, SN[1] + 10.42, MZ + 0.82], 36), "mom0")
only("L44", ["me"])
me_seat(AD, "L44", "worried", head=[0, UP])
shot("L44", hookcam(AD, 0.15), "loop")

# ---------------------------------------------------------------------------------------------- finish
cue(0, "freeze", who="mom", on=False)
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
    {"at": "L01+0.4", "kind": "thud", "db": -15},
    {"at": "L13.1", "kind": "thud", "db": -21},
    {"at": "L14", "kind": "thud", "db": -21},
    {"at": "L15.2", "kind": "thud", "db": -21},
    {"at": "L17", "kind": "thud", "db": -21},
    {"at": "L22.1+0.5", "kind": "thud", "db": -21},
    {"at": "L25.1", "kind": "creak", "db": -16, "dur": 1.2},
    {"at": "L42+0.3", "kind": "thud", "db": -22},
]
music = {
    "root": 48, "mode": "minor", "bpm": 104, "seed": 128,
    "sections": [
        {"at": 0, "voices": ["pulse", "piano"], "energy": 0.35, "root": 48, "mode": "minor"},
        {"at": "L13", "voices": ["pulse", "piano", "drone"], "energy": 0.5, "root": 48, "mode": "minor"},
        {"at": "L20", "voices": ["pulse", "piano", "drone"], "energy": 0.68, "root": 48, "mode": "minor"},
        {"at": "L24", "voices": ["pulse", "drone"], "energy": 0.55, "root": 48, "mode": "minor"},
        {"at": "L27", "voices": ["pad", "drone"], "energy": 0.3, "root": 48, "mode": "minor"},
        {"at": "L34", "voices": ["piano", "pad", "pulse"], "energy": 0.5, "root": 48, "mode": "major"},
    ],
}
sound = {
    "floor": "wood", "steps_db": -26,
    "ambience": [{"kind": "room", "from": 0, "to": "end", "lufs": -44}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L27"), remap("L28")], "twist": remap("L28"),
          "emph": [remap(x) for x in ["L01.0", "L03.1", "L12.2", "L17", "L23", "L26.1", "L28", "L32.1", "L44"]],
          "quiet": [[remap("L35"), remap("L37")]],
          "hold": [names["opendoor"], names["stairs"], names["den"], names["phone900"], names["feet"], names["herlaundry"], names["slippers"], names["walk"], names["mewalk"], names["nightwalk"], names["momwalk"]]}
story = {
    "slug": "ep128-zero-feet",
    "title": "Mine Says ZERO Feet Away \U0001f4cd",
    "made_for_kids": False,
    "premise": ("In a town where every phone shows how far across you are from your nearest family, mine says zero in "
                "my first apartment four hundred miles from home, while footsteps overhead keep step with mine."),
    "twist": ("My mom moved in upstairs the week I left and has walked every step I take right over my head, so the "
              "phone can never tell us apart."),
    "world": ("A bright one-room apartment in a brick walk-up: cream walls, a coral couch, a butter-yellow fridge, a "
              "teal kitchen corner, a mint stairwell with a landing, and the lilac flat upstairs."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#9be15d",
    "gap": 0.15,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#e9eaf5", "fog_density": 0.004, "fog_start": 24.0, "sky": "#cfe6ff",
             "sky_strength": 1.0, "exposure": 0.25, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.15, "grain": 0.008},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "framing_ok": [names[n] for n in ["ceiling1", "ceiling2", "ceiling3", "ceiling4", "ceiling5", "opendoor", "slippers",
                                      "phone1", "stairs2", "phone900", "oldphone", "phone0", "still0", "phone0b", "mom0",
                                      "tablefortwo", "laundry", "fridge", "boxes", "oneroom",
                                      "hallmom", "hallnight", "den2"]],
    "frames_ok": [names["feet"]],
    "asr_forgive": ["grandpa's", "i'd", "walk", "too"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
print({k: v for k, v in names.items()})
