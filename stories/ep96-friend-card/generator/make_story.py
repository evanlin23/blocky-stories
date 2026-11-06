"""Writes ../story.json for ep96-friend-card (script.md). Run: python stories/ep96-friend-card/generator/make_story.py

Places: layout.py (stage origins). Every stage is built by set.py around its origin; x east, y away from the camera,
z up; a character facing -y has yaw 0, +x 90, -x -90, +y 180.
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
OUT = HERE.parent / "story.json"

# ------------------------------------------------------------------------------------------------ the words
orig = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = [], {}
for ln in orig:
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
    """A reference written against the script's chunks (L12.2) -> against the caption chunks after splitting."""
    if not isinstance(ref, str):
        return ref
    mm = re.match(r"^(L\d+)\.(\d+)(.*)$", ref)
    if mm and mm.group(1) in CHUNKMAP:
        return f"{mm.group(1)}.{CHUNKMAP[mm.group(1)][int(mm.group(2))]}{mm.group(3)}"
    return ref


# ------------------------------------------------------------------------------------------------ time refs
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from blocky import timeline as TL  # noqa: E402
import layout as LY  # noqa: E402

_voice = json.loads((HERE.parent / "voice-timings.json").read_text())
_tl = TL.build({"name": "ep96-friend-card", "gap": 0.12, "tail": 0.25, "lines": lines, "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
                "shots": [{"id": "S1", "cam": [[0, [0, -5, 1.5], [0, 0, 1.5], 30]]}]}, _voice)
TLINES = _tl["lines"]


def T(ref):
    if not isinstance(ref, str):
        return float(ref)
    m = re.match(r"^(L\d+|P\d+)(?:\.(\d+))?(>)?([+-][\d.]+)?$", ref)
    if not m:
        raise ValueError(ref)
    ln = TLINES[m.group(1)]
    if m.group(3):
        t = ln["end"]
    elif m.group(2) is not None:
        t = ln["chunks"][int(m.group(2))][0] if ln.get("chunks") else ln["onset"]
    else:
        t = ln["onset"]
    return t + (float(m.group(4)) if m.group(4) else 0.0)


# ------------------------------------------------------------------------------------------------ the cast
def person(skin, shirt, pants, shoes="#2b2d33", hair="cap", hair_c="#3a2418", pattern="solid", pattern_c=None,
           collar=None, hat="none", extras=(), extra_c=None, eyes="round", height=1.0, sleeves="long", zip_c=None, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "height": height,
         "face": {"eyes": eyes, "brows": True}}
    if pattern_c:
        d["pattern_c"] = pattern_c
    if collar:
        d["collar"] = collar
    if extras:
        d["extras"] = list(extras)
    if extra_c:
        d["extra_c"] = extra_c
    if zip_c:
        d["zip_c"] = zip_c
    d.update(kw)
    return d


cast = {
    "me": person("#d9a577", "#28324f", "#28324f", "#17181f", hair_c="#4a3020", collar="#fafafa", extras=["tie"], extra_c="#9cc59a"),
    "me_d": person("#d9a577", "#4f78a8", "#2c3550", "#f0f0ee", hair_c="#4a3020", collar="#e8f0f8"),
    "maya": person("#b57a53", "#5b84b8", "#2c3550", "#f0f0ee", hair="bun", hair_c="#1c1210", collar="#dbe6f2", eyes="lashes"),
    "maya_w": person("#b57a53", "#fffaf2", "#fffaf2", "#fffaf2", hair="bun", hair_c="#1c1210", eyes="lashes"),
    "nate": person("#d9a577", "#4f9a6a", "#3a3a4a", "#3a2a20", pattern="knit", pattern_c="#3a7a52", hair_c="#3a2418", height=1.08),
    "nate_s": person("#d9a577", "#28324f", "#28324f", "#17181f", hair_c="#3a2418", collar="#fafafa", extras=["tie"], extra_c="#ffb38a", height=1.08),
    "dad": person("#e8b890", "#5a8fb0", "#b99a6a", "#5a3b22", hair_c="#b8b8b8", collar="#f4f4f4", eyes="tired"),
    "reyes": person("#a9714a", "#d9a04a", "#4a4036", "#2a2a2a", hair="buzz", hair_c="#707070", collar="#f4e8c8", height=1.02),
    "abbott": person("#f0c8a0", "#9a7ad0", "#9a7ad0", "#5a4a6a", hair="bun", hair_c="#c8c8d0", eyes="lashes", extras=["coat"], zip_c="#fafafa"),
    "friend": person("#c58c63", "#ff8f7a", "#2f3548", "#f0f0ee", hair="long", hair_c="#6b2a1a", eyes="lashes", extras=["backpack"], extra_c="#4fb0ff"),
    "officiant": person("#e8b890", "#3a3a50", "#3a3a50", "#17181f", hair_c="#9a9a9a", collar="#fafafa", extras=["coat"], zip_c="#fafafa"),
    "mdad": person("#b57a53", "#3a3a50", "#3a3a50", "#17181f", hair="buzz", hair_c="#9a9a9a", collar="#fafafa", extras=["tie"], extra_c="#ffd23f", height=1.03),
    "g1": person("#f0c8a0", "#ff9fb8", "#4a4a5a", hair="long", hair_c="#c8923a", eyes="lashes", extras=["coat"], zip_c="#fafafa"),
    "g2": person("#8a5a3a", "#3a5a8a", "#2a2a38", hair="buzz", hair_c="#1a1210", collar="#fafafa"),
    "g3": person("#e8b890", "#9cc59a", "#6a6a7a", hair="swoop", hair_c="#a05a2a", eyes="lashes", extras=["coat"], zip_c="#fafafa"),
    "g4": person("#b98456", "#b88cff", "#2a2a38", hair="cap", hair_c="#1c1a18", collar="#fafafa"),
    "g5": person("#f0c8a0", "#ffd23f", "#4a4a5a", hair="bun", hair_c="#8a3a1f", eyes="lashes", extras=["coat"], zip_c="#fafafa"),
    "g6": person("#a9714a", "#e4573d", "#2a2a38", hair="spiky", hair_c="#2a1a12", collar="#fafafa"),
}
EX = {"nervous": "worried", "forced": "polite", "sneaky": "smirk", "stunned": "wide", "queasy": "squeeze"}

# ------------------------------------------------------------------------------------------------ acting machinery
acting = {n: [] for n in cast}
_seq = [0]
visible = {n: False for n in cast}
lastpos = {n: [0.0, 0.0] for n in cast}


def K(who, ref, **kw):
    _seq[0] += 1
    acting[who].append((T(ref), _seq[0], {"at": ref, **kw}))


def cam_keys(*keys):
    return [list(k) for k in keys]


def wpos(stage, p):
    ox, oy = LY.ST[stage]
    return [round(ox + p[0], 3), round(oy + p[1], 3)] + ([p[2]] if len(p) > 2 else [])


cues = []


def cue(ref, name, **kw):
    cues.append({"at": ref, "name": name, **kw})


shots = []
SH = []     # (time, shot dict)


def C(stage, tgt, az, F, lens=35, el=4.0, push=0.0, to=None, dz=0.0, daz=0.0, roll=0.0):
    """A camera `F` metres of frame height at the target (stage-local), azimuth az (0: camera on the -y side),
    elevation el degrees. push: fraction of the distance to close over the shot. to: the target a second key moves to."""
    d = F * lens / 24.0
    ox, oy = LY.ST[stage]

    def key(u, tg, a, dd):
        r = math.radians(a)
        e = math.radians(el)
        x = tg[0] + dd * math.cos(e) * math.sin(r)
        y = tg[1] - dd * math.cos(e) * math.cos(r)
        z = tg[2] + dd * math.sin(e) + dz
        return [u, [round(ox + x, 3), round(oy + y, 3), round(z, 3)], [round(ox + tg[0], 3), round(oy + tg[1], 3), round(tg[2], 3)], lens, roll]

    k0 = key(0, tgt, az, d)
    tg1 = to or tgt
    k1 = key(1, tg1, az + daz, d * (1 - push))
    if push == 0.0 and to is None and daz == 0.0:
        return [k0]
    return [k0, k1]


seated = {n: False for n in cast}
holding = {}     # prop -> who, as of the last shot


def S(ref, sid, stage, cam, who=None):
    """A shot at `ref`. who: {name: {pos, yaw, expr, arms, side, head, look, sit, held}}; characters not listed hide."""
    shots.append({"id": sid, "at": ref, "cam": cam, "stage": stage, "hand": 0.0, "step": 1})
    who = who or {}
    now = {}
    for n in cast:
        if n in who:
            d = dict(who[n])
            pos = wpos(stage, d.pop("pos"))
            sit = d.pop("sit", None)
            hl = d.pop("held", None)
            e = d.pop("expr", "neutral")
            keyd = {"pos": pos, "blend": 0.0, "hidden": False, "yaw": 0, "expr": EX.get(e, e)}
            keyd.update(d)
            K(n, ref, pos=list(lastpos[n]))
            K(n, ref, **keyd)
            lastpos[n] = pos
            visible[n] = True
            if sit is not None:
                cue(ref, "sit", who=n, z=sit, on=True)
                seated[n] = True
            elif seated[n]:
                cue(ref, "sit", who=n, z=0.68, on=False)
                seated[n] = False
            if hl:
                for h in (hl if isinstance(hl, list) else [hl]):
                    cue(ref, "held", who=n, **h)
                    now[h["obj"]] = n
        elif visible[n]:
            K(n, ref, hidden=True)
            visible[n] = False
            if seated[n]:
                cue(ref, "sit", who=n, z=0.68, on=False)
                seated[n] = False
    for obj in list(holding):
        if obj not in now:
            cue(ref, "held", obj=obj, who=holding[obj], off=[0, 0, 0], on=False)
    holding.clear()
    holding.update(now)


def M(who, ref, stage, **kw):
    """A mid-shot key for a character: pos (stage-local) walks there; other fields as acting keys."""
    d = dict(kw)
    if "pos" in d:
        d["pos"] = wpos(stage, d["pos"])
        lastpos[who] = d["pos"]
    if "expr" in d:
        d["expr"] = EX.get(d["expr"], d["expr"])
    K(who, ref, **d)


def held(obj, who, off, **kw):
    return {"obj": obj, "off": list(off), **kw}


def HC(tx, tz, az, F, lens=45, push=0.0, tx2=None, tz2=None, el=0.0, roll=0.0):
    """A camera on the hand stage: target (tx, tz) in the rig's frame (x, z), F metres of frame height."""
    tg = (tx, 0.0, 1.2 + tz)
    to = (tx2, 0.0, 1.2 + tz2) if tx2 is not None else None
    return C("hand", tg, az, F, lens, el, push, to, roll=roll)


# ---- shot tools for the hand rig
def hand_cues(ref, who="me", face=None, watch=None, ring=None, rz=None, dur=0.01, tremble=None):
    cue(ref, "hand", who=who)
    if face or rz is not None:
        d = {"face": face or "mine"}
        if rz is not None:
            d["rz"] = rz
            d["dur"] = dur
        cue(ref, "card", **d)
    if watch:
        cue(ref, "watch", time=watch)
    if tremble is not None:
        cue(ref, "tremble", amp=tremble)


NONE = None
# ================================================================================================ THE SHOTS
# ---- the hook (0 to 2.9 s): the card in my hand, 9:14 and my watch at 9:11, then TONIGHT
cue(0, "ring", p=0.25)
hand_cues(0, "me", "mine", "9:11", tremble=0)
cue(0, "card", face="mine", rz=0, dur=0.01)
S(0, "S01a", "hand", HC(0.0, 0.0, 0, 0.34, 40, push=0.12), None)
S("L01.2", "S01b", "hand", HC(0.0, 0.074, 6, 0.22, 40, push=0.10), None)
S("L01.3", "S01c", "hand", HC(0.05, -0.083, -8, 0.15, 50, push=0.10), None)
S("L01.4", "S01d", "hand", HC(0.0, 0.03, 0, 0.30, 40, push=0.22, tx2=0.0, tz2=0.062), None)

# ---- S02 (me, the suit, tucking the card away) on the roof, near the entrance
S("L02", "S02a", "roof", C("roof", (-0.3, 1.0, 1.25), 14, 1.55, 40, 2.0, push=0.18),
  {"me": {"pos": (-0.3, 1.0), "yaw": 14, "expr": "nervous", "arms": [0, 55],
          "held": held("card", "me", (0.46, -0.52, 1.02), s=1.0)}})
M("me", "L02+0.45", "roof", arms=[0, 25])
cue("L02+0.45", "held", obj="card", who="me", off=[0.16, -0.19, 1.2], dur=0.4)
S("L02.2", "S02b", "roof", C("roof", (-0.3, 1.0, 1.52), -16, 0.95, 50, 2.0, push=0.1),
  {"me": {"pos": (-0.3, 1.0), "yaw": -16, "expr": "nervous", "arms": [0, 25],
          "held": held("card", "me", (0.16, -0.19, 1.2))}})
M("me", "L02.2+0.2", "roof", expr="worried", head=[0.2, 0.0])

# ---- S03 to S07: the rule at work
cue("L03+0.1", "drop")
S("L03+0.1", "S03a", "hall", C("hall", (0, 3.5, 0.55), 8, 1.7, 30, 4.0, push=0.12), None)
S("L03.1+0.08", "S03b", "hand", HC(0.02, 0.0, 0, 0.30, 40, push=0.15), None)
hand_cues("L03.1+0.08", "me", "sealed", "9:11", rz=0, dur=0.01)
cue("L03.1+0.15", "card", face="mine", rz=0, dur=0.01)
S("L03.2", "S04", "hand", HC(0.0, 0.074, 14, 0.2, 50, push=0.14, tx2=0.0, tz2=0.07), None)
hand_cues("L03.2", "me", "mine", "9:11")

S("L05", "S05a", "park", C("park", (0.0, 3.0, 0.9), 0, 9.0, 24, 28.0, push=0.1),
  {"dad": {"pos": (-1.15, 2.6), "yaw": 80, "expr": "angry", "arms": [10, 10]},
   "reyes": {"pos": (1.15, 2.6), "yaw": -80, "expr": "angry", "arms": [10, 10]}})
S("L05.2", "S05b", "park", C("park", (0.0, 2.6, 0.95), 0, 3.2, 30, 2.0, push=0.15, to=(0.0, 2.6, 1.0)),
  {"dad": {"pos": (-0.8, 2.6), "yaw": 88, "expr": "angry", "arms": [10, 10]},
   "reyes": {"pos": (0.8, 2.6), "yaw": -88, "expr": "angry", "arms": [10, 10]}})
M("dad", "L05.3", "park", head=[0.0, 0.2])
M("reyes", "L05.3", "park", head=[0.0, 0.2])

S("L06", "S06a", "lawn", C("lawn", (0.0, 2.2, 1.2), 38, 6.0, 30, 4.0, push=0.12),
  {"dad": {"pos": (-1.5, 2.0), "yaw": -85, "expr": "angry", "arms": [75, 75]},
   "reyes": {"pos": (1.5, 2.0), "yaw": 85, "expr": "angry", "arms": [75, 75]}})
S("L06.2", "S06b", "lawn", C("lawn", (0.0, 2.0, 1.45), 10, 4.0, 35, 3.0, push=0.1),
  {"dad": {"pos": (-0.72, 2.0), "yaw": 55, "expr": "angry", "arms": [60, 60]},
   "reyes": {"pos": (0.72, 2.0), "yaw": -55, "expr": "angry", "arms": [60, 60]}})
S("L06.3", "S06c", "lawn", C("lawn", (0.0, 2.0, 1.45), -14, 3.8, 35, 3.0, push=0.1),
  {"dad": {"pos": (-0.72, 2.0), "yaw": 60, "expr": "angry", "arms": [60, 60]},
   "reyes": {"pos": (0.72, 2.0), "yaw": -60, "expr": "angry", "arms": [60, 60]}})

S("L07", "S07a", "gate", C("gate", (-0.6, 3.9, 1.3), 4, 4.4, 28, 3.0, push=0.12),
  {"abbott": {"pos": (-1.4, 3.2), "yaw": 20, "expr": "laugh", "side": [0, 0], "arms": [0, 150]},
   "friend": {"pos": (0.6, 4.4), "yaw": 150, "expr": "smile"}})
M("friend", "L07.1", "gate", pos=(2.4, 7.0), yaw=160)
M("abbott", "L07+0.3", "gate", arms=[0, 120])
M("abbott", "L07.1", "gate", arms=[0, 165])
S("L07.2", "S07b", "gate", C("gate", (3.5, 7.6, 2.2), 0, 4.5, 28, 2.0, push=0.08),
  {"abbott": {"pos": (3.4, 5.8), "yaw": 0, "expr": "laugh", "arms": [0, 165]},
   "friend": {"pos": (3.7, 8.2), "yaw": 180, "expr": "smile"}})
M("abbott", "L07.2+0.35", "gate", arms=[0, 120])
S("L07.3", "S07c", "gate", C("gate", (2.8, 6.8, 1.3), -20, 3.5, 30, 3.0, push=0.12),
  {"friend": {"pos": (2.2, 5.0), "yaw": 170, "expr": "smile"}})
M("friend", "L07.3+0.9", "gate", pos=(2.7, 6.4), yaw=180)

# ---- S08 to S13: mine, Maya, the back of the card
cue("L08", "ring", p=0.25)
cue("L14", "ring", p=0.05)
cue("L22", "ring", p=0.08)
cue("L23", "ring", p=0.3)
cue("L29", "ring", p=0.86)
cue("L32", "ring", p=0.94)
cue("P01", "ring", p=0.97)
cue("L34", "ring", p=1.0)
cue("L48", "ring", p=1.0)
cue("L49.3", "ring", p=0.25)
S("L08", "S08a", "hand", HC(0.0, 0.052, -10, 0.15, 50, push=0.12, tx2=0.02, tz2=0.062), None)
hand_cues("L08", "me", "mine", "9:11")
S("L08.1", "S08b", "curb", C("curb", (0.7, 3.2, 1.15), -6, 3.3, 40, 3.0, push=0.12),
  {"maya": {"pos": (0.0, 3.2), "yaw": -6, "expr": "laugh", "sit": 0.43},
   "me_d": {"pos": (1.4, 3.2), "yaw": -20, "expr": "smile", "sit": 0.43}})
S("L09", "S09a", "curb", C("curb", (0.4, 3.2, 1.0), 4, 4.0, 32, 3.0, push=0.14),
  {"maya": {"pos": (-0.3, 3.2), "yaw": 6, "expr": "laugh", "sit": 0.43, "arms": [60, 0]},
   "me_d": {"pos": (1.1, 3.2), "yaw": -6, "expr": "laugh", "sit": 0.43, "arms": [0, 60]}})
S("L09.1", "S09b", "curb", C("curb", (-0.3, 3.2, 1.4), 14, 1.2, 45, 3.0, push=0.1),
  {"maya": {"pos": (-0.3, 3.2), "yaw": 14, "expr": "laugh", "sit": 0.43, "arms": [60, 0]},
   "me_d": {"pos": (1.1, 3.2), "yaw": -6, "expr": "laugh", "sit": 0.43}})
cue("L09", "show", id="lastfry", on=True)
S("L10", "S10a", "curb", C("curb", (0.4, 3.2, 0.95), -8, 3.9, 36, 6.0, push=0.14),
  {"maya": {"pos": (-0.3, 3.2), "yaw": 22, "expr": "angry", "sit": 0.43, "arms": [55, 20]},
   "me_d": {"pos": (1.1, 3.2), "yaw": -22, "expr": "angry", "sit": 0.43, "arms": [20, 55]}})
M("maya", "L10.0+0.25", "curb", arms=[75, 20])
M("me_d", "L10.0+0.25", "curb", arms=[20, 75])
S("L10.1", "S10b", "curb", C("curb", (0.4, 3.2, 1.0), 6, 4.0, 32, 3.0, push=0.14),
  {"maya": {"pos": (-0.3, 3.2), "yaw": 8, "expr": "laugh", "sit": 0.43, "arms": [20, 20]},
   "me_d": {"pos": (1.1, 3.2), "yaw": -8, "expr": "laugh", "sit": 0.43, "arms": [20, 20]}})
cue("L10.1", "show", id="lastfry", on=False)
S("L11", "S11a", "hand", HC(0.0, 0.074, -6, 0.2, 45, push=0.1), None)
hand_cues("L11", "me", "mine", "9:11")
S("L11.1", "S11b", "hand", HC(-0.05, 0.1, 6, 0.1, 55, push=0.2, tx2=-0.05, tz2=0.098), None)
S("L12", "S12a", "hand", HC(0.0, 0.074, 12, 0.24, 40, push=0.12), None)
hand_cues("L12", "me", "mine", "9:11", rz=180, dur=0.45)
S("L12.2", "S12b", "hand", HC(0.0, 0.074, 180, 0.14, 55, push=0.1), None)
S("L12.4", "S12c", "hand", HC(0.0, 0.074, 180, 0.12, 55, push=0.35, tx2=0.0, tz2=0.067), None)
cue("L13", "ring", p=0.12)
S("L13", "S13a", "roof", C("roof", (-0.08, 1.0, 1.42), 12, 1.8, 40, 2.0, push=0.12),
  {"me": {"pos": (-0.3, 1.0), "yaw": 12, "expr": "scared", "arms": [0, 100],
          "held": held("card", "me", (0.44, -0.68, 1.4), s=1.4)}})
S("L13.1", "S13b", "roof", C("roof", (-0.1, 1.0, 1.42), -10, 1.35, 50, 2.0, push=0.12),
  {"me": {"pos": (-0.3, 1.0), "yaw": -10, "expr": "scared", "arms": [0, 100],
          "held": held("card", "me", (0.44, -0.68, 1.4), s=1.4)}})

# ---- S14 to S22: ten years of dodging
cue("L14", "calflip", i=0)
S("L14", "S14a", "cal", C("cal", (0.0, 2.9, 2.4), 0, 2.8, 32, 2.0, push=0.1), None)
cue("L14.1+0.0", "calflip", i=1)
cue("L14.2", "calflip", i=2)
S("L14.2", "S14b", "cal", C("cal", (0.0, 2.9, 2.35), 8, 2.2, 32, 2.0, push=0.14), None)
S("L15", "S15a", "living", C("living", (-0.05, 2.3, 1.05), 0, 4.0, 32, 4.0, push=0.14),
  {"maya": {"pos": (-0.75, 2.3), "yaw": 6, "expr": "smirk", "sit": 0.66, "arms": [45, 70],
            "held": held("remote", "maya", (0.0, -0.45, 0.85), tilt=60)},
   "me_d": {"pos": (0.65, 2.3), "yaw": -6, "expr": "polite", "sit": 0.66}})
M("maya", "L15.1", "living", arms=[45, 100])
S("L15.2", "S15b", "living", C("living", (0.65, 2.3, 1.38), -12, 1.5, 42, 3.0, push=0.12),
  {"me_d": {"pos": (0.65, 2.3), "yaw": -12, "expr": "forced", "sit": 0.66, "head": [0.0, 0.0]},
   "maya": {"pos": (-0.75, 2.3), "yaw": 6, "expr": "smirk", "sit": 0.66, "arms": [45, 100]}})
M("me_d", "L15.2+0.2", "living", head=[0.0, 0.25])
M("me_d", "L15.2+0.5", "living", head=[0.0, -0.1])
S("L16", "S16a", "diner", C("diner", (-1.15, 1.6, 1.1), 38, 2.4, 40, 10.0, push=0.12),
  {"me_d": {"pos": (-1.15, 1.6), "yaw": 90, "expr": "sneaky", "sit": 0.62, "arms": [0, 35],
            "held": held("phone", "me_d", (0.46, -0.35, 0.62), tilt=25)},
   "maya": {"pos": (1.15, 1.6), "yaw": -90, "expr": "smile", "sit": 0.62}})
M("me_d", "L16.1", "diner", head=[-0.4, 0.2])
cue("L16.3", "door", id="diner", open=True, dur=0.5)
S("L16.3", "S16b", "diner", C("diner", (4.2, 0.5, 1.2), 85, 2.8, 32, 3.0, push=0.12),
  {"nate": {"pos": (4.5, 0.4), "yaw": 90, "expr": "smile"}})
M("nate", "L16.3+0.9", "diner", pos=(3.0, 0.4), yaw=100)
cue("L17", "door", id="diner", open=False, dur=0.5)
cue("L17", "door", id="porch", open=True, dur=0.1)
S("L17", "S17a", "porch", C("porch", (0.0, -0.2, 1.2), 70, 4.0, 32, 3.0, push=0.12),
  {"nate": {"pos": (0.0, -1.6), "yaw": 180, "expr": "smile", "arms": [0, 0]},
   "me_d": {"pos": (0.0, -3.05), "yaw": 180, "expr": "forced", "arms": [80, 80]}})
M("nate", "L17.2", "porch", pos=(0.0, 1.6), yaw=180)
M("me_d", "L17.2", "porch", pos=(0.0, 0.15), yaw=180)
S("L17.2", "S17b", "porch", C("porch", (0.0, 0.3, 1.2), -60, 3.6, 30, 3.0, push=0.12),
  {"nate": {"pos": (0.0, -0.3), "yaw": 180, "expr": "laugh", "arms": [0, 0]},
   "me_d": {"pos": (0.0, -1.75), "yaw": 180, "expr": "forced", "arms": [80, 80]}})
M("nate", "L17.2+0.7", "porch", pos=(0.0, 1.5))
M("me_d", "L17.2+0.7", "porch", pos=(0.0, 0.05))
cue("L17.2+0.8", "door", id="porch", open=True, dur=0.1)
cue("L18", "show", id="balloons", on=True)
S("L18", "S18a", "yard", C("yard", (-0.08, 4.0, 1.2), 0, 3.9, 30, 3.0, push=0.12),
  {"maya": {"pos": (-0.8, 3.1), "yaw": 6, "expr": "laugh", "arms": [0, 0]},
   "nate": {"pos": (0.65, 3.1), "yaw": -8, "expr": "smile"}})
M("maya", "L18+0.2", "yard", arms=[25, 25])
M("nate", "L18+0.2", "yard", arms=[30, 30])
cue("L18", "show", id="cake", on=True)
S("L18.1", "S18b", "garage", C("garage", (-0.7, 2.0, 1.0), 10, 5.0, 28, 5.0, push=0.12, daz=-12),
  {"maya": {"pos": (0.0, 3.7), "yaw": 0, "expr": "laugh", "sit": 0.8, "arms": [60, 60]},
   "nate": {"pos": (-1.6, 0.4), "yaw": 150, "expr": "smile", "sit": 0.65}})
for i in range(8):
    a = [70, 20] if i % 2 == 0 else [20, 70]
    M("maya", f"L18.1+{0.12 + i * 0.13:.2f}", "garage", arms=a)
cue("L18.1", "show", id="balloons", on=False)
cue("L18.1", "show", id="cake", on=False)
S("L19", "S19a", "bowl", C("bowl", (0.0, 2.0, 1.1), 0, 4.0, 30, 12.0, push=0.1),
  {"maya": {"pos": (-0.72, 2.0), "yaw": 0, "expr": "smile"},
   "nate": {"pos": (0.72, 2.0), "yaw": 0, "expr": "smile", "arms": [40, 40],
            "held": held("bowlball", "nate", (0.0, -0.42, 0.85))}})
M("nate", "L19+0.35", "bowl", arms=[0, 40])
M("maya", "L19+0.35", "bowl", arms=[35, 0])
S("L19.2", "S19b", "beach", C("beach", (0.0, 5.5, 1.0), 0, 4.0, 30, 10.0, push=0.1),
  {"maya": {"pos": (-0.72, 5.5), "yaw": 6, "expr": "smile"},
   "nate": {"pos": (0.72, 5.5), "yaw": -6, "expr": "smile"}})
M("maya", "L19.2+0.1", "beach", arms=[0, 150])
S("L19.2+0.4", "S19c", "van", C("van", (0.0, 1.0, 1.1), 10, 4.0, 30, 3.0, push=0.1),
  {"maya": {"pos": (-0.73, 0.8), "yaw": 6, "expr": "smile", "arms": [75, 75]},
   "nate": {"pos": (0.73, 0.8), "yaw": -6, "expr": "smile", "arms": [75, 75],
            "held": held("movebox", "nate", (-0.55, -0.55, 0.95))}})
cue("L20", "ring", p=0.06)
S("L20", "S20a", "bench", C("bench", (-0.5, 4.2, 1.2), -4, 4.5, 32, 3.0, push=0.12),
  {"maya": {"pos": (-0.8, 3.3), "yaw": -4, "expr": "smile", "sit": 0.7},
   "nate": {"pos": (0.65, 3.3), "yaw": 4, "expr": "smile", "sit": 0.7},
   "me_d": {"pos": (-1.3, 6.5), "yaw": 6, "expr": "stunned", "arms": [0, 175]}})
S("L20.1", "S20b", "bench", C("bench", (-1.3, 6.5, 1.4), -50, 1.8, 36, 3.0, push=0.12),
  {"me_d": {"pos": (-1.3, 6.5), "yaw": -50, "expr": "stunned", "arms": [0, 175]},
   "maya": {"pos": (-0.8, 3.3), "yaw": -4, "expr": "laugh", "sit": 0.7},
   "nate": {"pos": (0.65, 3.3), "yaw": 4, "expr": "smile", "sit": 0.7}})
S("L21", "S21a", "street", C("street", (0.0, 2.6, 1.1), -4, 3.2, 30, 3.0, push=0.0, to=(1.0, 2.6, 1.1)),
  {"maya": {"pos": (-1.0, 2.6), "yaw": 88, "expr": "smile", "run": True,
            "held": [held("bouquet", "maya", (0.0, -0.42, 1.0)), held("swatches", "maya", (0.42, -0.35, 0.95))]}})
M("maya", "L21.1+0.25", "street", pos=(1.3, 2.6), yaw=88, arms=[45, 130], run=True)
S("L21.1+0.25", "S21b", "street", C("street", (2.0, 2.6, 1.15), -10, 2.6, 36, 3.0, push=0.0, to=(3.6, 2.6, 1.15)),
  {"maya": {"pos": (1.6, 2.6), "yaw": 88, "expr": "laugh", "arms": [45, 140], "run": True,
            "held": [held("bouquet", "maya", (0.0, -0.42, 1.0)), held("swatches", "maya", (0.42, -0.35, 0.95))]}})
M("maya", "L22", "street", pos=(3.6, 2.6), run=True)

S("L22", "S22a", "win", C("win", (0.2, 1.2, 1.4), 10, 2.2, 40, 2.0, push=0.12),
  {"me_d": {"pos": (0.0, 1.2), "yaw": 10, "expr": "worried", "arms": [0, 100],
            "held": held("card", "me_d", (0.44, -0.68, 1.4), s=1.4)}})
S("L22.1+0.2", "S22b", "win", C("win", (0.22, 1.2, 1.45), -8, 1.45, 50, 2.0, push=0.12),
  {"me_d": {"pos": (0.0, 1.2), "yaw": -8, "expr": "worried", "arms": [0, 100],
            "held": held("card", "me_d", (0.44, -0.68, 1.4), s=1.4)}})

# ---- S23 to S28: tonight, the rooftop wedding
S("L23", "S23a", "hand", HC(0.05, -0.083, 10, 0.16, 50, push=0.15), None)
hand_cues("L23", "me", "mine", "9:00")
S("L23.1+0.2", "S23b", "hand", HC(0.0, 0.074, -8, 0.22, 45, push=0.12), None)
hand_cues("L23.1+0.2", "me", "mine", "9:00")
cue("L24", "ring", p=0.38)
# S24a: the arch low from the aisle; the tally on the brass base sits low in the frame
S("L24", "S24a", "roof", C("roof", (-0.4, 11.5, 2.0), 8, 7.0, 26, -2.0, push=0.1), None)
S("L24.2", "S24b", "roof", C("roof", (-1.8, 10.6, 1.45), 14, 1.2, 45, 2.0, push=0.1),
  {"me": {"pos": (-1.8, 10.6), "yaw": 14, "expr": "nervous"},
   "nate_s": {"pos": (-0.55, 10.6), "yaw": 0, "expr": "nervous"}})
S("L24.3", "S24c", "roof", C("roof", (-1.17, 10.6, 1.4), 0, 3.9, 32, 3.0, push=0.12),
  {"me": {"pos": (-1.9, 10.6), "yaw": 10, "expr": "nervous"},
   "nate_s": {"pos": (-0.45, 10.6), "yaw": -10, "expr": "nervous"}})
GUESTS = {"g1": (-1.25, 4.07), "g2": (1.25, 4.07), "g3": (-1.25, 6.47), "g4": (1.25, 6.47), "g5": (-1.25, 8.87), "g6": (1.25, 8.87)}


def guests(expr, arms=None, yaw=180, names=None):
    out = {}
    for g_, p_ in GUESTS.items():
        if names and g_ not in names:
            continue
        d = {"pos": p_, "yaw": yaw, "expr": expr}
        if arms:
            d["arms"] = arms
        out[g_] = d
    return out


S("L25", "S25a", "roof", C("roof", (0.0, 6.0, 1.3), 180, 7.2, 30, 6.0, push=0.12, dz=0.0), guests("smile"))
S("L25+0.45", "S25b", "roof", C("roof", (-1.25, 8.87, 1.4), 170, 1.8, 36, 4.0, push=0.12), guests("smile", names=["g5", "g3"]))
S("L26", "S26", "roof", C("roof", (-1.8, 10.6, 1.4), -4, 1.55, 40, 2.0, push=0.12),
  {"me": {"pos": (-1.8, 10.6), "yaw": -4, "expr": "queasy", "arms": [40, 40]},
   "nate_s": {"pos": (-0.55, 10.6), "yaw": 0, "expr": "nervous"}})
M("me", "L26.1", "roof", arms=[0, 0], head=[0.0, 0.25])
S("L27", "S27a", "roof", C("roof", (0.0, 2.0, 1.2), 180, 3.8, 32, 3.0, push=0.0, to=(0.0, 3.4, 1.2)),
  {"maya_w": {"pos": (0.72, 1.2), "yaw": 180, "expr": "smile", "arms": [35, 35],
              "held": held("bouquet", "maya_w", (0.0, -0.42, 0.98))},
   "mdad": {"pos": (-0.72, 1.2), "yaw": 180, "expr": "polite"}})
M("maya_w", "L27.3", "roof", pos=(0.72, 3.2))
M("mdad", "L27.3", "roof", pos=(-0.72, 3.2))
S("L27.3", "S27b", "roof", C("roof", (-0.1, 6.9, 1.0), 175, 3.5, 32, 5.0, push=0.0, to=(-0.1, 7.6, 1.05)),
  {"maya_w": {"pos": (0.72, 6.4), "yaw": 180, "expr": "smile", "arms": [35, 35],
              "held": held("bouquet", "maya_w", (0.0, -0.42, 0.98))},
   "mdad": {"pos": (-0.72, 6.4), "yaw": 180, "expr": "polite"}})
M("maya_w", "L28", "roof", pos=(0.72, 7.5))
M("mdad", "L28", "roof", pos=(-0.72, 7.5))
S("L28", "S28a", "roof", C("roof", (0.0, 9.0, 1.4), 180, 1.1, 50, 2.0, push=0.1),
  {"maya_w": {"pos": (0.0, 9.0), "yaw": 180, "expr": "soft", "arms": [35, 35],
              "held": held("bouquet", "maya_w", (0.0, -0.42, 0.98))}})
S("L28.1", "S28b", "roof", C("roof", (0.0, 9.6, 1.45), 168, 0.95, 55, 2.0, push=0.1),
  {"maya_w": {"pos": (0.0, 9.6), "yaw": 175, "expr": "laugh", "arms": [35, 35],
              "held": held("bouquet", "maya_w", (0.0, -0.42, 0.98))}})
cue("L29", "watch", time="9:12")
S("L29", "S29", "hand", HC(0.05, -0.083, -10, 0.15, 50, push=0.14), None)
hand_cues("L29", "me", "mine", "9:12")
S("L30", "S30a", "roof", C("roof", (0.0, 10.7, 1.45), 180, 1.3, 45, 2.0, push=0.1),
  {"maya_w": {"pos": (0.0, 10.7), "yaw": 175, "expr": "worried", "arms": [35, 35],
              "held": held("bouquet", "maya_w", (0.0, -0.42, 0.98))}})
S("L30.2", "S30b", "roof", C("roof", (-0.98, 11.0, 1.4), 8, 3.5, 32, 2.0, push=0.1),
  {"nate_s": {"pos": (-0.25, 11.0), "yaw": 12, "expr": "nervous"},
   "me": {"pos": (-1.7, 11.0), "yaw": 0, "expr": "worried"}})
S("L31", "S31a", "roof", C("roof", (-1.7, 11.0, 1.5), -10, 1.2, 50, 2.0, push=0.12),
  {"me": {"pos": (-1.7, 11.0), "yaw": -10, "expr": "worried"}})
M("me", "L31.2", "roof", expr="squeeze", head=[0.1, 0.2])
S("L31.3", "S31b", "roof", C("roof", (-1.25, 8.87, 1.4), 172, 1.7, 36, 4.0, push=0.12), guests("wide", names=["g5", "g3"]))
S("L31.3+0.35", "S31c", "roof", C("roof", (1.25, 8.87, 1.4), 188, 1.7, 36, 4.0, push=0.12), guests("worried", names=["g6", "g4"]))
cue("L32", "watch", time="9:13")
S("L32", "S32", "hand", HC(0.05, -0.083, 10, 0.15, 50, push=0.14), None)
hand_cues("L32", "me", "mine", "9:13")
cue("L33", "tremble", amp=1.0)
S("L33", "S33a", "hand", C("hand", (0.0, 0.0, 1.2), 0, 0.3, 40, 38.0, push=0.12), None)
hand_cues("L33", "palm", None, "9:13", tremble=1.0)
S("L33.1", "S33b", "hand", C("hand", (0.0, 0.0, 1.27), 0, 0.14, 55, 42.0, push=0.15), None)
S("P01", "S33c", "hand", HC(0.05, -0.083, 0, 0.1, 50, push=0.12), None)
hand_cues("P01", "me", "mine", "9:13", tremble=0)
cue("P01", "wbar", p0=0.05, p1=1.0, dur=0.6)
S("L34", "S34", "hand", HC(0.05, -0.083, -6, 0.16, 50, push=0.14), None)
hand_cues("L34", "me", "mine", "9:14")
cue("L34", "petals", on=False)

# the ceremony
S("L35", "S35a", "roof", C("roof", (-0.4, 11.1, 1.3), 6, 5.4, 32, 3.0, push=0.12),
  {"officiant": {"pos": (0.0, 12.0), "yaw": 0, "expr": "smile", "side": [80, 80]},
   "maya_w": {"pos": (0.55, 10.6), "yaw": -90, "expr": "smile", "arms": [35, 35]},
   "nate_s": {"pos": (-0.55, 10.6), "yaw": 90, "expr": "smile"},
   "me": {"pos": (-1.75, 10.6), "yaw": 90, "expr": "worried"}})
S("L35.1", "S35b", "roof", C("roof", (0.0, 11.7, 1.55), -4, 1.3, 45, 2.0, push=0.1),
  {"officiant": {"pos": (0.0, 11.7), "yaw": 0, "expr": "delighted", "side": [150, 150]},
   "maya_w": {"pos": (0.55, 10.6), "yaw": -90, "expr": "smile"},
   "nate_s": {"pos": (-0.55, 10.6), "yaw": 90, "expr": "smile"}})
cue("L36", "petals", on=True)
S("L36", "S36a", "roof", C("roof", (0.0, 6.0, 1.5), 180, 7.2, 30, 6.0, push=0.12), guests("laugh", arms=[150, 150]))
S("L36+0.4", "S36b", "roof", C("roof", (1.25, 8.87, 1.6), 190, 2.0, 36, 3.0, push=0.12), guests("laugh", arms=[150, 150], names=["g6", "g4"]))
S("L37", "S37a", "roof", C("roof", (-0.8, 10.6, 1.2), 0, 4.8, 32, 3.0, push=0.12),
  {"maya_w": {"pos": (0.3, 10.7), "yaw": -60, "expr": "laugh", "arms": [70, 70]},
   "me": {"pos": (-1.0, 10.7), "yaw": 70, "expr": "stunned"},
   "nate_s": {"pos": (-1.9, 10.8), "yaw": 60, "expr": "smile"}})
M("maya_w", "L37+0.44", "roof", pos=(-0.25, 10.7), yaw=-80)
S("L37.1", "S37b", "roof", C("roof", (-0.9, 10.7, 1.3), 12, 3.6, 36, 2.0, push=0.12),
  {"maya_w": {"pos": (-0.25, 10.7), "yaw": -75, "expr": "laugh", "arms": [60, 60]},
   "me": {"pos": (-0.9, 10.7), "yaw": 80, "expr": "stunned", "arms": [45, 45]},
   "nate_s": {"pos": (-1.6, 10.9), "yaw": 70, "expr": "smile", "arms": [45, 45]}})
S("L37.2", "S37c", "roof", C("roof", (-0.5, 10.7, 1.3), -14, 3.0, 36, 2.0, push=0.12),
  {"maya_w": {"pos": (-0.5, 10.5), "yaw": 0, "expr": "laugh", "arms": [50, 50]},
   "me": {"pos": (0.15, 10.95), "yaw": -40, "expr": "soft", "arms": [45, 45]},
   "nate_s": {"pos": (-1.15, 10.95), "yaw": 40, "expr": "smile", "arms": [45, 45]}})
S("L38", "S38a", "roof", C("roof", (-0.5, 10.55, 1.5), -4, 1.0, 55, 2.0, push=0.1),
  {"maya_w": {"pos": (-0.5, 10.55), "yaw": 0, "expr": "smile", "arms": [70, 70]}})
S("L38.1", "S38b", "roof", C("roof", (-0.5, 10.55, 1.52), 10, 0.9, 55, 2.0, push=0.14),
  {"maya_w": {"pos": (-0.5, 10.55), "yaw": 8, "expr": "laugh", "arms": [70, 70]}})
S("L39", "S39a", "hand", HC(0.0, 0.074, 0, 0.26, 40, push=0.1), None)
hand_cues("L39", "me", "mine", "9:14")
S("L39.1", "S39b", "hand", HC(0.0, 0.074, -8, 0.15, 55, push=0.2, tx2=0.0, tz2=0.074), None)
# the reveal: the family photo, held with a slow push
cue("L40", "ring", p=1.0)
S("L40", "S40", "roof", C("roof", (0.0, 11.0, 1.25), 0, 4.9, 34, 3.0, push=0.14),
  {"nate_s": {"pos": (-1.0, 11.0), "yaw": 4, "expr": "smile", "side": [0, 12]},
   "maya_w": {"pos": (0.0, 10.9), "yaw": 0, "expr": "laugh", "side": [12, 12]},
   "me": {"pos": (1.0, 11.0), "yaw": -4, "expr": "soft", "side": [12, 0]}})
S("L41", "S41a", "roof", C("roof", (0.55, 10.9, 1.5), -10, 1.1, 50, 2.0, push=0.12),
  {"me": {"pos": (0.55, 10.9), "yaw": -10, "expr": "soft"}})
S("L41.1", "S41b", "roof", C("roof", (0.05, 10.9, 1.4), 0, 3.9, 40, 2.0, push=0.12),
  {"me": {"pos": (0.75, 10.9), "yaw": -8, "expr": "laugh"},
   "maya_w": {"pos": (-0.65, 10.9), "yaw": 8, "expr": "laugh", "side": [0, 55]}})
S("L42", "S42a", "roof", C("roof", (-0.3, 10.9, 1.35), 4, 1.7, 45, 2.0, push=0.12),
  {"maya_w": {"pos": (-0.3, 10.9), "yaw": 4, "expr": "smirk", "arms": [40, 40],
              "held": [held("bouquet", "maya_w", (-0.05, -0.42, 0.98)), held("cardhers", "maya_w", (0.05, -0.42, 1.12), dur=0.0)]}})
cue("L42.2", "held", obj="cardhers", who="maya_w", off=[0.12, -0.38, 1.38], dur=0.35, s=1.2)
S("L42.2", "S42b", "hand", HC(0.0, 0.074, 0, 0.26, 40, push=0.12), None)
hand_cues("L42.2", "hers", "hers", "9:11")
S("L43", "S43a", "hand", HC(0.0, 0.074, 10, 0.2, 45, push=0.1), None)
hand_cues("L43", "hers", "hers", "9:11")
S("L43.2", "S43b", "hand", HC(0.0, 0.074, 180, 0.15, 55, push=0.14), None)
hand_cues("L43.2", "hers", "hers", "9:11", rz=180, dur=0.35)
S("L43.4", "S43c", "hand", HC(0.0, 0.07, 180, 0.12, 55, push=0.3, tx2=0.0, tz2=0.067), None)
S("L44", "S44a", "roof", C("roof", (-0.3, 10.9, 1.4), 8, 1.2, 50, 2.0, push=0.12),
  {"maya_w": {"pos": (-0.3, 10.9), "yaw": 8, "expr": "smirk", "arms": [40, 70],
              "held": held("cardhers", "maya_w", (0.12, -0.38, 1.38), s=1.2)}})
M("maya_w", "L44+0.3", "roof", arms=[40, 100])
M("maya_w", "L44+0.6", "roof", arms=[40, 70])
S("L44.3", "S44b", "roof", C("roof", (0.3, 11.1, 1.4), -8, 3.4, 40, 2.0, push=0.1),
  {"maya_w": {"pos": (-0.3, 10.9), "yaw": 6, "expr": "smirk", "arms": [40, 70],
              "held": held("cardhers", "maya_w", (0.12, -0.38, 1.38), s=1.2)},
   "nate_s": {"pos": (1.0, 11.6), "yaw": -10, "expr": "laugh"}})
S("L44.5", "S44c", "roof", C("roof", (-0.3, 10.9, 1.5), 12, 0.95, 55, 2.0, push=0.12),
  {"maya_w": {"pos": (-0.3, 10.9), "yaw": 12, "expr": "smirk", "arms": [40, 70],
              "held": held("cardhers", "maya_w", (0.12, -0.38, 1.38), s=1.2)}})
S("L45", "S45a", "roof", C("roof", (-0.3, 10.9, 1.52), -6, 0.9, 55, 2.0, push=0.1),
  {"maya_w": {"pos": (-0.3, 10.9), "yaw": -6, "expr": "wide", "arms": [40, 70]}})
S("L45.2", "S45b", "roof", C("roof", (-0.3, 10.9, 1.5), 14, 1.1, 50, 2.0, push=0.12),
  {"maya_w": {"pos": (-0.3, 10.9), "yaw": 12, "expr": "smile", "arms": [40, 70]}})
S("L46", "S46a", "roof", C("roof", (0.75, 10.9, 1.52), -4, 0.95, 55, 2.0, push=0.1),
  {"me": {"pos": (0.75, 10.9), "yaw": -4, "expr": "stunned"}})
S("L46.1", "S46b", "roof", C("roof", (0.75, 10.9, 1.5), 12, 0.85, 55, 2.0, push=0.14),
  {"me": {"pos": (0.75, 10.9), "yaw": 12, "expr": "stunned"}})
cue("L47", "door", id="porch", open=True, dur=0.1)
S("L47", "S47a", "porch", C("porch", (0.0, 1.0, 1.3), 28, 4.8, 30, 4.0, push=0.12),
  {"nate": {"pos": (0.0, -1.1), "yaw": 180, "expr": "smile"},
   "me_d": {"pos": (-0.1, -2.55), "yaw": 180, "expr": "forced", "arms": [80, 80]},
   "maya": {"pos": (0.0, 3.2), "yaw": 0, "expr": "laugh", "arms": [40, 40]}})
M("nate", "L47.2", "porch", pos=(0.0, -0.3))
M("me_d", "L47.2", "porch", pos=(0.0, -1.75))
S("L47.2", "S47b", "porch", C("porch", (0.0, 3.2, 1.45), 0, 2.2, 55, 3.0, push=0.12),
  {"maya": {"pos": (0.0, 3.2), "yaw": 0, "expr": "laugh", "arms": [40, 40]}})
S("L48", "S48a", "roof", C("roof", (-0.3, 10.9, 1.5), 8, 1.0, 55, 2.0, push=0.1),
  {"maya_w": {"pos": (-0.3, 10.9), "yaw": 8, "expr": "laugh", "arms": [40, 70]}})
S("L48.2", "S48b", "roof", C("roof", (0.75, 10.9, 1.52), -10, 0.85, 55, 2.0, push=0.16),
  {"me": {"pos": (0.75, 10.9), "yaw": -10, "expr": "stunned"}})
cue("L49", "show", id="dinner", on=True)
S("L49", "S49a", "yard", C("yard", (0.0, 4.0, 1.2), 0, 4.4, 30, 3.0, push=0.12),
  {"maya": {"pos": (-1.0, 5.4), "yaw": 0, "expr": "laugh", "sit": 0.67},
   "nate": {"pos": (1.0, 5.4), "yaw": 0, "expr": "smile", "sit": 0.67},
   "me_d": {"pos": (0.0, 2.4), "yaw": 0, "expr": "forced", "arms": [0, 100],
            "held": held("card", "me_d", (0.44, -0.68, 1.4), s=1.4)}})
S("L49.1", "S49b", "yard", C("yard", (0.12, 2.4, 1.42), -10, 1.6, 42, 3.0, push=0.12),
  {"me_d": {"pos": (0.0, 2.4), "yaw": -10, "expr": "forced", "arms": [0, 100],
            "held": held("card", "me_d", (0.44, -0.68, 1.4), s=1.4)}})
S("L49.3", "S49c", "hand", HC(0.0, 0.0, 0, 0.34, 40, push=0.12), None)
hand_cues("L49.3", "me", "mine", "9:11")
cue("L49.3", "card", face="mine", rz=0, dur=0.01)

# --------------------------------------------------------------------------------------------- finish
for n in cast:
    acting[n].append((0.0, 0, {"at": 0, "pos": [0, 0], "hidden": True, "yaw": 0, "expr": "neutral"}))
final_acting = {}
for n, ks in acting.items():
    ks.sort(key=lambda a: (a[0], a[1]))
    final_acting[n] = [k for _, _, k in ks]

out_shots = []
for i, s in enumerate(shots):
    d = {"id": s["id"], "cam": s["cam"], "hand": s["hand"], "step": s["step"]}
    if i:
        d["at"] = s["at"]
    out_shots.append(d)
# sort the shots by time (they were written in order; check)
_ts = [T(s.get("at", 0)) for s in out_shots]
assert _ts == sorted(_ts), [(s["id"], t) for s, t in zip(out_shots, _ts)]

# ------------------------------------------------------------------------------------------------ sound and music
cue("L49.3-0.01", "ring", p=1.0)
cues.sort(key=lambda c: T(c["at"]))

sfx = [
    {"at": "L01.4", "kind": "thud", "db": -14},               # the hit on ENDS
    {"at": "L03+0.25", "kind": "click", "db": -17},          # the card lands on the mat
    {"at": "L16.3", "kind": "door", "db": -20},              # the diner door
    {"at": "L29+0.05", "kind": "click", "db": -15},          # one watch tick each: 9:12, 9:13, 9:14
    {"at": "L32+0.05", "kind": "click", "db": -15},
    {"at": "P01+0.1", "kind": "click", "db": -13, "keep": True},
    {"at": "L34+0.05", "kind": "click", "db": -12},
    {"at": "L36", "kind": "bubbles", "db": -23, "dur": 1.6},   # a soft crowd cheer
]
music = {
    "root": 47, "mode": "major", "bpm": 108, "seed": 96,
    "sections": [
        {"at": 0, "voices": ["pulse", "pad"], "energy": 0.4},
        {"at": "L14", "voices": ["piano", "pad", "pulse"], "energy": 0.5},
        {"at": "L22", "voices": ["pulse", "pad"], "energy": 0.3},
        {"at": "L23", "voices": ["pad", "piano"], "energy": 0.5},
        {"at": "L29", "voices": ["pulse", "pad"], "energy": 0.65},
        {"at": "L35", "voices": ["pad", "piano", "choir"], "energy": 0.85},
        {"at": "L37", "voices": ["pad", "piano", "pulse"], "energy": 0.55},
    ],
}
story = {
    "rev": 8,
    "staging_ok": ["S35a/vows face to face, arms down", "S37a/the group hug (Maya pulls me in)", "S37b/the group hug", "S37c/the group hug", "S40/family photo, arms around shoulders"],
    "slug": "ep96-friend-card",
    "title": "My Card Says We Stop Being FRIENDS",
    "made_for_kids": False,
    "premise": ("Everybody gets one card at eighteen that says how their closest friendship ends, and the cards are never wrong. "
                "Mine says my best friend Maya and I stop being friends at 9:14 tonight, and on the back, in tiny writing, it won't hurt. "
                "For ten years I have never been alone with her, bringing my big brother Nate to everything. Tonight is June twelfth, "
                "on a rooftop, in a suit."),
    "twist": ("Nate is marrying Maya, and at 9:14 she becomes my sister: the card never said we would fight, only that we would "
              "stop being friends. Her card says the same, she worked out what it meant at eighteen and never told me, and every June "
              "twelfth she makes me read mine out loud."),
    "world": ("A flat city rooftop at sunset with white folding chairs, a flower arch with a brass base, string lights and water "
              "towers on the skyline, and ten years of sunny day scenes: a mail slot hall, a parking lot, two lawns, an airport gate, a curb, a diner."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffb38a",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "look": {"style": "closer", "fog": "#ffd9bd", "fog_density": 0.012, "fog_start": 16.0, "sky": "#ffc9a3", "sky_strength": 1.0,
             "hdri": "kloppenheim_06_puresky", "hdri_strength": 0.5, "hdri_rotation": 0, "hdri_visible": False,
             "exposure": 0.0, "flash_safe": True,
             "polish": {"reveal": ["L40", "L41"], "quiet": [["L40", "L41"]]}},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.01, -0.02], "saturation": 1.3, "contrast": 1.04,
              "vignette": 0.2, "bloom": 0.3, "grain": 0.008},
    "phonemes": {"Reyes": "ɹˈAz"},
    "asr_forgive": ["nine fourteen", "nine twelve", "nine thirteen", "twelfth", "mister reyes"],
    "rain_shots": ["S20a", "S20b", "S22a", "S22b"],
    "clip_ok": ["petal"],
    "cast": cast,
    "lines": lines,
    "shots": out_shots,
    "acting": final_acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": {"floor": "concrete", "steps_db": -22,
              "ambience": [{"kind": "traffic", "from": "L23", "to": "end", "lufs": -40}],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "P01>"}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(out_shots)} shots, {len(cues)} cues)")
