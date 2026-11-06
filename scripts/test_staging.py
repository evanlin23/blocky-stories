"""Offline tests for scripts/staging.py: synthetic acting keys, no Blender, no voice.

Two characters, Ann and Bo, in one 3 s shot with a camera 6 m back looking at them: a lurch (a key 0.067 s after
a hold 0.6 m away, ep125), a too-close pair (0.85 m apart side by side, ep132), a clean pair, a deliberate pair
listed in staging_ok, a walk (not a lurch) and a jump hidden by a cut."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import staging  # noqa: E402

SPEC = {"skin": "#f1c9a0", "shirt": "#3d6ea6", "pants": "#2c3550"}
CAM = [[0, [0, -6, 1.5], [0, 0, 1.0], 30]]


def film(acting, shots=None, extra=None):
    shots = shots or [{"id": "S01", "start": 0.0, "end": 3.0, "f0": 0, "f1": 90, "step": 1}]
    st = {"name": "tiny", "cast": {w: dict(SPEC) for w in acting},
          "shots": [{"id": s["id"], "cam": s.get("cam", CAM)} for s in shots]}
    st.update(extra or {})
    for s in shots:
        s.pop("cam", None)
    tl = {"name": "tiny", "fps": 30, "duration": 3.0, "frames": 90, "lines": {}, "order": [], "captions": [],
          "talk": {w: [] for w in acting}, "shots": shots, "cues": [], "fx": [], "motion": {},
          "acting": {w: [dict(k, at=k["t"]) for k in ks] for w, ks in acting.items()}}
    return st, tl


def found(st, tl):
    return {(r["check"], r["who"]) for r in staging.lint(st, tl)}


def test_lurch():
    # Ann holds at x -1.5, then a key 0.067 s later puts her 0.6 m away: a slide in 2 frames, legs still
    st, tl = film({"ann": [{"t": 0, "pos": [-1.5, 0], "yaw": 0}, {"t": 1.0, "pos": [-1.5, 0]},
                           {"t": 1.067, "pos": [-0.9, 0]}],
                   "bo": [{"t": 0, "pos": [1.5, 0], "yaw": 0}]})
    rows = staging.lint(st, tl)
    assert [(r["check"], r["who"], r["shot"]) for r in rows] == [("lurch", "ann", "S01")]
    assert abs(rows[0]["t"] - 1.0) < 0.1


def test_two_keys_at_one_time_jump():
    st, tl = film({"ann": [{"t": 0, "pos": [-1.5, 0]}, {"t": 1.5, "pos": [-1.5, 0]}, {"t": 1.5, "pos": [-0.5, 0]}]})
    assert found(st, tl) == {("lurch", "ann")}


def test_walk_is_not_a_lurch():
    # 2 m in 1.2 s: a brisk walk with its legs swinging
    st, tl = film({"ann": [{"t": 0, "pos": [-1.5, 0]}, {"t": 0.8, "pos": [-1.5, 0]}, {"t": 2.0, "pos": [0.5, 0]}]})
    assert found(st, tl) == set()


def test_too_close():
    # side by side, 0.85 m apart: their arms (1.35 m arm to arm) pass through each other
    st, tl = film({"ann": [{"t": 0, "pos": [-0.425, 0], "yaw": 0}], "bo": [{"t": 0, "pos": [0.425, 0], "yaw": 0}]})
    rows = staging.lint(st, tl)
    assert [(r["check"], r["who"]) for r in rows] == [("close", "ann+bo")]
    assert rows[0]["detail"].startswith("0.85 m apart") and "side by side" in rows[0]["detail"]


def test_clean_pair():
    # 1.6 m apart side by side, and 0.8 m face to face (a body is 0.34 m deep): nobody touches
    st, tl = film({"ann": [{"t": 0, "pos": [-0.8, 0], "yaw": 0}], "bo": [{"t": 0, "pos": [0.8, 0], "yaw": 0}]})
    assert found(st, tl) == set()
    st, tl = film({"ann": [{"t": 0, "pos": [-0.4, 0], "yaw": 90}], "bo": [{"t": 0, "pos": [0.4, 0], "yaw": -90}]})
    assert found(st, tl) == set()


def test_staging_ok():
    acting = {"ann": [{"t": 0, "pos": [-0.3, 0], "yaw": 0}], "bo": [{"t": 0, "pos": [0.3, 0], "yaw": 0}]}
    for ok in (["S01/hug"], ["S01"], ["S01/ann+bo"]):
        st, tl = film(acting, extra={"staging_ok": ok})
        assert found(st, tl) == set(), ok
    st, tl = film(acting, extra={"staging_ok": ["S02/hug"]})
    assert found(st, tl) == {("close", "ann+bo")}


def test_off_camera_pair_and_cut():
    # the same too-close pair behind the camera is not reported
    st, tl = film({"ann": [{"t": 0, "pos": [-0.3, -9]}], "bo": [{"t": 0, "pos": [0.3, -9]}]})
    assert found(st, tl) == set()
    # Ann jumps 3 m exactly on a cut to a different camera: the cut hides it
    shots = [{"id": "S01", "start": 0.0, "end": 1.5, "f0": 0, "f1": 45, "step": 1},
             {"id": "S02", "start": 1.5, "end": 3.0, "f0": 45, "f1": 90, "step": 1,
              "cam": [[0, [6, -3, 1.5], [1.5, 0, 1.0], 30]]}]
    st, tl = film({"ann": [{"t": 0, "pos": [-1.5, 0]}, {"t": 1.5, "pos": [-1.5, 0]}, {"t": 1.5, "pos": [1.5, 0]}]},
                  shots=shots)
    assert found(st, tl) == set()
    # ...but not when the camera stays put: a jump cut
    shots[1]["cam"] = CAM
    st, tl = film({"ann": [{"t": 0, "pos": [-1.5, 0]}, {"t": 1.5, "pos": [-1.5, 0]}, {"t": 1.5, "pos": [1.5, 0]}]},
                  shots=shots)
    assert found(st, tl) == {("lurch", "ann")}
