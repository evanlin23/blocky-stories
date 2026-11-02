"""Writes ../story.json for ep22 "The little man in the model village moves one window a day".

Run from anywhere: python stories/ep22-model-village/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras,
the acting, the cues set.py reads, the score and the sound. The places are set.py's metres.
"""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
_sp = importlib.util.spec_from_file_location("ep22_layout", HERE.parent / "layout.py")
LAY = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(LAY)

cast = {
    "me": {"age": "adult", "skin": "#e2b48a", "shirt": "#4f6e4b", "pattern": "solid", "collar": "#3f5a3d",
           "pants": "#6b6e72", "shoes": "#2b2a2c", "sleeves": "long", "hair": "cap", "hair_c": "#5b3b27",
           "hat": "none", "extras": ["coat"], "face": {"eyes": "round", "brows": True, "ink": "#1d1416", "bags": True}},
    "maggie": {"age": "adult", "skin": "#e6bd98", "shirt": "#27355c", "pattern": "stripes", "pattern_c": "#e8e6e0",
               "pants": "#4a4a52", "shoes": "#2e2a28", "sleeves": "long", "hair": "bun", "hair_c": "#b9b9bd",
               "hat": "none", "height": 0.94, "face": {"eyes": "round", "brows": True, "ink": "#1d1416", "cheeks": "#e59a8e"}},
    "t1": {"age": "adult", "skin": "#d9a77c", "shirt": "#cfc6b0", "pattern": "knit", "pattern_c": "#b4aa94",
           "pants": "#2c3345", "shoes": "#222222", "sleeves": "long", "hair": "buzz", "hair_c": "#7a7a7a",
           "hat": "none", "width": 1.08, "face": {"eyes": "dot", "brows": True, "ink": "#1d1416"}},
    "t2": {"age": "adult", "skin": "#c68e64", "shirt": "#2d2f36", "pattern": "solid", "collar": "#24262c",
           "pants": "#24262c", "shoes": "#1c1c1e", "sleeves": "long", "hair": "cap", "hair_c": "#1e1a18",
           "hat": "none", "height": 1.04, "extras": ["coat"], "face": {"eyes": "round", "brows": True, "ink": "#1d1416"}},
    "t3": {"age": "adult", "skin": "#eac3a0", "shirt": "#f1e24f", "pattern": "solid", "collar": "#d9c93e",
           "pants": "#3b4a63", "shoes": "#5a2f2a", "sleeves": "long", "hair": "long", "hair_c": "#8a4a2a",
           "hat": "none", "height": 0.93, "extras": ["coat"], "face": {"eyes": "lashes", "brows": True, "ink": "#1d1416"}},
    "t4": {"age": "adult", "skin": "#dcb28a", "shirt": "#6c5b4a", "pattern": "plaid", "pattern_c": "#40382e",
           "pants": "#3a3a3a", "shoes": "#2a2220", "sleeves": "long", "hair": "none", "hair_c": "#999999",
           "hat": "ballcap", "hat_c": "#3a4a5a", "height": 0.97, "face": {"eyes": "tired", "brows": True, "ink": "#1d1416"}},
    "t5": {"age": "adult", "skin": "#b98260", "shirt": "#7a3f55", "pattern": "knit", "pattern_c": "#5f2f42",
           "pants": "#2a2c34", "shoes": "#222222", "sleeves": "long", "hair": "swoop", "hair_c": "#2a1d15",
           "hat": "none", "height": 0.96, "face": {"eyes": "round", "brows": True, "ink": "#1d1416"}},
    "resident": {"age": "adult", "skin": "#e8b98f", "shirt": "#1f2e52", "pattern": "solid", "collar": "#1a2644",
                 "pants": "#1e2230", "shoes": "#14161c", "sleeves": "long", "hair": "cap", "hair_c": "#2b1d14",
                 "hat": "none", "height": 0.0257, "extras": ["coat", "scarf"], "extra_c": "#cc9a1c",
                 "face": {"eyes": "round", "brows": False, "mouth": "line", "ink": "#120d0e", "pupil": "#0a0708"}},
}

TEA = LAY.stand("tea")
tr = LAY.room("tea")
fp = [TEA[0], TEA[1] - 0.0054, TEA[2] + 0.04]
shots = [{"id": "S01", "cam": [LAY.window_cam("tea", 0.13, lens=60, tz=-0.02) and [0, *LAY.window_cam("tea", 0.12, lens=60, tz=-0.021)]], "dof": [2.8, fp], "hand": 0.0, "step": 2}]
acting = {k: [{"at": 0, "pos": [0, 0], "hidden": True}] for k in cast}
acting["resident"] = [{"at": 0, "pos": TEA, "yaw": 180, "head": [172, 9], "expr": "blank"}]

story = {
    "slug": "ep22-model-village",
    "title": "The little man in the model village moves one window a day",
    "made_for_kids": False,
    "premise": "I've taken a job repainting the knee-high model village on the front of a small seaside town. A thumb-sized man in a mustard scarf, made better than the glued painted figures, stands in a different tiny window every afternoon, one window further up the hill, toward my own model cottage.",
    "twist": "He was never coming for me. Every afternoon his window filled with my giant face, and every window I leaned into, he left. To him I was the monster, and at the end I am a tiny figure in the tea shop window myself.",
    "world": "a grey out-of-season seaside model village of painted wood houses on a sloping green ground, a low sea wall, wet slate sea, a gravel path round its front edge, and a brick town with a warm tea shop",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#5ccfc0",
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#8d959c", "fog_density": 0.012, "fog_start": 6.0, "sky": "#8d959c", "sky_strength": 1.0, "exposure": 0.0},
    "grade": {"shadows": [-0.01, 0.0, 0.03], "highlights": [0.0, 0.0, 0.0], "saturation": 0.95, "contrast": 1.06,
              "vignette": 0.3, "bloom": 0.2, "grain": 0.012},
    "phonemes": {},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": [],
    "fx": [],
    "music": {"root": 50, "mode": "dorian", "bpm": 76, "seed": 22,
              "sections": [{"at": 0, "voices": ["drone", "pad"], "energy": 0.3}]},
    "sound": {"floor": "stone", "steps_db": -22, "ambience": [], "sfx": []},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT, f"({len(shots)} shots)")
