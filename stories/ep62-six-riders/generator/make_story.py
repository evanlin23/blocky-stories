"""Writes ../story.json for ep62-six-riders (script.md). Run: python stories/ep62-six-riders/generator/make_story.py

Places are set.py's (metres): the doors are the plane y = 0, the car runs toward the camera (y 0 to 3.65, x +-1.75).
Screen left is world +x. Riders face -y (yaw 0). The mirror cast stands at (x, -y), facing us (yaw 180).
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
LOOP = 0.12
for ln in lines:
    if ln["id"].startswith("L04"):
        ln["tempo"] = 0.9       # each letter on its own clip, 0.3 s apart, landing on its tag pop
lines = lines + [{"id": "P03", "pause": LOOP, "chunks": []}]

# ------------------------------------------------------------------------------------------------ cast
BW = 0.52


def person(skin, shirt, pants, hair, hair_c, height, collar=None, extras=None, hat="none"):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": "#2b2d33",
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "hat": hat, "height": height, "body_width": BW,
         "face": {"eyes": "round", "brows": True}}
    if collar:
        d["collar"] = collar
    if extras:
        d["extras"] = extras
    return d


C = person("#c58c63", "#2f5bea", "#2a2d3a", "cap", "#6b4423", 1.04, "#f4f4f4")
D = person("#c58c63", "#3fbf5a", "#2a2d3a", "cap", "#6b4423", 1.0, "#f4f4f4")
A = person("#6b4429", "#e8433a", "#22252d", "bun", "#141414", 0.97, "#f4f4f4")
B = person("#d9a679", "#ffd23f", "#2b2f3a", "cap", "#141414", 1.02, "#1d2a44", ["tie"])
cast = {"a": A, "b": B, "c": C, "d": D}
for k in "abcd":
    cast["r" + k] = dict(cast[k])
cast["x"] = dict(C)
cast["bro"] = dict(C)
for k in list(cast):
    if k.startswith("r") or k in ("x", "bro"):
        cast[k] = {**cast[k], "height": round(cast[k]["height"] * 1.1, 3)}

ROWS = {"c": (-1.2, 0.6), "a": (1.35, 0.6), "b": (0.95, 2.1), "d": (-1.0, 2.1)}
GAP = (-0.5, 0.6)
acting = {k: [] for k in cast}
for k, (x, y) in ROWS.items():
    # the real riders stand out of the first 3 s so the five faces in the glass are all clear (S01, S02)
    acting[k].append({"at": 0, "pos": [x, y], "yaw": 0, "expr": "neutral", "hidden": True})
    acting[k].append({"at": "L02+0.45", "pos": [x, y], "yaw": 0, "hidden": False, "blend": 0})
    # D's reflection stands a little right of his true x (-1.0) so his face is not behind the two blue jackets
    acting["r" + k].append({"at": 0, "pos": [0.2 if k == "d" else x, -y], "yaw": 180, "expr": "neutral"})
acting["x"].append({"at": 0, "pos": [GAP[0], -GAP[1]], "yaw": 180, "expr": "neutral", "look": [0, 0], "blink": False})
acting["bro"].append({"at": 0, "pos": [GAP[0], -GAP[1]], "yaw": 180, "expr": "worried", "hidden": True})
acting["c"].append({"at": "L09+0.2", "yaw": 40, "blend": 0})     # S13: he turns his face toward the lens
acting["c"].append({"at": "L10", "yaw": 0, "blend": 0})
# keys with a pos walk to it from the key before, so D is held at his spot and moved while hidden (he used to drift all film)
acting["d"].append({"at": "L09+0.17", "pos": list(ROWS["d"]), "hidden": True, "blend": 0})
acting["d"].append({"at": "L09+0.2", "pos": [-0.8, 1.05], "hidden": False, "blend": 0})     # S13: half a step behind his shoulder
acting["d"].append({"at": "L10-0.03", "pos": [-0.8, 1.05], "blend": 0})     # hold still to the cut, reset behind S14
acting["d"].append({"at": "L10", "pos": [ROWS["d"][0], ROWS["d"][1]], "blend": 0})
# S15: the glass shot is clear of the two riders in front of it, they stand aside for one shot
for k in "abcd":
    acting[k].append({"at": "L11", "hidden": True, "blend": 0})
    acting[k].append({"at": "L12", "hidden": False, "blend": 0})
acting["d"].append({"at": "L16.3", "expr": "wide", "blend": 0})
acting["d"].append({"at": "L17", "expr": "neutral", "blend": 0})
acting["x"].append({"at": "L14+0.4", "hidden": True, "blend": 0})
acting["bro"].append({"at": "L15+0.2", "hidden": False, "blend": 0})

# ------------------------------------------------------------------------------------------------ cameras
def still(loc, tgt, lens):
    return [[0, loc, tgt, lens]]


def move(a, b, la, lb=None):
    return [[0, a[0], a[1], la], [1, b[0], b[1], lb or la]]


MAS = [0.0, 4.25, 3.8]      # wide enough for A and B tags and both glass bags; D never hides the C tag
MT = [0.0, 0.0, 0.5]
ML = 14.0
MASTER = still(MAS, MT, ML)
GX, CX = GAP[0], ROWS["c"][0]
BLUE = (GX + CX) / 2          # the glass between the two blue jackets
S06 = still([-1.5, 3.0, 2.0], [-1.25, 0.6, 1.2], 15)
S14 = still([-1.5, 2.4, 3.3], [-1.5, 0.6, 1.45], 18)
S01A = ([0.05, 4.1, 2.9], [0.05, -0.6, 1.3])    # the five faces sit in the upper middle of the glass, under the door top
S01B = ([0.05, 4.0, 2.8], [0.05, -0.6, 1.3])
S02C = [0.05, 3.95, 2.65]
SHOTS = [
    (0, "S01", "close on the doors: five faces, push in until they fill the width", move(S01A, S01B, 19, 20)),
    ("L01.4", "S02", "the five faces, lower and closer, the hit on FIVE; held until after 3 s", still(S02C, [0.05, -0.6, 1.3], 20)),
    ("L02+0.45", "S03", "the master", MASTER),
    ("L03", "S04", "side view along the car", move(([1.6, 3.9, 1.7], [0.0, 0.3, 1.2]), ([1.55, 3.8, 1.7], [-0.1, 0.3, 1.2]), 18)),
    ("L04", "S05", "the master, tags pop", MASTER),
    ("L04c", "S05b", "punch in on C and D", still(MAS, MT, ML * 1.1)),
    ("L05", "S06", "over my shoulder", S06),
    ("L06", "S07", "the master, slow push", move((MAS, MT), ([0.0, 4.0, 2.9], [0, 0, 0.7]), ML, 13.0)),
    ("L07", "S08", "the display, wide enough that the dark plate is a small part of the frame", still([0, 2.0, 2.95], [0, 0.15, 2.85], 26)),
    ("P01", "S09", "the hold master, display 4 (two equal keys: the polish camera leaves it still so both bags stay in the glass)", move((MAS, MT), (MAS, MT), ML)),
    ("P01+1", "S10", "punch in 6 percent", move((MAS, MT), (MAS, MT), ML * 1.06)),
    ("P01+2", "S11", "punch in another 6 percent", move((MAS, MT), (MAS, MT), ML * 1.12)),
    ("L08", "S12", "push in on the two blue jackets in the glass", move(([BLUE, 4.0, 3.7], [BLUE, -0.6, 1.4]), ([BLUE, 3.7, 3.6], [BLUE, -0.6, 1.4]), 20, 24)),
    ("L09+0.2", "S13", "two-shot: my brother three-quarter front, me behind his shoulder", still([0.9, 0.2, 1.8], [-1.0, 0.9, 1.35], 20)),
    ("L10", "S14", "his right shoulder, the bag", S14),
    ("L11", "S15", "his reflection, bag on screen right", still([1.4, 3.9, 3.9], [-1.4, -0.6, 1.5], 31)),
    ("L11.3", "S15b", "the copy beside it, bag on screen left", still([1.4, 3.9, 3.9], [GX, -0.6, 1.5], 28)),
    ("L12", "S16", "the copy, mid close", still([GX, 3.9, 3.8], [GX, -0.6, 1.45], 36)),
    ("L12.2", "S17", "punch in on its face", still([GX - 0.05, 3.9, 3.8], [GX - 0.05, -0.6, 1.58], 60)),
    ("L13", "S18", "slow push on the copy and C's reflection", move(([BLUE + 0.25, 3.9, 3.8], [BLUE, -0.6, 1.4]), ([BLUE + 0.25, 3.5, 3.8], [BLUE, -0.6, 1.4]), 22, 27)),
    ("P02", "S19", "close on the display: 1", still([0, 2.0, 2.95], [0, 0.15, 2.85], 26)),
    ("L14", "S20", "the doors open on an empty corridor", MASTER),
    ("L15", "S21", "the doors close", MASTER),
    ("L16", "S22", "framed like S06, the bag now on screen left", S06),
    ("L16.3", "S23", "S14's close from behind, the bag now on screen left", S14),
    ("L17", "S24", "close on his tag, a backwards C", still([-1.2, 1.3, 1.75], [-1.2, 0.84, 1.3], 34)),
    ("L18", "S25", "my real brother in the glass", still([GX, 3.9, 3.8], [GX, -0.6, 1.45], 34)),
    ("L19", "S26", "the master, push in on the copy's back", move(([0.0, 4.2, 3.7], [-0.5, 0.0, 1.0]), ([-1.0, 3.5, 3.7], [-1.0, 0.6, 1.2]), 12, 19)),
]


def sees_display(cam):
    """Is any part of the real floor display's plate in the frame at the shot's start or end (pinhole, 9:16)?"""
    import math
    pts = [(sx * 0.31, 0.15, 2.92 + sz * 0.17) for sx in (-1, 0, 1) for sz in (-1, 0, 1)]
    for _, loc, tgt, lens in cam:
        f = [t - l for t, l in zip(tgt, loc)]
        n = math.sqrt(sum(v * v for v in f)); f = [v / n for v in f]
        r = [f[1], -f[0], 0.0]; n = math.hypot(r[0], r[1]); r = [v / n for v in r]
        u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
        th = 12.0 / lens
        for p in pts:
            v = [a - b for a, b in zip(p, loc)]
            zc = sum(a * b for a, b in zip(v, f))
            if zc > 0.1 and abs(sum(a * b for a, b in zip(v, r)) / zc) < th * 0.5625 and abs(sum(a * b for a, b in zip(v, u)) / zc) < th:
                return True
    return False


shots = []
corner = []
for i, (at, sid, what, cam) in enumerate(SHOTS):
    s = {"id": sid, "cam": cam, "hand": 0.0 if sid in ("S09", "S10", "S11") else 0.004, "step": 2, "what": what}
    if i:
        s["at"] = at
    shots.append(s)
    if not sees_display(cam):
        corner.append(sid)
print("corner copies on:", corner)

# ------------------------------------------------------------------------------------------------ cues
BEFORE = {"c": -1, "rc": 1, "x": -1}
GLASS_AFTER = {"c": -1, "rc": -1, "bro": -1}     # the glass sets itself while the doors are open
AFTER = {"c": 1, "rc": -1, "bro": -1}
cues = [
    {"at": 0, "name": "digit", "d": 5},
    {"at": "L07.1", "name": "digit", "d": 4},
    {"at": "L08+0.3", "name": "digit", "d": 3},
    {"at": "L12+0.3", "name": "digit", "d": 2},
    {"at": "P02+0.1", "name": "digit", "d": 1},
    {"at": 0, "name": "bags", "sides": BEFORE},
    {"at": "L14+0.4", "name": "bags", "sides": GLASS_AFTER},
    {"at": "L16", "name": "bags", "sides": AFTER},
    {"at": 0, "name": "door", "open": 0.0},
    {"at": "L14", "name": "door", "open": 1.0, "dur": 0.8},
    {"at": "L15", "name": "door", "open": 0.0, "dur": 0.8},
    {"at": "L08", "name": "ring", "on": True},
    {"at": "L09", "name": "ring", "on": False},
]
for L_, lid in zip("ABCD", ["L04", "L04b", "L04c", "L04d"]):
    cues.append({"at": lid, "name": "tag", "who": L_})
cues.append({"at": "L16", "name": "tagflip", "who": "C"})

# ------------------------------------------------------------------------------------------------ sound
sfx = [
    {"at": "L01.4+0.39", "kind": "sting", "db": -7, "dur": 0.8},    # the FIVE hit: a mid cluster (D4 to A4), phones play it; a thud is under 150 Hz
    {"at": "P01", "kind": "thud", "db": -22, "dur": 0.2},
    {"at": "P01+1", "kind": "thud", "db": -22, "dur": 0.2},
    {"at": "P01+2", "kind": "thud", "db": -22, "dur": 0.2},
    {"at": "P02+0.1", "kind": "bell", "db": -18, "dur": 0.6},
    {"at": "L07.1", "kind": "click", "db": -20, "dur": 0.1},
    {"at": "L08+0.3", "kind": "click", "db": -20, "dur": 0.1},
    {"at": "L12+0.3", "kind": "click", "db": -20, "dur": 0.1},
    {"at": "L14", "kind": "whoosh", "db": -22, "dur": 0.9},
    {"at": "L15", "kind": "whoosh", "db": -22, "dur": 0.9},
]
story = {
    "rev": 7,
    "slug": "ep62-six-riders",
    "title": "The Elevator Mirror Shows FIVE",
    "made_for_kids": False,
    "premise": "Four office workers ride a steel elevator and its mirror doors show five faces. You get three floors to find the extra one: two reflections wear the same blue jacket, and the bag on one of them is on the wrong side of the glass.",
    "twist": "The extra face was never a reflection. It was something standing in the glass, practicing being my brother. When the doors open and close it trades places with him: the brother in the car has his bag on the other shoulder and a backwards letter, and my real brother is the one inside the glass.",
    "world": "a bright brushed-steel office elevator with a white LED ceiling and a teal floor display counting down, mirror doors, and an empty white corridor beyond them",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff8a1f",
    "gap": 0.12,
    "tail": 0,
    "fade_in": False,
    "look": {"fog": "#cfd8de", "fog_density": 0, "fog_start": 5.0, "sky": "#cfd8de", "sky_strength": 1.0,
             "exposure": -0.5, "flash_safe": True,
             # the polish pack: punch-in on the hook, a reveal on the quotable line, a riser into the twist, tense sway on the copy
             "polish": {"emph": ["L01"], "reveal": ["L12"], "twist": "L17", "sway": ["S16", "S17", "S18", "S25"]}},
    "grade": {"shadows": [0.0, 0.0, 0.02], "highlights": [0.0, 0.0, 0.01], "saturation": 1.05, "contrast": 1.04,
              "vignette": 0.2, "bloom": 0.12, "grain": 0.008},
    "asr_forgive": ["ay bee see dee"],
    "phonemes": {"ay": "ˈAː", "bee": "bˈi", "see": "sˈi", "dee": "dˈi"},
    "notags": ["S13", "S15"],
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "corner": corner,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 50, "mode": "phrygian", "bpm": 112, "seed": 62,
              "sections": [
                  {"at": 0, "voices": ["pulse"], "energy": 0.3},
                  {"at": "L04", "voices": ["pulse", "pad"], "energy": 0.35},
                  {"at": "P01", "voices": ["pad"], "energy": 0.2},
                  {"at": "L08", "voices": ["drone", "pad"], "energy": 0.4},
                  {"at": "L14", "voices": ["drone"], "energy": 0.45},
              ]},
    "sound": {"floor": "metal", "steps_db": -22,
              "ambience": [{"kind": "hum", "from": 0, "to": "end", "lufs": -36},
                           {"kind": "room", "from": 0, "to": "end", "lufs": -38}],
              "sfx": sfx,
              "music_drops": [{"from": "P01", "to": "P01>", "keep": ["thud"], "db": -20},
                              {"from": "P02", "to": "P02>", "keep": ["bell"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
