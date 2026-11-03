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
    if ln["id"] == "L04":
        ln["tempo"] = 0.9
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
E = person("#e0b48c", "#8e5bd6", "#2b2b33", "bun", "#f1f1f1", 0.9, "#f4f4f4", ["glasses"])
E["glasses_c"] = "#3a3a40"
cast = {"a": A, "b": B, "c": C, "d": D, "e": E}
for k in "abcde":
    cast["r" + k] = dict(cast[k])
cast["x"] = dict(C)
cast["bro"] = dict(C)
for k in list(cast):
    if k.startswith("r") or k in ("x", "bro"):
        cast[k] = {**cast[k], "height": round(cast[k]["height"] * 1.1, 3)}

ROWS = {"c": (-1.1, 0.6), "a": (1.35, 0.6), "b": (0.9, 1.6), "d": (-0.6, 1.6), "e": (-1.5, 1.6)}
GAP = (0.1, 0.6)
acting = {k: [] for k in cast}
for k, (x, y) in ROWS.items():
    acting[k].append({"at": 0, "pos": [x, y], "yaw": 0, "expr": "neutral"})
    rx = -2.35 if k == "e" else x      # a reflection's x is mirrored, except E's: it steps out from behind C's reflection
    acting["r" + k].append({"at": 0, "pos": [rx, -y], "yaw": 180, "expr": "neutral"})
acting["x"].append({"at": 0, "pos": [GAP[0], -GAP[1]], "yaw": 180, "expr": "neutral", "look": [0, 0]})
acting["bro"].append({"at": 0, "pos": [GAP[0], -GAP[1]], "yaw": 180, "expr": "worried", "hidden": True})
acting["d"].append({"at": "L16.3", "expr": "wide", "blend": 0})
acting["d"].append({"at": "L17", "expr": "neutral", "blend": 0})
acting["x"].append({"at": "L14+0.4", "hidden": True, "blend": 0})
acting["bro"].append({"at": "L15+0.2", "hidden": False, "blend": 0})

# ------------------------------------------------------------------------------------------------ cameras
def still(loc, tgt, lens):
    return [[0, loc, tgt, lens]]


def move(a, b, la, lb=None):
    return [[0, a[0], a[1], la], [1, b[0], b[1], lb or la]]


MAS = [0.0, 4.25, 3.8]
MT = [0.0, 0.0, 0.5]
ML = 14.5
MASTER = still(MAS, MT, ML)
SHOTS = [
    (0, "S01", "close on the doors: six faces, push in", move(([0, 4.1, 3.7], [0, -0.6, 1.5]), ([0, 3.7, 3.6], [0, -0.6, 1.5]), 17, 20), 2, 0),
    ("L01.4", "S02", "punch in on the six faces, the hit on SIX", still([0, 4.0, 3.7], [0, -0.6, 1.5], 27), 2, 1),
    ("L02", "S03", "the master", MASTER, 2, 0),
    ("L03", "S04", "side view along the car", move(([1.6, 3.9, 1.7], [0.0, 0.3, 1.2]), ([1.55, 3.8, 1.7], [-0.1, 0.3, 1.2]), 18), 2, 1),
    ("L04", "S05", "the master, tags pop", MASTER, 2, 0),
    ("L05", "S06", "over my shoulder", still([-0.3, 2.45, 1.75], [-0.8, 0.6, 1.15], 17), 2, 1),
    ("L06", "S07", "the master, slow push", move((MAS, MT), ([0.0, 3.75, 2.3], [0, 0, 0.85]), ML, 12.0), 2, 0),
    ("L07", "S08", "close on the display", still([0, 1.3, 2.9], [0, 0.15, 2.92], 42), 2, 1),
    ("P01", "S09", "the hold master, display 3", MASTER, 2, 0),
    ("P01+1", "S10", "punch in 6 percent, display 2", still(MAS, MT, ML * 1.06), 2, 0),
    ("P01+2", "S11", "punch in another 6 percent, display 1", still(MAS, MT, ML * 1.12), 2, 0),
    ("L08", "S12", "push in on the two blue jackets in the glass", move(([-0.5, 4.0, 3.7], [-0.5, -0.6, 1.4]), ([-0.5, 3.7, 3.6], [-0.5, -0.6, 1.4]), 20, 24), 2, 1),
    ("L09", "S13", "my brother three-quarter front, me behind him", still([-0.62, 0.1, 1.6], [-1.1, 0.6, 1.5], 13), 2, 1),
    ("L10", "S14", "his right shoulder, the bag", still([-0.6, 1.15, 1.6], [-1.5, 0.6, 1.1], 19), 2, 1),
    ("L11", "S15", "his reflection, bag on screen right", still([-1.2, 3.9, 3.7], [-0.9, -0.6, 1.3], 28), 2, 1),
    ("L11.3", "S15b", "the copy beside it, bag on screen left", still([0.0, 3.9, 3.7], [0.0, -0.6, 1.4], 28), 2, 1),
    ("L12", "S16", "the copy, mid close", still([0.0, 3.9, 3.7], [0.0, -0.6, 1.45], 36), 2, 1),
    ("L12.2", "S17", "punch in on its face", still([0.0, 3.9, 3.7], [0.0, -0.6, 1.58], 55), 2, 1),
    ("L13", "S18", "slow push on the copy and C's reflection", move(([-0.6, 3.9, 3.7], [-0.45, -0.6, 1.35]), ([-0.6, 3.5, 3.7], [-0.45, -0.6, 1.35]), 22, 27), 2, 1),
    ("P02", "S19", "close on the display: 1", still([0, 1.3, 2.9], [0, 0.15, 2.92], 42), 2, 1),
    ("L14", "S20", "the doors open on an empty corridor", MASTER, 2, 0),
    ("L15", "S21", "the doors close", MASTER, 2, 0),
    ("L16", "S22", "over my shoulder again, the bag on screen left", still([-0.3, 2.45, 1.75], [-0.8, 0.6, 1.15], 17), 2, 1),
    ("L16.3", "S23", "me from the side, wide", still([1.0, 0.95, 2.7], [-0.6, 1.6, 1.4], 22), 2, 1),
    ("L17", "S24", "close on his tag, a backwards C", still([-1.1, 1.3, 1.75], [-1.1, 0.84, 1.3], 34), 2, 1),
    ("L18", "S25", "my real brother in the glass", still([0.0, 3.9, 3.7], [0.0, -0.6, 1.45], 34), 2, 1),
    ("L19", "S26", "the master, push in on the copy's back", move(([0.0, 4.2, 3.7], [-0.5, 0.0, 1.0]), ([-1.0, 3.5, 3.7], [-0.9, 0.6, 1.2]), 12, 19), 2, 1),
]
shots = []
corner = []
for i, (at, sid, what, cam, step, cor) in enumerate(SHOTS):
    s = {"id": sid, "cam": cam, "hand": 0.0 if sid in ("S09", "S10", "S11") else 0.004, "step": step, "what": what}
    if i:
        s["at"] = at
    shots.append(s)
    if cor:
        corner.append(sid)
# S08 and S19 are close on the display itself
corner = [c for c in corner if c not in ("S08", "S19")]

# ------------------------------------------------------------------------------------------------ cues
BEFORE = {"c": -1, "rc": 1, "x": -1}
AFTER = {"c": 1, "rc": -1, "bro": -1}
cues = [
    {"at": 0, "name": "digit", "d": 7},
    {"at": "L02", "name": "digit", "d": 6},
    {"at": "L05", "name": "digit", "d": 5},
    {"at": "L07.1", "name": "digit", "d": 4},
    {"at": "P01", "name": "digit", "d": 3},
    {"at": "P01+1", "name": "digit", "d": 2},
    {"at": "P01+2", "name": "digit", "d": 1},
    {"at": 0, "name": "bags", "sides": BEFORE},
    {"at": "L14+0.4", "name": "bags", "sides": AFTER},
    {"at": 0, "name": "door", "open": 0.0},
    {"at": "L14", "name": "door", "open": 1.0, "dur": 0.8},
    {"at": "L15", "name": "door", "open": 0.0, "dur": 0.8},
    {"at": "L08", "name": "ring", "on": True},
    {"at": "L09", "name": "ring", "on": False},
]
for i, L_ in enumerate("ABCDE"):
    cues.append({"at": f"L04.{i}", "name": "tag", "who": L_})
cues.append({"at": "L14+0.4", "name": "tagflip", "who": "C"})

# ------------------------------------------------------------------------------------------------ sound
sfx = [
    {"at": "L01.4", "kind": "thud", "db": -6, "dur": 0.8},
    {"at": "P01", "kind": "thud", "db": -22, "dur": 0.2},
    {"at": "P01+1", "kind": "thud", "db": -22, "dur": 0.2},
    {"at": "P01+2", "kind": "thud", "db": -22, "dur": 0.2},
    {"at": "P02+0.1", "kind": "bell", "db": -18, "dur": 0.6},
    {"at": "L14", "kind": "whoosh", "db": -22, "dur": 0.9},
    {"at": "L15", "kind": "whoosh", "db": -22, "dur": 0.9},
]
story = {
    "slug": "ep62-six-riders",
    "title": "Five Riders, SIX In The Mirror",
    "made_for_kids": False,
    "premise": "Five office workers ride a steel elevator and its mirror doors show six faces. You get three floors to find the extra one: two reflections wear the same blue jacket, and the bag on one of them is on the wrong side of the glass.",
    "twist": "The extra face was never a reflection. It was something standing in the glass, practicing being my brother. When the doors open and close it trades places with him: the brother in the car has his bag on the other shoulder and a backwards letter, and my real brother is the one inside the glass.",
    "world": "a bright brushed-steel office elevator with a white LED ceiling and a teal floor display counting down, mirror doors, and an empty white corridor beyond them",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff8a1f",
    "gap": 0.12,
    "tail": 0,
    "fade_in": False,
    "look": {"fog": "#cfd8de", "fog_density": 0, "fog_start": 5.0, "sky": "#cfd8de", "sky_strength": 1.0,
             "exposure": -0.5, "flash_safe": True},
    "grade": {"shadows": [0.0, 0.0, 0.02], "highlights": [0.0, 0.0, 0.01], "saturation": 1.05, "contrast": 1.04,
              "vignette": 0.2, "bloom": 0.12, "grain": 0.008},
    "asr_forgive": ["ay bee see dee ee"],
    "phonemes": {"ay": "ˈA", "bee": "bˈi", "see": "sˈi", "dee": "dˈi", "ee": "ˈi"},
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
              "music_drops": [{"from": "P01", "to": "P01>", "keep": ["thud"]},
                              {"from": "P02", "to": "P02>", "keep": ["bell"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
