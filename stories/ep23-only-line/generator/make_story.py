"""Writes ../story.json for ep23 "only-line", the redo (script.md, 2026-11-02): In this town the quiet ones fade.

Run from anywhere: python stories/ep23-only-line/generator/make_story.py
The words are in lines.json next to this file (the script's lines, chunk for chunk). Everything else is here: the
cast, the shots and cameras, the acting, the cues set.py reads (the mood of the light, the fades, costumes, the
throne, the audience), the score and the sound.

Places (set.py's metres, z up). The stage runs x -9 .. 9, y 0 (the lip) .. 7.2 (the brick back wall); a character
with yaw 0 faces -y (the house). Stage left is +x: four curtain legs hang there at y 3.3 .. 5.7, inner edge x 3.7.
The town street is at x = -40 (a brick terrace along y = 4.5) and the stage door at x = +40 (a wall at y = 3.2).
yaw 180 faces +y, yaw 90 faces +x, yaw -90 faces -x.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

# Captions show two or three words at a time (check blocks more): a longer chunk is cut into pieces of at most
# three words, never ending a piece on a word that needs the next one.
WEAK = {"the", "a", "an", "of", "to", "in", "on", "at", "my", "your", "his", "her", "its", "our", "and", "i", "we", "so",
        "with", "for", "from", "that", "then", "it", "was", "were", "is", "i'm", "i've", "you're", "who", "what", "if",
        "but", "as", "by", "into", "all", "out", "off", "like", "than", "didn't", "don't", "can't", "behind", "not"}


def _best_split(cw):
    """The cheapest way to cut words into pieces of 1 to 3: a piece that ends on a weak word costs 1, a one-word
    piece 1.5, an uneven pair a little, and a break after punctuation is a bonus."""
    n = len(cw)
    best = {0: (0.0, [])}
    for i in range(1, n + 1):
        opts = []
        for z in (1, 2, 3):
            j = i - z
            if j < 0 or j not in best:
                continue
            last = cw[i - 1]
            punct = last[-1] in ",.?!\""
            cost = best[j][0] + (1.5 if z == 1 else 0.0)
            if i < n:
                if not punct and last.strip('",.!?').lower() in WEAK:
                    cost += 1.0
                if punct:
                    cost -= 0.4
            cost += 0.05 * abs(z - 2)
            opts.append((cost, best[j][1] + [z]))
        best[i] = min(opts)
    return best[n][1]


def rechunk(chunks):
    out = []
    for cap, sp in chunks:
        cw, sw = cap.split(), sp.split()
        if len(cw) <= 3 or len(cw) != len(sw):
            out.append([cap, sp])
            continue
        k = 0
        for z in _best_split(cw):
            out.append([" ".join(cw[k:k + z]), " ".join(sw[k:k + z])])
            k += z
    return out


for ln in lines:
    if "chunks" in ln and ln["chunks"]:
        ln["chunks"] = rechunk(ln["chunks"])

BYID = {ln["id"]: ln for ln in lines}


def CH(lid, start):
    """The time reference of the chunk of line `lid` whose caption starts with `start` (so a re-chunk can't shift it)."""
    for k, (cap, _) in enumerate(BYID[lid]["chunks"]):
        if cap.strip('"').lower().startswith(start.lower()):
            return f"{lid}.{k}"
    raise SystemExit(f"{lid} has no chunk starting {start!r}: {[c[0] for c in BYID[lid]['chunks']]}")


# ---------------------------------------------------------------------------------------------------- loop
# S57 holds, then the 0.25 s tail and the loop cut to S01 (the same man in daylight)
TEMPO = {"L11": 0.88, "L13": 0.85, "L36": 0.78, "L38": 0.85, "L52": 0.88, "L54": 0.9}
SPOKEN = {("L36", 0): "the lights, sank"}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]
    for k, ch in enumerate(ln.get("chunks", [])):
        if (ln["id"], k) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], k)]

# ---------------------------------------------------------------------------------------------------- places
TX, SDX = -40.0, 40.0


def T(x, y, z=None):
    return [TX + x, y] if z is None else [TX + x, y, z]


def S(x, y, z=None):
    return [SDX + x, y] if z is None else [SDX + x, y, z]


LEGY = [3.3, 4.1, 4.9, 5.7]
MX = [-3.2, -2.05, -0.9, 0.25, 1.2, 2.3]
MARKS = [[x, round(3.2 - 0.07 * x * x, 2)] for x in MX]     # p1..p5, then the yellow cross
YEL = MARKS[5]
KING = [0.0, 2.0]
GH = [-2.4, 1.0]                                               # the ghost light
ROW3 = (-0.58, -4.5)
ROW3_POS = [ROW3[0], ROW3[1], -0.45]
LIP = {"p1": -3.0, "p2": -2.1, "p3": -1.2, "p4": -0.3, "p5": 0.6, "walt": 1.5, "me": 2.4}      # sitting on the stage lip
LIPZ = -0.51
THRONE = [0.0, 2.5, -0.06]
SM = T(1.6, 1.5)                                              # the bus-stop man
SD_W = S(-0.4, 1.4)                                           # Grandad at the stage door
SD_ME = S(0.5, 1.5)                                           # me beside him, the wall behind us both

WALT_FADE0 = 0.6

LINE_TOWN = "town"


def person(skin, shirt, pants, hair, hair_c, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": "#2a2a2e",
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "hat": "none",
         "face": {"eyes": "round", "brows": True, "ink": "#161012"}}
    d.update(kw)
    return d


cast = {
    "me": {"age": "adult", "skin": "#d9a47a", "shirt": "#c9a227", "pattern": "knit", "pattern_c": "#a8841a",
           "collar": "#8a6f16", "pants": "#2a2d3a", "shoes": "#35302c", "sleeves": "long", "hair": "cap",
           "hair_c": "#3a2616", "hat": "none", "face": {"eyes": "round", "brows": True, "ink": "#161012"}},
    "marion": {"age": "adult", "skin": "#e0b08a", "shirt": "#2f7f86", "pattern": "knit", "pattern_c": "#256a70",
               "pants": "#3a3a44", "shoes": "#2a2424", "sleeves": "long", "hair": "cap", "hair_c": "#a9a9ae",
               "extras": ["glasses"], "extra_c": "#2a2a30", "hat": "none",
               "face": {"eyes": "round", "brows": True, "ink": "#1a1214"}},
    "walt": {"age": "adult", "skin": "#c28a64", "shirt": "#6b4a2e", "pattern": "solid", "pattern_c": "#58391f",
             "pants": "#3a3530", "shoes": "#2a2220", "sleeves": "long", "hair": "cap", "hair_c": "#ececec",
             "hat": "none", "face": {"eyes": "tired", "brows": True, "ink": "#1c1612"}},
    "p1": {"age": "adult", "skin": "#8a5a40", "shirt": "#2e4f7a", "pattern": "stripes", "pattern_c": "#dfe3ea",
           "pants": "#2c2c34", "shoes": "#222226", "sleeves": "long", "hair": "spiky", "hair_c": "#15110f",
           "hat": "none", "face": {"eyes": "round", "brows": True, "ink": "#14100e"}},
    "p2": {"age": "adult", "skin": "#e8c09a", "shirt": "#5a7a4a", "pattern": "plaid", "pattern_c": "#2f4a2a",
           "pants": "#3b3a46", "shoes": "#2a2a2e", "sleeves": "long", "hair": "long", "hair_c": "#7a4a22",
           "hat": "none", "face": {"eyes": "lashes", "brows": True, "ink": "#1a1210"}},
    "p3": {"age": "adult", "skin": "#b57a56", "shirt": "#8a5c8a", "pattern": "knit", "pattern_c": "#c9a8c9",
           "pants": "#26262c", "shoes": "#2c2624", "sleeves": "short", "hair": "bun", "hair_c": "#2a1a14",
           "hat": "none", "face": {"eyes": "round", "brows": True, "ink": "#18100e"}},
    "p4": {"age": "adult", "skin": "#f0cfae", "shirt": "#3d7a4a", "pattern": "solid", "collar": "#2f6039",
           "pants": "#34343c", "shoes": "#222226", "sleeves": "long", "hair": "swoop", "hair_c": "#b8782a",
           "hat": "none", "face": {"eyes": "round", "brows": True, "ink": "#1c1210"}},
    "p5": {"age": "adult", "skin": "#7a4c36", "shirt": "#c8b890", "pattern": "plaid", "pattern_c": "#6a5a3a",
           "pants": "#2d3340", "shoes": "#2a2420", "sleeves": "long", "hair": "buzz", "hair_c": "#120e0c",
           "hat": "none", "face": {"eyes": "dot", "brows": True, "ink": "#14100e"}},
    # the town: the man at the bus stop (olive cap and a brown scarf are set.py's), a tan raincoat
    "stopman": person("#d9a47a", "#b89868", "#3c3a36", "buzz", "#8a8a8a", extras=["coat", "scarf"], extra_c="#6b4a2e",
                      face={"eyes": "round", "brows": True, "ink": "#161012"}),
    "mime": person("#f3f1ea", "#f1f1ee", "#17171b", "buzz", "#111114", pattern="stripes", pattern_c="#17171b",
                   face={"eyes": "round", "brows": True, "ink": "#141418"}),
    "wife9": person("#e6b48c", "#b8223a", "#3b3a46", "bun", "#9a9a9e", pattern="knit", pattern_c="#8f1a2e",
                    face={"eyes": "lashes", "brows": True, "ink": "#1a1012"}),
    "husband9": person("#c88a62", "#233f7a", "#2d3340", "buzz", "#b8b8b8", collar="#1c2f5c",
                       face={"eyes": "round", "brows": True, "ink": "#161012"}),
    "busker": person("#e0b08a", "#4f6f98", "#2c2c34", "long", "#4a3020", pattern="knit", pattern_c="#3f5a80",
                     face={"eyes": "round", "brows": True, "ink": "#161012"}),
    "walker1": person("#8a5a40", "#5a7a4a", "#2c2c34", "cap", "#1a1410", extras=["backscarf"], seam_c="#33426e"),
    "walker2": person("#f0cfae", "#d27a3a", "#34343c", "swoop", "#b8782a", extras=["backscarf"], seam_c="#33426e"),
    # the faded ones: ordinary townsfolk (the rig is the normal one; set.py makes them almost not there)
    "f1": person("#e0b08a", "#5a2a50", "#3a2a3a", "bun", "#6a6a6e", extras=["coat"], face={"eyes": "round", "brows": True, "ink": "#161012"}),
    "f2": person("#d9a47a", "#6a5a3a", "#3a3a40", "buzz", "#c8c8c8", pattern="knit", pattern_c="#52452c",
                 face={"eyes": "tired", "brows": True, "ink": "#161012"}),
    "f3": person("#b57a56", "#3a3f4a", "#26262c", "cap", "#1a1410", hat="hoodopen", hat_c="#3a3f4a",
                 face={"eyes": "round", "brows": True, "ink": "#161012"}),
    "f4": person("#e8c09a", "#7a9a7a", "#34343c", "long", "#5a3a22", extras=["apron"], extra_c="#6a8a6a",
                 face={"eyes": "lashes", "brows": True, "ink": "#161012"}),
}


# ---------------------------------------------------------------------------------------------------- cameras
def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return c([0, loc, tgt, lens])


def move(a, b, lens_a, lens_b=None):
    return c([0, a[0], a[1], lens_a], [1, b[0], b[1], lens_b or lens_a])


def yaw_to(a, b):
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


def face(pos, d=3.0, lens=50, ang=0.0, h=1.62, tz=1.34, push=0.0, lens2=None, z0=0.0):
    """A close-up of a standing face: the camera d metres out at `ang` degrees off the front, the face in the top
    third of the frame (above the caption band)."""
    d = d * 1.18
    a = math.radians(ang)

    def at(dd):
        return [round(pos[0] + dd * math.sin(a), 3), round(pos[1] - dd * math.cos(a), 3), h + z0]

    tgt = [pos[0], pos[1], tz + z0]
    if push:
        return c([0, at(d), tgt, lens], [1, at(d - push), tgt, lens2 or lens])
    return c([0, at(d), tgt, lens])


TRACK_L = c([0, [-0.6, -1.4, 1.5], [-0.6, 3.0, 1.35], 26], [1, [0.2, -1.4, 1.5], [0.2, 3.0, 1.35], 26])
HOUSE_WIDE = still([0.0, -8.0, 1.45], [0.8, 3.0, 1.2], 24)
RING = [(-0.95, 1.9), (0.95, 1.85), (-0.45, 2.95), (0.55, 3.0)]          # f1..f4 round the king at (0, 2)

# ---------------------------------------------------------------------------------------------------- shots
SH = []     # (id, at, what, step, cam)


def shot(sid, at, what, cam, step=2):
    SH.append((sid, at, what, step, cam))


# 01 the rule
shot("S01", 0, "bus-stop man, half see-through, brick through his chest", face(SM, 4.0, 42, 8, push=0.5, lens2=46))
shot("S02a", "L02", "wider: the shelter, the lamp post through his shoulder", still(T(0.6, -5.6, 1.5), T(1.9, 1.8, 1.3), 30))
shot("S02b", CH("L02", "right THROUGH"), "low: cobbles and a walker's legs seen through his coat",
     still(T(2.6, -1.6, 0.4), T(1.6, 1.8, 0.7), 28))
shot("S03", "L03", "the mime in the box, nearly glass", still(T(-3.0, -4.6, 1.4), T(-3.0, 0.8, 1.2), 32))
shot("S04", "L04", "the couple at number nine", still(T(7.5, -0.9, 1.7), T(7.5, 3.9, 1.5), 32))
shot("S05", "L05", "closer on the two", still(T(7.5, 0.7, 1.7), T(7.5, 3.9, 1.6), 38))
shot("S06a", "L06", "the busker singing", still(T(-9.5, -1.9, 1.5), T(-9.5, 1.5, 1.3), 38))
shot("S06b", CH("L06", "and he's"), "two walkers pass him, backs to us", still(T(-9.5, -6.8, 1.4), T(-9.5, 2.0, 1.3), 32))
shot("S07", "L07", "me beside the faint man", still(T(1.0, -2.8, 1.5), T(1.0, 1.5, 1.35), 36))
shot("S08", "L08", "my hand against the sun", face(T(-1.6, 0.7), 3.3, 50, 6))
# 02 Grandad
shot("S09", "L09", "stage door at dusk, Grandad mid-story", still(S(0.7, -2.6, 1.45), S(-0.2, 1.6, 1.3), 34))
shot("S10", "L10", "close on Grandad, brick through his cheek", face(SD_W, 2.6, 55, 28))
shot("S11a", "L11", "Grandad leaning toward me", still(S(-1.4, -2.6, 1.6), S(-0.4, 1.4, 1.4), 38))
shot("S11b", CH("L11", "Did I"), "over his shoulder to me, the lit wall behind", still(S(-2.8, -1.2, 1.6), S(0.5, 1.5, 1.45), 44))
shot("S12a", "L12", "me muttering my line, the lit wall behind", still(S(2.0, -1.2, 1.55), S(0.5, 1.5, 1.5), 46))
shot("S12b", CH("L12", "and went"), "Grandad's smile drops", face(SD_W, 2.7, 55, 6))
shot("S13", "L13", "wide from the house: Grandad in robe and crown", still([0.0, -8.0, 1.45], [0.0, 2.5, 1.2], 24))
shot("S14", "L14", "Grandad points me onto the cross", still([0.4, -3.6, 1.5], [1.2, 2.3, 1.3], 30))
shot("S15a", "L15", "me on the cross, mumbling", face(YEL, 3.0, 50, -10))
shot("S15b", CH("L15", "he said"), "Grandad out to the seats, a flat hand beside his mouth", face(KING, 4.2, 40, -8, tz=1.3))
# 03 Monday
shot("S16", "L16", "the king, arms out", face(KING, 3.4, 44, 8, tz=1.36))
shot("S17", "L17", "a track along the five players", TRACK_L)
shot("S18", "L18", "my face, I freeze", face(YEL, 3.0, 50, 6))
shot("S19", "L19", "Grandad waiting on me", face(KING, 3.0, 50, -8, tz=1.36))
shot("S20", "L20", "the ghost light", still([0.4, -3.0, 1.55], [GH[0], GH[1], 1.55], 34))
shot("S21", "L21", "push from my mark toward the wings", c([0, [1.6, 2.4, 1.62], [3.4, 6.5, 1.6], 30], [1, [2.2, 3.5, 1.62], [3.4, 6.5, 1.6], 34]))
shot("S22a", "L22", "three glass people behind the fourth leg", still([1.0, 3.6, 1.55], [3.6, 6.5, 1.5], 34))
shot("S22b", CH("L22", "the WAY"), "close on one face", face((3.15, 6.4), 2.0, 55, -34, h=1.6, tz=1.5))
# 04 Tuesday to Thursday
shot("S24", "L24", "my face, I froze again", face(YEL, 3.0, 50, 4))
shot("S25", "L25", "wide: the brick wall through his robe", still([0.0, -7.5, 1.45], [0.4, 2.6, 1.2], 24))
shot("S26", "L26", "they have come one curtain nearer", still([1.2, 2.9, 1.55], [3.3, 5.4, 1.45], 30))
shot("S27", "L27", "break: everyone on the stage lip", still([1.0, -4.6, 1.15], [-0.2, 0.4, 0.8], 22))
shot("S28a", "L28", "me, the script roll on my lap", face((LIP["me"], 0.45), 2.8, 44, -14, h=1.05, tz=0.7))
shot("S28b", CH("L28", "before"), "Grandad's hand comes down", face((LIP["walt"], 0.45), 2.8, 50, 14, h=1.0, tz=0.82))
shot("S29", "L29", "nobody looks up", still([-0.6, -3.8, 0.95], [-0.2, 0.4, 0.85], 24))
shot("S30", "L30", "the crown floats", still([0.0, -0.9, 1.0], [0.0, 2.0, 1.78], 40))
shot("S31a", "L31", "Grandad alone on the throne", still([0.0, -6.5, 1.5], [0.0, 2.5, 1.3], 26))
shot("S31b", CH("L31", "talking to"), "the empty rows from behind him", still([1.3, 3.5, 1.55], [0.0, -8.0, 1.0], 28))
shot("S32", "L32", "the faded ones at the lip", still([-0.4, -3.6, 1.2], [2.9, 1.0, 1.4], 28))
shot("S33", "L33", "four faces turned to him", still([0.8, 2.1, 0.45], [3.0, 1.0, 1.5], 30))
# 05 Friday
shot("S34", "L34", "dress rehearsal, wide", still([0.0, -8.0, 1.45], [0.3, 2.5, 1.2], 24))
shot("S35", "L35", "me in the cloak, I freeze", face(YEL, 3.0, 50, 6))
shot("S36", "L36", "the lights sink", still([0.0, -8.0, 1.45], [0.3, 2.4, 1.2], 24))
shot("S36b", "P01", "the dim hold", still([-3.2, -5.2, 1.3], [0.5, 2.4, 1.2], 28))
shot("S37", "L37", "the reveal: the ring round Grandad", still([0.0, -1.5, 1.3], [0.0, 2.2, 1.35], 18))
shot("S38", "L38", "heads tilted in", still([0.9, 0.3, 1.5], [-1.0, 1.9, 1.5], 26))
shot("S39", "L39", "Grandad still talking, Marion bowed", still([-0.2, -6.5, 1.5], [0.0, 2.0, 1.0], 60))
shot("S40", "L40", "the ring, everyone else turned away", still([0.0, -3.3, 1.6], [0.0, 2.6, 1.2], 24))
shot("S41", "L41", "my face, the script roll at the frame edge, I get it", face((2.0, 3.45), 2.8, 46, 0, tz=1.24))
shot("S42", "L42", "Grandad's mouth moving", face(KING, 2.6, 52, 4, tz=1.4))
shot("S43", "L43", "from Grandad's eye line: me, the ring out of the way", still([-0.35, 2.3, 1.6], [0.7, 0.0, 1.4], 60))
shot("S44", "L44", "low on the boards: the script roll falls and rolls to the cross", still([1.7, -1.2, 0.4], [1.5, 1.6, 0.25], 24))
shot("S45", "L45", "the one picture: his flat hand beside his mouth", still([-0.55, -0.9, 1.5], [0.05, 2.0, 1.5], 30), step=1)
# 06 Saturday
shot("S46", "L46", "from the back of the full house, the crown over a ghost", still([0.0, -9.2, 2.6], [0.0, 2.1, 1.6], 40))
shot("S47", "L47", "the full house from the stage, one whispering to the next", still([0.9, 0.3, 1.15], [-0.15, -3.55, 0.95], 36))
shot("S48", "L48", "me on the cross, glancing at him", face(YEL, 3.0, 50, 6))
shot("S49a", "L49", "me facing the house, a flat hand beside my mouth", face(YEL, 4.2, 40, -4, tz=1.3))
shot("S49b", CH("L49", "louder"), "over my shoulder to the back rows",
     c([0, [YEL[0] - 0.5, YEL[1] + 1.2, 1.7], [0.0, -8.0, 0.3], 32], [1, [YEL[0] - 0.5, YEL[1] + 1.2, 1.7], [0.0, -8.0, 1.3], 32]))
shot("S50", "L50", "two-shot: Grandad turns to me, the colour coming back", still([0.5, -2.0, 1.45], [0.55, 1.9, 1.4], 34))
shot("S51", "L51", "from behind Grandad out to the full house", still([-0.05, 3.4, 1.75], [0.0, -8.0, 1.1], 30))
# 07 The bow, and the sting
BOW = {"p1": -3.0, "p2": -2.1, "p3": -1.2, "p4": -0.3, "p5": 0.6, "walt": 1.5, "me": 2.4}
shot("S52", "L52", "the curtain call along the stage lip", still([-0.4, -5.6, 1.1], [0.0, 1.0, 1.0], 28))
shot("S54a", "L54", "the first leg, empty, the warm light on it", still([2.2, 1.0, 1.5], [4.2, 3.3, 1.4], 26))
shot("S54b", CH("L54", "GRAN"), "Grandad grinning at me", face([BOW["walt"], 1.0], 2.8, 52, 8, tz=1.38))
shot("S55a", "L55", "the empty stage, the lights sink", still([0.0, -6.5, 1.5], [0.5, 3.0, 1.2], 26))
shot("S55b", CH("L55", "the faded"), "the faded ones in the wings", still([0.6, 1.4, 1.55], [3.1, 5.2, 1.4], 30))
shot("S56", "L56", "a slow push: a new one at the back",
     c([0, [0.4, 1.4, 1.6], [3.4, 6.5, 1.5], 26], [1, [1.4, 2.9, 1.6], [3.7, 6.7, 1.5], 28]))
STOP_END = [3.9, 6.85]
shot("S57", "L57", "close on the bus-stop man", face(STOP_END, 2.3, 55, yaw_to(STOP_END, [0.5, 2.4]), h=1.62, tz=1.5))

shots = []
for sid, at, what, step, cam in SH:
    s = {"id": sid, "cam": cam, "hand": 0.004, "step": step, "what": what}
    if sid != "S01":
        s["at"] = at
    shots.append(s)
AT = {sid: at for sid, at, *_ in SH}

# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "sit": False, "blink": True,
           "look": [0, 0], "expr": "neutral"}
acting = {k: [] for k in cast}
PLAYERS = ["p1", "p2", "p3", "p4", "p5"]
FADED = ["f1", "f2", "f3", "f4"]


def put(who, at, pos, **kw):
    keys = acting[who]
    prev = next((k["pos"] for k in reversed(keys) if "pos" in k), None)
    if prev is not None:
        keys.append({"at": at, "pos": prev})
    keys.append({"at": at, "pos": pos, "blend": 0, "hidden": False, **NEUTRAL, **kw})


def walk(who, at, pos, **kw):
    acting[who].append({"at": at, "pos": pos, **kw})


def key(who, at, **kw):
    acting[who].append({"at": at, **kw})


def hide(who, at):
    acting[who].append({"at": at, "hidden": True, "blend": 0})


def talk(who, a, b):
    acting[who].append({"from": a, "to": b, "mouth": [0.55, 0.55], "flap": True})


def answers(line):
    for i, p in enumerate(PLAYERS):
        a = round(0.2 * i, 2)
        talk(p, f"{line}+{a}", f"{line}+{a + 0.3}")


def players(at, expr="neutral"):
    for i, p in enumerate(PLAYERS):
        put(p, at, MARKS[i], yaw=0, expr=expr)


def lip(who, at, expr="neutral", **kw):
    put(who, at, [LIP[who], 0.45, LIPZ], yaw=0, sit=True, expr=expr, **kw)


for k in cast:
    hide(k, 0)

# --- the town
put("stopman", 0, SM, yaw=0, expr="worried", look=[0, 0])
hide("stopman", "L08")
put("walker1", "L02", T(4.4, 2.5), expr="neutral")
walk("walker1", "L03", T(-1.2, 2.5))
hide("walker1", "L03+0.3")
put("mime", "L03", T(-3.0, 0.8), yaw=0, expr="neutral", arms=[88, 88])
for k in range(6):
    key("mime", f"L03+{0.35 + 0.28 * k:.2f}", arms=[88 + 10 * (k % 2), 88 - 10 * (k % 2)], side=[0, 0], blend=0.2)
hide("mime", "L04")
put("walker2", "L03", T(-6.4, 2.0), expr="neutral")
walk("walker2", "L04", T(0.4, 2.0))
hide("walker2", "L04+0.2")
put("wife9", "L04", T(6.9, 3.9, 0.18), yaw=70, expr="angry", arms=[100, 100])
put("husband9", "L04", T(8.1, 3.9, 0.18), yaw=-70, expr="angry", arms=[100, 100])
for k in range(8):
    for who, sgn in (("wife9", 1), ("husband9", -1)):
        key(who, f"L04+{0.2 + 0.3 * k:.2f}", arms=[100 + sgn * 18 * (-1) ** k, 100 - sgn * 18 * (-1) ** k], blend=0.1)
talk("wife9", "L04", "L06")
talk("husband9", "L04", "L06")
hide("wife9", "L06")
hide("husband9", "L06")
put("busker", "L06", T(-9.5, 1.5), yaw=0, expr="neutral")
acting["busker"].append({"from": "L06", "to": "L07", "mouth": [0.7, 0.7], "flap": True})
hide("busker", "L07")
put("walker1", CH("L06", "and he's"), T(-10.3, -3.2))
walk("walker1", "L07", T(-10.3, 0.4))
hide("walker1", "L07+0.1")
put("walker2", CH("L06", "and he's"), T(-8.7, -3.6))
walk("walker2", "L07", T(-8.7, 0.2))
hide("walker2", "L07+0.1")
# --- me, in town
put("me", "L07", T(0.2, 1.5), yaw=0, expr="neutral")
put("me", "L08", T(-1.6, 0.7), yaw=0, expr="neutral", arms=[0, 105])
hide("me", "L09")

# --- the stage door: Grandad and me side by side, the lit wall behind us both
put("walt", "L09", SD_W, yaw=0, expr="grin", side=[0, 40])
put("me", "L09", SD_ME, yaw=0, expr="neutral")
talk("walt", "L09", "L10>")
put("walt", "L11", SD_W, yaw=-25, expr="grin", lean=12)
put("me", "L11", SD_ME, yaw=0, expr="neutral")
talk("walt", "L11", "L11>")
key("me", CH("L11", "Did I"), yaw=-30, blend=0.3)
key("walt", f"{CH('L12', 'and went')}+0.3", expr="worried", lean=0, blend=0.5)
put("me", "L12", SD_ME, yaw=-40, expr="neutral", head=[0, 24])
acting["me"].append({"from": "L12", "to": "L12>", "mouth": [0.3, 0.3], "flap": True})
hide("me", "L13")
hide("walt", "L12>+0.05")

# --- the play
put("walt", "L13", KING, yaw=0, expr="smile")
for p_i, p in enumerate(PLAYERS):
    put(p, "L13", MARKS[p_i], yaw=0)
put("walt", "L14", KING, yaw=50, expr="grin", arms=[0, 88])
put("me", "L14", [3.9, 1.2], yaw=0, expr="neutral")
walk("me", "L14+1.4", YEL)
put("walt", CH("L15", "he said"), KING, yaw=0, expr="smile", arms=[0, 0], side=[0, 125])
talk("walt", CH("L15", "he said"), "L15>")
put("me", "L15", YEL, yaw=0, expr="worried")
acting["me"].append({"from": "L15", "to": "L15.1", "mouth": [0.2, 0.2]})

# --- Monday
put("walt", "L16", KING, yaw=0, expr="grin", side=[75, 75])
talk("walt", "L16", "L16>")
players("L16")
answers("L17")
put("me", "L16", YEL, yaw=0, expr="neutral")
key("me", "L18", expr="scared")
key("walt", "L19", side=[0, 0], expr="smile", head=[0, -8], blend=0.3)
hide("walt", "L20")
hide("me", "L20")
for p in PLAYERS:
    hide(p, "L20")
RING_W1 = [(3.15, 6.4), (3.65, 6.5), (4.15, 6.45)]
for i, (x, y) in enumerate(RING_W1):
    put(FADED[i], "L21", [x, y], yaw=yaw_to([x, y], [0.5, 2.4]), expr="neutral")
    hide(FADED[i], "L22>+0.1")

# --- Tuesday to Thursday
put("me", "L24", YEL, yaw=0, expr="scared")
put("walt", "L25", KING, yaw=0, expr="neutral")
players("L25")
hide("walt", "L26")
hide("me", "L26")
for p in PLAYERS:
    hide(p, "L26")
FT = [(2.6, 5.45), (3.1, 5.45), (3.55, 5.4), (3.9, 5.35)]
for i, (x, y) in enumerate(FT):
    put(FADED[i], "L26", [x, y], yaw=yaw_to([x, y], [0.5, 2.4]), expr="neutral")
    hide(FADED[i], "L26>+0.1")
for who in PLAYERS:
    lip(who, "L27")
lip("walt", "L27", expr="grin")
lip("me", "L27")
talk("walt", "L27", "L27>")
key("me", "L28", head=[-40, 0], blend=0.3)
key("walt", CH("L28", "You TOLD"), arms=[0, 70], blend=0.2)
key("walt", f"{CH('L28', 'You TOLD')}+0.6", arms=[0, 0], expr="worried", blend=0.5)
hide("walt", "L30")
hide("me", "L30")
for p in PLAYERS:
    hide(p, "L30")
put("walt", "L30", KING, yaw=0, expr="neutral")
hide("walt", "L31")
put("walt", "L31", THRONE, yaw=0, expr="grin", sit=True, arms=[40, 40], side=[20, 20])
talk("walt", "L31", "L32")
FTH = [(3.5, 0.7), (3.0, 1.1), (3.55, 1.5), (2.5, 0.75)]
for i, (x, y) in enumerate(FTH):
    put(FADED[i], "L32", [x, y], yaw=yaw_to([x, y], [0.0, 2.5]), expr="neutral")
    hide(FADED[i], "L33>+0.1")
hide("walt", "L33>+0.1")

# --- Friday
put("walt", "L34", KING, yaw=0, expr="smile")
players("L34")
put("me", "L34", YEL, yaw=0, expr="neutral")
key("me", "L35", expr="scared")
key("walt", "L35", expr="smile", side=[75, 75], blend=0.3)
put("walt", "L37", KING, yaw=0, expr="grin")
talk("walt", "L37", "L44>")
for i, p in enumerate(PLAYERS):
    put(p, "L37", [MX[i], 4.7], yaw=0)
ME_F = [2.0, 3.45]
put("me", "L37", ME_F, yaw=0, expr="worried")
for i, (x, y) in enumerate(RING):
    _y = yaw_to([x, y], KING)
    put(FADED[i], "L37", [x, y], yaw=(_y * 0.62 if abs(_y) < 110 else _y), expr="neutral", head=[0, 4])
put("marion", "L39", ROW3_POS, yaw=180, expr="neutral", sit=True, head=[0, 24])
hide("marion", "L40")
key("me", "L41", expr="wide")
put("me", "L43", [0.7, 0.0], yaw=yaw_to([0.7, 0.0], KING), expr="worried", head=[0, 22])
put("me", "L44", [0.7, 0.0], yaw=0, expr="soft", head=[0, 22])
hide("me", "L45")
put("walt", "L45", KING, yaw=0, expr="smile", side=[0, 125], arms=[0, 0])
for i in range(4):
    key(FADED[i], "L45", yaw=0, head=[0, 0])
hide("marion", "L40")

# --- Saturday: the wash comes up under L46 and the company is back; the faded ones are not visible in the full light
for i in range(4):
    hide(FADED[i], "L46")
for p in PLAYERS:
    hide(p, "L46")
for i, p in enumerate(PLAYERS[:4]):
    put(p, "L46", MARKS[i], yaw=0)
put("walt", "L46", KING, yaw=0, expr="smile", side=[0, 125], arms=[0, 0])
put("me", "L46", YEL, yaw=0, expr="neutral")
put("marion", "L46", [-0.58, -3.55, -0.57], yaw=180, expr="neutral", sit=True, head=[-35, 6], lean=14)
put("p5", "L46", [0.0, -3.55, -0.57], yaw=180, expr="worried", sit=True, head=[10, 4])
key("walt", "L47", side=[0, 0], arms=[0, 0], expr="smile", blend=0.4)
key("me", "L48", expr="neutral", head=[-30, 0], blend=0.4)
key("me", "L49", head=[0, -8], side=[0, 125], arms=[0, 0], expr="neutral", blend=0.3)
key("me", "L50", side=[0, 0], arms=[0, 0], head=[0, 0], blend=0.4)
talk("me", "L49", "L49>")
put("me", "L50", [1.15, 1.75], yaw=yaw_to([1.15, 1.75], KING), expr="smile")
put("walt", "L50", KING, yaw=yaw_to(KING, [1.15, 1.75]), expr="smile")
put("me", "L51", [1.15, 1.75], yaw=yaw_to([1.15, 1.75], KING), expr="smile")
hide("marion", "L52")
hide("p5", "L52")

# --- the bow, and the sting
for who, x in BOW.items():
    if who in ("walt", "me"):
        continue
    put(who, "L52", [x, 1.0], yaw=0, expr="smile")
put("walt", "L52", [BOW["walt"], 1.0], yaw=0, expr="grin", head=[-45, 0])
put("me", "L52", [BOW["me"], 1.0], yaw=0, expr="smile")
for who in BOW:
    key(who, "L52+0.8", lean=26, blend=0.7)
    key(who, "L52+2.2", lean=0, blend=0.7)
talk("walt", "L52", "L52>")
key("walt", "L54", expr="grin", head=[0, 0], blend=0.4)
hide("walt", "L55")
hide("me", "L55")
for p in PLAYERS:
    hide(p, "L55")
FEND = [(3.1, 4.55), (3.3, 5.3), (3.0, 6.1), (2.5, 3.9)]
for i, (x, y) in enumerate(FEND):
    put(FADED[i], CH("L55", "the faded"), [x, y], yaw=yaw_to([x, y], [0.0, 2.4]), expr="neutral")
for i in range(4):
    hide(FADED[i], "L57")
put("stopman", "L56", STOP_END, yaw=yaw_to(STOP_END, [0.5, 2.4]), expr="worried")

# ---------------------------------------------------------------------------------------------------- cues
cues = []


def cue(at, name, **kw):
    cues.append({"at": at, "name": name, **kw})


cue(0, "mood", set="ghost")
cue(0, "mood", set="sun", dur=0.4)
cue("L09-0.5", "mood", set="dusk", dur=0.5)
cue("L13-0.4", "mood", set="work", dur=0.4)
cue("L16-0.3", "mood", set="warm", dur=0.3)
cue("L20+0.2", "mood", set="ghost", dur=1.6)
cue("L22>-1.2", "mood", set="warm", dur=1.8)
cue("L26>-1.2", "mood", set="work", dur=1.8)
cue("L30-0.3", "mood", set="warm", dur=0.3)
cue("L30>-1.0", "mood", set="ghost", dur=1.6)
cue("L33>-1.0", "mood", set="warm", dur=1.8)
cue("L36+0.2", "mood", set="ghost", dur=1.6)
cue("L46", "mood", set="open", dur=2.0)
cue("L55+0.2", "mood", set="ghost", dur=1.6)
# the faded ones' lights follow the wings
cue(0, "flight", key=[1.6, -0.9, 1.5], rim=[4.0, 4.2, 2.6], aim=[0.0, 2.2, 1.3])
cue("L21", "flight", key=[1.0, 4.4, 1.9], rim=[4.8, 7.0, 2.4], aim=[3.5, 6.5, 1.4])
cue("L26", "flight", key=[1.2, 3.2, 1.9], rim=[4.8, 6.2, 2.4], aim=[3.2, 5.4, 1.4])
cue("L31", "flight", key=[1.6, -0.9, 1.5], rim=[4.0, 4.2, 2.6], aim=[0.0, 2.4, 1.3])
cue("L32", "flight", key=[1.6, -1.0, 1.6], rim=[4.6, 2.4, 2.4], aim=[3.0, 1.0, 1.4])
cue("L34", "flight", key=[1.6, -0.9, 1.5], rim=[4.0, 4.2, 2.6], aim=[0.0, 2.2, 1.3])
cue(CH("L55", "the faded"), "flight", key=[1.2, 3.0, 1.9], rim=[4.8, 6.6, 2.4], aim=[3.3, 5.2, 1.4])
cue("L57", "flight", key=[1.6, 4.6, 1.9], rim=[4.8, 7.4, 2.4], aim=[3.9, 6.85, 1.5])
# transparency: Grandad, the bus-stop man, the mime, the busker, the faded ones
for who, a in (("walt", WALT_FADE0), ("stopman", 0.3), ("mime", 0.12), ("busker", 0.4), ("f1", 0.15), ("f2", 0.15),
               ("f3", 0.15), ("f4", 0.15)):
    cue(0, "fade", who=who, a=a, dur=0)
# faces keep their strokes: the faded ones' heads stay at about 0.6, the bus-stop man's face is clear, Grandad's head
# follows his body at the stage door (the brick shows through his cheek), then 1.3 x his body from the play on
for who in FADED:
    cue(0, "headfade", who=who, a=0.6, dur=0)
cue(0, "headfade", who="stopman", a=0.55, dur=0)
cue(0, "headfade", who="walt", a=0.5, dur=0)
cue(f"{CH('L12', 'and went')}+0.35", "headfade", who="walt", a=0.52, dur=1.2)
cue("L13", "headfade", who="walt", a=-1, dur=0)
cue(f"{CH('L12', 'and went')}+0.35", "fade", who="walt", a=0.52, dur=1.2)
cue("L19+0.3", "fade", who="walt", a=0.45, dur=1.2)
cue("L21+0.3", "fade", who="walt", a=0.40, dur=1.5)
cue("L26+0.2", "fade", who="walt", a=0.36, dur=1.0)
cue(f"{CH('L28', 'You TOLD')}+0.3", "fade", who="walt", a=0.30, dur=1.2)
cue("L29+0.1", "headfade", who="walt", a=0.2, dur=1.4)
cue("L31", "headfade", who="walt", a=-1, dur=0)
cue("L31+0.4", "fade", who="walt", a=0.25, dur=1.2)
cue("L33+0.3", "fade", who="walt", a=0.20, dur=1.0)
cue("L36+0.5", "fade", who="walt", a=0.15, dur=1.4)
cue("L50+0.3", "fade", who="walt", a=0.50, dur=1.5)
cue("L51+0.35", "fade", who="walt", a=0.95, dur=1.8)
cue("L52+0.5", "fade", who="walt", a=1.0, dur=1.0)
cue("L54", "fade", who="stopman", a=0.15, dur=0.5)
cue("L54", "headfade", who="stopman", a=0.3, dur=0.5)
# costumes: Grandad's beard always, robe and crown from the play on; my cloak Friday and Saturday
cue(0, "costume", who="walt", beard=True, crown=False, robe=False)
cue("L13", "costume", who="walt", beard=True, crown=True, robe=True)
cue("L55", "costume", who="walt", beard=True, crown=True, robe=True)
# my script roll: under my arm in S12, S15 and S37 to S43, on my lap on the break, dropped in S44, gone before Saturday
cue(0, "costume", who="me", cloak=False, roll_arm=False, roll_lap=False)
cue("L12", "costume", who="me", cloak=False, roll_arm=True, roll_lap=False)
cue("L13", "costume", who="me", cloak=False, roll_arm=False, roll_lap=False)
cue("L14", "costume", who="me", cloak=False, roll_arm=True, roll_lap=False)
cue("L16", "costume", who="me", cloak=False, roll_arm=False, roll_lap=False)
cue("L27", "costume", who="me", cloak=False, roll_arm=False, roll_lap=True)
cue("L30", "costume", who="me", cloak=False, roll_arm=False, roll_lap=False)
cue("L34", "costume", who="me", cloak=True, roll_arm=False, roll_lap=False)
cue("L37", "costume", who="me", cloak=True, roll_arm=True, roll_lap=False)
cue("L44", "costume", who="me", cloak=True, roll_arm=False, roll_lap=False)
cue("L44", "roll", mode="drop", start=[0.8, -0.05, 0.85], land=[0.95, 0.35], to=YEL, t0=0.25, fall=0.5, dur=2.4)
cue("L46", "roll", mode="none")
cue(0, "throne", on=False)
cue("L31", "throne", on=True)
cue("L34", "throne", on=False)
cue(0, "audience", on=False)
cue("L46", "audience", on=True)
cue("L55", "audience", on=False)

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L21", "kind": "creak", "db": -26, "dur": 0.9},
    {"at": "L21+0.7", "kind": "whoosh", "db": -34},
    {"at": "L32", "kind": "creak", "db": -24, "dur": 0.9},
    {"at": "L33", "kind": "hit", "db": -10, "dur": 1.4},
    {"at": "L37", "kind": "hit", "db": -9, "dur": 1.6},
    {"at": "L50", "kind": "chime", "db": -24},
    {"at": "L52", "kind": "bubbles", "db": -20, "dur": 5.5},
    {"at": "L55+0.6", "kind": "creak", "db": -26, "dur": 0.9},
]

story = {
    "slug": "ep23-only-line",
    "title": "In This Town The Quiet Ones FADE",
    "made_for_kids": False,
    "premise": "In a small town the quiet ones fade until you can see the street through them. I'm the quietest person in town and perfectly solid, but my talkative grandad, the king in the playhouse play, is fading a shade each rehearsal, and under the ghost light the people who faded all the way stand in the wings, nearer every night.",
    "twist": "In this town quiet means unheard. Grandad is fading because I stopped listening to him years ago, and I never faded because every word I ever mumbled, he said again, louder, so everyone heard it. On Saturday the house can't hear the faded king, so I say his line again, louder, for the back row, and every word they hear brings him back a shade.",
    "world": "a sunny brick terrace street, a playhouse stage door at dusk, and a raked stage with green velvet legs and a ghost light, where the faded stand in the wings",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff8fb1",
    "caption": {"ink": "#08090d", "stroke_add": 1, "shadow": 0.7},
    "gap": 0.12,
    "tail": 0.25,
    "fade_out": False,
    "look": {"fog": "#080a12", "fog_density": 0.02, "fog_start": 5.0, "sky": "#05060a", "sky_strength": 1.0,
             "exposure": 0.0, "flash_safe": True},
    "grade": {"shadows": [-0.01, 0.0, 0.04], "highlights": [0.03, 0.01, -0.03], "saturation": 0.95, "contrast": 1.06,
              "vignette": 0.34, "bloom": 0.22, "grain": 0.012, "red_line": 0.79},
    "phonemes": {"gran": "ɡɹˈæn"},
    "places": {"marks": MARKS, "legy": LEGY, "king": KING, "ghost": GH},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    # A Dorian at 66 bpm: a soft wooden tick and a bright plucked pad for the montage. Phrygian with a thin drone from
    # L16; the tick stops under each freeze (L18, L24, L35). The heavy low drone comes in at L22 (an ambience layer) and
    # holds to L45, thins at L46 and drops out at L48. The pad warms to A major at L50. Saturday is A major, quiet. L55 on the drone returns, cold, and
    # stops dead on the loop cut.
    "music": {"root": 45, "mode": "dorian", "bpm": 66, "seed": 23,
              "sections": [
                  {"at": 0, "voices": ["pad", "tick"], "energy": 0.35},
                  {"at": "L16", "voices": ["drone", "pad", "tick"], "energy": 0.3, "mode": "phrygian"},
                  {"at": "L18", "voices": ["drone", "pad"], "energy": 0.3, "mode": "phrygian"},
                  {"at": "L19", "voices": ["drone", "pad", "tick"], "energy": 0.3, "mode": "phrygian"},
                  {"at": "L24", "voices": ["drone", "pad"], "energy": 0.35, "mode": "phrygian"},
                  {"at": "L25", "voices": ["drone", "pad", "tick"], "energy": 0.4, "mode": "phrygian"},
                  {"at": "L35", "voices": ["drone", "pad"], "energy": 0.4, "mode": "phrygian"},
                  {"at": "L36", "voices": ["drone", "pad", "tick"], "energy": 0.45, "mode": "phrygian"},
                  {"at": "L42", "voices": ["drone"], "energy": 0.3, "mode": "phrygian"},
                  {"at": "L46", "voices": ["drone", "pad"], "energy": 0.3, "mode": "phrygian"},
                  {"at": "L48", "voices": ["pad"], "energy": 0.35, "mode": "dorian"},
                  {"at": "L50", "voices": ["pad", "choir"], "energy": 0.5, "mode": "major"},
                  {"at": "L52", "voices": ["pad"], "energy": 0.25, "mode": "major"},
                  {"at": "L55", "voices": ["drone"], "energy": 0.3, "mode": "phrygian"},
                  {"at": "end-0.25", "voices": [], "energy": 0.0},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "L09", "lufs": -40},
                  {"kind": "room", "from": 0, "to": "L09", "lufs": -38},
                  {"kind": "room", "from": "L09", "to": "end", "lufs": -35},
                  {"kind": "hum", "from": "L20", "to": "L24", "lufs": -42},
                  {"kind": "hum", "from": "L26", "to": "L27", "lufs": -42},
                  {"kind": "hum", "from": "L31", "to": "L34", "lufs": -42},
                  {"kind": "hum", "from": "L36", "to": "L46", "lufs": -42},
                  {"kind": "room", "from": "L46", "to": "L48", "lufs": -29},
                  {"kind": "hum", "from": "L55", "to": "end", "lufs": -42},
                  {"kind": "drone", "from": "L22", "to": "L46", "lufs": -31},
                  {"kind": "drone", "from": "L46", "to": "L48", "lufs": -38},
                  {"kind": "drone", "from": "L55", "to": "end", "lufs": -31},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "L33-0.6", "to": "L33"},
                              {"from": "P01", "to": "L37", "keep": ["hit"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
