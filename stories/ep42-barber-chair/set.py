"""A town where everyone hums one note, and the three-chair barbershop on its high street.

Places (metres, floor z = 0, the camera's story coordinates):
- the high street runs along x: pavement y 0.2 to 2.0 on the north side, cobbled road to y -14; brick shopfronts on both
  sides, lamp posts, a parked double-deck bus, a market stall.
- the barbershop is the narrow shop in the north row: x -1.9 to 1.9, y 2.0 (front wall: big window, glass door) to 11.4
  (back wall: the sink). Left wall (x = -1.9): counter and the long mirror. The three barber chairs stand in a row at
  x = -0.2, y = 4.4 (Len's), 6.1 (Sid's) and 7.8 (the third), facing the mirror (-x). The waiting chairs are along the
  right wall by the door, the coat stand beside them, the sink at the back with its brass lamp.
- far rooms: the cafe (60, 0), the bus (-60, 0), Pat's flat (0, 60) and our kitchen (60, 60).

THE RINGS: a thin torus a hand above every head in that person's colour, rebuilt every frame so a slow wave travels
round its shape (never a change in brightness). Len's grows thinner and dimmer by cues; mine is clear glass until the
violet fades up. THE CREATURE (creature.py) is never ringed.

Cues read here (animate): row0 / row1 / row2 {to, dur}: the shop's three light rows (front, middle, back);
len_em / len_th {to, dur}: Len's ring brightness and thickness; violet {to, dur}: my ring; wobble {to, dur}: Sid's ring;
creature {on, where: "wait"|"sid"|"third", mouth}; swivel {to: degrees, dur}: the third chair's turn; cape {on}: the folded
cape on the third chair; broom {on}: Len's sweeping; bell {}: the door bell swings; door {to, dur}: the front door's angle;
hair {short}: my neat new hair. Story keys: "scenes" {shot: scene}, "shotlook" {shot: {...}} (see shot_look).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector as V

sys.path.insert(0, str(Path(__file__).resolve().parent))
import creature as CR  # noqa: E402

from blocky import acting as ac  # noqa: E402
from blocky import faces  # noqa: E402

# ------------------------------------------------------------------------------------------------ places
SX0, SX1, SY0, SY1, SH = -1.9, 1.9, 2.0, 11.4, 3.0
CHX = -0.2
CHY = {"len": 4.4, "sid": 6.1, "third": 7.8}
WAIT = [(1.30, 2.85), (1.30, 4.35), (1.30, 5.85)]
SINK = (0.7, 11.0)
CAFE, BUS, FLAT, KIT = (60.0, 0.0), (-60.0, 0.0), (0.0, 60.0), (60.0, 60.0)

# ring colours (nobody's neighbour shares a colour); None = clear glass
RINGS = {
    "me": None, "len": "#ffb030", "sid": "#7fbf4a", "mum": "#ff8aa0", "pat": "#ffb48a", "ostro": "#8a3d8f",
    "c1": "#4fd0e0", "c2": "#e05cc0", "c3": "#b8e04a", "c4": "#ff6a4a", "c5": "#5a8cff", "c6": "#ffd34a",
    "c7": "#4ae0b0", "c8": "#a89aff", "c9": "#ff9a3c", "c10": "#e8708a", "c11": "#9ad8ff", "c12": "#c8e06a",
}
EXTRA_COLORS = ["#4fd0e0", "#e05cc0", "#b8e04a", "#ff6a4a", "#5a8cff", "#ffd34a", "#4ae0b0", "#a89aff", "#ff9a3c", "#e8708a",
                "#9ad8ff", "#c8e06a", "#ffb030", "#7fbf4a", "#ff8aa0", "#8a3d8f"]
RING_R, RING_TUBE = 0.14, 0.0075          # 0.28 m across, 1.5 cm thick


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


# ------------------------------------------------------------------------------------------------ helpers
def wbox(kit, name, lo, hi, mat, parent=None):
    c = tuple((a + b) / 2 for a, b in zip(lo, hi))
    s = tuple(b - a for a, b in zip(lo, hi))
    return kit.mesh_obj(name, kit.box_verts(*s, c), kit.BOX_FACES, mat, parent)


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


def pane_mat(kit, name="pane", amount=0.07):
    """Window glass: nearly all see-through, a faint reflection."""
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.03
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs["Fac"].default_value = amount
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return m


def spiral_mat(kit, name, c1, c2):
    """A barber's pole: diagonal stripes round a vertical cylinder (object space)."""
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.25
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    at = nt.nodes.new("ShaderNodeMath")
    at.operation = "ARCTAN2"
    nt.links.new(sep.outputs["Y"], at.inputs[0])
    nt.links.new(sep.outputs["X"], at.inputs[1])
    a2 = nt.nodes.new("ShaderNodeMath")
    a2.operation = "MULTIPLY"
    a2.inputs[1].default_value = 1.0 / (2 * math.pi)
    nt.links.new(at.outputs[0], a2.inputs[0])
    zz = nt.nodes.new("ShaderNodeMath")
    zz.operation = "MULTIPLY"
    zz.inputs[1].default_value = 3.2
    nt.links.new(sep.outputs["Z"], zz.inputs[0])
    sm = nt.nodes.new("ShaderNodeMath")
    sm.operation = "ADD"
    nt.links.new(a2.outputs[0], sm.inputs[0])
    nt.links.new(zz.outputs[0], sm.inputs[1])
    fr = nt.nodes.new("ShaderNodeMath")
    fr.operation = "FRACT"
    nt.links.new(sm.outputs[0], fr.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = kit.col(c1)
    ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements[1].color = kit.col(c2)
    nt.links.new(fr.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m


# ------------------------------------------------------------------------------------------------ materials
def materials(kit):
    M = {}
    M["brick"] = kit.bricks("#8a4a38", "#6b3428", "#5a554e", 1.0, "brick")
    M["brick2"] = kit.bricks("#6e5546", "#55402f", "#4f4a44", 1.0, "brick2")
    M["cobble"] = kit.cobbles("#4a4d56", "#7d7a74", "#1c1c20", 2.6, 0.2, "cobbles")
    M["pave"] = kit.concrete("#9a9aa0", 1.3, 0.35, "pavement")
    M["kerb"] = kit.concrete("#7e7d7b", 1.0, 0.3, "kerb")
    M["checker"] = kit.checker("#0d0d0f", "#e9e6df", 3.33, "checker floor", 0.25)
    M["sage"] = kit.grime("#a9bfa3", 0.82, 6.0, "sage tile", 0.35)
    M["plaster"] = kit.grime("#d8cfbc", 0.8, 3.0, "plaster", 0.9)
    M["ceil"] = kit.grime("#e4dccb", 0.85, 2.0, "ceiling", 0.9)
    M["wood"] = kit.planks("#4a2f1c", "#2f1c10", 1.0, "Z", "dark wood", 0.55)
    M["counter"] = kit.planks("#5a3a22", "#3a2414", 1.0, "X", "counter wood", 0.4)
    M["floorwood"] = kit.planks("#7a5434", "#573a22", 1.0, "X", "floor wood", 0.6)
    M["leather"] = kit.plastic("#6b1f24", 0.38, "oxblood leather", 0.5)
    M["chrome"] = kit.metal("#c9ccd1", 0.15, "chrome")
    M["brass"] = kit.metal("#c8963c", 0.3, "brass")
    M["steel"] = kit.metal("#aeb2b6", 0.25, "steel")
    M["porcelain"] = kit.plastic("#f1f1ec", 0.15, "porcelain", 0.6)
    M["mirror"] = kit.metal("#e8eef0", 0.02, "mirror")
    M["black"] = kit.plastic("#08080a", 0.5, "black plastic", 0.3)
    M["towel"] = kit.plastic("#f0ece2", 0.9, "towel", 0.0)
    M["cream"] = kit.plastic("#e8dcc0", 0.6, "cream paint", 0.2)
    M["maroon"] = kit.plastic("#5a1a22", 0.5, "maroon paint", 0.3)
    M["green"] = kit.plastic("#1d3a30", 0.55, "bottle green", 0.3)
    M["navy"] = kit.plastic("#1c2a44", 0.55, "navy paint", 0.3)
    M["iron"] = kit.plastic("#1a1c20", 0.45, "iron", 0.5)
    M["dark_glass"] = kit.plastic("#101a26", 0.1, "dark glass", 0.8)
    M["pole"] = spiral_mat(kit, "barber pole", "#6b1f24", "#efe6d2")
    M["pane"] = pane_mat(kit)
    M["cardboard"] = kit.plastic("#a98a5e", 0.9, "plain box", 0.0)
    M["sofa"] = kit.plastic("#6a4f66", 0.9, "sofa", 0.0)
    M["bookshelf"] = kit.planks("#6a4a30", "#4a321e", 1.0, "Z", "shelf wood", 0.7)
    M["seatmaroon"] = kit.plastic("#7a2a32", 0.8, "bus seat", 0.1)
    M["busfloor"] = kit.plastic("#3a3c40", 0.8, "bus floor", 0.1)
    M["cafewall"] = kit.grime("#c9b48f", 0.8, 3.0, "cafe wall", 0.9)
    M["kitwall"] = kit.grime("#c8d0bf", 0.82, 3.0, "kitchen wall", 0.9)
    M["bristle"] = kit.plastic("#8a6a3a", 0.9, "bristle", 0.0)
    M["fur"] = kit.plastic("#222428", 0.8, "dark", 0.0)
    M["cape_oxblood"] = kit.plastic("#5b1620", 0.55, "oxblood cape", 0.2)
    M["stall"] = kit.plastic("#d8ccb0", 0.8, "stall cloth", 0.0)
    return M


# ------------------------------------------------------------------------------------------------ the street
def build_street(kit, ctx, M):
    G = ctx["groups"]["street"]

    def add(ob):
        G.append(ob)
        return ob

    add(wbox(kit, "road", (-70, -14, -0.2), (70, 0.25, 0.0), M["cobble"]))
    add(wbox(kit, "pavement", (-70, 0.25, -0.2), (70, 2.0, 0.12), M["pave"]))
    add(wbox(kit, "kerb", (-70, 0.12, -0.05), (70, 0.3, 0.12), M["kerb"]))
    add(wbox(kit, "south pavement", (-70, -14.0, -0.2), (70, -12.0, 0.12), M["pave"]))
    # the north row (the shop's neighbours) and the south row
    add(wbox(kit, "north west a", (-70, SY0, 0), (-22.0, 14, 8.0), M["brick"]))
    add(wbox(kit, "north west b", (-18.2, SY0, 0), (SX0, 14, 8.0), M["brick"]))
    add(wbox(kit, "north west c", (-22.0, SY0 + 3.6, 0), (-18.2, 14, 8.0), M["brick"]))
    add(wbox(kit, "north west d", (-22.0, SY0, 2.85), (-18.2, 14, 8.0), M["brick"]))
    add(wbox(kit, "north east", (SX1, SY0, 0), (70, 14, 8.0), M["brick"]))
    add(wbox(kit, "shop upper", (SX0, SY0, SH), (SX1, 14, 8.0), M["brick"]))
    add(wbox(kit, "south row", (-70, -20, 0), (70, -14, 8.0), M["brick2"]))
    fas = [M["green"], M["navy"], M["maroon"], M["cream"], M["green"], M["navy"]]
    k = 0
    for x0 in list(np.arange(-34.0, -4.0, 4.0)) + list(np.arange(4.0, 34.0, 4.0)):
        f = fas[k % len(fas)]
        k += 1
        if x0 == -22.0:
            build_ostro(kit, ctx, M, x0, add, f)
            continue
        add(wbox(kit, f"fascia{k}", (x0 + 0.1, SY0 - 0.14, 2.65), (x0 + 3.6, SY0 - 0.02, 3.25), f))
        add(wbox(kit, f"shopwin{k}", (x0 + 0.4, SY0 - 0.04, 0.5), (x0 + 2.4, SY0 - 0.01, 2.4), M["dark_glass"]))
        add(wbox(kit, f"shopdoor{k}", (x0 + 2.7, SY0 - 0.04, 0.0), (x0 + 3.4, SY0 - 0.01, 2.3), M["wood"]))
        for z0 in (4.0, 5.9):
            for dx in (0.3, 2.0):
                add(wbox(kit, f"upwin{k}.{z0}.{dx}", (x0 + dx, SY0 - 0.04, z0), (x0 + dx + 1.3, SY0 - 0.01, z0 + 1.2), M["dark_glass"]))
    k = 0
    for x0 in np.arange(-32.0, 32.0, 4.0):
        k += 1
        f = fas[(k + 2) % len(fas)]
        add(wbox(kit, f"sfascia{k}", (x0 + 0.1, -14.0, 2.65), (x0 + 3.6, -13.86, 3.25), f))
        add(wbox(kit, f"swin{k}", (x0 + 0.4, -13.99, 0.5), (x0 + 3.2, -13.96, 2.4), M["dark_glass"]))
        for z0 in (4.0, 5.9):
            for dx in (0.3, 2.0):
                add(wbox(kit, f"supwin{k}.{z0}.{dx}", (x0 + dx, -13.99, z0), (x0 + dx + 1.3, -13.96, z0 + 1.2), M["dark_glass"]))
    # lamp posts on the north pavement (their lights are on at dusk)
    ctx["lampem"] = []
    for i, x in enumerate((-13.0, -7.0, 4.0, 9.5, 15.0)):
        add(kit.cyl(f"lamp{i} post", 0.05, 3.6, (x, 0.55, 1.8), M["iron"], n=10))
        add(kit.cyl(f"lamp{i} foot", 0.11, 0.5, (x, 0.55, 0.25), M["iron"], n=10))
        add(kit.box(f"lamp{i} arm", (0.05, 0.4, 0.05), (x, 0.7, 3.55), M["iron"]))
        mat, em = emit_mat(kit, f"lamp{i} glass", "#ffd29a", 4.0)
        add(kit.cyl(f"lamp{i} lantern", 0.13, 0.3, (x, 0.9, 3.45), mat, n=12, r2=0.17))
        add(kit.cyl(f"lamp{i} cap", 0.2, 0.06, (x, 0.9, 3.65), M["iron"], n=12))
        ctx["lampem"].append(em)
        kit.light(f"lamp{i}", "POINT", (x, 0.9, 3.3), 0.0, "#ffbe78", size=0.15)
    # the barbershop's front: a pole in oxblood and cream, no lettering anywhere
    add(kit.cyl("pole", 0.06, 0.95, (1.78, 1.86, 1.5), M["pole"], n=20))
    add(kit.cyl("pole cap top", 0.075, 0.05, (1.78, 1.86, 2.0), M["chrome"], n=16))
    add(kit.cyl("pole cap bot", 0.075, 0.05, (1.78, 1.86, 1.0), M["chrome"], n=16))
    add(kit.box("pole bracket", (0.04, 0.12, 0.04), (1.78, 1.94, 2.0), M["chrome"]))
    # the bus: plain cream over maroon, no route and no words
    bx, by = 8.0, -6.2
    bus = kit.empty("bus", (bx, by, 0))
    G.append(bus)
    for nm, sz, loc, mat in (("lower", (10.2, 2.5, 1.3), (0, 0, 0.9), M["maroon"]), ("mid", (10.2, 2.5, 1.0), (0, 0, 2.0), M["cream"]),
                             ("upper", (9.8, 2.4, 1.0), (0, 0, 3.05), M["cream"]), ("roof", (9.9, 2.45, 0.1), (0, 0, 3.6), M["maroon"]),
                             ("beltline", (10.25, 2.52, 0.12), (0, 0, 2.5), M["maroon"])):
        add(kit.box(f"bus {nm}", sz, loc, mat, bus, bevel=0.06))
    for i in range(6):
        for z in (2.0, 3.05):
            add(kit.box(f"bus win{i}.{z}", (1.2, 2.56, 0.6), (-4.0 + i * 1.6, 0, z), M["dark_glass"], bus))
    for sx in (-3.2, 3.2):
        for sy in (-1.25, 1.25):
            add(kit.cyl(f"bus wheel{sx}{sy}", 0.5, 0.3, (sx, sy, 0.5), M["black"], bus, rot=(math.pi / 2, 0, 0), n=20))
    # a market stall on the pavement: blank awning
    sx, sy = -6.0, 1.5
    add(kit.box("stall table", (2.4, 0.7, 0.9), (sx, sy + 0.1, 0.5), M["wood"], bevel=0.02))
    for dx in (-1.15, 1.15):
        add(kit.cyl(f"stall post{dx}", 0.03, 2.4, (sx + dx, sy + 0.35, 1.3), M["iron"], n=8))
    add(kit.box("stall awning", (2.6, 1.3, 0.06), (sx, sy, 2.45), M["stall"], rot=(0.18, 0, 0), bevel=0.02))
    for k in range(5):
        add(kit.box(f"stall crate{k}", (0.3, 0.3, 0.25), (sx - 0.9 + k * 0.45, sy + 0.1, 1.07), M["cardboard"], bevel=0.02))


def build_ostro(kit, ctx, M, x0, add, fascia):
    """Mr Ostrowski's shop: a glass window onto a small lit room (the panes shiver when he hums)."""
    add(wbox(kit, "ostro fascia", (x0 + 0.1, SY0 - 0.14, 2.65), (x0 + 3.6, SY0 - 0.02, 3.25), fascia))
    add(wbox(kit, "ostro floor", (x0 + 0.1, SY0, -0.05), (x0 + 3.8, SY0 + 3.6, 0.0), M["floorwood"]))
    add(wbox(kit, "ostro back", (x0 + 0.1, SY0 + 3.5, 0), (x0 + 3.8, SY0 + 3.6, 2.7), M["plaster"]))
    add(wbox(kit, "ostro left", (x0 + 0.1, SY0, 0), (x0 + 0.2, SY0 + 3.6, 2.7), M["plaster"]))
    add(wbox(kit, "ostro right", (x0 + 3.7, SY0, 0), (x0 + 3.8, SY0 + 3.6, 2.7), M["plaster"]))
    add(wbox(kit, "ostro ceil", (x0 + 0.1, SY0, 2.7), (x0 + 3.8, SY0 + 3.6, 2.8), M["ceil"]))
    for nm, lo, hi in (("a", (x0 + 0.1, SY0 - 0.02, 0.0), (x0 + 0.4, SY0 + 0.12, 2.7)), ("b", (x0 + 3.4, SY0 - 0.02, 0.0), (x0 + 3.8, SY0 + 0.12, 2.7)),
                       ("c", (x0 + 0.1, SY0 - 0.02, 0.0), (x0 + 3.8, SY0 + 0.12, 0.5)), ("d", (x0 + 0.1, SY0 - 0.02, 2.4), (x0 + 3.8, SY0 + 0.12, 2.7))):
        add(wbox(kit, f"ostro frame {nm}", lo, hi, M["wood"]))
    pane = wbox(kit, "ostro pane", (x0 + 0.4, SY0 + 0.0, 0.5), (x0 + 3.4, SY0 + 0.012, 2.4), M["pane"])
    add(pane)
    ctx["ostro_pane"] = (pane, pane.location.copy())
    for k in range(4):
        add(kit.box(f"ostro crate{k}", (0.5, 0.4, 0.4), (x0 + 0.8 + k * 0.7, SY0 + 3.1, 0.2), M["cardboard"], bevel=0.02))
    kit.light("ostro_l", "AREA", (x0 + 1.9, SY0 + 1.6, 2.6), 0.0, "#ffd9a0", size=2.0)
    kit.aim(kit.LIGHTS["ostro_l"]["obj"], (x0 + 1.9, SY0 + 1.6, 0.0))
    ctx["ostro_x0"] = x0


# ------------------------------------------------------------------------------------------------ the shop
def build_shop(kit, ctx, M):
    G = ctx["groups"]["shop"]
    ctx["groups"]["props"] = []

    def add(ob, grp="shop"):
        ctx["groups"][grp].append(ob)
        return ob

    wide = SX1 - SX0
    add(wbox(kit, "shop floor", (SX0, SY0, -0.05), (SX1, SY1, 0.0), M["checker"]))
    add(wbox(kit, "shop ceil", (SX0, SY0, SH), (SX1, SY1, SH + 0.1), M["ceil"]))
    add(wbox(kit, "wall right", (SX1 - 0.1, SY0, 0), (SX1, SY1, SH), M["sage"]))
    add(wbox(kit, "wall left", (SX0, SY0, 0), (SX0 + 0.1, SY1, SH), M["sage"]))
    add(wbox(kit, "wall back", (SX0, SY1 - 0.1, 0), (SX1, SY1, SH), M["sage"]))
    # the front wall around the window (x -1.65 .. 0.6, z 0.55 .. 2.4) and the glass door (x 0.85 .. 1.65)
    fw = M["plaster"]
    add(wbox(kit, "front a", (SX0, SY0, 0), (-1.65, SY0 + 0.15, SH), fw))
    add(wbox(kit, "front b", (0.6, SY0, 0), (0.85, SY0 + 0.15, SH), fw))
    add(wbox(kit, "front c", (1.65, SY0, 0), (SX1, SY0 + 0.15, SH), fw))
    add(wbox(kit, "front sill", (-1.65, SY0, 0), (0.6, SY0 + 0.15, 0.55), fw))
    add(wbox(kit, "front head", (-1.65, SY0, 2.4), (0.6, SY0 + 0.15, SH), fw))
    add(wbox(kit, "front dhead", (0.85, SY0, 2.25), (1.65, SY0 + 0.15, SH), fw))
    add(wbox(kit, "fascia board", (SX0, SY0 - 0.06, 2.62), (SX1, SY0, 3.0), M["green"]))
    # window frame and door frame (dark wood), the panes
    for nm, lo, hi in (("wf l", (-1.7, SY0 - 0.04, 0.5), (-1.62, SY0 + 0.1, 2.45)), ("wf r", (0.56, SY0 - 0.04, 0.5), (0.64, SY0 + 0.1, 2.45)),
                       ("wf b", (-1.7, SY0 - 0.04, 0.5), (0.64, SY0 + 0.1, 0.58)), ("wf t", (-1.7, SY0 - 0.04, 2.38), (0.64, SY0 + 0.1, 2.45)),
                       ("wf m", (-0.52, SY0 - 0.03, 0.55), (-0.48, SY0 + 0.08, 2.4)),
                       ("df l", (0.82, SY0 - 0.04, 0.0), (0.9, SY0 + 0.1, 2.28)), ("df r", (1.6, SY0 - 0.04, 0.0), (1.68, SY0 + 0.1, 2.28)),
                       ("df t", (0.82, SY0 - 0.04, 2.2), (1.68, SY0 + 0.1, 2.28))):
        add(wbox(kit, nm, lo, hi, M["wood"]))
    add(wbox(kit, "window pane", (-1.62, SY0 + 0.03, 0.58), (0.56, SY0 + 0.035, 2.38), M["pane"]))
    # the door: a leaf that swings on its hinge (x = 1.6)
    hinge = kit.empty("door hinge", (1.6, SY0 + 0.04, 0.0))
    ctx["door"] = hinge
    ctx["groups"]["shop"].append(hinge)
    for nm, lo, hi in (("dl l", (-0.76, -0.02, 0.0), (-0.7, 0.02, 2.18)), ("dl r", (-0.04, -0.02, 0.0), (0.0, 0.02, 2.18)),
                       ("dl b", (-0.76, -0.02, 0.0), (0.0, 0.02, 0.1)), ("dl t", (-0.76, -0.02, 2.1), (0.0, 0.02, 2.18)),
                       ("dl m", (-0.76, -0.02, 1.0), (0.0, 0.02, 1.05))):
        add(wbox(kit, nm, lo, hi, M["wood"]))
        ctx["groups"]["shop"][-1].parent = hinge
    pn = wbox(kit, "door pane", (-0.70, -0.005, 0.1), (-0.04, 0.005, 2.1), M["pane"])
    pn.parent = hinge
    add(pn)
    hnd = kit.cyl("door handle", 0.012, 0.2, (-0.12, -0.04, 1.05), M["brass"], hinge, n=8)
    add(hnd)
    # the bell on its spring over the door
    bell = kit.empty("bell pivot", (1.25, SY0 + 0.3, 2.2))
    ctx["bell"] = bell
    add(bell)
    add(kit.cyl("bell spring", 0.012, 0.3, (0, 0, -0.05), M["steel"], bell, n=8))
    add(kit.cyl("bell", 0.07, 0.1, (0, 0, -0.26), M["brass"], bell, n=16, r2=0.035))
    add(kit.sphere("bell clapper", 0.018, (0, 0, -0.33), M["brass"], bell, 8))
    add(kit.box("bell bracket", (0.12, 0.06, 0.03), (1.25, SY0 + 0.1, 2.215), M["brass"]))
    # the long mirror over the counter on the left wall
    add(wbox(kit, "mirror", (SX0 + 0.1, 3.0, 1.0), (SX0 + 0.115, 10.5, 2.55), M["mirror"]))
    for nm, lo, hi in (("mf b", (SX0 + 0.1, 2.95, 0.95), (SX0 + 0.13, 10.55, 1.0)), ("mf t", (SX0 + 0.1, 2.95, 2.55), (SX0 + 0.13, 10.55, 2.6)),
                       ("mf a", (SX0 + 0.1, 2.95, 0.95), (SX0 + 0.13, 3.0, 2.6)), ("mf z", (SX0 + 0.1, 10.5, 0.95), (SX0 + 0.13, 10.55, 2.6))):
        add(wbox(kit, nm, lo, hi, M["wood"]))
    add(wbox(kit, "counter", (SX0 + 0.1, 2.9, 0.0), (SX0 + 0.55, 10.6, 0.88), M["wood"]))
    add(wbox(kit, "counter top", (SX0 + 0.1, 2.9, 0.88), (SX0 + 0.6, 10.6, 0.93), M["counter"]))
    # counter things: combs, a spray, folded towels
    for i, y in enumerate((4.0, 4.6, 5.7, 6.3, 7.3, 8.2)):
        if i in (4, 5):   # the counter in front of the third chair stays bare
            continue
        add(kit.box(f"comb{i}", (0.18, 0.045, 0.006), (SX0 + 0.35, y, 0.936), M["black"]))
        add(kit.cyl(f"spray{i}", 0.03, 0.14, (SX0 + 0.3, y + 0.25, 1.0), M["chrome"], n=10))
        add(kit.box(f"towel{i}", (0.2, 0.28, 0.07), (SX0 + 0.42, y - 0.4, 0.97), M["towel"], bevel=0.02))
    add(kit.box("towel back", (0.2, 0.28, 0.12), (SX0 + 0.42, 9.6, 0.99), M["towel"], bevel=0.02))
    # scissors and clippers lie flat at Len's and Sid's stations only, blades closed and pointing at the mirror
    for who in ("len", "sid"):
        y = CHY[who]
        add(kit.box(f"scissors {who} a", (0.16, 0.012, 0.004), (SX0 + 0.36, y + 0.04, 0.9375), M["steel"], rot=(0, 0, 0.05)), "props")
        add(kit.box(f"scissors {who} b", (0.16, 0.012, 0.004), (SX0 + 0.36, y + 0.043, 0.9395), M["steel"], rot=(0, 0, -0.05)), "props")
        for dy in (0.03, 0.058):
            add(kit.cyl(f"scissors {who} h{dy}", 0.017, 0.006, (SX0 + 0.47, y + dy, 0.938), M["steel"], rot=(0, 0, 0), n=10), "props")
        add(kit.box(f"clippers {who}", (0.15, 0.05, 0.04), (SX0 + 0.38, y - 0.2, 0.955), M["black"], bevel=0.01), "props")
        add(kit.box(f"clippers {who} plate", (0.03, 0.04, 0.008), (SX0 + 0.29, y - 0.2, 0.94), M["steel"]), "props")
    # waiting chairs along the right wall by the door, and a coat stand
    ctx["wait"] = []
    for i, (x, y) in enumerate(WAIT):
        root, sw, parts = CR.build_chair(f"wait{i}", M, waiting=True)
        root.location = (x, y, 0)
        root.rotation_euler = (0, 0, math.radians(-90))
        for p in parts:
            add(p)
        add(root)
        add(sw)
        ctx["wait"].append(root)
    add(kit.cyl("coat pole", 0.025, 1.8, (1.6, 7.4, 0.9), M["iron"], n=8))
    add(kit.cyl("coat foot", 0.18, 0.03, (1.6, 7.4, 0.015), M["iron"], n=16))
    for k in range(4):
        a = k * math.pi / 2
        add(kit.box(f"coat hook{k}", (0.22, 0.03, 0.03), (1.6 + 0.1 * math.cos(a), 7.4 + 0.1 * math.sin(a), 1.7), M["iron"], rot=(0, 0, a)))
    # the three barber chairs (the third has the tally under its footplate)
    ctx["chairs"] = {}
    for who in ("len", "sid", "third"):
        root, sw, parts = CR.build_chair(f"chair {who}", M, tally=(who == "third"))
        root.location = (CHX, CHY[who], 0)
        root.rotation_euler = (0, 0, math.radians(-90))
        for p in parts + [root, sw]:
            add(p)
        ctx["chairs"][who] = (root, sw)
    # the folded striped cape on the third chair's arm (a separate prop in the same stripes)
    capeprop = kit.box("cape prop", (0.22, 0.56, 0.18), (-0.5, 0.0, 0.88), CR.striped(), ctx["chairs"]["third"][1], bevel=0.05)
    ctx["capeprop"] = [capeprop,
                       kit.box("cape prop2", (0.22, 0.4, 0.1), (-0.5, -0.1, 0.82), CR.striped(), ctx["chairs"]["third"][1], bevel=0.04)]
    for p in ctx["capeprop"]:
        add(p)
    # the sink at the back with its brass lamp
    sx, sy = SINK
    add(kit.box("sink pedestal", (0.3, 0.3, 0.7), (sx, sy + 0.1, 0.35), M["porcelain"], bevel=0.03))
    add(kit.box("sink basin", (0.8, 0.5, 0.16), (sx, sy, 0.84), M["porcelain"], bevel=0.05))
    add(kit.box("sink inner", (0.6, 0.34, 0.02), (sx, sy, 0.915), M["steel"]))
    add(kit.cyl("tap stem", 0.02, 0.28, (sx, sy + 0.2, 1.05), M["chrome"], n=8))
    add(kit.box("tap spout", (0.03, 0.2, 0.03), (sx, sy + 0.1, 1.18), M["chrome"]))
    add(kit.box("sink shelf", (0.8, 0.02, 0.5), (sx, SY1 - 0.1, 1.2), M["sage"]))
    mat, em = emit_mat(kit, "sink lamp shade", "#ffcf90", 3.5)
    add(kit.cyl("sink lamp arm", 0.012, 0.5, (sx, SY1 - 0.3, 2.2), M["brass"], rot=(math.pi / 2, 0, 0), n=8))
    add(kit.cyl("sink lamp shade", 0.15, 0.2, (sx, SY1 - 0.55, 2.1), mat, n=16, r2=0.06))
    ctx["sinkem"] = em
    kit.light("sinklamp", "POINT", (sx, SY1 - 0.6, 2.0), 0.0, "#ffb86a", size=0.12)
    # three rows of ceiling lamps (front, middle, back): a bar each, with their own light
    ctx["rowem"] = []
    for i, y in enumerate((3.8, 6.4, 9.0)):
        mat, em = emit_mat(kit, f"row{i} bar", "#fff0d0", 4.0)
        add(kit.box(f"row{i} bar", (1.5, 0.22, 0.05), (-0.1, y, SH - 0.03), mat, bevel=0.01))
        add(kit.box(f"row{i} hood", (1.6, 0.3, 0.03), (-0.1, y, SH - 0.005), M["chrome"]))
        ctx["rowem"].append(em)
        kit.light(f"row{i}", "AREA", (-0.1, y, SH - 0.1), 0.0, "#ffe6bd", size=1.6)
        kit.aim(kit.LIGHTS[f"row{i}"]["obj"], (-0.1, y, 0.0))
    kit.light("mirrorfill", "AREA", (0.6, 6.5, 2.7), 0.0, "#ffe2c0", size=3.0)
    kit.aim(kit.LIGHTS["mirrorfill"]["obj"], (-1.7, 6.5, 1.3))
    # daylight through the front window, and the amber glow it throws out on the evening street
    kit.light("warmkey", "AREA", (1.4, 5.6, 2.6), 0.0, "#ffc47a", size=2.5)
    kit.aim(kit.LIGHTS["warmkey"]["obj"], (-0.2, 7.8, 0.9))
    kit.light("daywin", "AREA", (-0.5, 1.6, 1.5), 0.0, "#d6e6ff", size=2.0)
    kit.aim(kit.LIGHTS["daywin"]["obj"], (-0.5, 6.0, 0.8))
    kit.light("winglow", "AREA", (-0.5, 2.2, 1.3), 0.0, "#ffb060", size=1.2)
    kit.aim(kit.LIGHTS["winglow"]["obj"], (-0.5, -3.0, 0.4))
    # the broom Len sweeps with (head only is shown), the frost on the window
    broom = kit.empty("broom", (CHX, CHY["third"], 0))
    ctx["broom"] = broom
    add(broom)
    add(kit.box("broom head", (0.42, 0.09, 0.07), (0, 0, 0.05), M["bristle"], broom, bevel=0.015))
    add(kit.box("broom block", (0.44, 0.1, 0.04), (0, 0, 0.1), M["wood"], broom))
    add(kit.cyl("broom stick", 0.015, 1.0, (0, 0, 0.62), M["wood"], broom, n=8))
    ctx["frost"] = []
    for nm, lo, hi in (("frost a", (-1.62, SY0 + 0.04, 0.58), (-1.2, SY0 + 0.045, 1.2)), ("frost b", (-1.62, SY0 + 0.04, 1.9), (-1.35, SY0 + 0.045, 2.38)),
                       ("frost c", (0.2, SY0 + 0.04, 0.58), (0.56, SY0 + 0.045, 1.0)), ("frost d", (-0.3, SY0 + 0.04, 2.1), (0.56, SY0 + 0.045, 2.38)),
                       ("frost e", (-1.62, SY0 + 0.04, 0.58), (-0.9, SY0 + 0.045, 0.78))):
        fm = kit.plastic("#dfe9ef", 0.9, "frost", 0.0)
        ob = wbox(kit, nm, lo, hi, fm)
        ctx["frost"].append(ob)
        add(ob)
    # the sink side counter for Len (a basin towel rail is enough)


# ------------------------------------------------------------------------------------------------ the far rooms
def room(kit, ctx, name, o, w, d, h, wall, floor, M, lights):
    G = ctx["groups"][name]
    ox, oy = o
    G.append(wbox(kit, f"{name} floor", (ox - w / 2, oy - d / 2, -0.05), (ox + w / 2, oy + d / 2, 0.0), floor))
    G.append(wbox(kit, f"{name} ceil", (ox - w / 2, oy - d / 2, h), (ox + w / 2, oy + d / 2, h + 0.1), M["ceil"]))
    G.append(wbox(kit, f"{name} back", (ox - w / 2, oy + d / 2 - 0.1, 0), (ox + w / 2, oy + d / 2, h), wall))
    G.append(wbox(kit, f"{name} left", (ox - w / 2, oy - d / 2, 0), (ox - w / 2 + 0.1, oy + d / 2, h), wall))
    G.append(wbox(kit, f"{name} right", (ox + w / 2 - 0.1, oy - d / 2, 0), (ox + w / 2, oy + d / 2, h), wall))
    G.append(wbox(kit, f"{name} front", (ox - w / 2, oy - d / 2, 0), (ox + w / 2, oy - d / 2 + 0.1, h), wall))
    for lname, (lx, ly, lz, watts, hexc) in lights.items():
        kit.light(lname, "AREA", (ox + lx, oy + ly, lz), 0.0, hexc, size=1.6)
        kit.aim(kit.LIGHTS[lname]["obj"], (ox + lx, oy + ly, 0.0))
        ctx["room_watts"][lname] = watts


def build_rooms(kit, ctx, M):
    ctx["room_watts"] = {}
    # the cafe: warm, five round tables
    ox, oy = CAFE
    room(kit, ctx, "cafe", CAFE, 9.0, 8.0, 3.0, M["cafewall"], M["floorwood"], M,
         {"cafe_l1": (-1.5, 0, 2.8, 220, "#ffd9a0"), "cafe_l2": (2.0, -0.5, 2.8, 200, "#ffd9a0")})
    G = ctx["groups"]["cafe"]
    ctx["cafe_tables"] = [(-2.6, 1.6), (0.0, 1.8), (2.7, 1.5), (-1.4, -0.8), (1.4, -1.0)]
    for i, (tx, ty) in enumerate(ctx["cafe_tables"]):
        G.append(kit.cyl(f"cafe table{i}", 0.5, 0.04, (ox + tx, oy + ty, 0.74), M["counter"], n=24))
        G.append(kit.cyl(f"cafe stem{i}", 0.05, 0.72, (ox + tx, oy + ty, 0.37), M["iron"], n=10))
        G.append(kit.cyl(f"cafe cup{i}", 0.04, 0.07, (ox + tx + 0.12, oy + ty - 0.1, 0.795), M["porcelain"], n=12))
        for sx, sy in ((-0.62, 0), (0.62, 0), (0, -0.62), (0, 0.62)):
            G.append(kit.box(f"cafe chair{i}.{sx}{sy}", (0.42, 0.42, 0.05), (ox + tx + sx, oy + ty + sy, 0.46), M["wood"], bevel=0.01))
            G.append(kit.box(f"cafe chair legs{i}.{sx}{sy}", (0.34, 0.34, 0.44), (ox + tx + sx, oy + ty + sy, 0.22), M["iron"]))
    G.append(wbox(kit, "cafe window", (ox - 3.0, oy + 3.88, 0.9), (ox + 3.0, oy + 3.9, 2.4), M["pane"]))
    wm, wem = emit_mat(kit, "cafe daylight", "#cfe4f5", 2.0)
    G.append(wbox(kit, "cafe sky", (ox - 3.0, oy + 3.95, 0.9), (ox + 3.0, oy + 3.97, 2.4), wm))
    G.append(wbox(kit, "cafe counter", (ox - 4.4, oy - 3.5, 0), (ox - 3.6, oy + 2.5, 1.0), M["counter"]))
    # the bus: a long cabin along x
    ox, oy = BUS
    room(kit, ctx, "bus", BUS, 9.0, 4.0, 2.2, M["cream"], M["busfloor"], M,
         {"bus_l1": (-2.5, 0, 2.1, 120, "#ffe3b0"), "bus_l2": (2.5, 0, 2.1, 120, "#ffe3b0")})
    G = ctx["groups"]["bus"]
    wm2, _ = emit_mat(kit, "bus dusk", "#9db4d8", 1.4)
    for sy in (-1, 1):
        G.append(wbox(kit, f"bus window{sy}", (ox - 4.2, oy + sy * 1.93, 1.0), (ox + 4.2, oy + sy * 1.95, 1.9), wm2))
        for k in range(9):
            G.append(wbox(kit, f"bus pillar{sy}{k}", (ox - 4.3 + k * 1.0, oy + sy * 1.92, 1.0), (ox - 4.25 + k * 1.0, oy + sy * 1.95, 1.9), M["cream"]))
    for r in range(6):
        for sy in (-1, 1):
            x, y = ox - 3.2 + r * 1.3, oy + sy * 1.25
            G.append(kit.box(f"bus seat{r}.{sy}", (0.5, 1.4, 0.12), (x, y, 0.42), M["seatmaroon"], bevel=0.03))
            G.append(kit.box(f"bus back{r}.{sy}", (0.1, 1.4, 0.7), (x - 0.3, y, 0.8), M["seatmaroon"], bevel=0.03))
            G.append(kit.box(f"bus base{r}.{sy}", (0.4, 1.2, 0.36), (x, y, 0.18), M["iron"]))
    G.append(wbox(kit, "bus pole", (ox - 3.0, oy - 0.02, 0), (ox - 2.96, oy + 0.02, 2.2), M["chrome"]))
    # Pat's flat: a sofa, a bare bookshelf, one plain box
    ox, oy = FLAT
    room(kit, ctx, "flat", FLAT, 5.0, 4.5, 2.6, M["plaster"], M["floorwood"], M, {"flat_l": (0.3, -0.3, 2.5, 180, "#ffe0b8")})
    G = ctx["groups"]["flat"]
    G.append(kit.box("sofa seat", (1.8, 0.8, 0.28), (ox - 0.4, oy + 1.4, 0.3), M["sofa"], bevel=0.05))
    G.append(kit.box("sofa back", (1.8, 0.2, 0.55), (ox - 0.4, oy + 1.8, 0.7), M["sofa"], bevel=0.05))
    for sx in (-1, 1):
        G.append(kit.box(f"sofa arm{sx}", (0.2, 0.8, 0.5), (ox - 0.4 + sx * 0.95, oy + 1.4, 0.4), M["sofa"], bevel=0.05))
    G.append(wbox(kit, "shelf l", (ox + 1.6, oy + 1.95, 0), (ox + 1.66, oy + 2.15, 2.0), M["bookshelf"]))
    G.append(wbox(kit, "shelf r", (ox + 2.3, oy + 1.95, 0), (ox + 2.36, oy + 2.15, 2.0), M["bookshelf"]))
    for z in (0.0, 0.5, 1.0, 1.5, 1.97):
        G.append(wbox(kit, f"shelf board{z}", (ox + 1.6, oy + 1.95, z), (ox + 2.36, oy + 2.15, z + 0.04), M["bookshelf"]))
    G.append(kit.box("plain box", (0.5, 0.4, 0.35), (ox + 1.0, oy + 0.4, 0.18), M["cardboard"], bevel=0.01))
    G.append(wbox(kit, "flat window", (ox - 2.45, oy - 1.0, 0.9), (ox - 2.4, oy + 1.0, 2.1), M["pane"]))
    # our kitchen: a table with the keys on it
    ox, oy = KIT
    room(kit, ctx, "kitchen", KIT, 4.6, 4.0, 2.6, M["kitwall"], M["checker"], M, {"kit_l": (0.0, 0.0, 2.5, 160, "#ffe6bd")})
    G = ctx["groups"]["kitchen"]
    G.append(kit.box("kitchen table", (1.3, 0.8, 0.04), (ox, oy + 0.3, 0.74), M["counter"], bevel=0.01))
    for dx in (-0.55, 0.55):
        for dy in (-0.3, 0.3):
            G.append(kit.box(f"ktleg{dx}{dy}", (0.05, 0.05, 0.72), (ox + dx, oy + 0.3 + dy, 0.36), M["wood"]))
    G.append(kit.box("keys", (0.1, 0.05, 0.015), (ox - 0.25, oy + 0.3, 0.77), M["brass"], rot=(0, 0, 0.3)))
    G.append(kit.cyl("keyring", 0.03, 0.004, (ox - 0.31, oy + 0.3, 0.77), M["steel"], n=14))
    for dx in (-0.85, 0.85):
        G.append(kit.box(f"kchair{dx}", (0.42, 0.42, 0.05), (ox + dx, oy + 0.3, 0.46), M["wood"], bevel=0.01))
        G.append(kit.box(f"kchair legs{dx}", (0.34, 0.34, 0.44), (ox + dx, oy + 0.3, 0.22), M["iron"]))
    G.append(kit.box("fridge", (0.7, 0.7, 1.7), (ox + 1.7, oy + 1.5, 0.85), M["porcelain"], bevel=0.04))
    G.append(wbox(kit, "kitchen window", (ox - 1.0, oy + 1.9, 1.1), (ox + 1.0, oy + 1.92, 2.0), M["pane"]))
    km, _ = emit_mat(kit, "kitchen dusk", "#35486a", 1.4)
    G.append(wbox(kit, "kitchen sky", (ox - 1.0, oy + 1.95, 1.1), (ox + 1.0, oy + 1.97, 2.0), km))


# ------------------------------------------------------------------------------------------------ rings
class Ring:
    """A torus rebuilt every frame: positions in world space, so no object transform. m lobes travel round it."""

    NM, NT = 40, 6

    def __init__(self, kit, name, hexc, clear=False, lobes=3, speed=0.8, phase=0.0, amp=0.011, strength=6.0):
        self.name, self.hex, self.clear = name, hexc, clear
        self.lobes, self.speed, self.phase, self.amp = lobes, speed, phase, amp
        if clear:
            m = kit._new(f"ring {name}")
            nt = m.node_tree
            b = nt.nodes["Principled BSDF"]
            b.inputs["Base Color"].default_value = (0.95, 0.97, 1.0, 1)
            b.inputs["Roughness"].default_value = 0.04
            b.inputs["Transmission Weight" if "Transmission Weight" in b.inputs else "Transmission"].default_value = 0.9
            b.inputs["Emission Color"].default_value = (0.9, 0.95, 1.0, 1)
            b.inputs["Emission Strength"].default_value = 0.9
            kit._fogged(m, b.outputs[0])
            self.em = b.inputs["Emission Strength"]
            self.mat, self.base_em = m, 0.9
        else:
            self.mat, em = emit_mat(kit, f"ring {name}", hexc, strength)
            self.em, self.base_em = em.inputs["Strength"], strength
        n = self.NM * self.NT
        faces = []
        for i in range(self.NM):
            for j in range(self.NT):
                a, b = i * self.NT + j, i * self.NT + (j + 1) % self.NT
                c, d = ((i + 1) % self.NM) * self.NT + j, ((i + 1) % self.NM) * self.NT + (j + 1) % self.NT
                faces.append((a, b, d, c))
        self.ob = kit.mesh_obj(f"ring {name}", [(0, 0, 0)] * n, faces, self.mat, None, smooth=True)
        th = np.arange(self.NM) / self.NM * 2 * math.pi
        ph = np.arange(self.NT) / self.NT * 2 * math.pi
        self.th = np.repeat(th, self.NT)
        self.ph = np.tile(ph, self.NM)

    def place(self, centre, normal, t, thick=1.0, bright=1.0, amp_k=1.0, hidden=False):
        self.ob.hide_render = hidden or bright <= 0.001
        if self.ob.hide_render:
            return
        n = V(normal).normalized()
        u = n.cross(V((0, 0, 1)) if abs(n.z) < 0.95 else V((1, 0, 0))).normalized()
        w = n.cross(u)
        r = RING_TUBE * max(0.25, thick)
        wave = self.amp * amp_k * np.sin(self.lobes * self.th - 2 * math.pi * self.speed * t + self.phase)
        rad = RING_R + 0.004 * amp_k * np.sin(self.lobes * self.th - 2 * math.pi * self.speed * t + self.phase + 1.2)
        cx = (rad + r * np.cos(self.ph)) * np.cos(self.th)
        cy = (rad + r * np.cos(self.ph)) * np.sin(self.th)
        cz = r * np.sin(self.ph) + wave
        P = np.outer(cx, [u.x, u.y, u.z]) + np.outer(cy, [w.x, w.y, w.z]) + np.outer(cz, [n.x, n.y, n.z]) + np.array(centre)
        self.ob.data.vertices.foreach_set("co", P.astype(np.float32).ravel())
        self.ob.data.update()
        self.em.default_value = self.base_em * bright


# ------------------------------------------------------------------------------------------------ the crowd extras
def build_extras(kit, ctx, M):
    rng = np.random.default_rng(42)
    pts = []
    tries = 0
    while len(pts) < 64 and tries < 5000:
        tries += 1
        x, y = rng.uniform(-9.5, 9.5), rng.uniform(-3.4, 1.7)
        if abs(x - 1.5) < 1.2 and y > 0.2:
            continue                     # the shop's doorway
        if all((x - a) ** 2 + (y - b) ** 2 > 0.85 ** 2 for a, b, _ in pts):
            pts.append((x, y, 0))
    cols = []
    for i, (x, y, _) in enumerate(pts):
        near = {cols[j] for j in range(i) if (x - pts[j][0]) ** 2 + (y - pts[j][1]) ** 2 < 2.2 ** 2}
        choices = [c for c in range(len(EXTRA_COLORS)) if c not in near]
        cols.append(int(choices[int(rng.integers(len(choices)))]))
    coats = ["#3b4a63", "#6b2f33", "#2f4a3a", "#5a5448", "#44384f", "#7a5a3a", "#2c2f38", "#8a7a66", "#4a5a6a"]
    skins = ["#f1c9a0", "#e0b088", "#c98e66", "#8f5d3e", "#f4d6b8", "#a87050"]
    hairs = ["#2a1d15", "#4a3020", "#1a1a1a", "#8a6a3a", "#b8b0a6", "#6a3a22"]
    ctx["extras"] = []
    for i, (x, y, _) in enumerate(pts):
        root = kit.empty(f"extra{i}", (x, y, 0))
        root.rotation_euler = (0, 0, float(rng.uniform(-math.pi, math.pi)))
        coat = kit.plastic(coats[int(rng.integers(len(coats)))], 0.8, f"coat{i % 9}.{int(rng.integers(0, 3))}", 0.1)
        h = float(rng.uniform(0.94, 1.06))
        parts = [kit.box(f"extra{i}.legs", (0.34, 0.22, 0.8 * h), (0, 0, 0.4 * h), M["fur"], root, bevel=0.03),
                 kit.box(f"extra{i}.torso", (0.5, 0.3, 0.7 * h), (0, 0, 1.15 * h), coat, root, bevel=0.05),
                 kit.cyl(f"extra{i}.head", 0.145, 0.27, (0, 0, 1.64 * h), kit.plastic(skins[int(rng.integers(len(skins)))], 0.5), root, n=14),
                 kit.box(f"extra{i}.hair", (0.31, 0.31, 0.1), (0, 0.01, 1.8 * h), kit.plastic(hairs[int(rng.integers(len(hairs)))], 0.7), root, bevel=0.03)]
        ring = Ring(kit, f"x{i}", EXTRA_COLORS[cols[i]], lobes=int(rng.integers(2, 5)), speed=float(rng.uniform(0.6, 1.0)),
                    phase=float(rng.uniform(0, 6.28)))
        ctx["extras"].append({"root": root, "parts": parts, "ring": ring, "pos": (x, y), "h": 1.95 * h})
    ctx["groups"]["extras"] = []


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    ctx = {"groups": {k: [] for k in ("street", "shop", "cafe", "bus", "flat", "kitchen")}, "cr": None}
    M = materials(kit)
    M["ceil"] = M["ceil"]
    ctx["M"] = M
    build_street(kit, ctx, M)
    build_shop(kit, ctx, M)
    build_rooms(kit, ctx, M)
    build_extras(kit, ctx, M)
    # sun and sky for the day street
    kit.light("sun", "SUN", (0, 0, 10), 0.0, "#fff1d0")
    ctx["sun"] = kit.LIGHTS["sun"]["obj"]
    ctx["sun"].rotation_euler = (math.radians(52), 0, math.radians(-32))
    kit.light("skyfill", "AREA", (0, -4, 12), 0.0, "#a8c8ee", size=30.0)
    kit.aim(kit.LIGHTS["skyfill"]["obj"], (0, 0, 0))
    kit.light("dusk", "AREA", (0, -8, 12), 0.0, "#6f86bb", size=30.0)
    kit.aim(kit.LIGHTS["dusk"]["obj"], (0, 0, 0))
    # the creature and its lights for the dark shots (a cool key from the side, a warm rim from the sink lamp)
    cr = CR.build_creature(M)
    ctx["cr"] = cr
    for nm, hexc in (("ckey", "#9db8ff"), ("crim", "#ffb070"), ("cfill", "#b0c4ff")):
        kit.light(nm, "SPOT", (0, 0, 2), 0.0, hexc, size=0.1, spot=45, blend=0.7)
    # the plain oxblood cape for my trim (a smaller cape of the same cut, no stripes)
    mc = kit.empty("me cape", (CHX, CHY["third"], 0))
    CR._loft("me cape body", [(1.34, 0.21, 0.21, 0.21, 2.0), (1.28, 0.46, 0.30, 0.22, 3.0), (1.2, 0.60, 0.40, 0.26, 5.0), (1.0, 0.63, 0.43, 0.27, 6.0),
                              (0.78, 0.65, 0.44, 0.27, 6.0), (0.56, 0.67, 0.46, 0.27, 5.0), (0.46, 0.69, 0.66, 0.27, 4.0), (0.4, 0.69, 0.74, 0.27, 3.5)],
             M["cape_oxblood"], mc)
    ctx["mecape"] = [mc] + list(mc.children_recursive)
    # my rings (clear, then violet) and everyone else's
    ctx["rings"] = {}
    for who, hexc in RINGS.items():
        if who in story.get("cast", {}):
            pair = who in ("c8", "c9")      # the two who find each other by ear ripple in step
            ctx["rings"][who] = Ring(kit, who, hexc or "#ffffff", clear=hexc is None, lobes=3,
                                     speed=0.8 if pair else 0.6 + 0.07 * (sum(map(ord, who)) % 6),
                                     phase=0.0 if pair else (sum(map(ord, who)) % 7))
    ctx["violet"] = Ring(kit, "violet", "#b07cff", lobes=3, speed=0.8, phase=0.7, strength=0.7)
    return ctx


# ------------------------------------------------------------------------------------------------ the pieces that move
SCENES = {
    # scene: (world colour, world strength, {light: watts}); the shop's rows come from ROWF and the shot's `rows`
    "day": ("#9cc3e0", 1.5, {"sun": 6.5, "skyfill": 1500, "mirrorfill": 120, "sinklamp": 80}),
    "dusk": ("#2b3a55", 0.8, {"dusk": 1100, "winglow": 90, "mirrorfill": 200, "sinklamp": 120}),
    "shop": ("#10141c", 0.2, {"mirrorfill": 300, "sinklamp": 160}),
    "shopday": ("#9cc3e0", 0.7, {"daywin": 450, "mirrorfill": 300, "sinklamp": 160}),
    "flash": ("#d8b890", 1.2, {"daywin": 800, "mirrorfill": 440, "sinklamp": 240, "warmkey": 600}),
    "cafe": ("#10141c", 0.3, {"cafe_l1": 520, "cafe_l2": 460}),
    "bus": ("#10141c", 0.3, {"bus_l1": 420, "bus_l2": 420}),
    "flat": ("#10141c", 0.3, {"flat_l": 420}),
    "kitchen": ("#10141c", 0.3, {"kit_l": 420}),
}
ROWF = {"day": 0.45, "dusk": 1.0, "shop": 1.0, "shopday": 1.0, "flash": 1.0}
SHOW = {"day": ["street", "shop"], "dusk": ["street", "shop"], "shop": ["shop", "street"], "shopday": ["shop", "street"],
        "flash": ["shop", "street"], "cafe": ["cafe"], "bus": ["bus"], "flat": ["flat"], "kitchen": ["kitchen"]}
ROW_W = (220.0, 220.0, 220.0)


def _world(kit, hexc, strength):
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = kit.col(hexc)
    bg.inputs["Strength"].default_value = strength


def _seat(who, tl, t):
    return _switch(tl["acting"].get(who, []), "sit", t, False)


def animate(kit, story, tl, t, ctx):
    from blocky import bl_story as BL
    from blocky import kit as K

    over = {}
    shot = _shot(tl, t)
    sid = shot["id"]
    _cam = BL.cam_at({s_["id"]: s_ for s_ in story["shots"]}[sid], shot, t, {}, tl)[0]
    ctx["camxy"] = (_cam[0], _cam[1])
    scene = story.get("scenes", {}).get(sid, "dusk")
    look = story.get("shotlook", {}).get(sid, {})
    wc, ws, lights = SCENES[scene]
    _world(K, look.get("world", wc), look.get("world_k", 1.0) * ws)
    if not ctx.get("lights_hidden"):
        ctx["lights_hidden"] = True
        for ob in bpy.data.objects:
            if ob.type == "LIGHT":
                ob.visible_camera = False      # the lamps light the set but are never seen as white panels
    # ---- what exists in this shot
    show = set(SHOW[scene]) | set(look.get("show", []))
    for g, obs in ctx["groups"].items():
        for ob in obs:
            ob.hide_render = g not in show
    for ob in ctx["groups"].get("props", []):
        ob.hide_render = ("shop" not in show) or bool(look.get("no_props"))
    # ---- lights: every light off unless this scene (or the shot) lights it
    for nm in list(K.LIGHTS):
        over[nm] = 0.0
    for nm, w in lights.items():
        if nm in K.LIGHTS:
            K.LIGHTS[nm]["base"] = w
            over[nm] = 1.0
    for nm, w in look.get("lights", {}).items():
        if nm in K.LIGHTS:
            K.LIGHTS[nm]["base"] = w
            over[nm] = 1.0
    if look.get("sun"):
        ctx["sun"].rotation_euler = (math.radians(look["sun"][0]), 0, math.radians(look["sun"][1]))
    # lamp posts at dusk
    lamps_on = scene == "dusk"
    for i in range(5):
        K.LIGHTS[f"lamp{i}"]["base"] = 220.0
        over[f"lamp{i}"] = 1.0 if lamps_on else 0.0
        ctx["lampem"][i].inputs["Strength"].default_value = 4.0 if lamps_on else 0.4
    # ---- the shop's three light rows (separate slow fades), the sink lamp
    shop_on = scene in ROWF
    rows = look.get("rows", [1.0, 1.0, 1.0])
    for i in range(3):
        g = _level(tl, f"row{i}", t, 1.0) * rows[i] * ROWF.get(scene, 0.0)
        K.LIGHTS[f"row{i}"]["base"] = ROW_W[i]
        over[f"row{i}"] = g
        ctx["rowem"][i].inputs["Strength"].default_value = 4.0 * g
    over["mirrorfill"] = over.get("mirrorfill", 0.0) * look.get("mf", 1.0)
    sg = look.get("sink", 1.0) if shop_on else 0.0
    over["sinklamp"] = over.get("sinklamp", 0.0) * sg
    ctx["sinkem"].inputs["Strength"].default_value = 3.5 * (1.0 if shop_on else 0.0) * look.get("sink", 1.0)
    # ---- people: sitting, standing
    for who, keys in tl["acting"].items():
        for sx in (-1, 1):
            leg = bpy.data.objects.get(f"{who}.leg{sx}")
            if leg is not None and _switch(keys, "sit", t, False):
                leg.rotation_euler = (-math.pi / 2, 0, 0)
        tor = bpy.data.objects.get(f"{who}.torso")
        if tor is not None:
            tor.rotation_euler = (math.radians(ac._held(keys, "bend", t, 0.0)), 0, 0)
    _extras_people(ctx, story, tl, t, ctx.get("camxy"))
    # ---- the door, the bell, the broom, the frost, the cape prop
    ctx["door"].rotation_euler = (0, 0, math.radians(_level(tl, "door", t, 0.0)))
    bc = [c for c in _cues(tl, "bell") if c["t"] <= t + 1e-9]
    ang = 0.0
    if bc:
        x = t - bc[-1]["t"]
        ang = 0.22 * math.exp(-x * 1.6) * math.sin(2 * math.pi * 1.2 * x) if x < 3.0 else 0.0
    ctx["bell"].rotation_euler = (ang, 0, 0.0)
    bs = _switch(_cues(tl, "broom"), "on", t, False)
    ctx["broom"].hide_render = not (bs and "shop" in show)
    for ch in ctx["broom"].children:
        ch.hide_render = ctx["broom"].hide_render
    if bs:
        w = _switch(_cues(tl, "broom"), "at_x", t, CHX)
        sw_ = math.sin(t * 5.2)
        ctx["broom"].location = (CHX - 0.12 + 0.18 * sw_, CHY["third"] - 0.05 + look.get("broom_y", 0.0), 0.0)
        ctx["broom"].rotation_euler = (0, -0.28, 0)
    for nm in ("window pane", "door pane"):
        ob = bpy.data.objects.get(nm)
        if ob is not None and look.get("nopane"):
            ob.hide_render = True
    for ob in ctx["frost"]:
        ob.hide_render = not look.get("frost", False)
    on_cape = _switch(_cues(tl, "cape"), "on", t, False)
    for ob in ctx["capeprop"]:
        ob.hide_render = not (on_cape and "shop" in show)
    # ---- the chairs, the third swivelling
    sw_deg = _level(tl, "swivel", t, 0.0)
    for who in ("len", "sid", "third"):
        sw = ctx["chairs"][who][1]
        sw.rotation_euler = (0, 0, math.radians(sw_deg if who == "third" else 0.0))
    # ---- the creature
    cr = ctx["cr"]
    st = {"on": False, "where": "third", "mouth": False}
    for c in _cues(tl, "creature"):
        if c["t"] <= t + 1e-9:
            for k in st:
                if k in c:
                    st[k] = c[k]
    on = st["on"] and ("shop" in show)
    for ob in cr["parts"]:
        ob.hide_render = not on
    if on:
        where = st["where"]
        if where == "wait":
            x, y = WAIT[0]
            cr["root"].location = (x, y, 0.0)
            cr["root"].rotation_euler = (0, 0, math.radians(-90))
        else:
            wh = "sid" if where == "sid" else "third"
            cr["root"].location = (CHX, CHY[wh], 0.0)
            cr["root"].rotation_euler = (0, 0, math.radians(-90 + (sw_deg if wh == "third" else 0.0)))
        CR.set_mouth(cr, st["mouth"])
    for nm in ("ckey", "crim", "cfill"):
        spec = look.get(nm)
        if spec:
            pos, aim, watts = spec[:3]
            if len(spec) > 3 and spec[3]:
                K.LIGHTS[nm]["light"].spot_size = math.radians(spec[3])
            ob = K.LIGHTS[nm]["obj"]
            ob.location = pos
            ob.rotation_euler = (V(aim) - V(pos)).to_track_quat("-Z", "Y").to_euler()
            K.LIGHTS[nm]["base"] = watts
            over[nm] = 1.0
    # my plain oxblood cape (L61 on), Mr Ostrowski's shivering panes, the combs and the cape on Len's arm
    mo = bool(look.get("oxblood")) and "shop" in show
    for ob in ctx["mecape"]:
        ob.hide_render = not mo
    if mo:
        ctx["mecape"][0].location = (CHX, CHY["third"], 0)
        ctx["mecape"][0].rotation_euler = (0, 0, math.radians(-90))
    if "ostro_pane" in ctx:
        pane, home = ctx["ostro_pane"]
        k = look.get("buzz", 0.0)
        pane.location = (home.x + 0.004 * k * math.sin(t * 61.0), home.y, home.z + 0.003 * k * math.sin(t * 47.0))
        over["ostro_l"] = 0.0
        if "ostro" in look.get("show", []):
            K.LIGHTS["ostro_l"]["base"] = 260.0
            over["ostro_l"] = 1.0
    for nm, flag in (("sid.comb", "sidcomb"), ("len.comb", "lencomb"), ("len.armcape", "armcape")):
        ob = bpy.data.objects.get(nm)
        if ob is not None:
            gone = ac.state(tl, nm.split(".")[0], t)["hidden"]
            ob.hide_render = gone or not look.get(flag, False)
    # props (scissors, clippers) stay out of every shot the creature is in
    if on:
        for ob in ctx["groups"].get("props", []):
            ob.hide_render = True
    # ---- the hair: shaggy, then neat after the trim
    _dress(ctx)
    short = _switch(_cues(tl, "hair"), "short", t, False)
    me_gone = ac.state(tl, "me", t)["hidden"] if "me" in tl["acting"] else True
    me_parts = [bpy.data.objects.get(f"me.{n}") for n in ("hcap", "hback", "hside-1", "hside1", "fringe", "fringe2", "shag1", "shag2")]
    for ob in me_parts:
        if ob is not None:
            ob.hide_render = ob.hide_render or short
    for ob in [bpy.data.objects.get(n) for n in ("me.short_cap", "me.short_fr", "me.short_s1", "me.short_s2")]:
        if ob is not None:
            ob.hide_render = (not short) or me_gone
    # ---- the rings
    place_rings(K, BL, story, tl, t, ctx, shot, sid)
    kk = look.get("k", 1.0)
    if kk != 1.0:
        for nm in list(over):
            over[nm] = over[nm] * kk
    return over


def _dress(ctx):
    """What the rig doesn't make: Len's grey beard, Sid's moustache and bow tie, my shaggy locks and my neat new hair."""
    if ctx.get("dressed"):
        return
    ctx["dressed"] = True
    from blocky import kit

    R, H = faces.HEAD_R, faces.HEAD_H
    top = H / 2
    hg = lambda n: bpy.data.objects.get(f"{n}.headg")
    g = hg("len")
    if g is not None:
        grey = kit.plastic("#9a9a9c", 0.85, "grey beard")
        kit.box("len.beard", (2 * R * 0.92, 0.42, 0.30), (0, -R + 0.16, -0.47), grey, g, bevel=0.1)
        for sx in (-1, 1):
            kit.box(f"len.burn{sx}", (0.14, 0.5, 0.34), (sx * (R - 0.04), -0.1, -0.22), grey, g, bevel=0.05)
    g = hg("sid")
    if g is not None:
        wh = kit.plastic("#f2f2ee", 0.85, "white moustache")
        kit.box("sid.mous", (0.66, 0.14, 0.10), (0, -R - 0.01, -0.13), wh, g, bevel=0.04)
    tor = bpy.data.objects.get("sid.torso")
    if tor is not None:
        bow = kit.plastic("#7a2a3a", 0.6, "bow tie")
        for sx in (-1, 1):
            kit.box(f"sid.bow{sx}", (0.34, 0.1, 0.26), (sx * 0.24, -0.53, 1.88), bow, tor, bevel=0.03)
        kit.box("sid.knot", (0.14, 0.12, 0.16), (0, -0.54, 1.88), bow, tor, bevel=0.03)
    for who, nm in (("sid", "comb"), ("len", "comb")):
        arm = bpy.data.objects.get(f"{who}.arm1")
        if arm is not None:
            kit.box(f"{who}.comb", (0.1, 0.9, 0.06), (0, -0.3, -1.95), kit.plastic("#101012", 0.4, "comb"), arm)
    arm = bpy.data.objects.get("len.arm-1")
    if arm is not None:
        kit.box("len.armcape", (1.3, 1.8, 0.4), (0, -0.7, -1.2), bpy.data.materials.get("oxblood cape") or kit.plastic("#5b1620", 0.55, "oxblood cape", 0.2),
                arm, bevel=0.1)
    g = hg("me")
    if g is not None:
        hair = kit.plastic("#2a1b12", 0.7, "me hair")
        neat = kit.plastic("#3a2618", 0.65, "me neat hair")
        for k, sx in enumerate((-1, 1)):
            kit.box(f"me.shag{k + 1}", (0.3, 0.75, 0.8), (sx * (R + 0.02), 0.05, top - 0.6), hair, g, bevel=0.1)
        kit.box("me.short_cap", (2 * R + 0.05, 2 * R + 0.05, 0.2), (0, 0.02, top - 0.08), neat, g, bevel=0.1)
        kit.box("me.short_fr", (2 * R * 0.9, 0.22, 0.14), (0, -R + 0.1, top - 0.17), neat, g, bevel=0.06)
        for k, sx in enumerate((-1, 1)):
            kit.box(f"me.short_s{k + 1}", (0.12, 0.7, 0.34), (sx * (R - 0.01), 0.15, top - 0.26), neat, g, bevel=0.05)


def _extras_people(ctx, story, tl, t, camxy=None):
    """The street's background crowd: every one visible in a shot whose look asks for them (`crowd`: how many)."""
    sid = _shot(tl, t)["id"]
    look = story.get("shotlook", {}).get(sid, {})
    n = int(look.get("crowd", 0))
    box = look.get("crowd_box")
    for i, e in enumerate(ctx["extras"]):
        x, y = e["pos"]
        vis = i < n and (box is None or (box[0] <= x <= box[1] and box[2] <= y <= box[3]))
        if vis and camxy is not None and (x - camxy[0]) ** 2 + (y - camxy[1]) ** 2 < 1.6 ** 2:
            vis = False
        for ob in [e["root"]] + e["parts"]:
            ob.hide_render = not vis
        e["vis"] = vis


def place_rings(K, BL, story, tl, t, ctx, shot, sid):
    shots = {s["id"]: s for s in story["shots"]}
    loc, tgt, lens, roll = BL.cam_at(shots[sid], shot, t, {}, tl)
    cam = V(loc)

    def normal_for(c):
        d = cam - V(c)
        d.z = 0
        d = d.normalized() if d.length > 1e-4 else V((0, -1, 0))
        n = V((0, 0, 1)) * 0.6 + d * 0.8
        return n

    show_extras = False
    th_len = _level(tl, "len_th", t, 1.0)
    em_len = _level(tl, "len_em", t, 1.0)
    violet = _level(tl, "violet", t, 0.0)
    wob = _level(tl, "wobble", t, 0.0)
    for who, ring in ctx["rings"].items():
        s = ac.state(tl, who, t)
        hidden = s["hidden"]
        hs = story["cast"][who].get("height", 1.0)
        c = (s["x"], s["y"], s["z"] + 1.93 * hs)
        n = normal_for(c)
        thick, bright, amp = 1.0, 1.0, 1.0
        if who == "len":
            thick, bright = 0.33 + 0.67 * th_len, em_len
        rl = story.get("shotlook", {}).get(sid, {}).get("ringlook", {}).get(who)
        if rl:
            thick, bright = rl
        if who == "me":
            amp = 0.0                                  # the glass ring is perfectly still
            thick, bright = 1.0 - 0.6 * violet, 1.0 - 0.9 * violet   # the glass sinks inside the violet tube, no white patches
        if who == "sid":
            amp = 1.0 + 1.8 * wob
        ring.place(c, n, t, thick, bright, amp, hidden)
        if who == "me":
            vr = ctx["violet"]
            vr.place(c, n, t, 1.0, violet, 1.0, hidden or violet <= 0.001)
    for e in ctx["extras"]:
        vis = e.get("vis", False)
        c = (e["pos"][0], e["pos"][1], e["h"])
        e["ring"].place(c, normal_for(c), t, 1.0, 1.0, 1.0, not vis)
