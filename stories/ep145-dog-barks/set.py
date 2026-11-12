"""ep145 "our dog barked once, then twice": our sunny backyard on a Sunday. A green lawn, a white picket fence round
three sides with the side gate in the south one, a red brick patio, a kettle grill, a long picnic table under a gingham
cloth, bunting in plain colours, and the back of our yellow house with its kitchen window (a lit kitchen behind it, so
the camera never looks into an unlit volume) and a back door. Mr. Hale's house is over the west fence.

Moose, our dog, is built here from kit parts (a stocky tan pet with one white ear), and moved by the `moose` cue track.
Everything else the story moves is a cue (see animate): the bark badge (world copy over Moose's head, or the camera's
corner copy), the gate, the back door, the ring box, the carrot toy, the biscuit, the clipboard, the spatula, the napkin
under the table leg and the table's rocking. Nothing here glows, pulses or flickers; one sun, fixed.
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
SEG = {"1": "", "2": "abged"}


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
            return {k: (prev[k] + (cur[k] - prev[k]) * u if isinstance(cur[k], (int, float)) and not isinstance(cur[k], bool)
                        else cur[k]) for k in cur}
    return cur


def hide(ob, h):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


def noshadow(ob):
    ob.visible_shadow = False
    return ob


# ---------------------------------------------------------------------------------------------- the yard
def build_ground(kit):
    pl = kit.plastic
    kit.box("lawn", (80, 70, 0.2), (0, 6, -0.1), kit.texture("grass", 1.5, tint="#a6f08c"))
    # the patio: red brick, 6 cm proud of the lawn
    kit.box("patio", (9.6, 4.2, 0.06), (0.4, 4.9, 0.03), kit.bricks("#c75b3f", "#b84e36", "#9a9088", 1.0, grime_amt=0.2))
    # a stepping-stone path from the gate to the patio
    stone = pl("#d8d2c4", 0.8, spec=0.05)
    for k in range(5):
        kit.box(f"step{k}", (0.9, 0.55, 0.04), (-1.5 + 0.12 * (k % 2), -1.6 + k * 0.95, 0.02), stone, bevel=0.02)


def build_fence(kit):
    white = kit.plastic("#fbfbf6", 0.5, spec=0.1)
    rail = kit.plastic("#eceae0", 0.55, spec=0.08)
    gx0, gx1 = G.GATE[0] - G.GATE_W / 2, G.GATE[0] + G.GATE_W / 2

    def run_x(name, x0, x1, y):
        n = max(1, int(round((x1 - x0) / 0.2)))
        for i in range(n):
            kit.box(f"{name}.p{i}", (0.11, 0.04, 1.1), (x0 + (i + 0.5) * (x1 - x0) / n, y, 0.55), white, bevel=0.01)
        for z in (0.3, 0.8):
            kit.box(f"{name}.r{z}", (x1 - x0, 0.05, 0.08), (x0 + (x1 - x0) / 2, y + 0.04, z), rail)

    def run_y(name, y0, y1, x):
        n = max(1, int(round((y1 - y0) / 0.2)))
        for i in range(n):
            kit.box(f"{name}.p{i}", (0.04, 0.11, 1.1), (x, y0 + (i + 0.5) * (y1 - y0) / n, 0.55), white, bevel=0.01)
        for z in (0.3, 0.8):
            kit.box(f"{name}.r{z}", (0.05, y1 - y0, 0.08), (x + 0.04, y0 + (y1 - y0) / 2, z), rail)

    run_x("fs.w", G.FX0, gx0, G.FY0)
    run_x("fs.e", gx1, G.FX1, G.FY0)
    run_y("fw", G.FY0, G.HOUSE_Y, G.FX0)
    run_y("fe", G.FY0, G.HOUSE_Y, G.FX1)
    # two gate posts
    for sx in (gx0, gx1):
        kit.box(f"gpost{sx}", (0.14, 0.14, 1.3), (sx, G.FY0, 0.65), white, bevel=0.02)
    # the gate leaf, hinged at its east end; animate swings it inward (north)
    hinge = kit.empty("gate", (gx1 - 0.08, G.FY0, 0.0))
    W["gate"] = hinge
    gw = G.GATE_W - 0.16
    n = 8
    for i in range(n):
        kit.box(f"gate.p{i}", (0.11, 0.04, 1.0), (-0.05 - (i + 0.5) * gw / n, 0, 0.55), white, hinge, bevel=0.01)
    for z in (0.3, 0.8):
        kit.box(f"gate.r{z}", (gw, 0.05, 0.08), (-0.05 - gw / 2, 0.04, z), rail, hinge)
    kit.box("gate.brace", (gw * 0.9, 0.04, 0.07), (-0.05 - gw / 2, -0.03, 0.55), rail, hinge, rot=(0, 0.5, 0))
    # a latch block on the gate post
    kit.box("gate.latch", (0.06, 0.1, 0.1), (gx0 + 0.05, G.FY0 + 0.03, 0.9), kit.plastic("#3a3a40", 0.4))


def build_house(kit):
    pl = kit.plastic
    yel = pl("#ffd56b", 0.7, spec=0.05)
    trim = pl("#fbfbf6", 0.6, spec=0.08)
    x0, x1 = G.FX0, G.FX1
    y0, y1 = G.HOUSE_Y, G.HOUSE_Y + 0.4
    yc = (y0 + y1) / 2
    wx0, wx1 = G.WIN[0] - 1.2, G.WIN[0] + 1.2
    sill, head = G.WIN[1], G.WIN[2]
    dx0, dx1 = G.DOOR_X - 0.55, G.DOOR_X + 0.55
    H = 3.3

    def wall(name, ax, bx, az, bz):
        kit.box(name, (bx - ax, y1 - y0, bz - az), ((ax + bx) / 2, yc, (az + bz) / 2), yel)

    wall("w.left", x0, dx0, 0, H)
    wall("w.mid", dx1, wx0, 0, H)
    wall("w.right", wx1, x1, 0, H)
    wall("w.doorhead", dx0, dx1, 2.15, H)
    wall("w.under", wx0, wx1, 0, sill)
    wall("w.over", wx0, wx1, head, H)
    # white window frame and a deep sill, standing proud of the wall
    yf = y0 - 0.03
    kit.box("win.sill", ((wx1 - wx0) + 0.3, 0.3, 0.07), ((wx0 + wx1) / 2, y0 - 0.1, sill - 0.035), trim, bevel=0.015)
    kit.box("win.top", ((wx1 - wx0) + 0.2, 0.06, 0.1), ((wx0 + wx1) / 2, yf, head + 0.05), trim)
    for sx in (wx0 - 0.05, wx1 + 0.05):
        kit.box(f"win.side{sx}", (0.1, 0.06, head - sill + 0.1), (sx, yf, (sill + head) / 2), trim)
    # the door frame (a white surround) and the door leaf, hinged on its east edge, swung in by animate
    kit.box("door.top", (1.3, 0.06, 0.12), (G.DOOR_X, yf, 2.2), trim)
    for sx in (dx0 - 0.08, dx1 + 0.08):
        kit.box(f"door.side{sx}", (0.12, 0.06, 2.2), (sx, yf, 1.1), trim)
    kit.box("door.step", (1.4, 0.7, 0.12), (G.DOOR_X, y0 - 0.35, 0.06), pl("#d8d2c4", 0.8))
    hinge = kit.empty("backdoor", (dx1, y0 + 0.05, 0.0))
    kit.box("backdoor.leaf", (1.0, 0.06, 2.1), (-0.5, 0, 1.05), pl("#4a8fd8", 0.5, spec=0.15), hinge, bevel=0.02)
    kit.box("backdoor.knob", (0.07, 0.07, 0.07), (-0.88, -0.06, 1.0), pl("#e8c24a", 0.3, spec=0.6), hinge)
    W["backdoor"] = hinge
    # eaves and roof
    roof = pl("#9a4a3a", 0.7, spec=0.05)
    kit.box("eave", (x1 - x0 + 0.6, 0.2, 0.2), ((x0 + x1) / 2, y0 - 0.45, H + 0.1), trim)
    for sy, z, rx in ((1, 4.55, -0.55), (-1, 4.55, 0.55)):
        kit.box(f"roof{sy}", (x1 - x0 + 0.8, 3.6, 0.2), ((x0 + x1) / 2, y0 + 1.1 + (-1.6 if sy == 1 else 2.2), z), roof,
                rot=(rx, 0, 0), bevel=0.03)
    # kitchen behind the wall: floor, ceiling with a lit panel, back wall, side walls, counters, fridge
    cream = pl("#f6ecd6", 0.8, spec=0.03)
    ceil = pl("#fffaf0", 0.9, spec=0.02)
    floor = pl("#d9b27c", 0.6, spec=0.1)
    kit.box("k.floor", (x1 - x0, 3.4, 0.1), ((x0 + x1) / 2, y1 + 1.7, -0.03), floor)
    kit.box("k.ceiling", (x1 - x0, 3.4, 0.2), ((x0 + x1) / 2, y1 + 1.7, H + 0.1), ceil)
    kit.box("k.back", (x1 - x0, 0.2, H), ((x0 + x1) / 2, y1 + 3.5, H / 2), cream)
    for sx, nm in ((x0 - 0.1, "l"), (x1 + 0.1, "r")):
        kit.box(f"k.side{nm}", (0.2, 3.6, H), (sx, y1 + 1.7, H / 2), cream)
    cab = pl("#5a8ac8", 0.55, spec=0.1)
    top = pl("#f4f4ee", 0.4, spec=0.2)
    kit.box("k.cab", (4.2, 0.7, 0.9), (G.WIN[0], y1 + 2.9, 0.45), cab, bevel=0.02)
    kit.box("k.counter", (4.3, 0.8, 0.06), (G.WIN[0], y1 + 2.9, 0.93), top)
    kit.box("k.upper", (3.0, 0.4, 0.8), (G.WIN[0] + 0.4, y1 + 3.2, 2.1), cab, bevel=0.02)
    kit.box("k.fridge", (0.9, 0.8, 1.9), (G.WIN[0] - 2.8, y1 + 2.9, 0.95), pl("#e6eaee", 0.35, spec=0.3), bevel=0.04)
    em = kit.emit("#fff3dc", 3.0)
    kit.box("k.panel", (1.8, 1.0, 0.03), (G.WIN[0], y1 + 1.6, H - 0.02), em)
    lt = kit.light("kitchen", "AREA", (G.WIN[0], y1 + 1.6, H - 0.3), 260, "#fff0d6", size=3.0, shadow=False)
    kit.aim(lt, (G.WIN[0], y1 + 1.6, 0.0))


def build_neighbour(kit):
    pl = kit.plastic
    wall = pl("#b9d6ee", 0.7, spec=0.05)
    trim = pl("#fbfbf6", 0.6, spec=0.08)
    roof = pl("#5a5f78", 0.7, spec=0.05)
    gut = pl("#9aa0a8", 0.4, spec=0.35)
    xe = G.HALE_HOUSE_X
    kit.box("h.wall", (6.0, 12.0, 3.4), (xe - 3.0, 3.0, 1.7), wall)
    # a window and a door on the east face, white frames
    for yy in (0.2, 5.6):
        kit.box(f"h.win{yy}", (0.06, 1.3, 1.2), (xe + 0.03, yy, 1.7), pl("#8fd3ff", 0.2, spec=0.3))
        kit.box(f"h.winf{yy}", (0.08, 1.5, 1.4), (xe + 0.02, yy, 1.7), trim)
    kit.box("h.door", (0.06, 1.0, 2.1), (xe + 0.03, 3.0, 1.05), pl("#c75b3f", 0.6))
    # fascia under the roof edge, and a roof
    kit.box("h.fascia", (0.12, 12.2, 0.3), (xe + 0.08, 3.0, 3.35), trim)
    kit.box("h.roofE", (2.4, 12.4, 0.2), (xe - 1.0, 3.0, 4.1), roof, rot=(0, 0.5, 0), bevel=0.03)
    # the gutter along the eave, with a clean gap (pale board, two brackets) where it used to be
    gap0, gap1 = 1.2, 4.2
    for name, a, b in (("h.gut.s", -3.0, gap0), ("h.gut.n", gap1, 9.0)):
        kit.box(name, (0.16, b - a, 0.14), (xe + 0.17, (a + b) / 2, 3.12), gut, bevel=0.03)
    kit.box("h.clean", (0.05, gap1 - gap0, 0.3), (xe + 0.16, (gap0 + gap1) / 2, 3.3), pl("#ffffff", 0.5))
    for yy in (gap0 + 0.15, gap1 - 0.15):
        kit.box(f"h.bracket{yy}", (0.2, 0.05, 0.05), (xe + 0.2, yy, 3.1), gut)
    # his lawn bush and a flower bed
    kit.sphere("h.bush1", 0.6, (xe + 1.0, -1.2, 0.5), pl("#3f9a4a", 0.8), seg=10)
    kit.sphere("h.bush2", 0.5, (xe + 1.0, 7.5, 0.4), pl("#3f9a4a", 0.8), seg=10)


def build_trees(kit):
    for nm, loc, h in (("commontree_1", (11.5, 3.0, 0), 7.0), ("commontree_2", (11.0, 9.0, 0), 6.5),
                       ("commontree_1", (-1.0, -7.0, 0), 6.5), ("commontree_2", (6.0, -6.5, 0), 6.0),
                       ("commontree_2", (-13.0, -4.0, 0), 6.5), ("commontree_1", (-20.0, 6.0, 0), 7.0)):
        try:
            kit.prop(nm, loc, rot=hash(loc) % 360, height=h)
        except Exception:
            pass
    pl = kit.plastic
    for k, (x, y) in enumerate(((-6.0, 0.4), (-6.1, 4.2), (7.9, 1.0), (7.9, 5.0), (5.5, -1.9), (-5.2, -1.9))):
        kit.sphere(f"bush{k}", 0.55, (x, y, 0.45), pl("#3fa84e", 0.8), seg=10)


def build_grill(kit):
    pl = kit.plastic
    gx, gy = G.GRILL
    red = pl("#d83a2a", 0.35, spec=0.4)
    blk = pl("#2a2a30", 0.5, spec=0.3)
    kit.sphere("grill.bowl", 0.42, (gx, gy, 0.82), red, seg=20).scale = (1.0, 1.0, 0.6)
    kit.cyl("grill.rim", 0.43, 0.05, (gx, gy, 1.07), blk, n=24)
    kit.cyl("grill.coal", 0.36, 0.03, (gx, gy, 1.06), pl("#3a3430", 0.9), n=24)
    kit.cyl("grill.grate", 0.4, 0.025, (gx, gy, 1.11), pl("#7a7e86", 0.4, spec=0.5), n=24)
    for k in range(3):                       # three patties
        a = k * 2.1 + 0.4
        kit.cyl(f"patty{k}", 0.1, 0.04, (gx + 0.2 * math.cos(a), gy + 0.2 * math.sin(a), 1.145), pl("#6a3f26", 0.7), n=12)
    for k in range(3):
        a = k * 2.094 + 0.6
        kit.box(f"grill.leg{k}", (0.05, 0.05, 0.62), (gx + 0.3 * math.cos(a), gy + 0.3 * math.sin(a), 0.31), blk,
                rot=(0, 0, 0))
    # the lid, hung open on the back of the bowl
    kit.sphere("grill.lid", 0.44, (gx, gy + 0.55, 0.95), red, seg=18).scale = (1.0, 0.25, 0.8)
    kit.box("grill.handle", (0.3, 0.04, 0.04), (gx, gy + 0.45, 1.38), blk)
    # smoke: soft grey puffs drifting up from the coals (placed by animate)
    W["smoke"] = [kit.sphere(f"smoke{k}", 0.16, (gx, gy, 1.3), pl("#e6e6ea", 0.9), seg=8) for k in range(4)]
    for s in W["smoke"]:
        s.visible_shadow = False
    # the spatula (hand-held by cue)
    sp = kit.empty("spatula", (0, 0, -20))
    kit.box("spat.handle", (0.035, 0.035, 0.34), (0, 0, 0.0), pl("#5a3b22", 0.6), sp)
    kit.box("spat.blade", (0.12, 0.02, 0.14), (0, 0, 0.2), pl("#9aa0a8", 0.35, spec=0.5), sp)
    W["spat"] = sp


def build_table(kit):
    pl = kit.plastic
    tx, ty = G.TABLE
    wood = pl("#d9a066", 0.7, spec=0.05)
    dark = pl("#b87e46", 0.7, spec=0.05)
    root = kit.empty("table", (tx, ty, 0.0))
    W["table"] = root
    kit.box("table.top", (2.5, 0.9, 0.07), (0, 0, 0.76), wood, root, bevel=0.015)
    cloth = kit.checker("#ee6a55", "#ffffff", 4.0, name="gingham")
    kit.box("table.cloth", (2.56, 0.96, 0.02), (0, 0, 0.805), cloth, root)
    for sx in (-1.0, 1.0):
        for sy in (-0.3, 0.3):
            kit.box(f"table.leg{sx}{sy}", (0.08, 0.08, 0.74), (sx * 1.0, sy, 0.37), dark, root, bevel=0.01)
    for sx in (-1.0, 1.0):
        kit.box(f"table.brace{sx}", (0.06, 0.7, 0.06), (sx * 1.0, 0, 0.3), dark, root)
    # a lemonade pitcher on the cloth
    kit.cyl("pitcher.body", 0.1, 0.26, (-0.8, 0.0, 0.95), pl("#fff0a0", 0.2, spec=0.5), root, n=14)
    kit.box("pitcher.handle", (0.03, 0.12, 0.18), (-0.8, 0.14, 0.95), pl("#fff0a0", 0.3), root)
    kit.cyl("pitcher.lid", 0.105, 0.03, (-0.8, 0, 1.095), pl("#e8503c", 0.4), root, n=14)
    # two short benches, not under the west end (Mia stands there)
    for sy, nm in ((0.8, "n"),):          # one bench (north): the south side stays open for the napkin shot
        kit.box(f"bench.{nm}", (1.3, 0.3, 0.07), (tx + 0.6, ty + sy, 0.46), wood, None, bevel=0.015)
        for sx in (-0.5, 0.5):
            kit.box(f"bench.{nm}.leg{sx}", (0.07, 0.25, 0.43), (tx + 0.6 + sx, ty + sy, 0.215), dark)
    # the folded napkin that goes under the east-south leg (shown by cue)
    W["napkin"] = kit.box("napkin", (0.22, 0.22, 0.05), (tx + 1.0, ty - 0.3, 0.015), pl("#ffffff", 0.9), None, bevel=0.005)
    W["napkin"].hide_render = True


def build_bunting(kit):
    pl = kit.plastic
    pole = pl("#8a6238", 0.7)
    ya = 6.2
    xa, xb, z0 = -4.4, 6.4, 3.0
    for x in (xa, xb):
        kit.cyl(f"pole{x}", 0.04, 3.2, (x, ya, 1.6), pole, n=10)
    cols = ["#ff6a3d", "#ffe066", "#4aa8ff", "#66d06c", "#ff7aa8"]
    n = 14
    for i in range(n):
        u = (i + 0.5) / n
        x = xa + (xb - xa) * u
        z = z0 - 0.35 * math.sin(math.pi * u)
        kit.box(f"flag{i}", (0.22, 0.02, 0.22), (x, ya, z - 0.13), pl(cols[i % 5], 0.7), rot=(0, math.pi / 4, 0))
    for i in range(n):
        u0, u1 = i / n, (i + 1) / n
        x0 = xa + (xb - xa) * u0
        x1 = xa + (xb - xa) * u1
        z_0 = z0 - 0.35 * math.sin(math.pi * u0)
        z_1 = z0 - 0.35 * math.sin(math.pi * u1)
        ln = math.hypot(x1 - x0, z_1 - z_0)
        kit.box(f"string{i}", (ln, 0.012, 0.012), ((x0 + x1) / 2, ya, (z_0 + z_1) / 2), pole,
                rot=(0, -math.atan2(z_1 - z_0, x1 - x0), 0))


# ---------------------------------------------------------------------------------------------- Moose
def build_moose(kit):
    pl = kit.plastic
    tan = pl("#d9a868", 0.6, spec=0.1)
    dtan = pl("#b98748", 0.6, spec=0.1)
    cream = pl("#efd3a0", 0.6, spec=0.1)
    white = pl("#f6f2ea", 0.6, spec=0.1)
    blk = pl("#1c1410", 0.4, spec=0.3)
    pink = pl("#ee7f8f", 0.5, spec=0.15)
    root = kit.empty("moose", (0, 0, 0))
    W["moose"] = root
    bg = kit.empty("moose.bodyg", (0, 0.3, 0.3), root)           # pivot at the hips, for sitting and lying
    W["m_bodyg"] = bg
    kit.box("moose.body", (0.42, 0.8, 0.4), (0, -0.3, 0.16), tan, bg, bevel=0.06)
    kit.box("moose.chest", (0.34, 0.2, 0.3), (0, -0.62, 0.1), cream, bg, bevel=0.05)
    legs = {}
    for nm, sx, y in (("fl", -1, -0.52), ("fr", 1, -0.52)):
        g = kit.empty(f"moose.{nm}", (sx * 0.13, y, 0.12), bg)
        kit.box(f"moose.{nm}.b", (0.12, 0.12, 0.34), (0, 0, -0.17), tan, g, bevel=0.03)
        kit.box(f"moose.{nm}.p", (0.13, 0.17, 0.05), (0, -0.02, -0.34), cream, g, bevel=0.02)
        legs[nm] = g
    hg = kit.empty("moose.hindg", (0, 0, 0), root)
    for nm, sx in (("hl", -1), ("hr", 1)):
        g = kit.empty(f"moose.{nm}", (sx * 0.14, 0.3, 0.3), root)
        kit.box(f"moose.{nm}.b", (0.14, 0.2, 0.34), (0, 0, -0.17), tan, g, bevel=0.03)
        kit.box(f"moose.{nm}.p", (0.13, 0.19, 0.05), (0, -0.03, -0.3), cream, g, bevel=0.02)
        legs[nm] = g
    W["m_legs"] = legs
    # the head, on a neck at the front of the body
    head = kit.empty("moose.head", (0, -0.62, 0.38), bg)
    W["m_head"] = head
    kit.box("moose.skull", (0.34, 0.32, 0.32), (0, -0.1, 0.06), tan, head, bevel=0.05)
    kit.box("moose.snout", (0.2, 0.24, 0.16), (0, -0.3, -0.01), cream, head, bevel=0.04)
    kit.box("moose.nose", (0.1, 0.05, 0.07), (0, -0.43, 0.04), blk, head, bevel=0.015)
    jaw = kit.empty("moose.jawg", (0, -0.2, -0.08), head)
    W["m_jaw"] = jaw
    kit.box("moose.jaw", (0.17, 0.22, 0.05), (0, -0.1, 0.0), cream, jaw, bevel=0.015)
    W["m_tongue"] = kit.box("moose.tongue", (0.08, 0.12, 0.02), (0, -0.12, 0.03), pink, jaw)
    for sx in (-1, 1):
        kit.sphere(f"moose.eye{sx}", 0.032, (sx * 0.095, -0.27, 0.13), blk, head, seg=8)
        kit.sphere(f"moose.glint{sx}", 0.011, (sx * 0.095 + 0.008, -0.298, 0.142), white, head, seg=6)
        kit.box(f"moose.brow{sx}", (0.07, 0.015, 0.012), (sx * 0.095, -0.272, 0.19), dtan, head, rot=(0, sx * 0.25, 0))
    # ears: one tan, one white (the white one is on his left, +x)
    el = kit.empty("moose.earL", (-0.17, -0.02, 0.17), head)
    kit.box("moose.earL.b", (0.06, 0.1, 0.17), (-0.02, 0.0, -0.07), dtan, el, rot=(0, 0.35, 0), bevel=0.02)
    er = kit.empty("moose.earR", (0.17, -0.02, 0.17), head)
    kit.box("moose.earR.b", (0.06, 0.1, 0.17), (0.02, 0.0, -0.07), white, er, rot=(0, -0.35, 0), bevel=0.02)
    W["m_ears"] = (el, er)
    tail = kit.empty("moose.tail", (0, 0.1, 0.28), bg)
    W["m_tail"] = tail
    kit.box("moose.tail.b", (0.07, 0.07, 0.3), (0, 0.05, 0.13), dtan, tail, rot=(0.4, 0, 0), bevel=0.02)
    # the bark badge over his head and the camera's corner copy
    W["wb"] = build_badge(kit, None, "wbadge", 0.27)
    W["tag"] = build_badge(kit, kit.OBJ["cam"], "tag", 1.0)


def build_badge(kit, parent, nm, size):
    """The rule meter: a round cream plate with a thick dark rim, a coral paw on top and a big dark digit (1 or 2)."""
    cream = kit.emit("#fff1cc", 0.9, nm + "cream")
    edge = kit.emit("#3a2210", 0.5, nm + "edge")
    ink = kit.emit("#3a2210", 0.6, nm + "ink")
    coral = kit.emit("#e8503c", 0.8, nm + "coral")
    root = kit.empty(nm, (0, 0, -30) if parent is None else (0, 0, 0), parent)
    ob = kit.cyl(nm + ".edge", 0.58, 0.004, (0, 0, 0), edge, root, n=32)
    noshadow(ob)
    ob = kit.cyl(nm + ".plate", 0.5, 0.004, (0, 0, 0.004), cream, root, n=32)
    noshadow(ob)
    # a paw glyph near the top: a pad and three toes
    pads = [kit.box(nm + ".pad", (0.17, 0.12, 0.004), (0, 0.33, 0.008), coral, root, bevel=0.0)]
    for i, dx in enumerate((-0.14, 0.0, 0.14)):
        pads.append(kit.box(f"{nm}.toe{i}", (0.07, 0.08, 0.004), (dx, 0.43 if i == 1 else 0.41, 0.008), coral, root))
    for p in pads:
        noshadow(p)
    segs = {}
    w, h, th = 0.34, 0.5, 0.1
    cx, cy = 0.0, -0.1
    hh = h / 2
    defs = {"a": (0, hh - th / 2, w, th), "d": (0, -hh + th / 2, w, th), "g": (0, 0, w, th),
            "f": (-w / 2 + th / 2, hh / 2, th, hh), "b": (w / 2 - th / 2, hh / 2, th, hh),
            "e": (-w / 2 + th / 2, -hh / 2, th, hh), "c": (w / 2 - th / 2, -hh / 2, th, hh)}
    for s, (dx, dy, sx, sy) in defs.items():
        ob = kit.box(f"{nm}.d.{s}", (sx, sy, 0.004), (cx + dx, cy + dy, 0.008), ink, root)
        noshadow(ob)
        segs[s] = ob
    one = [noshadow(kit.box(nm + ".one.bar", (0.12, h, 0.004), (0, cy, 0.008), ink, root))]
    root.scale = (size, size, size)
    return {"root": root, "segs": segs, "one": one}


def set_digit(bd, n):
    for s, ob in bd["segs"].items():
        ob.hide_render = s not in SEG[n]
    for ob in bd["one"]:
        ob.hide_render = n != "1"


# ---------------------------------------------------------------------------------------------- props
def build_props(kit):
    pl = kit.plastic
    # the ring box: deep red velvet, big, with a gold clasp, standing in a pale window on the sill
    rb = kit.empty("ring", (0, 0, -20))
    kit.box("ring.base", (0.3, 0.22, 0.1), (0, 0, 0.0), pl("#c4183c", 0.9, spec=0.02), rb, bevel=0.025)
    kit.box("ring.lid", (0.3, 0.2, 0.08), (0, 0.03, 0.09), pl("#cf2046", 0.9, spec=0.02), rb, rot=(-0.5, 0, 0), bevel=0.025)
    kit.box("ring.clasp", (0.06, 0.03, 0.05), (0, -0.115, 0.03), pl("#f2c230", 0.3, spec=0.7), rb)
    W["ring"] = rb
    # the squeaky carrot: bright orange cone with a green leafy top
    ca = kit.empty("carrot", (0, 0, -20))
    kit.cyl("carrot.body", 0.07, 0.34, (0, 0, 0), pl("#ff8a2a", 0.5, spec=0.15), ca, rot=(0, math.pi / 2, 0), n=14, r2=0.025)
    for i, a in enumerate((-0.5, 0.0, 0.5)):
        kit.box(f"carrot.leaf{i}", (0.16, 0.035, 0.05), (-0.25, 0.04 * a * 3, 0.0), pl("#3fb04a", 0.6), ca, rot=(a, 0, 0.0),
                bevel=0.01)
    W["carrot"] = ca
    # Mia's engagement ring: a gold band round her wrist-end with a bright white stone each side (set on her arm in
    # animate; sizes are in the arm's own units, 1 wide)
    gold = pl("#ffcc33", 0.2, spec=0.8)
    W["mring"] = [(kit.box("mring.band", (1.12, 1.12, 0.2), (0, 0, -20), gold, None, bevel=0.03), (0.0, 0.0, -1.5)),
                  (kit.box("mring.stone0", (0.4, 0.4, 0.4), (0, 0, -20), pl("#ffffff", 0.1, spec=1.0), None, bevel=0.05),
                   (0.0, -0.62, -1.5)),
                  (kit.box("mring.stone1", (0.4, 0.4, 0.4), (0, 0, -20), pl("#ffffff", 0.1, spec=1.0), None, bevel=0.05),
                   (0.0, 0.62, -1.5))]
    # a biscuit
    W["biscuit"] = kit.box("biscuit", (0.12, 0.12, 0.03), (0, 0, -20), pl("#e0b070", 0.7), None, bevel=0.01)
    # the inspector's clipboard (a board, a white sheet, a clip): no marks on the sheet
    cb = kit.empty("clip", (0, 0, -20))
    kit.box("clip.board", (0.34, 0.03, 0.44), (0, 0, 0), pl("#8a6238", 0.7), cb, bevel=0.01)
    kit.box("clip.sheet", (0.29, 0.02, 0.38), (0, -0.02, -0.01), pl("#ffffff", 0.9), cb)
    kit.box("clip.clip", (0.1, 0.04, 0.05), (0, -0.03, 0.19), pl("#9aa0a8", 0.35, spec=0.5), cb)
    W["clip"] = cb
    # Grant's short beard, on his head (idempotent, attached in animate)
    bd = pl("#5a3b22", 0.8)
    W["beard_loc"] = [(0, -0.55, -0.4), (-0.37, -0.35, -0.3), (0.37, -0.35, -0.3)]
    W["beard"] = [kit.box("grant.beard.chin", (0.62, 0.1, 0.3), (0, -0.55, -0.4), bd, None, bevel=0.03),
                  kit.box("grant.beard.l", (0.12, 0.5, 0.36), (-0.37, -0.35, -0.3), bd, None, bevel=0.03),
                  kit.box("grant.beard.r", (0.12, 0.5, 0.36), (0.37, -0.35, -0.3), bd, None, bevel=0.03)]


def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    sun = kit.light("sun", "SUN", (-6, -20, 22), 3.0, "#fff0d0", size=0.06)
    sun.data.angle = 0.05
    sun.rotation_euler = (math.radians(52), math.radians(8), math.radians(-35))
    W["camfill"] = kit.light("camfill", "POINT", (0, 0, 5), 60, "#fff4e6", size=0.8, shadow=False)
    kit.LIGHTS["camfill"]["obj"].visible_camera = False
    build_ground(kit)
    build_fence(kit)
    build_house(kit)
    build_neighbour(kit)
    build_trees(kit)
    build_grill(kit)
    build_table(kit)
    build_bunting(kit)
    build_props(kit)
    build_moose(kit)
    try:
        from blocky import polish
        W["camspecs"] = polish.cam_specs(story, tl, polish.spec(story))
    except Exception:
        W["camspecs"] = None
    return {}


def cam_now(story, tl, t):
    from blocky import bl_story
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    try:
        cl, ct, lens, _ = bl_story.cam_at(W["camspecs"][shot["id"]], shot, t, {}, tl)
    except Exception:
        spec = next(s for s in story["shots"] if s["id"] == shot["id"])
        k0 = spec["cam"][0]
        cl, ct, lens = k0[1], k0[2], k0[3]
    return Vector(cl), Vector(ct), lens, shot


def hand(who, sx):
    ob = bpy.data.objects.get(f"{who}.arm{sx}")
    if ob is None:
        return None
    return ob.matrix_world @ Vector((0, 0, -1.55))


def hand_tip(who, sx):
    ob = bpy.data.objects.get(f"{who}.arm{sx}")
    if ob is None:
        return None
    return ob.matrix_world @ Vector((0, 0, -1.9))


def moose_state(tl, t):
    return sample("moose", tl, t, {"x": -1.3, "y": -1.2, "yaw": 0.0, "pose": 0.0, "dur": 0.0})


def animate(kit, story, tl, t, ctx):
    cl, ct, lens, shot = cam_now(story, tl, t)
    # ---- Moose: place, pose, walk, bark, wag
    ms = moose_state(tl, t)
    pm = moose_state(tl, t - 0.05)
    mx, my, yaw = ms["x"], ms["y"], ms["yaw"]
    root = W["moose"]
    root.location = (mx, my, 0.0)
    root.rotation_euler = (0, 0, yaw * D2R)
    dist = math.hypot(mx - pm["x"], my - pm["y"])
    speed = dist / 0.05
    walk = min(1.0, speed / 0.35)
    # distance travelled so far, for the leg phase: integrate the eased positions coarsely
    phase = 0.0
    keys = [c for c in tl["cues"] if c["name"] == "moose"]
    prevk = None
    for c in keys:
        if c["t"] > t:
            break
        if prevk is not None:
            d = math.hypot(c.get("x", 0) - prevk.get("x", 0), c.get("y", 0) - prevk.get("y", 0))
            dur = max(1e-6, c.get("dur", 0.0))
            frac = ss((t - c["t"]) / dur) if t < c["t"] + dur else 1.0
            phase += d * frac
        prevk = c
    sw = math.sin(phase * 7.0) * 0.6 * walk
    legs = W["m_legs"]
    sit, lie = ms["pose"] >= 0.5 and ms["pose"] < 1.5, ms["pose"] >= 1.5
    pose = ms["pose"]
    sitk = ss(min(1.0, max(0.0, pose))) * (1.0 - ss(min(1.0, max(0.0, pose - 1.0))))
    liek = ss(min(1.0, max(0.0, pose - 1.0)))
    bg = W["m_bodyg"]
    bg.rotation_euler = (-0.62 * sitk, 0, 0)
    bg.location = (0, 0.3, 0.3 - 0.17 * sitk - 0.16 * liek)
    for nm, s in (("fl", sw), ("fr", -sw), ("hl", -sw), ("hr", sw)):
        g = legs[nm]
        base = 0.0
        if nm.startswith("h"):
            g.rotation_euler = (s - 1.35 * sitk - 1.2 * liek, 0, 0)
            g.location.z = 0.3 - 0.2 * sitk - 0.14 * liek
        else:
            g.rotation_euler = (s + 0.0 - 1.4 * liek + 0.5 * sitk, 0, 0)
    # bark: the jaw drops and the head lifts on each bark cue
    bark = 0.0
    for c in tl["cues"]:
        if c["name"] == "bark":
            bark = max(bark, kit.bump(t, c["t"], 0.05, 0.16))
    W["m_jaw"].rotation_euler = (0.55 * bark + 0.12, 0, 0)
    head = W["m_head"]
    look = sample("mlook", tl, t, {"yaw": 0.0, "pitch": 0.0, "dur": 0.0})
    head.rotation_euler = (-0.3 * bark + look["pitch"] * D2R + 0.35 * liek, 0, look["yaw"] * D2R)
    W["m_tail"].rotation_euler = (0, 0, 0.45 * math.sin(t * 9.0) * (0.6 + 0.4 * (1 - liek)))
    for k, e in enumerate(W["m_ears"]):
        e.rotation_euler = (0.1 * math.sin(t * 2.0 + k) - 0.25 * bark, 0, 0)
    # ---- the badge: n (1 or 2), mode (0 off, 1 over Moose, 2 camera corner), a soft pop for 0.2 s after a change
    bd = sample("badge", tl, t, {"n": 1.0, "mode": 2.0})
    n = str(int(round(bd["n"])))
    mode = int(round(bd["mode"]))
    last_change = -9.0
    cur = None
    for c in tl["cues"]:
        if c["name"] != "badge" or c["t"] > t:
            continue
        if cur is not None and int(round(c.get("n", cur))) != cur:
            last_change = c["t"]
        cur = int(round(c.get("n", cur if cur is not None else 1)))
    pop = 1.0 + 0.22 * math.sin(math.pi * min(1.0, max(0.0, (t - last_change) / 0.25))) if t - last_change < 0.25 else 1.0
    wb, tag = W["wb"], W["tag"]
    hide(wb["root"], mode != 1)      # hide first: hide() also sets every child, so the digit goes on after
    hide(tag["root"], mode != 2)
    if mode == 1:
        set_digit(wb, n)
    if mode == 2:
        set_digit(tag, n)
    wr = wb["root"]
    toward = (cl - Vector((mx, my, 0.0)))
    kf = max(1.0, min(2.2, toward.length / 2.5))
    head_w = Vector((mx + 0.3 * math.sin(yaw * D2R), my - 0.3 * math.cos(yaw * D2R), 0.0)) + Vector((0, 0, 0.85 + 0.38 * kf - 0.25 * sitk - 0.3 * liek))
    toward = (cl - head_w)
    wr.location = head_w
    wr.rotation_euler = toward.to_track_quat("Z", "Y").to_euler()
    s = 0.38 * pop * max(1.0, min(2.2, toward.length / 2.5))
    wr.scale = (s, s, s)
    # ---- gate, back door
    g = sample("gate", tl, t, {"ang": 0.0, "dur": 0.0})
    swing = 3.0 * math.sin(t * 1.6) if g["ang"] > 30 else 0.0
    W["gate"].rotation_euler = (0, 0, -(g["ang"] + swing) * D2R)
    d = sample("door", tl, t, {"ang": 0.0, "dur": 0.0})
    W["backdoor"].rotation_euler = (0, 0, -d["ang"] * D2R)
    # ---- grill smoke
    gx, gy = G.GRILL
    for k, s_ in enumerate(W["smoke"]):
        u = ((t * 0.28) + k / 4.0) % 1.0
        s_.location = (gx + 0.08 * math.sin(t * 0.7 + k) + 0.25 * u, gy + 0.05 * k * 0.2, 1.2 + 1.1 * u)
        r = 0.25 + 0.6 * u
        sc = r * (1.0 - u * u)
        s_.scale = (sc, sc, sc)
    # ---- the table rocks while the `rock` cue is on, and stops when the napkin is under its leg
    rk = sample("rock", tl, t, {"amp": 0.0, "dur": 0.0})
    W["table"].rotation_euler = (0.018 * rk["amp"] * math.sin(t * 11.0), 0, 0)
    nap = sample("napkin", tl, t, {"on": 0.0})
    W["napkin"].hide_render = nap["on"] < 0.5
    # ---- the ring box: on the sill (0), in Grant's right hand (1), pocketed (2)
    rg = sample("ring", tl, t, {"mode": 0.0})
    rm = int(round(rg["mode"]))
    W["ring"].location = (0, 0, -20)
    hide(W["ring"], rm == 2)
    if rm == 0:
        W["ring"].location = G.RING
        W["ring"].rotation_euler = (0, 0, 0)
    elif rm == 1:
        h = hand("grant", 1)
        if h is not None:
            W["ring"].location = h + Vector((0.0, -0.12, 0.08))
            W["ring"].rotation_euler = (0, 0, 0)
    # ---- the carrot toy: placed (`at`), or in Moose's mouth (`carry` 1)
    ct_ = sample("carrot", tl, t, {"on": 0.0, "x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0, "carry": 0.0, "dur": 0.0})
    ca = W["carrot"]
    hide(ca, ct_["on"] < 0.5)
    if ct_["carry"] > 0.5:
        mouth = W["m_head"].matrix_world @ Vector((0, -0.4, -0.1))
        ca.location = mouth
        ca.rotation_euler = (0, 0, yaw * D2R + math.pi / 2)
    else:
        ca.location = (ct_["x"], ct_["y"], ct_["z"] + 0.07)
        ca.rotation_euler = (0, 0, ct_["yaw"] * D2R)
    # ---- the biscuit: from the carrier's hand (cue gives both ends) into Moose's mouth
    bs = sample("biscuit", tl, t, {"on": 0.0})
    W["biscuit"].hide_render = bs["on"] < 0.5
    h = hand("mail", 1)
    if h is not None and bs["on"] >= 0.5:
        W["biscuit"].location = h + Vector((0.0, 0.0, 0.0))
    # ---- the clipboard (inspector's left hand) and the spatula (Grant's right hand)
    cp = sample("clip", tl, t, {"on": 0.0})
    hide(W["clip"], cp["on"] < 0.5)
    if cp["on"] >= 0.5:
        h = hand("inspector", -1)
        if h is not None:
            W["clip"].location = h + Vector((0.0, -0.18, 0.12))
            W["clip"].rotation_euler = (0, 0, 0)
    sp = sample("spat", tl, t, {"on": 0.0})
    hide(W["spat"], sp["on"] < 0.5)
    if sp["on"] >= 0.5:
        h = hand("grant", 1)
        if h is not None:
            W["spat"].location = h + Vector((0.0, -0.1, 0.0))
            W["spat"].rotation_euler = (-1.2, 0, 0)
    # ---- Mia's ring: a gold band with a white stone on her ring hand (the one the camera sees)
    marm = bpy.data.objects.get("mia.arm1")
    for ob, off in W["mring"]:
        if marm is not None and ob.parent is not marm:
            ob.parent = marm
        ob.location = off
        ob.hide_render = marm is None or marm.hide_render
    # ---- Grant's beard follows his head
    hg = bpy.data.objects.get("grant.headg")
    for ob, loc in zip(W["beard"], W["beard_loc"]):
        if hg is not None:
            if ob.parent is not hg:
                ob.parent = hg
            ob.location = loc
            ob.hide_render = hg.hide_render
    # ---- the camera's own soft fill on faces, scaled by distance so a close-up is not blown out
    f = ct - cl
    dd = max(0.5, f.length)
    cf = kit.LIGHTS["camfill"]["obj"]
    cf.location = cl + Vector((0.0, 0.0, 0.35))
    return {"camfill": min(2.2, 0.25 + 0.16 * dd * dd) * 0.55}
