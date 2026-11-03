"""Offline tests for scripts/render_plan.py: pure decisions, no git, no network."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from render_plan import pick_shards, shard_name, skip_reason  # noqa: E402

PASS = {"stage": "proof", "verdict": "pass", "sha": "abc123"}


def test_skip_without_qa():
    assert "no qa/s.json" in skip_reason("s", None, None)


def test_skip_failed_proof():
    assert "failed" in skip_reason("s", {**PASS, "verdict": "fail"}, [])


def test_skip_film_changed_after_proof():
    why = skip_reason("s", PASS, ["stories/s/set.py"])
    assert "changed after the proof" in why


def test_skip_proof_commit_not_in_history():
    assert "isn't in this branch" in skip_reason("s", PASS, None)


def test_passed_proof_draws():
    assert skip_reason("s", PASS, []) is None


def test_passed_final_draws_even_without_proof_sha():
    assert skip_reason("s", {"stage": "final", "verdict": "pass"}, None) is None


def test_failed_final_is_skipped():
    assert skip_reason("s", {"stage": "final", "verdict": "fail"}, None) is not None


def art(k, id_, at="2026-11-03T10:00:00Z", n=4, expired=False, story="s"):
    return {"name": shard_name(story, k, n), "id": id_, "created_at": at, "expired": expired}


def test_nothing_drawn_draws_all():
    assert pick_shards("s", 4, [], lambda a: True) == ({}, [0, 1, 2, 3])


def test_reuse_drawn_and_draw_the_rest():
    reuse, missing = pick_shards("s", 4, [art(0, 10), art(2, 12)], lambda a: True)
    assert reuse == {0: 10, 2: 12} and missing == [1, 3]


def test_all_there_is_assemble_only():
    reuse, missing = pick_shards("s", 4, [art(k, k + 1) for k in range(4)], lambda a: True)
    assert missing == [] and sorted(reuse) == [0, 1, 2, 3]


def test_expired_stale_or_other_cut_are_not_reused():
    arts = [art(0, 1, expired=True), art(1, 2), art(2, 3, n=16), art(3, 4, story="other")]
    reuse, missing = pick_shards("s", 4, arts, lambda a: a["id"] != 2)
    assert reuse == {} and missing == [0, 1, 2, 3]


def test_newest_usable_wins():
    arts = [art(0, 1, "2026-11-03T08:00:00Z"), art(0, 2, "2026-11-03T12:00:00Z"), art(0, 3, "2026-11-03T14:00:00Z")]
    reuse, _ = pick_shards("s", 4, arts, lambda a: a["id"] != 3)   # the newest is stale: the next one is used
    assert reuse == {0: 2}
