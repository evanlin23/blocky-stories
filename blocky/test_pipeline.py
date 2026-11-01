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
