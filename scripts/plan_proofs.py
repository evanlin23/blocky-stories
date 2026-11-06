"""Which stories get a proof render (proof.yml): the final's drawings at half size, before merge.

    python scripts/plan_proofs.py --story NAME                      # a dispatch: that story
    python scripts/plan_proofs.py --base SHA                         # a pull request: see `decide`

Prints `matrix=`, `stories=`, `any=` and `sha=` lines for $GITHUB_OUTPUT.

On a pull request a story is proofed when the PR itself changed its film files (`git diff base...HEAD`: from
where the branch left main, so a story main changed after that is not this PR's), both reviews approve (gate
open), it isn't held, `qa/<story>.json` doesn't already hold a passed proof check for the film as it stands, no
live `proof-<story>` artifact was drawn from a commit with the same film files, and no older proof run of this
commit is still drawing it (GitHub API, GH_TOKEN). What the latest push touched does not matter: a newer push
that replaced a waiting run still gets the proof drawn. A dispatch (`--story`) passes the same checks except the
diff (`--force true` draws it anyway). When the PR changes the proof workflow itself and no story, SELFTEST
(env PROOF_SELFTEST) is proofed so the change proves itself.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))          # scripts/ (stories.py), when loaded by path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))      # the repo (blocky/)

from stories import ROOT, gate_open  # noqa: E402

from blocky.gate import film_files, load_package, merge_problems  # noqa: E402

PROOF_FILES = (".github/workflows/proof.yml", "scripts/plan_proofs.py")


def changed(a: str, b: str = "HEAD") -> list[str] | None:
    """Files that differ between two commits (two-dot: the film as it stands in each)."""
    if not a or set(a) == {"0"}:
        return None
    r = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-only", a] + ([b] if b else []),
                       capture_output=True, text=True)
    return r.stdout.split() if r.returncode == 0 else None


def pr_changed(base: str) -> list[str] | None:
    """What the PR itself changed: `base...HEAD`, from the merge base. A two-dot diff against main's tip also lists
    every story main changed since the branch left it, and proofed them on the wrong PR (2026-11-04: dryer-nine was
    drawn on the batch10-scripts PR and on ep83's, warm-shoes on ep58's)."""
    return changed(f"{base}...HEAD", "") if base and set(base) != {"0"} else None


def stories_in(paths: list[str]) -> list[str]:
    out = []
    for p in paths:
        parts = p.split("/")
        if len(parts) > 2 and parts[0] == "stories" and parts[1] not in out \
                and (ROOT / "stories" / parts[1] / "story.json").exists():
            out.append(parts[1])
    return out


def decide(film_vs_base: list[str], held: bool, gate: bool, merge_probs: list, drawn: str | None,
           live: int | None = None) -> str | None:
    """Why a story needs NO proof now (None: draw it). Pure, so it is tested without git or the network.
    A needed proof is never planned away by what the latest push touched (ep55, ep42: a main merge replaced a
    waiting run and the story was never drawn). `live`: an older proof run of this commit that draws the story."""
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
    if live:
        return f"proof run {live} is already drawing this commit"
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


def drawing_run(story: str, own: int, runs: list[dict], jobs: dict[int, list[dict]]) -> tuple[int | None, bool]:
    """(an older live proof run of this commit that draws `story`, whether one is still planning). Pure.
    `runs` are proof.yml runs of the same head sha, `jobs[id]` their jobs (name, status). Only runs older than
    `own` count (run ids grow), so of two runs started together the older draws and the newer stands down."""
    planning = False
    for r in sorted(runs, key=lambda r: r["id"]):
        if r["id"] >= own or r.get("status") == "completed":
            continue
        js = jobs.get(r["id"], [])
        if any(j["name"] in (f"voice ({story})", f"assemble ({story})") or j["name"].startswith(f"draw ({story},")
               for j in js):
            return r["id"], False
        if not any(j["name"] == "plan" and j.get("status") == "completed" for j in js):
            planning = True
    return None, planning


def gh_json(path: str) -> dict | None:
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    try:
        return json.loads(r.stdout) if r.returncode == 0 else None
    except ValueError:
        return None


def live_run(story: str, sha: str, wait: float = 180, step: float = 15) -> int | None:
    """An older queued or running proof run of `sha` that draws `story` (GH_TOKEN, GITHUB_REPOSITORY,
    GITHUB_RUN_ID). While an older run is still planning, wait for it (two runs started seconds apart drew ep45
    twice). Any failure: None (draw rather than skip)."""
    repo, own = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_RUN_ID", "")
    if not repo or not os.environ.get("GH_TOKEN") or not own.isdigit():
        return None
    end = time.time() + wait
    while True:
        d = gh_json(f"repos/{repo}/actions/workflows/proof.yml/runs?head_sha={sha}&per_page=30")
        if d is None:
            return None
        runs = [r for r in d.get("workflow_runs", []) if r["id"] < int(own) and r.get("status") != "completed"]
        jobs = {}
        for r in runs:
            j = gh_json(f"repos/{repo}/actions/runs/{r['id']}/jobs?per_page=100")
            jobs[r["id"]] = (j or {}).get("jobs", [])
        rid, planning = drawing_run(story, int(own), runs, jobs)
        if rid or not planning or time.time() >= end:
            return rid
        time.sleep(step)


def why_not(s: str, film: list[str], base: str | None, head: str) -> str | None:
    held = bool((load_package(s) or {}).get("hold"))
    gate = bool(film) and not held and gate_open(s)
    probs = merge_problems(s, base) if gate else [("block", "not checked")]
    drawn = drawn_sha(s, head, artifact_shas(s)) if gate and probs else None
    live = live_run(s, head) if gate and probs and not drawn else None
    return decide(film, held, gate, probs, drawn, live)


def plan(a) -> list[str]:
    """The stories to proof. A self-test (the workflow changed and no story did) is marked by `selftest`."""
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if a.story:
        if str(getattr(a, "force", "")).lower() == "true":
            return [a.story], False
        # a dispatch has no base: it is held to everything but the diff (one proof per commit, reviews first)
        why = why_not(a.story, ["(dispatch)"], None, head)
        if why:
            note(f"{a.story}: {why} (dispatch with force to draw it anyway)")
            return [], False
        return [a.story], False
    vs_base = pr_changed(a.base) or []
    todo = []
    for s in stories_in(vs_base):
        why = why_not(s, film_files(s, vs_base), a.base, head)
        if why:
            note(f"{s}: {why}")
            continue
        todo.append(s)
    if not todo and not stories_in(vs_base) and any(p in vs_base for p in PROOF_FILES) and a.selftest:
        note(f"the proof workflow changed: proofing {a.selftest} as its own test")
        return [a.selftest], True
    return todo, False


def note(line: str) -> None:
    """To the log and the run's summary page, so a session sees why nothing was drawn without opening the log."""
    print(line, file=sys.stderr)
    p = os.environ.get("GITHUB_STEP_SUMMARY")
    if p:
        with open(p, "a") as f:
            f.write(f"- {line}\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--story", default="")
    ap.add_argument("--base", default="")
    ap.add_argument("--before", default="")   # accepted and ignored: the push range no longer matters
    ap.add_argument("--shards", type=int, default=8)
    ap.add_argument("--selftest", default=os.environ.get("PROOF_SELFTEST", ""))
    ap.add_argument("--force", default="false")   # a dispatch: "true" skips the gate and the one-proof-per-commit checks
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
