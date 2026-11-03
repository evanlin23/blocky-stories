"""Writes ../story.json for ep95-corn-maze (WIP scaffold for the creature test still; the full shot plan comes later).

Run: python stories/ep95-corn-maze/generator/make_story.py
Places (metres): the maze field is centred on the origin, 40 x 64 (set.py layouts); the entrance close-up is built at
x = 200 (lantern at 200.3, 0, 2.8). Camera lens 34 everywhere so the marker panel (parented to the camera) fits.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())

story = {
    "slug": "ep95-corn-maze",
    "title": "Nobody Gets Lost In Our CORN Maze",
    "made_for_kids": False,
    "premise": "At our corn maze, if the lanterns go out while you're still inside, you stay the night, and nobody has, because a voice in the corn tells lost people where to turn.",
    "twist": "The voice is the maze itself; its paths are a huge face, and the farmer June stayed on her last night to say goodbye.",
    "world": "a farm's corn maze on its last night: gold corn, iron lanterns, silver-blue moonlight",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ff7a1f",
    "gap": 0.15,
    "tail": 0.25,
    "fade_in": False,
    "fade_out": False,
    "look": {"style": "closer", "polish": True, "flash_safe": True, "fog": "#4d6aa8", "fog_density": 0.0,
             "fog_start": 500.0, "sky": "#4d6aa8", "exposure": 0.3},
    "grade": {"shadows": [0.0, 0.0, 0.03], "highlights": [0.0, 0.0, 0.0], "saturation": 1.05, "contrast": 1.05,
              "vignette": 0.25, "bloom": 0.3, "grain": 0.009},
    "layouts": ["face", "entrance"],
    "shot_layout": {"S01": "entrance", "S34": "face", "S35": "face"},
    "shot_look": {"S01": "dusk", "S34": "moon", "S35": "moon"},
    "cast": {"june": {"age": "adult", "skin": "#e0b48c", "shirt": "#d8443a", "pattern": "plaid", "pants": "#3d5a80",
                      "shoes": "#3a2a20", "sleeves": "long", "hair": "long", "hair_c": "#a8a8a8", "hat": "bucket",
                      "hat_c": "#d8c070", "face": {"eyes": "round", "brows": True, "ink": "#24131f"}}},
    "lines": lines,
    "shots": [
        {"id": "S01", "cam": [[0, [200.3, -2.6, 2.7], [200.3, 0, 2.85], 34], [1, [200.3, -2.0, 2.75], [200.3, 0, 2.85], 34]], "step": 2},
        {"id": "S34", "at": "L34", "cam": [[0, [0, -0.3, 98], [0, 0, 0], 34], [1, [0, -0.2, 97.5], [0, 0, 0], 34]], "step": 2},
        {"id": "S35", "at": "L34+1.8", "cam": [[0, [0, -0.2, 97.5], [0, 0, 0], 34]], "step": 2},
    ],
    "acting": {"june": [{"at": 0, "hidden": True, "blend": 0}]},
    "cues": [{"at": 0, "name": "lanterns", "n": 12}],
    "music": {"root": 43, "mode": "mixolydian", "bpm": 70, "seed": 95,
              "sections": [{"at": 0, "voices": ["drone", "pad"], "energy": 0.3}]},
    "sound": {"floor": "grass", "steps_db": -20, "rev": 1, "ambience": [{"kind": "crickets", "from": 0, "to": "end", "lufs": -38}]},
    "rev": 2,
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False))
print("wrote", OUT)
