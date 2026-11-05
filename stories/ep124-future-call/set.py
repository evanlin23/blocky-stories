"""ep124 "future call": Dad's sunny two-car garage on a Saturday noon, a cream wall speakerphone, and three small
montage rooms far off along x (a rainy patio, a rowboat on a pond, a kitchen table).

Batch 13: ONE sun, never changed: nothing here blinks, pulses, glows or flickers. The phone has no lights. The rule
meter is a cream tag on the camera (top-left): a phone glyph and a big "1" until L10, then a call timer (MM:SS in
seven-segment digits) that steps on each line and stops at 09:12 at L38. Numerals and glyphs only.
Cues read by animate(): timer (mode, s), btn (p: the speaker button, 1 pressed), dsit (s: Dad sitting).
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


# ---------------------------------------------------------------------------------------------- the garage
def build_garage(kit):
    pl = kit.plastic
    wall = pl("#e4dccb", 0.9, spec=0.05)
    trim = pl("#c9bfa8", 0.8, spec=0.05)
    kit.box("garage.floor", (9.4, 8.2, 0.1), (0, 0.1, -0.05), kit.texture("concrete", 1.0, tint="#e0dcd2"))
    kit.box("garage.back", (9.6, 0.3, 3.3), (0, 4.15, 1.65), wall)
    kit.box("garage.westwall", (0.3, 8.2, 3.3), (-4.75, 0.1, 1.65), wall)
    kit.box("garage.eastwall", (0.3, 8.2, 3.3), (4.75, 0.1, 1.65), wall)
    # the front: two piers, a header, and the roll-up door rolled up under it
    for sx in (-1, 1):
        kit.box(f"garage.pier{sx}", (1.85, 0.3, 3.3), (sx * 3.7, -3.85, 1.65), wall)
    kit.box("garage.header", (5.7, 0.3, 0.85), (0, -3.85, 2.875), wall)
    kit.box("garage.doorroll", (5.5, 0.34, 0.3), (0, -3.7, 2.35), pl("#d8d2c4", 0.6))
    kit.box("garage.skirting", (9.2, 0.04, 0.12), (0, 3.98, 0.06), trim)
    # outside: lawn, drive, a tree and a bush
    kit.plane("lawn", (500, 500), (0, 0, -0.03), pl("#62c45a", 0.9, spec=0.05))
    kit.box("garage.drive", (5.8, 16.0, 0.06), (0, -12.0, -0.0), kit.texture("concrete", 1.0, tint="#f0ece4"))
    kit.prop("commontree_1", (-9.5, -13.0, 0), rot=20, height=6.5, tint="#d4f0c4")
    kit.prop("bush_1", (4.8, -9.0, 0), height=1.1, tint="#d4f0c4")
    kit.prop("bush_2", (-5.0, -7.0, 0), height=1.0, tint="#d4f0c4")


def build_pickup(kit):
    pl = kit.plastic
    red = pl("#d93a2f", 0.35, spec=0.5)
    dark = pl("#2a2a2e", 0.7)
    x, y0, y1 = G.TRUCK_X, G.TRUCK_Y0, G.TRUCK_Y1
    ym = (y0 + y1) / 2
    root = kit.empty("pickup", (x, 0, 0))
    kit.box("pickup.body", (1.9, y1 - y0, 0.55), (0, ym, 0.55), red, root, bevel=0.06)
    kit.box("pickup.hood", (1.8, 1.5, 0.16), (0, y1 - 0.85, 0.88), red, root, bevel=0.05)
    kit.box("pickup.cab", (1.78, 1.6, 0.78), (0, 0.55, 1.22), red, root, bevel=0.07)
    gl = pl("#9ed4f0", 0.12, spec=0.9)
    kit.box("pickup.windshield", (1.5, 0.05, 0.46), (0, 1.37, 1.27), gl, root)
    kit.box("pickup.rearwin", (1.3, 0.05, 0.36), (0, -0.27, 1.3), gl, root)
    for sx in (-1, 1):
        kit.box(f"pickup.sidewin{sx}", (0.05, 1.0, 0.4), (sx * 0.9, 0.62, 1.3), gl, root)
        kit.box(f"pickup.bedside{sx}", (0.08, 1.7, 0.36), (sx * 0.91, -1.1, 0.98), red, root)
        for yy in (-1.0, 2.0):
            kit.cyl(f"pickup.wheel{sx}{yy}", 0.37, 0.26, (sx * 0.97, yy, 0.37), dark, root, rot=(0, math.pi / 2, 0), n=14)
            kit.cyl(f"pickup.hub{sx}{yy}", 0.18, 0.28, (sx * 0.97, yy, 0.37), pl("#cfd2d6", 0.3, spec=0.8), root,
                    rot=(0, math.pi / 2, 0), n=10)
        kit.box(f"pickup.light{sx}", (0.3, 0.06, 0.16), (sx * 0.62, y1 + 0.02, 0.72), pl("#fff3c8", 0.3), root)
    kit.box("pickup.tailgate", (1.9, 0.08, 0.36), (0, y0 + 0.04, 0.98), red, root)
    kit.box("pickup.bumper", (2.0, 0.14, 0.18), (0, y1 + 0.08, 0.36), pl("#cfd2d6", 0.3, spec=0.8), root)
    kit.box("pickup.grille", (1.0, 0.06, 0.24), (0, y1 + 0.02, 0.72), dark, root)


def tool(kit, name, kind, x, z, root):
    """A tool on the pegboard: a painted silhouette (dark outline) with the tool itself 1 cm proud of it."""
    pl = kit.plastic
    sil = pl("#8a6a4a", 0.9, spec=0.02)
    metal = pl("#b8bcc2", 0.35, spec=0.8)
    wood = pl("#b5733a", 0.6)
    redh = pl("#d9483a", 0.5)
    y = -0.045   # in the pegboard's local frame, towards the room

    def b(nm, sz, loc, m, dy=0.0):
        return kit.box(f"{name}.{nm}", sz, (x + loc[0], y - dy, z + loc[1]), m, root)

    if kind == "hammer":
        b("s1", (0.085, 0.01, 0.4), (0, 0), sil)
        b("s2", (0.22, 0.01, 0.11), (0, 0.18), sil)
        b("h", (0.045, 0.01, 0.38), (0, 0), wood, 0.012)
        b("hd", (0.19, 0.01, 0.08), (0, 0.18), metal, 0.012)
    elif kind == "wrench":
        b("s1", (0.085, 0.01, 0.46), (0, 0), sil)
        b("s2", (0.16, 0.01, 0.16), (0, 0.2), sil)
        b("h", (0.04, 0.01, 0.44), (0, 0), metal, 0.012)
        b("hd", (0.12, 0.01, 0.12), (0, 0.2), metal, 0.012)
    elif kind == "saw":
        b("s1", (0.52, 0.01, 0.21), (0, 0), sil)
        b("bl", (0.46, 0.01, 0.14), (-0.03, -0.01), metal, 0.012)
        b("hd", (0.12, 0.01, 0.15), (0.2, 0.01), redh, 0.012)
    elif kind == "pliers":
        b("s1", (0.16, 0.01, 0.34), (0, 0), sil)
        b("a", (0.05, 0.01, 0.3), (-0.035, -0.02), redh, 0.012)
        b("c", (0.05, 0.01, 0.3), (0.035, -0.02), redh, 0.012)
        b("t", (0.1, 0.01, 0.1), (0, 0.13), metal, 0.012)
    elif kind == "driver":
        b("s1", (0.1, 0.01, 0.36), (0, 0), sil)
        b("h", (0.07, 0.01, 0.15), (0, -0.1), pl("#e8a030", 0.5), 0.012)
        b("t", (0.02, 0.01, 0.2), (0, 0.08), metal, 0.012)
    elif kind == "tape":
        b("s1", (0.2, 0.01, 0.2), (0, 0), sil)
        b("r", (0.16, 0.01, 0.16), (0, 0), pl("#f2c230", 0.5), 0.012)


def build_bench(kit):
    pl = kit.plastic
    bx, by = G.BENCH
    top = kit.planks("#d9a45b", "#c8934a", 2.0)
    kit.box("bench.top", (3.1, 0.8, 0.06), (bx, by, G.BENCH_Z - 0.03), top, bevel=0.01)
    leg = pl("#8a5a34", 0.7)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"bench.leg{sx}{sy}", (0.08, 0.08, 0.89), (bx + sx * 1.48, by + sy * 0.36, 0.445), leg)
    kit.box("bench.shelf", (3.0, 0.7, 0.04), (bx, by, 0.28), leg)
    kit.box("bench.apron", (3.0, 0.05, 0.12), (bx, by - 0.38, 0.8), leg)
    # the pegboard on the wall behind it
    root = kit.empty("pegboard", (1.8, 4.0, 1.85))
    kit.box("pegboard.panel", (3.4, 0.06, 1.3), (0, -0.03, 0), pl("#c8a07a", 0.85, spec=0.03), root)
    for k, (kind, px, pz) in enumerate([("hammer", -1.45, 0.25), ("wrench", -1.05, 0.2), ("saw", -0.5, 0.35),
                                        ("pliers", 0.05, 0.25), ("driver", 0.35, 0.28), ("driver", 0.58, 0.28),
                                        ("tape", 0.95, 0.35), ("wrench", 1.35, 0.2), ("hammer", 1.7, 0.25),
                                        ("saw", -0.95, -0.28), ("pliers", 0.0, -0.3), ("tape", 0.7, -0.28)]):
        tool(kit, f"peg{k}", kind, px, pz, root)
    # a toolbox with the two amber strokes scratched into its steel lid (1.5 cm proud), a coffee can of bolts
    tb = pl("#8c929a", 0.4, spec=0.6)
    kit.box("toolbox.body", (0.5, 0.26, 0.2), (1.38, 2.62, G.BENCH_Z + 0.1), tb, bevel=0.02)
    kit.box("toolbox.lid", (0.52, 0.28, 0.03), (1.38, 2.62, G.BENCH_Z + 0.215), tb, bevel=0.01)
    kit.box("toolbox.handle", (0.2, 0.03, 0.03), (1.38, 2.62, G.BENCH_Z + 0.26), pl("#3a3a3e", 0.5))
    amber = pl("#c8861c", 0.5)
    for k in range(2):
        kit.box(f"toolbox.stroke{k}", (0.025, 0.16, 0.015), (1.28 + k * 0.1, 2.62, G.BENCH_Z + 0.2375), amber)
    kit.cyl("coffeecan", 0.075, 0.16, (3.28, 2.4, G.BENCH_Z + 0.08), pl("#b8bcc2", 0.4, spec=0.7), n=14)
    kit.cyl("coffeecan.bolts", 0.065, 0.02, (3.28, 2.4, G.BENCH_Z + 0.165), pl("#6a5a48", 0.5), n=12)
    # the radio in pieces: a shell with no front, its dial, two knobs and its speaker, set apart
    wd = pl("#8a5a34", 0.6)
    rx, ry, rz = 2.25, 2.6, G.BENCH_Z
    kit.box("radio.back", (0.46, 0.04, 0.28), (rx, ry + 0.12, rz + 0.14), wd)
    kit.box("radio.top", (0.46, 0.22, 0.04), (rx, ry, rz + 0.3), wd)
    for sx in (-1, 1):
        kit.box(f"radio.side{sx}", (0.04, 0.22, 0.28), (rx + sx * 0.21, ry, rz + 0.14), wd)
    kit.cyl("radio.speaker", 0.1, 0.03, (rx + 0.55, ry - 0.1, rz + 0.015), pl("#4a4a50", 0.6), n=14)
    kit.box("radio.dial", (0.22, 0.03, 0.1), (rx + 0.28, ry + 0.14, rz + 0.05), pl("#e8dcc0", 0.5))
    for k in range(2):
        kit.cyl(f"radio.knob{k}", 0.03, 0.03, (rx - 0.25 - k * 0.1, ry - 0.2, rz + 0.015), pl("#e8dcc0", 0.5), n=10)
    # a plain frosted cake, no candles and no numerals
    kit.cyl("cake.plate", 0.27, 0.015, (3.0, 2.7, rz + 0.008), pl("#f4f4f2", 0.4), n=20)
    kit.cyl("cake.base", 0.2, 0.11, (3.0, 2.7, rz + 0.07), pl("#f2a0b8", 0.6), n=20)
    kit.cyl("cake.top", 0.19, 0.08, (3.0, 2.7, rz + 0.165), pl("#fff1d8", 0.6), n=20)
    for k in range(8):
        a = k * math.pi / 4
        kit.sphere(f"cake.dot{k}", 0.026, (3.0 + 0.16 * math.cos(a), 2.7 + 0.16 * math.sin(a), rz + 0.215),
                   pl("#f2a0b8", 0.5), seg=8)
    # the soup can and the rubber chicken at the west end (the jokes)
    kit.cyl("soup", 0.045, 0.11, (0.82, 2.55, rz + 0.055), pl("#d93a2f", 0.5), n=12)
    kit.cyl("soup.band", 0.047, 0.04, (0.82, 2.55, rz + 0.06), pl("#f4f4f2", 0.5), n=12)
    ch = pl("#f2d230", 0.5)
    kit.box("chicken.body", (0.17, 0.12, 0.12), (0.47, 2.6, rz + 0.07), ch, bevel=0.03)
    kit.box("chicken.head", (0.07, 0.07, 0.07), (0.47, 2.52, rz + 0.17), ch, bevel=0.02)
    kit.box("chicken.beak", (0.04, 0.05, 0.025), (0.47, 2.47, rz + 0.17), pl("#e8802a", 0.5))
    kit.box("chicken.comb", (0.025, 0.05, 0.03), (0.47, 2.52, rz + 0.225), pl("#d93a2f", 0.5))
    # two tires, stacked, by the bench's end; a low stool behind Dad
    tire = pl("#2a2a2e", 0.8, spec=0.1)
    for k in range(2):
        kit.cyl(f"tires.{k}", 0.31, 0.2, (2.4, 3.55, 0.1 + 0.2 * k), tire, n=18)
        kit.cyl(f"tires.hub{k}", 0.15, 0.205, (2.4, 3.55, 0.1 + 0.2 * k), pl("#a8acb2", 0.4, spec=0.6), n=12)
    kit.box("stool", (0.5, 0.5, 0.34), (G.DAD[0], G.DAD[1] + 0.1, 0.17), pl("#8a5a34", 0.7))


def build_shelves(kit):
    pl = kit.plastic
    wood = pl("#a6764a", 0.7)
    cols = ["#d9483a", "#4a8ad9", "#f2c230", "#5ab060", "#e8803a"]
    for k, z in enumerate((0.4, 1.15, 1.9)):
        kit.box(f"shelf.board{k}", (0.45, 3.2, 0.05), (4.4, 1.5, z), wood)
    for sy in (-0.1, 3.1):
        kit.box(f"shelf.post{sy}", (0.45, 0.05, 1.95), (4.4, sy, 0.98), wood)
    for k in range(9):
        z = (0.4, 1.15, 1.9)[k % 3]
        kit.box(f"shelf.box{k}", (0.3, 0.3 + 0.06 * (k % 3), 0.28), (4.4, 0.2 + 0.32 * k, z + 0.165), pl(cols[k % 5], 0.6), bevel=0.02)
    # the old radio on the top shelf (off)
    kit.box("shelf.radio", (0.22, 0.5, 0.3), (4.38, 2.8, 2.07), pl("#b07a3a", 0.55))
    kit.box("shelf.radiodial", (0.02, 0.28, 0.12), (4.26, 2.8, 2.1), pl("#e8dcc0", 0.5))


# ---------------------------------------------------------------------------------------------- the wall phone
def build_phone(kit):
    pl = kit.plastic
    px, py, pz = G.PHONE
    kit.box("phone.board", (0.56, 0.05, 0.78), (px, 3.975, pz), pl("#6a4a32", 0.7))
    root = kit.empty("phone", (px, 3.95 - 0.07, pz))
    W["phone"] = root
    cream = pl("#f2e6c8", 0.45, spec=0.3)
    kit.box("phone.body", (0.36, 0.14, 0.58), (0, 0, 0), cream, root, bevel=0.03)
    fy = -0.075
    kit.cyl("phone.grille", 0.095, 0.02, (0, fy, 0.14), pl("#4a3c2c", 0.7), root, rot=(math.pi / 2, 0, 0), n=18)
    for k in range(3):
        kit.box(f"phone.slit{k}", (0.14, 0.012, 0.014), (0, fy - 0.012, 0.1 + 0.04 * k), cream, root)
    W["btn"] = kit.box("phone.button", (0.08, 0.05, 0.08), (0, fy - 0.01, -0.02), pl("#e8913a", 0.5), root, bevel=0.01)
    for r in range(3):
        for c in range(3):
            kit.box(f"phone.key{r}{c}", (0.06, 0.02, 0.05), ((c - 1) * 0.09, fy + 0.0, -0.12 - r * 0.07),
                    pl("#c9b896", 0.6), root, bevel=0.008)


# ---------------------------------------------------------------------------------------------- the montage rooms
def chair(kit, name, x, y, pl):
    wood = pl("#a6764a", 0.7)
    kit.box(f"{name}.seat", (0.5, 0.5, 0.06), (x, y, 0.62), wood)
    kit.box(f"{name}.back", (0.5, 0.05, 0.5), (x, y + 0.27, 0.9), wood)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"{name}.leg{sx}{sy}", (0.05, 0.05, 0.6), (x + sx * 0.22, y + sy * 0.22, 0.3), wood)


def build_patio(kit):
    pl = kit.plastic
    mx, my = G.MOM_ROOM
    kit.box("patio.slab", (8, 5.5, 0.08), (mx, my + 0.6, 0.04), pl("#d8d2c6", 0.8, spec=0.05))
    kit.box("patio.house", (8, 0.3, 3.4), (mx, my + 3.3, 1.7), pl("#bcd4ec", 0.85, spec=0.05))
    kit.box("patio.door", (1.2, 0.1, 2.3), (mx - 2.0, my + 3.12, 1.2), pl("#fff7e6", 0.6))
    kit.box("patio.window", (1.8, 0.1, 1.3), (mx + 1.8, my + 3.12, 1.6), pl("#8fc9e8", 0.2, spec=0.7))
    kit.box("patio.windowframe", (2.0, 0.08, 1.5), (mx + 1.8, my + 3.1, 1.6), pl("#fff7e6", 0.6))
    ty = my + 0.35
    kit.cyl("patio.table", 0.78, 0.05, (mx, ty, 0.73), pl("#fff7e6", 0.45), n=22)
    kit.cyl("patio.tableleg", 0.06, 0.7, (mx, ty, 0.35), pl("#8a8e96", 0.5), n=8)
    chair(kit, "patio.chair", mx, my + 1.25, pl)
    kit.cyl("umbrella.pole", 0.03, 2.5, (mx + 0.6, ty, 1.25), pl("#cfd2d6", 0.4, spec=0.7), n=8)
    kit.cyl("umbrella.canopy", 1.75, 0.5, (mx + 0.6, ty, 2.45), kit.emit("#e02a22", 1.0, "umbrellared"), n=14, r2=0.08)
    kit.cyl("umbrella.rim", 1.77, 0.07, (mx + 0.6, ty, 2.2), kit.emit("#b3231c", 1.0, "umbrellarim"), n=14)
    for k, (dx, dy) in enumerate([(-1.9, 0.0), (2.0, 0.6), (-0.9, 2.0), (1.1, 2.1)]):
        kit.cyl(f"patio.puddle{k}", 0.38, 0.01, (mx + dx, my + dy, 0.09), pl("#6ab4e8", 0.1, spec=0.9), n=16)
    for k in range(2):
        kit.prop("bush_1", (mx - 3.4 + 6.8 * k, my + 2.6, 0), height=1.2, tint="#d4f0c4")


def build_pond(kit):
    pl = kit.plastic
    ux, uy = G.UNCLE_ROOM
    kit.box("pond.water", (16, 14, 0.05), (ux, uy + 2.0, 0.02), pl("#4fa8e0", 0.15, spec=0.7))
    kit.box("pond.bank", (16, 2.0, 0.3), (ux, uy + 9.0, 0.1), pl("#62c45a", 0.9, spec=0.05))
    kit.prop("willow_1", (ux - 4.5, uy + 8.0, 0), height=6.0, tint="#d4f0c4")
    kit.prop("bush_1", (ux + 4.0, uy + 8.0, 0), height=1.3, tint="#d4f0c4")
    kit.prop("rock_1", (ux + 3.0, uy + 6.0, 0), height=0.7)
    # the little green rowboat: floor, four sides, a bow, a thwart for him to sit on
    g = pl("#3aa860", 0.45, spec=0.3)
    inner = pl("#d9b98a", 0.7)
    kit.box("boat.floor", (2.8, 1.1, 0.06), (ux, uy + 0.15, 0.1), inner)
    for sy in (-1, 1):
        kit.box(f"boat.side{sy}", (2.9, 0.08, 0.36), (ux, uy + 0.15 + sy * 0.55, 0.27), g, bevel=0.02)
    for sx in (-1, 1):
        kit.box(f"boat.end{sx}", (0.08, 1.1, 0.36), (ux + sx * 1.42, uy + 0.15, 0.27), g, bevel=0.02)
    kit.box("boat.thwart", (0.32, 1.1, 0.05), (ux, uy + 0.15, 0.47), g)
    kit.box("boat.water", (0.9, 0.7, 0.012), (ux - 1.0, uy + 0.15, 0.135), pl("#4fa8e0", 0.1, spec=0.9))
    kit.cyl("boat.cup", 0.06, 0.1, (ux - 0.6, uy - 0.05, 0.19), pl("#f2c230", 0.5), n=12)
    kit.box("boat.oar", (2.0, 0.06, 0.03), (ux + 0.2, uy + 0.65, 0.42), pl("#b5733a", 0.6))


def build_kitchen(kit):
    pl = kit.plastic
    kx, ky = G.KITCHEN
    kit.box("kitchen.floor", (8, 6, 0.08), (kx, ky + 0.8, 0.04), pl("#e0c89a", 0.7, spec=0.1))
    kit.box("kitchen.wall", (8, 0.3, 3.2), (kx, ky + 3.6, 1.6), pl("#f6e2a8", 0.85, spec=0.05))
    kit.box("kitchen.windowframe", (2.0, 0.08, 1.5), (kx + 0.0, ky + 3.42, 1.8), pl("#fff7e6", 0.6))
    kit.box("kitchen.window", (1.7, 0.1, 1.2), (kx, ky + 3.4, 1.8), pl("#8fd0ff", 0.2, spec=0.5))
    for sx in (-1, 1):
        kit.box(f"kitchen.cabinet{sx}", (1.9, 0.6, 1.0), (kx + sx * 2.8, ky + 3.2, 0.5), pl("#e8803a", 0.6))
        kit.box(f"kitchen.counter{sx}", (2.0, 0.65, 0.06), (kx + sx * 2.8, ky + 3.2, 1.03), pl("#f4f4f2", 0.5))
    kit.box("kitchen.table", (1.9, 0.95, 0.06), (kx, ky + 0.4, 0.73), pl("#d9a45b", 0.5))
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"kitchen.tleg{sx}{sy}", (0.06, 0.06, 0.7), (kx + sx * 0.88, ky + 0.4 + sy * 0.42, 0.35), pl("#8a5a34", 0.7))
    kit.cyl("kitchen.mug1", 0.055, 0.1, (kx - 0.3, ky + 0.35, 0.81), pl("#4a8ad9", 0.5), n=12)
    kit.cyl("kitchen.mug2", 0.055, 0.1, (kx + 0.4, ky + 0.45, 0.81), pl("#d9483a", 0.5), n=12)
    kit.cyl("kitchen.plate", 0.16, 0.015, (kx, ky + 0.3, 0.77), pl("#f4f4f2", 0.4), n=16)
    chair(kit, "kitchen.chair1", kx - 0.6, ky + 1.2, pl)
    chair(kit, "kitchen.chair2", kx + 0.6, ky + 1.2, pl)


# ---------------------------------------------------------------------------------------------- the rule meter
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
    # a wall-phone glyph (the same phone as on the wall): a teal body, a cream round grille, six cream keys
    cream = kit.emit("#f2e6c8", 0.85, "tagcream")
    g = kit.empty("tag.glyph", (-0.5, 0.0, z), root)
    b("tag.g.body", (0.3, 0.46, 0.006), (0, 0, 0), teal, g)
    gr = kit.cyl("tag.g.grille", 0.075, 0.006, (0, 0.12, 0.007), cream, g, n=14)
    noshadow(gr)
    for r in range(3):
        for c in range(2):
            b(f"tag.g.k{r}{c}", (0.075, 0.05, 0.006), ((c - 0.5) * 0.11, -0.03 - r * 0.075, 0.007), cream, g)

    def seven(prefix, cx, cy, dw, dh, t):
        pos = {"a": (0, dh / 2 - t / 2, dw, t), "g": (0, 0, dw, t), "d": (0, -dh / 2 + t / 2, dw, t),
               "f": (-dw / 2 + t / 2, dh / 4, t, dh / 2), "b": (dw / 2 - t / 2, dh / 4, t, dh / 2),
               "e": (-dw / 2 + t / 2, -dh / 4, t, dh / 2), "c": (dw / 2 - t / 2, -dh / 4, t, dh / 2)}
        return {k: b(f"{prefix}{k}", (sw, sh, 0.006), (cx + px, cy + py, z), ink) for k, (px, py, sw, sh) in pos.items()}

    # the big "1" (mode 0) and the MM:SS timer (mode 1)
    W["one"] = seven("tag.one", 0.3, 0.0, 0.2, 0.46, 0.07)
    for k, ob in W["one"].items():
        ob.hide_render = k not in DIGIT_SEGS[1]
    W["digits"] = [seven(f"tag.d{i}", cx, 0.0, 0.1, 0.34, 0.036) for i, cx in enumerate((-0.12, 0.04, 0.3, 0.46))]
    W["colon"] = [b("tag.c1", (0.036, 0.036, 0.006), (0.17, 0.07, z), ink), b("tag.c2", (0.036, 0.036, 0.006), (0.17, -0.07, z), ink)]


def _digit(d, n):
    segs = DIGIT_SEGS.get(n, "")
    for k, ob in d.items():
        ob.hide_render = k not in segs


# ---------------------------------------------------------------------------------------------- build / animate
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    # ONE sun, constant: noon, a little from the south so faces on the garage's open side are lit
    sun = kit.light("sun", "SUN", (18, -27, 51), 1.0, "#fff1d6", size=0.06)
    sun.data.angle = 0.05
    kit.aim(sun, (0, 0, 0))
    fill = kit.light("fill", "SUN", (0, -10, 30), 1.0, "#e8f0ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    build_garage(kit)
    build_pickup(kit)
    build_bench(kit)
    build_shelves(kit)
    build_phone(kit)
    build_patio(kit)
    build_pond(kit)
    build_kitchen(kit)
    build_tag(kit)
    return {}


def _first_frame(kit, story):
    gh = bpy.data.objects.get("dad.headg")
    if gh is not None:
        kit.box("dad.stache", (0.5, 0.08, 0.1), (0, -0.62, -0.2), kit.plastic("#8f8f8f", 0.8), gh, bevel=0.03)
    W["inited"] = True


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    gains = {"sun": 4.2, "fill": 1.2}
    # the tag: "1" until the call, then the timer
    tm = sample("timer", tl, t, {"mode": 0.0, "s": 0.0})
    secs = int(round(tm["s"]))
    mm, ss_ = secs // 60, secs % 60
    call = tm["mode"] > 0.5
    for k, ob in W["one"].items():
        ob.hide_render = call or k not in DIGIT_SEGS[1]
    for d, n in zip(W["digits"], (mm // 10, mm % 10, ss_ // 10, ss_ % 10)):
        for k, ob in d.items():
            ob.hide_render = (not call) or k not in DIGIT_SEGS[n]
    for ob in W["colon"]:
        ob.hide_render = not call
    # the camera-hung tag's place, from this shot's lens
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next((s for s in story["shots"] if s["id"] == shot["id"]), None)
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
    s = 0.46 * w2
    tag = W["tag"]
    tag.scale = (s, s, s)
    tag.location = (-0.5 * w2, 0.62 * h2, -dist)
    # the speaker button: out (0), pressed in (1), flush with the face of the phone
    bt = sample("btn", tl, t, {"p": 0.0})["p"]
    W["btn"].location.y = -0.085 + 0.03 * bt
    # seated: Mom, the uncle, the friend and his sister always; Dad on his stool when he drops
    for who in ("mom", "uncle", "friend", "sister"):
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg:
                leg.rotation_euler = (SIT, 0, 0)
    ds = sample("dsit", tl, t, {"s": 0.0})["s"]
    if ds > 0.001:
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"dad.leg{sx}")
            if leg:
                leg.rotation_euler = (leg.rotation_euler.x * (1 - ds) + SIT * ds, 0, 0)
    return gains
