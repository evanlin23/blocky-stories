"""Offline tests for scripts/framing.py: small synthetic timelines, no Blender, no set.py.

One character, Gus, stands at the origin facing -y (towards a camera at y < 0). Each test moves the camera:
a cut head, the back of his head, an empty frame and a clean shot."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import framing  # noqa: E402

GUS = {"skin": "#f1c9a0", "shirt": "#3d6ea6", "pants": "#2c3550"}
HEAD = framing.HEAD_Z   # Gus's head centre, 1.57 m up


def story(cam, line="Gus waits at the DOOR.", who="narrator", extra=None, cast=None):
    st = {"name": "tiny", "cast": cast or {"gus": GUS},
          "lines": [{"id": "L01", "who": who, "chunks": [[line, line]]}],
          "shots": [{"id": "S01", "cam": [[0, *cam]]}],
          "acting": {"gus": [{"at": 0, "pos": [0, 0], "yaw": 0}]}}
    st.update(extra or {})
    return st


def timeline(st):
    """What blocky.timeline.build makes of it, by hand: one 2 s line under one 2.5 s shot."""
    return {"name": "tiny", "fps": 30, "duration": 2.5, "frames": 75, "fade_in": False, "fade_out": False,
            "lines": {"L01": {"id": "L01", "who": st["lines"][0]["who"], "text": st["lines"][0]["chunks"][0][1],
                              "onset": 0.25, "end": 2.25, "chunks": [[0.25, 2.25, st["lines"][0]["chunks"][0][0]]]}},
            "order": ["L01"], "captions": [], "talk": {"gus": []},
            "shots": [{"id": "S01", "start": 0.0, "end": 2.5, "f0": 0, "f1": 75, "step": 2}],
            "cues": [], "fx": [], "acting": {"gus": [{"at": 0, "t": 0.0, "pos": [0, 0], "yaw": 0}]}, "motion": {}}


def run(st):
    rows, _ = framing.lint(st, timeline(st), None, use_set=False)
    return rows


def checks(rows):
    return {(r["check"], r["who"]) for r in rows}


def test_clean_shot():
    # a medium close-up from the front: the face centred and well over 1/5 of the width
    st = story([[0, -2.2, HEAD], [0, 0, HEAD], 50])
    assert run(st) == []


def test_cut_head():
    # the camera aims at his chest from close up: the top of the head is past the top of the frame
    st = story([[0, -1.6, 0.9], [0, 0, 1.15], 50])
    rows = run(st)
    assert ("cut", "gus") in checks(rows)
    assert any("top" in r["detail"] for r in rows if r["check"] == "cut")


def test_back_of_head():
    # the same framing from behind him, on a line that names him
    st = story([[0, 2.2, HEAD], [0, 0, HEAD], 50])
    rows = run(st)
    assert ("back", "gus") in checks(rows)


def test_profile_counts_as_no_face():
    # side on (90 degrees): a blocky face is drawn on the front, so none of it shows
    st = story([[2.2, 0, HEAD], [0, 0, HEAD], 50])
    assert ("side", "gus") in checks(run(st))


def test_empty_frame():
    # a line about nobody in the cast, the camera turned to an empty wall
    st = story([[0, -2.2, HEAD], [6, -2.2, HEAD], 50], line="Nobody answers the PHONE.")
    rows = run(st)
    assert ("empty", "-") in checks(rows)


def test_named_prop_fills_the_frame():
    # the same empty-looking shot, but the line's prop is there
    st = story([[0, -2.2, HEAD], [6, -2.2, HEAD], 50], line="Nobody answers the PHONE.",
               extra={"framing_props": {"phone": [6, -1.5, HEAD]}})
    assert run(st) == []


def test_missing_and_small():
    # the line names Gus; the camera looks away (missing), then from far off (small)
    away = story([[0, -2.2, HEAD], [6, -2.2, HEAD], 50])
    assert ("missing", "gus") in checks(run(away))
    far = story([[0, -14, HEAD], [0, 0, HEAD], 50])
    assert ("small", "gus") in checks(run(far))


def test_speaker_counts_and_narrator_line_about_nobody_is_fine():
    st = story([[0, 2.2, HEAD], [0, 0, HEAD], 50], line="I'm right HERE.", who="gus")
    assert ("back", "gus") in checks(run(st))
    st = story([[0, 2.2, HEAD], [0, 0, HEAD], 50], line="It was late.")
    assert run(st) == []


def test_framing_ok_skips_the_shot():
    st = story([[0, 2.2, HEAD], [0, 0, HEAD], 50], extra={"framing_ok": ["S01"]})
    assert run(st) == []


def test_pronoun_carries_the_last_name():
    st = {"cast": {"dad": GUS, "me": GUS}}
    tl = {"order": ["L1", "L2", "L3"], "lines": {
        "L1": {"who": "narrator", "text": "Dad came home."},
        "L2": {"who": "narrator", "text": "He said nothing."},
        "L3": {"who": "me", "text": "I went to bed."}}}
    ab = framing.about(st, tl)
    assert ab == {"L1": [{"dad"}], "L2": [{"dad"}], "L3": [{"me"}]}


def test_stems_and_tokens():
    assert framing.stem("shelves") == "shelf"
    assert framing.stem("boxes") == "box"
    assert framing.tokens("shelf3.box_lid") == {"shelf", "box", "lid"}


# ---------- the 2026-11-05 recalibration (ep109, ep112, ep115, ep116) ----------

def test_slight_cut_at_the_left_edge():
    # from 4 m the frame is about 1.1 m wide; aimed 0.38 m right of him, his head (and hair) pokes 4%+ past the
    # left edge: what ep115's critic dropped five times, and the old 25% bar passed
    st = story([[0, -4.0, HEAD], [0.38, 0, HEAD], 50])
    rows = run(st)
    assert any(r["check"] == "cut" and "left" in r["detail"] for r in rows)
    centred = story([[0, -4.0, HEAD], [0, 0, HEAD], 50])
    assert not any(r["check"] == "cut" for r in run(centred))


def test_caption_over_the_mouth():
    # the head sits low in the frame, so the caption band (62 to 69% of the height) lands on his mouth
    st = story([[0, -2.2, HEAD + 0.08], [0, 0, HEAD + 0.08], 50])
    tl = timeline(st)
    tl["captions"] = [{"line": "L01", "who": "narrator", "text": "Gus waits at the DOOR.", "start": 0.25,
                       "end": 2.25, "big": False}]
    rows, _ = framing.lint(st, tl, None, use_set=False)
    assert ("caption", "gus") in checks(rows)
    tl["captions"][0].update(start=5.0, end=6.0)   # no caption up: nothing to cover
    rows, _ = framing.lint(st, tl, None, use_set=False)
    assert ("caption", "gus") not in checks(rows)


def test_hand_over_the_face():
    st = story([[0, -2.6, HEAD], [0, 0, HEAD], 50])
    tl = timeline(st)
    tl["acting"]["gus"] = [{"at": 0, "t": 0.0, "pos": [0, 0], "yaw": 0, "arms": [0, 160], "side": [0, -35]}]
    rows, _ = framing.lint(st, tl, None, use_set=False)
    assert ("hand", "gus") in checks(rows)
    assert run(st) == []   # arms down: no hand near the face


def test_tag_over_an_eye():
    # 13% of the face under the tag, but over one eye (ep116 S17): covered
    v = {"x": 0.0, "y": 0.0, "hw": 0.4, "hh": 0.22, "width": 0.4, "ang": 10.0}
    eye = framing.eye_boxes(v)[0]
    tag = (eye[0] - 0.05, eye[1] - 0.02, eye[2] + 0.02, 1.0)
    assert framing.overlap(tag, framing.face_box(v)) < framing.TAG_OVER * framing.area(framing.face_box(v))
    assert framing.under_tag(v, tag)
    assert not framing.under_tag(v, (0.5, 0.5, 0.9, 0.9))   # the tag clear of the face


def test_the_narrator_in_profile_on_an_i_line():
    # ep109 S52: me side on, on the narrator's "I finally said sorry": a self line, so the face has to show
    me = {"me": GUS}
    side = story([[2.2, 0, HEAD], [0, 0, HEAD], 50], line="I finally said SORRY.", cast=me,
                 extra={"acting": {"me": [{"at": 0, "pos": [0, 0], "yaw": 0}]}})
    tl = timeline(side)
    tl["acting"] = {"me": tl["acting"]["gus"]}
    tl["talk"] = {"me": []}
    rows, _ = framing.lint(side, tl, None, use_set=False)
    assert ("side", "me") in checks(rows)
    front = story([[0, -2.2, HEAD], [0, 0, HEAD], 50], line="I finally said SORRY.", cast=me)
    tl = timeline(front)
    tl["acting"] = {"me": tl["acting"]["gus"]}
    rows, _ = framing.lint(front, tl, None, use_set=False)
    assert rows == []


def test_back_of_the_only_head_on_a_he():
    # ep112 S26: "He said nobody ever looks at the guy", over the back of the man it's about, no name to reach him
    st = story([[0, 2.2, HEAD], [0, 0, HEAD], 50], line="He said NOTHING.")
    assert ("back", "gus") in checks(run(st))


def test_a_he_skips_a_woman():
    st = {"cast": {"mom": GUS, "dad": GUS}}
    tl = {"order": ["L1", "L2", "L3"], "lines": {
        "L1": {"who": "narrator", "text": "Dad came home."},
        "L2": {"who": "narrator", "text": "Mom came home."},
        "L3": {"who": "narrator", "text": "He said nothing."}}}
    assert framing.about(st, tl)["L3"] == [{"dad"}]
