"""Shared helpers for the workflows: which stories exist, in what order, and what GitHub already holds for them."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
UPLOADS = ROOT / "uploads.json"


def all_stories() -> list[str]:
    """Story folders in upload order: by the episode number in the slug (ep14-... before ep15-...)."""
    out = []
    for d in (ROOT / "stories").iterdir():
        sj = d / "story.json"
        if d.is_dir() and sj.exists():
            slug = json.loads(sj.read_text()).get("slug", d.name)
            m = re.match(r"ep(\d+)", slug)
            out.append((int(m.group(1)) if m else 10 ** 6, d.name))
    return [name for _, name in sorted(out)]


def slug(story: str) -> str:
    return json.loads((ROOT / "stories" / story / "story.json").read_text()).get("slug", story)


def gate_open(story: str) -> bool:
    """`python -m blocky gate` (it rebuilds the timeline first, so the caption checks run too)."""
    r = subprocess.run([sys.executable, "-m", "blocky", "gate", story], cwd=ROOT, capture_output=True, text=True)
    return r.returncode == 0


def release_tag(story: str) -> str:
    return f"render-{story}"


def release_assets(story: str) -> list[str] | None:
    """Asset names on the story's render release, or None when there's no release."""
    r = subprocess.run(["gh", "release", "view", release_tag(story), "--json", "assets,isPrerelease"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    d = json.loads(r.stdout)
    if d.get("isPrerelease"):   # a failed render (flash bar) is kept as a prerelease for the record
        return []
    return [a["name"] for a in d["assets"]]


def uploads() -> dict:
    return json.loads(UPLOADS.read_text()) if UPLOADS.exists() else {}
