"""Writes ../story.json for ep80 "Snow globe" (script.md, 2026-11-03, batch 7).

Run from anywhere: python stories/ep80-snow-globe/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads, the score and the sound. Places are set.py's (see its header).
A character with yaw 0 faces -y, 90 faces +x, -90 faces -x, 180 faces +y.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# captions show two or three words at a time (the house check): a longer chunk is split in two, and every chunk
# reference below is written for the script's own chunks, so it's remapped to the split ones with R()
IDX = {}
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
    ln["chunks"] = new
    IDX[ln["id"]] = m


def R(line, k=None, off=0.0):
    """A time reference to the script's chunk k of a line (after the split), plus an offset in seconds."""
    s = line if k is None else f"{line}.{IDX[line][k]}"
    if off:
        s += f"{off:+.2f}"
    return s



# ---------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True}


def mk(skin, shirt, pants="#2c2f3a", shoes="#3a2a20", hair="cap", hair_c="#2a1d15", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": shoes,
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "hat": "none", "face": dict(FACE)}
    d.update(kw)
    return d


cast = {
    # me: a teen boy, short black block hair under a mustard knit beanie, a teal hoodie with our snowflake-block patch
    "me": mk("#e0b08a", "#2a9d9a", "#2b2e3b", "#f2f2f2", "cap", "#15110f", age="teen", hat="beanie", hat_c="#e0a21c",
             collar="#238a87"),
    # gus: white block hair, a pine-green cardigan over cream, brown trousers (set.py adds the mustache and the flat cap)
    "gus": mk("#e8c3a0", "#2f7a4f", "#6a4a30", "#3a2a20", "cap", "#f2f2f0", collar="#f2e6c8", height=0.97,
              face={"eyes": "tired", "brows": True, "bags": True}),
    "ortiz": mk("#e8c8a8", "#c9a8ff", "#4a3a5a", "#3a2a20", "bun", "#b8b8b8", extras=["coat"], zip_c="#8a6fd0", height=0.95,
                face={"eyes": "lashes", "brows": True}),
    "mailman": mk("#d9a98a", "#22346e", "#1a2448", "#1a1a20", "cap", "#2a1d15", hat="ballcap", hat_c="#22346e", collar="#f2f2f2"),
    "examiner": mk("#f0ceac", "#8c929c", "#4a4e58", "#2a2a2e", "long", "#4a3022", extras=["coat"], zip_c="#5a6070",
                   face={"eyes": "lashes", "brows": True}),
    "n1": mk("#cf9c76", "#d96a4a", "#3c4a3e", "#3a2a20", "buzz", "#3a2a1e"),
    "n2": mk("#e0b898", "#4a7fd0", "#33363e", "#3a2a20", "spiky", "#6a4a2a"),
    "n3": mk("#b88460", "#8a9a3a", "#2e2e34", "#3a2a20", "long", "#1a1210", face={"eyes": "lashes", "brows": True}),
}
ALL = list(cast)


# ---------------------------------------------------------------------------------------------------- places
GX, GY = -10.25, 0.9            # the globe on the sill
GAUGE = 1.0 / 400.0


def MI(x, y, z=0.0):
    """A point in the tiny street (real metres inside the globe) in world coordinates."""
    return (GX + x * GAUGE, GY + y * GAUGE, 0.95 + 0.08 + z * GAUGE)


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return c([0, list(loc), list(tgt), lens])


def move(a, b, la, lb=None, roll=(0, 0)):
    return c([0, list(a[0]), list(a[1]), la, roll[0]], [1, list(b[0]), list(b[1]), lb or la, roll[1]])


def rollmove(a, lens, mid_roll):
    """The room tilts a few degrees and back (a 0.4 s ease each way)."""
    return c([0, list(a[0]), list(a[1]), lens, 0], [0.5, list(a[0]), list(a[1]), lens, mid_roll], [1, list(a[0]), list(a[1]), lens, 0])


def minicam(cam_off, tgt, lens, tgt_off=(0, 0, 0)):
    """A macro camera inside the globe: cam_off and tgt in tiny-street metres."""
    return still(MI(*cam_off), MI(tgt[0] + tgt_off[0], tgt[1] + tgt_off[1], tgt[2] + tgt_off[2]), lens)


def minimove(a, b, lens_a, lens_b=None):
    return move((MI(*a[0]), MI(*a[1])), (MI(*b[0]), MI(*b[1])), lens_a, lens_b)


MID = (0.0, 0.0)
SPOT_ORTIZ = (6.4, 0.3)
SPOT_MAIL = (-5.0, 0.2)
GCW = (GX, GY, 1.09)           # the dome's centre

# the globe, seen from inside the room, with the street behind it
G_FRONT = ((-11.1, 0.92, 1.28), (0.0, 0.0, 0.2))
SHOTS = []


def shot(at, note, cam, step=2, hand=0.006, **kw):
    SHOTS.append((at, note, cam, step, hand, kw))


# ---- 01 the hook: the globe, close, already wrong
shot(0, "S01 close-up of the globe on the sill, the street white behind with its bare spot",
     move(((-11.0, 0.9, 1.22), (-3.0, 0.0, 0.4)), ((-10.82, 0.9, 1.2), (-3.0, 0.0, 0.4)), 50), hand=0.0)
shot("L02", "S02 tighter on the tiny figure", minimove(((-5.0, -20.0, 6.0), (0.0, 0.0, 2.6)), ((-3.5, -15.0, 5.0), (0.0, 0.0, 2.6)), 36), hand=0.0)
# ---- 02 the rule at work: snow, stumbles, the dry spot
shot("L03", "S03 the globe swirling on the sill, no hand in frame", move(((-11.0, 0.5, 1.3), GCW), ((-10.8, 0.6, 1.25), GCW), 40), hand=0.0)
shot("L03.2", "S04 the real street snowing hard", move(((-4.4, -12.0, 1.9), (0.0, 8.0, 1.4)), ((-4.4, -10.0, 1.9), (0.0, 8.0, 1.4)), 28))
shot("L04", "S05 high wide: our street white and snowing, the corner dry and sunny",
     move(((-14.0, -30.0, 13.0), (0.0, 30.0, 2.0)), ((-12.0, -26.0, 12.0), (0.0, 30.0, 2.0)), 24), step=1)
shot("L04.2", "S06 the next street, sunny and dry", move(((-3.0, 22.0, 1.6), (0.0, 40.0, 1.3)), ((-2.0, 24.0, 1.6), (0.0, 40.0, 1.3)), 30))
shot("L05", "S07 three neighbours in a row wobble together", still((1.3, 9.0, 1.5), (-4.9, 9.0, 1.15), 25))
shot("L05.2", "S08 the man spills his mug", still((-1.0, 9.0, 1.5), (-4.9, 9.1, 1.2), 42))
shot("L05.3", "S09 the ground tips: the whole row, the camera rolls", rollmove(((1.3, 9.0, 1.5), (-4.9, 9.0, 1.15)), 25, 7))
shot("L06", "S10 the mailman drops his bag", still((0.2, -7.6, 1.5), (4.9, -6.6, 1.05), 30))
shot("L06.2", "S11 envelopes in the snow", still((3.0, -5.2, 1.0), (4.9, -6.6, 0.1), 38))
shot("L07", "S12 Mrs. Ortiz stumbles in her yard", still((3.2, 5.6, 1.6), (7.4, 3.0, 1.0), 30))
shot("L07.1", "S13 she sits right down in her flowerbed", still((4.0, 4.2, 1.1), (7.4, 2.4, 0.7), 34))
shot("L08", "S14 the snow stops: the street, empty and white", move(((-4.4, -5.0, 1.9), (0.0, 6.0, 0.8)), ((-4.0, -4.0, 1.9), (0.0, 6.0, 0.8)), 30))
shot("L08.2", "S15 top-down: one dry patch in the middle of the white road",
     move(((0.0, -0.06, 7.0), (0.0, 0.0, 0.0)), ((0.0, -0.06, 4.2), (0.0, 0.0, 0.0)), 28))
shot("L09", "S16 road level: the patch, cold steam coming off it", still((2.4, -2.0, 0.4), (0.0, 0.0, 0.3), 32))
shot("L09.2", "S17 about the size of a person", still((2.6, -3.0, 1.1), (0.7, 0.0, 0.7), 30))
shot("L10", "S18 a car swerves round it", still((-4.0, -7.0, 1.4), (0.6, -1.0, 0.8), 26))
shot("L10.2", "S19 the crosswalk painted in a curve", still((0.0, 25.0, 1.1), (0.0, 31.0, 0.1), 26))
# ---- 03 Grandpa, the globe, the figure
shot("L11", "S20 inside: Grandpa at the window, the globe on the sill, me in the doorway",
     move(((-14.6, -2.9, 1.7), (-11.0, 0.6, 1.2)), ((-14.2, -2.5, 1.7), (-11.0, 0.6, 1.2)), 24))
shot("L11.2", "S21 the globe on his windowsill", still((-11.4, -0.6, 1.45), (GX, GY, 1.05), 36))
shot("L12", "S22 inside it our whole street, looking up the road", minimove(((-1.0, -24.0, 5.0), (0.0, 8.0, 1.0)), ((-1.0, -18.0, 4.5), (0.0, 8.0, 1.0)), 30), hand=0.0)
shot("L12.2", "S23 down to the mailboxes", minimove(((-8.0, -6.0, 3.0), (-4.7, 0.9, 1.0)), ((-7.0, -4.0, 2.6), (-4.7, 0.9, 1.0)), 34), hand=0.0)
shot("L13", "S24 the middle of the tiny road", minicam((6.0, -14.0, 5.5), (0.0, 0.0, 2.2), 32), hand=0.0)
shot("L13.4", "S25 one tiny figure", minimove(((-2.0, -11.0, 3.4), (0.0, 0.0, 2.4)), ((-1.2, -7.5, 3.2), (0.0, 0.0, 2.6)), 36), hand=0.0)
shot("L14", "S26 my face through the curve of the glass", still((-10.9, 0.55, 1.55), (-12.6, 0.4, 1.55), 40))
shot("L14.2", "S27 a snowman", minimove(((4.0, -9.0, 4.0), (0.0, 0.0, 2.6)), ((2.6, -7.0, 3.6), (0.0, 0.0, 2.6)), 38), hand=0.0)
shot("L15", "S28 morning on the porch: Grandpa tips his cap to the empty road", still((-4.4, 3.0, 1.55), (-8.4, -0.4, 1.35), 30))
shot("L15.3", "S29 the empty middle of the road", move(((-3.2, -2.4, 1.0), (0.0, 0.0, 0.2)), ((-2.6, -2.0, 0.9), (0.0, 0.0, 0.2)), 30))
shot("L16", "S30 the pickup at the curb: me driving, Grandpa beside me", still((-6.6, 4.4, 1.55), (-3.4, 7.0, 1.3), 32))
shot("L16.2", "S31 the truck from the front", still((-3.3, 0.6, 1.5), (-3.4, 6.5, 1.3), 38))
shot("L17", "S32 my face at night, worried", still((-11.6, 0.2, 1.58), (-12.9, 0.4, 1.55), 42))
shot("L17.2", "S33 scared", still((-11.8, 0.0, 1.55), (-12.9, 0.4, 1.55), 52))
# ---- 04 the first shake
shot("L18", "S34 Grandpa's chair empty, the globe in the foreground", still((-12.6, -1.0, 1.35), (GX, GY, 1.05), 30))
shot("L18.2", "S35 me reaching (cut before contact)", still((-11.3, -0.9, 1.5), (-12.0, 0.55, 1.4), 36))
shot("L18.3", "S36 the globe swirling", move(((-11.2, 0.5, 1.35), GCW), ((-10.9, 0.6, 1.2), GCW), 44), hand=0.0)
shot("L19", "S37 the house lurches (the room tilts and back)", rollmove(((-13.8, -2.6, 1.7), (-10.5, 0.4, 1.3)), 24, 6))
shot("L20", "S38 it snows outside the window", move(((-12.5, 0.4, 1.5), (-5.0, 0.0, 1.5)), ((-11.8, 0.4, 1.5), (-5.0, 0.0, 1.5)), 26))
shot("L21", "S39 me grinning at my phone", still((-11.5, 0.1, 1.5), (-12.7, 0.5, 1.4), 40))
shot("L21.1", "S40 the phone: a snowflake and a cross", still((-12.2, 0.2, 1.4), (-12.75, 0.35, 1.35), 40), hand=0.0)
# ---- 05 the first scare: it moved
shot("L22", "S41 in the globe the middle of the road is empty", minimove(((5.0, -14.0, 5.0), (0.0, 0.0, 2.0)), ((3.8, -11.0, 4.5), (0.0, 0.0, 2.0)), 32), hand=0.0)
shot("L22.3", "S42 it has moved", minimove(((-1.0, -16.0, 6.0), (3.0, 0.0, 2.0)), ((0.0, -13.0, 5.0), (4.0, 0.0, 2.0)), 30), hand=0.0)
shot("L23.1", "S43 by Mrs. Ortiz's gate", minimove(((3.0, -9.0, 4.0), (5.4, 0.0, 2.5)), ((2.6, -7.0, 3.6), (5.4, 0.0, 2.5)), 36), hand=0.0)
shot("L24", "S44 morning: her whole yard is white", move(((1.5, -5.0, 2.4), (7.0, 1.0, 0.8)), ((1.9, -4.0, 2.2), (7.0, 1.0, 0.8)), 26))
shot("L25", "S45 except one dry spot", still((3.6, -2.4, 1.2), (6.3, 0.3, 0.3), 30))
shot("L25.2", "S46 right by the gate", move(((4.2, -1.4, 0.9), (6.2, 0.3, 0.2)), ((4.7, -0.9, 0.8), (6.2, 0.3, 0.2)), 36))
shot("L26", "S47 her curtains drawn", still((3.4, -3.4, 1.55), (10.0, -1.8, 1.55), 32))
shot("L27", "S48 her dog won't go near the gate", still((5.0, 2.8, 0.9), (8.6, 0.7, 0.35), 34))
# ---- 06 second shake
shot("L28", "S49 my phone: a new date", still((-12.2, 0.2, 1.4), (-12.75, 0.35, 1.35), 40), hand=0.0)
shot("L28.2", "S50 me, sheepish", still((-11.5, 0.2, 1.5), (-12.7, 0.5, 1.45), 42))
shot("L29", "S51 night: me at the window with the globe", still((-12.3, -0.6, 1.55), (-10.7, 0.8, 1.2), 30))
shot("L29.2", "S52 the globe swirling again", move(((-11.15, 0.55, 1.3), GCW), ((-10.85, 0.7, 1.22), GCW), 42), hand=0.0)
shot("L30", "S53 the figure ends up by our mailbox", minimove(((-1.0, -6.0, 3.6), (-4.7, 0.9, 2.0)), ((-2.0, -5.0, 3.2), (-4.7, 0.9, 2.0)), 36), hand=0.0)
shot("L30.3", "S54 our mailbox", minimove(((-0.5, -2.0, 3.0), (-4.7, 0.9, 1.6)), ((-1.5, -2.0, 2.8), (-4.7, 0.9, 1.6)), 36), hand=0.0)
shot("L31", "S55 the mailman comes up our path", move(((-1.0, -2.2, 1.6), (-5.2, 0.2, 1.1)), ((-1.0, -1.2, 1.6), (-5.2, 0.2, 1.1)), 30))
shot("L31.2", "S56 stops at the dry spot", still((-2.8, -1.4, 1.2), (-5.0, 0.2, 0.4), 36))
shot("L31.3", "S57 backs all the way down", still((-8.0, 3.4, 1.9), (-3.4, 0.2, 1.0), 26))
shot("L32", "S58 he leaves our mail at the gate", still((-3.6, -1.2, 1.0), (-5.6, 0.2, 0.1), 36))
shot("L32.2", "S59 in the snow", move(((-4.4, -0.6, 0.55), (-5.6, 0.2, 0.08)), ((-4.8, -0.4, 0.5), (-5.6, 0.2, 0.08)), 34))
shot("L33", "S60 Grandpa looks at the globe", still((-12.4, 1.8, 1.55), (-10.9, -1.2, 1.4), 34))
shot("L33.1", "S61 the globe on the sill", still((-11.5, 0.2, 1.3), (GX, GY, 1.05), 38))
shot("L34", "S62 dinner: Grandpa eats in silence", still((-12.3, -2.3, 1.45), (-14.2, -0.7, 1.2), 34))
shot("L34.2", "S63 me across, sheepish", still((-15.8, 1.9, 1.45), (-14.2, 0.8, 1.35), 34))
# ---- 07 the third shake, 2 a.m.
shot("L35", "S64 me awake in the dark front room", still((-16.0, -2.6, 1.35), (-13.0, 0.4, 1.2), 24), hand=0.01)
shot("L35.1", "S65 I couldn't sleep", still((-12.5, 0.6, 1.5), (-13.6, 0.7, 1.5), 40))
shot("L36", "S66 two a.m.: the globe, a pale glow by the window", still((-13.8, 2.6, 1.4), (-10.3, 0.9, 1.1), 30))
shot("L36.1", "S67 I picked up the globe", still((-12.7, 0.0, 1.5), (-11.3, 0.9, 1.25), 34))
shot("L36.3", "S68 just to look", still((-11.9, 1.4, 1.5), (-12.5, 0.6, 1.5), 40))
shot("L37", "S69 it slips", move(((-12.4, 0.2, 1.7), (-11.3, 0.9, 1.0)), ((-12.2, 0.2, 1.6), (-11.3, 0.9, 0.7)), 34), hand=0.01)
shot("L38", "S70 caught low, swirling", move(((-11.6, 0.2, 0.9), (-11.45, 0.9, 0.85)), ((-11.5, 0.3, 0.85), (-11.45, 0.9, 0.85)), 44), hand=0.0)
shot("P01", "S71 the drop: the globe swirling, nothing else", still((-11.35, 0.5, 1.0), (-11.45, 0.9, 0.85), 50), hand=0.0)
shot("L39", "S72 the figure is on our tiny porch", minimove(((-3.0, -9.0, 4.0), (-8.6, 0.0, 2.4)), ((-4.0, -6.0, 3.6), (-8.6, 0.0, 2.4)), 34), hand=0.0)
shot("L39.2", "S73 on our porch", minimove(((-12.0, -7.0, 4.5), (-8.6, 0.0, 2.4)), ((-11.5, -5.0, 4.0), (-8.6, 0.0, 2.4)), 34), hand=0.0)
shot("L40", "S74 the window: snow coming down", move(((-12.4, 0.4, 1.5), (-6.0, 0.0, 1.7)), ((-11.6, 0.4, 1.5), (-6.0, 0.0, 1.7)), 28))
shot("L41", "S75 the porch light goes dim", move(((-7.6, -1.0, 1.9), (-9.9, -1.9, 2.4)), ((-8.0, -1.2, 2.0), (-9.9, -1.9, 2.4)), 30))
shot("L42", "S76 snow settling on nothing", still((-6.4, 1.4, 1.9), (-8.9, -1.4, 2.0), 30))
shot("L42.2", "S77 on somebody", still((-6.6, 0.6, 2.2), (-9.0, -1.4, 2.5), 34))
shot("L43", "S78 on a hat", still((-7.4, -0.2, 3.05), (-9.0, -1.4, 2.5), 40))
shot("L43.1", "S79 on two shoulders", still((-6.0, -0.4, 2.0), (-9.0, -1.4, 2.0), 32))
shot("L44", "S80 low from inside: the tall outline fills the window", still((-12.8, -0.2, 0.9), (-9.0, -1.4, 2.0), 24))
shot("L44.2", "S81 too tall for our porch", still((-5.2, -4.8, 1.7), (-8.8, -1.4, 1.6), 24))
shot("L45", "S82 standing at the window", still((-5.5, -3.4, 1.45), (-9.4, -1.4, 1.5), 28))
shot("L45.2", "S83 where Grandpa was asleep in his chair", still((-13.0, -1.6, 1.62), (-10.9, -1.4, 1.5), 32))
shot("L46", "S84 it bends down, slow", move(((-8.4, -4.2, 2.0), (-9.3, -1.4, 1.9)), ((-8.4, -4.2, 2.0), (-9.4, -1.4, 1.85)), 28))
shot("L46.2", "S85 to the glass", still((-11.6, -2.8, 1.8), (-10.0, -1.4, 1.9), 34))
shot("L47", "S86 the test still: a face of snow an inch from his sleeping face", still((-13.3, -2.5, 1.75), (-10.0, -1.3, 2.0), 34))
shot("L47.2", "S87 an inch from his", move(((-11.4, -2.3, 1.75), (-10.2, -1.4, 1.8)), ((-11.1, -2.0, 1.72), (-10.2, -1.4, 1.8)), 40))
shot("L48", "S88 the glass fogs", still((-10.55, -1.4, 1.9), (-9.9, -1.4, 1.95), 36))
shot("L48.2", "S89 Grandpa sleeps on", still((-12.2, -1.2, 1.5), (-10.95, -1.4, 1.45), 40))
# ---- 08 the twist
shot("L49", "S90 my face, scared, lit by the window", still((-11.8, 0.4, 1.52), (-13.0, 0.5, 1.5), 42))
shot("L49.1", "S91 I got it", still((-11.9, 0.3, 1.52), (-13.0, 0.5, 1.5), 55))
shot("L50", "S92 the minimap grows to fill the frame: the dot on our porch", still((-11.0, 0.9, 1.3), (GX, GY, 1.1), 40), hand=0.0)
shot("L50.2", "S93 the middle of the tiny road is empty", minimove(((6.0, -12.0, 5.0), (0.0, 0.0, 2.0)), ((4.5, -9.0, 4.5), (0.0, 0.0, 2.0)), 32), hand=0.0)
shot("L51", "S94 the globe, close: the figure on the porch, the snow figure behind", move(((-11.0, 0.7, 1.3), (-8.0, -1.4, 1.4)), ((-10.8, 0.7, 1.25), (-8.0, -1.4, 1.4)), 50), hand=0.0)
shot("L51.2", "S95 the only place you can see it", minimove(((-12.0, -7.0, 4.5), (-8.6, 0.0, 2.4)), ((-11.4, -5.0, 4.0), (-8.6, 0.0, 2.4)), 36), hand=0.0)
shot("L52", "S96 top-down on the tiny street: the bare spot in the road", move((MI(0.0, -0.4, 17.0), MI(0.0, 0.0, 0.0)), (MI(0.0, -0.4, 11.0), MI(0.0, 0.0, 0.0)), 34), hand=0.0)
shot("L52.2", "S97 since before the street", minimove(((8.0, -12.0, 2.5), (0.0, 0.0, 2.0)), ((6.0, -9.0, 2.5), (0.0, 0.0, 2.0)), 32), hand=0.0)
shot("L53", "S98 and every shake", move(((-11.15, 0.55, 1.3), GCW), ((-10.85, 0.7, 1.22), GCW), 42), hand=0.0)
shot("L53.1", "S99 moves it: the dot slides on the minimap", still((-11.0, 0.9, 1.3), (GX, GY, 1.1), 40), hand=0.0)
shot("L54", "S100 recap: the dry spot", move(((0.0, -0.06, 4.2), (0.0, 0.0, 0.0)), ((0.0, -0.06, 3.2), (0.0, 0.0, 0.0)), 28))
shot("L54.2", "S101 the snow never lands there", still((2.4, -2.0, 0.4), (0.0, 0.0, 0.3), 32))
shot("L55", "S102 recap: a car swerves", still((-4.0, -7.0, 1.4), (0.6, -1.0, 0.8), 26))
shot("L55.1", "S103 everybody swerves", still((4.0, -4.0, 1.2), (0.0, 0.5, 0.7), 34))
shot("L56", "S104 the three neighbours wobble", still((1.3, 9.0, 1.5), (-4.9, 9.0, 1.15), 25))
shot("L56.2", "S105 a faint white blur passes between them", still((0.6, 9.2, 1.4), (-4.9, 9.1, 1.2), 36))
shot("L56.3", "S106 that's it", still((-2.8, 6.4, 1.3), (-4.9, 9.0, 1.2), 44))
shot("L56.4", "S107 brushing past", still((-1.0, 12.5, 1.4), (-4.9, 9.4, 1.2), 34))
# ---- 09 the warm turn: hands over mine, tip it back
shot("L57", "S108 Grandpa's eyes open", still((-11.0, -0.3, 1.5), (-10.95, -1.4, 1.45), 46))
shot("L58", "S109 he sees the globe in my hands", still((-12.3, 0.2, 1.5), (-11.2, 0.6, 1.3), 34))
shot("L58.1", "S110 he doesn't yell", still((-11.5, -0.4, 1.55), (-11.0, -1.4, 1.45), 46))
shot("L59", "S111 his hands over mine on the base", still((-11.8, 0.9, 1.45), (-11.3, 0.9, 1.25), 42), hand=0.0)
shot("L59.2", "S112 over mine", still((-11.6, 0.4, 1.3), (-11.3, 0.9, 1.22), 50), hand=0.0)
shot("L60", "S113 we tip it slowly toward the road", move(((-11.8, 1.5, 1.4), (-11.2, 0.9, 1.25)), ((-11.7, 1.4, 1.35), (-11.2, 0.9, 1.25)), 36), hand=0.0)
shot("L60.3", "S114 toward the road", still((-11.2, 0.9, 1.5), (-5.0, 0.0, 1.0), 26))
shot("L61", "S115 the figure slides down our path", minimove(((-12.0, -7.0, 4.0), (-8.6, 0.0, 2.4)), ((-8.0, -6.0, 3.6), (-6.0, 0.0, 2.4)), 34), hand=0.0)
shot("L61.2", "S116 down our path", minimove(((-1.0, -8.0, 3.6), (-4.0, 0.0, 2.4)), ((-1.5, -7.0, 3.4), (-3.0, 0.0, 2.4)), 34), hand=0.0)
shot("L62", "S117 back to the middle", minimove(((5.0, -9.0, 4.0), (-1.0, 0.0, 2.4)), ((4.0, -8.0, 3.6), (0.0, 0.0, 2.4)), 34), hand=0.0)
shot("L62.2", "S118 of the tiny road", minimove(((3.0, -10.0, 4.4), (0.0, 0.0, 2.4)), ((2.0, -8.0, 4.0), (0.0, 0.0, 2.4)), 34), hand=0.0)
shot("L63", "S119 outside: the snow slides off something very tall", move(((4.4, -4.2, 1.6), (0.0, 0.0, 1.5)), ((4.0, -3.8, 1.55), (0.0, 0.0, 1.5)), 26))
shot("L63.3", "S120 something very tall", still((3.0, -2.2, 0.9), (0.0, 0.0, 1.7), 24))
shot("L64", "S121 the dry spot is back in the middle", move(((0.0, -0.06, 4.0), (0.0, 0.0, 0.0)), ((0.0, -0.06, 3.0), (0.0, 0.0, 0.0)), 28))
shot("L64.2", "S122 of the road", still((2.4, -2.0, 0.4), (0.0, 0.0, 0.3), 32))
# ---- 10 morning
shot("L65", "S123 morning: Grandpa holds out his truck keys on a flat palm", still((-11.8, 0.2, 1.45), (-12.6, -0.5, 1.3), 38))
shot("L65.2", "S124 the keys", still((-12.0, -0.3, 1.3), (-12.6, -0.5, 1.15), 50), hand=0.0)
shot("L66", "S125 the pickup curves round the middle", move(((-9.0, -16.0, 9.0), (0.0, 0.0, 0.5)), ((-8.0, -14.0, 8.0), (0.0, 0.0, 0.5)), 26), step=1)
shot("L66.2", "S126 like everybody does", still((-3.8, -4.0, 1.5), (0.0, 0.0, 0.7), 30))
shot("L67", "S127 Grandpa tips his hat to the middle", still((0.7, 0.2, 1.6), (-1.5, 0.0, 1.5), 34))
shot("L68", "S128 Mrs. Ortiz at her open curtains", still((6.6, 0.6, 1.55), (10.0, -1.8, 1.55), 34))
shot("L68.2", "S129 and waves", still((7.6, -0.2, 1.6), (10.0, -1.8, 1.6), 44))
shot("L69", "S130 I passed: the cone lot, the examiner nods", still((197.0, -4.5, 1.5), (201.0, 0.0, 1.35), 30))
shot("L70", "S131 now he lets me dust the globe", still((-12.2, -0.6, 1.55), (-10.8, 0.3, 1.2), 30))
shot("L70.2", "S132 the old stone base under the brush", move(((-10.95, 0.8, 1.12), (GX, GY, 1.0)), ((-10.85, 0.85, 1.1), (GX, GY, 1.0)), 50), hand=0.0)
# ---- 11 the sting
shot("L71", "S133 night, the sill, the globe alone", move(((-12.0, 0.3, 1.5), (-10.4, 0.8, 1.2)), ((-11.6, 0.4, 1.45), (-10.4, 0.8, 1.2)), 28))
shot("L71.1", "S134 nobody touched it", still((-11.3, 0.7, 1.28), (GX, GY, 1.06), 40), hand=0.0)
shot("L72", "S135 the little figure, still in the middle", minimove(((0.0, -9.0, 3.6), (0.0, 0.0, 2.4)), ((0.5, -8.0, 3.4), (0.0, 0.0, 2.4)), 34), hand=0.0)
shot("L72.2", "S136 turned", minimove(((6.0, -7.0, 3.6), (0.0, 0.0, 2.4)), ((5.0, -6.0, 3.4), (0.0, 0.0, 2.4)), 34), hand=0.0)
shot("L72.4", "S137 to face our house: the dot's face turns on the minimap", still((-11.0, 0.9, 1.3), (GX, GY, 1.1), 40), hand=0.0)
shot("L73", "S138 push in on the globe, back to the first frame",
     move(((-11.1, 0.9, 1.23), (-3.0, 0.0, 0.4)), ((-11.0, 0.9, 1.22), (-3.0, 0.0, 0.4)), 50), hand=0.0)

shots = []
for i, (at, what, cam, step, hand, kw) in enumerate(SHOTS):
    s = {"id": f"S{i + 1:03d}", "cam": cam, "hand": hand, "step": step, "what": what}
    if i:
        s["at"] = at
    s.update(kw)
    shots.append(s)
SID = {what.split(" ")[0]: s["id"] for (at, what, *_), s in zip(SHOTS, shots)}   # script ids to ours

# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "blink": True, "sit": False}
acting = {n: [{"at": 0, "pos": [0, 40], "hidden": True, "blend": 0}] for n in ALL}


def put(who, at, pos, **kw):
    if at == 0:
        acting[who] = []
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


CHAIR = (-10.95, -1.4)
SEAT_Z = -0.06
GUS_SEAT = [CHAIR[0], CHAIR[1], SEAT_Z]


def gus_chair(at, expr="neutral", head=(0, 8), **kw):
    put("gus", at, GUS_SEAT, yaw=180, expr=expr, head=list(head), sit=True, **kw)


# ---- the wobble: three neighbours in a row (L05 .. L05.3), then they're gone
for who, y in (("n3", 7.9), ("n2", 9.0), ("n1", 10.1)):
    put(who, "L05", [-4.9, y], yaw=90, expr="neutral")
    key(who, "L05.2", lean=-16, side=[38, 38], arms=[20, 20], blend=0.2, expr="scared")
    key(who, "L05.2+0.45", lean=10, side=[10, 10], blend=0.3)
    key(who, "L05.3", lean=-6, side=[24, 24], blend=0.3)
    key(who, "L05.3+0.6", lean=0, side=[0, 0], arms=[0, 0], blend=0.5, expr="worried")
    hide(who, "L06")
# the mug: his right arm swings up as it spills
key("n1", "L05.2", arms=[10, 95], blend=0.15)
# the mailman drops his bag
put("mailman", "L05.3", [4.9, -8.6], yaw=180, expr="neutral")
walk("mailman", "L06+0.4", [4.9, -6.7], yaw=180)
key("mailman", "L06.1", lean=-14, arms=[70, 70], side=[25, 25], expr="scared", blend=0.15)
key("mailman", "L06.2+0.4", lean=0, arms=[0, 0], side=[0, 0], expr="worried", blend=0.4)
hide("mailman", "L07")
# Mrs. Ortiz sits down in her flowerbed
put("ortiz", "L06.2", [8.9, 3.9], yaw=-120, expr="neutral")
walk("ortiz", "L07+0.5", [7.45, 2.9], yaw=-120)
key("ortiz", "L07", arms=[20, 20], blend=0.3)
key("ortiz", "L07+0.55", lean=-18, arms=[60, 60], side=[30, 30], expr="scared", blend=0.2)
put("ortiz", "L07.1", [7.45, 2.35, -0.36], yaw=-115, expr="wide", sit=True)
key("ortiz", "L07.2", arms=[20, 20], expr="worried", blend=0.4)
hide("ortiz", "L08.2")
# the size of a person
put("n2", "L09.2", [0.95, 0.15], yaw=-70, expr="neutral")
hide("n2", "L10")
# ---- inside: Grandpa at the window, me behind him
gus_chair("L11", "neutral", (-70, 14))
put("me", "L11", [-13.9, 0.25], yaw=90, expr="soft", head=[0, 6])
hide("me", "L11.2")
# my face through the glass
put("me", "L14", [-12.6, 0.45], yaw=90, expr="neutral", head=[0, 4])
hide("me", "L14.2")
# morning on the porch
hide("gus", "L14.2")
put("gus", "L15", [-8.4, -0.5], yaw=90, expr="smile", head=[0, 6])
key("gus", "L15+0.4", arms=[0, 150], blend=0.4)
key("gus", "L15.3", arms=[0, 150], blend=0.1)
key("gus", "L15.3+0.5", arms=[0, 0], blend=0.4)
hide("gus", "L16")
# the truck: me driving, Grandpa beside me
put("gus", "L16", [-3.9, 7.0, 0.22], yaw=0, expr="smile", sit=True, head=[0, 4])
put("me", "L16", [-2.9, 7.0, 0.2], yaw=0, expr="worried", sit=True, head=[0, 0])
key("me", "L16.2", expr="worried")
hide("gus", "L17")
hide("me", "L17")
# the night before the test
put("me", "L17", [-12.9, 0.45], yaw=90, expr="worried", head=[0, 4])
key("me", "L17.2", expr="scared", blend=0.3)
hide("me", "L18")
# the first shake
put("me", "L18.2", [-11.6, 0.95], yaw=90, expr="neutral", arms=[78, 78], side=[-28, -28])
put("me", "L19", [-11.9, 0.95], yaw=90, expr="scared", lean=8)
key("me", "L19+0.25", lean=-10, arms=[40, 40], side=[30, 30], blend=0.15)
key("me", "L19+0.7", lean=2, arms=[0, 0], side=[0, 0], blend=0.4)
hide("me", "L20")
put("me", "L21", [-12.7, 0.5], yaw=90, expr="grin", head=[0, 20], arms=[70, 70], side=[-20, -20])
hide("me", "L22")
# nothing seen of anyone while the figure has moved
# the second shake
put("me", "L28", [-12.7, 0.5], yaw=90, expr="neutral", head=[0, 20], arms=[70, 70], side=[-20, -20])
key("me", "L28.2", expr="sad-smile", head=[0, 12], blend=0.3)
put("me", "L29", [-11.6, 0.95], yaw=90, expr="worried", arms=[78, 78], side=[-28, -28])
key("me", "L29.2", lean=6, blend=0.2)
hide("me", "L30")
# the mailman on our path (backwards, the way he came)
put("mailman", "L30", [1.5, 0.25], yaw=-90, expr="neutral")
walk("mailman", "L31.2", [-4.9, 0.25], yaw=-90)
key("mailman", "L31.2", expr="wide", blend=0.2)
walk("mailman", "L32", [-1.5, 0.25], yaw=-90)
key("mailman", "L32", expr="worried")
walk("mailman", "L32.2", [-0.5, 0.25], yaw=-90)
hide("mailman", "L33")
# Grandpa saw the globe: silent dinner
gus_chair("L33", "angry", (-60, 12))
key("gus", "L33.1", expr="angry")
hide("gus", "L34")
put("gus", "L34", [-14.2, -0.98, -0.23], yaw=180, expr="angry", head=[0, 22], sit=True)
put("me", "L34", [-14.2, 0.98, -0.23], yaw=0, expr="sad-smile", head=[0, 22], sit=True)
hide("gus", "L35")
hide("me", "L35")
# Friday night, 2 a.m.
put("me", "L35", [-13.6, 0.6], yaw=90, expr="worried", head=[0, 6])
put("me", "L35.1", [-13.0, 0.5], yaw=90, expr="worried", head=[0, 6])
put("me", "L36", [-12.6, 0.8], yaw=90, expr="worried", head=[0, 6])
put("me", "L36.1", [-12.2, 0.9], yaw=90, expr="worried", arms=[78, 78], side=[-26, -26], head=[0, 22], blend=0.4)
put("me", "L37", [-12.2, 0.9], yaw=90, expr="scared", arms=[70, 70], side=[-26, -26], lean=4)
key("me", "L37+0.2", arms=[30, 30], lean=10, blend=0.1)
key("me", "L38", arms=[40, 40], lean=14, blend=0.1)
key("me", "L38+0.3", arms=[78, 78], lean=4, blend=0.3)
hide("me", "L39")
gus_chair("L39", "asleep", (-95, 18))
put("gus", "L47", [GUS_SEAT[0], GUS_SEAT[1] + 0.45, GUS_SEAT[2]], yaw=180, expr="asleep", head=[-95, 18], sit=True)
put("gus", "L47.2", GUS_SEAT, yaw=180, expr="asleep", head=[-95, 18], sit=True)
# my face lit by the window
put("me", "L49", [-12.9, 0.5], yaw=90, expr="scared", head=[0, 4])
key("me", "L49.1", expr="scared", blend=0.3)
hide("me", "L50")
# Grandpa wakes (still seated), then stands beside me
key("gus", "L57", expr="neutral", head=[-60, 6], blend=0.3)
hide("gus", "L58")
put("gus", "L58", [-12.4, 1.55], yaw=90, expr="soft", head=[0, 8])
put("me", "L58", [-12.0, 0.6], yaw=90, expr="worried", arms=[78, 78], side=[-26, -26], head=[0, 10])
key("gus", "L58.1", expr="soft", head=[-50, 4])
walk("gus", "L58.1+0.3", [-12.0, 1.4], yaw=90)
put("gus", "L59", [-12.0, 1.4], yaw=90, expr="soft", arms=[78, 78], side=[-26, -26])
key("me", "L59", expr="soft", blend=0.5)
key("gus", "L60.3", expr="soft")
hide("gus", "L63")
hide("me", "L63")
# morning: the keys
put("gus", "L65", [-12.6, -0.5], yaw=90, expr="smile", arms=[0, 82], side=[0, -10], head=[0, 6])
hide("gus", "L66")
# the truck at the middle: Grandpa tips his hat to it
put("gus", "L67", [-1.1, -0.5, 0.22], yaw=180, expr="smile", sit=True, head=[0, 0])
key("gus", "L67", arms=[0, 150], blend=0.3)
key("gus", "L67.2+0.3", arms=[0, 0], blend=0.4)
put("me", "L67", [-2.1, -0.5, 0.2], yaw=180, expr="neutral", sit=True, head=[0, 0])
hide("gus", "L68")
hide("me", "L68")
put("ortiz", "L68", [9.55, -1.8], yaw=-90, expr="smile", head=[0, 4])
key("ortiz", "L68.2", arms=[0, 150], blend=0.3, expr="smile")
key("ortiz", "L68.2+0.5", arms=[0, 110], blend=0.25)
key("ortiz", "L68.2+0.9", arms=[0, 150], blend=0.25)
hide("ortiz", "L69")
# I passed
put("me", "L69", [199.4, 0.2], yaw=150, expr="grin", head=[0, 0])
put("examiner", "L69", [201.2, 1.0], yaw=-115, expr="smile", head=[0, 0])
key("examiner", "L69+0.2", head=[0, 22], blend=0.2)
key("examiner", "L69+0.45", head=[0, 0], blend=0.2)
hide("me", "L70")
hide("examiner", "L70")
# dusting the globe
put("me", "L70", [-11.05, 0.9], yaw=90, expr="smile", arms=[60, 60], side=[-18, -18], head=[0, 14])
key("me", "L70.2", arms=[70, 78], blend=0.3)
key("me", "L70.2+0.6", arms=[70, 60], blend=0.3)
gus_chair("L70", "smile", (-70, 6))
hide("me", "L71")
hide("gus", "L71")

# ---------------------------------------------------------------------------------------------------- cues
cues = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


# time of day: bright by day, a deeper blue for the night scenes, the 2 a.m. scene darkest (porch light halves at L41)
for at, m in ((0, "snow"), ("L08", "day"), ("L17", "dusk"), ("L21.1", "dusk"), ("L24", "day"), ("L28.2", "dusk"),
              ("L33", "day"), ("L34.2", "dusk"), ("L35", "dim"), ("L39", "night"), ("L57", "dim"), ("L63", "day"),
              ("L70.2", "day"), ("L71", "dim")):
    cue(at, "mode", set=m, dur=0.5)
cue("L41", "porch", on=0.5, dur=0.6)
cue("L57", "porch", on=1.0, dur=0.6)
# snow: the first storm (L03 to L07), the second (L20), the 2 a.m. one (L40 to L48)
for at, on in ((0, False), ("L03", True), ("L08", False), ("L20", True), ("L22", False), ("L40", True), ("L49", False)):
    cue(at, "snow", on=on)
# the dry patch: middle of the road until the first shake, then wherever it is
for at, pos in ((0, [0.0, 0.0]), ("L24", list(SPOT_ORTIZ)), ("L30.3", list(SPOT_MAIL)), ("L39", [0.0, 0.0] if False else None),
                ("L64", [0.0, 0.0])):
    if pos is not None:
        cue(at, "spot", pos=pos)
cue("L39", "spot", pos=[0.0, 0.0])
cue("L09", "steam", on=True)
cue("L10", "steam", on=False)
cue("L54", "steam", on=True)
cue("L54.2+0.8", "steam", on=False)
# the Stander: unseen on the real street until the snow settles on it
cue(0, "stander", hidden=True)
cue("L42", "stander", pos=[-8.85, -1.4], yaw=-90, reveal=0.0)
cue("L42+0.3", "stander", pos=[-8.85, -1.4], yaw=-90, reveal=1.0, dur=4.4)
cue("L46", "stander", pos=[-8.85, -1.4], yaw=-90, bend=45, head=-22, dur=1.4)
cue("L49", "stander", hidden=True)
cue("L63", "stander", pos=[0.0, 0.0], yaw=90, reveal=1.0, bend=0, head=0, melt=0.0)
cue("L63.3", "stander", pos=[0.0, 0.0], yaw=90, melt=1.0, dur=1.4)
cue("L64", "stander", hidden=True)
# the globe: on the sill, in my hands for the late shakes, tipped toward the road
G0 = [-10.25, 0.9, 0.95]
cue(0, "globe", pos=G0, tilt=[0, 0])
cue("L36.1", "globe", pos=[-11.55, 0.9, 1.12], tilt=[0, 0], dur=0.7)
cue("L37", "globe", pos=[-11.5, 0.9, 0.45], tilt=[20, 10], dur=0.4)
cue("L38", "globe", pos=[-11.5, 0.9, 0.78], tilt=[0, 0], dur=0.3)
cue("L38+0.6", "globe", pos=[-11.5, 0.9, 0.78], tilt=[-6, 8], dur=0.4)
cue("L39", "globe", pos=G0, tilt=[0, 0], dur=0.3)
cue("L58", "globe", pos=[-11.4, 0.6, 1.1], tilt=[0, 0], dur=0.3)
cue("L60", "globe", pos=[-11.4, 0.6, 1.1], tilt=[0, 32], dur=1.8)
cue("L63", "globe", pos=G0, tilt=[0, 0], dur=0.3)
cue("L69", "globe", pos=[-10.25, 0.9, 0.95], tilt=[0, 0])
# shakes: the swirl starts
for at in ("L03", "L18.3", "L29.2", "L38+0.3", "L53"):
    cue(at, "swirl")
# the tiny figure and the minimap dot: middle, Mrs. Ortiz's gate, our mailbox, our porch, back down the path, turned
cue(0, "fig", pos=[0.0, 0.0])
cue("L22", "fig", pos=list(MAP_ORTIZ) if False else [5.4, 0.0])
cue("L30", "fig", pos=[-4.7, 0.9])
cue("L39", "fig", pos=[-8.6, 0.0])
cue("L53.1", "fig", pos=[-4.7, 0.9], dur=0.8)
cue("L57", "fig", pos=[-8.6, 0.0], dur=0.4)
cue("L61", "fig", pos=[-5.6, 0.0], dur=1.5)
cue("L62", "fig", pos=[0.0, 0.0], dur=1.3)
cue(0, "turn", on=0.0)
cue("L72.2", "turn", on=1.0, dur=0.8)
cue("L50", "mapgrow", v=1.0, dur=0.7)
cue("L50.2", "mapgrow", v=0.0, dur=0.5)
cue("L53.1", "mapgrow", v=1.0, dur=0.4)
cue("L54", "mapgrow", v=0.0, dur=0.5)
cue("L72.4", "mapgrow", v=1.0, dur=0.5)
cue("L73", "mapgrow", v=0.0, dur=0.5)
cue("L48", "fog", on=1.0, dur=0.9)
cue("L49", "fog", on=0.0, dur=0.6)
# Mrs. Ortiz's curtains: shut from the second morning, open at the end
cue(0, "curtains", open=0.0)
cue("L68.1", "curtains", open=1.0, dur=0.6)
# the dog
cue(0, "dog", hidden=True)
cue("L07", "dog", pos=[6.5, 3.3], yaw=-60, pose="stand")
cue("L08.2", "dog", hidden=True)
cue("L27", "dog", pos=[9.2, 0.95], yaw=-90, pose="brace")
cue("L28", "dog", hidden=True)
# the truck: at the curb, then round the middle, then stopped beside the patch for Grandpa to tip his hat
cue(0, "truck", pos=[-3.4, 6.5], yaw=0)
cue("L67", "truck", pos=[-1.6, 0.0], yaw=180)
cue("L66", "tdrive", dur=2.6, y=[-16.0, 14.0], lane=-0.2, swerve=2.0, around=[0.0, 0.0])
# cars swerving
cue("L10", "car", dur=1.9, y=[-14.0, 14.0], lane=0.4, swerve=2.0, around=[0.0, 0.0])
cue("L55", "car", dur=1.9, y=[-14.0, 14.0], lane=0.4, swerve=2.0, around=[0.0, 0.0])
# mail and the bag
cue("L06.1", "bag", pos=[5.2, -6.5], yaw=25)
cue("L06.1", "mail", pos=[4.9, -6.4], n=9, fall=True)
cue("L07", "bag", pos=None)
cue("L07", "mail", pos=[4.9, -6.4], n=0)
cue("L32", "mail", pos=[-5.5, 0.1], n=7)
cue("L33", "mail", pos=[-5.5, 0.1], n=0)
# the blur
cue("L56.2", "blur", dur=1.4, **{"from": [-3.8, 8.0], "to": [-4.6, 11.0]})
# the phone
cue("L21", "phone", on=True, pos=[-12.38, 0.5, 1.3], rot=[0, 0, -90], state="snow")
cue("L22", "phone", on=False)
cue("L28", "phone", on=True, pos=[-12.38, 0.5, 1.3], rot=[0, 0, -90], state="cal")
cue("L29", "phone", on=False)

# ---------------------------------------------------------------------------------------------------- sound, music, look
sound = {
    "floor": "snow", "steps_db": -22, "rev": 1,
    "ambience": [{"kind": "wind", "from": 0, "to": "end", "lufs": -41},
                 {"kind": "hum", "from": "L39", "to": "L57", "lufs": -44}],
    "sfx": [
        {"at": "L01.1+0.18", "kind": "knock", "pattern": [0], "tone": "glass_soft", "db": -9},
        {"at": "L03+0.05", "kind": "thud", "db": -16},
        {"at": "L19+0.05", "kind": "creak", "db": -20, "dur": 0.9},
        {"at": "L19+0.2", "kind": "thud", "db": -16},
        {"at": "L29.2+0.1", "kind": "thud", "db": -18},
        {"at": "L38+0.4", "kind": "thud", "db": -14},
        {"at": "L41", "kind": "creak", "db": -30, "dur": 0.9},
        {"at": "L48+0.3", "kind": "whoosh", "db": -26, "dur": 0.9},
        {"at": "L63.3+0.4", "kind": "thud", "db": -22},
    ],
    "music_drops": [{"from": "P01", "to": "P01>"}],
}
music = {"root": 50, "mode": "major", "bpm": 96, "seed": 80, "sections": [
    {"at": 0, "voices": ["piano", "pulse"], "energy": 0.32},
    {"at": "L22", "voices": ["piano", "pulse", "pad"], "energy": 0.4},
    {"at": "L39", "voices": ["drone", "pad"], "energy": 0.5, "mode": "minor", "root": 50},
    {"at": "L57", "voices": ["drone", "pad", "piano"], "energy": 0.45, "mode": "major", "root": 50},
    {"at": "L71", "voices": ["drone"], "energy": 0.4, "mode": "minor", "root": 50},
]}
look = {"style": "closer", "fog": "#dcecf8", "fog_density": 0.01, "fog_start": 22.0, "sky": "#9ad6ff", "sky_strength": 1.0,
        "exposure": 0.0, "flash_safe": True,
        "polish": {"emph": ["L01.1", "L19", "L47", "L50", "L53", "L72.2"], "reveal": ["L47", "L53"], "twist": "L49",
                   "sway": [s["id"] for s in shots if s["what"].split(" ")[0] in
                            tuple(f"S{n}" for n in range(72, 90))]}}
story = {
    "slug": "ep80-snow-globe", "title": "Never Shake Grandpa's Snow GLOBE", "made_for_kids": False,
    "premise": "Grandpa Gus's snow globe makes it snow on our street and only ours, and everyone stumbles at once when it is shaken. "
               "After every snow one person-sized dry spot stays in the middle of the road and every car swerves around it. "
               "My driving test is tomorrow and I shake it for a snow day.",
    "twist": "Something far too tall has always stood in the middle of our road, the globe is the only place you can see it, "
             "and every shake moves it to somebody's door. The stumble is it brushing past everyone on its way.",
    "world": "one snowy street of nine painted houses a side, seen from Grandpa's front room and porch, with a glass snow globe on the sill",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45}, "key_color": "#6fd0ff", "gap": 0.15, "tail": 0.25,
    "fade_in": False, "fade_out": False, "look": look,
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.01, -0.02], "saturation": 1.08, "contrast": 1.05,
              "vignette": 0.22, "bloom": 0.22, "grain": 0.008},
    "cast": cast, "lines": lines, "shots": shots, "acting": acting, "cues": cues, "music": music, "sound": sound,
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False))
print("wrote", OUT, len(shots), "shots")
