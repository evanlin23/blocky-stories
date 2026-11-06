"""ep120 "Dad's Place Still Says My Last WORDS": a street of painted houses by day, an empty house, my building's lot
at night, a pickup, Dad's place over his auto shop.

Every place is its own stage far from the others (layout.py); animate() lights only the stage the shot's camera is in
and drives everything the story moves from cues in story.json: the ripple (a house's voice), the rule tag's counter
(days since I was in Dad's place), the pickup (drive, lights, door, the dark shape in its cab), the apartment's lamp,
door and dust, the toast, the dog's tail. The tag is a child of the camera.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {"lights": {}, "emit": {}}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


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


def B(kit, name, x0, x1, y0, y1, z0, z1, mat, parent=None, bevel=0.0):
    return kit.box(name, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), mat, parent, bevel=bevel)


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def LT(kit, stage, name, kind, loc, energy, hexc, **kw):
    ob = kit.light(f"{stage}.{name}", kind, loc, energy, hexc, **kw)
    W["lights"][f"{stage}.{name}"] = stage
    return ob


def ring(kit, name, r0, r1, mat, n=40, parent=None):
    """An annulus in the local XZ plane (its face toward -y)."""
    verts, faces = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        verts.append((r0 * math.cos(a), 0, r0 * math.sin(a)))
        verts.append((r1 * math.cos(a), 0, r1 * math.sin(a)))
    for i in range(n):
        j = (i + 1) % n
        faces.append((2 * i, 2 * i + 1, 2 * j + 1, 2 * j))
    return kit.mesh_obj(name, verts, faces, mat, parent)


# ------------------------------------------------------------------------------------------ seven segments
SEG = {"0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg", "5": "acdfg", "6": "acdefg", "7": "abc",
       "8": "abcdefg", "9": "abcdfg"}


def pbox(kit, name, parent, plane, cu, cv, w, h, layer, mat):
    if plane == "xy":
        return kit.box(name, (w, h, 0.002), (cu, cv, layer), mat, parent)
    if plane == "xz":
        return kit.box(name, (w, 0.002, h), (cu, -layer, cv), mat, parent)
    return kit.box(name, (w, h, 0.002), (cu, cv, layer), mat, parent)


def seg_digit(kit, name, parent, plane, cu, cv, w, h, t, layer, mat):
    hh = h / 2
    defs = {"a": (0, hh - t / 2, w, t), "g": (0, 0, w, t), "d": (0, -hh + t / 2, w, t),
            "f": (-w / 2 + t / 2, hh / 2, t, hh), "b": (w / 2 - t / 2, hh / 2, t, hh),
            "e": (-w / 2 + t / 2, -hh / 2, t, hh), "c": (w / 2 - t / 2, -hh / 2, t, hh)}
    return {k: pbox(kit, f"{name}.{k}", parent, plane, cu + du, cv + dv, sw, sh, layer, mat)
            for k, (du, dv, sw, sh) in defs.items()}


def show_digit(segs, ch):
    on = SEG.get(ch, "")
    for k, ob in segs.items():
        ob.hide_render = k not in on


# ------------------------------------------------------------------------------------------------ the tag
def build_tag(kit):
    """The rule meter: a cream tag with a sound-wave glyph and three seven-segment digits: days since I was in Dad's
    place. A child of the camera, top left of every frame."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    cream = kit.emit("#fff3d6", 1.0, "tagcream")
    edge = kit.emit("#2b1c14", 0.6, "tagedge")
    ink = kit.emit("#14202e", 0.8, "taginky")
    teal = kit.emit("#12a58a", 1.0, "tagteal")

    def b(name, size, loc, mat):
        ob = kit.box(name, size, loc, mat, root)
        noshadow(ob)
        return ob
    b("tag.edge", (1.04, 0.84, 0.004), (0, 0, 0.0), edge)
    b("tag.plate", (0.98, 0.78, 0.004), (0, 0, 0.004), cream)
    for i, hgt in enumerate([0.2, 0.36, 0.54, 0.36, 0.2]):
        b(f"tag.wave{i}", (0.05, hgt, 0.004), (-0.44 + i * 0.065, 0, 0.008), teal)
    W["digits"] = []
    W["digroot"] = kit.empty("tag.digits", (0, 0, 0), root)
    for i in range(3):
        segs = seg_digit(kit, f"tag.d{i}", W["digroot"], "xy", 0.0 + i * 0.185, 0.0, 0.14, 0.5, 0.06, 0.008, ink)
        for ob in segs.values():
            noshadow(ob)
        W["digits"].append((segs, 0.0 + i * 0.185))


def build_bezel(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("bezel", (0, 0, 0), cam)
    W["bezel"] = root
    m = kit.emit("#0b0c10", 0.25, "bezelmat")
    for nm, size, loc in [("t", (2.0, 0.09, 0.004), (0, 0.955, 0)), ("b", (2.0, 0.09, 0.004), (0, -0.955, 0)),
                          ("l", (0.12, 2.0, 0.004), (-0.94, 0, 0)), ("r", (0.12, 2.0, 0.004), (0.94, 0, 0))]:
        ob = kit.box(f"bezel.{nm}", size, loc, m, root)
        noshadow(ob)


def set_tag_value(n):
    s = str(int(n))
    k = len(s)
    for i, (segs, x0) in enumerate(W["digits"]):
        j = i - (3 - k)
        if j < 0:
            for ob in segs.values():
                ob.hide_render = True
            continue
        show_digit(segs, s[j])
    W["digroot"].location.x = -(3 - k) * 0.185 / 2


# ---------------------------------------------------------------------------------------------- the ripple
def build_ripple(kit):
    root = kit.empty("ripple", (0, 0, 0))
    W["ripple"] = root
    W["rings"] = []
    for i in range(3):
        m = kit.emit("#9ff5dc", 2.0, f"ripplemat{i}")
        e = next(n for n in m.node_tree.nodes if n.type == "EMISSION")
        ob = ring(kit, f"ripple.ring{i}", 0.92, 1.0, m, 48, root)
        noshadow(ob)
        W["rings"].append((ob, e))


def ripple_at(tl, t):
    r = sample("ripple", tl, t, {"on": 0.0, "x": 0.0, "y": 0.0, "z": 0.0, "s": 1.0, "yaw": 0.0, "ax": 1.0, "k": 1.0})
    root = W["ripple"]
    on = r["on"] > 0.02
    for i, (ob, e) in enumerate(W["rings"]):
        ph = ((t * 0.55 + i / 3.0) % 1.0)
        sc = r["s"] * (0.35 + 0.65 * ph)
        ob.scale = (sc * r["ax"], 1.0, sc)
        e.inputs["Strength"].default_value = 2.6 * r["on"] * r["k"] * (1.0 - ph) ** 0.8 * min(1.0, ph * 6.0)
        ob.hide_render = (not on) or e.inputs["Strength"].default_value < 0.05
    root.location = (r["x"], r["y"], r["z"])
    root.rotation_euler = (0, 0, r["yaw"] * D2R)


# ------------------------------------------------------------------------------------------- build helpers
def M(kit):
    p = kit.plastic
    return {
        "white": p("#fbf6ec", 0.6, spec=0.2), "cream": p("#f4e6c8", 0.8, spec=0.05), "wood": p("#b98a58", 0.7, spec=0.1),
        "dwood": p("#8a5c34", 0.7, spec=0.1), "dark": p("#2a2d36", 0.7, spec=0.1), "black": p("#0c0d12", 0.6, spec=0.1),
        "glass": p("#9fd0ea", 0.15, spec=0.8), "red": p("#d8342e", 0.35, spec=0.5), "chrome": kit.metal("#d9dde2", 0.2),
        "tire": p("#1a1b1f", 0.9, spec=0.05), "gray": p("#98a2ae", 0.6, spec=0.2),
    }


def gable(kit, name, cx, cy, w, d, z0, rise, mat):
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, cy, z0 + rise), (x1, cy, z0 + rise)]
    f = [(0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5)]
    return kit.mesh_obj(name, v, f, mat)


def house(kit, m, name, x, yf, col, door_col="#fff4e0", w=8.0, d=7.0, h=3.9, opened=False, roof="#a8553f"):
    """A clapboard house, front at y = yf facing -y, its door at x."""
    p = kit.plastic
    body = p(col, 0.7, spec=0.1)
    B(kit, f"{name}.body", x - w / 2, x + w / 2, yf, yf + d, 0, h, body)
    light = p("#ffffff", 0.7, spec=0.05)
    for i in range(9):
        z = 0.5 + i * 0.4
        B(kit, f"{name}.cb{i}", x - w / 2, x + w / 2, yf - 0.035, yf, z, z + 0.07, light)
    gable(kit, f"{name}.roof", x, yf + d / 2, w + 0.8, d + 0.8, h, 1.9, p(roof, 0.8, spec=0.05))
    for sx in (-2.7, 2.7):
        B(kit, f"{name}.wf{sx}", x + sx - 0.7, x + sx + 0.7, yf - 0.08, yf - 0.05, 1.5, 2.9, m["white"])
        B(kit, f"{name}.wg{sx}", x + sx - 0.55, x + sx + 0.55, yf - 0.1, yf - 0.08, 1.65, 2.75, m["glass"])
    B(kit, f"{name}.df", x - 0.68, x + 0.68, yf - 0.09, yf - 0.05, 0, 2.35, m["white"])
    if opened:
        B(kit, f"{name}.dark", x - 0.55, x + 0.55, yf - 0.095, yf - 0.09, 0, 2.2, p("#3a3246", 0.9))
        hinge = kit.empty(f"{name}.hinge", (x - 0.55, yf - 0.1, 0))
        hinge.rotation_euler = (0, 0, 85 * D2R)
        kit.box(f"{name}.leaf", (1.1, 0.07, 2.2), (0.55, 0, 1.1), p(door_col, 0.5, spec=0.3), hinge)
    else:
        B(kit, f"{name}.leaf", x - 0.55, x + 0.55, yf - 0.12, yf - 0.09, 0, 2.2, p(door_col, 0.5, spec=0.3))
        kit.sphere(f"{name}.knob", 0.05, (x + 0.38, yf - 0.15, 1.05), m["chrome"], seg=8)
    B(kit, f"{name}.step", x - 1.0, x + 1.0, yf - 0.9, yf - 0.1, 0, 0.18, m["gray"], bevel=0.03)
    B(kit, f"{name}.step2", x - 0.85, x + 0.85, yf - 1.4, yf - 0.9, 0, 0.1, m["gray"], bevel=0.03)


def tree(kit, name, x, y, h=5.5, tint="#bfe8a8"):
    try:
        kit.prop("commontree_1", (x, y, 0), height=h, tint=tint)
    except Exception:
        kit.cyl(f"{name}.trunk", 0.25, h * 0.45, (x, y, h * 0.22), kit.plastic("#7a5230", 0.8), n=8)
        kit.sphere(f"{name}.crown", h * 0.28, (x, y, h * 0.68), kit.plastic("#5fae4a", 0.8), seg=10)


def wheel(kit, name, parent, x, y, z, r=0.42):
    kit.cyl(f"{name}", r, 0.28, (x, y, z), kit.plastic("#1a1b1f", 0.9, spec=0.05), parent, rot=(0, math.pi / 2, 0), n=16)
    kit.cyl(f"{name}.hub", r * 0.5, 0.3, (x + (0.01 if x > 0 else -0.01), y, z), kit.metal("#cfd3d8", 0.3), parent,
            rot=(0, math.pi / 2, 0), n=12)


def vehicle(kit, m, name, loc, yaw, color, pickup=True, glass=True, shape=False, stage="lot", handle_marks=False):
    """A car or pickup: forward is local +y, the driver (a left-hand drive) sits at local x -0.45, y -0.2. Windows are
    open frames unless glass. Returns its parts."""
    p = kit.plastic
    root = kit.empty(name, loc, rot=(0, 0, yaw * D2R))
    body = p(color, 0.3, spec=0.6)
    dark = p("#23252c", 0.8, spec=0.1)
    L = 5.2 if pickup else 4.4
    front, rear = L / 2, -L / 2
    B(kit, f"{name}.low", -1.0, 1.0, rear, front, 0.4, 1.0, body, root, bevel=0.06)
    B(kit, f"{name}.floor", -0.95, 0.95, -1.0, 0.9, 0.3, 0.45, dark, root)
    # the cab: roof, pillars
    cab_y0, cab_y1 = -0.95, 0.85
    roof = B(kit, f"{name}.roof", -1.0, 1.0, cab_y0 - 0.05, -0.45 if shape else cab_y1 - 0.2, 1.93, 2.03, body, root, bevel=0.05)
    for sx in (-1, 1):
        kit.box(f"{name}.A{sx}", (0.1, 0.1, 1.0), (sx * 0.96, cab_y1 - 0.2 + 0.0, 1.48), body, root, rot=(0.35, 0, 0))
        B(kit, f"{name}.C{sx}", sx * 0.96 - 0.05, sx * 0.96 + 0.05, cab_y0 - 0.05, cab_y0 + 0.1, 1.0, 1.95, body, root)
    B(kit, f"{name}.rearwall", -1.0, 1.0, cab_y0 - 0.1, cab_y0 - 0.05, 1.0, 1.95, body, root)
    # seat, dash, wheel
    seat = p("#c9a678", 0.8, spec=0.05)
    B(kit, f"{name}.seat", -0.93, 0.93, -0.55, 0.2, 0.42, 0.62, seat, root, bevel=0.05)
    B(kit, f"{name}.seatback", -0.93, 0.93, -0.72, -0.56, 0.55, 1.35, seat, root, bevel=0.05)
    B(kit, f"{name}.dash", -0.95, 0.95, 0.5, 0.95, 0.85, 1.12, dark, root, bevel=0.05)
    wh = ring(kit, f"{name}.wheelring", 0.15, 0.2, p("#14151a", 0.6), 20, root)
    wh.location = (-0.45, 0.42, 1.12)
    wh.rotation_euler = (-0.5, 0, 0)
    # wheels, bed, lights
    for sx in (-1, 1):
        wheel(kit, f"{name}.wf{sx}", root, sx * 1.0, front - 0.95, 0.42)
        wheel(kit, f"{name}.wr{sx}", root, sx * 1.0, rear + 0.95, 0.42)
    if pickup:
        B(kit, f"{name}.bedfloor", -0.95, 0.95, -2.55, -1.05, 0.95, 1.05, dark, root)
        for sx in (-1, 1):
            B(kit, f"{name}.bedside{sx}", sx * 0.95 - 0.05, sx * 0.95 + 0.05, -2.6, -1.05, 1.0, 1.4, body, root, bevel=0.03)
        B(kit, f"{name}.bedback", -1.0, 1.0, -2.6, -2.5, 1.0, 1.4, body, root, bevel=0.03)
    B(kit, f"{name}.hood", -0.95, 0.95, 0.85, front, 1.0, 1.1, body, root, bevel=0.05)
    hl = kit.emit("#fff4d0", 5.0, f"{name}.hlmat")
    tl_ = kit.emit("#ff2a22", 3.0, f"{name}.tlmat")
    parts = {"root": root, "heads": [], "tails": []}
    for sx in (-1, 1):
        parts["heads"].append(kit.box(f"{name}.hl{sx}", (0.34, 0.05, 0.2), (sx * 0.7, front + 0.01, 0.78), hl, root))
        parts["tails"].append(kit.box(f"{name}.tl{sx}", (0.3, 0.05, 0.22), (sx * 0.78, rear - 0.01, 0.82), tl_, root))
    kit.box(f"{name}.grille", (1.0, 0.04, 0.24), (0, front + 0.01, 0.65), kit.metal("#c8ccd2", 0.3), root)
    sp = LT(kit, stage, f"{name}.spot", "SPOT", (0, front, 0.8), 700.0, "#fff1cc", parent=root, spot=55, blend=0.5, size=0.2,
            shadow=False)
    sp.rotation_euler = (math.pi / 2 - 0.12, 0, 0)
    parts["spot"] = f"{stage}.{name}.spot"
    if glass:
        gm = kit.glass("#c9dcee")
        ws = kit.box(f"{name}.windshield", (1.9, 0.03, 0.92), (0, cab_y1 - 0.02, 1.47), gm, root, rot=(0.37, 0, 0))
        B(kit, f"{name}.rearglass", -0.9, 0.9, cab_y0 - 0.03, cab_y0, 1.1, 1.9, gm, root)
        for sx in (-1, 1):
            B(kit, f"{name}.sidegl{sx}", sx * 1.0 - 0.015, sx * 1.0 + 0.015, cab_y0 + 0.1, cab_y1 - 0.2, 1.1, 1.9, gm, root)
    # the driver's door: hinge at its front edge, opens outward (-x)
    hinge = kit.empty(f"{name}.dhinge", (-1.02, 0.55, 0), root)
    parts["door"] = hinge
    kit.box(f"{name}.door", (0.06, 1.45, 0.62), (0.0, -0.72, 0.69), body, hinge, bevel=0.02)
    hm = kit.metal("#e6e9ee", 0.15)
    kit.box(f"{name}.handle", (0.04, 0.3, 0.06), (-0.045, -1.12, 0.88), hm, hinge)
    if handle_marks:
        gm2 = p("#49c06b", 0.5, spec=0.1)
        for k in range(2):
            kit.box(f"{name}.mark{k}", (0.012, 0.022, 0.05), (-0.0715, -1.05 - 0.09 * k, 0.88), gm2, hinge)
    if shape:
        sm = p("#05060a", 0.9, spec=0.02)
        rim = kit.emit("#ffb347", 5.0, "shaperim")
        sh = kit.empty(f"{name}.shape", (-0.45, -0.2, 0), root)
        parts["shape"] = sh
        kit.box(f"{name}.shape.torso", (0.82, 0.34, 0.62), (0, 0, 1.12), sm, sh, bevel=0.07)
        kit.box(f"{name}.shape.neck", (0.2, 0.2, 0.14), (0, 0, 1.5), sm, sh)
        head = kit.empty(f"{name}.shape.head", (0, 0, 1.72), sh)
        parts["head"] = head
        kit.box(f"{name}.shape.skull", (0.42, 0.44, 0.5), (0, 0, 0), sm, head, bevel=0.14)
        kit.box(f"{name}.shape.hrim", (0.3, 0.32, 0.015), (0, -0.04, 0.262), rim, head)
        kit.box(f"{name}.shape.srimL", (0.18, 0.3, 0.015), (-0.31, 0, 1.425), rim, sh)
        kit.box(f"{name}.shape.srimR", (0.18, 0.3, 0.015), (0.31, 0, 1.425), rim, sh)
        kit.box(f"{name}.shape.hrimL", (0.012, 0.32, 0.3), (-0.215, -0.04, 0.02), rim, head)
        kit.box(f"{name}.shape.hrimR", (0.012, 0.32, 0.3), (0.215, -0.04, 0.02), rim, head)
    return parts


def cab_interior(kit, m, ox, oy):
    """The pickup's cab from inside, facing +y: a bench seat, the wheel and dash, a roof with a dome light, pillars,
    side doors with open windows; the open windshield has nothing in it, so the camera sits past the dash."""
    p = kit.plastic
    body = p("#d8342e", 0.35, spec=0.5)
    seat = p("#d9b88a", 0.8, spec=0.05)
    dark = p("#2b2e36", 0.8, spec=0.1)
    floor = p("#3a3d46", 0.9, spec=0.05)
    B(kit, "cab.floor", ox - 1.1, ox + 1.1, oy - 1.0, oy + 1.2, -0.05, 0.05, floor)
    B(kit, "cab.seat", ox - 0.98, ox + 0.98, oy - 0.55, oy + 0.2, 0.05, 0.54, seat, bevel=0.05)
    B(kit, "cab.seatback", ox - 0.98, ox + 0.98, oy - 0.78, oy - 0.56, 0.5, 1.4, seat, bevel=0.06)
    B(kit, "cab.dash", ox - 1.0, ox + 1.0, oy + 0.7, oy + 1.15, 0.5, 1.0, dark, bevel=0.05)
    B(kit, "cab.dashtop", ox - 1.0, ox + 1.0, oy + 0.7, oy + 1.15, 1.0, 1.06, p("#d8342e", 0.5), bevel=0.03)
    wh = ring(kit, "cab.wheel", 0.17, 0.23, p("#14151a", 0.6), 24)
    wh.location = (ox - 0.45, oy + 0.5, 1.0)
    wh.rotation_euler = (-0.55, 0, 0)
    kit.cyl("cab.col", 0.05, 0.5, (ox - 0.45, oy + 0.55, 0.78), dark, rot=(0.9, 0, 0), n=10)
    B(kit, "cab.roof", ox - 1.15, ox + 1.15, oy - 1.0, oy + 0.9, 2.0, 2.1, body, bevel=0.05)
    for sx in (-1, 1):
        B(kit, f"cab.door{sx}", ox + sx * 1.0 - 0.06, ox + sx * 1.0 + 0.06, oy - 0.9, oy + 0.8, 0.0, 0.95, body, bevel=0.03)
        B(kit, f"cab.doorin{sx}", ox + sx * 0.93 - 0.02, ox + sx * 0.93 + 0.02, oy - 0.85, oy + 0.75, 0.1, 0.9, p("#a89478", 0.8))
        B(kit, f"cab.A{sx}", ox + sx * 1.0 - 0.06, ox + sx * 1.0 + 0.06, oy + 0.75, oy + 0.9, 0.9, 2.0, body)
        B(kit, f"cab.C{sx}", ox + sx * 1.0 - 0.06, ox + sx * 1.0 + 0.06, oy - 1.0, oy - 0.85, 0.9, 2.0, body)
    B(kit, "cab.rear", ox - 1.1, ox + 1.1, oy - 1.05, oy - 0.95, 0.0, 0.7, body)
    B(kit, "cab.reartop", ox - 1.1, ox + 1.1, oy - 1.05, oy - 0.95, 1.7, 2.0, body)
    # the rear window shows the night: a streetlight's glow beyond
    kit.sphere("cab.glow", 0.5, (ox + 1.5, oy - 6.0, 3.0), kit.emit("#ffb347", 3.0), seg=10)
    dome = kit.emit("#fff0cc", 3.0, "domemat")
    kit.box("cab.dome", (0.3, 0.2, 0.04), (ox, oy - 0.1, 1.97), dome)
    LT(kit, "cab", "dome", "POINT", (ox, oy - 0.1, 1.85), 60.0, "#ffe2b0", size=0.2)
    LT(kit, "cab", "fill", "AREA", (ox + 0.3, oy + 1.6, 1.8), 40.0, "#cfdcff", size=1.2, shadow=False)
    kit.aim(kit.LIGHTS["cab.fill"]["obj"], (ox - 0.3, oy - 0.2, 1.3))
    # the thermos
    tm = p("#49c06b", 0.35, spec=0.5)
    th = kit.empty("cab.thermos", (ox + 0.4, oy - 0.15, 0.54))
    kit.cyl("cab.thermos.body", 0.065, 0.3, (0, 0, 0.15), tm, th, n=18)
    kit.cyl("cab.thermos.cap", 0.062, 0.07, (0, 0, 0.33), kit.metal("#c9ced4", 0.3), th, n=18)
    kit.cyl("cab.thermos.lip", 0.07, 0.02, (0, 0, 0.285), kit.metal("#c9ced4", 0.3), th, n=18)
    kit.box("cab.thermos.handle", (0.025, 0.1, 0.17), (0.0, 0.0, 0.17), p("#2e8f4d", 0.5), th)
    # the dent faces the cameras at its +x,+y side: a dark squashed hollow with a pale scuffed lip under it
    dn = kit.sphere("cab.thermos.dent", 0.034, (0.0425, 0.0495, 0.16), p("#1b5530", 0.4, spec=0.1), th, seg=18)
    dn.scale = (1.3, 0.3, 1.7)
    dn.rotation_euler = (0, 0, -40.5 * D2R)
    dr_ = kit.sphere("cab.thermos.dentlip", 0.036, (0.0445, 0.0522, 0.118), p("#6fd88a", 0.8, spec=0.05), th, seg=18)
    dr_.scale = (1.2, 0.2, 0.4)
    dr_.rotation_euler = (0, 0, -40.5 * D2R)
    W["thermos"] = th
    W["palm3"] = palm(kit, "palm3", (ox + 0.05, oy - 0.05, 0.54), 0, "#d9a67a")


def palm(kit, name, loc, yaw, skin, phone=None):
    """A flat open hand (palm up) on a short forearm; a phone lying on it if phone is set."""
    root = kit.empty(name, loc, rot=(0, 0, yaw * D2R))
    root.scale = (1.5, 1.5, 1.5)
    sk = kit.plastic(skin, 0.5)
    kit.box(f"{name}.arm", (0.1, 0.34, 0.06), (0, 0.34, 0.03), sk, root, bevel=0.015)
    kit.box(f"{name}.palm", (0.12, 0.13, 0.04), (0, 0.1, 0.02), sk, root, bevel=0.012)
    for i, dx in enumerate([-0.045, -0.015, 0.015, 0.045]):
        kit.box(f"{name}.f{i}", (0.026, 0.1, 0.028), (dx, 0.0, 0.016), sk, root, bevel=0.008)
    kit.box(f"{name}.thumb", (0.03, 0.08, 0.03), (0.075, 0.12, 0.02), sk, root, rot=(0, 0, -0.5), bevel=0.01)
    if phone:
        ph = kit.empty(f"{name}.phone", (0, 0.07, 0.05), root)
        kit.box(f"{name}.phone.body", (0.085, 0.165, 0.012), (0, 0, 0.006), kit.plastic("#16181e", 0.4, spec=0.5), ph, bevel=0.01)
        scr = kit.emit("#bfe3ff", 1.6, f"{name}.screen")
        pbox(kit, f"{name}.phone.screen", ph, "xy", 0, 0, 0.074, 0.15, 0.0125, scr)
        ink = kit.emit("#16202e", 1.0, f"{name}.sink")
        grn = kit.emit("#2fae5f", 1.2, f"{name}.sgreen")
        wht = kit.emit("#f4fbff", 1.4, f"{name}.swhite")
        # a call log: a green handset tile and one "0" on top, then plain list rows (a dot and a bar each)
        pbox(kit, f"{name}.phone.tile", ph, "xy", -0.02, 0.052, 0.036, 0.036, 0.0135, grn)
        hs = pbox(kit, f"{name}.phone.hs", ph, "xy", -0.02, 0.052, 0.026, 0.008, 0.0145, wht)
        hs.rotation_euler = (0, 0, 0.8)
        for sgn in (-1, 1):
            pbox(kit, f"{name}.phone.hsend{sgn}", ph, "xy", -0.02 + sgn * 0.0095, 0.052 + sgn * 0.0095, 0.011, 0.011, 0.0145, wht)
        seg_digit(kit, f"{name}.phone.d0", ph, "xy", 0.02, 0.052, 0.022, 0.044, 0.008, 0.0135, ink)
        for k in "abcdefg":
            ob = bpy.data.objects.get(f"{name}.phone.d0.{k}")
            if ob is not None:
                ob.hide_render = k not in SEG["0"]
        for i in range(3):
            pbox(kit, f"{name}.phone.dot{i}", ph, "xy", -0.026, 0.0 - i * 0.03, 0.012, 0.012, 0.0135, ink)
            pbox(kit, f"{name}.phone.bar{i}", ph, "xy", 0.006 + (0.01 if i == 1 else 0.0), 0.0 - i * 0.03,
                 0.044 - (0.012 if i == 1 else 0.0), 0.01, 0.0135, ink)
    return root


# ===================================================================================================== stages
def build_day(kit, m):
    p = kit.plastic
    kit.plane("day.ground", (500, 200), (30, 20, 0), p("#8fd16a", 0.9, spec=0.02))
    kit.plane("day.street", (500, 9), (30, -5.5, 0.02), p("#7e8497", 0.9, spec=0.05))
    for i in range(30):
        B(kit, f"day.dash{i}", -80 + i * 6, -80 + i * 6 + 2.5, -5.6, -5.4, 0.02, 0.03, p("#fff2b0", 0.8))
    kit.plane("day.walk", (500, 2.6), (30, -0.4, 0.04), p("#efe3cf", 0.9, spec=0.05))
    B(kit, "day.curb", -220, 280, -1.8, -1.6, 0.0, 0.14, p("#d8d0c4", 0.9))
    cols = ["#8fe0c4", "#ffd86b", "#ff8a73", "#8fe0c4", "#ffd86b", "#ff8a73"]
    spec = [(-38, "#ff8a73", "#fff4e0", False), (-26, "#8fe0c4", "#ff8a73", False), (-14, "#ffd86b", "#8fe0c4", False),
            (-2, "#ff8a73", "#fff4e0", False), (10, "#8fe0c4", "#ffd86b", True), (22, "#ffd86b", "#ff8a73", False),
            (50, "#8fe0c4", "#ffd86b", False), (62, "#ff8a73", "#fff4e0", False)]
    for i, (x, c, dc, op) in enumerate(spec):
        house(kit, m, f"day.h{i}", x, 8.0, c, dc, opened=op)
    for i in range(8):
        house(kit, m, f"day.far{i}", -50 + i * 14, 26.0, cols[i % 6], "#fff4e0", w=9, d=6, h=4.4 + (i % 3) * 0.4)
    for k, (x, y) in enumerate([(-20, 4.2), (4.5, 4.4), (16, 4.0), (28, 4.2), (-44, 3.8), (56, 4.1)]):
        tree(kit, f"day.tree{k}", x, y, 5.0 + (k % 2) * 0.8)
    # the house for sale: a blank board on a post
    B(kit, "day.post", -11.6, -11.5, 3.2, 3.3, 0, 1.5, m["dwood"])
    B(kit, "day.board", -12.6, -10.5, 3.14, 3.2, 0.75, 1.6, m["white"], bevel=0.02)
    B(kit, "day.boardrim", -12.65, -10.45, 3.12, 3.14, 0.72, 1.63, p("#ff8a73", 0.6))
    for i in range(4):
        B(kit, f"day.fl{i}", -17.6 + i * 1.4, -17.5 + i * 1.4, 2.2, 2.3, 0, 0.5, p("#ffffff", 0.7))
    # sun and fills
    sun = LT(kit, "day", "sun", "SUN", (0, -30, 40), 3.6, "#fff0d8", size=0.06)
    sun.data.angle = 0.06
    sun.rotation_euler = (math.radians(50), 0, math.radians(-18))
    LT(kit, "day", "fill", "SUN", (0, 30, 30), 1.2, "#cfe6ff", shadow=False).rotation_euler = (math.radians(70), 0, math.radians(160))
    shop(kit, m, "dshop", G.DAY_SHOP[0], G.DAY_SHOP[1], night=False)
    # my car (the drive-by): heading -x, the driver nearest the camera
    car = vehicle(kit, m, "dcar", (G.DAY_SHOP[0], 0.4, 0), 90.0, "#3d7bd9", pickup=False, glass=False, stage="day")
    W["dcar"] = car


def build_hall(kit, m):
    ox, oy = G.HALL
    p = kit.plastic
    wall = p("#f7ecd6", 0.85, spec=0.03)
    kit.plane("hall.floor", (8, 10), (ox, oy + 0.5, 0.01), kit.planks("#d3a874", "#c4975f", 1.0))
    B(kit, "hall.back", ox - 3.4, ox + 3.4, oy + 4.5, oy + 4.8, 0, 2.9, wall)
    B(kit, "hall.l", ox - 3.2, ox - 2.9, oy - 4.5, oy + 4.5, 0, 2.9, wall)
    B(kit, "hall.r", ox + 2.9, ox + 3.2, oy - 4.5, oy + 4.5, 0, 2.9, wall)
    B(kit, "hall.ceil", ox - 3.4, ox + 3.4, oy - 4.5, oy + 4.8, 2.9, 3.0, wall)
    B(kit, "hall.base", ox - 2.9, ox + 2.9, oy + 4.45, oy + 4.5, 0, 0.22, m["white"])
    # the front door and the glass panel beside it
    B(kit, "hall.doorframe", ox - 0.75, ox + 1.4, oy + 4.44, oy + 4.5, 0, 2.35, m["white"])
    B(kit, "hall.door", ox - 0.6, ox + 0.4, oy + 4.38, oy + 4.44, 0, 2.2, p("#6fc7e8", 0.45, spec=0.3), bevel=0.02)
    kit.sphere("hall.knob", 0.05, (ox + 0.25, oy + 4.33, 1.05), m["chrome"], seg=8)
    B(kit, "hall.sidelight", ox + 0.55, ox + 1.3, oy + 4.38, oy + 4.44, 0.45, 2.2, kit.emit("#bcd8ee", 1.1, "hallglass"))
    B(kit, "hall.mullion", ox + 0.9, ox + 0.94, oy + 4.35, oy + 4.38, 0.45, 2.2, m["white"])
    B(kit, "hall.doorlite", ox - 0.35, ox + 0.15, oy + 4.35, oy + 4.38, 1.4, 2.0, kit.emit("#bcd8ee", 0.9, "hallglass2"))
    LT(kit, "hall", "main", "POINT", (ox + 0.2, oy - 0.8, 2.6), 520.0, "#fff1d8", size=0.5)
    LT(kit, "hall", "fill", "AREA", (ox - 0.4, oy - 2.6, 1.8), 180.0, "#e8f0ff", size=2.0, shadow=False)
    kit.aim(kit.LIGHTS["hall.fill"]["obj"], (ox + 0.3, oy + 3.5, 1.4))
    # kitchen
    kx, ky = G.KITCHEN
    kit.plane("kit.floor", (8, 10), (kx, ky + 0.5, 0.01), kit.checker("#f2e9d8", "#cdbb9a", 1.0))
    B(kit, "kit.back", kx - 3.4, kx + 3.4, ky + 4.5, ky + 4.8, 0, 2.9, p("#bfe9d7", 0.85, spec=0.03))
    B(kit, "kit.l", kx - 3.2, kx - 2.9, ky - 4.5, ky + 4.5, 0, 2.9, p("#bfe9d7", 0.85))
    B(kit, "kit.r", kx + 2.9, kx + 3.2, ky - 4.5, ky + 4.5, 0, 2.9, p("#bfe9d7", 0.85))
    B(kit, "kit.ceil", kx - 3.4, kx + 3.4, ky - 4.5, ky + 4.8, 2.9, 3.0, wall)
    cab = p("#ffd86b", 0.5, spec=0.2)
    B(kit, "kit.base", kx - 2.4, kx + 2.4, ky + 3.6, ky + 4.45, 0, 0.9, cab, bevel=0.02)
    B(kit, "kit.top", kx - 2.5, kx + 2.5, ky + 3.55, ky + 4.5, 0.9, 0.96, m["white"], bevel=0.015)
    B(kit, "kit.upper", kx - 2.4, kx + 0.2, ky + 4.15, ky + 4.45, 1.7, 2.6, cab, bevel=0.02)
    B(kit, "kit.sinkbasin", kx - 0.9, kx - 0.1, ky + 3.75, ky + 4.3, 0.88, 0.9, m["chrome"])
    kit.cyl("kit.tap", 0.025, 0.3, (kx - 0.5, ky + 4.35, 1.1), m["chrome"], n=8)
    B(kit, "kit.window", kx + 0.9, kx + 2.3, ky + 4.4, ky + 4.45, 1.3, 2.4, kit.emit("#dff4ff", 3.0, "kitglass"))
    LT(kit, "kitchen", "main", "POINT", (kx, ky - 0.6, 2.6), 500.0, "#fff1d8", size=0.5)
    LT(kit, "kitchen", "fill", "AREA", (kx, ky - 2.4, 1.8), 160.0, "#e8f0ff", size=2.0, shadow=False)
    kit.aim(kit.LIGHTS["kitchen.fill"]["obj"], (kx, ky + 3.5, 1.2))
    # living room, with a couch and a dog
    lx, ly = G.LIVING
    kit.plane("liv.floor", (8, 10), (lx, ly + 0.5, 0.01), kit.planks("#d3a874", "#c4975f", 1.0))
    kit.plane("liv.rug", (4.0, 3.0), (lx, ly + 2.4, 0.02), p("#ff8a73", 0.9, spec=0.02))
    B(kit, "liv.back", lx - 3.4, lx + 3.4, ly + 4.5, ly + 4.8, 0, 2.9, p("#ffe3a8", 0.85))
    B(kit, "liv.l", lx - 3.2, lx - 2.9, ly - 4.5, ly + 4.5, 0, 2.9, p("#ffe3a8", 0.85))
    B(kit, "liv.r", lx + 2.9, lx + 3.2, ly - 4.5, ly + 4.5, 0, 2.9, p("#ffe3a8", 0.85))
    B(kit, "liv.ceil", lx - 3.4, lx + 3.4, ly - 4.5, ly + 4.8, 2.9, 3.0, wall)
    B(kit, "liv.window", lx - 2.2, lx - 0.4, ly + 4.4, ly + 4.45, 1.0, 2.3, kit.emit("#dff4ff", 3.0, "livglass"))
    cs = p("#4aa7a0", 0.75, spec=0.05)
    B(kit, "liv.couch", lx - 1.2, lx + 1.6, ly + 3.55, ly + 4.4, 0.0, 0.5, cs, bevel=0.06)
    B(kit, "liv.couchback", lx - 1.3, lx + 1.7, ly + 4.2, ly + 4.45, 0.4, 1.15, cs, bevel=0.07)
    for sx in (-1.3, 1.55):
        B(kit, f"liv.coucharm{sx}", lx + sx - 0.12, lx + sx + 0.12, ly + 3.55, ly + 4.4, 0.0, 0.75, cs, bevel=0.06)
    LT(kit, "living", "main", "POINT", (lx, ly - 0.6, 2.6), 500.0, "#fff1d8", size=0.5)
    LT(kit, "living", "fill", "AREA", (lx, ly - 2.4, 1.8), 160.0, "#e8f0ff", size=2.0, shadow=False)
    kit.aim(kit.LIGHTS["living.fill"]["obj"], (lx, ly + 3.5, 0.8))
    # the dog, on the couch, facing -y
    brown, tan, blk = p("#b87a43", 0.8, spec=0.05), p("#e8c9a0", 0.8, spec=0.05), p("#14110f", 0.5)
    dx, dy = lx + 0.2, ly + 3.85
    dog = kit.empty("dog", (dx, dy, 0.5))
    kit.box("dog.body", (0.5, 0.7, 0.4), (0, 0.1, 0.2), brown, dog, bevel=0.07)
    kit.box("dog.chest", (0.34, 0.2, 0.3), (0, -0.2, 0.2), tan, dog, bevel=0.06)
    for sx in (-1, 1):
        kit.box(f"dog.fleg{sx}", (0.12, 0.14, 0.34), (sx * 0.14, -0.28, 0.0), brown, dog, bevel=0.04)
    head = kit.empty("dog.head", (0, -0.28, 0.58), dog)
    W["doghead"] = head
    kit.box("dog.skull", (0.38, 0.34, 0.34), (0, 0, 0.0), brown, head, bevel=0.1)
    kit.box("dog.snout", (0.22, 0.2, 0.17), (0, -0.2, -0.05), tan, head, bevel=0.06)
    kit.box("dog.nose", (0.09, 0.05, 0.06), (0, -0.31, -0.01), blk, head, bevel=0.02)
    for sx in (-1, 1):
        kit.box(f"dog.eye{sx}", (0.055, 0.03, 0.07), (sx * 0.1, -0.17, 0.07), blk, head)
        kit.box(f"dog.ear{sx}", (0.07, 0.15, 0.2), (sx * 0.215, 0.0, 0.1), p("#6e4020", 0.8, spec=0.05), head, rot=(0, sx * 0.25, 0), bevel=0.03)
    tailp = kit.empty("dog.tailp", (0, 0.45, 0.3), dog)
    W["dogtail"] = tailp
    kit.box("dog.tail", (0.1, 0.1, 0.4), (0, 0.0, 0.18), brown, tailp, bevel=0.04)


def build_lot(kit, m):
    ox, oy = G.LOT
    p = kit.plastic
    kit.plane("lot.ground", (200, 120), (ox, oy + 10, 0), p("#6b7186", 0.9, spec=0.05))
    kit.plane("lot.park", (30, 18), (ox, oy + 0.5, 0.01), p("#7b8196", 0.9, spec=0.05))
    for i in range(7):
        B(kit, f"lot.line{i}", ox - 9 + i * 3, ox - 8.9 + i * 3, oy - 3.5, oy + 4.0, 0.01, 0.02, p("#f4f0e0", 0.8))
    B(kit, "lot.curb", ox - 40, ox + 40, oy + 6.4, oy + 6.7, 0, 0.12, p("#d6d0c6", 0.9))
    brick = kit.bricks("#c0503f", "#ab4636", "#e6d8c6", 1.0)
    cream = p("#f6ead0", 0.7)
    # the facade: y = 10, with my window (x -0.8..0.8, z 7.9..9.5) three floors up
    X0, X1 = ox - 14, ox + 14
    def seg(n, xa, xb, za, zb):
        B(kit, f"lot.f{n}", xa, xb, oy + 9.8, oy + 10.2, za, zb, brick)
    seg("low", X0, X1, 0, 7.0)
    seg("l", X0, ox - 0.8, 7.0, 10.2)
    seg("r", ox + 0.8, X1, 7.0, 10.2)
    seg("sill", ox - 0.8, ox + 0.8, 7.0, 7.9)
    seg("head", ox - 0.8, ox + 0.8, 9.5, 10.2)
    seg("top", X0, X1, 10.2, 11.2)
    B(kit, "lot.parapet", X0 - 0.2, X1 + 0.2, oy + 9.7, oy + 10.4, 11.2, 11.6, cream)
    B(kit, "lot.sillstone", ox - 1.0, ox + 1.0, oy + 9.6, oy + 10.3, 7.8, 7.95, cream)
    for nm, a, b_, c, d in [("t", -0.9, 0.9, 9.5, 9.62), ("l", -0.9, -0.8, 7.9, 9.5), ("r", 0.8, 0.9, 7.9, 9.5)]:
        B(kit, f"lot.wfr{nm}", ox + a, ox + b_, oy + 9.62, oy + 9.8, c, d, m["white"])
    # other windows: some lit, most dark
    lit = kit.emit("#ffd98a", 2.2, "winlit")
    unlit = p("#2c3a66", 0.2, spec=0.6)
    k = 0
    for fz in (1.3, 4.1, 7.9):
        for wx in (-11, -8, -5, -2.5, 2.5, 5, 8, 11):
            if fz == 7.9 and abs(wx) < 3:
                continue
            ok = (k * 7 + int(fz)) % 4 == 0
            B(kit, f"lot.wa{k}", ox + wx - 0.75, ox + wx + 0.75, oy + 9.77, oy + 9.8, fz - 0.1, fz + 1.6, m["white"])
            B(kit, f"lot.wb{k}", ox + wx - 0.6, ox + wx + 0.6, oy + 9.75, oy + 9.77, fz, fz + 1.5, lit if ok else unlit)
            k += 1
    # the building's door and the buzzer panel
    B(kit, "lot.doorfr", ox + 3.3, ox + 5.1, oy + 9.7, oy + 9.8, 0, 2.5, m["white"])
    B(kit, "lot.door", ox + 3.45, ox + 4.95, oy + 9.62, oy + 9.7, 0, 2.35, p("#4a6fa5", 0.5, spec=0.3), bevel=0.02)
    B(kit, "lot.doorlite", ox + 3.7, ox + 4.7, oy + 9.58, oy + 9.62, 1.2, 2.1, kit.emit("#ffe2a8", 1.6, "doorlite"))
    B(kit, "lot.plate", ox + 5.3, ox + 5.85, oy + 9.65, oy + 9.8, 0.85, 1.75, p("#b9bfc9", 0.4, spec=0.6), bevel=0.02)
    for r in range(3):
        for c in range(2):
            kit.cyl(f"lot.btn{r}{c}", 0.075, 0.03, (ox + 5.43 + c * 0.2, oy + 9.62, 1.62 - r * 0.25), p("#f4f0e0", 0.4, spec=0.5),
                    rot=(math.pi / 2, 0, 0), n=14)
    kit.sphere("lot.led", 0.03, (ox + 5.58, oy + 9.6, 0.95), kit.emit("#7dffb0", 2.0), seg=6)
    # my room, behind the window
    ry = oy + G.ROOM_Y0
    rz = G.ROOM_Z
    rw = p("#e9dcc4", 0.85, spec=0.03)
    B(kit, "room.floor", ox - 3, ox + 3, ry - 0.2, ry + 5, rz - 0.2, rz, p("#a8845a", 0.7))
    B(kit, "room.back", ox - 3, ox + 3, ry + 4.8, ry + 5.0, rz, rz + 3.2, rw)
    B(kit, "room.l", ox - 3.2, ox - 3, ry - 0.2, ry + 5, rz, rz + 3.2, rw)
    B(kit, "room.r", ox + 3, ox + 3.2, ry - 0.2, ry + 5, rz, rz + 3.2, rw)
    B(kit, "room.ceil", ox - 3.2, ox + 3.2, ry - 0.2, ry + 5, rz + 3.2, rz + 3.4, rw)
    B(kit, "room.bed", ox + 1.4, ox + 2.95, ry + 2.6, ry + 4.75, rz, rz + 0.5, p("#7ea6d9", 0.8), bevel=0.05)
    B(kit, "room.pillow", ox + 1.5, ox + 2.85, ry + 4.1, ry + 4.7, rz + 0.5, rz + 0.62, m["white"], bevel=0.05)
    # the stove nook against the back wall, with the clock
    sx0 = ox - 2.7
    B(kit, "room.stove", sx0, sx0 + 1.5, ry + 4.1, ry + 4.8, rz, rz + 0.95, p("#d9dde3", 0.4, spec=0.5), bevel=0.03)
    B(kit, "room.stovetop", sx0, sx0 + 1.5, ry + 4.1, ry + 4.8, rz + 0.95, rz + 1.0, m["dark"])
    B(kit, "room.stovepanel", sx0, sx0 + 1.5, ry + 4.62, ry + 4.8, rz + 1.0, rz + 1.35, m["dark"])
    clk = kit.emit("#ff5a3c", 4.0, "clockred")
    for i, ch in enumerate("1100"):
        segs = seg_digit(kit, f"room.clk{i}", None, "xz", sx0 + 0.45 + i * 0.17 + (0.08 if i > 1 else 0), rz + 1.18, 0.1, 0.2,
                         0.028, 0.0, clk)
        for k2, ob in segs.items():
            ob.location.y = ry + 4.615
            ob.hide_render = k2 not in SEG[ch]
    for dz in (0.1, 0.28):
        kit.sphere(f"room.colon{dz}", 0.016, (sx0 + 0.45 + 0.17 + 0.085 + 0.0 + 0.08 * 0, ry + 4.61, rz + 1.1 + dz * 0.5), clk, seg=6)
    # a small table with the phone on my palm
    B(kit, "room.table", ox - 0.4, ox + 0.6, ry + 3.9, ry + 4.6, rz, rz + 0.62, p("#c49a68", 0.7))
    W["palm1"] = palm(kit, "palm1", (ox + 0.1, ry + 2.0, rz + 0.9), 0, "#d9a67a", phone="0")
    LT(kit, "lot", "roomlamp", "POINT", (ox + 0.2, ry + 1.8, rz + 2.6), 250.0, "#ffe0b0", size=0.4)
    LT(kit, "lot", "roomfill", "AREA", (ox, ry + 0.4, rz + 2.4), 90.0, "#dfe8ff", size=2.0, shadow=False)
    kit.aim(kit.LIGHTS["lot.roomfill"]["obj"], (ox, ry + 3.5, rz + 1.2))
    # the streetlight, behind the truck, and a cool fill from the building
    px, py = ox + 2.6, oy - 5.0
    steel = kit.metal("#6b7280", 0.5)
    kit.cyl("lot.pole", 0.08, 6.2, (px, py, 3.1), steel, n=10)
    B(kit, "lot.arm", px - 0.9, px + 0.05, py - 0.05, py + 0.05, 6.1, 6.2, steel)
    lamphead = kit.box("lot.lamphead", (0.6, 0.35, 0.12), (px - 0.9, py, 6.05), kit.emit("#ffb347", 5.0, "lamphead"))
    LT(kit, "lot", "street", "POINT", (px - 0.9, py, 5.8), 2300.0, "#ffb347", size=0.3)
    LT(kit, "lot", "fill", "AREA", (ox - 1.0, oy + 8.0, 6.0), 700.0, "#9db4ff", size=6.0, shadow=False)
    kit.aim(kit.LIGHTS["lot.fill"]["obj"], (ox, oy - 1.0, 1.0))
    LT(kit, "lot", "front", "AREA", (ox + 1.0, oy - 8.0, 3.5), 380.0, "#ffd9a0", size=4.0, shadow=False)
    kit.aim(kit.LIGHTS["lot.front"]["obj"], (ox, oy + 4.0, 1.5))
    # the phone Dad holds at my building (a lit screen on a flat palm)
    W["palm2"] = palm(kit, "palm2", (ox - 5.55, oy + 5.4, 1.05), 0, "#e0b088", phone="0")
    LT(kit, "lot", "phone", "POINT", (ox - 5.55, oy + 5.0, 1.4), 22.0, "#bfe3ff", size=0.1, shadow=False)
    # parked cars, far, dark
    for k, (cx, cy, cc) in enumerate([(-9.5, 3.2, "#445a8a"), (9.5, 2.6, "#3f6f5a"), (-13, -6, "#7a5a8a")]):
        B(kit, f"lot.pc{k}", ox + cx - 1.0, ox + cx + 1.0, oy + cy - 2.2, oy + cy + 2.2, 0.35, 1.2, p(cc, 0.4, spec=0.5), bevel=0.08)
        B(kit, f"lot.pcr{k}", ox + cx - 0.9, ox + cx + 0.9, oy + cy - 1.0, oy + cy + 0.9, 1.2, 1.85, p(cc, 0.4, spec=0.5), bevel=0.08)
    # distant houses across the street, windows lit
    for k in range(9):
        hx = ox - 60 + k * 15
        B(kit, f"lot.far{k}", hx - 4, hx + 4, oy - 48, oy - 41, 0, 4.5 + (k % 3), p(["#2b3a6e", "#33406e", "#3a3560"][k % 3], 0.8))
        B(kit, f"lot.farw{k}", hx - 1.0, hx + 1.0, oy - 41.1, oy - 41.0, 1.6, 2.6, kit.emit("#ffd98a", 1.6, "farwin") if k % 2 == 0 else m["dark"])
    # the pickup, parked nose toward the building, with the dark shape in its cab
    W["truck"] = vehicle(kit, m, "truck", (ox - 1.2, oy - 14.0, 0), 0.0, "#d8342e", pickup=True, glass=True, shape=True,
                         stage="lot", handle_marks=True)
    tree(kit, "lot.tree1", ox - 12, oy + 7.5, 6.0, "#9fc6a8")
    tree(kit, "lot.tree2", ox + 13, oy + 7.8, 6.5, "#9fc6a8")


def build_cab(kit, m):
    ox, oy = G.CAB
    cab_interior(kit, m, ox, oy)


def shop(kit, m, tag, ox, oy, night):
    """The auto shop and Dad's place over it. Its front wall is the plane y = oy; the lot is at y < oy. Local x is
    from -4.5 to 4.5; the apartment floor is at z = 3.2, the stair climbs left to right to the porch."""
    p = kit.plastic
    T = tag
    br = kit.bricks("#b8473a", "#a33d32", "#e6d8c6", 1.0)
    cream = p("#f6ecd6", 0.85, spec=0.03)
    gray = p("#8f9aa6", 0.6, spec=0.2)
    az = G.APT_Z
    top = 6.0
    X = lambda a: ox + a
    Y = lambda a: oy + a
    # ground ground
    kit.plane(f"{T}.lot", (90, 40), (ox, oy - 14, 0.012), p("#6e7488" if night else "#8c92a4", 0.9, spec=0.05))
    # ground floor: solid brick, the roll-up door at the right, a small window
    B(kit, f"{T}.gf", X(-4.5), X(4.5), Y(0), Y(7), 0, 3.0, br)
    B(kit, f"{T}.slab", X(-4.7), X(4.7), Y(-0.15), Y(7.2), 3.0, 3.2, cream)
    B(kit, f"{T}.dframe", X(1.3), X(4.3), Y(-0.1), Y(0), 0, 2.7, m["white"])
    for i in range(14):
        z = 0.1 + i * 0.185
        B(kit, f"{T}.slat{i}", X(1.4), X(4.2), Y(-0.16), Y(-0.1), z, z + 0.16, gray)
    B(kit, f"{T}.dhandle", X(2.6), X(2.9), Y(-0.2), Y(-0.16), 0.15, 0.25, m["dark"])
    # the apartment: walls (inside cream, the front veneered in brick)
    segs = [(-4.5, -3.5, az, top), (-3.5, -1.7, az, 4.4), (-3.5, -1.7, 5.6, top), (-1.7, 0.1, az, top),
            (0.1, 1.1, 5.4, top), (1.1, 4.5, az, top)]
    for i, (a, b_, za, zb) in enumerate(segs):
        B(kit, f"{T}.fw{i}", X(a), X(b_), Y(0), Y(0.2), za, zb, cream)
        B(kit, f"{T}.fv{i}", X(a), X(b_), Y(-0.05), Y(0), za, zb, br)
    for nm, a, b_, c, d in [("t", -3.65, -1.55, 5.6, 5.72), ("b", -3.65, -1.55, 4.28, 4.4), ("l", -3.65, -3.5, 4.4, 5.6),
                            ("r", -1.7, -1.55, 4.4, 5.6)]:
        B(kit, f"{T}.wfr{nm}", X(a), X(b_), Y(-0.09), Y(-0.05), c, d, m["white"])
    B(kit, f"{T}.sill", X(-3.8), X(-1.4), Y(-0.3), Y(0), 4.28, 4.36, m["white"])
    B(kit, f"{T}.back", X(-4.5), X(4.5), Y(6.8), Y(7.0), az, top, cream)
    B(kit, f"{T}.wl", X(-4.7), X(-4.5), Y(0), Y(7.0), az, top, cream)
    B(kit, f"{T}.wr", X(4.5), X(4.7), Y(0), Y(7.0), az, top, cream)
    B(kit, f"{T}.ceil", X(-4.7), X(4.7), Y(-0.15), Y(7.0), top, top + 0.2, cream)
    B(kit, f"{T}.roof", X(-4.9), X(4.9), Y(-0.5), Y(7.3), top + 0.2, top + 0.4, p("#5a3f33", 0.8))
    for nm, a, b_ in [("l", -4.7, -4.5), ("r", 4.5, 4.7)]:
        B(kit, f"{T}.vw{nm}", X(a), X(b_), Y(0), Y(0.2), az, top, br)
    kit.plane(f"{T}.afloor", (9.0, 6.8), (X(0), Y(3.4), az + 0.005), kit.planks("#c8a06c", "#b88f5a", 1.2))
    # the porch, rail and stair, the door
    B(kit, f"{T}.porch", X(-0.8), X(1.9), Y(-1.4), Y(0), 3.0, az, cream)
    B(kit, f"{T}.rail", X(-0.8), X(1.9), Y(-1.4), Y(-1.36), az + 0.9, az + 0.96, m["white"])
    B(kit, f"{T}.railr", X(1.86), X(1.9), Y(-1.4), Y(0), az + 0.9, az + 0.96, m["white"])
    for i in range(5):
        B(kit, f"{T}.rp{i}", X(-0.8 + i * 0.675), X(-0.76 + i * 0.675), Y(-1.4), Y(-1.36), az, az + 0.9, m["white"])
    n = 15
    for i in range(n):
        xa = -4.2 + i * 0.227
        zt = 0.2 * (i + 1)
        B(kit, f"{T}.st{i}", X(xa), X(xa + 0.24), Y(-1.35), Y(-0.45), 0, zt, p("#d8cdb8", 0.85))
    for i in range(0, n, 3):
        xa = -4.2 + i * 0.227
        B(kit, f"{T}.sp{i}", X(xa), X(xa + 0.04), Y(-1.38), Y(-1.34), 0.2 * (i + 1), 0.2 * (i + 1) + 0.9, m["white"])
    kit.box(f"{T}.srail", (4.0, 0.04, 0.05), (X(-2.2), Y(-1.36), 1.95), m["white"], rot=(0, -math.atan2(2.8, 3.2), 0))
    # the door frame: two jambs and a header (the doorway itself stays open)
    B(kit, f"{T}.djl", X(0.0), X(0.1), Y(-0.1), Y(0.2), az, 5.5, m["white"])
    B(kit, f"{T}.djr", X(1.1), X(1.2), Y(-0.1), Y(0.2), az, 5.5, m["white"])
    B(kit, f"{T}.djh", X(0.0), X(1.2), Y(-0.1), Y(0.2), 5.4, 5.5, m["white"])
    hinge = kit.empty(f"{T}.dhinge", (X(1.1), Y(0.1), az))
    kit.box(f"{T}.door", (1.0, 0.07, 2.1), (-0.5, 0, 1.05), p("#6fc7e8", 0.5, spec=0.3), hinge)
    kit.sphere(f"{T}.dknob", 0.05, (-0.85, -0.06, 1.0), m["chrome"], hinge, seg=8)
    W[f"{T}.door"] = hinge
    kit.box(f"{T}.porchlamp", (0.2, 0.12, 0.2), (X(1.55), Y(-0.1), az + 2.1), kit.emit("#ffe2a8", 3.0, "porchlamp"))
    LT(kit, "shop" if night else "day", f"{T}.porch", "POINT", (X(1.4), Y(-0.6), az + 1.9), 170.0, "#ffd98a", size=0.2,
       shadow=False)
    # the room's furniture, local floor z = az
    zz = az
    wood = p("#b98a58", 0.7, spec=0.1)
    kit.cyl(f"{T}.tabtop", 0.55, 0.06, (X(0.3), Y(3.8), zz + 0.87), wood, n=24)
    kit.cyl(f"{T}.tableg", 0.07, 0.85, (X(0.3), Y(3.8), zz + 0.43), wood, n=10)
    kit.cyl(f"{T}.tablefoot", 0.28, 0.04, (X(0.3), Y(3.8), zz + 0.02), wood, n=18)
    chairs = []
    for k, cx in enumerate((-0.15, 0.75)):
        B(kit, f"{T}.chs{k}", X(cx - 0.25), X(cx + 0.25), Y(4.55), Y(5.05), zz + 0.42, zz + 0.48, wood, bevel=0.02)
        B(kit, f"{T}.chb{k}", X(cx - 0.25), X(cx + 0.25), Y(5.0), Y(5.06), zz + 0.48, zz + 0.95, wood, bevel=0.02)
        for lx_, ly_ in [(-0.22, 4.58), (0.22, 4.58), (-0.22, 5.02), (0.22, 5.02)]:
            B(kit, f"{T}.chl{k}{lx_}{ly_}", X(cx + lx_ - 0.025), X(cx + lx_ + 0.025), Y(ly_ - 0.025), Y(ly_ + 0.025), zz, zz + 0.42, wood)
    couch = p("#e8a838", 0.75, spec=0.05)
    B(kit, f"{T}.couch", X(2.0), X(4.3), Y(5.6), Y(6.7), zz, zz + 0.5, couch, bevel=0.06)
    B(kit, f"{T}.couchback", X(2.0), X(4.3), Y(6.4), Y(6.72), zz + 0.4, zz + 1.15, couch, bevel=0.07)
    for sx in (2.0, 4.1):
        B(kit, f"{T}.couchar{sx}", X(sx), X(sx + 0.2), Y(5.6), Y(6.7), zz, zz + 0.75, couch, bevel=0.06)
    # kitchen nook on the left wall: counter, stove, pan, toaster
    cab = p("#8fd9c6", 0.5, spec=0.2)
    B(kit, f"{T}.kc", X(-4.5), X(-3.7), Y(3.0), Y(6.6), zz, zz + 0.9, cab, bevel=0.02)
    B(kit, f"{T}.kctop", X(-4.5), X(-3.65), Y(3.0), Y(6.6), zz + 0.9, zz + 0.95, m["white"], bevel=0.01)
    B(kit, f"{T}.stove", X(-4.45), X(-3.75), Y(3.1), Y(4.0), zz + 0.95, zz + 1.0, m["dark"])
    for k, yy in enumerate((3.35, 3.75)):
        kit.cyl(f"{T}.burner{k}", 0.1, 0.012, (X(-4.1), Y(yy), zz + 1.006), m["black"], n=14)
    pan = kit.empty(f"{T}.pan", (X(-3.98), Y(3.35), zz + 1.02))
    # a big pan, its handle out over the counter's edge toward the room (Dad holds it in S79), two fried eggs
    kit.cyl(f"{T}.pan.base", 0.2, 0.045, (0, 0, 0.022), m["black"], pan, n=24)
    kit.box(f"{T}.pan.handle", (0.44, 0.05, 0.03), (0.41, 0.0, 0.035), m["black"], pan)
    eggs_at = [(-0.075, 0.06), (0.07, -0.06)]
    egg = [kit.cyl(f"{T}.egg{k}", 0.088, 0.016, (dx_, dy_, 0.062), p("#fffdf6", 0.45), pan, n=18) for k, (dx_, dy_) in enumerate(eggs_at)]
    yolk = [kit.sphere(f"{T}.yolk{k}", 0.04, (dx_, dy_, 0.074), p("#ffb000", 0.35), pan, seg=10) for k, (dx_, dy_) in enumerate(eggs_at)]
    W[f"{T}.eggs"] = egg + yolk
    tst = kit.empty(f"{T}.toaster", (X(-3.92), Y(5.2), zz + 0.95))
    # a butter-yellow toaster, big enough to read in S80's close shot; its two slices burnt black
    kit.box(f"{T}.toaster.body", (0.36, 0.42, 0.25), (0, 0, 0.125), p("#f0b43c", 0.4, spec=0.3), tst, bevel=0.04)
    kit.box(f"{T}.toaster.lever", (0.06, 0.05, 0.05), (0.2, 0.12, 0.17), m["dark"], tst)
    toast = []
    crust = p("#6e3f18", 0.85, spec=0.05)
    burnt = p("#1a0f08", 0.9, spec=0.03)
    for k, dx_ in enumerate((-0.095, 0.095)):   # slots across, so S80's camera sees a slice face on
        ts = kit.box(f"{T}.toast{k}", (0.07, 0.26, 0.2), (dx_, 0, 0.2), crust, tst)
        for j, cy_ in enumerate((-0.065, 0.065)):   # the bread's rounded crown, two lobes on the top edge
            kit.cyl(f"{T}.toast{k}c{j}", 0.068, 0.07, (0, cy_, 0.1), crust, ts, rot=(0, math.pi / 2, 0), n=16)
        # the burnt face, a hair proud of the crust on both sides
        kit.box(f"{T}.toast{k}b", (0.09, 0.2, 0.16), (0, 0, 0.0), burnt, ts)
        for j, cy_ in enumerate((-0.058, 0.058)):
            kit.cyl(f"{T}.toast{k}bc{j}", 0.05, 0.09, (0, cy_, 0.09), burnt, ts, rot=(0, math.pi / 2, 0), n=16)
        toast.append(ts)
    W[f"{T}.toast"] = toast
    # jacket hook by the door
    kit.cyl(f"{T}.hook", 0.02, 0.1, (X(1.9), Y(0.35), zz + 1.7), m["chrome"], rot=(math.pi / 2, 0, 0), n=8)
    kit.box(f"{T}.jacket", (0.4, 0.1, 0.7), (X(1.9), Y(0.4), zz + 1.3), p("#8a5a34", 0.85), bevel=0.04)
    # plates of cold eggs on the table, a plant
    plates = []
    for k, cx in enumerate((-0.05, 0.65)):
        plates.append(kit.cyl(f"{T}.plate{k}", 0.17, 0.02, (X(cx), Y(3.95), zz + 0.92), m["white"], n=20))
        plates.append(kit.cyl(f"{T}.pegg{k}", 0.075, 0.014, (X(cx), Y(3.95), zz + 0.94), p("#fff6e6", 0.5), n=14))
        plates.append(kit.sphere(f"{T}.pyolk{k}", 0.03, (X(cx), Y(3.95), zz + 0.952), p("#e8a60e", 0.5), seg=8))
    W[f"{T}.plates"] = plates
    for pl in plates:
        pl.hide_render = True
    try:
        kit.prop("houseplant_1", (X(3.9), Y(2.2), zz), height=1.0, tint="#cfe8c0")
        kit.prop("bookshelf", (X(-1.0), Y(6.55), zz), rot=180, height=1.7, tint="#ffe3c0")
    except Exception:
        pass
    # dust on everything (hidden when Dad comes in): a gray film on the table, chairs, couch and floor, with specks
    dust = p("#8d8982", 0.97, spec=0.0)
    speck_l = p("#b4b0a8", 0.97, spec=0.0)
    speck_d = p("#6a665f", 0.97, spec=0.0)
    dl = []
    dl.append(kit.cyl(f"{T}.dust0", 0.52, 0.016, (X(0.3), Y(3.8), zz + 0.908), dust, n=22))
    for k, cx in enumerate((-0.15, 0.75)):
        dl.append(B(kit, f"{T}.dust1{k}", X(cx - 0.25), X(cx + 0.25), Y(4.55), Y(5.05), zz + 0.48, zz + 0.5, dust))
        dl.append(B(kit, f"{T}.dust1b{k}", X(cx - 0.25), X(cx + 0.25), Y(5.0), Y(5.06), zz + 0.95, zz + 0.97, dust))
    dl.append(B(kit, f"{T}.dust2", X(2.0), X(4.3), Y(5.6), Y(6.7), zz + 0.5, zz + 0.52, dust))
    dl.append(B(kit, f"{T}.dust2b", X(2.0), X(4.3), Y(6.4), Y(6.72), zz + 1.15, zz + 1.17, dust))
    dl.append(B(kit, f"{T}.dust3", X(-4.5), X(-3.65), Y(3.0), Y(6.6), zz + 0.95, zz + 0.97, dust))
    dl.append(B(kit, f"{T}.dust4", X(-2.6), X(-0.9), Y(1.4), Y(2.6), zz + 0.01, zz + 0.025, dust))
    dl.append(B(kit, f"{T}.dust5", X(1.2), X(3.2), Y(2.4), Y(3.6), zz + 0.01, zz + 0.025, dust))
    # specks and a few drifts, laid on the table top, the seats and the couch (deterministic)
    rnd = [0.5]

    def r():
        rnd[0] = (rnd[0] * 9301.0 + 49297.0) % 233280.0
        return rnd[0] / 233280.0
    spots = [(0.3, 3.8, zz + 0.925, 0.46, 0.46), (-0.15, 4.8, zz + 0.51, 0.22, 0.22), (0.75, 4.8, zz + 0.51, 0.22, 0.22),
             (3.15, 6.1, zz + 0.535, 1.0, 0.45), (3.15, 6.5, zz + 1.18, 1.0, 0.1)]
    n = 0
    for (cx, cy, cz, hx, hy) in spots:
        for _ in range(34 if hx > 0.3 else 12):
            sx_, sy_ = cx + (r() * 2 - 1) * hx, cy + (r() * 2 - 1) * hy
            sz_ = 0.01 + r() * 0.02
            dl.append(B(kit, f"{T}.speck{n}", X(sx_ - sz_), X(sx_ + sz_), Y(sy_ - sz_), Y(sy_ + sz_), cz, cz + 0.014,
                        speck_d if n % 3 == 0 else speck_l))
            n += 1
    W[f"{T}.dust"] = dl
    # the ceiling lamp: a fixed fitting
    gm = kit.emit("#fff0c8", 4.0, f"{T}.lampmat")
    W[f"{T}.lampmat"] = next(nn for nn in gm.node_tree.nodes if nn.type == "EMISSION")
    kit.cyl(f"{T}.lampcap", 0.18, 0.05, (X(0.3), Y(3.6), top - 0.025), m["white"], n=18)
    kit.sphere(f"{T}.lampglobe", 0.17, (X(0.3), Y(3.6), top - 0.2), gm, seg=12)
    if night:   # the lit window seen from the lot: a warm lamplit curtain just inside the glass (it follows the lamp)
        gl = kit.emit("#ffcf80", 1.3, f"{T}.winglowmat")
        W[f"{T}.winglow"] = next(nn for nn in gl.node_tree.nodes if nn.type == "EMISSION")
        noshadow(B(kit, f"{T}.winglow", X(-3.45), X(-1.75), Y(0.95), Y(1.0), 4.42, 5.58, gl))
    sky_stage = "shop" if night else "day"
    LT(kit, sky_stage, f"{T}.lamp", "POINT", (X(0.3), Y(3.6), top - 0.3), 330.0, "#ffd98a", size=0.25)
    LT(kit, sky_stage, f"{T}.roomfill", "AREA", (X(0.0), Y(0.6), top - 0.4), 120.0, "#dbe6ff" if night else "#fff6e6", size=3.0, shadow=False)
    kit.aim(kit.LIGHTS[f"{sky_stage}.{T}.roomfill"]["obj"], (X(0.0), Y(5.5), zz + 0.9))
    if night:
        LT(kit, "shop", "street", "SPOT", (X(-6.5), Y(-5.5), 6.2), 3200.0, "#ffb347", size=0.3, spot=60, blend=0.6)
        kit.aim(kit.LIGHTS["shop.street"]["obj"], (X(-2.6), Y(0.4), 4.7))
        LT(kit, "shop", "streetp", "POINT", (X(-6.0), Y(-5.2), 5.8), 1800.0, "#ffb347", size=0.3)
        LT(kit, "shop", "lotfill", "AREA", (X(1.0), Y(2.0), 8.0), 600.0, "#9db4ff", size=6.0, shadow=False)
        kit.aim(kit.LIGHTS["shop.lotfill"]["obj"], (X(0), Y(-7.0), 1.0))
        LT(kit, "shop", "front", "AREA", (X(1.0), Y(-14.0), 3.5), 360.0, "#ffd9a0", size=4.0, shadow=False)
        kit.aim(kit.LIGHTS["shop.front"]["obj"], (X(0), Y(-3.0), 2.0))
        px_, py_ = X(-6.5), Y(-5.5)
        kit.cyl("shop.pole", 0.08, 6.2, (px_, py_, 3.1), kit.metal("#6b7280", 0.5), n=10)
        kit.box("shop.lamphead", (0.6, 0.35, 0.12), (px_, py_, 6.15), kit.emit("#ffb347", 5.0, "lamphead2"))
        for k in range(8):
            hx = ox - 52 + k * 15
            B(kit, f"shop.far{k}", hx - 4, hx + 4, oy - 48, oy - 41, 0, 4.5 + (k % 3), p(["#2b3a6e", "#33406e", "#3a3560"][k % 3], 0.8))
            B(kit, f"shop.farw{k}", hx - 1.0, hx + 1.0, oy - 41.1, oy - 41.0, 1.6, 2.6, kit.emit("#ffd98a", 1.6, "farwin") if k % 2 == 0 else m["dark"])
        # Dad's pickup and my car, in the lot
        W["truck2"] = vehicle(kit, m, "truck2", (ox - 1.0, oy - 18.0, 0), 0.0, "#d8342e", pickup=True, glass=True, shape=False,
                              stage="shop")
        W["mycar"] = vehicle(kit, m, "mycar", (ox + 1.0, oy - 18.0, 0), 0.0, "#3d7bd9", pickup=False, glass=False, shape=False,
                             stage="shop")
    else:
        for k in range(6):
            hx = ox - 40 + k * 16
            B(kit, f"{T}.far{k}", hx - 4, hx + 4, oy - 48, oy - 41, 0, 4.5, p(["#ffd86b", "#8fe0c4", "#ff8a73"][k % 3], 0.8))


def build_shopin(kit, m):
    ox, oy = G.SHOPIN
    p = kit.plastic
    conc = p("#b9bcc4", 0.9, spec=0.03)
    kit.plane("sin.floor", (9, 8), (ox, oy + 3, 0.01), p("#9a9ea8", 0.9, spec=0.03))
    B(kit, "sin.back", ox - 4.5, ox + 4.5, oy + 6.5, oy + 6.8, 0, 3.0, p("#e9e0cc", 0.85))
    B(kit, "sin.l", ox - 4.7, ox - 4.4, oy - 4, oy + 6.8, 0, 3.0, p("#e9e0cc", 0.85))
    B(kit, "sin.r", ox + 4.4, ox + 4.7, oy - 4, oy + 6.8, 0, 3.0, p("#e9e0cc", 0.85))
    B(kit, "sin.ceil", ox - 4.7, ox + 4.7, oy - 4, oy + 6.8, 3.0, 3.2, p("#f1ead8", 0.85))
    couch = p("#4aa7a0", 0.75, spec=0.05)
    B(kit, "sin.couch", ox - 1.6, ox + 1.6, oy + 4.2, oy + 5.2, 0, 0.45, couch, bevel=0.06)
    B(kit, "sin.couchback", ox - 1.6, ox + 1.6, oy + 5.0, oy + 5.3, 0.4, 1.1, couch, bevel=0.07)
    for sx in (-1.7, 1.5):
        B(kit, f"sin.couchar{sx}", ox + sx, ox + sx + 0.2, oy + 4.2, oy + 5.2, 0, 0.7, couch, bevel=0.06)
    bl = p("#ff8a73", 0.9)   # the blanket: over his lap and up to his chin
    B(kit, "sin.blanket", ox - 0.78, ox + 0.78, oy + 4.42, oy + 4.56, 0.6, 1.14, bl, bevel=0.03)
    B(kit, "sin.blanket2", ox - 0.78, ox + 0.78, oy + 3.5, oy + 4.56, 0.7, 0.82, bl, bevel=0.03)
    B(kit, "sin.bench", ox + 2.6, ox + 4.3, oy + 5.2, oy + 6.2, 0, 0.95, p("#b98a58", 0.7))
    B(kit, "sin.tire", ox - 4.1, ox - 3.3, oy + 5.5, oy + 6.3, 0, 0.75, m["tire"])
    kit.cyl("sin.tire2", 0.38, 0.28, (ox - 3.7, oy + 5.9, 0.9), m["tire"], n=18)
    B(kit, "sin.jack", ox + 3.0, ox + 3.6, oy + 4.0, oy + 4.5, 0, 0.35, p("#e8a838", 0.6))
    kit.box("sin.lampfix", (0.4, 0.3, 0.1), (ox, oy + 3.0, 2.9), kit.emit("#ffe0b0", 3.0, "sinlamp"))
    LT(kit, "shopin", "lamp", "POINT", (ox, oy + 3.0, 2.7), 360.0, "#ffd9a0", size=0.4)
    LT(kit, "shopin", "fill", "AREA", (ox, oy + 0.5, 2.6), 160.0, "#dfe8ff", size=3.0, shadow=False)
    kit.aim(kit.LIGHTS["shopin.fill"]["obj"], (ox, oy + 4.6, 0.6))


STAGE_SKY = {"day": ("#8fd3ff", 1.0), "hall": ("#8fd3ff", 0.6), "kitchen": ("#8fd3ff", 0.6), "living": ("#8fd3ff", 0.6),
             "lot": ("#1d2a5c", 0.7), "cab": ("#16204a", 0.5), "shop": ("#1d2a5c", 0.7), "shopin": ("#16204a", 0.4)}


def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    m = M(kit)
    W["m"] = m
    build_day(kit, m)
    build_hall(kit, m)
    build_lot(kit, m)
    build_cab(kit, m)
    shop(kit, m, "shop", G.SHOP[0], G.SHOP[1], night=True)
    build_shopin(kit, m)
    for st_ in ("lot", "shop"):   # a cool fill that rides with Dad in the dark yard shots, so his hair and skin read
        LT(kit, st_, "dadfill", "AREA", (0, 0, 3.0), 140.0, "#e4ecff", size=1.6, shadow=False)
    build_ripple(kit)
    build_tag(kit)
    build_bezel(kit)
    return {}


# ---------------------------------------------------------------------------------------------- per frame
def _first_frame(kit, story):
    p = kit.plastic
    for sx_ in (-1, 1):
        sd = bpy.data.objects.get(f"dad.hside{sx_}")
        if sd is not None:   # gray temples, a little shorter so they read as hair, not ear flaps
            sd.scale = (1.0, 1.0, 0.8)
            sd.location.z += 0.05
    dh = bpy.data.objects.get("dad.headg")
    if dh is not None:
        g = p("#9a9aa2", 0.8)
        kit.box("dad.stache", (0.5, 0.06, 0.08), (0, -0.64, -0.11), g, dh, bevel=0.03)
    mh = bpy.data.objects.get("me.headg")
    if mh is not None:
        st = p("#2a2623", 0.9)
        kit.box("me.stubble", (0.5, 0.05, 0.1), (0, -0.62, -0.55), st, mh, bevel=0.03)
    W["inited"] = True


def _hide(ob, hide):
    ob.hide_render = hide
    for c in ob.children_recursive:
        c.hide_render = hide


def stage_at(story, tl, t):
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next((s for s in story["shots"] if s["id"] == shot["id"]), None)
    if not spec:
        return "day", shot, None
    k = spec["cam"][0][1]
    return G.stage_of(k[0], k[1]), shot, spec


def vehicle_cue(kit, tl, t, name, parts, base):
    c = sample(name, tl, t, {"x": base[0], "y": base[1], "yaw": (base[2] if len(base) > 2 else 0.0), "head": 0.0, "tail": 0.0, "door": 0.0, "shape": 0.0, "low": 0.0})
    root = parts["root"]
    root.location = (c["x"], c["y"], 0.0)
    root.rotation_euler = (0, 0, c["yaw"] * D2R)
    for ob in parts["heads"]:
        ob.hide_render = c["head"] < 0.05
    for ob in parts["tails"]:
        ob.hide_render = c["tail"] < 0.05
    parts["door"].rotation_euler = (0, 0, -c["door"] * 72 * D2R)
    kit.LIGHTS[parts["spot"]]["obj"].hide_render = c["head"] < 0.05
    sh = parts.get("shape")
    if sh is not None:
        _hide(sh, c["shape"] < 0.5)
        low = c["low"]
        parts["head"].location = (0, 0.28 * low, 1.72 - 0.58 * low)
        parts["head"].rotation_euler = (0.5 * low, 0, 0)
    return c


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    stage, shot, spec = stage_at(story, tl, t)
    gains = {n: (1.0 if s == stage else 0.0) for n, s in W["lights"].items()}
    # world
    skyc, skys = STAGE_SKY[stage]
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*kit_col(skyc), 1.0)
    bg.inputs["Strength"].default_value = skys
    # the day sun
    if stage == "day":
        gains["day.sun"] = 1.0
    # the apartment lamp (night copy): a fixed fitting switched on over its own ramp
    lamp = sample("lamp", tl, t, {"v": 1.0})
    gains["shop.shop.lamp"] = lamp["v"]
    gains["shop.shop.roomfill"] = sample("fill", tl, t, {"v": 1.0})["v"] * (1.0 if stage == "shop" else 0.0)
    W["shop.lampmat"].inputs["Strength"].default_value = 4.0 * lamp["v"]
    W["shop.winglow"].inputs["Strength"].default_value = 1.3 * lamp["v"]
    # my room lamp
    rl = sample("roomlamp", tl, t, {"v": 1.0})
    gains["lot.roomlamp"] = rl["v"]
    gains["lot.roomfill"] = 0.35 + 0.65 * rl["v"]
    # the cool fill that follows Dad (cue "dadfill": v and the offset from him)
    df = sample("dadfill", tl, t, {"v": 0.0, "ox": 0.0, "oy": -2.0, "oz": 2.0})
    dadob = bpy.data.objects.get("dad")
    for st_ in ("lot", "shop"):
        fl = kit.LIGHTS[f"{st_}.dadfill"]["obj"]
        gains[f"{st_}.dadfill"] = df["v"] if st_ == stage else 0.0
        if dadob is not None:
            dp = dadob.location
            fl.location = (dp.x + df["ox"], dp.y + df["oy"], dp.z + df["oz"])
            kit.aim(fl, (dp.x, dp.y, dp.z + 1.45))
    # dad's phone light
    ph = sample("phone", tl, t, {"v": 0.0})
    gains["lot.phone"] = ph["v"]
    pal = W["palm2"]
    _hide(pal, ph["v"] < 0.5)
    # the tag counter
    d = sample("days", tl, t, {"n": 731.0})
    set_tag_value(d["n"])
    # the tag sits at the top left at a fixed angular size
    lens = 40.0
    if spec:
        keys = spec["cam"]
        u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
        lens = keys[0][3]
        if len(keys) > 1:
            for a, b in zip(keys, keys[1:]):
                if u <= b[0]:
                    lens = a[3] + (b[3] - a[3]) * ss((u - a[0]) / max(1e-6, b[0] - a[0]))
                    break
            else:
                lens = keys[-1][3]
    dist = 1.0
    h2 = dist * 12.0 / lens
    w2 = h2 * 9.0 / 16.0
    s = 0.56 * w2
    td = 0.2
    th = td * 12.0 / lens
    tw = th * 9.0 / 16.0
    s = 0.56 * tw
    W["tag"].scale = (s, s, s)
    W["tag"].location = (-0.37 * tw, 0.6 * th, -td)
    bz = sample("bezel", tl, t, {"v": 0.0})
    W["bezel"].scale = (w2, h2, 1.0)
    W["bezel"].location = (0, 0, -0.95)
    _hide(W["bezel"], bz["v"] < 0.5)
    # the ripple
    ripple_at(tl, t)
    # the rule's door (night shop) and the day shop's door
    dr = sample("door", tl, t, {"v": 1.0})
    W["shop.door"].rotation_euler = (0, 0, -dr["v"] * 100 * D2R)
    W["dshop.door"].rotation_euler = (0, 0, -70 * D2R)
    # dust
    du = sample("dust", tl, t, {"v": 1.0})
    for ob in W["shop.dust"]:
        ob.hide_render = du["v"] < 0.5
    # the eggs, the plates, the toast
    eg = sample("eggs", tl, t, {"v": 0.0})
    for ob in W["shop.eggs"]:
        ob.hide_render = eg["v"] < 0.5
    pl = sample("plates", tl, t, {"v": 0.0})
    for ob in W["shop.plates"]:
        ob.hide_render = pl["v"] < 0.5
    ta = sample("toast", tl, t, {"v": 0.0})
    for k, ob in enumerate(W["shop.toast"]):
        ob.location.z = 0.2 + 0.1 * ta["v"]
        _hide(ob, ta["v"] < 0.02)
    # the dog
    dg = sample("dog", tl, t, {"v": 0.0})
    W["dogtail"].rotation_euler = (0, 0.55 * math.sin(t * 14.0) * dg["v"], 0)
    W["doghead"].rotation_euler = (0, 0, 0.08 * math.sin(t * 2.0) * dg["v"])
    # vehicles
    vehicle_cue(kit, tl, t, "truck", W["truck"], (G.LOT[0] - 1.2, G.LOT[1] - 14.0))
    vehicle_cue(kit, tl, t, "truck2", W["truck2"], (G.SHOP[0] - 1.0, G.SHOP[1] - 18.0))
    vehicle_cue(kit, tl, t, "mycar", W["mycar"], (G.SHOP[0] + 1.0, G.SHOP[1] - 18.0))
    vehicle_cue(kit, tl, t, "dcar", W["dcar"], (G.DAY_SHOP[0], 0.4, 90.0))
    # I ride along in a car that moves: the cue's offset is added to my root after the pose (no walking legs)
    rd = sample("ride", tl, t, {"dx": 0.0, "dy": 0.0, "on": 0.0})
    if rd["on"] > 0.5:
        me = bpy.data.objects.get("me")
        if me is not None:
            me.location.x += rd["dx"]
            me.location.y += rd["dy"]
    # the thermos in the cab is always there
    # who sits: legs straight out forward, hips on the seat
    sits = {}
    for c in tl["cues"]:
        if c["name"] == "sit" and c["t"] <= t:
            sits[c["who"]] = c
    for who, c in sits.items():
        root = bpy.data.objects.get(who)
        if c.get("on") and root is not None:
            root.location.z += c.get("z", 0.62) - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    return gains
