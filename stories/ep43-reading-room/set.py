"""Days Since You Last LAUGHED (ep43, the reading room): a town where the glowing number over your head is the days since
you last laughed, a round domed reading room, and the Negative (a person printed in reverse, no number, an upside-down grin).

Three scenes, each in its own patch of the Blender world (story["scenes"]); animate() shows only the current shot's scene:
  room (0,0)    the round reading room, radius 8.6: the arched window in the west wall (x = -8.5), the stacks along the
                east wall, a glass dome of plain square panes, tables W (the window table, Tam and me), M, B, C, D, N, P
  door (500,0)  the mailman's doorstep     street (700,0)  a sunny street
THE CREATURE is the Negative ("neg" in the cast): a normal R6 person printed in reverse (black skin, white face strokes,
white hair, library-green jumper, no number). Its mouth is a story-local decal (grin_image, curved_decal) bent onto the
head, because its face spec says "mouth": "none". Its size is the negscale cue (1.00, 1.10, 1.20), changed only on a cut.

Cues read here: num {who, v, snap?} (the number over a head; a change rolls in 0.4 s), lamps {to, dur} (the closing
timer), dome {to, dur}, dead {tables}, page {dur}, negscale {v}, phone {pos, yaw}, pencil {} (Tam's pencil falls).
Acting keys read here (acting.py ignores them): "sit": true bends both legs forward; "bend": torso degrees forward.
Nothing in the film carries a letter or a word: the only symbols are the glowing numbers.
"""

from __future__ import annotations

import math

import bpy
import numpy as np
from mathutils import Vector as V
from PIL import Image, ImageDraw

from blocky import faces, rig  # noqa: F401

SEAT_TOP = 0.38
NUM_PITCH = 0.31
NUM_H = 0.36
NUM_W = 0.24
NUM_T = 0.052
NUM_O = 0.08 * NUM_H          # the dark outline: 8% of the glyph's height
NUM_LIFT = 2.2                # centre of the number above the feet
NUM_GLOW = 3.4
ROOM_BOOST = 1.0
ROOM_EV = 0.9      # extra exposure in the reading room by day (dome level 1); the dark scene's dome level is 0.12
LAMP_BOOST = 0.5


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _cues(tl, name):
    return sorted((c for c in tl["cues"] if c["name"] == name), key=lambda c: c["t"])


def _last(cs, t):
    out = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            out = c
    return out


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


def _shot(tl, t):
    for s in tl["shots"]:
        if s["start"] <= t < s["end"]:
            return s
    return tl["shots"][-1]


# ------------------------------------------------------------------------------------------------ mesh helpers


def mbox(kit, name, boxes, mat, parent=None):
    """Many axis-aligned boxes (cx, cy, cz, sx, sy, sz) in ONE mesh."""
    verts, faces_ = [], []
    for cx, cy, cz, sx, sy, sz in boxes:
        base = len(verts)
        verts += kit.box_verts(sx, sy, sz, (cx, cy, cz))
        faces_ += [tuple(base + i for i in f) for f in kit.BOX_FACES]
    return kit.mesh_obj(name, verts, faces_, mat, parent)


def wbox(kit, name, lo, hi, mat, parent=None):
    c = tuple((a + b) / 2 for a, b in zip(lo, hi))
    s = tuple(b - a for a, b in zip(lo, hi))
    return kit.mesh_obj(name, kit.box_verts(*s, c), kit.BOX_FACES, mat, parent)


def emission(kit, name, hexc, strength):
    """An emissive material the caller can retune each frame (returns (material, strength input))."""
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col(hexc)
    em.inputs["Strength"].default_value = strength
    kit._fogged(m, em.outputs[0])
    return m, em


def img_mat(kit, name, pil, rough=0.7):
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
    kit._fogged(m, b.outputs[0])
    return m


def quad_uv(kit, name, size, loc, mat, parent=None, rot=(0, 0, 0)):
    w, h = size[0] / 2, size[1] / 2
    ob = kit.mesh_obj(name, [(-w, -h, 0), (w, -h, 0), (w, h, 0), (-w, h, 0)], [(0, 1, 2, 3)], mat, parent, loc, rot)
    uv = ob.data.uv_layers.new(name="UVMap")
    uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for p in ob.data.polygons:
        for li in p.loop_indices:
            uv.data[li].uv = uvs[ob.data.loops[li].vertex_index]
    return ob


def page_image(scribble):
    """A ruled page: pale rules, and for Tam's a block of scribble strokes that never form a letter."""
    rng = np.random.default_rng(11)
    im = Image.new("RGB", (240, 320), (236, 230, 216))
    d = ImageDraw.Draw(im)
    for y in range(30, 310, 18):
        d.line([(10, y), (230, y)], fill=(170, 184, 200), width=2)
    d.line([(34, 0), (34, 320)], fill=(200, 140, 140), width=2)
    if scribble:
        for row in range(8):
            y = 28 + row * 18
            x = 40
            while x < 200 - rng.integers(0, 70):
                n = int(rng.integers(8, 20))
                pts = [(x + k * 3, y - 4 + (int(rng.integers(0, 9)) if k % 2 else 0)) for k in range(n)]
                d.line(pts, fill=(52, 58, 76), width=2)
                x += n * 3 + int(rng.integers(8, 14))
    return im


# ------------------------------------------------------------------------------------------------ materials


def materials(kit):
    M = {}
    M["plaster"] = kit.grime("#2e5a46", 0.72, 2.4, "plaster", 0.9)
    M["oak"] = kit.planks("#7a5232", "#5c3d24", 1.2, "X", "oak", 0.5)
    M["oakd"] = kit.planks("#4a2f1c", "#33200f", 0.9, "Z", "oak dark", 0.55)
    M["floor"] = kit.planks("#5a3c26", "#3c2616", 1.4, "X", "parquet", 0.45)
    M["brass"] = kit.metal("#c8963c", 0.3, "brass")
    M["stone"] = kit.concrete("#bdb6a6", 1.3, 0.3, "stone")
    M["iron"] = kit.plastic("#1c2420", 0.7, "iron", 0.1)
    M["paper"] = kit.plastic("#ece6d8", 0.7, "paper", 0.1)
    M["slate"] = kit.plastic("#6a717c", 0.5, "slate", 0.3)
    M["slated"] = kit.plastic("#4c525c", 0.6, "slate dark", 0.2)
    M["green"] = kit.plastic("#3f9a62", 0.3, "tally green", 0.5)
    M["hairb"] = kit.plastic("#121216", 0.65, "hair black", 0.2)
    M["hairw"] = kit.plastic("#ececec", 0.65, "hair white", 0.2)
    M["grey"] = kit.plastic("#9a9a9a", 0.7, "moustache", 0.1)
    M["pencil"] = kit.plastic("#d6a830", 0.5, "pencil", 0.2)
    M["white"] = kit.plastic("#f2efe6", 0.6, "white", 0.2)
    M["cream"] = kit.grime("#d8c8a8", 0.8, 2.0, "cream wall", 0.9)
    M["floorlight"] = kit.planks("#9a7650", "#7c5a38", 1.0, "X", "flat floor", 0.55)
    M["tile"] = kit.checker("#d8d2c2", "#b8b09c", 3.0, "kitchen tile", 0.5)
    M["brick"] = kit.bricks("#8a4a38", "#6e3a2c", "#8a847a", 1.0, "street brick", 0.8)
    M["brickw"] = kit.bricks("#9a6a4a", "#7e5238", "#a09a8e", 1.0, "door brick", 0.8)
    M["cobble"] = kit.cobbles("#3b3d44", "#6d6a66", "#1a1a1d", 2.4, 0.6, "wet cobbles")
    M["plat"] = kit.concrete("#8f8d88", 1.2, 0.35, "platform")
    M["train"] = kit.plastic("#6c7d8a", 0.45, "carriage", 0.3)
    M["yellow"] = kit.plastic("#d8b830", 0.6, "line", 0.1)
    M["sofa"] = kit.plastic("#5a6b86", 0.85, "sofa", 0.05)
    M["steel"] = kit.metal("#9aa6b0", 0.3, "kettle")
    M["loaf"] = kit.plastic("#c68a4a", 0.7, "loaf", 0.1)
    M["wood2"] = kit.planks("#6b4a2e", "#4e3520", 1.0, "X", "wood2", 0.6)
    M["suit"] = kit.plastic("#8a2a2a", 0.6, "suitcase", 0.2)
    M["cake"] = kit.plastic("#f4f1e8", 0.6, "cake", 0.2)
    M["wire"] = kit.plastic("#2a2420", 0.8, "wire", 0.0)
    M["leaf"] = kit.plastic("#3f6a3a", 0.8, "leaf", 0.1)
    M["dark"] = kit.plastic("#16120e", 0.9, "dark", 0.0)
    M["steam"] = kit.plastic("#dfe4e8", 0.9, "steam", 0.0)
    M["book"] = [kit.plastic(c, 0.7, f"book {i}", 0.1) for i, c in enumerate(
        ("#5a3a2a", "#3a4a3a", "#4a2c30", "#3a3a4c", "#6a5030", "#55402c"))]
    M["pane"] = _pane_mat(kit)
    M["win"], M["win_em"] = emission(kit, "window pane", "#8197ab", 1.2)
    M["fshade"], M["fshade_em"] = emission(kit, "flat shade", "#ffcf90", 3.0)
    M["wwin"], M["wwin_em"] = emission(kit, "flat window", "#9bb0cc", 1.6)
    M["warm"], _ = emission(kit, "warm bulb", "#ffd9a0", 14.0)
    M["flame"], _ = emission(kit, "flame", "#ffc060", 12.0)
    M["lamp_glass_gold"], _ = emission(kit, "street globe", "#ffd890", 6.0)
    M["bright"], _ = emission(kit, "bright window", "#fff2d8", 1.3)
    M["train_in"], _ = emission(kit, "carriage inside", "#ffd9a8", 2.2)
    M["numdark"] = kit.plastic("#2a2018", 0.8, "num outline", 0.0)
    return M


def _pane_mat(kit):
    """Rain-grey dome glass: pale grey-blue light with soft vertical streaks running down it."""
    name = "dome pane"
    m = kit._new(name)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    nt.nodes.remove(N["Principled BSDF"])
    em = N.new("ShaderNodeEmission")
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (7.0, 7.0, 0.9)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.6
    nz.inputs["Detail"].default_value = 3.0
    L.new(mp.outputs["Vector"], nz.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = kit.col("#7d909f")
    ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[1].color = kit.col("#b9cad7")
    L.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    L.new(ramp.outputs["Color"], em.inputs["Color"])
    em.inputs["Strength"].default_value = 1.5
    kit._fogged(m, em.outputs[0])
    return m, em


# ------------------------------------------------------------------------------------------------ the reading room


def banker_lamp(kit, ctx, M, tid, x, y, with_tally=False):
    """A brass lamp with a green-glass shade, lit warm. One closing timer drives them all (animate)."""
    z0 = 0.78
    kit.cyl(f"lamp {tid} base", 0.12, 0.07, (x, y, z0 + 0.035), M["brass"], n=20)
    kit.cyl(f"lamp {tid} pole", 0.018, 0.34, (x, y, z0 + 0.24), M["brass"], n=10)
    mat, em = emission(kit, f"lamp {tid} glass", "#a6d98c", 1.3)
    kit.cyl(f"lamp {tid} shade", 0.085, 0.36, (x, y, z0 + 0.43), mat, rot=(0, math.pi / 2, 0), n=16)
    for sx in (-1, 1):
        kit.cyl(f"lamp {tid} cap{sx}", 0.09, 0.015, (x + sx * 0.18, y, z0 + 0.43), M["brass"], rot=(0, math.pi / 2, 0), n=16)
    if with_tally:
        # the Keeper's tally: two short upright library-green strokes scratched in the brass base, facing the old seat, +y (not narrated)
        for sx in (-1, 1):
            kit.box(f"lamp tally {sx}", (0.014, 0.01, 0.05), (x + sx * 0.032, y + 0.118, z0 + 0.035), M["green"])
    name = f"lamp.{tid}"
    if tid == "W":   # the window table's lamp throws its light down the table at Tam's page, never across to the far seat
        kit.light(name, "SPOT", (x, y, z0 + 0.5), 28.0, "#ffc77a", size=0.06, spot=75, blend=0.6)
        kit.aim(kit.LIGHTS[name]["obj"], (x, y - 0.5, z0))
    else:
        kit.light(name, "POINT", (x, y, z0 + 0.55), 30.0, "#ffc77a", size=0.08)
    ctx["lamps"].append({"table": tid.split("#")[0], "light": name, "em": em, "base_em": 1.3})


def chair(kit, M, name, x, y, yaw):
    g = kit.empty(name, (x, y, 0.0), rot=(0, 0, math.radians(yaw)))
    kit.box(f"{name}.seat", (0.46, 0.44, 0.05), (0, 0.0, SEAT_TOP - 0.025), M["oak"], g, bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"{name}.leg{sx}{sy}", (0.04, 0.04, SEAT_TOP - 0.05), (sx * 0.2, sy * 0.19, (SEAT_TOP - 0.05) / 2), M["oakd"], g)
    kit.box(f"{name}.back", (0.46, 0.04, 0.5), (0, 0.22, SEAT_TOP + 0.25), M["oak"], g, bevel=0.01)
    return g


def build_room(kit, ctx, M, story):
    R, WALL_H = 8.6, 4.4
    kit.cyl("floor", 8.7, 0.1, (0, 0, -0.05), M["floor"], n=64)
    # the wall: a ring of plain plaster panels, with a dark oak skirting
    n = 32
    for i in range(n):
        a = 2 * math.pi * i / n
        wd = 2 * math.pi * (R + 0.2) / n + 0.05
        kit.box(f"wall{i}", (wd, 0.4, WALL_H), ((R + 0.2) * math.cos(a), (R + 0.2) * math.sin(a), WALL_H / 2),
                M["plaster"], rot=(0, 0, a + math.pi / 2))
        kit.box(f"skirt{i}", (wd, 0.05, 0.3), ((R - 0.02) * math.cos(a), (R - 0.02) * math.sin(a), 0.15), M["oakd"],
                rot=(0, 0, a + math.pi / 2))
        # the gallery: an oak ledge and a rail, with plain posts
        kit.box(f"ledge{i}", (wd, 0.6, 0.1), ((R - 0.25) * math.cos(a), (R - 0.25) * math.sin(a), 3.25), M["oakd"],
                rot=(0, 0, a + math.pi / 2))
        kit.box(f"rail{i}", (wd, 0.07, 0.07), ((R - 0.5) * math.cos(a), (R - 0.5) * math.sin(a), 3.85), M["oakd"],
                rot=(0, 0, a + math.pi / 2))
        for k in (-1, 1):
            aa = a + k * 0.5 * (2 * math.pi / n) * 0.5
            kit.box(f"post{i}{k}", (0.05, 0.05, 0.6), ((R - 0.5) * math.cos(aa), (R - 0.5) * math.sin(aa), 3.55), M["oakd"])
    # the glass dome: square panes of rain-grey glass in a dark frame; the gaps between the panes are its bars
    h = 5.0
    Rs = (R ** 2 + h ** 2) / (2 * h)
    zc = WALL_H + h - Rs
    a1 = math.asin(R / Rs)
    rings, segs = 9, 36
    pv, pf, sv, sf = [], [], [], []

    def pt(rad, a, ph):
        return (rad * math.sin(a) * math.cos(ph), rad * math.sin(a) * math.sin(ph), zc + rad * math.cos(a))

    for i in range(rings):
        for j in range(segs):
            a_lo, a_hi = a1 * i / rings, a1 * (i + 1) / rings
            p_lo, p_hi = 2 * math.pi * j / segs, 2 * math.pi * (j + 1) / segs
            am, pm = (a_lo + a_hi) / 2, (p_lo + p_hi) / 2
            k = 0.9
            q = [(am + (a_lo - am) * k, pm + (p_lo - pm) * k), (am + (a_lo - am) * k, pm + (p_hi - pm) * k),
                 (am + (a_hi - am) * k, pm + (p_hi - pm) * k), (am + (a_hi - am) * k, pm + (p_lo - pm) * k)]
            b = len(pv)
            pv += [pt(Rs - 0.02, a, p) for a, p in q]
            pf.append((b, b + 1, b + 2, b + 3))
            qs = [(a_lo, p_lo), (a_lo, p_hi), (a_hi, p_hi), (a_hi, p_lo)]
            b = len(sv)
            sv += [pt(Rs + 0.1, a, p) for a, p in qs]
            sf.append((b, b + 1, b + 2, b + 3))
    kit.mesh_obj("dome panes", pv, pf, M["pane"][0])
    kit.mesh_obj("dome frame", sv, sf, M["iron"])
    ctx["pane_em"] = M["pane"][1]
    kit.light("dome", "AREA", (0, 0, 7.6), 2000.0, "#b8c8d6", size=8.0)
    kit.aim(kit.LIGHTS["dome"]["obj"], (0, 0, 0))
    kit.light("fill", "POINT", (0, 0, 3.4), 380.0, "#aab8c6", size=0.6, shadow=False)
    # the arched window in the west wall: a tall arch of small square panes in an oak frame
    wx = -(R - 0.03)
    verts, fcs = [], []
    wv = 1.1
    pts = [(-wv, 0.5), (wv, 0.5), (wv, 2.7)]
    arch = [(wv * math.cos(math.pi * k / 16), 2.7 + wv * math.sin(math.pi * k / 16)) for k in range(0, 17)]
    ring = [(-wv, 0.5), (wv, 0.5)] + arch
    verts = [(wx, -y, z) for y, z in ring] + [(wx, 0.0, 2.1)]
    c = len(ring)
    fcs = [(i, (i + 1) % c, c) for i in range(c)]
    kit.mesh_obj("window glass", verts, fcs, M["win"])
    for k in range(-2, 3):   # muntins: small square panes
        top = 2.7 + math.sqrt(max(0.0, wv ** 2 - (k * 0.44) ** 2))
        kit.box(f"muntin v{k}", (0.04, 0.05, top - 0.5), (wx + 0.02, k * 0.44, (top + 0.5) / 2), M["oakd"])
    for z in np.arange(0.5, 3.6, 0.44):
        half = wv if z < 2.7 else max(0.1, math.sqrt(max(0.0, wv * wv - (z - 2.7) ** 2)))
        kit.box(f"muntin h{z:.2f}", (0.04, 2 * half, 0.05), (wx + 0.02, 0, z), M["oakd"])
    kit.box("window sill", (0.3, 2.5, 0.08), (wx + 0.13, 0, 0.5), M["oakd"])
    kit.light("window", "AREA", (wx - 0.3, 0, 2.2), 1600.0, "#b4c8dc", size=2.4)
    kit.aim(kit.LIGHTS["window"]["obj"], (-3.0, 0, 1.2))
    # the brass wall clock with plain tick marks and no numerals, hands at five (north wall, facing -y)
    cx, cy, cz = -3.0, 8.0, 2.5
    kit.cyl("clock face", 0.36, 0.05, (cx, cy, cz), M["white"], rot=(math.pi / 2, 0, 0), n=32)
    kit.cyl("clock rim", 0.39, 0.04, (cx, cy + 0.015, cz), M["brass"], rot=(math.pi / 2, 0, 0), n=32)
    for hr in range(12):
        th = hr * math.pi / 6
        big = hr % 3 == 0
        kit.box(f"tick{hr}", (0.03 if big else 0.02, 0.02, 0.1 if big else 0.06),
                (cx + math.sin(th) * 0.29, cy - 0.03, cz + math.cos(th) * 0.29), M["dark"], rot=(0, th, 0))
    th = math.radians(150)
    kit.box("hour hand", (0.035, 0.02, 0.2), (cx + math.sin(th) * 0.1, cy - 0.04, cz + math.cos(th) * 0.1), M["dark"], rot=(0, th, 0))
    kit.box("minute hand", (0.025, 0.02, 0.29), (cx, cy - 0.045, cz + 0.145), M["dark"])
    kit.sphere("clock pin", 0.03, (cx, cy - 0.05, cz), M["brass"], seg=8)
    # the stacks along the east wall: tall dark shelves of plain leather book blocks, no spines, no lettering
    rng = np.random.default_rng(5)
    bybook = [[] for _ in M["book"]]
    frame = []
    for uy in (-2.7, -0.9, 0.9, 2.7):
        ux = 7.8
        frame += [(ux, uy - 0.85, 1.4, 0.5, 0.06, 2.8), (ux, uy + 0.85, 1.4, 0.5, 0.06, 2.8), (ux + 0.22, uy, 1.4, 0.05, 1.7, 2.8)]
        for zz in (0.12, 0.57, 1.02, 1.47, 1.92, 2.37, 2.8):
            frame.append((ux, uy, zz, 0.5, 1.7, 0.05))
        for zz in (0.35, 0.8, 1.25, 1.7, 2.15, 2.6):
            y = uy - 0.8
            while y < uy + 0.78:
                w = float(rng.uniform(0.035, 0.075))
                hh = float(rng.uniform(0.26, 0.4))
                if rng.random() < 0.06:
                    y += 0.09
                    continue
                bybook[int(rng.integers(0, len(bybook)))].append((ux - 0.1, y + w / 2, zz - 0.2 + hh / 2, 0.28, w, hh))
                y += w + 0.004
    mbox(kit, "stack frames", frame, M["oakd"])
    for k, bx in enumerate(bybook):
        if bx:
            mbox(kit, f"books {k}", bx, M["book"][k])
    # tables, chairs, lamps
    ctx["lamps"] = []
    for tb in story["room"]["tables"]:
        (cx_, cy_), (sx, sy) = tb["c"], tb["size"]
        kit.box(f"table {tb['id']}", (sx, sy, 0.05), (cx_, cy_, 0.755), M["oak"], bevel=0.012)
        kit.box(f"apron {tb['id']}", (sx - 0.1, sy - 0.1, 0.07), (cx_, cy_, 0.69), M["oakd"])
        legs = [(cx_ + a * (sx / 2 - 0.08), cy_ + b * (sy / 2 - 0.08)) for a in (-1, 1) for b in (-1, 1)]
        if sy > 2.5:
            legs += [(cx_ + a * (sx / 2 - 0.08), cy_) for a in (-1, 1)]
        if sx > 2.5:
            legs += [(cx_, cy_ + b * (sy / 2 - 0.08)) for b in (-1, 1)]
        for k, (lx, ly) in enumerate(legs):
            kit.box(f"table {tb['id']} leg{k}", (0.09, 0.09, 0.73), (lx, ly, 0.365), M["oakd"])
        for k, (lx, ly) in enumerate(tb["lamps"]):
            banker_lamp(kit, ctx, M, f"{tb['id']}#{k}" if tb["id"] != "W" else "W", lx, ly, with_tally=(tb["id"] == "W"))
    for k, (x, y, yaw) in enumerate(story["room"]["chairs"]):
        chair(kit, M, f"chair{k}", x, y, yaw)
    # papers: Tam's page (ruled, with scribble strokes), my blank page, a reader's page that turns
    pm = img_mat(kit, "tam page", page_image(True))
    quad_uv(kit, "tam page", (0.3, 0.4), (-7.5, -0.2, 0.784), pm)
    fm = img_mat(kit, "blank form", page_image(False))
    quad_uv(kit, "my page", (0.3, 0.4), (-6.4, -0.2, 0.784), fm, rot=(0, 0, 0.1))
    quad_uv(kit, "reader page", (0.3, 0.4), (-1.5, -4.3, 0.784), fm, rot=(0, 0, math.pi / 2))
    piv = kit.empty("page pivot", (-1.38, -4.3, 0.79))
    leaf = quad_uv(kit, "page leaf", (0.3, 0.4), (0.2, 0.0, 0.002), fm, piv, rot=(0, 0, math.pi / 2))
    ctx["page"] = piv
    # Tam's reason in one picture: a stack of plain book blocks taller than his head, on the table in front of him
    ctx["stack"] = []
    grp = kit.empty("book stack", (-7.0, -0.38, 0.78))
    zz = 0.0
    for k, (w, d, hh) in enumerate(((0.5, 0.36, 0.13), (0.46, 0.34, 0.1), (0.52, 0.36, 0.14), (0.44, 0.33, 0.11),
                                    (0.5, 0.35, 0.13), (0.45, 0.34, 0.12), (0.5, 0.36, 0.1), (0.42, 0.32, 0.13),
                                    (0.48, 0.34, 0.12), (0.44, 0.33, 0.1), (0.47, 0.34, 0.13))):
        ctx["stack"].append(kit.box(f"stack book {k}", (w, d, hh), (0.015 * ((-1) ** k), 0.01 * (k % 3 - 1), zz + hh / 2), M["book"][k % 6], grp, bevel=0.01, rot=(0, 0, 0.05 * (k % 4 - 1.5))))
        zz += hh
    # the Negative's key (cold, from the side) and rim (cool, behind it); its table lamp is dead
    kit.light("neg_key", "SPOT", (0, 0, 3), 0.0, "#a9c4e8", size=0.12, spot=34, blend=0.6)
    kit.light("neg_rim", "SPOT", (0, 0, 3), 0.0, "#8fb0e0", size=0.1, spot=40, blend=0.5)

    # CC0 props (2026-11-03 quality pass): a rug under the window table, plants, a floor lamp
    kit.prop("carpet_1", (-7.0, 0.0, 0.0), rot=90, fit=3.4, tint="#7a5a4a")
    for k, (px, py) in enumerate(((-7.9, 3.0), (-7.9, -3.0), (6.5, -5.4), (6.5, 5.4))):
        kit.prop("houseplant_1", (px, py, 0.0), rot=40 * k, height=0.9)
    kit.prop("light_floor1", (-6.3, 3.2, 0.0), height=1.5, tint="#d9b070")


# ------------------------------------------------------------------------------------------------ the other scenes


def scene_door(kit, ctx, M, O):
    ox, oy = O
    kit.box("ground", (30, 14, 0.2), (ox, oy - 4, -0.1), M["plat"])
    wbox(kit, "house wall", (ox - 6, oy + 1.4, 0.0), (ox + 6, oy + 1.9, 4.2), M["brickw"])
    wbox(kit, "door frame", (ox - 0.62, oy + 1.32, 0.2), (ox + 0.62, oy + 1.42, 2.55), M["oakd"])
    wbox(kit, "door leaf", (ox - 0.52, oy + 1.28, 0.2), (ox + 0.52, oy + 1.34, 2.45), M["oak"])
    kit.sphere("door knob", 0.045, (ox + 0.38, oy + 1.22, 1.25), M["brass"], seg=8)
    wbox(kit, "stoop", (ox - 1.2, oy - 0.35, 0.0), (ox + 1.2, oy + 1.4, 0.2), M["stone"])
    wbox(kit, "stoop step", (ox - 1.0, oy - 0.65, 0.0), (ox + 1.0, oy - 0.35, 0.1), M["stone"])
    for sx in (-3.6, 3.6):
        kit.box(f"window{sx}", (1.2, 0.08, 1.4), (ox + sx, oy + 1.36, 2.0), M["bright"])
        kit.box(f"window frame{sx}", (1.4, 0.06, 1.6), (ox + sx, oy + 1.4, 2.0), M["oakd"])
    kit.light("sun", "SUN", (ox + 7, oy - 12, 13), 2.8, "#fff0d4")
    kit.aim(kit.LIGHTS["sun"]["obj"], (ox, oy, 1.0))
    kit.light("fill", "AREA", (ox - 5, oy - 10, 5), 260.0, "#cfe0ff", size=8.0)
    kit.aim(kit.LIGHTS["fill"]["obj"], (ox, oy, 1.5))


def scene_street(kit, ctx, M, O):
    """A bright, saturated shopping street in daylight: light paving, painted facades with warm lit windows, no lettering."""
    ox, oy = O
    kit.box("street ground", (50, 12, 0.2), (ox, oy, -0.1), kit.concrete("#cfc9bb", 1.6, 0.15, "light paving"))
    paints = ["#e3a93a", "#3fa6a0", "#e0705a", "#efe3c6", "#8fbf6a", "#d9849a", "#4f8fcf"]
    winm, _ = emission(kit, "street window warm", "#fff0c8", 1.1)
    for sy, nm in ((4.6, "n"), (-4.6, "s")):
        face = -math.copysign(0.42, sy)
        for k in range(-8, 9):
            if nm == "n" and abs(k) <= 1:
                pm0 = kit.plastic(paints[(k + 8) % len(paints)], 0.9, f"paint {nm}{k}", 0.05)
                wbox(kit, f"fac {nm}{k}", (ox + k * 3.2 - 1.6, oy + sy - 0.4, 0.0), (ox + k * 3.2 + 1.6, oy + sy + 0.4, 6.5), pm0)
                continue
            pm = kit.plastic(paints[(k + 8 + (3 if nm == "s" else 0)) % len(paints)], 0.9, f"paint {nm}{k}", 0.05)
            wbox(kit, f"fac {nm}{k}", (ox + k * 3.2 - 1.6, oy + sy - 0.4, 0.0), (ox + k * 3.2 + 1.6, oy + sy + 0.4, 6.5), pm)
            kit.box(f"fwin{nm}{k}", (1.3, 0.06, 1.5), (ox + k * 3.2, oy + sy + face, 2.7), M["white"])
            kit.box(f"fpane{nm}{k}", (1.1, 0.06, 1.3), (ox + k * 3.2, oy + sy + face - math.copysign(0.02, sy), 2.7), winm)
            kit.box(f"fcor{nm}{k}", (3.2, 0.1, 0.18), (ox + k * 3.2, oy + sy + face, 4.9), M["white"])
    for k, lx in enumerate((-6.0, 3.2, 7.0)):
        kit.cyl(f"lamppost{k}", 0.06, 3.4, (ox + lx, oy + 3.7, 1.7), M["iron"], n=10)
        kit.sphere(f"streetglobe{k}", 0.16, (ox + lx, oy + 3.7, 3.5), M["lamp_glass_gold"], seg=10)
    kit.light("overcast", "AREA", (ox, oy, 9), 5200.0, "#fff4e0", size=14.0)
    kit.aim(kit.LIGHTS["overcast"]["obj"], (ox, oy, 0))
    kit.light("sfront", "AREA", (ox + 1.5, oy - 5.5, 3.5), 1500.0, "#fff2e2", size=5.0)
    kit.aim(kit.LIGHTS["sfront"]["obj"], (ox, oy, 1.6))

    # CC0 props: planters behind the narrator's street
    kit.prop("sub_planter", (ox - 2.4, oy + 3.5, 0.0), height=0.8)
    kit.prop("sub_planter", (ox + 2.6, oy + 3.5, 0.0), height=0.8)
    kit.prop("sub_planter", (ox + 4.4, oy + 3.5, 0.0), height=0.8)


# ------------------------------------------------------------------------------------------------ the numbers


SEG = {"0": "abcdef", "1": "spq", "2": "abdeg", "3": "abcdg", "4": "bcfg", "5": "acdfg", "6": "acdefg", "7": "abc",
       "8": "abcdefg", "9": "abcdfg"}


def _segments():
    """name -> (bar (cx, cy, sx, sy), outline (cx, cy, sx, sy), rotation in degrees). The outline is the bar grown by
    NUM_O (8% of the glyph's height) on the outside and by 0.4 NUM_O on the side that faces a hole, so a 0 keeps its
    open middle. The one is a centred stem with a top-left flag and a foot bar that reaches a stem-width either side."""
    w, h, t, o = NUM_W, NUM_H, NUM_T, NUM_O
    oi = 0.4 * o

    def sg(cx, cy, sx, sy, l, r, bt, tp, rot=0.0):
        return ((cx, cy, sx, sy), (cx + (r - l) / 2, cy + (tp - bt) / 2, sx + l + r, sy + bt + tp), rot)

    vb = h / 2 + t / 2
    return {"a": sg(0, h / 2 - t / 2, w, t, o, o, oi, o), "d": sg(0, -h / 2 + t / 2, w, t, o, o, o, oi),
            "g": sg(0, 0, w, t, o, o, 0.7 * o, 0.7 * o),
            "b": sg(w / 2 - t / 2, h / 4, t, vb, oi, o, o, o), "c": sg(w / 2 - t / 2, -h / 4, t, vb, oi, o, o, o),
            "f": sg(-w / 2 + t / 2, h / 4, t, vb, o, oi, o, o), "e": sg(-w / 2 + t / 2, -h / 4, t, vb, o, oi, o, o),
            "s": sg(0, 0, t, h, o, o, o, o),
            "p": sg(-t / 2 - 0.03, h / 2 - 0.058, 0.115, 0.042, o, o, o, o, 35.0),
            "q": sg(0, -h / 2 + 0.021, 3 * t, 0.042, o, o, o, o)}


def _rot_box(kit, c, size, depth, zc, ang):
    cx, cy, sx, sy = c[0], c[1], size[0], size[1]
    vs = kit.box_verts(sx, sy, depth, (0, 0, zc))
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca, z) for x, y, z in vs]


def build_numbers(kit, ctx, M, story):
    """A glowing number floating over each head that has one: rounded block digits (seven bars, each a cream bar on a
    thin dark outline), facing the camera. A change rolls: the old digit squashes up out, the new grows in."""
    cam = kit.OBJ["cam"]
    ctx["num"] = {}
    for who, n in story["numbers"].items():
        root = kit.empty(f"num.{who}", (0, 0, 0))
        con = root.constraints.new("COPY_ROTATION")
        con.target = cam
        mat, em = emission(kit, f"numglow.{who}", "#fff4dc", NUM_GLOW)
        slots = []
        for k in range(n):
            sroot = kit.empty(f"num.{who}.s{k}", ((k - (n - 1) / 2) * NUM_PITCH, 0, 0), root)
            layers = []
            for li in range(2):
                lay = kit.empty(f"num.{who}.s{k}.l{li}", (0, 0, 0), sroot)
                segs = {}
                for sname, ((cx, cy, sx, sy), (ocx, ocy, osx, osy), rot) in _segments().items():
                    verts = _rot_box(kit, (ocx, ocy), (osx, osy), 0.012, -0.021, rot) + _rot_box(kit, (cx, cy), (sx, sy), 0.03, 0.0, rot)
                    fcs = [tuple(i for i in f) for f in kit.BOX_FACES] + [tuple(8 + i for i in f) for f in kit.BOX_FACES]
                    ob = kit.mesh_obj(f"num.{who}.s{k}.l{li}.{sname}", verts, fcs, M["numdark"], lay)
                    ob.data.materials.append(mat)
                    for pi, p in enumerate(ob.data.polygons):
                        p.material_index = 1 if pi >= 6 else 0
                    ob.hide_render = True
                    segs[sname] = ob
                layers.append((lay, segs))
            slots.append((sroot, layers))
        ctx["num"][who] = {"root": root, "slots": slots, "em": em, "n": n}


def _fmt(v, n):
    s = "" if v is None else str(v)
    return s.rjust(n)


def update_numbers(ctx, tl, t, states, vis, scene_on):
    cues_by = ctx["numcues"]
    for who, d in ctx["num"].items():
        on = vis.get(who, False) and scene_on
        d["root"].hide_render = not on
        for sr, layers in d["slots"]:
            for lay, segs in layers:
                for o in segs.values():
                    if not on:
                        o.hide_render = True
        if not on:
            continue
        cs = cues_by.get(who, [])
        k = None
        for i, c in enumerate(cs):
            if c["t"] <= t + 1e-9:
                k = i
        cur = cs[k]["v"] if k is not None else None
        prev, u = cur, None
        if k is not None and not cs[k].get("snap") and k > 0:
            dt = t - cs[k]["t"]
            if dt < 0.4:
                prev, u = cs[k - 1]["v"], _ss(dt / 0.4)
        n = d["n"]
        sc, sp = _fmt(cur, n), _fmt(prev, n)
        st = states[who]
        nzc = _last([c for c in cues_by.get("_numz_" + who, [])], t)
        base = V((st["x"], st["y"], st["z"] + NUM_LIFT + (nzc["v"] if nzc else 0.0)))
        shift_c = -(n - len(str(cur or ""))) * NUM_PITCH / 2 if cur is not None else 0.0
        shift_p = -(n - len(str(prev or ""))) * NUM_PITCH / 2 if prev is not None else 0.0
        shift = shift_c if u is None else shift_p + (shift_c - shift_p) * u
        d["root"].location = base
        for k2, (sroot, layers) in enumerate(d["slots"]):
            sroot.location.x = (k2 - (n - 1) / 2) * NUM_PITCH + shift
            cc, cp = sc[k2], sp[k2]
            for li, (lay, segs) in enumerate(layers):
                if u is None or cc == cp:
                    ch, s, anchor = (cc if li == 0 else " "), 1.0, 0
                elif li == 0:
                    ch, s, anchor = cp, 1.0 - u, 1
                else:
                    ch, s, anchor = cc, u, -1
                lit = SEG.get(ch, "") if s > 0.02 else ""
                lay.scale = (1, max(s, 0.001), 1)
                lay.location.y = anchor * (1 - s) * NUM_H / 2
                lay.location.x = 0.0
                for sn, o in segs.items():
                    o.hide_render = sn not in lit


# ------------------------------------------------------------------------------------------------ the upside-down grin

GRIN_W, GRIN_H = 0.62, 0.42   # world size of the decal on the Negative's face (the mouth is about 0.5 wide: ~40% of the head)
EYE_W, EYE_H = 1.0, 0.40


def grin_image(w=1240, h=840):
    """The laughing D-shaped grin flipped upside down: a thick white outline, a dark inside, teeth along the flat edge
    (now at the bottom), a cold tongue under the dome of it."""
    S = 1
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = w / 2
    hw, hh = w * 0.43, h * 0.56
    base = h * 0.80                      # the flat edge, at the bottom
    pts = []
    for k in range(0, 181):
        a = math.radians(k)
        pts.append((cx + hw * math.cos(a), base - hh * math.sin(a) ** 0.8 * (1.0 if math.sin(a) > 0 else 0)))
    d.polygon(pts, fill=(244, 247, 252, 255))
    o = w * 0.045                        # outline thickness
    ins = []
    for k in range(0, 181):
        a = math.radians(k)
        ins.append((cx + (hw - o) * math.cos(a), base - o * 0.5 - (hh - o * 1.3) * math.sin(a) ** 0.8))
    d.polygon(ins, fill=(6, 7, 10, 255))
    # tongue: a rounded cold-grey lump up under the dome
    tw = hw * 0.55
    d.ellipse([cx - tw, base - hh * 0.62, cx + tw, base - hh * 0.05], fill=(128, 136, 150, 255))
    d.line([(cx, base - hh * 0.58), (cx, base - hh * 0.2)], fill=(70, 76, 88, 255), width=int(w * 0.012))
    # teeth along the flat edge: white blocks standing up from it
    n = 7
    x0, x1 = cx - (hw - o * 1.1), cx + (hw - o * 1.1)
    tw_ = (x1 - x0) / n
    for i in range(n):
        xa = x0 + i * tw_ + tw_ * 0.08
        d.rectangle([xa, base - o * 0.5 - hh * 0.26, xa + tw_ * 0.84, base - o * 0.5], fill=(244, 247, 252, 255))
    return im


def glint_image(w=1000, h=400):
    """Big white eye outlines on black with bright white pupils, and heavy slanted brows."""
    S = 2
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for sx in (-1, 1):
        x, y = w * S / 2 + sx * w * S * 0.255, h * S * 0.58
        rx, ry = w * S * 0.17, h * S * 0.27
        d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=(244, 247, 252, 255))
        r2 = rx * 0.80
        d.ellipse([x - r2, y - ry * 0.80, x + r2, y + ry * 0.80], fill=(8, 9, 12, 255))
        pr = ry * 0.40
        px = x - sx * rx * 0.08
        d.ellipse([px - pr, y - pr * 0.8, px + pr, y + pr * 1.2], fill=(255, 255, 255, 255))
        # a heavy brow slanting down toward the nose
        bx0, bx1 = x + sx * rx * 1.1, x - sx * rx * 0.9
        by0, by1 = h * S * 0.14, h * S * 0.27
        t = h * S * 0.05
        d.polygon([(bx0, by0 - t), (bx0, by0 + t), (bx1, by1 + t), (bx1, by1 - t)], fill=(226, 230, 238, 255))
    return im.resize((w, h), Image.LANCZOS)


def alpha_mat(kit, name, pil, emit=0.0):
    img = bpy.data.images.new(name, pil.width, pil.height, alpha=True)
    a = np.asarray(pil.convert("RGBA")).astype(np.float32)[::-1] / 255
    img.pixels.foreach_set(a.ravel())
    img.pack()
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.6
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = img
    tx.interpolation = "Linear"
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    if emit:
        nt.links.new(tx.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tx.outputs["Alpha"], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(b.outputs[0], mix.inputs[2])
    kit._fogged(m, mix.outputs[0])
    return m


def curved_decal(kit, name, size, zc, r, mat, parent):
    """A strip bent onto the front (-y) of a cylinder of radius r around the head, centred at height zc."""
    w, h = size
    cols = 20
    verts, uvs = [], []
    for j in range(cols + 1):
        u = j / cols
        th = (u - 0.5) * w / r
        for v in (0.0, 1.0):
            verts.append((r * math.sin(th), -r * math.cos(th), zc + (v - 0.5) * h))
            uvs.append((u, v))
    fcs = [(j * 2, (j + 1) * 2, (j + 1) * 2 + 1, j * 2 + 1) for j in range(cols)]
    ob = kit.mesh_obj(name, verts, fcs, mat, parent, smooth=True)
    uv = ob.data.uv_layers.new(name="UVMap")
    for p in ob.data.polygons:
        for li in p.loop_indices:
            uv.data[li].uv = uvs[ob.data.loops[li].vertex_index]
    return ob


def cat_image():
    """Our own picture for the phone: a blocky cat sliding off a shelf into a box. No text."""
    im = Image.new("RGB", (240, 420), (255, 214, 140))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 150, 150, 176], fill=(138, 94, 54))
    d.rectangle([110, 260, 230, 400], fill=(170, 120, 70))
    d.rectangle([118, 268, 222, 400], fill=(60, 40, 24))
    d.polygon([(70, 70), (190, 150), (176, 200), (56, 120)], fill=(70, 70, 78))      # the sliding cat
    d.rectangle([40, 60, 82, 100], fill=(70, 70, 78))
    d.polygon([(40, 60), (48, 42), (58, 60)], fill=(70, 70, 78))
    d.polygon([(66, 60), (74, 42), (82, 60)], fill=(70, 70, 78))
    d.ellipse([46, 74, 56, 84], fill=(255, 230, 90))
    d.ellipse([66, 74, 76, 84], fill=(255, 230, 90))
    d.line([(190, 150), (226, 176)], fill=(70, 70, 78), width=10)
    return im


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    ctx = {"scene_objs": {}}
    M = materials(kit)
    ctx["M"] = M
    O = {k: tuple(v) for k, v in story["scenes"].items()}
    builders = {"room": lambda: build_room(kit, ctx, M, story), "door": lambda: scene_door(kit, ctx, M, O["door"]),
                "street": lambda: scene_street(kit, ctx, M, O["street"])}
    for name, fn in builders.items():
        before = set(bpy.data.objects.keys())
        fn()
        ctx["scene_objs"][name] = [bpy.data.objects[k] for k in set(bpy.data.objects.keys()) - before]
    build_numbers(kit, ctx, M, story)
    ctx["cur_scene"] = None
    ctx["extras_done"] = False
    ctx["numcues"] = None
    return ctx


# ------------------------------------------------------------------------------------------------ the pieces that move

SKY = {"door": ("#9ccdf0", 0.8), "street": ("#a9c4d8", 1.0)}


def _extras(kit, ctx):
    """Parts the rig doesn't have: Tam's pencil, the Negative's upside-down grin, the phone."""
    ctx["extras_done"] = True
    M = ctx["M"]
    R, H = faces.HEAD_R, faces.HEAD_H
    hg = bpy.data.objects.get("tam.headg")
    ctx["pencil"] = None
    if hg is not None:
        ctx["pencil"] = kit.box("tam.pencil", (0.07, 0.07, 0.55), (R - 0.1, 0.12, 0.28), M["pencil"], hg, rot=(0.5, 0.0, 0.0), bevel=0.01)
    hg = bpy.data.objects.get("neg.headg")
    ctx["grin"] = None
    if hg is not None:
        gm = alpha_mat(kit, "neg grin", grin_image(), emit=0.5)
        ctx["grin"] = curved_decal(kit, "neg.grin", (GRIN_W, GRIN_H), -0.24, R + 0.012, gm, hg)
        em_ = alpha_mat(kit, "neg glints", glint_image(), emit=1.1)
        curved_decal(kit, "neg.glints", (EYE_W, EYE_H), 0.17, R + 0.012, em_, hg)
    pm = img_mat(kit, "cat picture", cat_image(), rough=0.4)
    sm = kit.plastic("#16181c", 0.4, "phone body", 0.3)
    ph = kit.empty("phone", (3000, 3000, 0))
    kit.box("phone.body", (0.09, 0.012, 0.17), (0, 0, 0), sm, ph, bevel=0.008)
    quad_uv(kit, "phone.screen", (0.078, 0.15), (0, -0.0075, 0), pm, ph, rot=(math.pi / 2, 0, 0))
    ctx["phone"] = ph


def _chars_inscene(story, tl, t, scene):
    from blocky import acting as ac
    ox, oy = story["scenes"][scene]
    out, states = {}, {}
    for who in story["cast"]:
        s = ac.state(tl, who, t)
        states[who] = s
        out[who] = abs(s["x"] - ox) < 80 and abs(s["y"] - oy) < 80
    return out, states


def animate(kit, story, tl, t, ctx):
    from blocky import acting as ac
    from blocky import kit as K

    if not ctx["extras_done"]:
        _extras(kit, ctx)
        by = {}
        for c in tl["cues"]:
            if c["name"] == "num":
                by.setdefault(c["who"], []).append(c)
        for v in by.values():
            v.sort(key=lambda c: c["t"])
        ctx["numcues"] = by
    over = {}
    shot = _shot(tl, t)["id"]
    scene = story["scene_of"][shot]
    # ---- only this shot's scene is drawn
    if ctx["cur_scene"] != scene:
        ctx["cur_scene"] = scene
        for nm, obs in ctx["scene_objs"].items():
            for ob in obs:
                ob.hide_render = nm != scene
        w = bpy.context.scene.world.node_tree.nodes["Background"]
        c, s = SKY.get(scene, ("#0c0f14", 0.15))
        w.inputs["Color"].default_value = K.col(c)
        w.inputs["Strength"].default_value = s
    inscene, states = _chars_inscene(story, tl, t, scene)
    # ---- people: sitting, leaning
    for who, keys in tl["acting"].items():
        root = bpy.data.objects.get(who)
        if root is not None and not inscene[who]:
            root.hide_render = True
            for ob in root.children_recursive:
                ob.hide_render = True
        tor = bpy.data.objects.get(f"{who}.torso")
        if tor is not None:
            tor.rotation_euler = (math.radians(ac._held(keys, "bend", t, 0.0)), 0, 0)
        sit = False
        for k in keys:
            if "sit" in k and k["t"] <= t + 1e-9:
                sit = k["sit"]
        if sit:
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (-math.pi / 2, 0, 0)
    for nm in ("tam.gl-1", "tam.gl1"):
        ob = bpy.data.objects.get(nm)
        if ob is not None:
            ob.hide_render = True
    # ---- the Negative grows with each swallowed laugh; it changes size only across a cut
    nr = bpy.data.objects.get("neg")
    sc_c = _last(_cues(tl, "negscale"), t)
    if nr is not None:
        if "neg_base" not in ctx:
            ctx["neg_base"] = nr.scale.copy()     # the rig's own root scale; ours multiplies it
        k = sc_c["v"] if sc_c else 1.0
        # a little too tall and too thin: wrong proportions, not a soft box
        nr.scale = tuple(v * k * m for v, m in zip(ctx["neg_base"], (0.9, 0.9, 1.14)))
        for nm in ("arm-1", "arm1"):
            ob = bpy.data.objects.get(f"neg.{nm}")
            if ob is not None:
                ob.scale = (0.62, 0.62, 1.12)
    # ---- the stack of books appears with its cue
    stc = _last(_cues(tl, "stack"), t)
    for ob in ctx["stack"]:
        ob.hide_render = not (stc and stc.get("on", True) and scene == "room")
    # ---- coming apart: the blocks separate a little, then drift up the dome, turning, and shrink away
    ap = _last(_cues(tl, "apart"), t)
    if ap and ap.get("off"):
        ap = None
    if not ctx.get("apart_base"):
        ctx["apart_base"] = {}
        for nm in ("torso", "leg-1", "leg1", "neck"):
            ob = bpy.data.objects.get(f"neg.{nm}")
            if ob is not None:
                ctx["apart_base"][nm] = (ob, ob.location.copy())
        for nm in ("arm-1", "arm1"):
            ob = bpy.data.objects.get(f"neg.{nm}")
            if ob is not None:
                ctx["apart_base"][nm] = (ob, ob.location.copy())
    x = (t - ap["t"]) if ap else -1.0
    sep = _ss(x / 1.6) if x > 0 else 0.0
    rise = _ss((x - 1.2) / 3.2) if x > 0 else 0.0
    off = {"neck": (0, 0, 0.75), "torso": (0, 0, 0.0), "arm-1": (-0.7, 0, 0.1), "arm1": (0.7, 0, 0.1),
           "leg-1": (-0.15, 0, -0.55), "leg1": (0.15, 0, -0.55)}
    for nm, (ob, b0) in ctx["apart_base"].items():
        o = off[nm]
        spread = 1.0 if nm != "torso" else 0.0
        ob.location = (b0.x + o[0] * sep, b0.y + o[1] * sep, b0.z + o[2] * sep + rise * (5.0 + 1.4 * (len(nm) % 3)))
        ob.rotation_euler[2] = rise * (0.7 if nm in ("neck", "arm1") else -0.5)
    if nr is not None and ap and x > 0:
        nr.scale = tuple(v * (1.0 - _ss((x - 3.6) / 1.0)) + 1e-5 for v in nr.scale)
    # ---- the phone (a cat picture), held where the cue says
    pc = _last(_cues(tl, "phone"), t)
    ph = ctx["phone"]
    if pc and pc.get("pos"):
        ph.location = tuple(pc["pos"])
        ph.rotation_euler = (0, 0, math.radians(pc.get("yaw", 0)))
    else:
        ph.location = (3000, 3000, 0)
    # ---- Tam's pencil drops from behind his ear, bounces off his nose (a 0.7 s fall) and lies on the page
    if ctx.get("pencil") is not None:
        pb = _last(_cues(tl, "pencil"), t)
        pen = ctx["pencil"]
        if pb:
            x = min(1.0, max(0.0, (t - pb["t"]) / 0.7))
            if x <= 0:
                pen.location, pen.rotation_euler = (faces.HEAD_R - 0.1, 0.12, 0.28), (0.5, 0.0, 0.0)
            else:
                fall = x * x
                pen.location = (faces.HEAD_R - 0.1 - 0.35 * x, 0.12 - 0.75 * x, 0.28 - 1.5 * fall + 0.25 * math.sin(math.pi * min(1, x * 1.6)) * (1 - x))
                pen.rotation_euler = (0.5 + 2.2 * x, 0.0, 1.2 * x)
        else:
            pen.location, pen.rotation_euler = (faces.HEAD_R - 0.1, 0.12, 0.28), (0.5, 0.0, 0.0)
    # ---- the closing timer: every table lamp together; the dome's dusk
    lamps = _level(tl, "lamps", t, 1.0)
    dome = _level(tl, "dome", t, 1.0)
    bpy.context.scene.view_settings.exposure = story["look"].get("exposure", 0.0) + (ROOM_EV * _ss((dome - 0.12) / 0.38) if scene == "room" else 0.0)
    dead_c = _last(_cues(tl, "dead"), t)
    dead = set(dead_c["tables"]) if dead_c else set()
    for lp in ctx["lamps"]:
        g = 0.0 if lp["table"] in dead else lamps
        over[lp["light"]] = g * (1.0 + LAMP_BOOST * lamps)
        lp["em"].inputs["Strength"].default_value = lp["base_em"] * (0.04 if lp["table"] in dead else lamps) + 0.05
    boost = 1.0 + ROOM_BOOST * dome
    over["dome"] = dome * (0.4 + 0.6 * lamps) * boost
    over["fill"] = dome * (0.25 + 0.75 * lamps) * boost
    over["window"] = dome * boost
    ctx["pane_em"].inputs["Strength"].default_value = 1.2 * (0.25 + 0.75 * dome)
    ctx["M"]["win_em"].inputs["Strength"].default_value = 1.2 * (0.12 + 0.88 * dome ** 1.5)
    # ---- the page turns
    pg = _last(_cues(tl, "page"), t)
    u = 0.0
    if pg:
        u = _ss((t - pg["t"]) / pg.get("dur", 0.8))
    ctx["page"].rotation_euler = (0.0, -math.pi * 0.96 * u, 0.0)
    # ---- the Negative's light: a cold key from the side and a cool rim behind it; its lamp is dead
    s = states["neg"]
    over["neg_key"] = over["neg_rim"] = 0.0
    if inscene["neg"] and scene == "room":
        yaw = math.radians(s["yaw"])
        f = V((math.sin(yaw), -math.cos(yaw), 0.0))
        sd = V((math.cos(yaw), math.sin(yaw), 0.0))
        if sd.x > 0:
            sd = -sd
        bend = ac._held(tl["acting"]["neg"], "bend", t, 0.0)
        head = V((s["x"], s["y"], s["z"] + 1.35)) + f * 0.25 * (1 + math.sin(math.radians(bend)))
        head += f * 0.55 * math.sin(math.radians(bend))
        for nm, pos, w in (("neg_key", head + sd * 1.2 + f * 0.9 + V((0, 0, -0.9)), 520.0),
                           ("neg_rim", head - f * 1.5 - sd * 0.5 + V((0, 0, 1.4)), 520.0)):
            ob = K.LIGHTS[nm]["obj"]
            ob.location = pos
            ob.rotation_euler = (head - pos).to_track_quat("-Z", "Y").to_euler()
            K.LIGHTS[nm]["base"] = w
            over[nm] = 1.0
    for who, dd in ctx["num"].items():
        dd["em"].inputs["Strength"].default_value = NUM_GLOW
    update_numbers(ctx, tl, t, states, inscene, True)
    return over
