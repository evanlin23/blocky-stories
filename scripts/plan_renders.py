"""Which stories need a final render: the gate is open and there's no film artifact yet.

    python scripts/plan_renders.py [--story NAME] [--shards 16]

Prints `matrix=<json>` and `stories=<json>` lines for $GITHUB_OUTPUT.
"""

from __future__ import annotations

import argparse
import json
import sys

from stories import all_stories, changed_since, film, gate_open, uploads
from upload import queue

from blocky.gate import load_package

ap = argparse.ArgumentParser()
ap.add_argument("--story", default="")
ap.add_argument("--shards", type=int, default=16)
ap.add_argument("--max", type=int, default=15)   # GitHub caps a matrix at 256 jobs: 15 stories x 16 shards = 240
a = ap.parse_args()

if a.story:
    todo = [a.story]
else:
    done = uploads()
    def needs(s):   # never rendered, or fixed since its film was made (a flash redraw, a re-voice)
        f = film(s)
        return f is None or changed_since(s, f["created_at"])
    held = lambda s: bool((load_package(s) or {}).get("hold"))   # held or killed: don't spend runner hours on it
    order = [s for s in queue() if s in all_stories()] + [s for s in all_stories() if s not in queue()]
    todo = [s for s in order if s not in done and not held(s) and needs(s) and gate_open(s)]
todo, later = todo[:a.max], todo[a.max:]   # the upload queue goes first, then the rest oldest first
print(f"to render: {todo or 'nothing'}" + (f"; next run: {later}" if later else ""), file=sys.stderr)
include = [{"story": s, "shard": k} for s in todo for k in range(a.shards)]
print("matrix=" + json.dumps({"include": include}))
print("stories=" + json.dumps(todo))
print("any=" + ("true" if todo else "false"))
print("more=" + ("true" if later else "false"))
