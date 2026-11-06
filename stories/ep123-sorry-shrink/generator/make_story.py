"""Writes ../story.json for ep123 "Every SORRY Here Costs An Inch" (script.md, 2026-11-05, batch 13).
Run: python stories/ep123-sorry-shrink/generator/make_story.py

The words are in lines.json (captions already two or three words). Places are in ../layout.py (shared with set.py).
A character facing -y has yaw 0. Nothing blinks, nothing glows, no light change, one sunny afternoon.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import layout as G  # noqa: E402

OUT = HERE.parent / "story.json"
REV = 7
lines = json.loads((HERE / "lines.json").read_text())
D2R = math.pi / 180
T = G.T
MX, MY = G.MAE
HEAD = (MX, MY, T + G.MAE_EYE)         # Mae's head centre (full height)
HX, HY, HZ = G.ME_HEAD


def person(skin, shirt, pants, shoes, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, collar=None,
           extras=(), eyes="round", sleeves="long", brow_w=1.0, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": "none", "hat_c": "#333333",
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
    # me: 31, sandy hair, blue polo, a big wristwatch (added in set.py)
    "me": person("#e8b890", "#3f7fe0", "#4a5a78", "#6a4a30", hair="swoop", hair_c="#c9a46a", collar="#fffaf0", brow_w=1.5),
    # Aunt Mae: 74, a gray perm (set.py adds the curls), red cat-eye glasses, a coral cardigan, pearls, sensible shoes.
    # An evenly scaled R6 rig, 13 cm tall.
    "mae": person("#f0c8a0", "#ff7f6b", "#7a5a8a", "#6a4a30", hair="bun", hair_c="#c4c4d0", pattern="knit",
                  pattern_c="#e8604a", eyes="lashes", extras=["glasses"], extra_c="#d22f3c", brow_w=1.0,
                  height=G.MAE_H / 1.75, width=0.97),
    # a neighbor, adult, one shot at L03 (a red cap), through the porch glass
    "neighbor": person("#c98f68", "#5cc46a", "#4a5a78", "#2a2a40", hair="cap", hair_c="#2a1d15", pattern="stripes",
                       pattern_c="#fffaf0"),
}
cast["mae"]["face"]["cheeks"] = "#ff9a88"   # raised, rosy cheeks: warm and mischievous, never stern
acting = {n: [] for n in cast}
cues = []
SH = []


def pose(who, at, pos, yaw=0, **kw):
    k = {"at": at, "pos": list(pos), "yaw": yaw, "blend": 0.0, "blink": False}
    k.update(kw)
    acting[who].append(k)


def hide(who, at):
    acting[who].append({"at": at, "hidden": True})


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def shot(at, camera, name, step=2, hand=0.0002):
    SH.append((at, camera, step, hand, name))


def mv(p0, t0, l0, p1=None, t1=None, l1=None):
    return [[0, list(p0), list(t0), l0], [1, list(p1), list(t1 if t1 is not None else t0), l1 or l0]]


def near(tgt, d, lens, az=0.0, el=0.0, push=0.08, dx=0.0, dz=0.0):
    """A camera d metres from tgt at azimuth az (0 = south of it, looking +y) and elevation el, pushing in by `push`
    while it slides a little round the target."""
    def at(dd, a):
        a *= D2R
        e = el * D2R
        return [tgt[0] + dd * math.sin(a) * math.cos(e) + dx, tgt[1] - dd * math.cos(a) * math.cos(e),
                tgt[2] + dd * math.sin(e) + dz]
    return mv(at(d, az), tgt, lens, at(d * (1 - push), az + 2.5), tgt, lens)


# ---------------------------------------------------------------------------------------------- the cast's marks
cue(0, "h1", v=5.0)
cue(0, "tag2", on=0.0, v=0.0)
cue(0, "mine", on=1.0)
cue(0, "win", on=0.0)
cue(0, "shrink", k=0.0)
cue(0, "arrows", n=0.0)
cue(0, "nudge", k=0.0)
cue(0, "bike", on=0.0)
cue(0, "slap", u=1.0)
cue(0, "winpos", dx=0.0, dy=0.0)
cue(0, "maecards", on=1.0)
cue(0, "capmove", dx=0.0, dy=0.0)
cue(0, "sit", who="me", on=True)

MAEP = [MX, MY, T]
pose("mae", 0, MAEP, 0, arms=[0, 0], expr="warm", head=[0, 0])
pose("me", 0, [HX, HY, 0.0], 0, arms=[62, 62], expr="neutral", head=[0, 3], hidden=True)
pose("neighbor", 0, [G.NEIGH[0], G.NEIGH[1], 0.0], 0, arms=[0, 0], expr="smile", hidden=True)


def me_on(at, expr, **kw):
    pose("me", at, [HX, HY, 0.0], 0, arms=[62, 62], expr=expr, hidden=False, **kw)


def me_off(at):
    acting["me"].append({"at": at, "hidden": True})


def mae(at, expr, **kw):
    acting["mae"].append({"at": at, "pos": MAEP, "expr": expr, **kw})


def SIDE(d, lens, push=0.04, x=0.28):
    """Both of them, the camera at the stripe's height so depth makes no difference to the stripe against her head."""
    return mv([x, MY - d, T + 0.13], [x, MY, T + 0.071], lens, [x, MY - d * (1 - push), T + 0.13], [x, MY, T + 0.071], lens)


# MAE focus helpers
def face(d, lens=85, az=0.0, el=0.0, push=0.08, f=1.0, dx=0.0, dz=0.0):
    tgt = (HEAD[0], HEAD[1], T + G.MAE_EYE * f)
    return near(tgt, d, lens, az=az, el=el, push=push, dx=dx, dz=dz)


# ===== 01 the rule (L01, L02): Mae's face at her eye level, a mug rim soft behind her
shot(0, face(0.46, 85, az=-6, push=0.06, f=0.93), "S01a")                                         # sly, the first frame
mae("L01.1", "warm", head=[0, -6], blend=0.4)
mae("L01.2", "warm", head=[0, 3], blend=0.3)
shot("L01.2", face(0.5, 85, az=-4, push=0.07), "S01b")                                   # punch in on INCH
mae("L02", "warm")
mae("L02.1", "warm", head=[0, 7], blend=0.4)
shot("L02", face(0.66, 85, az=6, push=0.07), "S02a")
cue("L02.2", "h1", v=5.0)
shot("L02.2", SIDE(0.47, 40), "S02b")     # scale shot 1: she and the whole striped mug side by side

# ===== 02 the rule at work (L03 to L06)
cue("L03", "bike", on=1.0)
acting["neighbor"].append({"at": "L03", "pos": [G.NEIGH[0], G.NEIGH[1], 0.0], "yaw": 0, "hidden": False, "expr": "smile", "arms": [0, 0],
                           "side": [86, 150], "blink": False})
for i in range(6):
    acting["neighbor"].append({"at": f"L03+{0.15 + i * 0.2:.2f}", "side": [86, 164 if i % 2 == 0 else 138], "blend": 0.12})
nz = 1.45
shot("L03", mv([G.NEIGH[0] - 0.1, 0.6, 1.4], [G.NEIGH[0], G.NEIGH[1], nz], 38, [G.NEIGH[0] - 0.05, 0.9, 1.4], [G.NEIGH[0], G.NEIGH[1], nz], 38), "S03")
mae("L03.2", "warm", head=[0, 4])
cue("L03.2", "bike", on=0.0)
shot("L03.2", face(0.66, 85, az=-5, push=0.06), "S03b")
hide("neighbor", "L03.2")
# L04: me across the table, cards fanned flat in front of me
me_on("L04", "neutral")
shot("L04", mv([0.5, -1.7, 1.62], [0.02, 0.9, 1.33], 38, [0.4, -1.5, 1.6], [0.02, 0.9, 1.33], 38), "S04")
me_off("L04.1")
mae("L04.1", "warm")
shot("L04.1", face(0.64, 85, az=4, push=0.07), "S04m")
shot("L04.2", near((0.0, 0.52, T + 0.02), 0.5, 40, az=-14, el=24, push=0.1), "S04b")      # my fanned cards, close
mae("L04.3", "warm")
mae("L04.4", "warm", head=[0, 7], blend=0.4)
shot("L04.3", face(0.66, 85, az=-3, push=0.07), "S04n")
# L05: the score pad, then my face
shot("L05", near((G.PAD[0], G.PAD[1] + 0.02, T + 0.02), 0.55, 40, az=0, el=52, push=0.08), "S05a")
me_on("L05.2", "sad-smile")
shot("L05.2", mv([0.5, -1.7, 1.75], [HX, HY, 1.42], 42, [0.4, -1.55, 1.72], [HX, HY, 1.42], 42), "S05b")
# L06: the calendar glyph, three arrows landing
me_off("L06")
mae("L06", "warm")
mae("L06.1", "warm", head=[0, 8], blend=0.4)
shot("L06", face(0.62, 85, az=-5, push=0.07), "S06a")
cue("L06.2", "arrows", n=1.0)
cue("L06.2+0.35", "arrows", n=2.0)
cue("L06.2+0.7", "arrows", n=3.0)
shot("L06.2", mv([G.CAL[0] + 0.02, 0.4, 1.27], [G.CAL[0], 2.55, 1.27], 35, [G.CAL[0] + 0.02, 0.6, 1.27], [G.CAL[0], 2.55, 1.27], 35), "S06b")

# ===== 03 the scare (L07 to L09)
mae("L07", "warm", head=[0, 0])
REV_T = (0.285, MY - 0.10, T + 0.07)
shot("L07", near(REV_T, 0.47, 43, az=0, el=18, push=0.04), "S07")                 # her cards at her feet, the mug beside her
cue("L07+0.2", "nudge", k=1.0, dur=0.6)
mae("L07.3", "warm", head=[0, 0])
shot("L07.3", face(0.5, 85, az=-3, push=0.1), "S07b")                                      # looks up into the lens
mae("L08", "warm")
acting["mae"].append({"from": "L08.1", "to": "L08>", "mouth": [0.35, 0.35], "flap": True})
shot("L08", face(0.42, 85, az=3, push=0.08, f=0.92), "S08")                                         # her face half the frame
cue("L09", "shrink", k=1.0, dur=0.8)
cue("L09.1", "h1", v=4.0)
mae("L09", "warm")
shot("L09", SIDE(0.47, 45, x=0.286), "S09")      # scale shot 2

# ===== 04 the reveal (L10 to L13)
me_on("L10", "wide")
shot("L10", mv([0.4, -1.7, 1.75], [HX, HY, 1.42], 42, [0.35, -1.5, 1.72], [HX, HY, 1.42], 42), "S10")
acting["me"].append({"at": "L10.1", "pos": [HX, HY, 0.0], "expr": "wide", "arms": [62, 62], "head": [0, -4], "blend": 0.4})
me_off("L11")
mae("L11", "warm")
mae("L11+0.35", "warm", head=[0, 9], blend=0.35)         # a small tilt of the head as the fan is shown
mae("L11+0.8", "warm", head=[0, -3], blend=0.35)
shot("L11", near((0.28, MY - 0.10, T + 0.06), 0.66, 36, az=0, el=34, push=0.03), "S11a")                       # the wide: Mae, the whole mug, her fanned cards
shot("L11.1", face(0.37, 45, az=0, el=12, push=0.03, f=0.55), "S11b")                      # on "was a GIN": her warm face, the flat fan beside her
mae("L12", "warm", yaw=0)
mae("L12.1", "warm", head=[0, -8], blend=0.4)
shot("L12", face(0.6, 85, az=5, push=0.07, f=0.8), "S12")
mae("L13", "warm")
shot("L13", face(0.46, 85, az=-4, push=0.08, f=0.8), "S13")
mae("L13.1", "warm", head=[0, 18], blend=0.5)          # a little bow of the head
mae("L13.2", "warm", head=[0, 2], blend=0.4)
acting["mae"].append({"at": "L14", "pos": MAEP, "hidden": True, "blend": 0.0})          # stay put until the cut (else she walks toward her next mark during S13)

# ===== 05 the turn (L14 to L18)
cue("L14", "mine", on=0.0)
cue("L14", "win", on=1.0)
me_on("L14", "smile")
shot("L14", mv([0.45, -1.65, 1.62], [0.02, 0.9, 1.33], 38, [0.35, -1.5, 1.6], [0.02, 0.9, 1.33], 38), "S14")
me_off("L15")
SX, SY = 0.46, -0.27      # where she stands for the slap: near the table's lower-right corner
acting["mae"].append({"at": "L14>", "pos": [SX, SY, T], "yaw": 0, "hidden": True, "blend": 0.0})                                       # she steps out of the cut, then stands near the corner for the slap
acting["mae"].append({"at": "L15", "pos": [SX, SY, T], "yaw": 0, "hidden": False, "expr": "wide", "arms": [0, 0], "head": [0, 0]})
cue("L15", "winpos", dx=0.40, dy=-0.74)
cue("L15", "maecards", on=0.0)
cue("L15", "slap", u=0.0)
cue("L15+0.05", "slap", u=1.0, dur=0.4)
S15_T = (0.435, -0.36, T + 0.058)
shot("L15", near(S15_T, 0.31, 40, az=0, el=20, push=0.03), "S15")
acting["mae"].append({"at": "L16", "pos": [SX, SY, T], "yaw": 0, "hidden": True})
cue("L16", "winpos", dx=0.0, dy=0.0)
cue("L16", "maecards", on=1.0)
me_on("L16", "sad-smile")
shot("L16", mv([0.45, -1.65, 1.75], [HX, HY, 1.4], 42, [0.35, -1.5, 1.72], [HX, HY, 1.4], 42), "S16")
acting["me"].append({"from": "L16.3", "to": "L16>", "mouth": [0.4, 0.4], "flap": True})
cue("L17", "tag2", on=1.0, v=0.0)
cue("L17.2", "tag2", v=1.0)
acting["me"].append({"at": "L17", "pos": [HX, HY, 0.0], "expr": "worried", "arms": [62, 62]})
acting["me"].append({"at": "L17.2", "pos": [HX, HY - 0.0, -0.05], "blend": 0.5})     # an inch lower in frame
shot("L17", mv([0.4, -1.6, 1.74], [HX, HY, 1.4], 42, [0.33, -1.45, 1.7], [HX, HY, 1.4], 42), "S17")
me_off("L18")
acting["mae"].append({"at": "L18", "pos": MAEP, "expr": "warm", "head": [0, 0], "hidden": False})
shot("L18", face(0.40, 85, az=-6, push=0.05, f=0.74), "S18")
acting["mae"].append({"at": "L18.1", "pos": MAEP, "expr": "warm", "head": [0, 7], "blend": 0.4})

# ---------------------------------------------------------------------------------------------- finish
shots, names = [], {}
for i, (at, camera, step, hand, nm) in enumerate(SH):
    s = {"id": nm, "cam": camera, "step": step, "hand": hand}
    if i:
        s["at"] = at
    shots.append(s)
    names[nm] = nm

sfx = [
    {"at": "L01.2", "kind": "knock", "db": -12, "pattern": [0.0], "tone": "soft"},        # the soft wooden tock on INCH
    {"at": "L04.1", "kind": "click", "db": -22},
    {"at": "L09.1", "kind": "ding", "db": -18, "dur": 0.7, "pitch": 1900, "fall": 0.7, "lp": 3600},    # the soft slide down an inch
    {"at": "L08.1", "kind": "sting", "db": -14},                                            # the "dun dun" on SORRY
    {"at": "L15+0.42", "kind": "thud", "db": -16, "dur": 0.4},                                 # cards slapping on the cloth
    {"at": "L16.3", "kind": "sting", "db": -14},
    {"at": "L17.2", "kind": "ding", "db": -18, "dur": 0.7, "pitch": 1900, "fall": 0.7, "lp": 3600},   # the same slide, my inch
    {"at": "L18>", "kind": "ding", "db": -14, "dur": 0.3, "pitch": 1300, "fall": 0.6, "lp": 3200},     # her tiny sip, audible, a short pitch fall
]
sfx = [s for s in sfx if s["at"] != "L04.1"]
music = {
    "root": 53, "mode": "major", "bpm": 112, "seed": 123,
    "sections": [
        {"at": 0, "voices": ["pluck", "pulse", "pad"], "energy": 0.35},
    ],
}
music["sections"][0]["voices"] = ["piano", "pulse", "pad"]
sound = {
    "floor": "wood", "steps_db": -26,
    "ambience": [{"kind": "room", "from": 0, "to": "end", "lufs": -44}],
    "sfx": sfx,
    "rev": REV,
}
polish = {"emph": ["L01.2", "L06.2", "L08.1", "L11.1", "L16.3", "L18.2"],
          "reveal": ["L11"], "camera": False, "idle_scale": 0.25, "hold": ["S11a", "S11b"],
          "key_hits": "all", "whoosh_cuts": False}
story = {
    "slug": "ep123-sorry-shrink",
    "title": "Every SORRY Here Costs An Inch ☕",
    "made_for_kids": False,
    "premise": ("In a town where every sorry shrinks you an inch, my aunt Mae is the size of a mug, and everyone says she "
                "is the politest woman alive. Every Sunday I play her at cards on her sun porch, and I have lost sixty "
                "games in a row."),
    "twist": ("She is not polite, she is the town's unbeaten card player: every inch she lost went on the sorry she says "
              "each time she lays down a winning hand. When I finally beat her I say sorry out of habit, and I shrink an inch."),
    "world": ("A sunny glassed-in porch on a pale blue house: white wicker, hanging ferns, a square card table with a "
              "yellow-and-white checked cloth, a white mug with a red stripe, a plate of shortbread, a score pad, a wall "
              "calendar, a sunny street outside."),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff7f6b",
    "gap": 0.15,
    "tail": 0,
    "fade_in": False,
    "fade_out": False,
    "rev": REV,
    "look": {"style": "closer", "fog": "#dff0ff", "fog_density": 0.002, "fog_start": 60.0, "sky": "#8fd0ff",
             "sky_strength": 1.0, "exposure": 0.25, "flash_safe": True, "polish": polish},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.08, "contrast": 1.04,
              "vignette": 0.15, "bloom": 0.1, "grain": 0.006},
    "phonemes": {"Mae": "mˈA"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": music,
    "sound": sound,
    "set_moves": ["S15", "S06b"],
}
story["framing_ok"] = ["S18", "S10", "S15"]   # the tool places Mae at full height; after the shrink her head sits lower, clear of the tag (checked in the still)
story["frames_ok"] = ["S17", "S07"]   # the second meter line (my height) appears with this shot, on purpose
story["asr_forgive"] = ["sun", "looked", "mae"]
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots, {len(cues)} cues)")
