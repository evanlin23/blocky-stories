"""Which stories need a final render: the gate is open and there's no film artifact yet.

    python scripts/plan_renders.py [--story NAME] [--shards 32]

Prints `matrix=`, `stories=`, `any=`, `more=` and the slot lines `a=`, `b=` (the first and second story, or empty) for
$GITHUB_OUTPUT. For each slot s: `shards_s=` (JSON list of the shards still to draw), `todo_s=` ('true' when there are
any; 'false' means every shard is already drawn and only assemble runs) and `reuse_s=` (JSON {shard: artifact id} of
shards drawn by an earlier run at the same inputs, which assemble downloads).

A story is drawn only after a passed proof (see render_plan.skip_reason). REQUIRE_PROOF=false, or --require-proof false,
turns that off (an explicit --story is never held back by it). Why each story is skipped goes to stderr.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

from stories import REPO, ROOT, all_stories, changed_since, film, gate_open, uploads   # (puts the repo root on sys.path)
from render_plan import pick_shards, shard_name, skip_reason
from upload import queue

from blocky.gate import _changed, film_files, load_package

ap = argparse.ArgumentParser()
ap.add_argument("--story", default="")
ap.add_argument("--shards", type=int, default=32)
ap.add_argument("--max", type=int, default=2)   # stories per run, clamped to 2 below: render.yml has two slots (a, b), each story's assemble waits only for its own shards; the again job starts the next run for the rest
ap.add_argument("--require-proof", default=os.environ.get("REQUIRE_PROOF", "false"))   # "false" draws stories that have no passed proof
a = ap.parse_args()
require_proof = a.require_proof.strip().lower() != "false"


def proof_skip(s):
    """Why `s` has no passed proof (or None). Reads qa/<s>.json and the film files changed since its sha."""
    p = ROOT / "qa" / f"{s}.json"
    qa = json.loads(p.read_text()) if p.exists() else None
    since = _changed(qa["sha"], "HEAD", s) if qa and qa.get("sha") else None
    return skip_reason(s, qa, since)


def drawn_shards(s, n):
    """Shards of `s` an earlier run drew and kept, when nothing that shapes the picture changed since that run's commit
    (the story's film files, the engine in blocky/, assets/)."""
    arts = []
    for k in range(n):   # the artifacts API matches a name exactly, so ask for each shard's
        r = subprocess.run(["gh", "api", f"repos/{REPO}/actions/artifacts?name={shard_name(s, k, n)}&per_page=30"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            arts += json.loads(r.stdout).get("artifacts", [])
    cache = {}
    def fresh(x):
        sha = x["workflow_run"]["head_sha"]
        if sha not in cache:
            d = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-only", sha, "HEAD", "--", "blocky", "assets", f"stories/{s}"],
                               capture_output=True, text=True)
            names = d.stdout.split()
            cache[sha] = d.returncode == 0 and not [q for q in names if q.startswith(("blocky/", "assets/"))] and not film_files(s, names)
        return cache[sha]
    return pick_shards(s, n, arts, fresh)

if a.story:
    todo = [a.story]
else:
    done = uploads()
    def needs(s):   # never rendered, or fixed since its film was made (a flash redraw, a re-voice)
        f = film(s)
        return f is None or changed_since(s, f["created_at"])
    held = lambda s: bool((load_package(s) or {}).get("hold"))   # held or killed: don't spend runner hours on it
    order = [s for s in queue() if s in all_stories()] + [s for s in all_stories() if s not in queue()]
    todo = []
    for s in order:
        if s in done or held(s) or not needs(s) or not gate_open(s):
            continue
        why = proof_skip(s) if require_proof else None
        if why:
            print(f"skipped {s}: {why}", file=sys.stderr)
            continue
        todo.append(s)
MAX = min(a.max, 2)   # render.yml has two slots: raising --max must never silently drop a third story (it goes to `more`)
todo, later = todo[:MAX], todo[MAX:]   # the upload queue goes first, then the rest oldest first
print(f"to render: {todo or 'nothing'}" + (f"; next run: {later}" if later else ""), file=sys.stderr)
slots = {}
for key, st in zip("ab", todo + [None] * 2):
    reuse, missing = drawn_shards(st, a.shards) if st else ({}, [])
    if reuse:
        print(f"{st}: reusing {len(reuse)} of {a.shards} drawn shards, drawing {missing or 'none'}", file=sys.stderr)
    slots[key] = (reuse, missing)
include = [{"story": s, "shard": k} for key, s in zip("ab", todo) for k in slots[key][1]]
print("matrix=" + json.dumps({"include": include}))
print("stories=" + json.dumps(todo))
print("any=" + ("true" if todo else "false"))
print("more=" + ("true" if later else "false"))
print("a=" + (todo[0] if len(todo) > 0 else ""))
print("b=" + (todo[1] if len(todo) > 1 else ""))
for key, (reuse, missing) in slots.items():
    print(f"shards_{key}=" + json.dumps(missing))
    print(f"todo_{key}=" + ("true" if missing else "false"))
    print(f"reuse_{key}=" + json.dumps({str(k): v for k, v in reuse.items()}))
