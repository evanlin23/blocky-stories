"""Writes ../story.json for ep40 "night market" (the luck coin, the Half). Run: python stories/ep40-night-market/generator/make_story.py

The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (the mood of the lanterns, the Half, the coins), the sound and the score.

Places (set.py's metres, z up, a character faces -y at yaw 0, +x at 90, +y at 180, -x at -90). The walkway runs along y
between two rows of stalls: the left row's counters front x = -2.2, the right row's x = +2.2. Six stalls a side, centres
y = 2.2 + 2.6 i. Ours is the left row's i = 3 (y 10.0), the noodle stall next door i = 4 (y 12.6), and the stall opposite
ours is the right row's i = 3. The lantern arch is at y = -0.8 (its left pole holds the bell at x = -2.6).
Bea stands behind our counter at (-3.35, 9.45); the spot at her left (+y) where I used to stand is (-3.35, 10.75).
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# silent beats the script plans, as gaps after a line, and the loop cut
GAPS = {"L34": 0.6, "L43": 0.6, "L25": 0.4, "L35": 0.6, "L42": 0.6, "L44": 0.5, "L57": 0.4, "L60": 0.4, "L61": 1.0}
for ln in lines:
    if ln["id"] in GAPS:
        ln["gap"] = GAPS[ln["id"]]
TEMPO = {"L05": 0.93, "L06": 0.95}
SPOKEN = {}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]
    for k, ch in enumerate(ln.get("chunks", [])):
        if (ln["id"], k) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], k)]
lines = lines + [{"id": "P01", "pause": 0.25, "chunks": []}]    # the loop: cut 0.25 s after "SHARED"

# ---------------------------------------------------------------------------------------------------- cast
MUSTARD, SLATE, TEAL = "#d5a32b", "#4a5d7a", "#2d7f7a"


def person(skin, shirt, pants, hair, hair_c, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": "#25262b",
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "hat": "none",
         "face": {"eyes": "round", "brows": True, "ink": "#161012"}}
    d.update(kw)
    return d


cast = {
    "me": person("#e0b48a", SLATE, "#2c2f3a", "cap", "#2e2018", hat="beanie", hat_c=SLATE, extras=["hooddown"], body_width=0.85),
    "me_hood": person("#e0b48a", SLATE, "#2c2f3a", "cap", "#2e2018", hat="hood", hat_c=SLATE, extras=["tie"],
                      extra_c="#1f2a4a", body_width=0.85),
    "me_office": person("#e0b48a", "#f1f1ee", "#34363e", "cap", "#2e2018", collar="#d9d9d6", extras=["tie"],
                        extra_c="#1f2a4a", body_width=0.85),
    "me_apron": person("#e0b48a", "#f1f1ee", "#34363e", "cap", "#2e2018", collar="#d9d9d6", extras=["apron"],
                       extra_c=MUSTARD, body_width=0.85),
    "bea": person("#c98f6a", TEAL, "#2c2f3a", "bun", "#16141a", pattern="knit", pattern_c="#25706c", extras=["apron"],
                  extra_c=MUSTARD, body_width=0.85, face={"eyes": "tired", "brows": True, "ink": "#161012", "bags": True}),
    "noodle": person("#e8b98e", "#f2f0ea", "#3b4a5c", "buzz", "#2a2420", sleeves="short", width=1.3,
                     face={"eyes": "round", "brows": True, "ink": "#161012"}),
    "ca": person("#8c5a3c", "#5f7f45", "#3a3a40", "swoop", "#1c1512", pattern="plaid", pattern_c="#3f5a2e"),
    "cb": person("#f0c8a0", "#8a5a8f", "#303342", "long", "#4a2a1a"),
    "cw": person("#b07a55", "#3d6ea6", "#2a2c34", "cap", "#251a14", extras=["apron"], extra_c="#e8e4d8"),
    "co": person("#d9a67a", "#a33c3c", "#2a2c34", "spiky", "#6b6b70", sleeves="short"),
    "g1": person("#f0c8a0", "#6a3d6e", "#6a3d6e", "swoop", "#3a2a22", pants_pattern="solid"),
    "g2": person("#c98f6a", "#8a8c92", "#8a8c92", "bun", "#2a2420"),
}


# ---------------------------------------------------------------------------------------------------- cameras
def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return c([0, list(loc), list(tgt), lens])


def move(a, b, lens_a, lens_b=None):
    return c([0, list(a[0]), list(a[1]), lens_a], [1, list(b[0]), list(b[1]), lens_b or lens_a])


BEA = (-3.35, 9.45)
SPOT = (-3.35, 10.75)
HALF_SPOT = (-3.35, 10.2)
COIN_Z = 2.1
OPP = (1.5, 10.55)          # the Half at the stall opposite ours, Friday 3 (its eye lands at y about 10.45)
PICNIC = (9.0, 6.0)
BACK = (-11.0, 8.0)
KITCHEN = (20.0, 22.0)
OFFICE = (-20.0, 22.0)
QX = -1.5                   # the queues stand here

BOARD = ((0.9, 10.0, 0.75), (-2.2, 10.0, 0.62), 32)      # the glyph on our front board
STALL_FRONT = still((1.8, 10.0, 1.5), (-3.0, 10.0, 1.75), 27)

SHOTS = [
    ("S01", 0, "Bea, the noodle man and a customer under the lanterns, all looking up, coins in frame",
     move(((1.9, 10.7, 1.4), (-2.4, 10.7, 1.2)), ((1.8, 10.7, 1.42), (-2.4, 10.7, 1.22)), 35, 36)),
    ("S02", "L01.3", "wide from above the arch: every coin flips",
     move(((0.3, -3.6, 4.6), (0.0, 8.0, 1.2)), ((0.3, -3.4, 4.8), (0.0, 8.0, 1.2)), 20)),
    ("S03", "L02", "a customer's coin settling sun, grinning", still((1.6, 7.4, 1.55), (-1.0, 7.4, 1.7), 30)),
    ("S04", "L03", "another settling moon, the woman sighing", still((1.5, 6.9, 1.55), (-0.2, 6.9, 1.75), 30)),
    ("S05", "L04", "picnic table: a man holds out a small box", still((PICNIC[0] - 3.2, PICNIC[1] - 1.7, 1.5), (PICNIC[0], PICNIC[1], 1.55), 30)),
    ("S06", "L04.3", "a worker asks the stall owner, both sun", still((BACK[0], BACK[1] - 3.4, 1.55), (BACK[0], BACK[1], 1.7), 22)),
    ("S07", "L05.1", "the home kitchen, dressing gowns, steaming bowls, two moons", still((KITCHEN[0] + 2.0, KITCHEN[1] - 3.0, 1.45), (KITCHEN[0], KITCHEN[1], 1.5), 28)),
    ("S08", "L06", "the noodle man chest out, his sun gleaming", still((0.2, 12.9, 1.55), (-3.35, 12.6, 1.8), 40)),
    ("S09", "L06.5", "the queue rolling their eyes", still((-3.9, 12.6, 1.55), (-1.4, 12.2, 1.6), 30)),
    ("S10", "L07", "two first daters at a picnic table", still((PICNIC[0] - 4.2, PICNIC[1], 1.55), (PICNIC[0], PICNIC[1], 1.65), 24)),
    ("S11", "L08", "over the shoulder of the crowd: coins landing all round",
     move(((0.9, 1.6, 1.65), (-0.5, 8.5, 2.0)), ((0.9, 2.2, 1.65), (-0.5, 9.1, 2.0)), 28)),
    ("S12", "L09", "me in my hood, a thin gold line", still((-1.1, 10.0, 1.5), (1.0, 10.0, 1.85), 30)),
    ("S13", "L10", "our stall front on, warm", move(((1.9, 10.6, 1.45), (-3.0, 9.9, 1.55)), ((1.5, 10.4, 1.45), (-3.0, 9.8, 1.55)), 24)),
    ("S14", "L11", "the glyph on the front board", still(*BOARD)),
    ("S15", "L12", "me at the grey desk", still((OFFICE[0] + 0.2, OFFICE[1] - 3.2, 1.55), (OFFICE[0], OFFICE[1], 1.5), 30)),
    ("S16", "L13", "Bea alone at the counter, the space at her left empty", still((2.2, 10.0, 1.55), (-3.0, 10.0, 1.6), 27)),
    ("S17", "L14", "close on Bea's coin, moon face", still((-0.9, 9.6, 1.7), (-3.35, 9.45, 2.12), 50)),
    ("S18", "L14.4", "Bea looking up at it, tired", still((0.2, 9.45, 1.5), (-3.35, 9.45, 1.62), 40)),
    ("S19", "L15", "my coin, edge-on, the ridged rim", still((-1.1, 10.0, 1.95), (1.0, 10.0, 2.1), 60)),
    ("S20", "L16", "wide across the car park: me in my hood at the far end", still((-0.3, -3.0, 3.2), (0.0, 7.0, 1.4), 22)),
    ("S21", "L17", "down the left row: the noodle queue snaking back to the arch, all suns", still((0.6, 14.4, 1.75), (-1.2, 2.0, 1.6), 24)),
    ("S22", "L18", "high angle: the queue bending round Bea's stall", still((1.6, 5.0, 5.0), (-1.4, 10.0, 0.8), 28)),
    ("S23", "L18.4", "low angle at Bea's counter, the queue passing behind", still((0.0, 8.0, 0.6), (-3.2, 9.6, 1.1), 28)),
    ("S24", "L19", "a man stops at her stall, looks up at her coin, walks out", still((-0.9, 7.5, 1.7), (-2.2, 9.6, 1.9), 32)),
    ("S25", "L20", "Bea folding, steam across her face", still((0.2, 9.0, 1.55), (-3.35, 9.45, 1.9), 45)),
    ("S26", "L20.2", "next door the noodle man's empty pot, him whistling", still((0.4, 13.0, 1.45), (-3.0, 12.6, 1.3), 32)),
    ("S27", "L21", "Bea's moon turning slowly as it rocks", still((-0.6, 10.3, 1.7), (-3.35, 9.45, 2.12), 55)),
    ("S28", "L22", "me across the car park, the gold line", still((0.3, 10.8, 1.8), (0.0, 17.0, 2.0), 70)),
    ("S29", "L23", "long lens: under the arch, a figure side on", still((-2.0, -0.6, 1.5), (0.9, -0.6, 1.4), 45)),
    ("S30", "L24", "closer, a customer in a red jacket, it looks whole", still((-2.0, -0.6, 1.55), (0.9, -0.6, 1.55), 62)),
    ("S31", "L25", "tilt up over its head: empty air, every head round it has a coin",
     c([0, [-1.7, -0.9, 1.1], [0.9, -0.6, 1.2], 38], [1, [-1.7, -0.9, 1.1], [0.9, -0.6, 2.35], 38])),
    ("S32", "L26", "Bea packing up steamers, talking without looking at me", still((2.2, 10.0, 1.55), (-3.0, 10.0, 1.6), 27)),
    ("S33", "L27", "me under the arch, hood up", still((0.3, 2.2, 1.5), (-0.9, -0.4, 1.45), 30)),
    ("S34", "L28", "the left row from my side: the figure three stalls nearer", still((-2.0, 7.2, 1.5), (0.9, 7.2, 1.4), 38)),
    ("S35", "L29", "reverse: its side profile, its one eye toward our stall", still((-1.35, 7.2, 1.6), (0.9, 7.2, 1.6), 42)),
    ("S36", "L30", "low insert: three shadows, the middle one half as wide", still((0.9, 2.0, 0.7), (0.9, 5.8, 0.0), 22)),
    ("S37", "L31", "the noodle man shouting at his queue", still((-0.9, 12.7, 1.7), (-3.35, 12.6, 1.75), 35)),
    ("S38", "L32", "me at Bea's counter, the only one", still((0.5, 8.3, 1.5), (-2.4, 9.55, 1.4), 30)),
    ("S39", "L33", "over my shoulder to the stall opposite: the figure at its counter", still((-2.2, 9.95, 1.65), (3.0, 10.5, 1.3), 30)),
    ("S40", "L34", "closer: it has turned front on", still((-0.3, 10.55, 1.45), (1.5, 10.5, 1.4), 34)),
    ("S41", "L35", "front on, full figure: only the left half", still((-1.9, 10.55, 1.2), (1.5, 10.5, 0.9), 27)),
    ("S42", "L36", "close on its half face: one eye, half a smile", still((0.1, 10.5, 1.65), (1.5, 10.5, 1.62), 42)),
    ("S43", "L36.2", "its one arm hanging at its side", still((-1.6, 9.6, 1.2), (1.5, 10.3, 0.9), 26)),
    ("S44", "L37.2", "three-quarter on the flat indigo plane", still((-0.2, 12.6, 1.4), (1.5, 10.55, 1.1), 28)),
    ("S45", "L38", "its POV: across to our stall, Bea, the empty space", still((1.45, 10.45, 1.55), (-3.35, 10.0, 1.3), 30)),
    ("S46", "L39", "the iron bell on the arch pole swinging", still((-2.9, -3.3, 2.2), (-2.2, -0.8, 2.4), 28)),
    ("S47", "L40", "wide down the row: the lanterns fading", still((0.0, -1.6, 1.95), (0.0, 10.0, 2.1), 26)),
    ("S48", "L41", "near dark: Bea's face in cool fill", still((0.2, 9.45, 1.5), (-3.35, 9.45, 1.58), 46)),
    ("S49", "L42", "same frame, the sound stops", still((0.2, 9.45, 1.5), (-3.35, 9.45, 1.58), 46)),
    ("S50", "L43", "the lanterns fading back up over our stall", still((1.8, 10.0, 1.5), (-3.0, 10.0, 1.75), 27)),
    ("S51", "L44", "front on our stall: the Half behind our counter. Scare", still((1.5, 10.1, 1.5), (-3.2, 10.1, 1.65), 32)),
    ("S52", "L45", "close two-shot: its flat side a hand's width from Bea's shoulder", still((0.3, 9.95, 1.55), (-3.35, 9.95, 1.5), 26)),
    ("S53", "L46", "wide: Bea and the Half filling the stall like two stallholders", still((2.0, 10.1, 1.45), (-3.3, 10.1, 1.35), 24)),
    ("S54", "L47", "Bea, very still, her eyes sliding toward me", still((0.0, 9.45, 1.6), (-3.35, 9.45, 1.6), 46)),
    ("S55", "L48", "the glyph on the front board", still(*BOARD)),
    ("S56", "L49", "tilt up from Bea to her moon coin", c([0, [0.2, 9.45, 1.2], [-3.35, 9.45, 1.4], 42], [1, [0.2, 9.45, 1.2], [-3.35, 9.45, 2.2], 42])),
    ("S57", "L50", "tilt up from me to my gold line", c([0, [-2.6, 7.2, 1.1], [-1.5, 8.5, 1.4], 38], [1, [-2.6, 7.2, 1.1], [-1.5, 8.5, 2.2], 38])),
    ("S58", "L51", "both coins in one frame", still((0.9, 9.5, 2.0), (-2.5, 9.0, 2.05), 38)),
    ("S59", "L52", "me, the realisation landing", still((-2.4, 7.0, 1.65), (-1.5, 8.5, 1.65), 26)),
    ("S60", "L53", "Bea's moon coin, alone", still((-0.4, 9.9, 2.3), (-3.35, 9.45, 2.12), 60)),
    ("S61", "L54", "my coin on its edge, alone", still((-3.2, 7.3, 2.2), (-1.5, 8.5, 2.1), 60)),
    ("S62", "L55", "me walking round the end of the counter", still((-0.4, 13.3, 1.5), (-2.7, 10.9, 1.2), 28)),
    ("S63", "L56", "behind the counter: I step into the spot, the Half gone", still((-4.2, 10.0, 1.6), (-2.5, 10.5, 1.35), 22)),
    ("S64", "L57", "front on our stall: just Bea and me", still((1.6, 10.1, 1.5), (-3.3, 10.1, 1.5), 30)),
    ("S65", "L58", "wide from above the arch: every coin flips",
     move(((0.3, -3.6, 4.6), (0.0, 8.0, 1.2)), ((0.3, -3.4, 4.8), (0.0, 8.0, 1.2)), 20)),
    ("S66", "L59", "two-shot from below: Bea and me side by side, a coin over each head, spinning in step",
     still((0.2, 10.1, 0.9), (-3.35, 10.1, 1.95), 22)),
    ("S67", "L59.2", "wider two-shot: both coins settle on the same frame, a head apart, never touching",
     still((0.8, 10.1, 1.2), (-3.35, 10.1, 1.9), 18)),
    ("S68", "L60", "both sun faces up; Bea's face lifts", still((0.4, 10.1, 1.65), (-3.35, 10.1, 1.9), 22)),
    ("S69", "L61", "low under the counter, the apron off the shelf", still((-3.9, 9.0, 0.6), (-2.7, 9.6, 0.5), 30)),
    ("S70", "L61.3", "the float tin on the shelf, the two indigo strokes", still((-3.5, 10.2, 0.9), (-2.78, 10.2, 0.55), 35)),
    ("S71", "L62", "Bea and me folding side by side, she bumps my elbow", still((1.4, 10.1, 1.5), (-3.3, 10.1, 1.4), 32)),
    ("S72", "L63", "the noodle man looking up at his moon, pulling a face", still((0.9, 12.6, 1.55), (-3.35, 12.6, 1.75), 40)),
    ("S73", "L64", "next Friday: our queue to the arch, two sun coins over two heads",
     move(((2.4, 12.5, 5.2), (-1.6, 4.0, 1.0)), ((2.4, 12.5, 5.2), (-1.6, 4.2, 1.0)), 24)),
    ("S74", "L64.3", "long lens down the queue: at the very back a customer side on, empty air over its head",
     still((1.8, 9.0, 3.4), (-1.5, -1.7, 1.5), 85)),
    ("S75", "L65", "slow push in on it: the one eye toward our stall",
     move(((1.8, 9.2, 2.7), (-1.5, -1.7, 1.5)), ((1.8, 8.2, 2.3), (-1.5, -1.7, 1.55)), 100)),
    ("S76", "L66", "hold on it, side on, still", still((1.8, 8.2, 2.3), (-1.5, -1.7, 1.55), 100)),
]

shots = []
for i, (sid, at, what, cam) in enumerate(SHOTS):
    s = {"id": sid, "cam": cam, "hand": 0.004, "step": 2, "what": what}
    if sid in ("S51", "S52", "S53", "S54"):
        s["step"] = 1
    if i:
        s["at"] = at
    shots.append(s)

# ---------------------------------------------------------------------------------------------------- acting
AT = {sh["id"]: sh.get("at", 0) for sh in shots}


def R(at):
    """A shot id (S12, S12+0.4) becomes the time reference of its cut."""
    if isinstance(at, str) and at[:1] == "S" and at[1:3].isdigit():
        base, off = at[:3], at[3:]
        a = AT[base]
        return a if (not off and a == 0) else (f"{a}{off}" if isinstance(a, str) else a + (float(off) if off else 0))
    return at


NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True, "look": [0, 0]}
acting = {k: [] for k in cast}


def put(who, at, pos, **kw):
    at = R(at)
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, "hidden": False, **NEUTRAL, "expr": "neutral", **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": R(at), "pos": pos, **kw})


def key(who, at, **kw):
    acting[who].append({"at": R(at), **kw})


def hide(who, at):
    acting[who].append({"at": R(at), "hidden": True, "blend": 0})


def talk(who, a, b, amt=0.55):
    acting[who].append({"from": R(a), "to": R(b), "mouth": [amt, amt], "flap": True})


UP = [0, -22]
X_ = 90       # facing +x (toward the walkway from a stall)
MX = -90      # facing -x (toward a counter)
FY = 180      # facing +y
for w in cast:
    hide(w, 0)

# Bea: behind our counter all film (S01 she stands a little nearer the middle of the stall)
put("bea", "S01", [-3.35, 9.95], yaw=X_, head=UP)
put("bea", "S02", list(BEA), yaw=X_)
put("bea", "S13", list(BEA), yaw=X_, head=[0, 8])
put("bea", "S16", list(BEA), yaw=X_, head=[0, 6], expr="soft")
put("bea", "S17", list(BEA), yaw=X_, head=[0, -10])
put("bea", "S18", list(BEA), yaw=X_, expr="worried", head=[0, -26])
put("bea", "S20", list(BEA), yaw=X_)
put("bea", "S22", list(BEA), yaw=X_, head=[0, 10])
put("bea", "S24", list(BEA), yaw=X_, head=[0, 8])
put("bea", "S25", list(BEA), yaw=X_, head=[-6, 24])
put("bea", "S27", list(BEA), yaw=X_, head=[0, -14])
put("bea", "S32", list(BEA), yaw=X_, head=[0, 10], expr="soft")
talk("bea", "S32", "S33")
put("bea", "S38", list(BEA), yaw=X_, head=[0, 8])
put("bea", "S45", list(BEA), yaw=X_)
put("bea", "S48", list(BEA), yaw=X_, head=[0, 22])
put("bea", "S51", list(BEA), yaw=X_, head=[0, 6])
put("bea", "S54", list(BEA), yaw=X_, expr="worried")
key("bea", "S54+0.5", look=[0.9, 0.0], blend=0.6)
put("bea", "S56", list(BEA), yaw=X_, expr="worried", head=[0, -10])
put("bea", "S57", list(BEA), yaw=X_, expr="worried")
put("bea", "S64", list(BEA), yaw=X_, expr="soft")
put("bea", "S66", list(BEA), yaw=X_, expr="soft", head=[0, -22])
put("bea", "S68", list(BEA), yaw=X_, expr="grin", head=[0, -24])
hide("bea", "S69")
put("bea", "S71", list(BEA), yaw=X_, expr="grin", head=[0, 10])
key("bea", "S71+0.5", side=[0, 18], blend=0.2)
key("bea", "S71+0.8", side=[0, 0], blend=0.25)
put("bea", "S73", list(BEA), yaw=X_, expr="grin")

# the noodle man: at his pot all film
put("noodle", "S01", [-3.35, 11.6], yaw=X_, head=UP, expr="grin")
put("noodle", "S02", [-3.35, 12.6], yaw=X_, expr="grin")
put("noodle", "S08", [-3.35, 12.6], yaw=X_, lean=-6, arms=[20, 0], expr="grin", head=[0, -8])
hide("noodle", "S09")
put("noodle", "S13", [-3.35, 12.6], yaw=X_, expr="grin")
put("noodle", "S26", [-3.35, 12.6], yaw=X_, expr="grin")
talk("noodle", "S26", "S27", 0.25)
put("noodle", "S37", [-3.35, 12.6], yaw=X_, lean=-8, arms=[30, 30], expr="grin", head=[0, -6])
talk("noodle", "S37", "S38", 0.7)
put("noodle", "S41", [-3.35, 12.6], yaw=X_, expr="grin")
put("noodle", "S72", [-3.35, 12.6], yaw=X_, expr="worried", head=[0, -22])
key("noodle", "S72+0.7", expr="angry", blend=0.3)

# me
put("me", "S12", [1.0, 10.0], yaw=MX, expr="worried")
hide("me", "S13")
put("me", "S16", [-1.5, 10.6], yaw=50, expr="soft", arms=[40, 40], head=[0, 8])
hide("me", "S17")
put("me", "S19", [1.0, 10.0], yaw=MX, expr="worried")
hide("me", "S20")
put("me_hood", "S20", [0.0, 6.0], yaw=0, expr="worried")
hide("me_hood", "S21")
put("me", "S28", [0.0, 17.0], yaw=0, expr="worried")
hide("me", "S29")
put("me", "S32", [-1.5, 10.6], yaw=50, expr="soft")
hide("me", "S33")
put("me_hood", "S33", [-0.9, -0.4], yaw=FY, expr="worried", head=[0, 4])
hide("me_hood", "S34")
put("me", "S38", [-1.5, 9.45], yaw=MX, expr="worried")
put("me", "S40", [-1.5, 9.45], yaw=MX, expr="scared")
hide("me", "S41")
put("me", "S45", [-1.5, 8.5], yaw=MX, expr="scared")
put("me", "S54", [-1.5, 8.5], yaw=MX, expr="terrified")
put("me", "S56", [-1.5, 8.5], yaw=MX, expr="wide")
put("me", "S62", [-1.6, 11.9], yaw=-130, expr="scared")
walk("me", "S62+0.5", [-2.5, 11.55], expr="scared")
walk("me", "S63-0.05", [-3.35, 11.0], expr="scared")
put("me", "S63", list(SPOT), yaw=X_, expr="wide")
put("me", "S64", list(SPOT), yaw=X_, expr="soft")
put("me", "S66", list(SPOT), yaw=X_, expr="soft", head=[0, -22])
put("me", "S68", list(SPOT), yaw=X_, expr="soft", head=[0, -24])
hide("me", "S69")
put("me_office", "S15", [OFFICE[0], OFFICE[1]], yaw=0, expr="blank", head=[0, 8])
hide("me_office", "S16")
put("me_apron", "S71", list(SPOT), yaw=X_, expr="grin", head=[0, 10])
put("me_apron", "S73", list(SPOT), yaw=X_, expr="grin")

# the extras (reused bodies)
put("ca", "S01", [-1.7, 10.75], yaw=X_, head=UP, expr="worried")
hide("ca", "S02")
put("ca", "S03", [-1.0, 7.4], yaw=X_, head=UP, expr="grin")
key("ca", "S03+0.6", head=[0, -14])
hide("ca", "S04")
put("ca", "S05", [PICNIC[0], PICNIC[1] - 0.7], yaw=FY, arms=[62, 62], expr="grin")
hide("ca", "S06")
put("ca", "S09", [QX, 12.0], yaw=MX, expr="blank", head=[0, -10])
hide("ca", "S10")
put("ca", "S10", [PICNIC[0], PICNIC[1] - 0.7], yaw=FY, expr="worried", head=UP)
walk("ca", "S10+1.0", [PICNIC[0] - 1.5, PICNIC[1] - 1.6])
hide("ca", "S11")
put("ca", "S24", [-1.6, 9.45], yaw=MX, head=[0, -24])
walk("ca", "S24+0.9", [-1.2, 9.45], head=[0, -24])
walk("ca", "S24+1.6", [-1.0, 13.0], head=[0, 0])
hide("ca", "S25")
put("ca", "S36", [-0.2, 7.2], yaw=FY)
hide("ca", "S37")

put("cb", "S04", [-0.2, 6.9], yaw=X_, head=UP, expr="worried")
key("cb", "S04+0.8", head=[0, 6], expr="squeeze", blend=0.5)
hide("cb", "S05")
put("cb", "S05", [PICNIC[0], PICNIC[1] + 0.7], yaw=0, expr="wide")
hide("cb", "S06")
put("cb", "S09", [QX, 12.9], yaw=MX, expr="smirk")
hide("cb", "S10")
put("cb", "S10", [PICNIC[0], PICNIC[1] + 0.7], yaw=0, expr="worried", head=UP)
hide("cb", "S11")
put("cb", "S36", [2.0, 7.2], yaw=FY)
hide("cb", "S37")

put("cw", "S06", [BACK[0] - 0.6, BACK[1]], yaw=X_, arms=[20, 20], expr="worried")
hide("cw", "S07")
put("co", "S06", [BACK[0] + 0.6, BACK[1]], yaw=MX, expr="grin")
key("co", "S06+0.9", head=[0, 12], blend=0.3)
hide("co", "S07")
put("g1", "S07", [KITCHEN[0] - 0.7, KITCHEN[1]], yaw=X_, expr="soft")
hide("g1", "S08")
put("g1", "S09", [QX, 13.8], yaw=MX, expr="blank", head=[0, -8])
hide("g1", "S10")
put("g2", "S07", [KITCHEN[0] + 0.7, KITCHEN[1]], yaw=MX, expr="soft")
hide("g2", "S08")

# ---------------------------------------------------------------------------------------------------- cues
# set.py reads: mood (the lanterns' level, 1 = full), half (where the creature stands), coin faces, flips, queues
cues = [
    {"at": 0, "name": "mood", "to": 1.0, "dur": 0.1},
    {"at": "L22", "name": "mood", "to": 0.55, "dur": 1.6},          # darker and cooler from L23
    {"at": "L40", "name": "mood", "to": 0.15, "dur": 1.2},          # the bell dim: down over 1.2 s
    {"at": "L43", "name": "mood", "to": 0.55, "dur": 1.2},          # and back up over 1.2 s
    {"at": "L57+0.3", "name": "mood", "to": 1.0, "dur": 1.6},       # warm and full again from L58
    {"at": "L01.3", "name": "flip", "dur": 2.6, "turns": 1.5},      # every coin flips at midnight
    {"at": "L58", "name": "flip", "dur": 2.6, "turns": 1.5, "last": True},
    {"at": "L59", "name": "spin", "dur": 2.4},                      # Bea's coin and mine spin in step, then both land sun up
    {"at": "L39", "name": "bell", "dur": 3.0},
    # the Half: found where it already stands, never seen moving
    {"at": 0, "name": "half", "on": False},
    {"at": "L23", "name": "half", "on": True, "pos": [0.9, -0.6], "yaw": FY},
    {"at": "L28", "name": "half", "on": True, "pos": [0.9, 7.2], "yaw": FY},
    {"at": "L33", "name": "half", "on": True, "pos": [1.5, 10.55], "yaw": FY},
    {"at": "L34", "name": "half", "on": True, "pos": [1.5, 10.55], "yaw": MX},
    {"at": "L38", "name": "half", "on": False},
    {"at": "L39", "name": "half", "on": True, "pos": [1.5, 10.55], "yaw": MX},
    {"at": "L44", "name": "half", "on": True, "pos": list(HALF_SPOT), "yaw": X_},

    {"at": "L56", "name": "half", "on": False},
    {"at": "L64.3", "name": "queue", "which": "ours_gap"},
    {"at": "L64.3", "name": "half", "on": True, "pos": [-1.5, -1.7], "yaw": 100},
    # which stall's queue the extras make: the noodle queue (14), then ours
    {"at": 0, "name": "queue", "which": "far"},                       # the queue's bend stays out of the cameras' way
    {"at": R("S21"), "name": "queue", "which": "noodle"},
    {"at": R("S25"), "name": "queue", "which": "far"},
    {"at": "L64", "name": "queue", "which": "ours"},
    {"at": R("S36"), "name": "shadow_light", "on": True},
    {"at": R("S37"), "name": "shadow_light", "on": False},
]

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L01.3", "kind": "riser", "db": -22, "dur": 1.6},                  # the soft rising shimmer of a flip
    {"at": "L08", "kind": "whoosh", "db": -28, "dur": 0.8},
    {"at": "L25", "kind": "sting", "db": -26},
    {"at": "L35", "kind": "sting", "db": -10},                               # only HALF of it (after the drop)
    {"at": "L39", "kind": "bell", "db": -12},                                # the midnight bell, long fall
    {"at": "L40", "kind": "hum_sweep", "db": -26, "dur": 1.4},
    {"at": "L41+0.3", "kind": "knock", "pattern": [0.0, 0.28, 0.56, 0.84], "tone": "hand", "db": -18},
    {"at": "L44", "kind": "hit", "db": -6},                                  # the scare, after the drop
    {"at": "L58", "kind": "riser", "db": -22, "dur": 1.8},
    {"at": "L59+2.3", "kind": "bell", "db": -27},                            # a soft double chime as both coins settle
    {"at": "L59+2.5", "kind": "bell", "db": -29},
]

story = {
    "slug": "ep40-night-market",
    "title": "In this town, a coin over your head decides your luck",
    "made_for_kids": False,
    "premise": "In a town where a gold coin floats over every head and flips at midnight to decide your luck, my sister Bea keeps our dumpling stall at the Friday night market alone since I took an office job. Her coin lands on the moon every night, the queues bend round her stall, and mine stands on its edge. Over three Fridays a customer with no coin comes one stall nearer, until it stands behind our counter, beside Bea. When I step in beside her, both our coins land sun side up, and next Friday it is waiting at the back of our queue.",
    "twist": "Bea's coin and mine are the two sides of one coin, the stall's coin, and it only lands when two people stand behind the counter. With only Bea back there it can only show her moon, and my sun side, out front with the customers, has nothing to land on. When I step behind the counter both coins spin in step and land sun up, still two coins over two heads. The stall's coin needs two heads and doesn't care whose.",
    "world": "an open-air car park night market on a wet Friday: two facing rows of striped-awning food stalls under strings of paper lanterns, and an arch of lanterns where the market begins",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#b49cff",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#1a2030", "fog_density": 0.04, "fog_start": 5.0, "sky": "#0e1220", "sky_strength": 1.0,
             "exposure": 1.2, "flash_safe": True},
    "grade": {"shadows": [-0.01, 0.0, 0.05], "highlights": [0.04, 0.012, -0.03], "saturation": 1.0, "contrast": 1.06,
              "vignette": 0.35, "bloom": 0.3, "grain": 0.012},
    "phonemes": {"Bea": "bˈiːɐ", "queue": "kjˈu"},
    "equal_coins": ["S58"],
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    # E Dorian, 100 bpm: a plucked tune over a hand drum and a low drone; the tune thins after L12; both voices
    # return, and the mode lifts, from L58
    "music": {"root": 40, "mode": "dorian", "bpm": 100, "seed": 40,
              "sections": [
                  {"at": 0, "voices": ["drone", "pulse", "piano"], "energy": 0.55},
                  {"at": "L12", "voices": ["drone", "pulse"], "energy": 0.4},
                  {"at": "L23", "voices": ["drone", "pad"], "energy": 0.35},
                  {"at": "L34", "voices": ["drone", "pad", "choir"], "energy": 0.45},
                  {"at": "L44", "voices": ["drone"], "energy": 0.25},
                  {"at": "L47", "voices": ["drone", "pad", "choir"], "energy": 0.5},
                  {"at": "L58", "voices": ["piano", "pulse", "pad"], "energy": 0.6, "mode": "major", "root": 40},
                  {"at": "L64.3", "voices": ["drone"], "energy": 0.2},
              ]},
    "sound": {"floor": "stone", "steps_db": -24,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "end", "lufs": -34},
                  {"kind": "hum", "from": "L23", "to": "L58", "lufs": -42},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "L35-0.6", "to": "L35.1", "keep": ["sting"]},
                              {"from": "L44-0.6", "to": "L44+0.5", "keep": ["hit"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
