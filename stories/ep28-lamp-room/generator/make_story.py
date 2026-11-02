"""Writes ../story.json for ep28 "Who was on the lighthouse stairs every night?" (the Upward). Run from anywhere:
python stories/ep28-lamp-room/generator/make_story.py

The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (the light, the creature, the torch and phone, the bolt, the doors, the sand, the coat
and blanket), the effects, the score and the sound. Places are set.py's metres: the tower's axis is x = y = 0 and
the slate floor is z = 0; the stair is 12 treads a turn, 2.2 m a turn, azimuth 0 = +x and counter-clockwise going
up; the kitchen is a separate room at x = 40; the lamp room floor is at LF. A character faces -y at yaw 0.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

RISE, PER, TURNS = 2.2, 12, 7
STEP = RISE / PER
LF = TURNS * RISE + 2.4
KX = 40.0
Z4, Z5, Z6, Z7 = 4 * RISE, 5 * RISE, 6 * RISE, 7 * RISE
LOOP = 0.25   # a hard cut 0.25 s after the last word, into L01 (no fade at either end)
HOLDS = {"L59": 0.5, "L45": 0.4, "L66": 0.4}   # a breath after the quiet beats (keeps the film over 2:15)
for ln in lines:
    if ln["id"] in HOLDS:
        ln["gap"] = HOLDS[ln["id"]]
# captions are two or three words, so a phrase of four or more is cut in two (4: 2+2, 5: 2+3, 6: 3+3, 7: 2+2+3). lines.json
# keeps the writer's phrases; every chunk reference below ("L54.2") counts phrases and is mapped to the cut chunks
# at the end (fix_refs)
PHRASE_START = {}


def split_chunks(chunks):
    out, starts = [], []
    for cap, sp in chunks:
        starts.append(len(out))
        cw, sw = cap.split(), sp.split()
        n = len(cw)
        if n <= 3 or len(sw) != n:
            out.append([cap, sp])
            continue
        p = -(-n // 3)                      # pieces of at most three words, the longer ones last
        sizes = [n // p + (1 if k >= p - n % p else 0) for k in range(p)]
        i = 0
        for z in sizes:
            out.append([" ".join(cw[i:i + z]), " ".join(sw[i:i + z])])
            i += z
    return out, starts


for ln in lines:
    if ln.get("chunks"):
        ln["chunks"], PHRASE_START[ln["id"]] = split_chunks(ln["chunks"])
lines = lines + [{"id": "P99", "pause": LOOP, "chunks": []}]

# the word check: Kokoro says "Ines" as ee-NESS (phonemes below). Whisper small.en writes "oilskin" as "oil skin", and
# hears "At three" as "Night three" and "slept two" as "slept too" (same sounds): the story's "homophones" below ask
# `asr` to forgive those, and the lines Whisper dropped words from are slowed or given a breath in their spoken text
# (the captions don't change)
TEMPO = {"L68": 0.8, "L32": 0.85}
SPOKEN = {("L51", "Its flat face"): "Its, flat face",
          ("L68", "ASLEEP,"): "Fast asleep,", ("L16", "torch in"): "torch, in"}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]
    for ch in ln.get("chunks", []):
        if (ln["id"], ch[0]) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], ch[0])]

# ---------------------------------------------------------------------------------------------------- cast
cast = {
    "me": {"age": "adult", "skin": "#e0b48c", "shirt": "#d0a232", "pattern": "knit", "pattern_c": "#26354f",
           "pants": "#80858c", "shoes": "#f4ecd8", "sleeves": "long", "collar": None, "hair": "cap",
           "hair_c": "#1b1511", "hat": "none", "face": {"eyes": "round", "brows": True, "ink": "#161012"}},
    "ines": {"age": "adult", "skin": "#c98f6a", "shirt": "#3f8f7d", "pattern": "plaid", "pattern_c": "#1d4a42",
             "pants": "#2a2f3c", "shoes": "#2a2420", "sleeves": "long", "collar": None, "hair": "long",
             "hair_c": "#0f0c0d", "hat": "none",
             "face": {"eyes": "lashes", "brows": True, "ink": "#161012"}},
}


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens, roll=0):
    return c([0, loc, tgt, lens] + ([roll] if roll else []))


def move(a, b, lens_a, lens_b=None):
    return c([0, a[0], a[1], lens_a], [1, b[0], b[1], lens_b or lens_a])


def pol(r, az, z):
    a = math.radians(az)
    return [round(r * math.cos(a), 3), round(r * math.sin(a), 3), round(z, 3)]


def wall_r(z):
    return 2.75 + (2.45 - 2.75) * max(0.0, min(1.0, z / LF))


def tread(i, r=1.7):
    return pol(r, 30.0 * i, i * STEP)


def yaw_to(a, b):
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


def az_of(a, b):
    return round(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])), 1)


def sit_at(i, back=0.3):
    """Where I sit on tread i with my back to the wall: (pos with the seat's z, yaw to face the well)."""
    z = i * STEP
    az = 30.0 * i
    r = wall_r(z) - back
    p = pol(r, az, z)
    yaw = yaw_to(p, (0, 0))
    return [p[0], p[1], round(z - 0.51, 3)], yaw, p


def local(base, yaw, fwd, right, up):
    """A world point from a base, its yaw, and offsets forward / to its right / up."""
    f = (math.sin(math.radians(yaw)), -math.cos(math.radians(yaw)))
    r = (-math.cos(math.radians(yaw)), -math.sin(math.radians(yaw)))
    return [round(base[0] + f[0] * fwd + r[0] * right, 3), round(base[1] + f[1] * fwd + r[1] * right, 3),
            round(base[2] + up, 3)]


def RF(n, d=2.0, lens=28, dz=1.5, side=0.0, tz=-0.1):
    """The camera in the well, looking at me at the rail on turn n (the wall and its feature behind me)."""
    z = n * RISE
    return still([1.62 - d, side, z + dz + 0.05], [1.6, 0.0, z + dz + tz], lens)


def POV(n, tgt, lens, push=0):
    z = n * RISE + 1.55
    loc = [1.3, 0.0, z]
    if push:
        return c([0, loc, tgt, lens], [1, loc, tgt, lens + push])
    return still(loc, tgt, lens)


# the lamp room: the cot, the lens, the glass
COT_FACE = still([-1.3, -1.6, LF + 1.6], [-1.3, 0.4, LF + 1.38], 32)
COT_WIDE = still([0.4, -1.7, LF + 1.5], [-1.3, 0.3, LF + 0.9], 28)
SOCKS = still([0.5, -2.15, LF + 1.0], [-0.3, -1.3, LF + 0.1], 24)
PLATE_CAM = still([0.8, 0.34, 16.34], [2.4, 0.34, 16.34], 40)
PLATE_C = [2.365, 0.34, 16.45]

# ---------------------------------------------------------------------------------------------------- shots
# (at, rain?, mode, what, step, camera). A mode is a cue (set below) so each shot's light is explicit.
SHOTS = []


def shot(at, what, cam, step=2, rain=False, hand=0.008):
    SHOTS.append({"at": at, "what": what, "cam": cam, "step": step, "rain": rain, "hand": hand})


# 01 the text (night one, cold open)
shot(0, "S01: black, then the phone glow on my face", COT_FACE)
shot("L02", "wide of the lamp room from outside the glass", still([0.3, -5.4, LF + 2.0], [-0.4, 0, LF + 1.4], 26), rain=True)
shot("L03", "the lighthouse on the cliff top, the warm window halfway up",
     move(([-4, -30, 6.5], [0, 0, 10.5]), ([-3.6, -28, 7.5], [0, 0, 10.5]), 20), rain=True)
# 02 arrival
shot("L04", "Ines and me at the foot, bags", still([0.0, 9.0, 1.45], [0.0, 3.6, 1.35], 30))
shot("L05", "low angle up the tower, rain", move(([0.5, -9.5, 0.5], [0.3, -0.3, 16]), ([0.3, -9.0, 0.5], [0.3, -0.3, 16]), 17), rain=True)
shot("L06", "from the stair foot, up the well by day", still([0.1, 0.1, 0.4], [0.2, -0.05, 17.0], 15))
shot("L07", "Ines at her blue door", RF(4, d=2.0, lens=28))
shot("L07.2", "the camp bed beside the lens", still([0.6, -2.3, LF + 1.4], [-1.1, 0.2, LF + 0.7], 28))
shot("L08", "me at the lamp room glass, my back to camera", still([-0.9, -0.6, LF + 1.7], [0.2, 2.1, LF + 1.45], 30))
shot("L09", "close on me, worried, glancing down the stairs", RF(7, d=2.0, lens=30))
shot("L10", "Ines on the phone in the kitchen", still([KX + 2.15, 0.4, 1.5], [KX - 1.0, 0.4, 1.35], 26))
shot("L11", "Ines looks up the stairwell", still([0.5, 1.6, 0.9], [0.0, -1.7, 1.3], 30))
shot("L12", "the stair foot by day: empty, sand under the door", still([0.0, -0.4, 1.0], [0.0, 2.0, 0.7], 20))
shot("L13", "the oak door from the landing", still([0.2, -0.9, 16.9], [2.3, 0.15, 16.3], 30))
shot("L13>-0.35", "the bolt plate: two strokes", PLATE_CAM, hand=0)
shot("L14>-0.3", "me in the camp bed, rain on the glass", still([0.5, -1.6, LF + 1.5], [-1.3, 0.4, LF + 0.9], 30), rain=True)
# 03 night one
shot("L15", "black, the buzz, the glow on my face; I'm standing",
     still([-0.7, -2.2, LF + 1.62], [-0.7, -0.6, LF + 1.4], 32))
shot("L16", "over my shoulder at the top rail", RF(7, d=2.2, lens=28))
shot("L17", "POV straight down seven turns: the figure, tiny",
     still([1.3, 0.0, Z7 + 1.55], [0.0, 1.55, 1.2], 26), step=1, hand=0)
shot("L18", "a longer lens: the crown face", still([1.3, 0.0, Z7 + 1.55], [0.0, 1.55, 1.2], 95), step=1, hand=0)
shot("L19", "tighter, held", still([1.3, 0.0, Z7 + 1.55], [0.0, 1.55, 1.5], 135), step=1, hand=0)
shot("L20", "a slow push", move(([1.3, 0.0, Z7 + 1.55], [0.0, 1.55, 1.5]), ([1.3, 0.0, Z7 + 1.55], [0.0, 1.55, 1.5]), 100, 150),
     step=1, hand=0)
shot("L21", "I run through the lamp-room door", still([-0.3, -1.4, 16.6], [1.9, 0.2, 15.9], 22), step=1)
shot("L21.1", "the bolt slides across", PLATE_CAM, hand=0)
shot("L22", "my face lit by the phone, scared", COT_FACE)
shot("L23", "the glow fades", COT_FACE)
# 04 morning one
shot("L24", "my socks on the clean boards, sand", SOCKS, hand=0.003)
shot("L25", "through the glass: the beach far below", still([0.0, 1.8, LF + 1.7], [0.0, 61.8, -7.2], 34))
shot("L26", "kitchen: toast", still([KX + 2.15, 0.1, 1.5], [KX, 0.1, 1.0], 24))
shot("L27", "close on Ines, looking", still([KX + 0.62, -0.5, 1.52], [KX, 0.95, 1.38], 34))
shot("L27.1", "insert: my socks under the table", still([KX + 1.3, -0.04, 0.6], [KX, -0.1, 0.6], 36), hand=0.003)
shot("L27.1+0.7", "close on Ines, the look", still([KX + 0.62, -0.5, 1.52], [KX, 0.95, 1.38], 34))
shot("L28", "close on me, misreading", still([KX, 0.7, 1.55], [KX, -0.75, 1.36], 30))
shot("L29", "me looking past her", still([KX + 0.9, 0.3, 1.5], [KX, -0.75, 1.38], 30))
shot("L29.2", "the stair foot through the doorway: empty", still([KX + 1.2, -1.3, 1.35], [KX + 3.4, -1.3, 0.8], 24))
shot("L30", "the two of us, silence", still([KX + 2.15, -1.5, 1.9], [KX, 0.1, 1.0], 20))
# 05 night two
shot("L31", "the tower in heavier rain", move(([-3, -27, 6], [0, 0, 10]), ([-2.2, -24, 8], [0, 0, 10]), 18), rain=True)
shot("L32", "black, buzz, glow ramps on my face", COT_FACE)
shot("L33", "the glow on my face, eyes wide", still([-1.3, -1.3, LF + 1.6], [-1.3, 0.4, LF + 1.42], 38))
shot("L34", "at the rail again, the round window behind", RF(6, d=2.2, lens=28))
shot("L35", "POV: the figure on turn 1, five turns below", POV(6, [1.6, 0.0, RISE + 1.78], 70), step=1, hand=0)
shot("L36", "tighter: the crown, a small open dot", POV(6, [1.6, 0.0, RISE + 1.78], 125), step=1, hand=0)
shot("L37", "I run up and bolt the door", still([-0.5, 0.0, 15.6], [1.2, -0.9, 14.4], 18), step=1)
shot("L37.1", "the bolt slides", PLATE_CAM, hand=0)
# 06 morning two
shot("L38", "more sand on my socks", SOCKS, hand=0.003)
shot("L39", "kitchen: Ines with two mugs", still([KX + 2.0, 1.2, 1.6], [KX, 0.2, 1.05], 24))
shot("L40", "close on Ines: her eyes on my sandy socks, then me", still([KX + 0.62, -0.5, 1.52], [KX, 0.95, 1.38], 34))
# 07 night three
shot("L41", "me in the camp bed, trying to stay awake", COT_WIDE)
shot("L42", "buzz, glow, the rail: a coil of rope behind me", RF(5, d=2.2, lens=28))
shot("L43", "POV: the figure on turn 2, three turns below", POV(5, [1.6, 0.0, 2 * RISE + 1.78], 34), step=1, hand=0)
shot("L44", "tight on the crown: a round hole", POV(5, [1.6, 0.0, 2 * RISE + 1.78], 56), step=1, hand=0)
shot("L45", "held, a slow push", POV(5, [1.6, 0.0, 2 * RISE + 1.78], 56, push=8), step=1, hand=0)
shot("L46", "straight up the well", still([0.3, 0.0, 9.4], [0.0, 0.0, 19.0], 17))
# 08 night four (the scare)
shot("L47", "black, a blue chill on my face, eyes opening", COT_FACE)
shot("L48", "over my shoulder at the rail: Ines's door ajar", RF(4, d=2.1, lens=26))
shot("L49", "the torch cone tilting down the well",
     c([0, [1.3, 0.0, Z4 + 1.55], [-1.0, 0.0, Z4 + 1.0], 26], [1, [1.3, 0.0, Z4 + 1.55], [1.6, 0.0, 5.6], 26]), step=1, hand=0.004)
shot("P01", "the cone settling on the steps", still([1.3, 0.0, Z4 + 1.55], [1.6, 0.0, 5.6], 30), step=1, hand=0.002)
shot("L50", "POV: the Upward one turn below", still([1.3, 0.0, Z4 + 1.55], [1.6, 0.0, 3 * RISE + 1.9], 28), step=1, hand=0.004)
shot("L51", "tight on the crown face, the mouth wide",
     c([0, [1.3, 0.0, Z4 + 1.55], [1.6, 0.0, 3 * RISE + 1.78], 38], [1, [1.3, 0.0, Z4 + 1.55], [1.6, 0.0, 3 * RISE + 1.78], 44]),
     step=1, hand=0.004)
shot("L52", "buzz: close on my face lit by the phone, terrified", RF(4, d=1.5, lens=32, tz=-0.3), step=1)
shot("L53", "back to the crown face, held",
     still([1.3, 0.0, Z4 + 1.55], [1.6, 0.0, 3 * RISE + 1.78], 44), step=1, hand=0.003)
def runcam(i, az, lens=24):
    """In the well, ahead of me round the spiral as I run up past tread i (azimuth az): my face comes toward the lens."""
    z = i * STEP
    a, a2 = math.radians(az + 80), math.radians(az)
    loc = [round(0.8 * math.cos(a), 3), round(0.8 * math.sin(a), 3), round(z + 1.6, 3)]
    return still(loc, [round(1.8 * math.cos(a2), 3), round(1.8 * math.sin(a2), 3), round(z + 1.4, 3)], lens)


shot("L54", "running up, one", runcam(48.6, 18), step=1)
shot("L54.1", "running up, two", runcam(61.9, 57, 20), step=1)
shot("L54.2", "running up, three", runcam(73.9, 57, 20), step=1)
shot("L54.3", "the bolt slides", PLATE_CAM, step=1, hand=0)
# 09 the last day
shot("L55", "kitchen, flat bright daylight", still([KX + 2.15, 0.6, 1.5], [KX, 0.1, 1.15], 24))
shot("L56", "Ines sits next to me instead of across", still([KX + 2.15, -1.5, 1.9], [KX + 0.2, -0.2, 1.0], 20))
shot("L57", "Ines says goodnight at her door, lamp on, her face to camera", still([0.0, -0.75, Z4 + 1.3], [1.8, 0.0, Z4 + 1.35], 32), hand=0.003)
shot("L58", "me in the camp bed, listening", COT_WIDE)
shot("L59", "the lamp room in the dark, rain settling", still([0.5, -2.0, LF + 1.8], [-0.8, 0.5, LF + 1.0], 22), rain=True)
# 10 dawn
SIT_ME, YAW_ME, SEAT_ME = sit_at(42)
SIT_IN, YAW_IN, SEAT_IN = sit_at(40)
SIT_IN2, YAW_IN2, SEAT_IN2 = sit_at(41)
shot("L60", "gold sun rises on my face, eyes open", still(local(SEAT_ME, YAW_ME, 1.7, -0.1, 1.2), local(SEAT_ME, YAW_ME, 0, 0, 0.92), 30))
shot("L61", "wider: me slumped on a step in the sun", still(local(SEAT_ME, YAW_ME, 3.0, 0.9, 1.6), local(SEAT_ME, YAW_ME, 0, 0, 0.8), 24))
shot("L62", "below her door, open, the room empty", still([-1.5, -0.2, 8.4], [2.3, 0.6, 9.6], 24))
shot("L63", "Ines asleep two steps down in the blanket",
     still(local(SEAT_IN, YAW_IN, 2.0, -0.35, 1.4), local(SEAT_IN, YAW_IN, 0, 0, 0.85), 30))
shot("L64", "her coat over my feet", still(local(SEAT_ME, YAW_ME, 0.9, 0.9, 0.9), local(SEAT_ME, YAW_ME, 0.55, 0, 0.1), 30), hand=0.004)
shot("L65", "high: me, Ines, the stair winding down", still([-0.2, -0.4, 10.4], [-1.9, 1.2, 6.8], 22))
shot("L66", "POV down the sunlit well: empty", still([-0.8, -0.9, 8.7], [0.0, 1.8, 0.2], 24), hand=0.004)
shot("L67", "close on me, understanding", still(local(SEAT_ME, YAW_ME, 1.7, -0.3, 1.3), local(SEAT_ME, YAW_ME, 0, 0, 0.9), 32))
def up(p, dz):
    return [p[0], p[1], round(p[2] + dz, 3)]


shot("L68", "memory: me walking down asleep, eyes shut, toward camera",
     c([0, up(tread(39.2, 1.3), 1.55), up(tread(42.9, 1.6), 1.4), 26], [1, up(tread(39.2, 1.3), 1.55), up(tread(41.3, 1.6), 1.4), 28]),
     hand=0.004)
shot("L69", "memory: the Upward's crown face below the sleeping me",
     still([0.3, 0.5, 11.4], [-1.15, 1.15, 8.7], 20), hand=0.004)
shot("L70", "memory: me walking past her blue door, eyes shut",
     still(up(tread(45.0, 1.5), 1.55), up(tread(48.2, 1.7), 1.4), 24), hand=0.004)
shot("L71", "memory: Ines frightened, phone glow", still([0.1, 0.55, Z4 + 1.55], [2.0, 0.55, Z4 + 1.4], 30))
shot("L72", "memory: Ines worried and soft, me waking at the rail", still([-0.3, 0.0, Z4 + 1.6], [1.9, 0.0, Z4 + 1.3], 26))
shot("L73", "dawn: Ines asleep in the blanket in the sun",
     still(local(SEAT_IN, YAW_IN, 1.9, -0.3, 1.3), local(SEAT_IN, YAW_IN, 0, 0, 0.88), 32))
shot("L74", "Ines opens her eyes, a small smile, lifts her phone",
     still(local(SEAT_IN, YAW_IN, 1.8, 0.0, 1.3), local(SEAT_IN, YAW_IN, 0, 0, 0.9), 32))
shot("L75", "close on me grinning at my phone", still(local(SEAT_ME, YAW_ME, 1.7, 0.0, 1.3), local(SEAT_ME, YAW_ME, 0, 0, 0.9), 32))
shot("L76", "two-shot across the well in full sun: both faces", still([0.5, -0.4, 9.0], [-2.1, 0.6, 8.7], 28))

shots = []
rain_shots = []
for i, sh in enumerate(SHOTS):
    s = {"id": f"S{i + 1:02d}", "cam": sh["cam"], "hand": sh["hand"], "step": sh["step"], "what": sh["what"]}
    if i:
        s["at"] = sh["at"]
    if sh["rain"]:
        rain_shots.append(s["id"])
    shots.append(s)

# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "sit": False, "blink": True}
acting = {"me": [], "ines": []}


def put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, "hidden": False, **NEUTRAL,
                 "expr": "worried" if who == "me" else "neutral", **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": pos, **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def talk(who, a, b):
    acting[who].append({"from": a, "to": b, "mouth": [0.5, 0.5], "flap": True})


FACE_IN = -90        # yaw facing the well from az 0 (facing -x)
ME_R = lambda n: [1.62, 0.0, n * RISE]   # me at the rail on turn n
SEAT_K = lambda y: [KX, y, -0.06]        # a kitchen seat (the seat is 0.45 m up, the sitting rig's hips at 0.17)
TAKEN = {}


def at_rail(n, at, **kw):
    kw = {"lean": 13, "head": [0, 24], "expr": "scared", "arms": [0, 0], **kw}
    put("me", at, ME_R(n), yaw=FACE_IN, **kw)


# me
put("me", 0, [-1.3, 0.55, LF + 0.01], yaw=0, sit=True, lean=-6, arms=[60, 60], head=[0, 22], expr="worried")   # S01 in the cot
hide("me", "L02")
put("me", "L04", [0.8, 3.9, 0], yaw=180, expr="smirk")
hide("me", "L05")
hide("me", "L06")
hide("me", "L07")
put("me", "L08", [0.2, 2.0, LF], yaw=180, expr="worried")
at_rail(7, "L09", head=[0, 30], lean=6, expr="worried")
hide("me", "L10")
put("me", "L13", [2.0, 0.1, Z7], yaw=90, arms=[0, 88], expr="worried")
hide("me", "L13>-0.35")
put("me", "L14>-0.3", [-1.3, 0.55, LF + 0.01], yaw=0, sit=True, lean=-8, head=[0, 8], expr="asleep", blink=False)
put("me", "L15", [-0.7, -0.6, LF], yaw=0, head=[0, 22], arms=[64, 64], expr="worried")
at_rail(7, "L16", head=[0, 28], arms=[0, 20])
hide("me", "L17")
put("me", "L21", tread(82), yaw=yaw_to(tread(82), tread(83)), expr="scared")
walk("me", "L21+0.5", tread(84, 1.9))
walk("me", "L21+0.85", [2.3, 0.0, Z7], arms=[0, 40])
hide("me", "L21.1")
put("me", "L22", [-1.3, 0.55, LF + 0.01], yaw=0, sit=True, lean=-6, arms=[60, 60], head=[0, 20], expr="scared")
put("me", "L24", [-0.3, -1.15, LF], yaw=0, expr="worried")
hide("me", "L25")
put("me", "L26", SEAT_K(-0.75), yaw=180, sit=True, expr="worried", head=[0, 8])
key("me", "L29", head=[-75, 6], blend=0.4)
key("me", "L30", head=[0, 12], blend=0.4)
put("me", "L32", [-1.3, 0.55, LF + 0.01], yaw=0, sit=True, lean=-6, arms=[60, 60], head=[0, 22], expr="worried")
key("me", "L33", expr="wide", blend=0.1)
at_rail(6, "L34", head=[0, 26])
hide("me", "L35")
put("me", "L37", tread(76), yaw=yaw_to(tread(76), tread(77)), expr="scared")
walk("me", "L37+0.45", tread(80))
walk("me", "L37+0.9", tread(84, 1.9))
walk("me", "L37+1.15", [2.3, 0.0, Z7])
hide("me", "L37.1")
put("me", "L38", [-0.3, -1.15, LF], yaw=0, expr="worried")
put("me", "L39", SEAT_K(-0.75), yaw=180, sit=True, expr="worried", head=[0, 8])
put("me", "L41", [-1.3, 0.55, LF + 0.01], yaw=0, sit=True, lean=-4, head=[0, 10], arms=[0, 0], expr="worried")
key("me", "L41.2", expr="shut", head=[0, 30], blend=0.5)
at_rail(5, "L42", head=[0, 26])
hide("me", "L43")
put("me", "L47", [-1.3, 0.55, LF + 0.01], yaw=0, sit=True, lean=-6, head=[0, 10], expr="asleep", blink=False)
key("me", "L47.1", expr="wide", blend=0.1)
at_rail(4, "L48", head=[0, 30], lean=18, expr="wide", blink=False)
hide("me", "L49")
at_rail(4, "L52", head=[0, 22], lean=10, expr="terrified", blink=False, arms=[40, 40])
hide("me", "L53")
def arc(who, at, i0, i1, dur, r=1.8, n=4, **kw):
    """Walk the spiral, not the chord across the well: n keys along the treads from i0 to i1."""
    for k in range(1, n + 1):
        walk(who, f"{at}+{round(dur * k / n, 3)}", tread(i0 + (i1 - i0) * k / n, r), **kw)


put("me", "L54", tread(48, 1.8), yaw=yaw_to(tread(48), tread(49)), expr="terrified")
arc("me", "L54", 48, 49.2, 0.35, n=2)
put("me", "L54.1", tread(61, 1.8), yaw=yaw_to(tread(61), tread(62)), expr="terrified")
arc("me", "L54.1", 61, 62.8, 0.8)
put("me", "L54.2", tread(73, 1.8), yaw=yaw_to(tread(73), tread(74)), expr="terrified")
arc("me", "L54.2", 73, 74.8, 0.76)
hide("me", "L54.3")
put("me", "L55", SEAT_K(-0.75), yaw=180, sit=True, expr="worried", head=[0, 8])
key("me", "L56", head=[0, 8])
hide("me", "L57")
put("me", "L58", [-1.3, 0.55, LF + 0.01], yaw=0, sit=True, lean=-4, head=[0, 8], expr="wide", blink=False)
put("me", "L59", [-1.3, 0.55, LF + 0.01], yaw=0, sit=True, lean=-8, head=[0, 10], expr="asleep", blink=False)
put("me", "L60", SIT_ME, yaw=YAW_ME, sit=True, lean=8, head=[0, 18], expr="asleep", blink=False)
key("me", "L60+0.9", expr="wide", head=[0, 8], blend=0.3)
key("me", "L61", expr="worried", blend=0.2)
key("me", "L67", expr="wide", head=[24, 26], blend=0.4)
put("me", "L68", tread(43.0, 1.7), yaw=yaw_to(tread(43), tread(42)), arms=[38, 38], expr="shut", blink=False)
arc("me", "L68", 43.0, 41.2, 3.5, r=1.7, n=5, arms=[38, 38])
put("me", "L69", tread(41, 1.7), yaw=yaw_to(tread(41), tread(40)), arms=[78, 78], expr="shut", blink=False)
put("me", "L70", tread(50, 1.7), yaw=yaw_to(tread(50), tread(49)), arms=[38, 38], expr="shut", blink=False)
arc("me", "L70", 50, 46.5, 1.67, r=1.7, n=4, arms=[38, 38])
put("me", "L72", tread(47, 1.55), yaw=FACE_IN - 20, expr="shut", blink=False, lean=8, head=[0, 20])
key("me", "L72.2", expr="wide", blend=0.2)
put("me", "L73", SIT_ME, yaw=YAW_ME, sit=True, lean=8, head=[0, 10], expr="worried")
put("me", "L75", SIT_ME, yaw=YAW_ME, sit=True, lean=4, head=[0, 12], arms=[40, 40], expr="warm", blink=False)
key("me", "L76", head=[14, 6], expr="warm")

# Ines
hide("ines", 0)
put("ines", "L04", [-0.8, 3.9, 0], yaw=180, expr="smirk")
hide("ines", "L05")
put("ines", "L07", [1.9, 0.0, Z4], yaw=FACE_IN, expr="smirk", head=[0, 4])
hide("ines", "L07.2")
put("ines", "L10", [KX - 1.3, 0.4, 0], yaw=90, arms=[0, 150], head=[0, 8], expr="neutral")
put("ines", "L11", [0.0, -1.7, 0], yaw=180, head=[0, -38], expr="worried")
hide("ines", "L12")
put("ines", "L26", SEAT_K(0.95), yaw=0, sit=True, expr="neutral", arms=[28, 28], head=[0, 4])
talk("ines", "L26.1", "L26>")
key("ines", "L27", expr="worried", head=[0, 6])
key("ines", "L27.1", look=[0, 0.9], head=[0, 18], blend=0.2)
key("ines", "L27.1+0.75", look=[0, 0], expr="soft", head=[0, 4], blend=0.3)
key("ines", "L28", look=[0, 0], expr="neutral")
hide("ines", "L31")
put("ines", "L39", SEAT_K(0.95), yaw=0, sit=True, expr="neutral", arms=[40, 40], head=[0, 4])
talk("ines", "L39", "L39>")
key("ines", "L40", expr="worried", head=[0, 6])
key("ines", "L40.1", look=[0, 0.9], head=[0, 18], blend=0.2)
key("ines", "L40.1+0.5", look=[0, 0], expr="soft", head=[0, 4], blend=0.3)
hide("ines", "L41")
put("ines", "L55", SEAT_K(0.95), yaw=0, sit=True, expr="neutral", head=[0, 6])
put("ines", "L56", SEAT_K(0.95), yaw=0, sit=True, expr="neutral", head=[0, 6])
key("ines", "L56.1", sit=False, blend=0.1)
walk("ines", "L56.1+0.7", [KX + 0.62, -0.15, 0])
put("ines", "L56.1+0.75", [KX + 0.62, -0.55, -0.06], yaw=180, sit=True, expr="neutral", head=[0, 6])
put("ines", "L57", [1.8, 0.0, Z4], yaw=yaw_to([1.8, 0.0], [0.0, -0.75]), expr="warm", head=[0, 2], arms=[30, 30], blink=False)
hide("ines", "L58")
put("ines", "L62", [2.0, 0.0, Z4], yaw=FACE_IN, expr="neutral")
hide("ines", "L62+0.2")
put("ines", "L63", SIT_IN, yaw=YAW_IN, sit=True, expr="asleep", blink=False, head=[0, 6], lean=4)
put("ines", "L68", SIT_IN, yaw=YAW_IN, sit=True, expr="asleep", blink=False)
hide("ines", "L69")
put("ines", "L71", [2.0, 0.55, Z4], yaw=FACE_IN, expr="scared", arms=[0, 66], head=[0, 14])
key("ines", "L72", expr="worried", blend=0.2)
key("ines", "L72.2", expr="soft", blend=0.4)
put("ines", "L73", SIT_IN, yaw=YAW_IN, sit=True, expr="asleep", blink=False, head=[0, 6], lean=4)
key("ines", "L74", expr="smirk", blend=0.2)
key("ines", "L74.1", arms=[0, 70], blend=0.3)
put("ines", "L75", SIT_IN, yaw=YAW_IN, sit=True, expr="smirk", arms=[0, 70], head=[0, 8])
put("ines", "L76", SIT_IN2, yaw=YAW_IN2, sit=True, expr="warm", arms=[0, 70], head=[-16, 8], blink=False)

# ---------------------------------------------------------------------------------------------------- cues
# the Upward: found where it stands, never seen moving. face = which way the top of its picture points (the way
# the camera looks along the floor, so its eyes read above its mouth)
FIG = lambda n: [1.6, 0.0, n * RISE]
cues = [
    # the light
    {"at": 0, "name": "mode", "set": "night"},
    {"at": "L04", "name": "mode", "set": "day", "dur": 0.4},
    {"at": "L14", "name": "mode", "set": "night", "dur": 0.8},
    {"at": "L24", "name": "mode", "set": "day", "dur": 0.8},
    {"at": "L31", "name": "mode", "set": "night", "dur": 0.8},
    {"at": "L38", "name": "mode", "set": "day", "dur": 0.8},
    {"at": "L41", "name": "mode", "set": "night", "dur": 0.8},
    {"at": "L54", "name": "mode", "set": "run", "dur": 0.3},
    {"at": "L54.3", "name": "mode", "set": "night", "dur": 0.3},
    {"at": "L55", "name": "mode", "set": "day", "dur": 0.8},
    {"at": "L57", "name": "mode", "set": "doorlamp", "dur": 0.6},
    {"at": "L58", "name": "mode", "set": "night", "dur": 0.6},
    {"at": "L60", "name": "mode", "set": "gold", "dur": 2.0},
    {"at": "L68", "name": "mode", "set": "memory", "dur": 0.8},
    {"at": "L72.2", "name": "mode", "set": "gold", "dur": 1.6},
    # the phone: the glow comes on over 0.5 s, fades over 0.6 s
    {"at": 0.0, "name": "phone", "on": 1.9, "dur": 0.4, "pos": [-1.3, 0.2, LF + 0.98], "color": "#cfe9e0"},
    {"at": "L02", "name": "phone", "on": 0.0, "dur": 0.0},
    {"at": "L15", "name": "phone", "on": 1.0, "dur": 0.5, "pos": [-0.7, -0.95, LF + 1.22], "color": "#cfe9e0"},
    {"at": "L16", "name": "phone", "on": 0.0, "dur": 0.0},
    {"at": "L22", "name": "phone", "on": 1.0, "dur": 0.5, "pos": [-1.3, 0.2, LF + 0.98], "color": "#cfe9e0"},
    {"at": "L23+0.2", "name": "phone", "on": 0.0, "dur": 0.6},
    {"at": "L32", "name": "phone", "on": 1.0, "dur": 0.5, "pos": [-1.3, 0.2, LF + 0.98], "color": "#cfe9e0"},
    {"at": "L34", "name": "phone", "on": 0.0, "dur": 0.0},
    {"at": "L47", "name": "phone", "on": 0.45, "dur": 1.6, "pos": [-1.3, 0.2, LF + 0.98], "color": "#7fa6e8"},
    {"at": "L48", "name": "phone", "on": 0.0, "dur": 0.0},
    {"at": "L52", "name": "phone", "on": 1.0, "dur": 0.4, "pos": [1.45, -0.05, Z4 + 1.0], "color": "#cfe9e0"},
    {"at": "L54", "name": "phone", "on": 0.0, "dur": 0.0},
    {"at": "L71", "name": "phone", "on": 0.7, "dur": 0.5, "pos": [2.0, 0.45, Z4 + 1.0], "color": "#cfe9e0"},
    {"at": "L72.2", "name": "phone", "on": 0.0, "dur": 0.8},
    {"at": "L75", "name": "phone", "on": 0.5, "dur": 0.4, "pos": local(SEAT_ME, YAW_ME, 0.3, 0.0, 1.0), "color": "#fff2d8"},
    {"at": "L76", "name": "phone", "on": 0.0, "dur": 0.0},
    # the torch (gain = (distance / 2) squared so the far figure is lit as the near one)
    {"at": 0, "name": "torch", "on": 0.0, "from": [0, 0, 20], "aim": [0, 0, 0]},
    {"at": "L13>-0.35", "name": "torch", "on": 1.0, "from": [0.8, 0.34, 16.34], "aim": PLATE_C, "gain": 0.45, "spill": 0.0},
    {"at": "L14>-0.3", "name": "torch", "on": 0.0, "from": [0.8, 0.34, 16.34], "aim": PLATE_C, "dur": 0.0, "gain": 0.45, "spill": 0.0},
    {"at": "L16", "name": "torch", "on": 1.0, "dur": 0.5, "from": [1.45, 0.0, Z7 + 1.05], "aim": [0.8, 0.0, Z7 - 6.0],
     "gain": 0.4, "spill": 1.0},
    {"at": "L17", "name": "torch", "on": 1.0, "from": [1.3, 0.0, Z7 + 1.55], "aim": [0.0, 1.55, 1.2], "gain": 29.0, "spill": 0.0, "spot": 7, "blend": 0.15},
    {"at": "L21", "name": "torch", "on": 0.0, "from": [1.3, 0.0, Z7 + 1.55], "aim": [0.0, 1.55, 1.2], "gain": 29.0, "dur": 0.2},
    {"at": "L21.1", "name": "torch", "on": 1.0, "from": [0.8, 0.34, 16.34], "aim": PLATE_C, "gain": 0.45, "spill": 0.0},
    {"at": "L22", "name": "torch", "on": 0.0, "from": [0.8, 0.34, 16.34], "aim": PLATE_C, "gain": 0.45, "dur": 0.0},
    {"at": "L34", "name": "torch", "on": 1.0, "dur": 0.5, "from": [1.45, 0.0, Z6 + 1.05], "aim": [0.8, 0.0, Z6 - 6.0], "gain": 0.4, "spill": 1.0},
    {"at": "L35", "name": "torch", "on": 1.0, "from": [1.3, 0.0, Z6 + 1.55], "aim": [1.6, 0.0, RISE + 1.0], "gain": 15.5, "spill": 0.0, "spot": 9, "blend": 0.15},
    {"at": "L37", "name": "torch", "on": 0.0, "from": [1.3, 0.0, Z6 + 1.55], "aim": [1.6, 0.0, RISE + 1.0], "gain": 15.5, "dur": 0.2},
    {"at": "L37.1", "name": "torch", "on": 1.0, "from": [0.8, 0.34, 16.34], "aim": PLATE_C, "gain": 0.45, "spill": 0.0},
    {"at": "L38", "name": "torch", "on": 0.0, "from": [0.8, 0.34, 16.34], "aim": PLATE_C, "gain": 0.45, "dur": 0.0},
    {"at": "L41", "name": "torch", "on": 0.5, "dur": 0.5, "from": [-1.3, 0.1, LF + 0.95], "aim": [-1.3, -2.5, LF + 0.7], "gain": 0.15, "spill": 0.5},
    {"at": "L42", "name": "torch", "on": 1.0, "dur": 0.5, "from": [1.45, 0.0, Z5 + 1.05], "aim": [0.8, 0.0, Z5 - 6.0], "gain": 0.4, "spill": 1.0},
    {"at": "L43", "name": "torch", "on": 1.0, "from": [1.3, 0.0, Z5 + 1.55], "aim": [1.6, 0.0, 2 * RISE + 1.0], "gain": 4.1, "spill": 0.0, "spot": 14, "blend": 0.2},
    {"at": "L47", "name": "torch", "on": 0.0, "from": [1.3, 0.0, Z5 + 1.55], "aim": [1.6, 0.0, 2 * RISE + 1.0], "gain": 4.1, "dur": 0.0},
    {"at": "L48", "name": "torch", "on": 1.0, "dur": 0.5, "from": [1.45, 0.0, Z4 + 1.05], "aim": [0.8, 0.0, Z4 - 6.0], "gain": 0.4, "spill": 1.0},
    {"at": "L49", "name": "torch", "on": 1.0, "from": [1.3, 0.0, Z4 + 1.55], "aim": [-1.0, 0.0, Z4 + 1.0], "aim_to": [1.6, 0.0, 5.0],
     "aim_dur": 0.9, "gain": 1.2, "spill": 0.0},
    {"at": "L50", "name": "torch", "on": 1.0, "from": [1.3, 0.0, Z4 + 1.55], "aim": [1.6, 0.0, 3 * RISE + 1.5], "gain": 0.4, "spill": 0.0},
    {"at": "L52", "name": "torch", "on": 1.0, "from": [1.45, 0.0, Z4 + 1.05], "aim": [1.6, 0.0, 3 * RISE + 1.0], "gain": 0.5, "spill": 0.8},
    {"at": "L53", "name": "torch", "on": 1.0, "from": [1.3, 0.0, Z4 + 1.55], "aim": [1.6, 0.0, 3 * RISE + 1.5], "gain": 0.4, "spill": 0.0},
    {"at": "L54", "name": "torch", "on": 0.0, "from": [1.3, 0.0, Z4 + 1.55], "aim": [1.6, 0.0, 3 * RISE + 1.5], "dur": 0.1, "gain": 1.0},
    {"at": "L54.3", "name": "torch", "on": 1.0, "from": [0.8, 0.34, 16.34], "aim": PLATE_C, "gain": 0.45, "spill": 0.0},
    {"at": "L55", "name": "torch", "on": 0.0, "from": [0.8, 0.34, 16.34], "aim": PLATE_C, "gain": 0.45, "dur": 0.0},
    # the Upward, seen only from above and only nearer each time
    {"at": 0, "name": "up", "hidden": True},
    {"at": "L17", "name": "up", "pos": [0.0, 1.55, 0.0], "face": 130, "mouth": 0},
    {"at": "L21", "name": "up", "hidden": True},
    {"at": "L35", "name": "up", "pos": FIG(1), "face": 0, "mouth": 0},
    {"at": "L36", "name": "up", "pos": FIG(1), "face": 0, "mouth": 1},
    {"at": "L37", "name": "up", "hidden": True},
    {"at": "L43", "name": "up", "pos": FIG(2), "face": 0, "mouth": 2},
    {"at": "L47", "name": "up", "hidden": True},
    {"at": "L50", "name": "up", "pos": FIG(3), "face": 0, "mouth": 2},
    {"at": "L51", "name": "up", "pos": FIG(3), "face": 0, "mouth": 3},
    {"at": "L54", "name": "up", "hidden": True},
    {"at": "L69", "name": "up", "pos": tread(40, 1.7), "face": 156, "mouth": 1, "rim": 0.0},
    {"at": "L70", "name": "up", "hidden": True},
    # the treads the view down the well needs gone
    {"at": 0, "name": "clear", "az": None},
    {"at": "L13>-0.35", "name": "clear", "az": 0, "span": 40, "z0": 99, "z1": 99, "rails": [15.3, 17.0]},
    {"at": "L14>-0.3", "name": "clear", "az": None},
    {"at": "L17", "name": "clear", "az": 60, "span": 100, "z0": 2.0, "z1": 15.6, "rails": [Z7 - 0.2, Z7 + 1.7], "rail_az": 60, "rail_span": 110},
    {"at": "L21", "name": "clear", "az": None},
    {"at": "L21.1", "name": "clear", "az": 0, "span": 40, "z0": 99, "z1": 99, "rails": [15.3, 17.0]},
    {"at": "L22", "name": "clear", "az": None},
    {"at": "L35", "name": "clear", "az": 0, "span": 55, "z0": RISE + 0.8, "z1": Z6 + 0.4, "rails": [Z6 - 0.2, Z6 + 1.7], "rail_span": 70},
    {"at": "L37", "name": "clear", "az": None},
    {"at": "L37.1", "name": "clear", "az": 0, "span": 40, "z0": 99, "z1": 99, "rails": [15.3, 17.0]},
    {"at": "L38", "name": "clear", "az": None},
    {"at": "L43", "name": "clear", "az": 0, "span": 55, "z0": 2 * RISE + 0.8, "z1": Z5 + 0.4, "rails": [Z5 - 0.2, Z5 + 1.7], "rail_span": 70},
    {"at": "L47", "name": "clear", "az": None},
    {"at": "L49", "name": "clear", "az": 0, "span": 55, "z0": 3 * RISE + 0.6, "z1": Z4 + 0.5, "rails": [Z4 - 0.5, Z4 + 0.9], "rail_span": 70},
    {"at": "L54", "name": "clear", "az": 25, "span": 75, "z0": 10.5, "z1": 11.6},
    {"at": "L54.1", "name": "clear", "az": 55, "span": 80, "z0": 12.8, "z1": 14.2},
    {"at": "L54.2", "name": "clear", "az": 55, "span": 80, "z0": 15.0, "z1": 16.3},
    {"at": "L54.3", "name": "clear", "az": 0, "span": 40, "z0": 99, "z1": 99, "rails": [15.3, 17.0]},
    {"at": "L55", "name": "clear", "az": None},
    {"at": "L57", "name": "clear", "az": 0, "span": 45, "z0": Z4 + 1.5, "z1": Z4 + 3.4, "rails": [Z4 - 0.5, Z4 + 1.8], "rail_span": 75},
    {"at": "L58", "name": "clear", "az": None},
    {"at": "L66", "name": "clear", "az": 90, "span": 40, "z0": 0.8, "z1": 7.0},
    {"at": "L67", "name": "clear", "az": None},
    {"at": "L69", "name": "clear", "az": 135, "span": 55, "z0": 8.6, "z1": 12.5, "rails": [6.6, 10.5], "rail_az": 135, "rail_span": 90},
    {"at": "L70", "name": "clear", "az": None},
    {"at": "L76", "name": "clear", "az": 150, "span": 0, "z0": 99, "z1": 99, "rails": [6.6, 9.4], "rail_az": 165, "rail_span": 75},
    # the bolt, Ines's door, the sand, the coat and the blanket
    {"at": 0, "name": "bolt", "open": 1.0, "dur": 0.0},
    {"at": "L14+0.15", "name": "bolt", "open": 0.0, "dur": 0.45},
    {"at": "L15", "name": "bolt", "open": 1.0, "dur": 0.0},
    {"at": "L21.1", "name": "bolt", "open": 1.0, "dur": 0.0},
    {"at": "L21.1+0.2", "name": "bolt", "open": 0.0, "dur": 0.45},
    {"at": "L24", "name": "bolt", "open": 1.0, "dur": 0.0},
    {"at": "L37.1", "name": "bolt", "open": 1.0, "dur": 0.0},
    {"at": "L37.1+0.2", "name": "bolt", "open": 0.0, "dur": 0.45},
    {"at": "L38", "name": "bolt", "open": 1.0, "dur": 0.0},
    {"at": "L54.3", "name": "bolt", "open": 1.0, "dur": 0.0},
    {"at": "L54.3+0.15", "name": "bolt", "open": 0.0, "dur": 0.4},
    {"at": "L55", "name": "bolt", "open": 1.0, "dur": 0.0},
    {"at": 0, "name": "door", "open": 0.0, "glow": 0.0, "dur": 0.0},
    {"at": "L47", "name": "door", "open": 14.0, "glow": 0.7, "dur": 0.6},
    {"at": "L55", "name": "door", "open": 0.0, "glow": 0.0, "dur": 0.0},
    {"at": "L57", "name": "door", "open": 55.0, "glow": 0.8, "dur": 0.0},
    {"at": "L58", "name": "door", "open": 0.0, "glow": 0.0, "dur": 0.0},
    {"at": "L62", "name": "door", "open": 85.0, "glow": 0.5, "dur": 0.0},
    {"at": "L62+0.2", "name": "door", "open": 85.0, "glow": 0.5, "dur": 0.0},
    {"at": "L70", "name": "door", "open": 60.0, "glow": 0.5, "dur": 0.0},
    {"at": "L73", "name": "door", "open": 85.0, "glow": 0.5, "dur": 0.0},
    {"at": 0, "name": "sand", "level": 0},
    {"at": "L24", "name": "sand", "level": 1},
    {"at": "L38", "name": "sand", "level": 2},
    {"at": "L41", "name": "sand", "level": 3},
    {"at": 0, "name": "coat", "where": "off"},
    {"at": "L57", "name": "coat", "where": "worn"},
    {"at": "L58", "name": "coat", "where": "off"},
    {"at": "L64-0.2", "name": "coat", "where": "feet", "pos": local(SEAT_ME, YAW_ME, 0.2, 0.0, 0.27), "yaw": YAW_ME},
    {"at": 0, "name": "blanket", "state": "none"},
    {"at": "L57", "name": "blanket", "state": "arm"},
    {"at": "L58", "name": "blanket", "state": "none"},
    {"at": "L63", "name": "blanket", "state": "wrap"},
]
# the coat's pose key uses "yaw" in degrees (the box's local y is its length, along the way I face)

# ---------------------------------------------------------------------------------------------------- sound
NIGHT_SPANS = [(0, "L04"), ("L14", "L24"), ("L31", "L38"), ("L41", "L55"), ("L57", "L60")]
DAY_SPANS = [("L04", "L14"), ("L24", "L31"), ("L38", "L41"), ("L55", "L57")]
ambience = [{"kind": "water", "from": 0, "to": "end", "lufs": -34}]
for a, b in NIGHT_SPANS:
    ambience.append({"kind": "wind", "from": a, "to": b, "lufs": -30})
    ambience.append({"kind": "rain", "from": a, "to": b, "lufs": -32})
for a, b in DAY_SPANS:
    ambience.append({"kind": "wind", "from": a, "to": b, "lufs": -40})
ambience.append({"kind": "wind", "from": "L60", "to": "end", "lufs": -40})


def buzz(at, db=-14, keep=False):
    e = {"at": at, "kind": "knock", "pattern": [0, 0.11, 0.22], "tone": "soft", "db": db}
    if keep:
        e["keep"] = True
    return e


sfx = [
    buzz("L01+0.05"), buzz("L15"), buzz("L32"), buzz("L42"), buzz("L52", keep=True), buzz("L75", -20),
    {"at": "L14+0.2", "kind": "click", "db": -10},
    {"at": "L21.1+0.3", "kind": "click", "db": -10},
    {"at": "L37.1+0.3", "kind": "click", "db": -10},
    {"at": "L54.3+0.25", "kind": "click", "db": -10},
    {"at": "L31b.2", "kind": "creak", "db": -18, "dur": 1.4},
    {"at": "L49", "kind": "riser", "db": -24, "dur": 1.2},
    {"at": "L50+0.2", "kind": "sting", "db": -8, "dur": 1.2, "keep": True},
    {"at": "L58.1", "kind": "door", "db": -22},
    {"at": "L76.1", "kind": "bell", "db": -12, "hz": 392.0, "dur": 3.0},
    {"at": "L76.1+0.2", "kind": "bell", "db": -12, "hz": 294.0, "dur": 3.0},
]

story = {
    "slug": "ep28-lamp-room",
    "title": "Every night in the lighthouse, her text asked who was on the stairs.",
    "made_for_kids": False,
    "premise": "On a first trip away together, a month in, Ines and I rent an old lighthouse for a stormy February week. She sleeps halfway up and I sleep in the lamp room at the top. Every night her text wakes me and I'm at the stair rail, and at the foot of the stairs a figure in a yellow oilskin looks straight up at me with its face on the top of its head. Each night it's nearer.",
    "twist": "The one on the stairs was me. I sleepwalk a turn further down toward the storm door every night while the oilskin figure comes up a turn each time I come down, and Ines has been texting only to wake me. The last text, her old question as a joke, is answered with one word: us.",
    "world": "a whitewashed lighthouse let as a cottage on a grassy sea cliff in a February storm: a tight stone spiral stair round a deep well, an iron rail, a sea-blue bedroom door halfway up, the dead lens in the glass lamp room at the top",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#6fe3c8",
    "caption": {"ink": "#08090d", "stroke_add": 2, "shadow": 0.8},
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#202838", "fog_density": 0.02, "fog_start": 2.5, "sky": "#0d1220", "sky_strength": 1.0, "exposure": 0.0},
    "grade": {"shadows": [-0.02, 0.0, 0.05], "highlights": [0.025, 0.01, -0.02], "saturation": 0.95, "contrast": 1.08,
              "vignette": 0.34, "bloom": 0.25, "grain": 0.012, "red_line": 0.79},
    "rain_shots": rain_shots,
    "phonemes": {"Ines": "inˈɛs"},
    "homophones": {"too": "two"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 45, "mode": "phrygian", "bpm": 60, "seed": 28,
              "sections": [
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L41", "voices": ["drone", "pad", "pulse"], "energy": 0.45},
                  {"at": "L47", "voices": ["drone", "pad", "pulse"], "energy": 0.55},
                  {"at": "L55", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L59", "voices": ["pad"], "energy": 0.25},
                  {"at": "L60", "voices": ["pad", "piano"], "energy": 0.4, "mode": "major", "root": 48},
              ]},
    "sound": {"floor": "stone", "steps_db": -22, "ambience": ambience, "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "L50+0.3", "keep": ["sting"]}, {"from": "L52", "to": "L53"}]},
}
import re

_REF = re.compile(r"^(L\d+b?)\.(\d+)(.*)$")


def fix_ref(v):
    if isinstance(v, str):
        m = _REF.match(v)
        if m and m.group(1) in PHRASE_START:
            return f"{m.group(1)}.{PHRASE_START[m.group(1)][int(m.group(2))]}{m.group(3)}"
    return v


def fix_refs(o):
    if isinstance(o, dict):
        return {k: (fix_ref(v) if k in ("at", "from", "to") else fix_refs(v)) for k, v in o.items()}
    if isinstance(o, list):
        return [fix_refs(x) for x in o]
    return o


for k in ("shots", "cues", "acting", "sound"):
    story[k] = fix_refs(story[k])
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False))
print(f"{len(shots)} shots, {len(cues)} cues -> {OUT}")
