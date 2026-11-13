"""ep152 "future late": Mom's bright yellow kitchen at night (every lamp on, a ceiling and tall walls, the curtains drawn),
fourteen clocks, a round table with a plain pie, and two daylight montage spots (a beach towel at x 60, a small blue
porch at x 90). The only light change is a hard cut between those spots and the kitchen.

The rule meter is the ep124/ep139 cream tag on the camera (top-left, placed by the engine's hud): a wall-phone glyph and a
big "1"; from the tap a call timer (MM:SS); the big digit comes back as "0" when the call ends. Under it a small readout
of Mom's kitchen clock (H:MM). Numerals and glyphs only.

Cues read by animate():
  timer   mode (0 big digit, 1 MM:SS), s (seconds), big (the big digit)
  clock   on (0/1), h, m   (every kitchen clock and the tag's readout)
  phone   mode (0 home screen, 1 call screen), buzz (0..1)
  tap     p (0..1): my finger comes down on the phone
  sit     who ("me"/"mom"), s (0..1)
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
SIT = -math.pi / 2 * 0.97


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def sample(name, tl, t, defaults, who=None):
    """The state of cue track `name` at t: numeric fields eased over a cue's own "dur"."""
    cur, prev = dict(defaults), dict(defaults)
    for c in tl["cues"]:
        if c["name"] != name or (who is not None and c.get("who") != who):
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


# ------------------------------------------------------------------------------------------------ the clocks
def clock(kit, name, x, z, r, rim, yaw=0.0, wall_y=3.64, second=False, side=None):
    """A round wall clock facing -y (yaw turns it about the vertical). Fourteen of them tell the same fast time."""
    pl = kit.plastic
    root = kit.empty(name, (x, wall_y, z) if side is None else side, rot=(0, 0, yaw * D2R))
    kit.cyl(f"{name}.rim", r * 1.14, 0.04, (0, -0.01, 0), pl(rim, 0.4, spec=0.3), root, rot=(math.pi / 2, 0, 0), n=28)
    kit.cyl(f"{name}.face", r, 0.02, (0, -0.03, 0), pl("#f6efdc", 0.5), root, rot=(math.pi / 2, 0, 0), n=28)
    ink = pl("#2a2018", 0.5)
    for i in range(12):
        a = i * 30 * D2R
        big = i % 3 == 0
        ln = r * (0.2 if big else 0.1)
        wd = r * (0.1 if big else 0.05)
        rr = r * 0.9 - ln / 2
        kit.box(f"{name}.tick{i}", (wd, 0.008, ln), (rr * math.sin(a), -0.0445, rr * math.cos(a)), ink, root,
                rot=(0, a, 0))
    hp = kit.empty(f"{name}.hp", (0, -0.052, 0), root)
    mp = kit.empty(f"{name}.mp", (0, -0.062, 0), root)
    kit.box(f"{name}.hour", (r * 0.2, 0.012, r * 0.5), (0, 0, r * 0.25 - r * 0.03), ink, hp, bevel=0.003)
    kit.box(f"{name}.min", (r * 0.13, 0.012, r * 0.82), (0, 0, r * 0.41 - r * 0.03), ink, mp, bevel=0.003)
    kit.cyl(f"{name}.cap", r * 0.09, 0.016, (0, -0.07, 0), pl("#d94a3a", 0.4), root, rot=(math.pi / 2, 0, 0), n=10)
    sp = None
    if second:
        sp = kit.empty(f"{name}.sp", (0, -0.074, 0), root)
        kit.box(f"{name}.sec", (r * 0.05, 0.008, r * 0.86), (0, 0, r * 0.4), pl("#d94a3a", 0.4), sp)
    W.setdefault("clocks", []).append((hp, mp, sp))
    return root


# ------------------------------------------------------------------------------------------------ the kitchen
def build_kitchen(kit):
    pl = kit.plastic
    X, WY = G.ROOM_X, G.WALL_Y
    yellow = pl("#f5d76e", 0.75)
    cream = pl("#efe4c4", 0.7)
    white = pl("#d9d2c0", 0.65)
    teal = pl("#2fa39a", 0.5)
    red = pl("#d94a3a", 0.5)
    wood = pl("#c98a4b", 0.55, spec=0.1)
    dark = pl("#3b2e26", 0.6)
    # shell: floor, four walls, ceiling
    kit.box("k.floor", (2 * X, 6.6, 0.1), (0, 0.6, -0.05), kit.texture("wood", 0.9, tint="#f0c890"))
    kit.box("k.wallN", (2 * X + 0.4, 0.2, G.CEIL), (0, WY - 0.0, G.CEIL / 2), yellow)
    kit.box("k.wallW", (0.2, 6.6, G.CEIL), (-X - 0.1, 0.6, G.CEIL / 2), yellow)
    kit.box("k.wallE", (0.2, 6.6, G.CEIL), (X + 0.1, 0.6, G.CEIL / 2), yellow)
    kit.box("k.wallS", (2 * X + 0.4, 0.2, G.CEIL), (0, -2.8, G.CEIL / 2), yellow)
    kit.box("k.ceil", (2 * X + 0.4, 6.8, 0.12), (0, 0.6, G.CEIL + 0.06), pl("#f7edd2", 0.8))
    # wainscot, chair rail and a crown strip all round
    for nm, (sx, sy, cx, cy) in {"N": (2 * X, 0.04, 0, WY - 0.12), "W": (0.04, 6.4, -X + 0.02, 0.6), "E": (0.04, 6.4, X - 0.02, 0.6),
                                  "S": (2 * X, 0.04, 0, -2.68)}.items():
        kit.box(f"k.wain{nm}", (sx, sy, 0.0) if False else (max(sx, 0.04), max(sy, 0.04), 0.92), (cx, cy, 0.46), white)
        kit.box(f"k.rail{nm}", (max(sx, 0.07), max(sy, 0.07), 0.07), (cx, cy, 0.95), teal)
        kit.box(f"k.crown{nm}", (max(sx, 0.07), max(sy, 0.07), 0.1), (cx, cy, G.CEIL - 0.05), teal)
    # a rug under the table
    kit.box("k.rug", (3.0, 2.3, 0.02), (0, 1.9, 0.01), pl("#c4553d", 0.9))
    kit.box("k.rug2", (2.7, 2.0, 0.025), (0, 1.9, 0.012), pl("#f0dfb4", 0.9))
    kit.box("k.rug3", (2.2, 1.5, 0.03), (0, 1.9, 0.014), pl("#3f9a93", 0.9))
    # counters along the north wall: fridge, left run (sink), the stove under the big clock, right run
    ty = WY - 0.1 - 0.32
    kit.box("k.fridge", (0.84, 0.76, 1.85), (-X + 0.5, ty + 0.03, 0.925), pl("#dcd6c6", 0.4, spec=0.3), bevel=0.02)
    kit.box("k.fridge.door", (0.8, 0.02, 1.0), (-X + 0.5, ty - 0.36, 1.3), pl("#e6e0d0", 0.4, spec=0.3))
    kit.box("k.fridge.h1", (0.04, 0.05, 0.45), (-X + 0.82, ty - 0.4, 1.3), dark)
    kit.box("k.fridge.h2", (0.04, 0.05, 0.3), (-X + 0.82, ty - 0.4, 0.55), dark)
    kit.box("k.fridge.line", (0.82, 0.022, 0.03), (-X + 0.5, ty - 0.37, 0.88), dark)
    for nm, x0, x1 in (("L", -X + 0.92, -0.46), ("R", 0.46, X)):
        w = x1 - x0
        cx = (x0 + x1) / 2
        kit.box(f"k.cnt{nm}", (w, 0.64, 0.88), (cx, ty, 0.44), white, bevel=0.01)
        kit.box(f"k.top{nm}", (w + 0.02, 0.68, 0.05), (cx, ty - 0.01, 0.905), wood)
        n = max(2, int(w / 0.62))
        for i in range(n):
            px = x0 + (i + 0.5) * w / n
            kit.box(f"k.door{nm}{i}", (w / n - 0.06, 0.02, 0.6), (px, ty - 0.33, 0.45), cream, bevel=0.008)
            kit.box(f"k.knob{nm}{i}", (0.1, 0.03, 0.025), (px, ty - 0.355, 0.72), teal)
    # backsplash: checker tiles from the counter to the clock line
    kit.box("k.splash", (2 * X - 1.0, 0.03, 0.32), (0.3, WY - 0.1 - 0.015, 1.1), kit.checker("#f4ead2", "#2fa39a", 28.0))
    # the stove (a clock above it)
    kit.box("k.stove", (0.92, 0.66, 0.9), (0, ty, 0.45), pl("#e4ddcb", 0.4, spec=0.3), bevel=0.02)
    kit.box("k.stove.win", (0.62, 0.02, 0.34), (0, ty - 0.34, 0.4), pl("#2a2e34", 0.2, spec=0.6))
    kit.box("k.stove.handle", (0.62, 0.04, 0.03), (0, ty - 0.37, 0.64), pl("#8a8e96", 0.3, spec=0.6))
    kit.box("k.stove.top", (0.92, 0.66, 0.04), (0, ty, 0.92), pl("#3a3a3e", 0.4, spec=0.5))
    for k, (dx, dy) in enumerate(((-0.22, -0.14), (0.22, -0.14), (-0.22, 0.14), (0.22, 0.14))):
        kit.cyl(f"k.burner{k}", 0.1, 0.02, (dx, ty + dy, 0.945), pl("#16161a", 0.4), n=14)
    kit.box("k.stove.back", (0.92, 0.1, 0.22), (0, WY - 0.1 - 0.06, 1.04), pl("#e4ddcb", 0.4, spec=0.3))
    kit.cyl("k.pot", 0.14, 0.18, (-0.22, ty - 0.14, 1.04), pl("#8a8e96", 0.3, spec=0.7), n=14)
    kit.cyl("k.potlid", 0.145, 0.025, (-0.22, ty - 0.14, 1.145), pl("#c04a3a", 0.4), n=14)
    kit.cyl("k.pan", 0.12, 0.05, (0.22, ty - 0.14, 0.99), pl("#2a2a2e", 0.4, spec=0.5), n=14)
    # the sink on the left run
    kit.box("k.sink", (0.7, 0.4, 0.04), (-1.5, ty - 0.02, 0.935), pl("#aab0b8", 0.2, spec=0.8))
    kit.box("k.tap", (0.05, 0.05, 0.28), (-1.5, ty + 0.2, 1.06), pl("#aab0b8", 0.2, spec=0.8))
    kit.box("k.tap2", (0.05, 0.2, 0.05), (-1.5, ty + 0.12, 1.19), pl("#aab0b8", 0.2, spec=0.8))
    # shelves with jars (open, so the clocks stay in view) on both runs
    for nm, x0, x1 in (("L", -2.6, -0.85), ("R", 0.85, 3.0)):
        cx = (x0 + x1) / 2
        kit.box(f"k.shelf{nm}", (x1 - x0, 0.22, 0.04), (cx, WY - 0.1 - 0.11, 2.1), wood)
        for i in range(5):
            jx = x0 + 0.2 + i * (x1 - x0 - 0.4) / 4
            h = 0.17 + 0.05 * ((i * 7) % 3)
            kit.cyl(f"k.jar{nm}{i}", 0.06, h, (jx, WY - 0.1 - 0.11, 2.12 + h / 2), pl(["#d94a3a", "#2fa39a", "#f0b840", "#f6efdc", "#7aa45a"][i], 0.45), n=12)
    # an art print and a fruit bowl for colour
    kit.box("k.print.f", (0.5, 0.03, 0.64), (-1.9, WY - 0.1 - 0.015, 2.05) if False else (3.0, WY - 0.1 - 0.015, 1.25), wood)
    kit.box("k.print", (0.4, 0.035, 0.54), (3.0, WY - 0.1 - 0.02, 1.25), pl("#6fb7c9", 0.6))
    kit.box("k.print.sun", (0.14, 0.04, 0.14), (3.04, WY - 0.1 - 0.025, 1.36), pl("#f6c040", 0.5))
    kit.cyl("k.bowl", 0.17, 0.09, (1.9, ty - 0.02, 0.97), pl("#d94a3a", 0.5), n=16)
    for i, c in enumerate(("#f0a030", "#7aa45a", "#d94a3a")):
        kit.sphere(f"k.fruit{i}", 0.07, (1.9 + (i - 1) * 0.1, ty - 0.02 + (0.03 if i == 1 else -0.02), 1.06), pl(c, 0.5), seg=10)
    kit.box("k.toaster", (0.3, 0.17, 0.2), (2.55, ty, 1.02), pl("#c9ccd2", 0.3, spec=0.7), bevel=0.03)
    # the fourteen clocks
    clock(kit, "ck.big", 0.0, 1.95, 0.7, "#d94a3a", second=True)
    spots = [(-1.3, 1.75, 0.16, "#2fa39a"), (-2.0, 1.6, 0.18, "#d94a3a"), (-2.7, 1.8, 0.15, "#2fa39a"),
             (1.45, 1.75, 0.16, "#d94a3a"), (2.05, 1.75, 0.16, "#d94a3a"), (2.7, 1.55, 0.18, "#2fa39a"),
             (-1.2, 2.45, 0.12, "#d94a3a"), (1.2, 2.45, 0.12, "#2fa39a")]
    for i, (x, z, r, c) in enumerate(spots):
        clock(kit, f"ck.n{i}", x, z, r, c)
    for i, (y, z, r, c) in enumerate([(2.9, 1.7, 0.27, "#2fa39a"), (1.9, 1.7, 0.26, "#d94a3a"), (0.9, 1.75, 0.16, "#2fa39a")]):
        clock(kit, f"ck.w{i}", 0, z, r, c, yaw=90, side=(-X + 0.0, y, z))
    clock(kit, "ck.w3", 0, 2.2, 0.14, "#d94a3a", yaw=90, side=(-X + 0.0, 3.45, 2.2))
    clock(kit, "ck.e0", 0, 1.7, 0.17, "#d94a3a", yaw=-90, side=(X - 0.0, 2.2, 1.7))
    # the one window on the west wall, curtains drawn (no black glass); the prop is dressing only
    kit.box("k.win", (0.05, 1.3, 1.3), (-X + 0.03, -0.3, 1.5), pl("#f2efe6", 0.6))
    kit.box("k.curt1", (0.12, 0.7, 1.5), (-X + 0.1, -0.62, 1.5), pl("#e57a5a", 0.8))
    kit.box("k.curt2", (0.12, 0.7, 1.5), (-X + 0.1, 0.02, 1.5), pl("#e57a5a", 0.8))
    kit.box("k.curtrod", (0.05, 1.6, 0.04), (-X + 0.1, -0.3, 2.28), dark)
    # lamps: the floor lamp and the ceiling fixture (both on, warm)
    kit.prop("light_floor1", (-3.0, -1.8, 0), height=1.6)
    kit.prop("light_ceiling1", (0.0, 1.6, G.CEIL - 0.41), height=0.41)
    kit.cyl("k.lampglow", 0.16, 0.06, (0.0, 1.6, G.CEIL - 0.45), kit.emit("#ffe2a0", 1.2, "lampglow"), n=14)
    # the table: pedestal, wood top, checked cloth, plates, mugs and a plain pie (no candles)
    tx, ty_ = G.TABLE
    kit.cyl("t.leg", 0.1, G.TABLE_Z - 0.05, (tx, ty_, (G.TABLE_Z - 0.05) / 2), wood, n=10)
    kit.cyl("t.base", 0.4, 0.05, (tx, ty_, 0.025), wood, n=18)
    kit.cyl("t.top", G.TABLE_R, 0.05, (tx, ty_, G.TABLE_Z - 0.025), wood, n=32)
    kit.cyl("t.cloth", G.TABLE_R - 0.02, 0.012, (tx, ty_, G.TABLE_Z + 0.006), kit.checker("#f4ead2", "#d94a3a", 9.0), n=32)
    kit.cyl("t.runner", 0.01, 0.0, (0, -90, 0), wood, n=3) if False else None
    for nm, (px, py) in (("me", (G.ME_SEAT[0], G.ME_SEAT[1] - 0.5)), ("mom", (G.MOM_SEAT[0], G.MOM_SEAT[1] - 0.5))):
        kit.cyl(f"t.plate.{nm}", 0.15, 0.015, (px, py, G.TABLE_Z + 0.02), pl("#f6efdc", 0.35, spec=0.4), n=20)
        kit.cyl(f"t.plate2.{nm}", 0.1, 0.018, (px, py, G.TABLE_Z + 0.023), pl("#2fa39a", 0.4), n=20)
        kit.cyl(f"t.mug.{nm}", 0.045, 0.1, (px + (0.26 if nm == "mom" else -0.26), py + 0.1, G.TABLE_Z + 0.07),
                pl("#d94a3a" if nm == "me" else "#2f8f8a", 0.4), n=12)
        kit.box(f"t.fork.{nm}", (0.025, 0.17, 0.01), (px - 0.24 if nm == "mom" else px + 0.24, py, G.TABLE_Z + 0.018), pl("#c9ccd2", 0.3, spec=0.7))
    kit.cyl("t.pie", 0.2, 0.06, (0.0, 2.05, G.TABLE_Z + 0.04), pl("#e0a85a", 0.55), n=24)
    kit.cyl("t.pie.top", 0.17, 0.02, (0.0, 2.05, G.TABLE_Z + 0.08), pl("#c4793a", 0.6), n=24)
    kit.cyl("t.pietin", 0.22, 0.03, (0.0, 2.05, G.TABLE_Z + 0.02), pl("#aab0b8", 0.3, spec=0.7), n=24)
    for sx in (-1, 1):
        x = G.ME_SEAT[0] if sx > 0 else G.MOM_SEAT[0]
        chair(kit, f"chair{sx}", x, G.ME_SEAT[1], pl)


def chair(kit, name, x, y, pl):
    """A wooden chair facing -y (back on the +y side)."""
    wood = pl("#c0602f", 0.65)
    root = kit.empty(name, (x, y, 0))
    kit.box(f"{name}.seat", (0.46, 0.46, 0.05), (0, 0, G.SEAT_H - 0.025), wood, root)
    kit.box(f"{name}.cush", (0.4, 0.4, 0.04), (0, 0, G.SEAT_H + 0.02), pl("#2fa39a", 0.8), root)
    kit.box(f"{name}.back", (0.46, 0.04, 0.26), (0, 0.22, G.SEAT_H + 0.15), wood, root)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"{name}.leg{sx}{sy}", (0.05, 0.05, G.SEAT_H - 0.05), (sx * 0.2, sy * 0.2, (G.SEAT_H - 0.05) / 2), wood, root)


# ------------------------------------------------------------------------------------------------ the montage spots
def build_beach(kit):
    pl = kit.plastic
    cx, cy = G.COUSIN
    kit.box("b.sand", (40, 30, 0.1), (cx, cy + 8, -0.05), pl("#f1dca0", 0.9))
    kit.box("b.sea", (40, 12, 0.1), (cx, cy + 24, -0.02), pl("#2f9fd0", 0.3, spec=0.5))
    kit.box("b.foam", (40, 0.7, 0.12), (cx, cy + 17.6, -0.0), pl("#f6f6f0", 0.6))
    # the towel: bold stripes
    for i, c in enumerate(("#d94a3a", "#f6efdc", "#2fa39a", "#f6efdc", "#d94a3a")):
        kit.box(f"b.towel{i}", (0.4, 1.0, 0.03), (cx - 0.8 + i * 0.4, cy - 0.05, 0.015), pl(c, 0.9))
    kit.cyl("b.bottle", 0.05, 0.2, (cx + 0.5, cy - 0.4, 0.13), pl("#f0b840", 0.4), n=10)
    kit.cyl("b.cap", 0.03, 0.05, (cx + 0.5, cy - 0.4, 0.26), pl("#d94a3a", 0.4), n=10)
    # an umbrella behind
    kit.cyl("b.pole", 0.03, 2.1, (cx - 1.4, cy + 1.2, 1.05), pl("#f2efe6", 0.5), n=8)
    kit.cyl("b.umb", 1.2, 0.35, (cx - 1.4, cy + 1.2, 2.15), pl("#d94a3a", 0.6), n=16, r2=0.06)
    kit.cyl("b.umb2", 1.0, 0.1, (cx - 1.4, cy + 1.2, 1.98), pl("#f6efdc", 0.6), n=16)
    # a ball and a bucket
    kit.sphere("b.ball", 0.2, (cx + 1.2, cy + 0.3, 0.2), pl("#f0b840", 0.5), seg=14)
    kit.cyl("b.bucket", 0.14, 0.22, (cx + 1.5, cy - 0.3, 0.11), pl("#2fa39a", 0.5), n=12)


def build_porch(kit):
    pl = kit.plastic
    cx, cy = G.FRIEND
    blue = pl("#4a78b8", 0.65)
    white = pl("#f2efe6", 0.6)
    wood = pl("#b9874f", 0.65)
    kit.box("p.lawn", (40, 30, 0.1), (cx, cy + 6, -0.05), pl("#62c45a", 0.9))
    kit.box("p.floor", (4.4, 2.6, 0.3), (cx, cy + 1.2, 0.15), wood)
    kit.box("p.step", (1.4, 0.5, 0.15), (cx, cy - 0.35, 0.075), wood)
    kit.box("p.wall", (5.6, 0.2, 3.2), (cx, cy + 2.6, 1.6), blue)
    for i in range(10):
        kit.box(f"p.siding{i}", (5.6, 0.03, 0.04), (cx, cy + 2.485, 0.5 + i * 0.28), pl("#3e66a0", 0.7))
    kit.box("p.door", (1.0, 0.06, 2.1), (cx + 1.2, cy + 2.46, 1.35), pl("#d94a3a", 0.55))
    kit.box("p.doorwin", (0.6, 0.04, 0.5), (cx + 1.2, cy + 2.41, 1.9), pl("#bfe4f0", 0.2, spec=0.7))
    kit.box("p.win", (1.0, 0.06, 1.0), (cx - 1.4, cy + 2.46, 1.7), white)
    kit.box("p.winglass", (0.84, 0.04, 0.84), (cx - 1.4, cy + 2.41, 1.7), pl("#bfe4f0", 0.2, spec=0.7))
    kit.box("p.roof", (5.0, 2.8, 0.14), (cx, cy + 1.3, 2.9), pl("#8a4a3a", 0.7))
    kit.box("p.postL", (0.14, 0.14, 2.6), (cx - 2.1, cy + 0.2, 1.6), white)
    kit.box("p.postR", (0.16, 0.16, 2.6), (cx + 0.38, cy + 0.2, 1.6), white)
    kit.box("p.postR2", (0.16, 0.16, 2.6), (cx + 2.1, cy + 0.2, 1.6), white)
    kit.box("p.rail", (1.5, 0.06, 0.07), (cx + 1.4, cy + 0.2, 0.75), white)
    kit.box("p.rail2", (1.5, 0.06, 0.07), (cx - 1.4, cy + 0.2, 0.75), white)
    kit.box("p.mat", (1.0, 0.6, 0.02), (cx + 1.2, cy + 1.6, 0.31), pl("#2fa39a", 0.9))
    kit.cyl("p.pot", 0.18, 0.3, (cx - 1.9, cy + 1.6, 0.45), pl("#c0602f", 0.6), n=12)
    kit.sphere("p.plant", 0.28, (cx - 1.9, cy + 1.6, 0.8), pl("#4aa04a", 0.7), seg=10)
    kit.box("p.hedge", (3.0, 0.8, 0.9), (cx - 4.2, cy + 2.0, 0.45), pl("#4aa04a", 0.8))
    kit.box("p.hedge2", (3.0, 0.8, 0.9), (cx + 4.2, cy + 2.0, 0.45), pl("#4aa04a", 0.8))


# ------------------------------------------------------------------------------------------------ the phone
def build_phone(kit):
    pl = kit.plastic
    px, py, pz = G.PHONE
    root = kit.empty("phone", (px, py, pz))
    W["phone"] = root
    root.scale = (2.6, 2.6, 2.6)
    kit.box("phone.body", (0.085, 0.172, 0.011), (0, 0, -0.0045), pl("#2a2a30", 0.35, spec=0.5), root, bevel=0.006)
    kit.box("phone.cam", (0.016, 0.016, 0.004), (0.0, 0.07, -0.0105), pl("#111114", 0.3), root)
    # the home screen: a speech bubble with three dots on deep blue (as in ep139, minus the paw)
    home = kit.empty("phone.home", (0, 0, 0.0015), root)
    blue = kit.emit("#2f5fb0", 0.9, "screenblue")
    cream = kit.emit("#fff1d0", 1.0, "screencream")
    kit.box("phone.homebg", (0.075, 0.158, 0.002), (0, 0, 0), blue, home)
    kit.box("phone.bub", (0.05, 0.036, 0.002), (0, 0.02, 0.0025), cream, home, bevel=0.004)
    kit.box("phone.bubtail", (0.012, 0.012, 0.002), (-0.012, -0.002, 0.0025), cream, home, rot=(0, 0, 0.785))
    for k in range(3):
        kit.cyl(f"phone.dot{k}", 0.0042, 0.002, ((k - 1) * 0.0125, 0.02, 0.0035), blue, home, n=8)
    # the call screen: teal with a white handset
    call = kit.empty("phone.call", (0, 0, 0.0015), root)
    teal = kit.emit("#14867a", 1.0, "screenteal")
    wh = kit.emit("#ffffff", 1.2, "screenwhite")
    kit.box("phone.callbg", (0.075, 0.158, 0.002), (0, 0, 0), teal, call)
    kit.cyl("phone.calldisc", 0.026, 0.002, (0, 0.0, 0.0025), kit.emit("#0d6258", 1.0, "screendisc"), call, n=20)
    kit.box("phone.hs1", (0.012, 0.04, 0.002), (0, 0.0, 0.0035), wh, call, rot=(0, 0, 0.0), bevel=0.003)
    kit.box("phone.hs2", (0.018, 0.012, 0.002), (0.006, 0.018, 0.0035), wh, call, bevel=0.003)
    kit.box("phone.hs3", (0.018, 0.012, 0.002), (0.006, -0.018, 0.0035), wh, call, bevel=0.003)
    W["home"], W["call"] = home, call
    sk = pl("#7a5238", 0.6)
    fg = kit.empty("finger", (0, -80, 0))
    W["finger"] = fg
    kit.box("finger.tip", (0.034, 0.12, 0.028), (0, -0.06, 0.0), sk, fg, bevel=0.012)
    kit.box("finger.hand", (0.1, 0.16, 0.04), (0.02, -0.2, 0.02), sk, fg, bevel=0.02)
    # the reveal clock: a big kitchen clock the camera frames beside a face (the real big one hides behind our heads);
    # animate() hangs it at a fixed spot in the frame on the shots listed in REV_CLOCK
    rc = clock(kit, "ck.rev", 0.0, 0.0, 0.5, "#d94a3a", second=True, wall_y=0.0)
    rc.location = (0, -80, 0)
    W["revclock"] = rc
    # ring cue: bright strokes either side of the phone, shown while it buzzes
    rg = kit.empty("phone.ring", (0, 0, 0.004), root)
    ringm = kit.emit("#ffd23a", 1.4, "ringglow")
    for sx in (-1, 1):
        for k in range(3):
            ob = kit.box(f"phone.ring{sx}{k}", (0.006, 0.05 - 0.01 * k, 0.002), (sx * (0.068 + 0.026 * k), 0.0, 0.0), ringm, rg,
                         rot=(0, 0, sx * 0.0))
            noshadow(ob)
    W["ring"] = rg
    # a close-up of the hand-hold (S14b): my orange cuff and hand on the cloth, Mom's teal-cuffed flat hand landing on it
    hh = kit.empty("handins", (0, -80, 0))
    W["handins"] = hh
    skin = pl("#7a5238", 0.6)
    skin2 = pl("#8a6040", 0.6)
    # my hand (underneath, right): orange cuff, palm, fingers pointing left, a thumb toward the camera
    kit.box("hi.mycuff", (0.1, 0.14, 0.05), (0.2, 0.0, 0.025), pl("#f08a2a", 0.6), hh, bevel=0.012)
    kit.box("hi.mycuffband", (0.014, 0.145, 0.052), (0.155, 0.0, 0.026), pl("#f8d9a0", 0.6), hh, bevel=0.004)
    kit.box("hi.myhand", (0.1, 0.11, 0.03), (0.1, -0.005, 0.015), skin, hh, bevel=0.008)
    for k in range(4):
        kit.box(f"hi.myfinger{k}", (0.07, 0.021, 0.024), (0.01, -0.035 + k * 0.025 + 0.012, 0.012), skin, hh, bevel=0.008)
    kit.box("hi.mythumb", (0.05, 0.026, 0.026), (0.095, -0.075, 0.013), skin, hh, rot=(0, 0, 0.5), bevel=0.01)
    # Mom's hand (on top, left): teal cuff, palm, four finger blocks over mine, a thumb toward the camera
    mg = kit.empty("hi.mom", (0, 0, 0), hh)
    W["hi.mom"] = mg
    kit.box("hi.momcuff", (0.1, 0.14, 0.058), (-0.16, 0.0, 0.05), pl("#2f8f8a", 0.6), mg, bevel=0.012)
    kit.box("hi.momband", (0.014, 0.145, 0.06), (-0.112, 0.0, 0.05), pl("#bfe8e2", 0.6), mg, bevel=0.004)
    kit.box("hi.momhand", (0.1, 0.11, 0.03), (-0.06, 0.0, 0.052), skin2, mg, bevel=0.008)
    for k in range(4):
        kit.box(f"hi.momfinger{k}", (0.075, 0.021, 0.026), (0.028, -0.039 + k * 0.026, 0.05), skin2, mg, bevel=0.009)
        kit.box(f"hi.momnail{k}", (0.014, 0.015, 0.004), (0.058, -0.039 + k * 0.026, 0.0645), pl("#f4d8c0", 0.5), mg)
    for k in range(3):   # knuckle creases between the fingers' roots
        kit.box(f"hi.momknuck{k}", (0.004, 0.012, 0.004), (-0.012, -0.026 + k * 0.026, 0.0675), pl("#5a3a26", 0.6), mg)
    kit.box("hi.momthumb", (0.055, 0.027, 0.027), (-0.025, -0.075, 0.05), skin2, mg, rot=(0, 0, -0.65), bevel=0.01)
    # my watch for the S21a close: orange sleeve, wrist and fist, a dark strap, a big white dial reading 11:48.
    # animate() hangs it in the frame like the reveal clock; it faces -y like the wall clocks
    cw = kit.empty("cw", (0, -80, 0))
    W["closewatch"] = cw
    ink = kit.emit("#16110d", 1.0, "cwink")
    kit.box("cw.sleeve", (1.5, 0.8, 0.45), (0, 0.0, -1.12), kit.emit("#e87a1c", 0.75, "cworange"), cw, bevel=0.08)
    kit.box("cw.sleeveband", (1.54, 0.84, 0.08), (0, 0.0, -0.88), kit.emit("#f0cf98", 0.7, "cwcream"), cw, bevel=0.03)
    kit.box("cw.wrist", (1.0, 0.6, 1.0), (0, 0.05, -0.3), kit.emit("#7a5238", 0.7, "cwskin"), cw, bevel=0.1)
    kit.box("cw.strap", (1.14, 0.7, 0.62), (0, 0.04, -0.3), kit.emit("#241a14", 0.8, "cwstrap"), cw, bevel=0.06)
    kit.cyl("cw.rim", 0.62, 0.12, (0, -0.36, -0.3), kit.emit("#b88f30", 0.8, "cwrim"), cw, rot=(math.pi / 2, 0, 0), n=28)
    kit.cyl("cw.face", 0.54, 0.06, (0, -0.43, -0.3), kit.emit("#f4f1e6", 0.85, "cwface"), cw, rot=(math.pi / 2, 0, 0), n=28)
    for i in range(12):
        a_ = i * 30 * D2R
        big = i % 3 == 0
        ln, wd = 0.54 * (0.26 if big else 0.14), 0.54 * (0.14 if big else 0.07)
        rr = 0.54 * 0.9 - ln / 2
        kit.box(f"cw.t{i}", (wd, 0.03, ln), (rr * math.sin(a_), -0.47, -0.3 + rr * math.cos(a_)), ink, cw, rot=(0, a_, 0))
    # 11:48: hour hand just short of 12 (354 degrees), minute hand on 48 (288 degrees)
    for nm, ang, ln, wd, yy in (("h", 354.0, 0.32, 0.17, -0.49), ("m", 288.0, 0.5, 0.11, -0.51)):
        pv = kit.empty(f"cw.{nm}p", (0, yy, -0.3), cw)
        pv.rotation_euler = (0, ang * D2R, 0)
        kit.box(f"cw.{nm}", (wd, 0.03, ln), (0, 0, ln / 2 - 0.03), ink, pv, bevel=0.01)
    kit.cyl("cw.cap", 0.07, 0.04, (0, -0.53, -0.3), kit.emit("#d94a3a", 0.9, "cwcap"), cw, rot=(math.pi / 2, 0, 0), n=10)


# ------------------------------------------------------------------------------------------------ the rule meter
DIGIT_SEGS = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd", 6: "afgedc", 7: "abc",
              8: "abcdefg", 9: "abcdfg"}


def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    edge = kit.emit("#2b2118", 0.6, "tagedge")
    plate = kit.emit("#f2e6c8", 0.85, "tagplate")
    ink = kit.emit("#2b2118", 0.6, "tagink")
    teal = kit.emit("#14867a", 0.9, "tagteal")

    def b(name, size, loc, mat, parent=None):
        ob = kit.box(name, size, loc, mat, parent or root)
        noshadow(ob)
        return ob

    b("tag.edge", (1.5, 0.7, 0.006), (0, 0, 0), edge)
    b("tag.plate", (1.44, 0.64, 0.006), (0, 0, 0.007), plate)
    z = 0.016
    cream = kit.emit("#f2e6c8", 0.85, "tagcream")
    g = kit.empty("tag.glyph", (-0.5, 0.0, z), root)
    b("tag.g.body", (0.3, 0.46, 0.006), (0, 0, 0), teal, g)
    gr = kit.cyl("tag.g.grille", 0.075, 0.006, (0, 0.12, 0.007), cream, g, n=14)
    noshadow(gr)
    for r in range(3):
        for c in range(2):
            b(f"tag.g.k{r}{c}", (0.075, 0.05, 0.006), ((c - 0.5) * 0.11, -0.03 - r * 0.075, 0.007), cream, g)

    def seven(prefix, cx, cy, dw, dh, t, zz=z, par=None):
        pos = {"a": (0, dh / 2 - t / 2, dw, t), "g": (0, 0, dw, t), "d": (0, -dh / 2 + t / 2, dw, t),
               "f": (-dw / 2 + t / 2, dh / 4, t, dh / 2), "b": (dw / 2 - t / 2, dh / 4, t, dh / 2),
               "e": (-dw / 2 + t / 2, -dh / 4, t, dh / 2), "c": (dw / 2 - t / 2, -dh / 4, t, dh / 2)}
        return {k: b(f"{prefix}{k}", (sw, sh, 0.006), (cx + px, cy + py, zz), ink, par) for k, (px, py, sw, sh) in pos.items()}

    W["one"] = seven("tag.one", 0.3, 0.0, 0.2, 0.46, 0.07)
    W["digits"] = [seven(f"tag.d{i}", cx, 0.0, 0.1, 0.34, 0.036) for i, cx in enumerate((-0.12, 0.04, 0.3, 0.46))]
    W["colon"] = [b("tag.c1", (0.036, 0.036, 0.006), (0.17, 0.07, z), ink), b("tag.c2", (0.036, 0.036, 0.006), (0.17, -0.07, z), ink)]
    # the clock readout under the plate: H:MM, bigger than ep139's so it reads at phone size (11:57 is four digits)
    clk = kit.empty("tag.clock", (0, -0.63, 0), root)
    W["clockroot"] = clk
    b("tag.cl.edge", (1.5, 0.5, 0.006), (0, 0, 0), edge, clk)
    b("tag.cl.plate", (1.44, 0.44, 0.006), (0, 0, 0.007), plate, clk)
    xs = (-0.5, -0.27, 0.2, 0.43)
    cs = [seven(f"tag.cl{i}", cx, 0.0, 0.16, 0.32, 0.05, z, clk) for i, cx in enumerate(xs)]
    W["clockdigits"] = cs
    W["clockcolon"] = [b("tag.cl.c1", (0.05, 0.05, 0.006), (-0.04, 0.07, z), ink, clk),
                       b("tag.cl.c2", (0.05, 0.05, 0.006), (-0.04, -0.07, z), ink, clk)]


def _digit(d, n):
    segs = DIGIT_SEGS.get(n, "")
    for k, ob in d.items():
        ob.hide_render = k not in segs


# ------------------------------------------------------------------------------------------------ build / animate
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    sun = kit.light("sun", "SUN", (-25, -30, 17), 1.0, "#ffd08a", size=0.06)
    sun.data.angle = 0.05
    kit.aim(sun, (0, 0, 0))
    fill = kit.light("fill", "SUN", (0, -10, 30), 1.0, "#fff0dc", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    kit.light("key", "POINT", (0, 0, 2), 1.0, "#fff4e0", size=0.8, shadow=False)
    kit.light("rimL", "POINT", (0, 0, 3), 1.0, "#ffe9c4", size=0.6, shadow=False)
    kit.light("lampA", "POINT", (-1.6, 1.4, 2.5), 1.0, "#ffdca0", size=0.5, shadow=False)
    kit.light("lampB", "POINT", (1.6, 1.4, 2.5), 1.0, "#ffdca0", size=0.5, shadow=False)
    kit.light("lampC", "POINT", (0.0, -0.8, 2.4), 1.0, "#fff0d0", size=0.5, shadow=False)
    for nm in ("sun", "fill", "key", "rimL", "lampA", "lampB", "lampC"):
        kit.LIGHTS[nm]["obj"].visible_camera = False
    build_kitchen(kit)
    build_beach(kit)
    build_porch(kit)
    build_phone(kit)
    build_tag(kit)
    return {}


def _first_frame(kit, story):
    get = bpy.data.objects.get
    mm = get("mom.headg")
    if mm is not None:
        gold = kit.plastic("#f0c040", 0.3, spec=0.8)
        for sx in (-1, 1):   # gold earrings on the v3 head (2.8 wide), and a glasses cord of gold beads down each cheek
            kit.sphere(f"mom.ear{sx}", 0.14, (sx * 1.46, 0.0, -0.3), gold, mm, seg=10)
            kit.sphere(f"mom.ear2{sx}", 0.1, (sx * 1.46, 0.0, -0.5), gold, mm, seg=10)
        # the bun's knot: a teal scrunchie round its waist and a gold hairpin through the front, so it reads as a bun not a hat
        kit.box("mom.scrunch", (2.6, 2.6, 0.42), (0, 0.15, 1.15 + 0.62), kit.plastic("#2fa39a", 0.5), mm, bevel=0.12)
        kit.box("mom.pin", (2.7, 0.1, 0.12), (0, -0.92, 1.15 + 1.0), gold, mm, rot=(0, 0.45, 0), bevel=0.03)
    build_watch(kit)
    W["inited"] = True


def build_watch(kit):
    """My watch, on my left-hand-side (screen-left) wrist: a strap over the cuff and a dial on the arm's front face,
    parented to the arm block so it goes where the arm goes. Its hands show the real time (ten minutes behind the wall)."""
    arm = bpy.data.objects.get("me.arm-1")
    if arm is None:
        return
    pl = kit.plastic
    edge = pl("#2a2018", 0.5)
    face = pl("#f6efdc", 0.5)
    red = pl("#d94a3a", 0.4)
    strap = pl("#3b2a20", 0.6)
    kit.box("wt.strap", (1.06, 1.06, 0.34), (0, 0, -1.0), strap, arm, bevel=0.05)
    root = kit.empty("wt.root", (0, -0.53, -1.0), arm)
    r = 0.68
    kit.cyl("wt.rim", r * 1.18, 0.14, (0, -0.04, 0), pl("#c9a24a", 0.35, spec=0.6), root, rot=(math.pi / 2, 0, 0), n=24)
    kit.cyl("wt.face", r, 0.06, (0, -0.12, 0), face, root, rot=(math.pi / 2, 0, 0), n=24)
    for i in range(12):
        a = i * 30 * D2R
        big = i % 3 == 0
        ln, wd = r * (0.24 if big else 0.12), r * (0.12 if big else 0.06)
        rr = r * 0.92 - ln / 2
        kit.box(f"wt.t{i}", (wd, 0.04, ln), (rr * math.sin(a), -0.16, rr * math.cos(a)), edge, root, rot=(0, a, 0))
    hp = kit.empty("wt.hp", (0, -0.2, 0), root)
    mp = kit.empty("wt.mp", (0, -0.25, 0), root)
    kit.box("wt.hour", (r * 0.2, 0.05, r * 0.52), (0, 0, r * 0.26), edge, hp, bevel=0.01)
    kit.box("wt.min", (r * 0.14, 0.05, r * 0.86), (0, 0, r * 0.43), edge, mp, bevel=0.01)
    kit.cyl("wt.cap", r * 0.12, 0.06, (0, -0.28, 0), red, root, rot=(math.pi / 2, 0, 0), n=10)
    W["wt"] = (hp, mp)


# shot id -> (x, y of the clock's centre as a fraction of the frame, its width as a fraction of the frame's)
REV_CLOCK = {"S08": (0.27, 0.40, 0.42), "S21a": (0.23, 0.375, 0.30), "S24": (0.25, 0.40, 0.40), "S25": (0.24, 0.40, 0.42)}
INDOOR_FROM = 0
OUTDOOR = ("S05a", "S05b", "S06a", "S06b")


def hexcol(h):
    h = h.lstrip("#")
    return tuple((int(h[i:i + 2], 16) / 255.0) ** 2.2 for i in (0, 2, 4))


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    sid = shot["id"]
    spec = next((s for s in story["shots"] if s["id"] == sid), None)
    outdoor = sid in OUTDOOR
    gains = {}
    sun = kit.LIGHTS["sun"]
    if outdoor:
        sun["obj"].location = Vector((28, -30, 22))
        sun["light"].color = (1.0, 0.95, 0.82)
        gains["sun"], gains["fill"] = 4.2, 1.5
        skyc, skys = "#9ad6ff", 1.0
        gains["lampA"] = gains["lampB"] = gains["lampC"] = 0.0
    else:
        gains["sun"], gains["fill"] = 0.0, 0.0
        skyc, skys = "#ffe9c0", 1.0
        gains["lampA"], gains["lampB"], gains["lampC"] = 150.0, 150.0, 90.0
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*hexcol(skyc), 1.0)
    bg.inputs["Strength"].default_value = skys
    # the follow lights: a key just left of the camera (faces always lit), a soft rim behind the subject
    if spec:
        c0 = spec["cam"][0]
        loc, tgt = Vector(c0[1]), Vector(c0[2])
        dist = max(1.0, (loc - tgt).length)
        base = (55.0 if outdoor else 30.0) * dist * dist
        right = Vector((tgt.y - loc.y, -(tgt.x - loc.x), 0))
        right = right.normalized() if right.length > 1e-4 else Vector((1, 0, 0))
        kl = kit.LIGHTS["key"]["obj"]
        kl.location = loc + Vector((0, 0, 0.4)) - right * 0.5
        rl = kit.LIGHTS["rimL"]["obj"]
        rl.location = tgt + (tgt - loc).normalized() * 1.5 + Vector((0, 0, 0.9))
        gains["key"], gains["rimL"] = base, base * 0.25
    else:
        gains["key"], gains["rimL"] = 0.0, 0.0
    # ---- the tag
    tm = sample("timer", tl, t, {"mode": 0.0, "s": 0.0, "big": 1.0})
    call = tm["mode"] > 0.5
    secs = int(round(tm["s"]))
    mm, ss_ = secs // 60, secs % 60
    big = int(round(tm["big"]))
    for k, ob in W["one"].items():
        ob.hide_render = call or k not in DIGIT_SEGS[big]
    for d, n in zip(W["digits"], (mm // 10, mm % 10, ss_ // 10, ss_ % 10)):
        for k, ob in d.items():
            ob.hide_render = (not call) or k not in DIGIT_SEGS[n]
    for ob in W["colon"]:
        ob.hide_render = not call
    ck = sample("clock", tl, t, {"on": 0.0, "h": 11.0, "m": 57.0})
    on = ck["on"] > 0.5
    hh, cm = int(round(ck["h"])), int(round(ck["m"]))
    for ob in [W["clockroot"]] + list(W["clockroot"].children_recursive):
        ob.hide_render = not on
    for d, n in zip(W["clockdigits"], (hh // 10, hh % 10, cm // 10, cm % 10)):
        for k, ob in d.items():
            ob.hide_render = (not on) or k not in DIGIT_SEGS[n]
    # ---- the clocks tell the same fast time; the big one sweeps a second hand
    hour_a = ((hh % 12) + cm / 60.0) * 30.0 * D2R
    min_a = cm * 6.0 * D2R
    for hp, mp, sp in W["clocks"]:
        hp.rotation_euler = (0, hour_a, 0)
        mp.rotation_euler = (0, min_a, 0)
        if sp is not None:
            sp.rotation_euler = (0, (0.0 if sid == "S21a" else (t * 36.0) % 360.0) * D2R, 0)
    # ---- the phone
    ph = sample("phone", tl, t, {"mode": 0.0, "buzz": 0.0})
    W["home"].hide_render = ph["mode"] > 0.5
    for ob in W["home"].children:
        ob.hide_render = ph["mode"] > 0.5
    W["call"].hide_render = ph["mode"] <= 0.5
    for ob in W["call"].children:
        ob.hide_render = ph["mode"] <= 0.5
    bz = ph["buzz"]
    px, py, pz = G.PHONE
    W["phone"].location = (px + 0.0016 * bz * math.sin(t * 38.0), py + 0.0013 * bz * math.sin(t * 31.0), pz)
    tp = sample("tap", tl, t, {"p": 0.0})["p"]
    fg = W["finger"]
    if tp < 0.02:
        fg.location = (0, -80, 0)
    else:
        u = ss(tp)
        fg.location = (px + 0.0 + 0.1 * (1 - u), py + 0.1 + 0.16 * (1 - u), pz + 0.02 + 0.08 * (1 - u))
        fg.rotation_euler = (-0.25 * (1 - u), 0, math.pi + 0.3)
    # ---- my watch tells the real time: ten minutes behind the wall clocks
    if W.get("wt"):
        real = (hh % 12) * 60 + cm - 10
        W["wt"][0].rotation_euler = (0, (real / 60.0) * 30.0 * D2R, 0)
        W["wt"][1].rotation_euler = (0, (real % 60) * 6.0 * D2R, 0)
    # ---- the ring cue on the phone
    for k, ob in enumerate(W["ring"].children):
        ob.hide_render = bz < 0.5
        sx = -1 if k < 3 else 1
        j = k % 3
        ob.location.x = sx * (0.068 + 0.026 * j + 0.004 * math.sin(t * 20.0 + j))
    # ---- the reveal clock, hung in the frame on its shots
    rc = W["revclock"]
    rv = REV_CLOCK.get(sid)
    if rv and spec:
        c0 = spec["cam"][0]
        loc, tgt, lens = Vector(c0[1]), Vector(c0[2]), c0[3]
        fwd = (tgt - loc).normalized()
        right = fwd.cross(Vector((0, 0, 1))).normalized()
        up = right.cross(fwd).normalized()
        D = 2.0
        wd = D * 13.5 / lens
        hd = wd * 16.0 / 9.0
        rc.location = loc + fwd * D + right * ((rv[0] - 0.5) * wd) + up * ((0.5 - rv[1]) * hd)
        rc.rotation_euler = (0, 0, math.atan2(-fwd.x, fwd.y))
        k = rv[2] * wd / 1.14
        rc.scale = (k, k, k)
    else:
        rc.location = (0, -80, 0)
    # ---- the close watch (S21a), hung in the frame like the reveal clock; the old arm watch is hidden there
    cw = W["closewatch"]
    for ob in bpy.data.objects:
        if ob.name.startswith("wt."):
            ob.hide_render = (sid == "S21a")
    if sid == "S21a" and spec:
        c0 = spec["cam"][0]
        loc, tgt, lens = Vector(c0[1]), Vector(c0[2]), c0[3]
        fwd = (tgt - loc).normalized()
        right = fwd.cross(Vector((0, 0, 1))).normalized()
        up = right.cross(fwd).normalized()
        D = 1.9
        wd = D * 13.5 / lens
        hd = wd * 16.0 / 9.0
        k = 0.26 * wd / 1.24
        cw.location = loc + fwd * D + right * ((0.23 - 0.5) * wd) + up * ((0.5 - 0.53) * hd)
        cw.rotation_euler = (0, 0, math.atan2(-fwd.x, fwd.y))
        cw.scale = (k, k, k)
    else:
        cw.location = (0, -80, 0)
    # ---- the hand-hold close (S14b): Mom's hand comes in from the left and settles on my cuff
    hi = W["handins"]
    if sid == "S14b":
        u = ss((t - shot["start"]) / 0.35)
        hi.location = (0.0, 1.5, G.TABLE_Z + 0.004)
        mg = W["hi.mom"]
        mg.location = (-0.12 * (1 - u), 0.0, 0.07 * (1 - u))
        mg.rotation_euler = (0, 0.2 * (1 - u), 0)
    else:
        hi.location = (0, -80, 0)
    # ---- seated
    for who in ("me", "mom"):
        sm = sample("sit", tl, t, {"s": 0.0}, who=who)["s"]
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg:
                leg.rotation_euler = (leg.rotation_euler.x * (1 - sm) + SIT * sm, 0, 0)
    return gains
