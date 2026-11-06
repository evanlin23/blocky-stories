"""The rule tag (a story's HUD on the camera), placed by the engine: just past the camera's near plane, so nothing
in the scene can come between it and the lens, and in whichever top corner keeps it off every face in the shot.

A set.py that hung its tag a fixed 1.0 m from the camera lost it behind anything nearer (a thermos close-up,
ep120 S40-S43) and parked it over faces (ep116 S17, ep111, ep112). story.json opts in:

    "hud": {"object": "tag", "at": [-0.37, 0.6], "size": 0.56}

`object` is the name of the empty or mesh set.py parents to the camera (a list for several). `at` is where its
origin sits in the frame (-1..1 across and up, the default corner); `size` is its scale as a share of the
frame's half width, so the tag keeps the angular size it had when set.py placed it itself (ep120's
`scale 0.56 * w2, location (-0.37 * w2, 0.6 * h2, -dist)` is exactly the example). Each frame, after
set.py's animate and the camera, the engine puts the object at DEPTH_K x the camera's clip_start and sizes it
for the lens. Once a shot, it looks at the faces at the shot's first, middle and last frames and keeps the
default corner unless a face is under it and the mirrored top corner is clearly clearer (`choose`): the tag never
jumps mid-shot. It sets the object's scale itself, so a set.py "pop" on the tag's scale no longer shows.

Pure python here (the choice, the boxes); `apply` is the Blender half, called from bl_story.py.
"""

from __future__ import annotations

DEPTH_K = 2.0   # the tag's distance from the lens, in clip_starts (0.05 m -> 0.1 m)


def spec(story: dict) -> dict | None:
    h = story.get("hud")
    if not h:
        return None
    objs = h.get("object", "tag")
    return {"objects": [objs] if isinstance(objs, str) else list(objs),
            "at": tuple(h.get("at", (-0.37, 0.6))), "size": float(h.get("size", 0.56))}


def overlap(a, b) -> float:
    """Area two boxes (x0, y0, x1, y1) share."""
    return max(0.0, min(a[2], b[2]) - max(a[0], b[0])) * max(0.0, min(a[3], b[3]) - max(a[1], b[1]))


def mirror(b):
    """The same box in the other top corner (mirrored across the frame's vertical middle)."""
    return (-b[2], b[1], -b[0], b[3])


SWAP_COVER = 0.1   # the default corner must cover at least this share of the tag with face before it moves
SWAP_BETTER = 0.5  # and the mirror must cover under this share of what the default covers


def choose(box, faces) -> int:
    """0: keep the default corner; 1: the mirrored one. The tag moves only when a face is really under it and the
    other corner is clearly clearer (ep120 S10 differed by 0.0002 of the frame: not worth a corner jump). When a
    face fills the top of the frame both corners cover it, and only a reframe helps (ep116 S17)."""
    area = max(1e-9, (box[2] - box[0]) * (box[3] - box[1]))
    cover = [sum(overlap(b, f) for f in faces) for b in (box, mirror(box))]
    return 1 if cover[0] >= SWAP_COVER * area and cover[1] < SWAP_BETTER * cover[0] else 0


def frame_box(at, size, local, aspect):
    """The tag's box in the frame (-1..1) with its origin at `at`: `local` is (x0, y0, x1, y1) of the tag's
    geometry in its own units at scale 1, `aspect` the frame's width / height."""
    ax, ay = at
    return (ax + size * local[0], ay + size * local[1] * aspect, ax + size * local[2], ay + size * local[3] * aspect)


def mirrored_at(at, size, local):
    """Where the origin goes so the tag's box is the mirror of its box at `at` (a tag needn't be centred on its
    origin)."""
    return (-at[0] - size * (local[0] + local[2]), at[1])


def place(at, size, lens, clip_start, aspect):
    """(location in camera space, uniform scale) for a tag with its origin at `at` in the frame. Blender's
    camera here fits a 24 mm sensor vertically, so the frame's half height at depth d is d * 12 / lens."""
    d = DEPTH_K * clip_start
    h2 = d * 12.0 / lens
    w2 = h2 * aspect
    return (at[0] * w2, at[1] * h2, -d), size * w2


# ------------------------------------------------------------------------------------------------- Blender half
_CHOICE: dict = {}
_LOCAL: dict = {}


def _local_box(root):
    """(x0, y0, x1, y1) of every mesh under `root`, in root's own unscaled space."""
    from mathutils import Vector

    inv = root.matrix_world.inverted()
    xs, ys = [], []
    stack = [root]
    while stack:
        ob = stack.pop()
        stack += list(ob.children)
        if ob.type == "MESH":
            m = inv @ ob.matrix_world
            for c in ob.bound_box:
                p = m @ Vector(c)
                xs.append(p.x)
                ys.append(p.y)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else (-0.5, -0.5, 0.5, 0.5)


def face_boxes(names):
    """Boxes (-1..1) of the cast's visible heads in the current pose, as the camera sees them."""
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector

    sc = bpy.context.scene
    bpy.context.view_layer.update()
    out = []
    for o in sc.objects:
        if o.type != "MESH" or ".headm" not in o.name or o.hide_render or not o.visible_get():
            continue
        if not any(o.name.startswith(n + ".") for n in names):
            continue
        pts = [world_to_camera_view(sc, sc.camera, o.matrix_world @ Vector(c)) for c in o.bound_box]
        pts = [p for p in pts if p.z > 0]
        if not pts:
            continue
        b = (min(p.x for p in pts) * 2 - 1, min(p.y for p in pts) * 2 - 1,
             max(p.x for p in pts) * 2 - 1, max(p.y for p in pts) * 2 - 1)
        b = (max(b[0], -1.0), max(b[1], -1.0), min(b[2], 1.0), min(b[3], 1.0))
        if b[2] > b[0] and b[3] > b[1]:
            out.append(b)
    return out


def apply(h, shot, pose_raw, t, names):
    """Place story.json's HUD objects for the frame at t. `pose_raw(t)` poses the scene (cast, set, camera) at t
    without this, for the once-a-shot look at the faces; the scene is posed at t again afterwards."""
    import bpy

    sc = bpy.context.scene
    cam = sc.camera
    aspect = sc.render.resolution_x / sc.render.resolution_y
    roots = [bpy.data.objects.get(n) for n in h["objects"]]
    roots = [r for r in roots if r is not None and r.parent is cam]
    if not roots:
        return
    for r in roots:
        if r.name not in _LOCAL:
            r.scale = (1.0, 1.0, 1.0)
            bpy.context.view_layer.update()
            _LOCAL[r.name] = _local_box(r)
    key = shot["id"]
    if key not in _CHOICE:
        fps_dt = 1.0 / 30.0
        ts = [shot["start"], (shot["start"] + shot["end"]) / 2, max(shot["start"], shot["end"] - fps_dt)]
        faces = []
        for u in ts:
            pose_raw(u)
            faces += face_boxes(names)
        lb = _LOCAL[roots[0].name]
        _CHOICE[key] = choose(frame_box(h["at"], h["size"], lb, aspect), faces)
        pose_raw(t)
    for r in roots:
        lb = _LOCAL[r.name]
        at = mirrored_at(h["at"], h["size"], lb) if _CHOICE[key] else h["at"]
        loc, s = place(at, h["size"], cam.data.lens, cam.data.clip_start, aspect)
        r.location = loc
        r.scale = (s, s, s)
