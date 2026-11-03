"""Which stories get a proof render (proof.yml): the final's drawings at half size, before merge.

    python scripts/plan_proofs.py --story NAME                      # a dispatch: that story
    python scripts/plan_proofs.py --base SHA                         # a pull request: see `decide`

Prints `matrix=`, `stories=`, `any=` and `sha=` lines for $GITHUB_OUTPUT.

On a pull request a story is proofed when its film files differ from the base, both reviews approve (gate
open), it isn't held, `qa/<story>.json` doesn't already hold a passed proof check for the film as it stands, and
no live `proof-<story>` artifact was drawn from a commit with the same film files (GitHub API, GH_TOKEN). What the
latest push touched does not matter: a newer push that replaced a waiting run still gets the proof drawn.
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


def decide(film_vs_base: list[str], held: bool, gate: bool, merge_probs: list, drawn: str | None) -> str | None:
    """Why a story needs NO proof now (None: draw it). Pure, so it is tested without git or the network.
    A needed proof is never planned away by what the latest push touched (ep55, ep42: a main merge replaced a
    waiting run and the story was never drawn)."""
    if not film_vs_base:
        return "its film files match the base"
    if held:
        return "held, no proof"
    if not gate:
        return "gate closed (reviews or checks), no proof yet"
    if not merge_probs:
        return "its proof check already covers these film files"
    if drawn:
        return f"a proof of these film files already exists (commit {drawn[:8]})"
    return None


def drawn_sha(story: str, head: str, shas: list[str]) -> str | None:
    """The first commit in `shas` (newest first, the head_sha of the live proof-<story> artifacts) whose film
    files equal the head's: that artifact already shows this film."""
    for sha in shas:
        if sha == head:
            return sha
        ch = changed(sha, head)
        if ch is not None and not film_files(story, ch):
            return sha
    return None


def artifact_shas(story: str) -> list[str]:
    """head_sha of each live `proof-<story>` artifact, newest first (GH_TOKEN, GITHUB_REPOSITORY). The listing
    carries the run's commit, so no artifact is downloaded. Any failure: [] (draw rather than skip)."""
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo or not os.environ.get("GH_TOKEN"):
        return []
    r = subprocess.run(["gh", "api", f"repos/{repo}/actions/artifacts?name=proof-{story}&per_page=30"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"{story}: artifact list failed, drawing: {r.stderr.strip()[:200]}", file=sys.stderr)
        return []
    try:
        arts = json.loads(r.stdout).get("artifacts", [])
    except ValueError:
        return []
    return [x["workflow_run"]["head_sha"] for x in arts
            if not x.get("expired") and (x.get("workflow_run") or {}).get("head_sha")]


def plan(a) -> list[str]:
    """The stories to proof. A self-test (the workflow changed and no story did) is marked by `selftest`."""
    if a.story:
        return [a.story], False
    vs_base = changed(a.base) or []
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    todo = []
    for s in stories_in(vs_base):
        film = film_files(s, vs_base)
        held = bool((load_package(s) or {}).get("hold"))
        gate = bool(film) and not held and gate_open(s)
        probs = merge_problems(s, a.base) if gate else [("block", "not checked")]
        drawn = drawn_sha(s, head, artifact_shas(s)) if gate and probs else None
        why = decide(film, held, gate, probs, drawn)
        if why:
            print(f"{s}: {why}", file=sys.stderr)
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
    ap.add_argument("--before", default="")   # accepted and ignored: the push range no longer matters
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
