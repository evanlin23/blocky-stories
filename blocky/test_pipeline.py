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


def test_cut_rate_warning(tmp_path):
    """`check` warns when the average shot runs longer than the hits' 2.3 s, and not otherwise."""
    from blocky import checks, timeline

    tlp = tmp_path / "tl.json"
    tl = timeline.write("knock-back", ROOT / "stories/knock-back/voice-timings.json", tlp)   # 79 shots in 147 s
    cut_warn = lambda path: [m for _, m in checks.run("knock-back", path) if "a shot every" in m]
    assert cut_warn(tlp) == []
    slow = tmp_path / "slow.json"
    slow.write_text(json.dumps(dict(tl, shots=tl["shots"][:20])))   # 20 shots in 147 s: one every 7.3 s
    assert cut_warn(slow) and "7.3 s" in cut_warn(slow)[0]


def test_flash_safe_flicker(monkeypatch):
    """Safe flicker never drops below 40% and changes gently frame to frame, with dips at least ~1 s apart. The
    default flicker is untouched (it still blacks out, which is why safe mode exists)."""
    import types

    monkeypatch.setitem(sys.modules, "bpy", types.ModuleType("bpy"))
    mu = types.ModuleType("mathutils")
    mu.Vector = tuple
    monkeypatch.setitem(sys.modules, "mathutils", mu)
    import importlib

    kit = importlib.import_module("blocky.kit")
    fl = {"rate": 14.0, "depth": 0.5, "seed": 3, "dropouts": 0.8}
    ts = [f / 30 for f in range(30 * 60)]
    default = [kit.flicker_gain(t, fl) for t in ts]
    assert min(default) < 0.1
    safe = [kit.flicker_gain(t, {**fl, "safe": True}) for t in ts]
    assert min(safe) >= 0.4 * (1 - kit.SAFE_MAX_DEPTH) - 1e-9
    assert max(abs(a - b) for a, b in zip(safe, safe[1:])) < 0.12          # no single-frame jumps
    lows = [i for i, g in enumerate(safe) if g < 0.6]
    starts = [i for i in lows if i - 1 not in lows]
    assert all(b - a >= 30 for a, b in zip(starts, starts[1:]))            # dips at least a second apart


def test_flash_detector_motion_is_not_flashing():
    """A pan across a high-contrast pattern isn't a flash; real strobes, quarter-screen strobes and two halves
    strobing in antiphase still fail the house bar (safety.py, GRID)."""
    import numpy as np
    from blocky import safety

    z = np.zeros((135, 240)); o = np.full((135, 240), 0.7)
    fails = lambda fr: not safety.house_report(fr, [z] * len(fr))["house_bar"]["pass"]
    assert fails([o if i % 2 else z for i in range(60)])
    assert fails([np.hstack([o[:, :120], z[:, 120:]]) if i % 2 else np.hstack([z[:, :120], o[:, 120:]]) for i in range(60)])
    assert fails([np.where(np.arange(240)[None, :] < 60, 0.7, 0) * np.ones((135, 1)) if i % 2 else z for i in range(60)])
    stripes = lambda off: ((np.arange(240)[None, :] + off) // 12 % 2 * 0.7) * np.ones((135, 1))
    assert not fails([stripes(4 * i) for i in range(90)])
    assert not fails([o] * 60)
