"""Writes ../story.json for "One Of These Paintings BREATHES" (ep88-six-paintings, batch 8).

Run from anywhere: python stories/ep88-six-paintings/generator/make_story.py
The words are in lines.json next to this file. Set.py builds the hall (metres, z up, the long wall at y 2.9, the
camera in the hall at -y looking +y). Grid columns x -1.2, 0, 1.2 (A B C top, D E F below); top row frame centre z 4.15,
bottom 1.6. C is a window: the man stands on the garden terrace (top z 2.85) at y 3.95 behind it.

THIS IS THE CREATURE-TEST VERSION: only the shots the reveal and frame 1 need. Rev stays at 1; bump it when shots change.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
LOOP = 0.25
GX = (-1.2, 0.0, 1.2)
TOPZ, BOTZ = 4.15, 1.6

cast = {
    "watcher": {"age": "adult", "skin": "#e2b48c", "shirt": "#15131a", "pattern": "solid", "pants": "#15131a",
                "shoes": "#101010", "sleeves": "long", "hair": "swoop", "hair_c": "#1d1719", "extras": ["coat", "tie"],
                "extra_c": "#e9e6e0", "zip_c": "#15131a", "height": 1.16, "width": 0.9,
                "face": {"eyes": "round", "brows": True, "ink": "#1a1114", "mouth": "line"}},
}
MAN = [1.2, 3.95, 2.9]
acting = {"watcher": [
    {"at": 0, "pos": MAN, "yaw": 0, "expr": "blank", "look": [0.45, 0.05], "blink": False, "arms": [0, 0], "side": [0, 0]},
    {"at": "L18", "pos": MAN, "look": [0, 0], "blend": 0.5},
]}


def C(loc, tgt, lens, loc2=None, tgt2=None, lens2=None):
    cam = [[0, list(loc), list(tgt), lens]]
    if loc2 or tgt2 or lens2:
        cam.append([1, list(loc2 or loc), list(tgt2 or tgt), lens2 or lens])
    return cam


shots = [
    {"id": "S01", "cam": C((0, -7.4, 3.3), (0, 3, 3.3), 31, (0, -6.8, 3.3), (0, 3, 3.3), 31), "step": 1, "hand": 0.0},
    {"id": "S05", "at": "L05", "cam": C((0.95, -1.6, 4.3), (1.05, 3, 4.3), 36), "step": 1, "hand": 0.0},
    {"id": "S12", "at": "L12", "cam": C((1.2, -0.6, 4.55), (1.2, 3, 4.45), 40), "step": 1, "hand": 0.0},
    {"id": "S18", "at": "L18", "cam": C((1.0, -1.0, 4.5), (1.12, 3.4, 4.45), 34), "step": 1, "hand": 0.0},
    {"id": "S19", "at": "L19", "cam": C((0, -7.2, 3.0), (0, 3, 3.0), 33), "step": 1, "hand": 0.0},
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
    "rev": 1,
    "look": {"fog": "#f0e0d0", "fog_density": 0.0, "fog_start": 30.0, "sky": "#a8dcff", "exposure": 0.0,
             "flash_safe": True, "style": "closer", "polish": True},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.01, -0.02], "saturation": 1.1, "contrast": 1.05,
              "vignette": 0.12, "bloom": 0.2, "grain": 0.008},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": [],
    "music": {"root": 38, "mode": "minor", "bpm": 60, "seed": 88,
              "sections": [{"at": 0, "voices": ["drone", "pad"], "energy": 0.35}]},
    "sound": {"rev": 1, "floor": "wood", "steps_db": -22, "ambience": [], "sfx": []},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots")
