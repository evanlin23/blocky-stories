"""Writes ../story.json for ep31 "Dawn Flight" (redo, script 2026-11-02).

Run from anywhere: python stories/ep31-dawn-flight/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (the day, the roars, the seams, the plants), the score and the sound.
Places are set.py's metres: the basket's floor centre is the origin, the sun is east (+x), a character with yaw 0
faces -y, yaw 90 faces +x, yaw 180 faces +y (north). Dad and I stand at the north rim, hands on the two worn patches.
The camera's lens is chosen from a wanted frame width W at the target (lens = distance x 13.5 / W).
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# ---------------------------------------------------------------------------------------------------- lines
out_lines = []
for ln in lines:
    out_lines.append(ln)
    if ln["id"] == "L27":
        out_lines.append({"id": "P01", "pause": 0.8, "chunks": []})
lines = out_lines

# ---------------------------------------------------------------------------------------------------- cast
BW = 0.78
SEAMS = {"seams": True, "body_width": BW, "width": 0.86}


def person(skin, shirt, pants, shoes="#2a2420", hair="cap", hair_c="#2a1d15", hat="none", hat_c="#333333", pattern="solid",
           pattern_c="#202020", collar=None, extras=(), extra_c="#20242c", height=1.0, face=None, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c, "height": height,
         "face": face or {"eyes": "round", "brows": True, "ink": "#161012"}, **SEAMS}
    if pattern != "solid":
        d["pattern_c"] = pattern_c
    if collar:
        d["collar"] = collar
    if extras:
        d["extras"] = list(extras)
        d["extra_c"] = extra_c
    d.update(kw)
    return d


cast = {
    # me: a mustard knit jumper under a navy gilet, a grey beanie; the finger-wide gaps
    "me": person("#d9a77f", "#d9a21b", "#26282e", "#3a3a3c", "cap", "#1e1714", "beanie", "#8a8d92", "knit", "#b8860f",
                 "#caa020", height=0.95, vest="#1f2c4a", seam=2.5),
    # Dad: waxed bottle-green jacket, cream and brown check scarf with the balloon badge, grey hair
    "dad": person("#e8bf99", "#2c4a38", "#3a3630", "#2a2420", "cap", "#9a9a9c", "none", "#333333", "solid", "#202020",
                  "#243d2e", extras=("scarf", "badge"), extra_c="#d6c49a", height=1.05,
                  face={"eyes": "round", "brows": True, "ink": "#1a1214", "bags": True}),
    # Rosa: cream fleece, burgundy beanie, black gloves
    "rosa": person("#8a5a44", "#e6dcc4", "#2b2d33", "#1c1c1e", "bun", "#1a1210", "beanie", "#7a2434", "knit", "#cfc4a8",
                   "#d4c8ac", height=0.93, face={"eyes": "round", "brows": True, "ink": "#140e0e"}),
    # the montage extras
    "groom": person("#d9a77f", "#1f2c4a", "#1f2c4a", "#1a1a1c", "cap", "#3a2a20", height=1.02),
    "bride": person("#e8bf99", "#efe4cc", "#efe4cc", "#d8d2c4", "long", "#5a3a22", height=0.94),
    "son": person("#c98f66", "#6a7a8a", "#2c2e36", "#d8d2c4", "spiky", "#1e1714", height=1.0),
    "mum": person("#e8bf99", "#8a3a4a", "#3a3630", "#2a2420", "bun", "#b8b8b8", height=0.93),
    "grandad": person("#e8bf99", "#6a4a32", "#3a3630", "#2a2420", "buzz", "#d8d8d8", "none", "#333333", "knit", "#5a3c28",
                      height=0.97, face={"eyes": "round", "brows": True, "ink": "#1a1214", "bags": True}),
    "rel1": person("#c98f66", "#3a6a8a", "#2c2e36", hair="cap", hair_c="#1e1714", height=1.0),
    "rel2": person("#e8bf99", "#a8453a", "#3a3630", hair="long", hair_c="#7a4a22", height=0.92),
    "rel3": person("#8a5a44", "#d8c8a0", "#2b2d33", hair="cap", hair_c="#1a1210", height=1.02),
    "rel4": person("#e8bf99", "#4a7a4a", "#3a3630", hair="bun", hair_c="#c8a060", height=0.95),
    "rel5": person("#d9a77f", "#5a4a7a", "#2c2e36", hair="swoop", hair_c="#3a2a20", height=0.9),
}
for k in ("groom", "bride", "son", "mum", "grandad", "rel1", "rel2", "rel3", "rel4", "rel5"):
    cast[k]["seam"] = 0.5
cast["dad"]["seam"] = 0.5
cast["rosa"]["seam"] = 0.5
cast["son"]["rattle"] = 1.0


# ---------------------------------------------------------------------------------------------------- camera helpers
def c(*keys):
    return [list(k) for k in keys]


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def lens(loc, tgt, W):
    return round(dist(loc, tgt) * 13.5 / W, 1)


def view(loc, tgt, W):
    return c([0, list(loc), list(tgt), lens(loc, tgt, W)])


def push(loc0, loc1, tgt0, tgt1, W0, W1):
    return c([0, list(loc0), list(tgt0), lens(loc0, tgt0, W0)], [1, list(loc1), list(tgt1), lens(loc1, tgt1, W1)])


def fwd(yaw):
    return (math.sin(math.radians(yaw)), -math.cos(math.radians(yaw)))


def facecam(pos, yaw, d, ang, W, h=0.0, hz=1.5, z0=0.0, ch=None):
    """A camera d metres out in front of a face (along yaw + ang), at the face's height (+ h), looking at it."""
    fx, fy = fwd(yaw + ang)
    tgt = [pos[0], pos[1], z0 + hz]
    loc = [pos[0] + fx * d, pos[1] + fy * d, z0 + (hz if ch is None else ch) + h]
    return view(loc, tgt, W)


def add(a, b):
    return [a[i] + b[i] for i in range(3)]


# ---------------------------------------------------------------------------------------------------- places
HERE_H = {"me": 0.95, "dad": 1.05, "rosa": 0.93}
DAD = (-0.47, 0.63)
ME = (0.47, 0.71)
ROSA = (0.0, -0.78)
FG = -0.55
K0 = -300.0
GATE = (40.0, 0.0, -300.0)
LANE = (120.0, 0.0, -300.0)
TRAILER = (160.0, 0.0, -300.0)
RH = 1.22                       # the rim's top


def head_z(who, k=1.5, hg=0.025, bg=0.025):
    """z (m) of the middle of the gap between head slice k-1 and k, for a character with these gaps (cm /100)."""
    h = HERE_H[who]
    return round(0.34 * 4.02 * h + 0.34 * 0.3 * k * h + bg + (k - 0.5) * hg, 3)


def on_field(x, y):
    return [x, y, FG]


# ---------------------------------------------------------------------------------------------------- shots
# (at, what, camera, step, extras)
GZ = head_z("me")                                   # 1.62: my head gap at 2.5 cm
GZ8 = head_z("me", hg=0.10, bg=0.08)                # my head gap in the scare (10 cm)
DGZ = head_z("dad", hg=0.005, bg=0.005)
FLAME = view([0.0, -0.45, 1.4], [0.0, 0.0, 3.0], 1.3)
FLAME[0][3] = 22
MEH = lambda z: [ME[0], ME[1], z]
DADH = lambda z: [DAD[0], DAD[1], z]
SOUTH_Y = -0.85

SHOTS = [
    # 01 the rule
    (0, "hook: a two-shot from inside the basket at pink dawn, mist through my gaps",
     view([0.0, SOUTH_Y, GZ], [0.0, DAD[1], GZ - 0.04], 1.45), 2, {"key": 22, "dsun": 5.0, "amb": 1.25}),
    ("L01.5", "my arm on the rim, three blocks a finger apart, the mist behind",
     view([-0.45, -0.55, 1.3], [0.85, 1.1, 1.25], 1.0), 2, {"key": 10, "dsun": 3.0}),
    ("L02", "the newlyweds at a field gate, their seams snapping shut",
     view([GATE[0], GATE[1] - 0.6, K0 + 1.2], [GATE[0], GATE[1] + 1.8, K0 + 1.2], 1.6), 2, {"room": "mont", "frame": "world", "key": 12}),
    ("L03", "a son with a holdall rattling at a cottage kitchen door, his mum leaning in",
     view([-0.3, -0.4, K0 + 1.45], [1.3, -2.3, K0 + 1.35], 2.0), 2, {"room": "kitchen", "frame": "world", "key": 10}),
    ("L04", "a grandad walking toward camera along a dry-stone wall, five relatives behind",
     view([LANE[0] + 3.4, -0.5, K0 + 1.3], [LANE[0] + 0.3, -0.2, K0 + 1.3], 2.2), 2, {"room": "mont", "frame": "world", "key": 10}),
    ("L05", "me at the kitchen window at dawn, side-on, gaps open",
     view([1.25, 0.15, K0 + GZ + 0.05], [-0.05, 1.45, K0 + GZ], 1.1), 2, {"room": "kitchen", "frame": "world", "key": 8}),
    ("L06", "through the gap between my head slices, the misty window",
     view([-0.1, -0.15, K0 + GZ], [-0.1, 1.45, K0 + GZ], 0.62), 2, {"room": "kitchen", "frame": "world", "key": 6}),
    ("L07", "Dad at the kitchen table, smiling at his tea",
     facecam((0.95, 0.0), -90, 1.15, 38, 1.0, hz=1.55, z0=K0), 2, {"room": "kitchen", "frame": "world", "key": 12}),
    ("L08", "a slow push on Dad's face as the smile goes polite",
     push([0.1, -0.85, K0 + 1.55], [0.35, -0.55, K0 + 1.55], [0.95, 0.0, K0 + 1.55], [0.95, 0.0, K0 + 1.55], 1.1, 0.8), 2,
     {"room": "kitchen", "frame": "world", "key": 12}),
    ("L09", "over Dad's shoulder: me across the table, waiting to be known",
     view([1.55, -0.45, K0 + 1.68], [-0.95, 0.0, K0 + 1.5], 2.0), 2, {"room": "kitchen", "frame": "world", "key": 10}),
    # 02 up
    ("L10", "the launch field in the plum dark, the lamp, Dad grinning",
     view([-0.1, -5.6, 1.0], [-2.9, -2.9, 1.0], 1.9), 2, {"frame": "world", "key": 14}),
    ("L11", "the envelope lying on the grass",
     view([-8.5, -12.0, 1.0], [-1.0, 0.0, 6.5], 11.0), 2, {"frame": "world"}),
    ("L11.2", "Dad and me side by side, looking up at it",
     view([-0.55, -5.2, 0.9], [-0.55, -3.2, 1.35], 1.7), 2, {"frame": "world", "key": 8}),
    ("L12", "the first flame into the mouth", view([1.6, -2.4, 1.2], [-0.2, 0.0, 3.0], 3.0), 2, {"frame": "world"}),
    ("L12.1", "the envelope standing up", view([-8.5, -12.0, 1.0], [-1.0, 0.0, 8.0], 11.0), 2, {"frame": "world"}),
    ("L13", "Rosa waving us into the basket without a word",
     facecam((2.15, -0.2), 190, 1.6, 20, 1.0, z0=FG, hz=1.35), 2, {"frame": "world", "key": 18}),
    ("L14", "Dad's sleeve", view([0.4, -0.2, 1.35], [DAD[0] + 0.3, DAD[1] - 0.3, 1.4], 0.7), 2, {"key": 12}),
    ("L14.1", "the balloon badge on his scarf",
     view([DAD[0] + 0.08, DAD[1] - 0.55, 1.55], [DAD[0] - 0.12, DAD[1] - 0.2, 1.47], 0.34), 2, {"key": 18}),
    ("L14.3", "Dad delighted: First time UP!",
     facecam(DAD, 0, 1.15, 14, 0.85, hz=1.64), 2, {"key": 16}),
    ("L15.1", "the leather rim: two worn patches, the slate tally between them",
     view([0.0, 0.2, 1.95], [0.0, 1.21, RH], 1.5), 2, {"key": 110}),
    ("L16.2", "Dad's hand and mine land on the two patches",
     view([0.0, 0.0, 1.85], [0.0, 1.15, 1.25], 1.3), 2, {"key": 30}),
    ("L17", "the basket lifts off the grass with no jolt",
     c([0, [-7.5, -10.0, 2.0], [0.0, 0.0, 3.0], 20], [1, [-7.5, -10.0, 2.0], [0.0, 0.0, 4.2], 20]), 2, {"frame": "world"}),
    # 03 loose
    ("L18", "the fields sinking under the mist",
     c([0, [0.5, -1.5, 2.0], [24, -8, 1.0], 24], [1, [0.5, -1.5, 2.0], [24, -8, -1.2], 24]), 2, {"key": 25, "dsun": 6.0}),
    ("L19", "the burner roars", FLAME, 2, {"key": 0}),
    ("L19.1", "my sleeve: the hand block slides a finger's width off",
     view([1.12, 0.02, 1.62], [ME[0] + 0.2, 1.08, 1.4], 0.7), 2, {"key": 12}),
    ("L20", "Dad pointing at barn roofs, delighted: LOOK at THAT",
     facecam(DAD, 150, 1.1, 0, 0.85, hz=1.64, z0=0.0), 2, {"key": 14}),
    ("L21", "Rosa at the burner frame, mouthing the words, a small sad smile",
     view([0.2, 0.15, 1.5], [ROSA[0], ROSA[1], 1.42], 0.75), 2, {"key": 14}),
    ("L22", "the burner roars again", FLAME, 2, {"key": 0}),
    ("L23", "Dad turning from the view to me, his face drops to polite",
     facecam(DAD, 60, 1.05, 0, 0.85, hz=1.62), 2, {"key": 14}),
    ("L24", "Dad leaning toward Rosa: And WHO'S this?",
     view([-1.0, -0.15, 1.72], [DAD[0] + 0.1, DAD[1], 1.55], 0.95), 2, {"key": 18}),
    ("L25", "the long roar swells", FLAME, 2, {"key": 3}),
    ("L25+0.85", "my hands drifting off my sleeves",
     view([1.6, 0.0, 1.6], [ME[0] - 0.1, 1.0, 1.36], 1.5), 2, {"key": 14}),
    ("L26", "wider: a hand's width off, then two",
     view([0.15, 1.95, 1.7], [ME[0], 1.0, 1.4], 1.0), 2, {"key": 14}),
    ("L27", "my head, front on, four slices apart, pink mist through every gap",
     push([ME[0], SOUTH_Y, GZ8 + 0.03], [ME[0], -0.45, GZ8 + 0.03], [ME[0], ME[1], GZ8], [ME[0], ME[1], GZ8], 0.95, 0.85), 2,
     {"key": 14, "dsun": 2.0}),
    ("P01", "hold on the sliced face: only the burner",
     view([ME[0], -0.5, GZ8 + 0.03], [ME[0], ME[1], GZ8], 0.8), 2, {"key": 14, "dsun": 2.0}),
    ("L28", "over my shoulder, through the gap in my own face: Dad, smiling politely",
     view([1.6, ME[1], GZ8], [DAD[0], DAD[1], 1.62], 0.8), 2, {"key": 8}),
    ("L29", "Dad's polite smile, close",
     facecam(DAD, 70, 1.0, 0, 0.8, hz=1.63), 2, {"key": 14}),
    # 04 the words
    ("L30", "my sliced face, eyes steady, the scared look going calm",
     view([ME[0], -0.4, GZ8 + 0.02], [ME[0], ME[1], GZ8], 0.85), 2, {"key": 14, "dsun": 2.0}),
    ("L31", "me turned to Dad: Happy BIRTHDAY, Dad. Look at the SUN.",
     view([0.0, -0.45, 1.72], [0.0, 0.67, 1.64], 1.5), 2, {"key": 14, "dsun": 2.0}),
    ("L32", "the sun breaks out of the mist, all gold", c([0, [-0.3, -0.2, 1.7], [60.0, -3.0, -6.0], 12.0], [1, [-0.3, -0.2, 1.7], [60.0, -3.0, -1.0], 12.0]), 2, {"key": 0}),
    ("L33", "Dad in gold light, his whole face waking up",
     facecam(DAD, 45, 1.05, 0, 0.85, hz=1.64), 2, {"key": 10}),
    ("L34", "Dad: There's my BOY",
     facecam(DAD, 20, 0.95, 0, 0.75, hz=1.64), 2, {"key": 10}),
    ("L35", "every slice and block sliding home, click by click",
     view([ME[0], -0.4, 1.68], [ME[0], ME[1], 1.66], 0.85), 2, {"key": 12}),
    # 05 the truth
    ("L36", "a bright wide down the sunlit valley, the basket level",
     view([15.0, -13.0, 2.4], [0.0, 0.0, 2.3], 7.0), 2, {"frame": "world"}),
    ("L37", "Dad and me at the rim, hands on the two worn patches",
     view([0.0, -0.55, 1.95], [0.0, 1.0, 1.3], 2.0), 2, {"key": 6}),
    ("L38", "Rosa at the burner frame, a sad smile, the gold valley behind",
     view([0.25, 0.25, 1.55], [ROSA[0], ROSA[1], 1.45], 0.85), 2, {"key": 10}),
    ("L38.3", "the landing in the stubble field",
     view([-9.0, -8.0, 1.2], [0.0, 0.0, 1.9], 6.0), 2, {"frame": "world"}),
    ("L39", "Rosa's sleeve pinning today's badge on the wall inside the trailer",
     view([TRAILER[0] + 1.0, -0.2, K0 + 1.3], [TRAILER[0] + 0.85, 1.3, K0 + 1.22], 0.7), 2,
     {"room": "trailer", "frame": "world", "key": 8}),
    ("L40", "pull back: the whole wall covered in identical balloon badges",
     push([TRAILER[0] + 0.55, -0.2, K0 + 1.3], [TRAILER[0], -2.1, K0 + 1.28], [TRAILER[0] + 0.9, 1.3, K0 + 1.22], [TRAILER[0], 1.3, K0 + 1.25], 0.6, 2.1), 2,
     {"room": "trailer", "frame": "world", "key": 6}),
    ("L41", "the landing field in late-morning light: Dad walking off beside Rosa, my sleeve in the foreground",
     view([-0.55, -3.75, FG + 0.95], [0.5, -3.1, FG + 0.85], 1.0), 2, {"frame": "world", "key": 10}),
    ("L42", "the next dawn: the basket rising off the launch field",
     push([-6.0, -9.0, 0.7], [-6.0, -9.0, 1.4], [0.0, 0.0, 1.8], [0.0, 0.0, 3.6], 7.0, 6.0), 2, {"frame": "world", "dsun": 3.0}),
]

shots = []
for i, (at, what, cam, step, extra) in enumerate(SHOTS):
    s = {"id": f"S{i + 1:02d}", "cam": cam, "hand": 0.003, "step": step, "what": what}
    if i:
        s["at"] = at
    s.update(extra)
    shots.append(s)

# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
ALL = list(cast)
acting = {k: [] for k in ALL}


def put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, "hidden": False, **NEUTRAL, **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": pos, **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def talk(who, a, b):
    acting[who].append({"from": a, "to": b, "mouth": [0.55, 0.55], "flap": True})


def p3(xy, z=0.0):
    return [xy[0], xy[1], z]


def yaw_to(a, b):
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


ARM_ME, ARM_DAD = 109, 96

# --- everyone starts hidden but the cast of the scene
for who in ALL:
    hide(who, 0)

# me
put("me", 0, p3(ME), yaw=-8, expr="worried", head=[0, 0])
put("me", "L01.5", p3(ME), yaw=180, arms=[ARM_ME, ARM_ME], expr="worried")
hide("me", "L02")
put("me", "L05", [0.0, 1.4, K0], yaw=0, expr="worried")                 # at the kitchen window (side-on in the shot)
key("me", "L05", yaw=60)
key("me", "L06", yaw=0, blend=0.0)
put("me", "L09", [-0.95, 0.0, K0], yaw=90, expr="worried")
hide("me", "L10")
put("me", "L11.2", [-0.2, -3.0, FG], yaw=180, expr="worried")
put("me", "L14", p3(ME), yaw=0, expr="worried", arms=[0, 0])
hide("me", "L15.1")                      # S20 opens on the empty rim: both patches and the tally in plain view
put("me", "L16.2", p3(ME), yaw=180, expr="worried")
key("me", "L16.2+0.55", arms=[ARM_ME, ARM_ME], blend=0.5)
key("me", "L19.1", expr="worried")
key("me", "L23", expr="worried")
key("me", "L25.1", expr="scared", blend=0.3)
put("me", "L26", p3(ME), yaw=180, arms=[ARM_ME, ARM_ME], expr="scared")
key("me", "L27", yaw=0, arms=[ARM_ME, ARM_ME], expr="scared")
key("me", "L28", yaw=-90, arms=[0, 0], blend=0.0)
key("me", "L30", yaw=0, expr="scared", arms=[ARM_ME, ARM_ME], blend=0.0)
key("me", "L30+0.9", expr="neutral", blend=0.6)
put("me", "L31", p3(ME), yaw=-62, expr="neutral", arms=[0, 0])
talk("me", "L31.1", "L31>")
key("me", "L35", yaw=0, expr="soft", arms=[0, 0], blend=0.0)
key("me", "L37", yaw=180, arms=[ARM_ME, ARM_ME], expr="soft", blend=0.0)
key("me", "L38.3", expr="soft")
put("me", "L41", [-0.1, -3.0, FG], yaw=90, expr="worried", arms=[0, 0])
put("me", "L42", p3(ME), yaw=-8, expr="worried")

# Dad
put("dad", 0, p3(DAD), yaw=35, expr="smile", head=[0, 0])
put("dad", "L01.5", p3(DAD), yaw=180, arms=[ARM_DAD, ARM_DAD], expr="smile")
hide("dad", "L02")
put("dad", "L07", [0.95, 0.0, K0], yaw=-90, expr="smile")
key("dad", "L08", expr="smile")
key("dad", "L08+0.9", expr="polite", blend=0.4)
hide("dad", "L10")
put("dad", "L10", [-2.6, -2.7, FG], yaw=15, expr="delighted")
put("dad", "L11.2", [-1.4, -3.0, FG], yaw=180, expr="delighted", head=[0, -22])
put("dad", "L14", p3(DAD), yaw=0, expr="smile", arms=[0, 70])
key("dad", "L14.1", arms=[0, 0], blend=0.1)
key("dad", "L14.3", expr="delighted", yaw=14)
talk("dad", "L14.4", "L14>")
key("dad", "L15.1", yaw=180, arms=[0, 0], expr="smile", blend=0.0)
hide("dad", "L15.1")
put("dad", "L16.2", p3(DAD), yaw=180, expr="smile")
key("dad", "L16.2+0.55", arms=[ARM_DAD, ARM_DAD], blend=0.5)
key("dad", "L20", yaw=150, expr="delighted", arms=[ARM_DAD - 8, 80], blend=0.0)
talk("dad", "L20.4", "L20>")
key("dad", "L21", yaw=180, arms=[ARM_DAD, ARM_DAD], expr="delighted", blend=0.0)
key("dad", "L23", yaw=60, expr="delighted", arms=[0, 0], blend=0.0)
key("dad", "L23+0.5", expr="polite", blend=0.2)
key("dad", "L24", yaw=15, expr="polite", blend=0.0)
talk("dad", "L24.1", "L24>")
key("dad", "L27", yaw=90, expr="polite", blend=0.0)
key("dad", "L28", yaw=90, expr="polite")
key("dad", "L29", yaw=70, expr="polite")
key("dad", "L31", yaw=60, expr="polite")
key("dad", "L33", yaw=45, expr="polite", blend=0.0)
key("dad", "L33+0.7", expr="delighted", blend=0.3)
key("dad", "L34", yaw=20, expr="laugh", blend=0.0)
talk("dad", "L34.1", "L34>")
key("dad", "L37", yaw=180, arms=[ARM_DAD, ARM_DAD], expr="smile", blend=0.0)
put("dad", "L41", [0.2, -3.0, FG], yaw=90, expr="smile", arms=[0, 0])
walk("dad", "L41>", [2.2, -3.0, FG])
put("dad", "L42", p3(DAD), yaw=0, expr="smile")

# Rosa
put("rosa", "L13", [2.15, -0.2, FG], yaw=190, expr="neutral", arms=[75, 0])
key("rosa", "L13+0.8", arms=[0, 75], blend=0.3)
put("rosa", "L19", p3(ROSA), yaw=180, expr="neutral")
key("rosa", "L21", yaw=170, expr="sad-smile", blend=0.2)
talk("rosa", "L21", "L21.2>")
key("rosa", "L22", yaw=180, expr="neutral", blend=0.3)
key("rosa", "L24", head=[0, 24], blend=0.3)
key("rosa", "L31", head=[0, 0], blend=0.3)
key("rosa", "L38", yaw=170, expr="sad-smile", blend=0.0)
put("rosa", "L39", [TRAILER[0] + 0.3, 0.62, TRAILER[2]], yaw=180, expr="sad-smile", arms=[0, 96])
hide("rosa", "L40")
put("rosa", "L41", [-0.2, -2.1, FG], yaw=90, expr="neutral")
walk("rosa", "L41>", [1.8, -2.1, FG])
put("rosa", "L42", p3(ROSA), yaw=180, expr="neutral")

# montage extras
put("groom", "L02", [GATE[0] - 0.55, 1.75, GATE[2]], yaw=0, expr="smile")
put("bride", "L02", [GATE[0] + 0.55, 1.75, GATE[2]], yaw=0, expr="smile")
hide("groom", "L03")
hide("bride", "L03")
put("son", "L03", [1.5, -2.9, K0], yaw=180, expr="worried", tremble=3.0)
put("mum", "L03", [1.5, -1.45, K0], yaw=0, expr="smile", head=[0, 10])
hide("son", "L04")
hide("mum", "L04")
GX = LANE[0]
put("grandad", "L04", [GX - 2.2, -0.3, LANE[2]], yaw=90, expr="smile")
walk("grandad", "L04>", [GX + 2.4, -0.3, LANE[2]])
for i, (dx, dy) in enumerate(((1.5, 0.5), (2.2, -0.9), (2.9, 0.3), (3.6, -0.7), (4.3, 0.5))):
    put(f"rel{i + 1}", "L04", [GX - 2.2 - dx, -0.3 + dy, LANE[2]], yaw=90, expr="smile")
    walk(f"rel{i + 1}", "L04>", [GX + 2.4 - dx, -0.3 + dy, LANE[2]])
hide("grandad", "L05")
for i in range(5):
    hide(f"rel{i + 1}", "L05")

# ---------------------------------------------------------------------------------------------------- cues
cues = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def seam(who, at, gap, body=None, head=None, hand=None, dur=0.0):
    cue(at, "seam", who=who, gap=gap, body=gap if body is None else body, head=gap if head is None else head,
        hand=gap if hand is None else hand, dur=dur)


# the day
cue(0, "dawn", v=0.42)
cue("L02", "dawn", v=0.7, dur=0)
cue("L05", "dawn", v=0.55, dur=0)
cue("L10", "dawn", v=0.0, dur=0)
cue("L18", "dawn", v=0.22, dur=4.0)
cue("L31+0.6", "dawn", v=1.0, dur=3.4)
cue("L41", "dawn", v=0.8, dur=0)
cue("L42", "dawn", v=0.42, dur=0)
# the ground
cue(0, "alt", alt=18.0)
cue("L10", "alt", alt=0.0, dur=0)
cue("L17", "alt", alt=18.0, dur=9.0)
cue("L38", "alt", alt=0.0, dur=3.2)
cue("L42", "alt", alt=0.0, dur=0)
cue("L42+0.3", "alt", alt=3.0, dur=3.5)
cue("L38", "field", f=1)
cue("L42", "field", f=0)
cue(0, "env", up=1.0)
cue("L10", "env", up=0.0, dur=0)
cue("L12", "env", up=1.0, dur=3.2)
cue("L41", "env", up=1.0, dur=0)
# the burner
cue("L12", "roar", peak=0.8, up=1.0, hold=1.2, down=0.9)
cue("L19", "roar", peak=1.0, up=0.6, hold=1.2, down=0.9)
cue("L22", "roar", peak=0.9, up=0.6, hold=1.2, down=0.9)
cue("L25-0.9", "roar", peak=0.6, up=1.0, hold=6.6, down=1.2)
cue("end-0.85", "roar", peak=0.25, up=0.25, hold=0.05, down=0.5)
# the seams (cm). Everyone else stays at their hairline.
seam("me", 0, 2.5)
seam("me", "L19", 2.5, hand=5.0, dur=0.8)
seam("me", "L23", 4.0, dur=0.8)
seam("me", "L25", 5.0, body=6.0, head=5.0, hand=10.0, dur=0.8)
seam("me", "L26", 5.0, body=6.0, head=5.0, hand=20.0, dur=0.9)
seam("me", "L27", 8.0, body=8.0, head=10.0, hand=20.0, dur=1.0)
seam("me", "L35", 0.5, dur=1.0)
seam("me", "L41", 0.5, hand=8.0, dur=0.0)
seam("me", "L42", 2.5, dur=0.0)
seam("groom", "L02", 2.5)
seam("groom", "L02.1", 0.5, dur=0.5)
seam("bride", "L02", 2.5)
seam("bride", "L02.1", 0.5, dur=0.5)
seam("son", "L03", 1.6)
seam("son", "L03.4", 0.7, dur=0.9)
cue("L03", "rattle", who="son", amp=0.6)
cue("L05", "rattle", who="son", amp=0.0)
# the new badge on the trailer wall
cue(0, "badge", on=False)
cue("L39+0.9", "badge", on=True)

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L12", "kind": "burner", "db": -15, "dur": 3.6},
    {"at": "L19", "kind": "burner", "db": -14, "dur": 3.6, "seed": 2},
    {"at": "L22", "kind": "burner", "db": -14, "dur": 3.4, "seed": 3},
    {"at": "L25-0.9", "kind": "burner", "db": -9, "dur": 9.4, "keep": True},
    {"at": "end-0.85", "kind": "burner", "db": -18, "dur": 0.85, "fall": 7.0},
    {"at": "L02.1", "kind": "click", "db": -10},
    {"at": "L02.2", "kind": "latch", "db": -16},
    {"at": "L03.3", "kind": "knock", "db": -16, "pattern": [0, 0.07, 0.15, 0.2, 0.3, 0.36], "tone": "hand"},
    {"at": "L04", "kind": "squeak", "db": -20},
    {"at": "L04.1", "kind": "squeak", "db": -20, "seed": 2},
    {"at": "L04.2", "kind": "squeak", "db": -20, "seed": 3},
    {"at": "L04.3", "kind": "squeak", "db": -20, "seed": 4},
    {"at": "L01.5", "kind": "knock", "db": -18, "pattern": [0, 0.5], "tone": "soft"},
    {"at": "L19", "kind": "knock", "db": -18, "pattern": [0.2], "tone": "soft"},
    {"at": "L23+0.5", "kind": "knock", "db": -18, "pattern": [0, 0.4], "tone": "soft"},
    {"at": "L25.1", "kind": "knock", "db": -16, "pattern": [0, 0.5, 1.0], "tone": "soft"},
    {"at": "L27", "kind": "knock", "db": -14, "pattern": [0, 0.35, 0.7], "tone": "soft"},
    {"at": "L35+0.1", "kind": "click", "db": -9},
    {"at": "L35+0.3", "kind": "click", "db": -10, "seed": 2},
    {"at": "L35+0.5", "kind": "click", "db": -9, "seed": 3},
    {"at": "L35+0.7", "kind": "click", "db": -10, "seed": 4},
    {"at": "L35+0.9", "kind": "click", "db": -11, "seed": 5},
    {"at": "L17", "kind": "creak", "db": -20, "dur": 1.4},
    {"at": "L14.1", "kind": "click", "db": -20, "seed": 9},
    {"at": "L28", "kind": "sting", "db": -14, "keep": True},
    {"at": "L32", "kind": "bell", "db": -26},
    {"at": "L39+0.9", "kind": "click", "db": -18, "seed": 7},
    {"at": "L42", "kind": "creak", "db": -22, "dur": 1.2},
]
story = {
    "slug": "ep31-dawn-flight",
    "title": json.loads((HERE.parent / "package.json").read_text())["title"],
    "made_for_kids": False,
    "premise": "In this valley, every body is built in blocks with thin seams between them, and if your family forgets you, "
               "your body comes apart, block by block. My blocks hang a finger's width apart because Dad, all the family I "
               "have, is forgetting me. For his sixtieth birthday he wants a balloon flight at dawn, just him and me, and "
               "the pilot Rosa takes us up over the mist. With each burner roar I come further apart, until Dad looks at "
               "me and asks Rosa who I am.",
    "twist": "Dad turned sixty four years ago. It is the last morning he remembers whole, with me in it, so Rosa flies us "
             "every dawn and I give him that birthday again: when I say what I said that morning he lands back in it and my "
             "blocks click shut. The wall of badges in her trailer is every one of those mornings, and by lunch he will "
             "ask who I am.",
    "world": "a hot-air balloon basket at dawn over misty farmland, a cold launch field and a farm kitchen, a field gate, a "
             "lane by a dry-stone wall and the inside of a pilot's trailer",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff7e6b",
    "gap": 0.12,
    "tail": 0.3,
    "fade_out": False,
    "fade_in": False,
    "look": {"fog": "#9d92b4", "fog_density": 0.0055, "fog_start": 14.0, "sky": "#8a6a92", "exposure": 0.0,
             "flash_safe": True},
    "grade": {"shadows": [0.0, 0.0, 0.05], "highlights": [0.02, 0.01, 0.0], "saturation": 1.0, "contrast": 1.04,
              "vignette": 0.28, "bloom": 0.25, "grain": 0.011},
    "phonemes": {"Rosa": "ɹˈOzɑ", "families": "fˈæməlˌiz", "fields": "fˈildz"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 50, "mode": "lydian", "bpm": 72, "seed": 31,
              "sections": [
                  {"at": 0, "voices": ["pluck_hi", "pad"], "energy": 0.35},
                  {"at": "L19", "voices": ["pad"], "energy": 0.3},
                  {"at": "L23", "voices": ["drone", "pad"], "energy": 0.5, "mode": "minor"},
                  {"at": "L32", "voices": ["pad", "piano"], "energy": 0.4, "mode": "major"},
                  {"at": "L40", "voices": ["drone"], "energy": 0.2, "mode": "minor"},
              ]},
    "sound": {"floor": "wood", "steps_db": -24,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "end", "lufs": -40},
                  {"kind": "wind", "from": "L10", "to": "L38", "lufs": -44},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01-0.05", "to": "L28", "keep": ["sting", "burner"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
