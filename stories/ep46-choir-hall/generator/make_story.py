"""Writes ../story.json for ep46 "choir hall" (rebuild as `heard-ten`, 2026-11-03).

Run from anywhere: python stories/ep46-choir-hall/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (time of day, lights, beads, chairs), the score and the sound.

Places are set.py's metres (see its docstring). A character with yaw 0 faces -y, yaw 90 faces +x, yaw 180 faces +y.
Rig keys read by set.py (acting.py ignores them): sit, bend, roll, tilt, lunge.
Faces: `talking` is a neutral face with a mouth flap, `sing` is a neutral face with a held round mouth, `listening` is
the "polite" face with a tilt of the head, `asleep` is the engine's own.
"""
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

HX = 100.0
KX, KY = 40.0, 0.0
BX = 60.0

# ------------------------------------------------------------------------------------------------ lines
LOOP = 0.25
lines.append({"id": "P99", "pause": LOOP, "chunks": []})


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
LASH = {"eyes": "lashes", "brows": True, "ink": "#1a1214"}
cast = {
    "me": person("#e0b08a", "#22304a", "#7b7f86", "#5a3b24", "cap", "#3a2418", "knit", "#1a2438", "#22304a"),
    "mum": person("#e8bd98", "#6b4a6e", "#4a4a52", "#3a2a22", "bun", "#7a6858", "knit", "#563a58", "#f0e6d0", LASH,
                  ["coat"], zip_c="#563a58"),
    "mumr": person("#e8bd98", "#4c3038", "#4c3038", "#2a2022", "bun", "#7a6858", "solid", None, "#f3efe6", LASH,
                   ["coat"], zip_c="#4a2230"),
    "ron": person("#e2b896", "#6b4a2e", "#4a463e", "#2a2a22", "none", "#e8e6e0", "knit", "#563a22", "#d8d0be", TIRED,
                  ["coat"], zip_c="#5a3a22", height=0.97),
    "postman": person("#d9a07c", "#22304a", "#22304a", "#1a1a1a", "cap", "#2a1d15", "solid", None, "#b0302a", None, None,
                      "ballcap", "#22304a"),
    "gatewoman": person("#8c5c40", "#d8c8a0", "#5a4634", "#3a2a22", "bun", "#1a1412", "knit", "#b8a880", None, LASH),
    "gateman": person("#f0c8a0", "#6a7a4a", "#4a4a40", "#3a2a22", "cap", "#9a5a32", "plaid", "#4a5a30"),
    "nb1": person("#d9a07c", "#8a3a3a", "#3a3a48", "#2a2420", "long", "#4a3a2a", "knit", "#6a2a2a", None, LASH),
    "nb2": person("#e0b08a", "#3a5a7a", "#4a4a4a", "#2a2420", "swoop", "#7a4a2a", "stripes", "#4a7a9a"),
}
SKINS = ["#e0b08a", "#c68a62", "#8c5c40", "#f0c8a0", "#d9a07c", "#a8744e", "#e8bd98", "#7a4a34"]
STYLES = ["cap", "spiky", "swoop", "long", "bun", "buzz", "cap", "long", "bun", "swoop", "spiky"]
HAIRS = ["#2a1d15", "#6a5a3a", "#1a1412", "#9a5a32", "#8a8a8a", "#3a2a22", "#4a3a2a", "#171717", "#7a4a2a", "#c8b48a", "#2a1d15"]
for i in range(11):
    cast[f"c{i + 1}"] = person(SKINS[i % 8], "#4c3038", "#4c3038", "#2a2022", STYLES[i], HAIRS[i], "solid", None, "#f3efe6",
                               dict(FACE), ["coat"], zip_c="#4a2230", height=[1.0, 0.96, 1.03, 0.98, 1.02, 0.95, 1.0, 1.04, 0.97, 1.01, 0.99][i])
cast["grin"] = person("#d8c0a6", "#4c3038", "#4c3038", "#2a2022", "buzz", "#5a4030", "solid", None, "#f3efe6",
                      {"eyes": "round", "brows": True, "ink": "#1a1214", "mouth": "none"}, ["coat"], zip_c="#4a2230", height=1.35)
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
    """A camera `dist` metres in front of someone (along their facing), turned `side` degrees round them."""
    dist = dist * 1.25 if dist < 2.5 else dist
    a = math.radians(yaw + side)
    loc = (pos[0] + math.sin(a) * dist, pos[1] - math.cos(a) * dist, h)
    return still(loc, (pos[0], pos[1], tz + dz), lens)


WIN = (HX + 2.8, 12.4, 2.3)       # outside the hall's back window


def winshot(tgt, lens, loc=WIN):
    return still(loc, tgt, lens)


def sit_z(step_top):
    return round(step_top - 0.06, 3)


def shift(ref, d):
    """A time reference moved by d seconds (the grammar takes one offset)."""
    if isinstance(ref, (int, float)):
        return ref + d
    m = re.match(r"^(.*?)([+-]\d+(?:\.\d+)?)?$", ref)
    base, off = m.group(1), float(m.group(2) or 0) + d
    return base if abs(off) < 1e-9 else f"{base}{off:+.2f}"


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


def sing(who, a, b, m=0.8):
    acting[who].append({"from": a, "to": b, "mouth": [m, m]})


def P(pos, yaw=0, expr="neutral", later=(), walks=(), talks=(), sings=(), **kw):
    return {"pos": pos, "yaw": yaw, "expr": expr, "later": list(later), "walks": list(walks), "talks": list(talks),
            "sings": list(sings), "kw": kw}


def listen(pos, yaw=0, tilt=12, **kw):
    """`listening`: head tilted, mouth shut, a small smile."""
    return P(pos, yaw, "polite", tilt=tilt, **kw)


def PK(pos, yaw, expr="neutral", **kw):
    """Someone seated at the kitchen table."""
    kw.setdefault("sit", True)
    return P(pos, yaw, expr, **kw)


def listenk(pos, yaw=180, tilt=12, **kw):
    return listen(pos, yaw, tilt, sit=True, **kw)


GRINP = (TWELFTH[0], TWELFTH[1], sit_z(TWELFTH[2]) - 0.12)


def G(**kw):
    """The Grin, seated in the twelfth chair (set lower than the cast's seat because it is 1.35x)."""
    k = {"sit": True, "arms": [14, 14], "blink": False, **kw}
    yaw = k.pop("yaw", 180)
    return P(GRINP, yaw, "neutral", **k)


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


def hall(sing_from=None, sing_to=None, grin=True, skip=(), **gk):
    """The twelve in their chairs: eleven singers and the Grin, always in the twelfth (far right, top step)."""
    out = choir(sing_from, sing_to, skip=skip)
    if grin:
        out["grin"] = G(**gk)
    return out


# ------------------------------------------------------------------------------------------------ shots
SH = []


def shot(at, what, cam, cast_, step=2, fill=None, hand=0.006, **kw):
    SH.append(dict(at=at, what=what, cam=cam, cast=cast_, step=step, fill=fill, hand=hand, **kw))


# street places (left side x<0 faces +x, right side x>0 faces -x; plot k gate at y=-7k-3.5)
GW = (-3.7, -3.5)                      # the woman at her sage gate (left plot 0)
GM = (-1.7, -3.5)                      # the man, in the lane at her gate
MOM_DOOR = (-5.0, -10.5)               # Mom's front door step (left plot 1)
OURS = (-3.7, -17.5)                   # my place (left plot 2, duck-egg gate)
RON = (-3.7, -24.5)                    # old Ron (left plot 3)
NB1 = (3.7, -10.5)
NB2 = (3.7, -17.5)
MK = (KX - 0.2, KY - 1.22, -0.1)       # Mom's seat at the kitchen table (south, faces +y)
MEK = (KX - 0.2, KY + 0.62, -0.1)      # my seat (north, faces -y)
TW = TWELFTH[0]

# ---- 01 the rule and the hook, L01 to L06
shot(0, "Mom's face and cord at breakfast, nine dark, the tenth fading on DARK",
     front(MK, 180, 1.5, 1.25, 1.2, 30, 0),
     {"mum": listenk(MK, 180, 12, look=[0.5, 0.0])}, hand=0.004)
shot("L01.4+0.5", "punch in on the dark tenth bead",
     front(MK, 180, 1.0, 1.05, 1.07, 36, 0),
     {"mum": listenk(MK, 180, 12, look=[0.5, 0.0])})
shot("L02", "ten amber beads over a cardigan in low sun, frost behind",
     still((-2.55, -2.5, 1.2), (-3.7, -3.5, 1.1), 36),
     {"gatewoman": P(GW, yaw_to(GW, (-2.55, -2.5)), "smile")})
shot("L03", "a man at her gate talks to the neighbour",
     still((-1.0, -1.6, 1.5), (-2.9, -3.5, 1.35), 30),
     {"gateman": P(GM, -90, "neutral", talks=[("L03", "L03.2")], arms=[40, 0]),
      "gatewoman": P(GW, 90, "neutral")})
shot("L03.2", "tight: one bead fades on the one he's talking to",
     still((-2.45, -3.0, 1.1), (-3.7, -3.5, 1.05), 40),
     {"gatewoman": P(GW, yaw_to(GW, (-2.45, -3.0)), "neutral")})
shot("L04", "all ten dark, eyes drifting past him; his mouth goes on",
     still((-1.3, -1.9, 1.5), (-3.7, -3.5, 1.45), 30),
     {"gatewoman": P(GW, yaw_to(GW, (-1.3, -1.9)), "neutral", look=[1.0, 0.2]),
      "gateman": P(GM, -90, "neutral", talks=[("L04", "L04>")])})
shot("L05", "she turns toward her own front door, head tilted",
     still((-1.4, -4.6, 1.5), (-3.7, -3.5, 1.45), 30),
     {"gatewoman": P(GW, 0, "polite", tilt=12, head=[0, 0], later=[("L05+0.2", dict(head=[-40, 0]))])})
shot("L06", "Mom at her door, thanking me, ten lit",
     front(MOM_DOOR, 90, 2.4, 1.55, 1.45, 32, 25),
     {"mum": P(MOM_DOOR, 90, "smile", arms=[60, 0], talks=[("L06", "L06.2")])})
shot("L06.3", "me on the step, worried, ten lit",
     front((-3.4, -10.5), -90, 2.6, 1.55, 1.45, 30, 70),
     {"me": P((-3.4, -10.5), -90, "worried"),
      "mum": P(MOM_DOOR, 90, "smile")})

# ---- 02 the village, L07 to L12
POSTMAN = (0.0, -9.5)
shot("L07", "wide down the lane: three gates talking at the postman, who says nothing",
     still((0.3, -0.8, 1.7), (0.0, -14.0, 1.3), 26),
     {"postman": P(POSTMAN, 0, "neutral"),
      "gateman": P((-3.7, -3.5), 90, "neutral", arms=[40, 0], talks=[("L07", "L07.4")]),
      "gatewoman": P((-3.7, -10.5), 90, "neutral", arms=[0, 40], talks=[("L07.1", "L07.4")]),
      "nb1": P(NB1, -90, "neutral", arms=[40, 0], talks=[("L07.2", "L07.4")]),
      "nb2": P(NB2, -90, "neutral", arms=[0, 40], talks=[("L07", "L07.4")])})
shot("L07.2", "close: his last bead fades",
     front(POSTMAN, 0, 1.3, 1.1, 1.05, 36),
     {"postman": P(POSTMAN, 0, "neutral")})
shot("L07.4", "the postman walks on up the lane, eyes unfocused, cord dark",
     still((-0.3, -26.0, 1.5), (0.0, -16.0, 1.35), 28),
     {"postman": P((0.0, -11.0), 0, "blank", walks=[("L08>", (0.0, -20.0))], look=[0.0, 0.6])})
shot("L08.1", "a neighbour waves from a gate; he doesn't turn",
     still((-0.9, -13.5, 1.5), (3.4, -17.5, 1.35), 26),
     {"postman": P((0.5, -13.5), 0, "blank", walks=[("L08>", (0.5, -22.0))], look=[0.0, 0.6]),
      "nb2": P(NB2, -90, "smile", arms=[160, 0], later=[("L08.1+0.3", dict(arms=[130, 0])), ("L08.1+0.6", dict(arms=[165, 0])),
                                                         ("L08.1+0.9", dict(arms=[130, 0]))])})
shot("L09", "Old Ron at his gate in the morning, earmuffs, ten lit",
     front(RON, 90, 3.0, 1.45, 1.4, 28, 14),
     {"ron": P(RON, 90, "angry")})
shot("L09.2+0.1", "punch in on the earmuffs",
     front(RON, 90, 1.5, 1.7, 1.72, 34, 12),
     {"ron": P(RON, 90, "angry")})
shot("L10", "close on Ron's cord: ten fat amber beads",
     front(RON, 90, 1.2, 1.15, 1.1, 36, 12),
     {"ron": P(RON, 90, "angry")})
shot("L11", "through the hall window at night: the round mouths, every bead lit",
     winshot((HX + 0.3, -7.6, 1.9), 85),
     {**hall("L11", "L11>"), "mumr": P((HX + 1.2, -3.0), 0, "smile", arms=[70, 20])})
shot("L12", "wide through the window: twelve in maroon, the far right one small and bare-necked",
     winshot((HX - 0.3, -7.6, 1.9), 48, (HX + 2.8, 12.4, 2.2)),
     {**hall(head=[0, 14]), "mumr": P((HX + 1.2, -3.0), 0, "smile", arms=[70, 20])})
shot("L12.2", "close from behind: the bare neck above the white collar, the singers beyond with lit cords",
     still((TW - 2.9, -10.8, 2.9), (TW + 0.1, -8.65, 2.5), 32),
     {**hall(head=[0, 14])}, fill=[150, "#ffe2c4"])

# ---- 03 me and Mom, L13 to L23
ME_L = (0.9, -10.5)
shot("L13", "me in the morning sun, talking, face clear, ten lit",
     front(ME_L, 180, 2.6, 1.55, 1.5, 30, 0),
     {"me": P(ME_L, 180, "neutral", talks=[("L13", "L13>")], arms=[40, 40]),
      "nb1": P(NB1, -90, "neutral")})
shot("L13.2", "me talking at two neighbours at once; their beads fade, mine stay lit",
     still((1.2, -6.5, 1.55), (1.8, -12.5, 1.4), 30),
     {"me": P((1.6, -11.5), 90, "neutral", talks=[("L13.1", "L14")], arms=[60, 60]),
      "nb1": P((3.7, -10.5), -90, "neutral"), "nb2": P((3.7, -12.7), -90, "neutral")})
shot("L14", "close on my collar: ten lit",
     front(ME_L, 180, 1.35, 1.2, 1.15, 34),
     {"me": P(ME_L, 180, "neutral", talks=[("L14", "L14>")])})
shot("L15", "nb1 opens her mouth to say something; I talk right over her; she shuts it",
     front(NB1, -90, 2.6, 1.5, 1.4, 30, -35),
     {"nb1": P(NB1, -90, "neutral", arms=[60, 0], talks=[("L15", "L15.1", 0.5)]),
      "me": P((1.6, -9.0), 90, "neutral", talks=[("L15", "L15>")], arms=[50, 50])})
shot("L16", "two neighbours nod at me as I pass",
     still((-1.6, -6.0, 1.5), (-3.6, -10.5, 1.4), 28),
     {"gateman": P((-3.7, -10.5), 90, "smile", later=[("L16+0.2", dict(head=[0, 12])), ("L16+0.6", dict(head=[0, -2]))]),
      "gatewoman": P((-3.7, -8.5), 90, "smile")})
shot("L17", "my place, the duck-egg gate, me stepping out into the frost",
     still((0.5, -13.5, 1.5), (-3.4, -17.5, 1.4), 26),
     {"me": P((-3.9, -17.5), 90, "neutral", walks=[("L17>", (-1.4, -17.5))])})
shot("L18", "me climbing the steep lane in the low sun toward a cottage halfway up",
     still((0.3, -29.0, 1.6), (0.0, -14.0, 1.3), 26),
     {"me": P((0.0, -22.0), 180, "neutral", walks=[("L18>", (0.0, -15.0))])})
shot("L18.3", "me reaching her gate, coming toward the camera",
     front((0.0, -9.5), 180, 3.0, 1.55, 1.4, 28),
     {"me": P((0.0, -14.0), 180, "neutral", walks=[("L18>", (0.0, -9.5))])})
HALL_MOM = (HX + 1.2, -3.0)
shot("L19", "Mom at her stand in the hall, conducting, ten lit",
     front(HALL_MOM, 0, 2.6, 1.55, 1.45, 30, 60),
     {"mumr": P(HALL_MOM, 0, "smile", arms=[75, 25]), **hall("L19", "L19>")})
shot("L20", "Mom across the round table, a tired smile, mouth open on a word",
     front(MK, 180, 2.6, 1.55, 1.4, 30, -25),
     {"mum": PK(MK, 180, "smile", talks=[("L20", "L20.1", 0.5)])})
shot("L21", "me at the table, talking, both hands going",
     front(MEK, 0, 2.6, 1.55, 1.4, 30, 25),
     {"me": PK(MEK, 0, "neutral", talks=[("L21", "L21>")], arms=[50, 50], side=[10, 10])})
shot("L22", "two shot: Mom starts a sentence and I talk right over her",
     still((KX + 1.9, KY - 0.3, 1.5), (KX - 0.2, KY - 0.3, 1.35), 16),
     {"mum": PK(MK, 180, "neutral", talks=[("L22", "L22.1", 0.5)]),
      "me": PK(MEK, 0, "neutral", talks=[("L22", "L22>")], arms=[45, 45])})
shot("L22.3", "Mom shuts her mouth, listening, a small smile",
     front(MK, 180, 1.7, 1.5, 1.42, 34, -15),
     {"mum": listenk(MK, 180, 12)})
shot("L23", "close on Mom's cord, the beads fading in turn",
     front(MK, 180, 1.35, 1.2, 1.12, 34),
     {"mum": listenk(MK, 180, 10)})
shot("L23.3", "the kettle on the stove, Mom's dark cord at the frame edge",
     still((KX + 0.3, KY - 0.6, 1.3), (KX + 0.5, KY - 1.9, 1.0), 30),
     {"mum": listenk((KX - 0.9, KY - 1.22, -0.1), 180, 8)})

# ---- 04 the week, L24 to L27
shot("L24", "Mom's kitchen at night: two cups, Mom leans toward the empty side and nods",
     still((KX + 1.8, KY - 0.2, 1.5), (KX - 0.2, KY - 0.3, 1.2), 28),
     {"mum": listenk(MK, 180, 12, later=[("L24.1", dict(head=[0, 8])), ("L24.2", dict(head=[0, -4])), ("L24.3", dict(head=[0, 8]))])})
shot("L24.3", "the clock with no numbers",
     still((KX + 1.3, KY - 0.6, 1.8), (KX + 2.15, KY - 0.6, 1.85), 32),
     {})
shot("L25", "my bedroom at night: me asleep, ten lit",
     still((BX + 1.0, -0.2, 1.25), (BX - 0.7, -0.2, 1.1), 30),
     {"me": P((BX - 0.7, -0.2, 0.0), 90, "asleep", sit=True)})
shot("L25.3", "breakfast the next morning: me worried, Mom laughs at something I never said",
     still((KX + 1.9, KY - 0.3, 1.5), (KX - 0.2, KY - 0.3, 1.35), 16),
     {"me": PK(MEK, 0, "worried"),
      "mum": PK(MK, 180, "laugh", later=[("L25.3+0.2", dict(head=[0, -6])), ("L25.3+0.5", dict(head=[0, 4]))])})
shot("L26", "through the hall window: Mom conducting, turned to the far right",
     winshot((HX + 0.3, -5.5, 1.7), 36),
     {**hall(), "mumr": P(HALL_MOM, -50, "neutral", arms=[75, 25])})
shot("L26.2", "Mom's face, listening, nodding to a beat nobody sings",
     front(HALL_MOM, -50, 2.2, 1.6, 1.5, 34),
     {"mumr": P(HALL_MOM, -50, "polite", tilt=10, later=[("L27.1", dict(head=[0, 8])), ("L27.1+0.3", dict(head=[0, -2])),
                                                           ("L27.1+0.6", dict(head=[0, 8]))])})
shot("L27.1", "from behind the riser: the back of the twelfth singer's head, a thin black line round it",
     still((TW + 0.15, -11.0, 2.9), (TW, TWELFTH[1], 2.6), 28),
     {**hall()})

# ---- 05 Thursday, L28 to L34
shot("L28", "Mom's kitchen at night, the window black, me in the doorway, worried",
     still((KX + 1.9, KY + 1.2, 1.5), (KX - 0.6, KY - 1.0, 1.3), 28),
     {"me": P((KX - 0.9, KY - 0.4), 180, "worried")}, fill=[40, "#ffd9a0"])
shot("P01", "the hall at night from the gravel path, one low window glowing amber",
     still((HX - 10.0, -0.8, 1.5), (HX - 5.15, -3.7, 1.7), 26),
     {"mum": listen((HX - 2.4, -1.0, 0.0), 0, 8, sit=True)}, step=4)
SIDE_WIN = (HX - 6.3, -4.4, 1.55)
shot("L29", "me at the side window, worried, my ten lit in the glow (seen through the panes)",
     still((HX - 3.9, -1.6, 1.6), (HX - 5.95, -3.5, 1.5), 30),
     {"me": P((HX - 5.95, -3.5), 90, "worried"),
      "mum": listen((HX - 2.4, -1.0, 0.0), 0, 8, sit=True)}, fill=[60, "#ffd9a0"])
shot("L29.3", "through the panes: Mom alone in the front row in her coat, the lamp on",
     still((HX - 6.3, -4.0, 1.5), (HX - 2.4, -1.4, 1.15), 30),
     {"mum": listen((HX - 2.4, -1.0, 0.0), 0, 8, sit=True), "grin": G()}, fill=[160, "#ffd9a0"])
shot("L30", "Mom nodding, listening",
     still((HX - 6.0, -4.2, 1.45), (HX - 2.4, -1.0, 1.2), 46),
     {"mum": listen((HX - 2.4, -1.0, 0.0), 0, 12, sit=True, later=[("L30+0.3", dict(head=[0, 8])), ("L30+0.7", dict(head=[0, -2])),
                                                                       ("L30+1.0", dict(head=[0, 8]))]), "grin": G()})
shot("L30.1+0.3", "Mom answering, mouth open, then a laugh",
     still((HX - 6.0, -4.0, 1.45), (HX - 2.4, -1.0, 1.25), 44),
     {"mum": P((HX - 2.4, -1.0, 0.0), 0, "smile", sit=True, tilt=8, talks=[("L30.1", "L30.1>")],
               later=[("L30.1>", dict(expr="laugh"))]), "grin": G()})
shot("L31", "close on me at the glass, scared, my ten lit",
     still((HX - 4.2, -1.9, 1.62), (HX - 5.95, -3.5, 1.55), 40),
     {"me": P((HX - 5.95, -3.5), 90, "scared")}, fill=[60, "#ffd9a0"])
shot("L32", "wide through the glass: the twelfth singer's upper body leans out, its face turned toward her",
     still((HX - 6.2, -3.4, 1.6), (HX - 1.65, -8.65, 2.0), 42),
     {"mum": listen((HX - 2.4, -1.0, 0.0), 0, 8, sit=True),
      "grin": G(bend=24, head=[-20, 8])})
shot("L32.3", "close on Mom's dark cord",
     still((HX - 5.9, -4.2, 1.15), (HX - 2.4, -1.0, 1.1), 50),
     {"mum": listen((HX - 2.4, -1.0, 0.0), 0, 8, sit=True), "grin": G(bend=24, head=[-20, 8])})
LANE = (0.0, -11.0)
shot("L33", "Mom and me on the steep lane at night under one streetlight, both cords in frame",
     still((2.0, -8.5, 1.5), (0.0, -12.5, 1.3), 30),
     {"me": P((0.5, -11.5), 180, "worried", walks=[("L33>", (0.5, -14.0))]),
      "mum": listen((-0.5, -11.5), 180, 6, walks=[("L33>", (-0.5, -14.0))])}, fill=[50, "#a8bce8"])
shot("L34", "Mom walking, chatting past me to the empty air on my far side",
     front((-0.4, -12.5), 180, 2.0, 1.5, 1.45, 32, -30),
     {"mum": P((-0.4, -12.5), 180, "smile", walks=[("L34>", (-0.4, -17.0))], talks=[("L34", "L34.4")]),
      "me": P((0.6, -12.5), 180, "worried", walks=[("L34>", (0.6, -17.0))])}, fill=[50, "#a8bce8"])
shot("L34.2", "me glancing at that side, worried, cord lit",
     front((0.6, -15.0), 180, 2.0, 1.5, 1.45, 32, 30),
     {"me": P((0.6, -15.0), 180, "worried", look=[-0.8, 0.0]),
      "mum": listen((-0.4, -15.0), 180, 8)}, fill=[50, "#a8bce8"])
shot("L34.5", "wide from behind: the two of us on the lane, nothing beside me but the hedge",
     still((0.3, -8.0, 1.8), (0.4, -22.0, 1.0), 26),
     {"me": P((0.9, -17.0), 180, "worried", walks=[("L34>", (0.9, -20.0))]),
      "mum": P((-0.4, -17.0), 180, "smile", walks=[("L34>", (-0.4, -20.0))])}, fill=[50, "#a8bce8"])

# ---- 06 the concert, L35 to L46
MUMX = TW - 1.1
MUMP = (MUMX, TWELFTH[1], 0.9)           # Mom on the top step beside the twelfth chair
ME_BACK = (HX + 3.8, 7.6)
shot("L35", "the hall is packed: bunting, the audience, the twelve singing 'ah'",
     still((HX + 1.2, 8.6, 2.1), (HX - 0.2, -7.0, 1.7), 20),
     {**hall("L35", "L36"), "mumr": P(HALL_MOM, 0, "neutral", arms=[40, 40])}, step=4)
shot("L36", "Mom at her stand, smiling",
     front(HALL_MOM, 0, 2.6, 1.55, 1.45, 30, 60),
     {"mumr": P(HALL_MOM, 0, "smile", arms=[60, 30]), **hall("L36", "L36.1")})
shot("L36.2", "me by the back wall, ten lit",
     still((HX + 3.4, 4.6, 1.5), (ME_BACK[0], ME_BACK[1], 1.5), 28),
     {"me": P(ME_BACK, 0, "neutral")})
shot("L37", "close on Mom's cord, all ten dark",
     front(HALL_MOM, 0, 1.4, 1.2, 1.15, 34, 40),
     {"mumr": P(HALL_MOM, 0, "smile", arms=[60, 30])})
shot("L38", "wide from the back: the hall lights go down in one slow ramp",
     still((HX + 1.4, 8.6, 2.1), (HX - 0.2, -7.0, 1.7), 20),
     {**hall(), "mumr": P(HALL_MOM, 0, "neutral", arms=[40, 40])}, step=4)
shot("L39", "the enamel lamp: a warm pool on the choir, the far right chair at its edge",
     still((HX - 0.6, -1.8, 0.9), (HX - 1.0, -7.4, 2.4), 24),
     {**hall()})
shot("L39.2", "cut away to Mom at the stand, listening",
     front(HALL_MOM, 0, 2.4, 1.55, 1.45, 30, 55),
     {"mumr": P(HALL_MOM, 0, "polite", tilt=10)})
shot("L40.2", "its head now turned toward the hall, mid shot",
     still((HX - 1.4, -3.4, 2.55), (TW, TWELFTH[1], 2.1), 48),
     {**hall()})
GCAM = (TW + 0.5, -5.2)
shot("L41", "front, lamp key: the grin and the teeth, the black line across the cheeks and round the sides",
     still((GCAM[0], GCAM[1], 3.0), (TW, TWELFTH[1], 2.6), 44),
     {**choir(skip=("c4", "c8")), "grin": G(yaw=yaw_to(GRINP, GCAM))}, fill=[180, "#ffe2c4"])
shot("L41.2", "punch in on the eyes",
     still((GCAM[0] - 0.1, -6.9, 2.9), (TW, TWELFTH[1], 2.75), 30),
     {**choir(skip=("c4", "c8")), "grin": G(yaw=yaw_to(GRINP, GCAM))}, fill=[150, "#ffe2c4"])
shot("L42", "from behind the riser: the seam meeting at mouth height",
     still((TW + 0.15, -11.0, 3.0), (TW, TWELFTH[1], 2.65), 28),
     {**hall()})
GF = [170, "#ffe2c4"]
shot("L43", "the Grin leans out of its chair to Mom's ear, a hand's width off, never touching",
     still((MUMX - 1.7, -5.0, 3.0), (MUMX + 0.7, TWELFTH[1], 2.55), 29),
     {**choir(skip=("c4",)), "mumr": P(MUMP, 180, "smile", arms=[10, 10], head=[0, 0]),
      "grin": G(head=[52, 0], roll=26, tilt=-18)}, fill=GF)
shot("L44", "close on its still grin beside her ear, the eye highlight brightest",
     still((MUMX - 0.5, -6.8, 2.5), (MUMX + 0.3, TWELFTH[1], 2.45), 44),
     {"mumr": P(MUMP, 180, "smile"), "grin": G(head=[62, 0], roll=38, tilt=-26)}, fill=GF)
shot("L44.2", "me at the back, scared, ten lit, as she smiles at ME",
     move(((HX + 3.4, 4.6, 1.5), (ME_BACK[0], ME_BACK[1], 1.5)), ((HX + 2.6, 5.4, 1.5), (ME_BACK[0], ME_BACK[1], 1.5)), 28, 32),
     {"me": P(ME_BACK, 0, "scared")})
shot("L44.5+0.2", "Mom steps away from her bare stand toward the riser",
     still((HX + 3.0, -1.2, 1.8), (HX - 0.4, -4.2, 1.4), 30),
     {**hall(), "mumr": P(HALL_MOM, 0, "smile", walks=[("L45>", (HX - 2.3, -4.1))])}, step=2)
shot("L45.1+0.2", "low: Mom on the first riser step, the singers either side still on their ah, the Grin above leaning down",
     still((MUMX + 1.6, -3.9, 0.9), (MUMX, -5.65, 1.9), 30),
     {**choir(skip=("c4",)), "mumr": P((MUMX, -5.65, 0.3), 180, "soft"),
      "grin": G(head=[40, 0], roll=14, tilt=-14, bend=18)}, fill=GF)
shot("L46", "me at the back, mouth open on her name, ten lit",
     still((HX + 3.4, 4.6, 1.5), (ME_BACK[0], ME_BACK[1], 1.5), 28),
     {"me": P(ME_BACK, 0, "worried", talks=[("L46.1", "L46.2")])})
shot("L46.3", "Mom's face, unblinking",
     front(MUMP, 180, 1.6, 2.6, 2.5, 38, 6),
     {"mumr": P(MUMP, 180, "soft", blink=False)})

# ---- 07 the reveal and the ah, L47 to L58
shot("P02", "hold on Mom's face",
     front(MUMP, 180, 1.6, 2.6, 2.5, 38, 6),
     {"mumr": P(MUMP, 180, "soft", blink=False)}, step=4)
REV_CAM = ((MUMX - 1.0, -4.0, 3.2), (MUMX + 0.6, -7.0, 1.7), 24)
REV_CAST = {**choir(skip=("c4",)), "mumr": P(MUMP, 180, "soft"), "grin": G(head=[62, 0], roll=38, tilt=-26),
            "me": P((HX + 0.6, 5.0), 0, "scared")}
shot("L47", "the reveal picture, wide: Mom's dark cord, the Grin at her ear, me at the back with ten lit",
     still(*REV_CAM), REV_CAST, fill=[90, "#ffe2c4"])
shot("L47.2", "punch in on Mom's dark cord",
     front(MUMP, 180, 1.4, 2.0, 1.9, 34, 12),
     {"mumr": P(MUMP, 180, "soft"), "grin": G(head=[62, 0], roll=38, tilt=-26)}, fill=GF)
shot("L48", "the gate again, wider: the man talks, ten lit; the neighbour's bead goes dark",
     still((-1.2, -5.3, 1.45), (-3.7, -3.5, 1.1), 30),
     {"gateman": P(GM, -90, "neutral", talks=[("L48", "L48.2")], arms=[40, 0]),
      "gatewoman": P(GW, yaw_to(GW, (-1.2, -5.3)), "neutral")})
shot("L49", "back to the wide: the Grin at her ear",
     still(*REV_CAM), REV_CAST, fill=[90, "#ffe2c4"])
shot("L49.2", "close on the Grin at her ear",
     still((MUMX - 0.5, -6.8, 2.5), (MUMX + 0.3, TWELFTH[1], 2.45), 44),
     {"mumr": P(MUMP, 180, "soft"), "grin": G(head=[62, 0], roll=38, tilt=-26)}, fill=GF)
shot("L50", "punch in on Mom's face, smiling up at it",
     front(MUMP, 180, 1.6, 2.6, 2.5, 38, 6),
     {"mumr": P(MUMP, 180, "smile"), "grin": G(head=[62, 0], roll=38, tilt=-26)}, fill=GF)
shot("L51-0.4", "punch in on me at the back, scared, ten lit",
     front(ME_BACK, 0, 1.7, 1.55, 1.5, 34, 20),
     {"me": P(ME_BACK, 0, "scared")})
shot("L51.2+0.4", "breakfast again: I talk over Mom as she starts a sentence",
     still((KX + 1.9, KY - 0.3, 1.5), (KX - 0.2, KY - 0.3, 1.35), 16),
     {"mum": PK(MK, 180, "neutral", talks=[("L51.2", "L51.2+0.5", 0.5)]),
      "me": PK(MEK, 0, "neutral", talks=[("L51.2", "L51>")], arms=[45, 45])})
shot("L52", "the gate again, wider: nb1 shuts her mouth while I talk",
     still((0.2, -7.6, 1.55), (2.8, -10.5, 1.4), 28),
     {"nb1": P(NB1, -90, "neutral", arms=[60, 0], talks=[("L52", "L52+0.5", 0.5)]),
      "me": P((1.6, -9.0), 90, "neutral", talks=[("L52", "L52>")], arms=[50, 50])})
shot("L52.2", "me starting up the aisle between the dark rows, worried",
     still((HX + 0.6, 7.6, 1.5), (HX - 0.2, 1.0, 1.4), 30),
     {"me": P((HX - 0.2, 3.0), 0, "worried", walks=[("L52>", (HX - 0.2, -1.0))]), **hall()})
shot("L53", "the eleven in the lamp light, round mouths, cords lit, Mom on the step among them",
     still((MUMX - 1.3, -5.0, 2.9), (MUMX + 1.0, TWELFTH[1], 2.1), 30),
     {**choir("L53", "L53>"), "mumr": P(MUMP, 180, "soft"), "grin": G(head=[62, 0], roll=38, tilt=-26)}, fill=GF)
shot("L53.2", "Mom's face, turned only toward the Grin",
     front(MUMP, 180, 1.6, 2.6, 2.5, 38, 6),
     {"mumr": P(MUMP, 180, "polite", tilt=12, head=[30, 0])})
shot("L54", "along the riser: eleven lit cords in a row, round mouths, one bare neck at the end",
     move(((HX + 1.6, -4.3, 2.3), (HX + 1.6, -8.6, 1.9)), ((HX - 0.6, -4.3, 2.3), (HX - 0.6, -8.6, 1.9)), 30),
     {**choir("L54", "L54>"), "grin": G(head=[0, 14])}, step=2)
FOOT = (MUMX, -3.7, 0.0)
shot("L55", "me at the foot of the riser below Mom, mouth open on a word; she doesn't look down",
     still((MUMX + 2.2, -2.2, 1.5), (MUMX, -4.8, 1.8), 30),
     {"me": P(FOOT, 180, "neutral", talks=[("L55", "L55.1", 0.55)]),
      "mumr": P((MUMX, -5.65, 0.3), 180, "soft", head=[0, 0]),
      **choir(skip=("c4",)), "grin": G(head=[40, 0], roll=14, tilt=-14, bend=18)}, fill=GF)
shot("L55.2", "close on Mom's dark cord",
     front((MUMX, -5.65, 0.3), 180, 1.4, 1.5, 1.4, 34, 10),
     {"mumr": P((MUMX, -5.65, 0.3), 180, "soft")})
shot("L56", "me at the foot of the riser, mouth closed, soft, looking up at her",
     front(FOOT, 180, 1.8, 1.6, 1.5, 34, 22),
     {"me": P(FOOT, 180, "soft", head=[0, -16])})
shot("L56.2", "Mom from below, not looking down",
     front((MUMX, -5.65, 0.3), 180, 1.9, 0.9, 1.7, 34, -12),
     {"mumr": P((MUMX, -5.65, 0.3), 180, "soft", head=[0, 0])})
shot("L57", "me singing 'ah', a round mouth",
     front(FOOT, 180, 1.7, 1.6, 1.5, 34, 12),
     {"me": P(FOOT, 180, "neutral", head=[0, -10], sings=[("L57.3", "L58>")])})
shot("L57.3", "close on my cord as I sing: all ten stay lit",
     front(FOOT, 180, 1.2, 1.25, 1.15, 36, 8),
     {"me": P(FOOT, 180, "neutral", head=[0, -10], sings=[("L57.3", "L58>")])})
shot("L58", "wide of the riser: Mom turned down to me, the Grin sat upright in its chair, facing front, head slightly down",
     move(((TW + 2.0, -3.4, 3.0), (TW + 0.2, TWELFTH[1], 1.9)), ((TW + 1.4, -3.9, 2.7), (TW + 0.2, TWELFTH[1], 1.9)), 22, 24),
     {**choir(skip=("c4",)), "mumr": P((MUMX, -5.65, 0.3), 180, "soft", head=[0, 12]),
      "grin": G(head=[0, 14]), "me": P(FOOT, 180, "neutral", sings=[("L58", "L58>")])}, fill=[90, "#ffe2c4"])
shot("L58.3", "behind the riser: eleven strokes scratched in a row, the stretch behind the twelfth chair bare",
     still((TW + 1.3, -11.05, 1.3), (TW + 1.3, -9.5, 1.25), 14),
     {**choir()}, step=4, hold=True)

# ---- 08 the next night, L59 to L63
shot("L59.1", "supper, warm: me at the table, mouth shut, soft; Mom talks across it",
     still((KX + 1.9, KY - 0.3, 1.5), (KX - 0.2, KY - 0.3, 1.35), 16),
     {"me": PK(MEK, 0, "soft"),
      "mum": PK(MK, 180, "smile", talks=[("L59.1", "L61")], arms=[30, 30], later=[("L59.3", dict(expr="laugh")), ("L59.4", dict(expr="smile"))])})
shot("L59.4", "close on my cord: one bead fades, then a second, the first ever",
     front(MEK, 0, 1.35, 1.2, 1.15, 34),
     {"me": PK(MEK, 0, "soft")})
shot("L60", "me, a little surprised, my cord half dark",
     c([0, *front(MEK, 0, 2.0, 1.5, 1.4, 34, 15)[0][1:]], [1, *front(MEK, 0, 1.6, 1.5, 1.4, 36, 15)[0][1:]]),
     {"me": PK(MEK, 0, "smile")})
shot("L61", "close on my cord, the tenth bead fading, the same framing as the first shot",
     front(MEK, 0, 1.55, 1.18, 1.27, 32, 0),
     {"me": PK(MEK, 0, "smile")}, hand=0.004)
shot("L62", "through the kitchen window: far up the hill, the hall's window lit amber in the dark",
     still((KX, KY + 1.2, 1.5), (KX + 2.0, 29.0, 2.5), 30),
     {})
shot("L62.3", "me turning toward the window, scared, my cord all dark",
     still((KX - 0.2, KY - 0.8, 1.45), (KX - 0.2, KY + 0.62, 1.4), 30),
     {"me": PK(MEK, 180, "scared")})
shot("L63", "two shot: Mom asleep upright at the table across from me, unhurt, her cord dark",
     still((KX + 1.9, KY - 0.3, 1.5), (KX - 0.2, KY - 0.3, 1.35), 16),
     {"me": PK(MEK, 180, "scared"),
      "mum": PK(MK, 180, "asleep", sit=True, head=[0, 10])})

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
            for a, b, *m in p["talks"]:
                talk(who, a, b, *m)
            for a, b in p["sings"]:
                if a:
                    sing(who, a, b)
        else:
            hide(who, at)

SHID = {s["at"] if i else 0: f"S{i + 1:02d}" for i, s in enumerate(SH)}

# ------------------------------------------------------------------------------------------------ cues
cues = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


def tod(at, name, **kw):
    cue(at, "tod", set=name, **kw)


LIGHTS = ["hall_house", "riser", "hall_low", "back_wash", "kitchen_day", "kitchen_lamp", "bed_lamp", "landing", "mum_key",
          "grin_key", "grin_rim", "front_key"]
PRESETS = {
    "street": {},
    "kday": {"kitchen_day": 0.5, "kitchen_lamp": 0.12},
    "knight": {"kitchen_lamp": 0.9, "mum_key": 0.0},
    "kdark": {"kitchen_lamp": 0.35},
    "bed": {"bed_lamp": 1.0, "landing": 0.5, "mum_key": 0.3},
    "hallwin": {"hall_house": 0.34, "riser": 0.9, "hall_low": 0.12},
    "thu": {"riser": 0.9, "hall_low": 0.18, "front_key": 1.0},
    "concert": {"hall_house": 1.0, "riser": 0.6},
    "lamp": {"hall_house": 0.0, "riser": 1.0, "grin_key": 1.0, "grin_rim": 1.0},
}
_cur = {k: 0.0 for k in LIGHTS}


def room(at, name, dur=0.3, lead=0.3):
    """Ramp every light to a preset, ending on the cut at `at` (so no light snaps in view)."""
    want = {k: 0.0 for k in LIGHTS}
    want.update(PRESETS[name])
    for k in LIGHTS:
        if abs(want[k] - _cur[k]) > 1e-6:
            cue(shift(at, -lead), "lt", l=k, v=want[k], dur=dur)
            _cur[k] = want[k]


def lt(at, light, v, dur=0.4):
    cue(at, "lt", l=light, v=v, dur=dur)
    _cur[light] = v


def beads(at, who, idx, step=0.0, dur=0.4, on=False):
    cue(at, "bead_on" if on else "bead_off", who=who, idx=list(idx), step=step, dur=dur)


def bset(at, who, ndark):
    """Set a cord at once (on a cut): the last `ndark` beads dark, the rest lit."""
    dark = list(range(10 - ndark, 10))
    lit = list(range(0, 10 - ndark))
    if dark:
        beads(at, who, dark, 0.0, 0.0)
    if lit:
        beads(at, who, lit, 0.0, 0.0, on=True)


# time of day, with the rooms' lights ramped on the cut
tod(0, "morning")
room(0.0, "kday", dur=0.0, lead=0.0)
room("L02", "street")
tod("L11", "night")
room("L11", "hallwin")
tod("L13", "morning")
room("L13", "street")
tod("L19", "inside")
room("L19", "concert")
tod("L20", "morning")
room("L20", "kday")
tod("L24", "night")
room("L24", "knight")
room("L25", "bed")
tod("L25.3", "morning")
room("L25.3", "kday")
tod("L26", "night")
room("L26", "hallwin")
room("L27.1", "hallwin")
tod("L28", "night")
room("L28", "kdark")
room("P01", "thu")
tod("L33", "night")
room("L33", "street")
tod("L35", "inside")
room("L35", "concert")
lt("L38", "hall_house", 0.1, 2.5)                       # the concert lights go down in one slow ramp
lt("L38", "riser", 1.0, 2.5)
lt("L39", "grin_key", 1.0, 3.0)
lt("L39", "grin_rim", 1.0, 3.0)
cue("L51.2", "tod", set="morning")
room("L51.2", "kday")
tod("L52", "morning")
room("L52", "street")
tod("L52.2", "inside")
room("L52.2", "lamp")
lt("L58.3-0.3", "back_wash", 1.0, 0.3)
tod("L59.1", "night")
room("L59.1", "knight")
tod("L62", "night")
room("L62", "kdark")
room("L62.3", "knight")
# props: the audience rows, bunting, the audience
cue(0, "rows", on=False)
cue("L28", "rows", on=True)
cue("L35", "audience", on=True)
cue("L35", "bunting", on=True)
cue("L35", "rows", on=True)
cue("L52", "audience", on=False)
cue("L52", "bunting", on=False)
cue("L52.2", "audience", on=True)
cue("L52.2", "bunting", on=True)
cue("L59.1", "audience", on=False)
cue("L59.1", "bunting", on=False)
cue("L59.1", "rows", on=False)
cue(0, "scarf", who=["mum", "mumr"])
cue(0, "props", scarf=False, robe=False)
cue(0, "stand", pos=[HX + 1.2, -3.5, 0.0])
cue("L43", "stand", pos=[MUMX + 0.7, TWELFTH[1] + 0.9, 0.9])
cue("L44.5+0.2", "stand", pos=[HX + 1.2, -3.5, 0.0])
cue(0, "farwin", on=False)
cue("L62", "farwin", on=True)
cue("L62.3", "farwin", on=False)

# beads: indices count from 0, the last dark first
# the hook: Mom's nine dark at breakfast, the tenth fades on DARK
bset(0, "mum", 9)
beads("L01.4", "mum", [0])
beads("L06", "mum", list(range(10)), 0.0, 0.0, on=True)                      # Monday morning at her door
bset("L02", "gatewoman", 0)
beads("L03.2+0.1", "gatewoman", [9])
bset("L04", "gatewoman", 10)
bset("L07", "postman", 0)
beads("L07.1", "postman", list(range(9, 0, -1)), step=0.12)
beads("L07.3+0.1", "postman", [0])
bset("L07", "gateman", 9)
bset("L07", "gatewoman", 10)
bset("L07", "nb1", 9)
bset("L07", "nb2", 10)
bset("L13", "nb1", 0)
bset("L13", "nb2", 0)
beads("L13.2+0.2", "nb1", [9, 8, 7], step=0.3)
beads("L13.2+0.5", "nb2", [9, 8, 7, 6], step=0.3)
bset("L15", "nb1", 0)
beads("L15+0.6", "nb1", [9, 8, 7, 6, 5, 4], step=0.25)
bset("L16", "gateman", 10)
bset("L16", "gatewoman", 10)
bset("L20", "mum", 0)
beads("L23", "mum", list(range(9, -1, -1)), step=0.12)
bset("L24", "mum", 10)
bset("L48", "gateman", 0)
bset("L48", "gatewoman", 0)
beads("L48.1+0.1", "gatewoman", [9])
bset("L51.2", "mum", 0)
beads("L51.2+0.5", "mum", [9, 8, 7, 6, 5], step=0.3)
bset("L52", "nb1", 0)
beads("L52+0.4", "nb1", [9, 8, 7, 6, 5, 4], step=0.25)
bset("L59.1", "mum", 0)
beads("L59.5+0.2", "me", [9, 8], step=0.55)
beads("L60", "me", [7, 6, 5], step=0.4)
beads("L60+0.55", "me", [4, 3, 2, 1], step=0.3)
beads("L61+0.2", "me", [0])
bset("L52.2", "mum", 10)
bset("L63", "mum", 10)

sfx = [
    {"at": "L01.4+0.1", "kind": "click", "db": -18},
    {"at": "L41", "kind": "sting", "db": -13},
    {"at": "P02+0.1", "kind": "hit", "db": -10},
    {"at": "L61+0.35", "kind": "click", "db": -20},
]

story = {
    "slug": "ep46-choir-hall",
    "title": "After Your Tenth Bead, It ISN'T Them",
    "made_for_kids": False,
    "premise": "In a hillside village everyone hears only ten words a day, counted on ten glass beads round the neck. After the tenth, only the voice you love most still gets through. I talk all day and mine never go dark, and this week my mom keeps thanking me for long talks in her kitchen that I was never at.",
    "twist": "The beads count the words that reach you, not the words you say. I never go dark because I talk over everyone, and once someone's ten are spent the only voice left to them is the grinning twelfth singer's, wearing the voice of whoever they love. The night I let Mom finish, my own ten go dark, and later Mom's voice calls me from the hall while Mom is asleep in her chair.",
    "world": "a hillside village in early winter: render cottages with painted gates and frosted hedges, a narrow house with a round-table kitchen, and a plain wooden village hall with a riser of twelve chairs under one enamel lamp",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff7f9e",
    "gap": 0.12,
    "tail": 0,
    "rev": 20,
    "look": {"fog": "#c8d4de", "fog_density": 0.01, "fog_start": 6.0, "sky": "#b6cde0", "sky_strength": 1.0,
             "exposure": 0.0, "flash_safe": True,
             "polish": {"reveal": ["L41", "L48", "L63"], "twist": "L62",
                        "quiet": [["L58", "L60"]], "hold": ["S01"],
                        "sway": []}},
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
                  {"at": "P01>", "voices": ["drone", "pad", "choir"], "energy": 0.42},
                  {"at": "L35", "voices": ["drone", "choir", "pad"], "energy": 0.5},
                  {"at": "L47", "voices": ["drone", "choir", "pad", "piano"], "energy": 0.55},
                  {"at": "L58", "voices": ["drone", "pad", "piano", "bubble"], "energy": 0.45, "mode": "major", "root": 57},
                  {"at": "L62", "voices": ["drone"], "energy": 0.4, "mode": "minor", "root": 57},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "L11", "lufs": -40},
                  {"kind": "room", "from": "L19", "to": "L28", "lufs": -42},
                  {"kind": "wind", "from": "P01", "to": "L35", "lufs": -34},
                  {"kind": "room", "from": "L35", "to": "L39", "lufs": -40},
                  {"kind": "wind", "from": "L62", "to": "end", "lufs": -38},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "P01>", "keep": []},
                              {"from": "P02", "to": "P02>", "keep": ["hit"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
