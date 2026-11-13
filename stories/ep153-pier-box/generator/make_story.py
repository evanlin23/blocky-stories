"""Writes ../story.json for ep153 "pier box" (script.md, 2026-11-13, batch 15). Run: python stories/ep153-pier-box/generator/make_story.py

The words are in lines.json; places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90; a camera `az` degrees round from the south looks at a character who faces it with yaw = az.
Time references use the script's own chunk numbers (remap() turns them into the split captions').
The v3 look (batch 15 override): big block heads, hair as the silhouette, flat exaggerated faces.
Day is one sun, never switched mid-shot. Dusk (S11, and the garage from L27) changes only on a cut.
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
REV = 1
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = T.split_lines(orig_lines)
# the 0.6 s music drop before L19, and the 3.5 s hold on the question after L30
idx = next(i for i, l in enumerate(lines) if l["id"] == "L19")
lines.insert(idx, {"id": "P00", "pause": 0.6, "chunks": [["", ""]]})
lines.append({"id": "P01", "pause": 3.5, "chunks": [["1 or 2?", ""]]})


def remap(ref):
    if not isinstance(ref, str):
        return ref
    mm = re.match(r"^(L\d+b?)\.(\d+)(.*)$", ref)
    if mm and mm.group(1) in CHUNKMAP:
        return f"{mm.group(1)}.{CHUNKMAP[mm.group(1)][int(mm.group(2))]}{mm.group(3)}"
    return ref


def remap_all(items):
    for it in items:
        for key in ("at", "from", "to"):
            if key in it:
                it[key] = remap(it[key])


D2R = math.pi / 180


def person(skin, shirt, pants, shoes, hair, hair_c, brow_w=1.3, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": shoes,
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "face": {"brows": True, "ink": "#1c120c", "brow_w": brow_w},
         "outline": 0.06}
    d.update(kw)
    return d


cast = {
    # me, 22: a yellow rain jacket (hood down), a big brown swoop; the blue pen is clipped to the pocket (set.py)
    "me": person("#f1c9a0", "#ffd23f", "#3d5a85", "#e8e4dc", "swoop", "#6a4630", brow_w=1.5, extras=["hooddown"]),
    # Ty, 22: very tall, a red hoodie, a black flat-top as tall as a brick
    "ty": person("#8a5a3a", "#e8433a", "#2f3a52", "#f4f4f2", "flattop", "#15110f", height=1.2, extras=["hooddown"]),
    # Old Hal, ~75: a white block beard, bald under a bucket hat (set.py), a khaki shirt and an olive fishing vest (set.py)
    "hal": person("#e8b890", "#d8cfa8", "#5a5a48", "#5a4a3a", "bald", "#f4f4f0", features=["beard"], brow_w=1.6),
    # Bea, ~40: a big high bun, a teal blazer over a white collar, gold earrings (set.py)
    "bea": person("#b97a52", "#1fa9a0", "#2a2f45", "#3a2a22", "bigbun", "#2a1a12", hair_c2="#f2c84a",
                  collar="#fbfbf6", brow_w=1.1),
}
acting = {n: [] for n in cast}
last = {n: [0, 0] for n in cast}
cues = []
SH = []


def key(who, at, pos=None, **kw):
    p = list(pos) if pos is not None else list(last[who])
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def cut(who, at, pos=None, **kw):
    """A key that takes effect at once (no blend): a pose or place that changes on a cut."""
    p = list(pos) if pos is not None else list(last[who])
    acting[who].append({"at": at, "pos": list(last[who]), "blend": 0.0})
    key(who, at, p, blend=0.0, **kw)


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def cam(tx, ty, tz, d, az, lens, el=0.0, push=None):
    """A camera d metres from (tx, ty, tz), az degrees round from the south, el metres above the target, looking at
    it. One key (the polish pack adds the slow push) or, with push=d2, two keys (a push to d2)."""
    def at_(dd):
        cx = tx + dd * math.sin(az * D2R)
        cy = ty - dd * math.cos(az * D2R)
        return [round(cx, 3), round(cy, 3), round(tz + el * dd / d, 3)], [tx, ty, tz]
    p, t_ = at_(d)
    keys = [[0, p, t_, lens]]
    if push:
        p2, t2 = at_(push)
        keys.append([1, p2, t2, lens])
    return keys


def shot(sid, at, camera, **kw):
    SH.append((sid, at, camera, kw))


# where the rule tag (the corner copy of the box) shows: every shot the real box isn't big in
TAG_OFF = set()
# where the light is dusk
DUSK = set()


# ----------------------------------------------------------------------------------------------- the cast at rest
far = {"me": (-20, -40), "ty": (-24, -40), "hal": (-28, -40), "bea": (-32, -40)}
for n in cast:
    key(n, 0, far[n], yaw=0, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0], lean=0)

BX, BY = G.BOX
MX, MY = G.ME_BOX
FZ = 1.75          # a standing adult's face centre (v3 head)
TZ = 2.1           # Ty's

cue(0, "lid", o=0.0)
cue(0, "c1", p=0)
cue(0, "c2", p=0)
cue(0, "q", u=0.0)
cue(0, "bread", u=0.0)

# ===== 01 the rule (L01 to L03)
cut("me", 0, (MX, MY), yaw=0, expr="nervous", head=[8, 0], arms=[0, 0], side=[0, 0])
TAG_OFF.add("S01a")
shot("S01a", 0, cam(-0.62, MY, 1.45, 3.9, 6, 32, el=0.15))
cut("me", "L01.3", (MX, MY), yaw=0, expr="nervous", head=[0, 6], arms=[0, 62])
cue("L01.3", "c1", p=1)
TAG_OFF.add("S01b")
shot("S01b", "L01.3", cam(MX + 0.1, MY, 1.4, 3.2, -6, 32, el=0.1))
cut("me", "L02", (MX, MY), yaw=0, expr="neutral", head=[18, -4], arms=[0, 0], side=[0, 62])
cue("L02", "c1", p=0)
TAG_OFF.add("S02")
shot("S02", "L02", cam(-0.5, MY, 1.3, 3.0, 14, 32, el=0.25))
cut("me", "L03", (MX, MY), yaw=0, expr="shocked", head=[0, 6], arms=[0, 62], side=[0, 0])
cue("L03", "c1", p=2)
cue("L03", "c2", p=3)
shot("S03a", "L03", cam(MX + 0.15, MY, 1.45, 3.2, 4, 32, el=0.1))
key("me", "L03.1", expr="shocked", head=[0, -6], blend=0.3)
shot("S03b", "L03.1", cam(MX, MY, FZ, 2.9, -6, 34))

# ===== 02 Ty and the bike (L04 to L06)
TX, TY_ = G.TY_RAIL
cue("L04", "c1", p=0)
cue("L04", "c2", p=0)
cut("me", "L04", (1.9, 7.9), yaw=-90, expr="nervous", head=[-25, 0], arms=[0, 0], side=[0, 0])
cut("ty", "L04", (1.9, 6.1), yaw=-90, expr="delighted", head=[0, 10], arms=[0, 40])
key("ty", "L04.1", arms=[0, 150], blend=0.35)
key("ty", "L04.2", arms=[0, 60], blend=0.4)
cue("L04.1", "bread", u=1.0, dur=1.2)
shot("S04", "L04", cam(1.9, 7.0, 1.9, 6.6, -90, 30, el=0.2))
cut("me", "L05", (G.ME_G[0], G.ME_G[1]), yaw=-20, expr="delighted", head=[-10, 0], arms=[0, 0], side=[0, 0])
cut("ty", "L05", far["ty"], yaw=0)
key("me", "L05.1", yaw=-20, side=[25, 0], blend=0.4)
shot("S05", "L05", cam(G.ME_G[0] - 0.6, G.ME_G[1], 1.45, 4.6, -12, 30, el=0.1))
cut("ty", "L06", (TX, TY_), yaw=0, expr="suspicious", head=[0, 0], arms=[0, 0])
cut("me", "L06", far["me"], yaw=0)
shot("S06", "L06", cam(TX, TY_, TZ, 3.4, 4, 34))
key("ty", "L06.1", head=[-8, 4], blend=0.4)

# ===== 03 two examples (L07 to L10)
HX, HY = G.HAL_BOX
cut("ty", "L07", far["ty"], yaw=0)
cut("hal", "L07", (HX, HY), yaw=-10, expr="neutral", head=[-8, 12], arms=[55, 0])
cue("L07", "ch", p=1)
TAG_OFF.add("S07")
shot("S07", "L07", cam(0.65, HY, 1.45, 4.2, -8, 32, el=0.15))
key("hal", "L07.1", head=[-4, 18], blend=0.4)
cue("L08", "ch", p=0)
CX, CY = G.HAL_CAST
cut("hal", "L08", (CX, CY), yaw=-90, expr="determined", head=[0, 0], arms=[70, 70])
cue("L08", "rod", r=1.0)
shot("S08a", "L08", cam(CX - 1.6, CY, 1.9, 7.0, 150, 28, el=0.6))
cue("L08.1", "rod", r=0.0)
cut("hal", "L08.1", (CX + 0.4, CY - 0.6), yaw=0, expr="delighted", head=[0, 0], arms=[70, 70])
cue("L08.1", "bucket", b=1.0)
shot("S08b", "L08.1", cam(CX + 0.4, CY - 0.6, 1.5, 4.0, -6, 32, el=0.1))
key("hal", "L08.1+0.5", arms=[80, 80], blend=0.4)
cue("L09", "bucket", b=0.0)
cut("hal", "L09", far["hal"], yaw=0)
cut("bea", "L09", (G.BEA_BOX[0], G.BEA_BOX[1]), yaw=-10, expr="nervous", head=[-8, 12], arms=[55, 0])
cue("L09", "cb", p=1)
TAG_OFF.add("S09")
shot("S09", "L09", cam(0.65, G.BEA_BOX[1], 1.45, 4.2, 8, 32, el=0.15))
key("bea", "L09.1", head=[-4, 16], blend=0.4)
cue("L10", "cb", p=0)
OX, OY = G.OFFICE
cut("bea", "L10", (OX + 0.9, OY - 0.9), yaw=0, expr="delighted", head=[0, 0], arms=[0, 70])
cue("L10", "donut", d=1.0)
shot("S10", "L10", cam(OX + 0.5, OY - 0.9, 1.5, 4.4, 8, 30, el=0.15))
key("bea", "L10.1", expr="crylaugh", head=[6, 0], blend=0.3)

# ===== 04 my question (L11), card one (L12 to L16)
cue("L11", "donut", d=0.0)
cut("bea", "L11", far["bea"], yaw=0)
cut("me", "L11", (MX + 0.25, MY), yaw=40, expr="determined", head=[0, 10], arms=[0, 0], side=[0, 70])
cue("L11", "q", u=0.0)
cue("L11.1", "q", u=1.0, dur=1.4)
DUSK.add("S11")
TAG_OFF.add("S11")
shot("S11", "L11", cam(-0.3, BY, 1.45, 3.4, 30, 32, el=0.25))
cue("L12", "q", u=2.0)
# Wednesday morning: the lid, from the side
cut("me", "L12", (MX, MY + 0.15), yaw=90, expr="nervous", head=[0, 10], arms=[0, 0], side=[0, 0])
cue("L12.1", "lid", o=1.0, dur=0.3)
cue("L12", "c1", p=5)
TAG_OFF.add("S12")
shot("S12", "L12", cam(BX - 0.2, BY, 1.45, 4.2, 70, 30, el=0.3))
cut("me", "L12b", (MX, MY), yaw=0, expr="shocked", head=[0, 8], arms=[0, 62])
cue("L12b", "c1", p=1)
shot("S12b", "L12b", cam(MX + 0.1, MY, 1.45, 3.2, 6, 32, el=0.1))
key("me", "L12b.1", head=[0, 14], blend=0.4)
cut("me", "L14", (MX, MY), yaw=0, expr="awe", head=[0, 14], arms=[0, 50])
cue("L14", "c1", p=4)
shot("S14", "L14", cam(MX - 0.05, MY, 1.3, 3.0, -10, 32, el=0.1))
cut("me", "L15", (MX, MY), yaw=0, expr="shocked", head=[0, 8], arms=[0, 62])
cue("L15", "c1", p=1)
shot("S15", "L15", cam(MX + 0.1, MY, 1.35, 3.0, 10, 34, el=0.05, push=2.6))
cue("L16", "c1", p=0)
SX, SY = G.TY_SHACK
cut("me", "L16", far["me"], yaw=0)
cut("ty", "L16", (SX - 1.2, SY - 0.6), yaw=90, expr="delighted", head=[0, 0], arms=[0, 0], lean=0)
key("ty", "L16+0.5", (SX - 0.3, SY - 0.6), lean=22, head=[0, -6])
key("ty", "L16.1", (SX + 0.8, SY - 0.6), lean=22)
key("ty", "L16.1+0.5", (SX + 1.3, SY - 0.6), lean=0, yaw=60, head=[0, 0], blend=0.4)
key("ty", "L16.2", (SX + 1.3, SY - 0.6), yaw=40, expr="crylaugh")
cut("me", "L16.1", (SX + 2.9, SY - 1.4), yaw=-35, expr="delighted", head=[-10, 10])
shot("S16", "L16", cam(SX + 0.6, SY - 0.6, 1.7, 7.4, 10, 28, el=0.2))

# ===== 05 card two (L17 to L21b)
cut("me", "L17", (MX, MY + 0.15), yaw=90, expr="nervous", head=[0, 10], arms=[0, 0], side=[0, 0])
cut("ty", "L17", far["ty"], yaw=0)
cue("L17", "lid", o=0.0)
cue("L17.1", "lid", o=1.0, dur=0.3)
cue("L17", "c2", p=5)
TAG_OFF.add("S17")
shot("S17", "L17", cam(BX + 0.1, BY, 1.4, 3.9, 110, 30, el=0.35))
cut("me", "L17b", (MX, MY), yaw=0, expr="shocked", head=[0, 6], arms=[0, 62])
cue("L17b", "c1", p=2)
cue("L17b", "c2", p=6)
cue("L17b+0.1", "c2", p=3, dur=0.45)
shot("S17b", "L17b", cam(MX + 0.15, MY, 1.45, 3.3, -4, 32, el=0.1))
# the drop: the open lid, the bay behind
TAG_OFF.add("S18")
shot("S18", "P00", cam(BX, BY, 1.25, 3.0, 160, 30, el=0.4, push=2.7))
cut("me", "L19", (MX, MY), yaw=0, expr="shocked", head=[0, 10], arms=[0, 62])
cue("L19", "c1", p=0)
cue("L19", "c2", p=1)
shot("S19", "L19", cam(MX + 0.1, MY, 1.38, 3.0, 8, 34, el=0.05))
key("me", "L19.1", expr="terrified", blend=0.3)
cut("me", "L20", (MX, MY), yaw=0, expr="nervous", head=[0, 14], arms=[0, 62])
cue("L20", "c1", p=2)
cue("L20", "c2", p=3)
shot("S20", "L20", cam(MX + 0.15, MY, 1.3, 2.9, -6, 34, el=0.1))
cut("me", "L21", (MX, MY), yaw=0, expr="nervous", head=[0, 0], arms=[0, 0])
cue("L21", "c1", p=0)
cue("L21", "c2", p=0)
key("me", "L21.1", head=[-12, 4], blend=0.5)
key("me", "L21b", expr="heartbroken", head=[6, 10], blend=0.5)
key("me", "L21b.1", head=[0, 14], blend=0.4)
shot("S21", "L21", cam(MX, MY, FZ, 3.1, 6, 34, push=2.7))

# ===== 06 Ty's been dodging (L22 to L24b)
GX = G.GARAGE[0]
cut("me", "L22", (GX - 0.4, 2.6), yaw=150, expr="suspicious", head=[0, 0], arms=[0, 0])
cut("ty", "L22", (GX - 2.6, -2.4), yaw=90, expr="delighted", head=[-55, 0])
key("ty", "L22>", (GX + 2.8, -2.4), yaw=90, head=[-60, 0])
shot("S22", "L22", cam(GX, 0.6, 1.8, 9.0, 200, 26, el=0.6))
cut("ty", "L23", (GX + 1.7, -0.35), yaw=-150, expr="neutral", head=[10, 0], arms=[0, 0], side=[0, 55])
cut("me", "L23", (GX - 0.3, 2.6), yaw=160, expr="suspicious", head=[0, 0])
shot("S23", "L23", cam(GX + 1.7, -0.35, TZ, 4.6, 200, 30, el=-0.3))
key("ty", "L23.1", head=[-14, 4], blend=0.4)
cut("ty", "L24", far["ty"], yaw=0)
cut("me", "L24", (G.ME_G[0], G.ME_G[1]), yaw=0, expr="nervous", head=[0, 0], arms=[0, 0], side=[0, 0])
shot("S24", "L24", cam(G.ME_G[0] + 0.2, G.ME_G[1], FZ, 3.4, 14, 32, push=3.0))
key("me", "L24.1", head=[-10, -6], blend=0.5)
key("me", "L24b", expr="heartbroken", head=[8, 8], blend=0.4)

# ===== 07 Thursday night, Ty at my garage (L27, L28)
for s_ in ("S27", "S28", "S25", "S26", "S29", "S30"):
    DUSK.add(s_)
BXg, BYg = G.BENCH
cue("L27", "c1", p=7)
cue("L27", "c2", p=8)
cut("me", "L27", (BXg - 0.3, BYg - 1.1), yaw=180, expr="nervous", head=[0, 18], arms=[0, 0])
shot("S27", "L27", cam(GX - 0.3, 3.6, 1.6, 6.0, 0, 26, el=0.6))
key("me", "L27.2", yaw=160, head=[-20, 10], blend=0.6)
cut("me", "L28", (BXg - 0.3, BYg - 1.1), yaw=180, expr="nervous")
TDX, TDY = G.TY_DOOR
cut("ty", "L28", (TDX, TDY), yaw=180, expr="delighted", head=[0, 0], arms=[60, 60])
cue("L28", "pizza", z=1.0)
shot("S28", "L28", cam(TDX, TDY, 1.9, 5.6, 180, 28, el=-0.2))
key("ty", "L28.1", head=[-8, 6], blend=0.4)

# ===== 08 the doubt (L25, L26)
cut("me", "L25", (GX - 0.2, 2.6), yaw=180, expr="nervous", head=[0, 10], arms=[0, 62])
cue("L25", "c1", p=1)
cue("L25", "c2", p=0)
cut("ty", "L25", (TDX, TDY), yaw=180, expr="neutral", head=[0, 0], arms=[60, 60])
shot("S25", "L25", cam(GX - 0.1, 2.6, 1.45, 3.4, 180, 32, el=0.15))
key("me", "L25.1", head=[0, 14], blend=0.4)
cut("me", "L26", (GX - 0.2, 2.6), yaw=180, expr="shocked", head=[0, 10], arms=[0, 62])
cue("L26", "c1", p=2)
cue("L26", "c2", p=3)
key("ty", "L26", expr="neutral", head=[0, 6])
shot("S26", "L26", cam(GX - 0.05, 2.6, 1.5, 3.6, 172, 32, el=0.1, push=3.1))
key("me", "L26.1", expr="terrified", blend=0.3)

# ===== 09 the question (L29, L30, P01)
cue("L29", "c1", p=7)
cue("L29", "c2", p=8)
cut("me", "L29", far["me"], yaw=0)
cut("ty", "L29", far["ty"], yaw=0)
shot("S29", "L29", cam(BXg - 0.75, BYg - 0.1, G.BENCH_Z + 0.1, 1.6, 0, 30, el=0.75, push=1.4))
cut("me", "L30", (G.ME_G[0], G.ME_G[1] + 0.4), yaw=0, expr="suspicious", head=[0, 0], arms=[0, 0])
cut("ty", "L30", far["ty"], yaw=0)
key("me", "L30.1", head=[6, 4], blend=0.5)
key("me", "P01", head=[-4, 6], blend=0.8)
key("me", "P01+1.6", head=[4, 2], expr="suspicious", blend=0.9)
# the hold: two slow 5% pushes on my face
shot("S30", "L30", [[0, *cam(G.ME_G[0], G.ME_G[1] + 0.4, FZ, 3.3, 0, 32)[0][1:]],
                    [0.35, *cam(G.ME_G[0], G.ME_G[1] + 0.4, FZ, 3.3, 0, 32)[0][1:]],
                    [0.65, *cam(G.ME_G[0], G.ME_G[1] + 0.4, FZ, 3.12, 0, 32)[0][1:]],
                    [1.0, *cam(G.ME_G[0], G.ME_G[1] + 0.4, FZ, 2.95, 0, 32)[0][1:]]])

# ----------------------------------------------------------------------------------------------- finish
for sid, at, camera, kw in SH:
    tag_on = 0.0 if sid in TAG_OFF else 1.0
    cue(at, "shot", tag=tag_on, dusk=1.0 if sid in DUSK else 0.0)
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
shots = []
for i, (sid, at, camera, kw) in enumerate(SH):
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    s.update({k: v for k, v in kw.items() if not k.startswith("_")})
    shots.append(s)

sfx = [
    {"at": "L12.1", "kind": "click", "db": -10},
    {"at": "L17.1", "kind": "click", "db": -10},
    {"at": "L28-0.45", "kind": "knock", "pattern": [0, 0.22], "tone": "soft", "db": -12},
    {"at": "L17b", "kind": "sting_mid", "db": -18},
]
music = {
    "root": 57, "mode": "major", "bpm": 100, "seed": 153,
    "sections": [
        {"at": 0, "voices": ["pluck", "pad"], "energy": 0.32},
        {"at": "L11", "voices": ["pluck", "pad"], "energy": 0.24},
        {"at": "L17", "voices": ["drone", "pluck", "pad"], "energy": 0.3},
        {"at": "L19", "voices": ["drone", "pad"], "energy": 0.28},
        {"at": "L27", "voices": ["drone", "pluck", "pad"], "energy": 0.3},
        {"at": "L29", "voices": ["drone", "tick"], "energy": 0.3},
    ],
}
sound = {
    "floor": "wood", "steps_db": -26,
    "ambience": [{"kind": "water", "from": 0, "to": "L22", "lufs": -40},
                 {"kind": "gulls", "from": 0, "to": "L11", "lufs": -44},
                 {"kind": "gulls", "from": "L12", "to": "L17b", "lufs": -46}],
    "sfx": sfx,
    "music_drops": [{"from": "P00", "to": "P00>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["ambience"])
remap_all(sound["music_drops"])
polish = {"reveal": [remap("L26.1")], "twist": remap("L26"),
          "emph": [remap(x) for x in ["L01.3", "L03.1", "L17b", "L26.1"]],
          "hold": ["S29"],
          "overlap": True, "turn_cap": 220, "punch_max": 4, "sharpen": 0.4, "bloom_thresh": 0.85}
story = {
    "slug": "ep153-pier-box",
    "title": "Two Cards In MY Handwriting Disagree 🗝️",
    "made_for_kids": False,
    "premise": ("The lock-box on our pier answers anything you ask in your own handwriting and has never sent anyone "
                "two cards; I asked whether to tell my best friend Ty about the bike I built him, and it sent two that disagree."),
    "twist": ("Either card could be Ty's: he knows my nickname for him and he knows my handwriting, so the story ends "
              "on the question of which card to trust."),
    "world": ("A sunny wooden fishing pier on a bright blue bay with white rails, gulls and a small green lock-box at its "
              "end; a bright tidy one-car garage with its door rolled up on a sunny street."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#3a7bff",
    "gap": 0.15,
    "tail": 0.0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "v3", "fog": "#cfe9ff", "fog_density": 0.001, "fog_start": 80.0, "sky": "#8fd3ff",
             "sky_strength": 1.0, "exposure": 0.05, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.02], "highlights": [0.03, 0.012, -0.02], "saturation": 1.08, "contrast": 1.04,
              "vignette": 0.15, "bloom": 0.12, "grain": 0.008},
    "hud": {"object": "tag", "at": [-0.62, 0.6], "size": 0.42},
    "homophones": {},
    "phonemes": {"Ty": "tˈI"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
    "framing_ok": [],
    "staging_ok": [],
    "clip_ok": [],
    "frames_ok": [],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
