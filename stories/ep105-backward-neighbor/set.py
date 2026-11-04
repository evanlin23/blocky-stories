"""ep105 "backward neighbor": a bright suburban cul-de-sac (my pale blue house west, Vern's butter yellow house east, a
white picket fence between), and the rule meter: a cream flip-calendar tag in the top-left corner of every frame whose
five big seven-segment digits count Vern's days down from 10,950.

Everything the story moves is driven by cues in story.json (see animate): the look (sun, fill, sky), the season, the
maple, the fence, the mailbox flag, the porch calendar page and the day count, the photo wall, the moving boxes, the
truck, the doors, who sits and rocks, and a generic "vis" switch for single props. The tag is a child of the camera.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {"vis": {}}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def _L(**kw):
    base = dict(sun=3.4, sun_col="#fff0d8", el=48.0, az=-25.0, fill=0.9, fill_col="#fff0e0", sky="#8fd3ff", sky_str=1.0,
                front=0.0, room=1.0)
    base.update(kw)
    return base


LOOKS = {
    "day": _L(),
    "snow": _L(sun=3.0, sun_col="#f4f8ff", fill=1.2, fill_col="#e8f0ff", sky="#b8dcff", front=0.4),
    "storm": _L(sun=1.0, sun_col="#d8e0f0", el=60.0, fill=1.5, fill_col="#c8d4ea", sky="#8ea4c8", sky_str=0.85, front=0.5),
    "night": _L(sun=1.1, sun_col="#a8bcff", el=38.0, az=-40.0, fill=1.3, fill_col="#9cb0f0", sky="#3a4c92", sky_str=0.55,
                front=0.7),
    "dusk": _L(sun=1.8, sun_col="#ffb070", el=9.0, az=-70.0, fill=0.9, fill_col="#ffd2b0", sky="#f0a878", sky_str=0.8,
               front=0.9),
    "bluedusk": _L(sun=0.7, sun_col="#ff9a78", el=7.0, az=-70.0, fill=1.5, fill_col="#7e96e0", sky="#5668b0", sky_str=0.8,
                   front=0.9, room=2.4),
    "dayroom": _L(fill=1.5, room=7.0),
    "morning": _L(sun=3.0, sun_col="#ffe2b8", el=24.0, az=-60.0, fill=1.0, fill_col="#ffeedd", sky="#a8dcff", front=0.3),
}


def look_at(tl, t):
    cues = [c for c in tl["cues"] if c["name"] == "look"]
    cur = LOOKS[cues[0]["id"]] if cues else LOOKS["day"]
    prev = cur
    for c in cues:
        if c["t"] > t:
            break
        prev, cur = cur, LOOKS[c["id"]]
        dur = c.get("dur", 0.0)
        dur = 0.0 if dur <= 0 else max(0.4, dur)       # house bar: no switch faster than 0.3 s, unless set on a cut
        if t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            out = {}
            for k in cur:
                a, b = prev[k], cur[k]
                if isinstance(a, str):
                    ca, cb = kit_col(a), kit_col(b)
                    out[k] = tuple(ca[i] + (cb[i] - ca[i]) * u for i in range(3))
                else:
                    out[k] = a + (b - a) * u
            return out
    return {k: (kit_col(v) if isinstance(v, str) else v) for k, v in cur.items()}


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


# ---------------------------------------------------------------------------------------------- seven segments
SEGS = {0: "abcdef", 1: "bc", 2: "abdeg", 3: "abcdg", 4: "bcfg", 5: "acdfg", 6: "acdefg", 7: "abc", 8: "abcdefg",
        9: "abcdfg"}


def digits(kit, prefix, parent, mat, plane, dw, dh, th, pitch, xs, z):
    """Five seven-segment digit slots. plane 'xy' (the camera tag) or 'xz' (world). Returns a list of {seg: obj}."""
    slots = []
    for i, x in enumerate(xs):
        d = {}
        for seg in "abcdefg":
            if seg in "adg":
                size = (dw, th)
                cx = 0.0
                cy = {"a": dh / 2, "g": 0.0, "d": -dh / 2}[seg]
            else:
                size = (th, dh / 2 + th * 0.5)
                cx = (dw / 2) if seg in "bc" else (-dw / 2)
                cy = (dh / 4) if seg in "bf" else (-dh / 4)
            if plane == "xy":
                ob = kit.box(f"{prefix}{i}{seg}", (size[0], size[1], z), (x + cx, cy, z * 0.5 + 0.012), mat, parent)
            else:
                ob = kit.box(f"{prefix}{i}{seg}", (size[0], z, size[1]), (x + cx, 0.0, cy), mat, parent)
            d[seg] = ob
        slots.append(d)
    return slots


def show_number(slots, comma, n):
    n = max(0, int(n))
    s = str(n)
    s = s.rjust(len(slots))[-len(slots):]
    for d, ch in zip(slots, s):
        on = SEGS[int(ch)] if ch != " " else ""
        for seg, ob in d.items():
            ob.hide_render = seg not in on
    if comma is not None:
        comma.hide_render = n < 1000


# ---------------------------------------------------------------------------------------------- build helpers
def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def vis(name, *obs):
    W["vis"].setdefault(name, []).extend(obs)


def prism(kit, name, x0, x1, ys, zb, zt, mat):
    """A gable triangle prism: base from x0 to x1 at z = zb, apex at (x0 + x1) / 2, z = zt; spans y ys[0]..ys[1]."""
    xm = (x0 + x1) / 2
    y0, y1 = ys
    v = [(x0, y0, zb), (x1, y0, zb), (xm, y0, zt), (x0, y1, zb), (x1, y1, zb), (xm, y1, zt)]
    f = [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    return kit.mesh_obj(name, v, f, mat)


def house(kit, name, cx, cy, w, d, h, wall, roof, front=-1, hollow=None, lit=None, door_col="#e8553f", door_x=None,
          porch=True, far=False):
    """A small house: body w x d x h centred (cx, cy), gable roof over x, front wall facing -y."""
    pl = kit.plastic
    wm = pl(wall, 0.7, spec=0.1)
    fy = cy - d / 2
    if hollow is None:
        kit.box(f"{name}.body", (w, d, h), (cx, cy, h / 2), wm)
    else:
        ox0, ox1, oz0, oz1 = hollow            # the window opening in the front wall (x range, z range)
        t = 0.3
        kit.box(f"{name}.fl", (ox0 - (cx - w / 2), t, h), ((cx - w / 2 + ox0) / 2, fy + t / 2, h / 2), wm)
        kit.box(f"{name}.fr", ((cx + w / 2) - ox1, t, h), ((ox1 + cx + w / 2) / 2, fy + t / 2, h / 2), wm)
        kit.box(f"{name}.fb", (ox1 - ox0, t, oz0), ((ox0 + ox1) / 2, fy + t / 2, oz0 / 2), wm)
        kit.box(f"{name}.ft", (ox1 - ox0, t, h - oz1), ((ox0 + ox1) / 2, fy + t / 2, (oz1 + h) / 2), wm)
        # the cell behind the window: 3 m wide, 2.7 m deep; solid blocks fill the rest of the house
        cw = (ox1 + 1.0) - (cx - w / 2)
        kit.box(f"{name}.back", (w, d - 2.7 - t, h), (cx, fy + t + 2.7 + (d - 2.7 - t) / 2, h / 2), wm)
        kit.box(f"{name}.east", (w - cw, 2.7, h), (cx + w / 2 - (w - cw) / 2, fy + t + 1.35, h / 2), wm)
        kit.box(f"{name}.cfloor", (cw, 2.7, 0.06), (cx - w / 2 + cw / 2, fy + t + 1.35, 0.03), pl("#e8c89a", 0.7))
        kit.box(f"{name}.cceil", (cw, 2.7, 0.2), (cx - w / 2 + cw / 2, fy + t + 1.35, h - 0.1), pl("#fff4e0", 0.7))
        kit.box(f"{name}.cwall", (0.05, 2.7, 1.8), (cx - w / 2 + cw + 0.0 - 0.03 - 0.3, fy + t + 1.35, 1.6),
                pl("#5a5078", 0.7))
        kit.light(f"{name}.cell", "POINT", (cx - w / 2 + cw / 2, fy + t + 1.0, h - 0.6), 70.0, "#fff0d8", size=0.4, shadow=False)
    # roof
    run = w / 2 + 0.45
    th = 28 * D2R
    rise = run * math.tan(th)
    slope = run / math.cos(th)
    rm = pl(roof, 0.6, spec=0.1)
    for sx in (-1, 1):
        kit.box(f"{name}.roof{sx}", (slope, d + 0.8, 0.22), (cx + sx * run / 2, cy, h + rise / 2 + 0.05), rm,
                rot=(0, sx * th, 0))
    prism(kit, f"{name}.gable", cx - w / 2, cx + w / 2, (fy - 0.01, fy + 0.25), h, h + (w / 2) * math.tan(th), wm)
    # a chimney
    kit.box(f"{name}.chim", (0.7, 0.7, 1.4), (cx + w * 0.28, cy + 0.6, h + rise + 0.2), pl("#c4624a", 0.8))
    win = pl("#7fc8ff", 0.2, spec=0.8)
    frame = pl("#fffdf4", 0.6)
    glow = kit.emit("#ffd27a", 2.2, f"glow{name}")
    xs = [cx - w / 2 + 1.1, cx + w / 2 - 1.1] if hollow is None else [cx + w / 2 - 1.1]
    if door_x is None:
        door_x = cx
    lits = []
    for x in xs:
        if abs(x - door_x) < 1.4:
            continue
        kit.box(f"{name}.wf{x:.1f}", (1.5, 0.08, 1.4), (x, fy - 0.04, 1.7), frame)
        kit.box(f"{name}.wg{x:.1f}", (1.2, 0.06, 1.1), (x, fy - 0.08, 1.7), win)
        lits.append(kit.box(f"{name}.wl{x:.1f}", (1.2, 0.06, 1.1), (x, fy - 0.12, 1.7), glow))
        kit.box(f"{name}.wb{x:.1f}", (1.6, 0.3, 0.25), (x, fy - 0.2, 0.95), pl("#8a5a3a", 0.8))
        for k in range(4):
            kit.sphere(f"{name}.fl{x:.1f}{k}", 0.13, (x - 0.5 + k * 0.33, fy - 0.2, 1.17), pl(["#ff6a8a", "#ffd23f"][k % 2], 0.6),
                       seg=8)
    for ob in lits:
        ob.hide_render = True
    vis(f"lit_{name}", *lits)
    if porch:
        dm = pl(door_col, 0.5, spec=0.3)
        kit.box(f"{name}.dframe", (1.4, 0.06, 2.4), (door_x, fy - 0.03, 1.2), frame)
        door = kit.empty(f"{name}.door", (door_x - 0.55, fy - 0.12, 0))
        kit.box(f"{name}.leaf", (1.1, 0.1, 2.25), (0.55, 0, 1.15), dm, door)
        kit.sphere(f"{name}.knob", 0.06, (0.95, -0.08, 1.1), pl("#e3b04b", 0.3, spec=0.6), door, seg=8)
        W[f"{name}.door"] = door
        kit.box(f"{name}.dopen", (1.1, 0.02, 2.25), (door_x, fy - 0.075, 1.15), pl("#5a4030", 0.9))
        # porch deck, steps, awning
        kit.box(f"{name}.deck", (4.2, 2.0, 0.3), (door_x, fy - 1.0, 0.15), pl("#f2dcb4", 0.8))
        kit.box(f"{name}.step", (1.8, 0.7, 0.15), (door_x, fy - 2.35, 0.075), pl("#f2dcb4", 0.8))
        kit.box(f"{name}.step2", (2.0, 0.5, 0.15), (door_x, fy - 2.65, 0.0), pl("#e8d0a4", 0.8))
        for sx in (-1, 1):
            kit.box(f"{name}.post{sx}", (0.18, 0.18, 2.5), (door_x + sx * 2.5, fy - 1.85, 1.55), frame)
        kit.box(f"{name}.awn", (4.6, 2.3, 0.14), (door_x, fy - 1.0, 2.9), rm, rot=(-6 * D2R, 0, 0))
    return wm


def maple_parts(kit, parent, name):
    trunk = kit.plastic("#8a5a36", 0.8)
    kit.cyl(f"{name}.trunk", 0.32, 3.6, (0, 0, 1.8), trunk, parent, n=10, r2=0.22)
    for sx, rz, ln in [(-1, 28, 1.6), (1, -26, 1.5), (0, 0, 1.2)]:
        kit.cyl(f"{name}.br{sx}", 0.12, ln, (sx * 0.5, 0, 3.7), trunk, parent, rot=(0, rz * D2R, 0), n=8)
    groups = {}
    spots = [(0, 0, 5.2, 1.7), (-1.1, 0.2, 4.4, 1.25), (1.1, -0.1, 4.5, 1.3), (0.2, 0.9, 4.7, 1.1), (-0.3, -0.9, 4.9, 1.1)]
    for season, col in [("summer", "#4fc03a"), ("autumn", "#ff8c3a"), ("spring", "#ffb8d0"), ("winter", None)]:
        g = kit.empty(f"{name}.crown_{season}", (0, 0, 0), parent)
        if col is not None:
            mat = kit.plastic(col, 0.7, spec=0.1)
            for i, (x, y, z, r) in enumerate(spots):
                kit.sphere(f"{name}.{season}{i}", r, (x, y, z), mat, g, seg=10)
            if season == "spring":
                mat2 = kit.plastic("#8ee06a", 0.7, spec=0.1)
                for i, (x, y, z, r) in enumerate(spots[:3]):
                    kit.sphere(f"{name}.springg{i}", r * 0.7, (x * 1.1, y - 0.5, z - 0.5), mat2, g, seg=8)
        else:
            snow = kit.plastic("#f8fcff", 0.8, spec=0.1)
            for i, (x, y, z, r) in enumerate(spots[:3]):
                kit.box(f"{name}.twig{i}", (0.1, 0.1, 1.6), (x * 0.8, y, z - 0.6), trunk, g, rot=(0, x * 0.3, 0))
                kit.box(f"{name}.snow{i}", (0.7, 0.4, 0.12), (x * 0.8, y, z + 0.1), snow, g)
        groups[season] = g
    return groups


def tree(kit, name, x, y, h=6.0, tint="#cfe8c0"):
    try:
        kit.prop("commontree_1", (x, y, 0), height=h, tint=tint)
    except Exception:
        kit.cyl(f"{name}.trunk", 0.3, h * 0.45, (x, y, h * 0.22), kit.plastic("#7a5230", 0.8), n=8)
        kit.sphere(f"{name}.crown", h * 0.28, (x, y, h * 0.68), kit.plastic("#5fae4a", 0.8), seg=10)


def cardboard(kit, name, loc, size=(0.6, 0.5, 0.45), rot=0.0, parent=None, mark=True):
    b = kit.box(name, size, loc, kit.plastic("#d9a05a", 0.8, spec=0.05), parent, rot=(0, 0, rot * D2R), bevel=0.02)
    kit.box(f"{name}.tape", (0.1, size[1] + 0.02, size[2] + 0.02), (0, 0, 0), kit.plastic("#f4d8a0", 0.8), b)
    if mark:     # a plain glyph (a maple-orange disc) on the front face, no letters
        m = kit.plastic("#ff8c3a", 0.7)
        kit.cyl(f"{name}.m1", 0.1, 0.02, (0.0, -size[1] / 2 - 0.012, 0.0), m, b, rot=(math.pi / 2, 0, 0), n=16)
    return b


def fence(kit, parent, mat, y0, y1, step=0.32):
    n = int((y1 - y0) / step)
    for i in range(n + 1):
        y = y0 + i * step
        kit.box(f"pk{i}", (0.1, 0.07, 1.0), (0, y, 0.5), mat, parent, bevel=0.015)
        kit.box(f"pt{i}", (0.1, 0.07, 0.1), (0, y, 1.04), mat, parent, rot=(0, 0, 0.0), bevel=0.02)
    for z in (0.3, 0.75):
        kit.box(f"rail{z}", (0.06, y1 - y0 + 0.2, 0.08), (0.075, (y0 + y1) / 2, z), mat, parent)


def mailbox(kit, name, x, y, col):
    kit.box(f"{name}.post", (0.12, 0.12, 1.1), (x, y, 0.55), kit.plastic("#fffdf4", 0.6))
    kit.box(f"{name}.box", (0.38, 0.62, 0.34), (x, y, 1.3), kit.plastic(col, 0.5, spec=0.3), bevel=0.05)
    fl = kit.empty(f"{name}.flag", (x + 0.22, y - 0.05, 1.32))
    kit.box(f"{name}.flagarm", (0.05, 0.05, 0.4), (0, 0, 0.2), kit.plastic("#fffdf4", 0.5), fl)
    kit.box(f"{name}.flagtip", (0.05, 0.2, 0.12), (0, -0.08, 0.42), kit.plastic("#e8553f", 0.5), fl)
    return fl


def rocker(kit, name, x, y):
    g = kit.empty(name, (x, y, 0))
    wood = kit.plastic("#b87a4a", 0.7, spec=0.1)
    cush = kit.plastic("#ffd23f", 0.6)
    kit.box(f"{name}.seat", (0.8, 0.8, 0.1), (0, 0, 0.5), wood, g)
    kit.box(f"{name}.cush", (0.7, 0.7, 0.08), (0, 0, 0.58), cush, g)
    kit.box(f"{name}.back", (0.8, 0.1, 0.9), (0, 0.4, 0.95), wood, g, rot=(-0.12, 0, 0))
    for sx in (-1, 1):
        kit.box(f"{name}.arm{sx}", (0.1, 0.8, 0.08), (sx * 0.44, 0, 0.78), wood, g)
        kit.box(f"{name}.rk{sx}", (0.08, 1.1, 0.1), (sx * 0.4, 0, 0.06), wood, g)
        kit.box(f"{name}.lg{sx}", (0.08, 0.08, 0.5), (sx * 0.4, 0, 0.3), wood, g)
    return g


def photo(kit, name, cx, cy, z, w, h, young_hair, old_hair, truck=False, big=False, wallcol=None):
    """A framed picture on the +y wall (faces -y): two plain figures hugging. No letters."""
    y = cy
    fr = kit.plastic("#5a3420" if not big else "#e8a63a", 0.6)
    root = kit.empty(name, (0, 0, 0))
    kit.box(f"{name}.frame", (w + 0.16, 0.06, h + 0.16), (cx, y - 0.05, z), fr, root, bevel=0.015)
    kit.box(f"{name}.bg", (w, 0.03, h), (cx, y - 0.1, z), kit.plastic("#cfe8ff", 0.9), root)
    kit.box(f"{name}.grass", (w, 0.03, h * 0.28), (cx, y - 0.115, z - h * 0.36), kit.plastic("#7ed957", 0.9), root)
    s = h / 1.1
    k = 1.4 if big else 1.0
    if truck:
        kit.box(f"{name}.truck", (w * 0.45, 0.03, h * 0.5), (cx - w * 0.22, y - 0.13, z + h * 0.02), kit.plastic("#fafafa", 0.7), root)
    skin = kit.plastic("#e8bd98", 0.7)
    sp = 0.12 if big else 0.17
    zb = 0.25 if big else 0.2
    for who, dx, col, hc in [("a", -sp * w, "#5a82c0", young_hair), ("b", sp * w, "#3f9a92", old_hair)]:
        bx = cx + dx + (w * 0.12 if truck else 0)
        kit.box(f"{name}.{who}body", (0.2 * s * 1.1 * k, 0.03, 0.42 * s * k), (bx, y - 0.14, z - zb * s), kit.plastic(col, 0.7), root)
        kit.box(f"{name}.{who}head", (0.19 * s * 1.1 * k, 0.03, 0.19 * s * k), (bx, y - 0.15, z + 0.12 * s * k), skin, root)
        kit.box(f"{name}.{who}hair", (0.2 * s * 1.1 * k, 0.03, 0.08 * s * k), (bx, y - 0.165, z + 0.2 * s * k), kit.plastic(hc, 0.7), root)
        for ex in (-1, 1):
            kit.box(f"{name}.{who}eye{ex}", (0.025 * s * k, 0.02, 0.03 * s * k), (bx + ex * 0.04 * s * k, y - 0.18, z + 0.13 * s * k), kit.plastic("#1c120c", 0.6), root)
        kit.box(f"{name}.{who}smile", (0.06 * s * k, 0.02, 0.012 * s * k), (bx, y - 0.18, z + 0.07 * s * k), kit.plastic("#7a3a30", 0.6), root)
        if who == "b":
            gm = kit.plastic("#ff7a2a", 0.5)
            kit.box(f"{name}.{who}gl", (0.16 * s * k, 0.02, 0.025 * s * k), (bx, y - 0.19, z + 0.14 * s * k), gm, root)
            for ex in (-1, 1):
                kit.box(f"{name}.{who}gr{ex}", (0.06 * s * k, 0.02, 0.06 * s * k), (bx + ex * 0.04 * s * k, y - 0.195, z + 0.13 * s * k), gm, root)
    # the arms around each other: each one's arm wraps across the other's back
    mx = cx + (w * 0.12 if truck else 0)
    ax = 0.17 * s * k
    kit.box(f"{name}.hug", (2 * sp * w + 0.2 * s * 1.1 * k, 0.03, 0.08 * s * k), (mx, y - 0.16, z - 0.02 * s * k),
            kit.plastic("#5a82c0", 0.7), root)
    kit.box(f"{name}.hug2", (2 * sp * w + 0.1 * s * k, 0.03, 0.07 * s * k), (mx + ax * 0.2, y - 0.175, z - 0.1 * s * k),
            kit.plastic("#3f9a92", 0.7), root)
    return root


def noreflect():
    pass


# ---------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    pl = kit.plastic
    fenc = pl("#fafafa", 0.55, spec=0.2)

    # ------------------------------------------------------------------ lights (gains set in animate)
    sun = kit.light("sun", "SUN", (0, -30, 40), 1.0, "#fff0d8", size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#cfe6ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    front = kit.light("front", "SUN", (-10, -30, 20), 1.0, "#ffd2ae", shadow=False)
    front.data.angle = 0.4
    kit.aim(front, (0, 0, 0))
    rx, ry = G.ROOM
    kit.light("room", "POINT", (rx, ry - 0.5, 3.0), 150.0, "#ffe2b0", size=0.5, shadow=False)
    kit.light("room2", "POINT", (rx + 2.5, ry + 1.5, 2.2), 50.0, "#ffd49a", size=0.5, shadow=False)
    wx, wy = G.WED
    kit.light("wed", "POINT", (wx, wy - 3.0, 4.0), 260.0, "#fff0d8", size=0.5, shadow=False)
    bx_, by_ = G.BARB
    kit.light("barb", "POINT", (bx_, by_ - 2.5, 3.0), 300.0, "#fff0d8", size=0.5, shadow=False)
    gx, gy = G.GAR
    kit.light("gar", "POINT", (gx, gy - 2.5, 3.0), 300.0, "#fff0d8", size=0.5, shadow=False)
    kit.light("porchv", "POINT", (7.5, 4.3, 2.6), 90.0, "#ffd49a", size=0.4, shadow=False)
    kit.light("porchm", "POINT", (-7.5, 4.3, 2.6), 60.0, "#ffd49a", size=0.4, shadow=False)

    # ------------------------------------------------------------------ ground, seasons, street
    kit.plane("ground", (700, 700), (0, 0, -0.03), pl("#8fd96a", 0.9, spec=0.05))
    lawns = {}
    for season, col in [("summer", "#79d94f"), ("autumn", "#d9a63a"), ("winter", "#f6faff"), ("spring", "#8ee060")]:
        lawns[season] = kit.plane(f"lawn_{season}", (40, 18), (0, 1.0, 0.0), pl(col, 0.9, spec=0.05))
    W["lawns"] = lawns
    leaves = kit.empty("leaves", (0, 0, 0))
    lm = [pl("#ff8c3a", 0.8), pl("#e8553f", 0.8), pl("#ffd23f", 0.8)]
    for i in range(60):
        x = -13 + (i * 7.31) % 26
        y = -6 + (i * 3.77) % 9
        kit.box(f"leaf{i}", (0.28, 0.22, 0.015), (x, y, 0.02 + (i % 3) * 0.003), lm[i % 3], leaves, rot=(0, 0, i * 0.7))
    W["leaves"] = leaves
    kit.plane("street", (90, 8.0), (0, -12.0, 0.01), pl("#9aa4b4", 0.9, spec=0.05))
    kit.box("curb", (90, 0.35, 0.12), (0, -7.9, 0.06), pl("#e8e4da", 0.8))
    kit.plane("sidewalk", (60, 1.8), (0, -6.9, 0.03), pl("#e8e4da", 0.9))
    kit.plane("walkm", (1.4, 8.0), (-7.5, 1.6, 0.03), pl("#e8e4da", 0.9))
    kit.plane("walkv", (1.4, 8.0), (7.5, 1.6, 0.03), pl("#e8e4da", 0.9))
    kit.plane("drive", (4.4, 20.0), (G.DRIVE[0], -2.0, 0.025), pl("#b4bcc8", 0.9))
    for i in range(8):
        kit.box(f"dash{i}", (1.6, 0.14, 0.01), (-18 + i * 5.5, -12.0, 0.03), pl("#fff0a0", 0.8))

    # ------------------------------------------------------------------ the two houses
    house(kit, "mine", -7.5, 9.0, 7.0, 6.0, 3.6, "#a9d8ff", "#5a7ac0", hollow=(-10.1, -8.7, 1.0, 2.3), door_x=-6.0,
          door_col="#ffd23f")
    house(kit, "vern", 7.5, 9.0, 7.0, 6.0, 3.6, "#ffe58a", "#e8553f", door_x=7.5, door_col="#2f8f6f")
    # my window glass (a thin pane just in front of the opening)
    kit.box("mywin.cellback", (3.2, 0.04, 2.6), (-9.45, 8.95, 1.5), pl("#4a4670", 0.8))
    for sx in (-1, 1):
        kit.box(f"mywin.f{sx}", (0.1, 0.12, 1.4), (-9.4 + sx * 0.75, 5.88, 1.65), pl("#fffdf4", 0.6))
    for sz in (-1, 1):
        kit.box(f"mywin.h{sz}", (1.6, 0.12, 0.1), (-9.4, 5.88, 1.65 + sz * 0.7), pl("#fffdf4", 0.6))
    # far houses and trees for the reverse angles and the distance
    cols = ["#ffb7c5", "#c8f0a8", "#ffd8a0", "#b8e0ff", "#f4c8ff"]
    for i, x in enumerate(range(-52, 53, 13)):
        house(kit, f"far{i}", x, 40.0 + (i % 2) * 3, 8.0, 6.0, 4.0 + (i % 3) * 0.4, cols[i % 5], ["#c4624a", "#5a7ac0", "#6a8a5a"][i % 3],
              porch=False, far=True)
    for i, x in enumerate(range(-56, 57, 14)):
        house(kit, f"opp{i}", x + 3, -34.0 - (i % 2) * 2, 8.0, 6.0, 4.0 + (i % 3) * 0.4, cols[(i + 2) % 5],
              ["#c4624a", "#5a7ac0", "#6a8a5a"][i % 3], porch=False, far=True)
    for k, (x, y) in enumerate([(-16, 2), (16, 1), (-15, -9), (17, -10), (-26, 12), (27, 14), (-4, 24), (6, 26), (-18, -22),
                                (20, -24), (0, -26), (-30, -8), (31, -6)]):
        tree(kit, f"t{k}", x, y, 6.5 + (k % 3) * 0.6)

    # ------------------------------------------------------------------ the maple between the yards (grows)
    mp = kit.empty("maple", (G.MAPLE[0], G.MAPLE[1], 0))
    W["maple"] = mp
    W["crowns"] = maple_parts(kit, mp, "mpl")

    # ------------------------------------------------------------------ the fence (hinged on the ground, falls east)
    fn = kit.empty("fence", (0, 0, 0))
    fence(kit, fn, fenc, G.FENCE_Y[0], G.FENCE_Y[1])
    W["fence"] = fn
    # the lemonade on the fence, the hammer and nails
    lem = kit.empty("lemon", (0.0, -1.6, 1.12))
    kit.cyl("lemon.glass", 0.1, 0.24, (0, 0, 0.12), kit.glass("#f4fbff"), lem, n=14)
    kit.cyl("lemon.liq", 0.085, 0.18, (0, 0, 0.1), pl("#ffe04a", 0.4), lem, n=14)
    kit.cyl("lemon.pitch", 0.14, 0.32, (0.4, 0, 0.16), kit.glass("#f4fbff"), lem, n=14)
    kit.cyl("lemon.pliq", 0.12, 0.26, (0.4, 0, 0.13), pl("#ffe04a", 0.4), lem, n=14)
    vis("lemon", lem)
    ham = kit.empty("hammer", (-1.4, -1.6, 0.0))
    kit.box("ham.nails", (0.4, 0.3, 0.18), (0, 0, 0.09), pl("#d9a05a", 0.8), ham)
    kit.box("ham.handle", (0.07, 0.45, 0.06), (0.1, 0, 0.21), pl("#b87a4a", 0.7), ham)
    kit.box("ham.head", (0.2, 0.08, 0.1), (0.1, -0.22, 0.22), pl("#6a7080", 0.4, spec=0.5), ham)
    vis("hammer", ham)

    # ------------------------------------------------------------------ mailboxes, flag, chairs, calendar, chime
    W["flagv"] = mailbox(kit, "mboxv", G.MBOX_VERN[0], G.MBOX_VERN[1], "#2f8f6f")
    mailbox(kit, "mboxm", G.MBOX_ME[0], G.MBOX_ME[1], "#4f7ae0")
    ca = rocker(kit, "chairA", *G.CHAIR_A)
    cb = rocker(kit, "chairB", *G.CHAIR_B)
    W["chairA"], W["chairB"] = ca, cb
    kit.box("chairA.mark1", (0.03, 0.4, 0.02), (G.CHAIR_A[0] + 0.5, G.CHAIR_A[1], 0.8 + 0.0), pl("#ff8c3a", 0.6), ca)
    # two maple-orange strokes scratched into the arm of Vern's left rocking chair (the lore tally)
    for k in range(2):
        kit.box(f"chairA.stroke{k}", (0.035, 0.34, 0.02), (-0.44 + 0.0 + k * 0.06 - 0.0, 0.0, 0.84), kit.emit("#ffb050", 1.2, f"stroke{k}"), ca)
    kit.light("tallylamp", "POINT", (G.CHAIR_A[0] - 0.9, G.CHAIR_A[1] - 1.0, 1.4), 40.0, "#fff0d8", size=0.3, shadow=False)
    vis("chairs", ca, cb)
    cx, cy = G.CAL
    paper = pl("#f4ead2", 0.7)
    ink = pl("#3a2210", 0.6)
    red = pl("#e8553f", 0.6)
    cal = kit.empty("cal", (0, 0, 0))
    kit.cyl("cal.nail", 0.035, 0.2, (cx, cy - 0.03, 2.62), pl("#6a7080", 0.4, spec=0.5), cal, rot=(math.pi / 2, 0, 0), n=8)
    kit.box("cal.card", (1.5, 0.08, 1.2), (cx, cy - 0.07, 2.0), paper, cal, bevel=0.01)
    kit.box("cal.band", (1.5, 0.1, 0.3), (cx, cy - 0.075, 2.45), red, cal)
    wslots = digits(kit, "cald", cal, ink, "xz", 0.2, 0.55, 0.045, 0.26, [cx - 0.62 + 0.0, cx - 0.36, cx + 0.0 + 0.1, cx + 0.34 + 0.0,
                                                                          cx + 0.6 + 0.0], 0.02)
    for dsl in wslots:       # sit the digits proud of the card face (1 cm gap)
        for ob in dsl.values():
            ob.location = (ob.location.x, cy - 0.145, ob.location.z + 1.95 - 0.0)
    wcomma = kit.box("cal.comma", (0.05, 0.02, 0.1), (cx - 0.18 + 0.05, cy - 0.145, 1.78), ink, cal)
    W["wslots"], W["wcomma"] = wslots, wcomma
    hinge = kit.empty("cal.hinge", (cx, cy - 0.2, 2.62))
    kit.box("cal.page", (1.5, 0.05, 1.2), (0, 0, -0.6), paper, hinge, bevel=0.01)
    kit.box("cal.pband", (1.5, 0.07, 0.3), (0, -0.01, -0.17), red, hinge)
    W["calhinge"] = hinge
    vis("cal", cal, hinge)
    chime = kit.empty("chime", (G.CHAIR_B[0] + 0.5, 4.6, 2.75))
    W["chime"] = chime
    for k in range(5):
        kit.cyl(f"chime.t{k}", 0.025, 0.5 - 0.05 * k, (-0.25 + k * 0.125, 0, -0.35 - 0.25 + 0.05 * k), pl("#ffd23f", 0.3, spec=0.7), chime, n=8)
    kit.cyl("chime.top", 0.3, 0.04, (0, 0, -0.04), pl("#8a5a3a", 0.6), chime, n=14)

    # ------------------------------------------------------------------ the moving truck
    tr = kit.empty("truck", (G.DRIVE[0], G.DRIVE[1], 0))
    W["truck"] = tr
    wht = pl("#fafafa", 0.55, spec=0.3)
    kit.box("truck.cargo", (2.5, 5.4, 2.6), (0, 2.4, 1.9), wht, tr, bevel=0.05)
    kit.box("truck.cab", (2.3, 2.0, 1.9), (0, -1.1, 1.5), pl("#e8eef8", 0.5, spec=0.3), tr, bevel=0.1)
    kit.box("truck.glass", (2.0, 0.06, 0.8), (0, -2.12, 1.9), kit.glass("#9ad0ff"), tr)
    kit.box("truck.stripe", (2.52, 5.0, 0.18), (0, 2.4, 1.0), pl("#4f7ae0", 0.6), tr)
    for sx in (-1, 1):
        for yy in (-1.2, 3.4):
            kit.cyl(f"truck.w{sx}{yy}", 0.45, 0.3, (sx * 1.2, yy, 0.45), pl("#2a2d36", 0.7), tr, rot=(0, math.pi / 2, 0), n=16)
        kit.box(f"truck.h{sx}", (0.3, 0.08, 0.2), (sx * 0.85, -2.14, 0.85), kit.emit("#fff4c8", 2.0, "truckhead"), tr)
    td = kit.empty("truck.door", (-1.2, 5.12, 0.7), tr)
    kit.box("truck.doorleaf", (2.4, 0.1, 2.2), (1.2, 0.0, 1.1), wht, td)
    W["truckdoor"] = td
    kit.box("truck.ramp", (1.4, 1.4, 0.06), (0, 5.9, 0.05), pl("#c8cdd6", 0.6), tr, rot=(0.12, 0, 0))

    # ------------------------------------------------------------------ props that come and go
    cardboard(kit, "mv.b1", (-4.7, -2.7, 0.23), rot=14)
    cardboard(kit, "mv.b2", (-5.4, -3.0, 0.23), rot=-8)
    cardboard(kit, "mv.b3", (-5.05, -2.85, 0.68), (0.5, 0.45, 0.4), rot=5)
    vis("movebox", *[bpy.data.objects[n] for n in ("mv.b1", "mv.b2", "mv.b3")])
    pb = cardboard(kit, "pbox", (-5.0, 4.9, 0.45), (0.6, 0.5, 0.45), rot=-10)
    vis("porchbox", pb)
    for i in range(5):                      # tomorrow's tomatoes: green plants in my garden
        kit.cyl(f"tom{i}", 0.04, 0.9, (-2.6 - i * 0.5, 1.0, 0.45), pl("#3f9f3a", 0.8), n=6)
        kit.sphere(f"tomf{i}", 0.12, (-2.6 - i * 0.5, 0.9, 0.7), pl("#7fd04a", 0.6), seg=8)
        kit.sphere(f"tomg{i}", 0.2, (-2.6 - i * 0.5, 1.0, 0.95), pl("#4fb03a", 0.8), seg=8)
    try:
        cp = kit.prop("couch_medium1", (-8.3, -0.8, 0.4), rot=0, height=0.9, tint="#ffb0a0")
        vis("couch", cp)
    except Exception:
        cp = kit.box("couch", (2.0, 0.9, 0.8), (-8.3, -0.8, 0.8), pl("#ff8a7a", 0.7))
        vis("couch", cp)
    gr = kit.empty("bbq", (3.6, -2.4, 0))
    kit.cyl("bbq.bowl", 0.4, 0.3, (0, 0, 0.85), pl("#2a2d36", 0.5, spec=0.4), gr, n=14)
    for sx in (-1, 1):
        kit.box(f"bbq.leg{sx}", (0.06, 0.06, 0.8), (sx * 0.28, 0, 0.4), pl("#2a2d36", 0.5), gr)
    kit.box("bbq.table", (1.6, 0.8, 0.08), (-1.3, 0, 0.8), pl("#b87a4a", 0.7), gr)
    for sx in (-1, 1):
        kit.box(f"bbq.tleg{sx}", (0.08, 0.7, 0.8), (-1.3 + sx * 0.7, 0, 0.4), pl("#b87a4a", 0.7), gr)
    kit.cyl("bbq.plate", 0.2, 0.03, (-1.3, 0, 0.86), pl("#ff6a8a", 0.5), gr, n=14)
    vis("bbq", gr)

    # ------------------------------------------------------------------ Vern's living room (far east)
    wallp = kit.grime("#f4e4cc", 0.8, 2.0, "wallpaper", 0.9)
    kit.plane("rfloor", (12, 9), (rx, ry, 0.03), kit.planks("#c9976a", "#b78456", 1.0))
    kit.box("rback", (12, 0.3, 3.4), (rx, ry + 3.5, 1.7), wallp)
    for sx in (-1, 1):
        kit.box(f"rside{sx}", (0.3, 9, 3.4), (rx + sx * 6, ry, 1.7), wallp)
    # the window wall at y = -3, with a big window opening (x -2.5..2.5, z 0.9..2.6)
    kit.box("rfl", (3.5, 0.3, 3.4), (rx - 4.25, ry - 3.5, 1.7), wallp)
    kit.box("rfr", (3.5, 0.3, 3.4), (rx + 4.25, ry - 3.5, 1.7), wallp)
    kit.box("rfb", (5.0, 0.3, 0.9), (rx, ry - 3.5, 0.45), wallp)
    kit.box("rft", (5.0, 0.3, 0.8), (rx, ry - 3.5, 3.0), wallp)
    vis("rglass", kit.box("rglass", (5.0, 0.03, 1.7), (rx, ry - 3.4, 1.75), kit.glass("#e8f4ff")))
    for sx in (-1, 0, 1):
        kit.box(f"rwf{sx}", (0.1, 0.1, 1.8), (rx + sx * 2.5, ry - 3.4, 1.75), pl("#fffdf4", 0.6))
    kit.box("rwfh", (5.2, 0.1, 0.1), (rx, ry - 3.4, 2.6), pl("#fffdf4", 0.6))
    kit.box("rwfh2", (5.2, 0.1, 0.1), (rx, ry - 3.4, 0.9), pl("#fffdf4", 0.6))
    kit.box("rceil", (12, 9, 0.2), (rx, ry, 3.45), pl("#fff4e0", 0.8))
    kit.plane("rrug", (4.4, 2.8), (rx, ry + 0.4, 0.045), pl("#e8553f", 0.9))
    kit.plane("rrug2", (3.8, 2.2), (rx, ry + 0.4, 0.055), pl("#ffd23f", 0.9))
    try:
        kit.prop("couch_medium1", (rx + 3.6, ry + 2.2, 0), rot=180, height=0.9, tint="#7ab0e0")
    except Exception:
        kit.box("rcouch", (2.0, 0.9, 0.8), (rx + 3.6, ry + 2.4, 0.4), pl("#7ab0e0", 0.7))
    kit.box("rcab", (1.6, 0.5, 0.8), (rx - 3.8, ry + 3.1, 0.4), pl("#b87a4a", 0.7))
    rad = pl("#2f8f6f", 0.5, spec=0.3)
    kit.box("radio", (0.7, 0.3, 0.4), (rx - 3.8, ry + 3.05, 1.0), rad, bevel=0.04)
    kit.cyl("radio.d1", 0.1, 0.04, (rx - 3.95, ry + 2.88, 1.02), pl("#fff4c8", 0.4), rot=(math.pi / 2, 0, 0), n=14)
    kit.cyl("radio.d2", 0.07, 0.04, (rx - 3.62, ry + 2.88, 1.02), pl("#ffd23f", 0.4), rot=(math.pi / 2, 0, 0), n=14)
    kit.cyl("lampbase", 0.12, 0.8, (rx + 5.3, ry + 2.6, 0.4), pl("#b87a4a", 0.7), n=10)
    kit.cyl("lampshade", 0.3, 0.35, (rx + 5.3, ry + 2.6, 1.0), kit.emit("#ffd8a0", 0.5, "shade"), n=14, r2=0.2)
    # the photo wall: 9 frames (0 = the last one, big and central), the pale squares under them
    spots = [(0.0, 1.85, 1.5, 1.1), (-2.3, 2.15, 0.9, 0.7), (-1.15, 2.35, 0.8, 0.65), (1.15, 2.4, 0.8, 0.65),
             (2.3, 2.1, 0.9, 0.7), (-2.3, 1.1, 0.9, 0.7), (-1.15, 1.2, 0.8, 0.65), (1.15, 1.2, 0.8, 0.65),
             (2.3, 1.05, 0.9, 0.7)]
    hairs = [("#6a4228", "#c9c9d0"), ("#5a3a22", "#fafafa"), ("#7a5a3a", "#e0e0e6"), ("#6a4228", "#f4f4f4"),
             ("#5a3a22", "#9a9aa2"), ("#5a3a22", "#f4f4f4"), ("#6a4228", "#c9c9d0"), ("#7a5a3a", "#9a9aa2"),
             ("#5a3a22", "#e0e0e6")]
    pale = pl("#ffffff", 0.9)
    W["photos"] = []
    for i, (px, pz, pw, ph) in enumerate(spots):
        kit.box(f"pale{i}", (pw + 0.28, 0.02, ph + 0.28), (rx + px, ry + 3.33, pz), pale)
        sh = pl("#b8946a", 0.9)
        kit.box(f"pale{i}.top", (pw + 0.28, 0.02, 0.06), (rx + px, ry + 3.31, pz + (ph + 0.28) / 2 - 0.03), sh)
        kit.box(f"pale{i}.left", (0.06, 0.02, ph + 0.28), (rx + px - (pw + 0.28) / 2 + 0.03, ry + 3.31, pz), sh)
        g = photo(kit, f"photo{i}", rx + px, ry + 3.32, pz, pw * (0.8 if i == 0 else 1), ph * (0.8 if i == 0 else 1), hairs[i][0], hairs[i][1], truck=(i == 0), big=(i == 0))
        W["photos"].append(g)
    # boxes by the door (left wall), stacked as the days go
    W["rboxes"] = []
    for i, (bx, by, bz, sz) in enumerate([(-5.3, -1.6, 0.25, (0.8, 0.7, 0.5)), (-5.3, -0.7, 0.25, (0.8, 0.7, 0.5)),
                                          (-5.3, -1.6, 0.75, (0.7, 0.6, 0.5)), (-4.4, -1.4, 0.25, (0.7, 0.6, 0.5)),
                                          (-5.3, -0.7, 0.75, (0.7, 0.6, 0.5)), (-4.4, -0.5, 0.25, (0.7, 0.6, 0.5))]):
        W["rboxes"].append(cardboard(kit, f"rbox{i}", (rx + bx, ry + by, bz), sz, rot=i * 9))
    kit.box("rdoor", (0.1, 1.2, 2.3), (rx - 5.82, ry - 1.1, 1.15), pl("#2f8f6f", 0.5, spec=0.3))

    # ------------------------------------------------------------------ the garden wedding
    kit.plane("wfloor", (30, 20), (wx, wy, 0.0), pl("#79d94f", 0.9))
    kit.plane("waisle", (1.4, 8.0), (wx, wy - 1.5, 0.02), pl("#fff0d8", 0.9))
    try:
        kit.prop("commontree_1", (wx, wy + 5.5, 0), height=8.0, tint="#cfe8c0")
    except Exception:
        pass
    for sx in (-1, 1):
        kit.cyl(f"arch.p{sx}", 0.08, 2.6, (wx + sx * 1.1, wy + 1.8, 1.3), fenc, n=8)
        for k in range(5):
            kit.sphere(f"arch.f{sx}{k}", 0.16, (wx + sx * 1.1, wy + 1.7, 0.5 + k * 0.5), pl(["#ff6a8a", "#ffd23f", "#fff0f4"][k % 3], 0.6), seg=8)
    kit.box("arch.top", (2.4, 0.12, 0.12), (wx, wy + 1.8, 2.6), fenc)
    for k in range(7):
        kit.sphere(f"arch.t{k}", 0.15, (wx - 1.0 + k * 0.33, wy + 1.8, 2.7), pl(["#ff6a8a", "#fff0f4"][k % 2], 0.6), seg=8)
    for row in range(3):
        for sx in (-1, 1):
            for c in range(2):
                chx, chy = wx + sx * (1.4 + c * 0.8), wy - 0.8 - row * 1.4
                kit.box(f"wch{row}{sx}{c}", (0.6, 0.6, 0.1), (chx, chy, 0.5), pl("#fff4e0", 0.7))
                kit.box(f"wchb{row}{sx}{c}", (0.6, 0.08, 0.5), (chx, chy + 0.3, 0.8), pl("#fff4e0", 0.7))
                for xx in (-0.25, 0.25):
                    for yy in (-0.25, 0.25):
                        kit.box(f"wchl{row}{sx}{c}{xx}{yy}", (0.06, 0.06, 0.5), (chx + xx, chy + yy, 0.25), pl("#fff4e0", 0.7))

    # ------------------------------------------------------------------ the barbershop corner
    kit.plane("bfloor", (10, 7), (bx_, by_, 0.03), pl("#e8e4da", 0.8))
    kit.box("bback", (10, 0.3, 3.4), (bx_, by_ + 2.5, 1.7), kit.grime("#ffd9a8", 0.8, 2.0, "barbw", 0.9))
    kit.box("bmirror.f", (2.8, 0.08, 1.9), (bx_, by_ + 2.3, 1.7), pl("#e3b04b", 0.4, spec=0.5))
    kit.box("bmirror.g", (2.6, 0.04, 1.7), (bx_, by_ + 2.26, 1.7), kit.metal("#fbfbff", 0.03))
    kit.box("bchair.seat", (0.9, 0.9, 0.2), (bx_, by_ + 0.9, 0.5), pl("#e8553f", 0.5, spec=0.3))
    kit.box("bchair.back", (0.9, 0.2, 1.0), (bx_, by_ + 1.35, 1.0), pl("#e8553f", 0.5, spec=0.3))
    kit.cyl("bchair.base", 0.2, 0.4, (bx_, by_ + 0.9, 0.2), pl("#c8cdd6", 0.4, spec=0.6), n=12)
    for sx in (-1, 1):
        kit.box(f"bchair.arm{sx}", (0.14, 0.7, 0.14), (bx_ + sx * 0.5, by_ + 0.9, 0.78), pl("#c8cdd6", 0.4, spec=0.6))

    # ------------------------------------------------------------------ Vern's garage
    kit.plane("gfloor", (10, 7), (gx, gy, 0.03), pl("#b4bcc8", 0.9))
    kit.box("gback", (10, 0.3, 3.4), (gx, gy + 2.5, 1.7), pl("#ffe9b0", 0.8))
    kit.box("gshelf", (3.0, 0.5, 0.1), (gx - 2.5, gy + 2.2, 1.4), pl("#b87a4a", 0.7))
    for k in range(4):
        kit.box(f"gshelf.b{k}", (0.4, 0.3, 0.35), (gx - 3.4 + k * 0.6, gy + 2.2, 1.65), pl(["#ff6a8a", "#4f7ae0", "#ffd23f", "#2f8f6f"][k], 0.7))
    for sx in (-1, 1):
        kit.box(f"ladder.r{sx}", (0.06, 0.06, 2.4), (gx + 2.2 + sx * 0.22, gy + 2.1, 1.2), pl("#ffb040", 0.5), rot=(0, 0.1, 0))
    for k in range(7):
        kit.box(f"ladder.s{k}", (0.44, 0.05, 0.05), (gx + 2.2, gy + 2.1, 0.3 + k * 0.33), pl("#ffb040", 0.5))
    kit.box("peg.board", (2.4, 0.05, 1.7), (gx - 0.5, gy + 2.325, 1.35), pl("#c9a46c", 0.8))
    for k in range(6):
        for j in range(4):
            kit.box(f"peg.h{k}{j}", (0.04, 0.012, 0.04), (gx - 1.5 + k * 0.4, gy + 2.296, 0.75 + j * 0.42), pl("#7a5a38", 0.9))
    kit.box("peg.hamH", (0.07, 0.03, 0.55), (gx - 1.3, gy + 2.28, 1.55), pl("#8a5a3a", 0.7))
    kit.box("peg.hamD", (0.3, 0.04, 0.12), (gx - 1.3, gy + 2.28, 1.88), pl("#6a7080", 0.4, spec=0.5))
    kit.box("peg.sawB", (0.7, 0.03, 0.2), (gx - 0.3, gy + 2.28, 1.7), pl("#c8cdd6", 0.4, spec=0.5))
    kit.box("peg.sawH", (0.2, 0.04, 0.26), (gx + 0.15, gy + 2.28, 1.7), pl("#e8553f", 0.6))
    kit.box("peg.wrN", (0.08, 0.03, 0.6), (gx + 0.5, gy + 2.28, 1.45), pl("#6a7080", 0.4, spec=0.5))
    kit.box("peg.wrH", (0.22, 0.04, 0.16), (gx + 0.5, gy + 2.28, 1.82), pl("#6a7080", 0.4, spec=0.5))
    kit.box("gbucket", (0.5, 0.5, 0.5), (gx + 0.9, gy + 1.7, 0.28), pl("#e8553f", 0.6))
    cane = kit.empty("garcane", (gx - 0.5, gy + 2.1, 0))
    cm = pl("#b87a4a", 0.6)
    kit.cyl("garcane.shaft", 0.03, 1.25, (0, 0, 0.62), cm, cane, rot=(0, 0.2, 0), n=8)
    kit.cyl("garcane.crook", 0.045, 0.34, (-0.1, 0, 1.28), cm, cane, rot=(0, math.pi / 2, 0), n=8)
    kit.cyl("garcane.hook", 0.045, 0.22, (-0.27, 0, 1.16), cm, cane, n=8)
    dust = pl("#d8d0c4", 0.95)
    kit.box("garcane.dust", (0.08, 0.08, 0.5), (0.04, 0.0, 0.5), dust, cane, rot=(0, 0.2, 0))

    # ------------------------------------------------------------------ the rule meter: a plate on the camera
    build_tag(kit)
    return {}


def build_tag(kit):
    """The rule meter: a cream flip-calendar tag with a red band and five big seven-segment digits (a comma after the
    second). A child of the camera, top-left in every frame."""
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    cream = kit.emit("#fff6dc", 1.15, "tagcream")
    edge = kit.emit("#3a2210", 0.6, "tagedge")
    redm = kit.emit("#e8553f", 0.9, "tagred")
    inkm = kit.emit("#2a1408", 0.5, "taginkd")
    ringm = kit.emit("#fffaf0", 1.0, "tagring")

    def b(name, size, loc, mat):
        ob = kit.box(name, size, loc, mat, root)
        noshadow(ob)
        return ob
    b("tag.edge", (1.06, 0.7, 0.004), (0, 0, 0.0), edge)
    b("tag.plate", (1.0, 0.64, 0.004), (0, 0, 0.004), cream)
    b("tag.band", (1.0, 0.17, 0.004), (0, 0.235, 0.008), redm)
    for sx in (-1, 1):
        b(f"tag.ring{sx}", (0.06, 0.06, 0.004), (sx * 0.3, 0.235, 0.012), ringm)
    xs = [-0.43, -0.25, -0.02, 0.17, 0.36]
    slots = digits(kit, "tagd", root, inkm, "xy", 0.11, 0.36, 0.045, 0.18, xs, 0.004)
    for d in slots:
        for ob in d.values():
            ob.location = (ob.location.x, ob.location.y - 0.08, 0.013)
            noshadow(ob)
    comma = b("tag.comma", (0.045, 0.1, 0.004), (-0.135, -0.24, 0.013), inkm)
    W["tslots"], W["tcomma"] = slots, comma


def _first_frame(kit, story):
    """Boxes carried on a hip and Vern's cane, parented to the cast roots (rig units: the torso is 2 wide)."""
    pl = kit.plastic
    for who in story.get("cast", {}):
        root = bpy.data.objects.get(who)
        if root is None:
            continue
        if who in ("vern0", "vern0s"):
            cane = kit.empty(f"{who}.cane", (1.9, -0.5, 0.0), root)
            kit.cyl(f"{who}.caneshaft", 0.07, 3.4, (0, 0, 1.7), pl("#b87a4a", 0.6), cane, n=8)
            kit.cyl(f"{who}.canecrook", 0.1, 0.5, (-0.2, 0, 3.4), pl("#b87a4a", 0.6), cane, rot=(0, math.pi / 2, 0), n=8)
            vis(f"cane_{who}", cane)
        if who in ("me", "me3", "vern0", "vern4", "m1", "m2", "vern3"):
            box = kit.empty(f"{who}.cbox", (0, -1.7, 2.7), root)
            kit.box(f"{who}.cboxb", (1.8, 1.4, 1.4), (0, 0, 0), pl("#d9a05a", 0.8, spec=0.05), box, bevel=0.05)
            kit.box(f"{who}.cboxt", (0.3, 1.42, 1.42), (0, 0, 0), pl("#f4d8a0", 0.8), box)
            vis(f"carry_{who}", box)
    me_ = bpy.data.objects.get("me")
    if me_ is not None:
        tb = kit.empty("me.tbrush", (1.1, -1.35, 3.0), me_)
        kit.cyl("me.tb.cup", 0.42, 0.8, (0, 0, 0), pl("#fafafa", 0.5), tb, n=14)
        kit.cyl("me.tb.tea", 0.34, 0.04, (0, 0, 0.39), pl("#8a4a22", 0.5), tb, n=14)
        kit.box("me.tb.handle", (0.14, 0.16, 0.5), (0.5, 0, 0.0), pl("#fafafa", 0.5), tb)
        kit.box("me.tb.band", (0.86, 0.86, 0.14), (0, 0, 0.1), pl("#4f7ae0", 0.5), tb)
        vis("tb_me", tb)
    g1 = bpy.data.objects.get("me3.gl1")
    if g1 is not None:        # me at 56: plain clear lenses with red rims, so they never read as sunglasses
        hgp = g1.parent
        rim = pl("#d8452f", 0.4)
        for sx in (-1, 1):
            bpy.data.objects[f"me3.gl{sx}"].hide_render = True
            kit.box(f"me3.rimb{sx}", (0.46, 0.04, 0.05), (sx * 0.24, -0.67, -0.19), rim, hgp)
            for ex in (-1, 1):
                kit.box(f"me3.rims{sx}{ex}", (0.05, 0.04, 0.32), (sx * 0.24 + ex * 0.21, -0.67, -0.02), rim, hgp)
    nr = bpy.data.objects.get("nora2")
    if nr is not None:
        cm = kit.empty("nora2.cam", (0, -1.6, 3.7), nr)
        kit.box("nora2.cam.body", (1.3, 0.7, 0.9), (0, 0, 0), pl("#2a2d36", 0.5, spec=0.3), cm, bevel=0.05)
        kit.cyl("nora2.cam.lens", 0.28, 0.4, (0, -0.5, 0), pl("#8a96b0", 0.3, spec=0.7), cm, rot=(math.pi / 2, 0, 0), n=14)
        vis("cam_nora", cm)
    W["inited"] = True


def _hide(ob, hide):
    ob.hide_render = hide
    for c in ob.children_recursive:
        c.hide_render = hide


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    look = look_at(tl, t)
    gains = {}
    az, el = look["az"] * D2R, look["el"] * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    so = kit.LIGHTS["sun"]["obj"]
    so.location = d * 60
    kit.aim(so, (0, 0, 0))
    kit.LIGHTS["sun"]["light"].color = look["sun_col"]
    kit.LIGHTS["fill"]["light"].color = look["fill_col"]
    gains["sun"], gains["fill"], gains["front"] = look["sun"], look["fill"], look["front"]
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*look["sky"], 1.0)
    bg.inputs["Strength"].default_value = look["sky_str"]
    night = 1.0 if (tl["cues"] and look["sky_str"] < 0.7) else 0.0
    gains["room"] = gains["room2"] = look["room"]
    gains["tallylamp"] = 0.0
    gains["porchv"] = 1.0 if night else 0.0
    gains["porchm"] = 1.0 if night else 0.0

    # the season: lawn, leaves, the maple's crown
    seasons = [c for c in tl["cues"] if c["name"] == "season" and c["t"] <= t]
    season = seasons[-1]["id"] if seasons else "summer"
    for k, ob in W["lawns"].items():
        ob.hide_render = k != season
    W["leaves"].hide_render = season != "autumn"
    for k, g in W["crowns"].items():
        _hide(g, k != season)
    mp = sample("maple", tl, t, {"s": 1.0, "bend": 0.0})
    W["maple"].scale = (mp["s"], mp["s"], mp["s"])
    wind = 0.0
    if look["sky_str"] < 0.9 and look["sun"] < 1.5 and look["sky"][2] > 0.4:      # the storm look
        wind = 0.09 * math.sin(t * 7.0)
    W["maple"].rotation_euler = (wind, mp["bend"] * D2R + wind * 0.4, 0)
    # the fence falls east and stands again
    fe = sample("fence", tl, t, {"v": 0.0})
    W["fence"].rotation_euler = (0, fe["v"] * 86 * D2R, 0)
    fl = sample("flag", tl, t, {"v": 0.0})
    W["flagv"].rotation_euler = (-(1.0 - fl["v"]) * 85 * D2R, 0, 0)
    # the calendar page, and the day count on the porch card and on the tag
    pg = sample("flip", tl, t, {"v": 1.0})
    W["calhinge"].rotation_euler = (-pg["v"] * 175 * D2R, 0, 0)
    ct = sample("count", tl, t, {"n": 10950.0})
    # the tag sits in the top-left corner at a fixed angular size, whatever the lens
    lens = 40.0
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next((s for s in story["shots"] if s["id"] == shot["id"]), None)
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
    s = 0.8 * w2
    W["tag"].scale = (s, s, s)
    W["tag"].location = (-0.55 * w2, 0.8 * h2, -dist)
    # photos, boxes, doors, truck
    ph = sample("photos", tl, t, {"n": 9.0})
    for i, g in enumerate(W["photos"]):
        _hide(g, i >= round(ph["n"]))
    bxs = sample("rboxes", tl, t, {"n": 0.0})
    for i, b in enumerate(W["rboxes"]):
        _hide(b, i >= round(bxs["n"]))
    tk = sample("truck", tl, t, {"y": 0.0, "vis": 1.0})
    W["truck"].location = (G.DRIVE[0], G.DRIVE[1] + tk["y"], 0)
    _hide(W["truck"], tk["vis"] < 0.5)
    W["truckdoor"].rotation_euler = (0, 0, sample("truckdoor", tl, t, {"a": 0.0})["a"] * D2R)
    W["mine.door"].rotation_euler = (0, 0, -sample("mydoor", tl, t, {"a": 0.0})["a"] * D2R)
    W["vern.door"].rotation_euler = (0, 0, -sample("vdoor", tl, t, {"a": 0.0})["a"] * D2R)
    # glowing windows at night
    nl = 1.0 if night else 0.0
    for nm in ("lit_mine", "lit_vern"):
        for ob in W["vis"].get(nm, []):
            ob.hide_render = nl < 0.5
    # generic prop switches: cue "vis" with obj and on
    state = {}
    for c in tl["cues"]:
        if c["name"] == "vis" and c["t"] <= t:
            state[c["obj"]] = c.get("on", True)
    for nm, obs in W["vis"].items():
        if nm.startswith("lit_"):
            continue
        on = state.get(nm, nm in ("cal", "chairs", "rglass"))
        for ob in obs:
            _hide(ob, not on)
    if state.get("tallylamp"):
        gains["tallylamp"] = 1.0
    show_number(W["tslots"], W["tcomma"], round(ct["n"]))
    show_number(W["wslots"], W["wcomma"], round(ct["n"]))
    if not state.get("cal", True):          # the porch card is off: its digits must go too (show_number just lit them)
        for dsl in W["wslots"]:
            for ob in dsl.values():
                ob.hide_render = True
        W["wcomma"].hide_render = True
    # the wind chime and the rocking chairs
    W["chime"].rotation_euler = (0.12 * math.sin(t * 2.3), 0.1 * math.sin(t * 1.7 + 1), 0)
    rocks = {}
    for c in tl["cues"]:
        if c["name"] == "rock" and c["t"] <= t:
            rocks[c["who"]] = c
    rk = 0.09 * math.sin(t * 2.6)
    W["chairA"].rotation_euler = (0, 0, 0)
    W["chairB"].rotation_euler = (0, 0, 0)
    # who sits: legs straight out forward, hips on the seat (and rocking if asked)
    sits = {}
    for c in tl["cues"]:
        if c["name"] == "sit" and c["t"] <= t:
            sits[c["who"]] = c
    for who, c in sits.items():
        root = bpy.data.objects.get(who)
        if c.get("on") and root is not None:
            root.location.z += c.get("z", 0.56) - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
            if who in rocks and rocks[who].get("on"):
                root.rotation_euler.x += rk
                ch = W.get(c.get("chair", "chairA"))
                if ch is not None:
                    ch.rotation_euler = (rk, 0, 0)
    return gains
