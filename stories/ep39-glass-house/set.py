"""The Glass House: a dry-summer terraced street where everyone wears a small cloud, a kitchen, a cinema's front row,
and our back garden with the glasshouse at the end of it, where the Long Neck comes nearer each night.

Four places far apart in x (each is its own little world, lit on its own; `animate` switches the lights, the sky and
what is drawn by the shot's room):
  street   x -40 .. 40    the road along x (y -9 .. -1.6), the pavement, gardens and house fronts (y 1.2 .. 10)
                          me at the sage gate x 0, Mr Pell at the cream gate x 4, the cafe at x -22, the wedding at x 22
  kitchen  x 100 + (-3 .. 3), y 0 .. 4: the sink and window on the back wall (y 4), the table, the hook board
  garden   x 200 + ...    the house's back wall at y 0, the stone path to the glasshouse (y 16 .. 22, x -2.3 .. 2.3), the
                          far hedge at y 26, Mr Pell's side over the west hedge (x -5.5)
  cinema   x 300 + (-4 .. 4), y 0 .. 9: the front row at y 3, the screen behind the camera
Characters face -y at yaw 0, +x at yaw 90.

THE CREATURE is the Long Neck: an R6-sized body in moss and terracotta, a neck of eight stacked blocks (each about
0.26 m square, posed as a stepped column and never a smooth tube), and a moss head with two small close eyes and a
cracked-pot mouth. Built once (`build_creature`), posed by the "neck" cue.

Cues read here (set.py's animate; everything else is the engine's):
- tod: {"mode": "day|dusk|night|morning", "dur": s}   the garden's light (ramps)
- lamps: {"to": 0..1, "dur": s}   the glasshouse's hanging lamps (always a ramp of 0.3 s or more)
- neck: {"on": bool, "body": [x, y], "yaw": deg, "pts": [[x, y, z], ...], "look": [x, y, z], "up": [x, y, z]?}
- vent / door: {"to": 0..1, "dur": s}   the roof vent opening, the glasshouse door opening
- plants: {"to": 0..1, "dur": s}   0 green and standing, 1 brown and drooping
- rustle: {"on": bool}   the dry leaves on the potting table
- cloud: {"who", "gap": m (head top to cloud's underside), "dur"}  {"who", "size": k, "dur"}  {"who", "tone": 0..1, "dur"}
  {"who", "rain": 0..1, "dur"}  {"who", "on": bool}
- umbrella: {"who", "on": bool}
- pour: {"on": bool}   the tipped pot over the sugar bowl
Acting keys read here: "sit": true bends both legs forward.
"""

from __future__ import annotations

import math

import bpy
import numpy as np
from mathutils import Matrix, Vector as V
from PIL import Image, ImageDraw, ImageFilter

from blocky import acting as ac
from blocky import faces, rig

GX, KX, CX = 200.0, 100.0, 300.0
S = rig.S
THETA = math.atan2(1.4, 2.3)          # the glasshouse roof pitch
EAVE, RIDGE = 1.7, 3.1
GH_Y0, GH_Y1 = 16.0, 22.0
SCENE_OF_SHOT = {}


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return sorted((c for c in tl.get("cues", []) if c["name"] == name), key=lambda c: c["t"])


def _switch(cs, attr, t, default):
    v = default
    for c in cs:
        if attr in c and c["t"] <= t + 1e-9:
            v = c[attr]
    return v


def _level(cs, key, t, default):
    """A value that ramps from cue to cue: each cue sets `key` and gets there over its dur."""
    v0 = v = default
    for c in cs:
        if key not in c:
            continue
        if c["t"] > t + 1e-9:
            break
        d = max(1e-6, c.get("dur", 0.3))
        v0, v = v, c[key]
        if t < c["t"] + d:
            return v0 + (v - v0) * _ss((t - c["t"]) / d)
    return v


def _who(tl, name, who):
    return sorted((c for c in tl.get("cues", []) if c["name"] == name and c.get("who") == who), key=lambda c: c["t"])


def wbox(kit, name, lo, hi, mat, parent=None):
    c = tuple((a + b) / 2 for a, b in zip(lo, hi))
    s = tuple(b - a for a, b in zip(lo, hi))
    return kit.mesh_obj(name, kit.box_verts(*s, c), kit.BOX_FACES, mat, parent)


def bbox(kit, name, lo, hi, mat, bevel=0.03, parent=None):
    c = tuple((a + b) / 2 for a, b in zip(lo, hi))
    s = tuple(b - a for a, b in zip(lo, hi))
    return kit.box(name, s, c, mat, parent, bevel=bevel)


def rod(kit, name, p1, p2, w, mat, parent=None):
    a, b = V(p1), V(p2)
    d = b - a
    up = "Y" if abs(d.normalized().y) < 0.9 else "X"
    ob = kit.box(name, (w, w, d.length), tuple((a + b) / 2), mat, parent)
    ob.rotation_euler = d.to_track_quat("Z", up).to_euler()
    return ob


def prism_roof(kit, name, x0, x1, y0, y1, z0, z1, mat):
    """A pitched roof along x: eaves at y0 and y1 (height z0), ridge at the middle (z1)."""
    ym = (y0 + y1) / 2
    v = [(x0, y0, z0), (x1, y0, z0), (x1, ym, z1), (x0, ym, z1), (x0, y1, z0), (x1, y1, z0), (x1, ym, z1), (x0, ym, z1)]
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, ym, z1), (x1, ym, z1)]
    f = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]
    return kit.mesh_obj(name, v, f, mat)


def pil_mat(kit, name, pil, rough=0.7, emit=0.0):
    img = bpy.data.images.new(name, pil.width, pil.height, alpha=False)
    a = np.asarray(pil.convert("RGBA")).astype(np.float32)[::-1] / 255
    img.pixels.foreach_set(a.ravel())
    img.pack()
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = img
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    if emit:
        nt.links.new(tx.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    kit._fogged(m, b.outputs[0])
    return m


def img_quad(kit, name, w, h, mat, loc, rot=(0, 0, 0), parent=None):
    """A flat picture facing -y (its front), w by h metres, centred on loc."""
    v = [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)]
    ob = kit.mesh_obj(name, v, [(0, 1, 2, 3)], mat, parent, loc, rot)
    uv = ob.data.uv_layers.new(name="UVMap")
    uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for p in ob.data.polygons:
        for li in p.loop_indices:
            uv.data[li].uv = uvs[ob.data.loops[li].vertex_index]
    return ob


def lou_photo():
    im = Image.new("RGB", (300, 380), (236, 220, 190))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 250, 300, 380], fill=(120, 170, 190))              # sea behind
    d.rectangle([0, 0, 300, 250], fill=(196, 222, 232))
    d.polygon([(50, 380), (250, 380), (230, 280), (70, 280)], fill=(232, 116, 88))   # coral shirt
    d.rectangle([128, 240, 172, 290], fill=(226, 172, 134))                 # neck
    d.ellipse([85, 120, 215, 262], fill=(232, 182, 142))                    # face
    d.ellipse([20, 118, 280, 168], fill=(220, 184, 104))                    # hat brim
    d.rectangle([92, 52, 208, 140], fill=(226, 190, 112))                   # crown
    d.rectangle([92, 112, 208, 130], fill=(190, 96, 70))
    for sx in (-1, 1):
        d.ellipse([150 + sx * 34 - 9, 188, 150 + sx * 34 + 9, 210], fill=(30, 24, 26))
    d.chord([112, 205, 188, 255], 10, 170, fill=(255, 250, 244), outline=(40, 24, 26), width=5)   # a big grin
    return im


def sea_card():
    im = Image.new("RGB", (360, 240), (246, 242, 230))
    d = ImageDraw.Draw(im)
    d.rectangle([14, 14, 346, 226], fill=(184, 214, 232))
    d.rectangle([14, 120, 346, 226], fill=(52, 108, 156))
    for k in range(6):
        y = 130 + k * 16
        for x in range(20, 340, 46):
            d.arc([x + (k % 2) * 20, y, x + 30 + (k % 2) * 20, y + 10], 200, 340, fill=(150, 196, 226), width=2)
    return im


# ------------------------------------------------------------------------------------------------ materials


def glass_mat(kit, name, tint="#d6e6ec", refl=0.07, milky=0.0):
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    tr = N.new("ShaderNodeBsdfTransparent")
    gl = N.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.1
    gl.inputs["Color"].default_value = kit.col(tint)
    mix = N.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = refl
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(gl.outputs[0], mix.inputs[2])
    out = mix.outputs[0]
    if milky:
        df = N.new("ShaderNodeBsdfDiffuse")
        df.inputs["Color"].default_value = kit.col("#d9e0da")
        m2 = N.new("ShaderNodeMixShader")
        m2.inputs[0].default_value = milky
        L.new(out, m2.inputs[1])
        L.new(df.outputs[0], m2.inputs[2])
        out = m2.outputs[0]
    kit._fogged(m, out)
    return m


def glow_mat(kit, name, hexc, strength):
    m = kit.emit(hexc, strength, name)
    return m


def soft_mat(kit, name, hexc, emit_hex=None, emit=0.0, rough=0.9):
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = kit.col(emit_hex or hexc)
        b.inputs["Emission Strength"].default_value = emit
    kit._fogged(m, b.outputs[0])
    return m


def materials(kit):
    P = kit.plastic
    M = {
        "brick": kit.bricks("#8a4a36", "#74402f", "#5a4e46", 1.0),
        "brick2": kit.bricks("#9a6a4c", "#865a40", "#5a4e46", 1.0),
        "brick_pale": kit.bricks("#a35a40", "#8a4a36", "#6a5e56", 1.0),
        "slate": kit.planks("#4a4e58", "#3a3e48", 2.0, "X"),
        "tiles": kit.planks("#9a4a34", "#7a3a2a", 2.0, "X"),
        "road": kit.concrete("#4a4a50", 2.0, 0.35),
        "pave": kit.concrete("#a8a398", 1.2, 0.35),
        "kerb": kit.concrete("#b4afa4", 3.0, 0.2),
        "straw": kit.grime("#c9b27a", 0.7, 5.0, rough=0.95),
        "green": kit.grime("#3fa536", 0.8, 5.0, rough=0.9),
        "dirt": kit.concrete("#9a8a66", 2.0, 0.3),
        "hedge": kit.grime("#2f4a2a", 0.45, 12.0, rough=0.97),
        "hedge_n": kit.grime("#1f3320", 0.45, 12.0, rough=0.97),
        "flag": kit.concrete("#8f8b82", 2.0, 0.35),
        "wood": kit.planks("#8a6a46", "#6a4c30", 1.0, "X"),
        "wood_dk": kit.planks("#5a4028", "#3e2a18", 1.0, "X"),
        "floor": kit.planks("#a5825a", "#876440", 1.0, "X"),
        "paint_w": P("#e8e4da", 0.55),
        "paint_c": P("#e6dcc0", 0.7),
        "sage": P("#9fb59a", 0.6),
        "plum": P("#6d4568", 0.6),
        "teal": P("#3f7f86", 0.6),
        "wallcream": kit.grime("#e2d6b8", 0.8, 3.0, rough=0.9),
        "wallblue": kit.grime("#8aa3b4", 0.8, 3.0, rough=0.9),
        "terra": P("#c8643c", 0.6),
        "moss": P("#4d6b34", 0.6),
        "mossd": P("#3c5528", 0.6),
        "iron": kit.metal("#2a2b2e", 0.5),
        "brass": kit.metal("#b08a40", 0.4),
        "steel": kit.metal("#9a9ea2", 0.35),
        "black": P("#141214", 0.6),
        "dark": P("#26282e", 0.7),
        "white": P("#f2f0ea", 0.5),
        "cream": P("#efe6cc", 0.5),
        "mug": P("#d8d2c4", 0.35),
        "mugb": P("#3a4a6a", 0.4),
        "tea": P("#6a3c1c", 0.2),
        "wicker": kit.planks("#b88a55", "#9a6e40", 3.0, "Y"),
        "pot": P("#c8643c", 0.8),
        "soil": P("#3a2a1c", 0.95),
        "blanket": P("#e6dcc0", 0.95),
        "leaf_dry": P("#8a6a3a", 0.9),
        "red": P("#8a2a2e", 0.8),
        "carpet": kit.grime("#5a1f2a", 0.6, 4.0, rough=0.95),
        "seat": P("#7a2a34", 0.75),
        "umb1": P("#33415f", 0.7), "umb2": P("#5a3a4a", 0.7), "umb3": P("#2f5a52", 0.7), "umb4": P("#8a5a2a", 0.7),
        "awn_a": P("#c8472f", 0.8), "awn_b": P("#efe6cc", 0.8),
        "flag_r": P("#d65a4a", 0.8), "flag_y": P("#e6c04a", 0.8), "flag_b": P("#4a86c8", 0.8), "flag_g": P("#58a85c", 0.8),
        "string": P("#c8c0b0", 0.9),
        "wrap": glass_mat(kit, "wrapper", "#e8f0f4", 0.12, 0.0),
        "band": P("#3a62b8", 0.6),
        "umb_furl": P("#2a2e3c", 0.7),
        "patch": P("#6a5a48", 0.9),
        "glass": glass_mat(kit, "glass_clear", "#d6e6ec", 0.06),
        "glass_old": glass_mat(kit, "glass_old", "#cfdcd4", 0.1, 0.22),
        "skyglow": kit.emit("#cfe3f4", 2.4, "skyglow"),
        "screen": kit.emit("#4a78c8", 1.0, "screen"),
        "lampw": kit.emit("#ffbe78", 3.0, "lampw"),
        "porch": kit.emit("#ffc886", 6.0, "porch"),
        "winwarm": kit.emit("#ffbe78", 2.2, "winwarm"),
        "star": kit.emit("#dfe8ff", 6.0, "star"),
        "drop": kit.emit("#a8c4e4", 0.9, "drop"),
        "cloud_dk": soft_mat(kit, "cloud_dark", "#6e7681", "#6e7681", 0.12),
    }
    return M


# ------------------------------------------------------------------------------------------------ the street


def build_street(kit, ctx, M):
    wbox(kit, "road", (-45, -10.5, -0.2), (45, -1.6, -0.1), M["road"])
    wbox(kit, "pave", (-45, -1.6, -0.1), (45, 1.2, 0.0), M["pave"])
    wbox(kit, "kerb", (-45, -1.75, -0.1), (45, -1.6, 0.06), M["kerb"])
    # a line of garden plots, 4 m each, house centres every 4 m from -40 to 40; the plum (-4), sage (0), cream (4)
    paints = {0: "sage", 4: "paint_c", -4: "plum", 8: "teal", -8: "paint_w"}
    for hx in range(-40, 41, 4):
        green = hx == 4
        lawn = M["green"] if green else M["straw"]
        wbox(kit, f"lawn{hx}", (hx - 1.9, 1.2, -0.02), (hx + 1.9, 4.4, 0.04), lawn)
        pc = M[paints.get(hx, ["paint_c", "plum", "sage", "teal", "paint_w"][(hx // 4) % 5])]
        # house front
        bm = M["brick"] if (hx // 4) % 2 == 0 else M["brick2"]
        wbox(kit, f"house{hx}", (hx - 2.0, 4.4, 0.0), (hx + 2.0, 11.0, 5.8), bm)
        prism_roof(kit, f"roof{hx}", hx - 2.05, hx + 2.05, 4.1, 11.3, 5.8, 7.6, M["slate"])
        bbox(kit, f"door{hx}", (hx - 0.5, 4.36, 0.0), (hx + 0.5, 4.44, 2.1), pc, 0.02)
        bbox(kit, f"step{hx}", (hx - 0.7, 4.1, 0.0), (hx + 0.7, 4.4, 0.15), M["kerb"], 0.02)
        for wx in (-1.35, 1.35):
            for z0 in (0.9, 3.4):
                bbox(kit, f"win{hx}_{wx}_{z0}", (hx + wx - 0.4, 4.37, z0), (hx + wx + 0.4, 4.43, z0 + 1.1), M["glass_old"], 0.0)
                bbox(kit, f"winf{hx}_{wx}_{z0}", (hx + wx - 0.46, 4.34, z0 - 0.06), (hx + wx + 0.46, 4.4, z0 + 1.16), M["paint_w"], 0.01)
        # low wall along the pavement with a gate gap, painted gate
        wbox(kit, f"fw{hx}a", (hx - 1.95, 1.2, 0.0), (hx - 0.45, 1.34, 0.5), bm)
        wbox(kit, f"fw{hx}b", (hx + 0.45, 1.2, 0.0), (hx + 1.95, 1.34, 0.5), bm)
        bbox(kit, f"gate{hx}", (hx - 0.43, 1.2, 0.05), (hx + 0.43, 1.28, 0.95), pc, 0.02)
        wbox(kit, f"sw{hx}", (hx + 1.95, 1.2, 0.0), (hx + 2.05, 4.4, 0.55), bm)
    # the far side of the road: a plain wall and a lamp post (the wedding's bunting hangs from it)
    wbox(kit, "farwall", (-45, -10.6, -0.2), (45, -10.4, 1.2), M["brick2"])
    for px in (14.0, 30.0):
        rod(kit, f"post{px}", (px, -1.2, 0.0), (px, -1.2, 4.6), 0.12, M["iron"])
        kit.sphere(f"lamp{px}", 0.16, (px, -1.2, 4.7), M["white"])
    # the cafe (x -22): a shopfront on house 20 and 24's wall, a striped awning, a table under it
    cx = -22.0
    wbox(kit, "cafe_front", (cx - 3.6, 4.3, 0.0), (cx + 3.6, 4.45, 3.4), M["paint_w"])
    bbox(kit, "cafe_win", (cx - 3.2, 4.25, 0.5), (cx - 0.5, 4.3, 2.6), M["winwarm"], 0.0)
    bbox(kit, "cafe_win2", (cx + 0.5, 4.25, 0.5), (cx + 3.2, 4.3, 2.6), M["winwarm"], 0.0)
    bbox(kit, "cafe_door", (cx - 0.4, 4.25, 0.0), (cx + 0.4, 4.3, 2.1), M["terra"], 0.01)
    for k in range(12):
        x0 = cx - 3.6 + k * 0.6
        a = ob = kit.box(f"awn{k}", (0.6, 3.4, 0.05), (x0 + 0.3, 2.8, 2.95), M["awn_a" if k % 2 == 0 else "awn_b"])
        a.rotation_euler = (math.radians(-8), 0, 0)
        kit.box(f"awnv{k}", (0.6, 0.05, 0.28), (x0 + 0.3, 1.1, 2.62), M["awn_a" if k % 2 == 0 else "awn_b"])
    for sx in (-3.5, 3.5):
        rod(kit, f"awnpost{sx}", (cx + sx, 1.15, 0.0), (cx + sx, 1.15, 2.6), 0.07, M["iron"])
    ctx["cafe"] = (cx, 2.6)
    kit.cyl("cafe_tab", 0.45, 0.04, (cx, 2.6, 0.75), M["white"], n=24)
    kit.cyl("cafe_leg", 0.05, 0.75, (cx, 2.6, 0.375), M["iron"], n=10)
    for sx in (-0.18, 0.18):
        kit.cyl(f"cup{sx}", 0.065, 0.08, (cx + sx, 2.6 + (0.04 if sx > 0 else -0.04), 0.81), M["mug"], n=14)
    for sx, yw in ((-0.85, 90), (0.85, -90)):
        bbox(kit, f"cafe_seat{sx}", (cx + sx - 0.22, 2.38, 0.4), (cx + sx + 0.22, 2.82, 0.46), M["wood_dk"], 0.01)
        for lx in (-0.18, 0.18):
            for ly in (-0.18, 0.18):
                rod(kit, f"cafe_cl{sx}{lx}{ly}", (cx + sx + lx, 2.6 + ly, 0.0), (cx + sx + lx, 2.6 + ly, 0.4), 0.04, M["iron"])
        bk = 0.22 * (-1 if sx < 0 else 1) * -1
        bbox(kit, f"cafe_bk{sx}", (cx + sx - (0.22 if sx < 0 else -0.18), 2.38, 0.46),
             (cx + sx - (0.18 if sx < 0 else -0.22), 2.82, 0.95), M["wood_dk"], 0.01)
    # the wedding street (x 22): bunting between the two posts, two strings
    for k, zoff in enumerate((4.35, 3.7)):
        pts = []
        for i in range(11):
            u = i / 10
            x = 14.0 + u * 16.0
            z = zoff - 0.55 * math.sin(math.pi * u)
            pts.append((x, -1.2 - 0.0, z))
        for a, b in zip(pts, pts[1:]):
            rod(kit, f"str{k}{a[0]}", a, b, 0.02, M["string"])
        for i in range(1, 10):
            x, y, z = pts[i]
            col = ("flag_r", "flag_y", "flag_b", "flag_g")[(i + k) % 4]
            v = [(-0.17, 0, 0), (0.17, 0, 0), (0, 0, -0.34)]
            kit.mesh_obj(f"flag{k}{i}", v, [(0, 1, 2)], M[col], None, (x, y, z - 0.02))
            ob = bpy.data.objects[f"flag{k}{i}"]
            kit.mesh_obj(f"flagb{k}{i}", v[::-1], [(0, 1, 2)], M[col], None, (x, y, z - 0.02))
    # a few street things: bins and a bench would crowd the shots; keep the pavement clear
    # lights
    kit.light("st_sun", "SUN", (0, 0, 20), 3.6, "#fff0d8", rot=(math.radians(52), math.radians(8), math.radians(-28)))
    kit.light("st_sky", "AREA", (0, -4, 18), 5000.0, "#bcd6ff", size=60, rot=(0, 0, 0))


# ------------------------------------------------------------------------------------------------ the kitchen


def build_kitchen(kit, ctx, M):
    x0 = KX
    wbox(kit, "k_floor", (x0 - 3.2, -3.0, -0.1), (x0 + 3.2, 4.0, 0.0), M["floor"])
    wbox(kit, "k_back", (x0 - 3.2, 4.0, 0.0), (x0 + 3.2, 4.15, 2.6), M["wallcream"])
    wbox(kit, "k_left", (x0 - 3.2, -3.0, 0.0), (x0 - 3.05, 4.0, 2.6), M["wallcream"])
    wbox(kit, "k_right", (x0 + 3.05, -3.0, 0.0), (x0 + 3.2, 4.0, 2.6), M["wallcream"])
    wbox(kit, "k_ceil", (x0 - 3.2, -3.0, 2.6), (x0 + 3.2, 4.15, 2.7), M["paint_c"])
    # the window over the sink: a frame with the bright garden behind
    bbox(kit, "k_win", (x0 - 2.0, 3.99, 1.2), (x0 - 0.2, 4.03, 2.3), M["skyglow"], 0.0)
    for i, (a, b) in enumerate(((-2.06, -1.98), (-1.13, -1.07), (-0.22, -0.14))):
        wbox(kit, f"k_winv{i}", (x0 + a, 3.9, 1.14), (x0 + b, 3.99, 2.36), M["paint_w"])
    for i, z in enumerate((1.14, 1.74, 2.3)):
        wbox(kit, f"k_winh{i}", (x0 - 2.06, 3.9, z), (x0 - 0.14, 3.99, z + 0.06), M["paint_w"])
    # the counter and sink on the back wall
    bbox(kit, "k_counter", (x0 - 2.6, 3.3, 0.0), (x0 + 0.3, 4.0, 0.9), M["sage"], 0.01)
    bbox(kit, "k_top", (x0 - 2.65, 3.25, 0.9), (x0 + 0.35, 4.0, 0.95), M["wood"], 0.01)
    bbox(kit, "k_sink", (x0 - 1.6, 3.45, 0.93), (x0 - 0.7, 3.95, 0.97), M["steel"], 0.01)
    rod(kit, "k_tap", (x0 - 1.15, 3.9, 0.95), (x0 - 1.15, 3.9, 1.2), 0.04, M["steel"])
    rod(kit, "k_tap2", (x0 - 1.15, 3.9, 1.2), (x0 - 1.15, 3.7, 1.2), 0.04, M["steel"])
    # cupboards along the left wall
    bbox(kit, "k_cup", (x0 - 3.05, 0.4, 0.0), (x0 - 2.45, 3.3, 0.9), M["paint_c"], 0.01)
    bbox(kit, "k_cupt", (x0 - 3.05, 0.4, 0.9), (x0 - 2.4, 3.3, 0.95), M["wood"], 0.01)
    for i, y in enumerate((1.0, 1.9, 2.8)):
        bbox(kit, f"k_hdl{i}", (x0 - 2.46, y - 0.08, 0.6), (x0 - 2.42, y + 0.08, 0.66), M["brass"], 0.01)
    # the table (top at 0.75) and two chairs
    tx, ty = x0 + 1.0, 1.9
    bbox(kit, "k_table", (tx - 0.8, ty - 0.5, 0.72), (tx + 0.8, ty + 0.5, 0.77), M["wood"], 0.015)
    for sx in (-0.72, 0.72):
        for sy in (-0.42, 0.42):
            rod(kit, f"k_tl{sx}{sy}", (tx + sx, ty + sy, 0.0), (tx + sx, ty + sy, 0.72), 0.06, M["wood_dk"])
    for cy, bk in ((ty + 0.85, 1), (ty - 0.85, -1)):
        bbox(kit, f"k_ch{cy}", (tx - 0.25, cy - 0.25, 0.42), (tx + 0.25, cy + 0.25, 0.47), M["wood_dk"], 0.01)
        for sx in (-0.2, 0.2):
            for sy in (-0.2, 0.2):
                rod(kit, f"k_chl{cy}{sx}{sy}", (tx + sx, cy + sy, 0.0), (tx + sx, cy + sy, 0.42), 0.04, M["wood_dk"])
        by = cy + bk * 0.23
        bbox(kit, f"k_chb{cy}", (tx - 0.25, by - 0.02, 0.47), (tx + 0.25, by + 0.02, 0.95), M["wood_dk"], 0.01)
    ctx["table"] = (tx, ty)
    # on the table: the sugar bowl, cups, the teapot (upright), and the tipped pot with its stream
    kit.cyl("sugar", 0.1, 0.1, (tx + 0.1, ty + 0.05, 0.82), M["white"], n=18)
    kit.cyl("sugar_in", 0.085, 0.02, (tx + 0.1, ty + 0.05, 0.875), M["cream"], n=18)
    kit.cyl("cup_a", 0.06, 0.08, (tx - 0.35, ty - 0.2, 0.81), M["mug"], n=14)
    kit.cyl("cup_b", 0.06, 0.08, (tx - 0.35, ty + 0.25, 0.81), M["mugb"], n=14)
    pot_up = kit.empty("pot_up", (tx + 0.45, ty + 0.1, 0.77))
    kit.sphere("pot_up_b", 0.13, (0, 0, 0.13), M["mugb"], pot_up)
    kit.cyl("pot_up_lid", 0.05, 0.05, (0, 0, 0.27), M["mugb"], pot_up, n=12)
    rod(kit, "pot_up_sp", (0.08, 0, 0.1), (0.2, 0, 0.2), 0.035, M["mugb"], pot_up)
    ctx["pot_up"] = pot_up
    pot_t = kit.empty("pot_tip", (tx + 0.1, ty + 0.05, 1.12), rot=(0, math.radians(-62), 0))
    kit.sphere("pot_tip_b", 0.13, (0, 0, 0), M["mugb"], pot_t)
    rod(kit, "pot_tip_sp", (-0.08, 0, 0.0), (-0.22, 0, 0.1), 0.035, M["mugb"], pot_t)
    stream = wbox(kit, "pour", (tx + 0.1 - 0.012, ty + 0.05 - 0.012, 0.88), (tx + 0.1 + 0.012, ty + 0.05 + 0.012, 1.04), M["tea"])
    ctx["pot_tip"], ctx["stream"] = pot_t, stream
    # the hall hook: a board on the back wall with four hooks, three worn umbrellas, and mine in its wrapper
    bx = x0 + 2.2
    bbox(kit, "k_hookboard", (bx - 0.9, 3.9, 1.5), (bx + 0.9, 4.0, 1.7), M["wood_dk"], 0.01)
    for i, hx in enumerate((-0.65, -0.2, 0.25, 0.7)):
        rod(kit, f"k_hook{i}", (bx + hx, 3.9, 1.6), (bx + hx, 3.78, 1.55), 0.035, M["brass"])
    for i, (hx, mat) in enumerate(((-0.65, "umb1"), (-0.2, "umb2"), (0.25, "umb3"))):
        u = kit.empty(f"k_umb{i}", (bx + hx, 3.76, 1.52))
        kit.cyl(f"k_umbc{i}", 0.055, 0.8, (0, 0, -0.4), M[mat], u, n=12, r2=0.025)
        kit.box(f"k_umbh{i}", (0.05, 0.05, 0.14), (0, 0, 0.02), M["wood_dk"], u)
        kit.box(f"k_umbp{i}", (0.075, 0.115, 0.1), (0, 0, -0.35 - 0.1 * i), M["patch"], u)    # a patch
    u = kit.empty("k_umb_mine", (bx + 0.7, 3.74, 1.5))
    kit.cyl("k_umb_m", 0.05, 0.8, (0, 0, -0.4), M["umb_furl"], u, n=12, r2=0.02)
    kit.cyl("k_umb_w", 0.075, 0.9, (0, 0, -0.43), M["wrap"], u, n=14)
    kit.cyl("k_umb_band", 0.078, 0.1, (0, 0, -0.28), M["band"], u, n=14)
    # lights
    kit.light("ki_win", "AREA", (x0 - 1.1, 4.8, 1.8), 600.0, "#d8e8ff", size=2.4, rot=(math.radians(90), 0, 0))
    kit.aim(kit.LIGHTS["ki_win"]["obj"], (x0 - 0.2, 1.8, 1.0))
    kit.light("ki_ceil", "AREA", (x0 + 0.3, 1.2, 2.5), 330.0, "#ffe2b8", size=2.6, rot=(math.pi, 0, 0))
    kit.light("ki_fill", "AREA", (x0 + 0.5, -2.0, 2.2), 140.0, "#ffe8cc", size=3.0)
    kit.aim(kit.LIGHTS["ki_fill"]["obj"], (x0 + 0.5, 2.0, 1.0))


# ------------------------------------------------------------------------------------------------ the cinema


def build_cinema(kit, ctx, M):
    x0 = CX
    wbox(kit, "c_floor", (x0 - 5, -1.0, -0.1), (x0 + 5, 10.0, 0.0), M["carpet"])
    wbox(kit, "c_back", (x0 - 5, 10.0, 0.0), (x0 + 5, 10.15, 5.0), M["dark"])
    wbox(kit, "c_l", (x0 - 5, -1.0, 0.0), (x0 - 4.85, 10.0, 5.0), M["dark"])
    wbox(kit, "c_r", (x0 + 4.85, -1.0, 0.0), (x0 + 5, 10.0, 5.0), M["dark"])
    wbox(kit, "c_ceil", (x0 - 5, -1.0, 4.0), (x0 + 5, 10.15, 4.1), M["dark"])
    for row, y in enumerate((3.0, 4.6, 6.2, 7.8)):
        z0 = 0.18 * row
        wbox(kit, f"c_step{row}", (x0 - 4.8, y - 0.6, 0.0), (x0 + 4.8, y + 0.7, z0), M["carpet"])
        for i in range(-4, 5):
            sx = x0 + i * 0.62
            bbox(kit, f"c_s{row}{i}", (sx - 0.26, y - 0.27, z0 + 0.38), (sx + 0.26, y + 0.27, z0 + 0.46), M["seat"], 0.03)
            bbox(kit, f"c_sb{row}{i}", (sx - 0.26, y + 0.2, z0 + 0.46), (sx + 0.26, y + 0.3, z0 + 1.0), M["seat"], 0.04)
            bbox(kit, f"c_sa{row}{i}", (sx + 0.27, y - 0.27, z0 + 0.44), (sx + 0.33, y + 0.27, z0 + 0.6), M["dark"], 0.02)
    kit.light("ci_screen", "AREA", (x0, 0.4, 2.0), 1400.0, "#6f9aff", size=3.5)
    kit.aim(kit.LIGHTS["ci_screen"]["obj"], (x0, 4.0, 1.0))
    kit.light("ci_fill", "AREA", (x0 + 0.5, -0.4, 3.0), 160.0, "#8fb0ff", size=3.0)
    kit.aim(kit.LIGHTS["ci_fill"]["obj"], (x0, 5.0, 0.5))


# ------------------------------------------------------------------------------------------------ the garden


def roof_z(x):
    return EAVE + (2.3 - abs(x)) / 2.3 * (RIDGE - EAVE)


def build_garden(kit, ctx, M):
    x0 = GX
    # ground: dry straw lawn, flagstone path, Pell's green lawn over the west hedge
    wbox(kit, "g_ground", (x0 - 7, -1.0, -0.2), (x0 + 14, 40, 0.0), M["straw"])
    wbox(kit, "g_pell_lawn", (x0 - 30, -1.0, -0.19), (x0 - 5.6, 40, 0.02), M["green"])
    for i in range(14):
        wbox(kit, f"g_flag{i}", (x0 - 0.45, 0.6 + i * 1.12, 0.0), (x0 + 0.45, 1.5 + i * 1.12, 0.05), M["flag"])
    wbox(kit, "g_pad", (x0 - 2.6, 15.0, 0.0), (x0 + 2.6, 15.9, 0.04), M["flag"])
    # the back of our house and the back door (lit)
    wbox(kit, "g_house", (x0 - 7, -6, 0.0), (x0 + 7, 0.0, 5.6), M["brick_pale"])
    prism_roof(kit, "g_roof", x0 - 7.1, x0 + 7.1, -6.4, 0.4, 5.6, 7.2, M["slate"])
    bbox(kit, "g_door", (x0 - 0.5, -0.06, 0.0), (x0 + 0.5, 0.0, 2.1), M["paint_c"], 0.0)
    for wx in (-3.4, 3.4, -3.4, 3.4):
        pass
    bbox(kit, "g_win1", (x0 - 3.9, -0.05, 1.0), (x0 - 2.7, 0.0, 2.3), M["winwarm"], 0.0)
    bbox(kit, "g_win2", (x0 + 2.7, -0.05, 1.0), (x0 + 3.9, 0.0, 2.3), M["winwarm"], 0.0)
    bbox(kit, "g_win3", (x0 - 3.9, -0.05, 3.5), (x0 - 2.7, 0.0, 4.8), M["glass_old"], 0.0)
    bbox(kit, "g_win4", (x0 + 2.7, -0.05, 3.5), (x0 + 3.9, 0.0, 4.8), M["glass_old"], 0.0)
    # hedges: the far privet (y 26), the west one low (so Mr Pell shows over it), an east fence
    wbox(kit, "g_far", (x0 - 14, 25.4, 0.0), (x0 + 14, 27.0, 2.1), M["hedge_n"])
    wbox(kit, "g_west", (x0 - 6.0, 0.8, 0.0), (x0 - 5.3, 26.0, 1.15), M["hedge"])
    wbox(kit, "g_east", (x0 + 6.0, 0.8, 0.0), (x0 + 6.1, 26.0, 1.5), M["wood_dk"])
    # Mr Pell's house over the west hedge, with a porch lamp
    wbox(kit, "g_pellh", (x0 - 20, 6, 0.0), (x0 - 12.5, 18, 5.4), M["brick"])
    prism_roof(kit, "g_pellr", x0 - 20.1, x0 - 12.4, 5.7, 18.3, 5.4, 7.0, M["slate"])
    bbox(kit, "g_pelld", (x0 - 12.55, 11.4, 0.0), (x0 - 12.45, 12.6, 2.1), M["paint_c"], 0.0)
    bbox(kit, "g_pellw", (x0 - 12.55, 8.0, 1.0), (x0 - 12.45, 9.4, 2.3), M["winwarm"], 0.0)
    kit.sphere("g_porch", 0.14, (x0 - 12.1, 12.8, 2.5), M["porch"])
    kit.light("ga_porch", "POINT", (x0 - 11.4, 12.8, 2.5), 260.0, "#ffc886", size=0.2)
    # stars
    ctx["stars"] = []
    rng = np.random.default_rng(5)
    for i in range(90):
        az = rng.uniform(math.radians(30), math.radians(150))
        el = rng.uniform(math.radians(20), math.radians(75))
        r = 90.0
        p = (x0 + r * math.cos(az), r * math.sin(az) * 0.9 + 10, r * math.sin(el))
        ctx["stars"].append(kit.sphere(f"star{i}", rng.uniform(0.07, 0.16), p, M["star"], seg=6))
    # moon and sun and sky, switched by time of day
    kit.light("ga_sun", "SUN", (x0, 0, 20), 3.6, "#fff0d8", rot=(math.radians(48), math.radians(6), math.radians(-30)))
    kit.light("ga_sky", "AREA", (x0, 12, 20), 4200.0, "#bcd6ff", size=60)
    kit.light("ga_moon", "SUN", (x0, 0, 20), 0.22, "#aac4ff", rot=(math.radians(50), 0, math.radians(180)))
    kit.light("ga_dusk", "SUN", (x0, 0, 20), 1.2, "#ff9a60", rot=(math.radians(80), math.radians(8), math.radians(-30)))
    kit.light("ga_morn", "SUN", (x0, 0, 20), 2.6, "#ffd8a0", rot=(math.radians(66), math.radians(8), math.radians(-60)))
    kit.light("ga_backdoor", "POINT", (x0, 1.2, 1.5), 90.0, "#ffbe78", size=0.2)
    # the creature's own lights (cool rim from the moon side, a low warm light from the lamps), set in animate
    kit.light("ga_rim", "SPOT", (x0 + 5, 22, 6.0), 900.0, "#a8c4ff", size=0.3, spot=40, blend=0.6)
    kit.light("ga_under", "SPOT", (x0 + 0.9, 18.7, 0.8), 50.0, "#ffc890", size=0.15, spot=60, blend=0.7)
    kit.light("ga_undr2", "SPOT", (x0 + 1.5, 18.2, 0.7), 40.0, "#ffc890", size=0.15, spot=60, blend=0.7)
    kit.aim(kit.LIGHTS["ga_rim"]["obj"], (x0 + 2.4, 19.5, 2.0))
    kit.aim(kit.LIGHTS["ga_under"]["obj"], (x0 + 1.55, 19.5, 1.35))
    kit.aim(kit.LIGHTS["ga_undr2"]["obj"], (x0 + 1.55, 19.5, 1.35))


def build_glasshouse(kit, ctx, M):
    x0 = GX
    th = THETA
    y0, y1 = GH_Y0, GH_Y1
    n = 6
    # brick dwarf wall, 0.6 m, all round; the front gable has the door gap
    h = 0.6
    wbox(kit, "gh_wl", (x0 - 2.3, y0, 0.0), (x0 - 2.22, y1, h), M["brick_pale"])
    wbox(kit, "gh_wr", (x0 + 2.22, y0, 0.0), (x0 + 2.3, y1, h), M["brick_pale"])
    wbox(kit, "gh_wb", (x0 - 2.3, y1 - 0.08, 0.0), (x0 + 2.3, y1, h), M["brick_pale"])
    wbox(kit, "gh_wf1", (x0 - 2.3, y0, 0.0), (x0 - 0.5, y0 + 0.08, h), M["brick_pale"])
    wbox(kit, "gh_wf2", (x0 + 0.5, y0, 0.0), (x0 + 2.3, y0 + 0.08, h), M["brick_pale"])
    wbox(kit, "gh_floor", (x0 - 2.3, y0, -0.05), (x0 + 2.3, y1, 0.02), M["flag"])
    wbox(kit, "gh_sill", (x0 - 2.34, y0 - 0.02, h), (x0 + 2.34, y1 + 0.02, h + 0.05), M["paint_w"])
    # posts, rails and glass on both long sides and both gables
    for i in range(n + 1):
        y = y0 + i * (y1 - y0) / n
        for sx in (-1, 1):
            wbox(kit, f"gh_post{sx}{i}", (x0 + sx * 2.3 - 0.04, y - 0.04, h), (x0 + sx * 2.3 + 0.04, y + 0.04, EAVE), M["paint_w"])
    for sx in (-1, 1):
        wbox(kit, f"gh_eave{sx}", (x0 + sx * 2.3 - 0.05, y0, EAVE - 0.05), (x0 + sx * 2.3 + 0.05, y1, EAVE + 0.04), M["paint_w"])
        wbox(kit, f"gh_rail{sx}", (x0 + sx * 2.3 - 0.03, y0, 1.1), (x0 + sx * 2.3 + 0.03, y1, 1.15), M["paint_w"])
        for i in range(n):
            ya = y0 + i * (y1 - y0) / n
            old = "glass_old" if (i + sx) % 3 == 0 else "glass"
            wbox(kit, f"gh_gw{sx}{i}", (x0 + sx * 2.3 - 0.01, ya + 0.04, h + 0.05), (x0 + sx * 2.3 + 0.01, ya + (y1 - y0) / n - 0.04, EAVE - 0.05), M[old])
    wbox(kit, "gh_ridge", (x0 - 0.06, y0 - 0.05, RIDGE - 0.03), (x0 + 0.06, y1 + 0.05, RIDGE + 0.06), M["paint_w"])
    # gables: a triangle of glass above the eaves at each end, door at the front
    for yy, nm in ((y0, "f"), (y1, "b")):
        v = [(x0 - 2.3, yy, EAVE), (x0 + 2.3, yy, EAVE), (x0, yy, RIDGE)]
        kit.mesh_obj(f"gh_gab{nm}", v, [(0, 1, 2)], M["glass"])
        kit.mesh_obj(f"gh_gab{nm}2", v[::-1], [(0, 1, 2)], M["glass"])
        for sx in (-1, 1):
            rod(kit, f"gh_gabr{nm}{sx}", (x0 + sx * 2.3, yy, EAVE), (x0, yy, RIDGE), 0.07, M["paint_w"])
    # back gable below the eaves: panes
    wbox(kit, "gh_bpane", (x0 - 2.22, y1 - 0.02, h), (x0 + 2.22, y1 - 0.01, EAVE), M["glass"])
    wbox(kit, "gh_fpane1", (x0 - 2.22, y0 + 0.01, h), (x0 - 0.5, y0 + 0.02, EAVE), M["glass_old"])
    wbox(kit, "gh_fpane2", (x0 + 0.5, y0 + 0.01, h), (x0 + 2.22, y0 + 0.02, EAVE), M["glass"])
    wbox(kit, "gh_fhead", (x0 - 0.55, y0 - 0.03, 2.0), (x0 + 0.55, y0 + 0.05, 2.1), M["paint_w"])
    for sx in (-1, 1):
        wbox(kit, f"gh_fjamb{sx}", (x0 + sx * 0.5 - 0.04, y0 - 0.03, 0.0), (x0 + sx * 0.5 + 0.04, y0 + 0.05, 2.1), M["paint_w"])
    # door: a leaf hinged on the left jamb (x -0.5), iron strap hinges, two terracotta strokes on the top one
    hinge = kit.empty("gh_doorhinge", (x0 - 0.5, y0 - 0.0, 0.0))
    ctx["door"] = hinge
    bbox(kit, "gh_leafd", (0.0, -0.02, 0.0), (1.0, 0.02, 2.0), M["paint_w"], 0.01, hinge)
    kit.box("gh_leafg", (0.62, 0.025, 1.2), (0.5, -0.02, 1.15), M["glass_old"], hinge)
    for i, z in enumerate((0.35, 1.55)):
        kit.box(f"gh_strap{i}", (0.5, 0.05, 0.1), (0.25, -0.045, z), M["iron"], hinge, bevel=0.01)
        kit.box(f"gh_pin{i}", (0.07, 0.07, 0.14), (0.02, -0.045, z), M["iron"], hinge, bevel=0.01)
    for k in range(2):
        kit.box(f"gh_scratch{k}", (0.026, 0.012, 0.085), (0.19 + 0.07 * k, -0.074, 1.55), M["terra"], hinge, rot=(0, 0.35, 0))
    kit.box("gh_knob", (0.06, 0.06, 0.06), (0.9, -0.05, 1.0), M["brass"], hinge)
    # roof: both slopes, three rows of panes per bay, glazing bars; the vent cell (bay 3, row 0, +x) is a hole
    L = math.hypot(2.3, 1.4)
    rows = 3
    sl = L / rows
    for sx in (-1, 1):
        for i in range(n + 1):
            y = y0 + i * (y1 - y0) / n
            mid = (x0 + sx * 1.15, y, (EAVE + RIDGE) / 2 + 0.03)
            ob = kit.box(f"gh_raf{sx}{i}", (L, 0.06, 0.07), mid, M["paint_w"])
            ob.rotation_euler = (0, th * sx, 0)
        for r in range(rows + 1):
            s = r * sl
            x = x0 + sx * (2.3 - s * math.cos(th))
            z = EAVE + s * math.sin(th)
            wbox(kit, f"gh_bar{sx}{r}", (x - 0.03, y0, z - 0.02), (x + 0.03, y1, z + 0.04), M["paint_w"])
        for i in range(n):
            ya, yb = y0 + i * (y1 - y0) / n, y0 + (i + 1) * (y1 - y0) / n
            for r in range(rows):
                if sx == 1 and i == 3 and r == 0:
                    continue
                s = (r + 0.5) * sl
                cx = x0 + sx * (2.3 - s * math.cos(th))
                cz = EAVE + s * math.sin(th) + 0.01
                old = "glass_old" if (i * 3 + r + (1 if sx > 0 else 0)) % 4 == 0 else "glass"
                ob = kit.box(f"gh_p{sx}{i}{r}", (sl - 0.07, yb - ya - 0.07, 0.016), (cx, (ya + yb) / 2, cz), M[old])
                ob.rotation_euler = (0, th * sx, 0)
    # the vent: hinged at the top edge of the hole (s = sl), a flap sl long, an iron arm to prop it
    ys = y0 + 3 * (y1 - y0) / n
    hx = x0 + (2.3 - sl * math.cos(th))
    hz = EAVE + sl * math.sin(th) + 0.01
    vent = kit.empty("gh_venthinge", (hx, ys + (y1 - y0) / n / 2, hz))
    ctx["vent"] = vent
    ctx["vent_base"] = th
    w = (y1 - y0) / n - 0.07
    kit.box("gh_vent", (sl - 0.07, w, 0.016), (-(sl - 0.07) / 2 - 0.02, 0, 0.0), M["glass"], vent)
    for sgn in (-1, 1):
        kit.box(f"gh_ventf{sgn}", (sl - 0.06, 0.05, 0.05), (-(sl - 0.07) / 2 - 0.02, sgn * (w / 2), 0.0), M["paint_w"], vent)
    kit.box("gh_ventf3", (0.05, w, 0.05), (-sl + 0.07, 0, 0.0), M["paint_w"], vent)
    ctx["vent_arm"] = None
    # the arm: a notched iron stay from the roof (s = 0.45 of the hole) to the flap's edge, set in animate
    base = (x0 + (2.3 - 0.4 * math.cos(th)), ys + (y1 - y0) / n / 2 + 0.3, EAVE + 0.4 * math.sin(th) + 0.04)
    arm = kit.box("gh_ventarm", (0.03, 0.03, 1.0), base, M["iron"])
    ctx["vent_arm"], ctx["vent_arm_base"] = arm, base
    # benches (Mum's on the left, Lou's on the right), each with slats and pots
    ctx["plants"] = []
    for sx, nm in ((-1, "mum"), (1, "lou")):
        bx0, bx1 = (x0 + sx * 1.65, x0 + sx * 2.2)
        lo, hi = min(bx0, bx1), max(bx0, bx1)
        for k in range(5):
            xa = lo + k * (hi - lo) / 5
            wbox(kit, f"gh_sl{nm}{k}", (xa + 0.01, y0 + 0.7, 0.72), (xa + (hi - lo) / 5 - 0.01, y1 - 0.7, 0.76), M["wood"])
        for yy in (y0 + 0.75, y0 + 2.5, y0 + 4.25, y1 - 0.75):
            for xx in (lo + 0.04, hi - 0.04):
                wbox(kit, f"gh_bl{nm}{yy}{xx}", (xx - 0.04, yy - 0.04, 0.0), (xx + 0.04, yy + 0.04, 0.72), M["wood_dk"])
        wbox(kit, f"gh_bs{nm}", (lo, y0 + 0.7, 0.5), (hi, y1 - 0.7, 0.54), M["wood_dk"])
        for j in range(7):
            if nm == "mum" and j in (1, 2):
                continue
            py = y0 + 0.95 + j * 0.7
            px = (lo + hi) / 2
            kit.cyl(f"gh_pot{nm}{j}", 0.1, 0.18, (px, py, 0.85), M["pot"], n=14, r2=0.12)
            kit.cyl(f"gh_soil{nm}{j}", 0.1, 0.01, (px, py, 0.94), M["soil"], n=14)
            for b in range(6):
                psi = b * math.pi / 3 + j * 0.7
                ob = kit.mesh_obj(f"gh_lf{nm}{j}{b}", kit.box_verts(0.07, 0.016, 0.34, (0, 0, 0.17)), kit.BOX_FACES,
                                  ctx["leaf"], None, (px, py, 0.94))
                ctx["plants"].append((ob, psi, 0.9 + 0.05 * (b % 3)))
    # the wicker chair for Mum, the potting table with dry leaves, the postcard and Lou's photo
    cx, cy = x0 + 0.85, 19.5
    bbox(kit, "gh_chs", (cx - 0.3, cy - 0.3, 0.36), (cx + 0.3, cy + 0.3, 0.44), M["wicker"], 0.03)
    bbox(kit, "gh_chb", (cx - 0.3, cy + 0.26, 0.44), (cx + 0.3, cy + 0.34, 1.15), M["wicker"], 0.05)
    for sx in (-1, 1):
        bbox(kit, f"gh_cha{sx}", (cx + sx * 0.3 - 0.03, cy - 0.3, 0.44), (cx + sx * 0.3 + 0.03, cy + 0.3, 0.62), M["wicker"], 0.02)
        for sy in (-1, 1):
            rod(kit, f"gh_chl{sx}{sy}", (cx + sx * 0.26, cy + sy * 0.26, 0.0), (cx + sx * 0.26, cy + sy * 0.26, 0.36), 0.04, M["wicker"])
    ctx["chair"] = (cx, cy)
    tx, ty = x0 - 0.2, 21.45
    bbox(kit, "gh_tbl", (tx - 0.65, ty - 0.3, 0.84), (tx + 0.65, ty + 0.3, 0.9), M["wood"], 0.01)
    for sx in (-0.58, 0.58):
        for sy in (-0.24, 0.24):
            rod(kit, f"gh_tl{sx}{sy}", (tx + sx, ty + sy, 0.0), (tx + sx, ty + sy, 0.84), 0.06, M["wood_dk"])
    bbox(kit, "gh_tsh", (tx - 0.6, ty - 0.26, 0.3), (tx + 0.6, ty + 0.26, 0.34), M["wood_dk"], 0.01)
    ctx["leaves"] = []
    rng = np.random.default_rng(11)
    for i in range(16):
        lx, ly = tx + rng.uniform(-0.55, 0.45), ty + rng.uniform(-0.2, 0.2)
        ob = kit.box(f"gh_dry{i}", (0.16, 0.08, 0.012), (lx, ly, 0.915), M["leaf_dry"], rot=(0, 0, rng.uniform(0, 3)))
        ctx["leaves"].append((ob, (lx, ly, 0.915), rng.uniform(0, 6)))
    img_quad(kit, "gh_card", 0.2, 0.135, pil_mat(kit, "sea card", sea_card(), 0.6), (tx + 0.52, ty + 0.0, 0.99), rot=(math.radians(-72), 0, 0))
    # card is propped against the wall of a pot: a little block behind it
    kit.box("gh_cardprop", (0.2, 0.03, 0.08), (tx + 0.52, ty + 0.04, 0.93), M["wood_dk"])
    # Lou's photo in a frame, standing on Mum's bench
    px, py = x0 - 1.93, y0 + 2.0
    bbox(kit, "gh_frame", (px - 0.13, py - 0.015, 0.76), (px + 0.13, py + 0.015, 1.07), M["brass"], 0.01)
    ob = img_quad(kit, "gh_photo", 0.2, 0.25, pil_mat(kit, "lou photo", lou_photo(), 0.5), (px, py - 0.017, 0.915))
    # the hanging lamps
    ctx["lamp_mats"] = []
    for i, yy in enumerate((17.7, 20.6)):
        lamp = kit.empty(f"gh_lampg{i}", (x0, yy, 2.45))
        rod(kit, f"gh_cord{i}", (x0, yy, RIDGE - 0.02), (x0, yy, 2.62), 0.012, M["iron"])
        kit.cyl(f"gh_shade{i}", 0.05, 0.16, (x0, yy, 2.5), M["iron"], n=14, r2=0.2)
        lm = kit.emit("#ffbe78", 3.0, f"lampbulb{i}")
        kit.sphere(f"gh_bulb{i}", 0.07, (x0, yy, 2.4), lm)
        ctx["lamp_mats"].append(lm)
        kit.light(f"ga_lamp{i}", "POINT", (x0, yy, 2.3), 55.0, "#ffd6a8", size=0.15)
    kit.light("ga_lampfill", "AREA", (x0, 19.0, 2.2), 25.0, "#ffd6a8", size=3.0, rot=(math.pi, 0, 0))
    kit.light("ga_cool", "AREA", (x0, 19.0, 2.9), 45.0, "#a8c0ff", size=4.0, rot=(math.pi, 0, 0))
    # the torn-off wrapper and its paper band on the floor, and the drops that fall through the open vent
    w1 = kit.cyl("gh_wrap", 0.075, 0.9, (x0 + 0.2, 18.1, 0.075), M["wrap"], n=14, rot=(math.pi / 2, 0, 0.25))
    w2 = kit.cyl("gh_wrapband", 0.078, 0.1, (x0 + 0.17, 17.85, 0.078), M["band"], n=14, rot=(math.pi / 2, 0, 0.25))
    ctx["wrapper"] = [w1, w2]
    ctx["ventrain"] = []
    for i in range(26):
        d = kit.mesh_obj(f"gh_vr{i}", kit.box_verts(0.016, 0.016, 0.16), kit.BOX_FACES, M["drop"])
        d.hide_render = True
        ctx["ventrain"].append(d)


# ------------------------------------------------------------------------------------------------ clouds and rain


def cloud_mat(kit, name, hexc, emit):
    m = kit._new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Roughness"].default_value = 0.95
    b.inputs["Emission Color"].default_value = kit.col(hexc)
    b.inputs["Emission Strength"].default_value = emit
    kit._fogged(m, b.outputs[0])
    return m, b


def build_clouds(kit, ctx, story, M):
    """One cloud per name in story['clouds'], parked at the origin; animate moves it over the head."""
    ctx["clouds"] = {}
    for who, spec in story.get("clouds", {}).items():
        m, b = cloud_mat(kit, f"cloud {who}", spec.get("color", "#f6f8fb"), spec.get("emit", 0.4))
        root = kit.empty(f"cloud.{who}", (0, 0, -50))
        parts = [(0.0, 0.0, 0.0, 0.2, 0.85), (-0.2, 0.02, -0.02, 0.15, 0.8), (0.2, -0.02, -0.02, 0.16, 0.8),
                 (-0.33, 0.0, -0.06, 0.1, 0.75), (0.34, 0.0, -0.06, 0.11, 0.75), (-0.08, -0.08, 0.1, 0.12, 0.8),
                 (0.1, 0.06, 0.1, 0.13, 0.8), (0.0, 0.1, -0.03, 0.15, 0.8)]
        for i, (x, y, z, r, fz) in enumerate(parts):
            ob = kit.sphere(f"cloud.{who}.{i}", r, (x, y, z), m, root, seg=14)
            ob.scale = (1.0, 0.9, fz)
        if spec.get("under"):
            um, ub = cloud_mat(kit, f"cloud under {who}", spec["under"], spec.get("emit", 0.3))
            ob = kit.sphere(f"cloud.{who}.under", 0.2, (0, 0, -0.1), um, root, seg=14)
            ob.scale = (1.5, 1.0, 0.35)
            ctx.setdefault("cloud_under", {})[who] = ub
        drops = []
        for k in range(spec.get("drops", 0)):
            d = kit.mesh_obj(f"drop.{who}.{k}", kit.box_verts(0.012, 0.012, 0.13), kit.BOX_FACES, M["drop"])
            d.hide_render = True
            drops.append(d)
        ctx["clouds"][who] = {"root": root, "bsdf": b, "drops": drops, "spec": spec, "base": spec.get("color", "#f6f8fb")}


def hexl(kit, hexc):
    return kit.col(hexc)[:3]


def head_top(story, who):
    return story["cast"][who].get("height", 1.0) * S * 5.3


def animate_clouds(kit, story, tl, t, ctx, active):
    from blocky import kit as K
    for who, c in ctx["clouds"].items():
        s = ac.state(tl, who, t)
        on = (not s["hidden"]) and _switch(_who(tl, "cloud", who), "on", t, True) and active(s["x"])
        for ob in [c["root"]] + list(c["root"].children_recursive):
            ob.hide_render = not on
        if not on:
            for d in c["drops"]:
                d.hide_render = True
            continue
        cs = _who(tl, "cloud", who)
        spec = c["spec"]
        gap = _level(cs, "gap", t, spec.get("gap", 0.12))
        size = _level(cs, "size", t, spec.get("size", 1.0))
        tone = _level(cs, "tone", t, 0.0)
        white = _level(cs, "white", t, 0.0)
        rain = _level(cs, "rain", t, 0.0)
        top = head_top(story, who) + spec.get("lift", 0.0)
        half = 0.14 * size
        ox, oy = spec.get("off", (0, 0))
        x, y, z = s["x"] + ox, s["y"] + oy, s["z"] + top + gap + half
        c["root"].location = (x, y, z)
        c["root"].scale = (size, size, size)
        # a slow bob and a tone shift toward grey (my cloud going grey)
        c["root"].location.z += 0.012 * math.sin(t * 0.9 + len(who))
        base = np.array(hexl(kit, c["base"]))
        base = base * (1 - white) + np.array(hexl(kit, "#f6f8fb")) * white
        grey = np.array(hexl(kit, spec.get("grey", "#737b88")))
        col = tuple(base * (1 - tone) + grey * tone)
        for k in ("Base Color", "Emission Color"):
            c["bsdf"].inputs[k].default_value = (*col, 1.0)
        if who in ctx.get("cloud_under", {}):
            ub = ctx["cloud_under"][who]
            ug = np.array(hexl(kit, spec["under"]))
            ucol = tuple(ug * (1 - tone) + grey * tone)
            for k in ("Base Color", "Emission Color"):
                ub.inputs[k].default_value = (*ucol, 1.0)
        # rain: a pool of drops falling from just under the cloud to the floor
        drops = c["drops"]
        if not drops:
            continue
        floor = spec.get("floor")
        zf = (s["z"] + top * 0.82 if floor is None else floor)
        zt = z - 0.08 * size
        H = max(0.2, zt - zf)
        nvis = int(round(rain * len(drops)))
        for i, d in enumerate(drops):
            if i >= nvis or H < 0.25:
                d.hide_render = True
                continue
            d.hide_render = False
            h = kit.hash01(i, len(who), 3)
            ang = kit.hash01(i, 5, len(who)) * math.tau
            rr = (0.1 + 0.55 * kit.hash01(i, 9, 2)) * size * 0.5 * spec.get("spread", 1.0)
            ph = (t * spec.get("fall", 2.6) / H + h) % 1.0
            d.location = (x + rr * math.cos(ang), y + rr * math.sin(ang) * 0.6 - 0.06, zt - ph * H)


# ------------------------------------------------------------------------------------------------ umbrellas


def build_umbrellas(kit, ctx, story, M):
    ctx["umb"] = {}
    for who, spec in story.get("umbrellas", {}).items():
        root = kit.empty(f"umb.{who}", (0, 0, -50))
        mat = M[spec.get("mat", "umb1")]
        kit.cyl(f"umb.{who}.c", 0.62, 0.2, (0, 0, 0.1), mat, root, n=24, r2=0.06)
        kit.cyl(f"umb.{who}.rim", 0.63, 0.03, (0, 0, 0.0), mat, root, n=24)
        kit.cyl(f"umb.{who}.pole", 0.02, 0.5, (0, 0, -0.2), M["steel"], root, n=8)
        kit.box(f"umb.{who}.h", (0.05, 0.05, 0.1), (0, 0, -0.46), M["wood_dk"], root)
        ctx["umb"][who] = (root, spec)


def animate_umbrellas(tl, t, ctx, story, active):
    for who, (root, spec) in ctx["umb"].items():
        s = ac.state(tl, who, t)
        on = _switch(_who(tl, "umbrella", who), "on", t, False) and not s["hidden"] and active(s["x"])
        for ob in [root] + list(root.children_recursive):
            ob.hide_render = not on
        if on:
            root.location = (s["x"], s["y"], s["z"] + head_top(story, who) + 0.28)
            c = ctx["clouds"].get(who)
            if c is not None:
                c["spec"]["floor"] = s["z"] + head_top(story, who) + 0.38
        else:
            c = ctx["clouds"].get(who)
            if c is not None and spec.get("floor_was") is None:
                c["spec"]["floor"] = None


# ------------------------------------------------------------------------------------------------ the creature


def creature_face():
    s = faces.FX1 - faces.FX0
    w, h = faces.TEX_W, faces.TEX_H
    im = Image.new("RGB", (w, h), (56, 80, 42))
    nz = np.random.default_rng(3).normal(0, 4, (h, w, 1))
    a = np.clip(np.asarray(im).astype(np.float32) + nz, 0, 255).astype(np.uint8)
    im = Image.fromarray(a)
    d = ImageDraw.Draw(im)
    fx = lambda f: faces.FX0 + f * s
    fy = lambda f: faces.FY0 + f * (faces.FY1 - faces.FY0)
    ink = (6, 6, 8)
    # two small black eyes, set too close together, each with one tiny bright highlight
    for side in (-1, 1):
        cx, cy = fx(0.5) + side * 0.082 * s, fy(0.40)
        r = 0.04 * s
        d.ellipse([cx - r, cy - r * 1.2, cx + r, cy + r * 1.2], fill=ink)
        hr = r * 0.36
        d.ellipse([cx - r * 0.3 - hr, cy - r * 0.45 - hr, cx - r * 0.3 + hr, cy - r * 0.45 + hr], fill=(255, 255, 250))
    # a mouth like the split in an old clay pot: one long jagged crack with a hairline branch
    rng = np.random.default_rng(8)
    pts = []
    n = 16
    for i in range(n + 1):
        u = i / n
        x = fx(0.5) + (u - 0.5) * 0.7 * s
        y = fy(0.72) + 0.03 * s * math.sin(u * 3.4 - 1.0) + 0.02 * s * (rng.random() - 0.5) * 2 + 0.012 * s * (1 if i % 2 else -1)
        pts.append((x, y))
    d.line(pts, fill=ink, width=max(8, int(0.026 * s)), joint="curve")
    x, y = pts[10]
    d.line([(x, y), (x + 0.03 * s, y + 0.07 * s), (x + 0.015 * s, y + 0.11 * s)], fill=ink, width=max(3, int(0.008 * s)))
    x, y = pts[4]
    d.line([(x, y), (x - 0.02 * s, y - 0.05 * s)], fill=ink, width=max(3, int(0.007 * s)))
    return im.filter(ImageFilter.SMOOTH)


def build_creature(kit, ctx, M):
    root = kit.empty("neckman", (0, 0, -60))
    ctx["neckman"] = root
    # the body: an R6-sized person in a moss shirt and terracotta trousers (hips at 0.68 m)
    for sx in (-1, 1):
        kit.box(f"nm.leg{sx}", (0.33, 0.33, 0.66), (sx * 0.17, 0, 0.34), M["terra"], root, bevel=0.03)
        kit.box(f"nm.shoe{sx}", (0.34, 0.35, 0.1), (sx * 0.17, 0, 0.05), M["mossd"], root, bevel=0.02)
        kit.box(f"nm.arm{sx}", (0.32, 0.32, 0.66), (sx * 0.51, 0, 1.0), M["moss"], root, bevel=0.03)
        kit.box(f"nm.hand{sx}", (0.3, 0.3, 0.14), (sx * 0.51, 0, 0.62), M["mossd"], root, bevel=0.03)
    kit.box("nm.torso", (0.68, 0.34, 0.68), (0, 0, 1.0), M["moss"], root, bevel=0.03)
    kit.box("nm.belt", (0.7, 0.36, 0.1), (0, 0, 0.7), M["terra"], root, bevel=0.02)
    # the neck: eight stacked blocks, alternating terracotta and moss
    ctx["blocks"] = []
    for i in range(8):
        b = kit.box(f"nm.blk{i}", (0.27, 0.27, 0.3), (0, 0, 0), M["terra" if i % 2 == 0 else "moss"], bevel=0.018)
        b.rotation_mode = "XYZ"
        ctx["blocks"].append(b)
    # the head: our soft rounded cylinder with its own face
    hm, tex = rig.head_material("neckman", "#4a6834")
    pil = creature_face()
    img = bpy.data.images.new("neckman face", pil.width, pil.height, alpha=False)
    a = np.asarray(pil.convert("RGBA")).astype(np.float32)[::-1] / 255
    img.pixels.foreach_set(a.ravel())
    img.pack()
    tex.image = img
    head = kit.empty("nm.head", (0, 0, -60))
    hg = kit.empty("nm.headg", (0, 0, 0), head)
    hg.scale = (S * 0.8, S * 0.92, S * 1.28)       # a narrow, too-tall head: wrong before anyone sees the face
    rig.head_mesh("nm.headm", hm, hg)
    gm = kit.emit("#ffffff", 14.0, "glint")
    for side in (-1, 1):
        # the eye highlight: one tiny bright point on each black eye, the brightest thing in the frame
        kit.sphere(f"nm.glint{side}", 0.012, (side * 0.0885 - 0.0135, -0.627, 0.101 + 0.02), gm, hg, seg=6)
    ctx["nm_head"] = head
    ctx["nm_objs"] = [root] + list(root.children_recursive) + ctx["blocks"] + [head] + list(head.children_recursive)


def _poly_at(pts, s):
    """A point and the direction on a polyline at arc length s."""
    acc = 0.0
    for a, b in zip(pts, pts[1:]):
        seg = (b - a).length
        if acc + seg >= s - 1e-9:
            d = (b - a).normalized()
            return a + d * (s - acc), d
        acc += seg
    d = (pts[-1] - pts[-2]).normalized()
    return pts[-1], d


def pose_creature(ctx, cue):
    objs = ctx["nm_objs"]
    on = bool(cue and cue.get("on"))
    for ob in objs:
        ob.hide_render = not on
    if not on:
        return
    bx, by = cue["body"]
    root = ctx["neckman"]
    root.location = (bx + GX if cue.get("abs") is None else bx, by, 0.0)
    root.rotation_euler = (0, 0, math.radians(cue.get("yaw", 0)))
    pts = [V((p[0] + GX, p[1], p[2])) for p in cue["pts"]]
    total = sum((b - a).length for a, b in zip(pts, pts[1:]))
    n = len(ctx["blocks"])
    L = total / n
    for i, b in enumerate(ctx["blocks"]):
        s = (i + 0.5) * L
        p, d = _poly_at(pts, s)
        # a block near a corner takes the mean of the two directions, so a bend reads as a lean, not a snap
        d0 = _poly_at(pts, max(0.0, s - L * 0.5))[1]
        d1 = _poly_at(pts, min(total, s + L * 0.5))[1]
        dm = (d0 + d1).normalized() if (d0 + d1).length > 1e-3 else d
        up = V((0, 1, 0)) if abs(dm.y) < 0.9 else V((1, 0, 0))
        q = dm.to_track_quat("Z", "Y" if up.y == 1 else "X")
        side = q.to_matrix() @ V((1, 0, 0))
        wob = 0.022 * (1 if i % 2 else -1) * (1 + 0.5 * math.sin(i * 1.7))
        b.location = p + side * wob
        e = q.to_euler()
        b.rotation_euler = e
        b.scale = (1.0, 1.0, (L * 1.05) / 0.3)
        # a small twist, block to block, like flower pots leaning in a stack
        b.rotation_euler.rotate_axis("Z", math.radians(3.5 * math.sin(i * 2.3)))
    # the head rides at the end of the neck; its up is back along the last direction, its face looks at `look`
    end = pts[-1]
    last = _poly_at(pts, total)[1]
    hup = V(cue["up"]) if cue.get("up") else -last
    hup = hup.normalized()
    centre = end + last * 0.2
    look = V((cue["look"][0] + GX, cue["look"][1], cue["look"][2])) if cue.get("look") else centre + V((0, -1, 0))
    f = look - centre
    f = (f - hup * f.dot(hup))
    if f.length < 1e-4:
        f = V((0, -1, 0))
    f.normalize()
    if cue.get("roll"):
        hup = (Matrix.Rotation(math.radians(cue["roll"]), 3, f) @ hup).normalized()
    # head frame: face is -Y, up is +Z
    ycol = -f
    xcol = ycol.cross(hup).normalized()
    ycol = hup.cross(xcol).normalized()
    m = Matrix(((xcol.x, ycol.x, hup.x), (xcol.y, ycol.y, hup.y), (xcol.z, ycol.z, hup.z)))
    if cue.get("rim"):
        from blocky import kit as K
        ro = K.LIGHTS["ga_rim"]["obj"]
        ro.location = centre + V(cue["rim"])
        K.aim(ro, centre)
        K.LIGHTS["ga_rim"]["base"] = cue.get("rim_w", 200.0)
    head = ctx["nm_head"]
    head.location = centre
    head.rotation_euler = m.to_euler()


# ------------------------------------------------------------------------------------------------ build


def _grab(fn, *a):
    before = set(bpy.data.objects)
    fn(*a)
    return [o for o in bpy.data.objects if o not in before]


def build(kit, story, tl):
    ctx = {"groups": {}}
    M = materials(kit)
    ctx["M"] = M
    ctx["leaf"] = soft_mat(kit, "leaf", "#4f8a38", rough=0.8)
    ctx["groups"]["street"] = _grab(build_street, kit, ctx, M)
    ctx["groups"]["kitchen"] = _grab(build_kitchen, kit, ctx, M)
    ctx["groups"]["cinema"] = _grab(build_cinema, kit, ctx, M)
    g = _grab(build_garden, kit, ctx, M)
    g += _grab(build_glasshouse, kit, ctx, M)
    g += _grab(build_creature, kit, ctx, M)
    ctx["groups"]["garden"] = g
    build_clouds(kit, ctx, story, M)
    build_umbrellas(kit, ctx, story, M)
    ctx["leaf_b"] = ctx["leaf"].node_tree.nodes["Principled BSDF"]
    ctx["shot_room"] = {s["id"]: s.get("room", "street") for s in story["shots"]}
    ctx["mugs"] = {}
    return ctx


# ------------------------------------------------------------------------------------------------ animate

SCENE_X = {"street": (-60, 60), "kitchen": (60, 140), "garden": (150, 260), "cinema": (260, 340)}
TOD = {
    # sun, sky, moon, dusk, morn, backdoor, porch gains; sky colour, exposure
    "day": {"ga_sun": 1.0, "ga_sky": 1.0, "ga_moon": 0.0, "ga_dusk": 0.0, "ga_morn": 0.0, "ga_backdoor": 0.0, "ga_porch": 0.0,
            "ga_rim": 0.0, "ga_under": 0.0, "ga_undr2": 0.0, "sky": "#9cc4ee", "exp": 0.0, "stars": 0.0},
    "dusk": {"ga_sun": 0.0, "ga_sky": 0.12, "ga_moon": 0.3, "ga_dusk": 1.0, "ga_morn": 0.0, "ga_backdoor": 1.0, "ga_porch": 0.5,
             "ga_rim": 0.0, "ga_under": 0.0, "ga_undr2": 0.0, "sky": "#4a4a66", "exp": 0.3, "stars": 0.0},
    "night": {"ga_sun": 0.0, "ga_sky": 0.0, "ga_moon": 1.0, "ga_dusk": 0.0, "ga_morn": 0.0, "ga_backdoor": 1.0, "ga_porch": 1.0,
              "ga_rim": 1.0, "ga_under": 1.0, "ga_undr2": 1.0, "sky": "#0a101c", "exp": 0.4, "stars": 1.0},
    "morning": {"ga_sun": 0.0, "ga_sky": 0.5, "ga_moon": 0.0, "ga_dusk": 0.0, "ga_morn": 1.0, "ga_backdoor": 0.0, "ga_porch": 0.0,
                "ga_rim": 0.0, "ga_under": 0.0, "ga_undr2": 0.0, "sky": "#b5d2ee", "exp": 0.0, "stars": 0.0},
}
ROOM_SKY = {"street": ("#9cc4ee", 0.0), "kitchen": ("#202428", 0.0), "cinema": ("#05060a", 0.0)}


def _tod(tl, t):
    """The garden's light as a blend of the modes (each cue ramps over its dur)."""
    cs = _cues(tl, "tod")
    cur = TOD[cs[0]["mode"]] if cs else TOD["day"]
    prev = cur
    for c in cs:
        if c["t"] > t + 1e-9:
            break
        d = max(1e-6, c.get("dur", 0.3))
        prev, cur = cur, TOD[c["mode"]]
        if t < c["t"] + d:
            u = _ss((t - c["t"]) / d)
            out = {}
            for k in cur:
                if k == "sky":
                    a = np.array(prev["sky"] and [int(prev["sky"][i:i + 2], 16) for i in (1, 3, 5)], float)
                    b = np.array([int(cur["sky"][i:i + 2], 16) for i in (1, 3, 5)], float)
                    out[k] = a * (1 - u) + b * u
                else:
                    out[k] = prev[k] + (cur[k] - prev[k]) * u
            return out
    out = dict(cur)
    out["sky"] = np.array([int(cur["sky"][i:i + 2], 16) for i in (1, 3, 5)], float)
    return out


def _rig_sit(tl, who, t):
    return _switch(tl["acting"].get(who, []), "sit", t, False)


def animate(kit, story, tl, t, ctx):
    from blocky import kit as K
    over = {}
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    room = ctx["shot_room"].get(shot["id"], "street")
    active = lambda x: SCENE_X[room][0] <= x <= SCENE_X[room][1]
    for g, obs in ctx["groups"].items():
        hide = g != room
        if ctx.get("_hid", {}).get(g) != hide:
            for ob in obs:
                ob.hide_render = hide
            ctx.setdefault("_hid", {})[g] = hide
    # the cast: only those in this room are drawn; people sit; Mum's glasses keep their frames only
    for who in story["cast"]:
        s = ac.state(tl, who, t)
        for ob in [bpy.data.objects.get(f"{who}.{k}") for k in ("gl-1", "gl1")]:
            if ob is not None:
                ob.hide_render = True
        root = bpy.data.objects.get(who)
        if root is not None and not active(s["x"]):
            for ob in [root] + list(root.children_recursive):
                ob.hide_render = True
        keys = tl["acting"].get(who, [])
        if _rig_sit(tl, who, t):
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (-math.pi / 2, 0, 0)
        # props held in the hand (a mug)
        tilt = ac._held(keys, "mug", t, 0.0)
    # ---- the sky, the lights of this room
    kit_lights = K.LIGHTS
    for name in kit_lights:
        pre = name.split("_")[0]
        if pre in ("st", "ki", "ci"):
            over[name] = 1.0 if {"st": "street", "ki": "kitchen", "ci": "cinema"}[pre] == room else 0.0
        else:
            over[name] = 1.0 if room == "garden" else 0.0
    world = bpy.data.worlds["world"].node_tree.nodes["Background"]
    sc = bpy.context.scene
    if room == "garden":
        td = _tod(tl, t)
        for k, v in td.items():
            if k in kit_lights and k.startswith("ga_"):
                over[k] = v
        sky = td["sky"] / 255.0
        lin = [K.srgb(float(c)) for c in sky]
        world.inputs["Color"].default_value = (*lin, 1.0)
        sc.view_settings.exposure = td["exp"]
        for st in ctx["stars"]:
            st.hide_render = td["stars"] < 0.5
        lamps = _level(_cues(tl, "lamps"), "to", t, 1.0)
        over["ga_cool"] = td["ga_moon"]
        over["ga_lamp0"] = lamps
        over["ga_lamp1"] = lamps
        over["ga_lampfill"] = lamps
        over["ga_undr2"] = over.get("ga_undr2", 0) * (0.25 + 0.75 * lamps)
        over["ga_under"] = over.get("ga_under", 0) * (0.25 + 0.75 * lamps)
        for m in ctx["lamp_mats"]:
            m.node_tree.nodes["Emission"].inputs["Strength"].default_value = 3.0 * lamps
        # the backdoor glow and the lit windows are warm all night; Mr Pell's porch lamp is steady
    else:
        sk, ex = ROOM_SKY[room]
        lin = [K.srgb(int(sk[i:i + 2], 16) / 255) for i in (1, 3, 5)]
        world.inputs["Color"].default_value = (*lin, 1.0)
        sc.view_settings.exposure = story.get("exposure", {}).get(room, ex)
        for st in ctx["stars"]:
            st.hide_render = True
    # ---- plants, vent, door
    brown = _level(_cues(tl, "plants"), "to", t, 0.0)
    g = np.array(K.col("#4f8a38")[:3])
    b = np.array(K.col("#8a6a34")[:3])
    ctx["leaf_b"].inputs["Base Color"].default_value = (*(g * (1 - brown) + b * brown), 1.0)
    for ob, psi, ln in ctx["plants"]:
        tau = 0.18 + brown * 1.0
        ob.rotation_euler = (tau, 0, psi)
        ob.scale = (1, 1, ln * (1 - 0.15 * brown))
    vent = _level(_cues(tl, "vent"), "to", t, 0.0)
    th = ctx["vent_base"]
    ctx["vent"].rotation_euler = (0, th - math.radians(44) * vent, 0)
    arm = ctx["vent_arm"]
    base = V(ctx["vent_arm_base"])
    hing = V(ctx["vent"].location)
    # the flap's lower edge swings up and out; the arm runs from its base on the roof to that edge
    fl = hing + V((math.cos(th - math.radians(44) * vent), 0, -math.sin(th - math.radians(44) * vent))) * 0.82
    p1, p2 = base, V((fl.x, base.y, fl.z))
    d = p2 - p1
    arm.location = (p1 + p2) / 2
    arm.scale = (1, 1, max(0.05, d.length))
    arm.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    door = _level(_cues(tl, "door"), "to", t, 0.0)
    ctx["door"].rotation_euler = (0, 0, -math.radians(100) * door)
    # ---- the creature
    cue = None
    for c in _cues(tl, "neck"):
        if c["t"] <= t + 1e-9:
            cue = c
    pose_creature(ctx, cue if room == "garden" else None)
    # ---- the dry leaves on the potting table
    rus = _switch(_cues(tl, "rustle"), "on", t, False)
    for ob, loc, ph in ctx["leaves"]:
        if rus:
            ob.location = (loc[0], loc[1], loc[2] + 0.02 * abs(math.sin(t * 17 + ph)))
            ob.rotation_euler = (0.25 * math.sin(t * 13 + ph), 0.25 * math.sin(t * 11 + ph * 2), ph)
        else:
            ob.location = loc
            ob.rotation_euler = (0, 0, ph)
    # ---- the teapot
    pour = _switch(_cues(tl, "pour"), "on", t, False)
    for ob in [ctx["pot_tip"]] + list(ctx["pot_tip"].children) + [ctx["stream"]]:
        ob.hide_render = (not pour) or room != "kitchen"
    for ob in [ctx["pot_up"]] + list(ctx["pot_up"].children):
        ob.hide_render = pour or room != "kitchen"
    # ---- the mugs in the hand
    mug_t = _cues(tl, "mug")
    for who in ("pell", "pell2", "me"):
        key = f"mug.{who}"
        mine = [c for c in mug_t if c.get("who") == who]
        on = bool(_switch(mine, "on", t, False))
        ob = bpy.data.objects.get(key)
        arm_o = bpy.data.objects.get(f"{who}.arm1")
        if on and arm_o is not None:
            if ob is None:
                ob = kit.cyl(key, 0.22, 0.46, (0, -0.1, -1.75), ctx["M"]["mugb"], arm_o, n=14)
                kit.cyl(key + ".in", 0.18, 0.02, (0, 0, 0.23), ctx["M"]["tea"], ob, n=14)
                kit.box(key + ".h", (0.08, 0.1, 0.26), (0.26, 0, 0), ctx["M"]["mugb"], ob)
            for o in [ob] + list(ob.children):
                o.hide_render = not active(ac.state(tl, who, t)["x"])
            ob.rotation_euler = (math.radians(_switch(mine, "raise", t, 0.0)), 0, 0)
        elif ob is not None:
            for o in [ob] + list(ob.children):
                o.hide_render = True
    animate_umbrellas(tl, t, ctx, story, active)
    animate_clouds(kit, story, tl, t, ctx, active)
    # ---- the wrapper on the floor, and rain through the open vent
    wr = _switch(_cues(tl, "wrapper"), "on", t, False)
    for ob in ctx["wrapper"]:
        ob.hide_render = (not wr) or room != "garden"
    vr = _switch(_cues(tl, "ventrain"), "on", t, False) and room == "garden"
    for i, d in enumerate(ctx["ventrain"]):
        d.hide_render = not vr
        if vr:
            ph = (t * 2.4 / 1.6 + kit.hash01(i, 4, 1)) % 1.0
            d.location = (GX + 1.55 + 0.75 * kit.hash01(i, 7, 2), 19.12 + 0.76 * kit.hash01(i, 1, 9), 3.2 - ph * 1.7)
    return over
