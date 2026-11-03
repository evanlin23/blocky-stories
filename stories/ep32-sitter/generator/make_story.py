"""Writes ../story.json for ep32 "sitter": "Never Paint A PERSON In Here" (script.md, revival 2026-11-03).

Run from anywhere: python stories/ep32-sitter/generator/make_story.py
The words are in lines.json next to this file (made from the script by script_to_lines.py). Everything else is here:
the cast, the places, the shots and their cameras, the acting, the cues set.py reads, the score and the sound.
Places are set.py's (metres, floor z = 0). A character with yaw 0 faces -y; yaw 90 faces +x; yaw 180 faces +y.

The life room is centred on the dais at the origin. Easel i stands at angle TH[i] on a curve of radius RE, its canvas facing
out; its painter stands at radius RP behind it, facing the dais. The little sets are separate places in the same scene: the bus
stop (x 80), the cafe (x 120), the bakery (x 160), my bedroom (x -40) and Mom's hall (x 38 .. 42, y -1.5 .. 7.5).
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# ---------------------------------------------------------------------------------------------------- holds
HOLDS = {"L12": 0.3, "L19": 0.7, "L22": 0.8}          # id -> seconds after the line (the music drops live in these)
LOOP = 0.13                                # with the 0.12 s gap, 0.25 s after the last word
for ln in lines:
    if ln["id"] in HOLDS:
        ln["gap"] = HOLDS[ln["id"]]
TEMPO = {"L23": 0.92, "L13": 0.96}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]
lines = lines + [{"id": "PEND", "pause": LOOP, "chunks": []}]


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
theo = person("#c9966e", "#2f6b3e", "#2b2f3a", "swoop", "#5a3a22", collar="#efe6d4", extras=["coat"], shoes="#b8864f", height=1.08,
              zip_c="#cfd6cc")
theo["face"].update({"pupil": "#5a3a22"})

cast = {
    "me": person("#b57a56", "#d3a022", "#33363c", "buzz", "#14120f", pattern="knit", pattern_c="#bd8d19", shoes="#e8e8e6"),
    "mum": mum,
    "theo": theo,
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
    "walk1": person("#8e5a3e", "#d88a2c", "#2c3a52", "long", "#14100e", pattern="stripes", pattern_c="#a8661c"),
    "walk2": person("#f2d2b4", "#5b8a5b", "#3c3a40", "cap", "#7a5a3a", pattern="plaid", pattern_c="#3f6a3f"),
    "baker": person("#f0cfae", "#f4f0e6", "#4a4a52", "none", "#1a1410", extras=["apron"], extra_c="#f4f0e6", hat="beanie",
                    hat_c="#f4f0e6", sleeves="short"),
    "cust": person("#c68a5e", "#7a4fa0", "#33363c", "swoop", "#2a1d15", pattern="solid", eyes="dot"),
}
PAINTERS = {1: "bg6", 2: "bg1", 3: "bg2", 4: "bg3", 5: "bg4", 6: "bg5", 7: "petra", 8: "me"}
FADERS = {"theo": "theo"}

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


def z3(p, z):
    return [p[0], p[1], z]


def front(p, yaw, dist, z):
    """A point dist metres in front of a character at p facing yaw."""
    r = math.radians(yaw)
    return [round(p[0] + dist * math.sin(r), 3), round(p[1] - dist * math.cos(r), 3), z]


def face_cam(p, yaw, ang, dist, zc, lens, ztgt=None, push=0.0):
    """A camera dist metres from a character's face, swung ang degrees round from straight ahead; optionally pushing in."""
    zt = ztgt if ztgt is not None else zc
    a = front(p, yaw + ang, dist, zc)
    tg = z3(p, zt)
    if push:
        b = front(p, yaw + ang, dist - push, zc)
        return c([0, a, tg, lens], [1, b, tg, lens])
    return still(a, tg, lens)


def canvas_cam(i, dist, z=1.3, lens=30, push=0.0, side=0.0, cs=0.0, lens2=None):
    e = E(i)
    n = (math.cos(math.radians(TH[i - 1])), math.sin(math.radians(TH[i - 1])))
    t = (-n[1], n[0])
    tgt = [e[0] + t[0] * side, e[1] + t[1] * side, z]
    a = [tgt[0] + n[0] * dist + t[0] * cs, tgt[1] + n[1] * dist + t[1] * cs, z]
    b = [tgt[0] + n[0] * (dist - push) + t[0] * cs, tgt[1] + n[1] * (dist - push) + t[1] * cs, z]
    return c([0, a, tgt, lens], [1, b, tgt, lens2 or lens]) if (push or lens2) else still(a, tgt, lens)


DAIS = (0.0, 0.0)
ME, PETRA = PP(8), PP(7)
N8 = (math.cos(math.radians(TH[7])), math.sin(math.radians(TH[7])))
T8 = (-N8[1], N8[0])
Z_DAIS = 0.12                       # a seated root z on the dais stool (cushion on): top 0.57 + the cushion
Z_BENCH, Z_CHAIR, Z_BED = 0.0, -0.04, 0.05
MOMP = pol(RP, TH[7] + 13)          # where Mom paints, beside me
KOFI_SIDE = (round(ME[0] + T8[0] * 0.95, 3), round(ME[1] + T8[1] * 0.95, 3))

# the little sets
BUS = (80.0, 0.2)
BENCH = (80.1, 1.62)
CAF = (120.0, 1.5)
BAK = (160.9, -0.15)
BED = (-40.0, 0.0)
HX = 40.0
TABLE = (39.5, 2.0)
SEAT_MOM, SEAT_ME, SEAT_THEO = (39.5, 3.0), (38.75, 2.0), (40.25, 2.0)
DOOR = (37.9, 3.85)
CARME = (-1.2, -8.5)

# ---------------------------------------------------------------------------------------------------- shots
SH = []


def shot(sid, at, what, cam, **flags):
    SH.append((sid, at, what, cam, flags))


# 01 the rule: frame 1 is the half-pine face
shot("S01", 0, "frame 1: a pine panel on an easel, a face half painted, half bare pine and pencil", canvas_cam(7, 1.25, 1.3, 36, push=0.2),
     hand=0.002)
shot("S01b", "L01.2", "punch in on the line where paint stops and pine begins", canvas_cam(7, 0.7, 1.31, 40, push=0.12, side=-0.02), hand=0.002)
shot("S02", "L02", "a quick push to the empty pencil eye", canvas_cam(7, 0.62, 1.36, 42, push=0.15, side=0.11), hand=0.002)
shot("S03", "L03", "the life room: a panel with a painted green bench", canvas_cam(3, 1.7, 1.3, 30, push=0.3, side=0.05), hide_cast=["bg2"])
shot("S03b", "L03.3", "closer on the bench, the meter steps toward Thursday", canvas_cam(3, 1.0, 1.25, 36, push=0.2, side=-0.08))
shot("S04", "L04", "the sunny bus stop: the new bench, raw pine with pencil lines, Mr Dobbs sitting on it anyway",
     c([0, [78.9, -3.2, 1.4], [80.15, 1.6, 0.7], 30], [1, [79.6, -2.7, 1.3], [80.15, 1.6, 0.7], 30]))
shot("S04b", "L04.2", "close on a pencil line along a slat",
     c([0, [82.6, -1.6, 0.9], [80.1, 1.6, 0.5], 34], [1, [82.2, -1.3, 0.85], [80.1, 1.6, 0.5], 34]))
shot("S05", "L04.3", "the bench ramps from pine to bright green, Mr Dobbs looking down at it, pleased",
     c([0, [79.1, -2.6, 1.0], [80.1, 1.6, 0.65], 32], [1, [79.7, -2.2, 0.9], [80.1, 1.6, 0.65], 32]))
shot("S05b", "L05.1", "the bakery window: a cake whose pink frosting is still filling in up one side, the baker and a customer staring",
     c([0, [BAK[0] - 0.1, -1.5, 1.4], [BAK[0] + 0.1, 0.9, 1.3], 26], [1, [BAK[0] + 0.3, -1.3, 1.4], [BAK[0] + 0.2, 0.9, 1.3], 28]))
shot("S06", "L06", "the cafe window flower box: red flowers on the left, pencil on bare pine on the right",
     c([0, [CAF[0] - 0.9, -0.3, 1.4], [CAF[0] - 0.1, 2.85, 1.3], 30], [1, [CAF[0] - 0.4, 0.0, 1.4], [CAF[0] + 0.3, 2.85, 1.3], 36]))
shot("S06b", "L06.3", "punch in on the pencil half", c([0, [CAF[0] + 0.2, 0.8, 1.35], [CAF[0] + 0.7, 2.85, 1.3], 40],
                                                      [1, [CAF[0] + 0.5, 1.2, 1.35], [CAF[0] + 0.9, 2.85, 1.3], 46]))
shot("S06c", "L06.5", "a blank pine panel on an easel with only a pencil cross for a face", canvas_cam(2, 1.5, 1.3, 32, push=0.3), hide_cast=["bg1"])
# S07: me at the cafe window, the ear patch toward the camera
ME_CAF = (CAF[0] + 0.1, 2.15)
shot("S07", "L07", "me at the cafe window, in profile", face_cam(ME_CAF, 180, 95, 1.1, 1.62, 34, 1.55, push=0.1), hand=0.003)
shot("S07b", "L07.3", "a close on the side of my head: the ear patch, raw pine with one faint curve", face_cam(ME_CAF, 180, 90, 0.8, 1.62, 36, 1.58, push=0.1),
     hand=0.002)
# 02 the want
M1, M2 = (39.25, -0.2), (40.0, -0.2)
shot("S08", "L08", "Mom's front hall, bright: Mom smiling at me, a hand on my shoulder", c([0, [39.2, 1.6, 1.5], [39.62, -0.2, 1.45], 26],
                                                                                          [1, [39.5, 1.3, 1.5], [39.62, -0.2, 1.45], 26]))
shot("S08b", "L08.2", "Mom's smile, close", face_cam(M2, -90, -50, 1.7, 1.52, 32, 1.5, push=0.15))
shot("S09", "L08.4", "the wider hall: Mom's folded easel against the wall behind us, a panel turned to it",
     c([0, [41.7, -1.0, 1.7], [38.7, -0.3, 1.1], 22], [1, [41.7, -0.7, 1.65], [38.7, -0.3, 1.1], 22]))
shot("S10", "L09", "me on the arts centre steps in sun, a pine panel under my arm", still([-8.9, -5.0, 1.55], [-6.1, -3.0, 1.15], 28))
shot("S10b", "L09.1", "the life room: Kofi waving me in toward easel 8",
     c([0, [-1.0, -4.4, 1.6], [-3.9, -2.7, 1.4], 24], [1, [-1.4, -4.0, 1.6], [-3.9, -2.7, 1.4], 24]))
KP = KOFI_SIDE
shot("S11", "L10", "Kofi beside me, looking down at my hand, a small puzzled smile", face_cam(KP, yaw_to(KP, ME), -40, 2.0, 1.6, 32, 1.52, push=0.2))
shot("S11b", "L10.2", "the brush tip on the panel, no hand in frame", canvas_cam(8, 0.75, 1.2, 40, push=0.1, side=-0.12), hide_cast=["me", "kofi"])
shot("S12", "L11", "over a painter's shoulder, a bus-stop panel", canvas_cam(5, 1.5, 1.3, 30, push=0.2), hide_cast=["bg4"])
shot("S12b", "L11.3", "my panel: a young man's figure in pencil, colour going in", canvas_cam(8, 1.1, 1.3, 34, push=0.2), hide_cast=["me", "kofi"])
shot("S13", "L12", "my panel close: Theo's grin and brown eyes, his face centre bare pine", canvas_cam(8, 0.8, 1.38, 38, push=0.15, side=0.0),
     hide_cast=["me", "kofi"])
shot("S13b", "L12.2", "me, proud, the ear patch in frame", face_cam(ME, yaw_to(ME, DAIS), 90, 1.2, 1.6, 32, 1.56, push=0.1), hide_cast=["kofi"])
shot("S14a", "L13", "my panel: a pine square with a pencil nose outline where the nose should be", canvas_cam(8, 0.62, 1.32, 46, push=0.1, side=0.0),
     hide_cast=["me", "kofi"])
shot("S14", "L13.3", "Kofi at the door with his keys, waving me out, the lamps ramping down behind him",
     c([0, [-1.4, -2.0, 1.55], [-4.9, -2.85, 1.4], 24], [1, [-1.9, -2.2, 1.55], [-4.9, -2.85, 1.4], 24]))
shot("S15", "L14", "the car park at dusk under the lamp post, me looking back", still([-5.0, -12.0, 1.0], [-1.4, -8.4, 1.1], 28))
shot("S15b", "L14.2", "through the lit window, my panel on easel 8, Theo's painted eyes turned to the glass",
     c([0, [0.6, -9.0, 1.5], [3.0, -0.5, 1.2], 38], [1, [1.0, -8.0, 1.5], [3.0, -0.5, 1.25], 46]), turn8=True)
# 03 Tuesday to Thursday: Mom's hall at night
shot("S16", "L15", "Mom's hall at night, one wall lamp: pine Theo at the far end by the stairs, facing my door",
     c([0, [38.35, 3.4, 1.5], [40.5, 6.6, 1.2], 28], [1, [38.5, 3.6, 1.5], [40.5, 6.6, 1.2], 30]), hand=0.01)
shot("S16b", "L15.2", "me in my doorway, frozen", face_cam((38.35, 3.85), 90, 70, 2.2, 1.6, 30, 1.5, push=0.2), hand=0.008)
shot("S17", "L16", "close on his face: the cross and two empty ovals, no nose",
     face_cam((40.4, 6.2), yaw_to((40.4, 6.2), DOOR), 15, 2.4, 1.78, 40, 1.8, push=0.4), hand=0.004)
shot("S18", "L17", "low from my doorway: pine Theo halfway down the hall, boots to chest in colour",
     c([0, [38.35, 3.3, 0.55], [39.2, 4.7, 0.9], 28], [1, [38.4, 3.45, 0.5], [39.1, 4.4, 1.0], 28]), hand=0.01)
shot("S18b", "L17.4", "his feet one board from my threshold", c([0, [38.8, 3.25, 0.35], [39.0, 3.9, 0.1], 36], [1, [38.7, 3.35, 0.3], [38.95, 3.9, 0.12], 36]), hand=0.006)
# Thursday morning: my room
shot("S19", "L18", "bright morning, from my pillow: Theo at the foot of my bed, full colour",
     c([0, [BED[0] - 0.05, 0.85, 1.2], [BED[0], -1.45, 1.3], 24], [1, [BED[0], 0.65, 1.2], [BED[0], -1.45, 1.3], 24]), hand=0.004)
shot("S19b", "L18.2", "me sitting up fast, the ear patch toward the camera", face_cam((BED[0], 0.45), 0, 90, 1.4, 1.3, 30, 1.2, push=0.2))
shot("S20", "L19", "close on Theo's face: warm skin, brown eyes, the pine nose patch with its pencil outline",
     face_cam((BED[0], -1.45), 180, 25, 1.9, 1.72, 36, 1.7, push=0.25))
shot("S21", "L20", "the room as the music drops: Theo beside the bed, starting to lean", c([0, [BED[0] - 1.3, -1.6, 1.5], [BED[0] + 0.4, 0.1, 1.0], 26],
                                                                                          [1, [BED[0] - 1.1, -1.4, 1.5], [BED[0] + 0.4, 0.1, 1.0], 26]))
TH_BED = (BED[0] + 1.6, 0.3)
shot("S22", "L20.2", "3/4: Theo leaning in from the waist, his face a hand from mine, grinning. Never touches",
     c([0, [BED[0] + 0.5, -0.9, 1.6], [BED[0] + 0.55, 0.3, 1.55], 24], [1, [BED[0] + 0.45, -0.75, 1.6], [BED[0] + 0.55, 0.3, 1.55], 26]), hand=0.004)
shot("S22b", "L21", "me, eyes going to the door", face_cam((BED[0], 0.45), 0, 40, 1.9, 1.42, 32, 1.35, push=0.2))
# 04 dinner
shot("S23", "L22", "Mom's hall, warm evening: Mom at the table, Theo coming down the stairs",
     c([0, [39.0, 0.1, 1.5], [40.7, 4.6, 1.3], 24], [1, [39.2, 0.2, 1.5], [40.9, 4.3, 1.2], 24]))
shot("S23b", "L22.3", "Theo in the third chair", c([0, [39.4, 0.2, 1.45], [40.25, 2.1, 1.5], 26], [1, [39.6, 0.5, 1.45], [40.2, 2.1, 1.55], 28]))
shot("S24", "L23", "Mom calmly laying a third plate in front of Theo", c([0, [39.3, 0.6, 1.5], [39.9, 2.4, 1.1], 24], [1, [39.5, 0.8, 1.45], [39.9, 2.4, 1.1], 24]))
shot("S24b", "L23.2", "me, stunned", face_cam(SEAT_ME, 90, -45, 1.8, 1.45, 30, 1.45, push=0.15))
PICM, PICY = (39.55, 0.12), (39.55, -0.45)
shot("S25", "L24", "THE PICTURE: Mom's fingertip on the ear patch, her face close and kind, her folded easel behind us",
     c([0, [41.4, -0.2, 1.62], [39.55, -0.17, 1.58], 30], [1, [41.1, -0.2, 1.62], [39.55, -0.17, 1.58], 32]), hand=0.002)
shot("S26", "L25", "the life room, a wide of the eight easels in afternoon light, nobody there",
     c([0, [-4.6, -3.6, 1.7], [1.5, 0.4, 1.3], 22], [1, [-4.2, -3.2, 1.7], [1.5, 0.4, 1.3], 22]))
shot("S26b", "L25.2", "Kofi's glasses catching the lamp", face_cam((0.6, -1.8), 20, 55, 1.9, 1.6, 34, 1.55, push=0.2))
shot("S27", "L26", "Mom across the table, a small guilty smile", face_cam(SEAT_MOM, 0, 28, 1.8, 1.5, 32, 1.45, push=0.15))
shot("S27b", "L26.2", "me, the ear patch in frame, getting it", face_cam(SEAT_ME, 90, -75, 1.7, 1.42, 30, 1.45, push=0.15))
shot("S28", "L27", "Mom's old folded easel in the hall, close, paint-worn",
     c([0, [39.2, -0.1, 1.1], [37.95, -0.4, 0.95], 34], [1, [39.0, -0.2, 1.1], [37.95, -0.4, 0.95], 34]))
shot("S29", "L28", "Mom looking at me like she's still scared to change a line", face_cam(SEAT_MOM, 0, -30, 1.8, 1.5, 32, 1.46, push=0.15))
shot("S29b", "L28.3", "the old panel, turned to the wall", c([0, [39.1, -0.3, 0.9], [37.95, -1.05, 0.45], 34], [1, [39.0, -0.5, 0.8], [37.95, -1.05, 0.45], 34]))
shot("S30", "L29", "Theo, grinning, a hand out, Mom sliding the salt to him", c([0, [39.2, 0.9, 1.5], [40.1, 2.2, 1.35], 28], [1, [39.4, 1.0, 1.5], [40.0, 2.2, 1.35], 28]))
# 05 finishing
shot("S31", "L30", "Mom and me in her hall, the old easel being unfolded, cut before hands meet it",
     c([0, [40.6, -0.9, 1.5], [38.75, -0.2, 1.1], 24], [1, [40.3, -0.7, 1.5], [38.75, -0.2, 1.1], 24]))
shot("S32", "L31", "the life room, bright: Theo on the dais stool as my sitter, the nine strokes on the dais edge under his boots",
     c([0, [0.35, -2.9, 0.55], [0.0, -0.4, 0.9], 24], [1, [0.35, -2.6, 0.7], [0.0, -0.4, 1.15], 24]), tally=True, hand=0.002)
shot("S32b", "L31.3", "me at easel 8, side on, steady", c([0, [4.7, -2.1, 1.55], [3.7, -0.7, 1.4], 28], [1, [4.4, -2.0, 1.55], [3.7, -0.7, 1.4], 28]))
shot("S33", "L32", "Mom at the easel beside mine, her old panel back to camera, her face just over its top edge",
     c([0, [1.3, 1.0, 1.65], [MOMP[0], MOMP[1], 1.45], 28], [1, [1.5, 0.9, 1.6], [MOMP[0], MOMP[1], 1.45], 30]))
shot("S33b", "L32.3", "close on my head: the pine patch warming to skin", face_cam(ME, yaw_to(ME, DAIS), 90, 1.0, 1.6, 36, 1.58, push=0.15),
     hand=0.002)
shot("S34", "L33", "Kofi behind us, arms folded, smiling", face_cam((4.5, 0.0), 180, 40, 2.2, 1.6, 30, 1.55, push=0.2), hide_cast=["bg6"])
shot("S34b", "L33.2", "two-shot, Mom and me at our easels, Theo grinning on the dais", c([0, [1.2, -0.2, 1.7], [3.3, 0.2, 1.4], 24],
                                                                                        [1, [1.4, -0.4, 1.7], [3.3, 0.2, 1.4], 24]))
# 06 the new student
shot("S35", "L34", "the life room, colder: Petra at easel 7 turning her panel to the wall, glancing around",
     c([0, [1.6, 1.6, 1.7], [PETRA[0], PETRA[1], 1.35], 28], [1, [1.9, 1.5, 1.7], [PETRA[0], PETRA[1], 1.35], 28]))
shot("S36", "L35", "from behind easel 7, the panel's front: a face half painted, half bare pine and pencil", canvas_cam(7, 1.25, 1.3, 36, push=0.2),
     hand=0.002, hide_cast=["petra"])
P7S = (round(PETRA[0] - 0.25 * T8[0] * 0, 3), PETRA[1])
shot("S37", "L36", "me at Petra's shoulder, kind, about to speak", c([0, [2.2, -2.2, 1.7], [PETRA[0] + 0.1, PETRA[1] - 0.2, 1.5], 28],
                                                                    [1, [2.5, -2.0, 1.7], [PETRA[0] + 0.1, PETRA[1] - 0.2, 1.5], 30]))

CANVAS = {"S01", "S01b", "S02", "S03", "S03b", "S06c", "S11b", "S12", "S12b", "S13", "S14a", "S36"}
WIDE = {"S04": 1.2, "S04b": 1.0, "S05": 1.2, "S05b": 1.4, "S06": 1.3, "S06b": 1.3}


def clampp(p, tgt):
    x, y, z = p
    if 37 < tgt[0] < 43:
        x, y = min(41.9, max(38.05, x)), min(7.4, max(-1.4, y))
    elif tgt[0] < -38:
        x, y = min(-38.2, max(-41.8, x)), min(1.7, max(-1.8, y))
    elif 116 < tgt[0] < 124:
        x, y = min(122.8, max(117.2, x)), min(2.8, max(-1.9, y))
    elif 156 < tgt[0] < 165:
        x, y = min(163.2, max(157.8, x)), min(2.8, max(-1.9, y))
    elif abs(tgt[0]) < 5.4 and -5 < tgt[1] < 5:
        x, y = min(5.3, max(-5.3, x)), min(4.8, max(-5.0, y))
    return [round(x, 3), round(y, 3), z]


def widen(sid, cam):
    k = 1.0 if sid in CANVAS else WIDE.get(sid, 2.3)
    if sid in ("S10", "S15", "S15b"):
        return cam
    out = []
    for kk in cam:
        loc, tgt = kk[1], kk[2]
        nl = [tgt[0] + (loc[0] - tgt[0]) * k, tgt[1] + (loc[1] - tgt[1]) * k, tgt[2] + (loc[2] - tgt[2]) * k]
        out.append([kk[0], clampp(nl, tgt), tgt] + kk[3:])
    return out


SH = [(a, b, c_, widen(a, d), e) for a, b, c_, d, e in SH]
shots = []
for i, (sid, at, what, cam, fl) in enumerate(SH):
    s = {"id": sid, "cam": cam, "hand": fl.get("hand", 0.006), "step": 2, "what": what}
    s.update({k: v for k, v in fl.items() if k in ("noceil", "hide_easels", "hide_cast", "fill", "ev", "turn8", "tally", "unp_gain", "noear")})
    if i:
        s["at"] = at
    shots.append(s)

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
SIT = {"sit": True, "arms": [24, 24], "side": [0, 0], "lean": 0, "bendto": [0, 0, 0]}
STAND = {"sit": False, "bendto": [0, 0, 0]}
for who in acting:
    hide(who, 0)

# the painters: at their easels from the class on, gone for the empty-room wide, back for Monday
for i, who in PAINTERS.items():
    if who == "me":
        continue
    p = PP(i)
    put(who, "L09.1", p, yaw=yaw_to(p, DAIS), **PAINT)
    hide(who, "L25")
    put(who, "L31", p, yaw=yaw_to(p, DAIS), **PAINT)
    if who == "petra":
        key(who, "L34", expr="wide", blend=0.3, arms=[0, 40], head=[-30, 0])
        key(who, "L34.2", head=[40, 0], blend=0.4)
        key(who, "L35", arms=[10, 62], head=[0, 8], blend=0.4)
        key(who, "L36", expr="smile", blend=0.4)

# the montage people
put("ade", "L04", (BENCH[0] - 0.2, BENCH[1] + 0.12, Z_BENCH), yaw=0, expr="worried", head=[0, 6], **SIT)
key("ade", "L05", expr="smile", head=[0, 24], blend=0.5)
hide("ade", "L06")
put("walk1", "L04", (78.0, 0.2), yaw=90, expr="neutral", arms=[0, 0])
walk("walk1", "L05", (83.6, 0.2))
hide("walk1", "L05.1")
put("walk2", "L04.2", (83.6, 0.5), yaw=-90, expr="neutral", arms=[0, 0])
walk("walk2", "L05", (78.2, 0.5))
hide("walk2", "L05.1")
put("baker", "L05.1", (BAK[0] + 0.8, 1.75), yaw=-20, expr="wide", arms=[0, 0], head=[20, 0])
hide("baker", "L06")
put("cust", "L05.1", (BAK[0] - 0.55, -0.05), yaw=yaw_to((BAK[0] - 0.55, -0.05), (BAK[0] + 0.15, 0.9)), expr="wide", arms=[0, 0])
key("cust", "L05.1+0.8", expr="scared", blend=0.3)
hide("cust", "L06")

# me
key("me", "L07", hidden=True)
put("me", "L07", ME_CAF, yaw=180, expr="worried", arms=[0, 0], head=[0, 0])
hide("me", "L08")
put("me", "L08", M1, yaw=90, expr="smile", arms=[0, 0], head=[0, 0])
hide("me", "L09")
put("me", "L09", (-5.9, -3.0), yaw=90, expr="worried", arms=[0, 0])
hide("me", "L09.1")
put("me", "L09.1", (-4.9, -2.9), yaw=80, expr="worried", arms=[0, 0])
walk("me", "L09.2+0.5", (-4.0, -2.9))
put("me", "L10", ME, yaw=yaw_to(ME, DAIS), expr="worried", **PAINT)
key("me", "L11", expr="soft", blend=0.3)
key("me", "L12", expr="smile", blend=0.3)
key("me", "L12.2", expr="grin", blend=0.3)
key("me", "L13", expr="soft", blend=0.3)
put("me", "L13.3", (-3.0, -2.5), yaw=-90, expr="soft", arms=[0, 0])
walk("me", "L13.3+0.9", (-3.9, -2.5))
put("me", "L14", CARME, yaw=180, expr="worried", arms=[0, 0])
key("me", "L14.2", expr="scared", blend=0.4)
hide("me", "L15")
put("me", "L15.2", (38.45, 3.85), yaw=yaw_to((38.45, 3.85), (40.4, 6.2)), expr="scared", arms=[0, 0], head=[0, 0])
hide("me", "L17")
put("me", "L18.2", (BED[0], 0.45, Z_BED), yaw=0, expr="scared", **SIT)
key("me", "L18.2", head=[0, 0])
key("me", "L19", expr="wide", blend=0.2)
key("me", "L21", expr="scared", head=[-40, 0], blend=0.3)
put("me", "L22", (SEAT_ME[0], SEAT_ME[1], Z_CHAIR), yaw=90, expr="worried", **SIT)
key("me", "L23.2", expr="wide", blend=0.2)
put("me", "L24", (PICM[0], PICM[1]), yaw=0, expr="soft", arms=[0, 0], head=[0, 0], **STAND)
put("me", "L26", (SEAT_ME[0], SEAT_ME[1], Z_CHAIR), yaw=90, expr="soft", **SIT)
key("me", "L26.2", expr="wide", blend=0.3)
key("me", "L28", expr="soft", blend=0.4)
put("me", "L30", (38.9, 0.35), yaw=-90, expr="soft", arms=[0, 0], **STAND)
put("me", "L31", ME, yaw=yaw_to(ME, DAIS), expr="soft", **PAINT, **STAND)
key("me", "L31.3", expr="neutral", arms=[10, 78], blend=0.5)
key("me", "L32.3", expr="smile", blend=0.5)
put("me", "L36", (PETRA[0] + T8[0] * 0.0 + 0.3, PETRA[1] - 0.85), yaw=yaw_to((PETRA[0] + 0.3, PETRA[1] - 0.85), PETRA), expr="smile", arms=[0, 0], **STAND)

# Mom
put("mum", "L08", M2, yaw=-90, expr="smile", arms=[0, 82])
key("mum", "L08.2", expr="smile")
hide("mum", "L09")
put("mum", "L22", (SEAT_MOM[0], SEAT_MOM[1], Z_CHAIR + 0.02), yaw=0, expr="soft", **SIT)
key("mum", "L23.1", arms=[0, 60], expr="soft", blend=0.4)
key("mum", "L23.2+0.9", arms=[24, 24], blend=0.5)
put("mum", "L24", (PICY[0], PICY[1]), yaw=180, expr="soft", arms=[0, 78], head=[0, 0], **STAND)
key("mum", "L24.2", arms=[0, 82], expr="smile", blend=0.4)
put("mum", "L26", (SEAT_MOM[0], SEAT_MOM[1], Z_CHAIR + 0.02), yaw=0, expr="worried", **SIT)
key("mum", "L28", expr="soft", blend=0.4)
key("mum", "L29", arms=[0, 50], expr="smile", blend=0.4)
put("mum", "L30", (38.85, -0.65), yaw=-90, expr="soft", arms=[0, 0], **STAND)
key("mum", "L30.2", arms=[0, 40], blend=0.5)
put("mum", "L32", (MOMP[0], MOMP[1]), yaw=yaw_to(MOMP, DAIS), expr="soft", **PAINT, **STAND)
key("mum", "L32.3", arms=[10, 75], blend=0.5)
key("mum", "L33.2", expr="smile", blend=0.5)
hide("mum", "L34")

# Theo: pine at night, the colour climbing him from the boots, then himself
TFAR = (40.35, 6.3)
put("theo", "L15", TFAR, yaw=yaw_to(TFAR, DOOR), expr="blank", fade=1.0, fade_h=1.0, fade_z=-5.0, stage=0, arms=[0, 0])
THALF = (38.95, 4.55)
put("theo", "L17", THALF, yaw=yaw_to(THALF, DOOR), expr="blank", fade=1.0, fade_h=1.0, fade_z=1.3, stage=0, arms=[0, 0])
put("theo", "L18", (BED[0], -1.5), yaw=180, expr="grin", fade=0.0, fade_h=0.0, fade_z=9.0, arms=[0, 0])
put("theo", "L20", (TH_BED[0], TH_BED[1]), yaw=-90, expr="grin", fade=0.0, fade_h=0.0, fade_z=9.0, arms=[0, 0], bendto=[BED[0], 0.35, 0])
key("theo", "L20.1", bendto=[BED[0], 0.35, 38], blend=0.9)
put("theo", "L22", (41.55, 5.7, 1.1), yaw=0, expr="grin", fade=0.0, fade_h=0.0, fade_z=9.0, arms=[0, 0], bendto=[0, 0, 0])
walk("theo", "L22.2", (41.55, 3.7, 0.0))
put("theo", "L22.3", (SEAT_THEO[0], SEAT_THEO[1], Z_CHAIR - 0.04), yaw=-90, expr="grin", fade=0.0, fade_h=0.0, fade_z=9.0, **SIT)
key("theo", "L29", arms=[0, 70], blend=0.4)
key("theo", "L29>", arms=[0, 0], blend=0.4)
put("theo", "L31", (0.0, 0.0, Z_DAIS), yaw=yaw_to((0.0, 0.0), ME), expr="grin", fade=0.0, fade_h=0.0, fade_z=9.0, **SIT)
key("theo", "L33.2", expr="grin")
hide("theo", "L34")

# Kofi
put("kofi", "L09.1", (-3.0, -2.6), yaw=-90, arms=[0, 70], expr="smile")
key("kofi", "L09.2", arms=[0, 20], blend=0.3)
put("kofi", "L10", (KP[0], KP[1]), yaw=yaw_to(KP, ME), expr="soft", arms=[0, 0], head=[0, 28])
hide("kofi", "L13.2")
put("kofi", "L13.3", (-5.0, -2.9), yaw=-90, expr="smile", arms=[0, 78])
key("kofi", "L13.5", arms=[0, 30], blend=0.5)
hide("kofi", "L14")
put("kofi", "L25.2", (0.6, -1.8), yaw=200, expr="soft", arms=[0, 0])
hide("kofi", "L26")
put("kofi", "L33", (4.5, 0.0), yaw=yaw_to((4.5, 0.0), DAIS), expr="smile", arms=[40, 40], head=[0, 0])
hide("kofi", "L34")

# ---------------------------------------------------------------------------------------------------- cues
cues = [
    {"at": 0, "name": "time", "set": "warm"},
    {"at": "L04", "name": "time", "set": "bus"},
    {"at": "L05.1", "name": "time", "set": "bake"},
    {"at": "L06", "name": "time", "set": "cafe"},
    {"at": "L06.5", "name": "time", "set": "warm"},
    {"at": "L07", "name": "time", "set": "cafe"},
    {"at": "L08", "name": "time", "set": "hall"},
    {"at": "L09", "name": "time", "set": "day"},
    {"at": "L09.1", "name": "time", "set": "warm"},
    {"at": "L13.3", "name": "time", "set": "dusk"},
    {"at": "L15", "name": "time", "set": "hallnight"},
    {"at": "L18", "name": "time", "set": "bed"},
    {"at": "L22", "name": "time", "set": "halleve"},
    {"at": "L25", "name": "time", "set": "warm"},
    {"at": "L26", "name": "time", "set": "halleve"},
    {"at": "L30", "name": "time", "set": "hall"},
    {"at": "L31", "name": "time", "set": "warm"},
    {"at": "L34", "name": "time", "set": "cold"},
    # the week meter: today's square (Monday = 0)
    {"at": 0, "name": "day", "d": 0},
    {"at": "L04", "name": "day", "d": 1},
    {"at": "L05", "name": "day", "d": 3},
    {"at": "L09", "name": "day", "d": 0},
    {"at": "L15", "name": "day", "d": 1},
    {"at": "L17", "name": "day", "d": 2},
    {"at": "L18", "name": "day", "d": 3},
    {"at": "L31", "name": "day", "d": 0},
    {"at": "L34", "name": "day", "d": 0},
    # easel pictures
    {"at": 0, "name": "easel", "i": 3, "img": "bench"},
    {"at": 0, "name": "easel", "i": 2, "img": "cross"},
    {"at": "L09", "name": "easel", "i": 2, "img": "town2"},
    {"at": "L09", "name": "easel", "i": 3, "img": "town3"},
    {"at": "L09", "name": "easel", "i": 5, "img": "bus"},
    {"at": "L09", "name": "easel", "i": 7, "img": "town5"},
    {"at": "L09", "name": "easel", "i": 8, "img": "blank"},
    {"at": "L11.3", "name": "easel", "i": 8, "img": "theo0"},
    {"at": "L12", "name": "easel", "i": 8, "img": "theo1"},
    {"at": "L31", "name": "easel", "i": 8, "img": "theo1"},
    {"at": "L35", "name": "easel", "i": 7, "img": "half"},
    # props
    {"at": 0, "name": "prop", "which": "canvas_carry", "on": False},
    {"at": "L09", "name": "prop", "which": "canvas_carry", "on": True},
    {"at": "L09.1", "name": "prop", "which": "canvas_carry", "on": False},
    {"at": "L10.2", "name": "prop", "which": "tipbrush", "on": True},
    {"at": "L11", "name": "prop", "which": "tipbrush", "on": False},
    {"at": "L23.1", "name": "prop", "which": "plate3", "on": True},
    {"at": "L32", "name": "prop", "which": "mom_easel", "on": True},
    # the lamps ramp from 100% to 35% over 1.2 s as Kofi locks up, and hold dim (never dark)
    {"at": "L13.3", "name": "dip", "down": 1.2, "hold": 0.0, "hold_to": "L15", "up": 0.4, "depth": 0.65},
    # colour fills: the bench (S05), the cake (S05b), Theo's nose and my ear (Monday)
    {"at": "L04.3+0.55", "name": "ramp", "name_": "bench", "v": 1.0, "dur": 0.95},
    {"at": "L05.1", "name": "ramp", "name_": "cake", "v": 0.1, "dur": 0.0},
    {"at": "L05.1+0.1", "name": "ramp", "name_": "cake", "v": 0.55, "dur": 1.6},
    {"at": "L31.1", "name": "ramp", "name_": "nose", "v": 1.0, "dur": 1.5},
    {"at": "L32.3", "name": "ramp", "name_": "ear", "v": 1.0, "dur": 1.5},
    # the nose is only a short ink stroke once it is finished: the pine patch hides after the ramp (set.py)
]

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L05.1+0.1", "kind": "chime", "db": -26},
    {"at": "L31.1", "kind": "chime", "db": -26},
    {"at": "L32.3", "kind": "chime", "db": -26},
    {"at": "L36>", "kind": "glide", "db": -18, "dur": 0.9},
]

story = {
    "slug": "ep32-sitter",
    "title": "Never Paint A PERSON In Here \U0001F58C️",
    "made_for_kids": False,
    "premise": "Kofi's art class paints new things into town, and each one turns up by Thursday, first as bare pine with the pencil lines still on it, then filling in with color. The one rule is never paint a person. I've always wanted a big brother, and Mom says one of me is plenty, so I join the class and paint him, Theo, but Kofi locks up for the night before I finish his nose, and anything missed on a painted person stays bare pine till their painter finishes it. By Tuesday a pine man with a pencil face stands in our hall, and each night he is a step nearer my door with more color on him.",
    "twist": "On Thursday Theo comes down to dinner in full color except a bare pine nose, and Mom calmly lays him a plate, because eighteen years ago she took Kofi's class and broke the rule herself: she painted me. The patch of bare pine I always called a birthmark is the ear she never dared finish, and the student Kofi said I hold a brush like was Mom. Only a painter can finish what they painted, so I finish Theo's nose and Mom finishes my ear at her old easel. The loop: a new student hides a half pine face, and I tell her never to paint a person.",
    "world": "a bright little town that Kofi's art class paints new things into, on pine panels: a sunny bus stop with a new bench, a bakery cake and a cafe flower box still filling in, the arts centre life room on Monday afternoons with eight easels round a pine dais, the car park at dusk, and Mom's front hall with her folded old easel and a small dining table",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#5fd068",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#bcd0e2", "fog_density": 0.006, "fog_start": 12.0, "sky": "#cfe3f5", "sky_strength": 1.0, "exposure": 0.55,
             "flash_safe": True,
             "polish": {"emph": ["L01.3", "L07.5", "L11.4", "L15.4", "L17.4", "L20.2", "L23.2", "L26.2", "L31.4"],
                        "reveal": ["L07.5", "L15.4", "L20.2", "L23.2"],
                        "twist": "L23",
                        "quiet": [["L24", "L25"]],
                        "hold": ["S25"],
                        "sway": ["S16", "S16b", "S17", "S18", "S18b"],
                        "bed_kind": "room"}},
    "grade": {"shadows": [-0.01, 0.0, 0.03], "highlights": [0.03, 0.015, -0.02], "saturation": 1.02, "contrast": 1.05,
              "vignette": 0.25, "bloom": 0.22, "grain": 0.01},
    "phonemes": {"Kofi": "kˈOfi"},
    "geom": {"RE": RE, "RP": RP, "TH": TH, "faders": FADERS},
    "clip_ok": ["meter"],
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 53, "mode": "major", "bpm": 96, "seed": 32,
              "sections": [
                  {"at": 0, "voices": ["pulse", "pad"], "energy": 0.34},
                  {"at": "L15", "voices": ["drone", "pad"], "energy": 0.42},
                  {"at": "L24", "voices": ["pad", "piano"], "energy": 0.4, "mode": "major", "root": 50, "bpm": 84},
                  {"at": "L34", "voices": ["drone"], "energy": 0.3, "mode": "minor", "root": 53, "bpm": 84},
              ]},
    "sound": {"rev": 1, "floor": "wood", "steps_db": -22,
              "ambience": [{"kind": "room", "from": 0, "to": "end", "lufs": -34}],
              "sfx": sfx,
              "music_drops": [{"from": "L20-0.6", "to": "L20"}, {"from": "L23-0.7", "to": "L23"}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
