"""CREATURE TEST ONLY (builder phase 1): writes ../story.json with one shot of Hal at full height (the L37 reveal).
The real make_story.py replaces this in step 2."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
lines = json.loads((HERE / "lines.json").read_text())
cast = {
    "me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#ff7f66", "pattern": "solid", "pants": "#c9b48a", "shoes": "#f4f4f2",
           "sleeves": "short", "hair": "buzz", "hair_c": "#c8a24a", "face": {"eyes": "round", "brows": True, "ink": "#24131f"}},
    "hal": {"age": "adult", "skin": "#e8b98f", "shirt": "#e0b23a", "pattern": "solid", "pants": "#6b5a3a",
            "shoes": "#3a2a20", "sleeves": "long", "collar": "#ffffff", "hair": "swoop", "hair_c": "#4a3a2a",
            "extras": ["tie"], "extra_c": "#2cc7c9", "height": 1.5, "width": 0.8,
            "face": {"eyes": "round", "brows": False, "ink": "#eabf96", "mouth": "flat", "eye_scale": 1.3}},
}
acting = {"me": [{"at": 0, "pos": [-1.7, -0.9, 0], "yaw": 160, "expr": "scared", "blend": 0, "hidden": False}],
          "hal": [{"at": 0, "pos": [0.2, 1.8, 0], "yaw": 0, "expr": "terrified", "blink": False, "blend": 0,
                   "lean": 26, "head": [14, 0], "arms": [62, 75], "side": [0, 0], "hidden": False}]}
shots = [{"id": "S37", "cam": [[0, [0.0, -1.3, 0.62], [0.1, 1.8, 2.15], 20],
                               [1, [0.0, -1.3, 0.62], [0.1, 1.8, 2.15], 20]],
          "step": 2, "hand": 0.0, "look": "night"}]
story = {"slug": "ep87-motel-rooms", "title": "Ranking This Motel's Worst ROOMS", "made_for_kids": False,
         "premise": "creature test", "twist": "creature test", "world": "a motel office", "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
         "key_color": "#ff4fb8", "gap": 0.15, "tail": 0.25, "min_read": 0.15, "fade_in": False, "fade_out": False,
         "look": {"style": "closer", "flash_safe": True, "polish": True},
         "grade": {"saturation": 1.1, "contrast": 1.05, "vignette": 0.15, "bloom": 0.2, "grain": 0.008},
         "cast": cast, "lines": lines, "shots": shots, "acting": acting, "cues": [],
         "music": {"root": 40, "mode": "major", "bpm": 92, "seed": 87, "sections": [{"at": 0, "voices": ["pad"], "energy": 0.4}]},
         "sound": {"rev": 7, "floor": "wood", "sfx": []}, "rev": 7}
(HERE.parent / "story.json").write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
