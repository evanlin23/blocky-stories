"""Writes ../story.json for "My Aunt Has A Key To YOURS" (ep125-aunts-keys, batch 13). Run: python stories/ep125-aunts-keys/generator/make_story.py

The words are in lines.json (the script's narration). Places are in ../layout.py (shared with set.py). A character
facing -y has yaw 0, +x 90, +y 180, -x -90. Time references use the script's own chunk numbers (L24.1 is the second
slash-chunk of L24): timeline.split_lines cuts long captions to two or three words and the references are remapped.

Looks: day / night / dawn. A look change is a 0.4 s ramp over the end of the shot before the cut (the light never
jumps); the one slow change is the 1.5 s sunrise at L48. Every lamp is steady in every frame (set.py).
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
REV = 7
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = T.split_lines(orig_lines)
idx = next(i for i, l in enumerate(lines) if l["id"] == "L35")
lines.insert(idx, {"id": "P01", "pause": 0.6, "chunks": [["", ""]]})     # the 0.6 s music drop before L35


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
LAND = G.LAND
hw = G.hw
YC = {k: G.yawc(k) for k in range(1, 13)}      # facing out, toward the fountain
YF = {k: G.yawf(k) for k in range(1, 13)}      # facing the house


def land(k, lx=0.0, d=0.55):
    return hw(k, lx, d, LAND)


def court(k, lx=0.0, d=2.4):
    return hw(k, lx, d, 0.0)


def ang_diff(a, b):
    return (b - a + 180) % 360 - 180


def turned(pos, door_yaw, cam_world, frac=0.4):
    """A sleepwalker at a door turns part of the way toward a camera on the side, and the head the rest: (body yaw, head yaw)."""
    yc = G.yaw_to(pos, cam_world)
    dl = ang_diff(door_yaw, yc)
    return door_yaw + frac * dl, max(-55.0, min(55.0, (1 - frac) * dl))


# ---------------------------------------------------------------------------------------------------- cast
def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", extras=(), eyes="round", sleeves="long", height=1.0,
           width=1.0, cheeks=None, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": shoes, "sleeves": sleeves,
         "hair": hair, "hair_c": hair_c, "hat": "none", "face": {"eyes": eyes, "brows": True, "ink": "#24131f"}}
    if cheeks:
        d["face"]["cheeks"] = cheeks
    if extras:
        d["extras"] = list(extras)
    if height != 1.0:
        d["height"] = height
    if width != 1.0:
        d["width"] = width
    d.update(kw)
    return d


cast = {
    "me": person("#f1c9a0", "#26386a", "#8a8f98", "#f6f6f6", hair="cap", hair_c="#c8a060", sleeves="short"),
    "lou": person("#f1c9a0", "#ffd23f", "#6b4a2a", "#6b3d1e", hair="swoop", hair_c="#d9dbe2", eyes="lashes", cheeks="#f0a590",
                  extras=["coat", "glasses", "hooddown"], height=0.94, collar="#4a9a5a", zip_c="#d8a93b", extra_c="#7a4a2a",
                  glasses_c="#7a4a2a"),
    "ames": person("#e2b088", "#8a5a32", "#4a4a52", "#3a2c24", hair="cap", hair_c="#f0f0f0", height=0.97, width=1.04),
    "haddad": person("#b88a62", "#d9483a", "#3a3a4a", "#f4f4f2", hair="cap", hair_c="#241a16", eyes="lashes", height=0.95,
                     collar="#f4f4f2"),
}
H_OF = {n: c.get("height", 1.0) for n, c in cast.items()}
acting = {n: [] for n in cast}
last = {n: None for n in cast}
cues = []
SH = []
LOOKS = {}


def K(who, at, pos=None, **kw):
    """A key at `at`; the position is held from the last key unless `pos` is given (then it walks there)."""
    p = list(pos) if pos is not None else list(last[who])
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def TP(who, at, pos, yaw, expr="neutral", **kw):
    """The character is there from this instant (a cut); everything it doesn't set goes back to neutral."""
    if last[who] is not None:
        acting[who].append({"at": at, "pos": list(last[who]), "blend": 0.0})
    st = {"hidden": False, "arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0}
    st.update(kw)
    acting[who].append({"at": at, "pos": list(pos), "blend": 0.0, "yaw": yaw, "expr": expr, **st})
    last[who] = list(pos)


def HIDE(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0.0})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def tagc(at, n=None, clock=None):
    kw = {}
    if n is not None:
        kw["n"] = n
    if clock is not None:
        kw["clock"] = clock
    cue(at, "tag", **kw)


def lock(at, k, a0=0, a1=70, dur=0.5, lz=0.78, hand=True):
    cue(at, "key", on=True, k=k, lx=0.38, lz=lz, a0=a0, a1=a1, dur=dur, hand=hand)


def lockcam(k, lp, lens, lt=(0.38, 0.0, 0.78), lp2=None):
    """A held close-up of the key in house k's lock: a camera in house-local (lx, d, z above the landing), at least 0.7 m
    from the door so the tag (0.4 m in front of the lens) is never behind it."""
    return HC(k, (lp[0], lp[1], LAND + lp[2]), (lt[0], lt[1], LAND + lt[2]), lens,
              (lp2[0], lp2[1], LAND + lp2[2]) if lp2 else None)


def unlock(at):
    cue(at, "key", on=False)


def door(at, k, a0, a1, dur=0.8):
    cue(at, f"door{k}", a0=a0, a1=a1, dur=dur)


# ---------------------------------------------------------------------------------------------------- cameras
def _unit(a, b):
    d = [b[0] - a[0], b[1] - a[1]]
    n = math.hypot(*d) or 1.0
    return d[0] / n, d[1] / n


FS = 1.28       # the distances below are for a chest-up single; this keeps the whole head and shoulders in with headroom


def cam_face(p, yaw, who, d=3.0, off=12.0, lens=34, shift=0.14, hdz=-0.10, tdz=-0.30, d2=None, lens2=None):
    """A camera in front of a standing character at p facing yaw: d metres off, `off` degrees round, the face a little
    right of centre (shift, m) and in the top third (tdz is where it looks, from the head centre)."""
    hz = p[2] + 1.57 * H_OF[who]
    d = d * FS
    d2 = d2 * FS if d2 else d2

    def at(dd, ll):
        a = math.radians(yaw + off)
        cam = [round(p[0] + dd * math.sin(a), 3), round(p[1] - dd * math.cos(a), 3), round(hz + hdz, 3)]
        fx, fy = _unit(cam, p)
        rx, ry = fy, -fx
        tgt = [round(p[0] - rx * shift, 3), round(p[1] - ry * shift, 3), round(hz + tdz, 3)]
        return [cam, tgt, ll]

    c0 = at(d, lens)
    ks = [[0, *c0]]
    if d2 or lens2:
        c1 = at(d2 or d, lens2 or lens)
        ks.append([1, *c1])
    return ks


def cam_at(pos, tgt, lens, pos2=None, tgt2=None, lens2=None):
    ks = [[0, [round(v, 3) for v in pos], [round(v, 3) for v in tgt], lens]]
    if pos2 or tgt2 or lens2:
        ks.append([1, [round(v, 3) for v in (pos2 or pos)], [round(v, 3) for v in (tgt2 or tgt)], lens2 or lens])
    return ks


def HC(k, lp, lt, lens, lp2=None, lt2=None, lens2=None):
    """A camera given in house-local coordinates (lx, d, z)."""
    return cam_at(hw(k, *lp), hw(k, *lt), lens, hw(k, *lp2) if lp2 else None, hw(k, *lt2) if lt2 else None, lens2)


def foot(lens=24, tgt=(0.1, 0.3, 1.5), pos=(1.6, 4.0, 2.3), k=1, pos2=None, tgt2=None, lens2=None):
    """The camera in my window: level-ish, across the court, looking at her door."""
    return HC(k, pos, tgt, lens, pos2, tgt2, lens2)


def ring_cam(p, yaw, who, d=1.9, lens=24, off=14):
    a = math.radians(yaw + off)
    cam = [p[0] + d * math.sin(a), p[1] - d * math.cos(a), p[2] + 1.32]
    return cam_at(cam, [p[0], p[1], p[2] + 1.2], lens)


def shot(at, camera, look, name, **kw):
    SH.append((at, camera, look, name, kw))


def tweak_ring_target(p, yaw, who, d, lens):
    return ring_cam(p, yaw, who, d, lens)


# ================================================================================================== the film
FAR = [0.0, -60.0, 0.0]
for w_ in cast:
    TP(w_, 0, FAR, 0, hidden=True)

LOUP = land(1, 0.2, 0.55)

# ===== 01 the hook (L01)
TP("lou", 0, LOUP, YC[1], "smile")
tagc(0, 0, 0)
shot(0, cam_face(LOUP, YC[1], "lou", 2.7, 10, 34), "night", "hook")
shot("L01.2", cam_face(LOUP, YC[1], "lou", 2.2, 10, 34), "night", "hook2")

# ===== 02 the court
shot("L02", cam_at([0.6, -3.0, 2.3], [0, 10.0, 3.4], 15), "day", "courtday", face=False)
shot("L02.2", cam_at([3.5, -5.8, 1.4], [0, 0, 1.5], 22, [2.6, -5.2, 1.4], [0, 0, 1.6], 22), "day", "fountainday", face=False)
shot("L03", cam_at([-3, -9.0, 5.0], [0, 8, 2.8], 15, [-2, -8.0, 4.6], [0, 8, 2.8], 15), "night", "courtnight", face=False)
shot("L03.2", HC(8, (1.3, 2.3, LAND + 2.5), (1.0, 0, LAND + 2.5), 30, (1.1, 1.9, LAND + 2.5), (1.0, 0, LAND + 2.5), 30), "night",
     "lampclose", face=False)

# ===== the clicks (L04)
# one held close-up for the three clicks: the key in house 4's green lock, the tag counting 1, 2, 3
tagc("L04", 1)
lock("L04", 4, 0, 70, 0.25)
lock("L04.1", 4, 70, 0, 0.2)
tagc("L04.1", 2)
lock("L04.2", 4, 0, 70, 0.25)
tagc("L04.2", 3)
shot("L04", lockcam(4, (-0.3, 0.85, 0.66), 44, lp2=(-0.2, 0.8, 0.68)), "night", "click1", key=5.0, fill=2.0)
unlock("L05")
tagc("L05", 0)

# ===== 05 Mr. Ames, 06 Mrs. Haddad
WX, WY = G.WIN
AMES_POS = [WX + 0.1, WY + 1.3, -0.35]
TP("ames", "L05", AMES_POS, 0, "asleep", head=[0, 10])
shot("L05", cam_at([WX, WY - 1.7, 1.55], [WX, WY + 1.3, 1.2], 30), "night", "ames")
shot("L05.2", cam_at([WX - 0.6, WY - 4.8, 1.8], [WX - 0.5, WY, 1.6], 22), "night", "ameswide")
HADP = land(5, -0.3, 0.55)
HIDE("ames", "L06")
TP("haddad", "L06", HADP, YC[5], "worried")
shot("L06", cam_face(HADP, YC[5], "haddad", 3.0, 12, 34), "night", "haddad")

# ===== 07 Lou's ring
HIDE("haddad", "L07")
TP("lou", "L07", LOUP, YC[1], "neutral")
shot("L07", ring_cam(LOUP, YC[1], "lou", 1.8, 22), "night", "ring1")

# ===== 08 the shop, 09 the doorway and the plate
sx0, sy0 = G.STAGE["shop"]
SHOPP = [sx0 + 0.2, sy0 - 1.15, 0.0]
TP("lou", "L08", SHOPP, 0, "smile")
shot("L08", cam_face(SHOPP, 0, "lou", 2.4, 10, 34, tdz=-0.28), "night", "shop")
TP("lou", "L09", LOUP, YC[1], "warm")
shot("L09", cam_face(LOUP, YC[1], "lou", 2.8, -12, 34), "night", "named")
shot("L09.2", HC(1, (0.0, 2.1, LAND + 2.6), (0.0, 0, LAND + 2.55), 34), "night", "plate1", face=False)

# ===== 10 moving in
HIDE("lou", "L10")
ME_APP = court(7, 0.0, 7.4)
TP("me", "L10", ME_APP, YC[7] + 180, "smile")
cue("L10", "box", on=True)
K("me", "L10", ME_APP, arms=[70, 70])
K("me", "L10.2", court(7, 0.0, 4.6), arms=[70, 70], expr="smile")
shot("L10", cam_at(hw(7, 0.3, 1.6, 1.7), hw(7, 0, 6.0, 1.3), 32), "day", "meapproach")
MEP7 = land(7, 0.25, 0.55)
TP("me", "L10.2", MEP7, YC[7], "smile", arms=[70, 70])
shot("L10.2", cam_at(hw(7, -0.1, 4.0, 1.85), hw(7, 0.2, 0.3, 1.75), 34), "day", "sevendoor")
cue("L11", "box", on=False)
cue("L11", "mekey", on=True)
TP("me", "L11", MEP7, YC[7], "neutral", arms=[65, 0])
shot("L11", cam_face(MEP7, YC[7], "me", 2.9, -12, 34), "day", "mekey")
cue("L12", "mekey", on=False)
HIDE("me", "L12")
TP("lou", "L12", LOUP, YC[1], "neutral")
shot("L12", ring_cam(LOUP, YC[1], "lou", 1.5, 22, -14), "day", "ring2")

# ===== 13 listening, the tag climbing to 10
mx0, my0 = G.STAGE["mine"]
WINP = [mx0 - 1.15, my0 + 0.95, 0.0]
HIDE("lou", "L13")
TP("me", "L13", WINP, 180, "worried")
tagc("L13.1", 3)
tagc("L13.1+0.45", 6)
tagc("L13.1+0.9", 10)
shot("L13", cam_face(WINP, 180, "me", 3.0, 8, 34, shift=0.12), "night", "listen")
BOLTP = [mx0 + 3.4 + 0.3, my0 + 0.18, 1.15]
shot("L14", cam_at([mx0 + 3.8, my0 + 1.4, 1.35], BOLTP, 36), "night", "bolt", face=False)

# ===== 15 the wet sneakers
MEBED = [mx0 + 0.2, my0 + 1.5, 0.0]
tagc("L15", 0)
TP("me", "L15", MEBED, 180, "worried", head=[0, 6])
shot("L15", cam_face(MEBED, 180, "me", 3.0, -10, 34), "day", "wake")
FEETP = [mx0 + 0.1, my0 + 3.3, 0.0]
cue("L15.2", "wet", on=True)
TP("me", "L15.2", FEETP, 180, "worried")
shot("L15.2", cam_at([mx0 + 0.9, my0 + 7.6, 0.8], [mx0 + 0.1, my0 + 3.3, 0.25], 52, [mx0 + 0.8, my0 + 7.2, 0.8],
                     [mx0 + 0.1, my0 + 3.3, 0.25], 52), "day", "wetfeet", key=2.5, exp=0.35)
cue("L16", "wet", on=False)

# ===== 16 to 20 the fight
HIDE("me", "L16")
HP16 = land(5, -0.3, 0.55)
TP("haddad", "L16", HP16, YC[5], "worried")
shot("L16", cam_face(HP16, YC[5], "haddad", 3.0, -12, 34), "day", "haddad2")
HIDE("haddad", "L17")
MEMID = [mx0 - 0.3, my0 + 1.15, 0.0]
TP("me", "L17", MEMID, 180, "worried")
shot("L17", cam_face(MEMID, 180, "me", 2.9, 10, 34), "day", "uneasy")
kx0, ky0 = G.STAGE["kitchen"]
KME = [kx0 - 0.5, ky0 - 1.1, 0.0]
KLOU = [kx0 + 0.6, ky0 - 1.1, 0.0]
TP("me", "L18", KME, 0, "angry")
shot("L18", cam_face(KME, 0, "me", 3.0, 12, 34, tdz=-0.28), "day", "fightme")
HIDE("me", "L18.2")
TP("lou", "L18.2", KLOU, 0, "worried")
shot("L18.2", cam_face(KLOU, 0, "lou", 3.0, -12, 34, tdz=-0.28), "day", "fightlou")
TP("lou", "L19", KLOU, 0, "sad-smile")
shot("L19", cam_face(KLOU, 0, "lou", 2.6, 10, 34, tdz=-0.28), "day", "lougentle")
HIDE("lou", "L20")
TP("me", "L20", KME, 0, "angry", side=[18, 18])
shot("L20", cam_face(KME, 0, "me", 2.9, -10, 34, tdz=-0.28), "day", "shrug")

# ===== 21 the camera on my sill, 22 and 23 the footage
cue("L21", "mycam", on=True)
SILLP = [mx0 - 1.15 + 0.5, my0 + 0.85, 0.0]
TP("me", "L21", SILLP, 180, "neutral", arms=[40, 0])
shot("L21", cam_at([mx0 - 1.15, my0 + 2.1, 1.5], [mx0 - 1.45, my0 + 0.3, 1.15], 32), "night", "sillcam")
HIDE("me", "L22")
tagc("L22", 0, 0)
shot("L22", foot(26, (0.1, 0.3, 1.7), (2.3, 6.0, 2.5)), "night", "doorfar", face=False)
tagc("L23", 0, 1201)
shot("L23", foot(24, (0.1, 0.3, 1.7)), "night", "footage1201", face=False)

# ===== 24 she comes out
INLOU = hw(1, 0.35, -0.8, LAND)
door("L24", 1, 0, 80, 0.5)
TP("lou", "L24", INLOU, YC[1], "worried")
K("lou", "L24+0.75", INLOU, expr="worried")
K("lou", "L24.1", land(1, 0.2, 0.55), expr="worried")
shot("L24", foot(24, (0.1, 0.3, 1.7)), "night", "dooropens", face=False)
shot("L24.1", cam_face(land(1, 0.2, 0.55), YC[1], "lou", 2.8, 12, 34), "night", "louraincoat")
shot("L25", ring_cam(land(1, 0.2, 0.55), YC[1], "lou", 1.7, 22), "night", "ring3")

# ===== 26 she hurries down the steps
K("lou", "L26", land(1, 0.2, 0.55), expr="worried")
K("lou", "L26+0.35", hw(1, 0.1, 1.3, 0.3))
K("lou", "L26+0.7", hw(1, -0.1, 2.0, 0.0))
K("lou", "L26>", court(1, -0.6, 3.6))
_o, _p = hw(1, 0, 0, 0), hw(1, 0, 1, 0)
_dx, _dy = _p[0] - _o[0], _p[1] - _o[1]
shot("L26", cam_at([_dx * 2.7, _dy * 2.7, 1.45], [0, 0, 1.25], 34), "night", "hurry", follow="lou", sway=False)
door("L26+0.4", 1, 80, 0, 0.5)

# ===== 27 the clicks round the court (house 2 sky blue, 12 sky, then the green door 4)
tagc("L27", 2)
TP("lou", "L27", hw(9, 1.0, 0.85, LAND), YF[9], "worried", arms=[55, 0])
lock("L27", 9, 0, 70, 0.25)
lock("L27.1", 9, 70, 0, 0.2)
tagc("L27.1", 4)
lock("L27.2", 9, 0, 70, 0.25)
tagc("L27.2", 6)
shot("L27", lockcam(9, (-0.55, 1.35, 0.72), 58), "night", "lock2", key=5.0, fill=2.0)
unlock("L27.3")
tagc("L27.3", 8)
tagc("L27.3+0.7", 10)
RUN0, RUN1 = court(11, 0.0, 2.6), court(9, 0.0, 2.6)
TP("lou", "L27.3", RUN0, G.yaw_to(RUN0, RUN1), "worried")
K("lou", "L27.3+0.2", RUN0, run=True)
K("lou", "L27.3>", RUN1, run=True)
shot("L27.3", cam_at([-4.0, -2.0, 3.0], [-6.6, 5.6, 1.2], 22, [-3.4, -1.2, 3.0], [-6.2, 6.0, 1.2], 24), "night", "round", face=False)

# ===== 28 catching her breath
BREATH = court(8, 0.2, 2.6)
tagc("L28", 10)
TP("lou", "L28", BREATH, YC[8], "worried", head=[-25, 0])
shot("L28", cam_face(BREATH, YC[8], "lou", 3.0, 12, 34), "night", "breath")

# ===== 29 to 31 back on her porch with the blanket, 12:03 and 12:04
BLP = land(1, 0.9, 0.5)
cue("L29", "blanket", where="arm")
tagc("L29", 10, 1203)
TP("lou", "L29", court(1, 1.9, 2.4), G.yaw_to(court(1, 1.9, 2.4), land(1, 0.9, 0.5)), "worried", arms=[0, 62])
K("lou", "L29+0.1", court(1, 1.9, 2.4), arms=[0, 62])
K("lou", "L29>", BLP, yaw=YC[1], arms=[0, 62], expr="worried")
shot("L29", foot(24, (0.6, 0.3, 1.5), (1.2, 4.0, 2.3)), "night", "footage1203", face=False)
K("lou", "L30", BLP, yaw=YC[1], arms=[0, 62], expr="worried")
shot("L30", cam_face(BLP, YC[1], "lou", 3.0, -12, 34), "night", "wait")
tagc("L31", 10, 1204)
shot("L31", foot(24, (0.1, 0.3, 1.7), (1.8, 4.0, 2.3)), "night", "footage1204", face=False)

# ===== 32 to 34 somebody walks up her steps (eyes shut), the drop, the reveal
S0 = hw(1, -0.9, 3.3, 0.0)
S1 = hw(1, -0.05, 2.1, 0.0)
SB = hw(1, 0.0, 1.5, 0.15)
SM = hw(1, 0.0, 1.1, 0.30)
ST = hw(1, -0.2, 0.62, LAND)
TP("me", "L31", S0, 0, "asleep")
K("me", "L32", S1, expr="asleep")
K("me", "L32.1+0.5", S1, expr="asleep", yaw=YF[1])
K("me", "L32.2+0.3", SB, expr="asleep")
shot("L32", cam_at(hw(1, 0.5, 0.25, LAND + 0.25), hw(1, 0.0, 1.9, 0.12), 28), "night", "feetbottom", face=False)
K("me", "L33+0.3", SM, expr="asleep")
shot("L33", cam_at(hw(1, 0.9, 3.6, 0.5), hw(1, 0.0, 0.9, 0.34), 26), "night", "feetmid", key=2.0)
shot("L34", cam_at(hw(1, 0.35, 0.3, 2.05), hw(1, 0.0, 1.1, 1.86), 27), "night", "eyesshut", key=0.8)
K("me", "L34>", SM, expr="asleep", yaw=YF[1])
K("me", "P01+0.35", ST, expr="asleep", yaw=YF[1])
shot("P01", foot(32, (0.2, 0.3, 2.2), (1.8, 4.0, 2.3)), "night", "dropdoor", face=False)
HIDE("lou", "P01")     # nobody else in the reveal footage
cue("P01+0.5", "blanket", where="arm")
TP("me", "L35", ST, YC[1], "asleep")
shot("L35", cam_face(ST, YC[1], "me", 3.4, 13, 30, tdz=-0.12, hdz=0.0, shift=0.1), "night", "reveal", key=0.9)

# ===== 36 awake, 37 the handle, 38 the door
HIDE("me", "L36+0.6")
WNDP = [mx0 - 1.15, my0 + 0.95, 0.0]
TP("me", "L36+0.6", WNDP, 180, "wide")
shot("L36+0.6", cam_face(WNDP, 180, "me", 2.9, 10, 34), "night", "stunned")
HIDE("me", "L37")
TP("me", "L37", land(1, -0.12, 0.5), YF[1], "asleep", arms=[58, 0])
shot("L37", cam_at(hw(1, 1.2, 1.6, LAND + 1.45), hw(1, 0.3, 0.2, LAND + 1.2), 30), "night", "handle", face=False)
door("L38", 1, 0, 85, 0.9)
K("me", "L38", land(1, -0.12, 0.5), yaw=YF[1], arms=[58, 0])
shot("L38", foot(26, (0.15, 0.3, 1.9), (1.8, 4.0, 2.3)), "night", "dooropen", face=False)

# ===== 39 the blanket, 40 into the hall
cue("L39", "blanket", where="shoulders")
TP("me", "L39", land(1, -0.15, 0.75), YC[1], "asleep")
TP("lou", "L39", land(1, 0.62, 0.4), YC[1], "warm")
mid39 = [(land(1, -0.15, 0.75)[0] + land(1, 0.62, 0.4)[0]) / 2, (land(1, -0.15, 0.75)[1] + land(1, 0.62, 0.4)[1]) / 2, LAND]
shot("L39", cam_face(mid39, YC[1], "me", 3.4, 4, 30, shift=-0.02, hdz=-0.1, tdz=-0.14), "night", "blanket")
hx, hy = G.STAGE["hall"]
FOOT = [hx - 4.1, hy - 2.8, 0.0]
cue("L40", "blanket", where="shoulders")
TP("lou", "L40", FOOT, G.yaw_to(FOOT, [hx - 5.6, hy - 5.0]), "sad-smile")
TP("me", "L40", [hx - 0.65, hy - 2.0, 0.44], 0, "asleep")
K("me", "L40", [hx - 0.65, hy - 2.0, 0.44], yaw=180)
K("me", "L40>", [hx - 0.65, hy - 0.3, 1.32], yaw=180)
shot("L40", cam_at([hx - 5.4, hy - 5.1, 1.7], [hx - 3.0, hy - 1.9, 1.5], 27), "night", "hall")

# ===== 41 to 44 the twist said plainly
cue("L41", "blanket", where="none")
door("L41", 1, 85, 0, 0.1)
HIDE("lou", "L41")
TP("me", "L41", WNDP, 180, "wide")
shot("L41", cam_face(WNDP, 180, "me", 2.8, -10, 34), "night", "twist1")
K("me", "L42", WNDP, expr="worried")
shot("L42", cam_face(WNDP, 180, "me", 2.2, 8, 34, tdz=-0.3), "night", "twist2")
# L43: a coral door, my sleeping face, three-quarter (the neighbors' doorbell footage)
tagc("L43", 10, 1204)
CORAL = land(3, -0.12, 0.5)
CCAM = hw(3, 1.5, 1.7, LAND + 1.95)
_by, _hy = turned(CORAL, YF[3], CCAM, 0.45)
HIDE("me", "L43")
TP("me", "L43", CORAL, _by, "asleep", head=[_hy, 0])
shot("L43", cam_at(CCAM, hw(3, 0.0, 0.5, LAND + 1.4), 22), "night", "coraldoor")
HIDE("me", "L44")
tagc("L44", 0, 0)
RACE = court(5, -0.4, 2.4)
TP("lou", "L44", RACE, YC[5], "worried")
K("lou", "L44", RACE, run=True)
shot("L44", cam_face(RACE, YC[5], "lou", 3.0, 10, 34), "night", "races")

# ===== 45 to 48 the logic of her keys
tagc("L45", 2)
lock("L45", 8, 0, 70, 0.25)
lock("L45.1", 8, 70, 0, 0.2)
tagc("L45.1", 6)
lock("L45.2", 8, 0, 70, 0.25)
tagc("L45.2", 10)
shot("L45", lockcam(8, (0.26, 0.9, 0.86), 46), "night", "lk1", key=5.0, fill=2.0)
unlock("L46")
HIDE("lou", "L46")
shot("L46", foot(26, (0.1, 0.3, 1.7), (1.8, 4.0, 2.3)), "night", "hersopen", face=False)
# L47: my bolt turns from inside, asleep
DOORIN = [mx0 + 3.4, my0, 0.0]
cue("L47", "bolt", a0=0, a1=90, dur=0.8)
TP("me", "L47", [mx0 + 3.4 - 0.1, my0 + 0.65, 0.0], 0, "asleep", arms=[55, 0])
K("me", "L47", [mx0 + 3.4 - 0.1, my0 + 0.65, 0.0], yaw=0, arms=[55, 0])
shot("L47", cam_at([mx0 + 5.6, my0 + 2.8, 1.6], [mx0 + 3.5, my0 + 0.4, 1.4], 28), "night", "boltturn", face=False)
_c47 = [mx0 + 2.2, my0 + 2.4, 1.6]
_p47 = [mx0 + 3.3, my0 + 0.75, 0.0]
_b47, _h47 = turned(_p47, 0.0, _c47, 0.5)
TP("me", "L47.3", _p47, _b47, "asleep", head=[_h47, 0])
shot("L47.3", cam_at(_c47, [_p47[0], _p47[1], 1.3], 24), "night", "sleepdoor")

# ===== 48 the sunrise (the one slow light change), 49 to 51
cue("L48", "look", id="dawn", dur=1.5)
cue("L48", "blanket", where="shoulders")
HIDE("me", "L48")
HIDE("lou", "L48")
A0L, A1L = court(7, -0.5, 7.0), court(7, -0.5, 4.2)
A0M, A1M = court(7, 0.5, 7.0), court(7, 0.5, 4.2)
TP("lou", "L48", A0L, G.yaw_to(A0L, A1L), "sad-smile")
K("lou", "L48>", A1L)
TP("me", "L48", A0M, G.yaw_to(A0M, A1M), "asleep")
K("me", "L48>", A1M)
shot("L48", cam_at(hw(7, 0.0, 1.1, LAND + 1.5), hw(7, 0.0, 5.0, 1.3), 30), "dawn", "dawnwalk", fade=True)
cue("L49", "blanket", where="none")
unlock("L49")
tagc("L49", 6)
tagc("L49.1", 3)
tagc("L49.2", 0)
lock("L49", 5, 70, 0, 0.5)
shot("L49", lockcam(5, (0.0, 0.95, 1.25), 42), "dawn", "unlock", key=4.0, fill=1.5)
unlock("L50")
TP("lou", "L50", LOUP, YC[1], "neutral")
shot("L50", ring_cam(LOUP, YC[1], "lou", 1.5, 22, -14), "dawn", "ring4")
TP("lou", "L51", LOUP, YC[1], "warm")
shot("L51", cam_face(LOUP, YC[1], "lou", 2.7, 12, 34), "dawn", "louwarm")

# ===== 52 to 57 Thursday
tagc("L52", 0, 1201)
HIDE("lou", "L52")
TP("me", "L52", WNDP, 180, "worried")
shot("L52", cam_face(WNDP, 180, "me", 2.8, 10, 34), "night", "thursday")
HIDE("me", "L53")
tagc("L53", 6)
SLOW = court(2, 0.4, 2.6)
TP("lou", "L53", SLOW, YC[2], "sad-smile", arms=[0, 0])
K("lou", "L53", SLOW)
shot("L53", cam_face(SLOW, YC[2], "lou", 3.0, 12, 34), "night", "slowlou")
TP("me", "L54", CORAL, _by, "asleep", head=[_hy, 0])
shot("L54", cam_at(CCAM, hw(3, 0.0, 0.5, LAND + 1.4), 22), "night", "amesdoor")
tagc("L54", 9)
K("me", "L55", CORAL, yaw=YF[3], head=[0, 0], arms=[58, 0])
shot("L55", cam_at(hw(3, 1.2, 1.5, LAND + 1.45), hw(3, 0.3, 0.2, LAND + 1.2), 30), "night", "hand2", face=False)
tagc("L56", 10)
TP("lou", "L56", land(3, 0.9, 0.7), YF[3], "worried", arms=[55, 0])
lock("L56", 3, 0, 80, 0.3)
HIDE("me", "L56")
shot("L56", lockcam(3, (0.12, 0.8, 0.52), 40, lp2=(0.2, 0.75, 0.56)), "night", "click56", key=5.0, fill=2.0)
unlock("L57")
SIT = hw(3, 0.3, 1.1, 0.30 - 0.55)
TP("lou", "L57", SIT, YC[3], "sad-smile", lean=8, head=[0, 10])
K("lou", "L57", SIT, lean=8, head=[0, 10])
shot("L57", cam_face(SIT, YC[3], "lou", 3.0, 12, 34, tdz=-0.28), "night", "shook")

# ===== 58 to 61 where I was walking to
tagc("L58", 0, 0)
HIDE("lou", "L58")
TP("me", "L58", MEMID, 180, "worried")
shot("L58", cam_face(MEMID, 180, "me", 2.8, 10, 34), "night", "walkingto")
# the hall door, past the stair, to the kitchen table
K("me", "L59", MEMID)
HIDE("me", "L59")
shot("L59", cam_at([kx0 - 0.1, ky0 - 6.2, 1.7], [kx0, ky0 - 2.3, 0.7], 27), "day", "tableend", key=1.4, exp=0.15)
shot("L60", cam_at([kx0 + 0.9, ky0 - 5.0, 1.8], [kx0, ky0 - 2.3, 0.75], 22, [kx0 + 0.6, ky0 - 4.5, 1.6], [kx0, ky0 - 2.3, 0.75], 22),
     "day", "tableclose", key=1.2, exp=0.15)
STOVE = [kx0 + 1.8, ky0 - 1.05, 0.0]
TP("lou", "L60.1", STOVE, 0, "smile")
shot("L60.1", cam_face(STOVE, 0, "lou", 3.2, 12, 34, tdz=-0.28), "day", "stove")
HIDE("lou", "L61")
MEL = [mx0 + 0.3, my0 + 1.7, 0.0]
TP("me", "L61", MEL, 180, "worried")
shot("L61", cam_face(MEL, 180, "me", 2.8, -10, 34), "day", "notback")

# ===== 62 to 65 the warm turn
APP = court(1, 0.0, 8.0)
HIDE("me", "L62")
TP("me", "L62", APP, G.yaw_to(APP, court(1, 0.0, 3.6)), "smile")
K("me", "L62", APP, expr="smile")
K("me", "L62>", court(1, 0.0, 3.8), expr="smile")
shot("L62", cam_at(hw(1, 0.3, 1.0, LAND + 1.3), hw(1, 0.0, 6.0, 1.2), 32), "day", "walkover")
TABLE = [kx0, ky0 - 1.25, 0.0]
HIDE("me", "L63")
TP("lou", "L63", TABLE, 0, "smile", arms=[0, 50])
shot("L63", cam_face(TABLE, 0, "lou", 3.2, 12, 34, tdz=-0.28), "day", "soup", exp=0.25)
HIDE("lou", "L64")
HOME0 = court(7, 0.0, 7.0)
TP("me", "L64", HOME0, G.yaw_to(HOME0, court(7, 0.0, 3.4)), "warm")
K("me", "L64", HOME0, expr="warm")
K("me", "L64>", court(7, 0.0, 3.6), expr="warm")
shot("L64", cam_at(hw(7, 0.3, 1.2, LAND + 1.3), hw(7, 0.0, 6.0, 1.2), 32), "day", "walkhome")
HIDE("me", "L65")
cue("L65", "sneaks", on=True)
shot("L65", cam_at([mx0 + 3.4 - 0.2, my0 + 1.6, 0.5], [mx0 + 3.4 - 0.55, my0 + 0.55, 0.05], 32), "day", "dry", face=False)
cue("L66", "sneaks", on=False)
ox0, oy0 = G.STAGE["old"]
shot("L66", cam_at([ox0 + 0.2, oy0 + 3.6, 1.45], [ox0 + 0.4, oy0 + 0.8, 0.85], 28), "day", "oldroom", face=False)
OLDP = [ox0 - 1.5, oy0 + 0.95, 0.0]
TP("lou", "L67", OLDP, 180, "warm")
shot("L67", cam_face(OLDP, 180, "lou", 2.8, 12, 34), "day", "oldroomlou")
tagc("L68", 10)
NIGHTP = court(11, 0.0, 2.8)
TP("lou", "L68", NIGHTP, YC[11], "smile")
shot("L68", cam_face(NIGHTP, YC[11], "lou", 3.0, 12, 34), "night", "rounds")
tagc("L69", 0, 0)
TP("lou", "L69", LOUP, YC[1], "smile")
shot("L69", cam_face(LOUP, YC[1], "lou", 3.0, 10, 34, d2=2.3), "night", "loop")

# ---------------------------------------------------------------------------------------------------- finish
SPAN = {}
remap_all(cues)
for ks in acting.values():
    remap_all(ks)

shots, names = [], {}
prev_look = None
for i, (at, camera, look, nm_, kw) in enumerate(SH):
    s = {"id": f"S{i + 1:02d}", "cam": camera, "step": 2, "hand": 0.004}
    kw = dict(kw)
    fade = kw.pop("fade", False)
    sway = kw.pop("sway", None)
    if i:
        s["at"] = remap(at)
    if look != prev_look and prev_look is not None and not fade:
        # the light ramps over the last 0.4 s of the shot before the cut
        cues.append({"at": remap(f"{at}-0.4") if isinstance(at, str) else max(0.0, at - 0.4), "name": "look", "id": look, "dur": 0.4})
    s.update(kw)
    if look and prev_look is None:
        cues.append({"at": 0, "name": "look", "id": look, "dur": 0.0})
    prev_look = "dawn" if fade else look
    shots.append(s)
    names[nm_] = s["id"]

DAWN = ["L48"]
sfx = [
    {"at": "L01.2", "kind": "thud", "db": -12},
    {"at": "L01.2", "kind": "click", "db": -9},
    {"at": "L04", "kind": "click", "db": -13},
    {"at": "L04.2", "kind": "click", "db": -13},
    {"at": "L27", "kind": "click", "db": -17},
    {"at": "L27.2", "kind": "click", "db": -17},
    {"at": "L38", "kind": "creak", "db": -16},
    {"at": "L56+0.15", "kind": "click", "db": -6},
    {"at": "L63", "kind": "click", "db": -20},
]
music = {
    "root": 43, "mode": "minor", "bpm": 92, "seed": 125,
    "sections": [
        {"at": 0, "voices": ["pulse", "piano"], "energy": 0.5},
        {"at": "L21", "voices": ["pulse", "pad"], "energy": 0.32},
        {"at": "L23", "voices": ["drone", "pad"], "energy": 0.3},
        {"at": "L35", "voices": ["drone", "pad", "pulse"], "energy": 0.5},
        {"at": "L44", "voices": ["pulse", "piano", "pad"], "energy": 0.62},
        {"at": "L58", "voices": ["pad", "piano"], "energy": 0.45, "mode": "major"},
        {"at": "L69", "voices": ["pulse", "piano"], "energy": 0.5, "mode": "minor"},
    ],
}
sound = {
    "floor": "stone", "steps_db": -26,
    "ambience": [{"kind": "crickets", "from": "L21", "to": "L58", "lufs": -40},
                 {"kind": "water", "from": "L21", "to": "L58", "lufs": -46}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"reveal": [remap("L35")], "twist": remap("L35"),
          "quiet": [[remap("L59"), remap("L68")]],
          "hold": [names[n] for n in ("courtday", "courtnight", "doorfar", "footage1201", "footage1203", "footage1204",
                                       "dropdoor", "dooropen", "plate1", "reveal", "hersopen", "dooropens", "click1", "lock2", "lk1", "unlock", "click56",
                                       "eyesshut", "feetmid", "wetfeet", "hall", "boltturn")]}
story = {
    "slug": "ep125-aunts-keys",
    "title": "My Aunt Has A Key To YOURS",
    "made_for_kids": False,
    "premise": ("My aunt Lou, the court's locksmith, has a key to every house on our court and locks them all at midnight, "
                "except mine, which never clicks, and my sneakers are wet every morning."),
    "twist": ("The one walking the court at midnight is me, asleep, trying handles on my way home to her house, so she races "
              "round locking every door but hers to make sure the only one I can open is hers; I stop sleepwalking when I "
              "walk over to her table awake."),
    "world": ("A horseshoe court of twelve narrow red-brick houses round a stone fountain, painted doors in a row of colours, "
              "a steady brass carriage lamp on every door; Aunt Lou's teal door with a brass knocker, red geraniums and a "
              "striped mat, and her warm kitchen."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffb347",
    "gap": 0.15,
    "tail": 0.2,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#1d3f5a", "fog_density": 0.001, "fog_start": 40.0, "sky": "#1d3f5a", "sky_strength": 0.55,
             "exposure": 0.0, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.015, -0.02], "saturation": 1.08, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.2, "grain": 0.008},
    "phonemes": {"Haddad": "hˈædəd"},
    # Whisper's spellings and near-sounds (it hears "twelve oh one" as 1201, "give" as "get"): checked by ear
    "homophones": {"1201": "twelveohone", "1203": "twelveohthree", "1204": "twelveohfour", "for": "her", "their": "her",
                   "get": "give", "watch": "watched", "around": "round", "amess": "ames", "and": "in"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
    "framing_ok": [names[n] for n in ("courtnight", "fightme", "round", "footage1203", "feetbottom", "lk1", "boltturn")],
    "frames_ok": [names[n] for n in ("dawnwalk", "tableend")],     # the dawn brightening and the day look easing in at the cut
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
print(names)
