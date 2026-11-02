"""ep22 "The little man in the model village moves one window a day": the world.

Places (metres, z up, -y toward the path and the camera, +y up the hill): layout.py. The model village is six
terraces going up a slope (rows 0..5), each with a street along its front and houses behind it. Six houses are
hollow with a lit tiny room behind a glazed window (bakery, blue door, chapel, next door, my cottage, tea shop).
The Resident is a cast member 4.5 cm tall (rig scale 0.0257), posed per shot from the acting keys. The full-size
town stands behind the camera and across the water; the real tea shop and my cottage room are built far off to
the sides (x = -40 and x = +40) and reached by a cut.

Light is grey daylight that never flickers: the only changes are slow ramps (cue "cloud", "sky").
"""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector as V

HERE = Path(__file__).resolve().parent
_sp = importlib.util.spec_from_file_location("ep22_layout", HERE / "layout.py")
LAY = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(LAY)

PASTEL = ["#a9bfd0", "#e6dcc0", "#dcaeb0", "#bccaa9", "#c4bbd0", "#e3cfa7", "#b5ccc7", "#cfc7b8"]
ROOFS = ["#4b5057", "#5a4d45", "#3e444c", "#6a5f58", "#555a60"]
DOORS = ["#6d7d8e", "#8a6a55", "#7c8a6c", "#9a7f8a", "#5f6670"]
SKINS = ["#d8b08c", "#c99c78", "#e2bd9a", "#b98a68"]
TOPS = ["#8f9aa5", "#a8947c", "#7d8f7a", "#9a8190", "#b3a58f", "#6f7f93"]


# ---------------------------------------------------------------------------------------------- cue helpers
def _cues(tl, name):
    return sorted([c for c in tl["cues"] if c["name"] == name], key=lambda c: c["t"])


def _last(cs, t):
    out = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            out = c
    return out


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def val(tl, name, key, t, default):
    """A cue number that ramps: each cue with `key` eases from the one before over its `dur` (at least 0 = a cut)."""
    cs = [c for c in _cues(tl, name) if key in c]
    v = default
    for c in cs:
        if t >= c["t"]:
            u = _ss((t - c["t"]) / c["dur"]) if c.get("dur") else 1.0
            v = v + (c[key] - v) * u if c.get("dur") else c[key]
            if u < 1.0:
                return v
        else:
            break
    return v


def flag(tl, name, t, default=False):
    c = _last(_cues(tl, name), t)
    return default if c is None else bool(c.get("on", default))


# ---------------------------------------------------------------------------------------------- materials
def glass_pane(kit, name="pane"):
    """A pane that is mostly not there: a faint Fresnel reflection of the grey sky over the view through it."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.04
    gl.inputs["Color"].default_value = (0.9, 0.95, 1.0, 1)
    fr = nt.nodes.new("ShaderNodeFresnel")
    fr.inputs["IOR"].default_value = 1.9
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(fr.outputs[0], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    kit._fogged(m, mx.outputs[0])
    return m


def stone_mat(kit):
    """One seamless worn grey stone: soft large mottling, a polished sheen, no joins, no pattern."""
    name = "old stone"
    if name in kit.MATS:
        return kit.MATS[name]
    m, N, L, b = kit._mat(name)
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 2.2
    nz.inputs["Detail"].default_value = 6.0
    nz.inputs["Roughness"].default_value = 0.6
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = kit.col("#8e9195")
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = kit.col("#c2c3c1")
    L.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    L.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.22
    nz2 = N.new("ShaderNodeTexNoise")
    nz2.inputs["Scale"].default_value = 60.0
    nz2.inputs["Detail"].default_value = 2.0
    L.new(tc.outputs["Object"], nz2.inputs["Vector"])
    kit._bump(N, L, b, nz2.outputs["Fac"], 0.04, 0.01)
    kit._fogged(m, b.outputs[0])
    return m


def sea_mat(kit):
    name = "slate sea"
    if name in kit.MATS:
        return kit.MATS[name]
    m, N, L, b = kit._mat(name)
    b.inputs["Base Color"].default_value = kit.col("#2c3640")
    b.inputs["Roughness"].default_value = 0.08
    tc = N.new("ShaderNodeTexCoord")
    wv = N.new("ShaderNodeTexNoise")
    wv.inputs["Scale"].default_value = 0.35
    wv.inputs["Detail"].default_value = 4.0
    L.new(tc.outputs["Object"], wv.inputs["Vector"])
    kit._bump(N, L, b, wv.outputs["Fac"], 0.35, 0.5)
    kit._fogged(m, b.outputs[0])
    return m


# ---------------------------------------------------------------------------------------------- parts
def prism_roof(kit, name, cx, y0, z0, w, d, rh, ov, mat_roof, mat_gable, axis_x=True):
    """A pitched roof, ridge along x (or y), over a body whose front-left-bottom corner is (cx - w/2, y0, z0)."""
    hx, hy = w / 2 + ov, d / 2 + ov
    if axis_x:
        v = [(-hx, -hy, 0), (hx, -hy, 0), (hx, hy, 0), (-hx, hy, 0), (-hx, 0, rh), (hx, 0, rh)]
        f = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]
        gab = [2, 3]
    else:
        v = [(-hx, -hy, 0), (hx, -hy, 0), (hx, hy, 0), (-hx, hy, 0), (0, -hy, rh), (0, hy, rh)]
        f = [(0, 4, 5, 3), (1, 2, 5, 4), (0, 1, 4), (2, 3, 5), (0, 3, 2, 1)]
        gab = [2, 3]
    ob = kit.mesh_obj(name, v, f, mat_roof, None, (cx, y0 + d / 2, z0))
    ob.data.materials.append(mat_gable)
    for i, p in enumerate(ob.data.polygons):
        p.material_index = 1 if i in gab else 0
    return ob


def tiny_fig(kit, M, name, x, y, z, yaw, top, hair, skin, pants="#4a4a52", sit=False, glue=True, scale=1.0, tall=1.0,
             mats=None):
    """A crude glued figure about 4.5 cm tall: block legs, torso and arms, a cube head, two dot eyes. Matte and a
    little wrong on purpose, so the Resident reads as made better."""
    s = scale
    root = kit.empty(name, (x, y, z), None, (0, 0, math.radians(yaw)))
    mt, mh, ms, mp = mats or (kit.plastic(top, 0.95), kit.plastic(hair, 0.95), kit.plastic(skin, 0.9), kit.plastic(pants, 0.95))
    if glue:
        kit.cyl(f"{name}.glue", 0.0135 * s, 0.0018, (0, 0, 0.0009), M["glue"], root, n=16)
        kit.cyl(f"{name}.base", 0.0105 * s, 0.0016, (0, 0, 0.0021), M["street"], root, n=16)
    z0 = 0.0035 if glue else 0.0
    lh = 0.016 * s * tall
    if sit:
        for sx in (-1, 1):
            kit.box(f"{name}.leg{sx}", (0.0085 * s, 0.018 * s, 0.0085 * s), (sx * 0.0045 * s, -0.0045 * s, z0 + 0.0125 * s), mp, root)
        zt = z0 + 0.0125 * s
    else:
        for sx in (-1, 1):
            kit.box(f"{name}.leg{sx}", (0.0085 * s, 0.009 * s, lh), (sx * 0.0045 * s, 0, z0 + lh / 2), mp, root)
        zt = z0 + lh
    kit.box(f"{name}.torso", (0.019 * s, 0.011 * s, 0.016 * s), (0, 0, zt + 0.008 * s), mt, root, bevel=0.0007)
    for sx in (-1, 1):
        kit.box(f"{name}.arm{sx}", (0.0055 * s, 0.0065 * s, 0.0145 * s), (sx * 0.0122 * s, 0, zt + 0.0083 * s), mt, root)
    kit.box(f"{name}.head", (0.0125 * s, 0.0115 * s, 0.0125 * s), (0, 0, zt + 0.0225 * s), ms, root, bevel=0.001)
    kit.box(f"{name}.hair", (0.0135 * s, 0.0125 * s, 0.005 * s), (0, 0.0006 * s, zt + 0.0285 * s), mh, root, bevel=0.0008)
    for sx in (-1, 1):
        kit.box(f"{name}.eye{sx}", (0.0013 * s, 0.0008, 0.0016 * s), (sx * 0.0029 * s, -0.0058 * s, zt + 0.0232 * s), M["ink"], root)
    return root


def window(kit, M, name, cx, y, zc, w=0.075, h=0.065, hollow=False, axis_sign=-1, bars=True):
    """A tiny glazed window on a front face at y: a white frame, the glass (dark if solid), and a cross bar."""
    fw = 0.006
    for sx in (-1, 1):
        kit.box(f"{name}.fv{sx}", (fw, 0.006, h + 2 * fw), (cx + sx * (w / 2 + fw / 2 - 0.001), y - 0.0025, zc), M["trim"])
    for sz in (-1, 1):
        kit.box(f"{name}.fh{sz}", (w + 2 * fw, 0.006, fw), (cx, y - 0.0025, zc + sz * (h / 2 + fw / 2 - 0.001)), M["trim"])
    if not hollow:
        kit.box(f"{name}.gl", (w, 0.003, h), (cx, y - 0.0005, zc), M["dark"])
        if bars:
            kit.box(f"{name}.bv", (0.003, 0.005, h), (cx, y - 0.003, zc), M["trim"])
            kit.box(f"{name}.bh", (w, 0.005, 0.003), (cx, y - 0.003, zc), M["trim"])


def simple_house(kit, M, name, row, cx, w, d, h, wall, roof, door, rh=0.12, nwin=2, axis_x=True, chimney=True):
    r0 = LAY.row_y(row)
    zt = LAY.top_z(row)
    yf = r0 + LAY.FRONT
    mw = kit.plastic(wall, 0.9)
    kit.box(f"{name}.body", (w, d, h), (cx, yf + d / 2, zt + h / 2), mw, bevel=0.002)
    prism_roof(kit, f"{name}.roof", cx, yf, zt + h, w, d, rh, 0.025, kit.plastic(roof, 0.85), mw, axis_x)
    kit.box(f"{name}.door", (0.04, 0.006, 0.085), (cx - w * 0.28, yf - 0.002, zt + 0.0425), kit.plastic(door, 0.7))
    kit.box(f"{name}.step", (0.05, 0.012, 0.006), (cx - w * 0.28, yf - 0.008, zt + 0.003), M["stone"])
    zc = zt + 0.0425 + LAY.FLOOR_T + 0.02 + 0.02
    wx = [cx + w * 0.17] if nwin == 1 else [cx + w * 0.12, cx + w * 0.34]
    for k, x in enumerate(wx[:nwin]):
        window(kit, M, f"{name}.w{k}", x, yf, zt + 0.095, w=0.07 if nwin == 2 else 0.08)
    if chimney:
        kit.box(f"{name}.chim", (0.04, 0.05, 0.08), (cx + w * 0.3, yf + d * 0.65, zt + h + rh * 0.7), mw)


def hollow_shell(kit, M, name, key, interior="#cfc3a8", floor="#7b5a3d", door=None):
    """A house with a real room behind its window. Returns the room's data (the roof is its own object)."""
    r = LAY.room(key)
    cx, w, d = r["cx"], r["w"], r["d"]
    yf, zf, zt = r["front_y"], r["floor_z"], LAY.top_z(r["row"])
    t = LAY.WALL
    h = LAY.H_BODY
    outer = kit.plastic(r["wall"], 0.9)
    inner = kit.plastic(interior, 0.95)
    flo = kit.plastic(floor, 0.8)
    kit.box(f"{name}.floor", (w, d, LAY.FLOOR_T), (cx, yf + d / 2, zt + LAY.FLOOR_T / 2), flo)
    # the front wall, with the window opening
    wx0, wx1 = r["win_x"] - LAY.WIN_W / 2, r["win_x"] + LAY.WIN_W / 2
    z0, z1 = zf + LAY.SILL, zf + LAY.SILL + LAY.WIN_H
    zb, zr = zt + LAY.FLOOR_T, zt + h
    L0, R1 = cx - w / 2, cx + w / 2
    yc = yf + t / 2
    kit.box(f"{name}.fw_low", (w, t, z0 - zt), (cx, yc, (zt + z0) / 2), outer)
    kit.box(f"{name}.fw_up", (w, t, zr - z1), (cx, yc, (z1 + zr) / 2), outer)
    kit.box(f"{name}.fw_l", (wx0 - L0, t, z1 - z0), ((L0 + wx0) / 2, yc, (z0 + z1) / 2), outer)
    kit.box(f"{name}.fw_r", (R1 - wx1, t, z1 - z0), ((wx1 + R1) / 2, yc, (z0 + z1) / 2), outer)
    # inside face of the front wall, a lining so the room reads as plaster, not the painted outside
    kit.box(f"{name}.bw", (w, t, h), (cx, yf + d - t / 2, zt + h / 2), inner)
    for sx in (-1, 1):
        kit.box(f"{name}.sw{sx}", (t, d, h), (cx + sx * (w / 2 - t / 2), yf + d / 2, zt + h / 2), inner)
    ceil = kit.box(f"{name}.ceil", (w, d, t), (cx, yf + d / 2, zr - t / 2), inner)
    # glass and frame
    kit.box(f"{name}.pane", (LAY.WIN_W, 0.0008, LAY.WIN_H), (r["win_x"], yf + t / 2, r["win_z"]), glass_pane(kit))
    window(kit, M, name + ".win", r["win_x"], yf, r["win_z"], w=LAY.WIN_W, h=LAY.WIN_H, hollow=True)
    # inner sill
    kit.box(f"{name}.sill", (LAY.WIN_W + 0.012, 0.012, 0.004), (r["win_x"], yf - 0.006, z0 - 0.002), M["trim"])
    kit.box(f"{name}.sill_in", (LAY.WIN_W + 0.01, 0.012, 0.004), (r["win_x"], yf + t + 0.006, z0 - 0.002), M["trim"])
    roof = prism_roof(kit, f"{name}.roof", cx, yf, zt + h, w, d, 0.13 if key != "tea" else 0.16, 0.03,
                      kit.plastic(r["roof"], 0.85), outer)
    dc = door or "#7a6a58"
    kit.box(f"{name}.door", (0.04, 0.006, 0.085), (cx - w * 0.30 if r["wx"] > 0 else cx + w * 0.30, yf - 0.002, zt + 0.0425),
            kit.plastic(dc, 0.7))
    kit.box(f"{name}.step", (0.05, 0.012, 0.006), (cx - w * 0.30 if r["wx"] > 0 else cx + w * 0.30, yf - 0.008, zt + 0.003), M["stone"])
    kit.box(f"{name}.chim", (0.04, 0.05, 0.08), (cx + w * 0.3, yf + d * 0.65, zt + h + 0.1), outer)
    return {"roof": roof, "ceil": ceil, "r": r}


def room_light(kit, name, key, dx, dy, dz, energy, hexc="#ffd7a8", size=0.012):
    r = LAY.room(key)
    return kit.light(name, "POINT", (r["win_x"] + dx, r["front_y"] + dy, r["floor_z"] + dz), energy, hexc, size=size)


def table(kit, M, name, x, y, z, w, d, h, mat, legs=True):
    kit.box(f"{name}.top", (w, d, 0.003), (x, y, z + h), mat)
    if legs:
        for sx in (-1, 1):
            for sy in (-1, 1):
                kit.box(f"{name}.l{sx}{sy}", (0.003, 0.003, h), (x + sx * (w / 2 - 0.003), y + sy * (d / 2 - 0.003), z + h / 2), mat)


def chair(kit, M, name, x, y, z, mat, yaw=0.0, s=1.0):
    root = kit.empty(name, (x, y, z), None, (0, 0, math.radians(yaw)))
    kit.box(f"{name}.seat", (0.016 * s, 0.016 * s, 0.002), (0, 0, 0.014 * s), mat, root)
    kit.box(f"{name}.back", (0.016 * s, 0.002, 0.018 * s), (0, 0.007 * s, 0.024 * s), mat, root)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"{name}.l{sx}{sy}", (0.002, 0.002, 0.014 * s), (sx * 0.0065 * s, sy * 0.0065 * s, 0.007 * s), mat, root)
    return root


# ---------------------------------------------------------------------------------------------- the rooms
def room_bakery(kit, M):
    sh = hollow_shell(kit, M, "bakery", "bakery", interior="#d8cdb3", floor="#8a6a48", door="#8c5f4a")
    r = sh["r"]
    cx, yf, zf = r["cx"], r["front_y"], r["floor_z"]
    wood = kit.plastic("#7a5236", 0.7)
    # a counter along the back and a shelf of tiny loaves
    kit.box("bakery.counter", (0.34, 0.06, 0.032), (cx, yf + 0.40, zf + 0.016), wood)
    kit.box("bakery.shelf", (0.30, 0.04, 0.003), (cx + 0.02, yf + 0.47, zf + 0.085), wood)
    kit.box("bakery.shelf2", (0.30, 0.04, 0.003), (cx + 0.02, yf + 0.47, zf + 0.15), wood)
    for k in range(6):
        kit.box(f"bakery.loaf{k}", (0.022, 0.012, 0.012), (cx - 0.1 + k * 0.045, yf + 0.47, zf + 0.092), kit.plastic("#b98a4f", 0.7), bevel=0.004)
    for k in range(4):
        kit.box(f"bakery.loafb{k}", (0.024, 0.012, 0.011), (cx - 0.07 + k * 0.05, yf + 0.47, zf + 0.157), kit.plastic("#a97a43", 0.7), bevel=0.004)
    kit.box("bakery.tray", (0.12, 0.05, 0.004), (cx - 0.06, yf + 0.40, zf + 0.034), M["metal"])
    for k in range(5):
        kit.box(f"bakery.roll{k}", (0.016, 0.014, 0.01), (cx - 0.1 + k * 0.022, yf + 0.40, zf + 0.041), kit.plastic("#c99a5c", 0.6), bevel=0.004)
    kit.box("bakery.sack", (0.05, 0.04, 0.06), (cx + 0.18, yf + 0.18, zf + 0.03), kit.plastic("#cfc6b2", 0.95), bevel=0.01)
    room_light(kit, "light bakery", "bakery", 0.07, 0.07, 0.04, 0.12)
    r = sh["r"]
    mist = kit.box("bakery.mist", (LAY.WIN_W, 0.0008, LAY.WIN_H), (r["win_x"], r["front_y"] + LAY.WALL / 2 + 0.002, r["win_z"]),
                   mist_mat(kit, "mist bakery", 0.0))
    sh["mist"] = mist
    return sh


def room_blue(kit, M):
    sh = hollow_shell(kit, M, "blue", "blue", interior="#cdd3d6", floor="#6d5a48", door="#3f6aa8")
    r = sh["r"]
    cx, yf, zf = r["cx"], r["front_y"], r["floor_z"]
    wood = kit.plastic("#6b4a33", 0.7)
    table(kit, M, "blue.table", r["win_x"] - 0.03, yf + 0.16, zf, 0.10, 0.07, 0.03, wood)
    # a cup the size of a seed on the table behind where he stands
    kit.cyl("blue.cup", 0.0022, 0.0035, (r["win_x"] - 0.03, yf + 0.16, zf + 0.0333), kit.plastic("#d8d2c4", 0.4), n=10)
    chair(kit, M, "blue.chair", r["win_x"] + 0.06, yf + 0.18, zf, wood, 90)
    kit.box("blue.rug", (0.16, 0.14, 0.002), (cx, yf + 0.25, zf + 0.001), kit.plastic("#7d6b8c", 0.95))
    kit.box("blue.shelf", (0.2, 0.03, 0.003), (cx, yf + d_in(r, 0.01), zf + 0.11), wood)
    room_light(kit, "light blue", "blue", -0.07, 0.07, 0.04, 0.9)
    return sh


def d_in(r, off):
    return r["d"] - off - 0.02


def room_chapel(kit, M):
    sh = hollow_shell(kit, M, "chapel", "chapel", interior="#d6d1c3", floor="#5f5a52", door="#5d4a3a")
    r = sh["r"]
    cx, yf, zf = r["cx"], r["front_y"], r["floor_z"]
    wood = kit.plastic("#5b4330", 0.7)
    for k in range(3):
        for sx in (-1, 1):
            kit.box(f"chapel.pew{k}{sx}", (0.12, 0.016, 0.03), (cx + sx * 0.14, yf + 0.17 + k * 0.1, zf + 0.015), wood)
    kit.box("chapel.altar", (0.12, 0.04, 0.035), (cx, yf + 0.55, zf + 0.0175), kit.plastic("#cfc9b8", 0.8))
    kit.box("chapel.bell", (0.08, 0.08, 0.16), (cx, yf + 0.3, LAY.top_z(r["row"]) + LAY.H_BODY + 0.18), kit.plastic(r["wall"], 0.9), bevel=0.004)
    room_light(kit, "light chapel", "chapel", 0.07, 0.07, 0.04, 0.1)
    return sh


def room_next(kit, M):
    sh = hollow_shell(kit, M, "next", "next", interior="#d9cdc9", floor="#6d5a48", door="#8a5a66")
    r = sh["r"]
    wood = kit.plastic("#6b4a33", 0.7)
    chair(kit, M, "next.chair", r["win_x"] - 0.07, r["front_y"] + 0.2, r["floor_z"], wood, 0)
    kit.box("next.bed", (0.12, 0.2, 0.02), (r["cx"] - 0.1, r["front_y"] + 0.38, r["floor_z"] + 0.01), kit.plastic("#8c9aa8", 0.95))
    room_light(kit, "light next", "next", -0.07, 0.07, 0.04, 1.0)
    return sh


def room_cottage(kit, M):
    sh = hollow_shell(kit, M, "cottage", "cottage", interior="#d3d0c6", floor="#6d5a48", door="#e0b52a")
    r = sh["r"]
    kit.box("cottage.bed", (0.12, 0.2, 0.02), (r["cx"] - 0.1, r["front_y"] + 0.38, r["floor_z"] + 0.01), kit.plastic("#8aa08a", 0.95))
    room_light(kit, "light cottage", "cottage", -0.07, 0.07, 0.04, 0.8)
    return sh


def room_tea(kit, M):
    sh = hollow_shell(kit, M, "tea", "tea", interior="#e2d6b8", floor="#8a6240", door="#7a5a40")
    r = sh["r"]
    cx, yf, zf = r["cx"], r["front_y"], r["floor_z"]
    wood = kit.plastic("#7a5236", 0.7)
    wx = r["win_x"]
    ctx = {"roof": sh["roof"], "ceil": sh["ceil"]}
    # the window table with the one empty chair at it (my figure's, later), the Resident stands beside it
    table(kit, M, "tea.wt", wx - 0.02, yf + 0.045, zf, 0.05, 0.038, 0.026, wood)
    chair(kit, M, "tea.chair_empty", wx - 0.02, yf + 0.078, zf, wood, 0)
    kit.cyl("tea.cup1", 0.003, 0.004, (wx - 0.03, yf + 0.045, zf + 0.0285), kit.plastic("#d8d2c4", 0.4), n=10)
    ctx["seat"] = (wx - 0.02, yf + 0.078, zf)
    # the tiny townsfolk at their tables: the same clothes as the ones who come to the model at L64
    spots = [(cx + 0.2, yf + 0.25), (cx - 0.02, yf + 0.33), (cx + 0.22, yf + 0.46), (cx - 0.24, yf + 0.45), (cx - 0.25, yf + 0.22)]
    cols = [("#cfc6b0", "#7a7a7a", "#2c3345"), ("#2d2f36", "#1e1a18", "#24262c"), ("#f1e24f", "#8a4a2a", "#3b4a63"),
            ("#6c5b4a", "#3a4a5a", "#3a3a3a"), ("#7a3f55", "#2a1d15", "#2a2c34")]
    for k, (x, y) in enumerate(spots):
        table(kit, M, f"tea.t{k}", x, y, zf, 0.065, 0.05, 0.026, wood)
        top, hair, pants = cols[k]
        tiny_fig(kit, M, f"tea.seat{k}", x, y + 0.045, zf, 0, top, hair, SKINS[k % 4], pants=pants, sit=True, glue=False)
        chair(kit, M, f"tea.c{k}", x, y + 0.047, zf, wood, 0)
    kit.box("tea.counter", (0.34, 0.05, 0.034), (cx - 0.1, yf + 0.58, zf + 0.017), wood)
    kit.box("tea.urn", (0.03, 0.03, 0.05), (cx - 0.2, yf + 0.58, zf + 0.06), M["metal"])
    room_light(kit, "light tea", "tea", 0.075, 0.025, 0.004, 0.45, "#ffc08a", size=0.004)
    room_light(kit, "light tea back", "tea", 0.1, 0.4, 0.1, 0.5, "#ffcf9a", size=0.02)
    return ctx


# ---------------------------------------------------------------------------------------------- the village
def build_village(kit, M, ctx):
    green = kit.grime("#5f7d47", dark=0.78, scale=14, name="moss paint", rough=0.92)
    M["green"] = green
    xs, xe = LAY.XMIN, LAY.XMAX
    for i in range(LAY.ROWS):
        y0 = LAY.row_y(i)
        zt = LAY.top_z(i)
        kit.box(f"terrace{i}", (xe - xs, LAY.ROW_DY, zt), ((xs + xe) / 2, y0 + LAY.ROW_DY / 2, zt / 2), green)
        # the street along the terrace's front (a grey lane) and a pavement edge
        kit.box(f"street{i}", (xe - xs - 0.1, 0.5, 0.004), ((xs + xe) / 2, y0 + 0.31, zt + 0.002), M["street"])
    # the main street, up the hill at x = 0 (a lane through every row)
    for i in range(LAY.ROWS):
        y0 = LAY.row_y(i)
        kit.box(f"main{i}", (0.55, LAY.ROW_DY - 0.06, 0.004), (0.0, y0 + LAY.ROW_DY / 2 + 0.0, LAY.top_z(i) + 0.0025), M["street"])
    # the old stone under the green, revealed when it's sanded off (S17), at the front-left corner of terrace 0
    ctx["stone_objs"] = build_stone(kit, M)
    # houses: skip the six rooms' slots
    occupied = {(v["row"], round(v["cx"], 2)) for v in LAY.ROOMS.values()}
    import random
    rng = random.Random(22)
    for i in range(LAY.ROWS):
        x = xs + 0.35
        k = 0
        while x < xe - 0.3:
            w = rng.choice([0.38, 0.42, 0.46, 0.5])
            cx = x + w / 2
            clash = [v for v in LAY.ROOMS.values() if v["row"] == i and abs(v["cx"] - cx) < (v["w"] + w) / 2 + 0.06]
            if abs(cx) < 0.36:      # the main street
                x = 0.36 + 0.02
                continue
            if clash:
                x = max(v["cx"] + v["w"] / 2 for v in clash) + 0.08
                continue
            simple_house(kit, M, f"h{i}_{k}", i, cx, w, rng.choice([0.4, 0.45, 0.5]), rng.choice([0.22, 0.25, 0.28]),
                         rng.choice(PASTEL), rng.choice(ROOFS), rng.choice(DOORS), rh=rng.choice([0.1, 0.12, 0.14]),
                         nwin=rng.choice([1, 2]), axis_x=rng.random() < 0.7)
            x += w + rng.choice([0.07, 0.1, 0.14])
            k += 1
    ctx["rooms"] = {"bakery": room_bakery(kit, M), "blue": room_blue(kit, M), "chapel": room_chapel(kit, M),
                    "next": room_next(kit, M), "cottage": room_cottage(kit, M)}
    ctx["tea"] = room_tea(kit, M)
    rb = LAY.room("bakery")
    kit.light("open key", "POINT", (rb["win_x"] - 0.035, rb["front_y"] - 0.035, rb["floor_z"] + 0.05), 0.5, "#ffe0bc", size=0.006)


def build_stone(kit, M):
    """The ground's old stone, under the green: laid over terrace 0's front-left corner (top and both faces) from
    L17, rounded so it wraps the corner with no joins. A few flakes of green paint lie around its edge."""
    st = stone_mat(kit)
    zt = LAY.top_z(0)
    objs = []
    # a rounded slab over the corner: x from -2.92 to -1.0, y from -0.002 to 0.9, top at zt + 0.0015, down the faces
    ob = kit.box("stone.corner", (1.9, 0.9, zt + 0.008), (-1.97, 0.45 - 0.003, (zt + 0.008) / 2), st, bevel=0.05, seg=4)
    objs.append(ob)
    import random
    rng = random.Random(5)
    for k in range(34):
        x = rng.uniform(-3.0, -0.95)
        y = rng.uniform(0.7, 1.1)
        if rng.random() < 0.5:
            y = rng.uniform(0.45, 0.95)
            x = rng.choice([-0.96, -0.94]) + rng.uniform(-0.03, 0.12)
        s = rng.uniform(0.015, 0.05)
        objs.append(kit.box(f"flake{k}", (s, s * rng.uniform(0.5, 1.2), 0.0015), (x, y, zt + 0.0095), M["green"], rot=(0, 0, rng.uniform(0, 3))))
    return objs


def build_town(kit, M, ctx):
    """The full-size town: a brick terrace across the road behind the camera, my cottage with the yellow door."""
    brick = kit.bricks("#9a5a44", "#7d4636", "#b4aa9c", scale=1.0, name="town brick")
    slate = kit.plastic("#454a50", 0.8)
    xs = [-9.0, -5.2, -1.6, 2.0, 5.8, 9.4]
    cols = [(brick, "#6a4d3a"), (brick, "#3f6a8c"), (brick, "#e0b52a"), (brick, "#5a6a5f"), (brick, "#8a5a66"), (brick, "#4a4f5a")]
    for k, x in enumerate(xs):
        w, h = 3.4, 5.6 + (k % 3) * 0.5
        y = -9.0
        kit.box(f"town{k}", (w, 5.0, h), (x, y, h / 2), brick)
        prism_roof(kit, f"town{k}.roof", x, y - 2.5, h, w, 5.0, 1.6, 0.25, slate, brick)
        kit.box(f"town{k}.door", (0.95, 0.12, 2.0), (x - 0.7, y + 2.5 + 0.0, 1.0), kit.plastic(cols[k][1], 0.6))
        kit.box(f"town{k}.chim", (0.6, 0.6, 1.4), (x + 0.9, y, h + 1.2), brick)
        for wx_ in (0.55, 1.05):
            for wz in (1.4, 3.4):
                kit.box(f"town{k}.w{wx_}{wz}", (0.7, 0.1, 1.0), (x + wx_ * 1.2 - 0.1, y + 2.5 + 0.0, wz), M["dark"])
                kit.box(f"town{k}.wf{wx_}{wz}", (0.82, 0.08, 1.12), (x + wx_ * 1.2 - 0.1, y + 2.52, wz), M["trim"])



# ---------------------------------------------------------------------------------------------- full-size rooms
def mist_mat(kit, name="mist", fac=0.0):
    """A pane that fogs: a white-grey film mixed over nothing; `fac` is a value node the animation moves."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    df = nt.nodes.new("ShaderNodeBsdfDiffuse")
    df.inputs["Color"].default_value = (0.55, 0.57, 0.6, 1)
    vl = nt.nodes.new("ShaderNodeValue")
    vl.outputs[0].default_value = fac
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(vl.outputs[0], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(df.outputs[0], mx.inputs[2])
    kit._fogged(m, mx.outputs[0])
    m["fac_node"] = vl.name
    return m


def build_tea_real(kit, M, ctx):
    """The full-size tea shop at x = TX: honey wood, warm cream walls, steamed windows, a counter and tables."""
    TX = LAY.TX
    wall = kit.plastic("#e9dcc0", 0.9)
    honey = kit.planks("#9a6a3c", "#7a512c", scale=2.2, axis="X", name="tea honey")
    wood = kit.plastic("#8a5a32", 0.6)
    brick = kit.bricks("#9a5a44", "#7d4636", "#b4aa9c", scale=1.0, name="town brick")
    kit.box("tea.floorR", (8, 6, 0.1), (TX, 0, -0.05), honey)
    kit.box("tea.ceilR", (8, 6, 0.1), (TX, 0, 3.15), wall)
    kit.box("tea.backR", (8, 0.12, 3.1), (TX, 3.0, 1.55), wall)
    for sx in (-1, 1):
        kit.box(f"tea.sideR{sx}", (0.12, 6, 3.1), (TX + sx * 4.0, 0, 1.55), wall)
    # the front wall (y = -3): pillars, windows, door gap
    fy = -3.0
    kit.box("tea.fb0", (3.5, 0.2, 0.9), (TX - 2.25, fy, 0.45), brick)
    kit.box("tea.fb1", (3.5, 0.2, 0.9), (TX + 2.25, fy, 0.45), brick)
    kit.box("tea.ftop", (8, 0.2, 1.0), (TX, fy, 2.6), brick)
    for x0, x1 in ((-4.0, -3.3), (-1.7, -0.5), (0.5, 1.7), (3.3, 4.0)):
        kit.box(f"tea.fp{x0}", (x1 - x0, 0.2, 1.2), (TX + (x0 + x1) / 2, fy, 1.5), brick)
    mist = mist_mat(kit, "mist tea", 0.6)
    for x0, x1 in ((-3.3, -1.7), (1.7, 3.3)):
        kit.box(f"tea.pane{x0}", (x1 - x0, 0.01, 1.2), (TX + (x0 + x1) / 2, fy + 0.02, 1.5), mist)
        kit.box(f"tea.sill{x0}", (x1 - x0 + 0.2, 0.3, 0.05), (TX + (x0 + x1) / 2, fy - 0.1, 0.9), M["trim"])
    kit.box("tea.doorframe", (1.2, 0.3, 0.12), (TX, fy - 0.05, 2.15), kit.plastic("#5a3f2a", 0.6))
    kit.box("tea.doorpost0", (0.1, 0.3, 2.1), (TX - 0.55, fy - 0.05, 1.05), kit.plastic("#5a3f2a", 0.6))
    kit.box("tea.doorpost1", (0.1, 0.3, 2.1), (TX + 0.55, fy - 0.05, 1.05), kit.plastic("#5a3f2a", 0.6))
    kit.box("tea.awning", (8.4, 0.9, 0.1), (TX, fy - 0.45, 2.3 + 0.4), kit.plastic("#cfd6cf", 0.8), rot=(math.radians(-10), 0, 0))
    kit.box("ground2", (60, 40, 0.1), (TX, -23.0, -0.05), kit.cobbles("#6f6d68", "#8a867d", "#3b3a38", scale=3, wet=0.2, name="town cobbles"))
    kit.box("ground3", (60, 40, 0.1), (TX, 23.0, -0.05), kit.concrete("#6a6862", 3, 0.4, name="back lane"))
    # the counter along the back, shelves, a cake stand, tables with chairs
    kit.box("tea.counter", (5.0, 0.8, 1.05), (TX + 0.5, 2.4, 0.525), wood)
    kit.box("tea.counter_top", (5.2, 0.9, 0.06), (TX + 0.5, 2.4, 1.08), kit.plastic("#d8cdb4", 0.4))
    for k in range(3):
        kit.box(f"tea.shelf{k}", (5.0, 0.3, 0.05), (TX + 0.5, 2.85, 1.5 + k * 0.5), wood)
        for j in range(8):
            kit.box(f"tea.jar{k}{j}", (0.2, 0.2, 0.28), (TX - 1.6 + j * 0.62, 2.85, 1.68 + k * 0.5), kit.plastic(["#c9d6cf", "#d9c9a0", "#b7c2d0"][(j + k) % 3], 0.4), bevel=0.04)
    kit.box("tea.urn", (0.35, 0.35, 0.55), (TX - 1.6, 2.4, 1.38), M["metal"], bevel=0.05)
    tables = [(-2.5, -1.0), (2.2, -1.2), (-0.2, 0.6), (-2.6, 0.9), (2.4, 0.9)]
    ctx["tea_tables"] = tables
    for k, (x, y) in enumerate(tables):
        table(kit, M, f"tea.rt{k}", TX + x, y, 0, 0.9, 0.7, 0.75, wood)
        for sy in (-1, 1):
            chair(kit, M, f"tea.rc{k}{sy}", TX + x, y + sy * 0.62, 0, wood, 0 if sy > 0 else 180, s=28.0)
        kit.cyl(f"tea.rcup{k}", 0.05, 0.08, (TX + x + 0.15, y, 0.79), kit.plastic("#e8e2d4", 0.4), n=16)
    # warm light in the room: honey, the same grey day only coming through steamed glass
    for k, x in enumerate((-2.4, 0.2, 2.6)):
        kit.light(f"tea lamp{k}", "POINT", (TX + x, 0.2, 2.8), 60, "#ffcf98", size=0.3)
    kit.light("tea table fill", "POINT", (TX - 2.5, -1.3, 1.6), 22, "#ffe2bd", size=0.2)
    kit.light("tea window fill", "POINT", (TX, -1.8, 1.8), 22, "#ffe2bd", size=0.3)
    # a window box and flower pots outside would be text-free decoration: two pots
    for sx in (-1, 1):
        kit.cyl(f"tea.pot{sx}", 0.18, 0.4, (TX + sx * 2.5, fy - 0.6, 0.2), kit.plastic("#8a5a44", 0.8), n=16)


def build_cottage_room(kit, M, ctx):
    """My cottage room at x = CX: a bed along the west wall, a desk with a lamp, a window with curtains."""
    CX = LAY.CX
    wall = kit.plastic("#cfc7b6", 0.92)
    floor = kit.planks("#6a4a30", "#4e3520", scale=2.0, axis="X", name="cottage boards")
    kit.box("cot.floor", (4.4, 5.4, 0.1), (CX, 0, -0.05), floor)
    kit.box("cot.ceil", (4.4, 5.4, 0.1), (CX, 0, 2.55), wall)
    kit.box("cot.back", (4.4, 0.1, 2.5), (CX, 2.7, 1.25), wall)
    kit.box("cot.front", (4.4, 0.1, 2.5), (CX, -2.7, 1.25), wall)
    kit.box("cot.west", (0.1, 5.4, 2.5), (CX - 2.2, 0, 1.25), wall)
    ex = CX + 2.2
    # the east wall with a window opening y -0.7..0.7, z 0.95..2.05
    kit.box("cot.e0", (0.1, 2.0, 2.5), (ex, -1.7, 1.25), wall)
    kit.box("cot.e1", (0.1, 2.0, 2.5), (ex, 1.7, 1.25), wall)
    kit.box("cot.e2", (0.1, 1.4, 0.95), (ex, 0, 0.475), wall)
    kit.box("cot.e3", (0.1, 1.4, 0.45), (ex, 0, 2.275), wall)
    kit.box("cot.sill", (0.25, 1.6, 0.05), (ex - 0.1, 0, 0.95), M["trim"])
    for k in range(2):
        kit.box(f"cot.pane{k}", (0.02, 1.4, 1.1), (ex + 0.06, 0, 1.5), glass_pane(kit)) if k == 0 else None
    kit.box("cot.frame_t", (0.1, 1.5, 0.06), (ex - 0.02, 0, 2.06), M["trim"])
    kit.box("cot.frame_m", (0.08, 0.05, 1.1), (ex - 0.02, 0, 1.5), M["trim"])
    ctx["curtains"] = []
    cm = kit.plastic("#8a8f7a", 0.95)
    for sy in (-1, 1):
        c = kit.box(f"cot.curtain{sy}", (0.06, 0.85, 1.7), (ex - 0.2, sy * 0.95, 1.4), cm)
        ctx["curtains"].append((c, sy))
    # bed along the west wall, head at the north end of x
    kit.box("cot.bed", (2.0, 0.95, 0.4), (CX - 1.0, -0.9, 0.2), kit.plastic("#6b5848", 0.8))
    kit.box("cot.mattress", (1.95, 0.9, 0.18), (CX - 1.0, -0.9, 0.49), kit.plastic("#d9d4c6", 0.95), bevel=0.04)
    kit.box("cot.quilt", (1.1, 0.92, 0.1), (CX - 0.55, -0.9, 0.62), kit.plastic("#7e8f78", 0.97), bevel=0.04)
    kit.box("cot.pillow", (0.45, 0.6, 0.12), (CX - 1.78, -0.9, 0.64), kit.plastic("#ece8de", 0.95), bevel=0.05)
    kit.box("cot.table", (0.4, 0.4, 0.5), (CX - 1.95, 0.0, 0.25), kit.plastic("#7a5a40", 0.7))
    kit.cyl("cot.lampbase", 0.08, 0.2, (CX - 1.95, 0.0, 0.6), kit.plastic("#d8d0bc", 0.6), n=16)
    kit.cyl("cot.shade", 0.12, 0.18, (CX - 1.95, 0.0, 0.8), kit.emit("#ffd9a0", 1.2), n=16, r2=0.09)
    # the desk and its lamp (the painting, L63)
    kit.box("cot.desk", (1.2, 0.6, 0.04), (CX + 0.6, 1.5, 0.75), kit.plastic("#7a5a40", 0.7))
    for sx in (-1, 1):
        kit.box(f"cot.dl{sx}", (0.05, 0.5, 0.75), (CX + 0.6 + sx * 0.55, 1.5, 0.375), kit.plastic("#7a5a40", 0.7))
    kit.cyl("cot.dlamp", 0.06, 0.4, (CX + 0.05, 1.7, 1.0), M["metal"], n=12)
    for k in range(4):
        kit.cyl(f"cot.jar{k}", 0.035, 0.07, (CX + 0.95 + k * 0.07, 1.7, 0.805), kit.plastic(["#5ccfc0", "#d9d2c0", "#8aa08a", "#aa8888"][k], 0.3), n=10)
    kit.light("lamp bedside", "POINT", (CX - 1.95, 0.0, 0.85), 22, "#ffcf98", size=0.1)
    kit.light("lamp desk", "POINT", (CX + 0.05, 1.45, 1.25), 110, "#ffd5a0", size=0.08)
    kit.light("cottage fill", "POINT", (CX, -1.2, 2.3), 18, "#c9d2e0", size=0.4)
    ctx["cottage_lamps"] = ["lamp bedside", "lamp desk", "cottage fill"]


def build_props(kit, M, ctx):
    # three tins of paint on the path, a brush
    for k in range(3):
        kit.cyl(f"tin{k}", 0.09, 0.14, (-0.9 + k * 0.22, -0.62, 0.07), kit.plastic(["#e8e2d4", "#cfd8d6", "#e3d6c0"][k], 0.45), n=18)
        kit.cyl(f"tinlid{k}", 0.092, 0.015, (-0.9 + k * 0.22, -0.62, 0.145), M["metal"], n=18)
    # the paint pot of L45: on its side, rolled; teal inside and out
    root = kit.empty("pot", (0, 0, 0.1), None, (math.pi / 2, 0, 0))
    kit.cyl("pot.body", 0.085, 0.16, (0, 0, 0), kit.plastic("#d8d4cc", 0.45), root, n=20)
    kit.cyl("pot.paint", 0.074, 0.01, (0, 0, 0.081), kit.plastic("#5ccfc0", 0.25), root, n=20)
    ctx["pot"] = root
    ctx["puddle"] = kit.cyl("puddle", 1.0, 0.004, (0, 0, 0.003), kit.plastic("#5ccfc0", 0.2), None, n=24)
    # Maggie's box: a small brown carton with a lid, holding the blank figure
    box = kit.empty("mybox", (0, 0, 0))
    cb = kit.plastic("#a98458", 0.85)
    kit.box("mybox.base", (0.16, 0.11, 0.05), (0, 0, 0.025), cb, box, bevel=0.003)
    kit.box("mybox.tissue", (0.145, 0.095, 0.004), (0, 0, 0.045), kit.plastic("#ece8de", 0.95), box)
    ctx["lid"] = kit.box("mybox.lid", (0.17, 0.12, 0.012), (0, 0, 0.056), cb, box, bevel=0.002)
    ctx["box"] = box
    # my figure: crude, like the rest, painted in stages (blank, hair, coat, brush); standing and sitting
    ctx["mf"] = {k: kit.plastic(c, 0.95, name=f"myfig {k}") for k, c in
                 (("top", "#d9d4c8"), ("hair", "#d9d4c8"), ("skin", "#d9d4c8"), ("pants", "#d9d4c8"))}
    mats = (ctx["mf"]["top"], ctx["mf"]["hair"], ctx["mf"]["skin"], ctx["mf"]["pants"])
    ctx["myfig"] = tiny_fig(kit, M, "myfig", 0, 0, 0, 0, "", "", "", sit=False, glue=False, mats=mats)
    ctx["myfig_sit"] = tiny_fig(kit, M, "myfigs", 0, 0, 0, 0, "", "", "", sit=True, glue=False, mats=mats)
    ctx["brush"] = kit.box("myfig.brush", (0.0012, 0.0012, 0.012), (0.0125, -0.006, 0.0255), kit.plastic("#5b3b27", 0.6), ctx["myfig"])
    ctx["brush2"] = kit.box("myfigs.brush", (0.0012, 0.0012, 0.012), (0.0125, -0.006, 0.0255), kit.plastic("#5b3b27", 0.6), ctx["myfig_sit"])



def dog(kit, name, x, y, z, yaw, col="#8a6a48"):
    root = kit.empty(name, (x, y, z), None, (0, 0, math.radians(yaw)))
    m = kit.plastic(col, 0.95)
    kit.box(f"{name}.body", (0.011, 0.022, 0.011), (0, 0, 0.0115), m, root, bevel=0.0008)
    kit.box(f"{name}.head", (0.0085, 0.009, 0.0085), (0, -0.0135, 0.0165), m, root, bevel=0.001)
    kit.box(f"{name}.tail", (0.002, 0.002, 0.008), (0, 0.012, 0.0165), m, root, rot=(0.5, 0, 0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"{name}.l{sx}{sy}", (0.002, 0.002, 0.0075), (sx * 0.0035, sy * 0.008, 0.00375), m, root)
    return root


def build_figures(kit, M, ctx):
    """About twenty glued villagers in the model's streets, every one with its back to the path (yaw 180)."""
    import random
    rng = random.Random(8)
    spots = [(0, -1.9, 0.36), (0, -0.9, 0.2), (0, 0.55, 0.4), (0, 1.1, 0.25), (0, 1.8, 0.4), (0, 2.6, 0.3),
             (1, -2.4, 0.3), (1, -1.5, 0.4), (1, 0.1, 0.25), (1, 0.7, 0.4), (1, 2.2, 0.28),
             (2, -2.0, 0.35), (2, -0.2, 0.3), (2, 1.4, 0.42), (2, 2.5, 0.25),
             (3, -2.6, 0.3), (3, 0.5, 0.35), (3, 1.9, 0.28),
             (4, -0.5, 0.3), (4, 0.8, 0.4), (4, 2.1, 0.3), (5, -1.6, 0.3), (5, -0.6, 0.38), (5, 2.0, 0.3)]
    for k, (row, x, dy) in enumerate(spots):
        y = LAY.row_y(row) + 0.06 + dy * 0.9
        tiny_fig(kit, M, f"vf{k}", x, y, LAY.top_z(row) + 0.002, 180 + rng.uniform(-9, 9), rng.choice(TOPS), rng.choice(["#2a1d15", "#8a8a8a", "#6a4a2a", "#c9b27a", "#3a3028"]),
                 rng.choice(SKINS), pants=rng.choice(["#3b4a63", "#4a4a52", "#5b5348", "#2c3345"]), scale=rng.uniform(0.92, 1.08))
    # the man with the dog (row 1) and the woman at the gate (row 2)
    row = 1
    y = LAY.row_y(row) + 0.28
    tiny_fig(kit, M, "walker", -0.95, y, LAY.top_z(row) + 0.002, 180, "#7d8f7a", "#444444", SKINS[1], pants="#2c3345")
    dog(kit, "dog", -0.95 + 0.045, y + 0.03, LAY.top_z(row) + 0.002, 180)
    row = 2
    gy = LAY.row_y(row) + 0.30
    gz = LAY.top_z(row)
    fence = kit.plastic("#e8e4d8", 0.8)
    for k in range(7):
        x = -1.15 + k * 0.1
        if 3 <= k <= 3:
            continue
        kit.box(f"fence{k}", (0.012, 0.008, 0.032), (x, gy, gz + 0.016), fence)
    kit.box("fence_rail", (0.2, 0.006, 0.006), (-1.0, gy, gz + 0.024), fence)
    kit.box("fence_rail2", (0.2, 0.006, 0.006), (-0.5, gy, gz + 0.024), fence)
    kit.box("gate", (0.07, 0.006, 0.03), (-0.85, gy + 0.03, gz + 0.016), fence, rot=(0, 0, 1.2))
    tiny_fig(kit, M, "gatewoman", -0.85, gy + 0.005, gz + 0.002, 180, "#9a8190", "#8a4a2a", SKINS[2], pants="#3a3a3a")


# ---------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    ctx = {"tl": tl, "open_end": next((c["t"] for c in tl["cues"] if c["name"] == "bakerylight" and c.get("gain") == 1.0), 2.0)}
    # the camera can get very close to tiny things
    cam = kit.OBJ["cam"]
    cam.data.clip_start = 0.004
    cam.data.dof.use_dof = False
    M = {}
    M["street"] = kit.concrete("#5a5855", scale=9, stains=0.3, name="lane", rough=0.9)
    M["glue"] = kit.plastic("#d9cf9a", 0.25)
    M["ink"] = kit.plastic("#16110f", 0.5)
    M["trim"] = kit.plastic("#ece8dc", 0.7)
    M["dark"] = kit.plastic("#2a3844", 0.12, spec=0.9)
    M["stone"] = kit.plastic("#8d8b86", 0.9)
    M["metal"] = kit.metal("#9a9da0", 0.4)
    ctx["M"] = M

    # the path round the model's front edge (gravel), the grass bank behind, the sea wall and the sea
    grav = kit.cobbles("#6f6d68", "#9a968d", "#3b3a38", scale=26, wet=0.2, name="gravel")
    kit.box("path", (60, 7.0, 0.1), (0, -3.6, -0.05), grav)
    kit.box("bank", (14, 9, 1.6), (-4.0, 14.0, 0.6), kit.grime("#5b6a4c", 0.7, 3.0, name="bank"))
    kit.box("bank2", (16, 6, 2.6), (-3.0, 17.0, 1.2), kit.grime("#4f5d44", 0.7, 3.0, name="bank2"))
    kit.box("wall_e", (0.5, 12.0, 0.7), (3.45, 3.4, 0.0), kit.concrete("#838079", 2, 0.5, name="seawall"))
    sea = kit.box("sea", (160, 160, 0.2), (88, 20, -0.7), sea_mat(kit))
    kit.box("shore", (30, 60, 1.4), (22.0, 6.0, -1.05), kit.concrete("#6d6a64", 3, 0.5, name="shore"))
    build_village(kit, M, ctx)
    build_town(kit, M, ctx)
    build_tea_real(kit, M, ctx)
    build_cottage_room(kit, M, ctx)
    build_props(kit, M, ctx)
    build_figures(kit, M, ctx)

    # light: a soft grey sun from upper left behind, the sky's own fill
    ctx["sun"] = kit.light("sun", "SUN", (0, 0, 10), 2.4, "#e8edf2", rot=(math.radians(-38), 0, math.radians(38)), size=0.0)
    ctx["sun"].data.angle = math.radians(14)
    ctx["world"] = bpy.context.scene.world.node_tree.nodes["Background"]
    ctx["sky_color"] = None
    ctx["world_base"] = 1.0
    return ctx


# ---------------------------------------------------------------------------------------------- animate
def _main_mod():
    return sys.modules.get("__main__")


def _set_color(m, hexc, kit):
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    m.diffuse_color = kit.col(hexc)


def _show(objs, on):
    for o in objs:
        o.hide_render = not on
        for c in o.children_recursive:
            c.hide_render = not on


def animate(kit, story, tl, t, ctx):
    over = {}
    # --- light: grey day, the only changes are slow ramps
    lvl = val(tl, "cloud", "level", t, 1.0)
    over["sun"] = lvl
    sky = _last(_cues(tl, "sky"), t)
    sk = val(tl, "sky", "strength", t, 1.0)
    w = ctx["world"]
    colr = (sky or {}).get("color", "#8d959c")
    if ctx.get("sky_color") != colr:
        w.inputs["Color"].default_value = kit.col(colr)
        ctx["sky_color"] = colr
    w.inputs["Strength"].default_value = sk * (0.62 + 0.38 * lvl)
    over["sun"] = lvl * (sky or {}).get("sun", 1.0)
    over["light bakery"] = val(tl, "bakerylight", "gain", t, 1.0)
    over["open key"] = 1.0 if t < ctx["open_end"] else 0.0
    # --- the lore stone (from L17), the tea shop's roof (lifted for S65), the fog on the bakery glass
    for ob in ctx["stone_objs"]:
        ob.hide_render = not flag(tl, "stone", t, False)
    roof_off = flag(tl, "tearoof", t, False)
    ctx["tea"]["roof"].hide_render = roof_off
    ctx["tea"]["ceil"].hide_render = roof_off
    mist = val(tl, "mist", "level", t, 0.0)
    bpy.data.materials["mist bakery"].node_tree.nodes[bpy.data.materials["mist bakery"]["fac_node"]].outputs[0].default_value = mist
    ctx["rooms"]["bakery"]["mist"].hide_render = mist < 0.005
    # --- the curtains close (a slow slide, never a hand)
    cur = val(tl, "curtain", "level", t, 0.0)
    for c, sy in ctx["curtains"]:
        c.location = (c.location[0], sy * (0.95 - 0.62 * cur), c.location[2])
    # --- the paint pot of L45: knocked over, rolling, teal spreading on the gravel
    pc = _last(_cues(tl, "pot"), t)
    pot, pud = ctx["pot"], ctx["puddle"]
    if pc is None or pc.get("state") == "hidden":
        _show([pot], False)
        pud.hide_render = True
    else:
        x0, y0 = pc["at_xy"]
        z0 = pc.get("z0", 0.0)
        _show([pot], True)
        if pc["state"] == "stand":
            pud.hide_render = True
            pot.rotation_euler = (0, 0, 0)
            pot.location = (x0, y0, z0 + 0.085)
            for ch in pot.children:
                ch.rotation_euler = (0, 0, 0)
        else:
            sec = max(0.0, t - pc["t"])
            pud.hide_render = sec < 0.25
            tip = min(1.0, sec / 0.22)
            trav = 1.1 * (1 - math.exp(-sec * 1.3)) if sec > 0.2 else 0.0
            pot.rotation_euler = (tip * math.pi / 2, 0, 0)
            pot.location = (x0 + trav, y0, z0 + 0.085)
            for ch in pot.children:
                ch.rotation_euler = (0, 0, -trav / 0.085)
            sp = min(1.0, max(0.0, (sec - 0.25) / 1.6))
            pud.location = (x0 + 0.1, y0 - 0.02, z0 + 0.003)
            pud.scale = (0.02 + 0.3 * sp, 0.02 + 0.2 * sp, 1.0)
    # --- Maggie's box
    bc = _last(_cues(tl, "box"), t) or {"where": "none"}
    box, lid = ctx["box"], ctx["lid"]
    where = bc.get("where", "none")
    _show([box], where != "none")
    if where == "hands":
        m = bpy.data.objects.get("maggie")
        yaw = m.rotation_euler.z
        fx, fy = math.sin(yaw), -math.cos(yaw)
        box.location = (m.location.x + 0.40 * fx, m.location.y + 0.40 * fy, m.location.z + 0.93)
        box.rotation_euler = (0, 0, yaw)
        lid.hide_render = False
    elif where == "table":
        box.location = tuple(bc.get("pos", (LAY.TX - 2.5, -1.0, 0.77)))
        box.rotation_euler = (0, 0, math.radians(bc.get("yaw", 0)))
        lid.hide_render = True
    # --- my little figure, painted in stages, in the box, on the desk, or in the window chair
    mc = _last(_cues(tl, "myfig"), t) or {"where": "none"}
    mw, st = mc.get("where", "none"), int(mc.get("stage", 0))
    standing, sitting = ctx["myfig"], ctx["myfig_sit"]
    _show([standing], mw in ("box", "desk"))
    _show([sitting], mw == "seat")
    if mw == "box":
        p = mc.get("pos", (LAY.TX - 2.5 + 0.055, -1.0, 0.838))
        standing.location = tuple(p)
        standing.rotation_euler = (-math.pi / 2, 0, math.radians(90))
    elif mw == "desk":
        standing.location = tuple(mc.get("pos", (LAY.CX + 0.6, 1.45, 0.77)))
        standing.rotation_euler = (0, 0, math.radians(mc.get("yaw", 0)))
    elif mw == "seat":
        sx, sy, sz = ctx["tea"]["seat"]
        sitting.location = (sx, sy + 0.004, sz + 0.002)
        sitting.rotation_euler = (0, 0, 0)
    mf = ctx["mf"]
    pale = "#d9d4c8"
    _set_color(mf["hair"], "#5b3b27" if st >= 1 else pale, kit)
    _set_color(mf["skin"], "#e2b48a" if st >= 1 else pale, kit)
    _set_color(mf["top"], "#4f6e4b" if st >= 2 else pale, kit)
    _set_color(mf["pants"], "#6b6e72" if st >= 2 else pale, kit)
    for fig, nm in ((standing, "myfig"), (sitting, "myfigs")):
        for sx in (-1, 1):
            ob = bpy.data.objects.get(f"{nm}.eye{sx}")
            if ob is not None:
                ob.hide_render = st < 1 or ob.hide_render
    ctx["brush"].hide_render = st < 3 or standing.hide_render
    ctx["brush2"].hide_render = st < 3 or sitting.hide_render
    # --- R6 sitting: both legs straight out in front
    for who, keys in tl.get("acting", {}).items():
        if _switch_(keys, "sit", t, False):
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (math.radians(-90), 0, 0)
    # --- depth of field: a shot may carry "dof": [f-stop, [x, y, z] the focus point]
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = next((s for s in story["shots"] if s["id"] == shot["id"]), {})
    cam = kit.OBJ["cam"]
    mm = _main_mod()
    if spec.get("dof") and mm is not None and hasattr(mm, "cam_at"):
        loc, tgt, lens, roll = mm.cam_at(spec, shot, t, {}, tl)
        fp = spec["dof"][1]
        cam.data.dof.use_dof = True
        cam.data.dof.aperture_fstop = spec["dof"][0]
        cam.data.dof.focus_distance = max(0.01, (V(fp) - V(loc)).length)
    else:
        cam.data.dof.use_dof = False
    return over


def _switch_(keys, attr, t, default):
    v = default
    for k in keys:
        if attr in k and k["t"] <= t + 1e-9:
            v = k[attr]
    return v
