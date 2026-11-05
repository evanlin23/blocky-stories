"""ep122 "face the wall": Grandma Elsie's small white house in winter.

Upstairs (the hall, my lilac spare room, Dad's sky-blue room, Grandma's cream room), the butter kitchen, the snowy front
and drive, the stair, and a row of three beds are all built once, far apart, and lit per shot (meta.json, written by the
generator, names each shot's look and what to hide). Nothing in the film blinks, pulses or flickers: every light is
steady. The only light changes are the two slow dawn fades (cue "dawn", 1.5 s). The rule meter is a cream tag on the
camera, top-left: a wall-and-bed glyph and my nights facing the wall, then two more small glyphs from L56 and L66.
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {}
try:
    META = json.loads((HERE / "meta.json").read_text())
except Exception:   # noqa: BLE001 - the stand-in lint may run before the generator has
    META = {}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def hx(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def grp(name, ob):
    W.setdefault("g", {}).setdefault(name, []).append(ob)
    return ob


def sample(name, tl, t, defaults):
    """The state of cue track `name` at t: numeric fields eased over a cue's own "dur"."""
    cues = [c for c in tl["cues"] if c["name"] == name]
    cur, prev = dict(defaults), dict(defaults)
    for c in cues:
        if c["t"] > t:
            break
        prev = dict(cur)
        cur.update({k: v for k, v in c.items() if k in defaults})
        dur = c.get("dur", 0.0)
        if dur > 0 and t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            return {k: (prev[k] + (cur[k] - prev[k]) * u if isinstance(cur[k], (int, float)) else cur[k]) for k in cur}
    return cur


# ---------------------------------------------------------------------------------------------- walls and doors
def wall(kit, name, group, p0, p1, thick, h, mat, holes=(), z0=0.0):
    """A wall along x (p0[1] == p1[1]) or along y, as boxes round its openings. holes: (centre, width, zlo, zhi)."""
    alongx = abs(p1[1] - p0[1]) < 1e-6
    a0, a1 = (p0[0], p1[0]) if alongx else (p0[1], p1[1])
    if a0 > a1:
        a0, a1 = a1, a0
    fixed = p0[1] if alongx else p0[0]
    cuts = sorted(holes, key=lambda hh: hh[0])

    def put(lo, hi, zlo, zhi, tag):
        if hi - lo < 1e-3 or zhi - zlo < 1e-3:
            return
        c = (lo + hi) / 2
        ctr = (c, fixed, (zlo + zhi) / 2) if alongx else (fixed, c, (zlo + zhi) / 2)
        size = (hi - lo, thick, zhi - zlo) if alongx else (thick, hi - lo, zhi - zlo)
        grp(group, kit.box(f"{name}.{tag}", size, ctr, mat))

    cur = a0
    for i, (c, w, zl, zh) in enumerate(cuts):
        put(cur, c - w / 2, z0, h, f"s{i}")
        put(c - w / 2, c + w / 2, z0, zl, f"u{i}") if zl > z0 else None
        put(c - w / 2, c + w / 2, zh, h, f"o{i}")
        cur = c + w / 2
    put(cur, a1, z0, h, "end")


def door(kit, name, group, hinge, ang, mat, width=0.88, hgt=2.02, thick=0.045, knob=None):
    """A door panel hinged at `hinge` (x, y), extending +y from it when closed (a door in a wall along y) turned by ang
    degrees about z. Returns the hinge empty."""
    root = kit.empty(name, (hinge[0], hinge[1], 0), rot=(0, 0, ang * D2R))
    grp(group, root)
    ob = kit.box(f"{name}.panel", (thick, width, hgt), (0, width / 2, hgt / 2), mat, root, bevel=0.01)
    if knob:
        kit.sphere(f"{name}.knob", 0.035, (thick, width - 0.1, 1.0), knob, root, seg=8)
    return root


# ---------------------------------------------------------------------------------------------- small makers
def soft(kit, name, mat, xs, ys, fn, loc=(0, 0, 0)):
    """A smooth sheet over (x, y) whose height is fn(x, y), with sides to z = 0 dropped at the edge (a quilt, a pillow)."""
    nx, ny = len(xs), len(ys)
    verts = [(x, y, fn(x, y)) for y in ys for x in xs]
    faces = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            faces.append((a, a + 1, a + nx + 1, a + nx))
    ob = kit.mesh_obj(name, verts, faces, mat, loc=loc, smooth=True)
    return ob


def linspace(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def dent(x, y, cx, cy, depth, sig):
    r2 = ((x - cx) ** 2 + (y - cy) ** 2) / (sig * sig)
    return -depth * math.exp(-r2)


def quilt_top(y):
    """The height of a quilt over a body on my bed along y (the body's axis rises 6 degrees toward the pillow)."""
    return 1.04 + 0.105 * (y - 1.58)


def make_quilt(kit, name, mat, bx, y0, y1, dents=(), tucked=False, mirror=1):
    """A rose quilt over a lying body: flat on top across the middle, draped over the mattress edges."""
    xs = linspace(-0.66, 0.66, 41)
    ys = linspace(y0, y1, 36)

    def fn(x, y):
        ax = abs(x)
        top = quilt_top(y)
        if tucked:
            top = 0.60 + 0.012 * (y - 1.58)
        if ax <= 0.26:
            z = top
        elif ax <= 0.48:
            u = (ax - 0.26) / 0.22
            z = top + (0.60 - top) * ss(u)
        else:
            u = (ax - 0.48) / 0.18
            z = 0.60 + (0.33 - 0.60) * ss(u)
        # the ends taper down to the mattress
        e = min(y - y0, y1 - y) / 0.06
        if e < 1:
            z = 0.55 + (z - 0.55) * ss(max(0.0, e))
        for cx, cy, dp, sg in dents:
            z += dent(x * mirror, y, cx, cy, dp, sg)
        return z

    return soft(kit, name, mat, xs, ys, fn, loc=(bx, 0, 0))


def make_pillow(kit, name, mat, bx, dents=()):
    xs = linspace(-0.3, 0.3, 21)
    ys = linspace(2.78, 3.5, 20)

    def fn(x, y):
        u = (x / 0.3) ** 2
        v = ((y - 3.14) / 0.36) ** 2
        z = 0.52 + 0.06 * max(0.0, 1.0 - (u * 0.7 + v * 0.7) ** 1.3) ** 0.7
        for cx, cy, dp, sg in dents:
            z += dent(x, y, cx, cy, dp, sg) * (1 if z > 0.55 else 0)
        return max(z, 0.52)

    return soft(kit, name, mat, xs, ys, fn, loc=(bx, 0, 0))


def iron_bed(kit, name, group, root, white, mattress_mat, with_head=True):
    """An iron bed in its own frame: the long side along y, head at +y, mattress top at z 0.52, 0.95 wide, 2.0 long.
    Origin at the bed's centre on the floor."""
    kit.box(f"{name}.mattress", (0.95, 2.0, 0.17), (0, 0, 0.435), mattress_mat, root, bevel=0.03)
    kit.box(f"{name}.frame", (1.0, 2.06, 0.05), (0, 0, 0.33), white, root)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"{name}.leg{sx}{sy}", (0.05, 0.05, 0.34), (sx * 0.48, sy * 1.0, 0.17), white, root)
    # the foot: low rail with bars; the head: tall
    for sy, hh in ((-1, 0.78), (1, 1.15)):
        for sx in (-1, 1):
            kit.box(f"{name}.post{sx}{sy}", (0.06, 0.06, hh), (sx * 0.48, sy * 1.02, hh / 2), white, root, bevel=0.01)
        kit.box(f"{name}.rail{sy}", (1.0, 0.045, 0.05), (0, sy * 1.02, hh - 0.04), white, root)
        for k in range(1, 9):
            kit.cyl(f"{name}.bar{sy}{k}", 0.011, hh - 0.4, (-0.48 + k * 0.96 / 9, sy * 1.02, 0.34 + (hh - 0.4) / 2 + 0.02), white, root, n=6)
        kit.box(f"{name}.low{sy}", (1.0, 0.04, 0.04), (0, sy * 1.02, 0.4), white, root)
    kit.box(f"{name}.siderail0", (0.03, 2.0, 0.04), (-0.48, 0, 0.38), white, root)
    kit.box(f"{name}.siderail1", (0.03, 2.0, 0.04), (0.48, 0, 0.38), white, root)


def box_stack(kit, plastic, bx, by):
    """Moving boxes with glyph labels (no text): a rose disc, a green triangle, a blue square."""
    card = plastic("#d6a56a", 0.8, spec=0.05)
    card2 = plastic("#c8955a", 0.8, spec=0.05)
    tape = plastic("#f4e6c4", 0.7, spec=0.05)
    gl = [plastic("#e8869e", 0.6), plastic("#3fa66a", 0.6), plastic("#6f8fe0", 0.6)]
    spots = [(0, 0, 0, 0.62, 0.52, 0.46), (0.66, 0.05, 0, 0.58, 0.5, 0.42), (0.1, -0.02, 0.46, 0.55, 0.48, 0.4),
             (-0.2, 0.62, 0, 0.5, 0.46, 0.5), (0.5, 0.7, 0, 0.5, 0.5, 0.36)]
    for i, (dx, dy, dz, sx, sy, sz) in enumerate(spots):
        c = bx + dx
        d = by + dy
        z = dz + sz / 2
        grp("boxes", kit.box(f"mbox{i}", (sx, sy, sz), (c, d, z), card if i % 2 else card2, bevel=0.015))
        grp("boxes", kit.box(f"mbox{i}.tape", (0.07, sy * 0.98, 0.005), (c, d, dz + sz + 0.001), tape))
        # the glyph label on the face looking at the camera side (+x, toward the hall) 1.5 cm proud
        m = gl[i % 3]
        gx = c + sx / 2 + 0.015
        if i % 3 == 0:
            grp("boxes", kit.cyl(f"mbox{i}.g", 0.09, 0.012, (gx, d, z), m, rot=(0, math.pi / 2, 0), n=14))
        elif i % 3 == 1:
            grp("boxes", kit.box(f"mbox{i}.g", (0.012, 0.16, 0.16), (gx, d, z), m))
        else:
            grp("boxes", kit.box(f"mbox{i}.g", (0.012, 0.18, 0.05), (gx, d, z - 0.04), m))
            grp("boxes", kit.box(f"mbox{i}.g2", (0.012, 0.1, 0.05), (gx, d, z + 0.01), m))


def flowers(kit, plastic, group, face, a0, a1, z0, z1, fixed, step=0.5):
    """Wallpaper flowers: tiny pink crosses with gold hearts on a lilac wall, 1.5 cm proud. face 'x' (wall at x = fixed,
    looking along +-x) or 'y'. sign in face = +1 / -1 for the side the camera sees."""
    pink = plastic("#f29ac0", 0.7)
    gold = plastic("#ffd36b", 0.7)
    ax, sgn = face
    n = 0
    za = z0
    row = 0
    while za <= z1:
        a = a0 + (0.25 if row % 2 else 0.0)
        while a <= a1:
            if ax == "x":
                p = (fixed + sgn * 0.012, a, za)
                grp(group, kit.box(f"fl{group}{n}a", (0.01, 0.1, 0.034), p, pink))
                grp(group, kit.box(f"fl{group}{n}b", (0.01, 0.034, 0.1), p, pink))
                grp(group, kit.box(f"fl{group}{n}c", (0.014, 0.036, 0.036), (p[0] + sgn * 0.004, p[1], p[2]), gold))
            else:
                p = (a, fixed + sgn * 0.012, za)
                grp(group, kit.box(f"fl{group}{n}a", (0.1, 0.01, 0.034), p, pink))
                grp(group, kit.box(f"fl{group}{n}b", (0.034, 0.01, 0.1), p, pink))
                grp(group, kit.box(f"fl{group}{n}c", (0.036, 0.014, 0.036), (p[0], p[1] + sgn * 0.004, p[2]), gold))
            n += 1
            a += step
        za += step * 0.8
        row += 1


# ---------------------------------------------------------------------------------------------- the tag
def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    edge = kit.emit("#3a2f4a", 0.7, "tagedge")
    plate = kit.emit("#f6eed8", 0.9, "tagplate")
    ink = kit.emit("#2b2240", 0.7, "taginkx")
    blue = kit.emit("#4f6fe0", 0.9, "tagblue")
    rose = kit.emit("#e8546e", 0.9, "tagrose")
    gold = kit.emit("#e8a21a", 1.0, "taggoldx")
    cream = kit.emit("#fffaf0", 0.9, "tagcream")
    skin = kit.emit("#8a5a3a", 0.8, "tagskin")

    def b(name, size, loc, mat, group=None):
        ob = kit.box(name, size, loc, mat, root)
        noshadow(ob)
        if group:
            grp(group, ob)
        return ob

    def disc(name, r, loc, mat, group=None):
        ob = kit.cyl(name, r, 0.006, loc, mat, root, n=14)
        noshadow(ob)
        if group:
            grp(group, ob)
        return ob

    # main plate: wall glyph on the left, my count on the right
    b("tag.edge", (1.2, 0.74, 0.006), (0, 0, 0), edge)
    b("tag.plate", (1.14, 0.68, 0.006), (0, 0, 0.03), plate)
    z = 0.06
    # the wall: a thick brick-red block with a mortar line, and a bed beside it, a head on the pillow facing the wall
    b("tag.wall", (0.15, 0.5, 0.006), (-0.43, 0.0, z), rose)
    for k in range(3):
        b(f"tag.wallm{k}", (0.15, 0.025, 0.006), (-0.43, -0.15 + k * 0.15, z + 0.03), cream)
    b("tag.bed", (0.34, 0.15, 0.006), (-0.19, -0.1, z), blue)
    b("tag.bedleg", (0.34, 0.04, 0.006), (-0.19, -0.2, z), ink)
    b("tag.pillow", (0.12, 0.1, 0.006), (-0.3, -0.0, z + 0.03), cream)
    disc("tag.head", 0.06, (-0.285, 0.04, z + 0.06), skin)
    W["digits"] = []
    dw, dh, th = 0.27, 0.5, 0.075
    cx = 0.28
    d = {}
    pos = {"a": (0, dh / 2 - th / 2, dw, th), "g": (0, 0, dw, th), "d": (0, -dh / 2 + th / 2, dw, th),
           "f": (-dw / 2 + th / 2, dh / 4, th, dh / 2), "b": (dw / 2 - th / 2, dh / 4, th, dh / 2),
           "e": (-dw / 2 + th / 2, -dh / 4, th, dh / 2), "c": (dw / 2 - th / 2, -dh / 4, th, dh / 2)}
    for k, (px, py, sw, sh) in pos.items():
        d[k] = b(f"tag.d{k}", (sw, sh, 0.006), (cx + px, py, z), ink)
    W["digits"].append(d)
    # second row: appears at L56 (a bed across a hall: two walls and a bed between) and L66 (a bed behind a door)
    b("tag.row.edge", (1.2, 0.44, 0.006), (0, -0.585, 0), edge, "row")
    b("tag.row.plate", (1.14, 0.38, 0.006), (0, -0.585, 0.03), plate, "row")
    z2 = 0.06
    # cell 2 at x -0.3: two hall walls, a bed between them, my digit 1 at its right
    for sx in (-1, 1):
        b(f"tag.h2w{sx}", (0.05, 0.3, 0.006), (-0.5 + (sx + 1) * 0.12, -0.585, z2), rose, "cell2")
    b("tag.h2bed", (0.14, 0.09, 0.006), (-0.38, -0.62, z2), blue, "cell2")
    b("tag.h2pil", (0.05, 0.07, 0.006), (-0.43, -0.6, z2 + 0.03), cream, "cell2")
    b("tag.h2one", (0.05, 0.22, 0.006), (-0.18, -0.585, z2), ink, "cell2")
    b("tag.h2flag", (0.09, 0.05, 0.006), (-0.215, -0.5, z2), ink, "cell2")
    # cell 3 at x +0.28: a door at the end of a hall with a gold crack, a bed, digit 1
    b("tag.h3door", (0.12, 0.3, 0.006), (0.14, -0.585, z2), ink, "cell3")
    b("tag.h3crack", (0.025, 0.28, 0.006), (0.115, -0.585, z2 + 0.03), gold, "cell3")
    b("tag.h3bed", (0.14, 0.09, 0.006), (0.3, -0.62, z2), blue, "cell3")
    b("tag.h3pil", (0.05, 0.07, 0.006), (0.35, -0.6, z2 + 0.03), cream, "cell3")
    b("tag.h3one", (0.05, 0.22, 0.006), (0.46, -0.585, z2), ink, "cell3")
    b("tag.h3flag", (0.09, 0.05, 0.006), (0.425, -0.5, z2), ink, "cell3")


DIGIT = {0: "abcdef", 1: "bc", 2: "abdeg", 3: "abcdg", 4: "bcfg", 5: "acdfg"}


# ---------------------------------------------------------------------------------------------- upstairs
def build_upstairs(kit):
    plastic = kit.plastic
    white = plastic("#fbf8ff", 0.5, spec=0.3)
    cream = plastic("#f7edd3", 0.85, spec=0.05)
    lilac = plastic("#c9b6e4", 0.9, spec=0.03)
    sky = plastic("#9fd0f5", 0.9, spec=0.03)
    gran_w = plastic("#f6e8c8", 0.9, spec=0.03)
    trim = plastic("#fffaf0", 0.6, spec=0.1)
    floor = kit.planks("#e2b784", "#d6a574", 1.4, "Y")
    mattress_mat = plastic("#f4eef8", 0.9, spec=0.03)
    rose = kit.checker("#e8869e", "#f4a8bb", 5.0, rough=0.9)
    pillow_mat = plastic("#fff6fb", 0.9, spec=0.03)
    H = 2.5
    # ---- floors (one slab each, a little under the bottoms of the walls)
    kit.box("floor.hall", (1.2, 6.6, 0.1), (0, 3.25, -0.05), floor)
    kit.box("floor.sp", (3.62, 3.8, 0.1), (-2.41, 1.9, -0.05), floor)
    kit.box("floor.dd", (3.62, 3.8, 0.1), (2.41, 1.9, -0.05), floor)
    kit.box("floor.gr", (3.62, 3.55, 0.1), (0, 8.28, -0.05), floor)
    kit.box("floor.landing", (1.2, 1.0, 0.1), (0, -0.5, -0.05), floor)
    # ---- my room: west wall, north wall with the moon window, south wall, the hall wall with the door
    wall(kit, "spW", "w_sp_W", (-4.25, 0), (-4.25, 3.8), 0.1, H, lilac)
    wall(kit, "spN", "w_sp_N", (-4.3, 3.85), (-0.5, 3.85), 0.1, H, lilac, [(G.WIN_X, 1.6, 0.95, 2.05)])
    wall(kit, "spS", "w_sp_S", (-4.3, -0.05), (-0.5, -0.05), 0.1, H, lilac)
    wall(kit, "spE", "w_sp_E", (-0.55, 0), (-0.55, 3.8), 0.1, H, lilac, [(G.DOOR_Y, 0.9, 0, 2.05)])
    flowers(kit, plastic, "fl_E", ("x", -1), 0.3, 3.5, 0.45, 2.1, -0.6, 0.5)
    flowers(kit, plastic, "fl_N", ("y", -1), -4.0, -3.4, 0.45, 2.1, 3.8, 0.5)
    flowers(kit, plastic, "fl_N", ("y", -1), -1.8, -0.8, 0.45, 2.1, 3.8, 0.5)
    flowers(kit, plastic, "fl_S", ("y", 1), -4.0, -0.9, 0.45, 2.1, 0.0, 0.5)
    # the moon window: a frame, a pane of sky (colour set per look), the moon, snowy roofs
    wx = G.WIN_X
    for nm, sz, loc in (("fl", (1.7, 0.1, 0.07), (wx, 3.8, 0.96)), ("ft", (1.7, 0.1, 0.07), (wx, 3.8, 2.04)),
                        ("fa", (0.07, 0.1, 1.15), (wx - 0.8, 3.8, 1.5)), ("fb", (0.07, 0.1, 1.15), (wx + 0.8, 3.8, 1.5)),
                        ("fm", (0.05, 0.1, 1.1), (wx, 3.8, 1.5)), ("fh", (1.6, 0.1, 0.05), (wx, 3.8, 1.5))):
        grp("w_sp_N", kit.box(f"win.{nm}", sz, loc, trim))
    kit.box("win.sill", (1.9, 0.22, 0.05), (wx, 3.74, 0.93), trim)
    pane_m = kit.emit("#6f8fe0", 1.0, "winpane")
    W["pane"] = kit.box("win.pane", (3.2, 0.04, 2.2), (wx, 4.25, 1.5), pane_m)
    W["pane"].visible_shadow = False
    moon = kit.cyl("win.moon", 0.3, 0.02, (wx + 0.35, 4.2, 1.75), kit.emit("#fff6d8", 1.4, "moondisc"), rot=(math.pi / 2, 0, 0), n=24)
    moon.visible_shadow = False
    W["moon"] = moon
    snow = plastic("#f4f7ff", 0.9, spec=0.05)
    for k, (rx, rw, rh) in enumerate(((-4.6, 1.8, 0.35), (-3.3, 1.6, 0.5), (-1.7, 1.8, 0.4), (-0.4, 1.6, 0.55), (0.8, 1.4, 0.3))):
        kit.box(f"win.roof{k}", (rw, 0.4, rh), (rx + 0.6, 4.15, 0.95 + rh / 2 - 0.1), snow, bevel=0.03)
    # ---- Dad's room (mirror): east wall, north, south, the hall wall with its door
    wall(kit, "ddE", "w_dd_E", (4.25, 0), (4.25, 3.8), 0.1, H, sky)
    wall(kit, "ddN", "w_dd_N", (0.5, 3.85), (4.3, 3.85), 0.1, H, sky)
    wall(kit, "ddS", "w_dd_S", (0.5, -0.05), (4.3, -0.05), 0.1, H, sky)
    wall(kit, "ddW", "w_dd_W", (0.55, 0), (0.55, 3.8), 0.1, H, sky, [(G.DOOR_Y, 0.9, 0, 2.05)])
    # ---- the hall: the rest of both walls, the north wall with Grandma's door, the cream trim
    hallw = plastic("#f3e6cf", 0.9, spec=0.03)
    wall(kit, "hallW2", "w_hall", (-0.55, 3.8), (-0.55, 6.6), 0.1, H, hallw)
    wall(kit, "hallE2", "w_hall", (0.55, 3.8), (0.55, 6.6), 0.1, H, hallw)
    wall(kit, "hallN", "w_hallN", (-0.6, 6.55), (0.6, 6.55), 0.1, H, hallw, [(0.0, 0.9, 0, 2.05)])
    kit.box("hall.baseW", (0.03, 6.4, 0.12), (-0.52, 3.25, 0.06), trim)
    kit.box("hall.baseE", (0.03, 6.4, 0.12), (0.52, 3.25, 0.06), trim)
    kit.box("hall.dwin", (0.03, 0.8, 1.0), (0.52, 5.5, 1.5), kit.emit("#bcd0ff", 0.5, "hallwin"))
    # ---- Grandma's room: cream
    wall(kit, "grW", "w_gr", (-1.85, 6.55), (-1.85, 10.05), 0.1, H, gran_w)
    wall(kit, "grE", "w_gr", (1.85, 6.55), (1.85, 10.05), 0.1, H, gran_w)
    wall(kit, "grN", "w_gr", (-1.9, 10.05), (1.9, 10.05), 0.1, H, gran_w)
    # ---- doors: mine ajar a hand's width, Dad's half open, Grandma's a crack
    dm = plastic("#fff6e2", 0.6, spec=0.1)
    knob = plastic("#d9a62e", 0.3, spec=0.8)
    door(kit, "door.sp", "door_sp", (-0.55, G.DOOR_Y - 0.44), 10.0, dm, knob=knob)
    d2 = door(kit, "door.dd", "door_dd", (0.55, G.DOOR_Y + 0.44), 0.0, dm, knob=knob)
    d2.rotation_euler = (0, 0, (180 + 40) * D2R)    # hinged on the north edge, swung 40 degrees into his room
    grm = plastic("#fff6e2", 0.6, spec=0.1)
    d3 = kit.empty("door.gr", (-0.44, 6.55, 0), rot=(0, 0, (-90 + 12) * D2R))
    grp("door_gr", d3)
    kit.box("door.gr.panel", (0.045, 0.88, 2.02), (0, 0.44, 1.01), grm, d3, bevel=0.01)
    # ---- my bed, pushed against the west wall, head to the north
    broot = kit.empty("bed.sp", (G.BX, 2.55, 0))
    iron_bed(kit, "bed.sp", "bed_sp", broot, white, mattress_mat)
    # two lilac tally strokes on the headboard's east corner post, 1.5 cm proud
    tally = plastic("#b78be0", 0.5)
    for k in range(2):
        kit.box(f"tally{k}", (0.014, 0.012, 0.12), (G.BX + 0.48 - 0.013 + k * 0.026, 3.57 - 0.03 - 0.006, 0.93), tally, rot=(0, 0.25 * (1 if k else -1), 0))
    W["quilt"] = {
        "flat": make_quilt(kit, "quilt.flat", rose, G.BX, 1.6, 3.0, tucked=True),
        "lump": make_quilt(kit, "quilt.lump", rose, G.BX, 1.6, 2.92),
        "foot": make_quilt(kit, "quilt.foot", rose, G.BX, 1.6, 2.92, dents=[(0.36, 1.95, 0.07, 0.13)]),
        "knee": make_quilt(kit, "quilt.knee", rose, G.BX, 1.6, 2.92, dents=[(0.36, 2.35, 0.07, 0.13)]),
        "shoulder": make_quilt(kit, "quilt.shoulder", rose, G.BX, 1.6, 2.92, dents=[(0.12, 2.65, 0.07, 0.11)]),
        "pat": make_quilt(kit, "quilt.pat", rose, G.BX, 1.6, 2.92, dents=[(0.36, 2.8, 0.05, 0.15)]),
    }
    W["pillow"] = {
        "plain": make_pillow(kit, "pillow.plain", pillow_mat, G.BX),
        "dent": make_pillow(kit, "pillow.dent", pillow_mat, G.BX, dents=[(0.2, 3.28, 0.1, 0.12)]),
    }
    # an empty quilt for the shots with nobody in bed: smooth, folded sharp at the edges
    # ---- the nightstand and the clock (a round wind-up one with hands, never lit)
    nx, ny = -2.95, 3.35
    kit.box("night.top", (0.5, 0.45, 0.04), (nx, ny, 0.56), plastic("#c9946a", 0.6, spec=0.1), bevel=0.01)
    kit.box("night.body", (0.46, 0.41, 0.54), (nx, ny, 0.27), plastic("#d9a47a", 0.7, spec=0.08), bevel=0.02)
    kit.box("night.drawer", (0.38, 0.012, 0.16), (nx, ny - 0.215, 0.38), plastic("#c9946a", 0.6), bevel=0.01)
    cz = 0.58 + 0.1
    brass = plastic("#e6c050", 0.3, spec=0.8)
    face = plastic("#fff6e0", 0.5, spec=0.1)
    ink = plastic("#2b2240", 0.5)
    W["clock"] = kit.empty("clock", (nx, ny, cz))
    kit.cyl("clock.case", 0.105, 0.07, (nx, ny, cz), brass, rot=(0, math.pi / 2, 0), n=24)
    kit.cyl("clock.face", 0.088, 0.012, (nx - 0.037, ny, cz), face, rot=(0, math.pi / 2, 0), n=24)
    for k in range(12):
        a = k * 30 * D2R
        big = k % 3 == 0
        kit.box(f"clock.t{k}", (0.006, 0.012 if not big else 0.02, 0.012 if not big else 0.02),
                (nx - 0.045, ny - 0.07 * math.sin(a), cz + 0.07 * math.cos(a)), ink)
    # the hands show 2:00: the hour hand at 60 degrees (up and south as seen from the west), the minute hand at 12
    kit.box("clock.hour", (0.008, 0.012, 0.052), (nx - 0.05, ny - 0.026 * math.sin(60 * D2R), cz + 0.026 * math.cos(60 * D2R)), ink,
            rot=(60 * D2R, 0, 0))
    kit.box("clock.min", (0.008, 0.01, 0.07), (nx - 0.052, ny, cz + 0.035), ink)
    for sy in (-1, 1):   # the two bells and feet
        kit.sphere(f"clock.bell{sy}", 0.03, (nx, ny + sy * 0.075, cz + 0.1), brass, seg=8)
        kit.box(f"clock.foot{sy}", (0.03, 0.02, 0.03), (nx, ny + sy * 0.07, cz - 0.11), brass)
    # a toy plane on Dad's dresser, a dresser in my room, boxes by the door
    box_stack(kit, plastic, -1.5, 0.55)
    # ---- Dad's room furniture (mirrored): bed, nightstand with a warm lamp, a dresser with the model plane
    droot = kit.empty("bed.dd", (G.DX, 2.55, 0), rot=(0, 0, 0))
    iron_bed(kit, "bed.dd", "bed_dd", droot, white, mattress_mat)
    qd = plastic("#7aa6d6", 0.9, spec=0.03)
    W["dad_quilt"] = make_quilt(kit, "dquilt", kit.checker("#6f9ad6", "#9bc0ea", 5.0, rough=0.9), G.DX, 1.6, 2.92)
    make_pillow(kit, "dpillow", pillow_mat, G.DX)
    kit.box("dnight.body", (0.46, 0.41, 0.54), (3.15, 3.5, 0.27), plastic("#d9a47a", 0.7, spec=0.08), bevel=0.02)
    kit.cyl("dlamp.base", 0.07, 0.04, (3.15, 3.5, 0.58), plastic("#e6c050", 0.4, spec=0.5), n=14)
    kit.cyl("dlamp.stem", 0.018, 0.2, (3.15, 3.5, 0.7), plastic("#e6c050", 0.4, spec=0.5), n=8)
    kit.cyl("dlamp.shade", 0.12, 0.15, (3.15, 3.5, 0.88), kit.emit("#ffcf8a", 1.2, "lampshade"), n=16, r2=0.09)
    kit.box("dresser", (0.5, 1.0, 0.8), (3.9, 0.6, 0.4), plastic("#d9a47a", 0.7, spec=0.08), bevel=0.02)
    pl = kit.empty("modelplane", (3.9, 0.6, 0.84))
    kit.box("mp.body", (0.2, 0.05, 0.05), (3.9, 0.6, 0.86), plastic("#e8546e", 0.4), pl)
    kit.box("mp.wing", (0.06, 0.34, 0.012), (3.9, 0.6, 0.86), plastic("#f6eed8", 0.4))
    kit.box("mp.tail", (0.04, 0.12, 0.012), (3.99, 0.6, 0.88), plastic("#f6eed8", 0.4))
    # ---- Grandma's bed, against the east wall of her room, and the end-of-hall stripe
    groot = kit.empty("bed.gr", (G.GBX + 0.0, G.GY, 0))
    iron_bed(kit, "bed.gr", "bed_gr", groot, white, mattress_mat)
    kit.box("gquilt", (1.0, 1.25, 0.14), (G.GBX, G.GY - 0.15, 0.6), kit.checker("#8fd8bc", "#b6ebd6", 5.0, rough=0.9), bevel=0.05)
    kit.box("gpillow", (0.55, 0.36, 0.1), (G.GBX, G.GY + 0.75, 0.58), pillow_mat, bevel=0.04)
    kit.box("gr.nightstand", (0.42, 0.4, 0.5), (0.35, G.GY + 0.9, 0.25), plastic("#d9a47a", 0.7), bevel=0.02)
    kit.box("gr.glasses", (0.12, 0.04, 0.04), (0.35, G.GY + 0.9, 0.55), plastic("#e6c050", 0.3, spec=0.8))
    kit.box("gr.slipperL", (0.1, 0.22, 0.05), (-0.25, 6.2, 0.025), plastic("#7fd8b8", 0.8), rot=(0, 0, 0.1))
    # ---- the gold stripe: the hall light under my door across the floor, and a band across the hall; steady, 1.2 cm proud
    gold = kit.emit("#f7c04e", 1.2, "stripegold")
    s0 = kit.mesh_obj("stripe.sp", [(-0.56, G.DOOR_Y - 0.1, 0.012), (-0.56, G.DOOR_Y + 0.1, 0.012), (-2.9, G.DOOR_Y + 0.05, 0.012), (-2.9, G.DOOR_Y - 0.05, 0.012)],
                      [(0, 1, 2, 3)], gold)
    s0.visible_shadow = False
    grp("stripe_sp", s0)
    s1 = kit.mesh_obj("stripe.hall", [(-0.5, 2.15, 0.012), (0.5, 2.15, 0.012), (0.5, 3.05, 0.012), (-0.5, 3.05, 0.012)], [(0, 1, 2, 3)], gold)
    s1.visible_shadow = False
    grp("stripe_hall", s1)
    s2 = kit.mesh_obj("stripe.dd", [(0.56, G.DOOR_Y - 0.1, 0.012), (0.56, G.DOOR_Y + 0.1, 0.012), (1.6, G.DOOR_Y + 0.05, 0.012), (1.6, G.DOOR_Y - 0.05, 0.012)],
                      [(0, 1, 2, 3)], gold)
    s2.visible_shadow = False
    grp("stripe_dd", s2)
    # Ezra's green pennant, dropped on the floor beside his bed: a triangle with a gold star (no letters)
    pen = kit.mesh_obj("pennant", [(-2.0, 0.6, 0.014), (-2.0, 1.2, 0.014), (-3.1, 0.9, 0.014)], [(0, 1, 2)], plastic("#2f8f4f", 0.8))
    grp("pennant", pen)
    grp("pennant", kit.cyl("pennant.star", 0.07, 0.012, (-2.35, 0.9, 0.024), plastic("#ffd36b", 0.5), n=5))
    grp("pennant", kit.box("pennant.stick", (1.3, 0.025, 0.025), (-2.5, 0.9, 0.03), plastic("#b07c4a", 0.6)))
    # a hall rug and the mint slippers outside my door (morning)
    kit.box("hall.rug", (0.7, 1.4, 0.015), (0.0, 4.6, 0.008), plastic("#e8869e", 0.9, spec=0.03))
    cream_s = plastic("#f7edd3", 0.8)
    for sx in (-1, 1):   # a pair side by side just outside my door, toes toward the door's wall
        sl = kit.box(f"slip{sx}", (0.11, 0.26, 0.07), (-0.21 + sx * 0.09, 3.4, 0.04), plastic("#7fd8b8", 0.8), bevel=0.03)
        grp("slippers", sl)
        grp("slippers", kit.box(f"slip{sx}.cuff", (0.07, 0.1, 0.02), (-0.21 + sx * 0.09, 3.47, 0.085), cream_s, bevel=0.008))
    # the stairs' top: a gap in the floor, a banister
    kit.box("rail.top", (0.05, 0.05, 0.9), (0.55, -0.2, 0.45), plastic("#b07c4a", 0.6))
    kit.box("rail.bar", (0.05, 1.0, 0.05), (0.55, -0.7, 0.9), plastic("#b07c4a", 0.6))


# ---------------------------------------------------------------------------------------------- the kitchen
def build_kitchen(kit):
    plastic = kit.plastic
    KX = G.KX
    butter = plastic("#ffe08a", 0.9, spec=0.03)
    mint = plastic("#9fe0c8", 0.6, spec=0.2)
    wood = kit.planks("#f0c690", "#e0b27a", 1.3, "X")
    kit.box("k.floor", (6.4, 6.0, 0.1), (KX + 2.6, 2.5, -0.05), wood)
    wall(kit, "k.N", "k_N", (KX - 0.6, 5.05), (KX + 5.8, 5.05), 0.1, 2.6, butter, [(KX + 4.2, 1.3, 0.95, 2.1)])
    wall(kit, "k.W", "k_W", (KX - 0.6, -0.5), (KX - 0.6, 5.05), 0.1, 2.6, butter)
    wall(kit, "k.E", "k_E", (KX + 5.8, -0.5), (KX + 5.8, 5.05), 0.1, 2.6, butter)
    # a frosted window full of morning sun
    grp("k_N", kit.box("k.win", (1.5, 0.05, 1.3), (KX + 4.2, 5.2, 1.5), kit.emit("#fffbe8", 1.0, "kwin")))
    for nm, sz, loc in (("a", (1.62, 0.09, 0.06), (KX + 4.2, 5.0, 0.93)), ("b", (1.62, 0.09, 0.06), (KX + 4.2, 5.0, 2.07)),
                        ("c", (0.06, 0.09, 1.2), (KX + 3.42, 5.0, 1.5)), ("d", (0.06, 0.09, 1.2), (KX + 4.98, 5.0, 1.5)),
                        ("e", (0.05, 0.09, 1.2), (KX + 4.2, 5.0, 1.5))):
        grp("k_N", kit.box(f"k.wf{nm}", sz, loc, plastic("#fffaf0", 0.6), ))
    # the black stove with four rings and a pan, cabinets, a fridge
    stv = plastic("#26262e", 0.35, spec=0.5)
    kit.box("k.stove", (0.9, 0.7, 0.9), (KX + 1.4, 4.65, 0.45), stv, bevel=0.03)
    for i, (dx, dy) in enumerate(((-0.2, -0.12), (0.2, -0.12), (-0.2, 0.15), (0.2, 0.15))):
        kit.cyl(f"k.ring{i}", 0.12, 0.012, (KX + 1.4 + dx, 4.65 + dy, 0.906), plastic("#5a5a66", 0.4, spec=0.4), n=16)
    kit.cyl("k.pan", 0.2, 0.05, (KX + 1.2, 4.5, 0.94), plastic("#44444e", 0.3, spec=0.6), n=18)
    kit.box("k.panh", (0.3, 0.05, 0.03), (KX + 1.2, 4.2, 0.95), plastic("#44444e", 0.4))
    kit.box("k.cab1", (1.6, 0.6, 0.9), (KX + 2.5 + 0.0, 4.72, 0.45), plastic("#fff6e2", 0.6, spec=0.2), bevel=0.02)
    kit.box("k.cab1t", (1.62, 0.62, 0.04), (KX + 2.5, 4.72, 0.92), plastic("#c9946a", 0.6, spec=0.2))
    kit.box("k.cab2", (1.4, 0.6, 0.9), (KX + 0.0, 4.72, 0.45), plastic("#fff6e2", 0.6, spec=0.2), bevel=0.02)
    kit.box("k.cab2t", (1.42, 0.62, 0.04), (KX + 0.0, 4.72, 0.92), plastic("#c9946a", 0.6, spec=0.2))
    kit.box("k.fridge", (0.85, 0.75, 1.9), (KX + 5.3, 4.6, 0.95), plastic("#f4f7ff", 0.35, spec=0.5), bevel=0.04)
    for i in range(2):
        kit.box(f"k.upper{i}", (0.9, 0.35, 0.7), (KX + 0.3 + i * 1.2, 4.88, 1.75), plastic("#ffd36b", 0.6, spec=0.2), bevel=0.02)
    # the mint table, three chairs
    kit.cyl("k.table", 0.95, 0.07, (KX + 3.0, 2.8, 0.74), mint, n=28)
    kit.cyl("k.tleg", 0.1, 0.7, (KX + 3.0, 2.8, 0.36), plastic("#e8f0ea", 0.5), n=10)
    kit.cyl("k.tfoot", 0.4, 0.04, (KX + 3.0, 2.8, 0.02), plastic("#e8f0ea", 0.5), n=20)
    chair = plastic("#ffb27a", 0.6, spec=0.2)
    for i, (cx, cy) in enumerate(((3.0, 3.9), (4.3, 2.6), (1.8, 2.6))):
        kit.box(f"k.chair{i}", (0.44, 0.44, 0.05), (KX + cx, cy, 0.44), chair, bevel=0.01)
        for sx in (-1, 1):
            for sy in (-1, 1):
                kit.box(f"k.chair{i}l{sx}{sy}", (0.04, 0.04, 0.42), (KX + cx + sx * 0.18, cy + sy * 0.18, 0.21), chair)
    # plates, the big pancake, cocoa mugs
    plate = plastic("#fffaf0", 0.4, spec=0.5)
    pancake = plastic("#e0a050", 0.7, spec=0.1)
    for i, (px, py) in enumerate(((3.0, 3.35), (3.0, 2.25), (3.7, 2.8), (2.3, 2.8))):
        grp(f"plate{i}", kit.cyl(f"k.plate{i}", 0.2, 0.015, (KX + px, py, 0.79), plate, n=18))
    for i, (px, py) in enumerate(((3.0, 3.35), (3.0, 2.25))):
        grp(f"cake{i}", kit.cyl(f"k.cake{i}", 0.17, 0.045, (KX + px, py, 0.82), pancake, n=18))
        grp(f"cake{i}", kit.cyl(f"k.butter{i}", 0.05, 0.03, (KX + px, py, 0.865), plastic("#fff0a0", 0.6), n=8))
    kit.cyl("k.mug", 0.06, 0.1, (KX + 3.45, 3.3, 0.84), plastic("#e8546e", 0.4, spec=0.5), n=14)
    kit.cyl("k.cocoa", 0.05, 0.01, (KX + 3.45, 3.3, 0.89), plastic("#6a3e2a", 0.4), n=14)
    kit.box("k.spatula", (0.04, 0.3, 0.012), (KX + 1.4, 4.1, 0.95), plastic("#c9c9d0", 0.3, spec=0.6))


# ---------------------------------------------------------------------------------------------- outside
def build_outside(kit):
    plastic = kit.plastic
    EX = G.EX
    snow = plastic("#dce6f6", 0.9, spec=0.03)
    kit.plane("e.ground", (120, 120), (EX, 6, 0.0), snow)
    kit.box("e.drive", (4.0, 14.0, 0.02), (EX + 3.4, -1.0, 0.01), plastic("#dfe6f2", 0.9, spec=0.03))
    wallc = plastic("#fbfbff", 0.7, spec=0.1)
    # the white clapboard house: a body, a roof, a door with a wreath, windows
    kit.box("e.house", (7.0, 5.0, 3.6), (EX, 8.5, 1.8), wallc, bevel=0.03)
    for i in range(14):   # clapboard lines
        kit.box(f"e.lap{i}", (7.02, 0.02, 0.04), (EX, 5.98, 0.3 + i * 0.25), plastic("#dfe6f2", 0.8))
    kit.box("e.roof1", (7.6, 3.2, 0.3), (EX, 7.2, 4.2), plastic("#8a7fc0", 0.7), rot=(0.55, 0, 0))
    kit.box("e.roof2", (7.6, 3.2, 0.3), (EX, 9.8, 4.2), plastic("#8a7fc0", 0.7), rot=(-0.55, 0, 0))
    kit.box("e.snowroof1", (7.6, 3.0, 0.14), (EX, 7.2, 4.38), snow, rot=(0.55, 0, 0))
    kit.box("e.snowroof2", (7.6, 3.0, 0.14), (EX, 9.8, 4.38), snow, rot=(-0.55, 0, 0))
    kit.box("e.door", (1.0, 0.08, 2.2), (EX, 5.94, 1.1), plastic("#e8546e", 0.5, spec=0.2), bevel=0.02)
    kit.box("e.doorf", (1.2, 0.07, 2.36), (EX, 5.97, 1.18), plastic("#fff6e2", 0.6))
    kit.box("e.step", (1.6, 0.6, 0.18), (EX, 5.65, 0.09), plastic("#dfe6f2", 0.8))
    kit.box("e.doorknob", (0.07, 0.07, 0.07), (EX + 0.35, 5.88, 1.05), plastic("#e6c050", 0.3, spec=0.8))
    # a wreath: a ring of green blocks with a red bow and berries, no letters
    for k in range(16):
        a = k * 22.5 * D2R
        kit.box(f"e.wr{k}", (0.13, 0.05, 0.1), (EX + 0.28 * math.cos(a), 5.88, 1.6 + 0.28 * math.sin(a)),
                plastic("#3fa66a", 0.7), rot=(0, a, 0))
    kit.box("e.bow1", (0.18, 0.04, 0.1), (EX - 0.08, 5.85, 1.3), plastic("#e8383e", 0.5), rot=(0, 0.6, 0))
    kit.box("e.bow2", (0.18, 0.04, 0.1), (EX + 0.08, 5.85, 1.3), plastic("#e8383e", 0.5), rot=(0, -0.6, 0))
    for sx in (-2.3, 2.3):
        kit.box(f"e.win{sx}", (1.1, 0.06, 1.3), (EX + sx, 5.96, 1.9), plastic("#9fd0f5", 0.2, spec=0.8))
        kit.box(f"e.winf{sx}", (1.3, 0.05, 1.5), (EX + sx, 5.95, 1.9), plastic("#fff6e2", 0.6))
        kit.box(f"e.snowsill{sx}", (1.4, 0.18, 0.08), (EX + sx, 5.9, 1.2), snow)
    # a pine or two, snowy
    for i, (tx, ty, th) in enumerate(((-6.5, 7, 5.5), (-9.0, 3, 4.8), (9.5, 9, 6.0), (7.0, 14, 5.0), (-5.0, 13, 5.5))):
        try:
            kit.prop("pinetree_snow_1", (EX + tx, ty, 0), height=th)
        except Exception:   # noqa: BLE001
            kit.cyl(f"e.pine{i}", 0.2, th * 0.3, (EX + tx, ty, th * 0.15), plastic("#7a5230", 0.8), n=8)
            kit.cyl(f"e.pinec{i}", th * 0.2, th * 0.7, (EX + tx, ty, th * 0.55), plastic("#3f8a5a", 0.8), n=12, r2=0.1)
    # the hatchback in the drive: blue body, a cabin, glass-dark windows, boxes up to the windows
    cx, cy = EX + 3.4, 1.0
    car = kit.empty("car", (cx, cy, 0))
    W["car"] = car
    blue = plastic("#4a8ae8", 0.35, spec=0.6)
    seatm = plastic("#3a3f5a", 0.8)
    snow_c = plastic("#f6f9ff", 0.9, spec=0.03)
    kit.box("car.floor", (1.8, 3.8, 0.1), (0, 0, 0.42), blue, car, bevel=0.03)
    kit.box("car.hood", (1.8, 1.0, 0.42), (0, -1.4, 0.7), blue, car, bevel=0.1)
    kit.box("car.rear", (1.8, 0.5, 0.5), (0, 1.65, 0.75), blue, car, bevel=0.1)
    for sx in (-1, 1):
        kit.box(f"car.tub{sx}", (0.08, 2.9, 0.4), (sx * 0.86, 0.25, 0.7), blue, car, bevel=0.03)
        for sy, yy in ((-1, -0.95), (1, 1.15)):
            kit.box(f"car.pil{sx}{sy}", (0.07, 0.09, 0.8), (sx * 0.84, yy, 1.2), blue, car)
    kit.box("car.roof", (1.8, 2.4, 0.09), (0, 0.1, 1.64), blue, car, bevel=0.04)
    kit.box("car.snow", (1.7, 2.3, 0.07), (0, 0.1, 1.72), snow_c, car, bevel=0.03)
    kit.box("car.snowH", (1.7, 0.95, 0.07), (0, -1.4, 0.94), snow_c, car, bevel=0.03)
    kit.box("car.dash", (1.6, 0.3, 0.3), (0, -0.85, 0.78), seatm, car, bevel=0.05)
    for sx in (-1, 1):
        kit.box(f"car.seat{sx}", (0.55, 0.5, 0.12), (sx * 0.42, -0.1, 0.55), seatm, car, bevel=0.04)
        kit.box(f"car.seatb{sx}", (0.55, 0.12, 0.6), (sx * 0.42, 0.18, 0.85), seatm, car, bevel=0.04)
    kit.cyl("car.wheel", 0.17, 0.03, (-0.42, -0.72, 0.96), plastic("#26262e", 0.6), car, rot=(0.9, 0, 0), n=14)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"car.w{sx}{sy}", 0.34, 0.22, (sx * 0.9, sy * 1.2, 0.34), plastic("#26262e", 0.8), car, rot=(0, math.pi / 2, 0), n=14)
    for sx in (-1, 1):
        kit.box(f"car.light{sx}", (0.3, 0.05, 0.15), (sx * 0.62, -1.92, 0.7), kit.emit("#fff6d8", 0.6, "carlight"), car)
    card = plastic("#d6a56a", 0.8, spec=0.05)
    gl = [plastic("#e8869e", 0.6), plastic("#3fa66a", 0.6), plastic("#6f8fe0", 0.6)]
    cargo = [(-0.42, 0.55, 0.85, 0.55, 0.6, 0.62), (0.4, 0.5, 0.85, 0.55, 0.6, 0.62), (-0.42, 1.2, 0.8, 0.55, 0.55, 0.52),
             (0.4, 1.2, 0.8, 0.55, 0.55, 0.52), (-0.42, 0.55, 1.42, 0.5, 0.5, 0.45), (0.4, 0.5, 1.4, 0.5, 0.5, 0.4)]
    for i, (bx, by, bz, sx, sy, sz) in enumerate(cargo):
        grp("cargo", kit.box(f"car.box{i}", (sx, sy, sz), (bx, by, bz), card, car, bevel=0.02))
        grp("cargo", kit.box(f"car.boxg{i}", (0.012, 0.16, 0.16), (bx + (sx / 2 + 0.012) * (1 if bx > 0 else -1), by, bz), gl[i % 3], car))
    grp("duffel", kit.box("duffel", (0.8, 0.34, 0.36), (EX + 0.75, 5.0, 0.18), plastic("#5a6e3a", 0.8), bevel=0.08))
    grp("duffel", kit.box("duffel.strap", (0.9, 0.05, 0.05), (EX + 0.75, 5.0, 0.37), plastic("#2b2b34", 0.7)))
    # footprints in the snow beside the car (Dad's)
    foot = plastic("#c9d8f0", 0.9, spec=0.03)
    for k in range(7):
        grp("prints", kit.box(f"print{k}", (0.14, 0.34, 0.012), (EX + 1.3 + 0.0 + (0.14 if k % 2 else -0.14) * 0, 2.5 + k * 0.62, 0.022 + 0.001 * k), foot, rot=(0, 0, 0.1)))
        grp("prints", kit.box(f"printb{k}", (0.12, 0.3, 0.012), (EX + 1.3 + (0.32), 2.8 + k * 0.62, 0.022), foot))
    # a Christmas-morning scatter of snowflakes: small white blocks hung in the air in front of the house
    sf = kit.emit("#ffffff", 2.0, "flake")
    import random
    rng = random.Random(22)
    for k in range(120):
        grp("flakes", kit.box(f"flake{k}", (0.05, 0.05, 0.05), (EX + rng.uniform(-5, 5), rng.uniform(-0.5, 5.2), rng.uniform(0.2, 4.4)), sf,
                              rot=(rng.random(), rng.random(), rng.random())))


# ---------------------------------------------------------------------------------------------- the stair
def build_stair(kit):
    plastic = kit.plastic
    SX = G.SX
    wallc = plastic("#f3e6cf", 0.9, spec=0.03)
    wood = kit.planks("#e2b784", "#d6a574", 1.4, "Y")
    n = 14
    for i in range(n):
        h = G.STEP_RISE * (i + 1)
        kit.box(f"s.step{i}", (1.2, G.STEP_RUN, h), (SX, G.SY + 0.14 + i * G.STEP_RUN, h / 2), wood, bevel=0.01)
    kit.box("s.floor", (1.2, 1.5, 0.1), (SX, -0.6, -0.05), wood)
    wall(kit, "s.W", "s_W", (SX - 0.65, -1.4), (SX - 0.65, 5.5), 0.1, 3.6, wallc)
    wall(kit, "s.E", "s_E", (SX + 0.65, -1.4), (SX + 0.65, 5.5), 0.1, 3.6, wallc)
    wall(kit, "s.S", "s_S", (SX - 0.7, -1.4), (SX + 0.7, -1.4), 0.1, 3.6, wallc)
    kit.box("s.rail", (0.05, 4.2, 0.05), (SX + 0.55, 2.0, 1.45), plastic("#b07c4a", 0.6))
    kit.box("s.top", (1.2, 1.5, 0.1), (SX, 4.6, G.STEP_RISE * n - 0.05), wood)


# ---------------------------------------------------------------------------------------------- the row of three beds
def build_row(kit):
    plastic = kit.plastic
    RX = G.RX
    white = plastic("#fbf8ff", 0.5, spec=0.3)
    mm = plastic("#f4eef8", 0.9, spec=0.03)
    hall = plastic("#f3e6cf", 0.9, spec=0.03)
    kit.box("r.floor", (7.6, 6.0, 0.1), (RX, 2.0, -0.05), kit.planks("#e2b784", "#d6a574", 1.4, "X"))
    cols = ["#c9b6e4", "#9fd0f5", "#f6e8c8"]
    quilts = ["#e8869e", "#6f9ad6", "#8fd8bc"]
    for i in range(3):
        cx = RX + (i - 1) * 1.55
        # the doorway in a front wall, an alcove behind it, an iron bed against its side wall
        wall(kit, f"r.f{i}", f"r_f{i}", (cx - 0.775, 1.5), (cx + 0.775, 1.5), 0.1, 2.5, hall, [(cx, 0.95, 0, 2.05)])
        kit.box(f"r.back{i}", (1.55, 0.1, 2.5), (cx, 4.0, 1.25), plastic(cols[i], 0.9, spec=0.03))
        kit.box(f"r.side{i}", (0.1, 2.5, 2.5), (cx - 0.775, 2.75, 1.25), plastic(cols[i], 0.9, spec=0.03))
        kit.box(f"r.sidee{i}", (0.1, 2.5, 2.5), (cx + 0.775, 2.75, 1.25), plastic(cols[i], 0.9, spec=0.03))
        broot = kit.empty(f"r.bed{i}", (cx - 0.25, 2.9, 0))
        iron_bed(kit, f"r.bed{i}", "row_bed", broot, white, mm)
        kit.box(f"r.quilt{i}", (0.98, 1.4, 0.1), (cx - 0.25, 2.55, 0.58), plastic(quilts[i], 0.9, spec=0.03), bevel=0.04)
        kit.box(f"r.pillow{i}", (0.5, 0.35, 0.12), (cx - 0.25, 3.65, 0.6), plastic("#fff6fb", 0.9), bevel=0.05)


# ---------------------------------------------------------------------------------------------- the build
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    plastic = kit.plastic
    cam = kit.OBJ["cam"]
    # ------------------------------------------------------------------ lights (gains set in animate)
    def L(name, kind, loc, col, **kw):
        ob = kit.light(name, kind, loc, 1.0, col, **kw)
        return ob

    sun = L("sun", "SUN", (0, 0, 30), "#fff0d6", size=0.06, shadow=True)
    sun.data.angle = 0.1
    W["sun"] = sun
    amb = {}
    amb["p_sp"] = L("p_sp", "POINT", (-2.4, 1.9, 2.3), "#cdbcff", size=0.9, shadow=False)
    amb["p_hall"] = L("p_hall", "POINT", (0.0, 3.0, 2.2), "#ffd9a0", size=0.7, shadow=False)
    amb["p_hallN"] = L("p_hallN", "POINT", (0.0, 5.5, 2.2), "#ffd9a0", size=0.7, shadow=False)
    amb["p_dd"] = L("p_dd", "POINT", (2.4, 1.9, 2.3), "#cdbcff", size=0.9, shadow=False)
    amb["p_gr"] = L("p_gr", "POINT", (0.0, 8.3, 2.2), "#ffe2c0", size=0.9, shadow=False)
    amb["p_k"] = L("p_k", "POINT", (G.KX + 2.6, 2.0, 2.2), "#ffe9b8", size=0.9, shadow=False)
    amb["p_st"] = L("p_st", "POINT", (G.SX, 2.0, 3.0), "#ffe9c8", size=0.9, shadow=False)
    amb["p_row"] = L("p_row", "POINT", (G.RX, 0.5, 2.6), "#fff0d0", size=1.2, shadow=False)
    amb["p_row2"] = L("p_row2", "POINT", (G.RX, 3.0, 2.2), "#fff0d0", size=1.2, shadow=False)
    L("moon", "AREA", (G.WIN_X, 3.55, 1.5), "#8fb0ff", rot=(math.pi / 2, 0, math.pi), size=1.4, shadow=False)
    L("lamp", "POINT", (3.15, 3.5, 0.95), "#ffcf8a", size=0.2, shadow=False)
    rim = L("rim", "SPOT", (-0.9, 3.4, 1.9), "#ffc060", spot=60, blend=0.5, shadow=False, size=0.05)
    kit.aim(rim, (-3.1, 3.15, 1.2))
    for nm in ("sun",) + tuple(amb) + ("moon", "lamp", "rim"):
        kit.LIGHTS[nm]["obj"].visible_camera = False
    # the light that rides on the camera: a soft fill so a face always reads
    cf = kit.light("camfill", "POINT", (0.1, 0.2, 0.0), 1.0, "#bcd0ff", size=0.3, parent=cam, shadow=False)
    cf.visible_camera = False
    cr = kit.light("camrim", "SPOT", (0.0, 0.0, 0.0), 1.0, "#ffc680", spot=80, blend=0.6, size=0.05, parent=cam, shadow=False)
    cr.visible_camera = False
    W["camfill"], W["camrim"] = cf, cr
    # ------------------------------------------------------------------ places
    build_upstairs(kit)
    build_kitchen(kit)
    build_outside(kit)
    build_stair(kit)
    build_row(kit)
    build_tag(kit)
    return {}


# ---------------------------------------------------------------------------------------------- the looks
# world colour/strength and the gain (watts) of each light, per look. N: upstairs at night (moon blue, lilac), D: upstairs by
# day, K: the kitchen, E: outside, SD/SN: the stair by day and at night, B: the row of beds.
LOOKS = {
    "N": dict(world=("#3a47a8", 0.5), sun=0.0, g={"p_sp": 90, "p_hall": 70, "p_hallN": 50, "p_dd": 80, "p_gr": 70, "moon": 150, "rim": 0}, pane="#6f8fe8",
              moonc="#8fb0ff", fill=("#a8bcff", 14), rimcam=0, panes=0.35),
    "DAWN": dict(world=("#8a8fa8", 0.7), sun=0.0, g={"p_sp": 90, "p_hall": 70, "p_hallN": 50, "p_dd": 80, "p_gr": 70, "moon": 150, "rim": 0}, pane="#b5b8c8",
                 moonc="#c8ccd8", fill=("#d0d4e8", 14), rimcam=0, panes=0.35),
    "D": dict(world=("#fff3dc", 0.55), sun=1.3, g={"p_sp": 60, "p_hall": 60, "p_hallN": 50, "p_dd": 60, "p_gr": 50, "moon": 0, "rim": 0}, pane="#e8f2ff",
              moonc="#ffffff", fill=("#fff0dc", 8), rimcam=0, panes=0.6),
    "NDAD": dict(world=("#3a47a8", 0.5), sun=0.0, g={"p_sp": 60, "p_hall": 70, "p_hallN": 50, "p_dd": 90, "p_gr": 70, "moon": 90, "lamp": 40, "rim": 0}, pane="#6f8fe8",
                 moonc="#8fb0ff", fill=("#ffd9a8", 12), rimcam=0, panes=0.35),
    "K": dict(world=("#fff1c8", 0.6), sun=1.5, g={"p_k": 70}, pane="#6f8fe0", moonc="#ffffff", fill=("#fff0dc", 8), rimcam=0, panes=0),
    "E": dict(world=("#bcd6f5", 0.35), sun=0.9, g={}, pane="#6f8fe0", moonc="#ffffff", fill=("#fff0dc", 6), rimcam=0, panes=0),
    "SD": dict(world=("#fff3dc", 0.55), sun=1.2, g={"p_st": 50}, pane="#6f8fe0", moonc="#ffffff", fill=("#fff0dc", 8), rimcam=0, panes=0),
    "SN": dict(world=("#3a47a8", 0.5), sun=0.0, g={"p_st": 60}, pane="#6f8fe0", moonc="#ffffff", fill=("#a8bcff", 14), rimcam=0, panes=0),
    "B": dict(world=("#fff3dc", 0.55), sun=1.0, g={"p_row": 60, "p_row2": 50}, pane="#6f8fe0", moonc="#ffffff", fill=("#fff0dc", 6), rimcam=0, panes=0),
}
SUNDIR = {"D": (-0.5, -0.6, 0.62), "K": (-0.3, -0.5, 0.8), "E": (-0.45, -0.7, 0.55), "SD": (-0.3, -0.4, 0.85), "B": (-0.3, -0.5, 0.8)}
PLACE = {"N": "up", "DAWN": "up", "D": "up", "NDAD": "up", "K": "k", "E": "e", "SD": "s", "SN": "s", "B": "r"}

SPARE_WALLS = ("w_sp_W", "w_sp_N", "w_sp_S", "w_sp_E", "fl_E", "fl_N", "fl_S")
DAD_WALLS = ("w_dd_E", "w_dd_N", "w_dd_S", "w_dd_W")
ALLWALLS = SPARE_WALLS + DAD_WALLS + ("w_hall", "w_hallN", "w_gr", "k_N", "k_W", "k_E", "s_W", "s_E", "s_S", "r_f0", "r_f1", "r_f2")


def _mix_look(a, b, u):
    out = {}
    for k, va in a.items():
        vb = b[k]
        if k == "g":
            out[k] = {n: va.get(n, 0) + (vb.get(n, 0) - va.get(n, 0)) * u for n in set(va) | set(vb)}
        elif isinstance(va, tuple):
            ca, cb = hx(va[0]), hx(vb[0])
            out[k] = (tuple(ca[i] + (cb[i] - ca[i]) * u for i in range(3)), va[1] + (vb[1] - va[1]) * u)
        elif isinstance(va, str) and va.startswith("#"):
            ca, cb = hx(va), hx(vb)
            out[k] = tuple(ca[i] + (cb[i] - ca[i]) * u for i in range(3))
        elif isinstance(va, (int, float)):
            out[k] = va + (vb - va) * u
        else:
            out[k] = va
    return out


def _first_frame(kit, story):
    plastic = kit.plastic
    B = bpy.data.objects.get
    # Grandma: white curls, a small nose, a mint cardigan over the nightgown (off in the night shots), pearl buttons, glasses by day
    gh = B("grandma.headg")
    if gh is not None:
        curl = plastic("#f2eee4", 0.8, spec=0.05)
        import random
        rng = random.Random(5)
        for k in range(18):
            a = k * 2 * math.pi / 18
            r = 0.62
            kit.sphere(f"grandma.curl{k}", 0.15, (r * math.sin(a) * 0.95, r * math.cos(a) * 0.95 + 0.0, 0.46 + 0.05 * rng.random()), curl, gh, seg=8)
        for k in range(9):
            a = k * math.pi / 8 - math.pi / 2
            kit.sphere(f"grandma.curlt{k}", 0.16, (0.55 * math.sin(a), -0.05 + 0.05 * (k % 2), 0.66), curl, gh, seg=8)
        for sx in (-1, 1):   # side curls down to the ears
            kit.sphere(f"grandma.curls{sx}", 0.2, (sx * 0.58, 0.05, 0.12), curl, gh, seg=8)
            kit.sphere(f"grandma.curls2{sx}", 0.18, (sx * 0.56, 0.12, -0.15), curl, gh, seg=8)
        skin = plastic("#9a6a48", 0.5)
        kit.box("grandma.nose", (0.1, 0.08, 0.13), (0, -0.635, -0.05), skin, gh, bevel=0.03)
    # the wink: a skin lid over one eye with a short dark closed-eye arc, both 1 cm or more proud of the head
    if gh is not None:
        import math as _m
        skin_w = plastic("#a8754f", 0.5)
        ink_w = plastic("#1c120c", 0.5)
        W["wink"] = []
        ang = 22.0
        ex_, ey_ = 0.62 * _m.sin(ang * D2R), -0.62 * _m.cos(ang * D2R)
        rr = 0.64
        px, py = rr * _m.sin(ang * D2R), -rr * _m.cos(ang * D2R)
        W["wink"].append(kit.box("grandma.lid", (0.28, 0.02, 0.27), (px, py, 0.08), skin_w, gh, rot=(0, 0, ang * D2R), bevel=0.04))
        rr2 = 0.675
        for k, (dx, tilt) in enumerate(((-0.065, -14.0), (0.065, 14.0))):
            lx = rr2 * _m.sin(ang * D2R) + dx * _m.cos(ang * D2R)
            ly = -rr2 * _m.cos(ang * D2R) + dx * _m.sin(ang * D2R)
            ob = kit.box(f"grandma.lidline{k}", (0.13, 0.02, 0.035), (lx, ly, 0.08 + 0.012), ink_w, gh, rot=(0, tilt * D2R, ang * D2R))
            W["wink"].append(ob)
    gt = B("grandma.torso")
    if gt is not None:
        mint = plastic("#7fd8b8", 0.7, spec=0.1)
        cream = plastic("#f7edd3", 0.8)
        W["gcard"] = []
        W["gcard"].append(kit.box("grandma.card", (2.06, 1.06, 2.04), (0, 0, 1.0), mint, gt, bevel=0.08))
        W["gcard"].append(kit.box("grandma.placket", (0.34, 0.02, 2.0), (0, -0.54, 1.0), cream, gt))
        for k in range(5):
            W["gcard"].append(kit.sphere(f"grandma.pearl{k}", 0.075, (0.0, -0.57, 0.3 + k * 0.38), plastic("#fffaf4", 0.2, spec=1.0), gt, seg=8))
        for sx in (-1, 1):
            arm = B(f"grandma.arm{sx}")
            if arm is not None:
                W["gcard"].append(kit.box(f"grandma.cardsleeve{sx}", (1.04, 1.04, 1.76), (0, 0, -0.625), mint, arm, bevel=0.05))
        skirt = kit.box("grandma.skirt", (2.1, 1.14, 1.5), (0, 0, -0.78), plastic("#f4ecf6", 0.8), gt, bevel=0.06)
        W["gskirt"] = skirt
    for sx in (-1, 1):   # her gold glasses are the rig's (extras), toggled by shot
        pass
    # Dad: a short gray beard and reading glasses pushed up on his head
    dh = B("dad.headg")
    if dh is not None:
        gray = plastic("#a2a2ab", 0.8, spec=0.05)
        kit.box("dad.beard", (0.9, 0.12, 0.3), (0, -0.56, -0.47), gray, dh, bevel=0.05)
        kit.box("dad.beardsides", (1.22, 0.5, 0.45), (0, -0.2, -0.33), gray, dh, bevel=0.1)
        for sx in (-1, 1):   # ears, so a head turned away still reads as a head
            kit.box(f"dad.ear{sx}", (0.1, 0.16, 0.3), (sx * 0.665, 0.02, -0.02), plastic("#855536", 0.5), dh, bevel=0.03)
        blk = plastic("#2b2b34", 0.4)
        kit.box("dad.rd1", (1.0, 0.05, 0.05), (0, -0.52, 0.5), blk, dh)
        for sx in (-1, 1):
            kit.box(f"dad.rl{sx}", (0.36, 0.05, 0.26), (sx * 0.26, -0.54, 0.4), kit.glass("#dde6ea"), dh, bevel=0.03)
    # Ro: a duffel is a prop by her feet when she is shown (placed in meta); Ezra's jersey number is a glyph only
    W["inited"] = True


def _group(name, on):
    for ob in W.get("g", {}).get(name, []):
        ob.hide_render = not on


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    sid = shot["id"]
    m = META.get(sid, {})
    lk = m.get("look", "N")
    look = LOOKS[lk]
    if m.get("dawn"):
        dw = sample("dawn", tl, t, {"u": 0.0})["u"]
        look = _mix_look(LOOKS["N"], LOOKS["DAWN"], dw)
    gains = {}
    for nm in ("sun", "p_sp", "p_hall", "p_hallN", "p_dd", "p_gr", "p_k", "p_st", "p_row", "p_row2", "moon", "lamp", "rim"):
        gains[nm] = look["g"].get(nm, 0.0) * m.get("gmul", 1.0) if nm != "sun" else 0.0
    gains["sun"] = look["sun"] * 1.0
    gains["rim"] = m.get("rim", 0.0)
    gains["lamp"] = look["g"].get("lamp", 0.0)
    # world and the sun's direction
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    wc, ws = look["world"]
    wc = hx(wc) if isinstance(wc, str) else wc
    bg.inputs["Color"].default_value = (*wc, 1.0)
    bg.inputs["Strength"].default_value = ws * m.get("wmul", 1.0)
    if lk in SUNDIR:
        d = Vector(SUNDIR[lk]).normalized()
        W["sun"].location = d * 60
        kit.aim(W["sun"], (0, 0, 0))
    # the camera fill: scaled to how far the camera is from what it looks at, so a close-up and a wide read the same
    spec = next((s for s in story["shots"] if s["id"] == sid), None)
    dist = 1.5
    lens = 40.0
    if spec:
        k0 = spec["cam"][0]
        dist = max(0.5, float((Vector(k0[1]) - Vector(k0[2])).length))
        lens = k0[3]
    fc, fe = look["fill"]
    fc = hx(fc) if isinstance(fc, str) else fc
    kit.LIGHTS["camfill"]["light"].color = fc
    gains["camfill"] = fe * m.get("fill", 1.0) * max(0.5, (dist / 1.3) ** 2)
    gains["camrim"] = 0.0
    # the window pane and the moon
    if W.get("pane") is not None:
        pm = W["pane"].data.materials[0]
        pc = look["pane"]
        pc = hx(pc) if isinstance(pc, str) else pc
        em = next((n for n in pm.node_tree.nodes if n.type == "EMISSION"), None)
        if em is not None:
            em.inputs["Color"].default_value = (*pc, 1.0)
            em.inputs["Strength"].default_value = look["panes"]
    kit.LIGHTS["moon"]["light"].color = hx(look["moonc"]) if isinstance(look["moonc"], str) else look["moonc"]
    # what to show: walls (a camera "outside" a wall hides it), the quilt and pillow variants, day-or-night things
    hide = set(m.get("hide", ()))
    for g in ALLWALLS:
        _group(g, g not in hide)
    for fl, wl in (("fl_E", "w_sp_E"), ("fl_N", "w_sp_N"), ("fl_S", "w_sp_S")):
        if wl in hide:
            _group(fl, False)
    qv = m.get("quilt", "lump")
    for k, ob in W["quilt"].items():
        ob.hide_render = k != qv
    pv = m.get("pillow", "plain")
    for k, ob in W["pillow"].items():
        ob.hide_render = k != pv
    _group("slippers", bool(m.get("slippers")))
    _group("pennant", bool(m.get("pennant")))
    _group("duffel", bool(m.get("duffel")))
    W["g"]["door_sp"][0].rotation_euler = (0, 0, m.get("door_sp", 10.0) * D2R)
    W["g"]["door_dd"][0].rotation_euler = (0, 0, (180 + m.get("door_dd", 40.0)) * D2R)
    W["g"]["door_gr"][0].rotation_euler = (0, 0, (-90 + m.get("door_gr", 14.0)) * D2R)
    _group("prints", lk == "E")
    _group("flakes", bool(m.get("flakes")))
    _group("cargo", bool(m.get("cargo", True)))
    _group("cake0", bool(m.get("cake0")))
    _group("cake1", bool(m.get("cake1")))
    for i in range(4):
        _group(f"plate{i}", True)
    _group("boxes", True)
    W["car"].hide_render = False
    if W.get("gskirt") is not None:
        W["gskirt"].hide_render = bool(m.get("noskirt", False))
    for ob in W.get("wink", []):
        ob.hide_render = not m.get("wink", False)
    for ob in W.get("gcard", []):
        ob.hide_render = not m.get("card", False)
    # glasses: Grandma's rig extras on by day only
    for nm in ("grandma.gl-1", "grandma.gl1", "grandma.glf-1", "grandma.glf1", "grandma.glb"):
        ob = bpy.data.objects.get(nm)
        if ob is not None:
            ob.hide_render = (not m.get("glasses", False)) or nm in ("grandma.gl-1", "grandma.gl1")
    # the tag: my nights facing the wall, then the second row's two cells
    tg = sample("tag", tl, t, {"n": 0.0, "h": 0.0})
    n = int(round(tg["n"]))
    segs = DIGIT.get(n, "")
    for k, ob in W["digits"][0].items():
        ob.hide_render = k not in segs
    _group("row", tg["h"] >= 0.5)
    _group("cell2", tg["h"] >= 0.5)
    _group("cell3", tg["h"] >= 1.5)
    # the tag sits top-left, scaled to the lens
    dd = 1.0
    h2 = dd * 12.0 / lens
    w2 = h2 * 9.0 / 16.0
    s = 0.60 * w2 / 0.6
    tag = W["tag"]
    s = 0.56 * w2
    tag.scale = (s, s, s)
    tag.location = (-0.50 * w2, 0.62 * h2, -dd)
    _apply_cast_pose(m)
    return gains


def _apply_cast_pose(m):
    """Sitting legs for whoever the shot sits, and a pat for Grandma's hand."""
    sit = m.get("sit", {})
    for who in ("me", "dad", "grandma", "ro", "ezra"):
        ang = sit.get(who)
        if ang is None:
            continue
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg is not None:
                leg.rotation_euler = (-ang * D2R, 0, 0)
    sl = m.get("stepleg")
    leg = bpy.data.objects.get("grandma.leg-1")
    if leg is not None and sl:
        leg.rotation_euler = (-sl * D2R, 0, 0)
