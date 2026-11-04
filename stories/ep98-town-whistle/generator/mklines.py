"""One-off: reads the narration block of ../script.md and writes lines.json (chunks of at most 3 words)."""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
txt = (HERE.parent / "script.md").read_text()
sec = txt.split("## The narration")[1].split("(The 0.7 s")[0]
out = []
for m in re.finditer(r"^- (L\d+): (.*)$", sec, re.M):
    lid, body = m.group(1), m.group(2).replace("HAL", "ARLO")
    chunks = []
    for part in body.split(" / "):
        w = part.split()
        n = len(w)
        k = 1 if n <= 3 else 2 if n <= 6 else 3
        sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
        i = 0
        for sz in sizes:
            cap = " ".join(w[i:i + sz]); i += sz
            chunks.append([cap, cap.lower()])
    out.append({"id": lid, "who": "narrator", "chunks": chunks})
    if lid == "L29":
        out.append({"id": "P01", "pause": 0.7, "chunks": []})
    if lid == "L52":
        out.append({"id": "P02", "pause": 0.7, "chunks": []})
(HERE / "lines.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
for l in out:
    if "pause" in l: print(l["id"], "pause"); continue
    print(l["id"], " | ".join(f"{i}:{c[0]}" for i, c in enumerate(l["chunks"])))
