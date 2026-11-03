"""The Reading Room (ep43): a town where the glowing number over your head is how many people know your name, a round
domed reading room, and the Negative (a person printed in reverse, with no number) that sits one table nearer to Tam.

Built from kit.py's parts. Every scene has its own patch of the Blender world (story["scenes"] holds each origin), and
animate() shows only the current shot's scene, with only the characters standing in it:
  room (0,0)     the round reading room, radius 8.6: the arched window in the west wall (x = -8.5), the stacks along the
                 east wall, glass dome of plain square panes, tables W (the window table for two), B, C, D, N, P
  steps (200,0)  sunny library steps          party (300,0)  a living room        station (400,0)  a platform
  door (500,0)   the postman's doorstep       kitchen (600,0) Ossie's table        street (700,0)   a wet street
  flat (800,0)   our small flat
THE CREATURE is the Negative ("neg" in the cast): a normal R6 person printed in reverse (black skin, white face strokes,
white hair, library-green jumper, no number). It is one model, posed by the acting keys.

Cues read here: num {who, v, snap?} (the number over a head; a change rolls in 0.4 s), warm {who}, phones {mode},
lamps {to, dur} (the closing timer), dome {to, dur}, dead {tables}, oldchair {d}, page {dur}, steam {on},
extra_chairs {on}. Story keys: scene_of, scenes, numbers, room, night_shots, steam_shots.
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
NUM_PITCH = 0.235
NUM_H = 0.32
NUM_W = 0.185
NUM_T = 0.055
NUM_GLOW = 3.4


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
    ox, oy, oyaw = story["room"]["old_chair"]
    ctx["old_chair"] = chair(kit, M, "old chair", ox, oy, oyaw)
    ctx["old_base"] = (ox, oy, oyaw)
    ctx["extra_chair"] = chair(kit, M, "extra chair", -6.0, 0.0, -90)
    # papers: Tam's page (ruled, with scribble strokes), my blank forms, a reader's page that turns
    pm = img_mat(kit, "tam page", page_image(True))
    quad_uv(kit, "tam page", (0.3, 0.4), (-7.0, -0.28, 0.784), pm)
    fm = img_mat(kit, "blank form", page_image(False))
    quad_uv(kit, "form a", (0.3, 0.4), (3.3, -4.55, 0.784), fm, rot=(0, 0, 0.1))
    quad_uv(kit, "form b", (0.3, 0.4), (2.85, -4.75, 0.784), fm, rot=(0, 0, -0.15))
    quad_uv(kit, "reader page", (0.3, 0.4), (1.5, -0.9, 0.784), fm, rot=(0, 0, math.pi / 2))
    piv = kit.empty("page pivot", (1.62, -0.9, 0.79))
    leaf = quad_uv(kit, "page leaf", (0.3, 0.4), (0.2, 0.0, 0.002), fm, piv, rot=(0, 0, math.pi / 2))
    leaf.scale = (1, 1, 1)
    ctx["page"] = piv
    # the Negative's key (cold, from the side) and rim (cool, behind it); its table lamp is dead
    kit.light("seatglow", "POINT", (-7.0, 0.55, 1.5), 110.0, "#ffc77a", size=0.2, shadow=False)
    kit.light("neg_key", "SPOT", (0, 0, 3), 0.0, "#a9c4e8", size=0.12, spot=34, blend=0.6)
    kit.light("neg_rim", "SPOT", (0, 0, 3), 0.0, "#8fb0e0", size=0.1, spot=40, blend=0.5)


# ------------------------------------------------------------------------------------------------ the other scenes


def scene_steps(kit, ctx, M, O):
    ox, oy = O
    kit.box("steps ground", (60, 30, 0.2), (ox, oy - 8, -0.1), M["plat"])
    for i in range(6):
        fy = 1.0 - 0.55 * (i + 1)
        wbox(kit, f"step{i}", (ox - 5.0, oy + fy, 0.0), (ox + 5.0, oy + 5.0, 0.16 * (6 - i)), M["stone"])
    wbox(kit, "library wall", (ox - 9, oy + 5.0, 0.0), (ox + 9, oy + 5.6, 8.0), M["stone"])
    for sx in (-3.2, 3.2):
        kit.cyl(f"column{sx}", 0.42, 6.6, (ox + sx, oy + 4.2, 3.9), M["stone"], n=24)
    wbox(kit, "lintel", (ox - 4.4, oy + 3.7, 7.1), (ox + 4.4, oy + 5.0, 7.8), M["stone"])
    wbox(kit, "library door", (ox - 1.1, oy + 4.95, 0.96), (ox + 1.1, oy + 5.02, 4.2), M["oakd"])
    # a bread stand (a tray of plain loaves) at the foot of the steps
    kit.box("bread table", (1.1, 0.6, 0.06), (ox - 0.9, oy - 3.3, 0.9), M["oak"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"bread leg{sx}{sy}", (0.05, 0.05, 0.9), (ox - 0.9 + sx * 0.5, oy - 3.3 + sy * 0.25, 0.45), M["oakd"])
    for k in range(5):
        kit.box(f"loaf{k}", (0.2, 0.34, 0.12), (ox - 1.25 + k * 0.17, oy - 3.3, 0.99), M["loaf"], bevel=0.05, rot=(0, 0, 0.2 * (k % 2 - 0.5)))
    kit.light("sun", "SUN", (ox + 8, oy - 12, 14), 2.8, "#fff0d4")
    kit.aim(kit.LIGHTS["sun"]["obj"], (ox, oy, 1.0))
    kit.light("sunfill", "AREA", (ox - 6, oy - 12, 6), 260.0, "#cfe0ff", size=8.0)
    kit.aim(kit.LIGHTS["sunfill"]["obj"], (ox, oy, 1.5))


def room_box(kit, M, O, x0, x1, y0, y1, h, wall, floor, ceil=None):
    ox, oy = O
    kit.box("floor", (x1 - x0, y1 - y0, 0.1), (ox + (x0 + x1) / 2, oy + (y0 + y1) / 2, -0.05), floor)
    kit.box("ceiling", (x1 - x0 + 0.4, y1 - y0 + 0.4, 0.1), (ox + (x0 + x1) / 2, oy + (y0 + y1) / 2, h + 0.05), ceil or wall)
    kit.box("wall n", (x1 - x0 + 0.4, 0.2, h), (ox + (x0 + x1) / 2, oy + y1 + 0.1, h / 2), wall)
    kit.box("wall s", (x1 - x0 + 0.4, 0.2, h), (ox + (x0 + x1) / 2, oy + y0 - 0.1, h / 2), wall)
    kit.box("wall e", (0.2, y1 - y0, h), (ox + x1 + 0.1, oy + (y0 + y1) / 2, h / 2), wall)
    kit.box("wall w", (0.2, y1 - y0, h), (ox + x0 - 0.1, oy + (y0 + y1) / 2, h / 2), wall)


def scene_party(kit, ctx, M, O):
    ox, oy = O
    room_box(kit, M, O, -3.6, 3.6, -4.8, 2.6, 2.7, M["cream"], M["floorlight"])
    kit.box("sofa", (2.2, 0.9, 0.45), (ox - 2.2, oy + 1.9, 0.225), M["sofa"], bevel=0.05)
    kit.box("sofa back", (2.2, 0.22, 0.6), (ox - 2.2, oy + 2.35, 0.75), M["sofa"], bevel=0.05)
    kit.box("side table", (0.7, 0.7, 0.6), (ox + 2.6, oy + 1.8, 0.3), M["oak"])
    # steady string lights: a swag of small warm bulbs along the back wall and one across the ceiling
    for s_i, (z0, dz) in enumerate(((2.55, 0.35), (2.35, 0.3))):
        n = 15
        for k in range(n + 1):
            u = k / n
            x = -3.3 + 6.6 * u
            z = z0 - dz * math.sin(math.pi * u)
            kit.sphere(f"bulb{s_i}.{k}", 0.05, (ox + x, oy + 2.45 - 0.5 * s_i, z), M["warm"], seg=8)
            if k:
                u0 = (k - 1) / n
                x0 = -3.3 + 6.6 * u0
                z0_ = z0 - dz * math.sin(math.pi * u0)
                kit.box(f"wire{s_i}.{k}", (0.012, 0.012, 0.012), (ox + (x + x0) / 2, oy + 2.45 - 0.5 * s_i, (z + z0_) / 2), M["wire"])
    kit.light("warm1", "POINT", (ox - 1.6, oy - 0.5, 2.3), 150.0, "#ffc88a", size=0.3)
    kit.light("warm2", "POINT", (ox + 1.6, oy - 0.5, 2.3), 150.0, "#ffc88a", size=0.3)
    kit.light("front", "AREA", (ox, oy - 4.4, 2.3), 150.0, "#ffe0b8", size=3.0)
    kit.aim(kit.LIGHTS["front"]["obj"], (ox, oy, 1.6))


def scene_station(kit, ctx, M, O):
    ox, oy = O
    wbox(kit, "platform", (ox - 14, oy - 7, -0.6), (ox + 14, oy + 1.4, 0.0), M["plat"])
    wbox(kit, "line", (ox - 14, oy + 0.7, 0.0), (ox + 14, oy + 0.85, 0.012), M["yellow"])
    wbox(kit, "track bed", (ox - 14, oy + 1.4, -1.2), (ox + 14, oy + 6, -0.5), M["dark"])
    # a plain carriage with an open door: no signs, no route boards
    cy0, cy1 = oy + 1.8, oy + 4.2
    dx0, dx1 = ox - 0.4, ox + 1.0
    wbox(kit, "carriage l", (ox - 9, cy0, 0.45), (dx0, cy1, 3.5), M["train"])
    wbox(kit, "carriage r", (dx1, cy0, 0.45), (ox + 9, cy1, 3.5), M["train"])
    wbox(kit, "carriage top", (dx0, cy0, 2.7), (dx1, cy1, 3.5), M["train"])
    wbox(kit, "carriage floor", (dx0, cy0, 0.45), (dx1, cy1, 0.6), M["train"])
    wbox(kit, "carriage back", (dx0, cy1 - 0.2, 0.6), (dx1, cy1, 2.7), M["train_in"])
    wbox(kit, "carriage step", (dx0 + 0.1, oy + 1.4, 0.2), (dx1 - 0.1, cy0, 0.3), M["plat"])
    wbox(kit, "carriage roof", (ox - 9, cy0, 3.5), (ox + 9, cy1, 3.7), M["slated"])
    kit.cyl("post", 0.07, 3.6, (ox - 3.4, oy + 0.4, 1.8), M["iron"], n=12)
    kit.box("post cap", (0.4, 0.4, 0.08), (ox - 3.4, oy + 0.4, 3.6), M["iron"])
    # the suitcase that stands beside her (not held)
    kit.box("suitcase", (0.5, 0.22, 0.7), (ox + 1.0, oy - 0.15, 0.35), M["suit"], bevel=0.03)
    kit.box("suitcase handle", (0.2, 0.04, 0.05), (ox + 1.0, oy - 0.15, 0.74), M["dark"])
    kit.light("sky", "AREA", (ox, oy - 2, 7), 900.0, "#dde7ee", size=10.0)
    kit.aim(kit.LIGHTS["sky"]["obj"], (ox, oy, 0))
    kit.light("sunf", "SPOT", (ox + 3, oy - 7, 3.5), 350.0, "#fff0dc", size=0.5, spot=70, blend=0.6)
    kit.aim(kit.LIGHTS["sunf"]["obj"], (ox, oy, 1.6))


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


def scene_kitchen(kit, ctx, M, O):
    ox, oy = O
    room_box(kit, M, O, -2.4, 2.4, -3.6, 2.2, 2.6, M["cream"], M["tile"])
    kit.box("kitchen table", (1.1, 0.8, 0.05), (ox, oy + 0.2, 0.745), M["oak"], bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"kt leg{sx}{sy}", (0.06, 0.06, 0.72), (ox + sx * 0.5, oy + 0.2 + sy * 0.34, 0.36), M["oakd"])
    kit.cyl("cake", 0.15, 0.1, (ox, oy + 0.05, 0.82), M["cake"], n=24)
    kit.cyl("cake top", 0.155, 0.02, (ox, oy + 0.05, 0.87), M["white"], n=24)
    kit.cyl("candle", 0.011, 0.09, (ox, oy + 0.05, 0.93), M["white"], n=8)
    kit.sphere("flame", 0.017, (ox, oy + 0.05, 0.99), M["flame"], seg=8)
    kit.box("kitchen window", (1.2, 0.06, 1.0), (ox + 1.0, oy + 2.08, 1.6), M["bright"])
    kit.box("kitchen window frame", (1.34, 0.05, 1.14), (ox + 1.0, oy + 2.12, 1.6), M["oakd"])
    kit.light("kwarm", "POINT", (ox, oy - 0.2, 2.1), 55.0, "#ffcf90", size=0.2)
    kit.light("kfill", "AREA", (ox, oy - 3.4, 2.2), 80.0, "#ffe6c8", size=2.5)
    kit.aim(kit.LIGHTS["kfill"]["obj"], (ox, oy + 0.5, 1.4))
    kit.light("kwin", "AREA", (ox + 1.0, oy + 1.6, 1.7), 90.0, "#cfe0ff", size=1.2)
    kit.aim(kit.LIGHTS["kwin"]["obj"], (ox, oy - 1.0, 1.0))


def scene_street(kit, ctx, M, O):
    ox, oy = O
    kit.box("street ground", (50, 12, 0.2), (ox, oy, -0.1), M["cobble"])
    for sy, nm in ((4.6, "n"), (-4.6, "s")):
        wbox(kit, f"row {nm}", (ox - 25, oy + sy - 0.4, 0.0), (ox + 25, oy + sy + 0.4, 6.5), M["brick"])
        for k in range(-9, 10):
            kit.box(f"win{nm}{k}", (0.9, 0.05, 1.2), (ox + k * 2.6, oy + sy - math.copysign(0.42, sy), 2.6), M["bright"])
    for k, lx in enumerate((-6.0, 0.5, 7.0)):
        kit.cyl(f"lamppost{k}", 0.06, 3.4, (ox + lx, oy + 3.7, 1.7), M["iron"], n=10)
        kit.sphere(f"streetglobe{k}", 0.16, (ox + lx, oy + 3.7, 3.5), M["lamp_glass_gold"], seg=10)
    kit.light("overcast", "AREA", (ox, oy, 9), 1100.0, "#9fb0be", size=14.0)
    kit.aim(kit.LIGHTS["overcast"]["obj"], (ox, oy, 0))
    kit.light("sfront", "AREA", (ox + 1.5, oy - 5.5, 3.5), 300.0, "#c8d4e0", size=5.0)
    kit.aim(kit.LIGHTS["sfront"]["obj"], (ox, oy, 1.6))


def scene_flat(kit, ctx, M, O):
    ox, oy = O
    room_box(kit, M, O, -3.0, 3.0, -3.0, 3.0, 2.6, M["cream"], M["floorlight"])
    kit.box("sofa seat", (2.0, 0.9, 0.45), (ox + 1.2, oy - 2.2, 0.225), M["sofa"], bevel=0.05)
    kit.box("sofa back", (2.0, 0.22, 0.62), (ox + 1.2, oy - 2.62, 0.78), M["sofa"], bevel=0.05)
    for sx in (-1, 1):
        kit.box(f"sofa arm{sx}", (0.22, 0.9, 0.62), (ox + 1.2 + sx * 1.1, oy - 2.2, 0.31), M["sofa"], bevel=0.05)
    kit.box("counter", (0.7, 2.4, 0.9), (ox + 2.65, oy + 1.0, 0.45), M["oak"])
    kit.box("counter top", (0.76, 2.46, 0.05), (ox + 2.65, oy + 1.0, 0.925), M["oakd"])
    kit.cyl("kettle", 0.1, 0.17, (ox + 2.65, oy + 1.0, 1.05), M["steel"], n=18)
    kit.cyl("kettle lid", 0.07, 0.04, (ox + 2.65, oy + 1.0, 1.15), M["steel"], n=18)
    kit.box("kettle spout", (0.12, 0.04, 0.05), (ox + 2.53, oy + 1.0, 1.08), M["steel"], rot=(0, 0, 0))
    kit.box("kettle handle", (0.03, 0.04, 0.14), (ox + 2.76, oy + 1.0, 1.1), M["dark"])
    ctx["steam"] = [kit.sphere(f"steam{k}", 0.035, (ox + 2.53, oy + 1.0, 1.2), M["steam"], seg=12) for k in range(6)]
    # the standing lamp and the rainy window
    kit.cyl("floor lamp pole", 0.025, 1.5, (ox - 2.4, oy - 1.4, 0.75), M["iron"], n=8)
    kit.cyl("floor lamp shade", 0.2, 0.32, (ox - 2.4, oy - 1.4, 1.62), M["fshade"], n=16, r2=0.15)
    ctx["flat_shade"] = M["fshade_em"]
    kit.box("flat window", (0.06, 2.0, 1.4), (ox - 2.95, oy + 0.4, 1.5), M["wwin"])
    for k in (-1, 0, 1):
        kit.box(f"flat muntin{k}", (0.05, 0.04, 1.4), (ox - 2.92, oy + 0.4 + k * 0.5, 1.5), M["oakd"])
    kit.box("flat muntin h", (0.05, 2.0, 0.04), (ox - 2.92, oy + 0.4, 1.5), M["oakd"])
    ctx["flat_win"] = M["wwin_em"]
    kit.light("flamp", "POINT", (ox - 2.2, oy - 1.3, 1.6), 90.0, "#ffbf78", size=0.2)
    kit.light("fwin", "AREA", (ox - 2.8, oy + 0.4, 1.6), 140.0, "#9bb4dc", size=1.6)
    kit.aim(kit.LIGHTS["fwin"]["obj"], (ox, oy + 0.4, 1.0))
    kit.light("ffill", "AREA", (ox + 1.5, oy + 2.5, 2.4), 120.0, "#ffe2c0", size=3.0)
    kit.aim(kit.LIGHTS["ffill"]["obj"], (ox + 1.2, oy - 1.5, 1.0))
    kit.light("ffront", "AREA", (ox + 0.5, oy - 0.5, 2.5), 90.0, "#ffe2c0", size=3.0)
    kit.aim(kit.LIGHTS["ffront"]["obj"], (ox + 1.2, oy - 2.2, 1.2))


# ------------------------------------------------------------------------------------------------ the numbers


SEG = {"0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg", "5": "acdfg", "6": "acdefg", "7": "abc",
       "8": "abcdefg", "9": "abcdfg"}


def _segments():
    w, h, t = NUM_W, NUM_H, NUM_T
    return {"a": (0, h / 2 - t / 2, w, t), "d": (0, -h / 2 + t / 2, w, t), "g": (0, 0, w, t),
            "b": (w / 2 - t / 2, h / 4, t, h / 2 + t / 2), "c": (w / 2 - t / 2, -h / 4, t, h / 2 + t / 2),
            "f": (-w / 2 + t / 2, h / 4, t, h / 2 + t / 2), "e": (-w / 2 + t / 2, -h / 4, t, h / 2 + t / 2)}


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
                for sname, (cx, cy, sx, sy) in _segments().items():
                    o = 0.012
                    verts = kit.box_verts(sx + 2 * o, sy + 2 * o, 0.012, (cx, cy, -0.02)) + kit.box_verts(sx, sy, 0.03, (cx, cy, 0.0))
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
        base = V((st["x"], st["y"], st["z"] + 2.12 + (nzc["v"] if nzc else 0.0)))
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
                lay.location.x = -0.065 if ch == "1" else 0.0   # the one's bar sits at its cell's right edge: pull it in
                for sn, o in segs.items():
                    o.hide_render = sn not in lit


# ------------------------------------------------------------------------------------------------ build


def build(kit, story, tl):
    ctx = {"scene_objs": {}}
    M = materials(kit)
    ctx["M"] = M
    O = {k: tuple(v) for k, v in story["scenes"].items()}
    builders = {"room": lambda: build_room(kit, ctx, M, story), "steps": lambda: scene_steps(kit, ctx, M, O["steps"]),
                "party": lambda: scene_party(kit, ctx, M, O["party"]), "station": lambda: scene_station(kit, ctx, M, O["station"]),
                "door": lambda: scene_door(kit, ctx, M, O["door"]), "kitchen": lambda: scene_kitchen(kit, ctx, M, O["kitchen"]),
                "street": lambda: scene_street(kit, ctx, M, O["street"]), "flat": lambda: scene_flat(kit, ctx, M, O["flat"])}
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

SKY = {"steps": ("#8ec5f0", 0.9), "door": ("#9ccdf0", 0.8), "station": ("#b4c2cc", 1.0), "street": ("#6f7d8a", 0.9)}


def _extras(kit, ctx):
    """Parts the rig doesn't have: Luke's headphones, Tam's pencil, Ossie's moustache."""
    ctx["extras_done"] = True
    M = ctx["M"]
    R, H = faces.HEAD_R, faces.HEAD_H
    top = H / 2
    hg = bpy.data.objects.get("tam.headg")
    if hg is not None:
        kit.box("tam.pencil", (0.07, 0.07, 0.55), (R - 0.1, 0.12, 0.28), M["pencil"], hg, rot=(0.5, 0.0, 0.0), bevel=0.01)
    hg = bpy.data.objects.get("ossie.headg")
    if hg is not None:
        kit.box("ossie.mous", (0.5, 0.1, 0.12), (0, -R - 0.005, -0.16), M["grey"], hg, bevel=0.04)
        for sx in (-1, 1):
            kit.box(f"ossie.mous{sx}", (0.16, 0.1, 0.1), (sx * 0.28, -R + 0.06, -0.24), M["grey"], hg, rot=(0, 0, sx * 0.4), bevel=0.03)
    # headphones (slate, over the ear, no logo): on the head, or hung round the neck
    ctx["ph_head"], ctx["ph_neck"] = [], []
    hg = bpy.data.objects.get("me.headg")
    tor = bpy.data.objects.get("me.torso")
    if hg is not None:
        for sx in (-1, 1):
            ctx["ph_head"].append(kit.box(f"me.phbar{sx}", (0.1, 0.16, top + 0.17 - 0.05), (sx * (R + 0.14), 0.0, (top + 0.17 + 0.05) / 2), M["slate"], hg, bevel=0.03))
            ctx["ph_head"].append(kit.box(f"me.phcup{sx}", (0.3, 0.56, 0.62), (sx * (R + 0.2), 0.05, -0.05), M["slated"], hg, bevel=0.1))
        ctx["ph_head"].append(kit.box("me.phtop", (2 * R + 0.38, 0.16, 0.1), (0, 0.0, top + 0.17), M["slate"], hg, bevel=0.03))
    if tor is not None:
        ctx["ph_neck"].append(kit.box("me.nkback", (1.6, 0.14, 0.14), (0, 0.45, 2.02), M["slate"], tor, bevel=0.04))
        for sx in (-1, 1):
            ctx["ph_neck"].append(kit.box(f"me.nkside{sx}", (0.14, 0.95, 0.14), (sx * 0.78, -0.02, 2.0), M["slate"], tor, bevel=0.04))
            ctx["ph_neck"].append(kit.box(f"me.nkcup{sx}", (0.32, 0.42, 0.55), (sx * 0.78, -0.55, 1.7), M["slated"], tor, bevel=0.1))


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
        for c in tl["cues"]:
            if c["name"] == "numz":
                by.setdefault("_numz_" + c["who"], []).append(c)
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
    # ---- people: sitting, leaning, the rig's black lenses, the extras
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
    # ---- headphones
    ph = _last(_cues(tl, "phones"), t)
    mode = ph["mode"] if ph else "head"
    for ob in ctx["ph_head"]:
        ob.hide_render = not (mode in ("head", "half") and inscene.get("me", False))
    for ob in ctx["ph_neck"]:
        ob.hide_render = not (mode == "neck" and inscene.get("me", False))
    # ---- the closing timer: every table lamp together; the dome's dusk
    lamps = _level(tl, "lamps", t, 1.0)
    dome = _level(tl, "dome", t, 1.0)
    dead_c = _last(_cues(tl, "dead"), t)
    dead = set(dead_c["tables"]) if dead_c else set()
    for lp in ctx["lamps"]:
        g = 0.0 if lp["table"] in dead else lamps
        over[lp["light"]] = g
        lp["em"].inputs["Strength"].default_value = lp["base_em"] * (0.04 if lp["table"] in dead else lamps) + 0.05
    over["dome"] = dome * (0.4 + 0.6 * lamps)
    over["fill"] = dome * (0.25 + 0.75 * lamps)
    over["window"] = dome
    over["seatglow"] = _level(tl, "seat", t, 0.0)
    ctx["pane_em"].inputs["Strength"].default_value = 1.5 * (0.25 + 0.75 * dome)
    ctx["M"]["win_em"].inputs["Strength"].default_value = 1.2 * (0.12 + 0.88 * dome ** 1.5)
    # ---- the old chair is pushed back, the extra chair slides in, the page turns
    oc = _last(_cues(tl, "oldchair"), t)
    d = oc["d"] if oc else 0.0
    ox, oy, oyaw = ctx["old_base"]
    ctx["old_chair"].location = (ox, oy + d, 0.0)
    ec = _last(_cues(tl, "extra_chairs"), t)
    ctx["extra_chair"].hide_render = not (ec and ec["on"] and scene == "room")
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
        head = V((s["x"], s["y"], s["z"] + 1.35)) + f * 0.25 * (1 + math.sin(math.radians(ac._held(tl["acting"]["neg"], "bend", t, 0.0))))
        bend = ac._held(tl["acting"]["neg"], "bend", t, 0.0)
        head += f * 0.55 * math.sin(math.radians(bend))
        for nm, pos, w in (("neg_key", head + sd * 1.7 + f * 0.8 + V((0, 0, 1.1)), 150.0),
                           ("neg_rim", head - f * 1.5 - sd * 0.5 + V((0, 0, 1.4)), 260.0)):
            ob = K.LIGHTS[nm]["obj"]
            ob.location = pos
            ob.rotation_euler = (head - pos).to_track_quat("-Z", "Y").to_euler()
            K.LIGHTS[nm]["base"] = w
            over[nm] = 1.0
    # ---- the flat at night, the kettle's steam
    night = shot in story.get("night_shots", [])
    if ctx.get("flat_win") is not None:
        ctx["flat_win"].inputs["Strength"].default_value = 0.35 if night else 1.4
        ctx["flat_shade"].inputs["Strength"].default_value = 2.2 if night else 3.0
    over["fwin"] = 0.25 if night else 1.0
    over["flamp"] = 0.8 if night else 1.0
    stc = shot in story.get("steam_shots", [])
    ox2, oy2 = story["scenes"]["flat"]
    for k, sp in enumerate(ctx["steam"]):
        ph_ = (t * 0.55 + k / len(ctx["steam"])) % 1.0
        sp.location = (ox2 + 2.53 + 0.02 * math.sin(6 * ph_ + k), oy2 + 1.0 + 0.02 * math.cos(5 * ph_ + k), 1.2 + 0.55 * ph_)
        sc = 0.6 + 2.2 * ph_
        sp.scale = (sc, sc, sc)
        sp.hide_render = not (stc and scene == "flat") or ph_ > 0.97
    # ---- plant 2: my 1 warms a little (a 0.5 s ramp up to 120% and back)
    wc = _last(_cues(tl, "warm"), t)
    for who, dd in ctx["num"].items():
        f = 1.0
        if who == "me" and wc is not None:
            x = t - wc["t"]
            if 0 <= x <= 1.0:
                f = 1.0 + 0.2 * math.sin(math.pi * x)
        dd["em"].inputs["Strength"].default_value = NUM_GLOW * f
    update_numbers(ctx, tl, t, states, inscene, True)
    return over
