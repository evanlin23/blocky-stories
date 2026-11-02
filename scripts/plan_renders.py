"""Which stories need a final render: the gate is open and there's no film artifact yet.

    python scripts/plan_renders.py [--story NAME] [--shards 16]

Prints `matrix=<json>` and `stories=<json>` lines for $GITHUB_OUTPUT.
"""

from __future__ import annotations

import argparse
import json
import sys

from stories import all_stories, film, gate_open, uploads

ap = argparse.ArgumentParser()
ap.add_argument("--story", default="")
ap.add_argument("--shards", type=int, default=16)
a = ap.parse_args()

if a.story:
    todo = [a.story]
else:
    done = uploads()
    todo = [s for s in all_stories() if s not in done and film(s) is None and gate_open(s)]
print(f"to render: {todo or 'nothing'}", file=sys.stderr)
include = [{"story": s, "shard": k} for s in todo for k in range(a.shards)]
print("matrix=" + json.dumps({"include": include}))
print("stories=" + json.dumps(todo))
print("any=" + ("true" if todo else "false"))
