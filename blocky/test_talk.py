"""Opt-in `polish.talk` (2026-11-12): narrated I/me/my lines move the narrator's mouth, and blinks keep natural
time. Pure Python, no Blender."""

import copy

from blocky import acting, polish, timeline
from blocky.test_polish import story


def test_first_person():
    assert timeline.first_person("I was ten.") and timeline.first_person("my MOM's phone")
    assert timeline.first_person("They took me") and timeline.first_person("i'm late")
    assert not timeline.first_person("You get one call.") and not timeline.first_person("Imagine the mines")


def _narrated(talk, text="My mom called me."):
    st, _ = story()
    for ln in st["lines"]:
        if "pause" not in ln:
            ln["chunks"] = [[text, text]]
    if talk is not None:
        st["look"] = {"polish": {"talk": talk}}
    vl = {ln["id"]: {"text": text, "onset": 0.05, "end": 1.6, "chunks": [[0.05, 1.6]]}
          for ln in st["lines"] if "pause" not in ln}
    return st, {"voice": "am_adam", "rate": 1.45, "tempo": 1.03, "model": "x", "lines": vl}


def test_talk_is_off_by_default():
    assert polish.DEFAULTS["talk"] is False
    st, v = _narrated(None)
    st["look"] = {"polish": True}
    assert timeline.build(st, v)["talk"]["me"] == []


def test_talk_flaps_the_narrators_first_person_lines():
    st, v = _narrated(True)
    tl = timeline.build(st, v)
    assert len(tl["talk"]["me"]) >= 5
    a, d = tl["talk"]["me"][0]
    assert acting.mouth(tl["talk"]["me"], a + d / 2) > 0.9
    st, v = _narrated(True, "You get one call.")   # not the narrator speaking as themself
    assert timeline.build(st, v)["talk"]["me"] == []


def test_natural_blinks_vary_and_respect_a_held_key():
    rate = 30
    tl = {"acting": {"me": [{"t": 0.0, "pos": [0, 0]}]}, "talk": {}, "motion": {"talk": True}}
    b = [acting.state(tl, "me", f / rate)["blink"] for f in range(60 * rate)]
    starts = [f / rate for f in range(1, len(b)) if b[f] and not b[f - 1]]
    gaps = [y - x for x, y in zip(starts, starts[1:])]
    long = [g for g in gaps if g > 1.0]
    assert 12 <= len(starts) <= 35
    assert min(long) >= 1.9 and max(long) <= 5.2 and max(long) - min(long) > 1.0   # not a clock
    assert all(1 <= n <= 3 for n in _runs(b))                                       # 1 to 3 frames shut
    held = copy.deepcopy(tl)
    held["acting"]["me"][0]["blink"] = False
    assert not any(acting.state(held, "me", f / rate)["blink"] for f in range(60 * rate))
    off = {**tl, "motion": {}}
    assert [acting.state(off, "me", f / rate)["blink"] for f in range(300)] == \
           [acting.blink(f / rate, 0) for f in range(300)]                          # off: the old blink


def _runs(b):
    out, n = [], 0
    for x in b + [0.0]:
        if x:
            n += 1
        elif n:
            out.append(n)
            n = 0
    return out
