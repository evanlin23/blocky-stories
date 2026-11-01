"""Render one blocky story in Blender (bpy venv, never the repo's Python):

    <bpy python> blocky/bl_story.py job.json

job.json: {"story_dir": ..., "timeline": ..., "out": <dir>, "res": [w, h], "samples": n, "threads": n,
           "frames": [frame numbers] or null, "stills": [seconds] or null, "skip_existing": true}

The world is the story's own `set.py`: `build(kit, story, tl)` makes the set and its lights and returns
anything the story wants to keep, and an optional `animate(kit, story, tl, t, ctx)` moves story things (a door,
a monster, a light switching off) and may return {light name: gain}. The cast comes from the spec and is posed
from `acting.py`. The camera follows each shot's keys in the spec:

    "cam": [[u, [x, y, z], [tx, ty, tz], lens_mm, roll_deg?], ...]   u from 0 to 1 over the shot
    "follow": "<cast name>"   camera and target positions are relative to that character's feet
    "hand": 0.02              handheld drift in metres
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from blocky import acting, kit, rig  # noqa: E402


def load_set(story_dir: Path):
    spec = importlib.util.spec_from_file_location("story_set", story_dir / "set.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def cam_at(shot_spec, shot, t, chars, tl):
    keys = shot_spec["cam"]
    u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
    if u <= keys[0][0] or len(keys) == 1:
        k = keys[0]
        loc, tgt, lens, roll = k[1], k[2], k[3], (k[4] if len(k) > 4 else 0)
    else:
        loc = tgt = lens = roll = None
        for a, b in zip(keys, keys[1:]):
            if u <= b[0]:
                v = _ease((u - a[0]) / max(1e-6, b[0] - a[0]))
                loc = kit.lerp(tuple(a[1]), tuple(b[1]), v)
                tgt = kit.lerp(tuple(a[2]), tuple(b[2]), v)
                lens = a[3] + (b[3] - a[3]) * v
                roll = (a[4] if len(a) > 4 else 0) + ((b[4] if len(b) > 4 else 0) - (a[4] if len(a) > 4 else 0)) * v
                break
        if loc is None:
            k = keys[-1]
            loc, tgt, lens, roll = k[1], k[2], k[3], (k[4] if len(k) > 4 else 0)
    who = shot_spec.get("follow")
    if who:
        s = acting.state(tl, who, t)
        loc = (loc[0] + s["x"], loc[1] + s["y"], loc[2] + s["z"])
        tgt = (tgt[0] + s["x"], tgt[1] + s["y"], tgt[2] + s["z"])
    h = shot_spec.get("hand", 0.012)
    if h:
        seed = sum(map(ord, shot["id"]))
        loc = (loc[0] + h * kit.noise1(t, seed, 0.9), loc[1] + h * kit.noise1(t, seed + 3, 0.7),
               loc[2] + h * kit.noise1(t, seed + 7, 1.1))
        tgt = (tgt[0] + h * 0.6 * kit.noise1(t, seed + 9, 0.6), tgt[1], tgt[2] + h * 0.6 * kit.noise1(t, seed + 5, 0.8))
    return loc, tgt, lens, math.radians(roll)


def main():
    job = json.loads(Path(sys.argv[1]).read_text())
    sdir = Path(job["story_dir"])
    story = json.loads((sdir / "story.json").read_text())
    tl = json.loads(Path(job["timeline"]).read_text())
    out = Path(job["out"])
    out.mkdir(parents=True, exist_ok=True)
    faces_dir = out.parent / "faces"
    faces_dir.mkdir(parents=True, exist_ok=True)

    kit.reset()
    # the fog and sky: "look" (the story's "world" is its one-line description); an older spec kept them in "world"
    look = story.get("look") or (story["world"] if isinstance(story.get("world"), dict) else {})
    kit.set_fog(look.get("fog", "#141820"), look.get("fog_density", 0.05), look.get("fog_start", 2.0))
    kit.world(look.get("sky", look.get("fog", "#141820")), look.get("sky_strength", 1.0))
    kit.setup_render(job["res"], job.get("samples", 8), job.get("threads", 2), look.get("exposure", 0.0))
    setmod = load_set(sdir)
    ctx = setmod.build(kit, story, tl) or {}
    chars = {}
    for i, (name, spec) in enumerate(story.get("cast", {}).items()):
        if spec.get("offscreen"):
            continue
        chars[name] = (rig.Character(name, spec, faces_dir), i)
    shots = {s["id"]: s for s in story["shots"]}

    if job.get("stills"):
        frames = [int(round(t * tl["fps"])) for t in job["stills"]]
    else:
        frames = job.get("frames") or list(range(tl["frames"]))
    t_start = time.time()
    for n, f in enumerate(frames):
        path = out / f"f{f:05d}.png"
        if job.get("skip_existing") and path.exists():
            continue
        t = f / tl["fps"]
        shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
        for name, (c, seed) in chars.items():
            s = acting.state(tl, name, t, seed)
            c.pose(s["x"], s["y"], s["z"], s["yaw"], s["legs"], s["arms"], s["arms_side"], s["head_yaw"],
                   s["head_pitch"], s["lean"], s["bob"], s["expr"], s["mouth"], s["look"], s["blink"], s["hidden"])
        overrides = {}
        if hasattr(setmod, "animate"):
            overrides = setmod.animate(kit, story, tl, t, ctx) or {}
        kit.update_lights(t, overrides)
        loc, tgt, lens, roll = cam_at(shots[shot["id"]], shot, t, chars, tl)
        kit.place_camera(loc, tgt, lens, roll)
        t0 = time.time()
        kit.render_to(path)
        print(f"frame {f} ({shot['id']}) {time.time() - t0:.1f}s  [{n + 1}/{len(frames)}]", flush=True)
    print(f"done {len(frames)} frames in {(time.time() - t_start) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
