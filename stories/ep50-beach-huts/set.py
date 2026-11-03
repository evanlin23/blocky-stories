"""ep50 "In this town, your reflection does what you really want to do": a row of painted beach huts on an off-season
shore, and four small town rooms far off to the side (office, bakery street, shop, cafe) that are used once each.

Metres. The hut row runs along x at y = 0 (fronts face the sea, -y). Hut i is centred on x = (i - 5) * 4.0 and ours is
hut 5 (faded blue). Dry sand y -1.5 .. -4.8, wet sand (glossy, see-through to a mirrored world) y -4.8 .. -18, then the
sea. The point and the breakwater are at x = +50. Everything faces the narrator's left: the window, the second
deckchair, the point and the boats are all toward +x. A character with yaw 0 faces -y (the sea).

Reflections (the whole marker) are real posed copies, never a render trick, each with its own acting under the name
"r_<who>":
- stage: a tiny shore built behind a hut window (ground that climbs, a sea strip, boats, the point, the bench), the
  copies standing in it, shrinking with depth. Acting pos [x, d]: d 0 (at the glass) .. 1 (the point).
- sand: copies hung upside down under the wet sand, at the real figure's x, y.
- glass: an upright copy standing behind a shop or cafe window (a cool-tinted twin).
- table: copies hung under a glass table top.
Which of them a shot shows is story["shotx"][shot id]["refl"] = {name: kind or {kind, ...}}. Extra acting keys read
here (acting.py ignores them): "sit": true (legs forward), "bow": degrees the torso bends forward.
"""

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

from blocky import acting, rig
from blocky.acting import _held, _switch

DECK_Z = 0.30
CHAIR_A = (-1.2, -1.4)
CHAIR_B = (1.3, -1.5)
LANT = (1.85, -2.4)
BENCH = (46.8, -5.6)
SPACING = 4.0
HW = 1.6                       # half width of a hut
HUT_COLORS = ["#9a9288", "#a9cfb4", "#e09a84", "#b7a6c9", "#e8d48a", "#8fb3c9", "#a9cfb4", "#b7a6c9", "#e09a84",
              "#a9cfb4", "#9a9288", "#b7a6c9"]
OURS = 5
WIN_X = 1.0                    # window centre, hut-local
WIN_W, WIN_Z0, WIN_Z1 = 0.7, 1.1, 1.8
_WX, _WW, _WZ0, _WZ1 = WIN_X, WIN_W, WIN_Z0, WIN_Z1
BIGWIN = (1.05, 1.0, 0.5, 2.3)    # hut 4 (the neighbour's) has a big window for the opening
TOWN = {"office": 200.0, "bakery": 300.0, "shop": 400.0, "cafe": 500.0}

# time of day: sun energy, sun colour, sun elevation (deg), azimuth (deg), sky colour, sky strength, fog colour
TOD = {
    "day":   dict(se=4.2, sc="#fff1dc", el=38, az=-20, sky="#c9d3d6", ss=1.05, fog="#b4c2c8", back="#c4d2d8"),
    "grey":  dict(se=1.0, sc="#dfe8f0", el=30, az=-20, sky="#b4bfc6", ss=0.95, fog="#a6b2ba", back="#a8b6bf"),
    "peach": dict(se=2.4, sc="#ffd2b4", el=11, az=-35, sky="#d9b09c", ss=0.9, fog="#c4a496", back="#e6bfa6"),
    "blue":  dict(se=1.5, sc="#a9bfe6", el=7, az=-35, sky="#4a6a90", ss=0.95, fog="#50688a", back="#6a86a6"),
    "bench": dict(se=2.4, sc="#b7c8ee", el=10, az=-30, sky="#6a88aa", ss=1.5, fog="#5a7494", back="#5a7694"),
    "gold":  dict(se=3.2, sc="#ffbf6e", el=9, az=-40, sky="#f0c397", ss=0.85, fog="#d9b48c", back="#f0cfa6"),
}


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _hex(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def _mix_hex(a, b, u):
    return "#%02x%02x%02x" % tuple(int(round(255 * (x + (y - x) * u))) for x, y in zip(_hex(a), _hex(b)))


def _cues(tl, name):
    return [c for c in tl["cues"] if c["name"] == name]


def _ramp(tl, name, key, t, default):
    """A numeric cue value that eases to each new value over the cue's `dur` (default 0.5 s)."""
    v = default
    for c in sorted(_cues(tl, name), key=lambda c: c["t"]):
        if key not in c:
            continue
        if t < c["t"]:
            break
        u = ss((t - c["t"]) / max(1e-6, c.get("dur", 0.5)))
        v = v + (c[key] - v) * u
    return v


def _last(tl, name, t):
    got = [c for c in _cues(tl, name) if c["t"] <= t + 1e-9]
    return got[-1] if got else None


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


def hx(i):
    return (i - OURS) * SPACING


# ------------------------------------------------------------------------------------------------ materials


def wetsand(kit, name, hexc, alpha):
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Roughness"].default_value = 0.12
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = 0.9
            break
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = alpha
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(b.outputs[0], mix.inputs[2])
    kit._fogged(m, mix.outputs[0])
    return m


def glasstop(kit, name, hexc, alpha):
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Roughness"].default_value = 0.05
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = alpha
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(b.outputs[0], mix.inputs[2])
    kit._fogged(m, mix.outputs[0])
    return m


def stripes_x(kit, name, cols, scale):
    """Wide vertical bands (deckchair canvas) across x in object space, three colours."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.85
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = scale
    nt.links.new(sep.outputs["X"], mul.inputs[0])
    fr = nt.nodes.new("ShaderNodeMath")
    fr.operation = "FRACT"
    nt.links.new(mul.outputs[0], fr.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = kit.col(cols[0])
    ramp.color_ramp.elements[1].position = 0.34
    ramp.color_ramp.elements[1].color = kit.col(cols[1])
    e = ramp.color_ramp.elements.new(0.67)
    e.color = kit.col(cols[2])
    nt.links.new(fr.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m


def screen_mat(kit):
    m = kit._new("laptop screen")
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col("#bcc9d4")
    e.inputs["Strength"].default_value = 1.2
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    return m, e


# ------------------------------------------------------------------------------------------------ build


def B(kit, name, size, loc, mat, rot=(0, 0, 0), bevel=0.0, parent=None):
    return kit.box(name, size, loc, mat, parent, rot, bevel=bevel)


def make_hut(kit, M, i, ctx):
    WIN_X, WIN_W, WIN_Z0, WIN_Z1 = BIGWIN if i == 4 else (_WX, _WW, _WZ0, _WZ1)
    X = hx(i)
    col = HUT_COLORS[i]
    paint = kit.plastic(col, 0.85, name=f"paint {col}")
    trim = M["trim"]
    root = kit.empty(f"hut{i}", (X, 0, 0))
    T = 0.1
    z0, z1 = DECK_Z, 2.5
    zc, zh = (z0 + z1) / 2, z1 - z0

    def wall(nm, x0, x1, za, zb):
        B(kit, f"hut{i}.{nm}", (x1 - x0, T, zb - za), ((x0 + x1) / 2, T / 2, (za + zb) / 2), paint, parent=root)

    wall("l", -HW, -0.5, z0, z1)
    wall("m", 0.5, WIN_X - WIN_W / 2, z0, z1)
    wall("r", WIN_X + WIN_W / 2, HW, z0, z1)
    wall("below", WIN_X - WIN_W / 2, WIN_X + WIN_W / 2, z0, WIN_Z0)
    wall("above", WIN_X - WIN_W / 2, WIN_X + WIN_W / 2, WIN_Z1, z1)
    wall("door_top", -0.5, 0.5, 2.2, z1)
    # gable
    v = [(-HW, 0, z1), (HW, 0, z1), (0, 0, 3.25), (-HW, T, z1), (HW, T, z1), (0, T, 3.25)]
    f = [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)]
    kit.mesh_obj(f"hut{i}.gable", v, [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], paint, root)
    # sides, back, floor
    B(kit, f"hut{i}.sl", (T, 2.0, zh), (-HW + T / 2, 1.0 + T / 2, zc), paint, parent=root)
    B(kit, f"hut{i}.sr", (T, 2.0, zh), (HW - T / 2, 1.0 + T / 2, zc), paint, parent=root)
    B(kit, f"hut{i}.back", (2 * HW, T, zh + 0.7), (0, 2.0 + T / 2, (z0 + 3.25) / 2), paint, parent=root)
    B(kit, f"hut{i}.floor", (2 * HW, 2.1, 0.12), (0, 1.0 + T, DECK_Z - 0.06), M["inwood"], parent=root)
    # roof: two slabs from the ridge (z 3.25) to the eaves (+-1.8, z 2.45)
    ang = math.atan2(3.25 - 2.45, 1.8)
    ln = math.hypot(1.8, 3.25 - 2.45)
    for sx in (-1, 1):
        B(kit, f"hut{i}.roof{sx}", (ln, 2.5, 0.07), (sx * 0.9, 1.0, 2.85 + 0.035), M["roof"], rot=(0, -sx * ang, 0),
          parent=root)
    # window trim and sill
    wx0, wx1 = WIN_X - WIN_W / 2, WIN_X + WIN_W / 2
    for nm, sz, lc in (("t", (WIN_W + 0.12, 0.06, 0.06), (WIN_X, -0.03, WIN_Z1 + 0.03)),
                       ("b", (WIN_W + 0.12, 0.06, 0.06), (WIN_X, -0.03, WIN_Z0 - 0.03)),
                       ("l", (0.06, 0.06, WIN_Z1 - WIN_Z0), (wx0 - 0.03, -0.03, (WIN_Z0 + WIN_Z1) / 2)),
                       ("r", (0.06, 0.06, WIN_Z1 - WIN_Z0), (wx1 + 0.03, -0.03, (WIN_Z0 + WIN_Z1) / 2))):
        B(kit, f"hut{i}.wt{nm}", sz, lc, trim, parent=root)
    B(kit, f"hut{i}.sill", (WIN_W + 0.2, 0.18, 0.05), (WIN_X, -0.06, WIN_Z0 - 0.08), trim, parent=root)
    B(kit, f"hut{i}.dtl", (0.07, 0.06, 1.9), (-0.53, -0.03, 1.25), trim, parent=root)
    B(kit, f"hut{i}.dtr", (0.07, 0.06, 1.9), (0.53, -0.03, 1.25), trim, parent=root)
    B(kit, f"hut{i}.dtt", (1.14, 0.06, 0.08), (0, -0.03, 2.24), trim, parent=root)
    # door on a hinge at x = 0.5
    hinge = kit.empty(f"hut{i}.hinge", (0.5, 0.0, 0), root)
    dcol = _mix_hex(col, "#5a5a5a", 0.25)
    dm = kit.plastic(dcol, 0.8, name=f"door {dcol}")
    B(kit, f"hut{i}.door", (1.0, 0.06, 1.9), (-0.5, 0.05, 1.25), dm, parent=hinge)
    ctx["huts"].append({"root": root, "hinge": hinge, "x": X})
    if i == 4:   # the opening's window: a cool-tinted pane just inside the opening, so it reads as glass
        gl = glasstop(kit, "openpane", "#6aa4d0", 0.16)
        ctx["openpane"] = B(kit, "openpane", (WIN_W, 0.012, WIN_Z1 - WIN_Z0), (WIN_X, 0.045, (WIN_Z0 + WIN_Z1) / 2), gl, parent=root)
        ctx["openpane"].visible_shadow = False
    if i == OURS:
        brass = M["brass"]
        B(kit, "hasp", (0.09, 0.025, 0.3), (-0.93, -0.0, 1.22), brass, parent=hinge)
        B(kit, "hasp.p", (0.05, 0.03, 0.05), (-0.93, -0.012, 1.12), brass, parent=hinge)
        sc = kit.plastic("#5f93b8", 0.6, name="scratch blue")
        for k, dx in enumerate((-0.02, 0.02)):
            B(kit, f"hasp.s{k}", (0.006, 0.004, 0.13), (-0.93 + dx, -0.0145, 1.25), sc, parent=hinge)
        ctx["hasp"] = hinge


def make_deck(kit, M, i):
    X = hx(i)
    B(kit, f"deck{i}", (3.8, 3.0, 0.3), (X, -1.5, DECK_Z / 2), M["deck"])
    for k in range(4):   # posts under the deck edge
        B(kit, f"deck{i}.p{k}", (0.1, 0.1, 0.3), (X + (-1.7 + k * 1.13), -3.0, 0.15), M["roof"])


def deckchair(kit, M, name):
    root = kit.empty(name, (0, 0, 0))
    wood = M["chairwood"]
    can = M["canvas"]
    parts = {}
    for sx in (-1, 1):
        B(kit, f"{name}.fl{sx}", (0.04, 0.04, 0.4), (sx * 0.3, -0.3, 0.2), wood, parent=root)
        parts[f"rail{sx}"] = B(kit, f"{name}.rail{sx}", (0.04, 0.05, 0.95), (sx * 0.3, 0.25, 0.45), wood,
                                rot=(math.radians(-24), 0, 0), parent=root)
        parts[f"arm{sx}"] = B(kit, f"{name}.arm{sx}", (0.05, 0.55, 0.03), (sx * 0.3, -0.02, 0.52), wood, parent=root)
    parts["seat"] = B(kit, f"{name}.seat", (0.56, 0.52, 0.03), (0, -0.04, 0.4), can, rot=(math.radians(-8), 0, 0),
                      parent=root)
    parts["back"] = B(kit, f"{name}.back", (0.56, 0.03, 0.62), (0, 0.28, 0.72), can, rot=(math.radians(-22), 0, 0),
                      parent=root)
    parts["root"] = root
    return parts


def place_chair(kit, ch, pos, yaw, sag=0.0, folded=False, hidden=False):
    root = ch["root"]
    for ob in [root] + list(root.children_recursive):
        ob.hide_render = hidden
    if hidden:
        return
    root.location = pos
    root.rotation_euler = (0, 0, math.radians(yaw))
    if folded:
        root.rotation_euler = (math.radians(-80), 0, math.radians(yaw))   # leaned back against the wall
        root.location = (pos[0], pos[1] - 0.05, pos[2])
        ch["seat"].scale = (1, 1, 1)
        ch["seat"].location = (0, 0.1, 0.5)
        ch["back"].location = (0, 0.12, 0.52)
        return
    ch["seat"].location = (0, -0.04, 0.4 - 0.1 * sag)
    ch["seat"].scale = (1 + 0.55 * sag, 1 + 0.2 * sag, 1)
    ch["seat"].rotation_euler = (math.radians(-8 - 14 * sag), 0, 0)
    ch["back"].location = (0, 0.28 + 0.04 * sag, 0.72 - 0.06 * sag)
    ch["back"].scale = (1 + 0.55 * sag, 1, 1)
    for sx in (-1, 1):
        ch[f"rail{sx}"].location = (sx * (0.3 + 0.16 * sag), 0.25, 0.45)
        ch[f"arm{sx}"].location = (sx * (0.3 + 0.16 * sag), -0.02, 0.52 - 0.04 * sag)


def build_stage(kit, M, ctx):
    """The tiny shore behind a hut window (see the module doc). Local x across, y into the hut, z up."""
    st = kit.empty("stage", (0, 0, 0))
    sand = M["stage_sand"]
    D = 0.8
    # climbing ground: near edge (y 0, z 0) to the far edge (y D, z 0.3)
    kit.mesh_obj("stage.ground", [(-0.6, 0.0, 0.0), (0.6, 0.0, 0.0), (0.6, D, 0.3), (-0.6, D, 0.3)], [(0, 1, 2, 3)],
                 sand, st)
    kit.mesh_obj("stage.sea", [(-0.6, D, 0.3), (0.6, D, 0.3), (0.6, D + 0.15, 0.36), (-0.6, D + 0.15, 0.36)],
                 [(0, 1, 2, 3)], M["stage_sea"], st)
    back = kit.mesh_obj("stage.back", [(-0.7, D + 0.15, 0.0), (0.7, D + 0.15, 0.0), (0.7, D + 0.15, 1.2),
                                       (-0.7, D + 0.15, 1.2)], [(0, 1, 2, 3)], M["stage_back"], st)
    for nm, pts in (("l", [(-0.62, 0, 0), (-0.62, D + 0.15, 0), (-0.62, D + 0.15, 1.2), (-0.62, 0, 1.2)]),
                    ("r", [(0.62, 0, 0), (0.62, D + 0.15, 0), (0.62, D + 0.15, 1.2), (0.62, 0, 1.2)]),
                    ("t", [(-0.62, 0, 0.78), (0.62, 0, 0.78), (0.62, D + 0.15, 0.78), (-0.62, D + 0.15, 0.78)]),
                    ("f", [(-0.62, 0, -0.02), (0.62, 0, -0.02), (0.62, D + 0.15, -0.02), (-0.62, D + 0.15, -0.02)])):
        kit.mesh_obj(f"stage.w{nm}", pts, [(0, 1, 2, 3), (3, 2, 1, 0)], M["stage_dark"], st)
    # props: three boats at d 0.45 (left), the point and the bench at d 0.86 (right)
    def at(d):
        return D * d, 0.3 * d, ctx["sfn"](d)
    for k, x in enumerate((-0.30, -0.19, -0.08)):
        y, z, s = at(0.46)
        ob = kit.sphere(f"stage.boat{k}", 1.0, (x, y, z + 0.012), M["boat"], st)
        ob.scale = (s * 1.7, s * 0.65, s * 0.5)
    y, z, s = at(0.86)
    kit.box("stage.point", (0.5, 0.12, 0.03), (0.2, y - 0.02, z + 0.0), M["stage_sandlit"], st)
    kit.box("stage.break", (0.03, 0.2, 0.03), (0.32, y + 0.08, z + 0.02), M["stone"], st)
    kit.box("stage.bench", (0.03, 0.008, 0.012), (0.12, y - 0.05, z + 0.02), M["chairwood"], st)
    ctx["stage"] = st
    # a small empty deckchair in the glass (L53, L54): its reflection with nobody in it
    sch = deckchair(kit, M, "chairS")
    sch["root"].parent = st
    sch["root"].scale = (0.3, 0.3, 0.3)
    sch["root"].location = (-0.12, 0.12, 0.0)
    ctx["schair"] = sch["root"]


def build(kit, story, tl):
    ctx = {"huts": [], "refl": {}, "init": False}
    sfn = lambda d: 0.15 * (1 - 0.85 * d ** 0.8)
    ctx["sfn"] = sfn
    M = {}
    M["trim"] = kit.plastic("#e8e4d8", 0.7, name="trim")
    M["roof"] = kit.plastic("#9a9288", 0.9, name="roof")
    M["inwood"] = kit.plastic("#b49a74", 0.8, name="inwood")
    M["deck"] = kit.planks("#a39a8a", "#85796a", scale=2.4, axis="X")
    M["chairwood"] = kit.plastic("#a98b62", 0.7, name="chairwood")
    M["canvas"] = stripes_x(kit, "canvas", ["#a97d74", "#e8dfc8", "#6f9e9a"], 2.4)
    M["brass"] = kit.metal("#b5964f", 0.35)
    M["boat"] = kit.plastic("#4f74a0", 0.55, name="boat")
    M["stone"] = kit.concrete("#7b7d78", 1.2, 0.35)
    M["sand"] = kit.grime("#d9cba8", 0.82, 3.0, rough=0.95)
    M["stage_sand"] = kit.plastic("#7a8a96", 0.35, name="stage sand")
    M["stage_sandlit"] = kit.plastic("#8d9ca6", 0.4, name="stage sandlit")
    M["stage_sea"] = kit.plastic("#4a6c70", 0.3, name="stage sea")
    M["stage_dark"] = kit.plastic("#20262c", 0.9, name="stage dark")
    bm = kit._new("stage back")
    nt = bm.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col("#aebcc4")
    e.inputs["Strength"].default_value = 0.9
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    M["stage_back"] = bm
    ctx["backnode"] = e

    # --- ground
    kit.plane("sand", (400, 6.6), (0, -4.2, 0.0), M["sand"])
    kit.plane("sandback", (400, 10), (0, 5.0, 0.0), M["sand"])
    kit.plane("sandx", (60, 5.2), (62, 0.1, 0.0), M["sand"])
    wet = wetsand(kit, "wet sand", "#8f8572", 0.58)
    wp = kit.plane("wet", (400, 13.2), (0, -11.4, 0.0), wet)
    wp.visible_shadow = False
    kit.plane("under", (400, 14), (0, -11.4, -2.4), kit.plastic("#8a98a4", 0.9, name="under"))
    kit.plane("sea", (800, 400), (0, -218, -0.06), kit.plastic("#5f7a78", 0.25, name="sea"))
    kit.plane("foam", (400, 0.7), (0, -18.4, -0.04), kit.plastic("#e6ece8", 0.9, name="foam"))

    for i in range(12):
        make_hut(kit, M, i, ctx)
        make_deck(kit, M, i)
    # our hut: the step (a threshold board), interior props
    B(kit, "step", (1.2, 0.8, 0.06), (0, -0.4, DECK_Z + 0.03), M["inwood"])
    # chairs
    ctx["chairA"] = deckchair(kit, M, "chairA")
    ctx["chairB"] = deckchair(kit, M, "chairB")
    # the folded one against the wall is chairB too (place_chair folded)
    # scarf and phone on Remi's chair
    scarf = kit.plastic("#d9a441", 0.9, name="scarfprop")
    sc = kit.empty("scarfprop", (0, 0, 0))
    B(kit, "scarf.a", (0.46, 0.34, 0.035), (0, 0, 0), scarf, parent=sc, bevel=0.012)
    B(kit, "scarf.b", (0.1, 0.34, 0.03), (0.17, -0.3, -0.12), scarf, rot=(0.2, 0, 0), parent=sc, bevel=0.01)
    for k in range(5):
        B(kit, f"scarf.f{k}", (0.012, 0.06, 0.012), (-0.2 + k * 0.1, -0.2, 0.0), scarf, parent=sc)
    B(kit, "phone", (0.08, 0.15, 0.012), (-0.08, 0.02, 0.03), kit.plastic("#16181c", 0.3, name="phone"), parent=sc,
      bevel=0.005)
    ctx["scarfprop"] = sc
    # paint pot, sanding block, the little props
    pp = kit.cyl("paintpot", 0.11, 0.2, (-1.7, -0.9, DECK_Z + 0.1), kit.plastic("#cfd6dc", 0.4, name="pot"), n=16)
    kit.cyl("paintpot.p", 0.095, 0.01, (-1.7, -0.9, DECK_Z + 0.205), kit.plastic("#3f6fa6", 0.35, name="paintblue"), n=16)
    B(kit, "block", (0.12, 0.07, 0.04), (-1.3, -0.6, DECK_Z + 0.02), kit.plastic("#c9a46a", 0.9, name="block"))
    # lantern
    lant = kit.empty("lantern", (LANT[0], LANT[1], DECK_Z))
    B(kit, "lant.base", (0.2, 0.2, 0.04), (0, 0, 0.02), kit.plastic("#2c2a28", 0.5, name="lantbase"), parent=lant)
    kit.cyl("lant.glass", 0.085, 0.22, (0, 0, 0.15), kit.emit("#f6c27a", 1.1, name="lantglow"), lant, n=14)
    kit.cyl("lant.top", 0.1, 0.03, (0, 0, 0.275), kit.plastic("#2c2a28", 0.5, name="lantbase"), lant, n=14)
    ctx["lantern"] = lant
    # the puddle on the deck boards (L08): sky, a gull, the eave
    pud = kit.empty("puddle", (-1.0, -1.1, DECK_Z + 0.004))
    ctx["puddle"] = pud
    kit.plane("pud.sky", (0.9, 0.55), (0, 0, 0), kit.emit("#cfd9de", 0.9, name="pudsky"), pud)
    kit.plane("pud.eave", (0.9, 0.12), (0, 0.2, 0.002), kit.emit("#5d5a56", 0.5, name="pudeave"), pud)
    for sx in (-1, 1):
        B(kit, f"pud.gull{sx}", (0.1, 0.012, 0.012), (sx * 0.045, -0.05, 0.004), kit.emit("#ffffff", 1.0, name="gull"),
          rot=(0, 0, sx * 0.4), parent=pud)
    # laptop
    lap = kit.empty("laptop", (0, 0, 0))
    gm = kit.plastic("#34383e", 0.4, name="lapbody")
    B(kit, "lap.base", (0.34, 0.24, 0.02), (0, 0, 0.01), gm, parent=lap, bevel=0.006)
    hinge = kit.empty("lap.hinge", (0, -0.12, 0.02), lap)
    B(kit, "lap.lid", (0.34, 0.01, 0.23), (0, 0, 0.115), gm, parent=hinge, bevel=0.004)
    smat, snode = screen_mat(kit)
    kit.plane("lap.screen", (0.31, 0.2), (0, 0.0062, 0.115), smat, hinge, rot=(math.radians(90), 0, 0))
    ctx["laptop"], ctx["lap_hinge"], ctx["lap_screen"] = lap, hinge, snode
    # kettle, stove, cups, shelf (inside our hut, left wall)
    ox = -HW + 0.35
    B(kit, "counter", (0.6, 1.4, 0.8), (ox, 1.1, DECK_Z + 0.4), M["inwood"])
    B(kit, "stove", (0.34, 0.34, 0.08), (ox, 0.85, DECK_Z + 0.84), kit.plastic("#2e3236", 0.4, name="stove"))
    kit.cyl("kettle", 0.1, 0.17, (ox, 0.85, DECK_Z + 0.97), kit.metal("#9aa2a8", 0.3), n=16)
    for k, y in enumerate((1.35, 1.6)):
        kit.cyl(f"cup{k}", 0.045, 0.08, (ox, y, DECK_Z + 0.84), kit.plastic("#e8e4d8", 0.5, name="cup"), n=12)
    B(kit, "shelf", (0.3, 1.2, 0.04), (-HW + 0.2, 1.1, 1.75), M["inwood"])
    kit.cyl("shelfpot", 0.1, 0.18, (-HW + 0.2, 1.7, 1.86), kit.plastic("#cfd6dc", 0.4, name="pot"), n=14)
    ctx["steam"] = [kit.sphere(f"steam{k}", 0.03 + 0.012 * k, (ox, 0.85, DECK_Z + 1.1 + 0.07 * k),
                               kit.emit("#e8eef0", 0.6, name="steam"), None, 8) for k in range(4)]
    # the breakwater, bench, boats, point
    B(kit, "break", (1.8, 38, 0.7), (50, -28, 0.3), M["stone"])
    B(kit, "bench.seat", (1.6, 0.45, 0.06), (BENCH[0], BENCH[1], 0.45), M["chairwood"])
    B(kit, "bench.back", (1.6, 0.05, 0.45), (BENCH[0], BENCH[1] + 0.22, 0.72), M["chairwood"])
    for sx in (-0.7, 0.7):
        B(kit, f"bench.l{sx}", (0.07, 0.4, 0.45), (BENCH[0] + sx, BENCH[1], 0.22), M["chairwood"])
    for k, bx in enumerate((24.0, 27.5, 31.0)):
        ob = kit.sphere(f"boat{k}", 1.0, (bx, -5.5 - 0.4 * k, 0.25), M["boat"])
        ob.scale = (1.7, 0.7, 0.55)
        kit.box(f"boat{k}.keel", (3.2, 0.1, 0.1), (bx, -5.5 - 0.4 * k, 0.04), M["chairwood"])
    build_stage(kit, M, ctx)
    build_towns(kit, M, ctx)

    # --- CC0 props (2026-11-03 quality pass): dune grass in the hut gaps, rocks and driftwood on the dry sand
    for i in range(11):
        gx = (i - 5) * 4.0 + 2.0
        kit.prop("grass_short" if i % 2 else "grass", (gx, -0.25, 0), rot=37 * i, height=0.45 + 0.08 * (i % 3), tint="#cfd6a6")
        kit.prop("flowers", (gx + 0.5, -0.45, 0), rot=19 * i, height=0.38, tint="#f0e6d8") if i % 3 == 0 else None
    for k, (rx, ry, rr, rh, nm) in enumerate([(-7.5, -4.4, 20, 0.5, "rock_1"), (-11.5, -3.6, 80, 0.7, "rock_3"),
                                              (6.5, -4.6, 140, 0.45, "rock_moss_1"), (11.0, -3.4, 10, 0.6, "rock_5"),
                                              (19.5, -4.3, 60, 0.5, "rock_1"), (34.0, -3.8, 100, 0.8, "rock_3"),
                                              (44.0, -4.2, 30, 0.6, "rock_moss_1"), (-17.0, -4.0, 70, 0.55, "rock_5")]):
        kit.prop(nm, (rx, ry, 0), rot=rr, height=rh, tint="#b8b4a8")
    kit.prop("nat_stump_old", (8.5, -2.8, 0), rot=30, height=0.4, tint="#c9b9a0")
    kit.prop("nat_log_stack", (-5.9, -0.9, 0), rot=90, height=0.8, tint="#c9b08c")
    kit.prop("nat_pot_large", (7.9, -1.2, DECK_Z), fit=0.6, tint="#e8c8a8")
    kit.prop("woodlog", (47.8, -4.6, 0), rot=95, fit=1.8, tint="#cdbba0")
    kit.prop("rock_moss_1", (49.2, -6.6, 0), rot=15, height=0.5, tint="#b8b4a8")

    # --- lights
    sun = kit.light("sun", "SUN", (0, -20, 30), 4.0, "#fff1dc", size=0.01)
    ctx["sun"] = sun
    kit.light("lantern", "POINT", (LANT[0], LANT[1], DECK_Z + 0.16), 150, "#f0b46a", size=0.08)
    kit.light("laptop", "POINT", (0.0, -1.05, 1.0), 12, "#cfe0ff", size=0.1)
    kit.light("hutin", "POINT", (-0.4, 1.0, 2.1), 220, "#ffcf94", size=0.15)
    kit.light("headkey", "POINT", (2.3, -2.2, 1.0), 160, "#ffc27a", size=0.3)
    kit.light("dusklift", "AREA", (-2.8, -6.5, 2.8), 110, "#9db8ea", size=4.0)
    kit.aim(LIGHT("dusklift", kit), (1.0, -1.3, 1.5))
    kit.light("benchlift", "AREA", (42.0, -13.0, 3.0), 900, "#c3d3f2", size=6.0)
    kit.aim(LIGHT("benchlift", kit), (46.8, -6.4, 0.3))
    kit.light("stagelit", "POINT", (hx(OURS) + WIN_X, 0.4, WIN_Z0 + 0.4), 10, "#d8e4f4", size=0.04)   # inside the glass box
    kit.light("faceup", "POINT", (0.2, -1.3, 0.9), 160, "#ffb878", size=0.25)   # the Small Head, lit from below
    kit.light("shadowkey", "POINT", (3.3, -4.0, 1.5), 1400, "#f4b66e", size=0.04)
    kit.light("rim", "AREA", (3.0, -12.0, 1.4), 400, "#7aa2e0", size=5.0)
    kit.aim(LIGHT("rim", kit), (0.6, -0.9, 1.1))
    # 'rim' is a cool light from the sea side, low; only the night scenes switch it on
    return ctx


def LIGHT(name, kit):
    return kit.LIGHTS[name]["obj"]


# ---------------------------------------------------------------------------------------------- town rooms


def build_towns(kit, M, ctx):
    wallm = kit.plastic("#cfc9bd", 0.9, name="townwall")
    floorm = kit.plastic("#8d8678", 0.8, name="townfloor")
    ceil = kit.plastic("#e4e0d6", 0.9, name="townceil")

    def room(nm, ox, w, d, h, wm=wallm, fm=floorm, oy=0.0, back=True):
        B(kit, f"{nm}.floor", (w, d, 0.1), (ox, oy, -0.05), fm)
        B(kit, f"{nm}.ceil", (w, d, 0.1), (ox, oy, h + 0.05), ceil)
        if back:
            B(kit, f"{nm}.wb", (w, 0.1, h), (ox, oy + d / 2, h / 2), wm)
        B(kit, f"{nm}.wf", (w, 0.1, h), (ox, oy - d / 2, h / 2), wm)
        B(kit, f"{nm}.wl", (0.1, d, h), (ox - w / 2, oy, h / 2), wm)
        B(kit, f"{nm}.wr", (0.1, d, h), (ox + w / 2, oy, h / 2), wm)

    # OFFICE: a glass-topped table, three people stand behind it
    ox = TOWN["office"]
    room("office", ox, 8, 8, 2.8, kit.plastic("#aeb9c0", 0.9, name="officewall"), kit.plastic("#58606a", 0.8, name="officefl"),
         oy=40.0)
    gl = glasstop(kit, "tableglass", "#9fb8c6", 0.45)
    ctx["tableglass"] = B(kit, "table.top", (3.0, 1.2, 0.04), (ox, 40.0, 0.76), gl)
    ctx["tableglass"].visible_shadow = False
    for sx in (-1.3, 1.3):
        for sy in (-0.45, 0.45):
            B(kit, f"table.leg{sx}{sy}", (0.06, 0.06, 0.74), (ox + sx, 40.0 + sy, 0.37), kit.plastic("#2c3036", 0.4, name="tleg"))
    kit.light("office.u", "POINT", (ox, 40.0, 0.35), 90, "#dfe8f0", size=0.4)
    B(kit, "office.win", (4.0, 0.04, 1.2), (ox, 43.9, 1.5), kit.emit("#dfe8ee", 0.7, name="officewin"))
    kit.light("office.l", "POINT", (ox, 38.8, 2.5), 380, "#fff4e6", size=0.6)
    kit.light("office.f", "POINT", (ox, 42.0, 2.5), 220, "#fff4e6", size=0.6)
    # BAKERY street
    bx = TOWN["bakery"]
    kit.plane("bak.street", (14, 14), (bx, 40.0, 0.0), kit.plastic("#8e8a84", 0.9, name="street"))
    wm = kit.plastic("#b86f5a", 0.85, name="bakwall")
    B(kit, "bak.wl", (4.0, 0.3, 3.3), (bx - 3.5, 41.5, 1.65), wm)
    B(kit, "bak.wr", (4.0, 0.3, 3.3), (bx + 3.5, 41.5, 1.65), wm)
    B(kit, "bak.wt", (3.0, 0.3, 0.9), (bx, 41.5, 2.85), wm)
    B(kit, "bak.wb", (3.0, 0.3, 0.7), (bx, 41.5, 0.35), wm)
    B(kit, "bak.roof", (12, 5, 0.2), (bx, 43.5, 3.4), wm)
    B(kit, "bak.back", (12, 0.2, 3.4), (bx, 46.0, 1.7), wm)
    B(kit, "bak.floor", (12, 5, 0.1), (bx, 43.5, -0.05), kit.plastic("#8c7a66", 0.8, name="bakfl"))
    B(kit, "bak.side", (0.2, 5, 3.4), (bx - 6, 43.5, 1.7), wm)
    B(kit, "bak.sider", (0.2, 5, 3.4), (bx + 6, 43.5, 1.7), wm)
    B(kit, "bak.counter", (2.8, 0.9, 0.9), (bx, 45.2, 0.45), kit.plastic("#d9c8a4", 0.8, name="bakcounter"))
    cake = kit.cyl("bak.cake", 0.55, 0.42, (bx + 0.2, 43.0, 1.0), kit.plastic("#f0e6d0", 0.6, name="cake"), n=24)
    kit.cyl("bak.cake2", 0.36, 0.3, (bx + 0.2, 43.0, 1.34), kit.plastic("#f6efe0", 0.6, name="cake2"), n=24)
    kit.cyl("bak.cakecherry", 0.06, 0.07, (bx + 0.2, 43.0, 1.53), kit.plastic("#b8453d", 0.4, name="cherry"), n=10)
    B(kit, "bak.stand", (1.5, 1.1, 0.9), (bx + 0.2, 43.0, 0.45), kit.plastic("#d9c8a4", 0.8, name="bakcounter"))
    for k, x in enumerate((-1.3, -0.9, 1.5, 1.95)):   # drawn loaves, cups: bread shapes only
        ob = kit.sphere(f"bak.loaf{k}", 0.2, (bx + x, 44.1, 1.05), kit.plastic("#c98f4e", 0.7, name="loaf"))
        ob.scale = (1.4, 0.8, 0.8)
    B(kit, "bak.shelf", (3.2, 0.5, 0.05), (bx, 45.6, 1.0), kit.plastic("#d9c8a4", 0.8, name="bakcounter"))
    kit.light("bak.l", "POINT", (bx, 43.8, 2.9), 600, "#ffe2b8", size=0.7)
    # SHOP: a changing-room cubicle and the shop window
    sx0 = TOWN["shop"]
    room("shop", sx0, 4.0, 3.0, 2.6, kit.plastic("#d7d0c8", 0.9, name="shopwall"), kit.plastic("#7a6f64", 0.8, name="shopfl"),
         oy=40.0)
    B(kit, "shop.pale", (0.7, 0.03, 1.3), (sx0, 41.45, 1.25), kit.plastic("#c9c4ba", 0.9, name="pale"))
    B(kit, "shop.hook", (0.05, 0.08, 0.05), (sx0 + 0.9, 41.43, 1.8), kit.metal("#9a9a9a", 0.4))
    kit.light("shop.l", "POINT", (sx0, 40.0, 2.4), 140, "#fff2e0", size=0.5)
    wx = sx0 + 20.0
    kit.plane("shopw.street", (14, 14), (wx, 40.0, 0.0), kit.plastic("#8e8a84", 0.9, name="street"))
    sm = kit.plastic("#5b6b78", 0.85, name="shopwall2")
    B(kit, "shopw.wl", (4.0, 0.3, 3.3), (wx - 3.5, 41.5, 1.65), sm)
    B(kit, "shopw.wr", (4.0, 0.3, 3.3), (wx + 3.5, 41.5, 1.65), sm)
    B(kit, "shopw.wt", (3.0, 0.3, 0.9), (wx, 41.5, 2.85), sm)
    B(kit, "shopw.wb", (3.0, 0.3, 0.7), (wx, 41.5, 0.35), sm)
    B(kit, "shopw.roof", (12, 5, 0.2), (wx, 43.5, 3.4), sm)
    B(kit, "shopw.back", (12, 0.2, 3.4), (wx, 46.0, 1.7), kit.plastic("#d9d2c6", 0.9, name="shopback"))
    B(kit, "shopw.floor", (12, 5, 0.1), (wx, 43.5, -0.05), kit.plastic("#7a6f64", 0.8, name="shopfl"))
    B(kit, "shopw.side", (0.2, 5, 3.4), (wx - 6, 43.5, 1.7), sm)
    B(kit, "shopw.sider", (0.2, 5, 3.4), (wx + 6, 43.5, 1.7), sm)
    kit.light("shopw.l", "POINT", (wx, 43.8, 2.9), 500, "#fff2e0", size=0.7)
    # CAFE
    cx = TOWN["cafe"]
    room("cafe", cx, 7.0, 6.0, 2.9, kit.plastic("#7d8a6a", 0.9, name="cafewall"), kit.plastic("#7c6048", 0.8, name="cafefl"),
         oy=40.0, back=False)
    cw = kit.plastic("#7d8a6a", 0.9, name="cafewall")
    # window opening on the back wall: pieces around a 2.4 x 1.3 hole at z 0.9 .. 2.2 (wall at y = 43.0)
    for nm, sz, lc in (("l", (2.3, 0.3, 2.9), (cx - 2.35, 42.9, 1.45)), ("r", (2.3, 0.3, 2.9), (cx + 2.35, 42.9, 1.45)),
                       ("t", (2.4, 0.3, 0.7), (cx, 42.9, 2.55)), ("b", (2.4, 0.3, 0.9), (cx, 42.9, 0.45))):
        B(kit, f"cafe.w{nm}", sz, lc, cw)
    B(kit, "cafe.sill", (2.6, 0.4, 0.05), (cx, 42.75, 0.92), kit.plastic("#e4dccb", 0.7, name="cafesill"))
    for nm, sz, lc in (("t", (2.6, 0.05, 0.06), (cx, 42.76, 2.2)), ("l", (0.06, 0.05, 1.3), (cx - 1.2, 42.76, 1.55)),
                       ("r", (0.06, 0.05, 1.3), (cx + 1.2, 42.76, 1.55))):
        B(kit, f"cafe.f{nm}", sz, lc, kit.plastic("#e4dccb", 0.7, name="cafesill"))
    B(kit, "cafe.table", (1.3, 0.8, 0.04), (cx, 41.1, 0.74), kit.plastic("#cdb894", 0.6, name="cafetable"))
    kit.cyl("cafe.tleg", 0.05, 0.72, (cx, 41.1, 0.36), kit.plastic("#2c3036", 0.4, name="tleg"), n=10)
    for k, x in enumerate((-0.25, 0.25)):
        kit.cyl(f"cafe.cup{k}", 0.05, 0.08, (cx + x, 41.0, 0.80), kit.plastic("#f0ece2", 0.5, name="cup2"), n=12)
    # beyond the cafe window (what they would be reflected in): a street strip lit from the side
    B(kit, "cafe.out", (6.5, 0.1, 2.2), (cx, 45.2, 1.3), kit.emit("#7e8d99", 0.35, name="cafeout"))
    kit.light("cafe.l", "POINT", (cx, 40.0, 2.5), 420, "#ffd9a8", size=0.6)
    kit.light("cafe.f", "POINT", (cx, 42.0, 2.0), 160, "#ffd9a8", size=0.6)
    kit.light("cafe.b", "POINT", (cx, 43.9, 2.0), 260, "#cfdcf0", size=0.6)


# ------------------------------------------------------------------------------------------------ first frame


def cool(spec, tint):
    import copy
    sp = copy.deepcopy(spec)
    for k in ("skin", "shirt", "pattern_c", "pants", "shoes", "collar", "hair_c", "hat_c", "extra_c", "zip_c"):
        if sp.get(k):
            sp[k] = _mix_hex(sp[k], "#3d5470", tint)
            sp[k] = _mix_hex(sp[k], "#000000", 0.12 * tint / 0.3)
    return sp


def init(kit, story, tl, ctx):
    import copy
    ctx["init"] = True
    fd = Path(tempfile.gettempdir()) / "ep50-faces"
    fd.mkdir(parents=True, exist_ok=True)
    cast = story["cast"]
    for rn, rd in story.get("reflections", {}).items():
        sp = cool(cast[rd["of"]], rd.get("tint", 0.3))
        for k, v in rd.get("set", {}).items():
            sp[k] = v
        c = rig.Character(rn, sp, fd)
        c.base = tuple(c.root.scale)
        ctx["refl"][rn] = c
    # fog nodes (every material's fog emission), found once the cast exists
    nodes = []
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        for n in m.node_tree.nodes:
            if n.type != "EMISSION":
                continue
            for l in n.outputs[0].links:
                if l.to_node.type == "MIX_SHADER" and l.to_socket == l.to_node.inputs[2]:
                    nodes.append(n)
    ctx["fognodes"] = nodes
    # the Small Head: vertical bands on the body, a head the size of a fist
    cr = bpy.data.objects.get("smallhead")
    if cr is not None:
        can = kit.MATS["canvas"]
        sh = [ob for ob in bpy.data.objects if ob.name in ("smallhead.torsom", "smallhead.sleeve-1", "smallhead.sleeve1")]
        for ob in sh:
            ob.data.materials.clear()
            ob.data.materials.append(can)
        wd = story["cast"]["smallhead"].get("width", 1.0)
        hs = story["cast"]["smallhead"].get("head_scale", 0.34)
        head = bpy.data.objects.get("smallhead.head")
        head.scale = (hs / wd * 0.9, hs, hs * 1.05)   # a small blocky head
        for sx in (-1, 1):   # no legs: the canvas drapes over the chair
            bpy.data.objects[f"smallhead.leg{sx}"].scale = (0.001, 0.001, 0.001)
        # lifted clear of the stripes on a neck
        nl = story["cast"]["smallhead"].get("neck", 0.0)
        if nl:
            nk = bpy.data.objects["smallhead.neck"]
            nk.location = (0, 0, 2.0 + nl)
            skin = bpy.data.objects["smallhead.headm"].data.materials[0] if False else None
            skm = kit.plastic(story["cast"]["smallhead"]["skin"], 0.5)
            kit.box("smallhead.neckm", (0.42, 0.42, nl + 0.3), (0, 0, 2.0 + nl / 2 - 0.05), skm,
                    bpy.data.objects["smallhead.torso"], bevel=0.06)
    ctx["base"] = {}
    for who in story["cast"]:
        o = bpy.data.objects.get(who)
        ctx["base"][who] = tuple(o.scale) if o else None


def pose_char(c, tl, name, t, seed, hidden=False):
    keys = tl["acting"].get(name)
    if not keys or hidden:
        c.pose(0, 0, 0, 0, hidden=True)
        if name == "smallhead" and bpy.data.objects.get("smallhead.neckm") is not None:
            bpy.data.objects["smallhead.neckm"].hide_render = True
        return None
    s = acting.state(tl, name, t, seed)
    c.pose(s["x"], s["y"], s["z"], s["yaw"], s["legs"], s["arms"], s["arms_side"], s["head_yaw"], s["head_pitch"],
           s["lean"], s["bob"], s["expr"], s["mouth"], s["look"], s["blink"], s["hidden"])
    if _switch(keys, "sit", t, False) and not s["hidden"]:
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{c.name}.leg{sx}")
            leg.rotation_euler = (-math.pi / 2, 0, 0)
    if name == "smallhead":
        nm = bpy.data.objects.get("smallhead.neckm")
        if nm is not None:
            nm.hide_render = bool(s["hidden"])   # the neck block is made after the rig: it must hide with it
    if name == "smallhead" and not s["hidden"]:
        hd = bpy.data.objects.get("smallhead.head")
        hd.rotation_euler = (hd.rotation_euler[0], hd.rotation_euler[1] + 0.22, hd.rotation_euler[2])   # tilted a little
    bow = math.radians(_held(keys, "bow", t, 0.0))
    tor = bpy.data.objects.get(f"{c.name}.torso")
    if tor is not None:
        tor.rotation_euler = (bow, 0, 0)
        if bow:
            for sx in (-1, 1):
                arm = bpy.data.objects.get(f"{c.name}.arm{sx}")
                e = arm.rotation_euler
                arm.rotation_euler = (e[0] - bow * 0.0, e[1], e[2])
    return s


def animate(kit, story, tl, t, ctx):
    if not ctx["init"]:
        init(kit, story, tl, ctx)
    shot = _shot(tl, t)
    sx_ = story.get("shotx", {}).get(shot["id"], {})
    # --- time of day
    prev = TOD["day"]
    cur = dict(prev)
    for c in sorted(_cues(tl, "tod"), key=lambda c: c["t"]):
        if t < c["t"]:
            break
        u = ss((t - c["t"]) / max(1e-6, c.get("dur", 0.0001)))
        tgt = TOD[c["set"]]
        cur = dict(cur)
        for k in ("se", "el", "az", "ss"):
            cur[k] = cur[k] + (tgt[k] - cur[k]) * u
        for k in ("sc", "sky", "fog", "back"):
            cur[k] = _mix_hex(cur[k], tgt[k], u)
    gl = float(sx_.get("gloom", 0.0))
    cur["se"] *= (1 - gl)
    cur["ss"] *= (1 - 0.8 * gl)
    sun = ctx["sun"]
    el, az = math.radians(cur["el"]), math.radians(cur["az"])
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))   # toward the sun, from the sea
    d = Vector((d.x, -d.y, d.z))
    sun.location = d * 40
    kit.aim(sun, (0, 0, 0))
    sun.data.color = kit.col(cur["sc"])[:3]
    kit.LIGHTS["sun"]["base"] = cur["se"]
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = kit.col(cur["sky"])
    bg.inputs["Strength"].default_value = cur["ss"]
    fc = kit.col(cur["fog"])
    for n in ctx["fognodes"]:
        n.inputs["Color"].default_value = fc
    ctx["backnode"].inputs["Color"].default_value = kit.col(cur["back"])
    # --- cast
    ctx.setdefault("seeds", {})
    for i, who in enumerate(story["cast"]):
        pass
    for rn, c in ctx["refl"].items():
        kind = sx_.get("refl", {}).get(rn)
        place_refl(kit, tl, ctx, rn, c, kind, t, sx_)
    # Remi's scarf (worn only some of the time)
    scarf_on = (_last(tl, "remi_scarf", t) or {"on": True})["on"]
    for nm in ("remi.scarf", "remi.scarft"):
        ob = bpy.data.objects.get(nm)
        if ob is not None:
            ob.hide_render = (not scarf_on) or bpy.data.objects["remi"].hide_render
    # extra keys on real cast: sit, bow
    for who in story["cast"]:
        keys = tl["acting"].get(who, [])
        root = bpy.data.objects.get(who)
        if root is None or not keys:
            continue
        if _switch(keys, "sit", t, False):
            for sx in (-1, 1):
                bpy.data.objects[f"{who}.leg{sx}"].rotation_euler = (-math.pi / 2, 0, 0)
        bow = math.radians(_held(keys, "bow", t, 0.0))
        tor = bpy.data.objects.get(f"{who}.torso")
        tor.rotation_euler = (bow, 0, 0)
        # the Small Head's head: nothing else to do, it is posed by its acting keys
    cam = kit.OBJ["cam"]
    dof = sx_.get("dof")
    cam.data.dof.use_dof = bool(dof)
    if dof:
        cam.data.dof.focus_distance = float(dof[0])
        cam.data.dof.aperture_fstop = float(dof[1])
    # --- hut stage
    st = sx_.get("stage")
    ctx["stage"].hide_render = st is None
    for ob in ctx["stage"].children_recursive:
        if ob.name.startswith("r_"):
            continue   # a reflection parented to the stage keeps its own hidden flag (it was being unhidden here)
        ob.hide_render = st is None
    if st is not None:
        h = st["hut"]
        if h == 4:
            ctx["stage"].location = (hx(h) + BIGWIN[0], 0.12, BIGWIN[2])
            ctx["stage"].scale = (1.5, 1.5, 1.5)
        else:
            ctx["stage"].location = (hx(h) + WIN_X, 0.12, WIN_Z0)
            ctx["stage"].scale = (1.0, 1.0, 1.0)
        # the stage sits behind the glass: its x is centred on the window
    sc_on = bool(sx_.get("schair")) and st is not None
    ctx["schair"].hide_render = not sc_on
    for ob in ctx["schair"].children_recursive:
        ob.hide_render = not sc_on
    # --- doors
    dc = _cues(tl, "door")
    ang = 0.0
    for c in sorted(dc, key=lambda c: c["t"]):
        if t < c["t"]:
            break
        u = ss((t - c["t"]) / max(1e-6, c.get("dur", 0.8)))
        ang = ang + (c["open"] - ang) * u
    for hdat in ctx["huts"]:
        hdat["hinge"].rotation_euler = (0, 0, math.radians(100) * (ang if hdat["x"] == 0 else 0))
    # --- chairs
    cb = _last(tl, "chairB", t) or {"state": "hidden"}
    sag = _ramp(tl, "chairB", "sag", t, 0.0)
    place_chair(kit, ctx["chairB"], tuple(cb.get("pos", (WIN_X, -0.95, DECK_Z))), cb.get("yaw", 0), sag,
                folded=cb["state"] == "folded", hidden=cb["state"] == "hidden")
    ca = _last(tl, "chairA", t) or {"state": "open"}
    place_chair(kit, ctx["chairA"], (CHAIR_A[0], CHAIR_A[1], DECK_Z), 0, 0.0, hidden=ca["state"] == "hidden")
    sp = _last(tl, "scarfprop", t) or {"on": False}
    ctx["scarfprop"].hide_render = not sp["on"]
    for ob in ctx["scarfprop"].children_recursive:
        ob.hide_render = not sp["on"]
    ctx["scarfprop"].location = (CHAIR_A[0], CHAIR_A[1] - 0.03, DECK_Z + 0.43)
    ctx["scarfprop"].rotation_euler = (math.radians(-12), 0, 0)
    # --- laptop
    lc = _last(tl, "laptop", t) or {"mode": "hide"}
    lap = ctx["laptop"]
    show = lc.get("mode", "hide") != "hide"
    lap.hide_render = not show
    for ob in lap.children_recursive:
        ob.hide_render = not show
    op = _ramp(tl, "laptop", "open", t, 1.0)
    ctx["lap_hinge"].rotation_euler = (math.radians(-100 * op), 0, 0)
    ctx["lap_screen"].inputs["Strength"].default_value = 1.2 * ss(op * 1.5)
    if show:
        lap.location = tuple(lc.get("pos", (0, -0.9, 0.62)))
        lap.rotation_euler = (0, 0, math.radians(lc.get("yaw", 0)))
    # --- puddle, kettle steam
    pu = sx_.get("puddle", False)
    ctx["puddle"].hide_render = not pu
    for ob in ctx["puddle"].children_recursive:
        ob.hide_render = not pu
    # --- lights
    over = {}
    over["lantern"] = ss(_ramp(tl, "lantern", "on", t, 0.0))
    lp = [c for c in _cues(tl, "lantern") if c["t"] <= t and "pos" in c]
    lx, ly = (lp[-1]["pos"] if lp else LANT)
    ctx["lantern"].location = (lx, ly, DECK_Z)
    kit.LIGHTS["lantern"]["obj"].location = (lx, ly, DECK_Z + 0.16)
    over["laptop"] = ss(op) * (1.0 if show else 0.0) * _ramp(tl, "lapglow", "on", t, 1.0)
    over["hutin"] = _ramp(tl, "hutin", "on", t, 0.0)
    over["rim"] = _ramp(tl, "rim", "on", t, 0.0)
    lift = ss(_ramp(tl, "lift", "on", t, 0.0))
    over["headkey"] = lift * (0.0 if sx_.get("ghost") else 1.0)
    over["shadowkey"] = 1.0 if sx_.get("ghost") else 0.0
    over["lantern"] = over["lantern"] * (0.0 if sx_.get("ghost") else 1.0)
    over["stagelit"] = _ramp(tl, "stagelit", "on", t, 0.0)
    over["faceup"] = lift * (0.0 if sx_.get("ghost") else 1.0)
    over["dusklift"] = lift
    over["benchlift"] = ss(_ramp(tl, "benchlift", "on", t, 0.0))
    # ghost shots: the Small Head is out of sight but its shadow still falls (L42 to L43)
    gh = bool(sx_.get("ghost"))
    for ob in bpy.data.objects:
        if ob.name.startswith("smallhead"):
            if gh:
                ob.hide_render = False
            ob.visible_camera = not (gh or bool(sx_.get("hidecr")))
            ob.visible_shadow = not sx_.get("hidecr")
    nm, hm = bpy.data.objects.get("smallhead.neckm"), bpy.data.objects.get("smallhead.headm")
    if nm is not None and hm is not None and not gh:
        nm.hide_render = hm.hide_render   # the neck block hides with the head
    return over


def place_refl(kit, tl, ctx, rn, c, kind, t, sx_):
    """Pose one reflection for its shot (see the module doc)."""
    if kind is None:
        c.pose(0, 0, 0, 0, hidden=True)
        return
    if isinstance(kind, str):
        kind = {"kind": kind}
    k = kind["kind"]
    keys = tl["acting"].get(rn)
    if not keys:
        c.pose(0, 0, 0, 0, hidden=True)
        return
    base = c.base
    s = acting.state(tl, rn, t, 3)
    z = s["z"]
    px, py = s["x"], s["y"]
    root = c.root
    if k == "stage":
        d = max(0.0, min(1.0, s["y"]))
        sc = ctx["sfn"](d)
        if root.parent is not ctx["stage"]:
            root.parent = ctx["stage"]
        # lateral x is in window metres at the glass and shrinks with depth like everything else
        c.pose(px * sc, 0.8 * d + 0.02, 0.3 * d + 0.006 + z * sc, s["yaw"], s["legs"], s["arms"],
               s["arms_side"], s["head_yaw"], s["head_pitch"], s["lean"], 0.0, s["expr"], s["mouth"], s["look"],
               s["blink"], s["hidden"])
        big = _held(keys, "big", t, 1.0)
        root.scale = (base[0] * sc * big, base[1] * sc * big, base[2] * sc * big)
        if _switch(keys, "stroll", t, False) and not s["hidden"]:
            # the stage's distances are tiny, so the acting's own leg swing never starts: walk in place
            ph = t * 2 * math.pi / 0.85
            for sx in (-1, 1):
                bpy.data.objects[f"{c.name}.leg{sx}"].rotation_euler = (sx * 0.38 * math.sin(ph), 0, 0)
                bpy.data.objects[f"{c.name}.arm{sx}"].rotation_euler = (-sx * 0.4 * math.sin(ph), 0, 0)
    else:
        if root.parent is not None:
            root.parent = None
        flip = k in ("sand", "table")
        zbase = kind.get("base", 0.0)
        c.pose(px, py, (zbase + (-z if flip else z)), s["yaw"], s["legs"], s["arms"], s["arms_side"], s["head_yaw"],
               s["head_pitch"], s["lean"], 0.0, s["expr"], s["mouth"], s["look"], s["blink"], s["hidden"])
        zs = kind.get("scale", 1.0)
        root.scale = (base[0] * zs, base[1] * zs, (-base[2] if flip else base[2]) * zs)
    roll = math.radians(_held(keys, "roll", t, 0.0))
    if roll:
        e = root.rotation_euler
        root.rotation_euler = (e.x, roll, e.z)
        if k == "stage":
            # a cartwheel turns about the hips, not the feet: shift the root so the hips stay where they were
            zc = 2.3 * root.scale[2]
            root.location = (root.location.x - zc * math.sin(roll), root.location.y, root.location.z + zc * (1 - math.cos(roll)))
    if _switch(keys, "sit", t, False) and not s["hidden"]:
        for sx in (-1, 1):
            bpy.data.objects[f"{c.name}.leg{sx}"].rotation_euler = (-math.pi / 2, 0, 0)
    bow = math.radians(_held(keys, "bow", t, 0.0))
    tor = bpy.data.objects.get(f"{c.name}.torso")
    tor.rotation_euler = (bow, 0, 0)
    sx0 = kind.get("scarf")
    if sx0 is not None:
        for nm in (f"{rn}.scarf", f"{rn}.scarft"):
            ob = bpy.data.objects.get(nm)
            if ob is not None:
                ob.hide_render = not sx0
