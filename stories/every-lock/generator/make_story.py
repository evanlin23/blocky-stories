"""Writes ../story.json for "My Bathroom Door Has 1,024 LOCKS" (every-lock, script.md).

Run from anywhere: python stories/every-lock/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, who
stands where in each shot, the cues set.py reads (lock counts, the pile, the meter, the light, the props), the score
and the sound. A shot over 1.95 s is split into punch-ins (the voice timings decide, so run `voice` first; the
split refs are line-relative, so a re-voice keeps them close).
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

K, DK, ST, SR = 40.0, 80.0, 120.0, 160.0


def split_chunks(lines):
    """Captions show two or three words at a time: split any longer chunk, and remember where each original chunk went."""
    remap = {}
    for ln in lines:
        new = []
        for j, (cap, spk) in enumerate(ln["chunks"]):
            cw, sw = cap.split(), spk.split()
            remap[(ln["id"], j)] = len(new)
            if len(cw) <= 3 or len(cw) != len(sw):
                new.append([cap, spk])
                continue
            n = len(cw)
            k = 2 if n == 4 else 3
            sizes = [k, n - k] if n <= 6 else [3] * (n // 3) + ([n % 3] if n % 3 else [])
            i = 0
            for sz in sizes:
                new.append([" ".join(cw[i:i + sz]), " ".join(sw[i:i + sz])])
                i += sz
        ln["chunks"] = new
    return remap


import re as _re
REMAP = split_chunks(lines)


def R(ref):
    """Rewrite a chunk ref (L04.2) written against the script's chunks to the split chunks."""
    if not isinstance(ref, str):
        return ref
    return _re.sub(r"(L\d+b?)\.(\d+)", lambda m: f"{m.group(1)}.{REMAP.get((m.group(1), int(m.group(2))), int(m.group(2)))}", ref)


def insert_pause(lines, before, pid, dur):
    i = next(k for k, l in enumerate(lines) if l["id"] == before)
    lines.insert(i, {"id": pid, "pause": dur, "chunks": []})


insert_pause(lines, "L36", "P01", 0.6)
insert_pause(lines, "L68", "P02", 0.6)
for _l in lines:
    if _l["id"] == "L41":
        _l["tempo"] = 0.9
lines.append({"id": "P03", "pause": 0.12, "chunks": []})

# ---------------------------------------------------------------------------------------------------- cast
cast = {}


def person(name, age, skin, shirt, pants, shoes, hair, hair_c, sleeves="short", pattern="solid", hat="none", hat_c=None,
           extras=None, extra_c=None, height=1.0, eyes="round", pattern_c=None):
    d = {"age": age, "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "height": height, "width": 0.9,
         "face": {"eyes": eyes, "brows": True}}
    if hat_c:
        d["hat_c"] = hat_c
    if extras:
        d["extras"] = extras
    if extra_c:
        d["extra_c"] = extra_c
    if pattern_c:
        d["pattern_c"] = pattern_c
    cast[name] = d


person("me", "teen", "#e0ac69", "#e3a62f", "#8a8f99", "#f4f4f4", "cap", "#4a3020", sleeves="long", pattern="stripes",
       pattern_c="#1f2f5a", extras=["hooddown"], extra_c="#e3a62f")
person("jade", "adult", "#c98d62", "#3fb8b0", "#26324f", "#f2a0c0", "long", "#15151a", eyes="lashes")
person("jadeb", "adult", "#c98d62", "#3fb8b0", "#26324f", "#f2a0c0", "long", "#15151a", eyes="lashes",
       extras=["hooddown", "scarf"], extra_c="#b9a0e0")
person("mom", "adult", "#e0b080", "#f08a6c", "#3a3f58", "#2b2e36", "swoop", "#6a4a2a", sleeves="long",
       extras=["glasses"], height=0.96)
person("downstairs", "adult", "#d4a373", "#4a9a5a", "#3a5a4a", "#6a4a2a", "none", "#2a1a10", sleeves="long")
person("bro1", "adult", "#b57a52", "#c0392b", "#2d3a5c", "#262626", "spiky", "#2a1a10", sleeves="long", pattern="plaid",
       pattern_c="#2b0f0c")
person("bro2", "adult", "#8d5524", "#c0392b", "#2d3a5c", "#262626", "cap", "#1a1a1a", sleeves="long", pattern="plaid",
       pattern_c="#2b0f0c", hat="beanie", hat_c="#3a3a40")
person("pike", "adult", "#e8c9a0", "#8a55b8", "#6a4a8a", "#e0c0e8", "bun", "#f2f2f2", sleeves="long",
       hat="beanie", hat_c="#bfe6f2", extras=["glasses"], height=0.92)
person("dale", "adult", "#d9a77a", "#c8a878", "#5a4a3a", "#7a5a3a", "swoop", "#b8b8b8", sleeves="long", height=0.98)
person("fa1", "adult", "#c68642", "#f2b01e", "#2d3a8c", "#262626", "buzz", "#2a1a10")
person("fa2", "adult", "#e0ac69", "#e8453c", "#1e6e5a", "#262626", "long", "#6a3a1a")
person("fb1", "adult", "#a96b44", "#7a4cc2", "#2b2e36", "#262626", "buzz", "#1a1a1a", sleeves="long")
person("fb2", "adult", "#d4a373", "#2fa4e0", "#5a3a8a", "#262626", "bun", "#3a2a1a")

# ---------------------------------------------------------------------------------------------------- DSL
SH = []


def S(ref, cam, who=None, cues=(), step=2, note=""):
    SH.append({"ref": R(ref), "cam": cam, "who": who or {}, "cues": [(R(r), n, f) for r, n, f in cues], "step": step, "note": note})


def cam(loc, tgt, lens):
    return [[0, list(loc), list(tgt), lens]]


def fit(c, hmin=1.5):
    """Pull a close camera back (and widen the lens) so the frame is at least hmin metres tall at the subject."""
    out = []
    for k in c:
        loc, tgt, lens = k[1], k[2], k[3]
        d = [loc[i] - tgt[i] for i in range(3)]
        dist = math.sqrt(sum(x * x for x in d)) or 1e-6
        h = 24.0 * dist / lens
        if h < hmin:
            nd = dist * math.sqrt(hmin / h)
            lens = max(14.0, 24.0 * nd / hmin)
            f = nd / dist
            loc = [tgt[0] + d[0] * f, tgt[1] + d[1] * f, tgt[2] + d[2] * f]
        out.append([k[0], list(loc), list(tgt), round(lens, 1)] + k[4:])
    return out


def headfit(c, who, top=1.78, share=0.68):
    """Widen (then pull back) a camera until every standing character's head is inside the frame (critic r1: headless
    torsos), and keep a hall camera off the hall's walls (a camera outside a wall draws black)."""
    heads = []
    for w in (who or {}).values():
        pos = w["pos"]
        z = pos[2] if len(pos) > 2 else 0.0
        if 0.2 < z < 0.35 or w.get("lean", 0) > 20:
            continue
        heads.append((pos[0], pos[1], z + top))
    out = []
    for k in c:
        loc, tgt, lens = list(k[1]), list(k[2]), k[3]
        for _ in range(30):
            v = [tgt[i] - loc[i] for i in range(3)]
            n = math.sqrt(sum(x * x for x in v)) or 1e-6
            v = [x / n for x in v]
            up = [-v[2] * v[0], -v[2] * v[1], 1 - v[2] * v[2]]
            un = math.sqrt(sum(x * x for x in up)) or 1e-6
            up = [x / un for x in up]
            bad = False
            for h in heads:
                rel = [h[i] - loc[i] for i in range(3)]
                depth = sum(rel[i] * v[i] for i in range(3))
                vert = sum(rel[i] * up[i] for i in range(3))
                rt = [v[1] * up[2] - v[2] * up[1], v[2] * up[0] - v[0] * up[2], v[0] * up[1] - v[1] * up[0]]
                horiz = sum(rel[i] * rt[i] for i in range(3))
                half = depth * 12.0 / lens
                if depth > 0.2 and (vert > half * share or abs(horiz) + 0.22 > half * 0.5625 * 0.9):
                    bad = True
            if not bad:
                break
            if lens > 14.5:
                lens = max(14.0, lens * 0.92)
            else:
                f = 1.08
                loc = [tgt[i] - (tgt[i] - loc[i]) * f for i in range(3)]
        if -1.3 < loc[0] < 1.3 and (0.2 < loc[1] < 6.9 or -8.3 < loc[1] < -2.5) and abs(loc[0]) > 0.72:
            loc[0] = math.copysign(0.72, loc[0])
        out.append([k[0], loc, tgt, round(lens, 1)] + k[4:])
    return out


def dolly(a, b, ta, tb, la, lb=None):
    return [[0, list(a), list(ta), la], [1, list(b), list(tb), lb or la]]


def P(x, y, yaw=0, expr="neutral", z=0.0, **kw):
    d = {"pos": (x, y, z), "yaw": yaw, "expr": expr}
    d.update(kw)
    return d


def fy(pos, cam_loc, off=0.0):
    """The yaw that makes a character at pos face a camera at cam_loc."""
    return round(math.degrees(math.atan2(cam_loc[0] - pos[0], -(cam_loc[1] - pos[1]))) + off, 1)


def FP(x, y, c, expr="neutral", z=0.0, off=0.0, **kw):
    return P(x, y, fy((x, y), c, off), expr, z, **kw)


def DR(**kw):
    return (None, "door", kw)


def MT(v, dur=0.0, ref=None):
    return (ref, "meter", {"v": v, "dur": dur})


def CU(name, ref=None, **kw):
    return (ref, name, kw)


ANNOYED, SMUG, SHEEP = "angry", "smirk", "polite"
HOLE_JADE = [-0.5, 0.5, 4.3, 6.4, 0.2, 2.3]
def MEHOLE(x, y):
    """A clearing in the pile around a standing character (the pile keeps off their head)."""
    return [x - 0.9, x + 0.9, y - 0.9, y + 0.9, 0.0, 2.4]


HOLE_HINGE = [-0.9, 0.7, 3.2, 7.0, 0.0, 2.3]
FRONT = (0.0, 5.0, 1.25)

# ---------------------------------------------------------------------------------------------------- the shots
# 01 the rule (L01 to L10b)
S(0, dolly((0, 4.6, 1.22), (0, 5.6, 1.2), (0, 7, 1.1), (0, 7, 1.1), 19, 24), note="frame 1: the 1,024-lock door, pushing in",
  cues=[DR(n=1024, L=0.4, lean=4.0, swing=0.0), MT(1024), CU("flap", a=70.0), CU("keys", v=0.0)], step=1)
S("L01.3", dolly((0.0, 5.9, 1.55), (0.3, 5.7, 1.85), (0.1, 7, 1.6), (0.17, 6.6, 1.86), 40, 55), note="a punch in across the locks, the flaps glint; the clunk",
  cues=[CU("shudder", ref="L01>-0.2")])
S(
    "L02", cam((K - 0.8, 1.9, 1.0), (K - 0.8, 3.64, 0.95), 26),
    {"me": P(K + 0.15, 3.0, -90, "neutral")}, note="the cupboard: a second lock pops on",
    cues=[CU("cupboard", a=60.0), CU("cupboard", ref="L02+0.1", a=0.0, dur=0.25), CU("cuplock", ref="L02.1")])
S("L02b", cam((K - 0.7, 2.9, 0.95), (K - 0.7, 3.64, 0.95), 55), {"me": P(K - 0.2, 3.0, -90, "angry")},
  note="my hand tugs at the new lock; it holds", cues=[CU("cupboard", a=0.0)])
S("L03", cam((DK + 1.8, 0.6, 1.45), (DK - 0.4, 3.0, 1.05), 22),
  {"downstairs": FP(DK - 0.1, 2.4, (DK + 1.8, 0.6), "neutral")}, note="the man by his open fridge",
  cues=[CU("fridge", a=70.0), CU("dknight", v=0.0), CU("frtiny", on=False)])
S("L03.1", cam((DK + 1.5, 0.9, 1.5), (DK - 0.1, 2.5, 1.45), 30), {"downstairs": FP(DK - 0.1, 2.4, (DK + 1.5, 0.9), "squeeze")},
  note="the sneeze, the fridge door swings shut", cues=[CU("fridge", ref="L03.1+0.45", a=0.0, dur=0.3)])
S("L04", cam((DK + 1.6, 0.2, 1.4), (DK - 0.1, 3.2, 1.1), 20), {"downstairs": FP(DK + 0.6, 2.4, (DK + 1.6, 0.2), SHEEP)},
  note="the 64-lock fridge, the man sheepish", cues=[CU("frtiny", on=True)])
S("L04+0.7", cam((DK - 0.1, 2.7, 1.68), (DK - 0.1, 3.25, 1.62), 70), note="plant 1: the little keyhole flaps, a tiny lock growing")
S("L04+1.5", cam((DK - 0.2, 3.0, 1.35), (DK + 1.2, 1.0, 0.3), 24), note="the cooler and the milk (held: no swoop, the 8.3 s flash fix)")
S("L05", dolly((-11.8, -1.2, 1.4), (-8.0, -1.2, 1.4), (-9.0, 0.0, 1.2), (-6.0, 0.0, 1.2), 17), note="open front doors on our floor, one propped with a boot")
S("L05+0.9", dolly((1.0, -0.6, 1.4), (5.0, -0.6, 1.4), (3.0, -2.4, 1.2), (7.0, -2.4, 1.2), 17), note="across the hall, more open doors")
S("L06", cam((-6.0, -0.6, 1.45), (-6.0, -5.0, 1.0), 19),
  {"fa1": P(-6.7, -4.5, 180, "grin", arms=[55, 0]), "fa2": P(-5.3, -4.5, 180, "smile", arms=[0, 55])}, note="a family at dinner")
S("L06+0.7", cam((6.0, -0.6, 1.45), (6.0, -5.0, 1.0), 19),
  {"fb1": P(5.3, -4.5, 180, "smile", arms=[55, 0]), "fb2": P(6.7, -4.5, 180, "grin", arms=[0, 55])}, note="another table")
S("L07", cam((ST - 0.1, 0.28, 1.45), (ST - 0.1, -0.8, 1.5), 14),
  {"bro1": P(ST - 0.55, -0.85, 90, "angry", mouth=True), "bro2": P(ST + 0.4, -0.85, -90, "angry", mouth=True)},
  note="the brothers nose to nose on the landing")
S("L07.3", cam((ST - 0.9, 4.3, -1.8), (ST + 0.2, -0.6, 1.6), 18), note="low up the stairwell: no door anywhere")
S("L08", cam((ST + 0.9, -1.2, 1.5), (ST - 1.55, -0.4, 1.3), 20), note="Mrs. Pike's front door stands open")
S("L08.1", cam((ST - 2.8, 0.0, 1.55), (ST - 4.2, 0.0, 1.45), 24), {"pike": P(ST - 4.9, 0.0, 90, "neutral", mouth=True)},
  note="her bathroom doorway: shower cap above the curtain, singing")
S("L09", cam((ST - 3.0, 0.0, 1.58), (ST - 4.9, 0.0, 1.58), 40), {"pike": P(ST - 4.9, 0.0, 90, "smile", mouth=True)},
  note="punch in: she sings louder")
S("L10", cam((0.0, 0.2, 1.5), (0.0, -3.0, 1.35), 16), {"dale": P(0.0, -2.75, 180, "smile")},
  note="Mr. Dale in his open doorway, curb finds behind him")
S("L10.2", dolly((SR - 3.5, 0.2, 1.0), (SR - 2.6, 0.2, 1.0), (SR, 3.8, 1.0), (SR, 4.4, 1.1), 26),
  {"dale": P(SR - 0.2, 2.2, 0, "smile", arms=[75, 75], to=[(SR, 4.9, 0.3)])}, note="he carries a curb lamp up the front steps",
  cues=[CU("carry", on=True), CU("frtiny", ref="L10", on=False)])
S("L10b", cam((DK + 2.2, 0.2, 1.5), (DK - 0.2, 3.4, 1.0), 18), note="the downstairs kitchen at night, nobody in it",
  cues=[CU("dknight", ref="L10b-0.6", v=1.0, dur=0.4), CU("carry", on=False), CU("frflap", ref="L10b-0.6", a=70.0)])
S("L10b.2", cam((DK - 0.1, 2.4, 1.66), (DK - 0.1, 3.25, 1.62), 65), note="a flap swings shut and something tiny buds",
  cues=[CU("frflap", ref="L10b.2+0.1", a=0.0, dur=0.12), CU("frtiny", ref="L10b.2+0.45", on=True)])
# 02 me and Jade (L11 to L15)
S("L11", cam((0.5, 2.4, 1.5), (-0.9, 4.7, 1.35), 22), {"me": FP(-1.0, 4.55, (0.5, 2.4), "smile")},
  note="me in my doorway, my door wide open", cues=[CU("dknight", ref="L11", v=0.0, dur=0.4)])
S("L11.2", cam((0.3, 3.6, 1.4), (-0.8, 5.3, 1.2), 26), {"me": FP(-1.0, 4.55, (0.3, 3.6), "smile")}, note="not a single lock on it")
S("L12", cam((-0.5, 2.9, 1.5), (0.5, 4.4, 1.3), 24), {"jade": FP(0.2, 3.7, (-0.5, 2.9), ANNOYED), "me": FP(-0.6, 4.3, (-0.5, 2.9), "neutral")},
  note="Jade steps past me; her door behind her has 16 locks")
S("L12.1", cam((-0.2, 3.2, 1.5), (0.2, 3.8, 1.5), 32), {"jade": FP(0.2, 3.7, (-0.2, 3.2), ANNOYED)}, note="she slams them")
S("L12b", cam((0.0, 5.2, 1.3), (0.0, 7.0, 1.1), 20), note="a month ago: the plain yellow door, four locks; the meter winds back",
  cues=[DR(n=4, L=0.0, lean=0.0, swing=0.0), MT(4, dur=0.5)])
S("L12b.2", cam((0.2, 6.0, 1.1), (0.2, 7.0, 1.1), 32), note="four locks")
S("L13", cam((K - 0.5, 1.4, 1.5), (K - 1.9, 4.1, 1.8), 22), note="the kitchen clock at 7:15", cues=[CU("clock", h=7.25)])
S("L13.1", cam((-0.85, 4.0, 1.55), (0.0, 5.5, 1.5), 22),
  {"me": P(-0.3, 5.4, 160, ANNOYED), "jade": P(0.3, 5.4, 160, ANNOYED)}, note="the two of us facing the bathroom door")
S("L14", cam((0.0, 6.3, 1.4), (0.0, 1.5, 1.2), 20),
  {"me": P(-0.4, 1.0, 180, ANNOYED, to=[(-0.4, 5.0)], run=True), "jade": P(0.4, 1.1, 180, ANNOYED, to=[(0.4, 5.2)], run=True)},
  note="shoulder to shoulder, racing down the hall")
S("L15", cam((0.5, 5.1, 1.5), (0.0, 7.0, 1.3), 22), {"jade": P(0.0, 7.7, 0, SMUG)}, note="Jade inside the doorway, the door swinging",
  cues=[DR(swing=80.0)])
S("L15.2", cam((0.8, 5.2, 1.5), (0.0, 6.8, 1.3), 20), {"me": FP(0.0, 6.1, (0.8, 5.2), ANNOYED)}, note="shut in my face: four new locks",
  cues=[DR(swing=0.0, dur=0.14), DR(ref="L15.2+0.14", n=8), MT(8, ref="L15.2+0.14")])
# 03 doubling (L16 to L35)
S("L16", cam((0.7, 5.1, 1.5), (0.0, 6.8, 1.3), 22), {"me": FP(0.1, 6.2, (0.7, 5.1), ANNOYED)}, note="me working a key into a lock")
S("L16.2", cam((0.25, 5.9, 1.2), (0.25, 7.0, 1.2), 34), note="the eight locks, half open")
S("L17", cam((0.4, 6.2, 1.95), (0.29, 6.97, 1.95), 62), note="plant 2: one new lock, its flap swinging and settling half shut",
  cues=[CU("swingflap", a=60.0), CU("swingflap", ref="L17+0.25", a=24.0, dur=0.5)])
S("L18", cam((-0.1, 1.5, 0.95), (-0.55, 0.55, 0.3), 30), note="the key bucket", cues=[CU("keys", v=0.8), DR(n=16), MT(16)])
S("L19", cam((0.7, 4.5, 1.2), (0.1, 6.6, 1.0), 24), {"me": FP(-0.2, 5.7, (0.7, 4.5), "neutral")}, note="rows of locks, me and the bucket",
  cues=[CU("bucketat", loc=(0.25, 5.5, 0.0)), DR(n=32), MT(32), DR(ref="L19+0.4", n=64), MT(64, ref="L19+0.4")])
S("L20", cam((3.9, 4.4, 1.45), (3.9, 6.3, 1.0), 24), {"jade": P(3.9, 6.15, 0, SMUG, z=0.28)}, note="Jade in bed, a phone glowing",
  cues=[CU("bucketat", loc=(-0.55, 0.55, 0.0))])
S("L20.2", cam((2.5, 6.7, 1.5), (3.9, 6.0, 1.0), 30), {"jade": P(3.9, 6.15, 0, SMUG, z=0.28)}, note="dawn at her window",
  cues=[CU("night", ref="L21-0.5", v=0.55, dur=0.45)])
S("L21", cam((-3.9, 4.5, 1.4), (-3.9, 6.3, 1.0), 24), {"me": P(-3.9, 6.15, 0, "worried", z=0.28)}, note="me in bed in the dark blue")
S("L22", cam((0.7, 5.2, 1.5), (0.0, 7.0, 1.3), 22), {"jade": P(0.0, 7.7, 0, SMUG)}, note="Jade already at the bathroom door; the slam",
  cues=[DR(swing=80.0), DR(ref="L22>-0.35", swing=0.0, dur=0.14), DR(ref="L22>-0.3", n=128), MT(128, ref="L22>-0.3")])
S("L23", cam((K - 0.5, 0.6, 1.5), (K - 0.5, 2.6, 1.4), 22), {"mom": P(K - 0.5, 2.4, 0, ANNOYED, arms=[85, 0])},
  note="Mom points at the hall", cues=[CU("night", v=0.0, dur=0.4), CU("keys", v=0.8)])
S("L23.2", cam((K - 0.3, 0.2, 1.5), (K - 0.3, 1.6, 1.3), 22),
  {"me": P(K - 0.9, 1.9, 0, SHEEP), "jade": P(K + 0.4, 1.9, 0, SHEEP)}, note="both sheepish at the table")
S("L24", cam((4.5, -1.9, 1.4), (0.0, -0.8, 1.3), 18), {"jade": P(0.0, 0.9, 0, "worried", to=[(0.0, -1.2), (5.5, -1.2)], run=True)},
  note="Jade runs out the front door", cues=[DR(n=256), MT(256)])
S("L24.1", cam((ST + 0.9, 3.4, -1.0), (ST - 0.8, 1.4, -0.7), 20),
  {"me": P(ST - 0.8, 0.4, 0, "worried", to=[(ST - 0.8, 3.4, -2.16)], run=True)}, note="me running down the stairs")
S("L25", cam((0.0, 5.0, 1.3), (0.0, 7.0, 1.2), 20), note="no wood left to see",
  cues=[DR(n=512, L=0.12, dur=0.6), MT(512)])
S("L25.2", dolly((-0.35, 6.2, 1.0), (0.35, 6.2, 1.4), (-0.2, 7.0, 1.0), (0.3, 7.0, 1.4), 38), note="a slide across the locks")
S("L26", cam((0.6, 5.0, 1.2), (0.1, 6.2, 0.9), 26), {"me": FP(0.0, 5.9, (0.6, 5.0), ANNOYED, z=0.32)}, note="an hour: me on a stool with the bucket",
  cues=[CU("bucketat", loc=(0.5, 5.6, 0.0)), CU("stoolat", loc=(0.0, 5.9, 0.0))])
S("L26.1", cam((K - 1.6, 2.7, 1.8), (K - 2.0, 4.1, 1.9), 26), note="the clock's hands a whole hour round",
  cues=[CU("clock", h=7.25), CU("clock", ref="L26.1+0.1", h=8.25, dur=1.1), CU("bucketat", ref="L27", loc=(-0.55, 0.55, 0.0)),
        CU("stoolat", ref="L27", loc=(0.5, 5.7, -5.0))])
S("L27", cam((K + 0.2, 2.5, 1.5), (K + 1.0, 3.6, 1.3), 28), {"mom": FP(K + 1.0, 3.2, (K + 0.2, 2.5), "neutral", mouth=True)},
  note="Mom brushes her teeth in the kitchen sink")
S("L28", dolly((0.5, 5.4, 0.7), (0.2, 5.6, 0.45), (0.1, 7.0, 0.4), (0.3, 7.1, 0.12), 24), note="the door ajar, her shoe wedged at its foot",
  cues=[DR(swing=12.0), CU("shoeat", loc=(0.33, 7.14, 0.04), rot=-8.0)])
S("L28.1", cam((0.3, 5.0, 1.5), (0.0, 6.3, 1.4), 26), {"mom": FP(0.0, 6.0, (0.3, 5.0), "smile", arms=[40, 40])}, note="Mom dusts off her hands")
S("L29", cam((0.65, 5.3, 0.3), (0.3, 6.7, 0.1), 28), {"jade": P(0.15, 5.5, 180, ANNOYED, to=[(0.3, 6.5)])}, note="a pink slipper flicks the shoe away",
  cues=[CU("shoeat", ref="L29+0.45", loc=(-0.25, 5.9, 0.04), rot=60.0, dur=0.3)])
S("L30", cam((0.0, 5.0, 1.3), (0.0, 7.0, 1.15), 20), note="the slam: a wave of locks pops on",
  cues=[DR(swing=0.0, dur=0.12), DR(ref="L30+0.1", n=1024, L=0.4, dur=0.5), MT(1024, ref="L30+0.1"),
        CU("shoeat", loc=(0.0, 0.0, -3.0))])
S("L31", cam((-0.55, 4.5, 1.2), (0.35, 7.0, 1.3), 20), note="side-on: the door a lumpy bulge, its top leaning out",
  cues=[DR(ref="L31", lean=4.0, dur=0.6)])
S("L31.2", cam((0.0, 4.3, 1.55), (0.0, 6.3, 1.5), 24), {"jade": FP(0.0, 5.6, (0.0, 4.3), SHEEP)}, note="Jade beside it, the meter above her")
S("L32", cam((-0.85, 3.0, 1.6), (0.2, 5.0, 1.4), 20),
  {"bro1": P(-0.3, 4.4, 210, "wide"), "bro2": P(0.3, 4.8, 210, "wide"), "downstairs": P(0.0, 3.6, 210, "wide"), "pike": P(-0.35, 5.3, 210, "wide")},
  note="the whole floor comes to look")
S("L33", cam((0.0, 3.7, 1.55), (0.0, 5.2, 1.5), 30), {"pike": P(0.0, 5.2, 0, "neutral", mouth=True)}, note="Mrs. Pike: the worst one she's seen")
S("L34", cam((-0.6, 4.2, 1.5), (0.1, 6.0, 1.4), 24), {"dale": P(0.1, 5.75, 196, "smile", arms=[85, 0])},
  note="Mr. Dale tests the locks like a melon")
S("L35", cam((0.0, 5.4, 1.5), (0.2, 3.4, 1.2), 24), {"jadeb": P(0.2, 3.3, 180, ANNOYED)},
  note="Jade sleeps in the hall, evening light", cues=[CU("matat", loc=(0.2, 3.3, 0.0)), CU("night", ref="L35+0.2", v=1.0, dur=1.3)])
# 04 by itself (L36 to L54)
S("L36", cam((-3.9, 4.5, 1.4), (-3.9, 6.3, 1.0), 24), {"me": P(-3.9, 6.15, 0, "worried", z=0.28)}, note="a tiny click: me in bed, moonlight")
S("L36.2", cam((-2.4, 4.55, 1.35), (0.2, 4.55, 1.2), 20), {"jadeb": P(0.2, 3.3, 180, "asleep")}, note="my doorway, the hall in nightlight amber")
S("L37", cam((0.5, 5.7, 1.9), (0.17, 6.5, 1.86), 60), note="a lock high on the pile, its flap catching the light")
S("L37.1", cam((0.3, 6.1, 1.88), (0.17, 6.5, 1.86), 95), note="the keyhole flap, close")
S("L38", cam((0.3, 6.2, 1.88), (0.17, 6.5, 1.86), 110), note="match cut: the flap swings on its tiny hinge",
  cues=[CU("flap", a=70.0), CU("flap", ref="L38+0.1", a=22.0, dur=0.3), CU("flap", ref="L38+0.45", a=70.0, dur=0.3)])
S("L38+0.65", cam((0.0, -6.0, 1.25), (0.0, -8.4, 1.0), 22), note="the same swing: the bathroom door a month ago, in day colours",
  cues=[CU("doorat", loc=(0.0, -8.4, 0.0), rot=180.0), DR(n=4, L=0.0, lean=0.0, swing=0.0), CU("hole", holes=[]),
        DR(ref="L38+0.75", swing=38.0, dur=0.3), DR(ref="L38+1.1", swing=0.0, dur=0.3)])
S("L38+1.3", cam((0.3, 6.2, 1.88), (0.17, 6.5, 1.86), 110), note="back to the flap",
  cues=[CU("doorat", loc=(0.0, 7.0, 0.0), rot=0.0), DR(n=1024, L=0.4, lean=4.0, swing=0.0), CU("flap", a=70.0)])
S("L39", cam((0.3, 6.2, 1.88), (0.17, 6.5, 1.86), 100), note="one of them just swung shut",
  cues=[CU("flap", ref="L39.1", a=0.0, dur=0.1)])
S("L40", cam((0.3, 6.1, 1.88), (0.17, 6.5, 1.86), 95), note="the shut flap, held still")
S("L40.2", cam((0.28, 6.1, 1.9), (0.17, 6.5, 1.86), 120), note="a tiny lock pops onto that lock",
  cues=[CU("tiny")])
S("L41", cam((0.2, 4.4, 1.7), (0.17, 6.6, 1.7), 24), note="CLICK, click click: locks budding on locks",
  cues=[DR(L=0.7, dur=0.5)])
S("L41.2", cam((0.5, 4.3, 1.3), (0.1, 6.6, 1.3), 24), note="click click click click: four",
  cues=[DR(L=1.0, dur=0.4)])
S("L42", cam((0.0, 0.6, 1.55), (0.0, 6.0, 1.2), 17),
  {"jadeb": P(0.2, 3.3, 180, "asleep"), "me": P(-0.85, 4.55, 90, "worried")}, note="nobody's touching it",
  cues=[DR(L=1.25, dur=0.6)])
S("L43", cam((0.4, 2.4, 1.5), (0.0, 6.0, 1.3), 22), note="doubling by itself", cues=[DR(L=1.5, dur=1.0)])
S("L44", cam((0.0, 2.0, 1.5), (0.0, 5.8, 1.3), 22), note="TWO THOUSAND, FOUR THOUSAND: the pile swelling", cues=[MT(2048), MT(4096, ref="L44.1"), DR(L=1.8, dur=0.8)])
S("L44.2", cam((0.2, 2.6, 1.5), (-0.5, 4.0, 1.5), 30), {"me": FP(-0.5, 4.0, (0.2, 2.6), "scared")}, note="EIGHT, my face", cues=[MT(8192)])
S("L45", cam((-0.1, 1.4, 0.9), (-0.55, 0.55, 0.35), 30), note="the key bucket rattles in moonlight",
  cues=[CU("keys", v=1.3, dur=1.4)])
S("L45.2", cam((0.1, 1.0, 0.35), (-0.55, 0.55, 0.2), 28), note="keys slide off onto the floor",
  cues=[CU("dknight", ref="L45.2", v=1.0, dur=0.4), CU("keys", v=1.7, dur=0.5)])
S("L46", cam((DK + 2.0, 0.3, 1.4), (DK, 2.0, 1.6), 22), {"downstairs": FP(DK - 0.8, 1.8, (DK + 2.0, 0.3), "worried", head=[0, -22])},
  note="downstairs the ceiling light starts to swing", cues=[CU("dkswing", a=16.0, dur=0.6), DR(L=2.4, dur=0.0)])
S("L46.2", cam((DK + 0.5, 1.2, 0.6), (DK, 2.0, 2.2), 20), {"downstairs": FP(DK - 0.8, 1.8, (DK + 0.5, 1.2), "worried", head=[0, -22])},
  note="low, up at the light")
S("L47", cam((0.0, 0.8, 1.5), (0.0, 6.0, 1.3), 19), note="by three it fills the hall", cues=[MT(16384)])
S("L47.2", cam((-0.3, 3.6, 1.4), (-0.8, 4.6, 1.4), 24), {"me": FP(-0.5, 4.2, (-0.3, 3.6), "worried")}, note="up to my door",
  cues=[MT(32768, ref="L47.2")])
S("L48", cam((0.2, 3.7, 1.4), (-0.7, 5.3, 1.2), 26), {"me": FP(-0.45, 3.8, (0.2, 3.7), "worried")}, note="it's pushing my door shut",
  cues=[CU("mydoor", a=170.0), CU("mydoor", ref="L48", a=140.0, dur=1.2)])
S("L49", cam((-0.15, 4.5, 1.3), (-0.6, 5.5, 1.2), 42), note="my lockless door, the pile's edge pressing it",
  cues=[CU("mydoor", a=134.0, dur=0.8)])
S("L50", cam((0.3, 4.2, 0.35), (-0.4, 5.2, 0.15), 30), {"me": P(-0.3, 4.85, 0, "angry")}, note="my sneaker against the bottom of my door")
S("L51", cam((0.0, 3.6, 1.6), (0.0, 5.9, 1.55), 26), {"jadeb": P(0.0, 5.9, 0, "worried")},
  note="Jade in a gap of the pile, in her blanket", cues=[CU("hole", holes=[HOLE_JADE]), MT(65536)])
S("L51.1", cam((0.2, 3.4, 1.5), (-0.5, 4.3, 1.5), 30), {"me": FP(-0.55, 4.3, (0.2, 3.4), "worried"), "jadeb": P(0.0, 5.9, 0, "worried")},
  note="me looking back", cues=[CU("hole", holes=[HOLE_JADE, MEHOLE(-0.55, 4.3)])])
S("L52", cam((0.0, 4.3, 1.6), (0.0, 5.9, 1.55), 34), {"jadeb": P(0.0, 5.9, 0, SHEEP, mouth=True)}, note="through the gaps she says she's sorry",
  cues=[CU("hole", holes=[HOLE_JADE])])
S("L53", cam((-0.85, -6.3, 1.5), (0.0, -7.8, 1.4), 24), {"me": P(0.05, -7.4, 0, ANNOYED, arms=[95, 95])},
  note="an earlier morning in day colours: me pounding on the yellow door, it flies shut",
  cues=[CU("doorat", loc=(0.0, -8.4, 0.0), rot=180.0), DR(n=8, L=0.0, lean=0.0, swing=45.0), CU("hole", holes=[]),
        DR(ref="L53+0.9", swing=0.0, dur=0.12)])
S("L53.2", cam((0.0, 4.3, 1.6), (0.0, 5.9, 1.55), 34), {"jadeb": P(0.0, 5.9, 0, SHEEP, mouth=True)}, note="back to Jade in the gap",
  cues=[CU("doorat", loc=(0.0, 7.0, 0.0), rot=0.0), DR(n=65536, L=2.4, lean=4.0, swing=0.0), CU("hole", holes=[HOLE_JADE])])
S("L54", cam((0.0, 3.8, 1.4), (-0.4, 5.1, 0.9), 26), {"me": P(-0.35, 4.85, 0, SHEEP)}, note="I'm sorry too, foot still on the door",
  cues=[CU("hole", holes=[HOLE_JADE, MEHOLE(-0.35, 4.85)]), CU("night", ref="L54>-0.5", v=0.0, dur=0.5)])
# 05 the loophole (L55 to L64)
S("L55", cam((-0.2, 5.0, 1.3), (-0.5, 6.9, 1.2), 24), note="the hall light is on; the hinges, the only bare metal",
  cues=[CU("hole", holes=[HOLE_HINGE, HOLE_JADE])])
S("L56", cam((0.2, 3.6, 1.55), (-0.5, 4.9, 1.5), 28), {"me": FP(-0.5, 4.5, (0.2, 3.6), "smile")}, note="the idea", cues=[CU("hole", holes=[HOLE_HINGE, HOLE_JADE, MEHOLE(-0.5, 4.5)])])
S("L56.2", cam((0.0, 3.7, 1.6), (0.0, 5.9, 1.55), 26), {"jadeb": P(0.0, 5.9, 0, "smile")}, note="Jade smiles back from the gap", cues=[CU("hole", holes=[HOLE_HINGE, HOLE_JADE])])
S("L57", cam((0.2, 5.0, 0.7), (-0.5, 6.7, 0.5), 26), {"me": P(-0.55, 6.2, 0, "neutral", lean=50, z=-0.1)},
  note="the bottom pin, up and out", cues=[CU("pin", ref="L57+0.5", i=0)])
S("L57.1", cam((-0.2, 5.9, 0.9), (-0.45, 6.9, 0.9), 34), {"me": P(-0.55, 6.2, 0, "neutral", lean=50, z=-0.1)},
  note="the middle one, both ringing on the tile", cues=[CU("pin", ref="L57.1+0.1", i=1)])
S("L58", cam((0.2, 3.8, 1.7), (0.0, 5.9, 1.8), 24), {"jadeb": P(0.0, 5.9, 0, "worried", z=0.45, arms=[160, 160])},
  note="Jade on a chair, stretching over the pile", cues=[CU("chairat", loc=(0.0, 5.9, 0.0))])
S("L58+0.65", cam((-0.5, 5.2, 1.78), (-0.5, 6.9, 1.78), 24), note="the bare top hinge plate, three tally strokes beside the screws (held)",
  cues=[CU("pin", ref="L58+0.65", i=2)])
S("L59", cam((0.0, 3.0, 1.5), (0.0, 4.4, 1.5), 22), {"me": P(-0.7, 4.2, 90, "neutral", arms=[40, 40]), "jadeb": P(0.7, 4.2, -90, "neutral", arms=[40, 40])},
  note="a two-person door", cues=[CU("chairat", loc=(0.0, 0.0, -3.0))])
S("L60", cam((0.0, 3.2, 1.6), (0.0, 6.2, 1.2), 20), {"me": P(-0.7, 4.2, 90, "neutral", arms=[60, 60]), "jadeb": P(0.7, 4.2, -90, "neutral", arms=[60, 60])},
  note="we lift it out of the frame", cues=[CU("doorat", loc=(0.0, 7.0, 0.0)), CU("doorat", ref="L60+0.2", loc=(0.0, 5.6, 0.25), dur=0.8)])
S("L60.2", cam((0.0, 3.0, 1.5), (0.0, 4.8, 1.4), 22), {"me": P(-0.65, 4.4, 90, "neutral", arms=[100, 100]), "jadeb": P(0.65, 4.4, -90, "neutral", arms=[100, 100])},
  note="the pile on our shoulders", cues=[CU("doorat", loc=(0.0, 4.9, 0.95), scale=0.5, dur=0.4)])
S("L61", cam((ST + 1.3, -1.4, 2.8), (ST - 0.8, 1.8, -0.8), 22),
  {"me": P(ST - 1.2, 0.4, 0, "neutral", arms=[100, 100], to=[(ST - 1.2, 2.2, -0.9)]),
   "jadeb": P(ST - 0.4, 0.4, 0, "neutral", arms=[100, 100], to=[(ST - 0.4, 2.2, -0.9)])},
  note="down four flights", cues=[CU("doorat", loc=(ST - 0.8, 0.9, 0.0), rot=0.0, scale=0.45), CU("doorat", ref="L61+0.1", loc=(ST - 0.8, 2.7, -0.9), scale=0.45, dur=1.3), MT(131072)])
S("L62", dolly((ST - 0.7, -0.2, 1.0), (ST - 0.7, 1.0, 0.1), (ST - 0.8, 2.0, -0.8), (ST - 0.8, 2.6, -1.3), 24),
  {"me": P(ST - 1.2, 2.2, 0, "neutral", arms=[100, 100], to=[(ST - 1.2, 3.0, -1.6)]),
   "jadeb": P(ST - 0.4, 2.2, 0, "neutral", arms=[100, 100], to=[(ST - 0.4, 3.0, -1.6)])},
  note="every step it clicks louder", cues=[CU("doorat", loc=(ST - 0.8, 2.7, -0.9)), CU("doorat", ref="L62+0.2", loc=(ST - 0.8, 3.5, -1.6), scale=0.45, dur=1.0), DR(L=2.7, dur=1.0)])
S("L63", cam((ST + 1.0, 2.8, -1.2), (ST, 4.1, -1.3), 24), {"jadeb": P(ST, 4.1, 0, "laugh", z=-1.5)},
  note="Jade laughing so hard she sits on it",
  cues=[CU("doorat", loc=(ST, 4.2, -2.16), rot=0.0, scale=0.5), DR(L=2.4)])
S("L63.2", cam((ST - 0.2, 2.4, -1.2), (ST + 0.9, 3.3, -1.4), 28), {"me": FP(ST + 0.9, 3.3, (ST - 0.2, 2.4), "laugh", z=-2.16)}, note="me laughing, leaning on the rail")
S("L64", cam((SR - 4.0, -3.0, 1.2), (SR + 1.5, 3.0, 1.1), 24), note="the pile on end at the curb, car-sized",
  cues=[CU("doorat", loc=(SR + 3.5, 2.6, 0.1), rot=0.0, scale=0.9), DR(L=2.4, lean=0.0)])
S("L64.2", cam((SR - 2.5, -1.6, 1.2), (SR, 3.6, 1.1), 26),
  {"me": P(SR - 0.6, 1.5, 0, "smile", to=[(SR - 0.6, 4.9, 0.3)]), "jadeb": P(SR + 0.4, 1.5, 0, "smile", to=[(SR + 0.4, 4.9, 0.3)])},
  note="backing away, up the front steps")
# 06 the next morning (L65 to L72)
S("L65", cam((0.0, 5.2, 1.3), (0.0, 7.0, 1.1), 20), note="a shower curtain for a door",
  cues=[CU("doorat", loc=(0.0, 7.0, -60.0), rot=0.0, scale=1.0), CU("curtain", v=1.0), DR(swing=0.0)])
S("L65.2", cam((-0.7, 5.0, 1.5), (0.0, 6.6, 1.3), 26), {"mom": FP(0.45, 6.3, (-0.7, 5.0), "smile", arms=[60, 0])}, note="Mom straightens it")
S("L65b", cam((0.6, 4.9, 1.5), (0.0, 6.6, 1.4), 24), {"jade": FP(-0.1, 6.3, (0.6, 4.9), "laugh")}, note="Jade whips it shut",
  cues=[CU("curtain", v=0.1), CU("curtain", ref="L65b+0.3", v=1.0, dur=0.22)])
S("L65b.1", cam((0.0, 5.6, 1.3), (0.0, 6.9, 1.3), 32), note="no lock pops on; the meter holds")
S("L66", cam((-0.2, 5.7, 1.3), (-0.55, 6.9, 1.2), 34), {"me": P(-0.6, 6.1, 180, "neutral", arms=[95, 0])}, note="we knock on the bare frame")
S("L67", cam((K - 1.6, 2.7, 1.8), (K - 2.0, 4.1, 1.9), 26), note="7:15 again", cues=[CU("clock", h=7.25)])
S("L67.1", cam((-0.5, 2.8, 1.5), (0.3, 4.8, 1.5), 24), {"jade": FP(0.67, 4.8, (-0.5, 2.8), "smile", arms=[0, 100]), "me": P(0.03, 3.2, 180, "neutral", to=[(0.03, 5.6)])},
  note="Jade waves me past")
S("L68", cam((SR, 4.6, 6.0), (SR + 0.5, 1.0, 0.2), 22), note="the curb is empty")
S("L69", cam((0.0, 0.35, 1.5), (0.0, -7.0, 1.2), 20), note="across the hall, a new bathroom door at the end of Mr. Dale's hall",
  cues=[CU("doorat", loc=(0.0, -8.4, 0.0), rot=180.0, scale=1.0), DR(n=65536, L=2.5, lean=4.0, swing=0.0), CU("hole", holes=[])])
S("L69.1", cam((0.0, -3.4, 1.5), (0.0, -5.5, 1.4), 24), {"dale": P(0.0, -5.2, 180, "smile")}, note="Mr. Dale admiring it")
S("L70", cam((0.2, -1.8, 1.5), (0.0, -6.2, 1.2), 22), note="very thick", cues=[DR(L=3.0, dur=0.8)])
S("L71", cam((0.6, -1.6, 1.6), (0.0, -6.5, 1.3), 22), note="still clicking: new locks budding",
  cues=[DR(L=4.6, dur=0.8), MT(262144)])
S("L71.1", cam((0.3, -0.5, 1.4), (0.0, -3.2, 1.3), 20), note="it has filled his hall and nudges his front door",
  cues=[DR(ref="L71.1", L=6.6, dur=1.0), CU("daledoor", a=85.0), CU("daledoor", ref="L71.1+0.3", a=62.0, dur=1.6)])
S("L72", cam((0.0, -0.9, 1.5), (0.0, -2.8, 1.4), 22), {"dale": P(0.1, -2.75, 180, "neutral", head=[0, 18])}, note="Mr. Dale looks down at his swinging door")
S("L72.2", cam((0.0, 4.0, 1.6), (0.0, 1.4, 1.5), 30), {"me": P(0.0, 1.4, 180, "worried")}, note="me, straight down the lens; then the cut to frame 1")

# ---------------------------------------------------------------------------------------------------- timeline stub
from blocky import timeline  # noqa: E402

VOICE = HERE.parent / "voice-timings.json"
BASE = {"slug": "every-lock", "name": "every-lock", "gap": 0.12, "tail": 0, "fade_in": False, "lines": lines, "cast": {}}


def stub_times():
    if not VOICE.exists():
        return None
    st = dict(BASE)
    st["shots"] = [{"id": f"B{i}", "at": s["ref"]} for i, s in enumerate(SH)]
    return timeline.build(st, json.loads(VOICE.read_text()))


def line_ref(tl, t):
    """A line-relative ref for time t: the last line (or pause) starting at or before it."""
    best = None
    for lid in tl["order"]:
        p = tl["lines"][lid]
        if p["onset"] <= t + 1e-6:
            best = p
    if best is None:
        return round(t, 3)
    return f"{best['id']}+{t - best['onset']:.2f}"


tl = stub_times()
final = []
if tl:
    for i, s in enumerate(SH):
        a, b = tl["shots"][i]["start"], tl["shots"][i]["end"]
        d = b - a
        n = max(1, math.ceil(d / 1.85 - 1e-6))
        for j in range(n):
            ref = s["ref"] if j == 0 else line_ref(tl, a + j * d / n)
            c = s["cam"]
            if j % 2 == 1:
                c = [[k[0], k[1], k[2], round(k[3] * 1.1, 1)] + k[4:] for k in c]
            elif j >= 2:
                c = [[k[0], [k[1][0] + 0.12, k[1][1], k[1][2]], k[2], k[3]] + k[4:] for k in c]
            piece = {"ref": ref, "cam": headfit(fit(c, 1.6), s["who"]), "who": s["who"], "cues": s["cues"] if j == 0 else [], "step": s["step"], "note": s["note"],
                     "orig": i, "first": j == 0}
            final.append(piece)
else:
    for i, s in enumerate(SH):
        final.append({**s, "orig": i, "first": True})

shots = [{"id": f"S{i + 1:03d}", "at": p["ref"], "cam": p["cam"], "step": p["step"], "hand": 0.01} for i, p in enumerate(final)]
shots[0].pop("at")


# ---------------------------------------------------------------------------------------------------- acting
def off(ref, d):
    import re
    if isinstance(ref, (int, float)):
        return round(ref + d, 3)
    m = re.match(r"^(.*?)([+-]\d+(?:\.\d+)?)$", ref)
    if m and not re.match(r"^L\d+b?$", ref):
        return f"{m.group(1)}{float(m.group(2)) + d:+.3f}"
    return f"{ref}{d:+.3f}"


refs = [p["ref"] for p in final] + ["end"]
paths = []   # per shot start ref
acting = {name: [] for name in cast}
last_pos = {name: (0.0, 0.0, -50.0) for name in cast}
BL = 0.001


def next_pos(name, k):
    for q in range(k, len(final)):
        w = final[q]["who"].get(name)
        if w:
            return w["pos"]
    return last_pos[name]


def endat(name, k, nxt, pos):
    """When a character's stay in shot k ends: BL before the next shot, or exactly at it where the next shot puts them
    somewhere else (a cut, not a walk: a zero-length move, so the sound mix gets no phantom burst of footsteps)."""
    if nxt == "end":
        return nxt
    nw = final[k + 1]["who"].get(name) if k + 1 < len(final) else None
    npos = nw["pos"] if nw else next_pos(name, k + 1)
    if math.hypot(npos[0] - pos[0], npos[1] - pos[1]) >= 1.5:
        return nxt
    return off(nxt, -BL)


for k, p in enumerate(final):
    ref, nxt = refs[k], refs[k + 1]
    t_start = tl["shots"][k]["start"] if False else None
    for name in cast:
        w = p["who"].get(name)
        if not w:
            np_ = next_pos(name, k)
            acting[name].append({"at": ref if k else 0, "pos": list(np_), "yaw": 0, "hidden": True, "blend": BL, "arms": [0, 0],
                                 "head": [0, 0], "lean": 0, "expr": "neutral"})
            continue
        key = {"at": ref if k else 0, "pos": list(w["pos"]), "yaw": w.get("yaw", 0), "expr": w.get("expr", "neutral"),
               "hidden": False, "blend": BL, "arms": w.get("arms", [0, 0]), "head": w.get("head", [0, 0]), "lean": w.get("lean", 0)}
        if w.get("run"):
            key["run"] = True
        if w.get("keep_yaw"):
            key["keep_yaw"] = True
        acting[name].append(key)
        last_pos[name] = w["pos"]
        if w.get("to"):
            pts = [tuple(w["pos"])] + [tuple(q) if len(q) == 3 else (q[0], q[1], 0.0) for q in w["to"]]
            lens = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
            tot = sum(lens) or 1.0
            if tl:
                a_t, b_t = tl["shots"][k]["start"], tl["shots"][k]["end"]
                dur = max(0.2, b_t - a_t - 0.05)
            else:
                dur = 1.0
            acc = 0.0
            for q, (pt, ln) in enumerate(zip(pts[1:], lens)):
                acc += ln
                if q == len(lens) - 1:
                    key2 = {"at": endat(name, k, nxt, pt), "pos": list(pt), "blend": BL}
                else:
                    key2 = {"at": off(ref, (acc / tot) * dur) if False else f"{line_ref(tl, a_t + acc / tot * dur)}" if tl else ref,
                            "pos": list(pt), "blend": BL}
                if w.get("run"):
                    key2["run"] = True
                acting[name].append(key2)
            last_pos[name] = pts[-1]
        else:
            if nxt != "end":
                acting[name].append({"at": endat(name, k, nxt, w["pos"]), "pos": list(w["pos"]), "blend": BL})
        if w.get("mouth"):
            acting[name].append({"from": ref if k else 0, "to": nxt if nxt != "end" else "end", "mouth": [0.7, 0.7], "flap": True})

# ---------------------------------------------------------------------------------------------------- cues
cues = []
for k, p in enumerate(final):
    if not p["first"]:
        continue
    ref = p["ref"] if k else 0
    for (r, name, fields) in p["cues"]:
        cues.append({"at": r if r is not None else ref, "name": name, **fields})

# the sound budget (2 to 4 events per 10 s, owner 2026-11-03): only the impacts, the doors and a few sparse clicks;
# the meter pops silently and the polish pack's door marks are off (the door cue is a lock count, not a door).
sfx = [
    {"at": "L01>-0.2", "kind": "thud", "db": -4, "dur": 0.5},
    {"at": "L15.2+0.12", "kind": "door", "db": -10}, {"at": "L22>-0.36", "kind": "door", "db": -10}, {"at": "L30+0.05", "kind": "door", "db": -9},
    {"at": "L36.2", "kind": "click", "db": -14}, {"at": "L39.1", "kind": "click", "db": -13}, {"at": "L40.2", "kind": "click", "db": -14},
    {"at": "L41", "kind": "click", "db": -15}, {"at": "L41.1", "kind": "click", "db": -14}, {"at": "L41.2", "kind": "click", "db": -13},
    {"at": "L46", "kind": "creak", "db": -18, "dur": 1.4},
    {"at": "L57+0.5", "kind": "ding", "db": -26, "pitch": 3200, "lp": 4500},
    {"at": "L58+0.65", "kind": "latch", "db": -16},
    {"at": "L60+0.2", "kind": "thud", "db": -14, "dur": 0.6},
    {"at": "L66.1-0.2", "kind": "knock", "pattern": [0, 0.22], "tone": "hand", "db": -12},
    {"at": "P02+0.3", "kind": "thud", "db": -14, "dur": 0.9},
]
# the night's clicks thin in, then thicken, never a buzz
for lid, n, step, db in (("L45", 2, 0.5, -19), ("L47", 3, 0.5, -18), ("L52", 2, 0.6, -21)):
    for i in range(n):
        sfx.append({"at": f"{lid}+{0.2 + i * step:.2f}", "kind": "click", "db": db - (i % 3)})

music = {"root": 48, "mode": "mixolydian", "bpm": 116, "seed": 21, "sections": [
    {"at": 0, "voices": ["pulse", "pluck_hi", "tick"], "energy": 0.45},
    {"at": "L19", "voices": ["pulse", "pluck_hi", "tick"], "energy": 0.7},
    {"at": "L25", "voices": ["pulse", "pluck_hi", "tick"], "energy": 0.9},
    {"at": "L36", "voices": [], "energy": 0.3},
    {"at": "L41", "voices": ["drone"], "energy": 0.5},
    {"at": "L56.2", "voices": ["drone", "pulse"], "energy": 0.6},
    {"at": "L63", "voices": ["drone", "pulse", "pluck"], "energy": 0.55, "mode": "major"},
    {"at": "P02", "voices": ["drone", "tick"], "energy": 0.35, "mode": "mixolydian"},
]}
sound = {
    "rev": 1, "floor": "wood", "steps_db": -22,
    "ambience": [{"kind": "room", "from": 0, "to": "end", "lufs": -35}, {"kind": "traffic", "from": 0, "to": "end", "lufs": -44},
                 {"kind": "hum", "from": "L36", "to": "L55", "lufs": -40}],
    "sfx": sfx,
    "music_drops": [{"from": "L35>", "to": "L36", "keep": ["click"]}, {"from": "L67>", "to": "L68", "keep": ["thud"]}],
}

for e in sfx:
    e["at"] = R(e["at"])
for sec in music["sections"]:
    sec["at"] = R(sec["at"])
for d in sound["music_drops"]:
    d["from"], d["to"] = R(d["from"]), R(d["to"])

import re as _re2
SWAY = [sh["id"] for sh in shots if isinstance(sh.get("at"), str) and (_m := _re2.match(r"L(\d+)", sh["at"])) and 41 <= int(_m.group(1)) <= 50]
story = {
    "slug": "every-lock", "title": "My Bathroom Door Has 1,024 LOCKS", "made_for_kids": False,
    "premise": ("In our apartment building, closing a door doubles its locks and the locks never come off, so everybody lives with "
                "their doors open. I have never closed one. My big sister Jade slams them, and we fight for the one bathroom at "
                "7:15 every morning, until our bathroom door is a brass bulge of 1,024 locks leaning into the hall."),
    "twist": ("A lock's keyhole flap is a little door too, so one flap swinging shut gives its lock a lock and the door doubles itself "
              "with nobody touching it. The locks never come off, but the door does: we carry it down to the curb, and Mr. Dale "
              "across the hall takes it home, where it starts pushing on his own front door."),
    "world": ("a bright four-floor city apartment building: mint hall with a terracotta floor and open front doors, a sky-blue "
              "apartment with a short inner hall and one yellow bathroom door, a downstairs kitchen, a stairwell and a sunny curb"),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45}, "key_color": "#ffb21f", "gap": 0.12, "tail": 0, "fade_in": False,
    "look": {"style": "closer", "flash_safe": True,
             "polish": {"emph": ["L01", "L12b", "L30", "L40", "L42", "L44", "L47", "L60"], "reveal": ["L30", "L40", "L44"],
                        "quiet": [["L52", "L54"]], "sway": SWAY, "marks": False}, "fog": "#dbe9f2", "fog_density": 0.004, "fog_start": 8.0, "sky": "#79c3ff",
             "exposure": 0.0, "hdri": "lebombo", "hdri_strength": 0.9, "hdri_rotation": 0},
    "grade": {"shadows": [0.0, 0.0, 0.01], "highlights": [0.01, 0.005, -0.01], "saturation": 1.12, "contrast": 1.04,
              "vignette": 0.18, "bloom": 0.12, "grain": 0.008},
    "cast": cast, "lines": lines, "shots": shots, "acting": acting, "cues": cues, "fx": [], "music": music, "sound": sound,
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False))
print("wrote", OUT, len(shots), "shots", "(split)" if tl else "(no timings yet)")
