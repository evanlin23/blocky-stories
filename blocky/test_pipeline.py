"""The ship pipeline: package lint, review verdicts, the flash line, voice drift. No Blender or TTS needed."""

import json
import sys
from pathlib import Path

import numpy as np

from blocky import flash, gate

ROOT = Path(__file__).resolve().parents[1]

GOOD = {"title": "Our building doesn't have a thirteenth floor",
        "description": "A short scary story about a lift that stops where it shouldn't. It's made up.\n\nBuilt with code and Blender.",
        "pin": "would you have stayed quiet?", "made_for_kids": False}


def test_good_package_passes():
    assert [p for p in gate.lint_package(GOOD) if p[0] == "block"] == []


def test_package_blocks():
    cases = {"title": "A true story from a Roblox server", "description": "Made for kids. It's made up.",
             "pin": "this really happened — right?"}
    for k, v in cases.items():
        assert any(p[0] == "block" for p in gate.lint_package({**GOOD, k: v})), k
    assert any(p[0] == "block" for p in gate.lint_package({**GOOD, "made_for_kids": True}))
    assert any(p[0] == "block" for p in gate.lint_package({**GOOD, "description": "A scary story."}))
    assert gate.lint_package(None)[0][0] == "block"


def test_verdicts_take_the_latest_round(tmp_path, monkeypatch):
    d = tmp_path / "s"
    (d / "reviews").mkdir(parents=True)
    (d / "reviews" / "r1-standards.md").write_text("Verdict: revise\n1. fix")
    (d / "reviews" / "r2-standards.md").write_text("# r2\n**Verdict:** approve\n")
    (d / "reviews" / "r1-critic.md").write_text("Verdict: approve\n")
    monkeypatch.setattr(gate, "story_dir", lambda name: d)
    assert gate.verdicts("s") == {"standards": (2, "approve"), "critic": (1, "approve")}


def test_flash_line_and_steady_film(monkeypatch, tmp_path):
    frames = np.full((90, 135, 240, 3), 40, np.uint8)
    monkeypatch.setattr(flash, "decode_low", lambda p: frames)
    rep = flash.measure(tmp_path / "x.mp4", [30, 60])
    assert rep["house_bar"]["pass"] and rep["description_line"] is None
    json.dumps(rep)
    strobe = frames.copy()
    strobe[::2] = 250
    monkeypatch.setattr(flash, "decode_low", lambda p: strobe)
    rep = flash.measure(tmp_path / "x.mp4", None)
    assert not rep["house_bar"]["pass"]
    assert rep["description_line"].startswith("Flashing lights and fast cuts from 0:00 to 0:0")


def test_voice_verify(tmp_path):
    from blocky.__main__ import verify_voice

    kept = json.loads((ROOT / "stories" / "knock-back" / "voice-timings.json").read_text())
    (tmp_path / "k.json").write_text(json.dumps(kept))
    (tmp_path / "n.json").write_text(json.dumps(kept))
    assert verify_voice(tmp_path / "n.json", tmp_path / "k.json") == 0
    stale = json.loads(json.dumps(kept))
    stale["lines"]["L999"] = stale["lines"][next(iter(kept["lines"]))]   # a line cut in revision: ignored
    (tmp_path / "k.json").write_text(json.dumps(stale))
    assert verify_voice(tmp_path / "n.json", tmp_path / "k.json") == 0
    lid = next(iter(kept["lines"]))
    kept["lines"][lid]["chunks"][0][1] += 0.1
    (tmp_path / "n.json").write_text(json.dumps(kept))
    assert verify_voice(tmp_path / "n.json", tmp_path / "k.json") == 1


def test_upload_description_adds_flash_line():
    sys.path.insert(0, str(ROOT / "scripts"))
    import upload

    d = upload.description(GOOD, {"description_line": "Flashing lights and fast cuts from 0:02 to 2:13."})
    assert d.startswith("Flashing lights and fast cuts from 0:02 to 2:13.\n\nA short scary story")
    assert upload.description(GOOD, {"description_line": None}).startswith("A short scary")


def test_metrics_summary_and_titles():
    sys.path.insert(0, str(ROOT / "scripts"))
    import metrics

    assert metrics.norm("The driver on my night bus counted 6. I counted 5.") == "the driver on my night bus counted 6 i counted 5"
    assert metrics.story_titles()[metrics.norm("The driver on my night bus counted 6. I counted 5.")] == "back-row"
    rows = [{"story": "back-row", "title": "x", "published": "2026-10-31", "length_s": 147,
             "totals": {"views": 21000, "engagedViews": 15000, "averageViewPercentage": 71.2, "likes": 900,
                        "comments": 40, "shares": 12, "subscribersGained": 30},
             "traffic": {"SHORTS": 0.93, "YT_CHANNEL": 0.07},
             "retention": {"at": {"5%": 0.95, "50%": 0.7}, "biggest_drops": [{"at_s": 3.0, "drop": 0.08}], "relative_mid": 0.6}}]
    md = metrics.summary(rows, "2026-11-02")
    assert "| back-row | 2026-10-31 | 147 s | 21,000 | 15,000 | 71% |" in md and "93%" in md and "3.0 s (-8%)" in md


def test_metrics_status_says_why_there_are_no_numbers():
    sys.path.insert(0, str(ROOT / "scripts"))
    import metrics

    assert metrics.status({"privacy": "private"}) == "not public (private)"
    assert metrics.status({"privacy": "public", "totals": {}}).startswith("no data yet")
    assert metrics.status({"privacy": "public", "totals": {"views": "24800"}}) == "24,800 views"
    md = metrics.summary([{"story": "back-row", "title": "x", "published": "2026-10-31", "length_s": 147, "privacy": "public",
                           "totals": {}}], "2026-11-01")
    assert "no data yet" in md and "| ? |" not in md


def test_film_artifact_lookup(monkeypatch):
    sys.path.insert(0, str(ROOT / "scripts"))
    import subprocess

    import stories

    payload = {"artifacts": [
        {"id": 1, "expired": False, "created_at": "2026-11-01T10:00:00Z", "workflow_run": {"id": 11}},
        {"id": 2, "expired": False, "created_at": "2026-11-02T10:00:00Z", "workflow_run": {"id": 22}},
        {"id": 3, "expired": True, "created_at": "2026-11-03T10:00:00Z", "workflow_run": {"id": 33}}]}

    class R:
        returncode = 0

        @property
        def stdout(self):
            return json.dumps(payload)

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: R())
    f = stories.film("photo-strip")
    assert f["id"] == 2 and f["run_id"] == 22 and f["url"].endswith("/actions/runs/22")
    payload["artifacts"] = []
    assert stories.film("photo-strip") is None
