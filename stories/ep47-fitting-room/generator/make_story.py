"""Writes ../story.json for ep47 "Fitting room" (script.md, 2026-11-02).

Run from anywhere: python stories/ep47-fitting-room/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (time of day, lamps, curtain, the Empty, tags, props), the score and the sound.
Places are set.py's (see its header). A character with yaw 0 faces -y, 90 faces +x, -90 faces -x, 180 faces +y.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# captions show two or three words at a time (the house check): a longer chunk is split in two, and every chunk
# reference below (L53.3 and the like) is written for the script's own chunks, so it's remapped to the split ones
IDX = {}
SPLIT = []
for ln in lines:
    if "chunks" not in ln or not ln["chunks"]:
        continue
    new, m = [], {}
    for k, (cap, spk) in enumerate(ln["chunks"]):
        m[k] = len(new)
        cw, sw = cap.split(" "), spk.split(" ")
        n = len(cw)
        if n <= 3:
            new.append([cap, spk])
            continue
        h = (n + 1) // 2
        new.append([" ".join(cw[:h]), " ".join(sw[:h])])
        new.append([" ".join(cw[h:]), " ".join(sw[h:])])
        SPLIT.append(ln["id"])
    ln["chunks"] = new
    IDX[ln["id"]] = m
print("split lines:", ",".join(sorted(set(SPLIT))))

# a swallowed name or title is helped: slower, or a spelling the voice says plainly
TEMPO = {"L12": 0.95, "L07": 0.95, "L64": 0.95, "L63": 0.9}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]

# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True}


def mk(skin, shirt, pants="#33363e", shoes="#3a2a20", hair="cap", hair_c="#2a1d15", tags=None, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": shoes,
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "hat": "none", "face": dict(FACE)}
    d.update(kw)
    if tags:
        d["tags"] = tags
    return d


cast = {
    "me": mk("#e0b08a", "#4a6078", "#3b3e46", "#6a4a30", "cap", "#241a16", collar="#efe6d2", extras=["coat"],
             zip_c="#3b4a5c", face={"eyes": "lashes", "brows": True}),
    "me2": mk("#e0b08a", "#efe6d2", "#3b3e46", "#6a4a30", "cap", "#241a16", face={"eyes": "lashes", "brows": True}),
    "uncle": mk("#d9a98a", "#e9e5da", "#3c4a3e", "#3a2a20", "cap", "#9a9a98", tags="uncle", extras=["apron"],
                extra_c="#c9b996", face={"eyes": "tired", "brows": True, "bags": True}),
    "uncle2": mk("#d9a98a", "#e9e5da", "#3c4a3e", "#3a2a20", "cap", "#9a9a98", extras=[], extra_c="#4a4a4a",
                 face={"eyes": "tired", "brows": True, "bags": True}),
    "salesman": mk("#cf9c76", "#7a5a8a", hair="buzz", hair_c="#3a2a1e", tags="lump"),
    "salon_a": mk("#e6bd98", "#a65a4a", hair="cap", hair_c="#3a2a1e", tags="speckle", face={"eyes": "lashes", "brows": True}),
    "salon_b": mk("#d8a47c", "#b49ad8", hair="bun", hair_c="#6a4a34", tags="speckle", face={"eyes": "lashes", "brows": True}),
    "date_m": mk("#c98f6a", "#2f4a6a", hair="spiky", hair_c="#2a1d15", tags="lump"),
    "date_f": mk("#e8c2a0", "#a84a5a", hair="long", hair_c="#4a2a1a", tags="lump", face={"eyes": "lashes", "brows": True}),
    "cafe_man": mk("#b88460", "#556b4a", hat="beanie", hat_c="#b8302e", tags="speckle"),
    "cafe_f": mk("#f0ceac", "#d8a040", hair="swoop", hair_c="#7a4a2a", tags="speckle", face={"eyes": "lashes", "brows": True}),
    "mrs_kettle": mk("#e8c8a8", "#6a2f55", "#2a2830", hair="bun", hair_c="#b8b8b8", height=0.94,
                     face={"eyes": "round", "brows": True}),
    "mr_kettle": mk("#d8b08c", "#7a7466", "#4a4a44", hat="ballcap", hat_c="#6a6a64", hair="buzz", hair_c="#aaaaaa", tags="lump"),
    "cam": mk("#d4a07c", "#b08850", hair="buzz", hair_c="#8a8a88", tags="speckle", extras=["coat"], zip_c="#6a4a2a"),
    "teal": mk("#a87454", "#2f7a78", hair="long", hair_c="#1a1210", tags="speckle", extras=["scarf"], extra_c="#2a9a96",
               face={"eyes": "lashes", "brows": True}),
    "stick": mk("#e0b898", "#5a5a60", "#2e2e34", hair="buzz", hair_c="#dcdcdc", tags="speckle", height=0.96),
}
XS = [("x1", "#d09a76", "#8a4a3a", "buzz", "#2a1d15"), ("x2", "#e8c2a0", "#3a6a5a", "long", "#5a3a22"),
      ("x3", "#b88460", "#7a8a4a", "spiky", "#1a1210"), ("x4", "#f0ceac", "#6a4a7a", "cap", "#8a5a2a"),
      ("x5", "#9a6a4a", "#a8883a", "buzz", "#101010"), ("x6", "#e0b898", "#4a5a8a", "long", "#2a1d15")]
for n, sk, sh, hr, hc in XS:
    cast[n] = mk(sk, sh, hair=hr, hair_c=hc, tags="speckle", face={"eyes": "lashes" if hr == "long" else "round", "brows": True})
ALL = list(cast)


# ---------------------------------------------------------------------------------------------------- cameras
def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return c([0, list(loc), list(tgt), lens])


def move(a, b, la, lb=None):
    return c([0, list(a[0]), list(a[1]), la], [1, list(b[0]), list(b[1]), lb or la])


def yaw_to(a, b):
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


ST = (-12.6, 1.8)      # my station
EM = (-12.6, 2.9)      # the Empty
UN = (-7.75, -1.0)     # Uncle at the counter
UB = (-12.6, -1.8)     # Uncle at his bench
HEAP = (-11.35, 1.75)
FOOT = (-11.72, 0.62)
FRONT = ((-5.0, 0.5, 1.5), (-12.6, 2.2, 1.3), 24)

SHOTS = [
    # 01 the arcade
    (0, "two walkers toward camera", 2, still((0.1, 3.9, 1.5), (0, -2, 1.45), 42)),
    ("L01.2", "wide down the arcade", 2, move(((0.5, 8.0, 1.6), (0, -20, 1.9)), ((0.3, 7.0, 1.6), (0, -20, 1.9)), 26)),
    ("L02", "the shoe man", 2, still((1.0, -4.6, 1.5), (-3.45, -7.1, 1.45), 40)),
    ("L03", "salon pair", 2, still((-2.0, -14.4, 1.5), (-2.0, -11.0, 1.45), 42)),
    ("L03.2", "lilac lapel, tag, door shuts", 2, still((-2.0, -13.4, 1.6), (-2.0, -11.0, 1.4), 60)),
    ("L04", "the date table", 2, still((0.4, -3.0, 1.45), (3.2, -3.0, 1.35), 42)),
    ("L05", "cafe man, sheepish", 2, still((0.4, -5.2, 1.45), (3.2, -5.2, 1.4), 42)),
    ("L05.2", "his chest, the tag drifts", 2, still((1.5, -5.2, 1.4), (3.3, -5.2, 1.2), 60)),
    ("L06", "the cafe claps", 2, still((-0.5, -2.0, 1.6), (3.2, -5.4, 1.4), 30)),
    ("L07", "Mrs. Kettle", 2, still((0.0, -9.0, 1.45), (-0.45, -6, 1.45), 45)),
    ("L08", "her clean lapel", 2, still((0.1, -8.0, 1.3), (0, -6, 1.2), 70)),
    ("L09", "Mr. Kettle, white", 2, move(((0.0, -8.4, 1.4), (0, -6, 1.3)), ((0.0, -10.4, 1.6), (0, -6, 1.3)), 45)),
    ("L10", "me up the arcade", 2, still((0.2, -2.0, 1.5), (0, 5, 1.45), 40)),
    ("L11", "the cafe counter", 2, still((5.2, -3.0, 1.55), (7.3, -4.4, 1.5), 40)),
    # 02 the shop
    ("L12", "the shopfront", 2, still((1.8, 1.5, 1.6), (-4, 0.3, 1.8), 28)),
    ("L12.2", "Uncle at his bench", 2, still((-12.0, 0.2, 1.55), (UB[0], UB[1], 1.35), 40)),
    ("L13", "the train", 2, still((82.2, -2.0, 1.55), (82.0, 0.6, 1.5), 36)),
    ("L14", "boxes, Uncle folding", 2, still((-8.6, 0.3, 1.7), (-6.9, -1.2, 1.4), 32)),
    ("L14.2", "me at the hook", 2, still((-12.2, 0.4, 1.5), (-15.2, -0.3, 1.3), 34)),
    ("L15", "upstairs table", 2, still((44.0, -1.8, 1.6), (42.5, 0.6, 1.4), 38)),
    ("L16", "me, I love it", 2, still((42.3, 0.9, 1.5), (42.5, -0.75, 1.5), 42)),
    ("L17", "my clean sleeve", 2, still((42.1, 0.5, 1.45), (42.5, -0.8, 1.25), 50)),
    ("L18", "Uncle, tea", 2, still((42.5, -1.4, 1.55), (42.5, 0.75, 1.5), 42)),
    ("L19", "the counter, back to camera", 2, still((-9.6, -0.4, 1.65), (-6.2, -1.0, 1.5), 34)),
    ("L19.3", "the bib, a tag", 2, still((-6.3, -1.2, 1.5), (-7.75, -1.0, 1.15), 60)),
    ("L20", "me with a box", 2, still((-12.0, 1.3, 1.5), (-9.8, 0.3, 1.45), 36)),
    ("L21", "Uncle speckled", 2, still((-12.1, 0.1, 1.55), (UB[0], UB[1], 1.3), 42)),
    ("L22", "the teal woman backs out", 2, still((-6.0, 0.9, 1.5), (-4.2, 1.9, 1.4), 28)),
    ("L23", "snow on his shoulders", 2, still((-11.5, -3.2 + 1.4, 2.4), (UB[0], UB[1], 1.6), 40)),
    # 03 traces
    ("L24", "from the stair, the curtain", 2, still((-15.3, 1.3, 1.95), (-14.3, -1.8, 1.3), 30)),
    ("L24.2", "low under the hem", 2, still((-12.8, -1.7, 0.13), (-14.4, -1.7, 0.15), 24)),
    ("L25", "chalk on my bench", 2, still((-12.6, 1.0, 2.3), (-12.6, 1.0, 0.92), 36)),
    ("L26", "the tape on the floor", 2, still((-12.8, 2.3, 2.9), (-12.8, 2.3, 0), 34)),
    ("L27", "low, behind my bench; me scared", 2, still((-13.9, 2.2, 0.4), (-9.8, 0.3, 1.2), 28)),
    # 04 Thursday
    ("L28", "grey shop, nobody", 1, still((-12.0, -0.2, 1.6), (-6.8, -0.6, 1.2), 24)),
    ("L28.1", "the empty stair", 1, still((-14.6, -0.1, 1.2), (-15.4, 2.2, 2.2), 24)),
    ("L29", "his room", 2, still((60.5, -1.5, 1.6), (62.9, 0, 0.6), 28)),
    ("L29.1", "the phone", 2, still((-6.2, -0.1, 1.35), (-6.75, -0.6, 1.07), 40)),
    ("L30", "tape and pincushion", 2, still((-12.2, 0.2, 1.5), (-12.6, 0.95, 0.95), 36)),
    ("L31", "the curtain, shut", 2, still((-12.8, -1.6, 1.4), (-14.3, -1.7, 1.3), 30)),
    ("L32", "shoes under the hem", 2, still((-13.2, -1.7, 0.09), (-14.5, -1.75, 0.2), 28)),
    ("L33", "me looks at my shoes", 2, still((-11.5, -1.4, 1.35), (-13.8, -1.7, 1.25), 34)),
    ("L34", "the rings slide", 2, still((-14.3, -0.95, 2.3), (-14.3, -2.6, 2.5), 35)),
    ("L35", "the suit hangs", 2, still((-12.8, -1.2, 1.5), (-15.55, -1.75, 1.0), 35)),
    ("L35.2", "chalk on the jacket", 2, still((-13.2, -1.3, 1.4), (-15.55, -1.75, 1.2), 42)),
    ("L36", "nobody in it", 2, still((-12.5, -2.2, 1.45), (-14.3, -1.5, 1.3), 34)),
    ("L37", "Uncle comes home", 2, still((-6.0, 0.8, 1.5), (-4.2, 1.9, 1.4), 28)),
    ("L38", "the table, the ticket", 2, still((44.0, -1.8, 1.6), (42.5, 0.7, 1.4), 38)),
    ("L39", "his smile", 2, still((43.2, -1.8, 1.55), (42.5, 0.75, 1.5), 42)),
    ("L40", "the heart tag", 2, still((42.2, -0.4, 1.35), (42.7, 0.75, 1.2), 50)),
    ("L41", "his back at the window", 2, still((42.0, 0.2, 1.5), (44.3, 0.2, 1.4), 30)),
    ("L42", "me in bed", 2, still((60.8, 0.1, 1.5), (62.9, 0, 0.95), 30)),
    ("L42.2", "the dark stairs", 2, still((-15.4, 2.4, 2.3), (-15.4, 0.3, 0.4), 24)),
    ("L43", "the bare hanger", 2, still((-12.8, -1.4, 1.6), (-15.5, -1.75, 1.6), 35)),
    # 05 Friday
    ("L44", "the shop crowded, over Uncle", 2, still((-8.6, -0.2, 1.65), (-5.2, 0.4, 1.5), 28)),
    ("L44.3", "the man with the stick", 2, still((-8.3, 0.0, 1.6), (-5.9, -0.9, 1.5), 40)),
    ("L45", "his collar", 2, still((-6.3, -1.0, 1.65), (UN[0], UN[1], 1.5), 55)),
    ("L45.2", "his collar, another", 2, still((-6.3, -0.8, 1.6), (UN[0], UN[1], 1.5), 60)),
    ("L46", "tags to his chin", 2, still((-5.9, -0.6, 1.55), (UN[0], UN[1], 1.5), 45)),
    ("L47", "something standing", 1, move(((-8.6, 0.3, 1.65), (-12.6, 2.6, 1.2)), ((-8.9, 0.4, 1.65), (-12.6, 2.7, 1.2)), 26)),
    ("L48", "it's the suit", 1, still((-9.4, 2.5, 1.5), (EM[0], EM[1], 1.35), 40)),
    ("L49", "standing, nobody inside", 1, still((-10.4, 2.2, 0.7), (EM[0], EM[1], 1.0), 34)),
    ("L50", "the open collar", 1, still((-12.6, 2.45, 2.25), (EM[0], EM[1], 1.5), 48)),
    ("L51", "wide: both of us bare", 1, still((-7.4, 0.2, 1.55), (-12.0, 1.8, 1.3), 32)),
    ("L52", "sleeves lift", 1, still((-10.6, 1.4, 1.5), (EM[0], 2.3, 1.2), 40)),
    ("L52.3", "the space between its cuffs", 1, still((-11.6, 1.0, 1.4), (EM[0], 2.1, 1.1), 45)),
    ("L53", "it leans, 12", 1, still((-10.6, 0.8, 1.5), (-12.6, 2.2, 1.45), 50)),
    ("L53.2", "it leans, 24", 1, still((-10.7, 0.9, 1.5), (-12.6, 2.2, 1.45), 55)),
    ("L53.3", "35: eyes level with mine", 1, still((-12.0, 0.4, 1.58), (-12.8, 2.3, 1.5), 32)),
    ("L54", "past its shoulder to me; Uncle far behind", 1, still((-13.8, 2.8, 1.55), (-9.0, 0.4, 1.45), 34)),
    ("L55", "Uncle says it", 2, still((-6.0, -0.7, 1.6), (UN[0], UN[1], 1.5), 48)),
    # 06 the truth
    ("L56", "every tag the same lie", 2, move(((-6.0, -0.6, 1.9), (UN[0] + 0.3, UN[1], 1.7)), ((-6.0, -1.4, 1.5), (UN[0], UN[1], 1.2)), 55)),
    ("L57", "he's known", 2, still((-10.0, 0.3, 1.6), (UN[0], UN[1], 1.55), 55)),
    ("L58", "a tag drifts off", 2, still((1.5, -5.2, 1.4), (3.3, -5.2, 1.2), 60)),
    ("L58.3", "me turns from it", 2, still((-9.8, 0.2, 1.6), (-12.0, 1.4, 1.5), 40)),
    ("L59", "this truth is mine", 2, still((-8.9, 0.7, 1.55), (-11.5, 0.5, 1.45), 40)),
    ("L60", "the shop turns to me", 2, still((-8.2, -0.9, 1.7), (-4.9, 0.6, 1.5), 26)),
    ("L60.2", "me, I miss this", 2, still((-12.2, 0.4, 1.55), (-10.0, 0.5, 1.5), 45)),
    ("L61", "the tags fall like snow", 2, still((-5.9, -0.6, 1.55), (UN[0], UN[1], 1.5), 40)),
    ("L62", "I step up to my bench", 2, still((-9.2, 0.6, 1.6), (-11.5, 1.2, 1.45), 36)),
    ("L62.2", "the heap", 2, still((-10.0, 1.1, 0.45), (HEAP[0], HEAP[1], 0.2), 28)),
    ("L63", "I look at my sleeves", 2, still((-12.6, 0.2, 1.6), (ST[0], ST[1], 1.35), 44)),
    ("L64", "Mrs. Kettle again", 2, still((-8.2, -0.6, 1.6), (-5.6, 0.2, 1.45), 34)),
    ("L65", "my sleeve", 2, still((-12.0, 0.2, 1.45), (-12.5, ST[1], 1.25), 40)),
    # 07 the window
    ("L66", "the window seat, gold", 2, still((-2.0, -2.6, 1.25), (-5.0, -0.8, 1.0), 36)),
    ("L67", "clean shirtsleeves", 2, still((-2.6, -1.6, 1.2), (-5.2, -0.8, 1.0), 50)),
    ("L68", "chalk on canvas", 2, still((-12.0, 0.3, 1.6), (-12.6, 1.0, 0.95), 40)),
    ("L68.1", "the tally on the foot", 2, move(((-10.7, -0.1, 0.4), (FOOT[0], FOOT[1], 0.13)), ((-10.9, 0.05, 0.35), (FOOT[0], FOOT[1], 0.13)), 45)),
    ("L69.1", "two aprons", 2, still((-13.0, -0.3, 1.5), (-15.9, -0.3, 1.3), 34)),
    ("L69.3", "turn the sign", 2, still((-6.0, 1.9, 1.6), (-4.3, 1.9, 1.7), 40)),
    ("L70", "Saturday, push in", 2, move(((0.4, 7.0, 1.6), (0, -20, 1.9)), ((-1.5, -0.2, 1.45), (-4.9, -0.4, 1.45)), 26, 34)),
    ("L71", "me at my bench", 2, still((-12.6, 0.2, 1.6), (ST[0], ST[1], 1.45), 44)),
    ("L72", "the fitting room, empty", 2, still((-11.0, -0.9, 1.55), (-15.4, -1.75, 1.3), 30)),
    ("L73", "my sleeve", 4, still((-12.0, 0.2, 1.45), (-12.5, ST[1], 1.25), 40)),
]
def widen(cam):
    return [[k[0], k[1], k[2], (max(20, round(k[3] * 0.68)) if k[3] >= 28 else k[3])] + k[4:] for k in cam]


shots = []
for i, (at, what, step, cam) in enumerate(SHOTS):
    cam = widen(cam)
    s = {"id": f"S{i + 1:02d}", "cam": cam, "hand": 0.0 if step == 4 else 0.006, "step": step, "what": what}
    if i:
        s["at"] = at
    shots.append(s)

# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True, "sit": False}
acting = {n: [] for n in ALL}
for n in ALL:
    acting[n].append({"at": 0, "pos": [0, 40], "hidden": True, "blend": 0})


def put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, "hidden": False, **NEUTRAL, "expr": "neutral", **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": pos, **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def talk(who, a, b):
    acting[who].append({"from": a, "to": b, "mouth": [0.55, 0.55], "flap": True})


def clap(who, a, off=0.0, n=5):
    for k in range(n):
        v = 82 if k % 2 == 0 else 58
        key(who, f"{a}+{off + k * 0.22:.2f}", arms=[v, v], blend=0.1)


def rub(who, a, off=0.0, n=6, base=50):
    """The other sleeve end rubbing my left sleeve (arms swing a little, crossing the body)."""
    for k in range(n):
        v = base + (8 if k % 2 else -8)
        key(who, f"{a}+{off + k * 0.3:.2f}", arms=[base - 20, v], side=[0, -28], blend=0.25)


# 01 the arcade
put("x1", 0, [-0.5, -2.2], yaw=180, expr="smirk")
walk("x1", "L01.2", [-0.5, 1.4])
hide("x1", "L02")
put("x2", 0, [0.5, -2.2], yaw=180, expr="grin")
walk("x2", "L01.2", [0.5, 1.4])
hide("x2", "L02")
talk("x1", 0, "L01.2")
put("x1", "L01.2", [0.8, -3.0], yaw=180, expr="neutral")
walk("x1", "L02", [0.8, -9.0])
for n, (p0, p1) in {"x3": ([-1.5, -6], [-1.0, -2]), "x4": ([1.8, -9], [1.3, -4]), "x5": ([-2.2, -12], [-1.2, -8]),
                    "x6": ([2.2, -14], [2.0, -10])}.items():
    put(n, "L01.2", p0, yaw=180)
    walk(n, "L02", p1)
    hide(n, "L02+0.01")
put("salesman", "L02", [-3.3, -7.1], yaw=90, expr="smirk", arms=[20, 20], side=[-15, -15])
hide("salesman", "L03")
put("salon_a", "L03", [-2.5, -11.0], yaw=20, expr="smirk")
put("salon_b", "L03", [-1.5, -11.0], yaw=-20, expr="grin")
talk("salon_b", "L03", "L03.2")
put("salon_a", "L03.2", [-2.5, -11.0], yaw=20, expr="smirk")
put("salon_b", "L03.2", [-2.0, -11.0], yaw=-15, expr="grin")
hide("salon_a", "L04")
hide("salon_b", "L04")
put("date_m", "L04", [3.4, -2.5], yaw=-70, expr="grin")
put("date_f", "L04", [3.4, -3.5], yaw=-110, expr="grin")
hide("date_m", "L05")
hide("date_f", "L05")
put("cafe_man", "L05", [3.4, -5.0], yaw=-75, expr="worried", head=[0, 10])
put("cafe_f", "L05", [3.4, -5.9], yaw=-100, expr="neutral")
talk("cafe_man", "L05", "L05.2")
put("cafe_man", "L05.2", [3.4, -5.0], yaw=-75, expr="smirk")
put("cafe_f", "L06", [3.3, -6.4], yaw=-110, expr="grin")
put("cafe_man", "L06", [3.3, -4.9], yaw=-80, expr="grin")
put("x1", "L06", [2.7, -2.4], yaw=-90, expr="grin")
put("x2", "L06", [1.9, -3.6], yaw=-60, expr="grin")
put("x3", "L06", [3.4, -3.0], yaw=-110, expr="grin")
for n in ("cafe_man", "cafe_f", "x1", "x2", "x3"):
    clap(n, "L06", 0.2, 6)
hide("cafe_man", "L07")
hide("cafe_f", "L07")
for n in ("x1", "x2", "x3"):
    hide(n, "L07")
put("mrs_kettle", "L07", [-0.45, -6.0], yaw=0, expr="smirk", head=[0, -8], arms=[10, 10])
put("mr_kettle", "L09", [0.45, -6.0], yaw=0, expr="neutral")
put("mrs_kettle", "L09", [-0.45, -6.0], yaw=0, expr="smirk", head=[0, -8], arms=[10, 10])
hide("mrs_kettle", "L10")
hide("mr_kettle", "L10")
put("me", "L10", [0.0, 5.5], yaw=0, expr="neutral")
walk("me", "L11", [0.0, -1.0])
for n, p0, p1 in (("x1", [-1.8, 7], [-1.5, 1]), ("x2", [1.9, 8], [1.6, 2]), ("x3", [1.0, -4], [1.0, 4])):
    put(n, "L10", p0, yaw=0)
    walk(n, "L11", p1)
    hide(n, "L11+0.01")
put("me", "L11", [5.6, -4.2], yaw=90, expr="neutral")
put("x4", "L11", [7.9, -4.3], yaw=-125, expr="smirk", head=[0, 5])
key("x4", "L11.1", head=[0, 14], blend=0.3)
key("x4", "L11.2", head=[0, 4], blend=0.3)
hide("me", "L12")
hide("x4", "L12")
# 02 the shop
put("uncle", "L12", [-3.0, 1.0], yaw=180)           # in the arcade at the shop front, S15 (through the window)
put("uncle", "L12.2", [UB[0], UB[1]], yaw=180, expr="soft", arms=[40, 40])
put("me", "L13", [82.0, 0.5], yaw=0, expr="neutral", head=[0, 6])
rub("me", "L13", 0.3, 7, 55)
hide("uncle", "L13")
hide("me", "L14")
put("uncle", "L14", [-7.9, -1.1], yaw=90, expr="neutral", arms=[55, 55], side=[-10, -10], head=[0, 24])
put("me", "L14.2", [-15.0, -0.3], yaw=-90, expr="neutral", arms=[60, 0])
key("me", "L14.2+0.9", yaw=90, arms=[0, 0], blend=0.4)
hide("uncle", "L14.2")
hide("me", "L15")
put("uncle", "L15", [42.5, 0.8], yaw=0, expr="neutral", head=[0, 5])
put("me", "L15", [42.5, -0.8], yaw=180, expr="neutral")
put("me", "L16", [42.5, -0.8], yaw=180, expr="smirk", arms=[35, 55], side=[0, -22])
rub("me", "L16", 0.1, 5, 55)
hide("uncle", "L16")
put("uncle", "L18", [42.5, 0.8], yaw=0, expr="soft", head=[0, 28])
hide("me", "L18")
hide("uncle", "L19")
put("uncle", "L19", [UN[0], UN[1]], yaw=90, expr="soft", head=[-60, 0])
put("cam", "L19", [-5.7, -1.0], yaw=-90, expr="neutral", head=[0, 8], lean=12)
talk("cam", "L19", "L19.3")
hide("cam", "L20")
put("me", "L20", [-9.8, 0.3], yaw=-60, expr="worried", arms=[60, 60])
put("uncle", "L20", [UN[0], UN[1]], yaw=90, expr="soft")
hide("me", "L21")
hide("uncle", "L21")
put("uncle", "L21", [UB[0], UB[1]], yaw=180, expr="worried", arms=[40, 40])
hide("uncle", "L22")
put("teal", "L22", [-4.5, 1.9], yaw=-90, expr="wide")
walk("teal", "L22+1.2", [-2.6, 1.9], keep_yaw=True)
hide("teal", "L23")
put("uncle", "L23", [UB[0], UB[1]], yaw=0, expr="tired")        # from behind: faces away
# 03 traces
hide("uncle", "L24")
put("me", "L27", [-9.8, 0.3], yaw=-90, expr="scared", head=[0, 6])
hide("me", "L28")
# 04 Thursday
put("me", "L33", [-13.8, -1.7], yaw=90, expr="scared", head=[0, 30])
key("me", "L33+0.8", head=[0, 0], blend=0.4)
put("me", "L36", [-14.1, -0.8], yaw=-90, expr="scared", head=[-70, 0])
hide("me", "L37")
put("uncle", "L37", [-3.2, 1.9], yaw=-90, expr="soft", head=[0, 8])
walk("uncle", "L37+1.0", [-5.4, 1.4])
hide("uncle", "L38")
put("uncle", "L38", [42.5, 0.8], yaw=0, expr="soft", head=[0, 10])
put("me", "L38", [42.5, -0.8], yaw=180, expr="worried")
put("uncle", "L39", [42.5, 0.8], yaw=0, expr="smirk", head=[0, 6])
key("uncle", "L39", look=[0.8, 0.0])
put("uncle", "L41", [44.3, 0.2], yaw=90, expr="worried")
hide("me", "L41")
put("me", "L42", [62.9, 0.0, 0.0], yaw=-90, expr="scared", head=[0, 24])
hide("uncle", "L42")
hide("me", "L42.2")
# 05 Friday
put("uncle", "L44", [UN[0], UN[1]], yaw=90, expr="tired", head=[0, 6])
put("mrs_kettle", "L44", [-5.3, 0.4], yaw=-90, expr="smirk")
put("cam", "L44", [-5.6, 0.0], yaw=-90, expr="neutral")
put("teal", "L44", [-5.3, 1.5], yaw=-90, expr="neutral")
put("stick", "L44", [-5.6, -0.2], yaw=-90, expr="neutral", lean=10)
put("mr_kettle", "L44", [-4.7, 0.5], yaw=-90, expr="neutral")
put("x1", "L44", [-4.8, 1.5], yaw=-90, expr="neutral")
put("x2", "L44", [-4.5, 0.6], yaw=-90, expr="neutral")
put("x3", "L44", [-5.0, -2.0], yaw=-90, expr="smirk")
put("stick", "L44.3", [-6.0, -0.9], yaw=-90, expr="neutral", lean=14)
put("cam", "L44.3", [-5.2, 0.9], yaw=-90)
put("stick", "L45", [-5.6, -1.9], yaw=-90, expr="neutral", lean=8)
put("cam", "L45", [-5.4, 0.6], yaw=-90)
put("uncle", "L55", [UN[0], UN[1]], yaw=90, expr="soft")
put("me", "L47", [-9.8, 0.3], yaw=-90, expr="wide")
hide("me", "L47+0.01")
put("me", "L51", [-9.8, 0.3], yaw=-90, expr="scared")
put("me", "L53", [-13.25, 2.0], yaw=150, expr="scared", head=[-30, 0])

put("me", "L54", [-13.25, 2.0], yaw=150, expr="scared", head=[-30, 0])
put("me", "L58.3", [-11.5, 1.5], yaw=-40, expr="worried", head=[-40, 0])
put("me", "L59", [-10.6, 0.6], yaw=90, expr="worried")
put("me", "L60", [-10.0, 0.5], yaw=90, expr="worried")
put("me", "L60.2", [-10.0, 0.5], yaw=-90, expr="worried", head=[0, 0])
key("me", "L60.2", expr="crying")
talk("me", "L60.2", "L61")
put("me", "L62", [-11.0, 1.0], yaw=90, expr="worried")
walk("me", "L62+0.9", [ST[0], ST[1]])
put("me", "L62.2", [ST[0], ST[1]], yaw=0, expr="worried")
put("me", "L63", [ST[0], ST[1]], yaw=0, expr="worried", head=[0, 30], arms=[40, 40], side=[0, 0])
put("me", "L65", [ST[0], ST[1]], yaw=0, expr="worried", head=[0, 24])
put("uncle", "L56", [UN[0], UN[1]], yaw=90, expr="tired")
key("uncle", "L57", expr="worried", head=[0, 0], look=[0, 0], blend=0.4)
key("uncle", "L61+0.6", expr="soft")
put("uncle", "L61", [UN[0], UN[1]], yaw=90, expr="tired")
key("uncle", "L61+0.8", expr="soft", blend=0.5)
put("mrs_kettle", "L64", [-5.4, 0.3], yaw=-90, expr="smirk", head=[0, -8])
put("mr_kettle", "L64", [-5.3, -0.6], yaw=-90, expr="neutral", head=[20, 0])
put("uncle", "L64", [UN[0], UN[1]], yaw=90, expr="soft")
put("x1", "L60", [-5.0, 1.0], yaw=-90, expr="wide")
put("x3", "L60", [-5.2, -2.0], yaw=-90, expr="wide")
put("teal", "L60", [-4.7, 0.4], yaw=-90, expr="wide")
put("cam", "L60", [-5.6, 0.7], yaw=-90, expr="wide")
for n in ("stick", "x2", "x3", "x1", "teal", "cam", "mr_kettle", "mrs_kettle"):
    hide(n, "L65+0.5") if n not in ("mr_kettle", "mrs_kettle") else None
# 07 the window
hide("me", "L66")
hide("uncle", "L66")
hide("mrs_kettle", "L66")
hide("mr_kettle", "L66")
SEAT = {"yaw": 90, "sit": True}
put("uncle2", "L66", [-5.5, -1.3, -0.01], expr="soft", **SEAT)
put("me2", "L66", [-5.5, -0.3, -0.01], expr="soft", **SEAT)
put("uncle2", "L68", [-12.6, -1.8], yaw=180, expr="soft", arms=[45, 45])
put("me2", "L68", [ST[0] + 0.0, 0.2], yaw=180, expr="soft")
hide("uncle2", "L68.1")
hide("me2", "L68.1")
hide("uncle2", "L69.3")
put("uncle2", "L70", [-5.5, -1.2], yaw=90, expr="soft")
put("me2", "L70", [-5.5, 0.1], yaw=90, expr="soft")
for n, p0, p1 in (("x1", [-1.2, 1], [-1.0, -8]), ("x2", [1.2, 2], [1.4, -9]), ("x3", [-2.5, -3], [-2.0, -12]),
                  ("x4", [0.5, -5], [0.2, -14])):
    put(n, "L70", p0, yaw=180)
    walk(n, "L71", p1)
    hide(n, "L71")
put("me2", "L71", [ST[0], ST[1]], yaw=0, expr="soft", arms=[45, 45], head=[0, 14])
hide("uncle2", "L71")
put("me2", "L72", [-12.9, -0.2], yaw=90, expr="neutral")
put("me2", "L73", [-12.6, 1.8], yaw=0, expr="neutral", arms=[20, 50], side=[0, -28])
rub("me2", "L73", 0.1, 6, 50)

# ---------------------------------------------------------------------------------------------------- cues
cues = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


# the time of day
for at, m in ((0, "day"), ("L24", "night_w"), ("L28", "grey"), ("L37", "up"), ("L43", "grey"), ("L44", "friday"),
              ("L66", "eve"), ("L69.1", "sat")):
    cue(at, "mode", set=m, dur=0.3)
# practicals (every ramp 1 s)
cue(0, "lamp", light="ceiling", on=0.0)
cue("L28", "lamp", light="ceiling", on=1.0, dur=1.0)
cue("L36.1", "lamp", light="ceiling", on=0.0, dur=1.0)
cue(0, "lamp", light="lamp m", on=0.0)
cue("L47", "lamp", light="lamp m", on=1.0, dur=1.0)
cue("L66", "lamp", light="lamp m", on=0.5, dur=1.0)
cue(0, "lamp", light="lamp u", on=0.0)
cue("L66", "lamp", light="lamp u", on=0.5, dur=1.0)
cue("L69.1", "lamp", light="lamp m", on=0.0, dur=1.0)
cue("L69.1", "lamp", light="lamp u", on=0.0, dur=1.0)
# the curtain
cue(0, "curtain", open=1.0)
cue("L24", "curtain", open=0.0, dur=0.3)
cue("L34", "curtain", open=1.0, dur=1.0)
# the Empty: only shadows and traces until L47
cue(0, "empty", hidden=True)
cue("L31", "empty", pose="hang", pos=[-15.55, -1.75], yaw=90)
cue("L43", "empty", hidden=True)
cue("L47", "empty", pose="stand", pos=list(EM), yaw=90)
cue("L52", "empty", pose="sleeves_up", pos=list(EM), yaw=0)
cue("L53", "empty", pose="lean", pos=list(EM), yaw=0, lean=12, tilt=22)
cue("L53.2", "empty", pose="lean", pos=list(EM), yaw=0, lean=24, tilt=40)
cue("L53.3", "empty", pose="lean", pos=list(EM), yaw=0, lean=35, tilt=58)
cue("L62", "empty", pose="lean", pos=list(EM), yaw=0, lean=35, tilt=58)
cue("L62.2", "empty", pose="heap", pos=[-11.35, 1.75], yaw=-40)
cue("L63", "empty", hidden=True)
cue(0, "hanger", on=False)
cue("L31", "hanger", on=True)
cue("L43", "hanger", on=True, swing=1)
cue("L62.2", "hanger", on=False)
# props
for at, n in ((0, 2), ("L14", 3), ("L19", 4), ("L21", 5), ("L24", 6), ("L44", 8)):
    cue(at, "boxes", n=n)
for at, s in ((0, "neck"), ("L26", "outline"), ("L28", "none"), ("L30", "coil"), ("L62.2", "none")):
    cue(at, "tape", state=s)
cue("L30", "pincushion", on=True)
cue("L31", "pincushion", on=False)
cue("L25", "cloth", on=True)
cue("L28", "cloth", on=False)
cue("L68", "canvas", on=True)
cue("L69.1", "canvas", on=False)
cue("L29", "phone", on=True)
cue("L30", "phone", on=False)
cue("L38", "ticket", on=True)
cue("L43", "ticket", on=False)
cue(0, "aprons", n=0)
cue("L69.1", "aprons", n=2)
cue("L69.3", "sign", turn=1.0, dur=0.8)
cue("L22+0.5", "bell")
cue("L44", "bell")
cue("L68.1", "dust")
# tags: kinds start full; the story's own counts follow
for n, kind in (("salesman", 74), ("date_m", 40), ("date_f", 40), ("mr_kettle", 74)):
    cue(0, "tags", who=n, n=kind, pop=False)
for n in ("salon_a", "cafe_f", "cam", "teal", "stick", "x1", "x2", "x3", "x4", "x5", "x6"):
    cue(0, "tags", who=n, n=7, pop=False)
cue(0, "tags", who="salon_b", n=2, pop=False)
cue("L03.2+0.5", "tags", who="salon_b", n=3)
cue(0, "tags", who="cafe_man", n=4, pop=False)
cue("L05.2+0.1", "tags", who="cafe_man", n=3, fall=True)
cue("L58+0.2", "tags", who="cafe_man", n=4, pop=False)
cue("L58+0.5", "tags", who="cafe_man", n=3, fall=True)
cue("L01+1.0", "tags", who="x1", n=8)
cue(0, "tags", who="uncle", n=0, pop=False)
for at, n, pop in (("L12", 3, False), ("L19.3+0.25", 4, True), ("L21", 12, False), ("L23", 30, False), ("L37", 40, False),
                   ("L40+0.35", 41, True), ("L44", 44, False), ("L45+0.4", 47, True), ("L45.2+0.4", 50, True),
                   ("L46", 55, False), ("L55+0.3", 57, True)):
    cue(at, "tags", who="uncle", n=n, pop=pop)
cue("L61", "tags", who="uncle", n=0, fall=True)

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L01+1.0", "kind": "click", "db": -26},
    {"at": "L03.2+0.5", "kind": "click", "db": -26},
    {"at": "L05.2+0.1", "kind": "whoosh", "db": -30, "dur": 1.0},
    {"at": "L06+0.2", "kind": "bubble", "db": -24},
    {"at": "L19.3+0.25", "kind": "click", "db": -26},
    {"at": "L22+0.5", "kind": "bell", "db": -22},
    {"at": "L28", "kind": "click", "db": -16},
    {"at": "L29.1", "kind": "click", "db": -22},
    {"at": "L32", "kind": "creak", "db": -26, "dur": 0.8},
    {"at": "P01+0.1", "kind": "creak", "db": -22, "dur": 0.6, "keep": True},
    {"at": "L34+0.1", "kind": "creak", "db": -22, "dur": 1.0},
    {"at": "L36", "kind": "sting", "db": -18},
    {"at": "L40+0.35", "kind": "click", "db": -26},
    {"at": "L42.1", "kind": "scrape", "db": -20, "dur": 2.0, "distant": True},
    {"at": "L44", "kind": "bell", "db": -22},
    {"at": "L45+0.4", "kind": "click", "db": -26},
    {"at": "L45.2+0.4", "kind": "click", "db": -26},
    {"at": "P02+0.45", "kind": "thud", "db": -10, "keep": True},
    {"at": "L50", "kind": "riser", "db": -22, "dur": 2.0},
    {"at": "L53.3", "kind": "hit", "db": -16},
    {"at": "L55+0.3", "kind": "click", "db": -26},
    {"at": "L61", "kind": "whoosh", "db": -26, "dur": 2.5},
    {"at": "L62.2", "kind": "thud", "db": -18},
    {"at": "L69.3", "kind": "click", "db": -22},
    {"at": "L73>", "kind": "glide", "db": -20, "dur": 1.2},
]
story = {
    "slug": "ep47-fitting-room",
    "title": "In this town, every lie you tell pins a tag to your clothes",
    "made_for_kids": False,
    "premise": "In a town where every lie you tell pins a small white tag to your clothes, I've never had one. I'm back for a week to help Uncle Aurel shut the alterations shop where he taught me to cut. He has never told a lie in his life, but every time a customer asks after me, a tag pins onto him. By night the fitting-room curtain draws itself, my old bench gets chalked up for a suit, and a tape measure lies on the floor in the shape of a person where I used to stand.",
    "twist": "A lie you believe doesn't count. I never had a tag because I believed my own: I love it there. Uncle knew all along, and every tag on him is the same lie, she's happy in the city, told to every customer so I could stay away without guilt. A suit with nobody in it stands in my place until I say the truth out loud and step back up to my bench.",
    "world": "an old covered shopping arcade of bottle-green shopfronts, and a narrow alterations shop with two cutting benches, a fitting-room curtain and a stair",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#7cc4f0",
    "gap": 0.12,
    "tail": 0.25,
    "look": {"fog": "#1c2230", "fog_density": 0.012, "fog_start": 8.0, "sky": "#cfe0ee", "sky_strength": 0.9,
             "exposure": 0.0, "flash_safe": True},
    "grade": {"shadows": [-0.02, 0.0, 0.05], "highlights": [0.03, 0.01, -0.02], "saturation": 0.95, "contrast": 1.06,
              "vignette": 0.3, "bloom": 0.25, "grain": 0.012},
    "phonemes": {"Aurel": "ˈɔɹəl"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 47, "mode": "minor", "bpm": 74, "seed": 47,
              "sections": [
                  {"at": 0, "voices": ["pulse", "piano", "pad"], "energy": 0.35},
                  {"at": "L28", "voices": ["drone", "pad", "pulse"], "energy": 0.5},
                  {"at": "L37", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L44", "voices": ["drone", "pad", "choir", "pulse"], "energy": 0.55},
                  {"at": "L60", "voices": ["drone", "piano", "pad"], "energy": 0.45, "mode": "major", "root": 50},
                  {"at": "L70", "voices": ["drone", "pad"], "energy": 0.3},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [{"kind": "room", "from": 0, "to": "end", "lufs": -36},
                           {"kind": "hum", "from": "L28", "to": "end", "lufs": -40}],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "P01>", "keep": ["creak"]},
                              {"from": "P02", "to": "P02>", "keep": ["thud"]}]},
}
import re


def remap(v):
    if isinstance(v, str):
        m = re.match(r"^(L\d+)\.(\d+)(.*)$", v)
        if m and m.group(1) in IDX:
            return f"{m.group(1)}.{IDX[m.group(1)][int(m.group(2))]}{m.group(3)}"
        return v
    if isinstance(v, list):
        return [remap(x) for x in v]
    if isinstance(v, dict):
        return {k: (remap(x) if k in ("at", "from", "to") else walk_(x)) for k, x in v.items()}
    return v


def walk_(v):
    if isinstance(v, list):
        return [walk_(x) for x in v]
    if isinstance(v, dict):
        return {k: (remap(x) if k in ("at", "from", "to") else walk_(x)) for k, x in v.items()}
    return v


for key_ in ("shots", "acting", "cues", "fx"):
    story[key_] = walk_(story[key_])
story["sound"] = walk_(story["sound"])
story["music"] = walk_(story["music"])
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
