"""every-lock: a bright four-floor apartment building where closing a door doubles its locks.

Places (metres, floor z = 0, a character with yaw 0 faces -y, yaw 90 faces +x, yaw 180 faces +y):
  H   our inner hall, x -0.9..0.9, y 0..7. The front door is at y 0, the bathroom doorway at y 7 (the door is the
      story's "creature": one group, posed by its lock count). My room is left (x < -0.9, y 3.6..7), Jade's right
      (y 3.6..7), Mom's right (y 0.2..3.4). The bathroom is behind the door (y 7..10).
  D   the building's hall, x -13..13, y -2.4..0, mint walls, terracotta floor. Mr. Dale's door is at x 0, y -2.4 and
      his hall runs south (y -2.4..-8.4) to his own bathroom doorway, set like ours.
  K   our kitchen at x 40, DK the fridge man's kitchen at x 80, ST the stairwell at x 120 (Mrs. Pike's flat to its
      west), SR the street at x 160.
The bathroom door group ("bath") has a root (placed per stage), a swing pivot at the hinge, the slab, a pool of 288
locks, a pile of 640 big locks that grows outward (cue "door": n, L, lean, swing), and a hero lock whose keyhole
flap swings by itself. Every lock arrives shut with its own brass keyhole flap.
"""
from __future__ import annotations

import hashlib
import math
import random
from pathlib import Path

import bpy
from PIL import Image, ImageDraw, ImageFont

from blocky import acting

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FONT = ROOT / "blocky" / "fonts" / "SchibstedGrotesk-Black.ttf"

P = dict(mint="#8fdcc2", terra="#d9774a", yellow="#f6c844", brass="#d9a441", chrome="#c9d1d9", sky="#8cc8f2",
         white="#f4f1ea", teal="#3fb8b0", mustard="#e3a62f", coral="#f08a6c", tan="#c8a878", walk="#cfcac0",
         amber="#ffb21f", dark="#2a2420")
H_HALF = 0.9           # half the width of both inner halls
WALL_H = 2.6
DOOR_W, DOOR_H = 0.9, 2.05
SLAB_T = 0.05
POOL_N = 288
PILE_N = 640
PILE_MAX = 5.0
K0, DK0, ST0, SR0 = 40.0, 80.0, 120.0, 160.0


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def workdir(tl) -> Path:
    d = ROOT / "out" / "work" / tl.get("name", "every-lock") / "meter"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ------------------------------------------------------------------------------------------ cue tracks


def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def track(cs, key, t, default):
    """A numeric (or tuple) value that eases from one cue's value to the next over its `dur`."""
    v = default
    for c in sorted(cs, key=lambda c: c["t"]):
        if key not in c:
            continue
        nv = c[key]
        d = float(c.get("dur", 0.0))
        if t >= c["t"] + d:
            v = nv
        elif t > c["t"]:
            u = ss((t - c["t"]) / d)
            return _lerp(v, nv, u)
        else:
            break
    return v


def _lerp(a, b, u):
    if isinstance(a, (list, tuple)):
        return tuple(x + (y - x) * u for x, y in zip(a, b))
    return a + (b - a) * u


def last(cs, t):
    cs = [c for c in cs if c["t"] <= t + 1e-9]
    return cs[-1] if cs else None


# ------------------------------------------------------------------------------------------ materials


def mats(kit):
    M = {}
    pm = lambda h, r=0.5: kit.plastic(h, r, name=f"p {h} {r}")
    for k, h in P.items():
        M[k] = pm(h)
    M["trim"] = pm("#fff6e6", 0.5)
    M["dark"] = pm("#2a2420", 0.6)
    M["black"] = pm("#15110e", 0.7)
    M["flap"] = pm("#a9741f", 0.35)
    M["steel"] = kit.metal("#aab2ba", 0.35, name="steel")
    for nm, h, met, rough in (("brassm", "#d9962a", 0.85, 0.3), ("chromem", P["chrome"], 0.9, 0.2)):
        m = kit._new(nm)
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = kit.col(h)
        b.inputs["Metallic"].default_value = met
        b.inputs["Roughness"].default_value = rough
        kit._fogged(m, b.outputs[0])
        M[nm] = m
    M["floor_wood"] = kit.texture("wood", 1.0, tint="#f1d3a8")
    M["floor_tile"] = kit.texture("concrete", 1.0, tint="#f09560")
    M["walk"] = kit.texture("concrete", 1.0, tint="#d8d4c8")
    M["asphalt"] = kit.texture("asphalt", 0.5, tint="#8a8a92")
    M["grass"] = kit.texture("grass", 1.0, tint="#a8e060")
    M["bathtile"] = pm("#bfe6f2", 0.35)
    M["cooler_r"] = pm("#e0322b", 0.4)
    M["cooler_w"] = pm("#f6f6f2", 0.4)
    M["glowwin"] = unfogged_emit(kit, "glowwin", "#cfe8ff", 3.0)
    M["moonwin"] = unfogged_emit(kit, "moonwin", "#9fbfff", 1.4)
    M["phone"] = unfogged_emit(kit, "phone", "#dff4ff", 2.0)
    M["curtain"] = kit.plastic("#f3a6c8", 0.7, name="curtain_stripe")
    M["frost"] = kit.plastic("#e6f3fa", 0.5, name="frost")
    M["steam"] = kit.plastic("#ffffff", 0.9, name="steam")
    return M


def unfogged_emit(kit, name, hexc, strength):
    m = kit._new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = kit.col(hexc)
    e.inputs["Strength"].default_value = strength
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    return m


# ------------------------------------------------------------------------------------------ builders


def bx(kit, name, size, loc, mat, parent=None, rot=(0, 0, 0), bevel=0.0):
    return kit.box(name, size, loc, mat, parent, rot, bevel)


def wall(kit, M, name, axis, c, a0, a1, h, mat=None, openings=(), t=0.12, z0=0.0):
    """A wall along `axis` ('x': at y = c, 'y': at x = c) from a0 to a1, with door openings (centre, width, height)."""
    if not isinstance(h, (int, float)):   # called without a height: wall(..., a1, mat)
        if mat is not None and not isinstance(mat, (int, float)) and openings == ():
            pass
        h, mat = WALL_H, h
    segs, cur = [], a0
    for (oc, ow, oh) in sorted(openings):
        if oc - ow / 2 > cur:
            segs.append((cur, oc - ow / 2, z0, h))
        segs.append((oc - ow / 2, oc + ow / 2, oh, h))
        cur = oc + ow / 2
    if cur < a1:
        segs.append((cur, a1, z0, h))
    out = []
    for i, (s0, s1, z0, z1) in enumerate(segs):
        sz = (s1 - s0, t, z1 - z0) if axis == "x" else (t, s1 - s0, z1 - z0)
        loc = ((s0 + s1) / 2, c, (z0 + z1) / 2) if axis == "x" else (c, (s0 + s1) / 2, (z0 + z1) / 2)
        out.append(bx(kit, f"{name} {i}", sz, loc, mat))
    return out


def frame(kit, M, name, axis, c, oc, ow, oh, mat, t=0.12):
    """Door jambs and a head, standing 2 cm proud of both faces of the wall."""
    w = 0.07
    for s in (-1, 1):
        a = oc + s * (ow / 2 + w / 2 - 0.01)
        sz = (w, t + 0.04, oh) if axis == "x" else (t + 0.04, w, oh)
        loc = (a, c, oh / 2) if axis == "x" else (c, a, oh / 2)
        bx(kit, f"{name} jamb{s}", sz, loc, mat)
    sz = (ow + 2 * w - 0.02, t + 0.04, w) if axis == "x" else (t + 0.04, ow + 2 * w - 0.02, w)
    loc = (oc, c, oh + w / 2 - 0.01) if axis == "x" else (c, oc, oh + w / 2 - 0.01)
    bx(kit, f"{name} head", sz, loc, mat)


def room_floor(kit, name, x0, x1, y0, y1, mat):
    return bx(kit, name, (x1 - x0, y1 - y0, 0.1), ((x0 + x1) / 2, (y0 + y1) / 2, -0.05), mat)


class Leaf:
    """A door leaf on a hinge pivot. It extends along the pivot's local +x; the pivot's z rotation is base + angle."""

    def __init__(self, kit, M, name, hinge, base, w, h, mat, angle=0.0, sign=1, t=0.045):
        self.base, self.sign = base, sign
        self.pivot = kit.empty(f"{name} pivot", (hinge[0], hinge[1], 0), None, (0, 0, math.radians(base + sign * angle)))
        self.slab = bx(kit, f"{name} slab", (w - 0.01, t, h - 0.02), ((w - 0.01) / 2 + 0.005, 0, h / 2), mat, self.pivot)
        self.w, self.h, self.t = w, h, t

    def set(self, angle):
        self.pivot.rotation_euler.z = math.radians(self.base + self.sign * angle)


# ------------------------------------------------------------------------------------------ locks


def make_lock(kit, M, name, kind, parent, loc, s, rot=(0, 0, 0)):
    """A chunky toy lock whose back sits on the plane y = 0 of its parent and sticks out toward -y. kind 0 brass
    box, 1 chrome barrel bolt, 2 brass deadbolt rose. Every one has a brass keyhole flap hinged at its top."""
    extras = []
    if kind == 0:
        root = kit.box(f"{name} body", (s, 0.55 * s, 0.8 * s), (0, -0.275 * s, 0), M["brassm"], parent, rot)
        extras.append(bx(kit, f"{name} kh", (0.12 * s, 0.08 * s, 0.2 * s), (0, -0.59 * s, 0.0), M["black"], root))
        yf, zt, fw, fh = -0.55 * s - 0.1 * s, 0.3 * s, 0.34 * s, 0.34 * s
    elif kind == 1:
        root = kit.box(f"{name} plate", (1.3 * s, 0.1 * s, 0.45 * s), (0, -0.05 * s, 0), M["chromem"], parent, rot)
        extras.append(kit.cyl(f"{name} barrel", 0.12 * s, 1.1 * s, (0, -0.26 * s, -0.16 * s), M["chromem"], root,
                              (0, math.pi / 2, 0), 12))
        extras.append(bx(kit, f"{name} kh", (0.1 * s, 0.07 * s, 0.14 * s), (0, -0.135 * s, 0.1 * s), M["black"], root))
        yf, zt, fw, fh = -0.13 * s - 0.03 * s, 0.2 * s, 0.3 * s, 0.22 * s
    else:
        # a disc whose axis is y: after the quarter turn its local z points toward -y and local y is up
        root = kit.cyl(f"{name} rose", 0.5 * s, 0.35 * s, (0, -0.175 * s, 0), M["brassm"], parent,
                       (math.pi / 2 + rot[0], rot[1], rot[2]), 14)
        extras.append(kit.cyl(f"{name} knob", 0.17 * s, 0.3 * s, (0, -0.2 * s, 0.325 * s), M["brassm"], root, (0, 0, 0), 10))
        yf, zt, fw, fh = -0.35 * s - 0.1 * s, 0.3 * s, 0.3 * s, 0.26 * s
    root.location = tuple(loc)
    # the flap: origin at its hinge, hangs down from it; swings out (toward -y) at a negative x angle
    v = kit.box_verts(fw, 0.06 * s, fh, (0, 0, -fh / 2))
    flap = kit.mesh_obj(f"{name} flap", v, kit.BOX_FACES, M["flap"], parent, (loc[0], loc[1] + yf, loc[2] + zt))
    flap.rotation_euler = rot
    lk = Lock(root, flap, extras, s, parent)
    lk.flap_rest = rot
    return lk


class Lock:
    def __init__(self, root, flap, extras, s, parent):
        self.root, self.flap, self.extras, self.s, self.parent = root, flap, extras, s, parent
        self.objs = [root, flap] + extras
        self.loc = tuple(root.location)
        self.flap_loc = tuple(flap.location)
        self.flap_rest = (0, 0, 0)

    def show(self, v, k=1.0):
        """v: visible; k: 0..1 pop scale (the lock's body and flap scale about the lock's own place)."""
        for o in self.objs:
            o.hide_render = not v
        if v:
            k = max(k, 1e-3)
            self.root.scale = (k, k, k)
            # the flap is parented to the door, not the lock, so it scales and moves with it by hand
            self.flap.scale = (k, k, k)
            self.flap.location = tuple(l + (f - l) * k for l, f in zip(self.loc, self.flap_loc))

    def flap_angle(self, deg):
        self.flap.rotation_euler = (math.radians(-deg), self.flap_rest[1], self.flap_rest[2])


def lock_kind(i):
    return (0, 1, 2, 0, 2, 1)[i % 6]


# ------------------------------------------------------------------------------------------ the door


def build_bath(kit, M, ctx):
    """The bathroom door group. Local frame: the wall plane is y = 0, the face of the door looks toward -y."""
    root = kit.empty("bath root", (0, 7.0, 0))
    swing = kit.empty("bath swing", (-DOOR_W / 2, 0, 0), root)
    slab = bx(kit, "bath slab", (DOOR_W - 0.01, SLAB_T, DOOR_H - 0.02), (DOOR_W / 2, 0, DOOR_H / 2), M["yellow"], swing)
    handle = kit.cyl("bath handle", 0.03, 0.12, (DOOR_W - 0.12, -0.065, 1.0), M["steel"], swing, (math.pi / 2, 0, 0), 10)
    face = -SLAB_T / 2
    rng = random.Random(11)
    pool = []
    # four hand-placed locks, then a column of four, then eight, then rows from the top
    spots = [(0.62, 1.72, 0, 1.0, 0.0), (0.38, 0.52, 0, 1.0, 9.0), (0.62, 1.2, 0, 1.0, 0.0), (0.3, 0.95, 2, 1.0, 0.0)]
    for i in range(4, 8):
        spots.append((0.74, 1.95 - (i - 4) * 0.4, lock_kind(i), 0.95, 0.0))
    for i in range(8, 16):
        spots.append((0.54, 1.95 - (i - 8) * 0.24, lock_kind(i), 0.9, 0.0))
    cols, rows = 8, 18
    cells = [(c, r) for r in range(rows) for c in range(cols)] * 2
    for i in range(16, POOL_N):
        c, r = cells[i - 16]
        layer = (i - 16) // (cols * rows)
        spots.append((0.1 + c * 0.105 + 0.02 * rng.random() - 0.0, 2.0 - r * 0.108 - 0.06, lock_kind(i), 0.82 + 0.0 * layer, 0.0,
                      -0.05 * layer))
    for i, sp in enumerate(spots):
        x, z, kind, k, tilt = sp[:5]
        dy = (sp[5] if len(sp) > 5 else 0.0) + 0.012 * rng.random()
        s = 0.1 * k * (0.9 + 0.2 * rng.random())
        lk = make_lock(kit, M, f"bl{i}", kind, swing, (x, face + dy, z), s, (0, math.radians(0), math.radians(tilt)))
        lk.show(False)
        pool.append(lk)
    # the pile: big locks budding on locks. d is the depth out from the door, x and z a spread that widens with d
    pile = []
    for i in range(PILE_N):
        near = i < 220
        d = rng.uniform(0.04, 0.40) if near else 0.40 + (PILE_MAX - 0.4) * (rng.random() ** 0.9)
        w = 0.42 + 0.46 * min(1.0, d / 1.0)
        h = DOOR_H + 0.05 + 0.4 * min(1.0, d / 1.0)
        s = (0.2 + 0.16 * rng.random()) if near else min(0.7, 0.3 + 0.1 * d + 0.25 * rng.random())
        w = max(0.1, w - 0.35 * s)
        x = DOOR_W / 2 + rng.uniform(-w, w)
        z = rng.uniform(0.12, h)
        rot = (math.radians(rng.uniform(-15, 15)), 0.0, math.radians(rng.uniform(-35, 35)))
        lk = make_lock(kit, M, f"pc{i}", i % 3, swing, (x, face - d, z), s, rot)
        lk.show(False)
        lk.d = d
        pile.append(lk)
    # the hero lock: high on the bulge, its flap swings on its own; a tiny lock grows on the flap
    hero = make_lock(kit, M, "hero", 0, swing, (0.62, face - 0.46, 1.86), 0.22)
    hero.show(False)
    tiny = make_lock(kit, M, "tiny", 0, hero.flap, (0, -0.03 * 0.22, -0.055), 0.045)
    tiny.flap.parent = hero.flap
    tiny.show(False)
    ctx["bath"] = dict(root=root, swing=swing, slab=slab, handle=handle, pool=pool, pile=pile, hero=hero, tiny=tiny)


def build_lockset(kit, M, name, parent, n, x0, x1, z0, z1, y, s, seed, cols=None):
    """A static grid of n locks on a surface (the fridge's 64, Jade's 16, the cupboard's pair)."""
    rng = random.Random(seed)
    cols = cols or max(1, int(round(math.sqrt(n * (x1 - x0) / (z1 - z0)))))
    rows = math.ceil(n / cols)
    out = []
    for i in range(n):
        c, r = i % cols, i // cols
        x = x0 + (c + 0.5) * (x1 - x0) / cols
        z = z1 - (r + 0.5) * (z1 - z0) / rows
        lk = make_lock(kit, M, f"{name}{i}", lock_kind(i + int(seed)), parent, (x, y + 0.006 * rng.random(), z),
                       s * (0.9 + 0.2 * rng.random()))
        lk.show(False)
        out.append(lk)
    return out


# ------------------------------------------------------------------------------------------ places


def build_h(kit, M, ctx):
    """Our inner hall, the rooms off it, the bathroom behind the door."""
    f = M["floor_wood"]
    room_floor(kit, "h floor", -H_HALF, H_HALF, -0.06, 7.0, f)
    room_floor(kit, "h floor L", -4.9, -H_HALF, 3.6, 7.0, f)
    room_floor(kit, "h floor R", H_HALF, 4.9, 3.6, 7.0, f)
    room_floor(kit, "h floor M", H_HALF, 4.9, 0.2, 3.4, f)
    room_floor(kit, "bath floor", -1.6, 1.6, 7.0, 10.0, M["bathtile"])
    wl = M["sky"]
    wall(kit, M, "h wallL", "y", -H_HALF, 0, 7, WALL_H, wl, [(4.55, 0.9, 2.05)])
    wall(kit, M, "h wallR", "y", H_HALF, 0, 7, WALL_H, wl, [(4.55, 0.9, 2.05), (2.45, 0.9, 2.05)])
    wall(kit, M, "h wallE", "x", 7.0, -H_HALF, H_HALF, WALL_H, wl, [(0.0, DOOR_W + 0.02, DOOR_H)])
    wall(kit, M, "h wallW", "x", 0.0, -H_HALF - 0.06, H_HALF + 0.06, WALL_H, wl, [(0.0, 1.0, 2.1)])
    frame(kit, M, "h front", "x", 0.0, 0.0, 1.0, 2.1, M["trim"])
    frame(kit, M, "h my", "y", -H_HALF, 4.55, 0.9, 2.05, M["trim"])
    frame(kit, M, "h jade", "y", H_HALF, 4.55, 0.9, 2.05, M["trim"])
    frame(kit, M, "h mom", "y", H_HALF, 2.45, 0.9, 2.05, M["trim"])
    # the bathroom frame: yellow jambs, three steel hinge plates and the tally strokes beside the top one
    t = 0.12
    for s in (-1, 1):
        bx(kit, f"bath jamb{s}", (0.07, t + 0.04, DOOR_H), (s * (DOOR_W / 2 + 0.035 - 0.005), 7.0, DOOR_H / 2), M["yellow"])
    bx(kit, "bath head", (DOOR_W + 0.14, t + 0.04, 0.07), (0, 7.0, DOOR_H + 0.035), M["yellow"])
    ctx["pins"] = []
    for i, z in enumerate((0.25, 1.0, 1.78)):
        bx(kit, f"hinge plate{i}", (0.09, 0.02, 0.2), (-DOOR_W / 2 - 0.01, 6.915, z), M["steel"])
        pin = kit.cyl(f"hinge pin{i}", 0.014, 0.2, (-DOOR_W / 2 + 0.03, 6.89, z), M["steel"], None, (0, 0, 0), 8)
        ctx["pins"].append((pin, (-DOOR_W / 2 + 0.03, 6.89, z)))
    for k in range(3):
        bx(kit, f"tally{k}", (0.006, 0.014, 0.1), (-DOOR_W / 2 - 0.035 - 0.02 * k, 6.898, 1.78), M["brassm"])
    # rooms off the hall: my room (left), Jade's, Mom's, and the bathroom
    wall(kit, M, "my wallW", "y", -4.9, 3.6, 7.0, WALL_H, wl)
    wall(kit, M, "my wallS", "x", 3.6, -4.9, -H_HALF, WALL_H, wl)
    wall(kit, M, "my wallN", "x", 7.0, -4.9, -H_HALF, WALL_H, wl)
    wall(kit, M, "jade wallE", "y", 4.9, 3.6, 7.0, WALL_H, wl)
    wall(kit, M, "jade wallS", "x", 3.6, H_HALF, 4.9, WALL_H, wl)
    wall(kit, M, "jade wallN", "x", 7.0, H_HALF, 4.9, WALL_H, wl)
    wall(kit, M, "mom wallE", "y", 4.9, 0.2, 3.4, WALL_H, wl)
    wall(kit, M, "mom wallS", "x", 0.2, H_HALF, 4.9, WALL_H, wl)
    wall(kit, M, "mom wallN", "x", 3.4, H_HALF, 4.9, WALL_H, wl)
    wall(kit, M, "h wallL2", "y", -H_HALF - 0.06, 0, 3.5, WALL_H, wl)
    wall(kit, M, "bath wallW", "y", -1.6, 7.0, 10.0, WALL_H, M["bathtile"])
    wall(kit, M, "bath wallE", "y", 1.6, 7.0, 10.0, WALL_H, M["bathtile"])
    wall(kit, M, "bath wallN", "x", 10.0, -1.6, 1.6, WALL_H, M["bathtile"])
    kit.prop("bathroom_bathtub", (1.15, 8.9, 0), rot=0, height=0.63)
    kit.prop("bathroom_sink", (-1.2, 9.4, 0), rot=90)
    kit.prop("bathroom_toilet", (0.2, 9.6, 0), rot=180)
    # beds and furniture
    kit.prop("bed_single", (-3.9, 5.6, 0), rot=0, tint="#ffd89a")
    kit.prop("nightstand_1", (-2.6, 6.55, 0))
    kit.prop("bookshelf", (-2.2, 6.75, 0), rot=0)
    kit.prop("carpet_1", (-2.6, 4.8, 0.0), rot=90)
    kit.prop("bed_single", (3.9, 5.6, 0), rot=0, tint="#a0e6e0")
    kit.prop("nightstand_1", (2.6, 6.55, 0))
    kit.prop("houseplant_1", (1.3, 6.7, 0), scale=1.4)
    kit.prop("bed_king", (3.2, 1.8, 0), rot=90, tint="#ffc0a8")
    kit.prop("houseplant_1", (1.3, 0.5, 0), scale=1.5)
    kit.prop("shelf_1", (-0.78, 1.0, 0), rot=90)
    kit.prop("light_floor1", (1.6, 6.6, 0), scale=1.4)
    # phones
    bx(kit, "phone jade", (0.07, 0.14, 0.012), (3.3, 5.2, 0.62), M["phone"])
    bx(kit, "phone me", (0.07, 0.14, 0.012), (-3.3, 5.2, 0.62), M["phone"])
    # the key bucket by the front door
    broot = kit.empty("bucket root", (-0.55, 0.55, 0))
    ctx["bucket"] = broot
    kit.cyl("bucket", 0.2, 0.34, (0, 0, 0.17), kit.metal("#9aa6b0", 0.4, name="galv"), broot, (0, 0, 0), 20)
    keys = []
    rng = random.Random(5)
    for i in range(60):
        a = rng.uniform(0, math.tau)
        r = 0.17 * math.sqrt(rng.random())
        k = bx(kit, f"key{i}", (0.07, 0.02, 0.016), (r * math.cos(a), r * math.sin(a), 0.3 + 0.04 * rng.random()),
               M["brassm"], broot, (rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), rng.uniform(0, 3)))
        keys.append(k)
    ctx["keys"] = keys
    ctx["keys_base"] = [tuple(k.location) for k in keys]
    ctx["stool"] = kit.prop("stool", (0.5, 5.7, 0))
    # doors: front (open, against the wall), mine (animated), Jade's (16 locks), Mom's (open)
    ctx["leaf_front"] = Leaf(kit, M, "front", (0.5, 0.0), 180, 1.0, 2.1, M["mint"], 85, -1)
    ctx["leaf_my"] = Leaf(kit, M, "mydoor", (-H_HALF + 0.1, 5.0), -90, 0.9, 2.05, M["white"], 170, 1)
    ctx["leaf_jade"] = Leaf(kit, M, "jadedoor", (H_HALF, 5.0), -90, 0.9, 2.05, M["white"], 60, 1)
    ctx["leaf_mom"] = Leaf(kit, M, "momdoor", (H_HALF, 2.9), -90, 0.9, 2.05, M["white"], 88, 1)
    # Jade's door carries 16 locks on the hall face; this face looks toward the hall when it stands open
    ctx["jade_locks"] = build_lockset(kit, M, "jl", ctx["leaf_jade"].slab, 16, -0.4, 0.4, -0.9, 0.9, -0.03, 0.09, 3, 4)
    for lk in ctx["jade_locks"]:
        lk.show(True)
    ctx["shoe"] = bx(kit, "shoe", (0.1, 0.26, 0.08), (0, 0, -3.0), kit.plastic("#7a4a2a", 0.5, name="p shoe"), None, (0, 0, 0), 0.02)
    ctx["mat"] = bx(kit, "camp mat", (0.7, 1.8, 0.06), (0, 0, -3.0), M["teal"])
    ctx["chair_j"] = kit.prop("chair_1", (0, 0, -3.0))
    ctx["lamp"] = kit.prop("light_floor1", (0, 0, -9.0), scale=1.4)
    kit.cyl("curtain rod", 0.015, DOOR_W + 0.1, (0, 6.85, 2.0), M["steel"], None, (0, math.pi / 2, 0), 8)
    ctx["curtain"] = []
    for i in range(10):
        x0 = -0.46 + (i + 0.5) * (DOOR_W + 0.02) / 10
        ob = bx(kit, f"curt{i}", (0.1, 0.012, 1.95), (x0, 6.85 + 0.004 * (i % 2), 1.02), M["curtain"] if i % 2 == 0 else M["white"])
        ob.hide_render = True
        ctx["curtain"].append((ob, x0))
    # lights
    L = kit.light
    L("h_a", "AREA", (0, 1.8, 2.5), 250, "#fff1d8", size=1.4)
    L("h_b", "AREA", (0, 4.6, 2.5), 250, "#fff1d8", size=1.4)
    L("h_c", "AREA", (0, 6.2, 2.4), 200, "#fff1d8", size=1.0)
    L("h_bath", "AREA", (0, 8.4, 2.4), 180, "#ffffff", size=1.0)
    L("h_my", "AREA", (-2.9, 5.2, 2.4), 120, "#fff1d8", size=1.0)
    L("h_jade", "AREA", (2.9, 5.2, 2.4), 120, "#fff1d8", size=1.0)
    L("h_mom", "AREA", (2.9, 1.8, 2.4), 120, "#fff1d8", size=1.0)
    L("h_nfill", "AREA", (0, 3.0, 2.5), 190, "#ffb86b", size=1.6)
    L("h_night", "POINT", (-0.7, 1.2, 0.35), 18, "#ffb86b", size=0.08)
    mo = L("h_moon", "AREA", (-5.4, 5.2, 1.9), 900, "#8fb0ff", size=1.6)
    kit.aim(mo, (-1.0, 5.2, 0.9))
    bx(kit, "moon window", (0.05, 0.8, 1.1), (-4.84, 5.2, 1.5), M["moonwin"])


def build_d(kit, M, ctx):
    """The building's hall, the neighbours' open doors, Mr. Dale's door and his hall."""
    room_floor(kit, "d floor", -13, 13, -2.4, 0.0, M["floor_tile"])
    openings_n = [(0.0, 1.0, 2.1), (-7.5, 1.0, 2.1), (-10.5, 1.0, 2.1), (7.5, 1.0, 2.1), (10.5, 1.0, 2.1)]
    wall(kit, M, "d wallN", "x", 0.0, -13, 13, WALL_H, M["mint"], [(oc, ow, oh) for oc, ow, oh in openings_n if oc != 0.0] + [(0.0, 1.0, 2.1)])
    openings_s = [(0.0, 1.0, 2.1), (-6.0, 1.0, 2.1), (6.0, 1.0, 2.1)]
    wall(kit, M, "d wallS", "x", -2.4, -13, 13, WALL_H, M["mint"], openings_s)
    wall(kit, M, "d end W", "y", -13, -2.4, 0, WALL_H, M["mint"])
    wall(kit, M, "d end E", "y", 13, -2.4, 0, WALL_H, M["mint"])
    for oc, _, _ in openings_n[1:]:
        frame(kit, M, f"d n{oc}", "x", 0.0, oc, 1.0, 2.1, M["trim"])
    for oc, _, _ in openings_s:
        frame(kit, M, f"d s{oc}", "x", -2.4, oc, 1.0, 2.1, M["trim"])
    # open door leaves with their props: a boot, a watering can, a brick, a rug
    ctx["dleaves"] = {}
    # neighbour doors, north wall (our side): brothers (-7.5, two locks), a family (-10.5), 7.5, 10.5
    for oc, nl in ((-7.5, 2), (-10.5, 0), (7.5, 0), (10.5, 0)):
        lf = Leaf(kit, M, f"nd{oc}", (oc + 0.5, 0.0), 180, 1.0, 2.1, M["coral"] if oc < 0 else M["teal"], 82, -1)
        if nl:
            for lk in build_lockset(kit, M, f"nl{oc}", lf.slab, nl, -0.2, 0.2, -0.3, 0.5, -0.03, 0.09, oc, 1):
                lk.show(True)
    for oc, col in ((-6.0, "#ffd36b"), (6.0, "#b6a0f0")):
        Leaf(kit, M, f"sd{oc}", (oc + 0.5, -2.4), 180, 1.0, 2.1, kit.plastic(col, 0.5, name=f"p {col}"), 82, 1)
    # props holding doors: boot, watering can, brick
    bx(kit, "boot", (0.14, 0.3, 0.26), (-6.6, -0.35, 0.13), M["dark"])
    kit.cyl("can", 0.12, 0.26, (-10.0, -0.35, 0.13), kit.plastic("#3d8bd9", 0.4, name="p can"), None, (0, 0, 0), 16)
    bx(kit, "brick", (0.22, 0.1, 0.07), (7.0, -0.4, 0.035), kit.plastic("#b5503a", 0.7, name="p brick"))
    # the neighbours' rooms (lit living rooms) behind the open doors on both walls
    for oc in (-7.5, -10.5, 7.5, 10.5):
        room_floor(kit, f"nr floor{oc}", oc - 1.6, oc + 1.6, 0.0, 4.0, M["floor_wood"])
        wall(kit, M, f"nr back{oc}", "x", 4.0, oc - 1.6, oc + 1.6, WALL_H, kit.plastic("#f4d28a" if oc < 0 else "#a8e0c8", 0.6, name=f"p nr{oc}"))
        wall(kit, M, f"nr side{oc}", "y", oc - 1.6, 0.0, 4.0, WALL_H, M["white"])
        wall(kit, M, f"nr sideb{oc}", "y", oc + 1.6, 0.0, 4.0, WALL_H, M["white"])
        kit.light(f"n{oc}", "AREA", (oc, 2.0, 2.4), 110, "#ffe6bf", size=0.9)
    for oc in (-6.0, 6.0):
        room_floor(kit, f"fr floor{oc}", oc - 1.6, oc + 1.6, -6.4, -2.4, M["floor_wood"])
        wall(kit, M, f"fr back{oc}", "x", -6.4, oc - 1.6, oc + 1.6, WALL_H, kit.plastic("#ffb8a0", 0.6, name=f"p fr{oc}"))
        wall(kit, M, f"fr side{oc}", "y", oc - 1.6, -6.4, -2.4, M["white"])
        wall(kit, M, f"fr sideb{oc}", "y", oc + 1.6, -6.4, -2.4, M["white"])
        kit.light(f"f{oc}", "AREA", (oc, -4.4, 2.4), 110, "#ffe6bf", size=0.9)
        # a round table with plates and a little steam
        kit.prop("table_roundsmall", (oc, -4.9, 0), scale=1.3)
        for k, (px, py) in enumerate(((-0.3, -0.1), (0.3, 0.1), (0.1, -0.3))):
            kit.cyl(f"plate{oc}{k}", 0.1, 0.02, (oc + px, -4.9 + py, 0.76), M["white"], None, (0, 0, 0), 14)
            kit.sphere(f"steam{oc}{k}", 0.06, (oc + px, -4.9 + py, 0.9), M["steam"], None, 8)
        kit.prop("chair_1", (oc - 0.9, -4.9, 0), rot=90)
        kit.prop("chair_2", (oc + 0.9, -4.9, 0), rot=-90)
    kit.prop("couch_medium1", (-7.5, 3.4, 0), rot=180)
    kit.prop("couch_medium1", (7.5, 3.4, 0), rot=180)
    for k in (-1, 1):
        kit.light(f"dl_hall{k}", "AREA", (k * 7.0, -1.2, 2.5), 160, "#fff1d8", size=1.4)
    for xx in (-11.0, -3.5, 3.5, 11.0):
        kit.light(f"d_a{xx}", "AREA", (xx, -1.2, 2.5), 170, "#fff1d8", size=1.4)
    kit.light("d_0", "AREA", (0, -1.2, 2.5), 200, "#fff1d8", size=1.4)
    # Mr. Dale: a front door with no locks, open, and his hall to his own bathroom (the same doorway as ours)
    ctx["leaf_dale"] = Leaf(kit, M, "daledoor", (-0.5, -2.4), 0, 1.0, 2.1, M["dark"], 85, -1)
    ctx["leaf_dale"].slab.parent = ctx["leaf_dale"].pivot
    room_floor(kit, "dale floor", -H_HALF, H_HALF, -8.4, -2.4, M["floor_wood"])
    wall(kit, M, "dale wallE", "y", H_HALF, -8.4, -2.4, WALL_H, M["tan"])
    wall(kit, M, "dale wallW", "y", -H_HALF, -8.4, -2.4, WALL_H, M["tan"], [(-4.1, 1.0, 2.1)])
    wall(kit, M, "dale wallS", "x", -8.4, -H_HALF, H_HALF, WALL_H, M["tan"], [(0.0, DOOR_W + 0.02, DOOR_H)])
    room_floor(kit, "dale living", -4.0, -H_HALF, -6.4, -2.8, M["floor_wood"])
    wall(kit, M, "dale lv S", "x", -6.4, -4.0, -H_HALF, WALL_H, M["tan"])
    wall(kit, M, "dale lv N", "x", -2.8, -4.0, -H_HALF, WALL_H, M["tan"])
    wall(kit, M, "dale lv W", "y", -4.0, -6.4, -2.8, WALL_H, M["tan"])
    room_floor(kit, "dale bath", -1.6, 1.6, -11.4, -8.4, M["bathtile"])
    wall(kit, M, "dale bath W", "y", -1.6, -11.4, -8.4, WALL_H, M["bathtile"])
    wall(kit, M, "dale bath E", "y", 1.6, -11.4, -8.4, WALL_H, M["bathtile"])
    wall(kit, M, "dale bath S", "x", -11.4, -1.6, 1.6, WALL_H, M["bathtile"])
    for s in (-1, 1):
        bx(kit, f"dale jamb{s}", (0.07, 0.16, DOOR_H), (s * (DOOR_W / 2 + 0.03), -8.4, DOOR_H / 2), M["yellow"])
    bx(kit, "dale head", (DOOR_W + 0.14, 0.16, 0.07), (0, -8.4, DOOR_H + 0.035), M["yellow"])
    frame(kit, M, "dale lvdoor", "y", -H_HALF, -4.1, 1.0, 2.1, M["trim"])
    kit.prop("light_floor1", (-3.4, -3.3, 0), scale=1.5)
    kit.prop("chair_1", (-2.3, -5.6, 0), rot=30, tint="#e07a7a")
    kit.prop("chair_2", (-3.2, -5.9, 0), rot=-40, tint="#7aa0e0")
    kit.cyl("curb wheel", 0.32, 0.08, (-3.5, -4.5, 0.32), M["dark"], None, (math.pi / 2, 0, 0), 20)
    kit.prop("bookshelf", (-2.0, -2.95, 0), rot=0, tint="#e8c890")
    kit.prop("couch_medium1", (-2.4, -6.1, 0), rot=0, tint="#c4a0e0")
    kit.light("dale_a", "AREA", (0, -5.0, 2.5), 280, "#fff1d8", size=1.4)
    kit.light("dale_b", "AREA", (-2.4, -4.6, 2.4), 160, "#fff1d8", size=1.0)
    kit.light("dale_c", "AREA", (0, -7.4, 2.4), 200, "#fff1d8", size=1.0)
    kit.light("dale_bath", "AREA", (0, -9.8, 2.4), 160, "#ffffff", size=1.0)


def build_k(kit, M, ctx):
    """Our kitchen: the cupboard with the lock that doubles, the clock, the sink, a table."""
    x = K0
    room_floor(kit, "k floor", x - 2.6, x + 2.6, -0.2, 4.2, M["floor_wood"])
    wall(kit, M, "k wallN", "x", 4.2, x - 2.6, x + 2.6, WALL_H, M["white"])
    wall(kit, M, "k wallW", "y", x - 2.6, -0.2, 4.2, WALL_H, M["sky"])
    wall(kit, M, "k wallE", "y", x + 2.6, -0.2, 4.2, WALL_H, M["sky"])
    wall(kit, M, "k wallS", "x", -0.2, x - 2.6, x + 2.6, WALL_H, M["sky"])
    # the cupboard: a white box with a door on a hinge; its pair of locks sit on the door
    bx(kit, "cup body", (0.9, 0.5, 0.9), (x - 0.8, 3.9, 0.95), M["white"])
    bx(kit, "cup base", (0.9, 0.5, 0.85), (x - 0.8, 3.9, 0.425), M["white"])
    lf = Leaf(kit, M, "cupboard", (x - 1.25, 3.64), 0, 0.9, 0.85, kit.plastic("#fff7ea", 0.4, name="p cup"), 0, -1, 0.03)
    lf.pivot.location.z = 0.525
    lf.slab.location.z = 0.425
    lf.slab.parent = lf.pivot
    # the door's face looks toward -y; locks stand on it
    ctx["cup_locks"] = build_lockset(kit, M, "cl", lf.slab, 2, -0.2, 0.25, -0.1, 0.3, -0.015, 0.1, 9, 2)
    ctx["cup_locks"][0].show(True)
    ctx["leaf_cup"] = lf
    kit.prop("kitchen_cabinet1", (x + 0.4, 3.9, 0), rot=0)
    kit.prop("kitchen_sink", (x + 1.0, 3.9, 0), rot=0)
    kit.prop("kitchen_oven", (x + 1.6, 3.9, 0), rot=0)
    kit.prop("table_roundsmall", (x - 0.3, 1.4, 0), scale=1.3)
    kit.prop("chair_1", (x - 1.1, 1.4, 0), rot=90)
    kit.prop("chair_2", (x + 0.5, 1.4, 0), rot=-90)
    kit.prop("stool", (x + 1.4, 1.2, 0))
    # the wall clock: hands only
    kit.cyl("clock face", 0.22, 0.04, (x - 2.0, 4.12, 1.9), M["white"], None, (math.pi / 2, 0, 0), 28)
    ctx["clock_h"] = kit.empty("clock pivot", (x - 2.0, 4.08, 1.9))
    ctx["hand_h"] = bx(kit, "hand h", (0.025, 0.012, 0.11), (0, 0, 0.055), M["black"], ctx["clock_h"])
    ctx["clock_m"] = kit.empty("clock pivot m", (x - 2.0, 4.075, 1.9))
    ctx["hand_m"] = bx(kit, "hand m", (0.018, 0.012, 0.17), (0, 0, 0.085), M["black"], ctx["clock_m"])
    kit.box("window k", (1.0, 0.04, 1.1), (x + 0.9, 4.16, 1.5), M["glowwin"])
    kit.light("k_a", "AREA", (x, 1.8, 2.5), 110, "#fff1d8", size=1.4)
    kit.light("k_b", "AREA", (x, 3.0, 2.4), 60, "#fff1d8", size=1.0)


def build_dk(kit, M, ctx):
    """The fridge man's kitchen, enclosed so its day and night are its own: the fridge, the 64 locks, the cooler."""
    x = DK0
    room_floor(kit, "dk floor", x - 2.6, x + 2.6, -0.2, 4.2, M["floor_wood"])
    wall(kit, M, "dk wallN", "x", 4.2, x - 2.6, x + 2.6, WALL_H, M["mint"])
    wall(kit, M, "dk wallW", "y", x - 2.6, -0.2, 4.2, WALL_H, M["mint"])
    wall(kit, M, "dk wallE", "y", x + 2.6, -0.2, 4.2, WALL_H, M["mint"])
    wall(kit, M, "dk wallS", "x", -0.2, x - 2.6, x + 2.6, WALL_H, M["mint"])
    bx(kit, "dk ceiling", (5.4, 4.6, 0.1), (x, 2.0, WALL_H + 0.05), M["white"])
    # the fridge: body and a hinged door; the door carries 64 locks
    bx(kit, "fr body", (0.9, 0.7, 1.75), (x - 0.2, 3.7, 0.875), M["white"])
    lf = Leaf(kit, M, "fridge", (x - 0.65, 3.33), 0, 0.9, 1.7, kit.plastic("#eef2f4", 0.35, name="p frd"), 0, -1, 0.07)
    lf.slab.location.z = 0.85
    ctx["leaf_fridge"] = lf
    ctx["fr_locks"] = build_lockset(kit, M, "fl", lf.slab, 64, -0.38, 0.38, -0.72, 0.72, -0.035, 0.07, 4, 8)
    for lk in ctx["fr_locks"]:
        lk.show(True)
    ctx["fr_hero"] = make_lock(kit, M, "frhero", 0, lf.slab, (0.1, -0.08, 0.77), 0.1)
    ctx["fr_tiny"] = make_lock(kit, M, "frtiny", 0, ctx["fr_hero"].flap, (0, -0.002, -0.02), 0.025)
    ctx["fr_tiny"].show(False)
    ctx["fr_hero"].show(True)
    # the cooler and the milk
    bx(kit, "cooler", (0.7, 0.45, 0.4), (x + 1.2, 1.2, 0.2), M["cooler_r"], None, (0, 0, 0.1))
    bx(kit, "cooler lid", (0.72, 0.47, 0.06), (x + 1.2, 1.2, 0.43), M["cooler_w"], None, (0, 0, 0.1))
    kit.cyl("milk", 0.07, 0.26, (x + 1.2, 1.2, 0.58), M["white"], None, (0, 0, 0), 14)
    kit.prop("kitchen_cabinet1", (x + 1.3, 3.9, 0), rot=0)
    kit.prop("kitchen_oven", (x + 1.9, 3.9, 0), rot=0)
    kit.prop("table_roundsmall", (x - 1.4, 1.3, 0), scale=1.2)
    # the ceiling light on a cord that swings
    ctx["dk_swing"] = kit.empty("dk swing", (x, 2.0, WALL_H))
    kit.cyl("dk cord", 0.01, 0.5, (0, 0, -0.25), M["dark"], ctx["dk_swing"], (0, 0, 0), 6)
    kit.prop("light_ceiling1", (0, 0, -0.84), parent=ctx["dk_swing"], scale=1.3)
    kit.sphere("dk bulb", 0.07, (0, 0, -0.55), unfogged_emit(kit, "bulb", "#fff0c8", 6.0), ctx["dk_swing"], 10)
    L = kit.light
    L("dk_a", "AREA", (x, 1.8, 2.45), 200, "#fff1d8", size=1.4)
    L("dk_b", "AREA", (x - 0.2, 3.0, 2.4), 200, "#ffffff", size=1.0)
    L("dk_n1", "AREA", (x, 1.8, 2.45), 140, "#ffb86b", size=1.6)
    L("dk_n2", "POINT", (x + 0.9, 3.1, 0.45), 26, "#ffb86b", size=0.08)


def build_stairs(kit, M, ctx):
    """A square stairwell: an upper landing, a flight down, a mid landing, a second flight down; Mrs. Pike's flat west."""
    x = ST0
    wm, wc = kit.texture("concrete", 1.0, tint="#e8e2d6"), M["mint"]
    room_floor(kit, "st land", x - 1.5, x + 1.5, -1.5, 0.3, wm)
    for i in range(12):
        top = -0.18 * (i + 1)
        bx(kit, f"st1 {i}", (1.4, 0.26, top + 4.6), (x - 0.8, 0.3 + 0.26 * (i + 0.5), (top - 4.6) / 2 + 4.6 / 2 - 0.0 if False else (top + (-4.6)) / 2), wm)
    bx(kit, "st mid", (3.0, 1.4, 0.1), (x, 4.12, -2.21), wm)
    for i in range(12):
        top = -2.16 - 0.18 * (i + 1)
        bx(kit, f"st2 {i}", (1.4, 0.26, top + 4.6), (x + 0.8, 3.42 - 0.26 * (i + 0.5), (top + (-4.6)) / 2), wm)
    bx(kit, "st low", (3.0, 2.4, 0.1), (x, -0.9, -4.37), wm)
    wall(kit, M, "st wallE", "y", x + 1.55, -2.1, 4.9, 5.0, wc, z0=-4.5)
    wall(kit, M, "st wallW", "y", x - 1.55, -2.1, 4.9, 5.0, wc, [(-0.4, 1.0, 2.1)], z0=-4.5)
    wall(kit, M, "st wallN", "x", -2.1, x - 1.55, x + 1.55, 5.0, wc, z0=-4.5)
    wall(kit, M, "st wallS", "x", 4.9, x - 1.55, x + 1.55, 5.0, wc, z0=-4.5)
    bx(kit, "st rail", (0.06, 1.8, 0.06), (x + 0.02, -0.6, 0.95), M["tan"])
    for yy in (-0.2, -1.1):
        kit.cyl(f"st post{yy}", 0.03, 0.95, (x + 0.02, yy, 0.475), M["tan"], None, (0, 0, 0), 8)
    bx(kit, "st rail2", (0.06, 3.8, 0.06), (x + 0.02, 2.2, -1.05), M["tan"], None, (math.radians(-35.0), 0, 0))
    for yy in (-0.2, 0.9):
        pass
    for yy in (-0.3, -1.2):
        bx(kit, f"st win{yy}", (0.04, 0.7, 1.2), (x + 1.51, yy, 1.5), M["glowwin"])
    # Mrs. Pike's flat, through the open door in the west wall: a front room and a bathroom with a curtain
    room_floor(kit, "pike floor", x - 6.2, x - 1.55, -1.6, 1.6, M["floor_wood"])
    wall(kit, M, "pike wallN", "x", -1.6, x - 6.2, x - 1.55, WALL_H, kit.plastic("#f6c8f0", 0.6, name="p pk"))
    wall(kit, M, "pike wallS", "x", 1.6, x - 6.2, x - 1.55, WALL_H, kit.plastic("#f6c8f0", 0.6, name="p pk"))
    wall(kit, M, "pike wallW", "y", x - 6.2, -1.6, 1.6, WALL_H, kit.plastic("#f6c8f0", 0.6, name="p pk"))
    wall(kit, M, "pike bathwall", "y", x - 4.2, -1.6, 1.6, WALL_H, M["bathtile"], [(0.0, 1.0, 2.1)])
    bx(kit, "pike curtain", (0.04, 1.0, 1.4), (x - 4.2, 0.0, 0.72), M["frost"])
    kit.prop("bathroom_sink", (x - 5.6, 1.1, 0), rot=0)
    kit.prop("bathroom_bathtub", (x - 5.4, -0.8, 0), rot=90)
    kit.prop("couch_medium1", (x - 2.6, 0.9, 0), rot=-90)
    ctx["leaf_pike"] = Leaf(kit, M, "pikedoor", (x - 1.55, -0.9), 90, 1.0, 2.1, M["coral"], 85, 1)
    L = kit.light
    L("st_a", "AREA", (x, -0.4, 4.0), 700, "#fff1d8", size=2.0)
    L("st_b", "AREA", (x, 2.6, 4.5), 500, "#fff1d8", size=2.0)
    L("st_c", "AREA", (x, 4.0, 1.5), 200, "#fff1d8", size=1.5)
    L("pk_a", "AREA", (x - 3.0, 0.0, 2.4), 220, "#fff1d8", size=1.2)
    L("pk_b", "AREA", (x - 5.2, 0.0, 2.4), 200, "#ffffff", size=1.0)
    # the brothers' door, closed-off for good: nothing to slam. (the landing has no door, only the bare opening)


def build_street(kit, M, ctx):
    x = SR0
    bx(kit, "sr road", (60, 9.0, 0.1), (x, -3.5, -0.05), M["asphalt"])
    bx(kit, "sr curb", (60, 0.3, 0.2), (x, 1.15, 0.0), M["walk"])
    bx(kit, "sr walk", (60, 4.4, 0.1), (x, 3.5, -0.0 - 0.05 + 0.1), M["walk"])
    bx(kit, "sr grass", (60, 10, 0.1), (x, 10.7, -0.05 + 0.02), M["grass"])
    kit.prop("bldg_4story", (x, 8.0, 0.0), rot=180, height=14.0)
    for i in range(3):
        bx(kit, f"sr step{i}", (2.4, 0.4, 0.15 * (i + 1)), (x, 4.4 + 0.4 * (2 - i) - 0.0, 0.075 * (i + 1)), M["walk"])
    kit.prop("sub_tree_large", (x - 6.0, 2.4, 0.0), scale=1.6)
    kit.prop("commontree_1", (x + 9.0, 5.0, 0.0), scale=1.4)
    # a parked car: a block body with a cab, four wheels
    cm = kit.plastic("#d8453b", 0.35, name="p car")
    bx(kit, "car body", (4.0, 1.7, 0.8), (x + 6.5, -1.2, 0.6), cm, None, (0, 0, 0), 0.08)
    bx(kit, "car cab", (2.0, 1.5, 0.6), (x + 6.3, -1.2, 1.3), kit.plastic("#b0dcf2", 0.2, name="p glass"), None, (0, 0, 0), 0.08)
    for wx in (-1.3, 1.3):
        for wy in (-0.85, 0.85):
            kit.cyl(f"wheel{wx}{wy}", 0.32, 0.22, (x + 6.5 + wx, -1.2 + wy, 0.32), M["black"], None, (math.pi / 2, 0, 0), 16)
    sun = kit.light("sr_sun", "SUN", (x, 0, 10), 3.0, "#fff0d8", rot=(math.radians(55), math.radians(10), math.radians(25)))
    kit.light("sr_fill", "AREA", (x, 2.0, 5.0), 500, "#ffffff", size=3.0)


# ------------------------------------------------------------------------------------------ the meter


def meter_png(path: Path, value: int):
    W, Hh = 960, 260
    im = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # the sunny-yellow door shape behind the padlock
    d.rounded_rectangle((34, 14, 164, 246), 16, fill=(246, 200, 68, 255), outline=(0, 0, 0, 255), width=10)
    d.ellipse((136, 120, 150, 134), fill=(60, 40, 10, 255))
    # the padlock: a thick shackle and an amber body
    d.arc((52, 40, 136, 150), 180, 360, fill=(0, 0, 0, 255), width=30)
    d.arc((60, 48, 128, 142), 180, 360, fill=(190, 200, 210, 255), width=14)
    d.rounded_rectangle((38, 108, 150, 210), 18, fill=(255, 178, 31, 255), outline=(0, 0, 0, 255), width=10)
    d.ellipse((82, 142, 106, 166), fill=(0, 0, 0, 255))
    d.rectangle((90, 156, 98, 188), fill=(0, 0, 0, 255))
    f = ImageFont.truetype(str(FONT), 190)
    txt = f"{value:,}"
    tw = d.textlength(txt, font=f)
    x0 = 200 + (W - 200 - tw) / 2
    d.text((x0, 18), txt, font=f, fill=(255, 255, 255, 255), stroke_width=14, stroke_fill=(0, 0, 0, 255))
    im.save(path)


def build_meter(kit, ctx, tl):
    cam = kit.OBJ["cam"]
    m = kit._new("meter")
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    b.inputs["Roughness"].default_value = 1.0
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = 0.0
    b.inputs["Base Color"].default_value = (0, 0, 0, 1)
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 0.95
    nt.links.new(tex.outputs["Alpha"], b.inputs["Alpha"])
    plane = kit.plane("meter", (1.0, 260 / 960), (0, 0, -0.3), m, cam)
    uv = plane.data.uv_layers.new(name="UVMap")
    for i, (u, v) in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[i].uv = (u, v)
    for a in ("visible_shadow",):
        try:
            setattr(plane, a, False)
        except Exception:
            pass
    ctx["meter"] = dict(plane=plane, tex=tex, cur=None)


def meter_value(tl, t):
    """The number on the meter and the time since it last doubled (for the pop)."""
    cs = sorted(_cues(tl, "meter"), key=lambda c: c["t"])
    v, since, prev = 1024.0, 9.0, 1024.0
    for c in cs:
        nv, d = float(c["v"]), float(c.get("dur", 0.0))
        if t < c["t"]:
            break
        if d > 0 and t < c["t"] + d:   # a roll between two numbers, in log space
            u = ss((t - c["t"]) / d)
            return math.exp(math.log(v) + (math.log(nv) - math.log(v)) * u), 9.0
        if nv != v:
            since = t - c["t"] - d
        v = nv
    return v, since


def update_meter(kit, ctx, tl, t):
    M = ctx["meter"]
    v, since = meter_value(tl, t)
    n = int(round(2 ** round(math.log2(max(v, 1.0)))))   # the meter only ever shows powers of two
    wd = ctx["wd"]
    p = wd / f"m{n}.png"
    if not p.exists():
        meter_png(p, n)
    if M["cur"] != n:
        img = bpy.data.images.load(str(p), check_existing=True)
        img.colorspace_settings.name = "sRGB"
        img.alpha_mode = "STRAIGHT"
        M["tex"].image = img
        M["cur"] = n
    from blocky import bl_story
    shot = next((x for x in tl["shots"] if x["start"] <= t < x["end"]), tl["shots"][-1])
    spec = {x["id"]: x for x in ctx["story"]["shots"]}[shot["id"]]
    lens = bl_story.cam_at(spec, shot, t, {}, tl)[2]
    dist = 0.3
    fh = 24.0 * dist / lens           # the frame's height at that distance (sensor 24 mm, vertical fit)
    fw = fh * 9.0 / 16.0
    width = fw * 0.86
    pop = 1.0 + 0.2 * (math.sin(math.pi * min(1.0, since / 0.25)) if 0 <= since < 0.25 else 0.0)
    pl = M["plane"]
    pl.scale = (width * pop, width * pop, 1.0)
    pl.location = (0.0, fh * (0.5 - 0.115), -dist)



# ------------------------------------------------------------------------------------------ build / animate


def build(kit, story, tl):
    ctx = {"story": story, "wd": workdir(tl)}
    M = mats(kit)
    ctx["M"] = M
    build_h(kit, M, ctx)
    build_bath(kit, M, ctx)
    build_d(kit, M, ctx)
    build_k(kit, M, ctx)
    build_dk(kit, M, ctx)
    build_stairs(kit, M, ctx)
    build_street(kit, M, ctx)
    build_meter(kit, ctx, tl)
    ctx["lens_last"] = None
    return ctx


def _world_strength(v):
    w = bpy.context.scene.world
    for n in w.node_tree.nodes:
        if n.type == "BACKGROUND" and n.inputs["Color"].is_linked:
            n.inputs["Strength"].default_value = v


def _night(tl, t):
    return float(track(_cues(tl, "night"), "v", t, 0.0))


def animate(kit, story, tl, t, ctx):
    B = ctx["bath"]
    # ---- the door group: placement, lock count, pile length, lean, swing
    pl = _cues(tl, "doorat")
    loc = track(pl, "loc", t, (0.0, 7.0, 0.0))
    sh = last(_cues(tl, "shudder"), t)
    off = (0.0, 0.0)
    if sh:
        dt = t - sh["t"]
        e = math.exp(-dt * 8.0) * math.sin(dt * 75.0) * 0.022
        off = (e, 0.4 * e)
    B["root"].location = (loc[0] + off[0], loc[1], loc[2] + off[1])
    B["root"].rotation_euler.z = math.radians(float(track(pl, "rot", t, 0.0)))
    sc = float(track(pl, "scale", t, 1.0))
    B["root"].scale = (sc, sc, sc)
    B["root"].rotation_euler.x = math.radians(float(track(pl, "pitch", t, 0.0)))
    dc = _cues(tl, "door")
    L = float(track(dc, "L", t, 0.0))
    lean = float(track(dc, "lean", t, 0.0))
    swing = float(track(dc, "swing", t, 0.0))
    B["swing"].rotation_euler.z = math.radians(swing)
    B["swing"].rotation_euler.x = math.radians(lean)
    n, n0, tn = 4, 4, -9.0
    for c in sorted(dc, key=lambda c: c["t"]):
        if "n" in c and c["t"] <= t + 1e-9:
            n0, n, tn = n, c["n"], c["t"]
    B["handle"].hide_render = L > 0.05 or n >= 512
    pop = min(1.0, max(0.0, (t - tn) / 0.2))
    for i, lk in enumerate(B["pool"]):
        if i < min(n0, n, POOL_N):
            lk.show(True, 1.0)
        elif i < min(n, POOL_N):
            lk.show(True, ss(pop))
        else:
            lk.show(False)
    hc = last(_cues(tl, "hole"), t)
    holes = hc["holes"] if hc else []
    for lk in B["pile"]:
        k = ss((L - lk.d) / 0.28 + 0.0) if L > 0 else 0.0
        if holes and k > 0:
            wx, wy, wz = lk.root.location[0] - DOOR_W / 2, 6.975 - lk.d, lk.root.location[2]
            if any(h[0] <= wx <= h[1] and h[2] <= wy <= h[3] and h[4] <= wz <= h[5] for h in holes):
                k = 0.0
        if k <= 0.001:
            lk.show(False)
        else:
            lk.show(True, k)
    # the hero lock and the tiny lock on its flap
    hv = L >= 0.3 or n >= 1024
    B["hero"].show(hv and n >= 1024, 1.0)
    fa = float(track(_cues(tl, "flap"), "a", t, 70.0))
    B["hero"].flap_angle(fa)
    tiny_t = [c for c in _cues(tl, "tiny") if c["t"] <= t + 1e-9]
    if tiny_t:
        B["tiny"].show(hv, ss((t - tiny_t[-1]["t"]) / 0.2))
    else:
        B["tiny"].show(False)
    # the flap's busy cue: the little flaps on pool locks move a bit on their own (plant 2)
    # keyhole flaps of the lock that swings in L17 (a pool lock near the top)
    sw = track(_cues(tl, "swingflap"), "a", t, 60.0)
    B["pool"][4].flap_angle(sw)
    # ---- doors
    ctx["leaf_my"].set(float(track(_cues(tl, "mydoor"), "a", t, 170.0)))
    ctx["leaf_dale"].set(float(track(_cues(tl, "daledoor"), "a", t, 85.0)))
    ctx["leaf_cup"].set(float(track(_cues(tl, "cupboard"), "a", t, 0.0)))
    ctx["leaf_fridge"].set(float(track(_cues(tl, "fridge"), "a", t, 0.0)))
    cc = last(_cues(tl, "cuplock"), t)
    ctx["cup_locks"][1].show(bool(cc), ss((t - cc["t"]) / 0.2) if cc else 0)
    fh_ = float(track(_cues(tl, "frflap"), "a", t, 70.0))
    ctx["fr_hero"].flap_angle(fh_)
    ft = last(_cues(tl, "frtiny"), t)
    ft_on = bool(ft and ft.get("on", True))
    ctx["fr_tiny"].show(ft_on, ss((t - ft["t"]) / 0.2) if ft_on else 0)
    # the bucket (a cue moves it to the door) and its keys
    ctx["bucket"].location = track(_cues(tl, "bucketat"), "loc", t, (-0.55, 0.55, 0.0))
    ctx["stool"].location = track(_cues(tl, "stoolat"), "loc", t, (0.5, 5.7, -5.0))
    fill = float(track(_cues(tl, "keys"), "v", t, 0.0))
    for k, base in zip(ctx["keys"], ctx["keys_base"]):
        k.location = (base[0], base[1], base[2] + 0.16 * fill)
    # props: Mom's shoe, the curb lamp Dale carries, Jade's camping mat and chair, the curtain, the hinge pins
    ctx["shoe"].location = track(_cues(tl, "shoeat"), "loc", t, (0.12, 6.62, -3.0))
    ctx["shoe"].rotation_euler.z = math.radians(float(track(_cues(tl, "shoeat"), "rot", t, 10.0)))
    ctx["mat"].location = track(_cues(tl, "matat"), "loc", t, (0.2, 3.2, -3.0))
    ctx["chair_j"].location = track(_cues(tl, "chairat"), "loc", t, (0.0, 5.9, -3.0))
    c0 = last(_cues(tl, "carry"), t)
    if c0 and c0.get("on"):
        sd = acting.state(tl, "dale", t)
        ctx["lamp"].location = (sd["x"], sd["y"] - 0.5, sd["z"] + 0.5)
    else:
        ctx["lamp"].location = (0, 0, -9)
    cv = float(track(_cues(tl, "curtain"), "v", t, -1.0))
    for i, (ob, x0) in enumerate(ctx["curtain"]):
        ob.hide_render = cv < 0
        if cv >= 0:
            ob.location.x = -0.46 + (x0 + 0.46) * (0.1 + 0.9 * cv)
    for k, (pin, base) in enumerate(ctx["pins"]):
        cs = [c for c in _cues(tl, "pin") if c["i"] == k and c["t"] <= t + 1e-9]
        if cs:
            u = t - cs[-1]["t"]
            drop = ss(u / 0.18)
            lift = 0.12 * math.sin(math.pi * min(1.0, u / 0.18)) * (1 - drop)
            pin.location = (base[0] + 0.1 * drop, base[1] - 0.12 * drop, base[2] + lift + (0.02 - base[2]) * drop)
            pin.rotation_euler.x = math.radians(90 * drop)
        else:
            pin.location = base
            pin.rotation_euler.x = 0.0
    # the clock
    hrs = float(track(_cues(tl, "clock"), "h", t, 7.25))
    ctx["clock_h"].rotation_euler.y = math.radians(hrs * 30.0)
    ctx["clock_m"].rotation_euler.y = math.radians(hrs * 360.0)
    # the downstairs light swings
    sa = float(track(_cues(tl, "dkswing"), "a", t, 0.0))
    ctx["dk_swing"].rotation_euler.x = math.radians(sa * math.sin(t * 2.4))
    # ---- light: our apartment's day or night, the fridge man's kitchen day or night
    p = _night(tl, t)
    pd = float(track(_cues(tl, "dknight"), "v", t, 0.0))
    _world_strength(0.9 * (1 - p) + 0.06 * p)
    over = {}
    for nm in ("h_a", "h_b", "h_c", "h_my", "h_jade", "h_mom", "h_bath"):
        over[nm] = 1 - 0.88 * p
    over["h_nfill"] = p
    over["h_night"] = p
    over["h_moon"] = p
    over["dk_a"] = over["dk_b"] = 1 - pd
    over["dk_n1"] = over["dk_n2"] = pd
    # the pile's own glints at night: a little warm fill by the bath door
    # ---- the meter
    update_meter(kit, ctx, tl, t)
    return over
