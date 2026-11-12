"""Writes ../story.json for "The Ice Cream Truck Knows Who's LEAVING" (ep151-truck-attic).

WIP: creature-test version (cast, S01 placeholder, S27 the reveal). Run: python stories/ep151-truck-attic/generator/make_story.py
World (metres, z up, the house front faces -y): our garage front wall at y 0, x 0..5; the attic window over it at
x 2.5, z 3.15..4.05; the driveway x 1.5..5.5 running to the street at y -9; the truck stops in it, nose to the garage.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
FACE = {"eyes": "round", "brows": True, "ink": "#2b1d1a"}
cast = {
    "me": {"age": "teen", "skin": "#c89868", "shirt": "#e0b030", "pattern": "solid", "pants": "#6e727a",
           "shoes": "#f4f4f2", "sleeves": "short", "hair": "swoop", "hair_c": "#5a3a22", "face": dict(FACE)},
    "icecream": {"age": "adult", "skin": "#e0b890", "shirt": "#9fe6c8", "pattern": "solid", "pants": "#f2f2ee",
                 "shoes": "#f4f4f2", "sleeves": "long", "hair": "none", "hat": "ballcap", "hat_c": "#f6f6f2",
                 "face": dict(FACE)},
}
shots = [
    {"id": "S01", "cam": [[0, [-3.6, -9.4, 1.2], [2.2, -2.4, 2.45], 21]], "step": 2, "look": "day"},
    {"id": "S27", "at": "L26", "cam": [[0, [-3.6, -9.4, 1.2], [2.2, -2.4, 2.45], 21],
                                       [1, [-3.4, -9.0, 1.2], [2.2, -2.4, 2.45], 22]], "step": 2, "look": "day",
     "note": "the reveal: window, sleeve over the gutter, down to the hatch, the ice cream man, the cuff in sun"},
]
acting = {
    "me": [{"at": 0, "pos": [0.0, 30.0], "yaw": 150, "expr": "scared", "head": [0, 0]}],
    "icecream": [{"at": 0, "pos": [3.15, -3.7, 0.45], "yaw": -90, "expr": "neutral"}],
}
story = {
    "slug": "ep151-truck-attic", "title": "The Ice Cream Truck Knows Who's LEAVING \U0001f69a", "made_for_kids": False,
    "premise": "In this town the ice cream truck stops at any house where someone is about to move out, and it stops at ours every day while nobody is moving.",
    "twist": "Someone has lived in our attic longer than we have, and on Saturday a gray sleeve reached out of the attic window for an ice pop and moved in next door.",
    "world": "a bright summer suburban street, our pale blue house with a white garage and a small attic window over it, a mint ice cream truck",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45}, "key_color": "#b46cff", "gap": 0.15, "tail": 0.25,
    "min_read": 0.15, "fade_in": False, "fade_out": False,
    "look": {"sky": "#8fd0ff", "fog": "#cfe8ff", "fog_density": 0.002, "fog_start": 40.0, "exposure": 0.0,
             "flash_safe": True, "style": "closer", "polish": True},
    "grade": {"shadows": [-0.01, 0.0, 0.03], "highlights": [0.03, 0.01, -0.02], "saturation": 1.12,
              "contrast": 1.05, "vignette": 0.15, "bloom": 0.15, "grain": 0.008},
    "cast": cast, "lines": lines, "shots": shots, "acting": acting, "cues": [], "rev": 1,
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False))
print("wrote", OUT)
