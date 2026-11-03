"""Writes ../story.json for ep90 (creature-test stage: one line, one shot). Run: python stories/ep90-closing-page/generator/make_story.py"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "story.json"
story = {
    "slug": "ep90-closing-page", "title": "Nobody Answers The Closing PAGE", "made_for_kids": False,
    "premise": "creature test", "twist": "creature test", "world": "a supermarket back room",
    "key_color": "#8a4fd1", "gap": 0.15, "tail": 0.9, "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "look": {"flash_safe": True, "polish": True, "fog": "#e8dcc4", "fog_density": 0.006, "fog_start": 12.0,
             "sky": "#cbbfa6", "exposure": -0.2},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.03, 0.012, -0.02], "saturation": 1.08, "contrast": 1.04,
              "vignette": 0.2, "bloom": 0.2, "grain": 0.008},
    "cast": {},
    "lines": [{"id": "L26", "who": "narrator", "chunks": [["He beeped", "He beeped"], ["at my FACE,", "at my face,"]]}],
    "shots": [{"id": "S26", "n": 1, "cam": [[0, [0.3, -1.2, 1.2], [0, 5.0, 1.75], 26],
                                            [1, [0.2, 0.1, 1.3], [0, 5.0, 1.85], 26]], "hand": 0.003}],
    "acting": {}, "cues": [],
    "music": {"root": 56, "mode": "major", "bpm": 112, "seed": 9, "sections": [{"at": 0, "voices": ["pad"], "energy": 0.3}]},
    "sound": {"floor": "concrete", "rev": 1},
}
OUT.write_text(json.dumps(story, indent=1))
