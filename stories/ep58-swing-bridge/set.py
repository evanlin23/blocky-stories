"""Swing Bridge (ep58). Creature-test build so far: the Reach, a rough rail, a cabin window. Rest of the set to come.

Coordinates: metres, z up, front of a character is -y at yaw 0. The bridge deck runs along +x.
"""
from __future__ import annotations

import math

import bpy
from mathutils import Vector as V

from blocky import rig

OCHRE, PEAT, TAN, CLAY = "#8a6424", "#2b2420", "#b39a78", "#c49a74"
REACH_SPEC = {
    "age": "adult", "skin": CLAY, "shirt": OCHRE, "pattern": "solid", "collar": "#4a3c30", "pants": PEAT, "shoes": TAN,
    "sleeves": "none", "hair": "cap", "hair_c": "#3a2e26", "hat": "none", "body_width": 0.78,
    "face": {"eyes": "pin", "mouth": "flat", "brows": False, "ink": "#161012"},
}


COAT, RIM = "#a07a4c", "#8fb4d8"
PALE = "#dcb894"


def seg(kit, name, a, b, t, mat, up_t=None):
    a, b = V(a), V(b)
    d = b - a
    return kit.box(name, (t, up_t or t, d.length), tuple((a + b) / 2), mat, rot=d.to_track_quat("Z", "Y").to_euler(),
                   bevel=0.03)


def long_arm(kit, name, pts, t=0.19, fold=1.4, hand=True):
    """One continuous sleeve through pts (shoulder first, hand end last): blocks <= fold long laid end to end,
    a fold of cloth at each join, a cool rim along the top, a visible cuff, a big pale hand with spread blocky
    fingers lying flat along the last direction."""
    sl = kit.plastic(COAT, 0.85)
    cuffm = kit.plastic("#3a2c20", 0.8)
    rim = kit.emit(RIM, 0.9)
    skin = kit.plastic(PALE, 0.5)
    P = [V(p) for p in pts]
    joints = [P[0]]
    for i in range(len(P) - 1):
        d = P[i + 1] - P[i]
        n = max(1, int(math.ceil(d.length / fold)))
        for k in range(1, n + 1):
            joints.append(P[i] + d * (k / n))
    up = V((0, 0, 1))
    for i in range(len(joints) - 1):
        a, b = joints[i], joints[i + 1]
        seg(kit, f"{name}.s{i}", a, b, t, sl)
        seg(kit, f"{name}.r{i}", a + up * (t / 2 + 0.006), b + up * (t / 2 + 0.006), 0.045, rim, 0.012)
    for i in range(1, len(joints) - 1):
        d = joints[i + 1] - joints[i - 1]
        kit.box(f"{name}.f{i}", (t * 1.18, t * 1.18, 0.12), tuple(joints[i]), sl,
                rot=d.to_track_quat("Z", "Y").to_euler(), bevel=0.05)
    if hand:
        e, d = joints[-1], (joints[-1] - joints[-2]).normalized()
        yaw = math.atan2(d.y, d.x)
        kit.box(f"{name}.cuff", (t * 1.2, t * 1.2, 0.1), tuple(e), cuffm, rot=d.to_track_quat("Z", "Y").to_euler(), bevel=0.03)
        c = e + d * 0.14
        kit.box(f"{name}.palm", (0.17, 0.2, 0.07), tuple(c - up * (t / 2 - 0.05)), skin, rot=(0, 0, yaw), bevel=0.02)
        perp = V((-d.y, d.x, 0))
        for k in range(4):   # four blocky fingers, fingers together
            fc = e + d * 0.34 + perp * (-0.075 + 0.05 * k) - up * (t / 2 - 0.05)
            kit.box(f"{name}.fing{k}", (0.15, 0.045, 0.06), tuple(fc), skin, rot=(0, 0, yaw), bevel=0.015)
        kit.box(f"{name}.thumb", (0.1, 0.05, 0.06), tuple(e + d * 0.15 - perp * 0.12 - up * (t / 2 - 0.05)), skin,
                rot=(0, 0, yaw + 0.5), bevel=0.015)


def make_reach(kit, workdir, pos, yaw=0.0, lean=0.0, head_pitch=0.0, head_yaw=0.0, paths=None, shirt=None):
    """One Reach: a man, plus two continuous sleeves. paths(shoulderL, shoulderR) -> two point lists."""
    ch = rig.Character("reach", REACH_SPEC, workdir)
    ch.pose(pos[0], pos[1], pos[2], yaw, lean=lean, head_pitch=head_pitch, head_yaw=head_yaw, expr="neutral")
    for sx in (-1, 1):
        for ob in ch.P[f"arm{sx}"].children_recursive:
            ob.hide_render = True
    bpy.context.view_layer.update()
    sh = [ch.torso.matrix_world @ V((sx * 1.5 * REACH_SPEC["body_width"], 0, 1.75)) for sx in (-1, 1)]
    for name, pts in zip(("armL", "armR"), paths(*sh)):
        long_arm(kit, name, pts)
    return ch


def bridge(kit, length, rail_y=0.0, rail_z=0.98, dirv=(1, 0), origin=(0, 0)):
    green = kit.plastic("#5f8a74", 0.6)
    dark = kit.plastic("#2f4a3e", 0.7)
    deck = kit.plastic("#5a4a3a", 0.9)
    d = V((*dirv, 0)).normalized()
    o = V((origin[0], origin[1], 0))
    ang = math.atan2(d.y, d.x)
    mid = o + d * (length / 2)
    kit.box("deck", (length, 1.6, 0.12), (mid.x, mid.y, -0.06), deck, rot=(0, 0, ang))
    n = int(length / 1.5)
    perp = V((-d.y, d.x, 0))
    for side in (0,):
        base = o + perp * rail_y
        kit.box("topchord", (length, 0.12, 0.07), (mid.x + perp.x * rail_y, mid.y + perp.y * rail_y, rail_z - 0.035), green,
                rot=(0, 0, ang))
        kit.box("lowchord", (length, 0.05, 0.05), (mid.x + perp.x * rail_y, mid.y + perp.y * rail_y, 0.3), green, rot=(0, 0, ang))
        for i in range(n + 1):
            p = base + d * (i * length / n)
            kit.box(f"post{i}", (0.07, 0.07, rail_z), (p.x, p.y, rail_z / 2), dark, rot=(0, 0, ang))
    return d
