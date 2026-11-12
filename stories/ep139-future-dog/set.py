"""ep139 "future dog": my ground-floor apartment patio (gold evening, then the same patio at sunrise), a leafy side
street at 7:40 a.m. with Theo's yellow house and a plain white moving van, and two montage spots (a neighbor's front
step, Sam's driveway with a red hatchback). No dark scene anywhere, no light ever switches on camera.

The rule meter is the ep124 cream tag on the camera (top-left, placed by the engine's hud): a wall-phone glyph and a big
"1"; at L14 a call timer (MM:SS); at L23 the big digit comes back as "0"; from L28 a small clock readout under it.
Numerals and glyphs only.

Cues read by animate():
  timer   mode (0 big digit, 1 MM:SS), s (seconds), big (the big digit)
  clock   on (0/1), h, m
  phone   mode (0 home screen, 1 call screen), buzz (0..1)
  gate    open (0..1), latch (0..1)
  dog     a key per cue: x, y, z, yaw, sit, lie, up, hy, hp, tongue, glide (1: travel from the key before)
  achoo   a sneeze starts at the cue's time (Noodle dips his head over 0.4 s, ears flap)
  leash   on (0/1), arm (the arm angle of the hand that holds it)
  sit_me / squat_theo   s (0..1)
  steam   on (0/1)
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layout as G  # noqa: E402

D2R = math.pi / 180.0
W = {}
SIT = -math.pi / 2 * 0.97


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def noshadow(ob):
    ob.visible_shadow = False
    for c in ob.children_recursive:
        c.visible_shadow = False


def sample(name, tl, t, defaults):
    """The state of cue track `name` at t: numeric fields eased over a cue's own "dur"."""
    cur, prev = dict(defaults), dict(defaults)
    for c in tl["cues"]:
        if c["name"] != name:
            continue
        if c["t"] > t:
            break
        prev = dict(cur)
        cur.update({k: v for k, v in c.items() if k in defaults})
        dur = c.get("dur", 0.0)
        if dur > 0 and t < c["t"] + dur:
            u = ss((t - c["t"]) / dur)
            return {k: (prev[k] + (cur[k] - prev[k]) * u if isinstance(cur[k], (int, float)) else cur[k]) for k in cur}
    return cur


# ------------------------------------------------------------------------------------------------ the patio
def build_patio(kit):
    pl = kit.plastic
    kit.plane("lawn", (500, 500), (100, 0, -0.04), pl("#62c45a", 0.9, spec=0.05))
    kit.box("patio.slab", (9.0, 6.4, 0.1), (0, 1.3, -0.05), kit.texture("brick", 1.2, tint="#f2dcc0"))
    for i in range(-4, 5):
        pass
    # the brick wall behind, a high soffit overhanging the whole back half (a ceiling behind every low angle)
    kit.box("patio.wall", (9.2, 0.3, 3.6), (0, 3.95, 1.8), kit.texture("brick", 1.0, tint="#e8b79c"))
    for sx in (-1, 1):
        kit.box(f"patio.wallside{sx}", (0.3, 4.4, 3.6), (sx * 4.55, 2.0, 1.8), kit.texture("brick", 1.0, tint="#e8b79c"))
    kit.box("patio.soffit", (9.2, 2.3, 0.12), (0, 2.85, 2.74), pl("#d7c3a0", 0.8, spec=0.05))
    kit.box("patio.fascia", (9.2, 0.08, 0.34), (0, 1.74, 2.62), pl("#c9b08a", 0.7, spec=0.05))
    # the sliding door (glass, half open) and a window
    white = pl("#efe9da", 0.6)
    glass = pl("#a9d6e8", 0.15, spec=0.8)
    kit.box("patio.doorframe", (2.3, 0.06, 2.3), (1.8, 3.77, 1.15), white)
    kit.box("patio.doorglass", (1.0, 0.04, 2.1), (2.3, 3.735, 1.15), glass)
    kit.box("patio.dooropen", (1.0, 0.04, 2.1), (1.2, 3.725, 1.15), pl("#3b3a38", 0.6))   # the dark open half (interior)
    kit.box("patio.doormull", (0.06, 0.06, 2.2), (1.7, 3.74, 1.15), white)
    kit.box("patio.winframe", (1.6, 0.06, 1.2), (-2.0, 3.77, 1.5), white)
    kit.box("patio.winglass", (1.4, 0.04, 1.0), (-2.0, 3.735, 1.5), glass)
    # the wall lamp (decor, always on at the same warm glow)
    kit.box("patio.lampback", (0.16, 0.05, 0.3), (-0.9, 3.77, 2.0), pl("#5a4a3a", 0.5))
    kit.box("patio.lamp", (0.12, 0.1, 0.22), (-0.9, 3.7, 2.0), kit.emit("#ffc873", 0.7, "lampglow"))
    # fences: low white pickets east (with the gate gap) and west
    pk = pl("#ece6d6", 0.6, spec=0.1)
    rail = pl("#e4dcc8", 0.6, spec=0.1)

    def fence(x, y0, y1, name):
        n = int((y1 - y0) / 0.16)
        for i in range(n + 1):
            y = y0 + i * (y1 - y0) / max(1, n)
            kit.box(f"{name}.p{i}", (0.05, 0.08, 0.86), (x, y, 0.43), pk)
        ln = y1 - y0
        kit.box(f"{name}.rtop", (0.07, ln + 0.1, 0.06), (x - 0.045, (y0 + y1) / 2, 0.8), rail)
        kit.box(f"{name}.rlow", (0.07, ln + 0.1, 0.06), (x - 0.045, (y0 + y1) / 2, 0.22), rail)

    fence(3.0, -1.4, G.GATE_Y0 - 0.12, "fenceE1")
    fence(3.0, G.GATE_Y1 + 0.12, 3.7, "fenceE2")
    fence(-3.0, -1.4, 3.7, "fenceW")
    for y in (G.GATE_Y0 - 0.1, G.GATE_Y1 + 0.1):
        kit.box(f"gatepost{y}", (0.12, 0.12, 1.0), (3.0, y, 0.5), pl("#d9d1bb", 0.6))
    # the gate: a wooden leaf hinged at y 1.4; the leaf extends toward -y and swings out east
    hinge = kit.empty("gate.hinge", (3.0, G.GATE_Y1, 0.0))
    W["hinge"] = hinge
    wood = pl("#b9874f", 0.65)
    wood2 = pl("#a67840", 0.7)
    for i in range(7):
        kit.box(f"gate.slat{i}", (0.04, 0.11, 0.84), (0, -0.07 - i * 0.145, 0.45), wood, hinge)
    kit.box("gate.rtop", (0.03, 1.0, 0.07), (-0.035, -0.5, 0.78), wood2, hinge)
    kit.box("gate.rlow", (0.03, 1.0, 0.09), (-0.035, -0.5, 0.4), wood2, hinge)
    kit.box("gate.rmid", (0.03, 1.0, 0.06), (-0.035, -0.5, 0.12), wood2, hinge)
    # the lore tally: three short chalk strokes on the inside of the lower rail, at Noodle's eye level
    chalk = pl("#f3f0e6", 0.9)
    for k in range(3):
        kit.box(f"gate.tally{k}", (0.012, 0.025, 0.16), (-0.062, -0.4 - k * 0.1, 0.4), chalk, hinge)
    kit.box("gate.mat", (0.9, 1.3, 0.025), (2.35, 0.9, 0.012), pl("#8a5a3a", 0.9))
    kit.box("gate.mat2", (0.78, 1.18, 0.028), (2.35, 0.9, 0.014), pl("#b07a4e", 0.9))
    # the latch: a thumb bar pivoting on a bolt near the free end, lifted by Noodle's nose
    lp = kit.empty("gate.latchpiv", (-0.06, -0.88, 0.55), hinge)
    W["latch"] = lp
    kit.box("gate.latchbar", (0.025, 0.2, 0.035), (0, 0.08, 0), pl("#3a3a3e", 0.4, spec=0.6), lp)
    kit.cyl("gate.latchbolt", 0.022, 0.03, (-0.01, 0, 0), pl("#8a8e96", 0.3, spec=0.8), lp, rot=(0, math.pi / 2, 0), n=10)
    kit.box("gate.catch", (0.04, 0.06, 0.05), (3.0 - 0.06, G.GATE_Y0 - 0.1, 0.55), pl("#3a3a3e", 0.4, spec=0.6))
    # a string of unlit bulbs along the west fence (decor only)
    kit.box("bulbs.wire", (0.015, 5.0, 0.015), (-2.9, 1.2, 1.35), pl("#3a3a3e", 0.6))
    for i in range(10):
        kit.sphere(f"bulbs.b{i}", 0.05, (-2.9, -1.0 + i * 0.5, 1.28), pl("#f6e7b5", 0.3, spec=0.5), seg=8)
    # plants
    kit.prop("nat_pot_large", (-2.4, 3.1, 0), height=0.5, tint="#e8d8c0")
    kit.prop("houseplant_1", (-2.4, 3.1, 0.5), height=0.7)
    kit.prop("houseplant_1", (3.7, -0.8, 0), height=0.9)
    kit.prop("bush_1", (-5.2, 1.0, 0), height=1.3, tint="#d4f0c4")
    kit.prop("bush_2", (5.3, 3.2, 0), height=1.2, tint="#d4f0c4")
    kit.prop("bush_1", (5.5, -2.5, 0), height=1.1, tint="#d4f0c4")
    kit.prop("commontree_1", (-8.0, 4.5, 0), rot=20, height=6.0, tint="#d4f0c4")
    # table and chairs
    tx, ty = G.TABLE
    top = pl("#d8bf8e", 0.55, spec=0.1)
    kit.cyl("table.top", G.TABLE_R, 0.05, (tx, ty, G.TABLE_Z - 0.025), top, n=28)
    kit.cyl("table.leg", 0.06, G.TABLE_Z - 0.05, (tx, ty, (G.TABLE_Z - 0.05) / 2), pl("#8a8e96", 0.5), n=10)
    kit.cyl("table.base", 0.3, 0.04, (tx, ty, 0.02), pl("#8a8e96", 0.5), n=16)
    chair(kit, "chairA", G.ME_SEAT[0], G.ME_SEAT[1], 0.0, pl)
    chair(kit, "chairB", G.CHAIR2[0], G.CHAIR2[1], 90.0, pl)


def chair(kit, name, x, y, rot_deg, pl):
    """A wooden chair facing -y at rot 0 (back on the +y side); rot_deg turns it about its seat centre."""
    wood = pl("#a6764a", 0.7)
    root = kit.empty(name, (x, y, 0), rot=(0, 0, rot_deg * D2R))
    kit.box(f"{name}.seat", (0.46, 0.46, 0.05), (0, 0, G.SEAT_H - 0.025), wood, root)
    kit.box(f"{name}.back", (0.46, 0.04, 0.46), (0, 0.22, G.SEAT_H + 0.24), wood, root)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"{name}.leg{sx}{sy}", (0.05, 0.05, G.SEAT_H - 0.05), (sx * 0.2, sy * 0.2, (G.SEAT_H - 0.05) / 2), wood, root)


# ------------------------------------------------------------------------------------------------ the phone
def build_phone(kit):
    pl = kit.plastic
    px, py, pz = G.PHONE
    root = kit.empty("phone", (px, py, pz))
    W["phone"] = root
    root.scale = (2.2, 2.2, 2.2)
    kit.box("phone.body", (0.085, 0.172, 0.011), (0, 0, -0.0045), pl("#2a2a30", 0.35, spec=0.5), root, bevel=0.006)
    kit.box("phone.cam", (0.016, 0.016, 0.004), (0.0, 0.07, -0.0105), pl("#111114", 0.3), root)
    # the home screen: a speech bubble and a paw on deep blue
    home = kit.empty("phone.home", (0, 0, 0.0015), root)
    blue = kit.emit("#2f5fb0", 0.9, "screenblue")
    cream = kit.emit("#fff1d0", 1.0, "screencream")
    kit.box("phone.homebg", (0.075, 0.158, 0.002), (0, 0, 0), blue, home)
    kit.box("phone.bub", (0.05, 0.036, 0.002), (0, 0.04, 0.0025), cream, home, bevel=0.004)
    kit.box("phone.bubtail", (0.012, 0.012, 0.002), (-0.012, 0.016, 0.0025), cream, home, rot=(0, 0, 0.785))
    kit.cyl("phone.pad", 0.013, 0.002, (0, -0.03, 0.0025), cream, home, n=12)
    for k, (dx, dy) in enumerate(((-0.022, -0.006), (-0.008, 0.004), (0.008, 0.004), (0.022, -0.006))):
        kit.cyl(f"phone.toe{k}", 0.006, 0.002, (dx, -0.012 + dy, 0.0025), cream, home, n=8)
    # the call screen: teal with a white handset
    call = kit.empty("phone.call", (0, 0, 0.0015), root)
    teal = kit.emit("#14867a", 1.0, "screenteal")
    wh = kit.emit("#ffffff", 1.2, "screenwhite")
    kit.box("phone.callbg", (0.075, 0.158, 0.002), (0, 0, 0), teal, call)
    kit.cyl("phone.calldisc", 0.026, 0.002, (0, 0.0, 0.0025), kit.emit("#0d6258", 1.0, "screendisc"), call, n=20)
    kit.box("phone.hs1", (0.012, 0.04, 0.002), (0, 0.0, 0.0035), wh, call, rot=(0, 0, 0.0), bevel=0.003)
    kit.box("phone.hs2", (0.018, 0.012, 0.002), (0.006, 0.018, 0.0035), wh, call, bevel=0.003)
    kit.box("phone.hs3", (0.018, 0.012, 0.002), (0.006, -0.018, 0.0035), wh, call, bevel=0.003)
    W["home"], W["call"] = home, call
    sk = pl("#c98f64", 0.6)
    fg = kit.empty("finger", (0, -80, 0))
    W["finger"] = fg
    kit.box("finger.tip", (0.034, 0.12, 0.028), (0, -0.06, 0.0), sk, fg, bevel=0.012)
    kit.box("finger.hand", (0.1, 0.16, 0.04), (0.02, -0.2, 0.02), sk, fg, bevel=0.02)
    # the framed photo on the table: a standing frame, a blue backdrop, Theo (a tiny cast member) and a tiny Noodle
    fx, fy = G.PHOTO
    fr = kit.empty("photo", (fx, fy, G.TABLE_Z))
    W["photo"] = fr
    # a dark wooden frame (four bars, standing proud of the picture) on a slanted stand, so it reads as a printed photo
    darkw = pl("#2a1c14", 0.55, spec=0.1)
    kit.box("photo.frame", (0.62, 0.05, 0.60), (0, 0.016, 0.3), pl("#1f1610", 0.6), fr, bevel=0.01)   # the back board
    kit.box("photo.back", (0.54, 0.02, 0.52), (0, -0.016, 0.3), pl("#8fc7ea", 0.6), fr)
    kit.box("photo.grass", (0.54, 0.02, 0.07), (0, -0.0175, 0.065), pl("#6cc15e", 0.7), fr)
    for nm, sz, loc in (("t", (0.62, 0.05, 0.05), (0, -0.03, 0.575)), ("b", (0.62, 0.05, 0.05), (0, -0.03, 0.025)),
                        ("l", (0.05, 0.05, 0.6), (-0.285, -0.03, 0.3)), ("r", (0.05, 0.05, 0.6), (0.285, -0.03, 0.3))):
        kit.box(f"photo.bar{nm}", sz, loc, darkw, fr, bevel=0.008)
    kit.box("photo.stand", (0.05, 0.22, 0.03), (0, 0.11, 0.03), darkw, fr, rot=(0.0, 0, 0))
    kit.box("photo.easel", (0.05, 0.03, 0.42), (0, 0.1, 0.2), darkw, fr, rot=(-0.4, 0, 0))
    pd = build_dog(kit, "pdog", fr)
    W["pdog"] = pd
    pd["root"].location = (0.2, -0.045, 0.03)
    pd["root"].scale = (0.52, 0.52, 0.52)
    pd["tail"].rotation_euler = (-0.5, 0, 0)


# ------------------------------------------------------------------------------------------------ Noodle
def build_dog(kit, name, parent=None):
    """A blocky beagle, about 0.45 m at the back, facing -y. Returns the parts animate() moves."""
    pl = kit.plastic
    tan = pl("#d79a55", 0.6)
    tan2 = pl("#c98a45", 0.6)
    white = pl("#f6efe2", 0.6)
    brown = pl("#6a3a1e", 0.6)
    black = pl("#17120e", 0.45, spec=0.5)
    red = pl("#d8322f", 0.5)
    pink = pl("#e8788a", 0.5)
    root = kit.empty(name, (0, -80, 0), parent)
    PV = (0.0, 0.25, 0.15)            # the pitch pivot (the hips), in root coordinates
    bg = kit.empty(f"{name}.bodyg", PV, root)

    def B(nm, size, loc, mat, par=None, rot=(0, 0, 0), bevel=0.0):
        p = par or bg
        if par is None:
            loc = (loc[0] - PV[0], loc[1] - PV[1], loc[2] - PV[2])
        return kit.box(f"{name}.{nm}", size, loc, mat, p, rot, bevel)

    B("body", (0.22, 0.56, 0.24), (0, 0.0, 0.33), tan, bevel=0.05)
    B("belly", (0.2, 0.4, 0.05), (0, -0.02, 0.215), white, bevel=0.02)
    B("saddle", (0.23, 0.3, 0.05), (0, 0.06, 0.435), brown, bevel=0.02)
    B("chest", (0.2, 0.14, 0.22), (0, -0.2, 0.34), white, bevel=0.05)
    B("collar", (0.235, 0.05, 0.25), (0, -0.28, 0.35), red, bevel=0.015)
    B("clip", (0.08, 0.06, 0.1), (0, -0.30, 0.485), pl("#cfd2d6", 0.25, spec=0.9), bevel=0.01)
    # the tail pivots at the rump; the white tip
    tail = kit.empty(f"{name}.tail", (0, 0.28 - PV[1], 0.4 - PV[2]), bg)
    kit.box(f"{name}.tailb", (0.045, 0.045, 0.24), (0, 0.0, 0.1), tan2, tail, bevel=0.012)
    kit.box(f"{name}.tailtip", (0.05, 0.05, 0.07), (0, 0.0, 0.235), white, tail, bevel=0.012)
    tail.rotation_euler = (-0.35, 0, 0)
    # the head on a neck pivot
    head = kit.empty(f"{name}.headg", (0, -0.29 - PV[1], 0.46 - PV[2]), bg)
    kit.box(f"{name}.head", (0.2, 0.22, 0.2), (0, -0.09, 0.02), tan, head, bevel=0.05)
    kit.box(f"{name}.blaze", (0.05, 0.1, 0.205), (0, -0.14, 0.02), white, head, bevel=0.012)
    kit.box(f"{name}.snout", (0.12, 0.16, 0.1), (0, -0.25, -0.03), white, head, bevel=0.03)
    kit.box(f"{name}.nose", (0.07, 0.04, 0.05), (0, -0.335, -0.005), black, head, bevel=0.015)
    kit.box(f"{name}.mouth", (0.09, 0.012, 0.012), (0, -0.325, -0.06), black, head)
    tongue = kit.box(f"{name}.tongue", (0.05, 0.1, 0.015), (0, -0.3, -0.085), pink, head, bevel=0.005)
    tongue.hide_render = True
    ears = []
    for sx in (-1, 1):
        ep = kit.empty(f"{name}.earp{sx}", (sx * 0.105, -0.06, 0.1), head)
        kit.box(f"{name}.ear{sx}", (0.04, 0.12, 0.2), (sx * 0.012, 0.0, -0.09), brown, ep, bevel=0.012)
        ears.append(ep)
        eye = kit.sphere(f"{name}.eye{sx}", 0.021, (sx * 0.06, -0.2, 0.05), black, head, seg=10)
        eye.scale = (0.9, 0.6, 1.15)
        kit.sphere(f"{name}.glint{sx}", 0.007, (sx * 0.056, -0.213, 0.06), white, head, seg=6)
        kit.box(f"{name}.brow{sx}", (0.05, 0.01, 0.012), (sx * 0.06, -0.205, 0.088), brown, head, rot=(0, 0.25 * sx, 0))
    # legs: pivot empties with a short box and a white paw
    legs = []
    for nm, (lx, ly) in (("fl", (-0.07, -0.2)), ("fr", (0.07, -0.2)), ("hl", (-0.07, 0.2)), ("hr", (0.07, 0.2))):
        lp = kit.empty(f"{name}.{nm}", (lx - PV[0], ly - PV[1], 0.2 - PV[2]), bg)
        kit.box(f"{name}.{nm}b", (0.065, 0.065, 0.14), (0, 0, -0.07), tan, lp, bevel=0.015)
        kit.box(f"{name}.{nm}p", (0.07, 0.085, 0.07), (0, -0.008, -0.165), white, lp, bevel=0.015)
        legs.append(lp)
    # the haunch that sits on the ground when Noodle sits (grows from nothing)
    haunch = kit.box(f"{name}.haunch", (0.2, 0.24, 0.2), (0, 0.3, 0.1), tan, root, bevel=0.05)
    haunch.scale = (0.001, 0.001, 0.001)
    return {"root": root, "bodyg": bg, "head": head, "ears": ears, "legs": legs, "tail": tail, "tongue": tongue,
            "haunch": haunch, "PV": PV}


DOGKEYS = {"x": 0.0, "y": -80.0, "z": 0.0, "yaw": 0.0, "sit": 0.0, "lie": 0.0, "up": 0.0, "hy": 0.0, "hp": 0.0,
           "tongue": 0.0, "wag": 0.0, "lean": 0.0}


def dog_state(tl, t):
    """The dog's track: each key holds, or (glide 1) travels from the key before with a smooth ease; a key's dur eases
    the change in over that many seconds."""
    ks = [c for c in tl["cues"] if c["name"] == "dog"]
    if not ks:
        return dict(DOGKEYS)
    cur = None
    for i, c in enumerate(ks):
        if c["t"] <= t:
            cur = i
    if cur is None:
        return {k: ks[0].get(k, v) for k, v in DOGKEYS.items()}

    def full(c):
        return {k: c.get(k, v) for k, v in DOGKEYS.items()}
    s = full(ks[cur])
    if cur + 1 < len(ks) and ks[cur + 1].get("glide"):
        n = full(ks[cur + 1])
        u = ss((t - ks[cur]["t"]) / max(1e-6, ks[cur + 1]["t"] - ks[cur]["t"]))
        return {k: s[k] + (n[k] - s[k]) * u for k in s}
    dur = ks[cur].get("dur", 0.0)
    if cur > 0 and dur > 0 and t < ks[cur]["t"] + dur:
        p = full(ks[cur - 1])
        # the previous key may itself be a glide target: its value is what we leave from
        u = ss((t - ks[cur]["t"]) / dur)
        return {k: p[k] + (s[k] - p[k]) * u for k in s}
    return s


def pose_dog(d, st, t, sneeze_u, moving):
    root, bg = d["root"], d["bodyg"]
    root.location = (st["x"], st["y"], st["z"])
    root.rotation_euler = (st.get("lean", 0.0) * D2R, 0, st["yaw"] * D2R)
    sit, lie, up = st["sit"], st["lie"], st["up"]
    pitch = -0.78 * sit - 1.15 * up
    bg.rotation_euler = (pitch, 0, 0)
    bg.location = (d["PV"][0], d["PV"][1], d["PV"][2] - 0.12 * lie)
    hs = d["haunch"]
    hv = max(0.001, sit)
    hs.scale = (hv, hv, hv)
    hs.location = (0, 0.3, 0.1 * hv)
    # the head: yaw hy, pitch hp (+ lowers the nose), the sneeze dip, a lift when sitting
    dip = 0.0
    ear = 0.0
    if sneeze_u is not None:
        dip = 0.62 * math.sin(math.pi * sneeze_u) ** 1.2
        ear = 0.55 * math.sin(math.pi * 3 * sneeze_u) * (1 - sneeze_u)
    d["head"].rotation_euler = (st["hp"] * D2R + dip - pitch * 0.9, 0, st["hy"] * D2R)
    for k, ep in enumerate(d["ears"]):
        ep.rotation_euler = (0, (0.12 + ear) * (1 if k else -1) * (1 if k else 1), 0)
    d["tongue"].hide_render = st["tongue"] < 0.5
    d["tail"].rotation_euler = (-0.35 - 0.1 * sit, 0, 0.35 * math.sin(t * 9.0) * (st["wag"] if st["wag"] else 0.0))
    # legs
    fl, fr, hl, hr = d["legs"]
    swing = 0.0
    if moving > 0.05 and sit < 0.2 and lie < 0.2 and up < 0.2:
        swing = 0.75 * min(1.0, moving)
    ph = t * 15.0
    pivz = d["PV"][2]
    # front pivot height above the ground after the pitch (root coords: y -0.45 from the hips, z +0.05)
    zf = pivz + (-0.45) * math.sin(pitch) + 0.05 * math.cos(pitch)
    for i, lg in enumerate((fl, fr)):
        sw = swing * math.sin(ph + (math.pi if i else 0.0))
        counter = -pitch * (1 - up)
        fold = -1.45 * lie
        lg.rotation_euler = (sw + counter + fold - 0.7 * up, 0, 0)
        sc = 1.0 + (zf / 0.2 - 1.0) * sit * (1 - lie)
        lg.scale = (1, 1, max(0.3, sc * (1 - 0.3 * sit)) * (1 - 0.45 * lie))
    for i, lg in enumerate((hl, hr)):
        sw = swing * math.sin(ph + (0.0 if i else math.pi))
        lg.rotation_euler = (sw - 1.35 * sit - 1.1 * lie + 0.5 * up, 0, 0)
        lg.scale = (1, 1, 1 - 0.5 * max(sit, lie))


def sneeze_u(tl, t, dur=0.42):
    for c in tl["cues"]:
        if c["name"] == "achoo" and c["t"] <= t < c["t"] + dur:
            return (t - c["t"]) / dur
    return None


# ------------------------------------------------------------------------------------------------ the street
def build_street(kit):
    pl = kit.plastic
    x0, x1 = 54.0, 112.0
    cx = (x0 + x1) / 2
    ln = x1 - x0
    kit.box("st.sidewalk", (ln, 3.0, 0.1), (cx, 0.0, -0.05), kit.texture("concrete", 1.0, tint="#e4dccb"))
    kit.box("st.road", (ln, 7.0, 0.1), (cx, -5.1, -0.06), kit.texture("asphalt", 0.5, tint="#a8a8ac"))
    kit.box("st.kerb", (ln, 0.18, 0.09), (cx, -1.59, -0.04), pl("#d8d2c4", 0.8))
    for i in range(int(ln / 3.0)):
        kit.box(f"st.dash{i}", (1.4, 0.14, 0.012), (x0 + 1.5 + i * 3.0, -5.1, -0.0035), pl("#f2e2a8", 0.8))
    # a driveway to the van across the sidewalk's north side
    kit.box("st.drive", (3.4, 8.0, 0.04), (G.VAN_X, 5.4, -0.02), kit.texture("concrete", 1.0, tint="#f2ece0"))
    # Theo's yellow house (porch on its south face)
    hx, hy = G.HOUSE
    yellow = pl("#f2cf4a", 0.7, spec=0.05)
    trim = pl("#f4efe2", 0.6)
    kit.box("th.wall", (7.2, 6.0, 3.2), (hx, hy, 1.6), yellow, bevel=0.03)
    for sg in (-1, 1):
        kit.box(f"th.roof{sg}", (8.0, 3.7, 0.2), (hx, hy + sg * 1.55, 3.55), pl("#8a4a3a", 0.7), rot=(sg * 0.5, 0, 0))
    kit.box("th.gable", (7.0, 4.6, 0.8), (hx, hy, 3.5), yellow)
    py = G.PORCH_Y
    kit.box("th.deck", (4.4, 1.9, 0.3), (hx, py - 0.05, 0.15), kit.texture("wood", 1.0, tint="#d9a870"), bevel=0.01)
    kit.box("th.step1", (1.8, 0.4, 0.17), (hx, py - 1.2, 0.085), pl("#b8a688", 0.8))
    kit.box("th.step2", (1.8, 0.4, 0.26), (hx, py - 1.0, 0.13), pl("#a89878", 0.8))
    kit.box("th.path", (1.8, 3.5, 0.03), (hx, 3.2, 0.015), pl("#b8a688", 0.8))
    kit.box("th.door", (1.0, 0.08, 2.0), (hx, hy - 3.0 - 0.04, 1.3), pl("#3f7f5a", 0.55))
    kit.box("th.doorknob", (0.06, 0.06, 0.06), (hx + 0.34, hy - 3.1, 1.25), pl("#d8b24a", 0.3, spec=0.8))
    for sx in (-1, 1):
        kit.box(f"th.winf{sx}", (1.3, 0.06, 1.15), (hx + sx * 2.3, hy - 3.0 - 0.03, 1.7), trim)
        kit.box(f"th.win{sx}", (1.1, 0.07, 0.95), (hx + sx * 2.3, hy - 3.0 - 0.04, 1.7), pl("#8fc9e8", 0.2, spec=0.7))
    # porch roof on two posts, a ledge rail on the house wall with two plain mugs, side rails
    kit.box("th.proof", (4.6, 2.1, 0.12), (hx, py + 0.1, 2.75), pl("#8a4a3a", 0.7))
    for sx in (-1, 1):
        kit.box(f"th.post{sx}", (0.12, 0.12, 2.4), (hx + sx * 2.1, py - 0.85, 1.55), trim)
        kit.box(f"th.siderail{sx}", (0.06, 1.7, 0.06), (hx + sx * 2.1, py - 0.05, 1.2), trim)
        for k in range(5):
            kit.box(f"th.bal{sx}{k}", (0.04, 0.04, 0.82), (hx + sx * 2.1, py - 0.8 + k * 0.4, 0.76), trim)
    kit.box("th.ledge", (3.0, 0.14, 0.07), (hx, hy - 3.0 - 0.1, 1.1), trim)
    for i, c in enumerate(("#f4f4ee", "#e0a826")):
        kit.cyl(f"th.mug{i}", 0.075, 0.14, (hx - 0.17 + 0.34 * i, hy - 3.0 - 0.1, 1.205), pl(c, 0.45), n=14)
    # a small porch table between us, with the two plain mugs
    wd = pl("#8a5a3a", 0.6)
    kit.box("th.ptable", (0.62, 0.4, 0.05), (hx, py - 0.45, 0.8), wd, bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            kit.box(f"th.ptleg{sx}{sy}", (0.05, 0.05, 0.55), (hx + sx * 0.26, py - 0.45 + sy * 0.15, 0.5), wd)
    for i, c in enumerate(("#f4f4ee", "#e0a826")):
        kit.cyl(f"th.pmug{i}", 0.07, 0.13, (hx - 0.14 + 0.28 * i, py - 0.45, 0.905), pl(c, 0.45), n=14)
    # neighbouring houses and trees
    kit.prop("sub_building_type_a", (66.0, 10.5, 0), rot=0, tint="#f0e2d0")
    kit.prop("sub_building_type_c", (96.0, 10.5, 0), rot=0, tint="#dfe9ee")
    kit.prop("sub_building_type_f", (108.0, 12.0, 0), rot=0, tint="#f0dcd0")
    for i, (x, y, h) in enumerate(((70.0, 3.2, 4.2), (74.0, 2.4, 3.6), (81.5, 2.7, 4.0), (91.0, 3.0, 4.4), (101.0, 2.6, 3.8),
                                   (62.0, 3.0, 4.2))):
        kit.prop("sub_tree_large", (x, y, 0), height=h, tint="#d4f0c4")
    kit.prop("bush_1", (73.0, 6.0, 0), height=0.9, tint="#d4f0c4")
    kit.prop("bush_2", (83.0, 6.2, 0), height=0.8, tint="#d4f0c4")
    build_van(kit)


def build_van(kit):
    pl = kit.plastic
    vx = G.VAN_X
    white = pl("#e2e2da", 0.55, spec=0.1)
    inner = pl("#ece6d6", 0.8)
    y0, y1 = 0.7, 6.1
    kit.box("van.floor", (2.3, y1 - y0, 0.1), (vx, (y0 + y1) / 2, 0.62), pl("#c9bfa8", 0.7))
    for sx in (-1, 1):
        kit.box(f"van.wall{sx}", (0.1, 4.6, 1.95), (vx + sx * 1.15, y0 + 2.3, 1.62), white)
    kit.box("van.roof", (2.4, y1 - y0 - 0.9, 0.12), (vx, (y0 + y1 - 0.9) / 2, 2.66), white)
    kit.box("van.bulkhead", (2.2, 0.1, 1.95), (vx, y0 + 4.65, 1.62), inner)
    kit.box("van.cab", (2.3, 1.4, 1.55), (vx, y1 - 0.7, 1.4), white)
    kit.box("van.windscreen", (2.0, 0.06, 0.7), (vx, y1 + 0.01, 1.7), pl("#9ed4f0", 0.12, spec=0.9))
    kit.box("van.bumper", (2.4, 0.2, 0.2), (vx, y1 + 0.08, 0.5), pl("#9a9ea4", 0.4))
    kit.box("van.rearbumper", (2.4, 0.2, 0.2), (vx, y0 - 0.06, 0.5), pl("#9a9ea4", 0.4))
    kit.box("van.rolldoor", (2.3, 0.1, 0.25), (vx, y0, 2.62), pl("#cfcfc6", 0.6))   # the rolled-up door at the top edge
    for sx in (-1, 1):
        for yy in (2.0, 4.9):
            kit.cyl(f"van.wheel{sx}{yy}", 0.38, 0.26, (vx + sx * 1.1, yy, 0.38), pl("#2a2a2e", 0.8), rot=(0, math.pi / 2, 0), n=14)
    # a warm fill inside the box and some plain cardboard boxes
    kit.light("vanfill", "POINT", (vx, 2.2, 2.0), 1.0, "#ffe2b0", size=0.8, shadow=False)
    kit.LIGHTS["vanfill"]["obj"].visible_camera = False
    card = pl("#c9a06a", 0.7)
    card2 = pl("#b98e58", 0.7)
    for i, (dx, dy, sz) in enumerate(((-0.6, 1.4, (0.7, 0.6, 0.55)), (0.5, 1.6, (0.6, 0.6, 0.5)), (-0.5, 2.4, (0.6, 0.7, 0.6)),
                                      (0.6, 2.6, (0.7, 0.6, 0.45)), (0.0, 3.3, (0.9, 0.6, 0.7)))):
        kit.box(f"van.box{i}", sz, (vx + dx, y0 + dy, 0.67 + sz[2] / 2), card if i % 2 else card2, bevel=0.01)
    # the ramp: a plank from the van floor down to the sidewalk, and boxes on it
    ln = 2.6
    kit.box("van.ramp", (1.1, ln, 0.05), (vx, y0 - 1.25, 0.33), pl("#a8aeb6", 0.5, spec=0.5), rot=(0.24, 0, 0))
    for i, (dx, dy, sz) in enumerate(((-0.2, -0.3, (0.5, 0.45, 0.4)), (0.25, -0.9, (0.45, 0.4, 0.35)))):
        yy = y0 + dy - 0.2
        zz = 0.33 + (yy - (y0 - 1.25)) * 0.24 + 0.04
        kit.box(f"van.rbox{i}", sz, (vx + dx, yy, zz + sz[2] / 2), card2 if i else card, rot=(0.24, 0, 0), bevel=0.01)


# ------------------------------------------------------------------------------------------------ the montage spots
def build_neighbor(kit):
    pl = kit.plastic
    nx, ny = G.NEIGH
    kit.box("nb.walk", (9.0, 3.0, 0.1), (nx, ny - 0.5, -0.05), kit.texture("concrete", 1.0, tint="#e4dccb"))
    kit.box("nb.wall", (9.0, 0.3, 3.4), (nx, ny + 3.7, 1.7), pl("#f0c9a8", 0.8, spec=0.05))
    kit.box("nb.door", (1.1, 0.08, 2.2), (nx, ny + 3.51, 1.2), pl("#c8503a", 0.55))
    kit.box("nb.doorknob", (0.07, 0.07, 0.07), (nx + 0.38, ny + 3.45, 1.15), pl("#d8b24a", 0.3, spec=0.8))
    kit.box("nb.stoop", (1.9, 0.9, 0.18), (nx, ny + 2.95, 0.09), pl("#d8d0c0", 0.8))
    kit.box("nb.roofover", (9.2, 1.0, 0.14), (nx, ny + 3.3, 2.9), pl("#8a6a5a", 0.7))
    for sx in (-1, 1):
        kit.box(f"nb.winf{sx}", (1.5, 0.06, 1.3), (nx + sx * 2.8, ny + 3.53, 1.7), pl("#f4efe2", 0.6))
        kit.box(f"nb.win{sx}", (1.3, 0.07, 1.1), (nx + sx * 2.8, ny + 3.5, 1.7), pl("#8fc9e8", 0.2, spec=0.7))
        kit.prop("nat_pot_large", (nx + sx * 1.5, ny + 3.0, 0), height=0.45, tint="#e8d8c0")
        kit.prop("houseplant_1", (nx + sx * 1.5, ny + 3.0, 0.45), height=0.55)
    kit.prop("bush_1", (nx - 4.2, ny + 2.2, 0), height=1.0, tint="#d4f0c4")


def build_sam(kit):
    pl = kit.plastic
    sx0, sy0 = G.SAM
    kit.box("sm.drive", (9.0, 9.0, 0.1), (sx0, sy0 + 2.0, -0.05), kit.texture("concrete", 1.0, tint="#e9e3d6"))
    kit.box("sm.wall", (9.0, 0.3, 3.2), (sx0, sy0 + 6.7, 1.6), pl("#dfe9ee", 0.8, spec=0.05))
    kit.box("sm.garage", (3.4, 0.08, 2.3), (sx0 + 0.5, sy0 + 6.5, 1.15), pl("#f4f0e4", 0.6))
    for k in range(4):
        kit.box(f"sm.gpanel{k}", (3.3, 0.04, 0.02), (sx0 + 0.5, sy0 + 6.45, 0.4 + k * 0.55), pl("#cfc9b6", 0.7))
    kit.box("sm.eave", (9.2, 1.0, 0.14), (sx0, sy0 + 6.3, 2.95), pl("#8a6a5a", 0.7))
    # the red hatchback along y, its hood (to the south) lifted on a hinge; steam puffs above it
    cx, cy = sx0 + 1.9, sy0 + 2.6
    red = pl("#d93a2f", 0.35, spec=0.5)
    dark = pl("#2a2a2e", 0.7)
    gl = pl("#9ed4f0", 0.12, spec=0.9)
    car = kit.empty("car", (cx, cy, 0))
    kit.box("car.body", (1.7, 3.6, 0.55), (0, 0, 0.55), red, car, bevel=0.06)
    kit.box("car.cabin", (1.55, 1.9, 0.5), (0, 0.75, 1.07), red, car, bevel=0.07)
    kit.box("car.wind", (1.4, 0.05, 0.4), (0, -0.2, 1.07), gl, car, rot=(0.5, 0, 0))
    kit.box("car.rearwin", (1.4, 0.05, 0.38), (0, 1.7, 1.07), gl, car, rot=(-0.4, 0, 0))
    for sx in (-1, 1):
        kit.box(f"car.sidewin{sx}", (0.04, 1.6, 0.36), (sx * 0.79, 0.75, 1.1), gl, car)
        for yy in (-1.15, 1.15):
            kit.cyl(f"car.wheel{sx}{yy}", 0.3, 0.2, (sx * 0.82, yy, 0.3), dark, car, rot=(0, math.pi / 2, 0), n=14)
            kit.cyl(f"car.hub{sx}{yy}", 0.14, 0.22, (sx * 0.82, yy, 0.3), pl("#cfd2d6", 0.3, spec=0.8), car, rot=(0, math.pi / 2, 0), n=10)
        kit.box(f"car.light{sx}", (0.3, 0.05, 0.14), (sx * 0.55, -1.8, 0.62), pl("#fff3c8", 0.3), car)
    kit.box("car.bumper", (1.8, 0.1, 0.16), (0, -1.82, 0.4), pl("#cfd2d6", 0.3, spec=0.8), car)
    # the engine bay under the hood (dark), and the hood on its hinge at the windscreen base (y -0.55)
    kit.box("car.bay", (1.5, 1.2, 0.2), (0, -1.15, 0.78), dark, car)
    hood = kit.empty("car.hoodpiv", (0, -0.55, 0.85), car)
    kit.box("car.hood", (1.68, 1.25, 0.06), (0, -0.62, 0.0), red, hood, bevel=0.03)
    hood.rotation_euler = (-1.05, 0, 0)
    W["hood"] = hood
    W["steam"] = [kit.sphere(f"steam{k}", 0.16, (cx, cy - 1.5, 1.5), pl("#f2f2f4", 0.9), seg=10) for k in range(4)]
    for s in W["steam"]:
        s.hide_render = True
        noshadow(s)


# ------------------------------------------------------------------------------------------------ the rule meter
DIGIT_SEGS = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd", 6: "afgedc", 7: "abc",
              8: "abcdefg", 9: "abcdfg"}


def build_tag(kit):
    cam = kit.OBJ["cam"]
    root = kit.empty("tag", (0, 0, 0), cam)
    W["tag"] = root
    edge = kit.emit("#2b2118", 0.6, "tagedge")
    plate = kit.emit("#f2e6c8", 0.85, "tagplate")
    ink = kit.emit("#2b2118", 0.6, "tagink")
    teal = kit.emit("#14867a", 0.9, "tagteal")

    def b(name, size, loc, mat, parent=None):
        ob = kit.box(name, size, loc, mat, parent or root)
        noshadow(ob)
        return ob

    b("tag.edge", (1.5, 0.7, 0.006), (0, 0, 0), edge)
    b("tag.plate", (1.44, 0.64, 0.006), (0, 0, 0.007), plate)
    z = 0.016
    cream = kit.emit("#f2e6c8", 0.85, "tagcream")
    g = kit.empty("tag.glyph", (-0.5, 0.0, z), root)
    b("tag.g.body", (0.3, 0.46, 0.006), (0, 0, 0), teal, g)
    gr = kit.cyl("tag.g.grille", 0.075, 0.006, (0, 0.12, 0.007), cream, g, n=14)
    noshadow(gr)
    for r in range(3):
        for c in range(2):
            b(f"tag.g.k{r}{c}", (0.075, 0.05, 0.006), ((c - 0.5) * 0.11, -0.03 - r * 0.075, 0.007), cream, g)

    def seven(prefix, cx, cy, dw, dh, t, zz=z):
        pos = {"a": (0, dh / 2 - t / 2, dw, t), "g": (0, 0, dw, t), "d": (0, -dh / 2 + t / 2, dw, t),
               "f": (-dw / 2 + t / 2, dh / 4, t, dh / 2), "b": (dw / 2 - t / 2, dh / 4, t, dh / 2),
               "e": (-dw / 2 + t / 2, -dh / 4, t, dh / 2), "c": (dw / 2 - t / 2, -dh / 4, t, dh / 2)}
        return {k: b(f"{prefix}{k}", (sw, sh, 0.006), (cx + px, cy + py, zz), ink) for k, (px, py, sw, sh) in pos.items()}

    W["one"] = seven("tag.one", 0.3, 0.0, 0.2, 0.46, 0.07)
    W["digits"] = [seven(f"tag.d{i}", cx, 0.0, 0.1, 0.34, 0.036) for i, cx in enumerate((-0.12, 0.04, 0.3, 0.46))]
    W["colon"] = [b("tag.c1", (0.036, 0.036, 0.006), (0.17, 0.07, z), ink), b("tag.c2", (0.036, 0.036, 0.006), (0.17, -0.07, z), ink)]
    # the clock readout under the plate: H:MM in small digits on its own small plate
    clk = kit.empty("tag.clock", (0, -0.55, 0), root)
    W["clockroot"] = clk
    b("tag.cl.edge", (0.9, 0.4, 0.006), (0.25, 0, 0), edge, clk)
    b("tag.cl.plate", (0.84, 0.34, 0.006), (0.25, 0, 0.007), plate, clk)
    cs = [seven(f"tag.cl{i}", cx, 0.0, 0.09, 0.22, 0.03, z) for i, cx in enumerate((0.0, 0.26, 0.44))]
    for dd in cs:
        for ob in dd.values():
            ob.parent = clk
    W["clockdigits"] = cs
    W["clockcolon"] = [b("tag.cl.c1", (0.03, 0.03, 0.006), (0.13, 0.05, z), ink, clk), b("tag.cl.c2", (0.03, 0.03, 0.006), (0.13, -0.05, z), ink, clk)]


def _digit(d, n):
    segs = DIGIT_SEGS.get(n, "")
    for k, ob in d.items():
        ob.hide_render = k not in segs


# ------------------------------------------------------------------------------------------------ the leash
def build_leash(kit):
    red = kit.plastic("#c0303a", 0.6)
    W["leash"] = kit.box("leash.line", (1.0, 0.012, 0.012), (0, -80, 0.9), red)
    W["loop"] = [kit.box(f"leash.loop{k}", (0.15 if k < 2 else 0.012, 0.012 if k < 2 else 0.11, 0.012),
                         (0, -80, 0.9), red) for k in range(4)]


# ------------------------------------------------------------------------------------------------ build / animate
def build(kit, story, tl):
    tl["cues"].sort(key=lambda c: c["t"])
    sun = kit.light("sun", "SUN", (-25, -30, 17), 1.0, "#ffd08a", size=0.06)
    sun.data.angle = 0.05
    kit.aim(sun, (0, 0, 0))
    fill = kit.light("fill", "SUN", (0, -10, 30), 1.0, "#fff0dc", shadow=False)
    fill.data.angle = 0.5
    kit.aim(fill, (0, 0, 0))
    kit.light("key", "POINT", (0, 0, 2), 1.0, "#fff4e0", size=0.8, shadow=False)
    kit.light("rimL", "POINT", (0, 0, 3), 1.0, "#ffe9c4", size=0.6, shadow=False)
    for nm in ("sun", "fill", "key", "rimL"):
        kit.LIGHTS[nm]["obj"].visible_camera = False
    build_patio(kit)
    build_phone(kit)
    W["dog"] = build_dog(kit, "dog")
    build_street(kit)
    build_neighbor(kit)
    build_sam(kit)
    build_leash(kit)
    build_tag(kit)
    return {}


def _first_frame(kit, story):
    get = bpy.data.objects.get
    th = get("theo.headg")
    if th is not None:
        dk = kit.plastic("#2a1b12", 0.8)
        kit.box("theo.beard", (0.5, 0.12, 0.2), (0, -0.56, -0.47), dk, th, bevel=0.05)
        kit.box("theo.beardL", (0.07, 0.3, 0.3), (-0.265, -0.4, -0.2), dk, th, bevel=0.025)
        kit.box("theo.beardR", (0.07, 0.3, 0.3), (0.265, -0.4, -0.2), dk, th, bevel=0.025)
    pt = get("photo_theo.headg")
    if pt is not None:
        dk = kit.plastic("#2a1b12", 0.8)
        kit.box("ptheo.beard", (0.5, 0.12, 0.2), (0, -0.56, -0.47), dk, pt, bevel=0.05)
        kit.box("ptheo.beardL", (0.07, 0.3, 0.3), (-0.265, -0.4, -0.2), dk, pt, bevel=0.025)
        kit.box("ptheo.beardR", (0.07, 0.3, 0.3), (0.265, -0.4, -0.2), dk, pt, bevel=0.025)
    nb = get("neighbor.headg")
    if nb is not None:
        hc = kit.plastic("#3a2418", 0.7)
        kit.box("neighbor.bang", (0.55, 0.06, 0.2), (-0.1, -0.6, 0.3), hc, nb, rot=(0, 0.35, 0), bevel=0.02)
        kit.box("neighbor.bang2", (0.22, 0.06, 0.3), (0.2, -0.61, 0.2), hc, nb, rot=(0, -0.5, 0), bevel=0.02)
        gold = kit.plastic("#f0c040", 0.3, spec=0.8)
        for sx in (-1, 1):
            kit.sphere(f"neighbor.ear{sx}", 0.09, (sx * 0.56, -0.1, -0.4), gold, nb, seg=10)
            kit.box(f"neighbor.bobside{sx}", (0.14, 0.6, 0.9), (sx * 0.52, 0.0, -0.1), hc, nb, bevel=0.05)
    W["inited"] = True


MORNING = {"S27d"}
EVE_SKY = ("#ffe0b0", 1.0)
MORN_SKY = ("#c4e6ff", 1.0)


def is_morning(sid):
    try:
        n = int("".join(ch for ch in sid[1:4] if ch.isdigit()))
    except ValueError:
        return False
    return sid in MORNING or n >= 28


def hexcol(h):
    h = h.lstrip("#")
    return tuple((int(h[i:i + 2], 16) / 255.0) ** 2.2 for i in (0, 2, 4))


def animate(kit, story, tl, t, ctx):
    if not W.get("inited"):
        _first_frame(kit, story)
    pto = bpy.data.objects.get("photo_theo")
    if pto is not None:
        W.setdefault("pto0", tuple(pto.scale))
        o = W["pto0"]
        pto.scale = (o[0], o[1] * 0.22, o[2])       # a printed picture: no depth
    ppd = W.get("pdog")
    if ppd is not None:
        ppd["root"].scale = (0.52, 0.16, 0.52)
    shot = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    sid = shot["id"]
    spec = next((s for s in story["shots"] if s["id"] == sid), None)
    morning = is_morning(sid)
    gains = {}
    sun = kit.LIGHTS["sun"]
    if morning:
        sun["obj"].location = Vector((28, -30, 22))
        sun["light"].color = (1.0, 0.93, 0.78)
        gains["sun"], gains["fill"] = 4.0, 1.5
        skyc, skys = MORN_SKY
    else:
        sun["obj"].location = Vector((-25, -30, 17))
        sun["light"].color = (1.0, 0.82, 0.54)
        gains["sun"], gains["fill"] = 4.4, 1.3
        skyc, skys = EVE_SKY
    kit.aim(sun["obj"], (0, 0, 0))
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*hexcol(skyc), 1.0)
    bg.inputs["Strength"].default_value = skys
    # the follow lights: a key just left of the camera (faces always lit), a soft rim behind the subject
    if spec:
        c0 = spec["cam"][0]
        loc, tgt = Vector(c0[1]), Vector(c0[2])
        dist = max(1.0, (loc - tgt).length)
        base = 55.0 * dist * dist
        right = Vector((tgt.y - loc.y, -(tgt.x - loc.x), 0))
        right = right.normalized() if right.length > 1e-4 else Vector((1, 0, 0))
        kl = kit.LIGHTS["key"]["obj"]
        kl.location = loc + Vector((0, 0, 0.4)) - right * 0.5
        rl = kit.LIGHTS["rimL"]["obj"]
        rl.location = tgt + (tgt - loc).normalized() * 1.5 + Vector((0, 0, 0.9))
        gains["key"], gains["rimL"] = base, base * 0.25
    else:
        gains["key"], gains["rimL"] = 0.0, 0.0
    gains["vanfill"] = 260.0
    # ---- the tag
    tm = sample("timer", tl, t, {"mode": 0.0, "s": 0.0, "big": 1.0})
    call = tm["mode"] > 0.5
    secs = int(round(tm["s"]))
    mm, ss_ = secs // 60, secs % 60
    big = int(round(tm["big"]))
    for k, ob in W["one"].items():
        ob.hide_render = call or k not in DIGIT_SEGS[big]
    for d, n in zip(W["digits"], (mm // 10, mm % 10, ss_ // 10, ss_ % 10)):
        for k, ob in d.items():
            ob.hide_render = (not call) or k not in DIGIT_SEGS[n]
    for ob in W["colon"]:
        ob.hide_render = not call
    ck = sample("clock", tl, t, {"on": 0.0, "h": 7.0, "m": 38.0})
    on = ck["on"] > 0.5
    hh, cm = int(round(ck["h"])), int(round(ck["m"]))
    for ob in [W["clockroot"]] + list(W["clockroot"].children_recursive):
        ob.hide_render = not on
    for d, n in zip(W["clockdigits"], (hh % 10, cm // 10, cm % 10)):
        for k, ob in d.items():
            ob.hide_render = (not on) or k not in DIGIT_SEGS[n]
    # ---- the phone
    ph = sample("phone", tl, t, {"mode": 0.0, "buzz": 0.0})
    W["home"].hide_render = ph["mode"] > 0.5
    for ob in W["home"].children:
        ob.hide_render = ph["mode"] > 0.5
    W["call"].hide_render = ph["mode"] <= 0.5
    for ob in W["call"].children:
        ob.hide_render = ph["mode"] <= 0.5
    bz = ph["buzz"]
    px, py, pz = G.PHONE
    W["phone"].location = (px + 0.0012 * bz * math.sin(t * 38.0), py + 0.001 * bz * math.sin(t * 31.0), pz)
    tp = sample("tap", tl, t, {"p": 0.0})["p"]
    fg = W["finger"]
    if tp < 0.02:
        fg.location = (0, -80, 0)
    else:
        u = ss(tp)
        fg.location = (px + 0.0 + 0.16 * (1 - u), py + 0.04 + 0.16 * (1 - u), pz + 0.02 + 0.08 * (1 - u))
        fg.rotation_euler = (-0.25 * (1 - u), 0, math.pi + 0.3)
    # ---- the gate and its latch
    gt = sample("gate", tl, t, {"open": 0.0, "latch": 0.0})
    W["hinge"].rotation_euler = (0, 0, 1.45 * ss(gt["open"]))
    W["latch"].rotation_euler = (0.75 * ss(gt["latch"]), 0, 0)
    # ---- Noodle (and the sneeze)
    d = W["dog"]
    st = dog_state(tl, t)
    st2 = dog_state(tl, t + 0.06)
    st1 = dog_state(tl, t - 0.06)
    speed = math.hypot(st2["x"] - st1["x"], st2["y"] - st1["y"]) / 0.12
    pose_dog(d, st, t, sneeze_u(tl, t), speed / 1.2)
    # ---- seated / squatting
    sm = sample("sit_me", tl, t, {"s": 0.0})["s"]
    for sx in (-1, 1):
        leg = bpy.data.objects.get(f"me.leg{sx}")
        if leg:
            leg.rotation_euler = (leg.rotation_euler.x * (1 - sm) + SIT * sm, 0, 0)
    sq = sample("squat_theo", tl, t, {"s": 0.0})["s"]
    for sx in (-1, 1):
        leg = bpy.data.objects.get(f"theo.leg{sx}")
        if leg:
            leg.rotation_euler = (leg.rotation_euler.x * (1 - sq) - 1.0 * sq, 0, 0)
    # ---- the leash, from my hand to Noodle's collar
    ls = sample("leash", tl, t, {"on": 0.0, "arm": 75.0})
    me = bpy.data.objects.get("me")
    lash, loop = W["leash"], W["loop"]
    if ls["on"] > 0.5 and me is not None and not me.hide_render:
        yaw = me.rotation_euler.z
        fwd = Vector((math.sin(yaw), -math.cos(yaw), 0))
        rgt = Vector((math.cos(yaw), math.sin(yaw), 0))
        a = ls["arm"] * D2R
        hand = Vector(me.location) + rgt * 0.34 + fwd * 0.68 * math.sin(a) + Vector((0, 0, 1.275 - 0.68 * math.cos(a)))
        dyaw = st["yaw"] * D2R
        dfwd = Vector((math.sin(dyaw), -math.cos(dyaw), 0))
        end = Vector((st["x"], st["y"], st["z"])) + dfwd * 0.28 + Vector((0, 0, 0.5))
        dv = end - hand
        lash.location = (hand + end) / 2
        lash.scale = (max(0.05, dv.length), 1, 1)
        lash.rotation_euler = (0, -math.atan2(dv.z, math.hypot(dv.x, dv.y)), math.atan2(dv.y, dv.x))
        for k, ob in enumerate(loop):
            off = [(0, 0.055), (0, -0.055), (0.075, 0), (-0.075, 0)][k]
            ob.location = hand + Vector((off[0] * math.cos(yaw), off[0] * math.sin(yaw), 0)) * 1.0 + Vector((0, 0, 0.02))
            ob.rotation_euler = (0, 0, yaw)
    else:
        lash.location = (0, -80, 0.9)
        for ob in loop:
            ob.location = (0, -80, 0.9)
    # ---- the hatchback's hood and its steam
    if "hood" in W:
        stm = sample("steam", tl, t, {"on": 0.0})["on"]
        cx, cy = G.SAM[0] + 1.9, G.SAM[1] + 2.6
        for k, ob in enumerate(W["steam"]):
            ob.hide_render = stm < 0.5
            u = ((t * 0.18) + k * 0.25) % 1.0
            ob.location = (cx + 0.1 * math.sin(k * 2.0 + t), cy - 1.35 + 0.15 * math.sin(t * 0.7 + k), 1.2 + 0.9 * u)
            sc = 0.5 + 1.4 * u * (1 - 0.6 * u)
            ob.scale = (sc, sc, sc)
    return gains
