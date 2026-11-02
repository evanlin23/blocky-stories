"""Ep56 "marsh mill": a marsh town in late autumn. One world, four places.

The street (house fronts on y = 6, pavement y 1 to 6, people stand at y 4.6 facing +y): painted doors in five colours,
a bakery, a cafe with a striped awning. A lone shop at (30, 25) where the narrator tries his key at dusk, with the
windmill far behind it. The track runs up +y along x = 30 to the windmill at (MX, MY) = (30, 95), its door on the -y
side. Inside, the floor is local to the tower centre: stones at (0, 1.1), the sack hoist and its oak post by (0.55, -0.9),
the cleared patch of floor beside them. The cafe interior is at x 150, the kitchen at x 200.

Everything that changes inside a shot is keyed from story.json cues: `glow` (a key warms to gold over 1 s), `door`,
`moon` (a 2 s fade). The light is a preset per shot (look_of) and only ever changes at a cut. No light flickers: the
stove, the torch and the lamp are steady, and every ramp inside a shot is 0.3 s or longer.
"""

from __future__ import annotations

import math
import random

import bpy
from mathutils import Vector as V

from blocky import acting, kit
from blocky.kit import box, cyl, empty, plane, sphere

MX, MY = 30.0, 95.0
AP = 3.2          # the tower's inner apothem
CX, CY = 150.0, 0.0
KX, KY = 200.0, 0.0
FOG_NODES = {"built": False}
S = 0.34


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------------------------------------ materials


def materials(kit):
    M = {}
    M["tar"] = kit.plastic("#2a2624", 0.85, name="tar")
    M["white"] = kit.plastic("#bfb9ab", 0.95, name="whitewash")
    M["sailw"] = kit.plastic("#e4dfd2", 0.7, name="sail_white")
    M["flour"] = kit.plastic("#bab5a7", 0.95, name="flour_floor")
    M["flour_pl"] = kit.plastic("#cfcabc", 0.95, name="flour_plain")
    M["clean"] = kit.plastic("#5a4c40", 0.9, name="clean_patch")
    M["oak"] = kit.planks("#7a5a3c", "#5a4029", scale=2.0, axis="Z", name="oak")
    M["oakh"] = kit.planks("#6e5036", "#4e3722", scale=2.0, axis="X", name="oak_h")
    M["oak_dk"] = kit.plastic("#4a3524", 0.8, name="oak_dk")
    M["iron"] = kit.metal("#2e2e30", 0.55, name="iron")
    M["stone"] = kit.plastic("#8d8a82", 0.85, name="millstone")
    M["stone_dk"] = kit.plastic("#6a6862", 0.9, name="stone_dk")
    M["brick"] = kit.bricks("#8a4a36", "#6e3a2a", "#4a4540", scale=1.0, name="brick_town")
    M["slate"] = kit.plastic("#3c3f48", 0.8, name="slate")
    M["pave"] = kit.cobbles("#8d8678", "#b3ab9a", "#4a453d", scale=2.4, wet=0.0, name="pave")
    M["road"] = kit.grime("#6e6a62", 0.5, 2.0, name="road")
    M["marsh"] = kit.grime("#7e7a4c", 0.55, 0.5, name="marsh_ground")
    M["track"] = kit.grime("#8a7456", 0.4, 1.5, name="track_earth")
    M["water"] = kit.plastic("#4f6a6e", 0.15, name="dyke")
    M["reed"] = kit.plastic("#a89a5c", 0.9, name="reed")
    M["reed2"] = kit.plastic("#8a7e46", 0.9, name="reed2")
    M["glass"] = kit.plastic("#2e3a44", 0.15, name="win_glass")
    M["glass_dk"] = kit.plastic("#161a1e", 0.2, name="win_dark")
    M["sill"] = kit.plastic("#e4dfd2", 0.7, name="sill")
    M["brass"] = kit.plastic("#c8a24a", 0.35, name="brass_set")
    M["plum"] = kit.plastic("#7a3d6c", 0.5, name="plum_stroke")
    M["sack"] = kit.plastic("#bdb49c", 0.95, name="sack")
    M["red"] = kit.plastic("#b4503e", 0.6, name="p_red")
    M["teal"] = kit.plastic("#3f8a86", 0.6, name="p_teal")
    M["green"] = kit.plastic("#4f7a4a", 0.6, name="p_green")
    M["yellow"] = kit.plastic("#d8b23c", 0.6, name="p_yellow")
    M["blue"] = kit.plastic("#3f64a0", 0.6, name="p_blue")
    M["orange"] = kit.plastic("#d4803a", 0.6, name="p_orange")
    M["plumpaint"] = kit.plastic("#8a4a7a", 0.6, name="p_plum")
    M["cream"] = kit.plastic("#eadfc8", 0.7, name="cream")
    M["stripe_a"] = kit.plastic("#efe7d6", 0.7, name="stripe_cream")
    M["stripe_b"] = kit.plastic("#b4503e", 0.7, name="stripe_red")
    M["bread"] = kit.plastic("#b9803f", 0.6, name="bread")
    M["floorw"] = kit.planks("#8a7a62", "#6a5c48", scale=2.0, axis="X", name="floor_wood")
    M["wall_in"] = kit.plastic("#c4b8a2", 0.9, name="wall_in")
    M["lamp"] = kit.emit("#ffcf8a", 3.0, name="lampshade")
    M["cup"] = kit.plastic("#e8e2d4", 0.4, name="cup")
    M["shadow"] = kit.plastic("#0b0a0c", 0.95, name="shadowcut")
    M["dark"] = kit.plastic("#161412", 0.9, name="dark_in")
    M["rope"] = kit.plastic("#a8946a", 0.9, name="rope")
    M["chain"] = kit.metal("#4a4a4c", 0.5, name="chain")
    M["spill"] = kit.emit("#ffc070", 1.1, name="spill")
    M["moonpane"] = kit.emit("#a8c0ff", 0.9, name="moonpane")
    M["sky"] = kit.plastic("#a9c8e0", 1.0, name="skyplane")
    M["cord"] = kit.plastic("#2a1c14", 0.8, name="cord")
    M["btn"] = kit.plastic("#2a1822", 0.5, name="smock_btn")
    return M


# ------------------------------------------------------------------------------------------------ the street


def window(kit, M, x, y, z, w=0.9, h=1.1, parent=None):
    box("win", (w, 0.06, h), (x, y, z), M["glass"], parent, bevel=0.02)
    box("winf", (w + 0.16, 0.04, 0.08), (x, y - 0.02, z + h / 2 + 0.04), M["sill"], parent)
    box("winf", (w + 0.16, 0.08, 0.1), (x, y - 0.04, z - h / 2 - 0.05), M["sill"], parent)
    for sx in (-1, 1):
        box("winf", (0.08, 0.04, h), (x + sx * (w / 2 + 0.04), y - 0.02, z), M["sill"], parent)


def house(kit, M, ctx, name, xc, paint, width=5.3, floors=2, door=True, hall=True):
    h = 3.2 * floors
    box(f"{name}.wall", (width, 0.6, h), (xc, 6.3, h / 2), M["brick"])
    box(f"{name}.base", (width + 0.04, 0.64, 0.5), (xc, 6.3, 0.25), M["stone_dk"] if "stone_dk" in M else M["slate"])
    # pitched roof, two slopes, and a chimney
    box(f"{name}.roofa", (width + 0.3, 5.0, 0.3), (xc, 8.2, h + 0.9), M["slate"], rot=(0.5, 0, 0))
    box(f"{name}.roofb", (width + 0.3, 3.0, 0.3), (xc, 6.4, h + 0.15), M["slate"], rot=(-0.2, 0, 0))
    box(f"{name}.chim", (0.7, 0.7, 1.6), (xc + width * 0.3, 7.4, h + 1.3), M["brick"])
    for fl in range(floors):
        zz = 1.9 + fl * 3.2
        if fl == 0:
            window(kit, M, xc + width * 0.3, 5.96, zz + 0.2, 0.9, 1.1)
            window(kit, M, xc - width * 0.34, 5.96, zz + 0.2, 0.8, 1.1)
        else:
            window(kit, M, xc - width * 0.3, 5.96, zz, 0.9, 1.2)
            window(kit, M, xc + width * 0.3, 5.96, zz, 0.9, 1.2)
            window(kit, M, xc, 5.96, zz, 0.9, 1.2)
    if door:
        # a recess behind the door (dark hall), a pale frame, a painted leaf on a hinge, a lock plate
        box(f"{name}.hall", (1.1, 0.6, 2.2), (xc, 6.45, 1.1), M["dark"])
        for sx in (-1, 1):
            box(f"{name}.jamb", (0.12, 0.1, 2.34), (xc + sx * 0.6, 5.93, 1.17), M["sill"])
        box(f"{name}.lintel", (1.32, 0.1, 0.12), (xc, 5.93, 2.34), M["sill"])
        box(f"{name}.step", (1.5, 0.7, 0.14), (xc, 5.55, 0.07), M["stone_dk"] if "stone_dk" in M else M["slate"])
        piv = empty(f"{name}.piv", (xc - 0.5, 5.9, 0.14))
        box(f"{name}.leaf", (1.0, 0.07, 2.12), (0.5, 0, 1.06), paint, piv, bevel=0.02)
        box(f"{name}.panel", (0.7, 0.03, 0.8), (0.5, -0.04, 1.5), paint, piv, bevel=0.02)
        box(f"{name}.plate", (0.16, 0.03, 0.3), (0.84, -0.045, 1.0), M["iron"], piv)
        cyl(f"{name}.kh", 0.03, 0.04, (0.84, -0.06, 1.04), M["dark"], piv, rot=(math.pi / 2, 0, 0), n=10)
        ctx["doors"][name] = (piv, 100.0)
    return h


def build_street(kit, M, ctx):
    plane("pave", (110, 5.2), (0, 3.5, 0.0), M["pave"])
    plane("road", (110, 8), (0, -2.5, -0.01), M["road"])
    box("curb", (110, 0.25, 0.14), (0, 0.85, 0.05), M["stone_dk"] if "stone_dk" in M else M["slate"])
    # low wall on the marsh side
    box("lowwall", (60, 0.4, 0.7), (0, -6.5, 0.35), M["stone"], bevel=0.04)
    pal = [("bakery", -21.6, M["cream"]), ("h1", -16.2, M["teal"]), ("h2", -10.8, M["red"]), ("h3", -5.4, M["green"]),
           ("h4", 0.0, M["yellow"]), ("h5", 5.4, M["blue"]), ("cafe", 10.8, M["plumpaint"]), ("h7", 16.2, M["orange"]),
           ("h8", 21.6, M["teal"]), ("h9", 27.0, M["red"])]
    for nm, xc, paint in pal:
        h = house(kit, M, ctx, nm, xc, paint, floors=2, door=True)
    # the bakery: a board with a loaf glyph, a window of loaves
    box("bk.board", (2.6, 0.12, 0.8), (-21.6, 5.9, 3.1), M["oak"], bevel=0.03)
    box("bk.loaf", (0.95, 0.14, 0.42), (-21.6, 5.82, 3.1), M["bread"], bevel=0.14)
    for k in (-0.25, 0, 0.25):
        box("bk.slash", (0.05, 0.16, 0.32), (-21.6 + k, 5.8, 3.1), M["cream"], rot=(0, 0.5, 0))
    for k in range(4):
        box("bk.bread", (0.4, 0.3, 0.26), (-23.0 + 0.5 * k, 5.85, 1.0), M["bread"], bevel=0.1)
    # the cafe: a striped awning, blank windows
    for k in range(10):
        box("awn", (0.54, 1.5, 0.05), (10.8 - 2.7 + 0.27 + 0.54 * k, 5.2, 2.75), M["stripe_a"] if k % 2 else M["stripe_b"],
            rot=(0.28, 0, 0))
    for sx in (-1, 1):
        box("awnpost", (0.06, 0.06, 2.6), (10.8 + sx * 2.5, 4.55, 1.3), M["iron"])
    # a lamp post
    box("lamppost", (0.1, 0.1, 3.4), (3.0, 1.4, 1.7), M["iron"])
    # the sky beyond, the marsh behind the terrace is hidden by the houses


# ------------------------------------------------------------------------------------------------ the marsh, shop, mill


def build_marsh(kit, M, ctx):
    plane("marsh", (900, 900), (0, 0, -0.03), M["marsh"])
    box("track", (3.0, 80, 0.06), (MX, 60, 0.04), M["track"])
    box("trackb", (14, 30, 0.05), (MX, 22, 0.03), M["track"])
    for sx in (-1, 1):
        box("dyke", (3.2, 100, 0.03), (MX + sx * 6.5, 60, 0.0), M["water"])
    rnd = random.Random(7)
    for i in range(70):
        cx = MX + rnd.uniform(-34, 34)
        cy = rnd.uniform(34, 130)
        if abs(cx - MX) < 3.2:
            continue
        for j in range(4):
            hh = rnd.uniform(1.0, 1.8)
            box("reed", (0.06, 0.06, hh), (cx + rnd.uniform(-0.5, 0.5), cy + rnd.uniform(-0.5, 0.5), hh / 2),
                M["reed"] if j % 2 else M["reed2"], rot=(rnd.uniform(-0.1, 0.1), rnd.uniform(-0.1, 0.1), 0))
    for i in range(30):
        cx = rnd.uniform(-50, 70)
        cy = rnd.uniform(-30, -9)
        for j in range(3):
            hh = rnd.uniform(1.0, 1.8)
            box("reed", (0.06, 0.06, hh), (cx + rnd.uniform(-0.5, 0.5), cy + rnd.uniform(-0.5, 0.5), hh / 2), M["reed"])


def build_shop(kit, M, ctx):
    # a lone low shop on the track, door facing -y; a second shed door beside it
    x, y = MX - 4.5, 25.0
    box("shop.body", (4.2, 3.0, 2.9), (x, y + 1.5, 1.45), M["brick"])
    box("shop.roof", (4.6, 3.4, 0.2), (x, y + 1.6, 3.0), M["slate"], rot=(0.12, 0, 0))
    box("shop.hall", (1.1, 0.5, 2.2), (x, y - 0.1, 1.1), M["dark"])
    piv = empty("shop.piv", (x - 0.5, y - 0.28, 0.0))
    box("shop.leaf", (1.0, 0.07, 2.1), (0.5, 0, 1.05), M["blue"], piv, bevel=0.02)
    box("shop.plate", (0.16, 0.03, 0.3), (0.84, -0.045, 1.0), M["iron"], piv)
    for sx in (-1, 1):
        box("shop.jamb", (0.12, 0.1, 2.2), (x + sx * 0.6, y - 0.3, 1.1), M["sill"])
    box("shop.lintel", (1.32, 0.1, 0.12), (x, y - 0.3, 2.2), M["sill"])
    window(kit, M, x + 1.5, y - 0.02, 1.4, 0.8, 0.9)
    kit.light("shoplamp", "POINT", (x - 0.2, y - 1.4, 2.3), 1.0, "#ffd9a0", size=0.4, shadow=False)
    for k in range(7):
        box("shop.awn", (0.6, 1.0, 0.05), (x - 2.0 + 0.3 + 0.6 * k, y - 0.7, 2.45), M["stripe_a"] if k % 2 else M["stripe_b"], rot=(0.3, 0, 0))
    # second door, a shed
    x2 = MX - 11.0
    y2 = 26.0
    box("shed.body", (2.6, 2.4, 2.5), (x2, y2 + 1.2, 1.25), M["oakh"])
    box("shed.roof", (3.0, 2.8, 0.15), (x2, y2 + 1.3, 2.6), M["slate"], rot=(0.1, 0, 0))
    piv2 = empty("shed.piv", (x2 - 0.45, y2 - 0.1, 0.0))
    box("shed.leaf", (0.9, 0.07, 2.0), (0.45, 0, 1.0), M["green"], piv2, bevel=0.02)
    box("shed.plate", (0.14, 0.03, 0.28), (0.74, -0.045, 1.0), M["iron"], piv2)


def mill_slab(kit, M, ctx, i, hole=None, door=False):
    """Slab i of the tower (i = 0 faces -y). Local: x along the wall, -y outward, z up. 8 slabs round an apothem 2.5."""
    th = math.radians(i * 45 - 90)
    ap = AP
    ob = empty(f"slab{i}", (MX + ap * math.cos(th), MY + ap * math.sin(th), 0), rot=(0, 0, th + math.pi / 2))
    W, Hh = 2.95, 3.6

    def piece(x0, x1, z0, z1):
        w, h = x1 - x0, z1 - z0
        box(f"s{i}.tar", (w, 0.4, h), ((x0 + x1) / 2, -0.2, (z0 + z1) / 2), M["tar"], ob)
        box(f"s{i}.in", (w, 0.1, min(h, 3.6 - z0) if z0 < 3.6 else 0.01), ((x0 + x1) / 2, 0.04, z0 + (min(h, 3.6 - z0) if z0 < 3.6 else 0.01) / 2),
            M["white"], ob)

    if door:
        piece(-W / 2, -0.5, 0, Hh)
        piece(0.5, W / 2, 0, Hh)
        piece(-0.5, 0.5, 2.12, Hh)
    elif hole:
        hx, hz0, hz1, hw = hole
        piece(-W / 2, hx - hw / 2, 0, Hh)
        piece(hx + hw / 2, W / 2, 0, Hh)
        piece(hx - hw / 2, hx + hw / 2, 0, hz0)
        piece(hx - hw / 2, hx + hw / 2, hz1, Hh)
    else:
        piece(-W / 2, W / 2, 0, Hh)
    return ob


def build_mill(kit, M, ctx):
    # floor with flour, the plinth, the tower
    cyl("mill.plinth", 4.2, 0.3, (MX, MY, -0.12), M["stone_dk"], n=8, rot=(0, 0, math.radians(22.5)))
    cyl("mill.floor", 3.55, 0.04, (MX, MY, 0.012), M["flour"], n=8, rot=(0, 0, math.radians(22.5)))
    for i in range(8):
        if i == 0:
            mill_slab(kit, M, ctx, i, door=True)
        elif i == 4:
            mill_slab(kit, M, ctx, i, hole=(0.0, 2.1, 2.8, 0.62))
        else:
            mill_slab(kit, M, ctx, i)
    # ceiling and beams
    cyl("mill.ceil", 3.9, 0.15, (MX, MY, 3.68), M["oakh"], n=8, rot=(0, 0, math.radians(22.5)))
    for k in range(-4, 5):
        box("beam", (6.6, 0.26, 0.3), (MX, MY + k * 0.85, 3.45), M["oak_dk"], bevel=0.02)
    # the trapdoor over the hoist: a dark square in the beams
    box("trapdoor", (0.9, 0.9, 0.06), (MX + 0.55, MY - 0.1, 3.58), M["dark"])
    # upper tower and cap, sails
    cyl("mill.top", 3.92, 6.0, (MX, MY, 6.6), M["tar"], n=8, rot=(0, 0, math.radians(22.5)), r2=3.2)
    cyl("mill.cap", 3.3, 1.6, (MX, MY, 10.4), M["sailw"], n=8, rot=(0, 0, math.radians(22.5)))
    cyl("mill.roof", 3.4, 1.9, (MX, MY, 12.15), M["sailw"], n=8, rot=(0, 0, math.radians(22.5)), r2=0.25)
    cyl("mill.gal", 4.5, 0.12, (MX, MY, 6.0), M["oakh"], n=8, rot=(0, 0, math.radians(22.5)))
    for i in range(8):
        th = math.radians(i * 45 - 90)
        box("mill.rail", (0.07, 0.07, 0.95), (MX + 4.3 * math.cos(th), MY + 4.3 * math.sin(th), 6.5), M["sailw"])
    box("mill.axle", (0.5, 1.9, 0.5), (MX, MY - 4.0, 10.4), M["oak_dk"])
    hub = (MX, MY - 5.0, 10.4)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        rot = (0, a, 0)
        arm = empty(f"sail{k}", hub, rot=(0, -a, 0))
        box("stock", (0.22, 0.22, 15.0), (0, 0, 0), M["sailw"], arm)
        box("sailp", (1.5, 0.09, 6.2), (0.85, 0.2, 4.4), M["sailw"], arm)
        for j in range(6):
            box("lat", (1.5, 0.12, 0.08), (0.85, 0.2, 1.5 + j * 1.0), M["oakh"], arm)
    # the door: a leaf on a hinge, a small window at face height, a lock plate with the wheel glyph
    slab = bpy.data.objects["slab0"]
    piv = empty("mill.doorpiv", (0, 0, 0), slab)
    piv.location = (-0.5, -0.2, 0.0)
    w, wz0, wz1, ww = 1.0, 1.25, 1.85, 0.62
    box("md.bot", (w, 0.1, wz0), (0.5, 0, wz0 / 2), M["oak"], piv)
    box("md.top", (w, 0.1, 2.08 - wz1), (0.5, 0, (2.08 + wz1) / 2), M["oak"], piv)
    for sx in (-1, 1):
        sw = (w - ww) / 2
        box("md.side", (sw, 0.1, wz1 - wz0), (0.5 + sx * (ww + sw) / 2, 0, (wz0 + wz1) / 2), M["oak"], piv)
    for sx in (-1, 1):
        box("md.fr", (0.05, 0.12, wz1 - wz0 + 0.06), (0.5 + sx * ww / 2, -0.01, (wz0 + wz1) / 2), M["oak_dk"], piv)
    box("md.frt", (ww, 0.12, 0.05), (0.5, -0.01, wz1 + 0.01), M["oak_dk"], piv)
    box("md.frb", (ww, 0.12, 0.05), (0.5, -0.01, wz0 - 0.01), M["oak_dk"], piv)
    for z in (0.5, 1.9):
        box("md.band", (w, 0.12, 0.07), (0.5, -0.01, z), M["iron"], piv)
    ctx["lockplate"] = box("md.plate", (0.26, 0.04, 0.36), (0.82, -0.07, 0.95), M["iron"], piv, bevel=0.01)
    # escutcheon: the same four-spoke wheel as the narrator's key head, cut dark with a pale rim
    gl = empty("md.glyph", (0.82, -0.1, 0.99), piv)
    cyl("md.gr", 0.1, 0.02, (0, 0, 0), M["brass"], gl, rot=(math.pi / 2, 0, 0), n=20)
    cyl("md.gd", 0.075, 0.03, (0, -0.002, 0), M["dark"], gl, rot=(math.pi / 2, 0, 0), n=20)
    for ang in (0, 90):
        box("md.spk", (0.15, 0.034, 0.028), (0, -0.003, 0), M["brass"], gl, rot=(0, math.radians(ang), 0))
    cyl("md.hub", 0.03, 0.036, (0, -0.004, 0), M["brass"], gl, rot=(math.pi / 2, 0, 0), n=12)
    ctx["doors"]["mill"] = (piv, 100.0)    # swings inward (toward +y)
    # the stone step, three sacks
    box("mill.step", (1.7, 0.9, 0.2), (MX, MY - 4.1, 0.1), M["stone"], bevel=0.03)
    ctx["sacks"] = []
    for k in range(3):
        ctx["sacks"].append(box(f"sack{k}", (0.5, 0.34, 0.62), (MX - 0.75 + 0.62 * k, MY - 4.55 - 0.3 * (k % 2), 0.4), M["sack"], bevel=0.12))
    # the scarf caught in the door (L27)
    ctx["scarf"] = box("scarf", (0.2, 0.03, 0.8), (MX + 0.45, MY - 3.64, 1.1), M["sack"], bevel=0.02)
    # the spill of light on the marsh when the door is open at night
    ctx["spill"] = plane("spillpl", (1.5, 5.0), (MX, MY - 6.6, 0.08), M["spill"])
    # ---- inside: stones, hopper, chute and bins, stove, stools, ladder, the hoist and its post
    casing = box("casing", (1.7, 1.7, 0.85), (MX, MY + 1.4, 0.42), M["oakh"], bevel=0.03)
    cyl("stone_a", 0.78, 0.22, (MX, MY + 1.4, 0.95), M["stone"], n=24)
    cyl("stone_b", 0.4, 0.04, (MX, MY + 1.4, 1.08), M["stone_dk"], n=16)
    ctx["hopper"] = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            ctx["hopper"].append(box("hop.leg", (0.08, 0.08, 1.5), (MX + sx * 0.5, MY + 1.4 + sy * 0.5, 1.55), M["oak_dk"]))
    ctx["hopper"].append(cyl("hopper", 0.7, 0.7, (MX, MY + 1.4, 2.0), M["oak"], n=4, rot=(0, 0, math.radians(45)), r2=0.2))
    box("chute", (0.3, 0.9, 0.2), (MX + 1.3, MY + 0.95, 0.6), M["oakh"], rot=(0, 0, -0.3))
    box("bin", (0.8, 0.7, 0.7), (MX - 2.4, MY + 1.3, 0.35), M["oak"])
    box("bin2", (0.8, 0.7, 0.7), (MX + 2.3, MY + 1.6, 0.35), M["oak"])
    # stove
    box("stove", (0.7, 0.6, 0.9), (MX - 2.4, MY + 0.0, 0.45), M["iron"], bevel=0.03)
    box("stovepipe", (0.12, 0.12, 2.9), (MX - 2.4, MY + 0.2, 2.3), M["iron"])
    box("stoveglow", (0.3, 0.04, 0.18), (MX - 2.03, MY + 0.0, 0.5), kit.emit("#ff9a3a", 2.2, name="stove_door"))
    # a ladder
    for sx in (-1, 1):
        box("lad", (0.07, 0.07, 3.4), (MX + 1.6 + sx * 0.25, MY + 2.9, 1.7), M["oak_dk"], rot=(-0.12, 0, 0))
    for k in range(7):
        box("rung", (0.5, 0.05, 0.05), (MX + 1.6, MY + 2.86 - 0.002 * k, 0.4 + k * 0.45), M["oak_dk"])
    # stools: Win's, and my old one with a back plank so which way it faces reads
    def stool(nm, back):
        ob = empty(nm, (0, 0, 0))
        cyl(f"{nm}.seat", 0.23, 0.07, (0, 0, 0.5), M["oak"], ob, n=14)
        for k in range(3):
            a = k * 2.094
            box(f"{nm}.leg", (0.05, 0.05, 0.5), (0.15 * math.cos(a), 0.15 * math.sin(a), 0.25), M["oak_dk"], ob)
        if back:
            box(f"{nm}.back", (0.4, 0.05, 0.4), (0, 0.22, 0.75), M["oak_dk"], ob, bevel=0.015)
        return ob
    ctx["stool_win"] = stool("stool_win", False)
    ctx["stool_me"] = stool("stool_me", True)
    # the hoist: chain and hook through the trapdoor, and the oak post beside it, with two plum strokes
    box("hoist.chain", (0.04, 0.04, 1.6), (MX + 0.55, MY - 0.1, 2.8), M["chain"])
    for k in range(7):
        box("hoist.link", (0.1, 0.03, 0.06), (MX + 0.55, MY - 0.1, 2.1 + 0.2 * k), M["chain"], rot=(0, 0, 0.0))
    box("hoist.hook", (0.12, 0.05, 0.14), (MX + 0.55, MY - 0.1, 1.98), M["iron"])
    post = box("hoist.post", (0.26, 0.26, 3.5), (MX + 0.95, MY - 0.15, 1.75), M["oak"], bevel=0.02)
    ctx["post"] = post
    # two plum strokes scratched at shoulder height on the post's door-facing side (lore tally)
    for k, dx in enumerate((-0.05, 0.06)):
        box(f"tally{k}", (0.035, 0.012, 0.34), (MX + 0.95 + dx, MY - 0.15 - 0.133, 1.5), M["plum"], rot=(0, 0.1 if k else -0.1, 0))
    # the clean patch: two boot shapes (sole and heel each)
    ctx["patch"] = empty("patch", (MX, MY, 0.045))
    for k, dx in enumerate((-0.2, 0.2)):
        box("patch.sole", (0.2, 0.36, 0.01), (dx, 0.07, 0.0), M["clean"], ctx["patch"])
        box("patch.heel", (0.14, 0.14, 0.01), (dx, -0.22, 0.0), M["clean"], ctx["patch"])
    # the torch-shadow cut-out on the back wall (L30 to L32): a person with arms down and arms up
    sh = empty("shadowcut", (MX + 0.4, MY + 3.06, 0))
    ctx["shadow_body"] = [
        box("sh.legL", (0.34, 0.02, 1.4), (-0.2, 0, 0.7), M["shadow"], sh),
        box("sh.legR", (0.34, 0.02, 1.4), (0.2, 0, 0.7), M["shadow"], sh),
        box("sh.torso", (1.0, 0.02, 1.1), (0, 0, 1.95), M["shadow"], sh),
        box("sh.head", (0.5, 0.02, 0.55), (0, 0, 2.78), M["shadow"], sh),
    ]
    ctx["shadow_down"] = [box("sh.dL", (0.3, 0.02, 1.2), (-0.72, 0, 1.95), M["shadow"], sh),
                          box("sh.dR", (0.3, 0.02, 1.2), (0.72, 0, 1.95), M["shadow"], sh)]
    ctx["shadow_up"] = [box("sh.uL", (0.3, 0.02, 1.5), (-0.62, 0, 3.0), M["shadow"], sh),
                        box("sh.uR", (0.3, 0.02, 1.5), (0.62, 0, 3.0), M["shadow"], sh)]
    ctx["shadow"] = sh
    # flour in the air: tiny flecks
    fl = kit.emit("#d8d2c0", 1.0, name="fleck")
    rnd = random.Random(3)
    ctx["flecks"] = [(sphere(f"fleck{i}", 0.014, (MX, MY, -50), fl, seg=6),
                      (rnd.uniform(-1.8, 1.8), rnd.uniform(-2.4, 2.2), rnd.uniform(0, 3.2), rnd.uniform(0.04, 0.12)))
                     for i in range(34)]
    # the moon at the back window: a pale pane outside it, so the high window reads as a lit square
    ctx["doorglow"] = plane("doorglow", (1.0, 2.1), (MX, MY - 3.3, 1.07), kit.emit("#ffc070", 1.6, name="doorglow_m"), rot=(math.pi / 2, 0, 0))
    ctx["moonpane"] = plane("moonpane", (0.9, 0.9), (MX + 0.0, MY + 3.75, 2.45), M["moonpane"], rot=(math.pi / 2, 0, 0))


# ------------------------------------------------------------------------------------------------ rooms


def build_cafe(kit, M, ctx):
    x, y = CX, CY
    plane("cafe.floor", (8, 6), (x, y, 0), M["floorw"])
    box("cafe.back", (8, 0.2, 3), (x, y + 3, 1.5), M["wall_in"])
    box("cafe.left", (0.2, 6, 3), (x - 4, y, 1.5), M["wall_in"])
    box("cafe.right", (0.2, 6, 3), (x + 4, y, 1.5), M["wall_in"])
    box("cafe.win", (2.2, 0.1, 1.4), (x + 1.2, y + 2.88, 1.6), kit.emit("#cfe2f0", 1.1, name="cafe_window"))
    box("cafe.table", (1.1, 1.1, 0.08), (x, y + 0.2, 0.75), M["oak"], bevel=0.02)
    box("cafe.tleg", (0.1, 0.1, 0.75), (x, y + 0.2, 0.37), M["oak_dk"])
    cyl("cafe.cup", 0.07, 0.1, (x + 0.2, y + 0.1, 0.84), M["cup"], n=12)
    for k, (cx_, cy_) in enumerate(((x - 2.4, y + 1.6), (x + 2.2, y + 1.4), (x - 1.8, y - 0.6))):
        box("cafe.ct", (0.9, 0.9, 0.06), (cx_, cy_, 0.74), M["oak"])
        box("cafe.ctl", (0.08, 0.08, 0.74), (cx_, cy_, 0.37), M["oak_dk"])
        box("cafe.chair", (0.4, 0.4, 0.05), (cx_, cy_, 0.92), M["oak_dk"], rot=(0, 0, 0.3 * k))
    kit.light("cafe_lamp", "POINT", (x, y + 0.5, 2.6), 1.0, "#ffe6bf", size=0.5, shadow=False)
    # a satchel on the floor
    box("cafe.sat", (0.5, 0.18, 0.34), (x - 0.7, y - 0.5, 0.17), M["oak_dk"], bevel=0.05)


def build_kitchen(kit, M, ctx):
    x, y = KX, KY
    plane("kit.floor", (6, 5), (x, y, 0), M["floorw"])
    box("kit.back", (6, 0.2, 3), (x, y + 2.5, 1.5), M["wall_in"])
    box("kit.left", (0.2, 5, 3), (x - 3, y, 1.5), M["wall_in"])
    box("kit.right", (0.2, 5, 3), (x + 3, y, 1.5), M["wall_in"])
    box("kit.table", (1.8, 0.9, 0.08), (x, y + 0.6, 0.76), M["oak"], bevel=0.02)
    for sx in (-1, 1):
        box("kit.tl", (0.1, 0.1, 0.76), (x + sx * 0.8, y + 0.6, 0.38), M["oak_dk"])
    box("kit.lamp", (0.22, 0.22, 0.28), (x + 0.6, y + 0.9, 1.0), M["lamp"], bevel=0.05)
    box("kit.lamps", (0.05, 0.05, 0.22), (x + 0.6, y + 0.9, 0.86), M["iron"])
    box("kit.win", (0.9, 0.08, 1.0), (x - 1.6, y + 2.38, 1.7), kit.emit("#1c2a4a", 1.0, name="kit_window"))
    kit.light("kit_lamp", "POINT", (x + 0.6, y + 0.8, 1.35), 1.0, "#ffc680", size=0.15)
    kit.light("kit_fill", "POINT", (x, y - 1.5, 2.2), 1.0, "#ffd9a8", size=0.6, shadow=False)


# ------------------------------------------------------------------------------------------------ keys


GLYPHS = ("wheel", "crescent", "dots", "step", "leaf")


def make_key(kit, who, glyph, torso, M):
    """A brass key on a dark cord, hanging mid-chest, in front of the torso (torso-local: front at y -0.5)."""
    g = empty(f"{who}.key", (0, 0, 0), torso)
    br = kit.plastic("#c8a24a", 0.35, name=f"key_{who}")
    b = br.node_tree.nodes["Principled BSDF"]
    for k, v in (("Emission Color", kit.col("#ffcc66")), ("Emission", kit.col("#ffcc66"))):
        if k in b.inputs:
            b.inputs[k].default_value = v
    dk = M["cord"]
    ink = kit.plastic("#2a1a0c", 0.6, name="key_ink")
    # cord: a V from the shoulders to the bow
    for sx in (-1, 1):
        box(f"{who}.cord", (0.07, 0.05, 1.0), (sx * 0.22, -0.54, 1.5), dk, g, rot=(0, -sx * 0.32, 0))
    # bow (a disc facing -y), with a glyph inlaid
    yb = -0.6
    cyl(f"{who}.bow", 0.34, 0.1, (0, yb, 0.98), br, g, rot=(math.pi / 2, 0, 0), n=24)
    box(f"{who}.shaft", (0.13, 0.09, 0.66), (0, yb, 0.44), br, g, bevel=0.02)
    for k in range(2):
        box(f"{who}.tooth", (0.2, 0.09, 0.1), (0.1, yb, 0.2 + 0.17 * k), br, g, bevel=0.02)
    yg = yb - 0.07
    if glyph == "wheel":
        cyl(f"{who}.g", 0.26, 0.02, (0, yg, 0.98), ink, g, rot=(math.pi / 2, 0, 0), n=20)
        cyl(f"{who}.g", 0.19, 0.03, (0, yg - 0.004, 0.98), br, g, rot=(math.pi / 2, 0, 0), n=20)
        for ang in (0, 90):
            box(f"{who}.g", (0.4, 0.034, 0.06), (0, yg - 0.01, 0.98), ink, g, rot=(0, math.radians(ang), 0))
        cyl(f"{who}.g", 0.06, 0.04, (0, yg - 0.012, 0.98), ink, g, rot=(math.pi / 2, 0, 0), n=12)
    elif glyph == "crescent":
        cyl(f"{who}.g", 0.24, 0.02, (0, yg, 0.98), ink, g, rot=(math.pi / 2, 0, 0), n=20)
        cyl(f"{who}.g", 0.2, 0.03, (0.09, yg - 0.004, 1.0), br, g, rot=(math.pi / 2, 0, 0), n=20)
    elif glyph == "dots":
        for dx, dz in ((-0.14, 0.92), (0.14, 0.92), (0, 1.1)):
            cyl(f"{who}.g", 0.08, 0.02, (dx, yg, dz), ink, g, rot=(math.pi / 2, 0, 0), n=12)
    elif glyph == "step":
        for k in range(3):
            box(f"{who}.g", (0.14 * (3 - k) + 0.1, 0.02, 0.1), (-0.12 + 0.07 * (3 - k) * 0.5, yg, 0.84 + 0.14 * k), ink, g)
    else:   # leaf
        box(f"{who}.g", (0.26, 0.02, 0.26), (0, yg, 0.98), ink, g, rot=(0, 0.785, 0))
        box(f"{who}.g", (0.03, 0.03, 0.42), (0, yg - 0.01, 0.98), br, g, rot=(0, 0.3, 0))
    return g, b


def make_lifter_extras(kit, torso, M):
    """The second pair of arms: full size, out of the top of the shoulders behind the first pair, held straight up, hands
    open (palms up). Each is on a pivot so a bend at the waist can keep them upright."""
    skin = kit.plastic("#c9a27a", 0.5, name="lifter_skin_up")
    plum = kit.plastic("#5a2d4f", 0.6, name="lifter_plum_up")
    pivs = []
    for sx in (-1, 1):
        p = empty(f"lifter.up{sx}", (sx * 1.46, 0.46, 1.9), torso)
        # sleeve from the shoulder up, then the bare forearm and a flat open hand with the thumb out
        box("lifter.upsl", (0.98, 1.0, 1.3), (0, 0, 0.62), plum, p, bevel=0.08)
        box("lifter.upfa", (0.92, 0.95, 0.9), (0, 0, 1.75), skin, p, bevel=0.08)
        box("lifter.uphand", (1.05, 0.5, 0.34), (0, 0, 2.38), skin, p, bevel=0.08)
        for k in range(4):
            box("lifter.upfin", (0.17, 0.4, 0.3), (-0.4 + 0.27 * k, 0.0, 2.55), skin, p, bevel=0.05)
        pivs.append(p)
    # smock buttons down the front
    btn = M["btn"]
    for k in range(5):
        box("lifter.btn", (0.1, 0.05, 0.1), (0, -0.52, 1.82 - 0.36 * k), btn, torso)
    return pivs


# ------------------------------------------------------------------------------------------------ looks

# (sky, sky strength, sun elevation, azimuth, sun colour, sun power, fog colour, fog density, {light: watts})
LOOKS = {
    "day": ("#a9c8e0", 0.9, 46, 170, "#fff0d8", 2.7, "#c4d2dc", 0.0030, {}),
    "dawn": ("#d8c0b0", 0.8, 14, 100, "#ffc890", 2.4, "#d8c8bc", 0.0050, {}),
    "aft": ("#b4cce0", 0.85, 30, 120, "#ffe2b0", 2.6, "#c8d2d8", 0.0035, {}),
    "grey": ("#b4bcc4", 0.9, 38, 160, "#e8eaee", 1.4, "#b9bfc0", 0.0060, {}),
    "dusk": ("#9a8aae", 0.85, 6, 250, "#ff9a58", 2.6, "#8a7a8c", 0.0070, {}),
    "indark": ("#707880", 0.55, 8, 250, "#a0a8b8", 0.4, "#6c747c", 0.0100, {}),
    "night": ("#16203e", 0.4, 40, 220, "#8aa0ff", 1.2, "#1e2844", 0.0100, {}),
    "fog": ("#222c46", 0.45, 40, 220, "#8aa0ff", 0.9, "#2a3652", 0.0300, {}),
    "dawn2": ("#e4c8b4", 0.8, 10, 110, "#ffc088", 1.8, "#e0cdbb", 0.0050, {}),
    "noon": ("#aecbe2", 0.9, 56, 170, "#fff2dc", 2.8, "#c8d6e0", 0.0030, {}),
}

# interior lights by place and mood: watts for mill_fill, mill_door (daylight through the door window), stove, moon, moon2
MILL = {
    "in_day": dict(mill_fill=70, mill_door=900, stove=18, moon=0, moon2=0),
    "in_mem": dict(mill_fill=70, mill_door=900, stove=18, moon=0, moon2=0),
    "in_dim": dict(mill_fill=14, mill_door=140, stove=14, moon=0, moon2=0),
    "in_dark": dict(mill_fill=18, mill_door=260, stove=16, moon=0, moon2=0),
    "in_night": dict(mill_fill=7, mill_door=0, stove=16, moon=1.0, moon2=1.0),
    "in_dawn": dict(mill_fill=130, mill_door=500, stove=16, moon=0, moon2=0),
    "out": dict(mill_fill=0, mill_door=0, stove=0, moon=0, moon2=0),
}


def look_of(sid, n):
    """(exterior look, mill-interior mood) for a shot (n = the narration line it sits on)."""
    if sid in ("S11", "S74", "S58"):
        return "dusk", "out"
    if sid in ("S20", "S20b", "S59"):
        return "night", "out"
    if sid == "S57":
        return "day", "out"
    if sid in ("S05",):
        return "dawn", "out"
    if sid in ("S06",):
        return "dawn", "out"
    if 1 <= n <= 8 and sid not in ("S11",):
        return "day", "out"
    if n in (9, 10, 11, 12, 13, 14):
        return "aft", "in_mem"
    if 15 <= n <= 24:
        return "grey" if n >= 15 else "aft", "in_day"
    if n == 25:
        return "indark", "in_dark"
    if n in (26, 27, 28):
        return "indark", "in_dark"
    if n in (29, 30, 31, 32):
        return "night", "in_dim"
    if n == 33:
        return "night", "out"
    if n == 34:
        return "fog", "in_night"
    if 35 <= n <= 50:
        return "fog", "in_night"
    if n in (51, 52):
        return "fog", "in_night"
    if n in (53, 54, 55, 56, 57, 58):
        return "dawn2", "in_dawn"
    if n >= 59 and n <= 61:
        return "dawn2", "in_dawn"
    if n in (62, 63, 64):
        return "noon", "in_day"
    if n == 65:
        return "dawn2", "in_dawn"
    return "day", "out"


def build(kit, story, tl):
    ctx = {"story": story, "nmap": {s["id"]: s.get("n", 0) for s in story["shots"]}, "doors": {}}
    M = materials(kit)
    ctx["M"] = M
    kit.light("sun", "SUN", (0, 0, 20), 3.6, "#fff0d8")
    kit.LIGHTS["sun"]["light"].angle = math.radians(2.5)
    # interior lights, all steady; their gains are set per shot (only ever changing at a cut), the moon eases in over 2 s
    kit.light("mill_fill", "POINT", (MX - 0.3, MY + 0.4, 2.9), 1.0, "#ffe2b8", size=0.6, shadow=False)
    kit.light("mill_door", "SPOT", (MX, MY - 3.62, 1.7), 1.0, "#fff0d8", spot=40, blend=0.4, size=0.2)
    kit.aim(kit.LIGHTS["mill_door"]["obj"], (MX + 0.2, MY + 0.8, 1.0))
    kit.light("stove", "POINT", (MX - 1.5, MY + 0.0, 0.55), 1.0, "#ff9a48", size=0.3)
    kit.light("moon", "SPOT", (MX + 0.2, MY - 5.0, 2.2), 1.0, "#9fb4ff", spot=50, blend=0.6, size=0.4)
    kit.aim(kit.LIGHTS["moon"]["obj"], (MX + 0.2, MY - 0.1, 1.5))
    kit.light("moon2", "SPOT", (MX, MY + 4.9, 2.6), 1.0, "#9fb4ff", spot=60, blend=0.6, size=0.4)
    kit.aim(kit.LIGHTS["moon2"]["obj"], (MX + 0.2, MY - 0.8, 1.6))
    kit.light("rim", "POINT", (MX + 0.2, MY + 1.1, 3.0), 1.0, "#a8bcff", size=0.3, shadow=False)
    kit.light("torch", "SPOT", (MX + 0.4, MY - 5.6, 1.4), 1.0, "#fff0d0", spot=30, blend=0.35, size=0.1)
    kit.aim(kit.LIGHTS["torch"]["obj"], (MX + 0.4, MY + 3.06, 1.8))
    kit.light("keyglow", "POINT", (0, 0, -50), 1.0, "#ffcc66", size=0.2, shadow=False)
    kit.light("spilll", "POINT", (MX, MY - 4.2, 1.0), 1.0, "#ffb868", size=0.5, shadow=False)
    kit.light("mface", "POINT", (MX - 1.6, MY - 6.4, 2.2), 1.0, "#a8bcff", size=0.4, shadow=False)
    kit.light("lkey", "SPOT", (MX - 1.7, MY - 1.4, 0.35), 1.0, "#ffb070", spot=38, blend=0.6, size=0.3, shadow=False)
    kit.aim(kit.LIGHTS["lkey"]["obj"], (MX + 0.2, MY - 0.1, 2.0))
    kit.light("lfill", "POINT", (MX + 0.6, MY - 2.9, 1.3), 1.0, "#9fb4ff", size=0.5, shadow=False)
    build_marsh(kit, M, ctx)
    build_street(kit, M, ctx)
    build_shop(kit, M, ctx)
    build_mill(kit, M, ctx)
    build_cafe(kit, M, ctx)
    build_kitchen(kit, M, ctx)
    ctx["lazy"] = False
    ctx["keys"] = {}
    return ctx


# ------------------------------------------------------------------------------------------------ animate


def _cues(tl, name):
    return [c for c in tl["cues"] if c["name"] == name]


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


def track(cues, t, key=None, val=None, start=0.0):
    """The eased value at t from cues {"t", "to", "ramp"} (filtered by key == val)."""
    v = start
    for c in sorted((c for c in cues if key is None or c.get(key) == val), key=lambda c: c["t"]):
        if t < c["t"]:
            break
        r = c.get("ramp", 0.0)
        if r > 1e-6 and t < c["t"] + r:
            u = ss((t - c["t"]) / r)
            prev = v
            v = prev + (c["to"] - prev) * u
            return v
        v = c["to"]
    return v


def _sun_dir(el, az):
    e, a = math.radians(el), math.radians(az)
    return V((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)))


def _fog_nodes(kit):
    if FOG_NODES["built"]:
        return FOG_NODES["mul"], FOG_NODES["col"]
    mul, col = [], []
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        for nd in m.node_tree.nodes:
            if nd.type == "MATH" and nd.operation == "EXPONENT":
                src = nd.inputs[0].links[0].from_node if nd.inputs[0].links else None
                if src is not None and src.type == "MATH" and src.operation == "MULTIPLY":
                    mul.append(src)
            if nd.type == "MIX_SHADER" and len(nd.inputs[0].links) and len(nd.inputs[2].links) and nd.inputs[2].links[0].from_node.type == "EMISSION":
                col.append(nd.inputs[2].links[0].from_node)
    FOG_NODES.update(built=True, mul=mul, col=col)
    return mul, col


def _lazy(kit, story, tl, ctx):
    M = ctx["M"]
    for who, spec in story["cast"].items():
        if spec.get("key"):
            torso = bpy.data.objects.get(f"{who}.torso")
            if torso is not None:
                ctx["keys"][who] = make_key(kit, who, spec["key"], torso, M)
    mt = bpy.data.objects.get("me.torso")
    ctx["sack_me"] = box("sack_me", (1.2, 0.9, 1.6), (1.2, 0.2, 2.2), M["sack"], mt, bevel=0.2) if mt is not None else None
    wt = bpy.data.objects.get("win.torso")
    red = kit.plastic("#b4503e", 0.8, name="sailcloth")
    ctx["cloth"] = cyl("cloth", 0.4, 2.4, (1.55, -0.45, 0.6), red, wt, rot=(math.pi / 2, 0, 0.2), n=14) if wt is not None else None
    lt = bpy.data.objects.get("lifter.torso")
    ctx["lifter_up"] = make_lifter_extras(kit, lt, M) if lt is not None else []
    ctx["lazy"] = True


def animate(kit, story, tl, t, ctx):
    over = {}
    if not ctx["lazy"]:
        _lazy(kit, story, tl, ctx)
    shot = _shot(tl, t)
    sid = shot["id"]
    n = ctx["nmap"][sid]
    ext, mood = look_of(sid, n)
    if sid == "TEST":
        ext, mood = "fog", "in_night"
    sky, sky_s, el, az, scol, spow, fcol, fd, _ = LOOKS[ext]
    c = lambda h: kit.col(h)[:3]
    w = bpy.context.scene.world.node_tree.nodes["Background"]
    w.inputs["Color"].default_value = (*c(sky), 1)
    w.inputs["Strength"].default_value = sky_s
    sun = kit.LIGHTS["sun"]
    sun["obj"].rotation_euler = (V((0, 0, 0)) - _sun_dir(el, az)).to_track_quat("-Z", "Y").to_euler()
    sun["light"].color = c(scol)
    over["sun"] = spow / sun["base"]
    mul, cols = _fog_nodes(kit)
    for nd in mul:
        nd.inputs[1].default_value = -fd
    for nd in cols:
        nd.inputs["Color"].default_value = (*c(fcol), 1)
    # ---- interior mood
    ml = MILL[mood]
    over["mill_fill"] = ml["mill_fill"]
    over["mill_door"] = ml["mill_door"]
    over["stove"] = ml["stove"] if mood != "out" else 0.0
    moon_v = track(_cues(tl, "moon"), t, start=1.0 if mood == "in_night" and sid not in ("S45",) else 0.15)
    if sid == "TEST":
        moon_v = 1.0
    if mood != "in_night":
        moon_v = 0.0
    over["moon"] = ml["moon"] * moon_v * 220
    over["moon2"] = ml["moon2"] * moon_v * 70
    over["rim"] = 0.0
    over["lkey"] = 0.0
    over["lfill"] = 0.0
    ctx["moonpane"].hide_render = not (mood == "in_night" and moon_v > 0.02)
    mp = ctx["M"]["moonpane"].node_tree.nodes
    for nd in mp:
        if nd.type == "EMISSION":
            nd.inputs["Strength"].default_value = 0.9 * moon_v
    # the torch (L29 to L32): steady, lit before the shot begins
    over["torch"] = 900.0 if n in (29, 30, 31, 32) else 0.0
    # night-time rim for the creature: a cool light behind it, from the door side
    if n in (36, 37, 38, 39, 40, 41, 42) or sid in ("TEST", "S61", "S62"):
        over["rim"] = 200.0
        over["stove"] = 70.0
        over["lkey"] = 420.0
        over["lfill"] = 60.0
    # ---- spill of light on the marsh from an open door at night
    ctx["spill"].hide_render = not (sid in ("S20", "S20b", "S59"))
    ctx["doorglow"].hide_render = not (sid in ("S11", "S20", "S20b", "S59", "S74"))
    over["spilll"] = 160.0 if sid in ("S20", "S20b", "S59") else 0.0
    over["shoplamp"] = 90.0 if sid in ("S11", "S74", "S58") else 0.0
    over["mface"] = 260.0 if sid in ("S46", "S53", "S56", "S60", "S61", "S62", "S63", "S64") else 0.0
    # ---- doors
    dcues = _cues(tl, "door")
    for did, (piv, ang) in ctx["doors"].items():
        v = track(dcues, t, "id", did, 0.0)
        if did == "mill":
            frac = v
            if sid in ("S11", "S20", "S20b", "S59", "S74", "S79", "S76", "S77", "S78", "S69", "S70", "S71", "S72", "S80", "S66", "S67"):
                frac = 1.0
            if sid == "S75":
                frac = 1.0 - 0.7 * ss((t - shot["start"]) / max(0.5, shot["end"] - shot["start"]))
            if sid == "S68":
                frac = ss((t - shot["start"]) / 1.0)
            if sid in ("S64",):
                frac = ss((t - shot["start"] - 0.2) / 0.9)
            if sid in ("S65", "S66", "S67"):
                frac = 1.0
            if sid in ("S21", "S22", "S23", "S24", "S37", "S61", "S62", "S63", "S73", "S73b", "S81", "S82", "S64x"):
                frac = 0.0
            v = frac
        piv.rotation_euler = (0, 0, math.radians(ang) * v)
    if ctx.get("sack_me") is not None:
        ctx["sack_me"].hide_render = sid != "S19"
    if ctx.get("cloth") is not None:
        ctx["cloth"].hide_render = not (n in (54, 55, 56, 57))
    # ---- the scene's props by line
    ctx["scarf"].hide_render = n != 27
    ctx["scarf"].rotation_euler = (0, 0.08 * math.sin(t * 1.3), 0)
    for k, s_ in enumerate(ctx["sacks"]):
        s_.hide_render = not (n in (12, 13) or sid in ("S17",))
    # stools: mine turned to face Win (L19 on, to the west), later to face the door (L28 on)
    sw, sm = ctx["stool_win"], ctx["stool_me"]
    sw.location = (MX - 0.1, MY + 0.3, 0)
    sm.location = (MX + 0.9, MY + 0.3, 0)
    face_stones = math.radians(0)       # back plank at +y (behind the sitter), so the sitter faces -y?  see below
    sm.rotation_euler = (0, 0, math.radians(180))     # default: sitter faces +y, toward the stones
    if 19 <= n <= 27:
        sm.rotation_euler = (0, 0, math.radians(90))   # faces -x, toward Win
    if 28 <= n <= 64 and n != 62:
        sm.rotation_euler = (0, 0, math.radians(0))    # faces -y, the door
    if n >= 62 and n <= 64:
        sm.rotation_euler = (0, 0, math.radians(180))
    sw.rotation_euler = (0, 0, math.radians(180))
    # Win's stool is pushed back a little behind her on Thursday
    # ---- the clean patch: where, and whether
    pa = ctx["patch"]
    ppos = None
    if 20 <= n <= 22:
        ppos = (0.2, -0.1)
    elif n in (23, 24):
        ppos = (-0.9, -0.1)
    elif 25 <= n <= 39 or n == 51 or n == 52 or n == 65:
        ppos = (0.2, -0.1)
    elif 40 <= n <= 50:
        ppos = (0.05, -1.95)
    if sid == "TEST":
        ppos = (0.2, -0.1)
    pa.hide_render = ppos is None
    for ch in pa.children:
        ch.hide_render = ppos is None
    if ppos is not None:
        pa.location = (MX + ppos[0], MY + ppos[1], 0.045)
    hop = n in (30, 31, 32)
    for o in ctx["hopper"]:
        o.hide_render = hop
    # ---- the shadow cut-out
    ctx["shadow"].hide_render = True
    for grp, on in ((ctx["shadow_body"], n in (30, 31, 32)), (ctx["shadow_down"], n in (31, 32)), (ctx["shadow_up"], n == 32)):
        for o in grp:
            o.hide_render = not on
    ctx["shadow"].hide_render = False
    sc = 1.0 + (0.18 if n == 31 else 0.28 if n == 32 else 0.0)
    ctx["shadow"].scale = (sc, 1, sc)
    ctx["shadow"].location = (MX + 0.4, MY + 3.06, -0.3 * (sc - 1.0) * 2)
    # ---- flour in the air (interior day moods, never over the clean patch)
    air = mood in ("in_day", "in_mem", "in_dawn", "in_dim") and sid not in ("S21", "S22", "S23", "S24")
    for i, (sp, (fx, fy, fz, vz)) in enumerate(ctx["flecks"]):
        z = (fz - vz * t) % 3.2 + 0.2
        x = fx + 0.15 * math.sin(t * 0.4 + i)
        y = fy + 0.1 * math.cos(t * 0.3 + i * 1.7)
        if abs(x - 0.2) < 0.45 and abs(y + 0.1) < 0.45:
            x += 0.9
        sp.location = (MX + x, MY + y, z)
        sp.hide_render = not air
    # ---- keys: the glow, fading up over its ramp
    gl = _cues(tl, "glow")
    best = None
    for who, (g, b) in ctx["keys"].items():
        st = acting.state(tl, who, t)
        g.hide_render = st["hidden"]
        for ch in g.children_recursive:
            ch.hide_render = st["hidden"]
        v = track(gl, t, "who", who, 0.0)
        for k in ("Emission Strength",):
            if k in b.inputs:
                b.inputs[k].default_value = 2.6 * v
        if v > 0.01 and not st["hidden"] and (best is None or v > best[1]):
            best = (who, v, g)
    if best:
        bpy.context.view_layer.update()
        wp = best[2].matrix_world.translation
        # the glow light sits just in front of the key (toward the camera side, -y of the wearer)
        kit.LIGHTS["keyglow"]["obj"].location = (wp.x, wp.y - 0.35, wp.z + 0.25)
        over["keyglow"] = 24.0 * best[1]
    else:
        over["keyglow"] = 0.0
    # ---- the Lifter: the raised arms stay upright whatever the bend, and the bend at the waist is a cue
    lt = bpy.data.objects.get("lifter.torso")
    if lt is not None:
        bend = track(_cues(tl, "bend"), t, start=0.0)
        if n < 40 or sid in ("TEST",):
            bend = 0.0
        if n > 42 and sid not in ("S61", "S62", "S63"):
            bend = 0.0
        lt.rotation_euler = (math.radians(60) * bend, 0, 0)
        nk = bpy.data.objects.get("lifter.neck")
        if nk is not None:
            nk.rotation_euler = (nk.rotation_euler.x - math.radians(62) * bend, nk.rotation_euler.y, nk.rotation_euler.z)
        for p in ctx["lifter_up"]:
            p.rotation_euler = (-math.radians(60) * bend, 0, 0)
        near = n >= 40
        kit.aim(kit.LIGHTS["lkey"]["obj"], (MX + 0.05, MY - 1.7, 1.5) if near else (MX + 0.2, MY - 0.1, 2.0))
    return over
