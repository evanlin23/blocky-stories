"""Writes ../story.json for ep92 "blackout ben" (script.md, 2026-11-03). Run: python stories/ep92-blackout-ben/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py).
x east, y north, z up. A character facing -y has yaw 0, +x 90, -x -90, +y 180. Shot ids follow the script's.
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


def remap(ref):
    if not isinstance(ref, str):
        return ref
    mm = re.match(r"^(L\d+[a-z]?)\.(\d+)(.*)$", ref)
    if mm and mm.group(1) in CHUNKMAP:
        return f"{mm.group(1)}.{CHUNKMAP[mm.group(1)][int(mm.group(2))]}{mm.group(3)}"
    return ref


def remap_all(items):
    for it in items:
        for key in ("at", "from", "to"):
            if key in it:
                it[key] = remap(it[key])


# ---------------------------------------------------------------------------------------------- cast
def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, collar=None,
           eyes="round", ink="#16100c", sleeves="long", extras=(), brow_w=1.0, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": "none",
         "face": {"eyes": eyes, "brows": True, "ink": ink}}
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
    "me": person("#e8b890", "#8d9099", "#6a7a9a", "#f4f4f2", hair="cap", hair_c="#2a1d15", sleeves="short",
                 pattern="stripes", pattern_c="#e8301f", collar="#e8301f", brow_w=1.3),
    "ben": person("#f0c8a0", "#26355e", "#3d5a8a", "#f4f4f2", hair="swoop", hair_c="#c9a35a", extras=["hooddown"],
                  extra_c="#26355e"),
    "mom": person("#e0a878", "#b79ad8", "#4a4a66", "#2a2a30", hair="long", hair_c="#b9b6c4", pattern="knit",
                  pattern_c="#d9c4ef", eyes="lashes"),
    "varga": person("#e8b890", "#ff8a3a", "#6a5a3a", "#3a2a1a", hair="none", sleeves="short"),
    "varga2": person("#e8b890", "#ff8a3a", "#6a5a3a", "#3a2a1a", hair="cap", hair_c="#9a9aa6", sleeves="short"),
    "dale": person("#e8c4a0", "#ffb03a", "#4a4036", "#3a2a1a", hair="none", eyes="tired", ink="#55555c",
                   extras=["glasses"]),
    "f1": person("#d3a07a", "#ff8a6a", "#2f3548", "#f2f2f0", hair="long", hair_c="#3a1f14", eyes="lashes"),
    "f2": person("#e8b890", "#3a8a6a", "#4a4036", "#3a2a1a", hair="buzz", hair_c="#5a3a22"),
    "f3": person("#b98456", "#6a8cff", "#3a3a44", "#f2f2f0", hair="bun", hair_c="#150f0c", eyes="lashes"),
    "n1": person("#d9a577", "#ffd23a", "#3a3a44", "#e8e8e8", hair="spiky", hair_c="#2a1d15", brow_w=1.0),
    "n1b": person("#d9a577", "#2f6bff", "#3a3a44", "#e8e8e8", hair="spiky", hair_c="#2a1d15", brow_w=2.0),
}

EXP = {"annoyed": "angry", "sulky": "worried", "stunned": "wide", "uneasy": "worried", "suspicious": "smirk",
       "scared": "scared", "thinking": "neutral", "relief": "soft", "soft": "smile", "smug": "smirk", "blank": "blank",
       "sad": "worried", "unsure": "worried", "sheepish": "polite", "laugh": "laugh", "amused": "smile",
       "content": "soft", "confused": "worried", "relieved": "soft", "grumpy": "angry", "squeeze": "squeeze",
       "grin": "delighted", "smile": "smile"}

acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0]}] for n in cast}
last = {n: [0, 0] for n in cast}
sitting = {n: False for n in cast}
cues = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def ex(e):
    return EXP.get(e, e)


def put(who, at, pos, yaw=None, sit=None, expr=None, **kw):
    """Appear (or jump) to pos on `at`. sit: the hip height to sit at (None: stand)."""
    p = list(pos)
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False}
    if yaw is not None:
        k["yaw"] = yaw
    if expr:
        k["expr"] = ex(expr)
    k.update(kw)
    acting[who].append(k)
    last[who] = p
    if sit is not None:
        cue(at, "sit", who=who, on=True, z=sit)
        sitting[who] = True
    elif sitting[who]:
        cue(at, "sit", who=who, on=False)
        sitting[who] = False


def go(who, at, pos, **kw):
    p = list(pos)
    k = {"at": at, "pos": p}
    if "expr" in kw:
        kw["expr"] = ex(kw["expr"])
    k.update(kw)
    acting[who].append(k)
    last[who] = p


def pose(who, at, **kw):
    if "expr" in kw:
        kw["expr"] = ex(kw["expr"])
    acting[who].append({"at": at, "pos": list(last[who]), **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True})
    if sitting[who]:
        cue(at, "sit", who=who, on=False)
        sitting[who] = False


def look(at, id_, dur=0.0):
    cue(at, "look", id=id_, dur=dur)


def obj(id_, at, pos=None, yaw=0.0, dur=0.0, hide_=False, rot=None):
    c = {"at": at, "name": "obj", "id": id_}
    if hide_:
        c["hide"] = True
    else:
        c["pos"] = list(pos)
        c["yaw"] = yaw
        c["rot"] = list(rot or [0, 0, 0])
    if dur:
        c["dur"] = dur
    cues.append(c)


def fl(who, at, v=1.0, dur=0.0):
    cue(at, "fl", who=who, v=v, dur=dur)


def ver(at, v):
    cue(at, "ver", v=v)


def watch(at, side):
    cue(at, "watch", side=side)


def gain(at, v):
    cue(at, "gain", v=v, dur=0.0)


def check(at, state, big=False):
    cue(at, "check", state=state, big=big)


def hs(at, i, win=None, porch=None, dur=0.4):
    c = {"at": at, "name": "hs", "id": i, "dur": dur}
    if win is not None:
        c["win"] = win
    if porch is not None:
        c["porch"] = porch
    cues.append(c)


def uplight(at, v, pos=None, tgt=None, dur=0.0):
    c = {"at": at, "name": "uplight", "v": v, "dur": dur}
    if pos:
        c["pos"] = list(pos)
        c["tgt"] = list(tgt)
    cues.append(c)


# ---------------------------------------------------------------------------------------------- cameras
SH = []


def shot(id_, at, cam_, step=2, hand=None, follow=None):
    SH.append((id_, at, cam_, step, hand, follow))


WIDEN = 0.82


def C(p, t, lens, p2=None, t2=None, lens2=None, roll=0.0):
    lens = lens * WIDEN
    lens2 = lens2 * WIDEN if lens2 else None
    if p2 is None:
        return [[0, list(p), list(t), lens, roll]]
    return [[0, list(p), list(t), lens, roll], [1, list(p2), list(t2 if t2 is not None else t), lens2 or lens, roll]]


SY, SZ = G.SEAT_Y, G.SEAT_Z
S_L, S_M, S_R = G.SEAT["L"], G.SEAT["M"], G.SEAT["R"]
HX = G.HOUSE_X
N_, V_, D_ = HX[1], HX[2], HX[3]          # neighbour, Varga, Dale houses
PORCH_FRONT = -18.9
CAR = G.CAR


def porch_cam(hx, z=1.15, d=3.3, f=26, tz=0.9, dx=0.0):
    return C([hx + dx, -18.9 + d, z], [hx + dx * 0.4, -19.2, tz], f)


# ========================================================================================== 01 the hook (L01, L02)
look(0, "hook", 0)
ver(0, "B")
watch(0, "R")
check(0, "A")
obj("tblfl", 0, [0.3, 0.1, 0.46])
uplight(0, 1.0, [0.3, 0.05, 0.62], [0.3, 0.95, 1.5])
obj("plate", 0, [0.3, 0.3, 1.15])
put("ben", 0, [0.3, 0.95], 0, expr="smile", arms=[85, 85], head=[0, 4])
shot("S01a", 0, C([0.3, -1.5, 1.52], [0.3, 0.9, 1.42], 36))
shot("S01b", "L01.2", C([0.3, -0.5, 1.55], [0.3, 0.9, 1.5], 36, [0.3, -0.35, 1.55], [0.3, 0.9, 1.5], 36))
# L02: top-down on the plate, the check inset's Ben icon blinks
look("L02", "hook", 0)
check("L02", "A0")
check("L02+0.3", "A")
check("L02+0.6", "A0")
check("L02+0.9", "A")
gain("L02", 0.7)
shot("S02", "L02", C([0.3, 0.55, 2.2], [0.3, 0.28, 1.15], 24, [0.3, 0.45, 2.0], [0.3, 0.28, 1.15], 24))
gain("L03", 1.0)
uplight("L03", 0.0, dur=0.4)

# ========================================================================================== 02 the montage (L03 to L10)
# L03: the street at dusk, then every window goes dark left to right
look("L03", "dusk", 0)
obj("tblfl", "L03", hide_=True)
obj("plate", "L03", hide_=True)
hide("ben", "L03")
for i in range(len(HX)):
    hs(0, i, win=1.0, porch=1.0, dur=0)
for i in range(len(HX)):
    hs(f"L03.1+{0.12 * i:.2f}", i, win=0.0, porch=0.0, dur=0.4)
look("L03.1", "street", 0.5)
shot("S03", "L03", C([0.0, -9.2, 2.4], [0.0, -24.0, 2.6], 10, [0.0, -10.2, 2.5], [0.0, -24.0, 2.6], 10))
# L04: a neighbour alone on a dark porch step, then the porch light returns and the shirt has changed
put("n1", "L04", [N_ - 0.2, -18.55], 180, sit=0.38, expr="neutral", head=[0, 6])
pose("n1", "L04+0.4", expr="shut")
shot("S04a", "L04", C([N_ + 0.2, -15.6, 1.1], [N_ - 0.1, -18.7, 0.95], 27))
hide("n1", "L04.2")
put("n1b", "L04.2", [N_ - 0.2, -18.55], 180, sit=0.38, expr="confused")
hs("L04.2", 1, porch=1.0, dur=0.4)
shot("S04b", "L04.2", C([N_ + 0.5, -15.8, 1.15], [N_ - 0.1, -18.7, 0.95], 27, [N_ + 0.3, -16.2, 1.15], [N_ - 0.1, -18.7, 0.95], 27))
# L05: two quick inserts, same face, different eyebrows
hide("n1b", "L05")
put("n1", "L05", [N_ - 0.2, -18.55], 180, sit=0.38, expr="neutral")
shot("S05a", "L05", C([N_ - 0.2, -17.3, 1.3], [N_ - 0.2, -18.55, 1.25], 34))
hide("n1", "L05.1")
put("n1b", "L05.1", [N_ - 0.2, -18.55], 180, sit=0.38, expr="confused")
shot("S05b", "L05.1", C([N_ - 0.2, -17.3, 1.3], [N_ - 0.2, -18.55, 1.25], 34))
hs("L05.1", 1, porch=0.0, dur=0.4)
# L06: through a window, a family inside a ring of flashlight beams; then two sisters
WX, WY = G.WR
hide("n1b", "L06")
look("L06", "street", 0)
put("f1", "L06", [WX - 1.1, WY + 4.2], 0, sit=SZ, expr="soft")
put("f2", "L06", [WX + 1.1, WY + 4.2], 0, sit=SZ, expr="smile")
put("f3", "L06", [WX + 0.0, WY + 4.2], 0, sit=SZ, expr="soft")
obj("ring", "L06", [WX, WY + 2.6, 0.0])
cue("L06", "ringlight", v=1.0, dur=0.0)
shot("S06a", "L06", C([WX - 0.3, WY - 1.4, 1.4], [WX, WY + 4.0, 1.1], 28, [WX + 0.2, WY - 1.1, 1.4], [WX, WY + 4.0, 1.1], 28))
hide("f1", "L06.1")
hide("f2", "L06.1")
hide("f3", "L06.1")
sx2 = WX + 6.0
put("f1", "L06.1", [sx2 - 0.9, WY + 2.0], 40, expr="laugh", arms=[0, 165])
put("f3", "L06.1", [sx2 + 0.9, WY + 2.0], -40, expr="laugh", arms=[0, 165])
fl("f1", "L06.1", 1.0)
fl("f3", "L06.1", 1.0)
shot("S06b", "L06.1", C([sx2 - 0.2, WY - 2.0, 1.5], [sx2, WY + 2.0, 1.45], 26, [sx2 + 0.2, WY - 1.8, 1.5], [sx2, WY + 2.0, 1.45], 26))
# L07: Mr. Varga alone in the dark, then lights up with a ponytail
hide("f1", "L07")
hide("f3", "L07")
fl("f1", "L07", -1.0)
fl("f3", "L07", -1.0)
cue("L07", "ringlight", v=0.0, dur=0.0)
obj("ring", "L07", hide_=True)
put("varga", "L07", [V_, -19.6], 180, sit=0.97, expr="neutral")
shot("S07a", "L07", C([V_ + 0.2, -15.6, 1.4], [V_, -19.4, 1.3], 25))
hide("varga", "L07.2")
put("varga2", "L07.2", [V_, -19.6], 90, sit=0.97, expr="confused", arms=[0, 150])
hs("L07.2", 2, porch=1.0, dur=0.4)
shot("S07b", "L07.2", C([V_ + 0.3, -15.8, 1.5], [V_, -19.4, 1.4], 24, [V_ + 0.1, -16.3, 1.5], [V_, -19.4, 1.4], 24))
# L08: Mr. Dale in a lawn chair, scowling in the dark, then lights up and he's beaming
hide("varga2", "L08")
hs("L08", 2, porch=0.0, dur=0.4)
put("dale", "L08", [D_, -17.55], 180, sit=0.5, expr="grumpy")
shot("S08", "L08", C([D_ + 0.3, -14.3, 1.2], [D_, -17.5, 1.1], 28))
hs("L08.1", 3, porch=1.0, dur=0.4)
pose("dale", "L08.1+0.3", expr="laugh")
# L09: the Dale family hugging him on the porch
hide("dale", "L09")
put("dale", "L09", [D_, -19.3], 180, expr="laugh", arms=[0, 150])
put("f1", "L09", [D_ - 1.0, -19.35], 160, expr="laugh", arms=[60, 60])
put("f2", "L09", [D_ + 1.0, -19.35], -160, expr="laugh", arms=[60, 60])
put("f3", "L09", [D_ + 0.0, -18.7], 180, expr="laugh", arms=[60, 60])
shot("S09", "L09", C([D_ + 0.2, -15.0, 1.7], [D_, -19.3, 1.4], 24, [D_ + 0.1, -15.7, 1.7], [D_, -19.3, 1.4], 24))
# L10: Varga alone in the dark again, then bald again and relieved
for who in ("dale", "f1", "f2", "f3"):
    hide(who, "L10")
hs("L10", 3, porch=0.0, dur=0.4)
put("varga2", "L10", [V_, -19.6], 90, sit=0.97, expr="squeeze")
shot("S10a", "L10", C([V_ + 0.3, -15.8, 1.5], [V_, -19.4, 1.4], 24))
hide("varga2", "L10.3")
put("varga", "L10.3", [V_, -19.6], 180, sit=0.97, expr="relieved", arms=[0, 150])
hs("L10.3", 2, porch=1.0, dur=0.4)
shot("S10b", "L10.3", C([V_ - 0.3, -15.6, 1.45], [V_, -19.4, 1.4], 24, [V_ - 0.1, -16.2, 1.45], [V_, -19.4, 1.4], 24))

# ========================================================================================== 03 my version (L11 to L16)
hide("varga", "L11")
look("L11", "day", 0)
ver("L11", "A")
watch("L11", "L")
check("L11", "A")
put("me", "L11", [S_L, SY], 0, sit=SZ, expr="annoyed")
put("ben", "L11", [S_R, SY], 0, sit=SZ, expr="annoyed")
obj("remote", "L11", [0.3, 1.95, 0.7])
shot("S11a", "L11", C([0.3, -1.6, 1.4], [0.3, 2.1, 1.1], 15, [0.3, -1.9, 1.4], [0.3, 2.1, 1.1], 15))
pose("ben", "L11.2", expr="smug", arms=[0, 70])
obj("cereal", "L11.2", [S_R - 0.2, 1.35, 1.0], 0)
obj("cereal", "L11.2+0.25", [S_R - 0.2, 1.35, 1.1], 0, dur=0.12)
obj("cereal", "L11.2+0.45", [S_R - 0.2, 1.35, 0.95], 0, dur=0.12)
shot("S11b", "L11.2", C([S_R + 0.2, -0.2, 1.5], [S_R - 0.1, 1.9, 1.35], 30))
# L11b: he tips my last cereal into his own bowl; I slide the remote under a cushion while he isn't looking
obj("cereal", "L11b", [S_R - 0.15, 1.5, 1.12], 0)
obj("cereal", "L11b+0.35", [S_R - 0.15, 1.5, 1.1], 150, dur=0.5, rot=[0, 150, 0])
obj("bowl", "L11b", [S_R - 0.15, 1.5, 0.74], 0)
pose("ben", "L11b", expr="smug", arms=[0, 70])
shot("S11c", "L11b", C([S_R + 0.9, 0.2, 1.25], [S_R - 0.15, 1.6, 0.95], 30, [S_R + 0.7, 0.5, 1.2], [S_R - 0.15, 1.6, 0.95], 30))
obj("cereal", "L11b.1", hide_=True)
obj("bowl", "L11b.1", hide_=True)
pose("ben", "L11b.1", expr="smug", arms=[0, 0], head=[-40, 0])
pose("me", "L11b.1", expr="smug", arms=[0, 60], head=[20, 0])
obj("remote", "L11b.1+0.1", [0.3, 1.95, 0.7])
obj("remote", "L11b.1+0.35", [-0.35, 2.0, 0.62], 0, dur=0.5)
shot("S11d", "L11b.1", C([0.0, -0.4, 1.3], [-0.1, 1.95, 0.95], 28, [-0.1, -0.1, 1.25], [-0.1, 1.95, 0.95], 28))
obj("remote", "L12", hide_=True)
pose("ben", "L12", expr="annoyed", arms=[0, 0], side=[50, 50])
pose("me", "L12", expr="annoyed", side=[50, 50], head=[0, -6])
shot("S12", "L12", C([0.3, -0.2, 1.3], [0.3, 2.1, 1.1], 17, [0.3, -0.5, 1.3], [0.3, 2.1, 1.1], 17))
# L13: the lamp ramps off
look("L13", "lamp", 0)
look("L13.1", "night", 0.45)
hide("me", "L13")
hide("ben", "L13")
obj("remote", "L13", hide_=True)
shot("S13", "L13", C([1.8, 3.0, 1.5], [-2.1, -3.5, 1.4], 20, [1.5, 2.7, 1.5], [-2.1, -3.5, 1.4], 20))
# L14: Mom, Ben and Pickle on the mustard couch, flashlights up
put("mom", "L14", [S_L, SY], 0, sit=SZ, expr="amused", arms=[0, 165])
put("ben", "L14", [S_R, SY], 0, sit=SZ, expr="smug", arms=[165, 0])
fl("mom", "L14", 1.0)
fl("ben", "L14", 1.0)
obj("dog", "L14", [S_M, SY + 0.05, SZ - 0.1], 0)
shot("S14a", "L14", C([0.3, -1.4, 1.3], [0.3, 2.1, 1.0], 21, [0.3, -1.0, 1.3], [0.3, 2.1, 1.0], 21))
shot("S14b", "L14.1+0.5", C([S_M, -0.5, 1.25], [S_M, 2.1, 0.8], 34, [S_M, -0.2, 1.2], [S_M, 2.1, 0.8], 34))
# L14b: his flashlight lights his BLACK watch on his LEFT wrist (S14c), then a pull to his smug face (S14d)
pose("ben", "L14b", expr="smug", arms=[165, 55])
shot("S14c", "L14b", C([3.9, 1.1, 1.4], [2.18, 1.73, 1.03], 34, [3.6, 1.2, 1.32], [2.18, 1.73, 1.03], 34))
pose("ben", "L14b.2", expr="smug", arms=[105, 20], head=[0, 0])
shot("S14d", "L14b.2", C([1.2, -0.4, 1.4], [S_R, 2.1, 1.3], 28, [1.3, -0.1, 1.4], [S_R, 2.1, 1.3], 28))
# L15: me alone on my bed in the dark, door shut
hide("mom", "L15")
hide("ben", "L15")
fl("mom", "L15", -1.0)
fl("ben", "L15", -1.0)
obj("dog", "L15", hide_=True)
put("me", "L15", [16.05, 1.15], -90, sit=0.66, expr="sulky")
shot("S15", "L15", C([13.9, -1.6, 1.4], [15.9, 1.1, 0.95], 26, [14.2, -1.4, 1.4], [15.9, 1.1, 0.95], 26))
# L16: a strip of flashlight under my door, two soft knocks, then I roll over
hide("me", "L16")
cue("L16", "strip", v=1.0, dur=0.4)
shot("S16a", "L16", C([15.2, 0.4, 0.8], [12.0, 0.0, 0.6], 27, [14.6, 0.3, 0.7], [12.0, 0.0, 0.55], 27))
put("me", "L16.1", [14.9, 1.15], 90, sit=0.66, expr="sulky")
cue("L16.1+0.8", "strip", v=0.0, dur=0.4)
shot("S16b", "L16.1", C([13.1, 0.9, 1.3], [15.5, 1.15, 1.0], 28, [13.5, 0.9, 1.3], [15.5, 1.15, 1.0], 28))

# ========================================================================================== 04 the strange days (L17 to L30)
# L17: my lamp ramps on, then the new living room and the plate
look("L17", "night", 0)
look("L17+0.2", "lamp", 0.5)
cue("L17.1", "strip", v=0.0, dur=0.0)
put("me", "L17", [16.05, 1.15], -90, sit=0.66, expr="sulky")
shot("S17a", "L17", C([13.9, -1.6, 1.4], [15.9, 1.1, 0.95], 26, [14.0, -1.3, 1.5], [16.3, 0.4, 0.8], 26))
hide("me", "L17.2")
look("L17.2", "lamp", 0)
ver("L17.2", "B")
watch("L17.2", "R")
put("ben", "L17.2", [0.1, 0.95], 0, expr="soft", arms=[80, 80])
obj("plate", "L17.2", [0.1, 0.3, 1.12])
shot("S17b", "L17.2", C([0.1, -2.4, 1.35], [0.1, 0.6, 1.35], 24, [0.1, -2.1, 1.35], [0.1, 0.6, 1.35], 24))
# L18: me taking the plate
put("me", "L18", [0.1, -0.5], 0, expr="stunned", arms=[80, 80])
obj("plate", "L18", [0.1, -1.1, 1.12])
pose("ben", "L18", expr="soft", arms=[0, 0])
shot("S18", "L18", C([0.1, -3.0, 1.45], [0.1, 0.0, 1.35], 26, [0.1, -2.7, 1.45], [0.1, 0.0, 1.35], 26))
# L19: the crusts
hide("me", "L19")
obj("plate", "L19", [0.1, 0.3, 1.12])
shot("S19", "L19", C([0.1, -0.75, 1.5], [0.1, 0.3, 1.12], 40, [0.1, -0.65, 1.35], [0.1, 0.3, 1.12], 40))
# L20: his watch, on the right
check("L20", "B")
pose("ben", "L20", arms=[0, 0], side=[14, 14], expr="soft")
obj("plate", "L20", hide_=True)
shot("S20", "L20", C([-0.45, -0.75, 1.0], [-0.45, 0.95, 0.92], 34, [-0.45, -0.55, 1.0], [-0.45, 0.95, 0.92], 34))
# L21: callbacks to my Ben, watch on his left, a rewind
look("L21", "day", 0)
ver("L21", "A")
watch("L21", "L")
hide("ben", "L21")
put("ben", "L21", [S_R, SY], 0, sit=SZ, expr="annoyed", arms=[0, 55])
shot("S21a", "L21", C([0.9, -0.6, 1.3], [S_R, 2.1, 1.1], 24))
pose("ben", "L21.1", expr="smug", arms=[0, 60])
shot("S21b", "L21.1", C([3.7, 0.7, 1.3], [1.96, 1.8, 1.0], 34, [3.4, 0.85, 1.25], [1.96, 1.8, 1.0], 34))
# L22: back to now, his right wrist
look("L22", "lamp", 0)
ver("L22", "B")
watch("L22", "R")
obj("remote", "L22", hide_=True)
hide("ben", "L22")
put("ben", "L22", [0.1, 0.95], 0, expr="soft", arms=[0, 0], side=[14, 14])
shot("S22", "L22", C([-1.5, -0.4, 0.95], [-0.45, 0.95, 0.92], 34, [-1.2, -0.2, 0.95], [-0.45, 0.95, 0.92], 34))
# L23: Mom waves me off, the canoe photo behind her
hide("ben", "L23")
put("mom", "L23", [S_L + 0.6, SY], 0, sit=SZ, expr="amused", arms=[0, 100])
shot("S23", "L23", C([-0.4, -0.9, 1.45], [-0.2, 2.3, 1.45], 22, [-0.4, -0.6, 1.45], [-0.1, 2.3, 1.45], 22))
# L24: Ben crouched in the hall doorway, calling
hide("mom", "L24")
put("ben", "L24", [5.6, 0.0], -90, sit=0.22, expr="soft", arms=[0, 80])
shot("S24", "L24", C([2.8, -0.6, 1.0], [5.5, 0.0, 0.7], 30, [3.0, -0.4, 0.95], [5.5, 0.0, 0.7], 30))
# L25: me, uneasy, half off the couch
put("me", "L25", [S_R - 0.6, SY], 0, sit=SZ, expr="uneasy", head=[18, 0])
hide("ben", "L25")
shot("S25", "L25", C([0.8, -1.0, 1.35], [S_R - 0.6, 2.1, 1.25], 27, [0.9, -0.8, 1.35], [S_R - 0.6, 2.1, 1.25], 27))
# L26: Pickle bounding to Ben
hide("me", "L26")
put("ben", "L26", [5.6, 0.0], -90, sit=0.22, expr="soft", arms=[0, 80])
obj("dog", "L26", [0.0, 0.8, 0.0], 90)
obj("dog", "L26+0.05", [4.8, 0.1, 0.0], 90, dur=0.9)
shot("S26", "L26", C([1.0, -3.0, 1.1], [2.6, 0.3, 0.4], 22, [2.6, -3.0, 1.1], [3.6, 0.3, 0.4], 22))
# L27: the dinner table, Ben leaning in, me suspicious
hide("ben", "L27")
obj("dog", "L27", hide_=True)
look("L27", "day", 0)
put("ben", "L27", [-3.8, 1.45], 0, sit=0.5, expr="soft", head=[-30, 0], lean=0.1)
put("me", "L27", [-2.6, 1.45], 0, sit=0.5, expr="suspicious", head=[10, 0])
shot("S27", "L27", C([-3.2, -1.2, 1.4], [-3.2, 1.2, 1.15], 22, [-3.2, -0.9, 1.4], [-3.2, 1.2, 1.15], 22))
# L27b: the last slice of pizza: the box first, then Ben slides the slice onto my plate
obj("pizza", "L27b", [-3.2, 0.3, 0.8], 0)
obj("slice", "L27b", [-3.2, 0.3, 0.84], 0)
shot("S27b", "L27b", C([-3.0, -0.5, 1.35], [-3.2, 0.35, 0.8], 30, [-3.1, -0.3, 1.25], [-3.2, 0.35, 0.8], 30))
pose("ben", "L27b.2", expr="soft", arms=[0, 70], head=[-20, 0])
pose("me", "L27b.2", expr="suspicious", head=[10, 0])
obj("slice", "L27b.2", [-3.2, 0.3, 0.84], 0)
obj("slice", "L27b.2+0.1", [-2.6, 0.62, 0.82], 20, dur=0.55)
shot("S27c", "L27b.2", C([-3.2, -1.2, 1.5], [-3.2, 0.9, 0.95], 24, [-3.2, -0.9, 1.45], [-3.2, 0.9, 0.95], 24))
# L28: Ben laughing, me stunned
obj("pizza", "L28", hide_=True)
obj("slice", "L28", hide_=True)
pose("ben", "L28", expr="laugh", head=[-20, 0])
pose("me", "L28", expr="stunned", head=[10, 0])
shot("S28", "L28", C([-3.4, -0.3, 1.3], [-3.2, 1.4, 1.2], 28, [-3.3, 0.0, 1.3], [-3.2, 1.4, 1.2], 28))
# L29: Ben holds the car door open for me
hide("ben", "L29")
hide("me", "L29")
cue("L29", "cardoor", open=1.0, dur=0.5)
put("ben", "L29", [CAR[0] + 0.1, CAR[1] - 1.9], 180, expr="soft", arms=[0, 70])
shot("S29", "L29", C([CAR[0] + 1.8, CAR[1] - 5.2, 1.5], [CAR[0] + 0.1, CAR[1] - 1.7, 1.2], 24, [CAR[0] + 1.4, CAR[1] - 4.8, 1.5], [CAR[0] + 0.1, CAR[1] - 1.7, 1.2], 24))
# the second half of L29: Ben at the wheel, me beside him (so it is Ben who drives)
hide("ben", "L29.1")
put("ben", "L29.1", [CAR[0] + 0.45, CAR[1] + 0.42], 90, sit=0.82, expr="soft", arms=[70, 70])
put("me", "L29.1", [CAR[0] + 0.45, CAR[1] - 0.42], 90, sit=0.82, expr="stunned")
shot("S29b", "L29.1", C([CAR[0] + 3.4, CAR[1] + 1.2, 1.7], [CAR[0] + 0.45, CAR[1], 1.45], 26, [CAR[0] + 3.0, CAR[1] + 0.9, 1.7], [CAR[0] + 0.45, CAR[1], 1.45], 26))
hide("me", "L30")
# L30: Mom in the back seat, humming
hide("ben", "L30")
put("mom", "L30", [CAR[0] - 0.95, CAR[1]], 90, sit=0.82, expr="content")
shot("S30", "L30", C([CAR[0] + 3.0, CAR[1] - 1.4, 1.65], [CAR[0] - 0.95, CAR[1], 1.45], 24, [CAR[0] + 2.7, CAR[1] - 1.2, 1.65], [CAR[0] - 0.95, CAR[1], 1.45], 24))

# L30b: Thursday night, a strip of flashlight light sat under my door for an hour (the clock rolls on)
hide("mom", "L30b")
look("L30b", "night", 0)
cue("L30b", "sheet", on=False)
cue("L30b", "clock", txt="11:04")
cue("L30b", "doorm", open=0.0, dur=0.0)
cue("L30b", "strip", v=1.0, dur=0.4)
put("me", "L30b", [16.05, 1.15], -90, sit=0.66, expr="uneasy")
shot("S30b", "L30b", C([13.4, -1.7, 1.15], [15.7, 0.9, 0.9], 26, [13.8, -1.4, 1.15], [15.7, 0.9, 0.9], 26))
shot("S30b2", "L30b.1", C([14.3, -0.7, 0.5], [12.2, 0.0, 0.25], 26, [13.9, -0.5, 0.45], [12.2, 0.0, 0.25], 26))
cue("L30b.3", "clock", txt="11:04")
cue("L30b.3+0.45", "clock", txt="12:04")
shot("S30c", "L30b.3", C([14.6, -0.9, 0.95], [16.35, -0.1, 0.62], 34, [15.0, -0.7, 0.9], [16.35, -0.1, 0.62], 34))
# L30c: I open the door a crack, scared; the hall is empty
hide("me", "L30c")
put("me", "L30c", [13.0, -0.3], -90, expr="scared", arms=[0, 60])
cue("L30c", "doorm", open=0.5, dur=0.4)
shot("S30d", "L30c", C([10.6, -0.3, 1.5], [13.0, -0.2, 1.4], 26, [10.9, -0.3, 1.5], [13.0, -0.2, 1.4], 26))
hide("me", "L30c.1")
cue("L30c.1", "strip", v=0.0, dur=0.4)
cue("L30c.1", "doorm", open=1.0, dur=0.4)
shot("S30e", "L30c.1", C([12.9, -0.3, 1.45], [5.0, 0.0, 1.3], 24, [12.4, -0.2, 1.45], [5.0, 0.0, 1.3], 24))

# ========================================================================================== 05 Friday night (L31 to L38)
# L31: my room at night, the clock reads 2:00
hide("mom", "L31")
cue("L31", "clock", txt="2:00")
cue("L31", "sheet", on=True)
look("L31", "night", 0)
cue("L31", "doorm", open=0.0, dur=0.0)
put("me", "L31", [16.05, 1.15], -90, sit=0.66, expr="asleep")
pose("me", "L31+0.9", expr="wide")
shot("S31", "L31", C([13.6, -1.3, 1.1], [16.3, 0.5, 0.8], 30, [14.0, -1.1, 1.1], [16.3, 0.5, 0.8], 30))
# L32: Ben in my doorway, lit by his own flashlight
cue("L32-0.7", "doorm", open=1.0, dur=0.45)
put("ben", "L32", [12.0, 0.0], 90, expr="blank", arms=[100, 0], side=[-25, 0])
uplight("L32", 1.0, [12.55, -0.3, 1.12], [12.0, 0.0, 1.55])
fl("ben", "L32", 1.0)
shot("S32", "L32", C([15.0, 0.3, 1.35], [12.0, 0.0, 1.4], 28, [14.6, 0.3, 1.4], [12.0, 0.0, 1.4], 28))
# L33: my point of view into the beam (cover frame)
shot("S33", "L33", C([14.4, 0.15, 1.45], [12.5, -0.2, 1.45], 30, [13.9, 0.05, 1.45], [12.5, -0.2, 1.45], 30))
# L34: Ben, close, perfectly still
shot("S34", "L34", C([13.7, 0.3, 1.55], [12.2, -0.1, 1.5], 30, [13.4, 0.2, 1.55], [12.2, -0.1, 1.5], 30))
# L35: me scared with the sheet to my chin, then Ben close again
pose("ben", "L35", yaw=90)
cue("L35", "bface", v=1.0, dur=0.4)
shot("S35a", "L35", C([13.5, 0.2, 1.45], [16.0, 1.15, 1.15], 26, [13.9, 0.3, 1.45], [16.0, 1.15, 1.15], 26))
pose("me", "L35", expr="scared", arms=[0, 0])
pose("ben", "L35.2", yaw=90)
shot("S35b", "L35.2", C([13.2, -0.3, 1.5], [12.0, 0.0, 1.5], 34))
# the drop: the beam steady on my face, dust in the light
cue("P01", "dust", on=True)
pose("ben", "P01", yaw=90)
shot("SP01", "P01", C([13.5, 0.7, 1.3], [12.5, 0.1, 1.35], 38, [13.1, 0.6, 1.3], [12.5, 0.1, 1.35], 38))
cue("L36", "dust", on=False)
# L36: Ben close, blank, the beam not moving; L37 me close, scared
pose("ben", "L36", yaw=90)
shot("S36", "L36", C([13.6, -0.2, 1.5], [12.0, 0.0, 1.5], 30, [13.3, -0.1, 1.5], [12.0, 0.0, 1.5], 30))
shot("S37", "L37", C([14.4, 1.15, 1.55], [16.0, 1.15, 1.5], 30, [14.8, 1.15, 1.55], [16.0, 1.15, 1.5], 30))
# L38: the flashlight clicks off, then the empty doorway and his footsteps
fl("ben", "L38", 0.0, dur=0.4)
uplight("L38", 0.0, dur=0.4)
cue("L38", "bface", v=0.0, dur=0.4)
shot("S38a", "L38", C([13.3, -0.2, 1.5], [12.0, 0.0, 1.5], 36))
go("ben", "L38.1", [12.0, 0.0])
go("ben", "L38>", [6.0, 0.0], yaw=-90)
hide("ben", "L38>")
shot("S38b", "L38.1", C([13.8, 0.2, 1.4], [8.0, 0.0, 1.3], 24, [13.0, 0.2, 1.4], [8.0, 0.0, 1.3], 24))

# L38b: I lie awake till the sun comes up (the window goes from cobalt to peach)
hide("ben", "L38b")
fl("ben", "L38b", -1.0)
pose("me", "L38b", expr="uneasy", arms=[0, 0])
shot("S38c", "L38b", C([13.7, -1.6, 1.2], [15.9, 1.0, 0.95], 26, [14.0, -1.4, 1.2], [15.9, 1.0, 0.95], 26))
look("L38b.1", "dawn", 0.9)
pose("me", "L38b.1", expr="wide")
shot("S38d", "L38b.1", C([14.4, -1.2, 1.15], [15.9, 1.0, 0.95], 26, [14.7, -1.0, 1.15], [15.9, 1.0, 0.95], 26))

# ========================================================================================== 06 the reveal (L39 to L47)
# L39: me in the dark living room with my own flashlight; the beam lands on the mantel photo
look("L39", "night", 0)
fl("ben", "L39", -1.0)
cue("L39", "sheet", on=False)
cue("L39", "doorm", open=0.0, dur=0.0)
hide("me", "L39")
put("me", "L39", [0.6, -0.3], 160, expr="uneasy", arms=[0, 98])
fl("me", "L39", 1.0)
shot("S39a", "L39", C([-1.6, -2.0, 1.45], [0.5, 0.0, 1.3], 24, [-1.3, -1.9, 1.45], [0.5, 0.0, 1.3], 24))
shot("S39b", "L39.2", C([0.2, 0.9, 1.35], [-0.3, 3.2, 1.45], 28, [-0.1, 1.5, 1.4], [-0.3, 3.2, 1.45], 28))
# L40: the photo
hide("me", "L40")
fl("me", "L40", -1.0)
uplight("L39.2", 0.8, [-0.4, 1.9, 1.4], [-0.4, 3.2, 1.55])
shot("S40", "L40", C([-0.4, 2.2, 1.55], [-0.4, 3.2, 1.55], 22, [-0.4, 2.45, 1.55], [-0.4, 3.2, 1.55], 22))
# L40b: push in on the red canoe, then a callback insert of S20: this Ben's canoe-red watch on his right wrist
shot("S40b", "L40b", C([-0.4, 2.7, 1.55], [-0.4, 3.2, 1.55], 26, [-0.4, 2.95, 1.55], [-0.4, 3.2, 1.57], 26))
look("L40b.1", "lamp", 0)
put("ben", "L40b.1", [0.1, 0.95], 0, expr="soft", arms=[0, 0], side=[14, 14])
shot("S40c", "L40b.1", C([-0.45, -0.75, 1.0], [-0.45, 0.95, 0.92], 34, [-0.45, -0.55, 1.0], [-0.45, 0.95, 0.92], 34))
look("L41", "night", 0)
uplight("L41", 0.8, [-0.4, 1.9, 1.4], [-0.4, 3.2, 1.55])
hide("ben", "L41")
# L41: me stunned, the beam trembling
put("me", "L41", [0.3, -0.2], 0, expr="stunned", arms=[0, 0])
pose("me", "L41+0.3", arms=[0, 6])
pose("me", "L41+0.6", arms=[0, 0])
shot("S41", "L41", C([0.3, -1.8, 1.55], [0.3, 0.0, 1.5], 32, [0.3, -1.5, 1.55], [0.3, 0.0, 1.5], 32))
# L42: a callback to S15, and the check inset's question mark slides onto me
uplight("L42", 0.0, dur=0.4)
hide("me", "L42")
put("me", "L42", [16.05, 1.15], -90, sit=0.66, expr="sulky")
shot("S42a", "L42", C([13.9, -1.6, 1.4], [15.9, 1.1, 0.95], 26, [14.1, -1.5, 1.4], [15.9, 1.1, 0.95], 26))
for k, u in enumerate([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]):
    check(f"L42.1+{0.14 * k:.2f}", ["q", "tick", round(u, 2)] if u < 1.0 else "C", big=True)
check("L42.1+1.2", "C", big=False)
hide("me", "L42.1")
put("me", "L42.1", [0.3, -0.2], 0, expr="stunned")
shot("S42b", "L42.1", C([0.3, -1.6, 1.55], [0.3, 0.0, 1.5], 30, [0.3, -1.4, 1.55], [0.3, 0.0, 1.5], 30))
# L43: a callback to S16a (my shut door, the strip under it), then me close
cue("L43", "strip", v=1.0, dur=0.4)
shot("S43", "L43", C([15.2, 0.4, 0.8], [12.0, 0.0, 0.6], 27, [14.6, 0.3, 0.7], [12.0, 0.0, 0.55], 27))
cue("L43+0.5", "strip", v=0.0, dur=0.4)
shot("S43b", "L43+0.5", C([0.3, -1.1, 1.58], [0.3, 0.0, 1.55], 34, [0.3, -0.9, 1.58], [0.3, 0.0, 1.55], 34))
# L44: the one reveal picture, a split of the two living rooms
hide("me", "L44")
look("L44", "split", 0)
cue("L44", "ringlight", v=0.0, dur=0.0)
shot("S44", "L44", C([120.0, -2.6, 1.3], [120.0, 1.0, 1.25], 17, [120.0, -2.3, 1.3], [120.0, 1.0, 1.25], 17))
# L45: the hall wall of photos, as grown-ups; push along them
look("L45", "lamp", 0)
ver("L45", "B")
shot("S45a", "L45", C([6.4, -0.5, 1.5], [7.3, 0.95, 1.5], 24, [7.6, -0.5, 1.5], [8.4, 0.95, 1.5], 24))
shot("S45b", "L45.1", C([8.8, -0.5, 1.5], [9.7, 0.95, 1.5], 24, [10.4, -0.5, 1.5], [10.9, 0.95, 1.5], 24))
# L46: callbacks (the sandwich, the day, the doorway beam)
look("L46", "lamp", 0)
obj("plate", "L46", [0.1, 0.3, 1.12])
shot("S46a", "L46", C([0.1, -0.5, 1.45], [0.1, 0.3, 1.12], 38))
obj("plate", "L46.1", hide_=True)
look("L46.1", "day", 0)
put("ben", "L46.1", [-3.8, 1.45], 0, sit=0.5, expr="laugh", head=[-20, 0])
shot("S46b", "L46.1", C([-3.3, -0.4, 1.35], [-3.6, 1.4, 1.25], 28))
look("L46.2", "night", 0)
hide("ben", "L46.2")
cue("L46.2", "doorm", open=1.0, dur=0.0)
put("ben", "L46.2", [12.0, 0.0], 94, expr="blank", arms=[85, 0])
fl("ben", "L46.2", 1.0)
shot("S46c", "L46.2", C([14.0, 0.3, 1.4], [12.0, 0.0, 1.45], 28, [13.4, 0.2, 1.4], [12.0, 0.0, 1.45], 28))
# L47: Ben alone on the teal couch at night; me at my window
fl("ben", "L47", -1.0)
cue("L47", "doorm", open=0.0, dur=0.0)
hide("ben", "L47")
put("ben", "L47", [S_M, SY], 0, sit=SZ, expr="sad", head=[40, 0])
shot("S47a", "L47", C([0.3, -1.6, 1.3], [0.3, 2.1, 1.0], 24, [0.3, -1.3, 1.3], [0.3, 2.1, 1.0], 24))
hide("ben", "L47.1")
put("me", "L47.1", [15.0, -1.7], 180, expr="uneasy")
shot("S47b", "L47.1", C([15.4, 0.6, 1.65], [14.2, -3.0, 1.5], 22, [15.2, 0.4, 1.65], [14.2, -3.0, 1.5], 22))

# ========================================================================================== 07 Saturday and the storm (L48 to L53)
# L48: daylight on the porch steps
hide("me", "L48")
look("L48", "day", 0)
put("ben", "L48", [2.1, -6.85], 0, sit=0.3, expr="sad", head=[0, 14])
put("me", "L48", [3.5, -6.85], 0, sit=0.3, expr="uneasy", head=[-20, 0])
shot("S48a", "L48", C([2.8, -10.0, 1.2], [2.8, -6.8, 0.95], 24, [2.8, -9.4, 1.2], [2.8, -6.8, 0.95], 24))
pose("ben", "L48.2", arms=[90, 0], head=[0, 22])
fl("ben", "L48.2", 0.0)
shot("S48b", "L48.2", C([-0.1, -7.5, 1.0], [1.6, -7.45, 0.85], 30, [0.1, -7.5, 0.98], [1.6, -7.45, 0.85], 30))
pose("ben", "L48.2+0.7", arms=[76, 0])
# L49: a drawer of batteries
look("L49", "split", 0)
gain("L49", 0.6)
KX, KY = G.KD
shot("S49", "L49", C([KX - 0.3, KY - 0.7, 1.55], [KX - 0.3, KY + 0.5, 0.85], 24, [KX - 0.3, KY - 0.5, 1.45], [KX - 0.3, KY + 0.5, 0.85], 24))
# L50: me on the porch, Pickle's head on my knee
look("L50", "day", 0)
gain("L50", 1.0)
fl("ben", "L50", -1.0)
hide("ben", "L50")
hide("me", "L50")
put("me", "L50", [2.8, -6.85], 0, sit=0.3, expr="thinking")
obj("dog", "L50", [2.15, -7.05, 0.0], 90)
shot("S50", "L50", C([3.4, -9.6, 1.1], [2.6, -6.9, 0.75], 28, [3.1, -9.2, 1.1], [2.6, -6.9, 0.75], 28))
# L51: the pile of crusts on a plate
hide("me", "L51")
obj("dog", "L51", hide_=True)
obj("plate", "L51", [0.3, 0.1, 0.46])
gain("L51", 0.45)
shot("S51", "L51", C([0.3, -0.45, 1.05], [0.3, 0.1, 0.46], 34, [0.3, -0.35, 1.0], [0.3, 0.1, 0.46], 34))
gain("L52", 1.0)
# L52: a storm over the street
obj("plate", "L52", hide_=True)
look("L52", "storm", 0)
cue("L52", "clouds", on=True)
shot("S52", "L52", C([0.0, -9.0, 1.2], [0.0, -22.0, 8.0], 20, [0.0, -9.0, 1.6], [0.0, -22.0, 9.5], 20))
# L53: the lamp ramps off
look("L53", "lamp", 0)
cue("L53", "clouds", on=False)
look("L53+0.3", "night", 0.45)
shot("S53", "L53", C([-3.9, -3.1, 1.5], [1.0, 2.0, 1.2], 24, [-3.6, -3.0, 1.5], [1.0, 2.0, 1.2], 24))
# L54: Ben walks me to my room
put("ben", "L54", [8.8, 0.2], 90, expr="soft", arms=[85, 0])
fl("ben", "L54", 1.0)
put("me", "L54", [7.4, -0.2], 90, expr="uneasy")
go("ben", "L55", [11.0, 0.2])   # one steady walk over L54 and L54.2 (no sprint, no dead stop)
go("me", "L55", [9.6, -0.2])
shot("S54a", "L54", C([5.2, -0.1, 1.55], [9.5, 0.0, 1.3], 24, [5.6, -0.1, 1.55], [10.0, 0.0, 1.3], 24))
acting["ben"].append({"at": "L54.2", "yaw": 60})   # turn without a pos key: the walk carries on
shot("S54b", "L54.2", C([8.3, -0.9, 0.85], [11.5, -0.2, 0.7], 24, [8.6, -0.9, 0.8], [11.8, -0.2, 0.65], 24))
# L55: Ben, close, in his own beam
hide("me", "L55")
hide("ben", "L55")
put("ben", "L55", [11.0, 0.0], -90, expr="soft", arms=[0, 0])
fl("ben", "L55", -1.0)
uplight("L55", 1.0, [10.3, 0.0, 0.8], [11.0, 0.0, 1.5])
shot("S55", "L55", C([9.0, 0.1, 1.55], [11.0, 0.0, 1.5], 36, [9.4, 0.1, 1.55], [11.0, 0.0, 1.5], 36))
# L56: my door closes, the strip of light goes; me alone on my bed
uplight("L56", 0.0, dur=0.4)
hide("ben", "L56")
cue("L56", "doorm", open=1.0, dur=0.0)
cue("L56", "doorm", open=0.0, dur=0.6)
cue("L56", "strip", v=1.0, dur=0.4)
cue("L56+0.8", "strip", v=0.0, dur=0.4)
shot("S56a", "L56", C([15.0, 0.4, 0.9], [12.0, 0.0, 0.8], 28, [14.4, 0.3, 0.9], [12.0, 0.0, 0.8], 28))
put("me", "L56.2", [16.05, 1.15], -90, sit=0.66, expr="squeeze")
shot("S56b", "L56.2", C([13.9, -1.6, 1.4], [15.9, 1.1, 0.95], 26, [14.2, -1.5, 1.4], [15.9, 1.1, 0.95], 26))
# L57: the clock, 9:41 turns to 9:42
cue("L57", "clock", txt="9:41")
cue("L57+1.1", "clock", txt="9:42")
shot("S57", "L57", C([14.6, -0.9, 0.95], [16.35, -0.1, 0.62], 34, [15.0, -0.7, 0.9], [16.35, -0.1, 0.62], 34))

# ========================================================================================== 08 home again (L58 to L67)
look("L58", "night", 0)
look("L58+0.2", "lamp", 0.5)
ver("L58", "A")
watch("L58", "L")
hide("me", "L58")
shot("S58", "L58", C([14.8, 0.6, 1.2], [12.0, 0.2, 1.1], 22))
cue("L59-0.7", "doorm", open=1.0, dur=0.4)
put("ben", "L59", [12.0, 0.0], 90, expr="unsure")
go("ben", "L59.1+0.2", [12.0, 0.0])
go("ben", "L60", [12.7, 0.0])
cue("L60", "doorm", open=0.0, dur=0.0)
shot("S59", "L59", C([15.0, 0.4, 1.3], [8.0, 0.4, 1.2], 22, [14.4, 0.4, 1.3], [8.0, 0.4, 1.2], 22))
pose("ben", "L60", arms=[0, 30])
shot("S60", "L60", C([14.6, 1.5, 1.3], [12.9, 0.85, 1.0], 34, [14.3, 1.4, 1.25], [12.9, 0.85, 1.0], 34))
# L61 "My BEN.": Ben on the line, not me; every icon in the check inset gets a tick
check("L61", "D")
pose("ben", "L61", expr="soft")
put("me", "L61", [15.0, 1.15], -90, sit=0.66, expr="relief")
shot("S61", "L61", C([14.7, 0.4, 1.5], [12.7, 0.0, 1.38], 26, [14.4, 0.3, 1.48], [12.7, 0.0, 1.38], 26))
pose("ben", "L62", expr="unsure")
shot("S62", "L62", C([14.7, 0.5, 1.5], [12.7, 0.0, 1.38], 26, [14.3, 0.3, 1.48], [12.7, 0.0, 1.38], 26))
pose("ben", "L63", expr="polite", arms=[0, 165], head=[0, 8])
shot("S63a", "L63", C([14.6, 0.2, 1.5], [12.7, 0.0, 1.38], 26))
pose("me", "L63.2", expr="stunned")
shot("S63b", "L63.2", C([13.0, 0.5, 1.4], [15.3, 1.15, 1.2], 24))
pose("ben", "L64", expr="sheepish", arms=[0, 0], head=[35, 6])
shot("S64", "L64", C([14.6, 0.1, 1.5], [12.7, 0.0, 1.38], 26, [14.3, 0.1, 1.48], [12.7, 0.0, 1.38], 26))
# L65: I hold a plate out to him
hide("ben", "L65")
hide("me", "L65")
look("L65", "day", 0)
put("me", "L65", [0.3, -0.3], 180, expr="soft", arms=[80, 80])
obj("plate", "L65", [0.3, 0.3, 1.12])
shot("S65", "L65", C([0.3, 1.8, 1.4], [0.3, -0.2, 1.35], 26, [0.3, 1.5, 1.4], [0.3, -0.2, 1.35], 26))
hide("me", "L66")
obj("plate", "L66", [0.3, 0.28, 1.15])
gain("L66", 0.45)
shot("S66", "L66", C([0.3, 0.55, 2.2], [0.3, 0.28, 1.15], 24, [0.3, 0.45, 2.0], [0.3, 0.28, 1.15], 24))
gain("L67", 1.0)
# L67: Ben looks from the sandwich to me, the question mark returns; push in to the first frame
put("ben", "L67", [0.3, 0.95], 0, expr="suspicious", arms=[85, 85])
check("L67", "C")
shot("S67a", "L67", C([0.3, -1.9, 1.5], [0.3, 0.9, 1.4], 30))
look("L67.1", "day", 0.5)
shot("S67b", "L67.1", C([0.3, -1.8, 1.52], [0.3, 0.9, 1.42], 36, [0.3, -1.5, 1.52], [0.3, 0.9, 1.42], 36))

# ---------------------------------------------------------------------------------------------- finish the lists
for k_ in acting.values():
    remap_all(k_)
remap_all(cues)
shots = []
for i, (id_, at, camera, step, hand, follow) in enumerate(SH):
    s = {"id": id_, "cam": camera, "step": step}
    if i:
        s["at"] = remap(at)
    if hand is not None:
        s["hand"] = hand
    if follow:
        s["follow"] = follow
    shots.append(s)

sfx = [
    {"at": "L01.2+0.15", "kind": "click", "db": -14},
    {"at": "L13.1", "kind": "glide", "db": -20, "dur": 0.9},
    {"at": "L16", "kind": "knock", "db": -13, "pattern": [0, 0.4], "tone": "soft"},
    {"at": "L38", "kind": "click", "db": -12},
    {"at": "L53.1", "kind": "glide", "db": -20, "dur": 0.9},
    {"at": "L56+0.55", "kind": "door", "db": -16},
    {"at": "L58", "kind": "riser", "db": -22, "dur": 0.7},
]
music = {
    "root": 55, "mode": "harmonic", "bpm": 86, "seed": 92,
    "sections": [
        {"at": 0, "voices": ["pad", "pulse"], "energy": 0.4},
        {"at": "L03", "voices": ["pad", "pulse", "drone"], "energy": 0.5},
        {"at": "L06", "voices": ["pad", "pulse"], "energy": 0.4},
        {"at": "L13", "voices": ["pad", "drone"], "energy": 0.45},
        {"at": "L17", "voices": ["pad", "piano"], "energy": 0.45},
        {"at": "L31", "voices": ["drone"], "energy": 0.8},
        {"at": "L39", "voices": ["drone", "piano"], "energy": 0.6},
        {"at": "L45", "voices": ["pad"], "energy": 0.4},
        {"at": "L52", "voices": ["drone"], "energy": 0.7},
        {"at": "L58", "voices": ["pad", "pulse"], "energy": 0.5},
        {"at": "L65", "voices": ["pad", "piano"], "energy": 0.5},
    ],
}
sound = {
    "floor": "wood", "steps_db": -22,
    "floor_spans": [{"from": "L03", "to": "L11", "floor": "grass"}, {"from": "L48", "to": "L52", "floor": "wood"}],
    "ambience": [
        {"kind": "crickets", "from": "L03", "to": "L11", "lufs": -40},
        {"kind": "hum", "from": "L13", "to": "L17", "lufs": -38},
        {"kind": "hum", "from": "L31", "to": "L39", "lufs": -36},
        {"kind": "rain", "from": "L52", "to": "L54", "lufs": -34},
        {"kind": "hum", "from": "L54", "to": "L58", "lufs": -38},
    ],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
}

story = {
    "slug": "ep92-blackout-ben",
    "title": "After The Blackout, Ben Was NICE",
    "made_for_kids": False,
    "premise": ("In this town a blackout can swap anyone sitting alone in the dark with another version of themselves, "
                "so families sit together with flashlights and check each other after. My big brother Ben and I haven't "
                "been nice to each other in three years, and after Tuesday's blackout he makes me a sandwich with the "
                "crusts cut off."),
    "twist": ("Ben didn't swap. I did: I was the one alone in the dark on Tuesday, and I woke in the house where "
              "my brother and I never stopped being friends. Swapped back at the next blackout, my real Ben says the "
              "other me was nice all week, so I make him the sandwich, and now he's sure I'm not his."),
    "world": ("One summer week in a suburban house: a sunny living room with a big window, a mantel, a couch that is "
              "mustard in my version and teal in this one, a hall of photos, my bedroom with a bedside clock, a street "
              "of painted houses with porches that goes dark and lights up."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff5a4e",
    "gap": 0.12,
    "tail": 0.25,
    "look": {"fog": "#9fd0ff", "fog_density": 0.0, "fog_start": 30.0, "sky": "#a8d8ff", "sky_strength": 1.0,
             "exposure": 0.3, "flash_safe": True, "style": "closer",
             "polish": {"emph": ["L02", "L19", "L22", "L36", "L44", "L67"], "reveal": ["L44"], "twist": "L42",
                        "sway": ["S32", "S33", "S34", "S35b", "S36"], "hold": ["S44"]}},
    "grade": {"shadows": [-0.01, 0.0, 0.05], "highlights": [0.03, 0.01, -0.02], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.25, "grain": 0.009, "red_line": 0.7},
    "phonemes": {"varga": "vˈɑɹɡɑ", "wrist": "ɹˈɪst"},
    "clip_ok": ["tblfl", "fl"],
    # QA-checked deliberate close pairs (cast standing close in a corridor/clump, arms clear): kept as shot/pair
    "staging_ok": ["S06a/f1+f3", "S06a/f2+f3", "S09/dale+f1", "S09/dale+f2", "S09/dale+f3", "S09/f1+f3", "S09/f2+f3",
                   "S27/me+ben", "S27b/me+ben", "S27c/me+ben", "S28/me+ben", "S29b/me+ben"],
    "rain_shots": ["S52"],
    "set_moves": ["S03", "S26", "S45a", "S45b", "S52"],
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "rev": 4,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["floor_spans"])
remap_all(sound["ambience"])
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
