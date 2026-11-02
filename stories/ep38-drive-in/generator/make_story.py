"""Writes ../story.json for ep38 "In this town, a silhouette over your head shows who you miss".

Run from anywhere: python stories/ep38-drive-in/generator/make_story.py
The words are in lines.json next to this file (L01 to L65, from script.md). The pause beats, the cast, the shots, the
acting, the cues, the score and the sound are here. Every light change in this film is a slow fade (look.flash_safe):
the beam, the screen, the reel running out, the ring filling back in. Nothing strobes.

Coordinates (metres): the lot's rows run along y (row 1 at y = 0, the screen at y = +48, the booth at y = -56), cars
face +y, the aisle with the beam is x = 0. Theo's cream car is row 1 at x = 3.4; my teal car is row 4 (y = -21) at
x = 3.4. Seated people face +y (yaw 180). The montage vignettes stand far off at x = 300, 400, 500, 600, 700.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
base = json.loads((HERE / "lines.json").read_text())

# ---- pause beats (silent, about 0.6 s): after these lines, plus the music drop before L47 and the tally hold
PAUSES = {"L18": 0.6, "L22": 0.6, "L27": 0.6, "L35": 0.6, "L41": 0.6, "L46": 0.6, "L50": 0.6, "L59": 0.6, "L62": 0.9}
lines = []
for ln in base:
    lines.append(ln)
    if ln["id"] in PAUSES:
        lines.append({"id": "P" + ln["id"][1:], "pause": PAUSES[ln["id"]], "chunks": []})
CH = {ln["id"]: [c[0] for c in ln["chunks"]] for ln in base}


def A(lid, prefix):
    """The reference to the chunk of a line that starts with a given text."""
    for i, c in enumerate(CH[lid]):
        if c.lower().startswith(prefix.lower()):
            return f"{lid}.{i}"
    raise SystemExit(f"{lid} has no chunk starting {prefix!r}: {CH[lid]}")


# ---- places
SEAT_Z = 0.04            # root z of someone seated on a car's bench (cushion top 0.55)
CHAIR_Z = 0.11           # root z on a stool or chair (seat top 0.62)
SEAT_Y = -0.32           # root y on the bench, from the car's centre
THEO = (3.4, 0.0)        # Theo's cream car (row 1)
ME = (3.4, -21.0)        # my teal car (row 4)


def seat(car, side, z=SEAT_Z, **kw):
    """A bench place: side -1 is the driver (left), +1 the passenger."""
    x = car[0] + side * 0.95
    return {"pos": [round(x, 2), round(car[1] + SEAT_Y, 2), z], "yaw": 180, "sit": True, **kw}


def key(at, **kw):
    return {"at": at, **kw}


def jump(at, pos, **kw):
    """A cut-away move: the same moment, so nobody walks on film (a copy of the old place is added before it)."""
    return {"at": at, "pos": pos, "blend": 0.0, "_j": True, **kw}


def stand(at, x, y, yaw=0, **kw):
    return {"at": at, "pos": [x, y, 0.0], "yaw": yaw, "sit": False, "arms": [0, 0], **kw}


# ---- cast (adults; one narrator voice reads everything)
def person(skin, shirt, pants, hair, hair_c, pattern="solid", pattern_c=None, collar=None, shoes="#2a2220",
           sleeves="long", hat="none", hat_c=None, extras=None, extra_c=None, face=None, **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "collar": collar, "pants": pants,
         "shoes": shoes, "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat,
         "face": face or {"eyes": "round", "brows": True}}
    if pattern_c:
        d["pattern_c"] = pattern_c
    if hat_c:
        d["hat_c"] = hat_c
    if extras:
        d["extras"] = extras
        d["extra_c"] = extra_c or "#20242c"
    d.update(kw)
    return d


cast = {
    "me": person("#e3ad84", "#c9a23a", "#2a2f3d", "cap", "#3a2416", pattern="knit", pattern_c="#a9822a",
                 collar="#f0ece4", shoes="#1c1c20", hat="ballcap", hat_c="#a6402f",
                 face={"eyes": "round", "brows": True}),
    "theo": person("#d9a67c", "#2f5d3f", "#34373d", "cap", "#b58a56", pattern="plaid", pattern_c="#1c3a27",
                   collar="#8c9096", shoes="#2a2420", face={"eyes": "classic", "brows": True, "ink": "#1a1210"}),
    "dev": person("#c98e66", "#3d5a80", "#2d2f36", "swoop", "#1d1410", pattern="stripes", pattern_c="#e6e9ef",
                  collar="#e6e9ef", face={"eyes": "round", "brows": True}),
    "mate1": person("#f0c9a6", "#7a3b32", "#33363c", "buzz", "#4a3220", sleeves="short",
                    face={"eyes": "classic", "brows": True, "ink": "#1a1210"}),
    "mate2": person("#8a5636", "#d0c9b8", "#2c3140", "spiky", "#1a1410", pattern="stripes", pattern_c="#b9b09a",
                    face={"eyes": "round", "brows": True}),
    "sailor": person("#e7b896", "#1d2a44", "#1d2a44", "buzz", "#6b4a2a", hat="beanie", hat_c="#18223a",
                     extras=["coat"], extra_c="#1b2742", collar="#9aa4b4", shoes="#17171a",
                     face={"eyes": "tired", "brows": True}),
    "cafe_woman": person("#efc6a2", "#8a3a4a", "#2f3340", "bun", "#33241c", pattern="knit", pattern_c="#6e2a38",
                         face={"eyes": "lashes", "brows": True}),
    "cafe_date": person("#d8a27a", "#4b5e7a", "#2d3038", "swoop", "#201812", collar="#e8e8ec",
                        face={"eyes": "round", "brows": True}),
    "sofa_woman": person("#e9b994", "#6b7f5a", "#3a3f4a", "long", "#5a3622", pattern="knit", pattern_c="#566848",
                         shoes="#2a2220", face={"eyes": "lashes", "brows": True}),
    "bg1": person("#f1c7a2", "#9a4a3a", "#2e3340", "long", "#7a4a2a", pattern="stripes", pattern_c="#e8dcc0",
                  face={"eyes": "lashes", "brows": True}),
    "bg2": person("#c8946a", "#3b7d7a", "#2c2f38", "spiky", "#1c140e", face={"eyes": "round", "brows": True}),
    "bg3": person("#e0ac86", "#e8dcc0", "#3a3a40", "bun", "#2a1c14", face={"eyes": "round", "brows": True}),
    "bg4": person("#a56a46", "#7a5a3a", "#2f323a", "buzz", "#161210", pattern="plaid", pattern_c="#c9a96a",
                  face={"eyes": "classic", "brows": True, "ink": "#1a1210"}),
    "bg5": person("#f0d0b0", "#4a3b5a", "#33363c", "swoop", "#8a5a2a", face={"eyes": "round", "brows": True}),
    "bg6": person("#7b4a30", "#c9784a", "#2a2d35", "long", "#150f0c", pattern="knit", pattern_c="#a85f38",
                  face={"eyes": "lashes", "brows": True}),
    # the Unlit: an ordinary R6 person, a whole head too tall (about 2.4 m), every surface a matte black that no
    # light lands on. set.py gives it the thin cool rim and the two glints; it has no silhouette and no ring.
    "unlit": {"age": "adult", "skin": "#050506", "shirt": "#060607", "pattern": "solid", "collar": None,
              "pants": "#040405", "shoes": "#030304", "sleeves": "long", "hair": "none", "hat": "none",
              "height": 1.36, "width": 0.86, "face": {"eyes": "none", "mouth": "none", "brows": False}},
}

# ================================================================================================ acting
HID = {"hidden": True}


def _hide(name_keys, until, then, **kw):
    return name_keys


acting = {}

# ---- me. The cap is on my head except in the office (S14) and in my car on the first Friday (S19): set.py hides it
acting["me"] = [
    stand(0, 0.55, -21.9, yaw=22, hidden=True),                                         # the hook starts without me
    jump("S09", [0.55, -21.9, 0.0], yaw=22, hidden=False, expr="neutral", sit=False, arms=[0, 0]),
    key("S10", expr="smirk", head=[-20, 4]),
    jump("S11", [700.0, 0.55, CHAIR_Z], yaw=0, hidden=True),
    jump("S14", [700.6, 0.55, CHAIR_Z], yaw=20, hidden=False, sit=True, expr="neutral", head=[-10, 0], arms=[34, 34]),
    jump("S15", [700.6, 0.55, CHAIR_Z], hidden=True),
    jump("S19", seat(ME, -1)["pos"], yaw=180, sit=True, hidden=False, expr="worried", head=[0, 0], arms=[60, 60]),
    key("S25", expr="wide"),
    key("S26", expr="worried"),
    key("S28", head=[40, 0]),
    key("S34", head=[0, 0]),
    key("S46", expr="scared", tremble=1.2),
    key("S48", expr="scared"),
    jump("S50", seat(ME, -1)["pos"], yaw=180, sit=True, expr="scared", tremble=0.0, arms=[60, 60]),
    jump("S51", [0.0, -21.0, 0.0], yaw=180, sit=False, arms=[0, 0], expr="worried", head=[0, 0], hidden=False),
    {"at": "S51+1.4", "pos": [0.0, -17.6, 0.0], "yaw": 180},
    jump("S56", [0.0, -19.0, 0.0], yaw=180, sit=False, expr="wide", head=[0, -28], look=[0, 0.5]),
    jump("S57", [0.0, -19.0, 0.0], yaw=180, head=[0, 0], look=[0, 0]),
    jump("S58", [0.0, -19.0, 0.0], yaw=180),
    key("S62", expr="wide"),
    jump("S66", [-0.8, -19.0, 0.0], yaw=58, expr="soft", head=[0, 0], look=[0, 0]),
    jump("S67", [-0.8, -19.0, 0.0], yaw=58, hidden=True),
    jump("S68", seat(THEO, 1)["pos"], yaw=180, sit=True, hidden=False, expr="soft", arms=[60, 60]),
    jump("S72", seat(THEO, 1)["pos"], yaw=180, sit=True, expr="soft"),
    jump("S73", seat(THEO, 1)["pos"], yaw=180, sit=True, expr="soft"),
]
# ---- Theo, in the driver's seat of the cream car
acting["theo"] = [
    {"at": 0, "pos": [800.0, 0.0, 0.0], "yaw": 0, "hidden": True},
    jump("S11", seat(THEO, -1)["pos"], yaw=180, sit=True, hidden=False, expr="neutral", arms=[60, 60], head=[0, 0]),
    jump("S13", seat(THEO, -1)["pos"], yaw=180, expr="soft"),
    jump("S15", seat(THEO, -1)["pos"], yaw=180, expr="neutral"),
    key("S17", expr="worried", head=[0, 6]),
    key("S22", expr="blank", head=[0, 0]),
    key("S27", expr="blank"),
    key("S35", expr="blank"),
    key("S41", head=[-75, 0]),
    key("S43", head=[0, 0]),
    key("S44", head=[0, 0]),
    key("S45", expr="blank"),
    key("S59", head=[0, -22], expr="wide"),
    jump("S61", seat(THEO, -1)["pos"], yaw=180, sit=True, head=[0, -22]),
    jump("S62", [1.0, -22.5, 0.0], yaw=180, sit=False, arms=[0, 0], head=[0, -8], expr="soft"),
    {"at": "S62+1.0", "pos": [0.85, -19.4, 0.0], "yaw": 180},
    jump("S63", [0.85, -19.4, 0.0], yaw=180, head=[0, 0]),
    jump("S66", [0.85, -19.0, 0.0], yaw=-58, expr="soft"),
    jump("S67", [0.85, -19.0, 0.0], hidden=True),
    jump("S68", seat(THEO, -1)["pos"], yaw=180, sit=True, hidden=False, expr="soft", arms=[60, 60], head=[0, 0]),
    jump("S69", seat(THEO, -1)["pos"], yaw=180, head=[0, -10], look=[0, 0.2], expr="neutral"),
    jump("S72", seat(THEO, -1)["pos"], yaw=180, expr="soft", head=[0, 0]),
]
# ---- the montage and the office
acting["dev"] = [
    {"at": 0, "pos": [800.0, 0.0, 0.0], "hidden": True},
    jump("S04", [300.0, 0.15, CHAIR_Z], yaw=0, sit=True, hidden=False, expr="grin", arms=[34, 34], head=[0, 0]),
    jump("S05", [300.0, 0.15, CHAIR_Z], hidden=True),
]
acting["mate1"] = [
    {"at": 0, "pos": [800.0, 0.0, 0.0], "hidden": True},
    jump("S04", [298.85, 0.25, CHAIR_Z], yaw=15, sit=True, hidden=False, expr="neutral", arms=[34, 34]),
    jump("S05", [299.25, 0.4, 0.0], yaw=10, sit=False, expr="angry", arms=[0, 0], head=[-8, -26], look=[0, 0.6]),
    jump("S06", [299.25, 0.4, 0.0], hidden=True),
]
acting["mate2"] = [
    {"at": 0, "pos": [800.0, 0.0, 0.0], "hidden": True},
    jump("S04", [301.15, 0.25, CHAIR_Z], yaw=-15, sit=True, hidden=False, expr="neutral", arms=[34, 34]),
    jump("S05", [300.75, 0.4, 0.0], yaw=-10, sit=False, expr="angry", arms=[0, 0], head=[8, -26], look=[0, 0.6]),
    jump("S06", [300.75, 0.4, 0.0], hidden=True),
]
acting["sailor"] = [
    {"at": 0, "pos": [800.0, 0.0, 0.0], "hidden": True},
    jump("S06", [400.0, -0.3, 0.0], yaw=0, hidden=False, sit=False, expr="soft", arms=[0, 0], head=[0, 0]),
    jump("S07", [400.0, -0.3, 0.0], hidden=True),
]
acting["cafe_woman"] = [
    {"at": 0, "pos": [800.0, 0.0, 0.0], "hidden": True},
    jump("S07", [499.35, 0.1, CHAIR_Z], yaw=48, sit=True, hidden=False, expr="neutral", arms=[34, 34], head=[0, 0]),
    jump("S08", [499.35, 0.1, CHAIR_Z], hidden=True),
]
acting["cafe_date"] = [
    {"at": 0, "pos": [800.0, 0.0, 0.0], "hidden": True},
    jump("S07", [500.65, 0.1, CHAIR_Z], yaw=-48, sit=True, hidden=False, expr="neutral", arms=[34, 34], head=[10, 0]),
    key("S07+0.9", head=[-6, -14], look=[-0.4, 0.8], expr="wide"),
    jump("S08", [500.65, 0.1, CHAIR_Z], hidden=True),
]
acting["sofa_woman"] = [
    {"at": 0, "pos": [800.0, 0.0, 0.0], "hidden": True},
    jump("S08", [600.0, 0.4, CHAIR_Z + 0.02], yaw=8, sit=True, hidden=False, expr="soft", arms=[40, 40], head=[0, 0]),
    jump("S09", [600.0, 0.4, CHAIR_Z], hidden=True),
]
# the couples at the lot: standing beside the cream car in the golden hour, then in their cars for the night
acting["bg1"] = [
    stand(0, -1.15, -6.45, yaw=90, expr="grin", head=[10, 0]),
    jump("S09", [800.0, 0.0, 0.0], hidden=True),
    jump("S14", seat((-3.4, 0.0), -1)["pos"], yaw=180, sit=True, hidden=False, expr="neutral", arms=[60, 60]),
    key("S60", head=[0, -22], expr="wide"),
]
acting["bg2"] = [
    stand(0, -1.15, -7.9, yaw=90, expr="grin", head=[-10, 0]),
    jump("S09", [800.0, 0.0, 0.0], hidden=True),
    jump("S14", seat((-3.4, 0.0), 1)["pos"], yaw=180, sit=True, hidden=False, expr="neutral", arms=[60, 60]),
    key("S60", head=[0, -22], expr="wide"),
]
acting["bg3"] = [
    stand(0, -6.2, -13.2, yaw=90, expr="neutral", head=[0, 0]),
    jump("S09", seat((-8.4, -14.0), -1)["pos"], yaw=180, sit=True, expr="neutral", arms=[60, 60]),
    key("S60", head=[0, -22], expr="wide"),
]
acting["bg4"] = [
    stand(0, -6.2, -14.8, yaw=90, expr="smirk"),
    jump("S09", seat((-8.4, -14.0), 1)["pos"], yaw=180, sit=True, expr="neutral", arms=[60, 60]),
    key("S60", head=[0, -22], expr="wide"),
]
acting["bg5"] = [
    jump(0, seat((-8.4, -7.0), -1)["pos"], yaw=180, sit=True, expr="neutral", arms=[60, 60], head=[0, 0]),
    key("S60", head=[0, -22], expr="wide"),
]
acting["bg6"] = [
    jump(0, seat((-8.4, -7.0), 1)["pos"], yaw=180, sit=True, expr="neutral", arms=[60, 60], head=[0, 0]),
    key("S60", head=[0, -22], expr="wide"),
]
# ---- the Unlit. Hidden until Friday 1, in a new place each Friday, never seen moving: every move is on a cut
UN = "unlit"
SU = seat(THEO, 1, z=-0.28)["pos"]
acting[UN] = [
    {"at": 0, "pos": [800.0, 0.0, 0.0], "hidden": True},
    # Friday 1: at the very back, behind row 7, by the booth, facing the screen (head turned toward the lot for S24)
    jump("S23", [8.4, -47.5, 0.0], yaw=180, hidden=False, sit=False, arms=[0, 0], head=[0, 0], expr="blank"),
    key("S24", head=[175, 0], blend=0.0),
    jump("S27", [8.4, -47.5, 0.0], hidden=True),
    # Friday 2: in the aisle of row 4, in the beam, facing the screen
    jump("S28", [0.1, -22.4, 0.0], yaw=180, hidden=False, head=[-30, 0]),
    jump("S32", [0.1, -22.4, 0.0], hidden=True),
    # Friday 3: beside Theo's car, facing his passenger door, then its head turned back at my car
    jump("S32", [6.8, 0.0, 0.0], yaw=-90, hidden=False, head=[0, 0]),
    key("S34", head=[40, 0], blend=0.0),
    jump("S35", [6.8, 0.0, 0.0], hidden=True),
    # the scare: in Theo's passenger seat, head bent against the roof lining, glints turned back at me
    jump("S40", SU, yaw=180, sit=True, hidden=False, arms=[34, 34], head=[158, 44], lean=14),
    key("S41", head=[0, 38], blend=0.0),
    key("S42", head=[0, 32], blend=0.0),
    key("S43", head=[158, 44], blend=0.0),
    key("S44", head=[0, 38], blend=0.0),
    key("S45", head=[158, 44], blend=0.0),
    jump("S67", SU, hidden=True),
]

# ================================================================================================ shots


def C(frm, tgt, lens, frm2=None, tgt2=None, lens2=None):
    ks = [[0, list(frm), list(tgt), lens]]
    if frm2 is not None:
        ks.append([1, list(frm2), list(tgt2 if tgt2 is not None else tgt), lens2 or lens])
    return ks


ARENA = ((-1.0, -44.0, 3.2), (0.0, -4.0, 2.0), 24)
SCREEN_CAM = ((0.0, -8.0, 2.0), (0.0, 48.0, 8.5), 26)
THEO_RING = ((3.2, -3.6, 2.2), (2.45, -0.3, 2.35), 40)
THEO_REAR = ((3.4, -17.0, 1.8), (3.4, -0.3, 1.45), 80)
SHADOW_WIDE = ((0.0, -4.0, 3.5), (0.0, 48.0, 11.0), 28)

# (id, anchor, cam keys, options). options: step, hand
SH = [
    ("S01", 0, C((2.9, -7.15, 1.6), (-1.15, -7.15, 1.75), 24, (2.8, -7.15, 1.62), (-1.15, -7.15, 1.75), 26), {"hand": 0.006}),
    ("S02", A("L01", "over your"), C(*ARENA, (-1.0, -40.0, 3.0), (0.0, -4.0, 2.0), 26), {}),
    ("S03", "L02", C((2.4, -7.9, 2.5), (-1.15, -7.9, 2.5), 50, (2.2, -7.9, 2.5), (-1.15, -7.9, 2.5), 56), {"step": 1}),
    ("S04", "L03", C((300.0, -4.0, 1.7), (300.0, 0.15, 1.65), 30, (300.0, -3.7, 1.7), (300.0, 0.15, 1.65), 32), {}),
    ("S05", A("L03", "and his mates"), C((300.0, -3.3, 1.9), (300.0, 0.4, 2.0), 22, (300.0, -3.1, 1.9), (300.0, 0.4, 2.0), 23), {"hand": 0.01}),
    ("S06", "L04", C((400.4, -4.4, 1.5), (400.4, -0.3, 1.8), 26, (400.4, -4.1, 1.55), (400.4, -0.3, 1.8), 28), {}),
    ("S07", "L05", C((500.0, -3.6, 1.6), (500.0, 0.1, 1.8), 26, (500.0, -3.4, 1.6), (500.0, 0.1, 1.8), 27), {}),
    ("S08", "L06", C((599.9, -2.3, 1.2), (599.5, -0.6, 1.1), 30, (599.8, -2.0, 1.2), (599.5, -0.6, 1.1), 32), {}),
    ("S09", "L07", C((1.7, -25.8, 1.6), (0.55, -21.9, 1.95), 34, (1.1, -24.8, 1.7), (0.55, -21.9, 2.3), 32), {}),
    ("S10", "L08", C((1.0, -24.4, 1.9), (0.55, -21.9, 1.9), 52), {"step": 1, "hand": 0.006}),
    ("S11", "L09", C((4.9, 3.6, 2.0), (2.45, -0.3, 1.45), 34, (4.7, 3.2, 2.0), (2.45, -0.3, 1.45), 36), {}),
    ("S12", "L10", C((2.45, -3.4, 2.5), (2.45, -0.3, 2.1), 40), {"hand": 0.004}),
    ("S13", "L11", C((3.4, 4.3, 1.9), (3.4, -0.3, 1.45), 24, (3.4, 4.0, 1.9), (3.4, -0.3, 1.45), 25), {}),
    ("S14", "L12", C((701.6, -2.4, 1.8), (699.9, 1.4, 1.95), 28, (701.4, -2.2, 1.8), (699.9, 1.4, 1.95), 30), {}),
    ("S15", "L13", C((0.2, -7.0, 1.7), (3.4, 0.0, 2.0), 28, (0.9, -6.2, 1.7), (3.4, 0.0, 2.0), 30), {}),
    ("S16", "L14", C(*THEO_RING), {"hand": 0.004}),
    ("S17", "L15", C(*THEO_RING), {"hand": 0.004}),
    ("S18", "L16", C((8.4, -16.0, 1.2), (3.4, -23.0, 1.0), 30, (7.6, -15.4, 1.2), (3.4, -21.5, 1.0), 30), {}),
    ("S19", A("L16", "parked"), C((2.45, -19.4, 1.7), (2.45, -21.32, 1.8), 40, (2.45, -19.6, 1.7), (2.45, -21.32, 1.8), 42), {}),
    ("S20", "L17", C((-4.0, -47.0, 2.2), (0.0, 10.0, 5.0), 24, (-3.0, -46.0, 2.4), (0.0, 12.0, 5.5), 24), {}),
    ("S21", A("L17", "and the screen"), C((0.0, -12.0, 2.5), (0.0, 48.0, 9.0), 22, (0.0, -6.0, 2.5), (0.0, 48.0, 9.0), 24), {}),
    ("S22", "L18", C((2.9, -1.6, 2.05), (2.45, -0.3, 2.5), 32, (2.85, -1.45, 2.05), (2.45, -0.3, 2.5), 34), {}),
    ("S23", "L19", C((2.45, -21.5, 2.6), (8.4, -47.5, 2.0), 44, (2.45, -21.5, 2.6), (8.4, -47.5, 2.0), 52), {}),
    ("S24", "L20", C((2.4, -37.5, 2.0), (8.4, -47.5, 2.0), 40, (2.6, -36.8, 2.0), (8.4, -47.5, 2.0), 42), {}),
    ("S25", "L21", C((2.45, -19.6, 1.7), (2.45, -21.32, 1.8), 42), {"hand": 0.006}),
    ("S26", "L22", C((2.6, -39.0, 1.9), (8.4, -47.5, 2.7), 50), {"hand": 0.004}),
    ("S27", "L23", C(*THEO_RING), {"hand": 0.004}),
    ("S28", "L24", C((3.2, -31.0, 1.9), (0.1, -22.4, 2.3), 30, (3.2, -30.6, 1.9), (0.1, -22.4, 2.3), 32), {}),
    ("S29", "L25", C((-7.0, -22.4, 1.9), (0.0, -22.0, 2.2), 26), {}),
    ("S30", "L26", C(*SCREEN_CAM), {}),
    ("S31", "L27", C((1.0, -18.8, 0.6), (0.1, -22.4, 1.9), 28, (0.8, -19.0, 0.6), (0.1, -22.4, 1.9), 30), {}),
    ("S32", "L28", C((2.4, -11.5, 2.0), (6.8, 0.0, 2.2), 30), {}),
    ("S33", "L29", C((3.0, -8.0, 2.0), (6.8, 0.0, 2.2), 34, (3.2, -7.0, 2.0), (6.8, 0.0, 2.2), 38), {}),
    ("S34", "L30", C((5.2, -8.0, 1.9), (6.8, 0.0, 2.2), 46), {}),
    ("S35", "L31", C(*THEO_RING), {"hand": 0.004}),
    ("S36", "L32", C(*SCREEN_CAM), {}),
    ("S37", "L33", C(*ARENA), {}),
    ("S38", "L34", C((0.4, -20.2, 1.4), (1.55, -20.8, 1.15), 46), {"step": 1, "hand": 0.004}),
    ("S39", "L35", C((-4.0, -47.0, 2.2), (0.0, 10.0, 5.0), 24, (-3.0, -46.0, 2.4), (0.0, 12.0, 5.5), 24), {}),
    ("S40", "L36", C(*THEO_REAR), {"step": 1}),
    ("S41", "L37", C((3.4, 2.4, 1.7), (3.4, -0.3, 1.8), 26, (3.4, 2.2, 1.7), (3.4, -0.3, 1.8), 27), {"step": 1}),
    ("S42", "L38", C((3.2, 2.9, 1.8), (4.1, -0.5, 1.55), 30, (3.2, 2.7, 1.8), (4.1, -0.5, 1.55), 32), {}),
    ("S43", "L39", C((3.4, -17.0, 1.8), (3.4, -0.3, 1.5), 75, (3.4, -13.0, 1.8), (3.4, -0.3, 1.5), 95), {"step": 1}),
    ("S44", "L40", C((3.4, 4.4, 1.9), (3.4, -0.3, 1.85), 24, (3.4, 4.0, 1.9), (3.4, -0.3, 1.85), 25), {}),
    ("S45", "L41", C(*THEO_RING), {"hand": 0.003}),
    ("S46", "L42", C((2.45, -19.0, 1.6), (2.45, -21.32, 1.45), 30), {"step": 1}),
    ("S47", "L43", C((2.45, -18.2, 2.6), (2.45, -21.32, 2.55), 42, (2.45, -18.6, 2.6), (2.45, -21.32, 2.55), 46), {}),
    ("S48", "L44", C((3.4, -4.0, 2.4), (3.4, -21.0, 2.6), 50), {}),
    ("S49", "L45", C((0.0, -47.0, 3.5), (0.0, 30.0, 6.0), 24), {}),
    ("S50", "L46", C((-2.6, -23.4, 1.6), (1.3, -21.0, 1.3), 32), {"step": 1}),
    ("S51", A("L46", "and walked"), C((0.0, -13.0, 1.6), (0.0, -19.0, 1.5), 30, (0.0, -12.0, 1.6), (0.0, -18.0, 1.55), 30), {"step": 1}),
    ("S52", "L47", C((0.0, -8.0, 1.6), (0.0, 48.0, 8.0), 22), {}),
    ("S53", "L48", C((0.0, -8.0, 2.0), (0.0, 48.0, 4.0), 22, (0.0, -8.0, 2.0), (0.0, 48.0, 12.5), 22), {}),
    ("S54", A("L48", "in a ring"), C(*SHADOW_WIDE, (0.0, -2.0, 3.2), (0.0, 48.0, 11.0), 30), {}),
    ("S55", "L49", C((0.0, 22.0, 12.0), (0.0, 48.0, 13.0), 40, (0.0, 26.0, 12.5), (0.0, 48.0, 13.2), 44), {}),
    ("S56", "L50", C((0.3, -14.5, 1.45), (0.0, -19.0, 1.85), 30), {"step": 1}),
    ("S57", "L51", C((0.0, -22.4, 1.95), (0.0, -19.0, 1.9), 55), {}),
    ("S58", "L52", C((0.0, -22.5, 1.7), (1.2, 12.0, 6.5), 22), {}),
    ("S59", "L53", C(*THEO_REAR), {}),
    ("S60", "L54", C((-3.4, 6.4, 2.5), (-3.4, -0.3, 1.9), 46), {}),
    ("S61", "L55", C((-3.2, -4.8, 2.3), (1.3, -0.5, 1.3), 30), {"step": 1}),
    ("S62", "L56", C((-0.3, -26.0, 1.9), (0.8, -20.0, 1.85), 30), {"step": 1}),
    ("S63", "L57", C((0.85, -15.6, 2.4), (0.85, -19.4, 2.4), 38), {"step": 1}),
    ("S64", "L58", C(*SHADOW_WIDE), {}),
    ("S65", "L59", C(*SHADOW_WIDE, (0.0, -2.0, 3.2), (0.0, 48.0, 11.0), 30), {}),
    ("S66", A("L59", "we turned"), C((0.0, -24.0, 1.7), (0.0, -19.0, 1.8), 34, (0.0, -23.4, 1.7), (0.0, -19.0, 1.8), 36), {}),
    ("S67", "L60", C((7.6, -0.3, 1.6), (4.35, -0.3, 1.0), 35), {}),
    ("S68", "L61", C((3.4, 4.2, 1.9), (3.4, -0.3, 1.45), 24), {}),
    ("S69", "L62", C((3.5, 2.4, 1.8), (3.6, -0.1, 0.8), 26), {"step": 1}),
    ("S70", A("L62", "like he"), C((-0.7, -1.2, 1.45), (1.45, 0.2, 1.15), 55), {"step": 1}),
    ("S71", "L63", C((700.0, -2.8, 1.9), (699.0, 2.4, 1.7), 30), {}),
    ("S72", "L64", C((3.4, 4.2, 1.95), (3.4, -0.3, 2.0), 20), {}),
    ("S73", "L65", C((4.35, 3.5, 2.5), (4.35, -0.3, 2.55), 45), {"hand": 0.004}),
]
shots = []
for i, (sid, at, cam, opt) in enumerate(SH):
    s = {"id": sid, "cam": cam, "step": opt.get("step", 2)}
    if i:
        s["at"] = at
    if "hand" in opt:
        s["hand"] = opt["hand"]
    shots.append(s)
SHOT_AT = {s[0]: s[1] for s in SH}


def _resolve(ref):
    """Acting anchors written as "S09" or "S51+1.4" mean the shot's own start."""
    if isinstance(ref, str) and ref.startswith("S") and ref[1:3].isdigit():
        sid, _, off = ref.partition("+")
        at = SHOT_AT[sid]
        if sid == "S01":
            return float(off or 0)
        return f"{at}+{off}" if off else at
    return ref


ORDER = {s[0]: i for i, s in enumerate(SH)}


def _order(k):
    a = k["at"]
    if isinstance(a, (int, float)):
        return (-1, float(a))
    sid, _, off = a.partition("+")
    return (ORDER[sid], float(off or 0))


for who, ks in acting.items():
    ks.sort(key=_order)                       # stable: keys at the same anchor keep their order
    out = []
    last = None
    for k in ks:
        k = dict(k)
        j = k.pop("_j", False)
        if j and last is not None:
            out.append({"at": k["at"], "pos": last, "blend": 0.0})
        if "pos" in k:
            last = k["pos"]
        out.append(k)
    for k in out:
        k["at"] = _resolve(k["at"])
    acting[who] = out

# ================================================================================================ cues
SHOT_T = lambda sid: SHOT_AT[sid] if sid != "S01" else 0
cues = [
    # lighting presets by shot (set.py ENV): the golden hour of the hook, dusk, then a darker night each Friday
    {"at": 0, "name": "env", "preset": "gold"},
    {"at": SHOT_T("S04"), "name": "env", "preset": "bar"},
    {"at": SHOT_T("S06"), "name": "env", "preset": "harbour"},
    {"at": SHOT_T("S07"), "name": "env", "preset": "cafe"},
    {"at": SHOT_T("S08"), "name": "env", "preset": "sofa"},
    {"at": SHOT_T("S09"), "name": "env", "preset": "gold"},
    {"at": SHOT_T("S14"), "name": "env", "preset": "office"},
    {"at": SHOT_T("S15"), "name": "env", "preset": "night1"},
    {"at": SHOT_T("S27"), "name": "env", "preset": "night2"},
    {"at": SHOT_T("S32"), "name": "env", "preset": "night3"},
    {"at": SHOT_T("S35"), "name": "env", "preset": "night4"},
    {"at": SHOT_T("S71"), "name": "env", "preset": "office_five"},
    {"at": SHOT_T("S67"), "name": "env", "preset": "warm"},
    # the beam: off in the golden hour, a 1.5 s fade up in S20, down over 1.5 s with the reel (L32), up at L35
    {"at": 0, "name": "beam", "v": 0.0, "dur": 0.0},
    {"at": SHOT_T("S15"), "name": "beam", "v": 1.0, "dur": 0.0},        # (earlier Fridays: already running, a cut)
    {"at": SHOT_T("S20"), "name": "beam", "v": 0.0, "dur": 0.0},
    {"at": SHOT_T("S20"), "name": "beam", "v": 1.0, "dur": 1.5},
    {"at": "L32", "name": "beam", "v": 0.04, "dur": 1.5},
    {"at": "L35", "name": "beam", "v": 1.0, "dur": 1.5},
    # Theo's silhouette fades by beat (full black = 1.0), a slow fill back at L57
    {"at": 0, "name": "ring", "v": 1.0, "dur": 0.0},
    {"at": SHOT_T("S16"), "name": "ring", "v": 0.80, "dur": 0.0},
    {"at": SHOT_T("S17"), "name": "ring", "v": 0.66, "dur": 0.0},
    {"at": SHOT_T("S22"), "name": "ring", "v": 0.50, "dur": 0.0},
    {"at": SHOT_T("S27"), "name": "ring", "v": 0.38, "dur": 0.0},
    {"at": SHOT_T("S33"), "name": "ring", "v": 0.30, "dur": 0.0},
    {"at": SHOT_T("S35"), "name": "ring", "v": 0.14, "dur": 0.0},
    {"at": SHOT_T("S44"), "name": "ring", "v": 0.008, "dur": 0.0},
    {"at": SHOT_T("S45"), "name": "ring", "v": 0.0, "dur": 0.0},
    {"at": "L57", "name": "ring", "v": 1.0, "dur": 1.5},
    # the giant shadows on the screen
    {"at": "L47", "name": "shadow", "who": "me", "on": True, "rise": 1.8},
    {"at": SHOT_T("S62"), "name": "shadow", "who": "theo", "on": True, "rise": 0.001},
    {"at": "L59", "name": "shadow", "turn": 1.0},
    {"at": SHOT_T("S67"), "name": "shadow", "who": "me", "on": False},
    {"at": SHOT_T("S67"), "name": "shadow", "who": "theo", "on": False},
    # doors, cut on the swing: a door's cue lands a hair before its shot, so the swing is already under way
    {"at": "L46-0.18", "name": "door", "car": "me", "side": -1, "open": 1.0},
    {"at": "L55-0.18", "name": "door", "car": "theo", "side": -1, "open": 1.0},
    {"at": SHOT_T("S62"), "name": "door", "car": "me", "side": -1, "open": 0.0, "dur": 0.0},
    {"at": SHOT_T("S67"), "name": "door", "car": "theo", "side": 1, "open": 1.0, "dur": 0.0},
    {"at": SHOT_T("S68"), "name": "door", "car": "theo", "side": 1, "open": 0.0, "dur": 0.0},
    {"at": SHOT_T("S63"), "name": "door", "car": "theo", "side": -1, "open": 0.0, "dur": 0.0},
    {"at": SHOT_T("S72"), "name": "turn", "who": "theo", "deg": 55},
    {"at": SHOT_T("S72"), "name": "turn", "who": "me", "deg": -55},
    {"at": SHOT_T("S73"), "name": "turn", "who": "theo", "deg": 0},
    {"at": SHOT_T("S73"), "name": "turn", "who": "me", "deg": 0},
    # my teal car rolls into its bay in S18 (cut in as it stops)
    {"at": SHOT_T("S18"), "name": "roll", "dur": 2.2},
    # the popcorn tub: on the bench by Theo (S13), gone at night, slides to me at L62
    {"at": "L62-0.12", "name": "tub", "slide": 0.9},
    # the cap (on my head except in the office and in my car on Friday 1): set.py reads these
    {"at": 0, "name": "cap", "on": True},
    {"at": SHOT_T("S14"), "name": "cap", "on": False},
    {"at": SHOT_T("S15"), "name": "cap", "on": True},
    {"at": SHOT_T("S19"), "name": "cap", "on": False},
    {"at": SHOT_T("S20"), "name": "cap", "on": True},
]
# the screen's own light: a slow drift, brightness changes of 2 s or more; it follows the beam gain
# rim and glints: nothing to cue (always on); the Unlit's pose comes from the acting.

# ================================================================================================ fx
fx = [
    {"at": "L03", "kind": "punch", "dur": 0.6, "zoom": 1.06, "fade": 0.2},
    {"at": "L36", "kind": "punch", "dur": 0.6, "zoom": 1.08, "fade": 0.2},
    {"at": "L47", "kind": "punch", "dur": 0.8, "zoom": 1.06, "fade": 0.25},
    {"at": "L50", "kind": "punch", "dur": 0.6, "zoom": 1.08, "fade": 0.2},
]

# ================================================================================================ sound
sfx = [
    {"at": "L19", "kind": "sting", "db": -14, "dur": 1.6, "keep": True},
    {"at": "L24", "kind": "thud", "db": -16},
    {"at": "L30", "kind": "sting", "db": -18, "dur": 1.2},
    {"at": "L33", "kind": "whoosh", "db": -22, "dur": 1.5},
    {"at": "L35", "kind": "riser", "db": -22, "dur": 1.5},
    {"at": "L36", "kind": "hit", "db": -8, "keep": True},
    {"at": "L36+0.05", "kind": "sting", "db": -12, "dur": 2.2, "keep": True},
    {"at": "L41", "kind": "thud", "db": -14},
    {"at": "L46-0.15", "kind": "thud", "db": -14},
    {"at": "L47", "kind": "hit", "db": -9, "keep": True},
    {"at": "L47+0.05", "kind": "riser", "db": -16, "dur": 1.6, "keep": True},
    {"at": "L55-0.12", "kind": "thud", "db": -14},
    {"at": "L57", "kind": "bell", "db": -16},
    {"at": "L62-0.1", "kind": "click", "db": -20},
    {"at": "L65>-0.1", "kind": "hiss_fall", "db": -18, "dur": 1.4},
]
story = {
    "slug": "ep38-drive-in",
    "title": "In this town, a silhouette over your head shows who you miss",
    "made_for_kids": False,
    "premise": "In a town where a little gold-ringed silhouette floats over everyone's head showing who they miss most, a woman whose own silhouette has always been herself goes to the drive-in every Friday, parking three rows behind her husband, whose silhouette of her is fading week by week, while a tall thing no light lands on comes a row nearer each time.",
    "twist": "Her silhouette was never herself: it wears the cap she has worn for years and the tuft at the back of the man she married, so the one she missed most all year was her husband three rows ahead. The projector throws her silhouette the size of a house on the screen for the whole lot to read.",
    "world": "A drive-in lot at golden hour and by night: rows of big old blocky cars facing one huge pale screen, a projector beam with soft dust, gravel, speaker boxes on the car windows, and a few small rooms for the montage (a bar table, a harbour rail, a cafe table, a sofa, a late office).",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff6f61",
    "gap": 0.1,
    "tail": 1.3,
    "look": {"fog": "#2a2540", "fog_density": 0.004, "fog_start": 14.0, "sky": "#3a2a55", "sky_strength": 1.0,
             "exposure": 0.0, "flash_safe": True},
    "grade": {"shadows": [-0.01, 0.0, 0.04], "highlights": [0.04, 0.015, -0.03], "saturation": 1.0,
              "contrast": 1.06, "vignette": 0.3, "bloom": 0.3, "grain": 0.012},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": fx,
    "music": {"root": 48, "mode": "minor", "bpm": 66, "seed": 38,
              "sections": [
                  {"at": 0, "voices": ["pad", "pulse"], "energy": 0.4},
                  {"at": "L12", "voices": ["pad", "pulse", "piano"], "energy": 0.35},
                  {"at": "L19", "voices": ["pad", "pulse", "drone"], "energy": 0.45},
                  {"at": "L31", "voices": ["pad", "drone", "pulse"], "energy": 0.55},
                  {"at": "L36", "voices": ["drone", "choir", "pad"], "energy": 0.6},
                  {"at": "L47", "voices": ["drone", "choir", "pulse", "pad"], "energy": 0.8},
                  {"at": "L56", "voices": ["pad", "piano", "pulse"], "energy": 0.5, "mode": "major"},
                  {"at": "L63", "voices": ["pad", "piano"], "energy": 0.4, "mode": "major"},
              ]},
    "sound": {"floor": "stone", "steps_db": -22,
              "ambience": [
                  {"kind": "static", "from": 0, "to": "L34.3", "lufs": -42},
                  {"kind": "crickets", "from": 0, "to": "L33", "lufs": -38},
                  {"kind": "hum", "from": "L17", "to": "L33", "lufs": -40},
                  {"kind": "static", "from": "L35", "to": "end", "lufs": -42},
                  {"kind": "crickets", "from": "L35", "to": "end", "lufs": -38},
                  {"kind": "hum", "from": "L35", "to": "L62", "lufs": -40},
              ],
              "sfx": sfx,
              "music_drops": [{"from": "P18", "to": "L19"}, {"from": "P35", "to": "L36"}, {"from": "P46", "to": "L47"},
                              {"from": "L34.3", "to": "L35"}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
