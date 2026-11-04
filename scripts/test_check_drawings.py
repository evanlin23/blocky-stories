import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("check_drawings", Path(__file__).parent / "check_drawings.py")
cd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cd)


def tl():
    # S1 on ones (frames 0-3), S2 on twos (frames 4-9): 4 + 3 drawings for 10 frames
    return {"frames": 10, "shots": [{"id": "S1", "f0": 0, "f1": 4, "step": 1}, {"id": "S2", "f0": 4, "f1": 10, "step": 2}]}


def test_twos_shots_need_only_their_drawings(tmp_path):
    for f in (0, 1, 2, 3, 4, 6, 8):
        (tmp_path / f"f{f:05d}.png").write_bytes(b"")
    assert cd.missing(tl(), tmp_path) == []          # 7 PNGs for 10 frames is a complete film


def test_a_missing_drawing_is_caught(tmp_path):
    for f in (0, 1, 3, 4, 8):                        # 2 and 6 lost with their shard
        (tmp_path / f"f{f:05d}.png").write_bytes(b"")
    assert cd.missing(tl(), tmp_path) == [2, 6]
