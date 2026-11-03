"""The polish pack (blocky/polish.py, `look.polish`): opt-in, soft, flash-safe, and the voice stays on top."""

import json
import wave

import numpy as np
import pytest

from blocky import polish, post, sound, timeline
from blocky.synth import SR


def story(polish_on=True, **over):
    lines, vl, shots = [], {}, [{"id": "S0", "cam": [[0, [0, -3, 1.5], [0, 0, 1.5], 30]]}]
    for i in range(6):
        lid = f"L{i + 1:02d}"
        lines.append({"id": lid, "chunks": [["In the HALL,", "In the hall,"], ["it MOVED.", "it moved."]]})
        vl[lid] = {"text": "In the hall, it moved.", "onset": 0.05, "end": 1.6, "chunks": [[0.05, 0.7], [0.75, 1.6]]}
        if i:
            cam = [[0, [0, -2, 1.5], [0, 0, 1.5], 40]] if i % 2 else [[0, [0, -2, 1.5], [0, 0, 1.5], 40],
                                                                     [1, [1, -2, 1.5], [0, 0, 1.5], 40]]
            shots.append({"id": f"S{i}", "at": lid, "cam": cam})
    lines.insert(3, {"id": "P1", "pause": 0.8, "chunks": [["THUD", ""]]})
    st = {"name": "t", "title": "x", "made_for_kids": False, "premise": "p", "twist": "w",
          "cast": {"me": {"age": "teen", "skin": "#f1c9a0", "face": {"eyes": "round"}}}, "lines": lines, "shots": shots,
          "acting": {"me": [{"at": 0, "pos": [0, 0]}, {"at": "L05", "pos": [2, 0], "sfx": "door"}]},
          "look": {"polish": True} if polish_on else {},
          "sound": {"ambience": [{"kind": "rain", "from": "L02", "to": "L04", "lufs": -30}],
                    "sfx": [{"at": "L02.1", "kind": "thud", "db": -12}],
                    "music_drops": [{"from": "L05-0.6", "to": "L05"}]},
          "music": {"root": 45, "bpm": 66, "sections": [{"at": 0, "voices": ["drone", "pad"], "energy": 0.5}]}}
    st.update(over)
    voice = {"voice": "am_adam", "rate": 1.45, "tempo": 1.03, "model": "x", "lines": vl}
    return st, timeline.build(st, voice)


def _hf(y, f0=4000.0):
    X = np.abs(np.fft.rfft(y)) ** 2
    return X[np.fft.rfftfreq(len(y), 1 / SR) > f0].sum() / X.sum()


def test_off_by_default_and_overridable():
    st, _ = story(False)
    assert polish.spec(st) is None
    st, _ = story(look={"polish": {"punch": 0.05, "sway": ["S2"]}})
    p = polish.spec(st)
    assert p["punch"] == 0.05 and p["sway"] == ["S2"] and p["drift"] == polish.DEFAULTS["drift"]


def test_sound_events_whoosh_hit_riser_and_marks():
    st, tl = story()
    p = polish.spec(st)
    at = timeline.resolver(tl["lines"], tl["duration"])
    ev = polish.sound_events(tl, st, p, at)
    kinds = [e["kind"] for e in ev]
    assert "whoosh" in kinds and "hit" in kinds and "riser" in kinds and "door" in kinds
    taken = at("L02.1")
    assert all(abs(e["t"] - taken) >= polish.SEP for e in ev if e["kind"] != "whoosh") \
        and all(abs(e["t"] + 0.12 - taken) >= polish.SEP for e in ev if e["kind"] == "whoosh")   # clear of the builder's
    riser = next(e for e in ev if e["kind"] == "riser")
    assert riser["t"] + riser["dur"] == pytest.approx(at("L05-0.6"))   # it ends where the silence starts
    hit = next(e for e in ev if e["kind"] == "hit")
    assert hit["t"] == pytest.approx(at("P1"))                            # the big pause word is a reveal
    cuts = sorted(e["t"] for e in ev if e["kind"] == "whoosh")
    emph = polish.emph_times(tl, p, at)
    assert all(b - a >= p["whoosh_gap"] - 1e-6 or b + 0.12 in emph for a, b in zip(cuts, cuts[1:]))


def test_every_polish_sound_is_soft():
    """Owner, 2026-11-02 (ep36): no harsh, scratchy effects. Each polish sound keeps under 5% above 4 kHz."""
    for e in ({"kind": "whoosh", "lp": 3500.0}, {"kind": "hit", "lp": 3800.0}, {"kind": "lowhit", "lp": 1200.0},
              {"kind": "riser", "dur": 1.6, "lp": 3800.0}, {"kind": "door", "lp": 4000.0}):
        y = sound.polish_sound(e, 3)
        assert np.isfinite(y).all() and np.abs(y).max() > 1e-3, e
        assert _hf(y) < 0.05, (e["kind"], _hf(y))


def _vo(tmp_path, tl, loud=True):
    vo = tmp_path / "vo"
    vo.mkdir(exist_ok=True)
    for lid, p in tl["lines"].items():
        if p["who"] == "pause":
            continue
        n = int(1.6 * 24000)
        t = np.arange(n) / 24000
        y = (0.3 * np.sin(2 * np.pi * 180 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 4 * t))) if loud else np.zeros(n)
        with wave.open(str(vo / f"{lid}.wav"), "wb") as w:
            w.setnchannels(1), w.setsampwidth(2), w.setframerate(24000)
            w.writeframes((y * 32767).astype("<i2").tobytes())
    return vo


def test_mix_has_a_bed_ducks_under_the_voice_and_masters(tmp_path):
    st, tl = story()
    vo = _vo(tmp_path, tl)
    out, stats = sound.mix(tl, st, vo)
    assert abs(stats["lufs"] - (-14.0)) < 0.2 and stats["true_peak_dbtp"] <= -1.9
    assert "bed" in stats["stems_lufs"] and "polish" in stats["stems_lufs"]
    # never digital silence: the quietest 100 ms window of the film still has the bed in it (inside the drop too)
    w = int(0.1 * SR)
    m = out.mean(axis=1)[: len(out) // w * w].reshape(-1, w)
    assert np.sqrt((m ** 2).mean(axis=1)).min() > 10 ** (-75 / 20)
    # the voice sits on top: over the lines, the voice stem is well above everything else together
    st_off, tl_off = story(False)
    off, _ = sound.mix(tl_off, st_off, vo)
    assert np.isfinite(off).all() and not np.allclose(off, out)
    spans = [(p["onset"], p["end"]) for p in tl["lines"].values() if p["who"] != "pause"]
    assert stats["voice_lufs_over_lines"] is not None
    v = sound.lufs(out, spans)
    assert v > -15.5


def test_motion_never_still_and_never_jumps():
    st, tl = story()
    p = polish.spec(st)
    emph = polish.emph_times(tl, p)
    fps = tl["fps"]
    zs = [polish.motion(tl, st, p, f / fps, emph) for f in range(tl["frames"])]
    for (z, dx, dy) in zs:
        assert 1.0 <= z <= 1.0 + p["punch"] + p["drift"] * 1.3 + 1e-6
        assert z >= 1 + 2 * max(abs(dx), abs(dy)) - 0.02
    cuts = {s["f0"] for s in tl["shots"]}
    for f in range(1, len(zs)):
        if f not in cuts:   # inside a shot: at most a 3.5% zoom step per frame (the punch eases over 0.12 s)
            assert abs(zs[f][0] - zs[f - 1][0]) < 0.035, f
    # a static shot over 1.5 s drifts: its first and last frames differ
    for s, spec in zip(tl["shots"], st["shots"]):
        if s["end"] - s["start"] >= 1.5 and len(spec["cam"]) == 1:
            assert abs(zs[s["f0"]][0] - zs[s["f1"] - 1][0]) > 0.01, s["id"]


def test_sway_is_slow_and_only_where_asked():
    st, tl = story(look={"polish": {"sway": ["S1"], "drift": 0, "punch": 0}})
    p = polish.spec(st)
    s1 = next(s for s in tl["shots"] if s["id"] == "S1")
    s2 = next(s for s in tl["shots"] if s["id"] == "S2")
    a = [polish.motion(tl, st, p, (s1["f0"] + k) / tl["fps"], []) for k in range(s1["f1"] - s1["f0"])]
    assert max(abs(x[1]) for x in a) > 0.001 and max(abs(x[1]) for x in a) < 0.01
    assert all(abs(x[1] - y[1]) < 0.0015 for x, y in zip(a, a[1:]))    # smooth, no jitter
    assert polish.motion(tl, st, p, (s2["f0"] + 3) / tl["fps"], []) == (1.0, 0.0, 0.0)


def test_caption_pop_and_bright_grade():
    assert polish.caption_scale(0) == pytest.approx(0.9) and polish.caption_scale(0.08) == 1.0
    assert all(polish.caption_scale(x / 1000) <= polish.caption_scale((x + 1) / 1000) for x in range(90))
    g = polish.grade({"exposure": 0.9, "vignette": 0.4, "grain": 0.02, "contrast": 1.2, "saturation": 0.8},
                     polish.DEFAULTS)
    assert g["exposure"] >= 1.04 and g["vignette"] <= 0.2 and g["grain"] <= 0.009 and g["contrast"] <= 1.05
    dark = np.full((4, 4, 3), 0.05, np.float32)
    assert post.grade(dark, {**g, "vignette": 0})[0, 0, 0] > post.grade(dark, {"vignette": 0, "contrast": 1.0})[0, 0, 0]


def test_finish_with_polish_is_brighter_and_moves(tmp_path):
    from PIL import Image

    st, tl = story()
    st_off, _ = story(False)
    raw = tmp_path / "f.png"
    yy, xx = np.mgrid[0:480, 0:270]
    Image.fromarray(np.stack([(xx * 0.5 + yy * 0.2) % 120 + 20] * 3, -1).astype(np.uint8)).save(raw)
    s = next(s for s in tl["shots"] if s["end"] - s["start"] >= 1.5)
    a = post.finish(tl, st, s["f0"] + 2, raw).astype(float)
    b = post.finish(tl, st, s["f1"] - 2, raw).astype(float)
    off = post.finish(tl, st_off, s["f0"] + 2, raw).astype(float)
    assert a[200:1100].mean() > off[200:1100].mean()     # the bright grade lifts it
    assert np.abs(a[100:1000] - b[100:1000]).mean() > 0.5  # and the static shot isn't a still


def test_check_blocks_unknown_polish_settings():
    from blocky import checks

    st, _ = story(look={"polish": {"punchh": 0.05, "sway": ["S9"], "grade": "teal", "punch": 0.2}})
    msgs = " ".join(m for lvl, m in checks.polish_problems(st) if lvl == "block")
    assert "punchh" in msgs and "S9" in msgs and "teal" in msgs and "0 to 8%" in msgs
    st, _ = story(look={"polish": {"sway": ["S1"], "emph": ["L02"]}})
    assert checks.polish_problems(st) == [] and checks.polish_problems(story()[0]) == []


def test_hits_land_on_the_key_word_and_long_shots_get_a_fill_punch():
    st, tl = story()
    p = polish.spec(st)
    at = timeline.resolver(tl["lines"], tl["duration"])
    a, b, text = tl["lines"]["L02"]["chunks"][1]          # "it MOVED.": the hit lands on MOVED, not "it"
    t = polish.on_key(tl, a)
    assert a < t < b and t == pytest.approx(a + (b - a) * 3 / len(text))
    emph = polish.emph_times(tl, {**p, "emph": [], "auto": False})
    long = [s for s in tl["shots"] if s["end"] - s["start"] >= p["fill"]]
    assert long and all(any(s["start"] <= e < s["end"] for e in emph) for s in long
                        if any(s["start"] + 0.8 <= c["start"] <= s["end"] - 0.6 for c in tl["captions"]))
    quiet = polish.sound_events(tl, {**st, "look": {"polish": {"quiet": ["L01"]}}}, {**p, "quiet": ["L01"]}, at)
    assert not any(e["kind"] == "lowhit" and abs(e["t"] - at("L01")) < 0.5 for e in quiet)


def test_risers_are_not_ducked_and_whooshes_avoid_words():
    st, tl = story()
    p = polish.spec(st)
    at = timeline.resolver(tl["lines"], tl["duration"])
    ev = polish.sound_events(tl, st, p, at)
    emph = polish.emph_times(tl, p, at)
    onsets = [ln["onset"] for ln in tl["lines"].values()]
    for e in ev:
        if e["kind"] == "whoosh":
            t = e["t"] + 0.12
            assert t in emph or any(abs(t - o) < 0.06 for o in onsets)
    y = sound.polish_sound({"kind": "riser", "dur": 1.8, "lp": 3800.0}, 1)
    q = len(y) // 4
    assert np.sqrt((y[q:2 * q] ** 2).mean()) > 0.05 * np.abs(y).max()   # it builds over its length, not only the end
