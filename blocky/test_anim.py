"""The animation audit's motion options (2026-11-12): overlap and the turn cap. Pure Python, no Blender."""

import math

from blocky import acting, polish

FPS = 30


def tl_with(keys, **motion):
    return {"acting": {"me": keys}, "talk": {}, "motion": {"ease": True, **motion}}


def yaw_rates(tl, t0, t1, attr="yaw"):
    out, prev = [], None
    for f in range(int(t0 * FPS), int(t1 * FPS)):
        v = acting.state(tl, "me", f / FPS)[attr]
        if prev is not None:
            out.append(math.degrees(abs(acting._wrap(v - prev))) * FPS)
        prev = v
    return out


TURN = [{"t": 0.0, "pos": [0, 0], "yaw": 0, "head": [0, 0], "arms": [0, 0]},
        {"t": 1.0, "pos": [0, 0], "yaw": 180, "head": [40, 0], "arms": [60, 0]}]


def test_off_is_unchanged():
    # with neither option, a key's blend is exactly what it was (a 180 degree turn over the default 0.25 s)
    tl = tl_with(TURN)
    assert max(yaw_rates(tl, 0.5, 1.5)) > 900
    assert acting.state(tl, "me", 0.75)["yaw"] == 0.0
    assert polish.DEFAULTS["overlap"] is False and polish.DEFAULTS["turn_cap"] == 0


def test_turn_cap_holds_turns_to_the_cap():
    keys = [dict(TURN[0]), {**TURN[1], "t": 2.0}]   # room for a 180 at 220 deg/s (1.23 s); closer keys keep their timing
    tl = tl_with(keys, turn_cap=220)
    assert max(yaw_rates(tl, 0.0, 2.5)) <= 220 * 1.02
    assert math.isclose(math.degrees(acting.state(tl, "me", 2.0)["yaw"]), 180, abs_tol=0.01)   # lands on its key
    assert max(yaw_rates(tl, 0.0, 2.5, "head_yaw")) <= 220 * 1.02


def test_turn_cap_takes_the_short_way():
    keys = [{"t": 0.0, "pos": [0, 0], "yaw": 180}, {"t": 2.0, "pos": [0, 0], "yaw": -90}]
    tl = tl_with(keys, turn_cap=220)
    mid = math.degrees(acting.state(tl, "me", 1.85)["yaw"])
    assert 180 <= mid <= 270   # through 225, not back through 45
    assert sum(yaw_rates(tl, 0.0, 2.5)) / FPS < 100


def test_turn_cap_never_moves_a_cut():
    # a blend 0 key (a re-staging on a cut) still lands on its own frame
    keys = [{"t": 0.0, "pos": [0, 0], "yaw": 0}, {"t": 1.0, "pos": [0, 0], "yaw": 180, "blend": 0.0}]
    for tl in (tl_with(keys, turn_cap=220, overlap=True), tl_with(keys)):
        assert acting.state(tl, "me", 0.99)["yaw"] == 0.0
        assert math.isclose(math.degrees(acting.state(tl, "me", 1.0)["yaw"]), 180)


def test_turn_cap_eases_a_walk_into_its_direction():
    # facing the camera, then walking off sideways: uncapped, the body snaps 90 degrees on the walk's first frame
    keys = [{"t": 0.0, "pos": [0, 0], "yaw": 0}, {"t": 1.0, "pos": [0, 0]}, {"t": 3.0, "pos": [3, 0]}]
    assert max(yaw_rates(tl_with(keys), 0.5, 2.0)) > 2000
    assert max(yaw_rates(tl_with(keys, turn_cap=220), 0.5, 3.5)) <= 220 * 1.05


def test_overlap_head_leads_and_arms_follow():
    tl = tl_with(TURN, overlap=True)
    plain = tl_with(TURN)
    t = 1.0 - acting.BLEND / 2   # halfway through the plain blend
    s, p = acting.state(tl, "me", t), acting.state(plain, "me", t)
    assert s["head_yaw"] > p["head_yaw"] + 1e-3          # the head is ahead
    assert s["arms"][0] < p["arms"][0] - 1e-3            # the arms are behind
    assert math.isclose(s["yaw"], p["yaw"])              # the body is on its key
    late = acting.state(tl, "me", 1.0 + 0.2)             # and everything lands
    assert math.isclose(late["head_yaw"], math.radians(40)) and math.isclose(late["arms"][0], math.radians(60))


def test_timeline_passes_the_options():
    from blocky import timeline
    st = {"look": {"polish": {"overlap": True, "turn_cap": 220}}}
    m = timeline._motion(st)
    assert m["overlap"] is True and m["turn_cap"] == 220.0
    assert timeline._motion({"look": {"polish": True}})["overlap"] is False
