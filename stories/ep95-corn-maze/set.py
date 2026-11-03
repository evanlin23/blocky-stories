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


EYE_L, EYE_R = (-6.2, 12.0), (6.6, 11.0)
HEAD = (0.0, -0.5, 14.5, 24.5)


def _wob(th):
    return 1 + 0.05 * math.sin(3 * th + 0.7) + 0.035 * math.sin(5 * th + 2.1) + 0.02 * math.sin(9 * th)


def maze_nodes(seed=95, na=13, nb=21):
    """A perfect maze (recursive backtracker) on a na x nb node grid. Returns the set of open edges."""
    import random
    rnd = random.Random(seed)
    seen, edges, stack = {(0, 0)}, set(), [(0, 0)]
    while stack:
        a, b = stack[-1]
        nb_ = [(a + dx, b + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
               if 0 <= a + dx < na and 0 <= b + dy < nb and (a + dx, b + dy) not in seen]
        if not nb_:
            stack.pop()
            continue
        n = rnd.choice(nb_)
        seen.add(n)
        edges.add(frozenset(((a, b), n)))
        stack.append(n)
    for _ in range(14):     # a few loops so it is not a tree
        a, b = rnd.randrange(na - 1), rnd.randrange(nb - 1)
        edges.add(frozenset(((a, b), rnd.choice(((a + 1, b), (a, b + 1))))))
    return edges


def maze_fn(w=FW, h=FH):
    """Path test of the field-wide maze: 1.5 m corridors between 1.5 m walls (a 6 cell pitch)."""
    edges = maze_nodes()
    nx, ny = int(w / CELL), int(h / CELL)

    def f(x, y):
        i, j = int((x + w / 2) / CELL), int((y + h / 2) / CELL)
        ua, va, a, b = i % 6, j % 6, i // 6, j // 6
        iu, iv = 1 <= ua <= 3, 1 <= va <= 3
        if iu and iv:
            return a < 13 and b < 21
        if iv and not iu:
            l = (i - 4) // 6
            return frozenset(((l, b), (l + 1, b))) in edges
        if iu and not iv:
            l = (j - 4) // 6
            return frozenset(((a, l), (a, l + 1))) in edges
        return False
    return f


def head_outside(x, y):
    cx, cy, rx, ry = HEAD
    th = math.atan2((y - cy) / ry, (x - cx) / rx)
    return math.hypot((x - cx) / rx, (y - cy) / ry) / _wob(th) > 1.0


def outline_band(x, y):
    cx, cy, rx, ry = HEAD
    th = math.atan2((y - cy) / ry, (x - cx) / rx)
    rho = math.hypot((x - cx) / rx, (y - cy) / ry) / _wob(th)
    if abs(rho - 1.0) * rx > 1.0:
        return False
    d = math.degrees(th) % 360
    return not any(lo <= d <= hi for lo, hi in ((20, 36), (98, 116), (158, 171), (222, 335)))


def eye_paths(c, outer, inner, gap_o, gap_i, tilt=0.0, sq=1.0):
    ex, ey = c
    return [arc(ex, ey, outer, gap_o[1], gap_o[0] + 360, 1.9), arc(ex, ey, inner, gap_i[1], gap_i[0] + 360, 1.6),
            seg(ex + outer * math.cos(math.radians(200)), ey + outer * math.sin(math.radians(200)),
                ex + inner * math.cos(math.radians(200)), ey + inner * math.sin(math.radians(200)), 1.0),
            seg(ex + inner * math.cos(math.radians(40 + tilt)), ey + inner * math.sin(math.radians(40 + tilt)), ex, ey, 1.0),
            disc(ex, ey, 1.05)]


def face_fn():
    mz = maze_fn()
    feats = []
    feats += eye_paths(EYE_L, 4.3, 2.3, (95, 130), (290, 325))            # left eye: round, pupil room for June
    ex, ey = EYE_R                                                       # right eye: smaller, lower, a different maze
    feats += [arc(ex, ey, 4.0, 110, 60 + 360, 1.9), arc(ex + 0.4, ey - 0.3, 2.0, 220, 130 + 360, 1.5),
              seg(ex + 4.0, ey - 1.0, ex + 4.0, ey - 3.2, 1.2), seg(ex - 3.5, ey + 1.9, ex - 3.5, ey + 3.6, 1.0),
              seg(ex + 2.0, ey - 0.1, ex + 0.4, ey - 0.3, 1.0), disc(ex + 0.9, ey + 0.4, 0.8)]
    pts = [(-10.8, -12.8), (-9.6, -15.8), (-7.0, -18.2), (-3.4, -19.6), (0.6, -20.0), (4.4, -19.2), (7.8, -16.8),
           (10.0, -14.0), (10.9, -11.6)]
    feats += [poly(pts, 2.7)]
    for (sx, sy, ex2, ey2) in ((-9.0, -15.2, -9.0, -12.0), (-3.4, -19.6, -3.4, -22.6), (4.4, -19.2, 4.8, -16.2),
                               (7.8, -16.8, 10.6, -17.2), (-5.4, -18.6, -6.6, -21.6), (0.6, -20.0, 0.6, -22.8)):
        feats.append(seg(sx, sy, ex2, ey2, 1.1))
    feats += [seg(-2.0, 3.0, 1.0, 3.0, 1.1), seg(1.0, 3.0, 1.0, -1.2, 1.1), seg(1.0, -1.2, 3.4, -1.2, 1.1),   # a nose-like branch
              seg(-11.0, -3.0, -8.0, -3.0, 1.1), seg(-8.0, -3.0, -8.0, -7.2, 1.1), seg(9.0, 2.0, 6.0, 2.0, 1.1)]
    cx, cy, rx, ry = HEAD
    for ang, ln in ((60, 2.8), (205, 2.4), (285, 3.2), (130, 2.0)):       # dead-end stubs from the outline inward
        th = math.radians(ang)
        p0 = (cx + rx * _wob(th) * math.cos(th), cy + ry * _wob(th) * math.sin(th))
        feats.append(seg(p0[0], p0[1], p0[0] - ln * math.cos(th), p0[1] - ln * math.sin(th) * 1.0, 1.1))
    # inside the head everything is corn but the features; outside is the maze
    return lambda x, y: (head_outside(x, y) and mz(x, y)) or outline_band(x, y) or any(f(x, y) for f in feats)


def layout_shapes(name):
    if name == "face":     # the face is a maze: see face_fn
        return [face_fn()]
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


def build_corn(kit, name, origin, mats, lean=(0.0, 0.0), w=FW, h=FH, hmax=2.0, leaf=1.0, stalk=1.0, nbl=4):
    """Reusable corn: on every wall cell a stalk bundle, a tassel and five long leaf blades arcing out and down.
    Returns (bodies, leaves+tassels) objects; ~25 faces a cell."""
    shapes = layout_shapes(name)
    ox, oy = origin
    nx, ny = int(w / CELL), int(h / CELL)
    bv, bf, lv, lf, tv, tf = [], [], [], [], [], []

    def P(cx, cy, x, y, z):
        return (cx + x + lean[0] * z / 2.5, cy + y + lean[1] * z / 2.5, z)

    for i in range(nx):
        for j in range(ny):
            x, y = -w / 2 + (i + 0.5) * CELL, -h / 2 + (j + 0.5) * CELL
            if any(s(x, y) for s in shapes):
                continue
            cx, cy = ox + x, oy + y
            hh = hmax + 0.4 * (h01(i, j, 1) - 0.5) * 2
            hw = (0.15 + 0.03 * h01(i, j, 2)) * stalk
            jx, jy = (h01(i, j, 3) - 0.5) * 0.12, (h01(i, j, 4) - 0.5) * 0.12
            for (vs, fs, z0, z1, a0, a1) in ((bv, bf, 0.0, hh, hw, hw * 0.8), (tv, tf, hh - 0.05, hh + 0.16, hw * 0.9, 0.05)):
                k = len(vs)
                for (zz, aa) in ((z0, a0), (z1, a1)):
                    for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                        vs.append(P(cx, cy, jx + sx * aa, jy + sy * aa, zz))
                fs.extend([tuple(k + q for q in f) for f in BOX_FACES])
            for b in range(nbl):    # leaf blades: a bent strip from the stalk, out and down
                ang = (b / nbl + 0.15 * h01(i, j, 10 + b)) * 2 * math.pi + h01(i, j, 5) * 6.28
                z0 = hh * (0.35 + 0.5 * b / nbl + 0.05 * h01(i, j, 20 + b))
                ca, sa = math.cos(ang), math.sin(ang)
                nxv, nyv = -sa, ca
                prof = ((0.0, 0.0, 0.0), (0.22, 0.14, 0.10), (0.42, 0.18, 0.02), (0.55, 0.05, 0.0))   # out, up, half-width
                prof = ((0.05, 0.0, 0.09), (0.26, 0.12, 0.13), (0.46, 0.1, 0.11), (0.62, -0.08, 0.03))
                k = len(lv)
                for (o, u, wd) in prof:
                    for sgn in (-1, 1):
                        lv.append(P(cx, cy, jx + ca * o * leaf + nxv * wd * leaf * sgn, jy + sa * o * leaf + nyv * wd * leaf * sgn, z0 + u * leaf))
                for q in range(len(prof) - 1):
                    lf.append((k + 2 * q, k + 2 * q + 1, k + 2 * q + 3, k + 2 * q + 2))
    body = kit.mesh_obj(f"corn.{name}", bv, bf, mats["corn"], smooth=False)
    tass = kit.mesh_obj(f"corn.{name}.leaf", lv, lf, mats["leaf"], smooth=False)
    top = kit.mesh_obj(f"corn.{name}.top", tv, tf, mats["tassel"], smooth=False)
    return body, tass, top


# ------------------------------------------------------------------------------------------------ the set
def materials(kit):
    return {
        "corn": kit.plastic("#d2ae3c", 0.85, "corn body", spec=0.1),
        "leaf": kit.plastic("#e6c552", 0.8, "corn leaf", spec=0.12),
        "tassel": kit.plastic("#d9b645", 0.8, "corn tassel", spec=0.1),
        "straw": kit.plastic("#e8d39a", 0.95, "straw", spec=0.05),
        "grass": kit.plastic("#27443f", 0.95, "night grass", spec=0.05),
        "iron": kit.plastic("#2b2b30", 0.5, "iron", spec=0.4),
        "pole": kit.plastic("#7a5230", 0.8, "pole", spec=0.1),
        "flame": kit.emit("#ff7f10", 1.0, "flame"),
        "flamecore": kit.emit("#ffb23a", 1.3, "flame core"),
        "glass": kit.emit("#c9792a", 0.35, "lantern glass"),
        "quilt1": kit.plastic("#d8443a", 0.9, "quilt red", spec=0.05),
        "quilt2": kit.plastic("#f2c94c", 0.9, "quilt gold", spec=0.05),
        "quilt3": kit.plastic("#3d6ea6", 0.9, "quilt blue", spec=0.05),
        "torch": kit.emit("#ffd8a0", 1.4, "torch"),
        "stroke": kit.emit("#f2c94c", 1.0, "stroke"),
        "plate": kit.plastic("#14121c", 0.9, "icon plate", spec=0.05),
        "i_pole": kit.plastic("#c99a62", 0.8, "icon pole", spec=0.05),
        "i_iron": kit.plastic("#9a98a6", 0.6, "icon iron", spec=0.1),
        "i_glass_lit": kit.emit("#ff9a2a", 1.6, "icon glass lit"),
        "i_flame": kit.emit("#fff2a8", 1.8, "icon flame"),
        "i_glass_dark": kit.plastic("#1c1a24", 0.9, "icon glass dark", spec=0.05),
    }


def build_lantern(kit, M, ox, oy):
    kit.box("pole", (0.2, 0.2, 2.5), (ox, oy, 1.25), M["pole"], bevel=0.02)
    for k in range(2):        # the lore tally: two strokes on the pole, proud of its face
        kit.box(f"stroke{k}", (0.03, 0.03, 0.34), (ox - 0.1 - 0.015, oy - 0.04 + k * 0.08, 1.35), M["stroke"])
    z = 2.55
    kit.box("lant.base", (0.42, 0.42, 0.08), (ox, oy, z), M["iron"], bevel=0.015)
    kit.box("lant.glass", (0.34, 0.02, 0.44), (ox, oy + 0.17, z + 0.27), M["glass"])   # the warm back pane; the front is open to see the flame
    # a small amber flame sitting low in the glass, dipping to one side
    kit.cyl("lant.wick", 0.03, 0.06, (ox, oy, z + 0.07), M["iron"], n=6)
    kit.cyl("lant.flame", 0.075, 0.2, (ox + 0.015, oy, z + 0.17), M["flame"], n=8, r2=0.012, rot=(0, 0.08, 0))
    kit.cyl("lant.core", 0.038, 0.1, (ox + 0.008, oy - 0.01, z + 0.13), M["flamecore"], n=8, r2=0.01, rot=(0, 0.08, 0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box("lant.bar", (0.04, 0.04, 0.46), (ox + sx * 0.2, oy + sy * 0.2, z + 0.27), M["iron"])
    kit.box("lant.cap", (0.5, 0.5, 0.07), (ox, oy, z + 0.53), M["iron"], bevel=0.015)
    kit.cyl("lant.roof", 0.3, 0.2, (ox, oy, z + 0.67), M["iron"], n=4, r2=0.05, rot=(0, 0, math.pi / 4))
    kit.box("lant.ring", (0.05, 0.3, 0.05), (ox, oy, z + 0.84), M["iron"])
    kit.light("lant.light", "POINT", (ox, oy - 0.9, z + 0.9), 60, "#ffb347", size=0.15)


def build_marker(kit, M, ctx):
    """Twelve lantern-on-a-pole icons, 4 x 3, about 27% of the frame width, parented to the camera at its top-left.
    Lit: amber glass and a bright flame. Out: dark glass, no flame (the iron and pole stay readable)."""
    cam = kit.OBJ["cam"]
    root = kit.empty("marker", (0, 0, 0), parent=cam)
    ctx["icons"] = []
    d = 1.6
    px, py = 0.034, -0.054
    x0, y0 = -0.274 + px / 2, 0.488 - 0.027
    kit.box("marker.plate", (px * 4, -py * 3, 0.004), (-0.274 + px * 2, 0.488 + py * 1.5, -d - 0.02), M["plate"], parent=root)
    for n in range(12):
        r, c = divmod(n, 4)
        e = kit.empty(f"icon{n}", (x0 + c * px, y0 + r * py, -d), parent=root)
        e.scale = (0.38, 0.38, 0.38)
        kit.box(f"icon{n}.pole", (0.02, 0.05, 0.01), (0, -0.03, 0.0), M["i_pole"], parent=e)
        kit.box(f"icon{n}.base", (0.07, 0.012, 0.012), (0, -0.004, 0.002), M["i_iron"], parent=e)
        gl = kit.box(f"icon{n}.glass", (0.056, 0.056, 0.012), (0, 0.032, 0.002), M["i_glass_lit"], parent=e)
        gd = kit.box(f"icon{n}.glass.d", (0.056, 0.056, 0.012), (0, 0.032, 0.002), M["i_glass_dark"], parent=e)
        fl = kit.cyl(f"icon{n}.flame", 0.014, 0.04, (0.002, 0.026, 0.01), M["i_flame"], n=6, r2=0.003, rot=(math.pi / 2, 0, 0), parent=e)
        for sx in (-1, 1):
            kit.box(f"icon{n}.bar", (0.008, 0.06, 0.014), (sx * 0.03, 0.032, 0.004), M["i_iron"], parent=e)
        kit.box(f"icon{n}.cap", (0.07, 0.01, 0.012), (0, 0.064, 0.002), M["i_iron"], parent=e)
        kit.cyl(f"icon{n}.roof", 0.045, 0.014, (0, 0.078, 0.002), M["i_iron"], n=3, rot=(0, 0, math.pi / 2), parent=e)
        ctx["icons"].append({"lit": [gl, fl], "dark": [gd]})


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
            ctx["layouts"][name] = build_corn(kit, name, (ox, 0), M, lean=(0.0, -0.5), leaf=1.25, stalk=0.8, nbl=5)
        else:
            kit.plane(f"straw.{name}", (FW, FH), (0, 0, 0.0), M["straw"])
            ctx["layouts"][name] = build_corn(kit, name, (0, 0), M)
        for ob in ctx["layouts"][name]:
            ob.hide_render = True
    build_lantern(kit, M, 200.3, 0.0)
    # June's dot in the middle of the left eye: a small lit quilt, a torch bead and a warm point light
    ex, ey = EYE_L
    for k, (qx, qy, m) in enumerate(((-0.42, -0.3, "quilt1"), (0.42, -0.3, "quilt2"), (-0.42, 0.3, "quilt3"), (0.42, 0.3, "quilt1"))):
        kit.box(f"june.quilt{k}", (0.82, 0.58, 0.06), (ex + qx, ey + qy, 0.07), M[m])
    kit.sphere("june.torch", 0.12, (ex + 0.55, ey - 0.35, 0.18), M["torch"], seg=10)
    kit.light("june.light", "POINT", (ex + 0.4, ey - 0.3, 1.6), 350, "#ffb347", size=0.5)
    kit.light("june.cone", "SPOT", (ex + 0.55, ey - 0.35, 0.3), 150, "#ffcf8a", rot=(math.radians(100), 0, math.radians(35)), size=0.1, spot=60, blend=0.6)
    build_farm(kit, M)
    # the sky lights: the moon (S34) and a low gold sun (S01)
    kit.light("moon", "SUN", (0, 0, 60), 2.7, "#d5e0ff", rot=(math.radians(42), 0, math.radians(-55)))
    kit.light("gold", "SUN", (0, 0, 60), 3.0, "#ffb870", rot=(math.radians(72), 0, math.radians(30)))
    for nm in ("moon", "gold"):
        kit.LIGHTS[nm]["light"].angle = math.radians(18)   # soft shadow edges
    build_marker(kit, M, ctx)
    return ctx


LOOKS = {   # per shot: which lights, the world colour and strength, exposure
    "moon": {"moon": 1.0, "gold": 0.0, "lant.light": 0.0, "june.light": 1.0, "june.cone": 1.0, "world": ("#8aa0d0", 1.5), "exp": 0.15},
    "dusk": {"moon": 0.0, "gold": 1.0, "lant.light": 1.0, "june.light": 0.0, "june.cone": 0.0, "world": ("#7fc8ff", 1.2), "exp": 0.2},
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
    for name, obs in ctx["layouts"].items():
        for ob in obs:
            ob.hide_render = (name != want)
    look = LOOKS[story.get("shot_look", {}).get(shot["id"], "moon")]
    w = bpy.context.scene.world.node_tree.nodes["Background"]
    w.inputs["Color"].default_value = kit.col(look["world"][0])
    w.inputs["Strength"].default_value = look["world"][1]
    bpy.context.scene.view_settings.exposure = look["exp"]
    n = int(cue_val(tl, "lanterns", t, "n", 12))
    for k, parts in enumerate(ctx["icons"]):
        for ob in parts["lit"]:
            ob.hide_render = k >= n
        for ob in parts["dark"]:
            ob.hide_render = k < n
    return {k: v for k, v in look.items() if k not in ("world", "exp")}
