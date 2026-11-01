"""Write like a person (house rule 9): words and shapes that make text read as AI-written. Run on every caption,
spoken line, title, description and pin."""

from __future__ import annotations

import re
from dataclasses import dataclass

AI_WORDS = ("delve", "tapestry", "testament", "unveil", "dive into", "deep dive", "journey", "embark",
            "fascinating", "captivating", "mesmerizing", "ever wondered", "let's explore",
            "in a world where", "buckle up", "game-changer", "game changer")
AI_PATTERNS = [
    (re.compile(r";"), "a semicolon"),
    (re.compile(r"\bnot (just|only)\b", re.I), "'not just' / 'not only'"),
    (re.compile(r"\bno [\w-]+, no [\w-]+", re.I), "a 'no X, no Y' line"),
    (re.compile(r"\([^()]*,[^()]*\)"), "a list in parentheses"),
    (re.compile(r"\b(\w+) [\w-]+\. \1 [\w-]+\.", re.I), "a slogan-style repeat ('Real data. Real sound.')"),
    (re.compile(r"^[A-Z][\w' ]{0,25}: "), "a 'Label: ...' opener"),
]
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")


@dataclass
class Result:
    check: str
    level: str   # pass | warn | block
    message: str


def voice_results(screen: list[str], prose: list[str]) -> list[Result]:
    out = []
    for text in screen + prose:
        low = text.lower()
        hits = [w for w in AI_WORDS if re.search(rf"\b{re.escape(w)}\b", low)]
        if "—" in text:
            hits.append("an em dash")
        if hits:
            out.append(Result("voice", "block", f"reads as AI-written ({', '.join(hits)}): {text[:80]!r}"))
        if len(EMOJI.findall(text)) > 2:
            out.append(Result("voice", "warn", f"stacked emojis: {text[:80]!r}"))
    sentences = [s.strip() for text in prose for s in re.split(r"(?<=[.?!])\s+|\s+\|\s+", text) if len(s.split()) >= 4]
    for s in sorted({s for s in sentences if sentences.count(s) > 1}):
        out.append(Result("voice", "warn", f"said twice: {s[:80]!r}"))
    for text in prose:
        for pattern, what in AI_PATTERNS:
            if pattern.search(text):
                out.append(Result("voice", "warn", f"{what} reads as AI-written; say it plainly: {text[:80]!r}"))
    return out or [Result("voice", "pass", "text reads as written by a person")]
