"""Writes ../story.json for ep50 "In this town, your reflection does what you really want to do".

Run: python stories/ep50-beach-huts/generator/make_story.py
The words are lines.json (the writer's, from script.md). The cast, shots, cameras, acting, cues, reflections, score and
sound are here. Places (set.py's metres): the hut row is along x at y = 0, fronts toward -y (the sea); ours is hut 5 at
x = 0; the deck top is z 0.3. Town rooms: office x 200, bakery 300, shop 400 (cubicle) and 420 (window), cafe 500, all
at y about 40. The bench is at x 46.8, y -5.6.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
LOOP = 0.25
# captions are two or three words: a longer chunk is cut in two. NEWIDX maps the writer's chunk numbers (used in every
# time reference below) to the new ones.
NEWIDX = {}
for ln in lines:
    out, m = [], {}
    for k, (cap, sp) in enumerate(ln["chunks"]):
        m[k] = len(out)
        cw, sw = cap.split(), sp.split()
        wide = (len(cw) == 3 and sum(len(w) for w in cw) > 17)
        if len(cw) > 3 or wide:
            h = len(cw) // 2 if wide else (len(cw) + 1) // 2
            if wide:
                h = 2
            out += [[" ".join(cw[:h]), " ".join(sw[:h])], [" ".join(cw[h:]), " ".join(sw[h:])]]
        else:
            out.append([cap, sp])
    ln["chunks"] = out
    NEWIDX[ln["id"]] = m
lines = lines + [{"id": "P03", "pause": LOOP, "chunks": []}]


def R(ref):
    """Translate 'L12.1+0.4' (writer's chunk numbers) to the split numbering."""
    import re
    if not isinstance(ref, str):
        return ref
    m = re.match(r"^(L\d+)\.(\d+)(.*)$", ref)
    if not m or m.group(1) not in NEWIDX:
        return ref
    return f"{m.group(1)}.{NEWIDX[m.group(1)][int(m.group(2))]}{m.group(3)}"

# ------------------------------------------------------------------------------------------------- cast
FACE = {"eyes": "round", "brows": True}
cast = {
    "me": {"age": "adult", "skin": "#e6bf98", "shirt": "#a8552e", "pattern": "solid", "collar": "#8c8c92",
           "pants": "#2f3033", "shoes": "#2a2522", "sleeves": "long", "hair": "swoop", "hair_c": "#a07850",
           "extras": ["coat"], "zip_c": "#e8dfc8", "face": FACE},
    "remi": {"age": "adult", "skin": "#b98760", "shirt": "#e8dfc8", "pattern": "knit", "pattern_c": "#cbbd9b",
             "pants": "#4b6a8f", "shoes": "#3a3028", "sleeves": "long", "hair": "bun", "hair_c": "#241812",
             "extras": ["scarf"], "extra_c": "#d9a441", "face": {"eyes": "lashes", "brows": True}},
    "neighbour": {"age": "adult", "skin": "#d9a98a", "shirt": "#e8e8ee", "pattern": "stripes", "pattern_c": "#243a5e",
                  "pants": "#2d3a4f", "shoes": "#222222", "sleeves": "long", "hair": "cap", "hair_c": "#c9c9c9",
                  "hat": "beanie", "hat_c": "#b83a32", "face": {"eyes": "round", "brows": True}},
    "o1": {"age": "adult", "skin": "#d9a98a", "shirt": "#a9c4dc", "pattern": "solid", "collar": "#e8ecef",
           "pants": "#2b2f38", "shoes": "#1c1c1c", "sleeves": "long", "hair": "spiky", "hair_c": "#3a2a20",
           "face": {"eyes": "tired", "brows": True}},
    "o2": {"age": "adult", "skin": "#8d5a3c", "shirt": "#e9ecef", "pattern": "solid", "collar": "#cfd6dc",
           "pants": "#3a3f4a", "shoes": "#1c1c1c", "sleeves": "long", "hair": "buzz", "hair_c": "#141010", "extras": ["tie"],
           "extra_c": "#6b2f3a", "face": {"eyes": "round", "brows": True}},
    "o3": {"age": "adult", "skin": "#e6bf98", "shirt": "#7d8450", "pattern": "solid", "collar": "#6a7144",
           "pants": "#2b2f38", "shoes": "#1c1c1c", "sleeves": "long", "hair": "long", "hair_c": "#6b4a2e",
           "face": {"eyes": "lashes", "brows": True}},
    "dieter": {"age": "adult", "skin": "#c99673", "shirt": "#8a8f96", "pattern": "solid", "pants": "#8a8f96",
               "shoes": "#d9d9d9", "sleeves": "long", "hair": "buzz", "hair_c": "#141010",
               "face": {"eyes": "round", "brows": True}},
    "shopper": {"age": "adult", "skin": "#8d5a3c", "shirt": "#b7a6c9", "pattern": "solid", "pants": "#2c2c34",
                "shoes": "#2c2c34", "sleeves": "long", "hair": "long", "hair_c": "#2a1d15", "extras": ["coat"],
                "zip_c": "#e8e0f0", "face": {"eyes": "lashes", "brows": True}},
    "date_f": {"age": "adult", "skin": "#e3b894", "shirt": "#2f5f4a", "pattern": "solid", "pants": "#2c2c34",
               "shoes": "#2c2c34", "sleeves": "long", "hair": "bun", "hair_c": "#4a2c1c", "extras": ["coat"],
               "zip_c": "#d9cf9f", "face": {"eyes": "lashes", "brows": True}},
    "date_m": {"age": "adult", "skin": "#c68f68", "shirt": "#7a5230", "pattern": "solid", "pants": "#3a3a40",
               "shoes": "#2a2522", "sleeves": "long", "hair": "cap", "hair_c": "#1c1410",
               "face": {"eyes": "round", "brows": True}},
    "smallhead": {"age": "adult", "skin": "#cfc3a6", "shirt": "#b5655a", "pattern": "solid", "pants": "#6a7480",
                  "shoes": "#4a4f58", "sleeves": "short", "hair": "none", "height": 1.3, "width": 1.3, "head_scale": 0.5,
                  "face": {"eyes": "dot", "mouth": "line", "brows": False}},
}
reflections = {
    "r_neighbour": {"of": "neighbour"},
    "r_o1": {"of": "o1"}, "r_o2": {"of": "o2"}, "r_o3": {"of": "o3"},
    "r_dieter": {"of": "dieter"},
    "r_shopper": {"of": "shopper", "set": {"shirt": "#c86a6a", "zip_c": "#f0d0c0"}},
    "r_date_f": {"of": "date_f"}, "r_date_m": {"of": "date_m"},
    "r_remi": {"of": "remi"},
    "r_me": {"of": "me", "tint": 0.06},
}


# ------------------------------------------------------------------------------------------------- helpers
def c(*keys):
    return [list(k) for k in keys]


def still(loc, tgt, lens):
    return c([0, list(loc), list(tgt), lens])


def move(a, b, lens_a, lens_b=None):
    return c([0, list(a[0]), list(a[1]), lens_a], [1, list(b[0]), list(b[1]), lens_b or lens_a])


def yaw_to(a, b):
    return round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 1)


DECK = 0.30
ME_SIT = (-0.35, -0.6)
CHAIR_A = (-1.2, -1.4)
CHAIR_B = (1.3, -1.5)
LANT = (1.85, -2.4)
BX, OFFX, SHOPX, SHOPWX, CAFEX = 300.0, 200.0, 400.0, 420.0, 500.0
BENCH = (46.8, -5.6)

# --------------------------------------------------------------------------------------------- the shots
# (at, name, camera, extras) where extras may hold step, follow, hand, stage (hut), refl {name: kind}, puddle, dof
SHOTS = []


def S(at, what, cam, step=2, **kw):
    SHOTS.append((at, what, cam, step, kw))


NSTAGE = lambda h, **r: dict(stage={"hut": h}, refl=r)

# 01 the rule
S(0, "neighbour at his window, cartwheel in the glass", still((-3.1, -3.6, 1.55), (-3.1, 0, 1.5), 26), 1,
  **NSTAGE(4, r_neighbour="stage"))
S("L01.2", "high wide of the sand, figures and reflections, the rust figure", still((10, -31, 6.5), (11, -7, 0.8), 18), 2,
  refl={"r_dieter": "sand", "r_shopper": "sand", "r_date_f": "sand", "r_me": "sand"})
S("L02", "close on the neighbour", still((-3.5, -2.5, 1.62), (-3.55, -0.8, 1.55), 40))
S("L02.2", "the glass alone", still((-3.0, -1.7, 1.45), (-3.0, 0, 1.45), 28), 1, **NSTAGE(4, r_neighbour="stage"))
S("L03", "office: reflections asleep in the glass top", still((OFFX, 36.5, 1.9), (OFFX, 40.3, 0.9), 20), 2,
  refl={"r_o1": {"kind": "table", "base": 0.78}, "r_o2": {"kind": "table", "base": 0.78},
        "r_o3": {"kind": "table", "base": 0.78}})
S("L04", "dieter passes the bakery", still((BX - 0.3, 36.8, 1.5), (BX + 0.4, 41.5, 1.35), 26))
S("L04.2", "his reflection face down in the cake", still((BX + 0.2, 38.2, 1.45), (BX + 0.2, 43.0, 1.3), 28), 2,
  refl={"r_dieter": "glass"})
S("L05", "the pale rectangle in the cubicle", still((SHOPX, 38.7, 1.45), (SHOPX, 41.4, 1.3), 28))
S("L05.2", "shop window: she stands, her reflection walks out", still((SHOPWX + 0.4, 36.2, 1.5), (SHOPWX + 0.4, 41.5, 1.4), 22),
  2, refl={"r_shopper": "glass"})
S("L06", "the date at the cafe", still((CAFEX + 0.2, 38.2, 1.35), (CAFEX, 41.9, 1.1), 26))
S("L06.1", "cafe window: their reflections close", still((CAFEX, 40.3, 1.35), (CAFEX, 43.0, 1.2), 28), 2,
  refl={"r_date_f": "glass", "r_date_m": "glass"})
S("L07", "me at the window: no me in the glass", still((0.9, -2.6, 1.5), (0.8, 0, 1.4), 24), 2, **NSTAGE(5))
S("L08", "the puddle with nothing of me in it", still((-1.0, -2.05, 0.5), (-1.0, -1.1, 0.3), 32), 2, puddle=True)
S("L09", "me on the step, laptop open", still((-1.0, -2.8, 1.25), (-0.3, -0.6, 1.2), 30))
# 02 Remi's reflection
S("L10", "Remi on the deck", still((-0.9, -3.2, 1.5), (-1.4, -1.0, 1.4), 32))
S("L11", "Remi sanding the frame", still((2.6, -1.8, 1.5), (1.0, -0.3, 1.4), 30))
S("L12", "me on the step, the chair folded", still((0.9, -2.8, 1.3), (0.4, -0.6, 1.1), 26))
S("L12.1", "the window: Remi's reflection stopped", still((1.0, -1.7, 1.45), (1.0, 0, 1.45), 28), 2, **NSTAGE(5, r_remi="stage"))
S("L13", "laptop glow on my face", still((-1.3, -1.6, 1.45), (-0.35, -0.7, 1.4), 50))
S("L14", "Remi sands, her reflection walks", still((1.15, -1.7, 1.45), (1.25, 0, 1.45), 28), 2, **NSTAGE(5, r_remi="stage"))
S("L15", "Monday: at the water's edge", still((1.0, -1.7, 1.45), (1.0, 0, 1.45), 28), 2, **NSTAGE(5, r_remi="stage"))
S("L16", "Tuesday: past the boats", still((1.0, -1.7, 1.45), (1.0, 0, 1.45), 28), 2, **NSTAGE(5, r_remi="stage"))
S("L17", "Thursday: a dot on the point", still((1.0, -1.35, 1.45), (1.0, 0, 1.45), 28), 2, **NSTAGE(5, r_remi="stage", r_me="stage"))
S("L18", "the reflection's back", still((1.0, -1.5, 1.45), (1.0, 0, 1.45), 28), 2, **NSTAGE(5, r_remi="stage"))
S("L18.2", "Remi turns to look at me", still((0.5, -2.4, 1.5), (1.0, -0.8, 1.45), 34))
S("L19", "Remi, worried, scarf to her chin", still((-0.8, -2.8, 1.55), (-1.4, -1.0, 1.5), 36))
S("L20", "me, sheepish, back to the laptop", still((0.5, -2.4, 1.3), (-0.35, -0.6, 1.35), 34))
S("L21", "morning: the second chair set out", still((0.4, -3.6, 1.1), (1.3, -1.5, 0.5), 30))
S("L22", "the canvas, stretched and sagging", still((1.35, -2.4, 0.75), (1.3, -1.5, 0.5), 38))
S("L22.2", "the two of us in the doorway", still((1.7, -2.4, 1.5), (0.1, -0.5, 1.4), 28))
S("L23", "inside: the kettle", still((0.6, 1.75, 1.4), (-1.2, 1.0, 1.1), 30))
# 03 gone
S("L24", "dusk on my laptop face", still((0.7, -2.6, 1.35), (-0.35, -0.6, 1.35), 32))
S("P01", "hold on my face", still((0.2, -2.0, 1.45), (-0.35, -0.6, 1.45), 44), 1)
S("L25", "the deck, her chair empty", still((0.5, -4.8, 1.8), (-0.3, -1.0, 0.9), 22))
S("L26", "her scarf on the chair", still((-1.0, -2.2, 0.95), (-1.2, -1.4, 0.7), 36))
S("L27", "her phone in the fold", still((-1.05, -1.9, 0.95), (-1.2, -1.42, 0.8), 50))
S("L28", "the hasp as the door swings", move(((-0.44, -0.5, 1.28), (-0.43, 0, 1.22)), ((0.12, -1.1, 1.3), (-0.21, -0.6, 1.22)), 50), 1)
S("L29", "her reflection still walking", still((1.0, -1.6, 1.45), (1.0, 0, 1.45), 28), 2, **NSTAGE(5, r_remi="stage"))
S("L30", "the glass and the empty deck", still((1.0, -2.6, 1.4), (1.0, 0, 1.35), 24), 2, **NSTAGE(5, r_remi="stage"))
S("L31", "running the row", c([0, [-1.2, -2.6, 1.35], [0.8, 0, 1.2], 26]), 2, follow="me")
S("L31.2", "the row from the end", still((26, -4.5, 1.7), (9, -1.0, 1.3), 22))
S("L32", "mint window", still((5.0, -1.7, 1.45), (5.0, 0, 1.45), 28), 2, **NSTAGE(6, r_remi="stage"))
S("L32.2", "lilac window", still((9.0, -1.7, 1.45), (9.0, 0, 1.45), 28), 2, **NSTAGE(7, r_remi="stage"))
S("L33", "coral window: no me", still((13.0, -6.8, 1.6), (13.0, 0, 1.4), 40), 2, **NSTAGE(8))
S("L34", "the last window: a dot", still((25.0, -1.5, 1.45), (25.0, 0, 1.45), 28), 2, **NSTAGE(11, r_remi="stage"))
S("L34.2", "the row at blue dusk", still((31, -6.5, 2.4), (11, -1, 1.5), 20))
S("L35", "walking back", c([0, [-1.6, -2.6, 1.4], [0.6, 0, 1.3], 28]), 2, follow="me")
S("L36", "I sit down again", still((0.7, -2.6, 1.3), (-0.35, -0.6, 1.3), 32))
# 04 beside me
S("L37", "the chair has turned", still((-0.5, -0.14, 1.7), (1.3, -1.5, 0.8), 26))
S("L38", "low behind the chair, me beyond", still((1.9, -2.4, 0.6), (-0.3, -0.6, 0.95), 28))
S("L39", "me, the canvas edge sinking", still((2.3, -0.9, 1.45), (-0.3, -0.6, 1.4), 34))
S("L40", "the lantern comes on", still((1.3, -3.3, 0.4), (1.85, -2.4, 0.45), 34))
S("L41", "me, lit from below", still((0.5, -2.0, 1.0), (-0.35, -0.6, 1.35), 36))
S("L42", "the shadow up the wall", still((-3.1, -1.3, 0.7), (0.9, 0, 1.7), 24))
S("L42.1", "its top beside the doorway", still((-1.2, -1.2, 1.9), (0.6, 0, 2.0), 28))
S("L43", "the tiny head on the wall", still((-0.6, -0.9, 2.0), (0.8, 0, 2.0), 40))
S("P02", "hold on my face", still((0.5, -1.9, 1.45), (-0.35, -0.6, 1.45), 50), 1)
# 05 the Small Head
S("L44", "I turn my head", still((-1.1, -1.8, 1.5), (-0.35, -0.6, 1.45), 45), 1)
S("L45", "the reveal", still((0.4, -5.4, 1.2), (1.3, -1.5, 1.3), 24), 1)
S("L46", "the stripes", still((0.2, -1.5, 1.0), (1.2, -1.5, 1.0), 42), 1)
S("L47", "spilling over the chair", still((0.1, -2.7, 0.4), (1.3, -1.5, 0.7), 24), 1)
S("L48", "tilt up to the head", move(((0.3, -1.4, 0.9), (1.3, -1.5, 1.0)), ((0.3, -1.4, 1.1), (1.3, -1.5, 1.9)), 40), 1)
S("L49", "its head bends down", still((0.6, -3.4, 1.45), (0.6, -1.0, 1.4), 26), 1)
S("L50", "closer", still((0.6, -3.4, 1.45), (0.6, -1.0, 1.4), 26), 1)
S("L51", "closer still", still((0.5, -2.2, 1.5), (0.4, -0.9, 1.5), 32), 1)
S("L52", "its dot eyes", still((0.0, -1.1, 1.6), (0.5, -1.0, 1.6), 55), 1)
S("L52.2", "its view: me and the laptop", still((0.5, -0.95, 1.7), (-0.35, -0.7, 1.1), 30), 1)
S("L53", "over its shoulder to the glass", still((1.95, -1.9, 1.9), (1.0, 0, 1.45), 28), 2, **NSTAGE(5))
S("L54", "no reflection either", still((1.0, -1.0, 1.45), (1.0, 0, 1.45), 30), 2, **NSTAGE(5))
S("L55", "far down the shore: Remi has stopped", still((1.0, -1.1, 1.45), (1.0, 0, 1.45), 30), 2, **NSTAGE(5, r_remi="stage"))
S("L56", "a small figure in my coat beside her", still((1.0, -0.85, 1.45), (1.0, 0, 1.45), 38), 2,
  **NSTAGE(5, r_remi="stage", r_me="stage"))
S("L57", "me, calm now", still((0.8, -1.3, 1.45), (-0.35, -0.7, 1.45), 40), 1, dof=(1.0, 0.7))
S("L58", "two figures on the bench", still((1.0, -0.85, 1.45), (1.0, 0, 1.45), 38), 2,
  **NSTAGE(5, r_remi="stage", r_me="stage"))
S("L58.2", "my eyes go to the shore", still((0.5, -2.4, 1.5), (-0.35, -0.7, 1.45), 40), 2)
S("L59", "the wide again: the rust figure", still((10, -31, 6.5), (11, -7, 0.8), 18), 2, refl={"r_me": "sand"})
S("L60", "the lid comes down", still((0.2, -1.4, 1.1), (-0.35, -1.0, 0.8), 45), 1)
S("L61", "stepping down", still((-2.4, -5.0, 1.3), (-0.5, -2.2, 1.0), 26), 2)
S("L61.2", "over my shoulder", still((-0.7, -5.7, 1.5), (1.2, -1.5, 1.0), 28), 2)
# 06 the bench
S("L62", "coral window: my reflection beside me", still((13.0, -6.8, 1.6), (13.0, 0, 1.4), 40), 2, **NSTAGE(8, r_me="stage"))
S("L62.2", "mint window: there again", still((17.0, -6.8, 1.6), (17.0, 0, 1.4), 40), 2, **NSTAGE(9, r_me="stage"))
S("L63", "Remi on the bench", still((46.0, -9.6, 1.25), (46.6, -5.6, 1.0), 32))
S("L64", "me arriving", still((44.4, -8.3, 1.4), (47.0, -6.2, 1.25), 26))
S("L65", "two reflections in the sand", still((44.9, -8.6, 0.45), (46.8, -5.6, -0.4), 26), 2,
  refl={"r_remi": "sand", "r_me": "sand"})
S("L65.2", "me looking down", still((46.0, -9.8, 1.5), (47.3, -7.0, 1.3), 30))
S("L66", "hers faces mine", still((45.6, -8.0, 0.4), (46.8, -5.6, -0.5), 30), 2, refl={"r_remi": "sand", "r_me": "sand"})
S("L67", "keeping me in sight", still((46.4, -8.2, 1.2), (46.3, -5.6, 1.05), 40))
S("L68", "I sit down beside her", still((44.0, -11.5, 1.5), (47.0, -5.6, 0.9), 22))
S("L69", "our reflections in the pool", still((45.4, -7.9, 0.4), (46.8, -5.6, -0.4), 30), 2,
  refl={"r_remi": "sand", "r_me": "sand"})
S("L69.2", "the two of us, the same", still((45.2, -9.6, 1.25), (46.8, -5.6, 0.95), 30))
# 07 making time
S("L70", "walking back toward the lanterns", still((40.5, -12.0, 1.5), (40.0, -6.8, 1.0), 26))
S("L70.2", "me listening", c([0, [-0.9, -1.5, 1.45], [0.0, 0.0, 1.45], 40]), 2, follow="me")
S("L71", "the chair is empty", still((0.4, -3.5, 1.0), (1.3, -1.5, 0.5), 30))
S("L71.1", "we sit, the lantern between", still((0.0, -4.0, 1.3), (0.0, -1.5, 1.0), 26))
S("L72", "the laptop shut on the shelf", still((0.6, 1.75, 1.7), (-1.4, 1.1, 1.8), 32))
S("L73", "golden evening on the sand", still((5.5, -14.5, 1.3), (5.5, -6.8, 0.9), 20), 2,
  refl={"r_me": "sand", "r_remi": "sand"})
S("L73.2", "just the two reflections", still((5.5, -9.5, 0.5), (6.0, -6.8, -0.4), 26), 2,
  refl={"r_me": "sand", "r_remi": "sand"})
S("L74", "both reflections in our window", still((0.35, -2.7, 1.45), (0.35, 0, 1.4), 24), 2, **NSTAGE(5, r_me="stage", r_remi="stage"))
S("L75", "mine, smiling", still((1.0, -1.2, 1.45), (1.0, 0, 1.45), 32), 2, **NSTAGE(5, r_me="stage"))
S("L76", "this morning: our window, the empty chair", still((0.6, -4.2, 1.5), (0.9, -0.8, 1.0), 24), 1, **NSTAGE(5))
S("L76.2", "far down the sand, the rust figure alone", still((9.0, -6.0, 1.3), (18.0, -9.5, 0.7), 22), 1, refl={"r_me": "sand"})

shots = []
shotx = {}
SHOTS = [(R(a), w, c_, st, kw) for a, w, c_, st, kw in SHOTS]
for i, (at, what, cam, step, kw) in enumerate(SHOTS):
    sid = f"S{i + 1:02d}"
    s = {"id": sid, "cam": cam, "hand": 0.006 if step == 1 else 0.004, "step": step, "what": what}
    if sid in ("S99", "S100"):
        s["hand"] = 0.0
    if i:
        s["at"] = at
    if kw.get("follow"):
        s["follow"] = kw["follow"]
    shots.append(s)
    x = {k: v for k, v in kw.items() if k in ("stage", "refl", "puddle", "dof")}
    if x:
        shotx[sid] = x

# ------------------------------------------------------------------------------------------------ acting
acting = {n: [] for n in list(cast) + list(reflections)}
NEUTRAL = {"arms": [0, 0], "side": [0, 0], "head": [0, 0], "lean": 0, "tremble": 0, "sit": False, "bow": 0, "roll": 0}


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


for n in acting:
    hide(n, 0)
    acting[n][-1]["pos"] = [0, 0]

SMILE, GRIN = "smirk", "grin"
SEAT = 0.51       # a sitter's root sits this far under the seat top

# --- the neighbour and his cartwheeling reflection
put("neighbour", 0, [-3.55, -0.85], yaw=0)
hide("neighbour", "L03")
put("r_neighbour", 0, [0.3, 0.07, 0.45], yaw=0, roll=150, side=[85, 85], expr="grin")
key("r_neighbour", "L01.1", roll=-150, blend=0.5)
key("r_neighbour", "L01.3", roll=110, blend=0.4)
key("r_neighbour", "L02.2", roll=8, blend=0.35, pos=[0.3, 0.07, 0.0])
key("r_neighbour", "L02.2+0.5", roll=150, blend=0.4)
hide("r_neighbour", "L03")

# --- the sand figures (L01) and their reflections
put("dieter", 0, [8.0, -13.0], yaw=0)
put("shopper", 0, [3.5, -15.0], yaw=0)
put("date_f", 0, [13.0, -10.5], yaw=0)
hide("dieter", "L03"); hide("shopper", "L03"); hide("date_f", "L03")
put("r_dieter", 0, [8.0, -13.0], yaw=0, side=[70, 70], expr="grin")        # dancing
key("r_dieter", "L01.2+0.4", side=[10, 80], head=[25, 0], blend=0.4)
key("r_dieter", "L01.2+0.9", side=[80, 10], head=[-25, 0], blend=0.4)
key("r_dieter", "L01.3", side=[10, 80], blend=0.4)
key("r_dieter", "L01.3+0.5", side=[80, 10], blend=0.4)
put("r_shopper", 0, [3.5, -15.0], yaw=0, lean=-88, expr="soft")             # lying flat, sunbathing
put("r_date_f", 0, [13.0, -10.5], yaw=0, arms=[170, 0], expr="grin")       # waving
key("r_date_f", "L01.2+0.3", arms=[130, 0], blend=0.3)
key("r_date_f", "L01.2+0.6", arms=[170, 0], blend=0.3)
key("r_date_f", "L01.3", arms=[130, 0], blend=0.3)
key("r_date_f", "L01.3+0.4", arms=[170, 0], blend=0.3)
# the rust figure in the wet sand only, walking toward the point (+x)
put("r_me", 0, [16.5, -8.5], yaw=90)
walk("r_me", "L02", [17.6, -8.5])
for who in ("r_dieter", "r_shopper", "r_date_f"):
    hide(who, "L03")

# --- the office
for k, (n, x) in enumerate((("o1", OFFX - 1.0), ("o2", OFFX), ("o3", OFFX + 1.0))):
    put(n, "L03", [x, 40.95], yaw=0)
    hide(n, "L04")
    put("r_" + n, "L03", [x, 40.45], yaw=0, bow=50, head=[0, 35], expr="asleep", blink=False)
    hide("r_" + n, "L04")

# --- the bakery
put("dieter", "L04", [BX - 2.4, 40.2], yaw=90, head=[0, -12])
walk("dieter", "L04.2", [BX + 0.6, 40.2], head=[0, -12])
key("dieter", "L04.2+0.6", head=[0, -12])
hide("dieter", "L05")
put("r_dieter", "L04.2", [BX + 0.2, 43.8, 0.85], yaw=0, bow=82, head=[0, 20], expr="shut")
hide("r_dieter", "L05")

# --- the shop
put("shopper", "L05.2", [SHOPWX - 0.5, 40.1], yaw=0)
hide("shopper", "L06")
put("r_shopper", "L05.2", [SHOPWX + 0.3, 42.6], yaw=0)
walk("r_shopper", "L05.2+1.2", [SHOPWX + 2.4, 42.6])
hide("r_shopper", "L06")

# --- the cafe
put("date_f", "L06", [CAFEX - 0.45, 41.95, -SEAT + 0.46], yaw=0, sit=True, expr="smirk", head=[60, 0])
put("date_m", "L06", [CAFEX + 0.45, 41.95, -SEAT + 0.46], yaw=0, sit=True, expr="smirk", head=[-60, 0])
hide("date_f", "L06.1"); hide("date_m", "L06.1")
put("r_date_f", "L06.1", [CAFEX - 0.18, 44.0, -SEAT + 0.46], yaw=0, sit=True, expr="grin", arms=[45, 0])
put("r_date_m", "L06.1", [CAFEX + 0.18, 44.0, -SEAT + 0.46], yaw=0, sit=True, expr="grin", arms=[0, 45])
hide("r_date_f", "L07"); hide("r_date_m", "L07")

# --- me and Remi on the deck, morning
put("me", "L07", [0.35, -1.0], yaw=0)
put("me", "L08", [-1.0, -1.75], yaw=0)
ME_Z = 0.36 - SEAT
SIT_ME = dict(sit=True, arms=[68, 68], side=[0, 0], head=[0, 22])
put("me", "L09", [ME_SIT[0], ME_SIT[1], ME_Z], yaw=0, **SIT_ME)
key("me", "L12.1", expr="neutral")
put("me", "L22.2", [-0.2, -0.55, 0.36], yaw=52, expr="worried", head=[25, 0])
put("me", "L24", [ME_SIT[0], ME_SIT[1], ME_Z], yaw=0, **SIT_ME)
key("me", "P01", expr="neutral")
hide("me", "L25")
put("me", "L31", [-0.6, -1.1], yaw=90, expr="scared")
walk("me", "L31.2", [9.5, -1.1], expr="scared", run=True)
walk("me", "L32", [9.5, -1.1])
put("me", "L33", [10.8, -1.0], yaw=90, expr="scared")
walk("me", "L33+1.4", [15.2, -1.0], run=True)
hide("me", "L34")
put("me", "L34.2", [24.5, -1.1], yaw=-90, expr="worried")
walk("me", "L35", [20.0, -1.1], expr="worried")
walk("me", "L36", [1.0, -1.1], expr="worried")
put("me", "L36", [ME_SIT[0], ME_SIT[1], ME_Z], yaw=0, **SIT_ME)
key("me", "L38", expr="worried")
key("me", "L39", expr="scared", head=[0, 22], blend=0.3)
key("me", "L41", expr="scared")
key("me", "L44", head=[0, 12], blend=0.2)
key("me", "L44", head=[42, 6], blend=1.1)
key("me", "L49", head=[48, 8], expr="scared")
key("me", "L57", expr="neutral", head=[42, 4])
key("me", "L58.2", head=[-5, 0], blend=0.6)
key("me", "L60", arms=[68, 68], head=[0, 24], blend=0.4)
put("me", "L61", [ME_SIT[0], ME_SIT[1], 0.36], yaw=0, expr="neutral")
walk("me", "L61+0.5", [-0.8, -3.6], expr="neutral")
walk("me", "L61.2+0.9", [-0.9, -5.2], expr="neutral")
# the walk to the bench (left of the row's end): jump cuts
put("me", "L62", [11.2, -1.2], yaw=90, expr="neutral")
walk("me", "L62+1.2", [14.2, -1.2])
put("me", "L62.2", [15.8, -1.2], yaw=90)
walk("me", "L62.2+1.3", [18.8, -1.2])
hide("me", "L63")
put("me", "L64", [44.8, -7.8], yaw=70, expr="smirk")
walk("me", "L64+1.2", [47.5, -6.8], expr="smirk")
key("me", "L64+1.2", yaw=-150)
put("me", "L65", [47.6, -7.0], yaw=-130, expr="neutral", head=[0, 22])
put("me", "L68", [BENCH[0] + 0.5, BENCH[1], -SEAT + 0.45], yaw=0, sit=True, expr="smirk")
put("me", "L69.2", [BENCH[0] + 0.5, BENCH[1], -SEAT + 0.45], yaw=0, sit=True, expr="grin")
put("me", "L70", [38.5, -7.2], yaw=-90, expr="grin")
walk("me", "L70.2", [34.0, -7.2], expr="grin")
walk("me", "L71", [30.0, -7.2], expr="grin")
put("me", "L71.1", [CHAIR_B[0], CHAIR_B[1], DECK + 0.4 - SEAT], yaw=0, sit=True, arms=[0, 0], expr="grin")
hide("me", "L72")
put("me", "L73", [3.0, -6.8], yaw=90, expr="grin")
walk("me", "L73+2.6", [8.0, -6.8], expr="grin")
put("me", "L74", [-0.2, -1.25], yaw=0, expr="grin")
hide("me", "L75")

put("remi", "L10", [-1.4, -1.0], yaw=0, expr=SMILE, arms=[0, 0])
put("remi", "L11", [1.0, -0.55], yaw=180, arms=[88, 0], expr=SMILE)
hide("remi", "L12")
put("remi", "L14", [1.75, -0.55], yaw=-90, arms=[0, 90], expr="neutral")
key("remi", "L14+0.4", arms=[0, 82], blend=0.3)
key("remi", "L14+0.8", arms=[0, 92], blend=0.3)
hide("remi", "L15")
put("remi", "L18.2", [1.0, -0.8], yaw=150, expr=SMILE, head=[-60, 0])
put("remi", "L19", [-1.4, -1.0], yaw=0, expr="worried", arms=[115, 0], head=[0, 8])
hide("remi", "L20")
put("remi", "L22.2", [0.45, -0.55, 0.36], yaw=52, expr="worried", head=[-25, 0])
hide("remi", "L23")
put("remi", "L63", [BENCH[0] - 0.4, BENCH[1], -SEAT + 0.45], yaw=0, sit=True, arms=[60, 60], side=[0, 0], expr=GRIN)
key("remi", "L64", head=[20, 0], expr=SMILE)
key("remi", "L67", head=[0, 0], expr=GRIN)
put("remi", "L70", [39.7, -6.4], yaw=-90, expr=GRIN)
walk("remi", "L70.2", [35.2, -6.4])
talk("remi", "L70", "L70>")
walk("remi", "L71", [31.2, -6.4])
put("remi", "L71.1", [CHAIR_A[0], CHAIR_A[1], DECK + 0.4 - SEAT], yaw=0, sit=True, expr=GRIN)
hide("remi", "L72")
put("remi", "L73", [4.3, -6.4], yaw=90, expr=GRIN)
walk("remi", "L73+2.6", [9.3, -6.4])
put("remi", "L74", [0.4, -1.25], yaw=0, expr=GRIN)
hide("remi", "L75")

# --- the reflections of me and Remi (stage: pos [lateral, depth])
put("r_remi", "L12.1", [0.0, 0.42], yaw=180, look=[0.6, 0.0], expr="neutral")
put("r_remi", "L14", [0.0, 0.12], yaw=180)
walk("r_remi", "L14+1.4", [0.3, 0.36], yaw=180)
put("r_remi", "L15", [0.4, 0.5], yaw=180)
put("r_remi", "L16", [0.2, 0.68], yaw=180)
put("r_remi", "L17", [1.0, 0.88], yaw=180)
put("r_remi", "L18", [0.5, 0.74], yaw=180)
put("r_remi", "L29", [0.5, 0.58], yaw=180)
walk("r_remi", "L29+1.2", [0.5, 0.74], yaw=180)
put("r_remi", "L30", [0.5, 0.8], yaw=180)
walk("r_remi", "L30+1.2", [0.5, 0.86], yaw=180)
put("r_remi", "L32", [0.0, 0.6], yaw=180)
put("r_remi", "L32.2", [1.5, 0.82], yaw=180)
put("r_remi", "L34", [1.5, 0.94], yaw=180)
put("r_remi", "L55", [3.3, 0.86, -0.06], yaw=0, sit=True, expr="neutral")
put("r_remi", "L58", [3.3, 0.86, -0.06], yaw=0, sit=True, expr=SMILE)
hide("r_remi", "L59")
# sand: sitting under the bench (flipped, hers faces mine)
put("r_remi", "L65", [BENCH[0] - 0.45, BENCH[1] + 0.05, -SEAT + 0.45], yaw=90, sit=True, expr=GRIN)
put("r_remi", "L67", [BENCH[0] - 0.45, BENCH[1] + 0.05, -SEAT + 0.45], yaw=90, sit=True, expr=GRIN)
hide("r_remi", "L68")
put("r_remi", "L69", [BENCH[0] - 0.4, BENCH[1], -SEAT + 0.45], yaw=0, sit=True, expr=GRIN)
hide("r_remi", "L69.2")
put("r_remi", "L73", [4.3, -6.4], yaw=90, expr=GRIN)
walk("r_remi", "L73+2.6", [9.3, -6.4])
put("r_remi", "L74", [-1.2, 0.1], yaw=0, expr=GRIN)
hide("r_remi", "L75")

put("r_me", "L17", [-6.5, 0.94], yaw=180)
hide("r_me", "L18")
put("r_me", "L56", [3.8, 0.86, -0.06], yaw=0, sit=True, expr=SMILE)
put("r_me", "L58", [3.8, 0.86, -0.06], yaw=0, sit=True, expr=SMILE)
put("r_me", "L59", [20.0, -8.5], yaw=90)
walk("r_me", "L60", [20.8, -8.5])
hide("r_me", "L61")
put("r_me", "L62", [-1.1, 0.08], yaw=270)
walk("r_me", "L62+1.2", [1.2, 0.08])
put("r_me", "L62.2", [-1.1, 0.08], yaw=270)
walk("r_me", "L62.2+1.3", [1.2, 0.08])
hide("r_me", "L63")
put("r_me", "L65", [BENCH[0] + 0.5, BENCH[1] + 0.05, -SEAT + 0.45], yaw=-90, sit=True, expr=GRIN)
put("r_me", "L67", [BENCH[0] + 0.5, BENCH[1] + 0.05, -SEAT + 0.45], yaw=-90, sit=True, expr=GRIN)
hide("r_me", "L68")
put("r_me", "L69", [BENCH[0] + 0.5, BENCH[1], -SEAT + 0.45], yaw=0, sit=True, expr=GRIN)
hide("r_me", "L69.2")
put("r_me", "L73", [3.0, -6.8], yaw=90, expr=GRIN)
walk("r_me", "L73+2.6", [8.0, -6.8])
put("r_me", "L74", [0.3, 0.1], yaw=0, expr=GRIN)
put("r_me", "L75", [0.3, 0.1], yaw=0, expr=GRIN)
hide("r_me", "L76")
put("r_me", "L76", [13.5, -9.5], yaw=90)
walk("r_me", "end", [19.0, -9.5])

# --- the Small Head. Three held poses, each closer; never moving inside a shot.
SH = CHAIR_B
SH_Z = DECK + 0.4 - SEAT - 0.04
to_me = yaw_to(SH, ME_SIT)
put("smallhead", "L41", [SH[0], SH[1], SH_Z], yaw=-25, sit=True, bow=0, expr="neutral", head=[0, 14])
put("smallhead", "L49", [SH[0], SH[1], SH_Z], yaw=to_me, sit=True, bow=22, head=[0, 18], expr="neutral")
put("smallhead", "L50", [SH[0] - 0.18, SH[1] + 0.12, SH_Z], yaw=to_me, sit=True, bow=45, head=[0, 28], expr="neutral")
put("smallhead", "L51", [SH[0] - 0.42, SH[1] + 0.30, SH_Z], yaw=to_me, sit=True, bow=68, head=[0, 36], expr="neutral")
key("smallhead", "L52.2", bow=68)
key("smallhead", "L53", bow=68)
put("smallhead", "L61.2", [SH[0] - 0.1, SH[1] + 0.08, SH_Z], yaw=yaw_to(SH, (-0.1, -0.4)), sit=True, bow=40, head=[0, 30])
hide("smallhead", "L62")

# ------------------------------------------------------------------------------------------------- cues
cues = [
    {"at": 0, "name": "tod", "set": "day"},
    {"at": "L21", "name": "tod", "set": "grey", "dur": 0.0001},
    {"at": "L24", "name": "tod", "set": "peach", "dur": 3.0},
    {"at": "L34", "name": "tod", "set": "blue", "dur": 3.0},
    {"at": "L62", "name": "tod", "set": "bench", "dur": 0.0001},
    {"at": "L71", "name": "tod", "set": "blue", "dur": 0.0001},
    {"at": "L73", "name": "tod", "set": "gold", "dur": 0.0001},
    {"at": "L76", "name": "tod", "set": "grey", "dur": 0.0001},
    {"at": 0, "name": "chairB", "state": "hidden"},
    {"at": "L12", "name": "chairB", "state": "folded", "pos": [1.15, -0.22, DECK], "yaw": 0},
    {"at": "L21", "name": "chairB", "state": "open", "pos": [CHAIR_B[0], CHAIR_B[1], DECK], "yaw": 0, "sag": 1.0, "dur": 0.2},
    {"at": "L23", "name": "chairB", "state": "open", "pos": [CHAIR_B[0], CHAIR_B[1], DECK], "yaw": 0, "sag": 1.0},
    {"at": "L24", "name": "chairB", "state": "open", "pos": [CHAIR_B[0], CHAIR_B[1], DECK], "yaw": 0, "sag": 0.0, "dur": 0.2},
    {"at": "L37", "name": "chairB", "state": "open", "pos": [CHAIR_B[0], CHAIR_B[1], DECK], "yaw": yaw_to(CHAIR_B, ME_SIT),
     "sag": 0.25},
    {"at": "L39", "name": "chairB", "state": "open", "pos": [CHAIR_B[0], CHAIR_B[1], DECK], "yaw": yaw_to(CHAIR_B, ME_SIT),
     "sag": 0.7, "dur": 0.9},
    {"at": "L41", "name": "chairB", "state": "open", "pos": [CHAIR_B[0], CHAIR_B[1], DECK], "yaw": yaw_to(CHAIR_B, ME_SIT),
     "sag": 0.9, "dur": 0.4},
    {"at": "L62", "name": "chairB", "state": "open", "pos": [CHAIR_B[0], CHAIR_B[1], DECK], "yaw": 0, "sag": 0.0, "dur": 0.3},
    {"at": "L71", "name": "chairB", "state": "open", "pos": [CHAIR_B[0], CHAIR_B[1], DECK], "yaw": 0, "sag": 0.0},
    {"at": "L72", "name": "chairB", "state": "hidden"},
    {"at": "L74", "name": "chairB", "state": "open", "pos": [CHAIR_B[0], CHAIR_B[1], DECK], "yaw": 0, "sag": 0.0},
    {"at": "L24", "name": "scarfprop", "on": True},
    {"at": "L62", "name": "scarfprop", "on": False},
    {"at": "L12", "name": "remi_scarf", "on": True},
    {"at": "L24", "name": "remi_scarf", "on": False},
    {"at": "L71", "name": "remi_scarf", "on": True},
    {"at": "L63", "name": "remi_scarf", "on": False},
    {"at": "L71", "name": "remi_scarf", "on": True},
    # the laptop: open on my knees, shut on the step, shut on the shelf
    {"at": 0, "name": "laptop", "mode": "hide", "open": 1.0},
    {"at": "L09", "name": "laptop", "mode": "show", "pos": [ME_SIT[0], ME_SIT[1] - 0.36, 0.71], "open": 1.0},
    {"at": "L25", "name": "laptop", "mode": "hide"},
    {"at": "L36", "name": "laptop", "mode": "show", "pos": [ME_SIT[0], ME_SIT[1] - 0.36, 0.71], "open": 1.0},
    {"at": "L60", "name": "laptop", "mode": "show", "pos": [ME_SIT[0], ME_SIT[1] - 0.36, 0.71], "open": 0.0, "dur": 0.6},
    {"at": "L61", "name": "laptop", "mode": "show", "pos": [-0.15, -0.2, 0.38], "open": 0.0, "dur": 0.4},
    {"at": "L62", "name": "laptop", "mode": "hide"},
    {"at": "L72", "name": "laptop", "mode": "show", "pos": [-1.3, 1.1, 1.82], "open": 0.0, "yaw": 90},
    {"at": "L73", "name": "laptop", "mode": "hide"},
    {"at": "L76", "name": "laptop", "mode": "show", "pos": [-0.15, -0.2, 0.38], "open": 0.0},
    {"at": "L28", "name": "door", "open": 0.4, "dur": 1.6},
    {"at": "L29", "name": "door", "open": 0.0, "dur": 0.4},
    {"at": "L40", "name": "lantern", "on": 1.0, "dur": 1.2},
    {"at": "L62", "name": "lantern", "on": 0.0, "dur": 0.5},
    {"at": "L71", "name": "lantern", "on": 1.0, "dur": 0.6, "pos": [0.05, -1.65]},
    {"at": "L73", "name": "lantern", "on": 0.0, "dur": 0.5},
    {"at": "L34", "name": "rim", "on": 1.0, "dur": 3.0},
    {"at": "L76", "name": "rim", "on": 0.0, "dur": 0.3},
    {"at": "L23", "name": "hutin", "on": 0.35, "dur": 0.5},
    {"at": "L24", "name": "hutin", "on": 0.0, "dur": 0.6},
    {"at": "L72", "name": "hutin", "on": 1.0, "dur": 0.5},
    {"at": "L73", "name": "hutin", "on": 0.0, "dur": 0.5},
]

sfx = [
    {"at": "L25", "kind": "thud", "db": -6, "dur": 1.2},
    {"at": "L28", "kind": "creak", "db": -16, "dur": 1.4},
    {"at": "L39", "kind": "creak", "db": -14, "dur": 1.2},
    {"at": "L40", "kind": "click", "db": -14},
    {"at": "L43", "kind": "riser", "db": -20, "dur": 1.4},
    {"at": "P02+0.1", "kind": "creak", "db": -12, "dur": 0.7},
    {"at": "L44", "kind": "hit", "db": -9},
    {"at": "L49", "kind": "creak", "db": -18, "dur": 0.8},
    {"at": "L50", "kind": "creak", "db": -17, "dur": 0.8},
    {"at": "L51", "kind": "creak", "db": -16, "dur": 0.8},
    {"at": "L60", "kind": "click", "db": -14},
    {"at": "L76>", "kind": "sting", "db": -18, "dur": 0.35},
]

story = {
    "slug": "ep50-beach-huts",
    "title": "In this town, your reflection does what you really want to do",
    "made_for_kids": False,
    "premise": ("In a town where every reflection does what its owner really wants, the narrator has no reflection at all and "
                "takes it to mean he wants nothing. His fiancee Remi is getting their beach hut ready for summer while he "
                "stays in the doorway on his laptop, and her reflection in the hut window walks a little further down the "
                "shore each day."),
    "twist": ("Remi's reflection was following his. His own reflection was never missing: what he really wants is to walk "
              "the shore with her, so it had been out there doing it all along, where he never looked. The rule that seemed "
              "to show she wanted to leave means they both wanted the same walk."),
    "world": ("a row of twelve faded pastel beach huts on a windy off-season shore, glossy wet sand that mirrors, a breakwater "
              "and a bench at the point, and a second deckchair that is set out every morning"),
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#7fe3c8",
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#b4c2c8", "fog_density": 0.022, "fog_start": 12.0, "sky": "#c9d3d6", "sky_strength": 1.05,
             "exposure": 0.0, "flash_safe": True},
    "grade": {"shadows": [-0.02, 0.0, 0.05], "highlights": [0.02, 0.01, -0.02], "saturation": 0.95, "contrast": 1.06,
              "vignette": 0.34, "bloom": 0.3, "grain": 0.012},
    "phonemes": {"Remi": "ɹˈɛmi"},
    "cast": cast,
    "reflections": reflections,
    "lines": lines,
    "shots": shots,
    "shotx": shotx,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 43, "mode": "dorian", "bpm": 76, "seed": 50,
              "sections": [
                  {"at": 0, "voices": ["pulse", "pad"], "energy": 0.22},
                  {"at": "L10", "voices": ["pulse", "pad"], "energy": 0.28},
                  {"at": "L24", "voices": ["pad"], "energy": 0.2},
                  {"at": "L25", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L37", "voices": ["drone", "pad", "choir"], "energy": 0.5},
                  {"at": "L44", "voices": ["drone", "choir"], "energy": 0.55},
                  {"at": "L57", "voices": ["drone", "pad", "choir"], "energy": 0.5},
                  {"at": "L62", "voices": ["drone", "pad"], "energy": 0.45},
                  {"at": "L66", "voices": ["drone", "pad", "piano"], "energy": 0.5, "mode": "major"},
                  {"at": "L74", "voices": ["drone"], "energy": 0.4},
              ]},
    "sound": {"floor": "grass", "steps_db": -22,
              "ambience": [
                  {"kind": "wind", "from": 0, "to": "end", "lufs": -30},
                  {"kind": "water", "from": 0, "to": "end", "lufs": -38},
                  {"kind": "drone", "from": "L25", "to": "end", "lufs": -26},
                  {"kind": "hum", "from": "L23", "to": "L24", "lufs": -42},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "L25", "keep": ["thud"]},
                              {"from": "P02", "to": "L44", "keep": ["creak"]}]},
}
for keys in acting.values():
    for k in keys:
        for f in ("at", "from", "to"):
            if f in k:
                k[f] = R(k[f])
for k in cues + sfx:
    k["at"] = R(k["at"])
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
