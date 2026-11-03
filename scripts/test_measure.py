"""Offline tests for scripts/measure.py: a tiny synthetic film made by ffmpeg, and a tiny story. No network."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))
import measure  # noqa: E402

FFMPEG = shutil.which("ffmpeg") and shutil.which("ffprobe")
need_ffmpeg = pytest.mark.skipif(not FFMPEG, reason="ffmpeg isn't installed")


def make_clip(path: Path):
    """6 s at 30 fps, 216 x 384: a moving test pattern (0-2 s), a still blue card (2-4 s), a pattern sliding
    right (4-6 s). Sound: a quiet tone with three clicks (1, 3, 5 s) and true silence from 2.0 to 2.5 s."""
    v = ("testsrc2=s=216x384:r=30:d=2[a];color=c=0x2040c0:s=216x384:r=30:d=2[b];"
         "testsrc=s=432x384:r=30:d=2,crop=216:384:'t*40':0[c];[a][b][c]concat=n=3:v=1:a=0,format=yuv420p[v]")
    a = ("aevalsrc='if(between(t,2,2.5),0,0.05*sin(2*PI*220*t)"
         "+if(lt(mod(t-1,2),0.004),0.8*sin(2*PI*3000*t),0))':s=48000:d=6[aud]")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-filter_complex", f"{v};{a}", "-map", "[v]",
                    "-map", "[aud]", "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-b:a", "192k", str(path)],
                   check=True)


def tiny_story(d: Path):
    st = {"name": "tiny", "lines": [
        {"id": "L01", "who": "narrator", "chunks": [["Never SIT", "Never sit"], ["at the BACK.", "at the back."]]},
        {"id": "L02", "who": "me", "chunks": [["I sat", "I sat"], ["there.", "there."]]}],
        "cast": {"me": {"age": "adult", "skin": "#f1c9a0"}},
        "shots": [{"id": "S1", "cam": [[0, [0, -3, 1.5], [0, 0, 1.5], 50]]},
                  {"id": "S2", "at": "L02", "cam": [[0, [0, -1.2, 1.5], [0, 0, 1.5], 50],
                                                   [1, [0, -1.0, 1.6], [0, 0, 1.5], 55]]}],
        "acting": {"me": [{"at": 0, "pos": [0, 0]}, {"at": 1.0, "pos": [0, 0]}, {"at": 2.0, "pos": [2, 0]}]},
        "fx": [{"at": "L01.1", "kind": "punch", "dur": 0.4, "zoom": 1.1}],
        "sound": {"sfx": [{"at": "L01.1", "kind": "hit"}]}}
    voice = {"voice": "am_adam", "lines": {
        "L01": {"text": "Never sit at the back.", "onset": 0.2, "end": 1.4, "chunks": [[0.2, 0.6], [0.7, 1.4]]},
        "L02": {"text": "I sat there.", "onset": 0.1, "end": 1.0, "chunks": [[0.1, 0.5], [0.5, 1.0]]}}}
    d.mkdir(parents=True, exist_ok=True)
    (d / "story.json").write_text(json.dumps(st))
    (d / "voice-timings.json").write_text(json.dumps(voice))
    return d


@need_ffmpeg
def test_picture_finds_cuts_stills_and_colour(tmp_path):
    clip = tmp_path / "c.mp4"
    make_clip(clip)
    info = measure.probe(clip)
    assert abs(info["duration"] - 6) < 0.1 and info["fps"] == 30
    m = measure.picture(measure.read_frames(clip), info["fps"])
    assert m["cuts"] == 2
    assert [round(t) for t in m["cut_times"]] == [2, 4]
    assert 1.5 <= m["longest_still_s"] <= 2.1          # the blue card
    assert m["camera_motion_share"] > 0.2              # the slide in the last 2 s
    assert m["saturation_mean"] > 0.3 and 0.05 < m["brightness_mean"] < 0.9
    assert m["picture_changes_per_10s"] > 0


@need_ffmpeg
def test_sound_finds_clicks_silence_and_loudness(tmp_path):
    clip = tmp_path / "c.mp4"
    make_clip(clip)
    x = measure.read_audio(clip)
    on = measure.onsets(x)
    for t in (1.0, 3.0, 5.0):
        assert any(abs(o - t) < 0.06 for o in on), (t, on)
    s = measure.sound(x, None, None, measure.ebur128(clip))
    assert s["lufs"] is not None and s["lufs"] < -10
    assert 0.05 < s["silence_share"] < 0.12             # 0.5 s of 6
    assert s["hf_share_max_5s"] >= s["hf_share"]


def test_edit_metrics_from_a_tiny_story(tmp_path):
    d = tiny_story(tmp_path / "tiny")
    res = measure.measure(None, d)
    sp = res["spec"]
    assert sp["shots"] == 2 and sp["transitions"]["cut"] == 1 and sp["transitions"]["punch"] == 1
    assert sp["caption_share"] > 0.7 and sp["caption_words_max"] <= 3
    assert sp["walks"] == 1 and sp["walk_dead_end_share"] == 1.0   # a linear walk starts and stops dead
    assert sp["face_big_share"] > 0                    # S2 is a close-up at 1.2 m
    assert sp["camera_move_share"] > 0                 # S2 pushes in
    assert sp["sound_events_per_10s"] > 0
    assert res["checks"] and all(c["status"] in ("ok", "warn") for c in res["checks"])
    assert "| metric |" in measure.table(res)


def test_project_centre_and_width():
    loc, tgt = np.array([0, -2.0, 1.5]), np.array([0, 0, 1.5])
    x, y, wpm = measure.project(loc, tgt, 50, np.array([0, 0, 1.5]))
    assert abs(x) < 1e-9 and abs(y) < 1e-9
    # 2 m away with a 50 mm lens on a 24 mm tall sensor: the frame is 0.54 m wide
    assert abs(1 / wpm - 2 * 12 / 50 * 1080 / 1920 * 2) < 1e-6
    assert measure.project(loc, tgt, 50, np.array([0, -3.0, 1.5])) is None   # behind the camera


def test_targets_name_real_metrics(tmp_path):
    d = tiny_story(tmp_path / "tiny")
    res = measure.measure(None, d)
    found = {c["metric"] for c in res["checks"]}
    for key in measure.TARGETS:
        if key.startswith(("sound.", "macro.")) or key == "micro.caption_sync_p90_ms":   # these need the film
            continue
        assert key in found, key


def test_confirmed_targets_block_and_the_rest_warn():
    res = {"macro": {"picture_changes_per_10s": 8.0, "brightness_mean": 0.2, "longest_still_q_s": 0.5}}
    st = {c["metric"]: c["status"] for c in measure.check(res)}
    assert st["macro.picture_changes_per_10s"] == "block"   # confirmed by the hit data
    assert st["macro.brightness_mean"] == "warn"            # not confirmed
    assert st["macro.longest_still_q_s"] == "ok"
    assert "**block**" in measure.table({**res, "checks": measure.check(res)})
