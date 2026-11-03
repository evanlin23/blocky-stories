"""Writes ../story.json for night-mower "His Mower Makes Grass LONGER" (revival, script.md r2).

Run from anywhere: python stories/night-mower/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots with their cameras and
who stands where in each, the tracks set.py animates (the yardstick's grass, the blinds, the vision's light), the
cups, the score and the sound. Shot ids match script.md (S01 ... S43, with letters for extra cuts).

Places (metres, the ground is z = 0; yaw 0 faces -y, 90 faces +x, 180 faces +y, -90 faces -x):
  the street: y -4 .. 4, running along x. Our side (north) has the sidewalk y 4 .. 5.2 and the yards y 5.2 .. 12.
  our yard x -15 .. -0.2, the low fence at x = 0, Mr. Odell's lawn x 0.2 .. 15 (straight stripes), his mint house
  behind it (y 12 and up), our butter-yellow house x -14 .. -4 (the bedroom upstairs at z 2.8, the porch at (-8.2, 10.8)).
  the lime yardstick at (2.75, 7.0); the mow line is x = 3.4; the coffee cart at (4.2, 4.9) facing the street.
  across the street: the south houses (front wall y = -9), the coral one at x = -6 (straight).
  the bedside clock is built at x = 130.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

LOOP = 0.25
GAP = 0.12
TEMPO = {}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]
    for ch in ln["chunks"]:
        ch[1] = ch[1].replace("Odell", "Oh-dell") if False else ch[1]

# captions run 2 or 3 words at a time: split any longer chunk, and remember where each script chunk went
def _split(n):
    return {1: [1], 2: [2], 3: [3], 4: [2, 2], 5: [3, 2], 6: [3, 3], 7: [3, 2, 2], 8: [3, 3, 2]}[n]


CHUNK_MAP = {}
for ln in lines:
    new_chunks, mp = [], []
    for cap, spk in ln["chunks"]:
        cw, sw = cap.split(), spk.split()
        assert len(cw) == len(sw), (ln["id"], cap, spk)
        mp.append(len(new_chunks))
        i = 0
        for k in _split(len(cw)):
            new_chunks.append([" ".join(cw[i:i + k]), " ".join(sw[i:i + k])])
            i += k
    ln["chunks"] = new_chunks
    CHUNK_MAP[ln["id"]] = mp

for ln in lines:
    for ch in ln["chunks"]:
        if ln["id"] == "L01":
            ch[1] = ch[1].replace("neighbor's mower", "neighbor's lawn mower")
        if ln["id"] == "L32":
            ch[1] = ch[1].replace("they're", "they are")
        if ln["id"] == "L24":
            ch[1] = ch[1].replace("eyes still", "eyes, still")
    if ln["id"] == "L24":
        ln["tempo"] = 0.95

# two pause beats (music drops) go before L20 and L25
_out = []
for ln in lines:
    if ln["id"] == "L20":
        _out.append({"id": "P01", "pause": 0.6, "chunks": [["", ""]]})
    if ln["id"] == "L25":
        _out.append({"id": "P02", "pause": 0.7, "chunks": [["", ""]]})
    _out.append(ln)
lines = _out

# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True, "ink": "#2a1810"}
cast = {
    "me": {"age": "adult", "skin": "#e0ac84", "shirt": "#1fb5a8", "pattern": "solid", "collar": "#188f85",
           "pants": "#8a8d93", "shoes": "#f4f4f4", "sleeves": "long", "hair": "cap", "hair_c": "#3b2416",
           "hat": "none", "extras": ["hooddown"], "extra_c": "#1fb5a8", "face": dict(FACE)},
    "dad": {"age": "adult", "skin": "#e8b48a", "shirt": "#d93a3a", "pattern": "plaid", "pattern_c": "#ffffff",
            "collar": "#b32d2d", "pants": "#c9b27a", "shoes": "#f4f4f4", "sleeves": "short", "hair": "cap",
            "hair_c": "#c99a52", "hat": "ballcap", "hat_c": "#3fa65a", "width": 1.05, "face": dict(FACE)},
    "dadn": {"age": "adult", "skin": "#e8b48a", "shirt": "#2a3f8f", "pattern": "solid",
             "collar": "#c4ccf0", "zip_c": "#c4ccf0", "pants": "#c9b27a", "shoes": "#f4f4f4", "sleeves": "long", "hair": "cap",
             "hair_c": "#c99a52", "hat": "none", "extras": ["coat"], "width": 1.05, "face": dict(FACE)},
    "odell": {"age": "adult", "skin": "#e8bf9a", "shirt": "#2f6b3a", "pattern": "solid", "collar": "#25552d",
              "pants": "#6b4a2e", "shoes": "#5a3a22", "sleeves": "long", "hair": "cap", "hair_c": "#f2f2ee",
              "hat": "none", "height": 0.97, "width": 1.0, "face": {**FACE, "brow_w": 1.7}},
}

# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {w: [] for w in cast}


def _put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, **NEUTRAL, "hidden": False, "expr": "neutral", **kw})


def stage(at, keep=(), **ents):
    """Who stands where from `at`: who=(pos, yaw, expr, extras dict). Anyone not named (or kept) is hidden."""
    for who in cast:
        if who in keep:
            continue
        if who in ents:
            pos, yaw, expr, *rest = ents[who]
            kw = dict(rest[0]) if rest else {}
            if who == "odell" and expr == "shut" and "arms" not in kw:
                kw["arms"] = [62, 62]          # his hands on the mower's handle bar
            if expr == "shut":
                expr = "asleep"            # flat drooping lids, never the up-arcs that read as a smile
            _put(who, at, pos, yaw=yaw, expr=expr, **kw)
        else:
            acting[who].append({"at": at, "hidden": True, "blend": 0})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": pos, **kw})


def backward(who):
    """The walk that starts at this actor's latest key keeps its yaw (heels first)."""
    acting[who][-1]["keep_yaw"] = True


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


# ---------------------------------------------------------------------------------------------------- cameras
def C(loc, tgt, lens, loc2=None, tgt2=None, lens2=None):
    ks = [[0, list(loc), list(tgt), lens]]
    if loc2 or tgt2 or lens2:
        ks.append([1, list(loc2 or loc), list(tgt2 or tgt), lens2 or lens])
    return ks


shots = []
looks = {}
Z2 = 2.8   # the bedroom floor
STK = (2.75, 7.0)


def shot(sid, at, cam, note, day=0, step=2, hand=0.008, follow=None, **look):
    d = {"id": sid, "cam": cam, "step": step, "hand": hand, "note": note}
    if at is not None and sid != "S01":
        d["at"] = at
    if follow:
        d["follow"] = follow
    shots.append(d)
    if day >= 0.5 and "exposure" not in look:
        look["exposure"] = 0.2
    looks[sid] = {"day": day, **look}


X0 = 3.4   # the mow line

# ---------------------------------------------------------------------------------------------------- 01 the rule
shot("S01", 0, C((3.1, 4.4, 0.5), (3.3, 8.4, 0.78), 24, (3.1, 5.2, 0.5), (3.3, 8.4, 0.8), 24),
     "frame 1: the red mower coming straight at camera at grass height, a fountain of clippings UP into the deck, "
     "the taller strip behind it, Mr. Odell's shut-eyed face above the handle, the lime yardstick left", step=1, hand=0.004)
stage(0, odell=((X0, 9.9), 0, "shut"))
walk("odell", "L02", (X0, 8.2))
shot("S02", "L02", C((129.3, -1.6, 0.95), (130.0, -0.3, 0.7), 40, (129.6, -1.3, 0.9), (130.0, -0.3, 0.69), 44),
     "night: the bedside clock reads 3:00 in red digits")
stage("L02")
shot("S02b", "L02.2", C((-6.9, 13.0, 4.75), (-5.2, 11.0, 4.1), 30, (-6.7, 12.9, 4.7), (-5.0, 10.9, 4.05), 32),
     "inside our dark front room, close on the white blinds: one slat dips by itself, a green stripe of floodlight, the stick a lime sliver")
stage("L02.2")
shot("S03", "L03", C((-6.0, 3.8, 3.8), (-6.0, -9.0, 3.9), 17, (-6.0, 3.2, 3.8), (-6.0, -9.0, 3.9), 17),
     "the coral house across the street: three upstairs blinds drop shut, left to right")
stage("L03")
shot("S04", "L04", C((-9.2, -2.4, 3.9), (-9.2, -9.0, 3.9), 40, (-9.2, -3.2, 3.9), (-9.2, -9.0, 3.9), 44),
     "the coral house's upstairs window: one bent slat eases back flat and stays shut")
stage("L04")
shot("S05", "L05", C((3.0, 6.3, 0.13), (2.8, 7.0, 0.14), 40, (2.9, 6.5, 0.14), (2.8, 7.0, 0.16), 44),
     "macro at blade height beside the yardstick: clippings landing back on their cut tops, the blades sealing whole",
     macro=True, mower="none", step=1)
stage("L05")
shot("S05b", "L05.1+0.3", C((5.4, 4.7, 0.3), (3.3, 7.6, 0.4), 26, (5.0, 4.9, 0.3), (3.3, 7.8, 0.42), 28),
     "low wide: the mower passing, a taller stripe growing in its wake, the grass up the yardstick to four ticks (cover)", step=1)
stage("L05.1+0.3", odell=((X0, 9.4), 0, "shut"))
walk("odell", "L06", (X0, 7.6))
shot("S06", "L06", C((0.9, 5.4, 0.55), (3.0, 7.6, 0.3), 30, (1.3, 5.6, 0.5), (3.0, 7.6, 0.3), 32),
     "day: his lawn in bright sun, the grass sinking down the stick with nobody near", day=1, mower="park", strip=0.0)
stage("L06")
shot("S06b", "L06.1+0.3", C((2.9, 6.2, 0.4), (2.75, 7.0, 0.3), 42, (2.8, 6.4, 0.4), (2.75, 7.0, 0.3), 46),
     "punch in on the stick: blades sliding down past the ticks", day=1, mower="park", strip=0.0)
stage("L06.1+0.3")
shot("S07", "L07", C((-11.0, 1.2, 1.6), (-4.0, 8.4, 0.9), 20, (-4.0, 1.2, 1.6), (4.2, 8.0, 0.8), 20),
     "morning: a slow push along the row of front lawns, ours shaggy, the others patchy, his straight-striped and even",
     day=1, mower="park", strip=0.0)
stage("L07")
shot("S07b", "L07.2", C((-3.0, 1.6, 1.5), (3.2, 8.2, 0.8), 22, (-1.5, 1.7, 1.5), (4.2, 8.2, 0.8), 22),
     "the row of lawns, his straight and even, the stick at one tick", day=1, mower="park", strip=0.0)
shot("S08", "L08", C((2.1, 5.7, 1.5), (3.3, 8.4, 1.6), 46, (2.2, 5.9, 1.5), (3.3, 8.4, 1.6), 50),
     "tight on Mr. Odell's face at night, eyes shut, calm, floods behind his hair, handle at the bottom, the stick soft beside",
     step=1)
stage("L08", odell=((3.3, 8.5), 0, "shut"))
walk("odell", "L08.3", (3.3, 7.9))
shot("S08b", "L08.2", C((2.4, 5.5, 1.55), (3.3, 8.2, 1.62), 62, (2.5, 5.7, 1.55), (3.3, 8.2, 1.62), 68),
     "closer on the shut eyes, calm", step=1)

# ---------------------------------------------------------------------------------------------------- 02 day
FX = -0.9   # Dad and me at the fence, facing west toward camera
shot("S09", "L09", C((-4.2, 6.3, 1.45), (-0.9, 7.7, 1.3), 30, (-3.8, 6.5, 1.45), (-0.9, 7.7, 1.3), 32),
     "day: me and Dad side by side at the fence, his lawn and the stick behind them", day=1, mower="park", strip=0.0)
stage("L09", dad=((FX, 8.0), -90, "neutral"), me=((FX, 7.0), -90, "neutral"))
shot("S09b", "L09.1", C((-5.2, 4.2, 1.9), (3.2, 12.0, 2.2), 20, (-4.6, 4.4, 1.9), (3.2, 12.0, 2.3), 20),
     "the wide: both houses and the fence, Mr. Odell on his porch", day=1, mower="park", strip=0.0)
stage("L09.1", dad=((-1.6, 6.4), 90, "neutral"), odell=((9.0, 11.4), 0, "smile"))
shot("S09c", "L09.3", C((-2.4, 6.2, 1.45), (-0.9, 7.7, 1.35), 44, (-2.2, 6.3, 1.45), (-0.9, 7.7, 1.35), 48),
     "me and Dad, closer", day=1, mower="park", strip=0.0)
stage("L09.3", dad=((FX, 8.0), -90, "neutral"), me=((FX, 7.0), -90, "neutral"))
shot("S10", "L10", C((0.7, 4.6, 1.5), (-0.5, 7.7, 1.55), 30, (0.8, 4.8, 1.5), (-0.5, 7.7, 1.55), 30),
     "Dad at the fence, angry, glaring over; the stick just over the fence", day=1, mower="park", strip=0.0)
stage("L10", dad=((-0.55, 7.7), 70, "angry"))
shot("S11", "L11", C((7.7, 8.7, 1.65), (9.0, 11.4, 1.6), 40, (7.9, 8.9, 1.65), (9.0, 11.4, 1.6), 42),
     "Mr. Odell on his porch waving slowly, eyes open, wistful (plant 2a)", day=1, mower="park", strip=0.0)
stage("L11", odell=((9.0, 11.4), 0, "sad-smile", {"side": [0, 140]}))
key("odell", "L11.1+0.2", side=[0, 105], blend=0.3)
key("odell", "L11.1+0.7", side=[0, 140], blend=0.3)
key("odell", "L11.2", side=[0, 105], blend=0.3)
key("odell", "L11.2+0.5", side=[0, 140], blend=0.3)

shot("S11b", "L11.2", C((8.0, 9.4, 1.65), (9.0, 11.4, 1.65), 62, (8.1, 9.5, 1.65), (9.0, 11.4, 1.65), 70),
     "closer: the wave, he misses him", day=1, mower="park", strip=0.0)

# the coffee cart (the line stands north, facing the cart)
QX = 4.2
shot("S12", "L12", C((2.2, -0.2, 1.6), (4.3, 3.9, 1.3), 28, (2.4, 0.2, 1.6), (4.3, 3.9, 1.3), 30),
     "the coffee cart, morning sun: Mr. Odell at the counter with his back half to camera, his plain lidded cup held low, "
     "Dad and me behind; the street and the stick behind", day=1, mower="park", strip=0.0)
stage("L12", odell=((QX, 3.7), 160, "smile", {"arms": [0, 50]}), dad=((QX, 2.9), 180, "neutral"), me=((QX, 2.15), 180, "neutral"))
shot("S12b", "L12.2", C((5.2, 1.9, 1.65), (4.2, 3.6, 1.65), 42, (5.0, 2.1, 1.65), (4.2, 3.6, 1.65), 46),
     "Mr. Odell turning to Dad, smile; the cup out of frame", day=1, mower="park", strip=0.0)
stage("L12.2", odell=((QX, 3.7), 160, "smile", {"arms": [0, 50]}), dad=((QX, 2.9), 180, "neutral"), me=((QX, 2.15), 180, "neutral"))
key("odell", "L12.2+0.2", yaw=15, blend=0.5, arms=[0, 0])
shot("S13", "L13", C((3.3, 3.95, 1.62), (4.2, 2.8, 1.6), 42, (3.4, 3.8, 1.62), (4.2, 2.7, 1.6), 46),
     "Dad's face, frozen; me behind him, worried", day=1, mower="park", strip=0.0)
stage("L13", odell=((QX, 3.7), 10, "smile"), dad=((QX, 2.9), 180, "neutral"), me=((QX, 2.15), 180, "worried"))
shot("S14", "L14", C((2.6, 3.3, 1.3), (3.8, 3.15, 1.22), 24, (2.8, 3.3, 1.3), (3.8, 3.15, 1.22), 24),
     "close on a new white cup with a brown lid at Mr. Odell's sleeve end, held toward Dad", day=1, mower="park", strip=0.0)
stage("L14", odell=((QX, 3.7), 0, "smile", {"arms": [0, 78]}), dad=((QX, 2.9), 180, "neutral"))
shot("S15", "L15-0.45", C((2.9, 3.0, 1.4), (4.3, 4.9, 1.2), 30, (3.1, 3.2, 1.4), (4.3, 4.9, 1.2), 32),
     "the cart counter, nobody serving yet", day=1, mower="park", strip=0.0)
stage("L15-0.45")
shot("S15b", "L15.1", C((4.2, 1.5, 1.62), (4.2, 2.9, 1.6), 44, (4.2, 1.9, 1.62), (4.2, 2.9, 1.6), 50),
     "punch in on Dad's face, he hasn't ordered", day=1, mower="park", strip=0.0)
stage("L15.1", dad=((QX, 2.9), 0, "neutral"))

# ---------------------------------------------------------------------------------------------------- 03 friday, 3 AM
shot("S16", "L16", C((-9.5, 18.5, Z2 + 1.55), (-6.6, 13.4, Z2 + 1.2), 27, (-9.3, 18.3, Z2 + 1.55), (-6.8, 13.6, Z2 + 1.2), 27),
     "Dad in his robe heading out; past his shoulder the window with the floodlit lawn", mower=None)
stage("L16", dadn=((-6.9, 14.2, Z2), 0, "neutral"), odell=((X0, 9.2), 0, "shut"))
walk("dadn", "L16.1", (-9.4, 17.3, Z2))
shot("S16b", "L16.1", C((-10.3, 8.9, 1.7), (-7.0, 11.0, 1.3), 34, (-10.2, 9.4, 1.7), (-6.4, 11.0, 1.3), 34),
     "Dad on our porch, facing the lawn", sway=True, mower=None)
stage("L16.1", dadn=((-8.2, 10.8, 0.2), 90, "neutral"), odell=((X0, 9.2), 0, "shut"))
shot("S16c", "L16.2", C((-6.3, 9.3, 1.62), (-8.2, 10.8, 1.6), 46, (-6.4, 9.5, 1.62), (-8.2, 10.8, 1.6), 50),
     "Dad's face on the porch, looking", mower=None)
stage("L16.2", dadn=((-8.2, 10.8, 0.2), 90, "neutral"))
shot("S17", "L17", C((-9.6, 10.0, 1.78), (3.0, 8.3, 0.9), 62, (-9.5, 10.1, 1.75), (3.0, 8.2, 0.85), 66),
     "over Dad's shoulder: the floodlit lawn, the mower running, the stick", step=1)
stage("L17", dadn=((-8.4, 10.9, 0.2), 90, "neutral"), odell=((X0, 9.4), 0, "shut"))
walk("odell", "L18", (X0, 8.2))
shot("S18", "L18", C((1.3, 6.4, 0.34), (3.4, 6.4, 0.28), 30, (1.4, 6.4, 0.34), (3.4, 6.4, 0.28), 32),
     "the reversed clippings side-on, the stick in the foreground with the grass climbing it", step=1)
stage("L18", odell=((X0, 8.6), 0, "shut"))
walk("odell", "L18.2", (X0, 7.0))
shot("S18b", "L18.2", C((1.5, 6.3, 0.3), (2.75, 7.0, 0.28), 42, (1.6, 6.4, 0.3), (2.75, 7.0, 0.3), 44),
     "the grass gets longer: the stick's patch climbing", step=1)
stage("L18.2", odell=((X0, 7.0), 0, "shut"))
walk("odell", "L19", (X0, 6.6))
shot("S19", "L19", C((3.4, 3.4, 0.6), (3.4, 8.0, 0.9), 26, (3.4, 3.3, 0.6), (3.4, 8.0, 0.9), 26),
     "low on the lawn: Mr. Odell and the mower moving away from camera heels first, eyes shut", step=1, sway=True)
stage("L19", odell=((X0, 7.2), 0, "shut"))
backward("odell")
walk("odell", "L19>", (X0, 9.6))
shot("S19b", "L19.1+0.5", C((5.2, 5.6, 0.45), (3.4, 8.4, 0.8), 30, (5.0, 5.8, 0.45), (3.4, 8.6, 0.85), 30),
     "low from the side: the mower and Odell moving backward, the clippings flying in", step=1)
shot("S20", "L20", C((-9.6, 10.2, 1.7), (0.5, 8.0, 1.2), 56, (-9.4, 10.3, 1.7), (0.5, 8.0, 1.25), 62),
     "over Dad's shoulder: a figure fading in by the fence in a pool of warm morning light, at night", flood=0.5)
stage("L20", dadn=((-8.4, 10.9, 0.2), 90, "scared"), dad=((0.5, 8.0), -90, "smile", {"arms": [58, 58]}))
shot("S21", "L21", C((-1.9, 8.1, 1.62), (0.55, 8.0, 1.5), 40, (-1.7, 8.1, 1.62), (0.55, 8.0, 1.5), 44),
     "the vision: Dad in day clothes at the fence with two cups, warm key, night all round", flood=0.5, ticks=[1, 1])
stage("L21", dad=((0.55, 8.0), -90, "smile", {"arms": [58, 58]}))
shot("S21b", "L21.2", C((-5.9, 10.4, 1.65), (-8.2, 10.8, 1.6), 46, (-6.0, 10.4, 1.65), (-8.2, 10.8, 1.6), 50),
     "robe Dad on the porch, scared", flood=0.6, ticks=[1, 1])
stage("L21.2", dadn=((-8.2, 10.8, 0.2), 90, "scared"), dad=((0.55, 8.0), -90, "smile", {"arms": [58, 58]}))
shot("S22", "L22", C((-6.2, 8.8, 1.55), (-8.5, 11.6, 1.5), 36, (-6.4, 8.9, 1.55), (-8.5, 11.6, 1.5), 38),
     "me beside the door behind Dad, scared, the lawn beyond")
stage("L22", dadn=((-8.0, 10.6, 0.2), 90, "scared"), me=((-8.9, 11.6, 0.2), 0, "scared"))
shot("S23", "L23-0.35", C((2.0, 5.2, 0.9), (3.4, 6.9, 0.5), 30, (2.2, 5.3, 0.9), (3.4, 6.9, 0.5), 32),
     "the mower halting; the hum cuts", step=1, clip=0.0)
stage("L23-0.35", odell=((X0, 7.7), 0, "shut"))
walk("odell", "L23+0.3", (X0, 7.5))
shot("S23b", "L23.1", C((0.15, -1.4, 1.2), (0.2, -0.55, 1.0), 26, (0.15, -1.2, 1.18), (0.2, -0.55, 1.0), 26),
     "the lore: two lime strokes scratched by the left grip", follow="odell", hand=0.0, clip=0.0)
stage("L23.1", odell=((X0, 7.5), 0, "shut"))
shot("S24", "L24", C((0.9, 7.2, 1.5), (3.4, 7.9, 1.55), 42, (1.0, 7.3, 1.5), (3.4, 7.9, 1.55), 46),
     "Mr. Odell turning toward our porch, eyes shut, a slow wave", mower=[X0, 6.05, 0], clip=0.0)
stage("L24", odell=((3.2, 7.9), 0, "shut", {"arms": [0, 0]}))
key("odell", "L24+0.3", yaw=-85, blend=0.9)
key("odell", "L24.1", side=[0, 140], blend=0.4)
key("odell", "L24.1+0.5", side=[0, 105], blend=0.3)
key("odell", "L24.2", side=[0, 140], blend=0.3)
shot("S24b", "L24.2", C((1.2, 7.0, 1.55), (3.1, 7.9, 1.6), 58, (1.3, 7.1, 1.55), (3.1, 7.9, 1.6), 62),
     "closer on the wave, eyes still shut", mower=[X0, 6.05, 0], clip=0.0)
stage("L24.2", odell=((3.2, 7.9), -85, "shut", {"arms": [0, 0], "side": [0, 140]}))
key("odell", "L24.2+0.4", side=[0, 105], blend=0.3)
key("odell", "L24.2+0.8", side=[0, 140], blend=0.3)

# ---------------------------------------------------------------------------------------------------- 04 said plainly
MS = [X0, 6.05, 0]   # the stopped mower
shot("S25", "L25", C((-1.6, 5.4, 5.2), (3.3, 7.6, 0.4), 30, (-1.0, 5.6, 5.0), (3.3, 7.6, 0.4), 30),
     "high above the fence: his lawn under the floods, the mower stopped, a slow fountain still rising into the deck, "
     "the stick at four ticks", mower=MS, clip=0.35, hand=0.0, step=1)
stage("L25", odell=((X0, 7.5), 0, "shut"))
shot("S26", "L26", C((-3.0, 5.3, 1.4), (-8.0, 10.8, 1.2), 28, (-3.0, 5.3, 1.4), (4.2, 8.0, 0.8), 28),
     "a slow pan along the fence from our porch to his, the stick passing through frame", mower=MS, clip=0.0, hand=0.003)
stage("L26", dadn=((-8.2, 10.8, 0.2), 90, "neutral"), odell=((X0, 7.5), 0, "shut"))
shot("S27", "L27", C((3.0, 4.15, 1.62), (4.2, 3.2, 1.6), 38, (3.2, 4.0, 1.62), (4.2, 3.2, 1.6), 40),
     "day: Mr. Odell at the cart, careful and stiff", day=1, mower="park", strip=0.0)
stage("L27", odell=((QX, 3.4), 140, "smile"))
shot("S27b", "L27.2", C((2.1, 5.7, 1.5), (3.3, 8.4, 1.6), 46, (2.2, 5.9, 1.5), (3.3, 8.4, 1.6), 50),
     "night: the same face, eyes shut, at ease behind the mower", step=1)
stage("L27.2", odell=((3.3, 8.5), 0, "shut"))
walk("odell", "L27>", (3.3, 7.8))
shot("S28", "L28", C((-6.0, 3.8, 3.8), (-6.0, -9.0, 3.9), 17, (-6.0, 3.2, 3.8), (-6.0, -9.0, 3.9), 17),
     "the coral house's blinds, shut tight", mower=None)
stage("L28")
shot("S28b", "L28.1+0.2", C((-10.3, 8.9, 1.7), (-7.0, 11.0, 1.3), 34, (-10.2, 9.4, 1.7), (-6.4, 11.0, 1.3), 34),
     "Dad on the porch, still looking", sway=True, mower=MS, clip=0.0)
stage("L28.1+0.2", dadn=((-8.2, 10.8, 0.2), 90, "neutral"), odell=((X0, 7.5), 0, "shut"))
shot("S29", "L29", C((1.0, 5.8, 0.45), (2.75, 7.0, 0.3), 36, (1.2, 5.9, 0.45), (2.75, 7.0, 0.3), 38),
     "the stick by day, the grass sinking", day=1, mower="park", strip=0.0, ticks=[4, 1])
stage("L29")
shot("S29b", "L29.2", C((1.2, 6.1, 0.4), (2.75, 7.0, 0.3), 36, (1.3, 6.2, 0.4), (2.75, 7.0, 0.3), 38),
     "the stick at night, the grass climbing", mower=MS, clip=0.0, ticks=[1, 4])
stage("L29.2")
shot("S29c", "L29.3", C((1.0, 5.8, 0.5), (2.75, 7.0, 0.3), 34, (1.2, 5.9, 0.5), (2.75, 7.0, 0.3), 36),
     "morning: the stick at one tick, exactly as before", day=1, mower="park", strip=0.0, ticks=[1, 1])
stage("L29.3")
shot("S30", "L30", C((-0.6, 5.4, 0.55), (5.5, 8.6, 0.1), 28, (-0.2, 5.5, 0.5), (5.5, 8.6, 0.1), 28),
     "the straight-striped lawn in morning light, every blade even", day=1, mower="park", strip=0.0, ticks=[1, 1])
stage("L30")
shot("S31", "L31", C((2.1, 5.7, 1.5), (3.3, 8.4, 1.6), 50, (2.2, 5.9, 1.5), (3.3, 8.4, 1.6), 54),
     "Mr. Odell, eyes shut, calm", mower=None, step=1)
stage("L31", odell=((3.3, 8.5), 0, "shut"))
walk("odell", "L31.1", (3.3, 8.0))
shot("S31b", "L31.1", C((4.3, 5.4, 2.4), (3.4, 8.0, 0.0), 24, (4.2, 5.8, 2.3), (3.4, 7.6, 0.0), 24),
     "the mower tracing the same stripe edge exactly", step=1)
stage("L31.1", odell=((X0, 9.6), 0, "shut"))
walk("odell", "L31>", (X0, 8.0))
shot("S32", "L32", C((-2.6, 5.7, 1.1), (0.0, 8.5, 0.55), 30, (-2.2, 5.8, 1.1), (0.0, 8.5, 0.55), 32),
     "two lawn chairs by the low fence, one each side, two lidded cups on the fence rail; no people",
     day=1, mower="park", strip=0.0, chairs=True)
stage("L32")
shot("S32b", "L32.1", C((-0.9, 6.9, 0.85), (0.0, 8.5, 0.55), 52, (-0.8, 7.0, 0.85), (0.0, 8.5, 0.55), 58),
     "the two cups on the rail", day=1, mower="park", strip=0.0, chairs=True)
shot("S33", "L33", C((9.0, 8.3, 1.55), (9.0, 11.4, 1.45), 40, (9.0, 8.5, 1.55), (9.0, 11.4, 1.45), 44),
     "Mr. Odell alone on his porch at night, eyes shut", mower="none")
stage("L33", odell=((9.0, 11.4), 0, "shut", {"arms": [0, 0]}))
shot("S33b", "L33.2", C((7.7, 8.7, 1.65), (9.0, 11.4, 1.6), 40, (7.9, 8.9, 1.65), (9.0, 11.4, 1.6), 42),
     "the wave again, wistful, same framing as L11", day=1, mower="park", strip=0.0)
stage("L33.2", odell=((9.0, 11.4), 0, "sad-smile", {"side": [0, 140]}))
key("odell", "L33.2+0.3", side=[0, 105], blend=0.3)
key("odell", "L33.2+0.8", side=[0, 140], blend=0.3)

# ---------------------------------------------------------------------------------------------------- 05 two coffees
SUN = dict(day=0.85, warm=1.0, mower="park", strip=0.0)
shot("S34", "L34", C((3.7, 0.9, 1.5), (4.0, 3.7, 1.4), 32, (3.8, 1.2, 1.5), (4.0, 3.7, 1.4), 34),
     "the cart at sunrise: Dad with two cups at his sleeve ends, me beside him, smiling; the stick far behind", **SUN)
stage("L34", dad=((4.6, 3.5), 0, "smile", {"arms": [58, 58]}), me=((3.6, 3.5), 0, "smile"))
shot("S35", "L35", C((4.2, 3.9, 1.35), (4.25, 4.6, 1.05), 60, (4.2, 4.0, 1.3), (4.25, 4.6, 1.05), 68),
     "close on the two cups, a lime sleeve slipping onto one", **SUN)
stage("L35")
shot("S36", "L36", C((4.6, 1.8, 1.62), (4.6, 3.4, 1.6), 46, (4.6, 2.0, 1.62), (4.6, 3.4, 1.6), 52),
     "Dad's face, a small shrug", **SUN)
stage("L36", dad=((4.6, 3.5), 0, "smirk", {"arms": [58, 58]}))
key("dad", "L36+0.1", side=[25, 25], blend=0.2)
key("dad", "L36+0.5", side=[0, 0], blend=0.3)
shot("S37", "L37", C((-1.4, 5.7, 1.4), (0.8, 7.4, 0.9), 28, (-1.0, 5.8, 1.4), (1.0, 7.4, 0.9), 30),
     "Dad stepping over the low white fence onto the green lawn, two cups, the stick beside him", **SUN)
stage("L37", dad=((-1.8, 7.5), 90, "smile", {"arms": [58, 58]}))
walk("dad", "L37+0.5", (-0.5, 7.5))
walk("dad", "L37+0.85", (0.0, 7.5, 0.42))
walk("dad", "L37+1.2", (0.6, 7.5))
walk("dad", "L37>", (2.2, 7.4))
shot("S38", "L38", C((0.9, 6.0, 1.55), (3.3, 7.9, 1.6), 38, (1.1, 6.2, 1.55), (3.3, 7.9, 1.6), 40),
     "Mr. Odell turning toward Dad's steps, eyes opening, smile", **SUN)
stage("L38", odell=((3.7, 7.9), -60, "shut", {"arms": [0, 0]}), dad=((2.2, 7.4), 90, "smile", {"arms": [58, 58]}))
key("odell", "L38.1", yaw=-90, blend=0.5, expr="smile")
shot("S38b", "L38.2", C((2.5, 6.2, 1.5), (3.0, 7.7, 1.4), 46, (2.6, 6.3, 1.5), (3.0, 7.7, 1.4), 50),
     "the lime-sleeve cup passes to him on a cut", **SUN)
stage("L38.2", odell=((3.4, 7.6), -90, "smile", {"arms": [0, 60]}), dad=((2.2, 7.4), 90, "smile", {"arms": [58, 58]}))
shot("S39", "L39", C((2.75, 4.8, 1.35), (2.75, 7.2, 1.25), 36, (2.75, 5.1, 1.35), (2.75, 7.2, 1.25), 40),
     "the two at the fence, cups up, side by side, the stick between them", **SUN)
stage("L39", odell=((3.4, 7.2), -90, "smile", {"arms": [0, 62]}), dad=((2.1, 7.2), 90, "smile", {"arms": [62, 62]}))
shot("S39b", "L39.2", C((3.0, 6.3, 1.2), (3.35, 7.2, 1.15), 60, (3.05, 6.4, 1.2), (3.35, 7.2, 1.15), 68),
     "punch in on the lime sleeve", **SUN)
stage("L39.2", odell=((3.4, 7.2), -90, "smile", {"arms": [0, 62]}), dad=((2.1, 7.2), 90, "smile", {"arms": [62, 62]}))
shot("S40", "L40", C((2.2, 5.5, 1.62), (2.1, 7.2, 1.6), 46, (2.2, 5.7, 1.62), (2.1, 7.2, 1.6), 50),
     "Dad's face, smile, morning sun", **SUN)
stage("L40", dad=((2.1, 7.2), 0, "smile", {"arms": [62, 62]}))
shot("S41", "L41", C((3.5, 5.5, 1.5), (3.4, 7.2, 1.55), 46, (3.4, 5.7, 1.5), (3.4, 7.2, 1.55), 52),
     "Mr. Odell's face, smile, holding the cup, eyes closing slowly; the sting", **SUN)
stage("L41", odell=((3.4, 7.2), 0, "smile", {"arms": [0, 62]}))
key("odell", "L41+0.7", expr="soft")

# ---------------------------------------------------------------------------------------------------- 06 loop
shot("S42", "L42", C((-10.2, 9.4, 1.72), (2.8, 7.8, 0.95), 56, (-10.1, 9.5, 1.72), (2.8, 7.7, 0.95), 62),
     "Dad on our porch at night, robe, a lime-sleeve cup at his sleeve end, the floodlit lawn and the stick beyond; the hum swells",
     mower=None, ticks=[1, 1])
stage("L42", dadn=((-8.4, 10.9, 0.2), 90, "smile", {"arms": [55, 55]}), odell=((X0, 9.6), 0, "shut"))
walk("odell", "L42>", (X0, 8.4))
shot("S42b", "L42.2", C((-5.9, 10.4, 1.65), (-8.2, 10.8, 1.6), 46, (-6.0, 10.4, 1.65), (-8.2, 10.8, 1.6), 50),
     "Dad smiling, he likes what's coming", mower=None, ticks=[1, 1])
stage("L42.2", dadn=((-8.2, 10.8, 0.2), 90, "smile", {"arms": [55, 55]}))
shot("S43", "L43", C((-6.0, 3.8, 3.8), (-6.0, -9.0, 3.9), 17, (-6.0, 3.2, 3.8), (-6.0, -9.0, 3.9), 17),
     "the blinds across the street snap shut", mower=None, ticks=[1, 1])
stage("L43")
shot("S43b", "L43.2", C((-6.9, 13.0, 4.75), (-5.2, 11.0, 4.1), 30, (-6.7, 12.9, 4.7), (-5.0, 10.9, 4.05), 32),
     "our own blinds, the green stripe; 0.25 s after 'wonder' we cut back to S01", mower=None, ticks=[1, 1])
stage("L43.2")

# ---------------------------------------------------------------------------------------------------- cups
cups = [
    {"who": "odell", "hand": "r", "from": "L12", "to": "L12.2", "kind": "plain"},           # his plain lidded cup, never named
    {"who": "odell", "hand": "r", "from": "L14", "to": "L15", "kind": "plain", "scale": 1.6},   # the one held toward Dad
    {"who": "dad", "hand": "l", "from": "L20", "to": "L22", "kind": "plain"},               # the vision's two cups
    {"who": "dad", "hand": "r", "from": "L20", "to": "L22", "kind": "plain"},
    {"who": "dad", "hand": "l", "from": "L34", "to": "L35", "kind": "plain"},               # sunrise: two coffees
    {"who": "dad", "hand": "r", "from": "L34", "to": "L35", "kind": "plain"},
    {"pos": [4.0, 4.6, 1.035], "from": "L35", "to": "L36", "kind": "plain", "scale": 2.0, "shots": ["S35"]},
    {"pos": [4.5, 4.6, 1.035], "from": "L35", "to": "L36", "kind": "lime", "scale": 2.0, "shots": ["S35"],
     "slide": ["L35.2", "L35.2+0.5"]},
    {"who": "dad", "hand": "l", "from": "L36", "to": "L41>", "kind": "plain"},
    {"who": "dad", "hand": "r", "from": "L36", "to": "L38.2", "kind": "lime"},
    {"who": "odell", "hand": "r", "from": "L38.2", "to": "L41>", "kind": "lime"},
    {"who": "dadn", "hand": "r", "from": "L42", "to": "end", "kind": "lime"},
    {"pos": [0.0, 8.25, 0.575], "from": 0, "to": "end", "kind": "plain", "shots": ["S32"]},
    {"pos": [0.0, 8.75, 0.575], "from": 0, "to": "end", "kind": "plain", "shots": ["S32"]},
]

# ---------------------------------------------------------------------------------------------------- tracks
tracks = {
    # ticks of grass on the yardstick: climbs while the mower runs, sinks in daylight
    "stick": [[0, 1], ["L01", 1], ["L05>", 4], ["L06", 4], ["L06>", 1], ["L16", 1], ["L18.2", 1], ["L19>", 4],
              ["L33", 4], ["L34", 4], ["L41", 1], ["end", 1]],
    "slat": [[0, 0], ["L02.2+0.1", 0], ["L02.2+0.6", 1], ["L02>", 1], ["L03", 0]],
    "bend": [[0, 1], ["L04", 1], ["L04+0.5", 1], ["L04>", 0]],
    "vision": [[0, 0], ["L20", 0], ["L20+0.5", 1], ["L21>", 1], ["L22", 0]],
    # the south blinds: open by day, snapped shut at night, open at sunrise, snapped shut again at the end
    "bw0": [[0, 0], ["L03.1+0.3", 0], ["L03.1+0.65", 1], ["L05>", 1], ["L06", 0], ["L16", 0], ["L16+0.4", 1], ["L34", 1],
            ["L34+0.4", 0], ["L43", 0], ["L43+0.35", 1]],
    "bw1": [[0, 0], ["L03.1+0.6", 0], ["L03.1+0.95", 1], ["L05>", 1], ["L06", 0], ["L16", 0], ["L16+0.4", 1], ["L34", 1],
            ["L34+0.4", 0], ["L43+0.3", 0], ["L43+0.65", 1]],
    "bw2": [[0, 0], ["L03.1", 0], ["L03.1+0.35", 1], ["L05>", 1], ["L06", 0], ["L16", 0], ["L16+0.4", 1], ["L34", 1],
            ["L34+0.4", 0], ["L43+0.6", 0], ["L43+0.95", 1]],
}

premise = ("Our neighbor Mr. Odell mows his lawn at three in the morning with his eyes shut, and the grass comes out "
           "longer. The street's rule is never to look while the mower runs, so every blind snaps shut. My dad lives "
           "next door to him and has never spoken to him, but Mr. Odell waves at Dad like he misses him, and at a "
           "coffee cart he says Dad's order before Dad gives it.")
twist = ("Mr. Odell lives backward through time. Our tomorrow is his yesterday: he isn't guessing Dad's future, he "
         "remembers it, and in Dad's future the two of them are best friends. Dad buys two coffees at sunrise, guesses "
         "hot chocolate, crosses the fence, and Mr. Odell has ordered that for six years. Dad's guess is the first day "
         "of a friendship that, for Mr. Odell, ends today.")
world = ("a bright suburban cul-de-sac at three in the morning: a floodlit straight-striped lawn with a lime yardstick "
         "staked in it and a red push mower on an orange cord, a butter yellow house with a blinded upstairs window, a "
         "coral house across the street, a low white fence, and by day a teal coffee cart at the curb")

story = {
    "slug": "night-mower",
    "rev": 3,
    "title": "His Mower Makes Grass LONGER",
    "made_for_kids": False,
    "premise": premise,
    "twist": twist,
    "world": world,
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#b6ff3b",
    "gap": GAP,
    "tail": LOOP,
    "fade_in": False,
    "fade_out": False,
    "look": {"style": "closer", "fog": "#6f86c8", "fog_density": 0.012, "fog_start": 14.0, "sky": "#1b2a6b",
             "exposure": 0.0, "flash_safe": True,
             "polish": {"emph": ["L01", "L18", "L25", "L36"], "reveal": ["L21", "L25"], "twist": "L25",
                        "quiet": [["L37", "L39"]], "sway": ["S16b", "S19", "S28b"],
                        "hold": ["S03", "S28", "S43", "S09b", "S32"]},
             "hdri": "moonless_golf", "hdri_strength": 0.6, "hdri_visible": False},
    "grade": {"shadows": [0.0, 0.0, 0.05], "highlights": [0.02, 0.01, -0.02], "saturation": 1.12, "contrast": 1.06,
              "vignette": 0.3, "bloom": 0.3, "grain": 0.01, "red_line": 0.78},
    "phonemes": {"Ours": "ˌaʊɚz", "ours": "ˌaʊɚz"},
    "caption": {"shadow": 0.6},
    "min_read": 0,
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": {w: ks for w, ks in acting.items() if ks},
    "tracks": tracks,
    "looks": looks,
    "cups": cups,
    "set_moves": ["S05", "S06", "S06b", "S29", "S29b", "S35"],
    "fx": [],
    "music": {"root": 50, "mode": "mixolydian", "bpm": 104, "seed": 7,
              "sections": [
                  {"at": 0, "voices": ["pulse", "piano"], "energy": 0.5},
                  {"at": "L06", "voices": ["pulse", "piano"], "energy": 0.55},
                  {"at": "L16", "voices": ["drone", "pad", "piano"], "energy": 0.5},
                  {"at": "L20", "voices": ["drone", "pad"], "energy": 0.6},
                  {"at": "L25", "voices": ["drone", "pad", "piano"], "energy": 0.55},
                  {"at": "L34", "voices": ["pad", "piano"], "energy": 0.45, "mode": "major", "root": 50},
                  {"at": "L40", "voices": ["pad"], "energy": 0.3, "mode": "major", "root": 50},
                  {"at": "L42", "voices": ["drone", "pad"], "energy": 0.45, "mode": "mixolydian", "root": 50},
              ]},
    "sound": {"floor": "grass", "steps_db": -22, "rev": 3,
              "ambience": [
                  {"kind": "crickets", "from": 0, "to": "L06", "lufs": -36},
                  {"kind": "hum", "from": 0, "to": "L02", "lufs": -34},
                  {"kind": "hum", "from": "L05.1", "to": "L06", "lufs": -34},
                  {"kind": "wind", "from": "L06", "to": "L16", "lufs": -42},
                  {"kind": "crickets", "from": "L16", "to": "L34", "lufs": -36},
                  {"kind": "hum", "from": "L16.1", "to": "L23", "lufs": -34},
                  {"kind": "drone", "from": "L20", "to": "L34", "lufs": -34},
                  {"kind": "wind", "from": "L34", "to": "L42", "lufs": -42},
                  {"kind": "crickets", "from": "L42", "to": "end", "lufs": -36},
                  {"kind": "hum", "from": "L42", "to": "end", "lufs": -32},
              ],
              "sfx": [
                  {"at": "L03.1+0.1", "kind": "latch", "db": -16},
                  {"at": "L03.1+0.4", "kind": "latch", "db": -16},
                  {"at": "L03.1+0.7", "kind": "latch", "db": -14},
                  {"at": "L21+0.1", "kind": "thud", "db": -9},
                  {"at": "L24.2", "kind": "thud", "db": -10},
                  {"at": "L25.1", "kind": "thud", "db": -8},
              ],
              "music_drops": [{"from": "P01", "to": "L20+0.4", "keep": ["thud"]},
                              {"from": "P02", "to": "L25.1-0.05", "keep": ["thud"]}]},
}
import re as _re

_REF = _re.compile(r"^(L\d+)\.(\d+)(.*)$")


def _remap(o):
    if isinstance(o, str):
        m = _REF.match(o)
        if m and m.group(1) in CHUNK_MAP:
            return f"{m.group(1)}.{CHUNK_MAP[m.group(1)][int(m.group(2))]}{m.group(3)}"
        return o
    if isinstance(o, list):
        return [_remap(x) for x in o]
    if isinstance(o, dict):
        return {k: (v if k in ("id", "note", "who", "lines", "kind", "hand") else _remap(v)) for k, v in o.items()}
    return o


def _fit_lens(sh):
    if sh["id"] in ("S05", "S06b", "S18b", "S35", "S39b", "S14") or sh.get("follow"):
        return
    for k in sh["cam"]:
        loc, tgt, lens = k[1], k[2], k[3]
        if lens < 34:
            continue
        d = math.dist(loc, tgt)
        k[3] = round(max(17.0, min(lens, 9.0 * d)), 1)


for _s in shots:
    _fit_lens(_s)

for _k in ("shots", "acting", "tracks", "cups", "music", "sound"):
    story[_k] = _remap(story[_k])
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
