"""CREATURE TEST ONLY (builder phase 1): writes ../story.json with one shot of Hal at full height (the L37 reveal).
The real make_story.py replaces this in step 2."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
lines = json.loads((HERE / "lines.json").read_text())
cast = {
    "hal": {"age": "adult", "skin": "#e8b98f", "shirt": "#e0b23a", "pattern": "solid", "pants": "#6b5a3a",
            "shoes": "#3a2a20", "sleeves": "long", "collar": "#ffffff", "hair": "swoop", "hair_c": "#4a3a2a",
            "extras": ["tie"], "extra_c": "#2cc7c9", "height": 1.38, "width": 0.8,
            "face": {"eyes": "round", "brows": True, "ink": "#24131f", "eye_scale": 1.25}},
}
acting = {"hal": [{"at": 0, "pos": [0.0, 2.1, 0], "yaw": 0, "expr": "blank", "blink": False, "blend": 0,
                   "lean": 24, "head": [0, 14], "arms": [0, 0], "side": [0, 0], "hidden": False}]}
shots = [{"id": "S37", "cam": [[0, [0.3, -1.9, 0.6], [0.0, 2.0, 1.35], 24],
                               [1, [0.3, -1.9, 0.6], [0.0, 2.0, 1.35], 24]],
          "step": 2, "hand": 0.0, "look": "night"}]
story = {"slug": "ep87-motel-rooms", "title": "Ranking This Motel's Worst ROOMS", "made_for_kids": False,
         "premise": "creature test", "twist": "creature test", "world": "a motel office", "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
         "key_color": "#ff4fb8", "gap": 0.15, "tail": 0.25, "min_read": 0.15, "fade_in": False, "fade_out": False,
         "look": {"style": "closer", "flash_safe": True, "polish": True},
         "grade": {"saturation": 1.1, "contrast": 1.05, "vignette": 0.15, "bloom": 0.2, "grain": 0.008},
         "cast": cast, "lines": lines, "shots": shots, "acting": acting, "cues": [],
         "music": {"root": 40, "mode": "major", "bpm": 92, "seed": 87, "sections": [{"at": 0, "voices": ["pad"], "energy": 0.4}]},
         "sound": {"rev": 1, "floor": "wood", "sfx": []}, "rev": 1}
(HERE.parent / "story.json").write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
