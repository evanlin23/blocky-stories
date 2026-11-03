"""Writes ../story.json for ep32 "sitter" (script.md, redo 2026-11-02).

Run from anywhere: python stories/ep32-sitter/generator/make_story.py
The words are in lines.json next to this file (made from the script by script_to_lines.py). Everything else is here:
the cast, the geometry of the life room, the shots and their cameras, the acting, the cues set.py reads, the effects,
the score and the sound. Places are set.py's (metres, floor z = 0). A character with yaw 0 faces -y; yaw 90 faces +x.

The life room is centred on the dais at the origin. Easel i stands at angle TH[i] on a curve of radius RE, its canvas
facing out; its painter stands at radius RP behind it, facing the dais. The two wider gaps (between easels 4 and 5, 6
and 7) are where faded Mum sits in weeks 2 and 3. The little daylight sets are separate places in the same scene:
the bus stop (x 80), the cafe (x 120), the bakery (x 160), my flat (x -40), Mum's hall (x 40) and the reveal pair (x 200).

Acting keys read by set.py (acting.py ignores them): "sit": true seats a character on whatever is under them;
"fade": 0..1 how far the body has faded to raw pine, "fade_h": 0..1 the face (it leads the body on a restore),
"stage": 0..2 the pencil lines on a faded face, "bendto": [x, y, deg] leans the torso from the waist toward x, y.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# ---------------------------------------------------------------------------------------------------- holds
HOLDS = {"L22": 0.75, "L30": 0.85, "L31": 0.6}          # id -> seconds after the line (the music drops live in these)
LOOP = 0.13          # with the 0.12 s gap, 0.25 s after the last word
for ln in lines:
    if ln["id"] in HOLDS:
        ln["gap"] = HOLDS[ln["id"]]
lines = lines + [{"id": "PEND", "pause": LOOP, "chunks": []}]

TEMPO = {"L22": 0.95, "L31": 0.95}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]


# ---------------------------------------------------------------------------------------------------- cast
def person(skin, shirt, pants, hair, hair_c, pattern="solid", extras=(), hat="none", hat_c=None, collar=None, eyes="round",
           sleeves="long", shoes="#2a2a2e", extra_c=None, bags=False, brows=True, ink="#161012", height=1.0, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "width": 0.8, "height": height,
         "face": {"eyes": eyes, "brows": brows, "ink": ink, **({"bags": True} if bags else {})}}
    if extras:
        d["extras"] = list(extras)
    if hat_c:
        d["hat_c"] = hat_c
    if collar:
        d["collar"] = collar
    if extra_c:
        d["extra_c"] = extra_c
    d.update(kw)
    return d


mum = person("#e8c4a2", "#2f7f82", "#39393f", "cap", "#c4c8cc", pattern="plaid", pattern_c="#256a6c",
             collar="#efe6d4", extras=["glasses"], extra_c="#6b4a2e", height=0.96)
mum["face"].update({"pupil": "#6a3d1f", "corners": True})

cast = {
    "me": person("#e3b48e", "#d3a022", "#33363c", "buzz", "#14120f", pattern="knit", pattern_c="#bd8d19", shoes="#e8e8e6"),
    "mum": mum,
    "kofi": person("#d9a67e", "#b4522f", "#3a3a40", "none", "#1a1410", extras=["glasses", "apron"], extra_c="#4a6788",
                   glasses_c="#14100e", collar="#9b4326"),
    "petra": person("#f0cfae", "#f2f2f0", "#2d3b5c", "bun", "#b4622e", pattern="stripes", pattern_c="#26365c"),
    "ade": person("#d9a67e", "#78803c", "#4a4033", "none", "#8a8a88", hat="ballcap", hat_c="#6b4a2e", pattern="plaid",
                  pattern_c="#5a6230", eyes="tired", height=0.98),
    "bg1": person("#b97d54", "#6e3b63", "#2e3138", "cap", "#1d1612", pattern="knit", pattern_c="#5a2f52"),
    "bg2": person("#f2d2b4", "#4d5a6b", "#3a3530", "long", "#6b4a32", pattern="solid"),
    "bg3": person("#8e5a3e", "#9aa3ad", "#242830", "cap", "#0f0d0c", pattern="stripes", pattern_c="#6b7580"),
    "bg4": person("#e3b48e", "#8b4f59", "#2f3640", "bun", "#2a2018", pattern="knit", pattern_c="#6e3b45"),
    "bg5": person("#d9a67e", "#56706a", "#33302c", "cap", "#6e6a64", pattern="plaid", pattern_c="#3f524e"),
    "bg6": person("#c68a5e", "#a8643a", "#3a3a40", "buzz", "#2a2220", pattern="solid"),
    # the montage
    "bus": person("#e3b48e", "#3a63a8", "#6d6a5a", "none", "#2a2018", hat="ballcap", hat_c="#c2362f", pattern="solid"),
    "walk1": person("#8e5a3e", "#d88a2c", "#2c3a52", "long", "#14100e", pattern="stripes", pattern_c="#a8661c"),
    "walk2": person("#f2d2b4", "#5b8a5b", "#3c3a40", "cap", "#7a5a3a", pattern="plaid", pattern_c="#3f6a3f"),
    "cpA": person("#d9a67e", "#c25a6a", "#3a3a40", "bun", "#4a3220", pattern="knit", pattern_c="#9a3e50"),
    "cpB": person("#b97d54", "#4a6fa5", "#3a3530", "cap", "#1d1612", pattern="solid"),
    "baker": person("#f0cfae", "#f4f0e6", "#4a4a52", "none", "#1a1410", extras=["apron"], extra_c="#f4f0e6", hat="beanie",
                    hat_c="#f4f0e6", sleeves="short"),
    "cust": person("#c68a5e", "#7a4fa0", "#33363c", "swoop", "#2a1d15", pattern="solid", eyes="dot"),
    "sit2": person("#d6b98a", "#d6b98a", "#d6b98a", "buzz", "#d6b98a", sleeves="long", shoes="#d6b98a"),
}
PAINTERS = {1: "bg6", 2: "bg1", 3: "bg2", 4: "bg3", 5: "bg4", 6: "bg5", 7: "petra", 8: "me"}
FADERS = {"mum": "mum", "ade": "plain", "bus": "plain", "sit2": "plain2"}      # who can fade, and which pencil face they wear

# ---------------------------------------------------------------------------------------------------- geometry
RE, RP = 3.1, 3.7
STEP = [20.4, 20.4, 20.4, 32.0, 20.4, 32.0, 20.4]
TH = [187.0]
for s_ in STEP:
    TH.append(TH[-1] + s_)               # TH[0] is easel 1, TH[7] easel 8


def pol(r, deg):
    return (round(r * math.cos(math.radians(deg)), 3), round(r * math.sin(math.radians(deg)), 3))


def E(i):
    return pol(RE, TH[i - 1])


def PP(i):
    return pol(RP, TH[i - 1])


def yaw_to(a, b):
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


def wrap(a):
    return (a + 180.0) % 360.0 - 180.0


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens, roll=0):
    return c([0, loc, tgt, lens, roll]) if roll else c([0, loc, tgt, lens])


def move(a, b, lens_a, lens_b=None):
    return c([0, a[0], a[1], lens_a], [1, b[0], b[1], lens_b or lens_a])


def z3(p, z):
    return [p[0], p[1], z]


def mid(a, b, z):
    return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, z]


def front(p, yaw, dist, z):
    """A point dist metres in front of a character at p facing yaw."""
    r = math.radians(yaw)
    return [round(p[0] + dist * math.sin(r), 3), round(p[1] - dist * math.cos(r), 3), z]


def canvas_cam(i, dist, z=1.3, lens=30, push=0.0, side=0.0, cs=0.0):
    e = E(i)
    n = (math.cos(math.radians(TH[i - 1])), math.sin(math.radians(TH[i - 1])))
    t = (-n[1], n[0])
    tgt = [e[0] + t[0] * side, e[1] + t[1] * side, z]
    a = [tgt[0] + n[0] * dist + t[0] * cs, tgt[1] + n[1] * dist + t[1] * cs, z]
    b = [tgt[0] + n[0] * (dist - push) + t[0] * cs, tgt[1] + n[1] * (dist - push) + t[1] * cs, z]
    return c([0, a, tgt, lens], [1, b, tgt, lens]) if push else still(a, tgt, lens)


DAIS = (0.0, 0.0)
ME, PETRA = PP(8), PP(7)
# faded Mum's places: week 1 on the dais stool, week 2 in the gap between easels 4 and 5, week 3 in the gap between 6 and 7
# (beside Petra), week 4 and on beside my easel
U1 = (0.0, 0.0)
U3 = pol(RP, (TH[3] + TH[4]) / 2)
U4 = pol(RP, (TH[5] + TH[6]) / 2)
_n8 = (math.cos(math.radians(TH[7])), math.sin(math.radians(TH[7])))
_t8 = (-_n8[1], _n8[0])
C8 = E(8)
U5 = (round(C8[0] + _n8[0] * 0.55 + _t8[0] * 0.85, 3), round(C8[1] + _n8[1] * 0.55 + _t8[1] * 0.85, 3))
P5 = (C8[0] + _n8[0] * 0.2, C8[1] + _n8[1] * 0.2)       # the face of my canvas
N8, T8 = _n8, _t8
Y1, Y3, Y4, Y5 = (yaw_to(U1, ME), yaw_to(U3, DAIS), yaw_to(U4, DAIS), yaw_to(U5, P5))
# the seat heights: root z for a seated rig character (set.py's figure) and the head's height
Z_DAIS, Z_SPARE = 0.13, -0.08
HD, HS = 1.69, 1.47


def head_of(U, z):
    return [U[0], U[1], z]


# the little sets
HX = 40.0
BUS = (80.0, 0.2)
CAF = (120.0, 1.5)
BAK = (160.9, -0.15)
FLAT = (-40.0, 0.0)
FLAT_EASEL = (-40.25, 0.7)
ME_FLAT = (-39.45, 0.45)
PAIR = (200.0, 0.0)

_mm = ((ME[0] + U5[0]) / 2, (ME[1] + U5[1]) / 2)


def PAIRMID(z):
    return [_mm[0], _mm[1], z]


def PAIRCAM(d, z):
    """A camera d metres inside the circle from the midpoint between me and the sitter, looking out at both faces."""
    return [round(_mm[0] - N8[0] * d, 3), round(_mm[1] - N8[1] * d, 3), z]


M36 = (U5[0] + 0.3 * N8[0], U5[1] + 0.3 * N8[1])


def fa36(dist, ang, z):
    dx, dy = P5[0] - M36[0], P5[1] - M36[1]
    n_ = math.hypot(dx, dy)
    dx, dy = dx / n_, dy / n_
    best = None
    for sg in (1, -1):
        a = math.radians(ang * sg)
        v = (dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a))
        if best is None or v[0] * N8[0] + v[1] * N8[1] > best[0] * N8[0] + best[1] * N8[1]:
            best = v
    return [round(M36[0] + best[0] * dist, 3), round(M36[1] + best[1] * dist, 3), z]


# ---------------------------------------------------------------------------------------------------- shots
SH = []


def shot(sid, at, what, cam, **flags):
    SH.append((sid, at, what, cam, flags))


# 01 the rule
shot("S01", 0, "the bus-stop man, half his face faded to pine, in the sun", still([80.1, -1.8, 1.56], [80.0, 0.2, 1.52], 40), fill=[80.9, -1.6, 2.2])
shot("S01b", "L01.3", "push in on the fade line across his cheek",
     c([0, [80.2, -1.5, 1.57], [80.0, 0.2, 1.56], 42], [1, [80.1, -1.15, 1.58], [79.97, 0.2, 1.57], 50]), fill=[80.9, -1.0, 2.2])
shot("S02", "L02", "his faded half: grain, a pencil oval", still([80.3, -1.0, 1.58], [80.0, 0.2, 1.57], 38), fill=[80.9, -0.5, 2.2])
shot("S02b", "L02.3", "two passers-by do not look", still([81.6, -5.8, 1.5], [79.9, 0.5, 1.4], 26))
shot("S03", "L03", "the cafe window table: a couple staring, toast going cold", still([120.0, -1.2, 1.5], [120.0, 1.5, 1.38], 17))
shot("S03b", "L03.2", "closer on their stare", still([120.0, -0.3, 1.42], [120.0, 1.5, 1.38], 25))
shot("S04", "L04", "the baker stares at the customer", still([160.35, -1.3, 1.62], [160.9, 1.7, 1.5], 26))
shot("S04b", "L04.2", "the customer's uneasy face", still([162.0, 0.95, 1.6], [160.9, -0.15, 1.55], 30), fill=[162.0, 0.6, 2.3])
shot("S05", "L05", "the life room, warm: Mr Dobbs on the dais, his cheek warming", still([3.0, -2.7, 1.55], [0.0, 0.0, 1.3], 28))
shot("S05b", "L05.4", "over a painter's shoulder, his face on the canvas", canvas_cam(3, 1.9, 1.35, 30, side=-0.5), hide_cast=["bg2"])
# 02 Mum
shot("S06", "L06", "my flat: Mum's portrait with only guide lines for a face, and me", still([-39.9, -2.1, 1.45], [-39.9, 0.7, 1.4], 17), ev=-1.3)
shot("S06b", "L06.3", "the guide lines, corner lines clear", still([-40.25, -0.55, 1.4], [-40.25, 0.7, 1.4], 24), ev=-1.3)
shot("S07", "L07", "my phone face down on the shelf", still([-39.35, -0.55, 1.3], [-38.3, 0.15, 1.03], 40), ev=-0.9)
shot("S07b", "L07.2", "Mum's hall, bare hooks and pale squares", still([HX + 1.15, 1.7, 1.45], [HX - 1.0, 1.0, 1.4], 17))
shot("S08", "L08", "me, turning away from the portrait", still([-40.0, -0.7, 1.55], [-39.5, 0.45, 1.55], 22), ev=-1.5)
# 03 week one
shot("S09", "L09", "the arts centre on its hill in rain", still([-15.0, -17.0, 9.0], [-1.0, -2.0, 1.6], 22), rain=True)
shot("S09b", "L09.1", "me on the rain-dark steps with a canvas", still([-8.7, -4.5, 1.55], [-6.2, -3.0, 1.1], 26), rain=True)
shot("S10", "L10", "the fruit bowl on the side table", still([-2.6, -4.2, 1.45], [-5.05, -2.0, 1.0], 27))
shot("S10b", "L10.3", "Kofi, friendly", still(front((-1.0, -0.4), 40, 1.9, 1.6), [-1.0, -0.4, 1.5], 36), ev=0.1)
_o = pol(4.25, TH[7] + 4)
shot("S11", "L11", "over my shoulder: the faded sitter on the dais stool, cushion flat",
     still([_o[0], _o[1], 1.72], [0.0, 0.0, 1.45], 36))
_g = pol(3.55, (TH[5] + TH[6]) / 2)
shot("S12", "L12", "low wide past two easels: bare pine from hair to shoes", still([_g[0], _g[1], 0.85], [0.0, 0.0, 0.95], 26),
     hide_cast=["bg5", "petra"])
shot("S13", "L13", "its face: the cross, two empty ovals, the corner lines", still(front(U1, Y1, 1.35, HD), z3(U1, HD), 27), hand=0.0)
shot("S14", "L14", "from behind the dais: every painter's head down", still([-1.7, 3.0, 2.0], [0.4, -3.4, 1.2], 22))
shot("S14b", "L14.1", "Petra's canvas: a pencil bowl of fruit", canvas_cam(7, 1.3, 1.3, 30), hide_cast=["petra"])
shot("S15", "L15", "me at easel 8, side on", still([4.6, 1.2, 1.55], [3.5, -0.5, 1.4], 30))
shot("S15b", "L15.4", "my canvas: a nose line stopped short", canvas_cam(8, 1.2, 1.25, 34), hide_cast=["me"])
shot("S16", "L16", "my face, jaw tight", still(front(ME, yaw_to(ME, DAIS) - 50, 1.4, 1.58), z3(ME, 1.55), 38))
# 04 weeks two and three
shot("S17", "L17", "its face, a short nose line", still(front(U1, Y1, 1.35, HD), z3(U1, HD), 27), hand=0.0)
shot("S17b", "L17.3", "my canvas, the same line, the same length", canvas_cam(8, 1.2, 1.25, 34), hide_cast=["me"])
shot("S18", "L18", "the empty dais stool, pan to it on a spare stool between easels 4 and 5",
     c([0, [2.9, 1.6, 1.5], [0, 0, 0.62], 24], [1, [2.9, 1.6, 1.5], [U3[0], U3[1], 1.3], 24]), )
shot("S19", "L19", "my canvas: half a mouth", canvas_cam(8, 1.2, 1.2, 34), hide_cast=["me"])
shot("S19b", "L19.3", "it beside Petra, half a mouth, its knee by her palette",
     still([1.3, -0.5, 1.75], [mid(U4, PETRA, 1.2)[0], mid(U4, PETRA, 1.2)[1], 1.3], 26), hide_easels=[7])
shot("S20", "L20", "Petra's canvas: a green pear", canvas_cam(7, 1.3, 1.3, 30), hide_cast=["petra"])
_m4 = (ME[0] + (U4[0] - ME[0]) * 0.28, ME[1] + (U4[1] - ME[1]) * 0.28)
shot("S21", "L21", "its head turned to my easel, empty eyes", still([_m4[0], _m4[1], 1.5], z3(U4, HS), 28), hide_cast=["me", "petra"], hide_easels=[7])
# 05 the scare
shot("S22", "L22", "wide of the room: the lamps sag", still([-4.6, -4.2, 1.9], [0.8, 0.3, 1.3], 20))
shot("S23", "L23", "lamps up: it on a spare stool at my elbow", still(PAIRCAM(2.4, 1.55), PAIRMID(1.5), 21), hide_easels=[7, 8], hide_cast=["petra"])
shot("S24", "L24", "3/4, lit from below: its face leaning toward mine",
     still(PAIRCAM(2.4, 1.55), PAIRMID(1.5), 18), hand=0.003, hide_easels=[7, 8], hide_cast=["petra"])
shot("S25", "L25", "my coat on the peg, the door swinging", still([-3.0, -4.1, 1.5], [-5.5, -3.0, 1.2], 26))
# 06 the car park
PETRA_C, ME_C = (-2.5, -8.9), (-1.2, -8.5)
shot("S26", "L26", "car park, rain, Petra jogging over with my coat", still([-6.5, -12.5, 1.0], [-2.3, -9.0, 0.9], 26), rain=True)
shot("S26b", "L26.4", "two-shot under the lamp", still([-1.9, -12.0, 0.8], [-1.8, -8.9, 0.95], 36), rain=True)
shot("S27", "L27", "Petra amused", still(front(PETRA_C, yaw_to(PETRA_C, ME_C) - 60, 1.3, 1.15), z3(PETRA_C, 1.05), 40), rain=True)
shot("S27b", "L27.1", "me, the words landing", still(front(ME_C, yaw_to(ME_C, PETRA_C) + 60, 1.3, 1.15), z3(ME_C, 1.05), 40), rain=True)
shot("S28", "L28", "through the rain-streaked window, every canvas", still([0.2, -9.5, 1.9], [0.0, -2.0, 1.3], 24), rain=True)
shot("S28b", "L28.2", "push in: seven bowls of fruit, then mine with the half face, it beside it, small",
     c([0, [0.5, -9.0, 1.7], [0.5, -2.0, 1.3], 28], [1, [1.9, -7.4, 1.5], [3.3, -0.2, 1.1], 40]), rain=True, turn8=True)
shot("S29", "L29", "the picture: Mum's home portrait beside my class canvas, line for line",
     still([PAIR[0], -1.55, 1.42], [PAIR[0], 0.9, 1.42], 15), hand=0.0, hide_unp=True)
shot("S30", "L30", "through the wet glass, its pencil face turns toward me", still([0.5, -8.0, 1.55], [U5[0], U5[1], HS + 0.05], 80), rain=True)
shot("S31", "L31", "close through the glass on its face", still([0.5, -8.0, 1.52], [U5[0], U5[1], HS + 0.02], 150), rain=True, hand=0.002)
# 07 the face
shot("S32", "L32", "me walking in wet; the room bright and warm", still([-3.4, -3.6, 1.65], [2.6, -0.4, 1.35], 22))
shot("S32b", "L32.3", "me painting, side on, steady", still([4.6, -2.3, 1.55], [3.7, -0.7, 1.4], 30), fill=[4.3, -1.3, 2.2])
shot("S33", "L33", "my canvas: Mum's eyes", canvas_cam(8, 1.0, 1.3, 34), hide_cast=["me"])
_dl = math.hypot(P5[0] - U5[0], P5[1] - U5[1])
DU = ((P5[0] - U5[0]) / _dl, (P5[1] - U5[1]) / _dl)


def fa(dist, ang, z):
    """A camera dist metres ahead of its face, swung ang degrees toward the outward side (3/4 view)."""
    best = None
    for sg in (1, -1):
        a = math.radians(ang * sg)
        v = (DU[0] * math.cos(a) - DU[1] * math.sin(a), DU[0] * math.sin(a) + DU[1] * math.cos(a))
        if best is None or v[0] * N8[0] + v[1] * N8[1] > best[0] * N8[0] + best[1] * N8[1]:
            best = v
    return [round(U5[0] + best[0] * dist, 3), round(U5[1] + best[1] * dist, 3), z]


shot("S33b", "L33.2", "its face: the brown coming into the ovals", still(fa(1.5, 25, HS + 0.06), z3(U5, HS), 30), hide_cast=["me"], hand=0.002)
shot("S34", "L34", "the restore: colour climbs her; Mum at my elbow, looking at the canvas",
     c([0, fa(2.4, 35, HS + 0.12), z3(U5, HS - 0.08), 26], [1, fa(1.9, 32, HS + 0.1), z3(U5, HS - 0.04), 28]), hide_cast=["me"], hand=0.002)
shot("S35", "L35", "Petra, staring at Mum, mouth open", still(front(PP(7), yaw_to(PP(7), U5) + 15, 1.3, 1.6), z3(PP(7), 1.55), 24))
shot("S35b", "L35.2", "the brush on the boards", still([PP(7)[0] - 0.6, PP(7)[1] + 0.2, 0.85], [PP(7)[0] + 0.05, PP(7)[1] - 0.25, 0.05], 34), ev=-1.0, hide_easels=[7], hide_cast=["petra"], fill=[PP(7)[0] - 0.3, PP(7)[1] - 0.5, 1.5])
shot("S36", "L36", "Mum's face, glasses, eyes shining, a small smile", still(fa36(1.3, 18, 1.6), z3(M36, 1.6), 30), hide_cast=["me"], hide_easels=[8], hand=0.002)
# 08 the hall, and the sting
shot("S37", "L37", "Mum's hall, bright morning: the portrait alone among the pale squares, Mum and me in front of it",
     still([HX + 1.15, 1.2, 1.5], [HX - 0.8, 1.2, 1.4], 8), ev=0.5)
shot("S38", "L38", "the life room, colder: Kofi plumping the green cushion", still(front((0.3, -1.45), 160, 1.7, 1.6), [0.3, -1.45, 1.5], 32), ev=-1.3, fill=[0.6, -1.0, 1.9])
shot("S39", "L39", "low on the dais: nine graphite strokes, rising to the new sitter",
     c([0, [0.3, -2.35, 0.3], [0.0, -1.0, 0.12], 16], [1, [0.3, -2.35, 0.34], [0.0, 0.0, 0.95], 24]), tally=True, hand=0.002)
shot("S40", "L40", "slow push on its blank pencil face, the ovals the palest thing",
     c([0, front(U1, 0, 2.6, HD), z3(U1, HD), 30], [1, front(U1, 0, 1.6, HD), z3(U1, HD), 30]), hand=0.0)

shots = []
for i, (sid, at, what, cam, fl) in enumerate(SH):
    s = {"id": sid, "cam": cam, "hand": fl.get("hand", 0.006), "step": 2, "what": what}
    s.update({k: v for k, v in fl.items() if k in ("noceil", "hide_easels", "hide_cast", "fill", "ev", "hide_unp", "turn8", "tally")})
    if i:
        s["at"] = at
    shots.append(s)
rain_shots = [s[0] for s in SH if s[4].get("rain")]

# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True}
acting = {k: [] for k in cast}


def put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": list(pos), "blend": 0, "hidden": False, **NEUTRAL, "expr": "neutral", **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": list(pos), **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


PAINT = {"arms": [10, 62], "side": [0, 0], "head": [0, 8]}
for who in acting:
    hide(who, 0)

# the painters: at their easels from the life-room opening on (Mr Dobbs is the sitter there, so easel 1 has bg6), gone
# for the car park, back for my last night
for i, who in PAINTERS.items():
    if who == "me":
        continue
    p = PP(i)
    put(who, "L05", p, yaw=yaw_to(p, DAIS), **PAINT)
    hide(who, "L06")
    put(who, "L09", p, yaw=yaw_to(p, DAIS), **PAINT)
    if who == "petra":
        key(who, "L20", expr="smirk", blend=0.4)
        key(who, "L21", expr="neutral", blend=0.4)
        put(who, "L26", PETRA_C + (-0.45,), yaw=yaw_to(PETRA_C, ME_C), expr="smirk")
        key(who, "L27.1", expr="neutral", blend=0.3)
        hide(who, "L28")
        put(who, "L32", p, yaw=yaw_to(p, DAIS), **PAINT)
        key(who, "L35", expr="wide", blend=0.3, arms=[0, 0], head=[0, 0])
        key(who, "L36", expr="wide", blend=0.3)
        key(who, "L37", hidden=True, blend=0)
    else:
        hide(who, "L26")
        put(who, "L32", p, yaw=yaw_to(p, DAIS), **PAINT)
        hide(who, "L37")
# the two I see only on the last frames of the class are already hidden by then

# me
put("me", "L06", ME_FLAT, yaw=-90, expr="worried", arms=[8, 30], head=[0, 5])
key("me", "L08", yaw=90, head=[0, 4], expr="worried", blend=0.5)
hide("me", "L09")
put("me", "L09.1", (-5.9, -3.0), yaw=90, expr="worried", arms=[0, 0])
hide("me", "L10")
put("me", "L10", ME, yaw=yaw_to(ME, DAIS), expr="worried", **PAINT)
key("me", "L11", expr="worried", blend=0.3)
key("me", "L12", expr="scared", blend=0.3)
key("me", "L15", expr="neutral", blend=0.3)
key("me", "L16", expr="angry", blend=0.3)
key("me", "L17", expr="wide", blend=0.2)
key("me", "L19", expr="worried", blend=0.4)
key("me", "L21", expr="scared", blend=0.4)
key("me", "L23", expr="terrified", blend=0.2)
key("me", "L24", expr="terrified", head=[34, 4], blend=0.2)
hide("me", "L25")
put("me", "L26", ME_C + (-0.45,), yaw=yaw_to(ME_C, PETRA_C), expr="scared")
key("me", "L27.1", expr="wide", blend=0.3)
key("me", "L28", expr="worried", blend=0.5)
key("me", "L30", expr="terrified", blend=0.4)
hide("me", "L32")
put("me", "L32", (-5.9, -2.95), yaw=90, expr="soft", arms=[0, 0])
walk("me", "L32.2", ME, expr="soft")
key("me", "L32.2", yaw=yaw_to(ME, DAIS), **PAINT, expr="soft", blend=0.3)
key("me", "L32.3", expr="neutral", arms=[10, 78], blend=0.5)
key("me", "L34", expr="soft", arms=[10, 40], head=[26, 0], blend=0.5)
key("me", "L35", expr="wide", head=[0, 0], blend=0.4)
put("me", "L36", (ME[0] - 0.1, ME[1] + 0.05), yaw=yaw_to(ME, U5), expr="soft", arms=[0, 0])
hide("me", "L37")
put("me", "L37", (HX - 0.35, 1.9), yaw=0, expr="smile", arms=[0, 0])
hide("me", "L38")

# the faded one: Mum's body, all pine on the dais stool and the spare stools, then herself
SIT = {"sit": True, "arms": [24, 24], "side": [0, 0], "lean": 0, "bendto": [0, 0, 0]}


def rel(U, yaw, toward):
    return round(wrap(yaw_to(U, toward) - yaw), 1)


UB = (0.9, 2.7)      # S05b: faded Mum on a spare stool at the back of the life room, nobody looking at her
put("mum", "L05.4", (UB[0], UB[1], Z_SPARE), yaw=yaw_to(UB, DAIS), expr="blank", fade=1.0, fade_h=1.0, stage=0, **SIT)
hide("mum", "L06")
put("mum", "L11", (U1[0], U1[1], Z_DAIS), yaw=Y1, expr="blank", fade=1.0, fade_h=1.0, stage=0, **SIT)
key("mum", "L17", stage=1)
put("mum", "L18", (U3[0], U3[1], Z_SPARE), yaw=Y3, expr="blank", head=[rel(U3, Y3, ME), 0], fade=1.0, fade_h=1.0, stage=1, **SIT)
put("mum", "L19.3", (U4[0], U4[1], Z_SPARE), yaw=Y4, expr="blank", head=[rel(U4, Y4, ME), 0], fade=1.0, fade_h=1.0, stage=2, **SIT)
put("mum", "L23", (U5[0], U5[1], Z_SPARE), yaw=Y5, expr="blank", head=[rel(U5, Y5, PAIRCAM(2.4, 1.5)), 0], fade=1.0, fade_h=1.0, stage=2, **SIT)
_dx, _dy = U5[0] - ME[0], U5[1] - ME[1]
_dn = math.hypot(_dx, _dy)
key("mum", "L24", pos=[round(U5[0] + _dx / _dn * 0.1, 3), round(U5[1] + _dy / _dn * 0.1, 3), Z_SPARE + 0.12], head=[-25, 4], bendto=[ME[0], ME[1], 0], blend=0.0)
key("mum", "L25", bendto=[ME[0], ME[1], 0], blend=0.0)
hide("mum", "L26")
put("mum", "L28", (U5[0], U5[1], Z_SPARE), yaw=Y5, expr="blank", head=[0, 0], fade=1.0, fade_h=1.0, stage=2, **SIT)
key("mum", "L30", yaw=yaw_to(U5, (0.5, -8.0)), blend=0.0)
put("mum", "L32", (U5[0], U5[1], Z_SPARE), yaw=Y5, expr="blank", head=[0, 0], fade=1.0, fade_h=1.0, stage=2, **SIT)
key("mum", "L33.2", expr="soft", fade=1.0, fade_h=1.0, stage=3)
key("mum", "L33+1.5", fade_h=0.0, blend=1.0)
key("mum", "L33+1.9", fade=0.0, blend=1.0)
key("mum", "L34+2.8", expr="smile", blend=0.3)
key("mum", "L35", expr="soft", fade=0.0, fade_h=0.0, head=[rel(U5, Y5, PP(7)), 0], blend=0.4)
put("mum", "L36", (U5[0] + 0.3 * N8[0], U5[1] + 0.3 * N8[1], 0.0), yaw=yaw_to(U5, P5), expr="soft", fade=0.0, fade_h=0.0,
    arms=[0, 0], head=[0, 0], lean=0, bendto=[0, 0, 0], sit=False)
key("mum", "L36.4", expr="smile", blend=0.3)
hide("mum", "L37")
put("mum", "L37", (HX - 0.35, 0.5), yaw=180, expr="smile", fade=0.0, fade_h=0.0, arms=[0, 0], sit=False)
hide("mum", "L38")

# Mr Dobbs, the montage sitter on the dais, half faded, being painted back in
put("ade", "L05", (U1[0], U1[1], Z_DAIS), yaw=yaw_to(U1, (3.0, -2.7)), expr="soft", fade=0.3, fade_h=0.5, stage=0, **SIT)
key("ade", "L05.6", fade=0.0, fade_h=0.0, blend=3.0)
hide("ade", "L06")

# the bus stop, the cafe, the bakery
put("bus", 0, BUS, yaw=0, expr="worried", fade=0.4, fade_h=0.8, stage=0, head=[0, 0])
hide("bus", "L03")
put("walk1", 0, (78.0, 1.3), yaw=90, expr="neutral", arms=[0, 0])
walk("walk1", "L03", (83.5, 1.3))
hide("walk1", "L03")
put("walk2", "L02.2", (83.5, 1.0), yaw=-90, expr="neutral", arms=[0, 0])
walk("walk2", "L03", (78.5, 1.0))
hide("walk2", "L03")
put("cpA", "L03", (CAF[0] - 0.55, CAF[1], -0.06), yaw=90, expr="angry", arms=[0, 0], head=[0, 0], **{"sit": True})
key("cpA", "L03.2", expr="wide", blend=0.2)
hide("cpA", "L04")
put("cpB", "L03", (CAF[0] + 0.55, CAF[1], -0.06), yaw=-90, expr="angry", arms=[0, 0], head=[0, 0], **{"sit": True})
key("cpB", "L03.2", expr="wide", blend=0.2)
hide("cpB", "L04")
put("baker", "L04", (BAK[0], 1.75), yaw=0, expr="angry", arms=[0, 0])
hide("baker", "L05")
put("cust", "L04", BAK, yaw=180, expr="worried", arms=[0, 0])
key("cust", "L04.2", expr="scared", blend=0.4)
hide("cust", "L05")

# Kofi
put("kofi", "L10", (-4.3, -1.6), yaw=-90, arms=[34, 34], expr="smile")
put("kofi", "L10.3", (-1.0, -0.4), yaw=40, expr="smile", arms=[0, 0])
hide("kofi", "L11")
put("kofi", "L38", (0.3, -1.45), yaw=180, expr="smile", arms=[40, 40])
hide("kofi", "L39")

# the sting sitter
put("sit2", "L39", (U1[0], U1[1], Z_DAIS), yaw=0, expr="blank", fade=1.0, fade_h=1.0, stage=0, **SIT)

# ---------------------------------------------------------------------------------------------------- cues
cues = [
    {"at": 0, "name": "time", "set": "bus"},
    {"at": "L03", "name": "time", "set": "cafe"},
    {"at": "L04", "name": "time", "set": "bake"},
    {"at": "L05", "name": "time", "set": "warm"},
    {"at": "L06", "name": "time", "set": "flat"},
    {"at": "L07.2", "name": "time", "set": "end"},
    {"at": "L08", "name": "time", "set": "flat"},
    {"at": "L09", "name": "time", "set": "night"},
    {"at": "L29", "name": "time", "set": "pair"},
    {"at": "L30", "name": "time", "set": "night"},
    {"at": "L32", "name": "time", "set": "warm"},
    {"at": "L37", "name": "time", "set": "end"},
    {"at": "L38", "name": "time", "set": "cold"},
    # the hall: bare, then with the portrait
    {"at": 0, "name": "hall", "state": "now"},
    {"at": "L37", "name": "hall", "state": "hung"},
    {"at": "L38", "name": "hall", "state": "now"},
    {"at": 0, "name": "drawer", "open": 0.0},
    # my class canvas: 0 cross, ovals and corner lines, 1 the nose, 2 a mouth corner, 4 Mum's eyes, 5 finished
    {"at": 0, "name": "canvas", "stage": 0},
    {"at": "L15.4", "name": "canvas", "stage": 1},
    {"at": "L19.2", "name": "canvas", "stage": 2},
    {"at": "L33", "name": "canvas", "stage": 4},
    {"at": "L34+2.6", "name": "canvas", "stage": 5},
    # the other canvases: the fruit; Petra's pencil bowl, then her pear
    {"at": 0, "name": "easel", "i": 7, "img": "pencil"},
    {"at": "L20", "name": "easel", "i": 7, "img": "pear"},
    {"at": "L05", "name": "easel", "i": 3, "img": "ade"},
    {"at": "L09", "name": "easel", "i": 3, "img": "bowlB"},
    # the spare stool (paint-spattered): where faded Mum sits
    {"at": 0, "name": "stool", "on": False},
    {"at": "L05.4", "name": "stool", "on": True, "pos": list(UB), "yaw": yaw_to(UB, DAIS)},
    {"at": "L06", "name": "stool", "on": False},
    {"at": "L18", "name": "stool", "on": True, "pos": list(U3), "yaw": Y3},
    {"at": "L19.3", "name": "stool", "on": True, "pos": list(U4), "yaw": Y4},
    {"at": "L23", "name": "stool", "on": True, "pos": list(U5), "yaw": Y5},
    {"at": "L26", "name": "stool", "on": False},
    {"at": "L28", "name": "stool", "on": True, "pos": list(U5), "yaw": Y5},
    {"at": "L37", "name": "stool", "on": False},
    # props
    {"at": 0, "name": "prop", "which": "canvas_carry", "on": False},
    {"at": "L09.1", "name": "prop", "which": "canvas_carry", "on": True},
    {"at": "L10", "name": "prop", "which": "canvas_carry", "on": False},
    {"at": 0, "name": "prop", "which": "coat", "on": False},
    {"at": "L25", "name": "prop", "which": "coat", "on": True},
    {"at": "L26", "name": "prop", "which": "coat", "on": False},
    {"at": 0, "name": "prop", "which": "brushdrop", "on": False},
    {"at": "L35.2", "name": "prop", "which": "brushdrop", "on": True},
    {"at": "L37", "name": "prop", "which": "brushdrop", "on": False},
    # the one power dip: down 1.2 s, held dim across the cut, back up 1.2 s into S23. Never dark
    {"at": "L22.2", "name": "dip", "down": 1.2, "hold": 0.0, "hold_to": "L23", "up": 1.2, "depth": 0.6},
]

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L11.3", "kind": "sting", "db": -20},
    {"at": "L22.2", "kind": "hum_sweep", "db": -20},
    {"at": "L23", "kind": "hit", "db": -6},
    {"at": "L31", "kind": "sting", "db": -14},
    {"at": "L25", "kind": "door", "db": -12},
    {"at": "L34", "kind": "riser", "db": -26, "dur": 2.6},
    {"at": "L34+1.6", "kind": "chime", "db": -22},
    {"at": "L35.2", "kind": "thud", "db": -18},
    {"at": "L40>", "kind": "glide", "db": -16, "dur": 0.9},
]

story = {
    "slug": "ep32-sitter",
    "title": "In This Town Your Face FADES If Nobody Looks",
    "made_for_kids": False,
    "premise": "In a town where your face fades to bare wood if nobody looks at you, and lonely people sit for the portrait class to be painted back in, I join that class to learn to finish a face. I haven't spoken to Mum since spring. On the dais stool sits someone faded all the way to raw pine and pencil guide lines, and every week its face copies the line I stopped on and it sits one easel nearer.",
    "twist": "Faded all the way, nobody can see you except someone who loves you, which is why the others paint the fruit and say the stool has been empty for months. The faded sitter is Mum, gone unlooked-at since I stopped speaking to her in spring, and the half face on my canvas is the one I have been failing to finish on my portrait of her at home. I finish the face from memory without stopping, the colour comes back up her, and she says not bad. The sting: a new faded sitter on the stool, and nobody else looks up.",
    "world": "a town where unlooked-at faces fade to wood: a sunny bus stop and a cafe and a bakery counter for the montage, my small flat with one easel, and a community arts centre life room on rainy Wednesday evenings with eight easels round a pine dais, a stool, a green cushion and a bowl of fruit, plus Mum's bare front hall",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#4cc3f0",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#1b2230", "fog_density": 0.012, "fog_start": 9.0, "sky": "#0c1018", "sky_strength": 1.0, "exposure": 0.6,
             "flash_safe": True},
    "grade": {"shadows": [-0.02, 0.0, 0.05], "highlights": [0.03, 0.01, -0.02], "saturation": 0.95, "contrast": 1.08,
              "vignette": 0.34, "bloom": 0.25, "grain": 0.012},
    "rain_shots": rain_shots,
    "phonemes": {"Kofi": "kˈOfi"},
    "geom": {"RE": RE, "RP": RP, "TH": TH, "faders": FADERS},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 45, "mode": "minor", "bpm": 68, "seed": 32,
              "sections": [
                  {"at": 0, "voices": ["pad", "pulse"], "energy": 0.32},
                  {"at": "L09", "voices": ["pad", "pulse"], "energy": 0.38},
                  {"at": "L22", "voices": ["drone", "pad"], "energy": 0.42},
                  {"at": "L26", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L30", "voices": ["drone", "pad", "choir"], "energy": 0.4},
                  {"at": "L32", "voices": ["pad", "piano"], "energy": 0.4, "mode": "major", "root": 45, "bpm": 76},
                  {"at": "L38", "voices": ["drone"], "energy": 0.3, "mode": "minor", "bpm": 68},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "end", "lufs": -34},
                  {"kind": "rain", "from": "L09", "to": "L32", "lufs": -30, "lp": 3500},
                  {"kind": "hum", "from": "L10", "to": "L32", "lufs": -42},
                  {"kind": "rain", "from": "L38", "to": "end", "lufs": -34, "lp": 3500},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "L23-0.6", "to": "L23"}, {"from": "L31-0.7", "to": "L31", "keep": ["sting"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
