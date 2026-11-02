"""Writes ../story.json for ep29 "My new workmates call me the Spare" (script 2026-11-02).

Run from anywhere: python stories/ep29-ten-pin/generator/make_story.py
(first version: lines only, so the voice can be made while set.py is built)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
lines = lines + [{"id": "P99", "pause": 0.25, "chunks": []}]

story = {
    "slug": "ep29-ten-pin",
    "title": "My new workmates call me the Spare",
    "made_for_kids": False,
    "premise": "I'm new at the warehouse and my workmates take me to their Thursday bowling league at a tired old alley, where I'm called the Spare. Their score screen has a fifth row with no picture that scores on its own, and a bowler in our team shirt with a second head stacked on its own stands one lane nearer ours every week.",
    "twist": "The team was five until their friend Juno moved away. Every Thursday since, the fifth row bowled itself, and they called whatever bowled it the Spare. They gave me the name on purpose, to take its place, and when I bowl in the fifth row's turn my picture slides up into the fifth row and the thing is gone.",
    "world": "a tired eight-lane bowling alley on league nights: honey maple lanes, burgundy squiggle carpet, mustard seats, warm tungsten approaches, cold strip lights over the pin decks",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#3ad6c0",
    "gap": 0.12,
    "tail": 0,
    "look": {"fog": "#15131c", "fog_density": 0.03, "fog_start": 8.0, "sky": "#0c0b10", "exposure": 0.0},
    "grade": {"shadows": [-0.02, 0.0, 0.04], "highlights": [0.03, 0.01, -0.02], "saturation": 1.0, "contrast": 1.05,
              "vignette": 0.3, "bloom": 0.25, "grain": 0.012},
    "phonemes": {},
    "cast": {},
    "lines": lines,
    "shots": [{"id": "S01", "cam": [[0, [0, -3, 1.5], [0, 5, 1.0], 28]], "step": 2}],
    "acting": {}, "cues": [], "fx": [],
    "music": {"root": 50, "mode": "dorian", "bpm": 92, "seed": 29,
              "sections": [{"at": 0, "voices": ["drone", "pad"], "energy": 0.4}]},
    "sound": {"floor": "wood", "steps_db": -22, "ambience": [], "sfx": []},
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT)
