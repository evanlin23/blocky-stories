"""Writes ../story.json for "One Of These Paintings BREATHES" (ep88-six-paintings, batch 8).

Run from anywhere: python stories/ep88-six-paintings/generator/make_story.py
The words are in lines.json next to this file. Set.py builds the hall (metres, z up, the long wall at y 2.9, the
camera in the hall at -y looking +y). Grid columns x -1.2, 0, 1.2 (A B C top, D E F below); top row frame centre z 4.15,
bottom 1.6. C is a window: the man stands on the garden terrace (top z 2.85) at y 3.95 behind it.

The full build: every shot of the plan (S01 to S22c). Bump rev when shots change.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
OUT = HERE.parent / "story.json"
import re
orig_lines = json.loads((HERE / "lines.json").read_text())
# captions are two or three words at a time: longer chunks are split and chunk references remapped
lines, FIRST, LAST = [], {}, {}
for ln in orig_lines:
    out, fi, la = [], [], []
    for cap, spoken in ln["chunks"]:
        cw, sw = cap.split(), spoken.split()
        n = len(cw)
        k = 1 if n <= 3 else 2
        sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
        fi.append(len(out))
        i = 0
        for sz in sizes:
            out.append([" ".join(cw[i:i + sz]), " ".join(sw[i:i + sz])])
            i += sz
        la.append(len(out) - 1)
    FIRST[ln["id"]], LAST[ln["id"]] = fi, la
    lines.append({**ln, "chunks": out})


def remap(ref, last=False):
    if isinstance(ref, list):
        return [remap(r, last) for r in ref]
    if not isinstance(ref, str):
        return ref
    mm = re.match(r"^(L\d+[a-z]?)\.(\d+)(.*)$", ref)
    if mm and mm.group(1) in FIRST:
        tab = LAST if last else FIRST
        return f"{mm.group(1)}.{tab[mm.group(1)][int(mm.group(2))]}{mm.group(3)}"
    return ref
LOOP = 0.25
GX = (-1.2, 0.0, 1.2)
TOPZ, BOTZ = 4.15, 0.85

cast = {
    "watcher": {"age": "adult", "skin": "#e2b48c", "shirt": "#15131a", "pattern": "solid", "pants": "#15131a",
                "shoes": "#101010", "sleeves": "long", "hair": "swoop", "hair_c": "#0c0a0b", "extras": ["coat", "tie"],
                "extra_c": "#e9e6e0", "zip_c": "#15131a", "height": 1.16, "width": 0.9, "body_width": 0.55,
                "face": {"eyes": "hollow", "brows": True, "brow_w": 3.4, "ink": "#120c0e", "pupil": "#0b0709", "mouth": "line", "glow": "#eef4ff"}},
}
MAN = [1.2, 3.95, 2.9]
acting = {"watcher": [
    {"at": 0, "pos": MAN, "yaw": 0, "expr": "blank", "look": [0.45, 0.05], "blink": False, "arms": [0, 0], "side": [0, 0], "head": [0, -8]},
    {"at": "L18", "pos": MAN, "look": [0, 0], "blend": 0.5},
    {"at": "L19", "pos": MAN, "hidden": True},
]}


def C(loc, tgt, lens, loc2=None, tgt2=None, lens2=None):
    cam = [[0, list(loc), list(tgt), lens]]
    if loc2 or tgt2 or lens2:
        cam.append([1, list(loc2 or loc), list(tgt2 or tgt), lens2 or lens])
    return cam


def shot(sid, at, *cam):
    d = {"id": sid, "cam": C(*cam), "step": 1, "hand": 0.0}
    if at is not None:
        d["at"] = at
    return d


GRID_T = (0, 3, 2.95)
shots = [
    shot("S01", None, (0, -8.55, 2.95), GRID_T, 36, (0, -8.1, 2.95)),
    shot("S02", "L02", (0.45, -8.2, 3.0), GRID_T, 36, (0.2, -7.5, 3.0)),
    shot("S03", "L03", (-1.35, -2.1, 4.0), (-1.2, 2.9, 4.0), 36, (-1.25, -1.7, 4.0)),
    shot("S04", "L04", (0.1, -2.1, 4.0), (0, 2.9, 4.0), 36, (0.05, -1.7, 4.0)),
    shot("S05", "L05", (1.0, -2.1, 4.0), (1.2, 2.9, 4.0), 36, (1.15, -1.7, 4.0)),
    shot("S06", "L06", (-1.3, -2.1, 0.85), (-1.2, 2.9, 0.85), 36, (-1.2, -1.7, 0.85)),
    shot("S07", "L07", (0.1, -2.1, 0.85), (0, 2.9, 0.85), 36, (0.05, -1.7, 0.85)),
    shot("S08", "L08", (1.3, -2.1, 0.85), (1.2, 2.9, 0.85), 36, (1.2, -1.7, 0.85)),
    shot("S09", "L09", (-0.5, -7.8, 2.95), GRID_T, 36, (-0.2, -7.0, 3.0)),
    shot("S10", "L10", (0.5, -6.4, 3.0), (0.3, 3, 3.1), 36, (0.4, -5.7, 3.1)),
    shot("S11", "L11", (1.0, -3.8, 4.0), (1.2, 2.9, 4.3), 36, (1.15, -1.2, 4.35), (1.2, 3.0, 4.4), 40),
    shot("S12", "L12", (1.15, 0.2, 4.45), (1.25, 3.95, 4.5), 38, (1.22, 0.9, 4.5), (1.25, 3.95, 4.5), 38),
    shot("S13", "L13", (1.35, 1.3, 4.4), (1.3, 3.3, 4.4), 38, (1.32, 1.8, 4.38)),
    shot("S14", "L14", (3.8, 0.9, 4.2), (0.9, 2.9, 4.15), 36, (3.3, 1.2, 4.2)),
    shot("S14a", "L14a", (2.6, 3.0, 4.5), (1.0, 3.25, 4.55), 38, (2.35, 3.02, 4.55)),
    shot("S15", "L15", (1.3, 1.2, 4.2), (1.7, 2.8, 4.15), 36, (1.4, 1.6, 4.2)),
    shot("S16", "L16", (0.5, -1.8, 4.2), (1.2, 3.5, 4.1), 34, (0.7, -1.0, 4.2)),
    shot("S17", "L17", (3.4, 7.6, 4.5), (1.3, 3.4, 4.5), 28, (3.1, 6.9, 4.5), (1.25, 3.4, 4.5), 28),
    shot("S18", "L18", (1.1, 1.4, 4.55), (1.2, 3.95, 4.75), 34, (1.15, 1.7, 4.58)),
    shot("S19", "L19", (0, -7.2, 3.0), (0, 3, 3.0), 33, (0.2, -6.6, 3.0)),
    shot("S20", "L20", (1.0, -2.0, 4.25), (1.2, 3.5, 4.3), 36, (1.1, -1.4, 4.3)),
    shot("S21", "L21", (-2.9, 0.6, 1.2), (-4.05, 2.8, 1.0), 36, (-3.2, 1.2, 1.15)),
    shot("S22", "L22", (0, -7.2, 3.0), (0, 3, 3.0), 33, (0, -6.6, 2.3), (0, -3.6, -0.3), 34),
    shot("S22a", "L22a", (0.1, -7.2, 2.6), (0.1, -3.9, -0.62), 28, (0.1, -7.1, 2.55)),
    shot("S22b", "L22b", (0.1, -7.1, 2.55), (0.1, -3.9, -0.62), 28, (0.1, -6.9, 2.5)),
    shot("S22c", "L22b+0.55", (0, -8.55, 2.95), GRID_T, 36, (0, -8.45, 2.95)),
]

story = {
    "slug": "ep88-six-paintings",
    "title": "One Of These Paintings BREATHES \U0001F5BC️",
    "made_for_kids": False,
    "premise": "Six framed paintings hang in a hall, lettered A to F, and one of them is breathing; the viewer must find it before a brass clock chimes.",
    "twist": "Frame C is a window, not a painting: a living man has stood in the garden all night, perfectly still, breathing on the glass and watching the viewer look for him, and when you look again the window is empty and the garden door clicks.",
    "world": "a long oxblood gallery hall in an old house museum, gilt frames and gold letter plaques, one white window onto a sunny sage-green garden",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#e2b23c",
    "gap": 0.15,
    "tail": LOOP,
    "fade_in": False,
    "fade_out": False,
    "rev": 11,
    "look": {"fog": "#f0e0d0", "fog_density": 0.0, "fog_start": 30.0, "sky": "#a8dcff", "exposure": 0.0,
             "flash_safe": True, "style": "closer",
             "polish": {"emph": [remap(r, True) for r in ["L01.3", "L11", "L14.1", "L16", "L18.1", "L20", "L22b"]], "reveal": [remap("L14.1", True), "L20"],
                        "twist": "L20", "sway": ["S12", "S13", "S18"], "hold": ["S01", "S13", "S14a", "S22c"], "idle": False}},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.01, -0.02], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.12, "bloom": 0.2, "grain": 0.008},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": [{"at": "L02", "name": "sweep"}, {"at": "L10", "name": "chime"}, {"at": "L11", "name": "snap"},
             {"at": "L13", "name": "fogs"}, {"at": "L19", "name": "gone"}, {"at": remap("L21.1"), "name": "latch"},
             {"at": remap("L22.1"), "name": "floor"}, {"at": "L22b", "name": "second"}, {"at": "L22a", "name": "shade"}],
    "set_moves": ["S10", "S21", "S22a", "S22b"],
    "music": {"root": 38, "mode": "minor", "bpm": 60, "seed": 88,
              "sections": [{"at": 0, "voices": ["drone", "pad"], "energy": 0.35},
                           {"at": "L11", "voices": ["drone", "pad"], "energy": 0.6, "root": 26},
                           {"at": "L19", "voices": ["drone"], "energy": 0.3}]},
    "sound": {"rev": 11, "floor": "wood", "steps_db": -22, "ambience": [],
              "sfx": [{"at": "L01.3", "kind": "whoosh", "db": -13, "dur": 1.1},
                      {"at": "L10", "kind": "bell", "db": -6, "dur": 1.6},
                      {"at": "L13", "kind": "whoosh", "db": -17, "dur": 0.6},
                      {"at": remap("L21.1"), "kind": "latch", "db": -6}],
              "music_drops": [["L09+0.55", "L10"], {"from": remap("L21.1") + "+0.25", "to": "L22+0.2", "keep": ["latch"]}]},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots")
