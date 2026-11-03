"""Pure decisions for plan_renders.py (no git, no network): which stories may be drawn as a final, and which shards of
a story are already drawn. The glue that looks things up lives in plan_renders.py; these are tested in test_render_plan.py."""

from __future__ import annotations

from typing import Callable

from blocky.gate import proof_problems


def skip_reason(story: str, qa: dict | None, changed_since_proof: list[str] | None) -> str | None:
    """Why a story is not drawn as a final yet, or None when it may be. It may be drawn when its final qa already
    passed, or its proof qa passed at a commit with no film file changed after it (the same check `test` makes)."""
    if qa and qa.get("stage") != "proof" and qa.get("verdict") == "pass":
        return None
    problems = proof_problems(story, qa, changed_since_proof)
    return problems[0][1] if problems else None


def shard_name(story: str, k: int, n: int) -> str:
    """The artifact a draw shard keeps. The count is in the name so shards cut for 16 are never taken for ones cut for 32."""
    return f"frames-{story}-{k}of{n}"


def pick_shards(story: str, n: int, artifacts: list[dict], fresh: Callable[[dict], bool]) -> tuple[dict[int, int], list[int]]:
    """({shard: artifact id} to reuse, [shards left to draw]). `artifacts` are GitHub's artifact records (name, id,
    expired, created_at); `fresh(a)` says whether the story's drawn inputs are unchanged since that artifact was made.
    The newest usable artifact of each shard wins."""
    best: dict[int, dict] = {}
    for a in artifacts:
        if a.get("expired"):
            continue
        for k in range(n):
            if a.get("name") == shard_name(story, k, n) and fresh(a):
                if k not in best or a["created_at"] > best[k]["created_at"]:
                    best[k] = a
    reuse = {k: a["id"] for k, a in best.items()}
    return reuse, [k for k in range(n) if k not in reuse]
