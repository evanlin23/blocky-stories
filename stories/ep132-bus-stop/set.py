"""ep132 "bus stop": one sunny morning on a small-town corner. A red bus shelter (glass back, a pale yellow side wall with
a slate chalk board, a long bench), a cherry tree, the street, and across it the brick bus depot with its big blue
roll-up door. The bus waits inside the depot until the door is up.

Batch 14: ONE sun, never changed; nothing blinks, glows or flickers. No text anywhere: the only marks are the chalk
numerals ("41", then "42") and tally strokes (then a chalk sun) on the slate board.
No set moves: the depot door is shut in one shot and already up in the next (a cut, never a roll); the bus is placed
by cues on cuts (inside the depot, at its mouth, stopped at the shelter) and never drives on screen.
Cues read by animate(): sit (per character 0..1, eased), door (up 0/1), chalk (two 0/1), bus (x, y, yaw, on a cut).
Every extra (mustaches, backpack, bus, board, sun) is built here in build(); animate attaches the mustaches to
their heads on every call, idempotently (the cast exists only after build).
"""
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

W = {}
SIT = -math.pi / 2 * 0.97
SEATED = ("me", "driver", "driver_b", "wa", "ma", "nc")


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


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


# ---------------------------------------------------------------------------------------------- the street and the depot
def build_ground(kit):
    pl = kit.plastic
    kit.plane("lawn", (500, 500), (0, 0, -0.03), pl("#62c45a", 0.9, spec=0.05))
    kit.box("sidewalk", (40, 6.6, 0.1), (0, 1.3, -0.05), kit.texture("concrete", 1.0, tint="#f0ece4"))
    kit.box("kerb", (40, 0.22, 0.16), (0, -2.0, 0.0), pl("#d8d4cc", 0.8, spec=0.05))
    kit.box("road", (60, 9.0, 0.1), (0, -6.5, -0.05), kit.texture("asphalt", 0.5, tint="#c8c8d0"))
    for k in range(-5, 6):   # a dashed centre line, plain paint
        kit.box(f"road.dash{k}", (1.6, 0.14, 0.02), (k * 3.0, -6.5, 0.005), pl("#f4e9a8", 0.7))
    kit.box("apron", (40, 1.2, 0.1), (0, -11.35, -0.05), kit.texture("concrete", 1.0, tint="#f0ece4"))


def build_depot(kit):
    pl = kit.plastic
    brick = kit.texture("brick", 1.0, tint="#f0a888")
    y0 = G.DEPOT_Y            # the front face's plane
    depth = 15.0
    cy = y0 - depth / 2
    # the front wall around a 5.2 x 3.6 opening
    kit.box("depot.fl", (6.6, 0.3, 5.4), (-5.9, y0 - 0.15, 2.7), brick)
    kit.box("depot.fr", (6.6, 0.3, 5.4), (5.9, y0 - 0.15, 2.7), brick)
    kit.box("depot.fh", (5.2, 0.3, 1.8), (0, y0 - 0.15, 4.5), brick)
    kit.box("depot.back", (19.2, 0.3, 5.4), (0, y0 - depth, 2.7), brick)
    kit.box("depot.sideW", (0.3, depth, 5.4), (-9.45, cy, 2.7), brick)
    kit.box("depot.sideE", (0.3, depth, 5.4), (9.45, cy, 2.7), brick)
    kit.box("depot.roof", (19.8, depth + 0.6, 0.3), (0, cy, 5.55), pl("#8a8f98", 0.7))
    kit.box("depot.floor", (19, depth, 0.1), (0, cy, -0.05), kit.texture("concrete", 1.0, tint="#e0dcd2"))
    kit.box("depot.cap", (19.4, 0.5, 0.25), (0, y0 + 0.1, 5.35), pl("#a8503a", 0.7))
    # the roll-up door: a blue panel with ribs (hidden once the door is up), its roll box above the opening stays
    blue = pl("#3a7fd6", 0.5, spec=0.3)
    dark = pl("#2a62ad", 0.5)
    parts = [kit.box("door.panel", (5.2, 0.1, 3.6), (0, y0 - 0.1, 1.8), blue)]
    for k in range(9):
        parts.append(kit.box(f"door.rib{k}", (5.2, 0.03, 0.07), (0, y0 - 0.045, 0.2 + k * 0.4), dark))
    for sx in (-1, 1):
        parts.append(kit.box(f"door.edge{sx}", (0.12, 0.05, 3.6), (sx * 2.55, y0 - 0.04, 1.8), dark))
    W["door"] = parts
    kit.cyl("door.roll", 0.3, 5.5, (0, y0 + 0.2, 3.95), pl("#2a62ad", 0.5, spec=0.3), rot=(0, math.pi / 2, 0), n=18)
    kit.box("door.rollcap", (5.6, 0.6, 0.08), (0, y0 + 0.2, 4.28), dark)
    # two small plain windows, high up, so the wall isn't blank
    for sx in (-1, 1):
        kit.box(f"depot.win{sx}", (1.4, 0.06, 0.8), (sx * 6.1, y0 + 0.02, 3.6), pl("#9ed4f0", 0.2, spec=0.7))
        kit.box(f"depot.winframe{sx}", (1.6, 0.04, 1.0), (sx * 6.1, y0 + 0.01, 3.6), pl("#f6f1e6", 0.6))


# ---------------------------------------------------------------------------------------------- the bus
def build_bus(kit):
    pl = kit.plastic
    cream = pl("#e6d198", 0.55, spec=0.2)
    red = pl("#c63a30", 0.5, spec=0.2)
    roofm = pl("#e3d8b8", 0.6)
    glass = pl("#7fb2dc", 0.15, spec=0.8)
    floor = pl("#6a6a74", 0.7)
    seat = pl("#e8a030", 0.6)
    dark = pl("#25252b", 0.7)
    root = kit.empty("bus", (0, 0, 0))
    W["bus"] = root

    def b(n, size, loc, m, bev=0.0):
        return kit.box(f"bus.{n}", size, loc, m, root, bevel=bev)

    L = 9.0
    # left (driver) side wall, with a red skirt and blue windows
    b("wl", (0.1, L, 2.55), (1.2, 0, 1.725), cream)
    b("wl.skirt", (0.04, L + 0.04, 0.6), (1.25, 0, 0.78), red)
    for k in range(5):
        b(f"wl.win{k}", (0.04, 1.05, 0.85), (1.25, -2.0 + 1.4 * k, 2.15), glass)
    # right (door) side: a front piece, an open door (ly -3.7 to -2.7) with a header, and the rear piece
    b("wr.f", (0.1, 0.8, 2.55), (-1.2, -4.1, 1.725), cream)
    b("wr.r", (0.1, 7.2, 2.55), (-1.2, 0.9, 1.725), cream)
    b("wr.head", (0.1, 1.0, 0.3), (-1.2, -3.2, 2.85), cream)
    b("wr.skirtf", (0.04, 0.84, 0.6), (-1.25, -4.1, 0.78), red)
    b("wr.skirtr", (0.04, 7.24, 0.6), (-1.25, 0.9, 0.78), red)
    for k in range(4):
        b(f"wr.win{k}", (0.04, 1.05, 0.85), (-1.25, -1.6 + 1.4 * k, 2.15), glass)
    b("step", (0.55, 0.95, 0.12), (-1.0, -3.2, 0.3), pl("#9a9aa2", 0.6))
    # the front: red lower panel, two cream pillars, a red header band, a dark rim round the open windshield (no glass
    # to hide a face), two round headlights in chrome rings
    rim = pl("#3a3a44", 0.6)
    b("front.low", (2.5, 0.12, 0.65), (0, -4.44, 0.775), red)
    b("front.pl", (0.25, 0.12, 1.6), (-1.125, -4.44, 1.9), cream)
    b("front.pr", (0.25, 0.12, 1.6), (1.125, -4.44, 1.9), cream)
    b("front.head", (2.5, 0.12, 0.3), (0, -4.44, 2.85), red)
    b("front.band", (2.5, 0.12, 0.1), (0, -4.44, 1.15), cream)
    b("rim.t", (2.04, 0.04, 0.06), (0, -4.52, 2.67), rim)
    b("rim.b", (2.04, 0.04, 0.06), (0, -4.52, 1.17), rim)
    for sx in (-1, 1):
        b(f"rim.s{sx}", (0.06, 0.04, 1.56), (sx * 1.0, -4.52, 1.92), rim)
        kit.cyl(f"bus.ring{sx}", 0.27, 0.05, (sx * 0.85, -4.52, 0.8), pl("#cfd2d6", 0.3, spec=0.8), root,
                rot=(math.pi / 2, 0, 0), n=16)
        kit.cyl(f"bus.lamp{sx}", 0.2, 0.05, (sx * 0.85, -4.55, 0.8), pl("#fff3c8", 0.3), root,
                rot=(math.pi / 2, 0, 0), n=16)
    b("bumper", (2.56, 0.22, 0.18), (0, -4.5, 0.55), pl("#9a9aa2", 0.5, spec=0.5))
    b("rear", (2.5, 0.1, 2.55), (0, 4.45, 1.725), cream)
    b("roof", (2.6, L + 0.2, 0.12), (0, 0, 3.06), roofm, 0.03)
    b("floor", (2.4, L - 0.2, 0.05), (0, 0, 0.475), floor)
    for sx in (-1, 1):
        for ly in (-3.0, 2.8):
            kit.cyl(f"bus.wheel{sx}{ly}", 0.5, 0.3, (sx * 1.2, ly, 0.5), dark, root, rot=(0, math.pi / 2, 0), n=16)
            kit.cyl(f"bus.hub{sx}{ly}", 0.24, 0.32, (sx * 1.2, ly, 0.5), pl("#cfd2d6", 0.3, spec=0.8), root,
                    rot=(0, math.pi / 2, 0), n=10)
    # seats: the driver's, the front seat on the door side, and rows behind
    for sx_, ly in ((G.BUS_DRV[0], G.BUS_DRV[1]), (G.BUS_FRONT[0], G.BUS_FRONT[1])):
        b(f"seat.{sx_}", (0.55, 0.55, 0.45), (sx_, ly, 0.725), seat, 0.04)
        b(f"seatback.{sx_}", (0.55, 0.1, 0.8), (sx_, ly + 0.3, 1.35), seat, 0.04)
    for k, ly in enumerate((-1.6, -0.2, 1.2, 2.6)):
        for sx_ in (-0.62, 0.62):
            b(f"row{k}.{sx_}", (0.8, 0.5, 0.45), (sx_, ly, 0.725), seat, 0.04)
            b(f"rowback{k}.{sx_}", (0.8, 0.1, 0.8), (sx_, ly + 0.28, 1.35), seat, 0.04)
    b("dash", (2.2, 0.32, 0.55), (0, -4.28, 0.78), pl("#4a4a54", 0.6))
    b("column", (0.1, 0.1, 0.5), (G.BUS_DRV[0], -3.98, 1.18), dark)
    kit.cyl("bus.wheel.steer", 0.21, 0.05, (G.BUS_DRV[0], -3.82, 1.36), dark, root, rot=(1.0, 0, 0), n=16)
    # the interior light stays on, constant
    kit.light("businside", "POINT", (0, -1.5, 2.5), 90, "#fff4e4", size=0.5, shadow=False, parent=root)


# ---------------------------------------------------------------------------------------------- the shelter
def build_shelter(kit):
    pl = kit.plastic
    red = pl("#d63a32", 0.45, spec=0.3)
    yellow = pl("#f6d76a", 0.8, spec=0.05)
    glass = pl("#cfeeff", 0.3, spec=0.5)
    wood = kit.planks("#d9a45b", "#c8934a", 2.0)
    for sx in (-2.5, 1.85):
        for sy in (0.7, 1.75):
            # the front-right post stands out at the wall's end, so it never crosses a face on the bench's right end
            px = 3.45 if (sx, sy) == (1.85, 0.7) else sx
            kit.box(f"shelter.post{sx}{sy}", (0.1, 0.1, 2.5), (px, sy, 1.25), red)
    roof = kit.box("shelter.roof", (6.2, 1.9, 0.12), (0.4, 1.35, 2.56), red, bevel=0.02)
    noshadow(roof)
    # glass back (an opaque pale panel), with a red frame
    kit.box("shelter.glass", (4.35, 0.05, 1.9), (-0.325, 1.76, 1.3), glass)
    kit.box("shelter.rail", (4.35, 0.08, 0.1), (-0.325, 1.76, 2.3), red)
    kit.box("shelter.sill", (4.35, 0.08, 0.1), (-0.325, 1.76, 0.3), red)
    for k, x in enumerate((-2.5, -1.4, -0.3, 0.8, 1.85)):
        kit.box(f"shelter.mull{k}", (0.07, 0.08, 1.9), (x, 1.76, 1.3), red)
    # the pale yellow side wall (face at y 1.55) with the slate chalk board on it
    kit.box("shelter.wall", (1.7, 0.2, 2.5), (2.7, 1.65, 1.25), yellow)
    # the bench
    kit.box("bench.top", (3.5, 0.5, 0.07), (0.05, 1.12, G.SEAT_Z - 0.035), wood, bevel=0.01)
    for sx in (-1.5, 1.6):
        for sy in (0.95, 1.3):
            kit.box(f"bench.leg{sx}{sy}", (0.08, 0.08, 0.43), (sx, sy, 0.215), red)
    kit.box("bench.rail", (3.4, 0.06, 0.08), (0.05, 1.12, 0.3), red)
    # the backpack on the ground by the bench's right end
    pack = pl("#d68a2a", 0.6)
    kit.box("pack.body", (0.34, 0.2, 0.45), (1.95, 0.7, 0.225), pack, bevel=0.04)
    kit.box("pack.flap", (0.32, 0.22, 0.12), (1.95, 0.7, 0.4), pl("#a9661a", 0.6), bevel=0.03)
    kit.box("pack.strap", (0.05, 0.03, 0.3), (1.95, 0.585, 0.25), pl("#7a4a14", 0.6))
    # two red tally strokes on the steel foot of the bench (lore, held in the shoe shot): 1 cm proud
    for k in range(2):
        kit.box(f"bench.tally{k}", (0.025, 0.012, 0.13), (-1.5 + 0.06 * k, 0.9, 0.2), pl("#8a1212", 0.5))


def build_chalk(kit):
    pl = kit.plastic
    cx, cy, cz = G.BOARD
    slate = pl("#2f4a5a", 0.85, spec=0.03)
    frame = pl("#8a5a34", 0.7)
    chalk = pl("#fbfbf2", 0.9, spec=0.02)
    kit.box("board.slate", (1.28, 0.03, 1.5), (cx + 0.13, 1.535, cz), slate)
    kit.box("board.frame.t", (1.38, 0.05, 0.06), (cx + 0.13, 1.525, cz + 0.78), frame)
    kit.box("board.frame.b", (1.38, 0.05, 0.06), (cx + 0.13, 1.525, cz - 0.78), frame)
    for sx in (-1, 1):
        kit.box(f"board.frame{sx}", (0.06, 0.05, 1.56), (cx + 0.13 + sx * 0.67, 1.525, cz), frame)
    y = 1.51
    t, dh, dw = 0.085, 0.78, 0.34
    zc = cz + 0.18                      # numerals sit in the board's upper part
    segs = {}

    def seg(prefix, cxd, name, size, loc):
        ob = kit.box(f"chalk.{prefix}{name}", size, (cxd + loc[0], y, zc + loc[1]), chalk)
        segs[name] = ob
        return ob

    def digit(prefix, cxd, want):
        pos = {"a": (0, dh / 2 - t / 2, dw, t), "g": (0, 0, dw, t), "d": (0, -dh / 2 + t / 2, dw, t),
               "f": (-dw / 2 + t / 2, dh / 4, t, dh / 2), "b": (dw / 2 - t / 2, dh / 4, t, dh / 2),
               "e": (-dw / 2 + t / 2, -dh / 4, t, dh / 2), "c": (dw / 2 - t / 2, -dh / 4, t, dh / 2)}
        out = {}
        for k, (px, py, sw, sh) in pos.items():
            out[k] = kit.box(f"chalk.{prefix}{k}", (sw, 0.03, sh), (cxd + px, y, zc + py), chalk)
        return out

    seven = {0: "abcdef", 1: "bc", 2: "abged", 4: "fgbc"}
    W["tens"] = digit("t", cx - 0.19, 4)
    W["ones"] = digit("o", cx + 0.25, 1)
    W["sevenseg"] = seven
    for k, ob in W["tens"].items():
        ob.hide_render = k not in seven[4]
    # tally strokes (4 bars and a slash) and, from day 42, a chalk sun in the same place
    tx, tz = cx + 0.13, cz - 0.42
    W["tally"] = []
    for k in range(4):
        W["tally"].append(kit.box(f"chalk.tally{k}", (0.06, 0.03, 0.34), (tx - 0.3 + 0.2 * k, y, tz), chalk))
    W["tally"].append(kit.box("chalk.tally4", (0.9, 0.03, 0.06), (tx, y, tz), chalk, rot=(0, -0.3, 0)))
    W["sun"] = [kit.cyl("chalk.sun", 0.2, 0.03, (tx, y, tz), chalk, rot=(math.pi / 2, 0, 0), n=20)]
    for k in range(8):
        a = k * math.pi / 4
        W["sun"].append(kit.box(f"chalk.ray{k}", (0.07, 0.03, 0.22), (tx + 0.4 * math.cos(a), y, tz + 0.4 * math.sin(a)),
                                chalk, rot=(0, math.pi / 2 - a, 0)))
    for ob in W["sun"]:
        ob.hide_render = True


def build_tree(kit):
    pl = kit.plastic
    kit.cyl("cherry.trunk", 0.16, 2.6, (-3.7, 2.4, 1.3), pl("#6a4a32", 0.8), n=10)
    pink = pl("#f5a3c0", 0.7, spec=0.05)
    for k, (dx, dy, dz, r) in enumerate([(0, 0, 3.4, 1.35), (-0.9, 0.2, 3.0, 0.95), (0.9, -0.1, 3.1, 1.0),
                                          (0.1, 0.5, 4.0, 0.9), (-0.3, -0.5, 3.7, 0.85)]):
        kit.sphere(f"cherry.bloom{k}", r, (-3.7 + dx, 2.4 + dy, dz), pink, seg=14)
    kit.prop("sub_building_type_a", (-9.0, 13.0, 0), rot=180, height=7.0)
    kit.prop("sub_building_type_c", (7.5, 14.0, 0), rot=180, height=6.5)
    kit.prop("commontree_1", (12.0, 9.0, 0), rot=20, height=6.0, tint="#d4f0c4")


def build_stache(kit):
    """The mustaches are built here (a brown block each side of the nose) and attached to their heads on the first
    animate, when the cast exists. Plain unlit brown, nothing glowing."""
    m = kit.plastic("#4a2e1c", 0.8)
    for who in ("driver", "driver_b"):
        for sx in (-1, 1):
            W.setdefault("stache", []).append(
                (who, kit.box(f"{who}.stache{sx}", (0.3, 0.08, 0.1), (0, 0, 0), m, bevel=0.03), sx))


# ---------------------------------------------------------------------------------------------- build / animate
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    # ONE sun, constant, high from the south so faces toward the camera are lit
    sun = kit.light("sun", "SUN", (18, -27, 51), 1.0, "#fff1d6", size=0.06)
    sun.data.angle = 0.05
    kit.aim(sun, (0, 0, 0))
    fill = kit.light("fill", "SUN", (0, -10, 30), 1.0, "#e8f0ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    build_ground(kit)
    build_depot(kit)
    build_bus(kit)
    build_shelter(kit)
    build_chalk(kit)
    build_tree(kit)
    build_stache(kit)
    # constant soft fills: the depot's north face and the bus nose (the sun is behind them), and the depot inside
    df = kit.light("depotfill", "AREA", (0, -6.5, 5.0), 1500, "#fff4e4", size=5.0, shadow=False)
    kit.aim(df, (0, G.DEPOT_Y - 1.5, 1.8))
    di = kit.light("depotin", "AREA", (0, -16.0, 4.6), 700, "#fff4e4", size=5.0, shadow=False)
    kit.aim(di, (0, -16.0, 0.5))
    bf = kit.light("busfill", "AREA", (-7.5, -4.0, 2.8), 700, "#fff4e4", size=3.0, shadow=False)
    kit.aim(bf, (-0.9, -3.45, 1.8))
    bf2 = kit.light("busfill2", "AREA", (-8.0, 5.0, 3.0), 1500, "#fff4e4", size=3.0, shadow=False)   # the door side
    kit.aim(bf2, (0.6, -2.3, 1.5))
    return {}


def _place_bus(st):
    r = W["bus"]
    r.location = (st["x"], st["y"], 0.0)
    r.rotation_euler = (0, 0, math.radians(st["yaw"]))


def animate(kit, story, tl, t, ctx):
    # the mustaches follow their heads on EVERY call (idempotent), so a shard that starts mid-film sees what a
    # continuous run sees; hidden state follows the head's
    for who, ob, sx in W.get("stache", []):
        hg = bpy.data.objects.get(f"{who}.headg")
        if hg is not None:
            if ob.parent is not hg:
                ob.parent = hg
                ob.location = (sx * 0.17, -0.64, -0.2)
                ob.rotation_euler = (0, sx * 0.3, 0)
            ob.hide_render = hg.hide_render
    gains = {"sun": 4.2, "fill": 1.2}
    # the bus: placed by cue (on cuts), never driven
    bs = sample("bus", tl, t, {"x": G.BUS_HIDE[0], "y": G.BUS_HIDE[1], "yaw": G.BUS_HIDE[2]})
    _place_bus(bs)
    # the door: up from its cue, a cut (no roll)
    up = sample("door", tl, t, {"up": 0.0})["up"] > 0.5
    for ob in W["door"]:
        ob.hide_render = up
    # the chalk: "41" with tally strokes, then "42" with a chalk sun
    two = sample("chalk", tl, t, {"two": 0.0})["two"] > 0.5
    want = W["sevenseg"][2 if two else 1]
    for k, ob in W["ones"].items():
        ob.hide_render = k not in want
    for ob in W["tally"]:
        ob.hide_render = two
    for ob in W["sun"]:
        ob.hide_render = not two
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
