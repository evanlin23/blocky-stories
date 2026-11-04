"""Swing Bridge (ep58): a river town in late autumn, one iron swing bridge, its brick cabin, and the Reach.

Coordinates: metres, z up, front of a character is -y at yaw 0. The river runs along y between the far bank (x < 0)
and the near bank (x > 18). The swing span runs along +x from the far bank (x = 0) to its pivot on the stone pier
(x = 18.3). The cabin stands on the near bank, its window wall (y = 2.0) facing the bridge's line, the window at
x 19.5 to 20.9 and the door at x 21.5 to 22.2. The Reach's sleeves always lie on the cabin-side rail (y = 0.8).

Other places are at x offsets: cinema 100, office 130, house window 160, sofa 190, street 220, kitchen 250,
bedroom 350. The new road bridge is far downriver at y = 120.

Everything that changes inside a shot is read from the shot's own keys in story.json (look, reach, sash, door, ...) or from
cues (`lvl`: a named level eased over `ramp` seconds, never under 0.3). Every light change is a slow ramp.
"""

from __future__ import annotations

import math

import bpy
from mathutils import Vector as V

from blocky import acting, rig

OCHRE, PEAT, TAN, CLAY = "#8a6424", "#2b2420", "#b39a78", "#c49a74"
HAND_SKIN = "#e0b894"
COAT, RIM = "#25202a", "#a9cbee"     # dark cool cloth (the old brown read as a wooden beam), a cool rim
FOLD = "#3a3340"
GOLD = "#ffc76a"
SPAN_X = 18.3          # the pivot
RAIL_Y = 0.8
RAIL_Z = 0.98
FOG_NODES = {"built": False}
CH = {}

REACH_SPEC = {
    "age": "adult", "skin": CLAY, "shirt": OCHRE, "pattern": "solid", "collar": "#4a3c30", "pants": PEAT, "shoes": TAN,
    "sleeves": "none", "hair": "cap", "hair_c": "#120e0d", "hat": "none", "body_width": 0.78,
    "face": {"eyes": "pin", "mouth": "flat", "brows": False, "ink": "#161012"},
}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def seg(kit, name, a, b, t, mat, up_t=None, parent=None, bevel=0.03):
    a, b = V(a), V(b)
    d = b - a
    return kit.box(name, (t, up_t or t, d.length), tuple((a + b) / 2), mat, parent=parent,
                   rot=d.to_track_quat("Z", "Y").to_euler(), bevel=bevel)


# ------------------------------------------------------------------------------------------------ the Reach


def long_arm(kit, name, pts, t=0.26, fold=1.4, hand=True, grp=None, skin_c=None, coat_c=None, em=None):
    """One continuous sleeve through pts (shoulder first, hand end last): blocks <= fold long laid end to end, a fold
    of cloth at each join, a thin cool rim along the top, and at the end a plain skin hand lying flat: a palm block
    and four blocky fingers together, palms down."""
    # dark cloth that does not pick up the scene's fill: lit plastic washed to a pale grey pipe (qa, 2026-11-03)
    if em:      # the bedroom's sleeves glow faintly and keep the lit material
        sl, cuffm = kit.plastic(coat_c or COAT, 0.85), kit.plastic(coat_c or COAT, 0.85)
    else:
        sl = kit.emit(coat_c or COAT, 0.9, name=f"sleeve {coat_c or COAT}")
        cuffm = sl
    rim = kit.emit(RIM, 0.35)
    foldm = sl if em else kit.emit(FOLD, 0.9, name="sleeve fold")
    skin = kit.plastic(skin_c or HAND_SKIN, 0.9 if skin_c else 0.55)
    if em:
        for m_ in (skin, sl, cuffm):
            b_ = m_.node_tree.nodes["Principled BSDF"]
            b_.inputs["Emission Color"].default_value = kit.col(em[0])
            b_.inputs["Emission Strength"].default_value = em[1]
    P = [V(p) for p in pts]
    joints = [P[0]]
    for i in range(len(P) - 1):
        d = P[i + 1] - P[i]
        n = max(1, int(math.ceil(d.length / fold)))
        for k in range(1, n + 1):
            joints.append(P[i] + d * (k / n))
    up = V((0, 0, 1))
    obs = []
    for i in range(len(joints) - 1):
        a, b = joints[i], joints[i + 1]
        obs.append(seg(kit, f"{name}.s{i}", a, b, t, sl))
        obs.append(seg(kit, f"{name}.r{i}", a + up * (t / 2 + 0.006), b + up * (t / 2 + 0.006), 0.035, rim, 0.01))
    for i in range(1, len(joints) - 1):
        d = joints[i + 1] - joints[i - 1]
        obs.append(kit.box(f"{name}.f{i}", (t * 1.3, t * 1.3, 0.16), tuple(joints[i]), foldm,
                           rot=d.to_track_quat("Z", "Y").to_euler(), bevel=0.05))
    if hand:
        H = 1.5      # a big, pale hand: palm and four blocky fingers, palms down
        e, d = joints[-1], (joints[-1] - joints[-2]).normalized()
        yaw = math.atan2(d.y, d.x)
        perp = V((-d.y, d.x, 0))
        zc = e.z - t / 2 + 0.05 * H
        obs.append(kit.box(f"{name}.cuff", (0.07, t * 1.02, t * 1.02), tuple(e + d * 0.02), cuffm, rot=(0, 0, yaw), bevel=0.03))
        obs.append(kit.box(f"{name}.palm", (0.24 * H, 0.21 * H, 0.09 * H), tuple(V((e.x, e.y, zc)) + d * 0.17 * H), skin, rot=(0, 0, yaw),
                           bevel=0.02))
        for k in range(4):
            fl = (0.19, 0.22, 0.2, 0.15)[k] * H
            off = (-0.078, -0.026, 0.026, 0.078)[k] * H
            obs.append(kit.box(f"{name}.fing{k}", (fl, 0.04 * H, 0.06 * H), tuple(V((e.x, e.y, zc)) + d * (0.29 * H + fl / 2) + perp * off),
                               skin, rot=(0, 0, yaw), bevel=0.012))
        obs.append(kit.box(f"{name}.thumb", (0.13 * H, 0.05 * H, 0.06 * H), tuple(V((e.x, e.y, zc)) + d * 0.14 * H - perp * 0.13 * H), skin,
                           rot=(0, 0, yaw + 0.5), bevel=0.012))
    return obs


def make_reach(kit, workdir, name, pos, yaw=0.0, lean=0.0, head_pitch=0.0, paths=None, fold=1.4):
    """One Reach: a man, plus two continuous sleeves. paths(shoulderL, shoulderR) -> two point lists. Returns every
    object, so a shot can show the one it wants."""
    n0 = set(bpy.data.objects.keys())
    ch = rig.Character(name, REACH_SPEC, workdir)
    CH[name] = ch
    ch.pose(pos[0], pos[1], pos[2], yaw, lean=lean, head_pitch=head_pitch, expr="neutral")
    for sx in (-1, 1):
        for ob in ch.P[f"arm{sx}"].children_recursive:
            ob.hide_render = True
    bpy.context.view_layer.update()
    sh = [ch.torso.matrix_world @ V((sx * 1.5 * REACH_SPEC["body_width"], 0, 1.75)) for sx in (-1, 1)]
    for nm, pts in zip(("armL", "armR"), paths(*sh)):
        long_arm(kit, f"{name}.{nm}", pts, fold=fold)
    skip = set()
    for sx in (-1, 1):
        skip.update(o.name for o in ch.P[f"arm{sx}"].children_recursive)
    return [bpy.data.objects[k] for k in bpy.data.objects.keys() if k not in n0 and k not in skip]


def rail_path(sh, x_from, x_to, kink_x=None, y=RAIL_Y, z=1.13, off=0.12, side=1):
    """From a shoulder, down to the rail at x_from, then flat along it to x_to, with one small elbow jog."""
    yy = y + side * off
    pts = [sh, V((sh.x + (x_from - sh.x) * 0.22, sh.y + (yy - sh.y) * 0.5, 1.0 + (sh.z - 1.0) * 0.35)),
           V((x_from, yy, z))]
    step = 1 if x_to > x_from else -1
    if kink_x is not None:
        pts += [V((kink_x, yy, z)), V((kink_x + step * 0.4, yy + side * 0.07, z))]
    pts.append(V((x_to, yy, z)))
    return pts


# ------------------------------------------------------------------------------------------------ places


def span(kit, parent):
    green = kit.plastic("#4d7461", 0.6)
    dark = kit.plastic("#2f4a3e", 0.7)
    deck = kit.planks("#6a5440", "#4a3a2c", 1.0, "Y", rough=0.85)
    L = SPAN_X
    kit.box("deck", (L, 1.8, 0.14), (-L / 2, 0, -0.07), deck, parent)
    n = 12
    bay = L / n
    for side in (-1, 1):
        y = side * RAIL_Y
        kit.box(f"top{side}", (L, 0.12, 0.07), (-L / 2, y, RAIL_Z - 0.035), green, parent, bevel=0.02)
        kit.box(f"low{side}", (L, 0.07, 0.07), (-L / 2, y, 0.22), green, parent, bevel=0.02)
        for i in range(n + 1):
            x = -i * bay
            kit.box(f"post{side}{i}", (0.09, 0.09, RAIL_Z), (x, y, RAIL_Z / 2), dark, parent, bevel=0.015)
            kit.box(f"rv{side}{i}", (0.13, 0.13, 0.05), (x, y, RAIL_Z + 0.01), dark, parent, bevel=0.015)
        for i in range(n):
            a = (-i * bay, y, 0.22)
            b = (-(i + 1) * bay, y, RAIL_Z - 0.04)
            seg(kit, f"dg{side}{i}", a, b, 0.05, dark, 0.05, parent, 0.01)
            seg(kit, f"dh{side}{i}", (b[0], y, 0.22), (a[0], y, RAIL_Z - 0.04), 0.05, dark, 0.05, parent, 0.01)
    # the steel plate and big bolts that pin the span shut at the pivot
    plate = kit.metal("#6a6e72", 0.5)
    kit.box("plate", (0.9, 1.5, 0.06), (-0.55, 0, 0.03), plate, parent, bevel=0.01)
    for i, (bx, by) in enumerate(((-0.25, -0.55), (-0.25, -0.18), (-0.25, 0.18), (-0.25, 0.55), (-0.85, -0.55),
                                  (-0.85, -0.18), (-0.85, 0.18), (-0.85, 0.55))):
        kit.cyl(f"bolt{i}", 0.07, 0.1, (bx, by, 0.1), kit.metal("#3a3d40", 0.4), parent, n=10)


def build_bridge(kit, ctx):
    river = kit.plastic("#34495a", 0.35)
    kit.box("river", (400, 400, 0.1), (9, 100, -1.0), river)
    ground = kit.grime("#3a3b30", 0.55, 2.0, rough=0.9)
    gravel = kit.cobbles("#4a4742", "#6d6a62", "#25241f", 4.0, 0.0)
    kit.box("farbank", (60, 400, 1.0), (-30, 100, -0.5), ground)
    kit.box("nearbank", (70, 400, 1.0), (18 + 35, 100, -0.5), ground)
    kit.box("pier", (1.9, 2.8, 1.6), (SPAN_X, 0, -0.8), kit.concrete("#7c7a74", 1.5, 0.5), bevel=0.02)
    kit.box("path", (1.4, 36, 0.04), (21.6, -14, 0.0), gravel)
    kit.box("path2", (6, 1.4, 0.04), (24, -3, 0.0), gravel)
    piv = kit.empty("span", (SPAN_X, 0, 0))
    span(kit, piv)
    ctx["span"] = piv
    # the striped barrier arm across the near end (stripes only)
    red, white = kit.plastic("#b0443a", 0.6), kit.plastic("#d8d4c8", 0.6)
    kit.box("barpost", (0.14, 0.14, 1.1), (19.2, -1.5, 0.55), kit.plastic("#3a3d40", 0.6), bevel=0.02)
    bar = []
    for i in range(8):
        bar.append(kit.box(f"bar{i}", (0.16, 0.36, 0.14), (19.2, -1.5 + 0.36 * i + 0.18 + 0.0, 1.05), red if i % 2 else white, bevel=0.02))
    # reeds and a lamp post
    rng = [(math.sin(i * 12.9898) * 43758.5453) % 1 for i in range(400)]
    reed = kit.plastic("#4a5236", 0.9)
    for i in range(70):
        r1, r2, r3 = rng[i * 3], rng[i * 3 + 1], rng[i * 3 + 2]
        side = i % 2
        x = (-0.3 - r1 * 0.6) if side == 0 else (18.4 + r1 * 0.6)
        y = -14 + r2 * 40
        if side == 1 and -1.5 < y < 1.5:
            continue
        kit.box(f"reed{i}", (0.05, 0.05, 0.6 + r3 * 0.8), (x, y, 0.3 + r3 * 0.4), reed, rot=(0.1 * (r1 - 0.5), 0.1 * (r2 - 0.5), 0))
    iron = kit.plastic("#26302b", 0.5)
    kit.box("lpost", (0.1, 0.1, 2.9), (20.2, -3.0, 1.45), iron, bevel=0.02)
    kit.box("lhead", (0.34, 0.34, 0.4), (20.2, -3.0, 2.95), kit.emit("#ffcf8a", 3.0), bevel=0.04)
    kit.box("lcap", (0.5, 0.5, 0.08), (20.2, -3.0, 3.2), iron)
    # far-bank trees, dark and blocky, so the fog has something to swallow
    tree = kit.plastic("#1e2a22", 0.9)
    for i in range(18):
        x = -6 - rng[100 + i] * 20
        y = -28 + i * 3.4
        h = 5 + rng[130 + i] * 4
        h = 2.2 + rng[130 + i] * 1.6
        kit.box(f"tree{i}", (0.45, 0.45, h), (x, y, h / 2), kit.plastic("#2b2418", 0.9), bevel=0.05)
        kit.box(f"leaf{i}", (3.4, 3.4, 2.6), (x, y, h + 0.9), tree, bevel=0.2)
    # the memory boat and the gold streaks (summer shots only)
    hull = kit.plastic("#8a3a30", 0.6)
    boat = [kit.box("hull", (2.6, 0.8, 0.5), (0, 0, 0), hull, bevel=0.1),
            kit.box("cabinb", (0.9, 0.6, 0.4), (-0.4, 0, 0.45), kit.plastic("#d8d4c8", 0.6), bevel=0.05),
            kit.box("mast", (0.07, 0.07, 3.0), (0.4, 0, 1.7), kit.plastic("#cfc4a8", 0.6)),
            kit.box("sail", (1.5, 0.03, 2.4), (-0.35, 0, 1.9), kit.plastic("#e9e2cf", 0.7), rot=(0, 0, 0))]
    ctx["boat"] = boat
    streaks = []
    sm = kit.emit(GOLD, 0.8)
    for i in range(7):
        streaks.append(kit.box(f"streak{i}", (0.1 + 0.05 * (i % 3), 3.0 + (i % 4) * 1.2, 0.02), (14.5 - i * 0.7, -2.5 + i * 0.4, -0.93), sm))
    ctx["streaks"] = streaks
    ctx["bar"] = bar + [bpy.data.objects["barpost"]]
    # the new road bridge far downriver: a pale deck on a pale arch, a slow string of car lights
    conc = kit.concrete("#b9bcbc", 1.0, 0.3)
    kit.box("nb_deck", (160, 7.0, 1.4), (9, 120, 9.0), conc)
    for sx in (-1, 1):
        kit.box(f"nb_rail{sx}", (160, 0.3, 0.9), (9, 120 + sx * 3.4, 10.0), conc)
    for i in range(16):
        a0 = math.radians(180 - i * 180 / 16)
        a1 = math.radians(180 - (i + 1) * 180 / 16)
        p0 = (9 + 25 * math.cos(a0), 120, 8.2 * math.sin(a0) + 0.0)
        p1 = (9 + 25 * math.cos(a1), 120, 8.2 * math.sin(a1) + 0.0)
        for sy in (-1.6, 1.6):
            seg(kit, f"nb_arch{i}{sy}", (p0[0], 120 + sy, p0[2]), (p1[0], 120 + sy, p1[2]), 1.2, conc, 1.2, None, 0.05)
    for i in range(9):
        x = 9 - 25 + i * 6.25
        h = 8.2 * math.sin(math.acos(max(-1, min(1, (x - 9) / 25))))
        kit.box(f"nb_col{i}", (0.7, 0.7, max(0.2, 9.0 - h)), (x, 120, h + max(0.2, 9.0 - h) / 2), conc)
    for sx in (-1, 1):
        kit.box(f"nb_abut{sx}", (5, 8, 8.5), (9 + sx * 29, 120, 4.25), conc)
    cars = []
    for i in range(7):
        cars.append(kit.box(f"car{i}", (0.8, 0.5, 0.35), (0, 119.2 + (i % 2) * 1.2, 10.3), kit.emit("#ffd9a0" if i % 2 else "#ff7a60", 1.2)))
    ctx["cars"] = cars
    pm = kit.emit("#a8c8e8", 1.4)
    prs = []
    for pi, (px, py) in enumerate(((17.55, RAIL_Y - 0.12), (17.7, RAIL_Y + 0.14))):
        prs.append(kit.box(f"print{pi}.p", (0.12, 0.12, 0.012), (px, py, RAIL_Z + 0.004), pm, bevel=0.004))
        for k in range(4):
            prs.append(kit.box(f"print{pi}.f{k}", (0.1, 0.028, 0.012), (px + 0.12, py + (k - 1.5) * 0.034, RAIL_Z + 0.004), pm, bevel=0.004))
        prs.append(kit.box(f"print{pi}.t", (0.07, 0.03, 0.012), (px - 0.02, py - 0.09, RAIL_Z + 0.004), pm, bevel=0.004))
    ctx["prints"] = prs
    lp = []
    for pi in range(2, 16):
        for sd in (-1, 1):
            px = 17.0 - (pi - 2) * 1.2 - (0.25 if sd < 0 else 0.0)
            py = RAIL_Y + sd * 0.1
            lp.append(kit.box(f"lprint{pi}{sd}.p", (0.16, 0.16, 0.012), (px, py, RAIL_Z + 0.004), pm, bevel=0.004))
            for k in range(4):
                lp.append(kit.box(f"lprint{pi}{sd}.f{k}", (0.14, 0.036, 0.012), (px + 0.16, py + (k - 1.5) * 0.045, RAIL_Z + 0.004), pm, bevel=0.004))
    ctx["lprints"] = lp
    # a small car parked on the path, boot toward the bridge, and the crate Ada lifts
    cb = kit.plastic("#5a6a7a", 0.4)
    kit.box("car_body", (1.8, 4.2, 0.8), (25.0, -8.5, 0.6), cb, bevel=0.15)
    kit.box("car_top", (1.6, 2.1, 0.6), (25.0, -9.0, 1.2), kit.plastic("#8aa0b0", 0.3), bevel=0.15)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"car_w{sx}{sy}", 0.33, 0.25, (25.0 + sx * 0.92, -8.5 + sy * 1.4, 0.33), kit.plastic("#1a1a1c", 0.8), rot=(0, math.pi / 2, 0), n=14)
    kit.box("car_boot", (1.7, 0.06, 0.8), (25.0, -6.7, 1.35), cb, rot=(1.1, 0, 0), bevel=0.02)
    ctx["crate"] = kit.box("crate_ada", (0.55, 0.4, 0.4), (0, 0, -60), kit.planks("#9a7a4a", "#6a5232", 2.0, "X"), bevel=0.02)


def build_cabin(kit, ctx):
    brick = kit.bricks("#8a4b3a", "#6f3a2c", "#4a4540", 1.0)
    cream = kit.plastic("#d9cfb8", 0.6)
    slate = kit.plastic("#3b4048", 0.7)
    wood = kit.planks("#6b4a2e", "#4e3520", 1.0, "X")
    X0, X1, Y0, Y1, H = 19.0, 22.6, 2.0, 5.3, 2.6
    kit.box("cab_floor", (X1 - X0, Y1 - Y0, 0.12), ((X0 + X1) / 2, (Y0 + Y1) / 2, -0.06), wood)
    kit.box("cab_ceil", (X1 - X0, Y1 - Y0, 0.12), ((X0 + X1) / 2, (Y0 + Y1) / 2, H + 0.06), kit.plastic("#5a4c3c", 0.9))
    # the window wall (y 2.0 to 2.3): a wide gap x 19.5 to 20.9, sill at 0.45, head at 2.05; then a door gap 21.5 to 22.2
    t = 0.3
    yc = Y0 + t / 2
    kit.box("wA", (0.5, t, H), (19.25, yc, H / 2), brick)
    kit.box("wB", (0.6, t, H), (21.2, yc, H / 2), brick)
    kit.box("wC", (0.4, t, H), (22.4, yc, H / 2), brick)
    kit.box("wsill", (1.4, t, 0.45), (20.2, yc, 0.225), brick)
    kit.box("whead", (1.4, t, H - 2.05), (20.2, yc, (H + 2.05) / 2), brick)
    kit.box("dhead", (0.7, t, H - 2.0), (21.85, yc, (H + 2.0) / 2), brick)
    kit.box("sillc", (1.7, 0.5, 0.06), (20.2, Y0 + 0.2, 0.48), cream, bevel=0.02)
    for nm, cx in (("fl", 19.5), ("fr", 20.9)):
        kit.box(f"frame{nm}", (0.08, 0.1, 1.6), (cx, Y0 + 0.05, 1.25), cream)
    kit.box("frametop", (1.5, 0.1, 0.08), (20.2, Y0 + 0.05, 2.04), cream)
    ctx["mullion"] = kit.box("mullion", (1.4, 0.06, 0.05), (20.2, Y0 + 0.05, 1.28), cream)
    # the lower sash: a cream frame with glass, slid up in some shots
    sash = [kit.box("sash_t", (1.34, 0.06, 0.06), (20.2, Y0 + 0.14, 0.0), cream), kit.box("sash_b", (1.34, 0.06, 0.06), (20.2, Y0 + 0.14, 0.0), cream),
            kit.box("sash_l", (0.06, 0.06, 0.8), (19.55, Y0 + 0.14, 0.0), cream), kit.box("sash_r", (0.06, 0.06, 0.8), (20.85, Y0 + 0.14, 0.0), cream),
            kit.box("sash_g", (1.28, 0.02, 0.74), (20.2, Y0 + 0.14, 0.0), kit.glass("#b8cad6"))]
    ctx["sash"] = sash
    ctx["sash_off"] = [0.37, -0.37, 0.0, 0.0, 0.0]
    kit.box("wback", (X1 - X0, t, H), ((X0 + X1) / 2, Y1 - t / 2, H / 2), brick)
    kit.box("wwest", (t, Y1 - Y0, H), (X0 + t / 2, (Y0 + Y1) / 2, H / 2), brick)
    kit.box("weast", (t, Y1 - Y0, H), (X1 - t / 2, (Y0 + Y1) / 2, H / 2), brick)
    # roof: a shallow gable running along x, slate, and a stubby chimney
    for sy in (-1, 1):
        kit.box(f"roof{sy}", (X1 - X0 + 0.5, 2.1, 0.12), ((X0 + X1) / 2, (Y0 + Y1) / 2 + sy * 0.95, H + 0.55), slate,
                rot=(-sy * 0.36, 0, 0))
    kit.box("chim", (0.5, 0.5, 1.0), (22.0, 4.5, H + 0.9), brick)
    # the door leaf (hinged at x 22.2, swings inward)
    hinge = kit.empty("doorhinge", (22.2, Y0 + 0.15, 0))
    kit.box("doorleaf", (0.7, 0.08, 1.98), (-0.35, 0, 0.99), kit.planks("#4a5a4a", "#34423a", 1.0, "Y"), hinge, bevel=0.01)
    ctx["door"] = hinge
    # the iron wheel on the east wall (axis along x), brass hub plate facing -x
    iron = kit.plastic("#23282a", 0.45)
    WX, WY, WZ = 22.32, 3.7, 1.3
    wheel = kit.empty("wheel", (WX, WY, WZ))
    for i in range(16):
        a0, a1 = 2 * math.pi * i / 16, 2 * math.pi * (i + 1) / 16
        seg(kit, f"wr{i}", (0, 0.55 * math.cos(a0), 0.55 * math.sin(a0)), (0, 0.55 * math.cos(a1), 0.55 * math.sin(a1)), 0.07, iron, 0.07, wheel, 0.01)
    for i in range(4):
        a = math.pi * i / 4
        seg(kit, f"wsp{i}", (0, 0.5 * math.cos(a), 0.5 * math.sin(a)), (0, -0.5 * math.cos(a), -0.5 * math.sin(a)), 0.05, iron, 0.05, wheel, 0.01)
    kit.cyl("hub", 0.13, 0.1, (-0.0, 0, 0), kit.plastic("#b8913e", 0.35), wheel, rot=(0, math.pi / 2, 0), n=18)
    kit.cyl("hubplate", 0.1, 0.03, (-0.06, 0, 0), kit.plastic("#c9a24a", 0.3), wheel, rot=(0, math.pi / 2, 0), n=18)
    ochre = kit.emit("#c89030", 0.6)
    for k, dy in enumerate((-0.025, 0.025)):
        kit.box(f"tally{k}", (0.012, 0.012, 0.07), (-0.08, dy, 0.0), ochre, wheel, rot=(0.3, 0, 0))
    kit.box("crank", (0.06, 0.06, 0.34), (-0.18, 0.0, 0.55 + 0.17), iron, wheel)
    kit.box("crankh", (0.22, 0.05, 0.05), (-0.18, 0.0, 0.55 + 0.34), iron, wheel)
    ctx["wheel"] = (WX, WY, WZ)
    # the cap that hangs on the crank in S40 (Emrys's own, off his head)
    cap = [kit.box("hangcap", (0.34, 0.34, 0.1), (WX - 0.22, WY, WZ + 0.78), kit.plastic("#34493b", 0.85), bevel=0.04),
           kit.box("hangbrim", (0.3, 0.14, 0.03), (WX - 0.22, WY - 0.16, WZ + 0.74), kit.plastic("#34493b", 0.85))]
    ctx["hangcap"] = cap
    # stools (his, worn; the second, with a plank back so a turn reads), the crate, the stove, the lamp, the mugs
    wd = kit.plastic("#7a5a38", 0.8)
    wd2 = kit.plastic("#8a6a44", 0.8)

    def stool(name, x, y, back):
        e = kit.empty(name, (x, y, 0))
        kit.cyl(f"{name}.top", 0.21, 0.07, (0, 0, 0.5), wd, e, n=20)
        for k in range(3):
            a = 2 * math.pi * k / 3
            kit.box(f"{name}.leg{k}", (0.05, 0.05, 0.5), (0.15 * math.cos(a), 0.15 * math.sin(a), 0.25), wd, e)
        if back:
            kit.box(f"{name}.back", (0.4, 0.05, 0.4), (0, 0.2, 0.74), wd2, e, bevel=0.01)
            for sx in (-1, 1):
                kit.box(f"{name}.bp{sx}", (0.05, 0.05, 0.3), (sx * 0.18, 0.2, 0.62), wd2, e)
        return e
    ctx["stool1"] = stool("stool1", 21.4, 3.6, False)
    ctx["stool2"] = stool("stool2", 20.6, 3.6, True)
    kit.box("crate", (0.5, 0.4, 0.42), (19.8, 3.55, 0.21), kit.planks("#6a5236", "#4a3824", 2.0, "X"), bevel=0.02)
    stove = kit.empty("stove", (19.5, 4.6, 0))
    kit.cyl("stbody", 0.34, 0.85, (0, 0, 0.5), kit.plastic("#1d1d20", 0.5), stove, n=20)
    kit.cyl("stpipe", 0.07, 1.4, (0.0, 0.2, 1.9), kit.plastic("#1d1d20", 0.5), stove, n=10)
    kit.cyl("stbase", 0.38, 0.1, (0, 0, 0.06), kit.plastic("#1d1d20", 0.5), stove, n=20)
    fire = kit.emit("#e0682a", 1.0, name="stovefire")
    kit.box("stdoor", (0.22, 0.04, 0.2), (0, -0.33, 0.4), fire, stove, bevel=0.01)
    ctx["firemat"] = fire
    lampm = kit.emit("#ffc070", 1.0, name="lampglow")
    kit.box("lampbr", (0.05, 0.3, 0.05), (21.2, 5.12, 1.55), iron)
    kit.box("lampbulb", (0.14, 0.14, 0.2), (21.2, 4.98, 1.5), lampm, bevel=0.04)
    ctx["lampmat"] = lampm
    mug = kit.plastic("#d8cdb4", 0.5)
    for k, mx in enumerate((19.95, 20.5)):
        kit.cyl(f"mug{k}", 0.055, 0.1, (mx, Y0 + 0.2, 0.56), mug, n=14)
        kit.box(f"mugh{k}", (0.02, 0.05, 0.06), (mx + 0.065, Y0 + 0.2, 0.56), mug)
    steam = kit.emit("#c8d0d8", 0.25)
    ctx["steam"] = [kit.box(f"steam{k}", (0.025, 0.025, 0.18 + 0.05 * k), (19.95 + 0.55 * (k // 2) + 0.01 * k, Y0 + 0.2, 0.74), steam) for k in range(4)]
    ctx["mugs"] = [bpy.data.objects[f"mug{k}"] for k in range(2)]
    # dull things that make a cabin: a coat peg, a shelf, a lantern on the floor
    kit.box("shelf", (1.0, 0.18, 0.04), (20.9, 5.1, 1.9), wd)
    kit.box("lantern", (0.2, 0.2, 0.3), (22.15, 4.9, 0.15), kit.plastic("#2a2d2c", 0.5))


def build_cinema(kit, ctx):
    X = 100.0
    dark = kit.plastic("#2a1d24", 0.9)
    kit.box("cin_floor", (10, 17, 0.1), (X, -1.5, -0.05), kit.plastic("#3a2a30", 0.9))
    kit.box("cin_ceil", (10, 17, 0.1), (X, -1.5, 4.05), dark)
    kit.box("cin_wback", (10, 0.2, 4), (X, 6.9, 2.0), kit.plastic("#4a3038", 0.9))
    kit.box("cin_wl", (0.2, 17, 4), (X - 5, -1.5, 2.0), kit.plastic("#43303a", 0.9))
    kit.box("cin_wr", (0.2, 17, 4), (X + 5, -1.5, 2.0), kit.plastic("#43303a", 0.9))
    kit.box("cin_wf", (10, 0.2, 4), (X, -10.0, 2.0), dark)
    ctx["screen"] = kit.box("cin_screen", (7.0, 0.05, 3.4), (X, -9.85, 2.3), kit.emit("#6a86d8", 0.8, name="screenmat"))
    seat = kit.plastic("#6b2a3a", 0.8)
    for r, y in enumerate((-4.0, -2.6, -1.2, 0.2, 1.6, 3.0)):
        for i in range(-4, 5):
            x = X + i * 0.85
            if abs(i) <= 0 and False:
                continue
            kit.box(f"cs{r}_{i}", (0.7, 0.62, 0.45), (x, y, 0.225), seat, bevel=0.03)
            kit.box(f"cb{r}_{i}", (0.7, 0.14, 0.5), (x, y + 0.34, 0.65), seat, bevel=0.03)
    ctx["cin_back_y"] = 3.0


def build_office(kit, ctx):
    X = 130.0
    kit.box("of_floor", (9, 10, 0.1), (X, 3, -0.05), kit.plastic("#4a4a50", 0.8))
    kit.box("of_ceil", (9, 10, 0.1), (X, 3, 3.05), kit.plastic("#d8d8d8", 0.9))
    kit.box("of_wback", (9, 0.2, 3), (X, 8.0, 1.5), kit.plastic("#c9ccd0", 0.9))
    kit.box("of_wl", (0.2, 10, 3), (X - 4.5, 3, 1.5), kit.plastic("#b9bcc0", 0.9))
    kit.box("of_wr", (0.2, 10, 3), (X + 4.5, 3, 1.5), kit.plastic("#b9bcc0", 0.9))
    kit.box("of_wf", (9, 0.2, 3), (X, -2.0, 1.5), kit.plastic("#b9bcc0", 0.9))
    kit.box("of_table", (4.2, 1.2, 0.08), (X, 4.4, 0.74), kit.plastic("#6a4a30", 0.5), bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"of_leg{sx}{sy}", (0.08, 0.08, 0.72), (X + sx * 1.95, 4.4 + sy * 0.5, 0.36), kit.plastic("#2a2a2e", 0.5))
    kit.box("of_win", (3.0, 0.05, 1.6), (X - 1.5, 7.88, 1.7), kit.emit("#e8f0ff", 0.8))
    for i in range(3):
        kit.box(f"of_chair{i}", (0.5, 0.5, 0.9), (X - 1.3 + i * 0.95, 5.55, 0.45), kit.plastic("#2f3a4a", 0.7), bevel=0.05)


def build_homewin(kit, ctx):
    X = 160.0
    kit.box("hw_ground", (14, 14, 0.2), (X, -5, -0.1), kit.grime("#5a5a50", 0.6, 2.0))
    brick = kit.bricks("#8a5a44", "#6f4636", "#4a4540", 1.0)
    cream = kit.plastic("#d9cfb8", 0.6)
    kit.box("hw_wl", (4.0, 0.4, 3.2), (X - 3.0, 0, 1.6), brick)
    kit.box("hw_wr", (4.0, 0.4, 3.2), (X + 3.0, 0, 1.6), brick)
    kit.box("hw_wb", (2.0, 0.4, 0.9), (X, 0, 0.45), brick)
    kit.box("hw_wt", (2.0, 0.4, 1.2), (X, 0, 2.6), brick)
    kit.box("hw_sill", (2.3, 0.4, 0.07), (X, -0.15, 0.93), cream)
    for sx in (-1, 1):
        kit.box(f"hw_fr{sx}", (0.1, 0.12, 1.1), (X + sx * 0.95, -0.2, 1.5), cream)
    kit.box("hw_fm", (1.9, 0.12, 0.1), (X, -0.2, 2.02), cream)
    kit.box("hw_room", (8, 4, 0.1), (X, 2.2, -0.05), kit.planks("#6b4a2e", "#4e3520", 1.0, "X"))
    kit.box("hw_back", (8, 0.2, 3.2), (X, 4.2, 1.6), kit.plastic("#8a8070", 0.9))
    kit.box("hw_ceil", (8, 4, 0.1), (X, 2.2, 3.25), kit.plastic("#cfc8b8", 0.9))
    for sx in (-1, 1):
        kit.box(f"hw_side{sx}", (0.2, 4.2, 3.2), (X + sx * 3.95, 2.1, 1.6), brick)
    kit.box("hw_shelf", (1.6, 0.9, 0.7), (X + 1.6, 3.5, 0.35), kit.plastic("#5a3f28", 0.7))
    # the terrier on the sill, nose to the window
    tan, blk = kit.plastic("#b08a5a", 0.8), kit.plastic("#2a211b", 0.8)
    d = kit.empty("dog", (X, 0.2, 0.97))
    kit.box("dog_body", (0.34, 0.55, 0.34), (0, 0.3, 0.17), tan, d, bevel=0.06)
    kit.box("dog_head", (0.3, 0.3, 0.28), (0, -0.08, 0.38), tan, d, bevel=0.06)
    kit.box("dog_snout", (0.14, 0.2, 0.12), (0, -0.28, 0.33), kit.plastic("#d8c4a0", 0.8), d, bevel=0.03)
    kit.box("dog_nose", (0.06, 0.05, 0.05), (0, -0.4, 0.36), blk, d)
    for sx in (-1, 1):
        kit.box(f"dog_ear{sx}", (0.09, 0.12, 0.18), (sx * 0.17, -0.02, 0.5), blk, d, rot=(0, sx * 0.4, 0), bevel=0.03)
        kit.box(f"dog_eye{sx}", (0.045, 0.03, 0.045), (sx * 0.08, -0.22, 0.43), blk, d)
        kit.box(f"dog_leg{sx}", (0.09, 0.09, 0.3), (sx * 0.1, -0.06, 0.05), tan, d)
    kit.box("dog_tail", (0.07, 0.07, 0.28), (0, 0.62, 0.38), blk, d, rot=(-0.4, 0, 0))
    ctx["dog"] = d


def build_sofa(kit, ctx):
    X = 190.0
    kit.box("sf_floor", (8, 7, 0.1), (X, 1.0, -0.05), kit.planks("#5a4330", "#3d2d20", 1.0, "X"))
    kit.box("sf_ceil", (8, 7, 0.1), (X, 1.0, 3.05), kit.plastic("#cfc8b8", 0.9))
    kit.box("sf_wback", (8, 0.2, 3), (X, 4.6, 1.5), kit.plastic("#7a6a5a", 0.9))
    kit.box("sf_wf", (8, 0.2, 3), (X, -2.5, 1.5), kit.plastic("#7a6a5a", 0.9))
    for sx in (-1, 1):
        kit.box(f"sf_w{sx}", (0.2, 7, 3), (X + sx * 4, 1.0, 1.5), kit.plastic("#6f6050", 0.9))
    kit.box("sf_rug", (4.5, 3.0, 0.03), (X, 1.6, 0.015), kit.plastic("#5a3a3a", 0.95))
    sofa = kit.plastic("#8a5a3a", 0.8)
    kit.box("sf_seat", (3.4, 0.95, 0.45), (X, 3.7, 0.225), sofa, bevel=0.05)
    kit.box("sf_back", (3.4, 0.3, 0.9), (X, 4.25, 0.45), sofa, bevel=0.05)
    for sx in (-1, 1):
        kit.box(f"sf_arm{sx}", (0.3, 1.0, 0.7), (X + sx * 1.85, 3.75, 0.35), sofa, bevel=0.05)
    kit.box("sf_table", (1.4, 0.7, 0.4), (X, 1.9, 0.2), kit.plastic("#4a3524", 0.6))
    kit.box("sf_lamp_s", (0.07, 0.07, 1.3), (X + 3.0, 4.2, 0.65), kit.plastic("#2a2a2e", 0.5))
    kit.box("sf_lamp_h", (0.4, 0.4, 0.3), (X + 3.0, 4.2, 1.4), kit.emit("#ffc890", 1.2))
    kit.box("sf_pic", (1.2, 0.04, 0.8), (X - 1.4, 4.47, 1.8), kit.plastic("#4a6a7a", 0.8))


def build_street(kit, ctx):
    X = 220.0
    kit.box("st_ground", (20, 20, 0.2), (X, 0, -0.1), kit.grime("#6a6a64", 0.6, 1.5))
    kit.box("st_wall", (20, 0.4, 4.0), (X, 5.0, 2.0), kit.bricks("#8a5a44", "#6f4636", "#4a4540", 1.0))
    for i in range(4):
        kit.box(f"st_win{i}", (1.1, 0.06, 1.4), (X - 6 + i * 4, 4.78, 2.0), kit.plastic("#2a3440", 0.3))


def build_kitchen(kit, ctx):
    X = 250.0
    wall = kit.plastic("#d8c9a8", 0.9)
    kit.box("ki_floor", (8, 7, 0.1), (X, 3, -0.05), kit.planks("#7a5a3a", "#5a4228", 1.0, "X"))
    kit.box("ki_ceil", (8, 7, 0.1), (X, 3, 3.05), kit.plastic("#e8e0cc", 0.9))
    kit.box("ki_wback", (8, 0.2, 3), (X, 6.5, 1.5), wall)
    for sx in (-1, 1):
        kit.box(f"ki_w{sx}", (0.2, 7, 3), (X + sx * 4, 3, 1.5), wall)
    # the front wall has a doorway (Emrys in it, S46)
    kit.box("ki_wfl", (3.4, 0.2, 3), (X - 2.3, -0.5, 1.5), wall)
    kit.box("ki_wfr", (3.4, 0.2, 3), (X + 2.3, -0.5, 1.5), wall)
    kit.box("ki_wfh", (1.2, 0.2, 0.9), (X, -0.5, 2.55), wall)
    kit.box("ki_morning", (1.2, 0.05, 2.0), (X, -1.2, 1.0), kit.emit("#d7e3ea", 0.9))
    kit.box("ki_table", (1.6, 1.0, 0.06), (X, 3.4, 0.76), kit.plastic("#8a6a44", 0.6), bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"ki_tl{sx}{sy}", (0.07, 0.07, 0.74), (X + sx * 0.7, 3.4 + sy * 0.4, 0.37), kit.plastic("#6a4a30", 0.6))
    kit.box("ki_chair", (0.5, 0.5, 0.45), (X + 1.15, 3.4, 0.225), kit.plastic("#6a4a30", 0.7), bevel=0.03)
    kit.box("ki_win", (1.4, 0.05, 1.3), (X - 2.0, 6.38, 1.7), kit.emit("#e4ecf0", 0.35))
    kit.box("ki_chair2", (0.5, 0.5, 0.45), (X - 1.1, 3.4, 0.225), kit.plastic("#6a4a30", 0.7), bevel=0.03)
    ctx["kmug"] = kit.box("ki_mug1", (0.12, 0.12, 0.14), (X - 0.3, 3.3, 0.86), kit.plastic("#d8cdb4", 0.5), bevel=0.02)
    kit.box("ki_mug2", (0.1, 0.1, 0.1), (X + 0.3, 3.5, 0.84), kit.plastic("#d8cdb4", 0.5))


def build_bedroom(kit, ctx):
    X = 350.0
    kit.box("bd_floor", (6, 6, 0.1), (X, 2, -0.05), kit.planks("#4a3a2c", "#33281e", 1.0, "X"))
    kit.box("bd_ceil", (6, 6, 0.1), (X, 2, 3.05), kit.plastic("#8a8a90", 0.9))
    wl = kit.plastic("#5a5a68", 0.9)
    cream = kit.plastic("#d9cfb8", 0.6)
    # the back wall has a sash window over the bed: opening x 349.2 to 350.8, z 1.1 to 2.3
    kit.box("bd_wb_lo", (6, 0.2, 1.1), (X, 5.0, 0.55), wl)
    kit.box("bd_wb_hi", (6, 0.2, 0.7), (X, 5.0, 2.65), wl)
    kit.box("bd_wb_l", (2.2, 0.2, 1.2), (X - 1.9, 5.0, 1.7), wl)
    kit.box("bd_wb_r", (2.2, 0.2, 1.2), (X + 1.9, 5.0, 1.7), wl)
    for nm, cx in (("l", X - 0.8), ("r", X + 0.8)):
        kit.box(f"bd_fr{nm}", (0.1, 0.14, 1.2), (cx, 4.97, 1.7), cream)
    kit.box("bd_frt", (1.7, 0.14, 0.08), (X, 4.97, 2.3), cream)
    kit.box("bd_frb", (1.7, 0.14, 0.08), (X, 4.97, 1.1), cream)
    kit.box("bd_frm", (1.6, 0.1, 0.06), (X, 4.97, 1.7), cream)
    kit.box("bd_glass", (1.6, 0.02, 1.2), (X, 5.0, 1.7), kit.glass("#b8cad6"))
    kit.box("bd_blind", (1.56, 0.04, 0.6), (X, 4.9, 2.0), kit.plastic("#3a382f", 0.9))   # plain cream blind, half up
    kit.box("bd_sill", (1.9, 0.9, 0.06), (X, 5.55, 1.08), cream, bevel=0.01)
    kit.box("bd_ground", (30, 60, 0.2), (X, 35, -0.1), kit.grime("#2f3a30", 0.55, 2.0, rough=0.9))
    kit.box("bd_gwall", (10, 0.5, 1.0), (X, 8.5, 0.5), kit.bricks("#6a4a3e", "#523a30", "#3a3632", 1.0))
    kit.box("bd_back", (30, 0.2, 14), (X, 4.9, 7.0), wl, rot=(0, 0, 0)) if False else None
    kit.box("bd_wf", (6, 0.2, 3), (X, -1.0, 1.5), kit.plastic("#5a5a68", 0.9))
    for sx in (-1, 1):
        kit.box(f"bd_w{sx}", (0.2, 6, 3), (X + sx * 3, 2, 1.5), kit.plastic("#5a5a68", 0.9))
    kit.box("bd_bed", (2.2, 2.4, 0.5), (X, 2.6, 0.25), kit.plastic("#7a6a5a", 0.8), bevel=0.04)
    kit.box("bd_head", (2.4, 0.15, 1.1), (X, 3.9, 0.55), kit.plastic("#5a4330", 0.7))
    kit.box("bd_pillow1", (0.8, 0.3, 0.1), (X - 0.55, 3.72, 0.55), kit.plastic("#cfd2d8", 0.9), bevel=0.05)
    kit.box("bd_pillow2", (0.8, 0.3, 0.1), (X + 0.55, 3.72, 0.55), kit.plastic("#cfd2d8", 0.9), bevel=0.05)
    kit.box("bd_blanket", (2.1, 1.6, 0.14), (X, 1.9, 0.55), kit.plastic("#3a4a6a", 0.9), bevel=0.05)
    kit.box("bd_win", (1.2, 0.05, 1.4), (X + 1.8, -0.88, 1.6), kit.emit("#3a4c78", 0.6))


# ------------------------------------------------------------------------------------------------ the build


def build(kit, story, tl):
    ctx = {"lazy": False, "spec": {s["id"]: s for s in story["shots"]}}
    build_bridge(kit, ctx)
    build_cabin(kit, ctx)
    build_cinema(kit, ctx)
    build_office(kit, ctx)
    build_homewin(kit, ctx)
    build_sofa(kit, ctx)
    build_street(kit, ctx)
    build_kitchen(kit, ctx)
    build_bedroom(kit, ctx)
    # the Reach: five models (a body and two sleeves each), one shown at a time
    workdir = bpy.path.abspath("//") if False else None
    from pathlib import Path
    import os, tempfile
    # never a machine-specific path: Actions has no /home/user, so every draw shard died at once (2026-11-03)
    wd = Path(os.environ.get("BLOCKY_FACES") or os.path.join(tempfile.gettempdir(), "ep58-swing-bridge-faces"))
    wd.mkdir(parents=True, exist_ok=True)
    R = {}
    far = (-0.9, RAIL_Y, 0.0)
    for nm, xe in (("mon", 6.0), ("tue", 9.0), ("wed", 17.8)):
        R[nm] = make_reach(kit, wd, f"reach_{nm}", far, yaw=math.radians(90), head_pitch=0.12,
                           paths=lambda sl, sr, xe=xe: [rail_path(sl, 0.2, xe, kink_x=min(4.0, xe - 1), side=-1),
                                                        rail_path(sr, 0.2, xe, kink_x=min(4.0, xe - 1), side=1)])
    # Thursday, standing at the window: his arms run back along the whole rail to the far bank
    R["stand"] = make_reach(kit, wd, "reach_stand", (19.95, 1.15, 0.0), yaw=math.radians(180), head_pitch=0.1, fold=0.8,
                            paths=lambda sl, sr: [rail_path(sl, 18.3, 0.5, kink_x=11.0, side=-1),
                                                  rail_path(sr, 18.3, 0.5, kink_x=11.0, side=1)])
    # the lean: head and shoulders in at the open sash, face to face with me. He stands on a low stone step, and each
    # sleeve leaves the shoulder straight out through the window opening before it drops to the rail
    
    def lean_path(sh, side):
        # from the shoulder just inside the sash, back out through the opening, down to the rail, then flat along it
        yy = RAIL_Y + side * 0.12
        pts = [sh, V((sh.x + side * 0.1, 1.5, 1.0)), V((19.4, yy, 1.12)), V((18.3, yy, 1.13))]
        pts += [V((11.0, yy, 1.13)), V((10.6, yy + side * 0.07, 1.13)), V((0.5, yy, 1.13))]
        return pts
    # leaning in from the ankles: the feet outside at y 1.2, the body tilted 42 degrees so the head is just inside the open sash
    R["lean"] = make_reach(kit, wd, "reach_lean", (20.2, 1.2, 0.0), yaw=math.radians(180), lean=0.74, head_pitch=-0.62, fold=0.8,
                           paths=lambda sl, sr: [lean_path(sl, -1 if sl.x < sr.x else 1), lean_path(sr, 1 if sl.x < sr.x else -1)])
    # S11c: only two dull flat hands at the far end of the rail, the sleeves running off into the fog, no body
    def two_sleeves(name, mk, **kw):
        n0 = set(bpy.data.objects.keys())
        for sd in (-1, 1):
            long_arm(kit, f"{name}.{sd}", mk(sd), **kw)
        return [bpy.data.objects[k] for k in bpy.data.objects.keys() if k not in n0]
    R["far"] = two_sleeves("reach_far", lambda sd: [V((-16.0, RAIL_Y + sd * 0.12, 1.13)), V((1.4, RAIL_Y + sd * 0.12, 1.13))])
    # S91 and S92: the same two hands flat on our bedroom's outside sill, the sleeves running away over the garden into fog
    R["bed"] = two_sleeves("reach_bed", lambda sd: [V((350.0 + sd * 0.17, 45.0, 1.235)), V((350.0 + sd * 0.17, 5.95, 1.235))],
                          skin_c="#aaa2aa", coat_c="#566080", em=("#a9b6dc", 0.12))
    R["far2"] = two_sleeves("reach_far2", lambda sd: [V((-16.0, RAIL_Y + sd * 0.12, 1.13)), V((1.4, RAIL_Y + sd * 0.12, 1.13))],
                            skin_c="#cdbda9", em=("#b8c4e0", 0.12))
    ctx["reach"] = R
    # lights (all off by default, switched by the look)
    L = kit.light
    ctx["sun"] = L("sun", "SUN", (0, 0, 50), 1.0, "#ffd9a0", size=0.6)
    L("moon", "SUN", (0, 0, 50), 1.0, "#7f9fd0", size=2.0)
    L("camfill", "AREA", (0, 0, 3), 1.0, "#ffffff", size=3.0)
    L("lamppost", "POINT", (20.2, -3.0, 2.9), 900, "#ffcf8a", size=0.3)
    L("farlamp", "POINT", (0, 0, 0.3), 60, "#f0a24a", size=0.2)
    L("handlamp", "POINT", (0, 0, 0.3), 30, "#f0a24a", size=0.15)
    L("cab_lamp", "POINT", (21.2, 4.8, 1.55), 260, "#f0a24a", size=0.2)
    L("cab_stove", "POINT", (19.6, 4.1, 0.6), 220, "#e0682a", size=0.25)
    L("cab_amb", "AREA", (20.8, 3.6, 2.5), 450, "#c7d4ee", size=3.0, rot=(0, 0, 0))
    ctx["lights_sill"] = L("sill", "POINT", (19.9, 1.6, 0.6), 40, "#f0a24a", size=0.15)
    L("cin_screen", "AREA", (100, -8.8, 2.3), 2600, "#7a96e8", size=5.0)
    L("cin_amb", "POINT", (100, 1.5, 3.5), 160, "#8a7a9a", size=0.5)
    L("off_amb", "AREA", (130, 4.0, 2.9), 900, "#f4f0e8", size=4.0)
    L("hw_lamp", "POINT", (160, 2.4, 2.2), 160, "#ffd9a0", size=0.3)
    L("sf_amb", "POINT", (190, 1.4, 2.6), 160, "#ffd9a0", size=0.4)
    L("sf_lamp", "POINT", (193, 4.0, 1.3), 80, "#ffc890", size=0.3)
    L("ki_amb", "POINT", (250, 3, 2.6), 200, "#ffe3b8", size=0.4)
    L("ki_win", "AREA", (250, 1.0, 1.5), 800, "#e0ecf4", size=1.2)
    L("bd_amb", "AREA", (350, 2.0, 2.9), 20, "#6a82c0", size=3.0)
    L("bd_in", "POINT", (349.9, 3.6, 1.2), 7, "#9db4e0", size=0.2)
    L("bd_moon", "AREA", (350, 5.9, 6.0), 1500, "#9bb4e6", size=3.0)
    for nm, tg in (("cin_screen", (100, 0, 1.5)), ("ki_win", (250, 3.4, 1.0)), ("bd_moon", (350, 5.7, 1.2))):
        kit.aim(kit.LIGHTS[nm]["obj"], tg)
    L("torch", "SPOT", (0, 0, 1), 400, "#fff0d0", size=0.1, spot=40, blend=0.5)
    L("phone", "POINT", (0, 0, 1), 1.0, "#bcd4ff", size=0.1)
    ctx["phone"] = kit.box("phone", (0.12, 0.03, 0.2), (0, 0, -60), kit.emit("#cfe2ff", 1.2))
    for k in range(8):
        L(f"gl{k}", "POINT", (0, 0, -50), 1.0, GOLD, size=0.12)
    for lt in kit.LIGHTS.values():
        lt["on"] = True
    for nm in ("sun", "moon"):
        kit.aim(kit.LIGHTS[nm]["obj"], (0, 0, 0))
    for nm in ("bd_moon", "bd_amb", "ki_win", "cin_screen", "off_amb"):
        kit.LIGHTS[nm]["obj"].visible_camera = False
    return ctx


# ------------------------------------------------------------------------------------------------ looks
# sky colour, sky strength, fog colour, fog density, fog start, sun (elevation, azimuth from +y toward +x, W/m2, colour),
# moon W/m2, camera fill (W per m2 of distance), then the gain of each named light
LOOKS = {
    "day": dict(sky="#9cc8ec", ss=1.15, fog="#c4dcee", fd=0.004, fs=14, sun=(20, 20, 3.0, "#ffd9a0"), moon=0, fill=2.2,
                lights={"lamppost": 0.0}),
    "summer": dict(sky="#ffc890", ss=1.0, fog="#f3d2a8", fd=0.006, fs=12, sun=(12, 30, 3.4, "#ffc07a"), moon=0, fill=1.0,
                   lights={}),
    "dusk": dict(sky="#4a5a82", ss=1.2, fog="#6b7898", fd=0.014, fs=6, sun=(0, 0, 0.0, "#ffd9a0"), moon=0.5, fill=1.5,
                 lights={"lamppost": 1.0}),
    "nightfog": dict(sky="#34486e", ss=1.5, fog="#44598a", fd=0.03, fs=3, sun=(0, 0, 0.0, "#ffffff"), moon=1.2, fill=0.6,
                     lights={"lamppost": 0.6}),
    "fogpale": dict(sky="#5a6e98", ss=1.8, fog="#6a80aa", fd=0.028, fs=3, sun=(0, 0, 0.0, "#ffffff"), moon=1.4, fill=0.6,
                    lights={"lamppost": 0.5}),
    "fogreach": dict(sky="#5b72a0", ss=2.0, fog="#6479a4", fd=0.012, fs=4, sun=(0, 0, 0.0, "#ffffff"), moon=2.2, fill=0.9,
                     lights={"lamppost": 0.0}),
    "cab_eve": dict(sky="#2a3652", ss=0.7, fog="#2a3652", fd=0.01, fs=8, sun=(0, 0, 0.0, "#ffffff"), moon=0.0, fill=1.8,
                    lights={"cab_lamp": 1.0, "cab_stove": 1.0, "cab_amb": 0.5}),
    "cab_dark": dict(sky="#1b2640", ss=0.6, fog="#1b2640", fd=0.01, fs=8, sun=(0, 0, 0.0, "#ffffff"), moon=0.0, fill=1.9,
                     lights={"cab_lamp": 0.0, "cab_stove": 0.0, "cab_amb": 1.6}),
    "cab_night": dict(sky="#1b2640", ss=0.7, fog="#1b2640", fd=0.01, fs=8, sun=(0, 0, 0.0, "#ffffff"), moon=0.0, fill=1.6,
                      lights={"cab_lamp": 1.0, "cab_stove": 1.0, "cab_amb": 0.5}),
    "cab_low": dict(sky="#1b2640", ss=0.7, fog="#1b2640", fd=0.01, fs=8, sun=(0, 0, 0.0, "#ffffff"), moon=0.0, fill=1.4,
                    lights={"cab_lamp": 1.0, "cab_stove": 1.0, "cab_amb": 0.5}),
    "lean_ext": dict(sky="#5a6e98", ss=1.6, fog="#6a80aa", fd=0.03, fs=3, sun=(0, 0, 0.0, "#ffffff"), moon=1.0, fill=0.9,
                     lights={"cab_lamp": 0.7, "cab_stove": 0.9, "cab_amb": 0.25, "lamppost": 0.0}),
    "bedout": dict(sky="#3c4e74", ss=0.9, fog="#445a84", fd=0.05, fs=3, sun=(0, 0, 0.0, "#ffffff"), moon=0.0, fill=0.4,
                   lights={"bd_amb": 1.0, "bd_moon": 1.0}),
    "cinema": dict(sky="#201820", ss=0.1, fog="#201820", fd=0.0, fs=30, sun=(0, 0, 0.0, "#ffffff"), moon=0, fill=1.0,
                   lights={"cin_screen": 1.0, "cin_amb": 1.0}),
    "office": dict(sky="#c0c8d0", ss=0.3, fog="#c0c8d0", fd=0.0, fs=30, sun=(0, 0, 0.0, "#ffffff"), moon=0, fill=0.8,
                   lights={"off_amb": 1.0}),
    "home": dict(sky="#9cc8ec", ss=0.8, fog="#c4dcee", fd=0.0, fs=30, sun=(16, 200, 2.4, "#ffd9a0"), moon=0, fill=1.3,
                 lights={"hw_lamp": 1.0}),
    "sofa": dict(sky="#40382f", ss=0.2, fog="#40382f", fd=0.0, fs=30, sun=(0, 0, 0.0, "#ffffff"), moon=0, fill=0.8,
                 lights={"sf_amb": 1.0, "sf_lamp": 1.0}),
    "street": dict(sky="#9cc8ec", ss=1.2, fog="#c4dcee", fd=0.004, fs=14, sun=(30, 160, 2.6, "#ffd9a0"), moon=0, fill=1.6,
                   lights={}),
    "kitchen": dict(sky="#9aa8b4", ss=0.5, fog="#b0bcc4", fd=0.0, fs=30, sun=(0, 0, 0.0, "#ffffff"), moon=0, fill=0.8,
                    lights={"ki_amb": 1.0, "ki_win": 1.0}),
    "morning": dict(sky="#b8c4cc", ss=1.3, fog="#c0ccd4", fd=0.008, fs=10, sun=(25, 160, 1.2, "#f0e4d0"), moon=0, fill=1.4,
                    lights={}),
    "bed": dict(sky="#1b2440", ss=0.2, fog="#1b2440", fd=0.0, fs=30, sun=(0, 0, 0.0, "#ffffff"), moon=0, fill=0.0,
                lights={"bd_amb": 1.0}),
}


def _sun_vec(el, az):
    e, a = math.radians(el), math.radians(az)
    return V((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)))


def _fog_nodes(kit):
    if FOG_NODES["built"]:
        return FOG_NODES["mul"], FOG_NODES["col"], FOG_NODES["sub"]
    mul, col, sub = [], [], []
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        for nd in m.node_tree.nodes:
            if nd.type == "MATH" and nd.operation == "EXPONENT":
                src = nd.inputs[0].links[0].from_node if nd.inputs[0].links else None
                if src is not None and src.type == "MATH" and src.operation == "MULTIPLY":
                    mul.append(src)
                    s2 = src.inputs[0].links[0].from_node if src.inputs[0].links else None
                    mx = s2
                    if mx is not None and mx.operation == "MAXIMUM":
                        sb = mx.inputs[0].links[0].from_node
                        sub.append(sb)
            if nd.type == "MIX_SHADER" and len(nd.inputs[0].links) and len(nd.inputs[2].links) and nd.inputs[2].links[0].from_node.type == "EMISSION":
                col.append(nd.inputs[2].links[0].from_node)
    FOG_NODES.update(built=True, mul=mul, col=col, sub=sub)
    return mul, col, sub


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


def _lvl(tl, key, t, default):
    """Sequential easing through every `lvl` cue of this key up to t."""
    cues = [c for c in tl["cues"] if c["name"] == "lvl" and c["key"] == key]
    val = default
    for i, c in enumerate(cues):
        if t < c["t"]:
            break
        ramp = c.get("ramp", 0.0)
        if ramp <= 0:
            val = c["level"]
            continue
        ramp = max(0.3, ramp)
        nxt = cues[i + 1]["t"] if i + 1 < len(cues) else 1e9
        u = ss((min(t, nxt) - c["t"]) / ramp)
        start = val
        val = start + (c["level"] - start) * u
        if t >= c["t"] + ramp or t >= nxt:
            val = c["level"]
    return val


def _lazy(kit, story, tl, ctx):
    """First frame: glow hands, accessories, find the nodes."""
    ctx["lazy"] = True
    ctx["hands"] = {}
    for who, spec in story["cast"].items():
        for sx in (-1, 1):
            sk = bpy.data.objects.get(f"{who}.skinarm{sx}")
            if sk is None:
                continue
            m = kit.plastic(spec["skin"], 0.5, name=f"hand {who}{sx}")
            bsdf = m.node_tree.nodes["Principled BSDF"]
            bsdf.inputs["Emission Color"].default_value = kit.col("#ffa02e")
            bsdf.inputs["Emission Strength"].default_value = 0.0
            sk.data.materials.clear()
            sk.data.materials.append(m)
            sk.scale = (1.03, 1.03, 2.0)
            ctx["hands"][(who, sx)] = (sk, bsdf)
            shells = []
            for si, (rad, al) in enumerate(((0.55, 0.22), (0.72, 0.14), (0.95, 0.08), (1.25, 0.04))):
                bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=32, ring_count=16, location=(0, 0, 0))
                ob = bpy.context.active_object
                ob.name = f"halo.{who}{sx}.{si}"
                ob.parent = sk
                ob.location = (0, 0, -0.04)
                ob.scale = (rad, rad, rad * 0.5)
                ob.visible_shadow = False
                hm = bpy.data.materials.new(f"halo {who}{sx}{si}")
                hm.use_nodes = True
                nt = hm.node_tree
                for nd in list(nt.nodes):
                    nt.nodes.remove(nd)
                em = nt.nodes.new("ShaderNodeEmission")
                em.inputs["Color"].default_value = kit.col(GOLD)
                em.inputs["Strength"].default_value = 1.6
                tr = nt.nodes.new("ShaderNodeBsdfTransparent")
                mx = nt.nodes.new("ShaderNodeMixShader")
                mx.inputs[0].default_value = 0.0
                out = nt.nodes.new("ShaderNodeOutputMaterial")
                nt.links.new(tr.outputs[0], mx.inputs[1])
                nt.links.new(em.outputs[0], mx.inputs[2])
                nt.links.new(mx.outputs[0], out.inputs[0])
                ob.data.materials.append(hm)
                shells.append((mx, al, ob))
            ctx.setdefault("halos", {})[(who, sx)] = shells
    # accessories
    R = 0.62
    for who, spec in story["cast"].items():
        hg = bpy.data.objects.get(f"{who}.headg")
        if hg is None:
            continue
        if spec.get("flatcap"):
            cm = kit.plastic(spec["flatcap"], 0.85)
            top = 0.6
            ctx.setdefault("emrys_cap", []).append(kit.box(f"{who}.fc1", (2 * R + 0.14, 2 * R + 0.14, 0.3), (0, 0.0, top + 0.02), cm, hg, bevel=0.1))
            ctx["emrys_cap"].append(kit.box(f"{who}.fc2", (2 * R + 0.2, 0.6, 0.07), (0, -R - 0.2, top - 0.08), cm, hg, bevel=0.03))
            for sx in (-1, 1):
                lg = bpy.data.objects.get(f"{who}.leg{sx}")
                ctx.setdefault("mud", []).append(kit.box(f"{who}.mud{sx}", (1.04, 1.06, 1.0), (0, 0, -1.35), kit.plastic("#4a3a28", 0.95), lg, bevel=0.1))
        if spec.get("hardhat"):
            hm = kit.plastic("#e0b020", 0.5)
            kit.cyl(f"{who}.hh1", R + 0.1, 0.5, (0, 0, 0.62), hm, hg, n=24, r2=R)
            kit.box(f"{who}.hh2", (2 * R + 0.2, 0.5, 0.06), (0, -R - 0.1, 0.4), hm, hg, bevel=0.02)
        if spec.get("moustache"):
            kit.box(f"{who}.mo", (0.78, 0.14, 0.17), (0, -R - 0.0, -0.1), kit.plastic(spec["moustache"], 0.9), hg, bevel=0.06)
    for who in ("me", "mec", "pk"):
        tor = bpy.data.objects.get(f"{who}.torso")
        if tor is None:
            continue
        ctx.setdefault("slits", {})[who] = [kit.box(f"{who}.slit{sx}", (0.7, 0.04, 0.09), (sx * 0.78, -0.53, 0.5),
                                                      kit.plastic("#d8a050", 0.4, name=f"slit {who}{sx}"), tor) for sx in (-1, 1)]
    # materials' fog nodes
    ctx["fog"] = _fog_nodes(kit)
    ctx["rim_mats"] = []


def _cam(story, tl, t):
    from blocky import bl_story
    shot = _shot(tl, t)
    spec = next(s for s in story["shots"] if s["id"] == shot["id"])
    loc, tgt, lens, roll = bl_story.cam_at(spec, shot, t, {}, tl)
    return V(loc), V(tgt)


GLOW_EM = 0.28
GLOW_LIGHT = 11.0


def animate(kit, story, tl, t, ctx):
    over = {}
    bpy.context.scene.cycles.transparent_max_bounces = 32
    if not ctx["lazy"]:
        _lazy(kit, story, tl, ctx)
    shot = _shot(tl, t)
    spec = ctx["spec"][shot["id"]]
    look = LOOKS[spec.get("look", "day")]
    c = lambda h: kit.col(h)[:3]
    mixc = lambda a, b, u: tuple(x + (y - x) * u for x, y in zip(a, b))
    cam, tgt = _cam(story, tl, t)
    # ---- sky, fog
    w = bpy.context.scene.world.node_tree.nodes["Background"]
    w.inputs["Color"].default_value = (*c(look["sky"]), 1)
    w.inputs["Strength"].default_value = look["ss"] * spec.get("sky_k", 1.0)
    mul, cols, subs = ctx["fog"]
    fd = spec.get("fd", look["fd"])
    for nd in mul:
        nd.inputs[1].default_value = -max(fd, 1e-6)
    for nd in subs:
        nd.inputs[1].default_value = spec.get("fs", look["fs"])
    fc_ = c(spec.get("fogc", look["fog"]))
    for nd in cols:
        nd.inputs["Color"].default_value = (*fc_, 1)
    # ---- sun, moon, camera fill
    el, az, se, scol = look["sun"]
    if "sun" in spec:
        el, az, se, scol = spec["sun"]
    sun = kit.LIGHTS["sun"]
    sun["obj"].rotation_euler = (-_sun_vec(el, az)).to_track_quat("-Z", "Y").to_euler()
    sun["light"].color = c(scol)
    over["sun"] = se
    moon = kit.LIGHTS["moon"]
    moon["obj"].rotation_euler = (-_sun_vec(35, spec.get("moon_az", 200))).to_track_quat("-Z", "Y").to_euler()
    over["moon"] = look["moon"] * spec.get("moon_k", 1.0)
    cf = kit.LIGHTS["camfill"]
    fwd = tgt - cam
    dist = max(1.0, fwd.length)
    cf["obj"].location = cam + V((0, 0, 0.1))
    cf["obj"].rotation_euler = fwd.to_track_quat("-Z", "Y").to_euler()
    over["camfill"] = look["fill"] * spec.get("fill_k", 1.0) * min(dist, 10.0) ** 2 * 0.6
    # ---- named lights
    for name in kit.LIGHTS:
        if name in look["lights"]:
            over[name] = look["lights"][name] * spec.get("lk", {}).get(name, 1.0)
        elif name not in over and not name.startswith("gl") and name not in ("torch", "phone"):
            over[name] = spec.get("lk", {}).get(name, 0.0)
    lamp = _lvl(tl, "lamp", t, 1.0)
    stove = _lvl(tl, "stove", t, 1.0)
    over["cab_lamp"] = over.get("cab_lamp", 0.0) * lamp
    over["cab_stove"] = over.get("cab_stove", 0.0) * stove
    # ---- the emissive lamp and fire follow the same levels
    if spec.get("look", "") in ("cab_dark",):
        lamp_e, fire_e = 0.0, 0.0
    else:
        lamp_e, fire_e = lamp, stove
    ctx["lampmat"].node_tree.nodes["Emission"].inputs["Strength"].default_value = 3.0 * lamp_e
    ctx["firemat"].node_tree.nodes["Emission"].inputs["Strength"].default_value = 3.5 * fire_e
    # ---- the screen: slow drifting colour (never a flicker)
    scr = bpy.data.materials["screenmat"].node_tree.nodes["Emission"]
    ph = 0.5 + 0.5 * math.sin(t * 0.35)
    scr.inputs["Color"].default_value = (*mixc(c("#5f7fd0"), c("#b878c8"), ph), 1)
    # ---- the bridge: shut, or swung open for the summer memories
    ctx["span"].rotation_euler = (0, 0, math.radians(-78 if spec.get("open") else 0))
    for o in ctx["boat"]:
        o.hide_render = not spec.get("boat")
    if spec.get("boat"):
        u = (t - shot["start"])
        bx, by = spec.get("boat_x", 14.8), spec.get("boat_y0", -4.0) + 0.55 * u
        base = {"hull": (0, 0, 0), "cabinb": (-0.4, 0, 0.45), "mast": (0.4, 0, 1.7), "sail": (-0.35, 0, 1.9)}
        for o in ctx["boat"]:
            dx, dy, dz = base[o.name.split(".")[0]]
            o.location = (bx + dy, by + dx, -0.85 + dz)
            o.rotation_euler = (0, 0, math.pi / 2)
    for o in ctx["bar"]:
        o.hide_render = bool(spec.get("nobar"))
    for o in ctx["streaks"]:
        o.hide_render = not spec.get("streaks")
    # ---- the far road bridge's car lights: slow and steady
    for i, o in enumerate(ctx["cars"]):
        x = -60 + ((t * 1.1 + i * 24) % 160) - 0.0
        o.location = (x if i % 2 else 78 - ((t * 1.1 + i * 24) % 160), o.location.y, 10.3)
    # ---- the cabin: sash, door, stools, cap, mugs, steam
    sup = spec.get("sash", False)
    gone = spec.get("reach") in ("lean", "stand") or bool(spec.get("nosash"))
    ctx["mullion"].hide_render = bool(spec.get("nosash"))
    for o, off in zip(ctx["sash"], ctx["sash_off"]):
        o.hide_render = gone
        o.location.z = (1.6 if sup else 0.9) + off + (0.0 if o.name != "sash_g" else 0.0) - (0.0)
    ctx["door"].rotation_euler = (0, 0, math.radians(spec.get("door", 0)))
    ctx["stool2"].rotation_euler = (0, 0, math.radians(spec.get("stool2", 180)))
    for o in ctx["hangcap"]:
        o.hide_render = not spec.get("hangcap")
    for o in ctx["steam"]:
        o.hide_render = not spec.get("steam", True)
    # ---- the Reach: one model at a time
    rv = spec.get("reach") or ("bed" if spec.get("bedreach") else None)
    for k, obs in ctx["reach"].items():
        for o in obs:
            o.hide_render = k != rv
    if "reach_lean" in CH:
        CH["reach_lean"].neck.rotation_euler = (spec.get("hpitch", -0.62), 0, spec.get("hyaw", 0.0))
    over["farlamp"] = 0.0
    over["handlamp"] = 0.0
    over["sill"] = 0.0
    if rv in ("mon", "tue", "wed"):
        xe = {"mon": 6.0, "tue": 9.0, "wed": 17.8}[rv]
        kit.LIGHTS["farlamp"]["obj"].location = (-0.35, RAIL_Y - 0.55, 0.28)
        kit.LIGHTS["handlamp"]["obj"].location = (xe - 0.15, RAIL_Y - 0.4, 0.4)
        over["farlamp"] = spec.get("farlamp", 1.0)
        over["handlamp"] = spec.get("handlamp", 1.0)
    elif rv == "far2":
        kit.LIGHTS["handlamp"]["obj"].location = tuple(spec.get("hl_pos", (1.0, 0.3, 0.5)))
        over["handlamp"] = spec.get("handlamp", 1.0)
    elif rv in ("stand", "lean"):
        kit.LIGHTS["farlamp"]["obj"].location = tuple(spec.get("fl_pos", (20.0, 1.0, 0.35)))
        kit.LIGHTS["handlamp"]["obj"].location = (0.35, RAIL_Y - 0.4, 0.4)
        kit.LIGHTS["sill"]["obj"].location = (20.1, 1.9, 0.58)
        over["farlamp"] = spec.get("farlamp", 0.8)
        over["handlamp"] = spec.get("handlamp", 1.0)
        over["sill"] = spec.get("sill", 1.0)
    # ---- props
    for o in ctx["prints"]:
        o.hide_render = not spec.get("prints")
    for o in ctx["lprints"]:
        o.hide_render = not spec.get("lprints")
    ctx["crate"].location = spec.get("crate", (0, 0, -60))
    mg = spec.get("mug", (249.7, 3.3))
    ctx["kmug"].location = (mg[0], mg[1], 0.86)
    for o in ctx.get("emrys_cap", []):
        o.hide_render = bool(spec.get("nocap"))
    for o in ctx.get("mud", []):
        o.hide_render = not spec.get("mud")
    over["torch"] = 0.0
    over["phone"] = 0.0
    ctx["phone"].location = (0, 0, -60)
    if spec.get("torch"):
        m = acting.state(tl, "mec", t)
        kit.LIGHTS["torch"]["obj"].location = (m["x"] + 0.35, m["y"] - 0.3, 1.0)
        kit.aim(kit.LIGHTS["torch"]["obj"], (m["x"] + 1.2, m["y"] - 4.5, 0.0))
        over["torch"] = 1.0
    if spec.get("phone"):
        m = acting.state(tl, "mec", t)
        h = ctx["hands"].get(("mec", 1))
        if h is not None:
            hp = h[0].matrix_world.translation
            ctx["phone"].location = (hp.x - 0.02, hp.y - 0.14, hp.z + 0.1)
        kit.LIGHTS["phone"]["obj"].location = (m["x"], m["y"] - 0.5, 1.35)
        over["phone"] = 7.0
    # ---- who sits; the glow hands
    bpy.context.view_layer.update()
    pool = []
    for who in story["cast"]:
        keys = tl["acting"].get(who, [])
        st = acting.state(tl, who, t)
        if acting._switch(keys, "sit", t, False):
            for sx in (-1, 1):
                lg = bpy.data.objects.get(f"{who}.leg{sx}")
                if lg is not None:
                    lg.rotation_euler = (-math.radians(88), 0, 0)
        g = _lvl(tl, f"glow.{who}", t, 0.0)
        for sx in (-1, 1):
            h = ctx["hands"].get((who, sx))
            if h is None:
                continue
            sk, bsdf = h
            hidden = st["hidden"]
            bsdf.inputs["Emission Strength"].default_value = 0.0 if hidden else GLOW_EM * g * spec.get("em_k", 1.0)
            bsdf.inputs["Emission Color"].default_value = kit.col("#ffcf80")
            for mx, al, ob_ in ctx.get("halos", {}).get((who, sx), []):
                mx.inputs[0].default_value = 0.0 if hidden else al * min(1.0, g * 1.3)
                ob_.hide_render = hidden or g < 0.02
                ob_.data.materials[0].node_tree.nodes["Emission"].inputs["Strength"].default_value = 1.6 * spec.get("halo_k", 1.0)
            sk0 = story["cast"][who]["skin"]
            a_ = kit.col(sk0)
            b_ = kit.col("#f2b858")
            u_ = min(1.0, g * 1.2)
            bsdf.inputs["Base Color"].default_value = tuple(x + (y - x) * u_ for x, y in zip(a_, b_))
            if __import__('os').environ.get('DBGH') and True:
                open('/tmp/claude-0/dbg.txt', 'a').write(f"{shot['id']} {sx} {tuple(round(v,2) for v in sk.matrix_world.translation)}\n")
            if not hidden and g > 0.02:
                hp_ = sk.matrix_world.translation.copy()
                tc_ = (cam - hp_)
                tc_ = tc_.normalized() * 0.32 if tc_.length > 0.01 else V((0, 0, 0))
                pool.append((g, hp_ + tc_))
        sl = ctx.get("slits", {}).get(who)
        if sl:
            pg = _lvl(tl, f"pocket.{who}", t, 0.0)
            for o in sl:
                m = o.data.materials[0].node_tree.nodes["Principled BSDF"]
                m.inputs["Emission Color"].default_value = kit.col(GOLD)
                m.inputs["Emission Strength"].default_value = 1.8 * pg
                o.hide_render = pg < 0.02
                if pg > 0.02:
                    sp_ = o.matrix_world.translation.copy()
                    tc_ = cam - sp_
                    pool.append((pg * 0.45, sp_ + (tc_.normalized() * 0.2 if tc_.length > 0.01 else V((0, 0, 0)))))
    pool.sort(key=lambda p: (p[1] - cam).length - 4 * p[0])
    for k in range(8):
        name = f"gl{k}"
        if k < len(pool):
            g, pos = pool[k]
            kit.LIGHTS[name]["obj"].location = pos + V((0, 0, 0.05))
            over[name] = GLOW_LIGHT * g * spec.get("glow_k", 1.0)
        else:
            over[name] = 0.0
    return over
