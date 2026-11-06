"""Writes ../story.json for ep129 "Dad Won't Open My PRESENT" (script.md, batch 14). Run:
    python stories/ep129-gift-box/generator/make_story.py

The words are in lines.json (the script's own slash chunks; captions are split to three words here and the
references remapped). Places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +y is 180.

Batch 14: no light change, no set move. Every state of the box is its own stage (set.py), so a shot just points the
camera at the stage it needs, and the acting keys put the people there. People are placed afresh at the start of each
shot (a jump between two stages is two keys at the same time, which makes no footsteps). Nothing blinks.
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
REV = 6
D2R = math.pi / 180

orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = timeline.split_lines(orig_lines)


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


# ---------------------------------------------------------------------------------------------- the cast
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


SKIN = "#d9a066"
cast = {
    # me, 30: short brown curly hair, warm tan skin, a green hoodie over a white T-shirt (the collar), jeans
    "me": person(SKIN, "#3e9a5a", "#4a5a8a", "#6a4a30", hair="mop", hair_c="#4a2f1c", collar="#ffffff", brow_w=1.4),
    # me at eighteen: the same face, a gray hoodie, a backpack with a strap over one shoulder
    "young": person(SKIN, "#8a8f99", "#4a5a8a", "#2a2a40", hair="swoop", hair_c="#4a2f1c", collar="#ffffff", brow_w=1.4,
                    extras=["backpack"], extra_c="#c0562c", strap="#c0562c"),
    # Dad (Gene), 60: gray hair combed back, a gray goatee, a light blue short-sleeved button shirt, khakis
    "dad": person(SKIN, "#a9cdea", "#c9b48a", "#6a4a30", hair="cap", hair_c="#b8b8c0", collar="#e8f0f8", sleeves="short",
                  goatee="#a8a8b0", brow_w=1.2),
    # Dad at 48: dark hair, no goatee, the same shirt
    "dad48": person(SKIN, "#a9cdea", "#c9b48a", "#6a4a30", hair="cap", hair_c="#4a3a2c", collar="#e8f0f8", sleeves="short",
                    brow_w=1.2),
    # Mrs. Albee: a silver bun, round glasses, a red cardigan
    "albee": person("#f0c8a0", "#c0392b", "#6a5a8a", "#6a4a30", hair="bun", hair_c="#c9c9d3", pattern="knit",
                    pattern_c="#e8604a", eyes="lashes", extras=["glasses"], extra_c="#8a2a22"),
    # Sam: a backward blue cap, a yellow T-shirt
    "sam": person("#b9794a", "#f5d442", "#4a5a7a", "#2a2a40", hair="none", hair_c="#2a1d15", sleeves="short",
                  backcap="#2f6fd6"),
    # the post office man: a navy vest over a pale shirt
    "postman": person("#e8b890", "#27386e", "#3a3a4a", "#2a2a40", hair="buzz", hair_c="#6a5a4a", sleeves="short"),
}
CAST = list(cast)
acting = {n: [] for n in cast}
cues = []
SH = []
last = {}      # who -> {"pos": [...], "hidden": bool}

EXPR = {"neutral": "neutral", "uneasy": "worried", "scared": "scared", "stunned": "wide", "sad": "worried",
        "smile": "smile", "laugh": "laugh", "warm": "warm", "proud": "smile", "angry": "angry", "sheepish": "sad-smile",
        "listen": "soft"}


def put(who, at, st, x, y, z=0.0, yaw=0.0, expr="neutral", arms=(0, 0), side=(0, 0), head=(0, 0), lean=0.0,
        look=(0, 0), seat=False, blend=0.0):
    pos = [round(G.ST[st] + x, 3), y, round(z - (G.SEAT if seat else 0.0), 3)]
    prev = last.get(who)
    if prev and prev["pos"] != pos:
        acting[who].append({"at": at, "pos": list(prev["pos"])})   # stand where we were, then jump (same time: no steps)
    acting[who].append({"at": at, "pos": pos, "yaw": yaw, "arms": list(arms), "side": list(side), "head": list(head),
                        "lean": lean, "expr": EXPR.get(expr, expr), "look": list(look), "hidden": False, "blink": False,
                        "blend": blend})
    last[who] = {"pos": pos, "hidden": False}


def hide(who, at):
    prev = last.get(who)
    if prev is None:
        acting[who].append({"at": 0, "pos": [0.0, -50.0, 0.0], "hidden": True, "blend": 0.0})
        last[who] = {"pos": [0.0, -50.0, 0.0], "hidden": True}
    elif not prev["hidden"]:
        acting[who].append({"at": at, "hidden": True})
        prev["hidden"] = True


def chg(who, at, blend=0.25, **kw):
    """A change inside a shot (expression, head, arms), eased over `blend`; the position stays."""
    k = {"at": at, "blend": blend}
    for a, b in kw.items():
        k[a] = EXPR.get(b, b) if a == "expr" else (list(b) if isinstance(b, tuple) else b)
    acting[who].append(k)


def talk(who, a, b, m=0.4):
    acting[who].append({"from": a, "to": b, "mouth": [m, m], "flap": True})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


# ---------------------------------------------------------------------------------------------- cameras
def cam(tx, ty, tz, d, lens, az=0.0, el=0.0, push=0.07, arc=2.5, to=None):
    """A camera d metres from the target at azimuth az (0 = south of it looking north, 180 = north of it) and
    elevation el, pushing in by `push` while it slides `arc` degrees round."""
    def at(dd, a):
        a, e = a * D2R, el * D2R
        return [round(tx + dd * math.sin(a) * math.cos(e), 3), round(ty - dd * math.cos(a) * math.cos(e), 3),
                round(tz + dd * math.sin(e), 3)]
    tgt = [tx, ty, tz]
    t1 = list(to) if to else tgt
    push, arc = push * 3.0, arc * 5.5   # batch 14 pace: a livelier camera on every shot
    return [[0, at(d, az), tgt, lens], [1, at(d * (1 - push), az + arc), t1, lens]]


def hz(d, lens):
    return 24.0 * d / lens


def fcam(st, x, y, z=0.0, d=3.0, lens=30, f=0.38, dx=0.0, dz=0.0, **kw):
    """Aim so that a head at (x, y, 1.57 + z) sits f of the way down the frame."""
    h = 1.57 + z
    return cam(G.ST[st] + x + dx, y, h - (0.5 - f) * hz(d, lens) + dz, d, lens, **kw)


def ocam(st, x, y, z, d, lens, **kw):
    return cam(G.ST[st] + x, y, z, d, lens, **kw)


def shot(id_, at, camera, who=None, hand=0.03, step=2):
    who = who or {}
    for n in CAST:
        if n in who:
            put(n, at, **who[n])
        else:
            hide(n, at)
    SH.append((at, camera, step, hand, id_))


# local shorthands for people
DX, DY = 0.0, G.STAND_Y          # kitchen: behind the island


def ps(st, x, y, **kw):
    return dict(st=st, x=x, y=y, **kw)


HOLD_ARMS = dict(arms=(66, 66), side=(-20, -20))
BOX_ARMS = dict(arms=(52, 52), side=(-20, -20))
SIT = dict(seat=True, arms=(18, 18), side=(4, 4))

# ============================================================================================ 01 the rule
ME0 = (1.05, 1.95)
ME1 = (0.6, 1.95)
shot("S01a", 0, fcam("R1", *ME1, d=3.9, lens=30, dx=-0.3, f=0.40), {
    "me": ps("R1", *ME1, expr="neutral", head=(-22, 0), look=(-0.5, 0))})
shot("S01b", "L01.2", fcam("R1", *ME1, d=2.8, lens=30, dx=-0.1, f=0.40, push=0.08, to=[0.2, 1.95, 1.346]), {
    "me": ps("R1", *ME1, expr="neutral", head=(-20, 0), look=(-0.5, 0))})
shot("S02", "L02", fcam("R1", *ME1, d=3.6, lens=30, dx=-0.3, f=0.40, az=-4), {
    "me": ps("R1", *ME1, expr="neutral", arms=(8, 8), side=(14, 14), head=(0, 3))})

# ============================================================================================ 02 the rule at work
ALB = (0.0, 1.5)
shot("S03", "L03", fcam("MA", *ALB, d=3.1, lens=30, f=0.31, push=0.06), {
    "albee": ps("MA", *ALB, expr="smile", **HOLD_ARMS)})
shot("S04", "L04", fcam("MA", *ALB, d=3.0, lens=30, f=0.31, az=4, push=0.06), {
    "albee": ps("MA", *ALB, expr="laugh", **HOLD_ARMS)})
chg("albee", "L04.0+0.4", blend=0.12, arms=(60, 60))
chg("albee", "L04.1", blend=0.12, arms=(70, 70))
SAM = (0.0, 2.45)
shot("S05", "L05", fcam("MS", *SAM, z=-G.SEAT, d=3.1, lens=30, f=0.40, dx=0.25), {
    "sam": ps("MS", *SAM, expr="smile", seat=True, arms=(72, 72), side=(-14, -14))})
shot("S06", "L06", fcam("MS", *SAM, z=-G.SEAT, d=3.1, lens=30, f=0.40, dx=0.25, az=-4, push=0.06), {
    "sam": ps("MS", *SAM, expr="proud", seat=True, arms=(72, 72), side=(-14, -14))})
shot("S07a", "L07", ocam("MS", 0.45, 1.6, 0.98, 1.6, 34, az=6, el=12, push=0.06), {})
shot("S07b", "L07.1", fcam("MS", *SAM, z=-G.SEAT, d=3.1, lens=30, f=0.40, dx=0.25, az=-3, push=0.06), {
    "sam": ps("MS", *SAM, expr="laugh", seat=True, arms=(72, 72), side=(-14, -14))})
PM = (0.1, 1.9)
shot("S08", "L08", fcam("MP", *PM, d=4.4, lens=30, f=0.36, dx=0.33), {
    "postman": ps("MP", *PM, expr="smile", arms=(8, 8))})
shot("S09", "L09", ocam("MP", 0.8, 1.5, 0.2, 2.0, 34, az=20, el=30, push=0.08), {})
ME_STEP = (-2.3, 6.0)
shot("S10", "L10", fcam("R1", ME_STEP[0], ME_STEP[1], z=-0.36, d=3.4, lens=30, f=0.40, push=0.06), {
    "me": ps("R1", *ME_STEP, z=-0.36, yaw=0, expr="smile")})

# ============================================================================================ 03 the present on the mantel
shot("S11", "L11", ocam("R1", 0.0, 1.9, 1.45, 5.3, 24, el=2, push=0.06), {})
shot("S12", "L12", ocam("R1", 0.0, 2.55, 1.62, 1.8, 30, az=-6, push=0.1), {})
YG = (-2.3, 2.62)
shot("S13", "L13", fcam("R1", *YG, d=3.0, lens=30, f=0.40), {
    "young": ps("R1", *YG, expr="uneasy", head=(0, 2))})
shot("S14", "L14", fcam("R1", *YG, d=2.7, lens=30, f=0.40, az=3, push=0.08), {
    "young": ps("R1", *YG, expr="angry", head=(0, 3))})
D48 = (-0.55, 1.9)
shot("S15", "L15", fcam("R1", *D48, d=3.2, lens=30, f=0.40, dx=0.3), {
    "dad48": ps("R1", *D48, expr="neutral", arms=(20, 20), side=(8, 8))})
shot("S16", "L16", ocam("KA", 0.1, 1.1, 1.1, 3.2, 30, az=0, el=22, push=0.08), {})
YK = (0.6, G.STAND_Y)
shot("S17", "L17", fcam("KA", *YK, d=2.9, lens=30, f=0.40, dx=-0.4), {
    "young": ps("KA", *YK, expr="angry", head=(0, 2))})
chg("young", "L17.2", blend=0.4, expr="sad", head=(0, 10))
shot("S18", "L18", ocam("R1", 0.0, 2.55, 1.62, 1.9, 30, az=4, push=0.08), {})

# ============================================================================================ 04 twelve stiff years
MED = (-2.3, 2.62)
shot("S19", "L19", fcam("R1", *MED, d=3.0, lens=30, f=0.40), {
    "me": ps("R1", *MED, expr="neutral")})
shot("S20", "L20", fcam("R1", *G.DAD_SEAT, z=0.0, d=3.5, lens=30, f=0.38, dx=0.3, push=0.07), {
    "dad": ps("R1", *G.DAD_SEAT, expr="neutral", **SIT)})
chg("dad", "L20.1", blend=0.4, head=(0, 8))
chg("dad", "L20.1+0.5", blend=0.4, head=(0, -2))
D21, M21 = (-0.35, 1.25), (0.55, 1.25)
shot("S21", "L21", ocam("R1", 0.05, 1.6, 1.4, 3.5, 30, push=0.03, arc=0.6), {
    "dad": ps("R1", *D21, expr="neutral", **SIT),
    "me": ps("R1", *M21, expr="neutral", **SIT)})
shot("S22", "L22", fcam("R1", *G.ME_SEAT, d=3.3, lens=30, f=0.38, dx=-0.25, push=0.07), {
    "me": ps("R1", *G.ME_SEAT, expr="listen", **SIT)})
shot("S23a", "L23", fcam("R1", -0.85, 1.9, d=3.6, lens=30, f=0.38, dx=0.3), {
    "dad": ps("R1", -0.85, 1.9, expr="smile", arms=(8, 8))})
talk("dad", "L23.1", "L23>")
shot("S23b", "L23.1", fcam("R1", -0.85, 1.9, d=2.7, lens=30, f=0.38, dx=0.3, push=0.06), {
    "dad": ps("R1", -0.85, 1.9, expr="smile", arms=(8, 8))})
DAD_MANTEL = (-0.1, 1.72)
FLAT = dict(arms=(84, 84), side=(-8, -8))
shot("S24", "L24", fcam("R1", *DAD_MANTEL, d=3.6, lens=30, f=0.40, az=30, dx=0.26), {
    "dad": ps("R1", *DAD_MANTEL, expr="warm", head=(10, 0), **FLAT)})
shot("S25", "L25", ocam("R1", -0.05, 2.55, 1.7, 2.4, 30, az=50, push=0.08, arc=-3), {})

# ============================================================================================ 05 the scare
HOLDER = G.HOLD
shot("S26", "L26", fcam("R2", *HOLDER, d=3.3, lens=30, f=0.40, el=4), {
    "me": ps("R2", *HOLDER, expr="uneasy", **BOX_ARMS)})
shot("S27", "L27", fcam("R2", *HOLDER, d=2.9, lens=30, f=0.40, el=5, az=3, push=0.08), {
    "me": ps("R2", *HOLDER, expr="stunned", **BOX_ARMS)})
shot("S28", "L28", fcam("R2", *HOLDER, d=2.9, lens=30, f=0.40, az=-4, el=6, push=0.08), {
    "me": ps("R2", *HOLDER, expr="uneasy", arms=(60, 60), side=(-22, -22), lean=4, head=(0, 6))})
chg("me", "L28.1", blend=0.5, lean=8, head=(0, 10))
shot("S29", "L29", fcam("R2", *HOLDER, d=2.7, lens=28, f=0.40, el=8, push=0.06), {
    "me": ps("R2", *HOLDER, expr="uneasy", **BOX_ARMS)})
shot("S30a", "L30", fcam("R2", *HOLDER, d=2.9, lens=30, f=0.40, el=5, az=-3, push=0.07), {
    "me": ps("R2", *HOLDER, expr="scared", **BOX_ARMS)})
shot("S30b", "L30.2", fcam("R2", *HOLDER, d=2.7, lens=28, f=0.40, el=7, az=-8, push=0.07), {
    "me": ps("R2", *HOLDER, expr="scared", **BOX_ARMS)})
shot("S31", "L31", ocam("R1", -2.3, 6.2, 0.1, 6.0, 24, az=180, el=3, push=0.06), {})
shot("S32", "L32", fcam("R3", -0.45, 1.95, d=3.4, lens=30, f=0.40, dx=0.25), {
    "me": ps("R3", -0.45, 1.95, expr="scared", arms=(30, 30), side=(-6, -6), head=(14, 0))})

# ============================================================================================ 06 thanksgiving
DAD_HANDS = (-0.12, 1.72)
shot("S33", "L33", fcam("R3", *DAD_HANDS, d=3.6, lens=30, f=0.40, az=30, dx=0.26), {
    "dad": ps("R3", *DAD_HANDS, expr="smile", head=(10, 0), **FLAT)})
shot("S34", "L34", ocam("R3", -0.05, 2.1, 1.38, 2.4, 30, az=-10, el=4, push=0.08), {
    "dad": ps("R3", *DAD_HANDS, expr="warm", head=(8, 6), **FLAT)})
MN = (1.5, 1.25)
shot("S35", "L35", fcam("R3N", *MN, z=-G.SEAT, d=4.4, lens=30, f=0.40, dx=0.42, push=0.05), {
    "me": ps("R3N", *MN, expr="scared", seat=True, arms=(70, 70), side=(-30, -30))})
shot("S36", "L36", ocam("R3N", 0.25, 2.55, 1.55, 3.2, 30, az=-72, push=0.06, arc=-2), {})
shot("S37", "L37", fcam("KB", 0.0, G.STAND_Y, d=3.2, lens=30, f=0.40), {
    "dad": ps("KB", 0.0, G.STAND_Y, expr="smile", arms=(40, 40), side=(-6, -6))})
chg("dad", "L37.1", blend=0.4, head=(0, 6))
shot("S38", "L38", fcam("KB", 0.0, G.STAND_Y, d=2.8, lens=30, f=0.40, az=3, push=0.07), {
    "dad": ps("KB", 0.0, G.STAND_Y, expr="warm", arms=(40, 40), side=(-6, -6))})
talk("dad", "L38.1", "L38>")
shot("S38b", "P01", ocam("R6", 0.0, 0.6, 1.3, 4.4, 22, el=3, push=0.05), {})

# ============================================================================================ 07 the party
shot("S39", "L39", fcam("R3", -2.3, 5.0, d=3.0, lens=28, f=0.42, push=0.06), {
    "dad": ps("R3", -2.3, 5.0, yaw=0, expr="smile", arms=(6, 6))})
ME_WIN = (1.85, 1.95)
shot("S40", "L40", fcam("R3", *ME_WIN, d=3.2, lens=30, f=0.40, dx=0.15), {
    "me": ps("R3", *ME_WIN, expr="sheepish", head=(0, 0))})
shot("S41", "L41", fcam("R3", *ME_WIN, d=2.8, lens=30, f=0.40, dx=0.1, az=3, push=0.08), {
    "me": ps("R3", *ME_WIN, expr="smile")})
shot("S42", "L42", fcam("R3", *ME_WIN, d=2.5, lens=30, f=0.40, dx=0.1, az=-3, push=0.08), {
    "me": ps("R3", *ME_WIN, expr="uneasy", head=(0, 4))})
DAD_WIN = (0.85, 1.9)
shot("S43a", "L43", fcam("R3", *DAD_WIN, d=3.2, lens=30, f=0.40, dx=-0.2), {
    "dad": ps("R3", *DAD_WIN, expr="stunned", look=(0.9, 0), head=(-20, 0))})
shot("S43b", "L43.1", fcam("R3", *DAD_WIN, d=2.7, lens=30, f=0.40, dx=-0.12, az=3, push=0.08), {
    "dad": ps("R3", *DAD_WIN, expr="neutral", head=(0, 0))})
chg("dad", "L43.1", blend=0.4, head=(0, 0), look=(0, 0))

# ============================================================================================ 08 the opening
shot("S44", "L44", fcam("R2", *HOLDER, d=3.3, lens=30, f=0.40, el=4), {
    "dad": ps("R2", *HOLDER, expr="neutral", **BOX_ARMS)})
shot("S45", "L45", fcam("R2", *HOLDER, d=2.9, lens=30, f=0.40, el=5, az=3, push=0.08), {
    "dad": ps("R2", *HOLDER, expr="warm", **BOX_ARMS)})
talk("dad", "L45.1", "L45>")
chg("dad", "L45.1", blend=0.3, head=(0, 8))
ME_B = (0.9, 1.95)
shot("S46", "L46", fcam("R6", *ME_B, d=3.4, lens=30, f=0.40, dx=-0.35), {
    "me": ps("R6", *ME_B, expr="scared", head=(0, 2))})
shot("S47", "L47", fcam("R6", *ME_B, d=3.2, lens=30, f=0.40, dx=0.0, az=-3, push=0.09), {
    "me": ps("R6", *ME_B, expr="sad", head=(0, 8))})
shot("S48", "L48", ocam("KC", 0.0, 1.1, 1.2, 1.6, 30, az=0, el=22, push=0.08), {})
shot("S49", "L49", ocam("KD", 0.0, 1.1, 1.3, 1.5, 30, az=-6, el=34, push=0.08), {})
shot("S50", "L50", ocam("KE", 0.0, 1.1, 1.0, 1.4, 30, az=0, el=70, push=0.06), {})
shot("S51", "L51", fcam("KF", 0.0, G.STAND_Y, d=3.2, lens=30, f=0.40, el=24, push=0.07), {
    "dad": ps("KF", 0.0, G.STAND_Y, expr="warm", head=(0, 6), **HOLD_ARMS)})
shot("S52", "L52", fcam("R6", *ME_B, d=3.0, lens=30, f=0.40, dx=-0.3), {
    "me": ps("R6", *ME_B, expr="stunned")})

# ============================================================================================ 09 the reveal
shot("S53", "L53", ocam("R6", 0.0, 1.9, 1.45, 4.6, 26, el=3, push=0.06), {})
shot("S54", "L54", fcam("R6", -0.7, 1.9, d=3.2, lens=30, f=0.40, dx=0.15), {
    "dad": ps("R6", -0.7, 1.9, expr="warm", head=(0, 3))})
shot("S55", "L55", ocam("R1", -2.3, 5.2, 0.55, 4.2, 30, az=180, el=-2, push=0.07), {
    "me": ps("R1", -2.3, 5.4, z=-0.18, yaw=0, expr="neutral")})
shot("S56", "L56", fcam("KF", 0.0, G.STAND_Y, d=3.2, lens=30, f=0.40, el=24, push=0.05), {
    "dad": ps("KF", 0.0, G.STAND_Y, expr="warm", head=(24, 0), look=(-0.7, 0), **HOLD_ARMS)})

# ============================================================================================ 10 the warm turn
shot("S57", "L57", fcam("KF", 0.0, G.STAND_Y, d=3.2, lens=30, f=0.40, el=24, az=3, push=0.07), {
    "dad": ps("KF", 0.0, G.STAND_Y, expr="laugh", head=(0, 8), **HOLD_ARMS)})
shot("S58", "L58", fcam("KF", 0.0, G.STAND_Y, d=3.2, lens=30, f=0.40, el=24, az=-3, push=0.07), {
    "dad": ps("KF", 0.0, G.STAND_Y, expr="warm", **HOLD_ARMS)})
talk("dad", "L58.1", "L58>")
DAD_SET = (-0.55, 1.7)
shot("S59", "L59", fcam("R4", *DAD_SET, d=3.2, lens=30, f=0.40, dx=0.2), {
    "dad": ps("R4", *DAD_SET, expr="warm", arms=(8, 80), side=(0, -6), head=(0, 4))})
shot("S60", "L60", ocam("R4", -0.62, 2.55, 1.3, 1.8, 30, az=40, el=18, push=0.08, arc=-3), {})
SIDE_L, SIDE_R = (-0.55, G.STAND_Y), (0.55, G.STAND_Y)
CAKE_ARMS = dict(arms=(48, 48), side=(-6, -6))
shot("S61", "L61", ocam("KG", -0.12, 1.85, 0.85, 4.0, 30, el=9, push=0.04), {
    "me": ps("KG", *SIDE_L, expr="smile", **CAKE_ARMS), "dad": ps("KG", *SIDE_R, expr="smile", **CAKE_ARMS)})
shot("S62", "L62", fcam("KG", *SIDE_L, d=2.9, lens=30, f=0.40, dx=0.2), {
    "me": ps("KG", *SIDE_L, expr="laugh", **CAKE_ARMS)})
shot("S63", "L63", fcam("KG", *SIDE_R, d=2.9, lens=30, f=0.40, dx=-0.2, az=3), {
    "dad": ps("KG", *SIDE_R, expr="laugh", **CAKE_ARMS)})
shot("S64", "L64", fcam("KG", *SIDE_L, d=2.6, lens=30, f=0.40, dx=0.2, az=-3, push=0.08), {
    "me": ps("KG", *SIDE_L, expr="laugh", **CAKE_ARMS)})
NIGHT_ARMS = dict(arms=(50, 50), side=(-12, -12))
shot("S65", "L65", ocam("KH", -0.55, 1.5, 1.1, 4.0, 30, el=8, push=0.05), {
    "me": ps("KH", -0.4, G.STAND_Y, expr="warm", **NIGHT_ARMS)})
shot("S66", "L66", fcam("KH", -0.4, G.STAND_Y, d=3.0, lens=30, f=0.40, dx=-0.1, az=-3), {
    "me": ps("KH", -0.4, G.STAND_Y, expr="warm", **NIGHT_ARMS)})
shot("S67", "L67", fcam("R5", *ME0, d=3.9, lens=30, f=0.40, dx=-0.2, push=0.08), {
    "me": ps("R5", *ME0, expr="warm", head=(-22, 0), look=(-0.5, 0))})

# the pause beat (the drop): nobody speaks, the front room is empty
# ---------------------------------------------------------------------------------------------- finish
shots, names = [], {}
for i, (at, camera, step, hand, nm) in enumerate(SH):
    s = {"id": nm, "cam": camera, "step": step, "hand": hand}
    if i:
        s["at"] = remap(at)
    shots.append(s)

# the narration with the pause beat after L38
lines_out = []
for ln in lines:
    lines_out.append(ln)
    if ln["id"] == "L38":
        lines_out.append({"id": "P01", "pause": 0.6, "chunks": [["", ""]]})

# order every acting list by time (the keys were written shot by shot, but chg() keys were written after their shot)
for items in (acting.values(), [cues]):
    for lst in items:
        remap_all(lst)

sfx = [
    {"at": "L01.2", "kind": "thud", "db": -14, "dur": 0.4},                                    # the box's soft thump on HOPE
    {"at": "L04.1", "kind": "ding", "db": -20, "dur": 0.8, "pitch": 150, "fall": 0.5, "lp": 700},   # a faint tuba-ish blat
    {"at": "L07.1", "kind": "ding", "db": -20, "dur": 0.35, "pitch": 210, "fall": 0.45, "lp": 900},  # one muffled woof
    {"at": "L29.1", "kind": "knock", "db": -17, "pattern": [0.0, 0.65], "tone": "below"},      # slow steps in the box
    {"at": "L30.2", "kind": "knock", "db": -17, "pattern": [0.0, 0.7], "tone": "below"},
    {"at": "L32.2", "kind": "thud", "db": -13, "dur": 0.4},                                    # set down hard
    {"at": "L36", "kind": "knock", "db": -15, "pattern": [0.0, 0.5, 1.0], "tone": "soft"},   # three soft knocks
    {"at": "L12.1", "kind": "thud", "db": -18, "dur": 0.4},
    {"at": "L49", "kind": "creak", "db": -18, "dur": 0.9, "tone": "cardboard"},
    {"at": "L55", "kind": "knock", "db": -17, "pattern": [0.0, 0.5], "tone": "soft"},
    {"at": "L40", "kind": "thud", "db": -19, "dur": 0.4},
    {"at": "L48.1", "kind": "creak", "db": -16, "dur": 1.5, "tone": "cardboard"},            # paper coming off, slow
]
for s_ in sfx:
    s_["at"] = remap(s_["at"])
music = {
    "root": 55, "mode": "major", "bpm": 88, "seed": 129,
    "sections": [
        {"at": 0, "voices": ["pluck", "pad"], "energy": 0.4, "mode": "major", "root": 55},
        {"at": "L11", "voices": ["piano", "pad"], "energy": 0.3, "mode": "minor", "root": 52},
        {"at": "L26", "voices": ["piano", "pad", "pulse"], "energy": 0.4, "mode": "minor", "root": 52},
        {"at": "L50", "voices": ["drone", "pad"], "energy": 0.2, "mode": "minor", "root": 52},
        {"at": "L53", "voices": ["pluck", "pad"], "energy": 0.3, "mode": "major", "root": 55},
        {"at": "L57", "voices": ["pluck", "pad", "piano"], "energy": 0.5, "mode": "major", "root": 55},
    ],
}
for sec in music["sections"]:
    sec["at"] = remap(sec["at"])
sound = {
    "floor": "wood", "steps_db": -26,
    "ambience": [{"kind": "room", "from": 0, "to": "end", "lufs": -44}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
polish = {"emph": [remap(r) for r in ("L01.2", "L12.1", "L25.2", "L28.1", "L29.1", "L50", "L56.3")],
          "reveal": ["L50", "L56"], "twist": "L50", "camera": False,
          "hold": ["S11", "S21", "S61", "S53"], "quiet": [["L65", "L67"]], "reframe_every": 0.7, "sway_amp": 0.012,
          "sway": True, "whoosh_cuts": False}
story = {
    "slug": "ep129-gift-box",
    "title": "Dad Won't Open My PRESENT \U0001F381",
    "made_for_kids": False,
    "premise": ("In our town a wrapped present is whatever you hope it is until it is opened, so nobody opens anything. "
                "My dad has kept one box wrapped on his mantel for twelve years, and it has grown heavy enough that "
                "something inside it walks."),
    "twist": ("I gave Dad an empty box when I moved out at eighteen. For twelve years it held the one thing he hoped for, me "
              "coming home, so when he finally opens it, it is empty because what he hoped for is standing in his doorway."),
    "world": ("A sunny small-town house: butter yellow walls, a white mantel with a round numberless clock, a blue armchair, "
              "a porch with five white steps and a blue rail, a mint kitchen, and the neighbours' porches."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffc94a",
    "gap": 0.15,
    "tail": 0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#dff0ff", "fog_density": 0.002, "fog_start": 60.0, "sky": "#8fd0ff",
             "sky_strength": 1.0, "exposure": 0.2, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.06, "contrast": 1.04,
              "vignette": 0.15, "bloom": 0.08, "grain": 0.006},
    "phonemes": {"Albee": "ˈælbi"},
    "cast": cast,
    "lines": lines_out,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
}
story["framing_ok"] = []
story["asr_forgive"] = ["mantel", "we'd", "that"]
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
