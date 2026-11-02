"""Comet Night: a sunny cream-stone square where every promise ties a glowing knot onto a cord over your head, the
hill behind it with a small house, and the green-domed observatory on top, inside and out. Built from kit.py's parts
(batch 4, ep37; nothing here is shared with another story's set).

Three zones, far apart so their lights never meet: the SQUARE at the origin (day), the HILL at x = 200 (the house,
the path, the dome from outside, dusk and night) and the DOME's inside at x = -300. The shot's "scene" (day, memory,
dusk, night, dome) in story.json says which lights, sky and fog colour are on.

THE MAN WITH THE HOLE (the creature, never named): one model, built once in build_keeper() and only posed per
cue. A person of 1.85 m in a long dome-green coat with two rows of brass buttons, verdigris skin, and a clean
30 x 30 cm square hole through the chest. A card in the hole shows a starfield whatever is behind it. Two lens-ring
eyes with one cold highlight each, no mouth, no brows, no cord. It carries no light of its own.

Cues read here (all optional, set by generator/make_story.py):
- keeper: {pos: [x, y] (dome metres), yaw, bend, head: [yaw, pitch], sit: 0..1, hidden: bool}  held until the next
- streak: {dur}  the bright streak crossing the hole
- star: {pos: [x, z], dur}  a small shooting star over the slit
- dome: {bulbs: 0..1, dur}  the four warm bulbs, eased over dur (never a switch)
- cloud: {amount: 0..1, pink: 0..1, dur}  the sky through the slit
- knot: {who, i, scale, glow, dur}  one knot's size and glow, eased
- cordset: {who, len, stand, dur}  a cord's length and how straight it stands, eased
- hair: {who, color}  a hair colour swap (Dad's four greys)
- puff: {who, dur}  a small rose puff at someone's cord
- bag: {on}  Dad's packed bag in the memory shots
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import bpy
from mathutils import Vector as V, Matrix
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
S = 0.34                       # rig metres per unit
HX, CX = 200.0, -300.0        # the hill's and the dome's x
TH = math.radians(10)          # the hill's slope
Y0 = 12.0                      # where the flat ground becomes the slope
DOME_YL = 58.0                 # the dome's distance up the slope from the hinge
SEAT = 0.46

ROSE = "#ff8fb0"


def hill(x, yl, zl=0.0):
    """Slope-local (x across, yl up the slope from the hinge, zl off the ground) to world."""
    return (HX + x, Y0 + yl * math.cos(TH) - zl * math.sin(TH), yl * math.sin(TH) + zl * math.cos(TH))


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def _last(cs, t):
    cs = [c for c in cs if c["t"] <= t + 1e-9]
    return cs[-1] if cs else None


def _eased(cs, key, t, default):
    level = prev = default
    for c in cs:
        if c["t"] > t + 1e-9 or key not in c:
            continue
        prev, level = level, c[key]
        d = float(c.get("dur", 0.0))
        if d > 0 and t < c["t"] + d and isinstance(level, (int, float)) and isinstance(prev, (int, float)):
            level = prev + (level - prev) * _ss((t - c["t"]) / d)
    return level


def workdir(tl) -> Path:
    d = ROOT / "out" / "work" / tl.get("name", "ep37-comet-night") / "faces"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ------------------------------------------------------------------------------------------- nodes and materials


def _node_mat(kit, name):
    m = kit._new(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return m, nt


def star_mat(kit, name, scale=26.0, thresh=0.5, size=0.2, bright=5.0, gradient=False):
    """A sky of random dots (no real constellations). Controls (nodes kept on the material): 'stars' (0..1),
    'bgh' and 'bgz' (horizon and zenith colours). Emission only, so the fog never touches it."""
    m, nt = _node_mat(kit, name)
    N, Lk = nt.nodes, nt.links
    out = N.new("ShaderNodeOutputMaterial")
    tc = N.new("ShaderNodeTexCoord")
    vor = N.new("ShaderNodeTexVoronoi")
    vor.feature = "F1"
    vor.inputs["Scale"].default_value = scale
    Lk.new(tc.outputs["Object"], vor.inputs["Vector"])
    sep = N.new("ShaderNodeSeparateColor")
    Lk.new(vor.outputs["Color"], sep.inputs["Color"])
    gt = N.new("ShaderNodeMath")
    gt.operation = "GREATER_THAN"
    gt.inputs[1].default_value = thresh
    Lk.new(sep.outputs["Red"], gt.inputs[0])
    rng = N.new("ShaderNodeMapRange")
    rng.inputs["From Min"].default_value = 0.0
    rng.inputs["From Max"].default_value = size
    rng.inputs["To Min"].default_value = 1.0
    rng.inputs["To Max"].default_value = 0.0
    Lk.new(vor.outputs["Distance"], rng.inputs["Value"])
    dot = N.new("ShaderNodeMath")
    dot.operation = "MULTIPLY"
    Lk.new(rng.outputs["Result"], dot.inputs[0])
    Lk.new(gt.outputs[0], dot.inputs[1])
    ctl = N.new("ShaderNodeValue")
    ctl.name = "stars"
    ctl.outputs[0].default_value = 1.0
    fac = N.new("ShaderNodeMath")
    fac.operation = "MULTIPLY"
    Lk.new(dot.outputs[0], fac.inputs[0])
    Lk.new(ctl.outputs[0], fac.inputs[1])
    bgh = N.new("ShaderNodeRGB")
    bgh.name = "bgh"
    bgz = N.new("ShaderNodeRGB")
    bgz.name = "bgz"
    bgh.outputs[0].default_value = kit.col("#0b1226")
    bgz.outputs[0].default_value = kit.col("#0b1226")
    sepx = N.new("ShaderNodeSeparateXYZ")
    Lk.new(tc.outputs["Object"], sepx.inputs[0])
    gz = N.new("ShaderNodeMath")
    gz.operation = "MULTIPLY"
    gz.use_clamp = True
    gz.inputs[1].default_value = 2.5
    Lk.new(sepx.outputs["Z"], gz.inputs[0])
    mix0 = N.new("ShaderNodeMix")
    mix0.data_type = "RGBA"
    Lk.new(gz.outputs[0], mix0.inputs["Factor"])
    Lk.new(bgh.outputs[0], mix0.inputs["A"])
    Lk.new(bgz.outputs[0], mix0.inputs["B"])
    mix1 = N.new("ShaderNodeMix")
    mix1.data_type = "RGBA"
    mix1.inputs["B"].default_value = kit.col("#d6e4ff")
    Lk.new(fac.outputs[0], mix1.inputs["Factor"])
    Lk.new(mix0.outputs["Result"], mix1.inputs["A"])
    st = N.new("ShaderNodeMath")
    st.operation = "MULTIPLY_ADD"
    st.inputs[1].default_value = bright
    st.inputs[2].default_value = 1.0
    Lk.new(fac.outputs[0], st.inputs[0])
    em = N.new("ShaderNodeEmission")
    Lk.new(mix1.outputs["Result"], em.inputs["Color"])
    Lk.new(st.outputs[0], em.inputs["Strength"])
    Lk.new(em.outputs[0], out.inputs["Surface"])
    return m


def hole_mat(kit):
    """The card in the creature's chest: stars whatever is behind it. Both sides."""
    m, nt = _node_mat(kit, "hole sky")
    N, Lk = nt.nodes, nt.links
    out = N.new("ShaderNodeOutputMaterial")
    tc = N.new("ShaderNodeTexCoord")
    vor = N.new("ShaderNodeTexVoronoi")
    vor.feature = "F1"
    vor.inputs["Scale"].default_value = 48.0
    Lk.new(tc.outputs["Object"], vor.inputs["Vector"])
    sep = N.new("ShaderNodeSeparateColor")
    Lk.new(vor.outputs["Color"], sep.inputs["Color"])
    gt = N.new("ShaderNodeMath")
    gt.operation = "GREATER_THAN"
    gt.inputs[1].default_value = 0.42
    Lk.new(sep.outputs["Red"], gt.inputs[0])
    rng = N.new("ShaderNodeMapRange")
    rng.inputs["From Max"].default_value = 0.2
    rng.inputs["To Min"].default_value = 1.0
    rng.inputs["To Max"].default_value = 0.0
    Lk.new(vor.outputs["Distance"], rng.inputs["Value"])
    dot = N.new("ShaderNodeMath")
    dot.operation = "MULTIPLY"
    Lk.new(rng.outputs["Result"], dot.inputs[0])
    Lk.new(gt.outputs[0], dot.inputs[1])
    mix = N.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = kit.col("#0a1234")
    mix.inputs["B"].default_value = kit.col("#dbe8ff")
    Lk.new(dot.outputs[0], mix.inputs["Factor"])
    st = N.new("ShaderNodeMath")
    st.operation = "MULTIPLY_ADD"
    st.inputs[1].default_value = 6.0
    st.inputs[2].default_value = 0.7
    Lk.new(dot.outputs[0], st.inputs[0])
    em = N.new("ShaderNodeEmission")
    Lk.new(mix.outputs["Result"], em.inputs["Color"])
    Lk.new(st.outputs[0], em.inputs["Strength"])
    Lk.new(em.outputs[0], out.inputs["Surface"])
    return m


def glow_mat(kit, name, hexc, strength):
    """A lit surface that the fog leaves alone (bulbs, window panes, the lens highlights). `.strength` is kept."""
    m, nt = _node_mat(kit, name)
    N, Lk = nt.nodes, nt.links
    out = N.new("ShaderNodeOutputMaterial")
    em = N.new("ShaderNodeEmission")
    em.name = "E"
    em.inputs["Color"].default_value = kit.col(hexc)
    em.inputs["Strength"].default_value = strength
    Lk.new(em.outputs[0], out.inputs["Surface"])
    return m


def knot_mat(kit, name, base, emit_hex, strength, rough=0.5):
    """A knot: a principled surface plus an emission we can turn up and down (the rose glow)."""
    m = kit._new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(base)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Emission Color"].default_value = kit.col(emit_hex)
    b.inputs["Emission Strength"].default_value = strength
    return m


def set_emit(m, strength):
    m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = strength


def set_rgb(m, node, hexc, kit):
    m.node_tree.nodes[node].outputs[0].default_value = kit.col(hexc)


def chart_image(path: Path, seed, w=420, h=300):
    """A pinned star chart of our own: dots joined by faint lines, and a few glyphs. No letters, no real sky."""
    rnd = random.Random(seed)
    im = Image.new("RGB", (w, h), (36, 52, 84))
    d = ImageDraw.Draw(im)
    for _ in range(140):
        x, y = rnd.randrange(w), rnd.randrange(h)
        r = rnd.choice((1, 1, 1, 2))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(226, 232, 244))
    for _ in range(3):
        pts = [(rnd.randrange(30, w - 30), rnd.randrange(30, h - 30)) for _ in range(rnd.randrange(4, 7))]
        d.line(pts, fill=(130, 150, 200), width=1)
        for p in pts:
            d.ellipse((p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3), outline=(240, 240, 255), width=1)
    for k in range(4):
        x, y = rnd.randrange(30, w - 30), rnd.randrange(30, h - 30)
        s = rnd.choice((7, 9))
        if k % 2:
            d.polygon([(x, y - s), (x + s, y + s), (x - s, y + s)], outline=(240, 200, 120))
        else:
            d.ellipse((x - s, y - s, x + s, y + s), outline=(240, 200, 120))
    d.rectangle((3, 3, w - 4, h - 4), outline=(216, 206, 176), width=3)
    im.save(path)
    return path


def img_mat(kit, name, path, rough=0.9):
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(path), check_existing=True)
    tex.image.colorspace_settings.name = "sRGB"
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    kit._fogged(m, b.outputs[0])
    return m


def materials(kit, wd: Path):
    M = {}
    M["stone"] = kit.grime("#e8dcc0", 0.8, 2.0, name="stone cream")
    M["stone2"] = kit.grime("#d9caa6", 0.7, 3.0, name="stone cream dark")
    M["cob"] = kit.cobbles("#cdbf9e", "#eadfc4", "#9d8f72", scale=2.4, wet=0.05, name="cobbles cream")
    M["path"] = kit.cobbles("#8d8470", "#b0a68e", "#4c463a", scale=3.2, wet=0.0, name="path stones")
    M["terra"] = kit.grime("#c46a3c", 0.72, 4.0, name="terracotta")
    M["window"] = kit.plastic("#3d5a78", 0.2, name="window glass")
    M["dark"] = kit.plastic("#1b1a1e", 0.8, name="dark")
    M["brass"] = kit.metal("#b8883a", 0.45, name="brass")
    M["iron"] = kit.metal("#2a2b2e", 0.5, name="iron")
    M["verd"] = kit.plastic("#3f7f6a", 0.5, name="verdigris")
    M["verd_dome"] = kit.grime("#3f7f6a", 0.62, 6.0, name="dome green")
    M["leather"] = kit.plastic("#5a1f22", 0.45, name="oxblood leather")
    M["woodA"] = kit.planks("#6e5c4a", "#4a3e32", 1.4, "X", name="oak floor")
    M["woodB"] = kit.planks("#5e4a38", "#3e3226", 1.6, "Y", name="oak dark")
    M["wall"] = kit.planks("#d4cebd", "#b6b09e", 1.5, "Z", name="whitewash boards", rough=0.85)
    M["dome_in"] = kit.grime("#b3ae9c", 0.7, 2.0, name="dome inside")
    M["dust"] = kit.plastic("#8d887e", 0.98, name="dust")
    M["pier"] = kit.grime("#6a6a68", 0.6, 5.0, name="dusty iron")
    M["grass"] = kit.grime("#9a8a52", 0.55, 8.0, name="dry grass ground")
    M["tuft1"] = kit.plastic("#b0a05c", 0.9, name="tuft1")
    M["tuft2"] = kit.plastic("#8c7c44", 0.9, name="tuft2")
    M["white"] = kit.grime("#ddd7c6", 0.78, 2.5, name="house white")
    M["cord"] = kit.plastic("#e6dfd0", 0.8, name="cord pale")
    M["cord_grey"] = kit.plastic("#a6a6a2", 0.9, name="cord grey")
    M["coat"] = kit.grime("#35705c", 0.55, 9.0, name="coat green")
    M["coat_dk"] = kit.plastic("#2c5e4d", 0.7, name="coat dark")
    M["kskin"] = kit.plastic("#4d7f69", 0.6, name="keeper skin")
    M["ktrou"] = kit.plastic("#2d5c4a", 0.7, name="keeper trousers")
    M["kboot"] = kit.plastic("#171b19", 0.5, name="keeper boots")
    M["lens"] = kit.metal("#9a7a40", 0.3, name="lens ring")
    M["black"] = kit.plastic("#050506", 0.2, name="lens black")
    M["hole"] = hole_mat(kit)
    M["glint"] = glow_mat(kit, "glint", "#f0f6ff", 9.0)
    M["bulb"] = glow_mat(kit, "bulb", "#ffc27a", 6.0)
    M["redlens"] = glow_mat(kit, "red lens", "#b8362c", 2.0)
    M["pane"] = glow_mat(kit, "pane", "#ffc07a", 4.0)
    M["streak"] = glow_mat(kit, "streak", "#eef4ff", 8.0)
    M["gline"] = glow_mat(kit, "grey line", "#7e7f7a", 0.5)
    M["puff"] = glow_mat(kit, "puff", ROSE, 1.2)
    M["sky_dome"] = star_mat(kit, "sky dome", scale=22.0, thresh=0.5, size=0.17, gradient=True)
    M["sky_hill"] = star_mat(kit, "sky hill", scale=22.0, thresh=0.5, size=0.17, gradient=True)
    M["bunting"] = [kit.plastic(c, 0.8, name=f"flag {c}") for c in ("#e9a3a8", "#f0d9a0", "#8ec9a8", "#9fb7e0")]
    M["awn"] = [kit.plastic("#d9d4c6", 0.8, name="awn w"), kit.plastic("#b5532c", 0.8, name="awn r")]
    for i in range(3):
        p = chart_image(wd / f"chart{i}.png", 11 + i)
        M[f"chart{i}"] = img_mat(kit, f"chart {i}", p)
    return M


# ------------------------------------------------------------------------------------------------ small builders


def box(kit, name, size, loc, mat, parent=None, rot=(0, 0, 0), bevel=0.0):
    return kit.box(name, size, loc, mat, parent, rot, bevel=bevel)


def dome_shell(kit, name, R, z0, mat, slit_w, slit_cx, loc=(0, 0, 0), n=40, rings=14):
    """A hemisphere shell with a slit open from the rim over the top."""
    verts, faces = [], []
    for i in range(rings + 1):
        a = 0.04 + (math.pi / 2 - 0.04) * i / rings
        for j in range(n):
            ph = 2 * math.pi * j / n
            verts.append((R * math.sin(a) * math.cos(ph), R * math.sin(a) * math.sin(ph), R * math.cos(a)))
    for i in range(rings):
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            c, d = b + n, a + n
            cx = sum(verts[k][0] for k in (a, b, c, d)) / 4
            if abs(cx - slit_cx) < slit_w / 2:
                continue
            faces.append((a, b, c, d))
    return kit.mesh_obj(name, verts, faces, mat, None, (loc[0], loc[1], loc[2] + z0), smooth=True)


def seg_between(ob, p0, p1, thick):
    d = V(p1) - V(p0)
    L = d.length
    if L < 1e-5:
        ob.hide_render = True
        return
    ob.hide_render = False
    up = "X" if abs(d.normalized().y) > 0.9 else "Y"
    ob.rotation_euler = d.to_track_quat("Z", up).to_euler()
    ob.location = (V(p0) + V(p1)) / 2
    ob.scale = (thick, thick, L)


# ------------------------------------------------------------------------------------------------ the square


def build_square(kit, ctx, M):
    kit.plane("square ground", (90, 90), (0, 0, 0), M["cob"])
    # the civic building, its steps, door and blank medallion
    box(kit, "civic", (14, 5.5, 6.6), (0, 13.75, 3.3), M["stone"])
    box(kit, "civic roof", (15.4, 6.6, 0.5), (0, 13.75, 6.85), M["terra"])
    box(kit, "civic cornice", (14.4, 0.5, 0.3), (0, 10.9, 6.4), M["stone2"])
    for i in range(5):
        y0 = 8.4 + 0.55 * i
        box(kit, f"step{i}", (8.4, 11.0 - y0, 0.18 * (i + 1)), (0, (y0 + 11.0) / 2, 0.09 * (i + 1)), M["stone2"])
    box(kit, "civic door", (1.7, 0.3, 2.5), (0, 10.95, 1.05 + 0.9), M["woodB"])
    kit.cyl("civic arch", 0.85, 0.3, (0, 10.95, 3.1 + 0.45), M["woodB"], rot=(math.pi / 2, 0, 0))
    kit.cyl("medallion", 0.7, 0.08, (0, 10.9, 4.9), M["stone2"], rot=(math.pi / 2, 0, 0), n=32)
    kit.cyl("medallion ring", 0.82, 0.05, (0, 10.93, 4.9), M["stone2"], rot=(math.pi / 2, 0, 0), n=32)
    for x in (-5.2, -3.2, 3.2, 5.2):
        box(kit, f"civic win{x}", (0.9, 0.2, 1.6), (x, 10.95, 3.6), M["window"])
    # the side buildings, terracotta roofs, the cafe on the east
    for k, (x, w, h, y0, y1) in enumerate([(-17, 11, 6.0, -10, 14), (17, 11, 5.4, -10, 14), (-6, 12, 5.0, -24, -16),
                                              (8, 12, 5.8, -24, -16)]):
        box(kit, f"bld{k}", (w, y1 - y0, h), (x, (y0 + y1) / 2, h / 2), M["stone"] if k % 2 == 0 else M["stone2"])
        box(kit, f"bld{k} roof", (w + 1.0, y1 - y0 + 1.0, 0.45), (x, (y0 + y1) / 2, h + 0.2), M["terra"])
        face_x = x + (-w / 2 if x > 0 else w / 2) if abs(x) > 10 else None
        for j in range(4):
            if abs(x) > 10:
                yy = y0 + 4 + j * 5
                box(kit, f"b{k}w{j}", (0.2, 1.1, 1.7), (x + (-w / 2 - 0.05 if x > 0 else w / 2 + 0.05), yy, 3.2), M["window"])
            else:
                xx = x - 4 + j * 2.7
                box(kit, f"b{k}w{j}", (1.1, 0.2, 1.7), (xx, y1 + 0.05, 3.2), M["window"])
    # the cafe awning: stripes slanting out from the east building at x = 11.5
    for j in range(8):
        y = -3.4 + j * 0.85
        box(kit, f"awning{j}", (2.6, 0.85, 0.07), (10.3, y + 0.4, 3.0), M["awn"][j % 2], rot=(0, math.radians(8), 0))
    for y in (-1.0, 1.6):
        kit.cyl(f"table top{y}", 0.55, 0.05, (10.4, y, 0.75), M["woodA"])
        kit.cyl(f"table leg{y}", 0.05, 0.72, (10.4, y, 0.36), M["iron"])
        box(kit, f"cafe chair{y}", (0.42, 0.42, 0.05), (9.3, y, 0.45), M["woodB"])
        box(kit, f"cafe chair back{y}", (0.05, 0.42, 0.5), (9.08, y, 0.72), M["woodB"])
        for sx in (-1, 1):
            for sy in (-1, 1):
                box(kit, f"cafe chair leg{y}{sx}{sy}", (0.04, 0.04, 0.45), (9.3 + sx * 0.17, y + sy * 0.17, 0.22), M["iron"])
    box(kit, "phone", (0.2, 0.11, 0.012), (10.3, -1.0, 0.785), M["dark"])
    # the bench the old friends sit on (west)
    box(kit, "bench seat", (0.5, 2.4, 0.07), (-8.5, -1.1, 0.45), M["woodB"])
    box(kit, "bench back", (0.07, 2.4, 0.55), (-8.8, -1.1, 0.78), M["woodB"])
    for y in (-2.1, -0.1):
        box(kit, f"bench leg{y}", (0.4, 0.07, 0.45), (-8.5, y, 0.22), M["iron"])
    # bunting in plain triangles on strings across the square
    for k, (a, b) in enumerate([((-12, 4, 5.2), (12, 4, 5.2)), ((-12, -7, 4.8), (12, -7, 4.8)), ((-12, 0, 5.0), (12, 0, 5.0))]):
        for i in range(17):
            u = i / 16
            x = a[0] + (b[0] - a[0]) * u
            sag = 0.5 * 4 * u * (1 - u)
            z = a[2] - sag
            ob = kit.box(f"flag{k}-{i}", (0.34, 0.02, 0.4), (x, a[1], z - 0.2), M["bunting"][(i + k) % 4])
    # an umbrella (the kept promise), folded, rests on the neighbour's forearms
    ctx["umbrella"] = kit.cyl("umbrella", 0.045, 0.95, (-2.7, -1.62, 1.02), kit.plastic("#2f5d44", 0.7, name="umbrella"),
                              rot=(math.pi / 2, 0, math.pi / 2))
    # the mayor's scarf of cords and his round blank medallion, built where he stands (3.5, 2.5)
    mx, my = 3.5, 2.5
    rnd = random.Random(5)
    ctx["scarf"] = []
    for ring in range(3):
        r = 0.34 + 0.02 * ring
        z = 1.27 + 0.07 * ring
        for k in range(14):
            a = 2 * math.pi * k / 14
            a2 = 2 * math.pi * (k + 1) / 14
            ob = kit.box(f"scarf{ring}-{k}", (1, 1, 1), (0, 0, 0), M["cord"])
            seg_between(ob, (mx + r * math.cos(a), my + r * math.sin(a), z + 0.02 * math.sin(a * 3)),
                        (mx + r * math.cos(a2), my + r * math.sin(a2), z + 0.02 * math.sin(a2 * 3)), 0.05)
            if k % 2 == ring % 2:
                m = knot_mat(kit, f"scarf knot {ring}{k}", "#7a4458", ROSE, rnd.choice((0.6, 1.2, 2.0)))
                kit.box(f"scarfk{ring}-{k}", (0.07, 0.07, 0.07), (mx + (r + 0.03) * math.cos(a), my + (r + 0.03) * math.sin(a), z), m,
                        bevel=0.02)
    kit.cyl("chain medallion", 0.11, 0.025, (mx, my - 0.55, 0.98), M["brass"], rot=(math.pi / 2, 0, 0))
    box(kit, "chain", (0.5, 0.02, 0.025), (mx, my - 0.52, 1.18), M["brass"], rot=(0, 0.55, 0))
    box(kit, "chain2", (0.5, 0.02, 0.025), (mx, my - 0.52, 1.18), M["brass"], rot=(0, -0.55, 0))


# ------------------------------------------------------------------------------------------------ the hill


def cottage(kit, ctx, M, name, cx, door_open):
    t = 0.3
    box(kit, f"{name} L", (2.0, t, 3.0), (cx - 1.5, -t / 2, 1.5), M["white"])
    box(kit, f"{name} R", (2.0, t, 3.0), (cx + 1.5, -t / 2, 1.5), M["white"])
    box(kit, f"{name} lintel", (1.1, t, 0.8), (cx, -t / 2, 2.6), M["white"])
    box(kit, f"{name} sideL", (t, 5.5, 3.0), (cx - 2.35, -2.75, 1.5), M["white"])
    box(kit, f"{name} sideR", (t, 5.5, 3.0), (cx + 2.35, -2.75, 1.5), M["white"])
    box(kit, f"{name} back", (4.7, t, 3.0), (cx, -5.5, 1.5), M["white"])
    box(kit, f"{name} roof", (5.4, 6.3, 0.35), (cx, -2.8, 3.15), M["terra"])
    box(kit, f"{name} floor", (4.4, 5.4, 0.1), (cx, -2.75, 0.05), M["woodA"])
    box(kit, f"{name} step", (1.9, 1.1, 0.12), (cx, 0.6, 0.06), M["stone2"])
    hinge = kit.empty(f"{name} hinge", (cx - 0.55, 0.0, 0.0))
    box(kit, f"{name} door", (1.1, 0.07, 2.2), (0.55, 0, 1.1), M["woodB"], hinge)
    hinge.rotation_euler = (0, 0, math.radians(-100 if door_open else 0))
    ctx[f"{name} hinge"] = hinge
    box(kit, f"{name} win frame", (1.02, 0.06, 1.02), (cx + 1.55, 0.02, 1.55), M["woodB"])
    kit.box(f"{name} pane", (0.88, 0.05, 0.88), (cx + 1.55, 0.06, 1.55), M["pane"])
    return hinge


def build_hill(kit, ctx, M):
    kit.plane("hill flat", (90, Y0 + 14), (HX, (Y0 - 14) / 2, 0), M["grass"])
    p = hill(0, 45)
    kit.plane("hill slope", (90, 100), p, M["grass"], rot=(TH, 0, 0))
    kit.plane("path flat", (1.5, Y0 + 3), (HX, (Y0 + 3) / 2 - 0.0, 0.02), M["path"])
    q = hill(0, 40, 0.02)
    kit.plane("path slope", (1.5, 84), q, M["path"], rot=(TH, 0, 0))
    ctx["hinge_me"] = cottage(kit, ctx, M, "mine", HX, False)
    # my house is built in world coordinates around HX: shift the cottage parts to the hill zone's y = 0 front wall
    cottage(kit, ctx, M, "mum", HX + 16, False)
    rnd = random.Random(21)
    for i in range(190):
        x = rnd.uniform(-14, 14)
        if abs(x) < 1.1:
            continue
        yl = rnd.uniform(2, 50)
        kit.box(f"tuft{i}", (0.03, 0.03, 0.4), hill(x, yl, 0.17), M["tuft1"] if i % 2 else M["tuft2"],
                rot=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(0, 3)))
    for i in range(40):   # a little grass on the flat, away from the houses
        x = rnd.uniform(-14, 14)
        if abs(x) < 3 or 13 < x < 20:
            continue
        kit.box(f"ftuft{i}", (0.03, 0.03, 0.4), (HX + x, rnd.uniform(-1, 11), 0.17), M["tuft1"] if i % 2 else M["tuft2"],
                rot=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(0, 3)))
    # the dome from outside: a stone drum, a verdigris dome with its slit open, one window of warm light
    bx, by, bz = hill(0, DOME_YL)
    kit.cyl("dome pad", 6.2, 1.2, (bx, by, bz - 0.2), M["stone2"], n=32)
    kit.cyl("dome drum", 4.7, 3.6, (bx, by, bz + 1.8), M["stone"], n=32)
    dome_shell(kit, "dome outside", 4.9, bz + 3.6, M["verd_dome"], 0.9, 0.0, loc=(bx, by, 0.0))
    kit.cyl("dome rim", 4.95, 0.22, (bx, by, bz + 3.6), M["brass"], n=40)
    box(kit, "dome win frame", (1.0, 0.1, 1.2), (bx, by - 4.7, bz + 1.9), M["brass"])
    kit.box("dome win", (0.8, 0.1, 1.0), (bx, by - 4.75, bz + 1.9), M["pane"])
    box(kit, "dome door out", (1.1, 0.1, 2.1), (bx + 2.0, by - 4.3, bz + 1.2), M["woodB"], rot=(0, 0, 0.4))
    kit.cyl("dome slit glow", 0.1, 0.1, (bx, by, bz + 8.0), M["pane"])  # a warm light just under the slit
    # the faint grey line from the dome's door down the slope to my front door (plant 1)
    pts = [(2.0, DOME_YL - 4.0), (1.0, 45.0), (1.4, 30.0), (0.6, 14.0), (0.9, 2.0)]
    flat = [(0.9, -1.0), (0.5, 0.7)]
    path = [hill(x, yl, 0.07) for x, yl in pts] + [(HX + x, y, 0.05) for x, y in flat]
    ctx["gline"] = []
    for i in range(len(path) - 1):
        ob = kit.box(f"gline{i}", (1, 1, 1), (0, 0, 0), M["gline"])
        seg_between(ob, path[i], path[i + 1], 0.06)
        ctx["gline"].append(ob)
    # the sky: stars at dusk and night, a warm sky in the memory
    sph = kit.sphere("sky hill", 1.0, (HX, 30, 0), M["sky_hill"], seg=24)
    sph.scale = (350, 350, 350)
    sph.visible_shadow = False
    ctx["sky_hill"] = sph
    # Dad's packed bag, for the two memory shots
    ctx["bag"] = box(kit, "bag", (0.5, 0.26, 0.34), (HX + 0.52, 0.55, 0.19), kit.plastic("#5c4a38", 0.8, name="bag"), bevel=0.05)
    ctx["bag_strap"] = box(kit, "bag strap", (0.52, 0.28, 0.06), (HX + 0.52, 0.55, 0.28), kit.plastic("#2a2420", 0.8, name="bag strap"))


# ------------------------------------------------------------------------------------------------ the dome inside


def D(x, y, z):
    return (CX + x, y, z)


def build_dome(kit, ctx, M):
    R = 4.4
    kit.cyl("dome floor", R + 0.2, 0.1, D(0, 0, -0.05), M["woodA"], n=48)
    n = 28
    door_k = None
    for k in range(n):
        a = 2 * math.pi * k / n
        if abs(math.sin(a) + 1) < 0.02 and abs(math.cos(a)) < 0.35:
            door_k = k
            continue
        w = 2 * math.pi * R / n + 0.05
        box(kit, f"dwall{k}", (w, 0.22, 3.1), D((R + 0.1) * math.cos(a), (R + 0.1) * math.sin(a), 1.55), M["wall"],
            rot=(0, 0, a + math.pi / 2))
    kit.cyl("dome wall cap", R + 0.25, 0.2, D(0, 0, 3.1), M["woodB"], n=48)
    dome_shell(kit, "dome inside", 4.55, 3.1, M["dome_in"], 1.1, -0.2, loc=(CX, 0, 0))
    # the arched plank door in the south wall, closed
    box(kit, "dome door", (1.15, 0.12, 2.0), D(0, -R - 0.02, 1.0), M["woodB"])
    kit.cyl("dome door arch", 0.575, 0.12, D(0, -R - 0.02, 2.0), M["woodB"], rot=(math.pi / 2, 0, 0))
    box(kit, "dome door frame L", (0.12, 0.2, 2.3), D(-0.64, -R - 0.02, 1.15), M["woodB"])
    box(kit, "dome door frame R", (0.12, 0.2, 2.3), D(0.64, -R - 0.02, 1.15), M["woodB"])
    kit.cyl("dome door frame top", 0.7, 0.2, D(0, -R - 0.02, 2.0), M["woodB"], rot=(math.pi / 2, 0, 0), n=24)
    # the pier and the long brass telescope, tilted toward the slit (collar with two scratched strokes)
    px, py = -0.45, 0.3
    kit.cyl("pier base", 0.34, 0.16, D(px, py, 0.08), M["pier"])
    kit.cyl("pier", 0.16, 1.3, D(px, py, 0.7), M["pier"])
    box(kit, "pier head", (0.36, 0.3, 0.2), D(px, py, 1.4), M["pier"], bevel=0.04)
    tube = kit.empty("tube", D(px, py, 1.45))
    tube.rotation_euler = (math.radians(-40), 0, 0)
    kit.cyl("tube body", 0.15, 2.4, (0, 0, 1.0), M["brass"], tube, n=28)
    kit.cyl("tube dew", 0.19, 0.5, (0, 0, 2.05), M["brass"], tube, n=28)
    collar = kit.cyl("tube collar", 0.178, 0.16, (0, 0, 0.55), M["brass"], tube, n=28)
    for dx in (-0.035, 0.035):   # two short verdigris-green strokes scratched into the collar, on its east face
        box(kit, f"tally{dx}", (0.012, 0.012, 0.1), (0.18, dx, 0.55), M["verd"], tube, bevel=0.003)
    # the eyepiece: a short elbow reaching toward the sitter
    ep = kit.empty("eyepiece", D(px, py - 0.12, 1.3))
    kit.cyl("eyepiece tube", 0.04, 0.3, (0, -0.1, 0), M["brass"], ep, rot=(math.pi / 2, 0, 0))
    kit.cyl("eyepiece cap", 0.05, 0.05, (0, -0.27, 0), M["iron"], ep, rot=(math.pi / 2, 0, 0))
    ctx["cap"] = box(kit, "eyepiece cap loose", (0.1, 0.1, 0.05), D(0.0, -0.5, 0.67), M["brass"], bevel=0.02)
    ctx["cap"].hide_render = True
    # two chairs side by side by the eyepiece: Dad's worn (at x -0.45), the second clean (at x 0.75)
    def chair(nm, x, clean):
        y = -0.55
        sm = M["leather"] if clean else kit.plastic("#4a1a1c", 0.7, name="worn leather")
        box(kit, f"{nm} seat", (0.52, 0.52, 0.07), D(x, y, SEAT - 0.035), sm, bevel=0.02)
        box(kit, f"{nm} back", (0.52, 0.06, 0.55), D(x, y - 0.26, SEAT + 0.3), sm, bevel=0.02)
        for sx in (-1, 1):
            for sy in (-1, 1):
                box(kit, f"{nm} leg{sx}{sy}", (0.05, 0.05, SEAT - 0.07), D(x + sx * 0.22, y + sy * 0.22, (SEAT - 0.07) / 2), M["woodB"])
    chair("chair1", -0.45, False)
    chair("chair2", 0.75, True)
    # the dusty stool (three legs), the chart table with pinned charts, the dust on everything but the second chair
    sx0, sy0 = 2.9, 2.6
    box(kit, 'side table top', (0.55, 0.42, 0.04), D(0.28, -0.5, 0.62), M['dust'], bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(kit, f'side leg{sx}{sy}', (0.04, 0.04, 0.6), D(0.28 + sx * 0.23, -0.5 + sy * 0.17, 0.3), M['woodB'])
    kit.cyl("stool top", 0.24, 0.06, D(sx0, sy0, SEAT - 0.03), M["dust"], n=24)
    for i in range(3):
        a = 2 * math.pi * i / 3 + 0.3
        box(kit, f"stool leg{i}", (0.05, 0.05, SEAT - 0.04), D(sx0 + 0.16 * math.cos(a), sy0 + 0.16 * math.sin(a), (SEAT - 0.04) / 2),
            M["woodB"], rot=(0.08 * math.sin(a), -0.08 * math.cos(a), 0))
    tx, ty = -3.85, 0.9
    top = box(kit, "chart table top", (0.9, 1.8, 0.06), D(tx, ty, 1.05), M["dust"], rot=(0, math.radians(-14), 0))
    for sy in (-1, 1):
        box(kit, f"chart table leg{sy}", (0.06, 0.06, 1.05), D(tx + 0.4, ty + sy * 0.8, 0.52), M["woodB"])
        box(kit, f"chart table leg2{sy}", (0.06, 0.06, 1.2), D(tx - 0.4, ty + sy * 0.8, 0.6), M["woodB"])
    for i, (dy, z) in enumerate([(-0.55, 1.08), (0.15, 1.07), (0.85, 1.06)]):
        kit.plane(f"chart on table{i}", (0.5, 0.36), D(tx - 0.02, ty + dy, z + 0.035), M[f"chart{i}"], rot=(0, math.radians(-14), math.pi / 2))
    for i, dy in enumerate((-0.5, 0.7)):
        kit.plane(f"chart on wall{i}", (0.7, 0.5), D(-4.18, ty + dy, 1.9 + 0.1 * i), M[f"chart{(i + 1) % 3}"], rot=(math.pi / 2, 0, math.pi / 2))
    # four warm bulbs in brass cages on the wall, and the one red working lamp low on the pier
    ctx["bulbs"] = []
    for i, a in enumerate((50, 130, 230, 310)):
        ar = math.radians(a)
        bxx, byy = (R - 0.12) * math.cos(ar), (R - 0.12) * math.sin(ar)
        kit.sphere(f"bulb{i}", 0.1, D(bxx, byy, 2.3), M["bulb"], seg=12)
        for cxo, cyo in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            box(kit, f"cage{i}{cxo}{cyo}", (0.014, 0.014, 0.27), D(bxx + cxo * 0.1, byy + cyo * 0.1, 2.3), M["brass"])
        for zz in (2.17, 2.43):
            box(kit, f"cagering{i}{zz}", (0.23, 0.23, 0.012), D(bxx, byy, zz), M["brass"])
        L = kit.light(f"bulb{i}", "POINT", D((R - 0.45) * math.cos(ar), (R - 0.45) * math.sin(ar), 2.3), 140, "#ffcf9a", size=0.2)
        ctx["bulbs"].append(f"bulb{i}")
    kit.sphere("red lens", 0.05, D(px + 0.22, py - 0.1, 0.5), M["redlens"], seg=10)
    kit.light("red", "POINT", D(px + 0.26, py - 0.12, 0.5), 45, "#b84a3e", size=0.08)
    kit.light("red2", "POINT", D(1.3, 0.2, 0.3), 38, "#b04438", size=0.1)
    # a cold starlight rim from the slit, a soft one, so a silhouette keeps an edge
    kit.light("rim", "AREA", D(-0.35, 1.6, 6.4), 380, "#7d9dff", rot=(0, 0, 0), size=2.4)
    kit.light("fill", "POINT", D(0.6, -0.4, 2.6), 30, "#ffd9a8", size=0.5)
    sph = kit.sphere("sky dome sph", 1.0, (CX, 0, 0), M["sky_dome"], seg=24)
    sph.scale = (350, 350, 350)
    sph.visible_shadow = False
    ctx["sky_dome"] = sph


# ------------------------------------------------------------------------------------------------ the creature


def build_keeper(kit, ctx, M):
    """The man with the hole. Root at the feet, facing -y at yaw 0, like the cast."""
    k = {}
    root = kit.empty("keeper", (0, 0, -50))
    k["root"] = root
    hipz = 0.82
    for sx in (-1, 1):
        hinge = kit.empty(f"keeper leg{sx}", (sx * 0.13, 0, hipz), root)
        box(kit, f"kleg{sx}", (0.24, 0.25, 0.72), (0, 0, -0.38), M["ktrou"], hinge, bevel=0.03)
        box(kit, f"kboot{sx}", (0.25, 0.36, 0.12), (0, -0.05, -0.78), M["kboot"], hinge, bevel=0.03)
        box(kit, f"kskirt{sx}", (0.34, 0.4, 0.64), (sx * 0.01, 0, -0.3), M["coat"], hinge, bevel=0.04)
        k[f"leg{sx}"] = hinge
    torso = kit.empty("keeper torso", (0, 0, hipz), root)
    k["torso"] = torso
    th, tw, td = 0.70, 0.64, 0.30
    hz0, hz1 = 0.20, 0.48       # the hole's height range above the hips
    hw = 0.15                   # half the hole's width
    box(kit, "kslabL", (tw / 2 - hw, td, th), (-(tw / 2 + hw) / 2, 0, th / 2), M["coat"], torso, bevel=0.012)
    box(kit, "kslabR", (tw / 2 - hw, td, th), ((tw / 2 + hw) / 2, 0, th / 2), M["coat"], torso, bevel=0.012)
    box(kit, "kslabB", (2 * hw, td, hz0), (0, 0, hz0 / 2), M["coat"], torso, bevel=0.012)
    box(kit, "kslabT", (2 * hw, td, th - hz1), (0, 0, (hz1 + th) / 2), M["coat"], torso, bevel=0.012)
    # the card of stars, mid-depth in the hole
    card = kit.plane("khole", (2 * hw, hz1 - hz0), (0, 0, (hz0 + hz1) / 2), M["hole"], torso, rot=(math.pi / 2, 0, 0))
    card.scale = (1, 1, 1)
    k["streak"] = box(kit, "kstreak", (0.012, 0.012, 0.1), (0, -0.04, 0.35), M["streak"], torso)
    k["streak"].hide_render = True
    # two rows of brass buttons down the slabs, a darker collar, a dark verdigris streak down the coat
    for sx in (-1, 1):
        for i in range(6):
            kit.cyl(f"kbtn{sx}{i}", 0.03, 0.02, (sx * 0.235, -td / 2 - 0.006, 0.07 + i * 0.113), M["brass"], torso, rot=(math.pi / 2, 0, 0), n=12)
        box(kit, f"kcoatstrip{sx}", (0.05, 0.31, th * 0.55), (sx * 0.31, 0, th * 0.45), M["coat_dk"], torso)
    box(kit, "kcollar", (0.34, 0.3, 0.07), (0, 0, th + 0.01), M["coat_dk"], torso, bevel=0.02)
    # arms hung from the shoulders
    for sx in (-1, 1):
        sh = kit.empty(f"keeper arm{sx}", (sx * 0.4, 0, th - 0.06), torso)
        box(kit, f"karm{sx}", (0.17, 0.19, 0.84), (0, 0, -0.42), M["coat"], sh, bevel=0.025)
        box(kit, f"khand{sx}", (0.14, 0.15, 0.2), (0, 0, -0.93), M["kskin"], sh, bevel=0.03)
        k[f"arm{sx}"] = sh
    neck = kit.empty("keeper neck", (0, 0, th + 0.03), torso)
    k["neck"] = neck
    box(kit, "khead", (0.27, 0.26, 0.36), (0, 0, 0.18), M["kskin"], neck, bevel=0.07)
    # two lens-ring eyes, set a little too far apart, one cold highlight each; no mouth, no brows
    for sx in (-1, 1):
        kit.cyl(f"kring{sx}", 0.054, 0.02, (sx * 0.1, -0.135, 0.2), M["lens"], neck, rot=(math.pi / 2, 0, 0), n=24)
        kit.cyl(f"kpupil{sx}", 0.046, 0.024, (sx * 0.1, -0.14, 0.2), M["black"], neck, rot=(math.pi / 2, 0, 0), n=24)
        kit.sphere(f"kglint{sx}", 0.008, (sx * 0.1 + 0.014, -0.156, 0.216), M["glint"], neck, seg=8)
    ctx["keeper"] = k


def pose_keeper(ctx, c, t):
    k = ctx["keeper"]
    root = k["root"]
    if c is None or c.get("hidden", True):
        root.hide_render = True
        for ob in root.children_recursive:
            ob.hide_render = True
        return
    root.hide_render = False
    for ob in root.children_recursive:
        ob.hide_render = False
    k["streak"].hide_render = True
    x, y = c.get("pos", [0, 0])
    sit = c.get("sit", 0.0)
    root.location = (CX + x, y, -0.34 * sit)
    root.rotation_euler = (0, 0, math.radians(c.get("yaw", 0)))
    k["torso"].rotation_euler = (math.radians(c.get("bend", 0)), 0, 0)
    for sx in (-1, 1):
        k[f"leg{sx}"].rotation_euler = (-math.radians(55) * sit, 0, 0)
        k[f"arm{sx}"].rotation_euler = (math.radians(c.get("arm", 3)), 0, sx * math.radians(2))
    hy, hp = c.get("head", [0, 0])
    k["neck"].rotation_euler = (math.radians(hp), 0, math.radians(hy))


# ------------------------------------------------------------------------------------------------ cords and knots


def build_cords(kit, story, ctx, M):
    """Every cast member with a "cord" spec gets a short pale cord and its knots. Everything is placed per frame."""
    ctx["cords"] = {}
    for who, spec in story["cast"].items():
        cs = spec.get("cord")
        if not cs:
            continue
        N = 9
        segs = [kit.box(f"{who}.cseg{i}", (1, 1, 1), (0, 0, 0), M["cord_grey"] if cs.get("grey") else M["cord"]) for i in range(N)]
        tail = []
        if cs.get("loose"):
            tail = [kit.box(f"{who}.ctail{i}", (1, 1, 1), (0, 0, 0), M["cord_grey"]) for i in range(10)]
        knots = []
        for i, st in enumerate(cs.get("knots", [])):
            if cs.get("grey"):
                m = knot_mat(kit, f"knot {who} {i}", "#8a8a86", ROSE, 0.0, rough=0.9)
                size = 0.11
            else:
                dull = st < 0.8
                m = knot_mat(kit, f"knot {who} {i}", "#a07688" if dull else "#ff9ab8", ROSE if not dull else "#c08a9c", st)
                size = 0.1
            ob = kit.box(f"{who}.knot{i}", (size, size, size), (0, 0, 0), m, bevel=size * 0.3)
            knots.append({"ob": ob, "mat": m, "size": size, "base": st})
        ctx["cords"][who] = {"segs": segs, "knots": knots, "tail": tail, "spec": cs, "ph": random.Random(sum(map(ord, who))).uniform(0, 6.28)}
    # the old friends' shared cord: two strands twisted between their heads, drawn in animate
    ctx["twin"] = {"a": [kit.box(f"twin.a{i}", (1, 1, 1), (0, 0, 0), M["cord"]) for i in range(14)],
                   "b": [kit.box(f"twin.b{i}", (1, 1, 1), (0, 0, 0), M["cord"]) for i in range(14)],
                   "knots": [knot_mat(kit, f"twin knot {i}", "#ff9ab8", ROSE, 1.6) for i in range(2)]}
    ctx["twin"]["kobs"] = [kit.box(f"twin.knot{i}", (0.07, 0.07, 0.07), (0, 0, 0), m, bevel=0.02) for i, m in enumerate(ctx["twin"]["knots"])]
    # a rose puff for a kept promise: a soft bloom and a ring of sparks
    pm = M["puff"]
    ctx["puff"] = [kit.sphere("puff core", 0.12, (0, 0, -90), pm, seg=10)] + \
                  [kit.sphere(f"puff{i}", 0.035, (0, 0, -90), pm, seg=6) for i in range(10)]
    # my own cord waits unseen: a rose knot ties in at the end
    # Dad's loose end: a long thread that runs down to the floor and across to the second chair


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    ctx = {"story": story, "shots": {s["id"]: s for s in story["shots"]}}
    wd = workdir(tl)
    M = materials(kit, wd)
    ctx["M"] = M
    build_square(kit, ctx, M)
    build_hill(kit, ctx, M)
    build_dome(kit, ctx, M)
    build_keeper(kit, ctx, M)
    build_cords(kit, story, ctx, M)
    # lights: the sun by scene, a dusk sun, a moon, the house windows, the dome's own
    sun = kit.light("sun_day", "SUN", (0, 0, 20), 3.6, "#fff0d4", rot=(math.radians(52), 0, math.radians(30)))
    sun.data.angle = math.radians(2.0)
    sd = kit.light("sun_dusk", "SUN", (0, 0, 20), 2.0, "#ff9a68", rot=(math.radians(76), 0, math.radians(200)))
    sd.data.angle = math.radians(3.0)
    sm = kit.light("sun_mem", "SUN", (0, 0, 20), 2.6, "#ffcf8a", rot=(math.radians(68), 0, math.radians(-18)))
    sm.data.angle = math.radians(3.0)
    mo = kit.light("moon", "SUN", (0, 0, 20), 0.9, "#7f9cff", rot=(math.radians(58), 0, math.radians(160)))
    mo.data.angle = math.radians(1.0)
    kit.light("mine window", "POINT", (HX + 1.55, 1.2, 1.6), 55, "#ffb470", size=0.3)
    kit.light("mine lamp", "POINT", (HX, -1.6, 2.2), 90, "#ffb86a", size=0.3)
    kit.light("mum window", "POINT", (HX + 17.55, 1.2, 1.6), 40, "#ffb470", size=0.3)
    bx, by, bz = hill(0, DOME_YL)
    kit.light("dome window", "POINT", (bx, by - 5.6, bz + 2.2), 120, "#ffb470", size=0.3)
    kit.light("hill dusk fill", "POINT", (HX, -10, 6), 300, "#ffa070", size=1.0)
    kit.light("hill night fill", "POINT", (HX, -10, 8), 500, "#6f86d8", size=1.0)
    # the fog's colour per scene: remember every fog node the kit made
    ctx["fog_nodes"] = []
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        for n in m.node_tree.nodes:
            if n.type == "EMISSION" and n.outputs[0].links:
                lk = n.outputs[0].links[0]
                if lk.to_node.type == "MIX_SHADER" and lk.to_socket == lk.to_node.inputs[2]:
                    ctx["fog_nodes"].append(n)
    ctx["scene_now"] = None
    ctx["hair"] = {}
    return ctx


# ------------------------------------------------------------------------------------------------ animate

SCENES = {
    #           world,       horizon,   zenith,     fog,        exposure
    "day":    ("#8ec9f0", 1.25, "#bfe0f5", "#6fb0e8", "#b9d6ea", 0.0),
    "memory": ("#e0c38a", 0.9, "#f0cf9a", "#c89868", "#c8a878", -0.1),
    "dusk":   ("#b0707a", 0.7, "#e08a6e", "#4a4a78", "#7a5a6c", -0.2),
    "night":  ("#0f1a33", 0.5, "#16224a", "#070c1c", "#0d1528", 0.2),
    "dome":   ("#1a2a50", 0.4, "#0b1226", "#0b1226", "#06080f", 0.95),
}
LIGHT_SCENES = {
    "sun_day": {"day": 1.0}, "sun_dusk": {"dusk": 1.0}, "sun_mem": {"memory": 1.0}, "moon": {"night": 1.0},
    "mine window": {"dusk": 1.0, "night": 1.0, "memory": 0.4}, "mine lamp": {"memory": 0.8, "dusk": 0.4, "night": 0.4},
    "mum window": {"dusk": 1.0, "night": 1.0}, "dome window": {"dusk": 1.0, "night": 1.0},
    "hill dusk fill": {"dusk": 0.5}, "hill night fill": {"night": 0.35},
}


def _world(sc, kit):
    w, ws, hor, zen, fog, exp = SCENES[sc]
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = kit.col(w)
    bg.inputs["Strength"].default_value = ws
    bpy.context.scene.view_settings.exposure = exp


def animate(kit, story, tl, t, ctx):
    from blocky import bl_story, timeline

    bpy.context.view_layer.update()
    shot = timeline.shot_at(tl, t)
    spec = ctx["shots"][shot["id"]]
    sc = spec["scene"]
    M = ctx["M"]
    if ctx["scene_now"] != sc:
        _world(sc, kit)
        fogc = kit.col(SCENES[sc][4])
        for n in ctx["fog_nodes"]:
            n.inputs["Color"].default_value = fogc
        ctx["scene_now"] = sc
    # the skies: the hill's by scene, the dome's by the cloud cues
    hor, zen = SCENES[sc][2], SCENES[sc][3]
    stars_on = 1.0 if sc == "night" else 0.0
    if sc != "dome":
        sm = M["sky_hill"]
        set_rgb(sm, "bgh", hor, kit)
        set_rgb(sm, "bgz", zen, kit)
        sm.node_tree.nodes["stars"].outputs[0].default_value = stars_on
    cl = _cues(tl, "cloud")
    amt = _eased(cl, "amount", t, 0.0)
    pink = _eased(cl, "pink", t, 0.0)
    dm = M["sky_dome"]
    base = V(kit.col("#0b1226")[:3])
    cloud = V(kit.col("#4a4f58")[:3])
    dawn = V(kit.col("#e9a3a8")[:3])
    h = base.lerp(cloud, amt).lerp(dawn, pink)
    z_ = base.lerp(V(kit.col("#3e434c")[:3]), amt).lerp(V(kit.col("#c8b4c4")[:3]), pink)
    dm.node_tree.nodes["bgh"].outputs[0].default_value = (h.x, h.y, h.z, 1)
    dm.node_tree.nodes["bgz"].outputs[0].default_value = (z_.x, z_.y, z_.z, 1)
    dm.node_tree.nodes["stars"].outputs[0].default_value = max(0.0, 1.0 - amt * 1.2)
    # sitting legs, and the cast's hair
    for who, keys in tl.get("acting", {}).items():
        sit = False
        for kk in keys:
            if "sit" in kk and kk["t"] <= t + 1e-9:
                sit = kk["sit"]
        if sit:
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (math.radians(-90), 0, 0)
    hc = {}
    for c in _cues(tl, "hair"):
        if c["t"] <= t + 1e-9:
            hc[c["who"]] = c["color"]
    for who, hexc in hc.items():
        cs_ = story["cast"][who]
        m = kit.MATS.get(f"plastic {cs_['hair_c']} 0.65")
        if m is not None:
            m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = kit.col(hexc)
    # the creature
    kc = _last(_cues(tl, "keeper"), t)
    pose_keeper(ctx, kc, t)
    stk = _last(_cues(tl, "streak"), t)
    k = ctx["keeper"]
    if stk is not None and not k["root"].hide_render:
        u = (t - stk["t"]) / max(0.2, stk.get("dur", 1.6))
        if 0 <= u <= 1:
            k["streak"].hide_render = False
            k["streak"].location = (-0.1 + 0.2 * u, -0.045, 0.45 - 0.2 * u)
            k["streak"].rotation_euler = (0, math.radians(40), 0)
            M["streak"].node_tree.nodes["E"].inputs["Strength"].default_value = 9.0 * math.sin(math.pi * u) ** 0.6
    # the dome's lights: bulbs ease; the red lamp is always on (low) in the dome
    bulbs = _eased(_cues(tl, "dome"), "bulbs", t, 1.0)
    M["bulb"].node_tree.nodes["E"].inputs["Strength"].default_value = 0.6 + 5.4 * bulbs
    gains = {}
    for nm, d in LIGHT_SCENES.items():
        gains[nm] = d.get(sc, 0.0)
    for i in range(4):
        gains[f"bulb{i}"] = (bulbs * 0.6 + 0.03) if sc == "dome" else 0.0
    gains["red"] = (1.0 + 1.2 * (1.0 - bulbs)) if sc == "dome" else 0.0
    gains["red2"] = (1.0 + 1.4 * (1.0 - bulbs)) if sc == "dome" else 0.0
    kit.LIGHTS["rim"]["light"].color = tuple(V((0.49, 0.62, 1.0)).lerp(V((1.0, 0.7, 0.72)), pink))
    gains["rim"] = (0.55 + 1.1 * (1.0 - bulbs)) if sc == "dome" else 0.0
    gains["fill"] = (0.5 * bulbs) if sc == "dome" else 0.0
    # shooting stars (rare) over the slit
    # the doors, the bag
    ctx["mine hinge"].rotation_euler = (0, 0, math.radians(-100 if sc == "memory" else 0))
    ctx["bag"].hide_render = sc != "memory"
    ctx["bag_strap"].hide_render = sc != "memory"
    for o in ctx["gline"]:
        o.hide_render = sc not in ("night", "dusk")
    ctx["umbrella"].hide_render = False
    # the eyepiece cap slides across the little table between the chairs and stops in front of me (S74)
    cc = _last(_cues(tl, "cap"), t)
    ctx["cap"].hide_render = cc is None
    if cc is not None:
        u = _ss((t - cc["t"]) / 0.9)
        ctx["cap"].location = D(0.02 + 0.4 * u, -0.5, 0.67)
    # the cords: face the camera, bob, and knots by cue
    loc, tgt, lens, roll = bl_story.cam_at(spec, shot, t, None, tl)
    cam = V(loc)
    place_cords(kit, tl, ctx, t, cam, M)
    return gains


def _head_top(who):
    hm = bpy.data.objects.get(f"{who}.headm")
    root = bpy.data.objects.get(who)
    if hm is None or root is None or root.hide_render:
        return None
    return hm.matrix_world.translation.copy() + V((0, 0, 0.38))


def knot_val(tl, who, i, key, t, default):
    cs = [c for c in _cues(tl, "knot") if c["who"] == who and c.get("i", 0) == i]
    return _eased(cs, key, t, default)


def place_cords(kit, tl, ctx, t, cam, M):
    ph_t = 2 * math.pi * 0.4 * t
    for who, c in ctx["cords"].items():
        top = _head_top(who)
        spec = c["spec"]
        hide = top is None
        # a character with no cord until a cue ties one (me, at the end)
        if spec.get("late") and not hide:
            sc = knot_val(tl, who, 0, "scale", t, 0.0)
            hide = sc <= 0.001
        for o in c["segs"] + [k["ob"] for k in c["knots"]] + c["tail"]:
            o.hide_render = hide
        if hide:
            continue
        flat = V((top.x - cam.x, top.y - cam.y, 0.0))
        if flat.length < 1e-4:
            flat = V((0, -1, 0))
        flat.normalize()
        r = V((flat.y, -flat.x, 0.0))      # camera-right, horizontal
        cs = [x for x in _cues(tl, "cordset") if x["who"] == who]
        L = _eased(cs, "len", t, spec.get("len", 0.34))
        stand = _eased(cs, "stand", t, 0.0)
        N = len(c["segs"])
        bob = 0.025 * math.sin(ph_t + c["ph"])
        pts = []
        for i in range(N + 1):
            u = i / N
            arc = top + r * ((u - 0.5) * L) + V((0, 0, 0.05 * math.sin(2 * math.pi * 0.85 * u + c["ph"]) + bob + 0.025 * (1 - (2 * u - 1) ** 2)))
            up = top + V((0, 0, 0.0 + u * L * 0.95 + bob * 0.3))
            pts.append(arc.lerp(up, stand))
        for i, ob in enumerate(c["segs"]):
            seg_between(ob, pts[i], pts[i + 1], 0.028)
        nk = len(c["knots"])
        for i, kn in enumerate(c["knots"]):
            u = (i + 1) / (nk + 1) if not spec.get("grey") else 0.5
            f = u * N
            a = int(min(N - 1, f))
            p = pts[a].lerp(pts[a + 1], f - a)
            sc = knot_val(tl, who, i, "scale", t, 0.0 if spec.get("late") else 1.0)
            kn["ob"].location = p + V((0, 0, -0.012))
            kn["ob"].scale = (max(sc, 0.001),) * 3
            kn["ob"].hide_render = sc <= 0.002
            g = knot_val(tl, who, i, "glow", t, kn["base"])
            set_emit(kn["mat"], g)
        # Dad's loose end: from the cord's near end down to the floor and across to the second chair
        if c["tail"]:
            p0 = pts[0]
            fl = V(D(0.2, -0.3, 0.03))
            tail_pts = [p0, p0 + r * -0.12 + V((0, 0, -0.28)), V((p0.x, p0.y, 0.05)) + r * -0.25, fl + V((-1.0, -0.1, 0)),
                        fl + V((-0.5, -0.15, 0.0)), fl + V((0.15, 0.0, 0.0))]
            # smooth: interpolate between the listed points
            M_ = len(c["tail"])
            for i, ob in enumerate(c["tail"]):
                a = i / M_
                b = (i + 1) / M_
                seg_between(ob, _poly(tail_pts, a), _poly(tail_pts, b), 0.016)
    # the old friends: two strands twisted between their heads, three knots along them
    ta, tb = _head_top("friend1"), _head_top("friend2")
    tw = ctx["twin"]
    show = ta is not None and tb is not None
    for o in tw["a"] + tw["b"] + tw["kobs"]:
        o.hide_render = not show
    if show:
        n = len(tw["a"])
        prev = {}
        for i in range(n + 1):
            u = i / n
            base = ta.lerp(tb, u) + V((0, 0, 0.06 * math.sin(math.pi * u) + 0.03 * math.sin(ph_t)))
            tw_ = math.sin(u * 22.0 + ph_t * 0.3) * 0.028 * math.sin(math.pi * u)
            tz = math.cos(u * 22.0 + ph_t * 0.3) * 0.028 * math.sin(math.pi * u)
            dirv = (tb - ta).normalized()
            side = V((-dirv.y, dirv.x, 0))
            for nm, sg in (("a", 1), ("b", -1)):
                p = base + side * tw_ * sg + V((0, 0, tz * sg))
                if nm in prev:
                    seg_between(tw["a" if nm == "a" else "b"][i - 1], prev[nm], p, 0.018)
                prev[nm] = p
        for i, ob in enumerate(tw["kobs"]):
            u = 0.4 + 0.2 * i
            ob.location = ta.lerp(tb, u) + V((0, 0, 0.06 * math.sin(math.pi * u) + 0.03 * math.sin(ph_t)))
    # the puffs
    pu = _last(_cues(tl, "puff"), t)
    for o in ctx["puff"]:
        o.hide_render = True
    if pu is not None:
        u = (t - pu["t"]) / pu.get("dur", 1.2)
        if 0 <= u <= 1:
            top = _head_top(pu["who"])
            if top is not None:
                p = top + V((0, 0, 0.0))
                M["puff"].node_tree.nodes["E"].inputs["Strength"].default_value = 1.4 * math.sin(math.pi * u) ** 1.2
                core = ctx["puff"][0]
                core.hide_render = False
                core.location = p
                core.scale = (0.6 + 2.2 * _ss(u),) * 3
                for i, sp in enumerate(ctx["puff"][1:]):
                    a = 2 * math.pi * i / 10
                    rad = 0.1 + 0.32 * _ss(u)
                    sp.hide_render = False
                    sp.location = p + V((rad * math.cos(a) * 0.9, rad * math.sin(a) * 0.9, rad * 0.5 * math.sin(a * 2) + 0.12 * u))
                    sp.scale = (max(0.05, 1 - u * 0.9),) * 3


def _poly(pts, u):
    f = max(0.0, min(0.9999, u)) * (len(pts) - 1)
    a = int(f)
    return pts[a].lerp(pts[a + 1], f - a)
