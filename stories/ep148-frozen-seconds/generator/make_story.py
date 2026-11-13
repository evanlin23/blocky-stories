"""Writes ../story.json for ep148 "frozen seconds" (script.md, 2026-11-12, batch 15). Run: python stories/ep148-frozen-seconds/generator/make_story.py

The words are in lines.json; places are in ../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90,
+y 180, -x -90; a camera `az` degrees round from the south looks at a character who faces it with yaw = az.
Time references use the script's own chunk numbers (remap() turns them into the split captions').
One sun, bright, never changed: the freeze is a motion stop only (no colour drain, no dimming, no flash).
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
REV = 11
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = T.split_lines(orig_lines)
# the 0.5 s music drop before L22
idx = next(i for i, l in enumerate(lines) if l["id"] == "L22")
lines.insert(idx, {"id": "P01", "pause": 0.5, "chunks": [["", ""]]})


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
X = {"neutral": "neutral", "uneasy": "nervous", "stunned": "shocked", "sad": "heartbroken", "cry": "heartbroken",
     "smile": "delighted", "laugh": "crylaugh", "warm": "delighted", "det": "determined", "sheepish": "nervous",
     "scared": "terrified", "shut": "delighted"}


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", hat="none", hat_c="#333333",
           extras=(), eyes="round", sleeves="long", brow_w=1.0, extra_c=None, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c,
         "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    if brow_w != 1.0:
        d["face"]["brow_w"] = brow_w
    if extras:
        d["extras"] = list(extras)
    if extra_c:
        d["extra_c"] = extra_c
    d.update(kw)
    return d


cast = {
    # me: a tall wavy brown mop, light tan skin, a green bomber, jeans
    "me": person("#e0b184", "#3f8a4e", "#3d5a85", "#e8e4dc", hair="quiff", hair_c="#6a4630", brow_w=1.5, outline=0.06),
    # Leo: an orange beanie over short black hair, warm brown skin, a purple hoodie, chunky lime sneakers
    "leo": person("#a8744a", "#7a4ad8", "#2f3a52", "#b8f04a", hair="buzz", hair_c="#15110f", hat="beanie", hat_c="#f28a2a",
                  extras=["hooddown"], brow_w=1.3, outline=0.06),
    "uncle": person("#d9a47a", "#e8e4dc", "#3a4a5a", "#5a4a3a", hair="bald", hair_c="#3a2a1a", extras=["apron"],
                    extra_c="#f4f4f2", brow_w=1.5, sleeves="short", features=["mustache"], outline=0.06),
    "neighbor": person("#e8b890", "#e0708a", "#5a6a8a", "#8a5a3a", hair="curtains", hair_c="#a8a8a8", eyes="lashes", hat="bucket", hat_c="#ecd58a", features=["glasses"], outline=0.06),
    "walker": person("#c48a5e", "#2f6aa0", "#4a4a5a", "#2a2a30", hair="bigbun", hair_c="#2a1a12", eyes="lashes", outline=0.06),
    "jogger": person("#f1c9a0", "#d9483a", "#2a2a38", "#f4f4f2", hair="spikes", hair_c="#4a2f1a", hair_c2="#f4d03a", sleeves="short", outline=0.06),
}
acting = {n: [] for n in cast}
last = {n: [0, 0] for n in cast}
cues = []
SH = []


def key(who, at, pos=None, **kw):
    p = list(pos) if pos is not None else list(last[who])
    if "expr" in kw:
        kw["expr"] = X.get(kw["expr"], kw["expr"])
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def cut(who, at, pos=None, **kw):
    """A key that takes effect at once (no blend): a pose or place that changes on a cut."""
    p = list(pos) if pos is not None else list(last[who])
    acting[who].append({"at": at, "pos": list(last[who]), "blend": 0.0})
    key(who, at, p, blend=0.0, **kw)


def mouth(who, a, b, amt=0.5):
    acting[who].append({"from": a, "to": b, "mouth": [amt, amt], "flap": True})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def cam(tx, ty, tz, d, az, lens, cz=None, push=None):
    """A camera d metres from (tx, ty, tz), az degrees round from the south, looking at it. One key (the polish pack
    adds the slow push) or, with push=(d2, tz2), two keys."""
    def at_(dd, tzz, czz):
        cx = tx + dd * math.sin(az * D2R)
        cy = ty - dd * math.cos(az * D2R)
        return [round(cx, 3), round(cy, 3), czz if czz is not None else tzz], [tx, ty, tzz]
    p, t_ = at_(d, tz, cz)
    keys = [[0, p, t_, lens]]
    if push:
        p2, t2 = at_(push[0], push[1], None if cz is None else cz + (push[1] - tz))
        keys.append([1, p2, t2, lens])
    return keys


FAR = 1.5


def ck(*keys):
    """Explicit camera keys: (u, (x, y, z), (tx, ty, tz), lens)."""
    return [[u, [p[0], p[1], p[2]], [t[0], t[1], t[2]], ln] for u, p, t, ln in keys]


def shot(sid, at, camera, **kw):
    """The first pass framed far too tight: close shots (under 5.5 m from the target) back off FAR times; `_raw` keeps one."""
    if not kw.get("_raw"):
        for k in camera:
            p, t_ = k[1], k[2]
            if math.dist(p, t_) < 5.5:
                k[1] = [round(t_[i] + (p[i] - t_[i]) * FAR, 3) if i < 2 else p[i] for i in range(3)]
                k[1][2] = round(t_[2] + (p[2] - t_[2]), 3)
    SH.append((sid, at, camera, kw))


def face(pos, d=2.5, az=0, lens=36, tz=1.5, dx=0.0, push=None, zlift=0.0):
    return cam(pos[0] + dx, pos[1], tz, d, az, lens, push=push)


ME0 = (-0.8, 3.9)
LEO0 = (0.8, 3.9)
MS, LS = G.ME_SIT, G.LEO_SIT
SZ = G.SIT_Z
KX, KY = G.KITCHEN
FX_, FY_ = G.FRONT
PZ = G.PRETZEL

# ----------------------------------------------------------------------------------------------- the cast at rest
key("me", 0, ME0, yaw=0, expr="neutral", head=[0, 0], arms=[0, 0], side=[0, 0], lean=0)
key("leo", 0, LEO0, yaw=0, expr="smile", head=[0, 0], arms=[0, 0], side=[0, 0], lean=0)
key("uncle", 0, (KX + 0.9, KY + 1.9), yaw=0, expr="neutral", arms=[0, 0], side=[0, 0])
key("neighbor", 0, (FX_, FY_ + 0.6), yaw=0, expr="neutral", arms=[0, 0], side=[0, 0])
# two adults far off on the lawn: they walk, and stop where the freeze finds them (L17)
key("walker", 0, (-8.0, 15.0 - 7.5), yaw=0, arms=[0, 0], side=[0, 0])
key("jogger", 0, (8.0, 6.0), yaw=0, arms=[0, 0], side=[0, 0])

# the tag: the pause glyph and "1461"; from the freeze it counts down in minutes and seconds
cue(0, "tag", mode=0.0, s=1461.0)
cue(0, "freeze", f=0.0)
cue(0, "sit_me", s=0.0)
cue(0, "sit_leo", s=0.0)
cue(0, "note_me", m=0.0)
cue(0, "note_leo", m=0.0)
cue(0, "bite", b=0.0)
cue(0, "pretz", p=0.0)

# ===== 01 the rule (L01, L02)
cut("me", 0, ME0, yaw=0, expr="neutral")
shot("S01a", 0, cam(ME0[0] + 0.05, ME0[1], 1.5, 2.6, 0, 36))
shot("S01b", "L01.2", cam(ME0[0] + 0.05, ME0[1], 1.5, 2.1, 0, 36))
key("me", "L02", head=[0, 9], expr="det")
key("me", "L02.1", head=[0, 0])
shot("S02", "L02", face(ME0, 2.3, 8, 36))

# ===== 02 Leo, then two examples (L03, L05, L06)
cut("leo", "L03", LEO0, yaw=0, expr="smile", head=[0, 0])
shot("S03", "L03", cam(LEO0[0], LEO0[1], 1.5, 2.6, 0, 36))
cut("uncle", "L05", (KX + 0.55, KY + 1.9), yaw=0, expr="stunned")
key("uncle", "L05.1", (KX + 0.55, KY + 1.55), yaw=0, expr="stunned", lean=38, arms=[75, 75], blend=0.35)
shot("S05", "L05", cam(KX + 0.95, KY + 1.35, 0.95, 6.4, -32, 34, cz=1.3), _raw=True)
cut("neighbor", "L06", (FX_, FY_ + 0.6), yaw=0, expr="sheepish")
key("neighbor", "L06.1", (FX_, FY_ + 0.6), yaw=0, expr="sheepish", lean=12, head=[-10, 0], blend=0.3)
shot("S06", "L06", cam(FX_ - 0.1, FY_ + 0.3, 1.85, 4.8, 10, 30), _raw=True)

# ===== 03 the count and the move (L07, L08, L09)
cut("me", "L07", ME0, yaw=0, expr="neutral", head=[0, 0])
shot("S07a", "L07", face(ME0, 2.3, -8, 36))
shot("S07b", "L07.2", face(ME0, 1.9, 6, 36))
shot("S08a", "L08", cam(G.CAR[0], G.CAR[1] - 1.5, 1.1, 7.5, 38, 34), _raw=True)
key("me", "L08.2", expr="uneasy")
shot("S08b", "L08.2", face(ME0, 2.2, 0, 36))
cut("me", "L09", ME0, yaw=0, expr="sheepish")
shot("S09a", "L09", face(ME0, 2.2, 8, 36))
cut("leo", "L09.2", LEO0, yaw=0, expr="sheepish", arms=[0, 150])
key("leo", "L09.2+0.5", LEO0, arms=[0, 40], blend=0.5)
shot("S09b", "L09.2", cam(LEO0[0], LEO0[1], 1.45, 2.6, -6, 36))

# ===== 04 the sneakers (L11)
cut("leo", "L11", (0.8, 3.6), yaw=0, expr="smile", arms=[0, 0])
key("leo", "L11.2", (0.8, 3.1))
shot("S11a", "L11", ck((0, (0.8, 1.9, 0.55), (0.8, 3.3, 0.0), 20), (1, (0.8, 1.9, 0.5), (0.8, 3.0, 0.0), 20)), _raw=True)
cut("leo", "L11.2", LEO0, yaw=0, expr="laugh")
shot("S11b", "L11.2", cam(LEO0[0], LEO0[1], 1.5, 2.5, 4, 36))

# ===== 05 Leo asks (L14)
key("leo", "L14", expr="smile", head=[0, 0])
shot("S14a", "L14", cam(LEO0[0], LEO0[1], 1.5, 2.4, -6, 36))
key("leo", "L14.2", expr="smile", head=[0, 5])
shot("S14b", "L14.2", cam(LEO0[0], LEO0[1], 1.5, 2.0, 8, 36))

# ===== 06 the plan (L15)
cut("me", "L15", ME0, yaw=0, expr="det", head=[0, 0])
shot("S15a", "L15", face(ME0, 2.3, 0, 36))
cue("L15.2", "note_me", m=2.0)
cue("L15.3", "note_me", m=1.0, dur=0.7)
cue("L15.2", "pocket", p=1.0)
cue("L15.3+1.2", "pocket", p=0.0)
key("me", "L15.2", expr="det", arms=[0, 70], blend=0.3)
key("me", "L15.3", arms=[0, 20], blend=0.5)
shot("S15b", "L15.2", cam(ME0[0] - 0.2, ME0[1] - 0.22, 0.9, 1.3, 0, 30, push=(1.15, 0.9)), _raw=True)

# ===== 07 we sit, the pretzel (L16)
cue("L16.2", "pretz", p=1.0)
cut("me", "L16", (MS[0], MS[1] - 0.4), yaw=0, keep_yaw=True, expr="neutral", arms=[0, 0], head=[0, 0])
cut("leo", "L16", (LS[0], LS[1] - 0.4), yaw=0, keep_yaw=True, expr="neutral", arms=[0, 0], head=[0, 0])
key("me", "L16.1", (MS[0], MS[1], SZ), yaw=0, keep_yaw=True, blend=0.9)
key("leo", "L16.1", (LS[0], LS[1], SZ), yaw=0, keep_yaw=True, blend=0.9)
cue("L16.1", "sit_me", s=1.0, dur=0.8)
cue("L16.1", "sit_leo", s=1.0, dur=0.8)
shot("S16a", "L16", ck((0, (0.0, -0.1, 1.7), (0.0, 5.55, 1.15), 27), (1, (0.0, 0.2, 1.7), (0.0, 5.55, 1.15), 27)), _raw=True)
key("leo", "L16.3", expr="smile")
shot("S16b", "L16.3", ck((0, (-0.03, 4.95, 2.7), (-0.03, 5.5, 0.5), 28), (1, (-0.03, 5.0, 2.55), (-0.03, 5.5, 0.5), 28)), _raw=True)

# ===== 08 the freeze (L17, L18)
cut("me", "L17", (MS[0], MS[1], SZ), yaw=0, expr="det", head=[0, 0])
shot("S17a", "L17", face((MS[0], MS[1]), 2.4, 8, 36, tz=1.35))
cue("L17.2", "freeze", f=1.0)
shot("S17b", "L17.2", cam(0.0, 8.0, 3.9, 8.5, 0, 55, cz=3.9), _raw=True)
key("me", "L17.2", expr="neutral")
cue("L17", "tag", mode=1.0, s=1461.0, dur=0.0)
shot("S18a", "L18", cam(0.0, 8.0, 3.0, 7.0, 80, 34, cz=1.4, push=(5.6, 3.2)), _raw=True)
shot("S18b", "L18.2", cam(-3.4, 6.2, 2.5, 4.2, -10, 34, cz=1.6), _raw=True)
# the two on the lawn stop where the freeze finds them
key("walker", "L17.2-1.5", (-8.0, 15.0 - 7.5), yaw=0)
key("walker", "L17.2", (-6.5, 9.0), yaw=0)
key("jogger", "L17.2-1.5", (8.0, 6.0), yaw=0)
key("jogger", "L17.2", (7.0, 7.4), yaw=0)

# ===== 09 Leo sits still (L20)
cue("L20", "tag", mode=1.0, s=1230.0, dur=1.0)
key("leo", "L20", expr="neutral", head=[0, 0], look=[-0.8, 0])
shot("S20a", "L20", cam(LS[0], LS[1], 1.78, 2.4, 0, 36))
shot("S20b", "L20+0.6", ck((0, (-1.1, 3.6, 1.1), (0.1, 5.5, 0.62), 36), (1, (-1.0, 3.7, 1.1), (0.1, 5.5, 0.62), 36)), _raw=True)

# ===== 10 I turn (L21, L22)
cue("L21", "tag", mode=1.0, s=1100.0, dur=1.0)
cue("L21", "note_me", m=2.0)
key("me", "L21", expr="smile", arms=[0, 70], head=[0, 15], blend=0.4)
shot("S21a", "L21", cam(MS[0] - 0.2, MS[1], 1.2, 2.1, 0, 36))
# Leo stands and slips round behind the spray while I look down at the note
cue("L21", "sit_leo", s=0.0, dur=0.4)
key("leo", "L21", (LS[0], LS[1], 0.5), keep_yaw=True, expr="neutral", blend=0.4)
key("leo", "L21+0.3", (LS[0], LS[1], 0.5), keep_yaw=True)
key("leo", "L21+0.65", (1.3, 6.9, 0.3))
key("leo", "L21+1.05", (1.35, 8.0, 0.3))
key("leo", "L21+1.4", (0.95, 9.0, 0.3))
key("leo", "L21+1.7", (0.45, 9.55, 0.3))
key("leo", "L21+1.95", G.LEO_HIDE, keep_yaw=True)
shot("S21b", "L21.2", face((MS[0], MS[1]), 2.2, -30, 36, tz=1.4))
cue("L22", "tag", mode=1.0, s=950.0, dur=1.0)
key("me", "L22", expr="smile", arms=[0, 70], head=[0, 15])
key("me", "L22+0.15", expr="worried", yaw=22, head=[62, 0], arms=[0, 0], blend=0.75)
cue("L22+0.15", "note_me", m=0.0)
shot("S22a", "L22", ck((0, (-0.3, 3.9, 0.9), (0.2, 5.5, 0.62), 28), (1, (-0.2, 4.0, 0.9), (0.2, 5.5, 0.62), 28)), _raw=True)
shot("S22b", "L22.2", ck((0, (0.0, 3.0, 2.2), (0.0, 8.0, 3.2), 32), (1, (0.0, 3.4, 2.3), (0.0, 8.0, 3.3), 32)), _raw=True)
cue("L23", "tag", mode=1.0, s=800.0, dur=1.0)
key("me", "L23", expr="scared", yaw=18, head=[40, 0])
shot("S23", "L23", face((MS[0], MS[1]), 2.3, 6, 36, tz=1.4))

# ===== 11 the bite (L24, L25)
cue("L24", "tag", mode=1.0, s=650.0, dur=1.0)
cue("L24", "bite", b=1.0)
key("me", "L24", expr="stunned", yaw=0, head=[0, 5])
shot("S24", "L24", [[0, [PZ[0] - 0.05, PZ[1] - 1.25, 1.05], [PZ[0] - 0.05, PZ[1], 0.62], 40],
                    [1, [-0.35, PZ[1] - 4.4, 1.35], [-0.35, PZ[1], 1.3], 26]], _raw=True)
cue("L25", "tag", mode=1.0, s=520.0, dur=1.0)
cut("leo", "L25", (0.95, 9.1, 0.3), yaw=0, expr="neutral", arms=[0, 0])
shot("S25", "L25", ck((0, (0.4, 5.8, 0.65), (0.95, 9.0, 0.5), 38), (1, (0.45, 6.0, 0.6), (0.95, 9.0, 0.5), 38)), _raw=True)

# ===== 12 it was Leo (L26 to L29)
cue("L26", "tag", mode=1.0, s=400.0, dur=1.0)
key("leo", "L26", (1.1, 8.6, 0.3), yaw=0, expr="neutral", head=[0, 8])
key("leo", "L27+0.4", (0.85, 7.1, 0.3), yaw=0)
shot("S26", "L26", ck((0, (0.8, 5.2, 1.55), (0.8, 8.4, 1.5), 36), (1, (0.8, 4.9, 1.55), (0.82, 8.0, 1.5), 36)), _raw=True)
cue("L27", "tag", mode=1.0, s=330.0, dur=1.0)
key("leo", "L27", expr="neutral", head=[0, 8])
shot("S27", "L27", cam(G.LEO_OUT[0] + 0.25, G.LEO_OUT[1], 1.55, 2.4, 0, 36))
cue("L28", "tag", mode=1.0, s=260.0, dur=1.0)
cue("L28", "note_leo", m=2.0)
key("leo", "L28", expr="warm", head=[0, 0], arms=[0, 70], blend=0.4)
shot("S28", "L28", cam(G.LEO_OUT[0] - 0.2, G.LEO_OUT[1], 1.3, 2.3, 0, 36))
cue("L29", "tag", mode=1.0, s=190.0, dur=1.0)
shot("S29", "L28+0.7", cam(G.LEO_OUT[0] - 0.1, G.LEO_OUT[1], 1.4, 3.1, 0, 36, push=(2.5, 1.4)), _raw=True)

# ===== 13 together (L32)
cue("L32", "tag", mode=1.0, s=100.0, dur=1.5)
cue("L32", "note_me", m=2.0)
cue("L32", "sit_me", s=0.0, dur=0.4)
cut("me", "L32", (-1.1, 8.6, 0.3), yaw=0, expr="laugh", arms=[0, 70], head=[0, 0])
key("me", "L32>", (-1.1, 6.6, 0.3))
cut("leo", "L32", (1.1, 8.6, 0.3), yaw=0, expr="laugh", arms=[0, 70])
key("leo", "L32>", (1.1, 6.6, 0.3))
shot("S32a", "L32", cam(0.0, 7.4, 1.35, 6.2, 0, 26), _raw=True)
cue("L32.2", "note_leo", m=2.0)
shot("S32b", "L32.2", cam(0.0, 6.9, 1.5, 6.0, 8, 26), _raw=True)

# ===== 14 the thaw, the loop (L37)
cue("L37", "freeze", f=0.0)
cue("L32.2", "tag", mode=1.0, s=40.0, dur=0.8)
cue("L37", "tag", mode=1.0, s=0.0, dur=0.0)
cut("me", "L37", (-0.7, 5.0), yaw=0, expr="smile", arms=[0, 0])
cut("leo", "L37", (0.7, 5.0), yaw=0, expr="smile", arms=[0, 0])
cue("L37", "note_me", m=0.0)
cue("L37", "note_leo", m=0.0)
shot("S37a", "L37", cam(0.0, 8.0, 1.5, 9.4, 0, 34, cz=1.5), _raw=True)
cut("me", "L37.2", ME0, yaw=0, expr="smile", head=[0, 0])
cue("L37.2", "tag", mode=2.0, s=1.0)
cue("L37.2", "pretz", p=0.0)
cue("L37.2", "bite", b=0.0)
shot("S37b", "L37.2", cam(ME0[0], ME0[1], 1.5, 2.6, 0, 36, push=(2.0, 1.5)))

# ----------------------------------------------------------------------------------------------- finish
remap_all(cues)
for k_ in acting.values():
    remap_all(k_)
shots, names = [], {}
V3_SKIP = {"S11a", "S15b", "S25", "S16a", "S16b", "S20b", "S06", "S24", "S05", "S08a", "S22a", "S22b", "S17b", "S18a", "S18b"}
V3_WIDE = {"S32a": 1.14, "S32b": 1.14, "S37a": 1.1, "S24": 1.0}
V3_MORE = {"S21a": 1.4, "S21b": 1.15, "S26": 1.3, "S27": 1.2, "S28": 1.25, "S29": 1.3, "S37b": 1.25, "S30": 1.1}
for sid, at, camera, kw in SH:   # v3 heads are about 40% bigger: back off and lift the aim a little
    if sid in V3_SKIP:
        continue
    f = V3_WIDE.get(sid, 1.28) * V3_MORE.get(sid, 1.0)
    for k in camera:
        p, t_ = k[1], k[2]
        if math.dist(p, t_) < 6.5 and sid not in V3_WIDE:
            if 1.2 <= t_[2] <= 1.6:
                t_[2] = round(t_[2] + 0.12, 3)
                p[2] = round(p[2] + 0.12, 3)
        for i_ in range(3):
            p[i_] = round(t_[i_] + (p[i_] - t_[i_]) * f, 3)
for i, (sid, at, camera, kw) in enumerate(SH):
    s = {"id": sid, "cam": camera, "step": 2}
    if i:
        s["at"] = remap(at)
    kw = {k: v for k, v in kw.items() if not k.startswith("_")}
    s.update(kw)
    shots.append(s)

sfx = []
music = {
    "root": 52, "mode": "minor", "bpm": 108, "seed": 148,
    "sections": [
        {"at": 0, "voices": ["musicbox", "pad"], "energy": 0.34},
        {"at": "L08", "voices": ["musicbox", "pad"], "energy": 0.22},
        {"at": "L17.2", "voices": ["pad"], "energy": 0.1},
        {"at": "L22", "voices": ["drone", "pad"], "energy": 0.2},
        {"at": "L26", "voices": ["musicbox", "pad"], "energy": 0.5, "mode": "major"},
        {"at": "L37", "voices": ["musicbox", "pad"], "energy": 0.4},
    ],
}
sound = {
    "floor": "stone", "steps_db": -26,
    "ambience": [{"kind": "water", "from": 0, "to": "L17.2", "lufs": -40}, {"kind": "water", "from": "L37", "to": "end", "lufs": -40}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["ambience"])
remap_all(sound["music_drops"])
polish = {"reveal": [remap("L26")], "twist": remap("L26"),
          "emph": [remap(x) for x in ["L01.2", "L02.1", "L03.1", "L07.1", "L09.2", "L26", "L29.1"]],
          "quiet": [[remap("L32"), remap("L32")]],
          "hold": ["S29", "S32a", "S32b", "S37a", "S11a", "S15b", "S16b", "S20b", "S22a", "S22b", "S25"],
          "overlap": True, "turn_cap": 220, "punch_max": 4, "sharpen": 0.4, "bloom_thresh": 0.85}
story = {
    "slug": "ep148-frozen-seconds",
    "title": "I Saved FOUR Years Of Frozen Seconds ⏸️",
    "made_for_kids": False,
    "premise": ("Everyone here can freeze the world for one second a day; I saved four years of seconds to freeze it for "
                "24 minutes at noon, and in the frozen park something else was still moving."),
    "twist": ("It was my best friend Leo: he had saved four years of seconds for the same noon, to leave me a goodbye, "
              "so the only other person who could move in the frozen world was the one who froze it too."),
    "world": ("A bright city park at noon in summer: a round stone fountain with a tall centre jet, green lawns, big "
              "trees, a pretzel cart with a green umbrella, benches and a pale stone plaza."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#4ad0ff",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "v3", "fog": "#dfe8f4", "fog_density": 0.001, "fog_start": 60.0, "sky": "#6fb4f0",
             "sky_strength": 1.0, "exposure": 0.05, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.02], "highlights": [0.03, 0.012, -0.02], "saturation": 1.08, "contrast": 1.04,
              "vignette": 0.15, "bloom": 0.12, "grain": 0.008},
    "homophones": {"fourhundredandsixtyone": "thousandfourhundredsixtyone"},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": [],
    "framing_ok": ["S08a", "S08b", "S09a", "S15a", "S15b", "S21a", "S21b", "S22a", "S22b", "S17b"],
    "staging_ok": ["S22a/leo", "S21b/leo", "S21a/leo"],
    "clip_ok": ["fleck"],
    "frames_ok": ["S05", "S21b", "S22a"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
