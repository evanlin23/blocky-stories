"""Corn Maze (ep95): the narrator is the maze itself. Gold corn, straw paths, twelve iron lanterns, one big face of paths.

SCENES live 400 m apart (geo.ORG) so a shot never sees another's props. Each scene is a 40 x 64 m field of corn on a 0.5 m
cell grid cut with path shapes (geo.layout_shapes). A "layout" is built lazily the first time a shot asks for it (story
"shot_layout"), once, and shown only in the shots that name it, so a path is open in one shot and different in the next
and never moves on screen. Stalks rustle (the leaf and tassel meshes shake against the stalks) and lean toward the paths.

THE MARKER (the rule meter): twelve lantern icons parented to the camera's top-left corner, each fading with its
lantern (cues out0..out11 and icon_up). THE LOOKS (LOOKS) set the suns, the world and the corn colours per shot and blend
from the lantern look into moonlight when the last lantern is out (cue "moon").
Nothing here has text, and no two surfaces share a plane.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import geo as G  # noqa: E402

CELL = G.CELL


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------------------------------------ the corn
BOX_FACES_NP = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]


def build_corn(kit, name, origin, mats, shapes, lean=None, w=G.FW, h=G.FH, hmax=2.0, leaf=1.0, stalk=1.0, nbl=4, yband=None):
    """On every wall cell a stalk, a tassel and nbl long leaf blades arcing out and down. Returns (body, leaves, tassels).
    lean: None, (lx, ly) or a function (x, y) -> (lx, ly): the top of a stalk shifts by lean * z / 2.5."""
    import numpy as np
    nx, ny = int(w / CELL), int(h / CELL)
    rng = np.random.default_rng(95)
    R = rng.random((nx, ny, 32))
    keep = []
    xs = [-w / 2 + (i + 0.5) * CELL for i in range(nx)]
    ys = [-h / 2 + (j + 0.5) * CELL for j in range(ny)]
    for i in range(nx):
        for j in range(ny):
            x, y = xs[i], ys[j]
            if not any(s(x, y) for s in shapes) and (yband is None or yband[0] <= y < yband[1]):
                keep.append((i, j))
    ij = np.array(keep, dtype=int)
    N = len(ij)
    Rk = R[ij[:, 0], ij[:, 1]]
    cx = np.array(xs)[ij[:, 0]] + origin[0]
    cy = np.array(ys)[ij[:, 1]] + origin[1]
    if lean is None:
        lx = ly = np.zeros(N)
    elif callable(lean):
        L = np.array([lean(xs[i], ys[j]) for i, j in keep])
        lx, ly = L[:, 0], L[:, 1]
    else:
        lx, ly = np.full(N, lean[0]), np.full(N, lean[1])
    hh = hmax + 0.8 * (Rk[:, 0] - 0.5)
    hw = (0.15 + 0.03 * Rk[:, 1]) * stalk
    jx, jy = (Rk[:, 2] - 0.5) * 0.12, (Rk[:, 3] - 0.5) * 0.12
    signs = np.array([(-1, -1), (1, -1), (1, 1), (-1, 1)], dtype=float)

    def prism(z0, z1, a0, a1):
        v = np.zeros((N, 8, 3))
        for lvl, (z, a) in enumerate(((z0, a0), (z1, a1))):
            for q in range(4):
                v[:, lvl * 4 + q, 0] = cx + jx + signs[q, 0] * a + lx * z / 2.5
                v[:, lvl * 4 + q, 1] = cy + jy + signs[q, 1] * a + ly * z / 2.5
                v[:, lvl * 4 + q, 2] = z
        return v

    def faces_for(count, per, pattern):
        base = (np.arange(count) * per)[:, None, None]
        return (base + np.array(pattern)[None, :, :]).reshape(-1, 4)

    body_v = prism(np.zeros(N), hh, hw, hw * 0.8)
    top_v = prism(hh - 0.05, hh + 0.16, hw * 0.9, np.full(N, 0.05))
    prof = ((0.05, 0.0, 0.09), (0.26, 0.12, 0.13), (0.46, 0.1, 0.11), (0.62, -0.08, 0.03))
    lv = np.zeros((N, nbl, len(prof) * 2, 3))
    for b in range(nbl):
        ang = (b / nbl + 0.15 * Rk[:, 10 + b]) * 2 * np.pi + Rk[:, 5] * 6.28
        z0 = hh * (0.35 + 0.5 * b / nbl + 0.05 * Rk[:, 16 + b])
        ca, sa = np.cos(ang), np.sin(ang)
        for p, (o, u, wd) in enumerate(prof):
            for s_i, sg in enumerate((-1, 1)):
                z = z0 + u * leaf
                lv[:, b, p * 2 + s_i, 0] = cx + jx + ca * o * leaf + (-sa) * wd * leaf * sg + lx * z / 2.5
                lv[:, b, p * 2 + s_i, 1] = cy + jy + sa * o * leaf + ca * wd * leaf * sg + ly * z / 2.5
                lv[:, b, p * 2 + s_i, 2] = z
    lpat = [(2 * q, 2 * q + 1, 2 * q + 3, 2 * q + 2) for q in range(len(prof) - 1)]
    body = kit.mesh_obj(f"corn.{name}", body_v.reshape(-1, 3).tolist(), faces_for(N, 8, BOX_FACES_NP).tolist(), mats["corn"])
    leaves = kit.mesh_obj(f"corn.{name}.leaf", lv.reshape(-1, 3).tolist(),
                          faces_for(N * nbl, len(prof) * 2, lpat).tolist(), mats["leaf"])
    tops = kit.mesh_obj(f"corn.{name}.top", top_v.reshape(-1, 3).tolist(), faces_for(N, 8, BOX_FACES_NP).tolist(), mats["tassel"])
    return body, leaves, tops


def lean_in(shapes, k=0.5, reach=2.0):
    """A stalk leans toward the nearest path (within reach metres), so the walls bow in over it."""
    dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))

    def f(x, y):
        for d in range(1, int(reach / CELL) + 1):
            for dx, dy in dirs:
                px, py = x + dx * d * CELL, y + dy * d * CELL
                if any(s(px, py) for s in shapes):
                    q = k * (1.0 if d <= 3 else 0.7)
                    return (dx * q, dy * q)
        return (0.0, 0.0)
    return f


LAYOUT_CFG = {
    "face": dict(nbl=4), "partial": dict(nbl=3, hmax=1.35, leaf=0.9), "star": dict(nbl=3), "tractor": dict(nbl=3), "pig": dict(nbl=3),
    "entrance": dict(nbl=5, leaf=1.25, stalk=0.8, lean=(0.0, -0.5)), "day": dict(nbl=4, leaf=1.1, lean="in"),
    "closed": dict(nbl=4, leaf=1.1, lean="in", k=0.6), "open": dict(nbl=4, leaf=1.1, lean="in", k=0.6),
    "summer": dict(nbl=4, hmax=1.3, leaf=0.9, lean="in", k=0.25), "dawn": dict(nbl=4, leaf=1.1, lean="in", k=0.35),
    "nosid": dict(nbl=4, leaf=1.1, lean="in", k=0.6), "sealed": dict(nbl=4, leaf=1.1, lean="in", k=0.6),
    "curve": dict(nbl=4, leaf=1.1, lean="in", k=0.35), "herface": dict(nbl=4, bands=8),
}


def make_layout(kit, name, M):
    cfg = dict(LAYOUT_CFG[name])
    shapes = G.layout_shapes(name)
    lean = cfg.pop("lean", None)
    k = cfg.pop("k", 0.45)
    if lean == "in":
        lean = lean_in(shapes, k)
    w, h = G.SIZE.get(name, (G.FW, G.FH))
    nb = cfg.pop("bands", 1)
    trip = []
    for q in range(nb):
        yb = None if nb == 1 else (-h / 2 + q * h / nb, -h / 2 + (q + 1) * h / nb)
        o = build_corn(kit, name if nb == 1 else f"{name}.b{q}", G.ORG[name], M, shapes, lean=lean, w=w, h=h, yband=yb, **cfg)
        yc = 0.0 if yb is None else (yb[0] + yb[1]) / 2
        trip.append((o, yc))
    for o, _ in trip:
        for ob in o:
            ob.hide_render = True
    return trip


# ------------------------------------------------------------------------------------------------ materials
CORN_KEYS = ("corn", "leaf", "tassel", "straw", "grass")


def materials(kit):
    M = {
        "corn": kit.plastic("#d2ae3c", 0.85, "corn body", spec=0.1),
        "leaf": kit.plastic("#e6c552", 0.8, "corn leaf", spec=0.12),
        "tassel": kit.plastic("#d9b645", 0.8, "corn tassel", spec=0.1),
        "straw": kit.plastic("#e8d39a", 0.95, "straw", spec=0.05),
        "grass": kit.plastic("#27443f", 0.95, "ground grass", spec=0.05),
        "iron": kit.plastic("#2b2b30", 0.5, "iron", spec=0.4),
        "pole": kit.plastic("#7a5230", 0.8, "pole", spec=0.1),
        "stroke": kit.emit("#f2c94c", 1.0, "stroke"),
        "quilt1": kit.plastic("#d8443a", 0.9, "quilt red", spec=0.05),
        "quilt2": kit.plastic("#f2c94c", 0.9, "quilt gold", spec=0.05),
        "quilt3": kit.plastic("#3d6ea6", 0.9, "quilt blue", spec=0.05),
        "quilt4": kit.plastic("#7ccf5a", 0.9, "quilt green", spec=0.05),
        "torch": kit.emit("#ffd8a0", 1.6, "torch"),
        "halo": kit.emit("#ffc070", 0.9, "halo"),
        "halo2": kit.emit("#ffb050", 0.45, "halo2"),
        "plate": kit.plastic("#14121c", 0.9, "icon plate", spec=0.05),
        "i_pole": kit.plastic("#c99a62", 0.8, "icon pole", spec=0.05),
        "i_iron": kit.plastic("#9a98a6", 0.6, "icon iron", spec=0.1),
        "i_flame": kit.emit("#fff2a8", 1.8, "icon flame"),
        "i_glass_dark": kit.plastic("#1c1a24", 0.9, "icon glass dark", spec=0.05),
        "wood": kit.plastic("#9a6a3c", 0.8, "wood", spec=0.05),
        "wood2": kit.plastic("#c9a06a", 0.8, "pale wood", spec=0.05),
        "orange": kit.plastic("#ff7a1f", 0.55, "pumpkin", spec=0.2),
        "stem": kit.plastic("#5a7a2a", 0.8, "stem", spec=0.05),
        "hay": kit.plastic("#e0bc58", 0.95, "hay", spec=0.03),
        "strap": kit.plastic("#7a4a2a", 0.8, "strap", spec=0.05),
        "cloth1": kit.plastic("#3d6ea6", 0.9, "scarecrow shirt", spec=0.05),
        "sack": kit.plastic("#d8c08a", 0.95, "sack", spec=0.03),
        "ink": kit.plastic("#1d1710", 0.9, "ink", spec=0.03),
        "dark": kit.plastic("#23232a", 0.6, "dark", spec=0.2),
        "glasswin": kit.plastic("#9fb8d0", 0.2, "cab glass", spec=0.6),
        "box": kit.plastic("#b98a54", 0.9, "cardboard", spec=0.03),
        "box2": kit.plastic("#cfa56c", 0.9, "cardboard light", spec=0.03),
        "barn": kit.plastic("#a83a30", 0.8, "barn red", spec=0.05),
        "roof": kit.plastic("#4a4f5c", 0.8, "roof", spec=0.05),
        "wall": kit.plastic("#efe6d4", 0.8, "house wall", spec=0.05),
        "wall2": kit.plastic("#7fa3c8", 0.8, "new house wall", spec=0.05),
        "trim": kit.plastic("#fbf8f0", 0.7, "trim", spec=0.05),
        "interior": kit.plastic("#f2dcc0", 0.9, "interior", spec=0.03),
        "floor": kit.plastic("#8a6a48", 0.9, "floor", spec=0.03),
        "mower": kit.plastic("#d8443a", 0.5, "mower red", spec=0.3),
        "steel": kit.plastic("#b8bcc4", 0.35, "steel", spec=0.5),
        "thermos": kit.plastic("#2f8f6a", 0.4, "thermos", spec=0.4),
        "cup": kit.plastic("#f4efe4", 0.5, "cup", spec=0.3),
        "cocoa": kit.plastic("#5a3322", 0.4, "cocoa", spec=0.3),
        "steam": kit.emit("#f4f6ff", 0.9, "steam"),
        "cob": kit.plastic("#f2c94c", 0.6, "cob", spec=0.2),
        "husk": kit.plastic("#7ccf5a", 0.8, "husk", spec=0.05),
        "shoot": kit.plastic("#7ccf5a", 0.7, "shoot", spec=0.1),
        "flash_body": kit.plastic("#d8443a", 0.4, "flashlight", spec=0.4),
        "lens": kit.emit("#fff0c8", 3.0, "flash lens"),
        "glow": kit.emit("#ffb347", 0.7, "pane glow"),
        "row1": kit.plastic("#2c4a3c", 0.95, "crop row a", spec=0.03),
        "row2": kit.plastic("#223d34", 0.95, "crop row b", spec=0.03),
        "stubble": kit.plastic("#58563a", 0.95, "stubble", spec=0.03),
        "dirt": kit.plastic("#6b5a45", 0.95, "farm dirt", spec=0.03),
        "hedge": kit.plastic("#1a3426", 0.95, "hedge", spec=0.03),
        "silo": kit.plastic("#aeb4bf", 0.6, "silo", spec=0.2),
        "braid1": kit.plastic("#cfd2da", 0.7, "braid a", spec=0.1),
        "braid2": kit.plastic("#8f94a2", 0.7, "braid b", spec=0.1),
        "tie": kit.plastic("#d8443a", 0.6, "hair tie", spec=0.1),
        "moon": kit.emit("#eef3ff", 2.6, "moon disc"),
        "moonhalo": kit.emit("#7f96d8", 0.5, "moon halo"),
        "star": kit.emit("#dfe8ff", 2.2, "star"),
    }
    return M


# ------------------------------------------------------------------------------------------------ lanterns
def build_lantern(kit, ctx, M, k, ox, oy, tally=False, energy=260.0, zb=2.55):
    """An iron lantern on a pole. Its flame, glass and light have their own materials so it can fade by itself."""
    mats = {"fl": kit.emit("#ff7a12", 1.8, f"lflame{k}"), "core": kit.emit("#ffe888", 2.0, f"lcore{k}"),
            "pane": kit.emit("#ffb347", 0.4, f"lpane{k}"), "side": kit.emit("#ffb347", 0.25, f"lside{k}")}
    kit.box(f"lant{k}.pole", (0.2, 0.2, zb - 0.05), (ox, oy, (zb - 0.05) / 2), M["pole"], bevel=0.02)
    if tally:   # the lore tally: two gold strokes on the pole's south and north faces, 1.5 cm proud
        for q in range(2):
            kit.box(f"lant{k}.stroke{q}", (0.035, 0.03, 0.34), (ox - 0.035 + q * 0.07, oy - 0.1 - 0.015, 1.35), M["stroke"])
            kit.box(f"lant{k}.strokeN{q}", (0.035, 0.03, 0.34), (ox - 0.035 + q * 0.07, oy + 0.1 + 0.015, 1.35), M["stroke"])
    z = zb
    kit.box(f"lant{k}.base", (0.42, 0.42, 0.08), (ox, oy, z), M["iron"], bevel=0.015)
    kit.box(f"lant{k}.back", (0.34, 0.02, 0.44), (ox, oy + 0.17, z + 0.27), mats["pane"])
    for sx in (-1, 1):
        kit.box(f"lant{k}.side", (0.02, 0.34, 0.44), (ox + sx * 0.17, oy, z + 0.27), mats["side"])
    kit.cyl(f"lant{k}.wick", 0.03, 0.06, (ox, oy, z + 0.07), M["iron"], n=6)
    fl = kit.empty(f"lant{k}.fl", (ox, oy - 0.02, z + 0.1))
    kit.sphere(f"lant{k}.bulb", 0.09, (0, 0, 0.03), mats["fl"], parent=fl, seg=10)
    kit.cyl(f"lant{k}.tip", 0.08, 0.28, (0, 0, 0.15), mats["fl"], parent=fl, n=8, r2=0.006)
    kit.sphere(f"lant{k}.cbulb", 0.038, (0, -0.06, 0.02), mats["core"], parent=fl, seg=8)
    kit.cyl(f"lant{k}.ctip", 0.032, 0.14, (0, -0.06, 0.07), mats["core"], parent=fl, n=6, r2=0.004)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"lant{k}.bar", (0.04, 0.04, 0.46), (ox + sx * 0.2, oy + sy * 0.2, z + 0.27), M["iron"])
    kit.box(f"lant{k}.cap", (0.5, 0.5, 0.07), (ox, oy, z + 0.53), M["iron"], bevel=0.015)
    kit.cyl(f"lant{k}.roof", 0.3, 0.2, (ox, oy, z + 0.67), M["iron"], n=4, r2=0.05, rot=(0, 0, math.pi / 4))
    kit.box(f"lant{k}.ring", (0.05, 0.3, 0.05), (ox, oy, z + 0.84), M["iron"])
    kit.light(f"lant{k}.light", "POINT", (ox, oy - 0.1, z + 0.3), energy, "#ffb347", size=0.12)
    ctx["lanterns"][k] = {"mats": mats, "fl": fl, "energy": energy,
                          "base": {"fl": 1.8, "core": 2.0, "pane": 0.4, "side": 0.25}}


def set_lantern(ctx, kit, k, g, wobble=1.0, light_mult=1.0):
    d = ctx["lanterns"][k]
    for key, base in d["base"].items():
        d["mats"][key].node_tree.nodes["Emission"].inputs["Strength"].default_value = base * g
    sc = max(0.001, g) * wobble
    d["fl"].scale = (max(0.001, g) ** 0.5, max(0.001, g) ** 0.5, sc)
    d["fl"].hide_render = g < 0.02
    kit.LIGHTS[f"lant{k}.light"]["base"] = d["energy"] * g * light_mult


# ------------------------------------------------------------------------------------------------ the marker
def build_marker(kit, M, ctx):
    """Twelve lantern-on-a-pole icons, 4 x 3, about 27% of the frame width, parented to the camera's top-left."""
    cam = kit.OBJ["cam"]
    root = kit.empty("marker", (0, 0, 0), parent=cam)
    ctx["icons"] = []
    d = 1.6
    px, py = 0.034, -0.054
    x0, y0 = -0.274 + px / 2, 0.488 - 0.027
    kit.box("marker.plate", (px * 4, -py * 3, 0.004), (-0.274 + px * 2, 0.488 + py * 1.5, -d - 0.02), M["plate"], parent=root)
    for n in range(12):
        r, c = divmod(n, 4)
        e = kit.empty(f"icon{n}", (x0 + c * px, y0 + r * py, -d), parent=root)
        e.scale = (0.38, 0.38, 0.38)
        glass = kit.emit("#ff9a2a", 1.6, f"icon glass lit {n}")
        kit.box(f"icon{n}.pole", (0.02, 0.05, 0.01), (0, -0.03, 0.0), M["i_pole"], parent=e)
        kit.box(f"icon{n}.base", (0.07, 0.012, 0.012), (0, -0.004, 0.002), M["i_iron"], parent=e)
        kit.box(f"icon{n}.glass.d", (0.056, 0.056, 0.012), (0, 0.032, 0.0), M["i_glass_dark"], parent=e)
        kit.box(f"icon{n}.glass", (0.056, 0.056, 0.012), (0, 0.032, 0.004), glass, parent=e)
        fl = kit.cyl(f"icon{n}.flame", 0.014, 0.04, (0.002, 0.026, 0.012), M["i_flame"], n=6, r2=0.003, rot=(math.pi / 2, 0, 0), parent=e)
        for sx in (-1, 1):
            kit.box(f"icon{n}.bar", (0.008, 0.06, 0.014), (sx * 0.03, 0.032, 0.004), M["i_iron"], parent=e)
        kit.box(f"icon{n}.cap", (0.07, 0.01, 0.012), (0, 0.064, 0.002), M["i_iron"], parent=e)
        kit.cyl(f"icon{n}.roof", 0.045, 0.014, (0, 0.078, 0.002), M["i_iron"], n=3, rot=(0, 0, math.pi / 2), parent=e)
        ctx["icons"].append({"glass": glass, "flame": fl})


# ------------------------------------------------------------------------------------------------ props
def bx(kit, name, size, loc, mat, **kw):
    return kit.box(name, size, loc, mat, **kw)


def build_scarecrow(kit, M, ox, oy):
    root = kit.empty("scarecrow", (ox, oy, 0))
    kit.box("sc.post", (0.12, 0.12, 2.3), (0, 0, 1.15), M["wood"], parent=root)
    kit.box("sc.body", (0.6, 0.34, 0.75), (0, 0, 1.45), M["cloth1"], parent=root, bevel=0.03)
    kit.box("sc.belt", (0.62, 0.36, 0.08), (0, 0, 1.08), M["strap"], parent=root)
    kit.box("sc.armL", (1.5, 0.12, 0.12), (-0.95, 0, 1.68), M["cloth1"], parent=root)       # pointing to its left (-x)
    kit.box("sc.handL", (0.22, 0.2, 0.2), (-1.78, 0, 1.68), M["hay"], parent=root)
    kit.box("sc.armR", (0.12, 0.12, 0.7), (0.4, 0, 1.4), M["cloth1"], parent=root)           # the other hangs
    kit.box("sc.handR", (0.2, 0.2, 0.24), (0.4, 0, 1.0), M["hay"], parent=root)
    kit.sphere("sc.head", 0.26, (0, 0, 2.02), M["sack"], parent=root, seg=12)
    for sx in (-1, 1):
        kit.box("sc.eye", (0.07, 0.03, 0.07), (sx * 0.1, -0.235, 2.06), M["ink"], parent=root)
    kit.box("sc.mouth", (0.2, 0.03, 0.04), (0, -0.24, 1.94), M["ink"], parent=root)
    kit.cyl("sc.brim", 0.44, 0.04, (0, 0, 2.2), M["hay"], parent=root, n=14)
    kit.cyl("sc.crown", 0.22, 0.2, (0, 0, 2.32), M["hay"], parent=root, n=12)
    for i in range(5):    # straw sticking out of the shirt hem
        kit.box("sc.straw", (0.04, 0.04, 0.3), (-0.24 + i * 0.12, -0.05, 0.95), M["hay"], parent=root, rot=(0.15, 0, 0.1 * (i - 2)))


def build_pumpkin(kit, M, ox, oy):
    root = kit.empty("pumpkin", (ox, oy, 0))
    p = kit.sphere("pk.body", 0.8, (0, 0, 0.62), M["orange"], parent=root, seg=20)
    p.scale = (1.0, 1.0, 0.8)
    for k in range(6):
        a = k * math.pi / 3
        r = kit.sphere("pk.rib", 0.34, (0.5 * math.cos(a), 0.5 * math.sin(a), 0.62), M["orange"], parent=root, seg=10)
        r.scale = (0.55, 0.55, 1.5)
    kit.box("pk.stem", (0.16, 0.16, 0.3), (0, 0, 1.28), M["stem"], parent=root, rot=(0.15, 0, 0.3))


def build_bales(kit, M, ox, oy):
    for i, (dx, dy, z) in enumerate(((0, 0, 0.25), (0, -1.1, 0.25), (0, -0.55, 0.75), (-1.1, 0.0, 0.25))):
        kit.box(f"bale{i}", (0.5, 1.0, 0.5), (ox + dx, oy + dy, z), M["hay"], bevel=0.03)
        for s in (-0.28, 0.28):
            kit.box(f"bale{i}.strap", (0.52, 0.04, 0.52), (ox + dx, oy + dy + s, z), M["strap"])


def build_board(kit, M, ox, oy):
    """The entrance board: two posts and a pale board with one arrow glyph of our own (no letters)."""
    for sx in (-0.62, 0.62):
        kit.box("board.post", (0.12, 0.12, 2.0), (ox + sx, oy, 1.0), M["wood"])
    kit.box("board", (1.4, 0.08, 0.95), (ox, oy, 1.55), M["wood2"], bevel=0.02)
    kit.box("board.shaft", (0.7, 0.04, 0.14), (ox - 0.12, oy - 0.05, 1.55), M["strap"])
    kit.cyl("board.head", 0.28, 0.04, (ox + 0.4, oy - 0.05, 1.55), M["strap"], n=3, rot=(math.pi / 2, 0, 0))


def build_phone(kit, M, name, loc, up=False):
    s = kit.box(name, (0.075, 0.15, 0.014), loc, M["dark"], bevel=0.005)
    if up:
        kit.box(name + ".scr", (0.065, 0.14, 0.004), (loc[0], loc[1], loc[2] + 0.009), M["lens"])
    return s


def build_barn(kit, M, ox, oy, rot=0.0):
    kit.box("barn", (9, 7, 5), (ox, oy, 2.5), M["barn"], rot=(0, 0, rot))
    kit.box("barn.roof", (9.8, 7.8, 0.35), (ox, oy, 5.2), M["roof"], bevel=0.05)
    kit.box("barn.door", (3, 0.1, 3.6), (ox, oy - 3.55, 1.8), M["trim"])


def build_house_front(kit, M, ox, oy):
    """A house front at y = oy (its window at x = ox) with a porch roof, and a room behind the window stacked with moving boxes."""
    t = 0.3
    kit.box("hs.wallL", (5.0, t, 4.0), (ox - 3.3, oy, 2.0), M["wall"])
    kit.box("hs.wallR", (5.0, t, 4.0), (ox + 3.3, oy, 2.0), M["wall"])
    kit.box("hs.wallT", (1.6, t, 1.8), (ox, oy, 3.1), M["wall"])
    kit.box("hs.wallB", (1.6, t, 0.9), (ox, oy, 0.45), M["wall"])
    for sx in (-0.85, 0.85):
        kit.box("hs.frame", (0.1, 0.4, 1.4), (ox + sx, oy - 0.05, 1.6), M["trim"])
    for sz in (0.85, 2.35):
        kit.box("hs.frame", (1.8, 0.4, 0.1), (ox, oy - 0.05, sz), M["trim"])
    kit.box("hs.back", (8, 0.1, 4.0), (ox, oy + 4.0, 2.0), M["interior"])
    kit.box("hs.floor", (8, 4.2, 0.1), (ox, oy + 2.0, 0.05), M["floor"])
    kit.box("hs.side", (0.1, 4.0, 4.0), (ox - 3.9, oy + 2.0, 2.0), M["interior"])
    kit.box("hs.side", (0.1, 4.0, 4.0), (ox + 3.9, oy + 2.0, 2.0), M["interior"])
    kit.box("hs.ceil", (8, 4.2, 0.1), (ox, oy + 2.0, 4.0), M["interior"])
    for i, (x, y, z, s) in enumerate(((-0.5, 1.4, 0.7, 1.1), (0.7, 1.5, 0.65, 1.0), (-0.4, 1.4, 1.75, 0.9), (0.9, 2.2, 0.6, 0.9), (0.1, 2.6, 0.6, 1.1))):
        kit.box(f"hs.crate{i}", (s, s, s), (ox + x, oy + y, z), M["box" if i % 2 == 0 else "box2"], rot=(0, 0, 0.12 * i), bevel=0.02)
    kit.light("hs.light", "POINT", (ox, oy + 2.0, 3.4), 220, "#ffd7a0", size=0.4)
    # the porch roof, sloping out from the front, on two posts
    kit.box("hs.porch", (7.4, 2.6, 0.18), (ox, oy - 1.45, 3.45), M["roof"], rot=(0.12, 0, 0))
    for sx in (-3.4, 3.4):
        kit.box("hs.postp", (0.2, 0.2, 3.5), (ox + sx, oy - 2.6, 1.75), M["trim"])
    kit.box("hs.roofmain", (9.0, 5.0, 0.3), (ox, oy + 2.0, 4.3), M["roof"])


def build_mower(kit, M):
    root = kit.empty("mower", (0, 0, 0))
    kit.box("mw.deck", (0.62, 0.8, 0.22), (0, 0, 0.26), M["mower"], parent=root, bevel=0.04)
    kit.box("mw.top", (0.34, 0.4, 0.16), (0, 0.1, 0.45), M["dark"], parent=root, bevel=0.03)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl("mw.wheel", 0.12, 0.08, (sx * 0.35, sy * 0.28, 0.12), M["dark"], parent=root, n=10, rot=(0, math.pi / 2, 0))
    # a handle from the back of the deck up to where her hands are
    kit.box("mw.handle", (0.04, 0.05, 0.9), (0, 0.55, 0.7), M["steel"], parent=root, rot=(-0.55, 0, 0))
    kit.box("mw.bar", (0.55, 0.04, 0.04), (0, 0.78, 0.98), M["steel"], parent=root)
    return root


def build_quilt(kit, M, name, ox, oy, sz=1.0):
    pats = ("quilt1", "quilt2", "quilt3", "quilt4")
    objs = []
    for a in range(3):
        for b in range(3):
            objs.append(kit.box(f"{name}.p", (0.5 * sz, 0.5 * sz, 0.04), (ox + (a - 1) * 0.5 * sz, oy + (b - 1) * 0.5 * sz, 0.02),
                                M[pats[(a + b) % 4]]))
    return objs


def build_cups(kit, M, ox, oy):
    objs = []
    for k, dx in enumerate((-0.28, 0.28)):
        objs.append(kit.cyl("cup", 0.065, 0.11, (ox + dx, oy - 0.75, 0.095), M["cup"], n=14))
        objs.append(kit.cyl("cup.top", 0.052, 0.01, (ox + dx, oy - 0.75, 0.152), M["cocoa"], n=14))
    objs.append(kit.cyl("thermos.g", 0.06, 0.3, (ox + 0.6, oy - 0.5, 0.19), M["thermos"], n=14))
    return objs


def hay_shoot(kit, M, name, x, y, sc=1.0):
    kit.box(f"{name}", (0.03, 0.03, 0.32 * sc), (x, y, 0.16 * sc), M["shoot"], rot=(0.1, 0, 0.3))
    kit.box(f"{name}.l", (0.2 * sc, 0.03, 0.02), (x + 0.07, y, 0.26 * sc), M["shoot"], rot=(0, 0.4, 0.2))
    kit.box(f"{name}.r", (0.2 * sc, 0.03, 0.02), (x - 0.07, y, 0.2 * sc), M["shoot"], rot=(0, -0.4, -0.2))


def trees(kit, ox, oy, n=9, ring=(55, 85)):
    for k in range(n):
        a = k * 2 * math.pi / n + 0.4 * math.sin(k * 7.1)
        r = ring[0] + (ring[1] - ring[0]) * (0.5 + 0.5 * math.sin(k * 3.3))
        kit.prop("commontree_1", (ox + r * math.cos(a), oy + r * math.sin(a), 0), rot=40 * k, height=6.0 + 2.5 * (k % 3) / 2, tint="#5a9a4a")


# ------------------------------------------------------------------------------------------------ the set
def build_farmland(kit, M, ox, oy):
    """What surrounds the field when it's seen from the sky: crop rows, hedges, a dirt yard, a farmhouse, a barn and a silo."""
    z = -0.012
    for q in range(30):       # the field to the west: rows running north to south
        kit.box("rowW", (1.7, 150.0, 0.004), (ox - 21.5 - q * 1.8, oy, z), M["row1" if q % 2 == 0 else "row2"])
    for q in range(26):       # the field to the east: rows running west to east, a different crop
        kit.box("rowE", (60.0, 1.7, 0.004), (ox + 51.0, oy - 46 + q * 3.6, z), M["row2" if q % 2 == 0 else "row1"])
        kit.box("rowE2", (60.0, 1.7, 0.004), (ox + 51.0, oy - 44.2 + q * 3.6, z), M["row1" if q % 2 == 0 else "row2"])
    kit.box("stubbleN", (44.0, 40.0, 0.004), (ox, oy + 52.5, z), M["stubble"])
    for sx in (-1, 1):
        kit.box("hedge", (1.2, 150.0, 0.8), (ox + sx * 20.9, oy, 0.4), M["hedge"], bevel=0.1)
    kit.box("hedgeN", (42.0, 1.2, 0.8), (ox, oy + 32.9, 0.4), M["hedge"], bevel=0.1)
    kit.box("yard", (44.0, 26.0, 0.004), (ox, oy - 45.0, z), M["dirt"])
    kit.box("lane", (44.0, 3.0, 0.004), (ox, oy - 34.5, -0.005), M["dirt"])


def build_farm(kit, M, ox, oy):
    """The farmhouse (a flat porch roof facing the field, where June stands at dawn), the barn and a silo, south of the field."""
    hx, hy = ox, oy - 46.0
    kit.box("farm.house", (12.0, 7.0, 4.0), (hx, hy, 2.0), M["wall"])
    kit.box("farm.roof", (12.8, 7.8, 0.3), (hx, hy, 4.15), M["roof"], bevel=0.05)
    kit.box("farm.door", (1.2, 0.1, 2.2), (hx, hy + 3.55, 1.1), M["wood"])
    kit.box("farm.win1", (1.6, 0.1, 1.3), (hx - 3.6, hy + 3.55, 1.9), M["glow"])
    kit.box("farm.win2", (1.6, 0.1, 1.3), (hx + 3.6, hy + 3.55, 1.9), M["glow"])
    kit.box("farm.porch", (10.4, 3.4, 0.22), (hx, hy + 5.2, 3.29), M["roof"], bevel=0.03)       # flat porch roof, top at z 3.4
    for sx in (-4.9, 4.9):
        for sy in (3.7, 6.7):
            kit.box("farm.post", (0.22, 0.22, 3.2), (hx + sx, hy + sy, 1.6), M["trim"])
    kit.box("farm.rail", (10.2, 0.08, 0.5), (hx, hy + 6.85, 3.7), M["trim"])
    kit.box("farm.barn", (9.0, 7.0, 5.0), (ox - 19.0, oy - 47.0, 2.5), M["barn"])
    kit.box("farm.barnroof", (9.8, 7.8, 0.35), (ox - 19.0, oy - 47.0, 5.2), M["roof"], bevel=0.05)
    kit.cyl("farm.silo", 2.4, 9.0, (ox - 27.0, oy - 44.0, 4.5), M["silo"], n=20)
    kit.cyl("farm.silocap", 2.5, 0.5, (ox - 27.0, oy - 44.0, 9.2), M["roof"], n=20)


def build_sky(kit, M):
    """A big moon and a few stars, parented to the camera so they sit in the sky whichever way it faces (the ground hides them
    when it looks down). Shown only by the night looks."""
    cam = kit.OBJ["cam"]
    D = 250.0
    moon = kit.sphere("moon.disc", 26.0, (34.0, 100.0, -D), M["moon"], parent=cam, seg=24)
    halo = kit.sphere("moon.halo", 40.0, (34.0, 100.0, -D - 30.0), M["moonhalo"], parent=cam, seg=20)
    import random
    rnd = random.Random(95)
    stars = []
    for q in range(46):
        x, y = rnd.uniform(-150, 150), rnd.uniform(40, 215)
        if (x - 34) ** 2 + (y - 100) ** 2 < 70 ** 2:
            continue
        stars.append(kit.sphere("star", rnd.uniform(0.8, 1.5), (x, y, -D - 20.0), M["star"], parent=cam, seg=6))
    return [moon, halo] + stars


def build(kit, story, tl):
    ctx = {"story": story, "kit": kit, "lanterns": {}, "built": {}, "bands": {}, "tog": {}}
    M = materials(kit)
    ctx["M"] = M
    for scene in sorted({tuple(v) for v in G.ORG.values()}):
        kit.plane(f"ground{scene}", (300, 300), (scene[0], scene[1], -0.03), M["grass"])
        if scene == (0, 0):
            continue                                  # the overhead scene: no trees, a farm instead (below)
        trees(kit, scene[0], scene[1], ring=(75, 105) if scene == (1600, 0) else (55, 85))
    # one straw floor per scene (the paths show it between the corn)
    done = set()
    for name in story.get("layouts", []):
        o = tuple(G.ORG[name])
        w, h = G.SIZE.get(name, (G.FW, G.FH))
        if (o, w, h) in done:
            continue
        done.add((o, w, h))
        kit.plane(f"straw{o}", (w + 0.0, h + 0.0), (o[0], o[1], 0.0), M["straw"])
    for o in ((0, 0), (1600, 0)):
        build_farmland(kit, M, *o)
        build_farm(kit, M, *o)
    # --- the lanterns: day maze (0..11) and the entrance (16)
    for k, (x, y) in enumerate(G.LANT_DAY):
        ox, oy = G.ORG["day"]
        build_lantern(kit, ctx, M, k, ox + x, oy + y, tally=(k == 0))
    ox, oy = G.ORG["entrance"]
    build_lantern(kit, ctx, M, 16, ox + G.LANT_ENT[0], oy + G.LANT_ENT[1], energy=200.0, zb=1.6)
    # --- the day maze props
    d = G.ORG["day"]
    build_scarecrow(kit, M, d[0] + G.SCARE[0], d[1] + G.SCARE[1])
    build_pumpkin(kit, M, d[0] + G.PUMPKIN[0], d[1] + G.PUMPKIN[1])
    build_bales(kit, M, d[0] + G.BALE[0], d[1] + G.BALE[1])
    build_board(kit, M, d[0] - 2.4, d[1] - 29.0)
    ctx["tog"]["phone_a"] = [build_phone(kit, M, "phone_a", (d[0] - 17.0, d[1] + 21.0, 0.012))]
    ctx["tog"]["phone_b"] = [build_phone(kit, M, "phone_b", (d[0] + G.BALE[0], d[1] + G.BALE[1] + 0.2, 1.02))]
    # --- the summer yard: house front, barn, mower
    s = G.ORG["summer"]
    build_house_front(kit, M, s[0] + 6.0, s[1] - 40.0)
    build_barn(kit, M, s[0] - 13.0, s[1] - 41.0)
    ctx["mower"] = build_mower(kit, M)
    # --- the clearing: quilt, cups, thermos (S30 on), and the held quilt, thermos and flashlight June carries
    c = G.ORG["day"]
    ctx["tog"]["ground_set"] = build_quilt(kit, M, "quilt", c[0] + G.QUILT[0], c[1] + G.QUILT[1], 1.4) \
        + build_cups(kit, M, c[0] + G.QUILT[0], c[1] + G.QUILT[1])
    ctx["steam"] = []
    for q in range(8):
        sp = kit.sphere("steam", 0.03, (c[0] + G.QUILT[0] + (-0.28 if q % 2 == 0 else 0.28), c[1] + G.QUILT[1] - 0.75, 0.2), M["steam"], seg=6)
        ctx["steam"].append(sp)
    ctx["tog"]["steam"] = ctx["steam"]
    q = kit.box("held.quilt", (0.7, 0.46, 0.2), (0, 0, 0), M["quilt1"], bevel=0.03)
    q2 = kit.box("held.quilt2", (0.72, 0.1, 0.2), (0, 0, 0), M["quilt2"])
    th = kit.cyl("held.thermos", 0.065, 0.3, (0, 0, 0), M["thermos"], n=14)
    ctx["tog"]["held_q"] = [q, q2]
    ctx["tog"]["held_th"] = [th]
    ctx["tog"]["cup_s"] = [kit.cyl("cup_s", 0.065, 0.11, (s[0] + 1.6, s[1] - 4.9, 0.055), M["cup"], n=14),
                           kit.cyl("cup_s.top", 0.052, 0.01, (s[0] + 1.6, s[1] - 4.9, 0.115), M["cocoa"], n=14)]
    ctx["held"] = {"q": q, "q2": q2, "th": th}
    fb = kit.cyl("flash.body", 0.04, 0.22, (0, 0, 0), M["flash_body"], n=10, rot=(math.pi / 2, 0, 0))
    fl = kit.cyl("flash.lens", 0.055, 0.04, (0, 0, 0), M["lens"], n=10, rot=(math.pi / 2, 0, 0))
    ctx["flash"] = (fb, fl)
    ctx["tog"]["flash"] = [fb, fl]
    kit.light("flash.spot", "SPOT", (0, 0, 0), 160, "#ffd9a0", size=0.05, spot=55, blend=0.6)
    # --- the overhead dot: the quilt in the eye (S33, S34), and June's light walking a shape (S42 to S44)
    ex, ey = G.EYE_L
    eye = []
    for k, (qx, qy, m) in enumerate(((-0.42, -0.3, "quilt1"), (0.42, -0.3, "quilt2"), (-0.42, 0.3, "quilt3"), (0.42, 0.3, "quilt1"))):
        eye.append(kit.box(f"june.quilt{k}", (0.82, 0.58, 0.06), (ex + qx, ey + qy, 0.07), M[m]))
    eye.append(kit.sphere("june.torch", 0.12, (ex + 0.55, ey - 0.35, 0.18), M["torch"], seg=10))
    for rr, mm, zz in ((0.95, "halo2", 0.02), (0.78, "halo", 0.035)):   # a soft glow on the straw that stays inside the centre path
        eye.append(kit.cyl("june.halo", rr, 0.01, (ex, ey, zz), M[mm], n=28))
    kit.light("june.light", "POINT", (ex + 0.4, ey - 0.3, 1.8), 520, "#ffb347", size=0.5)
    kit.light("june.cone", "SPOT", (ex + 0.55, ey - 0.35, 0.3), 150, "#ffcf8a", rot=(math.radians(100), 0, math.radians(35)), size=0.1, spot=60, blend=0.6)
    ctx["tog"]["eye"] = eye
    dot = [kit.sphere("dot.bead", 0.55, (0, 0, 0.7), M["torch"], seg=10), kit.cyl("dot.halo", 1.5, 0.01, (0, 0, 0.04), M["halo2"], n=24),
           kit.cyl("dot.halo2", 1.0, 0.01, (0, 0, 0.05), M["halo"], n=24)]
    ctx["dot"] = dot
    ctx["tog"]["dot"] = dot
    kit.light("dot.light", "POINT", (0, 0, 2.5), 900, "#ffb347", size=0.6)
    # --- the sky lights, and a camera fill so a face always reads
    kit.light("gold", "SUN", (0, 0, 60), 3.0, "#ffb870", rot=(math.radians(72), 0, math.radians(30)))
    kit.light("moon", "SUN", (0, 0, 60), 2.7, "#d5e0ff", rot=(math.radians(42), 0, math.radians(-55)))
    kit.light("rim", "SUN", (0, 0, 60), 1.0, "#8fb8ff", rot=(math.radians(76), 0, math.radians(170)))
    for nm in ("moon", "gold", "rim"):
        kit.LIGHTS[nm]["light"].angle = math.radians(14)
    kit.light("camfill", "POINT", (0.15, 0.25, 0.3), 0.0, "#dfe8ff", size=0.4, parent=kit.OBJ["cam"], shadow=False)
    ctx["sky"] = build_sky(kit, M)
    build_marker(kit, M, ctx)
    # the world: the camera sees the sky colour, the scene is lit by a separate ambient colour (so gold corn stays gold)
    nt = bpy.context.scene.world.node_tree
    bg = nt.nodes["Background"]
    out = next(n for n in nt.nodes if n.type == "OUTPUT_WORLD")
    sky = nt.nodes.new("ShaderNodeBackground")
    sky.name = "SkyBG"
    lp = nt.nodes.new("ShaderNodeLightPath")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
    nt.links.new(bg.outputs[0], mx.inputs[1])
    nt.links.new(sky.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return ctx


# ------------------------------------------------------------------------------------------------ looks
def _rgb(c):
    from blocky import kit as K
    return K.col(c)[:3] if isinstance(c, str) else tuple(c)


def mix(a, b, u):
    if isinstance(a, str):
        return tuple(x + (y - x) * u for x, y in zip(_rgb(a), _rgb(b)))
    if isinstance(a, (tuple, list)):
        return tuple(mix(x, y, u) for x, y in zip(a, b))
    return a + (b - a) * u


GOLD = ("#dcae32", "#efc94c", "#e3b63c", "#efd488", "#6bb04c")
NIGHT_COLS = ("#8c7a34", "#a89040", "#9c8438", "#d8c47c", "#2a5448")
# night: a deep navy sky with a big moon (star = how much of it shows), little ambient, silver-blue rims. A lit subject (June's
# flashlight, the lanterns, the camera fill) stands out from corn that is a few stops darker.
LOOKS = {
    "dusk": dict(gold=(4.2, "#ffc27a", 62, 25), moon=(0.0, "#d5e0ff", 40, -35), rim=(0.0, "#8fb8ff", 76, 170), cam=(0.0, "#fff0d8"),
                 sky=("#86cdff", 1.2), amb=("#ffeedd", 0.9), exp=0.25, cols=GOLD, lant=0.1, star=0.0),
    "dusk2": dict(gold=(2.2, "#ffb070", 70, 25), moon=(0.0, "#d5e0ff", 40, -35), rim=(0.0, "#8fb8ff", 76, 170), cam=(0.0, "#fff0d8"),
                  sky=("#d79a78", 1.0), amb=("#e8c8b0", 0.7), exp=0.25, cols=GOLD, lant=0.7, star=0.0),
    "summer": dict(gold=(3.8, "#fff0cf", 40, 20), moon=(0.0, "#d5e0ff", 40, -35), rim=(0.0, "#8fb8ff", 76, 170), cam=(0.0, "#fff0d8"),
                   sky=("#86cdff", 1.2), amb=("#f4f8ee", 1.0), exp=0.25, cols=("#4f9a3a", "#78c455", "#8ed565", "#d6c188", "#5cb347"), lant=0.0, star=0.0),
    "lantern": dict(gold=(0.0, "#ffc27a", 68, 25), moon=(1.5, "#aabcf0", 50, -35), rim=(1.2, "#8fb8ff", 78, 160), cam=(34.0, "#ffe2b8"),
                    sky=("#0a1233", 1.0), amb=("#5668a8", 0.32), exp=0.35, cols=NIGHT_COLS, lant=1.0, star=1.0),
    "moon": dict(gold=(0.0, "#ffc27a", 68, 25), moon=(1.9, "#c4d2ff", 40, -35), rim=(1.6, "#8fb8ff", 76, 170), cam=(55.0, "#d8e4ff"),
                 sky=("#0a1233", 1.0), amb=("#5668a8", 0.32), exp=0.3, cols=NIGHT_COLS, lant=0.0, star=1.0),
    "moonhi": dict(gold=(0.0, "#ffc27a", 68, 25), moon=(3.0, "#dfe8ff", 38, -35), rim=(2.4, "#8fb8ff", 70, 170), cam=(0.0, "#dce6ff"),
                   sky=("#0a1233", 1.0), amb=("#6272b0", 0.5), exp=0.2, cols=("#7a6a2a", "#98802e", "#8c742a", "#e2c46c", "#1e3a52"), lant=0.0, star=0.0),
    "predawn": dict(gold=(0.9, "#ffc4a0", 86, 0), moon=(1.2, "#c0d0f4", 45, -35), rim=(0.8, "#a0c0ff", 76, 170), cam=(40.0, "#e6eeff"),
                    sky=("#6f86b8", 1.0), amb=("#8e9cc4", 0.6), exp=0.3, cols=("#b09a40", "#c8ae4c", "#bda444", "#e6d08a", "#4a7a5a"), lant=0.0, star=0.0),
    "dawn": dict(gold=(4.2, "#ffae62", 78, 0), moon=(0.0, "#d5e0ff", 40, -35), rim=(0.0, "#8fb8ff", 76, 170), cam=(55.0, "#ffe6c0"),
                 sky=("#f7c590", 0.9), amb=("#ffe6cc", 0.9), exp=0.3, cols=GOLD, lant=0.0, star=0.0),
}


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


def cue_t(tl, name, default=None):
    for c in tl.get("cues", []):
        if c["name"] == name:
            return c["t"]
    return default


def lantern_gain(tl, k, t):
    """1 until its cue out<k>, then a 0.45 s fade (0.6 s for the last lantern) to 0; at the next dusk (cue icon_up) each lights
    again in turn over 0.4 s."""
    to = cue_t(tl, f"out{k}")
    if to is None:
        return 1.0
    dur = 0.6 if k == 11 else 0.45
    g = 1.0 - ss((t - to) / dur)
    up = cue_t(tl, "icon_up")
    if up is not None and t >= up + 0.07 * k:
        g = max(g, ss((t - up - 0.07 * k) / 0.4))
    return g


def icon_gain(tl, k, t):
    return lantern_gain(tl, k, t)


def apply_look(kit, ctx, name, b):
    look = LOOKS[name]
    if name in ("lantern", "moon"):   # the moonlight takes over as the last lantern goes out
        look = {key: mix(LOOKS["lantern"][key], LOOKS["moon"][key], b) if key not in ("cols",) else
                tuple(mix(c1, c2, b) for c1, c2 in zip(LOOKS["lantern"]["cols"], LOOKS["moon"]["cols"]))
                for key in LOOKS["moon"]}
        # mix of hex strings returns rgb tuples; of tuples (energy, rgb, tilt, az) is handled by mix recursion
    for nm in ("gold", "moon", "rim"):
        e, c, tilt, az = look[nm]
        L = kit.LIGHTS[nm]
        L["base"] = e
        L["light"].color = _rgb(c)
        L["obj"].rotation_euler = (math.radians(tilt), 0, math.radians(az))
    e, c = look["cam"]
    kit.LIGHTS["camfill"]["base"] = e
    kit.LIGHTS["camfill"]["light"].color = _rgb(c)
    nodes = bpy.context.scene.world.node_tree.nodes
    ac, as_ = look["amb"]
    nodes["Background"].inputs["Color"].default_value = (*_rgb(ac), 1.0)
    nodes["Background"].inputs["Strength"].default_value = as_
    sc_, ss_ = look["sky"]
    nodes["SkyBG"].inputs["Color"].default_value = (*_rgb(sc_), 1.0)
    nodes["SkyBG"].inputs["Strength"].default_value = ss_
    bpy.context.scene.view_settings.exposure = look["exp"]
    M = ctx["M"]
    for key, c in zip(CORN_KEYS, look["cols"]):
        M[key].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*_rgb(c), 1.0)
    on = look.get("star", 0.0) > 0.01
    for ob in ctx["sky"]:
        ob.hide_render = not on
    return look


def attach(ob, tl, who, t, local=(0.0, -0.6), z=1.1, seed=0, yaw_extra=0.0):
    from blocky import acting
    s = acting.state(tl, who, t, seed)
    c, sn = math.cos(s["yaw"]), math.sin(s["yaw"])
    a, b = local
    ob.location = (s["x"] + a * c - b * sn, s["y"] + a * sn + b * c, s["z"] + z + s["bob"] - 0.0)
    ob.rotation_euler = (0, 0, s["yaw"] + yaw_extra)
    return s


def seated(tl, who, t):
    """0..1: how far June has sat down (acting keys with "sit": true / false, eased over 0.5 s)."""
    state, t0, snap = False, None, False
    for k in sorted((k for k in tl["acting"].get(who, []) if "sit" in k), key=lambda k: k["t"]):
        if k["t"] <= t + 1e-9 and bool(k["sit"]) != state:
            state, t0, snap = bool(k["sit"]), k["t"], bool(k.get("snap"))
    if t0 is None:
        return 0.0
    u = 1.0 if snap else ss((t - t0) / 0.5)
    return u if state else 1.0 - u


def animate(kit, story, tl, t, ctx):
    from blocky import rig
    shot = _shot(tl, t)
    sid = shot["id"]
    # layouts: build lazily, show only the one this shot names
    want = story.get("shot_layout", {}).get(sid)
    if want and want not in ctx["built"]:
        trip = make_layout(kit, want, ctx["M"])
        ctx["bands"][want] = trip
        ctx["built"][want] = [ob for o, _ in trip for ob in o]
    for name, obs in ctx["built"].items():
        for ob in obs:
            ob.hide_render = (name != want)
    # props shown only in the shots listed for them
    for pname, shots in story.get("props_by_shot", {}).items():
        for ob in ctx["tog"].get(pname, []):
            ob.hide_render = sid not in shots
    lookname = story.get("shot_look", {}).get(sid, "moon")
    tm = cue_t(tl, "moon", 1e9)
    b = ss((t - tm) / 0.7)
    look = apply_look(kit, ctx, lookname, b if lookname in ("lantern", "moon") else 1.0)
    # rustle: the leaves and tassels shake against the stalks; the ripple (S50b) sweeps the dawn field band by band toward the house
    amp = story.get("shot_rustle", {}).get(sid, 0.0)
    rip = sid in story.get("ripple_shots", [])
    if want:
        for (body, leaves, tops), yc in [(o, yc) for o, yc in ctx["bands"][want]]:
            if rip:
                ta = shot["start"] + 0.05 + (32.0 - yc) / 64.0 * 1.0
                u = (t - ta) / 0.45
                a_ = 0.5 * math.exp(-u * u) * math.sin(2 * math.pi * 2.2 * (t - ta))
                body.location = (0.35 * a_, 0.0, 0.0)
                leaves.location = (0.55 * a_, 0.25 * a_, 0.0)
                tops.location = (0.9 * a_, 0.35 * a_, 0.0)
            elif amp:
                a = 0.05 * amp
                body.location = (0.0, 0.0, 0.0)
                leaves.location = (a * math.sin(2 * math.pi * 2.6 * t + 1.0), a * 0.7 * math.sin(2 * math.pi * 3.4 * t), 0.0)
                tops.location = (a * 1.5 * math.sin(2 * math.pi * 2.9 * t + 0.4), a * math.sin(2 * math.pi * 3.9 * t + 2.0), 0.0)
            else:
                for ob in (body, leaves, tops):
                    ob.location = (0, 0, 0)
    # lanterns
    lm = look["lant"]
    for k in range(12):
        g = lantern_gain(tl, k, t)
        wob = 1.0 + 0.04 * math.sin(2 * math.pi * 1.3 * t + k) + 0.03 * math.sin(2 * math.pi * 2.1 * t + 2 * k)
        set_lantern(ctx, kit, k, g, wob, lm)
    ts = cue_t(tl, "stay", 1e9)
    dip = ss((t - (ts - 0.1)) / 0.3) * (1 - ss((t - (ts + 0.2)) / 0.5))
    set_lantern(ctx, kit, 16, 1.0 - 0.3 * dip, (1.0 - 0.5 * dip) * (1.0 + 0.03 * math.sin(2 * math.pi * 1.7 * t)), 0.6)
    # the marker: each icon fades with its lantern
    dark = kit.col("#1c1a24")
    lit = kit.col("#ff9a2a")
    for k, ic in enumerate(ctx["icons"]):
        g = icon_gain(tl, k, t)
        nd = ic["glass"].node_tree.nodes["Emission"]
        nd.inputs["Color"].default_value = tuple(dark[i] + (lit[i] - dark[i]) * g for i in range(3)) + (1.0,)
        nd.inputs["Strength"].default_value = 0.2 + 1.4 * g
        ic["flame"].scale = (max(0.001, g),) * 3
        ic["flame"].hide_render = g < 0.03
    # June: sitting, and what she carries
    chars = rig.CHARS
    J = chars.get("june")
    seat = seated(tl, "june", t)
    if J is not None and "braid" not in ctx:
        # her long braid: six chunky links down the back from the hair, silver and grey, a red tie at the end, so her back reads
        # as June and never as a blank grey head. Parented to the head (rig units), 1 cm clear of the hair block.
        ctx["braid"] = []
        for q in range(6):
            m = ctx["M"]["braid1" if q % 2 == 0 else "braid2"]
            ctx["braid"].append(kit.box(f"june.braid{q}", (0.36, 0.34, 0.42), (0.0, 0.9, 0.86 - 0.37 * q), m, J.head, bevel=0.07))
        ctx["braid"].append(kit.box("june.tie", (0.4, 0.38, 0.14), (0.0, 0.9, 0.86 - 0.37 * 6 + 0.02), ctx["M"]["tie"], J.head, bevel=0.04))
    if J is not None and seat > 0:
        J.root.location.z -= 0.66 * seat
        J.P["leg-1"].rotation_euler = (1.5 * seat, 0, 0)
        J.P["leg1"].rotation_euler = (1.5 * seat, 0, 0)
    held = ctx["held"]
    s = attach(held["q"], tl, "june", t, (0.0, -0.62), 1.08)
    attach(held["q2"], tl, "june", t, (0.0, -0.62), 1.2)
    attach(held["th"], tl, "june", t, (-0.42, -0.5), 1.0)
    held["th"].rotation_euler = (0, 0, 0)
    fb, fl_ = ctx["flash"]
    attach(fb, tl, "june", t, (0.38, -0.55), 0.95 - 0.66 * seat)
    attach(fl_, tl, "june", t, (0.38, -0.69), 0.95 - 0.66 * seat)
    sp = kit.LIGHTS["flash.spot"]["obj"]
    sp.location = (fl_.location[0], fl_.location[1], fl_.location[2])
    sp.rotation_euler = (math.radians(88), 0, s["yaw"])
    fon = sid in story.get("flash_on", [])
    kit.LIGHTS["flash.spot"]["base"] = 160.0 if fon else 0.0
    # the mower, in front of June in the summer shots
    attach(ctx["mower"], tl, "june", t, (0.0, -0.95), 0.0)
    ctx["mower"].hide_render = sid not in story.get("mower_shots", [])
    for ch in ctx["mower"].children_recursive:
        ch.hide_render = ctx["mower"].hide_render
    # steam over the cups
    for i, sp_ in enumerate(ctx["steam"]):
        ph = ((t * 0.55 + i * 0.37) % 1.0)
        base = G.ORG["day"]
        cx = base[0] + G.QUILT[0] + (-0.28 if i % 2 == 0 else 0.28)
        sp_.location = (cx + 0.025 * math.sin(6 * ph + i), base[1] + G.QUILT[1] - 0.75 + 0.02 * math.cos(5 * ph + i), 0.17 + 0.5 * ph)
        k = (1 - ph) ** 0.6 * (0.6 + 0.8 * ph)
        sp_.scale = (k, k, k)
    # the overhead dot walks a shape (S42 to S44): story "dot_path": {shot: [[t0ref, t1ref, [pts]]]}
    dp = story.get("dot_path", {}).get(sid)
    if dp:
        pts = dp["pts"]
        u = ss((t - shot["start"]) / max(1e-6, shot["end"] - shot["start"]))
        u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
        f = u * (len(pts) - 1)
        i = min(len(pts) - 2, int(f))
        v = f - i
        px = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * v
        py = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * v
        ctx["dot"][0].location = (px, py, 0.7)
        ctx["dot"][1].location = (px, py, 0.04)
        ctx["dot"][2].location = (px, py, 0.05)
        kit.LIGHTS["dot.light"]["obj"].location = (px, py, 2.5)
        kit.LIGHTS["dot.light"]["base"] = 900.0
    else:
        kit.LIGHTS["dot.light"]["base"] = 0.0
    eyeon = sid in story.get("eye_shots", [])
    kit.LIGHTS["june.light"]["base"] = 520.0 if eyeon else 0.0
    kit.LIGHTS["june.cone"]["base"] = 150.0 if eyeon else 0.0
    return {}
