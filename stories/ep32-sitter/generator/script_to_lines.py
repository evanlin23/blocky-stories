"""One-off: turns the narrator lines in ../script.md into lines.json (caption, spoken) pairs.
Captions keep the script's CAPS key words; the spoken text lowercases them (names and sentence starts keep a capital)."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAMES = {"mum": "Mum", "kofi": "Kofi", "petra": "Petra", "wednesday": "Wednesday", "i": "I"}
OUT = []
for m in re.finditer(r"^- `(L\d+b?)` narrator: (.+)$", (HERE.parent / "script.md").read_text(), re.M):
    lid, body = m.group(1), m.group(2).strip()
    chunks = [c.strip() for c in body.split(" / ")]
    prev_end = True          # the line starts a sentence
    pairs = []
    for c in chunks:
        sp = []
        for w in c.split(" "):
            core = re.sub(r"[^A-Za-z']", "", w)
            if core.isupper() and len(core) > 1:
                low = w.lower()
                if core.lower() in NAMES:
                    low = low.replace(core.lower(), NAMES[core.lower()])
                if prev_end or w.startswith('"'):
                    low = re.sub(r"[a-z]", lambda mm: mm.group(0).upper(), low, count=1)
                sp.append(low)
            else:
                sp.append(w)
            prev_end = bool(re.search(r"[.?!]\"?$", w))
        pairs.append([c, " ".join(sp)])
    OUT.append({"id": lid, "who": "narrator", "chunks": pairs})


def split3(cap, spk):
    cw, sw = cap.split(" "), spk.split(" ")
    n = len(cw)
    if n <= 3 or len(sw) != n:
        return [[cap, spk]]
    k = -(-n // 3)
    base, extra = divmod(n, k)
    sizes = [base + (1 if i >= k - extra else 0) for i in range(k)]
    out, i = [], 0
    for z in sizes:
        out.append([" ".join(cw[i:i + z]), " ".join(sw[i:i + z])])
        i += z
    return out


for ln in OUT:
    ln["chunks"] = [p for ch in ln["chunks"] for p in split3(*ch)]
(HERE / "lines.json").write_text(json.dumps(OUT, indent=1, ensure_ascii=False) + "\n")
print(len(OUT), "lines")
# the speech check hears "Bare" as "bear": a comma gives it a pause to stand on
for ln in OUT:
    if ln["id"] == "L12":
        ln["chunks"][0][1] = "Bare pine,"
(HERE / "lines.json").write_text(json.dumps(OUT, indent=1, ensure_ascii=False) + "\n")
