"""Writes ../story.json for ep32 "sitter" (script.md, 2026-11-02).

Run from anywhere: python stories/ep32-sitter/generator/make_story.py
The words are in lines.json next to this file (made from the script by script_to_lines.py). Everything else is here:
the cast, the geometry of the life room, the shots and their cameras, the acting, the cues set.py reads, the effects,
the score and the sound. Places are set.py's (metres, floor z = 0). A character with yaw 0 faces -y; yaw 90 faces +x.

The life room is centred on the dais at the origin. Easel i stands at angle TH[i] on a curve of radius RE, its canvas
facing out; its painter stands at radius RP behind it, facing the dais. The two wider gaps (between easels 4 and 5, 6
and 7) are where the Unpainted sits in weeks 3 and 4. The hall (Mum's, x = 40) and the kitchen (x = -40) are separate
little sets in the same scene.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# ---------------------------------------------------------------------------------------------------- holds
HOLDS = {}                       # id -> seconds (a line's gap, or a pause beat's length)
LOOP = 0.25
for ln in lines:
    if ln["id"] in HOLDS:
        ln["gap"] = HOLDS[ln["id"]]
PAUSES = {"L40": ("P41", 0.8), "L12": ("P12", 0.5), "L46": ("P46", 0.5)}
out_lines = []
for ln in lines:
    out_lines.append(ln)
    if ln["id"] in PAUSES:
        pid, dur = PAUSES[ln["id"]]
        out_lines.append({"id": pid, "pause": dur, "chunks": []})
lines = out_lines + [{"id": "PEND", "pause": LOOP, "chunks": []}]

TEMPO = {"L05": 0.93, "L22": 0.95, "L50": 0.94}
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


cast = {
    "me": person("#e3b48e", "#d3a022", "#33363c", "cap", "#14120f", pattern="knit", pattern_c="#bd8d19", shoes="#e8e8e6"),
    "mum": person("#e8c4a2", "#2f7f82", "#39393f", "long", "#c4c8cc", pattern="plaid", pattern_c="#256a6c",
                  collar="#efe6d4", extras=["glasses"], extra_c="#6b4a2e", eyes="tired", height=0.96),
    "kofi": person("#c68a5e", "#b4522f", "#3a3a40", "none", "#1a1410", extras=["glasses", "apron"], extra_c="#4a6788",
                   collar="#9b4326"),
    "petra": person("#f0cfae", "#f2f2f0", "#2d3b5c", "bun", "#b4622e", pattern="stripes", pattern_c="#26365c"),
    "ade": person("#d9a67e", "#78803c", "#4a4033", "none", "#8a8a88", hat="ballcap", hat_c="#6b4a2e", pattern="plaid",
                  pattern_c="#5a6230", eyes="tired", height=0.98),
    "bg1": person("#b97d54", "#6e3b63", "#2e3138", "cap", "#1d1612", pattern="knit", pattern_c="#5a2f52"),
    "bg2": person("#f2d2b4", "#4d5a6b", "#3a3530", "long", "#6b4a32", pattern="solid"),
    "bg3": person("#8e5a3e", "#9aa3ad", "#242830", "cap", "#0f0d0c", pattern="stripes", pattern_c="#6b7580"),
    "bg4": person("#e3b48e", "#8b4f59", "#2f3640", "bun", "#2a2018", pattern="knit", pattern_c="#6e3b45"),
    "bg5": person("#d9a67e", "#56706a", "#33302c", "cap", "#6e6a64", pattern="plaid", pattern_c="#3f524e"),
}
PAINTERS = {1: "ade", 2: "bg1", 3: "bg2", 4: "bg3", 5: "bg4", 6: "bg5", 7: "petra", 8: "me"}

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


def over(i, rc, dth, z, tz=1.3):
    """Behind easel i's painter, looking at the canvas: (loc, tgt)."""
    p = pol(rc, TH[i - 1] + dth)
    e = E(i)
    return [p[0], p[1], z], [e[0], e[1], tz]


def canvas_cam(i, dist, z=1.3, lens=30, push=0.0, side=0.0, cs=0.0):
    e = E(i)
    n = (math.cos(math.radians(TH[i - 1])), math.sin(math.radians(TH[i - 1])))
    t = (-n[1], n[0])
    tgt = [e[0] + t[0] * side, e[1] + t[1] * side, z]
    a = [tgt[0] + n[0] * dist + t[0] * cs, tgt[1] + n[1] * dist + t[1] * cs, z]
    b = [tgt[0] + n[0] * (dist - push) + t[0] * cs, tgt[1] + n[1] * (dist - push) + t[1] * cs, z]
    return c([0, a, tgt, lens], [1, b, tgt, lens]) if push else still(a, tgt, lens)


DAIS = (0.0, 0.0)
ME, PETRA, ADE = PP(8), PP(7), PP(1)
# the Unpainted's places: (x, y, body yaw). Week 1 on the dais stool; week 2 beyond easel 1's end; week 3 in the gap
# between easels 4 and 5; week 4 in the gap between 6 and 7; week 5 beyond easel 8's end
U1 = (0.0, 0.0)
U2 = pol(RP, TH[0] - 17)
U3 = pol(RP, (TH[3] + TH[4]) / 2)
U4 = pol(RP, (TH[5] + TH[6]) / 2)
U5 = pol(RE, TH[7] + 11.5)
U5b = U5
Y2, Y3, Y4, Y5 = (yaw_to(U2, DAIS), yaw_to(U3, DAIS), yaw_to(U4, DAIS), yaw_to(U5, DAIS))
N8 = (math.cos(math.radians(TH[7])), math.sin(math.radians(TH[7])))      # outward at easel 8
T8 = (-N8[1], N8[0])
C8 = E(8)
MD8 = [(C8[0] + U5[0]) / 2, (C8[1] + U5[1]) / 2]                          # between my canvas and its head


def o5(d, z, along=0.0, side=False):
    """A camera d metres out from its head along the way its head faces (away from the dais); side: d out and `along` to the north."""
    L = math.hypot(*U5)
    f = (U5[0] / L, U5[1] / L)
    t = (-f[1], f[0])
    if side:
        return [U5[0] + t[0] * along + f[0] * d, U5[1] + t[1] * along + f[1] * d, z]
    return [U5[0] + f[0] * d + t[0] * along, U5[1] + f[1] * d + t[1] * along, z]


def out8(d, z, along=0.0):
    return [MD8[0] + N8[0] * d + T8[0] * along, MD8[1] + N8[1] * d + T8[1] * along, z]

Y1 = yaw_to(U1, ME)


def mid_yaw(a, b):
    """The yaw halfway between a and b along the short way round."""
    d = (b - a + 180) % 360 - 180
    return a + d / 2


def fc(U, yaw_face, d, z, off=0.0):
    """A camera d metres in front of a face that looks along yaw_face (off swings it round)."""
    return front(U, yaw_face + off, d, z)

HEAD_Z = 1.62          # the head's centre when seated on the floor stool (set.py's figure)

# the little sets (x offsets)
HX, KX = 40.0, -40.0

# ---------------------------------------------------------------------------------------------------- shots
# (id, at, what, step, cam, flags)
SH = []


def shot(sid, at, what, cam, step=2, **flags):
    SH.append((sid, at, what, step, cam, flags))


# 01 the criticism
shot("S01", 0, "my canvas: cross and two ovals", canvas_cam(8, 1.25, 1.25, 30, push=0.3), 2)
shot("S02", "L02", "Mum's hall, then: frames edge to edge, Mum hanging one", still([HX + 1.15, 1.7, 1.45], [HX - 1.0, 1.0, 1.4], 17))
shot("S03", "L03", "the hall now: bare hooks, pale squares", still([HX + 1.15, 1.7, 1.45], [HX - 1.0, 1.0, 1.4], 17))
shot("S03b", "L03.1", "a drawer half open, brushes in a jar on their side", still([HX + 0.3, 1.9, 1.35], [HX + 0.2, 2.7, 0.5], 30))
shot("S04", "L04", "the arts centre on its hill in rain",
     still([-15.0, -17.0, 9.0], [-1.0, -2.0, 1.6], 22), rain=True)
shot("S04b", "L04.2", "me on the rain-dark steps with a canvas",
     still([-8.7, -4.5, 1.55], [-6.2, -3.0, 1.1], 26), rain=True)
# 02 week one
shot("S05", "L05", "overhead of the life room", still([0.01, -3.2, 9.4], [0, -0.6, 0.5], 20), noceil=True)
shot("S06", "L06", "Kofi sets the stool and plumps the cushion", still([2.6, 2.4, 1.6], [-0.4, -0.3, 0.9], 28))
shot("S07", "L07", "Kofi's face", still(front((-1.0, -0.4), 40, 1.9, 1.6), [-1.0, -0.4, 1.5], 36))
shot("S08", "L08", "the fruit bowl, Kofi going out", still([-2.6, -4.2, 1.45], [-5.05, -2.0, 1.0], 27))
shot("S09", "L09", "over my shoulder to the dais", still([4.4, -0.9, 1.75], [0.0, 0.0, 1.15], 26))
shot("S10", "L10", "low wide on the Unpainted", still(front(U1, Y1 - 25, 3.2, 0.75), [0.0, 0.0, 1.3], 24))
shot("S11", "L11", "push on its head", move((front(U1, Y1, 2.6, 1.95), [0, 0, 1.75]), (front(U1, Y1, 1.8, 1.9), [0, 0, 1.75]), 38, 38))
shot("S12", "L12", "its face: the cross and two ovals", still(front(U1, Y1, 1.15, 1.85), z3(U1, 1.78), 44))
shot("S13", "L13", "Petra's canvas: a pencil bowl of fruit", canvas_cam(7, 1.3, 1.3, 30), hide_cast=["petra"])
shot("S14", "L14", "the curve from behind the dais", still([0.0, 3.0, 1.9], [0.0, -3.4, 1.2], 22))
shot("S15", "L15", "me at my easel, side on", still([4.6, 1.2, 1.55], [3.5, -0.5, 1.4], 30))
shot("S16", "L16", "my canvas: the nose begins", canvas_cam(8, 1.3, 1.25, 30), hide_cast=["me"])
shot("S17", "L17", "my face, eyes wide", still(front(ME, yaw_to(ME, DAIS) - 50, 1.5, 1.6), z3(ME, 1.55), 36))
shot("S17b", "L17.1", "Mum at a kitchen table, years ago", still([KX + 0.4, -1.1, 1.45], [KX - 0.2, 0.3, 1.5], 38))
shot("S17c", "L17.2", "my face again", still(front(ME, yaw_to(ME, DAIS) - 50, 1.4, 1.58), z3(ME, 1.55), 38))
shot("S18", "L18", "the canvas: a nose stopped short", canvas_cam(8, 1.2, 1.25, 34), hide_cast=["me"])
shot("S19", "L19", "Kofi in the doorway with a mug", still([-2.0, -3.5, 1.5], [-4.9, -3.0, 1.4], 30))
shot("S19b", "L19.1", "the cushion under it, flat", still([1.0, -0.7, 0.95], [0.0, 0.0, 0.62], 34))
# 03 weeks two to four
shot("S20", "L20", "its face: the nose", still(fc(U2, yaw_to(U2, ME), 1.2, 1.7), z3(U2, 1.55), 40))
shot("S20b", "L20.2", "my canvas: the same short nose", canvas_cam(8, 1.2, 1.25, 34), hide_cast=["me"])
shot("S21", "L21", "the empty dais stool, pan to the first easel",
     c([0, [2.9, -0.2, 1.3], [0, 0, 0.7], 24], [1, [2.9, -0.2, 1.3], [-3.6, 0.3, 1.2], 24]))
shot("S22", "L22", "over Mr Ade's shoulder: fruit in oils", canvas_cam(1, 1.3, 1.3, 28, cs=-0.5), hide_cast=["ade"])
shot("S23", "L23", "my phone on the easel shelf, glowing", still([C8[0] + N8[0] * 0.8 + T8[0] * 0.3, C8[1] + N8[1] * 0.8 + T8[1] * 0.3, 1.15], [C8[0] + N8[0] * 0.15, C8[1] + N8[1] * 0.15, 0.85], 36), hide_cast=["me"])
shot("S23b", "L23.1", "Mum in her kitchen, phone to her ear", still([KX + 0.7, -0.3, 1.45], [KX - 0.3, 1.0, 1.45], 36))
shot("S24", "L24", "one mouth corner", canvas_cam(8, 1.2, 1.2, 34), hide_cast=["me"])
shot("S25", "L25", "my face, jaw tight", still(front(ME, yaw_to(ME, DAIS) - 50, 1.3, 1.5), z3(ME, 1.5), 40))
shot("S26", "L26", "its face: the mouth corner", still(fc(U3, mid_yaw(yaw_to(U3, ME), Y3), 1.4, 1.7), z3(U3, 1.55), 40), hide_easels=[4, 5], hide_cast=["bg3", "bg4"])
shot("S27", "L27", "overhead: it sits mid curve", still([0.01, -1.4, 9.4], [0, -1.6, 0.5], 20), noceil=True)
shot("S28", "L28", "its head turned to my corner", still(fc(U3, mid_yaw(yaw_to(U3, ME), Y3), 2.4, 1.75), z3(U3, 1.72), 34), hide_easels=[5], hide_cast=["bg4"])
shot("S29", "L29", "an eyebrow on my canvas", canvas_cam(8, 1.2, 1.35, 34), hide_cast=["me"])
shot("S30", "L30", "my bag zipped on the stool", canvas_cam(8, 1.9, 0.95, 30), hide_cast=["me"])
shot("S31", "L31", "its face: an eyebrow", still(fc(U4, mid_yaw(yaw_to(U4, ME), Y4), 1.4, 1.7), z3(U4, 1.55), 40), hide_easels=[6, 7], hide_cast=["bg5"])
shot("S32", "L32", "Petra, and the Unpainted beside her", still([1.3, -0.5, 1.75], [mid(U4, PETRA, 1.2)[0], mid(U4, PETRA, 1.2)[1], 1.3], 26), hide_easels=[7])
shot("S33", "L33", "its knee by her palette", still(front(U4, Y4, 1.5, 0.62), [U4[0] + (PETRA[0] - U4[0]) * 0.5, U4[1] + (PETRA[1] - U4[1]) * 0.5, 0.75], 30), hide_easels=[7])
shot("S34", "L34", "Petra's pear", canvas_cam(7, 1.3, 1.3, 30), hide_cast=["petra"])
shot("S35", "L35", "me, eyes on the floor", still(front(ME, yaw_to(ME, DAIS) - 50, 1.3, 0.85), z3(ME, 1.45), 40))
# 04 week five
shot("S36", "L36", "the rain on the north window", still([0.0, -1.0, 1.6], [0.0, 5.0, 1.9], 24))
shot("S37", "L37", "wide of the room, the lamps sag", still([-4.6, -4.2, 1.9], [0.8, 0.3, 1.3], 20))
shot("S38", "L38", "Petra painting, her spare stool empty", still([1.3, -0.5, 1.75], [mid(U4, PETRA, 1.0)[0], mid(U4, PETRA, 1.0)[1], 1.0], 26), hide_easels=[7])
shot("S39", "L39", "me, eyes to the side", still(front(ME, yaw_to(ME, DAIS) - 65, 1.2, 1.55), z3(ME, 1.5), 40))
shot("S40", "L40", "the second dip", still([-4.6, -4.2, 1.9], [0.8, 0.3, 1.3], 20))
shot("S40b", "P41", "dim, held", still([-4.6, -4.2, 1.9], [0.8, 0.3, 1.3], 20))
shot("S41", "L41", "it is right beside me", still([0.9, -0.1, 1.5], [3.1, 0.1, 1.5], 24))
shot("S42", "L42", "its knee against my easel leg", still([1.6, 1.0, 0.55], [U5[0] - 0.35, U5[1] - 0.2, 0.5], 32))
shot("S43", "L43", "from behind: its head turned right round", still(o5(1.9, 1.95, 0.7), [U5[0], U5[1], 1.7], 26))
shot("S44", "L44", "profile: its face an inch from my canvas", still(o5(0.4, 1.6, 2.0, side=True), [MD8[0], MD8[1], 1.6], 40))
shot("S45", "L45", "straight on: the two faces", still(o5(2.3, 1.6), [MD8[0], MD8[1], 1.55], 30))
shot("S46", "L46", "its empty ovals", still(o5(1.4, 1.8), [U5[0], U5[1], 1.74], 44))
shot("S46b", "P46", "its ovals, held", still(o5(1.2, 1.8), [U5[0], U5[1], 1.74], 50))
shot("S47", "L47", "my coat on the peg, the door swinging", still([-3.0, -4.1, 1.5], [-5.5, -3.0, 1.2], 26))
# 05 the car park
PETRA_C, ME_C = (-2.5, -8.9), (-1.2, -8.5)
shot("S48", "L48", "car park, rain, Petra jogging over with my coat", still([-6.5, -12.5, 1.0], [-2.3, -9.0, 0.9], 26), rain=True)
shot("S49", "L49", "two-shot under the lamp", still([-1.9, -12.0, 0.8], [-1.8, -8.9, 0.95], 36), rain=True)
shot("S50", "L50", "Petra amused", still(front(PETRA_C, yaw_to(PETRA_C, ME_C) - 60, 1.3, 1.15), z3(PETRA_C, 1.05), 40), rain=True)
shot("S51", "L51", "me, the words landing", still(front(ME_C, yaw_to(ME_C, PETRA_C) + 60, 1.3, 1.15), z3(ME_C, 1.05), 40), rain=True)
shot("S52", "L52", "Petra shrugging", still(front(PETRA_C, yaw_to(PETRA_C, ME_C) + 55, 1.5, 1.1), z3(PETRA_C, 1.0), 38), rain=True)
shot("S53", "L53", "through the window, every canvas", still([0.2, -9.5, 1.9], [0.0, -2.0, 1.3], 24), rain=True)
shot("S54", "L54", "push in: seven bowls of fruit, then mine", c([0, [0.5, -9.0, 1.7], [0.5, -2.0, 1.3], 28], [1, [1.0, -7.0, 1.6], [2.4, -0.8, 1.4], 36]), rain=True)
shot("S55", "L55", "the empty stool, the flat cushion", c([0, [0.3, -9.0, 1.4], [0.0, 0.0, 0.8], 30], [1, [0.2, -7.0, 1.2], [0.0, 0.0, 0.75], 34]), rain=True)
shot("S56", "L56", "overhead: eight easels and a stool", still([0.01, -3.0, 9.4], [0, -0.6, 0.5], 20), noceil=True)
shot("S57", "L57", "it sits in, seen through the glass", still([0.5, -8.0, 1.6], [U5[0], U5[1], 1.45], 40), rain=True)
shot("S58", "L58", "its blank face behind wet glass", still([0.5, -8.0, 1.78], [U5[0], U5[1], 1.76], 100), rain=True)
shot("S59", "L59", "my canvas and its face, side by side", still(o5(2.1, 1.55), [MD8[0], MD8[1], 1.55], 30))
shot("S60", "L60", "me in the rain, understanding", still(front(ME_C, yaw_to(ME_C, PETRA_C) + 40, 1.2, 1.15), z3(ME_C, 1.05), 40), rain=True)
shot("S61a", "L61", "its four places: the dais", still(front(U1, Y1, 2.2, 1.7), z3(U1, 1.4), 32))
shot("S61b", "L61.1", "its four places: by easel 1", still(front(U2, Y2, 2.2, 1.7), z3(U2, 1.4), 32))
shot("S61c", "L61.2", "its four places: the gap", still(front(U3, Y3, 2.2, 1.7), z3(U3, 1.4), 32))
shot("S61d", "L61.3", "its four places: beside Petra", still(front(U4, Y4, 2.2, 1.7), z3(U4, 1.4), 32))
# 06 week six
shot("S62", "L62", "the room, warm, me walking in", still([-3.4, -3.6, 1.65], [2.6, -0.4, 1.35], 22))
shot("S63", "L63", "it at my elbow, waiting", still([1.3, 1.1, 1.6], [3.1, 0.0, 1.45], 26))
shot("S64", "L64", "me painting, steady", still([4.6, -2.3, 1.55], [3.7, -0.7, 1.4], 30))
shot("S65", "L65", "Mum's eyes on my canvas", canvas_cam(8, 1.0, 1.3, 34), hide_cast=["me"])
shot("S66", "L66", "the finished portrait", canvas_cam(8, 1.1, 1.25, 30, push=0.1), hide_cast=["me"])
shot("S67", "L67", "the spare stool, empty", still([2.0, 0.9, 1.1], [U5[0], U5[1], 0.45], 30))
shot("S68", "L68", "the dais stool: a dent in the cushion", still([1.1, -1.6, 1.3], [0.0, 0.0, 0.55], 30))
# 07 the show
shot("S69", "L69", "Mum at the door in daylight", still([-1.8, -1.0, 1.6], [-5.2, -2.85, 1.45], 26))
shot("S70", "L70", "the dais on its edge: nine strokes", still([-1.2, 1.8, 1.1], [-5.3, 1.8, 0.75], 22))
shot("S71", "L71", "Mum before my painting", still([-1.4, -0.9, 1.65], [-5.5, -0.9, 1.5], 26))
shot("S72", "L72", "Mum's face", still([-4.95, -1.9, 1.55], [-4.2, -0.9, 1.55], 38))
shot("S73", "L73", "me and Mum, the painting between us", still([-1.8, -0.8, 1.6], [-5.2, -0.8, 1.45], 26))
shot("S74", "L74", "Kofi grinning, Mum's hand up", still([-5.0, -0.1, 1.55], [-2.8, 0.1, 1.5], 26))
# 08 Mum's hall
shot("S75", "L75", "Mum's hall, bright morning, lifting the painting", still([HX + 1.1, 0.3, 1.5], [HX - 1.0, 1.4, 1.4], 18))
shot("S76", "L76", "the portrait hung alone, the jar below", still([HX + 1.1, 0.3, 1.45], [HX - 1.0, 1.2, 1.4], 18))

shots = []
for i, (sid, at, what, step, cam, fl) in enumerate(SH):
    s = {"id": sid, "cam": cam, "hand": 0.0 if sid in ("S70", "S12", "S46", "S46b", "S45") else 0.006, "step": step, "what": what}
    s.update({k: v for k, v in fl.items() if k in ("noceil", "hide_easels", "hide_cast")})
    if i:
        s["at"] = at
    shots.append(s)
rain_shots = [s[0] for s in SH if s[5].get("rain")]

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

# painters: at their easels from the overhead on, until the class has ended (L53), and back for my sixth week
for i, who in PAINTERS.items():
    if who == "me":
        continue
    p = PP(i)
    put(who, "L05", p, yaw=yaw_to(p, DAIS), **PAINT)
    if who in ("petra",):
        key(who, "L33", expr="smirk", blend=0.4)
        key(who, "L35", expr="neutral", blend=0.4)
    if who == "petra":
        put("petra", "L48", PETRA_C + (-0.45,), yaw=yaw_to(PETRA_C, ME_C), expr="smirk")
        key("petra", "L52", expr="neutral", blend=0.3)
    hide(who, "L53")
# the five background painters stay home for the show; Petra and Ade return as one of the room
# me
put("me", 0, ME, hidden=True)
hide("me", 0)
put("me", "L04.2", (-5.9, -3.0), yaw=90, expr="worried", arms=[0, 0])
hide("me", "L05")
put("me", "L09", ME, yaw=yaw_to(ME, DAIS), expr="worried", **PAINT)
key("me", "L12", expr="scared", blend=0.3)
key("me", "L15", expr="neutral", blend=0.3)
key("me", "L17", expr="wide", blend=0.2)
key("me", "L19", expr="worried", blend=0.4)
key("me", "L24", expr="worried", head=[0, 12])
key("me", "L25", expr="angry", blend=0.3)
key("me", "L29", expr="scared", blend=0.3)
key("me", "L35", expr="worried", head=[0, 38], blend=0.4)
key("me", "L39", expr="terrified", head=[-30, 6], look=[1, 0], blend=0.3)
key("me", "L41", expr="terrified", head=[0, 0], look=[0, 0], blend=0.1)
key("me", "L46", expr="scared")
hide("me", "L47")
put("me", "L48", ME_C + (-0.45,), yaw=yaw_to(ME_C, PETRA_C), expr="scared")
key("me", "L50", expr="worried", blend=0.4)
key("me", "L51", expr="wide", blend=0.3)
key("me", "L60", expr="worried", blend=0.5)
hide("me", "L61")
put("me", "L62", ME, yaw=yaw_to(ME, DAIS), expr="worried", **PAINT)
key("me", "L64", expr="neutral", arms=[10, 78], blend=0.5)
key("me", "L66", expr="soft", arms=[10, 40], blend=0.5)
hide("me", "L67")
put("me", "L73", (-4.2, 0.1), yaw=-90, expr="grin", arms=[0, 0])
hide("me", "L74")
# Mum
put("mum", "L02", (HX - 0.25, 0.6), yaw=-90, arms=[70, 85], expr="grin", head=[0, -6])
hide("mum", "L03")
put("mum", "L17.1", (KX - 0.2, 0.9), yaw=0, expr="angry", head=[0, 0])
key("mum", "L17.1", expr="worried")
hide("mum", "L17.2")
put("mum", "L23.1", (KX - 0.1, 0.7), yaw=38, expr="worried", arms=[0, 34], head=[0, 0])
key("mum", "L23.1+0.5", expr="scared", blend=0.4)
hide("mum", "L24")
put("mum", "L69", (-4.1, -2.75), yaw=90, expr="wide")
walk("mum", "L70", (-4.1, -2.0), expr="wide")
put("mum", "L71", (-4.2, -0.9), yaw=-90, expr="soft")
put("mum", "L72", (-4.2, -0.9), yaw=-90, expr="soft", head=[0, 0])
key("mum", "L72", expr="crying", blend=0.4)
put("mum", "L73", (-4.2, -1.7), yaw=-90, expr="grin")
put("mum", "L74", (-2.8, -0.5), yaw=-90, expr="grin", arms=[0, 110])
hide("mum", "L75")
put("mum", "L75", (HX - 0.3, 1.55), yaw=-90, expr="grin", arms=[75, 75])
hide("mum", "L76")
# Kofi
put("kofi", "L06", (-1.2, -0.7), yaw=yaw_to((-1.2, -0.7), DAIS), arms=[48, 48], expr="grin")
key("kofi", "L06.2", arms=[30, 30], blend=0.4)
put("kofi", "L07", (-1.0, -0.4), yaw=40, expr="grin", arms=[0, 0])
put("kofi", "L08", (-4.0, -1.6), yaw=-120, arms=[0, 0], expr="neutral")
walk("kofi", "L08+1.3", (-5.2, -3.0), arms=[0, 0])
hide("kofi", "L08>")
put("kofi", "L19", (-4.6, -3.05), yaw=60, arms=[0, 62], expr="grin")
hide("kofi", "L19.1")
put("kofi", "L74", (-2.8, 0.6), yaw=-90, expr="grin", arms=[0, 0])
hide("kofi", "L75")
# the characters in the hall/kitchen are hidden again after their shots
for who in acting:
    acting[who].sort(key=lambda k: 0)   # keep the writing order (acting.py sorts by time)

# ---------------------------------------------------------------------------------------------------- cues
def U(at, **kw):
    return {"at": at, "name": "unp", **kw}


cues = [
    {"at": 0, "name": "time", "set": "night"},
    {"at": "L02", "name": "time", "set": "day"},
    {"at": "L04", "name": "time", "set": "night"},
    {"at": "L17.1", "name": "time", "set": "day"},
    {"at": "L17.2", "name": "time", "set": "night"},
    {"at": "L23.1", "name": "time", "set": "day"},
    {"at": "L24", "name": "time", "set": "night"},
    {"at": "L69", "name": "time", "set": "show"},
    {"at": "L75", "name": "time", "set": "day"},
    # the hall
    {"at": 0, "name": "hall", "state": "then"},
    {"at": "L03", "name": "hall", "state": "now"},
    {"at": "L75", "name": "hall", "state": "lift"},
    {"at": "L76", "name": "hall", "state": "hung"},
    {"at": 0, "name": "drawer", "open": 0.55},
    # my canvas: 0 cross and ovals, 1 the nose, 2 mouth corner, 3 eyebrow, 5 finished
    {"at": 0, "name": "canvas", "stage": 0},
    {"at": "L16.1", "name": "canvas", "stage": 1},
    {"at": "L24.1", "name": "canvas", "stage": 2},
    {"at": "L29.1", "name": "canvas", "stage": 3},
    {"at": "L64", "name": "canvas", "stage": 3},
    {"at": "L65", "name": "canvas", "stage": 4},
    {"at": "L66", "name": "canvas", "stage": 5},
    {"at": "L69", "name": "canvas", "stage": 5},
    # the other canvases
    {"at": 0, "name": "easel", "i": 7, "img": "pencil"},
    {"at": "L22", "name": "easel", "i": 7, "img": "bowl2"},
    {"at": "L34", "name": "easel", "i": 7, "img": "pear"},
    # the Unpainted: found already where it is
    U(0, on=False),
    U("L09", on=True, pos=list(U1), yaw=Y1, head=0, dais=True, stage=0, look=list(ME)),
    U("L20", on=True, pos=list(U2), yaw=Y2, head=0, dais=False, stage=1, look=list(ME)),
    U("L26", on=True, pos=list(U3), yaw=Y3, head=0, dais=False, stage=2, look=list(ME)),
    U("L31", on=True, pos=list(U4), yaw=Y4, head=0, dais=False, stage=3, look=list(ME)),
    U("L38", on=False),
    U("L41", on=True, pos=list(U5), yaw=Y5, head=0, dais=False, stage=4),
    U("L43", on=True, pos=list(U5), yaw=Y5, head=180, dais=False, stage=4),
    U("L57", on=True, pos=list(U5), yaw=Y5, look=[0.5, -8.0], dais=False, stage=4),
    U("L59", on=True, pos=list(U5), yaw=Y5, head=180, dais=False, stage=4),
    U("L61", on=True, pos=list(U1), yaw=Y1, head=0, dais=True, stage=0, look=list(ME)),
    U("L61.1", on=True, pos=list(U2), yaw=Y2, head=0, dais=False, stage=1, look=list(ME)),
    U("L61.2", on=True, pos=list(U3), yaw=Y3, head=0, dais=False, stage=2, look=list(ME)),
    U("L61.3", on=True, pos=list(U4), yaw=Y4, head=0, dais=False, stage=3, look=list(ME)),
    U("L62", on=True, pos=list(U5), yaw=Y5, head=180, dais=False, stage=4),
    U("L67", on=False),
    # the spare stool (paint-spattered): under it, and left empty
    {"at": 0, "name": "stool", "on": False},
    {"at": "L20", "name": "stool", "on": True, "pos": list(U2), "yaw": Y2},
    {"at": "L26", "name": "stool", "on": True, "pos": list(U3), "yaw": Y3},
    {"at": "L31", "name": "stool", "on": True, "pos": list(U4), "yaw": Y4},
    {"at": "L41", "name": "stool", "on": True, "pos": list(U5), "yaw": Y5},
    {"at": "L61", "name": "stool", "on": False},
    {"at": "L61.1", "name": "stool", "on": True, "pos": list(U2), "yaw": Y2},
    {"at": "L61.2", "name": "stool", "on": True, "pos": list(U3), "yaw": Y3},
    {"at": "L61.3", "name": "stool", "on": True, "pos": list(U4), "yaw": Y4},
    {"at": "L62", "name": "stool", "on": True, "pos": list(U5), "yaw": Y5},
    {"at": "L69", "name": "stool", "on": False},
    # the dais cushion, the show
    {"at": 0, "name": "cushion", "dent": 0.0},
    {"at": "L68", "name": "cushion", "dent": 1.0},
    {"at": "L69", "name": "show", "on": True},
    {"at": "L75", "name": "show", "on": False},
    # props
    {"at": 0, "name": "prop", "which": "canvas_carry", "on": False},
    {"at": "L04.2", "name": "prop", "which": "canvas_carry", "on": True},
    {"at": "L05", "name": "prop", "which": "canvas_carry", "on": False},
    {"at": 0, "name": "prop", "which": "bag", "on": False},
    {"at": "L30", "name": "prop", "which": "bag", "on": True},
    {"at": "L31", "name": "prop", "which": "bag", "on": False},
    {"at": 0, "name": "prop", "which": "mug", "on": False},
    {"at": "L19", "name": "prop", "which": "mug", "on": True},
    {"at": "L19.1", "name": "prop", "which": "mug", "on": False},
    {"at": 0, "name": "prop", "which": "phone", "on": False},
    {"at": "L23", "name": "prop", "which": "phone", "on": True},
    {"at": "L23.1", "name": "prop", "which": "phone", "on": False},
    {"at": "L23.1", "name": "prop", "which": "phone_mum", "on": True},
    {"at": "L24", "name": "prop", "which": "phone_mum", "on": False},
    {"at": 0, "name": "prop", "which": "coat", "on": False},
    {"at": "L47", "name": "prop", "which": "coat", "on": True},
    {"at": "L48", "name": "prop", "which": "coat", "on": False},
    # the power dips (slow ramps: down 1.2 s, hold 0.8 s, up 1.2 s; never dark)
    {"at": "L37", "name": "dip", "down": 1.2, "hold": 0.8, "up": 1.2, "depth": 0.6},
    {"at": "L40", "name": "dip", "down": 1.2, "hold": 0.0, "hold_to": "L41", "up": 1.2, "depth": 0.6},
]

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L12", "kind": "sting", "db": -16},
    {"at": "L37", "kind": "hum_sweep", "db": -20},
    {"at": "L40", "kind": "hum_sweep", "db": -20},
    {"at": "L41", "kind": "hit", "db": -6},
    {"at": "L42", "kind": "knock", "pattern": [0.0], "tone": "soft", "db": -12},
    {"at": "L45", "kind": "sting", "db": -14},
    {"at": "L47", "kind": "door", "db": -12},
    {"at": "L68", "kind": "thud", "db": -22},
    {"at": "L76>-0.55", "kind": "knock", "pattern": [0.0], "tone": "soft", "db": -10},
    {"at": "L76>-0.5", "kind": "glide", "db": -16, "dur": 0.8},
]

story = {
    "slug": "ep32-sitter",
    "title": "The sitter in my art class had pencil lines for a face",
    "made_for_kids": False,
    "premise": "I'm an adult who paints in secret. I join a Wednesday evening portrait class without telling Mum, who always said I never finish a face. The sitter on the dais is made of raw pine, with pencil guide lines where its face should be. Every week its face copies the line I stopped on in my own half-done portrait, and every week it sits one easel nearer.",
    "twist": "The sitter's stool has been empty since spring and everyone else paints the bowl of fruit. A class built for eight painters and a sitter keeps its count of nine, so the Unpainted sat in. A sitter with no face isn't really there, and I was the only one painting it. Every face I gave up on was its face, and it came nearer so I could see it better. When I finish it, the stool is empty and the cushion on the dais has a dent at last, and Mum asks if the class needs a sitter.",
    "world": "a community arts centre life room on a rainy Wednesday evening: cream plaster walls, honey floorboards, eight easels with clamp lamps in a curve round a low pine dais with a stool and a green cushion, a rainy north window",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#4cc3f0",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#1b2230", "fog_density": 0.012, "fog_start": 9.0, "sky": "#0c1018", "sky_strength": 1.0, "exposure": 0.6},
    "grade": {"shadows": [-0.02, 0.0, 0.05], "highlights": [0.03, 0.01, -0.02], "saturation": 0.95, "contrast": 1.08,
              "vignette": 0.34, "bloom": 0.25, "grain": 0.012},
    "rain_shots": rain_shots,
    "phonemes": {"dais": "dˈAᵻs", "Kofi": "kˈOfi"},
    "geom": {"RE": RE, "RP": RP, "TH": TH},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 45, "mode": "minor", "bpm": 68, "seed": 32,
              "sections": [
                  {"at": 0, "voices": ["pad", "pulse"], "energy": 0.35},
                  {"at": "L05", "voices": ["drone", "pad", "pulse"], "energy": 0.4},
                  {"at": "L20", "voices": ["drone", "pad", "pulse"], "energy": 0.42},
                  {"at": "L26", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L31", "voices": ["drone", "pad", "choir"], "energy": 0.4},
                  {"at": "L36", "voices": ["drone", "choir"], "energy": 0.35},
                  {"at": "L41", "voices": ["drone", "pad", "choir"], "energy": 0.5},
                  {"at": "L48", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L56", "voices": ["drone", "pad", "choir"], "energy": 0.4},
                  {"at": "L62", "voices": ["pad", "piano"], "energy": 0.4, "mode": "major", "root": 45, "bpm": 76},
                  {"at": "L69", "voices": ["pad", "piano"], "energy": 0.45},
                  {"at": "L75", "voices": ["pad", "piano"], "energy": 0.4},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "end", "lufs": -34},
                  {"kind": "rain", "from": "L04", "to": "L05", "lufs": -30},
                  {"kind": "rain", "from": "L36", "to": "L47", "lufs": -30},
                  {"kind": "rain", "from": "L48", "to": "L62", "lufs": -30},
                  {"kind": "hum", "from": "L05", "to": "L62", "lufs": -42},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P41", "to": "L41"}, {"from": "L45-0.5", "to": "L45"}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
