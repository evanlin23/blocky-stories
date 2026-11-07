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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

W = {}
SIT = -math.pi / 2 * 0.97
SEATED = ("me",)
GOLD_KEY, DUSK_KEY = "#ffd9a0", "#9a82e8"
GOLD_FACE, DUSK_FACE = "#fff0dc", "#c0b0f8"
GOLD_SKY, DUSK_SKY = "#8fd0ff", "#7a6cc0"


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
    cream = pl("#fff2d0", 0.7, spec=0.05)
    kit.box("post.body", (0.8, 0.8, 3.1), (0, 0, 1.55), wood, root)
    kit.box("post.cap", (0.9, 0.9, 0.1), (0, 0, 3.15), pl("#7a5332", 0.8), root)
    for face in (-1, 1):                       # -1: the south face (seen from the canyon side), +1: the north face
        yy = face * 0.425
        m = -face                              # a viewer on the south side has +x to the right; on the north, -x
        kit.box(f"post.one{face}.stem", (0.24, 0.07, 1.62), (m * 0.03, yy, 2.0), cream, root)
        kit.box(f"post.one{face}.flag", (0.4, 0.07, 0.19), (m * -0.17, yy, 2.66), cream, root,
                rot=(0, m * 0.62, 0))
        kit.box(f"post.one{face}.base", (0.66, 0.07, 0.16), (0, yy, 1.28), cream, root)
    rim = pl("#ffd9a0", 0.6)
    W["rim"] = [kit.box(f"post.rim{sx}{sy}", (0.06, 0.06, 3.0), (sx * 0.42, sy * 0.42, 1.55), rim, root)
                for sx in (-1, 1) for sy in (-1, 1)]


def build_rocks(kit):
    pl = kit.plastic
    slab = pl("#6e2a22", 0.9, spec=0.03)
    dot = pl("#fff2d0", 0.7, spec=0.05)
    pos = {1: [(0.0, 0.0)], 2: [(-1.5, 0.0), (1.5, 0.0)], 3: [(-1.5, 1.6), (1.5, 1.6), (0.0, -1.7)]}
    for n, x in enumerate(G.ROCK_X, start=1):
        kit.box(f"rock{n}", (6.6, 1.5, 7.6), (x, G.WALL_Y + 0.75, G.ROCK_Z), slab, bevel=0.08)
        for k, (dx, dz) in enumerate(pos[n]):
            # a flat cream disc, 3 cm proud of the slab face (y = WALL_Y + 1.5)
            kit.cyl(f"rock{n}.dot{k}", 1.25, 0.1, (x + dx, G.WALL_Y + 1.5 + 0.02, G.ROCK_Z + dz), dot,
                    rot=(math.pi / 2, 0, 0), n=28)


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
    b("hood", (1.95, 1.7, 0.55), (0, -1.85, 0.95), teal, 0.03)
    b("grille", (1.9, 0.1, 0.5), (0, -2.74, 0.78), pl("#c8ccd0", 0.4, spec=0.7))
    b("bumper", (2.1, 0.2, 0.2), (0, -2.8, 0.52), pl("#c8ccd0", 0.4, spec=0.7))
    for sx in (-1, 1):
        kit.cyl(f"truck.lamp{sx}", 0.17, 0.08, (sx * 0.7, -2.76, 0.98), pl("#f4ecd0", 0.6), root,
                rot=(math.pi / 2, 0, 0), n=16)
    # cab: door panels below the belt line, A and C pillars, roof, the floor and a dash
    b("floor", (1.96, 2.0, 0.08), (0, -0.1, 0.5), pl("#4a4a54", 0.8))
    for sx in (-1, 1):
        b(f"door{sx}", (0.08, 2.0, 0.7), (sx * 0.99, -0.1, 0.85), teal, 0.02)
        b(f"apil{sx}", (0.12, 0.14, 1.1), (sx * 0.95, -1.05, 1.7), teal)
        b(f"cpil{sx}", (0.12, 0.14, 1.1), (sx * 0.95, 0.85, 1.7), teal)
    b("roof", (2.1, 2.2, 0.12), (0, -0.1, 2.26), teal, 0.03)
    b("dash", (1.9, 0.4, 0.2), (0, -0.8, 1.05), dark, 0.03)
    b("cabback", (1.9, 0.12, 0.8), (0, 0.85, 0.95), teal)
    kit.cyl("truck.wheel.steer", 0.19, 0.04, (G.SEAT[0] - G.XT, -0.52, 1.28), dark, root, rot=(0.95, 0, 0), n=18)
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
    # the knock window: a pale violet pane in the west door and a dark shoulder-high shape outside it, both hidden
    # until the cue "show" pane=1 (they are on a cut, never flashed)
    pane = kit.box("truck.pane", (0.03, 1.55, 0.95), (-0.99, -0.1, 1.64), kit.emit("#8f84d8", 0.55), root)
    sh = pl("#0b0916", 0.9, spec=0.0)
    parts = [kit.box("truck.shadow.torso", (0.06, 0.78, 0.5), (-1.06, -0.1, 1.38), sh, root),
             kit.box("truck.shadow.shL", (0.06, 0.36, 0.2), (-1.06, -0.43, 1.53), sh, root, rot=(0.5, 0, 0)),
             kit.box("truck.shadow.shR", (0.06, 0.36, 0.2), (-1.06, 0.23, 1.53), sh, root, rot=(-0.5, 0, 0)),
             kit.box("truck.shadow.neck", (0.06, 0.2, 0.22), (-1.06, -0.1, 1.72), sh, root)]
    W["pane"] = [pane] + parts


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


def build_loaf(kit):
    loaf = kit.sphere("loaf", 0.34, (0, 0.92, -200), kit.plastic("#d9a05a", 0.8, spec=0.05), seg=18)
    loaf.scale = (1.0, 0.95, 0.75)
    W["loaf"] = loaf


# ---------------------------------------------------------------------------------------------- build / animate
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    # afternoon gold: a key from the north-west (lights the far wall, the rocks, the ground) and a no-shadow fill from
    # the south (lights faces and the bluff, which look the other way)
    key = kit.light("key", "SUN", (-25, 22, 36), 4.3, GOLD_KEY, size=0.06)
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
    return {}


def animate(kit, story, tl, t, ctx):
    # the one slow light change
    d = sample("dusk", tl, t, {"v": 0.0})["v"]
    for name, a, b_ in (("key", GOLD_KEY, DUSK_KEY), ("face", GOLD_FACE, DUSK_FACE)):
        kit.LIGHTS[name]["light"].color = mix(a, b_, d, kit)
    wd = bpy.context.scene.world
    if wd is not None and wd.node_tree is not None and "Background" in wd.node_tree.nodes:
        wd.node_tree.nodes["Background"].inputs["Color"].default_value = (*mix(GOLD_SKY, DUSK_SKY, d, kit), 1.0)
    gains = {"key": 1.0 - 0.45 * d, "face": 1.0 - 0.2 * d}
    # the post: placed by cue, on cuts
    ps = sample("post", tl, t, {"x": G.POST_RAIL[0], "y": G.POST_RAIL[1]})
    W["post"].location = (ps["x"], ps["y"], 0.0)
    sh = sample("show", tl, t, {"car": 0.0, "loaf": 0.0, "pane": 0.0, "rim": 0.0})
    W["car"].location = (G.CAR[0], G.CAR[1], 0.0 if sh["car"] > 0.5 else -200.0)
    W["loaf"].location = (0.0, 0.92, 1.0 if sh["loaf"] > 0.5 else -200.0)
    for ob in W["pane"]:
        ob.hide_render = sh["pane"] < 0.5
    for ob in W["rim"]:
        ob.hide_render = sh["rim"] < 0.5
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
