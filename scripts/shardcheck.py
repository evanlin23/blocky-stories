"""A shard start must see the same scene as a continuous run (lesson 44). Report-only.

    python scripts/shardcheck.py --story stories/<story> [--shards 32] [--workers 2] [--jobs 4]

The final is drawn in 32 shards (render.yml), and each shard runs `python -m blocky render <story> --shard k/32`,
which keeps frames[k::32] of the final's frame list and splits those again over BLOCKY_WORKERS (2) Blender
processes, frames[k::32][w::2] (blocky/__main__.py `cmd_render` and `blender`). Every one of those processes is
fresh: it builds the set and calls the set's `animate` first at its own start frame. A set.py that keeps state
between `animate` calls (the lazy `_first_frame()` guarded by `W["inited"]`) can then see a different scene at a
shard start than a one-process run does: ep117's S02 extras were made after the owners were hidden and stayed
visible, on the final only (2026-11-06).

For every process start frame, this compares the scene two ways, without drawing anything:
  (a) fresh: a new bpy process runs blocky/bl_story.py's own `main()` on a job of just that frame;
  (b) continuous: one bpy process runs `main()` over the final's frame list from its first frame on.
`kit.render_to` is swapped for a snapshot of every object: hide_render, world location (to 1 mm), world scale,
its materials' emission strength and its light's energy. An object hidden in both is not compared further.
Exit 1 if anything differs at any start, 0 if nothing does, 2 if Blender failed.

Needs BLOCKY_BPY (bash blocky/setup.sh). Working files go to out/shardcheck/<story>/.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOC_TOL, SCALE_TOL, REL_TOL = 1e-3, 1e-3, 1e-3


# ------------------------------------------------------------------------------------------------ plain Python

def process_starts(frames: list[int], shards: int = 32, workers: int = 2) -> list[tuple[int, str]]:
    """(start frame, label) of every Blender process the final's shards start: the engine's own split,
    frames[k::shards] for shard k, then [w::workers] for each of its processes (one process if 1 frame)."""
    out = []
    for k in range(shards):
        sub = frames[k::shards]
        n = workers if len(sub) > 1 else 1
        for w in range(n):
            part = sub[w::n] if n > 1 else sub
            if part:
                out.append((part[0], f"shard {k}/{shards} worker {w}"))
    return out


def shot_at(tl: dict, f: int) -> str:
    return next((s["id"] for s in tl["shots"] if s["f0"] <= f < s["f1"]), tl["shots"][-1]["id"])


def _close(a, b, tol, rel=False):
    if a is None or b is None:
        return a is b
    t = tol * max(1.0, abs(a), abs(b)) if rel else tol
    return abs(a - b) <= t


def compare(fresh: dict, cont: dict) -> list[str]:
    """What differs between two snapshots ({object: state}), one line per object."""
    out = []
    for name in sorted(set(fresh) | set(cont)):
        a, b = fresh.get(name), cont.get(name)
        if a is None or b is None:
            here = b if a is None else a
            if here.get("hide"):
                continue   # exists in one run only, but hidden there: nothing shows
            out.append(f"{name}: only in the {'continuous' if a is None else 'fresh'} run (visible)")
            continue
        d = []
        if bool(a["hide"]) != bool(b["hide"]):
            d.append(f"hide_render {a['hide']} (shard start) vs {b['hide']} (continuous)")
        elif a["hide"]:
            continue   # hidden in both: nothing shows
        else:
            dl = max(abs(x - y) for x, y in zip(a["loc"], b["loc"]))
            if dl > LOC_TOL:
                d.append(f"location off by {dl * 1000:.0f} mm")
            ds = max(abs(x - y) for x, y in zip(a["scale"], b["scale"]))
            if ds > SCALE_TOL:
                d.append(f"scale {fmt(a['scale'])} vs {fmt(b['scale'])}")
            if len(a.get("emit", [])) != len(b.get("emit", [])) or not all(
                    _close(x, y, REL_TOL, True) for x, y in zip(a.get("emit", []), b.get("emit", []))):
                d.append(f"emission {fmt(a.get('emit'))} vs {fmt(b.get('emit'))}")
            if not _close(a.get("energy"), b.get("energy"), REL_TOL, True):
                d.append(f"light energy {a.get('energy')} vs {b.get('energy')}")
        if d:
            out.append(f"{name}: " + "; ".join(d))
    return out


def fmt(v):
    return "[" + ", ".join(f"{x:.3g}" for x in v) + "]" if isinstance(v, (list, tuple)) else str(v)


def check(tl: dict, starts: list[tuple[int, str]], fresh_at, continuous_at) -> list[dict]:
    """fresh_at(f) -> snapshot of a new process posed first at f; continuous_at(frames) -> {f: snapshot} from one
    process posed over the frame list up to each f. Returns one dict per (start, object) that differs."""
    cont = continuous_at(sorted({f for f, _ in starts}))
    found = []
    for f, label in starts:
        for line in compare(fresh_at(f), cont[f]):
            found.append({"frame": f, "shot": shot_at(tl, f), "start": label, "object": line.split(":")[0],
                          "detail": line})
    return found


def ranges(fs: list[int]) -> str:
    fs, out = sorted(set(fs)), []
    for f in fs:
        if out and f == out[-1][1] + 1:
            out[-1][1] = f
        else:
            out.append([f, f])
    return ", ".join(f"{a}" if a == b else f"{a}-{b}" for a, b in out)


def summarize(found: list[dict]) -> list[str]:
    """One line per object: the start frames and shots it differs at, and the first difference seen."""
    by = {}
    for x in found:
        by.setdefault(x["object"], []).append(x)
    return [f"{o}: frames {ranges([x['frame'] for x in xs])} "
            f"({', '.join(sorted({x['shot'] for x in xs}))}): {xs[0]['detail'].split(': ', 1)[1]}"
            for o, xs in sorted(by.items(), key=lambda kv: (kv[1][0]["frame"], kv[0]))]


# ------------------------------------------------------------------------------------------------ bpy side

def _snapshot() -> dict:
    import bpy

    bpy.context.view_layer.update()

    def emit(mat):
        vals = []
        if mat and mat.use_nodes and mat.node_tree:
            for n in mat.node_tree.nodes:
                for key in ("Emission Strength", "Strength") if n.type in ("BSDF_PRINCIPLED", "EMISSION") else ():
                    i = n.inputs.get(key)
                    if i is not None and not i.is_linked:
                        vals.append(float(i.default_value))
        return vals

    snap = {}
    for ob in bpy.data.objects:
        m = ob.matrix_world
        st = {"hide": bool(ob.hide_render), "loc": list(m.translation), "scale": list(m.to_scale()),
              "emit": [v for s in ob.material_slots for v in emit(s.material)]}
        if ob.type == "LIGHT":
            st["energy"] = float(ob.data.energy)
        snap[ob.name] = st
    return snap


def worker(job_path: str, snap_path: str, at: str) -> None:
    """Inside bpy: run the engine's own render loop on the job, snapshotting instead of drawing at frames `at`."""
    sys.path.insert(0, str(ROOT))
    from blocky import bl_story, kit

    want, snaps = {int(x) for x in at.split(",")}, {}

    def render_to(path):
        f = int(Path(path).stem[1:])
        if f in want:
            snaps[f] = _snapshot()

    kit.render_to = render_to
    sys.argv = ["bl_story.py", job_path]
    bl_story.main()
    Path(snap_path).write_text(json.dumps(snaps))


# ------------------------------------------------------------------------------------------------ driver

def run_story(story_dir: Path, shards: int, workers: int, jobs: int) -> tuple[list[dict], int, dict]:
    sys.path.insert(0, str(ROOT))
    from blocky import timeline

    name = story_dir.name
    bpy = os.environ.get("BLOCKY_BPY") or os.environ.get("CLAY_BPY")
    if not bpy or not Path(bpy).exists():
        sys.exit("set BLOCKY_BPY to the Python of a venv with Blender's bpy module (bash blocky/setup.sh)")
    w = ROOT / "out" / "shardcheck" / name
    (w / "frames").mkdir(parents=True, exist_ok=True)
    tlp = w / "timeline.json"
    if (story_dir / "timeline.json").exists() and not (story_dir / "voice-timings.json").exists():
        tlp.write_text((story_dir / "timeline.json").read_text())   # a test story ships its own timeline
    else:
        timeline.write(name, story_dir / "voice-timings.json", tlp)
    tl = json.loads(tlp.read_text())
    frames = timeline.frame_list(tl)   # the final's own frame list (each shot on its step)
    starts = process_starts(frames, shards, workers)
    base = {"story": name, "story_dir": str(story_dir), "timeline": str(tlp), "out": str(w / "frames"),
            "res": [54, 96], "samples": 1, "threads": 1, "skip_existing": False}

    def run(tag, fr, at):
        jp, sp = w / f"job-{tag}.json", w / f"snap-{tag}.json"
        jp.write_text(json.dumps({**base, "frames": fr}))
        with open(w / f"log-{tag}.txt", "w") as log:
            r = subprocess.run([bpy, str(Path(__file__).resolve()), "--worker", str(jp), str(sp), ",".join(map(str, at))],
                               stdout=log, stderr=subprocess.STDOUT, env={**os.environ, "OMP_NUM_THREADS": "1"})
        if r.returncode != 0 or not sp.exists():
            tail = "".join((w / f"log-{tag}.txt").read_text(errors="replace").splitlines(keepends=True)[-30:])
            raise RuntimeError(f"Blender failed on {name} ({tag}):\n{tail}")
        return {int(k): v for k, v in json.loads(sp.read_text()).items()}

    uniq = sorted({f for f, _ in starts})
    with ThreadPoolExecutor(max(1, jobs)) as ex:
        cfut = ex.submit(lambda: run("continuous", [f for f in frames if f <= uniq[-1]], uniq))
        fresh = dict(zip(uniq, ex.map(lambda f: run(f"fresh-{f}", [f], [f])[f], uniq)))
        cont = cfut.result()
    found = check(tl, starts, fresh.__getitem__, lambda fs: cont)
    return found, len(starts), tl


def main(argv=None) -> int:
    if argv is None and len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(*sys.argv[2:5])
        return 0
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--story", required=True, help="stories/<name>")
    ap.add_argument("--shards", type=int, default=32, help="render.yml's SHARDS")
    ap.add_argument("--workers", type=int, default=int(os.environ.get("BLOCKY_WORKERS", 2)),
                    help="Blender processes per shard (the engine's BLOCKY_WORKERS)")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2, help="bpy processes at once")
    ap.add_argument("--json", help="also write the findings here")
    a = ap.parse_args(argv)
    sd = Path(a.story)
    sd = sd if sd.is_absolute() else ROOT / sd
    try:
        found, n, tl = run_story(sd, a.shards, a.workers, a.jobs)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 2
    for line in summarize(found):
        print(line)
    objs = sorted({x["object"] for x in found})
    print(f"shardcheck {sd.name}: {n} process starts checked ({a.shards} shards x {a.workers} workers), "
          f"{len(objs)} object(s) differ" + (f": {', '.join(objs)}" if objs else ""))
    if a.json:
        Path(a.json).write_text(json.dumps({"story": sd.name, "starts": n, "found": found}, indent=1))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
