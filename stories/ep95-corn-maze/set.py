"""Corn Maze (ep95): the narrator is the maze itself. A big gold cornfield cut with straw paths.

THE FIELD is a grid of 0.5 m cells (CELL). A "layout" is a set of path cells made from shapes (disc, ring, arc,
polyline), so later shots reuse the same tiles: "face" (S34, the reveal), "entrance" (S01 close-up corridor), and
stubs for "star", "tractor", "pig" and "partial" (S17's one curve of the smile). Each layout is built once as a pair of
meshes (corn bodies and paler tassels) at its own place, and animate() shows the one a shot asks for (story
"shot_layout": {"S34": "face"}), so a path is open in one shot and different in the next and never moves on screen.

THE MARKER (the rule meter): twelve small lantern icons in the top-left corner, parented to the camera (a 3D panel,
no text). The count lit comes from the cue "lanterns" {"n": 0..12} (default 12).
Nothing here has text, and no two surfaces share a plane (the paths are a ground plane, the quilt stands 2 cm proud).
"""

from __future__ import annotations

import math

import bpy

CELL = 0.5
FW, FH = 40.0, 64.0           # field size in metres (x, y), centred on its layout origin
BOX_FACES = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]


def h01(*xs):
    n = 0
    for x in xs:
        n = (n * 1103515245 + int(x) * 12345 + 12345) & 0x7FFFFFFF
    return ((n >> 8) & 0xFFFF) / 65535.0


# ------------------------------------------------------------------------------------------------ layouts
def disc(cx, cy, r):
    return lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def ring(cx, cy, rx, ry, w):
    def f(x, y):
        d = math.hypot((x - cx) / rx, (y - cy) / ry)
        return abs(d - 1.0) * min(rx, ry) <= w / 2
    return f


def arc(cx, cy, r, a0, a1, w):
    """A band of width w along a circle of radius r from angle a0 to a1 (degrees), with round ends."""
    def f(x, y):
        dx, dy = x - cx, y - cy
        d = math.hypot(dx, dy)
        a = math.degrees(math.atan2(dy, dx)) % 360
        lo, hi = a0 % 360, a1 % 360
        inside = lo <= a <= hi if lo <= hi else (a >= lo or a <= hi)
        if inside and abs(d - r) <= w / 2:
            return True
        for ang in (a0, a1):
            ex, ey = cx + r * math.cos(math.radians(ang)), cy + r * math.sin(math.radians(ang))
            if (x - ex) ** 2 + (y - ey) ** 2 <= (w / 2) ** 2:
                return True
        return False
    return f


def seg(x0, y0, x1, y1, w):
    def f(x, y):
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy or 1.0
        u = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / L2))
        return (x - (x0 + u * dx)) ** 2 + (y - (y0 + u * dy)) ** 2 <= (w / 2) ** 2
    return f


def poly(pts, w, closed=False):
    segs = [seg(*pts[i], *pts[i + 1], w) for i in range(len(pts) - 1)]
    if closed:
        segs.append(seg(*pts[-1], *pts[0], w))
    return lambda x, y: any(s(x, y) for s in segs)


EYE_L, EYE_R = (-6.5, 9.0), (6.5, 9.0)


def layout_shapes(name):
    if name == "face":     # head outline, two round eyes, a wide smile
        return [ring(0, 0, 16.0, 27.0, 1.8), disc(*EYE_L, 4.6), disc(*EYE_R, 4.6),
                arc(0, 3.0, 14.0, 212, 328, 2.8)]
    if name == "partial":  # S17: only one long curve, the edge of the smile
        return [arc(0, 3.0, 14.0, 215, 300, 2.4)]
    if name == "star":     # S42
        pts = [(12 * math.sin(math.radians(144 * k)), 12 * math.cos(math.radians(144 * k)) + 2) for k in range(5)]
        return [poly(pts + [pts[0]], 2.0), ring(0, 2, 15, 15, 1.6)]
    if name == "tractor":  # S43: body, cab, two wheels, an exhaust (TODO: refine)
        return [poly([(-9, -4), (9, -4), (9, 6), (-9, 6)], 1.8, True), poly([(-2, 6), (-2, 14), (7, 14), (7, 6)], 1.8, True),
                ring(-7, -8, 6, 6, 1.8), ring(9, -7, 3.2, 3.2, 1.8)]
    if name == "pig":      # S44: body, head, ear, snout, legs (TODO: refine)
        return [ring(-2, 0, 12, 8, 1.8), ring(13, 3, 5, 5, 1.8), disc(15.5, 2, 1.6), seg(-8, -8, -8, -15, 1.8),
                seg(4, -8, 4, -15, 1.8)]
    if name == "entrance":  # S01/S02: a straight corridor, 3 m wide, that bends out of sight
        return [seg(0, -40, 0, 0, 3.0), seg(0, 0, 8, 7, 3.0), seg(8, 7, 8, 40, 3.0)]
    raise KeyError(name)


def build_corn(kit, name, origin, mats, lean=(0.0, 0.0), w=FW, h=FH):
    """Corn clumps on every cell that is not a path. Returns the two objects (bodies, tassels)."""
    shapes = layout_shapes(name)
    ox, oy = origin
    nx, ny = int(w / CELL), int(h / CELL)
    bv, bf, tv, tf = [], [], [], []
    for i in range(nx):
        for j in range(ny):
            x, y = -w / 2 + (i + 0.5) * CELL, -h / 2 + (j + 0.5) * CELL
            if any(s(x, y) for s in shapes):
                continue
            hh = 2.5 + 0.55 * (h01(i, j, 1) - 0.5) * 2
            half = CELL / 2 * 0.98
            for (vs, fs, z0, z1, hw, shade) in ((bv, bf, 0.0, hh, half, 0), (tv, tf, hh - 0.1, hh + 0.3, half * 0.62, 1)):
                k = len(vs)
                lx0, lx1 = lean[0] * z0 / 2.5, lean[0] * z1 / 2.5
                ly0, ly1 = lean[1] * z0 / 2.5, lean[1] * z1 / 2.5
                cx, cy = ox + x, oy + y
                for (zz, lx, ly) in ((z0, lx0, ly0), (z1, lx1, ly1)):
                    for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                        vs.append((cx + lx + sx * hw, cy + ly + sy * hw, zz))
                fs.extend([tuple(k + a for a in f) for f in BOX_FACES])
    body = kit.mesh_obj(f"corn.{name}", bv, bf, mats["corn"], smooth=False)
    tass = kit.mesh_obj(f"corn.{name}.top", tv, tf, mats["tassel"], smooth=False)
    return body, tass


# ------------------------------------------------------------------------------------------------ the set
def materials(kit):
    return {
        "corn": kit.plastic("#7a651f", 0.85, "corn body", spec=0.1),
        "tassel": kit.plastic("#e2b73e", 0.8, "corn tassel", spec=0.1),
        "straw": kit.plastic("#aebfdc", 0.95, "straw", spec=0.05),
        "grass": kit.plastic("#27443f", 0.95, "night grass", spec=0.05),
        "iron": kit.plastic("#2b2b30", 0.5, "iron", spec=0.4),
        "pole": kit.plastic("#7a5230", 0.8, "pole", spec=0.1),
        "flame": kit.emit("#ffb347", 5.0, "flame"),
        "glowpad": kit.emit("#ff8a2a", 0.4, "glowpad"),
        "quilt1": kit.plastic("#d8443a", 0.9, "quilt red", spec=0.05),
        "quilt2": kit.plastic("#f2c94c", 0.9, "quilt gold", spec=0.05),
        "quilt3": kit.plastic("#3d6ea6", 0.9, "quilt blue", spec=0.05),
        "stroke": kit.emit("#f2c94c", 1.0, "stroke"),
        "lit": kit.emit("#ff9f2e", 2.0, "icon lit"),
        "dark": kit.plastic("#2c2622", 0.7, "icon dark", spec=0.1),
        "core": kit.emit("#ffd98a", 2.4, "icon core"),
        "plate": kit.plastic("#1a1620", 0.9, "icon plate", spec=0.05),
        "icon_iron": kit.emit("#ff7a1f", 1.6, "icon roof"),
    }


def build_lantern(kit, M, ox, oy):
    kit.box("pole", (0.2, 0.2, 3.2), (ox, oy, 1.6), M["pole"], bevel=0.02)
    for k in range(2):        # the lore tally: two strokes on the pole, proud of its face
        kit.box(f"stroke{k}", (0.03, 0.03, 0.34), (ox - 0.1 - 0.015, oy - 0.04 + k * 0.08, 1.35), M["stroke"])
    z = 2.55
    kit.box("lant.base", (0.42, 0.42, 0.08), (ox, oy, z), M["iron"], bevel=0.015)
    kit.box("lant.flame", (0.26, 0.26, 0.42), (ox, oy, z + 0.27), M["flame"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box("lant.bar", (0.04, 0.04, 0.46), (ox + sx * 0.2, oy + sy * 0.2, z + 0.27), M["iron"])
    kit.box("lant.cap", (0.5, 0.5, 0.07), (ox, oy, z + 0.53), M["iron"], bevel=0.015)
    kit.cyl("lant.roof", 0.3, 0.2, (ox, oy, z + 0.67), M["iron"], n=4, r2=0.05, rot=(0, 0, math.pi / 4))
    kit.box("lant.ring", (0.05, 0.3, 0.05), (ox, oy, z + 0.84), M["iron"])
    kit.light("lant.light", "POINT", (ox, oy - 0.4, z + 0.27), 260, "#ffb347", size=0.15)


def build_marker(kit, M, ctx):
    """Twelve lantern icons, 3 rows of 4, parented to the camera at its top-left."""
    cam = kit.OBJ["cam"]
    root = kit.empty("marker", (0, 0, 0), parent=cam)
    ctx["icons"] = []
    d = 1.6
    kit.box("marker.plate", (0.25, 0.27, 0.01), (-0.275 + 0.081, 0.49 - 0.082 - 0.0, -d - 0.03), M["plate"], parent=root)
    x0, y0, dx, dy = -0.275, 0.49, 0.054, -0.082
    for n in range(12):
        r, c = divmod(n, 4)
        cx, cy = x0 + c * dx, y0 + r * dy
        e = kit.empty(f"icon{n}", (cx, cy, -d), parent=root)
        e.scale = (0.5, 0.5, 0.5)
        parts = {
            "lit": kit.box(f"icon{n}.body", (0.07, 0.082, 0.012), (0, -0.004, 0), M["lit"], parent=e),
            "dark": kit.box(f"icon{n}.body.d", (0.07, 0.082, 0.012), (0, -0.004, 0), M["dark"], parent=e),
        }
        kit.cyl(f"icon{n}.roof", 0.056, 0.016, (0, 0.056, 0.003), M["icon_iron"], n=3, rot=(0, 0, math.pi / 2), parent=e)
        kit.box(f"icon{n}.ring", (0.034, 0.01, 0.014), (0, 0.092, 0.003), M["icon_iron"], parent=e)
        kit.box(f"icon{n}.ringv", (0.01, 0.026, 0.014), (0, 0.08, 0.003), M["icon_iron"], parent=e)
        kit.box(f"icon{n}.core", (0.03, 0.044, 0.016), (0, -0.004, 0.003), M["core"], parent=e)
        ctx["icons"].append(parts)


def build_farm(kit, M):
    """Context at the field's edge (seen from above in S34): the red barn, the farmhouse and the truck."""
    red = kit.plastic("#8a2e2a", 0.8, "barn red", spec=0.05)
    roof = kit.plastic("#3a3f4c", 0.8, "roof", spec=0.05)
    wall = kit.plastic("#d8d0c0", 0.8, "house wall", spec=0.05)
    win = kit.emit("#ffb347", 3.0, "window")
    kit.box("barn", (9, 7, 5), (-27, -37, 2.5), red)
    kit.cyl("barn.roof", 5.6, 9.4, (-27, -37, 6.2), roof, n=4, r2=0.3, rot=(0, math.pi / 2, math.pi / 4))
    kit.box("house", (9, 7, 4), (26, -38, 2.0), wall)
    kit.cyl("house.roof", 6.2, 9.6, (26, -38, 5.4), roof, n=4, r2=0.3, rot=(0, math.pi / 2, math.pi / 4))
    kit.box("house.win", (1.4, 0.1, 1.4), (24, -41.55, 2.2), win)
    kit.box("truck", (2.2, 5.0, 1.6), (-27, -29, 0.8), kit.plastic("#d8443a", 0.6, "truck red"))
    for k, (tx, ty) in enumerate(((-31, 38), (30, 36), (-33, 8), (33, -6))):
        kit.prop("commontree_1", (tx, ty, 0), rot=40 * k, height=7.0, tint="#4f7a5a")


def build(kit, story, tl):
    ctx = {"story": story, "kit": kit}
    M = materials(kit)
    ctx["M"] = M
    # ground: grass far out, straw under the maze (the paths), with the field 2 cm proud of nothing
    kit.plane("ground", (400, 400), (0, 0, -0.02), M["grass"])
    ctx["layouts"] = {}
    for name in story.get("layouts", ["face"]):
        if name == "entrance":
            ox = 200.0
            kit.plane(f"straw.{name}", (FW, FH), (ox, 0, 0.0), M["straw"])
            ctx["layouts"][name] = build_corn(kit, name, (ox, 0), M, lean=(0.0, -0.9))
        else:
            kit.plane(f"straw.{name}", (FW, FH), (0, 0, 0.0), M["straw"])
            ctx["layouts"][name] = build_corn(kit, name, (0, 0), M)
        ctx["layouts"][name][0].hide_render = True
        ctx["layouts"][name][1].hide_render = True
    build_lantern(kit, M, 200.3, 0.0)
    # June's dot in the middle of one eye: a warm pad, a quilt of four squares, a flashlight glow
    ex, ey = EYE_L
    kit.cyl("june.pad", 1.5, 0.01, (ex, ey, 0.02), M["glowpad"], n=32)
    for k, (qx, qy, m) in enumerate(((-0.4, -0.3, "quilt1"), (0.4, -0.3, "quilt2"), (-0.4, 0.3, "quilt3"), (0.4, 0.3, "quilt1"))):
        kit.box(f"june.quilt{k}", (0.78, 0.58, 0.08), (ex + qx, ey + qy, 0.07), M[m])
    kit.sphere("june.torch", 0.22, (ex + 0.1, ey + 0.1, 0.4), M["flame"], seg=10)
    kit.light("june.light", "POINT", (ex, ey, 1.6), 400, "#ffb347", size=0.4)
    build_farm(kit, M)
    # the sky lights: the moon (S34) and a low gold sun (S01)
    kit.light("moon", "SUN", (0, 0, 60), 2.4, "#b4ccff", rot=(math.radians(2), 0, 0))
    kit.light("gold", "SUN", (0, 0, 60), 3.0, "#ffb870", rot=(math.radians(72), 0, math.radians(30)))
    for nm in ("moon", "gold"):
        kit.LIGHTS[nm]["light"].angle = math.radians(18)   # soft shadow edges
    build_marker(kit, M, ctx)
    return ctx


LOOKS = {   # per shot: which lights, the world colour and strength, exposure
    "moon": {"moon": 1.0, "gold": 0.0, "lant.light": 0.0, "june.light": 1.0, "world": ("#4d6aa8", 1.3), "exp": 0.05},
    "dusk": {"moon": 0.0, "gold": 1.0, "lant.light": 1.0, "june.light": 0.0, "world": ("#7fc8ff", 1.2), "exp": 0.2},
}


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


def cue_val(tl, name, t, key, default):
    out = default
    for c in tl.get("cues", []):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c.get(key, out)
    return out


def animate(kit, story, tl, t, ctx):
    shot = _shot(tl, t)
    want = story.get("shot_layout", {}).get(shot["id"])
    for name, (b, tp) in ctx["layouts"].items():
        b.hide_render = tp.hide_render = (name != want)
    look = LOOKS[story.get("shot_look", {}).get(shot["id"], "moon")]
    w = bpy.context.scene.world.node_tree.nodes["Background"]
    w.inputs["Color"].default_value = kit.col(look["world"][0])
    w.inputs["Strength"].default_value = look["world"][1]
    bpy.context.scene.view_settings.exposure = look["exp"]
    n = int(cue_val(tl, "lanterns", t, "n", 12))
    for k, parts in enumerate(ctx["icons"]):
        parts["lit"].hide_render = k >= n
        parts["dark"].hide_render = k < n
    return {k: v for k, v in look.items() if k not in ("world", "exp")}
