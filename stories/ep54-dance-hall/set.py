"""Ep54 "dance hall": the old upstairs dance hall above a row of shops, plus the sunny opener's street, a bus and the stair.
Built from kit.py's parts; nothing here is shared with another story's set. There is no text anywhere in the set.

Places (metres). THE HALL is at the origin: the floor is x -4 .. 4, y -8 .. 8, the ceiling 5.0 m. The worn ring is round
the middle. Ros's partner's spot P is (0, 0.6): Ros stands at (0, -0.6) facing +y in the demonstration, her partner at P.
The record player stands on its table at the north wall (0, 7.3). The chandelier hangs over the middle (0, 0), the
brass ring at 2.95 m and the lowest drops at 2.4 m.
THE STREET is at x = -80 (bus stop at -80, the long table at -64, the garden gate at -52, the neighbours' gate at -40,
shopfronts along y = +7). THE BUS is a closed box at x = -140. THE STAIR is at x = +40: it climbs along +y from the street
door at y = -1 (z = 0) to the landing at y = 7 .. 9 (z = 3.4).

THE STILTED (the creature). One model, built once, posed by the "keeper" cues: where it stands, its yaw, the hip bend
(degrees), arms raised forward and out. From the waist up an ordinary dancer, burgundy tailcoat with gold, a plain polite
face; from the waist down legs 2.4 m long. It carries no glyph. It is never seen moving: every change is across a cut.

Cues read here: hall (chandelier, wall lamps; ramped), sway, spin, skip, shoes, scuffs, parted, keeper, gloves, glovelid,
coat, ros_mark, me_mark, whole, tally, curtains, door.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector as V

from blocky import faces, rig

S = 0.34
GOLD = "#ffcf66"
BURG = "#6e1a2c"
KEEP_LEG = 2.4
PX, PY = 0.0, 0.6            # Ros's partner's spot
CEIL = 5.0
HALL_LAMPS = [(-3.85, -4.2), (-3.85, 4.2), (3.85, -4.2), (3.85, 4.2)]
STREET_X = -80.0
import os
_DEBUG = bool(os.environ.get('EP54_DEBUG'))


# ------------------------------------------------------------------------------------------------ helpers
def _cues(tl, name):
    return sorted((c for c in tl.get("cues", []) if c["name"] == name), key=lambda c: c["t"])


def _last(cs, t):
    out = None
    for c in cs:
        if c["t"] <= t + 1e-9:
            out = c
    return out


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _ramped(cs, key, t, default):
    """The value of `key` over time: each cue moves it to its target over its own `dur` seconds (smoothstep)."""
    prev = default
    for c in cs:
        if key not in c:
            continue
        if c["t"] > t + 1e-9:
            break
        dur = float(c.get("dur", 0.0))
        u = 1.0 if dur <= 0 else _ss((t - c["t"]) / dur)
        if u < 1.0:
            return prev + (c[key] - prev) * u
        prev = c[key]
    return prev


def _show(objs, on):
    for o in objs:
        for q in _all(o):
            q.hide_render = not on
            q.hide_viewport = not on


def _all(ob):
    return [ob] + list(ob.children_recursive)


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def B(kit, name, size, loc, mat, parent=None, rot=(0, 0, 0), bevel=0.0):
    return kit.box(name, size, loc, mat, parent, rot=rot, bevel=bevel)


def rod(kit, name, p0, p1, r, mat, parent=None, n=6):
    a, b = V(p0), V(p1)
    d = b - a
    ob = kit.cyl(name, r, d.length, tuple((a + b) / 2), mat, parent, n=n)
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return ob


def light_only(kit, coll, light_name, objs):
    col = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = "INCLUDE"
    kit.LIGHTS[light_name]["obj"].light_linking.receiver_collection = col


# ------------------------------------------------------------------------------------------------ the glyphs
def _glyph_images(workdir: Path):
    """Our own half-glyphs: each shape is drawn once and cut down the middle; the halves fit like two pieces of a coin."""
    from PIL import Image, ImageDraw
    workdir.mkdir(parents=True, exist_ok=True)
    W = 512
    gold = (255, 207, 102, 255)
    out = {}
    for k in range(6):
        im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c = W // 2
        if k == 0:    # a ring with a three-toothed comb inside
            d.ellipse([c - 200, c - 200, c + 200, c + 200], outline=gold, width=40)
            d.rectangle([c - 112, c + 40, c + 112, c + 84], fill=gold)
            for x in (-90, 0, 90):
                d.rectangle([c + x - 22, c - 90, c + x + 22, c + 50], fill=gold)
        elif k == 1:  # a split ring with a notch at the top
            d.arc([c - 200, c - 200, c + 200, c + 200], 25, 335, fill=gold, width=40)
            d.rectangle([c - 20, c - 74, c + 20, c + 74], fill=gold)
            d.polygon([(c - 90, c + 74), (c + 90, c + 74), (c, c + 10)], fill=gold)
        elif k == 2:  # a forked hook
            d.rectangle([c - 20, c - 190, c + 20, c + 90], fill=gold)
            d.arc([c - 110, c - 20, c + 110, c + 200], 0, 180, fill=gold, width=40)
            d.line([(c, c - 190), (c - 120, c - 270 + 100)], fill=gold, width=40)
            d.line([(c, c - 190), (c + 120, c - 270 + 100)], fill=gold, width=40)
        elif k == 3:  # a stepped arc
            for i, r in enumerate((200, 140, 80)):
                d.arc([c - r, c - r, c + r, c + r], 180, 360, fill=gold, width=36)
            d.rectangle([c - 200, c - 8, c + 200, c + 28], fill=gold)
            d.rectangle([c - 20, c - 80, c + 20, c + 190], fill=gold)
        elif k == 4:  # a diamond with a bar
            d.polygon([(c, c - 200), (c + 190, c), (c, c + 200), (c - 190, c)], outline=gold, width=40)
            d.rectangle([c - 20, c - 80, c + 20, c + 80], fill=gold)
        else:         # two stacked waves
            for off in (-70, 70):
                pts = [(c - 190 + 380 * i / 40, c + off + 50 * math.sin(i / 40 * 4 * math.pi)) for i in range(41)]
                d.line(pts, fill=gold, width=38, joint="curve")
        im = im.resize((256, 256), Image.LANCZOS)
        full = workdir / f"glyph{k}.png"
        im.save(full)
        im.crop((0, 0, 128, 256)).save(workdir / f"glyph{k}L.png")
        im.crop((128, 0, 256, 256)).save(workdir / f"glyph{k}R.png")
        out[k] = (full, workdir / f"glyph{k}L.png", workdir / f"glyph{k}R.png")
    return out


def glyph_mat(kit, name, path):
    m = kit._new(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type not in ("OUTPUT_MATERIAL",):
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    img = bpy.data.images.load(str(path))
    img.colorspace_settings.name = "sRGB"
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.extension = "CLIP"
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 0.0
    tint = nt.nodes.new("ShaderNodeMixRGB")
    tint.name = "tint"
    tint.blend_type = "MULTIPLY"
    tint.inputs[0].default_value = 1.0
    tint.inputs[2].default_value = (1, 1, 1, 1)
    nt.links.new(tex.outputs["Color"], tint.inputs[1])
    nt.links.new(tint.outputs[0], em.inputs["Color"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tex.outputs["Alpha"], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m, em


def make_plane(name, w, h, mat):
    verts = [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)]
    from blocky import kit as _k
    ob = _k.mesh_obj(name, verts, [(0, 1, 2, 3)], mat)
    uv = ob.data.uv_layers.new(name="UVMap")
    uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for poly in ob.data.polygons:
        for li, u in zip(poly.loop_indices, uvs):
            uv.data[li].uv = u
    try:
        ob.visible_shadow = False
    except Exception:
        pass
    return ob


# ------------------------------------------------------------------------------------------------ materials
def materials(kit):
    M = {}
    M["floor"] = kit.planks("#c99a5b", "#a97c43", 1.0, "Y")
    M["ring"] = kit.planks("#e2c79a", "#cfae7c", 1.0, "Y", name="ring planks")
    M["plaster"] = kit.grime("#efe0a8", 0.82, 3.0)
    M["cream"] = kit.plastic("#f4ecd6", 0.7)
    M["brass"] = kit.metal("#b8893a", 0.35)
    M["dark"] = kit.plastic("#4a2f1c", 0.55)
    M["ceiling"] = kit.plastic("#8f8260", 0.9)
    M["win"] = kit.emit("#26305a", 1.1, "win")
    M["wood"] = kit.planks("#a8926c", "#8a7656", 1.0, "X", name="wood a")
    M["drop"] = kit.emit("#f6e6c0", 0.4, "drop")
    M["bulb"] = kit.emit("#ffe6b8", 3.0, "bulb")
    M["burg"] = kit.plastic(BURG, 0.5)
    M["gold"] = kit.plastic("#d9a640", 0.35)
    M["black"] = kit.plastic("#0b0b0e", 0.7)
    M["curtain"] = kit.plastic("#cfd2b4", 0.9)
    M["dust"] = kit.plastic("#f4ead0", 0.95)
    M["scuff"] = kit.plastic("#16120e", 0.9)
    M["silver"] = kit.plastic("#c4cad2", 0.3)
    M["sleeve"] = kit.plastic("#e9dcc0", 0.8)
    M["glove"] = kit.plastic("#d6d2c6", 0.9)
    M["plum"] = kit.plastic("#5a2748", 0.85)
    M["boot"] = kit.plastic("#5b3a22", 0.7)
    M["white"] = kit.plastic("#f3efe4", 0.7)
    M["tan"] = kit.plastic("#d8a67c", 0.5)
    # the street
    M["pave"] = kit.concrete("#bdb7ac", 2.0, 0.25)
    M["road"] = kit.concrete("#4b4e55", 2.5, 0.25)
    M["mint"] = kit.plastic("#9fd8c0", 0.8)
    M["coral"] = kit.plastic("#f08a78", 0.8)
    M["butter"] = kit.plastic("#f6dc7a", 0.8)
    M["lilac"] = kit.plastic("#bfa8e0", 0.8)
    M["shopwin"] = kit.plastic("#3a5878", 0.2)
    M["shelterback"] = kit.plastic("#f3e3a0", 0.8)
    M["grass"] = kit.plastic("#7fb35a", 0.9)
    M["fence"] = kit.plastic("#f4f0e6", 0.8)
    M["leaf"] = kit.plastic("#4f9a4a", 0.9)
    M["disc"] = kit.plastic("#2f8a8a", 0.5)
    M["post"] = kit.plastic("#5a5f68", 0.5)
    M["busbody"] = kit.plastic("#d8d4c8", 0.7)
    M["busfloor"] = kit.plastic("#6a6258", 0.8)
    M["seat"] = kit.plastic("#c8604c", 0.8)
    M["skywin"] = kit.emit("#bfe0f5", 1.6, "skywin")
    M["stair"] = kit.planks("#7a5230", "#5a3a20", 1.0, "X", name="stair planks")
    M["stairwall"] = kit.grime("#c9b98c", 0.7, 3.0, name="stairwall")
    M["streetlight"] = kit.emit("#d9e6f0", 2.5, "streetlight")
    return M


# ------------------------------------------------------------------------------------------------ the hall
def arch_window(kit, M, x, y, face):
    """A tall arched window of indigo night: `face` is +1 on the west wall (looking +x) or -1 on the east wall."""
    xx = x
    B(kit, f"win {x},{y}", (0.06, 1.1, 2.4), (xx, y, 2.3), M["win"])
    sph = kit.cyl(f"winarch {x},{y}", 0.55, 0.06, (xx, y, 3.5), M["win"], n=24)
    sph.rotation_euler = (0, math.pi / 2, 0)
    B(kit, f"winf {x},{y}", (0.08, 1.3, 0.1), (xx - face * 0.01, y, 1.1), M["cream"])
    for dy in (-0.6, 0.6):
        B(kit, f"winf {x},{y},{dy}", (0.08, 0.1, 2.6), (xx - face * 0.01, y + dy, 2.3), M["cream"])
    B(kit, f"winmull {x},{y}", (0.08, 0.06, 2.4), (xx - face * 0.01, y, 2.3), M["cream"])
    B(kit, f"winmull2 {x},{y}", (0.08, 1.1, 0.06), (xx - face * 0.01, y, 2.5), M["cream"])
    # curtains each side, hanging dead still
    for dy in (-0.85, 0.85):
        B(kit, f"curt {x},{y},{dy}", (0.12, 0.3, 3.0), (xx - face * 0.1, y + dy, 2.1), M["curtain"], bevel=0.04)


def chair(kit, M, x, y, yaw):
    g = kit.empty(f"chair {x},{y}", (x, y, 0), rot=(0, 0, math.radians(yaw)))
    kit.cyl("seat", 0.22, 0.05, (0, 0, 0.46), M["dark"], g, n=16)
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        kit.cyl("leg", 0.018, 0.46, (sx * 0.17, sy * 0.17, 0.23), M["dark"], g, n=6)
    B(kit, "back", (0.34, 0.03, 0.4), (0, 0.2, 0.72), M["dark"], g, bevel=0.01)
    kit.cyl("backrod", 0.016, 0.28, (-0.14, 0.2, 0.62), M["dark"], g, n=6)
    kit.cyl("backrod", 0.016, 0.28, (0.14, 0.2, 0.62), M["dark"], g, n=6)
    return g


def build_hall(kit, M, ctx):
    # floor, worn ring, ceiling, walls
    B(kit, "floor", (8.0, 16.0, 0.1), (0, 0, -0.05), M["floor"])
    ring = kit.cyl("worn ring", 2.9, 0.012, (0, 0, 0.004), M["ring"], n=64)
    B(kit, "ceiling", (8.4, 16.4, 0.2), (0, 0, CEIL + 0.1), M["ceiling"])
    B(kit, "wall W", (0.2, 16.4, CEIL), (-4.1, 0, CEIL / 2), M["plaster"])
    B(kit, "wall E", (0.2, 16.4, CEIL), (4.1, 0, CEIL / 2), M["plaster"])
    B(kit, "wall N", (8.4, 0.2, CEIL), (0, 8.1, CEIL / 2), M["plaster"])
    B(kit, "wall S", (8.4, 0.2, CEIL), (0, -8.1, CEIL / 2), M["plaster"])
    B(kit, "skirt W", (0.08, 16.0, 0.22), (-3.96, 0, 0.11), M["cream"])
    B(kit, "skirt E", (0.08, 16.0, 0.22), (3.96, 0, 0.11), M["cream"])
    B(kit, "cornice W", (0.16, 16.0, 0.2), (-3.96, 0, CEIL - 0.1), M["cream"])
    B(kit, "cornice E", (0.16, 16.0, 0.2), (3.96, 0, CEIL - 0.1), M["cream"])
    for y in (-6.0, -2.0, 2.0, 6.0):
        B(kit, f"pilaster W{y}", (0.14, 0.4, CEIL - 0.2), (-3.93, y, CEIL / 2), M["cream"], bevel=0.02)
        B(kit, f"pilaster E{y}", (0.14, 0.4, CEIL - 0.2), (3.93, y, CEIL / 2), M["cream"], bevel=0.02)
    for y in (-4.0, 0.0, 4.0):
        arch_window(kit, M, 3.96, y, -1)
        arch_window(kit, M, -3.96, y, 1)
    # a door frame to the stair, in the south wall
    B(kit, "door S", (1.2, 0.1, 2.3), (-2.5, -7.98, 1.15), M["dark"])
    B(kit, "doorframe a", (0.12, 0.14, 2.45), (-3.15, -7.97, 1.22), M["cream"])
    B(kit, "doorframe b", (0.12, 0.14, 2.45), (-1.85, -7.97, 1.22), M["cream"])
    B(kit, "doorframe c", (1.4, 0.14, 0.12), (-2.5, -7.97, 2.45), M["cream"])
    # chairs along the long walls
    for i, y in enumerate((-6.2, -4.8, -3.4, -2.0, -0.6, 0.8, 2.2, 3.6, 5.0)):
        chair(kit, M, -3.55, y, -90)
        chair(kit, M, 3.55, y, 90)
    # wall lamps (the sconces are brass blocks; the lights are named for animate)
    for i, (x, y) in enumerate(HALL_LAMPS):
        B(kit, f"sconce {i}", (0.12, 0.16, 0.3), (x + (0.06 if x < 0 else -0.06), y, 2.4), M["brass"], bevel=0.03)
        kit.sphere(f"sconce bulb {i}", 0.07, (x + (0.18 if x < 0 else -0.18), y, 2.55), kit.emit("#ffe6b8", 3.0), seg=8)
        kit.light(f"lamp{i}", "POINT", (x + (0.5 if x < 0 else -0.5), y, 2.5), 90.0, "#ffd9a0", size=0.2)
    # the record player on its table at the north wall
    T = (0, 7.3)
    B(kit, "table", (1.9, 0.8, 0.06), (T[0], T[1], 0.82), M["wood"], bevel=0.02)
    for sx in (-0.85, 0.85):
        for sy in (-0.33, 0.33):
            B(kit, "tleg", (0.06, 0.06, 0.8), (T[0] + sx, T[1] + sy, 0.4), M["dark"])
    B(kit, "case", (0.74, 0.54, 0.16), (T[0] - 0.15, T[1], 0.93), M["wood"], bevel=0.02)
    B(kit, "case top", (0.7, 0.5, 0.02), (T[0] - 0.15, T[1], 1.02), M["dark"])
    disc = kit.cyl("turntable", 0.2, 0.012, (T[0] - 0.25, T[1], 1.035), M["black"], n=40)
    lab = kit.cyl("record label", 0.07, 0.014, (0, 0.0, 0.0), M["gold"], disc, n=20)
    lab.location = (0.0, 0.0, 0.002)
    B(kit, "rec ring", (0.1, 0.012, 0.016), (0.1, 0.0, 0.0), M["gold"], disc)
    ctx["disc"] = disc
    arm = kit.empty("tonearm", (T[0] - 0.4, T[1] + 0.2, 1.06))
    rod(kit, "arm rod", (0, 0, 0), (0.33, -0.16, 0.0), 0.007, M["brass"], arm)
    B(kit, "arm head", (0.05, 0.03, 0.02), (0.35, -0.17, 0.0), M["brass"], arm)
    ctx["tonearm"] = arm
    # the lid, lying beside the player, with its brass corners (and the two burgundy tally strokes)
    lid = kit.empty("lid", (T[0] + 0.55, T[1], 0.855))
    B(kit, "lid board", (0.62, 0.46, 0.05), (0, 0, 0.025), M["wood"], lid, bevel=0.015)
    for sx in (-1, 1):
        for sy in (-1, 1):
            B(kit, "lid corner", (0.09, 0.09, 0.056), (sx * 0.28, sy * 0.2, 0.026), M["brass"], lid, bevel=0.01)
    tally = [B(kit, f"tally {i}", (0.012, 0.045, 0.004), (0.255 + i * 0.03, -0.205, 0.057), M["burg"], lid) for i in (0, 1)]
    ctx["tally"] = tally
    ctx["lid"] = lid
    kit.light("lidlight", "POINT", (T[0] + 0.9, T[1] - 0.8, 1.4), 70.0, "#fff0d0", size=0.3)
    gl = [B(kit, f"lid glove {i}", (0.2, 0.09, 0.03), (-0.12 + i * 0.1, 0.02 - i * 0.04, 0.065), M["glove"], lid, rot=(0, 0, 0.4 - i * 0.7), bevel=0.012) for i in (0, 1)]
    ctx["lidgloves"] = gl
    # the crate of plain-sleeved records
    B(kit, "crate", (0.4, 0.5, 0.3), (T[0] - 0.85, T[1], 1.0), M["wood"], bevel=0.015)
    for i in range(8):
        B(kit, f"sleeve {i}", (0.02, 0.4, 0.28), (T[0] - 1.0 + i * 0.04, T[1], 1.06), M["sleeve"])
    # the chandelier: three chains, a brass ring, bulbs and a ring of glass drops, all hung from one pivot
    chan = kit.empty("chandelier", (0, 0, CEIL))
    R, zr = 0.9, -2.05
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.5
        rod(kit, f"chain {k}", (R * math.cos(a), R * math.sin(a), zr), (0, 0, -0.05), 0.012, M["brass"], chan)
    n = 20
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        rod(kit, f"ringseg {k}", (R * math.cos(a0), R * math.sin(a0), zr), (R * math.cos(a1), R * math.sin(a1), zr), 0.032, M["brass"], chan)
    for k in range(8):
        a = 2 * math.pi * k / 8
        kit.sphere(f"cbulb {k}", 0.07, (0.62 * math.cos(a), 0.62 * math.sin(a), zr + 0.16), M["bulb"], chan, seg=8)
        rod(kit, f"carm {k}", (0.9 * math.cos(a), 0.9 * math.sin(a), zr), (0.62 * math.cos(a), 0.62 * math.sin(a), zr + 0.1), 0.012, M["brass"], chan)
    drops = []
    for k in range(32):
        a = 2 * math.pi * k / 32
        for rr, ln in ((0.86, 0.5), (0.7, 0.36), (0.5, 0.28), (0.3, 0.22)):
            if k % 2 and rr in (0.86, 0.3):
                continue
            if k % 4 and rr == 0.5:
                continue
            d = B(kit, f"drop {k},{rr}", (0.03, 0.03, ln), (rr * math.cos(a), rr * math.sin(a), zr - ln / 2 - 0.03), M["drop"], chan, bevel=0.012)
            drops.append((d, rr, a, zr - ln / 2 - 0.03))
    ctx["drops"] = drops
    gap = B(kit, "dark gap", (0.62, 0.4, 1.5), (0, PY - 0.1, zr - 0.15), M["black"], chan)
    ctx["gap"] = gap
    ctx["chan"] = chan
    kit.light("chan", "POINT", (0, 0, -1.7), 360.0, "#ffe2b0", size=0.35, parent=chan)
    kit.light("hallfill", "POINT", (0, -5.5, 4.2), 230.0, "#ffe6c0", size=0.6)
    kit.light("hallfill2", "POINT", (0, 5.0, 4.2), 150.0, "#ffe6c0", size=0.6)
    # the scuffs in the rosin dust, one set per week (the last pair either side of the spot)
    sets = {
        "a": [(-2.4, -6.7), (-1.1, -6.2)],
        "b": [(-2.2, -3.0), (-0.9, -3.3)],
        "c": [(-1.6, -0.8), (0.0, -1.2)],
        "d": [(-0.45, PY + 0.05), (0.45, PY - 0.05)],
    }
    ctx["scuffs"] = {}
    for key, pts in sets.items():
        objs = []
        cx = sum(p[0] for p in pts) / 2
        cy = sum(p[1] for p in pts) / 2
        dust = B(kit, f"dust {key}", (3.2, 1.8, 0.004), (cx, cy, 0.006), M["dust"])
        objs.append(dust)
        for i, (x, y) in enumerate(pts):
            sc = B(kit, f"scuff {key}{i}", (0.1, 0.34, 0.006), (x, y, 0.011), M["scuff"], rot=(0, 0, 0.1 + 0.2 * i))
            objs.append(sc)
            for j in (-1, 1):
                objs.append(B(kit, f"scuffb {key}{i}{j}", (0.06, 0.22, 0.006), (x + j * 0.11, y - 0.05, 0.011), M["scuff"], rot=(0, 0, 0.3 * j)))
        ctx["scuffs"][key] = objs
    # Ros's silver dance shoes, left standing in the middle with their toes toward the spot
    shoes = []
    for sx in (-1, 1):
        sh = kit.empty(f"rshoe {sx}", (sx * 0.1, -0.55, 0))
        B(kit, "sole", (0.1, 0.27, 0.025), (0, 0, 0.0125), M["dark"], sh, bevel=0.01)
        B(kit, "upper", (0.095, 0.24, 0.06), (0, 0.01, 0.055), M["silver"], sh, bevel=0.025)
        B(kit, "heel", (0.05, 0.05, 0.04), (0, -0.1, 0.025), M["silver"], sh)
        shoes.append(sh)
    ctx["shoes"] = shoes
    shade = kit.plastic("#3a2a18", 0.95)
    ctx["ladder"] = [B(kit, f"ladder {i}", (0.13, 4.2, 0.004), (sx * 0.5, -2.7, 0.009), shade) for i, sx in enumerate((-1, 1))]


def build_stair(kit, M, ctx):
    X = 40.0
    n = 14
    for i in range(n):
        B(kit, f"step {i}", (1.5, 0.5, 0.243 * (i + 1)), (X, 0.25 + i * 0.5, 0.243 * (i + 1) / 2), M["stair"])
    B(kit, "landing", (1.5, 2.6, 3.4), (X, 8.2, 1.7), M["stair"])
    B(kit, "stair wall W", (0.2, 14.0, 6.6), (X - 0.85, 5.5, 3.3), M["stairwall"])
    B(kit, "stair wall E", (0.2, 14.0, 6.6), (X + 0.85, 5.5, 3.3), M["stairwall"])
    B(kit, "stair ceil", (1.9, 14.0, 0.2), (X, 5.5, 6.7), M["stairwall"])
    B(kit, "stair back", (1.9, 0.2, 6.6), (X, 12.5, 3.3), M["stairwall"])
    # the street door at the foot, a slice of street light behind it, a doorway at the top onto the hall
    B(kit, "street door", (1.2, 0.1, 2.3), (X, -1.0, 1.15), M["dark"])
    B(kit, "door slice", (0.14, 0.04, 2.1), (X - 0.4, -1.06, 1.15), M["streetlight"])
    B(kit, "stair frame", (1.5, 0.12, 0.2), (X, 9.4, 6.1), M["cream"])
    kit.light("stairlamp", "POINT", (X + 0.6, 2.5, 3.6), 50.0, "#ffd9a0", size=0.2)
    kit.light("landlamp", "POINT", (X + 0.4, 7.4, 5.2), 60.0, "#ffd9a0", size=0.2)
    kit.light("stairfront", "POINT", (X, 10.2, 5.6), 160.0, "#ffe2b8", size=0.3)
    kit.light("stairlow", "POINT", (X, 0.6, 1.6), 40.0, "#ffe6c0", size=0.2)
    B(kit, "lamp sc", (0.1, 0.2, 0.3), (X + 0.72, 2.5, 3.5), M["brass"], bevel=0.03)


# ------------------------------------------------------------------------------------------------ the street
def build_street(kit, M, ctx):
    X0 = STREET_X
    B(kit, "pave", (140.0, 9.0, 0.2), (X0 + 10, 2.5, -0.1), M["pave"])
    B(kit, "road", (140.0, 14.0, 0.2), (X0 + 10, -9.0, -0.12), M["road"])
    B(kit, "kerb", (140.0, 0.25, 0.18), (X0 + 10, -1.9, -0.02), M["cream"])
    B(kit, "lawn", (140.0, 30.0, 0.2), (X0 + 10, 22.0, -0.11), M["grass"])
    cols = ["mint", "coral", "butter", "lilac", "mint", "coral", "butter", "lilac"]
    for i, c in enumerate(cols):
        x = X0 - 16 + i * 6.0
        B(kit, f"shop {i}", (5.8, 5.0, 5.0 + (i % 3) * 0.5), (x, 9.5, 2.6), M[c])
        B(kit, f"shopdoor {i}", (1.1, 0.1, 2.2), (x + 1.2, 6.97, 1.1), M["cream"])
        B(kit, f"shopwin {i}", (2.2, 0.1, 1.5), (x - 1.0, 6.97, 1.6), M["shopwin"])
        B(kit, f"signboard {i}", (4.2, 0.12, 0.7), (x, 6.95, 3.4), M["cream"])   # blank signboard
        B(kit, f"awning {i}", (4.4, 0.9, 0.08), (x, 6.55, 2.7), M["coral" if i % 2 else "mint"], rot=(0.3, 0, 0))
    # the bus stop: a shelter and a post with a coloured disc
    sx = X0
    B(kit, "shelter roof", (3.2, 1.3, 0.08), (sx, 0.4, 2.5), M["mint"])
    B(kit, "shelter back", (3.2, 0.05, 2.3), (sx, 1.0, 1.3), M["shelterback"])
    for dx in (-1.55, 1.55):
        B(kit, "shelter post", (0.07, 0.07, 2.5), (sx + dx, 0.0, 1.25), M["post"])
    B(kit, "bench", (1.8, 0.4, 0.06), (sx, 0.65, 0.5), M["wood"])
    B(kit, "busstop post", (0.08, 0.08, 3.0), (sx + 3.0, -0.8, 1.5), M["post"])
    d = kit.cyl("busstop disc", 0.3, 0.05, (sx + 3.0, -0.84, 2.9), M["disc"], n=24)
    d.rotation_euler = (math.pi / 2, 0, 0)
    # the long table, then two gates and hedges
    B(kit, "long table", (4.4, 0.8, 0.06), (X0 + 16, 2.6, 0.92), M["wood"])
    for dx in (-2.0, 2.0):
        for dy in (-0.3, 0.3):
            B(kit, "tbl leg", (0.07, 0.07, 0.9), (X0 + 16 + dx, 2.6 + dy, 0.45), M["dark"])
    for gx in (X0 + 28, X0 + 40):
        B(kit, "fence L", (4.4, 0.06, 0.9), (gx - 2.8, 3.6, 0.45), M["fence"])
        B(kit, "fence R", (4.4, 0.06, 0.9), (gx + 2.8, 3.6, 0.45), M["fence"])
        B(kit, "gate post a", (0.12, 0.12, 1.2), (gx - 0.65, 3.6, 0.6), M["fence"])
        B(kit, "gate post b", (0.12, 0.12, 1.2), (gx + 0.65, 3.6, 0.6), M["fence"])
        B(kit, "house", (7.0, 5.0, 4.0), (gx, 10.0, 2.0), M["butter" if gx == X0 + 28 else "mint"])
        B(kit, "housedoor", (1.0, 0.1, 2.0), (gx, 7.45, 1.0), M["coral"])
        B(kit, "hedge a", (2.4, 0.9, 1.0), (gx - 3.0, 5.2, 0.5), M["leaf"], bevel=0.15)
        B(kit, "hedge b", (2.4, 0.9, 1.0), (gx + 3.0, 5.2, 0.5), M["leaf"], bevel=0.15)
    for i, tx in enumerate((-8, 6, 20, 34, 48)):
        kit.cyl(f"trunk {i}", 0.16, 2.2, (X0 + tx, 5.6, 1.1), M["dark"], n=8)
        kit.sphere(f"crown {i}", 1.4, (X0 + tx, 5.6, 3.2), M["leaf"], seg=10)
    sun = kit.light("sun", "SUN", (-6, -14, 13), 9.0, "#fff4dc", size=0.02)
    kit.aim(sun, (X0, 0, 0))
    ctx["sun"] = sun
    # an even fill on the two brothers at the gate so neither face sits in shadow
    kit.light("gatefill", "POINT", (X0 + 26.8, 1.0, 1.9), 600.0, "#fff4e4", size=0.8)


def build_bus(kit, M, ctx):
    X = -140.0
    B(kit, "bus floor", (2.6, 10.0, 0.1), (X, 0, -0.05), M["busfloor"])
    B(kit, "bus roof", (2.6, 10.0, 0.1), (X, 0, 2.5), M["busbody"])
    for sx in (-1, 1):
        B(kit, "bus wall low", (0.1, 10.0, 0.9), (X + sx * 1.3, 0, 0.45), M["busbody"])
        B(kit, "bus wall high", (0.1, 10.0, 0.25), (X + sx * 1.3, 0, 2.38), M["busbody"])
        B(kit, "bus window", (0.06, 10.0, 1.3), (X + sx * 1.33, 0, 1.5), M["skywin"])
        B(kit, "bus seat", (0.45, 7.0, 0.5), (X + sx * 1.0, 0, 0.5), M["seat"], bevel=0.04)
    B(kit, "bus front", (2.6, 0.1, 2.5), (X, 5.0, 1.25), M["busbody"])
    B(kit, "bus back", (2.6, 0.1, 2.5), (X, -5.0, 1.25), M["busbody"])
    kit.cyl("bus pole", 0.025, 2.5, (X, 0.3, 1.25), M["post"], n=8)
    rod(kit, "bus rail", (X - 0.9, -3, 2.3), (X - 0.9, 3, 2.3), 0.02, M["post"])
    rod(kit, "bus rail2", (X + 0.9, -3, 2.3), (X + 0.9, 3, 2.3), 0.02, M["post"])
    for i, y in enumerate((-2.5, 0.0, 2.5)):
        kit.light(f"busl{i}", "POINT", (X, y, 2.2), 160.0, "#fff0d0", size=0.3)


# ------------------------------------------------------------------------------------------------ the Stilted
def build_keeper(kit, M, ctx):
    root = kit.empty("keeper", (0, 0, -30))
    skin = kit.plastic("#d9a883", 0.5)
    LL = math.hypot(KEEP_LEG, 0.95)
    ang = math.atan2(0.95, KEEP_LEG)
    for sx in (-1, 1):
        lg = kit.empty(f"keeper.legp{sx}", (sx * 0.35, 0, KEEP_LEG), root, rot=(0, sx * ang, 0))
        B(kit, f"keeper.leg{sx}", (0.3, 0.3, LL - 0.05), (0, 0, -LL / 2 + 0.0), M["burg"], lg, bevel=0.03)
        B(kit, f"keeper.gstripe{sx}", (0.03, 0.31, LL - 0.1), (sx * 0.16, 0, -LL / 2), M["gold"], lg)
        B(kit, f"keeper.shoe{sx}", (0.32, 0.5, 0.1), (0, -0.08, -LL + 0.03), M["black"], lg, rot=(0, -sx * ang, 0), bevel=0.03)
    hips = kit.empty("keeper.hips", (0, 0, KEEP_LEG), root)
    torso = kit.empty("keeper.torso", (0, 0, 0), hips)
    B(kit, "keeper.torsom", (0.7, 0.36, 0.7), (0, 0, 0.35), M["burg"], torso, bevel=0.03)
    B(kit, "keeper.shirt", (0.26, 0.02, 0.5), (0, -0.19, 0.4), M["white"], torso)
    for i in range(3):
        kit.sphere(f"keeper.btn{i}", 0.022, (0, -0.2, 0.18 + i * 0.14), M["gold"], torso, seg=6)
    B(kit, "keeper.pipeL", (0.03, 0.375, 0.7), (-0.2, 0, 0.35), M["gold"], torso)
    B(kit, "keeper.pipeR", (0.03, 0.375, 0.7), (0.2, 0, 0.35), M["gold"], torso)
    B(kit, "keeper.tails", (0.5, 0.1, 0.55), (0, 0.22, -0.12), M["burg"], torso, bevel=0.03)
    B(kit, "keeper.collar", (0.3, 0.38, 0.06), (0, 0, 0.72), M["white"], torso)
    arms = []
    for sx in (-1, 1):
        arm = kit.empty(f"keeper.arm{sx}", (sx * 0.5, 0, 0.62), torso)
        B(kit, f"keeper.sleeve{sx}", (0.32, 0.32, 0.5), (0, 0, -0.25 + 0.03), M["burg"], arm, bevel=0.03)
        B(kit, f"keeper.cuff{sx}", (0.335, 0.335, 0.05), (0, 0, -0.5), M["gold"], arm)
        B(kit, f"keeper.hand{sx}", (0.28, 0.2, 0.22), (0, 0, -0.62), skin, arm, bevel=0.04)
        arms.append(arm)
    ctx["k_arms"] = arms
    # the head: the rig's own rounded cylinder with a drawn face, a combed black block of hair
    headc = kit.empty("keeper.headc", (0, 0, 0.74 + (faces.HEAD_H / 2 + 0.02) * S), torso)
    hg = kit.empty("keeper.hg", (0, 0, 0), headc)
    hg.scale = (S, S, S)
    mat, tex = rig.head_material("keeper", "#d9a883")
    rig.head_mesh("keeper.headm", mat, hg)
    hair = kit.plastic("#101014", 0.5)
    R, H = faces.HEAD_R, faces.HEAD_H
    top = H / 2
    B(kit, "keeper.hcap", (2 * R + 0.08, 2 * R + 0.08, 0.3), (0, 0.02, top - 0.05), hair, hg, bevel=0.12)
    B(kit, "keeper.hback", (2 * R + 0.08, 0.32, H * 0.75), (0, R - 0.08, top - H * 0.36), hair, hg, bevel=0.1)
    for sx in (-1, 1):
        B(kit, f"keeper.hside{sx}", (0.2, 0.9, 0.5), (sx * (R - 0.02), 0.2, top - 0.25), hair, hg, bevel=0.08)
    B(kit, "keeper.part", (0.05, 0.5, 0.05), (0.22, -R + 0.2, top + 0.14), kit.plastic("#2a2a30", 0.5), hg)
    face = {"eyes": "round", "brows": True, "ink": "#16100c"}
    pil = faces.face_image(face, "#d9a883", "smirk", 0.0, (0, 0), 0.0)
    path = Path(tempfile.gettempdir()) / "ep54-keeper-face.png"
    pil.save(path)
    img = bpy.data.images.load(str(path))
    img.colorspace_settings.name = "sRGB"
    tex.image = img
    ctx["k_root"], ctx["k_hips"], ctx["k_torso"], ctx["k_headc"] = root, hips, torso, headc
    ctx["k_objs"] = _all(root)
    # its own key (warm, above and to the side) and a cool rim from the windows: they light the Stilted and nothing else
    kit.light("kkey", "POINT", (2.2, 1.2, 4.4), 180.0, "#ffc890", size=0.5)
    kit.light("krim", "POINT", (-3.4, 2.2, 3.4), 260.0, "#9fb8ff", size=0.5)
    kit.light("kfront", "POINT", (0.9, -1.3, 1.9), 140.0, "#ffd8a8", size=0.3)
    for ln in ("kkey", "krim", "kfront"):
        light_only(kit, "keeper", ln, ctx["k_objs"])
    # face lights: a high one for the upright pose (its face is above the brass ring), a low one at eye height for the bend
    # (it lights Ros's face too). Each switches only on a cut, with the keeper's pose.
    kit.light("kface_hi", "POINT", (-1.0, -1.9, 3.5), 130.0, "#ffd9b0", size=0.4)
    light_only(kit, "keeper", "kface_hi", ctx["k_objs"])
    kit.light("kface_lo", "POINT", (1.5, -0.9, 2.1), 60.0, "#ffd9b0", size=0.4)
    kit.light("khand", "POINT", (-1.1, -1.3, 1.9), 150.0, "#ffd9b0", size=0.4)
    _show(ctx["k_objs"], False)


def pose_keeper(ctx, c):
    hidden = c is None or c.get("hidden", False)
    _show(ctx["k_objs"], not hidden)
    if hidden:
        return
    root = ctx["k_root"]
    root.location = (c["pos"][0], c["pos"][1], 0)
    root.rotation_euler = (0, 0, math.radians(c.get("yaw", 180)))
    bend = math.radians(c.get("bend", 0))
    ctx["k_torso"].rotation_euler = (bend, 0, 0)
    ctx["k_headc"].rotation_euler = (-bend + math.radians(c.get("tilt", 0)), 0, math.radians(c.get("hyaw", 0)))
    raise_ = c.get("arms", [0, 0])
    side = c.get("side", [0, 0])
    for i, arm in enumerate(ctx["k_arms"]):   # arm -1 is the first
        sx = -1 if i == 0 else 1
        r = math.radians(raise_[0 if sx == -1 else 1])     # [right (arm -1), left (arm 1)] like the rig
        sd = math.radians(side[0 if sx == -1 else 1])
        arm.rotation_euler = (-r - bend, -sx * sd, 0)


# ------------------------------------------------------------------------------------------------ build
def build(kit, story, tl):
    M = materials(kit)
    ctx = {"M": M, "inited": False}
    build_hall(kit, M, ctx)
    build_stair(kit, M, ctx)
    build_street(kit, M, ctx)
    build_bus(kit, M, ctx)
    build_keeper(kit, M, ctx)
    # glyph planes
    imgs = _glyph_images(Path(tempfile.gettempdir()) / "ep54-glyphs")
    ctx["glyph_imgs"] = imgs
    ctx["marks"] = {}
    ctx["wholes"] = {}
    for who, (k, side, arm) in story.get("marks", {}).items():
        m, em = glyph_mat(kit, f"mark {who}", imgs[k][1 if side == "L" else 2])
        pl = make_plane(f"mark {who}", 0.12, 0.24, m)
        ctx["marks"][who] = (pl, em, arm)
    for pid, (k, a, b) in story.get("pairs", {}).items():
        m, em = glyph_mat(kit, f"whole {pid}", imgs[k][0])
        pl = make_plane(f"whole {pid}", 0.24, 0.24, m)
        ctx["wholes"][pid] = (pl, em, a, b)
    kit.light("glyphglow", "POINT", (0, 0, -20), 0.0, GOLD, size=0.15)
    kit.light("facefill", "POINT", (-1.1, -1.1, 1.9), 55.0, "#ffe6c8", size=0.4)
    kit.light("footlight", "POINT", (0.45, -0.45, 0.3), 90.0, "#fff0d8", size=0.3)
    return ctx


# ------------------------------------------------------------------------------------------------ the cast's extras
def decorate(kit, story, ctx):
    M = ctx["M"]

    def ob(n):
        return bpy.data.objects.get(n)

    # me: a big white pointed collar, the shirt's placket, dark curls, white record gloves
    tor = ob("me.torso")
    if tor:
        for sx in (-1, 1):
            B(kit, f"me.collarw{sx}", (0.9, 0.1, 0.5), (sx * 0.5, -0.55, 1.8), M["white"], tor, rot=(0.25, sx * 0.0, sx * -0.55), bevel=0.02)
        B(kit, "me.placket", (0.44, 0.04, 1.75), (0, -0.52, 1.05), M["white"], tor, bevel=0.01)
    hg = ob("me.headg")
    if hg:
        curl = kit.plastic("#1d1612", 0.7)
        for i in range(7):
            a = 2 * math.pi * i / 7
            kit.sphere(f"me.curl{i}", 0.17, (0.38 * math.cos(a), 0.38 * math.sin(a), faces.HEAD_H / 2 + 0.06), curl, hg, seg=8)
        kit.sphere("me.curlc", 0.2, (0, 0, faces.HEAD_H / 2 + 0.1), curl, hg, seg=8)
    gl = []
    for sx in (-1, 1):
        arm = ob(f"me.arm{sx}")
        if arm:
            gl.append(B(kit, f"me.glove{sx}", (1.05, 1.06, 0.85), (0, 0, -1.33), M["glove"], arm, bevel=0.09))
    ctx["gloves"] = gl
    # Ros: a brooch, a side wave in the bob, and the plum coat and brown boots for the night she goes to the station
    tor = ob("ros.torso")
    if tor:
        B(kit, "ros.brooch", (0.22, 0.05, 0.22), (0.55, -0.52, 1.45), M["gold"], tor, bevel=0.03)
        coat = [B(kit, "ros.coat", (2.14, 1.14, 2.1), (0, 0, 1.0), M["plum"], tor, bevel=0.1)]
        for sx in (-1, 1):
            arm = ob(f"ros.arm{sx}")
            if arm:
                coat.append(B(kit, f"ros.coatsl{sx}", (1.06, 1.08, 1.8), (0, 0, -0.62), M["plum"], arm, bevel=0.08))
            leg = ob(f"ros.leg{sx}")
            if leg:
                coat.append(B(kit, f"ros.skirt{sx}", (1.06, 1.14, 1.3), (0, 0, -0.62), M["plum"], leg, bevel=0.08))
                coat.append(B(kit, f"ros.boot{sx}", (1.04, 1.1, 0.7), (0, 0, -1.55), M["boot"], leg, bevel=0.08))
        ctx["coat"] = coat
    hg = ob("ros.headg")
    if hg:
        sil = kit.plastic("#c6c9cf", 0.5)
        B(kit, "ros.wave", (1.0, 0.5, 0.34), (-0.3, -faces.HEAD_R + 0.22, faces.HEAD_H / 2 - 0.1), sil, hg, rot=(0, 0.3, 0), bevel=0.1)
    for who in ("me", "ros", "pm"):       # extras made after the cast was hidden must start hidden too
        root = ob(who)
        if root is not None and root.hide_render:
            for q in _all(root):
                q.hide_render = True
    ctx["inited"] = True


def _hand_pos(who, arm):
    o = bpy.data.objects.get(f"{who}.{arm}")
    root = bpy.data.objects.get(who)
    if o is None or root is None or root.hide_render:
        return None
    return o.matrix_world @ V((0, 0, -1.5))


def _cam_loc(story, tl, t):
    from blocky import bl_story
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    spec = {s["id"]: s for s in story["shots"]}[shot["id"]]
    loc, _tgt, _lens, _roll = bl_story.cam_at(spec, shot, t, None, tl)
    return V(loc)


def _billboard(pl, p, cam, lift=0.0):
    d = cam - p
    d.z = 0.0 if abs(d.x) + abs(d.y) > 1e-4 else d.z
    yaw = math.atan2(d.y, d.x) - math.pi / 2     # the plane's normal is -y in its own frame
    pl.location = p
    pl.rotation_euler = (0, 0, yaw + math.pi)


# ------------------------------------------------------------------------------------------------ animate
def animate(kit, story, tl, t, ctx):
    bpy.context.view_layer.update()
    if not ctx["inited"]:
        decorate(kit, story, ctx)
    over = {}
    # ---- the hall's lights: every change a slow ramp (hard rule 7)
    hc = _cues(tl, "hall")
    chan = _ramped(hc, "chan", t, 1.0)
    lamps = _ramped(hc, "lamps", t, 1.0)
    over["chan"] = chan
    over["hallfill"] = 0.35 + 0.65 * chan
    over["hallfill2"] = 0.35 + 0.65 * chan
    for i in range(len(HALL_LAMPS)):
        over[f"lamp{i}"] = lamps
    # ---- the sway: the whole chandelier swings a few degrees about its pivot, period about 3 s
    amp = _ramped(_cues(tl, "sway"), "amp", t, 0.0)
    a = math.radians(2.6) * amp
    ctx["chan"].rotation_euler = (a * math.sin(2 * math.pi * t / 3.0), a * 0.6 * math.sin(2 * math.pi * t / 3.0 + 1.1), 0)
    # ---- the drops pushed apart round a dark gap
    pc = _ramped(_cues(tl, "parted"), "v", t, 0.0)
    kc_ = _last(_cues(tl, "keeper"), t)
    kvis = kc_ is not None and not kc_.get("hidden", False)
    kb = kc_.get("bend", 0) if kvis else 0
    over["chan"] = chan * (0.06 if kvis and kb < 100 else 1.0)
    over["kface_hi"] = 1.0 if kvis and kb < 100 else 0.0
    over["kface_lo"] = 1.0 if kvis and kb >= 100 else 0.0
    over["khand"] = 1.0 if kvis and kb >= 100 else 0.0
    _show([ctx["gap"]], pc > 0.01 and (kc_ is None or kc_.get("hidden", False)))
    for d, rr, ang, zc in ctx["drops"]:
        x, y = rr * math.cos(ang), rr * math.sin(ang)
        gapped = pc > 0.5 and (x * x + (y - 0.35) ** 2 < 0.65 ** 2 or (y < 0 and abs(x) < 0.5))
        d.hide_render = bool(gapped)
        d.location = (x, y, zc)
    # ---- the record
    spin = bool((_last(_cues(tl, "spin"), t) or {"on": True}).get("on", True))
    ctx["disc"].rotation_euler = (0, 0, -t * 3.5 if spin else 0.0)
    tone = ctx["tonearm"]
    base = math.radians(-6)
    skip = _last(_cues(tl, "skip"), t)
    jump = 0.0
    if skip is not None and 0 <= t - skip["t"] < 1.2:
        u = t - skip["t"]
        jump = math.radians(7) * math.exp(-5 * u) * math.cos(14 * u) if u < 1.2 else 0.0
    tone.rotation_euler = (0, 0, base + jump + (0.01 * math.sin(t * 3.5) if spin else 0))
    # ---- props
    _show(ctx["shoes"], bool((_last(_cues(tl, "shoes"), t) or {}).get("on")))
    _show(ctx["ladder"], bool((_last(_cues(tl, "ladder"), t) or {}).get("on")))
    sc = (_last(_cues(tl, "scuffs"), t) or {"sets": []})["sets"]
    for key, objs in ctx["scuffs"].items():
        _show(objs, key in sc)
    _show(ctx["tally"], bool((_last(_cues(tl, "tally"), t) or {}).get("on")))
    on_g = (_last(_cues(tl, "gloves"), t) or {"on": True}).get("on", True)
    _show(ctx["gloves"], bool(on_g))
    _show(ctx["lidgloves"], bool((_last(_cues(tl, "glovelid"), t) or {}).get("on")))
    if "coat" in ctx:
        _show(ctx["coat"], bool((_last(_cues(tl, "coat"), t) or {}).get("on")))
    # ---- the Stilted
    pose_keeper(ctx, _last(_cues(tl, "keeper"), t))
    # ---- the glyphs: a plane on each hand that turns to the camera, brightness ramped
    cam = _cam_loc(story, tl, t)
    levels = {}
    for who in ctx["marks"]:
        lv = 1.0
        if who == "ros":
            lv = _ramped(_cues(tl, "ros_mark"), "v", t, 1.0)
        elif who == "me":
            lv = _ramped(_cues(tl, "me_mark"), "v", t, 0.0)
        levels[who] = lv
    glow = 0.0
    glow_p = None
    whole_of = {}
    for pid, (pl, em, a_, b_) in ctx["wholes"].items():
        w = _ramped([c for c in _cues(tl, "whole") if c.get("pair") == pid], "v", t, 0.0)
        whole_of[a_] = whole_of[b_] = w
        pa, pb = _hand_pos(a_, ctx["marks"][a_][2]), _hand_pos(b_, ctx["marks"][b_][2])
        if w > 0.01 and pa is not None and pb is not None:
            pl.hide_render = False
            mid = (pa + pb) / 2
            _billboard(pl, mid + (cam - mid).normalized() * 0.08, cam)
            sz = 1.5 + 0.15 * w
            pl.scale = (sz, 1, sz)
            em.inputs["Strength"].default_value = 7.0 * w * (levels.get("ros", 1.0) if "ros" in (a_, b_) else 1.0)
            if w * (levels.get("ros", 1.0) if "ros" in (a_, b_) else 1.0) > glow:
                glow = w
                glow_p = mid
        else:
            pl.hide_render = True
    for who, (pl, em, arm) in ctx["marks"].items():
        p = _hand_pos(who, arm)
        w = whole_of.get(who, 0.0)
        lv = levels[who]
        if p is None or lv <= 0.01:
            pl.hide_render = True
            continue
        pl.hide_render = False
        gloved = bool(on_g) and who == "me"
        off = 0.3 if gloved else (0.13 if who == "me" else (0.22 if lv < 0.3 else 0.1))
        _billboard(pl, p + (cam - p).normalized() * off, cam)
        sc_ = 1.8 if who == "me" and (lv > 0.5 or gloved) else 1.5
        pl.scale = (sc_, 1, sc_)
        _l52 = tl.get("lines", {}).get("L52")
        _dim = who == "ros" and _l52 is not None and _l52["onset"] - 0.05 <= t <= _l52["end"] + 0.05
        em.id_data.nodes["tint"].inputs[2].default_value = (0.30, 0.13, 0.05, 1) if _dim else (1, 1, 1, 1)
        em.inputs["Strength"].default_value = ((3.2 if not gloved else 4.5) if who == "me" else 6.0) * lv * (1.0 - w) * (0.6 if (who == "ros" and lv < 0.3) else 1.0)
        if who == "me" and lv > 0.5 and (1.0 - w) > 0.5 and glow < 0.2 and not gloved:
            glow = 0.2
            glow_p = p
        if _DEBUG:
            import sys
            print(f"DBG t={t:.2f} {who} hand={tuple(round(x, 2) for x in p)} cam={tuple(round(x, 2) for x in cam)}", file=sys.stderr)
    l68 = tl.get("lines", {}).get("L68")
    over["footlight"] = 1.0 if l68 and l68["onset"] - 0.05 <= t <= l68["end"] else 0.0
    l62 = tl.get("lines", {}).get("L62")
    over["facefill"] = 1.0 if l62 and l62["onset"] - 0.05 <= t <= l62["end"] + 0.05 else 0.0
    over["glyphglow"] = 1.0
    gl = kit.LIGHTS["glyphglow"]
    gl["obj"].location = glow_p + (cam - glow_p).normalized() * 0.25 if glow_p is not None else V((0, 0, -20))
    gl["base"] = 14.0 * glow
    return over
