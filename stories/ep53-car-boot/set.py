"""Car boot (ep53): a Sunday car-boot sale in a sloping field, a hedge and a five-bar gate on the low side, a narrow lane
climbing a hill past a wooden bus shelter. Two small rooms (a kitchen and a bedroom) sit off to the side for the week
at home. Built from kit.py's parts; nothing here is shared with another story's set. There is no text anywhere.

Coordinates (metres). Front is -y; yaw 0 faces -y, yaw 90 faces +x, yaw 180 faces +y.
- Row A of cars (tailgates up, facing the aisle) at y = 2.4 .. 7, k * 4.6 along x. Tables at y = 0, sellers stand at
  y = 0.8. OUR stall is k = 0: the faded cream estate, a pasting table at (0, 0), two green camp chairs at y = 1.45
  (Pip's at x = -0.65, mine at x = +0.65). Customers stand at y = -0.7 facing +y.
- Row B at y = -10.4 .. -15 facing +y. The aisle between the rows is the field's middle.
- A hedge along y = -16 with a five-bar gate at x = -16; the lane runs on down -y from it. A bus shelter sits at
  (-13.7, -28) on a flat stretch of the lane. Past y = -36 the lane climbs to a brow at y = -96.
- Kitchen at x = 100, bedroom at x = 130, coach window at x = 160, the house front at x = 260.

THE TILTED (the creature): a blocky person in rust overalls and a tarp-green sheet tied on like a coat, seated in Pip's
chair. Its head lies along one shoulder (the neck turned a full quarter round), its two eyes stacked. It is never seen
moving; every pose change is across a cut. Posed by the "tilted" cues: roll (head, degrees; -90 lies on its right
shoulder), lift/side (where the head sits), lean (torso degrees forward from the hips).

Cues read here: tod, goods, mug3, tarp, bag, pipflat, coat, nocoat, veh, lamp, beam, tilted, sit (via acting z < 0).
Every light change is a smooth ramp: tod (the fog and the sun) and lamp/beam ramp over 0.3 s or more.
"""

from __future__ import annotations

import math
import random

import bpy
from mathutils import Vector as V

from blocky import faces, rig

FOGC = "#b8bcc0"
WORLD_UP = V((0, 0, 1))
CHAIR_P = (-0.65, 1.45)
ROW_A_X = [4.6 * k for k in range(-5, 8)]
ROW_B_X = [-9.2 + 4.6 * j for j in range(0, 10)]
CAR_COLS = ["#8c3b3b", "#35506f", "#d8d2c0", "#4d6a4b", "#6b6e73", "#a4793a", "#2f3b4a", "#7a5c7e", "#b9b4a6", "#3d6b6a"]
COAT_COLS = ["#46a7d6", "#f2c230", "#8456c8", "#e86aa0", "#2fb3a3", "#f0902a"]

# time of day: sun strength and colour, direction (azimuth from +x toward +y, elevation), character fill, sky, fog
TOD = {
    "day":    dict(sun=7.0, sunc="#fff0d8", az=-50, el=48, fill=1.2, fillc="#b4c6ea", sky=1.3, hor="#cfd6e0", zen="#7fa6dc", fogd=0.004, fogb=1.0),
    "open":   dict(sun=8.0, sunc="#ffe0ac", az=78, el=44, fill=0.9, fillc="#ffe8cc", sky=1.3, hor="#d4d6dc", zen="#7fa6dc", fogd=0.004, fogb=1.0),
    "flat":   dict(sun=2.6, sunc="#dfe6f0", az=-60, el=40, fill=5.5, fillc="#c8d4e8", sky=1.0, hor="#cdd3da", zen="#9fb3cf", fogd=0.006, fogb=1.0),
    "dawn":   dict(sun=3.0, sunc="#b8c8ff", az=-70, el=10, fill=2.4, fillc="#a0b4e8", sky=1.4, hor="#aeb6d8", zen="#5f78b0", fogd=0.012, fogb=0.8),
    "fog":    dict(sun=3.0, sunc="#e8ecfa", az=80, el=9, fill=2.6, fillc="#c0cae8", sky=1.7, hor="#b8bece", zen="#98a6c0", fogd=0.055, fogb=1.0),
    "sil":    dict(sun=4.0, sunc="#e8ecfa", az=80, el=9, fill=0.3, fillc="#c0cae8", sky=1.8, hor="#c4c9d6", zen="#98a6c0", fogd=0.055, fogb=1.0),
    "fogmid": dict(sun=1.0, sunc="#cdd7f2", az=200, el=12, fill=1.7, fillc="#b4c0e0", sky=0.95, hor="#aab0bf", zen="#8794b0", fogd=0.035, fogb=0.8),
    "gold":   dict(sun=8.5, sunc="#ffbd6e", az=180, el=11, fill=0.4, fillc="#8fa6e0", sky=1.0, hor="#f0c496", zen="#8aa4c8", fogd=0.004, fogb=1.0, rim=5.5),
    "goldlo": dict(sun=1.9, sunc="#ffbd6e", az=180, el=11, fill=0.5, fillc="#8fa6e0", sky=0.7, hor="#f0c496", zen="#8aa4c8", fogd=0.004, fogb=1.0, rim=1.5),   # S67: a sleeve is white, so less sun
    "goldb":  dict(sun=8.5, sunc="#ffbd6e", az=0, el=11, fill=0.4, fillc="#8fa6e0", sky=1.0, hor="#f0c496", zen="#8aa4c8", fogd=0.004, fogb=1.0, rim=5.5),
    "morn":   dict(sun=7.5, sunc="#ffd49a", az=-40, el=30, fill=1.4, fillc="#a5b8e6", sky=1.1, hor="#e8c9a8", zen="#86a8d4", fogd=0.004, fogb=1.0),
    "house":  dict(sun=3.0, sunc="#b8c8ff", az=-70, el=10, fill=1.6, fillc="#8fa6e0", sky=1.4, hor="#aeb6d8", zen="#5f78b0", fogd=0.01, fogb=0.8),
    "inside": dict(sun=0.0, sunc="#ffffff", az=-50, el=48, fill=0.0, fillc="#b4c6ea", sky=0.3, hor="#cfd6e0", zen="#7fa6dc", fogd=0.002, fogb=1.0),
}
for _v in TOD.values():
    _v.setdefault("rim", 0.0)   # a back-light on the characters only (the Tilted's rim)
ROOMS = {"kitchen": 100.0, "bedroom": 130.0}


# ------------------------------------------------------------------------------------------------ helpers
def _cues(tl, name):
    return [c for c in tl.get("cues", []) if c["name"] == name]


def _last(cs, t):
    cs = [c for c in cs if c["t"] <= t + 1e-9]
    return cs[-1] if cs else None


def _ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _lin(c):
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def _mixc(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


def _show(objs, on):
    for o in objs:
        for oo in [o] + list(o.children_recursive):
            oo.hide_render = not on


def smooth_h(y):
    """The lane's height: flat to y = -36, then a long climb that flattens at a brow around y = -96."""
    yy = -36.0 - y
    if yy <= 0:
        return 0.0
    if yy < 62:
        return 8.5 * _ss(yy / 62.0)
    return 8.5 - 0.05 * (yy - 62)


def ground(x, y):
    h = smooth_h(y)
    # the banks rise either side of the lane as it climbs, and the far hills close the field in
    bank = _ss((-y - 28) / 20.0) * min(5.0, 0.35 * max(0.0, abs(x + 16.0) - 3.5))
    edge = _ss((abs(x) - 52) / 26.0) * 13.0 + _ss((y - 18) / 24.0) * 13.0
    far = _ss((-y - 12) / 6.0) * _ss((abs(x + 16.0) - 6.0) / 8.0) * 1.8 if y > -36 else 0.0
    return h + bank + edge + far


def noisy(kit, name, hexc, dark=0.7, scale=2.0, rough=0.9, detail=5.0):
    """A flat colour mottled by noise (grass, mud, hedge, tarpaulin, tarmac)."""
    if name in kit.MATS:
        return kit.MATS[name]
    m = kit._new(name)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = detail
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    c = kit.col(hexc)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (c[0] * dark, c[1] * dark, c[2] * dark, 1)
    ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[1].color = c
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    kit._fogged(m, b.outputs[0])
    return m


def rod(kit, name, p0, p1, r, mat, parent=None, n=8):
    a, b = V(p0), V(p1)
    d = b - a
    ob = kit.cyl(name, r, d.length, tuple((a + b) / 2), mat, parent, n=n)
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return ob


class Pal:
    """Materials, made once."""

    def __init__(self, kit):
        P = kit.plastic
        self.kit = kit
        self.grass = noisy(kit, "grass", "#5f7d3a", 0.72, 1.4)
        self.mud = noisy(kit, "mud", "#5b4632", 0.6, 1.1, 0.95)
        self.hedge = noisy(kit, "hedge", "#3c5530", 0.55, 3.0, 0.95, 6.0)
        self.tarmac = noisy(kit, "tarmac", "#6b6d72", 0.78, 4.0, 0.85)
        self.tarp = noisy(kit, "tarp", "#3f6b4a", 0.8, 6.0, 0.7)
        self.cream = P("#d9cfb4", 0.5)
        self.glass = P("#2a3440", 0.15)
        self.tyre = P("#1d1f22", 0.8)
        self.steel = P("#9aa0a6", 0.3)
        self.chair = P("#4c6a3e", 0.85)
        self.chairf = P("#2a2c2e", 0.5)
        self.wood = kit.planks("#8a6a45", "#6b4e30", 1.4)
        self.woodd = P("#5a4129", 0.8)
        self.cloth = P("#c9c3b3", 0.9)
        self.greyc = P("#8f9296", 0.8)
        self.brass = P("#b58a3a", 0.3)
        self.teap = P("#e8e4da", 0.3)
        self.rust = P("#85533a", 0.8)
        self.lampr = kit.emit("#ff2a10", 2.2, "tail")
        self.bag = P("#7d7a52", 0.9)
        self.black = P("#161618", 0.6)
        self.sofa = P("#2f7a52", 0.95)
        self.ply = P("#c8b890", 0.7)
        self.wallk = P("#d8c9a8", 0.9)
        self.floork = kit.planks("#9a7650", "#7a5a38", 1.6, "X")
        self.paper = P("#efe9d8", 0.9)
        self.bluew = P("#4d6a96", 0.8)
        self.coach = P("#c9ccd2", 0.5)
        self.busc = P("#c97a2a", 0.5)
        self.hand = P("#c9a06a", 0.9)
        self.pcoat = {}


# ------------------------------------------------------------------------------------------------ the world
def build_terrain(kit, M):
    nx, ny, step = 90, 90, 2.0
    x0, y0 = -90.0, -126.0
    verts, fcs, lane = [], [], []
    for j in range(ny + 1):
        for i in range(nx + 1):
            x, y = x0 + i * step, y0 + j * step
            verts.append((x, y, ground(x, y)))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            fcs.append((a, a + 1, a + nx + 2, a + nx + 1))
    kit.mesh_obj("terrain", verts, fcs, M.grass, smooth=True)
    # the lane: a tarmac strip over the same nodes
    lv, lf = [], []
    ys = [y0 + j * step for j in range(ny + 1) if -118 < y0 + j * step < -14]
    for k, y in enumerate(ys):
        for xx in (-17.4, -14.6):
            lv.append((xx, y, ground(xx, y) + 0.035))
    for k in range(len(ys) - 1):
        a = k * 2
        lf.append((a, a + 1, a + 3, a + 2))
    kit.mesh_obj("lane", lv, lf, M.tarmac, smooth=True)
    # rows of churned mud where the cars park
    for nm, yc in (("A", 4.2), ("B", -12.4)):
        kit.plane(f"mud{nm}", (74, 6.4), (0, yc, 0.025), M.mud)
    for nm, yc in (("A", 0.3), ("B", -9.6)):
        kit.plane(f"mudt{nm}", (70, 1.6), (0, yc, 0.02), M.mud)
    kit.plane("gatemud", (4.0, 3.2), (-16.0, -15.0, 0.022), M.mud)


def build_hedge(kit, M):
    rnd = random.Random(5)
    spans = [(-44, -18.2, -16.0), (-13.8, 44, -16.0), (-44, 44, 11.5)]
    for si, (xa, xb, y) in enumerate(spans):
        x = xa
        k = 0
        while x < xb:
            w = rnd.uniform(1.6, 2.4)
            h = rnd.uniform(1.5, 1.9)
            kit.box(f"hedge{si}_{k}", (w, 1.3, h), (x + w / 2, y, h / 2), M.hedge, bevel=0.35)
            x += w * 0.92
            k += 1
    for side, (xa, yb) in enumerate(((-44, 0.0), (44, 0.0))):
        for k in range(14):
            y = -16 + k * 2.0
            kit.box(f"hedgev{side}_{k}", (1.3, 2.2, 1.7), (xa, y, 0.85), M.hedge, bevel=0.35)


def build_gate(kit, M):
    for x in (-17.9, -14.1):
        kit.box(f"gatepost{x}", (0.2, 0.2, 1.5), (x, -16.0, 0.75), M.woodd, bevel=0.03)
    gate = kit.empty("gate", (-17.8, -16.0, 0.0))
    for k, z in enumerate((0.25, 0.55, 0.85, 1.15)):
        kit.box(f"bar{k}", (3.4, 0.05, 0.1), (1.7, 0, z), M.wood, gate)
    kit.box("gatestile", (0.1, 0.05, 1.25), (0.05, 0, 0.62), M.wood, gate)
    kit.box("gatestile2", (0.1, 0.05, 1.25), (3.35, 0, 0.62), M.wood, gate)
    rod(kit, "gatebrace", (0.1, 0, 0.2), (3.3, 0, 1.2), 0.025, M.wood, gate, 6)
    gate.rotation_euler = (0, 0, math.radians(62))   # standing open into the field


def build_shelter(kit, M):
    sx, sy = -13.7, -28.0
    root = kit.empty("shelter", (sx, sy, 0.0))
    kit.box("sh.floor", (1.5, 2.6, 0.1), (0.1, 0, 0.05), M.cloth, root)
    kit.box("sh.back", (0.1, 2.6, 2.0), (0.7, 0, 1.0), M.wood, root)
    for sgn in (-1, 1):
        kit.box(f"sh.side{sgn}", (1.5, 0.1, 2.0), (0.1, sgn * 1.25, 1.0), M.wood, root)
    kit.box("sh.roof", (1.9, 2.9, 0.12), (0.05, 0, 2.08), M.woodd, root, rot=(0, math.radians(-4), 0), bevel=0.02)
    kit.box("sh.bench", (0.45, 2.2, 0.08), (0.45, 0, 0.5), M.wood, root, bevel=0.02)
    for sgn in (-1, 1):
        kit.box(f"sh.bleg{sgn}", (0.4, 0.08, 0.5), (0.45, sgn * 1.0, 0.25), M.woodd, root)
    kit.light("shelter lamp", "POINT", (-14.0, -28.0, 1.9), 420, "#ffe8c8", size=0.5)
    kit.light("strip fill", "POINT", (-1.0, 0.25, 1.4), 1.0, "#c8d4f0", size=0.6)
    kit.light("shelter fill", "POINT", (-14.6, -27.2, 1.5), 1.0, "#ffe2bc", size=1.0)
    return root


def make_car(kit, M, name, x, y, yaw, colr, tail_up=True, estate=False):
    root = kit.empty(name, (x, y, 0.0), rot=(0, 0, math.radians(yaw)))
    body = kit.plastic(colr, 0.45)
    gl = M.glass
    # local frame: the tailgate end at y = 0, the car runs on toward +y (its nose), facing +y
    kit.box(f"{name}.low", (1.85, 4.3, 0.62), (0, 2.15, 0.68), body, root, bevel=0.1)
    for sx in (-1, 1):
        for yy in (0.8, 3.4):
            kit.cyl(f"{name}.wh{sx}{yy}", 0.33, 0.22, (sx * 0.92, yy, 0.33), M.tyre, root, rot=(0, math.pi / 2, 0), n=14)
    for sx in (-1, 1):
        kit.box(f"{name}.tl{sx}", (0.22, 0.04, 0.12), (sx * 0.72, -0.02, 0.8), M.lampr, root)
    if estate:
        # an estate: a roof on side walls over an open boot at the back; the hatch hinges at the roof's rear edge and
        # hangs down to shut (180 degrees) or swings up and back (55)
        kit.box(f"{name}.roof", (1.74, 3.3, 0.08), (0, 1.65, 1.62), body, root, bevel=0.03)
        for sx in (-1, 1):
            kit.box(f"{name}.side{sx}", (0.07, 3.3, 0.3), (sx * 0.83, 1.65, 1.15), body, root, bevel=0.02)
            kit.box(f"{name}.win{sx}", (0.02, 2.2, 0.36), (sx * 0.86, 1.65, 1.46), gl, root)
        kit.box(f"{name}.seats", (1.6, 1.1, 0.5), (0, 2.75, 1.22), body, root, bevel=0.05)
        kit.box(f"{name}.wind", (1.5, 0.03, 0.46), (0, 3.31, 1.4), gl, root)
        if True:
            pv = kit.empty(f"{name}.tgp", (0, 0.0, 1.61), root)
            kit.box(f"{name}.tg", (1.7, 0.07, 0.62), (0, -0.04, -0.31), body, pv, bevel=0.03)
            kit.box(f"{name}.tgw", (1.34, 0.075, 0.3), (0, -0.04, -0.2), gl, pv)
            kit.box(f"{name}.latch", (0.16, 0.05, 0.1), (0, -0.09, -0.52), M.steel, pv, bevel=0.01)
            pv.rotation_euler = (math.radians(-125 if tail_up else 0), 0, 0)
        kit.box(f"{name}.cargo", (1.5, 1.5, 0.04), (0, 0.8, 1.0), M.greyc, root)
    else:
        cy, ch = 3.35, 2.0
        kit.box(f"{name}.cab", (1.72, ch, 0.62), (0, cy, 1.3), body, root, bevel=0.14)
        for sx in (-1, 1):
            kit.box(f"{name}.win{sx}", (0.02, ch - 0.3, 0.38), (sx * 0.87, cy, 1.32), gl, root)
        kit.box(f"{name}.wind", (1.5, 0.02, 0.4), (0, cy + ch / 2 + 0.005, 1.3), gl, root)
        rear = cy - ch / 2
        kit.box(f"{name}.deck", (1.6, rear, 0.05), (0, rear / 2, 1.0), M.greyc, root)
        if tail_up:
            pv = kit.empty(f"{name}.tgp", (0, rear, 1.61), root)
            kit.box(f"{name}.tg", (1.62, 0.07, 0.95), (0, 0, 0.5), body, pv, bevel=0.03)
            kit.box(f"{name}.tgw", (1.34, 0.075, 0.45), (0, 0, 0.55), gl, pv)
            pv.rotation_euler = (math.radians(55), 0, 0)
    return root


def make_estate(kit, M, name, x, y, yaw, tail_up=True):
    return make_car(kit, M, name, x, y, yaw, "#d9cfb4", tail_up, estate=True)


def make_bus(kit, M, name, colr, coach=False):
    root = kit.empty(name, (0, 0, -60.0))
    L = 9.0 if coach else 7.0
    body = kit.plastic(colr, 0.45)
    kit.box(f"{name}.body", (2.5, L, 2.5 if coach else 2.3), (0, L / 2, 1.45 if coach else 1.35), body, root, bevel=0.15)
    kit.box(f"{name}.stripe", (2.52, L - 0.4, 0.14), (0, L / 2, 0.75), M.black, root)
    for sx in (-1, 1):
        kit.box(f"{name}.wins{sx}", (0.02, L - 1.6, 0.8), (sx * 1.26, L / 2 + 0.2, 1.8 if coach else 1.7), M.glass, root)
    # the front (at y = L): windscreen, a blank blind, two lamps; the back (y = 0): a rear window and two red lamps
    kit.box(f"{name}.ws", (2.1, 0.02, 0.95), (0, L + 0.005, 1.65), M.glass, root)
    kit.box(f"{name}.blind", (1.7, 0.02, 0.28), (0, L + 0.01, 2.35 if coach else 2.25), M.black, root)
    kit.box(f"{name}.rw", (1.9, 0.02, 0.7), (0, -0.005, 1.7), M.glass, root)
    for sx in (-1, 1):
        kit.box(f"{name}.rl{sx}", (0.24, 0.04, 0.16), (sx * 0.95, -0.02, 0.7), M.lampr, root)
        kit.cyl(f"{name}.wh{sx}a", 0.5, 0.3, (sx * 1.2, 1.4, 0.5), M.tyre, root, rot=(0, math.pi / 2, 0), n=14)
        kit.cyl(f"{name}.wh{sx}b", 0.5, 0.3, (sx * 1.2, L - 1.4, 0.5), M.tyre, root, rot=(0, math.pi / 2, 0), n=14)
    lamps = []
    for sx in (-1, 1):
        m = bpy_emit(kit, f"{name}.lamp{sx}")
        kit.box(f"{name}.hl{sx}", (0.3, 0.05, 0.22), (sx * 0.85, L + 0.025, 0.7), m, root, bevel=0.03)
        lamps.append(m)
    return root, lamps


def bpy_emit(kit, name):
    return kit.emit("#ffd9a0", 0.0, name)


def make_table(kit, M, name, x, y, cloth_hex, length=2.2):
    kit.box(f"{name}.top", (length, 0.75, 0.05), (x, y, 0.76), kit.plastic(cloth_hex, 0.9), bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"{name}.leg{sx}{sy}", (0.05, 0.05, 0.76), (x + sx * (length / 2 - 0.1), y + sy * 0.3, 0.38), M.chairf)


def make_chair(kit, M, name, x, y):
    root = kit.empty(name, (x, y, 0.0))
    kit.box(f"{name}.seat", (0.58, 0.52, 0.05), (0, 0, 0.44), M.chair, root, bevel=0.015)
    kit.box(f"{name}.back", (0.58, 0.05, 0.42), (0, 0.27, 0.72), M.chair, root, rot=(math.radians(-8), 0, 0), bevel=0.015)
    for sx in (-1, 1):
        kit.box(f"{name}.arm{sx}", (0.05, 0.5, 0.04), (sx * 0.32, 0.0, 0.62), M.chairf, root)
        kit.box(f"{name}.armp{sx}", (0.04, 0.04, 0.2), (sx * 0.32, -0.2, 0.52), M.chairf, root)
        for sy in (-1, 1):
            kit.box(f"{name}.lg{sx}{sy}", (0.04, 0.04, 0.44), (sx * 0.28, sy * 0.22, 0.22), M.chairf, root)
    return root


def clutter(kit, M, name, x, y, seed):
    rnd = random.Random(seed)
    for k in range(9):
        cx = x + rnd.uniform(-0.95, 0.95)
        cy = y + rnd.uniform(-0.22, 0.22)
        c = rnd.choice(["#c0392b", "#d9b44a", "#5a7fa8", "#a6a08c", "#7a5a3a", "#8a8f6a", "#c9c3b3", "#6b4a6e"])
        m = kit.plastic(c, 0.6)
        kind = rnd.choice(["box", "cyl", "tall"])
        if kind == "box":
            kit.box(f"{name}.c{k}", (rnd.uniform(0.15, 0.32), rnd.uniform(0.15, 0.25), rnd.uniform(0.1, 0.22)), (cx, cy, 0.785 + 0.08), m, bevel=0.02)
        elif kind == "cyl":
            kit.cyl(f"{name}.c{k}", rnd.uniform(0.07, 0.13), rnd.uniform(0.14, 0.3), (cx, cy, 0.785 + 0.1), m, n=10)
        else:
            kit.box(f"{name}.c{k}", (0.12, 0.12, rnd.uniform(0.3, 0.45)), (cx, cy, 0.785 + 0.2), m, bevel=0.03)


def build_row(kit, M, ctx):
    rnd = random.Random(11)
    for i, x in enumerate(ROW_A_X):
        if x == 0:
            continue
        colr = CAR_COLS[i % len(CAR_COLS)]
        make_car(kit, M, f"carA{i}", x, 2.4, 0, colr, True, estate=(i % 3 == 0))
        make_table(kit, M, f"tabA{i}", x, 0.0, rnd.choice(["#c9c3b3", "#a8b4c4", "#cdb89a", "#b4c3a8"]))
        k = round(x / 4.6)
        if k == -2:   # the haggler's lamp stall: one brass lamp in front, odds and ends behind
            clutter(kit, M, f"clA{i}", x + 0.5, 0.15, i + 3)
            kit.cyl("hl.base", 0.1, 0.04, (x - 0.4, -0.05, 0.8), M.brass, n=14)
            kit.cyl("hl.stem", 0.03, 0.32, (x - 0.4, -0.05, 0.98), M.brass, n=8)
            kit.cyl("hl.shade", 0.06, 0.18, (x - 0.4, -0.05, 1.2), M.cream, n=14, r2=0.15)
        elif k == 2:   # Walter's table of single shoes
            for q in range(7):
                kit.box(f"wsh{q}", (0.11, 0.28, 0.1), (x - 0.95 + 0.32 * q, 0.0 + 0.06 * ((q % 3) - 1), 0.84),
                        kit.plastic(["#7a4a2a", "#202226", "#a4793a", "#5a3a2a", "#3d4a5a", "#8a6a4a", "#2a2a2a"][q], 0.6), bevel=0.03)
        elif k == -5:   # the end stall: one teapot
            kit.cyl("wt.body", 0.12, 0.2, (x, 0.0, 0.89), M.teap, n=14)
            kit.sphere("wt.top", 0.08, (x, 0.0, 1.03), M.teap, seg=10)
            kit.box("wt.spout", (0.05, 0.14, 0.05), (x, -0.17, 0.93), M.teap, rot=(math.radians(25), 0, 0))
            kit.box("wt.handle", (0.04, 0.05, 0.14), (x, 0.16, 0.91), M.teap)
        else:
            clutter(kit, M, f"clA{i}", x, 0.0, i + 3)
    for j, x in enumerate(ROW_B_X):
        colr = CAR_COLS[(j + 4) % len(CAR_COLS)]
        make_car(kit, M, f"carB{j}", x, -10.4, 180, colr, True, estate=(j % 2 == 0))
        make_table(kit, M, f"tabB{j}", x, -9.6, rnd.choice(["#c9c3b3", "#a8b4c4", "#cdb89a", "#b4c3a8"]))
        clutter(kit, M, f"clB{j}", x, -9.6, j + 40)


def build_sofa(kit, M, x, y):
    root = kit.empty("sofa", (x, y, 0.0))
    kit.box("sofa.base", (2.0, 0.9, 0.4), (0, 0, 0.3), M.sofa, root, bevel=0.07)
    kit.box("sofa.seat", (1.7, 0.75, 0.14), (0, -0.05, 0.56), M.sofa, root, bevel=0.05)
    kit.box("sofa.back", (2.0, 0.22, 0.65), (0, 0.4, 0.75), M.sofa, root, bevel=0.08)
    for sx in (-1, 1):
        kit.box(f"sofa.arm{sx}", (0.22, 0.9, 0.6), (sx * 1.0, 0, 0.55), M.sofa, root, bevel=0.07)
    return root


# ---- goods on our table: they have a front (-y), so they can be turned toward Pip's chair -----------------------------
def build_goods(kit, M, ctx):
    items = {}
    spots = {"teapot": (-0.55, 0.05), "lamp": (-0.1, -0.05), "clock": (0.4, 0.05), "shoe": (0.85, -0.05), "radio": (0.75, 0.2)}
    spots["radio"] = (-0.95, 0.1)
    spots["shoe"] = (0.95, -0.05)
    spots["clock"] = (0.45, 0.05)
    for nm, (gx, gy) in spots.items():
        root = kit.empty(f"g.{nm}", (gx, gy, 0.785))
        if nm == "teapot":
            kit.cyl("tp.body", 0.1, 0.16, (0, 0, 0.09), M.teap, root, n=14)
            kit.sphere("tp.top", 0.07, (0, 0, 0.2), M.teap, root, seg=10)
            kit.box("tp.spout", (0.04, 0.12, 0.04), (0, -0.14, 0.12), M.teap, root, rot=(math.radians(25), 0, 0))
            kit.box("tp.handle", (0.03, 0.04, 0.12), (0, 0.13, 0.11), M.teap, root)
        elif nm == "lamp":
            kit.cyl("lp.base", 0.09, 0.03, (0, 0, 0.015), M.brass, root, n=14)
            kit.cyl("lp.stem", 0.025, 0.28, (0, 0, 0.17), M.brass, root, n=8)
            kit.cyl("lp.shade", 0.05, 0.16, (0, 0, 0.36), M.cream, root, n=14, r2=0.13)
            kit.box("lp.knob", (0.03, 0.06, 0.03), (0, -0.1, 0.2), M.brass, root)
        elif nm == "clock":
            kit.box("ck.body", (0.26, 0.1, 0.26), (0, 0, 0.13), M.woodd, root, bevel=0.02)
            kit.cyl("ck.face", 0.1, 0.01, (0, -0.056, 0.14), M.paper, root, rot=(math.pi / 2, 0, 0), n=18)
            kit.box("ck.h1", (0.012, 0.012, 0.07), (0, -0.065, 0.17), M.black, root)
            kit.box("ck.h2", (0.05, 0.012, 0.012), (0.02, -0.065, 0.14), M.black, root)
        elif nm == "shoe":
            kit.box("sh.sole", (0.12, 0.3, 0.03), (0, 0, 0.015), M.black, root, bevel=0.01)
            kit.box("sh.up", (0.11, 0.18, 0.1), (0, 0.05, 0.08), kit.plastic("#7a4a2a", 0.6), root, bevel=0.03)
            kit.box("sh.toe", (0.11, 0.12, 0.07), (0, -0.09, 0.055), kit.plastic("#7a4a2a", 0.6), root, bevel=0.03)
        elif nm == "radio":
            kit.box("rd.body", (0.4, 0.15, 0.24), (0, 0, 0.12), M.cream, root, bevel=0.025)
            kit.box("rd.grille", (0.2, 0.012, 0.16), (-0.07, -0.081, 0.12), M.chairf, root)
            dm = bpy_emit(kit, "dial")
            kit.cyl("rd.dial", 0.05, 0.01, (0.12, -0.082, 0.14), dm, root, rot=(math.pi / 2, 0, 0), n=16)
            kit.box("rd.knob", (0.04, 0.04, 0.04), (0.12, -0.09, 0.05), M.black, root)
            ctx["dial"] = dm
        items[nm] = (root, gx, gy)
    ctx["goods"] = items


def build_stall(kit, M, ctx):
    make_estate(kit, M, "estate", 0.0, 2.4, 0, True)
    make_table(kit, M, "tab0", 0.0, 0.0, "#c9c3b3")
    kit.cyl("flask", 0.06, 0.26, (0.55, 2.5, 1.16), M.steel, n=12)
    for k, mx in enumerate((-0.2, 0.0, 0.2)):
        mug = kit.cyl(f"mug{k}", 0.05, 0.1, (mx, 2.5, 1.08), kit.plastic(["#e8e4da", "#c9a85a", "#6b8cae"][k], 0.5), n=12)
        if k == 2:
            ctx["mug3"] = mug
    for nm, x in (("chairL", CHAIR_P[0]), ("chairR", 0.65)):
        make_chair(kit, M, nm, x, CHAIR_P[1])
    # a strip of tarp hung off the left chair's arm
    strip = kit.box("tarpstrip", (0.08, 0.02, 0.5), (-0.67 - 0.32, 1.35, 0.4), M.tarp, rot=(0.1, 0.08, 0.2))
    ctx["tarpstrip"] = strip
    # Pip's coat laid flat on the table, and on a bench/arm: one object, moved by the "pipflat" cue
    flat = kit.empty("pipflat", (0, 0, -40.0))
    cm = kit.plastic("#8a8d90", 0.9, "pipflat")
    kit.box("pf.body", (0.56, 0.7, 0.1), (0, -0.02, 0.05), cm, flat, bevel=0.03)
    for sx in (-1, 1):   # sleeves straight out to each side, a cuff at each end
        kit.box(f"pf.arm{sx}", (0.5, 0.17, 0.09), (sx * 0.5, 0.08, 0.045), cm, flat, rot=(0, 0, sx * -0.1), bevel=0.03)
        kit.box(f"pf.cuff{sx}", (0.07, 0.19, 0.1), (sx * 0.77, 0.06, 0.05), kit.plastic("#5e6063", 0.9), flat, bevel=0.02)
    # the hood lying open above the collar: a rim round a dark inside
    kit.box("pf.hood", (0.34, 0.26, 0.08), (0, 0.46, 0.04), cm, flat, bevel=0.04)
    kit.box("pf.hoodin", (0.2, 0.15, 0.02), (0, 0.46, 0.085), kit.plastic("#2a2b2d", 0.9), flat)
    # four toggles down the front, each on a short cord loop, in pale horn so they read from above
    horn = kit.plastic("#efe4c4", 0.5)
    for k, ty in enumerate((-0.25, -0.1, 0.05, 0.2)):
        kit.box(f"pf.tog{k}", (0.1, 0.045, 0.05), (0, ty, 0.12), horn, flat, bevel=0.015)
        kit.box(f"pf.loop{k}", (0.2, 0.012, 0.012), (0, ty, 0.102), kit.plastic("#3a3b3d", 0.9), flat)
    kit.box("pf.zip", (0.012, 0.64, 0.012), (0, -0.02, 0.102), kit.plastic("#3a3b3d", 0.9), flat)
    ctx["pipflat"] = flat
    bag = kit.empty("holdall", (0, 0, -40.0))
    kit.box("hb.body", (0.6, 0.28, 0.34), (0, 0, 0.17), M.bag, bag, bevel=0.07)
    kit.box("hb.strap", (0.34, 0.03, 0.12), (0, -0.02, 0.4), M.black, bag)
    ctx["bag"] = bag
    # the folded chair lying in the boot, and two tarp-green strokes scratched into the latch (shown once)
    fold = kit.empty("fold", (-0.3, 3.2, 1.06), rot=(0, 0, math.radians(20)))
    kit.box("fold.a", (0.62, 0.07, 0.8), (0, 0, 0.0), M.chair, fold, rot=(math.radians(80), 0, 0), bevel=0.01)
    kit.box("fold.b", (0.6, 0.06, 0.7), (0, 0.0, 0.08), M.chairf, fold, rot=(math.radians(78), 0, 0), bevel=0.01)
    ctx["fold"] = fold
    ctx["strokes"] = [kit.box(f"stroke{k}", (0.012, 0.012, 0.075), (-0.035 + 0.07 * k, 2.277, 1.095), M.tarp) for k in range(2)]


def build_house(kit, M, ctx):
    x, y = 260.0, 4.0
    kit.box("house", (7.0, 5.0, 4.6), (x, y + 2.5, 2.3), kit.plastic("#b9a58a", 0.9), bevel=0.05)
    kit.box("house.roof", (7.6, 5.6, 0.8), (x, y + 2.5, 4.9), kit.plastic("#5a4a45", 0.9), bevel=0.05)
    kit.box("house.door", (1.1, 0.08, 2.1), (x - 1.2, y - 0.03, 1.05), M.bluew)
    for wx in (1.4, 2.6):
        kit.box(f"house.win{wx}", (1.0, 0.08, 1.1), (x + wx, y - 0.03, 1.8), M.glass)
    kit.box("house.win2", (1.0, 0.08, 1.1), (x - 1.2 + 4.0, y - 0.03, 3.4), M.glass)
    kit.plane("house.drive", (14, 12), (x, y - 6, 0.03), M.mud)
    kit.plane("house.grass", (60, 60), (x, y + 10, 0.0), M.grass)


def build_room(kit, M, ctx, x0, kind):
    wall = kit.plastic("#d4c3a2" if kind == "kitchen" else "#8d9db8", 0.9)
    fl = M.floork
    W, D, H = 5.0, 4.2, 2.8
    kit.box(f"{kind}.floor", (W, D, 0.1), (x0, 0, -0.05), fl)
    kit.box(f"{kind}.ceil", (W, D, 0.1), (x0, 0, H + 0.05), wall)
    kit.box(f"{kind}.back", (W, 0.1, H), (x0, D / 2, H / 2), wall)
    kit.box(f"{kind}.left", (0.1, D, H), (x0 - W / 2, 0, H / 2), wall)
    kit.box(f"{kind}.right", (0.1, D, H), (x0 + W / 2, 0, H / 2), wall)
    kit.box(f"{kind}.front", (W, 0.1, H), (x0, -D / 2, H / 2), wall)
    # a window in the back wall, glowing pale blue daylight (a fixed colour: nothing switches)
    win = kit.emit("#9fb7da", 1.1 if kind == "kitchen" else 0.45, f"{kind}.win")
    kit.box(f"{kind}.winp", (1.5, 0.04, 1.2), (x0 + 1.2, D / 2 - 0.07, 1.6), win)
    for k, (wx, wz, ww, wh) in enumerate(((0, 0.62, 1.7, 0.08), (0, -0.62, 1.7, 0.08))):
        kit.box(f"{kind}.winf{k}", (ww, 0.06, wh), (x0 + 1.2, D / 2 - 0.08, 1.6 + wz), M.woodd)
    lamp = kit.light(f"{kind} lamp", "POINT", (x0, 0.0, 2.55), 520 if kind == "kitchen" else 480,
                     "#ffd2a0" if kind == "kitchen" else "#ffb878", size=0.4)
    ctx[f"{kind}_lamp"] = lamp
    kit.box(f"{kind}.shade", (0.5, 0.5, 0.18), (x0, 0.0, 2.7), kit.plastic("#e8dcc0", 0.9))
    if kind == "kitchen":
        kit.box("k.table", (1.6, 1.0, 0.05), (x0, -0.2, 0.76), M.wood, bevel=0.01)
        for sx in (-1, 1):
            for sy in (-1, 1):
                kit.box(f"k.tl{sx}{sy}", (0.06, 0.06, 0.76), (x0 + sx * 0.72, -0.2 + sy * 0.42, 0.38), M.woodd)
        for nm, cx, cy in (("kcp", x0, -1.1), ("kcm", x0, 0.7)):
            make_chair(kit, M, nm, cx, cy)
        ctx["kchair_flip"] = True
        # counter and sink
        kit.box("k.counter", (2.6, 0.7, 0.92), (x0 - 1.2, D / 2 - 0.45, 0.46), M.cream, bevel=0.02)
        kit.box("k.sink", (0.7, 0.5, 0.06), (x0 - 1.2, D / 2 - 0.45, 0.94), M.steel)
        kit.box("k.tap", (0.05, 0.05, 0.3), (x0 - 1.2, D / 2 - 0.62, 1.05), M.steel)
        kit.box("env", (0.3, 0.2, 0.012), (x0 + 0.1, -0.1, 0.8), M.paper, rot=(0, 0, 0.3))
        kit.box("toast", (0.2, 0.2, 0.02), (x0 - 0.3, -0.2, 0.795), kit.plastic("#c9a063", 0.8))
        kit.box("k.mug1", (0.1, 0.1, 0.1), (x0 + 0.4, -0.45, 0.85), kit.plastic("#e8e4da", 0.5))
        kit.box("k.mug2", (0.1, 0.1, 0.1), (x0 + 0.4, 0.1, 0.85), kit.plastic("#6b8cae", 0.5))
        # a door frame in the left wall
        kit.box("k.door", (0.05, 1.0, 2.0), (x0 - W / 2 + 0.06, -0.8, 1.0), M.woodd)
    else:
        kit.box("b.bed", (1.6, 2.0, 0.42), (x0 - 0.6, 0.6, 0.21), kit.plastic("#7a6a8a", 0.9), bevel=0.04)
        kit.box("b.pillow", (0.9, 0.4, 0.14), (x0 - 0.6, 1.4, 0.49), M.paper, bevel=0.05)
        kit.box("b.head", (1.7, 0.1, 0.9), (x0 - 0.6, 1.68, 0.6), M.woodd)
        kit.box("b.stand", (0.5, 0.5, 0.55), (x0 + 0.9, 1.5, 0.28), M.woodd)
        kit.box("b.lamp", (0.14, 0.14, 0.3), (x0 + 0.9, 1.5, 0.7), kit.plastic("#e8dcc0", 0.8))
        # a box of unpriced junk on the floor
        kit.box("b.crate", (0.9, 0.6, 0.35), (x0 + 0.9, -0.6, 0.18), M.ply, bevel=0.02)
        for k in range(6):
            kit.box(f"b.j{k}", (0.14, 0.12, 0.26 + 0.04 * k), (x0 + 0.62 + 0.11 * k, -0.6, 0.45), kit.plastic(["#c0392b", "#d9b44a", "#5a7fa8", "#a6a08c", "#7a5a3a", "#6b4a6e"][k], 0.6), bevel=0.02)


def build_coachwin(kit, M, ctx):
    x0 = 160.0
    kit.box("cw.wall", (0.1, 2.8, 2.2), (x0 + 1.65, 0.0, 1.1), kit.plastic("#5b6070", 0.9))
    kit.box("cw.back", (3.2, 0.1, 2.2), (x0, 1.4, 1.1), kit.plastic("#5b6070", 0.9))
    kit.box("cw.seat", (1.0, 0.7, 0.5), (x0 + 1.05, 0.0, 0.25), kit.plastic("#48506a", 0.9), bevel=0.06)
    kit.box("cw.sback", (1.0, 0.18, 0.9), (x0 + 1.05, 0.42, 0.95), kit.plastic("#48506a", 0.9), bevel=0.06)
    sky = kit.emit("#b9cfe8", 0.9, "cw.sky")
    kit.box("cw.glass", (0.03, 1.3, 0.95), (x0 + 1.6, -0.05, 1.45), sky)
    kit.box("cw.fr1", (0.05, 1.5, 0.08), (x0 + 1.58, -0.05, 1.96), M.black)
    kit.box("cw.fr2", (0.05, 1.5, 0.08), (x0 + 1.58, -0.05, 0.94), M.black)
    kit.box("cw.fr3", (0.05, 0.08, 1.1), (x0 + 1.58, -0.78, 1.45), M.black)
    kit.box("cw.fr4", (0.05, 0.08, 1.1), (x0 + 1.58, 0.68, 1.45), M.black)
    kit.light("boot lamp", "POINT", (0.0, 3.0, 1.9), 200, "#fff0d8", size=0.4)
    kit.light("coach lamp", "POINT", (x0 + 0.2, -0.9, 2.3), 150, "#ffe6c4", size=0.5)


# ------------------------------------------------------------------------------------------------ the Tilted
def build_tilted_clothes(kit, M):
    """Rust overalls (a bib and straps) and a tarp sheet tied round the shoulders with a cord, worn like a coat."""
    tor = bpy.data.objects.get("tilted.torso")
    if tor is None:
        return
    K = 0.82   # the Tilted's body_width: a narrower, taller trunk than the cast's
    kit.box("tilted.bib", (1.2 * K, 0.08, 1.15), (0, -0.54, 0.95), M.rust, tor, bevel=0.03)
    for sx in (-1, 1):
        kit.box(f"tilted.strap{sx}", (0.22, 0.09, 0.55), (sx * 0.48 * K, -0.54, 1.72), M.rust, tor, bevel=0.02)
        kit.box(f"tilted.pocket{sx}", (0.4 * K, 0.09, 0.4), (sx * 0.38 * K, -0.55, 0.5), M.rust, tor, bevel=0.02)
    cord = kit.plastic("#d4c7a0", 0.8)
    # the tarp, draped: thin sheets that slope off each shoulder, a hanging front flap each side of the bib, a back
    # panel and thin ridges for folds. Nothing here is a thick roll.
    for sx in (-1, 1):
        kit.box(f"tilted.shoulder{sx}", (1.2 * K, 1.2, 0.09), (sx * 0.9 * K, 0.02, 1.93), M.tarp, tor,
                rot=(0, math.radians(sx * 12), 0), bevel=0.03)
        kit.box(f"tilted.flap{sx}", (0.46 * K, 0.1, 1.15), (sx * 0.76 * K, -0.58, 1.2), M.tarp, tor,
                rot=(math.radians(-5), 0, math.radians(sx * -4)), bevel=0.03)
        kit.box(f"tilted.capes{sx}", (0.1, 1.15, 1.0), (sx * 1.42 * K, 0.04, 1.4), M.tarp, tor,
                rot=(0, math.radians(sx * 6), 0), bevel=0.03)
    kit.box("tilted.capeb", (2.4 * K, 0.12, 2.0), (0, 0.58, 1.0), M.tarp, tor, rot=(math.radians(-4), 0, 0), bevel=0.05)
    kit.box("tilted.cord", (1.7 * K, 0.07, 0.07), (0, -0.56, 1.66), cord, tor)
    kit.box("tilted.knot", (0.24, 0.1, 0.24), (0.1, -0.6, 1.62), cord, tor, bevel=0.03)
    # a neck block between the shoulders and the hanging head, placed every frame in animate()
    kit.box("tilted.nk", (0.7, 0.62, 1.0), (0, 0, 2.0), kit.plastic("#85704f", 0.5), tor, bevel=0.1)


# ------------------------------------------------------------------------------------------------ build
def build_props(kit, M, ctx):
    """CC0 props (2026-11-03): trees behind the hedges, a chair, a stool, a lamp, a sideboard and a pot plant at each
    neighbouring stall, bins and logs in the aisle. Our stall (k = 0) is left alone for the cameras."""
    rnd = random.Random(77)
    trees = ["commontree_1", "commontree_2", "birchtree_1", "commontree_1", "birchtree_1"]
    for i in range(14):
        x = -52 + i * 8.0 + rnd.uniform(-1.5, 1.5)
        kit.prop(trees[i % 5], (x, -20.5 + rnd.uniform(-1, 1), 0), rot=rnd.uniform(0, 360), height=rnd.uniform(6.0, 8.0))
        kit.prop(trees[(i + 2) % 5], (x + 3.5, 15.5 + rnd.uniform(-1, 1), 0), rot=rnd.uniform(0, 360), height=rnd.uniform(6.5, 8.5))
    for i in range(10):
        x = -40 + i * 9.0 + rnd.uniform(-2, 2)
        if abs(x + 16) < 4:
            continue
        kit.prop("bush_2" if i % 2 else "bush_1", (x, -17.4, 0), rot=rnd.uniform(0, 360), height=rnd.uniform(1.0, 1.4))
    for i, x in enumerate(ROW_A_X):
        k = round(x / 4.6)
        if k == 0:
            continue
        s = 1 if i % 2 else -1
        kit.prop("chair_1" if i % 2 else "chair_2", (x + s * 1.55, 1.0, 0), rot=170 + rnd.uniform(-25, 25), height=0.86)
        kit.prop("light_floor1", (x - s * 1.5, 1.3, 0), rot=rnd.uniform(0, 360), height=1.25)
        kit.prop("drawer_1", (x + s * 2.4, 0.2, 0), rot=0, height=0.7)
        kit.prop("houseplant_1" if i % 2 else "light_desk", (x + s * 2.4, 0.2, 0.7), rot=rnd.uniform(0, 360), height=0.32)
        if i % 3 == 1:
            kit.prop("stool", (x + s * 1.2, 1.7, 0), rot=rnd.uniform(0, 360), height=0.6)
        if k != -2 and i % 2 == 0:
            kit.prop("houseplant_1", (x - 0.7, 0.0, 0.785), rot=rnd.uniform(0, 360), height=0.3)
    for j, x in enumerate(ROW_B_X):
        s = 1 if j % 2 else -1
        kit.prop("chair_2" if j % 2 else "chair_1", (x + s * 1.5, -8.9, 0), rot=rnd.uniform(-20, 20), height=0.86)
        kit.prop("shelf_1", (x + s * 2.1, -9.3, 0), rot=rnd.uniform(-10, 10), height=1.5)
        kit.prop("table_roundsmall", (x - s * 1.9, -9.3, 0), rot=0, height=0.57)
        kit.prop("light_desk", (x + 0.7, -9.6, 0.785), rot=rnd.uniform(0, 360), height=0.3)
    for p in [(3.2, -5.6), (-6.2, -6.4), (12.5, -7.2), (-18.5, -7.0), (-3.0, 7.8)]:
        kit.prop("trashcan_cylindric", (p[0], p[1], ground(p[0], p[1])), rot=rnd.uniform(0, 360), height=0.6)
    kit.prop("nat_log_stack", (-20.5, -13.2, 0), rot=95, height=0.9)
    kit.prop("treestump", (18.5, -13.5, 0), rot=30, height=0.7)


def build(kit, story, tl):
    M = Pal(kit)
    ctx = {"M": M}
    w = bpy.context.scene.world
    nt = w.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.55
    mr.clamp = True
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], nt.nodes["Background"].inputs["Color"])
    ctx["sky"] = (ramp, nt.nodes["Background"])
    build_terrain(kit, M)
    build_hedge(kit, M)
    build_gate(kit, M)
    ctx["gate"] = bpy.data.objects["gate"]
    build_shelter(kit, M)
    build_row(kit, M, ctx)
    build_stall(kit, M, ctx)
    build_goods(kit, M, ctx)
    build_sofa(kit, M, 11.0, -4.6)
    build_props(kit, M, ctx)
    build_house(kit, M, ctx)
    build_room(kit, M, ctx, ROOMS["kitchen"], "kitchen")
    build_room(kit, M, ctx, ROOMS["bedroom"], "bedroom")
    build_coachwin(kit, M, ctx)
    # moving vehicles
    veh = {}
    veh["estate2"] = (make_estate(kit, M, "estate2", 0, 0, 0, False), [])
    veh["estate2"][0].location = (0, 0, -60)
    veh["bus"] = make_bus(kit, M, "bus", "#c97a2a")
    veh["coach"] = make_bus(kit, M, "coach", "#c9ccd2", True)
    ctx["veh"] = veh
    # sun, character fill, bus beams
    sun = kit.light("sun", "SUN", (30, 10, 30), 1.0, "#fff0d8", size=0.02)
    kit.aim(sun, (0, 0, 0))
    ctx["sun"] = sun
    fill = kit.light("char fill", "SUN", (-20, -24, 22), 1.0, "#b4c6ea", size=0.02)
    kit.aim(fill, (0, 0, 0))
    ctx["fill"] = fill
    rim = kit.light("rim", "SUN", (-10, 25, 12), 1.0, "#ffc88a", size=0.02)
    kit.aim(rim, (0, 0, 0))
    ctx["rim"] = rim
    # a low warm lamp (the radio's glow) that lights the Tilted's face from below while it is in the chair
    kit.light("boot front", "POINT", (0.55, 1.75, 1.7), 1.0, "#fff0d8", size=0.7, shadow=False)
    kit.light("tilt up", "POINT", (-1.0, -0.9, 1.15), 1.0, "#ffd9a8", size=0.35)
    for nm in ("bus", "coach"):
        b = kit.light(f"{nm} beam", "SPOT", (0, 0, -60), 1.0, "#ffd9a0", size=0.3, spot=50, blend=0.6)
        ctx[f"{nm}_beam"] = b
    ctx["inited"] = False
    return ctx


# ------------------------------------------------------------------------------------------------ animate
def light_only(kit, coll, light_name, objs):
    col = bpy.data.collections.get(coll) or bpy.data.collections.new(coll)
    for ob in objs:
        if ob.name not in col.objects:
            col.objects.link(ob)
    for co in col.collection_objects:
        co.light_linking.link_state = "INCLUDE"
    kit.LIGHTS[light_name]["obj"].light_linking.receiver_collection = col


def decorate(kit, story, ctx):
    """After the cast exists: clothes on the Tilted, a moustache, glasses, caps, the fog nodes, the fill's link."""
    M = ctx["M"]
    build_tilted_clothes(kit, M)
    hg = bpy.data.objects.get("walter.headg")
    if hg is not None:
        kit.box("walter.mous", (0.5, 0.1, 0.1), (0, -faces.HEAD_R - 0.01, -0.15), kit.plastic("#ece9e2", 0.8), hg, bevel=0.03)
        for sx in (-1, 1):
            kit.box(f"walter.mousend{sx}", (0.1, 0.08, 0.2), (sx * 0.25, -faces.HEAD_R, -0.22), kit.plastic("#ece9e2", 0.8), hg, bevel=0.03)
    hg = bpy.data.objects.get("haggler.headg")
    if hg is not None:
        cap = kit.plastic("#4a4540", 0.9)
        kit.box("haggler.cap", (2 * faces.HEAD_R + 0.2, 2 * faces.HEAD_R + 0.2, 0.2), (0, 0.0, faces.HEAD_H / 2 + 0.1), cap, hg, bevel=0.08)
        kit.box("haggler.capb", (0.9, 0.4, 0.06), (0, -faces.HEAD_R - 0.1, faces.HEAD_H / 2 + 0.02), cap, hg, bevel=0.02)
    # the Tilted: a short neck block under the rolled head so it doesn't float
    chars = []
    for who in ctx["cast_names"]:
        r = bpy.data.objects.get(who)
        if r is not None:
            chars += [o for o in r.children_recursive if o.type == "MESH"]
    ts_ = bpy.data.objects.get("tarpstrip")
    if ts_ is not None:
        chars.append(ts_)   # the strip on the chair arm takes the same fog daylight as the cast (S42)
    if chars:
        light_only(kit, "chars", "char fill", chars)
        light_only(kit, "chars2", "rim", chars)
    d0 = story["look"]["fog_density"]
    fc = _lin(_hex(FOGC))
    dens, ems = [], []
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        for n in m.node_tree.nodes:
            if n.type == "MATH" and n.operation == "MULTIPLY" and abs(n.inputs[1].default_value + d0) < 1e-6:
                dens.append(n)
            elif n.type == "EMISSION":
                c = n.inputs["Color"].default_value
                if all(abs(c[i] - fc[i]) < 0.02 for i in range(3)) and abs(n.inputs["Strength"].default_value - 1.0) < 1e-6:
                    ems.append(n)
    ctx["fog_dens"], ctx["fog_ems"] = dens, ems
    # cloth materials by character, so a coat can change colour
    cm = {}
    for who, spec in story["cast"].items():
        m = bpy.data.materials.get(f"cloth {spec['shirt']} {spec.get('pattern', 'solid')} {spec.get('pattern_c', '#202020')}")
        if m is not None:
            cm[who] = m
    flat = bpy.data.materials.get("plastic #8a8d90 pipflat")
    cm["pipflat"] = flat if flat is not None else bpy.data.materials.get("pipflat")
    ctx["cloth"] = cm
    ctx["inited"] = True


def tod_state(tl, t):
    cs = [c for c in _cues(tl, "tod") if c["t"] <= t + 1e-9]
    cur = cs[-1]["set"] if cs else "day"
    prev = cs[-2]["set"] if len(cs) > 1 else cur
    u = 1.0
    if cs and float(cs[-1].get("dur", 0)) > 0:
        u = _ss((t - cs[-1]["t"]) / float(cs[-1]["dur"]))
    a, b = TOD[prev], TOD[cur]
    out = {}
    for k in a:
        if isinstance(a[k], str):
            out[k] = _mixc(_hex(a[k]), _hex(b[k]), u)
        else:
            out[k] = a[k] + (b[k] - a[k]) * u
    return out


def coat_colour(tl, who, base, t):
    """A coat's colour at t: the cast's own, then each "coat" cue fades it to a new one (dur 0 is a cut)."""
    cur = _hex(base)
    for c in _cues(tl, "coat"):
        if c["who"] != who or c["t"] > t + 1e-9:
            continue
        to = _hex(c["to"])
        d = float(c.get("dur", 0.0))
        if d <= 0 or t >= c["t"] + d:
            cur = to
        else:
            return _mixc(cur, to, _ss((t - c["t"]) / d))
    return cur


def ramp_level(cs, t, default=0.0):
    """A level cue {"to": v, "dur": s}: eases from the last level to the new one over dur."""
    level = prev = default
    for c in cs:
        if c["t"] > t + 1e-9:
            break
        prev, level = level, c["to"]
        d = float(c.get("dur", 0.0))
        if d > 0 and t < c["t"] + d:
            level = prev + (level - prev) * _ss((t - c["t"]) / d)
    return level


def _sit(tl, who, t):
    v = False
    for k in tl["acting"].get(who, []):
        if "sit" in k and k["t"] <= t + 1e-9:
            v = bool(k["sit"])
    return v


def yaw_to(a, b):
    return math.atan2(b[0] - a[0], -(b[1] - a[1]))


def _set_emit(mat, strength):
    for n in mat.node_tree.nodes:
        if n.type == "EMISSION" and n.inputs["Color"].default_value[0] > 0.5 and n.inputs["Color"].default_value[1] > 0.3:
            n.inputs["Strength"].default_value = strength


def _frame(who, part, local):
    root = bpy.data.objects.get(who)
    ob = bpy.data.objects.get(f"{who}.{part}")
    if root is None or ob is None or root.hide_render:
        return None
    p = ob.matrix_world @ V(local)
    return p, root.matrix_world.to_euler("XYZ").z


def animate(kit, story, tl, t, ctx):
    bpy.context.view_layer.update()
    ctx.setdefault("cast_names", list(story["cast"].keys()))
    if not ctx["inited"]:
        decorate(kit, story, ctx)
    M = ctx["M"]
    # ---------------------------------------------------------------- light: sun, fill, sky and fog, all smooth ramps
    s = tod_state(tl, t)
    az, el = math.radians(s["az"]), math.radians(s["el"])
    d = V((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    ctx["sun"].location = tuple(d * 40)
    kit.aim(ctx["sun"], (0, 0, 0))
    ctx["sun"].data.color = _lin(s["sunc"])
    ctx["fill"].data.color = _lin(s["fillc"])
    ramp, bg = ctx["sky"]
    ramp.color_ramp.elements[0].color = (*_lin(s["hor"]), 1)
    ramp.color_ramp.elements[1].color = (*_lin(s["zen"]), 1)
    bg.inputs["Strength"].default_value = s["sky"] * 0.55
    for n in ctx["fog_dens"]:
        n.inputs[1].default_value = -s["fogd"]
    for n in ctx["fog_ems"]:
        n.inputs["Strength"].default_value = s["fogb"] * (0.75 + 0.25 * s["sky"] / 1.5)
    rd = V((math.cos(math.radians(62)) * math.cos(math.radians(24)), math.sin(math.radians(62)) * math.cos(math.radians(24)), math.sin(math.radians(24))))
    ctx["rim"].location = tuple(rd * 40)
    kit.aim(ctx["rim"], (0, 0, 0))
    over = {"sun": s["sun"], "char fill": s["fill"], "rim": s["rim"]}
    # ---------------------------------------------------------------- coats
    for who, mat in ctx["cloth"].items():
        if mat is None:
            continue
        spec = story["cast"].get(who, {"shirt": "#8a8d90"})
        c = coat_colour(tl, who, spec["shirt"], t)
        lc = _lin(c)
        for n in mat.node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                n.inputs["Base Color"].default_value = (*lc, 1)
        mat.diffuse_color = (*lc, 1)
    nc = _last([c for c in _cues(tl, "nocoat") if c["who"] == "pip"], t)
    for sx in (-1, 1):
        for part in (f"pip.coatm{sx}", "pip.zip", "pip.hooddown"):
            ob = bpy.data.objects.get(part)
            if ob is not None and nc is not None and nc.get("on"):
                ob.hide_render = True
    # ---------------------------------------------------------------- seated characters bend their legs
    for who in ctx["cast_names"]:
        r = bpy.data.objects.get(who)
        if r is None or r.hide_render:
            continue
        if _sit(tl, who, t):
            for sx in (-1, 1):
                leg = bpy.data.objects.get(f"{who}.leg{sx}")
                if leg is not None:
                    leg.rotation_euler = (-math.pi / 2, 0, 0)
    # ---------------------------------------------------------------- the Tilted
    tcs = [c for c in _cues(tl, "tilted") if c["t"] <= t + 1e-9]
    tc = dict(tcs[-1]) if tcs else {}
    if len(tcs) > 1 and float(tc.get("dur", 0)) > 0:   # a slow change: ease every number from the last pose (the lean)
        u = _ss((t - tcs[-1]["t"]) / float(tc["dur"]))
        for k in ("roll", "lift", "side", "pitch", "yawh", "lean", "fwd"):
            tc[k] = tcs[-2].get(k, 0.0) + (tc.get(k, 0.0) - tcs[-2].get(k, 0.0)) * u
    neck = bpy.data.objects.get("tilted.neck")
    tors = bpy.data.objects.get("tilted.torso")
    if neck is not None and tors is not None:
        roll = float(tc.get("roll", -90.0))
        neck.rotation_euler = (math.radians(tc.get("pitch", 0.0)), math.radians(roll), math.radians(tc.get("yawh", 0.0)))
        sgn = -1 if roll < 0 else 1
        neck.location = (sgn * tc.get("side", 0.38), tc.get("fwd", 0.0), 2.0 + tc.get("lift", 0.62))
        tors.rotation_euler = (math.radians(tc.get("lean", 0.0)), 0, 0)
        nk = bpy.data.objects.get("tilted.nk")
        if nk is not None:
            a0, b0 = V((0, 0, 1.85)), V(neck.location)
            dd = b0 - a0
            nk.location = tuple((a0 + b0) / 2)
            nk.rotation_euler = dd.to_track_quat("Z", "Y").to_euler()
            nk.scale = (1, 1, max(0.2, dd.length))
    # the fog glimpse (S39, S40): the Tilted is a flat dark shape, no face and no colour
    if "tsil_orig" not in ctx:
        ctx["tsil_orig"] = {o: list(o.data.materials) for o in bpy.data.objects
                            if o.name.startswith("tilted.") and o.type == "MESH"}
        ctx["tsil_mat"] = kit.plastic("#1b212d", 0.95, "tsil")
    sil = bool((_last(_cues(tl, "tsil"), t) or {}).get("on"))
    for o, mats in ctx["tsil_orig"].items():
        for i, m in enumerate(mats):
            o.data.materials[i] = ctx["tsil_mat"] if sil else m
    # ---------------------------------------------------------------- goods turned toward Pip's chair
    gc = _last(_cues(tl, "goods"), t) or {"mode": "straight"}
    for k, (nm, (root, gx, gy)) in enumerate(ctx["goods"].items()):
        root.location.z = -40.0 if gc["mode"] == "away" else 0.785
        if gc["mode"] == "turned":
            yaw = yaw_to((gx, gy), CHAIR_P)
        elif gc["mode"] == "chaos":
            yaw = math.radians([30, -70, 150, -20, 95][k % 5])
        else:
            yaw = math.radians([6, -8, 4, -5, 10][k % 5])
        root.rotation_euler = (0, 0, yaw)
    _show([ctx["mug3"]], bool((_last(_cues(tl, "mug3"), t) or {}).get("on")))
    _show([ctx["tarpstrip"]], bool((_last(_cues(tl, "tarp"), t) or {}).get("on")))
    # the radio's dial lamp ramps (0.5 s) and the bus beams ramp (1 s)
    lv = ramp_level(_cues(tl, "lamp"), t)
    _set_emit(ctx["dial"], 0.9 * lv)
    # ---------------------------------------------------------------- Pip's coat laid on the table, an arm or the bench
    pf = ctx["pipflat"]
    pc = _last(_cues(tl, "pipflat"), t) or {"where": "off"}
    if pc["where"] == "table":
        pf.location = (-0.15, 0.0, 0.785)
        pf.rotation_euler = (0, 0, math.radians(pc.get("yaw", 8)))
        pf.scale = (1, 1, 1)
    elif pc["where"] == "bench":
        pf.location = (-13.25 + pc.get("dx", 0.0), -28.0 + pc.get("dy", 0.55), 0.58)
        pf.rotation_euler = (0, 0, math.radians(90))
    elif pc["where"] == "arm":
        f = _frame("me", "arm1", (0, 0, -1.2))
        if f:
            pf.location = f[0] + V((0, 0, 0.0))
            pf.rotation_euler = (math.radians(90), 0, f[1])
        else:
            pf.location = (0, 0, -40)
    else:
        pf.location = (0, 0, -40)
    # ---------------------------------------------------------------- the holdall
    bc = _last(_cues(tl, "bag"), t) or {"where": "off"}
    bg_ = ctx["bag"]
    if bc["where"] == "shelter":
        bg_.location = (-14.1, -29.1, 0.1)
        bg_.rotation_euler = (0, 0, math.radians(90))
    elif bc["where"] == "boot":
        bg_.location = (0.0, 3.0, 1.03)
        bg_.rotation_euler = (0, 0, 0)
    elif bc["where"] == "pos":
        bg_.location = (bc["pos"][0], bc["pos"][1], bc.get("z", 0.0))
        bg_.rotation_euler = (0, 0, math.radians(bc.get("yaw", 0)))
    else:
        bg_.location = (0, 0, -40)
    # ---------------------------------------------------------------- our tailgate, the folded chair, the latch strokes
    tg = bpy.data.objects.get("estate.tgp")
    if tg is not None:
        a = ramp_level(_cues(tl, "hatch"), t, -125.0)
        tg.rotation_euler = (math.radians(a), 0, 0)
    _show(ctx["strokes"], bool((_last(_cues(tl, "strokes"), t) or {}).get("on")))
    fold_on = bool((_last(_cues(tl, "fold"), t) or {}).get("on"))
    _show([ctx["fold"]], fold_on)
    ch = bpy.data.objects.get("chairL")
    if ch is not None:
        _show([ch], not fold_on)
    # ---------------------------------------------------------------- vehicles
    names = ["estate2", "bus", "coach"]
    for nm in names:
        root = ctx["veh"][nm][0] if isinstance(ctx["veh"][nm], tuple) else ctx["veh"][nm]
        cs = [c for c in _cues(tl, "veh") if c["id"] == nm and c["t"] <= t + 1e-9]
        beam = ctx.get(f"{nm}_beam")
        if not cs or cs[-1].get("hide"):
            root.location = (0, 0, -60)
            if beam is not None:
                beam.location = (0, 0, -60)
            continue
        c = cs[-1]
        du = max(1e-6, float(c.get("dur", 1.0)))
        u = min(1.0, (t - c["t"]) / du)
        x = c["p0"][0] + (c["p1"][0] - c["p0"][0]) * u
        y = c["p0"][1] + (c["p1"][1] - c["p0"][1]) * u
        yaw = math.radians(c["yaw"])
        z = ground(x, y)
        root.location = (x, y, z + 0.02)
        dy = ground(x, y - 0.5 * (1 if c["yaw"] < 90 else -1)) - ground(x, y + 0.5 * (1 if c["yaw"] < 90 else -1))
        pitch = math.atan2(dy, 1.0) * (1 if c["yaw"] < 90 else -1)
        root.rotation_euler = (0, 0, yaw)
        if beam is not None:
            L = 7.0 if nm == "bus" else 9.0
            fwd = V((math.sin(yaw), -math.cos(yaw), 0))
            # these are built facing +y at yaw 0; a yaw of 180 turns the front toward -y
            fwd = V((-math.sin(yaw), math.cos(yaw), 0))
            beam.location = (x + fwd.x * (L + 0.1), y + fwd.y * (L + 0.1), z + 0.8)
            kit.aim(beam, (x + fwd.x * (L + 8.0), y + fwd.y * (L + 8.0), z + 0.1))
    bl = ramp_level(_cues(tl, "beam"), t)
    over["bus beam"] = 1500.0 * bl
    over["boot lamp"] = 1.0 + 1.0 * ramp_level(_cues(tl, "bootb"), t)
    over["boot front"] = 130.0 * ramp_level(_cues(tl, "bootb"), t)
    over["tilt up"] = 160.0 * ramp_level(_cues(tl, "tup"), t)
    over["coach beam"] = 0.0
    over["strip fill"] = 2600.0 * ramp_level(_cues(tl, "tfill"), t)
    over["shelter fill"] = 250.0 * ramp_level(_cues(tl, "sfill"), t)
    for nm in ("bus",):
        lamps = ctx["veh"][nm][1]
        for m in lamps:
            _set_emit(m, 2.0 * bl)
    return over
