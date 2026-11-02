"""One-off: turns the narrator lines in ../script.md into lines.json (caption, spoken) pairs.
Captions keep the script's CAPS key words; the spoken text lowercases them (names and sentence starts keep a capital)."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAMES = {"mum": "Mum", "kofi": "Kofi", "petra": "Petra", "ade": "Ade", "wednesday": "Wednesday", "mr": "Mr", "i": "I"}
OUT = []
for m in re.finditer(r"^- `(L\d+)` narrator: (.+)$", (HERE.parent / "script.md").read_text(), re.M):
    lid, body = m.group(1), m.group(2).strip()
    chunks = [c.strip() for c in body.split(" / ")]
    prev_end = True          # the line starts a sentence
    pairs = []
    for c in chunks:
        words = c.split(" ")
        sp = []
        for w in words:
            core = re.sub(r"[^A-Za-z']", "", w)
            if core.isupper() and len(core) > 1 or (core == "A" and False):
                low = w.lower()
                if core.lower() in NAMES:
                    low = low.replace(core.lower(), NAMES[core.lower()])
                if prev_end:
                    low = re.sub(r"[a-z]", lambda mm: mm.group(0).upper(), low, count=1)
                sp.append(low)
            else:
                sp.append(w)
            prev_end = bool(re.search(r"[.?!]\"?$", w))
        pairs.append([c, " ".join(sp)])
    OUT.append({"id": lid, "who": "narrator", "chunks": pairs})
FIX = {("L17", 2): 'And I heard Mum in my head, saying, "Halfway again?"', ("L66", 1): "about to say, \"Not bad.\""}
for ln in OUT:
    for k, ch in enumerate(ln["chunks"]):
        pass
for (lid, k), v in {("L17", 2): 'saying, "Halfway again?"', ("L66", 1): 'about to say, "Not bad."'}.items():
    next(l for l in OUT if l["id"] == lid)["chunks"][k][1] = v
(HERE / "lines.json").write_text(json.dumps(OUT, indent=1, ensure_ascii=False) + "\n")
print(len(OUT), "lines")
