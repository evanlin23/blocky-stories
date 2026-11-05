"""Writes ../story.json for ep97 "prize bears" (script.md, 2026-11-03). Run: python stories/ep97-prize-bears/generator/make_story.py

The words are in lines.json (every line of the script). Coordinates (metres): x east, y away from the street (the glass
door is at y = -1, the prize counter at y = 9, the closet door at x 4.1, y 11), z up. A character facing -y has yaw 0,
+x 90, -x -90, +y 180. The camera on the street/arcade-front side looks +y and sees fronts at yaw 0.
Shots are numbered by the script's S numbers; every shot starts on a line reference (chunk numbers are the script's own).
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
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
    if ln["id"] == "L22":     # the 0.6 s music drop before the closet
        lines.append({"id": "P01", "pause": 0.6, "chunks": []})


def remap(ref):
    if not isinstance(ref, str):
        return ref
    mm = re.match(r"^(L\d+):(\d+)(.*)$", ref)      # "L22:1" is the caption chunk after the script's own splitting
    if mm:
        return f"{mm.group(1)}.{mm.group(2)}{mm.group(3)}"
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
           hat="none", hat_c="#333333", extras=(), eyes="round", brow_w=1.0, sleeves="long", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c,
         "face": {"eyes": eyes, "brows": True, "ink": "#16100c"}}
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
    "me": person("#e0a878", "#6b7a3a", "#1c1c22", "#3fe7ff", hair="mop", hair_c="#3a2618", collar="#f2f2f2", brow_w=1.9),
    "tess": person("#e0a878", "#e0a31c", "#1f2f6a", "#f5f5f5", hair="cap", hair_c="#c0602a", pattern="knit",
                   pattern_c="#c68a10", eyes="lashes", brow_w=1.9),
    "prize": person("#f0c8a0", "#f5f5f5", "#3a3f4c", "#2b2b2b", hair="swoop", hair_c="#f2f2f2", extras=["glasses"],
                    vest="#2fc4d8"),
    "ticket_man": person("#c98f66", "#7a8590", "#33343c", "#d8d8d8", hair="cap", hair_c="#1c1a18", hat="ballcap",
                         hat_c="#d83a3a"),
    "hockey_a": person("#f0c8a0", "#2f9a4a", "#2a2f3c", "#f0f0f0", hair="spiky", hair_c="#5a3a22"),
    "hockey_b": person("#a9714a", "#2a5bd7", "#4a4036", "#3a2a1a", hair="buzz", hair_c="#1c1a18", pattern="stripes",
                       pattern_c="#f5f5f5", sleeves="short"),
    "jackpot_lady": person("#e8b890", "#b79cf0", "#4a4a58", "#8a6a9a", hair="long", hair_c="#a0a0a6", eyes="lashes"),
    "stranger": person("#8a5a3a", "#4a8bd8", "#2a2f3c", "#e8e8e8", hair="buzz", hair_c="#101010"),
}
EXPR = {"smile": "smile", "laugh": "laugh", "sheepish": "polite", "soft": "soft", "blink": "wide", "knowing": "smirk",
        "focus": "neutral", "neutral": "neutral", "worried": "worried", "scared": "scared", "grin": "grin",
        "shut": "shut", "wide": "wide"}

# ---------------------------------------------------------------------------------------------- acting helpers
acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0]}] for n in cast}
last = {n: [0, 0] for n in cast}
vis = {n: False for n in cast}


def _ex(kw):
    kw = dict(kw)
    if "expr" in kw:
        kw["expr"] = EXPR.get(kw["expr"], kw["expr"])
    return kw


def put(who, at, pos, yaw=0, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False, "yaw": yaw, "arms": [0, 0], "side": [0, 0], "head": [0, 0],
         "lean": 0, "expr": "neutral"}
    k.update(_ex(kw))
    acting[who].append(k)
    last[who] = p
    vis[who] = True


def walk(who, at, pos, **kw):
    p = list(pos)
    k = {"at": at, "pos": p}
    k.update(_ex(kw))
    acting[who].append(k)
    last[who] = p


def hold(who, at, **kw):
    """Change expression, arms, head, lean or yaw at `at` without touching position (a walk carries on)."""
    acting[who].append({"at": at, **_ex(kw)})


def scene(at, **actors):
    """Everyone not named is hidden from `at`; the named appear (jump) at their pos."""
    for n in cast:
        if n in actors:
            put(n, at, **actors[n])
        elif vis[n]:
            acting[n].append({"at": at, "hidden": True})
            vis[n] = False


# ---------------------------------------------------------------------------------------------- cues
cues = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def obj(id_, at, pos=None, yaw=0.0, dur=0.0, hide=False, scale=None):
    c = {"at": at, "name": "obj", "id": id_}
    if pos is not None:
        c["pos"] = list(pos)
        c["yaw"] = yaw
    if dur:
        c["dur"] = dur
    if hide:
        c["hide"] = True
    if scale is not None:
        c["scale"] = scale
    cues.append(c)


def shimmer(at, pos, d, dur=1.4):
    cue(at, "shimmer", pos=list(pos), dir=list(d), dur=dur)


def tickets(at, n, bear=False):
    cue(at, "tickets", n=n, bear=bear)


def fdoor(at, angle, frm, dur=0.4):
    cue(at, "fdoor", angle=angle, **{"from": frm}, dur=dur)


def cdoor(at, angle, frm, dur=0.5):
    cue(at, "cdoor", angle=angle, **{"from": frm}, dur=dur)


# ---------------------------------------------------------------------------------------------- cameras
shots = []


def C(p0, t0, lens, p1=None, t1=None, lens1=None):
    ks = [[0, list(p0), list(t0), lens]]
    if p1 is not None:
        ks.append([1, list(p1), list(t1 if t1 is not None else t0), lens1 or lens])
    return ks


def S(id_, at, cam, **kw):
    sh = {"id": id_, "cam": cam}
    if at is not None:
        sh["at"] = at
    sh.update(kw)
    shots.append(sh)


# ============================================================================================== the film
cue(0, "look", id="sun", dur=0.4)
cue(0, "weather", kind="")
cue(0, "fdoor", angle=0.0, **{"from": 0.0}, dur=0.4)
tickets(0, 0)
# the ever-present items
obj("card", 0, hide=True)
obj("car", 0, pos=(3.2, -6.4, 0.0))

# ---- S01 L01: the board, close, push. Nobody.
S("S01", None, C((-3.1, 7.85, 1.95), (-3.1, 10.73, 1.92), 35, (-3.1, 8.5, 1.95), (-3.1, 10.73, 1.92), 35), hand=0.004)
scene(0)
# ---- S02a L02.0-1: me in front of the board, cyan-lit
S("S02a", "L02", C((-2.5, 7.3, 1.72), (-3.1, 9.7, 1.62), 40, (-2.8, 7.6, 1.72), (-3.1, 9.7, 1.62), 40), hand=0.006)
scene("L02", me=dict(pos=(-3.1, 9.6), yaw=0, expr="worried", head=[-10, 0]))
hold("me", "L02+0.9", head=[14, 3])
# ---- S02b L02.2: the glass door from inside; a passer outside
S("S02b", "L02.2", C((0.2, 3.6, 1.5), (0, -1.0, 1.35), 30, (0.1, 2.6, 1.5), (0, -1.0, 1.35), 30))
scene("L02.2", stranger=dict(pos=(-3.4, -3.2), yaw=-90, expr="neutral"))
walk("stranger", "L03-0.05", (3.4, -3.2))
# ---- S03a L03.0-1: low at the door; sneakers step out
fdoor("L03-0.35", 95.0, 0.0)
S("S03a", "L03", C((-0.5, 1.7, 0.3), (0.1, -0.8, 0.45), 30, (-0.3, 1.1, 0.3), (0.1, -1.0, 0.45), 30), hand=0.006)
scene("L03", stranger=dict(pos=(0.35, 2.4), yaw=180 + 180, expr="neutral"))
walk("stranger", "L03.2", (0.1, -0.6))
# ---- S03b L03.2: outside, blinking twice, the shimmer slides off
S("S03b", "L03.2", C((-1.6, -4.4, 1.35), (0.15, -1.6, 1.4), 35, (-1.2, -4.0, 1.35), (0.2, -1.8, 1.4), 35))
shimmer("L03.2", (0.1, -1.3, 1.5), (0, 1.1, 0.1), 1.3)
scene("L03.2", stranger=dict(pos=(0.1, -0.9), yaw=0, expr="neutral"))
hold("stranger", "L03.2+0.15", expr="shut")
hold("stranger", "L03.2+0.28", expr="neutral")
hold("stranger", "L03.2+0.42", expr="shut")
walk("stranger", "L03.2+0.7", (0.4, -2.3), expr="neutral")
# ---- S04a L04.0-1: the ticket man walks out with a fistful
obj("fist", "L04", pos=(0, 0, 0))
S("S04a", "L04", C((1.4, -5.2, 1.4), (0.2, -1.8, 1.25), 32, (1.0, -4.6, 1.4), (0.2, -2.4, 1.3), 32))
scene("L04", ticket_man=dict(pos=(0.1, -0.6), yaw=0, expr="neutral", arms=[0, 1.3]))
walk("ticket_man", "L04.2", (0.4, -3.0))
# ---- S04b L04.2: close, blinking twice, no idea why
S("S04b", "L04.2", C((0.5, -5.1, 1.62), (0.4, -3.0, 1.58), 35, (0.45, -4.6, 1.62), (0.4, -3.0, 1.58), 35), hand=0.006)
scene("L04.2", ticket_man=dict(pos=(0.4, -3.0), yaw=0, expr="worried", arms=[0, 1.3], head=[8, 0]))
hold("ticket_man", "L04.2+0.35", expr="shut", arms=[0, 1.3])
hold("ticket_man", "L04.2+0.5", expr="worried", head=[-8, 0])
hold("ticket_man", "L04.2+0.8", expr="shut")
hold("ticket_man", "L04.2+0.95", expr="worried", head=[6, 2])
# ---- S05a L05.0-1: two guys arguing at air hockey
obj("fist", "L05", hide=True)
S("S05a", "L05", C((-1.6, -0.2, 1.5), (-1.6, 3.2, 1.4), 24, (-1.6, 0.4, 1.5), (-1.6, 3.2, 1.4), 24), hand=0.01)
scene("L05", hockey_a=dict(pos=(-2.3, 2.4), yaw=35, expr="angry", arms=[0, 1.45], head=[25, 0]),
      hockey_b=dict(pos=(-0.9, 2.4), yaw=-35, expr="angry", arms=[1.45, 0], head=[-25, 0]))
hold("hockey_a", "L05+0.25", arms=[0, 1.9], head=[20, -4])
hold("hockey_b", "L05+0.2", arms=[1.9, 0], head=[-20, -4])
hold("hockey_a", "L05+0.5", arms=[0, 1.45], head=[30, 4])
hold("hockey_b", "L05+0.6", arms=[1.5, 0], head=[-30, 4])
# ---- S05b L05.2: the chrome rim, two orange strokes (the lore tally), a puck sliding past
obj("puck", "L05.2-0.2", pos=(-1.4, 5.0, 0.76))
obj("puck", "L05.2", pos=(-1.1, 3.0, 0.76), dur=1.0)
S("S05b", "L05.2", C((-0.3, 2.55, 1.0), (-1.03, 3.45, 0.87), 50, (-0.55, 3.15, 0.99), (-1.03, 3.45, 0.87), 50), hand=0.006, cfill=2.0)
scene("L05.2")
# ---- S05c L05.3: neither knows; they leave
obj("puck", "L05.3", hide=True)
S("S05c", "L05.3", C((0.1, 4.5, 1.65), (0, 0.2, 1.4), 32, (0.0, 3.6, 1.65), (0, -0.6, 1.4), 32))
scene("L05.3", hockey_a=dict(pos=(0.75, 0.9), yaw=180 + 180, expr="worried", side=[0.5, 0.5]),
      hockey_b=dict(pos=(-0.75, 1.3), yaw=0, expr="worried", side=[0.5, 0.5]))
walk("hockey_a", "L06-0.05", (0.6, -2.0))
walk("hockey_b", "L06-0.05", (-0.6, -2.2))
# ---- S06a L06.0: the jackpot lady wins
obj("ladytix", "L06", pos=(0, 0, 0))
S("S06a", "L06", C((3.7, 6.3, 1.95), (1.7, 4.0, 1.6), 32, (3.3, 5.9, 1.9), (1.7, 4.0, 1.6), 32), hand=0.01)
scene("L06", jackpot_lady=dict(pos=(1.7, 3.3), yaw=180, expr="smile", arms=[2.4, 2.4]))
hold("jackpot_lady", "L06+0.3", arms=[2.7, 2.2], expr="laugh")
hold("jackpot_lady", "L06+0.6", arms=[2.2, 2.7])
# ---- S06b L06.1: walks out
S("S06b", "L06.1", C((0.4, 3.0, 1.55), (0.1, -0.8, 1.35), 32, (0.3, 2.4, 1.55), (0.1, -1.0, 1.35), 32))
scene("L06.1", jackpot_lady=dict(pos=(0.5, 0.5), yaw=0, expr="smile", arms=[0, 0.9]))
walk("jackpot_lady", "L06.2", (0.1, -1.2))
# ---- S06c L06.2: and walks right back in
S("S06c", "L06.2+0.3", C((0.1, 2.9, 1.55), (0.1, -1.5, 1.45), 32, (0.15, 2.3, 1.55), (0.1, -1.5, 1.45), 32))
shimmer("L06.2+0.6", (0.2, -1.2, 1.6), (0, 1.0, 0), 1.2)
scene("L06.2+0.3", jackpot_lady=dict(pos=(0.1, -3.2), yaw=180, expr="smile", arms=[0, 0.9]))
walk("jackpot_lady", "L07-0.05", (0.15, 0.9))
# ---- S07a L07.0-1: four boards, three blank
obj("ladytix", "L07", hide=True)
S("S07a", "L07", C((-7.3, 8.3, 1.9), (-6.9, 10.7, 1.9), 28, (-4.4, 8.3, 1.9), (-4.3, 10.7, 1.9), 28), hand=0.004)
scene("L07")
# ---- S07b L07.2: except mine
S("S07b", "L07.2", C((-3.1, 7.7, 1.75), (-3.1, 10.2, 1.85), 34, (-3.1, 8.3, 1.75), (-3.1, 10.2, 1.85), 34))
scene("L07.2", me=dict(pos=(-3.1, 9.4), yaw=0, expr="neutral", head=[0, 0]))
# ---- S08a L08.0: Tess at her car, keys up
tickets("L08", 0)
obj("keys", "L08", pos=(0, 0, 0))
obj("crown", "L08", pos=(0, 0, 0))
S("S08a", "L08", C((1.6, -11.0, 1.5), (2.6, -6.4, 1.2), 28, (1.8, -10.0, 1.5), (2.6, -6.4, 1.2), 28), hand=0.008)
scene("L08", tess=dict(pos=(2.0, -6.4), yaw=0, expr="smile", arms=[0, 2.4]))
hold("tess", "L08+0.5", arms=[0, 2.8], expr="laugh")
# ---- S08b L08.1: me beside her, same brows and cowlick
S("S08b", "L08.1", C((1.1, -9.0, 1.5), (1.15, -6.0, 1.4), 32, (1.1, -8.3, 1.5), (1.15, -6.0, 1.4), 32), hand=0.006)
scene("L08.1", tess=dict(pos=(1.7, -6.0), yaw=0, expr="smile", arms=[0, 2.4]),
      me=dict(pos=(0.6, -6.0), yaw=0, expr="neutral"))
hold("tess", "L08.1+0.5", arms=[0, 2.0], head=[-10, 0])
hold("me", "L08.1+0.4", head=[12, 0], expr="smile")
# ---- S09a L09.0-1: walking to the door
S("S09a", "L09", C((-1.6, -8.4, 1.35), (0.9, -3.4, 1.3), 32, (-1.2, -7.2, 1.35), (0.9, -2.8, 1.3), 32))
scene("L09", tess=dict(pos=(1.7, -6.0), yaw=0, expr="smile"), me=dict(pos=(0.7, -6.4), yaw=0, expr="smile"))
walk("tess", "L09.2-0.1", (0.9, -2.2))
walk("me", "L09.2-0.1", (0.1, -3.0))
# ---- S09b L09.2: Tess holds the door open for me
fdoor("L09.2-0.2", 95.0, 0.0, 0.4)
S("S09b", "L09.2", C((0.0, 2.5, 1.6), (0.4, -1.9, 1.5), 30, (0.1, 1.8, 1.6), (0.4, -1.9, 1.5), 30))
scene("L09.2", tess=dict(pos=(0.85, -2.0), yaw=180 + 180, expr="smile", arms=[0, 1.3]),
      me=dict(pos=(-0.2, -3.4), yaw=180, expr="smile"))
walk("me", "L10-0.05", (-0.2, 0.7))
# ---- S10a L10.0: at the counter looking up
S("S10a", "L10", C((-0.1, 5.4, 1.9), (0.2, 10.2, 2.0), 30, (0.0, 6.3, 1.9), (0.2, 10.2, 2.1), 30))
scene("L10", tess=dict(pos=(0.9, 7.9), yaw=180, expr="smile", arms=[0, 2.7], head=[0, -25]),
      me=dict(pos=(-0.1, 7.9), yaw=180, expr="neutral", head=[0, -22]))
# ---- S10b L10.1: tilt up the prize wall to the giant bear
S("S10b", "L10.1", C((0.2, 8.0, 1.0), (0, 10.5, 1.1), 35, (0.2, 8.0, 1.2), (0, 10.5, 3.0), 35), cfill=1.4)
scene("L10.1")
# ---- S11 L11: the number card
obj("card", "L11", pos=(0.35, 8.82, 1.11))
S("S11", "L11", C((0.0, 7.6, 1.4), (0.35, 8.8, 1.28), 40, (0.2, 8.0, 1.3), (0.35, 8.82, 1.28), 40), hand=0.006)
scene("L11")
# ---- S12a L12.0-2: the prize man looks up over his glasses
S("S12a", "L12", C((-0.4, 7.2, 1.75), (0.1, 9.6, 1.68), 34, (-0.2, 7.9, 1.75), (0.1, 9.6, 1.68), 34), hand=0.006)
scene("L12", prize=dict(pos=(0.3, 9.6), yaw=0, expr="knowing", head=[0, 18]))
hold("prize", "L12+0.5", head=[-6, -6])
obj("card", "L12.3", hide=True)
# ---- S12b L12.3: me, half turning to Tess
S("S12b", "L12.3", C((0.6, 10.2, 1.75), (-0.3, 8.0, 1.62), 34, (0.5, 9.9, 1.75), (-0.3, 8.0, 1.62), 34), hand=0.006)
scene("L12.3", me=dict(pos=(-0.3, 8.0), yaw=180, expr="neutral", head=[-30, 0]),
      tess=dict(pos=(1.0, 8.0), yaw=180, expr="smile"))
hold("me", "L12.3+0.3", head=[-45, 0], yaw=140)
# ---- S13 L13: Tess laughs a little too fast
S("S13", "L13", C((0.0, 10.2, 1.75), (1.0, 8.0, 1.65), 34, (0.3, 9.9, 1.75), (1.0, 8.0, 1.65), 34), hand=0.006)
scene("L13", tess=dict(pos=(1.0, 8.0), yaw=180, expr="sheepish", head=[0, 0]))
hold("tess", "L13+0.5", expr="sheepish", head=[-35, 4])
# ---- S14a L14.0: Tess on a stool, holding my jacket
obj("jacket", "L14", pos=(0, 0, 0))
S("S14a", "L14", C((3.4, -0.35, 1.45), (2.3, 0.8, 1.2), 32, (3.2, -0.3, 1.45), (2.3, 0.8, 1.2), 32), hand=0.008)
scene("L14", tess=dict(pos=(2.3, 0.6, -0.12), yaw=90, expr="soft", head=[0, 2]),
      me=dict(pos=(3.4, 1.3), yaw=180, expr="focus", arms=[1.0, 1.0]))
hold("me", "L14+0.3", arms=[1.5, 1.3])
# ---- S14b L14.1: she just watches me
S("S14b", "L14.1", C((3.2, 0.3, 1.5), (2.3, 0.7, 1.45), 45, (3.0, 0.45, 1.5), (2.3, 0.7, 1.5), 45), hand=0.006)
scene("L14.1", tess=dict(pos=(2.3, 0.6, -0.12), yaw=90, expr="soft", head=[0, 2]),
      me=dict(pos=(3.5, 1.4), yaw=180, expr="focus", arms=[1.3, 1.3]))
hold("me", "L14.1+0.3", arms=[1.0, 1.0])
hold("tess", "L14.1+0.4", head=[6, 0])
# ---- S15a L15.0: skee-ball, the throw
obj("jacket", "L15", hide=True)
tickets("L15", 1200)
S("S15a", "L15", C((2.4, -0.3, 1.7), (3.4, 2.8, 0.9), 30, (2.7, 0.1, 1.6), (3.4, 3.2, 0.8), 30), hand=0.008)
scene("L15", me=dict(pos=(3.4, 0.7), yaw=180, expr="focus", arms=[0.5, 0.5]))
hold("me", "L15+0.1", arms=[-0.3, -0.3], lean=-8)
hold("me", "L15+0.28", arms=[1.4, 1.4], lean=16)
hold("me", "L15+0.5", arms=[0.5, 0.5], lean=0)
obj("ball", "L15+0.27", pos=(3.4, 1.0, 0.9))
obj("ball", "L15+0.3", pos=(3.4, 6.2, 0.45), dur=1.1)
# ---- S15b L15.1: the ball rolls up the lane
obj("ball", "L15.1+0.14", pos=(3.2, 2.0, 0.45))
obj("ball", "L15.1+0.15", pos=(3.4, 6.5, 0.5), dur=1.2)
S("S15b", "L15.1+0.15", C((4.2, 2.6, 0.5), (3.4, 4.0, 0.4), 32, (4.0, 3.6, 0.5), (3.4, 5.6, 0.45), 32), hand=0.006)
scene("L15.1+0.15")
# ---- S16a L16.0: good, in the cabinet's glow
obj("ball", "L16", hide=True)
tickets("L16", 3400)
S("S16a", "L16", C((-6.2, 2.9, 1.65), (-6.1, 4.8, 1.55), 35, (-6.2, 3.3, 1.65), (-6.1, 4.8, 1.55), 35), hand=0.008)
scene("L16", me=dict(pos=(-5.9, 4.8), yaw=-60, expr="focus", arms=[1.4, 1.4], head=[-20, 4]))
hold("me", "L16+0.2", arms=[1.5, 1.3])
hold("me", "L16+0.4", arms=[1.3, 1.5])
# ---- S16b L16.1: the screen blooms orange
cue("L16.1", "win", on=True)
tickets("L16.1", 5100)
S("S16b", "L16.1", C((-5.6, 4.8, 1.55), (-6.77, 4.8, 1.52), 22, (-5.9, 4.8, 1.55), (-6.77, 4.8, 1.52), 22), cfill=0.3, hand=0.004)
scene("L16.1", me=dict(pos=(-5.4, 5.8), yaw=-90, expr="grin", arms=[1.2, 1.4]))
# ---- S17a L17.0-1: hands over two buttons
cue("L17.2", "win", on=False)
tickets("L17", 6400)
S("S17a", "L17", C((-6.3, 3.3, 1.3), (-6.35, 4.75, 1.15), 35, (-6.3, 3.6, 1.25), (-6.35, 4.75, 1.15), 35), hand=0.006)
scene("L17", me=dict(pos=(-5.75, 4.75), yaw=-90, expr="focus", arms=[1.4, 1.45]))
hold("me", "L17+0.15", arms=[1.5, 1.35])
hold("me", "L17+0.3", arms=[1.35, 1.5])
hold("me", "L17+0.45", arms=[1.5, 1.35])
hold("me", "L17+0.6", arms=[1.35, 1.5])
hold("me", "L17+0.75", arms=[1.5, 1.35])
# ---- S17b L17.2: a ribbon of tickets spilling out
tickets("L17.2", 8800)
obj("ribbon", "L17.2", pos=(-6.5, 4.8, 0.06), yaw=90, scale=0.2)
obj("ribbon", "L17.2+0.05", pos=(-6.5, 4.8, 0.06), yaw=90, scale=1.0, dur=1.0)
S("S17b", "L17.2", C((-5.7, 3.9, 0.75), (-6.3, 4.8, 0.3), 32, (-5.5, 4.5, 0.6), (-6.2, 4.8, 0.2), 32), hand=0.006)
scene("L17.2")
# ---- S18 L18: the rule meter fills the frame, rolling to 10,000
obj("ribbon", "L18", hide=True)
tickets("L18", 9400)
tickets("L18+0.35", 9800)
tickets("L18.1", 10000)
S("S18", "L18", C((3.4, 5.4, 0.95), (3.4, 6.7, 1.0), 40, (3.4, 5.7, 0.98), (3.4, 6.7, 1.0), 40), hud="big", cfill=0.6)
scene("L18")
# ---- S19a L19.0: tickets slide across the counter; S19b L19.1: he doesn't look up
tickets("L19", 10000)
obj("tix", "L19", pos=(-1.6, 8.6, 1.12), yaw=0)
obj("tix", "L19+0.05", pos=(-0.2, 8.6, 1.12), dur=0.9)
S("S19a", "L19", C((-0.9, 7.6, 1.55), (-0.3, 8.9, 1.15), 36, (-0.4, 7.9, 1.5), (-0.3, 9.0, 1.15), 36), hand=0.006)
scene("L19", prize=dict(pos=(-0.2, 9.6), yaw=0, expr="neutral", head=[0, 28], arms=[0.8, 0.8]))
hold("prize", "L19+0.25", arms=[0.5, 1.1])
S("S19b", "L19.1", C((0.2, 8.1, 1.78), (-0.2, 9.6, 1.62), 40, (0.1, 8.5, 1.78), (-0.2, 9.6, 1.62), 40), hand=0.006)
scene("L19.1", prize=dict(pos=(-0.2, 9.6), yaw=0, expr="neutral", head=[0, 30], arms=[0.5, 1.1]))
hold("prize", "L19.1+0.3", arms=[1.1, 0.5])
# ---- S20 L20: "Same as always?" already turning away
S("S20", "L20", C((-0.3, 7.9, 1.7), (0.2, 9.5, 1.65), 36, (-0.1, 8.5, 1.7), (0.2, 9.5, 1.65), 36), hand=0.006)
obj("tix", "L20", hide=True)
scene("L20", prize=dict(pos=(0.1, 9.6), yaw=0, expr="neutral", head=[0, 6]))
hold("prize", "L20.1", yaw=0, head=[10, 0])
hold("prize", "L20.1+0.9", yaw=140, head=[0, 0])
# ---- S21a L21.0: he goes for one from the back
S("S21a", "L21", C((1.6, 7.6, 1.5), (2.2, 9.9, 1.45), 30, (2.4, 7.9, 1.5), (3.0, 10.0, 1.45), 30))
scene("L21", prize=dict(pos=(0.5, 9.9), yaw=90, expr="neutral"))
walk("prize", "L21.1", (3.1, 9.95))
# ---- S21b L21.1: through the plain back door
cdoor("L21.1+0.3", 24.0, 0.0, 1.6)   # he opens it only a slice, his body fills the gap
S("S21b", "L21.1", C((3.9, 7.8, 1.5), (4.0, 11.0, 1.35), 32, (4.0, 8.6, 1.5), (4.1, 11.2, 1.35), 32))
scene("L21.1", prize=dict(pos=(3.2, 9.95), yaw=90, expr="neutral"))
walk("prize", "L21.1+0.5", (4.1, 10.3))
walk("prize", "L22", (4.1, 12.5))
# ---- S22a L22.0: the door ajar, a slice of warm bulb light
S("S22a", "L22", C((1.2, 6.4, 1.6), (3.7, 10.8, 1.3), 30, (1.9, 6.9, 1.6), (3.8, 10.8, 1.3), 30), hand=0.006)
scene("L22", me=dict(pos=(3.0, 9.7), yaw=180, expr="worried", lean=4))
hold("me", "L22+0.4", lean=14)
# ---- S22b L22.1: I lean to look
S("S22b", "L22:1+0.3", C((4.4, 7.9, 1.85), (3.5, 9.9, 1.55), 36, (4.2, 8.4, 1.8), (3.5, 9.9, 1.55), 36), hand=0.008)
scene("L22:1+0.3", me=dict(pos=(3.4, 9.6), yaw=180, expr="worried", head=[100, 0], lean=0))
hold("me", "L22:1+0.6", head=[75, 0], lean=12)
# ---- the drop: the dark slice of the door
S("S22c", "P01", C((1.6, 7.4, 1.6), (3.6, 10.2, 1.35), 30, (1.9, 7.8, 1.6), (3.6, 10.2, 1.35), 30), hand=0.004)
scene("P01", me=dict(pos=(3.4, 9.6), yaw=180, expr="worried", head=[75, 0], lean=12))
# ---- S23a L23.0: through the door into the closet
cdoor("L23", 88.0, 24.0, 0.5)
S("S23a", "L23", C((4.1, 9.9, 1.55), (4.1, 13.5, 1.5), 28, (4.1, 11.3, 1.55), (4.1, 14.5, 1.5), 28), hand=0.004, cfill=0.15)
scene("L23")
# ---- S23b L23.1: full
S("S23b", "L23.1", C((4.1, 12.0, 1.5), (4.1, 16.0, 1.5), 30, (4.1, 12.5, 1.5), (4.1, 16.0, 1.5), 28), hand=0.004, cfill=0.15)
scene("L23.1")
# ---- S24a / S24b
S("S24a", "L24", C((4.1, 12.4, 1.35), (4.1, 16.0, 1.5), 28, (4.1, 13.5, 1.35), (4.1, 16.0, 1.5), 28), hand=0.004, cfill=0.15)
scene("L24")
S("S24b", "L24.1", C((4.1, 13.6, 0.7), (4.1, 16.0, 0.8), 30, (4.1, 13.9, 0.8), (4.1, 16.0, 3.3), 30), hand=0.004, cfill=0.15)
scene("L24.1")
# ---- S25 L25: forty; the meter shows 40 and a bear
tickets("L25", 40, True)
S("S25", "L25", C((4.1, 11.5, 2.3), (4.1, 15.0, 1.7), 24, (4.1, 11.9, 2.1), (4.1, 15.0, 1.7), 24), hand=0.004, cfill=0.15)
scene("L25")
# ---- S26a L26.0-1 / S26b L26.2: ears and tags
S("S26a", "L26", C((3.3, 15.0, 1.15), (3.45, 16.0, 1.1), 36, (4.7, 14.95, 1.15), (4.5, 16.0, 1.1), 36), hand=0.004, cfill=0.9)
scene("L26")
S("S26b", "L26.2", C((3.9, 15.3, 1.18), (3.91, 15.96, 1.12), 40, (3.9, 15.5, 1.12), (3.91, 15.96, 1.1), 40), hand=0.003, cfill=1.2)
scene("L26.2")
# ---- S27a L27.0: the tag, tight; S27b L27.1: me, scared, in the doorway
S("S27a", "L27", C((3.91, 15.55, 1.1), (3.91, 15.96, 1.1), 42, (3.91, 15.68, 1.1), (3.91, 15.96, 1.1), 42), hand=0.0025, cfill=1.5)
scene("L27")
S("S27b", "L27.1", C((4.1, 14.2, 1.6), (4.1, 11.4, 1.58), 32, (4.1, 13.5, 1.6), (4.1, 11.4, 1.58), 32), hand=0.008, cfill=0.4)
scene("L27.1", me=dict(pos=(4.1, 11.6), yaw=180, expr="scared", head=[0, 0]))
hold("me", "L27.1+0.3", lean=-6, head=[8, -3])
# ---- S28a L28.0-1: Tess at the counter behind me (over my shoulder)
S("S28a", "L28", C((4.1, 12.3, 1.6), (2.6, 7.7, 1.5), 30, (4.0, 11.9, 1.6), (2.6, 7.7, 1.5), 30), cfill=0.3, hand=0.01)
scene("L28", tess=dict(pos=(2.5, 7.6), yaw=180, expr="soft", head=[20, 0]))
# ---- S28b L28.2: close on Tess, caught
S("S28b", "L28:2", C((3.4, 10.2, 1.62), (2.5, 7.6, 1.5), 34, (3.1, 9.9, 1.62), (2.5, 7.6, 1.5), 34), hand=0.006)
scene("L28:2", tess=dict(pos=(2.5, 7.6), yaw=180, expr="soft", head=[25, 0]))
hold("tess", "L28:2+0.3", head=[-5, 3], expr="soft")
# ---- S29: the same spot, sun, rain, leaves
cue("L29", "look", id="sun", dur=0.4)
S("S29a", "L29", C((0.2, -15.0, 1.4), (3.0, -6.6, 1.0), 32, (0.8, -13.8, 1.4), (3.0, -6.6, 1.0), 32), hand=0.008)
scene("L29")
cue("L29+0.6", "look", id="rain", dur=0.4)
cue("L29+0.6", "weather", kind="rain")
S("S29b", "L29+0.6", C((6.4, -14.0, 1.6), (3.2, -6.6, 1.0), 32, (5.6, -13.0, 1.6), (3.2, -6.6, 1.0), 32), hand=0.012)
scene("L29+0.6")
cue("L29+1.2", "look", id="leaf", dur=0.4)
cue("L29+1.2", "weather", kind="leaf")
S("S29c", "L29+1.2", C((0.4, -13.5, 1.0), (3.2, -6.6, 0.9), 32, (1.2, -12.5, 0.9), (3.2, -6.6, 0.9), 32), hand=0.008)
scene("L29+1.2")
# ---- S30a L30.0-1: I win it every time
cue("L30", "look", id="sun", dur=0.4)
cue("L30", "weather", kind="")
tickets("L30", 40, True)
obj("bear_me", "L30", pos=(0, 0, 0))
S("S30a", "L30", C((0.5, 10.1, 1.75), (0.0, 8.0, 1.6), 34, (0.4, 9.6, 1.75), (0.0, 8.0, 1.6), 34), hand=0.008)
scene("L30", me=dict(pos=(0.0, 8.0), yaw=180, expr="grin", arms=[1.45, 1.45]))
hold("me", "L30+0.4", arms=[1.6, 1.6], lean=-4)
# ---- S30b L30.2-3: at the door I lose it
S("S30b", "L30.2", C((-1.7, -4.3, 1.5), (0.2, -1.4, 1.5), 35, (-1.3, -3.9, 1.5), (0.2, -1.7, 1.5), 35))
obj("bear_me", "L30.2", hide=True)
shimmer("L30.2+0.2", (0.1, -1.2, 1.6), (0, 1.1, 0.1), 1.4)
scene("L30.2", me=dict(pos=(0.1, -0.7), yaw=0, expr="grin"))
hold("me", "L30.2+0.3", expr="shut")
hold("me", "L30.2+0.45", expr="worried")
hold("me", "L30.2+0.6", expr="shut")
hold("me", "L30.2+0.75", expr="worried")
walk("me", "L30.2+1.0", (0.3, -2.4))
# ---- S31a L31.0: Tess never plays; S31b L31.1: she remembers every one
S("S31a", "L31", C((3.3, 2.7, 1.55), (2.3, 0.7, 1.35), 32, (3.1, 2.3, 1.5), (2.3, 0.7, 1.35), 32), hand=0.008)
scene("L31", tess=dict(pos=(2.3, 0.6, -0.12), yaw=90, expr="soft", head=[0, 2]))
S("S31b", "L31.1", C((3.2, 0.2, 1.52), (2.3, 0.7, 1.5), 45, (2.9, 0.4, 1.5), (2.3, 0.7, 1.5), 45), hand=0.006)
scene("L31.1", tess=dict(pos=(2.3, 0.6, -0.12), yaw=90, expr="soft", head=[-10, 0]))
hold("tess", "L31.1+0.5", head=[12, -2])
# ---- S32a L32.0-1: she leaves every bear here
obj("bear_tess", "L32", pos=(0, 0, 0))
S("S32a", "L32", C((2.4, 8.7, 1.6), (0.2, 8.7, 1.4), 34, (2.1, 8.7, 1.6), (0.2, 8.7, 1.4), 34), hand=0.008)
scene("L32", tess=dict(pos=(0.2, 8.0), yaw=180, expr="sheepish", arms=[1.4, 1.4]),
      prize=dict(pos=(0.2, 9.5), yaw=0, expr="knowing", arms=[0.9, 0.9]))
hold("tess", "L32+0.6", arms=[1.5, 1.5])
# ---- S32b L32.2: the prize man carries it to the closet
obj("bear_tess", "L32.2", hide=True)
obj("bear_prize", "L32.2", pos=(0, 0, 0))
S("S32b", "L32.2", C((3.8, 8.8, 1.55), (4.0, 11.0, 1.35), 32, (4.1, 9.3, 1.55), (4.1, 11.4, 1.35), 32))
scene("L32.2", prize=dict(pos=(3.0, 9.95), yaw=90, expr="neutral", arms=[1.4, 1.4]))
walk("prize", "L32.2+0.7", (4.1, 10.4))
walk("prize", "L33", (4.1, 12.4))
# ---- S33: because to me it's always the first time
obj("bear_prize", "L33", hide=True)
obj("bear_me", "L33", pos=(0, 0, 0))
cdoor("L33", 24.0, 88.0, 0.5)
S("S33a", "L33", C((-0.2, 5.5, 1.6), (-0.2, 7.2, 1.45), 34, (-0.2, 6.0, 1.6), (-0.2, 7.2, 1.45), 34), hand=0.008)
scene("L33", me=dict(pos=(-0.8, 7.2), yaw=90, expr="smile", arms=[1.4, 1.4]),
      tess=dict(pos=(0.4, 7.2), yaw=-90, expr="smile", arms=[0.4, 0.4]))
S("S33b", "L33.1", C((-0.5, 5.5, 1.65), (0.4, 7.2, 1.62), 40, (-0.1, 5.8, 1.65), (0.4, 7.2, 1.62), 40), hand=0.006)
obj("bear_me", "L33.1", hide=True)
obj("bear_tess", "L33.1", pos=(0, 0, 0))
scene("L33.1", tess=dict(pos=(0.4, 7.2), yaw=-90, expr="soft", arms=[1.0, 1.0]),
      me=dict(pos=(-0.8, 7.2), yaw=90, expr="smile"))
S("S33c", "L33.2", C((-0.8, 5.5, 1.65), (-0.8, 7.2, 1.62), 40, (-0.8, 5.9, 1.65), (-0.8, 7.2, 1.62), 40), hand=0.006)
scene("L33.2", me=dict(pos=(-0.8, 7.2), yaw=0, expr="smile"))
hold("me", "L33.2+0.3", head=[10, 0])
S("S33d", "L33.3-0.15", C((3.8, 3.2, 1.8), (0.0, 8.0, 1.2), 28, (3.0, 3.8, 1.7), (0.0, 8.0, 1.2), 28), hand=0.01)
scene("L33.3-0.15", me=dict(pos=(-0.6, 8.0), yaw=180, expr="smile"), tess=dict(pos=(0.6, 8.0), yaw=180, expr="smile"))
hold("tess", "L33.3+0.1", arms=[0, 1.2])
S("S33e", "L33.4", C((0.3, 5.9, 1.65), (0.4, 7.6, 1.62), 40, (0.35, 6.3, 1.65), (0.4, 7.6, 1.62), 40), hand=0.006)
scene("L33.4", tess=dict(pos=(0.4, 7.6), yaw=0, expr="laugh", head=[0, 0]))
hold("tess", "L33.4+0.3", head=[-10, 2], expr="soft")
S("S33f", "L33.5", C((-0.6, 5.4, 1.62), (-0.6, 7.4, 1.6), 40, (-0.6, 6.0, 1.62), (-0.6, 7.4, 1.6), 40), hand=0.006)
scene("L33.5", me=dict(pos=(-0.6, 7.4), yaw=0, expr="smile"))
hold("me", "L33.5+0.4", head=[-8, 2], expr="soft")
# ---- S34a L34.0: the glass door, sun, the shimmer on its frame
tickets("L34", 0)
obj("bear_me", "L34", hide=True)
obj("bear_tess", "L34", hide=True)
cue("L34", "fdoor", angle=0.0, **{"from": 95.0}, dur=0.5)
shimmer("L34", (0.9, -0.7, 1.4), (0, 0.5, 0.25), 1.4)
S("S34a", "L34", C((0.4, 3.4, 1.5), (0, -1.0, 1.45), 30, (0.2, 2.4, 1.5), (0, -1.0, 1.45), 30))
scene("L34")
# ---- S34b L34.2: from whoever played last
S("S34b", "L34.1", C((2.0, 5.3, 1.7), (1.7, 3.2, 1.5), 32, (1.9, 4.9, 1.7), (1.7, 3.2, 1.5), 32), hand=0.008)
scene("L34.1", me=dict(pos=(1.7, 3.2), yaw=180, expr="soft", head=[-12, 0]))
hold("me", "L34.1+0.5", head=[10, 3])
# ---- S35a L35.0: a token slides across to Tess
obj("token", "L35", pos=(-0.24, 8.72, 1.13))
obj("token", "L35+0.05", pos=(-0.09, 8.72, 1.13), dur=0.5)
S("S35a", "L35", C((-0.165, 9.35, 1.3), (-0.165, 8.72, 1.13), 30, (-0.165, 9.33, 1.3), (-0.165, 8.72, 1.13), 30), hand=0.001)
scene("L35", tess=dict(pos=(0.8, 8.0), yaw=180, expr="smile", head=[0, 25]))
S("S35b", "L35.1", C((0.7, 9.6, 1.65), (0.8, 8.0, 1.62), 38, (0.7, 9.55, 1.65), (0.8, 8.0, 1.62), 38), hand=0.006)
scene("L35.1", tess=dict(pos=(0.8, 8.0), yaw=180, expr="smile", head=[0, 22]))
hold("tess", "L35.1+0.4", head=[0, 0], expr="laugh")
# ---- S36 L36: she's terrible
obj("token", "L36", hide=True)
obj("ring", "L36", pos=(-4.3, 2.5, 1.25))
obj("ring", "L36+0.05", pos=(-4.18, 3.18, 0.96), dur=0.45)
obj("ring", "L36+0.5", pos=(-3.8, 3.5, 0.2), dur=0.3)
S("S36", "L36", C((-4.0, 5.2, 1.65), (-4.3, 3.0, 1.2), 34, (-4.1, 4.7, 1.62), (-4.3, 3.0, 1.2), 34), hand=0.01)
scene("L36", tess=dict(pos=(-4.3, 2.2), yaw=180, expr="laugh", arms=[0, 1.6]))
hold("tess", "L36+0.35", arms=[0, 0.4], head=[0, 8])
# ---- S37a L37.0: she won me; S37b L37.1: a tiny rubber duck
obj("ring", "L37", hide=True)
obj("duck", "L37", pos=(0.2, 8.5, 1.12))
S("S37b", "L37", C((0.1, 7.8, 1.32), (0.2, 8.5, 1.16), 45, (0.3, 8.0, 1.25), (0.2, 8.5, 1.15), 45), hand=0.004)
scene("L37")
# ---- S38a L38.0-1: at the door she steps into the sun
obj("duck", "L38", hide=True)
obj("handduck", "L38", pos=(0, 0, 0))
fdoor("L38-0.3", 95.0, 0.0)
S("S38a", "L38", C((-1.6, -4.3, 1.5), (0.2, -1.2, 1.5), 35, (-1.2, -3.9, 1.5), (0.2, -1.6, 1.5), 35))
shimmer("L38+0.3", (0.1, -1.2, 1.6), (0, 1.1, 0.1), 1.3)
scene("L38", tess=dict(pos=(0.1, -0.5), yaw=0, expr="smile", arms=[0, 0.9]))
walk("tess", "L38.2", (0.3, -2.3))
# ---- S38b L38.2-3: she blinks, and asks where we'd been
S("S38b", "L38.2", C((0.4, -5.4, 1.62), (0.35, -3.0, 1.6), 36, (0.4, -4.7, 1.62), (0.35, -3.0, 1.6), 36), hand=0.006)
scene("L38.2", tess=dict(pos=(0.35, -3.0), yaw=0, expr="blink", arms=[0, 0.9], head=[0, 0]),
      me=dict(pos=(1.3, -3.1), yaw=-20, expr="worried"))
hold("tess", "L38.2+0.12", expr="shut", arms=[0, 0.9])
hold("tess", "L38.2+0.28", expr="blink", head=[-15, 0])
hold("tess", "L38.3", head=[10, 4], expr="worried")
# ---- S39a L39.0-1: the car, I tell her
obj("handduck", "L39", hide=True)
S("S39a", "L39", C((70.0, 2.5, 1.5), (70.0, 0.0, 1.3), 30, (70.0, 2.1, 1.5), (70.0, 0.0, 1.3), 30), hand=0.01)
scene("L39", tess=dict(pos=(69.5, 0.1, -0.5), yaw=180, expr="smile", arms=[1.25, 1.25], head=[0, 0]),
      me=dict(pos=(70.7, 0.1, -0.5), yaw=140, expr="smile", head=[0, 0]))
hold("me", "L39+0.4", head=[-15, 0], arms=[0.6, 0.0])
hold("tess", "L39+0.7", head=[-18, 0], expr="laugh")
# ---- S39b L39.2: every Saturday; the duck on the dash
S("S39b", "L39.2", C((69.8, 2.0, 1.4), (69.9, 0.95, 1.1), 36, (69.8, 1.7, 1.35), (69.9, 0.95, 1.1), 36), hand=0.01)
scene("L39.2", tess=dict(pos=(69.5, 0.1, -0.5), yaw=180, expr="smile", arms=[1.25, 1.25], head=[-12, 0]))
# ---- S40 L40: now I always call her back
tickets("L40", 0)
S("S40", "L40", C((40.2, 0.9, 1.25), (40.0, 3.9, 1.2), 35, (40.1, 1.5, 1.25), (40.0, 3.9, 1.2), 35), hand=0.008)
obj("phone", "L40", pos=(0, 0, 0))
scene("L40", me=dict(pos=(40.0, 3.7, -0.2), yaw=0, expr="smile", arms=[0, 2.75], head=[-8, 0]))
hold("me", "L40+0.5", head=[8, 2], expr="smile")
# ---- S41 L41: we take turns
obj("phone", "L41", hide=True)
obj("token", "L41", pos=(1.2, 1.3, 1.12))
S("S41", "L41", C((1.75, 3.35, 1.45), (1.75, 0.6, 1.15), 21, (1.75, 3.1, 1.45), (1.75, 0.6, 1.15), 21), hand=0.01)
scene("L41", tess=dict(pos=(1.2, 0.6, -0.12), yaw=180, expr="laugh", arms=[0, 1.6]),
      me=dict(pos=(2.3, 0.6, -0.12), yaw=180, expr="smile", head=[-25, 0]))
hold("tess", "L41+0.4", arms=[0, 1.0], expr="smile")
# ---- S42a L42.0: next Saturday, the car pulls in
obj("token", "L42", hide=True)
tickets("L42", 0)
cue("L42", "look", id="sun", dur=0.4)
obj("car", "L42-0.01", pos=(3.2, -11.5, 0.0))
obj("car", "L42", pos=(3.2, -6.4, 0.0), dur=1.2)
S("S42a", "L42", C((0.8, -18.0, 1.5), (3.2, -8.5, 1.0), 24, (1.4, -17.0, 1.5), (3.2, -8.0, 1.0), 24), hand=0.008)
scene("L42")
# ---- S42b L42.1: we walk toward the door
S("S42b", "L42.1+0.2", C((0.4, -9.3, 1.55), (1.4, -4.0, 1.4), 32, (0.6, -8.4, 1.55), (1.2, -3.0, 1.4), 32), hand=0.01)
scene("L42.1+0.2", tess=dict(pos=(2.1, -5.3), yaw=180, expr="smile"), me=dict(pos=(1.0, -5.3), yaw=180, expr="smile"))
walk("tess", "L43-0.05", (0.9, -1.8))
walk("me", "L43-0.05", (0.0, -1.8))
# ---- S43a L43.0: I walk in
fdoor("L43-0.4", 95.0, 0.0)
S("S43a", "L43", C((0.0, 3.4, 1.55), (0.1, -1.4, 1.5), 30, (0.0, 2.6, 1.55), (0.1, -1.4, 1.5), 30), hand=0.008)
scene("L43", me=dict(pos=(0.1, -3.0), yaw=180, expr="smile"))
walk("me", "L43.1", (0.1, 0.9))
# ---- S43b L43.1: and look up (ends on S01's framing)
S("S43b", "L43.1+0.15", C((-3.1, 5.8, 1.7), (-3.1, 8.6, 1.0), 35, (-3.1, 7.85, 1.95), (-3.1, 10.73, 1.92), 35), hand=0.003)
scene("L43.1+0.15", me=dict(pos=(-3.1, 7.4), yaw=180, expr="neutral", head=[0, -25]))
walk("me", "L43.1+0.6", (-5.0, 7.4))

# portrait frames are narrow: pull face shots back and aim at eye level
EXC = {"S41", "S42a", "S12b", "S13", "S30a", "S28b", "S01", "S07a", "S10a", "S10b", "S18", "S23a", "S23b", "S24a", "S24b", "S25", "S26a", "S26b", "S27a", "S27b", "S22c",
       "S05b", "S11", "S16b", "S17a", "S17b", "S15b", "S35a", "S37b", "S39b", "S19a"}
for sh in shots:
    if sh["id"] in EXC:
        continue
    for k in sh["cam"]:
        p, t = k[1], k[2]
        dx, dy, dz = p[0] - t[0], p[1] - t[1], p[2] - t[2]
        dist = (dx * dx + dy * dy + dz * dz) ** 0.5
        if dist < 3.3 and 1.3 <= t[2] <= 2.0:
            f = 1.0 + 0.45 * (3.3 - dist) / 3.3 + 0.2
            k[1] = [round(t[0] + dx * f, 3), round(t[1] + dy * f, 3), round(p[2] - 0.05, 3)]
            k[2] = [t[0], t[1], round(t[2] - 0.12, 3)]

# ---------------------------------------------------------------------------------------------- sound and music
sfx = [
    {"at": "L01.2", "kind": "hit", "db": -6, "dur": 0.9},
    {"at": "L18", "kind": "click", "db": -16, "dur": 0.4},
    {"at": "L22", "kind": "creak", "db": -14, "dur": 1.0},
]
music = {
    "root": 48, "mode": "major", "bpm": 140, "seed": 97,
    "sections": [
        {"at": 0, "voices": ["pulse", "piano"], "energy": 0.6, "root": 48, "mode": "major"},
        {"at": "L23", "voices": ["drone", "pulse"], "energy": 0.4, "root": 48, "mode": "minor"},
        {"at": "L32", "voices": ["drone", "pad"], "energy": 0.3, "root": 48, "mode": "major"},
        {"at": "L34", "voices": ["pulse", "piano", "pad"], "energy": 0.5, "root": 48, "mode": "major"},
        {"at": "L42", "voices": ["pulse"], "energy": 0.25, "root": 60, "mode": "major"},
    ],
}
sound = {
    "floor": "carpet", "steps_db": -22,
    "ambience": [
        {"kind": "room", "from": 0, "to": "end", "lufs": -40},
        {"kind": "hum", "from": "L23", "to": "L33", "lufs": -36},
    ],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>", "keep": ["creak"]}],
}

story = {
    "slug": "ep97-prize-bears",
    "title": "This Arcade Takes MEMORIES, Not Coins \U0001F579️",
    "made_for_kids": False,
    "premise": ("At a bright arcade every game costs you the memory of ever coming there, taken at the door from whoever "
                "played last, so my name is on every high score and I have never played, and my big sister brings me for her "
                "birthday to win the giant bear on the top shelf."),
    "twist": ("She has brought me every Saturday for forty weeks; I win her the same bear every time and lose the "
              "afternoon at the door, while she never plays and keeps every one. The door only takes from whoever played last, "
              "so I hand her my last token and now I remember the day for both of us."),
    "world": ("A sunny arcade with grape violet carpet, cyan and orange cabinets, skee-ball lanes, an air hockey table, "
              "a coin pusher, a white prize counter, a wall of plush and a back closet full of forty identical giant bears."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff9a1f",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "look": {"style": "closer", "flash_safe": True, "polish": {"twist": "L28", "reveal": ["L25", "L31"],
                                                                   "sway": ["S27b", "S28a"], "hold": ["S22a", "S22c", "S41", "S42a", "S17a"]},
             "fog": "#dfe9ff", "fog_density": 0.004, "fog_start": 20.0, "sky": "#bfe3ff", "sky_strength": 1.0,
             "exposure": 0.0},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.015, -0.02], "saturation": 1.1, "contrast": 1.04,
              "vignette": 0.18, "bloom": 0.25, "grain": 0.009},
    "set_moves": ["S05b", "S15a", "S15b", "S17b", "S19a", "S29b", "S35a", "S36", "S42a", "S03b", "S30b", "S34a", "S38a",
                  "S16b", "S18", "S06c", "S06a"],
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "rev": 4,
    "asr_forgive": ["thousand"],
    "clip_ok": ["S03b", "S04a", "S30b", "S38a", "S06c", "S34a"],
}
for it in (sfx, music["sections"], sound["music_drops"], sound["ambience"], cues, story["shots"]):
    remap_all(it)
for lst in acting.values():
    remap_all(lst)
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
