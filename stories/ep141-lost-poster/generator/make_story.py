"""Writes ../story.json for "The LOST Poster Has My Face" (ep141-lost-poster, batch 15). Run: python stories/ep141-lost-poster/generator/make_story.py

The words are in lines.json (the script's narration). Places are in ../layout.py (shared with set.py). A character facing -y
has yaw 0, +x 90, +y 180, -x -90; a camera `az` degrees round from the south looks at a character facing it with yaw = az.
Time references use the script's chunk numbers (L25.1 is the second slash-chunk of L25); timeline.split_lines cuts long
captions into two or three words and the references are remapped.

One bright sunny day look all the way through: no look cues, no light changes, nothing blinks or flickers.
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent.parent))
import layout as G  # noqa: E402
from blocky import timeline as T  # noqa: E402

OUT = HERE.parent / "story.json"
REV = 9
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = T.split_lines(orig_lines)
idx = next(i for i, l in enumerate(lines) if l["id"] == "L21")
lines.insert(idx, {"id": "P01", "pause": 0.5, "chunks": [["", ""]]})     # the 0.5 s music drop before L21


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
X = {"neutral": "neutral", "uneasy": "worried", "stunned": "wide", "sheepish": "sad-smile", "sly": "smirk",
     "proud": "warm", "scared": "scared", "smile": "smile", "laugh": "laugh", "warm": "warm"}


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", hat="none", hat_c="#333333", extras=(), eyes="round",
           sleeves="long", face=None, **kw):
    d = {"age": "adult", "body_width": 0.7, "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c,
         "face": {"eyes": eyes, "brows": True, "ink": "#24131f"}}
    if face:
        d["face"].update(face)
    if extras:
        d["extras"] = list(extras)
    d.update(kw)
    return d


cast = {
    # me: a tall red-brown quiff (built in set.py), light freckled skin
    "me": person("#f1c9a0", "#2f9aa0", "#3d4660", "#f4f4f2", hair="swoop", hair_c="#b4532c", sleeves="short",
                 face={"freckles": True, "brow_w": 1.2}),
    # the same man in a white tee and a blue apron (from the tent on)
    "me_b": person("#f1c9a0", "#ece8e0", "#3d4660", "#f4f4f2", hair="swoop", hair_c="#b4532c", sleeves="short",
                   extras=["apron"], extra_c="#3a6fd0", face={"freckles": True, "brow_w": 1.2}),
    # Mom: a dark bob (built in set.py), a pink sweater, lashes
    "mom": person("#f1c9a0", "#f0a0b8", "#5a6a8a", "#6a4a32", hair="cap", hair_c="#2a1a1a", eyes="lashes",
                  face={"cheeks": "#f0a590"}),
    # Grandma: white curls in a big round puff (set.py), glasses, a lavender cardigan, a flowered apron (set.py)
    "grandma": person("#f1c9a0", "#a98ad8", "#6a5a7a", "#5a4a5a", hair="cap", hair_c="#ece8f2", eyes="lashes",
                      extras=["glasses"], glasses_c="#3a2a3a", height=0.93, face={"cheeks": "#f0a590", "bags": True}),
    # Mr. Park: a gray cap, a wet-dark jacket
    "park": person("#d9a47a", "#4a5a6a", "#3a3a44", "#2f2a26", hair="cap", hair_c="#4a3626", hat="ballcap", hat_c="#8a8d92",
                   face={"brow_w": 1.3}),
    # my cousin: a green jacket
    "cousin": person("#c98f64", "#4a9a5a", "#3a3a52", "#3a2a1a", hair="buzz", hair_c="#1a1410", face={"brow_w": 1.3}),
    # my aunt: a plum cardigan, a bun
    "aunt": person("#e2b088", "#9a6ac0", "#4a4a60", "#4a3a2a", hair="bun", hair_c="#7a5a4a", eyes="lashes",
                   face={"cheeks": "#f0a590"}),
    # the judges: a green blazer and a red tie; a plum blouse and a bun
    "judgeA": person("#e2b088", "#3a8a5a", "#3a3a4a", "#2a2a2a", hair="cap", hair_c="#2a1d15", extras=["tie"],
                     extra_c="#d8322f", face={"brow_w": 1.2}),
    "judgeB": person("#b88a62", "#7a5aa8", "#3a3a4a", "#2a2a2a", hair="bun", hair_c="#241a16", eyes="lashes",
                     face={"cheeks": "#e89a80"}),
}
acting = {n: [] for n in cast}
last = {n: None for n in cast}
vis = set()
cues = []
SH = []
FAR = [0.0, -300.0, 0.0]
for w_ in cast:
    acting[w_].append({"at": 0, "pos": list(FAR), "yaw": 0, "hidden": True})
    last[w_] = list(FAR)


def K(who, at, pos=None, **kw):
    """A key at `at`; the position is held from the last key unless `pos` is given (then it walks there)."""
    p = list(pos) if pos is not None else list(last[who])
    if "expr" in kw:
        kw["expr"] = X.get(kw["expr"], kw["expr"])
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def TP(who, at, pos, yaw, expr="neutral", **kw):
    """The character is there from this instant (a cut); everything it doesn't set goes back to neutral."""
    if last[who] is not None:
        acting[who].append({"at": at, "pos": list(last[who]), "blend": 0.0})
    st = {"hidden": False, "arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "look": [0, 0]}
    st.update(kw)
    acting[who].append({"at": at, "pos": list(pos), "blend": 0.0, "yaw": yaw, "expr": X.get(expr, expr), **st})
    last[who] = list(pos)


def HIDE(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0.0})


def scene(at, **chars):
    """Everyone in `chars` is placed at this cut (pos, yaw, expr, ...); anyone who was on screen and isn't is hidden."""
    global vis
    for w in vis - set(chars):
        HIDE(w, at)
    for w, spec in chars.items():
        spec = dict(spec)
        TP(w, at, spec.pop("pos"), spec.pop("yaw", 0), spec.pop("expr", "neutral"), **spec)
    vis = set(chars)


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def tag(at, n=None, clock=None):
    kw = {}
    if n is not None:
        kw["n"] = n
    if clock is not None:
        kw["clock"] = clock
    cue(at, "tag", **kw)


def cam(tx, ty, tz, w, az, lens, cz=None, push=None):
    """A camera looking at (tx, ty, tz) from az degrees round from the south, far enough off that the frame is w metres
    wide there. One key or, with push=(w2, tz2), two keys."""
    def at_(ww, tzz, czz):
        d = ww * lens / 13.5
        return [round(tx + d * math.sin(az * D2R), 3), round(ty - d * math.cos(az * D2R), 3),
                czz if czz is not None else tzz], [tx, ty, tzz]
    p, t_ = at_(w, tz, cz)
    keys = [[0, p, t_, lens]]
    if push:
        p2, t2 = at_(push[0], push[1], None if cz is None else cz + (push[1] - tz))
        keys.append([1, p2, t2, lens])
    return keys


def camp(pos, tgt, lens, pos2=None, tgt2=None):
    keys = [[0, list(pos), list(tgt), lens]]
    if pos2 is not None or tgt2 is not None:
        keys.append([1, list(pos2 or pos), list(tgt2 or tgt), lens])
    return keys


def shot(sid, at, camera, **kw):
    SH.append((sid, at, camera, kw))


def P(c, x, y, z=0.0):
    return [round(c[0] + x, 3), round(c[1] + y, 3), z]


C, MAIL, AD, GD, CAR = G.CORNER, G.MAIL, G.ADOOR, G.GDOOR, G.CAR
MK, CD, GK, TN = G.MOMK, G.CARD, G.GRANK, G.TENT
L36 = 36

def fr(x, w, f=0.62):
    """The camera target x that puts a subject at x at `f` of the frame's width (right of the tag)."""
    return round(x - (f - 0.5) * w, 3)


# ================================================================================================== 01 the rule (L01, L02)
tag(0, 7, 0)
ME1 = P(C, -0.1, 1.3)
scene(0, me=dict(pos=ME1, yaw=0, expr="stunned"))
shot("S01a", 0, cam(0.3, 2.2, 1.2, 2.1, 0, L36, cz=1.4, push=(1.9, 1.2)))
shot("S01b", "L01.3", cam(0.22, 2.4, 1.4, 1.7, 0, L36, cz=1.45, push=(1.45, 1.4)))
K("me", "L02", ME1, yaw=0, expr="scared", blend=0.1)
K("me", "L02.1", ME1, yaw=10, expr="scared", head=[-14, 0], arms=[0, 0], side=[20, -20], blend=0.7)
shot("S02", "L02", cam(fr(ME1[0], 1.4), 1.3, 1.25, 1.4, 0, L36, cz=1.45, push=(1.2, 1.25)))

# ================================================================================================== 02 two small payoffs
PARK = P(C, -1.2, 1.3)
scene("L03", park=dict(pos=PARK, yaw=0, expr="sheepish"))
shot("S03a", "L03", cam(-1.0, 1.9, 1.2, 1.9, 0, L36, cz=1.4, push=(1.7, 1.2)), _rain=True)
shot("S03b", "L03.2", cam(-1.1, 1.9, 1.3, 1.7, 8, L36, cz=1.4, push=(1.45, 1.3)), _rain=True)
COUS = P(CAR, -0.4, 1.3)
scene("L04", cousin=dict(pos=COUS, yaw=0, expr="uneasy"))
for i in range(5):
    K("cousin", f"L04+{0.28 * i:.2f}", COUS, yaw=0, expr="uneasy", head=[18, 8 if i % 2 == 0 else -8], blend=0.2)
shot("S04a", "L04", cam(CAR[0] - 0.1, 2.0, 1.0, 2.1, 0, L36, cz=1.2, push=(1.9, 1.0)))
scene("L04.2")
shot("S04b", "L04.2", cam(-0.45, 2.9, 1.6, 2.3, 0, L36, cz=1.6, push=(2.0, 1.6)))

# ================================================================================================== 03 Mom (L05 to L07)
tag("L05", 6)
MOM1 = P(MK, 0.3, 1.4)
scene("L05", mom=dict(pos=MOM1, yaw=0, expr="scared"))
shot("S05", "L05", cam(MK[0] + 0.3, MK[1] + 1.4, 1.2, 1.4, 0, L36, cz=1.4, push=(1.2, 1.2)))
MOMM, MEM = P(MAIL, -0.55, 1.2), P(MAIL, 0.5, 1.7)
scene("L06", mom=dict(pos=MOMM, yaw=0, expr="uneasy"), me=dict(pos=MEM, yaw=0, expr="sheepish"))
shot("S06", "L06", cam(MAIL[0] - 0.02, 1.8, 1.2, 2.3, 0, L36, cz=1.4, push=(2.05, 1.2)))
tag("L07", 5)
AUNT, MEA = P(AD, -0.55, 1.7), P(AD, 0.45, 2.15)
scene("L07", aunt=dict(pos=AUNT, yaw=0, expr="uneasy", arms=[80, 80]), me=dict(pos=MEA, yaw=0, expr="sheepish"))
cue("L07", "scarf", on=1.0, x=AUNT[0], y=AUNT[1] - 0.62, z=1.17)
shot("S07b", "L07", cam(AD[0] - 0.05, 2.0, 1.2, 1.9, 0, L36, cz=1.4, push=(1.7, 1.2)))
cue("L08", "scarf", on=0.0)

# ================================================================================================== 04 Grandma (L08 to L14)
GRA = P(GD, 0.7, 2.2)
scene("L08", grandma=dict(pos=GRA, yaw=0, expr="smile"))
shot("S08a", "L08", cam(GD[0] + 0.35, 2.4, 1.2, 1.9, 0, L36, cz=1.4, push=(1.65, 1.2)))
shot("S08b", "L08.2", cam(GRA[0] - 0.1, 2.4, 1.3, 1.6, -8, L36, cz=1.4, push=(1.4, 1.3)))
K("grandma", "L09", GRA, yaw=0, expr="sly", blend=0.2)
shot("S09", "L09", cam(GRA[0] - 0.05, 2.2, 1.2, 1.25, 6, L36, cz=1.4, push=(1.05, 1.2)))
GOLDME = P(CD, 2.0, 3.3)
scene("L10", me=dict(pos=GOLDME, yaw=0, expr="sheepish"))
shot("S10a", "L10", cam(CD[0] + 2.3, CD[1] + 3.8, 1.6, 2.1, 0, 26, cz=1.7, push=(1.9, 1.6)))
shot("S10b", "L10.2", cam(CD[0] + 2.2, CD[1] + 3.8, 1.5, 1.6, 6, 26, cz=1.65, push=(1.4, 1.5)))
GRB = P(GK, -2.4, 3.3)
scene("L11", grandma=dict(pos=GRB, yaw=0, expr="smile"))
shot("S11a", "L11", cam(GK[0] - 2.6, GK[1] + 3.8, 1.6, 2.1, 0, 26, cz=1.7, push=(1.9, 1.6)))
shot("S11b", "L11.1", cam(GK[0] - 2.5, GK[1] + 3.8, 1.5, 1.6, -6, 26, cz=1.65, push=(1.4, 1.5)))
tag("L12", 4)
scene("L12", grandma=dict(pos=GRA, yaw=0, expr="sly"))
cue("L12", "watch", on=1.0)
K("grandma", "L12", GRA, yaw=0, expr="sly", arms=[55, 82], side=[-22, 0], blend=0.4)
for i in range(4):
    K("grandma", f"L12+{0.4 + 0.3 * i:.2f}", GRA, yaw=0, expr="sly", arms=[55 if i % 2 else 66, 82], side=[-22, 0], blend=0.12)
shot("S12b", "L12", cam(GRA[0] - 0.05, 2.2, 1.15, 1.5, 0, L36, cz=1.35, push=(1.3, 1.15)))
tag("L13", 3)
cue("L12>", "watch", on=0.0)
GRC = P(GK, 1.7, 2.3)
cue("L13", "flour", on=1.0)
scene("L13", grandma=dict(pos=GRC, yaw=0, expr="smile"))
shot("S13a", "L13", cam(GK[0] + 1.8, GK[1] + 3.0, 1.2, 2.1, 0, 28, cz=1.4, push=(1.8, 1.2)))
shot("S13b", "L13.2", cam(GK[0] + 1.75, GK[1] + 3.0, 1.1, 1.6, -6, 28, cz=1.35, push=(1.4, 1.1)))
cue("L14", "flour", on=0.0)
tag("L14", 2)
scene("L14", grandma=dict(pos=GRA, yaw=0, expr="sly"))
shot("S14a", "L14", cam(GRA[0] - 0.05, 2.2, 1.2, 1.4, -9, L36, cz=1.4, push=(1.2, 1.2)))
shot("S14b", "L14.2", cam(GRA[0] - 0.05, 2.2, 1.25, 1.15, 4, L36, cz=1.4, push=(1.0, 1.25)))

# ================================================================================================== 05 the pie tent (L15 to L20)
tag("L15", 1, 0)
tag("L15.2", 1, 1058)
JA, JB = P(TN, -1.0, 3.1), P(TN, 0.86, 2.97)
scene("L15", judgeA=dict(pos=JA, yaw=0, expr="neutral"), judgeB=dict(pos=JB, yaw=0, expr="neutral"))
shot("S15a", "L15", camp([TN[0] + 4.3, TN[1] - 3.6, 1.7], [TN[0] - 1.0, TN[1] + 2.4, 1.25], 24,
                         pos2=[TN[0] + 3.9, TN[1] - 3.3, 1.7]))
MEB, MOMB = P(TN, -0.5, 0.9), P(TN, 0.4, 0.9)
MOMHAND = dict(arms=[12, 0], side=[-16, 0])
scene("L15.2", me_b=dict(pos=MEB, yaw=0, expr="uneasy"))
shot("S15c", "L15.2", cam(fr(MEB[0], 1.4), TN[1] + 0.9, 1.2, 1.4, 0, 28, cz=1.4, push=(1.2, 1.2)))
scene("L16", me_b=dict(pos=MEB, yaw=0, expr="uneasy"), mom=dict(pos=MOMB, yaw=0, expr="scared"))
K("mom", "L16+0.2", MOMB, yaw=0, expr="scared", **MOMHAND, blend=0.5)
shot("S16", "L16", cam(TN[0] - 0.1, TN[1] + 1.0, 1.1, 2.3, 0, 28, cz=1.4, push=(2.05, 1.1)))
tag("L17", 1, 1059)
scene("L17", me_b=dict(pos=MEB, yaw=0, expr="uneasy"), mom=dict(pos=MOMB, yaw=0, expr="scared", **MOMHAND))
shot("S17", "L17", cam(fr(MEB[0], 1.4), TN[1] + 0.9, 1.2, 1.4, 0, L36, cz=1.4, push=(1.2, 1.2)))
scene("L18", judgeA=dict(pos=JA, yaw=0, expr="neutral", head=[0, 0]), judgeB=dict(pos=JB, yaw=0, expr="neutral"))
for i in range(3):
    K("judgeA", f"L18.1+{0.35 * i:.2f}", JA, yaw=0, expr="neutral", head=[0, 9 if i % 2 == 0 else -3], blend=0.2)
shot("S18", "L18", cam(JA[0] - 0.1, JA[1], 1.2, 1.5, 0, L36, cz=1.4, push=(1.25, 1.2)))
cue("L19", "pie", on=1.0)
scene("L19", judgeA=dict(pos=JA, yaw=0, expr="stunned"), judgeB=dict(pos=JB, yaw=0, expr="neutral"))
shot("S19a", "L19", cam(fr(JA[0], 1.5), JA[1], 1.2, 1.5, 0, L36, cz=1.4, push=(1.25, 1.2)))
GRT = P(TN, 2.9, 1.3)
scene("L19.1", grandma=dict(pos=GRT, yaw=0, expr="sly", look=[0.7, 0]))
shot("S19b", "L19.1", cam(fr(GRT[0], 1.3), GRT[1], 1.2, 1.3, -6, L36, cz=1.4, push=(1.1, 1.2)))
MEC, MOMC = P(TN, -0.5, 0.9), P(TN, 0.4, 0.9)
scene("L19.2+0.25", me_b=dict(pos=MEC, yaw=0, expr="uneasy"), mom=dict(pos=MOMC, yaw=0, expr="scared", **MOMHAND))
shot("S19c", "L19.2+0.25", cam(fr(MEC[0] + 0.45, 2.0), TN[1] + 0.9, 1.2, 2.0, 0, 28, cz=1.4, push=(1.75, 1.2)))
tag("L20", 1, 1100)
BELL = [TN[0] + 0.5, TN[1] + 2.35, 0.9]
scene("L20", judgeB=dict(pos=JB, yaw=0, expr="neutral", arms=[72, 0]))
K("judgeB", "L20.1", JB, yaw=0, expr="neutral", arms=[62, 0], blend=0.1)
K("judgeB", "L20.1+0.3", JB, yaw=0, expr="neutral", arms=[72, 0], blend=0.2)
K("judgeB", "L20.1+0.6", JB, yaw=0, expr="neutral", arms=[62, 0], blend=0.1)
cue("L20", "palm", on=1.0, z=1.6)
cue("L20.1", "palm", on=1.0, z=1.2)
cue("L20.1+0.3", "palm", on=1.0, z=1.08)
cue("P01", "palm", on=0.0, z=1.08)
shot("S20", "L20", cam(BELL[0] + 0.05, BELL[1], 0.95, 0.75, 0, L36, cz=1.0, push=(0.65, 0.95)))
cue("P01", "pie", on=0.0)
scene("P01")
shot("S20b", "P01", camp([TN[0] + 3.6, TN[1] - 3.2, 1.7], [TN[0] - 4.0, TN[1] + 1.0, 1.4], 24,
                         pos2=[TN[0] + 3.4, TN[1] - 3.0, 1.7]))

# ================================================================================================== 06 the twist (L21, L22)
GW = P(TN, 0.7, 1.0)
cue("L21", "trophy", on=1.0, x=GW[0], y=GW[1] - 0.5, z=0.8)
scene("L21", grandma=dict(pos=GW, yaw=0, expr="laugh", arms=[50, 50]))
shot("S21a", "L21", cam(fr(GW[0], 1.6), GW[1] - 0.1, 1.05, 1.6, 0, L36, cz=1.3, push=(1.4, 1.05)))
MED = P(TN, -0.6, 0.9)
scene("L22", me_b=dict(pos=MED, yaw=0, expr="stunned"))
shot("S22", "L22", cam(fr(MED[0], 1.35), MED[1], 1.2, 1.35, 0, L36, cz=1.4, push=(1.15, 1.2)))
cue("L26", "trophy", on=0.0, x=TN[0], y=TN[1] + 2.4, z=0.9)

# ================================================================================================== 07 Mom lets go, then the banner: the recast (L26, L25)
MEF, MOMF = P(TN, -0.5, 0.9), P(TN, 0.4, 0.9)
scene("L26", me_b=dict(pos=MEF, yaw=0, expr="laugh"), mom=dict(pos=MOMF, yaw=0, expr="laugh", **MOMHAND))
shot("S26a", "L26", cam(fr((MEF[0] + MOMF[0]) / 2, 2.0, 0.55), MOMF[1], 1.2, 2.0, 0, L36, cz=1.4, push=(1.8, 1.2)))
K("mom", "L26.1", MOMF, yaw=0, expr="laugh", **MOMHAND, blend=0.01)
K("mom", "L26.1+0.35", MOMF, yaw=0, expr="laugh", arms=[0, 0], side=[0, 0], blend=0.4)
shot("S26b", "L26.1", cam(fr((MEF[0] + MOMF[0]) / 2, 1.9, 0.55), MOMF[1], 1.2, 1.9, 6, L36, cz=1.4, push=(1.7, 1.2)))
cue("L25", "banner", on=1.0)
GBN = P(TN, -4.3, 2.7)
scene("L25", grandma=dict(pos=GBN, yaw=0, expr="proud", arms=[70, 70]))
shot("S24", "L25", cam(GBN[0] - 0.25, GBN[1] - 0.3, 1.0, 2.0, 0, 28, cz=1.5, push=(1.7, 1.0)))
shot("S25", "L25.2", cam(GBN[0] - 0.25, GBN[1] - 0.3, 1.0, 1.5, 0, L36, cz=1.3, push=(1.3, 1.0)))
cue("L28", "banner", on=0.0)

# ================================================================================================== 08 Sunday again (L28, the button and loop)
tag("L28", 7, 0)
cue("L28", "gposter", on=1.0)
cue("L28", "tally", on=1.0)
scene("L28")
shot("S28a", "L28", cam(0.8, 2.9, 1.8, 3.4, 0, L36, cz=1.5, push=(3.1, 1.8)))
shot("S28b", "L28.1", cam(1.5, 2.9, 2.0, 2.0, 0, L36, cz=1.7, push=(1.7, 2.0)))
ME29 = P(C, 0.85, 1.7)
scene("L28.2", me_b=dict(pos=ME29, yaw=0, expr="smile"))
shot("S29a", "L28.2", cam(1.25, 2.4, 1.3, 2.0, 0, L36, cz=1.5, push=(1.75, 1.3)))
K("me_b", "L28.3", ME29, yaw=0, expr="warm", blend=0.3)
shot("S29b", "L28.3", cam(1.2, 2.3, 1.25, 1.7, 0, L36, cz=1.5, push=(1.45, 1.25)))

# ================================================================================================== finish
remap_all(cues)
for ks in acting.values():
    remap_all(ks)

shots = []
rain = []
for i, (sid, at, camera, kw) in enumerate(SH):
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    kw = dict(kw)
    if kw.pop("_rain", False):
        rain.append(sid)
    s.update(kw)
    shots.append(s)

sfx = [
    {"at": "L20.1", "kind": "bell", "db": -14},
    {"at": "L21", "kind": "sting", "db": -14, "keep": True},
    {"at": "L12+0.4", "kind": "click", "db": -22},
    {"at": "L12+1.0", "kind": "click", "db": -22},
    {"at": "L15.2", "kind": "click", "db": -20},
    {"at": "L17", "kind": "click", "db": -20},
]
music = {
    "root": 45, "mode": "minor", "bpm": 112, "seed": 141,
    "sections": [
        {"at": 0, "voices": ["musicbox", "pulse"], "energy": 0.45},
        {"at": "L05", "voices": ["musicbox", "drone"], "energy": 0.4},
        {"at": "L08", "voices": ["musicbox", "pulse", "pad"], "energy": 0.5},
        {"at": "L15", "voices": ["pulse", "musicbox", "drone"], "energy": 0.62},
        {"at": "L21", "voices": ["piano", "pad", "pulse"], "energy": 0.7, "mode": "major"},
        {"at": "L28", "voices": ["musicbox", "pad"], "energy": 0.4, "mode": "major"},
    ],
}
sound = {
    "floor": "grass", "steps_db": -26,
    "ambience": [],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>", "keep": ["sting"]}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
polish = {"push": 0.16, "sway": True, "sway_amp": 0.005, "reveal": ["L21", "L25"], "twist": "L21", "hold": ["S15a", "S25", "S28a"]}
story = {
    "slug": "ep141-lost-poster",
    "title": "The LOST Poster Has My Face",
    "made_for_kids": False,
    "premise": ("In our town, if the LOST poster on the corner shows your face you've got one week, and when mine went up "
                "my whole family treated me like I was about to go missing."),
    "twist": ("'Lost' was about the town pie contest: on Saturday at eleven I lose to Grandma for the first time in six years "
              "and she'd painted her victory banner on the very Sunday my poster went up."),
    "world": ("A sunny town: a wooden notice board on a street corner with cream LOST posters carrying a red question mark "
              "and a drawing, Mom's kitchen, Grandma's kitchen and a white-and-red striped pie tent on the green."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff5a4f",
    "gap": 0.15,
    "tail": 0.0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#dfe8f4", "fog_density": 0.001, "fog_start": 80.0, "sky": "#8fd0ff",
             "sky_strength": 1.0, "exposure": 0.05, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.02], "highlights": [0.03, 0.012, -0.02], "saturation": 1.9, "contrast": 1.04,
              "vignette": 0.15, "bloom": 0.15, "grain": 0.008},
    "hud": {"object": "tag", "at": [-0.39, 0.61], "size": 0.37},
    "framing_ok": ["S20"],
    "phonemes": {},
    "asr_ignore_tail_repeat": True,
    "homophones": {"1058": "tenfiftyeight", "1059": "tenfiftynine", "arms": "arm", "i": "ive"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
    "staging_ok": ["S16/mom+me_b", "S17/mom+me_b", "S19c/mom+me_b", "S26a/mom+me_b", "S26b/mom+me_b"],
    "frames_ok": [],
}
if rain:
    story["rain_shots"] = rain
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
