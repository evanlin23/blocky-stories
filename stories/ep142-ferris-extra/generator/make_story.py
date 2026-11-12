"""Writes ../story.json for ep142-ferris-extra (script.md). Run: python stories/ep142-ferris-extra/generator/make_story.py

Places are set.py's (metres). Screen right is world +x, the camera looks along +y, and the cast faces -y (yaw 0).
The five stand in one row on the exit platform at y = 0: A -2.6, B -1.3, C 0, D 1.3, E 2.6 (1.3 m apart). The wheel is
behind them (hub x -1.3, y 8), the gate man and the iron gate are on screen right (x 5 to 5.75).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from blocky import timeline  # noqa: E402

OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
for ln in lines:
    if ln["id"] == "P01":
        ln["chunks"] = [["A to E?", ""]]
lines, cmap = timeline.split_lines(lines)


def rm(ref):
    """'L05.1' in the script's chunk numbering -> the split line's chunk number."""
    if "." in ref:
        lid, i = ref.split(".")
        return f"{lid}.{cmap[lid][int(i)]}"
    return ref


LOOP = 0.25
lines = lines + [{"id": "P03", "pause": LOOP, "chunks": []}]

# ------------------------------------------------------------------------------------------------ cast
FACE = {"eyes": "round", "brows": True}


def person(skin, shirt, pants, hair, hair_c, height, sleeves="short", hat="none", hat_c="#333333", face=None,
           extras=None, extra_c=None, collar=None, shoes="#2b2d33"):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c, "height": height,
         "face": face or dict(FACE)}
    if extras:
        d["extras"] = extras
    if extra_c:
        d["extra_c"] = extra_c
    if collar:
        d["collar"] = collar
    return d


cast = {
    "a": person("#8a5a3c", "#ff6f61", "#f2eee3", "bun", "#121212", 0.96, "none", face={"eyes": "lashes", "brows": True},
                shoes="#f4f4f4"),
    "b": person("#e1b48a", "#9be15d", "#3b4f7a", "cap", "#6b4423", 1.0, "short", "ballcap", "#2f3f66", shoes="#ffffff"),
    "c": person("#c58c63", "#59c3ff", "#4a4f5c", "spiky", "#121212", 1.05, "none"),
    "d": person("#f0c8a0", "#fbfbf6", "#c9ced8", "swoop", "#6a4a30", 1.02, "short", collar="#ffffff", shoes="#3a3a40"),
    "e": person("#d9a679", "#f4f1ea", "#7d52e6", "long", "#121212", 0.98, "short", face={"eyes": "lashes", "brows": True},
                extras=["apron"], extra_c="#9b6bff", shoes="#f4f4f4"),
    "man": person("#e8b890", "#d9453b", "#4a4036", "buzz", "#d8d8d8", 1.0, "long", "fedora", "#e6cf8a", collar="#ffffff"),
}
cast["man"]["band_c"] = "#c0392b"
X = {"a": -2.6, "b": -1.3, "c": 0.0, "d": 1.3, "e": 2.6}
GATE_X, MAN = 5.0, (5.75, -1.3)
ARM = 62          # degrees the right arm is raised: a cone at chest height

acting = {k: [] for k in cast}
for k, x in X.items():
    acting[k].append({"at": 0, "pos": [x, 0], "yaw": 0, "arms": [0, ARM], "expr": "smile", "blend": 0})
# the extra: smiles all film and never blinks
acting["d"][0]["blink"] = False

# B stands at a gondola door for S01a, then steps into the row on the cut
acting["b"][0] = {"at": 0, "pos": [-1.3, 4.9], "yaw": 0, "arms": [0, ARM], "expr": "smile", "blend": 0}
acting["b"].append({"at": "L01.1-0.04", "pos": [-1.3, 4.9]})
acting["b"].append({"at": "L01.1", "pos": [-1.3, 0], "hidden": True, "blend": 0})
acting["b"].append({"at": "L02", "pos": [-1.3, 0], "hidden": False, "blend": 0})
# L05: the cousins are uneasy
acting["b"].append({"at": "L05", "expr": "worried", "blend": 0})
acting["a"].append({"at": "L05.1", "expr": "worried", "blend": 0})
acting["c"].append({"at": "L05.1", "expr": "neutral", "blend": 0})
acting["e"].append({"at": "L05.1", "expr": "worried", "blend": 0})
acting["a"].append({"at": "L06", "expr": "neutral", "blend": 0})
acting["e"].append({"at": "L06", "expr": "neutral", "blend": 0})
acting["b"].append({"at": "L16", "expr": "wide", "blend": 0})
acting["b"].append({"at": "L18", "expr": "worried", "blend": 0})
# D: turns its head to the gate man (0.5 s), then walks out in front of E and through the gate
d = acting["d"]
d.append({"at": "L14", "pos": [1.3, 0]})
d.append({"at": "L15", "head": [0, 0], "blend": 0.3})
d.append({"at": "L15+0.8", "head": [0, 0]})
d.append({"at": "L18", "head": [-55, 0], "blend": 0.5})
d.append({"at": "L18+0.55", "head": [-55, 0], "pos": [1.3, 0]})
d.append({"at": "L18+0.7", "pos": [1.3, 0], "head": [0, 0], "blend": 0.3})
d.append({"at": "L19+0.15", "pos": [1.5, -1.3], "arms": [0, ARM], "blend": 0.3})
d.append({"at": "L19+1.35", "pos": [4.35, -1.3], "yaw": 90, "sfx": "latch", "sfx_db": -20})
d.append({"at": "L19+1.7", "pos": [4.35, -1.3], "yaw": 90})
# the gate man: looks up at the wheel (S03), tips his hat to D (S18)
m = acting["man"]
m.append({"at": 0, "pos": list(MAN), "yaw": -25, "head": [0, -28], "arms": [0, 0], "expr": "smile", "blend": 0})
m.append({"at": "L03+1.2", "yaw": -25, "head": [0, -28]})
m.append({"at": "L16+0.4", "yaw": -25, "head": [0, -28], "arms": [0, 0]})
m.append({"at": "L17", "yaw": -75, "head": [0, 0], "arms": [0, 165], "blend": 0.4})
m.append({"at": "L17+0.9", "yaw": -75, "head": [0, 0], "arms": [0, 165]})
m.append({"at": "L18", "yaw": -75, "head": [0, 0], "arms": [0, 0], "blend": 0.4})


# ------------------------------------------------------------------------------------------------ cameras
def still(loc, tgt, lens):
    return [[0, loc, tgt, lens]]


def move(a, b, la, lb=None):
    return [[0, a[0], a[1], la], [1, b[0], b[1], lb or la]]


MC = [0.1, -11.5, 5.8]
MT = [0.1, 0.0, 2.6]
ML = 23.0
MASTER = still(MC, MT, ML)
SHOTS = [
    (0, "S01a", "close: my face at the gondola door, my cone up, the wheel above, D tiny in the cabin above",
     move(([-1.0, 2.2, 1.1], [-1.3, 8.0, 5.0]), ([-1.0, 2.5, 1.1], [-1.3, 8.0, 5.6]), 17, 18)),
    ("L01.1", "S01b", "punch in on the wheel's hub turning", move(([-1.3, 1.0, 5.0], [-1.3, 8.0, 7.1]), ([-1.3, 3.0, 6.1], [-1.3, 8.0, 7.1]), 30, 38)),
    ("L02", "S02", "the master: the five on the platform, cones up, long shadows right", MASTER),
    ("L03", "S03", "the gate man at the gate, looking up at the wheel", move(([9.0, -8.0, 1.7], [5.7, -1.3, 1.9]), ([8.6, -7.4, 1.7], [5.7, -1.3, 1.95]), 24, 26)),
    ("L04", "S04", "the master again: a tag pops on each letter", MASTER),
    ("L05", "S05a", "close: me, uneasy, my melting cone", move(([-0.4, -3.2, 1.7], [-1.3, 0, 1.45]), ([-0.6, -2.8, 1.7], [-1.3, 0, 1.45]), 26, 28)),
    ("L05.2", "S05b", "quick pan across A, C and E", move(([-2.6, -4.5, 1.7], [-2.6, 0, 1.4]), ([2.6, -4.5, 1.7], [2.6, 0, 1.4]), 24, 24)),
    ("L06", "S06", "the ice cream cart at the platform's end", move(([-4.2, -4.8, 1.7], [-6.2, -0.4, 1.4]), ([-4.6, -4.2, 1.7], [-6.2, -0.4, 1.5]), 28, 30)),
    ("L07", "S07", "close: my cone dripping down my wrist, my face above", move(([-2.3, -2.8, 1.55], [-1.0, 0, 1.25]), ([-2.1, -2.4, 1.55], [-1.0, 0, 1.3]), 30, 32)),
    ("L08", "S08", "the wheel icon, punch in: the red dot starts its turn", move(([-6.0, -10.0, 3.0], [-1.0, 4.0, 4.5]), ([-5.0, -8.5, 3.0], [-1.0, 4.0, 4.5]), 18, 20)),
    ("L09", "S09", "the master, slow 4 percent push", move((MC, MT), ([0.1, -11.0, 5.6], MT), ML, ML * 1.04)),
    ("P01", "S10a", "hold: the lineup, all five faces, cones and shadows", move((MC, MT), (MC, MT), ML)),
    ("P01+1.2", "S10b", "hold: punch in 6 percent", move((MC, MT), (MC, MT), ML * 1.06)),
    ("P01+2.4", "S10c", "hold: punch in another 6 percent", move((MC, MT), (MC, MT), ML * 1.12)),
    ("L10", "S11", "punch in on D, the mint ring", move(([1.3, -4.2, 1.75], [1.3, 0, 1.35]), ([1.3, -3.6, 1.75], [1.3, 0, 1.4]), 26, 30)),
    ("L11", "S12a", "low and close along the row: A's, my and C's cones dripping", move(([-3.6, -3.6, 0.9], [-1.0, 0, 1.2]), ([-2.8, -3.4, 0.95], [-0.6, 0, 1.2]), 22, 24)),
    (rm("L11.2"), "S12b", "E's cone dripping", move(([1.6, -3.2, 0.95], [2.9, 0, 1.2]), ([2.0, -3.0, 0.95], [3.0, 0, 1.2]), 24, 27)),
    ("L12", "S13", "close: D's cone, tall and frosty, D's face above it", move(([2.0, -3.0, 1.4], [1.5, 0, 1.45]), ([1.8, -2.5, 1.45], [1.5, 0, 1.5]), 30, 32)),
    ("L13", "S14", "low wide along the platform: four long shadows lying to the right", move(([-5.5, -5.0, 0.8], [0.3, 0.4, 0.3]), ([-5.0, -4.8, 0.8], [0.6, 0.4, 0.3]), 22, 23)),
    ("L14", "S15a", "D's shadow lying to the left, toward the low sun", move(([2.4, -4.2, 2.2], [0.7, 0.2, 0.5]), ([2.2, -3.8, 2.2], [0.7, 0.2, 0.55]), 24, 26)),
    (rm("L14.1"), "S15b", "punch in on D's feet and the shadow, D's face at the top", move(([2.4, -3.0, 1.9], [0.8, 0.1, 0.9]), ([2.2, -2.6, 1.9], [0.8, 0.1, 1.0]), 28, 32)),
    ("L15", "S16", "up at the top of the wheel, a gondola there, its door just closing", move(([-1.3, 0.0, 3.5], [-1.3, 8.0, 12.0]), ([-1.3, 1.0, 3.8], [-1.3, 8.0, 12.2]), 20, 22)),
    ("L16", "S17", "my face, stunned", move(([-0.4, -2.8, 1.65], [-1.3, 0, 1.55]), ([-0.6, -2.4, 1.65], [-1.3, 0, 1.58]), 28, 30)),
    ("L17", "S18", "the gate man raising his hat", move(([4.4, -4.4, 1.6], [5.75, -1.3, 1.7]), ([4.6, -4.0, 1.6], [5.75, -1.3, 1.75]), 34, 36)),
    ("L18", "S19", "D turning its head to him", move(([0.9, -3.4, 1.7], [1.3, 0, 1.55]), ([1.0, -3.0, 1.7], [1.3, 0, 1.6]), 28, 30)),
    ("L19", "S20", "D at the gate, the gate swinging open", move(([2.4, -6.4, 1.7], [4.6, -1.3, 1.2]), ([3.2, -6.0, 1.7], [4.8, -1.3, 1.25]), 22, 24)),
    ("L20", "S21", "D seated alone in an empty mint gondola, cone in hand", move(([-1.3, 3.2, 1.3], [-1.3, 8.0, 1.6]), ([-1.3, 3.6, 1.3], [-1.3, 8.0, 1.7]), 20, 22)),
    ("L21", "S22", "wide: the wheel turning, the mint gondola rising; us small at the bottom", move(([-1.3, -17.0, 3.0], [-1.3, 8.0, 5.6]), ([-1.3, -17.0, 3.0], [-1.3, 8.0, 7.2]), 18, 18)),
    ("L22", "S23", "close at the top: D in the gondola, looking down at us", move(([-1.3, 3.0, 8.0], [-1.3, 8.0, 10.8]), ([-1.3, 3.6, 8.2], [-1.3, 8.0, 10.9]), 26, 28)),
]
shots = []
for i, (at, sid, what, cam) in enumerate(SHOTS):
    s = {"id": sid, "cam": cam, "hand": 0.0 if sid.startswith("S10") else 0.004, "step": 2, "what": what}
    if i:
        s["at"] = at
    shots.append(s)

# ------------------------------------------------------------------------------------------------ cues
cues = [
    {"at": "L08", "name": "turn", "on": True},
    {"at": "P01>", "name": "turn", "on": False},
    {"at": "L10", "name": "ring", "on": True},
    {"at": "L11", "name": "ring", "on": False},
    {"at": "L19", "name": "gate", "open": 1.0, "dur": 1.5},
    {"at": "L20+0.3", "name": "ride"},
    {"at": "L17", "name": "hat", "up": 1.0, "dur": 0.4},
    {"at": "L18", "name": "hat", "up": 0.0, "dur": 0.4},
]
for lid, who in zip(["L04", "L04b", "L04c", "L04d", "L04e"], "ABCDE"):
    cues.append({"at": lid, "name": "tag", "who": who})

# ------------------------------------------------------------------------------------------------ sound
sfx = [
    {"at": "L02", "kind": "thud", "db": -9, "dur": 0.4},
    {"at": "P01", "kind": "click", "db": -17, "dur": 0.1},
    {"at": "P01+1", "kind": "click", "db": -17, "dur": 0.1},
    {"at": "P01+2", "kind": "click", "db": -17, "dur": 0.1},
    {"at": "P01+3", "kind": "click", "db": -17, "dur": 0.1},
    {"at": "L20+0.15", "kind": "door", "db": -18},
]
story = {
    "rev": 1,
    "slug": "ep142-ferris-extra",
    "title": "Four Got On. FIVE Got Off 🎟️",
    "made_for_kids": False,
    "premise": "Four cousins ride a Ferris wheel and five people step off, and you get one turn of the wheel to find the extra one: four ice cream cones are melting down four wrists and one is still a tall frosty swirl, and four shadows point away from the low sun while one points at it.",
    "twist": "The extra isn't a copy of any of us. It is the wheel's own rider, who gets on at the top where nobody can, steps off with every group, and is tipped a hat by the gate man like he does every day, then walks back through the gate and rides up alone to wait for the next four.",
    "world": "a bright small-town park on a sunny afternoon: a white Ferris wheel with sixteen candy-coloured round gondolas, a pale sand wooden boarding platform with a short iron gate, a striped ice cream cart and low gold sun on the left",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#3fd6b0",
    "gap": 0.12,
    "tail": 0,
    "fade_in": False,
    "fade_out": False,
    "look": {"style": "closer", "fog": "#bfe6ff", "fog_density": 0, "fog_start": 60.0, "sky": "#8fd3ff", "sky_strength": 1.1,
             "exposure": 0.0, "flash_safe": True,
             "polish": {"emph": ["L01", "L02", "L12", "L14", "L15"], "reveal": ["L10", "L15"], "twist": "L15",
                        "hold": ["S02", "S04", "S09", "S10a", "S10b", "S10c", "S14", "S15a"]}},
    "grade": {"shadows": [0.0, 0.0, 0.02], "highlights": [0.02, 0.01, -0.01], "saturation": 1.08, "contrast": 1.04,
              "vignette": 0.15, "bloom": 0.12, "grain": 0.008},
    "hud": {"object": "tag", "at": [0.66, 0.8], "size": 0.5},
    "asr_forgive": ["ay bee see dee ee", "ferris", "dee", "ee", "bee", "dee's is", "dee's"],
    "phonemes": {"ay": "ˈAː", "bee": "bˈi", "see": "sˈi", "dee": "dˈi", "ee": "ˈiː", "dee's": "dˈiz", "ferris": "fˈɛɹɪs"},
    "notags": ["S01a", "S01b", "S03", "S05a", "S05b", "S06", "S07", "S08", "S11", "S12a", "S12b", "S13", "S15a", "S15b", "S16", "S17", "S18", "S19", "S20", "S21", "S22", "S23"],
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "music": {"root": 57, "mode": "dorian", "bpm": 120, "seed": 142,
              "sections": [
                  {"at": 0, "voices": ["pulse"], "energy": 0.3},
                  {"at": "L06", "voices": ["pulse", "musicbox"], "energy": 0.42},
                  {"at": "P01", "voices": ["pad"], "energy": 0.2},
                  {"at": "L10", "voices": ["drone", "pad"], "energy": 0.35, "root": 45},
                  {"at": "L19", "voices": ["drone", "musicbox"], "energy": 0.4, "root": 45},
              ]},
    "sound": {"floor": "wood", "steps_db": -26,
              "ambience": [{"kind": "wind", "from": 0, "to": "end", "lufs": -42}],
              "sfx": sfx,
              "music_drops": [{"from": "L02>", "to": "P02>"},
                              {"from": "P01", "to": "P01>", "keep": ["click"], "db": -20}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
