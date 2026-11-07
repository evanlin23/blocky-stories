"""Writes ../story.json for ep110 "bless you" (script.md, 2026-11-04). Run: python stories/ep110-bless-you/generator/make_story.py

The words are in lines.json. Places are in ../layout.py (shared with set.py). A character facing -y (the camera) has
yaw 0, +x 90, -x -90. Time references use the script's chunk numbers (L05.2 is the third slash-chunk of L05); captions are
split to two or three words and the references are remapped.
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
REV = 20
orig_lines = json.loads((HERE / "lines.json").read_text())
lines, CHUNKMAP = [], {}
SPLITS = {"on his LANDLORD'S couch.": [3, 1], "it was a dumb FIGHT,": [3, 2], "in a green ARMCHAIR,": [3, 1],
          "for a long TIME.": [3, 1], "on a stranger's WALL.": [3, 1], "in his dog's BED.": [3, 1], "it was my BIRTHDAY.": [3, 1]}
for ln in orig_lines:
    out, mp = [], []
    for cap, spoken in ln["chunks"]:
        cw, sw = cap.split(), spoken.split()
        n = len(cw)
        k = 1 if n <= 3 else (2 if n <= 6 else 3)
        sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
        if cap in SPLITS:
            sizes = SPLITS[cap]    # keep function words with the word they lead (no 0.1 s "in a" caption)
        mp.append(len(out))
        i = 0
        for sz in sizes:
            out.append([" ".join(cw[i:i + sz]), " ".join(sw[i:i + sz])])
            i += sz
    CHUNKMAP[ln["id"]] = mp
    lines.append({**ln, "chunks": out})
# the 0.6 s music drop before L28
idx = next(i for i, l in enumerate(lines) if l["id"] == "L28")
lines.insert(idx, {"id": "P01", "pause": 0.6, "chunks": [["", ""]]})


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


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return [[0, list(p0), list(t0), l0]]
    return [[0, list(p0), list(t0), l0], [1, list(p1), list(t1 if t1 is not None else t0), l1 or l0]]


def F(tx, ty, tz, d, lens, dx=0.0, dz=0.0, push=0.14, rise=0.0):
    """A camera in front of (tx, ty, tz) at distance d, easing in by `push`."""
    return mv([tx + dx, ty - d, tz + dz], [tx, ty, tz], lens,
              [tx + dx * 0.75, ty - d * (1 - push), tz + dz + rise], [tx, ty, tz + rise * 0.5], lens)


def TOP(tx, ty, tz, h, lens, dy=0.3):
    """Looking nearly straight down at (tx, ty, tz) from h above, sinking a little."""
    return mv([tx, ty - dy, tz + h], [tx, ty, tz], lens, [tx, ty - dy * 0.8, tz + h * 0.88], [tx, ty, tz], lens)


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


cast = {
    "me": person("#dca97c", "#8ec9ff", "#4a6a9a", "#f4f4f2", hair="swoop", hair_c="#c89a5a", brow_w=1.9, extras=["hooddown"],
                 zip_c="#e8f4ff"),
    "mom": person("#e6b48c", "#f6ecd8", "#6a7a9a", "#d8c8a8", hair="long", hair_c="#9a7a45", pattern="stripes",
                  pattern_c="#7a9ab8", eyes="lashes", brow_w=1.9, extras=["apron"], extra_c="#ffc94a", width=0.96),
    "grandpa": person("#e8b890", "#2f6b4a", "#5a5048", "#4a3626", hair="cap", hair_c="#f4f4f0", collar="#f2e6c8",
                      extras=["glasses"], extra_c="#6a6a70", width=1.02),
    "m1": person("#c98f68", "#ffffff", "#3a4a6a", "#2a2a2a", hair="cap", hair_c="#1a1410", extras=["tie"], extra_c="#e8493a"),
    "m1mom": person("#e6b48c", "#e8845a", "#6a5a4a", "#7a5a3a", hair="bun", hair_c="#cfcfd4", eyes="lashes", extras=["apron"],
                    extra_c="#fffaf0", width=0.96),
    "walker": person("#b98456", "#7fb070", "#4a4036", "#2a2a2a", hair="buzz", hair_c="#1a1410", hat="ballcap", hat_c="#c0543a",
                     sleeves="short"),
    "party": person("#f0c8a0", "#ff9fc0", "#3a4a5a", "#f4f4f2", hair="spiky", hair_c="#a05a2a", pattern="stripes",
                    pattern_c="#ffd23f", sleeves="short"),
    "landlord": person("#e8b890", "#c9b27a", "#5a5048", "#4a3626", hair="cap", hair_c="#6a4528", vest="#4a6a9a", width=1.04),
    "x1": person("#b98456", "#e8845a", "#4a4036", "#2a2a2a", hair="buzz", hair_c="#1a1410", sleeves="short"),
    "x2": person("#f0c8a0", "#8a5ab0", "#2a2a38", "#d8d0c8", hair="long", hair_c="#150f0c", eyes="lashes"),
    "x3": person("#8a5a3a", "#ffd23f", "#3a4a5a", "#3a2a1a", hair="spiky", hair_c="#2a2a2a", sleeves="short"),
    "x4": person("#d3a07a", "#e8c040", "#4a5a7a", "#6a3a2a", hair="swoop", hair_c="#7a3a1a", pattern="stripes", pattern_c="#ffffff"),
    "x5": person("#e8b890", "#7fb070", "#6a5a8a", "#f4f4f2", hair="bun", hair_c="#7a4a2c", eyes="lashes"),
    "x6": person("#dca97c", "#f4a3a3", "#3a4a6a", "#2a2a2a", hair="cap", hair_c="#a05a2a", sleeves="short"),
}
acting = {n: [{"at": 0, "hidden": True, "pos": [0, 0]}] for n in cast}
last = {n: [0, 0] for n in cast}
visible = set()
cues = []
SH = []


def put(who, at, pos, yaw=None, **kw):
    p = list(pos)
    if at == 0:   # a second key at 0 left frame 0 on the hidden placeholder, off at (0, 0): drop the placeholder
        acting[who] = [k_ for k_ in acting[who] if not (k_.get("at") == 0 and k_.get("hidden") and k_.get("pos") == [0, 0])]
    else:
        acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False}
    if yaw is not None:
        k["yaw"] = yaw
    k.update(kw)
    acting[who].append(k)
    last[who] = p
    visible.add(who)


def go(who, at, pos, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def beat(who, at, **kw):
    acting[who].append({"at": at, "pos": list(last[who]), **kw})


def only(at, names):
    for w in list(visible):
        if w not in names:
            acting[w].append({"at": at, "hidden": True})
            visible.discard(w)


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def shot(at, camera, name, step=2, hand=None, follow=None):
    SH.append((at, camera, step, hand, follow, name))


def swirl(at, x, y, z=0.95, dur=0.9, **kw):
    cue(at, "swirl", x=x, y=y, z=z, dur=dur, **kw)


def sit(who, at, on=True, z=0.62):
    cue(at, "sit", who=who, on=on, z=z)


def hold(who, at, on=True):
    cue(at, "hold", who=who, on=on)


SNEEZE = dict(expr="squeeze", head=[0, 20])        # eyes screwed shut, head dipped
cue(0, "look", id="day", dur=0)
cue(0, "count", n=63.0)
cue(0, "pin", v=0.0, v2=0.0)
cue(0, "tv", v=0.0)
cue(0, "pollen", level=1.0)
cue(0, "treat", v=0.0)
cue(0, "cup3", v=0.0)
cue(0, "wall", v=0.0)
cue(0, "pillpos", u=0.0)
cue(0, "pill0", v=0.0)

PK, ST, OF, MK, DG, PT, LD, GP, KT, BD = (G.PARK, G.STREET, G.OFFICE, G.MKIT, G.DOG, G.PARTY, G.LAND, G.GP, G.KIT, G.BED)
GCH = (GP + 1.6, 2.15)          # Grandpa's armchair seat (torso position)
GSOFA_R = (GP + 0.3, 2.15)
GRUG = (GP - 0.1, 0.7)

# ===== 01 the rule (L01 to L02)
put("me", 0, [PK, -8.0], 0, **SNEEZE)
acting["me"][-1]["head"] = [0, 6]
beat("me", "L01.1", head=[0, 22], expr="squeeze")
acting["me"].append({"at": 0, "pos": [PK, -8.0], "mouth": None}) if False else None
acting["me"].append({"from": 0, "to": "L01.2", "mouth": [0.1, 0.7]})
shot(0, F(PK, -8.0, 1.4, 2.1, 40, dx=0.05, push=0.1), "sneeze1")
beat("me", "L01.2", hidden=True)
visible.discard("me")
swirl("L01.2", PK, -8.0, 0.95, 1.0)
shot("L01.2", F(PK, -8.0, 1.2, 4.4, 34, dx=-0.3, push=0.12, rise=0.2), "gone1")
# L02: landing by the armchair, then his hand
only("L02", ["grandpa", "me"])
put("grandpa", "L02", list(GCH), 0, expr="warm", arms=[40, 40])
sit("grandpa", "L02")
put("me", "L02", [GP + 0.45, 2.9], 0, expr="wide")
swirl("L02", GP + 0.45, 2.9, 0.95, 1.0, sz=1.0)
cue("L02", "pin", v=1.0, dur=0.5)
shot("L02", F(GP + 1.0, 2.2, 1.45, 5.7, 30, dx=0.0, push=0.08), "land1")
shot("L02.2", F(GP + 1.6, 2.15, 1.3, 3.8, 34, dx=0.4, push=0.1), "hand1")

# ===== 02 the montage (L03 to L08)
only("L03", ["x1", "x2", "x3", "x4", "x5", "x6"])
xs = [("x1", -5.5, -1.2), ("x2", -3.2, 1.0), ("x3", -1.0, -0.8), ("x4", 1.2, 1.2), ("x5", 3.4, -0.9), ("x6", 5.6, 1.0)]
for k, (w_, x, y) in enumerate(xs):
    put(w_, "L03", [ST + x, y], 0, expr="neutral")
for k, w_ in enumerate(("x2", "x5", "x1", "x4", "x3", "x6")):
    ts = f"L03+{0.12 + 0.13 * k:.2f}"
    beat(w_, ts, **SNEEZE)
    x, y = last[w_]
    beat(w_, f"L03+{0.12 + 0.13 * k + 0.28:.2f}", hidden=True)
    swirl(f"L03+{0.12 + 0.13 * k + 0.26:.2f}", x, y, 0.95, 0.6, sz=1.2)
shot("L03", mv([ST - 1.0, -9.6, 3.0], [ST, 0.2, 1.3], 30, [ST + 0.4, -8.4, 2.7], [ST, 0.2, 1.3], 30), "street1")
# our kitchen: Mom at the stove-side counter, the pill bottle by the coffee maker, me sneezing away beside her
only("L03.2", ["mom", "me"])
put("mom", "L03.2", [KT - 0.75, 2.55], 0, expr="soft", arms=[40, 0])
put("me", "L03.2", [KT + 0.15, 2.2], 0, expr="neutral")
beat("me", "L03.2+0.08", **SNEEZE)
beat("me", "L03.2+0.4", hidden=True)
swirl("L03.2+0.4", KT + 0.15, 2.2, 0.95, 0.5, sz=1.0)
shot("L03.2", F(KT - 0.5, 2.6, 1.3, 4.8, 22, dx=0.0, push=0.06), "kitchen0")
cue("L03.2", "pill0", v=1.0)
cue("L04", "pill0", v=0.0)
cue("L03", "pollen", level=1.8)
# L04: the meeting man sneezes at a glass table, lands in a kitchen
only("L04", ["m1"])
cue("L04", "pollen", level=1.0)
put("m1", "L04", [OF, 1.9], 0, expr="neutral", arms=[40, 40])
beat("m1", "L04.1", **SNEEZE)
shot("L04", F(OF, 1.9, 1.4, 3.5, 36, dx=0.2, push=0.16), "meeting")
only("L04.2", ["m1"])
put("m1", "L04.2", [MK + 0.9, 2.5], 0, expr="wide")
swirl("L04.2", MK + 0.9, 2.5, 0.95, 1.0)
shot("L04.2", F(MK + 0.8, 2.5, 1.3, 3.8, 34, dx=-0.3, push=0.14), "kitchen1")
# L05: his mom, a plate already out
only("L05", ["m1mom"])
put("m1mom", "L05", [MK + 0.7, 2.55], 0, expr="smile")
beat("m1mom", "L05.1", expr="grin", head=[10, 0])
shot("L05", F(MK + 0.7, 2.55, 1.35, 3.3, 36, dx=0.1, push=0.16), "mom1")
# L06: a dog walker sneezes on a path, lands in a dog's bed
only("L06", ["walker"])
put("walker", "L06", [PK, 6.0], 0, expr="neutral")
beat("walker", "L06.1-0.35", **SNEEZE)
shot("L06", F(PK, 6.0, 1.4, 3.4, 36, dx=-0.15, push=0.16), "walker1")
only("L06.1", ["walker"])
put("walker", "L06.1", [DG - 0.1, 1.8], 0, expr="wide")
sit("walker", "L06.1", True, 0.5)
swirl("L06.1", DG - 0.1, 1.8, 0.8, 1.0)
shot("L06.1", F(DG + 0.3, 1.7, 1.0, 4.6, 34, dx=0.4, push=0.14), "bed1")
# L07: a man sneezes at a party and lands on his landlord's couch
only("L07", ["party"])
put("party", "L07", [PT + 0.4, 1.6], 0, expr="grin")
beat("party", "L07.1+0.2", **SNEEZE)
shot("L07", F(PT + 0.4, 1.6, 1.4, 3.4, 36, dx=-0.2, push=0.16), "party1")
only("L07.2", ["party", "landlord"])
sit("party", "L07.2", True, 0.62)
put("party", "L07.2", [LD - 1.6, 2.2], 0, expr="wide")
put("landlord", "L07.2", [LD + 2.0, 2.2], 0, expr="polite", arms=[40, 50])
sit("landlord", "L07.2", True, 0.62)
hold("landlord", "L07.2", True)
swirl("L07.2", LD - 1.6, 2.2, 0.95, 1.0)
shot("L07.2", F(LD - 1.4, 2.2, 1.2, 3.8, 34, dx=0.5, push=0.12), "couch1")
# L08: the landlord's eyebrows, the man sheepish
beat("landlord", "L08", expr="angry", head=[-10, 0])
shot("L08", F(LD + 2.0, 2.2, 1.35, 3.0, 40, dx=0.1, push=0.16), "landlord1")
beat("party", "L08.1+0.33", expr="worried", head=[12, 6])
shot("L08.1+0.33", F(LD - 1.6, 2.2, 1.35, 3.0, 40, dx=-0.1, push=0.16), "party2")
sit("party", "L09-0.1", False)
sit("landlord", "L09-0.1", False)
hold("landlord", "L09-0.1", False)

# ===== 03 the armchair (L09 to L18)
only("L09", ["me"])
put("me", "L09", [PK + 0.5, -10.0], 0, expr="neutral")
beat("me", "L09.1-0.2", **SNEEZE)
shot("L09", F(PK + 0.5, -10.0, 1.4, 3.3, 40, dx=-0.15, push=0.16), "sneeze2")
# L10: the green armchair room, the old man
only("L10", ["grandpa"])
put("grandpa", "L10", list(GCH), 0, expr="warm", arms=[40, 40])
sit("grandpa", "L10")
shot("L10", F(GCH[0] - 0.4, GCH[1], 1.2, 3.6, 32, dx=0.0, push=0.1), "room1")
beat("grandpa", "L10.2", expr="warm", head=[0, -4])
shot("L10.2", F(GCH[0], GCH[1], 1.4, 2.7, 40, dx=-0.15, push=0.16), "gp1")
# L11: top-down tray
shot("L11", TOP(GP - 0.25, 1.0, 0.6, 2.5, 34), "tray1")
# L12: the first time I said sorry and ran
only("L12", ["grandpa", "me"])
put("grandpa", "L12", list(GCH), 0, expr="warm", arms=[40, 40])
sit("grandpa", "L12")
put("me", "L12", list(GRUG), 0, expr="worried", arms=[30, 30])
swirl("L12", GRUG[0], GRUG[1], 0.95, 0.9)
beat("me", "L12.1", expr="worried", arms=[70, 70], head=[0, -5])
go("me", "L12.2", [GP - 5.8, 0.4], run=True, expr="scared")
shot("L12", F(GP - 0.1, 1.2, 1.35, 4.6, 36, dx=0.2, push=0.14), "sorry1")
shot("L12.2", F(GP - 2.0, 0.7, 1.2, 5.0, 32, dx=1.5, push=0.12), "ran1")
# L13: "Bless YOU."
only("L13", ["grandpa"])
put("grandpa", "L13", list(GCH), 0, expr="smile", arms=[40, 40])
sit("grandpa", "L13")
beat("grandpa", "L13.1", expr="warm", head=[0, 4])
shot("L13", F(GCH[0], GCH[1], 1.4, 2.5, 42, dx=0.1, push=0.16), "gp2")
# L14: by sneeze twenty I sat down
only("L14", ["grandpa", "me"])
put("grandpa", "L14", list(GCH), 0, expr="warm", arms=[40, 40])
sit("grandpa", "L14")
put("me", "L14", [GP - 1.2, 1.0], 0, expr="wide")
swirl("L14", GP - 1.2, 1.0, 0.95, 0.9)
shot("L14", F(GP - 1.2, 1.4, 1.3, 4.2, 34, dx=0.4, push=0.14), "sit1")
put("me", "L14.1", [GP - 1.2, 1.75], 20, expr="worried", arms=[0, 0])
sit("me", "L14.1")
shot("L14.1", F(GP - 1.2, 1.75, 1.3, 2.3, 44, dx=0.6, push=0.12), "sit2")
beat("me", "L14.1+0.5", expr="polite", yaw=-20)
# L15: forty, drinking the tea
hold("me", "L15")
put("me", "L15", [GP - 1.2, 1.75], -12, expr="polite", arms=[0, 62])
sit("me", "L15")
beat("me", "L15.1", expr="polite", arms=[0, 70], head=[0, 8])
shot("L15", F(GP - 1.2, 1.75, 1.3, 2.9, 40, dx=-0.1, push=0.12), "cup1")
# L16: he never asks my name
only("L16", ["grandpa", "me"])
put("grandpa", "L16", list(GCH), 0, expr="warm", arms=[40, 40])
sit("grandpa", "L16")
put("me", "L16", [GP - 1.2, 1.75], 10, expr="polite", arms=[0, 85])
sit("me", "L16")
hold("me", "L16")
shot("L16", F(GCH[0], GCH[1], 1.4, 2.6, 40, dx=-0.15, push=0.16), "gp3")
shot("L16.2", F(GP + 0.2, 2.1, 1.35, 4.9, 34, push=0.14), "both1")
# L17: how is the new job
beat("grandpa", "L17", expr="smile", head=[0, 5])
shot("L17", F(GCH[0], GCH[1], 1.4, 2.8, 40, dx=0.2, push=0.16), "gp4")
# L18: I never told him
beat("me", "L18", expr="worried", arms=[0, 85])
shot("L18", F(GP - 1.2, 1.75, 1.3, 2.8, 40, dx=-0.2, push=0.16), "me3")
hold("me", "L19-0.1", False)
sit("me", "L19-0.1", False)

# ===== 04 the song, the pill (L19 to L26)
only("L19", ["grandpa"])
put("grandpa", "L19", list(GCH), 0, expr="smile", arms=[40, 40])
sit("grandpa", "L19")
acting["grandpa"].append({"from": "L19", "to": "L19.2", "flap": True, "mouth": [0.0, 0.4]})
beat("grandpa", "L19+0.4", expr="smile", head=[8, 3])
beat("grandpa", "L19+0.9", expr="smile", head=[-8, 3])
shot("L19", F(GCH[0], GCH[1], 1.4, 2.7, 40, dx=0.1, push=0.16), "hum1")
only("L19.2", ["mom"])
put("mom", "L19.2", [KT - 2.4, 2.45], 0, expr="smile", arms=[40, 0])
acting["mom"].append({"from": "L19.2", "to": "L20", "flap": True, "mouth": [0.0, 0.4]})
beat("mom", "L19.2+0.3", expr="smile", head=[8, 3])
beat("mom", "L19.2+0.8", expr="smile", head=[-8, 3])
shot("L19.2", F(KT - 2.4, 2.45, 1.4, 2.9, 40, dx=0.1, push=0.16), "hum2")
# L20: Mom never sneezes, not even in May
only("L20", ["mom"])
put("mom", "L20", [PK - 0.4, 8.0], 0, expr="smile")
go("mom", "L20.2-0.1", [PK - 0.4, 2.4])   # stops 3.4 m short of the camera (it ends at y -0.97): she walked into the lens (S32 frames 1111-1115)
cue("L20", "pollen", level=2.4)
shot("L20", F(PK - 0.3, 3.5, 1.4, 5.2, 34, dx=0.4, push=0.14), "momwalk")
cue("L20.2", "pollen", level=1.0)
put("mom", "L20.2", [ST + 5.6, -1.2], 0, expr="soft")
shot("L20.2", F(ST + 5.9, -1.5, 1.3, 5.4, 34, dx=0.0, push=0.12), "momcar")
# L21: the pill
only("L21", [])
shot("L21", F(KT + 0.62, 3.2, 1.05, 1.5, 40, dx=0.25, push=0.14), "pill1")
only("L21.1", ["mom"])
put("mom", "L21.1", [KT + 0.2, 2.6], 0, expr="soft", arms=[0, 130])
beat("mom", "L21.1+0.6", expr="soft", arms=[0, 160], head=[0, -8])
beat("mom", "L21.1+1.2", expr="smile", arms=[0, 0], head=[0, 0])
shot("L21.1", F(KT + 0.2, 2.6, 1.4, 3.1, 40, dx=-0.15, push=0.16), "pill2")
# L22: just careful
beat("mom", "L22", expr="grin", arms=[0, 100])
beat("mom", "L22.1", expr="grin", arms=[0, 92])
shot("L22", F(KT + 0.2, 2.6, 1.4, 2.7, 40, dx=0.15, push=0.16), "careful")
# L23: I asked her
only("L23", ["me"])
put("me", "L23", [KT + 4.15, 1.5], -22, expr="worried")
sit("me", "L23")
beat("me", "L23.1", expr="worried", head=[-8, 0])
shot("L23", F(KT + 4.15, 1.5, 1.35, 2.8, 40, dx=-0.1, push=0.14), "ask")
sit("me", "L24-0.1", False)
# L24: guarded, and turning to the stove
only("L24", ["mom"])
put("mom", "L24", [KT + 1.85, 1.5], 22, expr="polite")
beat("mom", "L24.1", expr="polite", head=[-8, 0])
shot("L24", F(KT + 1.85, 1.5, 1.4, 2.7, 40, dx=0.1, push=0.14), "guard")
put("mom", "L24.2", [KT - 1.3, 2.5], 0, expr="soft")
beat("mom", "L24.2+0.5", expr="polite", head=[-30, 0])
shot("L24.2", F(KT - 1.3, 2.5, 1.4, 2.9, 38, dx=0.0, push=0.1), "turn")
# L25: the favourite cookies
only("L25", [])
cue("L25", "treat", v=1.0)
shot("L25", TOP(GP + 0.05, 1.0, 0.6, 2.4, 34), "cookies")
# L26: a small cake with one candle
only("L26", ["grandpa", "me"])
cue("L26", "treat", v=2.0)
put("grandpa", "L26", list(GCH), 0, expr="smile", arms=[40, 40])
sit("grandpa", "L26")
put("me", "L26", [GP - 1.2, 1.75], 0, expr="worried", arms=[0, 0])
sit("me", "L26")
shot("L26", F(GP + 0.2, 1.8, 1.2, 5.2, 32, push=0.14), "cake")
beat("me", "L26.1", expr="worried", head=[0, -6])
cue("L26>", "treat", v=0.0)
sit("me", "L26>", False)
sit("grandpa", "L26>", False)

# ===== 05 two in the morning (L27 to L38): the one dark scene
only("L27", ["me"])
cue("L27", "look", id="night", dur=0)
cue("L27", "pollen", level=0.0)
put("me", "L27", [BD, 2.55], 0, expr="shut", arms=[0, 0])
sit("me", "L27", True, 0.78)
beat("me", "L27.1", **SNEEZE)
beat("me", "L27.2", expr="wide", head=[0, 0])
cue("L27.2", "count", n=64.0)
cue("L27.2", "pin", v=1.0, dur=0.4)
shot("L27", F(BD - 0.1, 2.55, 1.45, 3.7, 36, dx=0.3, push=0.14), "bed")
only("P01", [])
cue("P01", "tv", v=0.35)
cue("P01+0.05", "tv", v=1.0, dur=0.9)
shot("P01", mv([GP + 0.4, -2.8, 1.8], [GP + 0.6, 2.0, 1.1], 30, [GP + 0.4, -2.5, 1.75], [GP + 0.6, 2.0, 1.1], 30), "dark")
only("L28", ["grandpa"])
cue("L28", "look", id="night", dur=0)
put("grandpa", "L28", list(GCH), 0, expr="soft", arms=[40, 40])
sit("grandpa", "L28")
shot("L28", mv([GP - 0.8, -5.6, 1.5], [GP - 0.8, 2.0, 1.1], 17, [GP - 0.8, -4.8, 1.45], [GP - 0.8, 2.0, 1.1], 17), "dark2")
# L29: he was awake
shot("L29", F(GCH[0], GCH[1], 1.35, 3.6, 38, dx=-0.5, push=0.16), "awake1")
beat("grandpa", "L29.2", expr="soft", head=[-6, 0])
shot("L29.2", F(GCH[0], GCH[1], 1.45, 2.3, 42, dx=-0.3, push=0.14), "awake2")
# L30: past his shoulder to the wall behind
cue("L30", "wall", v=1.0)
shot("L30", mv([GP + 3.4, -0.9, 1.45], [GP + 0.6, 3.0, 1.9], 30, [GP + 2.4, 0.5, 1.5], [GP - 0.6, 3.8, 2.0], 30), "pastshoulder")
# L31: ME (the portrait)
shot("L31", F(GP - 3.6, 3.6, 2.25, 2.6, 36, dx=0.1, push=0.2), "portrait")
# L32: the wall, then one clipping
shot("L32", mv([GP - 2.4, -3.8, 2.0], [GP - 2.4, 3.8, 2.0], 32, [GP - 2.4, -2.8, 2.0], [GP - 2.4, 3.8, 2.0], 32), "wall1")
shot("L32.2", F(GP - 2.4, 3.7, 2.0, 2.3, 38, dx=0.2, push=0.2), "clip1")
# L33: notice, trophy, first job
shot("L33", F(GP - 1.6, 3.7, 2.8, 1.5, 40, dx=0.0, push=0.2), "baby")
shot("L33.1", F(GP - 0.8, 3.7, 2.8, 1.5, 40, dx=0.0, push=0.2), "bowl")
shot("L33.2", F(GP + 0.0, 3.7, 2.8, 1.5, 40, dx=0.0, push=0.2), "work")
# L34: him small, the wall huge
shot("L34", mv([GP + 0.4, -5.2, 1.4], [GP + 0.4, 3.4, 1.9], 20, [GP + 0.4, -4.2, 1.4], [GP + 0.4, 3.4, 1.9], 20), "wide34")
# L35: he looks up
beat("grandpa", "L35", expr="warm", head=[0, -8])
shot("L35", F(GCH[0], GCH[1], 1.45, 2.6, 42, dx=0.3, push=0.14), "looksup")
# L36: me on the rug, scared
only("L36", ["grandpa", "me"])
put("grandpa", "L36", list(GCH), 0, expr="warm", arms=[40, 40])
sit("grandpa", "L36")
put("me", "L36", [GP - 0.1, 0.5], 0, expr="scared", arms=[20, 20])
beat("me", "L36.1", expr="scared", arms=[40, 40])
shot("L36", F(GP - 0.1, 0.5, 1.35, 3.0, 40, dx=-0.2, push=0.16), "scared")
# L37: he gets up and looks at the wall (back to us)
only("L37", ["grandpa"])
put("grandpa", "L37", [GP + 0.5, 3.1], 50, expr="soft", arms=[0, 0])
sit("grandpa", "L37", False)
beat("grandpa", "L37.1", yaw=35, head=[0, 4])
shot("L37", F(GP + 0.5, 3.1, 1.5, 3.0, 36, dx=-0.2, push=0.12, rise=0.1), "back")
# L38: asks about Carol (facing us, in front of the wall)
put("grandpa", "L38", [GP + 0.4, 3.1], 0, expr="sad-smile")
shot("L38", F(GP + 0.4, 3.1, 1.45, 2.4, 42, dx=0.2, push=0.16), "carol")

# ===== 06 the reveal (L39 to L46)
cue("L39", "look", id="day", dur=0.8)
cue("L39+0.9", "tv", v=0.0)
cue("L39", "pollen", level=1.0)
only("L39", ["grandpa"])
put("grandpa", "L39", list(GCH), 0, expr="sad-smile", arms=[40, 40])
sit("grandpa", "L39")
shot("L39", F(GP + 2.2, 2.0, 1.1, 3.5, 21, push=0.1), "reveal")
shot("L40", mv([GP + 2.4, -2.8, 1.2], [GP + 2.4, 2.0, 1.2], 30, [GP + 2.25, -3.1, 1.25], [GP + 2.25, 2.0, 1.25], 28), "photo")
beat("grandpa", "L41", expr="sad-smile")
acting["grandpa"].append({"at": "L41", "pos": list(GCH), "side": [0, 60]})
shot("L41", F(GCH[0] - 0.1, GCH[1], 1.2, 3.1, 38, dx=0.0, push=0.1), "hand2")
beat("grandpa", "L42", expr="warm", side=[0, 0])
shot("L42", mv([GP - 3.2, -2.2, 2.0], [GP - 2.0, 3.8, 2.1], 26, [GP + 2.4, -2.2, 2.0], [GP + 1.4, 3.8, 2.1], 26), "wall2")
# L43: morning, the pill bottle
only("L43", [])
cue("L43", "look", id="day", dur=0.6)
shot("L43", F(KT + 0.62, 3.2, 1.05, 1.9, 38, dx=-0.3, push=0.14), "pill3")
only("L44", ["mom"])
put("mom", "L44", [KT - 2.4, 2.45], 0, expr="soft", arms=[40, 0])
beat("mom", "L44.1", expr="soft", head=[0, 0])
shot("L44", F(KT - 2.4, 2.45, 1.4, 2.9, 40, dx=0.1, push=0.16), "stove2")
beat("mom", "L44.1+0.2", expr="worried", head=[-22, 0], yaw=-15)
shot("L44.1", F(KT - 2.4, 2.45, 1.4, 2.7, 40, dx=0.15, push=0.14), "stove3")
only("L45", ["grandpa"])
put("grandpa", "L45", [GP + 4.0, 1.4], 25, expr="sad-smile")
beat("grandpa", "L45.1", expr="sad-smile", head=[20, 0])
shot("L45", F(GP + 4.0, 1.4, 1.4, 3.0, 40, dx=-0.5, push=0.14), "window")
only("L46", ["mom"])
put("mom", "L46", [KT + 0.2, 2.6], 0, expr="soft", arms=[0, 150])
beat("mom", "L46+0.5", expr="smile", arms=[0, 0])
shot("L46", F(KT + 0.2, 2.6, 1.4, 3.0, 40, dx=0.3, push=0.14), "mornings1")
put("mom", "L46.1+0.45", [KT - 0.3, 2.6], 0, expr="soft", arms=[0, 150])
shot("L46.1+0.45", F(KT - 0.3, 2.6, 1.45, 3.4, 36, dx=-0.6, push=0.14), "mornings2")
put("mom", "L46.3", [KT + 0.3, 2.55], 0, expr="soft", arms=[0, 150])
shot("L46.3", F(KT + 0.3, 2.55, 1.4, 2.5, 42, dx=0.1, push=0.16), "mornings3")
beat("mom", "L46.3+0.65", expr="sad-smile", arms=[0, 0])
shot("L46.3+0.65", F(KT + 0.2, 2.6, 1.45, 3.3, 36, dx=0.5, push=0.12), "mornings4")

# ===== 07 Mom (L47 to L52)
only("L47", ["mom", "me"])
put("mom", "L47", [KT + 1.85, 1.5], 22, expr="soft")
sit("mom", "L47")
put("me", "L47", [KT - 0.4, 0.9], 0, expr="stunned" if False else "wide")
swirl("L47", KT - 0.4, 0.9, 0.95, 0.9)
shot("L47", F(KT + 1.2, 1.4, 1.3, 5.4, 32, push=0.14), "home")
beat("me", "L47+0.5", expr="polite", yaw=30)
beat("mom", "L48", expr="sad-smile", head=[4, 0])
shot("L48", F(KT + 1.85, 1.5, 1.5, 3.0, 36, dx=-0.2, push=0.1), "carolface")
beat("mom", "L48.1", expr="crying")
beat("mom", "L49", expr="polite", head=[-14, 0])
beat("mom", "L49+0.5", expr="polite", head=[14, 0])
shot("L49", F(KT + 1.85, 1.5, 1.4, 2.7, 40, dx=0.1, push=0.14), "shake")
beat("mom", "L50", expr="sad-smile", head=[0, 22], arms=[55, 55])
shot("L50", F(KT + 1.85, 1.5, 1.4, 2.7, 40, dx=0.1, push=0.14), "hands")
only("L51", ["me"])
put("me", "L51", [KT + 4.15, 1.5], -22, expr="smirk")
sit("me", "L51")
beat("me", "L51.1", expr="smirk", head=[8, 0])
shot("L51", F(KT + 4.15, 1.5, 1.35, 2.7, 40, dx=-0.1, push=0.14), "determined")
sit("me", "L52-0.1", False)
# L52: the pill into the bread box (my back to the camera)
only("L52", ["me"])
put("me", "L52", [KT + 0.35, 2.45], 160, expr="smirk", arms=[0, 75])
cue("L52", "pillpos", u=0.0)
cue("L52+0.2", "pillpos", u=1.0, dur=1.0)
beat("me", "L52+0.3", yaw=160, arms=[0, 85])
shot("L52", mv([KT + 2.5, 1.7, 1.75], [KT + 1.05, 3.2, 1.05], 40, [KT + 2.2, 1.9, 1.6], [KT + 1.1, 3.2, 1.05], 40), "breadbox")

# ===== 08 the field (L53 to L58)
only("L53", ["me", "mom"])
cue("L53", "pollen", level=2.4)
put("mom", "L53", [PK - 0.6, 9.0], 0, expr="soft", arms=[0, 0])
put("me", "L53", [PK + 0.6, 9.0], 0, expr="determined" if False else "smirk")
go("mom", "L53>", [PK - 0.6, -1.0])
go("me", "L53>", [PK + 0.6, -1.0])
shot("L53", F(PK, 3.0, 1.35, 8.5, 32, dx=0.3, push=0.2), "walkin")
put("mom", "L54", [PK - 0.6, 1.0], 0, expr="soft")
put("me", "L54", [PK + 0.6, 1.0], 0, expr="smirk")
go("mom", "L54.1+0.3", [PK - 0.5, -1.0])
go("me", "L54.1+0.3", [PK + 0.6, -1.0])
shot("L54", mv([PK - 0.8, -4.4, 0.55], [PK, 0.4, 1.0], 36, [PK - 0.2, -3.6, 0.7], [PK, 0.4, 1.1], 36), "grass1")
shot("L54.1", mv([PK + 1.2, -5.8, 0.6], [PK, -1.0, 0.7], 34, [PK + 0.4, -5.0, 0.8], [PK, -1.0, 0.8], 34), "grass2")
put("mom", "L55", [PK - 0.5, -1.0], 0, expr="crying")
shot("L55", F(PK - 0.5, -1.0, 1.4, 2.6, 42, dx=0.3, push=0.16), "water")
beat("mom", "L56", expr="smirk", head=[10, 0])
beat("mom", "L56.1", expr="smirk", head=[10, 0])
shot("L56", F(PK - 0.5, -1.0, 1.4, 2.5, 42, dx=-0.3, push=0.16), "dare")
beat("mom", "L57", **SNEEZE)
shot("L57", F(PK - 0.5, -1.0, 1.4, 2.8, 40, dx=0.2, push=0.16), "sneezemom")
beat("mom", "L57+0.45", hidden=True)
swirl("L57+0.45", PK - 0.5, -1.0, 0.95, 1.1)
cue("L57+0.55", "pin", v2=1.0, dur=0.4)
shot("L58", F(PK - 0.5, -1.0, 0.8, 3.0, 36, dx=-0.4, push=0.16, rise=0.3), "empty")

# ===== 09 both thinking about me (L59 to L62)
beat("me", "L59", expr="worried", head=[0, -4])
shot("L59", F(PK + 0.6, -1.0, 1.4, 2.6, 42, dx=0.3, push=0.16), "think")
only("L60", ["mom", "grandpa"])
put("grandpa", "L60", list(GCH), 0, expr="wide", arms=[40, 40])
sit("grandpa", "L60")
put("mom", "L60", [GP + 0.35, 1.25], 0, expr="wide", arms=[0, 0])
swirl("L60", GP + 0.35, 1.25, 0.95, 1.0)
shot("L60", F(GP + 0.9, 1.6, 1.4, 4.4, 34, dx=0.0, push=0.1), "momlands")
only("L61", ["me"])
put("me", "L61", [PK + 0.6, -1.0], 0, expr="smirk")
beat("me", "L61.0+0.5", **SNEEZE)
beat("me", "L61+0.9", hidden=True)
swirl("L61+0.9", PK + 0.6, -1.0, 0.95, 1.0)
shot("L61", F(PK + 0.6, -1.0, 1.4, 2.8, 40, dx=-0.2, push=0.16), "sneezeme")
only("L62", ["grandpa", "mom", "me"])
cue("L62", "cup3", v=1.0)
put("grandpa", "L62", list(GCH), 0, expr="sad-smile", arms=[40, 40])
sit("grandpa", "L62")
put("mom", "L62", [GP + 0.6, 2.0], 0, expr="sad-smile", arms=[0, 0])
put("me", "L62", [GP + 1.2, 3.2], 0, expr="wide")
swirl("L62", GP + 1.2, 3.2, 0.95, 1.0, sz=1.0)
cue("L62", "pin", v=1.0, v2=1.0)
shot("L62", F(GP + 1.1, 2.1, 1.55, 4.05, 30, push=0.04), "reunion")
shot("L62.3", F(GP - 0.25, 1.0, 0.66, 1.5, 36, dx=-0.7, dz=0.5, push=0.12), "threecups")
shot("L63", TOP(GP - 0.2, 1.0, 0.6, 2.4, 34, dy=0.9), "tray3")

# ===== 10 warm (L64 to L69)
shot("L64", F(GP + 0.2, 2.1, 1.3, 4.5, 36, push=0.14), "silence")
put("mom", "L65", list(GSOFA_R), 0, expr="sad-smile")
sit("mom", "L65")
hold("mom", "L65")
beat("mom", "L65", expr="sad-smile", arms=[0, 85], head=[-14, -6])
shot("L65", F(GSOFA_R[0], GSOFA_R[1], 1.4, 2.5, 42, dx=0.3, push=0.16), "momwall")
shot("L65.2", mv([GP - 1.2, -3.6, 2.4], [GP - 0.8, 3.8, 2.2], 26, [GP - 0.4, -2.8, 2.4], [GP - 0.4, 3.8, 2.2], 26), "wall3")
acting["grandpa"].append({"from": "L66", "to": "L67", "flap": True, "mouth": [0.0, 0.4]})
beat("grandpa", "L66", expr="smile", head=[6, 3])
beat("grandpa", "L66.1", expr="smile", head=[-6, 3])
shot("L66", F(GCH[0], GCH[1], 1.4, 2.5, 42, dx=-0.3, push=0.16), "hum3")
acting["mom"].append({"from": "L67", "to": "L68", "flap": True, "mouth": [0.0, 0.4]})
beat("mom", "L67", expr="sad-smile", arms=[0, 85], head=[6, 3])
beat("mom", "L67.1", expr="smile", head=[-6, 3])
shot("L67", F(GSOFA_R[0], GSOFA_R[1], 1.4, 2.4, 42, dx=0.1, push=0.16), "hum4")
hold("mom", "L68-0.1", False)
only("L68", ["mom"])
put("mom", "L68", [KT - 2.4, 2.45], 0, expr="grin")
beat("mom", "L68+0.8", **SNEEZE)
beat("mom", "L68+1.2", expr="smile", head=[0, 0])
shot("L68", F(KT - 2.4, 2.45, 1.4, 3.0, 40, dx=0.3, push=0.14), "sneezes")
cue("L68", "pollen", level=1.8)
beat("mom", "L69", expr="smile", head=[0, 3])
shot("L69", F(KT - 2.4, 2.45, 1.45, 2.4, 42, dx=-0.1, push=0.16), "pollen")
only("L69>-0.15", ["me"])
put("me", "L69>-0.15", [PK, -8.0], 0, expr="squeeze", head=[0, 6])
cue("L69>-0.15", "pollen", level=2.4)
shot("L69>-0.15", F(PK, -8.0, 1.4, 3.3, 40, dx=0.15, push=0.0), "loop")

OVR = {}
SH[:] = [(a, OVR.get(nm, c), st, h, f, nm) for (a, c, st, h, f, nm) in SH]

# ---------------------------------------------------------------------------------------------- finish
for k_ in acting.values():
    remap_all(k_)
remap_all(cues)
shots, names = [], {}
for i, (at, camera, step, hand, follow, nm) in enumerate(SH):
    s = {"id": f"S{i + 1:02d}", "cam": camera, "step": step}
    if i:
        s["at"] = remap(at)
    if hand is not None:
        s["hand"] = hand
    if follow:
        s["follow"] = follow
    shots.append(s)
    names[nm] = s["id"]

sfx = [
    {"at": "L01.2", "kind": "hit", "db": -9},
    {"at": "L27.2", "kind": "whoosh", "db": -21},
    {"at": "L57+0.45", "kind": "whoosh", "db": -21},
    {"at": "L62.3", "kind": "click", "db": -20, "lp": 3000},
    {"at": "L11", "kind": "click", "db": -22},
    {"at": "L21", "kind": "click", "db": -22, "lp": 3000},
    {"at": "L51", "kind": "click", "db": -23, "lp": 3000},
    {"at": "L21.1", "kind": "click", "db": -22},
    {"at": "L39", "kind": "hit", "db": -16},
    {"at": "L52+0.9", "kind": "thud", "db": -20},
    {"at": "L12.2", "kind": "thud", "db": -22},
]
music = {
    "root": 55, "mode": "major", "bpm": 108, "seed": 110,
    "sections": [
        {"at": 0, "voices": ["piano", "bubble", "pulse"], "energy": 0.5, "root": 55, "mode": "major"},
        {"at": "L09", "voices": ["piano", "pad"], "energy": 0.35, "root": 55, "mode": "minor"},
        {"at": "L27", "voices": ["drone", "pad"], "energy": 0.45, "root": 43, "mode": "minor"},
        {"at": "L39", "voices": ["pad", "piano"], "energy": 0.32, "root": 55, "mode": "minor"},
        {"at": "L43", "voices": ["piano", "pad"], "energy": 0.35, "root": 55, "mode": "minor"},
        {"at": "L47", "voices": ["pulse", "piano", "pad"], "energy": 0.5, "root": 55, "mode": "minor"},
        {"at": "L62", "voices": ["piano", "bubble", "pad"], "energy": 0.45, "root": 55, "mode": "major"},
    ],
}
sound = {
    "floor": "wood", "steps_db": -26,
    "ambience": [{"kind": "hum", "from": "L28", "to": "L38>", "lufs": -38}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
remap_all(sfx)
remap_all(music["sections"])
remap_all(sound["music_drops"])
remap_all(sound["ambience"])
polish = {"whoosh_lp": 2500.0, "reveal": [remap("L39")], "twist": remap("L39"),
          "emph": [remap(x) for x in ["L01.2", "L04.2", "L07.3", "L09.1", "L11.1", "L19", "L31", "L34", "L39.0", "L44.2", "L57"]],
          "quiet": [[remap("L64"), remap("L67")]],
          "sway": [names[n] for n in ("dark2", "awake1", "awake2", "pastshoulder", "portrait", "wall1", "clip1", "scared", "back")],
          "hold": [names[n] for n in ("wall1", "wide34", "reunion", "tray1", "tray3", "cookies", "kitchen0", "momlands", "carolface")]}
story = {
    "staging_ok": [names["kitchen0"] + "/me+mom walking-close, side by side, no overlap",
                   names["walkin"] + "/me+mom walk together, deliberate contact",
                   names["grass1"] + "/me+mom walk together, deliberate contact",
                   names["grass2"] + "/me+mom walk together, deliberate contact",
                   names["reunion"] + "/reunion: grandpa in his armchair, mom beside, me landing",
                   names["hum3"] + "/me+grandpa seated grandpa, me beside, no overlap"],
    "framing_ok": ["S12", "S14", names["gone1"], names["couch1"], names["party2"], names["tray3"]],
    "slug": "ep110-bless-you",
    "title": "Every Sneeze Lands Me by a STRANGER 🤧",
    "made_for_kids": False,
    "premise": ("In a pollen-gold spring town every sneeze carries you to whoever is thinking about you most; sixty-three "
                "sneezes in a row have landed me beside the same old man in a green armchair, with two cups of tea "
                "already poured, while my mom has never sneezed once."),
    "twist": ("The old man is my mom's dad, who has thought about me every day of my life, and Mom takes an allergy pill "
              "every morning so she never sneezes and lands next to him; I walk her through the pollen, she sneezes to "
              "him, and I sneeze after her."),
    "world": ("A pastel spring town of drifting gold pollen: a field of tall yellow grass with a path and a bench, a "
              "downtown street, an old man's deep-green and cream front room with an armchair, a tea tray and a wall of "
              "newspaper clippings, a blue stove in a family kitchen."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffd23f",
    "gap": 0.12,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#e6f2ff", "fog_density": 0.003, "fog_start": 30.0, "sky": "#9fd8ff",
             "sky_strength": 1.0, "exposure": 0.2, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.04, 0.02, -0.02], "saturation": 1.12, "contrast": 1.05,
              "vignette": 0.2, "bloom": 0.2, "grain": 0.008},
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
    "clip_ok": [],
    "asr_forgive": [],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
print({k: v for k, v in names.items()})
