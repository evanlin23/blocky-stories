import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_story_slots():
    story = sorted(p.name for p in (ROOT / "stories").iterdir() if (p / "script.md").exists() or p.is_dir())[0]
    out = subprocess.run([sys.executable, "scripts/plan_renders.py", "--story", story, "--shards", "16"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    kv = dict(l.split("=", 1) for l in out.splitlines() if "=" in l)
    assert kv["a"] == story and kv["b"] == ""
    assert json.loads(kv["shards"]) == list(range(16))
    assert json.loads(kv["stories"]) == [story] and kv["any"] == "true" and kv["more"] == "false"
    assert len(json.loads(kv["matrix"])["include"]) == 16
