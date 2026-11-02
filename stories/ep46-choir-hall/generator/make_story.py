"""Writes ../story.json for ep46 "choir hall" (script by the writer, 2026-11-02).

Run from anywhere: python stories/ep46-choir-hall/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (time of day, lights, beads, doors, chairs), the score and the sound.

Places are set.py's metres (see its docstring). A character with yaw 0 faces -y, yaw 90 faces +x, yaw 180 faces +y.
Rig keys read by set.py (acting.py ignores them): sit, bend, roll, tilt, lunge.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

HX = 100.0
KX, KY = 40.0, 0.0
BX = 60.0

# ------------------------------------------------------------------------------------------------ lines
PAUSES = {}      # P01 and P02 already sit in lines.json where the script puts them
LOOP = 0.25
lines.append({"id": "P99", "pause": LOOP, "chunks": []})
TEMPO = {}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]
def split_long(chs):
    out = []
    for cap, sp in chs:
        cw, sw = cap.split(), sp.split()
        if len(cw) <= 3 or len(cw) != len(sw):
            out.append([cap, sp])
            continue
        k = len(cw) // 2 if len(cw) == 4 else 3
        out.append([" ".join(cw[:k]), " ".join(sw[:k])])
        out.append([" ".join(cw[k:]), " ".join(sw[k:])])
    return out


for ln in lines:
    if ln.get("chunks"):
        ln["chunks"] = split_long(ln["chunks"])

# ------------------------------------------------------------------------------------------------ cast
FACE = {"eyes": "round", "brows": True, "ink": "#1a1214"}


def person(skin, shirt, pants, shoes="#2a2420", hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None,
           collar=None, face=None, extras=None, hat="none", hat_c=None, height=1.0, zip_c=None):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "hat": hat, "face": face or dict(FACE)}
    if pattern_c:
        d["pattern_c"] = pattern_c
    if collar:
        d["collar"] = collar
    if extras:
        d["extras"] = extras
    if hat_c:
        d["hat_c"] = hat_c
    if height != 1.0:
        d["height"] = height
    if zip_c:
        d["zip_c"] = zip_c
    return d


TIRED = {"eyes": "tired", "brows": True, "ink": "#1a1214", "bags": True}
cast = {
    "me": person("#e0b08a", "#22304a", "#7b7f86", "#5a3b24", "cap", "#3a2418", "knit", "#1a2438", "#22304a"),
    "mum": person("#e8bd98", "#6b4a6e", "#4a4a52", "#3a2a22", "bun", "#7a6858", "knit", "#563a58", "#f0e6d0", TIRED,
                  ["coat"], zip_c="#563a58"),
    "mumr": person("#e8bd98", "#4c3038", "#4c3038", "#2a2022", "bun", "#7a6858", "solid", None, "#f3efe6", TIRED,
                   ["coat"], zip_c="#4a2230"),
    "ron": person("#e2b896", "#6b4a2e", "#4a463e", "#2a2a22", "none", "#e8e6e0", "knit", "#563a22", "#d8d0be", TIRED,
                  ["coat"], zip_c="#5a3a22", height=0.97),
    "postman": person("#d9a07c", "#22304a", "#22304a", "#1a1a1a", "cap", "#2a1d15", "solid", None, "#b0302a", None, None,
                      "ballcap", "#22304a"),
    "groom": person("#c68a62", "#a8825a", "#3a3a42", "#2a2420", "cap", "#2a1d15", "solid", None, None, None, ["coat"],
                    zip_c="#8a6a44"),
    "bride": person("#f0c8a0", "#2f8a86", "#e0d8c8", "#4a3028", "long", "#6a4228", "solid", None, None, None, ["coat"],
                    zip_c="#24706c"),
    "gatewoman": person("#8c5c40", "#d8c8a0", "#5a4634", "#3a2a22", "bun", "#1a1412", "knit", "#b8a880"),
    "gateman": person("#f0c8a0", "#6a7a4a", "#4a4a40", "#3a2a22", "cap", "#9a5a32", "plaid", "#4a5a30"),
    "nb1": person("#d9a07c", "#8a3a3a", "#3a3a48", "#2a2420", "spiky", "#4a3a2a", "knit", "#6a2a2a"),
    "nb2": person("#e0b08a", "#3a5a7a", "#4a4a4a", "#2a2420", "swoop", "#7a4a2a", "stripes", "#4a7a9a"),
    "rowa": person("#f0c8a0", "#6a8a5a", "#3a3a3a", "#2a2420", "cap", "#8a8a8a", "plaid", "#8a3a2a"),
    "rowb": person("#c68a62", "#4a7a4a", "#4a4a52", "#2a2420", "long", "#2a1d15"),
}
SKINS = ["#e0b08a", "#c68a62", "#8c5c40", "#f0c8a0", "#d9a07c", "#a8744e", "#e8bd98", "#7a4a34"]
STYLES = ["cap", "spiky", "swoop", "long", "bun", "buzz", "cap", "long", "bun", "swoop", "spiky"]
HAIRS = ["#2a1d15", "#6a5a3a", "#1a1412", "#9a5a32", "#8a8a8a", "#3a2a22", "#4a3a2a", "#171717", "#7a4a2a", "#c8b48a", "#2a1d15"]
for i in range(11):
    cast[f"c{i + 1}"] = person(SKINS[i % 8], "#4c3038", "#4c3038", "#2a2022", STYLES[i], HAIRS[i], "solid", None, "#f3efe6",
                               dict(FACE), ["coat"], zip_c="#4a2230", height=[1.0, 0.96, 1.03, 0.98, 1.02, 0.95, 1.0, 1.04, 0.97, 1.01, 0.99][i])
cast["grin"] = person("#d8c0a6", "#4c3038", "#4c3038", "#2a2022", "buzz", "#5a4030", "solid", None, "#f3efe6",
                      {"eyes": "round", "brows": True, "ink": "#1a1214", "mouth": "none"}, ["coat"], zip_c="#4a2230", height=1.12)
NAMES = list(cast)

# the twelve chairs (set.py's STEPS and CHX)
STEPS = [(0.9, -8.65), (0.6, -7.15), (0.3, -5.65)]
CHX = [-1.65, -0.55, 0.55, 1.65]
SLOTS = [(HX + dx, y, z) for z, y in STEPS for dx in CHX]
TWELFTH = SLOTS[0]
SEATS = SLOTS[1:]


# ------------------------------------------------------------------------------------------------ camera helpers
def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return c([0, list(loc), list(tgt), lens])


def move(a, b, lens_a, lens_b=None):
    return c([0, list(a[0]), list(a[1]), lens_a], [1, list(b[0]), list(b[1]), lens_b or lens_a])


def yaw_to(a, b):
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


def front(pos, yaw, dist, h=1.5, tz=1.4, lens=30, side=0.0, dz=0.0):
    dist = dist * 1.25 if dist < 2.5 else dist
    """A camera `dist` metres in front of someone (along their facing), turned `side` degrees round them."""
    a = math.radians(yaw + side)
    loc = (pos[0] + math.sin(a) * dist, pos[1] - math.cos(a) * dist, h)
    return still(loc, (pos[0], pos[1], tz + dz), lens)


WIN = (HX + 2.8, 12.4, 2.3)       # outside the hall's back window


def winshot(tgt, lens, loc=WIN):
    return still(loc, tgt, lens)


def sit_z(step_top):
    return round(step_top - 0.06, 3)


# ------------------------------------------------------------------------------------------------ acting machinery
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True, "sit": False,
           "bend": 0, "roll": 0, "tilt": 0, "lunge": 0}
acting = {n: [] for n in NAMES}
visible = {n: False for n in NAMES}


def put(who, at, pos, yaw=0, expr="neutral", **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": list(pos), "yaw": yaw, "blend": 0, "hidden": False, **NEUTRAL, "expr": expr, **kw})
    visible[who] = True


def hide(who, at):
    if visible[who] or not acting[who]:
        acting[who].append({"at": at, "hidden": True, "blend": 0})
    visible[who] = False


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": list(pos), **kw})


def talk(who, a, b, m=0.55):
    acting[who].append({"from": a, "to": b, "mouth": [m, m], "flap": True})


def sing(who, a, b, m=0.75):
    acting[who].append({"from": a, "to": b, "mouth": [m, m]})


def P(pos, yaw=0, expr="neutral", later=(), walks=(), talks=(), sings=(), **kw):
    return {"pos": pos, "yaw": yaw, "expr": expr, "later": list(later), "walks": list(walks), "talks": list(talks),
            "sings": list(sings), "kw": kw}


def choir(sing_from=None, sing_to=None, skip=(), expr="neutral", look=None, **kw):
    out = {}
    for i, (x, y, z) in enumerate(SEATS):
        n = f"c{i + 1}"
        if n in skip:
            continue
        k = dict(sit=True, arms=[14, 14], **kw)
        if look:
            k["look"] = look
        out[n] = P((x, y, sit_z(z)), 180, expr, sings=[(sing_from, sing_to)] if sing_from else [], **k)
    return out


# ------------------------------------------------------------------------------------------------ shots
# (at, what, step, camera, cast {name: P}, extras)
SH = []


def shot(at, what, cam, cast_, step=2, fill=None, hand=0.006, **kw):
    SH.append(dict(at=at, what=what, cam=cam, cast=cast_, step=step, fill=fill, hand=hand, **kw))


# street places
GW = (3.7, -3.5)                      # the woman at her sage gate (right plot 0)
GM = (-3.7, -3.5)                     # the man at his gate (left plot 0)
OURS = (-3.7, -17.5)                  # our gate (left plot 2), inside the garden
RON = (-3.7, -24.5)                   # old Ron (left plot 3)
ME_ST = (0.0, -12.0)

# ---- 01 the rule, L01 to L16
shot(0, "woman at her sage gate, the rule on her chest, neighbours behind",
     still((2.1, -0.9, 1.5), (3.8, -4.4, 1.35), 24),
     {"gatewoman": P(GW, yaw_to(GW, (2.1, -0.9)), "smile"),
      "nb1": P((3.7, -10.5), -90, "neutral"), "nb2": P((3.7, -17.5), -90, "neutral"),
      "gateman": P((-3.7, -10.5), 90, "neutral")}, step=2, hand=0.004)
shot("L02", "close on a cord over a cardigan",
     still((2.55, -2.45, 1.2), (3.7, -3.5, 1.1), 36),
     {"gatewoman": P(GW, yaw_to(GW, (2.55, -2.45)), "smile")})
shot("L03", "a man at his gate opens his mouth to a neighbour",
     still((-2.95, 0.6, 1.5), (-2.95, -3.5, 1.4), 24),
     {"gateman": P(GM, 90, "neutral", talks=[("L03.0", "L03.1")]), "nb1": P((-2.2, -3.5), -90, "neutral")})
shot("L03.1", "close: one bead fades",
     still((-2.65, -2.5, 1.25), (-3.7, -3.5, 1.15), 36),
     {"gateman": P(GM, 90, "neutral")})
shot("L04", "the groom on one knee, two beads fading",
     still((-1.2, -8.5, 1.1), (-4.0, -8.5, 0.95), 24),
     {"groom": P((-4.0, -9.25, -0.34), 180, "worried", lunge=60, talks=[("L04.1", "L04.1>")]),
      "bride": P((-4.0, -7.85), 0, "hopeful")})
shot("L04.2", "the bride nods hard",
     still((-3.4, -10.4, 1.45), (-4.0, -7.85, 1.45), 30),
     {"bride": P((-4.0, -7.85), 0, "smile", later=[("L04.2+0.1", dict(head=[0, 20])), ("L04.2+0.3", dict(head=[0, -4])),
                                                    ("L04.2+0.5", dict(head=[0, 20])), ("L04.2+0.7", dict(head=[0, -4]))]),
      "groom": P((-4.0, -9.25, -0.34), 180, "worried", lunge=60)})
shot("L05", "the two walk off arm by arm, his eight lit beads",
     move(([0.6, -3.4, 1.35], [-0.1, -11, 1.3]), ([0.6, -3.4, 1.35], [-0.1, -11, 1.3]), 26),
     {"groom": P((-0.3, -16.0), 180, "smile", walks=[("L05>", (-0.3, -7.0))]),
      "bride": P((0.5, -16.0), 180, "smile", walks=[("L05>", (0.5, -7.0))])})
shot("L06", "the postman points at the sky, mouth open",
     front((-3.7, -10.5), 90, 3.0, 1.55, 1.4, 26, 18),
     {"postman": P((-3.7, -10.5), 90, "wide", arms=[150, 0], talks=[("L06", "L06.2>")])})
shot("L06.2", "close: his last bead fades",
     still((-2.6, -9.9, 1.25), (-3.7, -10.5, 1.15), 36),
     {"postman": P((-3.7, -10.5), 90, "wide", arms=[150, 0])})
shot("L07", "he mimes a big square parcel, the neighbour baffled",
     still((3.2, -14.2, 1.55), (4.4, -17.5, 1.4), 24),
     {"postman": P((3.6, -17.5), 90, "grin", arms=[80, 80], side=[-30, -30]),
      "nb2": P((5.0, -17.5), -90, "worried")})
shot("L08", "dusk: two neighbours glare across the hedge, cords dark",
     still((-1.2, -7.0, 1.3), (-4.3, -7.0, 1.15), 26),
     {"rowa": P((-4.3, -5.9), 0, "angry", arms=[70, 70]), "rowb": P((-4.3, -8.15), 180, "angry", arms=[70, 70])})
shot("L09", "through the hall window: eleven singers, Mum conducting",
     winshot((HX + 0.3, -7.5, 1.9), 34),
     {**choir("L09", "L09>"), "mumr": P((HX + 1.2, -3.0), 0, "smile", arms=[70, 20])})
shot("L10", "me at the kitchen window",
     still((KX + 0.35, KY + 3.8, 1.55), (KX, KY + 1.5, 1.5), 24),
     {"me": P((KX, KY + 1.5), 180, "neutral")})
shot("L12", "my bedroom at night, the bedside lamp, ten lit beads",
     still((BX + 1.0, -0.2, 1.25), (BX - 0.7, -0.2, 1.1), 30),
     {"me": P((BX - 0.7, -0.2, 0.0), 90, "neutral", sit=True)})
shot("L13", "two neighbours nod as I pass",
     still((-1.7, -1.0, 1.5), (3.6, -3.6, 1.3), 24),
     {"gatewoman": P(GW, yaw_to(GW, (0, -2.5)), "smile", later=[("L13.0+0.1", dict(head=[0, 14])), ("L13.0+0.4", dict(head=[0, -2]))]),
      "gateman": P((3.7, -2.1), yaw_to((3.7, -2.1), (0, -2.5)), "smile"),
      "me": P((-0.4, -0.2), 180, "neutral", walks=[("L13>", (-0.4, -5.5))])})
shot("L14", "old Ron at his gate, his cord wound three times",
     front(RON, 90, 3.0, 1.45, 1.35, 28, 12),
     {"ron": P(RON, 90, "angry")})
shot("L15", "close on the three loops",
     still((-2.7, -24.0, 1.2), (-3.7, -24.5, 1.1), 36),
     {"ron": P(RON, 90, "angry")})
shot("L16", "close on my collar and the bulge under the knit",
     front(ME_ST, 180, 1.35, 1.2, 1.12, 34),
     {"me": P(ME_ST, 180, "neutral")})
shot("L16.2", "me, guarded",
     front(ME_ST, 180, 2.0, 1.45, 1.3, 30),
     {"me": P(ME_ST, 180, "neutral", look=[0, 0.6])})

# ---- 02 Mum, L17 to L27
shot("L17", "Mum at her stand, conducting",
     still((HX + 0.3, -10.2, 3.2), (HX + 1.2, -3.0, 1.55), 50),
     {**choir(), "mumr": P((HX + 1.2, -3.0), 0, "smile", arms=[75, 25])})
shot("L18", "Mum at my half-open door",
     still((BX + 0.7, 0.2, 1.4), (BX, 2.9, 1.4), 30),
     {"mum": P((BX, 2.9), 0, "hopeful")})
shot("L19", "close on Mum speaking, her beads fading one by one",
     still((BX + 0.25, 1.55, 1.45), (BX, 2.9, 1.4), 40),
     {"mum": P((BX, 2.9), 0, "smile", talks=[("L19", "L19.4")])})
shot("L19.4", "her last bead goes dark",
     still((BX + 0.3, 1.9, 1.1), (BX, 2.9, 1.1), 42),
     {"mum": P((BX, 2.9), 0, "hopeful")})
shot("L20", "me on the bed, guarded",
     still((BX + 1.0, -0.2, 1.2), (BX - 0.7, -0.2, 1.1), 30),
     {"me": P((BX - 0.7, -0.2, 0.0), 90, "neutral", sit=True, look=[0, 0.6])})
shot("L21", "the kitchen at supper: Mum, ten dark beads, a cold cup",
     still((KX + 0.3, KY + 1.5, 1.45), (KX - 0.2, KY - 1.2, 1.2), 28),
     {"mum": P((KX - 0.2, KY - 1.22, 0.0), 180, "neutral", sit=True)})
shot("L22", "Mum conducts with just her hands, mouth shut",
     winshot((HX + 0.6, -5.5, 1.7), 34),
     {**choir(), "mumr": P((HX + 1.2, -3.0), -50, "neutral", arms=[75, 25])})
shot("L23", "wide through the window: eleven singers and an empty chair",
     winshot((HX - 0.3, -7.5, 1.9), 30, (HX + 2.8, 12.4, 2.2)),
     {**choir(), "mumr": P((HX + 1.2, -3.0), 0, "neutral", arms=[75, 25])})
shot("L24", "closer: the empty twelfth chair with a folded robe",
     winshot((TWELFTH[0], TWELFTH[1], 1.7), 90),
     {**choir()})
shot("L25", "me under the lamp post, looking up at the window",
     still((HX - 2.1, 10.3, 1.5), (HX - 2.9, 12.4, 1.55), 30),
     {"me": P((HX - 2.9, 12.4), 0, "neutral", head=[0, -16])}, fill=[60, "#a8bce8"])
shot("L26", "close through the glass on two singing mouths",
     winshot((HX + 0.3, -8.65, 2.0), 120),
     {**choir("L26", "L26.1"), })
shot("L26.1", "the empty chair, and a twelfth note",
     winshot((TWELFTH[0], TWELFTH[1], 1.8), 110, (HX + 2.5, 12.4, 2.3)),
     {**choir()})
shot("L27", "high through the glass: the twelfth chair angled toward Mum's stand",
     still((HX + 2.7, 12.0, 3.0), (HX - 0.4, -7.0, 1.5), 32),
     {**choir(), "mumr": P((HX + 1.2, -3.0), 0, "neutral", arms=[75, 25])})
shot("L27.3", "me at the window, worried",
     still((HX + 2.3, 10.4, 1.55), (HX + 2.8, 12.2, 1.55), 30),
     {"me": P((HX + 2.8, 12.2), 0, "worried", head=[0, -14])}, fill=[60, "#a8bce8"])

# ---- 03 the scarf, L28 to L38
shot("L28", "the kitchen at night: her empty chair, the clock with no numbers",
     still((KX - 1.6, KY - 1.9, 1.35), (KX + 0.8, KY + 0.8, 1.2), 26), {})
shot("L29", "me at the hall's open door, the inside black",
     still((HX - 0.6, 11.2, 1.55), (HX - 2.6, 10.0, 1.5), 28),
     {"me": P((HX - 2.6, 10.1), 150, "scared")}, fill=[90, "#a8bce8"])
shot("P01", "hold on the dark hall; one chair creaks",
     still((HX - 2.7, 8.4, 1.45), (HX - 1.2, -8.0, 1.0), 22), {}, step=4)
shot("L30", "her scarf on the twelfth chair, in the wedge of streetlight",
     still((HX - 0.8, -3.6, 1.7), (TWELFTH[0], TWELFTH[1], 1.35), 38), {})
shot("L31", "the other eleven chairs are turned to face it",
     still((HX - 2.4, 8.0, 1.8), (HX - 0.6, -7.0, 1.1), 20), {}, step=4)
shot("L31.4", "me, scared",
     still((HX - 2.3, 7.0, 1.55), (HX - 2.6, 10.1, 1.5), 30),
     {"me": P((HX - 2.6, 9.7), 0, "scared")}, fill=[90, "#a8bce8"])
shot("L32", "me on the lane in the dark, wind",
     still((0.3, -2.5, 1.5), (0.0, -14.0, 1.2), 26),
     {"me": P((0.0, -13.0), 180, "worried", walks=[("L32>", (0.0, -7.0))])}, fill=[50, "#a8bce8"])
shot("L33", "close on my collar and the bulge: ten lit beads",
     front(ME_ST, 180, 1.35, 1.2, 1.12, 34),
     {"me": P(ME_ST, 180, "neutral")}, fill=[40, "#a8bce8"])
shot("L34", "me, lips shut",
     front(ME_ST, 180, 1.8, 1.45, 1.4, 34),
     {"me": P(ME_ST, 180, "neutral", look=[0, 0.5])}, fill=[50, "#a8bce8"])
shot("L35", "grey dawn: Mum asleep upright in her coat, beads dark",
     still((KX + 0.4, KY + 1.4, 1.4), (KX - 0.2, KY - 1.22, 1.15), 28),
     {"mum": P((KX - 0.2, KY - 1.22, 0.0), 180, "asleep", sit=True, head=[0, 10])})
shot("L36", "Ron at our gate in the dawn",
     front(OURS, 90, 3.0, 1.45, 1.35, 28, 10),
     {"ron": P(OURS, 90, "angry")})
shot("L37", "close on Ron's loops: seven beads fade",
     still((-2.7, -17.0, 1.2), (-3.7, -17.5, 1.1), 36),
     {"ron": P(OURS, 90, "angry")})
shot("L38", "Ron looks right at me",
     front(OURS, 90, 2.0, 1.5, 1.4, 34, 8),
     {"ron": P(OURS, 90, "soft")})
shot("L38.2", "me, worried",
     front((-2.0, -17.5), -90, 2.0, 1.5, 1.4, 34),
     {"me": P((-2.0, -17.5), -90, "worried")})

# ---- 04 the concert, L39 to L65
shot("L39", "the hall by day: bunting up, chairs set in rows",
     still((HX + 1.5, 8.2, 2.2), (HX - 0.4, -6.5, 1.4), 20), {}, step=4)
shot("L40", "Mum at the kitchen table with a bare music stand, mouthing",
     still((KX + 1.0, KY + 1.5, 1.45), (KX - 0.2, KY - 1.22, 1.2), 28),
     {"mum": P((KX - 0.2, KY - 1.22, 0.0), 180, "hopeful", sit=True, talks=[("L40.1", "L40>")])})
shot("L41", "the choir shake their heads at the stand",
     still((HX + 0.2, -2.6, 1.9), (HX - 0.2, -7.2, 1.9), 32),
     {**choir(look=None), "mumr": P((HX + 1.2, -3.0), 0, "neutral", arms=[40, 40])})
shot("L42", "Mum stands up straight, ten beads lit",
     front((HX + 1.0, -3.0), 180, 3.0, 1.55, 1.4, 28),
     {"mumr": P((HX + 1.0, -3.0), 180, "smile")})
shot("L43", "Mum's shadow passes my half-open door",
     still((BX - 0.2, -0.4, 1.25), (BX, 2.9, 1.2), 26),
     {"mum": P((BX + 1.5, 3.3), -90, "neutral", walks=[("L43>", (BX - 1.6, 3.3))])})
shot("L44", "me in bed, facing the door",
     still((BX - 0.1, 1.3, 1.4), (BX - 1.3, -0.9, 1.0), 28),
     {"me": P((BX - 1.35, -1.0, 0.0), 180, "worried", sit=True)})
shot("L45", "the hall is packed",
     still((HX + 1.2, 8.6, 2.1), (HX - 0.2, -7.0, 1.7), 20),
     {**choir(), "mumr": P((HX + 1.2, -3.0), 0, "neutral", arms=[40, 40])}, step=4)
shot("L46", "me by the back wall",
     still((HX + 3.4, 4.4, 1.5), (HX + 3.8, 7.6, 1.5), 28),
     {"me": P((HX + 3.8, 7.6), 0, "neutral", look=[0, 0.5])})
shot("L47", "the lights go down slowly",
     still((HX + 1.4, 8.6, 2.1), (HX - 0.2, -7.0, 1.7), 20),
     {**choir(), "mumr": P((HX + 1.2, -3.0), 0, "neutral", arms=[40, 40])}, step=4)
shot("L48", "the lamp over the riser; the twelfth chair at the edge of the light",
     still((HX - 0.6, -1.8, 0.9), (HX - 1.0, -7.4, 2.4), 24),
     {**choir()})
shot("L49", "a slow pan along the riser, eleven faces",
     move(([HX + 1.9, -2.0, 2.15], [HX + 1.5, -8.6, 2.0]), ([HX - 0.4, -2.0, 2.15], [HX - 1.0, -8.6, 2.0]), 34),
     {**choir()}, step=2)
shot("L50", "someone in maroon in the twelfth chair, from the back",
     still((HX - 1.0, 8.6, 1.9), (TWELFTH[0], TWELFTH[1], 2.1), 70),
     {**choir(), "grin": P((TWELFTH[0], TWELFTH[1], sit_z(TWELFTH[2])), 180, "neutral", sit=True, head=[0, 24], arms=[14, 14], blink=False)})
shot("L51", "an ordinary singer, waxy, eyes straight ahead",
     still((HX - 1.4, -3.4, 2.55), (TWELFTH[0], TWELFTH[1], 2.1), 48),
     {**choir(), "grin": P((TWELFTH[0], TWELFTH[1], sit_z(TWELFTH[2])), 180, "neutral", sit=True, head=[0, 20], arms=[14, 14], blink=False)})
shot("L52", "cut away to Mum at the stand",
     front((HX + 1.2, -3.0), -60, 2.6, 1.55, 1.45, 30),
     {"mumr": P((HX + 1.2, -3.0), -60, "neutral", arms=[40, 40])})
shot("L52.1", "its head now turned toward the hall",
     still((HX - 1.4, -3.4, 2.55), (TWELFTH[0], TWELFTH[1], 2.1), 48),
     {**choir(), "grin": P((TWELFTH[0], TWELFTH[1], sit_z(TWELFTH[2])), 180, "neutral", sit=True, arms=[14, 14], blink=False)})
shot("L53", "the grin, and the black line carrying on round the cheeks",
     still((HX - 1.0, -4.3, 2.6), (TWELFTH[0] - 0.05, TWELFTH[1], 2.15), 60),
     {**choir(), "grin": P((TWELFTH[0], TWELFTH[1], sit_z(TWELFTH[2])), 180, "neutral", sit=True, head=[-28, 0], arms=[14, 14], blink=False)})
shot("L54", "from behind the riser: the black seam round the back of its head",
     still((TWELFTH[0] + 0.35, -10.95, 2.75), (TWELFTH[0], TWELFTH[1], 2.2), 36),
     {**choir(), "grin": P((TWELFTH[0], TWELFTH[1], sit_z(TWELFTH[2])), 180, "neutral", sit=True, arms=[14, 14], blink=False)})
shot("L55", "no cord round its neck",
     still((HX - 1.1, -4.2, 2.55), (HX - 1.1, -8.65, 2.0), 40),
     {**choir(), "grin": P((TWELFTH[0], TWELFTH[1], sit_z(TWELFTH[2])), 180, "neutral", sit=True, arms=[14, 14], blink=False)})
MUMX = TWELFTH[0] - 1.1
MUMP = (MUMX, TWELFTH[1], 0.9)
GRINP = (TWELFTH[0], TWELFTH[1], sit_z(TWELFTH[2]))
shot("L56", "Mum steps up beside the riser into the lamp light",
     still((MUMX + 0.8, -5.0, 2.7), (MUMX, TWELFTH[1], 2.45), 38),
     {**choir(), "mumr": P(MUMP, 180, "hopeful"),
      "grin": P(GRINP, 180, "neutral", sit=True, arms=[14, 14], blink=False)})
shot("L57", "Mum singing, close",
     front(MUMP, 180, 1.9, 2.55, 2.5, 36, 12),
     {**choir(), "mumr": P(MUMP, 180, "smile", talks=[("L57", "L57.1")]),
      "grin": P(GRINP, 180, "neutral", sit=True, arms=[14, 14], blink=False)})
shot("L57.1", "close on her cord: the beads fade one by one",
     front(MUMP, 180, 2.1, 2.5, 2.4, 34, 4),
     {"mumr": P(MUMP, 180, "smile")})
shot("L58", "it tilts toward her",
     still((MUMX + 2.8, -5.0, 2.9), (MUMX + 0.9, TWELFTH[1], 2.35), 40),
     {**choir(), "mumr": P(MUMP, 180, "smile"),
      "grin": P(GRINP, 180, "neutral", sit=True, head=[60, 0], roll=22, bend=6, arms=[14, 14], blink=False)})
shot("L59", "two shot: it leans further, its face a metre from hers",
     still((MUMX + 2.6, -5.2, 2.85), (MUMX + 0.7, TWELFTH[1], 2.35), 40),
     {**choir(), "mumr": P(MUMP, 180, "smile"),
      "grin": P(GRINP, 180, "neutral", sit=True, head=[85, 0], roll=40, bend=10, arms=[14, 14], blink=False)})
shot("L60", "close on Mum's cord: one lit bead left",
     front(MUMP, 180, 2.1, 2.5, 2.4, 34, 4),
     {"mumr": P(MUMP, 180, "worried")})
shot("L61", "Mum, worried, her mouth closing",
     front(MUMP, 180, 1.9, 2.6, 2.5, 36, 14),
     {"mumr": P(MUMP, 180, "worried"),
      "grin": P(GRINP, 180, "neutral", sit=True, head=[90, 0], roll=52, bend=14, arms=[14, 14], blink=False)})
shot("L62", "that grin is at her ear",
     still((MUMX + 1.5, -6.6, 2.7), (MUMX + 0.4, TWELFTH[1], 2.4), 52),
     {**choir(), "mumr": P(MUMP, 180, "worried"),
      "grin": P(GRINP, 180, "neutral", sit=True, head=[90, 0], roll=62, bend=14, arms=[14, 14], blink=False)})
shot("P02", "hold on Mum's face",
     front(MUMP, 180, 1.6, 2.6, 2.5, 38, 6),
     {"mumr": P(MUMP, 180, "worried")}, step=4)
shot("L63", "I remember: me at the back, a hand at my jumper",
     still((HX + 3.4, 4.6, 1.5), (HX + 3.8, 7.6, 1.5), 28),
     {"me": P((HX + 3.8, 7.6), 0, "scared")})
shot("L65", "the bulge under the jumper",
     still((HX + 3.7, 5.6, 1.1), (HX + 3.8, 7.6, 0.95), 36),
     {"me": P((HX + 3.8, 7.6), 0, "scared")})

# ---- 05 the verse, L66 to L75
shot("L66", "low behind me, up the aisle toward the lamp",
     still((HX + 0.0, 8.4, 0.8), (HX - 0.4, -6.0, 1.4), 26),
     {"me": P((HX, 6.5), 0, "neutral", walks=[("L66>", (HX, -1.5))])})
shot("L67", "the twelfth chair, empty in the lamp light",
     still((HX - 1.4, -3.4, 2.55), (TWELFTH[0], TWELFTH[1], 2.1), 48),
     {**choir(), "mumr": P(MUMP, 180, "neutral")})
shot("L67.1", "me in the twelfth chair",
     still((HX - 1.4, -3.4, 2.55), (TWELFTH[0], TWELFTH[1], 2.1), 48),
     {**choir(), "mumr": P(MUMP, 180, "neutral"),
      "me": P(GRINP, 180, "neutral", sit=True, arms=[14, 14])})
shot("L68", "me singing",
     front(GRINP, 180, 2.2, 2.4, 2.15, 36, 8),
     {"me": P(GRINP, 180, "smile", sit=True, arms=[14, 14], sings=[("L68", "L69>")]), "mumr": P(MUMP, 180, "smile")})
shot("L70", "the long cord slides out of my collar and spills down my front",
     still((TWELFTH[0], -4.5, 2.15), (TWELFTH[0], TWELFTH[1], 1.75), 42),
     {"me": P(GRINP, 180, "smile", sit=True, arms=[14, 14], sings=[("L70", "L71>")])})
shot("L71", "tilt down the cord as the beads go dark",
     move(([TWELFTH[0], -4.5, 2.2], [TWELFTH[0], TWELFTH[1], 2.2]), ([TWELFTH[0], -4.5, 2.2], [TWELFTH[0], TWELFTH[1], 1.35]), 42),
     {"me": P(GRINP, 180, "smile", sit=True, arms=[14, 14], sings=[("L70", "L71>")])})
shot("L72", "Mum smiles at the hall, one bead still lit",
     front(MUMP, 180, 2.0, 2.6, 2.5, 36, 12),
     {"mumr": P(MUMP, 180, "smile"), "me": P(GRINP, 180, "smile", sit=True, arms=[14, 14])})
shot("L72.2", "behind the riser: twelve strokes on the back board",
     still((TWELFTH[0] + 0.05, -11.05, 1.25), (TWELFTH[0] + 0.05, -9.5, 1.25), 20),
     {**choir(), "mumr": P(MUMP, 180, "smile"), "me": P(GRINP, 180, "smile", sit=True, arms=[14, 14])}, step=4)
shot("L73", "me singing, the cord dark below my chin",
     front(GRINP, 180, 1.9, 2.4, 2.15, 36, 8),
     {"me": P(GRINP, 180, "smile", sit=True, arms=[14, 14]), "mumr": P(MUMP, 180, "smile")})
shot("L74", "a past night: Mum at my door, my door swings shut on her",
     still((BX + 0.3, 0.9, 1.45), (BX, 2.9, 1.4), 30),
     {"mum": P((BX, 2.9), 0, "hopeful")})
shot("L75", "a past night: the bulge under the knit in the lamp light",
     still((BX + 0.9, -0.3, 1.0), (BX - 0.7, -0.2, 0.85), 36),
     {"me": P((BX - 0.7, -0.2, 0.0), 90, "neutral", sit=True)})

# ---- 06 the hill, L76 to L84
HILL = [(0.2, -9.0), (0.2, -19.0)]
shot("L76", "wide: Mum and me walk down the hill under the stars",
     still((3.2, -9.0, 1.5), (0.0, -14.0, 1.3), 24),
     {"me": P((0.9, -8.0), 180, "smile", walks=[("L76>", (0.9, -16.0))], talks=[("L76", "L76>")]),
      "mum": P((-0.7, -8.0), 180, "smile", walks=[("L76>", (-0.7, -16.0))])}, fill=[60, "#a8bce8"])
shot("L77", "Mum laughs, which is free",
     front((-0.3, -17.5), 180, 1.7, 1.5, 1.45, 34),
     {"mum": P((-0.3, -17.5), 180, "laugh", later=[("L77+0.2", dict(head=[0, -8]))])}, fill=[50, "#a8bce8"])
shot("L78", "at our gate she turns to me",
     still((-1.0, -13.5, 1.5), (-2.0, -17.5, 1.4), 28),
     {"mum": P((-2.0, -17.5), -90, "smile"), "me": P((-0.2, -17.5), 90, "smile")}, fill=[50, "#a8bce8"])
shot("L79", "Thursday? her last bead",
     front((-2.0, -17.5), -90, 1.7, 1.5, 1.45, 34, 20),
     {"mum": P((-2.0, -17.5), -90, "hopeful", talks=[("L79", "L79>")])}, fill=[50, "#a8bce8"])
shot("L80", "I say yes with my last lit bead",
     front((-0.5, -17.5), 90, 1.7, 1.5, 1.45, 34, -20),
     {"me": P((-0.5, -17.5), 90, "smile", talks=[("L80", "L80>")])}, fill=[50, "#a8bce8"])
shot("L81", "under one streetlight, two dark cords",
     still((0.6, -29.0, 4.2), (1.0, -31.0, 0.9), 32),
     {"me": P((0.6, -31.0), 180, "smile"), "mum": P((1.5, -31.0), 180, "smile")}, fill=[30, "#a8bce8"])
shot("L82", "morning, a later week: the bright street, Mum at our gate",
     still((-1.0, -13.3, 1.5), (-3.2, -17.5, 1.45), 26),
     {"mum": P((-3.7, -17.5), 90, "smile"), "gatewoman": P((3.7, -13.0), -90, "smile"), "nb1": P((3.7, -10.5), -90, "smile"),
      "nb2": P((3.7, -17.5), -90, "smile")})
shot("L83", "close on Mum's ten lit beads",
     front((-3.7, -17.5), 90, 1.6, 1.5, 1.35, 34, -14),
     {"mum": P((-3.7, -17.5), 90, "smile")})
shot("L84", "night, through the hall's high window: twelve heads in maroon",
     still((TWELFTH[0] + 0.5, -15.4, 2.3), (TWELFTH[0] + 0.1, -8.65, 2.2), 36),
     {**choir(), "grin": P(GRINP, 180, "neutral", sit=True, arms=[14, 14], blink=False),
      "me": P((TWELFTH[0] - 1.3, -14.7), 180, "worried", walks=[("L84>", (TWELFTH[0] - 1.1, -13.4))])}, fill=None)

# ------------------------------------------------------------------------------------------------ build the shots
shots = []
for i, s in enumerate(SH):
    sid = f"S{i + 1:02d}"
    sd = {"id": sid, "cam": s["cam"], "hand": s["hand"], "step": s["step"], "what": s["what"]}
    if i:
        sd["at"] = s["at"]
    if s.get("fill"):
        sd["fill"] = s["fill"]
    shots.append(sd)

for i, s in enumerate(SH):
    at = s["at"] if i else 0
    for who in NAMES:
        if who in s["cast"]:
            p = s["cast"][who]
            put(who, at, p["pos"], p["yaw"], p["expr"], **p["kw"])
            for ref, kw in p["later"]:
                key(who, ref, **kw)
            for ref, pos in p["walks"]:
                walk(who, ref, pos)
            for a, b in p["talks"]:
                talk(who, a, b)
            for a, b in p["sings"]:
                if a:
                    sing(who, a, b)
        else:
            hide(who, at)

# ------------------------------------------------------------------------------------------------ cues
cues = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def tod(at, name, **kw):
    cue(at, "tod", set=name, **kw)


def lt(at, light, v, dur=0.4):
    cue(at, "lt", l=light, v=v, dur=dur)


def beads(at, who, idx, step=0.0, dur=0.45, on=False):
    cue(at, "bead_on" if on else "bead_off", who=who, idx=list(idx), step=step, dur=dur)


tod(0, "morning")
tod("L08", "dusk")
tod("L09", "night")
tod("L10", "morning")
tod("L12", "inside")
tod("L13", "morning")
tod("L17", "inside")
tod("L21", "dusk")
tod("L22", "night")
tod("L28", "inside")
tod("L29", "night")
tod("L35", "dawn")
tod("L39", "inside")
tod("L40", "morning")
tod("L41", "inside")
tod("L76", "night")
tod("L82", "morning")
tod("L84", "night")
# the village is asleep at L32 and on the hill: few lit windows is the TOD "night" (win 1.0); fine either way

# lights, each a ramp that ends on the cut it belongs to (0.3 s before it) or a long slow one in the shot
lt("L10-0.3", "kitchen_day", 1.0, 0.3)
lt("L10-0.3", "kitchen_lamp", 0.12, 0.3)
lt("L09-0.3", "hall_house", 0.34, 0.3)
lt("L09-0.3", "riser", 0.9, 0.3)
lt("L09-0.3", "hall_low", 0.12, 0.3)
lt("L12-0.3", "kitchen_day", 0.0, 0.3)
lt("L12-0.3", "kitchen_lamp", 0.0, 0.3)
lt("L12-0.3", "bed_lamp", 1.0, 0.3)
lt("L12-0.3", "landing", 0.5, 0.3)
lt("L12-0.3", "mum_key", 0.3, 0.3)
lt("L21-0.3", "kitchen_day", 0.12, 0.3)
lt("L21-0.3", "kitchen_lamp", 0.9, 0.3)
lt("L28-0.3", "kitchen_lamp", 0.3, 0.3)
lt("L28-0.3", "kitchen_day", 0.0, 0.3)
lt("L29-0.3", "hall_house", 0.0, 0.3)
lt("L29-0.3", "riser", 0.0, 0.3)
lt("L29-0.3", "hall_low", 0.2, 0.3)
lt("L29-0.3", "door_wedge", 1.0, 0.3)
lt("L35-0.3", "kitchen_lamp", 0.0, 0.3)
lt("L35-0.3", "kitchen_day", 0.5, 0.3)
lt("L39-0.3", "door_wedge", 0.0, 0.3)
lt("L39-0.3", "hall_low", 0.0, 0.3)
lt("L39-0.3", "hall_house", 1.0, 0.3)
lt("L39-0.3", "riser", 0.6, 0.3)
lt("L40-0.3", "kitchen_day", 0.9, 0.3)
lt("L40-0.3", "kitchen_lamp", 0.2, 0.3)
lt("L43-0.3", "kitchen_day", 0.0, 0.3)
lt("L43-0.3", "kitchen_lamp", 0.0, 0.3)
lt("L43-0.3", "landing", 0.5, 0.3)
lt("L43-0.3", "mum_key", 0.0, 0.3)
lt("L45-0.3", "riser", 1.0, 0.3)
lt("L47", "hall_house", 0.1, 2.5)                          # the concert lights go down in one slow ramp
lt("L49", "grin_key", 1.0, 3.0)
lt("L49", "grin_rim", 1.0, 3.0)
lt("L84-0.3", "hall_house", 0.34, 0.3)
lt("L84-0.3", "riser", 0.9, 0.3)
lt("L84-0.3", "grin_key", 0.4, 0.3)
lt("L84-0.3", "grin_rim", 0.7, 0.3)
# props and rows
cue(0, "rows", on=False)
cue("L39", "rows", on=True)
cue("L39", "bunting", on=True)
cue("L45", "audience", on=True)
cue("L66", "audience", on=True)
cue("L76", "audience", on=False)
cue("L84", "rows", on=False)
cue("L84", "bunting", on=False)
cue(0, "props", scarf=False, robe=False)
cue("L24", "props", scarf=False, robe=True)
cue("L28", "props", scarf=False, robe=False)
cue("L30", "props", scarf=True, robe=False)
cue("L39", "props", scarf=False, robe=False)
cue("L67", "props", scarf=False, robe=False)
# the chairs
cue("L23", "c12", deg=-8, dur=0.0)
cue("L26.1", "c12", deg=-18, dur=0.0)
cue("L27", "c12", deg=-29, dur=0.0)
cue("L28", "c12", deg=0, dur=0.0)
cue("L31", "turned", on=True)
cue("L39", "turned", on=False)
# doors: the hall door stands open at night (L29 to L39)
cue("L29", "hdoor", deg=100)
cue("L39", "hdoor", deg=0)
cue("L18", "door", deg=-55, dur=0.0)
cue("L43", "door", deg=-40, dur=0.0)
cue("L74", "door", deg=-45, dur=0.0)
cue("L74+0.6", "door", deg=0, dur=0.8)
cue("L75", "door", deg=0, dur=0.0)
cue("L12", "door", deg=0, dur=0.0)
# Mum's scarf is worn at the hall and at the bedroom door through L27
cue(0, "scarf", who=[])
cue("L17", "scarf", who=["mumr"])
cue("L18", "scarf", who=["mum", "mumr"])
cue("L28", "scarf", who=[])
cue("L40", "scarf", who=[])
# the bulge under my knit, and the long cord
cue(0, "bulge", on=True)
cue("L70", "bulge", on=False)
cue("L75", "bulge", on=True)
cue("L76", "bulge", on=False)
cue(0, "cord", on=False)
cue("L70", "cord", on=True)
cue("L75", "cord", on=False)
cue("L71", "cordfade", step=0.03)
# beads: (who, indices) fade; indices count from 0, the last dark first. Ron's seven are indices 0 to 6 of his own.
beads("L03.1+0.15", "gateman", [9])
beads("L04.1", "groom", [9, 8], step=0.35)
beads("L06+0.05", "postman", list(range(9, 0, -1)), step=0.12)
beads("L06.2+0.1", "postman", [0])
beads("L19.0+0.05", "mum", [9, 8], step=0.2)
beads("L19.1+0.05", "mum", [7, 6], step=0.2)
beads("L19.2+0.05", "mum", [5, 4], step=0.2)
beads("L19.3+0.0", "mum", [3, 2, 1], step=0.2)
beads("L19.4+0.05", "mum", [0])
beads("L39-0.01", "mum", list(range(10)), dur=0.0, on=True)            # a new day: her ten are lit again
beads("L37+0.35", "ron", list(range(7)), step=0.2)
beads("L57.1", "mum", [9, 8, 7, 6, 5, 4, 3], step=0.34)
beads("L59.2+0.3", "mum", [2])
beads("L60+0.1", "mum", [1])
beads("L76+0.4", "me", [9, 8, 7, 6], step=0.3)
beads("L77", "me", [5, 4], step=0.3)
beads("L78+0.1", "me", [3, 2, 1], step=0.25)
beads("L79", "mum", [0])
beads("L80", "me", [0])
beads("L82-0.01", "mum", list(range(10)), dur=0.0, on=True)
beads("L82-0.01", "me", list(range(10)), dur=0.0, on=True)

sfx = [
    {"at": "L03.1+0.2", "kind": "click", "db": -18},
    {"at": "L06.2+0.2", "kind": "click", "db": -18},
    {"at": "L19.4+0.1", "kind": "click", "db": -20},
    {"at": "P01+0.15", "kind": "creak", "db": -16, "dur": 0.7},
    {"at": "L30", "kind": "hit", "db": -9},
    {"at": "L29", "kind": "creak", "db": -22, "dur": 1.6},
    {"at": "L37+0.35", "kind": "click", "db": -22},
    {"at": "L50", "kind": "sting", "db": -13},
    {"at": "L53", "kind": "hit", "db": -11},
    {"at": "L62", "kind": "riser", "db": -20, "dur": 1.2},
    {"at": "P02+0.1", "kind": "hit", "db": -10},
    {"at": "L71", "kind": "glide", "db": -22, "dur": 2.2},
    {"at": "L74+0.5", "kind": "door", "db": -14, "dur": 0.9},
    {"at": "L84+0.4", "kind": "bell", "db": -18, "dur": 2.0},
]

story = {
    "slug": "ep46-choir-hall",
    "title": "In this world, everyone gets ten words a day.",
    "made_for_kids": False,
    "premise": "In a hillside village everyone gets ten words a day, worn as ten glass beads that go dark one per word. Mum leads the village choir and spends all ten of hers at my door every night, asking me back to the twelfth chair. I haven't spent a word in three years and people call me the careful one. The week before the winter concert, the empty twelfth chair keeps turning toward her.",
    "twist": "I was never careful: I stopped talking to Mum three years ago, and every unspent word piled up in the lump under my jumper. The twelfth chair was mine all along, and while I stayed away something kept my place.",
    "world": "a hillside village in early winter: render cottages with painted gates and frosted hedges, a narrow house with a round-table kitchen, and a plain wooden village hall with a riser of twelve chairs under one enamel lamp",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff7f9e",
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#c8d4de", "fog_density": 0.01, "fog_start": 6.0, "sky": "#b6cde0", "sky_strength": 1.0,
             "exposure": 0.0, "flash_safe": True},
    "grade": {"shadows": [-0.01, 0.0, 0.05], "highlights": [0.04, 0.015, -0.03], "saturation": 0.92, "contrast": 1.06,
              "vignette": 0.34, "bloom": 0.2, "grain": 0.012},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 57, "mode": "minor", "bpm": 74, "seed": 46,
              "sections": [
                  {"at": 0, "voices": ["choir", "pad", "bubble"], "energy": 0.22},
                  {"at": "L30", "voices": ["drone", "pad", "choir"], "energy": 0.42},
                  {"at": "L56", "voices": ["drone", "choir", "pad", "piano"], "energy": 0.55},
                  {"at": "L66", "voices": ["drone", "choir", "pad"], "energy": 0.6},
                  {"at": "L73", "voices": ["drone", "pad", "piano", "bubble"], "energy": 0.45, "mode": "major", "root": 57},
                  {"at": "L82", "voices": ["drone"], "energy": 0.4},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "L12", "lufs": -38},
                  {"kind": "room", "from": "L12", "to": "L28", "lufs": -42},
                  {"kind": "wind", "from": "L25", "to": "L28", "lufs": -34},
                  {"kind": "wind", "from": "L29", "to": "L35", "lufs": -34},
                  {"kind": "room", "from": "L45", "to": "L49", "lufs": -38},
                  {"kind": "wind", "from": "L76", "to": "L82", "lufs": -34},
                  {"kind": "wind", "from": "L84", "to": "end", "lufs": -36},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "P01>", "keep": ["creak"]},
                              {"from": "P02-0.1", "to": "L63", "keep": ["hit"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
