"""Offline tests for scripts/frames.py: synthetic frames, no Blender, no film.

One 2 s shot at 30 fps drawn on fours, like a preview (frames 0, 4, 8, ... 56), over a moving gradient: a clean
shot has no findings; a run of flat frames is blank; a block appearing after frame 0 is a pop; a shot that opens
dark and brightens over 0.3 s is dark."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import frames  # noqa: E402

FPS = 30


def tl(n_shots=1, fx=None):
    """n 2 s shots; no fades, like a loop that cuts straight into frame 0 (ep116)."""
    shots = [{"id": f"S{i + 1:02d}", "start": 2.0 * i, "end": 2.0 * (i + 1), "f0": 60 * i, "f1": 60 * (i + 1),
              "step": 2} for i in range(n_shots)]
    return {"fps": FPS, "frames": 60 * n_shots, "duration": 2.0 * n_shots, "fx": fx or [], "fade_in": False,
            "fade_out": False, "shots": shots}


def scene(f, gain=1.0):
    """A soft gradient that drifts a little each frame, with a mid-grey floor: a lit room, a slow push."""
    y, x = np.mgrid[0:96, 0:54]
    g = 0.3 + 0.4 * (x + y + f * 0.5) % 54 / 54
    img = np.stack([g, g * 0.9, g * 0.8], -1) * gain
    return np.clip(img, 0, 1).astype(np.float32)


def shot(fn=scene, f0=0, f1=60, step=4):
    return {f: fn(f) for f in range(f0, f1, step)}


def run(fs, t=None):
    return frames.lint(fs, t or tl())


def checks(rows):
    return {r["check"] for r in rows}


def test_clean_shot():
    assert run(shot()) == []


def test_blank_frames():
    fs = shot()
    for f in (20, 24, 28):   # the camera inside a wall: one flat colour
        fs[f] = np.full((96, 54, 3), 0.55, np.float32)
    rows = run(fs)
    assert checks(rows) == {"blank"}
    assert len(rows) == 1 and "3 drawn frames" in rows[0]["detail"]


def test_black_fx_is_meant():
    fs = shot()
    for f in (20, 24):
        fs[f] = np.zeros((96, 54, 3), np.float32)
    assert run(fs, tl(fx=[{"t": 0.6, "kind": "black", "dur": 0.4}])) == []


def test_pop_on_frame_0():
    def late(f):   # a character (a dark block) is missing on the shot's first drawing, there from the next
        img = scene(f)
        if f > 0:
            img[30:70, 18:36] = (0.12, 0.08, 0.06)
        return img
    rows = run(shot(late))
    assert checks(rows) == {"pop"}


def test_steady_motion_is_no_pop():
    def walk(f):   # a block that walks across steadily from the first drawing: the same change every drawing
        img = scene(f)
        x = 2 + f // 2
        img[30:70, x:x + 10] = (0.12, 0.08, 0.06)
        return img
    assert run(shot(walk)) == []


def test_dark_opening():
    def fade(f):   # a fill light fading up over 0.3 s after the cut, then holding
        return scene(f, 0.5 + 0.5 * min(1.0, f / FPS / 0.3))
    rows = run(shot(fade))
    assert checks(rows) == {"dark"}


def test_dark_all_through_or_flicker_is_not_a_fade():
    assert run(shot(lambda f: scene(f, 0.15))) == []   # a dark shot that stays dark
    flick = shot(lambda f: scene(f, 0.6 if f in (0, 24, 48) else 1.0))   # a flicker: it falls back after
    assert "dark" not in checks(run(flick))


def test_the_fade_in_is_meant():
    t = tl()
    t["fade_in"] = True
    assert run(shot(lambda f: scene(f, 0.1 if f == 0 else 1.0)), t) == []


def test_frames_ok_skips_the_shot():
    fs = shot()
    fs[20] = np.full((96, 54, 3), 0.55, np.float32)
    assert frames.lint(fs, tl(), {"S01"}) == []


def test_reads_a_frames_folder(tmp_path):
    from PIL import Image
    for f, img in shot().items():
        Image.fromarray((img * 255).astype(np.uint8)).save(tmp_path / f"f{f:05d}.png")
    fs = frames.read_dir(tmp_path)
    assert sorted(fs) == list(range(0, 60, 4)) and fs[0].shape == (96, 54, 3)
    assert run(fs) == []
