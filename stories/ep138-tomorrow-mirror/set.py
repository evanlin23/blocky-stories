"""ep138 "the gym where you see tomorrow": one small bright gym (teal walls, orange rubber floor, black racks and benches,
steady white ceiling panels, a wall-to-wall mirror on the east wall with thick chrome mullions, a white flip-number date
board on the west wall). No light ever changes: nothing blinks, glows or flickers.

"The glass" is a camera at the mirror looking west out into the same gym. Its marker is the chrome edge: a chrome
pillar standing in the room about a metre in front of that camera, at the right of the frame, plus a faint cool-tinted
pane in front of it, both placed by the `glass` cue (position and yaw, on the cut) and hidden in every real shot.
The date board is one object set: cue `board` gives the number (v) and whether it is hung backward (flip). Held
things (the bar, the key) follow a character's hands; the paint and the moustache follow heads. Every extra is made
in build(); animate only moves, shows and hides them.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

W = {}
SIT = -math.pi / 2 * 0.97
SEATED = ("dre",)
SEG = {1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc"}
MIRROR_SEG = {"a": "a", "g": "g", "d": "d", "b": "f", "f": "b", "c": "e", "e": "c"}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def sample(name, tl, t, defaults):
    """The state of cue track `name` at t: numeric fields eased over a cue's own "dur"."""
    cur, prev = dict(defaults), dict(defaults)
    for c in tl["cues"]:
        if c["name"] != name:
            continue
        if c["t"] > t:
            break
        prev = dict(cur)
        cur.update({k: v for k, v in c.items() if k in defaults})
        dur = c.get("dur", 0.0)
        if dur > 0 and t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            return {k: (prev[k] + (cur[k] - prev[k]) * u if isinstance(cur[k], (int, float)) else cur[k]) for k in cur}
    return cur


# ---------------------------------------------------------------------------------------------- the room
def build_room(kit):
    pl = kit.plastic
    teal = pl("#2fb5a8", 0.8, spec=0.05)
    floor = pl("#f08a3a", 0.7, spec=0.08)
    ceil = pl("#f2f2ee", 0.9, spec=0.02)
    kit.box("floor", (10.6, 11.6, 0.1), (0, (G.Y0 + G.Y1) / 2, -0.05), floor)
    # rubber tile seams, darker orange, 1 cm proud
    seam = pl("#d06c26", 0.8, spec=0.02)
    for k in range(-4, 5):
        kit.box(f"seam.x{k}", (0.03, 11.0, 0.01), (k * 1.25, (G.Y0 + G.Y1) / 2, 0.005), seam)
    kit.box("wall.w", (0.4, 11.6, 3.4), (-5.2, (G.Y0 + G.Y1) / 2, 1.6), teal)
    kit.box("wall.e", (0.4, 11.6, 3.4), (5.2, (G.Y0 + G.Y1) / 2, 1.6), teal)
    kit.box("wall.n", (10.8, 0.4, 3.4), (0, 4.7, 1.6), teal)
    kit.box("ceiling", (10.6, 11.6, 0.2), (0, (G.Y0 + G.Y1) / 2, 3.3), ceil)
    W["ceil"] = bpy.data.objects["ceiling"]
    # the south wall has a high window; the afternoon sun comes through it
    sy = G.Y0 - 0.2
    kit.box("wall.s.low", (10.8, 0.4, 2.0), (0, sy, 0.9), teal)
    kit.box("wall.s.hi", (10.8, 0.4, 0.5), (0, sy, 2.95), teal)
    kit.box("wall.s.l", (4.4, 0.4, 0.8), (-3.2, sy, 2.3), teal)
    kit.box("wall.s.r", (5.0, 0.4, 0.8), (2.9, sy, 2.3), teal)
    win = pl("#bfe6ff", 0.2, spec=0.3)
    kit.box("window.glass", (1.2, 0.05, 0.8), (-0.5, G.Y0 - 0.02, 2.3), win)
    # white ceiling panels, steady
    em = kit.emit("#ffffff", 3.0)
    for i, x in enumerate((-3.2, 0.0, 3.2)):
        for j, y in enumerate((-5.0, -2.0, 1.0)):
            kit.box(f"panel{i}{j}", (1.6, 0.8, 0.02), (x, y, 3.19), em)
    # a high strip of paler teal on each side wall so the room isn't flat
    stripe = pl("#1f968b", 0.8, spec=0.05)
    kit.box("stripe.w", (0.03, 11.0, 0.5), (-4.985, (G.Y0 + G.Y1) / 2, 0.55), stripe)
    kit.box("stripe.n", (10.0, 0.03, 0.5), (0, 4.485, 0.55), stripe)


def build_mirror(kit):
    pl = kit.plastic
    chrome = pl("#8f9ba9", 0.35, spec=0.25)
    glass = pl("#6a9fbc", 0.3, spec=0.25)
    y0, y1 = G.MIR_Y0, G.MIR_Y1
    cy, ln = (y0 + y1) / 2, y1 - y0
    kit.box("mirror.plate", (0.03, ln, 2.5), (4.985, cy, 1.55), glass)
    # faint sheen bands, 1.2 cm proud of the plate
    sheen = pl("#a6cfe3", 0.3, spec=0.2)
    for k, yy in enumerate((-0.4, -2.0, -3.6)):
        kit.box(f"mirror.sheen{k}", (0.02, 0.18, 2.3), (4.96, yy, 1.55), sheen)
    # top and bottom rails, thick
    kit.box("mirror.rail.t", (0.16, ln + 0.3, 0.2), (4.9, cy, 2.9), chrome, bevel=0.03)
    kit.box("mirror.rail.b", (0.16, ln + 0.3, 0.2), (4.9, cy, 0.2), chrome, bevel=0.03)
    for k, yy in enumerate(G.MULL):
        wdt = 0.34 if k in (0, 3) else 0.2     # pillars at the ends are thicker
        kit.box(f"mirror.mull{k}", (0.3 if k in (0, 3) else 0.2, wdt, 3.2), (4.85 if k in (0, 3) else 4.9, yy, 1.6),
                chrome, bevel=0.03)
    # the lore tally: two teal strokes scratched in the north pillar's west face at its foot, 1.5 cm proud
    tealk = pl("#3ff0e0", 0.5, spec=0.1)
    px = 4.85 - 0.15 - 0.015
    for k, dy in enumerate((-0.05, 0.06)):
        kit.box(f"tally{k}", (0.03, 0.025, 0.2), (px, G.MULL[0] + dy, 0.38), tealk)


def build_gear(kit):
    pl = kit.plastic
    black = pl("#2a2a30", 0.5, spec=0.3)
    steel = pl("#8a9098", 0.4, spec=0.5)
    pad = pl("#1c1c20", 0.7, spec=0.1)
    # Dre's bench: a black pad on two steel feet, long side north-south
    bx, by = G.BENCH
    kit.box("bench.pad", (0.6, 2.3, 0.12), (bx, by, 0.4), pad, bevel=0.03)
    for sy in (-0.95, 0.95):
        kit.box(f"bench.leg{sy}", (0.5, 0.08, 0.35), (bx, by + sy, 0.175), steel)
    # a second bench near the north wall
    kit.box("bench2.pad", (0.46, 1.7, 0.1), (0.5, 3.3, 0.4), pad, bevel=0.03)
    for sy in (-0.65, 0.65):
        kit.box(f"bench2.leg{sy}", (0.4, 0.08, 0.35), (0.5, 3.3 + sy, 0.175), steel)
    # squat racks on the north wall, with bars and plates
    for rx in (-3.0, -0.6, 2.2):
        for sx in (-0.7, 0.7):
            kit.box(f"rack.{rx}.up{sx}", (0.12, 0.12, 2.4), (rx + sx, 4.1, 1.2), black, bevel=0.02)
            kit.box(f"rack.{rx}.foot{sx}", (0.12, 0.7, 0.08), (rx + sx, 3.85, 0.04), black)
        kit.box(f"rack.{rx}.top", (1.6, 0.12, 0.1), (rx, 4.1, 2.4), black)
        kit.cyl(f"rack.{rx}.bar", 0.025, 1.9, (rx, 3.95, 1.5), steel, rot=(0, math.pi / 2, 0), n=10)
        for sx in (-0.85, 0.85):
            kit.cyl(f"rack.{rx}.plate{sx}", 0.22, 0.06, (rx + sx, 3.95, 1.5), black, rot=(0, math.pi / 2, 0), n=16)
    # a plate tree and a few plates on the floor against the west wall
    for k in range(3):
        kit.cyl(f"plate.floor{k}", 0.22, 0.05, (-4.4, -4.6 + 0.0, 0.03 + k * 0.05), black, n=16)
    # a window of sun on the floor is the only extra (the light does it)


def build_board(kit):
    pl = kit.plastic
    cx, cy, cz = G.BOARD
    white = pl("#e9e9e4", 0.7, spec=0.03)
    frame = pl("#3a3a42", 0.6)
    ink = pl("#151518", 0.7, spec=0.02)
    kit.box("board.panel", (0.06, 2.1, 2.6), (cx, cy, cz), white)
    kit.box("board.f.t", (0.1, 2.3, 0.1), (cx + 0.02, cy, cz + 1.35), frame)
    kit.box("board.f.b", (0.1, 2.3, 0.1), (cx + 0.02, cy, cz - 1.35), frame)
    for s in (-1, 1):
        kit.box(f"board.f.s{s}", (0.1, 0.1, 2.8), (cx + 0.02, cy + s * 1.1, cz), frame)
    dh, dw, t = 1.8, 0.78, 0.22
    x = cx + 0.025    # the panel's front is at cx + 0.03: digits stand 1 cm proud of it, their backs inside it
    W["bd"] = {}
    for slot, off in (("L", -0.5), ("R", 0.5)):
        pos = {"a": (0, dh / 2 - t / 2, dw, t), "g": (0, 0, dw, t), "d": (0, -dh / 2 + t / 2, dw, t),
               "f": (-dw / 2 + t / 2, dh / 4, t, dh / 2), "b": (dw / 2 - t / 2, dh / 4, t, dh / 2),
               "e": (-dw / 2 + t / 2, -dh / 4, t, dh / 2), "c": (dw / 2 - t / 2, -dh / 4, t, dh / 2)}
        for k, (u, v, sw, sh) in pos.items():
            ob = kit.box(f"bd.{slot}{k}", (0.03, sw, sh), (x, cy + off + u, cz + v), ink)
            ob.hide_render = True
            W["bd"][(slot, k)] = ob


def build_glass(kit):
    """The glass's marker: a chrome pillar and a faint cool pane, both placed on the camera by the `glass` cue (also the real mirror's edge bar and cool strip)."""
    pl = kit.plastic
    W["post"] = kit.box("glass.post", (0.12, 0.5, 4.0), (0, 0, -20), pl("#4a535e", 0.35, spec=0.25), bevel=0.02)
    W["ebar"] = kit.box("edge.bar", (0.12, 0.5, 4.0), (0, 0, -20), pl("#4a535e", 0.35, spec=0.25), bevel=0.02)

    def tint(name, fac):
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        nt = m.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        df = nt.nodes.new("ShaderNodeBsdfDiffuse")
        df.inputs["Color"].default_value = kit.col("#8fcfee")
        mx = nt.nodes.new("ShaderNodeMixShader")
        mx.inputs["Fac"].default_value = fac
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(df.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs[0])
        return m

    W["estrip"] = kit.box("edge.strip", (0.01, 0.5, 4.0), (0, 0, -20), tint("edge.tint", 0.5))
    W["estrip"].visible_shadow = False
    W["pane"] = kit.box("glass.pane", (0.01, 8.0, 8.0), (0, 0, -20), tint("glass.tint", 0.2))
    W["pane"].visible_shadow = False


def build_props(kit):
    pl = kit.plastic
    steel = pl("#9aa0a8", 0.35, spec=0.6)
    blk = pl("#2a2a30", 0.5, spec=0.3)
    root = kit.empty("bar", (0, 0, -20))
    kit.cyl("bar.rod", 0.022, 1.9, (0, 0, 0), steel, root, rot=(0, math.pi / 2, 0), n=10)
    for s in (-0.8, 0.8):
        kit.cyl(f"bar.plate{s}", 0.2, 0.07, (s, 0, 0), blk, root, rot=(0, math.pi / 2, 0), n=16)
    W["bar"] = root
    gold = pl("#f2c230", 0.3, spec=0.7)
    key = kit.empty("key", (0, 0, -20))
    # a big flat gold key facing +x: ring on top, shaft down, two teeth
    kit.cyl("key.ring", 0.11, 0.05, (0, 0, 0.3), gold, key, rot=(0, math.pi / 2, 0), n=16)
    kit.cyl("key.hole", 0.05, 0.06, (0, 0, 0.3), pl("#2a2a30", 0.7), key, rot=(0, math.pi / 2, 0), n=12)
    kit.box("key.shaft", (0.05, 0.07, 0.42), (0, 0, 0.0), gold, key, bevel=0.01)
    kit.box("key.tooth1", (0.05, 0.12, 0.07), (0, 0.07, -0.12), gold, key)
    kit.box("key.tooth2", (0.05, 0.1, 0.07), (0, 0.06, -0.01), gold, key)
    W["key"] = key
    # paint on Lena's cheek (orange and teal), moustache on Wendell: attached to heads in animate
    W["paint"] = [kit.box("paint.o", (0.2, 0.08, 0.14), (0, 0, 0), pl("#ff8a1e", 0.6), bevel=0.02),
                  kit.box("paint.t", (0.16, 0.08, 0.1), (0, 0, 0), pl("#1fb8a8", 0.6), bevel=0.02)]
    sm = pl("#9a9aa2", 0.8)
    W["stache"] = [kit.box(f"wendell.stache{sx}", (0.3, 0.08, 0.1), (0, 0, 0), sm, bevel=0.03) for sx in (-1, 1)]


# ---------------------------------------------------------------------------------------------- build / animate
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    sun = kit.light("sun", "SUN", (-6, -20, 22), 1.0, "#ffe08a", size=0.06)
    sun.data.angle = 0.05
    kit.aim(sun, (1.5, 0, 0))
    build_room(kit)
    build_mirror(kit)
    build_gear(kit)
    build_board(kit)
    build_glass(kit)
    build_props(kit)
    # constant soft fills from the ceiling, and a face fill from each end of the room
    for i, (x, y) in enumerate(((-2.5, -4.0), (2.5, -4.0), (-2.5, 0.0), (2.5, 0.0), (0.0, 2.5))):
        a = kit.light(f"ceil{i}", "AREA", (x, y, 3.0), 230, "#fff6ec", size=3.0, shadow=False)
        kit.aim(a, (x, y, 0.0))
    fw = kit.light("faceW", "AREA", (-4.6, -3.0, 2.0), 330, "#fff6ec", size=3.0, shadow=False)
    kit.aim(fw, (2.5, -0.5, 1.4))
    fe = kit.light("faceE", "AREA", (4.4, 1.5, 2.2), 330, "#fff6ec", size=3.0, shadow=False)
    kit.aim(fe, (-1.0, -1.8, 1.4))
    fs = kit.light("faceS", "AREA", (3.0, -5.8, 2.2), 280, "#fff6ec", size=3.0, shadow=False)
    kit.aim(fs, (3.0, 0.0, 1.4))
    return {}


def cam_now(story, tl, t):
    """The camera (location, target, lens) at t, as the engine places it (the pack's move included, hand shake left out)."""
    from blocky import polish
    if "specs" not in W:
        W["specs"] = polish.cam_specs(story, tl, polish.spec(story))
    shot = next((x for x in tl["shots"] if x["start"] <= t < x["end"]), tl["shots"][-1])
    keys = W["specs"][shot["id"]]["cam"]
    u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
    if u <= keys[0][0] or len(keys) == 1:
        k = keys[0]
        return k[1], k[2], k[3]
    for a, b in zip(keys, keys[1:]):
        if u <= b[0]:
            v = ss((u - a[0]) / max(1e-6, b[0] - a[0]))
            lerp = lambda p, q: [p[i] + (q[i] - p[i]) * v for i in range(3)]
            return lerp(a[1], b[1]), lerp(a[2], b[2]), a[3] + (b[3] - a[3]) * v
    k = keys[-1]
    return k[1], k[2], k[3]


def hand(who, sx):
    ob = bpy.data.objects.get(f"{who}.arm{sx}")
    if ob is None:
        return None
    return ob.matrix_world @ Vector((0, 0, -1.55))


def animate(kit, story, tl, t, ctx):
    # heads carry the paint and the moustache (idempotent, on every call)
    for ob in W["paint"]:
        hg = bpy.data.objects.get("lena.headg")
        if hg is not None:
            if ob.parent is not hg:
                ob.parent = hg
            ob.location = (0.3, -0.5, -0.12) if ob.name == "paint.o" else (0.36, -0.45, -0.3)
            ob.rotation_euler = (0, 0.5, 0)
    for sx, ob in zip((-1, 1), W["stache"]):
        hg = bpy.data.objects.get("wendell.headg")
        if hg is not None:
            if ob.parent is not hg:
                ob.parent = hg
            ob.location = (sx * 0.17, -0.64, -0.2)
            ob.rotation_euler = (0, sx * 0.3, 0)
            ob.hide_render = hg.hide_render
    paint = sample("props", tl, t, {"paint": 0.0, "bar": 0.0, "key": 0.0, "bar_who": "me2", "key_who": "kim"})
    lena = bpy.data.objects.get("lena")
    for ob in W["paint"]:
        hg = bpy.data.objects.get("lena.headg")
        ob.hide_render = paint["paint"] < 0.5 or (hg is not None and hg.hide_render) or (lena is not None and lena.hide_render)
    bpy.context.view_layer.update()
    # the bar between both of its owner's hands, the key in the right (+x) hand
    bar_on = paint["bar"] > 0.5
    W["bar"].hide_render = not bar_on
    for c in W["bar"].children:
        c.hide_render = not bar_on
    if bar_on:
        a, b = hand(paint["bar_who"], -1), hand(paint["bar_who"], 1)
        if a is not None and b is not None:
            W["bar"].location = (a + b) / 2
            W["bar"].rotation_euler = (0, 0, math.atan2((b - a).y, (b - a).x))
    key_on = paint["key"] > 0.5
    W["key"].hide_render = not key_on
    for c in W["key"].children:
        c.hide_render = not key_on
    if key_on:
        h = hand(paint["key_who"], -1)
        if h is not None:
            W["key"].location = h + Vector((0.0, 0.0, 0.1))
            W["key"].rotation_euler = (0, 0, 0)
    # the date board: v (two digits, 0 hides it), hung backward when flip
    bd = sample("board", tl, t, {"v": 0.0, "flip": 0.0})
    v, flip = int(round(bd["v"])), bd["flip"] > 0.5
    lit = {("L", k): False for k in "abcdefg"}
    lit.update({("R", k): False for k in "abcdefg"})
    if v:
        tens, ones = v // 10, v % 10
        slots = [("L", tens), ("R", ones)]
        if flip:
            slots = [("L", ones), ("R", tens)]
        for slot, d in slots:
            for k in SEG[d]:
                lit[(slot, MIRROR_SEG[k] if flip else k)] = True
    for key_, ob in W["bd"].items():
        ob.hide_render = not lit[key_]
    # the glass (mode 1: a dark chrome bar and a cool pane over the frame) and the real mirror's edge (mode 2: the bar
    # and a strip of cool glass at the right of the frame): both ride on the camera, so they hold through its moves
    g = sample("glass", tl, t, {"on": 0.0, "fr": 0.45, "dp": 1.0})
    mode = int(round(g["on"]))
    for ob in (W["post"], W["pane"], W["ebar"], W["estrip"]):
        ob.hide_render = True
    if mode:
        loc, tgt, lens = cam_now(story, tl, t)
        fx, fy = tgt[0] - loc[0], tgt[1] - loc[1]
        n = math.hypot(fx, fy)
        fx, fy = fx / n, fy / n
        rx, ry = fy, -fx
        yaw = math.atan2(fy, fx)
        dp = g["dp"]
        hw = 6.75 * dp / lens

        def put(ob, d, lat, width):
            ob.hide_render = False
            ob.scale = (1.0, width / 0.5, 1.0)
            ob.location = (loc[0] + fx * d + rx * lat, loc[1] + fy * d + ry * lat, loc[2])
            ob.rotation_euler = (0, 0, yaw)

        if mode == 1:
            pw = max(0.5, 2.0 * hw)
            put(W["post"], dp, g["fr"] * hw + pw / 2, pw)
            W["pane"].hide_render = False
            W["pane"].location = (loc[0] + fx * 0.45, loc[1] + fy * 0.45, loc[2])
            W["pane"].rotation_euler = (0, 0, yaw)
        else:
            inner = 0.78 * hw
            wd = hw - inner + 0.5
            put(W["ebar"], dp, inner + wd / 2, wd)
            hs = 6.75 * (dp + 0.1) / lens
            put(W["estrip"], dp + 0.1, 0.46 * hs + (0.74 * hs - 0.46 * hs) / 2, 0.74 * hs - 0.46 * hs)
    # seated: legs level while Dre sits
    sit = sample("sit", tl, t, {n: 0.0 for n in SEATED})
    for who in SEATED:
        s = sit[who]
        if s > 0.001:
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (leg.rotation_euler.x * (1 - s) + SIT * s, 0, 0)
    return {"sun": 2.0}
