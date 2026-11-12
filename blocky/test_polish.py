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
        assert 1.0 <= z <= p["max_zoom"] + 1e-6
        assert max(abs(dx), abs(dy)) < 0.05                               # slides stay small
    cuts = {s["f0"] for s in tl["shots"]} | {int(round(t * fps)) for t in polish.reframe_times(tl, p)}
    for f in range(1, len(zs)):
        if f not in cuts and f - 1 not in cuts:   # inside a framing: at most a 3.5% zoom step per frame
            assert abs(zs[f][0] - zs[f - 1][0]) < 0.035, f
    # never still: the push moves the crop on every frame of every shot
    assert all(zs[f] != zs[f - 1] for f in range(1, len(zs)) if f not in cuts)
    # a static shot gets a real camera move (two different keys); with the camera off, a shot over 1.5 s drifts
    for i, (s, spec) in enumerate(zip(tl["shots"], st["shots"])):
        if len(spec["cam"]) == 1:
            moved = polish.cam_spec(spec, i, p)["cam"]
            assert len(moved) == 2 and moved[0][1] != moved[1][1], s["id"]
    p_off = {**p, "camera": False, "push": 0, "reframe_every": 0}
    zo = [polish.motion(tl, st, p_off, f / fps, emph) for f in range(tl["frames"])]
    for s, spec in zip(tl["shots"], st["shots"]):
        if s["end"] - s["start"] >= 1.5 and len(spec["cam"]) == 1:
            assert abs(zo[s["f0"]][0] - zo[s["f1"] - 1][0]) > 0.01, s["id"]


def test_sway_is_slow_and_only_where_asked():
    st, tl = story(look={"polish": {"sway": ["S1"], "drift": 0, "punch": 0, "push": 0, "reframe_every": 0}})
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
    emph = polish.emph_times(tl, {**p, "emph": [], "auto": False, "fill": 2.2, "punch_rate": None})
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


def test_a_quiet_span_keeps_whooshes_hits_and_added_punches_out():
    st, tl = story()
    at = timeline.resolver(tl["lines"], tl["duration"])
    p = {**polish.spec(st), "quiet": [["L03", "L05"]]}
    a, b = at("L03"), at("L05")
    ev = polish.sound_events(tl, st, p, at)
    assert not any(a <= e["t"] + (0.12 if e["kind"] == "whoosh" else 0) <= b
                   for e in ev if e["kind"] in ("whoosh", "lowhit"))
    assert not any(a <= t <= b for t in polish.emph_times(tl, p, at))


def test_eased_walks_start_and_stop_gently_and_feet_follow():
    """Craft metrics, 2026-11-03: every walk started and stopped dead (constant speed between keys)."""
    from blocky import acting

    keys = [{"t": 0.0, "pos": [0, 0]}, {"t": 1.0, "pos": [0, 0]}, {"t": 3.0, "pos": [2.4, 0]}, {"t": 4.0, "pos": [2.4, 0]}]
    fdt = 1 / 30
    for ease in (False, True):
        x = lambda t: acting.position(keys, t, ease)[0]
        jump = max(abs((x(te + fdt) - x(te)) - (x(te) - x(te - fdt))) / fdt for te in (1.0, 3.0))
        assert (jump < 0.5) if ease else (jump > 0.5), (ease, jump)
        assert x(3.0) == pytest.approx(2.4) and x(1.0) == pytest.approx(0.0)        # same keys, same timing
    # a path through several keys stays one walk: no slow-down at the middle key
    path = [{"t": 0.0, "pos": [0, 0]}, {"t": 1.0, "pos": [1.2, 0]}, {"t": 2.0, "pos": [2.4, 0]}]
    ea, eb = acting._ends(path, 0)
    assert ea >= acting.EASE_S and eb == 0.0
    # footsteps land where the eased walk has covered each stride
    tl = {"acting": {"me": keys}, "motion": {"ease": True}}
    for f in acting.footsteps(tl, "me"):
        assert acting.position(keys, f["t"], True)[0] == pytest.approx(f["x"], abs=1e-3)
    assert len(acting.footsteps(tl, "me")) == len(acting.footsteps({"acting": {"me": keys}}, "me"))


def test_idle_life_is_subtle_slow_and_only_with_the_pack():
    from blocky import acting

    keys = [{"t": 0.0, "pos": [0, 0], "yaw": 10}]
    base = {"acting": {"me": keys}, "talk": {}}
    still = [acting.state(base, "me", t / 10) for t in range(50)]
    assert len({(s["head_yaw"], s["lean"]) for s in still}) == 1                    # without the pack: a statue
    live = {**base, "motion": {"idle": True}}
    ss = [acting.state(live, "me", t / 30) for t in range(300)]
    hy = np.array([s["head_yaw"] for s in ss])
    assert np.degrees(np.abs(hy).max()) < 9 and np.degrees(np.abs(np.diff(hy)).max()) < 0.6   # small and slow
    still_windows = sum(np.abs(np.diff(hy[i:i + 30])).max() < np.radians(0.06) for i in range(0, 270, 30))
    assert still_windows == 0
    assert all(abs(s["bob"]) < 0.01 for s in ss)


def test_camera_moves_are_slow_and_keep_the_framing():
    st, tl = story()
    p = polish.spec(st)
    import math
    for i, spec in enumerate(st["shots"]):
        m = polish.cam_spec(spec, i, p)
        if len(spec["cam"]) > 1:
            assert m is spec                                                            # its own move is kept
            continue
        (_, a, ta, la), (_, b, tb, lb) = m["cam"][0][:4], m["cam"][1][:4]
        tgt = spec["cam"][0][2]
        assert la == lb == spec["cam"][0][3]
        assert math.dist(a, b) <= 0.6 + 1e-6 and math.dist(a, b) > 0.05
        d0, d1 = math.dist(a, tgt), math.dist(b, tgt)
        assert d1 < d0                                                                   # it pushes in
    assert polish.cam_spec(st["shots"][0], 0, {**p, "camera": False}) is st["shots"][0]


def test_punch_ins_are_capped_on_key_words():
    st, tl = story()
    p = polish.spec(st)
    at = timeline.resolver(tl["lines"], tl["duration"])
    emph = polish.emph_times(tl, p, at)
    assert len(emph) <= max(1, int(p["punch_rate"] * tl["duration"] / 10 + 0.5))
    keys = [t for _k, t in polish.key_times(tl, p, at)]
    assert all(any(abs(t - k) < 1e-9 for k in keys) for t in emph)                 # key words only
    assert all(b - a >= 5.0 / p["punch_rate"] - 1e-6 for a, b in zip(emph, emph[1:]))


def test_walk_shots_go_on_ones_only_with_the_pack():
    st, tl = story(look={"polish": {"ones": "walk"}})
    st_off, tl_off = story(False)
    for sp in (st, st_off):
        for s in sp["shots"]:
            s["step"] = 2
    voice = {"voice": "am_adam", "rate": 1.45, "tempo": 1.03, "model": "x",
             "lines": {l: {"text": "In the hall, it moved.", "onset": 0.05, "end": 1.6, "chunks": [[0.05, 0.7], [0.75, 1.6]]}
                       for l in [f"L{i:02d}" for i in range(1, 7)]}}
    on, off = timeline.build(st, voice), timeline.build(st_off, voice)
    from blocky import acting
    walking = {s["id"] for s in on["shots"]
               if any(acting.state(on, "me", f / 30)["speed"] > 0.05 for f in range(s["f0"], s["f1"], 6))}
    assert walking and all(s["step"] == (1 if s["id"] in walking else 2) for s in on["shots"])
    assert all(s["step"] == 2 for s in off["shots"])


def test_camera_push_is_capped_gentler_close_and_straight_on_a_reveal():
    """Critic, ep32 v2: a 0.6 s shot pushed too fast, a close-up cropped hair, and the reveal drifted."""
    import math
    p = polish.spec({"look": {"polish": True}})
    far = {"id": "A", "cam": [[0, [0, -6, 1.5], [0, 0, 1.5], 40]]}
    near = {"id": "B", "cam": [[0, [0, -0.8, 1.5], [0, 0, 1.5], 40]]}
    move = lambda sp, **kw: math.dist(*(k[1] for k in polish.cam_spec(sp, 0, p, **kw)["cam"]))
    assert move(far, dur=0.6) <= polish.CAM_SPEED * 0.6 + 1e-6 < move(far, dur=5.0)
    assert move(near, dur=5.0) / 0.8 < move(far, dur=5.0) / 6.0                  # less push, relative, up close
    calm = polish.cam_spec(far, 0, p, dur=5.0, calm=True)["cam"]
    a, b, tgt = calm[0][1], calm[1][1], far["cam"][0][2]
    assert a[0] == pytest.approx(0) and b[0] == pytest.approx(0)                     # straight in: no arc or truck
    assert math.dist(a, b) < move(far, dur=5.0)


def test_reveal_shots_are_calm():
    from blocky import acting
    st, tl = story()
    calm = tl["motion"]["calm_shots"]
    p = polish.spec(st)
    at = timeline.resolver(tl["lines"], tl["duration"])
    rev = polish.reveal_times(tl, p, at)
    assert calm and all(any(s["start"] <= t < s["end"] for t in rev) for s in tl["shots"] if s["id"] in calm)
    s = next(x for x in tl["shots"] if x["id"] in calm)
    hy = [acting.state(tl, "me", s["start"] + k / 30)["head_yaw"] for k in range(int((s["end"] - s["start"]) * 30))]
    assert max(hy) - min(hy) < 0.03                                                # nearly still on the reveal


def test_bright_grade_lift_keeps_colour():
    """Craft metrics, ep62: the lift added grey and washed the picture out (saturation 0.19). It scales by luma now."""
    rng = np.random.default_rng(1)
    img = (rng.random((40, 40, 3)) * 0.35).astype(np.float32)        # a dark, colourful frame
    sat = lambda a: float(((a.max(-1) - a.min(-1)) / np.maximum(a.max(-1), 1e-6)).mean())
    g = {"vignette": 0, "contrast": 1.0}
    lifted = np.clip(post.grade(img, {**g, "lift": 0.035}), 0, 1)
    plain = np.clip(post.grade(img, g), 0, 1)
    assert lifted.mean() > plain.mean() and sat(lifted) == pytest.approx(sat(plain), abs=1e-3)


def test_voice_sits_over_the_music_and_ambience(tmp_path):
    """v2.1 (craft metrics, ep62: 6.3 dB): the music dips under the lines until the voice is 10.5 dB over it."""
    import math
    st, tl = story()
    st["music"]["sections"][0]["energy"] = 1.0
    vo = _vo(tmp_path, tl)
    out, stats = sound.mix(tl, st, vo)
    s = stats["stems_lufs"]
    gap = s["voice"] - 10 * math.log10(sum(10 ** (s[k] / 10) for k in ("music", "amb") if k in s))
    assert gap >= 10.0 and abs(stats["lufs"] + 14.0) < 0.2


def test_ones_moving_draws_camera_moves_on_every_frame():
    st, tl = story(look={"polish": {"ones": "moving"}})
    for s in st["shots"]:
        s["step"] = 2
    voice = {"voice": "am_adam", "rate": 1.45, "tempo": 1.03, "model": "x",
             "lines": {l: {"text": "In the hall, it moved.", "onset": 0.05, "end": 1.6, "chunks": [[0.05, 0.7], [0.75, 1.6]]}
                       for l in [f"L{i:02d}" for i in range(1, 7)]}}
    on = timeline.build(st, voice)
    assert all(s["step"] == 1 for s in on["shots"])          # every shot's camera moves with the pack


def test_ones_moving_is_the_default():
    """Lead, 2026-11-03: the camera moves 96% of the time with the pack, so moves are drawn on every frame."""
    assert polish.DEFAULTS["ones"] == "all"


def test_bright_grade_lift_never_turns_near_black_red():
    """ep47 r8: contrast left near-black pixels with negative channels, their luma sat at the 1e-4 floor, and the
    lift scaled the one positive channel about 1000x into pure red. Near-blacks must lift to a dark, quiet grey."""
    img = np.full((8, 8, 3), 0.01, np.float32)
    img[..., 0] = 0.12                                                # contrast leaves R just above 0, G and B below
    out = np.clip(post.grade(img, {"vignette": 0, "contrast": 1.3, "lift": 0.035}), 0, 1)
    r, g, b = out[..., 0].mean(), out[..., 1].mean(), out[..., 2].mean()
    assert r < 0.15 and r - min(g, b) < 0.08                          # no saturated red
    assert out.mean() > 0.01                                          # still lifted off black


def test_bright_grade_lift_all_negative_pixel_lands_near_the_lift():
    """An all-negative pixel after contrast lifts to a grey near the lift value, never blown up."""
    img = np.full((4, 4, 3), 0.02, np.float32)
    out = post.grade(img, {"vignette": 0, "contrast": 1.3, "lift": 0.035})
    assert np.allclose(out, 0.035, atol=0.003)


def test_music_plays_under_the_whole_film():
    """Owner, 2026-11-03: "there is background music". A gap in the score is filled with a quiet drone and pad."""
    spec = {"sections": [{"at": "L02", "voices": ["musicbox"], "energy": 0.6}, {"at": "L04", "voices": [], "energy": 0}]}
    m = polish.music_spec(spec)
    assert m["sections"][0]["at"] == 0
    assert all(any(v in s["voices"] for v in polish.SUSTAIN) for s in m["sections"])
    assert "musicbox" in m["sections"][0]["voices"]                                  # the story's own voices stay
    st, tl = story(music={"root": 45, "bpm": 66, **spec})
    mus = sound.score(tl, polish.music_spec(st["music"]))
    w = int(0.5 * SR)
    blocks = np.sqrt((mus.mean(axis=1)[: len(mus) // w * w].reshape(-1, w) ** 2).mean(axis=1))
    assert blocks[:-1].min() > 1e-4                                                  # no silent half second


def test_fewer_sound_effects_by_default():
    """Owner, 2026-11-03: the hits use few effects. No whoosh on plain cuts, one opening key-word hit."""
    st, tl = story()
    p = polish.spec(st)
    at = timeline.resolver(tl["lines"], tl["duration"])
    ev = polish.sound_events(tl, st, p, at)
    emph = polish.emph_times(tl, p, at)
    assert all(any(abs(e["t"] + 0.12 - t) < 1e-6 for t in emph) for e in ev if e["kind"] == "whoosh")
    assert sum(e["kind"] == "lowhit" for e in ev) <= 1
    risers = sorted(e["t"] + e["dur"] for e in ev if e["kind"] == "riser")
    assert all(b - a >= p["riser_gap"] - 1e-6 for a, b in zip(risers, risers[1:]))


def test_pace_angle_cuts_split_long_shots_and_skip_reveals():
    """v2.3 (craft metrics blocks, 2026-11-03): angle cuts inside long shots, each on a caption change, never in a
    reveal shot or a shot that touches a quiet span, never leaving a part under 0.6 s."""
    st, tl = story()
    p = polish.spec(st)
    rts = polish.reframe_times(tl, p)
    assert rts
    calm = set(tl["motion"]["calm_shots"])
    caps = [c["start"] for c in tl["captions"]]
    for s in tl["shots"]:
        inside = [t for t in rts if s["start"] < t < s["end"]]
        if s["id"] in calm or s["end"] - s["start"] < p["reframe_min"]:
            assert not inside
        edges = [s["start"], *inside, s["end"]]
        assert all(b - a >= 0.6 - 1e-9 for a, b in zip(edges, edges[1:])) or not inside
    assert all(any(abs(t - c) < 1e-9 for c in caps) for t in rts)
    q = {**p, "quiet": [["L01", "end"]]}
    assert polish.reframe_times(tl, q) == []


def test_held_shots_keep_their_frame_and_short_shots_push_gently():
    """Critic, ep32 v2.3 round 2: a frame-exact shot (the twist's comparison) is held at crop 1.0, and a 0.4 s shot
    doesn't rush a 12% push."""
    st, tl = story()
    p = polish.spec(st)
    sid = tl["shots"][2]["id"]
    held = {**p, "hold": [sid], "punch": 0, "drift": 0}
    s = tl["shots"][2]
    assert all(polish.motion(tl, st, held, (s["f0"] + k) / tl["fps"], [])[0] == 1.0 for k in range(s["f1"] - s["f0"]))
    assert not [t for t in polish.reframe_times(tl, held) if s["start"] < t < s["end"]]
    short = {"id": "X", "start": 0.0, "end": 0.4, "f0": 0, "f1": 12, "step": 1}
    tl2 = {**tl, "shots": [short]}
    zs = [polish.motion(tl2, st, {**p, "punch": 0}, k / 30, [])[0] for k in range(12)]
    assert max(zs) - min(zs) <= 0.045                       # about 4% at most on a 0.4 s shot (critic)


def test_meter_panel_needs_me_or_ines():
    """A "meter" cue with no me/ines keys (another story's own cue name) never draws ep28's tower panel."""
    from PIL import Image
    blank = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    other = blank.copy()
    post.draw_meter(other, 1.0, {"cues": [{"name": "meter", "t": 0.0, "n": 0}]})
    assert other.tobytes() == blank.tobytes()
    ep28 = blank.copy()
    post.draw_meter(ep28, 1.0, {"cues": [{"name": "meter", "t": 0.0, "me": 7, "ines": 4, "dur": 0.0}]})
    assert ep28.tobytes() != blank.tobytes()


def test_ones_all_draws_every_frame():
    st, tl = story()
    assert all(s["step"] == 1 for s in tl["shots"])


def test_punch_max_keeps_the_hook_and_the_twist():
    # animation audit 2026-11-12: at most `punch_max` post punch-ins a film; the hook's own stays as it was
    st, tl = story()
    p = {**polish.spec(st), "punch_rate": None, "punch_gap": 0.5}
    at = timeline.resolver(tl["lines"], tl["duration"])
    full = polish.emph_times(tl, p, at)
    assert len(full) > 3
    capped = polish.emph_times(tl, {**p, "punch_max": 2, "twist": "L05"}, at)
    assert len(capped) == 2
    assert capped[0] == full[0]                                         # the hook punch-in is untouched
    assert polish.on_key(tl, at("L05")) in capped                       # the twist line gets the other
    assert polish.emph_times(tl, {**p, "punch_max": 0}, at) == full     # off by default
    assert polish.DEFAULTS["punch_max"] == 0
    # the whoosh follows the punch-ins, so the hook's whoosh stays too
    ev = polish.sound_events(tl, st, {**p, "punch_max": 2, "twist": "L05"}, at)
    assert any(e["kind"] == "whoosh" and abs(e["t"] - (capped[0] - 0.12)) < 0.2 for e in ev)
