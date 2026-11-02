"""Writes ../story.json for ep27-towpath (writer's script.md, builder round 1, 2026-11-02).

Run from anywhere: python stories/ep27-towpath/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and cameras, the acting,
the cues set.py reads (time of day, Moss, the Long Man, the hatch, the bolt, the wipe), the score and the sound.

Places (set.py's metres): x along the canal from the boat's stern (0) to its bow (12); y across it, the towpath at
+y, the water at -y, the boat's towpath side at y = -0.15; z up (water 0, towpath 0.5, back deck 0.72, cabin
floor 0.05). A character with yaw 0 faces -y, yaw 90 faces +x, yaw -90 faces -x, yaw 180 faces +y.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

HOLDS = {"P01": 0.7, "P02": 1.3, "P03": 1.7}
for ln in lines:
    if ln["id"] in HOLDS:
        ln["pause"] = HOLDS[ln["id"]]

# spoken-only fixes for the word check (the captions don't change)
SPOKEN = {("L02", "I live on a long boat"): "I live, on a long boat", ("L09", "I'd just step"): "I would just step",
          ("L74", "We walk the towpath"): "We walk, the towpath",
          ("L59", "everybody on board"): "everybody on board,", ("L59", "is crew."): "is crew.",
          ("L65", "and opened the hatch."): "and opened, the hatch."}
for ln in lines:
    for ch in ln.get("chunks", []):
        if (ln["id"], ch[1]) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], ch[1])]

# the word check (asr): lines a touch slower so a swallowed word comes through
TEMPO = {"L02": 0.9, "L09": 0.9, "L47": 0.9, "L59": 0.78, "L24": 0.88, "L65": 0.9, "L74": 0.9}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]

# captions show two or three words at a time: a longer chunk of the script is split into even pieces. CHUNK_MAP keeps
# the script's own chunk numbers ("L14.2") pointing at the same words, whatever the splitting did
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
        import re
        mm = re.match(r"^(L\d+)\.(\d+)(.*)$", v)
        if mm and mm.group(1) in CHUNK_MAP:
            return f"{mm.group(1)}.{CHUNK_MAP[mm.group(1)][int(mm.group(2))]}{mm.group(3)}"
        return v
    if isinstance(v, list):
        return [remap(x) for x in v]
    if isinstance(v, dict):
        return {k: (remap(x) if k in ("at", "from", "to") else remap(x) if isinstance(x, (list, dict)) else x)
                for k, x in v.items()}
    return v

cast = {
    "me": {"age": "adult", "skin": "#e0b690", "shirt": "#a99b7a", "pattern": "knit", "pattern_c": "#8d805f",
           "pants": "#1f2a40", "shoes": "#2c2622", "sleeves": "long", "hair": "cap", "hair_c": "#6b4a2e",
           "hat": "beanie", "hat_c": "#1f4a4d",
           "face": {"eyes": "tired", "brows": True, "ink": "#1b1513"}},
    "longman": {"age": "adult", "skin": "#8a8a64", "shirt": "#4d6638", "pattern": "knit", "pattern_c": "#34472a",
                "pants": "#6a4f33", "pants_pattern": "stripes", "pants_pattern_c": "#58402a", "shoes": "#6a4f33",
                "sleeves": "long", "hair": "cap", "hair_c": "#2f4026", "hat": "none", "height": 1.0,
                "face": {"eyes": "hollow", "brows": False, "mouth": "line", "ink": "#0e0e0e", "glow": "#f4faf6"}},
}


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens, roll=0):
    return c([0, loc, tgt, lens, roll])


def move(a, b, lens_a, lens_b=None, roll=0):
    return c([0, a[0], a[1], lens_a, roll], [1, b[0], b[1], lens_b or lens_a, roll])


# ----------------------------------------------------------------------------------------------- the shots
# (at, what, step, camera)
S = []


def shot(at, what, cam, step=2):
    S.append((at, what, step, cam))


# 01 the greeting
shot(0, "low on the towpath at dawn, the boat on the right, far up the path a long dark line",
     move(([-9.5, 1.5, 0.95], [12, -0.2, 0.95]), ([-7.2, 1.4, 0.95], [12, -0.2, 0.95]), 24))
shot("L02", "side wide of the whole boat on still water", still([6, -22, 1.7], [6, -0.15, 1.15], 20))
shot("L03", "close on Moss in her bed, white muzzle on her paws", still([3.3, -1.0, 0.42], [4.2, -1.05, 0.2], 36))
shot("L04", "the past: me at the open hatch from below, smirk", still([4.7, -1.4, 0.35], [2.85, -1.05, 2.15], 30))
shot("L05", "the past: Moss on the top step, wagging, me at the hatch", still([1.9, -1.8, 1.0], [2.2, -1.05, 0.85], 30))
shot("L06", "Moss lying at the foot of the steps, looking at them", still([5.8, -1.35, 0.55], [3.7, -1.05, 0.3], 28))
shot("L07", "the three steps from Moss's eye level, empty", still([3.9, -1.05, 0.26], [2.3, -1.05, 0.5], 32))
shot("L08", "me at the top of the steps, back to camera, hatch open on grey fog",
     still([4.4, -1.05, 1.1], [2.5, -1.05, 1.35], 28))
shot("L09", "high angle: my boots stepping past her bed, Moss's head turning",
     still([4.1, -1.75, 1.95], [4.0, -1.1, 0.2], 28))
# 02 the first dawn
shot("L10", "my bunk, me sitting up, Moss at the foot of the steps behind", still([8.0, -0.85, 1.35], [5.3, -0.85, 1.15], 26))
shot("L11", "the shut hatch from below, grey light round its edges", still([5.2, -1.3, 0.9], [3.0, -1.05, 2.0], 30))
shot("L12", "my face, half lit by the round window", still([4.0, -1.4, 1.45], [5.5, -0.6, 1.4], 34))
shot("L13", "Moss from behind and low, sitting square, head up at the shut hatch",
     still([5.0, -1.35, 0.5], [3.5, -1.05, 0.95], 28))
shot("L14", "Moss on the second step", still([4.4, -1.0, 0.55], [2.9, -1.05, 0.6], 28))
shot("L14.2", "Moss on the top step under the hatch, slid open", still([4.3, -1.05, 0.7], [2.5, -1.05, 1.0], 28))
shot("L15", "the back deck from behind: Moss at the rail, me rising out of the hatch",
     still([-1.8, -0.9, 1.5], [1.9, -0.9, 1.15], 28))
shot("L16", "wide over the water, fog and the willows' outlines", still([1.0, -1.1, 1.7], [3.0, -25, 1.0], 26))
shot("L17", "over my shoulder down the boat and up the towpath: the third ring and a long dark shape",
     still([0.9, -0.5, 2.3], [24, 0.3, 0.7], 22))
shot("L18", "a long lens on it", still([0.9, -0.5, 2.3], [28, 0.3, 0.6], 55))
shot("L19", "Moss at the rail facing up the towpath, wagging, me behind her", still([2.0, -1.8, 1.2], [1.1, -0.7, 1.05], 30))
shot("L20", "the same long lens: the fog thins, the grass is empty", still([0.9, -0.5, 2.3], [28, 0.3, 0.6], 55))
# 03 the second dawn
shot("L21", "the cabin, hatch open, Moss already on the second step", still([4.4, -1.0, 0.7], [2.9, -1.05, 0.55], 28))
shot("L22", "from the bow up the towpath: two rings, then its head", still([11.3, -0.6, 1.6], [21, 0.3, 0.6], 26))
shot("L23", "me at the front of the boat, scared", still([13.5, -1.0, 1.5], [10.9, -1.05, 1.95], 32))
shot("L24", "its head and shoulders, face up, eyes open", still([16.4, -0.7, 1.15], [19.3, 0.3, 0.7], 38))
shot("L25", "a slow pan from its shoulders along the torso and on",
     move(([16.4, -0.9, 1.1], [19.5, 0.3, 0.7]), ([16.4, -0.9, 1.1], [30, 0.3, 0.7]), 30))
shot("L26", "high wide: the boat and the Long Man end to end, the same length",
     still([15.5, -17, 15], [15.5, 0.2, 0.5], 15, 90))
shot("L27", "close on the weed-green coat", still([21.5, -0.5, 1.25], [21.8, 0.3, 0.7], 34))
shot("L27.2", "the rope-brown trouser stripe", still([26.5, -0.5, 1.25], [26.8, 0.3, 0.7], 34))
shot("L28", "straight down over its face", still([19.0, 0.3, 2.3], [19.0, 0.3, 0.7], 30))
shot("L29", "macro on the beads on its cheek", still([18.9, -0.2, 1.1], [19.05, 0.3, 0.8], 75))
shot("L30", "Moss on the back deck, ears up, looking along the boat", still([0.4, -0.95, 1.0], [2.4, -0.45, 0.9], 30))
shot("L31", "me behind her, mouth open on her name; Moss keeps looking", still([1.3, -1.85, 1.35], [0.9, -0.8, 1.2], 30))
# 04 the third dawn
shot("L32", "my bunk, me already sitting up in my beanie", still([8.0, -0.85, 1.35], [5.3, -0.85, 1.15], 26))
shot("L33", "me on the steps under the shut hatch, Moss at the foot",
     still([4.8, -1.05, 1.1], [2.9, -1.05, 1.3], 28))
shot("L34", "the shut hatch, my head turning toward the front", still([3.9, -0.5, 1.0], [2.9, -1.05, 1.45], 30))
shot("L35", "my face, worried, a hand at my throat", still([4.2, -1.05, 1.5], [2.9, -1.05, 1.45], 40))
shot("L36", "me with the hatch half open, calling out, side on", still([1.2, -1.8, 1.5], [2.7, -1.05, 2.0], 34))
shot("L37", "fog over the front of the boat", still([6.5, -1.05, 2.5], [14, 0.0, 0.8], 24))
shot("L38", "closer on me, scared", still([4.2, -1.05, 1.6], [2.7, -1.05, 2.0], 36))
shot("L39", "the water by the front ring, flat", still([12.6, -2.4, 0.9], [14.4, 0.0, 0.55], 30))
shot("L40", "Moss on the top step beside me, looking toward the front", still([4.5, -1.55, 0.95], [2.8, -1.05, 0.75], 30))
shot("L41", "its head at the front ring, now turned on its side, face toward the boat",
     still([3.0, -5.5, 2.0], [12.1, 0.3, 0.8], 70))
shot("L42", "close: the head turned flat sideways while the chest stays face up",
     still([10.4, -0.8, 1.45], [12.7, 0.3, 0.7], 42))
shot("L43", "inside at night: the bolt from below", still([4.7, -0.9, 1.0], [3.2, -0.62, 1.95], 36))
shot("L43.2", "my hand at the end of my sleeve beside it", still([5.1, -1.35, 1.55], [3.3, -0.7, 1.75], 34))
# 05 the fourth dawn: the scare
shot("L44", "the bunk window from inside: white fog, beaded with condensation", still([5.0, -1.5, 0.98], [5.0, -0.1, 0.84], 36))
shot("L45", "me lying awake, the round window above me", still([4.2, -1.3, 1.25], [5.5, -0.6, 0.85], 30))
shot("L46", "close on the cabin wall by the bunk, wood grain", still([6.4, -1.0, 0.75], [6.6, -0.25, 0.7], 40))
shot("L47", "me rising onto an elbow toward the window", still([4.3, -1.25, 1.3], [5.1, -0.55, 1.25], 32))
shot("L48", "my sleeve crossing the glass in a one second wipe", still([5.0, -1.5, 0.98], [5.0, -0.1, 0.84], 36))
shot("P01", "the wiped glass, white fog behind it", still([5.0, -1.5, 0.98], [5.0, -0.1, 0.84], 36), 1)
shot("L49", "two round eyes right behind the glass", still([5.0, -1.5, 0.98], [5.0, -0.1, 0.84], 36), 1)
shot("L50", "high wide outside in thick fog: the Long Man the whole length of the boat",
     still([8.5, -15, 14], [8.5, 0.2, 0.5], 15, 90), 1)
shot("L51", "its face at my window, me inside", still([3.9, -1.2, 1.15], [5.0, -0.15, 0.95], 36), 1)
shot("L52", "tight on me, my ear by the glass, its eyes beyond", still([6.2, -1.3, 1.35], [5.0, -0.35, 1.3], 42), 1)
shot("L53", "me turning from the window, two faint points behind me", still([4.2, -1.55, 1.3], [5.2, -0.4, 1.25], 34), 1)
shot("L54", "Moss at the foot of the steps, one front leg on the first step", still([4.9, -1.35, 0.4], [3.3, -1.05, 0.35], 30))
shot("L55", "low from behind Moss on the first step: the bolted hatch above", still([4.5, -1.05, 0.5], [3.0, -1.05, 1.5], 28))
shot("L56", "Moss's face, ears up, eyes on the hatch", still([2.95, -0.75, 0.5], [3.3, -1.05, 0.52], 48))
# 06 the turn
shot("L57", "the warm past: Moss waiting at the foot of the steps", still([5.0, -1.35, 0.5], [3.5, -1.05, 0.95], 28))
shot("L58", "the warm past: the hatch sliding open over light", still([5.2, -1.3, 0.9], [3.0, -1.05, 2.0], 30))
shot("L59", "the cabin, me looking from Moss to the window", still([7.6, -1.0, 1.3], [4.8, -0.9, 1.1], 26))
shot("L60", "the hatch from below, bolted", still([4.4, -0.9, 0.9], [3.2, -0.62, 1.95], 34))
shot("L61", "my face, neutral, the fear going", still([4.3, -1.3, 1.5], [5.4, -0.7, 1.45], 42))
shot("L62", "me at the foot of the hatch, saying nothing", still([4.4, -1.05, 1.1], [2.5, -1.05, 1.35], 28))
shot("L63", "outside wide: the Long Man along the boat in the fog", still([8.5, -15, 14], [8.5, 0.2, 0.5], 15, 90))
shot("L64", "Moss on the first step, looking up", still([4.5, -1.05, 0.5], [3.0, -1.05, 1.5], 28))
# 07 good morning
shot("L65", "from below: the bolt", still([4.7, -0.9, 1.0], [3.2, -0.62, 1.95], 36))
shot("L65.1", "from below: the hatch sliding open over 1.5 s", still([5.2, -1.3, 0.9], [3.0, -1.05, 2.0], 30))
shot("L66", "me at the foot of the steps by Moss, reaching", still([5.7, -1.7, 1.2], [4.0, -1.1, 0.9], 30))
shot("L66.2", "me rising out of the hatch with Moss held against my chest", still([0.3, -1.05, 1.9], [2.45, -1.05, 2.0], 32))
shot("L67", "the back deck from behind: me and Moss at the hatch, its face on the towpath",
     still([-3.0, 0.45, 1.3], [3.8, 0.0, 1.15], 30))
shot("L68", "Moss on the deck boards beside me, looking up", still([0.7, -1.75, 1.1], [1.4, -1.05, 0.9], 32))
shot("L69", "my face, a small smile", still([0.2, -1.7, 2.0], [1.35, -1.05, 2.0], 40))
shot("L70", "Moss wagging so hard she nearly sits", still([0.5, -0.5, 1.0], [1.4, -1.05, 0.9], 36))
shot("P02", "the canal and the towpath; the fog begins to ease",
     still([1.0, -1.1, 1.8], [6.0, -25, 1.2], 24))
shot("L72", "the towpath alongside the boat, the grass flattened in one long line",
     move(([2.0, 3.0, 1.35], [8.0, 0.1, 0.55]), ([4.0, 3.0, 1.35], [10.0, 0.1, 0.55]), 28))
shot("P03", "the lore plant: the back ring, two strokes", still([5.0, 0.62, 1.05], [5.0, -0.02, 0.66], 42))
# 08 her pace
shot("L73", "me at the open hatch in a clear morning, smirk", still([4.7, -1.4, 0.35], [2.85, -1.05, 2.15], 30))
shot("L74", "low in front of us on the towpath: me bent beside Moss, my sleeve on her back, the boat behind",
     still([-6.0, 1.45, 0.75], [-2.2, 1.0, 0.85], 34))
shot("L75", "side wide: the two of us small on the long towpath, the last fog lifting",
     still([-4.2, -7.0, 1.5], [-4.2, 1.0, 1.0], 26))
shot("L76", "the first shot again, lighter: the boat, and us walking back toward it",
     move(([-9.5, 1.5, 0.95], [12, -0.2, 0.95]), ([-7.2, 1.4, 0.95], [12, -0.2, 0.95]), 24))

# camera fixes: character shots framed on the face heights (standing: pos z + 1.55)
FIX = {
 0: move(([-10.5, 1.5, 1.0], [6, -0.2, 1.0]), ([-8.5, 1.4, 1.0], [6, -0.2, 1.0]), 28),
 "L02": still([6, -17, 1.4], [6, -0.15, 1.1], 18),
 "L04": still([4.6, -1.05, 1.25], [2.6, -1.05, 2.05], 32),
 "L05": still([3.5, -1.3, 1.2], [1.8, -1.05, 1.5], 28),
 "L08": still([5.3, -1.05, 1.7], [2.6, -1.05, 1.95], 26),
 "L10": still([8.2, -0.9, 1.45], [4.8, -0.8, 1.2], 24),
 "L12": still([3.7, -0.9, 1.5], [5.45, -0.55, 1.5], 34),
 "L15": still([-1.0, -1.1, 1.6], [2.6, -1.05, 1.9], 30),
 "L19": still([1.2, -4.0, 1.8], [1.1, -0.8, 1.7], 30),
 "L23": still([13.5, -1.0, 1.7], [10.8, -1.05, 2.1], 32),
 "L24": still([21.2, 0.6, 1.5], [19.1, 0.3, 0.8], 34),
 "L26": still([15.5, -26, 8], [15.5, 0.2, 0.6], 11),
 "L03": still([4.5, -0.4, 0.6], [3.9, -1.05, 0.3], 30),
 "L37": still([3.5, -0.6, 2.6], [14, 0.0, 0.8], 24),
 "P02": still([-0.3, -1.0, 1.9], [6.0, -25, 1.2], 24),
 "L31": still([1.2, -3.6, 1.9], [1.2, -0.7, 1.8], 30),
 "L33": still([0.6, -1.05, 1.7], [2.95, -1.05, 1.9], 30),
 "L34": still([4.2, -1.4, 1.8], [2.95, -1.05, 1.9], 30),
 "L35": still([1.3, -1.05, 1.9], [2.95, -1.05, 1.95], 26),
 "L36": still([4.4, -1.3, 1.5], [2.6, -1.05, 2.05], 30),
 "L38": still([4.0, -1.3, 1.6], [2.6, -1.05, 2.05], 36),
 "L40": still([4.6, -1.6, 1.4], [2.8, -1.05, 1.3], 30),
 "L41": still([4.0, -6.5, 5.0], [12.1, 0.3, 0.8], 60),
 "L42": still([8.5, -5.5, 4.0], [12.7, 0.3, 0.7], 50),
 "L43.2": still([5.4, -1.4, 1.6], [3.5, -0.85, 1.7], 30),
 "L47": still([3.6, -1.4, 1.5], [5.5, -0.6, 1.5], 32),
 "L50": still([9, -14, 5], [9, 0.2, 0.8], 16),
 "L52": still([6.2, -1.3, 1.45], [5.0, -0.35, 1.45], 36),
 "L53": still([4.2, -1.55, 1.45], [5.2, -0.4, 1.45], 34),
 "L59": still([7.6, -1.0, 1.4], [4.8, -0.9, 1.4], 26),
 "L61": still([4.3, -1.3, 1.5], [5.4, -0.7, 1.5], 32),
 "L63": still([9, -14, 5], [9, 0.2, 0.8], 16),
 "L66": still([7.0, -1.5, 1.4], [4.6, -1.4, 1.0], 30),
 "L66.2": still([0.3, -1.05, 1.9], [2.45, -1.05, 2.0], 32),
 "L67": still([-3.0, 0.45, 1.3], [3.8, 0.0, 1.6], 30),
 "L68": still([1.7, -3.8, 1.6], [1.7, -1.2, 1.5], 30),
 "L69": still([1.5, -3.3, 2.25], [1.5, -1.3, 2.25], 34),
 "L70": still([1.9, -3.3, 1.1], [1.9, -1.2, 0.95], 34),
 "L74": still([-5.5, 2.5, 1.5], [-2.0, 1.1, 1.3], 32),
}
S[:] = [(at, what, step, FIX.get(at, cam)) for at, what, step, cam in S]
S[-1] = (S[-1][0], S[-1][1], S[-1][2], FIX[0])

shots = []
for i, (at, what, step, cam) in enumerate(S):
    s = {"id": f"S{i + 1:02d}", "cam": cam, "hand": 0.004, "step": step, "what": what}
    if i:
        s["at"] = at
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


STEP0, STEP1 = [2.6, -1.05, 0.54], [2.95, -1.05, 0.36]
BUNK = [5.55, -0.62, -0.06]
FLAT = [0.0, 0.0]

# me
put("me", 0, [0, -1.05, 0.72], hidden=True)
hide("me", 0)
put("me", "L04", STEP0, yaw=90, head=[0, 22], expr="smirk")
put("me", "L05", [1.2, -1.05, 0.72], yaw=90, lean=18, arms=[35, 35], head=[0, 14], expr="smirk")
hide("me", "L06")
put("me", "L08", STEP0, yaw=-90, head=[0, 0], expr="neutral")
put("me", "L09", [5.3, -1.62, 0.05], yaw=-90, expr="neutral")
walk("me", "L09+1.4", [3.3, -1.62, 0.05], expr="neutral")
hide("me", "L09+1.45")
put("me", "L10", BUNK, yaw=-90, expr="worried", head=[0, 6])
put("me", "L12", [5.45, -0.55, -0.06], yaw=-95, expr="worried", head=[-25, 0])
hide("me", "L13")
put("me", "L15", STEP0, yaw=-90, head=[0, 0], expr="neutral")
walk("me", "L15+0.5", [2.6, -1.05, 0.54], expr="neutral")
hide("me", "L16")
put("me", "L19", [0.6, -1.0, 0.72], yaw=90, expr="wide")
hide("me", "L20")
put("me", "L23", [10.8, -1.05, 0.62], yaw=90, lean=22, expr="scared", head=[0, 10])
hide("me", "L24")
put("me", "L31", [0.7, -0.85, 0.72], yaw=90, expr="scared", arms=[10, 10])
talk("me", "L31", "L31.1")
hide("me", "L32")
put("me", "L32", BUNK, yaw=-90, expr="worried")
put("me", "L33", STEP1, yaw=-90, expr="neutral", head=[0, -22])
put("me", "L34", STEP1, yaw=-90, expr="worried", head=[0, -8])
key("me", "L34.2", head=[70, 0], blend=0.4)
put("me", "L35", STEP1, yaw=-90, expr="worried", arms=[0, 100], head=[0, 0])
put("me", "L36", STEP0, yaw=90, expr="worried", head=[0, 0])
talk("me", "L36", "L36>")
put("me", "L38", STEP0, yaw=90, expr="scared", head=[0, 0])
talk("me", "L38", "L38>")
put("me", "L40", STEP1, yaw=90, expr="scared")
hide("me", "L41")
put("me", "L43.2", [3.55, -0.85, 0.05], yaw=-90, expr="worried", arms=[150, 0])
hide("me", "L44")
put("me", "L45", [5.95, -0.7, 0.8], yaw=0, expr="worried", lie=[-88, 0, 90])
put("me", "L47", BUNK, yaw=-90, expr="worried", head=[-5, 0], lean=0)
put("me", "L48", [5.35, -0.55, -0.06], yaw=-90, expr="worried", head=[-40, 0])
hide("me", "P01>")
put("me", "L51", [5.35, -0.55, -0.06], yaw=-90, expr="scared", head=[-60, 0])
put("me", "L52", [5.0, -0.6, -0.06], yaw=180, expr="wide", head=[-25, 0])
put("me", "L53", [5.0, -0.7, -0.06], yaw=-20, expr="wide", head=[0, 0])
walk("me", "L53+0.6", [4.6, -0.9, 0.05], expr="wide")
hide("me", "L54")
put("me", "L59", [4.6, -1.35, 0.05], yaw=-90, expr="worried", head=[-20, 0])
key("me", "L59.2", head=[40, 0], expr="worried", blend=0.5)
put("me", "L61", [5.3, -0.7, 0.05], yaw=-100, expr="neutral", head=[0, 0])
put("me", "L62", STEP0, yaw=-90, expr="neutral")
hide("me", "L63")
hide("me", "L65")
put("me", "L66", [4.7, -1.6, 0.05], yaw=-90, expr="neutral", arms=[70, 70], lean=18, head=[0, 22])
put("me", "L66.2", STEP0, yaw=-90, expr="neutral", arms=[60, 60], head=[0, 8])
put("me", "L67", [1.5, -1.3, 0.72], yaw=90, expr="wide", arms=[60, 60], lean=-4)
put("me", "L68", [1.5, -1.3, 0.72], yaw=90, expr="neutral", arms=[0, 0], head=[0, 20])
put("me", "L69", [1.5, -1.3, 0.72], yaw=-10, expr="smirk", head=[0, 6])
key("me", "L69+0.3", yaw=0, blend=0.3)
put("me", "L70", [1.5, -1.3, 0.72], yaw=20, expr="smirk", head=[0, 16])
put("me", "P02", [1.5, -1.3, 0.72], yaw=20, expr="smirk", head=[0, 6])
hide("me", "L72")
put("me", "L73", STEP0, yaw=90, head=[0, 24], expr="smirk")
put("me", "L74", [-1.4, 1.35, 0.5], yaw=-90, lean=24, expr="smirk", arms=[30, 0], head=[0, 22])
walk("me", "L74>", [-2.3, 1.35, 0.5], lean=24, arms=[30, 0], head=[0, 22])
walk("me", "L75>", [-4.6, 1.35, 0.5], lean=24, arms=[30, 0], head=[0, 22])
put("me", "L76", [-6.6, 1.35, 0.5], yaw=90, lean=22, expr="smirk", arms=[30, 0], head=[0, 22])
walk("me", "end", [-4.7, 1.35, 0.5], lean=22, arms=[30, 0], head=[0, 22])

# the Long Man: eyes open, never blinking, a hairline mouth
put("longman", 0, [0, 0, 0], expr="wide", blink=False)
key("longman", "L67", look=[0, 1], blend=0.1)

# ------------------------------------------------------------------------------------------------- cues
cues = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


# time of day: ramps only inside shots
cue(0, "time", set="grey1")
cue("L04", "time", set="past")
cue("L06", "time", set="grey1")
cue("L16", "time", set="grey1")
cue("L20", "time", set="clear1", dur=1.8)
cue("L21", "time", set="grey2")
cue("L32", "time", set="night")
cue("L34", "time", set="grey3")
cue("L43", "time", set="night")
cue("L44", "time", set="thick")
cue("L57", "time", set="past")
cue("L59", "time", set="thick")
cue("L66", "time", set="clear1")
cue("P02", "time", set="clear2", dur=2.9)
cue("L73", "time", set="morning")
# Moss
cue(0, "moss", hidden=True)
cue("L03", "moss", hidden=False, pos=[4.15, -1.05, 0.12], yaw=-90, pose="lie", head=[0, 0], ears=0.2, tail=30, wag=0)
cue("L04", "moss", hidden=True)
cue("L05", "moss", hidden=False, pos=[2.45, -1.05, 0.54], yaw=-90, pose="stand", ears=0.9, tail=-40, wag=1.0)
cue("L06", "moss", pos=[4.0, -1.05, 0.12], yaw=-90, pose="lie", ears=0.3, tail=30, wag=0, head=[0, 0])
cue("L07", "moss", hidden=True)
cue("L09", "moss", hidden=False, pos=[4.05, -1.05, 0.12], yaw=-90, pose="lie", head=[0, 0], ears=0.2)
cue("L09+0.5", "moss", head=[-38, 0])
cue("L10", "moss", pos=[3.7, -1.05, 0.05], yaw=-90, pose="sit", head=[0, 38], ears=0.7, tail=30, wag=0)
cue("L14", "moss", pos=[3.0, -1.05, 0.36], yaw=-90, pose="climb", head=[0, 18], ears=0.8, dur=0.3)
cue("L14.2", "moss", pos=[2.5, -1.05, 0.54], yaw=-90, pose="stand", head=[0, 0], ears=0.9, tail=-35, wag=0.6)
cue("L15", "moss", pos=[1.4, -0.45, 0.72], yaw=180, pose="stand", head=[0, 0], ears=0.8, wag=0.5)
cue("L19", "moss", pos=[1.7, -0.5, 0.72], yaw=90, pose="stand", head=[0, 0], ears=1.0, tail=-35, wag=1.0)
cue("L21", "moss", pos=[2.95, -1.05, 0.36], yaw=-90, pose="stand", head=[0, 6], ears=0.9, tail=-20, wag=0.3)
cue("L22", "moss", hidden=True)
cue("L30", "moss", hidden=False, pos=[1.7, -0.5, 0.72], yaw=90, pose="stand", ears=1.0, tail=-10, wag=0)
cue("L32", "moss", pos=[3.7, -1.05, 0.05], yaw=-90, pose="sit", head=[0, 38], ears=0.6, tail=30, wag=0)
cue("L36", "moss", hidden=True)
cue("L40", "moss", hidden=False, pos=[2.5, -1.05, 0.54], yaw=-90, pose="sit", head=[40, 8], ears=1.0, tail=20, wag=0)
cue("L41", "moss", hidden=True)
cue("L53+0.2", "moss", hidden=False, pos=[3.5, -1.05, 0.2], yaw=-90, pose="climb", head=[0, 16], ears=0.7, tail=30, wag=0)
cue("L55", "moss", pos=[3.3, -1.05, 0.2], yaw=-90, pose="sit", head=[0, 40], ears=0.9)
cue("L57", "moss", pos=[3.7, -1.05, 0.05], yaw=-90, pose="sit", head=[0, 38], ears=0.8, tail=-10, wag=0.3)
cue("L58", "moss", hidden=True)
cue("L59", "moss", hidden=False, pos=[4.0, -1.05, 0.12], yaw=-90, pose="lie", head=[0, 0], ears=0.4, tail=30, wag=0)
cue("L64", "moss", pos=[3.3, -1.05, 0.2], yaw=-90, pose="sit", head=[0, 40], ears=0.9, tail=20, wag=0)
cue("L65", "moss", pos=[3.3, -1.05, 0.2], yaw=-90, pose="sit", head=[0, 40], ears=0.9)
cue("L66", "moss", pos=[4.2, -1.1, 0.12], yaw=-90, pose="lie", head=[0, 0], ears=0.5)
cue("L66.2", "moss", pose="held", hold="me", ears=0.6, head=[0, 0])
cue("L67", "moss", pose="held", hold="me", ears=0.8)
cue("L68", "moss", hold=None, pos=[1.9, -1.2, 0.72], yaw=-90, pose="stand", head=[0, 38], ears=0.9, tail=-30, wag=0.2)
cue("L69", "moss", head=[0, 36], wag=0.4)
cue("L70", "moss", tail=-45, wag=1.0)
cue("L70.2", "moss", pose="sit", pos=[1.9, -1.2, 0.72], wag=1.0)
cue("L72", "moss", hidden=True)
cue("L74", "moss", hidden=False, pos=[-1.5, 0.9, 0.5], yaw=-90, pose="stand", head=[0, 8], ears=0.7, tail=-20, wag=0.4, walk=True)
cue("L74>", "moss", pos=[-2.4, 0.9, 0.5], dur=2.5)
cue("L75>", "moss", pos=[-4.7, 0.9, 0.5], dur=3.0)
cue("L76", "moss", pos=[-6.7, 0.9, 0.5], yaw=90)
cue("L76+0.1", "moss", pos=[-4.8, 0.9, 0.5], dur=3.3)
# the Long Man (head x; body runs away up the towpath)
cue(0, "long", x=22.5, turn=0, hidden=False)
cue("L02", "long", hidden=True)
cue("L17", "long", x=22.5, turn=0, hidden=False)
cue("L20", "long", hidden=True)
cue("L22", "long", x=19.0, turn=0, hidden=False)
cue("L31>", "long", hidden=True)
cue("L41", "long", x=12.0, turn=1, hidden=False)
cue("L43", "long", hidden=True)
cue("L49", "long", x=5.0, turn=1, hidden=False)
cue("L57", "long", hidden=True)
cue("L63", "long", x=5.0, turn=1, hidden=False)
cue("L65", "long", hidden=True)
cue("L66.2", "long", x=5.0, turn=1, hidden=False)
cue("L68>", "long", hidden=True)
# the hatch and the bolt
cue(0, "hatch", open=0.0)
cue("L04", "hatch", open=1.0)
cue("L06", "hatch", open=0.0)
cue("L08", "hatch", open=1.0)
cue("L10", "hatch", open=0.0)
cue("L14.2", "hatch", open=1.0)
cue("L32", "hatch", open=0.0)
cue("L36", "hatch", open=1.0)
cue("L43", "hatch", open=0.0)
cue("L57", "hatch", open=0.0)
cue("L58", "hatch", open=1.0, dur=1.6)
cue("L59", "hatch", open=0.0)
cue("L65.1", "hatch", open=1.0, dur=1.6)
cue(0, "bolt", on=False)
cue("L43+0.9", "bolt", on=True)
cue("L65+0.7", "bolt", on=False)
# the bunk window: condensation, wiped in a second
cue(0, "wipe", to=0.0)
cue("L48+0.15", "wipe", to=1.0, dur=1.0)
cue("L53", "wipe", to=0.55)
cue("L57", "wipe", to=0.0)
cue(0, "flat", on=False)
cue("L72", "flat", on=True)
cue("L73", "flat", on=False)
cue(0, "tally", on=False)
cue("P03", "tally", on=True)
cue("L73", "tally", on=False)

# --------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L14", "kind": "click", "db": -26},
    {"at": "L14.2", "kind": "click", "db": -26},
    {"at": "L43.1", "kind": "click", "db": -16},
    {"at": "L46", "kind": "knock", "pattern": [0, 0.5, 1.15, 1.6], "tone": "soft", "db": -24},
    {"at": "L48.1", "kind": "whoosh", "db": -26, "dur": 1.0},
    {"at": "L49", "kind": "sting", "db": -11},
    {"at": "L54", "kind": "click", "db": -22},
    {"at": "L65", "kind": "click", "db": -16},
    {"at": "L65.1", "kind": "creak", "db": -22, "dur": 1.6},
    {"at": "L76>", "kind": "bell", "db": -17, "dur": 1.6},
]
story = {
    "slug": "ep27-towpath",
    "title": "Every morning, something on the towpath says good morning in my voice",
    "made_for_kids": False,
    "premise": "I live on a narrowboat with my old dog, and each autumn dawn a voice outside says good morning in my voice, one mooring ring nearer, while the dog climbs the steps to meet it.",
    "twist": "It never greeted me. On a boat everyone aboard is crew, a dog too, and when I stopped saying good morning to her, something came and called the roll for me, to her, in my voice.",
    "world": "a navy narrowboat moored on a still canal in autumn fog, a gravel towpath with iron mooring rings along the stone edge, willows on the far bank",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#9be37a",
    "caption": {"ink": "#0a0d0c", "stroke_add": 2, "shadow": 0.8},
    "key_stroke": 2,
    "gap": 0.12,
    "tail": 0.25,
    "look": {"fog": "#c2cac9", "fog_density": 0.06, "fog_start": 3.0, "sky": "#c2cac9", "sky_strength": 0.95,
             "exposure": 0.05},
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
                  {"at": "L10", "voices": ["drone", "pad", "pulse"], "energy": 0.36},
                  {"at": "L21", "voices": ["drone", "pad", "pulse"], "energy": 0.42},
                  {"at": "L32", "voices": ["drone", "pad", "pulse"], "energy": 0.46},
                  {"at": "L44", "voices": ["drone", "pad"], "energy": 0.3},
                  {"at": "L49", "voices": ["drone", "pad", "choir"], "energy": 0.5},
                  {"at": "L54", "voices": ["pad"], "energy": 0.25},
                  {"at": "L57", "voices": ["pad", "drone"], "energy": 0.3},
                  {"at": "L65", "voices": ["piano", "pad"], "energy": 0.3},
                  {"at": "P02", "voices": ["piano", "pad", "drone"], "energy": 0.4, "mode": "major", "root": 50},
                  {"at": "L76", "voices": ["pad"], "energy": 0.25},
              ]},
    "sound": {"floor": "wood", "steps_db": -24,
              "ambience": [
                  {"kind": "water", "from": 0, "to": "end", "lufs": -34},
                  {"kind": "wind", "from": 0, "to": "L10", "lufs": -44},
                  {"kind": "wind", "from": "L71", "to": "end", "lufs": -44},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "L49", "keep": ["sting"]}]},
}
story = remap(story)
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
