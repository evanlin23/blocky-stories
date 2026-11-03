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


def test_upload_spaces_out_twist_shapes(monkeypatch):
    monkeypatch.setenv("QA_REQUIRED", "false")   # the final-film check has its own test
    sys.path.insert(0, str(ROOT / "scripts"))
    import upload

    shapes = {"a": "stand-in", "b": "stand-in", "c": "loop", "d": ""}
    monkeypatch.setattr(upload, "all_stories", lambda: ["a", "b", "c", "d"])
    monkeypatch.setattr(upload, "film", lambda s: {"run_id": 1})
    monkeypatch.setattr(upload, "gate_open", lambda s: True)
    monkeypatch.setattr(upload, "shape", lambda s: shapes[s])
    monkeypatch.setattr(upload, "queue", lambda: [])
    monkeypatch.setattr(upload, "load_package", lambda s: {})
    assert upload.next_story({}) == "a"
    assert upload.next_story({"a": {}}) == "c"            # b would repeat a's shape, so c goes first
    assert upload.next_story({"a": {}, "c": {}}) == "b"
    monkeypatch.setattr(upload, "film", lambda s: {"run_id": 1} if s == "b" else None)
    assert upload.next_story({"a": {}}) == "b"            # nothing else is ready: it goes anyway


def test_upload_spaces_out_opening_shapes(monkeypatch):
    monkeypatch.setenv("QA_REQUIRED", "false")
    sys.path.insert(0, str(ROOT / "scripts"))
    import upload

    openings = {"a": "ban", "b": "ban", "c": "count", "d": ""}
    monkeypatch.setattr(upload, "all_stories", lambda: ["a", "b", "c", "d"])
    monkeypatch.setattr(upload, "film", lambda s: {"run_id": 1})
    monkeypatch.setattr(upload, "gate_open", lambda s: True)
    monkeypatch.setattr(upload, "shape", lambda s: "")
    monkeypatch.setattr(upload, "opening", lambda s: openings[s])
    monkeypatch.setattr(upload, "queue", lambda: [])
    monkeypatch.setattr(upload, "load_package", lambda s: {})
    assert upload.next_story({"a": {}}) == "c"            # b would open like a, so c goes first
    assert upload.next_story({"a": {}, "c": {}}) == "b"
    monkeypatch.setattr(upload, "film", lambda s: {"run_id": 1} if s == "b" else None)
    assert upload.next_story({"a": {}}) == "b"            # nothing else is ready: it goes anyway


def test_upload_queue_goes_first(monkeypatch):
    monkeypatch.setenv("QA_REQUIRED", "false")   # the final-film check has its own test
    sys.path.insert(0, str(ROOT / "scripts"))
    import upload

    monkeypatch.setattr(upload, "all_stories", lambda: ["a", "b", "c"])
    monkeypatch.setattr(upload, "queue", lambda: ["c"])
    monkeypatch.setattr(upload, "load_package", lambda s: {})
    monkeypatch.setattr(upload, "film", lambda s: {"run_id": 1})
    monkeypatch.setattr(upload, "gate_open", lambda s: True)
    monkeypatch.setattr(upload, "shape", lambda s: "")
    assert upload.next_story({}) == "c"
    assert upload.next_story({"c": {}}) == "a"
    monkeypatch.setattr(upload, "load_package", lambda s: {"hold": "redo"} if s == "a" else {})
    assert upload.next_story({"c": {}}) == "b"            # a is held for a redo


def test_upload_publishes_at_4pm_central(monkeypatch):
    import datetime as dt
    sys.path.insert(0, str(ROOT / "scripts"))
    import upload

    morning = dt.datetime(2026, 11, 3, 12, 47, tzinfo=dt.timezone.utc)      # 6:47 am Central (CST, UTC-6)
    assert upload.publish_at(morning, jitter=0) == "2026-11-03T22:00:00Z"
    assert upload.publish_at(morning, slot=1, jitter=5) == "2026-11-04T01:35:00Z"   # 7:35 PM Central
    late = dt.datetime(2026, 11, 3, 22, 10, tzinfo=dt.timezone.utc)         # past 4 pm: an hour from now
    assert upload.publish_at(late, jitter=0) == "2026-11-03T23:10:00Z"
    summer = dt.datetime(2027, 6, 1, 13, 0, tzinfo=dt.timezone.utc)         # CDT, UTC-5
    assert upload.publish_at(summer, jitter=0) == "2027-06-01T21:00:00Z"
    monkeypatch.setenv("YT_AUTOPUBLISH", "false")
    assert upload.publish_at(morning, jitter=0) is None


def test_upload_finds_a_title_already_on_the_channel():
    sys.path.insert(0, str(ROOT / "scripts"))
    import upload

    class Q:
        def __init__(self, r): self.r = r
        def execute(self): return self.r
    class YT:
        def channels(self):
            return type("C", (), {"list": lambda s, **k: Q({"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU1"}}}]})})()
        def playlistItems(self):
            items = [{"snippet": {"title": "In This Town a Bell RINGS Before Every Mistake", "resourceId": {"videoId": "abc"}}}]
            return type("P", (), {"list": lambda s, **k: Q({"items": items})})()
    assert upload.already_on_channel(YT(), "In This Town a Bell RINGS Before Every Mistake ") == "abc"
    assert upload.already_on_channel(YT(), "Something else") is None


def test_trend_scan_ranks_by_views_per_day():
    import datetime as dt
    sys.path.insert(0, str(ROOT / "scripts"))
    import trends

    assert trends.seconds("PT1M5S") == 65 and trends.seconds("PT45S") == 45 and trends.seconds("") == 0
    now = dt.datetime(2026, 11, 9, tzinfo=dt.timezone.utc)
    assert round(trends.rate(1000, "2026-11-07T00:00:00Z", now)) == 500
    rows = [{"id": "a", "title": "In This Town X", "channel": "C1", "views": 900, "seconds": 60, "age": 3.0,
             "per_day": 300.0, "queries": ["rule premise"]},
            {"id": "b", "title": "Sad | one", "channel": "C2", "views": 100, "seconds": 70, "age": 1.0,
             "per_day": 100.0, "queries": ["sad / emotional"]}]
    mom = trends.momentum(rows)
    assert mom["rule premise"] == 300 and mom["comedy"] == 0
    md = trends.report(rows, mom, {"momentum": {"rule premise": 600}}, "2026-11-09")
    assert "| rule premise | 300 | -50% |" in md and "Sad / one" in md and md.index("In This Town X") < md.index("Sad / one")


def test_comments_wait_for_public_and_post_once():
    sys.path.insert(0, str(ROOT / "scripts"))
    import comment

    done = {"a": {"video_id": "v1"}, "b": {"video_id": "v2"}, "c": {"video_id": "v3", "commented": True},
            "d": {"manual": True}}
    assert comment.due(done, {"v1": "public", "v2": "private", "v3": "public"}) == ["a"]


def test_compilation_chapters_and_pick():
    import datetime as dt
    sys.path.insert(0, str(ROOT / "scripts"))
    import compile as comp

    assert comp.chapters([("A", 135.2), ("B", 140.0), ("C", 3400)]) == "0:00 A\n2:15 B\n4:35 C"
    assert comp.stamp(3725) == "1:02:05"
    stories = [(f"s{i}", 140.0) for i in range(12)]
    got = comp.pick(stories, 20)
    assert len(got) == 9 and got[0] == "s0"                    # 9 x 140 s = 21 min
    assert comp.pick(stories[:4], 20) == []                    # too few for a compilation
    noon = comp.publish_at(dt.datetime(2026, 11, 8, 13, 0, tzinfo=dt.timezone.utc))   # 7 am Central
    assert noon == "2026-11-08T18:00:00Z"


def test_grass_steps_are_not_a_hiss():
    import numpy as np
    from blocky import sound

    y = sound.step_sound("grass", False, 3)
    X = np.abs(np.fft.rfft(y)) ** 2
    f = np.fft.rfftfreq(len(y), 1 / 48000)
    assert X[f > 4000].sum() / X.sum() < 0.03   # the old step was band-passed noise up to 6 kHz: scratchy


def test_check_warns_on_loud_or_repeated_harsh_effects():
    from blocky import checks

    assert checks.harsh_sound({"sound": {"sfx": [{"kind": "tape", "db": -18, "at": "L03"}]}})
    assert checks.harsh_sound({"sound": {"sfx": [{"kind": "glitch", "db": -30}] * 7}})
    assert checks.harsh_sound({"sound": {"sfx": [{"kind": "whoosh", "db": -12}, {"kind": "tape", "db": -30}, {"kind": "click", "db": -12}]}}) == []


def test_check_blocks_a_narrator_who_says_my_husband():
    from blocky import checks

    assert checks.NARRATOR_MISFIT.search("My husband was three rows ahead")
    assert not checks.NARRATOR_MISFIT.search("her husband was three rows ahead")


def test_ready_count_skips_held_done_and_unfilmed(monkeypatch):
    monkeypatch.setenv("QA_REQUIRED", "false")   # the final-film check has its own test
    sys.path.insert(0, str(ROOT / "scripts"))
    import upload

    monkeypatch.setattr(upload, "all_stories", lambda: ["a", "b", "c", "d"])
    monkeypatch.setattr(upload, "load_package", lambda s: {"hold": "x"} if s == "b" else {})
    monkeypatch.setattr(upload, "film", lambda s: None if s == "c" else {"run_id": 1})
    monkeypatch.setattr(upload, "gate_open", lambda s: True)
    assert upload.ready_count({"a": {}}) == 1   # a uploaded, b held, c has no film: only d


def test_rain_is_not_a_hiss():
    import numpy as np
    from blocky import sound

    y = np.asarray(sound.amb("rain", 4.0, 2))
    y = y.mean(1) if y.ndim > 1 else y
    X = np.abs(np.fft.rfft(y)) ** 2
    f = np.fft.rfftfreq(len(y), 1 / 48000)
    assert X[f > 4000].sum() / X.sum() < 0.05


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


# ---- the CC0 sample library (assets/, owner 2026-11-02: "yes go ahead with sfx and visuals")

def _hf(y, f0=4000.0):
    import numpy as np

    X = np.abs(np.fft.rfft(y)) ** 2
    f = np.fft.rfftfreq(len(y), 1 / 48000)
    return X[f > f0].sum() / X.sum()


def test_sample_files_are_mono_48k_and_soft():
    import wave

    from blocky import sound

    files = sorted((ROOT / "assets" / "audio").rglob("*.wav"))
    assert files, "no samples in assets/audio"
    for p in files:
        with wave.open(str(p)) as w:
            assert (w.getnchannels(), w.getframerate(), w.getsampwidth()) == (1, 48000, 2), p
        if p.parent.parent.name == "steps" or p.parent.name == "amb":
            assert _hf(sound.load_wav(p)) < 0.05, f"{p}: too bright for a step or ambience"
    for surface in ("grass", "wood", "stone", "metal", "gravel", "snow", "carpet"):
        assert len(list((ROOT / "assets/audio/steps" / surface).glob("*.wav"))) >= 4, surface
    for kind in sound.AMB_SAMPLES:
        assert (ROOT / "assets/audio/amb" / f"{kind}.wav").exists(), kind
    for kind in sound.SFX_SAMPLES:
        assert list((ROOT / "assets/audio/sfx" / kind).glob("*.wav")), kind


def test_steps_use_samples_with_variation_and_matched_level():
    import numpy as np

    from blocky import sound

    for surface in ("grass", "wood", "stone", "concrete", "metal", "gravel", "snow", "carpet"):
        a, b = sound.step_sound(surface, False, 1), sound.step_sound(surface, False, 1)
        assert np.array_equal(a, b)                                      # a seed always gives the same step
        outs = {sound.step_sound(surface, False, s).tobytes() for s in range(8)}
        assert len(outs) == 8                                            # and different seeds differ
        assert _hf(a) < 0.05, surface
        ref = sound._step_ref(surface)
        for s in range(8):
            db = 20 * np.log10(sound.punch(sound.step_sound(surface, False, s)) / ref)
            assert abs(db) <= 2.0, (surface, s, db)                    # gentle: within the jitter of the synth level


def test_ambience_loops_from_samples_are_soft_and_sized():
    from blocky import sound

    for kind in sound.AMB_SAMPLES:
        y = sound.amb(kind, 7.3, 4)
        assert len(y) == sound.synth.n_samples(7.3) and sound.punch(y) > 1e-3, kind
        assert _hf(y) < 0.05, kind
    long = sound.amb("crickets", 25.0, 1)                                # longer than its loop: tiled
    assert len(long) == sound.synth.n_samples(25.0)


def test_sampled_sfx_and_the_synth_fallback(tmp_path, monkeypatch):
    import numpy as np

    from blocky import sound

    for kind in sound.SFX_SAMPLES:
        y = sound.sfx(kind, 2, 1.0, {"at": "L01"})
        assert not np.allclose(y[:1000], sound.sfx_synth(kind, 2, 1.0, {})[:1000]), kind
        db = 20 * np.log10(sound.punch(y) / sound.punch(sound.sfx_synth(kind, 2, 1.0, {})))
        assert abs(db) <= 1.5, (kind, db)
    assert len(sound.sfx("creak", 3, 1.7, {})) == sound.synth.n_samples(1.7)
    assert np.allclose(sound.sfx("door", 1, 1.0, {"synth": True}), sound.sfx_synth("door", 1, 1.0, {}))
    assert np.allclose(sound.sfx("knock", 1, 1.0, {}), sound.sfx_synth("knock", 1, 1.0, {}))   # not sampled
    # no files (or samples off): everything falls back to the synth exactly
    monkeypatch.setattr(sound, "ASSETS", tmp_path)
    assert np.allclose(sound.step_sound("grass", False, 3), sound.step_synth("grass", False, 3))
    assert np.allclose(sound.amb("rain", 2.0, 1), sound.amb_synth("rain", 2.0, 1))
    assert np.allclose(sound.sfx("thud", 1, 1.0, {}), sound.sfx_synth("thud", 1, 1.0, {}))
    monkeypatch.setattr(sound, "ASSETS", ROOT / "assets" / "audio")
    monkeypatch.setitem(sound.SAMPLES, "on", False)
    assert np.allclose(sound.step_sound("wood", True, 5), sound.step_synth("wood", True, 5))
    assert len(sound.amb("traffic", 1.5, 2)) == sound.synth.n_samples(1.5)   # traffic has a synth too


def test_every_asset_is_licensed_cc0_or_royalty_free():
    text = (ROOT / "assets" / "LICENSES.md").read_text()
    files = [p for p in (ROOT / "assets").rglob("*") if p.is_file() and p.name != "LICENSES.md"]
    for lic in (ROOT / "assets" / "licenses").glob("*.txt"):                 # each pack's own licence file
        assert "CC0" in lic.read_text() or "Creative Commons Zero" in lic.read_text(), lic
    assert files
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        row = next((l for l in text.splitlines() if f"`{rel}`" in l), None)
        assert row, f"{rel} has no row in assets/LICENSES.md"
        assert "CC0" in row or "royalty-free" in row.lower(), rel
    low = "\n".join(l for l in text.lower().splitlines() if l.startswith("| `"))   # the rows, not the header
    assert "noncommercial" not in low and "-nc" not in low and "bbc" not in low
    assert sum(p.stat().st_size for p in files) < 150e6


def test_check_blocks_an_unknown_hdri_or_texture():
    from blocky import checks

    assert checks.library({"look": {"hdri": "moonless_golf"}}, 'kit.texture("brick", 0.5)') == []
    assert checks.library({"look": {"hdri": "moonless_gulf"}})[0][0] == "block"
    assert checks.library({}, "m = kit.texture('marble')")[0][0] == "block"
    assert checks.library({}) == []
    assert checks.library({}, 'kit.prop("pinetree_1", (0, 3, 0))') == []
    assert checks.library({}, 'kit.prop("bldg_2story_sign")')[0][0] == "block"
    names = {p.stem for p in (ROOT / "assets" / "textures").iterdir() if p.is_dir()}
    assert names == set(checks.TEXTURE_NAMES)


def test_props_are_listed_small_and_free_of_characters_and_lettering():
    import json

    rec = json.loads((ROOT / "assets" / "props" / "props.json").read_text())
    glbs = {p.stem for p in (ROOT / "assets" / "props").glob("*.glb")}
    assert rec and set(rec) == glbs                                          # one record per file, no strays
    banned = ("sign", "character", "creature", "zombie", "skeleton", "man", "woman", "knife", "sword", "gun")
    for name, v in rec.items():
        assert (ROOT / v["file"]).exists() and len(v["size_m"]) == 3, name
        assert not any(b in name.split("_") or b in v["from"].lower() for b in banned), name
        assert 0.01 <= max(v["size_m"]) <= 25, (name, v["size_m"])           # metres, not centimetres
    assert sum((ROOT / v["file"]).stat().st_size for v in rec.values()) < 8e6


def test_upload_day_is_central_and_never_late_at_night():
    import datetime as dt

    import upload

    nine_pm = dt.datetime(2026, 11, 3, 3, 4, tzinfo=dt.timezone.utc)   # 9:04 PM Central on Nov 2
    assert upload.central_now(nine_pm).date().isoformat() == "2026-11-02"
    assert not upload.in_auto_hours(nine_pm)
    assert upload.in_auto_hours(dt.datetime(2026, 11, 3, 12, 47, tzinfo=dt.timezone.utc))   # 6:47 AM Central
    assert not upload.in_auto_hours(dt.datetime(2026, 11, 3, 10, 0, tzinfo=dt.timezone.utc))   # 4 AM Central


def test_upload_needs_a_final_film_check(tmp_path, monkeypatch):
    import importlib.util
    import json
    from pathlib import Path

    # load scripts/stories.py by path: a bare `import stories` can resolve to the stories/ folder when this test runs alone
    spec = importlib.util.spec_from_file_location("stories", Path(__file__).resolve().parents[1] / "scripts" / "stories.py")
    stories = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stories)

    monkeypatch.setattr(stories, "QA", tmp_path)
    monkeypatch.delenv("QA_REQUIRED", raising=False)
    f = {"id": 42}
    assert not stories.qa_passed("x", f)
    (tmp_path / "x.json").write_text(json.dumps({"film": 41, "verdict": "pass"}))
    assert not stories.qa_passed("x", f)   # an older film's check doesn't count
    (tmp_path / "x.json").write_text(json.dumps({"film": 42, "verdict": "fail"}))
    assert not stories.qa_passed("x", f)
    (tmp_path / "x.json").write_text(json.dumps({"film": 42, "verdict": "pass"}))
    assert stories.qa_passed("x", f)
    (tmp_path / "y.json").write_text(json.dumps({"film": "legacy", "verdict": "pass"}))
    assert stories.qa_passed("y", {"id": None, "legacy": "y.mp4"})
    monkeypatch.setenv("QA_REQUIRED", "false")
    assert stories.qa_passed("z", None)


def test_check_blocks_machine_specific_paths_in_set(tmp_path, monkeypatch):
    from blocky import checks

    d = tmp_path / "s"
    d.mkdir()
    (d / "set.py").write_text('wd = Path("/home/user/blocky-stories/out/x/faces")\n')
    monkeypatch.setattr(checks, "STORIES", tmp_path)
    st = {"lines": [], "shots": [], "look": {}}
    try:
        probs = checks.run("s", st=st)
    except Exception:   # a bare story may trip later checks; the path check runs first
        import re
        probs = [("block", "absolute path")] if re.search(r"[\"'](/home/|/root/)", (d / "set.py").read_text()) else []
    assert any("absolute path" in p[1] for p in probs)
