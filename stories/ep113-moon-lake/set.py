"""ep113 "moon lake": a bright summer lake, Grandma's dock and red rowboat, and a moon that sleeps on the lake bed.
The moon is never built whole: only a rising cratered cap (a big sphere mostly under the water) and a patch of the
lake bed. Everything the story moves is driven by cues in story.json (see animate): the look (sun, fill, sky, always
eased or set on a cut), the rule meter (a day dial on a plate on the camera), the glow under the water, the moon's
rise, the boat, the oar, the water pouring off the cap, the fish and the bubbles.
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {}
WZ = G.WZ


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def _L(**kw):
    base = dict(sun=3.4, sun_col="#fff0d8", el=45.0, az=-25.0, fill=0.8, fill_col="#fff0e0", front=0.35,
                front_col="#ffe6c8", rim=0.3, moonl=0.0, moonl_col="#cfe0ff", ufill=0.0, sky="#5ab8ff", sky_str=1.0)
    base.update(kw)
    return base


LOOKS = {
    "day": _L(),
    # the afternoon goes dark: a dimming to dusk blue, never black
    "dim": _L(rim=0.25, sun=1.1, sun_col="#d4d8ff", el=40.0, fill=1.0, fill_col="#a8b8f0", front=0.5, front_col="#c8d4ff",
              sky="#5d72c4", sky_str=0.85),
    "dusk": _L(rim=0.6, sun=0.3, sun_col="#8fa0ff", el=6.0, fill=1.1, fill_col="#8aa2e8", front=0.7, front_col="#9fb8ff",
               sky="#26397a", sky_str=0.85),
    "night": _L(rim=0.55, sun=0.0, sun_col="#8fa0ff", el=6.0, fill=1.0, fill_col="#7f98e0", front=0.55, front_col="#9fb8ff",
                moonl=1.5, sky="#1e2d66", sky_str=0.8),
    "under": _L(rim=0.6, sun=0.0, fill=0.0, front=0.5, front_col="#a8e6ee", ufill=2.6, sky="#1a7a88", sky_str=0.9),
}
LIGHTS = ("sun", "fill", "front", "moonl", "rim")


def look_at(tl, t):
    cues = [c for c in tl["cues"] if c["name"] == "look"]
    cur = LOOKS[cues[0]["id"]] if cues else LOOKS["day"]
    prev = cur
    last = None
    for c in cues:
        if c["t"] > t:
            break
        prev, cur = cur, LOOKS[c["id"]]
        last = c
    if last is not None:   # only the latest look eases (an earlier ramp never swallows a later cue)
        dur = last.get("dur", 0.0)
        dur = 0.0 if dur <= 0 else max(0.4, dur)
        if t < last["t"] + dur:
            u = ss((t - last["t"]) / dur)
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
    last = None
    for c in cues:
        if c["t"] > t:
            break
        prev = dict(cur)
        cur.update({k: v for k, v in c.items() if k in defaults})
        last = c
    if last is not None:   # only the latest cue eases: an earlier ramp never swallows a later cue
        dur = last.get("dur", 0.0)
        if dur > 0 and t < last["t"] + dur:
            u = ss((t - last["t"]) / dur)
            return {k: (prev[k] + (cur[k] - prev[k]) * u if isinstance(cur[k], (int, float)) else cur[k]) for k in cur}
    return cur


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def _hide(ob, hide):
    ob.hide_render = hide
    for c in ob.children_recursive:
        c.hide_render = hide


# ---------------------------------------------------------------------------------------------- the moon's cap
def cratered(kit, root, name, R, n, theta_max, seed, rmin, rmax, mats):
    """Craters lying on a sphere's top cap (no face: random places and sizes, kept apart), parented to `root`
    whose origin is the sphere's centre. Each is a pale rim disc under a darker floor disc, 2 and 3 cm proud."""
    rng = random.Random(seed)
    body, floor, rim = mats
    placed = []
    tries = 0
    while len(placed) < n and tries < 4000:
        tries += 1
        th = math.acos(1 - rng.random() * (1 - math.cos(theta_max * D2R)))
        ph = rng.random() * 2 * math.pi
        r = rmin + (rmax - rmin) * rng.random() ** 2
        pos = Vector((math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th))) * R
        if any((pos - q).length < (r + rr) * 1.25 for q, rr in placed):
            continue
        placed.append((pos, r))
        nrm = pos.normalized()
        rot = (0, th, ph)
        kit.cyl(f"{name}.cr{len(placed)}", r * 1.22, 0.05, tuple(nrm * (R + 0.015)), rim, root, rot=rot, n=16)
        kit.cyl(f"{name}.cf{len(placed)}", r, 0.06, tuple(nrm * (R + 0.04)), floor, root, rot=rot, n=16)
        # a small bright speck on the near edge so a floor isn't a hole
        kit.cyl(f"{name}.cs{len(placed)}", r * 0.16, 0.07, tuple(nrm * (R + 0.06) + Vector((0.0, 0.0, 0.0))), body,
                root, rot=rot, n=8)
    return placed


def moon_mats(kit):
    # a cool, darker body (never beige, never white), deep blue crater floors and a pale-blue lip on each crater
    return (kit.emit("#5d74a6", 0.62, "moonbody"), kit.emit("#2a3a68", 0.5, "moonfloor"),
            kit.emit("#86aee0", 0.48, "moonrim"))


# ---------------------------------------------------------------------------------------------- dial (the rule meter)
def build_dial(kit, parent, prefix, store):
    """A day dial on a navy plate: a half-circle arc (left = morning, right = night), a noon tick at the top, a sun
    glyph that swings along the arc and a moon crescent at the right end. Past the tick the arc glows pale blue."""
    def b(name, size, loc, mat, rot=(0, 0, 0)):
        ob = kit.box(f"{prefix}.{name}", size, loc, mat, parent, rot=rot)
        noshadow(ob)
        return ob

    def c(name, r, loc, mat, n=20):
        ob = kit.cyl(f"{prefix}.{name}", r, 0.004, loc, mat, parent, n=n)
        noshadow(ob)
        return ob

    cream = kit.emit("#f6ecd8", 0.85, "dcream")
    navy = kit.emit("#1a2860", 0.7, "dnavy")
    arc_a = kit.emit("#f6ecd8", 0.9, "darcA")
    arc_b = kit.emit("#8fd0ff", 1.4, "darcB")
    sun_m = kit.emit("#ffd23f", 1.3, "dsun")
    ray_m = kit.emit("#ffe27a", 1.2, "dray")
    tick_m = kit.emit("#ffffff", 0.95, "dtick")
    moon_off = kit.emit("#7e8cb8", 0.55, "dmoonoff")
    moon_on = kit.emit("#d8ecff", 1.5, "dmoonon")
    halo = kit.emit("#4f86d8", 0.85, "dhalo")
    b("edge", (1.0, 0.92, 0.004), (0, 0, 0.0), cream)
    b("plate", (0.9, 0.82, 0.004), (0, 0, 0.004), navy)
    cy, rad = -0.2, 0.36
    for i in range(13):
        a = math.pi - i * math.pi / 12
        past = i < 6
        b(f"arc{i}", (0.12, 0.08, 0.004), (rad * math.cos(a), cy + rad * math.sin(a), 0.008), arc_b if past else arc_a,
          rot=(0, 0, a - math.pi / 2))
    b("tick", (0.05, 0.2, 0.004), (0, cy + rad + 0.02, 0.012), tick_m)
    b("horiz", (0.74, 0.03, 0.004), (0, cy - 0.06, 0.008), arc_a)
    sun = kit.empty(f"{prefix}.sun", (0, cy + rad, 0.016), parent)
    c("sundisc", 0.095, (0, 0, 0), sun_m)
    kit.OBJ and None
    for k in range(8):
        a = k * math.pi / 4
        rb = kit.box(f"{prefix}.ray{k}", (0.03, 0.07, 0.004), (0.15 * math.cos(a), 0.15 * math.sin(a), 0.0), ray_m, sun,
                     rot=(0, 0, a - math.pi / 2))
        noshadow(rb)
    store["sun"] = sun
    store["sun_cy"] = (cy, rad)
    moon = kit.empty(f"{prefix}.moon", (rad + 0.02, cy, 0.016), parent)
    store["halo"] = c("halo", 0.2, (rad + 0.02, cy, 0.012), halo, n=24)
    m_off = kit.cyl(f"{prefix}.moonoff", 0.15, 0.004, (0, 0, 0), moon_off, moon, n=20)
    m_on = kit.cyl(f"{prefix}.moonon", 0.15, 0.004, (0, 0, 0.002), moon_on, moon, n=20)
    cut = kit.cyl(f"{prefix}.moonbite", 0.13, 0.004, (0.08, 0.045, 0.006), navy, moon, n=20)
    for o in (m_off, m_on, cut):
        noshadow(o)
    store["moon_on"], store["moon_off"] = m_on, m_off


def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    W["tagd"] = {}
    build_dial(kit, root, "tag", W["tagd"])


def set_dial(store, v, lit):
    cy, rad = store["sun_cy"]
    a = math.pi - v * math.pi
    sun = store["sun"]
    sun.location = (rad * math.cos(a), cy + rad * math.sin(a), 0.016)
    sz = 1.0 if v < 0.93 else max(0.001, 1.0 - (v - 0.93) / 0.05)
    sun.scale = (sz, sz, sz)
    k = max(0.001, lit)
    for o in (store["moon_on"], store["halo"]):
        o.scale = (k, k, 1.0)
        o.hide_render = lit < 0.02


# ---------------------------------------------------------------------------------------------- the build
def tree(kit, name, x, y, h, tint="#9fcf9a"):
    try:
        kit.prop("pinetree_1", (x, y, 0.0), height=h, tint=tint, rot=(x * 7 + y * 3) % 360)
    except Exception:
        kit.cyl(f"{name}.t", 0.3, h * 0.3, (x, y, h * 0.15), kit.plastic("#7a5230", 0.8), n=8)
        kit.cyl(f"{name}.c", h * 0.18, h * 0.8, (x, y, h * 0.6), kit.plastic("#2f6b3a", 0.8), n=8, r2=0.2)


def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    pl = kit.plastic
    grass = kit.grime("#8fcf7a", 0.85, 1.4, "grass", 0.95)
    sand = pl("#efd9a8", 0.9, spec=0.05)
    water = kit.grime("#1fb0a8", 0.8, 0.5, "water", 0.35)
    gray = kit.grime("#a39a90", 0.75, 3.0, "dockgray", 0.85)
    gray2 = pl("#8a8178", 0.85, spec=0.05)
    red = pl("#e0453a", 0.5, spec=0.25)
    white = pl("#f6f1e6", 0.6, spec=0.1)
    cream = pl("#dcd2bb", 0.7, spec=0.05)
    darkw = pl("#6b4a32", 0.8, spec=0.05)
    green = pl("#2f8a52", 0.7, spec=0.1)

    # ------------------------------------------------------------------ lights (gains set in animate)
    sun = kit.light("sun", "SUN", (0, 30, 40), 1.0, "#fff0d8", size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -30, 30), 1.0, "#cfe6ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    front = kit.light("front", "SUN", (-6, 40, 14), 1.0, "#ffe6c8", shadow=False)
    front.data.angle = 0.4
    kit.aim(front, (0, 0, 0))
    rim = kit.light("rim", "SUN", (0, -60, 25), 1.0, "#a8c0ff", shadow=False)
    rim.data.angle = 0.4
    kit.aim(rim, (0, 0, 0))
    moonl = kit.light("moonl", "SUN", (0, -50, 36), 1.0, "#cfe0ff", shadow=False)
    moonl.data.angle = 0.3
    kit.aim(moonl, (0, -20, 0))
    ufill = kit.light("ufill", "SUN", (G.U[0] + 4, -6, 30), 1.0, "#a8e6ee", shadow=False)
    ufill.data.angle = 0.6
    kit.aim(ufill, (G.U[0], 0, -8))
    kit.light("glow", "POINT", (G.MID[0], G.MID[1], -1.0), 1.0, "#bfe0ff", size=0.8, shadow=False)
    kit.light("uglow", "POINT", (G.U[0], 0, G.UTOP + 3.0), 1.0, "#cfe6ff", size=0.8, shadow=False)
    kit.light("lamp", "POINT", (0, G.PORCH_Y + 1.0, 3.0), 120.0, "#ffe6c0", size=0.5, shadow=False)

    # ------------------------------------------------------------------ the land, lake and trees
    kit.plane("ground", (800, 800), (0, 0, 0), grass)
    kit.cyl("beach", 54.0, 0.1, (0, 0, 0.03), sand, n=96)
    kit.cyl("lake", 50.0, 0.12, (0, 0, WZ - 0.06 + 0.0), water, n=96)
    kit.box("beachpatch", (14, 8, 0.1), (G.BEACH[0] - 4, G.BEACH[1] - 3, 0.06), sand, rot=(0, 0, -0.6))
    rng = random.Random(113)
    for i in range(46):
        a = i / 46 * 2 * math.pi + rng.random() * 0.1
        r = 66 + rng.random() * 26
        x, y = r * math.cos(a), r * math.sin(a)
        if abs(x) < 14 and y < -52:
            continue
        tree(kit, f"pine{i}", x, y, 11 + rng.random() * 6)
    for i in range(26):
        a = i / 26 * 2 * math.pi + 0.07
        r = 112 + rng.random() * 30
        tree(kit, f"pineb{i}", r * math.cos(a), r * math.sin(a), 16 + rng.random() * 8, tint="#8bbf92")
    # hills on the horizon so the sky has a base
    for i, (a, s) in enumerate([(0.3, 60), (1.5, 80), (2.6, 70), (3.8, 90), (4.9, 64), (5.8, 76)]):
        kit.box(f"hill{i}", (s * 1.6, s * 0.5, s * 0.34), (170 * math.cos(a), 170 * math.sin(a), s * 0.1),
                pl("#6aa58a", 0.95, spec=0.02), rot=(0, 0, a + 1.0), bevel=0.2)

    # ------------------------------------------------------------------ Grandma's dock, the red boat, the posts
    dx = G.DOCK_X
    y0, y1 = G.DOCK_Y0, G.DOCK_Y1
    L = y1 - y0
    for i in range(int(L / 0.55)):
        kit.box(f"plank{i}", (2.3, 0.5, 0.1), (dx, y0 + 0.27 + i * 0.55, G.DECK - 0.05), gray if i % 2 else gray2)
    for k in range(0, int(L / 3.0) + 1):
        for sx in (-1, 1):
            kit.box(f"post{k}{sx}", (0.22, 0.22, 2.0), (dx + sx * 1.1, y0 + 0.3 + k * 3.0, G.DECK - 0.7), darkw)
    kit.box("dockrail", (0.12, L * 0.4, 0.1), (dx - 1.1, y0 + L * 0.3, G.DECK + 0.62), darkw)
    kit.box("dockrailp1", (0.14, 0.14, 0.65), (dx - 1.1, y0 + L * 0.3 - L * 0.2 + 0.1, G.DECK + 0.3), darkw)
    kit.box("dockrailp2", (0.14, 0.14, 0.65), (dx - 1.1, y0 + L * 0.3 + L * 0.2 - 0.1, G.DECK + 0.3), darkw)
    # the end posts, taller, by the boat (the "dock posts" of S36)
    for sx in (-1, 1):
        kit.box(f"endpost{sx}", (0.26, 0.26, 2.2), (dx + sx * 1.15, y1 + 0.1, G.DECK + 0.45), darkw)
    kit.cyl("endcap1", 0.19, 0.1, (dx - 1.15, y1 + 0.1, G.DECK + 1.6), pl("#c9c2b4", 0.7), n=10)
    kit.cyl("endcap2", 0.19, 0.1, (dx + 1.15, y1 + 0.1, G.DECK + 1.6), pl("#c9c2b4", 0.7), n=10)
    # my bare feet and shins hang off the dock's end in S01a only
    skin = pl("#dca97c", 0.7, spec=0.1)
    W["feet"] = kit.empty("feet", (dx + 0.45, y1 + 0.0, G.DECK), None)
    for sx in (-1, 1):
        kit.box(f"feet.thigh{sx}", (0.3, 0.7, 0.28), (sx * 0.28, -0.4, 0.14), pl("#2f5fc4", 0.7), W["feet"], bevel=0.05)
        kit.box(f"feet.shin{sx}", (0.24, 0.26, 0.34), (sx * 0.28, 0.1, -0.17), skin, W["feet"], bevel=0.04)
        kit.box(f"feet.foot{sx}", (0.24, 0.42, 0.13), (sx * 0.28, 0.2, -0.4), skin, W["feet"], bevel=0.05)

    # the rowboat: a red hull, a pale bench, two oars that Grandma leans (rotated about the oarlock)
    boat = kit.empty("boat", (G.BOAT_HOME[0], G.BOAT_HOME[1], WZ), None)
    W["boat"] = boat
    kit.box("boat.floor", (1.25, 3.0, 0.12), (0, 0, 0.12), red, boat, bevel=0.03)
    for sx in (-1, 1):
        kit.box(f"boat.side{sx}", (0.14, 3.2, 0.5), (sx * 0.64, 0, 0.3), red, boat, bevel=0.04)
        kit.box(f"boat.trim{sx}", (0.18, 3.25, 0.06), (sx * 0.66, 0, 0.57), white, boat)
    kit.box("boat.bow", (1.0, 0.6, 0.48), (0, -1.7, 0.3), red, boat, bevel=0.1, rot=(0, 0, 0))
    kit.box("boat.stern", (1.3, 0.14, 0.5), (0, 1.55, 0.32), red, boat, bevel=0.04)
    kit.box("boat.bench", (1.2, 0.36, 0.08), (0, 0.25, 0.36), pl("#e8d6a8", 0.7), boat)
    kit.box("boat.bench2", (1.2, 0.34, 0.08), (0, -0.85, 0.36), pl("#e8d6a8", 0.7), boat)
    brass = pl("#d8b04a", 0.35, spec=0.6)
    for sx in (-1, 1):
        kit.box(f"boat.lock{sx}", (0.2, 0.2, 0.12), (sx * 0.7, 0.25, 0.64), brass, boat, bevel=0.02)
    # the tally: two silver strokes scratched on the starboard oarlock (a plain count of two)
    for k in range(2):
        kit.box(f"boat.stroke{k}", (0.012, 0.15, 0.012), (0.8 + 0.0, 0.25 - 0.05 + k * 0.1, 0.705), pl("#e4e9f0", 0.3, spec=0.9),
                boat, rot=(0, 0, 0))
    # oar: a pivot at the starboard oarlock; the shaft goes out and down; silver scuff along one side
    oar = kit.empty("oar", (0.7, 0.25, 0.7), boat)
    W["oar"] = oar
    wood = pl("#b98a56", 0.6, spec=0.15)
    kit.box("oar.shaft", (0.07, 0.07, 2.6), (0, 0, 1.3), wood, oar, bevel=0.01)
    kit.box("oar.blade", (0.04, 0.3, 0.7), (0, 0, 2.55), wood, oar, bevel=0.01)
    kit.box("oar.scuff", (0.02, 0.075, 2.3), (-0.04, 0, 1.15), pl("#eef3fb", 0.25, spec=0.95), oar)
    kit.box("oar.scuffy", (0.075, 0.02, 2.3), (0, -0.04, 1.15), pl("#eef3fb", 0.25, spec=0.95), oar)
    kit.box("oar.scuffb", (0.02, 0.3, 0.55), (-0.025, 0, 2.55), pl("#eef3fb", 0.25, spec=0.95), oar)
    # a second oar rests in its lock on the other side
    oar2 = kit.empty("oar2", (-0.7, 0.25, 0.7), boat)
    kit.box("oar2.shaft", (0.07, 0.07, 2.2), (0, 0, 0.9), wood, oar2, bevel=0.01)
    kit.box("oar2.blade", (0.04, 0.3, 0.6), (0, 0, 2.1), wood, oar2, bevel=0.01)
    oar2.rotation_euler = (-92 * D2R, 0, 4 * D2R)

    # ------------------------------------------------------------------ the white house and its green screen porch
    hx, hy = G.HOUSE
    kit.box("house", (14, 8, 5.5), (hx, hy, 2.75), cream, bevel=0.05)
    kit.box("roof", (15.6, 9.6, 0.5), (hx, hy, 5.75), pl("#8a4a3a", 0.7), bevel=0.04)
    kit.box("roofp", (15.4, 4.8, 0.4), (hx, hy, 6.6), pl("#8a4a3a", 0.7), rot=(0.0, 0, 0))
    kit.box("chim", (1.2, 1.2, 3.0), (hx + 4, hy + 1, 7.0), pl("#b0584a", 0.8))
    glass = pl("#9fd0e8", 0.2, spec=0.8)
    for wxo in (-4.5, -1.5, 4.5):
        kit.box(f"hwin{wxo}", (1.4, 0.12, 1.5), (hx + wxo, hy + 4.04, 3.6), glass)
        kit.box(f"hwinf{wxo}", (1.8, 0.1, 1.9), (hx + wxo, hy + 4.02, 3.6), green)
    py = G.PORCH_Y
    kit.box("porchfloor", (11, 3.6, 0.2), (hx, py, 0.15), pl("#b5895a", 0.8))
    kit.box("porchroof", (11.4, 3.9, 0.25), (hx, py, 3.2), green)
    for k in (0, 2, 3, 5):
        kit.box(f"porchpost{k}", (0.2, 0.2, 3.0), (hx - 5.2 + k * 2.08, py + 1.7, 1.6), cream)
    kit.box("hdoor", (1.3, 0.12, 2.4), (hx, hy + 4.04, 1.4), pl("#2f8a52", 0.6))
    # breakfast: a small table with a cup and a coffee pot, and two chairs
    tx, ty = hx + 3.2, py + 0.2
    kit.box("table", (1.6, 1.0, 0.1), (tx, ty, 0.9), darkw)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"tleg{sx}{sy}", (0.1, 0.1, 0.75), (tx + sx * 0.7, ty + sy * 0.4, 0.52), darkw)
    kit.box("chair1", (0.55, 0.55, 0.08), (tx - 0.1, ty + 0.9, 0.55), darkw)
    kit.box("chair1b", (0.55, 0.08, 0.6), (tx - 0.1, ty + 1.2, 0.85), darkw)
    kit.cyl("cup.base", 0.17, 0.2, (tx + 0.3, ty + 0.1, 1.07), pl("#f6f1e6", 0.5), n=14)
    kit.cyl("cup.coffee", 0.14, 0.02, (tx + 0.3, ty + 0.1, 1.18), pl("#4a2c1a", 0.4), n=14)
    kit.box("cup.handle", (0.1, 0.04, 0.1), (tx + 0.5, ty + 0.1, 1.07), pl("#f6f1e6", 0.5))
    kit.cyl("pot.body", 0.14, 0.32, (tx - 0.4, ty - 0.1, 1.12), pl("#c9d2dc", 0.35, spec=0.6), n=14)
    kit.box("pot.spout", (0.14, 0.06, 0.06), (tx - 0.52, ty - 0.1, 1.2), pl("#c9d2dc", 0.35, spec=0.6))
    # the porch swing
    sx_ = hx - 3.6
    kit.box("swing.seat", (1.8, 0.7, 0.1), (sx_, py + 0.5, 0.75), darkw)
    kit.box("swing.back", (1.8, 0.1, 0.7), (sx_, py + 0.14, 1.1), darkw)
    for sx in (-1, 1):
        kit.box(f"swing.chain{sx}", (0.04, 0.04, 1.6), (sx_ + sx * 0.9, py + 0.5, 2.1), pl("#555555", 0.5))
    kit.box("swing.cushion", (1.6, 0.6, 0.12), (sx_, py + 0.5, 0.86), pl("#f2a8a0", 0.8))
    # a stone path and flowers on the lawn
    kit.box("path", (2.2, 16, 0.06), (hx, -49.0, 0.05), pl("#d8cdb8", 0.9, spec=0.05))
    # the boathouse (S30): a small shed near the shore, west of the dock
    kit.box("shed", (4.0, 3.0, 2.8), (-9.0, -50.5, 1.4), pl("#a85a3a", 0.8))
    kit.box("shedroof", (4.6, 3.6, 0.3), (-9.0, -50.5, 3.0), pl("#6b4a32", 0.8))
    kit.box("shedeave", (4.6, 0.2, 0.6), (-9.0, -52.1, 2.7), pl("#6b4a32", 0.8))

    # ------------------------------------------------------------------ the neighbours' docks, beach, float
    for nm, (nx, ny), ln in (("n1", G.NDOCK1, 14.0), ("n2", G.NDOCK2, 10.0), ("n3", (-25.0, -38.0), 11.0)):
        for i in range(int(ln / 0.55)):
            kit.box(f"{nm}.pl{i}", (1.8, 0.5, 0.1), (nx, ny - ln + 0.3 + i * 0.55, G.DECK - 0.05), gray if i % 2 else gray2)
        for k in range(int(ln / 3.2) + 1):
            for sx in (-1, 1):
                kit.box(f"{nm}.po{k}{sx}", (0.2, 0.2, 1.8), (nx + sx * 0.85, ny - ln + 0.4 + k * 3.2, G.DECK - 0.6), darkw)
    # a mug on the near dock post (S07b) and a coffee pot at the neighbour's dock edge (S07a)
    kit.cyl("nmug", 0.12, 0.2, (G.NDOCK1[0] - 0.9, G.NDOCK1[1] - 3.0, G.DECK + 1.1), pl("#f2a8a0", 0.5), n=12)
    kit.box("nmugpost", (0.22, 0.22, 1.0), (G.NDOCK1[0] - 0.9, G.NDOCK1[1] - 3.0, G.DECK + 0.45), darkw)
    W["steam"] = []
    sm = pl("#b9d6e4", 0.9, spec=0.0)
    for k in range(4):
        ob = kit.sphere(f"steam{k}", 0.05, (G.NDOCK1[0] - 0.9, G.NDOCK1[1] - 3.0, G.DECK + 1.5), sm, seg=10)
        noshadow(ob)
        W["steam"].append(ob)
    W["lakesteam"] = []
    for k in range(14):
        ob = kit.sphere(f"lsteam{k}", 0.3, (0, 0, WZ), sm, seg=10)
        noshadow(ob)
        W["lakesteam"].append(ob)
    pot_m = pl("#c9d2dc", 0.35, spec=0.6)
    W["nbrpot"] = kit.cyl("nbrpot", 0.16, 0.3, (G.NDOCK1[0] + 0.4, G.NDOCK1[1] + 0.9, WZ + 0.1), pot_m, n=14)
    kit.box("nbrpot.spout", (0.14, 0.06, 0.06), (G.NDOCK1[0] + 0.28, G.NDOCK1[1] + 0.9, WZ + 0.2), pot_m)
    # the old man's chair and line
    kit.box("fchair", (0.5, 0.5, 0.08), (G.NDOCK2[0], G.NDOCK2[1] - 1.6, G.DECK + 0.35), darkw)
    kit.box("frod", (0.04, 3.0, 0.04), (G.NDOCK2[0] + 0.5, G.NDOCK2[1] + 0.6, G.DECK + 1.5), darkw, rot=(-0.5, 0, 0))
    kit.box("fline", (0.012, 0.012, 2.4), (G.NDOCK2[0] + 0.5, G.NDOCK2[1] + 2.1, G.DECK + 0.4), pl("#dddddd", 0.5))
    # the swim float
    kit.box("float", (2.4, 2.4, 0.3), (-26.0, -20.0, WZ + 0.05), pl("#ffd23f", 0.6))
    kit.box("float2", (2.0, 2.0, 0.05), (-26.0, -20.0, WZ + 0.22), pl("#ffffff", 0.7))
    # the afternoon crowd's towels and an umbrella on the beach
    kit.box("towel1", (1.6, 0.9, 0.04), (G.BEACH[0] - 7, G.BEACH[1] - 4, 0.12), pl("#ff6a5a", 0.9))
    kit.box("towel2", (1.6, 0.9, 0.04), (G.BEACH[0] - 9, G.BEACH[1] - 2, 0.12), pl("#4aa8ff", 0.9))
    kit.cyl("umb.pole", 0.04, 2.2, (G.BEACH[0] - 8, G.BEACH[1] - 5, 1.1), pl("#dddddd", 0.5), n=8)
    kit.cyl("umb.top", 1.4, 0.2, (G.BEACH[0] - 8, G.BEACH[1] - 5, 2.2), pl("#ffd23f", 0.7), n=18, r2=0.1)

    # ------------------------------------------------------------------ the glow under the lake (three soft discs)
    W["glowdisc"] = kit.empty("glowdisc", (G.MID[0], G.MID[1], WZ + 0.1), None)
    for i, (r_, col_, st) in enumerate([(9.0, "#1f8fa0", 0.28), (6.2, "#3fb0c8", 0.38), (3.9, "#6fcfe6", 0.5),
                                        (2.0, "#a8e4f6", 0.62)]):
        ob = kit.cyl(f"gd{i}", r_, 0.02, (0, 0, 0.012 * i), kit.emit(col_, st, f"gdm{i}"), W["glowdisc"], n=40)
        noshadow(ob)
    W["gdock"] = kit.empty("gdock", (0.45, -28.6, WZ + 0.1), None)
    for i, (r_, col_, st) in enumerate([(3.2, "#2fa0b4", 0.42), (2.2, "#5cc0da", 0.55), (1.3, "#8fd8ea", 0.7)]):
        ob = kit.cyl(f"gdk{i}", r_, 0.02, (0, 0, 0.012 * i), kit.emit(col_, st, f"gdkm{i}"), W["gdock"], n=32)
        noshadow(ob)
    # its reflection off the dock (S08a): a pale disc in strips so ripples break it
    W["refl"] = kit.empty("refl", (0.3, -27.5, WZ + 0.05), None)
    rm = kit.emit("#b9d2f2", 0.55, "reflm")
    rm2 = kit.emit("#6f8fd8", 0.7, "reflm2")
    kit.cyl("refl.halo", 3.4, 0.02, (0, 0, 0), rm2, W["refl"], n=40)
    rr_ = random.Random(8)
    for i in range(9):
        yy = -1.9 + i * 0.47
        w_ = 2 * math.sqrt(max(0.05, 2.5 ** 2 - yy ** 2)) * (0.8 + 0.25 * rr_.random())
        kit.box(f"refl.s{i}", (w_, 0.34, 0.02), (rr_.random() * 0.4 - 0.2, yy, 0.02), rm, W["refl"])
    for i in range(4):
        kit.box(f"refl.rip{i}", (1.2 + 2.0 * rr_.random(), 0.05, 0.02), (rr_.random() * 2 - 1, -1.2 + i * 0.8 + rr_.random() * 0.3, 0.035), pl("#24346b", 0.4, spec=0.0), W["refl"])
    noshadow(W["refl"])

    # ------------------------------------------------------------------ the rising cap (a big sphere under the lake)
    mats = moon_mats(kit)
    R = G.DOME_R
    W["moon"] = kit.empty("moon", (G.MID[0], G.MID[1], -R - 3.0), None)
    ms = kit.sphere("moon.sph", R, (0, 0, 0), mats[0], W["moon"], seg=48)
    cratered(kit, W["moon"], "moon", R, 40, 70, 11, 0.5, 1.5, mats)
    noshadow(W["moon"])
    # water pouring off the cap
    W["pour"] = []
    rng = random.Random(5)
    pm = kit.emit("#8fc4ee", 0.7, "pourm")
    for i in range(16):
        a = rng.random() * 2 * math.pi
        rr = 3.0 + rng.random() * 8.0
        ob = kit.box(f"pour{i}", (0.18 + rng.random() * 0.12, 0.18, 1.6), (G.MID[0] + rr * math.cos(a), G.MID[1] + rr * math.sin(a), WZ), pm)
        noshadow(ob)
        W["pour"].append((ob, rr, a, rng.random()))

    # ------------------------------------------------------------------ the lake bed (U), the moon patch
    ux, uy = G.U
    kit.plane("ufloor", (160, 160), (ux, uy, G.UFLOOR), kit.grime("#235f6c", 0.7, 1.1, "usand", 0.95))
    kit.plane("usurf", (160, 160), (ux, uy, 14.0), kit.emit("#4fd0d8", 0.55, "usurfm"), rot=(math.pi, 0, 0))
    for i in range(14):
        a = i / 14 * 2 * math.pi
        kit.box(f"urock{i}", (1.6, 1.2, 0.9), (ux + 22 * math.cos(a) * (0.7 + 0.5 * (i % 3)), uy + 22 * math.sin(a) * (0.7 + 0.5 * (i % 2)), G.UFLOOR + 0.3),
                pl("#9aa89a", 0.9, spec=0.05), rot=(0, 0, a), bevel=0.2)
    for i in range(10):
        a = i / 10 * 2 * math.pi + 0.3
        kit.cyl(f"uweed{i}", 0.12, 3.0, (ux + 14 * math.cos(a), uy + 14 * math.sin(a), G.UFLOOR + 1.5), pl("#3f9a5a", 0.8), n=6, r2=0.05)
    UR = 40.0
    W["umoon"] = kit.empty("umoon", (ux, uy, G.UTOP - UR), None)
    kit.sphere("umoon.sph", UR, (0, 0, 0), mats[0], W["umoon"], seg=64)
    cratered(kit, W["umoon"], "um", UR, 44, 34, 23, 1.2, 3.6, mats)
    noshadow(W["umoon"])
    # fish for S06
    W["fish"] = []
    fm = [pl("#ff9a3a", 0.5), pl("#ffd23f", 0.5), pl("#ff6a5a", 0.5)]
    for i in range(14):
        f = kit.empty(f"fish{i}", (ux, uy, G.UFLOOR + 3), None)
        kit.box(f"fish{i}.body", (0.1, 0.5, 0.26), (0, 0, 0), fm[i % 3], f, bevel=0.04)
        kit.box(f"fish{i}.tail", (0.04, 0.18, 0.34), (0, 0.32, 0), fm[(i + 1) % 3], f)
        kit.box(f"fish{i}.fin", (0.03, 0.22, 0.12), (0, 0.0, 0.17), fm[(i + 1) % 3], f)
        for sx_ in (-1, 1):
            kit.box(f"fish{i}.eye{sx_}", (0.02, 0.05, 0.05), (sx_ * 0.055, -0.19, 0.04), pl("#1a1a2a", 0.4), f)
        W["fish"].append((f, i))
    W["bubbles"] = []
    bm = pl("#e8f8ff", 0.2, spec=0.9)
    for i in range(26):
        W["bubbles"].append(kit.sphere(f"bub{i}", 0.07 + 0.04 * (i % 3), (ux, uy, 0), bm, seg=8))

    # ------------------------------------------------------------------ the wristwatch (S05b) at WATCH
    wx, wy = G.WATCH
    kit.plane("wbg", (30, 30), (wx, wy + 6, 0), pl("#bfe6ff", 0.9, spec=0.0), rot=(math.pi / 2, 0, 0))
    kit.box("wrist", (1.5, 1.1, 0.9), (wx, wy, 1.0), pl("#dca97c", 0.7, spec=0.1), bevel=0.15)
    kit.box("wband", (1.7, 1.3, 0.25), (wx, wy, 1.0), pl("#3a3f4a", 0.6))
    kit.cyl("wcase", 0.78, 0.18, (wx, wy - 0.05, 1.62), pl("#d8dce4", 0.3, spec=0.9), n=32)
    kit.cyl("wface", 0.68, 0.06, (wx, wy - 0.05, 1.72), pl("#fbf7ec", 0.5, spec=0.1), n=32)
    for k in range(12):
        a = k * math.pi / 6
        big = k % 3 == 0
        kit.box(f"wtick{k}", (0.06 if big else 0.035, 0.17 if big else 0.1, 0.02),
                (wx + 0.56 * math.sin(a), wy - 0.05 + 0.56 * math.cos(a), 1.76), pl("#1a2250", 0.5), rot=(0, 0, -a))
    # 11:59 -- the hour hand just short of 12, the minute hand just short of 12 (tiny gap to the left)
    kit.box("whour", (0.07, 0.34, 0.03), (wx - 0.02, wy - 0.05 + 0.15, 1.78), pl("#1a2250", 0.5), rot=(0, 0, 0.1))
    kit.box("wmin", (0.05, 0.5, 0.03), (wx - 0.02, wy - 0.05 + 0.24, 1.8), pl("#1a2250", 0.5), rot=(0, 0, 0.04))
    kit.box("wsec", (0.025, 0.55, 0.03), (wx + 0.02, wy - 0.05 + 0.2, 1.82), pl("#e0453a", 0.5), rot=(0, 0, -0.1))
    kit.cyl("wpin", 0.06, 0.05, (wx, wy - 0.05, 1.83), pl("#1a2250", 0.5), n=12)
    kit.light("wlight", "POINT", (wx, wy - 3, 4), 0.0, "#fff4e0", size=1.0, shadow=False)

    build_tag(kit)
    return {}


def _first_frame(kit, story):
    from blocky import faces
    R, H = faces.HEAD_R, faces.HEAD_H
    top = H / 2
    gh = bpy.data.objects.get("grandma.headg")
    if gh is not None:
        vm = kit.plastic("#f0509a", 0.6)
        kit.box("grandma.vband", (2 * R + 0.14, 2 * R + 0.14, 0.2), (0, 0.0, top - 0.02), vm, gh, bevel=0.05)
        kit.box("grandma.vbrim", (2 * R * 0.95, 0.85, 0.07), (0, -R - 0.4, top - 0.05), vm, gh, bevel=0.03)
        # a white bun on top and to the back of her head (an old woman's cue)
        hair = kit.plastic("#f4f4f6", 0.8)
        kit.sphere("grandma.bun", R * 0.5, (0, R * 0.45, top + R * 0.42), hair, gh, seg=12)
    W["inited"] = True


# ---------------------------------------------------------------------------------------------- animate
def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    look = look_at(tl, t)
    gains = {}
    # sun, fill, front, moonlight
    az, el = look["az"] * D2R, look["el"] * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    so = kit.LIGHTS["sun"]["obj"]
    so.location = d * 60
    kit.aim(so, (0, 0, 0))
    kit.LIGHTS["sun"]["light"].color = look["sun_col"]
    kit.LIGHTS["fill"]["light"].color = look["fill_col"]
    kit.LIGHTS["front"]["light"].color = look["front_col"]
    kit.LIGHTS["moonl"]["light"].color = look["moonl_col"]
    kit.LIGHTS["ufill"]["light"].color = (0.45, 0.8, 0.85)
    gains["sun"], gains["fill"], gains["front"] = look["sun"], look["fill"], look["front"]
    gains["moonl"], gains["ufill"] = look["moonl"], look["ufill"]
    gains["rim"] = look["rim"]
    kit.LIGHTS["rim"]["light"].color = (0.66, 0.75, 1.0)
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*look["sky"], 1.0)
    bg.inputs["Strength"].default_value = look["sky_str"]

    # the glow under the lake: discs and a point light that climbs when the moon rises
    gl = sample("glow", tl, t, {"g": 0.0, "z": -1.0, "e": 0.0, "disc": 1.0})
    gd = W["glowdisc"]
    gd.scale = (max(0.001, gl["disc"] * max(gl["g"], 0.02)), max(0.001, gl["disc"] * max(gl["g"], 0.02)), 1.0)
    _hide(gd, gl["g"] < 0.03 or gl["disc"] < 0.03)
    gob = kit.LIGHTS["glow"]["obj"]
    gob.location = (G.MID[0], G.MID[1], gl["z"])
    gains["glow"] = gl["e"]
    gdk = sample("gdock", tl, t, {"on": 0.0})
    _hide(W["gdock"], gdk["on"] < 0.5)
    rf = sample("refl", tl, t, {"v": 0.0})
    rs = max(0.001, rf["v"])
    W["refl"].scale = (rs, rs, 1.0)
    _hide(W["refl"], rf["v"] < 0.03)

    # the moon's cap rising
    mo = sample("moon", tl, t, {"top": -3.0})
    R = G.DOME_R
    W["moon"].location = (G.MID[0], G.MID[1], mo["top"] - R)
    _hide(W["moon"], mo["top"] < WZ + 0.05 or mo["top"] > 30)
    # water pouring down the cap's sides
    pr = sample("pour", tl, t, {"p": 0.0})
    for ob, rr, a, ph in W["pour"]:
        cz = mo["top"] - R
        surf = cz + math.sqrt(max(0.0, R * R - rr * rr)) if rr < R else WZ
        fall = ((t * 0.55 + ph) % 1.0)
        top_z = surf - fall * min(1.8, max(0.0, surf - WZ))
        ob.location = (G.MID[0] + rr * math.cos(a), G.MID[1] + rr * math.sin(a), max(WZ + 0.1, top_z))
        ob.hide_render = pr["p"] < 0.5 or surf < WZ + 0.4

    # the boat
    bt = sample("boat", tl, t, {"x": G.BOAT_HOME[0], "y": G.BOAT_HOME[1], "z": WZ, "rock": 0.0, "yaw": 0.0})
    rock = bt["rock"] * math.sin(t * 2.1) * 4.0 * D2R
    W["boat"].location = (bt["x"], bt["y"], bt["z"])
    W["boat"].rotation_euler = (rock * 0.6, rock, bt["yaw"] * D2R)
    oa = sample("oar", tl, t, {"a": 80.0, "b": 0.0, "dip": 0.0})
    # a: tilt out from the vertical (deg), b: swing about the lock (deg); the shaft hangs from the lock down into the water
    W["oar"].rotation_euler = (oa["b"] * D2R, 0, 0)
    W["oar"].rotation_euler = (oa["b"] * D2R, (180.0 - oa["a"]) * D2R, 0)
    # my feet in S01a
    ft = sample("feet", tl, t, {"on": 0.0})
    _hide(W["feet"], ft["on"] < 0.5)
    # the rule meter
    dl = sample("dial", tl, t, {"v": 0.55, "lit": 0.0})
    set_dial(W["tagd"], dl["v"], dl["lit"])
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
    tz = sample("tagzoom", tl, t, {"z": 0.0, "oy": 0.0})
    z = tz["z"]
    tag = W["tag"]
    s = 0.52 * w2 * (1.0 + 1.8 * z)
    tag.scale = (s, s, s)
    tag.location = ((-0.38 * (1 - z)) * w2, (0.585 * (1 - z) + 0.28 * z + tz["oy"]) * h2, -dist)

    # the lake steam (S02a), the mug steam (S07b), the coffee pot
    sc = sample("steam", tl, t, {"lake": 0.0, "mug": 0.0})
    for i, ob in enumerate(W["lakesteam"]):
        ph = (t * 0.25 + i * 0.37) % 1.0
        ob.location = (-2.5 + (i * 1.7) % 5.5 + math.sin(t + i) * 0.3, -29.0 + (i * 2.3) % 5.0, WZ + 0.3 + ph * 2.4)
        ob.scale = (1.0 + ph * 0.8, 1.0 + ph * 0.8, 1.0 + ph * 0.8)
        ob.hide_render = sc["lake"] < 0.5
    for i, ob in enumerate(W["steam"]):
        ph = (t * 0.45 + i / 4.0) % 1.0
        ob.location = (G.NDOCK1[0] - 0.9 + math.sin(ph * 7 + i * 2.1) * 0.13, G.NDOCK1[1] - 3.0 + math.cos(ph * 5 + i) * 0.06, G.DECK + 1.28 + ph * 0.75)
        ob.scale = (0.7 + ph * 1.2, 0.7 + ph * 1.2, 0.7 + ph * 1.2)
        ob.hide_render = sc["mug"] < 0.5

    # the lake bed (U): the glow over my hands, the moon rolling, fish, bubbles
    ug = sample("ug", tl, t, {"e": 0.0, "x": 0.0, "roll": 0.0, "z": 3.0})
    ul = kit.LIGHTS["uglow"]["obj"]
    ul.location = (G.U[0] + ug["x"], G.U[1], G.UTOP + ug["z"])
    gains["uglow"] = ug["e"]
    W["umoon"].rotation_euler = (0, 0, ug["roll"] * D2R)
    fs = sample("fish", tl, t, {"on": 0.0})
    for f, i in W["fish"]:
        ph = (t * 0.22 + i * 0.13) % 1.0
        sx = -16.0 + (i % 5) * 1.2
        sy = -7.0 + (i % 7) * 2.2
        tx_, ty_ = 1.5, 0.0
        px, py = sx + (tx_ - sx) * ph, sy + (ty_ - sy) * ph
        f.location = (G.U[0] + px, G.U[1] + py, G.UFLOOR + 6.9 + math.sin(t * 2 + i) * 0.25 + (i % 4) * 0.45)
        f.rotation_euler = (0, 0, math.atan2(tx_ - sx, -(ty_ - sy)) + math.sin(t * 9 + i) * 0.12)
        f.scale = (3.2, 3.2, 3.2)
        _hide(f, fs["on"] < 0.5)
    bb = sample("bubbles", tl, t, {"on": 0.0, "x": 0.0, "y": 0.0, "z": 0.0})
    for i, ob in enumerate(W["bubbles"]):
        ph = (t * 0.55 + i * 0.173) % 1.0
        ob.location = (G.U[0] + bb["x"] + math.sin(i * 2.3 + t) * 0.45 + (i % 5 - 2) * 0.12, G.U[1] + bb["y"] + math.cos(i * 1.7) * 0.4,
                       bb["z"] - 0.6 + ph * 3.2)
        ob.hide_render = bb["on"] < 0.5

    # who sits: legs straight out forward
    sits = {}
    for c in tl["cues"]:
        if c["name"] == "sit" and c["t"] <= t:
            sits[c["who"]] = c
    for who, c in sits.items():
        root = bpy.data.objects.get(who)
        if c.get("on") and root is not None:
            root.location.z += c.get("z", 0.6) - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    return gains
