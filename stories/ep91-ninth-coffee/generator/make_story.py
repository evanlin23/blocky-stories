"""Writes ../story.json for "Each Coffee Makes Me TWICE As Fast" (ep91-ninth-coffee, batch 8).

Run from anywhere: python stories/ep91-ninth-coffee/generator/make_story.py
The words are in lines.json next to this file. Everything else is here: the cast, the shots and their cameras, the
acting, the cues set.py reads and the score.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
LOOP = 0.25

exec((HERE / "plan.py").read_text())   # cast, shots, acting, cues (the shot plan)

from blocky import timeline  # noqa: E402

look = {"fog": "#fff1d8", "fog_density": 0.003, "fog_start": 24.0, "sky": "#a9dcff", "exposure": 0.0,
        "flash_safe": True, "style": "closer",
        "polish": POLISH}
story = {
    "slug": "ep91-ninth-coffee",
    "title": "Each Coffee Makes Me TWICE As Fast ☕",
    "made_for_kids": False,
    "premise": "At my office every coffee makes you twice as fast and the speed never wears off. Most people stop at two. "
               "On a Friday with a report due I drink nine, while my best friend Kai, who sits one desk over, has been "
               "too busy for me all year.",
    "twist": "At nine cups I am fast enough to see the people who drank a tenth: frozen cyan streaks doing the whole "
             "office's work. Kai is one of them, finishing my work for a year. The rule never says what decaf does, so "
             "ten decafs bring him back down to normal speed, but they were every decaf in the building and I am stuck at nine.",
    "world": "one bright open-plan office on a high floor with cream desks, espresso chairs, big windows, plants and a "
             "shiny coffee machine with a coffee spout and a decaf spout",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#22e6ff",
    "gap": 0.12,
    "tail": LOOP,
    "min_read": 0.15,
    "fade_in": False,
    "fade_out": False,
    "look": look,
    "grade": {"shadows": [-0.01, 0.0, 0.04], "highlights": [0.03, 0.01, -0.02], "saturation": 1.12, "contrast": 1.05,
              "vignette": 0.15, "bloom": 0.2, "grain": 0.008, "red_line": 0.7},
    "cast": cast,
    "lines": lines,
    "shots": shots,
    "acting": acting,
    "cues": cues,
    "set_moves": SET_MOVES,
    "clip_heads": [],
    "clip_ok": CLIP_OK,
    "music": MUSIC,
    "sound": SOUND,
    "phonemes": {"Kai": "kˈI", "Kai's": "kˈIz"},
}

voice_p = HERE.parent / "voice-timings.json"
if voice_p.exists():
    voice = json.loads(voice_p.read_text())
    _tl0 = timeline.build({"name": "ep91-ninth-coffee", "lines": lines, "shots": [{"id": "S0"}], "gap": 0.12,
                           "tail": LOOP, "min_read": 0.15, "cast": cast}, voice)
    AT = timeline.resolver(_tl0["lines"], _tl0["duration"])
    for k in acting:
        acting[k].sort(key=lambda e: AT(e["at"] if "at" in e else e["from"]))
    cues.sort(key=lambda e: AT(e["at"]))
OUT.write_text(json.dumps(story, indent=1, ensure_ascii=False) + "\n")
print(f"{len(shots)} shots, {len(cues)} cues")
