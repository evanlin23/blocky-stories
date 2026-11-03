"""Writes ../story.json for ep51 "Fossil hall" (script by the writer, 2026-11-02).

Run from anywhere: python stories/ep51-fossil-hall/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the acting,
the cues set.py reads (glow strengths, the hall's lamps, the skeleton's head, the Stooped's poses, the torch, sparks), the
score and the sound.

Places are set.py's metres (see its docstring). A character with yaw 0 faces -y, yaw 90 faces +x, yaw 180 faces +y, and the
people on the bench sit facing the skeleton, so their yaw is 180. Abe's end of the bench is x +1.0, mine x -1.0.
"""
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# a quiet beat after the last word before the loop cut (the script: 0.25 s after "PLACE")
lines.append({"id": "P03", "pause": 0.25, "chunks": []})
# spoken forms Whisper needs (captions never change)
SPOKEN = {}
for ln in lines:
    for k, ch in enumerate(ln.get("chunks", [])):
        if (ln["id"], k) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], k)]

SWAP = [("grandad", "granddad"), ("neighbours", "neighbors"), ("tail bone", "tailbone")]
changed = []
for ln in lines:
    for ch in ln.get("chunks", []):
        new = ch[1]
        for a, b in SWAP:
            new = new.replace(a, b)
        if new != ch[1]:
            ch[1] = new
            changed.append(ln["id"])
print("spoken forms changed:", ",".join(sorted(set(changed))))

# ------------------------------------------------------------------------------------------------ cast
FACE = {"eyes": "round", "brows": True, "ink": "#1a1416"}


def person(skin, shirt, pants, hair_c, hair="cap", pattern="solid", pattern_c=None, shoes="#2a2a2e", extras=(), height=1.0,
           eyes="round", collar=None, bags=False, extra_c=None):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes, "sleeves": "long",
         "hair": hair, "hair_c": hair_c, "hat": "none", "height": height,
         "face": {"eyes": eyes, "brows": True, "ink": "#1a1416", **({"bags": True} if bags else {})}}
    if pattern_c:
        d["pattern_c"] = pattern_c
    if collar:
        d["collar"] = collar
    if extras:
        d["extras"] = list(extras)
    if extra_c:
        d["extra_c"] = extra_c
    if "coat" in extras:
        d["zip_c"] = "#3a3a3e"
    return d


cast = {
    # me: short ginger block hair, a mustard corduroy jacket (the ribbed knit) over a striped top (set.py adds the chest panel)
    "me": person("#e9bd98", "#d09a2c", "#232834", "#c4642a", "cap", "knit", "#b07f1e", "#f1f1ee"),
    # Grandad Abe: white block hair, a white moustache and round black-rimmed glasses, a bottle-green waistcoat over cream
    "abe": person("#e6bf9f", "#efe6d0", "#7a7c80", "#f2f0ea", "cap", shoes="#3a3028", extras=("glasses",), extra_c="#15161a",
                  height=0.95, eyes="tired", bags=True),
    "curator": person("#d9a98a", "#6e2f55", "#3b3b44", "#8d9096", "long", collar="#f2f0ea", height=0.97, eyes="lashes"),
    "visitor": person("#c98f66", "#e8c32a", "#2f3a52", "#3a2418", "bun", extras=("coat", "hooddown"), eyes="lashes"),
    "planner": person("#f0c8a0", "#3f6fb5", "#2a2a32", "#2a1d15", "spiky", "knit", "#2f5a9a"),
    "birthday": person("#b9835c", "#4a8a4c", "#3a3a40", "#222222", "buzz", "plaid", "#2f6a34", extras=("glasses",), extra_c="#1b1b1e"),
    "whisperer": person("#d6a781", "#b79a6b", "#3d3a36", "#4a3220", "swoop", extras=("coat",)),
    "friend": person("#e2b48f", "#c7708a", "#2e2e3a", "#5a3a22", "long", "knit", "#a85874", eyes="lashes"),
    "groom": person("#d9a47c", "#1f2c4e", "#1f2c4e", "#2a1d15", "cap", extras=("tie",), extra_c="#a02c3a", collar="#f0f0f0"),
    "bride": person("#ecc4a0", "#b9a2d6", "#b9a2d6", "#7a4a2a", "bun", eyes="lashes", shoes="#8a6a9a"),
    "waiter": person("#c58f68", "#17171c", "#17171c", "#4a3020", "cap", collar="#f4f4f0"),
    "dull": person("#e2b894", "#cdbf9f", "#8a8070", "#6a6a6a", "buzz", "knit", "#b3a582"),
}
SKINS = ["#f0c8a0", "#d9a47c", "#c58f68", "#a8714e", "#8c5c40", "#e6bf9f", "#d6a781", "#b9835c"]
SHIRTS = ["#7d8f5a", "#a8553f", "#4f6f8f", "#8a6fa8", "#c98a3a", "#3f7f78", "#9a4a5a", "#6a7a96", "#b0a070", "#566a4a",
          "#a06a8c", "#d0c0a0", "#5a5a7a", "#8f5f3f"]
PANTS = ["#2c3550", "#4a463e", "#3a3a40", "#5a4a3a", "#2a3a4a", "#49453f"]
HAIRS = ["#2a1d15", "#4a3220", "#7a5a38", "#8a8a90", "#1c1612", "#a07a48", "#5a3a22", "#c9c2b0"]
HAIRSTYLES = ["cap", "swoop", "long", "bun", "spiky", "buzz", "cap", "swoop", "long", "cap", "bun", "buzz", "cap", "swoop"]
CROWD = [f"c{i}" for i in range(1, 15)]
rng = random.Random(51)
for i, nm in enumerate(CROWD):
    patt = ["solid", "knit", "plaid", "stripes", "solid", "knit"][i % 6]
    cast[nm] = person(SKINS[i % len(SKINS)], SHIRTS[i % len(SHIRTS)], PANTS[(i * 5) % len(PANTS)], HAIRS[(i * 3) % len(HAIRS)],
                      HAIRSTYLES[i], patt, SHIRTS[(i + 5) % len(SHIRTS)], eyes=["round", "lashes", "tired", "round"][i % 4],
                      height=[1.0, 0.96, 1.03, 0.98][i % 4])
GLOW = {n: 1.0 for n in CROWD}
GLOW.update({"abe": 3.0, "planner": 4.0, "groom": 4.0, "bride": 4.0, "whisperer": 3.0, "friend": 1.0, "visitor": 1.5,
             "curator": 1.0, "birthday": 1.0, "waiter": 1.0, "me": 0.0, "dull": 0.0})

# ------------------------------------------------------------------------------------------------ helpers
SMILE, MOVED, TIRED, SLEEPY, SHEEPISH = "smirk", "soft", "neutral", "asleep", "worried"
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True, "sit": False}
SITZ = -0.06
acting = {n: [{"at": 0, "hidden": True, "blend": 0}] for n in cast}
cues = []
shots = []
visible = set()
env_state = {}


def P(x, y, yaw=0, **kw):
    return {"pos": (x, y), "yaw": yaw, **kw}


def SIT(x, y, yaw=180, z=SITZ, **kw):
    return {"pos": (x, y, z), "yaw": yaw, "sit": True, **kw}


def put(who, at, spec):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    spec = dict(spec)
    pos = spec.pop("pos")
    keys.append({"at": at, "pos": list(pos), "blend": 0, "hidden": False, **NEUTRAL, "expr": "neutral", **spec})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": list(pos), **kw})


def talk(who, a, b):
    acting[who].append({"from": a, "to": b, "mouth": [0.5, 0.5], "flap": True})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def glow(at, who, s, dur=0.0):
    c = {"at": at, "name": "glow", "who": who, "s": s}
    if dur:
        c["dur"] = dur
    cues.append(c)


def C(loc, tgt, lens, roll=0):
    k = [0, list(loc), list(tgt), lens]
    if roll:
        k.append(roll)
    return [k]


def MV(a, b, lens_a, lens_b=None):
    return [[0, list(a[0]), list(a[1]), lens_a], [1, list(b[0]), list(b[1]), lens_b or lens_a]]


# what each area needs from the sun and the sky; the glow reads brighter in daylight so it gets a boost there
ENV = {"hall": ("off", "#1a1c24", 0.2), "gal": ("off", "#1a1c24", 0.2), "bas": ("off", "#1a1c24", 0.2),
       "lv": ("off", "#1a1c24", 0.2), "rs": ("off", "#1a1c24", 0.2), "bd": ("off", "#1a1c24", 0.2),
       "st": ("steps", "#8fc1e8", 0.9), "pk": ("day", "#8fc1e8", 0.9), "ds": ("dusk", "#d8946e", 0.7),
       "sr": ("dusk", "#d8946e", 0.7)}
HALLLV = {"v": None}


def shot(at, area, cam, who=None, note="", hall=None, step=2, hand=0.006, **extra):
    """A new shot at `at`: its camera, who is on screen (everyone else is hidden at the cut) and where."""
    who = who or {}
    sid = f"S{len(shots) + 1:03d}"
    s = {"id": sid, "cam": cam, "hand": hand, "step": step, "what": note}
    if shots:
        s["at"] = at
    shots.append(s)
    sun, sky, sks = ENV[area]
    if env_state.get("area") != area:
        cue(at, "sun", set=sun)
        cue(at, "sky", color=sky, strength=sks)
        env_state["area"] = area
    if hall is not None and HALLLV["v"] != hall:
        cue(at, "hall", level=hall)
        HALLLV["v"] = hall
    for n in cast:
        if n in who:
            put(n, at, who[n])
            visible.add(n)
        elif n in visible:
            hide(n, at)
            visible.discard(n)
    return s


STOOPED = {"yaw": 180, "pos": [-0.69, -4.0]}


def stooped(at, **kw):
    cue(at, "stooped", **{**STOOPED, "neck": 0, "roll": 180, "pitch": 0, "hyaw": 0, **kw})


def stooped_off(at):
    cue(at, "stooped", hidden=True)


# ------------------------------------------------------------------------------------------------ the shots
HX = {"abe": 0.69, "me": -0.69}          # the two ends of the bench
BY = -3.4
EYE = 1.55
cue(0, "stripes", on=False)
cue(0, "skull", yaw=0.0)
cue(0, "stooped", hidden=True)
cue(0, "torch", on=0.0)
cue(0, "tailgold", on=0.0)
cue(0, "gal", level=1.0)
cue(0, "sheet", on=False)
cue(0, "glk", level=1.0)

# ---- 01 the rule (L01 to L09)
stepz = lambda y: 0.17 * min(5, max(0, int((y - 2.9) // 0.55) + 1)) if y > 2.9 else 0.0
SXC = 340.0


def sp(x, y, yaw=0, **kw):
    return P(x, y, yaw, **kw) if y <= 2.9 else {"pos": (x, y, stepz(y)), "yaw": yaw, **kw}


shot(0, "st", C([SXC - 0.25, -0.1, 1.62], [SXC - 0.1, 1.9, 1.55], 30), {
    "visitor": P(SXC - 0.1, 1.9, 0, expr=SMILE, head=[0, 4]),
    "c1": sp(SXC + 1.5, 3.2, 0), "c2": sp(SXC - 1.7, 3.2, 0)},
     "the yellow raincoat on the sunny steps, smug, a gold rim", step=1)
glow(0, "visitor", 3.0)   # a clear rim on the first frame, then settled
glow("L01.1", "visitor", 1.5, 1.0)
shot("L01.2", "st", C([SXC, -3.2, 2.5], [SXC, 3.6, 1.1], 26), {
    "planner": sp(SXC, 3.6, 0, arms=[80, 80], side=[10, 10], expr=SMILE),
    "c1": sp(SXC - 2.4, 3.2, 0, arms=[100, 0]), "c2": sp(SXC + 2.4, 3.3, 0, arms=[100, 100]),
    "c3": sp(SXC - 1.2, 4.2, 0, arms=[100, 0]), "c4": sp(SXC + 1.2, 4.3, 0, arms=[90, 90]),
    "c5": sp(SXC - 3.3, 4.2, 0), "c6": sp(SXC + 3.4, 3.2, 0), "c7": sp(SXC - 0.5, 2.6, 0, expr="shut"),
    "c8": sp(SXC + 2.1, 5.2, 0), "c9": sp(SXC - 2.2, 5.3, 0), "c10": sp(SXC + 0.3, 5.1, 0),
    "visitor": P(SXC - 0.9, 1.7, 180, expr=SMILE)},
     "wider: a dozen rims and one man lit like a lamp", step=2)
LV = 180.0
shot("L02", "lv", C([LV, -2.9, 1.85], [LV, 1.4, 1.0], 27), {
    "c3": P(LV - 1.0, 2.0, 0, z=-0.6, expr=SMILE), "c4": P(LV + 0.1, 2.05, 0, z=-0.6, expr="soft"),
    "c5": P(LV + 1.1, 2.0, 0, z=-0.6, expr=SMILE)}, "guests crouched behind the sofa, each faintly glowing")
DX = 220.0
shot("L03", "ds", C([DX - 1.6, -2.2, 1.5], [DX + 0.1, 1.4, 1.4], 28), {
    "planner": {"pos": (DX, 2.45, 0.18), "yaw": 0, "expr": SMILE, "arms": [40, 40]},
    "birthday": P(DX + 0.3, -0.5, 180, expr=SHEEPISH, head=[0, -6])},
     "dusk doorstep: the planner lamp-bright, the birthday man squinting")
PX = 260.0
shot("L04", "pk", C([PX, -4.6, 1.5], [PX, 0, 1.0], 30), {
    "whisperer": SIT(PX - 0.55, 0.0, 0, head=[-35, 0], expr="neutral"),
    "friend": SIT(PX + 0.55, 0.0, 0, head=[0, 0], expr="neutral")}, "the whisperer leans to his friend's ear")
glow("L04", "whisperer", 3.0)
glow("L04", "friend", 1.0)
shot("L04.2", "pk", C([PX, -3.2, 1.4], [PX + 0.05, 0, 1.1], 34), {
    "whisperer": SIT(PX - 0.55, 0.0, 0, head=[-35, 0], expr="neutral"),
    "friend": SIT(PX + 0.55, 0.0, 0, expr="neutral")}, "a spark crosses the gap and her rim swells")
glow("L04.2", "whisperer", 1.0, 1.0)
glow("L04.2", "friend", 3.5, 1.0)
key("friend", "L04.2", expr="wide", blend=0.1)
cue("L04.2", "spark1", a=[PX - 0.55, 0.0, 1.3], b=[PX + 0.55, 0.0, 1.3])
RX = 300.0
shot("L05", "rs", C([RX, -3.2, 1.9], [RX, 0, 1.0], 22), {
    "groom": SIT(RX - 1.15, 0, 90, expr="smirk"), "bride": SIT(RX + 1.15, 0, -90, expr=SMILE)},
     "the engaged couple glowing like two lamps, trying to look casual")
shot("L05.2", "rs", C([RX + 0.4, -3.1, 1.8], [RX, 0.4, 1.0], 26), {
    "groom": SIT(RX - 1.15, 0, 90, expr="neutral"), "bride": SIT(RX + 1.15, 0, -90, expr="neutral"),
    "waiter": P(RX, 1.15, 0, lean=18, expr="neutral", head=[0, 8])}, "the waiter leans in to blow out the candles")
shot("L06", "st", C([SXC, -0.4, 1.62], [SXC, 1.9, 1.55], 28), {
    "dull": P(SXC, 1.9, 0, expr=SMILE, arms=[85, 85], side=[-20, -20], head=[0, -8]),
    "c1": sp(SXC - 1.4, 3.3, 0), "c2": sp(SXC + 1.5, 3.2, 0), "c4": sp(SXC + 0.4, 4.4, 0)},
     "the dullest man, no rim, arms folded, chin up")
shot("L07", "st", C([SXC + 0.3, -0.1, 1.6], [SXC, 1.9, 1.55], 28), {
    "me": P(SXC, 1.9, 0, expr="neutral"),
    "c1": sp(SXC - 1.3, 3.3, 0), "c2": sp(SXC + 1.2, 3.3, 0), "c3": sp(SXC - 0.3, 4.4, 0), "c4": sp(SXC + 0.9, 4.5, 0),
    "c5": sp(SXC - 1.9, 4.5, 0)}, "me: close, no rim, a glowing crowd behind")
shot("L08", "st", C([SXC, -1.8, 1.55], [SXC, 1.9, 1.45], 24), {
    "me": P(SXC - 0.55, 1.9, 90, expr=SMILE), "c6": P(SXC + 0.6, 1.9, -90, expr="wide", head=[0, 3]),
    "c1": sp(SXC - 1.8, 3.3, 0), "c2": sp(SXC + 1.8, 3.4, 0)}, "me chatting to a stranger who looks overwhelmed")
talk("me", "L08", "L08>")
shot("L09", "hall", C([0.4, -7.8, 1.6], [0.2, -3.4, 1.1], 26), {
    "abe": SIT(HX["abe"], BY, 180, expr=SMILE), "me": SIT(HX["me"], BY, 180, expr=SMILE, head=[-55, 0])},
     "the fossil hall by day, from behind the bench: Abe's back and glow, me beside him talking", hall=0.6, step=2)
talk("me", "L09", "L09>")
# ---- 02 Grandad (L10 to L20)
TOUR = [("c1", -8.9, -7.2, 100), ("c2", -9.6, -8.1, 80), ("c3", -7.6, -8.4, 150), ("c4", -9.2, -6.9, 110),
        ("c5", -6.9, -7.4, -140)]
glow("L10", "abe", 3.0)
# us on the bench; visitors passing in front of it squint at Grandad's glow and step away (what he could lose)
shot("L10", "hall", C([0.3, 0.7, 1.3], [0.3, -3.2, 1.05], 20), {
    "abe": SIT(HX["abe"], BY, 180, expr=SMILE), "me": SIT(HX["me"], BY, 180, expr=SMILE),
    "c1": P(1.0, -1.9, 160, expr="neutral"), "c2": P(1.8, -1.8, 160, expr="neutral")},
     "us on the bench; two passing visitors turn to Grandad's glow, squint and step away")
key("c1", "L10.2", arms=[115, 105], expr="worried", blend=0.3)
key("c2", "L10.2+0.2", arms=[110, 100], expr="worried", blend=0.3)
walk("c1", "L10>", (1.6, -1.8))
walk("c2", "L10>", (2.4, -1.7))
shot("L11", "hall", C([-0.6, 0.5, 0.55], [0.5, -3.0, 1.2], 22), {
    "abe": SIT(HX["abe"], BY, 180, expr=SMILE), "me": SIT(HX["me"], BY, 180, expr=SMILE),
    "c3": P(1.0, -1.9, 160, arms=[115, 105], expr="worried"), "c4": P(1.8, -1.8, 160, arms=[110, 110], expr="worried"),
    "c5": P(2.5, -1.7, 160, arms=[100, 0], expr="worried")},
     "low wide: his glow soft on the bench; passers-by shield their eyes and edge away from it")
walk("c3", "L11.2", (1.5, -1.9))
walk("c4", "L11.2", (2.3, -1.8))
walk("c5", "L11.2+0.2", (3.1, -1.7))
shot("L12", "hall", C([0.0, -8.4, 1.45], [0.0, 1.5, 2.4], 19), {
    "abe": SIT(HX["abe"], BY, 180, expr=SMILE), "me": SIT(HX["me"], BY, 180, expr=SMILE)}, "wide from behind the bench: the skeleton over us")
shot("L12.3", "hall", C([-1.0, -4.6, 0.6], [-3.6, 1.5, 4.7], 22), {}, "tilt up the long neck to the head high over the hall")
TWO = C([0.0, 0.2, 1.3], [0.0, BY, 1.0], 24)
shot("L13", "hall", TWO, {
    "abe": SIT(HX["abe"], BY, 180, expr=SMILE), "me": SIT(HX["me"], BY, 180, expr=SMILE)}, "mid two-shot on the short bench: Grandad left, me right, shoulders touching")
shot("L14", "hall", MV(([4.3, 0.2, 1.95], [6.0, 1.5, 1.7]), ([4.7, 0.2, 1.95], [6.3, 1.5, 1.68]), 38),
     {}, "along the tail to the paler, mended block")
shot("L14.1", "hall", C([5.6, -5.0, 1.55], [6.1, 1.5, 1.7], 26), {
    "c7": P(6.5, -0.7, 180, arms=[110, 0], expr="neutral"), "abe": P(4.3, -1.5, 180, expr=SMILE, head=[40, 0])},
     "a visitor points at the tail; behind, Abe's glow swells")
glow("L14.1", "abe", 3.7, 1.0)
shot("L15", "hall", C([7.8, -4.6, 1.5], [5.1, -0.3, 1.5], 26), {
    "curator": P(5.5, -0.6, 180, arms=[150, 0], expr="neutral", head=[0, -22]),
    "abe": P(4.5, -0.55, 180, expr=SHEEPISH, head=[50, 0])}, "the curator points up at the pale block; Abe looks away")
glow("L15", "abe", 3.7)
shot("L16", "hall", C([7.8, -4.6, 1.5], [5.1, -0.3, 1.5], 26), {
    "curator": P(5.5, -0.6, 180, arms=[150, 0], expr="neutral", head=[0, -22]),
    "abe": P(4.5, -0.55, 180, expr=SHEEPISH, head=[50, 0])}, "a week later: his glow stronger, her face lit warm by it")
glow("L16", "abe", 4.6, 1.0)
SRX = 380.0
shot("L17", "sr", MV(([SRX + 6.5, -3.4, 1.5], [SRX - 1.0, 3.8, 1.3]), ([SRX + 6.2, -3.4, 1.5], [SRX - 1.4, 3.8, 1.3]), 24), {
    "abe": P(SRX - 3.5, 4.2, 90, expr=SMILE), "c1": P(SRX + 1.4, 3.6, 0), "c2": P(SRX + 2.3, 3.7, 0)},
     "dusk street: Abe glowing on one pavement, two neighbours crossing")
walk("abe", "L17>", (SRX - 1.0, 4.2))
walk("c1", "L17>", (SRX + 1.4, -3.4))
walk("c2", "L17>", (SRX + 2.3, -3.5))
shot("L18", "hall", C([-8.4, -5.0, 1.55], [-11.2, 0.0, 1.4], 24), {
    "curator": P(-10.4, -0.9, -90, arms=[90, 0], expr=SHEEPISH), "abe": P(-11.6, 0.6, -90, expr=TIRED)},
     "the curator points him through the arch into the dark side rooms", hall=0.6)
glow("L18", "abe", 4.8)
shot("L18.3", "gal", C([-16.2, -0.6, 1.5], [-20.2, 0.0, 1.25], 28), {"abe": P(-19.4, 0.0, 90, expr=TIRED)},
     "the dark gallery: Abe alone, the only light")
glow("L18.3", "abe", 1.0)
glow("L18.3+0.05", "abe", 5.0, 0.5)
cue("L18.3", "gal", level=0.25)
cue("L18.3+0.05", "gal", level=1.0, dur=0.5)
BX = 420.0
shot("L19", "bd", C([BX - 1.8, -1.9, 1.9], [BX, 0.0, 0.7], 30), {
    "abe": {"pos": (BX, 0.95, 0.7), "yaw": 180, "lean": -90, "expr": SLEEPY}}, "his small bedroom, a checked towel over his face")
shot("L20", "hall", C([-2.0, -6.8, 1.35], [0.1, -3.4, 0.95], 26), {"abe": SIT(HX["abe"], BY, 180, expr=TIRED)},
     "the bench: Abe alone at his end, mine empty", hall=0.6)
shot("L20.2", "lv", C([LV + 0.6, -2.6, 1.3], [LV, 0.85, 0.95], 28), {
    "me": SIT(LV, 0.85, 0, expr=SHEEPISH, head=[-45, 0])}, "me on the sofa, worried, looking away from the window")
# ---- 03 traces (L21 to L28)
cue("L21", "stripes", on=True)
shot("L21", "hall", C([-9.2, 0.7, 1.58], [-30.0, 0.0, 1.5], 27), {
    "me": P(-11.0, 0.4, -90, expr="neutral"), "abe": P(-27.0, 0.0, 90, expr=TIRED)},
     "me in the hall doorway; Abe far off in the dark gallery, a soft gold patch", hall=0.6)
glow("L21", "abe", 5.0)
shot("L22", "gal", C([-19.7, 1.2, 0.95], [-19.7, 2.4, 0.98], 45), {}, "close on a dusty case glass")
cue("L22", "stripes", on=False)
shot("L23", "gal", MV(([-15.4, 1.5, 0.52], [-30.0, 2.0, 0.55]), ([-15.8, 1.6, 0.52], [-30.0, 2.0, 0.55]), 24), {},
     "low along the row of cases: a clean stripe at knee height")
cue("L23", "stripes", on=True)
shot("L23.1", "gal", C([-15.3, 1.0, 0.55], [-33.0, -2.2, 0.5], 26), {}, "down the gallery, the stripe running into the dark")
shot("L24", "gal", C([-18.0, -0.7, 1.0], [-20.3, 1.7, 0.8], 30), {
    "me": P(-20.3, 1.55, 180, z=-0.28, lean=18, expr=SHEEPISH, head=[0, 8])}, "me crouching at the height of the stripe")
shot("L25", "hall", C([0.2, -3.9, 0.7], [-4.2, 1.5, 5.0], 21), {}, "up from the bench to the skeleton's head, turned a little", hall=0.6)
cue("L25", "skull", yaw=16.0)
shot("L26", "hall", C([0.2, -3.9, 0.7], [-4.2, 1.5, 5.0], 21), {}, "the same frame, the head turned more", hall=0.6)
cue("L26", "skull", yaw=34.0)
shot("L27", "gal", C([-17.6, 1.3, 1.55], [-27.0, -0.7, 1.3], 28), {"abe": P(-16.0, 0.9, -90, expr=TIRED)},
     "over Abe's shoulder, down the gallery: something level and dark bends over a case at the far end")
glow("L27", "abe", 5.0)
cue("L27", "stooped", pos=[-26.0, -0.7], yaw=0, neck=0, roll=180, pitch=0, hyaw=0)
cue("L27", "dof", on=True, focus=[-16.0, 0.9, 1.4], f=2.8)
shot("L27.2", "hall", C([-8.2, 1.1, 1.58], [-13.0, 0.0, 1.45], 30), {"me": P(-12.7, 0.2, 90, expr="scared")},
     "me in the doorway, scared")
cue("L27.2", "dof", on=False)
stooped_off("L27.2")
shot("L28", "gal", C([-15.6, 0.9, 1.62], [-33.0, -1.5, 1.25], 28), {"abe": P(-17.4, 0.2, -90, expr=TIRED)},
     "when he turns, only a case")
key("abe", "L28", yaw=-130, blend=0.9)
glow("L28", "abe", 5.0)
# ---- 04 taken (L29 to L41)
shot("L29", "hall", C([0.0, -8.0, 1.65], [0.0, 1.5, 2.5], 20), {}, "the hall from the bench: the lamps ramp down", hall=0.6)
cue("L29", "hall", level=0.07, dur=1.5)
HALLLV["v"] = 0.07
shot("P01", "hall", C([1.9, -5.6, 0.95], [-0.6, 0.6, 1.3], 22), {}, "hold on the dim hall", hall=0.07)
shot("L30", "gal", C([-10.5, -0.5, 1.5], [-18.0, 0.0, 1.5], 24), {}, "the gallery doorway where he stood: no gold anywhere")
cue("L30", "gal", level=1.0)
cue("L31", "torch", on=1.0, dur=0.5)
shot("L31", "hall", C([0.75, -1.3, 0.34], [-0.3, -0.2, 0.05], 28), {}, "low on the marble: his torch, beam on, by the skeleton's feet", hall=0.07)
shot("L32", "hall", C([-0.3, -1.2, 3.4], [-0.3, -0.2, 0.0], 26), {}, "overhead: the torch beam sweeping round on the tiles", hall=0.07)
shot("L32.2", "hall", C([-2.2, 0.4, 1.4], [-1.4, -1.6, 1.3], 30), {"me": P(-1.4, -1.6, 180, expr="scared")},
     "me at the hall's edge, the beam passing my feet", hall=0.07)
cue("L33", "torch", on=0.0, dur=0.5)
shot("L33", "gal", C([-11.0, 0.3, 1.55], [-14.6, 0.0, 1.5], 28), {"me": P(-14.6, 0.0, 90, expr="scared")},
     "me calling down the gallery")
talk("me", "L33.1", "L33>")
shot("L33.2", "gal", C([-31.0, 0.3, 1.45], [-16.0, 0.0, 1.35], 24), {}, "another dark gallery, empty, the cases blue")
shot("L34", "gal", C([-23.6, 1.0, 0.62], [-23.6, 2.1, 0.56], 42), {}, "a fresh clean line on the case")
shot("L35", "gal", C([-18.5, 0.1, 1.55], [-22.2, 0.0, 1.5], 30), {"me": P(-22.2, 0.0, 90, expr="scared", look=[1, 0])},
     "from the front, eyes sliding sideways; behind me dark and out of focus")
cue("L35", "dof", on=True, focus=[-22.2, 0.0, 1.5], f=1.2)
shot("L36", "gal", C([-20.2, 0.0, 1.55], [-22.2, 0.0, 1.5], 40), {"me": P(-22.2, 0.0, 90, expr="scared", tremble=0)},
     "close on my face, holding still")
cue("L36", "dof", on=False)
BAS = 100.0
SX = 140.0
shot("L37", "bas", C([SX, 1.4, 2.5], [SX, -4.1, 0.7], 26), {}, "the basement door at the bottom of the stairs, gold under it")
cue("L37", "sheet", on=True)
shot("L37.1", "bas", C([BAS - 0.2, -2.8, 1.35], [BAS - 0.2, 0.0, 0.7], 24), {
    "abe": {"pos": (BAS + 0.85, 0.0, 0.76), "yaw": 90, "lean": -90, "expr": SLEEPY}}, "inside: crates, shelves, and Abe lying along a long crate")
shot("L38", "bas", C([BAS - 0.5, -1.7, 1.2], [BAS - 0.3, 0.0, 0.8], 34), {
    "abe": {"pos": (BAS + 0.85, 0.0, 0.76), "yaw": 90, "lean": -90, "expr": SLEEPY}}, "the sheet over him glowing like a lampshade, his shoes out")
shot("L39", "bas", C([BAS - 0.4, -0.5, 2.3], [BAS - 0.5, 0.0, 0.85], 24), {
    "abe": {"pos": (BAS + 0.85, 0.0, 0.76), "yaw": 90, "lean": -90, "expr": SLEEPY},
    "me": SIT(BAS - 1.2, -1.9, 90, z=0.03, expr=SHEEPISH)}, "me on a crate beside him; he pulls the sheet off his face")
cue("L39", "sheet", on=False)
shot("L40", "bas", C([BAS - 0.3, 1.9, 1.25], [BAS - 0.3, 0.0, 0.95], 26), {
    "abe": SIT(BAS - 0.3, 0.0, 180, z=0.08, expr=TIRED, head=[0, -28])}, "Abe half sitting up, looking at the ceiling")
shot("L41", "bas", C([BAS + 1.0, -2.7, 1.3], [BAS - 1.0, -1.8, 1.2], 26), {
    "me": SIT(BAS - 1.2, -1.9, 0, z=0.03, expr="scared", head=[0, -22])}, "me looking up at the ceiling; a creak above")
# ---- 05 the bench (L42 to L57)
glow("L42", "abe", 5.0)
CROWD_POS = {  # the late-opening crowd, behind the bench (y < -4.6), all facing the bench (+y)
    "c1": (-4.2, -6.9), "c2": (-3.1, -5.6), "c3": (-1.9, -7.0), "c4": (-0.2, -5.7), "c5": (1.5, -6.9), "c6": (2.6, -5.5),
    "c7": (3.9, -6.8), "c8": (-5.4, -5.4), "c9": (-2.6, -8.3), "c10": (0.4, -8.4), "c11": (3.0, -8.2), "c12": (-4.4, -3.4),
    "c13": (4.7, -4.9), "c14": (-0.9, -9.0)}
ABE_B = SIT(HX["abe"], BY, 180, expr=TIRED)
shot("L42", "hall", C([0.0, -9.3, 6.2], [0.0, -3.0, 0.5], 22), {
    "abe": ABE_B, **{n: P(x, y, 180, expr="neutral") for n, (x, y) in CROWD_POS.items() if n != "c12"}},
     "the hall from high up: a crowd, every visitor a soft rim", hall=0.3)
shot("L43", "hall", C([-5.2, -9.0, 2.2], [-1.5, -5.4, 1.4], 24), {
    "c2": P(-3.1, -5.6, 150, expr=SMILE), "c3": P(-1.9, -7.0, 20, expr="soft"), "c8": P(-4.1, -6.5, 100, expr=SMILE),
    "c4": P(-0.2, -5.7, 200, expr=SMILE), "c9": P(-2.6, -8.3, 60, expr="neutral")}, "mid shot through the crowd, faces lit warm")
shot("L44", "hall", C([-5.6, -8.6, 2.3], [1.0, BY, 1.2], 24), {
    "abe": ABE_B, "c1": P(-1.2, -5.7, 190, expr="neutral"), "c4": P(2.9, -5.5, 160, expr="neutral")},
     "through gaps in the crowd: Abe lit like a lantern, the skeleton above")
glow("L44", "abe", 6.0, 1.0)
shot("L44.2", "hall", C([0.2, -8.4, 1.55], [0.9, -5.5, 1.55], 32), {
    "c3": P(0.6, -5.6, 180, arms=[110, 100], expr="worried"), "c5": P(1.6, -5.5, 180, arms=[110, 100], expr="worried"),
    "c6": P(2.6, -5.9, 180, arms=[100, 100], expr="worried")}, "two visitors squinting, hands up")
shot("L45", "hall", C([-7.4, -9.0, 1.9], [-4.7, -5.6, 1.5], 24), {
    "me": P(-4.7, -5.6, 113, expr=SHEEPISH), "c8": P(-5.6, -5.0, 140), "c12": P(-3.3, -5.0, 200), "c1": P(-5.0, -7.6, 180)},
     "me at the edge of the crowd, worried, looking toward the bench")
shot("L46", "hall", MV(([-2.6, -8.3, 1.55], [-3.4, -5.6, 1.5]), ([-2.0, -8.3, 1.55], [-2.6, -4.6, 1.5]), 28), {
    "me": P(-3.9, -5.9, 20, expr=SHEEPISH), "c2": P(-3.0, -5.7, 190), "c8": P(-4.9, -5.2, 170), "c1": P(-4.0, -7.6, 200)},
     "me squeezing between visitors, side on")
walk("me", "L46>", (-2.2, -4.7))
shot("L47", "hall", C([0.6, -0.7, 1.6], [-0.69, -6.4, 1.5], 16), {
    "abe": ABE_B, "c2": P(-3.1, -5.6, 140, expr="neutral"), "c3": P(-1.9, -7.0, 200, expr=SMILE), "c1": P(-4.2, -6.9, 160, expr=SMILE),
    "c9": P(-2.6, -8.3, 140, expr=SMILE), "c8": P(-5.4, -5.4, 190, expr=SMILE)}, "faces turn one after another and go still")
key("c3", "L47.2", yaw=180, expr="blank", blend=0.4)
key("c2", "L47.2+0.35", yaw=180, expr="blank", blend=0.4)
key("c1", "L47.2+0.7", yaw=180, expr="blank", blend=0.4)
key("c9", "L47.3", yaw=180, expr="blank", blend=0.4)
key("c8", "L47.3+0.3", yaw=180, expr="blank", blend=0.4)
cue("L47", "hall", level=0.12, dur=1.2)
HALLLV["v"] = 0.12
shot("L47.3-0.45", "hall", C([0.0, -9.4, 7.0], [-0.3, -5.6, 0.5], 10), {
    "abe": ABE_B, **{n: P(x, y, 180, expr="blank") for n, (x, y) in CROWD_POS.items() if n not in ("c12", "c14", "c3", "c4", "c10")}},
     "the crowd's glow from high up: a dark gap in it, right beside Grandad's light", hall=0.3)
shot("L48", "hall", C([-0.7, -8.6, 1.7], [-0.5, -3.4, 0.9], 12), {
    "me": P(-1.8, -7.3, 180, expr="scared"), "c2": P(-2.0, -5.6, 180, expr="blank"), "c8": P(-5.4, -4.2, 180, expr="blank"),
    "c1": P(-4.4, -6.9, 180, expr="blank"), "c4": P(0.8, -5.7, 180, expr="blank"), "c5": P(1.9, -6.8, 180, expr="blank"),
    "abe": ABE_B}, "over my shoulder: the crowd parts and the bench's end is in shadow")
shot("P02", "hall", C([-3.2, -6.0, 1.0], [-0.69, -3.7, 0.9], 24), {"abe": ABE_B}, "hold; the drone only, then one slow creak")
shot("L49", "hall", C([-5.0, 0.2, 0.45], [-0.3, -3.3, 1.45], 26), {"abe": ABE_B}, "the reveal, three-quarter front and low: the Stooped bent over my seat")
stooped("L49")
shot("L50", "hall", C([-1.3, -1.9, 0.5], [-0.69, -3.2, 2.4], 38), {"abe": ABE_B}, "close on the hanging coat front and its four brass buttons")
shot("L51", "hall", C([-6.8, -3.6, 0.7], [-0.69, -3.5, 1.5], 30), {"abe": ABE_B}, "low side profile: the right angle at its hips")
shot("L52", "hall", C([-0.69, -6.6, 3.0], [-0.69, -2.9, 2.2], 30), {"abe": ABE_B}, "along the flat of its back, level as a table")
stooped("L53", drop=2.16)
shot("L53", "hall", C([-1.9, -1.8, 0.4], [-0.69, -2.9, 0.34], 36), {"abe": ABE_B}, "close, low: the head hanging upside down at knee height")
stooped("L54", roll=140, pitch=0, drop=2.16)
shot("L54", "hall", C([-1.6, -1.5, 0.36], [-0.69, -2.9, 0.34], 36), {"abe": ABE_B}, "the head a quarter of the way round")
stooped("L54.2", roll=82, pitch=0, hyaw=12, drop=2.16)
shot("L54.2", "hall", C([-1.5, -1.5, 0.36], [-0.69, -2.9, 0.34], 36), {"abe": ABE_B}, "half round")
stooped("L54.3", roll=0, pitch=0, hyaw=0, drop=1.88)
shot("L54.3", "hall", C([-0.69, -1.45, 0.08], [-0.69, -2.9, 0.62], 34), {"abe": ABE_B}, "fully round, the right way up, eyes on camera, from below", hand=0.003)
shot("L55", "hall", C([-0.69, -1.45, 0.08], [-0.69, -2.9, 0.62], 34), {"abe": ABE_B},
     "hold the S072 framing: its face the right way up, eyes on camera, lit warm on one side only (the cover)", hand=0.003)
shot("L56", "hall", C([2.8, 0.6, 0.7], [-0.25, -3.0, 1.5], 28), {"abe": ABE_B}, "two-shot, low three-quarter: Grandad glowing, the Stooped a dark outline bent over my seat, no rim")
stooped("L57", roll=0, neck=-31, pitch=25, drop=1.5, hyaw=0)
cue("L57-0.5", "glk", level=0.15, dur=0.5)
cue("L57", "sface", level=0.7, dur=1.0, below=[0.35, -0.9, 0.1], aim=[-0.45, -2.0, 1.35])
cue("L58", "sface", level=0.0, dur=0.5)
shot("L57", "hall", C([1.3, 0.2, 0.62], [-0.5, -2.0, 1.28], 34), {
    "abe": ABE_B, "me": P(-0.22, -2.1, 165, expr="scared", lean=0, head=[-25, -8], look=[-1, 0])},
     "low three-quarter front two-shot: my scared face, its gape a hand below my chin, key from below", hand=0.002)
# ---- 06 the loophole (L58 to L70)
cue("L58", "glk", level=0.1)
shot("L58", "hall", C([0.9, -1.2, 1.15], [HX["abe"], BY, 1.1], 32), {"abe": SIT(HX["abe"], BY, 180, expr=TIRED, head=[0, -32])},
     "Abe won't look at me; he's looking at the tail")
cue("L58.2", "tailgold", on=1.0, dur=0.6)
shot("L58.2", "hall", C([5.1, -1.5, 1.95], [6.22, 1.5, 1.65], 32), {}, "the pale block at the tail's tip, lit gold")
cue("L59", "tailgold", on=0.0, dur=0.5)
cue("L59", "glk", level=1.0)
shot("L59", "hall", C([-0.69, -0.2, 1.55], [-0.69, -1.9, 1.5], 36), {
    "me": P(-0.69, -1.65, 180, expr=SHEEPISH), "abe": ABE_B}, "me thinking; behind me the Stooped's face is still turned up")
shot("L60", "hall", C([-3.2, -1.0, 1.55], [-0.69, -1.65, 1.5], 30), {"me": P(-0.69, -1.65, 180, expr="neutral"), "abe": ABE_B},
     "I turn toward the crowd")
key("me", "L60", yaw=0, blend=0.9)
shot("L61", "hall", C([0.6, -1.65, 1.55], [0.2, -6.8, 1.45], 30), {
    "abe": ABE_B, **{n: P(x, y, 180, expr="blank") for n, (x, y) in CROWD_POS.items() if n in ("c2", "c3", "c4", "c5", "c6", "c1", "c9", "c8")}},
     "the crowd from my eye line, all faces on me")
shot("L62", "hall", C([1.6, -5.3, 1.55], [-0.69, -1.9, 1.5], 30), {
    "me": P(-0.69, -1.65, 0, expr="neutral"), "abe": ABE_B}, "me standing tall in front of the bench, saying it out loud")
talk("me", "L62", "L62>")
shot("L63", "hall", MV(([0.0, -8.7, 1.55], [0.8, -6.0, 1.5]), ([0.0, -8.7, 1.55], [0.9, -5.4, 1.5]), 30), {
    "curator": P(0.9, -6.2, 180, expr="neutral"), "c3": P(-1.9, -6.8, 180, expr="blank"), "c5": P(2.0, -6.9, 180, expr="blank"),
    "c4": P(-0.4, -7.4, 180, expr="blank")}, "the curator in the crowd steps forward")
walk("curator", "L63>", (0.9, -5.0))
shot("L64", "hall", C([-3.3, -0.5, 1.7], [-0.69, -1.8, 1.5], 30), {
    "me": P(-0.69, -1.65, 0, expr=SHEEPISH, arms=[155, 0], head=[0, -22]), "abe": ABE_B}, "me pointing up at the tail")
cue("L65", "glk", level=0.1)
shot("L65", "hall", C([1.3, -1.5, 1.2], [HX["abe"], BY, 1.15], 34), {"abe": SIT(HX["abe"], BY, 180, expr=MOVED, head=[-42, 0])},
     "Abe finally looking at me")
cue("L66", "glk", level=0.1)
shot("L66", "hall", C([1.05, -1.9, 1.25], [HX["abe"], BY, 1.2], 40), {"abe": SIT(HX["abe"], BY, 180, expr=MOVED, head=[-30, 0])},
     "the glow sinks out of him like a slow sunset")
glow("L66", "abe", 1.0, 3.0)
cue("L67", "glk", level=1.0)
shot("L67", "hall", C([0.0, -2.6, 1.3], [0.0, -6.4, 2.3], 22), {
    "abe": SIT(HX["abe"], BY, 180, expr=MOVED), **{n: P(x, y, 180, expr="soft") for n, (x, y) in CROWD_POS.items() if n not in ("c12", "c14")}},
     "tiny soft sparks drift up over the crowd and go out")
cue("L67", "sparks", center=[0.0, -6.8])
glow("L67", CROWD, 0.4, 1.5)
shot("L68", "hall", C([0.3, 0.6, 1.4], [-0.3, -3.2, 1.6], 24), {"abe": SIT(HX["abe"], BY, 180, expr=MOVED)},
     "Abe faint and ordinary at his end, the Stooped still at mine, face up")
cue("L69", "stooped", hidden=True)
cue("L69", "glk", level=0.1)
shot("L69", "hall", C([0.3, 0.6, 1.4], [-0.3, -3.2, 1.6], 24), {
    "abe": SIT(HX["abe"], BY, 180, expr=MOVED), "me": SIT(HX["me"], BY, 180, expr=MOVED),
    "c3": P(-2.3, -1.7, 180, arms=[40, 40], expr=SMILE), "c5": P(2.2, -1.8, 180, arms=[40, 40], expr=SMILE),
    "c4": P(-3.6, -1.9, 180, arms=[40, 40], expr=SMILE), "c6": P(3.5, -1.7, 180, arms=[40, 40], expr=SMILE)},
     "me seated shoulder to shoulder with Abe, nothing over my seat, the crowd starting to clap")
key("c3", "L70", arms=[75, 75], blend=0.2)
key("c5", "L70", arms=[75, 75], blend=0.2)
key("c4", "L70+0.25", arms=[75, 75], blend=0.2)
key("c6", "L70+0.25", arms=[75, 75], blend=0.2)
cue("L70.2", "tally", on=1.0, dur=0.4)
cue("L71.1", "tally", on=0.0, dur=0.4)
shot("L70.2", "hall", C([-2.9, -2.6, 0.62], [-1.25, -3.4, 0.3], 16), {
    "abe": SIT(HX["abe"], BY, 180, expr=MOVED), "me": SIT(HX["me"], BY, 180, expr=MOVED)},
     "the lore plant: wide on my seat, the iron leg lit, two short strokes scratched in", step=4, hand=0.002)
# ---- 07 the name (L71 to L80)
shot("L71.1", "hall", C([6.9, -1.7, 1.4], [5.1, -0.3, 1.45], 28), {
    "curator": P(5.55, -0.5, -90, arms=[50, 0], expr=SMILE), "abe": P(4.6, -0.5, 90, arms=[50, 0], expr=SMILE)},
     "the curator and Abe by the tail, smiling; cut before the hands meet")
SRX2 = 380.0
glow("L72", "abe", 1.0)
shot("L72", "sr", C([SRX2 + 5.0, 0.3, 1.5], [SRX2 - 0.4, 4.0, 1.3], 26), {
    "abe": P(SRX2 - 1.4, 4.0, 90, expr=SMILE), "c1": P(SRX2 + 0.2, 4.0, -90, expr=SMILE)}, "dusk street: a neighbour stops to talk")
glow("L73", "me", 0.0)
shot("L73", "hall", TWO, {
    "abe": SIT(HX["abe"], BY, 180, expr=SMILE), "me": SIT(HX["me"], BY, 180, expr=SMILE)}, "back on the bench, shoulder to shoulder (L13 matched)", hall=0.3)
shot("L74", "hall", C([0.0, -0.9, 1.25], [0.0, BY, 1.15], 36), {
    "abe": SIT(HX["abe"], BY, 180, expr=SMILE), "me": SIT(HX["me"], BY, 180, expr=SMILE)}, "two faint gold rims, his and mine")
glow("L74", "me", 1.0, 1.0)
cue("L75", "glk", level=0.1)
shot("L75", "hall", C([0.69, -1.6, 1.3], [0.69, BY, 1.25], 38), {"abe": SIT(HX["abe"], BY, 180, expr=SHEEPISH, head=[0, -30])},
     "Abe glances up at the mended block")
shot("L75.3", "hall", C([5.1, -1.2, 1.75], [6.22, 1.5, 1.65], 34), {}, "the mended block, ordinary light")
cue("L76", "glk", level=1.0)
shot("L76", "hall", C([-0.69, -1.6, 1.3], [-0.69, BY, 1.2], 36), {"me": SIT(HX["me"], BY, 180, expr="neutral")}, "me close on the bench, faint rim")
cue("L77", "glk", level=0.1)
shot("L77", "hall", C([0.69, -1.6, 1.3], [0.69, BY, 1.25], 38), {"abe": SIT(HX["abe"], BY, 180, expr=SMILE, head=[0, -26])},
     "Grandad close, faint rim, looking up at the skeleton")
cue("L78", "glk", level=1.0)
glow("L78", "me", 2.2, 0.5)
shot("L78", "hall", C([-1.9, -2.2, 0.95], [-1.15, -3.0, 0.62], 20), {"me": SIT(HX["me"], BY, 180, expr="neutral", arms=[40, 0])},
     "my hand on my knee, a faint gold rim round it")
shot("L79", "hall", C([-0.69, -1.6, 1.3], [-0.69, BY, 1.2], 34), {"me": SIT(HX["me"], BY, 180, expr="neutral", look=[1, 0])},
     "the smile gone, eyes sliding to the side")
cue("L79.1", "hall", level=0.08, dur=1.4)
cue("L80", "hall", level=0.02, dur=0.9)
cue("L80", "cold", level=1.0, dur=0.9)
glow("L80", "me", 0.8, 0.9)
LOW = C([-0.69, -1.8, 0.3], [-0.69, -3.2, 0.72], 16)
shot("L80", "hall", LOW, {"abe": SIT(HX["abe"], BY, 180, expr=SMILE), "me": SIT(HX["me"], BY, 180, expr="neutral")},
     "a cold low hold from knee height in front of my seat: my knees and the seat edge, me seated and still; the hall dimmer behind")
shot("P03", "hall", LOW, {"abe": SIT(HX["abe"], BY, 180, expr=SMILE), "me": SIT(HX["me"], BY, 180, expr="neutral")}, "the loop beat")

# ------------------------------------------------------------------------------------------------ sound
sfx = [
    {"at": "L29", "kind": "hum_sweep", "db": -18, "dur": 1.6},
    {"at": "P01+0.45", "kind": "thud", "db": -10},
    {"at": "L30", "kind": "hit", "db": -16},
    {"at": "L35.1", "kind": "creak", "db": -14, "dur": 1.6},
    {"at": "L41.1", "kind": "creak", "db": -18, "dur": 1.2},
    {"at": "L47", "kind": "glide", "db": -26, "dur": 1.4},
    {"at": "P02+0.35", "kind": "creak", "db": -9, "dur": 1.8},
    {"at": "L49", "kind": "sting", "db": -17},
    {"at": "L54.3", "kind": "glide", "db": -22, "dur": 1.6},
    {"at": "L57", "kind": "thud", "db": -22},
    {"at": "L66", "kind": "hum_sweep", "db": -26, "dur": 2.8},
    {"at": "L69.1", "kind": "creak", "db": -18, "dur": 1.0},
    {"at": "L70", "kind": "bell", "db": -20, "dur": 2.0},
    {"at": "L80>", "kind": "glide", "db": -17, "dur": 1.2},
]

story = {
    "slug": "ep51-fossil-hall",
    "title": "In this town, you glow brighter for every secret you keep",
    "made_for_kids": False,
    "premise": "In a town where every person glows a little brighter for each secret they keep, I am the one person with no glow at all, because I tell everything. My grandad, a museum guide, has always been the brightest man in town, and this spring the curator starts asking about a mended bone in the big skeleton's tail. Every Friday he gets brighter, until neighbours cross the road, the museum moves him to its dark galleries, and a line is wiped clean through the dust on every case at knee height.",
    "twist": "The only secret my grandad has kept for nine years is mine: I knocked down the skeleton's tail in my first summer helping out, and he told everyone it was him. Every time somebody asked about that tail, he kept it again, so the brightest man in town was the most loyal. I never glowed because he was keeping my secret for me.",
    "world": "a town museum's long fossil hall on a Friday late opening: a chequered marble floor, a giant blocky skeleton of ochre bone on an iron frame, one long bench built for two, glass cases, dark side galleries, and soft gold outlines of light round everyone who keeps a secret",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffcf5c",
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#9aa3b2", "fog_density": 0.0, "fog_start": 6.0, "sky": "#1a1c24", "sky_strength": 0.2, "exposure": 0.0,
             "flash_safe": True},
    "grade": {"shadows": [-0.02, 0.0, 0.05], "highlights": [0.03, 0.01, -0.03], "saturation": 0.98, "contrast": 1.05,
              "vignette": 0.34, "bloom": 0.26, "grain": 0.012},
    "phonemes": {"mended": "mˈɛndɪd"},
    "glow": GLOW,
    "glow_later": ["me"],
    "glow_lights": ["abe", "planner", "groom", "bride"],
    "glow_light_w": 260.0,
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 53, "mode": "lydian", "bpm": 84, "seed": 51,
              "sections": [
                  {"at": 0, "voices": ["bubble", "pad"], "energy": 0.3},
                  {"at": "L21", "voices": ["bubble", "pad"], "energy": 0.36},
                  {"at": "L30", "voices": ["drone", "pad", "bubble"], "energy": 0.55},
                  {"at": "L37", "voices": ["drone", "pad"], "energy": 0.5},
                  {"at": "L42", "voices": ["drone", "pad", "choir"], "energy": 0.55},
                  {"at": "L49", "voices": ["drone", "choir"], "energy": 0.6},
                  {"at": "L66", "voices": ["drone", "pad", "piano"], "energy": 0.5, "mode": "major", "root": 53},
                  {"at": "L76", "voices": ["drone", "choir"], "energy": 0.45},
              ]},
    "sound": {"floor": "stone", "steps_db": -22,
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "L04", "lufs": -40},
                  {"kind": "room", "from": "L05", "to": "L06", "lufs": -38},
                  {"kind": "room", "from": "L09", "to": "end", "lufs": -38},
                  {"kind": "hum", "from": "L10", "to": "L29", "lufs": -44},
                  {"kind": "hum", "from": "L42", "to": "L66", "lufs": -42},
                  {"kind": "drone", "from": "L30", "to": "end", "lufs": -34},
                  {"kind": "drips", "from": "L33", "to": "L36", "lufs": -42},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "L29>", "to": "L30", "keep": ["thud"]},
                              {"from": "L48>", "to": "L49", "keep": ["creak"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
