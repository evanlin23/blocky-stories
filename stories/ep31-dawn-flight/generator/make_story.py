import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
lines = json.loads((HERE / "lines.json").read_text())
out = []
for ln in lines:
    out.append(ln)
    if ln["id"] == "L49":
        out.append({"id": "P01", "pause": 0.7, "chunks": []})
    if ln["id"] == "L58":
        out.append({"id": "P02", "pause": 0.8, "chunks": []})
story = {"slug": "ep31-dawn-flight", "title": "stub", "made_for_kids": False, "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
         "gap": 0.12, "tail": 0.9, "cast": {"me": {"age": "adult", "skin": "#f1c9a0", "shirt": "#d4a017", "pants": "#222222"}},
         "lines": out, "shots": [{"id": "S01", "cam": [[0, [0, -3, 1], [0, 0, 1], 30]]}]}
(HERE.parent / "story.json").write_text(json.dumps(story, indent=1))
