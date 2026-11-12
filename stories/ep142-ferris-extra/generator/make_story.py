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
BW = 0.8
SC = 1.25          # the cast is drawn a quarter bigger than the rig default so five fit a 9:16 frame


def person(skin, shirt, pants, hair, hair_c, height, sleeves="short", hat="none", hat_c="#333333", face=None,
           extras=None, extra_c=None, collar=None, shoes="#2b2d33"):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": "solid", "pants": pants, "shoes": shoes,
         "sleeves": sleeves, "hair": hair, "hair_c": hair_c, "hat": hat, "hat_c": hat_c, "height": round(height * SC, 3),
         "body_width": BW, "face": face or dict(FACE)}
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
X = {"a": -2.4, "b": -1.2, "c": 0.0, "d": 1.2, "e": 2.4}
GATE_X, MAN = 5.0, (5.75, -1.3)
ARM = 62          # degrees the right arm is raised: a cone at chest height

acting = {k: [] for k in cast}
for k, x in X.items():
    acting[k].append({"at": 0, "pos": [x, 0], "yaw": 0, "arms": [0, ARM], "expr": "smile", "blend": 0})
acting["d"][0]["blink"] = False
for k in "ace":      # S01a stands close to the lens: the other three step in on the cut
    acting[k][0]["hidden"] = True
    acting[k].append({"at": "L02", "hidden": False, "blend": 0})

# B stands close to the lens for S01a, then steps into the row on the cut
BS = [-0.6, 1.8]
acting["b"][0] = {"at": 0, "pos": BS, "yaw": 0, "arms": [0, ARM], "expr": "smile", "blend": 0}
acting["b"].append({"at": "L01.2-0.04", "pos": BS, "hidden": True, "blend": 0})
acting["b"].append({"at": "L01.2", "pos": [-1.2, 0], "hidden": True, "blend": 0})
acting["b"].append({"at": "L02", "pos": [-1.2, 0], "hidden": False, "blend": 0})
acting["b"].append({"at": "L05", "expr": "worried", "blend": 0})
acting["a"].append({"at": "L05.1", "expr": "worried", "blend": 0})
acting["c"].append({"at": "L05.1", "expr": "neutral", "blend": 0})
acting["e"].append({"at": "L05.1", "expr": "worried", "blend": 0})
acting["a"].append({"at": "L06", "expr": "neutral", "blend": 0})
acting["e"].append({"at": "L06", "expr": "neutral", "blend": 0})
acting["b"].append({"at": "L16", "expr": "wide", "blend": 0})
acting["b"].append({"at": "L18", "expr": "worried", "blend": 0})
# the cousins look up at the wheel as D rises
for k in "abce":
    acting[k].append({"at": "L21", "head": [0, -30], "blend": 0.4})
# D: turns its head to the gate man (0.5 s), then walks out in front of E and through the gate
d = acting["d"]
d.append({"at": "L14", "pos": [1.2, 0]})
d.append({"at": "L18-0.1", "head": [55, 0], "blend": 0.4})
d.append({"at": "L18+0.55", "head": [0, 0], "pos": [1.2, 0], "blend": 0.25})
d.append({"at": "L18+1.2", "pos": [1.5, -1.3], "yaw": 13, "keep_yaw": True})
d.append({"at": "L19+1.2", "pos": [4.3, -1.3], "yaw": 50, "blend": 1.2, "sfx": "latch", "sfx_db": -20})
d.append({"at": "L19+1.3", "pos": [4.3, -1.3], "yaw": 50})
# the gate man: looks up at the wheel (S03), tips his hat to D (S18)
m = acting["man"]
m.append({"at": 0, "pos": list(MAN), "yaw": -25, "head": [0, -28], "arms": [0, 0], "expr": "smile", "blend": 0})
m.append({"at": "L16+0.4", "yaw": -25, "head": [0, -28], "arms": [0, 0]})
m.append({"at": "L17", "yaw": -75, "head": [0, 0], "arms": [125, 0], "blend": 0.4})
m.append({"at": "L17+0.9", "yaw": -75, "head": [0, 0], "arms": [125, 0]})
m.append({"at": "L18", "yaw": -75, "head": [0, 0], "arms": [0, 0], "blend": 0.4})


# ------------------------------------------------------------------------------------------------ the wheel (set.py's maths)
def _ride_times():
    """The seconds of the ride cue and S21..S23, from the last voiced timeline (these shots are keyed to the mint cabin)."""
    f = ROOT / "out" / "work" / "ep142-ferris-extra" / "timeline.json"
    if f.exists():
        tl = json.loads(f.read_text())
        return tl["lines"]["L20"]["onset"] + 0.3, tl["duration"]
    return 29.8, 32.8


T_RIDE, T_END = _ride_times()


def wheel_angle(t):
    rate = 180.0 / T_RIDE
    if t <= T_RIDE:
        return rate * t
    tau = t - T_RIDE
    g = tau ** 3 - tau ** 4 / 2 if tau <= 1 else 0.5 + (tau - 1)
    return 180.0 + rate * tau + 48.0 * g


def mint_head(t):
    """Where D's head is when he sits in the mint cabin (cabin 9, hung from the rim; set.py: floor 1.7 under the pivot)."""
    import math
    psi = math.radians(180.0 + wheel_angle(t))
    x, z = -1.3 + 5.2 * math.sin(psi), 7.1 - 5.2 * math.cos(psi)
    return x, 8.0, z - 1.7 - 0.85 + 1.99


# ------------------------------------------------------------------------------------------------ cameras
def still(loc, tgt, lens):
    return [[0, loc, tgt, lens]]


def move(a, b, la, lb=None):
    return [[0, a[0], a[1], la], [1, b[0], b[1], lb or la]]


MC = [0.2, -11.4, 2.8]
MT = [0.2, 0.0, 5.4]
ML = 23.0
MASTER = still(MC, MT, ML)


def mint_cam(t, dist, lift=0.0):
    x, y, z = mint_head(t)
    return [x, y - dist, z + lift], [x, y, z - 0.1]


c21a, c21b = mint_cam(29.7, 4.4), mint_cam(30.4, 4.0)
c23a, c23b = mint_cam(31.6, 4.2), mint_cam(T_END - 0.05, 3.8)
SHOTS = [
    (0, "S01a", "close: my face, the lilac gondola up right with D in it, the wheel above",
     move(([-0.7, -1.2, 2.6], [0.9, 8.0, 3.0]), ([-0.6, -0.9, 2.6], [1.0, 8.0, 3.0]), 18, 19)),
    ("L01.2", "S01b", "punch in on the gondola above: D in his white shirt", move(([0.2, 1.0, 1.8], [2.5, 8.0, 3.1]), ([1.3, 3.5, 2.8], [2.95, 8.0, 3.6]), 20, 36)),
    ("L02", "S02", "the master: the five on the platform, cones up, long shadows right", MASTER),
    ("L03", "S03", "the gate man, face a quarter of the width, looking up at the wheel", move(([3.4, -5.0, 2.4], [5.75, -1.3, 1.5]), ([3.5, -4.6, 2.45], [5.75, -1.3, 1.55]), 30, 32)),
    ("L04", "S04a", "the master again: a tag pops on each letter", MASTER),
    ("L04c", "S04b", "the master, tighter and to the right: C, D, E tags", move(([0.9, -10.2, 2.8], [0.9, 0, 5.4]), ([0.7, -9.9, 2.8], [0.7, 0, 5.4]), 24, 25)),
    ("L04e", "S04c", "the whole row, the last tag lands", move(([0.2, -11.8, 2.8], [0.2, 0, 5.4]), ([0.2, -11.6, 2.8], [0.2, 0, 5.4]), 22, 22.5)),
    ("L05", "S05a", "close: me, uneasy, my melting cone", move(([-0.9, -3.2, 2.1], [-0.9, 0, 1.8]), ([-0.9, -2.9, 2.1], [-0.9, 0, 1.85]), 26, 28)),
    ("L05.2+0.2", "S05b", "quick pan across A, C and E", move(([-2.4, -4.6, 2.0], [-2.4, 0, 1.8]), ([2.4, -4.6, 2.0], [2.4, 0, 1.8]), 24, 24)),
    ("L06", "S06", "the ice cream cart at the platform's end", move(([-4.2, -4.8, 1.7], [-6.2, -0.4, 1.4]), ([-4.6, -4.2, 1.7], [-6.2, -0.4, 1.5]), 28, 30)),
    ("L07", "S07", "close: my cone dripping down my wrist, my face above", move(([-2.4, -3.0, 1.8], [-0.95, 0, 1.5]), ([-2.2, -2.6, 1.8], [-0.95, 0, 1.55]), 30, 32)),
    ("L08", "S08", "the wheel icon starts its turn: the five whole, a slow push", move(([0.2, -11.6, 2.8], [0.2, 0, 5.4]), ([0.2, -11.4, 2.8], [0.2, 0, 5.4]), 21, 22.2)),
    ("L09", "S09", "the master, slow 4 percent push", move((MC, MT), ([0.2, -11.0, 2.8], MT), ML, ML * 1.04)),
    ("P01", "S10a", "hold: the lineup, all five faces, cones and shadows", move((MC, MT), (MC, MT), ML)),
    ("P01+1.2", "S10b", "hold: punch in 6 percent", move((MC, MT), (MC, MT), ML * 1.06)),
    ("P01+2.4", "S10c", "hold: punch in another 6 percent", move((MC, MT), (MC, MT), ML * 1.12)),
    ("L10", "S11", "punch in on D, the mint ring", move(([1.45, -5.0, 2.0], [1.45, 0, 1.7]), ([1.45, -4.4, 2.0], [1.45, 0, 1.75]), 26, 30)),
    ("L11", "S12a", "low and close along the row: A's, my and C's cones dripping", move(([-3.4, -3.8, 1.2], [-1.2, 0, 1.4]), ([-2.6, -3.6, 1.25], [-0.8, 0, 1.4]), 22, 24)),
    (rm("L11.2"), "S12b", "E's cone dripping", move(([1.9, -3.2, 1.2], [2.5, 0, 1.4]), ([2.3, -3.0, 1.25], [2.6, 0, 1.4]), 24, 27)),
    ("L12", "S13", "close: D's cone, tall and frosty, D's face above it", move(([1.9, -3.4, 1.9], [1.5, 0, 1.7]), ([1.8, -3.0, 1.95], [1.5, 0, 1.75]), 28, 30)),
    ("L13", "S14a", "low wide along the platform: four long shadows lying to the right", move(([-4.6, -4.6, 1.7], [0.0, 0.3, 0.3]), ([-4.2, -4.4, 1.7], [0.2, 0.3, 0.3]), 20, 21)),
    ("L13.1+0.15", "S14b", "from the right, high: the same four shadows and the sun side", move(([4.8, -5.2, 2.4], [-0.6, 0.4, 0.2]), ([4.4, -4.9, 2.4], [-0.4, 0.4, 0.2]), 20, 21)),
    ("L14", "S15a", "tilted down to D's feet and the shadow lying left, D's face at the top", move(([0.9, -4.4, 2.7], [0.9, 0, 1.3]), ([0.9, -4.1, 2.7], [0.9, 0, 1.35]), 17, 18)),
    ("L14.1+0.15", "S15b", "punch in on D's feet and the shadow, D's face at the top", move(([1.0, -3.4, 2.5], [0.8, 0, 1.3]), ([1.0, -3.1, 2.5], [0.8, 0, 1.35]), 22, 25)),
    ("L15", "S16", "up at the top of the wheel, a gondola there, its door just closing", move(([-1.3, 0.0, 3.5], [-1.3, 8.0, 12.0]), ([-1.3, 1.0, 3.8], [-1.3, 8.0, 12.2]), 20, 22)),
    ("L16", "S17", "my face, stunned", move(([-0.7, -2.9, 2.0], [-0.9, 0, 1.9]), ([-0.8, -2.6, 2.0], [-0.9, 0, 1.95]), 28, 30)),
    ("L17", "S18", "the gate man raising his hat", move(([3.3, -4.4, 2.5], [5.7, -1.3, 1.6]), ([3.5, -4.1, 2.5], [5.7, -1.3, 1.65]), 30, 32)),
    ("L18", "S19", "D turning its head toward the gate", move(([0.5, -3.6, 2.0], [1.2, 0, 1.9]), ([0.6, -3.3, 2.0], [1.25, 0, 1.95]), 28, 30)),
    ("L19", "S20", "D beside the gate, the gate swinging open", move(([2.2, -5.3, 2.4], [4.5, -1.3, 2.2]), ([2.4, -5.0, 2.4], [4.55, -1.3, 2.25]), 34, 36)),
    ("L20", "S21", "D seated alone in the empty mint gondola, cone in hand", [[0, c21a[0], c21a[1], 26], [1, c21b[0], c21b[1], 28]]),
    ("L21", "S22", "wide: the wheel turning, the mint gondola rising; us small at the bottom", move(([-1.3, -17.0, 3.0], [-1.3, 8.0, 5.6]), ([-1.3, -17.0, 3.0], [-1.3, 8.0, 7.2]), 18, 18)),
    ("L22", "S23", "close at the top: D in the gondola, looking down at us", [[0, c23a[0], c23a[1], 26], [1, c23b[0], c23b[1], 28]]),
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
    {"at": "L02", "name": "pip5"},
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
                        "hold": ["S10a", "S10b", "S10c"]}},
    "grade": {"shadows": [0.0, 0.0, 0.02], "highlights": [0.02, 0.01, -0.01], "saturation": 1.08, "contrast": 1.04,
              "vignette": 0.15, "bloom": 0.12, "grain": 0.008},
    "hud": {"object": "tag", "at": [0.66, 0.8], "size": 0.5},
    "asr_forgive": ["ay bee see dee ee", "ferris", "dee", "ee", "bee", "dee's is", "dee's"],
    "phonemes": {"ay": "ˈAː", "bee": "bˈi", "see": "sˈi", "dee": "dˈi", "ee": "ˈiː", "dee's": "dˈiz", "ferris": "fˈɛɹɪs"},
    "notags": ["S01a", "S01b", "S03", "S05a", "S05b", "S06", "S07", "S11", "S12a", "S12b", "S13", "S14a", "S14b", "S15a", "S15b", "S16", "S17", "S18", "S19", "S20", "S21", "S22", "S23"],
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "fx": [],
    "framing_ok": ["S19", "S01b", "S06", "S16", "S21", "S23"],
    "staging_ok": ["S02", "S04a", "S04b", "S04c", "S05a", "S05b", "S07", "S08", "S09", "S10a", "S10b", "S10c", "S11", "S12a", "S12b", "S13", "S14a", "S14b", "S15a", "S15b", "S17", "S19/c+d", "S19/d+e", "S22/a+b", "S22/b+c"],
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
