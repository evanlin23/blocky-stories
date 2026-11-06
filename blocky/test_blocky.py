"""Tests for the blocky story engine. No Blender, no TTS: stories are checked from their committed word timings."""

import json
import math
from pathlib import Path

import pytest

from blocky import acting, checks, faces, post, timeline

STORIES = sorted(p.name for p in timeline.STORIES.iterdir()
                 if (p / "story.json").exists() and not p.name.startswith("_")) if timeline.STORIES.exists() else []


def tiny_story(**over):
    st = {"name": "t", "title": "the night bus", "made_for_kids": False, "premise": "p", "twist": "w",
          "cast": {"me": {"age": "teen", "skin": "#f1c9a0", "face": {"eyes": "round"}}},
          "lines": [{"id": "L01", "chunks": [["On my STREET,", "On my street,"], ["nobody SLEEPS.", "nobody sleeps."]]},
                    {"id": "L02", "who": "me", "chunks": [["Who's THERE?", "Who's there?"]]}],
          "shots": [{"id": "S1", "cam": [[0, [0, -3, 1.5], [0, 0, 1.5], 30]]},
                    {"id": "S2", "at": "L02", "cam": [[0, [0, -2, 1.5], [0, 0, 1.5], 40]]}],
          "acting": {"me": [{"at": 0, "pos": [0, 0]}, {"at": "L01.1", "pos": [0, 0]}, {"at": "L02", "pos": [0, 3.0]}]}}
    st.update(over)
    return st


def tiny_voice():
    return {"voice": "am_adam", "rate": 1.45, "tempo": 1.03, "model": "x", "lines": {
        "L01": {"text": "On my street, nobody sleeps.", "onset": 0.05, "end": 1.4, "chunks": [[0.05, 0.6], [0.65, 1.4]]},
        "L02": {"text": "Who's there?", "onset": 0.04, "end": 0.6, "chunks": [[0.04, 0.6]]}}}


@pytest.fixture
def tl():
    return timeline.build(tiny_story(), tiny_voice())


def test_time_references(tl):
    at = timeline.resolver(tl["lines"], tl["duration"])
    l1, l2 = tl["lines"]["L01"], tl["lines"]["L02"]
    assert at("L01") == l1["onset"] and at("L01>") == l1["end"]
    assert at("L01.1") == l1["chunks"][1][0] and at("L02+0.5") == pytest.approx(l2["onset"] + 0.5)
    assert at("end-1") == pytest.approx(tl["duration"] - 1)
    assert l2["onset"] == pytest.approx(l1["end"] + timeline.GAP, abs=1e-3)


def test_captions_follow_the_voice(tl):
    caps = tl["captions"]
    assert [c["text"] for c in caps] == ["On my STREET,", "nobody SLEEPS.", "Who's THERE?"]
    assert all(c["end"] - c["start"] >= 0.1 - 1e-6 for c in caps)
    # every caption starts on its own first word, never late (owner: captions were "out of sync with the voice")
    onsets = [a for l in tl["order"] for a, _b, _t in tl["lines"][l]["chunks"]]
    assert all(any(abs(c["start"] - (a - timeline.CAPTION_LEAD)) < 1e-3 for a in onsets) for c in caps)
    assert all(a["end"] <= b["start"] + 1e-6 for a, b in zip(caps, caps[1:]))


def test_frame_zero_takes_the_last_of_the_keys_stacked_at_zero():
    """Keys stacked at 0 (a generator's "hide everyone" at the origin, then the shot's own place): frame 0 poses from
    the last of them, as frame 1 does, so nothing pops on frame 0 or on a loop wrap (ep116: Grandpa missing on
    frame 0 of S01, there on frame 1)."""
    st = tiny_story(acting={"me": [{"at": 0, "pos": [0, 0], "hidden": True}, {"at": 0, "pos": [0, 0]},
                                   {"at": 0, "pos": [3.1, 1.0], "blend": 0.0, "hidden": False, "yaw": 90,
                                    "arms": [20, 0], "head": [10, 0], "lean": 3, "expr": "worried"},
                                   {"at": "L02", "pos": [3.1, 1.0]}]})
    tl = timeline.build(st, tiny_voice())
    f0, f1 = acting.state(tl, "me", 0.0), acting.state(tl, "me", 1 / 30)
    for k in ("x", "y", "z", "yaw", "arms", "head_yaw", "lean", "expr", "hidden"):
        assert f0[k] == pytest.approx(f1[k]) if not isinstance(f0[k], str) else f0[k] == f1[k], k
    assert (f0["x"], f0["y"], f0["hidden"]) == (3.1, 1.0, False)
    # before a first key that isn't at 0, the character holds that key's place (unchanged)
    st2 = tiny_story(acting={"me": [{"at": "L01.1", "pos": [1, 2]}, {"at": "L01.1", "pos": [4, 5]},
                                    {"at": "L02", "pos": [4, 5]}]})
    tl2 = timeline.build(st2, tiny_voice())
    assert acting.position(tl2["acting"]["me"], 0.0)[:2] == (4, 5)


def test_only_characters_move_their_mouths(tl):
    assert tl["talk"]["me"] and all(a >= tl["lines"]["L02"]["onset"] - 1e-6 for a, _ in tl["talk"]["me"])


def test_walking_swings_legs_and_faces_the_way_it_goes(tl):
    t_mid = (tl["acting"]["me"][1]["t"] + tl["acting"]["me"][2]["t"]) / 2
    still = acting.state(tl, "me", 0.1)
    walk = acting.state(tl, "me", t_mid)
    assert still["legs"] == 0 and still["speed"] == 0
    assert walk["speed"] > 0 and abs(walk["yaw"] - math.pi) < 1e-6  # walking +y faces +y
    steps = acting.footsteps(tl, "me")
    assert len(steps) == int(3.0 / acting.STRIDE)


def test_faces_are_drawn_and_refuse_the_default_look():
    im = faces.face_image({"eyes": "round"}, "#f1c9a0", "scared", 0.5)
    assert im.size == (faces.TEX_W, faces.TEX_H)
    assert faces.check_original({"eyes": "classic", "default_expr": "smirk"})
    assert not faces.check_original({"eyes": "round"})


@pytest.mark.parametrize("line,why", [
    ("This is a true story.", "claims"),
    ("It really happened to my cousin.", "claims"),
    ("There was blood on the stairs.", "graphic"),
    ("He killed the lights", "graphic"),
    ("I found it on Roblox", "name"),
    ("The little girl was dragged under.", "child"),
])
def test_check_blocks(line, why):
    st = tiny_story(lines=[{"id": "L01", "chunks": [[line, line]]}])
    blocks = [m for lvl, m in checks.run("t", None, st) if lvl == "block"]
    assert blocks, line


def test_check_passes_plain_fiction_and_needs_ages_and_not_for_kids():
    assert not [m for lvl, m in checks.run("t", None, tiny_story()) if lvl == "block"]
    st = tiny_story(made_for_kids=True)
    assert any("made_for_kids" in m for _, m in checks.run("t", None, st))
    st = tiny_story(cast={"me": {"age": "child", "skin": "#f1c9a0"}})
    assert any("age" in m for _, m in checks.run("t", None, st))


def test_caption_layout_reads_on_a_phone():
    im, m = post.caption_image("nobody SLEEPS.", False)
    assert m["cap_h"] >= 56 and m["lines"] <= 2
    assert not post.layout_problems([{"text": "In this TOWN,"}, {"text": "THUD", "big": True}])


@pytest.mark.parametrize("name", STORIES)
def test_every_story_passes_its_checks(name, tmp_path):
    vt = timeline.STORIES / name / "voice-timings.json"
    assert vt.exists(), f"{name}: run `python -m blocky voice {name}`"
    p = tmp_path / "tl.json"
    tl = timeline.write(name, vt, p)
    # 20 s floor: the writer's ultra-short arm runs 20 to 45 s (.claude/agents/writer.md, RULES length test)
    assert 20 <= tl["duration"] <= 180
    blocks = [m for lvl, m in checks.run(name, p) if lvl == "block"]
    assert blocks == []


# ---- round 2 of ep11 (decision r1, E1 to E4)

def test_mouth_track_opens_a_mouth_without_a_line():
    """E1: a mouth key ramps a mouth on any character, spoken or not, and takes the larger of it and the flaps."""
    st = tiny_story()
    st["acting"]["me"] += [{"from": "L01.1", "to": "L01>", "mouth": [0.0, 0.5]},
                           {"from": "L01>", "to": "L02>", "mouth": [0.5, 0.5]}]
    tl = timeline.build(st, tiny_voice())
    l1 = tl["lines"]["L01"]
    assert acting.state(tl, "me", 0.1)["mouth"] == 0.0                      # before the key: shut
    a, b = l1["chunks"][1][:2]
    mid = acting.state(tl, "me", (a + l1["end"]) / 2)["mouth"]
    assert 0.0 < mid < 0.5                                                  # opening, with nobody speaking
    assert acting.state(tl, "me", l1["end"] + 0.01)["mouth"] == pytest.approx(0.5)
    # over a spoken line the flaps still open it wider, and it never closes below the track
    l2 = tl["lines"]["L02"]
    vals = [acting.state(tl, "me", l2["onset"] + k * 0.01)["mouth"] for k in range(int((l2["end"] - l2["onset"]) * 100))]
    assert min(vals) >= 0.5 - 1e-9 and max(vals) > 0.9
    assert acting.state(tl, "me", tl["lines"]["L02"]["end"] + 0.05)["mouth"] == 0.0


def test_the_seam_never_goes_round_and_opens_in_fine_steps():
    """E1: the "line" mouth parts into a slit at any opening (never a round mouth), and still passes check_original."""
    import numpy as np

    face = {"eyes": "none", "mouth": "line", "brows": False}
    assert not faces.check_original(face)
    for k in (0.35, 0.75, 1.0):
        im = np.asarray(faces.face_image(face, "#a9adb1", "blank", k).convert("L"))
        ys, xs = np.nonzero(im < 40)
        w, h = xs.max() - xs.min(), ys.max() - ys.min()
        assert w > 5 * h, (k, w, h)
    assert faces.face_key(face, "#a9adb1", "blank", 0.3, (0, 0), 0) != faces.face_key(face, "#a9adb1", "blank", 0.4, (0, 0), 0)


def test_new_expressions_are_drawn():
    for e in ("terrified", "squeeze", "fish", "laugh"):
        assert e in faces.EXPRESSIONS
        assert faces.face_image({"eyes": "round"}, "#f1c9a0", e).size == (faces.TEX_W, faces.TEX_H)


def test_blink_hold_and_tremble():
    st = tiny_story()
    st["acting"]["me"] += [{"at": 0, "blink": False, "tremble": 3.0}]
    tl = timeline.build(st, tiny_voice())
    assert all(acting.state(tl, "me", k * 0.01)["blink"] == 0.0 for k in range(400))
    yaws = {round(acting.state(tl, "me", k * 0.013)["head_yaw"], 4) for k in range(50)}
    assert len(yaws) > 10 and max(abs(y) for y in yaws) <= math.radians(3.0) * 1.3


def test_cast_voices():
    """E2: a cast member's own Kokoro voice merges over the narrator's, and only for their lines."""
    from blocky import voice

    st = {"voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},
          "cast": {"woman": {"voice": {"voice": "af_heart", "tempo": 1.0, "rate": 1.15}},
                   "rider4": {"voice": {"voice": "am_michael", "tempo": 0.95}}}}
    assert voice.voice_for(st, "narrator") == {"voice": "am_adam", "tempo": 1.03, "rate": 1.45}
    assert voice.voice_for(st, "woman") == {"voice": "af_heart", "tempo": 1.0, "rate": 1.15}
    assert voice.voice_for(st, "rider4") == {"voice": "am_michael", "tempo": 0.95, "rate": 1.45}
    assert voice.voice_for(st, "me")["voice"] == "am_adam"


def test_asr_spellings_are_not_wrong_words():
    from blocky import voice

    assert voice.same_spoken("grey", "gray") and voice.same_spoken("handprint", "hand print")
    assert voice.same_spoken("eleven", "11") and voice.same_spoken("mannequin's", "mannequins")
    assert voice.same_spoken("back too", "back to")
    assert not voice.same_spoken("collar", "color") and not voice.same_spoken("six", "sex")


def _mix_story(drops, sfx):
    st = tiny_story(sound={"ambience": [{"kind": "rain", "from": 0, "to": "end", "lufs": -30}], "sfx": sfx,
                           "music_drops": drops},
                    music={"root": 45, "bpm": 66, "sections": [{"at": 0, "voices": ["drone", "pad"], "energy": 0.5}]})
    return st


def test_music_drops_silence_everything_but_the_voice_and_kept_hits(tmp_path):
    """E3: a drop takes the music, ambience and effects down at least 15 dB (the voice and a kept sting play on),
    anchored to line ids."""
    import numpy as np
    import wave

    from blocky.synth import SR
    from blocky import sound

    vo = tmp_path / "vo"
    vo.mkdir()
    for lid, n in (("L01", 1.5), ("L02", 0.7)):
        with wave.open(str(vo / f"{lid}.wav"), "wb") as w:
            w.setnchannels(1), w.setsampwidth(2), w.setframerate(24000)
            w.writeframes(np.zeros(int(n * 24000), "<i2").tobytes())   # a silent voice, so only the bed is measured
    voice = tiny_voice()
    st = _mix_story([], [])
    tl = timeline.build(st, voice)
    a, b = tl["lines"]["L01"]["chunks"][1][0], tl["lines"]["L02"]["end"]   # L01.1 to L02>
    rms = lambda x, t0, t1: float(np.sqrt(np.mean(x[int(t0 * SR):int(t1 * SR)] ** 2)) + 1e-12)
    open_, _ = sound.mix(tl, st, vo)
    st2 = _mix_story([{"from": "L01.1", "to": "L02>"}], [{"at": "L01.1+0.3", "kind": "sting", "dur": 0.5, "keep": True}])
    tl2 = timeline.build(st2, voice)
    shut, _ = sound.mix(tl2, st2, vo)
    st3 = _mix_story([["L01.1", "L02>"]], [])
    shut3, _ = sound.mix(timeline.build(st3, voice), st3, vo)
    # the hole, away from the kept sting: compare to the same moment with no drop (master gains differ, so
    # compare each mix's hole to its own level before the hole)
    pre = (0.05, a - 0.05)
    hole = (b - 0.35, b - 0.02)
    depth_open = 20 * np.log10(rms(open_, *hole) / rms(open_, *pre))
    depth_shut = 20 * np.log10(rms(shut3, *hole) / rms(shut3, *pre))
    assert depth_open - depth_shut >= 15
    # the kept sting sounds inside the hole
    sting = (a + 0.3, a + 0.6)
    assert rms(shut, *sting) > 10 * rms(shut3, *sting)


def test_no_tail_means_no_black_and_room_for_the_last_caption(tmp_path):
    """E4: tail 0 ends on picture: no fade on the last frames, and the last caption still gets MIN_CAPTION."""
    import numpy as np
    from PIL import Image

    st = tiny_story(tail=0)
    tl = timeline.build(st, tiny_voice())
    last = tl["lines"]["L02"]
    assert tl["tail"] == 0 and tl["duration"] < last["end"] + 0.5
    assert tl["captions"][-1]["end"] - tl["captions"][-1]["start"] >= timeline.MIN_CAPTION - 1e-6
    assert tl["captions"][-1]["end"] <= tl["duration"] + 1e-9
    raw = tmp_path / "f.png"
    Image.new("RGB", (270, 480), (128, 128, 128)).save(raw)
    st["grade"] = {"grain": 0.0, "vignette": 0.0, "bloom": 0.0}
    n = tl["frames"]
    end = post.finish(tl, st, n - 1, raw).astype(float)[200:400, 100:300].mean()
    mid = post.finish(tl, st, n // 2, raw).astype(float)[200:400, 100:300].mean()
    first = post.finish(tl, st, 0, raw).astype(float)[200:400, 100:300].mean()
    assert abs(end - mid) < 3 and abs(first - mid) < 3
    tl_tail = timeline.build(tiny_story(tail=1.0), tiny_voice())
    assert post.finish(tl_tail, st, tl_tail["frames"] - 1, raw).astype(float)[200:400, 100:300].mean() < mid * 0.4


def test_file_peak_is_fitted_after_the_encode():
    """The master can't see what AAC adds, so the mix limits lower until the encoded file measures under target."""
    import numpy as np

    from blocky.mixer import true_peak
    from blocky import sound

    t = np.arange(48000) / 48000
    x = np.stack([np.sin(2 * np.pi * 440 * t)] * 2, 1) * 10 ** (-2.0 / 20)
    overshoot = 0.8                                   # a stand-in encoder that adds 0.8 dB to the peak
    out, log = sound.fit_file_peak(x, lambda a: float(true_peak(a)) + overshoot)
    assert log[0][1] > sound.FILE_TP and log[-1][1] <= sound.FILE_TP
    assert float(true_peak(out)) + overshoot <= sound.FILE_TP


def test_a_distant_chunk_is_darker_with_a_tail():
    import numpy as np

    from blocky import sound

    sr = 24000
    y = np.zeros(sr)
    y[2400:4800] = np.sin(2 * np.pi * 3000 * np.arange(2400) / sr)   # a bright burst in chunk 0
    p = {"wav_at": 0.0, "chunks": [[0.1, 0.2, "TWO."], [0.5, 0.8, "In HIS"]],
         "space": {"chunks": [0], "lowpass": 1500, "verb": 0.6, "gain_db": -4}}
    out = sound.distant(y, p, sr)
    assert np.abs(out[2400:4800]).max() < 0.5 * np.abs(y[2400:4800]).max()   # the 3 kHz burst is filtered down
    assert np.abs(out[5000:9000]).max() > 1e-4                               # and a room tail follows it
    assert np.array_equal(out[23500:], y[23500:])                             # nothing changes past the tail


def test_pause_ids_are_time_references():
    """A pause beat's id resolves like a line's ("P01", "P01>", "P01-0.3"), so a knock's hole anchors to its beat."""
    st = tiny_story()
    st["lines"].insert(1, {"id": "P01", "pause": 0.6, "chunks": [["KNOCK KNOCK", ""]]})
    tl = timeline.build(st, tiny_voice())
    at = timeline.resolver(tl["lines"], tl["duration"])
    p = tl["lines"]["P01"]
    assert at("P01") == p["onset"] and at("P01>") == p["end"] and p["end"] - p["onset"] == pytest.approx(0.6)
    assert at("P01-0.3") == pytest.approx(p["onset"] - 0.3)
    assert at("L02") >= at("P01>") - 1e-9


def test_knock_patterns_land_on_their_times_and_tones_differ():
    """A knock plays its pattern's hits at their offsets, and the tones sound different: the floor's knock from
    below is deep and muffled, a knuckle on planks is sharper, and the door's pane rings."""
    import numpy as np

    from blocky.synth import SR
    from blocky import sound

    pat = [0.0, 0.62, 0.84]
    y = sound.sfx("knock", 3, 1.0, {"pattern": pat, "tone": "below"})
    env = np.convolve(np.abs(y), np.ones(240) / 240, "same")
    for t0 in pat:
        i = int(t0 * SR)
        assert env[i:i + int(0.06 * SR)].max() > 5 * env[int((t0 + 0.4 if t0 < 0.5 else 0.5) * SR)] or t0 > 0.5
    quiet = env[int(0.4 * SR):int(0.55 * SR)].max()
    assert env[int(0.62 * SR):int(0.68 * SR)].max() > 4 * quiet          # the gap after the first knock is a gap

    def centroid(tone):
        z = sound.knock_hit(tone, 1)
        S = np.abs(np.fft.rfft(z, 1 << 14))
        f = np.fft.rfftfreq(1 << 14, 1 / SR)
        return float((S * f).sum() / S.sum())

    def band(tone, lo, hi):
        z = sound.knock_hit(tone, 1)
        S = np.abs(np.fft.rfft(z, 1 << 14)) ** 2
        f = np.fft.rfftfreq(1 << 14, 1 / SR)
        return float(S[(f >= lo) & (f < hi)].sum() / S.sum())

    assert centroid("below") < 0.5 * centroid("hand") and centroid("below") < 0.5 * centroid("glass")
    assert band("glass", 1500, 2100) > 2 * band("hand", 1500, 2100)          # the pane rings
    assert np.abs(sound.knock_hit("glass_soft", 1)).max() < 0.5 * np.abs(sound.knock_hit("glass", 1)).max()
    old = sound.sfx("knock", 2, 1.0)                                         # no options: the old three thumps
    assert len(old) == sound.synth.n_samples(1.56)


def test_a_section_can_turn_to_another_mode():
    """A score section's own mode and root (the warm turn to the relative major) change only that section."""
    import numpy as np

    from blocky.synth import SR
    from blocky import sound

    tl = timeline.build(tiny_story(), tiny_voice())
    base = {"root": 38, "mode": "harmonic", "bpm": 58, "seed": 4,
            "sections": [{"at": 0, "voices": ["pad"], "energy": 0.4}, {"at": "L02", "voices": ["pad"], "energy": 0.4}]}
    turn = json.loads(json.dumps(base))
    turn["sections"][1].update(mode="major", root=41)
    a, b = sound.score(tl, base), sound.score(tl, turn)
    cut = int(tl["lines"]["L02"]["onset"] * SR)
    assert np.allclose(a[:cut - 10], b[:cut - 10])
    assert not np.allclose(a[cut + SR // 10:], b[cut + SR // 10:])


def test_a_flap_key_moves_a_mouth_under_reported_speech():
    """One voice: Ray's words are the narrator's, but his mouth flaps under them (a mouth key with "flap")."""
    st = tiny_story()
    st["acting"]["me"].append({"from": "L01", "to": "L01>", "mouth": [0.8, 0.8], "flap": True})
    tl = timeline.build(st, tiny_voice())
    a, b = tl["lines"]["L01"]["onset"], tl["lines"]["L01"]["end"]
    vals = [acting.state(tl, "me", a + k * 0.01)["mouth"] for k in range(int((b - a) / 0.01))]
    assert max(vals) > 0.7 and min(vals) < 0.1
    shut = sum(1 for x, y in zip(vals, vals[1:]) if x > 0.4 >= y)
    assert shut >= (b - a) / 0.11 * 0.6
    assert acting.state(tl, "me", b + 0.05)["mouth"] == 0.0


def test_a_pause_beat_pops_its_words_one_chunk_at_a_time():
    """A beat with several chunks shows them in turn, at its "times" or spread evenly, so a three-knock beat can
    put one big KNOCK on each knock instead of three words that won't fit."""
    st = tiny_story()
    st["lines"].insert(1, {"id": "P01", "pause": 1.5, "chunks": [["KNOCK", ""], ["KNOCK", ""], ["KNOCK", ""]],
                           "times": [0.0, 0.5, 1.0]})
    tl = timeline.build(st, tiny_voice())
    p = tl["lines"]["P01"]
    assert [round(a - p["onset"], 3) for a, _, _ in p["chunks"]] == [0.0, 0.5, 1.0]
    caps = [c for c in tl["captions"] if c["line"] == "P01"]
    assert len(caps) == 3 and all(c["big"] for c in caps)
    assert all(a["end"] <= b["start"] + 1e-6 for a, b in zip(caps, caps[1:]))
    st["lines"][1].pop("times")
    p = timeline.build(st, tiny_voice())["lines"]["P01"]
    assert [round(a - p["onset"], 3) for a, _, _ in p["chunks"]] == [0.0, 0.5, 1.0]


def test_a_homophone_is_a_spelling_not_a_wrong_word():
    """Whisper writes "threw" for "through" when the words around it suggest it: the same sound, listed as a
    spelling. A different word ("copped" for "copied") still counts as heard wrong."""
    from blocky import voice

    assert voice.same_spoken("through", "threw")
    assert not voice.same_spoken("copied", "copped")
    assert not voice.same_spoken("one eye", "when i")


def test_a_warm_grade_stays_under_saturated_red():
    """`grade.red_line` keeps every pixel of the picture under WCAG's saturated-red line (a linear red ratio of 0.8),
    so a warm, dark story doesn't flash red on every cut. Neutral pixels don't move, and the captions keep their red."""
    import numpy as np

    img = np.zeros((4, 4, 3), np.float32)
    img[0] = [0.42, 0.16, 0.14]      # oxblood
    img[1] = [0.25, 0.08, 0.05]      # a deep warm shadow
    img[2] = [0.5, 0.5, 0.5]         # grey
    img[3] = [0.85, 0.55, 0.3]       # honey wood
    out = post.red_clamp(img.copy(), 0.78)
    lin = post._to_lin(out)
    ratio = lin[..., 0] / np.maximum(lin.sum(axis=2), 1e-6)
    assert ratio.max() <= 0.781
    assert np.allclose(out[2], img[2], atol=1e-4) and np.allclose(out[3], img[3], atol=1e-4)
    assert abs(float(out[0, 0, 0]) - 0.42) < 1e-3           # the red channel itself is untouched
    st = tiny_story()
    st["grade"] = {"red_line": 0.78, "grain": 0.0, "vignette": 0.0, "bloom": 0.0}
    tl = timeline.build(st, tiny_voice())
    from PIL import Image
    raw = Path(__file__).parent / "_red_test.png"
    Image.new("RGB", (270, 480), (170, 40, 30)).save(raw)
    try:
        f = int(tl["captions"][0]["start"] * tl["fps"]) + 3
        a = post.finish(tl, st, f, raw).astype(np.float32) / 255
    finally:
        raw.unlink()
    lin = post._to_lin(a)
    sat = lin[..., 0] / np.maximum(lin.sum(axis=2), 1e-6) >= 0.8
    assert sat.mean() < 0.05          # only caption pixels (the key words) can be saturated red


def test_the_score_is_heard_through_water_until_the_filter_opens():
    """music.filter: a low-pass that moves. Closed, the highs are gone; once it opens they come back."""
    import numpy as np

    from blocky.synth import SR
    from blocky import sound

    x = np.random.default_rng(0).standard_normal(SR * 3)
    cut = sound.filter_track(len(x), [{"at": 0, "hz": 600}, {"at": 1.5, "hz": 16000, "dur": 0.2}], float)
    y = sound.lowpass_moving(x, cut)
    f = np.fft.rfftfreq(SR, 1 / SR)

    def hi_lo(seg):
        X = np.abs(np.fft.rfft(seg))
        return X[f > 4000].mean() / X[f < 300].mean()

    assert hi_lo(y[:SR]) < 0.01            # muffled
    assert hi_lo(y[2 * SR:3 * SR]) > 0.5   # open
    assert abs(len(y) - len(x)) == 0
    st = np.stack([x, x], 1)
    assert sound.lowpass_moving(st, cut).shape == st.shape


def test_new_sounds_and_the_bubbling_voice():
    """The applause of bubbles, the squeal of skin on acrylic and the rest exist, and are sounds, not silence. The
    bubble voice is the only change between two scores."""
    import numpy as np

    from blocky import sound

    for kind in ("pop", "bubbles", "tinybubbles", "squeak", "squeal", "glide", "hum_sweep", "castors"):
        y = sound.sfx(kind, 3, 1.2)
        assert len(y) > 100 and np.abs(y).max() > 0.05, kind
    assert len(sound.sfx("squeal", 1, 2.4)) > len(sound.sfx("squeak", 1, 2.4))
    tl = timeline.build(tiny_story(), tiny_voice())
    a = sound.score(tl, {"root": 33, "mode": "whole", "bpm": 50, "sections": [{"at": 0, "voices": ["pad"]}]})
    b = sound.score(tl, {"root": 33, "mode": "whole", "bpm": 50, "sections": [{"at": 0, "voices": ["pad", "bubble"]}]})
    assert not np.allclose(a, b)


def test_every_frame_belongs_to_its_own_shot():
    """A cut's first frame is drawn with its own shot, never the one before (a rounding bug once misplaced 32 cuts)."""
    for name in STORIES:
        tl = timeline.build(timeline.load_story(name), json.loads((timeline.STORIES / name / "voice-timings.json").read_text()))
        for s in tl["shots"]:
            for f in (s["f0"], s["f1"] - 1):
                t = f / tl["fps"]
                assert next(x for x in tl["shots"] if x["start"] <= t < x["end"])["id"] == s["id"], (name, s["id"], f)


def test_state_changes_never_land_inside_a_shots_first_frame():
    """A cue or acting key on a cut's word applies from the cut's own first frame (standards ep12 R7)."""
    for name in STORIES:
        tl = timeline.build(timeline.load_story(name), json.loads((timeline.STORIES / name / "voice-timings.json").read_text()))
        fr = 1.0 / tl["fps"]
        times = [c["t"] for c in tl["cues"]] + [k["t"] for ks in tl["acting"].values() for k in ks]
        for s in tl["shots"]:
            assert not any(s["start"] < t < s["start"] + fr - 1e-9 for t in times), (name, s["id"])


# ---- ep14 (mirror-maze): the copy's eyes, the bucket hat, the coat, the hood down and the hard fringe, all opt-in

def test_mirror_eyes_keep_the_round_outline_and_brows_but_have_no_white_pupil_or_glint():
    """The copy's "mirror" eyes: exactly a round eye's outline and size, near-black to the edge, nothing white
    inside, the brows and mouth kept; and a texture key of its own so a cached round-eye face is never reused."""
    import numpy as np

    skin = "#b07850"
    for expr in ("neutral", "blank", "scared", "wide", "smirk"):
        rnd = np.asarray(faces.face_image({"eyes": "round"}, skin, expr).convert("RGB")).astype(int)
        mir = np.asarray(faces.face_image({"eyes": "mirror"}, skin, expr).convert("RGB")).astype(int)
        sk = np.array(faces.hexrgb(skin))
        # the eye band: rows of the eyes, columns of the face box
        y0, y1 = int(faces._fy(0.42) - 0.14 * (faces.FX1 - faces.FX0)), int(faces._fy(0.42) + 0.14 * (faces.FX1 - faces.FX0))
        band = (slice(y0, y1), slice(faces.FX0, faces.FX1))
        drawn_r = np.abs(rnd[band] - sk).sum(axis=2) > 60
        drawn_m = np.abs(mir[band] - sk).sum(axis=2) > 60
        ys, xs = np.nonzero(drawn_r)
        ym, xm = np.nonzero(drawn_m)
        # never bigger: the same outer extent as the round eye
        assert abs(xs.min() - xm.min()) <= 2 and abs(xs.max() - xm.max()) <= 2, expr
        assert abs(ys.min() - ym.min()) <= 2 and abs(ys.max() - ym.max()) <= 2, expr
        # inside each eye (a box round its centre, well inside the outline): near-black, nothing white
        w = faces.FX1 - faces.FX0
        for side in (-1, 1):
            cx, cy, h = int(faces._fx(0.5) + side * 0.22 * w), int(faces._fy(0.42)), int(0.06 * w)
            core = (slice(cy - h, cy + h), slice(cx - h, cx + h))
            assert mir[core].max() < 30, expr                          # no white, no pupil, no glint
            assert rnd[core].max() > 230, expr                         # (the round eye has its white there)
    # the brows are drawn above the eyes, as on the round face
    above = (slice(int(faces._fy(0.42) - 0.26 * (faces.FX1 - faces.FX0)), int(faces._fy(0.42) - 0.13 * (faces.FX1 - faces.FX0))),
             slice(faces.FX0, faces.FX1))
    rnd = np.asarray(faces.face_image({"eyes": "round"}, skin, "blank").convert("RGB")).astype(int)
    mir = np.asarray(faces.face_image({"eyes": "mirror"}, skin, "blank").convert("RGB")).astype(int)
    assert np.array_equal(rnd[above], mir[above])
    assert "mirror" in faces.EYES and not faces.check_original({"eyes": "mirror"})
    assert faces.face_key({"eyes": "mirror"}, skin, "blank", 0, (0, 0), 0) != faces.face_key({"eyes": "round"}, skin, "blank", 0, (0, 0), 0)
    assert faces.face_key({"eyes": "round"}, skin, "blank", 0, (0, 0), 0) == "blank-0.0-0.0-0.0-0"   # unchanged


@pytest.fixture
def fake_rig(monkeypatch):
    """rig.py without Blender: a stand-in bpy records every part the rig builds (name -> its arguments)."""
    import importlib
    import sys
    import types

    class Mods:
        def new(self, name, kind):
            return types.SimpleNamespace(width=0.0, segments=0, limit_method="", keep_sharp=False)

    class Ob:
        def __init__(self, name):
            self.name, self.location, self.rotation_euler, self.scale = name, (0, 0, 0), (0, 0, 0), (1, 1, 1)
            self.hide_render, self.children_recursive = False, []
            self.modifiers, self.data = Mods(), types.SimpleNamespace(polygons=[])

    made = {}

    def part(kind):
        def f(name, *a, **k):
            made[name] = (kind, a, k)
            return Ob(name)
        return f

    monkeypatch.setitem(sys.modules, "bpy", types.ModuleType("bpy"))
    mu = types.ModuleType("mathutils")
    mu.Vector = tuple
    monkeypatch.setitem(sys.modules, "mathutils", mu)
    saved = {m: sys.modules.pop(m) for m in ("blocky.kit", "blocky.rig") if m in sys.modules}
    kit = importlib.import_module("blocky.kit")
    rig = importlib.import_module("blocky.rig")
    for nm in ("empty", "box", "cyl", "mesh_obj", "sphere", "plane"):
        monkeypatch.setattr(kit, nm, part(nm))
    monkeypatch.setattr(kit, "plastic", lambda c, *a, **k: f"plastic {c}")
    monkeypatch.setattr(kit, "glass", lambda *a, **k: "glass")
    monkeypatch.setattr(rig, "cloth", lambda spec, key: f"cloth {spec.get(key)}")
    monkeypatch.setattr(rig, "head_material", lambda name, skin: ("head", None))
    monkeypatch.setattr(rig, "head_mesh", part("head"))
    monkeypatch.setattr(rig.Character, "set_face", lambda self, *a: None)
    yield rig, made
    for m in ("blocky.kit", "blocky.rig"):
        sys.modules.pop(m, None)
    sys.modules.update(saved)
    import blocky as pkg
    for m, mod in saved.items():
        setattr(pkg, m.rsplit(".", 1)[1], mod)


BASE_SPEC = {"skin": "#d9a27a", "shirt": "#b8697a", "pants": "#17171b", "hair": "cap", "hair_c": "#141214",
             "face": {"eyes": "round"}}


def test_the_rig_defaults_build_no_new_parts(fake_rig):
    """Without the new options nothing new is built: ep11 to ep13's casts are unchanged (also checked in Blender:
    every existing cast member builds the same objects, transforms, meshes and materials)."""
    rig, made = fake_rig
    for spec in (BASE_SPEC, {**BASE_SPEC, "hair": "swoop", "hat": "fedora"}, {**BASE_SPEC, "hat": "ballcap"}):
        made.clear()
        c = rig.Character("x", spec, None)
        assert c.coat == []
        assert not [n for n in made if n.partition(".")[2].startswith(("bcrown", "bbrim", "coat", "zip", "hooddown",
                                                                         "fringe3"))]
        assert "x.hcap" in made


def test_the_bucket_hat_has_a_crown_and_a_brim_sloping_down_all_round(fake_rig):
    import numpy as np

    rig, made = fake_rig
    rig.Character("me", {**BASE_SPEC, "hat": "bucket", "hat_c": "#6f9a2e"}, None)
    assert made["me.bcrown"][0] == "cyl" and made["me.bbrim"][0] == "mesh_obj"
    assert "me.hcap" not in made                   # the crown covers the top: no block corners poking through
    verts, fcs = np.array(made["me.bbrim"][1][0]), made["me.bbrim"][1][1]
    r = np.hypot(verts[:, 0], verts[:, 1])
    outer, inner = verts[r > r.mean()], verts[r < r.mean()]
    assert outer[:, 2].max() < inner[:, 2].min()   # it slopes down, all the way round
    # every face of the brim faces outward from the ring's own centre line (no flipped normals)
    for f in fcs:
        p = verts[list(f)]
        n = np.cross(p[1] - p[0], p[2] - p[0])
        c = p.mean(axis=0)
        mid = np.array([c[0], c[1], 0.0]) / max(1e-9, np.hypot(c[0], c[1]))
        ring = np.array([mid[0] * (r.min() + r.max()) / 2, mid[1] * (r.min() + r.max()) / 2, verts[:, 2].mean()])
        assert np.dot(n, c - ring) > 0


def test_the_coat_swings_with_its_legs_and_the_hood_lies_down(fake_rig):
    rig, made = fake_rig
    c = rig.Character("tasha", {**BASE_SPEC, "hair": "swoop", "fringe": "hard", "extras": ["coat", "hooddown"]}, None)
    assert {"tasha.coatm-1", "tasha.coatm1", "tasha.zip", "tasha.hooddown", "tasha.fringe3"} <= set(made)
    assert len(c.coat) == 2
    c.pose(0, 0, 0, 0, legs=0.4)
    for hinge, sx in c.coat:   # each panel takes its own leg's swing, so a stride never pokes through it
        leg = c.P[f"leg{sx}"]
        assert hinge.rotation_euler == leg.rotation_euler and abs(hinge.rotation_euler[0]) == pytest.approx(0.4)
    # the hard fringe is only for a swoop
    made.clear()
    rig.Character("y", {**BASE_SPEC, "hair": "cap", "fringe": "hard"}, None)
    assert "y.fringe3" not in made


def test_mouth_inside_draws_an_open_mouth_as_a_hole_of_that_colour():
    """The copy's open mouth (face "mouth_inside"): the same size as the normal open mouth, that colour to its edge
    with no ink lip line; a shut mouth and every face without the option are drawn as before."""
    import numpy as np

    skin, black = "#b07850", "#07070a"
    w = faces.FX1 - faces.FX0
    cx, cy = int(faces._fx(0.5)), int(faces._fy(0.74))
    win = (slice(cy - int(0.08 * w), cy + int(0.08 * w)), slice(cx - int(0.12 * w), cx + int(0.12 * w)))
    sk = np.array(faces.hexrgb(skin))
    plain = np.asarray(faces.face_image({"eyes": "mirror"}, skin, "neutral", 0.67).convert("RGB")).astype(int)[win]
    hole = np.asarray(faces.face_image({"eyes": "mirror", "mouth_inside": black}, skin, "neutral", 0.67)
                      .convert("RGB")).astype(int)[win]
    drawn_p, drawn_h = np.abs(plain - sk).sum(2) > 60, np.abs(hole - sk).sum(2) > 60
    yp, xp = np.nonzero(drawn_p)
    yh, xh = np.nonzero(drawn_h)
    assert abs(xp.min() - xh.min()) <= 2 and abs(xp.max() - xh.max()) <= 2   # the same size
    assert abs(yp.min() - yh.min()) <= 2 and abs(yp.max() - yh.max()) <= 2
    ink = np.array(faces.hexrgb("#1a1416"))
    near_ink = lambda im: int((np.abs(im - ink).sum(2) < 8).sum())
    assert near_ink(plain) > 2000 and near_ink(hole) < near_ink(plain) / 20   # black to the edge: no ink lip line
    assert np.median(hole[drawn_h], axis=0).max() <= 10                     # and black inside
    shut = lambda f: np.asarray(faces.face_image(f, skin, "neutral", 0.0).convert("RGB"))
    assert np.array_equal(shut({"eyes": "mirror"}), shut({"eyes": "mirror", "mouth_inside": black}))
    k = lambda f: faces.face_key(f, skin, "neutral", 0.67, (0, 0), 0)
    assert k({"eyes": "mirror", "mouth_inside": black}) != k({"eyes": "mirror"})


def test_asleep_lids_are_opt_in_and_not_the_content_arcs():
    """ep17: Mum asleep at 3 a.m. "shut" draws up-arcs, which read as smiling eyes. "asleep" draws flat lids that
    droop at the outer ends. It's a new expression, so every existing face draws exactly as before."""
    import numpy as np
    face = {"eyes": "round", "brows": True}
    assert "asleep" in faces.EXPRESSIONS and not faces.check_original(face)
    asleep = np.asarray(faces.face_image(face, "#a86a58", "asleep").convert("L")).astype(int)
    for other in ("shut", "soft", "blank"):
        assert np.abs(asleep - np.asarray(faces.face_image(face, "#a86a58", other).convert("L")).astype(int)).sum() > 0
    # the lid's outer end sits lower than its inner end (a droop), on both eyes
    s = faces.FX1 - faces.FX0
    ey = faces._fy(0.42)
    ink = asleep < 80
    for side in (-1, 1):
        cx = faces._fx(0.5) + side * 0.22 * s
        inner = int(cx - side * 0.07 * s)
        outer = int(cx + side * 0.07 * s)
        rows_in = np.where(ink[:, inner])[0]
        rows_out = np.where(ink[:, outer])[0]
        rows_in = rows_in[np.abs(rows_in - ey) < 0.12 * s]
        rows_out = rows_out[np.abs(rows_out - ey) < 0.12 * s]
        assert rows_out.mean() > rows_in.mean()


def test_hall_and_ladder_homophones_are_not_wrong_words():
    """ep17: "the OLD HALL" and "No more LADDER". In General American "hall"/"haul" and the flapped
    "ladder"/"latter" are one sound, so Whisper writing either is a spelling, as "threw" for "through" is. Other
    words are still wrong words."""
    from blocky import voice
    assert voice.same_spoken("the old hall", "the old haul")
    assert voice.same_spoken("no more ladder", "no more latter")
    assert voice.same_spoken("right through it", "right threw it")
    assert not voice.same_spoken("the old hall", "the old hell")


def test_cardboard_sounds_are_opt_in():
    """ep17's three new kinds: a tape peel, a cardboard scrape (dull through a wall when distant), and a
    cardboard creak tone. The default creak is untouched."""
    import numpy as np
    from blocky import sound
    from blocky.synth import SR
    tape = sound.sfx("tape", 2)
    assert 0.5 * SR < len(tape) < 1.0 * SR and np.abs(tape).max() > 0.5
    near = sound.sfx("scrape", 4, 2.2, {})
    far = sound.sfx("scrape", 4, 2.2, {"distant": True})
    assert len(near) == len(far) > 2 * SR
    hf = lambda y: np.abs(np.fft.rfft(y))[int(1500 * len(y) / SR):].sum() / np.abs(np.fft.rfft(y)).sum()
    assert hf(far) < hf(near) * 0.6
    wood = sound.sfx("creak", 3, 1.0)
    assert np.allclose(wood, sound.sfx("creak", 3, 1.0, {})) and np.allclose(wood, sound.sfx("creak", 3, 1.0, {"tone": None}))
    card = sound.sfx("creak", 3, 1.0, {"tone": "cardboard"})
    assert len(card) == len(wood) and not np.allclose(card, wood) and np.abs(card).max() > 0.5


def test_mix_uses_samples_unless_the_story_turns_them_off(tmp_path):
    """sound.samples: false gives the old all-synthesized mix, and the switch never leaks into the next story."""
    import numpy as np
    import wave

    from blocky import sound

    vo = tmp_path / "vo"
    vo.mkdir()
    for lid, n in (("L01", 1.5), ("L02", 0.7)):
        with wave.open(str(vo / f"{lid}.wav"), "wb") as w:
            w.setnchannels(1), w.setsampwidth(2), w.setframerate(24000)
            w.writeframes(np.zeros(int(n * 24000), "<i2").tobytes())
    st = _mix_story([], [{"at": "L01", "kind": "door"}])
    st["sound"]["ambience"] = [{"kind": "rain", "from": 0, "to": "end", "lufs": -30}]
    tl = timeline.build(st, tiny_voice())
    rec, _ = sound.mix(tl, st, vo)
    st_off = json.loads(json.dumps(st))
    st_off["sound"]["samples"] = False
    syn, _ = sound.mix(tl, st_off, vo)
    assert sound.SAMPLES["on"] and np.isfinite(rec).all() and not np.allclose(rec, syn)
    assert np.allclose(sound.mix(tl, st, vo)[0], rec)                  # deterministic, and back on after "false"


def _sample(tl, name, t, defaults):
    """The cue sampler stories' set.py use (ep120's, verbatim in effect): fields eased over a cue's own "dur"."""
    cur, prev = dict(defaults), dict(defaults)
    for c in [c for c in tl["cues"] if c["name"] == name]:
        if c["t"] > t:
            break
        prev = dict(cur)
        cur.update({k: v for k, v in c.items() if k in defaults})
        dur = c.get("dur", 0.0)
        if dur > 0 and t < c["t"] + dur:
            u = min(1.0, max(0.0, (t - c["t"]) / dur))
            u = u * u * (3 - 2 * u)
            return {k: prev[k] + (cur[k] - prev[k]) * u for k in cur}
    return cur


def test_a_light_cue_at_a_cut_is_at_full_value_on_the_shots_first_frame():
    """ep120: Dad's fill cue at "L46-0.05" with dur 0.3 eased in after the cut, so the shot opened dark. Listed in
    light_cues, a cue on or just before a cut lands on the cut with no fade; a fade across a cut ends on it."""
    cues = [{"at": "L02-0.05", "name": "fill", "v": 1.0, "dur": 0.3},     # just before the cut
            {"at": "L02+0.3", "name": "fill", "v": 0.2, "dur": 0.3},      # inside the shot: its fade stays
            {"at": "L02", "name": "door", "v": 1.0, "dur": 0.5}]          # not a light: unchanged
    base = timeline.build(tiny_story(cues=cues), tiny_voice())
    cut = base["shots"][1]["start"]
    f0 = cut
    assert _sample(base, "fill", f0, {"v": 0.0})["v"] < 0.5          # the bug: the shot opens dark
    tl = timeline.build(tiny_story(cues=cues, light_cues=["fill"]), tiny_voice())
    assert _sample(tl, "fill", f0, {"v": 0.0})["v"] == 1.0
    assert _sample(tl, "fill", f0 - 1 / 30, {"v": 0.0})["v"] == 0.0   # the shot before keeps its light
    mid = [c for c in tl["cues"] if c["name"] == "fill"][1]
    assert mid["dur"] == 0.3 and mid["t"] > cut
    assert [c for c in tl["cues"] if c["name"] == "door"] == [c for c in base["cues"] if c["name"] == "door"]
    # a fade that runs across the cut ends on it; "fade": true keeps the fade as written
    across = timeline.build(tiny_story(cues=[{"at": "L02-0.5", "name": "fill", "v": 1.0, "dur": 1.0}],
                                       light_cues=["fill"]), tiny_voice())
    assert _sample(across, "fill", cut, {"v": 0.0})["v"] == 1.0
    keep = timeline.build(tiny_story(cues=[{"at": "L02-0.05", "name": "fill", "v": 1.0, "dur": 0.3, "fade": True}],
                                     light_cues=["fill"]), tiny_voice())
    assert _sample(keep, "fill", cut, {"v": 0.0})["v"] < 0.5


def test_caption_splitter_keeps_every_spoken_word():
    """A chunk with more spoken words than caption words keeps them all (ep115 L19: "has said 4:12" is read "has said
    four twelve"; the generators' copy sliced by caption count and voiced "has said four")."""
    assert timeline.split_chunk("has said 4:12", "has said four twelve") == [["has said 4:12", "has said four twelve"]]
    pieces = timeline.split_chunk("It was 9:14 PM, June TWELFTH.", "It was nine fourteen p m, June twelfth.")
    assert [c for c, _ in pieces] == ["It was 9:14", "PM, June TWELFTH."]
    assert [s for _, s in pieces] == ["It was nine fourteen", "p m, June twelfth."]
    for cap, sp in [("a b c d e f g", "a b c d e f g"), ("I owe 12 DOLLARS", "I owe twelve dollars"),
                    ("x", "one two three"), ("the 1990s went ON", "the nineteen nineties went on")]:
        got = timeline.split_chunk(cap, sp)
        assert " ".join(s for _, s in got).split() == sp.split()
        assert " ".join(c for c, _ in got).split() == cap.split()
        assert all(len(c.split()) <= 3 for c, _ in got)
    lines, cmap = timeline.split_lines([{"id": "L1", "chunks": [["one two three four", "one two three four"], ["five", "five"]]},
                                        {"id": "P1", "pause": 0.5, "chunks": [["THUD", ""]]}])
    assert lines[0]["chunks"] == [["one two", "one two"], ["three four", "three four"], ["five", "five"]]
    assert cmap == {"L1": [0, 2]} and lines[1]["chunks"] == [["THUD", ""]]


def test_check_finds_spoken_words_story_json_lost():
    st = {"lines": [{"id": "L19", "chunks": [["has said 4:12", "has said four"]]}]}
    src = [{"id": "L19", "chunks": [["has said 4:12", "has said four twelve"]]}]
    assert timeline.lost_words(st, src) and "twelve" in timeline.lost_words(st, src)[0]
    st["lines"][0]["chunks"] = timeline.split_lines(src)[0][0]["chunks"]
    assert timeline.lost_words(st, src) == []
