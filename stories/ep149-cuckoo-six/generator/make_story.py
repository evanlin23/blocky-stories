"""Writes ../story.json for ep149 "Grandpa's Clock Cuckooed SIX Times For Five" (script.md, batch 15). Run:
    python stories/ep149-cuckoo-six/generator/make_story.py

Words are in lines.json (the script's slash chunks; captions split to three words here, references remapped).
Places are in ../layout.py (shared with set.py). One room, one stage: the camera moves, people stay (except Ivy, who
steps out from behind the curtain at L12 and walks behind the chairs to Grandpa). A character facing -y (the camera)
has yaw 0. Seated characters are lowered by layout.SEAT. No light change.
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
REV = 3
D2R = math.pi / 180

orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = timeline.split_lines(orig_lines)


def remap(ref):
    if not isinstance(ref, str):
        return ref
    mm = re.match(r"^(L\d+b?)\.(\d+)(.*)$", ref)
    if mm and mm.group(1) in CHUNKMAP:
        return f"{mm.group(1)}.{CHUNKMAP[mm.group(1)][int(mm.group(2))]}{mm.group(3)}"
    return ref


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, collar=None,
           extras=(), eyes="round", sleeves="long", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": "none",
         "face": {"eyes": eyes, "brows": True, "ink": "#1c120c"}}
    if pattern_c:
        d["pattern_c"] = pattern_c
    if collar:
        d["collar"] = collar
    if extras:
        d["extras"] = list(extras)
    d.update(kw)
    return d


cast = {
    "me": person("#e3b07c", "#3fbf5a", "#3a4a7a", "#3a2a20", hair="swoop", hair_c="#5a3a22", pattern="stripes",
                 pattern_c="#2f9a46", collar="#ffffff", sleeves="short"),
    "mom": person("#e6b894", "#ee7a62", "#5a4a6a", "#3a2a20", hair="cap", hair_c="#2a1d15", eyes="lashes"),
    "dad": person("#d9a066", "#27386e", "#6a5a48", "#3a2a20", hair="cap", hair_c="#5a5148", pattern="knit",
                  pattern_c="#33497f", collar="#e8f0f8", extras=["glasses"], extra_c="#222222"),
    "grandma": person("#f0c8a0", "#b79bdb", "#6a5a8a", "#4a3a30", hair="bun", hair_c="#f2f2f4", pattern="knit",
                      pattern_c="#c8b0ea", eyes="lashes", extras=["glasses"], extra_c="#8a6a9a"),
    "grandpa": person("#e8bd98", "#e0a526", "#5a4a38", "#4a3a30", hair="buzz", hair_c="#f2f2f4", pattern="knit",
                      pattern_c="#c98f1c", wbeard="#f5f5f7", crown="#e8b92a"),
    "ivy": person("#c98d5c", "#6fb4ea", "#3a4a7a", "#ff2a2a", hair="long", hair_c="#15100c", eyes="lashes",
                  sneakers="#ff2a2a", frosting="#ff9cc0", curls=True),
}
CAST = list(cast)
acting = {n: [] for n in cast}
cues = []
SH = []

EXPR = {"neutral": "neutral", "uneasy": "worried", "scared": "scared", "stunned": "wide", "smile": "smile",
        "laugh": "laugh", "warm": "warm", "delighted": "delighted", "soft": "soft"}


def key(who, at, x=None, y=None, z=0.0, yaw=0.0, expr="smile", arms=(0, 0), side=(0, 0), head=(0, 0), lean=0.0,
        seat=False, blend=0.25, **kw):
    k = {"at": at, "yaw": yaw, "arms": list(arms), "side": list(side), "head": list(head), "lean": lean,
         "expr": EXPR.get(expr, expr), "blend": blend, "blink": True}
    if x is not None:
        k["pos"] = [round(x, 3), round(y, 3), round(z - (G.SEAT if seat else 0.0), 3)]
    k.update(kw)
    acting[who].append(k)


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


YW, YE = 35, -35        # the west side turns toward us (+), the east side the other way
SIT = dict(seat=True, arms=(14, 14), side=(4, 4))
SITW = dict(SIT, yaw=YW)
SITE = dict(SIT, yaw=YE)

# ---- the five at the table, and Ivy behind the curtain, from the first frame (all seated, turned toward us)
key("grandma", 0, *G.GRANDMA, expr="smile", **SITW)
key("mom", 0, *G.MOM, expr="smile", **SITW)
key("grandpa", 0, *G.GRANDPA, expr="smile", **SIT)
key("dad", 0, *G.DAD, expr="smile", **SITE)
key("me", 0, *G.ME, expr="smile", **SITE)
key("ivy", 0, *G.IVY0, expr="smile", arms=(0, 0), side=(6, 6))

# ---- the counting: Mom, Dad, me react in turn (L04: cuckoo 2, 4, 6)
key("mom", "L04.1-0.05", *G.MOM, expr="worried", blend=0.12, **SITW)
key("dad", "L04.3-0.05", *G.DAD, expr="worried", blend=0.12, **SITE)
key("me", "L04.5-0.05", *G.ME, expr="stunned", blend=0.12, **SITE)
key("grandpa", "L04b", *G.GRANDPA, expr="warm", blend=0.3, **SIT)
key("mom", "L04b", *G.MOM, expr="worried", **SITW)
key("me", "L05", *G.ME, expr="uneasy", blend=0.4, **SITE)
key("dad", "L05", *G.DAD, expr="uneasy", **SITE)
key("grandpa", "L08", *G.GRANDPA, expr="smile", blend=0.3, arms=(78, 78), side=(2, 2), seat=True)
# ---- the answer
key("me", "L10", *G.ME, expr="smile", blend=0.4, **SITE)
# ---- the reveal: Ivy steps out from behind the curtain's west edge (0.9 s, facing us), thumb up, laughing
IVY_EDGE = (1.3, 2.55)        # just clear of the curtain's left edge
key("ivy", "L12-0.6", *G.IVY0, yaw=0, expr="smile", arms=(0, 0), side=(6, 6), blend=0.3, keep_yaw=True)
key("ivy", "L12-0.05", *IVY_EDGE, yaw=0, expr="laugh", arms=(8, 80), side=(6, -6), blend=0.3, keep_yaw=True)
key("ivy", "L12+0.4", *G.IVY_OUT, yaw=0, expr="laugh", arms=(8, 80), side=(6, -6), blend=0.3, keep_yaw=True)
key("me", "L12", *G.ME, expr="stunned", blend=0.3, **SITE)
key("me", "L12.1", *G.ME, expr="laugh", blend=0.4, **SITE)
key("grandma", "L12.0+0.15", *G.GRANDMA, expr="laugh", blend=0.3, **SITW)
key("dad", "L12.0+0.15", *G.DAD, expr="laugh", blend=0.3, **SITE)
key("mom", "L12.0+0.15", *G.MOM, expr="laugh", blend=0.3, **SITW)
key("grandpa", "L12", *G.GRANDPA, expr="delighted", blend=0.3, **SIT)
# she shuffles the last 0.6 m facing us (keep_yaw), thumb still up, then her arms come round Grandpa's shoulders
key("ivy", "L12.1+0.2", *G.IVY_OUT, yaw=0, expr="laugh", arms=(8, 80), side=(6, -6), keep_yaw=True)
key("ivy", "L22-0.6", *G.IVY_HUG, yaw=0, expr="laugh", arms=(8, 80), side=(6, -6), keep_yaw=True, lean=12, z=-0.25)
key("ivy", "L22+0.5", *G.IVY_HUG, yaw=0, expr="laugh", arms=(10, 40), side=(-4, -22), blend=0.5, lean=12, z=-0.25)
key("grandpa", "L22", *G.GRANDPA, expr="laugh", blend=0.4, **SIT)
key("grandma", "L22", *G.GRANDMA, expr="warm", blend=0.4, **SITW)
key("grandpa", "L23", *G.GRANDPA, expr="smile", blend=0.5, **SIT)

# ---- cues for set.py
for i in range(6):
    cue(f"L04.{i}", f"ck{i}")
cue("L01.2+0.9", "bird_off")
cue("L04.5", "sixshow")
cue("L22", "six")
cue("L07", "ltrA")
cue("L07+0.25", "ltrB")
cue("L07+0.5", "ltrC")
cue("L07+0.75", "ltrD")
cue("L08", "cake_on")
cue("P01>", "cake_off")
cue("L10", "ring")
cue("L10-0.05", "ltr_off")
cue("L12-0.6", "ring_off")
cue("L12-0.5", "toes_off")
cue("L12-0.5", "server_off")


# ---------------------------------------------------------------------------------------------- cameras
def cam(tx, ty, tz, d, lens, az=0.0, el=0.0, push=0.06, arc=2.0, to=None):
    """A camera d metres from the target at azimuth az (0: south of it looking north) and elevation el, pushing in
    by `push` while it slides `arc` degrees round."""
    def at(dd, a):
        a, e = a * D2R, el * D2R
        return [round(tx + dd * math.sin(a) * math.cos(e), 3), round(ty - dd * math.cos(a) * math.cos(e), 3),
                round(tz + dd * math.sin(e), 3)]
    tgt = [tx, ty, tz]
    t1 = list(to) if to else tgt
    push, arc = push * 3.0, arc * 3.0
    return [[0, at(d, az), tgt, lens], [1, at(d * (1 - push), az + arc), t1, lens]]


def hz(d, lens):
    return 24.0 * d / lens


def fcam(x, y, d, lens=30, f=0.40, z=0.0, dx=0.0, dz=0.0, hz_=1.57, **kw):
    """Aim so that a head at (x, y, 1.57 + z) sits f of the way down the frame."""
    h = hz_ + z
    return cam(x + dx, y, h - (0.5 - f) * hz(d, lens) + dz, d, lens, **kw)


def shot(id_, at, camera, step=2, hand=0.03):
    SH.append((at, camera, step, hand, id_))


GF, DD = G.GRANDPA, G.DAD
SEATZ = -G.SEAT
MASTER = (0.0, 0.8, 0.9)   # the dollhouse target

# 01 the rule (0 - ~5 s): the whole clock (bird and door clear of the tag) with Grandpa's face above the caption band
shot("S01a", 0, cam(0.0, 2.4, 1.1, 5.6, 34, el=3, push=0.04, arc=0.5))
shot("S01b", "L01.1", cam(0.0, 2.45, 2.2, 2.9, 34, el=0, push=0.04, arc=0.5))
shot("S02", "L01.3", cam(0.0, 0.8, 0.95, 4.6, 14, el=12, push=0.08, arc=1.0))
# 02 seven o'clock
shot("S03", "L03", cam(0.0, 2.6, G.CLOCK_Z - 0.12, 1.3, 30, el=3, push=0.08))
# 03 six cuckoos, one cut each
shot("S04a", "L04.0-0.05", cam(0.0, 2.6, G.CLOCK_Z + 0.25, 1.6, 30, el=8, push=0.0, arc=0.0))
shot("S04b", "L04.1-0.05", fcam(G.MOM[0], G.MOM[1], 2.0, f=0.4, z=SEATZ, push=0.0, arc=0.0))
shot("S04c", "L04.2-0.05", cam(0.0, 2.6, G.CLOCK_Z + 0.25, 1.6, 30, el=8, az=3, push=0.0, arc=0.0))
shot("S04d", "L04.3-0.05", fcam(DD[0], DD[1], 2.2, f=0.40, z=SEATZ, push=0.0, arc=0.0, az=-35))
shot("S04e", "L04.4-0.05", cam(0.0, 2.6, G.CLOCK_Z + 0.25, 1.3, 30, el=8, az=-3, push=0.0, arc=0.0))
shot("S04f", "L04.5-0.05", fcam(G.ME[0], G.ME[1], 1.8, f=0.40, z=SEATZ, push=0.06, arc=0.0))
shot("S05", "L04b", fcam(GF[0], GF[1], 2.4, f=0.40, z=SEATZ, push=0.06))
# 04 the job: the dollhouse master, people high in the frame, the rug and the sixth chair under the caption band
MASTER = (0.1, 0.4, 0.9)
shot("S06", "L05", cam(*MASTER, 5.6, 15, el=26, push=0.03, arc=1.0))
shot("S08", "L07", cam(*MASTER, 5.5, 15, el=26, az=-4, push=0.03, arc=1.0))
shot("S09", "L08", cam(-0.1, 2.0, 1.2, 2.9, 30, el=12, az=-10, push=0.05, arc=1.0))
# P01: the 4.0 s hold on the question
shot("S11a", "P01", cam(*MASTER, 5.6, 15, el=26, push=0.0, arc=0.0))
shot("S11b", "P01+1.4", cam(0.7, 0.8, 1.0, 5.0, 15, el=27, push=0.0, arc=0.0))
shot("S11c", "P01+2.7", cam(0.85, 1.3, 1.2, 4.3, 15, el=33, push=0.0, arc=0.0))
# 05 the answer
shot("S12", "L10", cam(2.0, 2.3, 1.45, 6.0, 30, el=21, az=6, push=0.06, arc=1.0))
shot("S13", "L11", cam(1.85, 2.2, 0.28, 1.7, 30, el=6, az=10, push=0.05, arc=1.0))
shot("S14a", "L11b", cam(-0.15, 1.25, 0.9, 1.2, 30, el=68, az=-20, push=0.0, arc=0.0))
shot("S14b", "L11b+0.7", cam(1.45, 2.15, 1.0, 2.6, 40, el=40, az=-35, push=0.0, arc=0.0))
# 06 the reveal
shot("S15", "L12-0.5", cam(1.2, 2.4, 1.45, 4.6, 55, el=20, az=-30, push=0.0, arc=0.0, to=[0.85, 2.3, 1.45]))
shot("S16", "L12.1", fcam(G.ME[0], G.ME[1], 2.2, f=0.40, z=SEATZ, push=0.04, arc=1.0, dx=-0.2))
shot("S19", "L22", cam(0.3, 2.4, 1.15, 3.0, 30, el=4, push=0.04, arc=1.5))
shot("S24", "L23", cam(0.0, 2.4, 1.1, 5.6, 34, el=3, push=0.04, arc=0.5))

shots, names = [], {}
for i, (at, camera, step, hand, nm) in enumerate(SH):
    s = {"id": nm, "cam": camera, "step": step, "hand": hand}
    if i:
        s["at"] = remap(at) if isinstance(at, str) else at
    shots.append(s)


def fix(items):
    for it in items:
        for k in ("at", "from", "to"):
            if k in it and isinstance(it[k], str):
                it[k] = remap(it[k])


for lst in list(acting.values()) + [cues]:
    fix(lst)
# the acting keys with the same time must stay in order; the timeline sorts by time
sfx = [
    {"at": "L01", "kind": "click", "db": -17, "dur": 0.2},
] + [{"at": f"L04.{i}", "kind": "ding", "db": -22, "dur": 0.35, "pitch": 440 if i % 2 == 0 else 330, "fall": 0.7, "lp": 1200}
     for i in range(6)] + [
    {"at": "P01+0.9", "kind": "click", "db": -27, "dur": 0.1},
    {"at": "P01+1.9", "kind": "click", "db": -27, "dur": 0.1},
    {"at": "P01+2.9", "kind": "click", "db": -27, "dur": 0.1},
    {"at": "L12", "kind": "thud", "db": -20, "dur": 0.3},
]
for s_ in sfx:
    s_["at"] = remap(s_["at"])
music = {
    "root": 58, "mode": "major", "bpm": 116, "seed": 149,
    "sections": [
        {"at": 0, "voices": ["pluck", "pulse"], "energy": 0.35},
        {"at": "P01", "voices": ["pulse"], "energy": 0.2},
        {"at": "L12", "voices": ["pad", "pluck"], "energy": 0.5},
    ],
}
for sec in music["sections"]:
    sec["at"] = remap(sec["at"])

HOLDS = ["S11a", "S11b", "S11c", "S06", "S08", "S12"]
polish = {"emph": [remap(r) for r in ("L01.1", "L01.4", "L04b", "L10.1", "L12.0", "L22.1")],
          "reveal": ["L12"], "twist": "L12", "hold": HOLDS, "quiet": [["L22", "L23"]], "ones": "all"}

lines_out = []
for ln in lines:
    lines_out.append(ln)

story = {
    "slug": "ep149-cuckoo-six",
    "title": "Grandpa's Clock Cuckooed SIX Times For Five \U0001F570️",
    "made_for_kids": False,
    "premise": ("Grandpa's cuckoo clock cuckoos once for every person in the house. On his eightieth birthday there are "
                "five of us and it goes six times, so someone else is in the room, and the viewer has to find the sixth "
                "among four hiding places before Grandpa cuts the cake."),
    "twist": ("The sixth is my big sister Ivy, who swore she had to work all weekend, hiding behind the yellow curtain "
              "to surprise Grandpa, given away by her red sneakers and frosting on her thumb."),
    "world": ("Grandpa's bright living room on a sunny evening: green leaf wallpaper, a long table with a birthday cake, "
              "a carved wood cuckoo clock, long sunflower curtains, a red armchair, a hall closet."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffd23f",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#f4e9d0", "fog_density": 0.002, "fog_start": 60.0, "sky": "#a9d6a0",
             "sky_strength": 1.0, "exposure": 0.0, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.02], "highlights": [0.03, 0.012, -0.02], "saturation": 1.05, "contrast": 1.03,
              "vignette": 0.12, "bloom": 0.06, "grain": 0.006},
    "hud": {"object": "tag", "at": [0.44, 0.8], "size": 0.62},
    "cast": cast,
    "lines": lines_out,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": {"floor": "wood", "steps_db": -26, "ambience": [], "sfx": sfx, "rev": REV},
    "framing_ok": ["S02", "S14b"],   # L02 names Ivy, who is hidden on purpose; her empty chair is the plant
    "staging_ok": ["S15/grandpa+ivy", "S16/dad+ivy", "S16/grandpa+ivy", "S19/grandpa+ivy", "S24/grandpa+ivy"],   # Ivy stepping out past Dad and Grandpa, then the hug (touching on purpose); no limb through a body  # Ivy steps out at Grandpa's shoulder and hugs him from behind (touching on purpose, L12 to L23)
    "asr_forgive": ["bee", "cuckoo", "o'clock", "that"],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
