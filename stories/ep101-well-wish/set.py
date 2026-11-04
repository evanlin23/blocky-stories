"""ep101 "well wish": a sunny brick town square with a round stone well, a hilly street, and the rule meter: a cream
tag in the top-left corner of every frame (a road glyph and a bar that fills toward a red notch at one block; past the
town line it turns into a climbing mile count).

Everything the story moves is driven by cues in story.json (see animate): the look, the meter, the coin and its ripples,
the car and the bus, who sits, what Wes and I carry, the bedroom window's season, the clock, the door. The tag is a child
of the camera, and a second copy stands in the world for the close-ups.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def _L(**kw):
    base = dict(sun=3.4, sun_col="#fff0d8", el=45.0, az=-25.0, fill=0.9, fill_col="#fff0e0", sky="#8fd3ff", sky_str=1.0,
                front=0.0, lamp=0.0, hall=1.0)
    base.update(kw)
    return base


LOOKS = {
    "day": _L(),
    "dusk": _L(sun=1.8, sun_col="#ffb070", el=12.0, az=-60.0, fill=1.0, fill_col="#ffd9c0", sky="#ffb48a", sky_str=0.9,
               front=1.3, lamp=0.6),
    "night": _L(sun=0.9, sun_col="#9ab8ff", el=50.0, az=30.0, fill=1.0, fill_col="#b8c8ff", sky="#2b3d7a", sky_str=0.8,
                front=1.2, lamp=1.0, hall=0.35),
    "dawn": _L(sun=2.6, sun_col="#ffd2a0", el=14.0, az=-70.0, fill=1.1, fill_col="#ffe0c0", sky="#ffd7a8", sky_str=0.9,
               front=1.4),
    "snow": _L(sun=2.2, sun_col="#f4f6ff", el=40.0, az=-25.0, fill=1.1, fill_col="#e8f0ff", sky="#dbe7f3", sky_str=1.0),
    "sunrise": _L(sun=3.0, sun_col="#ffc890", el=8.0, az=170.0, fill=1.0, fill_col="#ffd9b8", sky="#ffb98a", sky_str=1.0,
                  front=0.6),
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


def last_cue(name, tl, t):
    cs = [c for c in tl["cues"] if c["name"] == name and c["t"] <= t]
    return cs[-1] if cs else None


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def set_emit(mat, hexc):
    mat.node_tree.nodes["Emission"].inputs["Color"].default_value = (*kit_col(hexc), 1.0)


def _hide(ob, hide):
    ob.hide_render = hide
    for c in ob.children_recursive:
        c.hide_render = hide


# ---------------------------------------------------------------------------------------------- build helpers
def house_x(kit, name, x, y, wx, wy, h, col, face=+1, roof="#c4624a", win=True):
    """A painted house whose front (windows) faces +x (face=+1) or -x (face=-1)."""
    wall = kit.grime(col, 0.9, 2.0, f"wall{col}", 0.9)
    kit.box(f"{name}.body", (wx, wy, h), (x, y, h / 2), wall)
    kit.box(f"{name}.roof", (wx + 0.6, wy + 0.6, 0.5), (x, y, h + 0.25), kit.plastic(roof, 0.7, spec=0.1))
    kit.box(f"{name}.roof2", (wx * 0.5, wy * 0.7, 0.5), (x, y, h + 0.7), kit.plastic(roof, 0.7, spec=0.1))
    if not win:
        return
    fx = x + face * (wx / 2)
    glass = kit.plastic("#5f8fb8", 0.2, spec=0.8)
    fr = kit.plastic("#fff4e0", 0.7)
    n = max(1, int(wy // 3.0))
    for i in range(n):
        wy_ = y - wy / 2 + (i + 0.5) * wy / n
        for wz in ([1.6, 3.8] if h > 4.8 else [1.9]):
            kit.box(f"{name}.win{i}_{wz}", (0.1, 1.0, 1.2), (fx + face * 0.03, wy_, wz), glass)
            kit.box(f"{name}.frame{i}_{wz}", (0.08, 1.3, 1.5), (fx + face * 0.015, wy_, wz), fr)


def tree(kit, name, x, y, h=5.0, tint="#cfe8c0", prop="commontree_1"):
    try:
        kit.prop(prop, (x, y, 0), height=h, tint=tint)
    except Exception:
        kit.cyl(f"{name}.trunk", 0.3, h * 0.45, (x, y, h * 0.22), kit.plastic("#7a5230", 0.8), n=8)
        kit.sphere(f"{name}.crown", h * 0.28, (x, y, h * 0.68), kit.plastic("#5fae4a", 0.8), seg=10)


def street(kit, name, ox, oy, y0, y1, snow=False, ours=False, wall_cols=None, skip_w=(), skip_tw=()):
    """A north-south street centred at x=ox: road, curbs, sidewalks, lawns, houses on both sides."""
    p = kit.plastic
    L = y1 - y0
    cy = (y0 + y1) / 2
    road = p("#6b6f78", 0.9, spec=0.05)
    kit.plane(f"{name}.road", (6.0, L), (ox, cy, 0.03), road)
    for k in range(int(L // 4)):
        yy = y0 + 2 + k * 4
        kit.box(f"{name}.dash{k}", (0.14, 1.6, 0.02), (ox, yy, 0.045), p("#ffd23f", 0.6))
    for sg in (-1, 1):
        kit.box(f"{name}.curb{sg}", (0.3, L, 0.16), (ox + sg * 3.15, cy, 0.08), p("#d8d0c0", 0.8, spec=0.05))
        kit.plane(f"{name}.walk{sg}", (3.0, L), (ox + sg * 4.8, cy, 0.05), p("#f0e8d8" if not snow else "#f4f8ff", 0.9, spec=0.05))
        kit.plane(f"{name}.lawn{sg}", (7.0, L), (ox + sg * 9.8, cy, 0.02), p("#6cc24a" if not snow else "#f4f8ff", 0.9, spec=0.05))
    cols = wall_cols or ["#9fe0c0", "#ffe38a", "#8fd3ff", "#ffb0a0", "#d8c0f0"]
    ys = [y for y in range(int(y0) + 8, int(y1) - 6, 11)]
    for i, y in enumerate(ys):
        if ours and abs(y - oy) < 7:
            continue
        if i not in skip_w:
            house_x(kit, f"{name}.w{i}", ox - 14.0, y, 8.0, 9.0, 4.6 + (i % 3) * 0.6, cols[i % 5], +1,
                    roof="#f4f8ff" if snow else "#c4624a")
        house_x(kit, f"{name}.e{i}", ox + 14.0, y + 3, 8.0, 9.0, 4.4 + (i % 2), cols[(i + 2) % 5], -1,
                roof="#f4f8ff" if snow else "#6a7aa8")
        if not snow and i not in skip_w and i not in skip_tw:
            tree(kit, f"{name}.tw{i}", ox - 6.6, y + 5.5, 4.5 + (i % 2))
            tree(kit, f"{name}.te{i}", ox + 6.6, y - 2, 4.5)
    # far hills behind
    for k in range(5):
        kit.box(f"{name}.hill{k}", (60, 30, 12 + k * 3), (ox + (k - 2) * 50, y1 + 60, 4 + k), p("#8fd36a" if not snow else "#e8f0f8", 0.9))


def car(kit, name, body="#2f7fd8"):
    p = kit.plastic
    root = kit.empty(name, (0, 0, 0))
    bm = p(body, 0.35, spec=0.5)
    kit.box(f"{name}.low", (1.8, 4.0, 0.55), (0, 0, 0.62), bm, root, bevel=0.1)
    kit.box(f"{name}.hood", (1.7, 1.3, 0.08), (0, -1.5, 0.92), bm, root, bevel=0.03)
    kit.box(f"{name}.cab", (1.62, 2.3, 0.98), (0, 0.45, 1.32), kit.glass("#e6f2fc"), root)
    kit.box(f"{name}.roof", (1.74, 2.44, 0.08), (0, 0.45, 1.84), bm, root, bevel=0.03)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"{name}.pil{sx}{sy}", (0.08, 0.1, 1.0), (sx * 0.83, 0.45 + sy * 1.15, 1.32), bm, root)
            kit.cyl(f"{name}.wh{sx}{sy}", 0.38, 0.24, (sx * 0.92, sy * 1.3, 0.38), p("#25272c", 0.8), root,
                    rot=(0, math.pi / 2, 0), n=14)
    kit.box(f"{name}.mirror", (0.4, 0.05, 0.14), (0.0, -0.6, 1.7), p("#25272c", 0.4), root)
    kit.box(f"{name}.seat", (0.6, 0.6, 0.12), (0.45, 0.5, 0.46), p("#444a58", 0.8), root)
    for sx in (-1, 1):
        kit.box(f"{name}.hl{sx}", (0.4, 0.06, 0.2), (sx * 0.6, -2.0, 0.7), kit.emit("#fff4c8", 1.2), root)
        kit.box(f"{name}.tl{sx}", (0.4, 0.06, 0.2), (sx * 0.6, 2.0, 0.7), kit.emit("#ff5040", 0.8), root)
    return root


def bus(kit, name):
    p = kit.plastic
    root = kit.empty(name, (0, 0, 0))
    bm = p("#ff9f43", 0.35, spec=0.4)
    kit.box(f"{name}.body", (2.8, 9.0, 2.6), (0, 0, 1.75), bm, root, bevel=0.15)
    kit.box(f"{name}.stripe", (2.84, 9.04, 0.3), (0, 0, 1.05), p("#fffaf0", 0.5), root)
    kit.box(f"{name}.roof", (2.7, 8.9, 0.1), (0, 0, 3.08), p("#fffaf0", 0.5), root)
    gl = kit.glass("#b8d8f0")
    for sx in (-1, 1):
        for k in range(5):
            kit.box(f"{name}.win{sx}{k}", (0.06, 1.2, 0.9), (sx * 1.42, -3.2 + k * 1.6, 2.2), gl, root)
    kit.box(f"{name}.ws", (2.4, 0.06, 1.1), (0, -4.52, 2.1), gl, root)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"{name}.wh{sx}{sy}", 0.55, 0.3, (sx * 1.3, sy * 2.9, 0.55), p("#25272c", 0.8), root,
                    rot=(0, math.pi / 2, 0), n=14)
        kit.box(f"{name}.hl{sx}", (0.5, 0.06, 0.3), (sx * 0.9, -4.52, 0.95), kit.emit("#fff4c8", 1.2), root)
    kit.box(f"{name}.door", (0.06, 1.0, 2.1), (-1.43, -3.4, 1.55), p("#2f7fd8", 0.5), root)
    return root


def room(kit, name, cx, cy, w, d, h, wall_c, floor_mat, ceil=False, door=None):
    """Four walls (and a ceiling). door="right" or "left" cuts a 1.3 m doorway at y=cy into that side wall."""
    p = kit.plastic
    wm = p(wall_c, 0.85, spec=0.05)
    kit.plane(f"{name}.floor", (w, d), (cx, cy, 0.03), floor_mat)
    kit.box(f"{name}.back", (w, 0.3, h), (cx, cy + d / 2, h / 2), wm)
    kit.box(f"{name}.front", (w, 0.3, h), (cx, cy - d / 2, h / 2), wm)
    for sg, nm in ((-1, "left"), (1, "right")):
        x = cx + sg * w / 2
        if door == nm:
            seg = (d - 1.3) / 2
            kit.box(f"{name}.{nm}a", (0.3, seg, h), (x, cy - 0.65 - seg / 2, h / 2), wm)
            kit.box(f"{name}.{nm}b", (0.3, seg, h), (x, cy + 0.65 + seg / 2, h / 2), wm)
            kit.box(f"{name}.{nm}c", (0.3, 1.3, h - 2.6), (x, cy, 2.6 + (h - 2.6) / 2), wm)
        else:
            kit.box(f"{name}.{nm}", (0.3, d, h), (x, cy, h / 2), wm)
    kit.box(f"{name}.base", (w, 0.34, 0.2), (cx, cy + d / 2 - 0.02, 0.1), p("#f4ecdc", 0.8))
    if ceil:
        kit.box(f"{name}.ceil", (w, d, 0.2), (cx, cy, h + 0.1), p("#e8e0d0", 0.9))


def seven_seg(kit, parent, name, x, mat, add):
    """Seven boxes of one digit (a, b, c, d, e, f, g); add(name, size, loc, mat, parent) makes one."""
    segs = []
    wd, hd, th = 0.12, 0.17, 0.04
    spec = [((0, hd * 2 - th * 0.0, 0), (wd, th)), ((wd / 2 + th / 2, hd, 0), (th, hd)), ((wd / 2 + th / 2, hd * 0, 0), (th, hd)),
            ((0, -hd, 0), (wd, th)), ((-wd / 2 - th / 2, hd * 0, 0), (th, hd)), ((-wd / 2 - th / 2, hd, 0), (th, hd)),
            ((0, 0, 0), (wd, th))]
    # layout: top y=+0.17, upper verticals y=+0.085, middle 0, lower verticals y=-0.085, bottom -0.17
    pos = [(0, 0.17), (wd / 2 + th / 2, 0.085), (wd / 2 + th / 2, -0.085), (0, -0.17), (-wd / 2 - th / 2, -0.085),
           (-wd / 2 - th / 2, 0.085), (0, 0.0)]
    siz = [(wd + th, th), (th, 0.17), (th, 0.17), (wd + th, th), (th, 0.17), (th, 0.17), (wd + th, th)]
    for i in range(7):
        segs.append(add(f"{name}.seg{i}", (siz[i][0], siz[i][1], 0.01), (x + pos[i][0], pos[i][1], 0.05), mat, parent))
    return segs


DIGITS = {0: "abcdef", 1: "bc", 2: "abdeg", 3: "abcdg", 4: "bcfg", 5: "acdfg", 6: "acdefg", 7: "abc", 8: "abcdefg", 9: "abcdfg"}


def build_meter(kit, name, parent, world=False):
    """The rule meter: a cream tag. A road glyph at the left, a bar that fills toward a red notch (one block), and
    three seven-segment digits for the miles. Layers are 1.2 cm apart (in unit space) so nothing shares a plane."""
    root = kit.empty(name, (0, 0, 0), parent)

    def b(n, size, loc, mat):
        ob = kit.box(f"{name}.{n}", size, loc, mat, root)
        noshadow(ob)
        return ob

    k = 0.012
    edge = kit.emit("#1f2a44", 0.9, "m_edge")
    plate = kit.emit("#fff3d6", 0.85, "m_plate")
    road = kit.emit("#3a4152", 0.9, "m_road")
    dash = kit.emit("#ffffff", 0.9, "m_dash")
    track = kit.emit("#cfc4a8", 0.85, "m_track")
    red = kit.emit("#e8402f", 0.9, "m_red")
    teal = kit.emit("#1f9e8f", 0.9, "m_teal")
    ink = kit.emit("#1f2a44", 0.9, "m_ink")
    b("edge", (1.0, 0.58, k), (0, 0, 0.0), edge)
    b("plate", (0.92, 0.5, k), (0, 0, k), plate)
    road_ob = b("road", (0.2, 0.38, k), (-0.33, 0, 2 * k), road)
    road_set = [road_ob]
    for i in range(3):
        road_set.append(b(f"dash{i}", (0.03, 0.07, k), (-0.33, -0.13 + i * 0.13, 3 * k), dash))
    # the miles glyph (shown with the digits): a green post plate with a white blocky m, so a bare number has a unit
    mplate = kit.emit("#1f7a4a", 0.9, "m_mile")
    mile_set = [b("milep", (0.2, 0.38, k), (-0.33, 0, 2 * k), mplate)]
    for j, mx in enumerate((-0.065, 0.0, 0.065)):
        mile_set.append(b(f"milem{j}", (0.032, 0.17, k), (-0.33 + mx, -0.03, 3 * k), dash))
    mile_set.append(b("milet", (0.162, 0.032, k), (-0.33, 0.05, 3 * k), dash))
    for ob in mile_set:
        ob.hide_render = True
    X0, X1 = -0.18, 0.42
    trk = b("track", (X1 - X0, 0.1, k), ((X0 + X1) / 2, 0, 2 * k), track)
    unit = (X1 - X0) / 1.25
    fill = b("fill", (1.0, 0.1, k), (X0 + 0.5, 0, 3 * k), teal)
    notch = b("notch", (0.06, 0.32, k), (X0 + unit, 0, 4 * k), red)
    digs = []
    for i, dx in enumerate((-0.07, 0.15, 0.37)):
        digs.append(seven_seg(kit, root, f"{name}.d{i}", dx, ink, lambda n, s, l, m, par: _seg(kit, n, s, l, m, par)))
    return {"root": root, "fill": fill, "teal": teal, "red": red, "notch": notch, "track": trk, "unit": unit, "x0": X0,
            "digs": digs, "world": world, "road_set": road_set, "mile_set": mile_set}


def _seg(kit, n, s, l, m, par):
    ob = kit.box(n, s, (l[0], l[1], l[2]), m, par)
    noshadow(ob)
    return ob


def update_meter(M, st):
    bar = max(0.0, st["bar"])
    ln = max(0.001, min(1.25, bar) * M["unit"])
    f = M["fill"]
    f.scale = (ln, 1.0, 1.0)
    f.location = (M["x0"] + ln / 2, 0, f.location.z)
    f.data.materials[0] = M["red"] if st["red"] > 0.5 else M["teal"]
    dig = st["digits"] > 0.5
    for ob in (f, M["notch"], M["track"]):
        ob.hide_render = dig
    for ob in M["road_set"]:
        ob.hide_render = dig
    for ob in M["mile_set"]:
        ob.hide_render = not dig
    n = int(round(st["num"]))
    s = str(max(0, n))
    for i in range(3):
        idx = i - (3 - len(s))
        ch = int(s[idx]) if (dig and 0 <= idx < len(s)) else None
        for j, seg in enumerate(M["digs"][i]):
            seg.hide_render = not (ch is not None and "abcdefg"[j] in DIGITS[ch])


# ---------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    p = kit.plastic
    SX, SY = G.SQ
    # ------------------------------------------------------------------ lights (gains set in animate)
    sun = kit.light("sun", "SUN", (0, -30, 40), 1.0, "#fff0d8", size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#cfe6ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    front = kit.light("front", "SUN", (-10, -30, 20), 1.0, "#ffd2ae", shadow=False)
    front.data.angle = 0.4
    kit.aim(front, (0, 0, 0))

    kit.light("wfill", "POINT", (0, 0, 0), 40.0, "#fff2e0", size=0.6, shadow=False)
    kit.LIGHTS["wfill"]["light"].specular_factor = 0.0
    kit.LIGHTS["wfill"]["obj"].visible_glossy = False
    kit.LIGHTS["wfill"]["obj"].visible_transmission = False

    # ------------------------------------------------------------------ the square and the well
    kit.plane("ground", (900, 300), (300, 0, -0.02), p("#9fd37a", 0.9, spec=0.05))
    kit.plane("sqfloor", (40, 40), (SX, SY, 0.0), kit.bricks("#d98a6a", "#c4553b", "#e8e0cf", 1.0))
    stone = kit.grime("#e8e0cf", 0.9, 2.5, "wellstone", 0.9)
    stone2 = kit.grime("#d9cfb8", 0.9, 2.5, "wellstone2", 0.9)
    kit.cyl("well.base", 1.7, 0.16, (SX, SY, 0.08), stone2, n=32)
    n = 36
    for i in range(n):
        a = 2 * math.pi * i / n
        kit.box(f"well.wall{i}", (0.5, 0.56, 0.9), (SX + 1.22 * math.cos(a), SY + 1.22 * math.sin(a), 0.45), stone,
                rot=(0, 0, a + math.pi / 2))
    wat = p("#1a4a86", 0.4, spec=0.2)
    kit.cyl("well.water", 1.0, 0.02, (SX, SY, 0.58), wat, n=28)
    kit.cyl("well.shaft", 0.99, 0.5, (SX, SY, 0.3), p("#0a1a33", 0.9), n=28)
    # the lore plant: a few newer bricks butted against the old seamless stone
    for i, a in enumerate((200, 215, 230, 245, 260)):
        kit.box(f"well.nbrick{i}", (0.5, 0.25, 0.14), (SX + 1.85 * math.cos(a * D2R), SY + 1.85 * math.sin(a * D2R), 0.07),
                p("#c4553b", 0.8, spec=0.05), rot=(0, 0, a * D2R))
    # the crank frame and a bucket on the rim
    wood = p("#a8744a", 0.7, spec=0.1)
    for sx in (-1, 1):
        kit.box(f"well.post{sx}", (0.18, 0.18, 2.4), (SX + sx * 1.62, SY + 0.05, 1.2), wood, bevel=0.03)
    kit.box("well.cross", (3.6, 0.2, 0.2), (SX, SY + 0.05, 2.4), wood, bevel=0.03)
    for sx in (-1, 1):
        kit.box(f"well.roof{sx}", (1.2, 1.9, 0.1), (SX + sx * 0.62, SY + 0.05, 2.62), p("#c4553b", 0.7),
                rot=(0, -sx * 0.35, 0), bevel=0.02)
    kit.cyl("well.bucket", 0.22, 0.34, (SX + 1.0, SY + 1.0, 1.1), p("#8a6a4a", 0.7), n=14, r2=0.26)
    kit.box("well.crankarm", (0.7, 0.07, 0.07), (SX + 1.62, SY - 0.1, 1.9), wood)
    # ripples (rings on the water) and the coin
    ring_a = kit.emit("#d8ecff", 0.9, "ripple")
    ring_g = kit.emit("#ffcf4a", 1.6, "ripple_gold")
    W["ring_a"], W["ring_g"] = ring_a, ring_g
    W["rings"] = []
    W["rings_in"] = []
    for i in range(4):
        r = kit.cyl(f"ripple{i}", 1.0, 0.012, (SX, SY, 0.595 + i * 0.012), ring_a, n=40, r2=1.0)
        W["rings"].append(r)
        W["rings_in"].append(kit.cyl(f"ripple_in{i}", 1.0, 0.004, (SX, SY, 0.603 + i * 0.012), wat, n=40, r2=1.0))
    W["coin"] = kit.cyl("coin", 0.11, 0.025, (0, 0, -50), kit.emit("#ffcf4a", 1.1, "coinmat"), n=16, rot=(0, 0, 0))
    # lamp posts
    for k, (lx, ly) in enumerate([(-6, -5), (6, -5), (-6, 7), (6, 7)]):
        kit.cyl(f"lamp{k}.post", 0.08, 3.4, (SX + lx, SY + ly, 1.7), p("#33405a", 0.5), n=8)
        kit.sphere(f"lamp{k}.glass", 0.28, (SX + lx, SY + ly, 3.55), kit.emit("#ffe6b0", 1.6, "lampglow"), seg=10)
        kit.light(f"lamp{k}", "POINT", (SX + lx, SY + ly, 3.3), 220.0, "#ffe0a0", size=0.4, shadow=False)
    # benches
    bw = p("#a8744a", 0.7, spec=0.1)
    for k, (bx, by, ry) in enumerate([(-8.5, 1.0, 90), (8.5, -1.0, -90), (3.5, -7.5, 0)]):
        a = ry * D2R
        kit.box(f"bench{k}.seat", (3.0 if ry == 0 else 1.0, 1.0 if ry == 0 else 3.0, 0.14), (SX + bx, SY + by, 0.55), bw)
        if ry == 0:
            kit.box(f"bench{k}.back", (3.0, 0.14, 0.8), (SX + bx, SY + by + 0.5, 1.0), bw)
        else:
            kit.box(f"bench{k}.back", (0.14, 3.0, 0.8), (SX + bx - (0.5 if ry == 90 else -0.5), SY + by, 1.0), bw)
    # the bakery wall on the +y side, with an awning, window boxes and the square's clock
    house_x(kit, "bk", SX, SY + 15.0, 22.0, 6.0, 7.0, "#ffe38a", +1, win=False)
    bkf = SY + 12.0
    for i in range(18):
        kit.box(f"awn{i}", (0.57, 2.0, 0.07), (SX - 9.0 + i * 0.57, bkf - 1.0, 3.3), p("#ff7a8a" if i % 2 else "#fffaf0", 0.6),
                rot=(22 * D2R, 0, 0))
    glassm = p("#7fb2cc", 0.2, spec=0.8)
    for dx in (-8.0, -4.5, 4.5, 8.0):
        kit.box(f"bk.win{dx}", (2.2, 0.12, 1.6), (SX + dx, bkf - 0.05, 1.8), glassm)
        kit.box(f"bk.wbox{dx}", (2.4, 0.5, 0.35), (SX + dx, bkf - 0.3, 0.9), p("#8a5a3a", 0.8))
        for q in range(4):
            kit.sphere(f"bk.fl{dx}_{q}", 0.2, (SX + dx - 0.8 + q * 0.53, bkf - 0.3, 1.2), p(["#ff7a8a", "#ffd23f", "#ffffff", "#ff9a4a"][q], 0.6), seg=8)
    kit.box("bk.door", (1.6, 0.12, 2.6), (SX, bkf - 0.05, 1.3), p("#ee9c86", 0.5, spec=0.3))
    cx_, cy_ = SX + 0.0, bkf - 0.1
    ccz = 5.6
    kit.cyl("clock.face", 1.3, 0.1, (cx_, cy_ - 0.05, ccz), p("#fffaf0", 0.6), n=28, rot=(math.pi / 2, 0, 0))
    kit.cyl("clock.rim", 1.45, 0.08, (cx_, cy_ - 0.02, ccz), p("#33405a", 0.5), n=28, rot=(math.pi / 2, 0, 0))
    for h in range(12):
        a = h * 30 * D2R
        kit.box(f"clock.tick{h}", (0.1, 0.05, 0.28 if h % 3 == 0 else 0.15),
                (cx_ + 1.05 * math.sin(a), cy_ - 0.14, ccz + 1.05 * math.cos(a)), p("#33405a", 0.5), rot=(0, -a, 0))
    hh = kit.empty("clock.hh", (cx_, cy_ - 0.2, ccz))
    kit.box("clock.hhand", (0.12, 0.05, 0.75), (0, 0, 0.3), p("#33405a", 0.5), hh)
    mh = kit.empty("clock.mh", (cx_, cy_ - 0.25, ccz))
    kit.box("clock.mhand", (0.09, 0.05, 1.05), (0, 0, 0.45), p("#e8402f", 0.5), mh)
    W["hh"], W["mh"] = hh, mh
    for k, tx in enumerate([-13.0, 13.0, -17.0, 16.0]):
        tree(kit, f"sqtree{k}", SX + tx, SY + 5.0 - 2 * k, 5.0)
    for k in range(7):
        kit.box(f"sqhouse{k}", (6, 6, 5), (SX - 21 + k * 7.0, SY - 18.0, 2.5),
                kit.grime(["#9fe0c0", "#ffe38a", "#8fd3ff", "#ffb0a0"][k % 4], 0.9, 2.0, f"sqh{k}", 0.9))
        kit.box(f"sqhouseroof{k}", (6.6, 6.6, 0.5), (SX - 21 + k * 7.0, SY - 18.0, 5.25), p("#c4553b", 0.7))
    # a flower box beside the well
    kit.box("sqplanter", (2.2, 0.9, 0.5), (SX - 4.5, SY - 3.5, 0.25), p("#8a5a3a", 0.8))
    for q in range(5):
        kit.sphere(f"sqplant{q}", 0.22, (SX - 5.3 + q * 0.4, SY - 3.5, 0.62), p(["#ff7a8a", "#ffd23f", "#ffffff"][q % 3], 0.6), seg=8)

    # ------------------------------------------------------------------ our street, Hobb's corner, Kemp's street
    ox, oy = G.ST
    street(kit, "st", ox, oy, -150, 55, ours=True)
    # fields past the last house
    for k in range(6):
        kit.plane(f"fld{k}", (30, 70), (ox - 18 if k % 2 == 0 else ox + 18, -80 - (k // 2) * 25, 0.01),
                  p(["#8fd36a", "#a8dc70", "#7cc45a"][k % 3], 0.9))
    W["stopsign"] = None
    kit.cyl("stop.post", 0.05, 2.2, (ox - 3.5, oy - 14.0, 1.1), p("#b8bcc4", 0.5), n=8)
    kit.cyl("stop.sign", 0.46, 0.05, (ox - 3.5, oy - 13.96, 2.35), p("#e8402f", 0.5), n=8, rot=(math.pi / 2, math.pi / 8, 0))
    kit.box("stop.mark", (0.6, 0.03, 0.12), (ox - 3.5, oy - 13.9, 2.35), p("#ffffff", 0.5))
    kit.box("crack", (2.4, 0.07, 0.02), (ox - 4.6, oy - 13.8, 0.07), p("#7d838f", 0.9))      # the crack Wes stops at
    kit.box("crack2", (0.6, 0.06, 0.02), (ox - 5.1, oy - 13.55, 0.07), p("#7d838f", 0.9), rot=(0, 0, 0.9))
    # the town-line post
    kit.box("line.post", (0.14, 0.14, 2.6), (ox - 3.5, G.LINE_Y, 1.3), p("#3b8f4e", 0.5))
    kit.box("line.panel", (1.5, 0.08, 1.1), (ox - 3.5, G.LINE_Y + 0.1, 2.4), p("#2f9e57", 0.4, spec=0.3))
    kit.box("line.arrow", (0.8, 0.04, 0.16), (ox - 3.5, G.LINE_Y + 0.17, 2.4), p("#ffffff", 0.5))
    kit.box("line.head1", (0.3, 0.04, 0.16), (ox - 3.2, G.LINE_Y + 0.17, 2.5), p("#ffffff", 0.5), rot=(0, -0.7, 0))
    kit.box("line.head2", (0.3, 0.04, 0.16), (ox - 3.2, G.LINE_Y + 0.17, 2.3), p("#ffffff", 0.5), rot=(0, 0.7, 0))
    # our house: brick-red, porch with steps facing the street, a door
    brick = kit.bricks("#c4553b", "#b04a30", "#e8d8c0", 1.0)
    hx = ox - 14.0
    kit.box("our.body", (8.0, 9.0, 5.0), (hx, oy, 2.5), brick)
    kit.box("our.roof", (8.8, 9.8, 0.5), (hx, oy, 5.25), p("#6a4a3a", 0.7))
    kit.box("our.roof2", (4.4, 6.0, 0.5), (hx, oy, 5.75), p("#6a4a3a", 0.7))
    kit.box("our.deck", (2.6, 5.0, 0.6), (hx + 5.3, oy, 0.3), p("#e8d8b8", 0.8))
    kit.box("our.step2", (1.0, 5.0, 0.4), (hx + 7.1, oy, 0.2), p("#e8d8b8", 0.8))
    kit.box("our.step1", (1.0, 5.0, 0.2), (hx + 8.1, oy, 0.1), p("#e8d8b8", 0.8))
    kit.box("our.doorframe", (0.12, 1.6, 2.7), (hx + 4.03, oy, 1.95), p("#fff4e0", 0.6))
    kit.box("our.door", (0.1, 1.2, 2.5), (hx + 4.1, oy, 1.9), p("#2f7fd8", 0.5, spec=0.3))
    kit.box("our.win1", (0.1, 1.2, 1.3), (hx + 4.03, oy - 3.0, 2.4), p("#7fb2cc", 0.2, spec=0.8))
    kit.box("our.win2", (0.1, 1.2, 1.3), (hx + 4.03, oy + 3.0, 2.4), p("#7fb2cc", 0.2, spec=0.8))
    for sy in (-1, 1):
        kit.box(f"our.rail{sy}", (2.6, 0.1, 0.9), (hx + 5.3, oy + sy * 2.4, 1.05), p("#fff4e0", 0.6))
    # the hatchback and the bus
    W["car"] = car(kit, "hatch")
    W["car"].location = (G.LANE_X - 0.4, oy + 3.0, 0)
    hbx, hby = G.HB
    street(kit, "hb", hbx, hby, -40, 60, skip_tw=(3,))
    kit.cyl("hb.signpost", 0.05, 2.6, (hbx - 3.5, hby + 6.0, 1.3), p("#b8bcc4", 0.5), n=8)
    kit.box("hb.sign", (0.7, 0.05, 0.7), (hbx - 3.5, hby + 6.0, 2.7), p("#2f7fd8", 0.5))
    kit.box("hb.bench", (0.6, 2.0, 0.12), (hbx - 5.2, hby + 9.0, 0.55), p("#a8744a", 0.7))
    W["bus"] = bus(kit, "bus")
    W["bus"].location = (hbx - 40.0, hby, 0)
    W["bus"].rotation_euler = (0, 0, 180 * D2R)
    kpx, kpy = G.KP
    street(kit, "kp", kpx, kpy, -40, 60, snow=True, skip_w=(4,))
    kit.plane("kp.ground", (900, 200), (kpx, kpy, -0.01), p("#f4f8ff", 0.9, spec=0.05))
    kit.plane("kp.yard", (3.4, 4.2), (kpx - 9.2, kpy + 12.6, 0.07), p("#5fc13c", 0.9))
    for i in range(5):
        for j in range(4):
            xx, yy = kpx - 10.4 + i * 0.45, kpy + 10.8 + j * 0.55
            kit.cyl(f"kp.st{i}{j}", 0.025, 0.4, (xx, yy, 0.27), p("#3f8f2a", 0.8), n=6)
            kit.sphere(f"kp.tu{i}{j}", 0.13, (xx, yy, 0.52), p(["#ff5a7a", "#ffd23f", "#ff9a4a", "#ff7ac0"][(i + j) % 4], 0.6), seg=8)
    kit.box("kp.chair", (0.8, 1.6, 0.1), (kpx - 9.2, kpy + 14.0, 0.45), p("#fffaf0", 0.6))
    for k in range(5):
        kit.box(f"kp.chairs{k}", (0.8, 0.12, 0.05), (kpx - 9.2, kpy + 13.4 + k * 0.3, 0.51), p(["#ff7a8a", "#4fc3d8"][k % 2], 0.6))
    kit.box("kp.chairback", (0.8, 0.1, 0.9), (kpx - 9.2, kpy + 14.7, 0.8), p("#fffaf0", 0.6), rot=(-0.3, 0, 0))
    for k in range(4):
        tree(kit, f"kp.tr{k}", kpx + 7 + k * 0.5, kpy - 10 + k * 14, 5.0, tint="#e8f4ff", prop="pinetree_snow_1")

    # ------------------------------------------------------------------ the rooms
    wood_f = kit.planks("#c9976a", "#b78456", 1.0)
    lrx, lry = G.LR
    room(kit, "lr", lrx, lry, 9.0, 8.0, 3.4, "#fbe6c8", wood_f)
    for k in range(8):                            # the stairs, rising along +x on the back wall
        kit.box(f"lr.stair{k}", (0.6, 1.8, 0.3 * (k + 1)), (lrx - 1.4 + k * 0.6, lry + 3.0, 0.15 * (k + 1)), p("#e8d8b8", 0.8))
    kit.box("lr.landing", (1.6, 1.8, 2.4), (lrx + 3.6, lry + 3.0, 1.2), p("#e8d8b8", 0.8))
    kit.box("lr.rail", (0.1, 0.1, 1.0), (lrx + 1.0, lry + 2.0, 1.8), p("#fff4e0", 0.6))
    for k, (bx, by, bz) in enumerate([(lrx - 3.2, lry + 3.0, 0.4), (lrx - 3.2, lry + 3.0, 1.1), (lrx - 2.3, lry + 3.2, 0.4)]):
        kit.box(f"lr.box{k}", (0.8, 0.7, 0.7), (bx, by, bz), p("#c9955a", 0.8))
    try:
        kit.prop("couch_medium1", (lrx - 2.0, lry - 2.4, 0), rot=180, height=0.9, tint="#9fc8e8")
        kit.prop("chair_1", (lrx + 2.2, lry - 1.2, 0), rot=-70, height=1.0, tint="#e3a72f")
        kit.prop("houseplant_1", (lrx - 4.0, lry - 3.0, 0), height=1.3)
    except Exception:
        kit.box("lr.sofa", (2.4, 1.0, 0.8), (lrx - 2.0, lry - 2.4, 0.4), p("#9fc8e8", 0.7))
        kit.box("lr.chair", (0.9, 0.9, 0.8), (lrx + 2.2, lry - 1.2, 0.4), p("#e3a72f", 0.7))
    kit.box("lr.tvstand", (2.4, 0.6, 0.6), (lrx - 3.5, lry - 3.7, 0.3), wood)
    kit.box("lr.tv", (1.7, 0.1, 1.0), (lrx - 3.5, lry - 3.55, 1.1), p("#20242c", 0.2, spec=0.7))
    kit.light("lr", "POINT", (lrx, lry - 0.5, 3.0), 380.0, "#fff0d8", size=0.5, shadow=False)

    wrx, wry = G.WR
    room(kit, "wr", wrx, wry, 8.0, 7.0, 3.2, "#cfe8f4", kit.planks("#d8b288", "#c9a070", 1.0), ceil=False, door="left")
    kit.box("wr.desk", (1.0, 2.2, 0.9), (wrx + 3.1, wry - 0.6, 0.45), wood)
    kit.box("wr.deskchair", (0.6, 0.6, 0.1), (wrx + 2.0, wry - 0.6, 0.5), p("#2f7fd8", 0.6))
    kit.box("wr.lamp", (0.2, 0.2, 0.5), (wrx + 3.2, wry + 0.3, 1.15), kit.emit("#fff0c0", 1.0))
    try:
        kit.prop("bed_single", (wrx - 2.4, wry + 0.9, 0), rot=0, height=0.9, tint="#bcd8ff")
    except Exception:
        kit.box("wr.bed", (1.6, 2.4, 0.5), (wrx - 2.4, wry + 0.9, 0.25), p("#bcd8ff", 0.7))
    # the bedroom window (+x wall) whose weather changes
    wmat = kit.emit("#9fe0ff", 0.9, "winsky")
    W["winsky"] = wmat
    kit.box("wr.winfr", (0.12, 2.2, 1.9), (wrx + 3.9, wry - 0.6, 1.9), p("#fff4e0", 0.6))
    kit.box("wr.win", (0.1, 1.9, 1.6), (wrx + 3.82, wry - 0.6, 1.9), wmat)
    kit.box("wr.winbar", (0.12, 0.08, 1.6), (wrx + 3.78, wry - 0.6, 1.9), p("#fff4e0", 0.6))
    W["sill"] = kit.box("wr.snow", (0.4, 2.3, 0.22), (wrx + 3.7, wry - 0.6, 1.0), p("#ffffff", 0.9))
    W["leaf"] = [kit.box(f"wr.leaf{i}", (0.1, 0.3, 0.25), (wrx + 3.78, wry - 1.3 + i * 0.5, 2.3 - (i % 2) * 0.5),
                         p(["#e8702a", "#d9a02a", "#c4452a"][i % 3], 0.8), rot=(0, 0, i)) for i in range(4)]
    W["posters"] = []
    for i, (px, pz, c1, c2) in enumerate([(-1.5, 2.1, "#e8402f", "#ffd23f"), (0.0, 2.0, "#2f7fd8", "#8fd3ff"), (1.5, 2.2, "#3b8f4e", "#ffcf4a")]):
        grp = kit.empty(f"wr.poster{i}", (wrx + px, wry + 3.35, pz))
        kit.box(f"wr.poster{i}.a", (1.0, 0.05, 1.3), (0, 0, 0), p(c1, 0.6), grp)
        kit.box(f"wr.poster{i}.b", (0.6, 0.05, 0.5), (0, -0.02, 0.1), p(c2, 0.6), grp)
        kit.sphere(f"wr.poster{i}.c", 0.14, (0, -0.04, -0.35), p("#ffffff", 0.6), grp, seg=8)
        W["posters"].append(grp)
    kit.box("wr.rug", (3.0, 2.2, 0.03), (wrx, wry - 1.0, 0.05), p("#ffb0a0", 0.9))
    kit.light("wr", "POINT", (wrx, wry - 0.5, 2.9), 330.0, "#fff0d8", size=0.5, shadow=False)

    hlx, hly = G.HL
    room(kit, "hl", hlx, hly, 8.0, 5.0, 3.2, "#f6dcc8", wood_f, ceil=True, door="right")
    dh = kit.empty("hl.door", (hlx + 3.85, hly - 0.65, 0))     # Wes's door on the hall's +x wall, hinged at -y
    W["door"] = dh
    kit.box("hl.leaf", (0.12, 1.3, 2.5), (0, 0.65, 1.25), p("#2f7fd8", 0.5, spec=0.3), dh)
    kit.box("hl.line", (0.14, 1.2, 0.07), (-0.02, 0.65, 0.05), kit.emit("#ffe6a0", 2.0, "doorline"), dh)
    W["doorline"] = dh.children[-1]
    W["spill"] = kit.box("hl.spill", (0.9, 1.1, 0.01), (hlx + 3.4, hly - 0.1, 0.07), kit.emit("#ffd890", 0.55, "spill"))
    noshadow(W["spill"])
    kit.box("hl.frame", (0.3, 0.14, 2.6), (hlx + 3.85, hly + 0.72, 1.3), p("#fff4e0", 0.6))
    kit.box("hl.jamb", (0.3, 0.14, 2.6), (hlx + 3.85, hly - 0.72, 1.3), p("#fff4e0", 0.6))
    kit.light("hl", "POINT", (hlx - 1.5, hly - 0.5, 2.8), 260.0, "#fff0d8", size=0.5, shadow=False)

    ktx, kty = G.KT
    room(kit, "kt", ktx, kty, 8.0, 7.0, 3.4, "#fff0b8", kit.checker("#fff8e8", "#e8c8a0", 1.0))
    try:
        kit.prop("table_roundsmall", (ktx, kty, 0), height=0.9)
        kit.prop("kitchen_fridge", (ktx + 3.2, kty + 2.8, 0), rot=90, height=2.0)
    except Exception:
        kit.cyl("kt.table", 0.9, 0.9, (ktx, kty, 0.45), wood, n=20)
    kit.box("kt.chair", (0.6, 0.6, 0.1), (ktx, kty + 1.0, 0.5), p("#e8402f", 0.6))
    kit.box("kt.win", (2.0, 0.1, 1.5), (ktx - 1.8, kty + 3.42, 2.0), kit.emit("#bfe8ff", 0.9))
    kit.box("kt.winfr", (2.2, 0.1, 1.7), (ktx - 1.8, kty + 3.4, 2.0), p("#fff4e0", 0.6))
    kit.light("kt", "POINT", (ktx, kty - 0.5, 3.0), 360.0, "#fff4dc", size=0.5, shadow=False)

    bix, biy = G.BI
    room(kit, "bi", bix, biy, 4.4, 10.0, 2.7, "#ffe0b0", p("#6b6f78", 0.9), ceil=False)
    for k in range(4):
        for sx in (-1, 1):
            kit.box(f"bi.seat{k}{sx}", (1.0, 0.7, 0.14), (bix + sx * 1.3, biy - 1.0 + k * 1.4, 0.5), p("#2f7fd8", 0.7))
            kit.box(f"bi.sback{k}{sx}", (1.0, 0.12, 0.8), (bix + sx * 1.3, biy - 0.65 + k * 1.4, 0.95), p("#2f7fd8", 0.7))
    kit.box("bi.dashboard", (4.0, 0.6, 0.9), (bix, biy - 4.6, 0.6), p("#444a58", 0.6))
    kit.cyl("bi.wheel", 0.35, 0.05, (bix - 1.2, biy - 4.0, 1.15), p("#25272c", 0.6), n=16, rot=(1.2, 0, 0))
    kit.box("bi.dseat", (0.6, 0.6, 0.12), (bix - 1.2, biy - 3.3, 0.5), p("#444a58", 0.8))
    kit.box("bi.wsb", (3.8, 0.06, 1.2), (bix, biy - 4.9, 1.75), kit.emit("#bfe8ff", 0.9))
    kit.light("bi", "POINT", (bix, biy - 1.5, 2.4), 280.0, "#fff4dc", size=0.5, shadow=False)

    # ------------------------------------------------------------------ the highway at sunrise (a windshield view)
    hwx, hwy = G.HW
    kit.plane("hw.road", (7.0, 400), (hwx, hwy - 150, 0.02), p("#5a5e68", 0.9, spec=0.05))
    for k in range(40):
        kit.box(f"hw.dash{k}", (0.18, 2.2, 0.02), (hwx, hwy - 4 - k * 8, 0.04), p("#fffaf0", 0.6))
    for sg in (-1, 1):
        kit.box(f"hw.edge{sg}", (0.18, 400, 0.02), (hwx + sg * 3.2, hwy - 150, 0.04), p("#fffaf0", 0.6))
        kit.plane(f"hw.field{sg}", (60, 400), (hwx + sg * 33, hwy - 150, 0.0), p("#7cc45a", 0.9))
        for k in range(8):
            kit.box(f"hw.hill{sg}{k}", (50, 40, 10 + (k % 3) * 5), (hwx + sg * 50, hwy - 60 - k * 40, 3), p("#6cb04a", 0.9))
    kit.sphere("hw.sun", 14.0, (hwx + 8, hwy - 330, 14), kit.emit("#fff0c0", 4.0, "hwsun"), seg=14)
    kit.box("hw.dash", (3.0, 1.0, 0.5), (hwx, hwy + 1.6, 0.55), p("#3a3f4c", 0.5))
    kit.cyl("hw.wheel", 0.34, 0.05, (hwx - 0.55, hwy + 1.1, 0.95), p("#25272c", 0.6), n=20, rot=(1.0, 0, 0))
    kit.box("hw.sleeve", (0.2, 0.5, 0.18), (hwx - 0.55, hwy + 0.8, 1.15), p("#3f7d4e", 0.7))
    kit.box("hw.hand", (0.16, 0.16, 0.14), (hwx - 0.55, hwy + 0.5, 1.2), p("#e8b48c", 0.7))
    kit.light("hw", "POINT", (hwx, hwy + 2.0, 2.0), 120.0, "#ffe6c0", size=0.5, shadow=False)

    # ------------------------------------------------------------------ the big meter backdrop (close-ups)
    mtx, mty = G.MT
    kit.box("mt.wall", (20, 0.3, 12), (mtx, mty + 3.0, 6.0), p("#f4d8a8", 0.9))
    kit.light("mt", "POINT", (mtx, mty - 2.0, 3.0), 200.0, "#fff4dc", size=0.5, shadow=False)

    # ------------------------------------------------------------------ the laptop map
    lpx, lpy = G.LP
    kit.box("lp.lid", (6.4, 0.2, 4.0), (lpx, lpy + 0.1, 2.5), p("#2a2f3a", 0.5))
    kit.box("lp.screen", (6.0, 0.05, 3.6), (lpx, lpy - 0.03, 2.5), kit.emit("#dff0d0", 0.8, "mapbase"))
    kit.box("lp.river", (0.7, 0.04, 3.6), (lpx - 1.0, lpy - 0.06, 2.5), kit.emit("#8fd3ff", 0.8, "mapriver"), rot=(0, 0.25, 0))
    kit.box("lp.lake", (1.4, 0.04, 1.0), (lpx + 1.6, lpy - 0.06, 3.2), kit.emit("#8fd3ff", 0.8, "mapriver"))
    route = kit.emit("#e8402f", 1.0, "maproute")
    pts = [(-2.4, 1.0), (-1.4, 0.6), (-0.4, 1.0), (0.6, 0.2), (1.6, 0.5), (2.6, 0.2), (3.4, 0.4)]
    for i in range(len(pts) - 1):
        ax, az = pts[i]
        bx_, bz = pts[i + 1]
        ln = math.hypot(bx_ - ax, bz - az)
        kit.box(f"lp.route{i}", (ln + 0.08, 0.03, 0.12), (lpx + (ax + bx_) / 2, lpy - 0.1, 1.9 + (az + bz) / 2), route,
                rot=(0, -math.atan2(bz - az, bx_ - ax), 0))
    kit.sphere("lp.start", 0.2, (lpx - 2.4, lpy - 0.12, 2.9), kit.emit("#1f2a44", 1.0, "mapdot"), seg=8)
    kit.box("lp.body", (6.6, 3.0, 0.2), (lpx, lpy - 1.4, 0.45), p("#2a2f3a", 0.5))
    kit.light("lp", "POINT", (lpx, lpy - 3.0, 3.0), 150.0, "#ffffff", size=0.5, shadow=False)

    # ------------------------------------------------------------------ the rule meter: a plate on the camera, and one in the world
    cam = kit.OBJ["cam"]
    W["tagcam"] = build_meter(kit, "tag", cam)
    W["tagw"] = build_meter(kit, "bigtag", None, world=True)
    W["tagw"]["root"].location = (mtx, mty, 3.0)
    W["tagw"]["root"].scale = (1.8, 1.8, 1.8)
    W["tagw"]["root"].rotation_euler = (math.pi / 2, 0, 0)
    W["tagw"]["root"].rotation_euler = (math.pi / 2, 0, 0)
    return {}


# ---------------------------------------------------------------------------------------------- first frame props
def _first_frame(kit, story):
    p = kit.plastic
    W["inited"] = True
    wh = bpy.data.objects.get("wes.headg")
    if wh is not None:
        bm = p("#7a5430", 0.8)       # a darker beard than his hair, sideburns and a chin only: the mouth stays bare
        kit.box("wes.beard", (0.84, 0.3, 0.22), (0, -0.5, -0.6), bm, wh, bevel=0.06)
        for sx in (-1, 1):
            kit.box(f"wes.sideburn{sx}", (0.16, 0.2, 0.5), (sx * 0.52, -0.33, -0.3), bm, wh, bevel=0.04)
    ht = bpy.data.objects.get("wes.torso")
    if ht is not None:
        W["duffel"] = kit.box("wes.duffel", (1.5, 0.8, 1.5), (0, 0.9, 1.1), p("#8a5a2a", 0.8), ht, bevel=0.1)
        kit.box("wes.duffel.strap", (0.3, 0.84, 1.52), (0, 0.9, 1.1), p("#e3c070", 0.8), W["duffel"])
        W["wbox"] = kit.box("wes.carrybox", (1.9, 1.1, 1.5), (0, -1.2, 1.3), p("#c9955a", 0.8), ht, bevel=0.03)
        kit.box("wes.carrybox.tape", (0.3, 1.14, 1.54), (0, -1.2, 1.3), p("#e8d0a0", 0.8), W["wbox"])
    mt = bpy.data.objects.get("me.torso")
    if mt is not None:
        W["mbox"] = kit.box("me.carrybox", (1.9, 1.1, 1.5), (0, -1.2, 1.3), p("#c9955a", 0.8), mt, bevel=0.03)
        kit.box("me.carrybox.tape", (0.3, 1.14, 1.54), (0, -1.2, 1.3), p("#e8d0a0", 0.8), W["mbox"])
    ma = bpy.data.objects.get("me.arm1")
    if ma is not None:
        ring = kit.box("me.keys", (0.34, 0.34, 0.05), (0, -0.4, -2.14), p("#e8402f", 0.5), ma)
        kit.box("me.keys.a", (0.12, 0.62, 0.05), (-0.1, -0.12, 0.05), p("#dfe3ea", 0.3, spec=0.8), ring)
        kit.box("me.keys.b", (0.12, 0.5, 0.05), (0.12, -0.1, 0.05), p("#e8c050", 0.3, spec=0.8), ring)
        W["keys"] = ring
    for who in ("wes", "me"):
        arm = bpy.data.objects.get(f"{who}.arm1")
        if arm is not None:
            ph = kit.box(f"{who}.phone", (0.42, 0.1, 0.78), (0, -0.52, -1.9), p("#20242c", 0.3, spec=0.6), arm, bevel=0.03)
            scr = kit.box(f"{who}.phone.scr", (0.34, 0.02, 0.66), (0, -0.585, -1.9), kit.emit("#bfe8ff", 1.0, f"{who}scr"), ph)
            noshadow(scr)
            W[f"{who}phone"] = ph
            W[f"{who}scr"] = scr
    hb = bpy.data.objects.get("hobb.torso")
    if hb is not None:
        np_ = kit.box("hobb.paper", (1.9, 0.08, 1.3), (0, -1.1, 1.2), p("#f4efe0", 0.9), hb)
        for i in range(4):
            kit.box(f"hobb.paper.c{i}", (0.34, 0.04, 0.9), (-0.7 + i * 0.47, -0.06, 0), p("#9aa0ac", 0.9), np_)
        kit.box("hobb.paper.pic", (0.7, 0.04, 0.4), (0.0, -0.07, 0.35), p("#8a6a4a", 0.9), np_)
    ha = bpy.data.objects.get("hobb.arm1")
    if ha is not None:
        W["watch"] = kit.cyl("hobb.watch", 0.4, 0.14, (0.58, 0.0, -1.55), p("#fffaf0", 0.5), ha, rot=(0, math.pi / 2, 0), n=18)
        kit.cyl("hobb.watch.rim", 0.46, 0.1, (0.54, 0.0, -1.55), p("#33405a", 0.5), ha, rot=(0, math.pi / 2, 0), n=18)
        kit.box("hobb.watch.h1", (0.05, 0.05, 0.32), (0.68, 0.0, -1.42), p("#33405a", 0.5), ha)
        kit.box("hobb.watch.h2", (0.05, 0.28, 0.05), (0.68, -0.1, -1.55), p("#33405a", 0.5), ha)
        kit.box("hobb.watch.sec", (0.05, 0.05, 0.3), (0.7, 0.0, -1.7), p("#e8402f", 0.5), ha)
    for who in ("wes", "me", "hobb"):
        pass


# ---------------------------------------------------------------------------------------------- animate
def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    look = look_at(tl, t)
    gains = {}
    az, el = look["az"] * D2R, look["el"] * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    so = kit.LIGHTS["sun"]["obj"]
    ref = Vector(ctx.get("focus", (0, 0, 0))) if isinstance(ctx, dict) else Vector((0, 0, 0))
    so.location = d * 60
    kit.aim(so, (0, 0, 0))
    kit.LIGHTS["sun"]["light"].color = look["sun_col"]
    kit.LIGHTS["fill"]["light"].color = look["fill_col"]
    gains["sun"], gains["fill"], gains["front"] = look["sun"], look["fill"], look["front"]
    for k in range(4):
        gains[f"lamp{k}"] = look["lamp"]
    gains["hl"] = look["hall"]
    cx_ = None
    try:
        sh_ = next((s_ for s_ in tl["shots"] if s_["start"] <= t < s_["end"]), None)
        sp_ = next((s_ for s_ in story["shots"] if s_["id"] == sh_["id"]), None) if sh_ else None
        cx_ = sp_["cam"][0][1][0] if sp_ else None
    except Exception:
        cx_ = None
    if cx_ is not None and 425 < cx_ < 450 and look["lamp"] >= 0.99:       # the night hall and bedroom: only their own lamps
        gains["fill"] *= 0.12
        gains["front"] *= 0.1
        gains["sun"] *= 0.2
        gains["hl"] = 0.9
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*look["sky"], 1.0)
    bg.inputs["Strength"].default_value = look["sky_str"]

    # the meter
    ms = sample("meter", tl, t, {"bar": 0.3, "red": 0.0, "digits": 0.0, "num": 0.0})
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
    dist = 0.3         # the tag sits close to the lens, so a prop a metre away never hides it
    h2 = dist * 12.0 / lens
    w2 = h2 * 9.0 / 16.0
    tag = W["tagcam"]["root"]
    big = False       # the small tag stays on the lens in every shot, even the close-ups of the big one
    for c_ in [tag] + list(tag.children_recursive):
        c_.hide_render = big
    if not big:
        update_meter(W["tagcam"], ms)
    update_meter(W["tagw"], ms)
    s = 0.66 * w2
    tag.scale = (s, s, s)
    tag.location = (-0.04 * w2, 0.72 * h2, -dist)

    # the clock
    ck = sample("clock", tl, t, {"h": 10.0})
    W["hh"].rotation_euler = (0, -(ck["h"] % 12) * 30 * D2R, 0)
    W["mh"].rotation_euler = (0, -(ck["h"] % 1) * 360 * D2R, 0)

    # the coin and the ripples
    SX, SY = G.SQ
    cs = sample("coin", tl, t, {"x": 0.0, "y": 0.0, "z": -50.0, "spin": 0.0, "att": 0.0, "who": ""})
    coin = W["coin"]
    if cs["att"] > 0.5 and cs["who"]:
        arm = bpy.data.objects.get(f"{cs['who']}.arm1")
        if arm is not None:
            bpy.context.view_layer.update()
            pos = arm.matrix_world @ Vector((0.0, -0.35, -2.05))
            coin.location = pos
        else:
            coin.location = (cs["x"], cs["y"], cs["z"])
    else:
        coin.location = (cs["x"], cs["y"], cs["z"])
    coin.rotation_euler = (cs["spin"] * D2R, 0, 0.4)
    pl = last_cue("plink", tl, t)
    for i, ring in enumerate(W["rings"]):
        inner = W["rings_in"][i]
        if pl is None:
            ring.hide_render = inner.hide_render = True
            continue
        a = (t - pl["t"]) - i * 0.16
        if a < 0 or a > 2.2:
            ring.hide_render = inner.hide_render = True
            continue
        r = 0.12 + a * 0.5
        if r > 0.95:
            ring.hide_render = inner.hide_render = True
            continue
        ring.hide_render = inner.hide_render = False
        ring.scale = (r, r, 1.0)
        inner.scale = (max(0.01, r - 0.07), max(0.01, r - 0.07), 1.0)
        ring.data.materials[0] = W["ring_g"] if pl.get("glow") else W["ring_a"]

    # the car, the bus
    cc = sample("car", tl, t, {"x": G.LANE_X - 0.4, "y": 3.0, "yaw": 0.0})
    W["car"].location = (cc["x"], cc["y"], 0)
    W["car"].rotation_euler = (0, 0, cc["yaw"] * D2R)
    bs = sample("bus", tl, t, {"x": G.HB[0] - 40.0, "y": 0.0, "yaw": 180.0})
    W["bus"].location = (bs["x"], bs["y"], 0)
    W["bus"].rotation_euler = (0, 0, bs["yaw"] * D2R)
    rd = sample("ride", tl, t, {"v": 0.0})
    if rd["v"] > 0.5:
        wes = bpy.data.objects.get("wes")
        if wes is not None:
            a = cc["yaw"] * D2R
            lx, ly = 0.45, 0.35
            wes.location.x = cc["x"] + lx * math.cos(a) - ly * math.sin(a)
            wes.location.y = cc["y"] + lx * math.sin(a) + ly * math.cos(a)
            wes.rotation_euler.z = a

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

    # what Wes and I carry, the phones, the duffel
    if "wbox" in W:
        W["wbox"].hide_render = sample("wbox", tl, t, {"v": 0.0})["v"] < 0.5
        for c_ in W["wbox"].children:
            c_.hide_render = W["wbox"].hide_render
    if "mbox" in W:
        W["mbox"].hide_render = sample("mbox", tl, t, {"v": 0.0})["v"] < 0.5
        for c_ in W["mbox"].children:
            c_.hide_render = W["mbox"].hide_render
    du = sample("duffel", tl, t, {"v": 0.0})
    if "duffel" in W:
        dff = W["duffel"]
        if du["v"] > 1.5:
            _hide(dff, True)
        else:
            _hide(dff, False)
            dff.location = (0, 0.9, 1.1) if du["v"] < 0.5 else (0, -1.1, 0.5)
    for who in ("wes", "me"):
        if f"{who}phone" in W:
            ph = sample({"wes": "wphone", "me": "mphone"}[who], tl, t, {"v": 0.0, "lit": 1.0})
            _hide(W[f"{who}phone"], ph["v"] < 0.5)
            W[f"{who}scr"].hide_render = ph["v"] < 0.5 or ph["lit"] < 0.5
    # the bedroom window's weather, the posters, Wes's door
    se = sample("season", tl, t, {"v": 0.0})["v"]
    set_emit(W["winsky"], ["#9fe0ff", "#f2a65a", "#eaf2ff"][int(round(se)) % 3])
    W["sill"].hide_render = int(round(se)) != 2
    for lf in W["leaf"]:
        lf.hide_render = int(round(se)) != 1
    npost = sample("posters", tl, t, {"n": 3.0})["n"]
    for i, g in enumerate(W["posters"]):
        _hide(g, i >= int(round(npost)))
    da = sample("wdoor", tl, t, {"a": 0.0})["a"]
    W["door"].rotation_euler = (0, 0, da * D2R)
    W["doorline"].hide_render = abs(da) > 3.0
    W["spill"].hide_render = abs(da) > 3.0
    if "keys" in W:
        _hide(W["keys"], sample("keys", tl, t, {"v": 0.0})["v"] < 0.5)
    # what a hidden character carries stays hidden with them (the pose above hid them, the cues just now showed them)
    for who, props in (("wes", ("wbox", "duffel", "wesphone")), ("me", ("mbox", "keys", "mephone"))):
        ro = bpy.data.objects.get(who)
        if ro is not None and ro.hide_render:
            for k_ in props:
                if k_ in W:
                    _hide(W[k_], True)
    # a soft fill on Wes's face in the car and in the dark hall, so he reads like his porch shots
    wes_o = bpy.data.objects.get("wes")
    cam_o = kit.OBJ.get("cam")
    fillg = 0.0
    if wes_o is not None and cam_o is not None and not wes_o.hide_render:
        in_car = sample("ride", tl, t, {"v": 0.0})["v"] > 0.5
        dark_hall = cx_ is not None and 425 < cx_ < 450
        if in_car or dark_hall:
            hp = Vector(wes_o.location) + Vector((0, 0, 1.6 if in_car else 1.5))
            cp = Vector(cam_o.matrix_world.translation)
            if sp_ is not None and sh_ is not None:      # the camera is placed after this runs: use the shot's own path
                ks = sp_["cam"]
                uu = (t - sh_["start"]) / max(1e-6, sh_["end"] - sh_["start"])
                a_, b_ = ks[0], ks[-1]
                for k0, k1 in zip(ks, ks[1:]):
                    if uu <= k1[0]:
                        a_, b_ = k0, k1
                        break
                fr = min(1.0, max(0.0, (uu - a_[0]) / max(1e-6, b_[0] - a_[0]))) if b_ is not a_ else 0.0
                cp = Vector(a_[1]) * (1 - fr) + Vector(b_[1]) * fr
            dv = cp - hp
            dl = max(0.01, dv.length)
            dist = min(0.8 if in_car else 1.2, dl * 0.6)
            kit.LIGHTS["wfill"]["obj"].location = hp + dv / dl * dist
            fillg = 1.0 if in_car else 1.0
    gains["wfill"] = fillg
    return gains
