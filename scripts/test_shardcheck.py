"""Tests for scripts/shardcheck.py (lesson 44): a tiny synthetic set.py with ep117's lazy-extras bug must be caught,
and the same set with its extra made in build() must pass.

The set hides its owner at t >= 1 s, but only when the hidden state changes, and makes an extra on its first
`animate` call. A process that starts after 1 s hides the owner first and makes the extra afterwards, visible:
ep117's floating moustache. The offline tests drive the set with a stand-in kit (no Blender, as on CI); the last
test runs the real engine in bpy and is skipped without BLOCKY_BPY."""

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import shardcheck  # noqa: E402

LAZY = '''
W = {}


def build(kit, story, tl):
    W["mat"] = kit.plastic("#888888")
    return {"parts": [kit.box("owner", (1, 1, 1), (0, 0, 0.5), W["mat"])]}


def animate(kit, story, tl, t, ctx):
    hidden = t >= 1.0
    if hidden != W.get("was_hidden"):   # visibility is only touched when it changes
        W["was_hidden"] = hidden
        for ob in ctx["parts"]:
            ob.hide_render = hidden
    if not W.get("inited"):   # the lazy first-frame extra: made on this process's first call
        W["inited"] = True
        ctx["parts"].append(kit.box("owner.extra", (0.2, 0.2, 0.2), (0, 0, 1.2), W["mat"]))
'''

GOOD = LAZY.replace('''    return {"parts": [kit.box("owner", (1, 1, 1), (0, 0, 0.5), W["mat"])]}''',
                    '''    return {"parts": [kit.box("owner", (1, 1, 1), (0, 0, 0.5), W["mat"]),
                      kit.box("owner.extra", (0.2, 0.2, 0.2), (0, 0, 1.2), W["mat"])]}''').replace(
    '''    if not W.get("inited"):''', '''    if False:''')

FPS = 2
SHOTS = [{"id": "S01", "start": 0.0, "end": 1.0, "f0": 0, "f1": 2, "step": 1},
         {"id": "S02", "start": 1.0, "end": 4.0, "f0": 2, "f1": 8, "step": 1}]
TL = {"fps": FPS, "frames": 8, "duration": 4.0, "shots": SHOTS}


class Ob:
    def __init__(self, name, loc):
        self.name, self.loc, self.hide_render = name, loc, False


class Kit:
    """Just what the synthetic set calls: boxes that can be hidden."""

    def __init__(self):
        self.objects = {}

    def plastic(self, hexc):
        return hexc

    def box(self, name, size, loc, mat=None):
        self.objects[name] = Ob(name, loc)
        return self.objects[name]

    def snap(self):
        return {n: {"hide": o.hide_render, "loc": list(o.loc), "scale": [1, 1, 1], "emit": []}
                for n, o in self.objects.items()}


def fresh_module(src, tmp_path):
    p = tmp_path / "set.py"
    p.write_text(src)
    spec = importlib.util.spec_from_file_location("story_set", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def producers(src, tmp_path, frames):
    def fresh_at(f):   # a new process: build, then animate first at f
        mod, kit = fresh_module(src, tmp_path), Kit()
        ctx = mod.build(kit, {}, TL)
        mod.animate(kit, {}, TL, f / FPS, ctx)
        return kit.snap()

    def continuous_at(want):   # one process over the frame list
        mod, kit, out = fresh_module(src, tmp_path), Kit(), {}
        ctx = mod.build(kit, {}, TL)
        for f in frames:
            if f > max(want):
                break
            mod.animate(kit, {}, TL, f / FPS, ctx)
            if f in want:
                out[f] = kit.snap()
        return out

    return fresh_at, continuous_at


def test_process_starts_follow_the_engine_split():
    frames = list(range(0, 400, 2))   # a shot on twos
    starts = shardcheck.process_starts(frames, 32, 2)
    assert len(starts) == 64
    # blocky render --shard k/32 keeps frames[k::32]; blender() gives worker w frames[k::32][w::2]
    assert sorted(f for f, _ in starts) == frames[:64]
    assert {l: f for f, l in starts}["shard 5/32 worker 1"] == frames[37]
    assert shardcheck.process_starts([0, 1], 32, 2) == [(0, "shard 0/32 worker 0"), (1, "shard 1/32 worker 0")]


def test_lazy_extras_are_caught(tmp_path):
    frames = list(range(8))
    starts = shardcheck.process_starts(frames, 4, 1)
    found = shardcheck.check(TL, starts, *producers(LAZY, tmp_path, frames))
    assert {(x["frame"], x["shot"], x["object"]) for x in found} == {(2, "S02", "owner.extra"), (3, "S02", "owner.extra")}
    assert "hide_render False (shard start) vs True (continuous)" in found[0]["detail"]
    assert shardcheck.summarize(found)[0].startswith("owner.extra: frames 2-3 (S02)")


def test_extras_made_in_build_pass(tmp_path):
    frames = list(range(8))
    starts = shardcheck.process_starts(frames, 4, 1)
    assert shardcheck.check(TL, starts, *producers(GOOD, tmp_path, frames)) == []


def test_compare_tolerances():
    a = {"o": {"hide": False, "loc": [0, 0, 0], "scale": [1, 1, 1], "emit": [2.0]},
         "L": {"hide": False, "loc": [0, 0, 0], "scale": [1, 1, 1], "emit": [], "energy": 100.0},
         "gone": {"hide": True, "loc": [0, 0, 0], "scale": [1, 1, 1], "emit": []}}
    near = json.loads(json.dumps(a))
    near["o"]["loc"] = [0.0009, 0, 0]
    near["L"]["energy"] = 100.05
    del near["gone"]   # hidden where it exists: nothing shows
    assert shardcheck.compare(a, near) == []
    far = json.loads(json.dumps(near))
    far["o"]["loc"], far["o"]["emit"], far["L"]["energy"] = [0.002, 0, 0], [0.0], 40.0
    out = shardcheck.compare(a, far)
    assert out[0].startswith("L: light energy") and "location off by 2 mm" in out[1] and "emission" in out[1]


def write_story(d: Path, src: str):
    d.mkdir()
    (d / "set.py").write_text(src)
    cam = [[0, [0, -6, 1.5], [0, 0, 0.8], 35]]
    (d / "story.json").write_text(json.dumps({"cast": {}, "shots": [{"id": s["id"], "cam": cam} for s in SHOTS]}))
    (d / "timeline.json").write_text(json.dumps({**TL, "lines": {}, "order": [], "captions": [], "cues": []}))


@pytest.mark.skipif(not os.environ.get("BLOCKY_BPY"), reason="needs Blender's bpy (bash blocky/setup.sh)")
@pytest.mark.parametrize("src,code", [(LAZY, 1), (GOOD, 0)])
def test_real_engine(tmp_path, src, code, capsys):
    write_story(tmp_path / "toy", src)
    assert shardcheck.main(["--story", str(tmp_path / "toy"), "--shards", "4", "--workers", "1", "--jobs", "2"]) == code
    out = capsys.readouterr().out
    assert ("owner.extra: frames 2-3 (S02)" in out) == (code == 1)
