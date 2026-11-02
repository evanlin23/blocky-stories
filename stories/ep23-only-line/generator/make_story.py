"""Writes ../story.json for ep23 "only-line" (script.md, writer 2026-11-02).

Run from anywhere: python stories/ep23-only-line/generator/make_story.py
The words are in lines.json next to this file (the script's lines, chunk for chunk). Everything else is here: the
cast, the shots and cameras, the acting, the cues set.py reads (the mood of the light, the Prompter's pose,
costumes, chairs, the audience), the effects, the score and the sound.

Places (set.py's metres, z up, the stage floor is z = 0). The stage runs x -9 .. 9, y 0 (the lip) .. 7.2 (the
brick back wall). The proscenium is at y = -0.2, opening x -4.2 .. 4.2. A character with yaw 0 faces -y, which is
the house (the seats, y -2.6 and down). Stage left is +x: four curtain legs hang there at y 3.3, 4.2, 5.1, 6.0,
inner edge x = 3.7. Six tape marks make a curve behind the king: five white, the yellow one last, at x 2.3.
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


# ---------------------------------------------------------------------------------------------------- holds
# The held silence at the end is P04. The loop pause after it carries the clap's fade to black.
# The tally shot (L16) is held 1.5 s or longer: its gap makes sure of it.
GAPS = {"L16": 0.55}
for ln in lines:
    if ln["id"] in GAPS:
        ln["gap"] = GAPS[ln["id"]]
for ln in lines:
    if ln["id"] == "P04":
        ln["pause"] = 1.0
lines = lines + [{"id": "P05", "pause": 0.36, "chunks": []}]

for ln in lines:      # "around", not "round": Whisper writes the American spelling and so does the narrator
    for ch in ln.get("chunks", []):
        for k in (0, 1):
            ch[k] = ch[k].replace("ROUND", "AROUND").replace("round", "around")

# lines a touch slower so the word check hears every word (filled in by a fix round, if it needs any)
TEMPO = {"L96": 0.9}
SPOKEN = {}
for ln in lines:
    if ln["id"] in TEMPO:
        ln["tempo"] = TEMPO[ln["id"]]
    for k, ch in enumerate(ln.get("chunks", [])):
        if (ln["id"], k) in SPOKEN:
            ch[1] = SPOKEN[(ln["id"], k)]

# ---------------------------------------------------------------------------------------------------- places
LEGY = [3.3, 4.2, 5.1, 6.0]
LEG_EDGE = 3.7
MX = [-3.2, -2.05, -0.9, 0.25, 1.2, 2.3]
MARKS = [[x, round(3.2 - 0.07 * x * x, 2)] for x in MX]     # p1..p5, then the yellow cross
YEL = MARKS[5]
KING = [0.0, 1.4]
CHAIRS = [[-1.8, 3.2], [-1.0, 4.1], [0.2, 4.4], [1.3, 3.9], [1.8, 3.0], [-1.5, 2.3]]
ROW3 = (-0.58, -4.5)           # Marion's seat (the third row)
ME_EDGE = [2.9, 1.9]
EDGE_ME, EDGE_WALT = [0.6, 0.45, -0.51], [-0.3, 0.45, -0.51]       # sitting on the stage edge
FLAT = (-40.0, 0.0)
CAR = (40.0, 0.0)
# the Prompter: where it stands each day, and how it faces
PP = {"mon": [3.78, 6.35], "tue": [3.77, 5.45], "wed": [3.45, 4.55], "thu": [3.4, 3.65], "fri": YEL}

cast = {
    "me": {"age": "adult", "skin": "#d9a47a", "shirt": "#c9a227", "pattern": "knit", "pattern_c": "#a8841a",
           "collar": "#8a6f16", "pants": "#2a2d3a", "shoes": "#35302c", "sleeves": "long", "hair": "cap",
           "hair_c": "#3a2616", "hat": "none", "face": {"eyes": "round", "brows": True, "ink": "#161012"}},
    "marion": {"age": "adult", "skin": "#e0b08a", "shirt": "#2f7f86", "pattern": "knit", "pattern_c": "#256a70",
               "pants": "#3a3a44", "shoes": "#2a2424", "sleeves": "long", "hair": "cap", "hair_c": "#a9a9ae",
               "extras": ["glasses"], "extra_c": "#2a2a30", "hat": "none",
               "face": {"eyes": "round", "brows": True, "ink": "#1a1214"}},
    "walt": {"age": "adult", "skin": "#c28a64", "shirt": "#6b4a2e", "pattern": "stripes", "pattern_c": "#58391f",
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
}


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
    a = math.radians(ang)

    def at(dd):
        return [round(pos[0] + dd * math.sin(a), 3), round(pos[1] - dd * math.cos(a), 3), h + z0]

    tgt = [pos[0], pos[1], tz + z0]
    if push:
        return c([0, at(d), tgt, lens], [1, at(d - push), tgt, lens2 or lens])
    return c([0, at(d), tgt, lens])


# ---------------------------------------------------------------------------------------------------- shots
HOUSE_WIDE = still([0.0, -8.0, 1.45], [0.8, 3.0, 1.2], 24)
LOW_CROSS = still([1.3, 1.5, 0.3], [YEL[0], YEL[1], 0.05], 28)
WINGS_FROM_MARK = still([1.4, 2.0, 1.7], [4.5, 4.5, 1.4], 28)
TRACK_L = c([0, [-3.6, 0.6, 1.5], [-3.4, 3.0, 1.4], 32], [1, [1.6, 0.6, 1.5], [1.8, 3.0, 1.4], 32])
TRACK_R = c([0, [1.6, 0.6, 1.5], [1.8, 3.0, 1.4], 32], [1, [-3.6, 0.6, 1.5], [-3.4, 3.0, 1.4], 32])
MARION_CAM = [-0.8 + 0.5, -1.5, 1.25]
SEATED_MARION = [ROW3[0], ROW3[1], 1.1]
FLAT_FACE = still([FLAT[0] - 0.15, FLAT[1] + 2.2, 1.28], [FLAT[0], FLAT[1] - 0.75, 1.0], 38)

SHOTS = [
    # 01 the line
    (0, "me, dim ghost light, push in", 2, face(YEL, 3.2, 50, 12, push=0.5, lens2=56)),
    ("L02", "wide from the house, the ghost light and me small", 2, still([0.0, -9.0, 1.4], [1.2, 3.4, 1.1], 24)),
    ("L03", "low on my feet on the yellow cross", 2, still([YEL[0] + 0.35, YEL[1] - 1.5, 0.3], [YEL[0], YEL[1], 0.1], 38)),
    ("L04", "day, work lights: the circle of chairs", 2, still([0.0, -4.5, 1.7], [0.3, 3.2, 0.9], 25)),
    ("L05", "my face, embarrassed", 2, face(ME_EDGE, 3.0, 50, -10)),
    ("L06", "Marion in the third row with her flask", 2,
     still([0.6, 1.4, 1.25], [ROW3[0], ROW3[1] + 0.2, 1.0], 36)),
    ("L07", "wide on the stage in warm wash: Walt and the marks", 2, still([0.0, -8.0, 1.5], [0.0, 3.0, 1.0], 26)),
    ("L08", "Walt, chin up", 2, face(KING, 3.0, 50, 8, tz=1.36)),
    ("L09", "overhead on the six crosses", 2, still([0.0, 1.2, 8.8], [0.0, 3.0, 0.0], 19)),
    ("L10", "low on the yellow cross, nearest the wings", 2, still([0.4, 1.6, 0.28], [YEL[0] + 0.1, YEL[1] + 0.1, 0.18], 26)),
    ("L11", "me by Marion's row, worried", 2, still([-2.05, -2.2, 1.25], [-2.3, -4.5, 1.25], 42)),
    ("L12", "Marion laughing", 2, still([ROW3[0] + 0.1, ROW3[1] + 2.9, 1.2], [ROW3[0], ROW3[1], 1.0], 48)),
    ("L13", "Marion pointing her flask at the wings", 2, still([0.7, 0.2, 1.3], [ROW3[0], ROW3[1], 0.95], 34)),
    ("L14", "slow pan across the proscenium", 2,
     c([0, [-3.5, -6.0, 2.4], [-3.2, -0.2, 3.9], 24], [1, [-3.5, -6.0, 2.4], [3.2, -0.2, 3.9], 24])),
    ("L15", "four green legs from centre stage", 2, still([0.2, 1.0, 1.5], [4.3, 4.7, 1.2], 22)),
    ("L16", "the chalk tally on the brick", 2, still([5.3, 5.7, 1.0], [5.3, 7.2, 0.78], 28)),
    # 02 Monday
    ("L17", "the company on their marks", 2, still([0.0, -7.0, 1.4], [0.5, 3.0, 1.1], 24)),
    ("L18", "Walt, arms out", 2, face(KING, 3.4, 44, 8, tz=1.36)),
    ("L19", "slow track along the curve", 2, TRACK_L),
    ("L20", "me on the yellow cross", 2, face(YEL, 3.6, 40, -22)),
    ("L21", "my face, the tick stops", 2, face(YEL, 3.0, 50, 6)),
    ("L22", "mouth open, nothing comes out", 2, face(YEL, 2.8, 55, -4)),
    ("L23", "past my shoulder to the dark wings", 1, still([1.35, 2.0, 1.7], [4.5, 4.5, 1.4], 28)),
    ("L24", "nobody turned round", 2, still([0.0, -6.0, 1.5], [0.4, 2.9, 1.2], 22)),
    ("L25", "Marion clapping in the dark house", 2, still([0.7, 1.4, 1.2], [ROW3[0], ROW3[1] + 0.2, 1.0], 36)),
    ("L26", "half turned to the wings", 2, face(YEL, 3.0, 50, -12)),
    ("L27", "push into the wings: a gold glint", 2,
     c([0, [1.8, 2.0, 1.65], [4.0, 6.3, 1.7], 30], [1, [2.9, 3.2, 1.65], [3.9, 6.3, 1.7], 34])),
    # 03 Tuesday
    ("L28", "Walt again", 2, face(KING, 3.0, 50, -8, tz=1.38)),
    ("L29", "quick track", 2, TRACK_R),
    ("L30", "my eyes slide to stage left", 2, face(YEL, 3.0, 50, -6)),
    ("L31", "I turn my head to the wings", 2, face(YEL, 3.0, 50, -26)),
    ("L32", "behind the 3rd leg: the edge of the mask", 2, still([YEL[0], YEL[1], 1.58], [PP["tue"][0] - 0.2, PP["tue"][1], 1.72], 34)),
    ("L33", "closer on the edge: brow and crack", 2, still([3.1, 4.5, 1.66], [3.62, PP["tue"][1], 1.74], 42)),
    # 04 Wednesday
    ("L34", "work lights: Walt and me on the stage edge", 2, still([0.9, -3.4, 0.85], [0.1, 0.4, 0.7], 32)),
    (CH("L34", "who STANDS"), "Walt, a tin crown pushed up", 2, face(EDGE_WALT, 2.8, 50, 14, h=1.0, tz=0.82, z0=0.0)),
    ("L37", "Walt looks at me funny", 2, face(EDGE_WALT, 2.7, 52, 8, h=1.0, tz=0.82)),
    ("L38", "over Walt's shoulder: the wings in work light", 2, still([-0.9, 0.1, 1.3], [4.3, 4.2, 1.2], 26)),
    ("L39", "Walt points at the yellow cross", 2, still([0.3, -2.4, 1.05], [-0.1, 0.4, 0.95], 32)),
    ("L40", "me on the cross, eyes to stage left", 2, face(YEL, 3.0, 50, -6)),
    ("L41", "from my mark: the Prompter half out of the velvet", 2,
     still([YEL[0] + 0.1, YEL[1] + 0.07, 1.55], [PP["wed"][0], PP["wed"][1], 1.2], 17)),
    ("L43", "tilt up the coat to the tiny shoulders", 2,
     c([0, [2.85, 3.2, 0.4], [PP["wed"][0], PP["wed"][1], 0.35], 34], [1, [2.85, 3.2, 0.4], [PP["wed"][0], PP["wed"][1], 1.3], 34])),
    ("L44", "the reveal: the huge cracked gilt mask", 2, still([2.4, 2.9, 1.55], [PP["wed"][0] + 0.02, PP["wed"][1], 1.38], 24)),
    # 05 Thursday
    ("L45", "wide from the house: the Prompter at the 1st leg", 2, still([-0.2, -6.0, 1.35], [2.4, 3.4, 1.35], 28)),
    ("L47", "Walt asks, arms out", 2, face(KING, 3.4, 44, 6, tz=1.36)),
    ("L48", "I freeze, the tick stops", 2, face(YEL, 3.0, 50, 4)),
    ("L49", "the mask, eye sparks, two metres from me", 1, still([YEL[0], YEL[1] + 0.05, 1.62], [PP["thu"][0], PP["thu"][1], 1.6], 19)),
    ("L50", "its mouth opened", 1, still([YEL[0], YEL[1] + 0.05, 1.62], [PP["thu"][0], PP["thu"][1], 1.62], 24)),
    ("L51", "the black inside the mouth", 1, still([2.78, 3.2, 1.5], [PP["thu"][0], PP["thu"][1], 1.5], 30)),
    ("L52", "my face, terrified", 2, face(YEL, 2.9, 52, -10)),
    ("L53", "night: me in my car under one streetlamp", 2, still([CAR[0] - 3.2, CAR[1] - 3.4, 1.15], [CAR[0], CAR[1] + 0.2, 0.85], 32)),
    # 06 dress rehearsal
    ("L54", "everyone in costume", 2, still([0.0, -7.0, 1.4], [0.5, 3.0, 1.1], 24)),
    ("L55", "me in the borrowed cloak", 2, face(YEL, 3.0, 50, 6)),
    ("L56", "Walt in his robe asks", 2, face(KING, 3.4, 44, -6, tz=1.36)),
    ("L57", "low on the boards: my feet on the cross", 1, still([YEL[0] + 0.3, YEL[1] - 1.5, 0.3], [YEL[0], YEL[1], 0.1], 38)),
    (CH("L57", "and stepped"), "my feet are off the cross", 1, still([YEL[0] + 0.3, YEL[1] - 1.5, 0.3], [YEL[0], YEL[1] + 0.2, 0.1], 38)),
    ("L58", "the lights sink (wide from the house)", 1, still([0.0, -8.0, 1.45], [1.2, 3.0, 1.2], 24)),
    ("L59", "my face, nearly dark", 1, face([YEL[0], YEL[1] + 0.65], 2.6, 52, 6)),
    (CH("L59", "right BESIDE"), "the dim boards at my feet", 1, still([YEL[0] + 0.2, YEL[1] - 1.1, 0.35], [YEL[0], YEL[1] + 0.4, 0.05], 36)),
    ("L61", "the lights creep back up (wide)", 1, still([0.0, -8.0, 1.45], [1.2, 3.0, 1.2], 24)),
    ("L62", "it stands on my mark, facing the seats", 1, still([0.2, -6.5, 1.45], [1.9, 3.0, 1.45], 26)),
    ("L64", "the mask turned all the way round to me", 1, still([-1.3, 3.3, 1.7], [YEL[0] + 0.2, 3.3, 1.6], 24)),
    ("L65", "an arm's length from my nose", 1, still([YEL[0] + 0.1, 4.55, 1.7], [YEL[0], YEL[1], 1.82], 30)),
    ("L66", "the open mouth", 1, still([YEL[0] + 0.14, 3.4, 1.55], [YEL[0], YEL[1], 1.5], 44)),
    ("L67", "Marion writing, not looking up", 2, still([0.7, 1.4, 1.2], [ROW3[0], ROW3[1] + 0.2, 1.0], 36)),
    ("L68", "the yellow cross alone", 2, still([3.0, 1.0, 0.5], [YEL[0], YEL[1], 0.05], 30)),
    # 07 what it was doing
    ("L69", "my flat at night, the lamp", 2, FLAT_FACE),
    ("L70", "the script on the table", 2, still([FLAT[0] - 0.25, FLAT[1] - 1.4, 1.65], [FLAT[0], FLAT[1] + 0.05, 0.74], 38)),
    ("L71", "memory: Walt from behind, along the curve", 2, still([0.15, 0.35, 1.7], [1.0, 3.0, 1.35], 30)),
    ("L72", "overhead on the six crosses again", 2, still([0.0, 1.2, 8.8], [0.0, 3.0, 0.0], 19)),
    ("L73", "the yellow cross with nobody on it", 2, still([3.0, 1.0, 0.5], [YEL[0] - 0.1, YEL[1], 0.05], 30)),
    ("L74", "the four green legs in the dark", 2, still([0.5, 0.8, 1.5], [4.5, 4.5, 1.2], 24)),
    ("L75", "memory: the Prompter on my cross, small and still", 2, still([0.0, -7.0, 1.3], [2.3, 2.9, 1.25], 26)),
    ("L76", "my face at the table", 2, FLAT_FACE),
    ("L77", "the lamp, my hand flat on the script", 2, still([FLAT[0] - 0.15, FLAT[1] - 1.1, 1.45], [FLAT[0], FLAT[1] - 0.05, 0.9], 34)),
    # 08 opening night
    ("L78", "from the back of the house over the heads", 2, still([0.0, -12.8, 2.6], [0.0, 3.0, 1.1], 27)),
    ("L79", "my knees shaking under the cloak", 2, still([YEL[0] + 0.2, YEL[1] - 2.0, 0.6], [YEL[0], YEL[1], 0.6], 36)),
    ("L80", "me in the wings, looking up the row of legs", 2, still([4.35, 1.3, 1.95], [4.6, 5.0, 1.5], 28)),
    ("L82", "a slow track past the legs to the brick", 2,
     c([0, [4.45, 2.8, 1.5], [4.45, 6.6, 1.4], 28], [1, [4.45, 5.2, 1.5], [4.45, 7.2, 1.3], 28])),
    ("L83", "my face, a small breath", 2, face([3.2, 2.0], 3.0, 50, 6)),
    ("L84", "my feet land on the cross", 2, still([YEL[0] + 0.3, YEL[1] - 1.5, 0.3], [YEL[0], YEL[1], 0.1], 38)),
    ("L85", "Walt asks, robe and crown", 2, face(KING, 3.4, 44, 6, tz=1.36)),
    ("L86", "five voices (track)", 2, TRACK_L),
    ("L87", "my throat shut", 2, face(YEL, 3.0, 50, 4)),
    ("L88", "past my shoulder: the empty wings", 2, still([1.35, 2.0, 1.7], [4.5, 4.5, 1.4], 28)),
    ("L89", "from the stage over the footlights: the house waiting", 2, still([0.4, 1.0, 1.55], [0.0, -8.0, 0.95], 28)),
    (CH("L89", "was WAITING"), "Walt, the smallest nod", 2, face(KING, 3.0, 50, 4, tz=1.4)),
    ("L91", "my face, breath held", 2, face(YEL, 2.7, 55, 0)),
    ("L92", "my shoulders rise under the cloak", 2, still([YEL[0] + 0.1, YEL[1] - 1.5, 1.35], [YEL[0], YEL[1], 1.25], 40)),
    ("L93", "my voice shook", 2, face(YEL, 2.7, 55, -4)),
    ("L94", "Walt starts to smile", 2, face(KING, 3.0, 50, -4, tz=1.4)),
    ("L95", "wide: the curve complete, the wings empty", 2, still([0.0, -7.5, 1.4], [1.0, 3.0, 1.2], 22)),
    ("L96", "close on my face, mouth closing, eyes wet but steady", 2, face(YEL, 2.9, 52, 2, push=0.25, lens2=54)),
]

shots = []
for i, (at, what, step, cam) in enumerate(SHOTS):
    s = {"id": f"S{i + 1:02d}", "cam": cam, "hand": 0.004, "step": step, "what": what}
    if i:
        s["at"] = at
    shots.append(s)
SID = {s["what"]: s["id"] for s in shots}

# ---------------------------------------------------------------------------------------------------- acting
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "sit": False, "blink": True,
           "look": [0, 0], "expr": "neutral"}
acting = {k: [] for k in cast}
PLAYERS = ["p1", "p2", "p3", "p4", "p5"]


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


def quake(who, t0, n, amp, step=0.07, **base):
    """A body shaking: small fast lean and arm steps."""
    for k in range(n):
        v = amp if k % 2 else -amp
        acting[who].append({"at": f"{t0}+{k * step:.2f}", "lean": v, "arms": [base.get("a", 4) + v, base.get("a", 4) - v],
                            "blend": step * 0.8})


def players(at, expr="neutral"):
    for i, p in enumerate(PLAYERS):
        put(p, at, MARKS[i], yaw=0, expr=expr)


def answers(line):
    """Five voices answer in turn: a mouth flap each."""
    for i, p in enumerate(PLAYERS):
        a = round(0.0 + 0.2 * i, 2)
        talk(p, f"{line}+{a}", f"{line}+{a + 0.3}")


# me
put("me", 0, YEL, yaw=0, expr="worried")                                   # the frame: alone, in the ghost light
key("me", 0.5, mouth=0)
acting["me"].append({"from": 0, "to": "L01>", "mouth": [0.0, 0.3]})
put("me", "L04", ME_EDGE, yaw=0, expr="worried", arms=[0, 0])                # day: at the edge of the circle
put("me", "L11", [-2.3, -4.5, -0.41], yaw=90, expr="worried")                      # in the aisle by Marion's row
hide("me", "L12")
put("me", "L17", YEL, yaw=0, expr="neutral")
put("me", "L20", YEL, yaw=0, expr="worried")
key("me", "L21", expr="scared")
acting["me"].append({"from": "L22", "to": "L22>", "mouth": [0.8, 0.8]})
key("me", "L22", expr="scared")
key("me", "L26", expr="worried", head=[58, 0], blend=0.3)
put("me", "L28", YEL, yaw=0, expr="neutral")
key("me", "L30", expr="scared", look=[0.9, 0])
key("me", "L31", expr="scared", head=[60, 0], look=[0.9, 0], blend=0.4)
hide("me", "L32")
put("me", "L34", EDGE_ME, yaw=0, expr="neutral", sit=True)
hide("me", "L40")
put("me", "L40", YEL, yaw=0, expr="scared", look=[0.9, 0])
hide("me", "L41")                                                          # from my mark: the camera is my eyes
put("me", "L45", YEL, yaw=0, expr="scared", look=[0.9, 0])
put("me", "L47", YEL, yaw=0, expr="worried")
put("me", "L48", YEL, yaw=0, expr="scared", look=[0.9, 0])
hide("me", "L49")
put("me", "L52", YEL, yaw=0, expr="terrified", look=[0.9, 0])
put("me", "L53", [CAR[0] - 0.4, CAR[1] + 0.1, 0.01], yaw=0, expr="worried", sit=True)       # in the car
put("me", "L54", YEL, yaw=0, expr="neutral")
put("me", "L55", YEL, yaw=0, expr="worried")
key("me", "L57", expr="scared")
put("me", CH("L57", "and stepped"), [YEL[0], 3.75], yaw=0, expr="scared")                    # stepped back (on the cut)
put("me", "L59", [YEL[0], 3.75], yaw=0, expr="terrified")
put("me", "L62", [YEL[0], 3.75], yaw=0, expr="terrified")
hide("me", "L68")
put("me", "L69", [FLAT[0], FLAT[1] - 0.85, -0.06], yaw=180, expr="soft", sit=True)  # at the table (tired)
put("me", "L71", [FLAT[0], FLAT[1] - 0.85, -0.06], yaw=180, expr="soft", sit=True)
hide("me", "L71")
put("me", "L76", [FLAT[0], FLAT[1] - 0.85, -0.06], yaw=180, expr="worried", sit=True)
put("me", "L77", [FLAT[0], FLAT[1] - 0.85, -0.06], yaw=180, expr="soft", sit=True, arms=[52, 0])
put("me", "L78", YEL, yaw=0, expr="worried")
put("me", "L79", YEL, yaw=0, expr="worried")
quake("me", "L79", 11, 2.2, a=2)
put("me", "L80", [4.35, 2.4], yaw=180, expr="worried")
put("me", "L83", [3.2, 2.0], yaw=0, expr="worried")
key("me", CH("L83", "was there"), expr="soft")
put("me", "L84", YEL, yaw=0, expr="worried")
put("me", "L87", YEL, yaw=0, expr="scared")
put("me", "L88", YEL, yaw=0, expr="scared")
put("me", "L91", YEL, yaw=0, expr="worried")
key("me", "L92", expr="worried", arms=[0, 0], side=[0, 0])
key("me", "L92.1", side=[14, 14], blend=0.6)
acting["me"].append({"from": "L93", "to": "L93>", "mouth": [0.0, 0.5]})
key("me", "L93", expr="scared")
key("me", "L94", expr="worried", blend=0.4)
key("me", "L95", expr="soft")
acting["me"].append({"from": "L96", "to": "L96>", "mouth": [0.6, 0.6], "flap": True})
key("me", "L96", expr="soft", blend=0.1)

# Walt
hide("walt", 0)
put("walt", "L04", CHAIRS[5] + [-0.06], yaw=yaw_to(CHAIRS[5], [0, 3.2]), expr="neutral", sit=True)
put("walt", "L07", KING, yaw=0, expr="neutral")
key("walt", "L08", expr="neutral", head=[0, -12], blend=0.3)
key("walt", "L09", head=[0, 0])
hide("walt", "L11")
put("walt", "L17", KING, yaw=0)
key("walt", "L18", side=[75, 75], head=[0, -10], expr="neutral", blend=0.3)
key("walt", "L19", side=[0, 0], head=[0, 0], blend=0.4)
put("walt", "L28", KING, yaw=0, head=[0, -12])
key("walt", "L29", head=[0, 0])
put("walt", "L34", EDGE_WALT, yaw=0, sit=True, expr="neutral")
key("walt", "L37", expr="wide")
key("walt", "L38", expr="neutral")
key("walt", "L39", expr="worried", arms=[0, 88], side=[0, -20], blend=0.3)
put("walt", "L40", KING, yaw=0)
put("walt", "L47", KING, yaw=0, side=[75, 75], head=[0, -10])
key("walt", "L48", side=[0, 0], head=[0, 0], blend=0.4)
put("walt", "L54", KING, yaw=0)
key("walt", "L56", head=[0, -14], side=[75, 75], blend=0.3)
key("walt", "L57", side=[0, 0], head=[0, 0], blend=0.4)
put("walt", "L71", KING, yaw=180, expr="neutral")                           # memory: from behind, looking along the marks
put("walt", "L75", KING, yaw=0)
put("walt", "L78", KING, yaw=0)
put("walt", "L85", KING, yaw=0, head=[0, -14], side=[75, 75])
key("walt", "L86", side=[0, 0], head=[0, 0], blend=0.4)
key("walt", CH("L89", "was WAITING"), expr="neutral", head=[3, 2], blend=0.2)
key("walt", CH("L89", "was WAITING") + "+0.5", head=[3, 7], blend=0.15)
key("walt", CH("L89", "was WAITING") + "+0.8", head=[3, 1], blend=0.2)
key("walt", "L94", expr="soft", blend=0.4)
key("walt", "L95", expr="soft")

# the company
for i, p in enumerate(PLAYERS):
    hide(p, 0)
    put(p, "L04", CHAIRS[i] + [-0.06], yaw=yaw_to(CHAIRS[i], [0, 3.2]), sit=True)
    hide(p, "L07")
players("L17")
answers("L19")
players("L28")
answers("L29")
players("L45")
players("L47")
answers("L48")
players("L54")
answers("L57")
for p in ("p3", "p4", "p5"):                       # the three nearest the camera in the side-on shots
    hide(p, "L64")
    put(p, "L67", MARKS[PLAYERS.index(p)], yaw=0)
for i, p in enumerate(PLAYERS):
    put(p, "L72", MARKS[i], yaw=0)
    put(p, "L75", MARKS[i], yaw=0)
    put(p, "L78", MARKS[i], yaw=0)
answers("L86")

# Marion
hide("marion", 0)
ROW3_POS = [ROW3[0], ROW3[1], -0.45]
put("marion", "L06", ROW3_POS, yaw=180, expr="grin", sit=True, arms=[0, 85], side=[0, 5])
key("marion", CH("L06", "gave"), arms=[0, 0], blend=0.4)
hide("marion", "L07")
put("marion", "L11", ROW3_POS, yaw=180, expr="neutral", sit=True)
put("marion", "L12", ROW3_POS, yaw=180, expr="grin", sit=True, head=[0, -22], tremble=1.6)
put("marion", "L13", ROW3_POS, yaw=180, expr="grin", sit=True, arms=[30, 62], side=[0, 62])
hide("marion", "L14")
put("marion", "L25", ROW3_POS, yaw=180, expr="grin", sit=True)
for k in range(8):
    key("marion", f"L25+{0.3 + k * 0.17:.2f}", arms=[60 + (k % 2) * 8, 60 - (k % 2) * 8], blend=0.06)
key("marion", "L26", arms=[0, 0], blend=0.3)
hide("marion", "L26")
put("marion", "L67", ROW3_POS, yaw=180, expr="neutral", sit=True, head=[0, 24], arms=[40, 0])
hide("marion", "L68")

# ---------------------------------------------------------------------------------------------------- cues
cues = [
    # the mood of the light (set.py MOODS): every change is a ramp, never a cut
    {"at": 0, "name": "mood", "set": "ghost"},
    {"at": "L04", "name": "mood", "set": "work"},
    {"at": "L07", "name": "mood", "set": "warm"},
    {"at": "L16", "name": "mood", "set": "wing"},
    {"at": "L17", "name": "mood", "set": "warm"},
    {"at": "L34", "name": "mood", "set": "work"},
    {"at": "L40", "name": "mood", "set": "warm"},
    {"at": "L53", "name": "mood", "set": "car"},
    {"at": "L54", "name": "mood", "set": "warm"},
    {"at": "L58", "name": "mood", "set": "dim", "dur": 1.6},
    {"at": "L61", "name": "mood", "set": "cold", "dur": 1.8},
    {"at": "L69", "name": "mood", "set": "flat"},
    {"at": "L71", "name": "mood", "set": "cold"},
    {"at": "L74", "name": "mood", "set": "wing"},
    {"at": "L75", "name": "mood", "set": "cold"},
    {"at": "L76", "name": "mood", "set": "flat"},
    {"at": "L78", "name": "mood", "set": "open", "dur": 2.0},
    # the Prompter: where it stands, how it faces, the mouth (open from L50 on), and its own lights
    {"at": 0, "name": "prompter", "hidden": True},
    {"at": "L27", "name": "prompter", "pos": PP["mon"], "yaw": yaw_to(PP["mon"], YEL), "head": 0, "mouth": 0,
     "key_gain": 0.0, "rim_gain": 0.0},
    {"at": "L28", "name": "prompter", "hidden": True},
    {"at": "L32", "name": "prompter", "pos": PP["tue"], "yaw": yaw_to(PP["tue"], YEL), "head": 0, "mouth": 0,
     "key_gain": 0.8, "rim_gain": 0.7},
    {"at": "L34", "name": "prompter", "hidden": True},
    {"at": "L41", "name": "prompter", "pos": PP["wed"], "yaw": yaw_to(PP["wed"], YEL), "head": 0, "mouth": 0,
     "key_gain": 1.0, "rim_gain": 1.0},
    {"at": "L45", "name": "prompter", "pos": PP["thu"], "yaw": yaw_to(PP["thu"], YEL), "head": 0, "mouth": 0,
     "key_gain": 1.0, "rim_gain": 1.0},
    {"at": "L50", "name": "prompter", "pos": PP["thu"], "yaw": yaw_to(PP["thu"], YEL), "head": 0, "mouth": 1,
     "key_gain": 1.0, "rim_gain": 1.0},
    {"at": "L53", "name": "prompter", "hidden": True},
    {"at": "L62", "name": "prompter", "pos": PP["fri"], "yaw": 0, "head": 0, "mouth": 1, "key_gain": 0.9, "rim_gain": 0.9,
     "key": [-0.9, -0.9, 0.35]},
    {"at": "L64", "name": "prompter", "pos": PP["fri"], "yaw": 0, "head": 180, "mouth": 1, "key_gain": 0.9, "rim_gain": 0.9,
     "key": [1.2, 1.1, 0.4], "rim": [-0.5, -0.9, 2.6]},
    {"at": "L68", "name": "prompter", "hidden": True},
    {"at": "L75", "name": "prompter", "pos": PP["fri"], "yaw": 0, "head": 0, "mouth": 0, "key_gain": 0.9, "rim_gain": 0.9,
     "key": [-0.9, -0.9, 0.35]},
    {"at": "L76", "name": "prompter", "hidden": True},
    # costumes: the king's crown (a prop from Wednesday) and robe (dress rehearsal on), my cloak
    {"at": 0, "name": "costume", "who": "walt", "beard": True, "crown": False, "robe": False},
    {"at": "L34", "name": "costume", "who": "walt", "beard": True, "crown": True, "robe": False},
    {"at": "L40", "name": "costume", "who": "walt", "beard": True, "crown": False, "robe": False},
    {"at": "L54", "name": "costume", "who": "walt", "beard": True, "crown": True, "robe": True},
    {"at": "L71", "name": "costume", "who": "walt", "beard": True, "crown": False, "robe": False},
    {"at": "L85", "name": "costume", "who": "walt", "beard": True, "crown": True, "robe": True},
    {"at": 0, "name": "costume", "who": "me", "cloak": False},
    {"at": "L54", "name": "costume", "who": "me", "cloak": True},
    {"at": "L69", "name": "costume", "who": "me", "cloak": False},
    {"at": "L78", "name": "costume", "who": "me", "cloak": True},
    {"at": 0, "name": "chairs", "on": False},
    {"at": "L04", "name": "chairs", "on": True},
    {"at": "L06", "name": "chairs", "on": False},
    {"at": 0, "name": "audience", "on": False},
    {"at": "L78", "name": "audience", "on": True},
]

# ---------------------------------------------------------------------------------------------------- effects
# the clap at the end of P04, then a 0.36 s fade to black: twelve one-frame steps (a ramp, never a cut)
fx = []
for k in range(1, 12):
    fx.append({"at": f"P04>+{(k - 1) / 30:.4f}", "kind": "black", "dur": 1 / 30, "amp": round(k / 12, 4)})
fx.append({"at": f"P04>+{11 / 30:.4f}", "kind": "black", "dur": 3.0, "amp": 1.0})

# ---------------------------------------------------------------------------------------------------- sound
sfx = [
    {"at": "L21", "kind": "creak", "db": -26, "dur": 0.9},
    {"at": "L23", "kind": "whoosh", "db": -30},
    {"at": "L31+0.4", "kind": "creak", "db": -24, "dur": 0.9},
    {"at": "L43", "kind": "riser", "db": -30, "dur": 1.2},
    {"at": "L44", "kind": "sting", "db": -13, "dur": 1.6},
    {"at": "L48+0.3", "kind": "creak", "db": -24, "dur": 0.9},
    {"at": "L50", "kind": "hit", "db": -9, "dur": 1.6},
    {"at": "L52", "kind": "breath", "db": -30},
    {"at": "L59+0.2", "kind": "creak", "db": -9, "dur": 1.0},
    {"at": "L62", "kind": "riser", "db": -28, "dur": 1.3},
    {"at": "L66>", "kind": "hit", "db": -8, "dur": 1.6},
    {"at": "L87", "kind": "creak", "db": -30, "dur": 0.8},
    {"at": "L93", "kind": "bell", "db": -34},
    {"at": "P04>", "kind": "clap", "db": -9, "dur": 0.9},
]

story = {
    "slug": "ep23-only-line",
    "title": "Every rehearsal, my one line comes out of the wings in my own voice",
    "made_for_kids": False,
    "premise": "I'm a quiet adult who joined a small old playhouse's volunteer company to meet people, with one line in the last scene, where the old king asks who stands with him and each player answers from a tape mark. Every run of rehearsal week I freeze, and my line comes out of the dark wings in my own voice. The thing saying it, a small figure with a huge gilt stage mask for a head, is one curtain nearer each run.",
    "twist": "The scene is a roll call and no mark can stay empty. Every time I froze, the Prompter answered for me so the count came out right: it was keeping my place all week. On opening night, with the wings empty, I say the line for the first time myself.",
    "world": "a small old playhouse in rehearsal week: a raked stage of scuffed boards, a soot-black proscenium, bottle-green curtain legs down stage left, a ghost light, tape marks, an empty house of plum-grey seats",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff8fb1",
    "caption": {"ink": "#08090d", "stroke_add": 1, "shadow": 0.7},
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#080a12", "fog_density": 0.02, "fog_start": 5.0, "sky": "#05060a", "sky_strength": 1.0,
             "exposure": 0.0},
    "grade": {"shadows": [-0.01, 0.0, 0.04], "highlights": [0.03, 0.01, -0.03], "saturation": 0.95, "contrast": 1.06,
              "vignette": 0.34, "bloom": 0.22, "grain": 0.012, "red_line": 0.79},
    "asr_ignore_tail_repeat": True,   # Whisper repeats the last line after the held silence; the film has no words there
    "phonemes": {},
    "places": {"marks": MARKS, "legy": LEGY, "king": KING, "chairs": CHAIRS, "ghost": [-0.3, 2.0], "flat": list(FLAT),
               "car": list(CAR)},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    # A Phrygian, 66 bpm: a low reed drone and a soft wooden tick on every beat. The tick stops under each freeze
    # (L21, L31, L48, L59). Opening night the drone lifts to A major, very quiet under L94 to L96, then out.
    "music": {"root": 45, "mode": "phrygian", "bpm": 66, "seed": 23,
              "sections": [
                  {"at": 0, "voices": ["drone", "tick"], "energy": 0.35},
                  {"at": "L21", "voices": ["drone"], "energy": 0.3},
                  {"at": "L24", "voices": ["drone", "pad", "tick"], "energy": 0.4},
                  {"at": "L31", "voices": ["drone"], "energy": 0.3},
                  {"at": "L33", "voices": ["drone", "pad", "tick"], "energy": 0.45},
                  {"at": "L44", "voices": ["drone", "choir"], "energy": 0.4},
                  {"at": "L45", "voices": ["drone", "pad", "tick"], "energy": 0.5},
                  {"at": "L48", "voices": ["drone"], "energy": 0.3},
                  {"at": "L51", "voices": ["drone", "pad", "choir"], "energy": 0.55},
                  {"at": "L54", "voices": ["drone", "pad", "tick"], "energy": 0.45},
                  {"at": "L59", "voices": ["drone"], "energy": 0.25},
                  {"at": "L62", "voices": ["drone", "pad", "choir"], "energy": 0.6},
                  {"at": "L69", "voices": ["pad", "tick"], "energy": 0.25},
                  {"at": "L75", "voices": ["drone", "pad"], "energy": 0.35},
                  {"at": "L78", "voices": ["drone", "pad"], "energy": 0.3, "mode": "major", "root": 45},
                  {"at": "L94", "voices": ["drone"], "energy": 0.12, "mode": "major", "root": 45},
                  {"at": "P04", "voices": [], "energy": 0.0},
              ]},
    "sound": {"floor": "wood", "steps_db": -22,
              "ambience": [
                  {"kind": "room", "from": 0, "to": "end", "lufs": -35},
                  {"kind": "hum", "from": 0, "to": "L04", "lufs": -42},
                  {"kind": "wind", "from": "L27", "to": "L28", "lufs": -44},
                  {"kind": "hum", "from": "L58", "to": "L61", "lufs": -40},
                  {"kind": "hum", "from": "L69", "to": "L71", "lufs": -42},
                  {"kind": "hum", "from": "L76", "to": "L78", "lufs": -42},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "L50", "keep": ["hit"]},
                              {"from": "L61-0.7", "to": "L61+0.3"},
                              {"from": "P03", "to": "L67", "keep": ["hit"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
