"""Writes ../story.json for ep24 "wash-cycle". Run: python stories/ep24-wash-cycle/generator/make_story.py
(skeleton for the voice step; the shots, acting and sound are added below it)"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
story = {
    "slug": "ep24-wash-cycle", "title": "The dryer nobody started had a warm coat inside", "made_for_kids": False,
    "premise": "x", "twist": "x", "world": "x", "key_color": "#b99cf2", "gap": 0.14, "tail": 0.25,
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "cast": {}, "lines": lines, "shots": [{"id": "S01", "cam": [[0, [0, 0, 1], [1, 0, 1], 30]]}],
    "acting": {}, "cues": [], "fx": [],
}
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False))
