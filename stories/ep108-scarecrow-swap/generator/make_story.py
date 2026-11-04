"""Writes ../story.json for ep108 "Don't Wave at the SCARECROW" (script.md, 2026-11-04).
Run: python stories/ep108-scarecrow-swap/generator/make_story.py

The words are in lines.json (captions already split to 2 or 3 words, so chunk numbers are the file's). Places are in
../layout.py (shared with set.py). A character facing -y has yaw 0, +x 90, +y 180, -x -90.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import layout as G  # noqa: E402

OUT = HERE.parent / "story.json"
REV = 3
lines = json.loads((HERE / "lines.json").read_text())
# the 0.4 s music drop before L12
idx = next(i for i, l in enumerate(lines) if l["id"] == "L12")
lines.insert(idx, {"id": "P01", "pause": 0.4, "chunks": [["", ""]]})
D2R = math.pi / 180
PX, PY = G.POST
STEP = G.STEP
KX, KY = G.KIT
LX, LY = G.LIV


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
    # me: 19, green flannel over a white tee, jeans, boots
    "me": person("#e0ac80", "#3fae4a", "#4a6fa8", "#6a4a30", hair="swoop", hair_c="#5a3a22", pattern="plaid",
                 pattern_c="#2a7a3a", collar="#fffaf0", brow_w=1.6),
    # Grandpa Walt: red plaid, overalls blue, glasses, a sack hat over his cap (the field), white mustache and brows
    "grandpa": person("#e8b890", "#d6453a", "#4a6ea8", "#6a4a30", hair="cap", hair_c="#d8d8de", pattern="plaid",
                      pattern_c="#8a2a22", extras=["glasses"], extra_c="#2a2a30", hat="bucket", hat_c="#c9a46a",
                      width=1.04),
    # Grandma Dot: gray bun, blue cardigan, floral dress, apron
    "grandma": person("#f0c8a0", "#5a8fd6", "#e07ab0", "#8a5a3a", hair="bun", hair_c="#c4c4d0", eyes="lashes",
                      extras=["apron"], extra_c="#fff4dc", height=0.95, brow_w=1.4, width=0.96),
    # the straw one at dinner: Grandpa's second plaid shirt and tan cap on a burlap sack
    "straw": person("#d8b878", "#d6453a", "#4a6ea8", "#6a4a30", hair="none", hair_c="#d8b878", pattern="plaid",
                    pattern_c="#8a2a22", hat="ballcap", hat_c="#6a4a2a", eyes="button", width=1.04),
}
acting = {n: [{"at": 0, "hidden": True, "pos": [60 + 6 * i, 60]}] for i, n in enumerate(cast)}
last = {n: [60 + 6 * i, 60] for i, n in enumerate(cast)}
cues = []
SH = []


def put(who, at, pos, yaw=None, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": list(last[who])})
    k = {"at": at, "pos": p, "blend": 0.0, "hidden": False}
    if yaw is not None:
        k["yaw"] = yaw
    k.update(kw)
    acting[who].append(k)
    last[who] = p


def go(who, at, pos, **kw):
    p = list(pos)
    acting[who].append({"at": at, "pos": p, **kw})
    last[who] = p


def beat(who, at, **kw):
    acting[who].append({"at": at, "pos": list(last[who]), **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def shot(at, camera, name, step=2, hand=0.004):
    SH.append((at, camera, step, hand, name))


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    if p1 is None:
        return [[0, list(p0), list(t0), l0]]
    return [[0, list(p0), list(t0), l0], [1, list(p1), list(t1 if t1 is not None else t0), l1 or l0]]


def near(tgt, d, lens, az=0.0, dz=0.0, push=0.14, dx=0.0):
    """A camera d metres from tgt at azimuth az (0 = south of it, looking +y), pushing in by `push`."""
    a = az * D2R
    tx, ty, tz = tgt

    def at(dd):
        return [tx + dd * math.sin(a) + dx, ty - dd * math.cos(a), tz + dz]
    return mv(at(d), tgt, lens, at(d * (1 - push)), tgt, lens)


def wave(who, ref, n, lo, hi, other=86, both=False, step=0.19):
    """Alternating arm angles for n half-waves starting at ref (a plain "Lxx.n" reference)."""
    for i in range(n):
        a = hi if i % 2 == 0 else lo
        side = [a, a] if both else [other, a]
        acting[who].append({"at": f"{ref}+{i * step:.2f}", "side": side, "blend": 0.12})


# ---------------------------------------------------------------------------------------------- the cast's marks
FACE = (0.0, PY, 1.72)           # Grandpa's face on the post
cue(0, "look", id="day", dur=0)
cue(0, "flash", on=0.0, bob=0.0, show=0.0)
cue(0, "wave", on=0.0)
cue(0, "tagbig", k=0.0)
cue(0, "crossword", on=0.0)
cue(0, "crowfly", u=0.0)
cue(0, "mask", on=1.0)
cue("L12", "mask", on=0.0, dur=0.3)     # pushed up onto the hat brim, glasses showing
cue("L16", "mask", on=1.0)

# Grandpa on the post for the whole film: arms along the crossbar
last["grandpa"] = [PX, PY, STEP]
acting["grandpa"] = []                   # no hidden key at 0: the first drawing already holds him on the post
put("grandpa", 0, [PX, PY, STEP], 0, arms=[0, 0], side=[86, 156], expr="blank", blink=True)

# ===== 01 the rule and the first wave (L01 to L02)
shot(0, near((0.22, PY, 1.72), 2.6, 20, az=-3, push=0.08), "scarecrow")                       # the first frame: face and glove
wave("grandpa", "L01.2", 3, 148, 164, other=86)                                     # the glove tips while "SCARECROW" lands
shot("L01.2", near((0.6, PY, 1.95), 2.7, 24, az=-8, push=0.1), "glove")
wave("grandpa", "L01.3", 6, 140, 168, other=86)
# L02: me at the fence at dusk, then the glove lowering
cue("L02", "look", id="dusk", dur=0)
cue("L02", "wave", on=1.0)
put("me", "L02", [0.0, -6.5], 180, arms=[0, 62], expr="worried", head=[0, 4])
shot("L02", mv([0.7, -3.4, 1.55], [0.0, -6.5, 1.45], 30, [0.5, -4.0, 1.55], [0.0, -6.5, 1.45], 30), "mefence")
acting["grandpa"].append({"at": "L02.2", "side": [86, 86], "blend": 0.5})
shot("L02.2", near((0.6, PY, 1.7), 3.2, 22, az=10, push=0.1), "lowering")
cue("L02.2+0.5", "wave", on=0.0)

# ===== 02 the mystery at work (L03 to L10)
cue("L03", "look", id="day", dur=0)
hide("me", "L03")
shot("L03", mv([-6.2, -8.6, 1.5], [-13.0, -1.0, 0.5], 17, [-6.0, -8.0, 1.45], [-13.0, -1.0, 0.5], 17), "road", step=2)
shot("L03.2", mv([-4.0, -12.0, 1.2], [-14.0, -6.0, 0.8], 28, [-5.0, -10.0, 1.3], [-14.0, -6.0, 0.8], 28), "crowfence")
LX_, LY_ = G.LNEIGH
shot("L04", near((LX_, LY_, 1.9), 4.8, 24), "neighbor")
shot("L04.3", near((LX_ + 0.03, LY_ - 0.1, 2.0), 2.6, 28, az=5), "hatcrow")
shot("L05", mv([0.5, -9.0, 1.0], [0.0, 3.0, 0.6], 22, [0.3, -7.6, 1.05], [0.0, 3.0, 0.6], 22), "empty")
cue("L05.1", "tagbig", k=1.0, dur=0.3)
shot("L05.1", mv([1.5, -5.0, 1.1], [0.0, 3.0, 0.8], 24, [1.5, -4.0, 1.1], [0.0, 3.0, 0.8], 24), "tagclose")
cue("L06", "tagbig", k=0.0, dur=0.0)
# the kitchen at dinner (the straw one in Grandpa's chair, seen from behind)
put("straw", "L06", [KX, KY - 1.5], 180, arms=[62, 62], expr="neutral", head=[0, 2])
cue("L06", "sit", who="straw", on=True)
shot("L06", mv([KX + 0.7, KY - 5.2, 1.5], [KX, KY - 1.5, 1.1], 24, [KX + 0.5, KY - 4.6, 1.5], [KX, KY - 1.5, 1.1], 24), "dinner")
# L07: the mail jeep passes the farmhouse, its driver waving at the empty rocker
cue("L07", "jeepgo", x0=30.0, x1=40.0, dur=2.4)
cue("L07", "jwave", on=1.0, dur=0.3)
cue("L07", "wave", on=1.0)
RX, RY = G.ROCKER
shot("L07", mv([RX - 1.2, -22.0, 1.5], [RX, RY, 1.0], 20, [RX - 1.0, -21.0, 1.5], [RX, RY, 1.0], 20), "jeep")
cue("L07.2", "jwave", on=0.0, dur=0.3)
cue("L07.2", "wave", on=0.0)
shot("L07.2", mv([RX + 0.2, -13.4, 0.95], [RX, RY, 0.65], 26, [RX + 0.1, -12.6, 0.95], [RX, RY, 0.65], 26), "rocker")
shot("L08", mv([KX + 0.8, KY - 4.2, 1.5], [KX, KY - 1.5, 1.15], 26, [KX + 0.6, KY - 3.5, 1.5], [KX, KY - 1.5, 1.15], 26), "strawback")
put("grandma", "L08.1", [KX, KY + 4.9], 0, expr="smile", arms=[0, 0], head=[0, 3])
cue("L08.1", "sit", who="grandma", on=True)
acting["grandma"].append({"from": "L08.1", "to": "L08>", "mouth": [0.5, 0.5], "flap": True})
shot("L08.2", mv([KX + 0.5, KY + 1.8, 1.5], [KX, KY + 4.9, 1.3], 28, [KX + 0.4, KY + 2.6, 1.5], [KX, KY + 4.9, 1.3], 28), "grandmatalk")
hide("grandma", "L09")
cue("L09", "sit", who="grandma", on=False)
shot("L09", mv([KX + 2.4, KY - 1.3, 1.5], [KX + 0.4, KY - 1.2, 1.0], 22, [KX + 2.0, KY - 1.3, 1.45], [KX + 0.4, KY - 1.2, 1.0], 22), "sleeve")
# L10: dusk at the post: the crossword on the crossbar, Grandma's palm sliding away, then she walks home
cue("L10", "look", id="dusk", dur=0)
cue("L10", "crossword", on=1.0)
hide("straw", "L10")
put("grandma", "L10", [2.0, 1.2], 180, arms=[0, 98], expr="smirk", head=[0, 6])
beat("grandma", "L10.1", arms=[0, 60], blend=0.5)
shot("L10", mv([0.2, -1.4, 1.75], [1.6, 2.3, 1.55], 21, [0.5, -0.9, 1.75], [1.6, 2.3, 1.55], 21), "crossword")
put("grandma", "L10.2", [1.0, -0.6], 0, expr="smirk", arms=[0, 0])
go("grandma", "L10.2+0.1", [1.0, -0.6])
go("grandma", "L10>", [1.0, -4.8])
shot("L10.2", mv([1.9, -9.0, 1.45], [1.0, -2.8, 1.35], 36, [1.7, -8.0, 1.45], [1.0, -3.4, 1.35], 36), "grandmawalks")

# ===== 03 the beam and the reveal (L11 to L16)
put("me", "L11", [34.4, -9.2], 0, arms=[0, 78], expr="worried", head=[0, 4])
hide("grandma", "L11")
cue("L11", "flash", show=1.0, on=0.0, bob=0.0)
shot("L11", mv([33.0, -14.5, 1.5], [34.4, -9.2, 1.3], 30, [33.2, -13.5, 1.5], [34.4, -9.2, 1.3], 30), "porch")
put("me", "L11.1", [0.0, -10.0], 180, arms=[0, 78], expr="worried")
go("me", "L11.1+0.1", [0.0, -10.0])
go("me", "L11.2", [0.9, -2.6])
cue("L11.1", "flash", on=1.0, bob=1.0, show=1.0, beam=1.0, pow=0.6, dur=0.4)
shot("L11.1", mv([-0.7, -13.5, 1.75], [0.3, -3.0, 1.0], 24, [-0.5, -12.0, 1.75], [0.3, -3.0, 1.0], 24), "beamrows")
cue("L11.2+0.3", "flash", bob=0.0, dur=0.5)
shot("L11.2", mv([-0.9, -4.6, 1.35], [0.9, -2.5, 1.2], 34, [-0.6, -4.2, 1.35], [0.9, -2.5, 1.2], 34), "torch")
put("me", "P01", [1.1, -1.6], 180, arms=[0, 78], expr="squeeze", head=[0, 2])
go("me", "P01+0.05", [1.1, -1.6])
shot("P01", mv([-1.4, -0.9, 1.2], [0.0, PY, 1.45], 30, [-1.2, -0.5, 1.25], [0.0, PY, 1.45], 30), "chest")
beat("grandpa", "L12", expr="blank", blink=False)
shot("L12", mv([0.9, -0.5, 0.8], [0.0, PY, 1.72], 36, [0.7, 0.1, 0.85], [0.0, PY, 1.72], 36), "frombelow")
shot("L12.2", near((0.0, PY, 1.7), 1.2, 38, az=8, dz=-0.35), "glasses")
beat("grandpa", "L13", expr="blank", blink=False)
cue("L13", "flash", beam=0.0)
cue("L14", "flash", beam=1.0)
acting["grandpa"].append({"from": "L13", "to": "L13>", "mouth": [0.18, 0.18], "flap": True})
shot("L13", near((0.05, PY, 1.8), 2.1, 34, az=-12, dz=-0.35, push=0.08), "whisperface")
beat("me", "L13.2", expr="wide")
shot("L13.2", mv([0.3, 1.0, 1.4], [1.1, -1.6, 1.35], 32, [0.4, 0.8, 1.4], [1.1, -1.6, 1.35], 32), "mestunned")
beat("grandpa", "L14", expr="blank", blink=False)
shot("L14", mv([-2.1, -1.6, 1.35], [0.0, PY, 1.55], 48, [-1.9, -1.4, 1.35], [0.0, PY, 1.55], 48), "reveal")
shot("L14.1", near((0.0, PY, 1.2), 3.2, 28, az=-25), "whole")
shot("L15", mv([-5.0, -3.8, 1.4], [-8.6, -6.8, 1.15], 40, [-5.4, -4.6, 1.4], [-8.6, -6.8, 1.15], 40), "crowlook")
hide("me", "L15")
cue("L15", "flash", on=0.0, bob=0.0, show=0.0, beam=0.0, dur=0.5)
cue("L15.2", "crowfly", u=1.0, dur=1.3)
shot("L15.2", mv([-5.5, -4.4, 1.5], [-8.6, -6.8, 1.4], 30, [-6.5, -5.4, 1.7], [-10.4, -8.0, 4.2], 30), "crowflap")
shot("L15.4", near((0.0, PY, 1.7), 1.9, 34, az=10, dz=-0.2), "himface")
beat("grandpa", "L16", blink=True)
# L16: smash cut to the bright kitchen
cue("L16", "look", id="day", dur=0)
put("straw", "L16", [KX, KY - 1.5], 180, arms=[62, 62], expr="neutral", head=[0, 2])
cue("L16", "sit", who="straw", on=True)
put("grandma", "L16", [KX + 0.95, KY - 1.2], -80, expr="laugh", arms=[0, 40], head=[0, 3])
acting["grandma"].append({"from": "L16", "to": "L16>", "mouth": [0.5, 0.5], "flap": True})
shot("L16", mv([KX + 1.7, KY + 2.9, 1.55], [KX + 0.45, KY - 1.3, 1.05], 20, [KX + 1.4, KY + 2.5, 1.55], [KX + 0.45, KY - 1.3, 1.05], 20), "kitchenwide")
shot("L16.2", mv([KX + 0.3, KY + 1.6, 1.4], [KX, KY - 1.5, 1.25], 36, [KX + 0.3, KY + 1.2, 1.4], [KX, KY - 1.5, 1.25], 36), "strawface")

# ===== 04 the sting (L17 to L21)
cue("L17", "look", id="gold", dur=0)
hide("straw", "L17")
hide("grandma", "L17")
cue("L17", "sit", who="grandma", on=False)
put("grandma", "L17", [1.4, 1.2], -90, arms=[0, 98], expr="smirk", head=[0, 4])
shot("L17", mv([3.0, 0.6, 1.5], [1.0, 1.6, 1.4], 26, [2.6, 0.9, 1.5], [1.0, 1.6, 1.4], 26), "crosswordgold")
# L17.1: Grandma comes back in at the back door (three straw-gold strokes on the frame, Rufus on the mat)
DX, DY = G.DOOR
put("grandma", "L17.1", [DX - 3.0, DY - 0.2], 90, expr="smile", arms=[0, 0])
go("grandma", "L17.1+0.1", [DX - 3.0, DY - 0.2])
go("grandma", "L17>", [DX - 0.5, DY + 0.7])
shot("L17.1", mv([DX - 3.4, DY - 3.0, 1.3], [DX - 0.9, DY - 0.2, 1.4], 24, [DX - 3.1, DY - 2.8, 1.3], [DX - 0.9, DY - 0.2, 1.4], 24), "backdoor")
hide("grandma", "L18")
shot("L18", mv([-1.3, 4.2, 0.9], [0.0, G.CHAIR[1], 0.4], 26, [-0.9, 4.6, 0.95], [0.0, G.CHAIR[1], 0.4], 26), "lawnchair")
shot("L18.2", mv([1.2, 5.2, 0.7], [0.3, G.CHAIR[1], 0.35], 30, [1.0, 5.7, 0.7], [0.3, G.CHAIR[1], 0.35], 30), "thermos")
# L19: the couch
cue("L19", "look", id="day", dur=0)
put("grandma", "L19", [LX - 0.64, LY], 180, expr="smile", arms=[40, 0], head=[0, 2])
cue("L19", "sit", who="grandma", on=True)
acting["grandma"].append({"from": "L19", "to": "L19>", "mouth": [0.5, 0.5], "flap": True})
put("straw", "L19", [LX + 0.64, LY], 180, arms=[22, 22], expr="neutral", head=[0, 2])
cue("L19", "sit", who="straw", on=True)
shot("L19", mv([LX - 1.7, LY + 3.4, 1.4], [LX, LY, 0.95], 24, [LX - 1.4, LY + 3.0, 1.4], [LX, LY, 0.95], 24), "couchback")
shot("L19.2", mv([LX - 2.7, LY + 2.6, 1.25], [LX - 0.4, LY, 1.2], 34, [LX - 2.3, LY + 2.3, 1.25], [LX - 0.4, LY, 1.2], 34), "grandmasmile")
beat("grandma", "L20", arms=[62, 0], expr="warm", blend=0.4)
shot("L20", mv([LX - 0.03, LY + 3.6, 1.6], [LX - 0.03, LY + 0.3, 0.95], 20, [LX - 0.03, LY + 3.3, 1.55], [LX - 0.03, LY + 0.3, 0.95], 20), "remote")      # her hand and the remote from the first drawing
shot("L20.1", mv([LX + 0.9, LY + 1.9, 1.15], [LX - 0.15, LY + 0.65, 0.88], 30, [LX + 0.7, LY + 1.6, 1.1], [LX - 0.15, LY + 0.65, 0.88], 30), "remote2")
# L21: sunset, the jeep passes, Grandpa waves at everybody
cue("L21", "look", id="gold", dur=0)
hide("grandma", "L21")
hide("straw", "L21")
cue("L21", "jeepgo", x0=-5.0, x1=9.0, dur=1.3)
cue("L21", "jwave", on=1.0, dur=0.3)
cue("L21", "wave", on=1.0)
wave("grandpa", "L21", 12, 128, 170, both=True, step=0.2)
shot("L21", mv([0.5, 5.6, 2.7], [0.0, -9.0, 0.5], 14.5, [0.4, 5.2, 2.7], [0.0, -9.0, 0.5], 14.5), "everybody")
shot("L21.2", near((0.25, PY, 1.8), 1.7, 20, az=-3, push=0.2), "loop")

# ---------------------------------------------------------------------------------------------- finish
shots, names = [], {}
for i, (at, camera, step, hand, nm) in enumerate(SH):
    s = {"id": f"S{i + 1:02d}", "cam": camera, "step": step, "hand": hand}
    if i:
        s["at"] = at
    shots.append(s)
    names[nm] = s["id"]

sfx = [
    {"at": "L01.3", "kind": "hit", "db": -9},                        # the low comic note on "BACK"
    {"at": "L10.2", "kind": "door", "db": -22, "synth": True},        # not heard: a soft screen-door as she leaves
    {"at": "L20.1", "kind": "thud", "db": -20, "dur": 0.5},           # the couch cushion's soft thump
    {"at": "L21>-0.25", "kind": "hit", "db": -9},                     # on the last word
]
sfx = [s for s in sfx if s["at"] != "L10.2"]
music = {
    "root": 50, "mode": "major", "bpm": 120, "seed": 108,
    "sections": [
        {"at": 0, "voices": ["musicbox", "pulse"], "energy": 0.4},
        {"at": "L11", "voices": ["musicbox", "drone"], "energy": 0.25},
        {"at": "L12", "voices": ["drone"], "energy": 0.3},
        {"at": "L15", "voices": ["musicbox", "pulse", "pad"], "energy": 0.5},
    ],
}
sound = {
    "floor": "grass", "steps_db": -24,
    "ambience": [{"kind": "wind", "from": 0, "to": "end", "lufs": -42},
                 {"kind": "crickets", "from": "L10", "to": "L16", "lufs": -44}],
    "sfx": sfx,
    "music_drops": [{"from": "P01", "to": "P01>"}],
    "rev": REV,
}
polish = {"reveal": ["L14"], "twist": "L14", "emph": ["L01.3", "L05.1", "L08.1", "L10.2", "L14", "L16.2", "L20.1", "L21.2"],
          "sway": [names["frombelow"], names["glasses"], names["whisperface"]]}
story = {
    "slug": "ep108-scarecrow-swap",
    "title": "Don't Wave at the SCARECROW 🌾",
    "made_for_kids": False,
    "premise": ("My grandpa's pumpkin patch is the only field on our road without a single crow, and since June "
                "Grandpa has gone quiet at dinner while Grandma takes his crossword out to the field every night. "
                "On Tuesday at dusk the scarecrow waved back at me."),
    "twist": ("Crows are scared of Grandpa, so he has stood on the scarecrow's post since June while a straw scarecrow "
              "in his clothes sits in his chair at dinner, and Grandma, who set it up with him, likes the straw one "
              "better because it never hogs the remote."),
    "world": ("A late-summer farm: orange pumpkins on green vines, a gold cornfield, a red barn, a white farmhouse with "
              "a yellow kitchen, neighbors' fields black with crows, and a scarecrow's post in the middle of the patch."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff8c1a",
    "gap": 0.12,
    "tail": 0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#cfe6f5", "fog_density": 0.003, "fog_start": 40.0, "sky": "#8fd3ff",
             "sky_strength": 1.0, "exposure": 0.2, "flash_safe": True, "polish": True},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.1, "contrast": 1.05,
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
    "set_moves": [names["jeep"], names["crowflap"], names["everybody"]],
}
story["look"]["polish"] = polish
story["clip_ok"] = ["beam.cone", "S20/beam.cone", "S20/beam"]
story["asr_forgive"] = ["there is", "there's"]
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
print(names)
