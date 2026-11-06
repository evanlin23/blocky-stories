"""Writes ../story.json for "My Best Friend Countdown Ended 11 YEARS Ago" (ep130-rival-clock, batch 14).
Run: python stories/ep130-rival-clock/generator/make_story.py

The words are in lines.json (the script's narration). Places are in ../layout.py (shared with set.py). A character
facing -y has yaw 0 (toward the camera). Time references use the script's own chunk numbers (L24.1 is the second
slash-chunk of L24): timeline.split_lines cuts long captions to two or three words and the references are remapped.

One steady, sunny world: the sun, the sky and every light are the same strength in every frame. Cuff numerals change only
at a cut (cue "gus"). No set moves.
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE.parent))
import layout as G  # noqa: E402
from blocky import timeline as T  # noqa: E402

OUT = HERE.parent / "story.json"
REV = 6
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = T.split_lines(orig_lines)
for _l in lines:       # L11 and L38: the splitter cut "He looked / at me" and left "at me" up for under 0.2 s; keep every caption at 3 words or fewer and 0.2 s or more
    if _l["id"] == "L11":
        _l["chunks"] = [["He yelled", "he yelled"], ["at me about", "at me about"], ["the HOSES.", "the hoses."]]
        CHUNKMAP["L11"] = [0, 2]
    if _l["id"] == "L38":
        CHUNKMAP["L38"] = [0, 2, 3]
        _l["chunks"] = [["He looked", "he looked"], ["at me like", "at me like"], ["I'd grown", "I'd grown"], ["a second HEAD.", "a second head."]]
idx = next(i for i, l in enumerate(lines) if l["id"] == "L29")
lines.insert(idx, {"id": "P01", "pause": 0.5, "chunks": [["", ""]]})     # the 0.5 s music drop before L29


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


SX = G.SX
BX, BY = G.BUS
YX, YY = G.YARD
WX, WY = G.WALK
DX, DY = G.BED


# ---------------------------------------------------------------------------------------------------- cast
def person(skin, shirt, pants, shoes, hair="cap", hair_c="#15110e", extras=(), eyes="round", sleeves="short", height=1.0,
           width=1.0, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": shoes, "sleeves": sleeves,
         "hair": hair, "hair_c": hair_c, "hat": "none", "face": {"eyes": eyes, "brows": True, "ink": "#24131f"}}
    if extras:
        d["extras"] = list(extras)
    if height != 1.0:
        d["height"] = height
    if width != 1.0:
        d["width"] = width
    d.update(kw)
    return d


APRON = "#2f8a52"
cast = {
    "me": person("#a9744f", "#8d939e", "#3b4a6b", "#2a2a2e", extras=["apron"], extra_c=APRON),
    "me_young": person("#a9744f", "#5aa0e8", "#3b4a6b", "#2a2a2e"),
    "gus": person("#d6945c", "#c63a32", "#5a4a3a", "#3a2c24", hair="none", extras=["apron"], extra_c=APRON, height=1.04,
                  width=1.1, pattern="plaid", pattern_c="#1a1a1a"),
    "stranger_a": person("#f1c9a0", "#ffd23f", "#6b4a2a", "#f6f6f6", hair="bun", hair_c="#3a2418", eyes="lashes", body_width=0.8),
    "stranger_b": person("#c58a5c", "#e0643a", "#3a3a4a", "#f6f6f6", hair="cap", hair_c="#241a16", body_width=0.8),
    "mom": person("#f1c9a0", "#d9487a", "#4a4a6a", "#f4f4f2", hair="bun", hair_c="#c9ccd2", eyes="lashes", body_width=0.8),
    "rita": person("#8a5a3a", "#2fa8a0", "#6b4a2a", "#f4f4f2", hair="long", hair_c="#15110e", eyes="lashes", body_width=0.8),
    "walker": person("#d9a86a", "#2b6fd8", "#2b6fd8", "#f6f6f6", hair="buzz", hair_c="#241a16", pattern="stripes",
                     pattern_c="#ffffff"),
}
H_OF = {n: c.get("height", 1.0) for n, c in cast.items()}
acting = {n: [] for n in cast}
last = {n: None for n in cast}
cues = []
SH = []
FAR = [0.0, -600.0, 0.0]


def TP(who, at, pos, yaw=0.0, expr="neutral", **kw):
    """The character is there from this instant (a cut); everything it doesn't set goes back to neutral."""
    if last[who] is not None:
        acting[who].append({"at": at, "pos": list(last[who]), "blend": 0.0})
    st = {"hidden": False, "arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0}
    st.update(kw)
    acting[who].append({"at": at, "pos": list(pos), "blend": 0.0, "yaw": yaw, "expr": expr, **st})
    last[who] = list(pos)


def K(who, at, pos=None, **kw):
    p = list(pos) if pos is not None else list(last[who])
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def HIDE(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0.0})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def gus_state(at, sleeve="buttoned", n=None):
    cue(at, "gus", sleeve=sleeve, n=n)


def props(at, on=()):
    cue(at, "props", on=list(on))


# ---------------------------------------------------------------------------------------------------- cameras
def sub(x, y, H=2.9, tz=1.62, off=8.0, lens=34, sh=0.0, up=0.0, pf=0.16):
    """A camera in front of a subject at (x, y): the frame is H metres tall at the subject, looking at height tz, `off`
    degrees round, the subject `sh` metres right of centre (positive moves it right on screen)."""
    d = H * lens / 24.0
    a = math.radians(off)
    cam = [round(x + d * math.sin(a) + 0.0, 3), round(y - d * math.cos(a), 3), round(tz + up, 3)]
    tgt = [round(x - sh * math.cos(a), 3), round(y - sh * math.sin(a) * 0.0, 3), round(tz, 3)]
    k = [0, cam, tgt, lens]
    p2 = [round(a + (b - a) * pf, 3) for a, b in zip(cam, tgt)]
    return [k, [1, p2, tgt, lens]]


def look_at(cam, tgt, lens):
    return [[0, [round(v, 3) for v in cam], [round(v, 3) for v in tgt], lens]]


def ins(center, dist=2.1, elev=52.0, lens=40, off=0.0, dz=0.0):
    """An insert on a forearm lying flat: the camera in front and above, looking down at it."""
    e, a = math.radians(elev), math.radians(off)
    cam = [center[0] + dist * math.cos(e) * math.sin(a), center[1] - dist * math.cos(e) * math.cos(a), center[2] + dist * math.sin(e)]
    return look_at(cam, [center[0], center[1], center[2] + dz], lens)


def cc(arm, s=1.0, p=35.0):
    """The middle of a tilted cuff prop's numerals (see set.arm_prop pitch)."""
    r = math.radians(p)
    return (arm[0] + 0.05 * s, arm[1] - 0.35 * s * math.sin(r), arm[2] + 0.165 * s * math.sin(r) + 0.35 * s * math.cos(r))


def push(cam, f=0.1):
    k = cam[0]
    p2 = [round(a + (b - a) * f, 3) for a, b in zip(k[1], k[2])]
    return [k, [1, p2, k[2], k[3]]]


def shot(at, camera, name, **kw):
    SH.append((at, camera, name, kw))


# a character facing the camera at a station
def at_(who, at, x, y, expr="neutral", z=0.0, **kw):
    TP(who, at, [x, y, z], 0.0, expr, **kw)


SIT = -0.23
BENCH_CX = SX["bench"]
ARM_BENCH = G.BENCH_ARM
ARM_RIM = G.RIM_ARM
ARM_TABLE = G.TABLE_ARM
TBX = SX["table"]
TNK = SX["tank"]
HSX = SX["hose"]
TOM = SX["tom"]
RAD = SX["radio"]

for w_ in cast:
    TP(w_, 0, FAR, 0, hidden=True)

# ===== L01 the hook: my face, my forearm on the bench in the lower third with the 0
ME_BENCH = [BENCH_CX + 0.2, 1.7]
CAMY = 1.15
gus_state(0, "buttoned", None)
props(0, ["barm"])
at_("me", 0, *ME_BENCH, expr="neutral")
shot(0, push(sub(ME_BENCH[0], CAMY, H=1.95, tz=1.02, off=6, sh=-0.05, up=0.8), 0.05), "hook")
shot("L01.1", ins(cc(ARM_BENCH, 1.35, 30), dist=1.3, elev=72, lens=40, dz=-0.05), "hookcuff")
# ===== L02
ME_SIDE = [BENCH_CX - 1.95, 0.45]
props("L02", [])
at_("me", "L02", *ME_SIDE, expr="smile")
shot("L02", sub(ME_SIDE[0], ME_SIDE[1], H=2.9, tz=1.6, off=-10), "here")
# ===== L03 three forearms on a bus rail (a stack), 3 cuffs, 3 numbers
HIDE("me", "L03")
shot("L03", look_at([BX + 2.4, BY - 3.1, 2.5], [BX + 2.4, BY - 1.0, 0.62], 24), "threearms")
# ===== L04 two strangers on the bus
SA, SB = [BX - 0.54, BY + 1.1], [BX + 0.54, BY + 1.1]
at_("stranger_a", "L04", *SA, expr="laugh", z=SIT)
at_("stranger_b", "L04", *SB, expr="laugh", z=SIT)
shot("L04", sub(BX - 0.17, BY + 1.1, H=4.0, tz=0.55, off=0, sh=0, up=0.5, pf=0.0), "bus")
HIDE("stranger_a", "L05")
HIDE("stranger_b", "L05")
# ===== L05 Mom and Rita on the yard-sale couch
MA, MB = [YX - 0.54, YY + 1.2], [YX + 0.54, YY + 1.2]
at_("mom", "L05", *MA, expr="smile", z=SIT)
at_("rita", "L05", *MB, expr="smile", z=SIT)
shot("L05", sub(YX - 0.17, YY + 1.2, H=4.0, tz=0.55, off=0, up=0.5, pf=0.0), "yard")
HIDE("mom", "L06")
HIDE("rita", "L06")
# ===== L06 the fast walker, then his cuff
TP("walker", "L06", [WX, WY + 1.7], 0.0, "angry", arms=[0, 0])
K("walker", "L06.2", [WX, WY - 0.2])
shot("L06", look_at([WX + 0.4, WY - 3.4, 1.5], [WX, WY + 0.4, 1.35], 34), "walker")
shot("L06.2", ins((WX + 0.2, WY + 3.4, 0.75 + 0.35), dist=2.0, elev=50, lens=40), "walkercuff")
HIDE("walker", "L07")
# ===== L07 to L13 the first morning
ME_TOM = [TOM + 0.0, 0.6]
at_("me", "L07", *ME_TOM, expr="neutral")
shot("L07", sub(ME_TOM[0], ME_TOM[1], H=2.9, tz=1.6, off=8), "mine")
HIDE("me", "L08")
at_("gus", "L08", HSX + 0.0, 1.6, expr="neutral")
shot("L08", push(look_at([-7.5, -4.2, 1.9], [18.0, 3.0, 1.1], 22), 0.1), "wide", )
HIDE("gus", "L09")
at_("me_young", "L09", TOM + 1.6, 0.6, expr="worried")
shot("L09", sub(TOM + 1.6, 0.6, H=2.9, tz=1.6, off=-8), "young")
HIDE("me_young", "L10")
GUS_H = [HSX, 0.75]
at_("gus", "L10", *GUS_H, expr="angry")
shot("L10", sub(GUS_H[0], GUS_H[1], H=2.9, tz=1.6, off=8), "gus1")
gus_mouth = {"from": "L11", "to": "L11.1", "mouth": [0.7, 0.7], "flap": True}
K("gus", "L11", GUS_H, expr="angry")
acting["gus"].append(gus_mouth)
shot("L11", sub(GUS_H[0], GUS_H[1], H=2.3, tz=1.62, off=-6), "gus2")
GUS_HC = [HSX - 1.7, 1.75]
TP("gus", "L11.1", [GUS_HC[0], GUS_HC[1], 0.0], 0.0, "angry")
acting["gus"].append({"from": "L11.1", "to": "L12", "mouth": [0.7, 0.7], "flap": True})
shot("L11.1", sub(HSX - 2.1, 1.75, H=3.5, tz=0.85, off=6), "gushoses")
props("L12", [])
HIDE("gus", "L12")
ME_HOSE = [HSX + 0.0, 0.6]
at_("me", "L12", *ME_HOSE, expr="wide")
shot("L12", sub(ME_HOSE[0], ME_HOSE[1], H=2.9, tz=1.6, off=12), "stunned1")
HIDE("me", "L13")
at_("gus", "L13", *GUS_H, expr="angry")
shot("L13", sub(GUS_H[0], GUS_H[1], H=2.6, tz=1.6, off=-12), "gus3")
shot("L13.2", sub(GUS_H[0], GUS_H[1], H=2.2, tz=1.62, off=14), "gus4")
# ===== L14 the tomatoes and the radio
HIDE("gus", "L14")
shot("L14", look_at([TOM + 0.3, 1.1, 1.45], [TOM - 0.1, 3.2, 1.3], 38), "tomatoes")
shot("L14.1", look_at([RAD - 0.05, -0.95, 1.0], [RAD + 0.12, 0.0, 0.8], 40), "radio")
# ===== L15 country / fern
GUS_R = [RAD, G.CHAIR_Y - 0.3]
at_("gus", "L15+0.3", *GUS_R, expr="smile", arms=[0, 62])
shot("L15+0.3", sub(GUS_R[0], GUS_R[1], H=2.7, tz=1.45, off=-9), "gusradio")
HIDE("gus", "L15.1")
ME_RAD = [RAD - 1.25, 0.6]
at_("me", "L15.1", *ME_RAD, expr="angry")
shot("L15.1", sub(ME_RAD[0], ME_RAD[1], H=2.9, tz=1.6, off=10), "fern")
# ===== L16 my cuff, my other hand tapping
HIDE("me", "L16")
props("L16", ["barm", "tap"])
shot("L16", ins(cc(ARM_BENCH, 1.35, 30), dist=1.5, elev=52, lens=36, off=10), "tapcuff")
# ===== L17 the birthday cactus, L18 the boss
props("L17", [])
shot("L17", look_at([BENCH_CX - 0.15, -0.55, 1.4], [BENCH_CX - 0.3, 0.52, 1.25], 40), "cactus")
ME_BR = [BENCH_CX + 1.95, 0.45]
at_("me", "L18", *ME_BR, expr="neutral", side=[0, 20])
shot("L18", sub(ME_BR[0], ME_BR[1], H=2.9, tz=1.6, off=-10), "shrug")
HIDE("me", "L19")
# ===== L19 Gus's buttoned flannel cuff on the tank rim
props("L19", ["rarm"])
shot("L19", ins(tuple(a + b for a, b in zip(cc(ARM_RIM), (0.15, 0, 0))), dist=1.5, elev=50, lens=40, off=-8), "flannelcuff")
# ===== L20 keys in the koi tank
props("L20", [])
ME_TL = [TNK - 2.55, 0.3]
at_("me", "L20", *ME_TL, expr="polite", head=[-28, 18])
shot("L20", sub(ME_TL[0], ME_TL[1], H=2.9, tz=1.55, off=-14, sh=-0.2), "tankme")
# ===== L21 Gus rolls up his sleeve and goes in to the elbow
HIDE("me", "L21")
GUS_T = [TNK, G.TANK_Y]
gus_state("L21", "rolled", None)
at_("gus", "L21", *GUS_T, expr="angry", arms=[0, 68])
shot("L21", sub(GUS_T[0], GUS_T[1], H=2.8, tz=1.62, off=10, sh=0.1), "tank1")
shot("L21.2", sub(GUS_T[0], GUS_T[1], H=2.5, tz=1.55, off=-12, sh=0.0), "tank2")
HIDE("gus", "L22")
at_("me", "L22", *ME_TL, expr="wide", head=[-25, 8])
shot("L22", sub(ME_TL[0], ME_TL[1], H=2.7, tz=1.55, off=12), "tankme2")
# ===== L23 his cuff said ONE
HIDE("me", "L23-0.3")
gus_state("L23-0.3", "rolled", 1)
props("L23-0.3", ["rarm"])
shot("L23-0.3", ins(cc(ARM_RIM), dist=1.4, elev=50, lens=40, off=8, dz=-0.1), "cuff1")
shot("L23.1", ins(cc(ARM_RIM), dist=1.15, elev=52, lens=40, off=0, dz=-0.18), "cuff1big")
props("L24", [])
at_("me", "L24", ME_TL[0] + 0.4, ME_TL[1], expr="wide", head=[-18, 6])
shot("L24", sub(ME_TL[0] + 0.4, ME_TL[1], H=2.4, tz=1.6, off=-8), "tankme3")
# ===== L25 Gus walks away down the aisle
HIDE("me", "L25")
AIS = SX["aisle"]
TP("gus", "L25", [AIS, 0.0], 180.0, "neutral")
K("gus", "L25>", [AIS, 5.5])
shot("L25", look_at([AIS, -3.6, 1.6], [AIS, 2.0, 1.2], 30), "walkaway")
# ===== L26 Gus alone at his table
GUS_TB = [TBX, G.CHAIR_Y]
at_("gus", "L26", *GUS_TB, expr="neutral", z=SIT)
shot("L26", sub(GUS_TB[0], GUS_TB[1], H=2.9, tz=1.4, off=8), "gusalone")
# ===== L27 jealous
HIDE("gus", "L27")
ME_J = [TOM + 1.8, 0.6]
at_("me", "L27", *ME_J, expr="angry", head=[0, 0])
shot("L27", sub(ME_J[0], ME_J[1], H=2.9, tz=1.6, off=-12), "jealous")
# ===== L28 in bed (night is the room's blue window; the light never changes)
HIDE("me", "L28")
BED_POS = [DX, DY - 0.15, 0.86]
TP("me", "L28", BED_POS, 0.0, "worried", lean=-90.0)
shot("L28", look_at([DX + 0.35, DY - 1.0, 2.3], [DX, DY + 1.1, 0.9], 34), "bed")
# the drop: the greenhouse, still
HIDE("me", "P01")
shot("P01", push(look_at([14.0, -5.5, 2.4], [30.0, 3.0, 1.2], 20), 0.12), "dropwide")
# ===== L29 I got it
TP("me", "L29", BED_POS, 0.0, "wide", lean=-90.0)
props("L29", ["bedarm"])
shot("L29", look_at([DX + 0.2, DY - 1.6, 2.6], [DX, DY + 1.25, 0.9], 34), "bed2")
# ===== L30 the clocks count down to when someone BECOMES your best friend
props("L30", ["bedarm"])
shot("L30", ins((DX + 0.0, DY + 0.15, 1.14 + 0.35), dist=1.5, elev=55, lens=40), "quiltcuff")
shot("L30.2", look_at([DX + 0.3, DY - 1.3, 2.4], [DX, DY + 1.5, 0.9], 34), "bed3")
# ===== L31 day one again
props("L31", [])
HIDE("me", "L31")
gus_state("L31", "buttoned", None)
at_("gus", "L31", *GUS_H, expr="angry")
shot("L31", sub(GUS_H[0], GUS_H[1], H=2.9, tz=1.6, off=8), "gus1b")
HIDE("gus", "L32")
gus_state("L32", "rolled", 1)
shot("L32", look_at([BENCH_CX - 0.5, -0.6, 1.5], [BENCH_CX - 0.3, 0.52, 1.2], 40), "cactus2")
# ===== L33 his clock had been counting down to ME (the reveal)
props("L33", [])
at_("gus", "L33", *GUS_TB, expr="neutral", z=SIT, arms=[0, 35])
shot("L33", push(sub(GUS_TB[0], GUS_TB[1], H=2.9, tz=1.3, off=0, sh=-0.2), 0.03), "gusface")
props("L33.1", ["rev"])
K("gus", "L33.1", arms=[0, 0])
shot("L33.1", sub(GUS_TB[0], GUS_TB[1], H=2.9, tz=0.8, off=0, sh=0.0, up=1.7, pf=0.08), "reveal", exp=0.0)
# ===== L34 I'd finally be his
HIDE("gus", "L34")
ME_S = [BENCH_CX + 1.9, 0.5]
props("L34", [])
at_("me", "L34", *ME_S, expr="worried")
shot("L34", sub(ME_S[0], ME_S[1], H=2.9, tz=1.6, off=-8), "sad")
K("me", "L34.1", expr="angry")
# ===== L35 two coffees
HIDE("me", "L35")
cue("L35", "cups", on=True)
shot("L35", look_at([TBX, -2.3, 1.6], [TBX + 0.02, 0.15, 0.8], 26), "cups")
# ===== L36 I sat down at his little table
at_("me", "L36", *GUS_TB, expr="smile", z=SIT)
shot("L36", sub(GUS_TB[0], GUS_TB[1], H=2.9, tz=1.4, off=-8), "mesit")
# ===== L37 the radio on COUNTRY
HIDE("me", "L37")
cue("L37", "radio2", on=True)
cue("L37", "dialhand", on=True)
shot("L37", look_at([TBX + 0.1, -1.6, 1.4], [TBX + 0.1, 0.15, 0.9], 34), "radiotable")
# ===== L38 a second head
at_("gus", "L38", *GUS_TB, expr="wide", z=SIT)
cue("L38", "dialhand", on=False)
shot("L38", sub(GUS_TB[0], GUS_TB[1], H=2.4, tz=1.45, off=8), "gusstunned")
# ===== L39 his sleeve, L40 ZERO
props("L39", ["tarm"])
HIDE("gus", "L39")
shot("L39", ins(cc(ARM_TABLE, 1.25), dist=1.6, elev=50, lens=40, off=-8), "armtable")
gus_state("L40", "rolled", 0)
shot("L40", (lambda c: [[0, [c[0] + 0.3, c[1] - 1.4, c[2] + 1.1], list(c), 40], [1, [c[0] + 0.05, c[1] - 0.95, c[2] + 0.8], list(c), 40]])(cc(ARM_TABLE, 1.25)), "cuff0")
# ===== L41 late
props("L41", [])
at_("gus", "L41", *GUS_TB, expr="smile", z=SIT)
shot("L41", sub(GUS_TB[0], GUS_TB[1], H=2.4, tz=1.45, off=-8), "gussmile")
# ===== L42, L43 still fighting (two faces side by side, both to camera)
HIDE("gus", "L42")
TWO_ME, TWO_GUS = [HSX + 0.56, 0.5], [HSX - 0.5, 0.5]
at_("me", "L42", *TWO_ME, expr="angry", arms=[0, 0])
at_("gus", "L42", *TWO_GUS, expr="angry", arms=[0, 0])
shot("L42", sub(HSX, 0.5, H=4.5, tz=1.1, off=0, lens=40, sh=-0.02, pf=0.0), "two1")
shot("L43", push(sub(HSX, 0.5, H=4.5, tz=1.1, off=-5, lens=40, sh=-0.03, pf=0.0), 0.06), "two2")
# ===== L44 lunch together
HIDE("me", "L44")
at_("gus", "L44", *GUS_TB, expr="laugh", z=SIT)
cue("L44", "radio2", on=False)
shot("L44", sub(GUS_TB[0], GUS_TB[1], H=2.6, tz=1.25, off=6, sh=-0.3), "guslaugh")
# ===== L45 pointing past camera
HIDE("gus", "L45")
at_("me", "L45", *ME_BR, expr="smile", side=[0, 22])
shot("L45", sub(ME_BR[0], ME_BR[1], H=3.0, tz=1.6, off=-8, sh=0.0), "point")
# ===== L46 the first frame again (loop)
HIDE("me", "L46")
props("L46", ["barm"])
at_("me", "L46", *ME_BENCH, expr="neutral")
shot("L46", push(sub(ME_BENCH[0], CAMY, H=1.95, tz=1.02, off=6, sh=-0.05, up=0.8), 0.1), "loopend")

# ---------------------------------------------------------------------------------------------------- finish
remap_all(cues)
for ks in acting.values():
    remap_all(ks)

shots, names = [], {}
for i, (at, camera, nm_, kw) in enumerate(SH):
    s = {"id": f"S{i + 1:02d}", "cam": camera, "step": 2, "hand": 0.008}
    s.update(kw)
    if i:
        s["at"] = remap(at)
    shots.append(s)
    names[nm_] = s["id"]

sfx = [
    {"at": "L01.2", "kind": "click", "db": -12},
    {"at": "L04", "kind": "bell", "db": -20},
    {"at": "L37.1", "kind": "click", "db": -14},
    {"at": "L40", "kind": "click", "db": -10},
    {"at": "L19", "kind": "click", "db": -16},
    {"at": "L21", "kind": "thud", "db": -16},
    {"at": "L35", "kind": "click", "db": -14},
    {"at": "L44", "kind": "bell", "db": -18},
]
music = {
    "root": 50, "mode": "major", "bpm": 112, "seed": 130,
    "sections": [
        {"at": 0, "voices": ["pulse", "pluck_hi"], "energy": 0.6},
        {"at": "L20", "voices": ["pulse"], "energy": 0.35, "mode": "minor", "root": 47},
        {"at": "L30", "voices": ["pad", "choir"], "energy": 0.3, "mode": "minor", "root": 47},
        {"at": "L35", "voices": ["pulse", "pluck_hi", "piano"], "energy": 0.65, "mode": "major", "root": 50},
    ],
}
sound = {
    "floor": "concrete", "steps_db": -26,
    "ambience": [{"kind": "water", "from": "L21", "to": "L22", "lufs": -38}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L33.1") if False else "L33"], "twist": remap("L30"),
          "quiet": [[remap("L41"), remap("L44")]],
          "hold": [names[n] for n in ("reveal",)]}
story = {
    "slug": "ep130-rival-clock",
    "title": "Best Friend Countdown Ended 11 YEARS Ago",
    "made_for_kids": False,
    "premise": ("Everyone's cuff counts down the days to their best friend, and mine hit zero eleven years ago on my first morning "
                "at a plant nursery, when the only other person there was Gus, the coworker I have fought with ever since."),
    "twist": ("The cuffs count down to the day someone BECOMES your best friend, so Gus became mine on day one, and his own cuff "
              "reads one: it has spent eleven years counting down to the day I would become his, which is tomorrow."),
    "world": ("A bright glass plant-nursery greenhouse with white frames, tables of green seedlings, red tomatoes, a slate koi "
              "tank, a little old radio on a crate and Gus's round table by the far door; broad cloth cuffs with blocky numerals "
              "on everyone's left forearm."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffcf3a",
    "gap": 0.15,
    "tail": 0.2,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#bfe6ff", "fog_density": 0.0005, "fog_start": 60.0, "sky": "#8fd0ff", "sky_strength": 0.85,
             "exposure": 0.0, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.02], "highlights": [0.03, 0.02, -0.01], "saturation": 1.08, "contrast": 1.04,
              "vignette": 0.15, "bloom": 0.15, "grain": 0.008},
    "phonemes": {},
    "homophones": {"walked": "walks", "we": "weve"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
    "framing_ok": [names[n] for n in ("fern", "walkaway", "quiltcuff")],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
print(names)
