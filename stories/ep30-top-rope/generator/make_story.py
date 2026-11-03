"""Writes ../story.json for ep30 "In This Town, When You Fall, Someone Goes UP" (script.md, redo 2026-11-02).

Run from anywhere: python stories/ep30-top-rope/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (lamps, bench, rings, sitting, the rope), the effects, the score and the sound.
Places are set.py's: the wall is the plane y = 0 (the room is at -y, so the camera mostly looks toward +y), the mats
are z 0.3, the top hold is at z 8.35, the roof (the "ceiling") at z 9.8, the anchor at x -0.45.
A "lift" (script.md) is an acting z key: the person rises straight up with their arms out, and a ring cue lights the
floor under them.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# Whisper-safe readings (see script: mishear watch)
TEMPO = {"L52": 0.92, "L02": 0.95, "L42": 0.95, "L14": 0.82, "L12": 0.76, "L36": 0.85, "L44": 0.95}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]

FACE = {"eyes": "round", "brows": True, "ink": "#161012"}
cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#b9622f", "pattern": "stripes", "pattern_c": "#e3d6b2",
           "collar": "#a2542a", "pants": "#4a5560", "shoes": "#e8dcc0", "sleeves": "short", "hair": "cap",
           "hair_c": "#2a1c14", "hat": "none", "face": FACE},
    "mum": {"age": "adult", "skin": "#c68f6e", "shirt": "#2f5a3e", "pattern": "solid", "collar": "#294f37",
            "pants": "#6a6e72", "shoes": "#2a2a2a", "sleeves": "long", "hair": "bun", "hair_c": "#a9acb2", "hat": "none",
            "face": FACE, "ceil_face": {"eyes": "hollow", "eye_scale": 0.7, "brows": True, "ink": "#161012", "glow": "#fffdf0"}},
    "date_guy": {"age": "adult", "skin": "#e0b48c", "shirt": "#d9a82a", "pattern": "solid", "collar": "#c4961f",
                 "pants": "#233a63", "shoes": "#d8d2c4", "sleeves": "short", "hair": "swoop", "hair_c": "#15110f",
                 "hat": "none", "face": FACE},
    "date": {"age": "adult", "skin": "#f0c8a4", "shirt": "#1f8a86", "pattern": "solid", "collar": "#1a7773",
             "pants": "#1b1b1f", "shoes": "#e8e0d0", "sleeves": "long", "hair": "long", "hair_c": "#8a3b1c", "hat": "none",
             "face": {**FACE, "eyes": "lashes"}},
    "his_mum": {"age": "adult", "skin": "#d9a98a", "shirt": "#e8dcc4", "pattern": "solid", "collar": "#6e2f4f",
                "pants": "#4b3a52", "shoes": "#3a2a2a", "sleeves": "long", "hair": "cap", "hair_c": "#a3a3a8", "hat": "none",
                "extras": ["glasses"], "extra_c": "#2a2a2a", "face": FACE},
}


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return c([0, list(loc), list(tgt), lens])


def move(a, b):
    return c([0, list(a[0]), list(a[1]), a[2]], [1, list(b[0]), list(b[1]), b[2]])


# ---------------------------------------------------------------------------------------------------- shots
SH = []


def shot(sid, at, cam, step=2, **kw):
    SH.append({"id": sid, "at": at, "cam": cam, "step": step, **kw})


shot("S01", 0, move(((0.4, -5.2, 1.9), (0.05, -0.9, 1.4), 26), ((0.4, -4.9, 1.9), (0.05, -0.9, 1.4), 27)))
shot("S01b", "L01+1.2", still((0.45, -4.8, 1.5), (0.55, -0.7, 1.15), 30))
shot("S02", "L02", still((-0.2, -3.6, 1.5), (-0.5, -0.7, 1.4), 32))
shot("S03", "L03", still((0.0, -4.0, 1.7), (0.0, -0.7, 1.6), 32))
shot("S04", "L04", still((-2.4, -10.2, 2.0), (-3.8, -7.0, 2.1), 26))
shot("S05", "L05", still((2.2, -8.0, 1.5), (4.05, -4.6, 1.35), 34))
shot("S06", "L06", still((3.3, -7.0, 1.4), (4.1, -4.6, 1.3), 38))
shot("S07", "L07-0.35", still((2.8, -5.4, 1.1), (3.5, -2.2, 0.9), 28))
shot("S07b", "L07.1", still((3.4, -5.8, 1.7), (2.5, -2.0, 1.8), 28))
shot("S08", "L08", still((4.8, -6.0, 1.7), (3.0, -2.2, 1.9), 28))
shot("S09", "L09", still((0.8, -3.2, 1.6), (0.0, -0.3, 1.6), 30))
shot("S10", "L10", still((1.5, -3.3, 1.6), (0.0, -0.3, 1.8), 30))
#shot("S10b", "L10+1.4", still((1.2, -3.0, 1.5), (0.0, -0.3, 1.5), 40))
#shot("S11", "L11", still((3.3, -7.0, 1.4), (4.1, -4.6, 1.2), 38))
shot("S12", "L12", still((-1.9, -1.9, 3.4), (0.0, -0.3, 3.3), 34))
shot("S13", "L13", still((0.9, -1.6, 7.2), (-0.2, -0.2, 8.7), 26))
shot("S14b", "L14", still((-0.45, -2.9, 8.58), (-0.45, 0, 8.58), 34))
shot("S15", "L15", still((-0.2, -0.6, 7.9), (0.15, -2.55, 8.4), 20))
shot("S16", "L16", still((2.8, -2.45, 8.3), (0.15, -2.55, 9.2), 24))
shot("S17", "L17", still((2.0, -2.45, 7.6), (0.15, -2.6, 7.9), 42))
shot("S18", "L18", still((0.2, -1.9, 8.0), (0.0, -0.3, 8.0), 38))
shot("S19", "L19", still((-4.5, -8.5, 1.6), (-0.8, -2.0, 6.5), 22))
shot("S20", "L20", still((0.0, -1.2, 1.6), (0.2, -2.0, 9.6), 22))
shot("S21", "L21", still((1.2, -5.4, 1.3), (0.2, -2.55, 1.3), 34))
shot("S22", "L22", still((0.9, -4.2, 2.8), (0.15, -2.6, 2.2), 45))
shot("S23", "L23", still((3.0, -2.0, 7.2), (0.0, -0.3, 7.2), 28))
shot("S24", "L24", still((3.0, -1.75, 8.3), (0.15, -1.75, 9.0), 24))
shot("S25", "L25", still((1.6, -0.7, 8.0), (0.15, -1.75, 8.9), 26))
shot("S26", "L26", c([0, [0.0, -0.6, 8.2], [0.15, -1.75, 8.5], 36, 180]))
shot("S27", "L27", still((0.6, -5.3, 1.7), (0.8, -2.8, 1.5), 28))
shot("S28", "L28", still((0.3, -4.8, 1.8), (0.3, -2.8, 1.8), 40))
shot("S28b", "L28.3", still((1.8, -5.0, 2.0), (0.8, -2.7, 1.6), 28))
shot("S29", "L29", still((2.4, -6.0, 2.2), (0.15, -1.4, 1.0), 24))
shot("S30", "L30", still((-3.0, -2.2, 7.4), (0.0, -0.3, 7.3), 28))
shot("S31", "L31", still((0.0, -0.4, 8.1), (0.15, -1.05, 8.3), 24))
shot("S32", "L32", still((1.3, -1.5, 8.1), (0.0, -0.3, 8.0), 40))
shot("S33", "L33", still((0.9, -1.6, 7.2), (-0.2, -0.2, 8.7), 26))
shot("S33b", "L33.3", still((-3.0, -9.0, 0.8), (0.0, -1.0, 6.0), 20))
shot("S33c", "P01", still((4.0, -10.0, 2.0), (0.0, -3.0, 6.0), 20))
shot("S34", "L34", still((3.0, -3.0, 7.4), (-1.2, -0.3, 7.6), 30))
shot("S35", "L35", still((-2.4, -2.6, 7.0), (0.0, -0.3, 7.0), 28))
shot("S36", "L36", still((1.1, -0.6, 8.3), (0.1, -0.55, 8.2), 40))
shot("S37", "L37", still((-0.35, -2.0, 8.1), (0.3, -0.55, 8.1), 24))
shot("S38", "L38", c([0, [-0.3, -0.6, 8.2], [0.55, -0.55, 8.5], 22, 180]))
shot("S39", "L39", still((0.0, -3.0, 7.8), (0.0, -0.5, 7.6), 38))
shot("S40", "L40", still((3.4, -8.0, 0.9), (-0.1, -1.2, 0.9), 24))
shot("S41", "L41", still((0.2, -4.4, 1.2), (0.55, -0.55, 1.15), 38))
shot("S42", "L42", still((0.6, -3.4, 0.55), (0.55, -1.2, 0.6), 32))
#shot("S43", "L43", still((-0.6, -2.6, 1.8), (-0.6, -1.7, 1.8), 40))
shot("S44", "L44", still((0.6, -3.4, 4.6), (0.55, -0.7, 9.8), 36))
shot("S45", "L45", still((0.2, -3.4, 1.4), (0.05, -0.6, 1.3), 26))
shot("S46", "L46", still((0.6, -3.6, 4.4), (0.5, -0.9, 9.8), 30))
shot("S47", "L47", still((0.5, -2.6, 1.8), (0.55, -0.55, 1.7), 44))
shot("S48", "L48", c([0, [-0.3, -0.6, 8.2], [0.55, -0.55, 8.5], 22, 180]))
#shot("S48b", "L48.1+0.4", still((0.5, -2.6, 1.8), (0.55, -0.55, 1.7), 44))
shot("S49", "L49", still((0.9, -3.6, 1.7), (-0.05, -0.6, 1.35), 34))
shot("S50", "L50", still((2.4, -1.6, 7.6), (-0.4, -0.5, 7.5), 30))
shot("S51", "L51", still((-0.5, -7.8, 3.8), (-0.45, -0.5, 4.8), 16))
shot("S52", "L52", c([0, [0.6, -1.7, 1.6], [0, 0, 1.5], 40]), follow="mum")
shot("S53", "L53", still((-0.45, -6.0, 4.6), (-0.45, -0.6, 4.6), 30), step=1)
shot("S54", "L54", still((-0.45, -3.0, 6.0), (-0.05, -0.6, 5.95), 44), step=1)
shot("S55", "L55", still((-3.5, -8.0, 0.9), (-0.45, -0.6, 3.8), 22), step=1)
shot("S55b", "L55+1.4", still((-0.45, -2.6, 5.8), (-0.45, -0.6, 5.9), 34), step=1)
shot("S56", "L56", still((-0.5, -5.5, 0.6), (0.2, -1.5, 9.8), 22), step=1)

# the lens is a long one on this engine (the width in view is about 8 x distance / lens), so the wide and medium shots
# are halved; the close ones on the ceiling figure and the lore plant are already set for their framing
KEEP = {"S14b", "S15", "S16", "S17", "S18", "S22", "S24", "S25", "S26", "S31", "S32", "S36", "S37", "S38", "S48", "S20",
        "S56", "S44", "S46"}
for s_ in SH:
    if s_["id"] not in KEEP:
        for k_ in s_["cam"]:
            k_[3] = round(k_[3] * 0.5, 1)

# ---------------------------------------------------------------------------------------------------- acting
acting = {}
OFF = re.compile(r"^(?P<base>[LP]\d+(?:\.\d+)?>?)(?P<off>[+-]\d+(?:\.\d+)?)?$")


def minus(ref, d=0.03):
    m = OFF.match(ref)
    base, off = m.group("base"), float(m.group("off") or 0)
    off -= d
    return f"{base}{off:+.2f}"


def seq(who, items):
    """items: (ref, dict), in time order. A dict with 'pos' holds that spot until just before the next item that
    has a different pos (no drift across a cut); 'glide': True lets it walk, lower or rise to the next pos instead."""
    out = []
    for i, (ref, kw) in enumerate(items):
        kw = dict(kw)
        glide = kw.pop("glide", False)
        kw.setdefault("blend", 0.06)
        out.append({"at": ref, **kw})
        nxt = next(((r2, k2) for r2, k2 in items[i + 1:] if "pos" in k2), None)
        if "pos" in kw and nxt and nxt[1]["pos"] != kw["pos"] and not glide:
            out.append({"at": minus(nxt[0]), "pos": kw["pos"], "blend": 0.06})
    acting[who] = out


UP = [165, 165]
seat = {"home": [4.05, -4.6, -0.1], "t1": [0.15, -2.55, 0.2], "t2": [0.15, -1.75, 0.2], "t3": [0.15, -1.05, 0.2],
        "lip": [0.55, -0.55, 0.2]}
ST = {"sit": True}
START = [-0.05, -0.6, 0.3]       # where Mum stands to hold the rope, and where the last ring glows

me = [
    ("L01", dict(hidden=True, pos=[0, -0.3, 0.3])),
    ("L07.1", dict(hidden=False, pos=[2.5, -2.0, 0.3], yaw=90, arms=[0, 0], side=[0, 0], expr="wide", glide=True)),
    ("L07.1+0.55", dict(pos=[2.5, -2.0, 1.3], side=[65, 65], expr="laugh")),
    ("L09", dict(pos=[0, -0.3, 0.3], yaw=180, arms=[165, 150], side=[0, 0], expr="neutral", head=[0, 0])),
    ("L10", dict(pos=[0, -0.3, 1.6], arms=UP, expr="worried", glide=True)),
    ("L10+0.6", dict(pos=[0, -0.3, 1.6], glide=True)),
    ("L10+1.0", dict(pos=[0, -0.3, 1.1])),
    ("L10+1.4", dict(yaw=90, head=[-80, 0], expr="worried")),
    ("L11", dict(hidden=True)),
    ("L12", dict(hidden=False, pos=[0, -0.3, 3.2], yaw=180, arms=[110, 110], head=[0, 0], expr="wide")),
    ("L13", dict(pos=[0, -0.3, 6.4], arms=UP, expr="worried")),
    ("L13.2", dict(arms=[125, 125])),
    ("L14", dict(pos=[0, -0.3, 6.0], arms=UP, expr="neutral")),
    ("L14.1", dict(head=[0, -35])),
    ("L18", dict(yaw=90, head=[0, -40], expr="worried")),
    ("L19", dict(pos=[0, -0.3, 6.0], yaw=180, head=[0, 0], glide=True)),
    ("L20+0.2", dict(pos=[0, -0.3, 0.3], arms=[0, 0])),
    ("L23", dict(pos=[0, -0.3, 6.4], arms=UP, expr="worried", glide=True)),
    ("L23+0.6", dict(pos=[0, -0.3, 6.4], glide=True)),
    ("L23+1.0", dict(pos=[0, -0.3, 6.0])),
    ("L27", dict(pos=[0.3, -2.8, 0.3], yaw=90, arms=[30, 30], expr="neutral", head=[0, 0])),
    ("L28", dict(yaw=0)),
    ("L28+0.1", dict(head=[-22, 0])),
    ("L28+0.3", dict(head=[22, 0])),
    ("L28+0.5", dict(head=[0, 0])),
    ("L28.3", dict(yaw=180, blend=0.5)),
    ("L29", dict(pos=[0, -0.4, 0.3], yaw=180, arms=[0, 0])),
    ("L30", dict(pos=[0, -0.3, 6.4], arms=UP, glide=True)),
    ("L30+0.7", dict(pos=[0, -0.3, 6.4], glide=True)),
    ("L30+1.1", dict(pos=[0, -0.3, 6.0])),
    ("L31", dict(yaw=90, head=[0, -30], expr="worried")),
    ("L33", dict(pos=[0.1, -0.55, 6.6], yaw=180, head=[0, 0], arms=UP, expr="worried")),
    ("L35", dict(pos=[0.1, -0.55, 6.6], glide=True)),
    ("L35+0.2", dict(pos=[0.1, -0.55, 6.1], glide=True)),
    ("L35+0.5", dict(pos=[0.1, -0.55, 6.6])),
    ("L36", dict(pos=[-0.15, -0.55, 6.6], yaw=90, arms=[25, 25], expr="scared")),
    ("L38", dict(hidden=True)),
    ("L39", dict(hidden=False, pos=[0.1, -0.55, 6.6], yaw=0, arms=[25, 25], expr="shut", glide=True)),
    ("L40.2", dict(pos=[-0.6, -0.55, 0.3], arms=[0, 0], expr="worried")),
    ("L43", dict(pos=[-0.6, -1.7, 0.3], yaw=0, expr="worried", head=[0, -50])),
    ("L44", dict(head=[0, -55])),
    ("L45", dict(pos=[-0.45, -0.75, 0.3], yaw=90, head=[0, 0], expr="soft")),
    ("L46", dict(hidden=True)),
    ("L49", dict(hidden=False, pos=[-0.85, -0.6, 6.4], yaw=90, arms=UP, side=[0, 0], expr="neutral", head=[0, 0])),
    ("L50+0.7", dict(arms=[35, 35])),
    ("L51", dict(pos=[-0.85, -0.6, 6.4], arms=[25, 25], side=[40, 40], expr="wide", glide=True)),
    ("L53", dict(pos=[-0.85, -0.6, 4.4], yaw=60, arms=[0, 0], side=[40, 40], expr="smile")),
    ("L55", dict(expr="laugh")),
    ("L56", dict(hidden=True)),
]
seq("me", me)

mum = [
    ("L01", dict(hidden=True, pos=seat["home"])),
    ("L05", dict(hidden=False, pos=seat["home"], yaw=0, arms=[10, 150], side=[0, 0], head=[0, 0], expr="smile")),
    ("L06", dict(arms=[35, 35], head=[0, 35], expr="neutral")),
    ("L07-0.35", dict(pos=[3.65, -2.2, 0], yaw=-90, lean=28, arms=[60, 60], head=[0, 0], expr="wide")),
    ("L08", dict(lean=0, arms=[0, 0], head=[0, -30], expr="laugh")),
    ("L09", dict(pos=seat["home"], yaw=0, head=[0, 0], expr="smile")),
    ("L11", dict(arms=[45, 30], head=[0, 35], expr="neutral")),
    ("L12", dict(hidden=True)),
    ("L21", dict(hidden=False, pos=seat["t1"], yaw=0, arms=[50, 50], head=[0, 0], expr="smile")),
    ("L23", dict(hidden=True)),
    ("L27", dict(hidden=False, pos=[1.3, -2.8, 0.3], yaw=-90, arms=[70, 70], expr="soft")),
    ("L28.3", dict(arms=[15, 15], head=[0, 20])),
    ("L29", dict(pos=seat["t3"], yaw=0, arms=[50, 50], head=[0, 0], expr="smile")),
    ("L30", dict(hidden=True)),
    ("L40", dict(hidden=False, pos=seat["lip"], yaw=0, arms=[40, 40], expr="scared")),
    ("L45", dict(head=[-60, 0], expr="soft")),
    ("L47", dict(head=[0, 0], expr="soft")),
    ("L48.1+0.4", dict(expr="smile")),
    ("L49", dict(pos=START, yaw=0, arms=[55, 55], expr="soft")),
    ("L51", dict(pos=START, arms=[0, 0], side=[35, 35], expr="shut", glide=True)),
    ("L52.1", dict(expr="wide")),
    ("L53", dict(pos=[-0.05, -0.6, 4.4], yaw=-60, arms=[0, 0], side=[35, 35], expr="smile")),
    ("L55", dict(expr="laugh")),
    ("L56", dict(hidden=True)),
]
seq("mum", mum)

seq("date_guy", [
    ("L01", dict(pos=[-0.5, -0.7, 1.6], yaw=0, arms=[150, 150], side=[0, 0], expr="wide", glide=True)),
    ("L01+0.9", dict(pos=[-0.5, -0.7, 1.6], glide=True)),
    ("L02+0.55", dict(pos=[-0.5, -0.7, 0.3], yaw=50, arms=[0, 0], head=[0, -30], expr="laugh")),
    ("L03", dict(head=[0, 0], expr="grin")),
    ("L04", dict(hidden=True)),
])
seq("date", [
    ("L01", dict(pos=[0.55, -0.7, 0.3], yaw=-50, arms=[0, 0], side=[0, 0], expr="laugh", glide=True)),
    ("L01+0.2", dict(pos=[0.55, -0.7, 0.3], glide=True)),
    ("L01+0.7", dict(pos=[0.55, -0.7, 1.4], side=[65, 65])),
    ("L03", dict(pos=[0.55, -0.7, 1.3], glide=True)),
    ("L03+0.9", dict(pos=[0.55, -0.7, 0.3], side=[0, 0], expr="grin")),
    ("L04", dict(hidden=True)),
])
seq("his_mum", [
    ("L01", dict(hidden=True, pos=[-3.8, -7.0, -0.1], yaw=0, arms=[0, 0], side=[0, 0], expr="neutral")),
    ("L04", dict(hidden=False, pos=[-3.8, -7.0, -0.1], glide=True)),
    ("L04+0.3", dict(pos=[-3.8, -7.0, -0.1], glide=True)),
    ("L04+0.9", dict(pos=[-3.8, -7.0, 0.9], side=[55, 55], expr="scared")),
    ("L05", dict(hidden=True)),
])

# ---------------------------------------------------------------------------------------------------- cues
cues = [
    {"at": 0, "name": "warm", "to": 1.0, "dur": 0.01},
    {"at": "L33.3", "name": "lamps", "to": 0.15, "dur": 0.7},      # the lamps go out: a slow ramp, never black
    {"at": "L40.2", "name": "lamps", "to": 1.0, "dur": 0.6},       # and come back as my feet touch the mat
    {"at": "L33.3", "name": "flood", "to": 0.35, "dur": 0.7},
    {"at": "L40.2", "name": "flood", "to": 1.0, "dur": 0.6},
    {"at": 0, "name": "rope", "mode": "me"},
    {"at": "L27", "name": "rope", "mode": "offer"},
    {"at": "L29", "name": "rope", "mode": "me"},
    {"at": "L49", "name": "rope", "mode": "mum"},
    {"at": 0, "name": "bench", "spot": "home"},
    {"at": 0, "name": "sit", "who": "his_mum", "on": True},
    {"at": 0, "name": "sit", "who": "mum", "on": True},
    {"at": "L07", "name": "sit", "who": "mum", "on": False},
    {"at": "L09", "name": "sit", "who": "mum", "on": True},
    {"at": "L27", "name": "sit", "who": "mum", "on": False},
    {"at": "L29", "name": "sit", "who": "mum", "on": True},
    {"at": "L49", "name": "sit", "who": "mum", "on": False},
    # the ceiling
    {"at": "L15", "name": "head", "pose": "t1"},
    {"at": "L20", "name": "head", "hidden": True},
    {"at": "L24", "name": "head", "pose": "t2"},
    {"at": "L26", "name": "head", "pose": "t2", "expr": "angry"},
    {"at": "L27", "name": "head", "hidden": True},
    {"at": "L31", "name": "head", "pose": "t3"},
    {"at": "L33", "name": "head", "hidden": True},
    {"at": "L37", "name": "head", "pose": "lip", "yaw_head": 0.0, "expr": "angry"},
    {"at": "L39", "name": "head", "hidden": True},
    {"at": "L48", "name": "head", "pose": "lip"},
    {"at": "L49", "name": "head", "hidden": True},
    {"at": "L22", "name": "mum_dust", "hair": True, "soles": False},
    {"at": "L42", "name": "mum_dust", "hair": True, "soles": True},
    {"at": "L49", "name": "harness", "on": True},
    {"at": "L40", "name": "prints", "lip": True, "all": False},
    {"at": "L46", "name": "prints", "lip": True, "all": True},
    # the lift rings
    {"at": "L01+0.3", "name": "ring", "who": "date", "on": True},
    {"at": "L03", "name": "ring", "who": "date", "on": False},
    {"at": "L04+0.1", "name": "ring", "who": "his_mum", "on": True},
    {"at": "L04+1.0", "name": "ring", "who": "his_mum", "on": False},
    {"at": "L07.1", "name": "ring", "who": "me", "on": True},
    {"at": "L08+0.8", "name": "ring", "who": "me", "on": False},
    {"at": "L18", "name": "ring", "who": "bench", "on": True, "level": 0.5},
    {"at": "L20", "name": "ring", "who": "bench", "on": False},
    {"at": "L36", "name": "ring", "who": "bench", "on": True, "level": 0.5},
    {"at": "L40.2", "name": "ring", "who": "bench", "on": False},
    {"at": "L51-0.2", "name": "ring", "who": "mum", "on": True},
    {"at": "L56", "name": "ring", "who": "mum", "on": False},
]
# bench: Thursdays move it nearer the wall
for at, spot in (("L12", "t1"), ("L23", "t2"), ("L29", "t3"), ("L33", "lip")):
    cues.append({"at": at, "name": "bench", "spot": spot})

# per-shot lights. Mum's silhouette shots: the front lamps dead, a key from below, a cold blue rim (set.py places them)
DARK = {"lamps": 0.03, "flood": 0.1, "fill": 0.4}
looks = {}
for sid in ("S15", "S16", "S17", "S24", "S25", "S26", "S31"):
    looks[sid] = {**DARK, "ckey_g": 0.25, "crim_g": 1.5, "glow": [[0.4, -1.8, 9.0], 4.0]}
looks["S19"] = {"lamps": 0.1, "flood": 0.25, "fill": 0.6, "glow": [[0.2, -2.2, 8.6], 40.0]}
looks["S20"] = {"lamps": 0.3, "flood": 0.5, "fill": 0.8, "glow": [[0.2, -2.0, 8.6], 80.0]}
for sid in ("S36", "S37", "S38", "S48"):
    looks[sid] = {"ckey_g": 1.0, "crim_g": 1.6}
looks["S37"].update({"lamps": 0.4, "ckey_g": 0.9, "crim_g": 1.3, "cfill": 140.0, "cfill_at": [-0.2, -1.6, 7.4]})
looks["S38"].update({**DARK, "ckey_g": 0.0, "crim_g": 1.6, "cfill": 160.0, "cfill_at": [-0.45, -0.6, 7.3]})
looks["S48"].update({"ckey_g": 0.0, "crim_g": 1.6, "cfill": 160.0, "cfill_at": [-0.45, -0.6, 7.3]})
looks["S26"].update({"cfill": 90.0, "cfill_at": [0.15, -1.0, 7.3]})
looks["S44"] = {"lamps": 0.5, "flood": 0.5, "glow": [[0.55, -1.6, 8.6], 90.0]}
looks["S46"] = {"lamps": 0.5, "flood": 0.5, "glow": [[0.45, -1.6, 8.6], 80.0]}
looks["S56"] = {"lamps": 0.06, "flood": 0.15, "fill": 0.9, "glow": [[0.3, -2.6, 8.4], 110.0]}
for sid in ("S01", "S01b", "S02", "S03"):
    looks[sid] = {"lamps": 1.0, "flood": 0.8, "fill": 1.0}
looks["S04"] = {"lamps": 1.1, "flood": 0.8, "fill": 1.0}

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L01+0.3", "kind": "bell", "db": -28, "dur": 0.5},
    {"at": "L04+0.1", "kind": "bell", "db": -28, "dur": 0.5},
    {"at": "L07.1", "kind": "bell", "db": -28, "dur": 0.5},
    {"at": "L32", "kind": "whoosh", "db": -30, "dur": 0.7},
    {"at": "L32.2", "kind": "whoosh", "db": -30, "dur": 0.6},
    {"at": "L33.3", "kind": "hum_sweep", "db": -20, "dur": 0.8},
    {"at": "P01+0.15", "kind": "click", "db": -26},
    {"at": "P01+0.6", "kind": "click", "db": -26},
    {"at": "L35", "kind": "thud", "db": -24},
    {"at": "L37", "kind": "hit", "db": -8},
    {"at": "L40.2", "kind": "thud", "db": -20},
    {"at": "P02", "kind": "creak", "db": -22, "dur": 0.9},
    {"at": "L51-0.2", "kind": "bell", "db": -26, "dur": 0.6},
    {"at": "L56.1", "kind": "creak", "db": -16, "dur": 1.5},
]
story = {
    "slug": "ep30-top-rope",
    "title": "In This Town, When You Fall, Someone Goes UP",
    "made_for_kids": False,
    "premise": "In a town where your fall lifts the one who loves you most straight off the floor, I climb a wall inside an old brick mill, and every Thursday I come off the top, someone is standing upside down on the ceiling above me, one hold closer each week.",
    "twist": "The figure on the ceiling is Mum, who is scared of heights and has gone up for me every single time I fell, and at the end she holds my rope so the rule lifts her on the other end while I drop.",
    "world": "a tall old brick mill turned climbing gym: soot brick, iron lamps on chains, a grey-green wall with a roof of holds, blue crash mats, deep evening windows",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#3ee0c8",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0.25,
    "look": {"fog": "#10141c", "fog_density": 0.012, "fog_start": 6.0, "sky": "#080a10", "sky_strength": 1.0,
             "exposure": 0.6, "flash_safe": True},
    "grade": {"shadows": [-0.02, 0.0, 0.05], "highlights": [0.03, 0.01, -0.02], "saturation": 0.95, "contrast": 1.08,
              "vignette": 0.38, "bloom": 0.28, "grain": 0.013, "red_line": 0.79},
    "phonemes": {"route": "ɹˈaʊt"},
    "cast": cast,
    "looks": looks,
    "lines": lines,
    "shots": SH,
    "acting": acting,
    "cues": cues,
    "fx": [{"at": "L37", "kind": "punch", "dur": 0.35, "zoom": 1.1, "fade": 0.2},
           {"at": "L13", "kind": "dissolve", "dur": 0.3}, {"at": "L14", "kind": "dissolve", "dur": 0.3},
           {"at": "L50", "kind": "dissolve", "dur": 0.3}],
    "music": {"root": 40, "mode": "phrygian", "bpm": 74, "seed": 30,
              "sections": [
                  {"at": 0, "voices": ["pulse", "pad"], "energy": 0.3},
                  {"at": "L09", "voices": ["pulse", "pad"], "energy": 0.25},
                  {"at": "L15", "voices": ["drone", "pad", "pulse"], "energy": 0.4},
                  {"at": "L33", "voices": ["drone", "pad", "pulse"], "energy": 0.5},
                  {"at": "L45", "voices": ["drone", "pad"], "energy": 0.35},
                  {"at": "L49", "voices": ["piano", "pad"], "energy": 0.45, "mode": "major", "root": 40},
                  {"at": "L56", "voices": ["drone"], "energy": 0.3},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "end", "lufs": -33},
                  {"kind": "hum", "from": "L33.3", "to": "L40", "lufs": -40},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "L37-0.7", "to": "L37+0.1", "keep": ["hit"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(SH)} shots)")
