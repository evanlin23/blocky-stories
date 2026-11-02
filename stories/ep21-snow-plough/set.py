"""Snow Plough (ep21): a single-lane mountain pass road in heavy snow, the plough, and the Marker.

Frames. The plough stays at the origin facing +y; everything else is the WORLD, which this file turns and slides
round the plough each frame (`drive` cues give the distance s up the road and the heading theta). So every
camera in story.json is in the plough's frame, and the road really does run past it. World coordinates: the road
runs along +y (the village at y < 0, the hut at y ~ 1240), 6.6 m wide (x -3.3 .. 3.3), the drop on the +x side
with 40 posts at x = 3.0 every 30 m, the mountain bank on -x. The plough drives in the outer lane (x = 1.6).
Heading 0 is going up; heading 180 degrees is coming down (posts then pass on the plough's left).

The interiors sit far off to the side: Odile's room at (500, 0) and the hut's stove room at (500, 300).

Cues read here (all optional; `at` is resolved to "t" by timeline):
- drive: {s, theta?}  the plough's place on the road and its heading (degrees). Keys are joined by straight lines;
  two keys at the same time make a cut. "ease": true smooths the segment that ends at this key.
- tod: {v}  0 night, 1 grey-lilac dawn, 2 pale gold; one continuous curve between the keys (the light plan)
- lights: {g, dur}  headlight level (never below 0.2), eased over dur
- marker: {x, y, vis, drift, snow}  the Marker's place in the world, faces +y (uphill, at the plough coming down)
- slide: {on}  the outer half of the road at post 23 has gone
- season: {v: snow|spring}; plough: {on}; van: {mode: none|parked|follow}; bag: {where}; table: {keys,bag,glass,cups}
- tally: {on}; square: {on}; newpost: {on}; wipers: {on}; psnow: {on} (snow hood on the plough)
Shot keys read here: "snow" (0..1, default 1) falling snow near the camera.
Acting keys read here: "hide_parts", "sit".
"""

from __future__ import annotations

import math
import os

import bpy
from mathutils import Vector as V

from blocky import faces

RIG_S = 0.34
ROAD = 3.3
POST_X = 3.0
PX = 0.6
NPOST = 40
SP = 30.0
SLID0, SLID1 = 665.0, 740.5
SLAB_Z = -13.0
BASE = {"odile": (500.0, 0.0), "hut": (500.0, 300.0)}

FOGC = {0: "#17233d", 1: "#8a8ea9", 2: "#e6d2a6"}
SUNC = {0: "#7f9ad8", 1: "#c9c5e6", 2: "#ffdca8"}
SUNE = {0: 0.8, 1: 1.6, 2: 3.0}
EXPO = {0: 0.0, 1: -0.25, 2: -0.6}


def hide_tree(root, flag):
    root.hide_render = flag
    for o in root.children_recursive:
        o.hide_render = flag


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


def lerp3(a, b, u):
    return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))


def cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def eased(cs, key, t, default):
    v = prev = default
    for c in cs:
        if c["t"] > t + 1e-9:
            break
        u = min(1.0, (t - c["t"]) / max(c.get("dur", 0.0), 1e-6))
        v = prev + (c[key] - prev) * ss(u)
        if u >= 1.0:
            prev = c[key]
    return v


def last(cs, t, default=None):
    cs = [c for c in cs if c["t"] <= t + 1e-9]
    return cs[-1] if cs else default


def piece(cs, key, t, default):
    """Straight lines between keys; two keys at one time are a cut; 'ease' smooths the segment ending at a key."""
    if not cs:
        return default
    i = max([k for k, c in enumerate(cs) if c["t"] <= t + 1e-9], default=-1)
    if i < 0:
        return cs[0].get(key, default)
    a = cs[i]
    if i + 1 < len(cs) and cs[i + 1]["t"] > a["t"]:
        b = cs[i + 1]
        u = (t - a["t"]) / (b["t"] - a["t"])
        if b.get("ease"):
            u = ss(u)
        return lerp(a.get(key, default), b.get(key, default), u)
    return a.get(key, default)


def travelled(cs, t):
    """Distance driven so far (for the falling snow)."""
    d, prev = 0.0, None
    for c in cs:
        if c["t"] > t:
            break
        if prev is not None:
            d += abs(c["s"] - prev["s"]) if c["t"] > prev["t"] else 0.0
        prev = c
    if prev is not None and cs:
        s_now = piece(cs, "s", t, prev["s"])
        d += abs(s_now - prev["s"])
    return d


# ------------------------------------------------------------------------------------------------ small parts


def quad(kit, name, pts, mat, parent):
    return kit.mesh_obj(name, [tuple(p) for p in pts], [tuple(range(len(pts)))], mat, parent)


def fog_emit(kit, name, hexc, strength):
    """An emissive material that goes through the fog and keeps its Emission node, so a cue can change its level."""
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = strength
    kit._fogged(m, e.outputs[0])
    return m, e


def plain_emit(kit, name, hexc, strength):
    """Emissive and not fogged (the sun disc, windows seen from inside a lit room)."""
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = strength
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    return m, e


def metalish(kit, hexc, rough=0.5):
    return kit.plastic(hexc, rough, name=f"m {hexc} {rough}", spec=0.6)


# ------------------------------------------------------------------------------------------------ the world


def build_world(kit, ctx):
    W = kit.empty("world")
    ctx["W"] = W
    snow = kit.grime("#d6e0ef", dark=0.84, scale=0.7, name="snow", rough=0.85)
    cliff = kit.grime("#9db0cc", dark=0.5, scale=2.4, name="cliff", rough=0.9)
    pine = kit.plastic("#0f1d1c", 0.9, name="pine")
    stone = kit.cobbles("#4a4c52", "#7b7873", "#1d1d20", scale=1.2, wet=0.1, name="stone")
    spring = kit.grime("#5e8a44", dark=0.7, scale=1.6, name="spring grass", rough=0.9)
    asphalt = kit.grime("#3a3d44", dark=0.7, scale=2.5, name="asphalt", rough=0.8)
    ctx["M"] = dict(snow=snow, cliff=cliff, pine=pine, stone=stone, spring=spring, asphalt=asphalt)

    snow_objs, spring_objs, pre, post, pre_sp = [], [], [], [], []

    def road(name, x0, x1, y0, y1, bucket):
        o = quad(kit, name, [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], snow, W)
        bucket.append(o)
        a = quad(kit, name + " sp", [(x0, y0, 0.01), (x1, y0, 0.01), (x1, y1, 0.01), (x0, y1, 0.01)], asphalt, W)
        (pre_sp if bucket is pre else spring_objs).append(a)
        return o

    # the road in four pieces: the outer half of the slid stretch is its own piece
    road("road A", -ROAD, ROAD, 0, SLID0, snow_objs)
    road("road Bin", -ROAD, 0, SLID0, SLID1, snow_objs)
    road("road Bout", 0, ROAD, SLID0, SLID1, pre)
    road("road C", -ROAD, ROAD, SLID1, 1300, snow_objs)
    # the village flat and the hut pad
    quad(kit, "village", [(-90, -170, 0), (90, -170, 0), (90, 0, 0), (-90, 0, 0)], snow, W)
    spring_objs.append(quad(kit, "village sp", [(-90, -170, 0.01), (90, -170, 0.01), (90, 0, 0.01), (-90, 0, 0.01)], spring, W))
    quad(kit, "pad", [(-30, 1190, 0), (-ROAD, 1190, 0), (-ROAD, 1300, 0), (-30, 1300, 0)], snow, W)
    quad(kit, "farflat", [(-60, 1300, 0), (60, 1300, 0), (60, 1500, 0), (-60, 1500, 0)], snow, W)
    # the mountain bank on -x
    for nm, mat, ob in (("bank", snow, snow_objs), ("bank sp", spring, spring_objs)):
        z0 = 0.02 if "sp" in nm else 0
        ob.append(quad(kit, nm + "1", [(-ROAD, 0, z0), (-7, 0, 2.4 + z0), (-7, 1190, 2.4 + z0), (-ROAD, 1190, z0)], mat, W))
        ob.append(quad(kit, nm + "2", [(-7, 0, 2.4), (-45, 0, 17), (-45, 1190, 17), (-7, 1190, 2.4)], mat, W))
    # the drop on +x
    def slope(nm, y0, y1, mat, bucket):
        bucket.append(quad(kit, nm, [(ROAD, y0, 0), (45, y0, -33), (45, y1, -33), (ROAD, y1, 0)], mat, W))
    slope("slope A", 0, SLID0, snow, snow_objs)
    slope("slope B", SLID0, SLID1, snow, pre)
    slope("slope C", SLID1, 1300, snow, snow_objs)
    for nm, y0, y1 in (("slope A sp", 0, SLID0), ("slope C sp", SLID1, 1300)):
        spring_objs.append(quad(kit, nm, [(ROAD, y0, 0.02), (45, y0, -33), (45, y1, -33), (ROAD, y1, 0.02)], spring, W))
    # the slide: the outer half gone, a raw cut, the old slab lying below
    gully = quad(kit, "gully", [(0, SLID0, -13.5), (45, SLID0, -40), (45, SLID1, -40), (0, SLID1, -13.5)], snow, W)
    cutwall = quad(kit, "cut wall", [(0, SLID0, 0), (0, SLID0, -13.5), (0, SLID1, -13.5), (0, SLID1, 0)], cliff, W)
    prof = [(0, 0), (ROAD, 0), (45, -33), (45, -40), (0, -13.5)]
    endwall1 = quad(kit, "end wall 1", [(x, SLID1, z) for x, z in prof], cliff, W)
    endwall0 = quad(kit, "end wall 0", [(x, SLID0, z) for x, z in reversed(prof)], cliff, W)
    slab = kit.box("slab", (ROAD, 36, 0.8), (ROAD / 2, 690.0, SLAB_Z - 0.4), snow, W, rot=(0, math.radians(7), 0), bevel=0.12)
    rub = []
    for k in range(9):
        h = kit.hash01(k, 3)
        rub.append(kit.box(f"rubble{k}", (1.2 + 2 * h, 1.4 + h, 0.7 + h), (0.5 + 4 * kit.hash01(k, 5), 676 + 56 * kit.hash01(k, 9),
                                                                          SLAB_Z - 1.6 - 5 * kit.hash01(k, 11)), cliff, W,
                           rot=(0.3 * h, 0.2, 0.9 * h), bevel=0.2))
    post.extend([gully, cutwall, endwall1, endwall0, slab] + rub)
    ctx.update(snow_objs=snow_objs, spring_objs=spring_objs, pre=pre, post=post, pre_sp=pre_sp)

    # pines down the drop
    for k in range(150):
        y = -120 + k * 9.6 + 4 * kit.hash01(k, 1)
        x = 10 + 22 * kit.hash01(k, 2)
        z = -(x - ROAD) * 0.74 - 1.0
        if SLID0 - 20 < y < SLID1 + 20 and x < 30:
            continue
        r = 1.1 + 0.9 * kit.hash01(k, 4)
        kit.cyl(f"pine{k}", r, 5.5, (x, y, z + 2.2), pine, W, n=7, r2=0.05)
        kit.cyl(f"pine{k}b", r * 1.4, 4.5, (x, y, z + 0.4), pine, W, n=7, r2=0.1)

    # posts
    orange = kit.plastic("#c4501e", 0.6, name="post orange")
    black = kit.plastic("#0b0b0d", 0.5, name="post black")
    ctx["posts"] = {}
    for i in range(1, NPOST + 1):
        root = kit.empty(f"post{i}", (POST_X, SP * i, 0), W)
        kit.box(f"post{i}.shaft", (0.12, 0.12, 2.0), (0, 0, 1.0), orange, root, bevel=0.015)
        kit.box(f"post{i}.cap", (0.15, 0.15, 0.2), (0, 0, 2.05), black, root, bevel=0.02)
        m, e = fog_emit(kit, f"refl{i}", "#ffb03a", 0.0)
        sph = kit.sphere(f"post{i}.eye", 0.075, (0, 0, 1.72), m, root, seg=10)
        sph.scale = (0.9, 1.5, 0.9)
        ctx["posts"][i] = {"root": root, "node": e}
    ctx["slab_post_pos"] = (2.9, 690.0, SLAB_Z + 0.35 * 0 + 0.55)
    # the new post, in spring
    root = kit.empty("newpost", (PX, SLID1 + 0.3, 0), W)
    o2 = kit.plastic("#d9561d", 0.5, name="new orange")
    kit.box("newpost.shaft", (0.12, 0.12, 2.0), (0, 0, 1.0), o2, root, bevel=0.015)
    kit.box("newpost.cap", (0.15, 0.15, 0.2), (0, 0, 2.05), black, root, bevel=0.02)
    m, e = fog_emit(kit, "refl new", "#ffb03a", 0.0)
    sph = kit.sphere("newpost.eye", 0.075, (0, 0, 1.72), m, root, seg=10)
    sph.scale = (0.9, 1.5, 0.9)
    ctx["newpost"] = {"root": root, "node": e}

    # the hut and the parked van at the top
    hut = kit.empty("hut", (-8.0, 1240.0, 0), W)
    kit.box("hut.walls", (5.0, 4.2, 2.6), (0, 0, 1.3), stone, hut, bevel=0.05)
    kit.box("hut.roof", (5.6, 4.8, 0.5), (0, 0, 2.85), snow, hut, bevel=0.15)
    wm, _ = plain_emit(kit, "hut window", "#f2a050", 0.9)
    kit.box("hut.win", (0.02, 0.9, 0.7), (2.52, 0.2, 1.5), wm, hut)
    dark = kit.plastic("#1a1d22", 0.7, name="dark door")
    kit.box("hut.door", (0.04, 0.9, 1.9), (2.52, -1.3, 1.0), dark, hut)
    ctx["hut_pos"] = (-8.0, 1240.0)
    ctx["van_parked"] = build_van(kit, "vanP", W, (-3.8, 1226.0, 0), yaw=0.35)
    ctx["marker"] = build_marker(kit, ctx, W)
    sq = kit.box("square", (1.8, 0.7, 0.02), (PX, SLID1 + 0.7, 0.012), kit.plastic("#8b9dba", 0.95, name="pressed"), W)
    ctx["square"] = sq
    # the sun, far off
    sm, se = plain_emit(kit, "sun disc", "#fff0c8", 9.0)
    sun = kit.sphere("sun disc", 14.0, (-60, -520, 40), sm, W, seg=16)
    ctx["sundisc"], ctx["sundisc_node"] = sun, se
    build_village(kit, ctx, W, stone, snow)
    pm, pn = plain_emit(kit, "plant glint", "#ffb03a", 0.0)
    ctx["plant"] = kit.sphere("plant glint", 0.55, (2.9, 690.0, SLAB_Z + 1.9), pm, W, seg=8)
    ctx["plant_node"] = pn
    fm2, _ = plain_emit(kit, "far light", "#f2b36b", 3.0)
    ctx["farlight"] = kit.sphere("far light", 1.3, (-14.0, 300.0, 6.5), fm2, W, seg=8)


def build_van(kit, name, parent, loc, yaw=0.0):
    """The chemist's small white van. The cab is open at the front (a windscreen frame, not glass) so Bram can sit in it."""
    root = kit.empty(name, loc, parent, rot=(0, 0, yaw))
    white = kit.plastic("#e9edf0", 0.55, name="van white")
    dark = kit.plastic("#16181c", 0.6, name="van dark")
    kit.box(f"{name}.body", (2.1, 3.0, 1.9), (0, -1.4, 1.55), white, root, bevel=0.1)
    kit.box(f"{name}.floor", (2.1, 2.4, 0.2), (0, 1.1, 0.7), dark, root)
    kit.box(f"{name}.roof", (2.1, 2.4, 0.15), (0, 1.1, 2.55), white, root, bevel=0.06)
    kit.box(f"{name}.seat", (0.8, 0.5, 0.35), (-0.5, 0.65, 0.95), dark, root)
    for sx in (-1, 1):
        kit.box(f"{name}.side{sx}", (0.08, 2.4, 0.7), (sx * 1.0, 1.1, 1.0), white, root)
        kit.box(f"{name}.pil{sx}", (0.12, 0.12, 1.2), (sx * 0.98, 2.25, 1.95), white, root)
    kit.box(f"{name}.dash", (1.9, 0.5, 0.45), (0, 1.95, 0.95), dark, root)
    kit.box(f"{name}.nose", (2.1, 1.0, 0.95), (0, 2.7, 0.95), white, root, bevel=0.08)
    kit.box(f"{name}.under", (2.0, 5.8, 0.3), (0, 0.3, 0.45), dark, root)
    for sx in (-1, 1):
        for y in (-1.6, 2.1):
            kit.cyl(f"{name}.w{sx}{y}", 0.45, 0.35, (sx * 1.05, y, 0.45), dark, root, rot=(0, math.radians(90), 0), n=12)
    hm, _ = fog_emit(kit, f"{name} lamp", "#f4f8ff", 5.0)
    for sx in (-1, 1):
        kit.sphere(f"{name}.lamp{sx}", 0.17, (sx * 0.7, 3.22, 0.95), hm, root, seg=8)
    return root


def build_village(kit, ctx, W, stone, snow):
    plaster = kit.grime("#8c8478", dark=0.6, scale=2.0, name="cottage wall", rough=0.9)
    roofm = kit.plastic("#cfd9e8", 0.9, name="cottage roof")
    wm, wnode = plain_emit(kit, "cottage window", "#f2a050", 0.8)
    ctx["win_nodes"] = [wnode]
    spots = [(-9.0, -20.0, 0), (-14, -52, 90), (16, -34, -90), (18, -78, -80), (-20, -90, 85), (-8, -118, 90), (12, -122, -90)]
    for k, (x, y, yaw) in enumerate(spots):
        r = kit.empty(f"cottage{k}", (x, y, 0), W, rot=(0, 0, math.radians(yaw)))
        mat = stone if k % 2 else plaster
        kit.box(f"cottage{k}.walls", (4.4, 5.8, 2.6), (0, 0, 1.3), mat, r, bevel=0.04)
        kit.box(f"cottage{k}.roofa", (2.8, 6.4, 0.25), (-1.1, 0, 3.15), roofm, r, rot=(0, math.radians(-30), 0), bevel=0.05)
        kit.box(f"cottage{k}.roofb", (2.8, 6.4, 0.25), (1.1, 0, 3.15), roofm, r, rot=(0, math.radians(30), 0), bevel=0.05)
        kit.box(f"cottage{k}.chim", (0.5, 0.5, 1.1), (1.2, 1.2, 3.7), stone, r, bevel=0.03)
        if k == 0:
            kit.box("cottage0.win", (0.03, 1.1, 0.9), (2.22, -0.5, 1.5), wm, r)
            kit.box("cottage0.win2", (0.03, 0.8, 0.9), (2.22, 1.5, 1.5), wm, r)
        elif k in (3, 5):
            kit.box(f"cottage{k}.win", (0.03, 0.9, 0.8), (2.22, 0.3, 1.5), wm, r)
    # a yard fence for Odile's: low posts
    fence = kit.plastic("#4a3a2a", 0.8, name="fence")
    for j in range(6):
        kit.box(f"fence{j}", (0.1, 0.1, 0.9), (-5.5 + 0.0, -26.5 + j * 1.0, 0.45), fence, W)


# ------------------------------------------------------------------------------------------------ the Marker


def build_marker(kit, ctx, W):
    """The Marker: a person built as a road post and squashed. 1.4 m tall, 1.8 m wide, no neck, the black cap
    flush with the shoulders, two arm lines moulded flat in its sides, two amber reflectors for eyes. Built once;
    posed per shot by the 'marker' cue. It faces +y (uphill)."""
    root = kit.empty("marker", (0, 0, 0), W)
    orange = kit.plastic("#9a3f18", 0.75, name="marker orange")
    black = kit.plastic("#0b0b0d", 0.5, name="marker black")
    lighter = kit.plastic("#b5521f", 0.6, name="marker arm paint")
    snowm = kit.plastic("#dfe7f3", 0.95, name="marker snow")
    kit.box("marker.body", (1.8, 0.5, 1.05), (0, 0, 0.525), orange, root, bevel=0.03)
    kit.box("marker.cap", (1.82, 0.52, 0.35), (0, 0, 1.225), black, root, bevel=0.03)
    for sx in (-1, 1):
        kit.box(f"marker.arm{sx}", (0.12, 0.04, 0.78), (sx * 0.74, 0.265, 0.58), lighter, root, bevel=0.015)
        kit.box(f"marker.hand{sx}", (0.26, 0.14, 0.26), (sx * 0.78, 0.31, 0.34), lighter, root, bevel=0.03)
    nodes = []
    for sx in (-1, 1):
        m, e = fog_emit(kit, f"marker eye {sx}", "#ffb03a", 0.0)
        s = kit.sphere(f"marker.eye{sx}", 0.17, (sx * 0.42, 0.25, 1.2), m, root, seg=12)
        s.scale = (1.0, 0.3, 1.0)
        nodes.append(e)
    sn = []
    sn.append(kit.box("marker.snow1", (1.7, 0.46, 0.06), (0, 0, 1.42), snowm, root, bevel=0.03))
    sn.append(kit.box("marker.snow2", (0.5, 0.4, 0.05), (0.5, 0, 1.46), snowm, root, bevel=0.02))
    drift = kit.box("marker.drift", (1.9, 0.9, 0.6), (0, 0.65, 0.2), snowm, root, rot=(math.radians(-18), 0, 0), bevel=0.15)
    return {"root": root, "eyes": nodes, "snow": sn, "drift": drift}


# ------------------------------------------------------------------------------------------------ the plough


def light_except(kit, coll, light_name, objs):
    """Light linking: this light lights everything but these objects."""
    col = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = "EXCLUDE"
    kit.LIGHTS[light_name]["obj"].light_linking.receiver_collection = col


def light_only(kit, coll, light_name, objs):
    """Light linking: this light lights only these objects."""
    col = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = "INCLUDE"
    kit.LIGHTS[light_name]["obj"].light_linking.receiver_collection = col


def build_plough(kit, ctx):
    """A tall boxy yellow plough, cab-over: the driver sits high with a short nose and a wide angled blade ahead,
    so the road is visible close in front. Floor z = 1.4, bench top 2.25, roof 3.75, windscreen at y = 2.1."""
    PL = kit.empty("plough")
    ctx["PL"] = PL
    yellow = kit.plastic("#e8b923", 0.5, name="plough yellow")
    ydark = kit.plastic("#b88c14", 0.6, name="plough yellow dark")
    grey = kit.plastic("#2a2f38", 0.6, name="chassis")
    rubber = kit.plastic("#15171b", 0.8, name="rubber")
    hub = kit.plastic("#8f969f", 0.4, name="hub")
    black = kit.plastic("#0e0f12", 0.7, name="dash black")
    seatm = kit.plastic("#3a3f48", 0.9, name="seat")
    liner = kit.plastic("#26282c", 0.9, name="liner")
    kit.box("chassis", (2.6, 5.4, 0.7), (0, 0.1, 1.05), grey, PL, bevel=0.05)
    for sx in (-1, 1):
        for y in (2.0, -1.8):
            kit.cyl(f"wheel{sx}{y}", 0.68, 0.5, (sx * 1.38, y, 0.68), rubber, PL, rot=(0, math.radians(90), 0), n=16)
            kit.cyl(f"hub{sx}{y}", 0.3, 0.52, (sx * 1.38, y, 0.68), hub, PL, rot=(0, math.radians(90), 0), n=10)
    kit.box("nose", (2.3, 0.9, 0.7), (0, 2.55, 1.65), yellow, PL, bevel=0.06)
    kit.box("cab floor", (2.5, 3.4, 0.1), (0, 0.5, 1.38), grey, PL)
    kit.box("cab back", (2.5, 0.12, 2.3), (0, -1.2, 2.55), yellow, PL, bevel=0.03)
    kit.box("cab roof", (2.6, 3.6, 0.14), (0, 0.5, 3.75), yellow, PL, bevel=0.05)
    kit.box("cab liner", (2.3, 3.2, 0.04), (0, 0.5, 3.67), liner, PL)
    for sx in (-1, 1):   # side walls with a window gap (z 2.55 to 3.3) each
        x = sx * 1.22
        kit.box(f"door low{sx}", (0.1, 3.4, 1.1), (x, 0.5, 2.0), yellow, PL, bevel=0.02)
        kit.box(f"door hi{sx}", (0.1, 3.4, 0.45), (x, 0.5, 3.52), yellow, PL, bevel=0.02)
        kit.box(f"door pillar f{sx}", (0.1, 0.22, 0.8), (x, 2.1, 2.93), yellow, PL, bevel=0.02)
        kit.box(f"door pillar b{sx}", (0.1, 0.22, 0.8), (x, -1.1, 2.93), yellow, PL, bevel=0.02)
        kit.box(f"door pillar m{sx}", (0.1, 0.14, 0.8), (x, -0.5, 2.93), yellow, PL, bevel=0.02)
    kit.box("screen low", (2.4, 0.14, 0.4), (0, 2.1, 2.4), black, PL, bevel=0.03)
    for sx in (-1, 1):
        kit.box(f"a pillar{sx}", (0.14, 0.14, 1.2), (sx * 1.14, 2.1, 3.1), yellow, PL, bevel=0.02)
    kit.box("screen top", (2.4, 0.14, 0.3), (0, 2.1, 3.6), yellow, PL, bevel=0.03)
    kit.box("dash", (2.3, 0.7, 0.4), (0, 1.65, 2.15), black, PL, bevel=0.05)
    gm, _ = plain_emit(kit, "gauge green", "#52e69a", 1.4)
    for k in range(5):
        kit.cyl(f"gauge{k}", 0.1, 0.02, (-0.95 + 0.17 * k, 1.29, 2.3 + (0.0 if k % 2 else 0.02)), gm, PL,
                rot=(math.radians(90), 0, 0), n=12)
    wheel = kit.empty("wheel", (-0.55, 1.05, 2.62), PL, rot=(math.radians(-62), 0, 0))
    for k in range(14):
        a = 2 * math.pi * k / 14
        kit.box(f"wheel.r{k}", (0.1, 0.06, 0.05), (0.2 * math.cos(a), 0, 0.2 * math.sin(a)), black, wheel, rot=(0, -a, 0))
    kit.box("wheel.hub", (0.12, 0.05, 0.12), (0, 0, 0), black, wheel)
    kit.box("bench", (2.0, 0.9, 0.7), (0, 0.4, 1.9), seatm, PL, bevel=0.06)
    kit.box("bench back", (2.0, 0.2, 1.2), (0, -0.1, 2.85), seatm, PL, bevel=0.06)
    wip = []
    for sx in (-0.55, 0.5):
        piv = kit.empty(f"wiper{sx}", (sx, 2.0, 2.55), PL)
        kit.box(f"wiper{sx}.arm", (0.035, 0.03, 0.95), (0, 0, 0.475), black, piv)
        kit.box(f"wiper{sx}.blade", (0.04, 0.03, 0.45), (0, 0, 0.8), black, piv)
        wip.append(piv)
    ctx["wipers"] = wip
    blade = kit.empty("blade", (0.0, 3.7, 0.0), PL, rot=(0, 0, math.radians(12)))
    kit.box("blade.slab", (3.5, 0.28, 1.3), (0, 0, 0.9), yellow, blade, bevel=0.06)
    kit.cyl("blade.curl", 0.12, 3.5, (0, 0.05, 1.58), ydark, blade, rot=(0, math.radians(90), 0), n=10)
    kit.box("blade.edge", (3.5, 0.34, 0.12), (0, 0.02, 0.28), kit.plastic("#7d8590", 0.4, name="steel"), blade, bevel=0.02)
    for sx in (-0.9, 0.9):
        kit.box(f"arm{sx}", (0.18, 1.0, 0.2), (sx, 3.25, 0.95), grey, PL, bevel=0.03)
    tally_m = kit.plastic("#c4501e", 0.55, name="tally orange")
    tally = []
    for dx in (-0.09, 0.09):
        tally.append(kit.box(f"tally{dx}", (0.05, 0.012, 0.42), (0.35 + dx, 0.146, 0.85), tally_m, blade, bevel=0.004))
    ctx["tally"] = tally
    kit.cyl("beacon", 0.14, 0.2, (0.6, -0.3, 3.92), kit.plastic("#555555", 0.6, name="beacon dead"), PL, n=10)
    sm = kit.plastic("#e1e8f3", 0.95, name="plough snow")
    ctx["psnow"] = [kit.box("psnow roof", (2.7, 3.7, 0.3), (0, 0.5, 3.98), sm, PL, bevel=0.12),
                    kit.box("psnow hood", (2.1, 0.8, 0.2), (0, 2.55, 2.08), sm, PL, bevel=0.08),
                    kit.box("psnow blade", (3.3, 0.5, 0.2), (0.4, 3.7, 1.65), sm, PL, bevel=0.08)]
    bagm = kit.plastic("#f1f1ee", 0.9, name="bag paper")
    bag = kit.box("bag", (0.28, 0.14, 0.34), (0.55, 0.35, 2.42), bagm, PL, bevel=0.025)
    kit.box("bag.fold", (0.28, 0.14, 0.05), (0, 0, 0.19), kit.plastic("#d9d9d5", 0.9, name="bag fold"), bag)
    ctx["bag"] = bag
    ctx["van_follow"] = build_van(kit, "vanF", PL, (0.0, -13.5, 0))
    for nm, sx in (("headL", -0.85), ("headR", 0.85)):
        ob = kit.light(nm, "SPOT", (sx, 3.0, 1.75), 26000.0, "#fff1d8", spot=62, blend=0.7, size=0.18, parent=PL)
        kit.aim(ob, (sx * 0.5, 40.0, 0.0))
        ob.visible_camera = False
    near = [o for o in PL.children_recursive if o.type == "MESH" and (
        o.name.split(".")[0] in ("nose", "chassis", "bag", "cab roof", "cab floor", "cab back", "bench", "bench back",
                                 "dash", "screen low", "screen top")
        or o.name.startswith(("blade", "wheel", "hub", "arm", "psnow", "door", "a pillar")))]
    for nm in ("headL", "headR"):
        light_except(kit, "head except", nm, near)
    kit.box("step", (0.5, 0.9, 0.1), (-1.5, 0.3, 1.0), grey, PL, bevel=0.02)
    kit.box("step r", (0.5, 0.9, 0.1), (1.5, 0.3, 1.0), grey, PL, bevel=0.02)
    vd = kit.light("van dome", "POINT", (-0.3, -12.4, 2.3), 7.0, "#dfe8ff", size=0.15, parent=PL)
    vd.visible_camera = False
    dg = kit.light("dash glow", "POINT", (0.0, 1.3, 2.6), 3.5, "#6dffb0", size=0.08, parent=PL)
    dg.visible_camera = False
    fl = kit.light("cab fill", "POINT", (0.0, 0.9, 3.5), 12.0, "#8aa4d0", size=0.2, parent=PL)
    fl.visible_camera = False


# ------------------------------------------------------------------------------------------------ interiors


def build_odile(kit, ctx):
    bx, by = BASE["odile"]
    R = kit.empty("odile room", (bx, by, 0))
    plaster = kit.grime("#a08a6c", dark=0.7, scale=2.0, name="odile wall", rough=0.9)
    floor = kit.planks("#6b4a2e", "#4e3520", scale=1.0, name="odile floor")
    wood = kit.plastic("#5a3e26", 0.7, name="odile wood")
    kit.box("o.floor", (6.4, 5.0, 0.1), (0, 0, -0.05), floor, R)
    kit.box("o.ceil", (6.4, 5.0, 0.1), (0, 0, 2.65), plaster, R)
    kit.box("o.back", (6.4, 0.12, 2.7), (0, 2.5, 1.3), plaster, R)
    kit.box("o.front", (6.4, 0.12, 2.7), (0, -2.5, 1.3), plaster, R)
    kit.box("o.left", (0.12, 5.0, 2.7), (-3.2, 0, 1.3), plaster, R)
    kit.box("o.right", (0.12, 5.0, 2.7), (3.2, 0, 1.3), plaster, R)
    # the window on the back wall: a sky panel behind it
    sm, se = plain_emit(kit, "odile sky", "#17233d", 1.0)
    ctx["odile_sky"] = se
    kit.box("o.sky", (1.6, 0.04, 1.2), (0.6, 2.42, 1.55), sm, R)
    for dx in (-0.82, 0.0, 0.82):
        kit.box(f"o.frame{dx}", (0.07, 0.06, 1.3), (0.6 + dx, 2.4, 1.55), wood, R)
    for dz in (-0.62, 0.0, 0.62):
        kit.box(f"o.bar{dz}", (1.7, 0.06, 0.06), (0.6, 2.4, 1.55 + dz), wood, R)
    # the table, the chair, the lamp stand
    kit.cyl("o.tabletop", 0.7, 0.07, (0.5, 0.2, 0.75), wood, R, n=20)
    kit.cyl("o.tableleg", 0.08, 0.72, (0.5, 0.2, 0.36), wood, R, n=8)
    kit.box("o.seat", (0.56, 0.56, 0.08), (-1.0, 0.1, 0.45), wood, R, bevel=0.02)
    kit.box("o.chairback", (0.56, 0.08, 0.62), (-1.0, 0.38, 0.78), wood, R, bevel=0.02)
    for sx in (-0.24, 0.24):
        for sy in (-0.24, 0.24):
            kit.box(f"o.cl{sx}{sy}", (0.06, 0.06, 0.42), (-1.0 + sx, 0.1 + sy, 0.21), wood, R)
    kit.box("o.side", (0.5, 0.5, 0.55), (-2.0, 0.35, 0.28), wood, R, bevel=0.02)
    lampm, _ = plain_emit(kit, "odile shade", "#f2b36b", 3.0)
    kit.cyl("o.shade", 0.2, 0.3, (-2.0, 0.35, 0.72), lampm, R, n=12, r2=0.14)
    lt = kit.light("odile lamp", "POINT", (bx - 1.9, by + 0.3, 0.9), 160.0, "#ffbd78", size=0.12)
    lt.visible_camera = False
    fl = kit.light("odile fill", "POINT", (bx + 0.2, by - 0.6, 2.2), 55.0, "#f0b070", size=0.3)
    fl.visible_camera = False
    # on the table
    keysm = kit.plastic("#d4d0bf", 0.3, name="keys")
    objs = {"keys": [], "bag": [], "glass": [], "cups": []}
    objs["keys"].append(kit.cyl("o.ring", 0.05, 0.015, (0.28, 0.1, 0.79), keysm, R, n=10))
    objs["keys"].append(kit.box("o.key1", (0.04, 0.12, 0.012), (0.34, 0.2, 0.787), keysm, R))
    objs["keys"].append(kit.box("o.key2", (0.04, 0.1, 0.012), (0.22, 0.2, 0.787), keysm, R, rot=(0, 0, 0.4)))
    bag = kit.box("o.bag", (0.28, 0.14, 0.34), (0.55, 0.0, 0.955), kit.plastic("#f1f1ee", 0.9, name="bag paper"), R, bevel=0.025)
    objs["bag"].append(bag)
    objs["glass"].append(kit.cyl("o.glass", 0.055, 0.14, (0.9, 0.18, 0.86), kit.glass("#d6e6f0"), R, n=14))
    cup = kit.plastic("#e6e1d6", 0.5, name="cup")
    objs["cups"].append(kit.cyl("o.cup1", 0.06, 0.09, (0.3, -0.25, 0.835), cup, R, n=14))
    objs["cups"].append(kit.cyl("o.cup2", 0.06, 0.09, (0.75, -0.2, 0.835), cup, R, n=14))
    ctx["table"] = objs
    ctx["o_base"] = (bx, by)


def build_hut(kit, ctx):
    bx, by = BASE["hut"]
    R = kit.empty("hut room", (bx, by, 0))
    stone = kit.cobbles("#4a4c52", "#7b7873", "#1d1d20", scale=1.5, wet=0.1, name="hut stone in")
    floor = kit.planks("#5a4630", "#42301f", scale=1.0, name="hut floor")
    kit.box("h.floor", (5.0, 4.2, 0.1), (0, 0, -0.05), floor, R)
    kit.box("h.ceil", (5.0, 4.2, 0.1), (0, 0, 2.6), stone, R)
    kit.box("h.back", (5.0, 0.12, 2.7), (0, 2.1, 1.3), stone, R)
    kit.box("h.front", (5.0, 0.12, 2.7), (0, -2.1, 1.3), stone, R)
    kit.box("h.left", (0.12, 4.2, 2.7), (-2.5, 0, 1.3), stone, R)
    kit.box("h.right", (0.12, 4.2, 2.7), (2.5, 0, 1.3), stone, R)
    iron = kit.plastic("#1b1c1f", 0.5, name="stove iron")
    kit.box("h.stove", (0.8, 0.7, 1.0), (1.3, 1.5, 0.5), iron, R, bevel=0.04)
    kit.cyl("h.pipe", 0.08, 1.6, (1.3, 1.6, 1.8), iron, R, n=8)
    gm, _ = plain_emit(kit, "stove glow", "#f2a24a", 3.0)
    kit.box("h.stoveglow", (0.3, 0.02, 0.2), (1.3, 1.14, 0.45), gm, R)
    wood = kit.plastic("#5a3e26", 0.7, name="hut wood")
    kit.box("h.bench", (1.6, 0.4, 0.45), (-0.9, 1.6, 0.22), wood, R, bevel=0.02)
    cup = kit.plastic("#d8d4c8", 0.5, name="hut cup")
    kit.cyl("h.cup", 0.05, 0.1, (0.55, 1.5, 0.95), cup, R, n=12)
    kit.cyl("h.flask", 0.07, 0.3, (-1.3, 1.55, 0.6), kit.plastic("#3d5a4a", 0.5, name="flask"), R, n=12)
    lt = kit.light("stove light", "POINT", (bx + 0.9, by + 1.0, 0.7), 130.0, "#ffa860", size=0.15)
    lt.visible_camera = False
    fl = kit.light("hut fill", "POINT", (bx, by, 2.1), 45.0, "#e8b080", size=0.3)
    fl.visible_camera = False


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    ctx = {"story": story, "part_base": {}}
    build_world(kit, ctx)
    build_plough(kit, ctx)
    build_odile(kit, ctx)
    build_hut(kit, ctx)
    # the moon / sun and the marker's rim light
    sun = kit.light("sun", "SUN", (0, 0, 60), 1.0, "#7f9ad8", rot=(math.radians(58), 0, math.radians(215)))
    ctx["sun"] = sun
    mrim = kit.light("mrim", "AREA", (0, 0, 2), 90.0, "#7fa4ff", size=1.8, parent=ctx["W"])
    mrim.visible_camera = False
    ctx["mrim"] = mrim
    # the Marker is lit by its own soft key, not by the headlights (those would flatten it)
    mobjs = [o for o in ctx["marker"]["root"].children_recursive if o.type == "MESH"]
    col = bpy.data.collections["head except"]
    for o in mobjs:
        if o.name not in col.objects:
            col.objects.link(o)
    for co in col.collection_objects:
        co.light_linking.link_state = "EXCLUDE"
    mk = kit.light("mkey", "SPOT", (0, 0, 3), 260.0, "#ffe2b8", spot=48, blend=0.6, size=0.3, parent=ctx["W"])
    mk.visible_camera = False
    light_only(kit, "mk only", "mkey", mobjs)
    ctx["mkey"] = mk
    # falling snow
    fm = kit._new("flake")
    nt = fm.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col("#dbe6f6")
    e.inputs["Strength"].default_value = 1.6
    kit._fogged(fm, e.outputs[0])
    ctx["flakes"] = []
    for k in range(260):
        f = kit.box(f"flake{k}", (0.025, 0.025, 0.025), (0, 0, -50), fm)
        ctx["flakes"].append(f)
    # the fog nodes (so the fog colour can follow the light of the day)
    fogc = tuple(kit.FOG["color"])
    nodes = []
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        for n in m.node_tree.nodes:
            if n.type == "EMISSION" and tuple(round(v, 4) for v in n.inputs["Color"].default_value[:3]) == tuple(round(v, 4) for v in fogc):
                if any(l.from_node == n and l.to_node.type == "MIX_SHADER" for l in m.node_tree.links):
                    nodes.append(n)
    ctx["fog_nodes"] = nodes
    ctx["hand_ready"] = False
    return ctx


# ------------------------------------------------------------------------------------------------ animate


def _shot_at(story, tl, t):
    sh = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    return sh, next(s for s in story["shots"] if s["id"] == sh["id"])


def _tod_col(table, v):
    v = max(0.0, min(2.0, v))
    a = int(min(1, math.floor(v)))
    u = v - a
    ca, cb = kit_col(table[a]), kit_col(table[a + 1])
    return lerp3(ca, cb, u)


_KC = {}


def kit_col(h):
    if h not in _KC:
        from blocky import kit as k
        _KC[h] = k.col(h)[:3]
    return _KC[h]


def animate_people(kit, story, tl, t, ctx):
    for who, keys in tl.get("acting", {}).items():
        root = bpy.data.objects.get(who)
        if root is None or root.hide_render:
            continue
        hp, sit = [], False
        for k in keys:
            if k["t"] > t + 1e-9:
                break
            if "hide_parts" in k:
                hp = k["hide_parts"]
            if "sit" in k:
                sit = k["sit"]
        for part in hp:
            ob = bpy.data.objects.get(f"{who}.{part}")
            if ob is not None:
                for o in [ob] + list(ob.children_recursive):
                    o.hide_render = True
        if sit:
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (math.radians(-90), 0, 0)
    # Bram's bobble and the bag in his hand (parented once the cast exists)
    if not ctx["hand_ready"] and bpy.data.objects.get("bram.arm1") is not None:
        top = faces.HEAD_H / 2
        hg = bpy.data.objects.get("bram.headg")
        bob = kit.sphere("bram.bobble", 0.2, (0, 0, top + 0.5), kit.plastic("#c9b9a0", 0.9, name="bobble"), hg, seg=8)
        bg = kit.box("bram.bag", (0.8, 0.45, 1.0), (0, -0.55, -2.15), kit.plastic("#f1f1ee", 0.9, name="bag paper"),
                     bpy.data.objects["bram.arm1"], bevel=0.06)
        ctx["bram_bag"] = bg
        ctx["hand_ready"] = True


def animate(kit, story, tl, t, ctx):
    over = {}
    dbg = os.environ.get("EP21_CAM")   # look-dev only: "x,y,z,tx,ty,tz,lens" replaces every shot's camera
    if dbg:
        v = [float(x) for x in dbg.split(",")]
        for sp in story["shots"]:
            sp["cam"] = [[0, v[0:3], v[3:6], v[6]]]
    sh, sspec = _shot_at(story, tl, t)
    # ---- the drive: the world turned and slid round the plough
    dr = sorted(cues(tl, "drive"), key=lambda c: c["t"])
    s = piece(dr, "s", t, 0.0)
    th = math.radians(piece(dr, "theta", t, 0.0))
    px = piece(dr, "x", t, PX)
    W = ctx["W"]
    W.rotation_euler = (0, 0, th)
    c, sn = math.cos(th), math.sin(th)
    W.location = (-(c * px - sn * s), -(sn * px + c * s), 0)
    # ---- the light of the day
    tod_keys = sorted(cues(tl, "tod"), key=lambda c: c["t"])
    tod = piece(tod_keys, "v", t, 0.0)
    fogc = _tod_col(FOGC, tod)
    for n in ctx["fog_nodes"]:
        n.inputs["Color"].default_value = (*fogc, 1.0)
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*fogc, 1.0)
    over["sun"] = lerp(SUNE[0], SUNE[1], ss(tod)) if tod <= 1 else lerp(SUNE[1], SUNE[2], ss(tod - 1))
    ctx["sun"].data.color = _tod_col(SUNC, tod)
    ctx["sun"].data.energy = ctx["sun"].data.energy  # base is 1.0; gain below
    bpy.context.scene.view_settings.exposure = lerp(EXPO[0], EXPO[1], ss(tod)) if tod <= 1 else lerp(EXPO[1], EXPO[2], ss(tod - 1))
    ctx["odile_sky"].inputs["Color"].default_value = (*fogc, 1.0)
    ctx["odile_sky"].inputs["Strength"].default_value = 0.9 + 1.4 * min(tod, 2.0)
    sd = ctx["sundisc"]
    sd.hide_render = tod < 1.5
    ctx["sundisc_node"].inputs["Strength"].default_value = 3.0 * ss((tod - 1.5) / 0.5)
    # ---- the headlights: eased, never to black
    hg = max(0.2, eased(cues(tl, "lights"), "g", t, 1.0))
    over["headL"] = over["headR"] = hg
    over["dash glow"] = 1.0
    over["van dome"] = 1.0 if (last(cues(tl, "van"), t) or {}).get("mode") == "follow" else 0.0
    day = 1.0 - 0.6 * min(1.0, tod)    # reflectors fade a little in daylight
    # ---- the posts: a glint fades up as the headlights reach it and down as they leave
    sl = last(cues(tl, "slide"), t)
    slid = bool(sl and sl.get("on"))
    seas = last(cues(tl, "season"), t)
    spring = bool(seas and seas.get("v") == "spring")
    for o in ctx["snow_objs"]:
        o.hide_render = spring
    for o in ctx["spring_objs"]:
        o.hide_render = not spring
    for o in ctx["pre"]:
        o.hide_render = slid or spring
    for o in ctx["pre_sp"]:
        o.hide_render = slid or not spring
    for o in ctx["post"]:
        o.hide_render = not slid
    for i, d in ctx["posts"].items():
        root = d["root"]
        wx, wy = POST_X, SP * i
        z = 0.0
        if i == 23 and slid:
            wx, wy, z = ctx["slab_post_pos"]
            root.rotation_euler = (math.radians(4), math.radians(9), 0)
        else:
            root.rotation_euler = (0, 0, 0)
        root.location = (wx, wy, z)
        hide_tree(root, i == 24 and slid)
        dx, dy = wx - px, wy - s
        ypl = sn * dx + c * dy
        xpl = c * dx - sn * dy
        g = ss((ypl + 2.0) / 7.0) * (1.0 - ss((ypl - 34.0) / 22.0)) if abs(xpl) < 12 else 0.0
        d["node"].inputs["Strength"].default_value = 4.0 * g * hg * day if ypl < 70 else 0.0
    # the plant: post 23's glint, down on the slab, seen from far up the road, sitting lower than the line
    dxp, dyp = 2.9 - px, 690.0 - s
    yp = sn * dxp + c * dyp
    gp = ss((yp - 50.0) / 50.0) * (1.0 - ss((yp - 230.0) / 30.0)) if slid else 0.0
    ctx["plant"].hide_render = gp <= 0.0
    ctx["plant_node"].inputs["Strength"].default_value = 3.5 * gp * hg * day
    ctx["farlight"].hide_render = not (s < 100.0 and abs(th) < 0.1)
    nw = last(cues(tl, "newpost"), t)
    on = bool(nw and nw.get("on"))
    hide_tree(ctx["newpost"]["root"], not on)
    nv = eased(cues(tl, "newpost"), "glow", t, 0.0) if on else 0.0
    ctx["newpost"]["node"].inputs["Strength"].default_value = 5.0 * nv
    # ---- the Marker
    mk = last(cues(tl, "marker"), t)
    M = ctx["marker"]
    vis = bool(mk and mk.get("vis", True))
    M["root"].hide_render = not vis
    for ob in M["root"].children_recursive:
        ob.hide_render = not vis
    if mk and vis:
        x, y = mk["x"], mk["y"]
        M["root"].location = (x, y, 0)
        M["drift"].hide_render = not mk.get("drift", False)
        for sob in M["snow"]:
            sob.hide_render = not mk.get("snow", True)
        dx, dy = x - px, y - s
        ypl = sn * dx + c * dy
        g = ss((ypl + 1.0) / 4.0) * (1.0 - ss((ypl - 30.0) / 18.0))
        cl = V(sspec["cam"][0][1])
        mpl = V((sn * 0 + c * (x - px) - sn * (y - s), sn * (x - px) + c * (y - s), 0.8))
        near = min(1.0, max(0.3, (cl - mpl).length / 9.0))   # eyes close to the camera would clip to white
        for e in M["eyes"]:
            e.inputs["Strength"].default_value = 3.2 * g * hg * day * near
        rim = ctx["mrim"]
        rim.location = (x, y - 3.0, 1.9)
        rim.rotation_euler = (V((x, y, 0.8)) - V((x, y - 3.0, 1.9))).to_track_quat("-Z", "Y").to_euler()
        over["mrim"] = 1.0
        ctx["mkey"].location = (x + 0.8, y + 3.2, 2.6)
        ctx["mkey"].rotation_euler = (V((x, y, 0.7)) - V((x + 0.8, y + 3.2, 2.6))).to_track_quat("-Z", "Y").to_euler()
        over["mkey"] = hg * float(mk.get("kg", 1.0))
    else:
        over["mrim"] = 0.0
        over["mkey"] = 0.0
    sq = last(cues(tl, "square"), t)
    ctx["square"].hide_render = not (sq and sq.get("on"))
    # ---- the plough, the vans, the bag, the tally, the snow hood
    pl = last(cues(tl, "plough"), t)
    pon = not (pl and pl.get("on") is False)
    for o in [ctx["PL"]] + list(ctx["PL"].children_recursive):
        o.hide_render = not pon
    mode = (last(cues(tl, "van"), t) or {}).get("mode", "none")
    for o in [ctx["van_parked"]] + list(ctx["van_parked"].children_recursive):
        o.hide_render = mode != "parked"
    for o in [ctx["van_follow"]] + list(ctx["van_follow"].children_recursive):
        o.hide_render = not (pon and mode == "follow")
    bw = (last(cues(tl, "bag"), t) or {}).get("where", "none")
    ctx["bag"].hide_render = not (pon and bw == "seat")
    for o in ctx["bag"].children:
        o.hide_render = ctx["bag"].hide_render
    if ctx.get("bram_bag") is not None:
        ctx["bram_bag"].hide_render = bw != "hand"
    ty = last(cues(tl, "tally"), t)
    for o in ctx["tally"]:
        o.hide_render = not (ty and ty.get("on"))
    ps = last(cues(tl, "psnow"), t)
    for o in ctx["psnow"]:
        o.hide_render = not (pon and ps and ps.get("on"))
    tb = last(cues(tl, "table"), t) or {}
    for k, objs in ctx["table"].items():
        for o in objs:
            o.hide_render = not tb.get(k, False)
    # ---- the wipers
    wp = last(cues(tl, "wipers"), t)
    won = not (wp and wp.get("on") is False)
    ang = (0.5 - 0.5 * math.cos(2 * math.pi * t / 1.82)) if won else 0.0
    for k, piv in enumerate(ctx["wipers"]):
        piv.rotation_euler = (0, math.radians(-8 + 68 * ang * (1 if k == 0 else 1)), 0)
    # ---- falling snow around the camera
    snow_amt = float(sspec.get("snow", 1.0)) * (1.0 - ss((tod - 0.2) / 1.2))
    if sspec["cam"][0][1][0] > 100:
        snow_amt = 0.0
    k0 = sspec["cam"][0]
    loc, tgt = V(k0[1]), V(k0[2])
    fwd = (tgt - loc)
    fwd = fwd.normalized() if fwd.length > 1e-6 else V((0, 1, 0))
    cen = loc + fwd * 7.0
    trav = travelled(dr, t)
    n_on = int(len(ctx["flakes"]) * snow_amt)
    for k, f in enumerate(ctx["flakes"]):
        if k >= n_on:
            f.hide_render = True
            continue
        f.hide_render = False
        rx, ry, rz = kit.hash01(k, 1), kit.hash01(k, 2), kit.hash01(k, 3)
        x = cen.x + (rx - 0.5) * 16 + 0.25 * math.sin(t * 1.3 + k)
        y = cen.y + ((ry * 18 - trav * 0.8) % 18) - 9
        z = cen.z + 5 - ((rz * 12 + 1.7 * t) % 12)
        f.location = (x, y, z)
    return over
