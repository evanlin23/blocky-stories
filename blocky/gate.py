"""The ship gate for one story: `python -m blocky gate <story>`. Open means ready to render on Actions and upload.

A story is open when all of these hold:
- `check` has no block (the rules in RULES.md that code can see)
- `stories/<story>/package.json` passes `lint_package` (below)
- the latest review by **standards** and by **critic** in `stories/<story>/reviews/` both say `Verdict: approve`

Reviews are markdown files named `r<round>-<reviewer>.md`, with the verdict on a line of its own:
`Verdict: approve`, `Verdict: revise` or `Verdict: kill`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from blocky.timeline import story_dir

REVIEWERS = ("standards", "critic")
VERDICT = re.compile(r"^\s*\**verdict\**\s*:\s*\**\s*(approve|revise|kill)\b", re.I | re.M)
REVIEW_FILE = re.compile(r"^r(\d+)-([a-z-]+)\.md$")

# words that never go in a title, description or pin (RULES.md, packaging)
BANNED = [
    (re.compile(r"\broblox\b", re.I), "the game's name"),
    (re.compile(r"\b(lego|minecraft|doors)\b", re.I), "another game or toy brand"),
    (re.compile(r"\btrue story\b|\bthis (really )?happened\b|\bbased on\b|\breal\b", re.I), "a claim that it's real"),
    (re.compile(r"\b(ai voice|no ai|made by hand|100% original|kokoro)\b", re.I), "a claim about how it's made"),
    (re.compile(r"\b(kid|kids|child|children|teen|teens|baby|school)\b", re.I), "a word that aims it at kids"),
    (re.compile(r"\b(slender ?man|scp)\b", re.I), "someone else's monster"),
    (re.compile("[–—]"), "an en or em dash"),
]
REQUIRED = ("title", "description", "pin")


def load_package(story: str) -> dict | None:
    p = story_dir(story) / "package.json"
    return json.loads(p.read_text()) if p.exists() else None


def lint_package(pkg: dict | None) -> list[tuple[str, str]]:
    from blocky import voicecheck

    if pkg is None:
        return [("block", "no package.json")]
    out = []
    for k in REQUIRED:
        if not str(pkg.get(k, "")).strip():
            out.append(("block", f"package.json: {k} is missing"))
    if pkg.get("made_for_kids", False) is not False:
        out.append(("block", "package.json: made_for_kids must be false"))
    title = pkg.get("title", "")
    if len(title) > 100:
        out.append(("block", f"package.json: the title is {len(title)} characters (YouTube's cap is 100)"))
    if len(pkg.get("description", "")) > 4900:
        out.append(("block", "package.json: the description is over 4,900 characters"))
    for k in REQUIRED:
        text = str(pkg.get(k, ""))
        for pat, what in BANNED:
            m = pat.search(text)
            if m:
                out.append(("block", f"package.json {k}: {m.group(0)!r} is {what}"))
    for r in voicecheck.voice_results([title], [pkg.get("description", ""), pkg.get("pin", "")]):
        if r.level != "pass":
            out.append((r.level, f"package.json: {r.message}"))
    if "made up" not in pkg.get("description", "").lower():
        out.append(("block", "package.json: the description must say it's made up"))
    return out


def verdicts(story: str) -> dict[str, tuple[int, str] | None]:
    """The latest (round, verdict) per reviewer."""
    d = story_dir(story) / "reviews"
    best: dict[str, tuple[int, str] | None] = {r: None for r in REVIEWERS}
    for f in sorted(d.glob("r*.md")) if d.exists() else []:
        m = REVIEW_FILE.match(f.name)
        if not m or m.group(2) not in best:
            continue
        rnd = int(m.group(1))
        v = VERDICT.search(f.read_text())
        cur = best[m.group(2)]
        if cur is None or rnd >= cur[0]:
            best[m.group(2)] = (rnd, v.group(1).lower() if v else "none")
    return best


def run(story: str, timeline: Path | None = None) -> tuple[bool, list[tuple[str, str]]]:
    from blocky import checks

    problems = [p for p in checks.run(story, timeline)]
    problems += lint_package(load_package(story))
    for who, v in verdicts(story).items():
        if v is None:
            problems.append(("block", f"no review by {who}"))
        elif v[1] != "approve":
            problems.append(("block", f"{who} (round {v[0]}) says {v[1]}"))
    return not any(p[0] == "block" for p in problems), problems
