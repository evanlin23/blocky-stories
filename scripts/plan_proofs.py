"""Which stories get a proof render (proof.yml): the final's drawings at half size, before merge.

    python scripts/plan_proofs.py --story NAME                      # a dispatch: that story
    python scripts/plan_proofs.py --base SHA [--before SHA]          # a pull request: see `wanted`

Prints `matrix=`, `stories=`, `any=` and `sha=` lines for $GITHUB_OUTPUT.

On a pull request a story is proofed when its film files differ from the base, both reviews approve (gate
open), this push changed its film files or its reviews (so a push of something else doesn't draw it again), and
`qa/<story>.json` doesn't already hold a passed proof check for the film as it stands.
When the PR changes the proof workflow itself and no story, SELFTEST (env PROOF_SELFTEST) is proofed so the
change proves itself.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))          # scripts/ (stories.py), when loaded by path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))      # the repo (blocky/)

from stories import ROOT, gate_open  # noqa: E402

from blocky.gate import film_files, load_package, merge_problems  # noqa: E402

PROOF_FILES = (".github/workflows/proof.yml", "scripts/plan_proofs.py")


def changed(a: str, b: str = "HEAD") -> list[str] | None:
    if not a or set(a) == {"0"}:
        return None
    r = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-only", a, b], capture_output=True, text=True)
    return r.stdout.split() if r.returncode == 0 else None


def stories_in(paths: list[str]) -> list[str]:
    out = []
    for p in paths:
        parts = p.split("/")
        if len(parts) > 2 and parts[0] == "stories" and parts[1] not in out \
                and (ROOT / "stories" / parts[1] / "story.json").exists():
            out.append(parts[1])
    return out


def wanted(story: str, vs_base: list[str], in_push: list[str] | None) -> bool:
    """Film files differ from the base, and this push touched the film or the reviews (None: a new PR or an
    unknown range, so yes)."""
    if not film_files(story, vs_base):
        return False
    if in_push is None:
        return True
    return bool(film_files(story, in_push)) or any(p.startswith(f"stories/{story}/reviews/") for p in in_push)


def plan(a) -> list[str]:
    """The stories to proof. A self-test (the workflow changed and no story did) is marked by `selftest`."""
    if a.story:
        return [a.story], False
    vs_base = changed(a.base) or []
    in_push = changed(a.before)
    todo = []
    for s in stories_in(vs_base):
        if not wanted(s, vs_base, in_push):
            continue
        if (load_package(s) or {}).get("hold"):
            print(f"{s}: held, no proof", file=sys.stderr)
            continue
        if not gate_open(s):
            print(f"{s}: gate closed (reviews or checks), no proof yet", file=sys.stderr)
            continue
        if not merge_problems(s, a.base):   # a passed proof check already covers this film: nothing to redraw
            print(f"{s}: its proof check already covers these film files", file=sys.stderr)
            continue
        todo.append(s)
    if not todo and not stories_in(vs_base) and any(p in vs_base for p in PROOF_FILES) and a.selftest:
        print(f"the proof workflow changed: proofing {a.selftest} as its own test", file=sys.stderr)
        return [a.selftest], True
    return todo, False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--story", default="")
    ap.add_argument("--base", default="")
    ap.add_argument("--before", default="")
    ap.add_argument("--shards", type=int, default=8)
    ap.add_argument("--selftest", default=os.environ.get("PROOF_SELFTEST", ""))
    a = ap.parse_args()
    todo, selftest = plan(a)
    print(f"to proof: {todo or 'nothing'}", file=sys.stderr)
    sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    print("matrix=" + json.dumps({"include": [{"story": s, "shard": k} for s in todo for k in range(a.shards)]}))
    print("stories=" + json.dumps(todo))
    print("any=" + ("true" if todo else "false"))
    # a self-test proves the workflow, not the story: its verdict is reported, not enforced
    print("selftest=" + ("true" if selftest else "false"))
    print("sha=" + sha)
