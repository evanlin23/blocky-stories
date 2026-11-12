"""ep140-town-photo: a bright town square on photo day, a long hallway of framed photos, and a beach kite stall.

One sunny plastic set (the "closer" look). World (metres, z up, characters at yaw 0 face -y, toward the shot cameras):
- THE BLEACHERS: five white tiers (0.9 m deep, 0.45 m rise) centred on x = 0, the front row at y = 3.0. A seat is
  (row r, k): x = 0.72 k (+0.36 on odd rows), y = 3.0 + 0.9 r, feet z = 0.45 (r + 1) + 0.06 - 0.68 (the legs hang inside
  the solid tier, so a sitter shows from the hips up). Row 2 k = 0 is mine, k = -1 Mom's, row 0 k = -1 Grandma's, row 0
  k = 0 is Mr. Okafor's, empty until he sits. The rest of the crowd is built here from blocks (faces drawn as dots).
- THE TOWN HALL: a red-brick wall behind the stands (y = 10), windows, a door, cream trim. Bunting in yellow, teal and
  coral, no lettering. A ring of trees and houses round the square.
- THE HEADCOUNT BOARD: a green chalkboard on an easel at x = -4.6, y = 1.0 (face y = 0.945). States: a (212 over 211),
  a900 / a859 (with a chalk clock), smudge, b859 (212 over 212). Cue "board" (g). A print ledge on it.
- THE CAMERA: a big wooden box camera on a brass tripod at (0.1, -5.0), lens toward +y, the photographer behind it.
  Cue "bulb" (pos): the rubber shutter bulb held out. A one-stroke tally on a tripod collar.
- THE PRINTS: square instant prints (PIL, prints.py). Cues "pr_proof", "pr_last", "pr_test", "pr_final": on, pos,
  rot (yaw, pitch), s, and optional to / dur to move it.
- THE HALLWAY at x = 70: ceiling, windows, a wall of framed old photos. THE KITE STALL at x = -60 (Uncle Benny).
- THE RULE TAG (camera child "tag"), set by the cue "tag" (g a or b), placed by the engine (story.json hud).
- THE VIEWFINDER FRAME (camera child "vf"), shown by the cue "vf".
- The cheering crowd: cue "cheer" (on).
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prints  # noqa: E402

HALLX = 70.0
BEACHX = -60.0
BOARDX, BOARDY = -4.6, 1.0
_n = [0]


def nm(p):
    _n[0] += 1
    return f"{p}.{_n[0]}"


def ss(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


class K:
    kit = None


def P(hexc, rough=0.5, spec=0.35):
    return K.kit.plastic(hexc, rough, spec=spec)


def B(parent, size, loc, mat, name="b", bevel=0.01, rot=(0, 0, 0)):
    return K.kit.box(nm(name), size, loc, mat, parent, rot, bevel)


def E(parent=None, loc=(0, 0, 0), name="e", rot=(0, 0, 0)):
    return K.kit.empty(nm(name), loc, parent, rot)


def hide(ob, h=True):
    ob.hide_render = h
    for c in ob.children_recursive:
        c.hide_render = h


def cue_at(tl, name, t):
    out = {}
    for c in tl.get("cues", []):
        if c["name"] == name and c["t"] <= t + 1e-9:
            out = c
    return out


def noshadow(ob):
    try:
        ob.visible_shadow = False
    except Exception:
        pass


# --------------------------------------------------------------------------------------------------- images
def img_mat(kit, name, pil, rough=0.6, emit=0.0):
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
    if emit:
        nt.links.new(tx.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    kit._fogged(m, b.outputs[0])
    return m


def img_plane(kit, name, w, h, loc, mat, parent=None, facing="-y"):
    """A picture quad. facing -y: stands in the x-z plane with the picture toward -y (the shot cameras). facing +z: in the
    x-y plane toward +z (the camera's tag, facing back toward the lens)."""
    x, y = w / 2, h / 2
    if facing == "-y":
        verts = [(-x, 0, -y), (x, 0, -y), (x, 0, y), (-x, 0, y)]
    else:
        verts = [(-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0)]
    ob = kit.mesh_obj(name, verts, [(0, 1, 2, 3)], mat, parent, loc)
    uv = ob.data.uv_layers.new(name="UVMap")
    uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for p in ob.data.polygons:
        for li in p.loop_indices:
            uv.data[li].uv = uvs[ob.data.loops[li].vertex_index]
    return ob


# --------------------------------------------------------------------------------------------------- the stands
def seat_pos(r, k):
    x = 0.8 * k + (0.4 if r % 2 else 0.0)
    return x, 3.0 + 0.9 * r, 0.45 * (r + 1) + 0.06 - 0.68


RESERVED = {(2, 0), (2, -1), (0, -1), (0, 0)}
SKIN = ["#f1c9a0", "#e8b891", "#c98f62", "#a8714a", "#f6d5b5", "#8a5a3a"]
HAIR = ["#2a1c14", "#5a3a22", "#c9a46a", "#8a8a8a", "#7a2a1a", "#171717", "#e8d9a8"]
SHIRT = ["#ff6f61", "#ffd23f", "#2bb3a3", "#4a7fd0", "#f4f4f0", "#9a63c8", "#e2884a", "#6dbf5a", "#d94f7a", "#3f4a66"]


def build_stands(kit):
    seat = P("#f4f0e2", 0.55, 0.25)
    riser = P("#d9d4c2", 0.6, 0.2)
    for r in range(5):
        top = 0.45 * (r + 1)
        y0 = 3.0 + 0.9 * r - 0.45
        y1 = 3.0 + 4 * 0.9 + 0.7
        B(None, (8.4, y1 - y0, top), (0, (y0 + y1) / 2, top / 2), riser, "tier", 0.0)
        B(None, (8.4, 0.9, 0.05), (0, 3.0 + 0.9 * r, top + 0.012), seat, "bench", 0.01)
        B(None, (8.4, 0.03, 0.4), (0, y0 - 0.01, top - 0.2), P("#a9c7d8", 0.6, 0.2), "riserband", 0.0)
    # side rails
    for sx in (-4.2, 4.2):
        B(None, (0.08, 4.4, 1.0), (sx, 5.9, 1.6), P("#e0ddd0", 0.6, 0.2), "rail", 0.01)


def crowd_person(kit, i, x, y, z, rng):
    root = E(None, (x, y, z), "crowd")
    skin, hair, shirt = rng.choice(SKIN), rng.choice(HAIR), rng.choice(SHIRT)
    sm, hm, tm = P(skin, 0.6, 0.2), P(hair, 0.65, 0.15), P(shirt, 0.6, 0.2)
    dk = P("#1c141c", 0.6, 0.1)
    B(root, (0.5, 0.3, 0.68), (0, 0, 1.02), tm, "tors", 0.05)
    arms = []
    for sx in (-1, 1):
        piv = E(root, (sx * 0.32, 0, 1.3), "armp")
        B(piv, (0.15, 0.2, 0.58), (0, 0, -0.29), tm, "arm", 0.03)
        B(piv, (0.14, 0.16, 0.14), (0, 0, -0.65), sm, "hand", 0.03)
        arms.append(piv)
    head = E(root, (0, 0, 1.57), "head")
    B(head, (0.42, 0.40, 0.42), (0, 0, 0), sm, "face", 0.1)
    B(head, (0.45, 0.43, 0.17), (0, 0.01, 0.2), hm, "hair", 0.07)
    if rng.random() < 0.45:
        B(head, (0.44, 0.14, 0.36), (0, 0.19, -0.03), hm, "hairback", 0.05)
    for sx in (-0.09, 0.09):
        B(head, (0.05, 0.02, 0.075), (sx, -0.205, 0.03), dk, "eye", 0.0)
    B(head, (0.1, 0.02, 0.035), (0, -0.205, -0.1), P("#8a2f2f", 0.6, 0.1), "mouth", 0.0)
    return {"arms": arms, "ph": rng.random() * 6.28, "root": root, "row": 0, "x": x}


def build_crowd(kit):
    rng = random.Random(140)
    out = []
    for r in range(5):
        for k in range(-5, 6):
            x, y, z = seat_pos(r, k)
            if abs(x) > 3.7 or (r, k) in RESERVED:
                continue
            cp = crowd_person(kit, len(out), x, y, z, rng)
            cp["row"] = r
            out.append(cp)
    return out


# --------------------------------------------------------------------------------------------------- the town
def build_town(kit):
    grass = kit.texture("grass", 0.6, tint="#a9e08a")
    B(None, (500, 400, 0.4), (0, 40, -0.2), grass, "lawn", 0.0)
    B(None, (9.5, 5.4, 0.04), (0, -1.6, 0.0), P("#d9d3c4", 0.9, 0.05), "pave", 0.0)
    # the town hall
    brick = kit.texture("brick", 1.0, tint="#e6a08a")
    cream = P("#f6ecd0", 0.55, 0.25)
    B(None, (30, 1.2, 10.5), (0, 10.6, 5.25), brick, "hall", 0.0)
    B(None, (30.6, 1.6, 0.5), (0, 10.5, 10.6), cream, "cornice", 0.02)
    B(None, (30.4, 1.3, 0.3), (0, 10.35, 0.45), cream, "plinth", 0.02)
    glass = P("#bfe3ff", 0.15, 0.7)
    for row_z in (4.0, 7.6):
        for i in range(-5, 6):
            x = i * 2.6
            if row_z < 5 and abs(x) < 2.0:
                continue
            B(None, (1.3, 0.05, 1.9), (x, 9.96, row_z), cream, "winframe", 0.01)
            B(None, (1.1, 0.04, 1.7), (x, 9.93, row_z), glass, "win", 0.01)
            B(None, (0.05, 0.05, 1.7), (x, 9.9, row_z), cream, "winbar", 0.005)
    B(None, (2.4, 0.2, 3.2), (0, 9.9, 1.6), P("#7d4a2c", 0.6, 0.2), "hdoor", 0.02)
    B(None, (3.2, 0.3, 0.3), (0, 9.8, 3.35), cream, "hlintel", 0.02)
    B(None, (4.6, 2.0, 0.25), (0, 8.8, 0.12), cream, "hstep", 0.02)
    # bunting between two poles and the hall
    pole = P("#b9b3a2", 0.5, 0.3)
    cols = [P("#ffd23f", 0.5, 0.2), P("#2bb3a3", 0.5, 0.2), P("#ff6f61", 0.5, 0.2)]
    for px_ in (-5.6, 5.6):
        kit.cyl(nm("pole"), 0.06, 5.6, (px_, 0.4, 2.8), pole, None, n=12)
    for (y_a, z_a) in ((0.4, 5.3), (7.5, 9.0)):
        n = 22
        for j in range(n):
            u = j / (n - 1)
            x = lerp(-5.6, 5.6, u)
            sag = 0.55 * 4 * u * (1 - u)
            z = z_a - sag
            B(None, (0.34, 0.03, 0.34), (x, y_a, z - 0.17), cols[j % 3], "flag", 0.0, rot=(0, math.radians(45), 0))
        B(None, (11.2, 0.03, 0.03), (0, y_a, z_a - 0.08), pole, "string", 0.0)
    # a ring of houses and trees round the square
    rng = random.Random(3)
    for i, nme in enumerate(["bldg_2story", "bldg_1story_gableroof", "bldg_2story_balcony", "bldg_3story_small",
                             "bldg_1story", "bldg_2story_slim", "bldg_2story", "bldg_1story_gableroof"]):
        x = -34 + i * 9.5
        try:
            kit.prop(nme, (x, -34, 0), rot=180 + (i % 3) * 8, height=6 + (i % 3), tint="#ffe9d0")
        except Exception:
            pass
    for i in range(18):
        try:
            kit.prop("commontree_1" if i % 2 else "commontree_2", (-30 + i * 3.7 + rng.random() * 2, -22 - rng.random() * 8, 0),
                     rot=40 * i, height=6 + (i % 4), tint="#8fe07a")
            kit.prop("commontree_2" if i % 2 else "commontree_1", (-24 + i * 3.1, 24 + rng.random() * 8, 0),
                     rot=30 * i, height=6 + (i % 3), tint="#8fe07a")
        except Exception:
            pass
    for i in range(10):
        try:
            kit.prop("bush_1" if i % 2 else "bush_2", (-12 + i * 2.6, -9.5, 0), rot=50 * i, height=0.9, tint="#7ad068")
        except Exception:
            pass


def build_board(kit):
    """The headcount board: a wooden frame, the chalk face (swapped by cue), an easel and a print ledge."""
    wood, dark = P("#a9763c", 0.7, 0.1), P("#7d5429", 0.7, 0.1)
    root = E(None, (BOARDX, BOARDY, 0), "board")
    bw, bh, zc = 1.5, 1.1, 1.45
    B(root, (bw + 0.16, 0.08, bh + 0.16), (0, 0, zc), wood, "bframe", 0.02)
    B(root, (bw, 0.06, bh), (0, -0.01, zc), P("#2f5d4a", 0.9, 0.05), "bpanel", 0.01)
    for sx in (-0.55, 0.55):
        B(root, (0.09, 0.09, 1.9), (sx, 0.32, 0.95), dark, "eleg", 0.01, rot=(math.radians(10), 0, 0))
    B(root, (0.09, 0.09, 1.7), (0, 0.4, 0.85), dark, "efront", 0.01, rot=(math.radians(8), 0, 0))
    B(root, (1.65, 0.2, 0.05), (0, -0.1, 0.9), wood, "ledge", 0.012)
    chalks = {}
    for st in ("a", "a900", "a859", "smudge", "b859"):
        m = img_mat(kit, f"chalk {st}", prints.chalk(st), 0.9, emit=0.08)
        ob = img_plane(kit, nm("chalk"), bw - 0.06, (bw - 0.06) * 700 / 960, (0, -0.052, zc), m, root)
        hide(ob, True)
        chalks[st] = ob
    return {"root": root, "chalks": chalks}


def build_camera_box(kit):
    """The photographer's box camera on its tripod, lens toward +y."""
    wood, brass, black = P("#a9763c", 0.55, 0.2), P("#e0b84a", 0.3, 0.8), P("#1e1b1f", 0.5, 0.2)
    cx, cy = 0.1, -5.0
    root = E(None, (cx, cy, 0), "boxcam")
    B(root, (0.46, 0.5, 0.42), (0, 0, 1.52), wood, "cbody", 0.03)
    B(root, (0.5, 0.04, 0.46), (0, -0.27, 1.52), brass, "cback", 0.01)
    B(root, (0.36, 0.34, 0.32), (0, 0.4, 1.52), black, "bellows1", 0.04)
    B(root, (0.26, 0.2, 0.22), (0, 0.64, 1.52), black, "bellows2", 0.03)
    kit.cyl(nm("lens"), 0.1, 0.16, (0, 0.82, 1.52), brass, root, rot=(math.pi / 2, 0, 0), n=20)
    kit.cyl(nm("lensglass"), 0.075, 0.03, (0, 0.91, 1.52), kit.glass("#5a7a9a"), root, rot=(math.pi / 2, 0, 0), n=20)
    B(root, (0.48, 0.52, 0.04), (0, 0, 1.74), brass, "chood", 0.01)
    B(root, (0.02, 0.3, 0.12), (-0.235, 0, 1.4), P("#1e1b1f"), "slot", 0.0)   # the print slot on the back
    collar = E(root, (0, 0, 0), "legs")
    for i, a in enumerate((0, 120, 240)):
        ar = math.radians(a + 90)
        lx, ly = 0.55 * math.cos(ar), 0.55 * math.sin(ar)
        foot = (lx, ly, 0.0)
        top = (0.0, 0.0, 1.3)
        mid = ((foot[0] + top[0]) / 2, (foot[1] + top[1]) / 2, (foot[2] + top[2]) / 2)
        ln = math.dist(foot, top)
        leg = B(collar, (0.06, 0.06, ln), mid, wood, "tleg", 0.01)
        d = (top[0] - foot[0], top[1] - foot[1], top[2] - foot[2])
        h_ = math.hypot(d[0], d[1])
        nd = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
        eul = (math.acos(d[2] / nd), 0.0, math.atan2(d[0], -d[1]) if h_ > 1e-9 else 0.0)
        leg.rotation_euler = eul
        if i == 0:
            col = B(collar, (0.12, 0.12, 0.08), (lerp(foot[0], top[0], 0.62), lerp(foot[1], top[1], 0.62), lerp(foot[2], top[2], 0.62)),
                    brass, "collar", 0.01)
            col.rotation_euler = eul
    # the one-stroke tally on the front tripod leg's collar, chalk white, 1.5 cm proud
    ar0 = math.radians(90)
    tx, ty = 0.55 * math.cos(ar0) * 0.38, 0.55 * math.sin(ar0) * 0.38
    bulb = E(None, (0, 0, 0), "bulb")
    kit.sphere(nm("bulbball"), 0.055, (0, 0, 0), black, bulb, seg=14)
    kit.cyl(nm("bulbneck"), 0.016, 0.07, (0, 0, 0.06), black, bulb, n=10)
    hide(bulb, True)
    return {"root": root, "bulb": bulb}


def build_prints(kit):
    out = {}
    specs = {
        "proof": prints.draw_crowd(11, gap=(2, 0), ring=True),
        "last": prints.draw_crowd(12, gap=(1, 2), ring=True),
        "test": prints.test_print(),
        "final": prints.draw_crowd(13, okafor=True),
    }
    cream = P("#fbf8ee", 0.6, 0.15)
    for nme, pil in specs.items():
        root = E(None, (0, -30, 0), f"print_{nme}")
        B(root, (0.46, 0.012, 0.54), (0, 0, 0), cream, "pborder", 0.004)
        m = img_mat(kit, f"print {nme}", pil, 0.5, emit=0.3)
        img_plane(kit, nm("pimg"), 0.4, 0.4 * pil.height / pil.width, (0, -0.0075, 0.04), m, root)
        hide(root, True)
        out[nme] = root
    return out


# --------------------------------------------------------------------------------------------------- the hallway
def build_hall(kit):
    X = HALLX
    wood = P("#d8b07a", 0.6, 0.15)
    creamw = P("#f6ecd6", 0.8, 0.1)
    B(None, (18, 6.4, 0.2), (X, 0, -0.08), wood, "hfloor", 0.0)
    B(None, (18, 6.4, 0.2), (X, 0, 3.5), kit.emit("#f0e6cc", 0.45), "hceil", 0.0)
    B(None, (0.3, 6.4, 3.4), (X - 9.1, 0, 1.7), creamw, "hend1", 0.0)
    B(None, (0.3, 6.4, 3.4), (X + 9.1, 0, 1.7), creamw, "hend2", 0.0)
    B(None, (18, 0.3, 3.4), (X, 3.15, 1.7), P("#f1e2c0", 0.8, 0.1), "hwallN", 0.0)
    B(None, (18, 0.3, 3.4), (X, -3.15, 1.7), creamw, "hwallS", 0.0)
    B(None, (18, 0.05, 0.12), (X, 2.98, 0.07), P("#8b5d33", 0.6, 0.1), "skirt", 0.0)
    # windows along the south wall: bright sky panes in white frames
    for i in range(-3, 4):
        wx = X + i * 2.4
        B(None, (1.5, 0.05, 2.1), (wx, -2.97, 1.8), P("#ffffff", 0.5, 0.2), "wframe", 0.01)
        B(None, (1.3, 0.04, 1.9), (wx, -2.95, 1.8), kit.emit("#d8efff", 1.4), "wpane", 0.0)
        B(None, (0.04, 0.045, 1.9), (wx, -2.93, 1.8), P("#ffffff", 0.5, 0.2), "wbar", 0.0)
    # ceiling lights
    for i in range(-3, 4):
        B(None, (0.9, 0.5, 0.04), (X + i * 2.4, 0.5, 3.38), kit.emit("#fff6e0", 2.2), "clight", 0.0)
    # the wall of framed photos at y = 2.97 (picture toward -y)
    tints = ["sepia", "blue", "rose", "sepia", "blue", "sepia", "rose", "blue", "sepia", "rose"]
    frame = P("#7d5429", 0.6, 0.15)
    mat_ = P("#fbf6e6", 0.8, 0.05)
    slots = []
    for i in range(-4, 5):
        slots.append(X + i * 1.6)
    for i, wx in enumerate(slots):
        pil = prints.hall_photo(200 + i, tints[i % len(tints)], grass=(i == 4))
        B(None, (1.34, 0.06, 1.1), (wx, 2.97, 1.75), frame, "pframe", 0.02)
        B(None, (1.24, 0.06, 1.0), (wx, 2.935, 1.75), mat_, "pmat", 0.01)
        m = img_mat(kit, f"hall photo {i}", pil, 0.9, emit=0.0)
        img_plane(kit, nm("hphoto"), 1.08, 1.08 * pil.height / pil.width, (wx, 2.89, 1.75), m)
    # light for the hallway
    kit.light("hall1", "AREA", (X - 3.0, 0.5, 3.2), 260, "#fff3dc", size=3.0, shadow=False)
    kit.light("hall2", "AREA", (X + 3.0, 0.5, 3.2), 260, "#fff3dc", size=3.0, shadow=False)
    kit.aim(kit.LIGHTS["hall1"]["obj"], (X - 3.0, 0.5, 0.0))
    kit.aim(kit.LIGHTS["hall2"]["obj"], (X + 3.0, 0.5, 0.0))


def build_beach(kit):
    X = BEACHX
    B(None, (60, 40, 0.2), (X, 8, -0.1), P("#f2deaa", 0.95, 0.03), "sand", 0.0)
    B(None, (60, 30, 0.1), (X, 30, -0.02), P("#4fb5e8", 0.15, 0.6), "sea", 0.0)
    wood = P("#c4884a", 0.6, 0.1)
    for sx in (-1.4, 1.4):
        B(None, (0.1, 0.1, 2.5), (X + sx, 1.6, 1.25), wood, "spost", 0.01)
    B(None, (3.2, 0.7, 0.9), (X, 1.4, 0.45), wood, "counter", 0.02)
    for i in range(8):
        B(None, (0.4, 1.4, 0.05), (X - 1.4 + 0.4 * i + 0.2, 1.0, 2.5), P("#ff6f61" if i % 2 else "#ffffff", 0.5, 0.2),
          "awn", 0.0, rot=(math.radians(14), 0, 0))
    cols = ["#ffd23f", "#2bb3a3", "#ff6f61", "#4a7fd0", "#9a63c8"]
    for i in range(5):
        B(None, (0.55, 0.03, 0.55), (X - 1.0 + 0.5 * i, 1.0, 1.7 - 0.12 * (i % 2)), P(cols[i], 0.5, 0.2), "skite", 0.0,
          rot=(0, math.radians(45), 0))
    kite = E(None, (X, -0.35, 0.85), "kite")
    B(kite, (0.8, 0.03, 0.8), (0, 0, 0.1), P("#ffd23f", 0.5, 0.2), "bigkite", 0.0, rot=(0, math.radians(45), 0))
    B(kite, (0.03, 0.035, 1.0), (0, -0.002, 0.1), P("#ff6f61", 0.5, 0.2), "kspar", 0.0)
    B(kite, (1.0, 0.035, 0.03), (0, -0.002, 0.1), P("#ff6f61", 0.5, 0.2), "kspar2", 0.0)
    for j in range(5):
        B(kite, (0.12, 0.02, 0.12), (0.02 * j, 0, -0.5 - 0.2 * j), P(cols[j], 0.5, 0.2), "ktail", 0.0, rot=(0, math.radians(45), 0))
    return kite


# --------------------------------------------------------------------------------------------------- build
def build(kit, story, tl):
    K.kit = kit
    ctx = {"story": story}
    ctx["shots"] = {s["id"]: s for s in story["shots"]}
    sc = bpy.context.scene
    nt = sc.world.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.55
    mr.clamp = True
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements.new(0.3)
    for el, c in zip(ramp.color_ramp.elements, ["#e4f3ff", "#a8d8ff", "#7cc8ff"]):
        r, g, b = (int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))
        el.color = (kit.srgb(r), kit.srgb(g), kit.srgb(b), 1.0)
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0
    sun = kit.light("sun", "SUN", (0, 0, 50), 5.0, "#fff3dc", size=0.1)
    sun.data.angle = 0.06
    azr, elr = math.radians(25), math.radians(48)
    pos = (math.sin(azr) * math.cos(elr), -math.cos(azr) * math.cos(elr), math.sin(elr))
    from mathutils import Vector as V
    sun.rotation_euler = (-V(pos)).to_track_quat("-Z", "Y").to_euler()
    ctx["fill"] = kit.light("camfill", "POINT", (0, 0, 2), 60, "#fff0dc", size=0.6, shadow=False)
    build_stands(kit)
    ctx["crowd"] = build_crowd(kit)
    build_town(kit)
    ctx["board"] = build_board(kit)
    ctx["cam"] = build_camera_box(kit)
    ctx["prints"] = build_prints(kit)
    build_hall(kit)
    ctx["kite"] = build_beach(kit)
    # the rule tag and the viewfinder frame ride on the camera
    cam = kit.OBJ["cam"]
    tag = kit.empty("tag", (0, 0, 0), cam)
    ctx["tags"] = {}
    for st in ("a", "b"):
        m = img_mat(kit, f"tag {st}", prints.tag(st), 0.9, emit=0.65)
        ob = img_plane(kit, nm("tagimg"), 1.0, 300 / 420, (0, 0, 0), m, tag, facing="+z")
        noshadow(ob)
        ob.hide_render = True
        ctx["tags"][st] = ob
    ctx["tag"] = tag
    vf = kit.empty("vf", (0, 0, 0), cam)
    cream = kit.emit("#fff8e0", 1.0, "vfcream")
    ang = cam.data.angle_x if cam.data.angle_x else 0.6
    d = 0.3
    hw = d * math.tan(ang / 2) * 0.86
    hh = hw * 16 / 9 * 0.86
    th = 0.0035
    for nme, size, loc in (("t", (2 * hw, th, 0.002), (0, hh, -d)), ("b", (2 * hw, th, 0.002), (0, -hh, -d)),
                           ("l", (th, 2 * hh, 0.002), (-hw, 0, -d)), ("r", (th, 2 * hh, 0.002), (hw, 0, -d))):
        ob = kit.box(f"vf.{nme}", size, loc, cream, vf)
        noshadow(ob)
    hide(vf, True)
    ctx["vf"] = vf
    ctx["acc"] = False
    return ctx


def add_accessories(kit):
    from blocky import rig
    P_ = lambda c, r=0.5: kit.plastic(c, r)  # noqa: E731
    chars = rig.CHARS
    if "okafor" in chars:
        hg = chars["okafor"].head.children[0]
        kit.box("ok.beard", (1.0, 0.42, 0.56), (0, -0.46, -0.34), P_("#f4f4f0", 0.7), hg, bevel=0.12)
        kit.box("ok.beard2", (0.64, 0.3, 0.2), (0, -0.62, -0.1), P_("#f4f4f0", 0.7), hg, bevel=0.08)
        kit.box("ok.cap", (1.38, 1.3, 0.3), (0, -0.02, 0.62), P_("#3a3d44", 0.7), hg, bevel=0.1)
        kit.box("ok.brim", (1.0, 0.5, 0.08), (0, -0.78, 0.5), P_("#2c2e34", 0.7), hg, bevel=0.03)
    for who, gold in (("mom", "#e8b838"), ("grandma", "#e8e8f0")):
        if who in chars:
            hg = chars[who].head.children[0]
            for sx in (-1, 1):
                kit.box(f"{who}.ear{sx}", (0.12, 0.12, 0.3), (sx * 0.66, -0.05, -0.32), P_(gold, 0.3), hg, bevel=0.03)
    if "grandma" in chars:
        hg = chars["grandma"].head.children[0]
        for i, (x, z) in enumerate(((-0.55, 0.3), (0.55, 0.3), (-0.62, -0.05), (0.62, -0.05), (0, 0.66), (-0.3, 0.6), (0.3, 0.6))):
            kit.sphere(f"gm.curl{i}", 0.22, (x, 0.0, z), P_("#f4f4f4", 0.8), hg, seg=10)


# --------------------------------------------------------------------------------------------------- animate
def animate(kit, story, tl, t, ctx):
    sc = bpy.context.scene
    if not ctx["acc"]:
        add_accessories(kit)
        ctx["acc"] = True
    cur = next((s for s in tl["shots"] if s["start"] <= t < s["end"]), tl["shots"][-1])
    sd = ctx["shots"][cur["id"]]
    from blocky import bl_story
    cl, _, _, _ = bl_story.cam_at(sd, cur, t, {}, tl)
    ctx["fill"].location = (cl[0], cl[1], cl[2])
    hall = cl[0] > HALLX - 12 and cl[0] < HALLX + 12
    ov = {"sun": 0.0 if hall else 1.0, "camfill": sd.get("fill", 1.0) * (0.45 if hall else 1.0),
          "hall1": 1.0 if hall else 0.0, "hall2": 1.0 if hall else 0.0}
    cd = kit.OBJ["cam"].data
    dof = sd.get("dof")
    if dof:
        cd.dof.use_dof = True
        cd.dof.focus_distance = dof[0]
        cd.dof.aperture_fstop = dof[1]
    else:
        cd.dof.use_dof = False
    # the board
    g = cue_at(tl, "board", t).get("g", "a")
    for k, ob in ctx["board"]["chalks"].items():
        hide(ob, k != g)
    # the tag
    tg = cue_at(tl, "tag", t).get("g", "a")
    for k, ob in ctx["tags"].items():
        hide(ob, k != tg)
    # the viewfinder frame
    hide(ctx["vf"], not bool(cue_at(tl, "vf", t).get("on")))
    # prints
    for nme, ob in ctx["prints"].items():
        c = cue_at(tl, f"pr_{nme}", t)
        if not c.get("on"):
            hide(ob, True)
            continue
        hide(ob, False)
        p = list(c["pos"])
        if c.get("to"):
            u = ss((t - c["t"]) / max(1e-3, c.get("dur", 1.0)))
            p = [lerp(a, b, u) for a, b in zip(p, c["to"])]
        yaw, pitch = (c.get("rot") or [0, 0])[:2]
        ob.location = tuple(p)
        sc_ = c.get("s", 1.0)
        ob.scale = (sc_, sc_, sc_)
        ob.rotation_euler = (math.radians(pitch), 0, math.radians(yaw))
    # the shutter bulb
    c = cue_at(tl, "bulb", t)
    if c.get("on"):
        hide(ctx["cam"]["bulb"], False)
        p = list(c["pos"])
        if c.get("to"):
            u = ss((t - c["t"]) / max(1e-3, c.get("dur", 1.0)))
            p = [lerp(a, b, u) for a, b in zip(p, c["to"])]
        sh = c.get("shake", 0.0)
        if sh:
            p = [p[0] + sh * math.sin(t * 12.5), p[1], p[2] + sh * 0.7 * math.sin(t * 12.5 + 1.3)]
        ctx["cam"]["bulb"].location = tuple(p)
        big = c.get("big", 1.0)
        sq = c.get("squeeze")
        z = 1.0
        if sq is not None:
            u = t - (c["t"] + sq)
            z = 1.0 - 0.45 * ss(u / 0.08) * (1.0 - ss((u - 0.18) / 0.2)) if u > 0 else 1.0
        ctx["cam"]["bulb"].scale = (big, big, big * z)
    else:
        hide(ctx["cam"]["bulb"], True)
    # the crowd's cheer: arms up, eased over 0.4 s
    c = cue_at(tl, "cheer", t)
    if c:
        u = ss((t - c["t"]) / 0.4)
        amt = u if c.get("on") else 1.0 - u
    else:
        amt = 0.0
    for p_ in ctx["crowd"]:
        wob = 0.9 + 0.1 * math.sin(8.0 * t + p_["ph"])
        ang = -math.radians(150) * amt * wob
        if p_["row"] in (0, 1, 3) and abs(p_["x"]) < 1.5:
            ang = 0.0
        for piv in p_["arms"]:
            piv.rotation_euler = (ang, 0, 0)
    return ov
