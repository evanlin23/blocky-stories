"""Shared helpers for the workflows: which stories exist, in what order, and what GitHub already holds for them."""

from __future__ import annotations

import json
import os
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


REPO = os.environ.get("GITHUB_REPOSITORY", "evanlin23/blocky-stories")


LEGACY = ROOT / "legacy"   # approved finals made in evanlin23/content (ep12, ep13), uploaded as they are


def film(story: str) -> dict | None:
    lf = LEGACY / f"{story}.mp4"
    if lf.exists():
        return {"id": None, "run_id": None, "url": f"https://github.com/{REPO}/blob/main/legacy/{story}.mp4",
                "created_at": "2099-01-01T00:00:00Z", "legacy": str(lf)}
    """The newest unexpired `film-<story>` artifact the render workflow saved: {id, run_id, url}, or None when the
    story has never been rendered (or its film expired after 90 days). The film's flash report says whether it may
    be uploaded."""
    r = subprocess.run(["gh", "api", f"repos/{REPO}/actions/artifacts?name=film-{story}&per_page=30"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    arts = [x for x in json.loads(r.stdout).get("artifacts", []) if not x.get("expired")]
    if not arts:
        return None
    x = max(arts, key=lambda x: x["created_at"])
    run = x["workflow_run"]["id"]
    return {"id": x["id"], "run_id": run, "url": f"https://github.com/{REPO}/actions/runs/{run}",
            "created_at": x["created_at"]}


QA = ROOT / "qa"   # qa/<story>.json: the final-film check (owner, 2026-11-03: "We should ensure everything is good before we publish.")


def qa_passed(story: str, f: dict | None) -> bool:
    """True when qa/<story>.json passed this exact film (its artifact id, or "legacy"). A re-render needs a new check.
    QA_REQUIRED=false turns the check off (emergencies only)."""
    if os.environ.get("QA_REQUIRED", "true").strip().lower() == "false":
        return True
    if not f:
        return False
    p = QA / f"{story}.json"
    if not p.exists():
        return False
    q = json.loads(p.read_text())
    return q.get("verdict") == "pass" and str(q.get("film")) == str(f.get("id") or "legacy")


# what changes the film: everything in the story folder but the words around it (package, reviews, notes)
NOT_FILM = ("package.json", "reviews", "notes", "*.md")


def changed_since(story: str, when: str) -> bool:
    """True when a file that shapes the film (story.json, set.py, voice-timings.json, ...) has a commit after
    `when` (ISO time), so a fix to a story with a film gets drawn again. Needs the full git history."""
    spec = [f"stories/{story}"] + [f":(exclude)stories/{story}/{x}" for x in NOT_FILM]
    r = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%cI", "--", *spec], capture_output=True, text=True)
    last = r.stdout.strip()
    if not last:
        return False
    import datetime as dt
    norm = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return norm(last) > norm(when)


def uploads() -> dict:
    return json.loads(UPLOADS.read_text()) if UPLOADS.exists() else {}
