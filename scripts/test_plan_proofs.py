"""plan_proofs.decide / drawn_sha: which stories get a proof (no git state, no network)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan_proofs as pp  # noqa: E402

FILM = ["stories/ep1/story.json"]
BLOCK = [("block", "no qa/ep1.json")]


def d(film=FILM, held=False, gate=True, probs=BLOCK, drawn=None):
    return pp.decide(film, held, gate, probs, drawn)


def test_needed_proof_is_planned():
    assert d() is None


def test_replaced_run_or_handoff_push_still_plans():
    # decide() no longer sees what the push touched: a main merge or a HANDOFF.md push changes nothing here
    assert d() is None


def test_no_film_change_vs_base():
    assert "base" in d(film=[])


def test_held_story():
    assert "held" in d(held=True)


def test_closed_gate():
    assert "gate closed" in d(gate=False)


def test_passed_proof_check():
    assert "covers" in d(probs=[])


def test_existing_proof_for_same_film():
    assert "already exists" in d(drawn="abcdef0123")


def test_drawn_sha_same_commit_and_unchanged_film(monkeypatch):
    assert pp.drawn_sha("ep1", "h", ["h"]) == "h"
    monkeypatch.setattr(pp, "changed", lambda a, b="HEAD": ["HANDOFF.md", "stories/ep1/reviews/x.md"])
    assert pp.drawn_sha("ep1", "h", ["old"]) == "old"


def test_drawn_sha_film_changed_or_unknown(monkeypatch):
    monkeypatch.setattr(pp, "changed", lambda a, b="HEAD": ["stories/ep1/story.json"])
    assert pp.drawn_sha("ep1", "h", ["old"]) is None
    monkeypatch.setattr(pp, "changed", lambda a, b="HEAD": None)
    assert pp.drawn_sha("ep1", "h", ["gone"]) is None


def test_no_token_means_draw(monkeypatch):
    monkeypatch.delenv("GH_TOKEN", raising=False)
    assert pp.artifact_shas("ep1") == []


def test_selftest_when_workflow_only(monkeypatch):
    monkeypatch.setattr(pp, "changed", lambda a, b="HEAD": [".github/workflows/proof.yml"])
    class A: story = ""; base = "b"; before = ""; selftest = "ep62-six-riders"
    assert pp.plan(A) == (["ep62-six-riders"], True)
