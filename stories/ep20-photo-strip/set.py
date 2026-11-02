"""The Third in the photo booth: a hotel hall on a wedding night, the old coin booth in its alcove, and the flat sepia
person who stands behind the bench in every strip.

Built from kit.py's parts (plus prints.py, which draws every photo strip). The hall runs along x (the ballroom door at
the far +x end, x = 19), 4 m wide (y -2 .. 2), with the booth in an alcove in its +y wall, centred on x = BX = 9. The
booth faces -y (the hall): its curtain is at y = 3.2, its back velvet at y = 4.76, with one vertical seam at x = BX.
People who sit in it face -y (yaw 0). The floor is z = 0 and the bench's top is z = 0.5.

THE CREATURE is the Third (never named on screen): a full person in an old dark three-piece suit, 2.7 m tall and
2 cm thick (flat: from the side it is one dark line), every part one sepia tone with grain, standing against the back
velvet with its right hand flat on the seam at ear height. `build_third()` makes it once; `animate()` only moves the
head, its smile, its arm and whether it is in the booth or in the hall.

Cues read here (set.py's animate; everything else is the engine's):
- lamp: {"to": 0..1, "dur": s}  the booth's dome lamp (0.4 at rest, a glow is a ramp to about 0.7 and back)
- curtain: {"to": [left_open, right_open], "dur": s}  0 closed, 1 pulled right back
- third: {"on": bool, "mode": "booth"|"hall", "x", "y", "yaw", "smile": "normal"|"wide", "head": deg, "roll": deg,
  "arm": "seam"|"down"}  the creature from here on (state carries forward)
- strip: {"id": "s1".."s5"|"s5a"|"s5b", "on": bool, "pos": [x, y, z], "rot": deg, "tilt": deg, "flip": bool,
  "from": [x, y, z], "dur": s}  a strip placed in the set (it slides from `from` over `dur`)
- midlamp / nearlamp / farlamp: {"to": 0..1, "dur": s}  the hall's brass lamps
- pools: {"on": bool}  a soft pool of light follows Wren and me (the hall's dark middle gets smaller as we meet)
- cake: {"from": [x, y], "to": [x, y], "dur": s}  the trolley
- shot: {"look": {...}}  one shot's own lights (see shot_look)
Story keys: "stage": {shot: [[strip, x, y, rot], ...]} lays strips on the far-away black table for insert shots;
"hide": {shot: [group, ...]} hides "curtain", "front", "wall_l", "wall_r" for that shot (a lens shot looks through them).
Acting keys read here (acting.py ignores them): "sit": true bends both legs forward; "bend": torso degrees forward.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector as V
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prints  # noqa: E402

from blocky import faces, rig  # noqa: E402

# ------------------------------------------------------------------------------------------------ the places
HX0, HX1, HY0, HY1, CEIL = -1.0, 19.0, -2.0, 2.0, 3.4
BX = 9.0                       # the booth's middle and its seam
IW = 1.34                      # inside half width
Y_CURT, Y_BACK, Y_VELVET = 3.2, 4.9, 4.76
BENCH_TOP = 0.5
STAGE = (40.0, 0.0)            # a black table far from the hall, for the insert shots
LAMP_X = (3.0, BX, 15.0)
DOME_W, HALL_W = 120.0, 210.0
TH = 0.02                      # the Third's thickness
HEAD_H = 0.62


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return [c for c in tl["cues"] if c["name"] == name]


def _switch(cs, attr, t, default):
    v = default
    for c in cs:
        if attr in c and c["t"] <= t + 1e-9:
            v = c[attr]
    return v


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


def _level(tl, name, t, default):
    """A value that ramps from cue to cue: each cue {"to", "dur"} starts at its time and gets there in dur."""
    v0, v = default, default
    for c in _cues(tl, name):
        if c["t"] > t + 1e-9:
            break
        d = max(1e-6, c.get("dur", 0.3))
        v0, v = v, c["to"]
        if t < c["t"] + d:
            return v0 + (v - v0) * _ss((t - c["t"]) / d)
    return v


def _level2(tl, name, t, default):
    out = []
    for i in range(2):
        v0 = v = default[i]
        for c in _cues(tl, name):
            if c["t"] > t + 1e-9:
                break
            d = max(1e-6, c.get("dur", 0.3))
            v0, v = v, c["to"][i]
            if t < c["t"] + d:
                v = v0 + (v - v0) * _ss((t - c["t"]) / d)
                break
        out.append(v)
    return out


# ------------------------------------------------------------------------------------------------ helpers


def wbox(kit, name, lo, hi, mat, parent=None):
    """A box from two world corners; object space is world space, so wood and paper line up from piece to piece."""
    c = tuple((a + b) / 2 for a, b in zip(lo, hi))
    s = tuple(b - a for a, b in zip(lo, hi))
    return kit.mesh_obj(name, kit.box_verts(*s, c), kit.BOX_FACES, mat, parent)


def uv_quad(kit, name, x0, y0, x1, y1, z, mat, tile):
    verts = [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
    ob = kit.mesh_obj(name, verts, [(0, 1, 2, 3)], mat)
    uv = ob.data.uv_layers.new(name="UVMap")
    uvs = [(x0 / tile, y0 / tile), (x1 / tile, y0 / tile), (x1 / tile, y1 / tile), (x0 / tile, y1 / tile)]
    for p in ob.data.polygons:
        for li in p.loop_indices:
            uv.data[li].uv = uvs[ob.data.loops[li].vertex_index]
    return ob


def img_mat(kit, name, pil, rough=0.6, emit=0.0):
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
    return m, img


def grain_mat(kit, name, c1, c2, scale=260.0, rough=0.85):
    """One faded sepia tone with a fine grain, like an old print (object space, so the grain stays put)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 2.0
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = kit.col(c1)
    ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[1].color = kit.col(c2)
    L.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    L.new(ramp.outputs["Color"], b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m


def carpet_image():
    rng = np.random.default_rng(3)
    n = 512
    im = Image.new("RGB", (n, n), (26, 20, 32))
    d = ImageDraw.Draw(im)
    for k in range(-1, 3):                       # the diamond lattice
        for sgn in (1, -1):
            for off in range(-n, 2 * n, n // 2):
                d.line([(off, 0), (off + sgn * n, n)] if sgn > 0 else [(off, n), (off + n, 0)], fill=(96, 36, 50), width=7)
    for cx in (0, n // 2, n):
        for cy in (0, n // 2, n):
            d.polygon([(cx, cy - 46), (cx + 46, cy), (cx, cy + 46), (cx - 46, cy)], fill=(58, 24, 40))
            d.polygon([(cx, cy - 20), (cx + 20, cy), (cx, cy + 20), (cx - 20, cy)], fill=(132, 104, 58))
    for cx in (n // 4, 3 * n // 4):
        for cy in (n // 4, 3 * n // 4):
            d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(112, 88, 52))
    a = np.asarray(im).astype(np.float32) + rng.normal(0, 4, (n, n, 3))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))


def third_face(wide):
    """The Third's face: two small black dots set too high and too far apart, no highlight, and a long thin smile cut
    as a dark slot that runs wider than the head should allow (it wraps past the face box, to the head's edges)."""
    rng = np.random.default_rng(5)
    s = faces.FX1 - faces.FX0
    skin = (158, 128, 96)
    im = Image.new("RGB", (faces.TEX_W, faces.TEX_H), skin)
    a = np.asarray(im).astype(np.float32) + rng.normal(0, 7, (faces.TEX_H, faces.TEX_W, 3))
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    cx = faces._fx(0.5)
    ey = faces._fy(0.20)
    # the eyes sit in soft dark hollows, like an old print gone brown around them
    hol = Image.new("L", im.size, 0)
    hd = ImageDraw.Draw(hol)
    for side in (-1, 1):
        x = cx + side * 0.30 * s
        hd.ellipse([x - 0.17 * s, ey - 0.2 * s, x + 0.17 * s, ey + 0.2 * s], fill=190)
    hd.ellipse([cx - 0.5 * s, faces._fy(0.80) - 0.1 * s, cx + 0.5 * s, faces._fy(0.80) + 0.2 * s], fill=70)
    hol = hol.filter(ImageFilter.GaussianBlur(0.07 * s))
    im = Image.composite(Image.new("RGB", im.size, (40, 26, 18)), im, hol)
    d = ImageDraw.Draw(im)
    for side in (-1, 1):
        x = cx + side * 0.30 * s
        d.ellipse([x - 0.04 * s, ey - 0.055 * s, x + 0.04 * s, ey + 0.055 * s], fill=(4, 3, 3))
    sw = (1.25 if wide else 0.92) * s
    th = (0.17 if wide else 0.115) * s
    bend = (0.2 if wide else 0.15) * s
    my = faces._fy(0.66)
    pts = [(cx - sw + 2 * sw * i / 40, my - bend * 0.5 + bend * (1 - (2 * i / 40 - 1) ** 2)) for i in range(41)]   # ends up, middle down
    # the slot: a long dark lens shape, thickest in the middle and fading to a hair at both ends
    top = [(x, y - th / 2 * math.sin(math.pi * i / 40) ** 0.6) for i, (x, y) in enumerate(pts)]
    bot = [(x, y + th / 2 * math.sin(math.pi * i / 40) ** 0.6) for i, (x, y) in enumerate(pts)]
    d.polygon(top + bot[::-1], fill=(4, 3, 3))
    return im.filter(ImageFilter.SMOOTH)


# ------------------------------------------------------------------------------------------------ materials


def materials(kit):
    M = {}
    M["carpet"], _ = img_mat(kit, "carpet", carpet_image(), 0.9)
    M["wall"] = kit.grime("#1d3a2c", 0.74, 3.0, "wall green", 0.85)
    M["dado"] = kit.planks("#4a2f1c", "#2f1c10", 1.0, "Z", "dado")
    M["ceil"] = kit.grime("#5e564a", 0.6, 2.0, "ceiling", 0.9)
    M["brass"] = kit.metal("#c8963c", 0.3, "brass")
    M["wood"] = kit.planks("#3d2517", "#26150a", 1.0, "Z", "booth wood", 0.7)
    M["floor"] = kit.planks("#4a3020", "#2c1a0e", 1.0, "X", "booth floor", 0.6)
    M["velvet"] = kit.grime("#4c1c3c", 0.55, 16.0, "plum velvet", 0.96)
    M["seam"] = kit.plastic("#2a0f22", 0.95, "seam", 0.0)
    M["leather"] = kit.plastic("#3b2820", 0.5, "bench", 0.3)
    M["black"] = kit.plastic("#050404", 0.2, "black", 0.8)
    M["slot"] = kit.plastic("#020202", 0.9, "slot", 0.0)
    M["cake"] = kit.plastic("#eeeae0", 0.6, "cake", 0.2)
    M["icing"] = kit.plastic("#e9b9c4", 0.6, "icing", 0.2)
    M["trolley"] = kit.metal("#b9b4a8", 0.35, "trolley")
    M["paper"] = kit.plastic("#ece6d8", 0.7, "paper", 0.1)
    M["stage"] = kit.planks("#1c1410", "#120c08", 2.0, "X", "stage", 0.6)
    M["door"] = kit.planks("#5a3a22", "#3c2414", 1.0, "Z", "ballroom door", 0.6)
    M["door_glow"] = kit.emit("#ffb86a", 3.0, "door glow")
    M["suit"] = grain_mat(kit, "suit", "#2e2015", "#43321f")
    M["suit2"] = grain_mat(kit, "suit2", "#4a3826", "#5f4a32")
    M["sepia_skin"] = grain_mat(kit, "sepia skin", "#a08462", "#bd9f7c")
    M["shirt3"] = grain_mat(kit, "shirt3", "#7d6a4c", "#917c5a")
    M["ink"] = kit.plastic("#120c08", 0.9, "ink", 0.0)
    # the curtain and the lamp share glows driven from animate()
    m = kit._new("curtain")
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col("#5a2448")
    b.inputs["Roughness"].default_value = 0.95
    b.inputs["Emission Color"].default_value = kit.col("#d4683e")
    b.inputs["Emission Strength"].default_value = 0.0
    kit._fogged(m, b.outputs[0])
    M["curtain"], M["curtain_bsdf"] = m, b
    shade = kit._new("hall shade")
    nt = shade.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col("#ffcf90")
    em.inputs["Strength"].default_value = 3.0
    kit._fogged(shade, em.outputs[0])
    M["shade_proto"] = em
    return M


def emit_mat(kit, name, hexc, strength):
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col(hexc)
    em.inputs["Strength"].default_value = strength
    kit._fogged(m, em.outputs[0])
    try:
        m.emission_sampling = "NONE"
    except Exception:
        pass
    return m, em


# ------------------------------------------------------------------------------------------------ the hall


def build_hall(kit, ctx, M):
    G = ctx["groups"]
    uv_quad(kit, "carpet", HX0, HY0, HX1, HY1, 0.0, M["carpet"], 1.3)
    wbox(kit, "alcove floor", (BX - 2.2, 2.0, -0.04), (BX + 2.2, Y_BACK, 0.0), M["floor"])
    wbox(kit, "ceiling", (HX0 - 0.3, HY0 - 0.3, CEIL), (HX1 + 0.3, 5.3, CEIL + 0.1), M["ceil"])
    # the long front wall, the two ends, the +y wall either side of the alcove
    wbox(kit, "wall front", (HX0 - 0.3, HY0 - 0.3, 0), (HX1 + 0.3, HY0, CEIL), M["wall"])
    wbox(kit, "wall near", (HX0 - 0.3, HY0 - 0.3, 0), (HX0, 5.3, CEIL), M["wall"])
    wbox(kit, "wall far", (HX1, HY0 - 0.3, 0), (HX1 + 0.3, 5.3, CEIL), M["wall"])
    wbox(kit, "wall back a", (HX0 - 0.3, HY1, 0), (BX - 2.2, HY1 + 0.3, CEIL), M["wall"])
    wbox(kit, "wall back b", (BX + 2.2, HY1, 0), (HX1 + 0.3, HY1 + 0.3, CEIL), M["wall"])
    wbox(kit, "alcove wall l", (BX - 2.4, HY1, 0), (BX - 2.2, 5.3, CEIL), M["wall"])
    wbox(kit, "alcove wall r", (BX + 2.2, HY1, 0), (BX + 2.4, 5.3, CEIL), M["wall"])
    wbox(kit, "alcove back", (BX - 2.4, Y_BACK, 0), (BX + 2.4, 5.3, CEIL), M["wall"])
    # dado panelling and a brass picture rail's worth of trim, so the long walls aren't one flat green
    wbox(kit, "dado front", (HX0, HY0, 0), (HX1, HY0 + 0.05, 1.0), M["dado"])
    wbox(kit, "dado a", (HX0, HY1 - 0.05, 0), (BX - 2.2, HY1, 1.0), M["dado"])
    wbox(kit, "dado b", (BX + 2.2, HY1 - 0.05, 0), (HX1, HY1, 1.0), M["dado"])
    wbox(kit, "rail front", (HX0, HY0, 1.0), (HX1, HY0 + 0.07, 1.05), M["brass"])
    wbox(kit, "rail a", (HX0, HY1 - 0.07, 1.0), (BX - 2.2, HY1, 1.05), M["brass"])
    wbox(kit, "rail b", (BX + 2.2, HY1 - 0.07, 1.0), (HX1, HY1, 1.05), M["brass"])
    wbox(kit, "cornice", (HX0, HY0, CEIL - 0.12), (HX1, HY0 + 0.1, CEIL), M["ceil"])
    # the ballroom door at the far end: closed, with the party's light round its edges
    wbox(kit, "door frame", (HX1 - 0.22, -1.1, 0), (HX1, 1.1, 2.7), M["wood"])
    wbox(kit, "door leaf l", (HX1 - 0.18, -1.0, 0), (HX1 - 0.12, -0.012, 2.6), M["door"])
    wbox(kit, "door leaf r", (HX1 - 0.18, 0.012, 0), (HX1 - 0.12, 1.0, 2.6), M["door"])
    for nm, lo, hi in (("bottom", (HX1 - 0.19, -1.0, 0.0), (HX1 - 0.17, 1.0, 0.035)),
                       ("mid", (HX1 - 0.19, -0.012, 0.0), (HX1 - 0.17, 0.012, 2.6)),
                       ("top", (HX1 - 0.19, -1.0, 2.585), (HX1 - 0.17, 1.0, 2.6)),
                       ("l", (HX1 - 0.19, -1.01, 0.0), (HX1 - 0.17, -0.99, 2.6)),
                       ("r", (HX1 - 0.19, 0.99, 0.0), (HX1 - 0.17, 1.01, 2.6))):
        wbox(kit, f"door glow {nm}", lo, hi, M["door_glow"])
    # three brass wall lamps on the long front wall; the middle one over a small side table
    ctx["shades"] = []
    for i, x in enumerate(LAMP_X):
        wbox(kit, f"lamp{i} plate", (x - 0.09, HY0, 2.0), (x + 0.09, HY0 + 0.03, 2.6), M["brass"])
        arm = kit.cyl(f"lamp{i} arm", 0.012, 0.28, (x, HY0 + 0.15, 2.18), M["brass"], rot=(math.pi / 2, 0, 0))
        mat, em = emit_mat(kit, f"lamp{i} shade", "#ffcf90", 3.0)
        kit.cyl(f"lamp{i} shade", 0.1, 0.3, (x, HY0 + 0.3, 2.3), mat, n=16, r2=0.075)
        kit.cyl(f"lamp{i} cap", 0.105, 0.025, (x, HY0 + 0.3, 2.14), M["brass"], n=16)
        ctx["shades"].append(em)
        kit.light(f"lamp{i}", "POINT", (x, HY0 + 0.45, 2.3), HALL_W, "#ffb86a", size=0.12)
    tx, ty = BX, HY0 + 0.55
    kit.cyl("table top", 0.58, 0.04, (tx, ty, 0.78), M["wood"], n=28)
    kit.cyl("table stem", 0.06, 0.74, (tx, ty, 0.39), M["wood"], n=12)
    kit.cyl("table foot", 0.3, 0.03, (tx, ty, 0.015), M["wood"], n=24)
    ctx["table"] = (tx, ty, 0.8)
    # light from the ballroom, a faint cool fill under the ceiling, and the table's lamp already above
    kit.light("door", "AREA", (HX1 - 0.9, 0.0, 0.9), 220.0, "#ffb86a", size=1.2)
    kit.aim(kit.LIGHTS["door"]["obj"], (HX1 - 6.0, 0.0, 0.5))
    kit.light("hallfill", "AREA", (9.0, 0.0, CEIL - 0.1), 140.0, "#9fb0d8", size=6.0)
    kit.aim(kit.LIGHTS["hallfill"]["obj"], (9.0, 0.0, 0.0))
    for nm in ("pool_w", "pool_m"):
        kit.light(nm, "POINT", (0, 0, 2.6), 0.0, "#ffc888", size=0.4)
    # the cake trolley that passes the ballroom door (blank white cake, no topper)
    cake = kit.empty("cake", (HX1 - 1.5, -1.4, 0))
    ctx["cake"] = cake
    kit.box("cake deck", (0.9, 0.6, 0.04), (0, 0, 0.78), M["trolley"], cake, bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"cake leg{sx}{sy}", 0.02, 0.72, (sx * 0.4, sy * 0.25, 0.4), M["trolley"], cake, n=8)
            kit.cyl(f"cake wheel{sx}{sy}", 0.05, 0.03, (sx * 0.4, sy * 0.25, 0.05), M["black"], cake, rot=(0, math.pi / 2, 0), n=12)
    for k, (r, h, z) in enumerate(((0.34, 0.2, 0.9), (0.25, 0.18, 1.09), (0.16, 0.16, 1.26))):
        kit.cyl(f"cake tier{k}", r, h, (0, 0, z), M["cake"], cake, n=28)
        kit.cyl(f"cake icing{k}", r + 0.012, 0.03, (0, 0, z - h / 2 + 0.04), M["icing"], cake, n=28)
    kit.sphere("cake top", 0.05, (0, 0, 1.38), M["icing"], cake, 12)
    return ctx


# ------------------------------------------------------------------------------------------------ the booth


def build_booth(kit, ctx, M):
    G = ctx["groups"]
    wbox(kit, "booth floor", (BX - IW, Y_CURT - 0.1, 0.0), (BX + IW, Y_VELVET, 0.012), M["floor"])
    wbox(kit, "back panel", (BX - IW - 0.1, Y_VELVET, 0), (BX + IW + 0.1, Y_BACK, 3.0), M["wood"])
    wbox(kit, "velvet l", (BX - IW, Y_VELVET - 0.02, 0.45), (BX - 0.004, Y_VELVET, 2.78), M["velvet"])
    wbox(kit, "velvet r", (BX + 0.004, Y_VELVET - 0.02, 0.45), (BX + IW, Y_VELVET, 2.78), M["velvet"])
    wbox(kit, "seam", (BX - 0.006, Y_VELVET - 0.024, 0.45), (BX + 0.006, Y_VELVET - 0.016, 2.78), M["seam"])
    wbox(kit, "bench base", (BX - IW, 3.95, 0.0), (BX + IW, Y_VELVET - 0.02, 0.42), M["wood"])
    wbox(kit, "bench seat", (BX - IW, 3.93, 0.42), (BX + IW, Y_VELVET - 0.02, BENCH_TOP), M["leather"])
    ctx["bench_front"] = 3.93
    wl = wbox(kit, "wall l", (BX - 1.44, 3.25, 0), (BX - IW, Y_BACK, 3.0), M["wood"])
    wr = wbox(kit, "wall r", (BX + IW, 3.25, 0), (BX + 1.44, Y_BACK, 3.0), M["wood"])
    G["wall_l"], G["wall_r"] = [wl], [wr]
    roof = wbox(kit, "roof", (BX - 1.44, 3.1, 2.9), (BX + 1.44, Y_BACK, 3.0), M["wood"])
    front = [
        wbox(kit, "pillar l", (BX - 1.74, 3.1, 0), (BX - IW, 3.25, 3.0), M["wood"]),
        wbox(kit, "pillar r", (BX + IW, 3.1, 0), (BX + 1.74, 3.25, 3.0), M["wood"]),
        wbox(kit, "header", (BX - IW, 3.1, 2.5), (BX + IW, 3.25, 3.0), M["wood"]),
        wbox(kit, "header trim", (BX - IW, 3.08, 2.48), (BX + IW, 3.1, 2.52), M["brass"]),
        wbox(kit, "coin plate", (BX + 1.4, 3.085, 1.3), (BX + 1.7, 3.1, 1.8), M["brass"]),
        wbox(kit, "coin slot", (BX + 1.5, 3.078, 1.5), (BX + 1.62, 3.086, 1.525), M["slot"]),
        wbox(kit, "delivery tray", (BX + 1.42, 2.97, 0.86), (BX + 1.68, 3.1, 0.98), M["brass"]),
        wbox(kit, "delivery slot", (BX + 1.44, 2.965, 0.9), (BX + 1.66, 2.975, 0.955), M["slot"]),
        kit.cyl("rail", 0.016, 2.8, (BX, 3.15, 2.46), M["brass"], rot=(0, math.pi / 2, 0), n=10),
    ]
    G["front"] = front
    # the lens and the dome lamp above it (on the header's inner face, looking at the bench)
    kit.cyl("lens ring", 0.1, 0.03, (BX, 3.27, 2.66), M["brass"], rot=(math.pi / 2, 0, 0), n=20)
    kit.cyl("lens", 0.075, 0.04, (BX, 3.275, 2.66), M["black"], rot=(math.pi / 2, 0, 0), n=20)
    mat, em = emit_mat(kit, "dome", "#ffc27a", 6.0)
    kit.sphere("dome", 0.15, (BX, 3.55, 2.9), mat, seg=16)
    ctx["dome_em"] = em
    kit.light("dome", "POINT", (BX, 3.6, 2.7), DOME_W, "#ffb86a", size=0.15)
    # the curtain: two halves that bunch toward the pillars; plum, a rail, and a glow that comes through it
    ctx["curtain"] = []
    ctx["glow_out"] = None
    curt = []
    for side in (-1, 1):
        piv = kit.empty(f"curtain{side}", (BX + side * IW, 3.185, 0))
        w = IW
        curt.append(kit.box(f"curtain{side}.cloth", (w, 0.045, 1.9), (-side * w / 2, 0, 1.5), M["curtain"], piv))
        for k in range(1, 9):
            curt.append(kit.box(f"curtain{side}.fold{k}", (0.05, 0.03, 1.9), (-side * (w * k / 9), -0.025, 1.5), M["curtain"], piv,
                                bevel=0.012))
        ctx["curtain"].append(piv)
        curt.append(piv)
    G["curtain"] = curt
    kit.light("glow_out", "AREA", (BX, 2.5, 1.0), 0.0, "#ff9a58", size=2.0)
    kit.aim(kit.LIGHTS["glow_out"]["obj"], (BX, 0.0, 0.6))
    kit.light("booth_fill", "AREA", (BX, 3.5, 0.9), 14.0, "#ffcf9a", size=1.4)   # a little bounce off the floor
    kit.aim(kit.LIGHTS["booth_fill"]["obj"], (BX, 4.7, 1.6))
    kit.light("third_rim", "SPOT", (BX + 0.9, 1.2, 1.4), 0.0, "#9db4ff", size=0.1, spot=40, blend=0.5)


# ------------------------------------------------------------------------------------------------ the Third


def build_third(kit, ctx, M):
    """One model: flat (2 cm), 2.7 m, a dark three-piece suit and a sepia face. Built once, posed per shot."""
    root = kit.empty("third", (BX, Y_VELVET - 0.015, 0.0))
    ctx["third"] = root

    def part(name, cx, cz, w, h, mat, parent=root, bevel=0.0, layer=0):
        # each layer stands 2 mm proud of the one under it, so nothing is coplanar (no z-fighting, still 2 cm thin)
        return kit.box(name, (w, TH, h), (cx, -0.002 * layer, cz), mat, parent, bevel=bevel)

    for sx in (-1, 1):
        part(f"third.leg{sx}", sx * 0.15, 0.575, 0.24, 1.15, M["suit"])
        part(f"third.shoe{sx}", sx * 0.15, 0.04, 0.27, 0.08, M["ink"])
    part("third.torso", 0, 1.6, 0.62, 0.95, M["suit"], bevel=0.004)
    part("third.vest", 0, 1.58, 0.26, 0.93, M["suit2"], layer=1)
    part("third.shirt", 0, 2.0, 0.12, 0.2, M["shirt3"], layer=2)
    part("third.tie", 0, 1.74, 0.035, 0.5, M["ink"], layer=3)
    part("third.neck", 0, 2.17, 0.14, 0.2, M["sepia_skin"], layer=1)
    # the left arm hangs; the right arm is two pieces with an elbow, so its hand can rest on the seam
    lsh = kit.empty("third.larm", (0.31, -0.012, 2.0), root)
    kit.box("third.larm.sleeve", (0.17, TH, 1.1), (0.085, 0, -0.55), M["suit"], lsh, bevel=0.004)
    kit.box("third.larm.hand", (0.15, TH, 0.18), (0.085, 0, -1.19), M["sepia_skin"], lsh)
    L1, L2 = 0.588, 0.52
    rsh = kit.empty("third.rsh", (-0.31, -0.012, 2.0), root)
    kit.box("third.rsh.upper", (0.2, TH, L1 + 0.05), (0, 0, -L1 / 2), M["suit"], rsh, bevel=0.004)
    rel = kit.empty("third.rel", (0, 0, -L1), rsh)
    kit.box("third.rel.joint", (0.2, TH, 0.2), (0, 0, 0), M["suit"], rel, bevel=0.004)
    kit.box("third.rel.fore", (0.18, TH, L2), (0, 0, -L2 / 2), M["suit"], rel, bevel=0.004)
    kit.box("third.rel.cuff", (0.19, TH * 1.2, 0.07), (0, 0, -L2 + 0.035), M["shirt3"], rel)
    kit.box("third.rel.palm", (0.2, TH, 0.17), (0, 0, -L2 - 0.085), M["sepia_skin"], rel, bevel=0.003)
    for k, (dz, ln) in enumerate(((0.085, 0.19), (0.027, 0.235), (-0.031, 0.215), (-0.087, 0.16))):
        kit.box(f"third.rel.f{k}", (0.042, TH, ln), (dz, 0, -L2 - 0.17 - ln / 2), M["sepia_skin"], rel, bevel=0.003)
    kit.box("third.rel.thumb", (0.05, TH, 0.11), (0.12, 0, -L2 - 0.07), M["sepia_skin"], rel, rot=(0, 0.35, 0))
    ctx["rsh"], ctx["rel"] = rsh, rel
    # the head: the rig's soft rounded cylinder, squashed flat, on a neck pivot so it alone can turn
    neck = kit.empty("third.neckpivot", (0, 0, 2.2), root)
    ctx["tneck"] = neck
    headg = kit.empty("third.headg", (0, 0, HEAD_H / 2 + 0.02), neck)
    k = HEAD_H / faces.HEAD_H
    headg.scale = (k * 0.62, TH / (2 * faces.HEAD_R), k)
    hm, tex = rig.head_material("third", "#b59878")
    rig.head_mesh("third.headm", hm, headg)
    ctx["tface"] = tex
    ctx["tface_img"] = {}
    for wide in (False, True):
        pil = third_face(wide)
        img = bpy.data.images.new(f"third face {wide}", pil.width, pil.height, alpha=False)
        a = np.asarray(pil.convert("RGBA")).astype(np.float32)[::-1] / 255
        img.pixels.foreach_set(a.ravel())
        img.pack()
        ctx["tface_img"][wide] = img
    tex.image = ctx["tface_img"][False]
    ctx["third_objs"] = [root] + list(root.children_recursive)


# ------------------------------------------------------------------------------------------------ the prints


def build_strips(kit, ctx, M):
    """The strips: five whole strips and the last strip's two halves (the second half's back carries the tally)."""
    ctx["strips"] = {}
    W = 0.2

    def make(sid, pil, back_pil):
        ratio = pil.height / pil.width
        h = W * ratio
        mf, _ = img_mat(kit, f"print {sid}", pil, 0.4)
        mb, _ = img_mat(kit, f"print {sid} back", back_pil.resize((pil.width, pil.height)), 0.7)
        root = kit.empty(f"strip {sid}", (STAGE[0], 20.0, 0.0))
        for face, mat, z, flip in (("front", mf, 0.0006, False), ("back", mb, -0.0006, True)):
            verts = [(-W / 2, -h / 2, z), (W / 2, -h / 2, z), (W / 2, h / 2, z), (-W / 2, h / 2, z)]
            fc = [(0, 1, 2, 3)] if not flip else [(3, 2, 1, 0)]
            ob = kit.mesh_obj(f"strip {sid} {face}", verts, fc, mat, root)
            uvs = [(0, 0), (1, 0), (1, 1), (0, 1)] if not flip else [(1, 0), (0, 0), (0, 1), (1, 1)]
            uv = ob.data.uv_layers.new(name="UVMap")
            for p in ob.data.polygons:
                for li in p.loop_indices:
                    uv.data[li].uv = uvs[ob.data.loops[li].vertex_index]
        ctx["strips"][sid] = root
        ctx.setdefault("strip_h", {})[sid] = h

    plain = prints.back(False)
    for n in range(1, 5):
        make(f"s{n}", prints.strip(n), plain)
    make("s5", prints.strip(5), plain)
    make("s5a", prints.strip(5, (0, 1)), plain)
    make("s5b", prints.strip(5, (2, 3)), prints.back(True))
    # the black table the inserts are laid on
    kit.mesh_obj("stage", kit.box_verts(5.0, 3.0, 0.1, (STAGE[0], STAGE[1], -0.05)), kit.BOX_FACES, M["stage"])
    kit.light("stage", "AREA", (STAGE[0] - 0.1, STAGE[1] - 0.25, 1.1), 22.0, "#fff0dc", size=1.3)
    kit.aim(kit.LIGHTS["stage"]["obj"], (STAGE[0], STAGE[1], 0.0))


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    ctx = {"groups": {}}
    M = materials(kit)
    ctx["M"] = M
    build_hall(kit, ctx, M)
    build_booth(kit, ctx, M)
    build_third(kit, ctx, M)
    build_strips(kit, ctx, M)
    for nm in ("key", "key2", "under"):
        kit.light(nm, "SPOT", (0, 0, 1), 0.0, "#ffd2a0", size=0.06, spot=40, blend=0.6)
    return ctx


# ------------------------------------------------------------------------------------------------ the pieces that move


def _extras(ctx):
    """Wren's brass hair clip and the pocket on my jacket, once the cast exists (the rig has no such parts)."""
    if ctx.get("extras"):
        return
    ctx["extras"] = True
    M = ctx["M"]
    from blocky import kit

    hg = bpy.data.objects.get("wren.headg")
    if hg is not None:
        kit.box("wren.clip", (0.3, 0.1, 0.12), (0.45, -0.52, 0.28), M["brass"], hg, rot=(0, 0, 0.3), bevel=0.02)
    tor = bpy.data.objects.get("me.torso")
    if tor is not None:
        kit.box("me.pocket", (0.5, 0.06, 0.42), (0.5, -0.52, 1.55), kit.plastic("#2e3a5c", 0.7, "pocket"), tor, bevel=0.03)
        ctx["pocket_strip"] = kit.box("me.pocket.strip", (0.36, 0.03, 0.7), (0.5, -0.55, 1.95), M["paper"], tor, bevel=0.01)
        ctx["pocket_strip"].hide_render = True


def _third_state(tl, t):
    s = {"on": False, "mode": "booth", "x": BX, "y": Y_VELVET - 0.015, "yaw": 0.0, "smile": "normal", "head": 0.0,
         "roll": 0.0, "arm": "seam"}
    for c in _cues(tl, "third"):
        if c["t"] <= t + 1e-9:
            for k in s:
                if k in c:
                    s[k] = c[k]
    return s


def place_third(ctx, tl, t):
    s = _third_state(tl, t)
    root = ctx["third"]
    for ob in ctx["third_objs"]:
        ob.hide_render = not s["on"]
    if not s["on"]:
        return s
    if s["mode"] == "booth":
        root.location = (BX, Y_VELVET - 0.015, 0.0)
        root.rotation_euler = (0, 0, 0)
    else:
        root.location = (s["x"], s["y"], 0.0)
        root.rotation_euler = (0, 0, math.radians(s["yaw"]))
    if s["arm"] == "seam":
        ctx["rsh"].rotation_euler = (0, math.atan2(0.31, 0.5), 0)
        ctx["rel"].rotation_euler = (0, -math.pi / 2 - math.atan2(0.31, 0.5), 0)
    else:
        ctx["rsh"].rotation_euler = (0, 0, 0)
        ctx["rel"].rotation_euler = (0, 0, 0)
    ctx["tneck"].rotation_euler = (0, math.radians(s["roll"]), math.radians(s["head"]))
    ctx["tface"].image = ctx["tface_img"][s["smile"] == "wide"]
    return s


def place_strips(ctx, story, tl, t, shot):
    state = {}
    for c in _cues(tl, "strip"):
        if c["t"] <= t + 1e-9:
            state[c["id"]] = c
    stage = {e[0]: e for e in story.get("stage", {}).get(shot, [])}
    for sid, ob in ctx["strips"].items():
        if sid in stage:
            _, x, y, rz = stage[sid][:4]
            ob.hide_render = False
            ob.location = (STAGE[0] + x, STAGE[1] + y, 0.004)
            ob.rotation_euler = (0, 0, math.radians(rz))
            continue
        c = state.get(sid)
        if not c or not c.get("on", True):
            ob.hide_render = True
            ob.location = (STAGE[0], 20.0, 0.0)
            for ch in ob.children:
                ch.hide_render = True
            continue
        ob.hide_render = False
        for ch in ob.children:
            ch.hide_render = False
        pos = V(c["pos"])
        if "from" in c:
            u = _ss((t - c["t"]) / max(1e-6, c.get("dur", 0.6)))
            pos = V(c["from"]).lerp(pos, u)
        ob.location = pos
        ob.rotation_euler = (math.radians(c.get("tilt", 0)) + (math.pi if c.get("flip") else 0), 0, math.radians(c.get("rot", 0)))
    for sid, ob in ctx["strips"].items():
        for ch in ob.children:
            ch.hide_render = ob.hide_render


# ------------------------------------------------------------------------------------------------ animate


def animate(kit, story, tl, t, ctx):
    from blocky import acting as ac
    from blocky import kit as K

    _extras(ctx)
    over = {}
    for nm in ("mum.gl-1", "mum.gl1"):   # the rig's lenses render black; keep the frames (pose() unhides them each frame)
        ob = bpy.data.objects.get(nm)
        if ob is not None:
            ob.hide_render = True
    shot = _shot(tl, t)["id"]
    # ---- people: sitting, bending at the hips
    for who, keys in tl["acting"].items():
        tor = bpy.data.objects.get(f"{who}.torso")
        if tor is not None:
            tor.rotation_euler = (math.radians(ac._held(keys, "bend", t, 0.0)), 0, 0)
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg is not None and _switch(keys, "sit", t, False):
                leg.rotation_euler = (-math.pi / 2, 0, 0)
    if ctx.get("pocket_strip") is not None:
        ctx["pocket_strip"].hide_render = not _switch(_cues(tl, "pocket"), "on", t, False)
    # ---- what this shot hides (a lens shot looks through the curtain and the booth's front)
    hide = set(story.get("hide", {}).get(shot, []))
    for g, obs in ctx["groups"].items():
        for ob in obs:
            ob.hide_render = g in hide
    # ---- the curtain
    lo = _level2(tl, "curtain", t, [0.0, 0.0])
    closed = 1.0 - 0.5 * (lo[0] + lo[1])
    for piv, o in zip(ctx["curtain"], lo):
        piv.scale = (max(0.12, 1.0 - 0.9 * o), 1, 1)
    # ---- the dome lamp and every glow it makes: the lamp, the curtain lit from within, the light under it
    lv = _level(tl, "lamp", t, 0.4)
    over["dome"] = lv
    ctx["dome_em"].inputs["Strength"].default_value = 7.0 * lv
    ctx["M"]["curtain_bsdf"].inputs["Emission Strength"].default_value = 1.7 * max(0.0, lv - 0.38) * closed
    K.LIGHTS["glow_out"]["base"] = 70.0
    over["glow_out"] = max(0.0, lv - 0.38) * closed
    over["booth_fill"] = 0.35 + lv
    # ---- the hall's lamps
    lamp_levels = []
    for i, nm in enumerate(("nearlamp", "midlamp", "farlamp")):
        g = _level(tl, nm, t, 1.0)
        over[f"lamp{i}"] = g
        ctx["shades"][i].inputs["Strength"].default_value = 3.0 * g
    # ---- the pools of light that follow Wren and me while the hall's middle is dark
    on = _switch(_cues(tl, "pools"), "on", t, False)
    for nm, who in (("pool_w", "wren"), ("pool_m", "me")):
        if on and who in tl["acting"]:
            s = ac.state(tl, who, t)
            ob = K.LIGHTS[nm]["obj"]
            ob.location = (s["x"], s["y"] - 0.2, 2.3)
            K.LIGHTS[nm]["base"] = 70.0
            over[nm] = 1.0
        else:
            over[nm] = 0.0
    # ---- the cake trolley
    cc = [c for c in _cues(tl, "cake") if c["t"] <= t + 1e-9]
    if cc:
        c = cc[-1]
        u = min(1.0, max(0.0, (t - c["t"]) / max(1e-6, c.get("dur", 2.0))))
        ctx["cake"].location = (c["from"][0] + (c["to"][0] - c["from"][0]) * u, c["from"][1] + (c["to"][1] - c["from"][1]) * u, 0)
    # ---- the Third, the strips
    third = place_third(ctx, tl, t)
    place_strips(ctx, story, tl, t, shot)
    shot_look(kit, tl, t, ctx, over, third)
    return over


def shot_look(kit, tl, t, ctx, over, third):
    """One shot's own light, from a "shot" cue's `look` (on at the shot's first frame, off with {"look": null} at its
    last). Keys: dome, hall, fill: gains on the booth lamp, the brass lamps and the hall's fill; door: the ballroom light;
    key, key2, under, third_rim: [pos, aim, watts, cone degrees?, colour?] a spot put exactly there ("head" or "hand"
    for aim means the Third's head or hand)."""
    from blocky import kit as K

    look = _switch(_cues(tl, "shot"), "look", t, None)
    for nm in ("key", "key2", "under", "third_rim"):
        over[nm] = 0.0
    if not look:
        return
    if "dome" in look:
        over["dome"] = over.get("dome", 1.0) * look["dome"]
    if "hall" in look:
        for i in range(3):
            over[f"lamp{i}"] = over.get(f"lamp{i}", 1.0) * look["hall"]
        over["door"] = over.get("door", 1.0) * look["hall"]
    if "fill" in look:
        over["hallfill"] = look["fill"]
        over["booth_fill"] = over.get("booth_fill", 1.0) * look["fill"]
    if "door" in look:
        over["door"] = look["door"]
    heads = {"head": (BX, Y_VELVET - 0.02, 2.35), "hand": (BX, Y_VELVET - 0.02, 1.5)}
    for nm in ("key", "key2", "under", "third_rim"):
        if nm not in look:
            continue
        pos, aim, watts = look[nm][:3]
        if isinstance(aim, str):
            aim = heads[aim]
        ob = K.LIGHTS[nm]["obj"]
        ob.location = pos
        ob.rotation_euler = (V(aim) - V(pos)).to_track_quat("-Z", "Y").to_euler()
        K.LIGHTS[nm]["base"] = watts
        if len(look[nm]) > 3:
            K.LIGHTS[nm]["light"].spot_size = math.radians(look[nm][3])
        K.LIGHTS[nm]["light"].color = K.col(look[nm][4] if len(look[nm]) > 4 else "#ffd2a0")[:3]
        over[nm] = 1.0
