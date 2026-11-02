"""Writes ../story.json for ep21 "snow-plough" (script.md, writer 2026-11-02).

Run from anywhere: python stories/ep21-snow-plough/generator/make_story.py
The words are in lines.json beside this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads (the drive up and down the road, the light of the day, the headlights, the Marker's
places), the score and the sound.

Cameras are in the PLOUGH's frame (it stays at the origin facing +y; set.py slides and turns the world round it).
W2P() turns a world point into that frame for a given drive position. Interiors sit far off: Odile's room at
(500, 0) and the hut's stove room at (500, 300), in plain world coordinates.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

PX = 0.6                 # the plough's lane
EDGE_Y = 740.5           # where the outer half of the road ends now
MK_FINAL = (0.6, 741.2)  # the Marker, on the new edge
S_STOP = MK_FINAL[1] + 4.4

# ---------------------------------------------------------------------------------------------------- lines
LOOP = 0.25
HOLDS = {}
# the tally hold after L65 (not narrated), and the loop gap at the end
i65 = next(i for i, l in enumerate(lines) if l["id"] == "L65")
lines.insert(i65 + 1, {"id": "P03", "pause": 1.6, "chunks": []})
lines.append({"id": "P04", "pause": LOOP, "chunks": []})
# length: the script's own fallback (two wipers words after L53), then breaths where the picture needs them
i53 = next(i for i, l in enumerate(lines) if l["id"] == "L53")
lines.insert(i53 + 1, {"id": "L53b", "who": "narrator", "chunks": [["The wipers kept", "The wipers kept"], ["TICKING.", "ticking."]]})
HOLDS = {"P01": 1.0, "P02": 1.3, "L45": 0.45, "L64": 0.5, "L72": 0.3, "L54": 0.3, "L05": 0.35, "L13": 0.3,
         "L19": 0.3, "L27": 0.3, "L46": 0.35, "L71": 0.6, "L66": 0.25, "L62": 0.3}
for ln in lines:
    if ln["id"] in HOLDS:
        if "pause" in ln:
            ln["pause"] = HOLDS[ln["id"]]
        else:
            ln["gap"] = HOLDS[ln["id"]]
TEMPO = {}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]



MAP = {}


def ref(lid, k):
    """The new index of the first caption piece of the script's chunk k, once long chunks are split."""
    return f"{lid}.{MAP[lid][k]}"


def split_chunks(chunks, lid=None):
    """Captions run two or three words at a time (house rule): split any longer chunk, spoken text alongside."""
    out, starts = [], []
    for cap, spk in chunks:
        starts.append(len(out))
        cw, sw = cap.split(), spk.split()
        n = len(cw)
        if len(cw) != len(sw) or (n <= 3 and len(cap) <= 18):
            out.append([cap, spk])
            continue
        k = max(2 if len(cap) > 18 and n >= 2 else 1, -(-n // 3))
        sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
        i = 0
        for sz in sizes:
            out.append([" ".join(cw[i:i + sz]), " ".join(sw[i:i + sz])])
            i += sz
    if lid:
        MAP[lid] = starts
    return out


for ln in lines:
    if ln.get("chunks"):
        ln["chunks"] = split_chunks(ln["chunks"], ln["id"])

# the word check: Whisper writes numbers above twenty as digits and "plow" the American way, so the spoken text
import re
SAY = [(r"\b[Ff]orty-first\b", "41st"), (r"\b[Ff]orty-one\b", "41"), (r"\b[Tt]wenty-three\b", "23"),
       (r"\b[Tt]wenty-one\b", "21"), (r"\b[Ff]orty\b", "40"), (r"\bploughed\b", "plowed"), (r"\b[Pp]lough\b", "plow")]
for ln in lines:
    for ch in ln.get("chunks", []):
        for pat, rep in SAY:
            ch[1] = re.sub(pat, rep, ch[1])

# ---------------------------------------------------------------------------------------------------- cast
cast = {
    "me": {"age": "adult", "skin": "#e0b08a", "shirt": "#2f5fa8", "pattern": "solid", "collar": "#27497f",
           "pants": "#2b2f38", "shoes": "#1c1d21", "sleeves": "long", "hair": "cap", "hair_c": "#5a3a22",
           "hat": "beanie", "hat_c": "#8d9096", "face": {"eyes": "round", "brows": True, "ink": "#161012"}},
    "odile": {"age": "adult", "skin": "#e8c4a0", "shirt": "#3f6b4a", "pattern": "knit", "collar": "#34583d",
              "pants": "#4a4038", "shoes": "#2a2420", "sleeves": "long", "hair": "bun", "hair_c": "#f1f1f1",
              "hat": "none", "extras": ["scarf"], "extra_c": "#b9a77c", "height": 0.95,
              "face": {"eyes": "tired", "brows": True, "ink": "#1a1214", "bags": True}},
    "bram": {"age": "adult", "skin": "#c58f6a", "shirt": "#1f2f55", "pattern": "solid", "collar": "#192544",
             "pants": "#3a3a40", "shoes": "#1c1d21", "sleeves": "long", "hair": "cap", "hair_c": "#3a2a1c",
             "hat": "beanie", "hat_c": "#c9b9a0", "height": 1.03,
             "face": {"eyes": "classic", "brows": True, "ink": "#1a1210"}},
}


def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens, roll=0):
    return c([0, loc, tgt, lens] + ([roll] if roll else []))


def move(a, b, lens_a, lens_b=None):
    return c([0, a[0], a[1], lens_a], [1, b[0], b[1], lens_b or lens_a])


def W2P(w, s, th=0.0, px=PX):
    """A world point in the plough's frame when the plough is at s, heading th degrees, in lane px."""
    r = math.radians(th)
    dx, dy = w[0] - px, w[1] - s
    return [round(math.cos(r) * dx - math.sin(r) * dy, 3), round(math.sin(r) * dx + math.cos(r) * dy, 3),
            w[2] if len(w) > 2 else 0.0]


# ---------------------------------------------------------------------------------------------------- places
ME_CAB = [-0.55, 0.45, 1.57]
EYE = [-0.5, 0.9, 3.2]
POV = still(EYE, [-0.5, 30, 2.75], 19)
POV_BEND = c([0, EYE, [-0.5, 30, 2.75], 19], [1, EYE, [-3.2, 24, 2.6], 19])
FACE = still([0.55, 1.2, 3.3], [-0.55, 0.45, 3.2], 25)
FACE_BAG = still([0.0, 1.95, 3.3], [0.0, 0.4, 2.7], 14)
DASH = still([0.55, 0.6, 3.2], [-0.2, 1.4, 2.3], 26)
SHAKE_CAM = still([0.5, 1.0, 3.3], [-0.2, 1.9, 2.6], 26)
WIN_R = still([-0.1, 0.2, 3.2], [4.0, 0.7, 2.4], 22)
WIN_L = still([-1.45, 1.0, 1.5], [-2.2, 8.0, 1.2], 24)
SIDE_WIDE = still([9.0, 1.5, 2.6], [0.0, 0.8, 2.2], 20)
O_BASE = (500.0, 0.0)
H_BASE = (500.0, 300.0)
CHAIR = [O_BASE[0] - 1.0, 0.1]

# ---------------------------------------------------------------------------------------------------- the drive
drive = []
_prev = {"v": None}


def seg(t0, t1, s0, s1, th0=0.0, th1=None, x0=PX, x1=None, ease=False):
    th1 = th0 if th1 is None else th1
    x1 = x0 if x1 is None else x1
    p = _prev["v"]
    if p is not None and p != (s0, th0, x0):
        drive.append({"at": t0, "name": "drive", "s": p[0], "theta": p[1], "x": p[2]})
    drive.append({"at": t0, "name": "drive", "s": s0, "theta": th0, "x": x0})
    drive.append({"at": t1, "name": "drive", "s": s1, "theta": th1, "x": x1, "ease": ease})
    _prev["v"] = (s1, th1, x1)


# the hook, on the way down (the Marker stands at world y 1005)
seg(0, "L04>", 1050, 1032, 180)
# the evening before: the plough in Odile's yard
seg("L05", "L12>", -20, -20, 0)
# up
seg("L13", "L13>", -20, 40, 0, ease=True)
seg("L14", "L14>", 40, 90)
seg("L15", "L15>", 90, 135)
seg("L16", "L16>", 171, 173)
seg("L17", "L17>", 215, 245)
seg("L18", "L18>", 262, 292)
seg("L19", "L19>", 664, 700)
seg("L20", "L20>", 700, 735)
seg("L21", "L21>", 740, 760)
seg("L22", "L22>", 1168, 1200)
seg("L23", "L25>", 1215, 1215)
seg("L26", "L26>", 1215, 1215, 0, 180)
# down: the Marker at 1005 (L29 to L33), at 855 (L34 to L37), at 795 (L38 to L40)
seg("L27", "L27>", 1215, 1185, 180)
seg("L28", "L28>", 1150, 1120, 180)
seg("L29", "L29>", 1065, 1045, 180)
seg("L30", "L30>", 1032, 1024, 180)
seg("L31", "L31>", 1022, 1020, 180)
seg("L32", "L32>", 1018, 1008, 180)
seg("L33", "L33>", 990, 940, 180)
seg("L34", "L34>", 900, 880, 180)
seg("L35", "L35>", 878, 870, 180)
seg("L36", "L36>", 868, 868, 180)
seg("L37", "L37>", 862, 830, 180)
seg("L38", "L38>", 826, 808, 180)
seg("L39", "L40>", 806, 806, 180)
seg("L41", "L41>", 806, 790, 180)
seg("L42", "L45>", 790, 756, 180)
seg("L46", "L46>", 752.5, 751, 180)
seg("L47", "L47>", 751, 748.5, 180)
seg("L48", "L49>", 748.5, S_STOP, 180, ease=True)
seg("L50", "L65>", S_STOP, S_STOP, 180)  # L53b is inside it
seg("P03", "P03>", S_STOP, S_STOP, 180)
seg("L66", "L66>", S_STOP, 712, 180, x1=-1.9, ease=True)
seg("L67", "L67>", 240, 240, 180)
seg("L68", "L68>", -5, -5, 180)
seg("L69", "L71>", -5, -5, 180)
seg("L72", "L73>", 700, 700, 0)

cues = list(drive)
cues += [
    # the light of the day: night until L53, then one continuous ramp to grey-lilac, then pale gold
    {"at": 0, "name": "tod", "v": 0.0},
    {"at": "L53", "name": "tod", "v": 0.0},
    {"at": "L66", "name": "tod", "v": 1.0},
    {"at": "L67", "name": "tod", "v": 1.35},
    {"at": "L72", "name": "tod", "v": 1.95},
    {"at": "end", "name": "tod", "v": 2.0},
    # headlights: sink to 25% over 1.2 s at L42, hold through P01, climb back over 1.4 s from L45 (never to black)
    {"at": "L42", "name": "lights", "g": 0.25, "dur": 1.2},
    {"at": "L45", "name": "lights", "g": 1.0, "dur": 1.4},
    # the Marker: always found where it already is, never seen moving
    {"at": 0, "name": "marker", "x": 3.0, "y": 1005, "vis": True, "drift": False, "snow": True},
    {"at": "L05", "name": "marker", "vis": False, "x": 3.0, "y": 1005},
    {"at": "L29", "name": "marker", "x": 3.0, "y": 1005, "vis": True, "drift": False, "snow": True},
    {"at": "L34", "name": "marker", "x": 2.2, "y": 855, "vis": True, "drift": False, "snow": True},
    {"at": "L36", "name": "marker", "x": 2.2, "y": 855, "vis": True, "drift": True, "snow": True},
    {"at": "L38", "name": "marker", "x": 2.0, "y": 795, "vis": True, "drift": False, "snow": True, "kg": 2.5},
    {"at": "L41", "name": "marker", "x": 2.0, "y": 795, "vis": False},
    {"at": "L46", "name": "marker", "x": MK_FINAL[0], "y": MK_FINAL[1], "vis": True, "drift": False, "snow": True},
    {"at": "L64", "name": "marker", "x": MK_FINAL[0], "y": MK_FINAL[1], "vis": False},
    {"at": "L65", "name": "square", "on": True},
    {"at": 0, "name": "slide", "on": False},
    {"at": "L27", "name": "slide", "on": True},
    {"at": 0, "name": "season", "v": "snow"},
    {"at": "L72", "name": "season", "v": "spring"},
    {"at": 0, "name": "psnow", "on": False},
    {"at": "L05", "name": "psnow", "on": True},
    {"at": "L13+0.4", "name": "psnow", "on": False},
    {"at": "L72", "name": "plough", "on": False},
    {"at": 0, "name": "van", "mode": "none"},
    {"at": "L22", "name": "van", "mode": "parked"},
    {"at": "L26", "name": "van", "mode": "follow"},
    {"at": "L72", "name": "van", "mode": "none"},
    {"at": 0, "name": "bag", "where": "none"},
    {"at": "L24", "name": "bag", "where": "hand"},
    {"at": "L25", "name": "bag", "where": "seat"},
    {"at": "L69", "name": "bag", "where": "none"},
    {"at": "L65", "name": "tally", "on": False},
    {"at": "P03", "name": "tally", "on": True},
    {"at": "L66", "name": "tally", "on": True},
    {"at": "L09", "name": "table", "keys": True},
    {"at": "L13", "name": "table"},
    {"at": "L69", "name": "table", "keys": True, "bag": True, "glass": True},
    {"at": "L71", "name": "table", "keys": True, "bag": True, "glass": True, "cups": True},
    {"at": "L72", "name": "table"},
    {"at": "L72", "name": "newpost", "on": True, "glow": 0.25, "dur": 0.1},
    {"at": "L73", "name": "newpost", "on": True, "glow": 1.0, "dur": 1.6},
]

# ---------------------------------------------------------------------------------------------------- shots
# (at, what, step, camera, extra). step 1 on ones (the scare), 4 on fours (locked), else 2
SHOTS = [
    # 01 the count
    (0, "POV through the windscreen, wipers sweeping, a glint slides past", 2, POV, {}),
    ("L02", "my face in green dash light", 2, FACE, {}),
    ("L03", "the Marker glimpse at the edge of the beams", 2,
     still(EYE, W2P((3.0, 1005, 1.1), 1040, 180), 30), {}),
    ("L04", "close on two amber eyes", 2, still(EYE, W2P((3.0, 1005, 1.2), 1030, 180), 62), {}),
    (ref("L04", 2), "a normal post's single glint", 2, still(EYE, W2P((3.0, 990, 1.7), 1030, 180), 45), {}),
    # 02 the promise
    ("L05", "Odile's cottage window lit warm in falling snow", 2,
     still([-1.5, -5.5, 1.7], [-7.4, 0.5, 1.5], 26), {}),
    ("L06", "the plough in her yard under a hood of snow", 2, still([6.0, -6.0, 2.2], [0.0, 0.8, 2.2], 20), {}),
    ("L07", "Odile in her chair by the lamp, coughing", 2,
     still([O_BASE[0] + 0.9, -1.3, 1.3], [CHAIR[0], 0.2, 0.95], 30), {"snow": 0}),
    ("L08", "the far light high on the mountain", 2, still([-5.0, -8.0, 1.6], [-14.0, 300.0, 6.5], 36), {}),
    ("L09", "the keys on the table", 2, still([O_BASE[0] + 0.5, -0.8, 1.35], [O_BASE[0] + 0.35, 0.2, 0.8], 32), {"snow": 0}),
    (ref("L09", 4), "Odile's face", 2, still([O_BASE[0] + 0.6, -0.35, 1.3], [CHAIR[0], 0.1, 1.25], 32), {"snow": 0}),
    ("L10", "my face, nodding", 2, still([CHAIR[0] + 0.5, -0.5, 1.55], [O_BASE[0] + 1.0, 0.9, 1.5], 34), {"snow": 0}),
    ("L11", "Odile, one hand raised flat", 2, still([O_BASE[0] + 0.7, -0.6, 1.4], [CHAIR[0], 0.1, 1.15], 26), {"snow": 0}),
    ("L12", "close on her, then a cough", 2, still([O_BASE[0] + 0.5, -0.3, 1.3], [CHAIR[0], 0.1, 1.28], 42), {"snow": 0}),
    # 03 up
    ("L13", "side wide of the plough pulling out", 2, SIDE_WIDE, {}),
    ("L14", "POV, all white ahead", 2, POV, {}),
    ("L15", "the post line on the right, glints fading up one after another", 2,
     still(EYE, [1.2, 30, 2.0], 17), {}),
    ("L16", "close on one post, snow on its cap", 2, still([0.4, 0.8, 3.1], [2.4, 9.0, 1.7], 40), {}),
    ("L17", "POV, the beams finding the next glint", 2, POV, {}),
    ("L18", "my face, lips moving", 2, FACE, {}),
    ("L19", "the cab, a slow small shake", 2, SHAKE_CAM, {"hand": 0.02}),
    ("L20", "the right-hand window, black below the post line", 2, WIN_R, {}),
    ("L21", "my face, worried", 2, FACE, {}),
    (ref("L21", 2), "the road ahead again", 2, POV, {}),
    ("L22", "the fortieth post, then the hut and the white van", 2, still(EYE, [-2.5, 40, 1.6], 17), {}),
    ("L23", "Bram by the stove", 2, still([H_BASE[0] + 0.3, H_BASE[1] - 1.7, 1.45], [H_BASE[0] + 0.6, H_BASE[1] + 0.6, 1.4], 30), {"snow": 0}),
    ("L24", "the white bag at the end of Bram's sleeve", 2,
     still([H_BASE[0] - 0.3, H_BASE[1] - 1.9, 1.5], [H_BASE[0] + 0.5, H_BASE[1] + 0.5, 1.3], 30), {"snow": 0}),
    ("L25", "the bag on the passenger seat", 2, FACE_BAG, {}),
    ("L26", "the plough turning at the top, white van lights behind", 2, still([10.0, -1.0, 3.0], [0.0, 0.8, 2.2], 18), {}),
    # 04 down
    ("L27", "POV, the line now on the left", 2, POV, {}),
    ("L28", "my face, lips moving", 2, FACE, {}),
    ("L29", "POV, a wide glint pair fading up in the line", 2, still(EYE, [-1.8, 40, 1.8], 17), {}),
    ("L30", "the Marker in the post line", 2, still(EYE, W2P((3.0, 1005, 0.8), 1028, 180), 36), {}),
    ("L31", "my face, scared", 2, FACE, {}),
    ("L32", "from my window as the plough passes it", 2, WIN_L, {}),
    ("L33", "POV, normal glints", 2, still(EYE, [-1.5, 30, 2.0], 16), {}),
    ("L34", "the Marker ahead in the beams", 2, still(EYE, W2P((2.2, 855, 0.9), 892, 180), 30), {}),
    ("L35", "closer, one glint far down the line sitting lower", 2, still(EYE, W2P((2.2, 855, 0.9), 874, 180), 24), {}),
    ("L36", "the snow heaped against its front", 2, still(EYE, W2P((2.2, 855.5, 0.6), 868, 180), 42), {}),
    ("L37", "POV, the low glint, round the bend", 2, POV_BEND, {}),
    ("L38", "the Marker at the edge of my lane", 2, still(EYE, W2P((2.0, 795, 1.0), 817, 180), 28), {}),
    ("L39", "the arm lines and blunt hands", 2, still(W2P((2.7, 799.3, 0.95), 806, 180), W2P((2.0, 795.3, 0.7), 806, 180), 32), {}),
    ("L40", "my face, scared", 2, FACE, {}),
    ("L41", "a normal glint fading past", 2, still(EYE, [-3.0, 8.0, 1.8], 24), {}),
    ("L42", "POV, the beams sinking", 2, POV, {}),
    ("L43", "the gauges dimming, wipers going", 2, DASH, {}),
    ("L44", "my face in near dark, the bag a pale shape", 2, FACE_BAG, {}),
    ("L45", "POV, the beams climb back on empty snow", 2, POV, {}),
    ("L46", "the Marker in the middle of the road", 1, still(EYE, W2P(MK_FINAL + (1.0,), 751.8, 180), 26), {}),
    ("L47", "side wide: the plough and the Marker almost touching", 1, still([-9.0, 4.0, 2.2], [0.0, 6.5, 1.0], 24), {}),
    ("L48", "my face, thrown forward", 1, FACE, {}),
    ("L49", "low on the blade, snow sheeting off", 1, still([3.5, 6.5, 0.6], [0.3, 3.8, 0.8], 24), {}),
    ("L50", "blade edge and the two eyes", 1, still([-2.6, 3.9, 0.8], [0.0, 4.5, 1.1], 28), {}),
    ("L51", "the mirror: two white lights stopping", 1, still([-1.6, 0.0, 3.0], [-0.3, -14.0, 1.5], 24), {}),
    (ref("L51", 2), "Bram in his own cab", 1, still([-0.5, -9.2, 1.95], [-0.5, -12.6, 1.9], 38), {}),
    ("L52", "the Marker through the glass, unmoved", 2,
     still([-0.5, 0.9, 3.2], W2P(MK_FINAL + (1.0,), S_STOP, 180), 20), {}),
    ("L53", "same frame, the dawn beginning", 4,
     still([-0.5, 0.9, 3.2], W2P(MK_FINAL + (1.0,), S_STOP, 180), 20), {}),
    # 05 the edge
    ("L54", "over my shoulder, past the Marker", 2, still([0.15, 0.8, 3.3], [0.6, 15.0, 1.2], 22), {}),
    ("L55", "the raw edge beyond the Marker", 2, still([0.0, 2.9, 2.2], W2P((0.6, 738.0, -2.0), S_STOP, 180), 20), {}),
    ("L56", "wide from the bend above: the scar of the slide", 2,
     still(W2P((-14.0, 800.0, 22.0), S_STOP, 180), W2P((4.0, 705.0, -6.0), S_STOP, 180), 20), {}),
    ("L57", "the same stretch, broken", 2,
     still([0.7, 0.8, 3.3], W2P((2.0, 722.0, -5.0), S_STOP, 180), 20), {}),
    ("L58", "the slab below, post twenty-three upright on it", 2,
     still(W2P((7.0, 748.0, 6.0), S_STOP, 180), W2P((2.9, 690.0, -12.5), S_STOP, 180), 28), {}),
    ("L59", "POV along the posts, off the edge to its glint", 2, still(EYE, [-1.5, 40, 0.0], 16), {}),
    ("L60", "my face, scared easing", 2, FACE, {}),
    ("L61", "the snow lip of the edge", 2,
     still(W2P((-1.6, 741.3, 0.7), S_STOP, 180), W2P((1.2, 740.3, -0.3), S_STOP, 180), 28), {}),
    ("L62", "low wide: the Marker on the new edge, the drop behind", 2, still([-3.6, 3.7, 1.0], [0.2, 5.0, 0.9], 34), {}),
    ("L63", "Bram knocking at my door", 2, still([0.3, 0.3, 3.0], [1.7, 0.3, 2.8], 34), {}),
    ("L64", "the road ahead, the edge, nothing standing on it", 2, still(EYE, W2P((0.6, 738.0, 0.0), S_STOP, 180), 18), {}),
    ("L65", "the wide square pressed in the snow", 2, still([2.2, 8.5, 2.4], [0.6, 4.4, 0.0], 26), {}),
    ("P03", "the tally on the blade: two rust-orange strokes", 4, still([0.05, 5.21, 0.95], [0.34, 3.85, 0.73], 38), {"hand": 0.0}),
    # 06 home
    ("L66", "side wide: the plough creeping along the inside bank, the van behind", 2,
     still([-8.0, 2.0, 2.4], [0.0, 0.8, 2.2], 20), {}),
    ("L67", "sunrise over the stone cottages", 2, still(EYE, [4.0, 40, 3.6], 18), {}),
    ("L68", "Odile's window, warm and steady", 2, still(EYE, W2P((-6.8, -20.5, 1.5), -5, 180), 30), {}),
    ("L69", "the bag on her table beside a glass of water", 2,
     still([O_BASE[0] + 0.5, -0.9, 1.4], [O_BASE[0] + 0.5, 0.1, 0.85], 30), {"snow": 0}),
    ("L70", "Odile looks from the bag to me", 2, still([O_BASE[0] + 0.7, -0.6, 1.4], [CHAIR[0], 0.1, 1.2], 30), {"snow": 0}),
    ("L71", "two cups on the table", 2, still([O_BASE[0] + 0.7, -0.7, 1.3], [O_BASE[0] + 0.5, 0.1, 0.85], 30), {"snow": 0}),
    (ref("L71", 2), "Odile smiles", 2, still([O_BASE[0] + 0.5, -0.35, 1.3], [CHAIR[0], 0.1, 1.28], 36), {"snow": 0}),
    ("L72", "spring: the mended road, the new post at the new edge, me beside it", 2,
     still(W2P((-0.4, 752.0, 1.5), 700, 0), W2P((0.5, 741.0, 1.2), 700, 0), 26), {}),
    ("L73", "the new post's reflector catches the low sun", 4,
     still(W2P((0.3, 743.4, 1.9), 700, 0), W2P((0.6, 740.9, 1.72), 700, 0), 42), {"hand": 0.0}),
]

shots = []
for i, (at, what, step, cam, extra) in enumerate(SHOTS):
    s = {"id": f"S{i + 1:02d}", "cam": cam, "hand": 0.006 if step == 1 else 0.004, "step": step, "what": what}
    s.update(extra)
    if step == 4:
        s["hand"] = 0.0
    if i:
        s["at"] = at
    shots.append(s)

# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "hide_parts": [], "sit": False,
           "blink": True}
acting = {"me": [], "odile": [], "bram": []}


def put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, "hidden": False, **NEUTRAL, "expr": "worried", **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def talk(who, a, b):
    acting[who].append({"from": a, "to": b, "mouth": [0.5, 0.5], "flap": True})


LEGS = ["leg-1", "leg1"]
DRIVE = {"yaw": 180, "hide_parts": LEGS, "arms": [62, 62], "side": [-8, -8]}
# me: in the cab for the hook, in Odile's room for one shot, back in the cab, then spring
put("me", 0, ME_CAB, expr="worried", **DRIVE)
talk("me", "L02", "L02>")
hide("me", "L05")
put("me", "L10", [O_BASE[0] + 1.0, 0.9], yaw=-90, expr="neutral", head=[0, 6])
hide("me", "L11")
put("me", "L13", ME_CAB, expr="neutral", **DRIVE)
talk("me", "L18", "L18>")
key("me", "L21", expr="worried")
talk("me", "L28", "L28>")
key("me", "L29", expr="worried")
key("me", "L31", expr="scared")
key("me", "L38", expr="worried")
key("me", "L40", expr="scared")
key("me", "L43", expr="scared", tremble=1.5)
key("me", "L44", expr="terrified", tremble=1.2)
key("me", "L46", expr="wide", tremble=0)
key("me", "L48", expr="scared", lean=-22, arms=[70, 70], blend=0.12)
key("me", "L48>", lean=0, blend=0.5)
key("me", "L51", expr="wide")
key("me", "L52", expr="scared")
key("me", "L54", expr="worried")
key("me", "L60", expr="scared")
key("me", "L60>", expr="neutral", blend=0.6)
key("me", "L66", expr="neutral")
hide("me", "L69")
put("me", "L72", W2P((-0.2, 743.2), 700, 0)[:2] + [0.0], yaw=150, expr="soft",
    **{k: v for k, v in NEUTRAL.items() if k not in ("hide_parts",)})
# Odile: in her chair by the lamp
hide("odile", 0)
put("odile", "L07", [CHAIR[0], CHAIR[1], -0.17], yaw=90, expr="neutral", sit=True, head=[0, 18])
key("odile", "L07", expr="neutral")
key("odile", "L07+1.0", head=[14, 22], tremble=3.0, blend=0.1)
key("odile", "L07+1.6", head=[0, 6], tremble=0, blend=0.3)
key("odile", "L09", head=[0, 4])
talk("odile", ref("L09", 3), "L09>")
key("odile", "L11", arms=[80, 85], expr="neutral")
talk("odile", "L11", "L11>")
key("odile", "L12", arms=[0, 0], blend=0.3)
talk("odile", "L12", "L12>")
key("odile", "L12>", tremble=3.0, blend=0.1)
hide("odile", "L13")
put("odile", "L70", [CHAIR[0], CHAIR[1], -0.17], yaw=90, expr="neutral", sit=True, head=[0, 10])
key("odile", "L71", expr="neutral")
key("odile", ref("L71", 2), expr="grin", head=[0, 2], blend=0.5)
# Bram: the hut, then his van, then at my door
hide("bram", 0)
put("bram", "L23", [H_BASE[0] + 0.6, H_BASE[1] + 0.5], yaw=0, expr="grin", head=[0, 4])
key("bram", "L24", arms=[0, 84], blend=0.35)
hide("bram", "L26")
put("bram", ref("L51", 2), [-0.5, -12.6, 0.3], yaw=180, expr="scared", hide_parts=LEGS, arms=[60, 60])
hide("bram", "L52")
put("bram", "L63", [1.65, 0.3, 1.1], yaw=-90, expr="scared", arms=[0, 0])
key("bram", "L63", arms=[75, 75], blend=0.2)
key("bram", ref("L63", 2), expr="worried", blend=0.5)
hide("bram", "L64")

# ---------------------------------------------------------------------------------------------------- music and sound
music = {"root": 47, "mode": "phrygian", "bpm": 66, "seed": 21,
         "sections": [
             {"at": 0, "voices": ["drone", "pulse"], "energy": 0.35},
             {"at": "L05", "voices": ["drone", "pad"], "energy": 0.22},
             {"at": "L13", "voices": ["drone", "pad", "pulse"], "energy": 0.35},
             {"at": "L19", "voices": ["drone", "pulse"], "energy": 0.45},
             {"at": "L22", "voices": ["drone", "pad"], "energy": 0.28},
             {"at": "L27", "voices": ["drone", "pulse"], "energy": 0.4},
             {"at": "L34", "voices": ["drone", "pulse", "choir"], "energy": 0.5},
             {"at": "L41", "voices": ["drone", "pulse", "choir"], "energy": 0.6},
             {"at": "L45", "voices": ["drone", "pulse", "choir"], "energy": 0.7},
             {"at": "L52", "voices": ["drone"], "energy": 0.25},
             {"at": "L54", "voices": ["drone", "pad"], "energy": 0.4},
             {"at": "L66", "voices": ["drone", "pad", "piano"], "energy": 0.4, "mode": "major", "root": 47},
             {"at": "L72", "voices": ["pad", "piano"], "energy": 0.3},
         ]}
sound = {"floor": "wood", "steps_db": -26,
         "ambience": [
             {"kind": "wind", "from": 0, "to": "end", "lufs": -33},
             {"kind": "hum", "from": 0, "to": "L05", "lufs": -38},
             {"kind": "room", "from": "L07", "to": "L08", "lufs": -34},
             {"kind": "room", "from": "L09", "to": "L13", "lufs": -34},
             {"kind": "hum", "from": "L13", "to": "L23", "lufs": -38},
             {"kind": "room", "from": "L23", "to": "L25", "lufs": -34},
             {"kind": "hum", "from": "L25", "to": "L66", "lufs": -38},
             {"kind": "room", "from": "L69", "to": "L72", "lufs": -34},
         ],
         "sfx": [
             {"at": "L19+0.2", "kind": "creak", "db": -14, "dur": 2.4},
             {"at": "L29", "kind": "sting", "db": -16},
             {"at": "L35", "kind": "riser", "db": -22, "dur": 1.6},
             {"at": "L43", "kind": "thud", "db": -16},
             {"at": "L45", "kind": "riser", "db": -16, "dur": 1.2},
             {"at": "L46", "kind": "hit", "db": -8},
             {"at": "L48", "kind": "whoosh", "db": -12, "dur": 1.8},
             {"at": "L57", "kind": "creak", "db": -10, "dur": 3.4},
             {"at": ref("L63", 1), "kind": "knock", "pattern": [0, 0.28, 0.56], "tone": "glass_soft", "db": -10},
             {"at": "L73>", "kind": "click", "db": -10},
         ],
         "music_drops": [{"from": "L44>", "to": "L45"},
                         {"from": "P02", "to": "L52", "keep": ["hit"]}]}

story = {
    "slug": "ep21-snow-plough",
    "title": "There were forty posts on the way up the mountain. Coming down, I counted forty-one",
    "made_for_kids": False,
    "premise": "A neighbour's plough keys, one instruction (count the posts to the top, and if you can't see the next one, stop) and a promise to bring her tablets by morning. On the way down in the last dark before dawn there is a forty-first road post, too short, wide as a car, with two reflectors for eyes, and each sighting it is further onto the road.",
    "twist": "The outer half of the road slid away at post twenty-three while I was at the top. The forty I trusted included one now over the edge, and the extra one was standing exactly where the road ends. It was keeping the count true by standing in the gap.",
    "world": "a single-lane mountain pass road in heavy snow, a yellow plough with a broken beacon, orange snow posts with amber reflectors, a stone hut and a village at the foot",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffd23f",
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#17233d", "fog_density": 0.014, "fog_start": 6.0, "sky": "#17233d", "sky_strength": 1.0,
             "exposure": 0.0},
    "grade": {"shadows": [-0.02, 0.0, 0.05], "highlights": [0.02, 0.01, -0.02], "saturation": 0.95, "contrast": 1.08, "red_line": 0.79,
              "vignette": 0.4, "bloom": 0.28, "grain": 0.013},
    "phonemes": {"Odile": "oʊdˈil"},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [{"at": "L19", "kind": "shake", "dur": 1.6, "amp": 0.6, "fade": 0.5}],
    "music": music,
    "sound": sound,
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
