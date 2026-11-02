"""Writes ../story.json for ep27-towpath (writer's script.md round 1 revision, builder review round 2, 2026-11-02).

Run from anywhere: python stories/ep27-towpath/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and cameras, the acting,
the cues set.py reads (time of day, Moss, the Long Man, the hatch, the bolt, the wipe, the patch), the score and sound.

Places (set.py's metres): x along the canal from the boat's stern (0) to its bow (12); y across it, the towpath at
+y, the water at -y, the boat's towpath side at y = -0.15; z up (water 0, towpath 0.5, back deck 0.72, cabin
floor 0.05). A character with yaw 0 faces -y, yaw 90 faces +x, yaw -90 faces -x, yaw 180 faces +y.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
if lines[-1]["id"] != "P04":
    lines.append({"id": "P04", "pause": 0.25, "chunks": []})   # the loop beat: no words, the water carries on

HOLDS = {"P01": 0.7, "P02": 1.6, "P03": 1.7, "P04": 0.25}
for ln in lines:
    if ln["id"] in HOLDS:
        ln["pause"] = HOLDS[ln["id"]]

# spoken-only fixes for the word check (the captions don't change)
SPOKEN = {("L10", "So I'd step round her"): "So I'd step, round her", ("L24", "It lay there"): "It lay there.",
          ("L53", "I looked back."): "I looked, back.", ("L58", "one ring nearer"): "one ring nearer,", ("L58", "to lie there"): "to lie there,"}
for ln in lines:
    for ch in ln.get("chunks", []):
        if (ln["id"], ch[1]) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], ch[1])]

# lines a touch slower so a swallowed word comes through (the word check)
TEMPO = {"L10": 0.8, "L24": 1.0, "L53": 0.9, "L58": 0.8}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]

CHUNK_MAP = {}


def pieces(n):
    return {4: [2, 2], 5: [3, 2], 6: [3, 3], 7: [3, 2, 2], 8: [3, 3, 2]}.get(n, [n])


for ln in lines:
    if "pause" in ln:
        continue
    new, m = [], []
    for cap, spk in ln["chunks"]:
        cw, sw = cap.split(), spk.split()
        m.append(len(new))
        if len(cw) <= 3 or len(cw) != len(sw):
            new.append([cap, spk])
            continue
        i = 0
        for k in pieces(len(cw)):
            new.append([" ".join(cw[i:i + k]), " ".join(sw[i:i + k])])
            i += k
    ln["chunks"] = new
    CHUNK_MAP[ln["id"]] = m


def remap(v):
    """Time references written against the script's chunks, moved onto the split chunks."""
    if isinstance(v, str):
        mm = re.match(r"^(L\d+)\.(\d+)(.*)$", v)
        if mm and mm.group(1) in CHUNK_MAP:
            return f"{mm.group(1)}.{CHUNK_MAP[mm.group(1)][int(mm.group(2))]}{mm.group(3)}"
        return v
    if isinstance(v, list):
        return [remap(x) for x in v]
    if isinstance(v, dict):
        return {k: remap(x) for k, x in v.items()}
    return v


cast = {
    "me": {"age": "adult", "skin": "#e0b690", "shirt": "#7a705a", "pattern": "knit", "pattern_c": "#625a46",
           "pants": "#1f2a40", "shoes": "#2c2622", "sleeves": "long", "hair": "cap", "hair_c": "#6b4a2e",
           "hat": "beanie", "hat_c": "#1f4a4d",
           "face": {"eyes": "tired", "brows": True, "ink": "#1b1513"}},
    "longman": {"age": "adult", "skin": "#6f7352", "shirt": "#4d6638", "pattern": "solid", "pattern_c": "#34472a",
                "pants": "#6a4f33", "pants_pattern": "stripes", "pants_pattern_c": "#58402a", "shoes": "#6a4f33",
                "sleeves": "long", "hair": "cap", "hair_c": "#25321d", "hat": "none", "height": 1.0,
                "face": {"eyes": "round", "brows": False, "mouth": "line", "ink": "#0a0a0a", "pupil": "#050505"}},
}


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens, roll=0):
    return c([0, loc, tgt, lens, roll])


def move(a, b, lens_a, lens_b=None, roll=0):
    return c([0, a[0], a[1], lens_a, roll], [1, b[0], b[1], lens_b or lens_a, roll])


# ----------------------------------------------------------------------------------------------- the shots
S = []
LAMP = {}


EXTRA = {}


def shot(at, what, cam, step=2, lamp=None, **extra):
    S.append((at, what, step, cam))
    if extra:
        EXTRA[at] = extra
    if lamp:
        LAMP[at] = round(lamp * 0.4)


HOOK = move(([-11.5, -5.8, 4.3], [1.4, 0.7, 1.9]), ([-10.9, -5.8, 4.3], [1.4, 0.7, 1.9]), 75, 80)
HOOK_END = still([-10.9, -5.8, 4.3], [1.4, 0.7, 1.9], 80)
LONGSIDE = still([40.0, 3.0, 1.4], [14.0, -1.4, 0.6], 14)
WIDE_BOAT = still([-3.0, 5.5, 3.4], [9.0, 0.0, 0.8], 15)
RING_CAM = still([3.3, 2.3, 0.78], [5.0, 0.45, 0.8], 26)
WINDOW = still([5.0, -1.5, 1.06], [5.0, -0.1, 0.70], 30)

# 01 good morning
shot(0, "the hook: me at the hatch, face lit, the long dark line far up the towpath, empty grass by the back ring",
     HOOK, 2, 60, fogx=0.3)
shot("L02", "Moss's head at the low round window", still([8.5, -4.2, 1.0], [8.5, -1.95, 0.95], 26), 2, 350)
shot("L02.2", "side wide of the whole boat on still water", still([6, -9.5, 1.2], [6, -0.15, 1.2], 11))
shot("L03", "the past: me at the open hatch from below, smirk", still([4.6, -1.05, 1.25], [2.6, -1.05, 2.05], 32), 2, 300)
shot("L04", "the past: Moss on the top step", still([0.9, -1.05, 1.7], [2.5, -1.05, 0.6], 24))
shot("L04.1", "the past: Moss's landing in the grass beside the back deck", still([-1.6, 2.6, 1.0], [1.4, 0.8, 0.85], 26))
shot("L05", "the past, plant 1: Moss rolled in the worn patch by the back ring, chin up, the round window above", RING_CAM)
shot("L06", "the past: low from behind, me and Moss slow on the hedge side", still([-9.0, 3.9, 1.0], [0.0, 3.4, 1.0], 22))
shot("L07", "Moss in her bed, white muzzle on her paws", still([2.7, -1.5, 0.7], [4.05, -1.05, 0.25], 22))
shot("L08", "the three steps from Moss's eye level, empty, the hatch above", still([3.9, -1.05, 0.26], [2.3, -1.05, 0.6], 30))
shot("L09", "Moss in her bed looking up at me, tail up, me at the top step",
     still([5.2, -1.4, 0.55], [3.4, -1.05, 1.0], 20), 2, 150)
shot("L10", "high angle: my boots past her bed", still([6.6, -0.79, 1.89], [4.4, -1.4, 0.3], 15))
shot("L10.1", "me striding alone on the hedge side, upright", still([-6.5, 3.4, 1.2], [-1.0, 3.7, 1.35], 26), 2, 200)
shot("L11", "plant 2: the back ring under my bunk window, the grass grown in", still([4.0, 2.2, 0.95], [5.0, 0.35, 0.62], 30), 2, 500)

# 02 the first dawn
shot("L12", "me rising out of the hatch, worried", still([0.3, -1.05, 1.95], [2.6, -1.05, 1.95], 34), 2, 420)
shot("L13", "over my shoulder: three rings past the front and a long dark shape", still([0.4, 0.2, 2.3], [24, 0.3, 0.5], 28))
shot("L14", "a side view of it, too long to be a log", LONGSIDE)
shot("L15", "Moss sitting up, ears forward", still([2.5, -1.55, 0.75], [3.9, -1.05, 0.4], 24), 2, 150)
shot("L16", "me walking away on the hedge side, glancing back", still([-8.0, 3.2, 1.4], [-3.0, 3.6, 1.5], 30), 2, 300)
shot("L17", "the same view: the fog thins, the grass is empty", LONGSIDE)

# 03 the second dawn
shot("L18", "from the front of the boat: two rings, then its head", still([11.0, -0.8, 2.2], [20, 0.3, 0.6], 26))
shot("L19", "me crouched at the bow, scared", still([13.5, -1.0, 1.7], [10.8, -1.05, 2.1], 32), 2, 380)
shot("L20", "its head and shoulders, face up, eyes open", still([18.4, -1.3, 1.9], [19.0, 0.3, 0.7], 30))
shot("L21", "a slow pan along it", move(([16.6, -1.0, 1.2], [19.8, 0.3, 0.7]), ([16.6, -1.0, 1.2], [30, 0.3, 0.7]), 30))
shot("L22", "low along the towpath from its feet: the Long Man end to end and the boat beyond", still([34.0, 1.3, 2.0], [14.0, 0.0, 0.45], 18), 2, None, fogx=0.3, toplit=2500)
shot("L23", "the weed-green coat", still([21.5, -0.5, 1.25], [21.8, 0.3, 0.7], 34))
shot("L23.2", "the rope-brown trousers and a boot", still([26.0, -1.7, 1.5], [26.8, 0.3, 0.7], 26))
shot("L24", "straight down over its face", still([19.0, 0.3, 2.3], [19.0, 0.3, 0.7], 30))
shot("L25", "the beads on its cheek", still([18.92, 0.12, 2.0], [18.92, 0.12, 0.95], 70))
shot("L26", "low along the grass to its still face", still([19.7, 1.7, 0.72], [19.0, 0.3, 0.8], 34))
shot("L27", "Moss whining, one leg on the first step", still([4.9, -1.35, 0.4], [3.3, -1.05, 0.35], 30), 2, 150)
shot("L28", "Moss back on the cabin floor, looking up", still([5.0, -1.35, 0.5], [3.5, -1.05, 0.95], 22), 2, 150)

# 04 the third dawn
shot("L29", "my bunk, me sitting up in my beanie", still([4.0, -1.5, 1.35], [5.55, -0.62, 1.2], 22), 2, 150)
shot("L30", "me at the round window, side on", still([3.7, -0.9, 1.5], [5.45, -0.55, 1.5], 34), 2, 150)
shot("L31", "through the window: white fog, then the towpath comes clear", WINDOW)
shot("L32", "along the boat's side: its head at the front ring", still([4.2, 0.35, 0.95], [12.0, 0.3, 0.7], 24))
shot("L33", "my face at the window, worried", still([3.6, -1.6, 1.5], [5.2, -0.6, 1.45], 24), 2, 250)
shot("L34", "from the front ring: its head now on its side", still([14.6, -3.8, 2.8], [12.4, 0.3, 0.7], 26))
shot("L35", "the head turned flat while the chest stays face up", still([12.5, -1.7, 1.35], [12.2, 0.3, 0.75], 30))
shot("L36", "low behind its sideways head: the look runs along the grass to the back ring", still([13.6, 1.5, 1.7], [4.0, 0.2, 0.6], 24))
shot("L37", "the back ring and the grown-in grass under my window, my face small in the glass",
     still([3.0, 2.4, 1.0], [5.0, -0.05, 0.8], 28), 2, 400)
shot("L38", "night: the bolt from below", still([4.7, -0.9, 1.0], [3.2, -0.62, 1.95], 36), 2, 100)
shot("L38.2", "my hand at the end of my sleeve beside the bolt", still([5.2, -1.0, 1.5], [3.6, -0.85, 1.4], 22), 2, 150)
shot("L39", "Moss at the foot of the steps, watching the hatch", still([4.5, -1.05, 0.5], [3.0, -1.05, 1.5], 28), 2, 150)

# 05 the fourth dawn: the scare
shot("L40", "the bunk window from inside: white fog, beaded", WINDOW)
shot("L41", "me lying awake, the round window above me", still([4.2, -1.3, 1.25], [5.5, -0.6, 0.85], 30), 2, 150)
shot("L42", "close on the round window, white", still([5.0, -1.5, 0.98], [5.0, -0.1, 0.84], 52))
shot("L43", "my sleeve crossing the glass in a one second wipe", WINDOW)
shot("P01", "the wiped glass, white fog behind it", WINDOW, 1)
shot("L44", "two round eyes right behind the glass (the creature test)", WINDOW, 1)
shot("L45", "low along the towpath from its feet: it lies along the whole boat", still([24.0, 1.3, 2.0], [3.0, 0.0, 0.5], 18), 1, None, fogx=0.3, toplit=2500)
shot("L46", "its head by the back ring, face at the round window", still([2.2, 0.9, 1.15], [5.0, 0.1, 0.85], 30), 1)
shot("L47", "tight on me by the glass, its eyes beyond", still([5.7, -1.55, 1.0], [4.9, -0.2, 0.95], 30), 1, 250)
shot("L48", "its eyes through the glass, close", still([5.0, -1.5, 0.98], [5.0, -0.1, 0.84], 70, 90), 1)
shot("L49", "me turning from the window, two faint points behind me", still([3.6, -1.7, 1.5], [5.2, -0.6, 1.45], 22), 1, 250)
shot("L50", "Moss climbing", still([4.3, -1.25, 0.5], [3.4, -1.05, 0.25], 28), 1, 150)
shot("L51", "Moss on the first step, the bolted hatch above", still([4.5, -1.05, 0.5], [3.0, -1.05, 1.5], 28), 1, 150)
shot("L52", "Moss's face, ears up, eyes on the hatch", still([2.4, -1.25, 1.0], [3.3, -1.05, 0.85], 20), 1, 200)

# 06 the turn
shot("L53", "its head in the grass by the back ring, face up (L05's framing)", still([5.8, 0.65, 1.7], [5.0, 0.5, 0.8], 22))
shot("L54", "the past: Moss in the same grass, the same sky", RING_CAM)
shot("L55", "the grown-in grass in the present, its hair at the edge", still([2.4, 2.4, 0.95], [4.7, 0.4, 0.6], 30))
shot("L56", "outside wide: it lies along the boat, unchanged", WIDE_BOAT)
shot("L57", "Moss on the first step, looking up", still([4.7, -1.1, 0.55], [3.1, -1.05, 1.4], 22), 2, 150)
shot("L58", "high wide: the rings along the towpath, its head at the last", still([-4.0, 3.2, 3.6], [14.0, 0.0, 0.5], 22))
shot("L59", "my face at the window, the fear going", still([3.5, -1.55, 1.55], [5.3, -0.7, 1.5], 22), 2, 300)

# 07 her spot
shot("L60", "from below: the bolt", still([4.7, -0.9, 1.0], [3.2, -0.62, 1.95], 36), 2, 100)
shot("L60.1", "the hatch sliding open, the grey light easing in", still([5.2, -1.3, 0.9], [3.0, -1.05, 2.0], 30), 2, 100)
shot("L61", "me crouched at the foot of the steps by Moss", still([6.2, -0.5, 1.2], [4.4, -1.5, 1.0], 17), 2, 200)
shot("L61.2", "me rising out of the hatch with Moss against my chest", still([0.3, -1.05, 1.9], [2.45, -1.05, 2.0], 32), 2, 420)
shot("L62", "the back deck: me with Moss, and its face on the grass by the back ring",
     still([3.8, 4.6, 4.2], [3.7, -0.3, 0.8], 12), 2, 150)
shot("L63", "my face, Moss's head at my chin", still([1.5, -3.3, 2.25], [1.5, -1.3, 2.25], 34), 2, 350)
shot("P02", "wide over the canal: the fog thins, the willows come clear", still([-0.3, -1.0, 1.9], [6.0, -25, 1.2], 24))
shot("L64", "the towpath alongside the boat, the fog easing",
     move(([2.0, 3.0, 1.35], [8.0, 0.1, 0.55]), ([3.0, 3.0, 1.35], [9.0, 0.1, 0.55]), 28))
shot("L65", "the grass flattened in one long line, no one there",
     move(([3.0, 3.0, 1.35], [9.0, 0.1, 0.55]), ([4.0, 3.0, 1.35], [10.0, 0.1, 0.55]), 28))
shot("P03", "the lore plant: two strokes on the back ring", still([5.0, 0.62, 1.3], [5.0, 0.12, 0.6], 20))
shot("L66", "me stepping off the deck onto the towpath, Moss in my arms", still([-1.2, 3.8, 1.5], [1.8, 0.9, 1.1], 20), 2, 300)
shot("L66.1", "Moss set down on the grass by the ring", still([1.6, 3.8, 1.1], [5.0, 0.9, 0.7], 22), 2, 300)
shot("L67", "Moss rolled over, tail up, me crouched beside her", still([1.4, 3.6, 1.15], [5.0, 1.0, 0.75], 21), 2, 200)

# 08 her pace
shot("L68", "me at the open hatch in a clear morning, Moss in my arms",
     still([4.6, -1.05, 1.25], [2.6, -1.05, 2.05], 32), 2, 380)
shot("L69", "low from behind: me upright beside Moss on the hedge side, very slow",
     still([-5.2, 4.8, 1.2], [2.4, 3.2, 0.9], 22), 2, 200)
shot("L70", "side wide from the hedge: the two of us small on the long towpath",
     still([3.0, 6.8, 1.5], [3.0, 2.0, 1.0], 20))
shot("L71", "Moss's face, ears soft, looking ahead", still([5.0, 4.4, 1.15], [3.1, 3.1, 1.1], 34), 2, 200)
shot("L72", "the last shot: S01's camera, me on the stern deck, Moss rolled chin-up in the grass by the back ring", HOOK, 2, 80, fogx=0.3)

S[:] = [(at, what, step, cam) for at, what, step, cam in S]

shots = []
for i, (at, what, step, cam) in enumerate(S):
    s = {"id": f"S{i + 1:02d}", "cam": cam, "hand": 0.004, "step": step, "what": what}
    if i:
        s["at"] = at
    if at in EXTRA:
        s.update(EXTRA[at])
    if at in LAMP:
        s["lamp"] = LAMP[at]
    shots.append(s)

# ---------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "lie": None, "blink": True}
acting = {"me": [], "longman": []}


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


STEP0, STEP1, STEP2 = [2.6, -1.05, 0.54], [2.95, -1.05, 0.36], [3.3, -1.05, 0.2]
BUNK = [5.55, -0.62, -0.06]

# me
put("me", 0, [0.6, -0.5, 0.72], yaw=-60, expr="neutral", head=[0, 6])
key("me", "L02>", hidden=True, blend=0)
put("me", "L03", STEP0, yaw=90, head=[0, 22], expr="smirk")
hide("me", "L04")
put("me", "L06", [-2.2, 3.7, 0.5], yaw=90, expr="smirk", head=[0, 12])
walk("me", "L06+3.0", [3.4, 3.7, 0.5], expr="smirk", head=[0, 12])
hide("me", "L07")
put("me", "L09", STEP0, yaw=90, head=[0, 24], expr="neutral")
talk("me", "L09", "L09.1>")
put("me", "L10", [5.3, -1.62, 0.05], yaw=-90, expr="neutral")
walk("me", "L10+1.4", [3.3, -1.62, 0.05], expr="neutral")
hide("me", "L10.1")
put("me", "L10.1", [-2.0, 3.7, 0.5], yaw=90, expr="neutral", head=[0, 0])
walk("me", "L10.1+1.8", [4.0, 3.7, 0.5], expr="neutral")
hide("me", "L11")
put("me", "L12", [2.6, -1.05, 0.54], yaw=-90, expr="worried", head=[0, 0])
hide("me", "L13")
put("me", "L16", [-2.0, 3.6, 0.5], yaw=-90, expr="worried", head=[-40, 4])
walk("me", "L16+1.8", [-6.5, 3.6, 0.5], expr="worried", head=[-40, 4])
hide("me", "L17")
put("me", "L19", [10.8, -1.05, 0.62], yaw=90, lean=22, expr="scared", head=[0, 10])
hide("me", "L20")
put("me", "L29", BUNK, yaw=-90, expr="neutral", head=[0, 6])
put("me", "L30", [5.45, -0.55, -0.06], yaw=-95, expr="worried", head=[-25, 0])
put("me", "L31", [5.45, -0.55, -0.06], yaw=-95, expr="worried", head=[-25, 0])
hide("me", "L32")
put("me", "L33", [5.0, -0.7, -0.06], yaw=-20, expr="worried", head=[0, 0])
put("me", "L37", [5.0, -0.5, -0.06], yaw=180, expr="worried", head=[0, 0])
hide("me", "L38")
put("me", "L38", STEP0, yaw=90, expr="worried", head=[0, 0])
hide("me", "L38.2")
put("me", "L38.2", [3.55, -0.85, 0.05], yaw=90, expr="worried", arms=[150, 0])
hide("me", "L39")
put("me", "L41", [5.95, -0.7, 0.8], yaw=0, expr="worried", lie=[-88, 0, 90])
put("me", "L43", [5.35, -0.55, -0.06], yaw=-90, expr="worried", head=[-40, 0])
hide("me", "P01>")
put("me", "L46", [5.35, -0.55, -0.06], yaw=-90, expr="scared", head=[-60, 0])
put("me", "L47", [4.7, -0.55, -0.5], yaw=110, expr="wide", head=[0, 0])
hide("me", "L48")
put("me", "L49", [5.0, -0.7, -0.06], yaw=-20, expr="wide", head=[0, 0])
walk("me", "L49+0.6", [4.6, -0.9, 0.05], expr="wide")
hide("me", "L50")
put("me", "L59", [5.3, -0.7, -0.06], yaw=-100, expr="neutral", head=[0, 0])
hide("me", "L60")
put("me", "L60.1", STEP0, yaw=90, expr="neutral")
hide("me", "L61")
put("me", "L61", [4.7, -1.6, 0.05], yaw=-90, expr="neutral", arms=[70, 70], lean=18, head=[0, 22])
put("me", "L61.2", STEP0, yaw=-90, expr="neutral", arms=[60, 60], head=[0, 8])
put("me", "L62", [1.4, -1.05, 0.72], yaw=-60, expr="neutral", arms=[60, 60], lean=-4, head=[0, 8])
put("me", "L63", [1.5, -1.3, 0.72], yaw=-10, expr="smirk", arms=[60, 60], head=[0, 6])
key("me", "L63+0.3", yaw=0, blend=0.3)
hide("me", "P02")
put("me", "L66", [0.8, 0.95, 0.5], yaw=90, expr="neutral", arms=[60, 60], head=[0, 14])
walk("me", "L66+1.0", [4.2, 1.5, 0.5], expr="neutral", arms=[60, 60], head=[0, 14])
put("me", "L66.1", [4.5, 1.45, -0.2], yaw=180, expr="neutral", arms=[0, 0], lean=0, head=[0, 22])
put("me", "L67", [4.6, 1.5, -0.2], yaw=180, expr="smirk", lean=0, arms=[30, 0], head=[0, 20])
hide("me", "L68")
put("me", "L68", STEP0, yaw=90, expr="smirk", head=[0, 24], arms=[60, 60])
hide("me", "L69")
put("me", "L69", [0.0, 3.5, 0.5], yaw=90, expr="smirk", head=[0, 14], arms=[0, 0])
walk("me", "L69+2.5", [2.2, 3.5, 0.5], expr="smirk", head=[0, 14])
put("me", "L70", [2.2, 3.5, 0.5], yaw=90, expr="smirk", head=[0, 14])
walk("me", "L70+1.5", [3.6, 3.5, 0.5], expr="smirk", head=[0, 14])
hide("me", "L71")
put("me", "L72", [0.6, -0.5, 0.72], yaw=-60, expr="smirk", head=[0, 6])

# the Long Man: eyes open, never blinking, a hairline mouth
put("longman", 0, [0, 0, 0], expr="neutral", blink=False)

# ------------------------------------------------------------------------------------------------- cues
cues = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


# time of day: slow ramps only inside shots
cue(0, "time", set="hook")
cue("L02", "time", set="grey1")
cue("L03", "time", set="past")
cue("L07", "time", set="grey1")
cue("L13", "time", set="wide3")
cue("L14", "time", set="far")
cue("L16", "time", set="grey1")
cue("L17", "time", set="far")
cue("L17+0.3", "time", set="clear1", dur=3.0)
cue("L18", "time", set="grey2")
cue("L22", "time", set="wide3")
cue("L23", "time", set="grey2")
cue("L29", "time", set="night")
cue("L32", "time", set="grey3")
cue("L38", "time", set="night")
cue("L40", "time", set="thick")
cue("L44", "time", set="scare")
cue("L45", "time", set="wide2")
cue("L46", "time", set="scare")
cue("L53", "time", set="thick")
cue("L54", "time", set="past")
cue("L55", "time", set="thick")
cue("L56", "time", set="wide2")
cue("L57", "time", set="thick")
cue("L60", "time", set="night")
cue("L60.1", "time", set="grey1")
cue("L62", "time", set="thick")
cue("L63", "time", set="grey1")
cue("P02", "time", set="clear2", dur=3.0)
cue("L66", "time", set="clear2")
cue("L68", "time", set="morning")
cue("L72", "time", set="hook")

# Moss
UPRIGHT = {"pose": "stand", "ears": 0.6, "tail": 20, "wag": 0}
cue(0, "moss", hidden=True)
cue("L02", "moss", hidden=False, pos=[8.5, -1.5, 0.05], yaw=0, pose="stand", head=[0, -26], ears=0.9, tail=20, wag=0)
cue("L03", "moss", hidden=True)
cue("L04", "moss", hidden=False, pos=[2.45, -1.05, 0.54], yaw=-90, pose="stand", head=[0, 0], ears=0.9, tail=-35, wag=0.7)
cue("L04.1", "moss", pos=[1.4, 0.8, 0.5], yaw=90, pose="stand", head=[0, 10], ears=0.9, tail=-35, wag=0.5)
cue("L05", "moss", pos=[5.15, 0.5, 0.5], yaw=-90, pose="roll", head=[0, 0], ears=0.4, tail=-10, wag=0.0)
cue("L06", "moss", pos=[-1.5, 3.1, 0.5], yaw=90, pose="stand", head=[0, 14], ears=0.7, tail=-10, wag=0.3, walk=True)
cue("L06+3.0", "moss", pos=[3.7, 3.1, 0.5], dur=3.0)
cue("L07", "moss", pos=[4.15, -1.05, 0.12], yaw=-90, pose="lie", head=[0, 0], ears=0.2, tail=30, wag=0, walk=False)
cue("L08", "moss", hidden=True)
cue("L09", "moss", hidden=False, pos=[4.05, -1.05, 0.12], yaw=-90, pose="lie", head=[0, 28], ears=0.7, tail=-40, wag=0.9)
cue("L10", "moss", pos=[4.05, -1.05, 0.12], yaw=-90, pose="lie", head=[-38, 0], ears=0.3, tail=30, wag=0)
cue("L10.1", "moss", hidden=True)
cue("L15", "moss", hidden=False, pos=[3.8, -1.05, 0.05], yaw=-90, pose="sit", head=[0, 30], ears=1.0, tail=30, wag=0)
cue("L16", "moss", hidden=True)
cue("L27", "moss", hidden=False, pos=[3.5, -1.05, 0.2], yaw=-90, pose="climb", head=[0, 16], ears=0.7, tail=30, wag=0)
cue("L28", "moss", pos=[3.7, -1.05, 0.05], yaw=-90, pose="sit", head=[0, 38], ears=0.8, tail=30, wag=0)
cue("L29", "moss", hidden=True)
cue("L39", "moss", hidden=False, pos=[3.9, -1.05, 0.12], yaw=-90, pose="lie", head=[0, 30], ears=0.8, tail=30, wag=0)
cue("L40", "moss", hidden=True)
cue("L50", "moss", hidden=False, pos=[3.5, -1.05, 0.2], yaw=-90, pose="climb", head=[0, 16], ears=0.7, tail=30, wag=0)
cue("L51", "moss", pos=[3.3, -1.05, 0.2], yaw=-90, pose="sit", head=[0, 40], ears=0.9, tail=20, wag=0)
cue("L53", "moss", hidden=True)
cue("L54", "moss", hidden=False, pos=[5.15, 0.5, 0.5], yaw=-90, pose="roll", head=[0, 0], ears=0.4, tail=-10, wag=0.0)
cue("L55", "moss", hidden=True)
cue("L57", "moss", hidden=False, pos=[3.3, -1.05, 0.2], yaw=-90, pose="sit", head=[0, 40], ears=0.9, tail=20, wag=0)
cue("L58", "moss", hidden=True)
cue("L60", "moss", hidden=False, pos=[4.0, -1.05, 0.12], yaw=-90, pose="lie", head=[0, 0], ears=0.4, tail=30, wag=0)
cue("L61.2", "moss", pose="held", hold="me", ears=0.6, head=[0, 0])
cue("L62", "moss", pose="held", hold="me", ears=0.8)
cue("P02", "moss", hidden=True)
cue("L66", "moss", hidden=False, pose="held", hold="me", ears=0.8, head=[0, 0])
cue("L66.1", "moss", hold=None, pos=[5.15, 0.55, 0.5], yaw=-90, pose="lie", head=[0, 0], ears=0.5, tail=20, wag=0)
cue("L67", "moss", pos=[5.15, 0.5, 0.5], yaw=-90, pose="roll", head=[0, 0], ears=0.6, tail=-45, wag=1.0)
cue("L68", "moss", hidden=False, pose="held", hold="me", ears=0.8, head=[0, 0], walk=False)
cue("L69", "moss", hold=None, pos=[-0.2, 3.0, 0.5], yaw=90, pose="stand", head=[0, 30], ears=0.9, tail=-30, wag=0.2, walk=True)
cue("L69+2.5", "moss", pos=[2.1, 3.0, 0.5], dur=2.5)
cue("L70", "moss", pos=[2.1, 3.0, 0.5], dur=0.01)
cue("L70+1.5", "moss", pos=[3.5, 3.0, 0.5], dur=2.0)
cue("L71", "moss", pos=[2.6, 3.1, 0.5], yaw=90, head=[0, 4], ears=0.5, tail=-20, wag=0.2, walk=False, dur=0.01)
cue("L72", "moss", pos=[3.4, 3.3, 0.5], yaw=-90, pose="roll", head=[0, 0], ears=0.4, tail=-10, wag=0.0, walk=False, scale=2.2)

# the Long Man (head x, y; body runs away up the towpath)
cue(0, "long", x=5.0, y=5.0, turn=0, hidden=False)
cue("L02", "long", hidden=True)
cue("L13", "long", x=22.5, y=0.3, turn=0, hidden=False)
cue("L17", "long", hidden=True)
cue("L18", "long", x=19.0, y=0.3, turn=0, hidden=False)
cue("L29", "long", hidden=True)
cue("L32", "long", x=12.0, y=0.3, turn=0, hidden=False)
cue("L34", "long", x=12.0, y=0.3, turn=1, hidden=False)
cue("L38", "long", hidden=True)
cue("P01>", "long", x=5.0, y=0.17, turn=1, hidden=False)
cue("L50", "long", hidden=True)
cue("L53", "long", x=5.0, y=0.5, turn=0, hidden=False)
cue("L54", "long", hidden=True)
cue("L55", "long", x=5.0, y=0.5, turn=0, hidden=False)
cue("L57", "long", hidden=True)
cue("L58", "long", x=5.0, y=0.5, turn=0, hidden=False)
cue("L59", "long", hidden=True)
cue("L62", "long", x=5.0, y=0.5, turn=0, hidden=False)
cue("L65", "long", hidden=True)
# the worn patch (past only) and the grown-in tufts (present)
cue(0, "patch", on=False)
cue("L05", "patch", on=True)
cue("L06", "patch", on=True)
cue("L07", "patch", on=False)
cue("L54", "patch", on=True)
cue("L55", "patch", on=False)
# the hatch and the bolt
cue(0, "hatch", open=1.0)
cue("L02", "hatch", open=0.0)
cue("L03", "hatch", open=1.0)
cue("L04", "hatch", open=0.0)
cue("L08", "hatch", open=1.0)
cue("L10", "hatch", open=0.0)
cue("L12", "hatch", open=1.0)
cue("L15", "hatch", open=0.0)
cue("L19", "hatch", open=0.0)
cue("L27", "hatch", open=1.0)
cue("L28", "hatch", open=1.0)
cue("L29", "hatch", open=0.0)
cue("L38", "hatch", open=1.0)
cue("L38.1", "hatch", open=0.0)
cue("L60.1", "hatch", open=1.0, dur=1.5)
cue("L68", "hatch", open=1.0)
cue(0, "bolt", on=False)
cue("L38.2+0.5", "bolt", on=True)
cue("L60+0.6", "bolt", on=False)
# the bunk window: condensation, wiped in a second
cue(0, "wipe", to=0.0)
cue("L31", "wipe", to=0.0)
cue("L31.1", "wipe", to=0.0)
cue("L32", "wipe", to=0.0)
cue("L40", "wipe", to=0.0)
cue("L43+0.15", "wipe", to=1.0, dur=1.0)
cue("L48-0.3", "wipe", to=0.6, dur=0.25)
cue("L49", "wipe", to=0.55)
cue("L53", "wipe", to=0.0)
cue(0, "flat", on=False)
cue("L65", "flat", on=True)
cue("L66", "flat", on=False)
cue(0, "tally", on=False)
cue("P03", "tally", on=True)
cue("L66", "tally", on=False)

# --------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L03+0.2", "kind": "creak", "db": -26, "dur": 1.2},
    {"at": "L38.2+0.5", "kind": "click", "db": -16},
    {"at": "L44", "kind": "sting", "db": -11},
    {"at": "L50", "kind": "click", "db": -24},
    {"at": "L50.2", "kind": "click", "db": -24},
    {"at": "L51", "kind": "click", "db": -24},
    {"at": "L52", "kind": "glide", "db": -26, "dur": 1.0},
    {"at": "L60+0.6", "kind": "click", "db": -16},
    {"at": "L60.1", "kind": "creak", "db": -22, "dur": 1.6},
    {"at": "L72>", "kind": "bell", "db": -17, "dur": 1.6},
]
story = {
    "slug": "ep27-towpath",
    "title": "On our boat, the day starts with good morning, then something lies down on the towpath",
    "made_for_kids": False,
    "premise": "I live on a long boat with my old dog, Moss. Every dawn since her legs went, something as long as the boat lies down on the towpath one mooring ring nearer, and it ends beside my window, in the grass by the back ring.",
    "twist": "It was never coming for me or the boat. Moss rolled in the grass by the back ring every morning for twelve years, and since her legs went the patch has sat empty, so something came to lie in her place for her, until I carry her out to her spot.",
    "world": "a navy narrowboat moored on a still canal in autumn fog, a gravel towpath with iron mooring rings along the stone edge, willows on the far bank",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#9be37a",
    "caption": {"ink": "#0a0d0c", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#c2cac9", "fog_density": 0.06, "fog_start": 3.0, "sky": "#c2cac9", "sky_strength": 0.95,
             "exposure": 0.05, "flash_safe": True},
    "grade": {"shadows": [-0.01, 0.0, 0.03], "highlights": [0.0, 0.004, 0.0], "saturation": 0.9, "contrast": 1.04,
              "vignette": 0.28, "bloom": 0.12, "grain": 0.012},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 47, "mode": "minor", "bpm": 66, "seed": 27,
              "sections": [
                  {"at": 0, "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L07", "voices": ["drone", "pad", "pulse"], "energy": 0.36},
                  {"at": "L18", "voices": ["drone", "pad", "pulse"], "energy": 0.42},
                  {"at": "L32", "voices": ["drone", "pad", "pulse"], "energy": 0.46},
                  {"at": "L40", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L44", "voices": ["drone", "pad", "choir"], "energy": 0.5},
                  {"at": "L53", "voices": ["pad"], "energy": 0.25},
                  {"at": "L57", "voices": ["pad", "drone"], "energy": 0.3},
                  {"at": "P02", "voices": ["piano", "pad", "drone"], "energy": 0.4, "mode": "major", "root": 50},
                  {"at": "L72", "voices": ["pad"], "energy": 0.25},
              ]},
    "sound": {"floor": "wood", "steps_db": -24,
              "ambience": [
                  {"kind": "water", "from": 0, "to": "end", "lufs": -34},
                  {"kind": "wind", "from": 0, "to": "L10", "lufs": -44},
                  {"kind": "wind", "from": "L66", "to": "end", "lufs": -44},
                  {"kind": "water", "from": "L72>-0.6", "to": "end", "lufs": -14},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "L44", "keep": ["sting"]}]},
}
story = remap(story)
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
