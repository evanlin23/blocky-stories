"""Contact probe for ep14 "Lookout": BVH overlaps and closest distances between the cast, the giant, the lamp and
the set (the tower with its stairs, cab, catwalk and rail, the gate at the stairs' foot, the trees), at every drawn frame,
posed exactly as bl_story poses them (acting.state, then the set's animate).

Run in the bpy venv, from anywhere (paths are relative to this file):
    $BLOCKY_BPY stories/lookout/generator/probe.py            # every drawn frame of the final
    $BLOCKY_BPY stories/lookout/generator/probe.py --shots S47,S48 --out /tmp/probe.json

It needs the timeline (python -m blocky timeline lookout). The report lists, for each pair, the frames
whose meshes intersect (grouped by shot) and the closest distance seen, with its frame. My meshes are lifted 2 cm
for the tests against the set, so standing on the deck isn't counted as touching it. Allowed contact (the brief):
the giant's feet on the ground, the trees it walks past, and one stone shoulder on the tower's frame at L38 to L41.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORY = HERE.parent
ROOT = STORY.parents[1]
sys.path.insert(0, str(ROOT))

import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

from blocky import acting, bl_story, kit, rig, timeline  # noqa: E402


def local_mesh(ob, dg):
    """An object's evaluated mesh in its own space (modifiers applied), as (verts n x 3, polys)."""
    me = ob.evaluated_get(dg).to_mesh()
    v = np.array([x.co[:] for x in me.vertices], np.float64)
    polys = [list(p.vertices) for p in me.polygons]
    ob.evaluated_get(dg).to_mesh_clear()
    return v, polys


class Group:
    """Some objects, cached in their own spaces, put into the world on demand as one BVH."""

    def __init__(self, objs, dg, lift=0.0):
        self.items = []
        for ob in objs:
            v, p = local_mesh(ob, dg)
            if len(v) and p:
                self.items.append((ob, v, p))
        self.lift = lift
        self.key = None
        self.tree = None
        self.verts = None
        self.ranges = []          # (first polygon, object name) of the last world(), to name what touches

    def world(self, select=None):
        vs, ps, off = [], [], 0
        self.ranges = []
        for ob, v, p in self.items:
            if select is not None and not select(ob):
                continue
            if ob.hide_render:
                continue
            self.ranges.append((len(ps), ob.name))
            m = np.array(ob.matrix_world)
            w = v @ m[:3, :3].T + m[:3, 3]
            w[:, 2] += self.lift
            vs.append(w)
            ps += [[i + off for i in poly] for poly in p]
            off += len(v)
        if not vs:
            return None, None
        allv = np.concatenate(vs)
        return BVHTree.FromPolygons(allv.tolist(), ps), allv

    def name_of(self, poly):
        name = None
        for first, n in self.ranges:
            if poly >= first:
                name = n
        return name

    def tree_for(self, key, select=None):
        if key != self.key or self.tree is None:
            self.tree, self.verts = self.world(select)
            self.key = key
        return self.tree, self.verts


def nearest(verts, tree, every=3):
    if tree is None or verts is None:
        return None
    best = None
    for p in verts[::every]:
        hit = tree.find_nearest(Vector(p))
        if hit[0] is not None and (best is None or hit[3] < best[0]):
            best = (hit[3], tuple(round(float(c), 2) for c in p))
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots")
    ap.add_argument("--every", type=int, default=1, help="probe every nth drawn frame")
    ap.add_argument("--out")
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    story = json.loads((STORY / "story.json").read_text())
    tl = json.loads((ROOT / "out/work/lookout/timeline.json").read_text())
    kit.reset()
    look = story["look"]
    kit.set_fog(look["fog"], look["fog_density"], look["fog_start"])
    kit.world(look["sky"])
    kit.setup_render([270, 480], 1, 2, look.get("exposure", 0.0))
    setmod = bl_story.load_set(STORY)
    ctx = setmod.build(kit, story, tl)
    faces_dir = ROOT / "out/work/lookout/faces"
    faces_dir.mkdir(parents=True, exist_ok=True)
    chars = {n: (rig.Character(n, s, faces_dir), i) for i, (n, s) in enumerate(story["cast"].items())}
    frames = timeline.frame_list(tl, None)
    if a.shots:
        keep = set(a.shots.split(","))
        frames = [f for f in frames for s in tl["shots"] if s["id"] in keep and s["f0"] <= f < s["f1"]]
    frames = frames[::a.every]
    # pose once so every modifier is evaluated, then cache the meshes
    t0 = frames[0] / tl["fps"]
    setmod.animate(kit, story, tl, t0, ctx)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    gobj = [o for o in setmod.giant_objects(ctx["giant"]) if "curtain" not in o.name and ".light" not in o.name]
    giant = Group(gobj, dg)
    me = Group([o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("me.")], dg, lift=0.02)
    lamp = Group([o for o in ctx["lamp"].children if o.type == "MESH"], dg, lift=0.01)   # set down on a floor, it rests
    tower_objs = [o for o in ctx["tower"].children_recursive if o.type == "MESH" and not o.name.startswith("glass_")]
    tower = Group(tower_objs, dg)
    fence = Group([o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("gate.")], dg)
    trees = Group(ctx.get("tree_objs", []), dg)
    pairs = {k: {"overlap_frames": {}, "closest": None} for k in
             ("giant x tower", "giant x me", "giant x lamp", "giant x gate", "giant x trees", "me x tower",
              "me x gate", "lamp x tower")}

    def note(key, f, sid, over, near, ga=None, gb=None):
        rec = pairs[key]
        if over:
            rec["overlap_frames"].setdefault(sid, []).append(f)
            if ga is not None:
                names = rec.setdefault("parts", {}).setdefault(sid, set())
                for i, j in over[:40]:
                    names.add(f"{ga.name_of(i)} / {gb.name_of(j)}")
        if near is not None and (rec["closest"] is None or near[0] < rec["closest"][0]):
            rec["closest"] = (round(near[0], 3), f, sid, near[1])

    tstart = time.time()
    for n, f in enumerate(frames):
        t = f / tl["fps"]
        sid = next(s["id"] for s in tl["shots"] if s["start"] <= t < s["end"] or s is tl["shots"][-1])
        for name, (c, seed) in chars.items():
            s = acting.state(tl, name, t, seed)
            c.pose(s["x"], s["y"], s["z"], s["yaw"], s["legs"], s["arms"], s["arms_side"], s["head_yaw"],
                   s["head_pitch"], s["lean"], s["bob"], s["expr"], s["mouth"], s["look"], s["blink"], s["hidden"])
        setmod.animate(kit, story, tl, t, ctx)
        bpy.context.view_layer.update()
        gs = setmod.giant_state(tl, t)
        g_vis = gs is not None and not gs["hidden"]
        lean = round(ctx["tower"].rotation_euler.x, 4)
        tt, tv = tower.tree_for(("lean", lean, round(ctx["door"].rotation_euler.z, 3)))   # the door swings too
        ft, fv = fence.tree_for(("gate", round(ctx["gate"].rotation_euler.z, 3)))
        mt, mv = me.world()
        lt, lv = lamp.world()
        if mt is not None:
            note("me x tower", f, sid, mt.overlap(tt), None, me, tower)
            note("me x gate", f, sid, mt.overlap(ft), None, me, fence)
        if lt is not None:
            note("lamp x tower", f, sid, lt.overlap(tt), None, lamp, tower)
        if g_vis:
            gt, gv = giant.world()
            note("giant x tower", f, sid, gt.overlap(tt), nearest(gv, tt, 6), giant, tower)
            note("giant x gate", f, sid, gt.overlap(ft), nearest(gv, ft, 6), giant, fence)
            if mt is not None:
                note("giant x me", f, sid, gt.overlap(mt), nearest(mv, gt, 1), giant, me)
            if lt is not None:
                note("giant x lamp", f, sid, gt.overlap(lt), nearest(lv, gt, 1), giant, lamp)
            gx, gy = gs["pos"][0], gs["pos"][1]
            near_trees = lambda ob: (ob.location.x - gx) ** 2 + (ob.location.y - gy) ** 2 < 24.0 ** 2
            trt, trv = trees.world(near_trees)
            if trt is not None:
                note("giant x trees", f, sid, gt.overlap(trt), nearest(trv, gt, 2), giant, trees)
        if n % 200 == 0:
            print(f"  {n}/{len(frames)} frames, {time.time() - tstart:.0f} s", flush=True)
    rep = {k: {"overlap_shots": {s: [len(v), v[0], v[-1]] for s, v in r["overlap_frames"].items()},
               "parts": {s: sorted(v) for s, v in r.get("parts", {}).items()},
               "closest": r["closest"]} for k, r in pairs.items()}
    rep["frames_probed"] = len(frames)
    rep["seconds"] = round(time.time() - tstart, 1)
    for k, r in rep.items():
        if isinstance(r, dict):
            print(f"{k:14s} overlaps in {len(r['overlap_shots'])} shot(s) {r['overlap_shots'] or ''}  closest {r['closest']}")
            for sid, names in r["parts"].items():
                print(f"      {sid}: {', '.join(names[:6])}{' ...' if len(names) > 6 else ''}")
    print("frames", len(frames), "in", rep["seconds"], "s")
    if a.out:
        Path(a.out).write_text(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
