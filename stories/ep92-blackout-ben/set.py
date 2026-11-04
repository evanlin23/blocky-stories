"""ep92 "blackout ben": a summer-night blackout in one house, our own set built from kit.py's parts.

Everything the story moves is driven by cues in story.json (see animate): the look (sun, moon, fill, sky and the
house lamps, always eased over 0.4 s or more), houses' windows and porch lamps, objects ("obj"), who sits ("sit"),
flashlights ("fl"), the watch ("watch"), the two versions of the living room ("ver"), the clock, the doors and the
check inset (the rule meter, glued to the camera).
"""
import math
import os
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {}
TMP = Path(tempfile.mkdtemp(prefix="ep92-"))
FONT = Path(__file__).resolve().parents[2] / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lin(h):
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(v / 255) for v in hexrgb(h))


def noshadow(ob):
    try:
        ob.visible_shadow = False
    except Exception:
        pass
    for c in ob.children_recursive:
        try:
            c.visible_shadow = False
        except Exception:
            pass


def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


# ---------------------------------------------------------------------------------------------- looks
def _L(**kw):
    base = dict(sun=0.0, sun_col="#fff1d6", el=60.0, az=-15.0, fill=0.0, fill_col="#ffffff", moon=0.0,
                moon_col="#8fb0ff", sky="#9fd0ff", sky_str=1.0, lr=0.0, hall=0.0, br=0.0, wr=0.0, mf=0.0)
    base.update(kw)
    return base


LOOKS = {
    "day": _L(sun=4.2, fill=1.1, sky="#a8d8ff", sky_str=1.1),
    "dusk": _L(sun=2.6, sun_col="#ff9a5a", el=9, az=-60, fill=0.8, fill_col="#ffc9a0", sky="#f7a46a", sky_str=0.9),
    "night": _L(moon=2.0, el=64, az=-12, fill=1.15, fill_col="#7f9cff", sky="#2d5be3", sky_str=0.65, hall=0.4,
                wr=0.0),
    # the montage street: the night look plus a warm shadowless face light from our side of the street, so each
    # neighbour's face and shirt read at phone size
    "street": _L(moon=1.1, el=64, az=-12, fill=1.0, fill_col="#7f9cff", sky="#2d5be3", sky_str=0.7, hall=0.4, mf=2.6),
    # first light, peach through the bedroom window
    "dawn": _L(sun=2.4, sun_col="#ffa070", el=11, az=-55, fill=1.0, fill_col="#ffc8a8", sky="#ffb48c", sky_str=0.9,
               hall=0.4),
    # the hook: cobalt room, the table flashlight does the lighting
    "hook": _L(moon=1.4, el=64, az=-12, fill=1.0, fill_col="#7f9cff", sky="#2d5be3", sky_str=0.55, lr=0.0),
    # lights back on at night: warm lamps inside, blue outside
    "lamp": _L(moon=0.8, el=64, az=-12, fill=0.9, fill_col="#ffdcb0", sky="#3a64d6", sky_str=0.5, lr=1.0, hall=1.0,
               br=1.0),
    "storm": _L(sun=1.6, sun_col="#c9d8f0", el=50, az=-15, fill=1.0, fill_col="#b8c8e8", sky="#7d90b8", sky_str=0.85),
    "split": _L(sun=1.4, fill=0.75, sky="#bcd8ff", sky_str=0.6),
}


def look_at(tl, t):
    cues = [c for c in tl["cues"] if c["name"] == "look"]
    cur = LOOKS[cues[0]["id"]] if cues else LOOKS["day"]
    prev = cur
    for c in cues:
        if c["t"] > t:
            break
        prev = cur
        cur = LOOKS[c["id"]]
        dur = c.get("dur", 0.5)
        dur = 0.0 if dur <= 0 else max(0.4, dur)
        if t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            return _mix(prev, cur, u)
    return _mix(cur, cur, 0.0)


def _mix(a, b, u):
    out = {}
    for k in a:
        if isinstance(a[k], str):
            ca, cb = lin(a[k]), lin(b[k])
            out[k] = tuple(ca[i] + (cb[i] - ca[i]) * u for i in range(3))
        else:
            out[k] = a[k] + (b[k] - a[k]) * u
    return out


def sample(cues, t, fields, defaults):
    cur = dict(defaults)
    prev = dict(defaults)
    for c in cues:
        if c["t"] > t:
            break
        prev = dict(cur)
        for f in fields:
            if f in c:
                cur[f] = c[f]
        dur = c.get("dur", 0.0)
        if dur > 0 and t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            res = {}
            for f in fields:
                a, b = prev[f], cur[f]
                if isinstance(a, (list, tuple)):
                    res[f] = [a[i] + (b[i] - a[i]) * u for i in range(len(a))]
                else:
                    res[f] = a + (b - a) * u
            return res, c
    last = None
    for c in cues:
        if c["t"] <= t:
            last = c
    return cur, last


def _track(tl, name, keyf=lambda c: c.get("id")):
    out = {}
    for c in tl["cues"]:
        if c["name"] == name:
            out.setdefault(keyf(c), []).append(c)
    return out


def last_cue(cues, t):
    last = None
    for c in cues:
        if c["t"] <= t:
            last = c
    return last


# ---------------------------------------------------------------------------------------------- materials
def alpha_mat(kit, name, hexc, mixf, emit=2.0):
    """A soft glowing see-through shape (a flashlight beam)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = kit.col(hexc)
    em.inputs["Strength"].default_value = emit
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = mixf
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def image_mat(kit, name, strength=1.0):
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    gc = nt.nodes.new("ShaderNodeTexCoord")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    nt.links.new(gc.outputs["Generated"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m, tex


# ---------------------------------------------------------------------------------------------- walls
def wall_x(kit, name, y, x0, x1, h, mat, opening=None, th=0.15, z0=0.0, ext=None, ext_side=-1):
    """A wall along x at y, with one optional opening (a0, a1, zb, zt). ext: a material for a thin outer skin."""
    pieces = []
    if opening is None:
        pieces.append((x0, x1, z0, h))
    else:
        a0, a1, zb, zt = opening
        pieces += [(x0, a0, z0, h), (a1, x1, z0, h), (a0, a1, z0, zb), (a0, a1, zt, h)]
    for i, (p0, p1, q0, q1) in enumerate(pieces):
        if p1 - p0 < 0.01 or q1 - q0 < 0.01:
            continue
        kit.box(f"{name}.{i}", (p1 - p0, th, q1 - q0), ((p0 + p1) / 2, y, (q0 + q1) / 2), mat)
        if ext is not None:
            kit.box(f"{name}.x{i}", (p1 - p0, 0.02, q1 - q0), ((p0 + p1) / 2, y + ext_side * (th / 2 + 0.01),
                                                                 (q0 + q1) / 2), ext)


def wall_y(kit, name, x, y0, y1, h, mat, opening=None, th=0.15):
    pieces = []
    if opening is None:
        pieces.append((y0, y1, 0.0, h))
    else:
        a0, a1, zb, zt = opening
        pieces += [(y0, a0, 0.0, h), (a1, y1, 0.0, h), (a0, a1, 0.0, zb), (a0, a1, zt, h)]
    for i, (p0, p1, q0, q1) in enumerate(pieces):
        if p1 - p0 < 0.01 or q1 - q0 < 0.01:
            continue
        kit.box(f"{name}.{i}", (th, p1 - p0, q1 - q0), (x, (p0 + p1) / 2, (q0 + q1) / 2), mat)


# ---------------------------------------------------------------------------------------------- furniture
def couch(kit, name, loc, hexc, width=3.9, parent=None):
    e = kit.empty(name, loc, parent)
    body = kit.plastic(hexc, 0.6, spec=0.2)
    cush = kit.plastic(hexc, 0.7, name=f"cush {hexc}", spec=0.1)
    kit.box(f"{name}.base", (width, 1.0, 0.36), (0, 0, 0.2), body, e, bevel=0.04)
    kit.box(f"{name}.back", (width, 0.28, 0.9), (0, 0.5, 0.65), body, e, bevel=0.05)
    for sx in (-1, 1):
        kit.box(f"{name}.arm{sx}", (0.3, 1.0, 0.62), (sx * (width / 2 - 0.15), 0, 0.5), body, e, bevel=0.05)
    n = 3
    sw = (width - 0.6) / n
    for i in range(n):
        x = -(width - 0.6) / 2 + sw * (i + 0.5)
        kit.box(f"{name}.seat{i}", (sw - 0.04, 0.8, 0.14), (x, -0.04, 0.45), cush, e, bevel=0.04)
        kit.box(f"{name}.bk{i}", (sw - 0.04, 0.2, 0.55), (x, 0.28, 0.82), cush, e, bevel=0.05)
    return e


def person_box(kit, parent, name, x, y, z, skin, shirt, hair, scale=1.0, smile=True, arm_to=None):
    """A tiny blocky person for a photo: torso, head, hair, two dot eyes and a smile. Faces -y."""
    s = scale
    kit.box(f"{name}.body", (0.09 * s, 0.05 * s, 0.12 * s), (x, y, z + 0.06 * s), kit.plastic(shirt, 0.6), parent, bevel=0.008)
    kit.box(f"{name}.legs", (0.08 * s, 0.045 * s, 0.1 * s), (x, y, z - 0.03 * s), kit.plastic("#3d4a6e", 0.7), parent, bevel=0.006)
    kit.sphere(f"{name}.head", 0.045 * s, (x, y, z + 0.17 * s), kit.plastic(skin, 0.5), parent, seg=10)
    kit.box(f"{name}.hair", (0.092 * s, 0.07 * s, 0.03 * s), (x, y + 0.012 * s, z + 0.205 * s), kit.plastic(hair, 0.6), parent, bevel=0.01)
    ink = kit.plastic("#1b1210", 0.5)
    for sx in (-1, 1):
        kit.box(f"{name}.eye{sx}", (0.012 * s, 0.006, 0.02 * s), (x + sx * 0.017 * s, y - 0.042 * s, z + 0.18 * s), ink, parent)
    kit.box(f"{name}.mouth", (0.05 * s, 0.006, 0.012 * s), (x, y - 0.043 * s, z + 0.156 * s), ink, parent)


def photo(kit, name, loc, rot_z, kind, w=0.42, h=0.34, stand=False):
    """A framed photo of the brothers, grown up, doing something together. Faces -y, then turned by rot_z."""
    e = kit.empty(name, loc, rot=(0, 0, rot_z * D2R))
    frame = kit.plastic("#fff4d0" if kind == "canoe" else "#f4ead8", 0.5)
    kit.box(f"{name}.fr", (w, 0.03, h), (0, 0, 0), frame, e, bevel=0.008)
    back = {"canoe": "#bfe6ff", "fish": "#79c4ff", "road": "#ffd27a", "ball": "#7fd06a", "camp": "#26305a"}[kind]
    kit.box(f"{name}.bg", (w - 0.05, 0.01, h - 0.05), (0, -0.016, 0), kit.plastic(back, 0.7), e)
    zb = -h / 2 + 0.05
    # the brothers: Ben (sandy hair, navy) and me (dark hair, grey)
    bx = -0.07
    person_box(kit, e, f"{name}.b", bx, -0.03, zb + 0.07, "#f0c8a0", "#26355e", "#c9a35a")
    person_box(kit, e, f"{name}.m", -bx, -0.03, zb + 0.07, "#e8b890", "#8d9099", "#2a1d15")
    if kind == "canoe":
        kit.box(f"{name}.lake", (w - 0.05, 0.012, 0.17), (0, -0.024, -h / 2 + 0.025 + 0.085), kit.plastic("#1f6be0", 0.45), e)
        for k_, wx_ in enumerate((-0.17, 0.0, 0.17)):
            kit.box(f"{name}.wave{k_}", (0.07, 0.006, 0.012), (wx_, -0.032, -h / 2 + 0.045), kit.plastic("#d8f0ff", 0.5), e)
        kit.box(f"{name}.can", (0.3, 0.05, 0.05), (0, -0.04, zb + 0.07), kit.plastic("#ff5a4e", 0.5), e, bevel=0.015)
        for sx in (-1, 1):
            kit.box(f"{name}.cb{sx}", (0.06, 0.05, 0.05), (sx * 0.16, -0.04, zb + 0.085), kit.plastic("#ff5a4e", 0.5), e,
                    rot=(0, sx * -0.5, 0), bevel=0.012)
        # arms over each other's shoulders
        kit.box(f"{name}.arm", (0.17, 0.02, 0.024), (0, -0.065, zb + 0.185), kit.plastic("#d8d8dc", 0.6), e, bevel=0.006)
    elif kind == "fish":
        kit.box(f"{name}.rod", (0.01, 0.01, 0.2), (0.12, -0.05, zb + 0.18), kit.plastic("#7a5a3a", 0.6), e, rot=(0, 0.5, 0))
    elif kind == "road":
        kit.box(f"{name}.car", (0.16, 0.05, 0.06), (0.0, -0.01, zb + 0.03), kit.plastic("#ff5a4e", 0.5), e, bevel=0.01)
    elif kind == "ball":
        kit.sphere(f"{name}.ball", 0.02, (0.12, -0.05, zb + 0.18), kit.plastic("#ffffff", 0.4), e, seg=8)
    elif kind == "camp":
        kit.box(f"{name}.fire", (0.05, 0.03, 0.07), (0, -0.04, zb + 0.035), kit.emit("#ff9a3a", 3.0), e, bevel=0.01)
    return e


# ---------------------------------------------------------------------------------------------- the dog
def dog(kit, name):
    e = kit.empty(name, (0, 0, -50))
    brown = kit.plastic("#9a6234", 0.7)
    white = kit.plastic("#fff7ea", 0.7)
    dark = kit.plastic("#3a2314", 0.6)
    kit.box(f"{name}.body", (0.34, 0.8, 0.34), (0, 0, 0.43), brown, e, bevel=0.05)
    kit.box(f"{name}.head", (0.32, 0.32, 0.3), (0, -0.52, 0.62), brown, e, bevel=0.05)
    kit.box(f"{name}.snout", (0.18, 0.2, 0.14), (0, -0.7, 0.57), kit.plastic("#c99660", 0.7), e, bevel=0.03)
    kit.box(f"{name}.nose", (0.07, 0.04, 0.05), (0, -0.81, 0.6), dark, e, bevel=0.01)
    kit.box(f"{name}.earL", (0.08, 0.12, 0.2), (0.19, -0.5, 0.65), dark, e, bevel=0.02)
    kit.box(f"{name}.earR", (0.08, 0.12, 0.2), (-0.19, -0.5, 0.65), white, e, bevel=0.02)   # the one white ear
    for sx in (-1, 1):
        kit.sphere(f"{name}.eye{sx}", 0.03, (sx * 0.09, -0.68, 0.68), kit.plastic("#101010", 0.3), e, seg=8)
    W["legs"] = []
    for i, (lx, ly) in enumerate([(-0.11, -0.28), (0.11, -0.28), (-0.11, 0.28), (0.11, 0.28)]):
        hinge = kit.empty(f"{name}.leg{i}", (lx, ly, 0.3), e)
        kit.box(f"{name}.legm{i}", (0.09, 0.09, 0.3), (0, 0, -0.15), brown, hinge, bevel=0.02)
        W["legs"].append(hinge)
    W["tail"] = kit.empty(f"{name}.tail", (0, 0.4, 0.52), e)
    kit.box(f"{name}.tailm", (0.06, 0.06, 0.3), (0, 0.0, 0.14), brown, W["tail"], bevel=0.02)
    # a round tag with a bone shape (no text)
    kit.cyl(f"{name}.tag", 0.05, 0.015, (0, -0.4, 0.36), kit.plastic("#ffd23a", 0.3, spec=0.8), e, rot=(math.pi / 2, 0, 0), n=14)
    kit.box(f"{name}.bone", (0.05, 0.02, 0.012), (0, -0.412, 0.36), kit.plastic("#8a6a10", 0.5), e)
    return e


# ---------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    plastic = kit.plastic
    tl["cues"].sort(key=lambda c: c["t"])
    ctx = {}
    wall = plastic("#fbf6ec", 0.8, spec=0.1)
    floorm = plastic("#d9a86c", 0.55, spec=0.2)
    lawn = plastic("#79c256", 0.85, spec=0.05)
    road = plastic("#5b6070", 0.9, spec=0.05)
    walk = plastic("#d9d6cf", 0.85, spec=0.05)
    wood = plastic("#8a5a34", 0.6, spec=0.2)
    cream = plastic("#fff4d0", 0.55)
    ext = plastic("#7fc7ff", 0.7)
    dark = plastic("#262c3c", 0.6)
    mus = "#e0b030"
    teal = "#2fbfb0"

    # lights: the base is 1, animate sets the real strengths through the gains
    sun = kit.light("sun", "SUN", (0, 0, 40), 1.0, "#fff1d6", size=0.06)
    sun.data.angle = 0.06
    fill = kit.light("fill", "SUN", (0, -30, 20), 1.0, "#ffffff", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    moon = kit.light("moon", "SUN", (-10, -6, 30), 1.0, "#8fb0ff")
    moon.data.angle = 0.1
    mf = kit.light("mf", "SUN", (0, 30, 20), 1.0, "#ffd9a8", shadow=False)
    mf.data.angle = 0.3
    kit.aim(mf, (0, 0, 0))
    kit.light("lamp_lr", "POINT", (0.3, 0.4, 2.45), 1.0, "#ffd9a0", size=0.25)
    kit.light("lamp_h", "POINT", (8.5, 0.0, 2.3), 1.0, "#ffd9a0", size=0.25)
    kit.light("lamp_br", "POINT", (14.6, 0.2, 2.3), 1.0, "#ffd9a0", size=0.25)
    kit.light("wr", "POINT", (G.WR[0], G.WR[1] + 2.6, 2.3), 1.0, "#dfe8ff", size=0.3, shadow=False)
    kit.light("spl", "POINT", (120.0, -2.0, 2.2), 1.0, "#ffffff", size=0.5, shadow=False)
    kit.light("kd", "POINT", (G.KD[0], G.KD[1] - 1.4, 2.0), 1.0, "#ffffff", size=0.5, shadow=False)
    bf = kit.light("bface", "SPOT", (13.0, 0.2, 1.5), 1.0, "#fff4d0", size=0.06, spot=40, blend=0.6, shadow=False)
    kit.aim(bf, (16.0, 1.15, 1.3))
    ufl = kit.light("ufl", "SPOT", (0.3, 0.1, 0.5), 1.0, "#fff4d0", size=0.06, spot=48, blend=0.5)
    W["ufl"] = ufl
    ring = kit.light("ring", "SPOT", (G.WR[0], G.WR[1] + 2.6, 0.5), 1.0, "#fff4d0", size=0.05, spot=70, blend=0.6)
    ring.rotation_euler = (0, 0, 0)         # shines straight down, replaced below
    ring.rotation_euler = (math.pi, 0, 0)    # pointing up
    for i, hx in enumerate(G.HOUSE_X):
        kit.light(f"porch{i}", "POINT", (hx, -20.3, 2.4), 1.0, "#ffd39a", size=0.2, shadow=False)

    # ---------------------------------------------------------------------------- ground and street
    kit.plane("lawn", (500, 500), (0, 0, 0), lawn)
    kit.plane("verge", (500, 3.0), (0, -8.0, 0.005), walk)
    kit.plane("road", (500, 5.0), (0, -11.5, 0.006), road)
    kit.plane("verge2", (500, 3.0), (0, -15.0, 0.005), walk)
    for i in range(-12, 13):
        kit.box(f"dash{i}", (1.6, 0.14, 0.01), (i * 4.0, -11.5, 0.012), plastic("#fff4d0", 0.6), None)
    kit.plane("drive", (4.5, 6.0), (-8.0, -6.5, 0.012), walk)

    # ---------------------------------------------------------------------------- the row of houses across
    palette = ["#ffcf5a", "#ff7d6a", "#6fd0c8", "#b99cff", "#ffa94d", "#79b8ff", "#ff9ecb", "#9be06a", "#ffe28a"]
    roofc = ["#d2553d", "#5a4aa8", "#2c7ab8", "#d27a2a", "#a33b6a"]
    W["winmats"] = []
    W["porchmesh"] = []
    for i, hx in enumerate(G.HOUSE_X):
        body = plastic(palette[i % len(palette)], 0.7, spec=0.1)
        hy = G.HOUSE_Y
        kit.box(f"h{i}.body", (6.6, 6.0, 3.4), (hx, hy, 1.7), body, bevel=0.03)
        for sx in (-1, 1):
            kit.box(f"h{i}.roof{sx}", (3.9, 6.4, 0.18), (hx + sx * 1.6, hy, 3.75), plastic(roofc[i % 5], 0.7), None,
                    rot=(0, sx * 0.42, 0), bevel=0.02)
        kit.box(f"h{i}.chim", (0.6, 0.6, 1.2), (hx + 2.0, hy - 1.0, 4.3), plastic("#b05a3a", 0.8), None)
        kit.box(f"h{i}.door", (1.0, 0.06, 2.1), (hx, -20.96, 1.05), plastic("#8a5a34", 0.6), None, bevel=0.01)
        wm = kit._new(f"win{i}")
        nt = wm.node_tree
        nt.nodes.remove(nt.nodes["Principled BSDF"])
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = kit.col("#ffd98a")
        em.inputs["Strength"].default_value = 0.0
        out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
        nt.links.new(em.outputs[0], out.inputs["Surface"])
        W["winmats"].append(em)
        for sx in (-1, 1):
            kit.box(f"h{i}.win{sx}", (1.2, 0.06, 1.3), (hx + sx * 2.2, -20.96, 1.9), wm, None, bevel=0.01)
            kit.box(f"h{i}.winf{sx}", (1.34, 0.04, 1.44), (hx + sx * 2.2, -20.94, 1.9), cream, None)
        # porch: deck, steps, posts, roof
        kit.box(f"h{i}.deck", (3.6, 2.2, 0.4), (hx, -19.9, 0.2), plastic("#c9a070", 0.7), None, bevel=0.02)
        kit.box(f"h{i}.step", (1.8, 0.6, 0.2), (hx, -18.5, 0.1), plastic("#c9a070", 0.7), None, bevel=0.02)
        for sx in (-1, 1):
            kit.box(f"h{i}.post{sx}", (0.14, 0.14, 2.3), (hx + sx * 1.7, -18.9, 1.55), cream, None)
        kit.box(f"h{i}.proof", (3.9, 2.6, 0.12), (hx, -19.8, 2.75), plastic(roofc[(i + 2) % 5], 0.7), None, bevel=0.02)
        kit.box(f"h{i}.lampm", (0.16, 0.16, 0.2), (hx + 0.9, -20.9, 2.2), kit.emit("#ffe0a0", 2.0), None)
    # chairs for Varga (house 2) and Dale (house 3, on the lawn)
    kit.box("chairV.seat", (0.7, 0.7, 0.08), (0.0, -19.6, 0.85), plastic("#ff5a4e", 0.6), None, bevel=0.02)
    kit.box("chairV.back", (0.7, 0.08, 0.7), (0.0, -19.95, 1.2), plastic("#ff5a4e", 0.6), None, bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"chairV.l{sx}{sy}", (0.06, 0.06, 0.45), (sx * 0.3, -19.6 + sy * 0.3, 0.62), plastic("#8a2a24", 0.6), None)
    dx = G.HOUSE_X[3]
    kit.box("chairD.seat", (0.8, 0.7, 0.07), (dx, -17.4, 0.42), plastic("#3fa7d9", 0.6), None, bevel=0.02)
    kit.box("chairD.back", (0.8, 0.07, 0.6), (dx, -17.75, 0.75), plastic("#3fa7d9", 0.6), None, bevel=0.02, rot=(-0.3, 0, 0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"chairD.l{sx}{sy}", (0.05, 0.05, 0.4), (dx + sx * 0.33, -17.4 + sy * 0.28, 0.2), plastic("#1c5a80", 0.6), None)
    # trees along the verge
    for i, x in enumerate(range(-36, 40, 9)):
        kit.cyl(f"tree{i}.t", 0.2, 2.4, (x + 3.0, -16.5, 1.2), plastic("#7a5230", 0.8), n=8)
        kit.sphere(f"tree{i}.l", 1.5, (x + 3.0, -16.5, 3.4), plastic("#3fa84a", 0.8), seg=10)

    # ---------------------------------------------------------------------------- our house: the living room
    wall_x(kit, "lr.back", G.LR_Y1, G.LR_X0, G.LR_X1, G.WALL_H, wall)
    wall_x(kit, "lr.front", G.LR_Y0, G.LR_X0, G.LR_X1, G.WALL_H, wall, opening=(-3.7, -0.5, 0.8, 2.2), ext=ext)
    wall_y(kit, "lr.left", G.LR_X0, G.LR_Y0, G.LR_Y1, G.WALL_H, wall)
    wall_y(kit, "lr.right", G.LR_X1, G.LR_Y0, G.LR_Y1, G.WALL_H, wall, opening=(-1.0, 1.0, 0.0, 2.3))
    kit.box("lr.floor", (10.0, 7.0, 0.1), (0, 0, -0.04), floorm)
    kit.box("lr.rug", (3.6, 2.4, 0.02), (0.3, 0.3, 0.015), plastic("#e8d9b8", 0.9), None)
    kit.box("lr.door", (1.0, 0.06, 2.1), (2.9, -3.62, 1.05), plastic("#ff5a4e", 0.6), None, bevel=0.01)
    for nm, (xx, ww) in {"w": (-2.1, 3.2)}.items():
        kit.box("lr.winframe", (ww + 0.24, 0.06, 1.64), (xx, -3.6, 1.5), cream, None)
    # window glass: bright sky behind
    W["couchA"] = couch(kit, "couchA", (G.COUCH[0], G.COUCH[1], 0), mus)
    W["couchB"] = couch(kit, "couchB", (G.COUCH[0], G.COUCH[1], 0), teal)
    # coffee table
    kit.box("ctable.top", (1.5, 0.75, 0.07), (G.TABLE[0], G.TABLE[1], 0.43), plastic("#9a6a40", 0.5), None, bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"ctable.l{sx}{sy}", (0.08, 0.08, 0.4), (G.TABLE[0] + sx * 0.66, G.TABLE[1] + sy * 0.3, 0.2), wood, None)
    # fireplace, mantel
    fp = plastic("#e8dcc8", 0.8)
    kit.box("fp.body", (2.0, 0.5, 1.25), (0.0, 3.2, 0.62), fp, None, bevel=0.02)
    kit.box("fp.hole", (0.9, 0.06, 0.7), (0.0, 2.94, 0.4), plastic("#2a2320", 0.9), None)
    kit.box("fp.mantel", (2.5, 0.38, 0.1), (0.0, 3.18, 1.3), wood, None, bevel=0.02)
    kit.cyl("plant.pot", 0.12, 0.2, (0.85, 3.2, 1.45), plastic("#ff9a6a", 0.6), None, n=12)
    kit.sphere("plant.leaf", 0.17, (0.85, 3.2, 1.7), plastic("#3fa84a", 0.7), None, seg=10)
    # the photo on the mantel (version B only)
    W["mphoto"] = photo(kit, "mphoto", (-0.4, 3.2, 1.55), 0, "canoe", w=0.5, h=0.4)
    # floor lamp and dressing
    kit.cyl("flamp.pole", 0.03, 1.6, (-2.0, 2.9, 0.8), plastic("#444a58", 0.4), None, n=8)
    W["flampshade"] = kit.cyl("flamp.shade", 0.22, 0.3, (-2.0, 2.9, 1.7), kit.emit("#fff0c8", 0.0, name="shade_em"), None, n=14, r2=0.15)
    try:
        kit.prop("bookshelf", (-4.55, 1.6, 0), rot=90, height=2.0, tint="#d9b890")
        kit.prop("houseplant_1", (4.4, 2.8, 0), height=1.2)
        kit.prop("houseplant_1", (-4.4, -2.8, 0), height=1.0)
    except Exception:
        pass
    # dining table and chairs
    dxx, dyy = G.DINE
    kit.cyl("dt.top", 0.95, 0.06, (dxx, dyy, 0.74), plastic("#c28a52", 0.5), None, n=24)
    kit.cyl("dt.leg", 0.1, 0.72, (dxx, dyy, 0.36), wood, None, n=10)
    for k, (cxx, cyy) in enumerate([(-3.8, 1.55), (-2.6, 1.55), (-3.2, -0.7)]):
        kit.box(f"dt.ch{k}.s", (0.5, 0.5, 0.07), (cxx, cyy, 0.45), plastic("#ff5a4e", 0.6), None, bevel=0.02)
        kit.box(f"dt.ch{k}.b", (0.5, 0.07, 0.5), (cxx, cyy + (0.22 if cyy > 0.5 else -0.22), 0.75), plastic("#ff5a4e", 0.6), None, bevel=0.02)
        for sx in (-1, 1):
            for sy in (-1, 1):
                kit.box(f"dt.ch{k}.l{sx}{sy}", (0.05, 0.05, 0.42), (cxx + sx * 0.2, cyy + sy * 0.2, 0.21), wood, None)
    for k, (cxx, cyy) in enumerate([(-3.8, 0.7), (-2.6, 0.7)]):
        kit.cyl(f"dt.plate{k}", 0.15, 0.015, (cxx, cyy, 0.78), plastic("#ffffff", 0.4), None, n=16)

    # ---------------------------------------------------------------------------- hall and my room
    wall_x(kit, "hall.n", 1.0, G.HALL_X0, 12.0, 2.6, wall)
    wall_x(kit, "hall.s", -1.0, G.HALL_X0, 12.0, 2.6, wall)
    kit.box("hall.floor", (7.0, 2.0, 0.1), (8.5, 0, -0.04), floorm)
    kit.box("hall.runner", (6.4, 0.7, 0.02), (8.5, 0, 0.015), plastic("#ff7d6a", 0.9), None)
    wall_y(kit, "br.door", 12.0, -2.5, 2.5, 2.6, wall, opening=(-0.45, 0.45, 0.0, 2.1))
    wall_x(kit, "br.n", 2.5, 12.0, 17.0, 2.6, wall)
    wall_x(kit, "br.s", -2.5, 12.0, 17.0, 2.6, wall, opening=(14.0, 16.0, 0.9, 2.1), ext=ext)
    wall_y(kit, "br.e", 17.0, -2.5, 2.5, 2.6, wall)
    kit.box("br.floor", (5.0, 5.0, 0.1), (14.5, 0, -0.04), floorm)
    kit.box("br.rug", (2.2, 1.6, 0.02), (13.8, -0.4, 0.015), plastic("#9ec3ff", 0.9), None)
    kit.box("br.winframe", (2.24, 0.06, 1.34), (15.0, -2.54, 1.5), cream, None)
    # the door leaf, hinged at y = +0.45 and swinging into my room
    W["door"] = kit.empty("mydoor", (12.0, 0.45, 0.0))
    kit.box("mydoor.leaf", (0.06, 0.88, 2.06), (0.0, -0.45, 1.03), plastic("#ff5a4e", 0.55), W["door"], bevel=0.01)
    kit.box("mydoor.knob", (0.08, 0.06, 0.06), (0.05, -0.8, 1.0), plastic("#ffd23a", 0.3), W["door"])
    # the strip of light under it
    W["strip"] = kit.box("strip", (0.4, 0.86, 0.006), (12.25, 0.0, 0.02), kit.emit("#fff4d0", 0.0, name="strip_em"), None)
    for n in W["strip"].data.materials:
        pass
    # four strokes scratched into the frame, knee height, 1 cm proud of the hall face
    for i in range(4):
        kit.box(f"tally{i}", (0.014, 0.022, 0.2), (11.918, -0.62 - 0.055 * i, 0.45), kit.plastic("#fff4d0", 0.5), None)
    # hall photos (version B)
    W["hallphotos"] = []
    kinds = ["fish", "road", "ball", "camp", "canoe", "fish"]
    for i, k in enumerate(kinds):
        p = photo(kit, f"hp{i}", (6.0 + 1.0 * i, 0.94, 1.55), 0, k, w=0.5, h=0.4)
        p.rotation_euler = (0, 0, 0)
        W["hallphotos"].append(p)
    # my bed, bedside table, lamp, clock
    bx_, by_ = G.BED
    kit.box("bed.frame", (2.4, 1.3, 0.3), (bx_, by_, 0.2), wood, None, bevel=0.03)
    kit.box("bed.mat", (2.3, 1.2, 0.18), (bx_, by_, 0.43), plastic("#ffffff", 0.8), None, bevel=0.05)
    kit.box("bed.head", (0.1, 1.3, 1.1), (16.4, by_, 0.75), wood, None, bevel=0.03)
    kit.box("bed.pillow", (0.5, 0.9, 0.14), (16.05, by_, 0.58), plastic("#fff4d0", 0.8), None, bevel=0.05)
    kit.box("bed.blanket", (1.5, 1.24, 0.1), (14.95, by_, 0.54), plastic("#ff5a4e", 0.8), None, bevel=0.04)
    sx_, sy_ = G.STAND
    kit.box("stand.box", (0.5, 0.5, 0.55), (sx_, sy_, 0.275), wood, None, bevel=0.02)
    kit.box("blamp.base", (0.14, 0.14, 0.3), (sx_ + 0.02, sy_ + 0.12, 0.7), plastic("#ffd23a", 0.4), None)
    kit.cyl("blamp.shade", 0.17, 0.22, (sx_ + 0.02, sy_ + 0.12, 0.95), kit.emit("#fff0c8", 0.0, name="bshade_em"), None, n=14, r2=0.1)
    W["clockface"], W["clocktex"] = _clock(kit, sx_, sy_)
    # the sheet (for Friday)
    W["sheet"] = kit.box("sheet", (1.7, 1.2, 0.5), (15.4, by_, 0.88), plastic("#b9cdf0", 0.8), None, bevel=0.06)
    hide(W["sheet"], True)
    # ---------------------------------------------------------------------------- the plate and friends
    pl = kit.empty("plate", (0, 0, -50))
    kit.cyl("plate.disc", 0.2, 0.02, (0, 0, 0), plastic("#d9d2c2", 0.45), pl, n=24)
    bread = plastic("#d9b377", 0.8)
    fill_ = plastic("#d9534f", 0.7)
    for sgn in (-1, 1):
        tri = kit.mesh_obj(f"plate.tri{sgn}", [(-0.08, -0.08, 0), (0.08, -0.08, 0), (-0.08, 0.08, 0),
                                                (-0.08, -0.08, 0.05), (0.08, -0.08, 0.05), (-0.08, 0.08, 0.05)],
                           [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)], bread, pl,
                           (0.0 + sgn * 0.02, 0.0 + sgn * 0.01, 0.012), (0, 0, (0.0 if sgn < 0 else 180.0) * D2R))
        kit.box(f"plate.fill{sgn}", (0.1, 0.1, 0.012), (sgn * 0.0, 0, 0.034), fill_, pl, rot=(0, 0, 0.78))
    for k in range(7):
        kit.box(f"plate.crust{k}", (0.1, 0.022, 0.024), (-0.09 + 0.012 * (k % 3), 0.09 - 0.02 * (k % 4), 0.022 + 0.022 * (k // 4)),
                plastic("#b5823c", 0.8), pl, rot=(0, 0, 0.3 * k))
    W["plate"] = pl
    rem = kit.box("remote", (0.07, 0.2, 0.03), (0, 0, -50), plastic("#222733", 0.5), None, bevel=0.01)
    kit.box("remote.btn", (0.04, 0.04, 0.012), (0, 0.04, 0.02), plastic("#ff5a4e", 0.5), rem)
    cer = kit.empty("cereal", (0, 0, -50))
    kit.box("cereal.box", (0.2, 0.08, 0.3), (0, 0, 0), plastic("#ff9a3a", 0.5), cer, bevel=0.01)
    kit.box("cereal.pic", (0.14, 0.01, 0.12), (0, -0.045, 0.03), plastic("#ffe27a", 0.5), cer)
    bowl = kit.empty("bowl", (0, 0, -50))
    kit.cyl("bowl.cup", 0.13, 0.09, (0, 0, 0.045), plastic("#4aa8e8", 0.4), bowl, n=18, r2=0.1)
    kit.cyl("bowl.milk", 0.11, 0.012, (0, 0, 0.085), plastic("#fff4e0", 0.4), bowl, n=18)
    for k in range(5):
        kit.sphere(f"bowl.o{k}", 0.024, (-0.06 + 0.03 * k, 0.03 * ((k * 3) % 4 - 1.5) / 1.5, 0.1), plastic("#ffb83a", 0.5), bowl, seg=6)
    # a pizza box with a one-slice pizza, and the slice on its own so it can slide to my plate
    pz = kit.empty("pizza", (0, 0, -50))
    kit.box("pizza.box", (0.56, 0.56, 0.04), (0, 0, 0.02), plastic("#c9a070", 0.7), pz, bevel=0.01)
    kit.box("pizza.lid", (0.56, 0.03, 0.4), (0, 0.29, 0.2), plastic("#c9a070", 0.7), pz, rot=(-0.25, 0, 0))
    kit.box("pizza.dots", (0.1, 0.012, 0.1), (0.1, 0.2, 0.05), plastic("#ff5a4e", 0.5), pz, rot=(0, 0, 0.78))
    sl = kit.empty("slice", (0, 0, -50))
    kit.mesh_obj("slice.tri", [(-0.1, -0.1, 0), (0.1, -0.1, 0), (0, 0.12, 0), (-0.1, -0.1, 0.035), (0.1, -0.1, 0.035), (0, 0.12, 0.035)],
                 [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)], plastic("#f2b83a", 0.6), sl, (0, 0, 0), (0, 0, 0))
    for k, (px_, py_) in enumerate([(-0.04, -0.04), (0.04, -0.03), (0.0, 0.05)]):
        kit.cyl(f"slice.pep{k}", 0.028, 0.012, (px_, py_, 0.04), plastic("#c8342c", 0.5), sl, n=10)
    W["objs"] = {"plate": pl, "remote": rem, "cereal": cer, "bowl": bowl, "pizza": pz, "slice": sl}
    # flashlight standing on the coffee table (a prop; the light is "ufl")
    fts = kit.empty("tblfl", (0, 0, -50))
    kit.cyl("tblfl.body", 0.04, 0.26, (0, 0, 0.13), plastic("#ff5a4e", 0.4), fts, n=10)
    kit.cyl("tblfl.head", 0.065, 0.06, (0, 0, 0.29), plastic("#333844", 0.3), fts, n=10)
    kit.cyl("tblfl.lens", 0.055, 0.01, (0, 0, 0.325), kit.emit("#fff4d0", 6.0), fts, n=10)
    beam = alpha_mat(kit, "beam_up", "#fff0c0", 0.018, 1.5)
    kit.cyl("tblfl.beam", 0.05, 1.6, (0, 0, 1.1), beam, fts, n=24, r2=0.45)
    noshadow(fts)
    W["objs"]["tblfl"] = fts
    # the ring of flashlights in the window room
    ringg = kit.empty("ringg", (0, 0, -50))
    for k in range(5):
        a = k * 2 * math.pi / 5
        fe = kit.empty(f"ring{k}", (0.22 * math.cos(a), 0.22 * math.sin(a), 0), ringg)
        kit.cyl(f"ring{k}.b", 0.035, 0.22, (0, 0, 0.11), plastic("#ffd23a", 0.4), fe, n=8)
        kit.cyl(f"ring{k}.lens", 0.045, 0.01, (0, 0, 0.225), kit.emit("#fff4d0", 5.0), fe, n=8)
    noshadow(ringg)
    W["objs"]["ring"] = ringg
    W["dog"] = dog(kit, "pickle")
    W["objs"]["dog"] = W["dog"]
    ctx["dog"] = True

    # ---------------------------------------------------------------------------- the car
    cx_, cy_ = G.CAR
    car = kit.empty("car", (cx_, cy_, 0))
    cb = plastic("#ff5a4e", 0.5, spec=0.5)
    kit.box("car.low", (4.2, 1.8, 0.55), (0, 0, 0.55), cb, car, bevel=0.08)
    kit.box("car.hood", (1.3, 1.76, 0.25), (1.5, 0, 0.9), cb, car, bevel=0.05)
    kit.box("car.trunk", (0.9, 1.76, 0.25), (-1.65, 0, 0.9), cb, car, bevel=0.05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.cyl(f"car.w{sx}{sy}", 0.34, 0.22, (sx * 1.35, sy * 0.9, 0.34), plastic("#262c3c", 0.8), car, rot=(math.pi / 2, 0, 0), n=16)
            kit.cyl(f"car.hub{sx}{sy}", 0.16, 0.24, (sx * 1.35, sy * 0.9, 0.34), plastic("#d9d6cf", 0.4), car, rot=(math.pi / 2, 0, 0), n=12)
    seatm = plastic("#3b4660", 0.7)
    kit.box("car.seatF", (0.5, 1.5, 0.35), (0.5, 0, 0.85), seatm, car, bevel=0.05)
    kit.box("car.seatFb", (0.14, 1.5, 0.6), (0.28, 0, 1.2), seatm, car, bevel=0.05)
    kit.box("car.seatB", (0.5, 1.5, 0.35), (-0.95, 0, 0.85), seatm, car, bevel=0.05)
    kit.box("car.seatBb", (0.14, 1.5, 0.6), (-1.18, 0, 1.2), seatm, car, bevel=0.05)
    kit.box("car.dash", (0.3, 1.6, 0.4), (1.2, 0, 1.15), plastic("#262c3c", 0.6), car, bevel=0.03)
    kit.cyl("car.wheel", 0.24, 0.05, (0.98, 0.42, 1.3), plastic("#262c3c", 0.5), car, rot=(0, math.pi / 2 - 0.5, 0), n=18, r2=0.24)
    kit.cyl("car.wheelhub", 0.07, 0.07, (1.0, 0.42, 1.32), plastic("#ffd23a", 0.4), car, rot=(0, math.pi / 2 - 0.5, 0), n=10)
    # the passenger door (side facing -y), hinged at its front edge x = +1.1
    W["cardoor"] = kit.empty("cardoor", (cx_ + 1.1, cy_ - 0.9, 0))
    kit.box("cardoor.leaf", (1.6, 0.07, 0.6), (-0.8, 0, 0.98), cb, W["cardoor"], bevel=0.02)
    kit.box("cardoor.win", (1.3, 0.075, 0.4), (-0.8, 0, 1.45), plastic("#bfe3ff", 0.1, spec=0.9), W["cardoor"])

    # ---------------------------------------------------------------------------- our porch
    pdk = plastic("#c9a070", 0.7)
    kit.box("our.deck", (4.0, 3.0, 0.3), (2.8, -5.0, 0.15), pdk, None, bevel=0.02)
    kit.box("our.step", (2.6, 0.7, 0.15), (2.8, -6.85, 0.075), pdk, None, bevel=0.02)
    for sx in (-1, 1):
        kit.box(f"our.post{sx}", (0.14, 0.14, 2.3), (2.8 + sx * 1.9, -6.4, 1.45), cream, None)
    kit.box("our.roof", (4.3, 3.4, 0.12), (2.8, -5.0, 2.65), plastic("#d2553d", 0.7), None, bevel=0.02)

    # ---------------------------------------------------------------------------- the window room (families)
    wx, wy = G.WR
    wallc = plastic("#ffe9c9", 0.8)
    ext_wall = plastic("#ffb98a", 0.7)
    wall_x(kit, "wr.fa", wy, wx - 5.0, wx + 3.0, 2.8, ext_wall, opening=(wx - 1.7, wx + 1.7, 0.8, 2.1))
    wall_x(kit, "wr.fb", wy, wx + 3.0, wx + 9.0, 2.8, ext_wall, opening=(wx + 4.3, wx + 7.7, 0.8, 2.1))
    wall_x(kit, "wr.back", wy + 5.5, wx - 5.0, wx + 9.0, 2.8, wallc)
    wall_y(kit, "wr.l", wx - 5.0, wy, wy + 5.5, 2.8, wallc)
    wall_y(kit, "wr.r", wx + 9.0, wy, wy + 5.5, 2.8, wallc)
    kit.box("wr.floor", (14.0, 5.5, 0.1), (wx + 2.0, wy + 2.75, -0.04), floorm)
    W["famcouch"] = couch(kit, "famcouch", (wx, wy + 4.6, 0), "#6fb0ff", width=3.6)
    kit.box("wr.rug", (3.2, 2.0, 0.02), (wx, wy + 2.9, 0.015), plastic("#ffd27a", 0.9), None)
    # a second window opening for the sisters, a frame around both
    for nm, xx in (("a", wx), ("b", wx + 6.0)):
        for sx in (-1, 1):
            kit.box(f"wr.frame{nm}{sx}", (0.1, 0.05, 1.4), (xx + sx * 1.75, wy - 0.05, 1.45), cream, None)
        for zz in (0.78, 2.12):
            kit.box(f"wr.frame{nm}z{zz}", (3.6, 0.05, 0.1), (xx, wy - 0.05, zz), cream, None)
    # ---------------------------------------------------------------------------- the kitchen drawer
    kx, ky = G.KD
    kit.box("kd.floor", (6.0, 5.0, 0.1), (kx, ky, -0.04), floorm)
    kit.box("kd.back", (6.0, 0.15, 2.6), (kx, ky + 1.6, 1.3), plastic("#ffe9c9", 0.8), None)
    kit.box("kd.cab", (2.6, 0.7, 0.9), (kx, ky + 1.1, 0.45), plastic("#6fb0ff", 0.6), None, bevel=0.02)
    kit.box("kd.top", (2.7, 0.8, 0.06), (kx, ky + 1.1, 0.93), plastic("#fff4d0", 0.5), None, bevel=0.01)
    kit.box("kd.drawer", (2.2, 0.62, 0.22), (kx, ky + 0.5, 0.72), plastic("#8ec5ff", 0.6), None, bevel=0.02)
    kit.box("kd.in", (2.1, 0.55, 0.02), (kx, ky + 0.5, 0.64), plastic("#26305a", 0.8), None)
    # batteries you can name at a glance: a dark or gold body, a white band and a silver nub, lying along x
    kit.box("kd.tray", (2.1, 0.56, 0.02), (kx, ky + 0.5, 0.84), plastic("#26305a", 0.8), None)
    bcols = ["#23262f", "#ffb02e", "#23262f", "#3fa84a"]
    for r in range(5):
        for c in range(6):
            bz = 0.89 + (0.09 if (r + c) % 3 == 0 else 0.0)
            bxx = kx - 0.88 + c * 0.35 + (0.12 if r % 2 else 0.0)
            byy = ky + 0.26 + r * 0.11
            mat_ = plastic(bcols[(r + c) % 4], 0.4)
            kit.cyl(f"kd.bat{r}{c}", 0.05, 0.3, (bxx, byy, bz), mat_, None, rot=(0, math.pi / 2, 0), n=10)
            kit.cyl(f"kd.bat{r}{c}n", 0.026, 0.05, (bxx + 0.17, byy, bz), plastic("#e8e8ee", 0.25, spec=0.8), None, rot=(0, math.pi / 2, 0), n=8)
            kit.cyl(f"kd.bat{r}{c}b", 0.053, 0.05, (bxx - 0.05, byy, bz), plastic("#fff4d0", 0.4), None, rot=(0, math.pi / 2, 0), n=10)
    # ---------------------------------------------------------------------------- the split pair
    sx0 = 120.0
    for side, (hexc, nm) in enumerate([(mus, "A"), (teal, "B")]):
        ox = sx0 + (-1.5 if side == 0 else 1.5)
        kit.box(f"sp{nm}.floor", (3.0, 3.0, 0.1), (ox, 0.5, -0.04), floorm)
        kit.box(f"sp{nm}.back", (3.0, 0.12, 2.7), (ox, 2.0, 1.35), plastic("#fbf6ec", 0.8), None)
        kit.box(f"sp{nm}.fp", (1.4, 0.4, 1.1), (ox, 1.75, 0.55), fp, None, bevel=0.02)
        kit.box(f"sp{nm}.mantel", (1.8, 0.3, 0.08), (ox, 1.72, 1.14), wood, None, bevel=0.02)
        couch(kit, f"sp{nm}.couch", (ox, 0.55, 0), hexc, width=2.5)
    kit.box("sp.divider", (0.07, 0.1, 2.9), (sx0, 0.5, 1.4), kit.emit("#fffaf0", 2.0), None)
    photo(kit, "spphoto", (sx0 + 1.2, 1.5, 1.5), 0, "canoe", w=0.5, h=0.4)

    # ---------------------------------------------------------------------------- clouds, dust
    W["clouds"] = []
    cm = plastic("#6f7e9c", 0.9)
    for i in range(16):
        e = kit.empty(f"cloud{i}", ((i * 7) % 60 - 30, -28 - (i % 4) * 8, 13 + (i % 3) * 2.5))
        for k in range(4):
            kit.sphere(f"cloud{i}.{k}", 3.2 - 0.4 * k, (k * 3.0 - 4.0, (k % 2) * 1.0, (k % 3) * 0.5), cm, e, seg=10)
        e.scale = (1.0, 1.0, 0.55)
        hide(e, True)
        W["clouds"].append(e)
    W["dust"] = []
    dm = kit.emit("#fff4d0", 3.0, name="dustm")
    for k in range(26):
        d = kit.sphere(f"dust{k}", 0.005, (0, 0, -50), dm, None, seg=6)
        noshadow(d)
        W["dust"].append(d)

    build_inset(kit, ctx)
    W["ctx"] = ctx
    return ctx


def _clock(kit, sx_, sy_):
    face = kit.box("clock.body", (0.26, 0.3, 0.14), (sx_, sy_ - 0.12, 0.62), kit.plastic("#262c3c", 0.5), None, bevel=0.015)
    m, tex = image_mat(kit, "clockmat", 1.4)
    pl = kit.plane("clock.face", (0.22, 0.1), (sx_ - 0.136, sy_ - 0.12, 0.64), m, None, rot=(math.pi / 2, 0, -math.pi / 2))
    pl.rotation_euler = (math.pi / 2, 0, -math.pi / 2)
    noshadow(pl)
    return pl, tex


def clock_image(txt):
    from PIL import Image, ImageDraw, ImageFont
    p = TMP / f"clock-{txt.replace(':', '_')}.png"
    if not p.exists():
        im = Image.new("RGB", (440, 200), hexrgb("#10162c"))
        d = ImageDraw.Draw(im)
        f = ImageFont.truetype(str(FONT), 150)
        bb = d.textbbox((0, 0), txt, font=f)
        d.text(((440 - (bb[2] - bb[0])) / 2 - bb[0], (200 - (bb[3] - bb[1])) / 2 - bb[1]), txt, fill=hexrgb("#7dffd0"), font=f)
        im.save(p)
    return str(p)


# ---------------------------------------------------------------------------------------------- the check inset
ICON = {"mom": ("#d8b9f2", "#b9b6c4"), "ben": ("#f0c8a0", "#c9a35a"), "me": ("#e8b890", "#2a1d15"), "pickle": ("#9a6234", "#fff7ea")}


def check_image(state):
    """The rule meter: four round faces in a row (Mom, Ben, me, Pickle), each with a badge. state = (ben, me, qx)."""
    from PIL import Image, ImageDraw, ImageFont
    ben, me, qx = state
    p = TMP / f"check-{ben}-{me}-{qx}.png"
    if p.exists():
        return str(p)
    Wd, Hd = 800, 300
    im = Image.new("RGB", (Wd, Hd), hexrgb("#1b2750"))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, Wd - 7, Hd - 7], radius=34, outline=hexrgb("#fff4d0"), width=9)
    f = ImageFont.truetype(str(FONT), 120)
    centres = [100 + 200 * i for i in range(4)]
    marks = {"mom": "tick", "ben": ben, "me": me, "pickle": "tick"}
    for cx, who in zip(centres, ["mom", "ben", "me", "pickle"]):
        skin, hair = ICON[who]
        cy = 130
        r = 74
        d.ellipse([cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6], fill=hexrgb("#fff4d0"))
        if who == "pickle":
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hexrgb("#9a6234"))
            d.rounded_rectangle([cx - r + 2, cy - r + 6, cx - r + 34, cy - 4], radius=10, fill=hexrgb("#fff7ea"))   # the one white ear
            d.rounded_rectangle([cx + r - 34, cy - r + 6, cx + r - 2, cy - 4], radius=10, fill=hexrgb("#3a2314"))
            d.ellipse([cx - 18, cy + 8, cx + 18, cy + 36], fill=hexrgb("#c99660"))
            d.ellipse([cx - 8, cy + 10, cx + 8, cy + 22], fill=hexrgb("#1b1210"))
        else:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hexrgb(skin))
            d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=hexrgb(hair))
            if who == "mom":
                d.rectangle([cx - r, cy - 6, cx - r + 14, cy + 50], fill=hexrgb(hair))
                d.rectangle([cx + r - 14, cy - 6, cx + r, cy + 50], fill=hexrgb(hair))
            if who == "ben":
                d.rectangle([cx - r + 6, cy + r - 26, cx + r - 6, cy + r - 6], fill=hexrgb("#26355e"))
        if who != "pickle":
            for sx in (-1, 1):
                d.ellipse([cx + sx * 26 - 9, cy - 4, cx + sx * 26 + 9, cy + 14], fill=hexrgb("#1b1210"))
            d.arc([cx - 24, cy + 14, cx + 24, cy + 46], 20, 160, fill=hexrgb("#1b1210"), width=7)
        else:
            for sx in (-1, 1):
                d.ellipse([cx + sx * 26 - 8, cy - 14, cx + sx * 26 + 8, cy + 2], fill=hexrgb("#1b1210"))
        m = marks[who]
        bx, by = cx + 52, 228
        if m == "tick":
            d.ellipse([bx - 36, by - 36, bx + 36, by + 36], fill=hexrgb("#38d27a"), outline=hexrgb("#fff4d0"), width=5)
            d.line([bx - 17, by + 2, bx - 4, by + 16, bx + 20, by - 14], fill=(255, 255, 255), width=11, joint="curve")
        elif m == "q" and qx is None:
            d.ellipse([bx - 36, by - 36, bx + 36, by + 36], fill=hexrgb("#ffd23a"), outline=hexrgb("#fff4d0"), width=5)
            bb = d.textbbox((0, 0), "?", font=f)
            fs = ImageFont.truetype(str(FONT), 66)
            bb = d.textbbox((0, 0), "?", font=fs)
            d.text((bx - (bb[2] - bb[0]) / 2 - bb[0], by - (bb[3] - bb[1]) / 2 - bb[1]), "?", fill=hexrgb("#1b2750"), font=fs)
    if qx is not None:
        # the question mark slides from Ben's badge to mine
        bx = (centres[1] + 52) + (centres[2] + 52 - (centres[1] + 52)) * qx
        by = 228 - 34 * math.sin(math.pi * qx)
        d.ellipse([bx - 40, by - 40, bx + 40, by + 40], fill=hexrgb("#ffd23a"), outline=hexrgb("#fff4d0"), width=5)
        fs = ImageFont.truetype(str(FONT), 72)
        bb = d.textbbox((0, 0), "?", font=fs)
        d.text((bx - (bb[2] - bb[0]) / 2 - bb[0], by - (bb[3] - bb[1]) / 2 - bb[1]), "?", fill=hexrgb("#1b2750"), font=fs)
    im.save(p)
    return str(p)


def build_inset(kit, ctx):
    cam = kit.OBJ["cam"]
    m, tex = image_mat(kit, "inset", 1.0)
    m2, tex2 = image_mat(kit, "inset2", 1.0)
    pl = kit.plane("inset", (1.0, 1.0), (0, 0, -0.15), m, cam)
    big = kit.plane("insetbig", (1.0, 1.0), (0, 0, -0.15), m2, cam)
    for o in (pl, big):
        noshadow(o)
    ctx["inset"] = (pl, big, tex, tex2)
    ctx["imgs"] = {}


def _img(ctx, state):
    if state not in ctx["imgs"]:
        im = bpy.data.images.load(check_image(state))
        im.colorspace_settings.name = "sRGB"
        ctx["imgs"][state] = im
    return ctx["imgs"][state]


STATES = {"A": ("tick", "tick", None), "A0": ("none", "tick", None), "B": ("q", "tick", None),
          "C": ("tick", "q", None), "D": ("tick", "tick", None)}


def place_inset(ctx, state, big, lens):
    pl, bg, tex, tex2 = ctx["inset"]
    key = state if isinstance(state, tuple) else STATES[state]
    tex.image = _img(ctx, key)
    tex2.image = tex.image
    d = 0.15
    unit = d / lens
    pw0 = 0.42 * 13.5 * unit
    ph0 = pw0 * 300 / 800
    pw, ph = pw0 * 1.3, ph0 * 1.3             # 1.3x larger (critic r1), top and left edges where they were
    x = -0.40 * 6.75 * unit + (pw - pw0) / 2
    y = 0.775 * 12.0 * unit - (ph - ph0) / 2
    if big:
        pl.location, pl.scale = (0, 0, 5), (pw, ph, 1)        # out of sight behind the camera
        bw = 0.86 * 13.5 * unit
        bg.location, bg.scale = (0, 0.30 * 12.0 * unit, -d), (bw, bw * 300 / 800, 1)
    else:
        pl.location, pl.scale = (x, y, -d), (pw, ph, 1)
        bg.location, bg.scale = (0, 0, 5), (pw, ph, 1)


# ---------------------------------------------------------------------------------------------- animation
def _first(kit, story, tl):
    """After the cast exists: the flashlights, the watch and the ponytail ride the rig's own parts."""
    beam = alpha_mat(kit, "beam_fwd", "#fff0c0", 0.06, 1.5)
    W["fls"] = {}
    for who, arm in (("me", "arm1"), ("ben", "arm-1"), ("mom", "arm1"), ("f1", "arm1"), ("f2", "arm1"), ("f3", "arm1")):
        a = bpy.data.objects.get(f"{who}.{arm}")
        if a is None:
            continue
        e = kit.empty(f"fl.{who}", (0, 0, -1.55), a)
        kit.cyl(f"fl.{who}.body", 0.19, 1.0, (0, 0, 0.0), kit.plastic("#ff5a4e", 0.4), e, n=10)
        kit.cyl(f"fl.{who}.head", 0.3, 0.3, (0, 0, -0.62), kit.plastic("#333844", 0.3), e, n=10)
        kit.cyl(f"fl.{who}.lens", 0.25, 0.04, (0, 0, -0.79), kit.emit("#fff4d0", 14.0), e, n=10)
        bm = kit.cyl(f"fl.{who}.beam", 3.0, 11.0, (0, 0, -6.3), beam, e, n=20, r2=0.2)
        bm.scale = (1, 1, 1)
        # the beam's wide end is at -z: cyl() puts r at -h/2 and r2 at +h/2, so swap by making r the far end
        sp = kit.light(f"fl_{who}", "SPOT", (0, 0, -0.85), 1.0, "#fff4d0", size=0.04, spot=52, blend=0.6, parent=e)
        noshadow(e)
        W["fls"][who] = e
        hide(e, True)
    # the watch: my Ben's is BLACK on his LEFT wrist (arm1), this Ben's canoe red on his RIGHT (arm-1). A plain pale
    # disc dial on the front, the outer side and the back of the band (it reads from any side), no numerals
    W["watch"] = {}
    for side, arm, bandc in (("L", "arm1", "#16181e"), ("R", "arm-1", "#d00018")):
        a = bpy.data.objects.get(f"ben.{arm}")
        if a is None:
            continue
        e = kit.empty(f"watch{side}", (0, 0, -1.4), a)
        bmat = kit.emit(bandc, 0.9, name="watchR_em") if side == "R" else kit.plastic(bandc, 0.35, spec=0.6)
        kit.box(f"watch{side}.band", (1.2, 1.18, 0.7), (0, 0, 0), bmat, e, bevel=0.05)
        sgn = 1 if side == "L" else -1
        dc = kit.plastic("#fbf3df", 0.3)
        kit.box(f"watch{side}.dial", (0.9, 0.12, 0.54), (0, -0.6, 0.0), dc, e, bevel=0.04)
        kit.box(f"watch{side}.dialb", (0.9, 0.12, 0.54), (0, 0.6, 0.0), dc, e, bevel=0.04)
        kit.box(f"watch{side}.dial2", (0.12, 0.9, 0.54), (sgn * 0.6, 0, 0.0), dc, e, bevel=0.04)
        hide(e, True)
        W["watch"][side] = e
    # Varga's ponytail
    hg = bpy.data.objects.get("varga2.headg")
    if hg is not None:
        kit.box("pony.tie", (0.2, 0.2, 0.14), (0, 0.66, 0.12), kit.plastic("#ff5a4e", 0.5), hg)
        kit.box("pony.tail", (0.34, 0.3, 1.9), (0, 0.8, -0.75), kit.plastic("#e6e6f2", 0.65), hg, bevel=0.1)
    W["inited"] = True


def animate(kit, story, tl, t, ctx):
    from blocky import acting
    if not W.get("inited"):
        _first(kit, story, tl)
    L = look_at(tl, t)
    gains = {}
    sc = bpy.context.scene
    # ---- sun, moon, fill, sky
    so = kit.LIGHTS["sun"]["obj"]
    el, az = L["el"] * D2R, L["az"] * D2R
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    so.location = d * 60
    kit.aim(so, (0, 0, 0))
    kit.LIGHTS["sun"]["light"].color = L["sun_col"]
    gains["sun"] = L["sun"]
    gains["moon"] = L["moon"]
    kit.LIGHTS["moon"]["light"].color = L["moon_col"]
    mo = kit.LIGHTS["moon"]["obj"]
    mo.location = d * 60
    kit.aim(mo, (0, 0, 0))
    gains["fill"] = L["fill"]
    gains["mf"] = L["mf"]
    kit.LIGHTS["fill"]["light"].color = L["fill_col"]
    gains["lamp_lr"] = L["lr"] * 260.0
    gains["lamp_h"] = L["hall"] * 140.0 if L["lr"] > 0.5 else L["hall"] * 40.0
    gains["lamp_br"] = L["br"] * 220.0
    gains["wr"] = 120.0
    gains["spl"] = 35.0
    gains["kd"] = 30.0
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*L["sky"], 1.0)
    bg.inputs["Strength"].default_value = L["sky_str"]
    for n in W["flampshade"].data.materials[0].node_tree.nodes:
        if n.type == "EMISSION":
            n.inputs["Strength"].default_value = L["lr"] * 3.0
    for n in bpy.data.materials["bshade_em"].node_tree.nodes:
        if n.type == "EMISSION":
            n.inputs["Strength"].default_value = L["br"] * 3.0
    # ---- houses: windows and porch lamps
    hs = _track(tl, "hs")
    for i in range(len(G.HOUSE_X)):
        v, _ = sample(hs.get(i, []), t, ["win", "porch"], {"win": 0.0, "porch": 0.0})
        W["winmats"][i].inputs["Strength"].default_value = v["win"] * 5.0
        gains[f"porch{i}"] = v["porch"] * 90.0
    # ---- versions of the living room
    vc = last_cue([c for c in tl["cues"] if c["name"] == "ver"], t)
    ver = vc["v"] if vc else "B"
    hide(W["couchA"], ver != "A")
    hide(W["couchB"], ver != "B")
    hide(W["mphoto"], ver != "B")
    for p in W["hallphotos"]:
        hide(p, ver != "B")
    # ---- the doors, the strip of light
    dv, _ = sample([c for c in tl["cues"] if c["name"] == "doorm"], t, ["open"], {"open": 0.0})
    W["door"].rotation_euler = (0, 0, dv["open"] * 95 * D2R)
    cv, _ = sample([c for c in tl["cues"] if c["name"] == "cardoor"], t, ["open"], {"open": 0.0})
    W["cardoor"].rotation_euler = (0, 0, cv["open"] * 78 * D2R)
    sv, _ = sample([c for c in tl["cues"] if c["name"] == "strip"], t, ["v"], {"v": 0.0})
    for n in W["strip"].data.materials[0].node_tree.nodes:
        if n.type == "EMISSION":
            n.inputs["Strength"].default_value = sv["v"] * 4.0
    # ---- the clock
    cc = last_cue([c for c in tl["cues"] if c["name"] == "clock"], t)
    txt = cc["txt"] if cc else "2:00"
    key = ("clock", txt)
    if key not in W:
        im = bpy.data.images.load(clock_image(txt))
        im.colorspace_settings.name = "sRGB"
        W[key] = im
    W["clocktex"].image = W[key]
    # ---- the uplight and the table flashlight
    uv, uc = sample([c for c in tl["cues"] if c["name"] == "uplight"], t, ["v", "pos", "tgt"],
                    {"v": 0.0, "pos": [0, 0, -50], "tgt": [0, 1, 1]})
    W["ufl"].location = tuple(uv["pos"])
    kit.aim(W["ufl"], tuple(uv["tgt"]))
    gains["ufl"] = uv["v"] * 45.0
    bv, _ = sample([c for c in tl["cues"] if c["name"] == "bface"], t, ["v"], {"v": 0.0})
    gains["bface"] = bv["v"] * 450.0
    rv, _ = sample([c for c in tl["cues"] if c["name"] == "ringlight"], t, ["v"], {"v": 0.0})
    gains["ring"] = rv["v"] * 110.0
    # ---- objects (props, the dog): "obj" cues
    tracks = _track(tl, "obj")
    for oid, cues in tracks.items():
        ob = W["objs"].get(oid)
        if ob is None:
            continue
        v, c = sample(cues, t, ["pos", "yaw", "rot"], {"pos": [0, 0, -50], "yaw": 0.0, "rot": [0, 0, 0]})
        hid = bool(c and c.get("hide"))
        ob.location = (0, 0, -50) if hid else tuple(v["pos"])
        ob.rotation_euler = (v["rot"][0] * D2R, v["rot"][1] * D2R, v["yaw"] * D2R)
        if oid == "dog":
            moving = c is not None and c.get("dur", 0) > 0 and t < c["t"] + c["dur"]
            ph = t * (22.0 if moving else 0.0)
            for i, lg in enumerate(W["legs"]):
                lg.rotation_euler = (math.sin(ph + (math.pi if i in (1, 2) else 0)) * 0.7 if moving else 0.0, 0, 0)
            W["tail"].rotation_euler = (0.5, 0, math.sin(t * 14.0) * 0.6)
            if moving:
                ob.location.z += abs(math.sin(ph)) * 0.08
    # ---- the sheet
    shc = last_cue([c for c in tl["cues"] if c["name"] == "sheet"], t)
    hide(W["sheet"], not (shc and shc.get("on")))
    # ---- who sits
    for who, cs in _track(tl, "sit", lambda c: c["who"]).items():
        lc = last_cue(cs, t)
        root = bpy.data.objects.get(who)
        if lc and lc.get("on") and root is not None:
            root.location.z += lc.get("z", 0.6) - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    # ---- flashlights: -1 hidden, 0 held and off, >0 on
    for who, e in W["fls"].items():
        cs = [c for c in tl["cues"] if c["name"] == "fl" and c["who"] == who]
        v, _ = sample(cs, t, ["v"], {"v": -1.0})
        vv = v["v"]
        st = acting.state(tl, who, t, 0)
        show = vv >= 0 and not st["hidden"]
        hide(e, not show)
        gains[f"fl_{who}"] = max(0.0, vv) * 420.0 if show else 0.0
        bm = bpy.data.objects.get(f"fl.{who}.beam")
        if bm is not None:
            bm.hide_render = (vv <= 0.02) or not show
    # ---- the watch
    wc = last_cue([c for c in tl["cues"] if c["name"] == "watch"], t)
    side = wc["side"] if wc else "R"
    bh = acting.state(tl, "ben", t, 0)["hidden"]
    for s, e in W["watch"].items():
        hide(e, s != side or bh)
    vh = acting.state(tl, "varga2", t, 0)["hidden"]
    for ob in bpy.data.objects:
        if ob.name.startswith("pony."):
            ob.hide_render = vh
    # ---- dust motes drifting in a beam (shown only while a "dust" cue is on)
    dc = last_cue([c for c in tl["cues"] if c["name"] == "dust"], t)
    for k, dm in enumerate(W["dust"]):
        if dc and dc.get("on"):
            u = (k * 0.37) % 1.0
            x = 12.6 + 2.4 * u + 0.05 * math.sin(t * 0.7 + k)
            y = (0.0 + 1.15 * u) + 0.25 * math.sin(k * 1.9) + 0.04 * math.sin(t * 0.9 + k * 2.0)
            z = 1.25 - 0.25 * u + 0.18 * math.sin(k * 2.7) + 0.05 * math.sin(t * 0.5 + k * 1.3)
            dm.location = (x, y, z)
        else:
            dm.location = (0, 0, -50)
    # ---- clouds
    cl = last_cue([c for c in tl["cues"] if c["name"] == "clouds"], t)
    for k, e in enumerate(W["clouds"]):
        on = bool(cl and cl.get("on"))
        hide(e, not on)
        if on:
            e.location.x = ((k * 7) % 60 - 30) + (t - cl["t"]) * 0.8
    # ---- the check inset
    ch = last_cue([c for c in tl["cues"] if c["name"] == "check"], t)
    state = "A"
    big = False
    if ch:
        state = ch["state"]
        if isinstance(state, list):
            state = tuple(state)
        big = bool(ch.get("big"))
    _, _, lens, _ = _cam_now(story, tl, t)
    place_inset(ctx, state, big, lens)
    # a per-shot light scale (the plate close-ups, so the plate isn't blown white): the "gain" cue, set between cuts
    gv, _ = sample([c for c in tl["cues"] if c["name"] == "gain"], t, ["v"], {"v": 1.0})
    for nm in ("sun", "moon", "fill", "mf", "lamp_lr", "lamp_h", "lamp_br", "ufl"):
        if nm in gains:
            gains[nm] = gains[nm] * gv["v"]
    gains["ufl"] = gains.get("ufl", 0.0)
    if os.environ.get("EP92_DBG"):
        bpy.context.view_layer.update()
        for s_, e_ in W["watch"].items():
            if not e_.hide_render:
                print("DBG watch", s_, [round(v, 2) for v in e_.matrix_world.translation], flush=True)
        for nm in ("ben", "me"):
            h_ = bpy.data.objects.get(f"{nm}.headg")
            if h_ is not None:
                print("DBG head", nm, [round(v, 2) for v in h_.matrix_world.translation], flush=True)
        for nm in ("ben", "me"):
            for a_ in ("arm1", "arm-1"):
                o_ = bpy.data.objects.get(f"{nm}.{a_}")
                if o_ is not None:
                    print("DBG arm", nm, a_, [round(v, 2) for v in o_.matrix_world.translation], flush=True)
    return gains


def _cam_now(story, tl, t):
    from blocky import bl_story, polish
    if "shots" not in W:
        pol = polish.spec(story)
        W["shots"] = polish.cam_specs(story, tl, pol)
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    return bl_story.cam_at(W["shots"][shot["id"]], shot, t, {}, tl)
