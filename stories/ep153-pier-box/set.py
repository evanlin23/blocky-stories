"""ep153 "pier box": a sunny wooden fishing pier on a bright blue bay (weathered gold-gray planks, white rails, tall
pilings, gulls, little sailboats far off) with a small green lock-box on a post at its end; my bright one-car garage
with its door rolled up on a sunny street; Bea's office door. All far apart along x.

Light: one sun by day. Dusk (S11 on the pier; the garage from L27) changes only on a cut, read from the "shot" cue
(dusk 0/1): the sun dims, a low warm sun takes over, the sky deepens. The pier lamps and the garage's ceiling lights
are on and steady in every shot, so nothing switches.
The rule meter: the box's brass "1", and a corner copy (a green tile with a brass "1") on the camera in every shot
the box isn't big in ("shot" cue, tag 0/1). It never changes.
Cues: lid (o 0..1), c1 / c2 (p: the card's place, r: a rise offset), ch / cb (Hal's and Bea's cards), q (u: my
folded question, 0 held, 1 in the slot, 2 gone), bread (u), rod (r), bucket (b), donut (d), pizza (z).
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

W = {}
BX, BY = G.BOX
Z0, Z1 = G.BOX_Z0, G.BOX_Z1


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def sample(name, tl, t, defaults, smooth=()):
    """The cue track `name` at time t: every key holds from its cue; the keys in `smooth` ease over the cue's dur."""
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
            out = dict(cur)
            for k in smooth:
                out[k] = prev[k] + (cur[k] - prev[k]) * u
            return out
    return cur


def root_frame(who):
    """The character's root position and yaw (radians), without its scale."""
    r = bpy.data.objects.get(who)
    if r is None:
        return Vector((0, 0, -50)), 0.0
    m = r.matrix_world
    return m.translation.copy(), m.to_euler().z


def place(ob, who, local, rot=(0.0, 0.0, 0.0), scale=1.0):
    """Put `ob` at `local` (metres, the character's own frame: x to its left, -y in front, z up) round `who`."""
    p, yaw = root_frame(who)
    c, s = math.cos(yaw), math.sin(yaw)
    x, y, z = local
    ob.location = (p.x + c * x - s * y, p.y + s * x + c * y, p.z + z)
    ob.rotation_euler = (rot[0], rot[1], yaw + rot[2])
    ob.scale = (scale, scale, scale)


def hide(ob, h=True):
    ob.location = (0, 0, -80) if h else ob.location
    ob.hide_render = h


# ------------------------------------------------------------------------------------------------ the pier
def build_pier(kit):
    pl = kit.plastic
    water = pl("#2a9df4", 0.18, spec=0.5)
    kit.plane("bay", (900, 900), (0, 0, G.WATER_Z), water)
    deck = kit.texture("wood", 0.7, tint="#d9c49a", rough=0.8)
    x0 = -G.PIER_W / 2
    L = G.PIER_Y1 - G.PIER_Y0
    yc = (G.PIER_Y0 + G.PIER_Y1) / 2
    kit.box("deck", (G.PIER_W, L, 0.2), (0, yc, -0.1), deck)
    seam = pl("#8f7a58", 0.85)
    for k in range(int(L / 0.6)):   # plank seams across the deck, 1 cm proud
        kit.box(f"deck.seam{k}", (G.PIER_W, 0.025, 0.012), (0, G.PIER_Y0 + 0.3 + 0.6 * k, 0.006), seam)
    pile = pl("#8a7458", 0.8)
    for y in range(int(G.PIER_Y0), int(G.PIER_Y1) + 1, 3):
        for sx in (-1, 1):
            kit.cyl(f"pile{y}{sx}", 0.17, 3.0, (sx * (G.PIER_W / 2 - 0.15), y, -1.6), pile, n=10)
    white = pl("#f7f5ef", 0.55, spec=0.2)
    for sx in (-1, 1):
        x = sx * (G.PIER_W / 2 - 0.08)
        kit.box(f"rail{sx}.top", (0.1, L, 0.09), (x, yc, G.RAIL_H), white, bevel=0.02)
        kit.box(f"rail{sx}.mid", (0.06, L, 0.06), (x, yc, G.RAIL_H * 0.55), white)
        for k in range(int(L / 2.0) + 1):
            kit.box(f"rail{sx}.post{k}", (0.12, 0.12, G.RAIL_H + 0.05), (x, G.PIER_Y0 + 2.0 * k, G.RAIL_H / 2), white, bevel=0.02)
    kit.box("railn.top", (G.PIER_W, 0.1, 0.09), (0, G.PIER_Y1 - 0.08, G.RAIL_H), white, bevel=0.02)
    kit.box("railn.mid", (G.PIER_W, 0.06, 0.06), (0, G.PIER_Y1 - 0.08, G.RAIL_H * 0.55), white)
    for k in range(4):
        kit.box(f"railn.post{k}", (0.12, 0.12, G.RAIL_H + 0.05), (-2.92 + 1.95 * k, G.PIER_Y1 - 0.08, G.RAIL_H / 2), white, bevel=0.02)
    # the tall piling out in the water (Old Hal's "left of the post")
    px, py = G.POST
    kit.cyl("post", 0.3, 6.5, (px, py, G.WATER_Z + 3.25), pl("#7a6448", 0.8), n=14)
    kit.cyl("post.cap", 0.33, 0.12, (px, py, G.WATER_Z + 6.5), pl("#f7f5ef", 0.6), n=14)
    # lamps along the rails: gold globes, steady (lit the same in every shot)
    gold = kit.emit("#ffd27a", 2.2, "lampglow")
    dark = pl("#2f3a44", 0.5)
    for i, (x, y) in enumerate([(-2.92, 8.5), (2.92, 8.5), (-2.92, 1.5), (2.92, 2.5), (-2.92, -6.0), (2.92, -6.0)]):
        kit.cyl(f"lamp{i}.pole", 0.05, 3.0, (x, y, 1.5), dark, n=8)
        kit.sphere(f"lamp{i}.globe", 0.2, (x, y, 3.15), gold, seg=12)
    # the bait shack (west side), a striped awning reaching east over the deck
    sx_, sy_ = G.SHACK
    kit.box("shack", (2.2, 3.2, 2.8), (sx_ - 0.2, sy_, 1.4), pl("#5aa9c9", 0.7), bevel=0.04)
    kit.box("shack.roof", (2.6, 3.6, 0.18), (sx_ - 0.2, sy_, 2.9), pl("#f7f5ef", 0.6))
    kit.box("shack.window", (0.05, 1.6, 0.9), (sx_ + 0.92, sy_, 1.55), pl("#cfeaff", 0.2, spec=0.6))
    kit.box("shack.sill", (0.2, 1.8, 0.08), (sx_ + 0.98, sy_, 1.05), pl("#f7f5ef", 0.6))
    for k in range(6):
        c = "#e8433a" if k % 2 == 0 else "#f7f5ef"
        kit.box(f"awning{k}", (1.6, 0.6, 0.06), (sx_ + 1.65, sy_ - 1.5 + 0.6 * k, 2.42), pl(c, 0.7), rot=(0, math.radians(-14), 0))
    for k, y in enumerate((sy_ - 1.5, sy_ + 1.5)):
        kit.box(f"awning.pole{k}", (0.06, 0.06, 2.3), (sx_ + 2.38, y, 1.15), white)
    # crates and a coil of rope for clutter
    crate = kit.texture("wood", 1.4, tint="#c9a46a", rough=0.8)
    kit.box("crate1", (0.6, 0.6, 0.5), (2.3, -2.5, 0.25), crate, bevel=0.02)
    kit.box("crate2", (0.5, 0.5, 0.4), (2.25, -1.9, 0.2), crate, bevel=0.02)
    kit.cyl("rope", 0.28, 0.12, (-2.3, 10.6, 0.06), pl("#d8c08a", 0.9), n=16)
    kit.box("benchp.seat", (0.5, 1.8, 0.08), (2.55, 9.5, 0.48), crate)
    kit.box("benchp.back", (0.08, 1.8, 0.5), (2.78, 9.5, 0.78), crate)
    # the far shore behind the pier's start, and sailboats out on the bay
    kit.box("shore", (400, 60, 2.0), (0, G.PIER_Y0 - 30, G.WATER_Z + 0.6), pl("#e8d6a8", 0.9))
    kit.box("shore.green", (400, 40, 6.0), (0, G.PIER_Y0 - 48, G.WATER_Z + 3.0), pl("#5cb85a", 0.9))
    for i, (x, h) in enumerate([(-30, 6), (-16, 8), (-4, 7), (12, 9), (26, 6), (40, 8)]):
        kit.prop("bldg_2story" if i % 2 else "bldg_1story_gableroof", (x, G.PIER_Y0 - 38, G.WATER_Z + 6.0), rot=180, height=h)
    sail = pl("#fbfbf6", 0.6)
    hull = pl("#e8433a", 0.6)
    for i, (x, y, s) in enumerate([(-38, 70, 1.6), (-14, 110, 2.0), (22, 85, 1.8), (46, 130, 2.2), (-60, 140, 2.0),
                                   (60, 60, 1.4), (34, 40, 1.2), (-44, 34, 1.2)]):
        kit.box(f"boat{i}.hull", (2.4 * s, 0.8 * s, 0.5 * s), (x, y, G.WATER_Z + 0.25 * s), hull if i % 2 else pl("#f7f5ef", 0.6), bevel=0.1)
        kit.mesh_obj(f"boat{i}.sail", [(0, 0, 0), (1.1 * s, 0, 0), (0, 0, 3.2 * s)], [(0, 1, 2)], sail,
                     loc=(x - 0.4 * s, y, G.WATER_Z + 0.5 * s))
        kit.cyl(f"boat{i}.mast", 0.04 * s, 3.3 * s, (x - 0.42 * s, y, G.WATER_Z + 2.1 * s), pl("#8a7458", 0.7), n=6)


def build_box(kit):
    """The green lock-box on its post at the pier's end, facing south: a brass "1" plate on its front, a keyhole, a
    slot in the lid; the lid is hinged at the back (empty "lid", rotated about x)."""
    pl = kit.plastic
    green = pl("#2f9e5a", 0.45, spec=0.35)
    dkg = pl("#1d5e37", 0.5)
    brass = pl("#d9a441", 0.3, spec=0.8)
    ink = pl("#163f27", 0.5)
    w, d = G.BOX_W, G.BOX_D
    kit.box("boxpost", (0.16, 0.16, Z0), (BX, BY + 0.05, Z0 / 2), pl("#f7f5ef", 0.55), bevel=0.02)
    kit.box("boxbracket", (0.12, 0.4, 0.1), (BX, BY + 0.35, G.RAIL_H), pl("#f7f5ef", 0.55))
    # the body: four walls and a floor, open at the top (so a card can stand inside)
    th = 0.05
    h = Z1 - Z0
    zc = (Z0 + Z1) / 2
    kit.box("box.floor", (w, d, th), (BX, BY, Z0 + th / 2), green)
    kit.box("box.front", (w, th, h), (BX, BY - d / 2 + th / 2, zc), green, bevel=0.015)
    kit.box("box.back", (w, th, h), (BX, BY + d / 2 - th / 2, zc), green, bevel=0.015)
    for sx in (-1, 1):
        kit.box(f"box.side{sx}", (th, d, h), (BX + sx * (w / 2 - th / 2), BY, zc), green, bevel=0.015)
    kit.box("box.inside", (w - 2 * th - 0.01, d - 2 * th - 0.01, 0.01), (BX, BY, Z0 + th + 0.005), pl("#174a2c", 0.8))
    kit.box("box.band", (w + 0.03, d + 0.03, 0.05), (BX, BY, Z0 + 0.06), dkg, bevel=0.01)
    # the brass "1" plate on the front, 1.5 cm proud, and its numeral 1 cm proud of the plate
    fy = BY - d / 2
    kit.box("box.plate", (0.3, 0.03, 0.32), (BX, fy - 0.015, zc + 0.01), brass, bevel=0.02)
    kit.box("box.one.stem", (0.065, 0.02, 0.24), (BX + 0.012, fy - 0.035, zc + 0.01), ink, bevel=0.006)
    kit.box("box.one.flag", (0.075, 0.02, 0.05), (BX - 0.03, fy - 0.035, zc + 0.1), ink, rot=(0, math.radians(-35), 0), bevel=0.006)
    kit.box("box.one.base", (0.15, 0.02, 0.045), (BX + 0.012, fy - 0.035, zc - 0.105), ink, bevel=0.006)
    for sx in (-1, 1):
        for sz in (-1, 1):
            kit.cyl(f"box.rivet{sx}{sz}", 0.015, 0.02, (BX + sx * 0.12, fy - 0.035, zc + 0.01 + sz * 0.13), brass,
                    rot=(math.pi / 2, 0, 0), n=8)
    # the lid, hinged along the top back edge, with a slot through it and a brass keyhole on its front lip
    hinge = kit.empty("lid", (BX, BY + d / 2, Z1))
    W["lid"] = hinge
    lt = 0.07
    ld = d + 0.04
    sw, sd = 0.4, 0.05          # the slot
    yc_ = -ld / 2 + 0.02        # lid centre (y, local to the hinge)
    sy0 = yc_ - 0.02            # slot centre a little forward of the middle
    front_d = (sy0 - sd / 2) - (yc_ - ld / 2)
    back_d = (yc_ + ld / 2) - (sy0 + sd / 2)
    kit.box("lid.front", (w + 0.04, front_d, lt), (0, yc_ - ld / 2 + front_d / 2, lt / 2), green, hinge, bevel=0.012)
    kit.box("lid.back", (w + 0.04, back_d, lt), (0, yc_ + ld / 2 - back_d / 2, lt / 2), green, hinge, bevel=0.012)
    side_w = (w + 0.04 - sw) / 2
    for sx in (-1, 1):
        kit.box(f"lid.side{sx}", (side_w, sd + 0.002, lt), (sx * (sw / 2 + side_w / 2), sy0, lt / 2), green, hinge)
    kit.box("lid.slotin", (sw, sd, 0.01), (0, sy0, -0.01), pl("#0f2a18", 0.9), hinge)
    kit.box("lid.lip", (w + 0.04, 0.03, 0.1), (0, yc_ - ld / 2 - 0.0, -0.02), dkg, hinge, bevel=0.01)
    kit.cyl("lid.keyhole", 0.03, 0.02, (0.24, yc_ - ld / 2 - 0.02, -0.02), brass, hinge, rot=(math.pi / 2, 0, 0), n=12)
    kit.box("lid.keyslot", (0.012, 0.01, 0.035), (0.24, yc_ - ld / 2 - 0.032, -0.03), pl("#2a1d10", 0.6), hinge)
    for sx in (-1, 1):
        kit.cyl(f"lid.hinge{sx}", 0.02, 0.12, (sx * 0.22, 0.0, 0.0), brass, hinge, rot=(0, math.pi / 2, 0), n=10)


# ------------------------------------------------------------------------------------------------ cards and props
def scribble(kit, name, parent, slant, rnd, width=0.36, lines=3, big_last=False, ink=None):
    """Blue handwriting that's never words: each word a zigzag of thin strokes, upright or slanted hard right.
    It sits 1 cm proud of the card's front (local -y)."""
    ink = ink or kit.plastic("#3a7bff", 0.5)
    lh = 0.07
    y = -0.012
    top = 0.075
    for li in range(lines):
        x = -width / 2
        z = top - li * lh
        k = 0
        while x < width / 2 - 0.04:
            n = rnd.randint(3, 6)
            last = big_last and li == lines - 1 and x > 0.0
            sc = 1.5 if last else 1.0
            for j in range(n):
                hgt = (0.032 if j % 2 == 0 else 0.026) * sc
                ang = slant + (0.45 if j % 2 == 0 else -0.45)
                kit.box(f"{name}.s{li}.{k}.{j}", (0.007 * sc, 0.006, hgt), (x + 0.008 * j * sc, y, z + (0.0 if not last else 0.008)),
                        ink, parent, rot=(0, ang, 0))
            if last:
                kit.box(f"{name}.u{li}.{k}", (0.008 * n * sc + 0.02, 0.006, 0.006), (x + 0.004 * n * sc, y, z - 0.03), ink, parent,
                        rot=(0, -0.08 if slant == 0 else 0.0, 0))
            x += 0.008 * n * sc + 0.03
            k += 1
            if last:
                break


def build_card(kit, name, slant, seed, size=(0.42, 0.3), big_last=False):
    cream = kit.plastic("#fbf3df", 0.75, spec=0.1)
    root = kit.empty(name, (0, 0, -80))
    kit.box(f"{name}.card", (size[0], 0.008, size[1]), (0, 0, 0), cream, root, bevel=0.004)
    kit.box(f"{name}.rule", (size[0] - 0.04, 0.009, 0.006), (0, -0.001, size[1] / 2 - 0.05), kit.plastic("#f2a0a8", 0.7), root)
    scribble(kit, name, root, slant, random.Random(seed), width=size[0] - 0.08, lines=3, big_last=big_last)
    noshadow(root)
    return root


def build_props(kit):
    pl = kit.plastic
    W["c1"] = build_card(kit, "card1", 0.0, 11, big_last=True)
    W["c2"] = build_card(kit, "card2", 0.62, 12)
    W["ch"] = build_card(kit, "cardh", 0.0, 13, size=(0.34, 0.24))
    W["cb"] = build_card(kit, "cardb", 0.0, 14, size=(0.34, 0.24))
    # my folded question
    q = kit.empty("question", (0, 0, -80))
    kit.box("question.paper", (0.22, 0.012, 0.14), (0, 0, 0), pl("#fbfbf6", 0.8), q, bevel=0.003)
    kit.box("question.fold", (0.22, 0.014, 0.004), (0, -0.001, 0.0), pl("#d8d2c0", 0.8), q)
    W["q"] = q
    # bread for the gulls
    W["bread"] = kit.box("bread", (0.12, 0.09, 0.07), (0, 0, -80), pl("#e0a85a", 0.8), bevel=0.02)
    # the gulls over the east rail (S04): white bodies, grey wings, flapping slowly
    W["gulls"] = []
    for i, (x, y, z) in enumerate([(3.6, 6.4, 3.2), (4.4, 7.6, 3.8), (3.3, 8.6, 2.9), (5.4, 5.6, 4.3)]):
        g = kit.empty(f"gull{i}", (x, y, z))
        kit.box(f"gull{i}.body", (0.16, 0.42, 0.16), (0, 0, 0), pl("#fbfbf6", 0.6), g, bevel=0.05)
        kit.box(f"gull{i}.head", (0.13, 0.14, 0.13), (0, -0.25, 0.07), pl("#fbfbf6", 0.6), g, bevel=0.04)
        kit.box(f"gull{i}.beak", (0.03, 0.09, 0.03), (0, -0.35, 0.06), pl("#f2b632", 0.6), g)
        wings = []
        for s_ in (-1, 1):
            wg = kit.empty(f"gull{i}.wing{s_}", (s_ * 0.07, 0, 0.04), g)
            kit.box(f"gull{i}.wingm{s_}", (0.5, 0.2, 0.025), (s_ * 0.25, 0, 0), pl("#c9ced6", 0.6), wg)
            kit.box(f"gull{i}.tip{s_}", (0.14, 0.14, 0.026), (s_ * 0.55, 0.02, 0), pl("#3a3f48", 0.6), wg)
            wings.append((wg, s_))
        noshadow(g)
        W["gulls"].append((g, wings, i))
    # Hal's rod and line
    rod = kit.empty("rod", (0, 0, -80))
    kit.cyl("rod.pole", 0.018, 2.6, (0, -1.3, 0), pl("#2f3a44", 0.5), rod, rot=(math.pi / 2, 0, 0), n=8)
    kit.cyl("rod.reel", 0.05, 0.06, (0.05, -0.15, -0.04), pl("#cfd2d6", 0.4, spec=0.7), rod, rot=(0, math.pi / 2, 0), n=10)
    W["rod"] = rod
    W["line"] = kit.cyl("rod.line", 0.004, 1.0, (0, 0, -80), pl("#f7f5ef", 0.5), n=6)
    W["bobber"] = kit.sphere("bobber", 0.07, (0, 0, -80), pl("#e8433a", 0.5), seg=10)
    noshadow(rod)
    # Hal's bucket with six fish standing up in it
    bk = kit.empty("bucket", (0, 0, -80))
    kit.cyl("bucket.pail", 0.24, 0.3, (0, 0, 0), pl("#cfd8e0", 0.4, spec=0.6), bk, n=18, r2=0.27)
    kit.cyl("bucket.water", 0.24, 0.01, (0, 0, 0.12), pl("#4aa8f0", 0.3), bk, n=18)
    fish = pl("#9fb6c8", 0.35, spec=0.6)
    fin = pl("#5f7a90", 0.5)
    for k in range(6):
        a = 2 * math.pi * k / 6
        fx, fy = 0.13 * math.cos(a), 0.11 * math.sin(a)
        kit.box(f"fish{k}.body", (0.08, 0.05, 0.26), (fx, fy, 0.2), fish, bk, rot=(0.15 * math.sin(a), 0.2 * math.cos(a), 0), bevel=0.02)
        kit.box(f"fish{k}.tail", (0.12, 0.02, 0.06), (fx, fy, 0.35), fin, bk, rot=(0.15 * math.sin(a), 0.2 * math.cos(a), 0))
    kit.box("bucket.handle", (0.5, 0.02, 0.02), (0, 0, 0.32), pl("#8a8d90", 0.4), bk)
    W["bucket"] = bk
    noshadow(bk)
    # Bea's big pink donut
    dn = kit.empty("donut", (0, 0, -80))
    dough = pl("#e0a85a", 0.7)
    icing = pl("#ff7ab8", 0.5)
    for k in range(14):
        a = 2 * math.pi * k / 14
        kit.box(f"donut.d{k}", (0.12, 0.12, 0.12), (0.16 * math.cos(a), 0, 0.16 * math.sin(a)), dough, dn, rot=(0, -a, 0), bevel=0.04)
        kit.box(f"donut.i{k}", (0.11, 0.03, 0.11), (0.16 * math.cos(a), -0.06, 0.16 * math.sin(a)), icing, dn, rot=(0, -a, 0), bevel=0.02)
    rnd = random.Random(5)
    for k in range(16):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0.12, 0.2)
        kit.box(f"donut.sp{k}", (0.03, 0.01, 0.012), (r * math.cos(a), -0.081, r * math.sin(a)),
                pl(["#3a7bff", "#ffd23f", "#f7f5ef"][k % 3], 0.5), dn, rot=(0, rnd.uniform(0, 3), 0))
    W["donut"] = dn
    noshadow(dn)
    # Ty's pizza: an open box held flat, the lid up behind
    pz = kit.empty("pizza", (0, 0, -80))
    card = pl("#d8b27a", 0.8)
    kit.box("pizza.base", (0.56, 0.56, 0.05), (0, 0, 0), card, pz)
    kit.box("pizza.lid", (0.56, 0.02, 0.34), (0, 0.25, 0.12), card, pz, rot=(math.radians(-55), 0, 0))
    kit.cyl("pizza.pie", 0.25, 0.03, (0, 0, 0.04), pl("#f2b84a", 0.7), pz, n=24)
    kit.cyl("pizza.sauce", 0.22, 0.032, (0, 0, 0.046), pl("#f2c05a", 0.7), pz, n=24)
    for k, (x, y) in enumerate([(0.1, 0.05), (-0.08, 0.1), (-0.05, -0.1), (0.12, -0.09), (0.0, 0.0), (-0.15, -0.01)]):
        kit.cyl(f"pizza.pep{k}", 0.035, 0.01, (x, y, 0.065), pl("#c8352e", 0.6), pz, n=12)
    W["pizza"] = pz
    noshadow(pz)


# ------------------------------------------------------------------------------------------------ the garage
def build_garage(kit):
    pl = kit.plastic
    gx = G.GARAGE[0]
    w, d, h = G.G_W, G.G_D, G.G_H
    wall = pl("#cfd4d8", 0.85, spec=0.05)
    kit.box("g.floor", (w, d, 0.1), (gx, d / 2, -0.05), kit.texture("concrete", 0.6, tint="#e2e2dc"))
    kit.box("g.wallw", (0.2, d, h), (gx - w / 2 - 0.1, d / 2, h / 2), wall)
    kit.box("g.walle", (0.2, d, h), (gx + w / 2 + 0.1, d / 2, h / 2), wall)
    kit.box("g.walln", (w + 0.4, 0.2, h), (gx, d + 0.1, h / 2), wall)
    kit.box("g.ceil", (w + 0.4, d + 0.2, 0.15), (gx, d / 2, h + 0.075), kit.emit("#e6e9ec", 0.55, "gceil"))
    side = (w - G.DOOR_W) / 2
    fw = pl("#f2efe6", 0.7)
    for sx in (-1, 1):
        kit.box(f"g.front{sx}", (side + 0.2, 0.25, h), (gx + sx * (G.DOOR_W / 2 + side / 2 + 0.1), -0.12, h / 2), fw)
        kit.box(f"g.jamb{sx}", (0.12, 0.3, G.DOOR_H), (gx + sx * (G.DOOR_W / 2 + 0.06), -0.12, G.DOOR_H / 2), pl("#ffffff", 0.6))
    kit.box("g.header", (w + 0.4, 0.25, h - G.DOOR_H + 0.2), (gx, -0.12, (h + G.DOOR_H) / 2 + 0.05), fw)
    kit.box("g.roll", (G.DOOR_W, 0.5, 0.4), (gx, 0.4, G.DOOR_H + 0.15), pl("#e6e8ea", 0.6))
    kit.box("g.roofeave", (w + 1.2, d + 1.4, 0.25), (gx, d / 2 - 0.3, h + 0.28), pl("#7a4a3a", 0.8))
    # outside walls of the house beside the garage
    kit.box("house.w", (6.0, 0.3, 5.5), (gx - w / 2 - 3.2, 0.2, 2.75), pl("#f2d38a", 0.85))
    kit.box("house.e", (6.0, 0.3, 5.5), (gx + w / 2 + 3.2, 0.2, 2.75), pl("#f2d38a", 0.85))
    for sx in (-1, 1):
        kit.box(f"house.win{sx}", (1.4, 0.05, 1.2), (gx + sx * (w / 2 + 3.0), 0.02, 1.8), pl("#9ed4f0", 0.2, spec=0.6))
        kit.box(f"house.winf{sx}", (1.6, 0.04, 1.4), (gx + sx * (w / 2 + 3.0), 0.04, 1.8), pl("#ffffff", 0.6))
    # ceiling lights: two panels, always on
    lamp = kit.emit("#fff6e0", 3.0, "gpanel")
    for k, y in enumerate((2.4, 5.8)):
        kit.box(f"g.panel{k}", (1.4, 0.4, 0.04), (gx, y, h - 0.02), lamp)
        lt = kit.light(f"glight{k}", "AREA", (gx, y, h - 0.15), 260, "#fff1dc", size=1.6, shadow=True)
        lt.rotation_euler = (0, 0, 0)
    # the workbench on the north wall, a pegboard, a toolbox, a lamp
    bx, by = G.BENCH
    hon = kit.texture("wood", 1.2, tint="#e0b278", rough=0.6)
    kit.box("bench.top", (G.BENCH_L, 0.75, 0.08), (bx, by, G.BENCH_Z - 0.04), hon, bevel=0.01)
    for sx in (-1, 1):
        kit.box(f"bench.leg{sx}", (0.08, 0.6, G.BENCH_Z - 0.08), (bx + sx * (G.BENCH_L / 2 - 0.1), by, (G.BENCH_Z - 0.08) / 2), pl("#8a5a34", 0.7))
    kit.box("bench.shelf", (G.BENCH_L - 0.2, 0.6, 0.05), (bx, by, 0.3), pl("#a87a48", 0.7))
    kit.box("peg", (G.BENCH_L, 0.04, 1.1), (bx, d - 0.02, 1.75), pl("#c8a878", 0.8))
    for k in range(5):
        kit.box(f"peg.tool{k}", (0.06, 0.03, 0.4), (bx - 1.0 + 0.5 * k, d - 0.06, 1.8), pl(["#e8433a", "#3a7bff", "#2f3a44"][k % 3], 0.5))
    kit.box("toolbox", (0.5, 0.3, 0.28), (bx + 0.9, by + 0.1, G.BENCH_Z + 0.14), pl("#e8433a", 0.5), bevel=0.02)
    kit.box("cardrest", (0.95, 0.06, 0.06), ((G.C1B[0] + G.C2B[0]) / 2, G.C1B[1] + 0.12, G.BENCH_Z + 0.03), pl("#a87a48", 0.7))
    # the bike under its sheet: a tall draped shape, one red wheel edge showing below at the front
    kx, ky = G.BIKE
    red = pl("#e8433a", 0.45, spec=0.4)
    for k, yy in enumerate((ky - 1.05, ky + 1.05)):
        kit.cyl(f"bike.wheel{k}", 0.46, 0.06, (kx, yy, 0.46), red, rot=(0, math.pi / 2, 0), n=28)
        kit.cyl(f"bike.tire{k}", 0.48, 0.05, (kx, yy, 0.48), pl("#2a2a2e", 0.7), rot=(0, math.pi / 2, 0), n=28)
    sheet = pl("#9aa0a6", 0.9, spec=0.05)
    kit.box("sheet.body", (0.6, 2.9, 1.25), (kx, ky, 1.25), sheet, bevel=0.22)
    kit.box("sheet.bars", (0.95, 0.4, 0.35), (kx, ky + 1.05, 1.9), sheet, bevel=0.14)
    kit.box("sheet.seat", (0.45, 0.6, 0.3), (kx, ky - 0.8, 1.95), sheet, bevel=0.12)
    kit.box("sheet.hem", (0.66, 2.95, 0.12), (kx, ky, 0.66), pl("#8a9096", 0.9), bevel=0.04)
    # the street: sidewalk, road, houses across
    kit.box("g.drive", (G.DOOR_W + 0.4, 3.0, 0.06), (gx, -1.5, -0.03), kit.texture("concrete", 0.5, tint="#e8e6e0"))
    kit.box("g.walk", (80, 2.0, 0.08), (gx, -4.0, -0.02), kit.texture("concrete", 0.5, tint="#dcdad4"))
    kit.box("g.road", (80, 9.0, 0.06), (gx, -9.5, -0.06), kit.texture("asphalt", 0.4, tint="#9a9ea6"))
    kit.plane("g.lawn", (90, 50), (gx, 20.0, -0.07), pl("#5cc45a", 0.9, spec=0.05))
    for i, x in enumerate((-16, -6, 4, 14)):
        kit.prop("sub_building_type_a" if i % 2 else "sub_building_type_c", (gx + x, -18.0, 0), rot=180, height=6.0)
    for i, x in enumerate((-11, 9)):
        kit.prop("sub_tree_large", (gx + x, -14.5, 0), height=6.0, tint="#d4f0c4")
    for i, x in enumerate((-8.5, 8.5)):
        kit.cyl(f"g.slamp{i}", 0.06, 3.6, (gx + x, -5.2, 1.8), pl("#2f3a44", 0.5), n=8)
        kit.sphere(f"g.slampg{i}", 0.2, (gx + x, -5.2, 3.7), kit.emit("#ffd27a", 2.2, "lampglow"), seg=12)


def build_office(kit):
    pl = kit.plastic
    ox, oy = G.OFFICE
    kit.box("o.wall", (14, 0.3, 7), (ox, oy + 0.2, 3.5), kit.texture("brick", 1.0, tint="#e8b8a0"))
    kit.box("o.door", (1.3, 0.1, 2.5), (ox - 0.9, oy + 0.02, 1.25), pl("#3a7bff", 0.5))
    kit.box("o.doorf", (1.5, 0.08, 2.65), (ox - 0.9, oy + 0.06, 1.3), pl("#f7f5ef", 0.6))
    kit.box("o.knob", (0.06, 0.06, 0.06), (ox - 0.45, oy - 0.06, 1.15), pl("#d9a441", 0.3, spec=0.8))
    for sx in (-1, 1):
        kit.box(f"o.win{sx}", (1.6, 0.05, 1.4), (ox + 1.4 + sx * 0.0 + (2.2 if sx > 0 else 0), oy + 0.02, 1.8), pl("#9ed4f0", 0.2, spec=0.6))
    kit.box("o.walk", (14, 6, 0.06), (ox, oy - 3.0, -0.03), kit.texture("concrete", 0.5, tint="#e8e6e0"))
    kit.plane("o.ground", (60, 40), (ox, oy - 10, -0.07), pl("#5cc45a", 0.9, spec=0.05))
    kit.prop("plant_1", (ox - 2.1, oy - 0.4, 0), height=1.1)
    kit.prop("plant_1", (ox + 0.4, oy - 0.4, 0), height=1.0)
    kit.box("o.awning", (2.2, 0.9, 0.08), (ox - 0.9, oy - 0.35, 2.85), pl("#ffd23f", 0.6), rot=(math.radians(10), 0, 0))


# ------------------------------------------------------------------------------------------------ the rule tag
def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    edge = kit.emit("#123a22", 0.7, "tagedge")
    tile = kit.emit("#2f9e5a", 0.85, "tagtile")
    brass = kit.emit("#e8b44a", 0.95, "tagbrass")
    ink = kit.emit("#123a22", 0.7, "tagink")

    def b(name, size, loc, mat, rot=0.0):
        ob = kit.box(name, size, loc, mat, root, rot=(0, 0, rot))
        noshadow(ob)
        return ob

    b("tag.edge", (1.0, 1.0, 0.006), (0, 0, 0), edge)
    b("tag.tile", (0.92, 0.92, 0.006), (0, 0, 0.007), tile)
    b("tag.slot", (0.5, 0.06, 0.006), (0, 0.36, 0.014), ink)
    b("tag.plate", (0.52, 0.56, 0.006), (0, -0.06, 0.014), brass)
    b("tag.stem", (0.11, 0.42, 0.006), (0.02, -0.06, 0.021), ink)
    b("tag.flag", (0.13, 0.08, 0.006), (-0.05, 0.1, 0.021), ink, rot=math.radians(35))
    b("tag.base", (0.26, 0.07, 0.006), (0.02, -0.25, 0.021), ink)


# ------------------------------------------------------------------------------------------------ build / animate
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    sun = kit.light("sun", "SUN", (18, -27, 51), 1.0, "#fff1d6", size=0.06)
    sun.data.angle = 0.05
    kit.aim(sun, (0, 0, 0))
    fill = kit.light("fill", "SUN", (-10, -30, 30), 1.0, "#e8f0ff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    dusk = kit.light("dusk", "SUN", (-60, -10, 12), 1.0, "#ffb27a", size=0.1)
    dusk.data.angle = 0.1
    kit.aim(dusk, (0, 0, 0))
    # a soft gold key from the lamp beside the box (steady in every shot)
    lk = kit.light("boxlamp", "AREA", (BX - 1.5, BY - 2.2, 3.0), 120, "#ffd9a0", size=1.5, shadow=False)
    kit.aim(lk, (BX - 0.6, BY, 1.4))
    build_pier(kit)
    build_box(kit)
    build_props(kit)
    build_garage(kit)
    build_office(kit)
    build_tag(kit)
    return {}


DAY_SKY = (0.13, 0.45, 1.0)
DUSK_SKY = (0.10, 0.14, 0.42)


def _first_frame(kit, story):
    """v3 draws no hats or vests, so Hal's bucket hat and fishing vest, Bea's earrings and my blue pen are built here."""
    W["inited"] = True
    top = 1.15   # faces_v3.HEAD3_H / 2
    pl = kit.plastic
    hh = bpy.data.objects.get("hal.headg")
    if hh is not None:
        c = pl("#c9b27a", 0.9)
        kit.cyl("hal.crown", 1.5, 0.75, (0, 0.05, top + 0.25), c, hh, n=24, r2=1.3)
        kit.cyl("hal.band", 1.52, 0.16, (0, 0.05, top + 0.0), pl("#5a6a3a", 0.8), hh, n=24)
        kit.cyl("hal.brim", 2.1, 0.08, (0, 0.0, top - 0.1), c, hh, n=28, r2=2.0)
    ht = bpy.data.objects.get("hal.torso")
    if ht is not None:
        v = pl("#6f7a3a", 0.8)
        for sx in (-1, 1):
            kit.box(f"hal.vest{sx}", (0.85, 0.06, 1.85), (sx * 0.55, -0.53, 1.02), v, ht, bevel=0.03)
            kit.box(f"hal.pocket{sx}", (0.5, 0.06, 0.4), (sx * 0.55, -0.58, 0.6), pl("#5a6430", 0.8), ht, bevel=0.02)
        kit.box("hal.vestback", (2.04, 1.06, 1.85), (0, 0.02, 1.02), v, ht, bevel=0.05)
    bh = bpy.data.objects.get("bea.headg")
    if bh is not None:
        gold = pl("#f2c84a", 0.3, spec=0.8)
        for sx in (-1, 1):
            kit.sphere(f"bea.ear{sx}", 0.16, (sx * 1.48, -0.1, -0.55), gold, bh, seg=10)
    mt = bpy.data.objects.get("me.torso")
    if mt is not None:   # my blue pen with its chewed white cap, clipped to my left chest pocket
        kit.box("me.pocket", (0.62, 0.06, 0.5), (0.5, -0.53, 1.35), pl("#f2c22f", 0.6), mt, bevel=0.03)
        kit.cyl("me.pen", 0.07, 0.95, (0.32, -0.6, 1.62), pl("#3a7bff", 0.4, spec=0.5), mt, n=10)
        kit.cyl("me.pencap", 0.08, 0.28, (0.32, -0.6, 2.0), pl("#f7f5ef", 0.6), mt, n=10)
        kit.box("me.penclip", (0.05, 0.04, 0.3), (0.32, -0.69, 1.9), pl("#cfd2d6", 0.3, spec=0.8), mt)
        kit.box("me.penchew", (0.1, 0.1, 0.06), (0.32, -0.6, 2.15), pl("#e0ded6", 0.8), mt, rot=(0.3, 0.4, 0))


def hand_of(who):
    """The world position of whichever of `who`'s hands is higher (the raised one)."""
    best = None
    for sx in (-1, 1):
        h = bpy.data.objects.get(f"{who}.hand{sx}")
        if h is not None:
            p = h.matrix_world.translation
            if best is None or p.z > best.z:
                best = p.copy()
    if best is None:   # no rig hands (the lints' stand-in scene): about hand height at the root
        best = root_frame(who)[0] + Vector((0, 0, 1.0))
    return best


# my cards' places round my raised hand, in my own frame (x to my left = screen right when I face the camera, -y in
# front, z up), with a small turn (radians about z): 1 one card on the palm, 2 and 3 card one and card two fanned
# (card one on the screen's left), 4 card one held up by the pen on my chest
SLOTS = {1: ((0.0, -0.1, 0.26), 0.0), 2: ((-0.25, -0.1, 0.26), 0.1), 3: ((0.2, -0.13, 0.29), -0.1),
         4: ((0.06, -0.1, 0.24), 0.0)}


def place_at_hand(ob, who, local, turn):
    hp = hand_of(who)
    p0, yaw = root_frame(who)
    c, s = math.cos(yaw), math.sin(yaw)
    x, y, z = local
    ob.location = (hp.x + c * x - s * y, hp.y + s * x + c * y, hp.z + z)
    ob.rotation_euler = (0, 0, yaw + turn)


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    sh = sample("shot", tl, t, {"tag": 1.0, "dusk": 0.0})
    dusk = sh["dusk"] > 0.5
    gains = {"sun": 0.5 if dusk else 4.2, "fill": 0.45 if dusk else 1.2, "dusk": 2.4 if dusk else 0.0,
             "boxlamp": 1.0, "glight0": 1.0, "glight1": 1.0}
    bg = bpy.context.scene.world.node_tree.nodes.get("Background")
    if bg is not None:
        c = DUSK_SKY if dusk else DAY_SKY
        bg.inputs["Color"].default_value = (*c, 1.0)
    W["tag"].hide_render = sh["tag"] < 0.5
    for ob in W["tag"].children_recursive:
        ob.hide_render = sh["tag"] < 0.5
    # the lid
    o = sample("lid", tl, t, {"o": 0.0}, smooth=("o",))["o"]
    W["lid"].rotation_euler = (math.radians(-105) * o, 0, 0)
    bpy.context.view_layer.update()
    # my cards
    for nm in ("c1", "c2"):
        cs = sample(nm, tl, t, {"p": 0, "r": 0.0}, smooth=("r",))
        ob = W[nm]
        p = int(round(cs["p"]))
        if p == 0:
            ob.location = (0, 0, -80)
            continue
        if p in SLOTS:
            loc, turn = SLOTS[p]
            place_at_hand(ob, "me", (loc[0], loc[1], loc[2] - 0.55 * cs["r"]), turn)
        elif p == 5:   # standing in the open box, its top half above the rim
            ob.location = (BX + (0.08 if nm == "c2" else -0.08), BY - 0.02, Z1 + 0.02)
            ob.rotation_euler = (math.radians(-8), 0, 0)
        elif p in (7, 8):
            cx, cy = G.C1B if p == 7 else G.C2B
            ob.location = (cx, cy, G.BENCH_Z + 0.13)
            ob.rotation_euler = (math.radians(-22), 0, math.radians(4 if p == 7 else -4))
    # Hal's and Bea's cards
    for nm, who in (("ch", "hal"), ("cb", "bea")):
        cs = sample(nm, tl, t, {"p": 0})
        ob = W[nm]
        if cs["p"] < 0.5:
            ob.location = (0, 0, -80)
            continue
        place_at_hand(ob, who, (0.0, -0.14, 0.22), 0.0)
        ob.rotation_euler.x = math.radians(-20)
    # my folded question going into the slot
    qu = sample("q", tl, t, {"u": 0.0}, smooth=("u",))["u"]
    q = W["q"]
    if qu > 1.5 or not (sh["dusk"] > 0.5):
        q.location = (0, 0, -80)
    else:
        sy0 = BY + G.BOX_D / 2 - (G.BOX_D + 0.04) / 2 + 0.02 - 0.02 - 0.02
        q.location = (BX, sy0, Z1 + 0.25 - 0.3 * qu)
        q.rotation_euler = (0, 0, 0)
    # the bread, thrown up toward the gulls
    bu = sample("bread", tl, t, {"u": 0.0}, smooth=("u",))["u"]
    if 0.02 < bu < 0.98:
        p0, _ = root_frame("ty")
        x = p0.x + 0.6 + 2.0 * bu
        z = 1.9 + 2.4 * bu - 1.4 * bu * bu
        W["bread"].location = (x, p0.y + 0.1, z)
        W["bread"].rotation_euler = (bu * 6, bu * 4, 0)
    else:
        W["bread"].location = (0, 0, -80)
    # gulls: slow flaps and a lazy drift
    for g, wings, i in W["gulls"]:
        ph = t * (2.2 + 0.3 * i) + i
        for wg, s_ in wings:
            wg.rotation_euler = (0, s_ * 0.45 * math.sin(ph * 2 * math.pi / 2.2), 0)
        g.location.z = [3.2, 3.8, 2.9, 4.3][i] + 0.12 * math.sin(t * 1.1 + i)
    # Hal's rod and line
    rr = sample("rod", tl, t, {"r": 0.0})["r"]
    if rr > 0.5:
        hp = hand_of("hal")
        _, yaw = root_frame("hal")
        rod = W["rod"]
        rod.location = hp
        rod.rotation_euler = (math.radians(32), 0, yaw)
        bpy.context.view_layer.update()
        tip = rod.matrix_world @ Vector((0, -2.6, 0))
        end = Vector((G.POST[0] + 0.3, G.POST[1] - 1.3, G.WATER_Z + 0.02))
        mid = (tip + end) / 2
        dv = end - tip
        ln = W["line"]
        ln.location = mid
        ln.scale = (1, 1, dv.length)
        ln.rotation_euler = dv.to_track_quat("Z", "Y").to_euler()
        W["bobber"].location = end
    else:
        W["rod"].location = (0, 0, -80)
        W["line"].location = (0, 0, -80)
        W["bobber"].location = (0, 0, -80)
    # Hal's bucket, Bea's donut, Ty's pizza: held at chest height in front
    b_ = sample("bucket", tl, t, {"b": 0.0})["b"]
    if b_ > 0.5:
        hp = hand_of("hal")
        p0, yaw = root_frame("hal")
        place(W["bucket"], "hal", (0.0, -0.62, hp.z - p0.z - 0.05))
    else:
        W["bucket"].location = (0, 0, -80)
    d_ = sample("donut", tl, t, {"d": 0.0})["d"]
    if d_ > 0.5:
        hp = hand_of("bea")
        p0, yaw = root_frame("bea")
        place(W["donut"], "bea", (-0.36, -0.66, hp.z - p0.z + 0.22))
    else:
        W["donut"].location = (0, 0, -80)
    z_ = sample("pizza", tl, t, {"z": 0.0})["z"]
    if z_ > 0.5:
        hp = hand_of("ty")
        p0, yaw = root_frame("ty")
        place(W["pizza"], "ty", (0.0, -0.66, hp.z - p0.z + 0.1))
    else:
        W["pizza"].location = (0, 0, -80)
    return gains
