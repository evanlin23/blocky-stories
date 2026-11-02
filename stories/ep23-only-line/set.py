"""Only Line: a small old playhouse in rehearsal week, and the Prompter (ep23). Built from kit.py's parts; nothing
here is shared with another story's set.

Coordinates (metres, z up, the stage floor is z = 0). The stage runs x -9 .. 9 from the lip (y = 0) to the brick
back wall (y = 7.2). The proscenium is at y = -0.2 with its opening x -4.2 .. 4.2. A character with yaw 0 faces
-y, which is the house: the seats start at y = -2.6 and step back and up. Stage left is +x: four bottle-green curtain legs
hang there (inner edge x = 3.7), and behind the fourth the back wall carries the chalk tally. My flat is at x = -40
and my car at x = +40 (separate little sets, nothing in common with the stage).

THE PROMPTER (RULES.md, The creature): one model, built once and posed per shot from the "prompter" cue. An ordinary
R6-shaped body at 0.85 of our height in a long soot-black coat with a column of dull gilt buttons, and on it a head
about three times too big: a cracked gilt stage mask, a smooth oval with carved brows, a nose ridge, two eye pits with
one warm spark deep in each (the brightest thing in frame) and a carved closed mouth that, from L50 on, is a tall dark
oval going back into black. Wrong in one dimension only: the head's width. It is never seen moving, only nearer.
Light: the stage wash does not reach it (its front lights are dead). A key from low in the wings (the blue running
light), a thin warm rim on the mask's edge, and the eye sparks.

Cues read here:
- mood: {"set": a MOODS name, "dur": s} the light, eased from the mood before (every change is a ramp)
- prompter: {"pos": [x, y], "yaw": deg, "head": deg (the mask turned on its neck), "mouth": 0|1, "hidden": bool,
  "key": [dx, dy, dz], "rim": [dx, dy, dz], "key_gain": g, "rim_gain": g}
- costume: {"who": "walt", "beard": b, "crown": b, "robe": b} or {"who": "me", "cloak": b}
- chairs: {"on": bool}   - audience: {"on": bool}
Acting keys read here (acting.py ignores them): "sit": true (R6 sitting, the legs straight out).
"""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector as V

CEIL = 9.0
U = 0.29                      # metres per unit in the Prompter's own build (0.85 x the rig's 0.34)
MASK_A, MASK_B, MASK_C = 1.75, 0.6, 2.05     # the mask is an ellipsoid: 3.5 wide, 1.2 deep, 4.1 tall (units)
ROWS = 10
ROW_Y0, ROW_DY, ROW_Z0, ROW_DZ = -2.6, 0.95, -0.65, 0.12


def row_y(r):
    return ROW_Y0 - ROW_DY * r


def row_z(r):
    return ROW_Z0 + ROW_DZ * r


def seat_xs():
    return [round(-4.06 + 0.58 * k, 2) for k in range(15) if not (-2.7 < -4.06 + 0.58 * k < -2.0)]


# ------------------------------------------------------------------------------------------------ helpers


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def _last(cs, t):
    cs = [c for c in cs if c["t"] <= t + 1e-9]
    return cs[-1] if cs else None


def _switch(keys, attr, t, default):
    v = default
    for k in keys:
        if attr in k and k["t"] <= t + 1e-9:
            v = k[attr]
    return v


def _show(ob, on):
    for o in [ob] + list(ob.children_recursive):
        o.hide_render = not on


def tube(kit, name, r_out, r_in, z0, z1, mat, parent, n=28):
    """A ring of wall between two radii, from z0 to z1 along its own axis."""
    verts, faces = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        c, s = math.cos(a), math.sin(a)
        verts += [(r_out * c, r_out * s, z0), (r_out * c, r_out * s, z1), (r_in * c, r_in * s, z1), (r_in * c, r_in * s, z0)]
    for i in range(n):
        a, b = 4 * i, 4 * ((i + 1) % n)
        faces += [(a, b, b + 1, a + 1), (a + 1, b + 1, b + 2, a + 2), (a + 2, b + 2, b + 3, a + 3), (a + 3, b + 3, b, a)]
    return kit.mesh_obj(name, verts, faces, mat, parent, smooth=True)


def pleated(kit, name, x0, x1, y, z0, z1, mat, folds=8, amp=0.07):
    """A curtain leg: a velvet sheet hanging in folds."""
    n = folds * 5
    verts, faces = [], []
    for i in range(n + 1):
        u = i / n
        verts += [(x0 + (x1 - x0) * u, y + amp * math.sin(u * folds * 2 * math.pi), z0),
                  (x0 + (x1 - x0) * u, y + amp * math.sin(u * folds * 2 * math.pi), z1)]
    for i in range(n):
        a = 2 * i
        faces.append((a, a + 2, a + 3, a + 1))
    return kit.mesh_obj(name, verts, faces, mat, None, smooth=True)


def light_only(kit, coll, light_name, objs):
    col = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = "INCLUDE"
    kit.LIGHTS[light_name]["obj"].light_linking.receiver_collection = col


def light_except(kit, coll, light_name, objs):
    col = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = "EXCLUDE"
    kit.LIGHTS[light_name]["obj"].light_linking.receiver_collection = col


def lamp(kit, name, kind, loc, energy, hexc, aim=None, size=0.2, spot=None, blend=0.4):
    ob = kit.light(name, kind, loc, energy, hexc, size=size, spot=spot, blend=blend)
    ob.visible_camera = False
    if aim is not None:
        kit.aim(ob, aim)
    return ob


# ------------------------------------------------------------------------------------------------ materials


def materials(kit):
    M = {}
    M["wood"] = kit.planks("#4a3626", "#2a1e15", scale=1.4, axis="Y", name="stage boards", rough=0.7)
    M["wood2"] = kit.planks("#33261b", "#1e1510", scale=1.2, axis="X", name="flat boards", rough=0.75)
    M["brick"] = kit.bricks("#5a4b4a", "#443837", mortar="#262223", scale=1.0, name="cold brick", grime_amt=0.5)
    M["black"] = kit.plastic("#08080a", 0.7, name="black")
    M["soot"] = kit.plastic("#171517", 0.8, name="soot coat", spec=0.2)
    M["gilt"] = kit.plastic("#b8913a", 0.38, name="gilt", spec=0.7)
    M["gilt_dull"] = kit.plastic("#7d6428", 0.5, name="gilt dull")
    M["mask"] = kit.grime("#b8913a", 0.3, 5.0, name="mask gilt", rough=0.42)
    M["bronze"] = kit.plastic("#3f2c10", 0.7, name="crack bronze")
    M["pit"] = kit.plastic("#020203", 0.9, name="pit")
    M["velvet"] = kit.plastic("#1a4a35", 0.97, name="velvet")
    M["seat"] = kit.plastic("#4b4049", 0.92, name="seat plum")
    M["carpet"] = kit.grime("#2a1f27", 0.5, 2.0, name="carpet", rough=0.95)
    M["dark_wall"] = kit.plastic("#16141a", 0.9, name="dark wall")
    M["tape_w"] = kit.plastic("#cfc8b2", 0.85, name="tape white")
    M["tape_y"] = kit.plastic("#e3b81f", 0.85, name="tape yellow")
    M["chalk"] = kit.emit("#e0cc8a", 0.7, name="chalk")
    M["steel"] = kit.metal("#6c7075", 0.45, name="steel")
    M["tin"] = kit.plastic("#9ba2a8", 0.4, name="tin", spec=0.8)
    M["white"] = kit.plastic("#e9e9e4", 0.9, name="beard white")
    M["robe"] = kit.plastic("#2c3b5c", 0.9, name="robe")
    M["robe_trim"] = kit.plastic("#b8913a", 0.5, name="robe trim")
    M["cloak"] = kit.plastic("#2b2d33", 0.95, name="cloak")
    M["wood_dark"] = kit.plastic("#3a2a1e", 0.7, name="chair wood")
    M["folding"] = kit.plastic("#7a7e84", 0.5, name="folding chair")
    M["paper"] = kit.plastic("#d9d4c6", 0.9, name="paper")
    M["grey_bar"] = kit.plastic("#5d5f66", 0.9, name="grey bar")
    M["bulb"] = kit.emit("#ffe3b0", 6.0, name="bulb")
    M["lamp_shade"] = kit.plastic("#2f4a3a", 0.6, name="lamp shade")
    M["asphalt"] = kit.grime("#1a1b20", 0.5, 3.0, name="asphalt", rough=0.9)
    M["car"] = kit.plastic("#38585f", 0.5, name="car body")
    M["tyre"] = kit.plastic("#0c0c0e", 0.9, name="tyre")
    M["window_night"] = kit.emit("#1c2a46", 0.5, name="window night")
    M["head_dark"] = kit.plastic("#2d2b38", 0.9, name="aud head")
    M["body_dark"] = kit.plastic("#34323f", 0.9, name="aud body")
    M["spark"] = kit.emit("#ff9a2e", 5.0, name="eye spark")
    return M


# ------------------------------------------------------------------------------------------------ the playhouse


def build_stage(kit, ctx, M):
    kit.box("stage floor", (18, 7.4, 0.2), (0, 3.7, -0.1), M["wood"])
    kit.box("stage lip", (18, 0.06, 0.8), (0, -0.03, -0.4), M["black"])
    kit.box("pit floor", (18, 2.5, 0.2), (0, -1.35, -0.75), M["carpet"])
    kit.box("back wall", (18, 0.3, 9.0), (0, 7.35, 4.5), M["brick"])
    for sx in (-1, 1):
        kit.box(f"side wall {sx}", (0.3, 7.6, 9.0), (sx * 9.0, 3.6, 4.5), M["brick"])
    # the proscenium: soot-black with worn gilt edging
    for sx in (-1, 1):
        kit.box(f"pros col {sx}", (1.0, 0.6, 5.9), (sx * 4.7, -0.2, 2.25), M["black"])
        kit.box(f"pros trim {sx}", (0.07, 0.64, 4.6), (sx * 4.18, -0.2, 2.3), M["gilt_dull"])
        kit.box(f"pros foot {sx}", (1.04, 0.64, 0.12), (sx * 4.7, -0.2, -0.3), M["gilt_dull"])
    kit.box("pros beam", (10.4, 0.6, 1.3), (0, -0.2, 5.25), M["black"])
    kit.box("pros trim top", (8.5, 0.64, 0.07), (0, -0.2, 4.58), M["gilt_dull"])
    for k in range(9):
        kit.box(f"pros tile {k}", (0.5, 0.64, 0.14), (-3.6 + 0.9 * k, -0.2, 5.0), M["gilt_dull"], bevel=0.02)
    # the tall green curtain legs in the wings, four a side, hanging in velvet folds
    legy = ctx["places"]["legy"]
    for sx in (-1, 1):
        for k, y in enumerate(legy):
            x0, x1 = (3.7, 5.3) if sx > 0 else (-5.3, -3.7)
            pleated(kit, f"leg {sx} {k}", x0, x1, y, 0.04, 4.6, M["velvet"])
    # the tape marks: five white, the yellow one last (stage left)
    for k, (x, y) in enumerate(ctx["places"]["marks"]):
        m = M["tape_y"] if k == 5 else M["tape_w"]
        rot = (0, 0, math.radians(((k * 37) % 11) - 5))
        kit.box(f"mark a {k}", (0.5, 0.07, 0.008), (x, y, 0.004), m, rot=rot)
        kit.box(f"mark b {k}", (0.07, 0.5, 0.008), (x, y, 0.004), m, rot=rot)
    kit.box("king mark", (0.45, 0.07, 0.008), (0.0, ctx["places"]["king"][1], 0.004), M["tape_w"])
    # the eight chalk strokes on the brick, in the wings behind the fourth leg (pale gilt, for a cast of seven)
    for k in range(8):
        x = 5.05 + 0.07 * k + 0.004 * math.sin(k * 2.3)
        kit.box(f"chalk {k}", (0.02, 0.012, 0.25 + 0.015 * math.sin(k * 1.9)), (x, 7.195, 1.04), M["chalk"],
                rot=(0, 0.035 * math.sin(k * 3.1), 0), bevel=0.004)
    # paper cups on the stage edge
    for k, x in enumerate((-0.05, 0.9)):
        kit.cyl(f"cup {k}", 0.04, 0.1, (x, 0.18, 0.05), M["paper"], n=14, r2=0.03)
    # the ghost light: a bare bulb in a cage on a stand
    gx, gy = ctx["places"]["ghost"]
    kit.cyl("ghost base", 0.22, 0.04, (gx, gy, 0.02), M["steel"])
    kit.cyl("ghost pole", 0.022, 1.7, (gx, gy, 0.87), M["steel"], n=10)
    kit.sphere("ghost bulb", 0.075, (gx, gy, 1.78), M["bulb"], seg=10)
    for k in range(4):
        a = k * math.pi / 2
        kit.box(f"ghost cage {k}", (0.012, 0.012, 0.3), (gx + 0.12 * math.cos(a), gy + 0.12 * math.sin(a), 1.78), M["steel"])
    kit.cyl("ghost cap", 0.13, 0.02, (gx, gy, 1.94), M["steel"], n=14)


def build_house(kit, ctx, M):
    xs = seat_xs()
    ctx["seats"] = []
    for r in range(ROWS):
        y, z = row_y(r), row_z(r)
        kit.box(f"row {r}", (10.0, ROW_DY + 0.02, z + 1.1), (0, y, (z - 1.1) / 2 + 0.0), M["carpet"])
        for x in xs:
            kit.box(f"seat {r} {x}", (0.5, 0.5, 0.1), (x, y, z + 0.42), M["seat"], bevel=0.03)
            kit.box(f"back {r} {x}", (0.5, 0.1, 0.62), (x, y - 0.27, z + 0.78), M["seat"], bevel=0.04)
            kit.box(f"rest {r} {x}", (0.1, 0.42, 0.06), (x + 0.3, y, z + 0.6), M["black"])
    # the audience for opening night: dark heads and shoulders in most of the seats from the 2nd row back
    aud = []
    for r in range(1, ROWS):
        for i, x in enumerate(xs):
            if kit.hash01(r, i, 5) < 0.3 or (r == 2 and abs(x + 0.58) < 0.1):
                continue
            h = 0.02 * kit.hash01(r, i, 9)
            hd = kit.sphere(f"aud head {r} {i}", 0.12, (x, row_y(r) - 0.12, row_z(r) + 0.95 + h), M["head_dark"], seg=8)
            bd = kit.box(f"aud body {r} {i}", (0.44, 0.26, 0.5), (x, row_y(r) - 0.12, row_z(r) + 0.66), M["body_dark"], bevel=0.05)
            aud += [hd, bd]
            hd.hide_render = bd.hide_render = True
    ctx["aud"] = aud


def build_chairs(kit, ctx, M):
    ctx["chairs"] = []
    ctr = (0.0, 3.2)
    for k, (x, y) in enumerate(ctx["places"]["chairs"]):
        yaw = math.atan2(ctr[0] - x, -(ctr[1] - y))
        root = kit.empty(f"chair {k}", (x, y, 0), rot=(0, 0, yaw))
        kit.box(f"chair seat {k}", (0.42, 0.42, 0.04), (0, 0, 0.45), M["folding"], root)
        kit.box(f"chair back {k}", (0.42, 0.03, 0.34), (0, 0.2, 0.7), M["folding"], root)
        for sx in (-1, 1):
            for sy in (-1, 1):
                kit.box(f"chair leg {k} {sx} {sy}", (0.025, 0.025, 0.45), (sx * 0.18, sy * 0.18, 0.225), M["steel"], root)
        root.hide_render = True
        ctx["chairs"].append(root)


# ------------------------------------------------------------------------------------------------ my flat and car


def build_flat(kit, ctx, M):
    fx, fy = ctx["places"]["flat"]
    kit.box("flat floor", (7, 7, 0.1), (fx, fy, -0.05), M["wood2"])
    kit.box("flat wall back", (7, 0.12, 3.0), (fx, fy - 2.5, 1.5), M["dark_wall"])
    kit.box("flat wall front", (7, 0.12, 3.0), (fx, fy + 3.2, 1.5), M["dark_wall"])
    for sx in (-1, 1):
        kit.box(f"flat wall side {sx}", (0.12, 6.0, 3.0), (fx + sx * 3.4, fy + 0.35, 1.5), M["dark_wall"])
    kit.box("flat window", (1.1, 0.04, 1.1), (fx + 1.2, fy - 2.42, 1.5), M["window_night"])
    for k in (-1, 1):
        kit.box(f"flat sash {k}", (0.04, 0.05, 1.1), (fx + 1.2 + k * 0.0 + (0.0 if k < 0 else 0.0), fy - 2.4, 1.5), M["black"])
    kit.box("flat sash h", (1.1, 0.05, 0.04), (fx + 1.2, fy - 2.4, 1.5), M["black"])
    kit.box("table top", (1.4, 0.8, 0.05), (fx, fy + 0.05, 0.74), M["wood_dark"], bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"table leg {sx}{sy}", (0.05, 0.05, 0.72), (fx + sx * 0.64, fy + 0.05 + sy * 0.34, 0.36), M["wood_dark"])
    kit.box("chair seat flat", (0.46, 0.46, 0.05), (fx, fy - 0.85, 0.43), M["wood_dark"], bevel=0.01)
    kit.box("chair back flat", (0.46, 0.05, 0.5), (fx, fy - 1.08, 0.7), M["wood_dark"], bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"chair leg flat {sx}{sy}", (0.04, 0.04, 0.42), (fx + sx * 0.2, fy - 0.85 + sy * 0.2, 0.21), M["wood_dark"])
    # the script: a little stack of pages, grey bars for lines, no words
    for k in range(3):
        kit.box(f"page {k}", (0.31, 0.42, 0.012), (fx + 0.12 + 0.012 * k, fy - 0.02 + 0.01 * k, 0.77 + 0.012 * k), M["paper"],
                rot=(0, 0, math.radians(3 * k - 3)))
    for k in range(9):
        kit.box(f"bar {k}", (0.2 - 0.03 * (k % 3 == 2), 0.012, 0.003), (fx + 0.12, fy - 0.17 + 0.038 * k, 0.8), M["grey_bar"])
    # the desk lamp
    kit.cyl("lamp base", 0.09, 0.03, (fx - 0.5, fy + 0.22, 0.765), M["black"], n=14)
    kit.box("lamp arm", (0.02, 0.02, 0.4), (fx - 0.5, fy + 0.22, 0.97), M["black"])
    kit.cyl("lamp shade", 0.1, 0.14, (fx - 0.46, fy + 0.2, 1.2), M["lamp_shade"], n=16, r2=0.05, rot=(0.5, 0, 0))
    kit.sphere("lamp bulb", 0.035, (fx - 0.46, fy + 0.16, 1.14), M["bulb"], seg=8)
    # a shelf on the wall behind me
    kit.box("flat shelf", (1.4, 0.22, 0.04), (fx - 1.2, fy - 2.34, 1.7), M["wood_dark"])


def build_car(kit, ctx, M):
    cx, cy = ctx["places"]["car"]
    kit.box("road", (16, 16, 0.1), (cx, cy, -0.05), M["asphalt"])
    kit.box("car body", (1.75, 4.2, 0.5), (cx, cy, 0.55), M["car"], bevel=0.05)
    kit.box("car hood", (1.7, 1.3, 0.12), (cx, cy - 1.45, 0.86), M["car"], bevel=0.04)
    kit.box("car trunk", (1.7, 0.9, 0.12), (cx, cy + 1.6, 0.86), M["car"], bevel=0.04)
    kit.box("car dash", (1.6, 0.4, 0.34), (cx, cy - 0.75, 0.98), M["tyre"], bevel=0.04)
    kit.box("car floor", (1.6, 2.3, 0.04), (cx, cy + 0.3, 0.32), M["tyre"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"wheel {sx}{sy}", 0.33, 0.22, (cx + sx * 0.88, cy + sy * 1.4, 0.33), M["tyre"], rot=(0, math.pi / 2, 0), n=18)
            kit.box(f"pillar {sx}{sy}", (0.07, 0.07, 1.3), (cx + sx * 0.8, cy + sy * 0.75, 1.47), M["car"])
    kit.box("car roof", (1.7, 1.8, 0.07), (cx, cy, 2.15), M["car"], bevel=0.02)
    kit.box("car seat", (0.55, 0.55, 0.12), (cx - 0.4, cy + 0.1, 0.46), M["tyre"], bevel=0.03)
    kit.box("car seat back", (0.55, 0.1, 0.55), (cx - 0.4, cy + 0.42, 0.78), M["tyre"], bevel=0.03)
    wheel = kit.cyl("steering wheel", 0.17, 0.03, (cx - 0.4, cy - 0.5, 1.12), M["tyre"], n=20, r2=0.17)
    wheel.rotation_euler = (math.radians(-60), 0, 0)
    gx, gy = cx + 2.7, cy - 0.5
    kit.cyl("street pole", 0.05, 4.6, (gx, gy, 2.3), M["steel"], n=10)
    kit.box("street arm", (1.2, 0.07, 0.07), (gx - 0.55, gy, 4.55), M["steel"])
    kit.box("street head", (0.5, 0.25, 0.1), (gx - 1.1, gy, 4.5), M["black"])
    kit.box("street glass", (0.4, 0.2, 0.03), (gx - 1.1, gy, 4.44), kit.emit("#ffc479", 5.0, name="streetlamp"))


# ------------------------------------------------------------------------------------------------ the Prompter


def mask_pt(x, z, off=0.0):
    yy = -MASK_B * math.sqrt(max(0.02, 1 - (x / MASK_A) ** 2 - (z / MASK_C) ** 2))
    n = V((x / MASK_A ** 2, yy / MASK_B ** 2, z / MASK_C ** 2)).normalized()
    return V((x, yy, z)) + n * off, n


def feature(kit, name, parent, x, z, off=0.0, spin=0.0):
    """An empty on the mask's surface at (x, z), its +Z out along the surface normal and +Y up the face."""
    p, n = mask_pt(x, z, off)
    e = kit.empty(name, tuple(p), parent)
    q = n.to_track_quat("Z", "Y")
    e.rotation_euler = (q.to_matrix() @ Matrix.Rotation(spin, 3, "Z")).to_euler()
    return e


def build_prompter(kit, ctx, M):
    root = kit.empty("prompter", (0, 0, 0))
    root.scale = (U, U, U)
    body = kit.empty("prompter body", (0, 0, 0), root)
    # legs and shoes, hidden under the coat but there
    for sx in (-1, 1):
        kit.box(f"pr leg {sx}", (0.95, 0.95, 2.0), (sx * 0.5, 0, 1.0), M["soot"], body, bevel=0.06)
        kit.box(f"pr shoe {sx}", (1.0, 1.25, 0.3), (sx * 0.5, -0.12, 0.15), M["black"], body, bevel=0.08)
    # the long soot-black coat to the shins, with a column of small dull gilt buttons
    kit.box("pr skirt", (2.2, 1.28, 3.0), (0, 0, 2.1), M["soot"], body, bevel=0.14)
    kit.box("pr torso", (2.0, 1.0, 2.0), (0, 0, 3.0), M["soot"], body, bevel=0.1)
    for k in range(7):
        kit.box(f"pr button {k}", (0.13, 0.06, 0.13), (0, -0.66, 3.55 - 0.42 * k), M["gilt_dull"], body, bevel=0.025)
    kit.box("pr collar", (1.5, 1.05, 0.25), (0, 0, 4.0), M["soot"], body, bevel=0.07)
    for sx in (-1, 1):
        a = kit.empty(f"pr arm {sx}", (sx * 1.5, 0, 3.75), body)
        kit.box(f"pr sleeve {sx}", (0.98, 1.0, 1.7), (0, 0, -0.6), M["soot"], a, bevel=0.08)
        kit.box(f"pr hand {sx}", (0.9, 0.9, 0.55), (0, 0, -1.72), M["black"], a, bevel=0.1)
        a.rotation_euler = (0, math.radians(-5 * sx), 0)
    neck = kit.empty("pr neck", (0, 0.02, 4.1), body)
    kit.box("pr neck box", (0.8, 0.8, 0.5), (0, 0, 0.15), M["black"], neck, bevel=0.08)
    # the mask: a smooth oval, worn gilt, a bronze crack line. Two shells, the same oval: the eye holes are cut in
    # both, and the mouth hole only in the second (shown from L50 on), so the mouth is a real hole in the gilt
    mk = kit.empty("pr mask", (0, 0, 2.35), neck)
    shells = []
    for tag in ("shut", "open"):
        ell = kit.sphere(f"pr mask shell {tag}", 1.0, (0, 0, 0), M["mask"], mk, seg=40)
        ell.scale = (MASK_A, MASK_B, MASK_C)
        shells.append(ell)
    cutters = {"shut": [], "open": []}
    for sx in (-1, 1):                      # the eye holes, each with a spark deep inside
        f = feature(kit, f"pr eye {sx}", mk, sx * 0.68, 0.22)
        g = kit.empty(f"pr eye g {sx}", (0, 0, 0), f)
        g.scale = (1.0, 1.12, 1.0)
        for tag in cutters:
            cu = kit.cyl(f"pr cut eye {tag} {sx}", 0.23, 1.1, (0, 0, 0.1), M["pit"], g, n=28)
            cutters[tag].append(cu)
        kit.cyl(f"pr eye floor {sx}", 0.25, 0.02, (0, 0, -0.4), M["pit"], g, n=24)
        kit.sphere(f"pr spark {sx}", 0.055, (0.0, 0.0, -0.3), M["spark"], g, seg=10)
    for sx in (-1, 1):                      # carved brows, arched, the inner ends low
        f = feature(kit, f"pr brow {sx}", mk, sx * 0.72, 0.78, 0.0, spin=sx * 0.12)
        kit.box(f"pr brow bar {sx}", (1.05, 0.08, 0.16), (0, 0, 0.03), M["mask"], f, bevel=0.035)
    f = feature(kit, "pr nose", mk, 0.0, -0.15, 0.0)
    kit.box("pr nose bar", (0.17, 0.95, 0.34), (0, 0, 0.04), M["mask"], f, bevel=0.07)
    # the carved closed mouth: a thin, faintly smiling groove
    fm = kit.empty("pr mouth shut", (0, 0, 0), mk)
    for i in range(15):
        x = -0.7 + 0.1 * i
        zz = -1.3 + 0.07 * (x / 0.7) ** 2
        p, n = mask_pt(x, zz, 0.0)
        e = kit.empty(f"pr smile {i}", tuple(p), fm)
        q = n.to_track_quat("Z", "Y")
        e.rotation_euler = (q.to_matrix() @ Matrix.Rotation(math.atan(0.286 * x), 3, "Z")).to_euler()
        kit.box(f"pr smile seg {i}", (0.16, 0.045, 0.07), (0, 0, 0.0), M["pit"], e, bevel=0.012)
    ctx["mouth_shut"] = fm
    # ...and open (from L50): a tall dark oval, a hole in the gilt that goes back into black
    f = feature(kit, "pr mouth open", mk, 0.0, -1.3)
    g = kit.empty("pr mouth g", (0, 0, 0), f)
    g.scale = (0.62, 1.0, 1.0)
    cu = kit.cyl("pr cut mouth", 0.6, 1.8, (0, 0, 0.0), M["pit"], g, n=32)
    cutters["open"].append(cu)
    kit.cyl("pr mouth floor", 0.62, 0.02, (0, 0, -0.9), M["pit"], g, n=24)
    ctx["mouth_open"] = f
    # the crack in the gilt, bronze, two runs
    def crack(prefix, pts):
        for i, ((x1, z1), (x2, z2)) in enumerate(zip(pts, pts[1:])):
            L = math.hypot(x2 - x1, z2 - z1)
            fe = feature(kit, f"{prefix}{i}", mk, (x1 + x2) / 2, (z1 + z2) / 2, 0.0, spin=-math.atan2(x2 - x1, z2 - z1))
            kit.box(f"{prefix}bar{i}", (0.1, L, 0.07), (0, 0, 0.0), M["bronze"], fe)
    crack("pr crack a ", [(0.5, 2.0), (0.15, 1.5), (0.4, 1.05), (0.25, 0.6)])
    crack("pr crack b ", [(-1.2, 0.0), (-0.9, -0.7), (-1.05, -1.35), (-0.75, -1.8)])
    crack("pr crack c ", [(0.95, -0.2), (0.75, -0.55), (0.9, -0.95)])
    # cut the holes (Blender's boolean), keep the result as plain meshes, drop the cutters
    bpy.context.view_layer.update()
    for tag, shell in zip(("shut", "open"), shells):
        for cu in cutters[tag]:
            cu.display_type = "WIRE"
            m = shell.modifiers.new(f"cut {cu.name}", "BOOLEAN")
            m.operation = "DIFFERENCE"
            m.solver = "EXACT"
            m.object = cu
    dg = bpy.context.evaluated_depsgraph_get()
    for shell in shells:
        me = bpy.data.meshes.new_from_object(shell.evaluated_get(dg))
        shell.modifiers.clear()
        shell.data = me
        for p_ in me.polygons:
            p_.use_smooth = True
    for tag in cutters:
        for cu in cutters[tag]:
            bpy.data.objects.remove(cu, do_unlink=True)
    ctx["shell_shut"], ctx["shell_open"] = shells
    objs = [o for o in root.children_recursive if o.type == "MESH"]
    # the key from low in the wings (cool) and the thin warm rim: lit only on the Prompter
    key = lamp(kit, "pk_key", "SPOT", (0, 0, 0.3), 55.0, "#ffd2a0", spot=40, blend=0.7, size=0.1)
    rim = lamp(kit, "pk_rim", "SPOT", (0, 0, 2.5), 260.0, "#ffc070", spot=45, blend=0.5, size=0.06)
    low = lamp(kit, "pk_low", "POINT", (0, 0, 0.2), 160.0, "#8aa0e6", size=0.2)
    ctx["pr"] = {"root": root, "neck": neck, "mask": mk, "objs": objs, "key": key, "rim": rim, "low": low}
    light_only(kit, "pr only", "pk_key", objs)
    light_only(kit, "pr only", "pk_rim", objs)
    light_only(kit, "pr only", "pk_low", objs)


# ------------------------------------------------------------------------------------------------ the light

# per mood: light name -> gain; every light not listed is off. wash is the colour of the stage wash. exp is the exposure.
WASH_NAMES = ("wash_l", "wash_r", "wash_top", "wash_back")
_WARM = {"wash_l": 1.0, "wash_r": 1.0, "wash_top": 1.0, "wash_back": 1.0, "run1": 1.0, "run2": 0.5, "run3": 1.0,
         "ghost": 0.4, "marion_lamp": 1.0, "wing_fill": 1.0}
_COLD = {"wash_l": 0.7, "wash_r": 0.7, "wash_top": 0.7, "wash_back": 0.7, "run1": 1.0, "run2": 0.5, "run3": 1.0,
         "ghost": 0.4, "marion_lamp": 0.8, "wing_fill": 0.9}
MOODS = {
    "ghost": {"gains": {"ghost": 1.0, "ghost_fill": 1.8, "run1": 0.6, "run2": 0.3, "run3": 0.6, "wing_fill": 0.3},
              "wash": "#ffb868", "exp": 1.5},
    "work": {"gains": {"work_l": 1.0, "work_r": 1.0, "work_house": 1.0, "run1": 0.12, "run3": 0.12, "ghost": 0.2},
             "wash": "#ffb868", "exp": 0.0},
    "wing": {"gains": {"run1": 1.0, "run2": 0.6, "run3": 1.0, "ghost": 0.25, "ghost_fill": 0.3, "chalk_lit": 1.0,
                       "wing_fill": 0.8},
             "wash": "#ffb868", "exp": 0.9},
    "warm": {"gains": dict(_WARM), "wash": "#ffb868", "exp": 0.0},
    "dim": {"gains": {"wash_l": 0.07, "wash_r": 0.07, "wash_top": 0.07, "wash_back": 0.07, "run1": 1.2, "run2": 0.5,
                      "run3": 1.2, "ghost": 0.6, "ghost_fill": 0.3, "wing_fill": 0.5},
            "wash": "#ffb868", "exp": 0.5},
    "cold": {"gains": dict(_COLD), "wash": "#a9b9e6", "exp": 0.0},
    "open": {"gains": {"wash_l": 1.0, "wash_r": 1.0, "wash_top": 1.0, "wash_back": 1.0, "run1": 0.8, "run2": 0.4,
                       "run3": 0.8, "ghost": 0.3, "aud": 1.0, "wing_fill": 1.5, "wing_fill2": 2.5},
             "wash": "#ffb868", "exp": 0.0},
    # the flat and the car are far from the stage: the stage keeps its light, so the next stage shot starts where it was
    "flat": {"gains": {**_COLD, "flat_lamp": 1.0, "flat_fill": 1.0}, "wash": "#a9b9e6", "exp": 0.0},
    "car": {"gains": {**_WARM, "car_lamp": 1.0, "car_fill": 1.0}, "wash": "#ffb868", "exp": 0.0},
}


def build_lights(kit, ctx):
    gx, gy = ctx["places"]["ghost"]
    lamp(kit, "ghost", "POINT", (gx, gy, 1.78), 420.0, "#ffd7a0", size=0.08)
    lamp(kit, "ghost_fill", "AREA", (3.3, -1.6, 2.2), 160.0, "#ffd0a0", aim=(2.3, 2.8, 1.0), size=1.6)
    lamp(kit, "wash_l", "SPOT", (-3.5, -4.0, 5.4), 2600.0, "#ffb868", aim=(-0.5, 2.3, 1.0), spot=44, blend=0.5, size=0.3)
    lamp(kit, "wash_r", "SPOT", (3.5, -4.0, 5.4), 2600.0, "#ffb868", aim=(1.0, 2.3, 1.0), spot=44, blend=0.5, size=0.3)
    lamp(kit, "wash_top", "AREA", (0, 2.4, 5.6), 900.0, "#ffb868", aim=(0, 2.4, 0), size=5.0)
    lamp(kit, "wash_back", "AREA", (0, 6.3, 3.2), 500.0, "#ff9a58", aim=(0, 7.2, 1.2), size=3.0)
    lamp(kit, "work_l", "AREA", (-2.5, 2.5, 5.4), 1500.0, "#d9e5ff", aim=(-0.5, 2.5, 0), size=4.0)
    lamp(kit, "work_r", "AREA", (2.5, 2.5, 5.4), 1500.0, "#d9e5ff", aim=(1.0, 2.5, 0), size=4.0)
    lamp(kit, "work_house", "AREA", (0, -4.2, 3.9), 900.0, "#cfdcff", aim=(0, -5.5, 0), size=6.0)
    lamp(kit, "run1", "POINT", (4.6, 3.75, 0.45), 90.0, "#3f66ff", size=0.1)
    lamp(kit, "run2", "POINT", (5.3, 6.3, 0.9), 14.0, "#6d86d8", size=0.1)
    lamp(kit, "run3", "POINT", (4.5, 2.6, 0.4), 70.0, "#3f66ff", size=0.1)
    lamp(kit, "chalk_lit", "SPOT", (5.3, 6.0, 1.5), 7.0, "#7f94dc", aim=(5.3, 7.2, 0.9), spot=45, blend=0.6, size=0.1)
    lamp(kit, "wing_fill", "POINT", (4.3, 2.2, 2.8), 110.0, "#8da0e0", size=0.2)
    lamp(kit, "wing_fill2", "POINT", (4.2, 4.8, 2.4), 90.0, "#8da0e0", size=0.2)
    lamp(kit, "marion_lamp", "SPOT", (0.2, -3.0, 2.0), 600.0, "#ffc890", aim=(-0.58, -4.5, 0.95), spot=40, blend=0.5, size=0.15)
    lamp(kit, "aud", "AREA", (0, -2.0, 4.2), 1300.0, "#6d82b4", aim=(0, -8.0, 0.4), size=8.0)
    fx, fy = ctx["places"]["flat"]
    lamp(kit, "flat_lamp", "POINT", (fx - 0.46, fy + 0.17, 1.1), 28.0, "#ffbe74", size=0.05)
    lamp(kit, "flat_fill", "AREA", (fx + 1.8, fy + 2.2, 1.9), 40.0, "#7a92cc", aim=(fx, fy - 0.8, 1.2), size=1.5)
    cx, cy = ctx["places"]["car"]
    lamp(kit, "car_lamp", "SPOT", (cx + 0.9, cy - 1.7, 3.4), 900.0, "#ffbc66", aim=(cx - 0.3, cy, 0.7), spot=60, blend=0.6, size=0.2)
    lamp(kit, "car_fill", "AREA", (cx - 2.5, cy - 3.5, 2.5), 260.0, "#7f96cf", aim=(cx, cy, 1.0), size=2.5)


def _mood_state(tl, t):
    cs = [c for c in _cues(tl, "mood") if c["t"] <= t + 1e-9]
    cur = cs[-1]["set"] if cs else "ghost"
    prev = cs[-2]["set"] if len(cs) > 1 else cur
    u = 1.0
    if cs and float(cs[-1].get("dur", 0)) > 0:
        u = _ss((t - cs[-1]["t"]) / float(cs[-1]["dur"]))
    return MOODS[prev], MOODS[cur], u


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    ctx = {"story": story, "places": story["places"]}
    M = materials(kit)
    ctx["M"] = M
    build_stage(kit, ctx, M)
    build_house(kit, ctx, M)
    build_chairs(kit, ctx, M)
    build_flat(kit, ctx, M)
    build_car(kit, ctx, M)
    build_prompter(kit, ctx, M)
    build_lights(kit, ctx)
    objs = ctx["pr"]["objs"]
    # the stage wash doesn't reach the Prompter: its front lights are dead
    for nm in WASH_NAMES + ("work_l", "work_r", "work_house", "ghost_fill", "aud", "wing_fill", "wing_fill2"):
        light_except(kit, "pr dark", nm, objs)
    ctx["costumes"] = False
    return ctx


# ------------------------------------------------------------------------------------------------ animate


def attach_costumes(kit, ctx):
    M = ctx["M"]
    R, H = 0.62, 1.2
    wh = bpy.data.objects.get("walt.headg")
    if wh is None:
        return
    ctx["cost"] = {"walt": {}, "me": {}}
    W = ctx["cost"]["walt"]
    W["beard"] = [kit.box("walt beard", (0.95, 0.4, 0.34), (0, -R + 0.02, -0.5), M["white"], wh, bevel=0.1),
                  kit.box("walt mustache", (0.7, 0.14, 0.1), (0, -R - 0.02, -0.2), M["white"], wh, bevel=0.04)]
    crown = kit.empty("walt crown", (0, 0, H / 2 + 0.12), wh, rot=(0, 0.16, 0.05))
    kit.cyl("crown ring", R + 0.05, 0.22, (0, 0, 0), M["tin"], crown, n=24)
    for k in range(7):
        a = 2 * math.pi * k / 7
        kit.box(f"crown spike {k}", (0.14, 0.08, 0.2), ((R + 0.02) * math.cos(a), (R + 0.02) * math.sin(a), 0.22), M["tin"], crown,
                rot=(0, 0, a))
    W["crown"] = [crown]
    tor = bpy.data.objects["walt.torso"]
    hips = bpy.data.objects["walt.hips"]
    robe = [kit.box("walt robe top", (2.18, 1.14, 2.14), (0, 0, 1.0), M["robe"], tor, bevel=0.12),
            kit.box("walt robe trim", (0.34, 1.16, 2.16), (0, -0.01, 1.0), M["robe_trim"], tor, bevel=0.05),
            kit.box("walt robe skirt", (2.3, 1.2, 1.9), (0, 0, -0.95), M["robe"], tor, bevel=0.14),
            kit.box("walt robe hem", (2.34, 1.24, 0.2), (0, 0, -1.8), M["robe_trim"], tor, bevel=0.05),
            kit.box("walt robe sash", (2.2, 1.18, 0.22), (0, 0, 0.1), M["robe_trim"], tor, bevel=0.05)]
    for sx in (-1, 1):
        arm = bpy.data.objects[f"walt.arm{sx}"]
        robe.append(kit.box(f"walt robe sleeve {sx}", (1.04, 1.06, 1.1), (0, 0, -0.3), M["robe"], arm, bevel=0.1))
    W["robe"] = robe
    mt = bpy.data.objects["me.torso"]
    C = ctx["cost"]["me"]
    C["cloak"] = [kit.box("me cloak back", (2.5, 0.34, 3.6), (0, 0.66, 0.2), M["cloak"], mt, bevel=0.1),
                  kit.box("me cloak cape", (2.4, 1.3, 0.7), (0, 0, 1.78), M["cloak"], mt, bevel=0.14),
                  kit.box("me cloak sideL", (0.3, 1.3, 2.4), (-1.05, 0.0, 0.85), M["cloak"], mt, bevel=0.08),
                  kit.box("me cloak sideR", (0.3, 1.3, 2.4), (1.05, 0.0, 0.85), M["cloak"], mt, bevel=0.08)]
    # Marion's glasses: the lenses out (they render black), full frames in
    for ob in list(bpy.data.objects):
        if ob.name in ("marion.gl-1", "marion.gl1", "marion.glf-1", "marion.glf1", "marion.glb"):
            ob.hide_render = True
    mh = bpy.data.objects.get("marion.headg")
    if mh is not None:
        for sx in (-1, 1):
            for nm, size, loc in (("t", (0.5, 0.03, 0.035), (sx * 0.24, -R - 0.05, 0.15)),
                                  ("b", (0.5, 0.03, 0.035), (sx * 0.24, -R - 0.05, -0.19)),
                                  ("s0", (0.035, 0.03, 0.36), (sx * 0.24 - 0.23, -R - 0.05, -0.02)),
                                  ("s1", (0.035, 0.03, 0.36), (sx * 0.24 + 0.23, -R - 0.05, -0.02))):
                kit.box(f"marion frame {nm}{sx}", size, loc, M["tin"], mh)
    # Marion's flask, in her raised hand
    mar = bpy.data.objects.get("marion.arm1")
    if mar is not None:
        fl = kit.cyl("marion flask", 0.26, 0.9, (0, -0.1, -1.9), M["steel"], mar, rot=(0, math.pi / 2, 0), n=14)
        ctx["flask"] = fl
    # the pr-only lights must not touch the cast: the wash exclusion covers the Prompter alone
    ctx["costumes"] = True


def animate(kit, story, tl, t, ctx):
    if not ctx.get("costumes") and bpy.data.objects.get("walt.headg") is not None:
        attach_costumes(kit, ctx)
    A = tl.get("acting", {})
    # sitting: both legs straight out in front, on the pose's z
    for who, keys in A.items():
        if _switch(keys, "sit", t, False):
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (math.radians(-90), 0, 0)
    # costumes follow the cues, and are hidden when their wearer is
    for who, parts in ctx.get("cost", {}).items():
        c = _last([c for c in _cues(tl, "costume") if c.get("who") == who], t) or {}
        root = bpy.data.objects.get(who)
        shown = root is not None and not root.hide_render
        for name, objs in parts.items():
            on = bool(c.get(name, False)) and shown
            for o in objs:
                _show(o, on)
    if ctx.get("flask") is not None:
        _show(ctx["flask"], not bpy.data.objects["marion"].hide_render)
    # chairs and audience
    cc = _last(_cues(tl, "chairs"), t)
    for ch in ctx["chairs"]:
        _show(ch, bool(cc and cc.get("on")))
    ac = _last(_cues(tl, "audience"), t)
    for o in ctx["aud"]:
        o.hide_render = not bool(ac and ac.get("on"))
    # the Prompter
    over = {}
    pr = ctx["pr"]
    c = _last(_cues(tl, "prompter"), t)
    hidden = c is None or c.get("hidden", False)
    _show(pr["root"], not hidden)
    over["pk_key"] = over["pk_rim"] = over["pk_low"] = 0.0
    if not hidden:
        x, y = c["pos"]
        pr["root"].location = (x, y, 0)
        pr["root"].rotation_euler = (0, 0, math.radians(c.get("yaw", 0)))
        pr["neck"].rotation_euler = (0, 0, math.radians(c.get("head", 0)))
        _show(ctx["mouth_shut"], not c.get("mouth", 0))
        _show(ctx["shell_shut"], not c.get("mouth", 0))
        _show(ctx["mouth_open"], bool(c.get("mouth", 0)))
        _show(ctx["shell_open"], bool(c.get("mouth", 0)))
        bpy.context.view_layer.update()
        mc = pr["mask"].matrix_world.translation
        for name, dflt, gk in (("key", (-1.0, -0.6, 0.15), "key_gain"), ("rim", (-0.5, 0.9, 2.4), "rim_gain")):
            off = c.get(name, dflt)
            ob = pr[name]
            ob.location = (x + off[0], y + off[1], off[2])
            kit.aim(ob, tuple(mc))
            over["pk_" + name] = float(c.get(gk, 1.0))
        pr["low"].location = (x - 0.7, y - 0.9, 0.25)
        over["pk_low"] = float(c.get("key_gain", 1.0))
    # the light: the mood, eased from the one before
    a, b, u = _mood_state(tl, t)
    for name in kit.LIGHTS:
        if name in ("pk_key", "pk_rim", "pk_low"):
            continue
        over[name] = a["gains"].get(name, 0.0) * (1 - u) + b["gains"].get(name, 0.0) * u
    ca, cb = _hex(a["wash"]), _hex(b["wash"])
    wc = tuple(ca[i] + (cb[i] - ca[i]) * u for i in range(3))
    for nm in WASH_NAMES:
        L = kit.LIGHTS[nm]["light"]
        L.color = tuple(kit.srgb(v) for v in wc)
    bpy.context.scene.view_settings.exposure = a["exp"] * (1 - u) + b["exp"] * u
    return over
