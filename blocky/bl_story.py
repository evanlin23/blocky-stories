"""Render one blocky story in Blender (bpy venv, never the repo's Python):

    <bpy python> blocky/bl_story.py job.json

job.json: {"story_dir": ..., "timeline": ..., "out": <dir>, "res": [w, h], "samples": n, "threads": n,
           "frames": [frame numbers] or null, "stills": [seconds] or null, "skip_existing": true,
           "clip": [seconds] or null, "clip_out": <json path>}

With "clip", nothing is drawn: the scene is posed at each of those times and every character's head is tested
against every other mesh with a BVH overlap (`python -m blocky clipcheck`). A head that passes through a prop, a
wall or another character is the kind of thing only the final used to show (warm-shoes, a face in a boot).

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

from blocky import acting, kit, polish, rig  # noqa: E402


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


def pose_at(t, story, tl, setmod, ctx, chars, shots):
    """Everything at time t: the cast, the set's own animation, the lights and the camera. Returns the shot."""
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
    return shot


def _owner(ob, names):
    """Who an object belongs to: the cast member whose name starts it ('<name>.'), else its top ancestor (a
    creature set.py builds under one root is one thing)."""
    top = ob
    while ob is not None:
        for n in names:
            if ob.name == n or ob.name.startswith(n + "."):
                return n
        top, ob = ob, ob.parent
    return "set:" + top.name


def _world_bvh(ob, depsgraph, shrink=1.0):
    """The evaluated mesh in world space as a BVH tree, scaled by `shrink` about its own middle (a head shrunk 10%
    only counts as clipping when it's more than a skin's depth in: a head on a pillow is fine)."""
    import bmesh
    from mathutils import Matrix, Vector
    from mathutils.bvhtree import BVHTree

    ev = ob.evaluated_get(depsgraph)
    me = ev.to_mesh()
    try:
        bm = bmesh.new()
        bm.from_mesh(me)
        if shrink != 1.0 and bm.verts:
            c = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
            bm.transform(Matrix.Translation(c) @ Matrix.Scale(shrink, 4) @ Matrix.Translation(-c))
        bm.transform(ev.matrix_world)
        return BVHTree.FromBMesh(bm) if bm.faces else None
    finally:
        ev.to_mesh_clear()


def _bbox(ob):
    from mathutils import Vector

    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def _touch(a, b, pad=0.0):
    return all(a[0][i] <= b[1][i] + pad and b[0][i] <= a[1][i] + pad for i in range(3))


def clip_check(job, story, tl, setmod, ctx, chars, shots):
    """Pose the film at each time in job["clip"] and test each visible head against every other rendered mesh (the
    set, its props, the other characters). The heads: every cast member's, plus the set objects whose names start
    with one of story.json's `clip_heads` (a creature set.py builds, like warm-shoes' cat: ["chead"]).
    Writes {"hits": [{t, shot, who, what}]}."""
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    names = list(chars)
    sc = bpy.context.scene
    hits, t0 = [], time.time()
    for t in job["clip"]:
        shot = pose_at(t, story, tl, setmod, ctx, chars, shots)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        meshes = [o for o in sc.objects if o.type == "MESH" and not o.hide_render and o.visible_get()]
        extra = tuple(story.get("clip_heads", []))
        heads = [o for o in meshes if (".headm" in o.name and not _owner(o, names).startswith("set:"))
                 or (extra and o.name.startswith(extra))]
        if not heads:
            continue
        boxes = {o.name: _bbox(o) for o in meshes}
        trees = {}
        for h in heads:
            who = _owner(h, names)
            hb = boxes[h.name]
            mid = [(hb[0][i] + hb[1][i]) / 2 for i in range(3)]
            v = world_to_camera_view(sc, sc.camera, Vector(mid))
            if not (v.z > 0 and -0.05 <= v.x <= 1.05 and -0.05 <= v.y <= 1.05):
                continue   # off screen: nobody sees it
            for o in meshes:
                if _owner(o, names) == who or not _touch(hb, boxes[o.name]):
                    continue
                if h.name not in trees:
                    trees[h.name] = _world_bvh(h, dg, 0.9)
                if o.name not in trees:
                    trees[o.name] = _world_bvh(o, dg)
                if trees[h.name] is None or trees[o.name] is None:
                    continue
                if trees[h.name].overlap(trees[o.name]):
                    hits.append({"t": round(t, 3), "shot": shot["id"], "who": who.removeprefix("set:"),
                                 "what": o.name})
    cams = camera_check(job, story, tl, setmod, ctx, chars, shots)
    Path(job["clip_out"]).write_text(json.dumps({"times": len(job["clip"]), "hits": hits, "cam": cams}, indent=1))
    print(f"clip check: {len(job['clip'])} times, {len(hits)} head overlap(s), {len(cams)} camera finding(s) in "
          f"{time.time() - t0:.0f} s", flush=True)


_CLEAR: dict = {}


def _see_through(ob) -> bool:
    """Glass, a window pane, anything mostly transparent: a shot through it isn't a blank (warm-shoes' window, ep105's
    rglass). A Principled material with transmission or alpha, or "glass"/"pane" in the object's or material's name."""
    if ob.name in _CLEAR:
        return _CLEAR[ob.name]
    clear = any(k in ob.name.lower() for k in ("glass", "pane"))
    for slot in ob.material_slots:
        m = slot.material
        if m is None:
            continue
        clear = clear or any(k in m.name.lower() for k in ("glass", "pane"))
        for n in (m.node_tree.nodes if m.use_nodes and m.node_tree else []):
            if n.type == "BSDF_PRINCIPLED":
                tr = n.inputs.get("Transmission Weight") or n.inputs.get("Transmission")
                al = n.inputs.get("Alpha")
                if (tr is not None and tr.default_value >= 0.5) or (al is not None and al.default_value < 0.5):
                    clear = True
    _CLEAR[ob.name] = clear
    return clear


def _cast(sc, dg, origin, d, cam, far):
    """The first rendered surface along a ray from origin: (distance, object name, its face looks away from the
    ray) or None. Skips what hangs on the camera (the rule tag), anything hidden from the render, and glass."""
    from mathutils import Vector

    o, travelled = Vector(origin), 0.0
    for _ in range(16):
        ok, loc, nrm, _i, ob, _m = sc.ray_cast(dg, o, d, distance=far - travelled)
        if not ok:
            return None
        top = ob
        while top.parent is not None and top is not cam:
            top = top.parent
        step = (loc - o).length
        if ob.hide_render or top is cam or _see_through(ob):
            travelled += step + 1e-4
            o = loc + d * 1e-4
            continue
        return travelled + step, ob.name, nrm.dot(d) > 0
    return None


def camera_check(job, story, tl, setmod, ctx, chars, shots):
    """At each time in job["cam"] ([t, shot]: every camera key, and each shot's first and last frame): is the
    lens inside a mesh, or right behind a surface that fills the frame (checks.cam_verdict)? Rays from the lens
    with scene.ray_cast: six along the axes, and a 7 x 7 grid through the frame."""
    import bpy
    from mathutils import Vector

    from blocky import checks

    sc = bpy.context.scene
    out = []
    for t, sid in job.get("cam") or []:
        pose_at(t, story, tl, setmod, ctx, chars, shots)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        cam = sc.camera
        mw = cam.matrix_world
        o = mw.translation.copy()
        axis = []
        for v in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            h = _cast(sc, dg, o, Vector(v), cam, 200.0)
            axis.append((h[1], h[2]) if h else (None, False))
        fr = cam.data.view_frame(scene=sc)   # the frame's corners in camera space: tr, br, bl, tl
        tr, br, bl, tl_ = fr[0], fr[1], fr[2], fr[3]
        n, grid = checks.CAM_GRID, []
        rot = mw.to_3x3()
        for i in range(n):
            for j in range(n):
                u, w = (i + 0.5) / n, (j + 0.5) / n
                p = tl_.lerp(tr, u).lerp(bl.lerp(br, u), w)
                d = (rot @ p).normalized()
                h = _cast(sc, dg, o, d, cam, 3.0)
                grid.append(h if h else (None, None, False))
        v = checks.cam_verdict(axis, grid, cast=list(chars))
        if v:
            out.append({"t": t, "shot": sid, **v})
    return out


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
    kit.FLASH_SAFE = bool(look.get("flash_safe", False))   # opt-in: slow, smooth flicker (kit.flicker_gain)
    sky = look.get("sky", look.get("fog", "#141820"))
    if look.get("hdri"):   # opt-in: light from a CC0 HDRI in assets/hdri/ (the camera still sees the sky colour)
        kit.world_hdri(look["hdri"], look.get("hdri_strength", 0.5), look.get("hdri_rotation", 0.0),
                       look.get("hdri_visible", False), sky, look.get("sky_strength", 1.0))
    else:
        kit.world(sky, look.get("sky_strength", 1.0))
    kit.setup_render(job["res"], job.get("samples", 8), job.get("threads", 2), look.get("exposure", 0.0))
    setmod = load_set(sdir)
    ctx = setmod.build(kit, story, tl) or {}
    chars = {}
    for i, (name, spec) in enumerate(story.get("cast", {}).items()):
        if spec.get("offscreen"):
            continue
        chars[name] = (rig.Character(name, spec, faces_dir), i)
    pol = polish.spec(story)   # the polish pack's camera moves on shots whose own camera holds still
    shots = polish.cam_specs(story, tl, pol)

    if job.get("clip") is not None:
        return clip_check(job, story, tl, setmod, ctx, chars, shots)
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
        shot = pose_at(t, story, tl, setmod, ctx, chars, shots)
        t0 = time.time()
        kit.render_to(path)
        print(f"frame {f} ({shot['id']}) {time.time() - t0:.1f}s  [{n + 1}/{len(frames)}]", flush=True)
    print(f"done {len(frames)} frames in {(time.time() - t_start) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
