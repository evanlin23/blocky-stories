"""ep136 "one answer": the Rim, a red-gold canyon overlook. A wooden railing along the edge, a thick post painted with a
huge cream "1" (it moves between shots, on cuts only), the far canyon wall in bands with three painted rocks (one, two,
three cream dots), a dirt lot behind the railing with a teal pickup, and a bluff behind the lot.

Lane staging: ONE slow light change (afternoon gold to dusk violet over 1.5 s, cue "dusk"); nothing blinks or pulses;
the truck's lamps are plain cream paint (never lit); no text anywhere but the numeral 1 and the dots.
Cues read by animate(): sit (per character 0..1, eased), post (x, y: placed on cuts), dusk (0..1, eased over its own dur),
show (car, loaf, pane, rim: 0/1, on cuts).
Every extra (loaf, car, truck, pane, shadow) is built here in build(); animate only moves or shows them.
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
SEATED = ("me",)
MOUTH_Z = -0.46
GOLD_KEY, DUSK_KEY = "#ffd9a0", "#ff7a58"
GOLD_FACE, DUSK_FACE = "#fff0dc", "#ffc4b4"
GOLD_SKY, DUSK_SKY = "#c8dcf0", "#6a3cf0"


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


def mix(a, b, u, kit):
    ca, cb = kit.col(a)[:3], kit.col(b)[:3]
    return tuple(ca[i] + (cb[i] - ca[i]) * u for i in range(3))


# ---------------------------------------------------------------------------------------------- the land
def build_land(kit):
    pl = kit.plastic
    dirt = pl("#dd9558", 0.95, spec=0.03)
    kit.box("mesa.top", (160, 44, 0.6), (0, 21.85, -0.3), dirt)
    kit.box("mesa.body", (159.6, 43.7, 30.4), (0, 22.0, -15.8), pl("#b5452c", 0.9, spec=0.03))
    # the dry canyon floor and the side walls
    kit.box("canyon.floor", (160, 44, 1), (0, -20.0, -30.5), pl("#8f3b27", 0.95, spec=0.03))
    bands = [(-31, 0, "#b5452c"), (0, 12, "#f0b46a"), (12, 17, "#d8703c"), (17, 26, "#c8452f")]
    for sx in (-1, 1):
        for k, (z0, z1, c) in enumerate(bands):
            kit.box(f"side{sx}.{k}", (6, 52, z1 - z0), (sx * 46, -18.0, (z0 + z1) / 2), pl(c, 0.95, spec=0.03))
    # the far wall: banded, each band stepped a little for relief; its face plane is WALL_Y
    far = [(-31, -2, "#b5452c", 0.0), (-2, 12, "#f0b46a", 0.0), (12, 17, "#d8703c", 0.6), (17, 22, "#c8452f", 0.0),
           (22, 26, "#ea8a3c", 0.7)]
    for k, (z0, z1, c, off) in enumerate(far):
        kit.box(f"far.{k}", (160, 8, z1 - z0), (0, G.WALL_Y - 4 + off, (z0 + z1) / 2), pl(c, 0.95, spec=0.03))
    # the bluff behind the lot (its face looks south, at the cameras that look north at the people)
    bl = [(0, 5, "#e6c08a"), (5, 10, "#d8703c"), (10, 15, "#b5452c"), (15, 20, "#e6a65a"), (20, 26, "#c8452f")]
    for k, (z0, z1, c) in enumerate(bl):
        kit.box(f"bluff.{k}", (160, 8, z1 - z0), (0, 26.0 + (0.5 if k % 2 else 0.0), (z0 + z1) / 2), pl(c, 0.95, spec=0.03))
    # a few rocks and bushes to dress the lot (kept clear of the people, the post and the truck)
    kit.prop("rock_5", (-7.0, 6.0, 0), rot=30, height=1.4, tint="#e8a070")
    kit.prop("rock_1", (-4.5, 14.0, 0), rot=100, height=1.1, tint="#e8a070")
    kit.prop("rock_3", (9.0, 12.0, 0), rot=10, height=1.6, tint="#e8a070")
    kit.prop("bush_2", (-9.0, 3.5, 0), rot=0, height=0.9, tint="#c8c070")
    kit.prop("bush_1", (7.5, 2.5, 0), rot=60, height=0.8, tint="#c8c070")


def build_rim(kit):
    pl = kit.plastic
    wood = pl("#7a5332", 0.8, spec=0.05)
    y = G.RAIL_Y
    for k in range(-5, 6):
        x = k * 2.0
        kit.box(f"rail.post{k}", (0.14, 0.14, 1.15), (x, y, 0.575), wood)
    kit.box("rail.top", (22, 0.1, 0.12), (0, y, 1.08), wood)
    kit.box("rail.mid", (22, 0.08, 0.1), (0, y, 0.6), wood)


def build_post(kit):
    """The rule marker: a thick wooden post with a huge cream numeral 1 on its south and north faces, 5 cm proud.
    Dusk rim strips (pale paint, shown from the cue "show") run up its corners. One object, placed by cue."""
    pl = kit.plastic
    root = kit.empty("post", (G.POST_RAIL[0], G.POST_RAIL[1], 0))
    W["post"] = root
    wood = pl("#5e3a1e", 0.85, spec=0.04)
    cream = kit.emit("#e8d29a", 0.8)             # the numeral stays cream in the gold and at dusk alike
    kit.box("post.body", (0.8, 0.8, 2.7), (0, 0, 1.35), wood, root)
    kit.box("post.cap", (0.9, 0.9, 0.1), (0, 0, 2.75), pl("#7a5332", 0.8), root)
    for face in (-1, 1):                       # -1: the south face (seen from the canyon side), +1: the north face
        yy = face * 0.425
        m = -face                              # a viewer on the south side has +x to the right; on the north, -x
        kit.box(f"post.one{face}.stem", (0.22, 0.07, 1.4), (m * 0.03, face * 0.425, 1.58), cream, root)
        kit.box(f"post.one{face}.flag", (0.38, 0.07, 0.17), (m * -0.17, face * 0.44, 2.17), cream, root, rot=(0, m * 0.62, 0))
        kit.box(f"post.one{face}.base", (0.56, 0.07, 0.15), (0, face * 0.44, 0.9), cream, root)
    rim = pl("#ffd9a0", 0.6)
    W["rim"] = [kit.box(f"post.rim{sx}{sy}", (0.06, 0.06, 2.6), (sx * 0.42, sy * 0.42, 1.35), rim, root)
                for sx in (-1, 1) for sy in (-1, 1)]


def build_rocks(kit):
    pl = kit.plastic
    slab = pl("#6e2a22", 0.9, spec=0.03)
    dot = kit.emit("#fff2d0", 0.85)      # cream in the gold and at dusk alike (continuity)
    pos = {1: [(0.0, 0.0)], 2: [(-1.5, 0.0), (1.5, 0.0)], 3: [(-1.5, 1.6), (1.5, 1.6), (0.0, -1.7)]}
    W["rocks"] = {1: [], 2: [], 3: []}
    for n, x in enumerate(G.ROCK_X, start=1):
        W["rocks"][n].append(kit.box(f"rock{n}", (6.6, 1.5, 7.6), (x, G.WALL_Y + 0.75, G.ROCK_Z), slab, bevel=0.08))
        for k, (dx, dz) in enumerate(pos[n]):
            # a flat cream disc, 3 cm proud of the slab face (y = WALL_Y + 1.5)
            W["rocks"][n].append(kit.cyl(f"rock{n}.dot{k}", 1.25, 0.1, (x + dx, G.WALL_Y + 1.5 + 0.02, G.ROCK_Z + dz),
                                         dot, rot=(math.pi / 2, 0, 0), n=28))


# ---------------------------------------------------------------------------------------------- the truck
def build_truck(kit):
    """A teal pickup, nose to the canyon (-y). Open frames instead of glass (no face is hidden), lamps are plain paint.
    The west door has a window pane (shown only for the knock) with a dark shoulder-high shape outside it."""
    pl = kit.plastic
    teal = pl("#2fa8a0", 0.5, spec=0.25)
    dteal = pl("#1f7a76", 0.55, spec=0.2)
    dark = pl("#25252b", 0.7)
    seatc = pl("#3b3a50", 0.7)
    root = kit.empty("truck", (G.XT, G.YT, 0))
    W["truck"] = root

    def b(n, size, loc, m, bev=0.0, rot=(0, 0, 0)):
        return kit.box(f"truck.{n}", size, loc, m, root, bevel=bev, rot=rot)

    b("chassis", (2.0, 5.2, 0.45), (0, 0, 0.6), dteal)
    hood_c = pl("#14544f", 0.65, spec=0.08)       # dashboard teal, not the bright cab paint
    b("hood", (1.95, 1.7, 0.55), (0, -1.85, 0.95), hood_c, 0.03)
    b("grille", (1.9, 0.1, 0.5), (0, -2.74, 0.78), pl("#33363e", 0.5, spec=0.2))
    b("bumper", (2.1, 0.2, 0.2), (0, -2.8, 0.52), pl("#33363e", 0.5, spec=0.2))
    for sx in (-1, 1):
        kit.cyl(f"truck.lamp{sx}", 0.17, 0.08, (sx * 0.7, -2.76, 0.98), pl("#7a7a82", 0.6), root,
                rot=(math.pi / 2, 0, 0), n=16)
    # cab: door panels below the belt line, A and C pillars, roof, the floor and a dash
    b("floor", (1.96, 2.0, 0.08), (0, -0.1, 0.5), pl("#4a4a54", 0.8))
    for sx in (-1, 1):
        b(f"door{sx}", (0.08, 2.0, 0.7), (sx * 0.99, -0.1, 0.85), teal, 0.02)
        b(f"apil{sx}", (0.12, 0.14, 0.9), (sx * 0.95, -1.05, 1.6), teal)
        b(f"cpil{sx}", (0.12, 0.14, 0.9), (sx * 0.95, 0.85, 1.6), teal)
    b("dash", (1.9, 0.5, 0.34), (0, -0.78, 1.12), dark, 0.03)
    b("dash.lip", (1.9, 0.07, 0.05), (0, -1.04, 1.3), pl("#8d8d9c", 0.5, spec=0.2))
    # the steering-wheel rim in front of the driver's seat: a ring of twelve short bars, tilted back a little
    rimc = pl("#15151a", 0.6)
    wx, wy, wz, wr = -0.45, -0.38, 1.1, 0.16
    for k in range(12):
        a = k * math.tau / 12
        b(f"wheel.seg{k}", (0.17, 0.06, 0.06), (wx + wr * math.cos(a), wy, wz + wr * math.sin(a)), rimc, 0.01,
          rot=(0, -a - math.pi / 2, 0))
    b("wheel.hub", (0.12, 0.06, 0.12), (wx, wy, wz), rimc, 0.01)
    b("wheel.column", (0.08, 0.3, 0.08), (wx, wy - 0.18, wz - 0.1), rimc)
    b("cabback", (1.9, 0.12, 0.8), (0, 0.85, 0.95), teal)
    # seats: a cushion and a low back each (the back stays below the shoulders so the post shows past a head)
    for sx in (-0.45, 0.45):
        b(f"seat{sx}", (0.72, 0.62, 0.22), (sx, 0.15, 0.51), seatc, 0.03)
        b(f"seatback{sx}", (0.72, 0.14, 0.62), (sx, 0.52, 0.85), seatc, 0.03)
    # the bed
    b("bed", (2.0, 2.0, 0.12), (0, 1.95, 0.8), dteal)
    for sx in (-1, 1):
        b(f"bedside{sx}", (0.1, 2.0, 0.45), (sx * 0.95, 1.95, 1.05), teal, 0.02)
    b("tailgate", (1.9, 0.1, 0.45), (0, 2.95, 1.05), teal, 0.02)
    for sx in (-1, 1):
        for ly in (-1.7, 1.7):
            kit.cyl(f"truck.wheel{sx}{ly}", 0.44, 0.3, (sx * 1.0, ly, 0.44), dark, root, rot=(0, math.pi / 2, 0), n=18)
            kit.cyl(f"truck.hub{sx}{ly}", 0.2, 0.32, (sx * 1.0, ly, 0.44), pl("#cfd2d6", 0.3, spec=0.8), root,
                    rot=(0, math.pi / 2, 0), n=12)
    # the knock window: a window frame (dark bars), a pale violet pane in it and a soft grey head-and-shoulders
    # shadow on it, all hidden until the cue "show" pane=1 (they are on a cut, never flashed). The shadow is made of
    # rounded ellipsoids in two tones (a wide pale halo under a darker core) so its edge is soft, never stepped; it
    # is drawn on both faces of the pane so the cab camera and the outside camera both see it.
    pg = kit.empty("truck.paneg", (-0.985, -0.1, 0), root)
    W["paneg"] = pg
    PX = -0.985   # the group's own origin; children are placed relative to it

    def pb(n, size, loc, m):
        return kit.box(f"truck.{n}", size, (loc[0] - PX, loc[1] + 0.1, loc[2]), m, pg)

    pane = pb("pane", (0.03, 1.55, 0.95), (-0.99, -0.1, 1.64), kit.emit("#9a8ed0", 0.6))
    fr = pl("#1b2230", 0.7)
    bars = [pane,
            pb("pane.l", (0.07, 0.1, 1.15), (-0.985, -0.1 - 0.825, 1.64), fr),
            pb("pane.r", (0.07, 0.1, 1.15), (-0.985, -0.1 + 0.825, 1.64), fr),
            pb("pane.t", (0.07, 1.75, 0.1), (-0.985, -0.1, 2.165), fr),
            pb("pane.b", (0.07, 1.75, 0.1), (-0.985, -0.1, 1.115), fr)]
    halo = kit.emit("#7a70ad", 0.6)
    core = kit.emit("#5d5590", 0.6)
    for side, xs in (("in", -0.945), ("out", -1.035)):
        sgn = 1 if side == "in" else -1
        for tag, mat, dx, k in (("halo", halo, 0.0, 1.22), ("core", core, 0.012 * sgn, 1.0)):
            hd = kit.sphere(f"truck.shadow.{side}.head.{tag}", 1.0, (xs + dx - PX, 0.0, 1.86), mat, pg, seg=20)
            hd.scale = (0.012, 0.2 * k, 0.24 * k)
            sh = kit.sphere(f"truck.shadow.{side}.sh.{tag}", 1.0, (xs + dx - PX, 0.0, 1.33), mat, pg, seg=20)
            sh.scale = (0.012, 0.58 * k, 0.4 * k)
            bars += [hd, sh]
    W["pane"] = bars


def build_car(kit):
    pl = kit.plastic
    red = pl("#d63a2a", 0.4, spec=0.35)
    dark = pl("#25252b", 0.7)
    glass = pl("#27324a", 0.2, spec=0.6)
    chrome = pl("#cfd2d6", 0.3, spec=0.8)
    root = kit.empty("car", (G.CAR[0], G.CAR[1], -200))
    W["car"] = root

    def b(n, size, loc, m, bev=0.0):
        return kit.box(f"car.{n}", size, loc, m, root, bevel=bev)

    b("body", (2.1, 5.2, 0.75), (0, 0, 0.8), red, 0.05)
    b("cabin", (1.85, 2.5, 0.65), (0, 0.5, 1.5), red, 0.05)
    b("hoodline", (2.05, 1.6, 0.1), (0, -1.9, 1.2), red, 0.03)
    b("windshield", (1.7, 0.08, 0.5), (0, -0.78, 1.5), glass)
    b("rearwin", (1.7, 0.08, 0.5), (0, 1.78, 1.5), glass)
    for sx in (-1, 1):
        b(f"sidewin{sx}", (0.06, 2.0, 0.45), (sx * 0.93, 0.5, 1.52), glass)
        for ly in (-1.7, 1.7):
            kit.cyl(f"car.wheel{sx}{ly}", 0.42, 0.28, (sx * 1.05, ly, 0.42), dark, root, rot=(0, math.pi / 2, 0), n=18)
        kit.cyl(f"car.lamp{sx}", 0.17, 0.08, (sx * 0.7, -2.62, 0.88), pl("#f4ecd0", 0.6), root,
                rot=(math.pi / 2, 0, 0), n=16)
    b("bumper", (2.2, 0.2, 0.2), (0, -2.65, 0.5), chrome)
    b("grille", (1.2, 0.1, 0.3), (0, -2.62, 0.82), chrome)


def build_mouths(kit):
    """An open shouting mouth for each head: a tall dark-red oval with a pale teeth edge on top and a pink tongue
    below, a little proud of the face. Parented to the head on the first animate (the cast exists only after build)
    and shown by the cue "shout" (per character, on cuts)."""
    pl = kit.plastic
    ins = pl("#5a0d18", 0.8, spec=0.0)
    teeth = pl("#f6f0e4", 0.6, spec=0.0)
    tongue = pl("#d4586c", 0.7, spec=0.0)
    W["mouth"] = {}
    for who in ("me", "ruiz", "kofi", "bell"):
        parts = []
        for tag, mat, sc, dy, dz in (("in", ins, (0.2, 0.06, 0.3), 0.0, 0.0),
                                     ("teeth", teeth, (0.17, 0.05, 0.065), -0.03, 0.2),
                                     ("tongue", tongue, (0.11, 0.05, 0.1), -0.035, -0.15)):
            ob = kit.sphere(f"mouth.{who}.{tag}", 1.0, (0, 0, -200), mat, seg=14)
            ob.scale = sc
            parts.append((ob, dy, dz))
        W["mouth"][who] = parts


def build_win(kit):
    """The window edge seen from the cab in the three rock shots: a dark-teal side bar and a lip along the bottom,
    placed in the world just inside the truck window (not on the camera) by the cue "win"."""
    m = kit.plastic("#1b5f5a", 0.6, spec=0.1)
    W["win"] = [kit.box("win.bar", (0.015, 0.04, 0.6), (0, 0, -200), m),
                kit.box("win.lip", (0.6, 0.04, 0.03), (0, 0, -200), m)]
    for ob in W["win"]:
        ob.rotation_mode = "QUATERNION"


def build_loaf(kit):
    loaf = kit.sphere("loaf", 0.4, (0, 0.9, -200), kit.plastic("#eab870", 0.8, spec=0.05), seg=18)
    loaf.scale = (1.0, 0.95, 0.75)
    W["loaf"] = loaf


# ---------------------------------------------------------------------------------------------- build / animate
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    # afternoon gold: a key from the north-west (lights the far wall, the rocks, the ground) and a no-shadow fill from
    # the south (lights faces and the bluff, which look the other way)
    key = kit.light("key", "SUN", (-14, 14, 46), 4.3, GOLD_KEY, size=0.06)
    key.data.angle = 0.06
    kit.aim(key, (0, 0, 0))
    face = kit.light("face", "SUN", (3, -20, 25), 2.4, GOLD_FACE, shadow=False)
    face.data.angle = 0.4
    kit.aim(face, (0, 0, 0))
    build_land(kit)
    build_rim(kit)
    build_post(kit)
    build_rocks(kit)
    build_truck(kit)
    build_car(kit)
    build_loaf(kit)
    build_mouths(kit)
    build_win(kit)
    return {}


def animate(kit, story, tl, t, ctx):
    # the one slow light change
    d = sample("dusk", tl, t, {"v": 0.0})["v"]
    for name, a, b_ in (("key", GOLD_KEY, DUSK_KEY), ("face", GOLD_FACE, DUSK_FACE)):
        kit.LIGHTS[name]["light"].color = mix(a, b_, d, kit)
    wd = bpy.context.scene.world
    if wd is not None and wd.node_tree is not None and "Background" in wd.node_tree.nodes:
        wd.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0 - 0.3 * d
    if wd is not None and wd.node_tree is not None and "Background" in wd.node_tree.nodes:
        wd.node_tree.nodes["Background"].inputs["Color"].default_value = (*mix(GOLD_SKY, DUSK_SKY, d, kit), 1.0)
    gains = {"key": 1.0 - 0.25 * d, "face": 1.0 - 0.05 * d}
    # the post: placed by cue, on cuts
    ps = sample("post", tl, t, {"x": G.POST_RAIL[0], "y": G.POST_RAIL[1]})
    W["post"].location = (ps["x"], ps["y"], 0.0)
    sh = sample("show", tl, t, {"car": 0.0, "loaf": 0.0, "pane": 0.0, "rim": 0.0})
    W["car"].location = (G.CAR[0], G.CAR[1], 0.0 if sh["car"] > 0.5 else -200.0)
    W["loaf"].location = (0.0, 0.9, 0.88 if sh["loaf"] > 0.5 else -200.0)
    rk = sample("rocks", tl, t, {"r1": 1.0, "r2": 1.0, "r3": 1.0})
    for n in (1, 2, 3):
        for ob in W["rocks"][n]:
            ob.hide_render = rk[f"r{n}"] < 0.5
    wn = sample("win", tl, t, {"on": 0.0, "px": 0.0, "py": 0.0, "pz": 0.0, "qx": 0.0, "qy": 0.0, "qz": 0.0,
                               "fx": 0.0, "fy": -1.0, "fz": 0.0})
    quat = Vector((wn["fx"], wn["fy"], wn["fz"])).to_track_quat("-Y", "Z")
    for ob, key_ in zip(W["win"], ("p", "q")):
        ob.location = (wn[key_ + "x"], wn[key_ + "y"], wn[key_ + "z"] if wn["on"] > 0.5 else -200.0)
        ob.rotation_quaternion = quat
    pp = sample("panepos", tl, t, {"x": -0.985, "y": -0.1, "rz": 0.0, "s": 1.0})
    W["paneg"].scale = (pp["s"], pp["s"], pp["s"])
    W["paneg"].location = (pp["x"], pp["y"], 0.0)
    W["paneg"].rotation_euler = (0.0, 0.0, math.radians(pp["rz"]))
    for ob in W["pane"]:
        ob.hide_render = sh["pane"] < 0.5
    for ob in W["rim"]:
        ob.hide_render = sh["rim"] < 0.5
    # shouting mouths: attached to their heads on every call (idempotent) and shown by cue
    shout = sample("shout", tl, t, {n: 0.0 for n in W["mouth"]})
    for who, ob in W["mouth"].items():
        hg = bpy.data.objects.get(f"{who}.headg")
        if hg is not None:
            for part, dy, dz in ob:
                if part.parent is not hg:
                    part.parent = hg
                    part.location = (0, -0.6 + dy, MOUTH_Z + dz)
                part.hide_render = hg.hide_render or shout[who] < 0.5
    # seated: legs level while the character sits (eased over a cue's own dur)
    sit = sample("sit", tl, t, {n: 0.0 for n in SEATED})
    for who in SEATED:
        s = sit[who]
        if s > 0.001:
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (leg.rotation_euler.x * (1 - s) + SIT * s, 0, 0)
    return gains
