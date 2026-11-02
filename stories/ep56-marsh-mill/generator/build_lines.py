"""Writes lines.json from the narration table (CAPS are the caption key words; the spoken text is derived: CAPS go
lower case, sentence starts and names are capitalised again). The text is the script's Narration section."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
script = (HERE.parent / "script.md").read_text()
body = script[script.index("L01. In this town"):]
T = dict(re.findall(r"^(L\d\d)\. (.*)$", body, re.M))
NAMES = {"i": "I", "i've": "I've", "i'd": "I'd", "i'm": "I'm", "win": "Win", "win's": "Win's", "ames": "Ames",
         "mr": "Mr", "monday": "Monday", "mondays": "Mondays", "tuesday": "Tuesday", "wednesday": "Wednesday",
         "thursday": "Thursday", "friday": "Friday", "saturday": "Saturday"}


def chunks(text):
    words = text.split()
    parts, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r"[.,?!]\"?$", w):
            parts.append(cur)
            cur = []
    if cur:
        parts.append(cur)
    out = []
    for p in parts:
        n = len(p)
        if n <= 3:
            out.append(p)
        elif n == 4:
            out += [p[:2], p[2:]]
        elif n == 5:
            out += [p[:2], p[2:]]
        elif n == 6:
            out += [p[:3], p[3:]]
        else:
            k = (n + 2) // 3
            sz = [n // k + (1 if i < n % k else 0) for i in range(k)]
            i = 0
            for z in sz:
                out.append(p[i:i + z])
                i += z
    # a one-word chunk joins its neighbour when the pair is short
    merged = []
    for c in out:
        if merged and len(c) == 1 and len(merged[-1]) <= 2 and not re.search(r"[.?!]$", merged[-1][-1]):
            merged[-1] += c
        else:
            merged.append(c)
    return [" ".join(c) for c in merged]


def spoken(chs):
    toks = []
    for c in chs:
        toks += c.split()
    out, start = [], True
    for w in toks:
        core = re.sub(r"[^A-Za-zÉé'\-]", "", w)
        low = w
        if len(core) > 1 and core.replace("-", "").replace("'", "").isalpha() and core.upper() == core:
            low = w.lower()
        elif re.match(r"^[A-Z]{2,}-[a-z]", w):
            low = w.split("-")[0].lower() + "-" + w.split("-", 1)[1]
        key = re.sub(r"[^a-z']", "", low.lower())
        if key in NAMES and low.lower().startswith(key):
            low = NAMES[key] + low[len(key):]
        if start and low[:1].isalpha():
            low = low[0].upper() + low[1:]
        start = bool(re.search(r"[.!?]\"?$", low))
        out.append(low)
    res, i = [], 0
    for c in chs:
        n = len(c.split())
        res.append(" ".join(out[i:i + n]))
        i += n
    return res


lines = []
for lid, text in T.items():
    ch = chunks(text)
    lines.append({"id": lid, "who": "narrator", "chunks": [[c, s] for c, s in zip(ch, spoken(ch))]})
(HERE / "lines.json").write_text(json.dumps(lines, indent=1, ensure_ascii=False) + "\n")
for l in lines:
    print(l["id"], " | ".join(c[1] for c in l["chunks"]))
