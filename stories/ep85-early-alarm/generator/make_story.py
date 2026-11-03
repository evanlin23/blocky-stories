"""Writes ../story.json for ep85-early-alarm. WIP: the creature test still only (one shot, the eye opening on me).

Run: python stories/ep85-early-alarm/generator/make_story.py
Places (metres, z up): the Sun sits at (0, 7, 2.1); its front face is y = 6.175. Acting yaw: 0 faces -y, 180 faces +y.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "story.json"
lines = json.loads((HERE / "lines.json").read_text())
ids = [l["id"] for l in lines]
lines.insert(ids.index("L38"), {"id": "P01", "pause": 0.6, "chunks": []})     # the drop before the shed door
ids = [l["id"] for l in lines]
lines.insert(ids.index("L64a"), {"id": "P02", "pause": 0.5, "chunks": []})    # the held beat: two alarms

me = {"age": "teen", "skin": "#f1c9a0", "shirt": "#1f2f6a", "pattern": "solid", "pants": "#6a6fa8", "shoes": "#f4f4f2",
      "sleeves": "long", "hair": "spiky", "hair_c": "#5a3a22", "extras": ["hooddown"], "extra_c": "#1f2f6a",
      "face": {"eyes": "round", "brows": True, "ink": "#24131f"}}

story = {
    "slug": "ep85-early-alarm",
    "title": "Don't Get Up Before The ALARM",
    "made_for_kids": False,
    "premise": "In our town, if your alarm rings an hour early you lie still until it is light; my dad is always up first, and when his back goes out my alarm rings at five.",
    "twist": "The sun does not rise: every night it comes down to sleep in our backyard, and every morning someone who has seen it has to wake it and winch it back up. For thirty years that was my dad.",
    "world": "a small suburban backyard at five in the morning: a frost-free round bare patch, a barn-red shed with a pulley on its roof and a winch inside, a rope across the lawn to a garage-sized glowing sleeping sun",
    "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
    "key_color": "#ffb000",
    "gap": 0.12,
    "tail": 0.25,
    "look": {"fog": "#2a2f7a", "fog_density": 0.012, "fog_start": 8.0, "sky": "#2b2f7e", "exposure": -0.3,
             "flash_safe": True, "polish": True},
    "grade": {"shadows": [0.0, 0.0, 0.06], "highlights": [0.03, 0.0, -0.03], "saturation": 1.1, "contrast": 1.06,
              "vignette": 0.3, "bloom": 0.3, "grain": 0.01},
    "cast": {"me": me},
    "lines": lines,
    "shots": [
        {"id": "S45", "cam": [[0, [0.0, 1.5, 1.8], [0.0, 4.4, 1.8], 19], [1, [-1.0, 1.9, 1.5], [-0.05, 4.4, 1.75], 19]],
         "step": 2, "hand": 0.0, "note": "the eye opens an inch from my face"}
    ],
    "acting": {"me": [{"at": 0, "pos": [-0.72, 3.3, 0], "yaw": 45, "head": [-10, 0], "expr": "scared"}]},
    "cues": [{"at": "L44", "name": "eye", "open": 1.0}],
    "fx": [],
    "music": {"root": 46, "mode": "major", "bpm": 84, "seed": 85,
              "sections": [{"at": 0, "voices": ["drone", "pad"], "energy": 0.3}]},
    "sound": {"floor": "grass", "steps_db": -20, "rev": 1, "ambience": [{"kind": "crickets", "from": 0, "to": "end", "lufs": -34}]},
}
story["rev"] = 3
OUT.write_text(json.dumps(story, indent=1))
print("wrote", OUT)
