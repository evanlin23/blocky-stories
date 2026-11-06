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
    monkeypatch.setattr(pp, "pr_changed", lambda a: [".github/workflows/proof.yml"])
    class A: story = ""; base = "b"; before = ""; selftest = "ep62-six-riders"
    assert pp.plan(A) == (["ep62-six-riders"], True)


# --- migration step 1: one proof per sha, only the PR's own stories, only after both reviews approve ---------------

class Args:
    story, base, before, shards, selftest, force = "", "BASE", "", 8, "self", "false"


def world(monkeypatch, changed, approved=("a", "b"), drawn=None, live=None):
    """plan() with git, the gate and the GitHub API replaced: `changed` is what the PR changed (base...HEAD)."""
    monkeypatch.setattr(pp, "pr_changed", lambda base: changed)
    monkeypatch.setattr(pp, "stories_in", lambda paths: sorted({p.split("/")[1] for p in paths
                                                                if p.startswith("stories/") and len(p.split("/")) > 2}))
    monkeypatch.setattr(pp, "gate_open", lambda s: s in approved)
    monkeypatch.setattr(pp, "load_package", lambda s: {})
    monkeypatch.setattr(pp, "merge_problems", lambda s, base: [("block", "waiting for proof: no qa")])
    monkeypatch.setattr(pp, "artifact_shas", lambda s: [drawn] if drawn else [])
    monkeypatch.setattr(pp, "drawn_sha", lambda s, head, shas: shas[0] if shas else None)
    monkeypatch.setattr(pp, "live_run", lambda s, sha: live)


def test_no_film_push_plans_nothing(monkeypatch):
    # a push that changes only the package, the reviews' prose and a handoff note: nothing to draw, no selftest
    world(monkeypatch, ["stories/a/package.json", "stories/a/notes/handoff.md", "HANDOFF.md"])
    assert pp.plan(Args()) == ([], False)


def test_duplicate_dispatch_for_the_same_sha(monkeypatch):
    class D(Args):
        story = "a"
    world(monkeypatch, [], drawn="abc123")              # the PR's run already left proof-a for this film
    assert pp.plan(D()) == ([], False)
    world(monkeypatch, [], live=41769144473)             # the PR's run is still drawing this commit
    assert pp.plan(D()) == ([], False)
    D.force = "true"                                     # by hand, on purpose
    assert pp.plan(D()) == (["a"], False)


def test_a_fresh_dispatch_draws(monkeypatch):
    class D(Args):
        story = "a"
    world(monkeypatch, [])
    assert pp.plan(D()) == (["a"], False)


def test_pr_touching_two_stories_proofs_both(monkeypatch):
    world(monkeypatch, ["stories/a/set.py", "stories/b/story.json"])
    assert pp.plan(Args()) == (["a", "b"], False)


def test_story_whose_reviews_do_not_both_approve(monkeypatch):
    world(monkeypatch, ["stories/a/set.py", "stories/b/story.json"], approved=("a",))
    assert pp.plan(Args()) == (["a"], False)               # b's gate is closed: no proof yet
    class D(Args):
        story = "b"
    assert pp.plan(D()) == ([], False)                   # nor by dispatch, unless forced
    assert "gate closed" in pp.decide(["(dispatch)"], False, False, [], None)


def test_older_live_run_of_the_same_sha_draws_and_newer_stands_down():
    runs = [{"id": 10, "status": "in_progress"}, {"id": 20, "status": "in_progress"}]
    jobs = {10: [{"name": "plan", "status": "completed"}, {"name": "draw (a, 3)", "status": "queued"}],
            20: [{"name": "plan", "status": "in_progress"}]}
    assert pp.drawing_run("a", 20, runs, jobs) == (10, False)
    assert pp.drawing_run("a", 10, runs, jobs) == (None, False)          # only older runs count
    assert pp.drawing_run("b", 20, runs, jobs) == (None, False)          # 10 draws another story
    assert pp.drawing_run("a", 30, runs, {10: [{"name": "plan", "status": "in_progress"}]}) == (None, True)
    assert pp.drawing_run("a", 30, [{"id": 10, "status": "completed"}], jobs) == (None, False)


def test_live_run_without_token_means_draw(monkeypatch):
    monkeypatch.delenv("GH_TOKEN", raising=False)
    assert pp.live_run("a", "sha") is None


def test_pr_diff_is_from_the_merge_base(monkeypatch, tmp_path):
    """A story main changed after the branch left it is not the PR's (dryer-nine on the batch10-scripts PR)."""
    import subprocess

    def git(*args):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True,
                       env={"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                            "GIT_COMMITTER_EMAIL": "t@t", "PATH": "/usr/bin:/bin"})
    def write(rel, text):
        f = tmp_path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)

    git("init", "-q", "-b", "main")
    write("stories/mine/set.py", "1"); write("stories/other/set.py", "1")
    git("add", "."); git("commit", "-qm", "start")
    git("checkout", "-qb", "pr")
    write("stories/mine/set.py", "2"); git("commit", "-qam", "the PR's change")
    git("checkout", "-q", "main")
    write("stories/other/set.py", "2"); git("commit", "-qam", "main moves on")
    base = subprocess.run(["git", "-C", str(tmp_path), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    git("checkout", "-q", "pr")
    monkeypatch.setattr(pp, "ROOT", tmp_path)
    assert pp.pr_changed(base) == ["stories/mine/set.py"]
    assert sorted(pp.changed(base)) == ["stories/mine/set.py", "stories/other/set.py"]   # the old two-dot diff
    assert pp.pr_changed("") is None and pp.pr_changed("0" * 40) is None
