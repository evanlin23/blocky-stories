"""look.render_res (animation audit 2026-11-12): the final drawn at 720 x 1280 when a story opts in. No Blender."""

import pytest

from blocky import __main__ as cli
from blocky import post


def test_final_res_is_opt_in():
    q = cli.QUALITY["final"]
    assert cli.final_res(q, "final", {"look": {}}) is q
    assert cli.final_res(q, "final", {"look": {"render_res": "720"}})["res"] == [720, 1280]
    assert cli.final_res(q, "final", {"look": {"render_res": 1080}})["res"] == [1080, 1920]
    assert q["res"] == [540, 960]                                   # the preset itself is untouched


def test_final_res_never_changes_the_proof_or_flash():
    st = {"look": {"render_res": "720"}}
    for qn in ("proof", "preview", "flash"):
        assert cli.final_res(cli.QUALITY[qn], qn, st) is cli.QUALITY[qn]


def test_final_res_rejects_a_bad_size():
    with pytest.raises(SystemExit):
        cli.final_res(cli.QUALITY["final"], "final", {"look": {"render_res": "900"}})


def test_post_takes_a_720_drawing():
    import numpy as np
    out = post.to_output(np.zeros((1280, 720, 3), np.float32), 1.1, 0.01, 0.0)
    assert out.shape == (1920, 1080, 3)
