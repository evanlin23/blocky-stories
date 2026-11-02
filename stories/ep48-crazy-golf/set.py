"""ep48 "crazy golf": the closing week of a crazy-golf course in a town park. Our own set, built from kit.py's parts.

Everything the story moves is driven by cues in story.json (see animate): the look (every light, the sky and the
sun, always eased over 0.35 s or more), props and shadows ("obj"), the windmill's sails, the fences, the gate and
the door, the flags, the Wrung One ("wring"), who sits ("sit"). Nobody's body casts a shadow: every character's and
the creature's meshes have visible_shadow off. People's shadows are flat drawn silhouettes lying elsewhere.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golf_layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {}            # named things the animation moves


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


# ---------------------------------------------------------------------------------------------- looks
def _L(**kw):
    base = dict(sun=0.0, sun_col="#ffe2b0", el=20.0, az=-70.0, fill=0.0, sky="#9bb6d8", sky_str=0.5, moon=0.0,
                lamp=0.0, strings=0.0, rim=0.0, bed=0.0, hall=0.0, dadroom=0.0, kitchen=0.0, win=0.0, myshadow=1.0,
                tee=0.0)
    base.update(kw)
    return base


LOOKS = {
    # late afternoon, warm, long object shadows
    "day": _L(sun=4.2, sun_col="#ffd9a0", el=30, az=-60, fill=0.9, sky="#a8c0e0", sky_str=0.9),
    "eve": _L(sun=4.2, sun_col="#ffcf8a", el=22, az=-62, fill=0.8, sky="#b6b0d0", sky_str=0.8),
    "front": _L(sun=4.2, sun_col="#ffd9a0", el=22, az=12, fill=0.5, sky="#a8c0e0", sky_str=0.8),
    # my bedroom, evening
    "bedroom": _L(sun=0.0, sky="#554c70", sky_str=0.3, bed=1.0, myshadow=0.0),
    # Dad's empty room, moonlight in the window
    "dadroom": _L(sun=0.0, sky="#202845", sky_str=0.12, dadroom=1.0, hall=0.5, myshadow=0.0),
    # the course at midnight: cool moon, the lamp post on, string lights off
    "midnight": _L(sun=0.0, moon=4.5, sky="#2a3868", sky_str=0.5, lamp=1.0, strings=0.0, fill=0.0),
    "kitchen": _L(sun=0.0, sky="#26304f", sky_str=0.18, kitchen=1.0, myshadow=0.0),
    "dawn": _L(sun=3.0, sun_col="#b8ccff", el=14, az=100, fill=0.6, sky="#9db4e8", sky_str=0.7, hall=0.7),
    "dawn2": _L(sun=3.8, sun_col="#ffd8b0", el=16, az=100, fill=0.7, sky="#c0c4e4", sky_str=0.8, hall=0.0),
    "win_lit": _L(sun=0.0, moon=4.5, sky="#2a3868", sky_str=0.5, win=1.0, lamp=0.0),
    "win_dark": _L(sun=0.0, moon=4.5, sky="#2a3868", sky_str=0.5, win=0.0, lamp=0.0),
    # Friday and Saturday dusk: low gold sun, sinking
    "dusk": _L(sun=3.8, sun_col="#ffc070", el=17, az=-78, fill=0.45, sky="#8a78a8", sky_str=0.6, lamp=0.5),
    "dusk2": _L(sun=3.2, sun_col="#ff9e5a", el=13, az=-78, fill=0.3, sky="#6b5a8a", sky_str=0.55, lamp=0.8, rim=1.0),
    "dusk_str": _L(sun=2.6, sun_col="#ff9e5a", el=10, az=-78, fill=0.18, sky="#5b4c7e", sky_str=0.36, lamp=1.0,
                   strings=1.0, tee=1.0, rim=1.0),
    "dusk_str2": _L(sun=2.2, sun_col="#ff9450", el=9, az=-78, fill=0.14, sky="#4e426f", sky_str=0.32, lamp=1.0,
                    strings=1.0, tee=1.0, rim=1.0),
    "sunday": _L(sun=4.6, sun_col="#fff0d0", el=58, az=-40, fill=1.0, sky="#a0c4ee", sky_str=1.1),
    "gold": _L(sun=3.6, sun_col="#ffc070", el=13, az=-78, fill=0.4, sky="#9a88b0", sky_str=0.55, lamp=0.6),
    "gold2": _L(sun=2.8, sun_col="#ffa468", el=10, az=-78, fill=0.3, sky="#7c6c9c", sky_str=0.45, lamp=0.8),
    "blank": _L(),
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
        dur = max(0.35, c.get("dur", 0.5))        # house bar: no switch faster than 0.3 s
        if t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            out = {}
            for k in cur:
                a, b = prev[k], cur[k]
                if isinstance(a, str):
                    out[k] = (kit_col(a), kit_col(b), u)
                else:
                    out[k] = a + (b - a) * u
            return _resolve(out)
    return _resolve(cur)


def kit_col(h):
    h = h.lstrip("#")
    f = lambda c: (c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def _resolve(d):
    out = {}
    for k, v in d.items():
        if isinstance(v, str):
            out[k] = kit_col(v)
        elif isinstance(v, tuple):
            a, b, u = v
            out[k] = tuple(a[i] + (b[i] - a[i]) * u for i in range(3))
        else:
            out[k] = v
    return out


# ---------------------------------------------------------------------------------------------- cue tracks
def _track(tl, name, keyf=lambda c: c.get("id")):
    out = {}
    for c in tl["cues"]:
        if c["name"] == name:
            out.setdefault(keyf(c), []).append(c)
    return out


def sample(cues, t, fields, defaults):
    """The value of each numeric field at t from a time-ordered list of cues; a cue's own "dur" eases it in."""
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


def last_cue(cues, t):
    last = None
    for c in cues:
        if c["t"] <= t:
            last = c
    return last


# ---------------------------------------------------------------------------------------------- materials
def shadow_mat(kit, alpha, name, colour="#566580"):
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    dif.inputs["Color"].default_value = kit.col(colour)
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = alpha
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(dif.outputs[0], mix.inputs[2])
    kit._fogged(m, mix.outputs[0])
    return m


def mesh_mat(kit, hexc="#9aa0a4"):
    """Builders' mesh: a diamond-ish grid that lets light and the view through (alpha from a checker)."""
    name = "mesh " + hexc
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = kit.col(hexc)
    b.inputs["Metallic"].default_value = 0.6
    b.inputs["Roughness"].default_value = 0.45
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (24.0, 24.0, 24.0)
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(45))
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    ck = nt.nodes.new("ShaderNodeTexChecker")
    ck.inputs["Scale"].default_value = 1.0
    nt.links.new(mp.outputs[0], ck.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.4
    ramp.color_ramp.elements[1].position = 0.6
    nt.links.new(ck.outputs["Fac"], ramp.inputs["Fac"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(ramp.outputs["Color"], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(b.outputs[0], mix.inputs[2])
    kit._fogged(m, mix.outputs[0])
    return m


# ---------------------------------------------------------------------------------------------- small builders
def text(kit, name, s, loc, size, mat, rot=(math.pi / 2, 0, 0), parent=None):
    c = bpy.data.curves.new(name, "FONT")
    c.body = s
    c.size = size
    c.align_x = "CENTER"
    c.align_y = "CENTER"
    c.extrude = 0.004
    ob = bpy.data.objects.new(name, c)
    ob.location = loc
    ob.rotation_euler = rot
    ob.data.materials.append(mat)
    return kit.link(ob, parent)


def tree(kit, name, x, y, h=4.0, dark=False):
    trunk = kit.plastic("#5a4330", 0.8)
    leaf = kit.plastic("#3f7a3a" if not dark else "#2f5f35", 0.8)
    kit.cyl(f"{name}.t", 0.18, h * 0.5, (x, y, h * 0.25), trunk, n=8)
    kit.sphere(f"{name}.l1", h * 0.34, (x, y, h * 0.62), leaf, seg=10)
    kit.sphere(f"{name}.l2", h * 0.26, (x + 0.4, y - 0.2, h * 0.88), leaf, seg=10)


def bench(kit, name, loc, yaw, mat, wood):
    """A bench facing -y at yaw 0 (rotated by yaw about z)."""
    e = kit.empty(name, loc, rot=(0, 0, yaw * D2R))
    kit.box(f"{name}.seat", (1.6, 0.46, 0.06), (0, 0, 0.45), mat, e, bevel=0.015)
    kit.box(f"{name}.back", (1.6, 0.06, 0.4), (0, 0.22, 0.72), mat, e, bevel=0.015, rot=(-0.12, 0, 0))
    for sx in (-1, 1):
        kit.box(f"{name}.leg{sx}", (0.07, 0.4, 0.45), (sx * 0.7, 0, 0.225), wood, e, bevel=0.01)
        kit.box(f"{name}.arm{sx}", (0.06, 0.4, 0.05), (sx * 0.78, 0, 0.66), mat, e, bevel=0.01)
    return e


def putter(kit, name, mat_shaft, mat_head):
    e = kit.empty(name, (0, 0, -50))
    kit.box(f"{name}.shaft", (0.025, 0.025, 0.95), (0, 0, 0.475), mat_shaft, e, bevel=0.008)
    kit.box(f"{name}.head", (0.06, 0.17, 0.045), (0, -0.06, 0.02), mat_head, e, bevel=0.01)
    noshadow_off = None  # (putters are objects: they cast ordinary shadows)
    return e


# ---------------------------------------------------------------------------------------------- flat shadows
HEAD_R = 0.21


def _parts(pose):
    """Boxes (cx, cy, w, h, rot_deg) of a person lying flat on the ground, feet at y = 0, head toward +y, plus
    the head circle's centre. R6 sizes: torso 0.68 wide, limbs 0.34, head 0.42 across."""
    P = []
    if pose in ("stand", "lie", "wave"):
        P += [(-0.17, 0.34, 0.34, 0.68, 0), (0.17, 0.34, 0.34, 0.68, 0)]           # legs
        P += [(0.0, 1.02, 0.68, 0.68, 0)]                                            # torso
        P += [(-0.51, 1.02, 0.34, 0.68, 0)]                                          # arms
        if pose == "wave":
            P += [(0.82, 1.18, 0.34, 0.68, -52)]
        else:
            P += [(0.51, 1.02, 0.34, 0.68, 0)]
        head = (0.0, 1.57)
    elif pose in ("sit", "hug"):
        # seen from above, a person sitting: legs forward (toward -y), torso, arms in front over the knees
        P += [(-0.17, 0.0, 0.34, 0.7, 0), (0.17, 0.0, 0.34, 0.7, 0)]
        P += [(0.0, 0.69, 0.68, 0.68, 0)]
        P += [(-0.51, 0.4, 0.34, 0.68, 0), (0.51, 0.4, 0.34, 0.68, 0)]
        if pose == "hug":
            P = [(-0.17, 0.0, 0.34, 0.7, 0), (0.17, 0.0, 0.34, 0.7, 0), (0.0, 0.69, 0.68, 0.68, 0),
                 (-0.51, 0.22, 0.34, 0.32, 0), (0.51, 0.22, 0.34, 0.32, 0)]
        head = (0.0, 1.24)
    else:
        raise ValueError(pose)
    return P, head


def flat_fig(kit, name, pose="stand", bun=False, scale=1.0):
    """A flat soft-edged silhouette: three stacked layers, each a little bigger and fainter. Returns its empty."""
    e = kit.empty(name, (0, 0, -50))
    parts, head = _parts(pose)
    grow = [0.07, 0.035, 0.0]
    alpha = [0.14, 0.17, 0.22]
    for L in range(3):
        m = shadow_mat(kit, alpha[L], f"shadow{L}")
        z = 0.012 + 0.003 * L
        g = grow[L]
        for i, (cx, cy, w, h, rot) in enumerate(parts):
            kit.box(f"{name}.p{L}{i}", (w + 2 * g, h + 2 * g, 0.004), (cx * scale, cy * scale, z), m, e,
                    rot=(0, 0, rot * D2R))
        hd = kit.cyl(f"{name}.h{L}", (HEAD_R + g) * scale, 0.004, (head[0] * scale, head[1] * scale, z), m, e, n=20)
        if bun:
            kit.cyl(f"{name}.b{L}", (0.11 + g) * scale, 0.004, (0.0, (head[1] + 0.27) * scale, z), m, e, n=14)
    for c in [e] + list(e.children_recursive):
        if hasattr(c, "visible_shadow"):
            c.visible_shadow = False
    return e


# ---------------------------------------------------------------------------------------------- the creature
class Wrung:
    """A person wrung like a cloth. Each block is turned further round than the one below: hips 0.25 w, chest 0.5 w,
    shoulders and arms 0.75 w, head w (degrees). `lean` tips the whole top half (pitch toward its front, roll)."""

    def __init__(self, kit):
        white = kit.plastic("#d4d0c4", 0.75, spec=0.1)
        green = kit.plastic("#3f7d6a", 0.75, spec=0.1)
        pants = kit.plastic("#3a7664", 0.8, spec=0.05)
        black = kit.plastic("#050507", 0.2, spec=0.6)
        hi = kit.emit("#ffffff", 22.0, "wrung eye light")
        self.root = kit.empty("wrung", (0, 0, -50))
        r = self.root
        for sx in (-1, 1):
            kit.box(f"wrung.leg{sx}", (0.22, 0.24, 0.74), (sx * 0.13, 0, 0.39), pants, r, bevel=0.025)
            kit.box(f"wrung.shoe{sx}", (0.23, 0.32, 0.08), (sx * 0.13, -0.04, 0.04), white, r, bevel=0.025)
        self.hips = kit.empty("wrung.hips", (0, 0, 0.76), r)
        kit.box("wrung.hipsb", (0.5, 0.28, 0.3), (0, 0, 0.15), white, self.hips, bevel=0.03)
        self._stripes(kit, self.hips, 0.5, 0.28, 0.3, 0.15, green)
        self.lean = kit.empty("wrung.lean", (0, 0, 1.06), r)
        self.chest = kit.empty("wrung.chest", (0, 0, 0), self.lean)
        kit.box("wrung.chestb", (0.56, 0.3, 0.38), (0, 0, 0.19), white, self.chest, bevel=0.03)
        self._stripes(kit, self.chest, 0.56, 0.3, 0.38, 0.19, green)
        self.shoulders = kit.empty("wrung.shoulders", (0, 0, 0.38), self.chest)
        kit.box("wrung.neckb", (0.13, 0.13, 0.16), (0, 0, 0.06), white, self.shoulders, bevel=0.02)
        for sx in (-1, 1):
            kit.box(f"wrung.arm{sx}", (0.2, 0.2, 0.96), (sx * 0.44, 0, -0.48), white, self.shoulders, bevel=0.025)
            kit.box(f"wrung.armg{sx}", (0.04, 0.21, 0.96), (sx * (0.44 + (0.1 if sx > 0 else -0.1)), 0, -0.48),
                    green, self.shoulders, bevel=0.005)
            kit.box(f"wrung.hand{sx}", (0.19, 0.19, 0.1), (sx * 0.44, 0, -1.0), white, self.shoulders, bevel=0.03)
        self.head = kit.empty("wrung.head", (0, 0, 0.14), self.shoulders)
        kit.box("wrung.headb", (0.34, 0.34, 0.44), (0, 0, 0.22), white, self.head, bevel=0.08, seg=3)
        for sx in (-1, 1):
            e = kit.sphere(f"wrung.eye{sx}", 0.05, (sx * 0.085, -0.165, 0.24), black, self.head, seg=14)
            e.scale = (1.0, 0.5, 1.9)
            kit.sphere(f"wrung.hi{sx}", 0.012, (sx * 0.085 + 0.012, -0.192, 0.285), hi, self.head, seg=8)
            kit.box(f"wrung.brow{sx}", (0.1, 0.012, 0.014), (sx * 0.085, -0.172, 0.39), black, self.head, bevel=0.004)
        noshadow(self.root)

    def _stripes(self, kit, parent, w, d, h, z, mat):
        for k, x in enumerate((-w * 0.3, 0.0, w * 0.3)):
            kit.box(f"{parent.name}.sf{k}", (0.07, d + 0.012, h + 0.004), (x, 0, z), mat, parent, bevel=0.004)
        for k, y in enumerate((-d * 0.25, d * 0.25)):
            kit.box(f"{parent.name}.ss{k}", (w + 0.012, 0.07, h + 0.004), (0, y, z), mat, parent, bevel=0.004)

    def pose(self, pos, yaw, wring, lean=(0.0, 0.0), hidden=False, head_extra=0.0):
        r = self.root
        r.location = (pos[0], pos[1], 0.0 if not hidden else -50)
        r.rotation_euler = (0, 0, yaw * D2R)
        w = wring * D2R
        self.hips.rotation_euler = (0, 0, 0.25 * w)
        self.lean.rotation_euler = (lean[0] * D2R, lean[1] * D2R, 0.0)
        self.chest.rotation_euler = (0, 0, 0.5 * w)
        self.shoulders.rotation_euler = (0, 0, 0.25 * w)
        self.head.rotation_euler = (0, 0, 0.25 * w + head_extra * D2R)


# ---------------------------------------------------------------------------------------------- the world
def build(kit, story, tl):
    plastic = kit.plastic
    ctx = {"objs": {}}
    tl["cues"].sort(key=lambda c: c["t"])      # every track below reads its cues in time order

    # materials
    turf = kit.grime("#5f9e3a", 0.82, 4.0, "turf", 0.9)
    worn = kit.grime("#7fa05a", 0.8, 5.0, "worn", 0.9)
    lawn = kit.grime("#6fae4a", 0.78, 1.4, "lawn", 0.95)
    timber = plastic("#8a6a44", 0.7, spec=0.15)
    white = plastic("#eeeae0", 0.6, spec=0.15)
    pond = plastic("#3f7d6a", 0.55, spec=0.2)
    water = plastic("#2e5a54", 0.2, spec=0.7)
    cream = plastic("#efe2c4", 0.65, spec=0.1)
    grey = kit.concrete("#9aa0a4", 1.2, 0.2, "pavement")
    asphalt = kit.concrete("#4a4c52", 2.0, 0.25, "asphalt")
    brick = kit.bricks("#a0573a", "#8a4830", "#6a5a50", 1.2) if hasattr(kit, "bricks") else plastic("#a0573a", 0.8)
    iron = kit.metal("#2c2f33", 0.5)
    stone = kit.concrete("#a8a290", 3.0, 0.3, "stonelook")
    tee_mat = plastic("#36703a", 0.85, spec=0.05)
    rubber = plastic("#2a2c30", 0.9, spec=0.05)

    # lights (the base is 1: animate sets the real strength through the gains)
    sun = kit.light("sun", "SUN", (0, 0, 40), 1.0, "#ffd9a0", size=0.06)
    sun.data.angle = 0.075          # soft-edged shadows in a low sun
    fill = kit.light("fill", "SUN", (0, -30, 20), 1.0, "#cfd8ff", shadow=False)
    fill.data.angle = 0.5
    moon = kit.light("moon", "SUN", (-10, 6, 30), 1.0, "#8aa4ff")
    moon.data.angle = 0.1
    kit.aim(fill, (0, 0, 0))
    kit.aim(moon, (0, 0, 0))
    lx, ly = G.LAMP
    kit.light("lamp", "POINT", (lx - 0.25, ly, 3.0), 1.0, "#ffcf90", size=0.12)
    for i, (sx, sy) in enumerate([(-3.6, 21.5), (3.6, 21.5), (-3.6, 28.5), (3.6, 28.5), (0.0, 32.0)]):
        kit.light(f"str{i}", "POINT", (sx, sy, 2.4), 1.0, "#ffb860", size=0.1, shadow=False)
    kit.light("tee", "POINT", (-4.5, 17.8, 1.3), 1.0, "#ffb86a", size=0.2, shadow=False)
    kit.light("rim", "POINT", (1.2, 22.6, 2.3), 1.0, "#ffb060", size=0.25, shadow=False)
    ax, ay = G.ROOM_A
    bx, by = G.ROOM_B
    cx, cy = G.ROOM_C
    kit.light("bed", "POINT", (ax - 1.0, ay + 0.8, 1.5), 1.0, "#ffbb70", size=0.2)
    kit.light("hall", "POINT", (G.HOUSE[0], G.HOUSE[1] + 2.0, 2.2), 1.0, "#ffc890", size=0.3)
    kit.light("dadroom", "POINT", (bx + 1.2, by + 1.6, 1.8), 1.0, "#9ab4ff", size=0.3)
    kit.light("hallB", "POINT", (bx, by - 2.4, 2.2), 1.0, "#9ab4ff", size=0.3)
    kit.light("kitchen", "POINT", (cx, cy, 2.2), 1.0, "#ffbf80", size=0.2)

    # ------------------------------------------------------------------------------------ ground
    kit.plane("lawn", (500, 500), (0, 0, 0), lawn)
    kit.plane("pavement", (80, 6.0), (0, -3.0, 0.01), grey)
    kit.plane("road", (200, 6.0), (0, -9.0, 0.005), asphalt)
    kit.plane("kerb", (80, 0.3), (0, -6.05, 0.04), plastic("#8c8f92", 0.7))
    kit.plane("course", (28.0, 33.0), (0, 16.0, 0.02), turf)
    kit.plane("yard", (28.0, 4.0), (0, 1.5, 0.025), worn)     # worn ground by the gate

    # railings along y = 0 with the gate gap at -1.3..1.3
    for side, (x0, x1) in (("w", (-13.6, -1.3)), ("e", (1.3, 13.6))):
        n = int((x1 - x0) / 0.3)
        kit.box(f"rail.top.{side}", (x1 - x0, 0.05, 0.05), ((x0 + x1) / 2, 0, 1.15), iron)
        kit.box(f"rail.bot.{side}", (x1 - x0, 0.05, 0.05), ((x0 + x1) / 2, 0, 0.25), iron)
        for i in range(n + 1):
            kit.box(f"rail.{side}{i}", (0.03, 0.03, 1.15), (x0 + i * (x1 - x0) / n, 0, 0.58), iron)
    # the gate: two leaves hinged at +-1.3, swung by cue
    W["gate"] = []
    for sx in (-1, 1):
        hinge = kit.empty(f"gate{sx}", (sx * 1.3, 0, 0), rot=(0, 0, 0))
        for i in range(8):
            kit.box(f"gate{sx}.b{i}", (0.03, 0.03, 1.15), (-sx * (0.08 + i * 0.16), 0, 0.58), iron, hinge)
        kit.box(f"gate{sx}.t", (1.3, 0.05, 0.05), (-sx * 0.65, 0, 1.15), iron, hinge)
        kit.box(f"gate{sx}.m", (1.3, 0.05, 0.05), (-sx * 0.65, 0, 0.12), iron, hinge)
        W["gate"].append((hinge, sx))
    for sx in (-1, 1):
        kit.box(f"gatepost{sx}", (0.22, 0.22, 1.5), (sx * 1.42, 0, 0.75), iron, bevel=0.03)
    # side fences of the course (low timber) and the back
    for sx in (-1, 1):
        kit.box(f"side{sx}", (0.1, 33, 0.6), (sx * 13.8, 16.5, 0.3), timber)
    kit.box("backfence", (28, 0.1, 0.9), (0, 32.5, 0.45), timber)

    # kiosk: cream hut by the gate, its hatch facing the gate (-x face); hollow so Dad can stand in it
    kx, ky = G.KIOSK
    kw, kd, kh = 3.0, 2.0, 2.5
    W["kiosk"] = kit.empty("kiosk", (kx, ky, 0))
    kit.box("kiosk.floor", (kw, kd, 0.1), (0, 0, 0.05), timber, W["kiosk"])
    kit.box("kiosk.back", (0.1, kd, kh), (kw / 2, 0, kh / 2), cream, W["kiosk"])
    kit.box("kiosk.n", (kw, 0.1, kh), (0, kd / 2, kh / 2), cream, W["kiosk"])
    kit.box("kiosk.s", (kw, 0.1, kh), (0, -kd / 2, kh / 2), cream, W["kiosk"])
    # front (-x) wall with a hatch window (y +-0.8, z 1.05..1.95)
    kit.box("kiosk.f0", (0.1, kd, 1.05), (-kw / 2, 0, 0.525), cream, W["kiosk"])
    kit.box("kiosk.f1", (0.1, kd, kh - 1.95), (-kw / 2, 0, (kh + 1.95) / 2), cream, W["kiosk"])
    for sy in (-1, 1):
        kit.box(f"kiosk.fs{sy}", (0.1, (kd - 1.6) / 2, 0.9), (-kw / 2, sy * (0.8 + (kd - 1.6) / 4), 1.5), cream,
                W["kiosk"])
    kit.box("kiosk.sill", (0.3, 1.7, 0.06), (-kw / 2 - 0.12, 0, 1.05), timber, W["kiosk"])
    kit.box("kiosk.roof", (kw + 0.5, kd + 0.5, 0.12), (0, 0, kh + 0.06), pond, W["kiosk"], bevel=0.02)
    kit.box("kiosk.inner", (0.02, kd - 0.2, kh - 0.3), (kw / 2 - 0.07, 0, kh / 2), plastic("#c9b894", 0.8), W["kiosk"])

    # ------------------------------------------------------------------------------------ the holes
    flagt = plastic("#eeeae0", 0.6)
    W["holes"] = {}
    W["fence"] = {}
    for n, hx, hy in G.HOLES:
        g = kit.empty(f"hole{n}", (hx, hy, 0))
        kit.box(f"h{n}.turf", (3.2, 3.2, 0.06), (0, 0, 0.05), turf if n % 2 else worn, g)
        for sy in (-1, 1):
            kit.box(f"h{n}.e{sy}", (3.4, 0.12, 0.14), (0, sy * 1.66, 0.09), timber, g)
        for sx in (-1, 1):
            kit.box(f"h{n}.f{sx}", (0.12, 3.2, 0.14), (sx * 1.66, 0, 0.09), timber, g)
        kit.cyl(f"h{n}.cup", 0.1, 0.01, (0.0, 1.0, 0.084), plastic("#101014", 0.5), g, n=14)
        kit.box(f"h{n}.tee", (0.5, 0.4, 0.02), (0.0, -1.1, 0.085), tee_mat, g)
        # the numbered post and the flag
        kit.box(f"h{n}.post", (0.1, 0.1, 0.7), (-1.35, -1.35, 0.4), pond, g, bevel=0.01)
        kit.box(f"h{n}.plate", (0.34, 0.03, 0.26), (-1.35, -1.41, 0.62), white, g, bevel=0.01)
        text(kit, f"h{n}.num", str(n), (-1.35, -1.43, 0.62), 0.2, plastic("#1c2a24", 0.5), parent=g)
        kit.cyl(f"h{n}.pole", 0.012, 1.1, (0.0, 1.0, 0.65), white, g, n=8)
        cloth = kit.empty(f"h{n}.cloth", (0.0, 1.0, 1.08), g)
        kit.box(f"h{n}.flag", (0.36, 0.015, 0.23), (0.19, 0, 0), pond, cloth)
        text(kit, f"h{n}.fn", str(n), (0.2, -0.012, 0.0), 0.15, flagt, parent=cloth)
        wrap = kit.empty(f"h{n}.wrap", (0.0, 1.0, 1.08), g)
        kit.cyl(f"h{n}.wc", 0.05, 0.23, (0, 0, 0), pond, wrap, n=10)
        kit.cyl(f"h{n}.wd1", 0.08, 0.02, (0, 0, 0.12), pond, wrap, n=10)
        kit.cyl(f"h{n}.wd2", 0.08, 0.02, (0, 0, -0.12), pond, wrap, n=10)
        wrap.hide_render = True
        W["holes"][n] = {"cloth": cloth, "wrap": wrap, "g": g}
        # mesh fence round the hole: four panels on concrete feet
        panels = []
        mm = mesh_mat(kit)
        for k, (px, py, rz) in enumerate([(0, -1.9, 0), (0, 1.9, 0), (-1.9, 0, 90), (1.9, 0, 90)]):
            p = kit.empty(f"h{n}.fp{k}", (hx + px, hy + py, 0), rot=(0, 0, rz * D2R))
            kit.box(f"h{n}.fpm{k}", (3.5, 0.03, 1.9), (0, 0, 1.05), mm, p)
            kit.box(f"h{n}.fpt{k}", (3.5, 0.05, 0.05), (0, 0, 2.0), iron, p)
            for sx in (-1.6, 1.6):
                kit.box(f"h{n}.fpf{k}{sx}", (0.18, 0.5, 0.22), (sx, 0, 0.11), kit.concrete("#8d8d88", 2.0, 0.2,
                                                                                         "foot"), p)
            p.hide_render = True
            panels.append(p)
            for c in p.children_recursive:
                c.hide_render = True
        W["fence"][n] = panels

    # hole features: pond and bridge (hole 3), tunnel hill (hole 5), castle gate (hole 8), ramp (hole 12)
    def hole_xy(n):
        return next((x, y) for k, x, y in G.HOLES if k == n)

    px, py = hole_xy(3)
    pn = kit.cyl("pond", 0.9, 0.02, (px, py + 0.2, 0.07), water, n=24)
    pn.scale = (1.0, 0.65, 1.0)
    for i in range(7):
        a = i / 6.0
        kit.box(f"bridge{i}", (0.25, 0.7, 0.07), (px - 0.75 + a * 1.5, py + 0.2, 0.12 + 0.28 * math.sin(a * math.pi)),
                timber, rot=(0, 0.6 * math.cos(a * math.pi), 0))
    hx_, hy_ = hole_xy(5)
    hill = kit.sphere("hill", 1.1, (hx_, hy_ + 0.3, 0.0), kit.plastic("#4e8d3c", 0.9), seg=14)
    hill.scale = (1.3, 1.0, 0.8)
    kit.box("tunnel", (0.55, 0.3, 0.6), (hx_, hy_ - 0.65, 0.4), plastic("#0a0c0a", 0.9))
    cx8, cy8 = hole_xy(8)
    for k in range(5):
        kit.box(f"castle{k}", (0.32, 0.4, 0.9 if k % 2 == 0 else 0.75), (cx8 - 0.65 + k * 0.325, cy8 + 0.2, 0.52),
                stone, bevel=0.02)
    kit.box("castle.arch", (0.5, 0.42, 0.55), (cx8, cy8 + 0.2, 0.34), plastic("#15171a", 0.9))
    rx, ry = hole_xy(12)
    kit.box("ramp", (1.2, 1.8, 0.1), (rx, ry, 0.25), timber, rot=(0.25, 0, 0))

    # ------------------------------------------------------------------------------------ the last green
    lg = kit.empty("lastgreen", (0, 0, 0))
    x0, x1, y0, y1 = G.LAST["x0"], G.LAST["x1"], G.LAST["y0"], G.LAST["y1"]
    kit.box("last.turf", (x1 - x0, y1 - y0, 0.06), (0, (y0 + y1) / 2, 0.05), turf, lg)
    for sx in (x0 - 0.06, x1 + 0.06):
        kit.box(f"last.e{sx}", (0.12, y1 - y0 + 0.24, 0.14), (sx, (y0 + y1) / 2, 0.09), timber, lg)
    for sy in (y0 - 0.06, y1 + 0.06):
        kit.box(f"last.f{sy}", (x1 - x0 + 0.24, 0.12, 0.14), (0, sy, 0.09), timber, lg)
    for i, (tx, ty) in enumerate((G.TEE_L, G.TEE_R)):
        kit.box(f"tee{i}", (1.1, 1.6, 0.03), (tx, ty, 0.085), tee_mat, lg, bevel=0.01)
        W[f"tee{i}"] = (tx, ty)
    # the cup: an iron rim, a dark hole, two upright strokes on the near side of the rim (lore)
    cux, cuy = G.CUP
    kit.cyl("cup.rim", 0.14, 0.03, (cux, cuy, 0.085), iron, lg, n=20)
    kit.cyl("cup.hole", 0.105, 0.035, (cux, cuy, 0.09), plastic("#050507", 0.5), lg, n=20)
    W["cup_strokes"] = kit.empty("cup.strokes", (cux, cuy - 0.125, 0.104), lg)
    for k, dx in enumerate((-0.03, 0.03)):
        kit.box(f"cup.s{k}", (0.012, 0.03, 0.004), (dx, 0, 0), pond, W["cup_strokes"])
    kit.cyl("cup.pole", 0.013, 1.2, (cux, cuy + 0.1, 0.7), white, lg, n=8)
    n = 18
    cloth = kit.empty("h18.cloth", (cux, cuy + 0.1, 1.18), lg)
    kit.box("h18.flag", (0.4, 0.015, 0.26), (0.21, 0, 0), pond, cloth)
    text(kit, "h18.fn", "18", (0.22, -0.012, 0.0), 0.16, flagt, parent=cloth)
    wrap = kit.empty("h18.wrap", (cux, cuy + 0.1, 1.18), lg)
    kit.cyl("h18.wc", 0.055, 0.26, (0, 0, 0), pond, wrap, n=10)
    wrap.hide_render = True
    W["holes"][18] = {"cloth": cloth, "wrap": wrap}
    # a flag by the second tee, wound one more turn on cue
    ft = kit.empty("teeflag.pole", (1.9, 19.2, 0), lg)
    kit.cyl("teeflag.p", 0.013, 1.1, (0, 0, 0.6), white, ft, n=8)
    cloth = kit.empty("teeflag.cloth", (1.9, 19.2, 1.08), lg)
    kit.box("teeflag.flag", (0.36, 0.015, 0.23), (0.19, 0, 0), pond, cloth)
    wrap = kit.empty("teeflag.wrap", (1.9, 19.2, 1.08), lg)
    kit.cyl("teeflag.wc", 0.05, 0.23, (0, 0, 0), pond, wrap, n=10)
    kit.cyl("teeflag.wd", 0.085, 0.02, (0, 0, 0.12), pond, wrap, n=10)
    kit.cyl("teeflag.wd2", 0.085, 0.02, (0, 0, -0.12), pond, wrap, n=10)
    kit.cyl("teeflag.wt", 0.07, 0.03, (0, 0, 0.0), white, wrap, n=10)
    wrap.hide_render = True
    W["holes"][19] = {"cloth": cloth, "wrap": wrap}
    # the bench (pond green), facing -x, and the lamp post
    bx_, by_ = G.BENCH
    W["bench"] = bench(kit, "bench", (bx_, by_, 0), -90, pond, timber)
    lx, ly = G.LAMP
    kit.cyl("lamppost", 0.06, 3.0, (lx, ly, 1.5), iron, n=10)
    kit.box("lamphead", (0.4, 0.4, 0.3), (lx - 0.1, ly, 3.1), plastic("#ffcf90", 0.3), bevel=0.04)
    kit.box("lamparm", (0.3, 0.06, 0.06), (lx - 0.1, ly, 3.0), iron)
    # string lights round the last hole's fence: bulbs on the fence line, fading on by cue
    W["bulbs"] = []
    W["bulb_objs"] = []
    for i, (sx, sy) in enumerate([(x, 31.2) for x in (-3.0, -1.5, 0.0, 1.5, 3.0)] +
                                 [(x1 + 0.5, y) for y in (21, 23, 25, 27, 29)] +
                                 [(x0 - 0.5, y) for y in (21, 23, 25, 27, 29)]):
        mat = kit.emit("#ffc070", 0.0, f"bulb{i}")
        W["bulb_objs"].append(kit.sphere(f"bulb{i}", 0.06, (sx, sy, 2.2), mat, seg=8))
        W["bulbs"].append(mat)
    # last-hole fence (appears Friday): panels round the lot, with the gap by the tees
    W["lastfence"] = []
    mm = mesh_mat(kit)
    conc = kit.concrete("#8d8d88", 2.0, 0.2, "foot")
    segs = [((-3.85, 25.0), 90, 12.4), ((3.85, 25.0), 90, 12.4), ((0, 31.6), 0, 8.0),
            ((-2.6, 18.4), 0, 2.4), ((2.6, 18.4), 0, 2.4)]
    for k, (pos, rz, ln) in enumerate(segs):
        p = kit.empty(f"lf{k}", (pos[0], pos[1], 0), rot=(0, 0, rz * D2R))
        kit.box(f"lf{k}.m", (ln, 0.03, 1.9), (0, 0, 1.05), mm, p)
        kit.box(f"lf{k}.t", (ln, 0.05, 0.05), (0, 0, 2.0), iron, p)
        for j in range(int(ln // 3) + 1):
            kit.box(f"lf{k}.f{j}", (0.18, 0.5, 0.22), (-ln / 2 + 0.2 + j * 3.0, 0, 0.11), conc, p)
        p.hide_render = True
        for c in p.children_recursive:
            c.hide_render = True
        W["lastfence"].append(p)

    # props: putters, flask, balls, survey post
    W["props"] = {}
    for nm in ("putter1", "putter2", "putter3"):
        W["props"][nm] = putter(kit, nm, plastic("#b8bcc0", 0.3, spec=0.8), plastic("#3a3d44", 0.4))
    fl = kit.empty("flask", (0, 0, -50))
    kit.cyl("flask.b", 0.05, 0.16, (0, 0, 0.08), kit.metal("#b8bcc0", 0.3), fl, n=12)
    kit.cyl("flask.n", 0.025, 0.03, (0, 0, 0.175), kit.metal("#b8bcc0", 0.3), fl, n=10)
    W["props"]["flask"] = fl
    fll = kit.empty("flask_lid", (0, 0, -50))
    kit.cyl("flask.lid", 0.03, 0.03, (0, 0, 0.015), plastic("#2a2a30", 0.5), fll, n=10)
    W["props"]["flask_lid"] = fll
    for nm in ("ball1", "ball2", "ball3"):
        b = kit.sphere(nm, 0.045, (0, 0, -50), plastic("#fafafa", 0.35, spec=0.7), seg=10)
        W["props"][nm] = b
    sp = kit.empty("survey", (0, 0, -50))
    kit.box("survey.p", (0.05, 0.05, 1.1), (0, 0, 0.55), plastic("#d8d0b0", 0.7), sp)
    kit.box("survey.t", (0.07, 0.07, 0.1), (0, 0, 1.12), plastic("#e8a030", 0.6), sp)
    W["props"]["survey"] = sp
    tray = kit.box("panel_a", (3.5, 0.03, 1.9), (0, 0, -50), mesh_mat(kit))
    W["props"]["panel_a"] = tray
    W["props"]["panel_b"] = kit.box("panel_b", (3.5, 0.03, 1.9), (0, 0, -50), mesh_mat(kit))

    # windmill: white tower, cap, four pond-green sails turning on a hub, facing -y
    wx, wy = G.WINDMILL
    kit.cyl("wm.tower", 1.15, 3.6, (wx, wy, 1.8), white, n=16, r2=0.8)
    kit.cyl("wm.cap", 0.85, 0.6, (wx, wy, 3.85), pond, n=16, r2=0.3)
    kit.box("wm.door", (0.6, 0.1, 1.1), (wx, wy - 1.1, 0.55), pond, bevel=0.02)
    hub = kit.empty("wm.hub", (wx, wy - 1.0, 3.4))
    W["sails"] = kit.empty("wm.sails", (0, 0, 0), hub)
    kit.cyl("wm.axle", 0.12, 0.5, (0, 0.2, 0), iron, W["sails"], rot=(math.pi / 2, 0, 0), n=10)
    for k in range(4):
        arm = kit.empty(f"wm.arm{k}", (0, 0, 0), W["sails"], rot=(0, k * math.pi / 2, 0))
        kit.box(f"wm.spar{k}", (0.12, 0.1, 3.0), (0, 0, 1.5), timber, arm, bevel=0.02)
        kit.box(f"wm.sail{k}", (0.8, 0.06, 2.1), (0.45, -0.04, 1.75), pond, arm, bevel=0.01)
        for j in range(4):
            kit.box(f"wm.lat{k}{j}", (0.8, 0.07, 0.07), (0.45, -0.08, 0.9 + j * 0.55), white, arm)

    # trees round the park
    for i, (tx, ty, h) in enumerate([(-17, 6, 5), (17, 10, 6), (-16, 22, 5.5), (18, 26, 6), (-20, -20, 6.5),
                                     (14, -22, 5.5), (-8, -26, 6), (4, -30, 5), (26, -10, 6), (-30, -12, 6),
                                     (16, 34, 6), (-14, 36, 6), (-45, -50, 6), (-30, -48, 5.5), (-52, -30, 6.2)]):
        tree(kit, f"tree{i}", tx, ty, h, dark=i % 2 == 0)

    # the ex's front door and step, a low rail by a pitch, the pitch
    ex, ey = G.EX_DOOR
    kit.box("ex.wall", (6.0, 0.3, 3.2), (ex, ey + 0.15, 1.6), plastic("#c9b49a", 0.8))
    kit.box("ex.door", (1.0, 0.06, 2.1), (ex, ey - 0.02, 1.05), plastic("#6b2f3a", 0.6), bevel=0.01)
    kit.box("ex.step", (1.6, 0.9, 0.18), (ex, ey - 0.45, 0.09), plastic("#9c9892", 0.8), bevel=0.02)
    kit.box("ex.win0", (1.0, 0.04, 1.1), (ex - 2.0, ey - 0.02, 1.8), plastic("#aab9c9", 0.2))
    kit.box("ex.win1", (1.0, 0.04, 1.1), (ex + 2.0, ey - 0.02, 1.8), plastic("#aab9c9", 0.2))
    pxx, pyy = G.PITCH
    kit.plane("pitch", (24, 14), (pxx, pyy, 0.015), kit.grime("#5aa044", 0.88, 2.0, "pitch", 0.95))
    for nm, sz, loc in (("pl.n", (24, 0.1), (pxx, pyy + 7, 0.02)), ("pl.s", (24, 0.1), (pxx, pyy - 7, 0.02)),
                        ("pl.e", (0.1, 14), (pxx + 12, pyy, 0.02)), ("pl.w", (0.1, 14), (pxx - 12, pyy, 0.02)),
                        ("pl.m", (0.1, 14), (pxx, pyy, 0.02))):
        kit.plane(nm, sz, loc, white)
    kit.cyl("pl.c", 1.6, 0.003, (pxx, pyy, 0.021), white, n=28)
    kit.cyl("pl.ci", 1.5, 0.004, (pxx, pyy, 0.022), kit.MATS["pitch"], n=28)
    lrx, lry = G.LAWN_RAIL
    kit.box("lrail.top", (8.0, 0.08, 0.08), (lrx, lry, 1.0), timber)
    kit.box("lrail.mid", (8.0, 0.08, 0.08), (lrx, lry, 0.6), timber)
    for i in range(5):
        kit.box(f"lrail.p{i}", (0.1, 0.1, 1.05), (lrx - 4 + i * 2.0, lry, 0.52), timber)

    kit.plane("path", (2.4, 50.0), (-6.0, -38.0, 0.012), grey)
    bench(kit, "lawnbench", (-4.3, -25.6, 0.0), -90, timber, timber)

    # ------------------------------------------------------------------------------------ Dad's house
    hx0, hy0 = G.HOUSE
    house = brick
    hw, hd, hh = 9.0, 6.0, 4.6
    for nm, size, loc in (
        ("house.back", (hw, 0.3, hh), (hx0, hy0 + hd, hh / 2)),
        ("house.w", (0.3, hd, hh), (hx0 - hw / 2, hy0 + hd / 2, hh / 2)),
        ("house.e", (0.3, hd, hh), (hx0 + hw / 2, hy0 + hd / 2, hh / 2)),
        ("house.floor", (hw, hd, 0.2), (hx0, hy0 + hd / 2, 0.1)),
        ("house.ceil", (hw, hd, 0.2), (hx0, hy0 + hd / 2, 2.9)),
        ("house.roof", (hw + 0.6, hd + 0.8, 0.25), (hx0, hy0 + hd / 2, hh + 0.12)),
    ):
        kit.box(nm, size, loc, house if "roof" not in nm else plastic("#4b4a52", 0.8))
    # front: door at x = hx0-1.3..hx0-0.3 and windows at hx0+1.3 (bedroom) and hx0+3.2
    # simpler: build the front wall from strips
    front = [(hx0 - 4.5, hx0 - 1.3), (hx0 - 0.3, hx0 + 0.9), (hx0 + 1.9, hx0 + 4.5)]
    for i, (a, b) in enumerate(front):
        kit.box(f"house.fw{i}", (b - a, 0.3, hh), ((a + b) / 2, hy0, hh / 2), house)
    kit.box("house.fwtop", (9.0, 0.3, hh - 2.2), (hx0, hy0, (hh + 2.2) / 2), house)
    kit.box("house.fwsill", (1.0, 0.3, 1.0), (hx0 + 1.4, hy0, 0.5), house)
    kit.box("house.fwsill2", (1.0, 0.3, 1.0), (hx0 + 3.2 - 0.0, hy0, 0.5), house)
    kit.box("house.step", (1.4, 0.8, 0.15), (hx0 - 0.8, hy0 - 0.5, 0.075), plastic("#9c9892", 0.8))
    wm = kit.emit("#ffcf90", 0.0, "windowglow")
    kit.box("house.win", (0.9, 0.05, 1.2), (hx0 + 1.4, hy0 + 0.1, 1.6), wm)
    W["winmat"] = wm
    kit.box("house.frame", (1.05, 0.07, 1.35), (hx0 + 1.4, hy0 + 0.13, 1.6), plastic("#efe2c4", 0.6))
    W["winpane"] = kit.box("house.pane2", (0.9, 0.05, 1.2), (hx0 + 3.2 - 0.0, hy0 + 0.1, 1.6), plastic("#7f93aa", 0.2))
    # the front door, hinged on its +x edge, opening outward (-y)
    hinge = kit.empty("door.hinge", (hx0 - 0.3, hy0 - 0.02, 0))
    kit.box("door.leaf", (1.0, 0.06, 2.1), (-0.5, 0, 1.05),
            plastic("#2f4a6a", 0.6), hinge, bevel=0.01)
    W["door"] = hinge
    kit.box("house.hall.inner", (hw - 0.6, 0.02, hh - 1.0), (hx0, hy0 + hd - 0.2, 1.8), plastic("#d9c6a0", 0.8))
    bnch = bench(kit, "housebench", (G.BENCH_HOUSE[0], G.BENCH_HOUSE[1], 0), 0, pond, timber)
    dew = kit.plastic("#dfe8f0", 0.1, spec=1.0)
    for k in range(22):
        sx_ = -0.36 + 0.72 * ((k * 7) % 11) / 10.0
        kit.sphere(f"dew{k}", 0.014, (G.BENCH_HOUSE[0] + sx_, G.BENCH_HOUSE[1] - 0.02 - 0.08 * ((k * 3) % 4) / 3,
                                      1.15 - 0.03 * (k % 3) - (0.0 if abs(sx_) > 0.2 else 0.0)), dew, seg=6)

    # ------------------------------------------------------------------------------------ interior rooms
    def room(name, cx_, cy_, w, d, h, wallc, floorc, ceil=True, skip=(), gap_s=0.0):
        wm_ = plastic(wallc, 0.85)
        fm = kit.planks(floorc, "#4e3520", 1.0) if hasattr(kit, "planks") else plastic(floorc, 0.8)
        kit.box(f"{name}.floor", (w, d, 0.1), (cx_, cy_, -0.05), fm)
        if ceil:
            kit.box(f"{name}.ceil", (w, d, 0.1), (cx_, cy_, h + 0.05), wm_)
        if "n" not in skip:
            kit.box(f"{name}.n", (w, 0.1, h), (cx_, cy_ + d / 2, h / 2), wm_)
        if gap_s:
            sw = (w - gap_s) / 2
            for sx in (-1, 1):
                kit.box(f"{name}.s{sx}", (sw, 0.1, h), (cx_ + sx * (gap_s + sw) / 2, cy_ - d / 2, h / 2), wm_)
            kit.box(f"{name}.sl", (gap_s, 0.1, h - 2.1), (cx_, cy_ - d / 2, (h + 2.1) / 2), wm_)
        else:
            kit.box(f"{name}.s", (w, 0.1, h), (cx_, cy_ - d / 2, h / 2), wm_)
        kit.box(f"{name}.e", (0.1, d, h), (cx_ + w / 2, cy_, h / 2), wm_)
        kit.box(f"{name}.w", (0.1, d, h), (cx_ - w / 2, cy_, h / 2), wm_)

    ax, ay = G.ROOM_A
    room("roomA", ax, ay, 4.0, 4.4, 2.6, "#c9b6a0", "#6b4a2e")
    blanket = plastic("#7a8ec0", 0.9)
    kit.box("bedA.frame", (1.4, 2.0, 0.35), (ax + 1.2, ay + 1.1, 0.18), timber)
    kit.box("bedA.mat", (1.3, 1.9, 0.2), (ax + 1.2, ay + 1.1, 0.45), plastic("#f1ece0", 0.9))
    kit.box("bedA.blanket", (1.3, 1.2, 0.12), (ax + 1.2, ay + 0.9, 0.58), blanket, bevel=0.03)
    kit.box("bedA.pillow", (0.7, 0.4, 0.14), (ax + 1.2, ay + 1.85, 0.6), white, bevel=0.05)
    kit.box("lampA.table", (0.5, 0.5, 0.5), (ax - 0.4, ay + 1.9, 0.25), timber)
    kit.sphere("lampA.bulb", 0.12, (ax - 0.4, ay + 1.9, 0.62), kit.emit("#ffcf90", 6.0, "lampAglow"), seg=10)
    kit.box("windowA", (1.0, 0.04, 1.0), (ax, ay + 2.17, 1.5), kit.emit("#3b4a7a", 1.2, "winA"))
    bx, by = G.ROOM_B
    room("roomB", bx, by, 4.0, 4.0, 2.6, "#cdbfa8", "#6b4a2e", gap_s=1.0)
    room("hallB", bx, by - 3.5, 3.0, 3.0, 2.6, "#bfae98", "#6b4a2e", skip=("n",))
    kit.box("bedB.frame", (1.6, 2.1, 0.35), (bx + 1.2, by + 0.6, 0.18), timber)
    kit.box("bedB.mat", (1.5, 2.0, 0.2), (bx + 1.2, by + 0.6, 0.45), plastic("#f1ece0", 0.9))
    kit.box("bedB.quilt", (1.5, 1.5, 0.12), (bx + 1.2, by + 0.35, 0.58), plastic("#4a5f8f", 0.9), bevel=0.03)
    kit.box("bedB.pillow", (0.8, 0.4, 0.14), (bx + 1.2, by + 1.45, 0.6), white, bevel=0.05)
    kit.box("windowB", (1.1, 0.04, 1.2), (bx + 1.0, by + 2.02, 1.5), kit.emit("#7c92d0", 2.0, "winB"))
    # the door between the hall and the room (south wall opening is faked by two wall panels and a gap)
    dl = kit.empty("doorB.hinge", (bx + 0.5, by - 2.0, 0), rot=(0, 0, -55 * D2R))
    kit.box("doorB.leaf", (1.0, 0.05, 2.05), (-0.5, 0, 1.03), plastic("#efe2c4", 0.6), dl)
    cx, cy = G.ROOM_C
    room("roomC", cx, cy, 4.4, 4.0, 2.6, "#d8c9a4", "#7a5a3a")
    kit.box("kit.table", (1.4, 0.9, 0.75), (cx, cy + 0.2, 0.38), timber)
    for sx in (-1, 1):
        kit.box(f"kit.chair{sx}", (0.45, 0.45, 0.45), (cx + sx * 1.0, cy + 0.2, 0.23), timber)
    kit.box("kit.door", (1.0, 0.1, 2.0), (cx + 1.7, cy + 1.95, 1.0), plastic("#2f4a6a", 0.6))
    kit.box("kit.counter", (3.0, 0.6, 0.9), (cx - 0.4, cy + 1.7, 0.45), plastic("#b9b29a", 0.7))
    kit.sphere("kit.lamp", 0.14, (cx, cy + 0.2, 1.65), kit.emit("#ffcf90", 6.0, "kitglow"), seg=10)

    # ------------------------------------------------------------------------------------ shadows (flat)
    W["figs"] = {}
    for fid, (pose, bun) in story.get("figs", {}).items():
        W["figs"][fid] = flat_fig(kit, f"fig_{fid}", pose, bun)
    W["myshadow"] = flat_fig(kit, "fig_mine", "stand", False)
    W["wrung"] = Wrung(kit)
    W["inited"] = False
    ctx["W"] = W
    return ctx


# ---------------------------------------------------------------------------------------------- animation
def _first_frame(kit, story, tl):
    """Once, after the cast exists: no body casts a shadow, and Dad gets his grey moustache."""
    names = tuple(story.get("cast", {}))
    for ob in bpy.data.objects:
        if ob.name.split(".")[0] in names:
            ob.visible_shadow = False
    hg = bpy.data.objects.get("dad.headg")
    if hg is not None:
        m = kit.plastic("#8d8d92", 0.8)
        mo = kit.box("dad.stache", (0.52, 0.06, 0.1), (0, -0.62 - 0.02, -0.22), m, hg, bevel=0.03)
        mo.visible_shadow = False
    W["inited"] = True


def _state_sun(look):
    az = look["az"] * D2R
    el = look["el"] * D2R
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    return d


def animate(kit, story, tl, t, ctx):
    from blocky import acting
    if not W.get("inited"):
        _first_frame(kit, story, tl)
    look = look_at(tl, t)
    gains = {}
    # sun
    d = _state_sun(look)
    so = kit.LIGHTS["sun"]["obj"]
    so.location = d * 60
    kit.aim(so, (0, 0, 0))
    kit.LIGHTS["sun"]["light"].color = look["sun_col"]
    gains["sun"] = look["sun"]
    gains["fill"] = look["fill"]
    gains["moon"] = look["moon"]
    gains["lamp"] = look["lamp"] * 90.0
    for i in range(5):
        gains[f"str{i}"] = look["strings"] * 18.0
    gains["tee"] = look["tee"] * 70.0
    gains["rim"] = look["rim"] * 160.0
    gains["bed"] = look["bed"] * 140.0
    gains["hall"] = look["hall"] * 110.0
    gains["dadroom"] = look["dadroom"] * 320.0
    gains["hallB"] = look["dadroom"] * 90.0
    gains["kitchen"] = look["kitchen"] * 220.0
    # the world
    w = bpy.context.scene.world
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*look["sky"], 1.0)
    bg.inputs["Strength"].default_value = look["sky_str"]
    # string bulbs glow
    for ob in W["bulb_objs"]:
        ob.hide_render = look["strings"] < 0.02
    for m in W["bulbs"]:
        for n in m.node_tree.nodes:
            if n.type == "EMISSION":
                n.inputs["Strength"].default_value = look["strings"] * 6.0
    for n in W["winmat"].node_tree.nodes:
        if n.type == "EMISSION":
            n.inputs["Strength"].default_value = look["win"] * 4.0
    # the gate, the door, the sails
    g = _gate(tl, t)
    for hinge, sx in W["gate"]:
        hinge.rotation_euler = (0, 0, sx * g * 100 * D2R * -1)
    cues = [c for c in tl["cues"] if c["name"] == "door"]
    dv, _ = sample(cues, t, ["open"], {"open": 0.0})
    W["door"].rotation_euler = (0, 0, dv["open"] * 80 * D2R)
    W["sails"].rotation_euler = (0, _sails(tl, t) * D2R, 0)
    # fences
    fc = [c for c in tl["cues"] if c["name"] == "fenced"]
    last = last_cue(fc, t)
    nf = last["n"] if last else 0
    for n, panels in W["fence"].items():
        for p in panels:
            vis = n <= nf
            p.hide_render = not vis
            for c in p.children_recursive:
                c.hide_render = not vis
    lc = last_cue([c for c in tl["cues"] if c["name"] == "lastfence"], t)
    on = bool(lc and lc.get("on", True))
    for p in W["lastfence"]:
        p.hide_render = not on
        for c in p.children_recursive:
            c.hide_render = not on
    # flags
    for n, h in W["holes"].items():
        key = n
        cues = [c for c in tl["cues"] if c["name"] == "flag" and c.get("which") in ("all", n, "row3", "row", "near")]
        wound = 0.0
        for c in cues:
            if c["t"] > t:
                break
            wch = c.get("which")
            if wch == "all" or wch == n or (wch == "row3" and n in (13, 14, 15)) or (wch == "row" and n in (1, 2, 3)) \
                    or (wch == "near" and n == 19):
                wound = c.get("wound", 1)
        h["cloth"].hide_render = wound > 0
        for c in h["cloth"].children_recursive:
            c.hide_render = wound > 0
        h["wrap"].hide_render = wound <= 0
        for c in h["wrap"].children_recursive:
            c.hide_render = wound <= 0
        sc = 1.0 + 0.3 * max(0, wound - 1)
        h["wrap"].scale = (sc, sc, 1.0)
    # objects (props, shadows): "obj" cues with an id, a position, a yaw, an optional glide and "hide"
    objs = dict(W["props"])
    objs.update({f"fig_{k}": v for k, v in W["figs"].items()})
    objs["panel_a"] = W["props"]["panel_a"]
    tracks = _track(tl, "obj")
    for oid, cues in tracks.items():
        ob = objs.get(oid)
        if ob is None:
            continue
        v, c = sample(cues, t, ["pos", "yaw", "rot", "scale"],
                      {"pos": [0, 0, -50], "yaw": 0.0, "rot": [0, 0, 0], "scale": 1.0})
        hide = bool(c and c.get("hide"))
        ob.location = (v["pos"][0], v["pos"][1], v["pos"][2] if len(v["pos"]) > 2 else 0.0) if not hide else (0, 0, -50)
        ob.rotation_euler = (v["rot"][0] * D2R, v["rot"][1] * D2R, v["yaw"] * D2R) if oid.startswith(("putter", "panel", "flask", "ball", "survey", "fig_")) else ob.rotation_euler
        if oid.startswith("fig_"):
            s = v["scale"]
            ob.scale = (s, s, 1.0)
    # my shadow follows my feet, lying away from the sun
    st = acting.state(tl, "me", t, 0)
    shown = look["myshadow"] > 0.01 and not st["hidden"] and st["x"] < 100
    ms = W["myshadow"]
    if shown:
        away = Vector((-d.x, -d.y, 0)).normalized() if (d.x or d.y) else Vector((0, -1, 0))
        ang = math.atan2(away.x, -away.y)           # rotate the +y-pointing figure to point along `away`
        ms.location = (st["x"], st["y"], st["z"])
        ms.rotation_euler = (0, 0, math.atan2(-away.x, away.y))
        ms.scale = (1.0, 1.0, 1.0)
    else:
        ms.location = (0, 0, -50)
    # the Wrung One
    wr = W["wrung"]
    cues = [c for c in tl["cues"] if c["name"] == "wring"]
    v, c = sample(cues, t, ["pos", "yaw", "wring", "lean", "head_extra"],
                  {"pos": [0, 0], "yaw": 180.0, "wring": 180.0, "lean": [0.0, 0.0], "head_extra": 0.0})
    hid = (c is None) or bool(c.get("hide"))
    wr.pose(v["pos"], v["yaw"], v["wring"], v["lean"], hid, v["head_extra"])
    # who sits: legs straight out forward, hips on the seat
    for cue_ in [c for c in tl["cues"] if c["name"] == "sit"]:
        pass
    sit_tracks = _track(tl, "sit", lambda c: c["who"])
    for who, cs in sit_tracks.items():
        lc2 = last_cue(cs, t)
        root = bpy.data.objects.get(who)
        if lc2 and lc2.get("on") and root is not None:
            root.location.z += lc2.get("z", 0.46) - 0.68
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg:
                    leg.rotation_euler = (-math.pi / 2 * 0.97, 0, 0)
    return gains


def _gate(tl, t):
    cues = [c for c in tl["cues"] if c["name"] == "gate"]
    v, _ = sample(cues, t, ["open"], {"open": 0.0})
    return v["open"]


def _sails(tl, t):
    """Sail angle in degrees: the integral of the cues' rates (deg/s, negative = backwards)."""
    cues = sorted([c for c in tl["cues"] if c["name"] == "sails"], key=lambda c: c["t"])
    ang, rate, t0 = 0.0, 8.0, 0.0
    for c in cues:
        if c["t"] >= t:
            break
        ang += rate * (c["t"] - t0)
        rate, t0 = c["rate"], c["t"]
    return ang + rate * (t - t0)
